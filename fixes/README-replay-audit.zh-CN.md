# NPC 动画回放审计候选 v2 — 官方 STR 1.8.4 / Skyrim SE 1.6.1170

> 本文件描述 b084df6 的单独审计候选，作为历史证据保留。包含掉落物的当前版本及四文件安装说明见 [README-coop-dropfix1.zh-CN.md](README-coop-dropfix1.zh-CN.md)。下文“拾取仍暂停”仅描述该历史版本。

这不是“所有 NPC 卡住问题已经解决”的成品结论。游戏内坐姿／悬空问题仍需验证。
本分支撤掉上一版改变 NPC 战斗启动、增加敌意查询、补写 TargetEventName、显式初始化 ReplayCount 的改动。
Actor.cpp、Actor.h、CombatService.cpp、RemoteAnimationComponent.h 与官方 v1.8.4 保持一致。

## 官方依据

- 官方 PR #633 是战斗系统重做；提交 61ebb6e9 明确有意禁用旧目标选择系统。
  旧代码原本只处理已经进入战斗的 NPC。因此不能把禁用状态认定为制作组遗漏。
  https://github.com/tiltedphoques/TiltedEvolution/pull/633
  https://github.com/tiltedphoques/TiltedEvolution/commit/61ebb6e9cb4cb59b455d97fb4f748e90c1c3591f
- 官方 PR #811 明确描述坐着移动、站在椅子上等动画不同步，并说明连接前已经发生的
  动作没有完整回放历史，现有方案无法完全解决。这是已知限制。
  https://github.com/tiltedphoques/TiltedEvolution/pull/811
- 按项目固定的 EnTT 3.10.0，组件创建／替换会使用聚合初始化。
  原 ReplayCount 在当前 Setup 路径已经初始化；上一版显式写零属于冗余防护。

## 本候选仅修复的代码契约

真实服务端 ActionReplayCache 收到 IdleChairExitToStand 后，会移除退出动作并发送
ResetAnimationGraph=true、Actions=[]。原客户端将重置放在“队列非空、ReplayCount>0”
的分支内，因此这个明确的服务端指令永远不会执行，即使之后收到普通实时动作也不会补上。

现在把已有重置操作移到队列条件之外；保留原函数调用、一次性消费语义及原生战斗处理。
重置后仍检查图是否可取得再播放队列，不添加强制等待帧，不强制起身，不改坐姿高度或家具偏移。
原生函数返回值被记录用于诊断；它的引擎副作用未通过 IDA/Ghidra 或游戏运行验证。

增加少量信息日志：STR replay reset、STR replay audit v2。
记录分配／转交控制权时的角色、位置、原始状态位和回放数量，以便判断错误来自拥有者
还是接收端。日志不等于根因证明，不应将两边坐在空中的所有情况归结于上述契约问题。

## 验证方式和局限

TPTests 直接编译生产服务器缓存代码，检查退出后空回放、原地坐姿保留、退出再进入其他家具、
没有历史时保持未知、网络载荷往返，以及原始组件的 EnTT 初始化语义。
这些是无游戏依赖的数据契约测试，不会假装验证游戏内起身、物理或 AI。
Windows Actions 还实际编译客户端／服务器，检查 x64、1.6.1170 标记及重复构建哈希。

## 安装和游戏对照

关闭游戏和服务器，保留官方 v1.8.4 原文件备份。两位玩家均使用同一候选，
将包内 SkyrimTogether.exe、EarlyLoad.dll、STServer.dll 覆盖到原位置；独立服务器目录
也使用配套 STServer.dll。保留原 MOD 的其余依赖、UI、ESP、脚本和行为文件。
这仍是 EXE 内的客户端修复，不是独立 SKSE 插件。

请分别对照：NPC 已坐下后再连接／进入区域，以及两位玩家都在区域里才让 NPC 坐下；
记录双方同一 NPC 是否都悬空、谁是队长、谁先进入，保存双方及服务器日志。
敌人攻击／追击用另一轮单独测试，不把普通 NPC 正常坐着当作错误。

服务器没有连接前的历史时，本候选不会凭空推测正确家具和姿态；若此类情况仍异常，
需要同一 NPC 的运行日志、游戏内对照及必要的引擎检查，才能进一步实施修复。

掉落物拾取修复仍暂停，未包含在本候选中。
