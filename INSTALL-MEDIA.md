# 安装 20261010 GMS 媒体测试版 / Install media testing release

下载完整 ROM ZIP 与同批 `gms/` 六镜像、`Install-Recovery.ps1`、`MANIFEST.json`、`SHA256SUMS`。
这些配套文件来自 **20261010-media-test** 目录；不要混用旧 batch14 镜像或工具包。
校验 ROM 与镜像，备份数据；Bootloader 必须已解锁，安装后不要重新锁定。

## 当前已装 AviumUI

使用可正常进入的配套 AviumUI Recovery，选择 **Apply update → Apply from ADB**。
在电脑 PowerShell 中，把目录和目标序列号改为你自己的：

```powershell
$RomDir = 'C:\ROM'
$ToolsDir = 'C:\platform-tools'
$DeviceSerial = '填写你的目标手机序列号'
& "$ToolsDir\adb.exe" -s $DeviceSerial sideload "$RomDir\AviumUI-16.2.2-diting-gms-user-media20261010.zip"
```

以手机显示安装完成为准，随后手动重启。电脑约 47% 停止不一定是错误。
本批延续原发布签名，但保数据升级尚未独立验收；不要默认清数据。
Vanilla 转 GMS、其他 ROM 迁入及回退需另外准备干净安装与数据备份。
更新会替换 boot，root 应修补本批原始 boot，不能用旧版 boot。

## 恢复配套 AviumUI Recovery

手机手动进入 bootloader Fastboot，先检查同批文件：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$RomDir\Install-Recovery.ps1" -Serial $DeviceSerial -Flavour gms -FastbootPath "$ToolsDir\fastboot.exe"
```

检查通过，需要刷入六个同批镜像时，在上面命令末尾加 `-FlashRecovery`。
它会进入 Recovery，不会自动清数据；随后必须安装完整 ZIP，再启动系统。
首次干净安装的菜单顺序可参考 [INSTALL.md](INSTALL.md)，但文件必须换成本批配套文件。

## TWRP / OrangeFox 当前情况

维护者使用 `TWRP 3.7.1_16-ditingp-by-qiqi` 安装成功，但先修正了该 Recovery 的两处问题：
产品名检查把 `diting` 包与 `ditingp` 恢复环境判为不匹配；其 `fstab.postinstall`
带 CRLF，导致 `ErrorCode::kInstallDeviceOpenError`。修正发生在 Recovery 的临时内存文件中，未修改 ROM ZIP。
不能据此保证所有 TWRP/OFRP 直接安装成功。

AviderMin 的 diting OrangeFox 有狐狸标志循环的反馈，原因尚未取得运行时证据。
不要使用 `raphael` 等其他设备的 Recovery。当前建议使用配套 AviumUI Recovery；
本项目自编译的 OrangeFox 将在独立实测后另行提供。

## English

Use the full `media20261010` GMS OTA and its six matching images; do not mix batch14 files.
Back up data, keep the bootloader unlocked, and use the matching AviumUI Recovery's ADB update menu.
The commands above are manual; adapt paths and the target serial. Trust the phone's completion result.
Retained-data upgrades, Vanilla-to-GMS migration and downgrades are not qualified by this test.
TWRP installation succeeded only after correcting a product alias mismatch and a CRLF postinstall fstab
in that recovery's RAM filesystem. Universal TWRP/OrangeFox compatibility is not claimed.
Use the matching AviumUI Recovery until a separately tested project OrangeFox build is available.
