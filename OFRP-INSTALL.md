# OrangeFox review2 安装与验收

本说明以维护者网盘成品目录为工作目录，该目录包含完整 ROM、配套镜像和本批 `MANIFEST.json`。
GitHub 仓库根目录的 `MANIFEST.json` 是 batch14 历史资料，不能替代本批成品目录随附的清单。

镜像：OFRP/OrangeFox-diting-ditingp-20261016-review2.img。
本镜像作为 diting 非官方正式版提供，完整编译与主机检查已通过。维护者确认自 review2 编译后均用本镜像刷入项目 ROM，安装与 /sdcard 显示正常；PIN 解密、各类 USB 模式及 K50 Ultra 等仍待分别验证。
首次迁移前先看 INSTALL.md；仅在 Bootloader 已解锁且电脑识别为 diting 时继续。

## 已在本项目 ROM 上替换 Recovery

确认 Android 已正常启动且 OTA 快照已完成合并，核对 OFRP 的 SHA256。
进入 Bootloader fastboot，确认 product=diting、unlocked=yes、is-userspace=no、current-slot 为 a 或 b。
只将 OFRP 写入当前槽位的 recovery 分区（例如当前槽 a 就是 recovery_a），再重启到 recovery。
若任一步失败，立即停止后续写入。不要靠切换槽位或反复格式化尝试修复。

## 首次迁移：匹配启动环境

以下路径以在本目录打开 Windows CMD 为前提。先设置实际序列号与所选版本，勿照抄占位符：

```cmd
set SERIAL=YOUR_SERIAL
set ROM_FLAVOUR=gms
powershell.exe -NoProfile -ExecutionPolicy Bypass -File Install-Recovery.ps1 -Serial %SERIAL% -Flavour %ROM_FLAVOUR% -ManifestPath MANIFEST.json -FastbootPath C:\platform-tools\fastboot.exe
```

Vanilla 将 ROM_FLAVOUR 改为 vanilla。此命令只读核对 ROM/六个配套镜像、设备、槽位、分区类型和大小；应显示 No flash。
**此处不要加 -FlashRecovery**：该选项安装的是配套 Avium Recovery，不是 OFRP。

核对 OFRP 校验值后，读取 current-slot，将下面 SLOT 替换成实际 a 或 b。每行完成且无报错后才运行下一行；不要直接粘贴整组：

```cmd
C:\platform-tools\fastboot.exe -s %SERIAL% getvar current-slot
C:\platform-tools\fastboot.exe -s %SERIAL% flash boot_SLOT %ROM_FLAVOUR%\boot.img
C:\platform-tools\fastboot.exe -s %SERIAL% flash dtbo_SLOT %ROM_FLAVOUR%\dtbo.img
C:\platform-tools\fastboot.exe -s %SERIAL% flash vendor_boot_SLOT %ROM_FLAVOUR%\vendor_boot.img
C:\platform-tools\fastboot.exe -s %SERIAL% flash recovery_SLOT OFRP\OrangeFox-diting-ditingp-20261016-review2.img
C:\platform-tools\fastboot.exe -s %SERIAL% flash vbmeta_SLOT %ROM_FLAVOUR%\vbmeta.img
C:\platform-tools\fastboot.exe -s %SERIAL% flash vbmeta_system_SLOT %ROM_FLAVOUR%\vbmeta_system.img
C:\platform-tools\fastboot.exe -s %SERIAL% reboot recovery
```

确认 OFRP 触摸正常。仅首次迁移且已备份时执行 Format Data，再重启 Recovery；将完整 ROM ZIP 重新复制进去或通过 sideload 安装。
以手机端成功结果为准，电脑端约 47% 的显示本身不能判定成败。安装完整 ZIP 后启动 Android，不只刷这些启动镜像便启动系统。
正常启动并等快照合并完成后，才按需恢复 OFRP 或修补本批原版 boot。

## 验收与限制

检查启动、PIN 数据解密、触摸和熄屏唤醒、MTP/ADB、fastbootd、sideload、正常整包安装及系统启动/快照合并。
独立 Recovery 重装功能也待硬件验证。携带旧 compatibility.zip 的包默认拒绝，当前无界面跳过开关。
