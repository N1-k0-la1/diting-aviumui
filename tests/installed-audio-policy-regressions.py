# SPDX-License-Identifier: Apache-2.0
"""Run the native probe on the build-installed SKU policy, merging installed XIncludes."""
import argparse,hashlib,json,pathlib,subprocess,tempfile,xml.etree.ElementTree as ET
from xml.etree import ElementInclude
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('source',type=pathlib.Path)
parser.add_argument('--adb',default='adb');parser.add_argument('--serial',required=True)
parser.add_argument('--report',type=pathlib.Path)
args=parser.parse_args();source=args.source.resolve(strict=True)
out=source/'out/target/product/diting';vendor=out/'vendor';device=source/'device/xiaomi/sm8450-common'
def adb(*a):return subprocess.run([args.adb,'-s',args.serial,*a],capture_output=True,text=True,encoding='utf-8',errors='replace',check=True).stdout
def hostpath(path):
 return subprocess.check_output(['wslpath','-w',str(path)],text=True).strip() if args.adb.endswith('.exe') else str(path)
sku=adb('shell','getprop','ro.boot.product.vendor.sku').strip()
if sku not in ('taro','diwali','cape','ukee','parrot'):raise RuntimeError('Unexpected vendor SKU')
inputs={}
def loader(href,parse,encoding=None):
 if not href.startswith('/vendor/etc/'):raise RuntimeError('Unexpected include '+href)
 file=vendor/href.removeprefix('/vendor/')
 data=file.read_bytes();inputs[href]=hashlib.sha256(data).hexdigest()
 return ET.fromstring(data) if parse=='xml' else data.decode(encoding or 'utf-8')
policies=[]
for name in ('taro','diwali','cape','ukee','parrot'):
 file=vendor/f'etc/audio/sku_{name}/audio_policy_configuration.xml'
 assert file.read_bytes()==(device/'audio/audio_policy_configuration.xml').read_bytes()
 policies.append(file)
fragment=vendor/'etc/bluetooth_lhdc_audio_policy_configuration.xml'
assert fragment.read_bytes()==(device/'audio/bluetooth_lhdc_audio_policy_configuration.xml').read_bytes()
policy=vendor/f'etc/audio/sku_{sku}/audio_policy_configuration.xml'
tree=ET.parse(policy);ElementInclude.include(tree.getroot(),loader=loader)
assert any(m.get('name')=='bluetooth' for m in tree.findall('modules/module'))
remote='/data/local/tmp/diting-round2-policy'
probe=out/'system/bin/diting_lhdc_policy_probe'
with tempfile.TemporaryDirectory(prefix='installed-policy-') as tmp:
 merged=pathlib.Path(tmp)/'installed-merged.xml';tree.write(merged,encoding='utf-8',xml_declaration=True)
 adb('shell','mkdir','-p',remote);adb('push',hostpath(probe),remote+'/probe')
 adb('push',hostpath(merged),remote+'/installed-merged.xml');adb('shell','chmod','755',remote+'/probe')
 result=adb('shell',remote+'/probe',remote+'/installed-merged.xml','bluetooth')
 assert result.count('PASS')==19,result
 report={'passed':True,'vendor_sku':sku,'five_sku_installed_copies_match_source':True,
 'installed_policy_sha256':hashlib.sha256(policy.read_bytes()).hexdigest(),
 'installed_include_sha256':inputs,'merged_xml_sha256':hashlib.sha256(merged.read_bytes()).hexdigest(),
 'probe_sha256':hashlib.sha256(probe.read_bytes()).hexdigest(),'native_output':result,
 'policy_source':'build-installed vendor policy; XIncludes expanded from installed files',
 'phone_policy_or_settings_modified':False,'headset_playback_verified':False}
 if args.report:args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(report,indent=2))
