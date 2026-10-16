# OFRP 第二轮核实与修复（review2）

基于 review1 的实际设备树、Recovery 核心、Android 16 init/构建系统/驱动和已打包镜像逐项核实。
新增源码包在 [`recovery/orangefox-diting-20261016-review2`](recovery/orangefox-diting-20261016-review2/README.md)。
历史补丁包、镜像、哈希及验收记录不改写；ROM 85 份补丁不变。新版仍须独立进行手机验收。

## 已确认并修复

### P1：备用安装器的签名失败没有向调用者传递

`bootable/recovery/twrpinstall/install.cpp` 的 `verify_package()` 在有可用证书、但 `verify_file()`
返回失败时仍返回 true。恢复失败返回。主界面 `TWinstall_zip()` 在用户启用签名检查后直接调用
`verify_file()`，原本会中止；不能将此问题描述为主界面无条件跳过了所有签名检查。
没有改变 TWRP 允许用户主动选择是否检查 ZIP 签名的既有设置。

### P1：公共 init 与设备树的 USB 规则同时生效

`TW_EXCLUDE_DEFAULT_USB_INIT` 只排除额外的 `init.recovery.usb.rc` 模块；并不删除
`bootable/recovery/etc/init.rc` 中的公共 USB 规则。实际成品有 fastbootd 的 FunctionFS 挂载与
fastboot/sideload 规则，所述“完全缺失”不成立。但公共的 adb/none 规则又与设备文件重复操作 configfs，
这是本轮确认的跨文件缺陷：规则执行顺序不同会造成重复链接、修改已绑定配置等错误。

`etc/init.rc` 在 early-init 读取启动属性，默认保留公共 USB 配置；仅设备明确声明
`vendor.recovery.usb.device_config=1` 时让设备规则接管。设备树补齐 fastbootd/sideload 的挂载、
就绪触发、清理和绑定，并在 none 模式停止 fastbootd。共用服务定义保留。
其他设备的默认行为不要求新增配置。fastboot/sideload 按现有调用者先切 none、再切目标模式的流程验证。

此前测试只执行了设备文件；本轮把公共与设备规则一起执行，并设置去掉互斥条件的负面对照。
不把模拟执行的通过结果当作 USB 硬件验收。

### P1：旧兼容归档被解压后就当作兼容通过

`twrpinstall/installcommand.cpp` 的 `verify_package_compatibility()` 没有实际验证兼容性，
还会按不可信长度解压外层和内层内容，缺少上限、空数据保护，并在关闭 ZIP 后才结束迭代器生命周期。
当前 Android 16 `system/libvintf` 已不提供旧的 ZIP-vector 兼容验证接口；Recovery 版本头文件明确说明
不提供 Treble 分割兼容检查。直接调用提示词给出的旧接口不能编译，也不能提供正确的验证。

现不再分配或解压这个不支持的旧归档：缺少 `compatibility.zip` 时按现代包流程继续；存在时明确返回失败，
不再误报已经验证兼容。构建者显式设置 `OF_NO_TREBLE_COMPATIBILITY_CHECK=1` 的既有编译策略保留；
当前设备配置为 0，没有提供手机界面上的跳过开关。
主界面两种 OTA 路径都在运行脚本或卸载分区前执行这项检查，而非只检查传统脚本包。

**行为边界：** 本轮没有实现现代平台已移除的旧 VINTF 验证能力。默认检查开启时，携带旧归档的包会被拒绝，
包括可能兼容但无法证明兼容的旧包。本项目已交付的 reviewfix20261015 GMS 和 Vanilla ZIP 均不含该归档，
已只读核对，不受此限制。此结论不代表任意第三方旧 ROM 都兼容。

### P1：独立 Recovery 分区采用了全 ramdisk 重打包选项

`fox_diting.mk` 的 `OF_RECOVERY_AB_FULL_REFLASH_RAMDISK=1` 会让
`twrpRepacker::Flash_Current_Twrp()` 跳过专供独立 Recovery 分区的槽位复制分支。
移除该选项，保留设备的独立 recovery_a/recovery_b 路径。没有通过真机写入来测试重装功能。

### P2：增量包多指纹误拒绝、重复验证和错误状态遗漏

`twrpinstall/install.cpp` 改为按 `|` 精确匹配 `pre-build` 指纹列表；仍拒绝只匹配前缀的指纹。
`installcommand.cpp` 去掉第二份重复的增量版本/指纹检查，统一调用 `CheckPackageMetadata()`。
设备名和序列号的严格检查保留。

`TWinstall_zip()` 的 A/B 预检查失败后不再直接返回跳过公共错误处理。
先显示明确错误，再进入既有状态尾部，正确写入安装失败/损坏状态；失败时不挂载、不运行预刷脚本和更新器。
没有将设备验证推迟到预刷脚本之后。

同时给 `install/install.cpp` 的另一份实际元数据读取器补上空数据和 1 MiB 上限，
避免与此前已保护的 TWRP 读取器出现边界差异。

### P2：构建默认值、分区声明与 ADSP 兼容性

官方复现脚本已在 envsetup 前设置 `FOX_BUILD_DEVICE`，不是本次成品的构建失败原因。
不过只依赖有条件的 vendorsetup 环境导出并不稳妥；产品文件补上对应 FOX 默认值，
使所选产品的 A/B、Vanilla、目标设备名等配置不依赖用户先后执行命令的顺序。

`device.mk` 的构建期 A/B 分区声明补齐 system/system_ext/product，与动态分区声明对应。
这不等于旧 Recovery 安装外部 payload 时必然漏刷这些分区；已有整包安装成功记录不能据此推翻。

ADSP 固件身份识别补充 `adsp*.mbn`；原 diting 的 `.mdt` 路径保留。
这属于兼容性加固，没有实机证据说明原 diting 正常固件名会触发该问题。

## 核实后未按建议修改的项目

| 审查说法 | 当前源码证据与处理 |
|---|---|
| init 不支持 `${属性:-默认值}` | 不成立。`system/core/init/util.cpp` 的属性展开实现明确支持，保留。 |
| 正常启动没有设置 MTP 实现属性 | 不成立。`vendor.prop` 已声明 `vendor.usb.use_ffs_mtp=1`，成品启动属性亦包含；不是只在 charger 事件设置。 |
| `BOARD_RECOVERY_IMAGE_PREPARE` 无效、KeyMint 链接不会生成 | 不成立。当前 `build/make/core/Makefile` 在创建 ramdisk 时执行它；成品内三个旧名称链接及依赖已核对，保留。 |
| 2099 SPL、Recovery build tag 导致正常 OTA 必然被拒绝 | 不成立于实际主界面路径。AOSP `install/install.cpp` 与链接的 `twrpinstall` 是不同实现；TWRP 路径没有调用所指 SPL 检查，时间戳约束原本禁用，启动代码也将日期属性归零。没有盲目改动解密用的平台版本/SPL。保留策略，不声称本轮实现了 OEM 防回滚。 |
| 卸载 system 后读取属性必然失败 | 不成立。检查读取的是启动时已经加载/覆盖的属性服务值，不是在此处直接读取分区文件。后面为 backuptool 挂载 system，并不是加载这些值的前置条件。 |
| fastbootd 没等模块便能对不存在节点写入 | 原脚本已等待远程处理器节点及可写启动节点，不能据 RC 缺少额外属性条件就认定会写不存在节点。保留节点等待，不增加可能阻止 fastbootd 初始化的条件。 |
| firmware 卸载必定 EBUSY | 未证实。现有流程先等远程处理器运行及供电节点，再由 init 卸载；失败不会假报挂载已释放。没有改为强制卸载来掩盖实际错误。 |
| Goodix 复位没有等待、亮屏脚本没有入口 | 不成立。实际驱动 reset sysfs 写入同步调用带等待的硬件复位，`gui/blanktimer.cpp` 已调用亮屏脚本。保留既有互斥与后台检查。 |
| 所有设备名列表都应同时支持逗号和竖线 | 未采纳。配置允许逗号，OTA 元数据的列表使用竖线；按字段分隔符严格匹配更明确，没有必要接受非标准元数据来修复一个未复现的问题。 |

## 验证范围

结果见新增包的 `HOST-TESTS.json`、`SOURCE-VALIDATION.json`、`IMAGE-AUDIT.json` 与根目录 `VALIDATION.json`。
测试执行实际提取的签名结果处理、安装器函数和 GUI 错误分支；受控替身只替换 ZIP/进程/属性等外部接口。
公共/设备 init 联测覆盖 128 种切换、默认设备三种模式；签名失败返回和公共错误尾部均有负面对照。
原有触控并发、ADSP、设备别名、辅助脚本测试保留，补充多指纹、两份元数据读取器边界及 `.mbn` 用例。

完整编译和静态镜像核验不能代替真机验证。新镜像仍需启动、数据解密、触控、USB/fastbootd/Sideload、
正常签名 OTA 与系统启动/快照合并验收；独立 Recovery 重装功能也仍待硬件测试。
没有刷机、清除数据、改写 ROM/boot 或发布私有 Lineage 调试日志改动。
