#!/bin/bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 N1-k0-la1
set -eo pipefail
bundle=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
source_tree=${1:?Pass the synchronized OrangeFox source directory}
python3 "$bundle/apply-source.py" "$source_tree" --verify-applied
# Incremental builds can retain the old, misspelled device language overlay.
# Delete only that known generated file; refuse symlinks or unexpected content.
python3 - "$source_tree" <<'PY'
import hashlib,pathlib,sys
root=pathlib.Path(sys.argv[1]).resolve()
file=root/'out/target/product/diting/recovery/root/twres/languages/zn_TW.xml'
if file.exists() or file.is_symlink():
    if file.is_symlink() or not file.is_file() or not file.resolve().is_relative_to(root/'out'):
        raise RuntimeError('Unsafe obsolete language staging path')
    if hashlib.sha256(file.read_bytes()).hexdigest() != '4d95b25dc04979238f53184cb658ffee9d5795b63cbdcecef9264e65cc1ae587':
        raise RuntimeError('Unexpected obsolete language staging content')
    file.unlink()
PY
cd -- "$source_tree"
export FOX_BUILD_DEVICE=diting
export USE_CCACHE=1 CCACHE_EXEC=/usr/bin/ccache CCACHE_DIR="$PWD/out/ccache"
mkdir -p "$CCACHE_DIR"
export GOGC=50 GOMEMLIMIT=18GiB
unset ALLOW_MISSING_DEPENDENCIES
source build/envsetup.sh
lunch twrp_diting-bp2a-eng
m recoveryimage -j"${JOBS:-4}"
sha256sum out/target/product/diting/recovery.img
