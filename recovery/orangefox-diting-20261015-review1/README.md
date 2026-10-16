# OrangeFox diting / ditingp review1 source

This is the source for the review1 testing candidate, not a new hardware-qualified release.
The previous tested image and its source stay in [the historical bundle](../orangefox-diting-20261010-bootctrl/README.md).
See the [review and validation scope](../../OFRP-REVIEW-20261015.md) for every fix.
No new boot, decryption, USB, touch, fastbootd or OTA installation result is inferred from that older image.

## Contents and provenance

- OrangeFox fox_16.0 manifest at `4c65ca28fa67580172ee6bf99892a054c19dcebe`, with 405 pinned projects.
- Device upstream `1a1b5d3f6c908145e360da990a70b41042929615`, plus cumulative `device.patch`.
- Recovery upstream `0f7831d3240f4c3925a0b5fd7d2c907ddf8704c2`, plus cumulative `recovery.patch`.
- `SOURCE.json` records the exact modified project commits, file hashes, Git modes, deletions and image identity.
- `built-manifest.xml` records those two modified source revisions; `manifest.xml` retains upstream pins.
- `SOURCE-VALIDATION.json` records exact Git-tree reconstruction from local upstream objects.
- `HOST-TESTS.json` and `IMAGE-AUDIT.json` separate host checks from hardware qualification.

The candidate retains the prior boot-control shim, OTA verification certificate and storage decryption adaptations.
It has no standalone kernel and requires compatible boot/vendor_boot. Encrypted backups are compiled out;
this is separate from FBE storage decryption. No private signing keys or phone account data are included.

## Reproduce on Linux / WSL ext4

Use the [OrangeFox build dependencies](https://wiki.orangefox.tech/dev/building), native Linux permissions,
and adequate space for the pinned platform sources and toolchain. Replace the bundle path below.
Use a clean checkout of the upstream revisions: these patches already include the previous customizations.
Do not apply them over either historical bundle.

```bash
bundle=/path/to/diting-aviumui/recovery/orangefox-diting-20261015-review1
mkdir -p "$HOME/orangefox-diting-review1"
cd "$HOME/orangefox-diting-review1"
repo init -u https://gitlab.com/OrangeFox/Manifest.git \
  -b 4c65ca28fa67580172ee6bf99892a054c19dcebe --depth=1 --no-clone-bundle
cp "$bundle/manifest.xml" .repo/manifests/diting-review1.xml
repo init -m diting-review1.xml
repo sync -c -j4 --no-clone-bundle --no-tags --fail-fast
git clone https://github.com/AviderMin/ofrp_device_xiaomi_diting device/xiaomi/diting
git -C device/xiaomi/diting checkout --detach 1a1b5d3f6c908145e360da990a70b41042929615
python3 "$bundle/apply-source.py" "$PWD"
g++ -std=c++17 -Wall -Wextra -Werror -fsanitize=address,undefined \
  -I bootable/recovery "$bundle/test-diting-ota-aliases.cpp" -o /tmp/diting-alias-review1
/tmp/diting-alias-review1
python3 "$bundle/../../tests/ofrp-device-regressions.py" "$PWD"
python3 "$bundle/../../tests/ofrp-installer-regressions.py" "$PWD"
python3 "$bundle/../../tests/ofrp-source-helper-regressions.py"
bash "$bundle/build.sh" "$PWD"
```

`apply-source.py` validates all upstream project revisions and checks both patches before applying either.
`--verify-applied` validates hashes, executable bits, deleted files and unrelated changes, including symlink rejection.
The build helper removes only the hash-verified obsolete `zn_TW.xml` generated overlay when present.
Build with four jobs by default; set `JOBS` to change it. Output: `out/target/product/diting/recovery.img`.
Binary reproducibility is not claimed across different build timestamps or hosts.

## Device acceptance still needed

Use the project's established Recovery installation procedure for the correct device and compatible ROM.
First check boot/menu and FBE data access; then repeat screen off/on and touch, switch MTP/ADB and transfer a file,
check fastbootd and battery, and finally use a valid signed project OTA and confirm Android boot/snapshot merging.
Host rejection tests do not require flashing a deliberately incompatible or damaged package on a phone.
No K50 Ultra or direct stock HyperOS qualification is claimed.

## License and credits

Retain each file's upstream notices and license. Recovery code and tests retain GPL-3.0-or-later;
device/helper files retain their specified licenses. Included license texts do not relicense third-party assets.
Thanks to OrangeFox, TeamWin, AOSP, AviderMin, Xiaomi/Qualcomm and the upstream contributors.
Maintainer: N1-k0-la1. Unofficial testing candidate.
