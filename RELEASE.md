# batch29 · 2026-10-19 · 已发布

发布名称：**AVIUMUI-diting-UNOFFICIAL-261019**。维护者已确认通过酷安发布，两版完整成品已上传网盘。本仓库同步 93 份公开补丁、版本说明和二进制校验记录。

## 下载

- [夸克网盘](https://pan.quark.cn/s/50c002f7af5d?pwd=XTcx)，提取码：`XTcx`
- [Google Drive](https://drive.google.com/drive/folders/16n1umX8_nvy8ADYls8SkH9TVBS_wKAEl?usp=drive_link)

Vanilla / GMS 按需选择，核对完整文件名和 SHA256；每版使用各自对应的原始 boot。刷法见 [ROM 安装](INSTALL.md) 与 [OFRP 安装](OFRP-INSTALL.md)。

## What's new

- 修复 Telegram 等来源 APK 点击后出现两个“Android 系统”、选择后提示无应用可打开的问题。
- 修复 dock 与桌面应用组成文件夹后，拖出应用导致桌面持续模糊。
- 完善指纹 HAL 初始化、失败资源清理、会话同步和回调生命周期；共享同进程按用户锁定状态并衔接定时解除。
- 修复蓝牙开发者选项在设备编解码能力信息缺失时的对话框崩溃。

[文件名、各版原始 boot 与 SHA256](docs/releases/batch29-20261019/ARTIFACTS.json) · [本批校验清单](docs/releases/batch29-20261019/SHA256SUMS)

GMS（20261018 attempt1）与 Vanilla（20261019 attempt2）源于同一冻结输入，分别完成构建、签名、实际镜像及 OTA/payload 审核、组件一致性与 Windows 回读。保持既有签名身份，每版镜像来自自己的 OTA/payload。
维护者在验收清单后反馈 12T Pro GMS 没有问题；Vanilla、K50 Ultra 尚无本批实机验收记录。LHDC 缺设备未测。
指纹 CR-2 只保持同一 HAL 进程内失败计数，重启该进程后仍会清零；CR-3 未改，K50 Ultra 录入失败根因未确认。
OFRP 沿用 20261016-review2，本次没有更新；PIN 解密、扩展 USB 场景和 K50 Ultra 仍需分别验证。

[ROM 安装](INSTALL.md) · [OFRP 安装](OFRP-INSTALL.md) · [详细验证记录](VALIDATION.json) · [历史 round8 清单](ROUND8-VARIANTS.json)
