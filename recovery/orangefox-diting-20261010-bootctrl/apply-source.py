#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 N1-k0-la1
"""Validate pinned sources, then apply the two recovery patches, or verify applied inputs."""
import argparse, hashlib, json, pathlib, subprocess, xml.etree.ElementTree as ET

BUNDLE = pathlib.Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', type=pathlib.Path)
parser.add_argument('--verify-applied', action='store_true')
args = parser.parse_args()
source = args.source.resolve()
record = json.loads((BUNDLE / 'SOURCE.json').read_text())

def git(folder, *command):
    return subprocess.check_output(['git', '-C', str(folder), *command], stderr=subprocess.PIPE)

def sha(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()

assert sha(BUNDLE / 'manifest.xml') == record['manifest_sha256']
changed_projects = {p['path']: p for p in record['projects']}
for project in ET.parse(BUNDLE / 'manifest.xml').getroot().findall('project'):
    relative = project.get('path', project.get('name'))
    folder = source / relative
    head = git(folder, 'rev-parse', 'HEAD').decode().strip()
    if relative not in changed_projects:
        assert head == project.attrib['revision'], ('Unexpected upstream revision', relative, head)
        assert not git(folder, 'status', '--porcelain').strip(), ('Dirty upstream source', relative)

# Check both projects and all patch inputs before the first mutation.
for project in record['projects']:
    folder = source / project['path']
    assert sha(BUNDLE / project['patch']) == project['patch_sha256']
    head = git(folder, 'rev-parse', 'HEAD').decode().strip()
    if args.verify_applied:
        assert head in (project['upstream_commit'], project['local_build_commit']), (project['path'], head)
        allowed = {p['path'] for p in project['changed_files']}
        for entry in git(folder, 'status', '--porcelain', '-z', '--untracked-files=all').decode().split('\0'):
            if entry:
                assert entry[3:] in allowed, ('Unrelated change', project['path'], entry)
        for item in project['changed_files']:
            file = folder / item['path']
            assert (sha(file) if file.is_file() else None) == item['sha256'], (project['path'], item['path'])
    else:
        assert head == project['upstream_commit'], (project['path'], head)
        assert not git(folder, 'status', '--porcelain').strip(), project['path']
        git(folder, 'apply', '--check', str(BUNDLE / project['patch']))

if not args.verify_applied:
    for project in record['projects']:
        folder = source / project['path']
        git(folder, 'apply', str(BUNDLE / project['patch']))
        for item in project['changed_files']:
            file = folder / item['path']
            assert (sha(file) if file.is_file() else None) == item['sha256'], (project['path'], item['path'])
print('Pinned recovery source inputs verified.' if args.verify_applied else 'Both patches applied and exact changed-file hashes verified.')
