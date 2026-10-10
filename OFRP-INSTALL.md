# 修正版 OrangeFox：diting / ditingp（公开测试版）

文件：`OrangeFox-diting-ditingp-20261010-bootctrl.img`。

```text
SHA256: 6328c4b97b9ce0cfdf2f064fa40bef11bc5a354122f1e56f3131754804700f61
大小: 104857600 字节
```

**这是 Recovery 镜像，不是 ROM，也不是 KSU boot。** 接受 diting / ditingp 两个设备名；不要用于 raphael、marble 或其他设备。`ditingp` 是本项目 12T Pro 的产品别名，Recovery 的规范目标仍为 diting。

## 验证范围

在本项目 20261010 GMS ROM 的 12T Pro 上验证：启动进入菜单、触摸、灭屏后唤醒触摸、加密存储解密、完整 ROM ZIP 安装、Android 正常开机及虚拟 A/B 快照合并。MTP 在此前内存修补实例验证成功，当前完整 bootctrl 镜像未单独补做电脑存储显示验收。K50 至尊版与 fastbootd 尚未实机验证。

本镜像修复了继承中文字体引用造成的狐狸循环、Goodix 启动/唤醒后触摸异常、缺失 boot HAL VINTF 声明，以及旧 QTI HAL 把 unsuffixed boot 别名算成第三个槽的问题。槽位写入和快照操作保留原 HAL；没有修改触控固件。

**直接在 HyperOS 3.0.6 上启动本镜像尚未验证。** 它没有独立内核，依赖兼容的 boot / vendor_boot。不能用本次在 AviumUI 中成功的结果证明任意原厂系统可直接进入。首次迁入请读 [INSTALL.md](INSTALL.md)，不要把只刷 OFRP 的步骤当成完整 ROM 安装。

## 从当前项目 ROM 安装 OFRP

以下在 Windows **CMD** 运行。准备 Android platform-tools，放置镜像到 `C:\ROM`。手机按音量下 + 电源进入 Bootloader Fastboot，仅连接目标手机。

```bat
"C:\platform-tools\fastboot.exe" devices
```

将所有 `YOUR_SERIAL` 换成第一列的实际序列号，然后检查：

```bat
"C:\platform-tools\fastboot.exe" -s YOUR_SERIAL getvar product
"C:\platform-tools\fastboot.exe" -s YOUR_SERIAL getvar unlocked
"C:\platform-tools\fastboot.exe" -s YOUR_SERIAL getvar is-userspace
certutil -hashfile "C:\ROM\OrangeFox-diting-ditingp-20261010-bootctrl.img" SHA256
```

Bootloader 应报告产品 `diting`、unlocked `yes`、is-userspace `no`；哈希应与上方相同。检查不符就停止。然后刷 Recovery 并进入：

```bat
"C:\platform-tools\fastboot.exe" -s YOUR_SERIAL flash recovery "C:\ROM\OrangeFox-diting-ditingp-20261010-bootctrl.img"
"C:\platform-tools\fastboot.exe" -s YOUR_SERIAL reboot recovery
```

不使用 `fastboot boot`，不把它刷到 Boot，不手动强制切换 A/B 槽位。只安装 Recovery 不需要格式化数据。

进入菜单后测试点击、滑动和灭屏唤醒，再按 INSTALL.md 安装 ROM。ZIP 签名校验可开启：本镜像带有本项目公开 OTA 校验证书；不要关闭校验来绕过未知错误。工具包 ZIP / 源码 ZIP 不是可刷 ZIP。

## ROM 安装后

ROM 可能覆盖 Recovery。先进入新系统、解锁并完成快照合并，然后再按上面的 Fastboot 步骤恢复 OFRP。自动重装 OFRP 未独立验收，本流程使用手动恢复。**不要在首次系统启动前连续重装相同 ROM ZIP**；此情况曾在旧快照处理时出现 EBUSY，但前一次完整安装实际已经成功。

恢复 OFRP 后可以重新进入 Recovery 刷管理器修补的**本批 boot**，镜像目标选 **Boot**；OFRP 镜像目标则选 **Recovery**。不要互换两者，也不要使用旧批 root boot。

官方 OrangeFox 的通用说明提示 A/B ROM 安装可能替换 Recovery，并建议按设备/ROM 专用步骤操作：[Flashing guide](https://wiki.orangefox.tech/guides/flashing)。本项目的首次系统启动和快照合并顺序以这里的实测流程为准。

## 启动失败与备用 Recovery

如果当前项目 ROM 上仍狐狸循环或无法触摸，用音量下 + 电源回到 Fastboot。使用**同批**安装工具包的 Avium Recovery：

```bat
"C:\platform-tools\fastboot.exe" -s YOUR_SERIAL flash recovery "C:\ROM\gms\recovery.img"
"C:\platform-tools\fastboot.exe" -s YOUR_SERIAL reboot recovery
```

上述备用镜像用于当前 media20261010 ROM。原厂 HyperOS 的恢复需要匹配其原系统的材料，不能把这条当成通用 HyperOS 修复。不清数据来试探触摸/启动问题；保存日志后反馈。

## 源码与鸣谢

对应源码、405 项固定清单及重建验证在 GitHub 的 `recovery/orangefox-diting-20261010-bootctrl/`，或随附 `OrangeFox-diting-ditingp-20261010-bootctrl-source.zip`。源码 ZIP 不可在 Recovery 直接刷入。

感谢 OrangeFox、TeamWin、AOSP、AviderMin 的 diting 设备树、Xiaomi / Qualcomm 以及上游贡献者。非 OrangeFox 官方发布。保留上游 GPL / Apache 许可与硬件组件权利声明。

## English

Unofficial **testing** Recovery for diting / ditingp, tested on the project's media20261010 GMS ROM / 12T Pro. Menu, touch, screen-wake touch, FBE decryption, full OTA installation, Android boot and snapshot merge passed. K50 Ultra, fastbootd and direct HyperOS 3.0.6 boot are not qualified. The current complete image's MTP display check has not been repeated; earlier RAM tests passed.

The image fixes the missing Chinese font, guarded Goodix startup/wake recovery, boot HAL manifest and legacy slot counting. It has no standalone kernel and requires compatible boot/vendor_boot. In CMD, verify the target serial, unlocked diting Bootloader mode and the image SHA256, then use the `flash recovery` / `reboot recovery` commands above. Do not use fastboot boot, flash it to Boot, force slots or format data just to install Recovery.

For a ROM install, follow INSTALL.md. Boot Android and complete snapshot merge before another OTA or root; reinstall this Recovery manually afterwards if the ROM replaced it. Automatic OrangeFox restoration is not qualified. Patched boot must match this ROM and go to Boot; this image goes to Recovery. The matching Avium Recovery is a fallback for this project ROM, not a universal stock-firmware repair.

Corresponding source and exact reconstruction evidence are supplied separately. The source/package archives are **not flashable ZIPs**. Credit OrangeFox, TeamWin, AOSP, AviderMin, Xiaomi/Qualcomm and all upstream contributors; retain their licenses.
