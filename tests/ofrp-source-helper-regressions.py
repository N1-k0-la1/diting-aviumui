#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Exercise the review1 source helper against isolated Git projects, never a phone."""
import hashlib,json,pathlib,shutil,subprocess,sys,tempfile
PUBLIC=pathlib.Path(__file__).resolve().parents[1]
def run(*cmd):return subprocess.check_output(cmd,stderr=subprocess.STDOUT).decode().strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
with tempfile.TemporaryDirectory(prefix='ofrp-source-helper-') as tmp:
    root=pathlib.Path(tmp);source=root/'source';project=source/'project';project.mkdir(parents=True)
    run('git','init','-q',str(project))
    run('git','-C',str(project),'config','user.name','Fixture')
    run('git','-C',str(project),'config','user.email','fixture@localhost')
    old=project/'old.txt';old.write_text('old\n')
    run('git','-C',str(project),'add','old.txt');run('git','-C',str(project),'commit','-qm','baseline')
    head=run('git','-C',str(project),'rev-parse','HEAD')
    bundle=root/'bundle';bundle.mkdir()
    shutil.copyfile(PUBLIC/'recovery/orangefox-diting-20261015-review1/apply-source.py',bundle/'apply-source.py')
    for name in ('manifest.xml','built-manifest.xml'):(bundle/name).write_text('<manifest/>')
    old.unlink();new=project/'run.sh';new.write_text('#!/bin/sh\nexit 0\n');new.chmod(0o755)
    run('git','-C',str(project),'add','-A')
    patch=bundle/'device.patch';patch.write_bytes(subprocess.check_output(['git','-C',str(project),'diff','--cached','--binary',head]))
    record=dict(manifest_sha256=sha(bundle/'manifest.xml'),built_manifest_sha256=sha(bundle/'built-manifest.xml'),projects=[dict(path='project',upstream_commit=head,local_build_commit=head,patch='device.patch',patch_sha256=sha(patch),changed_files=[dict(path='run.sh',sha256=sha(new),git_mode='100755')],deleted_files=['old.txt'])])
    manifest=bundle/'SOURCE.json'
    def save():manifest.write_text(json.dumps(record))
    def check(expected=None,verify=True,optimize=False):
        result=subprocess.run([sys.executable]+(['-O'] if optimize else [])+[str(bundle/'apply-source.py'),str(source)]+(['--verify-applied'] if verify else []),capture_output=True,text=True)
        if expected:assert result.returncode and expected in result.stderr,result.stdout+result.stderr
        else:assert result.returncode==0,result.stdout+result.stderr
        checks.append(expected or ('applied verification' if verify else 'clean apply'))
    save()
    # Exercise staged deletion/addition, executable bits and optimized Python.
    for optimize in (False,True):
        check(optimize=optimize)
        old.write_text('unexpected restored old file\n');check('Deleted source still present',optimize=optimize);old.unlink()
        new.chmod(0o644);check('Executable mode mismatch',optimize=optimize);new.chmod(0o755)
    target=root/'target';target.write_bytes(new.read_bytes());target.chmod(0o755)
    new.unlink();new.symlink_to(target);check('Symlink in source path');new.unlink();new.write_bytes(target.read_bytes());new.chmod(0o755)
    old.symlink_to(root/'missing');check('Symlink in source path');old.unlink()
    extra=project/'extra';extra.write_text('extra');check('Unrelated change');extra.unlink()
    (bundle/'built-manifest.xml').write_text('changed');check('built manifest hash mismatch');(bundle/'built-manifest.xml').write_text('<manifest/>')
    record['projects'][0]['changed_files'][0]['path']='../target';save();check('Invalid source path')
    record['projects'][0]['changed_files'][0]['path']='run.sh';save()
    run('git','-C',str(project),'reset','--hard',head)
    check(verify=False,optimize=True);check(optimize=True)
print(json.dumps(dict(passed=len(checks),checks=checks),indent=2))
