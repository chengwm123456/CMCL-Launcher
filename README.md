<h1 align="center">Common Minecraft Launcher</h1>
<h5>Description</h5>

This is a third-party launcher for Minecraft Java Edition, by "chengwm123456" (in launcher my nickname is "chengwm").

<h5>Note</h5>

- Some files are not the project files **so you don't have to see them** (e.g. `newdesign.py` is a temporary file for
  designing new UI, `autoupdate.py` is for auto upgrading). You can see these files' name in .gitignore
  file (e.g. `newdesign.py`).
  > Or, all the project files are in the `Common Minecraft Launcher` directory.

- You can also call the author "chengwm".

- Translations in this launcher and these project files may not be 100% accurate.

- There are full of bugs in these files......(for example, close a window may cause the RuntimeError or the launcher
  crashes, click a button may cause the launcher crashes, the launcher's windows is very slow, etc.)

- I'm weak in English so these files may have a lot of incorrect spelling, spelling mistake, spelling by pinyin or
  spelling which is very confusing. (for example, "recommend"[correct] -> "recommand"[incorrect], "
  a"[in CMCLCore/CMCLGameLaunching/CommandGenerating.py] -> "argument"[its meaning], etc.)

<h5>Tip</h5>

- Any bugs or advices can be reported or created through the "Issues" tab.

- You can help me translate this launcher in more languages. (English translations: CMCL_en-gb.ts / CMCL_en-us.ts,
  Chinese translations: CMCL_zh-cn.ts / CMCL_zh-hk.ts / CMCL_zh-tw.ts / CMCL_lzh.ts, Other translations please make a
  Pull request.)

- Contributing is not illegal, be brave to do it ~~, that's why I use git, because I want to avoid evil destruction!~~

<h5>How to run this launcher</h5>

1. You can download the releases from the "Releases" on the right side.

2. You can download the source code.
    - Click "Code" -> "Download ZIP" to download the .zip file of all the source code.

    - Extract the .zip file.

    - Go to the [Official Python website](https://www.python.org/) to download Python 3.12 as your Python interpreter.
      > If you have it ...... then I'm a deaf, I didn't say anything before.

    - Run：
        - `python -m pip install -r requirements.txt`: On Windows
        - `python3 -m pip install -r requirements_linux.txt`: On Linux
            - Make sure you've got a venv (virtualenv). On Linux, download `python3-pip` via apt (or other thing can
              prove that I know too little.) cannot do this without a venv.

    - Run：
        - `python "Common Minecraft Launcher\main.py"`: On Windows
        - `python3 Common\ Minecraft\ Launcher/main.py`: On Linux

<h5>IMPORTANT MESSAGES</h5>

- You can download the source code, but you **shouldn't** edit it.

- You **can** copy a little from each file but **don't** Ctrl + C and Ctrl + V and **don't** use in business, thanks for
  your cooperation.

- **Don't** distribute any file in this project except the executable file of the launcher.
