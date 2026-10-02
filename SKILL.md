---
name: paper2wechat
description: Use when a user wants to analyze an academic paper URL, PDF, or local file into a source-grounded Chinese WeChat article, format an existing article for WeChat, verify paper-specific figures, or create a WeChat draft.
---

# Paper2WeChat

一个可同时由 **Claude Code** 和 **Codex** 发现的 Agent Skill：从论文来源核验、中文故事化解读和论文配图检查，到公众号排版与按需创建草稿。只有一份 `SKILL.md` 和一套脚本；按当前任务读取对应参考文件，不要求用户安装第二个排版 Skill。

## 按任务读取参考文件

- 用户提供论文链接、PDF 或本地论文并要分析/成稿：先完整读取 [`references/paper-analysis.md`](references/paper-analysis.md) 和 [`references/wechat-formatting.md`](references/wechat-formatting.md)。
- 用户只要求排版已有文章：读取 [`references/wechat-formatting.md`](references/wechat-formatting.md)；涉及 Obsidian 语法或需要内容结构建议时，再读取 [`references/obsidian-layout.md`](references/obsidian-layout.md)。
- 用户明确要求代码分析、公式或学术风格时，按论文分析参考文件中的可选模式执行。

## 跨 Agent 与路径约定

- 这是一份标准 `SKILL.md`，同一仓库可供 Claude Code 与 Codex 使用。使用当前 Agent 提供的文件、网页、浏览器和终端能力；不要假定另一宿主的专属工具或 shell。
- 先定位**当前加载的 `SKILL.md` 所在仓库根目录**，并确认其中存在 `scripts/paper2wechat.py`、`themes/` 和 `templates/`。如果 Skill 通过符号链接安装，使用链接实际指向的仓库目录。运行脚本时使用绝对路径，不能假定用户当前项目下有 `scripts/`。
- 论文 Markdown、下载文件、图片、清单、HTML 和预览都写入用户当前项目/工作区的 `outputs/paper2wechat/<paper-slug>/` 或用户指定目录。不要把生成物写进全局 Skill 安装目录。
- 相对 `--output` 以启动命令时的当前项目/工作区为基准。格式器的默认输出是当前工作区中的 `outputs/wechat-format/`。
- 命令使用跨 shell 的单行形式。按当前环境选择 `python`、`python3` 或 Windows 的 `py -3`；不要把 PowerShell 反引号续行或 Bash 反斜杠续行交给另一种 shell。

## 论文到公众号文章

用户给论文链接时，默认完成来源核验、论文分析、中文故事化写作、图片来源校验、格式生成和预览检查。具体的标题规则、证据边界、文章结构、配图闭环和交付门槛以 `references/paper-analysis.md` 为准。

只从当前论文的 HTML、PDF 或 source archive 提取图片。每张图都必须能追溯到论文图号/来源文件，并记录在该论文目录自己的 `work/images-manifest.json`。正文图片路径必须指向同一论文目录的 `images/`；排版后再检查 HTML 实际引用和图片数量，禁止混入 logo、头像、网页装饰图或其他论文图片。

所有事实以论文及其补充材料为准。区分论文报告、图中直接可见的结果和分析者推断；不猜图表数字，不夸大实验支持范围。默认读者向故事化表达，不写源码路径、函数名、公式源码或代码分析，除非用户明确要求相应模式。

## 排版与草稿

格式器、85 个主题、主题图库、Obsidian/Markdown 特性、校验器和发布工具都属于同一个 Skill 的能力。用户只要求分析或排版时，完成预览后停止；**只有用户明确要求推送/创建草稿时才调用发布脚本**。

通过论文和图片校验后，可用统一流水线完成标点检查、校验、微信 HTML 与预览生成：

```text
python "{skill-root}/scripts/paper2wechat.py" --input "{workspace-root}/outputs/paper2wechat/{paper-slug}/{paper-slug}.md" --output "{workspace-root}/outputs/wechat-format" --source-url "{paper-url}" --theme bytedance
```

若用户明确要求创建公众号草稿，在同一命令追加 `--push`，并传入标题、作者等必要参数。`--dry-run` 可能会上传素材到公众号素材库，不等于只做本地检查。调用发布工具前必须通过 Markdown 与 HTML 校验；不得声称草稿已创建，除非接口明确返回成功。密钥不得写入文章或输出日志。

已有文章排版、图库比较、智能语义增强、不同 HTML 输出格式、字号和完整发布参数见 [`references/wechat-formatting.md`](references/wechat-formatting.md)。不要为了使用这些选项删除或绕过论文来源、图片路径和推送安全检查。

## 最终交付检查

- 论文来源、版本、作者和链接准确；标题吸引人且不夸大论文结论。
- 文章中的每张图属于当前论文，来源清单、相对路径和 SHA-256 核验一致；没有混入其他图片。
- Markdown 与生成 HTML 的内容结构、公式处理及图片引用均通过校验；预览和公众号正文 HTML 都有完整可见正文。
- 明确区分已生成预览和已成功创建草稿；没有用户明确推送请求时，不执行发布。
