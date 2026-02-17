<h1 align="center">Common Minecraft Launcher</h1>

<h3 align="center">一个 Minecraft Java 版启动器</h3>

<div align="center">

![CurrentLanguage](https://img.shields.io/badge/当前语言-中文-5191FF)
![CurrentVersion](https://img.shields.io/badge/当前版本-AlphaDev--26001-5191FF)

</div>

<div align="center">

[English](https://github.com/chengwm123456/CMCL-Launcher/blob/CMCLMain/README.md)
·
**中文**

</div>

<h5>介绍</h5>

这是一个第三方的 Minecraft Java 版启动器，由 [chengwm123456](https://www.github.com/chengwm123456)（chengwm）开发

<h5>注意</h5>

* 一些文件不属于正式项目文件**所以你没有那个必要那么好奇**（比如，`newdesign.py`是用来设计新的界面设计的临时文件，
  `autoupdate.py`是用来搞自动升级的）。这些文件基本上在`.gitignore`文件里（比如`newdesign.py`就在）。
  > 或者，`Common Minecraft Launcher`文件夹里面的文件都是正式项目文件。

* 你还可以把作者叫做 chengwm。

* 启动器的翻译以及文件的翻译**未必 100% 准确**。

* 启动器的这些文件除了 bug 就是 bug …… （比如，关闭一个窗口就能整出 RuntimeError 或者直接崩掉，按一个按钮就能把启动器崩掉，窗口非常卡顿等等）

* 我英语很弱所以这里面会有大量的错误拼写、拼音起名以及离谱的名字。（比如，"recommend"[正确拼写] → "recommand"[错误的]、"
  a"[在 CMCLCore/CMCLGameLaunching/CommandGenerating.py 里面] → "argument"[其代表的意思]等等）

<h5>提示</h5>

* 任何 bug 或者建议都可以通过 Issues（问题）页面进行反馈。

* 你可以帮忙翻译一下启动器，让启动器支持更多的语言。
    * 英语翻译文件：`CMCL_en-gb.ts` / `CMCL_en-us.ts`。
    * **中文翻译文件**：`CMCL_zh-cn.ts` / `CMCL_zh-hk.ts` / `CMCL_zh-tw.ts` / `CMCL_lzh.ts`。
    * 其他翻译：请新建一个 Pull request。
    * 同时，你可以帮忙让启动器内的语言表述更好，比如说前面。
        * 请参考中文语言文件修改。

* 做出贡献又不违法，勇敢去做（Just do it）~~，不然为什么我要搞个 git，是为了避免有人搞**恶意**破坏呀！~~
    * 关于贡献指南，请见 `CONTRIBUTING_zh-cn.md`

<h5>运行启动器</h5>

1. 你可以从右侧的 "Releases"（版本）下载启动器。
    * 两个平台的可运行文件在一个叫做“CMCL.zip”的压缩文件里面。
        * Windows 系统文件名：`Common Minecraft Launcher.exe`
        * Linux 系统文件名：`Common Minecraft Launcher.bin`

2. 下载源代码。
    * 点击 "Code" → "Download ZIP"，下载源代码的 .zip 压缩包。

    * 解压 .zip 压缩包。

    * 去 [Python 官网](https://www.python.org/)下载 Python 3.13 作为 Python 解释器。
      > 如果你有 Python 3.13 的话……当这条不存在！

    * 进入解压的文件夹，进到根目录（有`requirements.txt`的那个）

    * 运行：
        * `python -m pip install -r requirements_windows.txt`（Windows）
        * `python3 -m pip install -r requirements_linux.txt`（Linux）
            * 确保你创建了 venv，Linux 通过包管理器下载的 `python3-pip` 不能这么干。

    * 运行：
        * `python "Common Minecraft Launcher\main.py"`（Windows）
        * `python3 Common\ Minecraft\ Launcher/main.py`（Linux）

<h5><span style="color: red">重要内容</span></h5>

Copyright (C) 2023-2026 chengwm123456

本启动器使用 GNU Affero General Public License 第三版授权，详见 [
`LICENSE.md`](https://github.com/chengwm123456/CMCL-Launcher/blob/CMCLMain/LICENSE.md)。

（仅英文版本，许可证文件不予翻译）

<h5><span style="color: red">免责声明</span></h5>

**<span style="color: red">本产品非 Minecraft 官方产品。<br/>
未经 Mojang Studios 或 Microsoft 批准，亦与 Mojang Studios 或 Microsoft 无任何从属关系。<br/>
Minecraft 官方网站请见：https://www.minecraft.net/</span>**
