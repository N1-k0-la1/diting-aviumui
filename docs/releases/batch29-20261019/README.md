# batch29 · 2026-10-19

适用 Xiaomi 12T Pro / Redmi K50 Ultra（diting / ditingp），AviumUI 16.2.2 / Android 16。

- 修复 Telegram 等来源 APK 打开时出现两个“Android 系统”并无法安装的问题。
- 修复 dock 应用与桌面应用组成文件夹后，拖出应用导致桌面模糊残留。
- 修复指纹 HAL 初始化、失败清理、会话同步及对象生命周期，按用户共享同进程锁定计数并衔接定时解除。
- 修复蓝牙开发者选项在编解码能力缺失时的对话框崩溃。

GMS 为 2026-10-18 attempt1，Vanilla 为 2026-10-19 attempt2；两版同一源码冻结，保留各自真实文件名、日期和哈希。
均完成整包构建、发布签名、实际镜像/OTA/payload、组件一致性及 Windows 回读。维护者在 batch29 验收后反馈 12T Pro GMS 没有问题；逐项结果未独立记录。
Vanilla、K50 Ultra 尚无本批实机验收记录，LHDC 缺少对应耳机未测。CR-2 的失败计数在 HAL 进程重启后仍会清零；CR-3 未改，K50U 录入失败根因未确认。

[两版完整文件清单](ARTIFACTS.json) · [本批二进制校验值](SHA256SUMS) · [ROM 安装](../../../INSTALL.md) · [OFRP 安装](../../../OFRP-INSTALL.md)

每版 boot 与另外五张配套镜像均来自自己的已签名 OTA/payload；原始 boot 未经 root 修补。不要混用变体、旧 boot 或旧修补镜像。
OFRP 沿用 20261016-review2，本批没有重编或更新。recovery.img 是 ROM 配套的 Avium Recovery。
完整 ROM 由维护者通过网盘分发；本记录尚未确认网盘上传完成。仓库仅更新源码、说明和校验记录。
