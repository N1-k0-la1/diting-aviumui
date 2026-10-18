# 许可范围 / Licensing

本仓库汇集固定上游版本、补丁、项目工具和验证记录，**不对 Android、LineageOS、AviumUI、内核、Recovery 或厂商组件重新统一授权**。
每份补丁及应用后的源文件保留目标项目适用的版权和许可声明。分发修改后的源码时应保留这些声明，并履行相应许可义务。

## 项目自有工具与测试

- `tools/` 的项目自有辅助代码，以及 `tests/` 中标注 `SPDX-License-Identifier: Apache-2.0` 的原创通用工具/Android 测试，采用 [Apache License 2.0 全文](LICENSES/Apache-2.0.txt)。
- `tests/ofrp-*.py` 及标注 `GPL-3.0-or-later` 的 Recovery 辅助/测试文件采用 [GPL version 3 或后续版本](LICENSES/GPL-3.0-or-later.txt)。
- 测试运行时抽取的生产方法、上游测试数据及生成代码保留其来源许可；脚本自身的许可不覆盖或重新授权这些输入。
- 文件已有的第三方声明继续有效；具体范围以文件声明和对应上游版本为准。

## 补丁、内核与 Recovery

`patches/` 的修改遵循各目标项目/文件的许可，不由工具目录的 Apache-2.0 统一覆盖。
Linux 内核遵循所固定提交中的 `COPYING` 与各文件声明，来源见 [KERNEL.md](KERNEL.md)。
`recovery/` 中保留的各 OrangeFox/TeamWin/diting 源码包（包括 `orangefox-diting-20261016-review2/`）沿用其原有许可。
项目新增 Recovery 辅助/测试文件和 OrangeFox 修改按文件标记采用 GPL-3.0-or-later；原 Android 设备文件保留各自声明。
公开 OTA 证书属于公钥材料，不包含签名私钥。

## 专有输入与媒体来源

23 个 LHDC/Dolby 专有 ELF 文件仅在 [external-artifacts.json](external-artifacts.json) 中记录固定来源与哈希，未作为 Git 二进制补丁发布。
这些库、媒体配置、原厂 firmware 和第三方应用仍受各权利人的条款约束；来源与哈希记录不代表取得或转授分发权。
导入的 LHDC 头文件和 Bluetooth 源码保留原始版权及许可声明。Via 的专有二进制差异不在仓库内，构建者应另行取得精确官方 APK。
参见 [CREDITS.md](CREDITS.md)。

## English

This repository does not relicense Android, LineageOS, AviumUI, Linux, OrangeFox, vendor firmware, proprietary libraries or third-party applications.
Patches and patched files remain subject to their destination projects' notices and licenses.
Original project tools/general Android tests are Apache-2.0 where marked; Recovery helpers/tests and modifications marked GPL-3.0-or-later retain that scope. Extracted production code keeps its upstream license.
Proprietary Via/LHDC/Dolby inputs are obtained separately under their owners' terms. No private signing keys, account data, phone logs, personal backups or root-module binaries are included.
