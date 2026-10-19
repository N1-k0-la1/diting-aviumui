# SPDX-License-Identifier: Apache-2.0
"""Run production Folder close methods for drag-out and interrupted-open lifecycles.

Android views/animators are host substitutes; this is not device acceptance.
"""
import argparse
import json
import pathlib
import re
import subprocess
import tempfile


def method(text, name):
    match = re.search(
        r"^    (?:public|private|protected) [^\n]+ \b" + name + r"\([^)]*\) \{",
        text, re.M,
    )
    assert match, name
    end, depth = match.end(), 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[match.start():end]


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=pathlib.Path)
root = parser.parse_args().source.resolve(strict=True)
relative = "packages/apps/Launcher3/src/com/android/launcher3/folder/Folder.java"
text = (root / relative).read_text()
names = ("onDragStart", "completeDragExit", "handleClose", "cancelRunningAnimations",
         "animateClosed")
production = "\n".join(method(text, name) for name in names)

fixture = r"""
import java.util.*;
class Animator {}
class AnimatorListenerAdapter {
    public void onAnimationStart(Animator a) {}
    public void onAnimationEnd(Animator a) {}
}
class AnimatorSet extends Animator {
    boolean running; int cancellations; Float targetDepth;
    Runnable pendingFrame;
    final List<AnimatorListenerAdapter> listeners = new ArrayList<>();
    void addListener(AnimatorListenerAdapter l) { listeners.add(l); }
    boolean isRunning() { return running; }
    void start() { running = true; listeners.forEach(l -> l.onAnimationStart(this)); }
    void cancel() {
        cancellations++; running = false;
        listeners.forEach(l -> l.onAnimationEnd(this));
    }
    void tick() { if (running && pendingFrame != null) pendingFrame.run(); }
    void finish(Context c) {
        if (!running) return;
        if (targetDepth != null) c.folderDepth = targetDepth;
        running = false; listeners.forEach(l -> l.onAnimationEnd(this));
    }
}
class Context {
    float folderDepth = .3f, stateDepth, widgetDepth;
    DragController getDragController() { return new DragController(); }
    Layer getDragLayer() { return new Layer(); }
}
class DragController { void removeDropTarget(Object o) {} }
class Layer { void sendAccessibilityEvent(int e) {} }
class AccessibilityEvent { static final int TYPE_WINDOW_STATE_CHANGED = 1; }
class AviumFolderDepthAnimator {
    static void setDepth(Context c, float v) { c.folderDepth = v; }
    static void addAnimator(AnimatorSet a, Context c, Object r, boolean opening) {
        a.targetDepth = opening ? .3f : 0f;
    }
}
class Content {
    final List<Integer> icons = new ArrayList<>();
    void removeItem(Object v) { icons.remove(v); }
    void setCanAnnouncePageDescriptionForFolder(boolean v) {}
    void completePendingPageChanges() {}
    void snapToPageImmediately(int n) {}
    int getDestinationPage() { return 0; }
}
class Icon { void clearLeaveBehindIfExists() {} }
class Name { void dispatchBackKey() {} }
class Log { static void d(String a, String b) {} }
class DropTarget { static class DragObject extends DragObjectBase {} }
class DragObjectBase { Object dragSource, dragInfo; }
class DragOptions {}
class FolderBase { public void onDragStart(DropTarget.DragObject d, DragOptions o) {} protected void handleClose(boolean animate) {} }
public class Probe extends FolderBase {
    static final String TAG = "Folder";
    static final int STATE_ANIMATING = 1, STATE_OPEN = 2, STATE_CLOSED = 3;
    final Context mActivityContext = new Context();
    final Content mContent = new Content();
    final Icon mFolderIcon = new Icon(); final Name mFolderName = new Name();
    Object mCurrentDragView, mKeyboardInsetAnimationCallback;
    boolean mIsOpen = true, mIsAnimatingClosed, mIsEditingName, mItemsInvalidated;
    boolean mIsDragInProgress, mItemAddedBackToSelfViaIcon, mRearrangeOnClose;
    int mState = STATE_OPEN, closes, rearranges;
    AnimatorSet mCurrentAnimator, closeAnimation;
    List<Integer> getIconsInReadingOrder() { return mContent.icons; }
    void executeWithContentUpdateSuppressed(Runnable r) { r.run(); }
    void removeFolderContent(boolean animate, Object item) {}
    void close(boolean animate) { handleClose(animate); }
    void closeComplete(boolean animated) { closes++; mState = STATE_CLOSED; }
    void clearDragInfo() {} void rearrangeChildren() { rearranges++; }
    void post(Runnable r) { r.run(); } void announceAccessibilityChanges() {}
    Object getResources() { return null; }
    void setWindowInsetsAnimationCallback(Object o) {}
    Manager getFolderAnimationManager() { return new Manager(); }
    class Manager {
        AnimatorSet createAnimatorSet(boolean opening) {
            closeAnimation = new AnimatorSet(); return closeAnimation;
        }
    }
    void addAnimationStartListeners(AnimatorSet a) {
        a.addListener(new AnimatorListenerAdapter() {
            public void onAnimationStart(Animator unused) { mCurrentAnimator = a; mState = STATE_ANIMATING; }
            public void onAnimationEnd(Animator unused) { mCurrentAnimator = null; }
        });
    }
"""

checks = r"""
    static void check(boolean v, String why) { if (!v) throw new AssertionError(why); }
    static Probe folder(int count, boolean opening) {
        Probe p = new Probe();
        for (int i = 0; i < count; i++) p.mContent.icons.add(i);
        if (opening) {
            p.mCurrentAnimator = new AnimatorSet();
            p.mCurrentAnimator.pendingFrame = () -> p.mActivityContext.folderDepth = .3f;
            p.mCurrentAnimator.start(); p.mState = STATE_ANIMATING;
            p.mActivityContext.folderDepth = .12f;
        }
        return p;
    }
    void dragOut(int index) {
        DropTarget.DragObject d = new DropTarget.DragObject();
        d.dragSource = this; d.dragInfo = mContent.icons.get(index);
        mCurrentDragView = d.dragInfo;
        onDragStart(d, new DragOptions()); completeDragExit();
    }
    static void earlyClose(Probe p, AnimatorSet opening) {
        check(p.closes == 1 && p.mState == STATE_CLOSED, "folder must close");
        check(p.mActivityContext.folderDepth == 0, "closed folder retained blur");
        check(p.closeAnimation == null, "single-icon folder must not create close animation");
        if (opening != null) {
            opening.tick();
            check(!opening.running && opening.cancellations == 1, "opening writer still running");
            check(p.mActivityContext.folderDepth == 0, "late opening frame restored blur");
        }
    }
    public static void main(String[] args) {
        // The reported dock -> workspace folder has two items. Either drag leaves one.
        for (boolean opening : new boolean[]{false, true}) {
            for (int index = 0; index < 2; index++) {
                Probe p = folder(2, opening); AnimatorSet old = p.mCurrentAnimator;
                p.dragOut(index); earlyClose(p, old);
                check(p.mIsDragInProgress && p.mRearrangeOnClose, "drag bookkeeping changed");
            }
        }
        for (int count = 0; count <= 1; count++) {
            Probe p = folder(count, true); AnimatorSet old = p.mCurrentAnimator;
            p.close(true); earlyClose(p, old);
        }
        // Immediate close (including disabled animations) also cancels an opening writer.
        Probe p = folder(2, true); AnimatorSet old = p.mCurrentAnimator;
        p.close(false); earlyClose(p, old);
        // A normal folder with >=2 remaining icons keeps its smooth blur fade-out.
        for (int count : new int[]{2, 3, 8}) {
            p = folder(count, false); p.close(true);
            check(p.closes == 0 && p.mIsAnimatingClosed, "normal close animation skipped");
            check(p.mActivityContext.folderDepth == .3f, "normal close snapped blur");
            p.closeAnimation.finish(p.mActivityContext);
            check(p.closes == 1 && p.mActivityContext.folderDepth == 0, "animated close failed");
        }
        // With a failed drag's item returned, close must again use the multi-item animation.
        p = folder(2, true); old = p.mCurrentAnimator; p.close(true);
        check(!old.running && p.closeAnimation.running, "interrupted open not handed to close");
        p.closeAnimation.finish(p.mActivityContext);
        check(p.mActivityContext.folderDepth == 0, "returned-item close retained blur");
        // Another close request during an active close must not replace/cancel that animator.
        p = folder(3, false); p.close(true); old = p.closeAnimation; p.close(true);
        check(old == p.closeAnimation && old.running && old.cancellations == 0,
                "reentrant close animation changed");
        old.finish(p.mActivityContext);
        // Cleanup owns only folder depth; overview/widget depth channels survive.
        p = folder(1, false); p.mActivityContext.stateDepth = .7f;
        p.mActivityContext.widgetDepth = .4f; p.close(true);
        check(p.mActivityContext.folderDepth == 0 && p.mActivityContext.stateDepth == .7f
                && p.mActivityContext.widgetDepth == .4f, "unrelated depth overwritten");
        // A subsequent fresh folder still receives its legitimate opening blur.
        p.mIsOpen = true; p.mContent.icons.add(2);
        AnimatorSet reopen = new AnimatorSet();
        AviumFolderDepthAnimator.addAnimator(reopen, p.mActivityContext, null, true);
        reopen.start(); reopen.finish(p.mActivityContext);
        check(p.mActivityContext.folderDepth == .3f, "new folder lost its blur");
    }
}
"""

java = root / "prebuilts/jdk/jdk21/linux-x86/bin"
with tempfile.TemporaryDirectory(prefix="folder-drag-close-") as temp:
    directory = pathlib.Path(temp)

    def execute(code):
        file = directory / "Probe.java"
        file.write_text(fixture + code + checks)
        build = subprocess.run([str(java / "javac"), str(file)], capture_output=True, text=True)
        assert build.returncode == 0, build.stderr
        return subprocess.run([str(java / "java"), "-cp", str(directory), "Probe"],
                              capture_output=True, text=True)

    result = execute(production)
    assert result.returncode == 0, result.stdout + result.stderr
    # Removing the cleanup must fail, even after the opening animation has finished.
    close = method(production, "animateClosed")
    reset = "            AviumFolderDepthAnimator.setDepth(mActivityContext, 0f);\n"
    assert close.count(reset) == 1
    # Omitting cancellation on the early return recreates the rapid-open stale writer.
    cancel = "            cancelRunningAnimations();\n"
    assert close.count(cancel) == 1
    late_cancel = close.replace(cancel, "")
    for mutant, expected in ((close.replace(reset, ""), "closed folder retained blur"),
                             (late_cancel, "opening writer still running")):
        result = execute(production.replace(close, mutant))
        assert result.returncode != 0 and expected in result.stderr, result.stderr

print(json.dumps({
    "passed": True,
    "production_methods_executed": list(names),
    "both_dragged_icons_and_interrupted_open": True,
    "zero_and_one_icon_close": True,
    "immediate_animated_and_reentrant_close": True,
    "negative_controls_rejected": 2,
    "android_views_and_animators": "host substitutes",
    "new_launcher_phone_tested": False,
}, indent=2))
