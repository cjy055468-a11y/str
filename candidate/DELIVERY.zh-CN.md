# corpse5 装备计数修订 loot2 交付说明

本包基于已由用户实测确认可搜索的 corpse5。新增改动尝试避免客机在 NPC 3D 首次就绪时，对已经与主机快照一致的库存再清空并重装，针对用户报告的同一装备数量从 1 变成 2。

Windows/MSVC 构建、110 项自动测试、18 个 Missives PEX 编译、服务端启动配置检查、四个程序的架构/版本/导入导出/哈希核对，以及两遍源码检查均已通过。loot2 装备计数尚未经过新的双人游戏实测；请用干净测试存档确认同件物品仍为 1，并确认 corpse5 的尸体搜索修复仍有效。

安装时双方客户端替换 `SkyrimTogether.exe` 与 `EarlyLoad.dll`；开服者还替换 `STServer.dll` 与 `SkyrimTogetherServer.exe`。四个文件必须来自本包，配置、资源、ESP 与现有兼容脚本保留。测试前备份存档。

构建日志、源码补丁、两轮检查报告及 SHA256 清单均在包内。构建记录：<https://github.com/cjy055468-a11y/str/actions/runs/42426112318>。
