# 官方基础与推断边界

源码固定官方v1.8.4 / 54b3a858e228dc8807ed65bc3f9ac3c3f81b610d，四个子模块仍按该提交锁定。官方架构明确客户端权威、信任客户端；原Inventory::Entry::IsExtraDataEquals注释也说明充能/毒药/临时附魔会变化，服务端库存缓存不可靠。不能将自加掉落缓存严格匹配导致的返还归咎官方遗漏。

确定：coopfix3r1当前服务器会话45次来源库存不可用拒绝；客户端Rejected路径主动返还；待确认记录已清除穿戴位。尚不确定每次缓存不符具体是数量、分散条目、强化还是充能，旧日志没有这些字段，不能推断45次都同一种原因。当前掉落唯一编号、并发第一赢家和重连不复活的账本设计保留。

官方接收装备流程原来保存本地旧护甲，先全部卸下，装备通知物品，再把旧护甲全部穿回；这有原作者为原生不自动卸甲的明确工作原因。本次保留该绕行所需的卸甲步骤，将恢复集合换为所有者本次已发送但旧Notify未携带的CurrentInventory。没有启用本地远端AI，也没有给所有裸体NPC强配默认服装。

浮空源码尝试参考 CommonLibSSE-NG：NiAVObject::GetCollisionObject RELOCATION_ID(25482,26022)；SetMotionType Offset::NiAVObject::SetMotionType RELOCATION_ID(76033,77866)，参数 this,uint32,bool=true,bool=false,bool=allowActivate；TESObjectREFR::SetMotionType使用节点调用并标记kHavokMoved。使用AE地址库ID26022/77866，无原始地址、新虚表槽或猜测布局。没有IDA/Ghidra证据，函数线程副作用、碰撞查询覆盖子节点情况、返回值与实际可激活状态关系均仍属假设。返回false不自动等于无碰撞，true也不证明能拾取。

快照重建和启用后MoveTo是可疑的生命周期路径，不是日志已证明的唯一悬空根因；修复避免无必要删建/再次移动，并增加实际碰撞诊断。未关闭世界/玩家碰撞，未通过向背包塞物再丢出来制造代理，未用隔墙自动拾取替代原生准星。

家具退出修复保持不变，用户已实测敌人坐着不起来的问题修复成功；正常坐姿高度和所有仇恨行为仍不承诺。当前上游master/dev核对结果见upstream-refs记录；未把已撤回的8d1e437战斗候选重新带入。

补充复核：项目Games/Forms.cpp的SetSkipSaveFlag(true)把TESForm::unk10写为0xFFFF，false无还原。项目偏移与CommonLibSSE-NG TESForm::inGameFormFlags同在0x18（本地字段名unk10不等于偏移0x10），其枚举包含kWantsDelete位0及kRefPermanentlyDeleted位7。项目原Actor::Create使用该助手有其上下文，本次不改原函数、不批量清标志，只撤掉我们此前加到实际掉落物上的复用。原写入可能造成“先可用、随后无碰撞/无激活”的状态，但尚无引擎运行记录证明全部悬空由此产生。

为保持联网掉落不写进本地存档，新增精确的保存资格过滤：CommonLibSSE-NG Offsets_VTABLE.h的AE VTABLE_TESObjectREFR[0] Address Library ID190259，TESObjectREFR.h中CheckSaveGame(BGSSaveFormBuffer*)虚函数slot0x0D；读取此实现并用项目已有MinHook机制detour，符合本服务formID+handle索引的临时引用返回false，其余调用原实现。不新增/改动虚表布局或序列化格式。该保存资格路径覆盖运行时新引用、调用时机、hook副作用尚未IDA/Ghidra核验，不能把源码推断当作游戏验证；需重启双方客户端/服务端，用新掉落物并覆盖保存/读档测试。

## 按用户追加要求的落点同步

保留拾取碰撞。由原始丢弃者的真实引用运行原生物理；非原始引用绝不发布落点。检查3D、实际碰撞对象、附着区域以及未暂停后，以250ms间隔采样既有position/rotation，连续两个稳定间隔后报告落点；后续移动限频500ms一次，发送失败不吃掉待发送位置。服务端校验当前玩家所有权/epoch/session、账本创建者、活物品及有限坐标，只更新位置/角度/区域，不改物品ID和数量。拾取后的晚到位置不能复活物品。快照和创建重试保留最后落点。

接收方通常等落点后创建副本，最多等2秒；没有来源报告则保留动态物理后备方式，避免永久隐藏。收到真实落点后保留碰撞，将副本设为Keyframed（hkpMotion::MotionType值4），减少第二套重力模拟；只有新位置到达时才移动并重新等碰撞就绪。未删除碰撞箱，不硬套玩家高度，不全局改变Havok或NPC。来源断开后没有另选物理所有者，后备方式保留拾取；远端副本不会独立滚动，这个取舍需游戏测试。

源码未证明REFR position/rotation始终与每种NIF的Havok可见节点同步，稳定采样不是引擎刚体休眠证明。没有IDA/Ghidra证据；这部分是用户授权的实际代码尝试，不宣称所有模型都已解决。

## 服务器两档tick

沿用原GameServer:bPremiumMode：true目标70，false目标60；不增加80档，不动匹配子模块。设置后重启服务器生效。底层1000ms/tick整数取整及2ms轮询休眠/系统调度会影响实测值；网络接包循环不完全受此tick限制，客户端约30ms发送角色状态，70不等于NPC/物品每秒收到70份新状态。

## 两次检查

按用户最新“检查两次”：第一次检查源码所有权、消息顺序、保存与拾取边界及保留修复；第二次在Windows/MSVC实际编译客户端/服务端，运行75项测试（48项必需专项），核对PE64、目标版本、四文件哈希和配套服务端启动。不是承诺引擎无遗漏，也不是两次游戏测试。新增6项落点账本/工厂/时间纯测试，保留原69项。最终构建记录须对应本补丁最新提交；未编译或失败的候选不作为成品。
