# SPDX-License-Identifier: Apache-2.0
"""Compile the production global font mapper and check native rendering in a temporary device process."""
import argparse, hashlib, json, pathlib, shlex, subprocess, tempfile, uuid

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('source',type=pathlib.Path)
parser.add_argument('--adb',type=pathlib.Path,required=True)
parser.add_argument('--serial',required=True)
parser.add_argument('--font',default='/sdcard/FZYaSongS-R-GB.ttf',help='Existing readable non-stock font; never installed by this test')
args=parser.parse_args();source=args.source.resolve(strict=True);adb=args.adb.resolve(strict=True)

def run(command):
    result=subprocess.run([str(a) for a in command],capture_output=True,text=True)
    if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    return result.stdout

prefix=[adb,'-s',args.serial]
assert int(run(prefix+['shell','getprop','ro.build.version.sdk']).strip())>=36
framework=source/'out/soong/.intermediates/frameworks/base/framework-minus-apex/android_common/combined/framework.jar'
sdk=source/'prebuilts/sdk/36/public/android.jar';jdk=source/'prebuilts/jdk/jdk21/linux-x86/bin'
helper=source/'frameworks/base/services/core/java/com/android/server/graphics/fonts/GlobalFontConfig.java'
probe=pathlib.Path(__file__).with_name('GlobalFontDeviceProbe.java')
with tempfile.TemporaryDirectory(prefix='global-font-') as temporary:
    root=pathlib.Path(temporary);classes=root/'classes';classes.mkdir();dex=root/'dex';dex.mkdir()
    stub=root/'UserCustomFontStore.java'
    stub.write_text('package com.android.server.graphics.fonts; final class UserCustomFontStore {static final String FAMILY="diting-user-custom";}')
    run([jdk/'javac','-source','17','-target','17','-cp',str(framework)+':'+str(sdk),'-d',classes,helper,probe,stub])
    run([jdk/'java','-cp',source/'prebuilts/r8/r8.jar','com.android.tools.r8.D8','--min-api','36',
         '--lib',sdk,'--classpath',framework,'--output',dex,*classes.rglob('*.class')])
    jar=root/'probe.jar';run([jdk/'jar','cf',jar,'-C',dex,'classes.dex'])
    # Windows adb.exe needs a Windows source path even when invoked from WSL.
    local=run(['wslpath','-w',jar]).strip() if adb.suffix.lower()=='.exe' else str(jar)
    remote='/data/local/tmp/global-font-test-'+uuid.uuid4().hex+'.jar'
    run(prefix+['push',local,remote])
    try:
        digest=hashlib.sha256(jar.read_bytes()).hexdigest()
        assert run(prefix+['shell','sha256sum',remote]).split()[0]==digest
        command='CLASSPATH='+shlex.quote(remote)+' app_process /system/bin com.android.server.graphics.fonts.GlobalFontDeviceProbe '+shlex.quote(args.font)
        output=run(prefix+['shell','su','-c',command])
        result=json.loads(output.strip());assert result['passed'] and not result['system_font_state_modified']
        result['production_source_sha256']=hashlib.sha256(helper.read_bytes()).hexdigest()
        print(json.dumps(result,indent=2))
    finally:
        # Only this invocation's uniquely named jar; no app/font data is removed.
        run(prefix+['shell','rm',remote])
