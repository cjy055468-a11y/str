# coopfix3 交付检查

基于官方 STR 1.8.4，面向 Skyrim SE 1.6.1170 / Windows x64。

实际构建：https://github.com/cjy055468-a11y/str/actions/runs/41864842460
源码提交：ef13a56dbd6d2627e6670b630718111d6d8928d7
构建已完整成功，55 项测试通过（28 项必需专项测试），失败 0。
三项检查：真实编译链接及匹配服务器配置生成启动；四件 PE64/版本/修复标记和导入检查；重复构建成功且四件 SHA256 不变。
本地另核对 ZIP、原始三个文件的导入/导出，以及候选补丁与源码提交一致。
编译仍有上游已有的转换、弃用等警告，并非零警告构建；新家具恢复和代理初始化没有报告编译错误。

测试性质：尝试版，未在游戏中验证。重点尝试让真实战斗中卡坐姿、且占用有效家具的 NPC 退出交互。无目标、无有效家具引用、未进入战斗或处于场景中的 NPC 会跳过。不能据此保证所有仇恨和正常坐姿悬空都已修好。

安装：备份后，两名玩家各替换 STR 实际目录的 SkyrimTogether.exe、EarlyLoad.dll；服务器替换启动目录的 STServer.dll、SkyrimTogetherServer.exe。同一目录则覆盖四件。保留原版资源/脚本/配置，四件不是完整 MOD。协议 v1.8.4-coopfix3，客户端与服务器须匹配。

测试：两人轮流先进入区域、先攻击坐椅敌人，观察进入战斗后约 4–6 秒是否起身，交换队长重复；分别检查正常坐下悬空、任务场景、骑马；再回归掉落物互捡、同时捡、区域重入、重连、尸体搜刮及随机遭遇。
若仍卡住，保留两端同一次会话的 logs/tp_client.log；新标记 STR furniture hit audit / recovery observed / reevaluate / exit，其中 accepted=true 仅表示事件被接受。日志位于实际启动的 SkyrimTogether.exe 旁边。

相比已交付 coopfix2，本次改变／新增的源码文件如下。包内完整补丁还包含之前修复，详细引擎假设见 UPSTREAM-AUDIT.zh-CN.md。

- Code/client/Games/Skyrim/Forms/TESForm.h
- Code/client/Games/Skyrim/Misc/MiddleProcess.h
- Code/client/Services/DroppedItemService.h
- Code/client/Services/FurnitureService.h
- Code/client/Services/Generic/DroppedItemService.cpp
- Code/client/Services/Generic/FurnitureService.cpp
- Code/client/Systems/AnimationSystem.cpp
- Code/client/Systems/DropProxySetup.h
- Code/client/Systems/FurnitureRecovery.h
- Code/client/World.cpp
- Code/common/BuildInfo.h.in
- Code/encoding/Structs/DroppedItemData.cpp
- Code/encoding/Structs/DroppedItemData.h
- Code/server/Services/DroppedItemService.cpp
- Code/tests/animation_replay_cache.cpp
- Code/tests/dropped_items.cpp
- Code/tests/proxy_furniture_timing.cpp
