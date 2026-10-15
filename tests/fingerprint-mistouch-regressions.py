"""Run production token conversion and the full mistouch controller with host Android fixtures."""
import argparse, json, os, pathlib, subprocess, tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', type=pathlib.Path)
source = parser.parse_args().source.resolve(strict=True)

def run(args, **kwargs):
    result = subprocess.run([str(a) for a in args], text=True, capture_output=True, **kwargs)
    if result.returncode:
        print(result.stdout + result.stderr)
        result.check_returncode()
    return result.stdout

with tempfile.TemporaryDirectory(prefix='fingerprint-mistouch-') as tmp:
    root = pathlib.Path(tmp)
    header = root / 'aidl/android/hardware/keymaster/HardwareAuthToken.h'
    header.parent.mkdir(parents=True)
    header.write_text('''#pragma once
#include <cstdint>
#include <vector>
namespace aidl::android::hardware::keymaster {
enum class HardwareAuthenticatorType : int32_t { PASSWORD=1, FINGERPRINT=2 };
struct Timestamp { int64_t milliSeconds=0; };
struct HardwareAuthToken {
 int64_t challenge=0,userId=0,authenticatorId=0;
 HardwareAuthenticatorType authenticatorType=HardwareAuthenticatorType::PASSWORD;
 Timestamp timestamp; std::vector<uint8_t> mac;
};
}
''')
    code = root / 'tokens.cpp'
    code.write_text('''#include <cassert>
#include <cstring>
#include "Legacy2Aidl.h"
using namespace aidl::android::hardware::keymaster;
using aidl::android::hardware::biometrics::fingerprint::translate;
int main() {
 HardwareAuthToken input;
 input.challenge=0x12345678; input.userId=0x87654321; input.authenticatorId=0x99887766;
 input.authenticatorType=HardwareAuthenticatorType::FINGERPRINT;
 input.timestamp.milliSeconds=0x123456789abcdef;
 input.mac.resize(32); for (size_t i=0;i<32;i++)input.mac[i]=i;
 hw_auth_token_t token; memset(&token,0xa5,sizeof(token));
 assert(translate(input,token)); assert(token.version==HW_AUTH_TOKEN_VERSION);
 assert(token.challenge==input.challenge && token.user_id==input.userId);
 assert(token.authenticator_id==input.authenticatorId);
 assert(be32toh(token.authenticator_type)==2);
 assert(be64toh(token.timestamp)==static_cast<uint64_t>(input.timestamp.milliSeconds));
 assert(memcmp(token.hmac,input.mac.data(),32)==0);
 HardwareAuthToken output; translate(token,output);
 assert(output.challenge==input.challenge && output.userId==input.userId);
 assert(output.authenticatorId==input.authenticatorId && output.mac==input.mac);
 assert(output.timestamp.milliSeconds==input.timestamp.milliSeconds);
 for (size_t size : {0u,1u,31u,33u,256u}) {
  input.mac.resize(size); auto before=token;
  assert(!translate(input,token)); assert(memcmp(&before,&token,sizeof(token))==0);
 }
}
''')
    exe = root / 'tokens'
    compile_token = ['g++', '-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
         '-I' + str(root), '-I' + str(source / 'hardware/libhardware/include_all'),
         '-I' + str(source / 'hardware/xiaomi/aidl/fingerprint/include'), code, '-o', exe]
    run(compile_token)
    run([exe])
    # A poisoned stack token must fail if the version initialization is removed.
    mutant = root / 'Legacy2Aidl.h'
    original = (source / 'hardware/xiaomi/aidl/fingerprint/include/Legacy2Aidl.h').read_text()
    assert '    hat = {};\n    hat.version = HW_AUTH_TOKEN_VERSION;' in original
    mutant.write_text(original.replace('    hat = {};\n    hat.version = HW_AUTH_TOKEN_VERSION;', ''))
    run(compile_token)
    negative = subprocess.run([str(exe)], text=True, capture_output=True)
    assert negative.returncode != 0 and 'token.version==HW_AUTH_TOKEN_VERSION' in negative.stderr
    mutant.unlink()

    # Compile the actual controller unchanged, rather than reproducing its state logic.
    fixtures = {
        'LockPattern.kt': '''package com.android.internal.widget
class LockPatternUtils {
 val disabledUsers=mutableSetOf<Int>()
 fun isLockScreenDisabled(user:Int)=user in disabledUsers
}
''',
        'SelectedUser.kt': '''package com.android.systemui.user.domain.interactor
class SelectedUserInteractor {var user=0;fun getSelectedUserId()=user}
''',
        'Context.kt': '''package android.content
class Context(val manager: android.hardware.SensorManager, val windows: android.view.WindowManager) {
 val contentResolver=Any()
 fun <T> getSystemService(type:Class<T>):T? = type.cast(when(type) {
  android.hardware.SensorManager::class.java -> manager
  android.view.WindowManager::class.java -> windows
  else -> null
 })
}
''',
        'Sensors.kt': '''package android.hardware
class Sensor(val type:Int,val maximumRange:Float=5f) {
 companion object { const val TYPE_PROXIMITY=8; const val TYPE_ACCELEROMETER=1 }
}
class SensorEvent(val sensor:Sensor,val values:FloatArray)
interface SensorEventListener { fun onSensorChanged(event:SensorEvent?); fun onAccuracyChanged(sensor:Sensor?,accuracy:Int) }
class SensorManager(var hasProximity:Boolean=true,var wakeup:Boolean=true) {
 companion object { const val SENSOR_DELAY_NORMAL=3 }
 val prox=Sensor(8); val accel=Sensor(1); var listener:SensorEventListener?=null
 var registrationSucceeds=true; val active=mutableSetOf<Int>(); var lastListener:SensorEventListener?=null
 fun getDefaultSensor(type:Int,wake:Boolean=false):Sensor? = when(type) {
  8 -> if(hasProximity && (!wake || wakeup))prox else null
  1 -> accel
  else -> null
 }
 fun registerListener(l:SensorEventListener,s:Sensor,delay:Int):Boolean {
  if(!registrationSucceeds)return false
  listener=l;lastListener=l;active.add(s.type);return true
 }
 fun unregisterListener(l:SensorEventListener){ active.clear();listener=null }
 fun send(s:Sensor,vararg v:Float){listener?.onSensorChanged(SensorEvent(s,v))}
}
''',
        'Os.kt': '''package android.os
object UserHandle { const val USER_CURRENT=-2 }
object SystemClock { var now=10000L; @JvmStatic fun elapsedRealtime()=now }
''',
        'Settings.kt': '''package android.provider
object Settings { object Secure {
 var enabled=1;val perUser=mutableMapOf<Int,Int>()
 @JvmStatic fun getIntForUser(resolver:Any,key:String,default:Int,user:Int)=perUser[user]?:enabled
}}
''',
        'View.kt': '''package android.view
open class View { var parent:Any?=null;var visibility=INVISIBLE; fun setVisibility(v:Int){visibility=v}; fun requestFocus(){}
 companion object { const val INVISIBLE=4;const val VISIBLE=0 }
}
class WindowManager {
 var current:View?=null;var added=0;var removed=0;var failAdd=false;var failRemove=false
 class LayoutParams(w:Int,h:Int,t:Int,f:Int,p:Int) {
  var privateFlags=0;var layoutInDisplayCutoutMode=0;var fitInsetsTypes=0
  fun setTitle(s:String){}
  companion object {const val MATCH_PARENT=-1}
 }
 fun addView(v:View,p:LayoutParams){if(failAdd)throw IllegalArgumentException("add failed");check(current==null);current=v;v.parent=this;added++}
 fun removeViewImmediate(v:View){if(failRemove)throw IllegalArgumentException("remove failed");check(current===v);v.parent=null;current=null;removed++}
}
''',
        'Keyguard.kt': '''package com.android.keyguard
open class KeyguardUpdateMonitorCallback {
 open fun onUserSwitching(userId:Int){};open fun onUserSwitchComplete(userId:Int){}
 open fun onKeyguardVisibilityChanged(showing:Boolean){};open fun onStartedWakingUp(){}
 open fun onStartedGoingToSleep(why:Int){}
}
class KeyguardUpdateMonitor {var callback:KeyguardUpdateMonitorCallback?=null
 fun registerCallback(c:KeyguardUpdateMonitorCallback){callback=c}
}
''',
        'Core.kt': '''package com.android.systemui
interface CoreStartable {fun start()}
''',
        'Log.kt': '''package android.util
object Log {fun w(tag:String,text:String,error:Throwable){}}
''',
        'Scope.kt': '''package com.android.systemui.dagger
annotation class SysUISingleton
''',
        'Inject.kt': '''package javax.inject
annotation class Inject
''',
        'Wake.kt': '''package com.android.systemui.keyguard
class WakefulnessLifecycle {
 interface Observer {
  fun onStartedGoingToSleep(){};fun onFinishedGoingToSleep(){}
  fun onStartedWakingUp(){};fun onFinishedWakingUp(){}
 }
 var observer:Observer?=null;fun addObserver(o:Observer){observer=o}
}
''',
        'Status.kt': '''package com.android.systemui.plugins.statusbar
class StatusBarStateController {var isDozing=false;var listener:StateListener?=null
 interface StateListener {fun onDozingChanged(isDozing:Boolean){}}
 fun addCallback(c:StateListener){listener=c}
}
''',
        'Biometric.kt': '''package com.android.systemui.statusbar.phone
class BiometricUnlockController {var isWakeAndUnlock=false}
''',
        'State.kt': '''package com.android.systemui.statusbar.policy
class KeyguardStateController {var isShowing=false;var isOccluded=false
 interface Callback {fun onKeyguardShowingChanged(){}}
 var callback:Callback?=null;fun addCallback(c:Callback){callback=c}
 fun change(showing:Boolean,occluded:Boolean=false){isShowing=showing;isOccluded=occluded;callback?.onKeyguardShowingChanged()}
}
''',
        'PreventionView.kt': '''package org.avium.systemui.mistouch
class MistouchPreventionView(c:android.content.Context):android.view.View() {
 interface VolumeKeyCallback {fun onVolumeUpPressed()}
 val callbacks=mutableSetOf<VolumeKeyCallback>()
 fun addCallback(c:VolumeKeyCallback){callbacks.add(c)}
 fun removeCallback(c:VolumeKeyCallback){callbacks.remove(c)}
}
''',
        'Checks.kt': '''package org.avium.systemui.mistouch
import android.content.Context
import android.hardware.*
import android.view.*
import android.provider.Settings
import com.android.keyguard.*
import com.android.systemui.keyguard.*
import com.android.systemui.plugins.statusbar.*
import com.android.systemui.statusbar.phone.*
import com.android.systemui.statusbar.policy.*
class Fixture(wakeup:Boolean=true) {
 val sensors=SensorManager(wakeup=wakeup);val windows=WindowManager();val state=KeyguardStateController()
 val monitor=KeyguardUpdateMonitor();val bio=BiometricUnlockController()
 val lock=com.android.internal.widget.LockPatternUtils()
 val users=com.android.systemui.user.domain.interactor.SelectedUserInteractor()
 val status=StatusBarStateController();val wake=WakefulnessLifecycle()
 val controller=MistouchPreventionWindowController(Context(sensors,windows),lock,users,state,monitor,bio,status,wake)
 fun start(){controller.start()}
 fun visible()=windows.current?.visibility==View.VISIBLE
}
fun main() {
 val f=Fixture();f.start();check(f.windows.current==null);check(f.sensors.active.isEmpty())
 // A stale dozing callback after unlocking may not register sensors or cover the desktop.
 f.status.listener!!.onDozingChanged(true);check(f.windows.current==null)
 f.state.change(true);check(f.sensors.active==setOf(8))
 f.sensors.send(f.sensors.prox,0f);check(f.visible())
 val queued=f.sensors.lastListener!!
 f.state.change(false);check(!f.visible());check(f.windows.current==null);check(f.sensors.active.isEmpty())
 queued.onSensorChanged(SensorEvent(f.sensors.prox,floatArrayOf(0f)));check(f.windows.current==null)
 f.state.change(true);check(!f.visible()) // no retained near state
 f.sensors.send(f.sensors.prox,5f);check(!f.visible())
 // Simulate an upside-down pose; proximity is far, so pose alone cannot block input.
 queued.onSensorChanged(SensorEvent(f.sensors.accel,floatArrayOf(0f,-9.8f,0f)));check(!f.visible())
 f.sensors.send(f.sensors.prox,0f);check(f.visible())
 f.state.change(true,true);check(f.windows.current==null);check(f.sensors.active.isEmpty())
 f.state.change(true);f.sensors.send(f.sensors.prox,0f);check(f.visible())
 f.sensors.send(f.sensors.prox,Float.NaN);check(!f.visible())
 f.sensors.send(f.sensors.prox,-1f);check(!f.visible())
 f.sensors.send(f.sensors.prox);check(!f.visible())
 f.sensors.send(f.sensors.prox,2f);check(f.visible()) // valid nonzero near distance
 Settings.Secure.enabled=0;f.sensors.send(f.sensors.prox,0f);check(f.windows.current==null)
 Settings.Secure.enabled=1;f.state.change(true);f.sensors.send(f.sensors.prox,0f)
 f.controller.onEmergencyButtonClick();check(f.windows.current==null)
 f.state.change(true);check(f.windows.current==null) // suppression interval
 android.os.SystemClock.now+=5001;f.state.change(true);check(f.windows.current!=null)
 f.wake.observer!!.onStartedGoingToSleep();check(f.windows.current==null)
 f.wake.observer!!.onStartedWakingUp();check(!f.visible())
 f.state.change(false)
 val fallback=Fixture(false);fallback.state.isShowing=true;fallback.start()
 check(fallback.sensors.active==setOf(8));fallback.sensors.send(fallback.sensors.prox,0f);check(fallback.visible())
 fallback.state.change(false)
 val failed=Fixture();failed.sensors.registrationSucceeds=false;failed.state.isShowing=true;failed.start()
 check(failed.windows.current==null)
 // Lockscreen=None can report showing during startup/wake: do not create a window.
 val none=Fixture();none.lock.disabledUsers.add(0);none.state.isShowing=true;none.start()
 none.status.listener!!.onDozingChanged(true);none.wake.observer!!.onStartedWakingUp()
 none.monitor.callback!!.onKeyguardVisibilityChanged(true)
 check(none.windows.current==null);check(none.sensors.active.isEmpty())
 // Changing to None while near must clear the active overlay, even with a stale showing bit.
 val changed=Fixture();changed.state.isShowing=true;changed.start()
 changed.sensors.send(changed.sensors.prox,0f);check(changed.visible())
 changed.lock.disabledUsers.add(0);changed.sensors.send(changed.sensors.prox,0f)
 check(changed.windows.current==null);check(changed.sensors.active.isEmpty())
 // The lockscreen policy belongs to the selected user, not always user zero.
 val user=Fixture();user.lock.disabledUsers.add(10);user.users.user=10;user.state.isShowing=true;user.start()
 check(user.windows.current==null)
 // Secure settings and lockscreen policy must use the same selected user.
 val settingUser=Fixture();settingUser.users.user=10;settingUser.state.isShowing=true
 Settings.Secure.perUser[10]=0;settingUser.start();check(settingUser.windows.current==null)
 Settings.Secure.perUser.clear()
 val brokenAdd=Fixture();brokenAdd.windows.failAdd=true;brokenAdd.state.isShowing=true;brokenAdd.start()
 check(brokenAdd.windows.current==null);check(brokenAdd.sensors.active.isEmpty())
 brokenAdd.windows.failAdd=false;brokenAdd.state.change(true);brokenAdd.sensors.send(brokenAdd.sensors.prox,0f);check(brokenAdd.visible())
 brokenAdd.windows.failRemove=true;brokenAdd.state.change(true,true)
 check(!brokenAdd.visible());check(brokenAdd.sensors.active.isEmpty())
 brokenAdd.windows.failRemove=false;brokenAdd.state.change(false);check(brokenAdd.windows.current==null)
}
''',
    }
    # Kotlin properties compile to setVisibility too; the fixture exposes the Android
    # Java method name via a different JVM name to model both source spellings.
    fixtures['View.kt'] = fixtures['View.kt'].replace('fun setVisibility(v:Int)', '@JvmName("setVisibilityExplicit") fun setVisibility(v:Int)')
    paths = []
    for name, text in fixtures.items():
        path = root / name
        path.write_text(text)
        paths.append(path)
    actual = source / 'frameworks/base/packages/SystemUI/src/org/avium/systemui/mistouch'
    paths += [actual / 'MistouchPreventionWindowController.kt', actual / 'MistouchInteractor.kt']
    env = os.environ.copy()
    env['JAVA_HOME'] = str(source / 'prebuilts/jdk/jdk21/linux-x86')
    env['PATH'] = env['JAVA_HOME'] + '/bin:' + env.get('PATH', '')
    jar = root / 'controller.jar'
    run([source / 'external/kotlinc/bin/kotlinc', *paths, '-include-runtime', '-d', jar], env=env)
    run([pathlib.Path(env['JAVA_HOME']) / 'bin/java', '-jar', jar])
    # Removing the lockscreen/occlusion guard recreates the desktop blocking path.
    controller = (actual / 'MistouchPreventionWindowController.kt').read_text()
    guarded = 'mistouchPreventionEnabled &&\n            !lockPatternUtils.isLockScreenDisabled(selectedUserInteractor.getSelectedUserId()) &&\n            keyguardShowing &&\n            !keyguardStateController.isOccluded && !biometricUnlockController.isWakeAndUnlock'
    assert guarded in controller
    mutation = root / 'MistouchPreventionWindowController.kt'
    mutation.write_text(controller.replace(guarded, 'mistouchPreventionEnabled'))
    negative_paths = [mutation if p == actual / 'MistouchPreventionWindowController.kt' else p for p in paths]
    run([source / 'external/kotlinc/bin/kotlinc', *negative_paths, '-include-runtime', '-d', jar], env=env)
    negative = subprocess.run([str(pathlib.Path(env['JAVA_HOME']) / 'bin/java'), '-jar', str(jar)], text=True, capture_output=True)
    assert negative.returncode != 0 and 'Check failed' in negative.stderr
    none_guard = '            !lockPatternUtils.isLockScreenDisabled(selectedUserInteractor.getSelectedUserId()) &&\n'
    assert controller.count(none_guard) == 1
    mutation.write_text(controller.replace(none_guard, ''))
    run([source / 'external/kotlinc/bin/kotlinc', *negative_paths, '-include-runtime', '-d', jar], env=env)
    negative = subprocess.run([str(pathlib.Path(env['JAVA_HOME']) / 'bin/java'), '-jar', str(jar)], text=True, capture_output=True)
    assert negative.returncode != 0 and 'Check failed' in negative.stderr
run(['python3',pathlib.Path(__file__).with_name('session-lifecycle-regressions.py'),source])
print(json.dumps({'passed': True, 'token_version_zero_and_endianness': True,
    'invalid_mac_lengths_rejected_under_asan_ubsan': [0, 1, 31, 33, 256],
    'full_production_mistouch_controller_host_fixtures_passed': True,
    'window_failures_and_selected_user_secure_settings_passed': True,
    'session_lifetime_concurrent_close_timers_and_enumeration_passed': True,
    'removed_fixes_negative_controls_failed_as_expected': 3,
    'real_k50_ultra_enrollment_and_pocket_hardware_tested': False}, indent=2))
