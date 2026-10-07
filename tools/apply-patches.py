# SPDX-License-Identifier: Apache-2.0
"""Apply the audited series once to a fresh checkout; no resets or downloads."""
import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess

PACKAGE = pathlib.Path(__file__).resolve().parents[1]

def contained(root, relative):
    result = (root / relative).resolve()
    if not result.is_relative_to(root) or result == root:
        raise RuntimeError(f'Path outside expected directory: {relative}')
    return result

def git(project, *args):
    return subprocess.check_output(['git', '-C', str(project), *args], text=True).strip()

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest() if hasattr(hashlib, 'file_digest') else hashlib.sha256(stream.read()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=pathlib.Path)
    parser.add_argument('--via-apk', required=True, type=pathlib.Path)
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    series = json.loads((PACKAGE / 'patch-series.json').read_text())
    via = json.loads((PACKAGE / 'external-artifacts.json').read_text())['via']
    marker = source / '.patch-application-in-progress'
    if marker.exists():
        raise RuntimeError('Previous application exists; inspect manually or use a fresh checkout.')
    if digest(args.via_apk) != via['sha256']:
        raise RuntimeError('Via APK SHA256 differs from the verified official 7.3.3 artifact.')
    for item in series['patches']:
        patch = contained(PACKAGE, item['patch'])
        if digest(patch) != item['sha256']:
            raise RuntimeError(f'Patch checksum mismatch: {item["patch"]}')
    for name, expected in series['upstream_bases'].items():
        project = contained(source, name)
        if git(project, 'rev-parse', 'HEAD') != expected:
            raise RuntimeError(f'Wrong upstream HEAD: {name}')
        if git(project, 'status', '--porcelain'):
            raise RuntimeError(f'Checkout is not clean: {name}')
    marker.write_text('Patches are applied in place. Inspect this marker after any interruption.\n')
    for index, item in enumerate(series['patches'], 1):
        project = contained(source, item['project'])
        patch = contained(PACKAGE, item['patch'])
        print(f'[{index}/{len(series["patches"])}] {item["project"]}: {item["patch"]}', flush=True)
        subprocess.run(['git', '-C', str(project), 'apply', '--check', '--index', str(patch)], check=True)
        subprocess.run(['git', '-C', str(project), 'apply', '--index', str(patch)], check=True)
    destination = contained(contained(source, via['project']), via['path'])
    shutil.copyfile(args.via_apk, destination)
    if digest(destination) != via['sha256']:
        raise RuntimeError('Via copied artifact checksum mismatch.')
    subprocess.run(['git', '-C', str(destination.parent), 'add', '--', destination.name], check=True)
    marker.write_text('Patch application complete. Changes are staged, not committed.\n')
    print('All source patches and the exact Via APK applied. Build/sign/phone validation remain.')

if __name__ == '__main__':
    main()
