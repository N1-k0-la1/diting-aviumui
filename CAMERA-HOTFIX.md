# diting 系统相机修复（2026-10-10）

适用于本项目已发布的 AviumUI 16.2.2 batch14 Vanilla / GMS。
这是约 8 MB 的系统相机更新 APK，使用与两版原相机相同的发布证书；直接覆盖安装即可，不需要 root、电脑或重刷 ROM。

## 安装

手机拿到 `Aperture-diting-camera-fix-20261010.apk` 后，点击文件并按系统提示安装“相机”更新。安装完成后重新打开相机。
若安装失败，请保留完整提示；其他作者的 ROM、不同证书或较早的本项目构建不在此包的确认范围内。

电脑安装也可使用一台已授权、通过 USB 连接的手机：

```powershell
adb -d install --no-incremental -r Aperture-diting-camera-fix-20261010.apk
```

## 修复内容

录像从主摄 1080p / 4K 切到右侧 1.1x 微距时，根据镜头实际输出尺寸自动回退到 720p，避免请求不支持的 1920×1080 流后退出。
只支持 SD/HD 的镜头使用其原生帧率范围，微距不再显示实际无效的 60fps。切回主摄保留原分辨率/帧率偏好。

在 12T Pro 实测：1080p/30fps、4K/30fps 切换与返回；1080p/60fps 切入微距回退到 720p/24fps；短视频成功保存并完整解码。K50 至尊版尚待实机反馈；HDR 与长期回归不在本轮验证范围内。

## 回退与后续

在“设置 → 应用 → 相机 → 右上角菜单 → 卸载更新”可恢复 ROM 内的原版相机。不要把“卸载更新”当作“清除数据”。
后续整包更新若相机仍使用此次单独安装的更新，可以卸载更新以使用新 ROM 内的版本。
原 batch14 ROM ZIP 的内容和哈希保持原有记录；本次没有生成新整包，也未加入 Dolby Vision / LHDC。

## 源码与鸣谢

系统相机基于 LineageOS Aperture（Apache-2.0）。修改见随包 `01_aperture_video_capabilities.patch`。
基线 commit：f7c0a93f787cc9e0db4193b6094bd51575567898。
项目：https://github.com/N1-k0-la1/diting-aviumui
感谢反馈的 K50 用户和所有上游贡献者。

## English

A signed camera app update for this project's released batch14 Vanilla/GMS ROMs. Install the APK as an update; no root or reflashing is needed. Both original camera certificates were checked against this update.

Unsupported SDR video profile resolutions are filtered against each lens's actual Camera2 output sizes. HD-only cameras retain their native frame-rate ranges. The macro lens falls back to 720p; returning to the main lens preserves its quality/FPS preference.

Validated on Xiaomi 12T Pro: FHD/UHD lens switching and return, 60fps-to-macro native-FPS fallback, saved short video and complete decoding. K50 hardware, HDR and long-term regression remain unverified. Uninstall camera updates in app settings to return to the ROM-bundled app. After a future ROM update, uninstall this standalone update if needed to use its newer bundled camera.
