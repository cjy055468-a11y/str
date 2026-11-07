# corpse4j-r1：客机远端 NPC 死亡初始化候选修复

本候选以官方 Skyrim Together Reborn 1.8.4 提交 `54b3a858e228dc8807ed65bc3f9ac3c3f81b610d` 为基底，先应用已测试包 `corpse4i` 的 `fixes/coopfix4i-corpse4-v184.patch`，再应用本目录的 `corpse4j-death-init.delta.patch`。不修改掉落物、告示板或服务器 tick 逻辑。

排查方向来自客机现象：主机击杀的 NPC 在客机端保持僵硬姿势、没有搜索提示；客机控制台复活后再次击杀，搜索才恢复。候选增加每个 Actor 的一次性标记，记录 STR 是否为远端 NPC 调用过本地 `Actor::Kill()`，并记录远端死亡是否进入原生 death-item 阶段。服务器确认远端 NPC 已死亡时，如果其本地原生死亡流程尚未被观察到，则尝试调用一次 `Kill()`；重复死亡快照不会重复触发，复活、确认为存活或角色从远端解除时重置标记。进一步的就绪保护会要求 3D、附着 cell、当前 AI process 和运行时标记都已就绪，才会消耗这一次机会；未就绪时不标记成功，由远端更新循环在就绪后重试一次。远端尸体的死亡物品仍由原有 hook 抑制，避免这次补调用产生本地额外战利品。

这是待实测的引擎行为假设，不是已证实根因。再次对已死亡 Actor 调用原生死亡流程可能有副作用；本候选仅做一次，并记录调用前后状态。若日志显示 `KillImpl` 已调用或 native death-item 阶段已进入，但客机仍没有搜索提示，就应转查激活目标／尸体位置／物理与动画图，不应继续重复调用死亡流程。

## 构建与验证

只有独立 Windows x64 Actions 构建、测试与 PE 检查全部通过后，artifact 才能用于测试。源码已增加就绪延迟与重试保险；Windows 构建和游戏内效果仍需验证。corpse4j-r1 的 EXE 和服务器组件 build tag 为 `coopfix4j-r1-corpse4-loot1`，两名玩家和服务器必须使用同一版本。

若构建通过，测试时双方退出游戏后替换 MO2 实际加载目录中的 `SkyrimTogether.exe`、`EarlyLoad.dll`，并成对替换服务器的 `STServer.dll`、`SkyrimTogetherServer.exe`。保留存档、配置和其它资源。先复测同一地点：主机击杀一个客机未攻击的普通敌人，客机立即瞄准尸体搜索；再测客机击杀、近战／法术击杀、重复死亡同步、复活后再次击杀、离区返回和重连。收集两边的 `tp_client.log` 与服务器 `STServerOut.log`；`STR corpse KillImpl deferred until actor is ready`（debug 级别）、`Retrying confirmed remote NPC death once runtime is ready`、`STR corpse KillImpl invoked`、`STR corpse native death item phase observed`、`Applying death state` 都应在对应客户端日志里核对。
