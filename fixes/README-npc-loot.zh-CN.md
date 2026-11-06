# STR 1.8.4 / Skyrim SE 1.6.1170 NPC 装备计数修订 loot1 测试候选

基于官方 1.8.4（54b3a858e228dc8807ed65bc3f9ac3c3f81b610d）和已送测的 missives2r1（377753b）。匹配四个官方子模块。保留此前尸体布娃娃/搜索、死亡字幕、家具起身、丢物同步、装备显示和告示板空板 r1 修订。

修正范围：只在非玩家 NPC 的背包含 ExtraLeveledItem 标记时，用已解析的动态库存替代对应模板数量。原逻辑把两者相加，会把默认铠甲/武器计入两次。保留不同附魔、强化、左右手、任务标记和合法的多件同款装备；未使用简单的“同款最多一件”规则。普通容器和玩家计数路径不变，不更改死亡流程/碰撞/动画/搜索。已有存档中已经生成的真实重复物品无法凭物品名称安全辨别，不自动删除。

源码依据：本仓库 TESObjectREFR::GetInventory 的模板/动态条目合并，与 CommonLibSSE-NG b93280e832f263dbef44e44cbe2936622a02f91a 的 TESObjectREFR::GetInventory、InventoryEntryData::IsLeveled 及 ExtraDataType::kLeveledItem(0x2E) 对照。仅新增标记枚举读取，复用现有背包接口，没有新地址或 vtable 调用。未使用 IDA/Ghidra 核验；引擎标记含义和事件顺序仍属源码参考假设，用户已授权尝试。编译通过不等于双人游戏验证。

安装：退出双方游戏和服务器，备份原文件。双方客户端替换 SkyrimTogether.exe、EarlyLoad.dll；服务器替换 STServer.dll、SkyrimTogetherServer.exe。四件必须来自本包，版本标识 coopfix4g-missives2r1-loot1，不能混用旧程序。配置、UI、其余 STR 资源保留。MissivesCompat 与 missives2r1 脚本/ESP 源码相同；用 Missives 时继续保留原 Missives.esp、汉化和兼容补丁，补丁覆盖脚本并排在 Missives.esp 之后。不用 Missives 不必安装它。

双人测试：推荐独立测试档，在未被旧版重复同步过的 NPC 上验证。A 先进入区域，B 后进入；检查守卫正常穿衣，击杀后双方分别看同一尸体的铠甲/武器数量，B 取一件后 A 重开尸体确认减少，不再出现第二套。换 B 先入区重测，并检查断线重连/切区域不增加装备。合法两把同款武器应保留，附魔/强化不丢。回归客机尸体倒地/原位搜索与死亡字幕，以及丢物、告示板。异常时提供双方 tp_client.log 和 STServerOut.log，注明谁先入区、具体 NPC、发生时间及两边数量。

新增六项纯库存数据/真实消息编解码测试；必须保留原 93 项测试。Windows x64 MSVC 实际编译、服务端配置生成启动检查、18 个 PEX 编译、四程序 PE/版本/哈希/导出和两轮源码比较通过后才发布。本包不包含守卫犯罪追捕和 Immersive Citizens 兼容改动。
