# SPDX-License-Identifier: GPL-3.0-or-later
"""Review2: execute shared/device init rules together and real verification/error branches."""
import argparse,json,os,pathlib,re,resource,shlex,subprocess,tempfile
p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=pathlib.Path)
source=p.parse_args().source.resolve();recovery=source/'bootable/recovery';device=source/'device/xiaomi/diting'
tests=pathlib.Path(__file__).parent
prefix=(tests/'ofrp-device-regressions.py').read_text().split("scripts=device/'recovery/root/system/bin'")[0]
ns={};exec(compile(prefix,str(tests/'ofrp-device-regressions.py'),'exec'),ns)
Usb=ns['Usb'];device_actions=list(ns['actions'])
def actions(text):
    result=[];current=None
    for line in text.splitlines():
        if line.startswith('on property:'):
            condition=dict(x.removeprefix('property:').split('=',1) for x in line[3:].split(' && '));current=(condition,[]);result.append(current)
        elif line and not line[0].isspace() and not line.startswith('#'):current=None
        elif current is not None and line.strip() and not line.lstrip().startswith('#'):current[1].append(shlex.split(line))
    return result
common=(recovery/'etc/init.rc').read_text();common_actions=actions(common)
assert 'setprop sys.usb.device_config ${vendor.recovery.usb.device_config:-0}' in common
assert 'vendor.usb.use_ffs_mtp=1' in (device/'vendor.prop').read_text()
assert 'vendor.recovery.usb.device_config=1' in (device/'vendor.prop').read_text()
for line in common.splitlines():
    if line.startswith('on property:sys.usb.config=') or line.startswith('on fs && property:sys.usb.configfs='):
        assert 'property:sys.usb.device_config=0' in line,line
ns['actions']=device_actions+common_actions
modes=['none','adb','mtp','mtp,adb','mass_storage','mass_storage,adb','fastboot','sideload']
def mode(u,name):
    u.event('sys.usb.config',name)
    if 'adb' in name or name in ('fastboot','sideload'):u.event('sys.usb.ffs.ready','1')
    if 'mtp' in name:u.event('sys.usb.ffs.mtp.ready','1')
def expect(u,name,ffs):
    if name not in ('fastboot','sideload'):u.expect(name,ffs);return
    values=[v.rsplit('/',1)[-1] for k,v in sorted(u.links.items()) if '/configs/b.1/f' in k]
    assert values==(['ffs.fastboot'] if name=='fastboot' else ['ffs.adb']) and u.bound
    assert u.props['sys.usb.state']==name and not u.errors,u.errors
count=0
for ffs in (0,1):
    for before in modes:
        for after in modes:
            u=Usb(ffs);u.props['sys.usb.device_config']='1'
            mode(u,'none');mode(u,before);expect(u,before,ffs)
            # Production fastboot/sideload callers disconnect through none first.
            mode(u,'none');mode(u,after);expect(u,after,ffs);count+=1
# Default devices still use the unchanged generic composition behavior.
ns['actions']=common_actions
for selected in ('adb','fastboot','sideload'):
    u=Usb(0);u.props['sys.usb.device_config']='0';mode(u,'none');mode(u,selected);expect(u,selected,0)
# A negative control reintroduces the actual cross-file collision.
old=subprocess.check_output(['git','-C',str(recovery),'show','HEAD:etc/init.rc']).decode()
old_actions=actions(old)
# Also remains useful after the fix is committed: explicitly remove only its selector.
old_actions=[({k:v for k,v in c.items() if k!='sys.usb.device_config'},cmd) for c,cmd in old_actions]
ns['actions']=device_actions+old_actions
u=Usb(1);u.props['sys.usb.device_config']='1';mode(u,'none');mode(u,'adb')
assert 'EEXIST' in u.errors or 'changed bound configuration' in u.errors,'negative control missed shared init collision'

def method(text,name):
    m=re.search(r'^(?:static )?(?:bool|int)[ \t\n]+'+name+r'\([^;{]*\)\s*\{',text,re.M);assert m,name
    masked=re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',lambda m:' '*len(m[0]),text)
    pos=m.end();depth=1
    while depth:depth+=(masked[pos]=='{')-(masked[pos]=='}');pos+=1
    return text[m.start():pos]
tw=(recovery/'twrpinstall/install.cpp').read_text();cmd=(recovery/'twrpinstall/installcommand.cpp').read_text();gui=(recovery/'twrpinstall/twinstall.cpp').read_text()
verify=method(tw,'verify_package');compat=method(cmd,'verify_package_compatibility')
assert 'ExtractToMemory' not in compat and 'std::string zip_content' not in compat
start=gui.index('            ret_val = check_ab_package(Zip);')
end=gui.index('\t\t\tLOGINFO("AB zip',start)
guard=gui[start:end]
tail=gui[gui.index('  if (ret_val == INSTALL_CORRUPT)',end):gui.index('  else // success -',end)]
code=r'''
#include <cassert>
#include <cstdio>
#include <sstream>
#include <string>
#include <vector>
#define LOG(x) std::ostringstream()
enum {VERIFY_SUCCESS=0,kZipVerificationFailure=1,INSTALL_SUCCESS=0,INSTALL_ERROR=1,INSTALL_CORRUPT=2,OTA_CORRUPT=20,OTA_ERROR=21};
struct Package{};struct Certificate{};int key_count=1,signature_status=0,verification_calls=0;
std::vector<Certificate> LoadKeysFromZipfile(const char*){return std::vector<Certificate>(key_count);}
int verify_file(Package*,const std::vector<Certificate>&){verification_calls++;return signature_status;}
struct ZipEntry64 {unsigned long long uncompressed_length=0;};struct Zip{bool compatibility=false;unsigned long long bytes=0;};using ZipArchiveHandle=Zip*;
int FindEntry(Zip* z,const char*,ZipEntry64* e){e->uncompressed_length=z->bytes;return z->compatibility?0:-1;}
int status=-1,errors=0,flashes=0,result=0;bool status_corrupt=false;
void set_miui_install_status(int value,bool corrupt){status=value;status_corrupt=corrupt;}
void gui_err(const char*){errors++;}int check_ab_package(Zip*){return result;}
'''+verify+'\n'+compat+'\n'+'''int RunAbPreflight(Zip* Zip) {
int ret_val=0;
'''+guard+'''flashes++; }
'''+tail+'''return ret_val;
}
'''+r'''
int main(){Package package;
 for(int code: {1,-1,7}){signature_status=code;assert(!verify_package(&package));}
 signature_status=VERIFY_SUCCESS;assert(verify_package(&package));key_count=0;
 int calls=verification_calls;assert(!verify_package(&package)&&verification_calls==calls);
 Zip z;assert(verify_package_compatibility(&z));z.compatibility=true;
 for(auto bytes:{0ULL,1ULL,1024ULL*1024*1024,~0ULL}){z.bytes=bytes;assert(!verify_package_compatibility(&z));}
 for(int code:{INSTALL_ERROR,INSTALL_CORRUPT}){result=code;status=-1;errors=flashes=0;assert(RunAbPreflight(&z)==code);assert(flashes==0&&errors>0&&status==(code==INSTALL_ERROR?OTA_ERROR:OTA_CORRUPT));}
 result=INSTALL_SUCCESS;status=-1;errors=flashes=0;assert(RunAbPreflight(&z)==0&&flashes==1&&errors==0&&status==-1);
}
'''
with tempfile.TemporaryDirectory(prefix='ofrp-cross-file-') as tmp:
    folder=pathlib.Path(tmp)
    def probe(label,code,success):
        cpp=folder/(label+'.cpp');cpp.write_text(code);exe=folder/label
        result=subprocess.run(['g++','-std=c++17','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(cpp),'-o',str(exe)],capture_output=True,text=True)
        assert result.returncode==0,result.stderr
        result=subprocess.run([str(exe)],capture_output=True,text=True,preexec_fn=lambda:resource.setrlimit(resource.RLIMIT_CORE,(0,0)))
        assert (result.returncode==0)==success,(label,result.stdout,result.stderr)
    probe('actual',code,True)
    broken=verify.replace('    return false;\n  }\n  return true;', '    /* lost failure return */\n  }\n  return true;')
    assert broken!=verify;probe('lost-signature-return',code.replace(verify,broken),False)
    broken_guard=guard.replace('            if (ret_val != INSTALL_SUCCESS) {','            if (ret_val != INSTALL_SUCCESS) return ret_val;\n            if (ret_val != INSTALL_SUCCESS) {')
    probe('lost-error-tail',code.replace(guard,broken_guard),False)
assert 'CheckPackageMetadata(metadata, OtaType::AB)' in cmd
assert 'pkg_pre_build_fingerprint != value' not in cmd
assert 'OF_RECOVERY_AB_FULL_REFLASH_RAMDISK := 1' not in (device/'fox_diting.mk').read_text()
assert all(x in (device/'device.mk').read_text().split('AB_OTA_PARTITIONS ?=',1)[1].splitlines()[0].split() for x in ('system','system_ext','product'))
with tempfile.TemporaryDirectory(prefix='ofrp-product-') as tmp:
    make=pathlib.Path(tmp)/'test.mk'
    make.write_text('include '+str(device/'fox_diting.mk')+'\nall:\n\t@test "$(FOX_TARGET_DEVICES)" = "diting,ditingp"\n\t@test "$(FOX_VIRTUAL_AB_DEVICE)" = "1"\n')
    subprocess.run(['make','-s','-f',str(make)],check=True,env={k:v for k,v in os.environ.items() if not k.startswith('FOX_')})
print(json.dumps(dict(passed=True,shared_and_device_usb_transitions=count,generic_usb_fallback_modes=3,negative_controls=3,actual_signature_wrapper_and_ab_error_tail_asan_ubsan=True,legacy_compatibility_archive_no_allocation_and_fail_closed=True,product_defaults_without_shell_exports=True,phone_tested=False),indent=2))
