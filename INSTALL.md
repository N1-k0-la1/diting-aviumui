# AviumUI 16.2.2 diting：media20261010 GMS / Vanilla 安装说明

本批 GMS / Vanilla 都包含相机视频切换修复、LHDC 和杜比视界视频组件。GMS 集成 Google 服务；Vanilla 不含 Google 服务。两包均为 user/release-keys、无内置 root。旧 batch14 Vanilla 不含本批更新。手机须已解锁 Bootloader，安装后不要重新锁定。

| 版本 | 完整 ROM ZIP（不可解压） | 配套工具包（需电脑解压） |
| --- | --- | --- |
| GMS | AviumUI-16.2.2-diting-gms-user-media20261010.zip | AviumUI-16.2.2-diting-gms-install-kit-media20261010.zip |
| Vanilla | AviumUI-16.2.2-diting-vanilla-user-media20261010.zip | AviumUI-16.2.2-diting-vanilla-install-kit-media20261010.zip |

下面文件布局以 GMS 举例；Vanilla 的镜像目录为 `vanilla/`。下载所选版本的完整 ZIP、工具包，以及下述 OFRP 镜像。不要混用 GMS / Vanilla 启动镜像。

**已验证组合：Xiaomi 12T Pro + 本项目 ROM + 修正版 OrangeFox。** 完整 ZIP 安装、系统开机和虚拟 A/B 快照合并通过；新 Vanilla 已通过构建/签名/OTA/镜像检查，但尚未刷入实机。K50 至尊版、本版直接从 HyperOS 3.0.6 迁入尚未实测。已有 HyperOS 3.0.6 用户报告配套 Recovery 无法操作、黑屏重启，但是否刷全六镜像未知，原因未确认。遇到这种情况不要清数据或继续安装，先保存报错、使用原系统的匹配恢复材料恢复，不要认为更换 OFRP 就一定能解决。

## 准备文件和电脑

按上表选择一个版本，下载完整 ROM ZIP（不解压）及其同批工具包（解压）。另外下载本项目的 `OrangeFox-diting-ditingp-20261010-bootctrl.img`（无需解压）。使用 Android platform-tools 中的全部文件。核对随附 SHA256SUMS；只连接目标手机，备份重要资料。

示例文件位置如下；若使用其他目录，请修改命令中的路径：

从本仓库取当前的 [Install-Recovery.ps1](Install-Recovery.ps1) 和 [CANDIDATES.json](CANDIDATES.json) 放到 `C:\ROM`。旧工具包内的脚本可能没有 `-ManifestPath` 参数；请使用当前脚本，镜像仍取所选版本的同批工具包，不修改旧工具包 ZIP。

```text
C:\platform-tools\adb.exe
C:\platform-tools\fastboot.exe
C:\ROM\AviumUI-16.2.2-diting-gms-user-media20261010.zip
C:\ROM\OrangeFox-diting-ditingp-20261010-bootctrl.img
C:\ROM\Install-Recovery.ps1
C:\ROM\CANDIDATES.json
C:\ROM\gms\boot.img
C:\ROM\gms\dtbo.img
C:\ROM\gms\vendor_boot.img
C:\ROM\gms\recovery.img
C:\ROM\gms\vbmeta.img
C:\ROM\gms\vbmeta_system.img
```

**下面的电脑命令全部在 CMD（命令提示符）运行。** 不要添加 PowerShell 的 `&`。`powershell.exe ...` 也直接从 CMD 执行；它们会自行启动 PowerShell，不需要更改系统执行策略。

**Vanilla ↔ GMS 的保数据切换未验证**；切换版本按迁移/重装准备完整备份，不能把同版本更新的结果直接套用。

## A. 已在本项目 ROM 中：用修正版 OFRP 安装更新

1. 确认上一轮更新已完成首次系统启动；不要在待合并的更新上连续重装 ZIP。备份数据，先处理与更新不兼容的 root 模块。保数据兼容性与长期稳定性没有全面保证。
2. 使用本次提供的 `OrangeFox-diting-ditingp-20261010-bootctrl.img`，安装方式见 [OFRP-INSTALL.md](OFRP-INSTALL.md)。只更新 Recovery 不需要格式化数据。
3. 进入 OFRP，确认界面、触摸正常，内部存储可见。将完整 ROM ZIP 放到手机存储或 OTG；如果需要，电脑可用 MTP 复制。点击“文件”，选完整 ROM ZIP，滑动安装。**解压后的文件、源码 ZIP 和工具包 ZIP 都不能作为 ROM 刷入。**
4. ZIP 签名校验可开启：本 OFRP 包含本项目公开 OTA 证书。不要启用“禁用加密/DM-Verity”等附加修改；自动重装 OFRP 未列入验收，本流程不依赖它。
5. 必须看 Recovery 是否明确安装成功，不能只看百分比。成功后先“重启 → 系统”，解锁并让后台完成快照合并，再考虑 root 或另一轮安装。**不要手动切换 A/B 槽位，不要在首次系统启动前反复安装同一 ZIP。**
6. ROM 安装可能替换 OFRP；系统启动、合并完成后，可按 OFRP-INSTALL.md 再刷回修正版 Recovery。root 请使用所选版本的本批 `gms/boot.img` 或 `vanilla/boot.img` 在管理器中修补，再刷到 Boot；不要用旧批次 boot。

本次实机日志明确 `Merge finished with state MergeCompleted.` 和 `CleanupPreviousUpdateAction ... kSuccess`。如需检查，可在系统已开启 USB 调试后，使用你自己的序列号运行：

```bat
"C:\platform-tools\adb.exe" -s YOUR_SERIAL logcat -b all -d -s update_engine > "C:\ROM\update-merge.txt"
findstr /C:"Merge finished with state MergeCompleted" /C:"CleanupPreviousUpdateAction with code ErrorCode::kSuccess" "C:\ROM\update-merge.txt"
```

`YOUR_SERIAL` 必须替换成你的目标序列号。日志没有这些行时不能仅凭等待时间认定合并完成；保存日志询问维护者，不要删除 `/metadata/ota` 或 COW 快照文件。

## B. 其他系统首次迁入：配套启动镜像 + 本项目 OFRP

该流程会清除用户资料。先在原系统正常启动并完成尚未结束的系统更新，再备份。HyperOS 3.0.6 直接迁入尚未实测。**首次迁入不能只刷 OFRP**：本镜像没有独立内核，需要同批 boot / dtbo / vendor_boot 等配套镜像。下面使用工具包里的五个启动镜像，以及单独下载的本项目 OFRP；工具包里的 `recovery.img` 只作备用。

### 1. Fastboot 中确认手机，选择版本

备份完成后，关机，按音量下 + 电源进入 Bootloader Fastboot。

```bat
"C:\platform-tools\fastboot.exe" devices
```

记下目标手机序列号，将下面全部 `YOUR_SERIAL` 替换为它。在 CMD 设置版本变量，**只执行与你下载版本对应的一条**：

GMS：

```bat
set "ROM_FLAVOUR=gms"
```

Vanilla：

```bat
set "ROM_FLAVOUR=vanilla"
```

后面 `%ROM_FLAVOUR%` 会展开为所选版本；新开 CMD 后要重新设置。没有设备输出时先处理驱动、线材和接口。Recovery 中的 `ditingp` 是本项目的产品别名；Bootloader 产品检查沿用硬件名称 `diting`。

### 2. 只读核对工具包、完整 ROM 和 OFRP

将完整 ROM ZIP 放在 `C:\ROM`，与解压后的脚本和 CANDIDATES.json 同级，运行：

```bat
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\ROM\Install-Recovery.ps1" -Serial YOUR_SERIAL -Flavour %ROM_FLAVOUR% -ManifestPath CANDIDATES.json -FastbootPath "C:\platform-tools\fastboot.exe"
```

必须看到 `Verified ... No flash, erase or reboot performed.`。这一步校验所选 ROM、工具包六镜像、解锁状态、Bootloader 模式和当前槽位分区；**此处不加 `-FlashRecovery`**，该旧开关会安装工具包里的 Avium Recovery。

另外校验单独下载的 OFRP：

```bat
certutil -hashfile "C:\ROM\OrangeFox-diting-ditingp-20261010-bootctrl.img" SHA256
```

必须与以下值一致：

```text
6328c4b97b9ce0cfdf2f064fa40bef11bc5a354122f1e56f3131754804700f61
```

检查失败就停止，重新核对文件，不绕过校验。

### 3. 刷五个配套启动镜像和 OFRP

**逐条执行并检查结果：每条都应显示 OKAY；出现 FAILED、报错或超时就停止，不继续后面的命令。** 手机保持同一 Fastboot 会话，不拔线、不切槽位。这些命令使用当前槽位，不指定 `_a` / `_b`。

```bat
"C:\platform-tools\fastboot.exe" -s YOUR_SERIAL flash boot "C:\ROM\%ROM_FLAVOUR%\boot.img"
"C:\platform-tools\fastboot.exe" -s YOUR_SERIAL flash dtbo "C:\ROM\%ROM_FLAVOUR%\dtbo.img"
"C:\platform-tools\fastboot.exe" -s YOUR_SERIAL flash vendor_boot "C:\ROM\%ROM_FLAVOUR%\vendor_boot.img"
"C:\platform-tools\fastboot.exe" -s YOUR_SERIAL flash recovery "C:\ROM\OrangeFox-diting-ditingp-20261010-bootctrl.img"
"C:\platform-tools\fastboot.exe" -s YOUR_SERIAL flash vbmeta "C:\ROM\%ROM_FLAVOUR%\vbmeta.img"
"C:\platform-tools\fastboot.exe" -s YOUR_SERIAL flash vbmeta_system "C:\ROM\%ROM_FLAVOUR%\vbmeta_system.img"
"C:\platform-tools\fastboot.exe" -s YOUR_SERIAL reboot recovery
```

现在应进入 OrangeFox。**完整 ROM 此时还未安装，不启动旧系统。** 先确认菜单、点击、滑动和灭屏唤醒正常。若黑屏、狐狸循环或触摸失效，停止，不清数据；保存故障信息后用匹配原系统的恢复材料处理。

### 4. 格式化 Data，再安装完整 ROM ZIP

1. 在 OFRP 的清除页面找到 **Format Data / 格式化数据**，输入 `yes` 确认。不是仅勾选 Data 的普通清除。这会删除应用、资料和内部存储；必须事先备份。不选删除 eSIM profile，不擦除 persist、modemst，也不手动擦除 system / vendor。
2. 格式化成功后选择 **重启 → Recovery**，重新进入 OFRP，再传入完整 ROM。若内部存储可见，可用 MTP 复制；也可用 OTG。
3. 在“文件”中选择完整 `AviumUI-16.2.2-diting-所选版本-user-media20261010.zip`，滑动安装。ZIP 签名校验可以开启，不启用“禁用加密 / DM-Verity”或自动重装 OFRP。工具包 ZIP、源码 ZIP 都不能当 ROM 刷入。
4. 若不用 MTP / OTG，在 OFRP 菜单找到 **ADB Sideload / ADB 侧载**，滑动开始接收，再在 CMD 执行下方命令。

```bat
"C:\platform-tools\adb.exe" -s YOUR_SERIAL sideload "C:\ROM\AviumUI-16.2.2-diting-%ROM_FLAVOUR%-user-media20261010.zip"
```

两种传输方式任选其一，不重复安装。以手机明确显示安装成功为准；电脑约 47% 结束本身不能判断成败。安装失败时保存完整提示和日志，停在 Recovery，不绕过校验或反复重刷。

### 5. 先启动系统，再恢复 OFRP / root

安装成功后选择 **重启 → 系统**。首次启动较慢，不手动切槽位。检查相机、SIM/eSIM、Wi-Fi、音频和指纹，并核对移动数据/漫游费用设置。GMS 版在系统自带设置里开启 Google 服务；Vanilla 不预装 GMS。

先完成首次系统启动与快照合并，再按 A 节检查日志、恢复 OFRP 或刷匹配 patched boot。**不要刚刷完 ROM 就再次安装 ZIP 或立即刷 root。** ROM 可能把 OFRP 替换为自带 Recovery，这是预期行为；完成上述步骤后再刷回本项目 OFRP。

本项目采用已验证的“安装 → 系统启动 / 合并 → 恢复 OFRP / root”顺序。[OrangeFox 官方通用指南](https://wiki.orangefox.tech/guides/flashing)也建议 A/B 设备遵循设备/ROM 专用流程；不要套用其他设备的槽位切换或重刷步骤。本流程从其他系统首次迁入仍需测试者反馈，不能把现有 GMS 上更新成功视为所有原厂版本迁移已通过。

## Vanilla 可选 microG / MIRA

Vanilla 不内置 microG。若自行安装 microG 并使用 MIRA + Kasumi 挂载，此前旧版 MIRA 在本设备上因不存在的 Volla 路径替换标记导致挂载失败、Play 商店闪退。可参考 [MIRA-KASUMI.md](MIRA-KASUMI.md) 及附带的非官方兼容预览；该预览此前已实测商店可打开，新 Vanilla 上仍需自行验收。它不是刷 ROM 的必需项，不保证 Play Integrity。

## 错误反馈

提供手机型号、原系统及版本、ROM 文件名、Recovery 名称/版本、是否刷全六镜像，以及错误之前和之后的完整文字。能进 Recovery 且 ADB 可用时，在**重启之前**保存安装日志：

```bat
"C:\platform-tools\adb.exe" -s YOUR_SERIAL pull /tmp/recovery.log "C:\ROM\recovery.log"
```

日志可能含个人信息，请私下提供，公开前删去标识。`Error 7`、黑屏、狐狸循环有多种原因，不能仅凭一句“安装失败”认定 ROM 有问题；本次重复安装的快照冲突也不等同于首次安装失败。

## English

These instructions use the project OrangeFox as the primary recovery for both media20261010 flavours. Download one unchanged full ROM ZIP, its matching install kit (extract on the PC), and the separate OrangeFox-diting-ditingp-20261010-bootctrl.img. Keep the bootloader unlocked. All commands above are Windows CMD commands; replace YOUR_SERIAL and paths, and select exactly one ROM_FLAVOUR value.

For updates on the existing project ROM, use section A. For migration from another OS, back up and complete any pending update in the original OS first. Use section B: run the kit installer WITHOUT -FlashRecovery for read-only ROM/image/device checks, then verify the separate OFRP hash. Execute each flash command individually, checking OKAY and stopping on any failure. Flash the five matching boot/dtbo/vendor_boot/vbmeta/vbmeta_system images plus our OFRP as recovery; reboot directly to recovery. The old -FlashRecovery switch installs bundled Avium Recovery and is not this guide's primary installation route.

Once OrangeFox boots with working touch, Format Data (type yes; this erases internal storage), reboot recovery, then install the full ROM ZIP through Files using MTP/OTG, or use ADB Sideload and the command above. Do not erase persist/modemst, manually wipe system/vendor, disable encryption/verity, or force slots. Preserve eSIM profiles. Require an explicit installation success on the phone. Boot Android and complete snapshot merging before another install, restoring OFRP or root. The ROM may replace OFRP; restore it only after that first boot and merge. Use this flavour's matching boot image for root.

Full OTA installation, Android boot and snapshot merge passed on the project GMS ROM / 12T Pro. New Vanilla passed host audits but is not phone-tested; K50 Ultra, retained-data flavour switching and direct HyperOS 3.0.6 migration remain unverified. OFRP has no standalone kernel: flashing it alone on arbitrary stock boot/vendor_boot is not a qualified migration. Stop before formatting if recovery is unusable. Save /tmp/recovery.log before reboot when reporting an error. Avium Recovery in the kit remains a fallback described in OFRP-INSTALL.md.

安装脚本默认使用历史 `MANIFEST.json`；本页 media20261010 资产请按上方命令显式选择 `CANDIDATES.json`，避免混用不同批次镜像。所有资产均在写入前核对大小及 SHA256。
