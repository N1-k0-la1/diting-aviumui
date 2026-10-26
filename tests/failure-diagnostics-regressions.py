# SPDX-License-Identifier: Apache-2.0
"""Exercise actual staged methods with fault injection; retain earlier installer assertions."""
from pathlib import Path
import argparse, hashlib, json, os, subprocess, tempfile
import xml.etree.ElementTree as ET

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('source',type=Path,help='Patched Android source checkout')
parser.add_argument('--output',type=Path,help='Optional JSON result path')
args=parser.parse_args()
R=args.source.resolve(strict=True);PACKAGE=Path(__file__).resolve().parents[1]
workspace=tempfile.TemporaryDirectory(prefix='failure-diagnostics-tests-')
E=Path(workspace.name);T=E/'tests';T.mkdir()
jdk=R/'prebuilts/jdk/jdk21/linux-x86/bin'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def method(text,signature):
    a=text.index(signature);b=text.index('{',a)+1;depth=1
    while depth:depth+=(text[b]=='{')-(text[b]=='}');b+=1
    return text[a:b]
def execute(code,kind,expect=True):
    with tempfile.TemporaryDirectory(prefix='diagnostics-host-') as tmp:
        w=Path(tmp);env=dict(os.environ,JAVA_HOME=str(jdk.parent))
        if kind=='kotlin':
            (w/'Test.kt').write_text(code)
            command=[str(R/'external/kotlinc/bin/kotlinc'),str(w/'Test.kt'),'-include-runtime','-d',str(w/'test.jar')]
            run=[str(jdk/'java'),'-jar',str(w/'test.jar')]
        else:
            (w/'Test.cpp').write_text(code)
            command=['g++','-std=c++17','-Wall','-Wextra','-Werror',str(w/'Test.cpp'),'-o',str(w/'test')]
            run=[str(w/'test')]
        build=subprocess.run(command,env=env,capture_output=True,text=True)
        assert build.returncode==0,build.stdout+build.stderr
        result=subprocess.run(run,env=env,capture_output=True,text=True)
        assert (result.returncode==0)==expect,result.stdout+result.stderr
        if not expect:assert 'AssertionError' in result.stderr or 'Assertion' in result.stderr,result.stderr
        return json.loads(result.stdout) if expect else {'rejected':True}

rel='frameworks/base/packages/PackageInstaller/src/com/android/packageinstaller/v2/model/'
repo=(R/rel/'InstallRepository.kt').read_text()
model=(R/rel/'InstallStages.kt').read_text()
code=(PACKAGE/'tests/fixtures/failure-diagnostics/Installer.kt').read_text()
for sig in ['    private fun isFactoryResetProtectionActive()', '    private fun handleSessionFailure(',
            '    private fun setStageBasedOnResult(', '    fun initiateInstall()', '    fun cleanupInstall()',
            '    private fun cleanupStagingSession()']:
    code=code.replace(method(code,sig),method(repo,sig),1)
code=code.replace(method(code,'data class InstallFailed('),method(model,'data class InstallFailed('),1)
code=code.replace('factoryResetProtectionBlocked','deviceProtectionActive')
needle=' println("{\\"cases\\":$cases,\\"assertions\\":$checks,\\"passed\\":true}")'
assert code.count(needle)==1
extra='''
 // Active protection is context for any security rejection, never proof of its cause.
 for (reason in listOf("Can't install packages while in secure FRP", "Session does not belong to caller", "commit not allowed after destruction", "")) {
  f=freshSession();commitFailure=SecurityException(reason);f.initiateInstall();result(f,true)
  checkThat(f.stagedSessionId==0 && abandonedId==7 && closes==1)
 }
 f=freshSession();queryThrows=true;commitFailure=SecurityException("owner mismatch");f.initiateInstall();result(f,false)
 checkThat(f.stagedSessionId==0 && closes==1)
'''
code=code.replace(needle,extra+'\n'+needle)
(T/'Installer.kt').write_text(code)
installer=execute(code,'kotlin')
mutant=code.replace('failure is SecurityException && isFactoryResetProtectionActive()','isFactoryResetProtectionActive()')
assert mutant!=code
negative={'non-security-failure-mislabelled':execute(mutant,'kotlin',False)}

native=method((R/'system/vold/FsCrypt.cpp').read_text(),'static bool prepare_subdirs(')
header=(R/'system/vold/PrepareSubdirsError.h').read_text().replace('#pragma once','')
cpp=r'''
#include <cassert>
#include <cerrno>
#include <climits>
#include <iostream>
#include <string>
#include <vector>
using userid_t=unsigned int;
struct Logger {template<class T>Logger& operator<<(const T&){return *this;}};
#define LOG(x) Logger()
static const std::string prepare_subdirs_path="/system/bin/vold_prepare_subdirs";
static int nextStatus, calls;
static std::vector<std::string> received;
namespace android::vold {int ForkExecvp(const std::vector<std::string>& args){++calls;received=args;return nextStatus;}}
HEADER
METHOD
int main(){
 int cases=0,checks=0;
 auto check=[&](bool ok){++checks;assert(ok);};
 auto run=[&](int status,const std::string& expected){
  ++cases;nextStatus=status;std::string error="unchanged";int before=calls;
  check(!prepare_subdirs("prepare","test-volume",10,3,&error));check(calls==before+1);
  check(error==expected);check(received==std::vector<std::string>({prepare_subdirs_path,"prepare","test-volume","10","3"}));
  check(!prepare_subdirs("prepare","test-volume",10,3,nullptr));
 };
 const char* names[]={"selinux-contexts","user-de","sdk-sandbox-de","vold-de","storaged-de","rollback-de","profiles-de","fingerprint-de","face-de","user-ce","sdk-sandbox-ce","vold-ce","storaged-ce","rollback-ce","checkin-ce","backup-ce","backup-stage-ce","appsearch-ce","face-ce"};
 for(int i=32;i<=50;++i)run(i,"prepare-subdirs/"+std::string(names[i-32])+":status="+std::to_string(i));
 for(int i:{1,99,255})run(i,"prepare-subdirs/unknown:status="+std::to_string(i));
 for(int i:{-ECHILD,-EINTR,-ENOMEM,INT_MIN})run(i,"prepare-subdirs/subprocess-error:status="+std::to_string(i));
 ++cases;nextStatus=0;std::string error="unchanged";check(prepare_subdirs("prepare","",0,1,&error));check(error=="unchanged");check(prepare_subdirs("prepare","",0,1,nullptr));
 std::cout<<"{\"cases\":"<<cases<<",\"assertions\":"<<checks<<",\"passed\":true}";
}
'''.replace('HEADER',header).replace('METHOD',native)
(T/'Subdirs.cpp').write_text(cpp)
subdirs=execute(cpp,'native')
mutant=cpp.replace('status < 0 ? "subprocess-error" : PrepareSubdirsErrorName(status)','PrepareSubdirsErrorName(status)')
assert mutant!=cpp
negative['negative-status-unknown']=execute(mutant,'native',False)

# Reuse the nine prior UI cases unchanged; adapt only the private model and resource names.
subprocess.run(['python3',str(PACKAGE/'tests/failure-diagnostics-ui-regressions.py'),str(R),'--output-dir',str(T/'ui')],check=True,capture_output=True,text=True)
uiresult=json.loads((T/'ui/regressions.json').read_text());assert all(x['passed'] for x in uiresult['results'])
for loc in ['values','values-zh-rCN']:
    resource=R/'frameworks/base/packages/PackageInstaller/res'/loc/'frp_install.xml'
    node=ET.parse(resource).find("string[@name='message_install_failed_protection_active']")
    assert node is not None and node.text
    text=node.text
    assert 'is blocking app installation' not in text and '系统暂时禁止安装应用' not in text
    assert ('may also have caused' in text) if loc=='values' else ('也可能由其他权限或安装会话问题导致' in text)
    negative['definitive-cause-text-'+loc]={'rejected':True,'scope':'old XML assertion; not executable runtime mutation'}
source_files=['system/vold/FsCrypt.cpp', 'frameworks/base/packages/PackageInstaller/src/com/android/packageinstaller/v2/model/InstallRepository.kt', 'frameworks/base/packages/PackageInstaller/src/com/android/packageinstaller/v2/model/InstallStages.kt', 'frameworks/base/packages/PackageInstaller/src/com/android/packageinstaller/v2/ui/fragments/InstallationFragment.java', 'frameworks/base/packages/PackageInstaller/res/values/frp_install.xml', 'frameworks/base/packages/PackageInstaller/res/values-zh-rCN/frp_install.xml']
result=dict(passed=True,installer=installer,subdirs=subdirs,ui_cases=len(uiresult['results']),
    negative_controls=negative,source_sha256={name:sha(R/name) for name in source_files},
    scope='Actual extracted production methods/model and UI with host doubles; no phone/FRP activation/encrypted-storage test.')
if args.output:args.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
