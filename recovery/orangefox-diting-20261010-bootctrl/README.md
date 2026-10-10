# Tested unofficial OrangeFox for diting / ditingp

This supersedes the failed first candidate. On the project media20261010 GMS ROM / 12T Pro,
the image passed menu/touch, screen-wake touch, FBE decryption, a full signed OTA,
Android boot and snapshot merging. K50 Ultra, fastbootd and direct HyperOS 3.0.6 boot
remain unqualified. MTP passed in earlier RAM tests; the complete final image's MTP
display test has not been repeated. See PHONE-RESULT.json and [installation](../../OFRP-INSTALL.md).

The canonical target is diting; ditingp is this project's Global product/SKU alias.
Only this exact pair is accepted at the OTA name check; other checks are retained.
The image has no standalone kernel and requires compatible boot/vendor_boot.
It is not a universal stock HyperOS Recovery.

## Fixes and provenance

- Official OrangeFox fox_16.0 manifest, commit 4c65ca28fa67580172ee6bf99892a054c19dcebe;
  manifest.xml pins 405 synchronized upstream projects.
- AviderMin diting device tree at 1a1b5d3f6c908145e360da990a70b41042929615 plus device.patch.
- Official OrangeFox Recovery at 0f7831d3240f4c3925a0b5fd7d2c907ddf8704c2 plus recovery.patch.
- Chinese resources now use the bundled WenQuanYi font, removing the missing-font crash.
- Startup and screen-wake hooks guard Goodix chip identity, recover only an invalid identity,
  and enable IRQ only after a valid identity read. They do not flash touch firmware.
- The missing boot HAL 1.2 VINTF entry is supplied. A recovery-only preload counts distinct
  boot_a/boot_b block nodes as two slots, excluding the unsuffixed alias. Slot mutations
  and snapshot calls remain in the original QTI HAL; fallback uses the original count.
- The LF postinstall fstab, precise partition dimensions, diting/ditingp OTA alias check,
  KeyMint library adaptation and public Avium OTA verification certificate are retained.

SOURCE.json records exact build revisions and changed-file hashes. SOURCE-VALIDATION.json
records reconstruction of both complete Git trees from isolated local upstream objects,
plus 12 host alias cases. It is not an independent remote fetch or second full build.
IMAGE-AUDIT.json describes the build-time image checks; runtime outcomes are separate.
built-manifest.xml records the actual build's local revisions. No private keys or device logs
are supplied. Encrypted backups are compiled out by the upstream default, distinct from
FBE storage decryption.

## Build on Linux / WSL ext4

Install the dependencies documented by [OrangeFox](https://wiki.orangefox.tech/dev/building),
including `repo`, Git, Python 3, ccache and the compiler/build prerequisites.
Use a filesystem with native Linux permissions and substantial free space; the initial
source/toolchain download and build require more than a small incremental ROM build.

Clone this public repository, then substitute its absolute path for `/path/to/diting-aviumui`:

```bash
bundle=/path/to/diting-aviumui/recovery/orangefox-diting-20261010-bootctrl
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

Retain every upstream license and copyright notice. Recovery modifications and alias tests
retain GPL-3.0-or-later; device/helper files retain their stated Apache-2.0 or upstream
licenses. Proprietary hardware files retain their owners' terms. Included license texts
do not relicense third-party components.

Thanks to OrangeFox, TeamWin, AOSP, AviderMin, Xiaomi/Qualcomm and all upstream contributors.
Maintainer: N1-k0-la1. This is an unofficial testing release.
