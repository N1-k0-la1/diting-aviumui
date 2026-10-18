# SPDX-License-Identifier: Apache-2.0
"""Exercise the actual installer with a mock fastboot and inert test assets."""
import hashlib,json,os,pathlib,shutil,subprocess,tempfile
root=pathlib.Path(__file__).resolve().parents[1]; results=[]
if os.name!='nt':raise SystemExit('Run installer regressions on Windows with PowerShell and .NET Framework.')
pwsh=shutil.which('pwsh') or str(pathlib.Path(os.environ['WINDIR'])/'System32/WindowsPowerShell/v1.0/powershell.exe')
with tempfile.TemporaryDirectory(prefix='review-installer-') as directory:
 d=pathlib.Path(directory); shutil.copyfile(root/'Install-Recovery.ps1',d/'Install-Recovery.ps1')
 assets=[]
 for name in ['rom.zip','boot.img','dtbo.img','vendor_boot.img','recovery.img','vbmeta.img','vbmeta_system.img']:
  path=d/'gms'/name; path.parent.mkdir(exist_ok=True); path.write_bytes(b'inert mock asset '+name.encode())
  assets.append({'flavour':'gms','path':'gms/'+name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
 (d/'MANIFEST.json').write_text(json.dumps({'candidates':[{'flavour':'gms','file':'gms/rom.zip'}],'assets':assets}))
 code='''using System;using System.IO;class Mock {static int Main(string[] args){
 if(args.Length==1&&args[0]=="--hold-pipe"){System.Threading.Thread.Sleep(9000);return 0;}
 string log=Environment.GetEnvironmentVariable("REVIEW_MOCK_FASTBOOT_LOG");
 string history=File.Exists(log)?File.ReadAllText(log):"";File.AppendAllText(log,String.Join("|",args)+"\\n");
 if(args.Length<4||args[0]!="-s"||args[1]!="fixture-serial")return 1;
 if(args[2]=="getvar") {string key=args[3];string value="";
 if(Environment.GetEnvironmentVariable("REVIEW_MOCK_EMPTY")==key){Console.Error.WriteLine("(bootloader) "+key+": \\r\\nFinished. Total time: 0.001s");return 0;}
 if(Environment.GetEnvironmentVariable("REVIEW_MOCK_HOLD")=="1"&&history.Length==0){
 var child=new System.Diagnostics.ProcessStartInfo(System.Reflection.Assembly.GetExecutingAssembly().Location,"--hold-pipe");child.UseShellExecute=false;child.CreateNoWindow=true;System.Diagnostics.Process.Start(child);}
 if(key=="product")value="diting";else if(key=="unlocked")value="yes";else if(key=="is-userspace")value="no";
 else if(key=="current-slot")value=Environment.GetEnvironmentVariable("REVIEW_MOCK_SLOT_CHANGE")=="1"&&history.Contains("flash|dtbo_a|")?"b":"a";
 else if(key.StartsWith("partition-size:"))value="0x100000";else if(key.StartsWith("partition-type:"))value="raw";else return 2;
 Console.Error.WriteLine("(bootloader) "+key+": "+value);return 0;}
 if(args[2]=="flash"||args[2]=="reboot") {Console.WriteLine("OKAY");return 0;}return 3;}}
'''
 cs=d/'Mock.cs'; cs.write_text(code); exe=d/'mock-fastboot.exe'
 csc=pathlib.Path(os.environ['WINDIR'])/'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
 subprocess.run([str(csc),'/nologo','/out:'+str(exe),str(cs)],check=True,capture_output=True)
 for name,flash,drift in [('read-only',False,False),('flash',True,False),('slot-drift',True,True),('nested-assets',False,False),('explicit-media-manifest',False,False),('empty-variable',True,False),('inherited-pipe',True,False),('missing-asset',False,False)]:
  (d/'MANIFEST.json').write_text(json.dumps({'candidates':[{'flavour':'gms','file':'gms/rom.zip'}],'assets':assets}))
  if name in ('nested-assets','missing-asset'):
   (d/'MANIFEST.json').write_text(json.dumps({'candidates':[{'flavour':'gms','file':'gms/rom.zip','assets':assets}]}))
  if name=='missing-asset':(d/'gms/boot.img').unlink()
  log=d/(name+'.log'); env=os.environ.copy();env['REVIEW_MOCK_FASTBOOT_LOG']=str(log);env['REVIEW_MOCK_SLOT_CHANGE']='1' if drift else '0'
  env['REVIEW_MOCK_EMPTY']='product' if name=='empty-variable' else ''
  env['REVIEW_MOCK_HOLD']='1' if name=='inherited-pipe' else '0'
  args=[pwsh,'-NoProfile','-File',str(d/'Install-Recovery.ps1'),'-Serial','fixture-serial','-FastbootPath',str(exe)]+(['-FlashRecovery'] if flash else [])
  if name=='explicit-media-manifest':
   (d/'CANDIDATES.json').write_text(json.dumps({'candidates':[{'flavour':'gms','file':'gms/rom.zip','assets':assets}]}))
   (d/'MANIFEST.json').write_text('{}');args+=['-ManifestPath','CANDIDATES.json']
  p=subprocess.run(args,env=env,capture_output=True,text=True,timeout=25)
  if name=='missing-asset':
   assert p.returncode!=0 and 'Missing required asset: gms/boot.img' in p.stderr and not log.exists(),p.stdout+p.stderr
   results.append({'case':name,'passed':True,'mock_writes':[]});continue
  if not log.exists(): raise RuntimeError(p.stdout+p.stderr)
  rows=[line.split('|')[2:] for line in log.read_text().splitlines()]
  writes=[row for row in rows if row[0] in ['flash','reboot','erase','format']]
  if name in ('empty-variable','inherited-pipe'):
   expected='Cannot parse Fastboot variable: product' if name=='empty-variable' else 'Fastboot output timed out'
   assert p.returncode!=0 and expected in p.stderr and not writes,p.stdout+p.stderr
   results.append({'case':name,'passed':True,'mock_writes':writes});continue
  if not flash: assert p.returncode==0 and writes==[]
  elif not drift:
   assert p.returncode==0 and [x[1] for x in writes if x[0]=='flash']==[n+'_a' for n in ['boot','dtbo','vendor_boot','recovery','vbmeta','vbmeta_system']]
   assert writes[-1]==['reboot','recovery'] and len(writes)==7
  else: assert p.returncode!=0 and [x[1] for x in writes]==['boot_a','dtbo_a']
  results.append({'case':name,'passed':True,'mock_writes':writes})
 print(json.dumps({'passed':True,'real_phone_used':False,'cases':results},indent=2))
