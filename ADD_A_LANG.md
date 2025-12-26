<h1 align="center">Common Minecraft Launcher</h1>

<h4 align="center">Adding a new language</h4>

<div align="center">

![CurrentLanguage](https://img.shields.io/badge/Current_language-English-blue)

</div>

<div align="center">

**English**
·
[中文](https://github.com/chengwm123456/CMCL-Launcher/blob/CMCLMain/ADD_A_LANG_zh-cn.md)

</div>

> Please search how to create a Pull request first.

First, please add your language to `Common Minecraft Launcher/languagesCodeMapping.json` in the following format:

```json
{
  "[code]": "[local_name]"
}
```

> Note:
> 1. The `[local_name]` is the language in that language, and you can apply some informations for this language.
     > For example:
     >

- en-uk -> "English (United Kingdom)"

> - zh-cn -> "简体中文（中国大陆）"
> 2. `[code]` should be consist with the language code of the corresponding language in the game (i.e. Minecraft: Java
     Edition).

Second, add a translation file use the following command:

```bash
# in dir "Common Minecraft Launcher"
[your lupdate.exe] main.py -ts CMCL_[code].ts
```

Third, open your `linguist.exe` to start your translate.

> Note: If you can understand Chinese, use `CMCL_zh-cn.ts` as a reference. Otherwise, use `CMCL_en-gb.ts` as the
> reference.

Finally, create a Pull request to this repo.

<h5>Note</h5>

- Please **DON'T** change other files except the files metioned above.
- The author may not merge your changed soon, so please wait for some time.
  > "Coming s$\infty$n"
