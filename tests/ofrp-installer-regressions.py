# SPDX-License-Identifier: GPL-3.0-or-later
"""Execute actual recovery package guards/setup paths with fault-controlled host ZIP and process APIs."""
import argparse,pathlib,re,subprocess,tempfile
p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=pathlib.Path)
source=p.parse_args().source.resolve(strict=True);recovery=source/'bootable/recovery'
def method(text,name):
    m=re.search(r'^(?:static )?(?:bool|int)[ \t\n]+'+name+r'\([^;{]*\)\s*\{',text,re.M);assert m,name
    masked=re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',lambda m:' '*len(m[0]),text)
    pos=m.end();depth=1
    while depth:depth+=(masked[pos]=='{')-(masked[pos]=='}');pos+=1
    return text[m.start():pos]
tw=(recovery/'twrpinstall/install.cpp').read_text();core=(recovery/'install/install.cpp').read_text()
cmd=(recovery/'twrpinstall/installcommand.cpp').read_text();gui=(recovery/'twrpinstall/twinstall.cpp').read_text()
code=r'''
#include <algorithm>
#include <cassert>
#include <cerrno>
#include <cstdarg>
#include <cstdio>
#include <cstring>
#include <map>
#include <memory>
#include <sstream>
#include <string>
#include <vector>
#include "diting_ota_aliases.h"
#define __unused
#define CHECK(x) assert(x)
#define LOG(x) std::ostringstream()
#define PLOG(x) std::ostringstream()
#define LOGERR(...) ((void)0)
enum {INSTALL_SUCCESS,INSTALL_ERROR,INSTALL_CORRUPT};
enum class OtaType {AB,BLOCK,BRICK};
const char* RELEASE_KEYS_TAG="release-keys";
std::map<std::string,std::string> props={{"ro.product.device","diting"},{"ro.twrp.target.devices","diting, ditingp"},{"ro.serialno","fixture"},{"ro.build.version.incremental","123"},{"ro.build.fingerprint","fixture/build"}};
namespace android::base {
std::string GetProperty(const std::string& k,const std::string& fallback){return props.count(k)?props[k]:fallback;}
std::string Trim(std::string s){auto l=s.find_first_not_of(" \t\r\n");return l==s.npos?"":s.substr(l,s.find_last_not_of(" \t\r\n")-l+1);}
std::vector<std::string> Split(const std::string& s,const std::string& delimiters){std::vector<std::string> out;size_t l=0;for(;;){auto r=s.find_first_of(delimiters,l);out.push_back(s.substr(l,r-l));if(r==s.npos)return out;l=r+1;}}
std::string StringPrintf(const char* format,...){char b[4096];va_list a;va_start(a,format);vsnprintf(b,sizeof(b),format,a);va_end(a);return b;}
struct unique_fd {int fd=-1;int get(){return fd;}void reset(){fd=-1;}};
bool pipe_ok=true;int pipe_calls=0;
bool Pipe(unique_fd* a,unique_fd* b,int){pipe_calls++;a->fd=10;b->fd=11;return pipe_ok;}
}
std::string get_value(const std::map<std::string,std::string>& m,const std::string& k){auto it=m.find(k);return it==m.end()?"":it->second;}
std::string OtaTypeToString(OtaType t){return t==OtaType::AB?"AB":t==OtaType::BRICK?"BRICK":"BLOCK";}
bool CheckCoreAbSpecificMetadata(const std::map<std::string,std::string>&){return true;}
void property_get(const char* k,char* value,const char* fallback){strcpy(value,android::base::GetProperty(k,fallback).c_str());}
constexpr int PROPERTY_VALUE_MAX=256;
struct ZipEntry64 {uint64_t uncompressed_length=0;long offset=64;int kind=0;};
struct Zip {std::string metadata="ota-type=AB\npre-device=ditingp\n";bool meta=true,properties=true,payload=true,updater=false,extract_meta=true,extract_properties=true;
uint64_t meta_size=0,property_size=4;};using ZipArchiveHandle=Zip*;
int FindEntry(Zip* z,const std::string& name,ZipEntry64* e){
 if(name=="META-INF/com/android/metadata"){e->kind=1;e->uncompressed_length=z->meta_size?z->meta_size:z->metadata.size();return z->meta?0:-1;}
 if(name=="payload_properties.txt"){e->kind=2;e->uncompressed_length=z->property_size;return z->properties?0:-1;}
 if(name=="payload.bin"){e->kind=3;return z->payload?0:-1;}return z->updater?0:-1;
}
int ExtractToMemory(Zip* z,ZipEntry64* e,uint8_t* dest,size_t size){
 if(e->kind==1){if(!z->extract_meta)return -1;memcpy(dest,z->metadata.data(),size);return 0;}
 if(!z->extract_properties)return -1;memset(dest,'x',size);return 0;
}
const char* ErrorCodeString(int){return "fixture failure";}
const char* UPDATE_BINARY_NAME="META-INF/com/google/android/update-binary";
const char* AB_OTA_PAYLOAD_PROPERTIES="payload_properties.txt";const char* AB_OTA_PAYLOAD="payload.bin";
Zip* active;bool package_ok=true;
struct Package {static std::unique_ptr<Package> CreateMemoryPackage(const std::string&){return package_ok?std::make_unique<Package>():nullptr;}Zip* GetZipArchiveHandle(){return active;}};
void read_source_target_build(Zip*){}void ReadSourceTargetBuild(const std::map<std::string,std::string>&,std::vector<std::string>*){}
constexpr int kUpdateBinaryCommandFailure=1;
int legacy_result=0;bool empty_legacy=false;
int SetUpNonAbUpdateCommands(const std::string&,Zip*,int,int,std::vector<std::string>* args){if(!empty_legacy)args->push_back("legacy-updater");return legacy_result;}
'''
code+=method(tw,'CheckAbSpecificMetadata').replace('CheckAbSpecificMetadata','CheckTwAbSpecificMetadata')+'\n'
code+=method(core,'CheckPackageMetadata').replace('CheckPackageMetadata','CheckCorePackageMetadata').replace('CheckAbSpecificMetadata','CheckCoreAbSpecificMetadata')+'\n'
code+=method(tw,'CheckPackageMetadata').replace('CheckPackageMetadata','CheckTwPackageMetadata').replace('CheckAbSpecificMetadata','CheckTwAbSpecificMetadata')+'\n'
code+='int CheckPackageMetadata(const std::map<std::string,std::string>& m,OtaType t){return CheckTwPackageMetadata(m,t);}\n'
for text,name in ((tw,'ReadMetadataFromPackage'),(cmd,'check_ab_package'),(cmd,'abupdate_binary_command'),(tw,'SetUpAbUpdateCommands')):code+=method(text,name)+'\n'
code+=method(core,'ReadMetadataFromPackage').replace('ReadMetadataFromPackage','ReadCoreMetadataFromPackage')+'\n'
prefix=method(tw,'try_update_binary').split('  pid_t pid = fork();')[0]
code+=prefix+'  return INSTALL_SUCCESS;\n}\n'
gui_prefix=method(gui,'Run_Update_Binary').split('\tif (pid == 0) {')[0]
for old,new in [('pipe(', 'ProbePipe('),('close(', 'ProbeClose('),('fdopen(', 'ProbeFdopen('),('fork()', 'ProbeFork()'),('fclose(', 'ProbeFclose(')]:gui_prefix=re.sub(r'\b'+re.escape(old),lambda m:new,gui_prefix)
code+=r'''
enum zip_type{UNKNOWN_ZIP_TYPE,UPDATE_BINARY_ZIP_TYPE,AB_OTA_ZIP_TYPE};
int pipe_failure=0,fork_failure=0,fdopen_failure=0,forks=0,closed=0,streams_closed=0;
int ProbePipe(int* f){if(pipe_failure)return -1;f[0]=10;f[1]=11;return 0;}int ProbeClose(int){closed++;return 0;}
FILE* ProbeFdopen(int,const char*){return fdopen_failure?nullptr:reinterpret_cast<FILE*>(1);}
int ProbeFclose(FILE*){streams_closed++;return 0;}int ProbeFork(){forks++;return fork_failure?-1:123;}
int update_binary_command(const char*,int,int,std::vector<std::string>* args){if(!empty_legacy)args->push_back("legacy-updater");return legacy_result;}
'''+gui_prefix+'    return INSTALL_SUCCESS;\n}\n'
code+=r'''
void expect_metadata(std::map<std::string,std::string> m,bool allowed){assert(CheckCorePackageMetadata(m,OtaType::AB)==allowed);assert((CheckTwPackageMetadata(m,OtaType::AB)==0)==allowed);}
int main(){
 std::map<std::string,std::string> meta={{"ota-type","AB"},{"pre-device","ditingp"}};
 expect_metadata(meta,true);for(auto value:{"other | diting ","diting | ditingp"}){meta["pre-device"]=value;expect_metadata(meta,true);}
 for(auto value:{"", "diting_other","notditing|other"}){meta["pre-device"]=value;expect_metadata(meta,false);}
 meta["pre-device"]="ditingp";meta["serialno"]="other | fixture ";expect_metadata(meta,true);meta["serialno"]="wrong";expect_metadata(meta,false);meta.erase("serialno");
 meta["ota-type"]="BLOCK";expect_metadata(meta,false);meta["ota-type"]="AB";
 props["ro.product.device"]="raphael";expect_metadata(meta,false);props["ro.product.device"]="diting";
 Zip z;active=&z;std::vector<std::string> args={"stale"};std::map<std::string,std::string> parsed;
 assert(ReadCoreMetadataFromPackage(&z,&parsed));
 z.metadata="";assert(!ReadCoreMetadataFromPackage(&z,&parsed)&&!ReadMetadataFromPackage(&z,&parsed));
 z.metadata="ota-type=AB\npre-device=ditingp\n";
 for(auto bytes:{1024ULL*1024+1,1ULL<<40}){z.meta_size=bytes;assert(!ReadCoreMetadataFromPackage(&z,&parsed)&&!ReadMetadataFromPackage(&z,&parsed));}z.meta_size=0;
 z.extract_meta=false;assert(!ReadCoreMetadataFromPackage(&z,&parsed));z.extract_meta=true;
 assert(check_ab_package(&z)==0);assert(abupdate_binary_command("fixture.zip",0,3,&args)==0&&args.size()==5&&args.front()=="/system/bin/update_engine_sideload");
 for(auto value:{"other | fixture/build", "fixture/build|another"}){z.metadata=std::string("ota-type=AB\npre-device=ditingp\npre-build=")+value+"\n";assert(check_ab_package(&z)==0);}
 for(auto value:{"fixture/build_other", "wrong|another"}){z.metadata=std::string("ota-type=AB\npre-device=ditingp\npre-build=")+value+"\n";assert(check_ab_package(&z)!=0);}
 z.metadata="ota-type=AB\npre-device=ditingp\n";
 z.extract_properties=false;assert(abupdate_binary_command("fixture.zip",0,3,&args)==INSTALL_CORRUPT&&args.empty());z.extract_properties=true;
 z.payload=false;assert(abupdate_binary_command("fixture.zip",0,3,&args)==INSTALL_CORRUPT);z.payload=true;
 z.properties=false;assert(abupdate_binary_command("fixture.zip",0,3,&args)==INSTALL_CORRUPT);z.properties=true;
 for(auto n:{uint64_t(0),uint64_t(1048577),uint64_t(1)<<32}){z.property_size=n;assert(abupdate_binary_command("fixture.zip",0,3,&args)==INSTALL_CORRUPT);}z.property_size=4;
 z.meta=false;assert(check_ab_package(&z)==INSTALL_CORRUPT);z.meta=true;
 z.meta_size=uint64_t(1)<<32;assert(check_ab_package(&z)==INSTALL_CORRUPT);z.meta_size=0;
 z.extract_meta=false;assert(check_ab_package(&z)==INSTALL_CORRUPT);z.extract_meta=true;
 z.metadata="garbage\n";assert(check_ab_package(&z)!=0);
 z.metadata="ota-type=AB\npre-device=wrong\n";assert(check_ab_package(&z)!=0);
 z.metadata="ota-type=AB\npre-device=ditingp\npre-build-incremental=wrong\n";assert(check_ab_package(&z)!=0);
 z.metadata="ota-type=AB\npre-device=ditingp\npre-build=wrong\n";assert(check_ab_package(&z)!=0);
 z=Zip{};bool wipe=false;int temperature=0;std::vector<std::string> log;
 assert(try_update_binary("fixture.zip",&z,&wipe,&log,0,&temperature)==0);
 z.meta=false;assert(try_update_binary("fixture.zip",&z,&wipe,&log,0,&temperature)==INSTALL_CORRUPT);
 z.updater=true;assert(try_update_binary("addon.zip",&z,&wipe,&log,0,&temperature)==0); // legacy add-ons remain supported
 legacy_result=INSTALL_ERROR;assert(try_update_binary("addon.zip",&z,&wipe,&log,0,&temperature)==INSTALL_ERROR);legacy_result=0;
 empty_legacy=true;assert(try_update_binary("addon.zip",&z,&wipe,&log,0,&temperature)==INSTALL_CORRUPT);empty_legacy=false;
 pipe_failure=1;assert(Run_Update_Binary("addon.zip",nullptr,UPDATE_BINARY_ZIP_TYPE)==INSTALL_ERROR&&forks==0);pipe_failure=0;
 legacy_result=INSTALL_ERROR;assert(Run_Update_Binary("addon.zip",nullptr,UPDATE_BINARY_ZIP_TYPE)==INSTALL_ERROR&&forks==0);legacy_result=0;
 empty_legacy=true;assert(Run_Update_Binary("addon.zip",nullptr,UPDATE_BINARY_ZIP_TYPE)==INSTALL_CORRUPT&&forks==0);empty_legacy=false;
 fdopen_failure=1;assert(Run_Update_Binary("addon.zip",nullptr,UPDATE_BINARY_ZIP_TYPE)==INSTALL_ERROR&&forks==0);fdopen_failure=0;
 fork_failure=1;assert(Run_Update_Binary("addon.zip",nullptr,UPDATE_BINARY_ZIP_TYPE)==INSTALL_ERROR&&streams_closed==1);fork_failure=0;
 assert(Run_Update_Binary("addon.zip",nullptr,UPDATE_BINARY_ZIP_TYPE)==0);
}
'''
with tempfile.TemporaryDirectory(prefix='ofrp-installer-') as tmp:
    d=pathlib.Path(tmp);cpp=d/'probe.cpp';cpp.write_text(code);exe=d/'probe'
    result=subprocess.run(['g++','-std=gnu++17','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(recovery),str(cpp),'-o',str(exe)],capture_output=True,text=True)
    assert result.returncode==0,result.stdout+result.stderr
    result=subprocess.run([str(exe)],capture_output=True,text=True);assert result.returncode==0,result.stdout+result.stderr
assert 'ret_val = check_ab_package(Zip);' in gui and gui.index('ret_val = check_ab_package(Zip);')<gui.index('TWFunc::IsRecoveryOverwritten(true);')
assert 'TWinstall_zip(FUSE_SIDELOAD_HOST_PATHNAME' in (recovery/'twrpinstall/adb_install.cpp').read_text()
print('PASS: actual metadata/device/serial/alias guards, GUI/sideload shared preflight, bounded metadata, payload failures, legacy add-ons, empty argv, pipe/stream/fork failures under ASAN/UBSAN; no device writes')
