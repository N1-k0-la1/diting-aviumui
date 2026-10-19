# 文件夹拖出后模糊残留修复 · 2026-10-17

反馈步骤：将 dock 中的应用拖到桌面应用上创建双应用文件夹，再从文件夹拖出任意一个应用，桌面持续模糊。

`Folder.onDragStart()` 会移除被拖动的图标；随后 `completeDragExit()` 请求关闭文件夹。`animateClosed()` 对只剩零或一个图标的文件夹直接执行 `closeComplete(false)`，没有创建负责将 `folderDepth` 降至零的关闭动画，也没有终止可能还在运行的打开动画。因此，即使文件夹已经关闭或解散，文件夹模糊通道仍可能保留非零值。

新增补丁只在这条快速关闭分支中先取消当前文件夹动画，再将文件夹深度清零。普通多图标文件夹的动画顺序保持原样；原有快速返回桌面修复及状态、小组件深度通道保持原样。

- Launcher 源码提交：`7e9b22915760d8fcbe565afa334e195b59187c27`，父提交 `fd0dc4d15f96428e2a5184e825b5e25ed97460e7`。
- 增量补丁：[01_packages_apps_Launcher3.patch](patches/folder-drag-20261017/01_packages_apps_Launcher3.patch)，为有序系列第 90 份。前 89 份补丁不变。
- 新增回归：[folder-drag-close-regressions.py](tests/folder-drag-close-regressions.py)。在修复前执行生产方法出现 `closed folder retained blur`，修复后通过。
- 回归执行实际的 `onDragStart`、`completeDragExit`、`handleClose`、`cancelRunningAnimations`、`animateClosed` 方法；Android 视图和动画为主机替身。覆盖两图标分别拖出、打开动画未结束时拖出、零/单图标关闭、非动画关闭、普通动画关闭及重复关闭。
- 删除清零或删除快速关闭分支的旧动画取消，各自都被反向测试拒绝。
- 既有 `folder-blur-regressions.py`、`launcher-resume-depth-regressions.py`、`round6-behavior-regressions.py`、`round6-regressions.py` 均通过。
- 全部 90 份公开补丁在临时索引中按序回放，31 个项目的树与公开源码目标完全一致。

桌面组件编译、实际 DEX 分支检查及后续 batch28/batch29 两变体整包与主机产物审核均通过。2026-10-19 维护者在 batch29 验收后反馈 12T Pro GMS 没有问题；这不等于两台机型或全部拖拽场景逐项通过。历史成品与校验值保持不变。当前交付及验证范围见 [发布说明](RELEASE.md)。
