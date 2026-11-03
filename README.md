# 旧 NPC 候选 8d1e437：撤回推荐使用

该候选确已通过 Windows 编译、文件检查和重复构建，但其战斗行为改动缺乏根因证据。
旧战斗系统是官方有意禁用；不能将禁用本身解释为错误，也未证明新增 StartCombat 能解决坐姿/悬空。
原 ReplayCount 在 EnTT 创建路径已有初始化，额外初始化不能作为原版缺陷证据。
请优先恢复官方备份，不再将此包当作针对坐姿/悬空的已确认修复。

重新审计与缩小范围的候选：
https://github.com/cjy055468-a11y/str/tree/codex/npc-animation-audit-v184
官方已记录的动画回放局限：
https://github.com/tiltedphoques/TiltedEvolution/pull/811

旧文件与检查记录保留用于追溯。游戏运行效果从未验证，构建通过不等于确认根因。
