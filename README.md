# diting-aviumui

AviumUI 16.2.2 / Android 16 的 diting 非官方定制项目，面向 Xiaomi 12T Pro 和 Redmi K50 至尊版。
维护者：[N1-k0-la1](https://github.com/N1-k0-la1)。与 AviumUI 官方发布独立。

当前基线是 batch13：真实 `user` 构建、维护者私有发布签名、无内置 root、无 GMS。
这是测试候选，尚未完成全面硬件回归或长期稳定性验收。ROM 下载暂未发布。

本仓库包含 1187 个基础项目、3 个可选 GMS 项目的固定版本清单、50 份有序补丁、构建说明和鸣谢。
第十四批正在准备 Vanilla / GMS 两个候选：内核命名及区域 eSIM 限制已改源码，尚未完成构建与实机验收。
K50 至尊版暂为源码支持、待实测；当前已实测的仍是 12T Pro 第十三批。
Via 补丁只保留元数据变更；对应官方 APK 由构建者另行获取并校验。

- [构建与签名说明 / Build](BUILD.md)
- [版本、实测范围与已知限制 / Release status](RELEASE.md)
- [源码关系与鸣谢 / Credits](CREDITS.md)
- [内核源码与命名 / Kernel](KERNEL.md)
- [许可说明 / Licensing](LICENSES.md)

## English

Unofficial AviumUI 16.2.2 / Android 16 customization targeting Xiaomi 12T Pro and Redmi K50 Ultra (`diting`).
Batch14 Vanilla/GMS builds are in preparation. K50 Ultra support is untested; the tested baseline remains batch13 on 12T Pro.
The batch13 candidate is a real `user` build, signed with maintainer-owned release keys,
without bundled root or GMS. Full hardware and long-term regression are pending.
No ROM download is published yet. See the English sections of the linked documents.
The repository contains pinned upstream sources and ordered patches, not the full Android checkout.
Private signing keys, device logs, personal backups, and third-party root modules are excluded.
