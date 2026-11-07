# corpse4k 源码审查：反向状态与副作用

独立从补丁落点反查其影响：

- Ragdoll 筛选只作用于远端 NPC：dying/dead 快照总是跳过；服务器已确认死亡或本地已是尸体时，活体 life-state 的陈旧 Ragdoll 也跳过。玩家、活着的远端 NPC 普通 ragdoll、战斗/移动/坐姿动作都继续走旧路径。
- 动作被丢弃后队列计数同步递减，避免队列卡住；函数不改 `LastRanAction`、actor flags、动画变量、装备或背包，也不创建/删除实体。新单测覆盖旧日志中的“确认死亡 + 活体快照”顺序，并确认普通存活 NPC 的 Ragdoll 仍通过。
- `Actor::Kill()` 的调用条件未放宽，因此本补丁不对已经标记死亡的 actor 重复执行 `KillImpl`，不额外派发伤害、经验、战利品或网络死亡消息。
- 原生 Actor Process 标记只在远端 NPC 的 dying/dead 过渡可见，恢复生命状态通过 `Respawn()` 清除。`HookActorProcess` 原有的 remote/player 过滤保持不变。
- 血量和死亡消息格式、服务器权威 owner/epoch 校验及转发对象均未改变。服务端改动只有诊断日志；尸体容器、库存、掉落物和 Missives 数据路径没有新增逻辑。
- 新交互日志只观察已发生的 `ActivateEvent`。它不宣称可读 Havok 碰撞体，也不从模型或内存布局推测搜索位置。
- 日志只在致命命中、致命血量、死亡状态、终结动作、远端 KillImpl 和尸体激活事件写入；一般每帧/每次动画变量没有新增日志。

静态风险仍在：Skyrim 原生 `KillImpl`、`ForceAction` 与 Havok 初始化顺序并没有用 1.6.1170 的 IDA/Ghidra 数据库核实。若本地和服务端均未将死亡标记为确认，且 Ragdoll 快照仍带活体状态，代码会保留原播放路径；新日志可识别该序列。若本地 `KillImpl` 后 `IsInRagdollState` 仍为 false 或没有激活事件，Ragdoll 覆盖可能不是唯一原因，应根据新日志继续定位。构建与单测不能替代游戏内验收。
