# 测试版安装与恢复 / Installation

面向已解锁 Bootloader、具备备份和 Fastboot 恢复能力的 diting 测试用户。只连接要刷的一台设备。K50 至尊版尚未实测，愿意承担实验性测试的志愿者才使用。使用近期 Android platform-tools。

1. 备份应用、文件和重要资料；干净安装将清空内部存储及 root 模块配置。不要删除 eSIM profile，不擦除 persist／modemst，不重新锁定 Bootloader。
2. 下载本目录对应完整 OTA、同 flavour 的六个 `.img`、`MANIFEST.json`、`Install-Recovery.ps1`；保留目录结构。用 `SHA256SUMS` 核对下载，脚本也会检查选定 OTA 和镜像 SHA256。
3. 手机手动进入 bootloader Fastboot。下方 Windows 命令中的序列号由你在本机查看并填写，不要把维护者的序列号或槽位当成自己的。

```powershell
fastboot devices
# 只连接一台目标手机；记下它的序列号。工具不在 PATH 时，用实际 fastboot.exe 路径。
# 从本发布目录运行，替换 YOUR_SERIAL。Flavour 选 gms 或 vanilla。
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Install-Recovery.ps1 -Serial YOUR_SERIAL -Flavour gms -FastbootPath 'C:\platform-tools\fastboot.exe'
```

默认只做文件／设备／当前槽位／容量检查。检查通过后，加 `-FlashRecovery` 才写入六个匹配镜像并请求进入 Recovery：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Install-Recovery.ps1 -Serial YOUR_SERIAL -Flavour gms -FastbootPath 'C:\platform-tools\fastboot.exe' -FlashRecovery
```

任何报错立即停，不继续后续步骤。不要在完整 OTA 安装前启动旧系统；新内核和模块不能只换其中一部分。

4. 在配套 AviumUI Recovery 选择 **Factory reset → Format data/factory reset**，确认清数据。若出现删除 eSIM 的选项，不勾选。
5. 返回，选择 **Apply update → Apply from ADB**。从发布目录传入同版本 OTA；根据所选 flavour 只运行对应一条：

```powershell
adb -s YOUR_SERIAL sideload .\AviumUI-16.2.2-diting-gms-user-batch14.zip
# 或 Vanilla：
# adb -s YOUR_SERIAL sideload .\AviumUI-16.2.2-diting-vanilla-user-batch14.zip
```

6. 以 Recovery 明确显示 **Install completed** 为成功依据；不要只看电脑传输百分比。失败停在 Recovery，保存错误信息。
7. 成功后选 **Reboot system now**。A/B OTA 会自行选择安装槽位，**不要强制切回原槽**。首次启动可能较慢。
8. 清数据可能重置网络开关；如有流量费用限制，提前处理运营商数据限制，或在首次启动后及时检查移动数据／漫游。使用 Wi-Fi 完成设置。GMS 版需在系统中开启“启用GMS服务”。

当前不承诺脏刷、保数据切换两种 flavour、外部 root 模块兼容或无风险降级。首次验收先保持纯 ROM，之后再单独测试 root／模块。

## 出错与恢复

不盲目重复刷写，不修改 eSIM／persist／modemst，不重新锁定 BL。当前槽位或设备检查报错时，保留现状并提供非私密错误文本。能进入 Fastboot 时，可重新核对后刷入匹配的整套启动镜像，进入配套 Recovery 再安装匹配完整包。`gms/boot.img` 和 `vanilla/boot.img` 都是对应原始 boot，可用于回退同版本 root 修改；若 root 方法同时改了其他镜像，应按其实际改动恢复。

不提供抹除全部分区或未经验证的厂商固件降级命令。完整包签名由维护者私钥生成，Recovery 使用匹配信任锚；签名失败不应直接选择绕过验证。

## English

Back up before a clean install: formatting erases internal storage and root-module data. Use one unlocked diting in bootloader Fastboot, its own serial, current platform-tools and exactly one flavour's full OTA plus six images. The supplied PowerShell script defaults to verification only; add `-FlashRecovery` to flash the current slot and enter the matching Recovery. It never formats data, sideloads an OTA, changes the slot or relocks the bootloader.

In Recovery, format data without deleting eSIM profiles, select Apply update → Apply from ADB, sideload the matching OTA, require the Recovery success message, then reboot system without forcing a slot. Check mobile-data/roaming costs after a reset. Enable the GMS preference for that flavour. Stop on errors; never erase persist/modemst or relock the bootloader. Full-GMS/Vanilla switching and third-party root compatibility are not guaranteed.
