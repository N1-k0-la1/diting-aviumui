# SPDX-License-Identifier: Apache-2.0
"""Exercise the production system-flow predicate, including spoofing negative controls."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', type=Path)
root = parser.parse_args().source.resolve(strict=True)
text = (root / 'frameworks/base/services/core/java/com/android/server/wm/ActivityStartInterceptor.java').read_text()
match = re.search(r'    static boolean isSystemLaunchFlow\([^;{]+\)\s*\{', text)
assert match
end = match.end()
depth = 1
while depth:
    depth += (text[end] == '{') - (text[end] == '}')
    end += 1
method = text[match.start():end]
fixture = '''
public class ResolverApproval {
 static class ApplicationInfo {boolean system; boolean isSystemApp(){return system;}}
 static class ActivityInfo {ApplicationInfo applicationInfo=new ApplicationInfo();String packageName,name;}
 static int assertions;
 static void check(boolean value){assertions++;if(!value)throw new AssertionError("case "+assertions);}
 static ActivityInfo info(String pkg,String cls,boolean system){ActivityInfo i=new ActivityInfo();i.packageName=pkg;i.name=cls;i.applicationInfo.system=system;return i;}
''' + method + '''
 public static void main(String[] args){
  String resolver="com.android.internal.app.ResolverActivity";
  check(isSystemLaunchFlow(info("android",resolver,true),null,true));
  check(!isSystemLaunchFlow(info("android",resolver,true),null,false));
  check(!isSystemLaunchFlow(info("android",resolver,false),null,true));
  check(!isSystemLaunchFlow(info("untrusted",resolver,true),null,true));
  check(!isSystemLaunchFlow(info("android","ordinary.Activity",true),null,true));
  check(!isSystemLaunchFlow(info("android",null,true),null,true));
  check(!isSystemLaunchFlow(info(null,resolver,true),null,true));
  check(!isSystemLaunchFlow(null,null,true));
  ActivityInfo missing=info("android",resolver,true);missing.applicationInfo=null;
  check(!isSystemLaunchFlow(missing,null,true));
  for(String pkg:new String[]{"com.android.packageinstaller","com.google.android.packageinstaller","com.android.documentsui","com.android.settings","com.android.systemui"}){
   check(isSystemLaunchFlow(info(pkg,"Activity",true),null,true));
   check(!isSystemLaunchFlow(info(pkg,"Activity",true),null,false));
   check(!isSystemLaunchFlow(info(pkg,"Activity",false),null,true));
  }
  check(isSystemLaunchFlow(info("configured.controller","Activity",true),"configured.controller",false));
  check(!isSystemLaunchFlow(info("configured.controller","Activity",false),"configured.controller",true));
  for(String pkg:new String[]{"com.tencent.mobileqq","fork.risin42.nagramx","com.android.chrome","com.example.camera"}){
   check(!isSystemLaunchFlow(info(pkg,"Activity",false),null,false));
   check(!isSystemLaunchFlow(info(pkg,"Activity",true),null,true));
  }
  System.out.println(assertions);
 }
}
'''
jdk = root / 'prebuilts/jdk/jdk21/linux-x86/bin'
with tempfile.TemporaryDirectory(prefix='resolver-approval-') as temporary:
    folder = Path(temporary)
    def execute(code, expected):
        source = folder / 'ResolverApproval.java'
        source.write_text(code)
        subprocess.run([str(jdk/'javac'), str(source)], check=True, capture_output=True)
        result = subprocess.run([str(jdk/'java'), '-cp', str(folder), 'ResolverApproval'], capture_output=True, text=True)
        assert (result.returncode == 0) == expected, result.stderr
        return result.stdout.strip()
    count = int(execute(fixture, True))
    old = fixture.replace('if ("android".equals(pkg)\n                && "com.android.internal.app.ResolverActivity".equals(target.name)) return true;', '')
    assert old != fixture
    execute(old, False)
    unguarded = fixture.replace('if (!platformSigned) return false;', '')
    execute(unguarded, False)
    broad = fixture.replace('if ("android".equals(pkg)\n                && "com.android.internal.app.ResolverActivity".equals(target.name)) return true;', 'if ("android".equals(pkg)) return true;')
    execute(broad, False)
print(json.dumps(dict(passed=True, assertions=count, extracted_production_method=True,
                     negative_controls_rejected=3, phone_test_separate=True)))
