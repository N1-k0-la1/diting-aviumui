# Vanilla 可选：MIRA / Kasumi 兼容说明

Vanilla 不内置 microG，MIRA 也不是 ROM / OFRP 安装必需项。先完成 ROM 首次开机与快照合并，之后才安装 root / 可选模块。

此前 MIRA 1.1.2 在不存在 Volla 系统应用的 diting 上保留了对应 .replace 标记，Kasumi 拒绝挂载计划，microG / 商店未获得系统特权，导致商店闪退。只在对应原系统路径不存在时移除无效标记的兼容修改已提交：[上游 PR #12](https://github.com/spacealtctrl/microg_installer_revived_again/pull/12)。

附带 microg_installer_revived_again-v1.1.2-kasumi-compat-preview1.zip 和 mira-kasumi-compat-preview1-source.zip，分别为模块和对应源码。模块只能在支持的 root 管理器中安装，源码 ZIP 不可刷入；二者都不是 ROM。先按 [上游 MIRA 文档](https://github.com/spacealtctrl/microg_installer_revived_again) 安装 microG 及配套商店/Companion，再按其要求提升到系统应用并重启。

兼容预览此前在维护者的旧 Vanilla / YukiSU + Kasumi 环境中通过安装、重启和商店打开验证；新 media20261010 Vanilla 未实机安装，不能把旧结果视作当前版本全面验收。没有 Google 登录/下载或 Play Integrity 三项通过保证。先尝试适合你环境的上游版本；只有遇到同类挂载问题时才考虑这个非官方旧版兼容预览。

感谢 microG、spacealtctrl 及 MIRA 上游贡献者。原 GPL-3.0 许可与对应源码随附。

English: This optional unofficial MIRA 1.1.2 compatibility preview removes replacement
markers only for absent Volla paths. It was previously installed/rebooted and the Store
opened with YukiSU/Kasumi on an older project Vanilla build. The new media Vanilla is
not phone-tested. The module is installed through a supported root manager; the source
ZIP is not flashable. Read upstream documentation and PR #12. No login/download or
Play Integrity guarantee. Preserve microG / spacealtctrl credits and the GPL license.
