"""Exercise the production depth target renderer across home/folder transition ordering."""
import argparse, pathlib, subprocess, tempfile, re, json
p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=pathlib.Path)
source=p.parse_args().source.resolve(strict=True)
launcher=source/'packages/apps/Launcher3'
relative='quickstep/src/com/android/quickstep/util/BaseDepthController.java'
text=(launcher/relative).read_text()

def method(text,name):
    m=re.search(r'    (?:public|private) [^\n]+ '+name+r'\([^)]*\) \{',text)
    assert m,name
    pos=m.end();depth=1
    while depth:
        depth+=(text[pos]=='{')-(text[pos]=='}');pos+=1
    return text[m.start():pos]

fixture='''import java.util.*;
class View {RenderEffect effect;void setRenderEffect(RenderEffect e){effect=e;}}
class RenderEffect {final float radius;RenderEffect(float r){radius=r;}
 static RenderEffect createBlurEffect(float x,float y,Object mode){if(x<=0||y<=0)throw new AssertionError();return new RenderEffect(x);}}
class Shader {enum TileMode {DECAL}}
class Flags {static boolean enabled=true;static boolean allAppsBlur(){return enabled;}}
class Log {static void d(String t,String s){}}
class Property {float value;float getValue(){return value;}}
class LauncherState {boolean blur;LauncherState(boolean b){blur=b;}boolean shouldBlurWorkspace(LauncherState target){return target.blur;}}
class StateManager<S,L> {LauncherState target=new LauncherState(false),state=target;
 LauncherState getTargetState(){return target;}LauncherState getState(){return state;}LauncherState getCurrentStableState(){return state;}}
class Launcher {final List<View> targets=List.of(new View(),new View());final StateManager<LauncherState,Launcher> state=new StateManager<>();
 List<View> getDepthBlurTargets(){return targets;}StateManager<LauncherState,Launcher> getStateManager(){return state;}}
class Probe {
 static final String TAG="test";Launcher mLauncher=new Launcher();int mCurrentBlur=0;Property folderDepth=new Property();
'''
checks='''
 void expect(float r){for(View v:mLauncher.targets){float actual=v.effect==null?0:v.effect.radius;if(actual!=r)throw new AssertionError("expected "+r+" got "+actual);}}
 public static void main(String[] args){Probe p=new Probe();
 p.mLauncher.state.target=new LauncherState(true);if(!p.blurWorkspaceDepthTargets())throw new AssertionError("Policy query changed at zero blur");
 p.mCurrentBlur=100;p.mLauncher.state.target=new LauncherState(true);p.blurWorkspaceDepthTargets();p.expect(100);
 // Opening a folder, followed by the late return-to-NORMAL update, must retain icon blur.
 p.folderDepth.value=.3f;p.blurWorkspaceDepthTargets();p.expect(100);
 p.mCurrentBlur=0;p.mLauncher.state.target=new LauncherState(false);p.blurWorkspaceDepthTargets();p.expect(60);
 p.folderDepth.value=0;p.blurWorkspaceDepthTargets();p.expect(0);
 // Folder blur remains supported with the optional all-apps blur flag disabled.
 Flags.enabled=false;p.folderDepth.value=.3f;p.blurWorkspaceDepthTargets();p.expect(60);
 p.folderDepth.value=.15f;p.blurWorkspaceDepthTargets();p.expect(30);
 p.folderDepth.value=0;p.blurWorkspaceDepthTargets();p.expect(0);
 Flags.enabled=true;p.mCurrentBlur=120;p.mLauncher.state.target=new LauncherState(true);
 p.folderDepth.value=.3f;p.blurWorkspaceDepthTargets();p.expect(120);
 p.folderDepth.value=0;p.blurWorkspaceDepthTargets();p.expect(120);
 p.mLauncher.state.target=new LauncherState(false);p.blurWorkspaceDepthTargets();p.expect(0);
 }}'''
jdk=source/'prebuilts/jdk/jdk21/linux-x86/bin'
with tempfile.TemporaryDirectory(prefix='folder-blur-') as tmp:
    root=pathlib.Path(tmp);java=root/'Probe.java'
    def compile_and_run(content):
        java.write_text(fixture+method(content,'blurWorkspaceDepthTargets')+method(content,'clearWorkspaceDepthTargets')+checks)
        subprocess.run([str(jdk/'javac'),str(java)],check=True)
        return subprocess.run([str(jdk/'java'),'-cp',str(root),'Probe'],capture_output=True,text=True)
    result=compile_and_run(text)
    assert result.returncode==0,result.stdout+result.stderr
    statement='float folderBlur = 60f * Math.min(1f, Math.max(0f, folderDepth.getValue() / 0.3f));'
    assert text.count(statement)==1
    old=text.replace(statement,'float folderBlur = 0f;')
    negative=compile_and_run(old)
    assert negative.returncode!=0 and 'expected 60.0 got 0.0' in negative.stderr,negative.stderr
folder=(launcher/'src/org/avium/launcher/folder/AviumFolderDepthAnimator.java').read_text()
quickstep=(launcher/'quickstep/src/com/android/launcher3/uioverrides/QuickstepLauncher.java').read_text()
assert 'animateFolderBlur' not in folder+quickstep
assert 'folderDepth.animateToValue' in folder
assert 'mFolderWorkspaceAnimator' not in quickstep
assert 'public UnfoldTransitionProgressProvider getUnfoldTransitionProgressProvider()' in quickstep
print(json.dumps({'passed':True,'actual_renderer_transition_orderings':True,
 'old_renderer_negative_control_failed':True,'duplicate_folder_writer_removed':True,
 'reported_screenshot_reproduced_on_hardware':False},indent=2))
