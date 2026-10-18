# SPDX-License-Identifier: Apache-2.0
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
with tempfile.TemporaryDirectory(prefix='folder-depth-dispatch-') as tmp:
    root=pathlib.Path(tmp);java=root/'Probe.java'
    dispatch_fixture=fixture.replace('static void d(String t,String s){}','static void d(String t,String s){} static void v(String t,String s){}')
    dispatch_fixture=dispatch_fixture.replace('boolean shouldBlurWorkspace(', 'float getDepth(Launcher l){return .7f;}boolean shouldBlurWorkspace(')
    dispatch_fixture=dispatch_fixture.replace('List<View> getDepthBlurTargets()', 'Root getRootView(){return new Root();}Scrim getScrimView(){return new Scrim();}List<View> getDepthBlurTargets()')
    dispatch_fixture=dispatch_fixture.replace('static final String TAG="test";', '''static final String TAG="test";
 float mDepth;SurfaceControl mBaseSurface=new SurfaceControl(),mBlurSurface;Wallpaper mWallpaperManager=new Wallpaper();
 boolean mWaitingOnSurfaceValidity,mHasContentBehindLauncher,mPauseBlurs,mCrossWindowBlursEnabled=true,mInEarlyWakeUp;
 int mMaxBlurRadius=100;
 static boolean enableOverviewBackgroundWallpaperBlur(){return false;}
 void applySurfaceTransaction(SurfaceTransaction t,boolean immediate){}void onInvalidSurface(){}
 void setEarlyWakeup(Object t,boolean b){mInEarlyWakeUp=b;}
 static float mapDepthToBlur(float d){return Math.min(1f,d/.3f);}
 protected void applyDepthAndBlur(){applyDepthAndBlur(null,false,true);}
 ''')
    dependencies='''
@interface Nullable {}
class IBinder {}
class Root {IBinder getWindowToken(){return new IBinder();}}
class Scrim {boolean isFullyOpaque(){return false;}}
class Wallpaper {void setWallpaperZoomOut(IBinder t,float d){}}
class SurfaceControl {boolean valid=true;boolean isValid(){return valid;}}
class SurfaceTransaction {SurfaceTransaction forSurface(SurfaceControl s){return this;}
 SurfaceTransaction setBackgroundBlurRadius(int r){return this;}SurfaceTransaction setOpaque(boolean b){return this;}
 Object getTransaction(){return this;}}
class BlurUtils {static boolean enabled=true;static boolean supportsBlursOnWindows(){return enabled;}}
class Utilities {static int dpToPx(int n){return 3;}static float boundToRange(float v,float l,float h){return Math.max(l,Math.min(v,h));}}
'''
    dispatch_checks='''
 void expect(float r){for(View v:mLauncher.targets){float actual=v.effect==null?0:v.effect.radius;if(actual!=r)throw new AssertionError("expected "+r+" got "+actual);}}
 public static void main(String[] args){Probe p=new Probe();
 // Exercise actual setDepth + applyDepthAndBlur; do not call the renderer directly.
 p.folderDepth.value=.3f;p.setDepth(.3f);p.expect(60);
 p.mLauncher.state.target=new LauncherState(true);p.setDepth(.7f);p.expect(100);
 p.mLauncher.state.target=new LauncherState(false);
 p.folderDepth.value=0;p.setDepth(.7f);p.expect(0); // max aggregate unchanged
 p.folderDepth.value=.3f;p.setDepth(.7f);p.expect(60);
 p.folderDepth.value=.15f;p.setDepth(.699f);p.expect(30);
 p.folderDepth.value=0;p.setDepth(.698f);p.expect(0);
 p.folderDepth.value=.3f;p.setDepth(.2f);p.expect(60);
 p.folderDepth.value=.15f;p.setDepth(.205f);p.expect(30); // small nonzero wallpaper blur delta
 p.folderDepth.value=0;p.setDepth(.209f);p.expect(0);
 p.mLauncher.state.target=new LauncherState(true);p.setDepth(.7f);p.expect(100);
 p.mLauncher.state.target=new LauncherState(false);p.setDepth(.7f);p.expect(0); // only policy changed
 p.folderDepth.value=.3f;p.mBaseSurface.valid=false;p.setDepth(.7f);p.expect(0);
 }}'''
    def dispatch(content):
        java.write_text('import java.util.*;\n'+dependencies+dispatch_fixture.replace('import java.util.*;','')+method(content,'setDepth')
            +method(content,'applyDepthAndBlur')+method(content,'blurWorkspaceDepthTargets')
            +method(content,'clearWorkspaceDepthTargets')+dispatch_checks)
        subprocess.run([str(jdk/'javac'),str(java)],check=True)
        return subprocess.run([str(jdk/'java'),'-cp',str(root),'Probe'],capture_output=True,text=True)
    result=dispatch(text);assert result.returncode==0,result.stdout+result.stderr
    for mutant in (
        re.sub(r'(if \(Float.compare\(mDepth, depthF\) == 0\) \{).*?(\n        mDepth = depthF;)',r'\1 return;\n        }\2',text,flags=re.S),
        text.replace('            blurWorkspaceDepthTargets();\n            return;','            return;',1)):
        result=dispatch(mutant);assert result.returncode!=0 and 'AssertionError' in result.stderr,result.stderr
quickstep=(launcher/'quickstep/src/com/android/launcher3/uioverrides/QuickstepLauncher.java').read_text()
assert 'animateFolderBlur' not in folder+quickstep
assert 'folderDepth.animateToValue' in folder
assert 'mFolderWorkspaceAnimator' not in quickstep
assert 'public UnfoldTransitionProgressProvider getUnfoldTransitionProgressProvider()' in quickstep
print(json.dumps({'passed':True,'actual_renderer_transition_orderings':True,
 'actual_depth_dispatch_equal_max_and_small_delta_paths_passed':True,
 'removed_dispatch_fixes_negative_controls_failed':2,
 'old_renderer_negative_control_failed':True,'duplicate_folder_writer_removed':True,
 'reported_screenshot_reproduced_on_hardware':False},indent=2))
