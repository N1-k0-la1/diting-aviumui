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
    root = root.resolve()
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
    parser.add_argument('--media-input-dir', required=True, type=pathlib.Path,
                        help='Prepared exact media ELF inputs; see prepare-media-inputs.py')
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    series = json.loads((PACKAGE / 'patch-series.json').read_text())
    artifacts = json.loads((PACKAGE / 'external-artifacts.json').read_text())
    via = artifacts['via']
    media = artifacts['media']['files']
    inputs = args.media_input_dir.resolve(strict=True)
    marker = source / '.patch-application-in-progress'
    if marker.exists():
        raise RuntimeError('Previous application exists; inspect manually or use a fresh checkout.')
    if digest(args.via_apk) != via['sha256']:
        raise RuntimeError('Via APK SHA256 differs from the verified official 7.3.3 artifact.')
    for item in media:
        supplied = contained(inputs, item['project']+'/'+item['path'])
        if digest(supplied) != item['sha256']:
            raise RuntimeError(f'Media input SHA256 mismatch: {item["path"]}')
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
    # Ignored files do not appear in git status. Reject every external-file
    # collision before staging any patches or creating the application marker.
    via_project = contained(source, via['project'])
    via_destination = contained(via_project, via['path'])
    # The pinned upstream APK is intentionally replaced. An unrelated ignored
    # file or a directory must never be overwritten as a side effect.
    if via_destination.exists():
        if not via_destination.is_file() or not git(via_project, 'ls-files', '--', via['path']):
            raise RuntimeError('Unexpected existing Via input')
    if not via_destination.parent.is_dir():
        raise RuntimeError('Via destination parent is not a directory')
    for item in media:
        destination = contained(contained(source, item['project']), item['path'])
        if destination.exists() or destination.is_symlink():
            raise RuntimeError(f'Unexpected existing media input: {item["path"]}')
        for parent in destination.parents:
            if parent == source:
                break
            if parent.exists() and not parent.is_dir():
                raise RuntimeError(f'Media destination parent is not a directory: {parent}')
    marker.write_text('Patches are applied in place. Inspect this marker after any interruption.\n')
    for index, item in enumerate(series['patches'], 1):
        project = contained(source, item['project'])
        patch = contained(PACKAGE, item['patch'])
        print(f'[{index}/{len(series["patches"])}] {item["project"]}: {item["patch"]}', flush=True)
        subprocess.run(['git', '-C', str(project), 'apply', '--check', '--index', str(patch)], check=True)
        subprocess.run(['git', '-C', str(project), 'apply', '--index', str(patch)], check=True)
    via_project = contained(source, via['project'])
    destination = contained(via_project, via['path'])
    shutil.copyfile(args.via_apk, destination)
    if digest(destination) != via['sha256']:
        raise RuntimeError('Via copied artifact checksum mismatch.')
    subprocess.run(['git', '-C', str(via_project), 'add', '--', via['path']], check=True)
    for item in media:
        supplied = contained(inputs, item['project']+'/'+item['path'])
        project = contained(source, item['project'])
        destination = contained(project, item['path'])
        if destination.exists():
            raise RuntimeError(f'Unexpected existing media input: {item["path"]}')
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(supplied, destination)
        destination.chmod(0o755 if item['mode'] == '100755' else 0o644)
        if digest(destination) != item['sha256']:
            raise RuntimeError(f'Copied media input mismatch: {item["path"]}')
        subprocess.run(['git', '-C', str(project), 'add', '--', item['path']], check=True)
    marker.write_text('Patch application complete. Changes are staged, not committed.\n')
    print('All source patches, exact media inputs and Via APK applied. Build/sign/phone validation remain.')

if __name__ == '__main__':
    main()
