// SPDX-License-Identifier: Apache-2.0
// Host fixture; production model and methods are replaced from the supplied checkout.

typealias Drawable = Any
object PackageUtil { class AppSnippet(val icon: Drawable?=null,val label: String="test") }
open class InstallStage(val code:Int) { companion object {const val STAGE_FAILED=6} }
class Uri(val scheme:String)
class Intent {
 constructor(){}
 constructor(action:String){}
 var data:Uri?=Uri("content")
 fun setFlags(i:Int):Intent=this
 fun setPackage(s:String):Intent=this

 var returned:Int?=null
 fun getBooleanExtra(key:String,default:Boolean)=returnResult
 fun putExtra(key:String,value:Int):Intent {returned=value;return this}
 companion object {const val FLAG_RECEIVER_FOREGROUND=1;const val EXTRA_RETURN_RESULT="return";const val EXTRA_INSTALL_RESULT="result"}
}
class InstallSuccess(a:PackageUtil.AppSnippet,b:Boolean,c:Boolean,d:Intent?):InstallStage(5)
class InstallAborted(a:Int,activityResultCode:Int=0):InstallStage(0)
class InstallInstalling(a:PackageUtil.AppSnippet,b:Boolean):InstallStage(3)
object PackageInstaller {const val STATUS_SUCCESS=0;const val STATUS_FAILURE=1;const val STATUS_FAILURE_BLOCKED=2;const val STATUS_FAILURE_ABORTED=3}
object PackageManager {class NameNotFoundException:Exception();const val INSTALL_REASON_USER=4;const val INSTALL_FAILED_INTERNAL_ERROR=-110;const val INSTALL_SUCCEEDED=1;const val INSTALL_FAILED_VERIFICATION_TIMEOUT=-22;const val INSTALL_FAILED_VERIFICATION_FAILURE=-23}
const val ABORT_REASON_INTERNAL_ERROR=0
const val LOG_TAG="host"
const val localLogv=false
var returnResult=false
var observerThrows=false
var abandonThrows=false
var removed=0
var abandoned=0
var queries=0
class PersistentDataBlockManager(val active:Boolean) {
 val isFactoryResetProtectionActive:Boolean get(){queries++;if(queryThrows)throw IllegalStateException("query unavailable");return active}
}
var queryThrows=false
class Context(var manager:PersistentDataBlockManager?) {
 fun <T>getSystemService(type:Class<T>):T?=manager?.let{type.cast(it)}
 val packageName="installer"
}
object EventResultPersister {const val GENERATE_NEW_ID=-1;const val EXTRA_ID="id";class OutOfIdsException:Exception()}
typealias OutOfIdsException=EventResultPersister.OutOfIdsException
object InstallEventReceiver {fun addObserver(c:Context,id:Int,o:Any):Int=11;fun removeObserver(c:Context,id:Int){removed++;if(observerThrows)throw IllegalStateException("observer unavailable")}}
var opens=0;var commits=0;var closes=0;var openFailure=false;var commitFailure:Exception?=null;var closeFailure=false;var abandonedId=0
class Session:java.io.Closeable{fun commit(sender:Any){commits++;commitFailure?.let{throw it}};override fun close(){closes++;if(closeFailure)throw IllegalStateException("close unavailable")}}
class Installer {fun setPermissionsResult(id:Int,b:Boolean){};fun openSession(id:Int):Session{opens++;if(openFailure)throw IllegalStateException("open unavailable");return Session()};fun abandonSession(id:Int){abandoned++;abandonedId=id;if(abandonThrows)throw IllegalStateException("session unavailable")}}
object Activity {const val RESULT_OK=-1}
class PendingIntent{val intentSender=Any();companion object{const val FLAG_UPDATE_CURRENT=1;const val FLAG_MUTABLE=2;fun getBroadcast(c:Context,id:Int,i:Intent,f:Int)=PendingIntent()}}
const val SCHEME_PACKAGE="package";const val BROADCAST_ACTION="result";const val ABORT_REASON_DONE=9
object Log {fun e(tag:String,msg:String,e:Exception?=null){};fun w(tag:String,msg:String,e:Exception){};fun i(tag:String,msg:String){}}
class Value {var value:InstallStage?=null}
class Pm {fun installExistingPackage(p:String,r:Int){};fun getLaunchIntentForPackage(s:String):Intent?=null}
data class InstallFailed(
    val appSnippet: PackageUtil.AppSnippet? = null,
    val legacyCode: Int,
    val statusCode: Int,
    val message: String? = null,
    val shouldReturnResult: Boolean = false,
    /**
     * If the caller is requesting a result back, this will hold an Intent with
     * [Intent.EXTRA_INSTALL_RESULT] set to the [PackageInstaller.EXTRA_LEGACY_STATUS].
     */
    val resultIntent: Intent? = null,
    // Set only by this installer after a framework FRP state query, never by an incoming Intent.
    val factoryResetProtectionBlocked: Boolean = false
) : InstallStage(STAGE_FAILED) {

    val appIcon: Drawable?
        get() = appSnippet?.icon

    val appLabel: String?
        get() = appSnippet?.label as String?
}
class Fixture(val context:Context) {
 val packageInstaller=Installer()
 val packageManager=Pm()
 var stagedSessionId=7
 var sessionId=0
 var wasUserConfirmationTriggeredByPia=false
 val intent=Intent()
 val _installResult=Value()
 val appSnippet=PackageUtil.AppSnippet()
 val isAppUpdating=false
 class Info {val packageName="app"}
 val newPackageInfo:Info?=Info()
 fun deleteSourcePackageIfNeeded(){throw AssertionError("failure must not delete APK")}
 fun isLauncherActivityEnabled(i:Intent?)=false
     private fun isFactoryResetProtectionActive(): Boolean {
        return try {
            context.getSystemService(PersistentDataBlockManager::class.java)
                ?.isFactoryResetProtectionActive ?: false
        } catch (e: RuntimeException) {
            // A failed diagnostic query must not replace the original installation error.
            Log.w(LOG_TAG, "Could not query factory reset protection state", e)
            false
        }
    }
    private fun handleSessionFailure(installId: Int, failure: Exception) {
        Log.e(LOG_TAG, "Session $stagedSessionId could not be committed", failure)
        // Classify only a real security rejection while the framework confirms protection is active.
        // Never infer it from exception text, a GMS setting or setup-completion flags.
        val frpBlocked = failure is SecurityException && isFactoryResetProtectionActive()
        try {
            InstallEventReceiver.removeObserver(context, installId)
        } catch (cleanupFailure: RuntimeException) {
            Log.w(LOG_TAG, "Could not remove failed installation observer", cleanupFailure)
        }
        val failedSessionId = stagedSessionId
        stagedSessionId = 0
        try {
            packageInstaller.abandonSession(failedSessionId)
        } catch (cleanupFailure: RuntimeException) {
            Log.w(LOG_TAG, "Could not abandon failed installation session", cleanupFailure)
        }
        setStageBasedOnResult(
            if (frpBlocked) PackageInstaller.STATUS_FAILURE_BLOCKED else PackageInstaller.STATUS_FAILURE,
            // Preserve the legacy result of a synchronous commit exception. The system SDK does
            // not expose a dedicated FRP legacy code; the public status and typed UI reason do.
            PackageManager.INSTALL_FAILED_INTERNAL_ERROR,
            null,
            frpBlocked
        )
    }
    private fun setStageBasedOnResult(
        statusCode: Int,
        legacyStatus: Int,
        message: String?,
        frpBlocked: Boolean = false,
    ) {
        if (localLogv) {
            Log.i(
                LOG_TAG, "Status code: $statusCode\n" +
                    "legacy status: $legacyStatus\n" +
                    "message: $message"
            )
        }

        val shouldReturnResult = intent.getBooleanExtra(Intent.EXTRA_RETURN_RESULT, false)

        if (statusCode == PackageInstaller.STATUS_SUCCESS) {
            deleteSourcePackageIfNeeded()
            val resultIntent = if (shouldReturnResult) {
                Intent().putExtra(Intent.EXTRA_INSTALL_RESULT, PackageManager.INSTALL_SUCCEEDED)
            } else {
                val intent = packageManager.getLaunchIntentForPackage(newPackageInfo!!.packageName)
                if (isLauncherActivityEnabled(intent)) intent else null
            }
            _installResult.value = InstallSuccess(
                appSnippet,
                shouldReturnResult,
                isAppUpdating,
                resultIntent
            )
        } else {
            // TODO (b/346655018): Use INSTALL_FAILED_ABORTED legacyCode in the condition
            // statusCode can be STATUS_FAILURE_ABORTED if:
            // 1. GPP blocks an install.
            // 2. User denies ownership update explicitly.
            // InstallFailed dialog must not be shown only when the user denies ownership update. We
            // must show this dialog for all other install failures.

            val userDenied = statusCode == PackageInstaller.STATUS_FAILURE_ABORTED &&
                            legacyStatus != PackageManager.INSTALL_FAILED_VERIFICATION_TIMEOUT &&
                            legacyStatus != PackageManager.INSTALL_FAILED_VERIFICATION_FAILURE

            if (shouldReturnResult) {
                val resultIntent = Intent().putExtra(Intent.EXTRA_INSTALL_RESULT, legacyStatus)
                _installResult.value = InstallFailed(
                    legacyCode = legacyStatus,
                    statusCode = statusCode,
                    shouldReturnResult = true,
                    resultIntent = resultIntent,
                    factoryResetProtectionBlocked = frpBlocked
                )
            } else if (userDenied) {
                _installResult.value = InstallAborted(ABORT_REASON_INTERNAL_ERROR)
            } else {
                _installResult.value = InstallFailed(
                    appSnippet, legacyStatus, statusCode, message,
                    factoryResetProtectionBlocked = frpBlocked
                )
            }
        }
    }
 fun reject(e:Exception){handleSessionFailure(11,e)}
 fun asyncBlocked(){setStageBasedOnResult(PackageInstaller.STATUS_FAILURE_BLOCKED,-111,"admin")}
     fun initiateInstall() {
        if (sessionId > 0) {
            packageInstaller.setPermissionsResult(sessionId, true)
            if (localLogv) {
                Log.i(LOG_TAG, "Install permission granted for session $sessionId")
            }
            // If it is triggered by PIA itself, show the installing dialog and wait for the
            // result from the receiver. Don't need to set the aborted.
            if (wasUserConfirmationTriggeredByPia) {
                wasUserConfirmationTriggeredByPia = false
                _installResult.value = InstallInstalling(appSnippet, isAppUpdating)
            } else {
                _installResult.value = InstallAborted(
                    ABORT_REASON_DONE, activityResultCode = Activity.RESULT_OK
                )
            }
            return
        }
        val uri = intent.data
        if (SCHEME_PACKAGE == uri?.scheme) {
            try {
                packageManager.installExistingPackage(
                    newPackageInfo!!.packageName, PackageManager.INSTALL_REASON_USER
                )
                setStageBasedOnResult(PackageInstaller.STATUS_SUCCESS, -1, null)
            } catch (e: PackageManager.NameNotFoundException) {
                setStageBasedOnResult(
                    PackageInstaller.STATUS_FAILURE,
                    PackageManager.INSTALL_FAILED_INTERNAL_ERROR,
                    null
                )
            }
            return
        }
        if (stagedSessionId <= 0) {
            // How did we even land here?
            Log.e(LOG_TAG, "Invalid local session and caller initiated session")
            _installResult.value = InstallAborted(ABORT_REASON_INTERNAL_ERROR)
            return
        }
        val installId: Int
        try {
            _installResult.value = InstallInstalling(appSnippet, isAppUpdating)
            installId = InstallEventReceiver.addObserver(
                context,
                EventResultPersister.GENERATE_NEW_ID,
                this
            )
        } catch (e: OutOfIdsException) {
            setStageBasedOnResult(
                PackageInstaller.STATUS_FAILURE, PackageManager.INSTALL_FAILED_INTERNAL_ERROR, null
            )
            return
        }
        val broadcastIntent = Intent(BROADCAST_ACTION)
        broadcastIntent.setFlags(Intent.FLAG_RECEIVER_FOREGROUND)
        broadcastIntent.setPackage(context.packageName)
        broadcastIntent.putExtra(EventResultPersister.EXTRA_ID, installId)
        val pendingIntent = PendingIntent.getBroadcast(
            context, installId, broadcastIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_MUTABLE
        )
        var commitReturned = false
        try {
            packageInstaller.openSession(stagedSessionId).use { session ->
                session.commit(pendingIntent.intentSender)
                commitReturned = true
            }
        } catch (e: Exception) {
            if (commitReturned) {
                // A close failure cannot turn an accepted asynchronous commit into a failure.
                Log.w(LOG_TAG, "Could not close committed installation session", e)
            } else {
                handleSessionFailure(installId, e)
            }
        }
    }
    fun cleanupInstall() {
        if (sessionId > 0) {
            packageInstaller.setPermissionsResult(sessionId, false)
        } else if (stagedSessionId > 0) {
            cleanupStagingSession()
        }
    }
    private fun cleanupStagingSession() {
        if (stagedSessionId > 0) {
            try {
                packageInstaller.abandonSession(stagedSessionId)
            } catch (ignored: SecurityException) {
            }
            stagedSessionId = 0
        }
    }
}
var checks=0
var cases=0
fun checkThat(ok:Boolean){checks++;if(!ok)throw AssertionError("case=$cases assertion=$checks")}
fun fresh(active:Boolean?):Fixture {
 cases++;queries=0;removed=0;abandoned=0;returnResult=false;observerThrows=false;abandonThrows=false;queryThrows=false
 return Fixture(Context(active?.let{PersistentDataBlockManager(it)}))
}
fun result(f:Fixture,blocked:Boolean){
 val r=f._installResult.value as InstallFailed
 checkThat(r.statusCode==if(blocked)2 else 1)
 checkThat(r.legacyCode==-110) // Preserve legacy result for synchronous commit exceptions.
 checkThat(r.factoryResetProtectionBlocked==blocked)
 checkThat(removed==1&&abandoned==1)
}
fun main(){
 var f=fresh(true);f.reject(SecurityException("unrelated text"));result(f,true);checkThat(queries==1)
 f=fresh(false);f.reject(SecurityException("FRP is active"));result(f,false);checkThat(queries==1)
 f=fresh(true);f.reject(IllegalStateException("FRP is active"));result(f,false);checkThat(queries==0)
 f=fresh(null);f.reject(SecurityException("rejected"));result(f,false);checkThat(queries==0)
 f=fresh(true);queryThrows=true;f.reject(SecurityException("rejected"));result(f,false);checkThat(queries==1)
 f=fresh(true);observerThrows=true;f.reject(SecurityException("rejected"));result(f,true)
 f=fresh(true);abandonThrows=true;f.reject(SecurityException("rejected"));result(f,true)
 f=fresh(true);observerThrows=true;abandonThrows=true;f.reject(SecurityException("rejected"));result(f,true)
 f=fresh(true);returnResult=true;f.reject(SecurityException("rejected"));result(f,true)
 var r=f._installResult.value as InstallFailed;checkThat(r.shouldReturnResult);checkThat(r.resultIntent?.returned==-110)
 f=fresh(false);returnResult=true;f.reject(SecurityException("rejected"));result(f,false)
 r=f._installResult.value as InstallFailed;checkThat(r.shouldReturnResult);checkThat(r.resultIntent?.returned==-110)
 cases++;r=InstallFailed(legacyCode=-111,statusCode=2,message="FRP is active")
 checkThat(!r.factoryResetProtectionBlocked)

 fun freshSession():Fixture{opens=0;commits=0;closes=0;openFailure=false;commitFailure=null;closeFailure=false;abandonedId=0;return fresh(true)}
 f=freshSession();f.initiateInstall();checkThat(commits==1&&closes==1);checkThat(abandoned==0&&removed==0);checkThat(f._installResult.value is InstallInstalling)
 f=freshSession();commitFailure=SecurityException("reject");f.initiateInstall();result(f,true);checkThat(closes==1&&abandonedId==7&&f.stagedSessionId==0);val beforeCleanup=abandoned;f.cleanupInstall();checkThat(abandoned==beforeCleanup)
 f=freshSession();closeFailure=true;f.initiateInstall();checkThat(commits==1&&closes==1&&abandoned==0&&removed==0);checkThat(f._installResult.value is InstallInstalling)
 f=freshSession();commitFailure=SecurityException("reject");closeFailure=true;f.initiateInstall();result(f,true);checkThat(closes==1&&f.stagedSessionId==0)
 f=freshSession();openFailure=true;f.initiateInstall();result(f,false);checkThat(closes==0&&f.stagedSessionId==0)
 f=freshSession();commitFailure=IllegalStateException("reject");abandonThrows=true;f.initiateInstall();result(f,false);checkThat(f.stagedSessionId==0);f.cleanupInstall();checkThat(abandoned==1)
 f=freshSession();f.asyncBlocked();r=f._installResult.value as InstallFailed;checkThat(r.statusCode==2&&!r.factoryResetProtectionBlocked);checkThat(queries==0) // BLOCKED plus active FRP is not causal proof.

 println("{\"cases\":$cases,\"assertions\":$checks,\"passed\":true}")
}
