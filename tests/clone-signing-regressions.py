# SPDX-License-Identifier: Apache-2.0
"""Execute production clone signing fallback and real activity-result visibility grant."""
import argparse,json,pathlib,re,subprocess,tempfile
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source',type=pathlib.Path)
root=parser.parse_args().source.resolve(strict=True)
base=root/'frameworks/base/services/core/java/com/android/server'
computer=(base/'pm/ComputerEngine.java').read_text()
starter=(base/'wm/ActivityStarter.java').read_text()
def method(text,name):
 match=re.search(r'^.*\b'+name+r'\([^;{]*\)\s*\{',text,re.M);assert match,name
 pos=match.end();depth=1
 while depth:depth+=(text[pos]=='{')-(text[pos]=='}');pos+=1
 return text[match.start():pos]
start=starter.index('        if (mStartActivity.resultTo != null && mStartActivity.resultTo.info != null) {')
end=starter.index('        } else if (mStartActivity.mShareIdentity)',start)
grant=starter[start:end]+'        }'
code='''
import java.util.*;
public class CloneSigning {
 static final String MUSIC="official.music";static final int CLONE_UID=1010270;
 static class PackageManager {@interface PackageInfoFlagsBits {} static final long GET_SIGNATURES=64,GET_SIGNING_CERTIFICATES=0x08000000;static final int COMPONENT_ENABLED_STATE_DEFAULT=0,COMPONENT_ENABLED_STATE_ENABLED=1;static final long VERSION_CODE_HIGHEST=-1;}
 static class Process {static final int FIRST_APPLICATION_UID=10000;static boolean isolated,sandbox;static boolean isIsolated(int uid){return isolated;}static boolean isSdkSandboxUid(int uid){return sandbox;}}
 static class UserHandle {static int getUserId(int uid){return uid/100000;}static int getAppId(int uid){return uid%100000;}static int getUid(int user,int app){return user*100000+app;}}
 static class Binder {static int uid=CLONE_UID;static int getCallingUid(){return uid;}}
 static class UserInfo {boolean clone,enabled=true,quiet,profile;boolean isCloneProfile(){return clone;}boolean isEnabled(){return enabled;}boolean isQuietModeEnabled(){return quiet;}boolean isProfile(){return profile;}}
 static class UserManagerInternal {Map<Integer,UserInfo> users=new HashMap<>();Set<Integer> locked=new HashSet<>();int parent;
 UserInfo getUserInfo(int id){return users.get(id);}int getProfileParentId(int id){return parent;}boolean isUserUnlocked(int id){return !locked.contains(id);}}
 static class Injector {UserManagerInternal users=new UserManagerInternal();UserManagerInternal getUserManagerInternal(){return users;}}
 static class GmsManagerService {static Set<Integer> hidden=new HashSet<>();static boolean shouldHide(int user,String pkg){return hidden.contains(user);}}
 static class PackageUserStateInternal {boolean installed,hidden,suspended,instant,archived;int enabled;
 boolean isInstalled(){return installed;}boolean isHidden(){return hidden;}boolean isSuspended(){return suspended;}boolean isInstantApp(){return instant;}int getEnabledState(){return enabled;}}
 static class PackageArchiver {static boolean isArchived(PackageUserStateInternal state){return state.archived;}}
 static class PackageStateInternal {Map<Integer,PackageUserStateInternal> states=new HashMap<>();Object pkg=new Object();int appId=10272;
 Object getPkg(){return pkg;}int getAppId(){return appId;}PackageUserStateInternal getUserStateOrDefault(int user){return states.computeIfAbsent(user,k->new PackageUserStateInternal());}}
 static class Settings {PackageStateInternal ps=new PackageStateInternal();PackageStateInternal getPackage(String pkg){return MUSIC.equals(pkg)?ps:null;}}
 static class Filter {Set<String> grants=new HashSet<>();boolean isImplicitlyQueryable(int caller,int visible){return grants.contains(caller+":"+visible);}void grant(int caller,int visible){grants.add(caller+":"+visible);}}
 static class PackageInfo {final int uid;final String signer;PackageInfo(int uid,String signer){this.uid=uid;this.signer=signer;}}
 final Injector mInjector=new Injector();final Settings mSettings=new Settings();final Filter mAppsFilter=new Filter();
 boolean instantCaller,filtered;PackageInfo local;int internalUser=-1,bodyCalls;long bodyFlags;
 String getInstantAppPackageName(int uid){return instantCaller?"instant":null;}
 PackageInfo getPackageInfoInternal(String pkg,long version,long flags,int caller,int user){
  if(user!=UserHandle.getUserId(caller))throw new SecurityException("explicit cross-user query");return local;}
 PackageInfo getPackageInfoInternalBody(String pkg,long version,long flags,int caller,int user){internalUser=user;bodyCalls++;bodyFlags=flags;return filtered?null:new PackageInfo(UserHandle.getUid(user,mSettings.ps.appId),"REAL-SIGNER");}
''' + method(computer,'getPackageInfo')+'\n'+method(computer,'getCloneCallerSigningInfo')+'''
 static class Activity {int mUserId;Activity resultTo;Info info=new Info();Activity(int user){mUserId=user;}}
 static class Info {String packageName=MUSIC;AppInfo applicationInfo=new AppInfo();}static class AppInfo {int uid=CLONE_UID;}
 class PackageManagerInternal {int lookupUser=-1,visible=-1,recipient=-1;boolean direct;
  int getPackageUid(String pkg,int flags,int user){lookupUser=user;return MUSIC.equals(pkg)&&user==mInjector.users.parent?UserHandle.getUid(user,10272):-1;}
  void grantImplicitAccess(int user,Object intent,int app,int visibleUid,boolean direct){visible=visibleUid;recipient=UserHandle.getUid(user,app);this.direct=direct;if(visibleUid>=0)mAppsFilter.grant(recipient,visibleUid);}}
 class Service {PackageManagerInternal pm=new PackageManagerInternal();PackageManagerInternal getPackageManagerInternalLocked(){return pm;}}
 Service mService=new Service();Activity mStartActivity=new Activity(10);Object mIntent=new Object();
 void start(){
''' +grant+'''
 }
 CloneSigning(){UserInfo parent=new UserInfo(),clone=new UserInfo();clone.clone=true;clone.profile=true;mInjector.users.users.put(0,parent);mInjector.users.users.put(10,clone);mSettings.ps.getUserStateOrDefault(0).installed=true;mStartActivity.resultTo=new Activity(0);}
 static int cases;
 static void check(boolean value,String name){cases++;if(!value)throw new AssertionError(name);}
 static CloneSigning ready(){Process.isolated=Process.sandbox=false;GmsManagerService.hidden.clear();Binder.uid=CLONE_UID;CloneSigning c=new CloneSigning();c.start();return c;}
 static void deny(CloneSigning c,String name){check(c.getPackageInfo(MUSIC,64,10)==null,name);check(c.bodyCalls==0,name+" never generate parent metadata");}
 public static void main(String[] args){
  CloneSigning c=ready();check(c.mService.pm.lookupUser==0,"resolve result owner in actual source user");check(c.mService.pm.visible==10272&&c.mService.pm.recipient==CLONE_UID&&c.mService.pm.direct,"grant exact UID pair");
  PackageInfo info=c.getPackageInfo(MUSIC,64,10);check(info!=null&&info.uid==10272&&info.signer.equals("REAL-SIGNER"),"authentic parent signature and UID");check(c.internalUser==0&&c.bodyFlags==64,"only original signing flags");
  c=ready();check(c.getPackageInfo(MUSIC,0x08000000,10)!=null,"modern signing flag");check(c.getPackageInfo(MUSIC,64|0x08000000,10)!=null,"both signing flags");
  c=ready();c.mAppsFilter.grants.clear();deny(c,"no direct interaction");
  c=ready();c.mAppsFilter.grants.clear();c.mAppsFilter.grant(10270,10272);deny(c,"owner UID cannot authorize clone");
  c=ready();c.mAppsFilter.grants.clear();c.mAppsFilter.grant(CLONE_UID,1010272);deny(c,"clone-local UID is not real parent caller");
  c=ready();c.mSettings.ps=null;deny(c,"package removed");
  c=ready();c.mSettings.ps.pkg=null;deny(c,"package code removed");
  c=ready();c.mSettings.ps.getUserStateOrDefault(10).installed=true;deny(c,"never override local install");
  c=ready();c.mSettings.ps.getUserStateOrDefault(0).installed=false;deny(c,"parent uninstalled");
  c=ready();c.mSettings.ps.getUserStateOrDefault(0).hidden=true;deny(c,"parent hidden");
  c=ready();c.mSettings.ps.getUserStateOrDefault(0).suspended=true;deny(c,"parent suspended");
  c=ready();c.mSettings.ps.getUserStateOrDefault(0).instant=true;deny(c,"parent instant");
  c=ready();c.mSettings.ps.getUserStateOrDefault(0).archived=true;deny(c,"parent archived");
  for(int disabled:new int[]{2,3,4}){c=ready();c.mSettings.ps.getUserStateOrDefault(0).enabled=disabled;deny(c,"parent disabled");}
  c=ready();c.mInjector.users.users.get(10).clone=false;deny(c,"managed/private/full users denied");
  c=ready();c.mInjector.users.users.get(10).enabled=false;deny(c,"clone disabled");
  c=ready();c.mInjector.users.users.get(10).quiet=true;deny(c,"clone quiet");
  c=ready();c.mInjector.users.locked.add(10);deny(c,"clone locked");
  c=ready();c.mInjector.users.locked.add(0);deny(c,"parent locked");
  c=ready();c.mInjector.users.users.remove(10);deny(c,"clone removed");
  c=ready();c.mInjector.users.users.remove(0);deny(c,"parent removed");
  c=ready();c.mInjector.users.users.get(0).enabled=false;deny(c,"parent disabled");
  c=ready();c.mInjector.users.users.get(0).profile=true;deny(c,"parent not a full user");
  c=ready();c.mInjector.users.parent=10;deny(c,"self parent");
  c=ready();GmsManagerService.hidden.add(0);deny(c,"parent GMS policy");
  c=ready();GmsManagerService.hidden.add(10);deny(c,"clone GMS policy");
  c=ready();c.instantCaller=true;deny(c,"instant caller");
  c=ready();Process.isolated=true;deny(c,"isolated caller");
  c=ready();Process.sandbox=true;deny(c,"sandbox caller");
  c=ready();Binder.uid=1001000;deny(c,"system appId");
  c=ready();c.filtered=true;check(c.getPackageInfo(MUSIC,64,10)==null,"normal package visibility still applies");
  for(long flags:new long[]{0,1,64|1,64|0x2000,64|0x200,64|0x800000000L}){c=ready();check(c.getPackageInfo(MUSIC,flags,10)==null&&c.bodyCalls==0,"no components/uninstalled/data queries");}
  c=ready();check(c.getPackageInfo("other.package",64,10)==null,"unrelated package denied");
  c=ready();c.local=new PackageInfo(1010272,"LOCAL-SIGNER");check(c.getPackageInfo(MUSIC,64,10)==c.local&&c.bodyCalls==0,"normal own-user result unchanged");
  c=ready();try{c.getPackageInfo(MUSIC,64,0);throw new AssertionError("cross user accepted");}catch(SecurityException expected){cases++;}
  // A non-primary parent must work without hardcoded owner=0.
  c=ready();c.mInjector.users.parent=11;c.mInjector.users.users.put(11,new UserInfo());c.mSettings.ps.getUserStateOrDefault(11).installed=true;c.mStartActivity.resultTo.mUserId=11;c.start();info=c.getPackageInfo(MUSIC,64,10);check(info!=null&&info.uid==1110272,"actual nonzero parent UID");
  System.out.println(cases);
 }
}
'''
java=root/'prebuilts/jdk/jdk21/linux-x86/bin'
with tempfile.TemporaryDirectory(prefix='clone-signing-') as tmp:
 d=pathlib.Path(tmp)
 def execute(code,expected):
  (d/'CloneSigning.java').write_text(code)
  r=subprocess.run([str(java/'javac'),str(d/'CloneSigning.java')],capture_output=True,text=True);assert r.returncode==0,r.stderr
  r=subprocess.run([str(java/'java'),'-cp',str(d),'CloneSigning'],capture_output=True,text=True)
  assert (r.returncode==0)==expected,r.stderr
  return r.stdout.strip()
 cases=int(execute(code,True))
 replacements=[
  ('mStartActivity.resultTo.mUserId);','mStartActivity.mUserId);'),
  ('!mAppsFilter.isImplicitlyQueryable(callingUid,','false && !mAppsFilter.isImplicitlyQueryable(callingUid,'),
  ('!clone.isCloneProfile()','false'),
  ('(flags & ~signingFlags) != 0','false'),
  ('(flags & signingFlags) == 0','false'),
  ('!users.isUserUnlocked(parentId)','false'),
  ('clone.isQuietModeEnabled()','false'),
  ('ps.getUserStateOrDefault(userId).isInstalled()','false'),
  ('state.isHidden()','false'),
  ('state.isSuspended()','false'),
  ('return getPackageInfoInternalBody(packageName, PackageManager.VERSION_CODE_HIGHEST,','return new PackageInfo(0,"FAKE"); /*getPackageInfoInternalBody(packageName, PackageManager.VERSION_CODE_HIGHEST,'),
 ]
 # Last mutant skips the normal visibility filter; close its intentionally removed invocation.
 for i,(old,new) in enumerate(replacements):
  assert old in code,old
  mutant=code.replace(old,new)
  if i==len(replacements)-1:mutant=mutant.replace('flags, callingUid, parentId);','flags, callingUid, parentId); */')
  execute(mutant,False)
print(json.dumps(dict(passed=True,extracted_production_methods=True,assertions=cases,negative_controls_rejected=len(replacements),real_signers_and_uid_preserved=True,no_package_enumeration_or_data_grant=True,new_framework_phone_acceptance_pending=True)))
