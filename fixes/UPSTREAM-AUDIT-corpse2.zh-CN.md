# 官方基线与引擎假设

仍基于官方v1.8.4源码54b3a858e228dc8807ed65bc3f9ac3c3f81b610d和匹配子模块，累计4g与netdiag1。官方dev711ca1b相关路径已核对；没有把corpse1回归归咎于官方或用户MOD。用户实际报告corpse1死亡角色不倒地，优先修复自己新增的过宽拦截。

CommonLibSSE-NG参考src/RE/A/Actor.cpp的Actor::IsInRagdollState使用RELOCATION_ID(36492,37491)，本项目目标1.6.1170使用AE ID37491。同一参考中的Actor::GetLevel AE37334与项目现有37334匹配，佐证ID系列；这不是IDA/Ghidra二进制验证。新增查询是只读bool接口，签名与参考一致；无新布局、虚表槽或原始地址。状态真是否足以保证本地参考与交互碰撞保持一致，仍是待游戏验证的假设。

明确恢复动作队列和所有动画变量更新，移除corpse1原生ActorProcess例外。只在远端、非玩家、死亡、实际ragdoll四条件成立时释放活人位置/旋转覆盖；原生SetPosition同条件放行。玩家死亡系统、存活NPC、家具、掉落、装备、库存/任务代码和网络编码保留；Missives修改已从工作区反向撤出并保存在独立分支，未混入本版。
