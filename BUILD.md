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
python3 "$PATCH_PROJECT/tools/apply-patches.py" "$PWD" --via-apk /absolute/path/to/Via-7.3.3.apk
export GOGC=50 GOMEMLIMIT=18GiB
export WITH_GMS=false AVIUM_FORCE_SET_FAKE_PROP=false TARGET_DITING_ESIM=true
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
维护者私钥不公开，因此自己的签名、日期和构建环境不同，输出字节和哈希不会与 batch13 相同。

## Validation scope / 验证范围

前 48 份补丁对应已构建的 batch13 功能源代码链，最后 2 份是 batch14 的区域 eSIM 与内核命名改动，两种 flavour 已完成维护者现有 checkout 的构建与主机产物核对。GMS 已在 12T Pro 完成首次启动和部分功能验收；Vanilla／K50 及完整硬件与长期回归尚待进行。公开清单固定上游基础版本，再按顺序恢复变更。
公开导出不包含 Via 二进制补丁，只包含 README 元数据和精确 APK 的独立输入要求。
从固定上游独立获取的 79 个原始文件已按顺序应用全部 50 份公开补丁。全新全量 repo sync / 构建仍需验证；这不等同于第二次完整构建。

## English

Use a Linux filesystem, repo, Git LFS and Android 16 host dependencies.
Initialize this manifest, sync pinned sources, provide the exact official Via APK, and apply the series once to a fresh checkout.
The commands above build real user target-files. Generate and audit your own complete signing material before producing an OTA.
Private maintainer keys are not distributed; your build is not byte-for-byte reproducible as the signed batch13 ZIP.
Do not substitute a newer Via binary without an explicit source/version change and validation.

## GMS / 可选 Google 组件

Vanilla 使用上面的 `WITH_GMS=false`。GMS 在应用补丁之前加入三个固定依赖：

```sh
mkdir -p .repo/local_manifests
cp "$PATCH_PROJECT/manifests/gms.xml" .repo/local_manifests/gms.xml
REPO_SKIP_SELF_UPDATE=1 repo sync vendor/pixel/gms vendor/pixel/clocks vendor/pixel/sounds --no-manifest-update -c -j3 --no-tags --no-clone-bundle
export WITH_GMS=true AVIUM_FORCE_SET_FAKE_PROP=false TARGET_DITING_ESIM=true
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
