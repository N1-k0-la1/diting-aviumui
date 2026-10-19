# 系统 APK 打开流程修复（2026-10-18）

Telegram 类客户端打开 APK 时，平台 ResolverActivity 被误当作普通目标应用，启动审批显示两个“Android 系统”。选择空间后把原始隐式 Intent 限定为 android 包，导致安装器等真正候选全部消失。

修复对系统安装、平台签名的 android/com.android.internal.app.ResolverActivity 精确豁免多余审批，保留原始 MIME、URI 授权及候选解析。普通应用分身选择和启动审批继续生效；没有按调用方 action/MIME 或整个 android 包放行。

生产方法 34 个断言与 3 个失败负例通过，另外四套已有启动审批/分身回归通过；真实 services 模块编译通过。93 份公开补丁在 31 个项目精确重放通过，历史 92 份补丁保持原样。

此补丁已进入 batch29，GMS、Vanilla 均完成正式整包构建、签名、实际镜像与 OTA/payload 核对、组件一致性及 Windows 回读审核。2026-10-19 维护者在 batch29 验收清单后反馈 12T Pro GMS 没有问题。逐项测试以及清除安装器默认项后的 Resolver 路径未由构建端独立确认；Vanilla 和 K50 Ultra 尚无本批实机验收记录。

已记住的安装器默认项可能使请求直接进入安装器；专项验证需覆盖真正的打开方式选择路径。此注意事项不要求清空应用数据。普通应用分身和授权回归仍需按各自场景验证。当前成品及哈希见 [batch29 清单](docs/releases/batch29-20261019/ARTIFACTS.json)。
