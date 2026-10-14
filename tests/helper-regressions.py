"""Regression checks using real helper scripts and extracted production functions."""
import hashlib, importlib.util, json, os, pathlib, re, shutil, subprocess, sys, tempfile
from unittest.mock import patch

PUBLIC = pathlib.Path(__file__).resolve().parents[1]
checks = []
def run(*args, cwd=None):
    return subprocess.check_output(args, cwd=cwd, stderr=subprocess.STDOUT, text=True).strip()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(file):
    spec=importlib.util.spec_from_file_location(file.stem,file); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def expect_error(fn, text):
    try: fn()
    except RuntimeError as e:
        if text not in str(e): raise
    else: raise RuntimeError('Expected rejection: '+text)
    checks.append(text)
def repo(p):
    p.mkdir(parents=True); run('git','init','-q',str(p)); (p/'.gitignore').write_text('lib\n')
    run('git','-C',str(p),'add','.gitignore'); run('git','-C',str(p),'-c','user.name=Fixture','-c','user.email=fixture@localhost','commit','-qm','fixture')
    return run('git','-C',str(p),'rev-parse','HEAD')
def function(text,name):
    match=re.search(r'^[^\n]*\b'+re.escape(name)+r'\([^;{]*\)\s*\{',text,re.M)
    if not match: raise RuntimeError('Missing definition '+name)
    start=match.start(); opening=match.end()-1; depth=1; pos=opening+1
    while depth:
        depth += (text[pos]=='{')-(text[pos]=='}'); pos+=1
    return text[start:pos]

with tempfile.TemporaryDirectory(prefix='review-regression-') as directory:
    d=pathlib.Path(directory); source=d/'src'; head=repo(source/'project'); inputs=d/'inputs'; inputs.mkdir()
    m=load(PUBLIC/'tools/apply-patches.py'); package=d/'package'; package.mkdir(); m.PACKAGE=package
    link=d/'alias'; link.symlink_to(source,target_is_directory=True)
    assert m.contained(link,'project') == source/'project'
    expect_error(lambda:m.contained(link,'../outside'),'Path outside')
    checks.append('resolved symlink root accepted')
    via=d/'via.apk'; via.write_bytes(b'fixture')
    supplied=inputs/'project/lib/test.so'; supplied.parent.mkdir(parents=True); supplied.write_bytes(b'media')
    item={'project':'project','path':'lib/test.so','sha256':sha(supplied),'mode':'100644'}
    (package/'patch-series.json').write_text(json.dumps({'patches':[],'upstream_bases':{'project':head}}))
    (package/'external-artifacts.json').write_text(json.dumps({'via':{'project':'project','path':'via.apk','sha256':sha(via)},'media':{'files':[item]}}))
    collision=source/'project/lib/test.so'; collision.parent.mkdir(); collision.write_bytes(b'existing ignored')
    argv=['test',str(source),'--via-apk',str(via),'--media-input-dir',str(inputs)]
    with patch.object(sys,'argv',argv): expect_error(m.main,'Unexpected existing media input')
    assert not (source/'.patch-application-in-progress').exists() and not (source/'project/via.apk').exists()
    assert run('git','-C',str(source/'project'),'status','--porcelain')==''
    collision.unlink(); collision.parent.rmdir(); collision.parent.write_bytes(b'not a directory')
    with patch.object(sys,'argv',argv): expect_error(m.main,'not a directory')
    assert not (source/'.patch-application-in-progress').exists()
    checks.append('collision preflight left source and marker unchanged')

    prep=load(PUBLIC/'tools/prepare-media-inputs.py'); prep.PACKAGE=package
    donor=d/'donor'; donor.mkdir(); (donor/'a').write_bytes(b'a'); (donor/'b').write_bytes(b'b')
    donoritems=[{'project':'project','path':'lhdc/'+n,'source_path':n,'sha256':sha(donor/n),'revision':'pin','mode':'100644'} for n in ['a','b']]
    (package/'external-artifacts.json').write_text(json.dumps({'media':{'files':donoritems}}))
    argv=['test','--lhdc-checkout',str(donor),'--dolby-checkout',str(donor),'--output',str(d/'prepared')]
    with patch.object(sys,'argv',argv),patch.object(prep.subprocess,'check_output',return_value='pin\n') as mocked: prep.main(); assert mocked.call_count==1
    checks.append('donor HEAD checked once for two inputs')
    donoritems[1]['path']='unknown/b'; (package/'external-artifacts.json').write_text(json.dumps({'media':{'files':donoritems}})); argv[-1]=str(d/'unknown-output')
    with patch.object(sys,'argv',argv),patch.object(prep.subprocess,'check_output',return_value='pin\n'): expect_error(prep.main,'Unknown media input family')
    assert not (d/'unknown-output').exists()

    for bundle in ['orangefox-diting-20261010','orangefox-diting-20261010-bootctrl']:
        b=d/bundle; b.mkdir(); shutil.copyfile(PUBLIC/'recovery'/bundle/'apply-source.py',b/'apply-source.py')
        manifest=b/'manifest.xml'; manifest.write_text('<manifest/>')
        for optimize in [False,True]:
            (b/'SOURCE.json').write_text(json.dumps({'manifest_sha256':'wrong','projects':[]}))
            args=[sys.executable]+(['-O'] if optimize else [])+[str(b/'apply-source.py'),str(source)]
            result=subprocess.run(args,capture_output=True,text=True); assert result.returncode and 'manifest hash mismatch' in result.stderr
            checks.append(bundle+': bad manifest rejected '+('optimized' if optimize else 'normal'))
        (b/'p.patch').write_text('wrong patch')
        record={'manifest_sha256':sha(manifest),'projects':[{'path':'project','patch':'p.patch','patch_sha256':'wrong','upstream_commit':head}]}
        (b/'SOURCE.json').write_text(json.dumps(record)); result=subprocess.run([sys.executable,'-O',str(b/'apply-source.py'),str(source)],capture_output=True,text=True)
        assert result.returncode and 'patch hash mismatch' in result.stderr
        record['projects'][0]['patch_sha256']=sha(b/'p.patch'); (b/'SOURCE.json').write_text(json.dumps(record)); (source/'project/dirty').write_text('dirty')
        result=subprocess.run([sys.executable,'-O',str(b/'apply-source.py'),str(source)],capture_output=True,text=True); assert result.returncode and "RuntimeError: project" in result.stderr
        (source/'project/dirty').unlink(); checks.append(bundle+': bad patch and dirty tree rejected optimized')


    # Via replaces a tracked upstream APK, but must reject an ignored collision.
    collision.parent.unlink()
    via_target=source/'project/lib'
    via_target.write_bytes(b'ignored unrelated input')
    (package/'external-artifacts.json').write_text(json.dumps({'via':{'project':'project','path':'lib','sha256':sha(via)},'media':{'files':[]}}))
    argv=['test',str(source),'--via-apk',str(via),'--media-input-dir',str(inputs)]
    with patch.object(sys,'argv',argv): expect_error(m.main,'Unexpected existing Via input')
    assert via_target.read_bytes()==b'ignored unrelated input'
    assert not (source/'.patch-application-in-progress').exists()
    run('git','-C',str(source/'project'),'add','-f','lib')
    run('git','-C',str(source/'project'),'-c','user.name=Fixture','-c','user.email=fixture@localhost','commit','-qm','upstream APK fixture')
    newhead=run('git','-C',str(source/'project'),'rev-parse','HEAD')
    (package/'patch-series.json').write_text(json.dumps({'patches':[],'upstream_bases':{'project':newhead}}))
    with patch.object(sys,'argv',argv): m.main()
    assert via_target.read_bytes()==via.read_bytes()
    checks.append('tracked upstream Via replacement remains supported')
print(json.dumps({'passed':len(checks),'checks':checks},indent=2))
