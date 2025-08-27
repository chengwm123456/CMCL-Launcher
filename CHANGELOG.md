<h1 align="center">Common Minecraft Launcher</h1>

<h4 align="center">Changelog</h4>

<div align="center">

![CurrentLanguage](https://img.shields.io/badge/Current_language-English-blue)

</div>

<div align="center">

**English**
·
[中文](https://github.com/chengwm123456/CMCL-Launcher/blob/CMCLMain/CHANGELOG_zh-cn.md)

</div>

- AlphaDev-25002
    - Added & Changes
        - Updated the version number
        - Optimised the logic of generating offline player's JWT (JSON Web Tokens)
        - Fought with Fabric
            - Done with the ~~stubborn~~ Fabric's downloading
            - Fixed this ~~stubborn~~ Fabric's launching, which requires me to handle `inheritsFrom`
        - Redesigned the UI
        - Other changes
    - Fixed
        - Since some wrong code in `class Minecraft`, the launcher cannot launch the game normally,
          see [there](https://github.com/chengwm123456/CMCL-Launcher/commit/160883c8a4b4b5b702e0b3492e58864af656f1bc#diff-e88aa0f0b51b655872366faf88a62ca76aac73bb43b964318d642e8ece9d3ccfL99)
        - Downloader cannot download file normally since Download didn't specify `Content-Encoding`.
        - Launcher cannot handle `inheritsFrom`
- AlphaDev-25001
    - Added & Changes
        - Updated the version number
        - A little supporting on modding
        - Support loading saves' info
        - UI components changes
            - The design of the border comes from the Start Menu of Win10
            - Simplified the up, down, left and right indicator
        - Wrong spelling correction
        - Other languages supporting
            - Currently, the launcher support Simplified Chinese, Traditional Chinese and British English /
              目前支持简体中文、繁体中文（无法保证一定正确）和英语。
            - Language translation may not be 100% accurate
            - Other languages may not be corresponded to the Simplified Chinese
            - Sometimes, other languages cannot be updated to the latest version when the Simplified Chinese updates /
              有的时候，简体中文更新时，其它语言未必能及时更新
        - Changes of the Loading Animation
        - Removed some Easter Eggs
        - ~~Added some Easter Eggs~~
        - ~~Removed Herobrine~~
        - Other changes
    - Fixed
        - (------)
- AlphaDev-24001 (No executable files)
    - Added & Changes
        - Updated the version number
        - Create this repo
        - Use a new UI design developed by myself
        - A little changes on the launcher's icon
        - Folder struct changed
            - All the core code moved to a package called`CMCLCore`
        - Other changes
    - Fixed
        - (------)
