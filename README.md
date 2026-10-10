# 当前版本：20261010 GMS 媒体测试版

本批整合相机视频切换修复、LHDC V3/V4/V5 软件编码和杜比视界视频组件。
12T Pro 已刷入开机，维护者反馈手动验收除 LHDC 外正常；尚无 LHDC 耳机实测，
本批 K50 至尊版和长期稳定性仍待反馈。杜比视频样本/profile/播放器范围未记录。
仅构建了新 **GMS** 包，旧 Vanilla 不是同批媒体版。

- [版本与验收范围 / Current release](MEDIA-RELEASE.md)
- [本批安装说明 / Installation](INSTALL-MEDIA.md)
- [精确成品校验 / Artifact metadata](MEDIA-RELEASE.json)
- [构建 / Build](BUILD.md) · [鸣谢 / Credits](CREDITS.md)

源码包含 1187 个上游基础项目、3 个可选 GMS 项目与 60 份有序补丁。
Via APK 及 23 个媒体 ELF 二进制不放入源码仓库；构建者按固定来源和 SHA256 另行提供。
本仓库未托管 ROM 二进制；网盘发布由维护者提供。

English: The latest artifact is the GMS-only **media20261010 testing release**.
The maintainer booted it on 12T Pro and reported the checklist passed except LHDC.
Actual LHDC headset playback, K50 Ultra and long-term testing remain pending;
specific Dolby profile coverage was not recorded. See the current release and installation links above.
Older release notes follow as historical records.
---

# diting-aviumui

AviumUI 16.2.2 / Android 16 的 diting 非官方定制项目，面向 Xiaomi 12T Pro 和 Redmi K50 至尊版。
维护者：[N1-k0-la1](https://github.com/N1-k0-la1)。与 AviumUI 官方发布独立。

当前第十四批 Vanilla / GMS 候选为真实 `user` 构建、维护者私有发布签名、无内置 root。
维护者决定先分发测试候选并按反馈迭代；尚未完成全面硬件回归或长期稳定性验收。本仓库暂未提供 ROM 下载链接。

本仓库包含 1187 个基础项目、3 个可选 GMS 项目的固定版本清单、51 份有序补丁、构建说明和鸣谢。
第十四批两候选已完成构建与主机核对，使用规范内核命名和区域 eSIM 限制。GMS 版已在 12T Pro 开机，核对新内核／签名构建身份／SELinux，并完成相机、eSIM、Google 登录和商店下载初测；完整硬件与长期回归仍待完成。
Vanilla 第十四批尚未实测；K50 至尊版暂为源码支持、待实测。当前完整 GMS Classic Integrity 为 BASIC-only，不承诺 DEVICE／STRONG。
2026-10-10 发布后相机修复：已编译并在 12T Pro 验证签名相机更新，修复录像切入微距退出及微距无效 60fps 显示。适配原 batch14 Vanilla / GMS 的相同相机证书；K50 尚待反馈。本次是组件更新，原 ROM ZIP 保持 batch14。见 [相机修复 / Camera hotfix](CAMERA-HOTFIX.md)。

Via 补丁只保留元数据变更；对应官方 APK 由构建者另行获取并校验。

- [构建与签名说明 / Build](BUILD.md)
- [版本、实测范围与已知限制 / Release status](RELEASE.md)
- [安装与恢复 / Installation](INSTALL.md)
- [源码关系与鸣谢 / Credits](CREDITS.md)
- [内核源码与命名 / Kernel](KERNEL.md)
- [许可说明 / Licensing](LICENSES.md)

## English

A signed post-release camera hotfix was built and validated on 12T Pro on 2026-10-10. It fixes unsupported macro video stream sizes and invalid high-FPS UI options. The original batch14 ROM ZIPs are unchanged; K50 testing remains pending. See [Camera hotfix](CAMERA-HOTFIX.md).

Unofficial AviumUI 16.2.2 / Android 16 customization targeting Xiaomi 12T Pro and Redmi K50 Ultra (`diting`).
Batch14 Vanilla/GMS candidates passed host qualification. GMS has booted on 12T Pro with preliminary camera/eSIM, Google login and Play Store download checks; full hardware and long-term regression are pending. Batch14 Vanilla and K50 Ultra remain untested. The current full-GMS Classic Integrity result is BASIC only.
The batch13 candidate is a real `user` build, signed with maintainer-owned release keys,
without bundled root or GMS. Full hardware and long-term regression are pending.
Testing candidates are being prepared for maintainer distribution and feedback; this repository does not yet provide ROM download links. See the English sections of the linked documents.
The repository contains pinned upstream sources and ordered patches, not the full Android checkout.
Private signing keys, device logs, personal backups, and third-party root modules are excluded.
