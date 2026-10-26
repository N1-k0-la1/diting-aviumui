# batch38 · 2026-10-26 源码与构建

当前113份有序补丁覆盖35个定制项目。固定清单为1187个基础项目及3个可选GMS项目。
GMS与Vanilla源于同一冻结，均通过整包构建、签名、实际镜像/OTA/payload、组件和Windows回读审核。
[源码清单](patch-series.json) · [本批成品与输入身份](docs/releases/batch38-20261026/ARTIFACTS.json)。

## 获取固定源码

使用Linux文件系统；WSL2源码放在ext4内。安装Android 16所需主机依赖、Git LFS、repo和ccache。
使用源码自带JDK21、-j4和ccache；内存、swap及其他编译器并行行为也会影响资源需求。

```sh
git clone https://github.com/N1-k0-la1/diting-aviumui.git
PATCH_PROJECT="$(realpath diting-aviumui)"
mkdir avium-source
cd avium-source
repo init -u "$PATCH_PROJECT" -b main -m manifests/default.xml --git-lfs --no-clone-bundle
repo sync -j4 --no-clone-bundle
repo forall -c 'git lfs pull'
```

GMS构建者在应用补丁前同步三个固定依赖；Vanilla跳过这一段：

```sh
mkdir -p .repo/local_manifests
cp "$PATCH_PROJECT/manifests/gms.xml" .repo/local_manifests/gms.xml
REPO_SKIP_SELF_UPDATE=1 repo sync vendor/pixel/gms vendor/pixel/clocks vendor/pixel/sounds --no-manifest-update -c -j3 --no-tags --no-clone-bundle
```

## 精确外部输入与补丁

按 [external-artifacts.json](external-artifacts.json) 取得官方Via 7.3.3 APK与23个媒体ELF，先核对固定哈希。上游下载内容可能变化，不能用新版文件替代原哈希。
在源码目录外准备媒体输入，例如：

```sh
git clone https://github.com/TheXPerienceProject/android_vendor_savitech_lhdc.git lhdc-donor
git -C lhdc-donor checkout 63fa4e2f923721ef7e1d25c90a5268afd196df8d
git clone https://github.com/Avicii-Labs/android_hardware_dolby.git dolby-donor
git -C dolby-donor checkout 30250166e08e6b4bc795aa361446851a0b2970be
git -C dolby-donor lfs pull
python3 "$PATCH_PROJECT/tools/prepare-media-inputs.py" --lhdc-checkout lhdc-donor --dolby-checkout dolby-donor --output media-inputs
```

在Android源码根目录执行：

```sh
python3 "$PATCH_PROJECT/tools/apply-patches.py" "$PWD" --via-apk /absolute/path/to/Via-7.3.3.apk --media-input-dir /absolute/path/to/media-inputs
```

工具先验证补丁/外部输入哈希、各项目固定HEAD与干净状态，再按序应用；只适用于全新checkout。
工具暂存改动但不代替提交。请使用自己的Git作者身份提交；失败须保留现场检查，不能直接重复运行或忽略标记。
内核提交号/dirty标记取决于实际构建者，不能保证与维护者产物相同。
本批SOURCE-PATCH-SERIES.json记录113份补丁及上游/目标版本，与构建冻结一致；根目录清单另含发布说明等元数据。

## 编译与变体切换

```sh
export USE_CCACHE=1 CCACHE_EXEC="$(command -v ccache)" CCACHE_DIR="$HOME/.cache/ccache"
export JAVA_HOME="$PWD/prebuilts/jdk/jdk21/linux-x86"
export PATH="$JAVA_HOME/bin:$PATH"
export GOGC=50 GOMEMLIMIT=18GiB
export WITH_GMS=false AVIUM_FORCE_SET_FAKE_PROP=false TARGET_DITING_ESIM=true TARGET_DITING_DOLBY_VISION=true
export AVIUM_VERSION_APPEND_TIME_OF_DAY=true
source build/envsetup.sh
lunch lineage_diting-bp4a-user
m target-files-package otatools -j4
```

GMS使用WITH_GMS=true，并提前同步可选依赖。envsetup按上游规则拼接GMS APK分片。
两变体共用out，必须串行；切换变体重新配置后执行m installclean，先另存上一版target-files及日志，再构建另一版。
缓存可以复用，签名/组件/镜像证据必须分别归档。不要将后续变体的共享out当作旧产物的证明。
12T Pro eSIM按SKU/固件区域限制启用；K50U不据同代号推定eSIM能力。Dolby开关启用不等于实机播放或流媒体认证通过。

## 发布签名与验证

上述命令生成原始user target-files，不是已签名发布OTA。构建者需准备自己的APK、APEX container/payload、OTA及AVB密钥，审计META/apkcerts.txt、META/apexkeys.txt与misc_info。
保留外部PRESIGNED APK原始签名和轮换链，不能仅执行默认APK映射便声称全系统已正确重签。
遵循 [AOSP release signing](https://source.android.com/docs/core/ota/sign_builds) 与实际otatools帮助，完成实际OTA/payload、分区镜像、组件及最终复制文件回读。
维护者密钥不分发。签名、时间和环境不同，公开者的构建不会与维护者发布包字节一致。

113份补丁已在临时Git索引按序重放，覆盖35个定制项目；这不等于另做一次从零同步全编或完整硬件验收。
维护者12T Pro GMS测试暂未发现问题；Vanilla、K50U、LHDC耳机及长期组合需独立验证，详见 [验证范围](README.md)。

## 主机回归

```sh
python3 tests/session-lifecycle-regressions.py /path/to/patched/android
python3 tests/resolver-approval-regressions.py /path/to/patched/android
python3 tests/failure-diagnostics-regressions.py /path/to/patched/android --output /tmp/failure-diagnostics.json
```

新的诊断回归使用源码JDK21/kotlinc和主机g++，从给定源码提取真实方法与模型，运行故障注入和9组安装失败UI场景；不操作手机、账户或加密存储。
测试替身不能代替完整Android平台和手机验收。其他专项范围见 [审查索引](docs/reviews/README.md)。

## English

Use pinned sources on a Linux filesystem, exact external inputs, bundled JDK21, ccache and -j4.
Apply the ordered series once to a fresh checkout. Build GMS and Vanilla serially, retain each target-files archive, and clean installed outputs when switching variants.
Provide and audit your own complete signing identity; preserve externally signed applications. Public source reconstruction and host regression tests do not replace full builds or device acceptance.
