# corpse4k 源码审查：反向状态与副作用

独立从补丁落点反查其影响：

- 终结动作筛选只作用于远端 NPC 且死亡生命状态为 dying/dead。玩家、同名但没有死亡状态的普通 ragdoll 动作、战斗/移动/坐姿动作都继续走旧路径。
- 动作被丢弃后队列计数同步递减，避免队列卡住；函数不改 `LastRanAction`、actor flags、动画变量、装备或背包，也不创建/删除实体。
- `Actor::Kill()` 的调用条件未放宽，因此本补丁不对已经标记死亡的 actor 重复执行 `KillImpl`，不额外派发伤害、经验、战利品或网络死亡消息。
- 原生 Actor Process 标记只在远端 NPC 的 dying/dead 过渡可见，恢复生命状态通过 `Respawn()` 清除。`HookActorProcess` 原有的 remote/player 过滤保持不变。
- 血量和死亡消息格式、服务器权威 owner/epoch 校验及转发对象均未改变。服务端改动只有诊断日志；尸体容器、库存、掉落物和 Missives 数据路径没有新增逻辑。
- 新交互日志只观察已发生的 `ActivateEvent`。它不宣称可读 Havok 碰撞体，也不从模型或内存布局推测搜索位置。
- 日志只在致命命中、致命血量、死亡状态、终结动作、远端 KillImpl 和尸体激活事件写入；一般每帧/每次动画变量没有新增日志。

静态风险仍在：Skyrim 原生 `KillImpl`、`ForceAction` 与 Havok 初始化顺序并没有用 1.6.1170 的 IDA/Ghidra 数据库核实。源码筛选若错过实际事件名，日志会显示该动作仍被回放；若本地 `KillImpl` 后 `IsInRagdollState` 仍为 false 或没有激活事件，当前假设就不完整，应根据这次日志继续定位。构建与单测不能替代游戏内验收。
