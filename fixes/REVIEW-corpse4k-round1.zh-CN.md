# corpse4k 源码审查：正向调用链

基线：官方 v1.8.4 `54b3a858e228dc8807ed65bc3f9ac3c3f81b610d` + 已交付 `STR-coopfix4g-corpse4-test`。仅审查远端死亡、动画动作、进程门控及交互回调。

1. `HookDamageActor` 先判断攻击者身份。本地玩家攻击 NPC 会触发 `HealthChangeEvent` 并执行原生 `RealDamageActor`；远端玩家对本地 NPC 的该分支只返回致死判定。此差异能说明攻击者侧和旁观端为何可能走不同死亡路径。
2. 本地健康事件发给服务器。服务器转发负血量增量给其他范围内玩家；接收端经 `ForceActorValue` 更新血量，并且只有当前 `IsDead()==false` 且血量不大于零时才调用 `Actor::Kill()`。
3. 拥有者的 `RunDeathStateUpdates` 将死亡布尔值和所有权 epoch 发给服务器。服务器只接受当前 owner/epoch 并向其他客户端广播。接收端按 `server id + epoch` 找远端 actor；仅当本地 `IsDead()` 与消息不同才调用 `Kill()` 或 `Respawn()`。
4. 并行的动作流进入 `AnimationSystem`。原 4g 在保护死亡生命位之后仍调用 `ForceAction(Ragdoll)`。新辅助条件只筛远端非玩家、事件名为 `Ragdoll`/`RagdollInstant` 且来态为 dying/dead 的情况；筛中时只减少队列计数并移除这一项，不改 actor flags、动画变量或其它动作。
5. 接下来让既有血量或死亡消息执行唯一正常死亡入口。远端 NPC 的 `Kill()` 在 `KillImpl` 前设置 native corpse-process 标记；`RunRemoteUpdates` 在死亡过渡期间保留它，使现有 `HookActorProcess` 允许原生处理。其他远端 actor 仍走原有移动/AI 抑制逻辑。`Respawn()` 清除标记。
6. 尸体交互只有在 Skyrim 触发并派发 `ActivateEvent` 后才进入 `ObjectService::OnActivate`。新增日志记录这个回调是否出现以及引用坐标；它不会改变交互本身。

本轮确认的是调用顺序和状态门控的源码事实。`ForceAction` 是否确实把相应远端 actor 推进到“IsDead 已真但 KillImpl 未完整执行”的状态，仍要看本次运行的前后日志和双人测试。
