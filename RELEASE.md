# 当前媒体测试版

最新 GMS 完整包及实测限制见 [MEDIA-RELEASE.md](MEDIA-RELEASE.md)，安装见
[INSTALL-MEDIA.md](INSTALL-MEDIA.md)。下方 batch14 / batch13 是历史记录，不能用来替代本批元数据。
The latest GMS media release is described in MEDIA-RELEASE.md. Notes below are historical.
---

# 第十四批 Vanilla / GMS 候选

两个私有签名 `user/release-keys` 候选均已完成编译、签名、OTA/payload、实际镜像、模块和 Windows 独立回读检查。
**两版本均未完成第十四批全面实机验收；本仓库暂未提供 ROM 下载链接。维护者决定先分发测试候选并按反馈迭代。**

2026-10-08：GMS 版已在 12T Pro 完成首次启动，实际内核／user/release-keys／SELinux Enforcing 匹配；维护者反馈相机、eSIM、Google 登录及商店下载正常。完整 GMS Classic Integrity 回执为 BASIC / PLAY_RECOGNIZED / LICENSED，启用内置 BL 伪装仍未获得 DEVICE／STRONG。其他硬件、推送和待机验收仍有缺项。Vanilla 第十四批和 K50 至尊版尚未实测，不能继承另一版本／机型的通过状态。

本次按测试版分发，不标稳定版。GMS 需在系统自带“启用GMS服务”开关中启用，不内置 root，不承诺 Google 认证。通用安装／恢复说明见 [INSTALL.md](INSTALL.md)，成品元数据见 [MANIFEST.json](MANIFEST.json)，原始二进制 SHA256 见 [ROM-SHA256SUMS](ROM-SHA256SUMS)。整包和同版本六镜像由维护者另行提供下载；个人固定序列号安装脚本不作为通用公开安装器。

| 版本 | 文件名 | 字节数 | SHA256 |
|---|---|---:|---|
| vanilla | `AviumUI-16.2.2-diting-vanilla-user-batch14.zip` | 2238123471 | `9853a48c17c2c1fa4bcd3620ef9fb61aa5c8a417ab9d31b165786146726f8c1c` |
| gms | `AviumUI-16.2.2-diting-gms-user-batch14.zip` | 3069512451 | `5cd3a7a955a04080da8d504cfa72ac96247a136f6ba432d4d5ff52b54d9d0789` |

两版本的 boot 内核和全部 727 个模块字节一致，内核为 `5.10.269-android12-9-g930e6f73f237`。
21 个 OEM 固件保持一致。recovery 按原 BoardConfig 不含独立内核，需使用同版配套 boot。
不内置 root；GMS 包保留外部预签名 Google APK，不承诺 Google 认证或 Play Integrity。

12T Pro 第十三批实测记录保留，不能作为第十四批验收。K50 至尊版暂为源码支持、未实测。
共用 diting 代号不代替 K50 启动、108MP 相机、双实体 SIM 和固件兼容实测。
计划两份通用候选，不拆成四份包。eUICC feature 限于 ditingp SKU，相关 RRO 限于 GL。
已测／未测范围以本页为准，安装准备见 [INSTALL.md](INSTALL.md)。

## English

Both Vanilla and GMS batch14 candidates passed host signing, full OTA/payload, actual-image,
kernel/module and independent Windows readback checks. GMS has booted on 12T Pro with preliminary camera/eSIM, Google login and Play Store download checks; full hardware acceptance remains incomplete. Batch14 Vanilla is untested.
The shared kernel release and all 727 matching modules were verified; 21 OEM firmware images remain unchanged.
Batch13 results remain historical evidence and do not qualify untested batch14 features. K50 Ultra support has no hardware acceptance. The fresh complete-GMS Classic Integrity response is BASIC only, with PLAY_RECOGNIZED and LICENSED.
The maintainer is distributing testing candidates and collecting feedback; this repository does not yet provide ROM download links. See INSTALL.md, MANIFEST.json and ROM-SHA256SUMS for installation preparation and exact artifacts. GMS inclusion does not guarantee certification or Play Integrity.

---

# batch13 测试候选 / Testing candidate

**ROM 下载尚未发布。此文档不构成现成刷机包的发布公告。**

| 项目 | 当前信息 |
|---|---|
| 设备 | Xiaomi 12T Pro / 22081212UG / diting，已测试的内置 eSIM 变体 |
| 系统 | AviumUI 16.2.2 / Android 16，真实 user 构建 |
| 签名 | 维护者私有发布签名；不是原厂签名 |
| Root / GMS | ROM 不内置；用户自行安装的模块另计 |
| 内核 | 5.10.269-gki-geff4b40407a1 |
| 原始 ROM 文件 | AviumUI-16.2.2-diting-private-user-batch13.zip |
| 字节数 | 2238111898 |
| SHA256 | 83fc2c8abe1d25e0e2d42ce1ace7bfc4e9dfcb90430f2a81fca822db7c7619a8 |
| 配套原始 boot SHA256 | dcbf81702ff576393e5e84882c8bcf98bc0fb0f9ac1eb246afaf63ca855f9196 |

## 已完成与限制

- 已构建、完成签名及实际产物审计，并由维护者干净刷入启动。
- 相机正常、内置 eSIM 管理与卡切换正常；曾短暂无信号，随后恢复，根因尚未确定。
- Via 7.3.3 的原备份导入、导出与重启持久性通过实际核对。
- 当前版蓝牙、NFC、定位、音频、快充/充电限制、触控和长期待机尚未全面验收。
- 付费移动数据/漫游测试未进行，不能据此保证运营商数据服务。
- 剩余部分包名与 Flyme 元数据可被检测；不承诺所有检测全绿、Play Integrity 或硬件证明通过。
- 用户反馈切换到 Zygisk Next 后模块环境下的 Memory 红项消失；这是独立模块配置的反馈，不是 ROM 内置功能保证。
- 第三方 Lineage SDK 客户端可能受平台接口和服务可见性调整影响。
- 当前只验证上述 diting 变体，其他 SKU 不视为已通过；eSIM 构建选项默认可关闭。
- 发布路线为备份后干净安装；不承诺与旧包的签名或数据兼容。**不要重新锁定 Bootloader。**

公开刷机前还需归档匹配的 recovery / 必要镜像、完整安装步骤和无需登录的下载链接。
本阶段不提供未经最终核对的刷机命令。

## English

The ROM download and final installation guide are not published yet.
The maintainer has clean-flashed and booted batch13, confirmed the camera and eSIM profile switching,
and verified Via backup import persistence. A transient loss of signal recovered; its cause is unknown.
Full Bluetooth/NFC/GPS/audio/charging/touch and long-term standby regression remains pending.
Paid mobile-data and roaming tests were deliberately not performed.
No universal detector, Play Integrity or hardware-attestation pass is guaranteed.
Do not relock the bootloader. Only the tested diting eSIM variant is qualified at this stage.

## 2026-10-10 Camera component hotfix

Aperture camera update compiled, release-signed, installed and verified on 12T Pro. Both batch14 Vanilla/GMS camera signer certificates match the update. FHD/UHD-to-macro switching now falls back to valid 720p video, while main-camera preferences return when switching back. HD-only cameras retain native FPS ranges; macro no longer advertises the ineffective 60fps overlay. A short macro video was saved and fully decoded.

This is a standalone app update, with source included in the patch series as patch 51. It is not a rebuilt batch15 ROM. K50 camera behavior and HDR/long-term regression remain unverified. Users reported a successful latest-Vanilla TWRP install, but the TWRP version is unknown and this does not establish blanket recovery compatibility. Dolby Vision/LHDC are separate pending investigations. See CAMERA-HOTFIX.md and CAMERA-HOTFIX.json.
