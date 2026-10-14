# 2026-10-14 复核结果

本次复核以本地最新 Android 源码 checkout 为准。GitHub 中较早的补丁快照只用于生成可复现的追加补丁；已发布的 ROM、Recovery 和二进制哈希没有被重写。

| 项目 | 结论 | 处理 |
| --- | --- | --- |
| BluetoothCodecConfig LHDC 比较 | 真问题 | 修正 `mCodecSpecific4` 比较，并修正 codec 专用参数比较方法的空对象判断。 |
| Settings 的 4 个 LHDC 控制器 | 真问题 | null 配置记录日志后返回默认索引，避免 NPE。 |
| A2DP 读取回调 | 部分成立 | HAL 读取接口本身已有有界轮询和长度限制；移除外层重复轮询，增加空指针、零长度和返回值边界保护。 |
| LHDC V3 解码器 | 真问题 | 修正 fmt 字符串、状态表达式、布尔失败值和未对齐时间戳读取；同步修正 V3 sink 与 V5 时间戳读取。 |
| Install-Recovery | 真问题 | 移除刷写完成后的冗余 `reboot bootloader`，减少 USB 重枚举窗口；本地发布模板同步修正。 |
| Goodix Recovery 延时 | 当前版本不成立 | 内核 reset 实现已经同步等待 100ms；没有改动 Recovery 脚本、设备补丁或已验收镜像。 |
| sepolicy / ADB root 默认值 | 防御性改进 | 补充聚合 domain 排除并给 BoardConfig 提供安全默认值；当前构建原本已有产品级赋值。 |
| Python 辅助脚本 | 真问题与防御性改进 | 修正路径解析、媒体碰撞预检、donor HEAD 缓存、未知媒体族拒绝，并用显式异常替代会被 `python -O` 删除的 `assert`。 |
| 构建与 Recovery 元数据 | 真问题 | 更新 Vanilla 状态、Recovery 历史字段和 manifest 的 detached SHA `dest-branch`；旧二进制哈希保持不变。 |

## 验证

- 本地最新源码组件构建通过：`m com.android.bt Settings selinux_policy -j4`，耗时约 7 分 48 秒。
- 公开仓库的 64 个补丁逐个通过 SHA256 核对和 `git apply --stat`。
- 4 个辅助 Python 脚本通过语法编译检查。
- 15 项主机回归检查通过：实际 Java 比较方法、实际 C++ 回调（ASAN/UBSAN）、路径边界、媒体碰撞预检、donor 缓存，以及两套 Recovery 脚本在普通和优化模式下的拒绝检查。
- 安装器以模拟 fastboot 和无效测试镜像完成三组回归：只读模式、六个分区写入后直接重启 Recovery、槽位变化停止后续写入；测试未连接真实设备。
- 最新本地 1190 个源码项目的 HEAD 与新固定清单一致且工作树干净；原有 60 个公开补丁字节保持一致，4 个追加补丁通过反向 index 检查，两套 Recovery 输入哈希核对通过。
- 本次追加补丁只描述源码纠错，不声称已经重建或替换历史发布 ROM。

## 范围

本轮没有自动刷写、清除应用数据、删除 Download 文件或上传私有崩溃研究。后续完整审查和最新源码同步见 [FULL-REVIEW-20261014.md](FULL-REVIEW-20261014.md)，其中记录扩展修复与当前补丁数量。
