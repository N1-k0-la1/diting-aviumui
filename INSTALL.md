# 安装说明

本说明以维护者网盘成品目录为工作目录，该目录包含完整 ROM、配套镜像和本批 `MANIFEST.json`。
GitHub 仓库根目录的 `MANIFEST.json` 是 batch14 历史资料，不能替代本批成品目录随附的清单。

适用 Xiaomi 12T Pro / Redmi K50 Ultra（diting 系列），需要已解锁 Bootloader。禁止重新上锁。
先备份照片、文档、验证器与重要应用数据。首次迁移的 Format Data 会清空内部存储；备份应放电脑/外置存储。
本目录不会自动执行刷机、清除数据或重启。

## 从此前本项目 ROM 升级

1. 选择同一版本系列：本目录 GMS 升 GMS；核对 SHA256SUMS。
2. 在已可用的 Recovery 中安装对应完整 ZIP，等待手机端显示成功。普通升级不要求逐个刷六个配套镜像，也不要求清空数据。
3. 先使用整包的原版 boot 启动 Android。不要叠加旧版本修补 boot。
4. 首次开机完成后等待 OTA 快照合并结束，再进行 root 或恢复 OFRP。
5. 按 [README.md](README.md) 中的验证范围验收；若异常，保留日志与当前模式，勿盲目格式化。

GMS/Vanilla 跨系列保留数据切换未验证，不按普通同系列升级处理。

## 从其他 ROM 首次迁移

本机有独立 Recovery 分区，OFRP 镜像不带完整的系统启动环境；只刷一个 OFRP 不等于完成首次迁移。
按 OFRP-INSTALL.md 核对配套镜像、准备启动环境并进入 OFRP。先确认触摸与 USB 正常，再进行所需的数据格式化及整包安装。
不要擦除 persist、modemst、eSIM 数据或手动格式化 system/vendor 等动态分区。
不要在 OTA 安装和合并过程中手动切换槽位。

## boot 与备用镜像

配套原版 boot 为 gms/boot.img，取自本目录 GMS ZIP 的已签名 payload，未经 root 修补。
另外五个镜像也只对应同目录版本；其中 recovery.img 是 Avium Recovery，不是 OFRP。
确认正常启动后才用本批 boot 修补 root。不要使用另一版本或旧包的 boot。
