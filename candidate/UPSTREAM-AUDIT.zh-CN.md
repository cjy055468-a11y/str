# 官方版本与修复范围核对

基础版本：官方 v1.8.4，提交 `54b3a858e228dc8807ed65bc3f9ac3c3f81b610d`。本次核对时官方 `master` 仍指向该提交；抓取到的 `dev` 为 `711ca1b832790e9035fd05c88a728e88f69c9b4b`，较基础版本多 9 个提交。相关掉落物拾取 TODO、动画空队列重置分支和旧战斗目标逻辑在该 dev 提交中仍然存在。此结论限定于实际抓取的这些提交，不代表穷尽所有未合并提案。

## 不能当作“官方遗漏”的证据

- 旧战斗目标逻辑由 `61ebb6e9cb4cb59b455d97fb4f748e90c1c3591f` 主动禁用，提交标题是 `Disable old combat targeting system (to test)`。[PR 633](https://github.com/tiltedphoques/TiltedEvolution/pull/633) 涉及战斗系统调整。该逻辑被注释不能单独证明本次故障由此导致，本包不重新启用。
- [PR 811](https://github.com/tiltedphoques/TiltedEvolution/pull/811) 已明确讨论 slide、skate、T-pose、stand on chairs、move/run while seated 等现象。连接前没有观察到的动作无法直接由重播恢复，是已知设计限制。
- `RemoteAnimationComponent::ReplayCount` 原定义没有显式初始化，但实际 EnTT 3.10 聚合构造会初始化它。生产组件创建/替换测试用来核对这一点，不能据此指责官方存在未初始化错误。
- [PR 937](https://github.com/tiltedphoques/TiltedEvolution/pull/937) 针对 ExtraDataList 锁导致的整进程冻结，其进程转储证据不等于本次 NPC 坐姿故障的证据，未为此扩大合并范围。[PR 901](https://github.com/tiltedphoques/TiltedEvolution/pull/901) 的 Havok 时序修改已经包含在 1.8.4 中。

## 本包有源码和数据测试支持的改动

1. 原生产 `ActionReplayCache` 在 `IdleChairFrontEnter` 后收到 `IdleChairExitToStand` 时，会发出重置标志并返回空动作列表。原客户端仅在存在到期动作的分支处理重置；此条件遗漏可以直接由源码和实际生产缓存测试核对。修复是提前消费该已有指令，没有重写 AI 或强行起身。
2. 原玩家掉落物以背包变化驱动其他客户端生成物品，没有完整的地面实例 ID、消费广播和争抢裁决。新增窄范围协议与账本，而非仅凭 TODO 修改通用背包增减。

测试覆盖数据、协议、并发首次领取和重复请求，但不代替 Skyrim 引擎执行。没有可用 IDA/Ghidra MCP，本包没有二进制反汇编验证；源代码接口的使用、原生 hook 的副作用与家具行为仍需游戏测试。NPC 原生战斗、伤害、ActorProcess、位置钩子与通用容器处理通过范围检查保持不变。
