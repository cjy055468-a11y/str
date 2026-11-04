# coopfix3r1 三轮复核与家具专项核对

上一轮于 2026-11-04 重新 fetch 官方 master/dev：master=54b3a858e228dc8807ed65bc3f9ac3c3f81b610d，dev=711ca1b832790e9035fd05c88a728e88f69c9b4b。针对动画采集、回放、ActorProcess、旧 combat 及插值逐段比较，dev 没有专门解决家具占用/战斗退出的改动；其相关动画和插值变化为看向/头部方向同步。未据此断言官方所有分支、未合并 PR 均无解决方案。

官方 PR 811：https://github.com/tiltedphoques/TiltedEvolution/pull/811，说明已通过回放减少 NPC 滑行、站在椅子上、坐着移动等问题，但明确没有完整解决，尤其连接前的动作未被采集。本次保留官方回放结构，不称此为制作组简单遗漏。

Games/References.cpp 的 AI_SYNC=0 旁明确写着实验未奏效，因此本次不启用该宏。ActorProcess 对 remote 副本跳过本地驱动是单控制端设计，不删除此保护。旧 CombatService 目标代码仍保持官方禁用状态，DamageActor/HookSetPosition/原始 AIProcess 路径均保持不变。

确认的源码事实：Animation.cpp 采集完整 State1/State2；AnimationSystem 回放时直接写回状态位并 ForceAction；原先构造 ActionOutput 时没有填已传输的 targetEventName；TESFurnitureEvent 在当前项目仅空声明，未找到家具专用事件订阅。控制权授予恢复 inventory/values/death/draw 等快照，但没有专门重建家具占用上下文。上述说明风险路径，不证明本例根因。两端都看到悬空也不能单独证明实际存在正常工作的 AI 控制端。

受限恢复并不重写家具同步：仅模拟端、真实 FURN 引用、持续战斗坐姿、有目标、无场景时，先 EvaluatePackage，之后一次 ForceFurnExit；使用既有 ActionEvent 广播和退出缓存语义。标准事件在 AnimationEventLists::kExitSpecial 已列出。新增时序测试仅验证次数/等待/取消及缓存退出语义，不验证引擎家具释放。

没有 IDA/Ghidra 二进制验证。新 occupiedFurniture 字段参考 CharmedBaryon/CommonLibSSE-NG 的 MiddleHighProcessData，0x208，并由 static_assert 与现有 0x218 commandingActor 布局交叉检查。这仍是源码参考，不能称为反编译确认。玩家此前已经同意基于源码尝试。真实坐点/动画根节点/碰撞副作用待游戏测试。

上一版成功的拾取确认与去重算法保留。新角度编码修复的是自定义掉落协议对弧度旋转的整数截断，不把它当作官方问题或无提示浮空的唯一原因。DropProxySetup 的模型就绪/唤醒流程基于公开原生调用和引用包装；未禁用全局碰撞。

用户原始日志、路径和崩溃报告仅用于本地排查，不随公开补丁发布。


r1 是对自己的 coopfix3 新增代码补充区域附加检查，不把此处遗漏归因于官方。服务器账本、消息字段、消息工厂、库存确认及 NPC/尸体身份修复均保留。家具恢复仍不覆盖 sit 为 0/2/4、无有效家具、未进入战斗或无目标的情况；这些是目前明确的覆盖边界，不能用单元测试或编译通过代替游戏证明。
