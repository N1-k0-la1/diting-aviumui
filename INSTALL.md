# 当前 20261010 GMS 媒体版

本批请先读 [INSTALL-MEDIA.md](INSTALL-MEDIA.md)，下载 media20261010 的完整 ZIP 与同批六镜像。
下方列出的 batch14 文件和工具包仅用于旧版。不要混用新旧 boot / vendor_boot / recovery。
For media20261010, follow INSTALL-MEDIA.md. The batch14 filenames below are historical.
---

# Windows 刷机教程：AviumUI 16.2.2 diting 测试版

本文讲完整 ROM 的首次安装／重装，会清空手机内部存储。**已装好 ROM、只想刷 root 的用户不要重走本流程，不要清数据；使用当前版本的原始 boot 在所用 root 管理器中修补即可。**

当前 12T Pro GMS 已完成基础实测；Vanilla 第十四批与 K50 至尊版尚未实测。安装需要已解锁 Bootloader，只连接一台目标手机。不要重新锁定 Bootloader。

## 先弄清三个步骤

1. 电脑通过 Fastboot 刷入六个启动／Recovery 镜像，手机进入 AviumUI Recovery。
2. 在手机 Recovery 清数据，再选择接收 ADB 更新。
3. 电脑把完整 ROM ZIP 传给 Recovery 安装，成功后手机启动系统。

**第 1 步完成不代表 ROM 已装完。完整系统在第 3 步的 ZIP 里。**
Fastboot 时用 fastboot 工具；Recovery 的 ADB 更新模式用 adb 工具；不要在 Fastboot 下用 adb 安装 APK。

## 1. 下载两个文件

先选一个版本，只下载同一版本的两份文件：

| 版本 | 完整 ROM（保持 ZIP，不解压） | 配套工具包（需要解压） |
| --- | --- | --- |
| GMS | AviumUI-16.2.2-diting-gms-user-batch14.zip | AviumUI-16.2.2-diting-gms-install-kit.zip |
| Vanilla | AviumUI-16.2.2-diting-vanilla-user-batch14.zip | AviumUI-16.2.2-diting-vanilla-install-kit.zip |

GMS 带 Google 服务和商店；Vanilla 不带。六个镜像都在工具包里，不需要自己从 ROM 解压。工具包不含 adb／fastboot，请另外准备 Android platform-tools。

## 2. 摆好电脑上的文件

下面为方便复制，统一假设刷机文件在 **C:\ROM**，platform-tools 在 **C:\platform-tools**。没有这些目录就创建／放到这些位置；使用其他位置时改后面两项变量。

解压工具包到 C:\ROM，再把完整 ROM ZIP 复制到同一目录。以 GMS 为例，正确结构是：

```text
C:\ROM\
  AviumUI-16.2.2-diting-gms-user-batch14.zip
  Install-Recovery.ps1
  MANIFEST.json
  SHA256SUMS
  INSTALL.md
  gms\
    boot.img
    dtbo.img
    vendor_boot.img
    recovery.img
    vbmeta.img
    vbmeta_system.img

C:\platform-tools\
  adb.exe
  fastboot.exe
  （以及 platform-tools 压缩包中的其他文件）
```

若解压后多了一层文件夹，请打开到能看见 Install-Recovery.ps1 的那层，把后面的 `$RomDir` 指向它。
Vanilla 的镜像文件夹应为 vanilla，不能混用 gms。

## 3. 手机进入 Fastboot，电脑确认连接

先备份手机文件、应用数据和重要资料。清数据会删除内部存储、账号和 root 模块配置；不要删除 eSIM profile。
手机关机，按住 **音量下＋电源键**，看到 Fastboot 后用 USB 接电脑。

在电脑打开 **Windows PowerShell**，复制：

```powershell
$RomDir = 'C:\ROM'
$ToolsDir = 'C:\platform-tools'
& "$ToolsDir\fastboot.exe" devices
```

正常会出现类似：

```text
你的序列号    fastboot
```

记下第一列。没有输出就先处理 USB 线／接口／Fastboot 驱动，不继续。将下面文字改成你的实际序列号；不要把示例文字原样保留：

```powershell
$DeviceSerial = '这里填第一列序列号'
$Flavour = 'gms'
```

装 Vanilla 时只把 `$Flavour` 改为 `'vanilla'`。

## 4. 电脑检查文件，然后刷入 Recovery 配套镜像

先运行检查，不刷写、不清数据、不重启：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$RomDir\Install-Recovery.ps1" -Serial $DeviceSerial -Flavour $Flavour -FastbootPath "$ToolsDir\fastboot.exe"
```

脚本会核对完整 ZIP 和六镜像的哈希，确认目标是解锁的 diting、处于 bootloader Fastboot，并读取实际槽位和分区容量。
成功会显示 `Verified ... No flash, erase or reboot performed.`。如有报错，停下并保存完整错误文本。

检查通过后，运行真正刷写的命令：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$RomDir\Install-Recovery.ps1" -Serial $DeviceSerial -Flavour $Flavour -FastbootPath "$ToolsDir\fastboot.exe" -FlashRecovery
```

`-ExecutionPolicy Bypass` 只放行这次脚本进程，不永久关闭系统策略；`-FlashRecovery` 才允许写入。
脚本会逐一刷六个镜像，并进入 AviumUI Recovery。你不需要手动选择 A／B 槽，也不用另找 Recovery。
到此**尚未安装完整系统**。不要点 Reboot system now 去启动旧系统。

## 5. 在手机 Recovery 清数据

在手机屏幕上选择：

**Factory reset → Format data/factory reset → 确认清除**

这是会删除手机资料的步骤，请先完成备份。若出现删除 eSIM 的选项，不勾选；不要擦除 persist／modemst 等分区。
完成后返回 Recovery 主菜单。

## 6. 手机打开接收模式，电脑发送 ROM

在手机选择：

**Apply update → Apply from ADB**

手机进入等待电脑发送更新的画面，再在刚才的 PowerShell 中运行：

```powershell
$RomZip = Join-Path $RomDir "AviumUI-16.2.2-diting-$Flavour-user-batch14.zip"
& "$ToolsDir\adb.exe" -s $DeviceSerial sideload $RomZip
```

这一条才会安装完整 ROM。不要拔线，也不要解压 ZIP 或改选另一版本的 ZIP。
判断成功以**手机 Recovery 显示 Install completed** 为准，不只看电脑传输百分比。报错就停在 Recovery，记录手机和电脑的提示；不要绕过签名验证。

## 7. 手机开机与首次设置

安装成功后在手机返回主页，选择 **Reboot system now**。首次启动可能比平时慢。
OTA 会自行处理 A／B 安装槽位，不要手动切回原槽。不要重新锁 BL。

进入桌面后先检查相机、SIM／eSIM 信号、Wi-Fi、音频和指纹等。清数据可能重置移动数据／漫游开关，有费用限制时及时检查，或事先在运营商侧限制数据。用 Wi-Fi 完成联网设置。
GMS 版在系统自带功能设置中打开 **启用GMS服务**，再自行登录 Google 账号。先验收纯 ROM，之后再装 root／模块。

## 失败时怎么处理

- 任何脚本／安装报错都先停，不把后续步骤硬做完。
- 能进 Fastboot 时，用同版本工具包重新核对设备和文件，可重新刷匹配六镜像进入 Recovery，再安装匹配完整包。
- 只回退同版本 root 修改时，可使用对应原始 boot；若 root 方法改了其他镜像，也要按实际改动恢复。不要为此直接清数据或刷另一版 boot。
- 本测试版不承诺脏刷、保数据切换 Vanilla／GMS 或无风险降级。不提供擦除全部分区、persist／modemst 或未经核对的旧固件命令。

## English

This is a Windows clean-install guide, not a rooting guide. Download one flavour's full ROM ZIP and matching install-kit ZIP. Extract only the kit, then put the unchanged ROM ZIP beside Install-Recovery.ps1 and MANIFEST.json. Set the ROM/platform-tools paths and your own Fastboot serial in PowerShell. Run the installer without -FlashRecovery for verification first; add that switch to flash the six matching images and enter Recovery.

Back up before Factory reset → Format data/factory reset. Do not delete eSIM profiles or erase persist/modemst. Select Apply update → Apply from ADB, sideload the matching full ZIP, require the Recovery Install completed message, then reboot system without forcing a slot. Do not relock the bootloader. Check mobile-data/roaming costs after reset, enable the GMS preference for that flavour, and test the plain ROM before root/modules. Batch14 Vanilla and K50 Ultra remain untested; full hardware acceptance is incomplete.
