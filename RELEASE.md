# 第十四批双 flavour 候选准备

Vanilla / GMS 正在构建准备阶段，还没有新的发布 ZIP。
第十三批在 12T Pro 的实测结论不能直接作为第十四批验收结果。
K50 至尊版（22081212C）源码包含区域型号、相机及 SIM 配置，但未完成实机测试。
第十四批将 eSIM feature 限于 ditingp SKU、相关 RRO 限于 GL；原 CN / GL 型号选择和固件二进制保留。
两种候选需各自验收；K50 的启动、108MP 相机、双实体 SIM 和固件兼容是发布前的单独检查项。
GMS 不保证 Google 认证、Play Integrity 或硬件认证通过；不预装 root。

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
