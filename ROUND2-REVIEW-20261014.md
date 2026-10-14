# 2026-10-14 第二轮反馈核实

以最新本地 Android 源码为准，反馈中的集成与字体生命周期问题均成立。补丁序列追加三份，当前为 73 份；原来的 70 份未改写。

| 问题 | 核实与修复 |
| --- | --- |
| LHDC XML 未安装且未被实际策略包含 | `common.mk` 将片段安装到 `/vendor/etc`，五个 SKU 的实际策略用绝对 XInclude 引用该片段。实际手机 vendor SKU 是 `cape`，其策略安装在 `/vendor/etc/audio/sku_cape/audio_policy_configuration.xml`。原 primary 模块保持原内容。 |
| 缺少字体共享内存时不回复 | 改为进入失败处理并发送失败回复，避免等待 20 秒超时。 |
| 验证已完成仍保留超时回调 | 使用固定回调引用，完成时立即移除；同步绑定失败时不再安排超时。 |
| 安装中断遗留 staged 字体 | 启动完成时清理 `staged-*.font`，保留已加载/已导入字体和无关文件。 |
| Custom overlay 标签错误 | 标签改为 Custom，所需系统字体元数据仍为 source-sans-pro。 |
| VALIDATION 当前补丁数过时 | 当前记录更新为 73，并新增当前 30 项目重放验证。媒体历史快照的 60 份记录保留其原有含义。 |

## 验证

- `tests/helper-regressions.py`：15 项通过。
- `tests/production-regressions.py`：4 组实际方法测试通过，C++ 使用 ASAN/UBSAN。
- `tests/font-lifecycle-regressions.py`：实际字体 IPC 处理、绑定失败、成功/失败/超时完成的回调清理，以及启动清理通过。Android API 由受控主机替身提供。
- 从固定上游重放全部 73 份补丁并加入已核对的外部输入：30 个定制项目文件树匹配最新公开版本。system/core 只匹配选定的公开版本，排除本地专用改动。
- `m com.android.bt Settings services.core selinux_policy diting_lhdc_policy_probe` 及五个 SKU 音频 XML 安装目标增量构建通过，耗时 7 分 56 秒。
- 五个构建实际安装的 SKU 策略与源输入逐字节一致。将其中 cape 策略的 XInclude 从构建实际安装的 `/vendor/etc` 文件展开后，运行原生 `diting_lhdc_policy_probe`：三类 A2DP 设备 × 六种编码的 18 项路由和扬声器检查通过。SBC/AAC/APTX/APTX_HD/LDAC 为 primary，LHDC 为 bluetooth；同时解析到 primary 的 9 个输出配置和 26 个设备。未修改手机正在使用的音频策略。

可复现命令：

```sh
python3 tests/helper-regressions.py
python3 tests/production-regressions.py /path/to/patched/android
python3 tests/font-lifecycle-regressions.py /path/to/patched/android
python3 tests/installed-audio-policy-regressions.py /path/to/patched/android --serial DEVICE_SERIAL
```

原生策略输入 SHA256：`2d134d904f52da1555252f2799e4efbf22cab7f5742a37240caf17472919a32e`；LHDC 片段：`73c858be944637a5703652c8f1c61e597838d8f0c94e29fc19a2344f1a321060`；展开配置：`ec73d219d64718fff003e1662fea9ac899aba22ebfb1a869627a9c7f69e60809`。

本轮更新源码、测试及验证记录。历史 ROM/Recovery 发布镜像未重建；没有进行全新独立 repo sync/build。LHDC 耳机实际播放、K50 Ultra 和 Vanilla 实机仍待验证。本地设备调查、专用日志实验、账号及签名材料未公开。
