# 内核 / Kernel

batch13 原始 boot：`5.10.269-gki-geff4b40407a1`。

- [内核源码固定提交](https://github.com/LineageOS/android_kernel_xiaomi_sm8450/tree/eff4b40407a1b6f1b1ab84554cbb540bcb495175)
- [设备树](https://github.com/LineageOS/android_kernel_xiaomi_sm8450-devicetrees/tree/2e649a7f3e762903eedad43d8256b91e28b512d8)
- [模块](https://github.com/LineageOS/android_kernel_xiaomi_sm8450-modules/tree/3b30ba7df6608c97c0ba2d55d679a6b5987c4c66)
- 配置入口：源码的 `build.config.common`、`build.config.gki`、`arch/arm64/configs/gki_defconfig` 及设备 BoardConfig。
- 分支标识：`BRANCH=android12-5.10`；`KMI_GENERATION=9`。

早期 16.2.1 boot 的内核为 `5.10.246-gki-g313dfdb07e51`，与本版不是同一二进制。
将本版规范为 `5.10.269-android12-9-g<实际提交>` 是后续计划，尚未实现或测试。
命名修改需要重新验证模块版本匹配及实机启动，不伪造原厂提交或宣称原厂锁定状态。

## English

The batch13 unmodified boot kernel identifies as `5.10.269-gki-geff4b40407a1`.
The exact upstream kernel, device-tree and module commits are linked above and pinned in the manifest.
The older reference image uses a different 5.10.246 kernel binary.
Kernel naming normalization is planned, not present in this candidate.
The Android 12 kernel branch label is independent of the Android 16 userspace version.
