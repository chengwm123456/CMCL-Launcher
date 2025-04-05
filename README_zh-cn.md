<h1 align="center">Common Minecraft Launcher</h1>
<h5>介绍</h5>

这是一个第三方的 Minecraft Java 版启动器，由 chengwm123456（启动器内叫做 chengwm）开发

<h5>注意</h5>

- 一些文件不属于项目正式文件**所以你没有那个必要那么好奇**。这些文件基本上在 .gitignore 文件里。

- 你还可以把作者叫做 chengwm。

- 启动器的翻译以及文件的翻译未必 100% 准确。

- 启动器的这些文件除了 bug 就是 bug …… （比如，关闭一个窗口就能整出 RuntimeError 或者直接崩掉，按一个按钮就能把启动器崩掉，窗口非常卡顿等等）

- 我英语很弱所以这里面会有大量的错误拼写、拼音起名以及离谱的名字。（比如，"recommend"[正确拼写] -> "recommand"[错误的]、"a"[在 CMCLCore/CMCLGameLaunching/CommandGenerating.py 里面] -> "argument"[其代表的意思]等等）
  
<h5>提示</h5>

- 任何 bug 都可以通过 Issues （问题）页面进行反馈。

- 你可以帮忙翻译一下启动器，让启动器支持更多的语言。（英语翻译文件：CMCL_en-gb.ts / CMCL_en-us.ts，中文翻译文件：CMCL_zh-cn.ts / CMCL_zh-hk.ts / CMCL_zh-tw.ts / CMCL_lzh.ts，其它翻译请新建一个 Pull request）

<h5>运行启动器</h5>

1. 你可以从右侧的 Releases（版本）下载启动器。

2. 下载源代码。
   - 点击 Code -> Download ZIP，下载源代码的 zip 压缩包。

   - 解压压缩包。

   - 确保你有 Python 3.12 作为 Python 解释器。

   - 运行 `pip install -r requirements.txt`。

   - 运行 `python main.py`。

<h5>重要内容</h5>

- 你可以下载源代码，但是你**不可以**修改。

- 你**能**借鉴每个文件的一小部分，但是请**不要**直接 Ctrl + C 然后 Ctrl + V（直接复制），也请**不要**商用，谢谢配合。

- 除了启动器的可执行文件外，其它文件不能二次转发。
