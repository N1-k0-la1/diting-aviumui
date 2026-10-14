# SPDX-License-Identifier: Apache-2.0
"""Prepare SHA256-checked media inputs from the two pinned donor checkouts; no downloads."""
import argparse, hashlib, json, pathlib, shutil, subprocess

PACKAGE = pathlib.Path(__file__).resolve().parents[1]
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def contained(root, relative):
    root = root.resolve()
    p = (root/relative).resolve()
    if not p.is_relative_to(root) or p == root: raise RuntimeError(relative)
    return p

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lhdc-checkout', required=True, type=pathlib.Path)
    parser.add_argument('--dolby-checkout', required=True, type=pathlib.Path)
    parser.add_argument('--output', required=True, type=pathlib.Path)
    args = parser.parse_args()
    files = json.loads((PACKAGE/'external-artifacts.json').read_text())['media']['files']
    output = args.output.resolve()
    if output.exists(): raise RuntimeError('Output already exists; use a new directory.')
    prepared = []
    checkout_heads = {}
    for item in files:
        if item['path'].startswith('lhdc/'):
            checkout = args.lhdc_checkout.resolve(strict=True)
        elif item['path'].startswith('dolby-vision/'):
            checkout = args.dolby_checkout.resolve(strict=True)
        else:
            raise RuntimeError('Unknown media input family: '+item['path'])
        if checkout not in checkout_heads:
            checkout_heads[checkout] = subprocess.check_output(['git','-C',str(checkout),'rev-parse','HEAD'],text=True).strip()
        head = checkout_heads[checkout]
        if head != item['revision']: raise RuntimeError('Donor checkout revision differs: '+item['path'])
        supplied = contained(checkout,item['source_path'])
        if digest(supplied) != item['sha256']: raise RuntimeError('Donor input hash differs: '+item['path'])
        prepared.append((item,supplied))
    for item,supplied in prepared:
        destination = contained(output,item['project']+'/'+item['path'])
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(supplied,destination)
        destination.chmod(0o755 if item['mode']=='100755' else 0o644)
    print('Prepared',len(files),'exact media ELF inputs. No signing material is included.')

if __name__ == '__main__': main()
