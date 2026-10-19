# 当前公开构建输入：batch29 · 2026-10-19

本仓库公开 93 份有序补丁。batch29 的 GMS 与 Vanilla 均完成正式构建、签名、实际镜像/OTA/payload/组件审核及 Windows 回读。
GMS 保留 20261018 attempt1，Vanilla 为 20261019 attempt2；同一源码冻结，签名身份不变。输入身份与实际文件哈希见 [本批清单](docs/releases/batch29-20261019/ARTIFACTS.json)。
前 89 份 round8 补丁保持原样；追加文件夹拖出修复、指纹/蓝牙修复及系统 Resolver 审批修复。上游清单、外部输入和 93 份补丁共同标识公开源码，后续文档提交不改变成品来源。
维护者反馈 12T Pro GMS 验收后没有问题，不代替 Vanilla、K50 Ultra 或全部专项硬件验收。LHDC 仍缺对应耳机实测。

软件 LHDC、相机修复和按区域启用的 eSIM 已纳入补丁；不启用 RAW 或未经验证的 Qualcomm DSP offload。
源码默认关闭 Dolby Vision；维护者公开媒体成品使用 `TARGET_DITING_DOLBY_VISION=true`。按需求明确设置，不把开关启用等同于实机解码验收。
应用补丁前，构建者应按 [external-artifacts.json](external-artifacts.json) 取得精确 Via APK 和23个媒体 ELF；来源、许可范围见 [LICENSES.md](LICENSES.md)。

```sh
git clone https://github.com/TheXPerienceProject/android_vendor_savitech_lhdc.git lhdc-donor
git -C lhdc-donor checkout 63fa4e2f923721ef7e1d25c90a5268afd196df8d
git clone https://github.com/Avicii-Labs/android_hardware_dolby.git dolby-donor
git -C dolby-donor checkout 30250166e08e6b4bc795aa361446851a0b2970be
git -C dolby-donor lfs pull
python3 diting-aviumui/tools/prepare-media-inputs.py --lhdc-checkout lhdc-donor --dolby-checkout dolby-donor --output media-inputs
```

将 media-inputs 的绝对路径传给下方 `--media-input-dir`，工具在写入源码前校验固定输入。

# Build / 构建

使用 Linux 文件系统中的源码目录（WSL2 请使用 ext4 虚拟磁盘内目录），安装 AOSP / LineageOS Android 16 所需的主机工具、Git LFS 和 repo。
本仓库只提供固定版本和补丁，不含完整 Android 源码。当前原机成功构建用了 32GB 内存、swap、低并发；不保证更高并发可用。

```sh
git clone https://github.com/N1-k0-la1/diting-aviumui.git
PATCH_PROJECT="$(realpath diting-aviumui)"
mkdir avium-source
cd avium-source
repo init -u "$PATCH_PROJECT" -b main -m manifests/default.xml --git-lfs --no-clone-bundle
repo sync -j4 --no-clone-bundle
repo forall -c 'git lfs pull'
```

取得官方 Via 7.3.3 APK（见 `external-artifacts.json`），先核对 SHA256。官方 URL 会更新；哈希不同则不能用它复现此候选。
本仓库不附带 APK，也不绕过文件校验。

```sh
python3 "$PATCH_PROJECT/tools/apply-patches.py" "$PWD" --via-apk /absolute/path/to/Via-7.3.3.apk --media-input-dir /absolute/path/to/media-inputs
export GOGC=50 GOMEMLIMIT=18GiB
export WITH_GMS=false AVIUM_FORCE_SET_FAKE_PROP=false TARGET_DITING_ESIM=true TARGET_DITING_DOLBY_VISION=false
export AVIUM_VERSION_APPEND_TIME_OF_DAY=true
source build/envsetup.sh
lunch lineage_diting-bp4a-user
m target-files-package otatools -j4
```

补丁工具在修改前检查所有文件哈希和各项目原始 HEAD / 干净状态；发生错误立即停止。
补丁工具只暂存改动。编译前请用自己的 Git 作者身份提交这些改动；内核版本会显示你实际的提交及 dirty 状态，不能期望复制维护者本地提交号。
只用于全新、与清单一致的 checkout。中途失败的目录须人工检查，不能靠重复运行忽略错误。
不要在已有定制源码目录使用这个工具。batch14 的 `TARGET_DITING_ESIM=true` 与 ditingp SKU / GL 区域限制配套；其他 SKU 或关闭此选项的构建均需独立验收。

## Signing / 签名

上面的输出是原始 user target-files，**不是已完成私有签名的发布 ZIP**。
构建者需生成自己的 APK、APEX container/payload、OTA 和 AVB 密钥，审计该 checkout 的
`META/apkcerts.txt`、`META/apexkeys.txt`、`META/misc_info.txt`，并使用其 otatools 完成重签名和 OTA 生成。
不要只执行默认 APK `-d` 映射就声称整个系统已经私有签名；嵌套 APK、共享 UID、APEX、payload 和 AVB 链还需独立核对。
遵循 [AOSP release signing](https://source.android.com/docs/core/ota/sign_builds) 并以实际工具的帮助和元数据为准。
维护者私钥不公开，因此自己的签名、日期和构建环境不同，输出字节和哈希不会与 发布包相同。

## Historical validation / 早期验证记录

以下 batch13/batch14 记录保留其历史范围；当前公开89补丁版本状态以本文顶部和 README 为准。

当前 93 份有序补丁已在 31 个定制项目的临时 Git 索引中按序重放，与公开目标树精确一致；1190 个项目包括 1187 个基础项目及 3 个可选 GMS 项目。
维护者现有 checkout 的两版正式整包已通过构建和主机产物审核。精确补丁重放不等于从零同步后再完成第二轮完整构建，也不等于全面设备验收。
Via APK 与媒体 ELF 是独立输入，均需满足固定来源和 SHA256；仓库不分发这些专有二进制。

## English

Use a Linux filesystem, repo, Git LFS and Android 16 host dependencies.
Initialize this manifest, sync pinned sources, provide the exact official Via APK, and apply the series once to a fresh checkout.
The commands above build real user target-files. Generate and audit your own complete signing material before producing an OTA.
Private maintainer keys are not distributed; your build is not byte-for-byte reproducible as the signed release ZIP.
Do not substitute a newer Via binary without an explicit source/version change and validation.

## GMS / 可选 Google 组件

Vanilla 使用上面的 `WITH_GMS=false`。GMS 在应用补丁之前加入三个固定依赖：

```sh
mkdir -p .repo/local_manifests
cp "$PATCH_PROJECT/manifests/gms.xml" .repo/local_manifests/gms.xml
REPO_SKIP_SELF_UPDATE=1 repo sync vendor/pixel/gms vendor/pixel/clocks vendor/pixel/sounds --no-manifest-update -c -j3 --no-tags --no-clone-bundle
export WITH_GMS=true AVIUM_FORCE_SET_FAKE_PROP=false TARGET_DITING_ESIM=true TARGET_DITING_DOLBY_VISION=true
source build/envsetup.sh
lunch lineage_diting-bp4a-user
m installclean
m target-files-package otatools -j4
```

`envsetup.sh` 会按上游规则拼接 GMS APK 分片。两个 flavour 切换时执行 `m installclean`，防止安装文件残留；编译缓存可以复用。
全新 checkout 应先同步 GMS 三个仓库，再执行前面的补丁应用步骤；已经应用过补丁的 checkout 不要再次应用。
先复制保存每个 flavour 的 target-files，再编译另一个；分别完成签名和验收。
保留 Google 等外部 `PRESIGNED` APK 的原始签名及签名轮换链，不将它们替换为维护者签名。
GMS 组件并不保证 Google 认证、Play Integrity 或硬件认证通过。
GMS proprietary inputs retain their upstream licenses; this source repository does not redistribute their APK binaries.

## Dual-model scope / 双机型范围

原设备树按 `ro.boot.hwc` 加载 CN / GL ODM 属性。相机组件已有 HM6 与 HP1，沿用其选择逻辑。
内置 eUICC feature 限于 `ro.boot.hardware.sku=ditingp`，两个相关 overlay 限于 `ro.boot.hwc=GL`。
这是源码范围限制，不代替 K50 至尊版的启动、108MP 相机和双实体 SIM 实测。
原固件二进制保持；两机型兼容未完成验收前，不把共用代号当成已经验证的刷机承诺。

第三轮反馈核实与修复见 [ROUND3-REVIEW-20261014.md](ROUND3-REVIEW-20261014.md)。

全局字体、防误触和文件夹模糊修复及验证边界见 [ROUND4-REVIEW-20261015.md](ROUND4-REVIEW-20261015.md)。

新增回归（主机测试使用 Android API 替身，设备字体测试使用真实 native 排版）：

```sh
python3 tests/fingerprint-mistouch-regressions.py /path/to/patched/android
python3 tests/folder-blur-regressions.py /path/to/patched/android
python3 tests/global-font-device-regressions.py /path/to/patched/android --adb /path/to/adb --serial DEVICE_SERIAL --font /sdcard/test-font.ttf
```

设备字体测试需要已构建的 framework.jar、SDK/JDK 21、Android 16 和 su；仅运行临时进程，不安装字体、不改系统配置、不重启。请使用与原字体明显不同的已有字体文件。

第五轮核实、修复与未成立的审查项见 [ROUND5-REVIEW-20261015.md](ROUND5-REVIEW-20261015.md)。已交付测试包不含本轮追加补丁。

单独运行指纹生命周期/guest guard 主机回归：`python3 tests/session-lifecycle-regressions.py /path/to/patched/android`；该套件也由 fingerprint-mistouch-regressions.py 调用。

Resolver 主机回归：`python3 tests/resolver-approval-regressions.py /path/to/patched/android`。正式手机验收与主机 API 替身测试分别记录。
