# 新增媒体来源

新增源码保留其原始版权和许可声明，特别是导入的 LHDC 头文件与 Bluetooth 源码。
23 个 LHDC/Dolby 专有 ELF 文件仅在 external-artifacts.json 记录固定来源与哈希，
未作为 Git 二进制补丁发布。它们不受本仓库 Apache-2.0 许可统一覆盖。
构建者仍需满足相关权利人的许可及分发条件。媒体配置与原厂 firmware 的权利亦归原权利人。
The repository license does not relicense proprietary LHDC/Dolby inputs.
See CREDITS.md and external-artifacts.json for pinned attribution and input hashes.
---

# Licensing

This is a collection of pinned upstream references and modifications to multiple projects,
not a relicensing of Android, LineageOS, AviumUI, vendor blobs or third-party applications.
Each patch remains subject to the license and copyright notices of its destination project/files.
Retain upstream notices when applying or redistributing modified sources.
The linked Linux kernel follows its upstream COPYING / GPL terms; see its exact source commit.
Vendor components and application binaries retain their respective owners' terms.

New project-specific helper code in `tools/` is licensed under Apache-2.0 as marked in those files.
No private signing keys, phone logs, Via backups, detector APKs or root-module binaries are included.
Via's proprietary binary delta is deliberately excluded; obtain the exact official APK separately.
