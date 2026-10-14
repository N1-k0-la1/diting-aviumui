# 2026-10-14 第三轮反馈核实与修复

以最新本地定制源码和公开提交 `250685f9029404bc66c47daa2b01d78766378c23` 为基准。反馈列出的代码和集成缺口成立；关于运行后果的判断保留以下边界：浮点零除可能产生 NaN/Inf，并非必然导致崩溃；1 字节解码输入的结果还依赖闭源库返回值，因此在进入库之前拒绝畸形包。

## 修复

新增 `patches/round3-20261014/01_packages_modules_Bluetooth.patch`：

- V3/V5 比特率查询在当前 codec 为空时返回 -1。
- V3 track 位深查询补齐未知值返回；源端及实际位于 `a2dp_vendor_lhdcv3_dec.cc` 的接收端配置解析都要求单个位深。能力声明仍允许多个位深。
- V3 编码器零包统计返回有限的 0.0f，保留正常平均占用率。
- V3 解码器在调用闭源库、调试录制和缓冲计算之前拒绝不足包头长度的输入并清空缓冲，避免无符号长度下溢。
- V5 32 位和 192000 Hz 的诊断字符串修正。

新增 `patches/round3-20261014/02_packages_apps_Settings.patch`：

- 完成校验时先清除绑定状态，容忍 Activity 已解绑产生的 IllegalArgumentException，继续清理临时文件。
- Activity 缺失、结束或销毁时不再开始验证/预览；异步完成时也检查原 Activity 是否已销毁。
- 使用统一的 overlay 校验器检查目标 android、字体类别及可变性。选择字体时检查对应 overlay；custom 候选、导入入口及保存前都检查 custom overlay。缺失 custom 不会禁用其他有效预设。

辅助工具直接修复：

- `apply-patches.py` 在解析路径前逐级拒绝链接，包括内部已有目标、内部悬空目标和父目录链接；用户选择的 checkout 根目录仍可通过别名访问。此检查解决静态链接绕过，不是对并发修改工作目录的完整隔离机制。
- 两套 Recovery 校验器同时核对普通文件、SHA256 和 Git 执行权限，在验证已应用源码及应用后都执行检查；拒绝内容一致的符号链接。
- 安装器优先使用候选内 assets，兼容顶层 assets；缺失文件在访问长度前给出明确报错。
- 从既有 Vanilla 发布记录补入六个镜像哈希，所有已有 ROM/Recovery 哈希保持原值。
- 删除未使用的辅助函数。

## 验证

- helper 回归：24 项，包括内部链接拒绝、两套 Recovery 在正常及优化 Python 下的模式检查和链接拒绝。
- production 回归：8 组。实际 V3/V5 查询、V3 两个解析器、track 返回路径、解码器和统计语句在 ASAN/UBSAN 下通过；统计语句额外开启 float-divide-by-zero 检查。覆盖一字节包、多位深配置拒绝、能力声明接受和正常行为。
- font 生命周期回归：解绑异常后文件清理、缺失/销毁 Activity、实际预览入口保护、实际 overlay 校验器及原有 IPC/超时/启动清理通过。Android API 用受控主机替身；预览测试覆盖入口保护，不渲染真实界面。
- Windows 安装器模拟：旧结构只读、六次写入后进入 Recovery、槽位变化停止、新候选 assets 结构和缺失文件五个场景通过。使用虚拟资产及模拟 fastboot，未刷入手机。
- 从固定上游重放 75 份补丁并加入核对过的外部输入：30 个定制项目的文件树匹配选定的最新公开版本。原 73 份补丁逐字节保持不变；system/core 仍仅导出选定的公开版本。
- 增量构建 `m com.android.bt Settings services.core selinux_policy diting_lhdc_policy_probe` 及五个 SKU 的音频 XML 安装目标通过，耗时 8 分 12 秒。
- 手机连接后补跑 installed-audio-policy：构建实际安装的五个 SKU 配置匹配源输入；将 cape 配置从实际安装文件展开后，在手机运行原生探针，18 项 A2DP 编码路由和扬声器检查全部通过。标准格式仍走 primary，LHDC 走 bluetooth；未改动手机运行中的音频策略，也未验证耳机播放。

Linux 回归：

```sh
python3 tests/helper-regressions.py
python3 tests/production-regressions.py /path/to/patched/android
python3 tests/font-lifecycle-regressions.py /path/to/patched/android
```

Windows 安装器回归：`python tests/installer-regressions.py`（需要 PowerShell 和 .NET Framework）。

本轮更新源码、测试、文档和校验记录，历史 ROM/Recovery 镜像未重建，不包含此次修复。没有进行全新独立 repo sync/build。实机 LHDC 播放、完整生命周期操作和 Vanilla/K50 Ultra 验证仍待补充。本地设备调查、日志实验、凭据和签名材料不公开。
