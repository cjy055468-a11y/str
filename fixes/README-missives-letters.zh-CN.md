# STR coopfix4g / Missives 私人信件兼容补丁 1

适用：STR 官方 v1.8.4、Skyrim SE 1.6.1170 x64，以及用户指定的 STR-coopfix4g-test 基准。
已核对用户上传的 Missives.esp，SHA256：5250bae11db78ac1f79d4af7aad9ae936be8469147ef858a97f0b7406bdf63bb。

目的：A 接公告板任务时，不再由 STR 的任务物品共享功能给未接任务的 B 额外塞入 Missives 信件。

## 安装

1. 退出游戏，备份当前 STR 文件和存档。
2. 每位玩家将 SkyrimTogetherReborn 文件夹里的 SkyrimTogether.exe、EarlyLoad.dll 覆盖到实际启动的 STR 目录。MO2 用户覆盖对应 STR mod 目录。
3. 包内 STServer.dll、SkyrimTogetherServer.exe 是同次构建的配套服务端，开服者可一并覆盖。协议未变，原 coopfix4g 服务端也兼容。
4. 保留原 Missives.esp 和原模组脚本、汉化、模型；无需额外 ESP，也不增加加载顺序项。

这是 STR 原生兼容构建，修复位置在 STR 客户端内；不是把源码补丁当成可安装 ESP。需要所有玩家更新客户端，才能让每个接收方都受到保护。

## 实际改动

- 其他玩家获得 Missives.esp 所属书籍/信件（含送信任务的 _M_MiscLetter 杂项信件）时，保留远端角色背包同步，只阻止 STR 把该物品额外复制到本地玩家背包。
- Missives 的任务开始、停止、阶段和登录时任务清单不再发送给队友；接收端也拒绝 Missives 的远程任务更新，避免队友阶段触发本地任务片段。
- 自己接取任务、取得自己的任务信件仍走原模组逻辑。普通 Skyrim 任务的共享逻辑沿用基准。
- 公告板容器同步沿用 coopfix4g；不提供全员任务、别名、奖励或公告列表完全一致功能。
- 保留 coopfix4g 的掉落、穿戴、落点同步、家具退出等修改。相对基准只改两个 C++ 文件并增加一个兼容头文件；无新引擎钩子、偏移或结构布局。

仅按所属插件识别 Missives.esp，支持加载顺序变化。改名、换用其他插件名的重制版未覆盖；人工主动转交信件不在自动复制拦截的范围内。

## 验证和双人测试

构建日志记录 MSVC 编译、配套服务端配置生成、基准现有 75 项测试、PE64/版本/标记/哈希检查和源码范围核对。只有这些检查全部通过才生成成品。
这些检查不代替 Skyrim 双人游戏验证，本包未进行游戏实测。

请用干净的测试存档：A 接普通委托、B 不接，检查 B 的书籍栏没有新增信件；然后交换 A/B、交换队长，测试送信委托、阶段推进和重新连接；A 自己应能阅读任务信并继续任务。再选一项普通原版任务确认原共享行为仍在。提供实际启动目录 logs/tp_client.log 可进一步定位。
已经进入旧存档的垃圾信件不会自动删除，以免误删玩家自己的有效任务信件。

客户端日志标记：STR Missives private letter copy blocked / STR Missives private quest update blocked。
