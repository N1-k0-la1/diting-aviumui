# SPDX-License-Identifier: Apache-2.0
"""Execute actual installation failure UI with public/legacy status pairs."""
from pathlib import Path
import argparse, datetime, hashlib, json, subprocess, tempfile

p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args()
root=a.source.resolve(strict=True);here=a.output_dir.resolve();here.mkdir(parents=True,exist_ok=False)
path=root/'frameworks/base/packages/PackageInstaller/src/com/android/packageinstaller/v2/ui/fragments/InstallationFragment.java'
source=path.read_text();start=source.index('private void updateInstallFailedUI(');opening=source.index('{',start);end=opening+1;depth=1
while depth:
    depth+=(source[end]=='{')-(source[end]=='}');end+=1
method=source[start:end]
code=r'''
class View {
 static final int VISIBLE=0,GONE=8;int visibility=VISIBLE;boolean clickable=true;
 interface OnClickListener{void onClick(View v);}OnClickListener click;
 void setVisibility(int v){visibility=v;}void setClickable(boolean b){clickable=b;}
 void setOnClickListener(OnClickListener l){click=l;}
 void post(Runnable r){r.run();}boolean performAccessibilityAction(int a,Object b){return true;}
 void setFilterTouchesWhenObscured(boolean b){}
}
class TextView extends View {Object text;void setText(Object t){text=t;}}
class Button extends TextView {}
class ImageView extends View {void setImageDrawable(Object x){}}
class Dialog {int title;Button positive=new Button(),negative=new Button();void setTitle(int t){title=t;}}
class Log {static void i(String t,String m){}}
class AccessibilityNodeInfo {static final int ACTION_ACCESSIBILITY_FOCUS=1;}
class UiUtil {
 static Button getAlertDialogPositiveButton(Dialog d){return d.positive;}
 static Button getAlertDialogNegativeButton(Dialog d){return d.negative;}
 static void applyFilledButtonStyle(Object c,Button b){}static void applyOutlinedButtonStyle(Object c,Button b){}
}
class PackageInstaller {static final int STATUS_FAILURE=1,STATUS_FAILURE_BLOCKED=2,STATUS_FAILURE_CONFLICT=5,STATUS_FAILURE_INCOMPATIBLE=7,STATUS_FAILURE_INVALID=4,STATUS_FAILURE_STORAGE=6;}
class R {static class string {
 static final int title_install_failed_not_installed=1,message_install_failed_blocked=2,title_install_failed_blocked=3,message_install_failed_conflict=4,title_cant_install_app=5,message_install_failed_incompatible=6,title_install_failed_incompatible=7,message_install_failed_invalid=8,message_install_failed_less_storage=9,title_install_failed_less_storage=10,button_manage_apps=11,button_close=12,message_install_failed_protection_active=13;
}}
class InstallFailed {boolean frp;boolean getDeviceProtectionActive(){return frp;}int legacy,status;InstallFailed(int l,int s){legacy=l;status=s;}
 int getLegacyCode(){return legacy;}int getStatusCode(){return status;}int getStageCode(){return 4;}
 Object getAppIcon(){return null;}String getAppLabel(){return "test apk";}
}
class Actions {int manage,close;void sendManageAppsIntent(){manage++;}void onNegativeResponse(int s){close++;}}
public class InstallerFailureTest {
 static final String LOG_TAG="test";View mIndeterminateProgressBar=new View(),mProgressBar=new View(),mAppSnippet=new View();
 TextView mCustomMessageTextView=new TextView(),mAppLabelTextView=new TextView();ImageView mAppIcon=new ImageView();Actions mInstallActionListener=new Actions();
 String getString(int x){return "string-"+x;}Object requireContext(){return null;}
 METHOD
 static int assertions;static void check(boolean b,String m){assertions++;if(!b)throw new AssertionError(m);}
 public static void main(String[] args){
  int legacy=Integer.parseInt(args[0]),status=Integer.parseInt(args[1]),message=Integer.parseInt(args[2]),title=Integer.parseInt(args[3]);
  InstallerFailureTest f=new InstallerFailureTest();Dialog d=new Dialog();InstallFailed stage=new InstallFailed(legacy,status);stage.frp=args.length>4&&Boolean.parseBoolean(args[4]);f.updateInstallFailedUI(d,stage);
  check(d.title==title,"failure title follows public status, not legacy code");
  if(message==0)check(f.mCustomMessageTextView.visibility==View.GONE,"unknown failure does not display misleading reason");
  else check(f.mCustomMessageTextView.visibility==View.VISIBLE&&Integer.valueOf(message).equals(f.mCustomMessageTextView.text),"specific failure reason visible");
  check(f.mProgressBar.visibility==View.GONE&&f.mIndeterminateProgressBar.visibility==View.GONE,"failure ends progress");
  if(status==6){check(d.positive.visibility==View.VISIBLE&&d.positive.click!=null,"storage error offers storage management");d.positive.click.onClick(d.positive);check(f.mInstallActionListener.manage==1&&!d.positive.clickable,"storage action dispatched once and disabled");}
  else check(d.positive.visibility==View.GONE,"other errors do not offer storage management");
  d.negative.click.onClick(d.negative);check(f.mInstallActionListener.close==1,"close action retained");
  System.out.println(assertions);
 }
}
'''.replace('METHOD',method)
# Exact platform public constants and representative INSTALL_FAILED_* legacy values.
rows=[]
cases=[('blocked',-111,2,2,3),('conflict',-7,5,4,5),('incompatible',-12,7,6,7),('invalid',-2,4,8,5),('storage',-4,6,9,10),('internal',-110,1,0,1),('unknown',-999,123,0,1),('frp-blocked',-111,2,13,3,'true'),('frp-flag-does-not-relabel-storage',-4,6,9,10,'true')]
with tempfile.TemporaryDirectory(prefix='installer-failure-') as tmp:
    work=Path(tmp);(work/'InstallerFailureTest.java').write_text(code)
    jdk=root/'prebuilts/jdk/jdk21/linux-x86/bin'
    subprocess.run([str(jdk/'javac'),str(work/'InstallerFailureTest.java')],check=True,capture_output=True)
    for name,*values in cases:
        r=subprocess.run([str(jdk/'java'),'-cp',tmp,'InstallerFailureTest',*[str(v) for v in values]],capture_output=True,text=True)
        rows.append({'case':name,'passed':r.returncode==0,'stdout':r.stdout,'stderr':r.stderr})
report={'at':datetime.datetime.now().astimezone().isoformat(),'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'results':rows,'scope':'Actual updateInstallFailedUI, host view/dialog fakes. Does not perform installation or deactivate protection.'}
(here/'regressions.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':sum(x['passed'] for x in rows),'cases':len(rows),'failed':[x['case'] for x in rows if not x['passed']]}))
assert all(x['passed'] for x in rows)
