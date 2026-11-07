# Missives 2.03 + STR 1.8.4 / Skyrim SE 1.6.1170 空板修复 r2 测试候选

仅当 Windows 构建、协议测试、PEX 编译和产物检查全部成功后才有候选文件。
基于官方 v1.8.4（54b3a858）和已编译的 corpse3 累积修复。

客户端两边及服务器必须使用本包四个匹配的程序文件；保留原有配置、UI 和其余资源。
客户端 SkyrimTogether.exe、EarlyLoad.dll 放入原 STR 对应位置。
服务器 STServer.dll、SkyrimTogetherServer.exe 放入原服务器对应位置。
MissivesCompat 在 MO2 中作为新模组安装，覆盖 Missives 原脚本，启用 STR_Missives_Compat.esp 并置于 Missives.esp 之后。
保留 Missives 原版和汉化；不将 Source 或编译接口当作 PEX 安装。所有玩家必须安装同版补丁及同版 Missives。
任务只归接取者；其他玩家告示删除，不复制任务信件、目标、奖励。每块告示板独立选择一个生成端，告示的目标/地点使用该端的任务实例。寻物任务将接取者的任务引用放进同一目标箱子。
已有离线任务保留给原玩家；推荐独立 MO2 测试档，保存原程序及存档备份。

需要双人实测：双方告示正文/目标一致；轮流/同时领取同一张；非接取者背包无信件及奖励；接取者完成领取奖励；重新打开告示板/区域切换/断线重连；尸体、丢物、衣服和家具原修复回归。
已接取任务的断线重连、服务器重启后的任务持久性、原有存档迁移、远区任务 NPC 和汉化文字替换还需游戏验证。此补丁基于用户提供的 2.03 汉化记录；未重新打包原 Missives 资源。
原生引擎布局和任务启动副作用仅按源码参考，未经 IDA/Ghidra 或游戏验证；编译成功不能证明完全兼容。

已有客机日志显示两个 ESP 和补丁脚本都已加载，但 `identity_available false`，启动一直停在 `reason 1`，没有发出 Missives 握手，因此专用告示板同步根本没有启动。r2 在连接后持续重试本地身份令牌生成，并在 `LOCALAPPDATA` 不可用时尝试稳定的 `APPDATA` 路径；日志区分玩家名、路径、目录、随机源和写文件失败，不打印角色名、令牌或路径。

同时，带兼容 ESP 的告示板现在不会接受通用容器初始快照或库存增量；公告只由专用 Missives 通道按任务别名应用，防止旧容器缓存把本地公告清空。原有 0 号网络实体握手、已在触发范围内连接后的启动恢复、等待本板生成权限时不消耗刷新日期等修复保留。
协议标识为 coopfix4g-missives2r2，四件程序和补丁脚本均须更新；旧 missives2 客户端/服务器不可混用。实测时双方和服务器使用同一版；打开告示板观察数秒、关闭后重开，并检查 `STR Missives hello sent`、`ready`、`board requested`、`snapshot ready` 与 `board scan` 日志。若仍空，提供双方本次 `tp_client.log` 和 `STServerOut.log`。
