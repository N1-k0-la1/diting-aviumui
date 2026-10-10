# 2026-10-10 媒体测试版 / Media testing release

本批已补齐新的 Vanilla，成品见 [MEDIA-VARIANTS.json](MEDIA-VARIANTS.json)，主机验收通过、实机待测。下文保留 GMS 的具体实测范围。

GMS 完整 ROM：`AviumUI-16.2.2-diting-gms-user-media20261010.zip`。
旧 batch14 Vanilla 仍是旧版本，不包含本批媒体整合；不要将两者标为同一批更新。

本批整合相机视频切换热修复、LHDC V3/V4/V5 软件编码和杜比视界视频组件。
LHDC RAW 未启用；不含 Dolby DAP 音效或 Dolby 音效应用。
内核保持 `5.10.269-android12-9-g930e6f73f237`，`user/release-keys`，不内置 root。

## 实测范围

12T Pro 已由维护者刷入并开机，反馈手动验收项目除 LHDC 外均正常。
这是一份用户实测反馈，不等于所有格式、硬件和长期稳定性均已通过。

- LHDC：组件、Bluetooth APEX 与依赖检查通过；在手机上 11 组实际编码测试通过。
  尚无确认支持 LHDC 的耳机，连接协商、持续播放和功耗仍待验证。
- 杜比视界：服务、codec、配置、策略及实际签名镜像核对通过；未记录实测视频的 profile、播放器与样本，暂不承诺全部杜比格式或流媒体认证。
- K50 至尊版：本批尚无实机验收；欢迎测试反馈。旧版用户的反馈不自动继承到本批。
- 本轮未确认干净/保数据安装及测试时的 root 状态，长期待机仍待反馈。
- 本批没有新的 Google 认证或 Play Integrity 通过承诺。

ROM 字节数、SHA256 与同版六镜像见 [MEDIA-RELEASE.json](MEDIA-RELEASE.json)。
本仓库发布源码和校验信息；ROM 网盘链接由维护者另行提供。
安装说明见 [INSTALL.md](INSTALL.md)，修正版 OrangeFox 见 [OFRP-INSTALL.md](OFRP-INSTALL.md)。12T Pro 已通过本修正版的完整 ZIP 安装、系统开机和快照合并；HyperOS 3.0.6 直接迁入仍未验证。

## English

A matching new Vanilla is now host-qualified, with phone testing pending; see MEDIA-VARIANTS.json. The following describes the tested GMS artifact, including the Aperture video-switch fix,
LHDC V3/V4/V5 software encoders and opt-in Dolby Vision video components.
The older batch14 Vanilla artifact does not contain this media update.
There is no bundled root or Dolby DAP audio app; unsupported LHDC RAW is disabled.

The maintainer installed and booted it on a 12T Pro and reported the manual checklist
passed except LHDC, for which no compatible headset is available. Eleven on-device
encoder cases and host APEX/signing/OTA/image audits passed. Actual headset playback,
K50 Ultra testing and long-term stability remain pending. Specific Dolby sample/profile/player
coverage was not recorded. Google certification and Play Integrity are not guaranteed.
See MEDIA-RELEASE.json for exact artifacts and INSTALL-MEDIA.md for installation.
