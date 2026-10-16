# OrangeFox diting / ditingp review2 source

Review2 fixes verified against the actual shared init, device tree, installer, Android 16 platform APIs
and kernel drivers. See the [item-by-item Chinese review](../../OFRP-REVIEW-20261016.md).
This is a newly built, host-qualified testing candidate; its own phone acceptance is pending.
Historical tested bootctrl and host-qualified review1 bundles remain unchanged.

## Changes and limitations

- Propagate failed signature verification from the alternative installer wrapper. The main GUI's existing
  explicit signature-verification setting is preserved.
- Select one USB configuration owner: generic init remains the default; this device opts into its complete
  device rules, including fastbootd and sideload. Test both init files together, not just the device file.
- Match pipe-separated source fingerprints through one shared metadata guard; report A/B failures through
  the normal GUI/status tail. Bound both real text metadata readers.
- Stop silently accepting obsolete `compatibility.zip`: the legacy validation API is absent in Android 16.
  With the compatibility check enabled, its presence now fails explicitly without decompressing untrusted
  nested archives. Modern packages without that archive continue. The existing build-time
  `OF_NO_TREBLE_COMPATIBILITY_CHECK=1` opt-out is preserved; this device sets it to 0 and has no runtime
  skip switch. This is not an implementation of a replacement VINTF validator.
- Use the dedicated recovery partition reinstall path, complete the build-time logical partition list,
  provide product-scoped FOX defaults and recognize ADSP `.mbn` identities as well as `.mdt`.

The supplied project GMS/Vanilla reviewfix20261015 ZIPs were inspected and do not contain the obsolete archive.
No universal third-party ZIP, stock HyperOS, K50 Ultra, downgrade safety or OEM anti-rollback claim is made.
The existing high build SPL needed by the recovery configuration was not changed on an unproven assumption.
The image has no standalone kernel; use compatible boot/vendor_boot. FBE decryption and encrypted backups
are separate features; encrypted backups remain compiled out.

## Source and reproduction

`manifest.xml` pins 405 upstream projects. The two cumulative patches start from device commit
`1a1b5d3f6c908145e360da990a70b41042929615` and Recovery commit
`0f7831d3240f4c3925a0b5fd7d2c907ddf8704c2`.
**Apply on clean upstream checkouts, not over review1 or another historical patch bundle.**
`SOURCE.json` identifies local source commits, changed file hashes/modes, deletion and image identity.
`built-manifest.xml` pins the two local revisions. `SOURCE-VALIDATION.json` records exact tree replay;
`HOST-TESTS.json` and `IMAGE-AUDIT.json` distinguish host qualification from phone testing.

On Linux / WSL ext4 with the [OrangeFox build dependencies](https://wiki.orangefox.tech/dev/building):

```bash
bundle=/path/to/diting-aviumui/recovery/orangefox-diting-20261016-review2
mkdir -p "$HOME/orangefox-diting-review2"
cd "$HOME/orangefox-diting-review2"
repo init -u https://gitlab.com/OrangeFox/Manifest.git \
  -b 4c65ca28fa67580172ee6bf99892a054c19dcebe --depth=1 --no-clone-bundle
cp "$bundle/manifest.xml" .repo/manifests/diting-review2.xml
repo init -m diting-review2.xml
repo sync -c -j4 --no-clone-bundle --no-tags --fail-fast
git clone https://github.com/AviderMin/ofrp_device_xiaomi_diting device/xiaomi/diting
git -C device/xiaomi/diting checkout --detach 1a1b5d3f6c908145e360da990a70b41042929615
python3 "$bundle/apply-source.py" "$PWD"
g++ -std=c++17 -Wall -Wextra -Werror -fsanitize=address,undefined \
  -I bootable/recovery "$bundle/test-diting-ota-aliases.cpp" -o /tmp/diting-alias-review2
/tmp/diting-alias-review2
python3 "$bundle/../../tests/ofrp-device-regressions.py" "$PWD"
python3 "$bundle/../../tests/ofrp-installer-regressions.py" "$PWD"
python3 "$bundle/../../tests/ofrp-cross-file-regressions.py" "$PWD"
bash "$bundle/build.sh" "$PWD"
```

The helper prechecks both patches and all upstream revisions, then validates files, modes and deletion.
Four build jobs are used by default; set `JOBS` to change this. The image is
`out/target/product/diting/recovery.img`. Build timestamps/host differences can change binary hashes.

## Phone acceptance pending

Check boot/menu and data decryption; repeat screen off/on with touch; transfer a file with MTP,
switch ADB/fastbootd/sideload through the normal UI and check enumeration/battery; finally install a valid
signed project OTA and verify Android boot and snapshot merging. Recovery reinstall remains untested.
The host fault tests never write deliberately incompatible, damaged or unsigned test packages to a phone.

Retain upstream licenses and copyright notices. Recovery changes/tests retain GPL-3.0-or-later;
device and helper files retain their stated licenses. No private signing material is supplied.
Credits: OrangeFox, TeamWin, AOSP, AviderMin, Xiaomi/Qualcomm and upstream contributors.
Maintainer: N1-k0-la1. Unofficial testing candidate.
