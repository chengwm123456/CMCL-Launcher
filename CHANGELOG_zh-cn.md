<h1 align="center">Common Minecraft Launcher</h1>

<h4 align="center">更新日志</h4>

<div align="center">

![CurrentLanguage](https://img.shields.io/badge/当前语言-中文-blue)

</div>

<div align="center">

[English](https://github.com/chengwm123456/CMCL-Launcher/blob/CMCLMain/CHANGELOG.md)
·
**中文**

</div>

- AlphaDev-25002
    - 添加和修改
        - 更新版本号
        - 优化了一下离线玩家的 JWT 生成逻辑
        - 与 Fabric 激烈对线
            - 把那倔种的下载搞定了
            - 把那倔种用`inheritsFrom`阻止启动器启动的 bug 修复了
        - 重新设计了 UI
        - 其他更改
    - 修复
        - 由于`class Minecraft`
          中一处错误代码，造成启动器无法启动游戏，详见[此处](https://github.com/chengwm123456/CMCL-Launcher/commit/160883c8a4b4b5b702e0b3492e58864af656f1bc#diff-e88aa0f0b51b655872366faf88a62ca76aac73bb43b964318d642e8ece9d3ccfL99).
        - 下载器没有指定`Content-Encoding`造成下载错误
        - 启动器无法处理`inheritsFrom`
- AlphaDev-25001
    - 添加和修改
        - 更新版本号
        - 模组小支持
        - 存档信息读取
        - 组件修改
            - 边框的灵感是来源于 Win10 的菜单
            - 上下左右指示箭头来了一波简化
        - 修改拼写
        - 多语言支持
            - 目前支持简体中文、繁体中文（无法保证一定正确）和英语。
            - 语言翻译未必 100% 准确
            - 其他语言未必和简体中文对应
            - 有的时候，简体中文更新时，其他语言未必能及时更新
        - 加载动画更改
        - 移除了部分彩蛋
        - ~~添加了部分彩蛋~~
        - ~~移除了 Herobrine~~
        - 其他更新
    - 修复
        - (------)
- AlphaDev-24001 (无可运行文件)
    - 添加和修改
        - 更新版本号
        - 创建该 repo（仓库）
        - 使用一个新的界面设计
        - 图标小修
        - 文件夹结构修改
            - 所有底层代码改到了`CMCLCore`包里
        - 其他更新
    - 修复
        - (------)
