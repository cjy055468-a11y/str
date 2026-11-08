# STR Missives 公告板同步候选

这是从旧 Missives 兼容实现移除后重新建立的 STR 网络公告板实现。它按**实体告示板引用 ID**同步公开公告；同一任务可以出现在不同实体板上。某一块板上的公告一旦被领取，就从所有玩家对这块板的视图中移除。

任务阶段、目标、奖励与任务道具不进入网络协议。每个玩家本地只启动自己成功领取的任务，其他玩家只清理该公告的本地影子副本。公告书目录从用户提供的 `Missives.esp` 提取并校验，共 264 条。

## 交付内容

- `coopfix4g-missives-board-sync-v184.patch`：针对官方 STR v1.8.4 源码的完整 native 源码补丁。
- `mods/missives-board-sync/`：覆盖 Missives 原脚本的全新 Papyrus 源码和公告目录；没有 ESP，也不复用旧兼容 ESP。
- 两轮源码审查记录、源码 SHA 清单、检查工具和 Windows 构建工作流。

## 构建与安装

Windows 工作流会核验官方源码基线和补丁范围，编译 Papyrus PEX、STR 客户端与服务器，再运行协议测试。只有这些步骤全部成功才会打包四个匹配的 STR 程序文件及 `MissivesBoardSync` 脚本。所有玩家和服务器必须使用同一版修改过协议的 STR；每位客户端还需要保留原版 `Missives.esp` 和其汉化文件，并安装新包的 `MissivesBoardSync/Scripts`。

本工作区尚未运行 Windows/MSVC 与 Caprica 构建，也没有 Skyrim 双客户端运行环境。因而目前是可审查的源码候选，不能标记为已编译、已安装或已通过游戏内兼容测试。工作流成功后，Windows 构建产物才是可安装包。
