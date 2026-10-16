# Round 6 review and fixes

本轮核实两个用户问题。Thanox 快速连续返回会留下 Launcher 的 `stateDepth=0.7` 和壁纸模糊半径；修复了被取消的返回动画、应用打开动画和 workspace reveal 的状态恢复，并停止迟到的深度动画写入。QQ 克隆授权失败的结果回传也属实：不可变 PendingIntent 会忽略发送方的 `FLAG_ACTIVITY_FORWARD_RESULT`，现已在创建 PendingIntent 前冻结该标志。HMA-OSS 隐藏预设导致 QQ 看不到官方酷狗的问题通过 HMA 的酷狗可见例外修复，属于设备配置，不写入 ROM。

主机回归覆盖 Launcher 深度恢复、QQ 授权回传边界、LHDC 空指针/畸形输入/除零，以及补丁和恢复脚本安全检查。GMS 组件编译和签名镜像审计通过；Vanilla 完整目标包仍在生成中。新包需要手机刷入后再验证快速返回两次、QQ 分身授权和酷狗登录。

本轮未公开 Lineage 调试日志、Skland 相关私有改动、账号数据、HMA 配置、签名材料或设备截图。
