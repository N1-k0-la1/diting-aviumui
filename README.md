# AviumUI 16.2.2 · diting / ditingp

基于 Android 16 的非官方定制 ROM，面向 **Xiaomi 12T Pro** 与 **Redmi K50 至尊版（K50 Ultra）**。
维护者：[N1-k0-la1](https://github.com/N1-k0-la1)。本项目独立于 AviumUI、OrangeFox 官方发行。

## 当前公开源码与成品

当前已发布 **AVIUMUI-diting-UNOFFICIAL-261019（batch29）**，公开 **93 份有序补丁**。维护者已确认通过酷安发布，GMS 与 Vanilla 成品已上传网盘。
本批合入 APK 打开流程、文件夹拖出模糊、指纹 HAL 和蓝牙开发者选项修复，见 [更新说明](docs/releases/batch29-20261019/README.md)。

| 成品 | 主机验证 | 已有手机实测范围 |
| --- | --- | --- |
| batch29 GMS（20261018 attempt1） | 构建、发布签名、OTA/payload、实际镜像、组件一致性及 Windows 回读通过 | 维护者在验收清单后反馈 12T Pro GMS 没有问题；未另行记录逐项结果 |
| batch29 Vanilla（20261019 attempt2） | 独立构建、签名及相同主机审核通过 | 无本批对应手机验收记录 |
| OrangeFox 20261016-review2 | 沿用原镜像，本次没有更新 | 维护者在 12T Pro 多次用其安装项目 ROM，且 `/sdcard` 显示正常 |

**12T Pro 的结果不能代替 K50 Ultra 验收。** K50 Ultra 指纹等硬件、LHDC 实耳机、OFRP PIN 解密与扩展 USB 场景仍需分别验证。
指纹失败计数在 HAL 进程重启后仍会清零，K50 Ultra 录入失败根因未确认。

成品由维护者通过网盘分发。本仓库提供源码补丁、说明和校验记录，不托管完整 ROM。
请按完整文件名、SHA256 和成品随附的 `MANIFEST.json` 核对版本，**每版使用它自己的原始 boot**。
本批 GMS 与 Vanilla 使用同一源码冻结，日期/attempt 不同是串行构建及同源恢复记录，不能据文件日期混用配套镜像。

## 下载

- [夸克网盘](https://pan.quark.cn/s/50c002f7af5d?pwd=XTcx)，提取码：`XTcx`
- [Google Drive](https://drive.google.com/drive/folders/16n1umX8_nvy8ADYls8SkH9TVBS_wKAEl?usp=drive_link)

Vanilla / GMS 按需选择，核对完整文件名和 SHA256；每版使用各自对应的原始 boot。刷法见 [ROM 安装](INSTALL.md) 与 [OFRP 安装](OFRP-INSTALL.md)。

## 常用入口

- 使用：[ROM 安装](INSTALL.md) · [OFRP 安装](OFRP-INSTALL.md) · [发布说明](RELEASE.md)
- 校验：[当前成品清单](docs/releases/batch29-20261019/ARTIFACTS.json) · [本批二进制 SHA256](docs/releases/batch29-20261019/SHA256SUMS) · [验证记录](VALIDATION.json)
- 构建：[构建说明](BUILD.md) · [补丁清单](patch-series.json) · [固定上游版本](manifests/default.xml)
- 来源：[鸣谢](CREDITS.md) · [许可范围](LICENSES.md) · [外部输入与哈希](external-artifacts.json) · [内核](KERNEL.md)
- 查阅：[文档导航](docs/README.md) · [历史版本](docs/history/README.md) · [审查记录](docs/reviews/README.md)

## 本次更新

- 修复 Telegram 等来源 APK 进入错误的“Android 系统”分身选择，恢复正常打开方式和安装流程。
- 修复双应用文件夹拖出应用后的模糊残留。
- 完善指纹 HAL 初始化、会话生命周期与同进程锁定计数衔接；蓝牙能力缺失时对话框安全降级。
- [APK 修复](RESOLVER-APPROVAL-FIX-20261018.md) · [文件夹修复](FOLDER-DRAG-FIX-20261017.md) · [指纹/蓝牙修复](docs/reviews/BATCH28-FIXES-20261018.md)

## 主要定制与限制

- 全局字体导入、预览、保存和恢复；保留等宽、emoji 与语言回退。应用自带字体和图片文字可能不变。
- 无锁屏状态下的防误触处理；桌面模糊、文件夹深度和快速连续返回修复。
- QQ 分身授权结果回传及跨空间真实调用者签名核验。使用隐藏模块时仍需保留必要的包查询可见性。
- 相机录像切换修复、LHDC 软件编码、HDR/杜比视界配置，以及按 SKU/区域启用的 12T Pro eSIM。
- GMS 的 Google 认证及 Play Integrity 以实际结果为准；已知验证范围不代表全部硬件、授权组合或长期稳定性通过。

仓库不包含完整 Android checkout；Via APK 和 23 个媒体 ELF 由构建者按固定来源及 SHA256 另行提供。
补丁、上游代码、Recovery 和专有输入各自保留适用许可，不能将整个 ROM 视为统一采用 Apache-2.0；详见 [LICENSES.md](LICENSES.md)。

## 风险与反馈

刷机可能导致数据丢失或设备无法启动；请先备份并按对应版本安装说明操作。项目按现状提供，不提供适用性或稳定性保证；各组件适用其自身许可中的担保条款。

问题请提交到 [GitHub Issues](https://github.com/N1-k0-la1/diting-aviumui/issues)，提供机型、完整版本、GMS/Vanilla、复现步骤和预期/实际结果。
日志提交前请移除账号、序列号、设备标识及其他个人信息；不要上传签名材料、HMA 配置或完整私人日志。

## 历史版本

[round8fix20261016 / batch27](ROUND8-VARIANTS.json) 保留原文件名、来源和校验值；其源码冻结仍为 `44ec6126bb2c74e922eed7b299f0c503d1eedcc0`。
更多历史记录见 [历史导航](docs/history/README.md)。

## English

Unofficial AviumUI 16.2.2 / Android 16 for Xiaomi 12T Pro and Redmi K50 Ultra (diting/ditingp).
The released version is **AVIUMUI-diting-UNOFFICIAL-261019 (batch29)**, with **93 ordered patches**: APK resolver approval, folder drag-out blur, fingerprint HAL lifecycle/lockout and Bluetooth dialog fixes.
Both GMS (20261018 attempt1) and Vanilla (20261019 attempt2) passed full builds, signing and independent host artifact qualification from the same frozen source inputs.
The maintainer reports no problems on 12T Pro GMS after the test checklist; individual cases were not independently recorded. Vanilla, K50 Ultra, LHDC headset playback and extended Recovery scenarios require their own acceptance.
OFRP remains the existing 20261016-review2 image. The maintainer has confirmed publication and cloud distribution. Download from [Quark](https://pan.quark.cn/s/50c002f7af5d?pwd=XTcx) (code: XTcx) or [Google Drive](https://drive.google.com/drive/folders/16n1umX8_nvy8ADYls8SkH9TVBS_wKAEl?usp=drive_link).
See [batch29 artifacts](docs/releases/batch29-20261019/ARTIFACTS.json), [Build](BUILD.md), [Install](INSTALL.md), [Licensing](LICENSES.md) and the [documentation index](docs/README.md).
