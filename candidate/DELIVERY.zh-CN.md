# NPC 装备重复计数修订 loot1 测试候选

源码 69e9b471ad684fb159cf70f48d5c8ea3352c03d4；实际 Windows 构建 run 42237137423：
https://github.com/cjy055468-a11y/str/actions/runs/42237137423

已通过：Windows x64 客户端/服务器实际编译链接、配套服务端配置生成启动检查、99项测试（原93项保留，新增6项纯库存数据/真实消息测试）、18个Papyrus脚本编译及Skyrim PEX3.2检查、四件程序架构/版本/哈希/导出检查、两轮源码比较、插件结构/对话条件检查。公开下载文件另进行完整ZIP及逐文件SHA256回读核对。

只修正带ExtraLeveledItem标记的非玩家NPC库存：动态数量替代对应模板数量，避免默认装备被累计两次，保留合法多件装备与附魔/强化/左右手/任务标记。普通容器与玩家读取路径不变。上一个已测通过的尸体布娃娃、搜索、字幕与家具/丢物逻辑不变，告示板r1和18个脚本源码、ESP也原样保留。

相对missives2r1只修改五个源码文件：
- Code/client/Games/Skyrim/ExtraData/ExtraData.h：补充现有LeveledItem标记编号0x2E，仅供读取。
- Code/client/Games/Skyrim/TESObjectREFR.cpp：仅对有此标记的非玩家NPC使用修正的库存合并。
- Code/encoding/Structs/NpcInventorySnapshot.h：纯数据计数合并，避免模板和已解析数量重复叠加。
- Code/tests/npc_inventory_snapshot.cpp：六项数据及真实协议工厂回归测试。
- Code/common/BuildInfo.h.in：loot1版本标识，避免程序混用。

这是源码参考修复候选。参考CommonLibSSE-NG库存读取方式，未通过IDA/Ghidra及Skyrim实际运行验证，不能据编译宣布所有双人掉落问题已解决。已存在的真实重复物品无法与合法战利品安全区分，不自动删除。请用未受旧版同步影响的新NPC测试。守卫犯罪追捕及Immersive Citizens仍在队列中。

安装见README.zh-CN.md：双方客户端更新SkyrimTogether.exe、EarlyLoad.dll，服务器更新STServer.dll、SkyrimTogetherServer.exe；四个程序必须同版。本包Missives脚本/ESP与r1源码相同，已有r1兼容补丁可继续使用。原配置、资源与Missives.esp/汉化保留。
