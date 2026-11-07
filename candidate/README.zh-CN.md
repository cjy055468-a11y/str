# STR 1.8.4 / Skyrim SE 1.6.1170：远端 NPC 尸体收发诊断版 corpse4l

本版基于已测试的 `STR-coopfix4g-corpse4-test` 和其后续 corpse4k 尸体状态修复；官方源码锁定为 `54b3a858e228dc8807ed65bc3f9ac3c3f81b610d`。新增的诊断差异只有 `corpse4l-delta.patch` 列出的 14 个源码文件。它不再添加新的死亡修复行为，保留 corpse4k 的处理；主要目的是在主机、服务器、客机三处把死亡消息、布娃娃动作和激活/搜索事件对齐。

## 这版会记录什么

- **击杀与死亡同步**：记录击杀路径、拥有者发出的致死血量/死亡状态、服务器接收与转发、客机接收死亡通知后是否调用原生 `Kill()`，以及调用前后的 `IsDead`、虚拟死亡状态和 Actor 状态位。
- **布娃娃和本地 Actor Process**：记录拥有者发送的 `Ragdoll`/`RagdollInstant`，服务器接受或拒绝及转发数量，客机收到动作、动画图未就绪、动作延后或执行的结果；并记录客机原生 `ActorProcess` 是被放行还是仍被 STR 拦截。尸体状态日志只在观测状态变化时输出，不逐帧刷屏。
- **引用与物理线索**：按服务器实体 ID、所有权 epoch、本地引用 FormID、基础 FormID、NPC 名称、位置、3D 是否存在、是否处于 Ragdoll 状态、Actor 根节点是否带有 collision object 对照两端。`root_collision` 仅表示根节点 collision object 指针非空，不能证明 Havok 碰撞形状或布娃娃模拟正常。
- **交互链路**：记录客机按下交互后是否进入 Skyrim 的 `Activate` hook，是否产生 STR `ActivateEvent`、是否发出网络请求、服务器是否收到并转发、其它客户端是否收到通知并调用本地 `Activate()`。

可在双方 `tp_client.log` 与服务器 `STServerOut.log` 中搜索 `STR corpse`、`STR remote NPC` 和 `STR NPC activate`。同一个 NPC 用 `server`、`epoch`、`ref`、`base` 及 `name` 对齐。不要只用 FormID 对日志：本地 `ref` 可能因运行时分配而不同。为避免在游戏工作线程里查询 ECS，`ActorProcess begin/end/suppressed` 只记录本地 `ref` 和状态；用同一客机日志中带有 `ref` 的尸体状态行对齐。

## 怎样读交互日志

请在客机完全没有“搜索”提示时，仍对准尸体按一次交互键，并从另一侧再试一次。随后按下列顺序比较客机、服务器日志：

1. 没有 `STR remote NPC Skyrim Activate hook`：这次按键没有到达 STR 所挂的 Skyrim `Activate` 调用。故障仍在 STR 收到交互事件之前，可能涉及游戏目标选择/碰撞/交互输入；仅靠这些日志无法进一步区分。
2. 有 `Skyrim Activate hook`，没有 `STR remote NPC activate event`：检查 hook 的 activator、调用参数和事件触发条件。正常由玩家触发且非书本目标时，hook 会向 STR 事件系统派发激活事件。
3. 有 `activate event`，随后有 `request not sent`：日志会给出断线、引用映射、cell 或 activator 实体映射等具体原因。若 `corpse_candidate=false`，表示该客机本地状态当时没有把这个远端 NPC 识别为尸体。
4. 有 `activate request tx`，服务器没有 `STR NPC activate request rx`：请求未到服务器处理器，需对照连接/断线日志与同一时间戳。
5. 服务器收到但 `target_count=0`：服务端认为没有同 cell 的其它收件人；若数量大于零但客机无 `activate notify rx`，继续检查该客机的消息接收和 cell 状态。
6. 客机有 `activate notify rx` 但搜索仍不正常：看本地 `Activate` 的返回值，以及该 NPC 当时的死亡、ragdoll、3D 和状态位。注意这类通知是他人激活的广播，不是 HUD 搜索提示本身。

Skyrim/STR 源码没有提供当前准星目标和“搜索”HUD 提示状态的可读接口，因此本日志**不能直接证明碰撞体正确，也不能单独判定提示为何没出现**。`Activate` hook 完全没出现时，只能判定请求未进入该 hook；需结合游戏内现象或引擎级调试再细分。

## 双人测试步骤

1. 备份当前版本。两名玩家和服务器都使用本包中的同一版本文件；不要混用旧版 `SkyrimTogether.exe`、`STServer.dll` 或服务器程序。
2. 进入能稳定复现的区域，让客机留在尸体附近，由主机击杀一个新生成的 NPC。等约 5 秒，不要用控制台执行 `resurrect`/`kill`，也不要先切区。
3. 客机记录 NPC 名称和地点、是否有搜索提示、站姿/布娃娃表现；没有提示时仍按上节方法尝试交互两次。再交换角色测试由客机击杀。
4. 复现后立即保存主机与客机的 `tp_client.log`、服务器的 `STServerOut.log`。记录哪一边击杀、哪一边无法搜索，以及最后一次按交互键的大致时间。不要裁掉前后几十秒日志。

这是一份诊断包，不把编译成功当成游戏问题已修复。GitHub Actions 的 Windows x64 / Skyrim 1.6.1170 构建已完成：客户端与服务器构建成功，Papyrus 编译成功，104 项自动测试全部通过，PE 检查确认客户端、加载器、服务端 DLL 和服务器程序均为 AMD64。配置日志前段包含 xmake 查找依赖时的试链接失败（例如尚未安装的 `lua.lib`）；随后依赖安装完成，最终 configure 与正式构建均成功。构建仍有原有 MSVC/Papyrus 警告，日志中没有正式编译错误。游戏内是否解决仍需双人实测。

本轮构建记录：Actions run `42387608510`，源码提交 `c5390f5028803fa568bcdd4c7144a93755dcc9ae`。Windows 产物 SHA256：`SkyrimTogether.exe` `606dc798dcf20ffc48d57123148a45b63895114da4b1c66d5baed2e4388b4ce2`；`EarlyLoad.dll` `edda5a42a93d44a0a1c43841980f004809d6d3b72e799a427aff25a177077152`；`STServer.dll` `d69f882824fe73d5e4296ff10655355f9227a135e4313a0a1b968097ff991b3d`；`SkyrimTogetherServer.exe` `9d1511e0de8e2dec4b44b168c54da83cc30998eecf8fb7d255a3cee8b53f904a`。压缩包内 `SHA256.txt` 列出除清单自身外的每个包内文件；再次解压后的四个程序也已重验。

## 文件与安装

测试包会提供同一次 Windows x64 / Skyrim 1.6.1170 构建的四个程序文件：客户端目录替换 `SkyrimTogether.exe`、`EarlyLoad.dll`；服务器目录替换 `STServer.dll`、`SkyrimTogetherServer.exe`。保留配置、资源、UI、存档和已有的 Missives 兼容插件。每个文件的 SHA256 会随包提供。
