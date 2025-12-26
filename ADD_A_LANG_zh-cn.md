<h1 align="center">Common Minecraft Launcher</h1>

<h4 align="center">添加语言</h4>

<div align="center">

![CurrentLanguage](https://img.shields.io/badge/当前语言-中文-blue)

</div>

<div align="center">

[English](https://github.com/chengwm123456/CMCL-Launcher/blob/CMCLMain/ADD_A_LANG.md)
·
**中文**

</div>

> 请先去搜索如何创建 Pull request。

首先，把你的语言，按照下面的格式，添加到 `Common Minecraft Launcher/languagesCodeMapping.json`：

```json
{
  "[code]": "[local_name]"
}
```

> Note:
> 1. `[local_name]` 要用那个语言表达那个语言（绕口令）。你可以给这个语言添加一些信息。
     > 示例：
     >

- en-uk -> "English (United Kingdom)"

> - zh-cn -> "简体中文（中国大陆）"
> 2. `[code]` 应和游戏内对应的语言代码对应。

其次，使用以下命令添加一个翻译文件：

```bash
# 在文件夹 "Common Minecraft Launcher" 内
[your lupdate.exe] main.py -ts CMCL_[code].ts
```

再次，打开 `linguist.exe` 开始翻译。

> 注：如果你看得懂中文（一般看这个的都是可以看懂的），请参考 `CMCL_zh-cn.ts`。否则（应该看这个的都不会这样），参考
`CMCL_en-gb.ts`。

最后，创建一个 Pull request。

<h5>注</h5>

- 除了上述提到的文件除外，请**不要**更改其他文件。
- 作者有可能不会立马合并更改，请⌛️等待一段时间。
  > “Coming s$\infty$n”
