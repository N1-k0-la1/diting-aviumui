"""Compile and exercise production methods with bounded host-side dependencies."""
import pathlib, re, subprocess, tempfile, json, argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', type=pathlib.Path, help='Patched Android source checkout; requires its JDK 21 and host g++')
SOURCE = parser.parse_args().source.resolve(strict=True)

def method(text, name):
    match = re.search(r'^.*\b' + name + r'\([^;{]*\)\s*\{', text, re.M)
    start, pos, depth = match.start(), match.end(), 1
    while depth:
        depth += (text[pos] == '{') - (text[pos] == '}')
        pos += 1
    return text[start:pos].replace('@Override ', '')

def run(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)

checks = []
with tempfile.TemporaryDirectory(prefix='full-review-') as tmp:
    d = pathlib.Path(tmp)
    java = SOURCE / 'prebuilts/jdk/jdk21/linux-x86/bin'
    bt = (SOURCE/'packages/modules/Bluetooth/framework/java/android/bluetooth/BluetoothCodecConfig.java').read_text()
    code = '''import java.util.Objects;
class Codec {
 int mCodecType=1,mSampleRate=48000,mBitsPerSample=24,mChannelMode=2;
 long mCodecSpecific1=0x8000,mCodecSpecific2=0x8000,mCodecSpecific3=0x4c000000,mCodecSpecific4=4;
 static final int SAMPLE_RATE_NONE=0,BITS_PER_SAMPLE_NONE=0,CHANNEL_MODE_NONE=0;
''' + method(bt, 'similarCodecFeedingParameters').replace('BluetoothCodecConfig', 'Codec') + '''
 public static void main(String[] args) {
  Codec a=new Codec(),b=new Codec();
  if(!a.similarCodecFeedingParameters(b))throw new AssertionError("nonzero flags");
  b.mSampleRate=0;b.mBitsPerSample=0;b.mChannelMode=0;
  if(!a.similarCodecFeedingParameters(b)||!b.similarCodecFeedingParameters(a))throw new AssertionError("wildcards");
  b.mSampleRate=96000;if(a.similarCodecFeedingParameters(b))throw new AssertionError("rate mismatch");
  b.mSampleRate=48000;b.mCodecType=2;if(a.similarCodecFeedingParameters(b)||a.similarCodecFeedingParameters(null))throw new AssertionError("type/null");
 }
}'''
    (d/'Codec.java').write_text(code)
    run(str(java/'javac'), str(d/'Codec.java'))
    run(str(java/'java'), '-cp', str(d), 'Codec')
    checks.append('production codec similarity: nonzero flags, symmetric wildcards, mismatched rate/type, null')

    font = (SOURCE/'frameworks/base/services/core/java/com/android/server/graphics/fonts/FontManagerService.java').read_text()
    fixtures = {
      'org/json/JSONObject.java': '''package org.json; public class JSONObject { public String value; public JSONObject(){value="old";} public JSONObject(String s){value=s;} public void put(String k,String v){value=v;} public String toString(){return value;} }''',
      'android/os/Binder.java': '''package android.os; public class Binder { public static long clearCallingIdentity(){return 0;} public static void restoreCallingIdentity(long i){} }''',
      'android/os/ServiceSpecificException.java': '''package android.os; public class ServiceSpecificException extends RuntimeException { public ServiceSpecificException(int i,String s){super(s);} }''',
      'android/provider/Settings.java': '''package android.provider; public class Settings { public static class Secure {
       public static final String THEME_CUSTOMIZATION_OVERLAY_PACKAGES="theme";
       public static final java.util.concurrent.CountDownLatch entered=new java.util.concurrent.CountDownLatch(1),release=new java.util.concurrent.CountDownLatch(1);
       public static String getStringForUser(Object c,String k,int u){return "old";}
       public static boolean putStringForUser(Object c,String k,String v,int u) throws Exception {
        if(Thread.currentThread().getName().equals("failed-import")){entered.countDown();release.await();return false;} return true;
       }
      }}''',
      'Transaction.java': '''import java.io.IOException;
class ParcelFileDescriptor { public void close() throws IOException {} }
class Base { void installUserCustomFont_enforcePermission() {} }
class Context { Object getContentResolver(){return this;} }
class Slog { static void w(String t,String m,Throwable e){} }
class Store { org.json.JSONObject value=new org.json.JSONObject();
 synchronized org.json.JSONObject snapshotImported(){return value;}
 synchronized void install(ParcelFileDescriptor f,String label){value=new org.json.JSONObject(label);}
 synchronized void restoreImported(org.json.JSONObject old) throws IOException {value=old;}
}
class Transaction extends Base {
 final Store mUserCustomFonts=new Store(); final Context mContext=new Context(); static final String TAG="test";
 void enforcePrimaryUserFontCaller(){}
''' + method(font, 'installUserCustomFont') + '''
 public static void main(String[] args) throws Exception {
  Transaction service=new Transaction();
  Thread a=new Thread(()->{try {service.installUserCustomFont(new ParcelFileDescriptor(),"A");throw new AssertionError();}catch(android.os.ServiceSpecificException expected){}},"failed-import");
  Thread b=new Thread(()->service.installUserCustomFont(new ParcelFileDescriptor(),"B"),"successful-import");
  a.start();if(!android.provider.Settings.Secure.entered.await(5,java.util.concurrent.TimeUnit.SECONDS))throw new AssertionError("timeout");
  b.start();b.join(200);boolean interleaved=!b.isAlive();
  android.provider.Settings.Secure.release.countDown();a.join(5000);b.join(5000);
  if(interleaved||a.isAlive()||b.isAlive()||!"B".equals(service.mUserCustomFonts.value.value))throw new AssertionError("rollback clobbered concurrent import");
 }
}'''
    }
    for name, text in fixtures.items():
        p=d/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
    run(str(java/'javac'),*[str(d/n) for n in fixtures])
    run(str(java/'java'),'-cp',str(d),'Transaction')
    checks.append('production font Binder method: concurrent failed/successful imports retain successful metadata')

    for v in ('3','5'):
        src=(SOURCE/f'packages/modules/Bluetooth/system/stack/a2dp/a2dp_vendor_lhdcv{v}_decoder.cc').read_text()
        cb=f'a2dp_lhdcv{v}_decoder_cb'; prefix='lhdc' if v=='3' else 'lhdcv5'
        success='LHDCBT_DEC_FUNC_SUCCEED' if v=='3' else 'LHDCV5BT_DEC_API_SUCCEED'
        code='''#include <cstdint>
#include <cstddef>
#include <cstring>
#include <cassert>
#include <pthread.h>
namespace log { template<class...T> void error(T...args){} template<class...T> void info(T...args){} }
struct BT_HDR { uint16_t offset=0,len=4; uint8_t data[64]{}; };
static bool oversized=false; static int callbacks=0;
struct State { uint32_t dec_buf_idx=0,dec_input_buf_bytes=0; uint8_t dec_input_buf[64]{},decode_buf[2][64]{}; int bits_per_sample=24;
 bool has_lhdc_handle=true; void* lhdc_handle=(void*)1; pthread_mutex_t mutex=PTHREAD_MUTEX_INITIALIZER;
 void (*decode_callback)(uint8_t*,uint32_t)=[](uint8_t*,uint32_t size){assert(size==6);++callbacks;};
};
void* lhdc_decoder_lib_handle=(void*)1;
''' + f'''State {cb};
constexpr int LHDCV{v}_DEC_PACKET_NUM=2,LHDCV{v}_DEC_INPUT_BUF_BYTES=64,LHDCV{v}_DEC_PKT_HDR_BYTES=2;
constexpr int {success}=0,LHDCBT_DEC_FUNC_INPUT_NOT_ENOUGH=1;
int (*{prefix}dec_check_frame_data_enough)(uint8_t*,uint32_t,uint32_t*)=[](uint8_t*,uint32_t n,uint32_t* out){{*out=n-2;return 0;}};
int (*{prefix}dec_decode)(uint8_t*,uint32_t,uint8_t*,uint32_t*,int)=[](uint8_t*,uint32_t,uint8_t*,uint32_t* out,int){{*out=oversized?65:8;return 0;}};
''' + method(src, f'a2dp_vendor_lhdcv{v}_decoder_decode_packet') + f'''
int main(){{BT_HDR packet;
 assert(!a2dp_vendor_lhdcv{v}_decoder_decode_packet(nullptr));
 oversized=true;assert(!a2dp_vendor_lhdcv{v}_decoder_decode_packet(&packet));assert(callbacks==0);
 oversized=false;assert(a2dp_vendor_lhdcv{v}_decoder_decode_packet(&packet));assert(callbacks==1);
 {cb}.decode_callback=nullptr;assert(!a2dp_vendor_lhdcv{v}_decoder_decode_packet(&packet));assert(callbacks==1);
}}
'''
        p=d/f'decoder{v}.cc';p.write_text(code)
        run('g++','-std=c++17','-fsanitize=address,undefined','-pthread',str(p),'-o',str(d/f'decoder{v}'))
        run(str(d/f'decoder{v}'))
        checks.append(f'production V{v} decoder: invalid output size, null callback, normal PCM conversion under ASAN/UBSAN')

print(json.dumps({'passed': True, 'checks': checks}, indent=2))
