# AviumUI 16.2.2 · diting / ditingp

基于 Android 16 的非官方定制 ROM，面向 **Xiaomi 12T Pro** 与 **Redmi K50 至尊版（K50 Ultra）**。
维护者：[N1-k0-la1](https://github.com/N1-k0-la1)。本项目独立于 AviumUI、OrangeFox 官方发行。

## 当前公开版本

最新已发布 ROM 为 **round8fix20261016（历史总批次 27）**，本仓库公开 **89 份有序补丁**。
对应 ROM 源码冻结版本是 [`44ec612`](https://github.com/N1-k0-la1/diting-aviumui/tree/44ec6126bb2c74e922eed7b299f0c503d1eedcc0)；后续文档整理不改变旧成品的源码来源、签名或 SHA256。
维护中的后续构建尚未作为本仓库的新版本公开，不能用当前公开补丁复现未公开候选。

| 成品 | 主机验证 | 已有手机实测范围 |
| --- | --- | --- |
| round8 GMS | 已独立构建、发布签名、OTA/payload、实际镜像及 Windows 回读校验 | 维护者确认 12T Pro 刷入后 QQ 登录和快速返回桌面 UI 正常 |
| round8 Vanilla | 已独立构建、签名及相同主机校验 | 无本批对应手机验收记录 |
| OrangeFox review2 | 本项目 diting 非官方正式版，源码和镜像保持原记录 | 维护者在 12T Pro 多次使用同一镜像安装项目 ROM，且 `/sdcard` 显示正常 |

**12T Pro 的结果不能代替 K50 Ultra 验收。** K50 Ultra 指纹等硬件、LHDC 实耳机、OFRP PIN 解密与扩展 USB 场景仍需分别验证。

成品由维护者通过网盘分发。本仓库提供源码补丁、说明和校验记录，不托管完整 ROM。
请按完整文件名、SHA256 和成品随附的 `MANIFEST.json` 核对版本，**每版使用它自己的原始 boot**。

## 常用入口

- 使用：[ROM 安装](INSTALL.md) · [OFRP 安装](OFRP-INSTALL.md) · [发布说明](RELEASE.md)
- 校验：[当前成品清单](ROUND8-VARIANTS.json) · [二进制 SHA256](ROM-SHA256SUMS) · [验证记录](VALIDATION.json)
- 构建：[构建说明](BUILD.md) · [补丁清单](patch-series.json) · [固定上游版本](manifests/default.xml)
- 来源：[鸣谢](CREDITS.md) · [许可范围](LICENSES.md) · [外部输入与哈希](external-artifacts.json) · [内核](KERNEL.md)
- 查阅：[文档导航](docs/README.md) · [历史版本](docs/history/README.md) · [审查记录](docs/reviews/README.md)

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

## English

Unofficial AviumUI 16.2.2 / Android 16 for Xiaomi 12T Pro and Redmi K50 Ultra (diting/ditingp).
The latest released ROM is **round8fix20261016 (batch 27)**. This public checkout contains **89 ordered patches**; its corresponding frozen ROM source is `44ec612`. Later documentation changes do not rebuild or relicense historical artifacts.
GMS and Vanilla passed independent host qualification. The maintainer reports QQ login and correct rapid-BACK desktop behavior on 12T Pro GMS. Vanilla, K50 Ultra, LHDC headset playback and extended Recovery scenarios require their own acceptance.
Subsequent local candidates are not a new public release of this repository. See [Build](BUILD.md), [Install](INSTALL.md), [Licensing](LICENSES.md) and the [documentation index](docs/README.md). Report reproducible issues through GitHub Issues with sanitized evidence.
