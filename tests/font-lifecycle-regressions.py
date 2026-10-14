"""Exercise production font IPC completion and boot cleanup with host API stubs."""
import argparse, pathlib, re, subprocess, tempfile
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('source',type=pathlib.Path)
source=parser.parse_args().source.resolve(strict=True)
def method(text,name):
 match=re.search(r'^.*\b'+name+r'\([^;{]*\)\s*\{',text,re.M)
 pos=match.end();depth=1
 while depth:
  depth+=(text[pos]=='{')-(text[pos]=='}');pos+=1
 return text[match.start():pos].replace('@Override ','')
java=source/'prebuilts/jdk/jdk21/linux-x86/bin'
files={
 'android/os/IBinder.java':'package android.os; public interface IBinder {}',
 'android/os/RemoteException.java':'package android.os; public class RemoteException extends Exception {}',
 'android/os/Looper.java':'package android.os; public class Looper { public static Looper getMainLooper(){return null;} }',
 'android/os/Handler.java':'''package android.os; public class Handler {
 public static java.util.List<Runnable> queue=new java.util.ArrayList<>();
 public Handler(Looper l){} public void handleMessage(Message m){}
 public void post(Runnable r){r.run();} public void postDelayed(Runnable r,long ms){queue.add(r);}
 public void removeCallbacks(Runnable r){queue.remove(r);}
 }''',
 'android/os/Bundle.java':'''package android.os; public class Bundle {Object value;
 public <T> T getParcelable(String k,Class<T> c){return c.cast(value);} public void putParcelable(String k,Object v){value=v;} }''',
 'android/os/Message.java':'''package android.os; public class Message {public int arg1; public Messenger replyTo; Bundle data=new Bundle();
 public static Message obtain(){return new Message();} public Bundle getData(){return data;} public void setData(Bundle b){data=b;} }''',
 'android/os/Messenger.java':'''package android.os; public class Messenger {
 public static int replies,last; public static Message lastMessage; public Handler handler;
 public Messenger(Handler h){handler=h;} public Messenger(IBinder b){}
 public IBinder getBinder(){return null;}
 public void send(Message m)throws RemoteException {replies++;last=m.arg1;lastMessage=m;if(handler!=null)handler.handleMessage(m);} }''',
 'android/os/SharedMemory.java':'''package android.os; public class SharedMemory implements AutoCloseable {
 public static SharedMemory create(String n,int s){return new SharedMemory();}
 public java.nio.ByteBuffer mapReadOnly(){return java.nio.ByteBuffer.allocate(10);}
 public java.nio.ByteBuffer mapReadWrite(){return java.nio.ByteBuffer.allocate(10);}
 public static void unmap(java.nio.ByteBuffer b){} public boolean setProtect(int p){return true;} public void close(){} }''',
 'android/system/OsConstants.java':'package android.system; public class OsConstants {public static final int PROT_READ=1;}',
 'android/content/ComponentName.java':'package android.content; public class ComponentName {}',
 'android/content/Intent.java':'package android.content; public class Intent {public Intent(Object a,Class<?> b){} }',
 'android/content/Context.java':'package android.content; public class Context {public static final int BIND_AUTO_CREATE=1;}',
 'android/content/ServiceConnection.java':'''package android.content; public interface ServiceConnection {
 void onServiceConnected(ComponentName c,android.os.IBinder b);void onServiceDisconnected(ComponentName c);void onBindingDied(ComponentName c); }''',
 'android/app/Service.java':'package android.app; public class Service {public android.os.IBinder onBind(android.content.Intent i){return null;} }',
 'android/app/Activity.java':'''package android.app; public class Activity {
 public static boolean bindResult=true;public static android.content.ServiceConnection connection;public static int unbinds;
 public boolean bindService(android.content.Intent i,android.content.ServiceConnection c,int f){connection=c;return bindResult;}
 public void unbindService(android.content.ServiceConnection c){unbinds++;} public boolean isFinishing(){return false;} }''',
 'android/graphics/fonts/Font.java':'''package android.graphics.fonts; public class Font {
 public static class Builder {public Builder(Object o){} public Font build(){return new Font();}} }''',
 'android/graphics/fonts/FontFamily.java':'package android.graphics.fonts; public class FontFamily {public static class Builder {public Builder(Font f){} public FontFamily build(){return new FontFamily();}}}',
 'android/graphics/Typeface.java':'package android.graphics; public class Typeface {public static class CustomFallbackBuilder {public CustomFallbackBuilder(android.graphics.fonts.FontFamily f){} public CustomFallbackBuilder setSystemFallback(String s){return this;} public Typeface build(){return new Typeface();}}}',
 'android/graphics/Bitmap.java':'package android.graphics; public class Bitmap {public enum Config {ARGB_8888} public static Bitmap createBitmap(int a,int b,Config c){return new Bitmap();} public void recycle(){} }',
 'android/graphics/Paint.java':'package android.graphics; public class Paint {public void setTypeface(Typeface f){} public void setTextSize(int s){} }',
 'android/graphics/Canvas.java':'package android.graphics; public class Canvas {public Canvas(Bitmap b){} public void drawText(String s,int a,int b,Paint p){} }',
 'android/widget/Toast.java':'package android.widget; public class Toast {public static final int LENGTH_LONG=1; public static Toast makeText(Object a,int s,int l){return new Toast();} public void show(){} }',
 'org/json/JSONObject.java':'package org.json; public class JSONObject {String digest;public JSONObject(String d){digest=d;} public String optString(String k){return digest;} }',
}
service=source/'packages/apps/Settings/src/com/android/settings/display/FontImportValidationService.java'
files['com/android/settings/display/FontImportValidationService.java']=service.read_text()
importer=(source/'packages/apps/Settings/src/com/android/settings/display/CustomFontImport.java').read_text()
files['com/android/settings/display/Completion.java']='''package com.android.settings.display;
import android.app.Activity;import android.content.*;import android.os.*;import android.graphics.*;
import android.graphics.fonts.*;import android.widget.Toast;import java.io.*;
class R {static class string {static int font_custom_invalid=1;}}
class ThreadUtils {static void postOnBackgroundThread(Runnable r){r.run();}}
class Fragment {Activity getActivity(){return new Activity();}boolean isAdded(){return true;}}
public class Completion {Fragment mFragment=new Fragment();boolean mBusy;int previews;
void showPreview(File f,String label,Typeface t){previews++;}
'''+method(importer,'validateIsolated')+'''
public static void main(String[] args)throws Exception {
 for(boolean result:new boolean[]{true,false}) {
  android.app.Activity.bindResult=result;
  Completion c=new Completion();c.mBusy=true;File f=File.createTempFile("font-test-",".ttf");
  c.validateIsolated(f,"test");
  if(!result) {if(!Handler.queue.isEmpty()||f.exists()||c.mBusy)throw new AssertionError("bind failure retained timeout");continue;}
  if(Handler.queue.size()!=1)throw new AssertionError("no timeout for pending validation");
  Activity.connection.onServiceDisconnected(null);
  if(!Handler.queue.isEmpty()||f.exists()||c.mBusy)throw new AssertionError("completion retained timeout");
 }
 Activity.bindResult=true;
 Completion c=new Completion();c.mBusy=true;File f=File.createTempFile("font-test-",".ttf");
 c.validateIsolated(f,"test");Runnable timeout=Handler.queue.get(0);timeout.run();
 if(!Handler.queue.isEmpty()||f.exists()||c.mBusy)throw new AssertionError("timeout cleanup failed");
 Completion ok=new Completion();ok.mBusy=true;File accepted=File.createTempFile("font-test-",".ttf");
 java.nio.file.Files.write(accepted.toPath(),new byte[]{1});ok.validateIsolated(accepted,"test");
 Activity.connection.onServiceConnected(null,null);
 Message response=Message.obtain();response.arg1=1;Messenger.lastMessage.replyTo.send(response);
 if(!Handler.queue.isEmpty()||ok.mBusy||ok.previews!=1||!accepted.exists())throw new AssertionError("success completion retained timeout");
 accepted.delete();
 android.os.Messenger.replies=0;
 FontImportValidationService service=new FontImportValidationService();
 java.lang.reflect.Field field=FontImportValidationService.class.getDeclaredField("mMessenger");field.setAccessible(true);
 Messenger endpoint=(Messenger)field.get(service);
 Message absent=Message.obtain();absent.replyTo=new Messenger((Handler)null);endpoint.handler.handleMessage(absent);
 if(Messenger.replies!=1||Messenger.last!=0)throw new AssertionError("missing memory needs immediate failure reply");
 Message valid=Message.obtain();valid.getData().putParcelable("font",new SharedMemory());valid.replyTo=absent.replyTo;
 endpoint.handler.handleMessage(valid);
 if(Messenger.replies!=2||Messenger.last!=1)throw new AssertionError("normal validation changed");
 }
}'''
store=(source/'frameworks/base/services/core/java/com/android/server/graphics/fonts/UserCustomFontStore.java').read_text()
files['BootCleanup.java']='''import java.io.*;import org.json.JSONObject;
class BootCleanup {File mDirectory,mBootMarker;JSONObject mLoaded,mImported;
File fileFor(JSONObject j){return new File(mDirectory,j.optString("digest")+".font");}
'''+method(store,'onBootCompleted')+'''
public static void main(String[] args)throws Exception {
 BootCleanup s=new BootCleanup();s.mDirectory=java.nio.file.Files.createTempDirectory("font-cleanup-").toFile();
 s.mBootMarker=new File(s.mDirectory,"boot-marker");s.mBootMarker.createNewFile();
 String a="a".repeat(64),b="b".repeat(64),c="c".repeat(64);
 s.mLoaded=new JSONObject(a);s.mImported=new JSONObject(b);
 for(String name:new String[]{a+".font",b+".font",c+".font","staged-123.font","staged-note.txt","unrelated.font"})new File(s.mDirectory,name).createNewFile();
 s.onBootCompleted();
 for(String name:new String[]{a+".font",b+".font","staged-note.txt","unrelated.font"})if(!new File(s.mDirectory,name).exists())throw new AssertionError("removed retained/unrelated "+name);
 for(String name:new String[]{c+".font","staged-123.font","boot-marker"})if(new File(s.mDirectory,name).exists())throw new AssertionError("orphan retained "+name);
 for(File f:s.mDirectory.listFiles())f.delete();s.mDirectory.delete();
 }
}'''
with tempfile.TemporaryDirectory(prefix='font-lifecycle-') as tmp:
 d=pathlib.Path(tmp)
 for n,t in files.items():p=d/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t)
 subprocess.run([str(java/'javac'),'-d',str(d),*[str(d/n) for n in files]],check=True)
 for cls in ('com.android.settings.display.Completion','BootCleanup'):
  subprocess.run([str(java/'java'),'-cp',str(d),cls],check=True)
print('PASS: absent/valid IPC reply, completion/bind-failure/timeout callback removal, boot orphan cleanup')
