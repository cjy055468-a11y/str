# corpse4l 源码审查：反向范围与副作用

第二轮从新补丁反向检查了死亡流程、Activate 入口和服务器处理器：

- 相对 corpse4k 的代码变化用于诊断。没有增加引擎 hook、地址、结构布局、网络消息字段或 opcode；没有改变 owner/epoch 验证及死亡/动作消息收件范围。
- `ActorExtension` 新增的位只用于抑制重复日志；尸体状态组件只保存本地上次观测值。服务器、客户端 Activate 处理和通知 relay 只新增状态查询、计数及日志。
- 不主动调用额外 `Kill()`/`Respawn()`，不改库存、尸体容器、战利品、任务或 Missives 逻辑。唯一一次性日志在死亡过渡状态放行/拦截时触发；Activate 日志只会在玩家实际激活远端 NPC 时触发。
- `root_collision` 采样只读，不访问 Havok 内部对象、不读取碰撞形状。未出现激活 hook 时，不会把“无搜索提示”武断归因到碰撞。
- Windows x64 / Skyrim 1.6.1170 Actions 构建已完成：client/server 正式构建、Papyrus 编译、配置生成 smoke check 均成功；Catch2 104 项通过，PE 检查确认四个交付程序均为 AMD64。配置初期有 xmake 依赖探测产生的 `LNK1181` 试链接失败；依赖安装后配置成功。正式 client/server 构建日志的结尾均为 `build ok`，没有 C++ 编译错误。仍有上游 MSVC 与 Papyrus 警告。构建日志、测试摘要和哈希随包提供；编译通过不替代双人游戏验证。
