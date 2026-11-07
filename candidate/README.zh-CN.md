# STR 1.8.4 / Skyrim SE 1.6.1170：远端 NPC 尸体同步排查候选 corpse4k

本候选严格以已交付的 `STR-coopfix4g-corpse4-test` 为基线，基线完整源码补丁为 `coopfix4g-corpse4-v184.patch`，官方源码提交为 `54b3a858e228dc8807ed65bc3f9ac3c3f81b610d`。本次只有 `corpse4k-delta.patch` 列出的 9 个文件变化；不包含 4h/4i 后续修改，也保留 4g 中已测试包的 NPC 战利品、掉落物同步和 Missives r1 文件。

## 根因判断

**源码已证实：**

- 攻击者客户端的 `HookDamageActor` 在本地玩家命中 NPC 时调用原生 `RealDamageActor`；非攻击者客机通过服务器的血量广播更新血量，只有本地 `IsDead()==false` 且血量不大于零时才调用 STR 的 `Actor::Kill()`。
- 远端死亡通知同样只在本地 `IsDead()` 与服务器通知不一致时调用 `Kill()` 或 `Respawn()`。
- 4g 的 `AnimationSystem` 即使过滤了快照中的死亡生命位，仍会把 `Ragdoll` 动作交给 `ForceAction`。此前候选的客机日志记录到：同一远端 NPC 已经 `dead=true, ragdoll=true` 后，仍回放一个 life-state 为活体 `0x1000041` 的 `Ragdoll` 快照；动作成功后，该引用转为 `dead=false, ragdoll=false`。这证实陈旧动画动作能够短暂覆盖已确认尸体状态，但这份日志没有确认该尸体是否就是不可搜索样本。
- 远端 NPC 的 Actor Process 默认被 STR 拦截；只有死亡过渡被标记为可运行时才调用游戏原生处理。4g 在死亡通知后才尝试打开该标记，时序上可能晚于 `KillImpl` 的开始。

另有一次日志记录到远端 NPC 收到 life-state 为 `dying` 的 `Ragdoll` 快照（`0x200041`），4g 的生命位保护把本地状态 `0x41` 保留下来。两条日志共同证明动画事件与原生死亡状态分开传播，且陈旧 `Ragdoll` 可以扰动已确认尸体。它们仍不能单独证明这种扰动造成了“无搜索提示”；日志没有记录当时的搜索激活回调是否触发。

**最可能根因：** 远端姿势动作和本地原生死亡状态竞态，特别是已确认死亡后又应用携带活体 life-state 的陈旧 `Ragdoll`，令尸体状态短暂回到非死亡/非物理状态。未确认的 dying/dead `Ragdoll` 也可能先于本地原生 `KillImpl` 到达。两种路径都可能让后续受 `IsDead()` 保护的死亡入口无法完成同一转换。此判断由实际旧日志状态序列和源码条件共同支持，但尚未通过 Skyrim 二进制反汇编或双人游戏测试证明它与不可搜索结果直接因果。

## 本次最小改动

远端非玩家 NPC 收到 dying/dead 的 `Ragdoll` 或 `RagdollInstant` 时，跳过该动作，让健康广播或服务器死亡通知走现有本地 `KillImpl`。若服务器已确认死亡，或本地已是尸体，即使动作快照错误地带着活体 life-state，也跳过陈旧 Ragdoll，避免 `ForceAction` 把现有死亡状态翻回活体。活着的 NPC 的非终结 Ragdoll 仍照常回放。没有新增第二次 Kill，不改变其它动画动作、网络协议、容器或战利品流程。

当远端 NPC 的现有 `Kill()` 确实运行时，先为该死亡过渡打开 STR 原生 Actor Process 通道；服务端确认消息尚未来到时，只要 actor 仍处于 dying/dead 状态，就保留这条通道。复活会清除此标记。其他远端 NPC 的 AI 和移动过滤保持原样。

新增日志可用 `local_player`、服务器实体 ID、owner、epoch 和本地引用 ID 对齐双方的致命命中路径、被跳过的 Ragdoll（记录快照 life-state、服务器确认和本地尸体状态）、血量广播、死亡通知、`KillImpl` 前后状态、原生处理标记，以及是否有尸体激活事件到达 STR。没有激活事件只表示交互没有进入 STR 的事件回调；它本身不能区分碰撞、瞄准或引擎交互状态。

## 构建和测试状态

`corpse4k` 尚未完成 Windows x64 构建和 Skyrim 双人测试前，不应当作修复成品安装。源码差异已能应用到指定的官方 1.8.4 提交；独立 C++ 检查覆盖终结动作筛选条件。GitHub Actions 还会检查固定子模块、回退 4g 精确基线、编译客户端/服务器与 Papyrus、执行全部单测、核验四个 PE32+ x64 文件和 SHA256。

若 Actions 构建通过，双方客户端必须同时替换 `SkyrimTogether.exe`、`EarlyLoad.dll`，服务器同时替换 `STServer.dll`、`SkyrimTogetherServer.exe`；四件需来自同一 `coopfix4g-corpse4k-native-death` 包。保留配置、UI/资源、存档、Missives.esp/汉化和 4g 的 Missives r1 兼容文件。不要混用其他 STR 构建。

## 双人验收

使用新刷出的 NPC，不使用旧存档中已卡住的尸体。分别测试房主击杀与客机击杀；每种情况至少覆盖普通近战、法术和终结动作。客机/房主都检查死亡姿势、尸体可搜索和搜索位置；确认整个过程没有控制台复活或重复 Kill。之后再测试死亡后切区重进、尸体初始入区和所有权移交。

出问题时先保留双方本次 `tp_client.log` 和 `STServerOut.log`，并记录哪一方击杀、哪一方看不到搜索提示。重点查看该尸体的 `STR corpse ragdoll action deferred`、`STR corpse health relay`、`STR corpse death notify`、`STR remote NPC KillImpl begin/end`、`STR corpse activate event`。编译通过不代表游戏问题已解决；是否通过验收以双人实测为准。
