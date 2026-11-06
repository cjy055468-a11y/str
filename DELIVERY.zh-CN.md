# 客机同步死亡流程 corpse4 测试候选

源码 f282f95cacaa33b179bc9da5d49496508f3367e2，Windows实际构建 42254446375：
https://github.com/cjy055468-a11y/str/actions/runs/42254446375

通过：客户端/服务端MSVC编译链接、配套服务端配置生成启动检查、103项测试（原99项保留）、18个Skyrim3.2 PEX编译、四程序PE/版本/哈希/导出检查、两轮源码比较和保留功能审查。

本包仅在loot1上修客机同步死亡：动作快照不抢先写入活着/濒死/死亡之间的生命位转换，完整动作重放保留；确认死亡且场景就绪时允许原生濒死过渡和尸体位置更新。没有自动复活再杀死、重置背包或清空动作队列。已有loot1装备计数及告示板r1原样保留；告示板r2和装备校正提速均不包含。

源码依据和假设见README。未通过IDA/Ghidra或Skyrim实际运行验证。用户的“主机击杀、客机没打过NPC时不可搜索；客机resurrect后kill恢复”与所修路径吻合，是否就是实际根因仍需双人验证。

双方客户端替换SkyrimTogether.exe和EarlyLoad.dll，服务器替换STServer.dll和SkyrimTogetherServer.exe，四件必须同版。保留配置/UI/资源和已安装Missives r1补丁。
