# STR 1.8.4 / SE 1.6.1170 客机尸体布娃娃修复候选 r2

本候选基于已送测的 corpse4 / loot1 源码，只处理远端死亡 NPC 的布娃娃状态回写。死亡时客机将本地 `bAnimationDriven` 关闭并确认成功后标记完成，失败会在后续快照重试；主机快照不再覆盖这个变量，其他动画变量继续同步。变量名按 NPC 当前动画图解析并缓存。相同保护也用于死亡动作回放和已死亡 NPC 的初始快照。

源码可确认，旧逻辑会把整组动画变量写回客机图；`bAnimationDriven` 确实在所用动画图描述符中。它可能覆盖客机本地的 Havok 死亡切换，与“主机击杀、客机看到尸体保持平面姿势且无法搜索”的现象相符。源码无法单独证明游戏引擎中的最终因果；需双人实测验证。

安装：双方客户端替换 `SkyrimTogether.exe`、`EarlyLoad.dll`，服务器替换 `STServer.dll`、`SkyrimTogetherServer.exe`。四个程序的构建标识为 `coopfix4i-corpse4-loot1`。其他 STR 资源、存档、Missives ESP、汉化和兼容 ESP/脚本照旧保留；不要与旧版 EXE/DLL 混用。

测试重点：主机杀死客机未攻击的普通 NPC 后，客机立即搜索；比较客机亲自击杀、法术击杀、近战击杀、已有尸体入区，以及复活后再次击杀。记录客机 `tp_client.log` 中 `STR corpse animation sync guard` 的 `found` 值和首次搜索结果。异常时提供两端 `tp_client.log` 和 `STServerOut.log`。

只有本分支的 Windows 构建、协议测试和文件校验全部通过后，Actions artifact 才可用作测试包；是否改善游戏内布娃娃和搜索仍需你的双人实测确认。
