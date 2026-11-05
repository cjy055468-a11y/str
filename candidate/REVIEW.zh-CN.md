# corpse2 两轮复核

第一轮对比已交付corpse1与实际游戏测试过的4g：确认actions.clear、ReplayCount清零和死亡提前return已撤回；每帧LoadAnimationVariables继续运行；HookActorProcess与4g相同。仅Actor.cpp/.h、AnimationSystem.cpp、InterpolationSystem.cpp和InterpolationComponent.h有本次改变，其余累计修复保留。

第二轮从干净官方分别重建4g/netdiag1、corpse1与corpse2，逐文件核对并检查增量边界，确认没有Missives代码、没有改协议/服务器/战利品。实际运行Windows MSVC客户端/服务器构建、75项执行测试、配套配置生成启动检查、PE64/版本/新回放标记与交付哈希，并对照官方原始三件及上一版四件的导入导出。实际执行结果见verification.json和构建日志。

本次编译与源码复核不能代替双人游戏验证；站尸回归是否恢复、搜索点是否贴合可见尸体均需要测试，不作已解决承诺。

实际构建结果：run42069705469 / source6b1635e0cb759a7f80c618a132cd324a1a13c68c，客户端/服务器编译链接、配置生成启动检查、75项执行测试、PE64/标记/哈希、两轮源码对比及官方/4g导入导出检查全部通过。未运行Skyrim游戏；引擎假设仍待游戏测试。
