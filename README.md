# AviumUI 16.2.2 · diting / ditingp · batch38

基于 Android 16 的非官方定制 ROM，面向 **Xiaomi 12T Pro** 与 **Redmi K50 至尊版（K50 Ultra）**。
维护者：[N1-k0-la1](https://github.com/N1-k0-la1)。本项目独立于 AviumUI、OrangeFox 官方发行。

## 当前版本与成品

当前版本为 **batch38 · 2026-10-26**，公开 **113 份有序补丁**。相对 batch29 的更新见 [本批发布说明](docs/releases/batch38-20261026/README.md)。

| 成品 | 主机验证 | 手机验证范围 |
| --- | --- | --- |
| batch38 GMS · 20261026 attempt1 | 构建、签名、实际镜像、OTA/payload、组件及 Windows 回读通过 | 维护者在 12T Pro 实测，暂未发现问题；逐项结果未由构建端独立确认 |
| batch38 Vanilla · 20261026 attempt1 | 独立构建、签名及相同主机审核通过 | 尚无本批独立手机验收 |
| OrangeFox 20261016-review2 | 沿用原镜像，本批未更新 | 维护者在 12T Pro 多次用其安装项目 ROM，且内部存储显示正常 |

**12T Pro 的结果不能代替 K50 Ultra 验收。** LHDC 缺兼容耳机实测；OFRP PIN 解密与扩展 USB 场景需单独验证。
每版使用其自己的原始 boot；六张配套镜像均取自对应签名产物。其中 recovery.img 是 Avium Recovery。

## 下载与入口

- [batch38 夸克网盘](https://pan.quark.cn/s/84341ea9ed0e?pwd=anJh)，提取码：`anJh`
- 本次暂无 Google Drive 下载。
- [当前文件名与哈希](docs/releases/batch38-20261026/ARTIFACTS.json) · [本批 SHA256](docs/releases/batch38-20261026/SHA256SUMS)
- [ROM 安装](INSTALL.md) · [OFRP 安装](OFRP-INSTALL.md) · [发布说明](RELEASE.md) · [验证记录](VALIDATION.json)
- [构建说明](BUILD.md) · [补丁清单](patch-series.json) · [固定上游](manifests/default.xml)
- [鸣谢](CREDITS.md) · [许可范围](LICENSES.md) · [外部输入](external-artifacts.json) · [内核](KERNEL.md)

batch38 成品已由维护者发布至上述夸克网盘。仓库提供源码补丁、说明和校验记录，不托管完整 ROM；请按完整文件名、SHA256 与随包清单核对批次。

## 本次更新

- 新增双频 Wi-Fi 连接开关：条件满足时同时连接同一网络的 2.4GHz 与 5GHz；默认关闭，不保证普通应用自动叠加带宽。
- 修正 GMS 版本中未设置过的 GMS 开关默认值，保留用户已有选择。
- 改善横屏游戏中从侧边栏打开竖屏应用的小窗布局，统一窗口比例与控制条；修正控制条归属、双窗口切换、无法关闭、重复最近任务和表面残留等问题。
- 修复 Termux 等应用小窗中返回手势无法收起键盘，完善取消手势及迟到动画回调处理。
- 修复最近任务侧滑返回失效，以及隐藏导航条后返回桌面时误触 QQ 底部切页的问题。
- 改善 ZIP 附件等文件跨应用打开时的授权传递，完善安装审批结果与调用者身份处理。
- 完善安装失败时的会话清理和错误提示；设备保护状态作为上下文显示，不把其他安全拒绝武断归因为 FRP，保留原安全检查。
- 修正杜比解码服务的系统接口兼容性，改善小窗切换场景下的检测兼容性。
- 完善用户存储准备失败的诊断分类，保留子进程原始负错误码。

## 功能与明确限制

- 全局系统字体替换支持导入、预览、保存及恢复；应用自带字体和图片文字可能保持原样。
- 保留相机修复、HDR/杜比视界、LHDC V3–V5、QQ 分身授权及按 SKU/固件区域启用的 12T Pro eSIM。格式支持不等于流媒体认证。
- 双频入口：设置 → 网络和互联网 → 互联网 → 网络偏好设置 → 双频 Wi-Fi 连接。已验证过 5GHz 主连接＋2.4GHz 副连接同时联网；不代表所有应用自动分流或单连接带宽叠加。反向主频段、长时与其他无线功能共存仍需验证。
- 隐藏手势条后仍保留底部手势触摸区域，该区域内的应用控件可能受影响。
- 指纹失败计数在同一 HAL 进程内跨会话保留，HAL 进程重启后仍会清零。
- GMS 不保证 Google 认证或 Play Integrity；完整硬件和长期稳定性验证尚未覆盖。

未定位的用户反馈作为待查线索处理，不直接认定为 ROM 缺陷，也不作为已修复项目发布。

## 源码、许可与反馈

固定清单包含 1187 个基础项目及 3 个可选 GMS 项目；113 份补丁覆盖 35 个定制项目。
仓库不包含完整 Android checkout。Via APK 与 23 个媒体 ELF 按固定来源、哈希独立提供，不在仓库分发。
各上游、补丁、Recovery 及专有组件保留各自许可，详见 [LICENSES.md](LICENSES.md)。

刷机可能导致数据丢失或无法启动；按对应安装说明操作。项目按现状提供，各组件适用其许可中的担保条款。
问题请提交到 [Issues](https://github.com/N1-k0-la1/diting-aviumui/issues)，提供机型、完整批次、变体、复现步骤和实际结果。日志请去除账号、设备标识等个人信息；不要提交签名材料、HMA 配置或完整私人日志。

## 历史版本

[batch29 · 20261019](docs/releases/batch29-20261019/README.md) · [round8 / batch27](ROUND8-VARIANTS.json) · [全部历史导航](docs/history/README.md) · [审查记录](docs/reviews/README.md)
历史成品文件名、签名身份和哈希保持原样。

## English

Unofficial AviumUI 16.2.2 / Android 16 for Xiaomi 12T Pro and Redmi K50 Ultra (diting/ditingp).
The current version is **batch38, 2026-10-26**, with **113 ordered patches** across 35 customized projects.
Both GMS and Vanilla passed full builds, signing, OTA/payload, actual-image/component checks and native Windows readback.
The maintainer reports no current problems after testing GMS on 12T Pro; this does not establish Vanilla, K50 Ultra, LHDC-headset or full long-term acceptance.
Changes include opt-in simultaneous dual-band Wi-Fi, unset GMS defaults, floating-window layout/lifecycle/control ownership, IME and navigation gestures, attachment permissions, installer failure handling, Dolby service compatibility and storage diagnostics.
Dual-band connectivity does not automatically aggregate ordinary-app traffic. Unconfirmed reports are investigation leads, not established ROM defects or claimed fixes.
OFRP remains 20261016-review2. Use each variant's own boot and verify exact [artifact hashes](docs/releases/batch38-20261026/ARTIFACTS.json).
Download batch38 from [Quark](https://pan.quark.cn/s/84341ea9ed0e?pwd=anJh), extraction code `anJh`. No Google Drive download is available for this release.
See [Build](BUILD.md), [Install](INSTALL.md), [Licensing](LICENSES.md) and the [documentation index](docs/README.md).
