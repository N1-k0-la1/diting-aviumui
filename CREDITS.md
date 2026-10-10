# 源码关系与鸣谢 / Credits

- [AviumUI](https://github.com/AviumUI)：当前系统源码与功能基础，采用 avium-16.2 系列。
- [AOSP](https://source.android.com/) 与 [LineageOS](https://github.com/LineageOS)：Android 基础、框架、diting / sm8450 设备支持和内核。
- [TheMuppets](https://github.com/TheMuppets) 及相关小米设备维护者：清单中的专有组件仓库。
- [OpenEUICC / PeterCxy](https://gitea.angry.im/PeterCxy/OpenEUICC)：集成的 eSIM 管理组件。
- [Via / tuyafeng](https://github.com/tuyafeng/Via)：官方签名浏览器；此次解决了原备份导入问题。
- **[WeiguangTWK](https://github.com/WeiguangTWK)**：感谢其 [patches_for_build_marble_AOSP](https://github.com/WeiguangTWK/patches_for_build_marble_AOSP) 提供 LineageOS 可见痕迹、框架文件边界和 vendor 服务实例迁移的设计参考。参考版本为 `898603cae89c1ab3d92fa3dd8eaa100b3788b798`；按 diting 的依赖重新适配，没有整体导入 marble 设备、相机、TEE 模拟器或 mimalloc 方案。
- 早期 **AviumUI 16.2.1 diting UNOFFICIAL** 构建及维护者：作为使用版本、恢复材料和功能对照。尚未取得该版本完整定制源码，因此不将其描述为当前源码分支的直接来源。

## English

This build uses AviumUI sources with pinned LineageOS diting/sm8450 support,
TheMuppets vendor repositories, OpenEUICC, and project-local patches.
WeiguangTWK's marble AOSP patches informed the design and adaptation of selected changes;
the marble device tree and unrelated patch sets were not imported wholesale.
The earlier unofficial AviumUI 16.2.1 image was a reference and recovery source,
not the direct source checkout or kernel binary used for this build.
User-installed root and hiding modules are separate from the ROM.

## 20261010 媒体整合 / Media integration

- [EvoX-LHDC](https://github.com/EvoX-LHDC)：Android 16 LHDC 集成和头文件的参考来源，保留导入源码版权声明。
- [Savitech / TheXPerienceProject](https://github.com/TheXPerienceProject/android_vendor_savitech_lhdc)：本次匹配的 LHDC 编码库来源；库的许可归各权利人所有。
- [Avicii-Labs](https://github.com/Avicii-Labs/android_hardware_dolby)：杜比视频组件与集成参考；本项目按 diting 做视频子集、ABI 桥接和策略适配。
- Xiaomi 与 Qualcomm、[diting 固件归档](https://dumps.tadiphone.dev/dumps/xiaomi/diting)：硬件基础与 diting 屏幕的杜比配置。
- 感谢实际测试和反馈的用户。新增媒体组件不构成相关商标、格式或流媒体认证。

## 自编译 Recovery / Recovery candidate

- [OrangeFox](https://gitlab.com/OrangeFox) 与 [TeamWin](https://github.com/TeamWin)：Recovery 和 Android 16 构建基础。
- [AviderMin](https://github.com/AviderMin/ofrp_device_xiaomi_diting)：本次 diting 设备树的直接基础；保留上游版权与许可声明。
- AOSP、Xiaomi / Qualcomm，以及 Recovery 上游贡献者。

- [microG](https://microg.org/) 与 [spacealtctrl / MIRA](https://github.com/spacealtctrl/microg_installer_revived_again)：Vanilla 可选 microG 安装/系统权限模块及兼容测试基础；可选模块与 ROM 分开。

- **@anatdx：我的精神支柱。**
