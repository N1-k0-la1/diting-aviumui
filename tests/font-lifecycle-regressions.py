# SPDX-License-Identifier: Apache-2.0
"""Exercise production font IPC completion and boot cleanup with host API stubs."""
import argparse, pathlib, re, subprocess, tempfile
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('source',type=pathlib.Path)
source=parser.parse_args().source.resolve(strict=True)
def method(text,name):
 match=re.search(r'^.*\b'+name+r'\([^;{]*\)\s*(?:throws\s+[^\{]+)?\{',text,re.M)
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
 java.util.Map<String,Object> values=new java.util.HashMap<>();
 public boolean getBoolean(String k){return Boolean.TRUE.equals(values.get(k));}public void putBoolean(String k,boolean v){values.put(k,v);}
 public String getString(String k){return (String)values.get(k);}public void putString(String k,String v){values.put(k,v);}
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
 'android/content/Context.java':'''package android.content; public class Context {public static final int BIND_AUTO_CREATE=1;
 public static android.content.om.OverlayManager manager=new android.content.om.OverlayManager();
 public <T> T getSystemService(Class<T> c){return c.cast(manager);}public int getUserId(){return 0;} }''',
 'android/content/om/OverlayManager.java':'''package android.content.om; public class OverlayManager {
 public static OverlayInfo info;public OverlayInfo getOverlayInfo(String key,android.os.UserHandle u){return info;} }''',
 'android/content/om/OverlayInfo.java':'''package android.content.om; public class OverlayInfo {
 public String targetPackageName="android",category="font";public boolean isMutable=true; }''',
 'android/os/UserHandle.java':'package android.os; public class UserHandle {public static UserHandle of(int u){return new UserHandle();}}',
 'android/content/ServiceConnection.java':'''package android.content; public interface ServiceConnection {
 void onServiceConnected(ComponentName c,android.os.IBinder b);void onServiceDisconnected(ComponentName c);void onBindingDied(ComponentName c); }''',
 'android/app/Service.java':'package android.app; public class Service {public android.os.IBinder onBind(android.content.Intent i){return null;} }',
 'android/app/Activity.java':'''package android.app; public class Activity {
 public static boolean bindResult=true,throwUnbind=false,destroyed=false;public static android.content.ServiceConnection connection;public static int unbinds;
 public boolean bindService(android.content.Intent i,android.content.ServiceConnection c,int f){connection=c;return bindResult;}
 public void unbindService(android.content.ServiceConnection c){unbinds++;if(throwUnbind)throw new IllegalArgumentException("Service not registered");} public boolean isFinishing(){return false;} public boolean isDestroyed(){return destroyed;} }''',
 'android/graphics/fonts/Font.java':'''package android.graphics.fonts; public class Font {
 public static class Builder {public Builder(Object o){} public Font build(){return new Font();}} }''',
 'android/graphics/fonts/FontFamily.java':'package android.graphics.fonts; public class FontFamily {public static class Builder {public Builder(Font f){} public FontFamily build(){return new FontFamily();}}}',
 'android/graphics/Typeface.java':'package android.graphics; public class Typeface {public static final Typeface DEFAULT=new Typeface();public static class CustomFallbackBuilder {public CustomFallbackBuilder(android.graphics.fonts.FontFamily f){} public CustomFallbackBuilder setSystemFallback(String s){return this;} public Typeface build(){return new Typeface();}}}',
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
class Fragment {static boolean gone;Activity getActivity(){return gone?null:new Activity();}boolean isAdded(){return !gone;}}
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
 Activity.throwUnbind=true;
 Completion detached=new Completion();detached.mBusy=true;File orphan=File.createTempFile("font-test-",".ttf");
 detached.validateIsolated(orphan,"test");Activity.connection.onServiceDisconnected(null);
 if(orphan.exists()||detached.mBusy||!Handler.queue.isEmpty())throw new AssertionError("unbind failure skipped cleanup");
 Activity.throwUnbind=false;Activity.destroyed=true;
 Completion destroyed=new Completion();destroyed.mBusy=true;File abandoned=File.createTempFile("font-test-",".ttf");
 destroyed.validateIsolated(abandoned,"test");
 if(abandoned.exists()||destroyed.mBusy||!Handler.queue.isEmpty())throw new AssertionError("destroyed activity retained import");
 Activity.destroyed=false;
 Fragment.gone=true;
 Completion missing=new Completion();missing.mBusy=true;File lost=File.createTempFile("font-test-",".ttf");
 missing.validateIsolated(lost,"test");if(lost.exists()||missing.mBusy)throw new AssertionError("absent activity retained import");
 Fragment.gone=false;
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
controller=(source/'packages/apps/Settings/src/com/android/settings/display/FontStylePreferenceController.java').read_text()
preview=method(importer,'showPreview').split('        LinearLayout preview')[0]
files['com/android/settings/display/OverlayGuard.java']='''package com.android.settings.display;
import android.content.*;import android.content.om.*;import android.os.*;import android.app.*;
import java.io.*;import android.graphics.Typeface;
class FontStyleConfig {static final String CATEGORY="font";}
public class OverlayGuard {
Fragment mFragment=new Fragment();boolean previewCreated;
'''+method(controller,'hasOverlay')+'\n'+preview+'''        previewCreated=true;
}
public static void main(String[] args)throws Exception {
 Context c=new Context();OverlayManager.info=null;if(hasOverlay(c,"custom"))throw new AssertionError("missing overlay accepted");
 OverlayInfo info=new OverlayInfo();OverlayManager.info=info;
 if(!hasOverlay(c,"custom"))throw new AssertionError("valid overlay rejected");
 info.targetPackageName="other";if(hasOverlay(c,"custom"))throw new AssertionError("target mismatch accepted");info.targetPackageName="android";
 info.category="other";if(hasOverlay(c,"custom"))throw new AssertionError("category mismatch accepted");info.category="font";
 info.isMutable=false;if(hasOverlay(c,"custom"))throw new AssertionError("immutable overlay accepted");
 Context.manager=null;if(hasOverlay(c,"custom"))throw new AssertionError("missing manager accepted");
 for(int state=0;state<3;state++){
  Fragment.gone=state==0;Activity.destroyed=state==1;
  OverlayGuard guard=new OverlayGuard();File f=File.createTempFile("preview-test-",".font");
  guard.showPreview(f,"test",null);
  if(state<2&&(f.exists()||guard.previewCreated))throw new AssertionError("dead preview activity used");
  if(state==2&&!guard.previewCreated)throw new AssertionError("normal preview blocked");f.delete();
 }
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
files['android/os/ParcelFileDescriptor.java']='''package android.os;public class ParcelFileDescriptor implements AutoCloseable {public void close(){}}'''
files['PreviewCache.java']='''import android.os.*;import android.graphics.Typeface;import android.graphics.fonts.*;
class PreviewCache {String mPreviewDigest;Typeface mPreviewTypeface;static int opens;static boolean fail;
static PreviewCache manager(){return new PreviewCache();}ParcelFileDescriptor openUserCustomFont()throws Exception{opens++;if(fail)throw new Exception();return new ParcelFileDescriptor();}
'''+method(importer,'previewTypeface')+'''
public static void main(String[] args){PreviewCache p=new PreviewCache();Bundle b=new Bundle();b.putBoolean("available",true);b.putString("digest","A");
Typeface a=p.previewTypeface(b);if(opens!=1||a==Typeface.DEFAULT)throw new AssertionError();
for(int i=0;i<20;i++)if(p.previewTypeface(b)!=a)throw new AssertionError();if(opens!=1)throw new AssertionError("repeated preview IPC");
b.putString("digest","B");if(p.previewTypeface(b)==a||opens!=2)throw new AssertionError("stale replacement preview");
b.putBoolean("available",false);if(p.previewTypeface(b)!=Typeface.DEFAULT||p.mPreviewTypeface!=null)throw new AssertionError("removed preview retained");
b.putBoolean("available",true);fail=true;if(p.previewTypeface(b)!=Typeface.DEFAULT)throw new AssertionError();fail=false;
if(p.previewTypeface(b)==Typeface.DEFAULT||opens!=4)throw new AssertionError("failure cached permanently");
}}
'''
files['DestinationRepair.java']='''import java.io.*;import org.json.JSONObject;
class VerityUtils {static boolean sealed;static boolean hasFsverity(String p){return sealed;}}
class DestinationRepair {JSONObject mLoaded;
'''+method(store,'prepareDestination')+'''
public static void main(String[] args)throws Exception {DestinationRepair s=new DestinationRepair();File f=File.createTempFile("unsealed-",".font");
s.prepareDestination(f,"a");if(f.exists())throw new AssertionError("unsealed orphan not removed");
f.createNewFile();VerityUtils.sealed=true;s.prepareDestination(f,"a");if(!f.exists())throw new AssertionError("sealed inode removed");
VerityUtils.sealed=false;s.mLoaded=new JSONObject("a");try{s.prepareDestination(f,"a");throw new AssertionError("loaded inode replaced");}catch(IOException expected){}
if(!f.exists())throw new AssertionError("loaded inode lost");s.mLoaded=new JSONObject("b");s.prepareDestination(f,"a");if(f.exists())throw new AssertionError();
}}
'''
settings=(source/'packages/apps/Settings/src/com/android/settings/display/FontStyleSettings.java').read_text()
files['android/R.java']='package android;public class R {public static class string{public static int cancel=1,ok=2;}}'
files['android/content/DialogInterface.java']='package android.content;public interface DialogInterface{interface OnClickListener{void onClick(DialogInterface d,int which);}}'
files['android/app/AlertDialog.java']='''package android.app;public class AlertDialog {public static class Builder {
android.content.DialogInterface.OnClickListener positive;public Builder(Activity a){}public Builder setTitle(int r){return this;}public Builder setMessage(int r){return this;}
public Builder setNegativeButton(int r,android.content.DialogInterface.OnClickListener l){return this;}
public Builder setPositiveButton(int r,android.content.DialogInterface.OnClickListener l){positive=l;return this;}public void show(){positive.onClick(null,0);}}}'''
files['Removal.java']='''import android.app.*;import android.os.*;import android.widget.Toast;
class R {static class string{static int font_custom_remove=1,font_custom_remove_note=2,font_custom_apply_error=3;}}
class FontStyleConfig{static final String CUSTOM="custom",DEFAULT="default";}
class RemovalFragment {boolean selected,restore=true;int updates,prompts;
Activity getActivity(){return new Activity();}String getDefaultKey(){return selected?"custom":"default";}
boolean setDefaultKey(String key){if(!restore)return false;selected=false;return true;}
void updateCandidates(){updates++;}void showRestartDialog(){prompts++;}
'''+method(settings,'isCustomFontSelected')+method(settings,'restoreBeforeRemovingImport')+method(settings,'onCustomFontRemoved')+'''
}
class Removal {RemovalFragment mFragment=new RemovalFragment();String mPreviewDigest="old";Object mPreviewTypeface=new Object();static Bundle imported;static int removes;
static Bundle status(){return imported;}static Removal manager(){return new Removal();}void removeUserCustomFont(){removes++;}
'''+method(importer,'remove')+'''
public static void main(String[] args){for(boolean selected:new boolean[]{false,true})for(boolean boot:new boolean[]{false,true}){
Removal p=new Removal();p.mFragment.selected=selected;imported=new Bundle();imported.putBoolean("activeAtBoot",boot);removes=0;p.remove();
if(removes!=1||p.mFragment.updates!=1||p.mFragment.prompts!=((selected||boot)?1:0)||p.mFragment.selected||p.mPreviewTypeface!=null)throw new AssertionError("removal state/restart prompt");}
Removal bad=new Removal();bad.mFragment.selected=true;bad.mFragment.restore=false;removes=0;bad.remove();if(removes!=0||bad.mFragment.updates!=0)throw new AssertionError("failed restore still removed font");
}}
'''
assert 'mImportedTypeface = null;' in settings
assert 'VerityUtils.setUpFsverity' in store and 'mBootMarker' in store
with tempfile.TemporaryDirectory(prefix='font-lifecycle-') as tmp:
 d=pathlib.Path(tmp)
 for n,t in files.items():p=d/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t)
 subprocess.run([str(java/'javac'),'-d',str(d),*[str(d/n) for n in files]],check=True)
 for cls in ('com.android.settings.display.Completion','BootCleanup','com.android.settings.display.OverlayGuard','PreviewCache','DestinationRepair','Removal'):
  subprocess.run([str(java/'java'),'-cp',str(d),cls],check=True)
print('PASS: IPC completion/lifecycle, overlay checks, boot cleanup, digest preview cache/invalidation/retry, active/boot font removal restart prompt, unsealed orphan repair without replacing loaded/sealed inodes')
