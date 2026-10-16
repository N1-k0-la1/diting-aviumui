"""Exercise actual device init actions and shell workers against isolated fake sysfs trees."""
import argparse,itertools,json,os,pathlib,shlex,subprocess,tempfile,time,xml.etree.ElementTree as ET
p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=pathlib.Path)
source=p.parse_args().source.resolve(strict=True);device=source/'device/xiaomi/diting'
actions=[];current=None
usb=(device/'recovery/root/init.recovery.usb.rc').read_text()
for line in usb.splitlines():
 if line.startswith('on property:'):
  condition=dict(x.removeprefix('property:').split('=',1) for x in line[3:].split(' && '));current=(condition,[]);actions.append(current)
 elif line and not line[0].isspace() and not line.startswith('#'):current=None
 elif current is not None and line.strip() and not line.lstrip().startswith('#'):current[1].append(shlex.split(line))
assert len({tuple(sorted(c.items())) for c,_ in actions})==len(actions),'duplicate property actions'
class Usb:
 def __init__(self,ffs):
  self.props={'sys.usb.config':'none','sys.usb.configfs':'1','vendor.usb.use_ffs_mtp':str(ffs),'sys.usb.ffs.ready':'0','sys.usb.ffs.mtp.ready':'0','sys.usb.controller':'controller'}
  self.links={};self.bound=False;self.errors=[]
 def event(self,key,value):
  self.props[key]=value
  selected=[commands for cond,commands in actions if key in cond and all((k in self.props and (v=='*' or self.props[k]==v)) for k,v in cond.items())]
  for commands in selected:
   for cmd in commands:
    name,*args=cmd
    if name=='rm':self.links.pop(args[0],None)
    elif name=='symlink':
     if self.bound:self.errors.append('changed bound configuration')
     if args[1] in self.links:self.errors.append('EEXIST')
     else:self.links[args[1]]=args[0]
    elif name=='write' and args[0].endswith('/UDC'):
     self.bound=args[1]!='none'
     if self.bound:
      if any(v.endswith('ffs.adb') for v in self.links.values()) and self.props['sys.usb.ffs.ready']!='1':self.errors.append('ADB not ready')
      if any(v.endswith('ffs.mtp') for v in self.links.values()) and self.props['sys.usb.ffs.mtp.ready']!='1':self.errors.append('MTP not ready')
    elif name=='setprop':self.props[args[0]]=self.props['sys.usb.config'] if args[1]=='${sys.usb.config}' else args[1]
 def mode(self,name):
  self.event('sys.usb.config',name)
  if 'adb' in name:self.event('sys.usb.ffs.ready','1')
  if 'mtp' in name:self.event('sys.usb.ffs.mtp.ready','1')
 def expect(self,name,ffs):
  functions=[v.rsplit('/',1)[-1] for k,v in sorted(self.links.items()) if '/configs/b.1/f' in k]
  expected={'none':[],'adb':['ffs.adb'],'mtp':['ffs.mtp' if ffs else 'mtp.gs0'],
   'mtp,adb':['ffs.mtp' if ffs else 'mtp.gs0','ffs.adb'],'mass_storage':['mass_storage.0'],'mass_storage,adb':['ffs.adb','mass_storage.0']}[name]
  assert functions==expected,(name,functions,expected)
  assert self.bound==(name!='none') and self.props.get('sys.usb.state')==name,(name,self.props)
  assert not self.errors,self.errors
modes=['none','adb','mtp','mtp,adb','mass_storage','mass_storage,adb'];transitions=0
for ffs,a,b in itertools.product((0,1),modes,modes):
 u=Usb(ffs);u.mode(a);u.expect(a,ffs)
 for n in range(3,10):u.links[f'/config/usb_gadget/g1/configs/b.1/f{n}']='stale'
 u.mode(b);u.expect(b,ffs);transitions+=1
for first in ('sys.usb.ffs.ready','sys.usb.ffs.mtp.ready'):
 u=Usb(1);u.event('sys.usb.config','mtp,adb');assert not u.bound
 u.event(first,'1');assert not u.bound
 other='sys.usb.ffs.ready' if first.endswith('mtp.ready') else 'sys.usb.ffs.mtp.ready'
 u.event(other,'1');u.expect('mtp,adb',1)

scripts=device/'recovery/root/system/bin'
for name in ('postrecoveryboot.sh','postscreenunblank.sh','diting-adsp-init.sh'):
 subprocess.run(['sh','-n',str(scripts/name)],check=True)
with tempfile.TemporaryDirectory(prefix='ofrp-sysfs-') as tmp:
 r=pathlib.Path(tmp);bin=r/'bin';bin.mkdir();(r/'tmp').mkdir();sysroot=r/'sys'
 goodix=sysroot/'bus/platform/devices/goodix_ts.0';goodix.mkdir(parents=True)
 brightness=sysroot/'class/backlight/panel0-backlight/brightness';brightness.parent.mkdir(parents=True);brightness.write_text('200\n')
 for name,value in [('chip_info','rom_pid:\n'),('reset',''),('irq_info','state:disabled\n')]: (goodix/name).write_text(value)
 adsp=sysroot/'class/remoteproc/remoteproc0';adsp.mkdir(parents=True)
 (adsp/'name').write_text('30000000.remoteproc\n');(adsp/'firmware').write_text('adsp.mdt\n');(adsp/'state').write_text('offline\n')
 boot=sysroot/'kernel/boot_adsp/boot';boot.parent.mkdir(parents=True);boot.write_text('')
 (sysroot/'class/power_supply/battery').mkdir(parents=True)
 env=os.environ.copy();env.update(PATH=str(bin)+':'+env.get('PATH',''),FAKE_ROOT=str(r),VALID_PID='rom_pid: BERLIN\n')
 def executable(path,text):path.write_text(text);path.chmod(0o755)
 cat='''#!/usr/bin/python3
import os,pathlib,sys,time
p=pathlib.Path(sys.argv[1]);root=pathlib.Path(os.environ['FAKE_ROOT']);g=root/'sys/bus/platform/devices/goodix_ts.0'
if p==g/'chip_info':
 if (g/'reset').read_text().strip()=='1':print(os.environ.get('VALID_PID','rom_pid:BERLIN'),end='');sys.exit()
 value=p.read_text()
 if value.strip()=='rom_pid:':
  with (root/'blank-reads').open('a') as f:f.write('blank\\n')
  time.sleep(float(os.environ.get('BLANK_DELAY','0')))
 print(value,end='');sys.exit()
if p==root/'sys/class/remoteproc/remoteproc0/state' and os.environ.get('DSP_FAIL')!='1':
 if (root/'sys/kernel/boot_adsp/boot').read_text().strip()=='1':print('running');sys.exit()
print(p.read_text(),end='')
'''
 executable(bin/'cat',cat)
 executable(bin/'setprop','''#!/bin/sh
printf '%s %s\\n' "$1" "$2" >> "$FAKE_ROOT/properties"
''')
 executable(bin/'sleep','''#!/bin/sh
if [ "$1" = 0.2 ] && [ -n "$BLOCK_WAKE" ]; then
    touch "$FAKE_ROOT/sleep-started"
    /usr/bin/python3 -c 'import os,pathlib,time; p=pathlib.Path(os.environ["FAKE_ROOT"])/"release-sleep"; deadline=time.monotonic()+8; exec("while not p.exists() and time.monotonic()<deadline: time.sleep(.01)")'
fi
''')
 def staged(name):
  t=(scripts/name).read_text().replace('#!/system/bin/sh','#!/bin/sh').replace('/sys/',str(sysroot)+'/').replace('/tmp/diting_',str(r/'tmp')+'/diting_')
  if name=='postscreenunblank.sh':t=t.replace('/system/bin/postrecoveryboot.sh',str(bin/'wake-common'))
  path=bin/name;executable(path,t);return path
 common=staged('postrecoveryboot.sh');wake=staged('postscreenunblank.sh');dsp=staged('diting-adsp-init.sh')
 executable(bin/'wake-common',f'#!/bin/sh\n"{common}" "$@"\ntouch "$FAKE_ROOT/wake-done"\n')
 def run(path,*args,allowed=(0,),extra=None):
  e=env.copy();e.update(extra or {});result=subprocess.run(['sh',str(path),*args],env=e,capture_output=True,text=True,timeout=20)
  assert result.returncode in allowed,result.stdout+result.stderr;return result
 # Exact startup recovery, whitespace, and enabled/unknown IRQ behavior.
 for irq,after,expected in [('state:disabled\n','rom_pid:BERLIN\n','1'),('state:enabled\n','rom_pid: BERLIN\n','state:enabled'),('unknown\n','rom_pid:\tBERLIN\r\n','unknown'),('state:disabled\n','rom_pid:OTHER\n','state:disabled')]:
  (goodix/'reset').write_text('');(goodix/'irq_info').write_text(irq)
  run(common,extra={'VALID_PID':after});assert (goodix/'reset').read_text().strip()=='1'
  assert (goodix/'irq_info').read_text().strip()==expected
 # A valid controller must never be reset.
 (goodix/'chip_info').write_text('rom_pid:BERLIN\n');(goodix/'reset').write_text('');run(common);assert not (goodix/'reset').read_text()
 (goodix/'chip_info').write_text('rom_pid:\n');(goodix/'reset').write_text('');(goodix/'irq_info').write_text('state:disabled\n')
 (r/'blank-reads').write_text('');parallel_env=env|{'BLANK_DELAY':'0.2'}
 children=[subprocess.Popen(['sh',str(common)],env=parallel_env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE) for _ in range(24)]
 for child in children:assert child.communicate(timeout=10)[1]==b'' and child.returncode==0
 assert (r/'blank-reads').read_text().splitlines()==['blank'],'concurrent controller resets'
 assert not (r/'tmp/diting_goodix_reset.lock').exists()
 # The UI hook must return while its delayed child is still blocked.
 (goodix/'reset').write_text('');brightness.write_text('0\n')
 run(wake,extra={'BLOCK_WAKE':'1'});assert not (r/'wake-done').exists()
 (r/'release-sleep').touch()
 deadline=time.monotonic()+5
 while not (r/'wake-done').exists() and time.monotonic()<deadline:time.sleep(.01)
 assert (r/'wake-done').exists() and not (goodix/'reset').read_text(),'late wake probe reset sleeping controller'
 brightness.write_text('200\n');run(common,'unblank');assert (goodix/'reset').read_text().strip()=='1'
 # The ADSP name may be a platform address; use firmware identity too.
 run(dsp);assert (r/'properties').read_text().strip()=='vendor.recovery.adsp.ready 1'
 stamp=boot.stat().st_mtime_ns;run(dsp);assert boot.stat().st_mtime_ns==stamp,'already-running ADSP booted twice'
 (r/'properties').unlink();boot.write_text('');run(dsp,allowed=(1,),extra={'DSP_FAIL':'1'});assert not (r/'properties').exists()
 assert not (r/'tmp/diting_adsp_init.lock').exists()
 # Unknown remote processors are never booted through the ADSP node.
 (adsp/'firmware').write_text('cdsp.mdt\n');boot.write_text('');run(dsp,allowed=(1,));assert not boot.read_text()

qcom=(device/'recovery/root/init.recovery.qcom.rc').read_text()
assert 'write /sys/kernel/boot_adsp/boot' not in qcom
assert 'on property:vendor.recovery.adsp.ready=1\n    start health-hal-2-1\n    umount /firmware' in qcom
assert not (device/'recovery/root/twres/languages/zn_TW.xml').exists()
ET.parse(device/'recovery/root/twres/languages/zh_TW.xml')
assert '/dev/block/bootdevice/by-name/metadata' in (device/'recovery.fstab').read_text()
print(json.dumps(dict(passed=True,usb_transition_cases=transitions,mtp_and_adb_readiness_orders=2,
    actual_goodix_worker_irq_identity_and_24_concurrent_invocations=True,unblank_returns_before_delay_and_ignores_sleeping_display=True,
    actual_adsp_worker_online_failed_unknown_and_repeated_start_cases=True,traditional_chinese_filename_and_fstab=True,
    hardware_usb_touch_and_fastbootd_tested=False),indent=2))
