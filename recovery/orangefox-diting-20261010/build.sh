#!/bin/bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 N1-k0-la1
set -eo pipefail
bundle=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
source_tree=${1:?Pass the synchronized OrangeFox source directory}
python3 "$bundle/apply-source.py" "$source_tree" --verify-applied
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
