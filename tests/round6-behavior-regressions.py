# SPDX-License-Identifier: Apache-2.0
"""Execute production Java methods with bounded fixtures and failing mutants."""
import argparse,json,pathlib,re,subprocess,tempfile
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source',type=pathlib.Path)
root=parser.parse_args().source.resolve(strict=True)
def method(text,name):
 match=re.search(r'^.*\b'+name+r'\([^;{]*\)\s*\{',text,re.M);assert match,name
 pos=match.end();depth=1
 while depth:
  depth+=(text[pos]=='{')-(text[pos]=='}');pos+=1
 return text[match.start():pos]
launcher=root/'packages/apps/Launcher3/quickstep/src'
transition=(launcher/'com/android/launcher3/QuickstepTransitionManager.java').read_text()
depth=(launcher/'com/android/launcher3/statehandlers/DepthController.java').read_text()
interceptor=(root/'frameworks/base/services/core/java/com/android/server/wm/ActivityStartInterceptor.java').read_text()
pending=(root/'frameworks/base/services/core/java/com/android/server/am/PendingIntentRecord.java').read_text()
candidate=interceptor[interceptor.index('                candidate.setSelector(null);'):interceptor.index('                final LaunchApproval approval =')].replace('android.content.ComponentName','ComponentName')
immutable=pending[pending.index('            final boolean immutable ='):pending.index('            // Apply any launch flags')].strip()
cancel=method(transition,'cancelAppLaunchDepthAnimation')
restore=method(depth,'restoreStateDepth');setstate=method(depth,'setState')
code='''
public class Round6 {
 static void check(boolean v){if(!v)throw new AssertionError();}
 static class LauncherState {static final LauncherState BACKGROUND_APP=new LauncherState(.7f);float depth;LauncherState(float v){depth=v;}float getDepth(Launcher l){return depth;}}
 static class Manager {LauncherState state=new LauncherState(0),target;LauncherState getState(){return state;}LauncherState getTargetState(){return target;}}
 static class Launcher {Manager manager=new Manager();Manager getStateManager(){return manager;}}
 static class Property {float value;void setValue(float v){value=v;}}
 static class ObjectAnimator {boolean cancelled;void cancel(){cancelled=true;}}
 Launcher mLauncher=new Launcher();Property stateDepth=new Property();ObjectAnimator mAppLaunchDepthAnimator;boolean layer;
 void cleanupAppLaunchBlurLayer(){layer=false;}
 void addOnDrawListener(){}
''' +cancel+'\n'+restore+'\n'+setstate+'''
 static class ComponentName {String pkg,name;ComponentName(String p,String n){pkg=p;name=n;}}
 static class Intent {static final int FLAG_ACTIVITY_FORWARD_RESULT=0x02000000,IMMUTABLE_FLAGS=0,FILL_IN_DATA=1;int flags;Object selector;String pkg;ComponentName component;
 Intent(){}Intent(Intent other){flags=other.flags;selector=other.selector;pkg=other.pkg;component=other.component;}
 void setSelector(Object s){selector=s;}void setPackage(String s){pkg=s;}void setComponent(ComponentName c){component=c;}
 void addFlags(int f){flags|=f;}int getFlags(){return flags;}void setFlags(int f){flags=f;}int fillIn(Intent i,int f){return 0;}}
 static class PendingIntent {static final int FLAG_IMMUTABLE=1;}
 static class Key {int flags=PendingIntent.FLAG_IMMUTABLE;String requestResolvedType="type";}
 static Intent freeze(){Intent candidate=new Intent();String targetPackage="target";
 class ActivityInfo {String name="Activity";}class Resolved {ActivityInfo activityInfo=new ActivityInfo();}Resolved resolved=new Resolved();
''' +candidate+'''
 return new Intent(candidate);}
 static Intent send(Intent stored){Intent finalIntent=new Intent(stored);Key key=new Key();Intent intent=null;String resolvedType=null;
 int flagsMask=Intent.FLAG_ACTIVITY_FORWARD_RESULT,flagsValues=flagsMask;
''' +immutable+'''
 return finalIntent;}
 public static void main(String[] args){
 Round6 r=new Round6();r.stateDepth.value=.7f;r.restoreStateDepth();check(r.stateDepth.value==0);
 r.mLauncher.manager.target=new LauncherState(.4f);r.restoreStateDepth();check(r.stateDepth.value==.4f);
 r.mLauncher.manager.target=null;r.mLauncher.manager.state=new LauncherState(.9f);r.restoreStateDepth();check(r.stateDepth.value==.9f);
 ObjectAnimator old=new ObjectAnimator();r.mAppLaunchDepthAnimator=old;r.layer=true;r.cancelAppLaunchDepthAnimation();
 check(old.cancelled && r.mAppLaunchDepthAnimator==null && !r.layer);r.cancelAppLaunchDepthAnimation();
 Intent sent=send(freeze());check((sent.flags&Intent.FLAG_ACTIVITY_FORWARD_RESULT)!=0);check(sent.component.pkg.equals("target"));
 check(send(new Intent()).flags==0);
 }}
'''
java=root/'prebuilts/jdk/jdk21/linux-x86/bin'
with tempfile.TemporaryDirectory(prefix='round6-production-') as tmp:
 d=pathlib.Path(tmp)
 def execute(source,expect_pass):
  (d/'Round6.java').write_text(source)
  build=subprocess.run([str(java/'javac'),str(d/'Round6.java')],capture_output=True,text=True)
  assert build.returncode==0,build.stderr
  run=subprocess.run([str(java/'java'),'-cp',str(d),'Round6'],capture_output=True,text=True)
  assert (run.returncode==0)==expect_pass,run.stderr
 execute(code,True)
 mutants=[code.replace('candidate.addFlags(Intent.FLAG_ACTIVITY_FORWARD_RESULT);',''),
  code.replace('if (animation != null) animation.cancel();',''),
  code.replace('setState(target != null ? target : mLauncher.getStateManager().getState());',''),
  code.replace('target != null ? target : mLauncher.getStateManager().getState()','mLauncher.getStateManager().getState()')]
 for mutant in mutants:assert mutant!=code;execute(mutant,False)
print(json.dumps(dict(passed=True,extracted_java_methods=True,immutable_sender_boundary_executed=True,negative_controls_rejected=4,phone_test_separate=True)))
