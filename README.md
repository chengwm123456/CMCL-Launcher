<h1 align="center">Common Minecraft Launcher</h1>

<h3 align="center">A Minecraft launcher for Minecraft: Java Edition</h3>

<div align="center">

![CurrentLanguage](https://img.shields.io/badge/Current_language-English-5191FF)
![CurrentVersion](https://img.shields.io/badge/Current_version-AlphaDev--26001-5191FF)

</div>

<div align="center">

**English**
·
[中文](https://github.com/chengwm123456/CMCL-Launcher/blob/CMCLMain/README_zh-cn.md)

</div>

<h5>Description</h5>

This is a third-party launcher for Minecraft Java Edition, by [chengwm123456](https://www.github.com/chengwm123456) (
chengwm).

<h5>Note</h5>

* Some files are not the project files **so you don't have to see them** (e.g. `newdesign.py` is a temporary file for
  designing new UI, `autoupdate.py` is for auto upgrading). You can see these files' name in `.gitignore`
  file (e.g. `newdesign.py`).
  > Or, all the official files for this project are in the `Common Minecraft Launcher` directory.

* You can also call the author chengwm.

* Translations in this launcher and these project files **may not be 100% accurate**.

* There are full of bugs in these files......(for example, close a window may cause the RuntimeError or the launcher
  crashes, click a button may cause the launcher crashes, the launcher's windows is very slow, etc.)

* I'm weak in English so these files may have a lot of incorrect spelling, spelling mistake, spelling by pinyin or
  spelling which is very confusing. (for example, "recommend"[correct] → "recommand"[incorrect], "
  a"[in CMCLCore/CMCLGameLaunching/CommandGenerating.py] → "argument"[its meaning], etc.)

<h5>Tip</h5>

* Any bugs or advices can be reported or created through the "Issues" tab.

* You can help me translate this launcher in more languages.
    * **English translations**: `CMCL_en-gb.ts` / `CMCL_en-us.ts`.
    * Chinese translations: `CMCL_zh-cn.ts` / `CMCL_zh-hk.ts` / `CMCL_zh-tw.ts` / `CMCL_lzh.ts`.
    * Other translations: please make a new Pull request.
    * Also, you can make the expressions in the launcher better.
        * Please refer the Chinese translations file for the original expression.

* Contributing is **not illegal**, be brave to do it ~~, that's why I use git, it's to prevent **evil** vandalising!~~
    * For the contributing guidelines, please see `CONTRIBUTING.md`.

<h5>How to run this launcher</h5>

1. You can download the executable files from the "Releases" on the right side.
    * The executable files for both platforms are in a .zip compressed file called "CMCL.zip".
        * Windows file name: `Common Minecraft Launcher.exe`
        * Linux file name: `Common Minecraft Launcher.bin`

2. You can download the source code.
    * Click "Code" → "Download ZIP" to download the .zip file of all the source code.

    * Extract the .zip file.

    * Go to the [Official Python website](https://www.python.org/) to download Python 3.13 as your Python interpreter.
      > If you have it (i.e. Python 3.13) ...... this requirement above doesn't exist before.

    * Enter the decompressed directory where `requirements.txt` is in it.

    * Run：
        * `python -m pip install -r requirements_windows.txt` (On Windows)
        * `python3 -m pip install -r requirements_linux.txt` (On Linux)
            * Make sure you've got a venv (virtualenv). On Linux, pip downloaded via package manager cannot do this
              without a venv.

    * Run：
        * `python "Common Minecraft Launcher\main.py"` (On Windows)
        * `python3 Common\ Minecraft\ Launcher/main.py` (On Linux)

<h5><span style="color: red">IMPORTANT MESSAGES</span></h5>

Copyright (C) 2023-2026 chengwm123456

Licensed under the GNU General Public License version 3, for further details please refer [
`LICENSE.md`](https://github.com/chengwm123456/CMCL-Launcher/blob/CMCLMain/LICENSE.md).

<h5><span style="color: red">DISCLAIMER</span></h5>

**<span style="color: red">THIS PRODUCT IS NOT AN OFFICIAL MINECRAFT PRODUCT.<br/>
NOT APPROVED BY OR ASSOCIATED WITH MOJANG STUDIOS OR MICROSOFT.<br/>
FOR THE OFFICIAL MINECRAFT WEBSITE PLEASE SEE: https://www.minecraft.net/</span>**
