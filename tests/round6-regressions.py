# SPDX-License-Identifier: Apache-2.0
"""Host checks for the round-six approval and launcher transition fixes."""
import argparse
import pathlib

parser = argparse.ArgumentParser()
parser.add_argument('source', type=pathlib.Path)
root = parser.parse_args().source.resolve(strict=True)

interceptor = (root / 'frameworks/base/services/core/java/com/android/server/wm/ActivityStartInterceptor.java').read_text()
assert 'candidate.addFlags(Intent.FLAG_ACTIVITY_FORWARD_RESULT);' in interceptor
assert 'FLAG_ONE_SHOT | FLAG_IMMUTABLE' in interceptor
assert 'launchGrantStillMatches' in interceptor
assert 'approval.allowed' in interceptor

transition = (root / 'packages/apps/Launcher3/quickstep/src/com/android/launcher3/QuickstepTransitionManager.java').read_text()
back = (root / 'packages/apps/Launcher3/quickstep/src/com/android/quickstep/LauncherBackAnimationController.java').read_text()
depth = (root / 'packages/apps/Launcher3/quickstep/src/com/android/launcher3/statehandlers/DepthController.java').read_text()
reveal = (root / 'packages/apps/Launcher3/quickstep/src/com/android/quickstep/util/ScalingWorkspaceRevealAnim.kt').read_text()
assert 'cancelAppLaunchDepthAnimation();' in transition
assert 'mAppLaunchDepthAnimator' in transition
assert 'restoreStateDepth()' in back and 'restoreStateDepth()' in reveal
assert 'target != null ? target : mLauncher.getStateManager().getState()' in depth
assert 'mQuickstepTransitionManager.cancelAppLaunchDepthAnimation();' in back

# Structural integration checks supplement the executable method fixtures.
assert transition.count('cancelAppLaunchDepthAnimation();') >= 3
assert back.count('restoreStateDepth();') >= 1
assert 'FLAG_IMMUTABLE' in interceptor and 'FLAG_ACTIVITY_FORWARD_RESULT' in interceptor
import runpy, sys
sys.argv = [str(pathlib.Path(__file__).with_name('round6-behavior-regressions.py')), str(root)]
runpy.run_path(sys.argv[0], run_name='__main__')
print('{"passed": true, "approval_forward_result_immutable_boundary": true, '
      '"launcher_depth_cancel_and_restore": true, "security_capability_checks_retained": true}')
