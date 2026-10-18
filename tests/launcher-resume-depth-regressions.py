# SPDX-License-Identifier: Apache-2.0
"""Exercise actual resumed-home recovery with no animation completion callback."""
import argparse,json,pathlib,re,subprocess,tempfile
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source',type=pathlib.Path)
root=parser.parse_args().source.resolve(strict=True)
text=(root/'packages/apps/Launcher3/quickstep/src/com/android/launcher3/uioverrides/QuickstepLauncher.java').read_text()
def method(name):
 match=re.search(r'^.*\b'+name+r'\([^;{]*\)\s*\{',text,re.M);assert match,name
 pos=match.end();depth=1
 while depth:depth+=(text[pos]=='{')-(text[pos]=='}');pos+=1
 return text[match.start():pos]
code='''
class ResumeBase {int baseCalls;protected void onDeferredResumed(){baseCalls++;}}
public class ResumeDepth extends ResumeBase {
 static final int NORMAL=0,OVERVIEW=1,ALL_APPS=2;
 boolean resumed=true,invisible,mIsPredictiveBackToHomeInProgress;int pendingCalls;
 static class Manager {boolean transition;int state=NORMAL;boolean isInTransition(){return transition;}boolean isInStableState(int s){return state==s;}}
 static class Workspace {boolean overlay;boolean isOverlayShown(){return overlay;}}
 final Manager manager=new Manager();final Workspace workspace=new Workspace();
 final StringBuilder order=new StringBuilder();float stateDepth=.7f,folderDepth=.4f,widgetDepth=.2f;boolean paused=true,oldWriter=true;
 class Transition {void cancelAppLaunchDepthAnimation(){order.append("cancel,");oldWriter=false;}}
 class Depth {void restoreStateDepth(){order.append("restore,");stateDepth=0;}void pauseBlursOnWindows(boolean v){order.append("unpause");paused=v;}}
 Transition mAppTransitionManager=new Transition();Depth mDepthController=new Depth();
 boolean hasBeenResumed(){return resumed;}boolean isForceInvisible(){return invisible;}
 Manager getStateManager(){return manager;}Workspace getWorkspace(){return workspace;}
 void handlePendingActivityRequest(){pendingCalls++;}
''' +method('onDeferredResumed')+'\n'+method('restoreDepthAfterUnanimatedResume')+'''
 static void check(boolean v){if(!v)throw new AssertionError();}
 static void unchanged(ResumeDepth l){l.onDeferredResumed();check(l.stateDepth==.7f&&l.paused&&l.oldWriter&&l.order.length()==0);}
 public static void main(String[] args){
  // A queued second BACK resumes a stable home without creating any home animation.
  ResumeDepth l=new ResumeDepth();l.onDeferredResumed();if(l.oldWriter)l.stateDepth=.7f;
  check(l.stateDepth==0&&!l.paused&&!l.oldWriter);check(l.folderDepth==.4f&&l.widgetDepth==.2f);
  check(l.order.toString().equals("cancel,restore,unpause"));check(l.baseCalls==1&&l.pendingCalls==1);
  l=new ResumeDepth();l.resumed=false;unchanged(l);
  l=new ResumeDepth();l.invisible=true;unchanged(l);
  l=new ResumeDepth();l.mIsPredictiveBackToHomeInProgress=true;unchanged(l);
  l=new ResumeDepth();l.manager.transition=true;unchanged(l);
  l=new ResumeDepth();l.manager.state=OVERVIEW;unchanged(l);
  l=new ResumeDepth();l.manager.state=ALL_APPS;unchanged(l);
  l=new ResumeDepth();l.workspace.overlay=true;unchanged(l);
  l=new ResumeDepth();l.mAppTransitionManager=null;unchanged(l);
  l=new ResumeDepth();l.mDepthController=null;unchanged(l);
 }
}
'''
java=root/'prebuilts/jdk/jdk21/linux-x86/bin'
with tempfile.TemporaryDirectory(prefix='launcher-resume-depth-') as tmp:
 d=pathlib.Path(tmp)
 def execute(code,expected):
  (d/'ResumeDepth.java').write_text(code)
  build=subprocess.run([str(java/'javac'),str(d/'ResumeDepth.java')],capture_output=True,text=True);assert build.returncode==0,build.stderr
  result=subprocess.run([str(java/'java'),'-cp',str(d),'ResumeDepth'],capture_output=True,text=True)
  assert (result.returncode==0)==expected,result.stderr
 execute(code,True)
 mutants=[code.replace('        restoreDepthAfterUnanimatedResume();',''),
  code.replace('        mAppTransitionManager.cancelAppLaunchDepthAnimation();',''),
  code.replace('        mDepthController.restoreStateDepth();',''),
  code.replace('                || getStateManager().isInTransition()',''),
  code.replace('                || !getStateManager().isInStableState(NORMAL)','')]
 for mutant in mutants:assert mutant!=code;execute(mutant,False)
print(json.dumps(dict(passed=True,actual_deferred_resume_and_recovery_methods=True,queued_back_without_animation_callback=True,legitimate_animation_and_ui_states_preserved=True,independent_folder_widget_channels_preserved=True,negative_controls_rejected=5,phone_acceptance_separate=True)))
