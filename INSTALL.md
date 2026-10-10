# AviumUI 16.2.2 diting：20261010 GMS 安装说明

本页对应 `AviumUI-16.2.2-diting-gms-user-media20261010.zip`，含相机视频切换修复、LHDC 和杜比视界视频组件。旧 batch14 Vanilla 不含本批更新。手机须已解锁 Bootloader，安装后不要重新锁定。

**已验证组合：Xiaomi 12T Pro + 本项目 ROM + 修正版 OrangeFox。** 完整 ZIP 安装、系统开机和虚拟 A/B 快照合并通过；K50 至尊版、本版直接从 HyperOS 3.0.6 迁入尚未实测。已有 HyperOS 3.0.6 用户报告配套 Recovery 无法操作、黑屏重启，但是否刷全六镜像未知，原因未确认。遇到这种情况不要清数据或继续安装，先保存报错、使用原系统的匹配恢复材料恢复，不要认为更换 OFRP 就一定能解决。

## 准备文件和电脑

下载完整 ROM ZIP（不解压）及同批 `AviumUI-16.2.2-diting-gms-install-kit-media20261010.zip`（解压）。使用 Android platform-tools 中的全部文件。核对随附 SHA256SUMS；只连接目标手机，备份重要资料。

示例文件位置如下；若使用其他目录，请修改命令中的路径：

```text
C:\platform-tools\adb.exe
C:\platform-tools\fastboot.exe
C:\ROM\AviumUI-16.2.2-diting-gms-user-media20261010.zip
C:\ROM\Install-Recovery.ps1
C:\ROM\MANIFEST.json
C:\ROM\gms\boot.img
C:\ROM\gms\dtbo.img
C:\ROM\gms\vendor_boot.img
C:\ROM\gms\recovery.img
C:\ROM\gms\vbmeta.img
C:\ROM\gms\vbmeta_system.img
```

**下面的电脑命令全部在 CMD（命令提示符）运行。** 不要添加 PowerShell 的 `&`。`powershell.exe ...` 这两条也直接从 CMD 执行；它们会自行启动 PowerShell，不需要更改系统执行策略。

## A. 已在本项目 ROM 中：用修正版 OFRP 安装更新

1. 确认上一轮更新已完成首次系统启动；不要在待合并的更新上连续重装 ZIP。备份数据，先处理与更新不兼容的 root 模块。保数据兼容性与长期稳定性没有全面保证。
2. 使用本次提供的 `OrangeFox-diting-ditingp-20261010-bootctrl.img`，安装方式见 [OFRP-INSTALL.md](OFRP-INSTALL.md)。只更新 Recovery 不需要格式化数据。
3. 进入 OFRP，确认界面、触摸正常，内部存储可见。将完整 ROM ZIP 放到手机存储或 OTG；如果需要，电脑可用 MTP 复制。点击“文件”，选完整 ROM ZIP，滑动安装。**解压后的文件、源码 ZIP 和工具包 ZIP 都不能作为 ROM 刷入。**
4. ZIP 签名校验可开启：本 OFRP 包含本项目公开 OTA 证书。不要启用“禁用加密/DM-Verity”等附加修改；自动重装 OFRP 未列入验收，本流程不依赖它。
5. 必须看 Recovery 是否明确安装成功，不能只看百分比。成功后先“重启 → 系统”，解锁并让后台完成快照合并，再考虑 root 或另一轮安装。**不要手动切换 A/B 槽位，不要在首次系统启动前反复安装同一 ZIP。**
6. ROM 安装可能替换 OFRP；系统启动、合并完成后，可按 OFRP-INSTALL.md 再刷回修正版 Recovery。root 请使用本批 `gms/boot.img` 在管理器中修补，再刷到 Boot；不要用旧批次 boot。

本次实机日志明确 `Merge finished with state MergeCompleted.` 和 `CleanupPreviousUpdateAction ... kSuccess`。如需检查，可在系统已开启 USB 调试后，使用你自己的序列号运行：

```bat
"C:\platform-tools\adb.exe" -s YOUR_SERIAL logcat -b all -d -s update_engine > "C:\ROM\update-merge.txt"
findstr /C:"Merge finished with state MergeCompleted" /C:"CleanupPreviousUpdateAction with code ErrorCode::kSuccess" "C:\ROM\update-merge.txt"
```

`YOUR_SERIAL` 必须替换成你的目标序列号。日志没有这些行时不能仅凭等待时间认定合并完成；保存日志询问维护者，不要删除 `/metadata/ota` 或 COW 快照文件。

## B. 其他系统首次迁入：使用同批 Avium Recovery 配套镜像

该流程会清除用户资料。HyperOS 3.0.6 的 Recovery 启动报告尚未复核；此来源暂不算已验证路径。**不能在未知兼容性的原厂 boot/vendor_boot 上只替换 OFRP 就保证可用**：本 OFRP 不带独立内核，依赖兼容的启动镜像。

### 1. Fastboot 中确认手机

备份完成后，关机，按音量下 + 电源进入 Bootloader Fastboot。

```bat
"C:\platform-tools\fastboot.exe" devices
```

记下目标手机序列号，将下面全部 `YOUR_SERIAL` 替换为它。没有设备输出时先处理驱动、线材和接口。Recovery 中出现 `ditingp` 是本项目的产品别名，并不等于刷错设备；Bootloader 的产品检查沿用硬件名称 `diting`。

### 2. 核对文件，再刷六个配套镜像

先只读检查文件哈希、解锁状态、Bootloader 模式和槽位分区：

```bat
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\ROM\Install-Recovery.ps1" -Serial YOUR_SERIAL -Flavour gms -FastbootPath "C:\platform-tools\fastboot.exe"
```

看到 `Verified ... No flash, erase or reboot performed.` 后，执行写入：

```bat
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\ROM\Install-Recovery.ps1" -Serial YOUR_SERIAL -Flavour gms -FastbootPath "C:\platform-tools\fastboot.exe" -FlashRecovery
```

脚本刷入同批 boot、dtbo、vendor_boot、recovery、vbmeta、vbmeta_system，然后进入 Avium Recovery；此时完整 ROM 还没安装。不要启动旧系统，也不要混用旧批镜像。若 Recovery 黑屏、重启或触摸不能操作，停止并保存故障信息，不要继续清数据。

### 3. 清数据并安装完整 ROM

确认 Avium Recovery 可正常操作后，在手机选 **Factory reset → Format data/factory reset**。这一步删除用户资料和内部存储；先完成备份。若有删除 eSIM profile 的选项，不选；不要擦除 persist、modemst 或手动擦除 system/vendor。

返回主菜单，选 **Apply update → Apply from ADB**，等待接收，再从 CMD 运行：

```bat
"C:\platform-tools\adb.exe" -s YOUR_SERIAL sideload "C:\ROM\AviumUI-16.2.2-diting-gms-user-media20261010.zip"
```

以手机显示安装完成为准。电脑约 47% 结束本身不能判断成败；安装失败时保存手机提示和电脑输出，停在 Recovery，不绕过校验。

### 4. 正常启动后再装 OFRP / root

安装成功后在手机选 **Reboot system now**。首次启动较慢；不手动切换槽位。进入系统，检查相机、SIM/eSIM、Wi-Fi、音频和指纹，并核对移动数据/漫游费用设置。GMS 在系统自带设置里开启。等待本轮快照合并完成后再安装 OFRP 或匹配的 patched boot，具体见 A 节。

## 错误反馈

提供手机型号、原系统及版本、ROM 文件名、Recovery 名称/版本、是否刷全六镜像，以及错误之前和之后的完整文字。能进 Recovery 且 ADB 可用时，在**重启之前**保存安装日志：

```bat
"C:\platform-tools\adb.exe" -s YOUR_SERIAL pull /tmp/recovery.log "C:\ROM\recovery.log"
```

日志可能含个人信息，请私下提供，公开前删去标识。`Error 7`、黑屏、狐狸循环有多种原因，不能仅凭一句“安装失败”认定 ROM 有问题；本次重复安装的快照冲突也不等同于首次安装失败。

## English

This guide applies to the full **media20261010 GMS** OTA and matching six-image install kit. The old batch14 Vanilla release does not include these media changes. The tested combination is a 12T Pro running the project ROM with the corrected project OrangeFox. Full OTA installation, Android boot and snapshot merge passed. K50 Ultra and direct migration from HyperOS 3.0.6 remain unqualified; one HyperOS 3.0.6 user reported an unusable recovery, black screen and reboot, with the exact six-image flashing steps unknown.

All Windows commands above are **CMD** commands. Replace YOUR_SERIAL and paths with your own. Keep the bootloader unlocked. Check hashes and back up first. On the existing project ROM, use the separately supplied tested OrangeFox image, select the unchanged full OTA ZIP and require an explicit successful result. Boot Android and complete snapshot merging before another install or root. Do not force a slot or delete OTA metadata/COW files.

For migration from another OS, use the matching Avium Recovery kit: run the installer without -FlashRecovery to verify, then with that switch to flash all six images. If recovery is unusable, stop before formatting. Once usable and backed up, select Factory reset → Format data/factory reset, then Apply update → Apply from ADB, and sideload the full OTA. This deletes user data; retain eSIM profiles and do not erase persist/modemst. Require the phone's success message, boot Android, then complete snapshot merging. Restore OrangeFox separately afterwards if desired. Root must use this ROM's matching boot image. Long-term and retained-data compatibility are not guaranteed.

For recovery errors, include the original OS, exact package/recovery versions, all six-image flashing steps and the complete error. Save /tmp/recovery.log before rebooting when ADB is available. The project's image has no standalone kernel and is not claimed compatible with arbitrary stock boot/vendor_boot firmware.
