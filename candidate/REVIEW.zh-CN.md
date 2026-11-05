# corpse1 两轮复核

第一轮检查相对已交付netdiag1的修改范围：仅Actor.cpp、InterpolationComponent.h、InterpolationSystem.cpp、AnimationSystem.cpp。物品/装备/家具/尸体战利品/服务器诊断和协议段不改变。存活NPC与远端玩家不进入新路径；新死亡/迟到动作/已有尸体/卸载和复活分支逐项审阅。

第二轮将已交付4g、netdiag1与当前完整补丁分别应用于干净官方文件，核对实际编译补丁和工作文件，比较保护文件及官方/4g二进制导入导出；实际执行Windows MSVC客户端/服务器构建、现有75项纯数据/协议测试、配套配置生成启动检查、PE64/版本/新标记与交付哈希。保留现有全部测试；未增加伪装成引擎测试的断言。

这里描述复核项目，实际结果须以本包的verification.json和构建日志为准。尚未在Skyrim中验证尸体搜索位置，也未确认断线根因。
