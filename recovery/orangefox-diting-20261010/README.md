# Unofficial OrangeFox for diting / ditingp

**First phone test failed:** the maintainer reports a repeating Fox logo on 12T Pro.
The active Recovery partition hash matches this candidate. The phone has returned to Android.
No live Recovery crash log has been captured yet; the cause is unconfirmed.
**Do not use this candidate for ROM installation or advertise it as a working Recovery.**

This is the corresponding source bundle for the project's Android 16 Recovery candidate.
It is separate from the ROM patch series. The first 100 MiB image has compiled and passed static image/AVB/dependency checks.
The initial 12T Pro boot test failed with a repeating Fox logo; the previous loop has not been fixed.
See IMAGE-AUDIT.json and [the phone test checklist](TESTING.md).
Encrypted backups are compiled out by the current upstream default; this is separate from FBE storage decryption.

## Device names and scope

Redmi K50 Ultra and Xiaomi 12T Pro share the diting device family. In this project's
Global product configuration, the 12T Pro uses `ditingp` as the product/SKU name.
The canonical Recovery target remains `diting`. Both exact OTA aliases are configured;
the Recovery patch permits this pair at the existing package-device check. It does not
alter the hardware SKU, region, serial checks, downgrade checks or payload/signature checks.
Packages for unrelated devices remain subject to the normal device check.

The image uses boot header v4 and excludes a standalone kernel. It depends on compatible
`boot` / `vendor_boot` firmware. The initial target is this project's Android 16 AviumUI ROM,
not universal MIUI/HyperOS compatibility. Storage decryption, touch, ADB, fastbootd,
OTA installation and the K50 Ultra still need real-device tests.

## Source provenance and changes

- Official [OrangeFox Manifest](https://gitlab.com/OrangeFox/Manifest), `fox_16.0`,
  manifest commit `4c65ca28fa67580172ee6bf99892a054c19dcebe`.
  `manifest.xml` pins all 405 upstream projects actually synchronized.
- [AviderMin's diting device tree](https://github.com/AviderMin/ofrp_device_xiaomi_diting),
  base `1a1b5d3f6c908145e360da990a70b41042929615`, plus `device.patch`.
- Official [OrangeFox Recovery](https://gitlab.com/OrangeFox/bootable/Recovery),
  base `0f7831d3240f4c3925a0b5fd7d2c907ddf8704c2`, plus `recovery.patch`.
- Android 16 KeyMint adaptation follows the official OrangeFox mondrian device tree;
  its exact revision is included in the manifest. Original diting prebuilt hardware files
  are retained from AviderMin's base, without binary changes in these patches.

The device port corrects super/dtbo dimensions, enforces LF checkout, includes debuggerd
dependencies, searches GKI/vendor_boot modules, uses legacy battery reads, and adapts the
legacy KeyMint library names. The public Avium OTA verification certificate is included;
**no private signing keys** are part of this bundle. A successful compilation cannot prove
that the legacy KeyMint service decrypts the installed ROM's data.

The AviderMin base already has an LF postinstall fstab. The CRLF issue observed in the
separate TWRP used during ROM installation is not attributed to that upstream repository.

## Build on Linux / WSL ext4

Install the dependencies documented by [OrangeFox](https://wiki.orangefox.tech/dev/building),
including `repo`, Git, Python 3, ccache and the compiler/build prerequisites.
Use a filesystem with native Linux permissions and substantial free space; the initial
source/toolchain download and build require more than a small incremental ROM build.

Clone this public repository, then substitute its absolute path for `/path/to/diting-aviumui`:

```bash
bundle=/path/to/diting-aviumui/recovery/orangefox-diting-20261010
mkdir -p "$HOME/orangefox-diting"
cd "$HOME/orangefox-diting"
repo init -u https://gitlab.com/OrangeFox/Manifest.git \
  -b 4c65ca28fa67580172ee6bf99892a054c19dcebe --depth=1 --no-clone-bundle
cp "$bundle/manifest.xml" .repo/manifests/diting-20261010.xml
repo init -m diting-20261010.xml
repo sync -c -j4 --no-clone-bundle --no-tags --fail-fast
git clone https://github.com/AviderMin/ofrp_device_xiaomi_diting device/xiaomi/diting
git -C device/xiaomi/diting checkout --detach 1a1b5d3f6c908145e360da990a70b41042929615
python3 "$bundle/apply-source.py" "$PWD"
g++ -std=c++17 -Wall -Wextra -Werror -I bootable/recovery \
  "$bundle/test-diting-ota-aliases.cpp" -o /tmp/test-diting-ota-aliases
/tmp/test-diting-ota-aliases
bash "$bundle/build.sh" "$PWD"
```

The first build used four jobs. A later rebuild may set `JOBS=4` explicitly.
The output is `out/target/product/diting/recovery.img`.
Patch/file hashes and the local commits used for the actual build are in `SOURCE.json`.
SOURCE-VALIDATION.json records exact complete Git-tree reconstruction for both modified
projects from isolated local pinned Git objects and the 12-case host alias test. This was
not a second full build or an independent remote fetch.

## License and credits

Preserve every upstream file's license and copyright notices. OrangeFox Recovery modifications
and the new helper/test files here are GPL-3.0-or-later; Android device files retain their
original Apache-2.0 notices, and proprietary hardware files retain their owners' terms.
This repository's general license does not relicense these components.

Thanks to OrangeFox, TeamWin, AOSP, AviderMin, Xiaomi/Qualcomm and upstream contributors.
Maintainer: N1-k0-la1. This is an unofficial project candidate, not an official OrangeFox release.
