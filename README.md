# AviumUI 16.2.2 · diting / ditingp · 20261016

基于 Android 16 的非官方定制 ROM，面向 **Xiaomi 12T Pro** 与 **Redmi K50 至尊版（K50 Ultra）**。
维护者：[N1-k0-la1](https://github.com/N1-k0-la1)。本项目独立于 AviumUI、OrangeFox 官方发行。

## 当前版本与进度

ROM 批次：**`round8fix20261016`**。当前公开源码包含 **89 份有序补丁**。
以下为 2026-10-16 本次更新时的状态：

| 成品 | 当前状态 | 已有实测 |
| --- | --- | --- |
| GMS ROM | 已完成构建、发布签名、OTA/分区镜像及 Windows 回读校验，已准备发布 | 维护者确认 12T Pro 刷入后 QQ 登录、快速返回后的桌面 UI 正常 |
| Vanilla ROM | 正在独立构建；尚未完成本批成品校验 | 本批尚无刷入结果 |
| OrangeFox review2 | 本项目 diting **非官方正式版** | 维护者在 12T Pro 持续使用同一镜像安装后续 ROM，刷入与 `/sdcard` 目录显示正常 |

GMS 文件名：`AviumUI-16.2.2-diting-gms-user-round8fix20261016.zip`。
对应原版 boot：成品目录中的 `gms/boot.img`。OFRP 镜像：`OrangeFox-diting-ditingp-20261016-review2.img`。
GMS 的六个配套镜像来自同一已签名 ROM；其中 `gms/recovery.img` 是 Avium Recovery。

- [当前 GMS / OFRP 文件、SHA256 与验证范围](GMS-ROUND8-RELEASE.json)
- [发布说明与已知限制](RELEASE.md)
- [当前 ROM 安装说明](INSTALL.md) · [当前 OFRP 安装说明](OFRP-INSTALL.md)
- [二进制校验值](ROM-SHA256SUMS) · [详细验证记录](VALIDATION.json)

**成品由维护者通过网盘分发。** 本仓库提供源码、构建说明和校验元数据；新版网盘上传状态未在仓库中确认。
请按完整文件名和 SHA256 取得同批文件，使用成品目录随附的安装说明与 `MANIFEST.json`。

## 本次主要更新

- **全局字体替换**：应用使用系统默认字体时也可生效；完善导入、预览、保存、恢复默认与异常清理。
- **防误触**：锁屏设为“无”时不再在桌面触发拦截。
- **桌面动画**：修复 Thanox 等应用极快连续返回后的壁纸模糊残留，完善文件夹模糊刷新。
- **QQ 分身授权**：修复结果回传，并让分身核验实际主空间调用者的真实签名。
- **蓝牙与指纹边界处理**：修复 LHDC 空指针、畸形包和参数处理，以及指纹会话、令牌与生命周期缺陷。
- 保留相机修复、HDR/杜比视界、LHDC V3/V4/V5 与按机型/固件区域启用的 12T Pro eSIM 支持。
- **OFRP review2**：完善安装器错误处理、公共/设备 USB 配置互斥、设备识别与 Recovery 重装策略。

源码审查与修复细节：[全局字体/防误触](ROUND4-REVIEW-20261015.md)、[生命周期与边界](ROUND5-REVIEW-20261015.md)、[授权回传](ROUND6-REVIEW-20261016.md)、[快速返回模糊](ROUND7-REVIEW-20261016.md)、[分身签名核验](ROUND8-REVIEW-20261016.md)、[OFRP review2](OFRP-REVIEW-20261016.md)。

## 验证范围

维护者使用 12T Pro。此前已确认全局字体、无锁屏防误触和 eSIM 写入；本批 GMS 新增 QQ 登录与快速返回 UI 的刷入反馈。
**K50 Ultra 仍待对应设备验证**，不能将 12T Pro 的结果视为其指纹等硬件均已通过。
LHDC 仍缺兼容耳机实测；OFRP 的 PIN 解密、各类 USB 模式及扩展场景尚未逐项验收。
上述结果不代表全面硬件、全部 QQ 授权组合或长期稳定性验证完成。

字体替换针对系统默认字体，应用自带字体或图片文字可能保持原样。
使用隐藏模块时仍需让 QQ 能查询发起授权应用的包和签名。GMS 的 Google 认证及 Play Integrity 以实际结果为准。

## 源码与构建

源码清单固定 1187 个基础项目及 3 个可选 GMS 项目，定制通过 89 份有序补丁追加。
本批 ROM 对应的公开源码构建版本为 [`44ec612`](https://github.com/N1-k0-la1/diting-aviumui/tree/44ec6126bb2c74e922eed7b299f0c503d1eedcc0)；后续文档更新不改变该二进制的源码来源。

- [构建说明](BUILD.md) · [补丁顺序与版本](patch-series.json) · [固定上游清单](manifests/default.xml)
- [OFRP review2 对应源码](recovery/orangefox-diting-20261016-review2/README.md)
- [内核源码与命名](KERNEL.md) · [外部组件来源与哈希](external-artifacts.json)
- [Credits](CREDITS.md) · [许可说明](LICENSES.md)

仓库不包含完整 Android checkout。Via APK 和 23 个媒体 ELF 由构建者按固定来源及 SHA256 另行提供。
签名私钥、账号、设备日志及私人源码审查文件不在公开仓库中。

## 历史版本

以下文件仅对应各自历史批次，旧二进制及哈希予以保留：

| 历史批次 | 记录 |
| --- | --- |
| media20261010 GMS / Vanilla | [媒体发布说明](MEDIA-RELEASE.md)、[两版本元数据](MEDIA-VARIANTS.json)、[当时安装说明](INSTALL-MEDIA.md) |
| batch14 及更早批次 | [历史发布说明](HISTORY-RELEASE-BATCH14.md)、[候选元数据](CANDIDATES-BATCH14.json)、[历史根目录清单](MANIFEST.json) |
| 20261010 相机热修复 | [Camera hotfix](CAMERA-HOTFIX.md) |
| OFRP 20261010 bootctrl | [当时安装说明](HISTORY-OFRP-20261010-bootctrl.md)、[源码](recovery/orangefox-diting-20261010-bootctrl/README.md) |
| OFRP review1 | [审查报告](OFRP-REVIEW-20261015.md)、[源码](recovery/orangefox-diting-20261015-review1/README.md) |

## English

Current batch: **round8fix20261016**, with **89 ordered public patches**.
The GMS build is signed, host-qualified and prepared for maintainer distribution. The maintainer reports successful QQ login and correct desktop UI after rapid BACK gestures on 12T Pro after flashing this build.
Vanilla is still being built and has no phone acceptance result for this batch.
OrangeFox review2 is this project's **unofficial stable diting release**: the maintainer repeatedly installed subsequent ROMs with it and confirmed internal storage listing works on 12T Pro.
K50 Ultra, LHDC headset playback and extended Recovery scenarios remain pending. See the current artifact metadata and installation documents above. Older batches are listed only under History.
