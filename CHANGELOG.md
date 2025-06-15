<h1 align="center">Common Minecraft Launcher</h1>

<h4 align="center">Changelog / 更新日志</h4>

- AlphaDev-25002
    - Added & Changes / 添加和修改
        - Updated the version number / 更新版本号
        - Optimised the logic of generating offline player's JWT (JSON Web Tokens) / 优化了一下离线玩家的 JWT 生成逻辑
    - Fixed / 修复
        - Since some wrong code in `class Minecraft`, the launcher cannot launch the game normally,
          see [there](https://github.com/chengwm123456/CMCL-Launcher/commit/160883c8a4b4b5b702e0b3492e58864af656f1bc#diff-e88aa0f0b51b655872366faf88a62ca76aac73bb43b964318d642e8ece9d3ccfL99) /
          由于`class Minecraft`
          中一处错误代码，造成启动器无法启动游戏，详见[此处](https://github.com/chengwm123456/CMCL-Launcher/commit/160883c8a4b4b5b702e0b3492e58864af656f1bc#diff-e88aa0f0b51b655872366faf88a62ca76aac73bb43b964318d642e8ece9d3ccfL99).
        - Downloader cannot download file normally by ignoring `Content-Encoding` / 下载器没有处理
          `Content-Encoding`造成下载错误
- AlphaDev-25001
    - Added & Changes / 添加和修改
        - Updated the version number / 更新版本号
        - A little supporting on modding / 模组小支持
        - Support loading saves' info / 存档信息读取
        - UI components changes / 组件修改
            - The design of the border comes from the Start Menu of Win10 / 边框的灵感是来源于 Win10 的菜单
            - Simplified the up, down, left and right indicator / 上下左右指示箭头来了一波简化
        - Wrong spelling correction / 修改拼写
        - Other languages supporting / 多语言支持
            - Currently, the launcher support Simplified Chinese, Traditional Chinese and British English /
              目前支持简体中文、繁体中文（无法保证一定正确）和英语。
            - Language translation may not be 100% accurate / 语言翻译未必 100% 准确
            - Other languages may not be corresponded to the Simplified Chinese / 其它语言未必和简体中文对应
            - Sometimes, other languages cannot be updated to the latest version when the Simplified Chinese updates /
              有的时候，简体中文更新时，其它语言未必能及时更新
        - Changes of the Loading Animation / 加载动画更改
        - Removed some Easter Eggs / 移除了部分彩蛋
        - ~~Added some Easter Eggs / 添加了部分彩蛋~~
        - ~~Removed Herobrine / 移除了 Herobrine~~
        - Other changes / 其它更新
    - Fixed / 修复
        - (------)
- AlphaDev-24001 (No executable files / 无可运行文件)
    - Added & Changes / 添加和修改
        - Updated the version number / 更新版本号
        - Create this repo / 创建该 repo（仓库）
        - Use a new UI design developed by myself / 使用一个新的界面设计
        - A little changes on the launcher's icon / 图标小修
        - Folder struct changed / 文件夹结构修改
            - All the core code moved to a package called CMCLCore / 所有底层代码改到了 CMCLCore 包里
        - Other changes / 其它更新
    - Fixed / 修复
        - (------)
