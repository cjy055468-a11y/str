# 晚上测试顺序

两名玩家都退出游戏，在MO2实际加载的STR模组目录备份并替换SkyrimTogether.exe和EarlyLoad.dll。服务器若已经是4g/netdiag1/corpse2可保持；若从官方原版首次使用累计修复包，停服后也替换STServer.dll及SkyrimTogetherServer.exe，保留STServer.ini与资源。

1. 新击杀一个普通、非任务NPC，优先比较主机与客机的倒地过程。客机观察是否自然落地并适应地形，是否仍永远固定在同一动作；有条件再观察本地轻推/产生物理作用的攻击。单凭不跟随主机推动，不能证明客机布娃娃未启用：本版没有完整逐骨骼姿态网络同步。
2. 客机直接瞄准可见尸体躯干，检查搜索提示、能否打开战利品，以及取走物品是否同步。不要只用旧版已经卡住的尸体判断新生成流程。
3. 最后一个敌人死亡后等待至少5秒，检查呻吟字幕是否消失、是否还会刷新。顺便确认活人正常对白/任务场景仍可播放。

若仍异常，请保留两端新tp_client.log和服务器日志，记下NPC/地点与大约时间。客户端日志中：STR corpse native process eligibility说明原生更新是否获准及前置条件；STR corpse death playback的dead/ragdoll反映实际状态；STR corpse graph probe为只读动画驱动探针；STR corpse life-state guard说明旧动作是否试图覆盖死亡；STR corpse speech cleanup记录字幕清理。入口获准不代表物理必然成功，编译/83项纯数据及既有测试也不能证明游戏效果。

旧版已被写入FFFF标志或动画队列已损坏的副本不保证自动恢复。请同时测新击杀和重新连接后的表现，避免批量复活/重置任务。既有掉落物、服装、家具起身修复仍保留；随机断线根因尚未确认。
