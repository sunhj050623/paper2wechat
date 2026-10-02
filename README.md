# 📚 Paper2WeChat

**从论文链接到微信公众号草稿，一站完成。** Paper2WeChat 将论文分析、中文故事化写作、论文配图校验、公众号排版和可选草稿推送整合为一个同时适用于 Claude Code 与 Codex 的 Agent Skill。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)]

[简体中文](#简体中文) · [English](#english)

## 简体中文

给它一篇 arXiv 论文、论文链接或 PDF，按照根目录的 [`SKILL.md`](SKILL.md) 阅读来源、撰写有证据支撑的中文文章，再生成公众号预览；只有你明确要求时，才会创建公众号草稿。

> **说明：** 阅读论文和撰写文章由 Skill 工作流完成；`scripts/paper2wechat.py` 从已经写好的 Markdown 文章开始，负责标点修复、校验、排版和可选推送。

### ✨ 功能

- 🧠 默认采用面向读者的故事化解读；代码分析和公式解释可按需开启。
- 🖼️ 只使用当前论文的图片。每篇文章都有图片来源清单和 SHA-256 校验，避免混入网页标志、头像或其他文章图片。
- 🎨 内置 **85 款排版主题**，包含主题图库、公众号预览，以及微信公众号内联 HTML、标准 HTML 和纯文本格式。
- 🪄 保留原格式器能力：Markdown 与 Obsidian 图片、脚注、提示块、对话、图集、长图、引用卡片、标题装饰、智能语义排版和字号设置。
- 🚀 可选上传素材并创建微信公众号草稿；不会因为完成分析或排版而自动推送。

### ⚡ 快速开始

#### 安装一份 Claude Code 与 Codex 共用的 Skill

只克隆一份仓库到 Codex 与 Agent Skills 共用目录，再让 Claude Code 的 skills 目录通过链接指向同一份仓库。更新时只需在共用目录执行一次 `git pull`。

**Windows PowerShell**

```powershell
$agentSkills = Join-Path $HOME ".agents/skills"
$claudeSkills = Join-Path $HOME ".claude/skills"
$skill = Join-Path $agentSkills "paper2wechat"
New-Item -ItemType Directory -Force $agentSkills, $claudeSkills | Out-Null
git clone https://github.com/sunhj050623/paper2wechat.git $skill
New-Item -ItemType Junction -Path (Join-Path $claudeSkills "paper2wechat") -Target $skill
```

**macOS / Linux**

```bash
git clone https://github.com/sunhj050623/paper2wechat.git "$HOME/.agents/skills/paper2wechat"
mkdir -p "$HOME/.claude/skills"
ln -s "$HOME/.agents/skills/paper2wechat" "$HOME/.claude/skills/paper2wechat"
```

Codex 会从 `~/.agents/skills/` 发现 Skill；Claude Code 会从 `~/.claude/skills/` 发现它。两个入口指向同一份 `SKILL.md` 和脚本。安装后重启或刷新 Agent。要更新时，在 `$HOME/.agents/skills/paper2wechat` 执行 `git pull`。

#### 安装脚本依赖

```powershell
python -m pip install -e "$HOME/.agents/skills/paper2wechat"
```

```bash
python3 -m pip install -e "$HOME/.agents/skills/paper2wechat"
```

Python 3.8 或更新版本均可。仅使用论文分析和排版时不需要配置微信公众号凭据。

### 📝 工作流

1. 提供论文链接、PDF、HTML 或本地论文文件。
2. 阅读论文并撰写来源可追溯的中文文章；只提取这篇论文的图片，并校验图片路径和来源清单。
3. 生成 `article.html` 和 `preview.html`，检查排版及所有图片引用。
4. 需要公众号草稿时，明确要求推送，并配置微信公众号凭据。

### 🛠️ 命令行

先由 Skill 工作流完成分析并保存 Markdown。假设文章位于当前项目的 `outputs/paper2wechat/<paper-slug>/<paper-slug>.md`。从任意工作目录调用脚本时，请使用 Skill 安装目录的完整路径；输出目录留在当前项目：

**生成排版和预览**（不会推送）：

```bash
python "/path/to/paper2wechat/scripts/paper2wechat.py" --input "/path/to/project/outputs/paper2wechat/<paper-slug>/<paper-slug>.md" --output "/path/to/project/outputs/wechat-format" --source-url "https://arxiv.org/abs/<paper-id>" --theme bytedance
```

**按需比较主题**（85 款主题均可通过 `--theme` 选择，图库展示精选主题）：

```bash
python "/path/to/paper2wechat/scripts/format.py" --input "/path/to/project/outputs/paper2wechat/<paper-slug>/<paper-slug>.md" --output "/path/to/project/outputs/wechat-format" --gallery --no-open
```

**明确创建公众号草稿：**

```bash
python "/path/to/paper2wechat/scripts/paper2wechat.py" --input "/path/to/project/outputs/paper2wechat/<paper-slug>/<paper-slug>.md" --output "/path/to/project/outputs/wechat-format" --source-url "https://arxiv.org/abs/<paper-id>" --theme bytedance --push
```

`--push` 会将素材上传并创建草稿；`--dry-run` 会验证发布链路并可能上传素材，但不会创建草稿。封面默认取当前论文图片清单中的图片，也可用 `--cover` 指定。推送前请确认标题、作者、来源链接和封面。

其他选项可运行 `python "/path/to/paper2wechat/scripts/paper2wechat.py" --help`、`python "/path/to/paper2wechat/scripts/format.py" --help` 或 `python "/path/to/paper2wechat/scripts/publish.py" --help` 查看。格式器保留 `--format {wechat,html,plain}`、`--smart`、`--font-size`、`--recommend` 等选项。

### 🔐 配置

复制 `config.example.json` 为仓库根目录下的 `config.json`，或者通过环境变量提供密钥。`config.json` 已被 Git 忽略，不要提交真实密钥。

```powershell
$env:WECHAT_APP_ID = "your-app-id"
$env:WECHAT_APP_SECRET = "your-app-secret"
$env:SMART_FORMAT_API_KEY = "your-api-key"  # 仅在请求 --smart 时需要
```

macOS / Linux:

```bash
export WECHAT_APP_ID="your-app-id"
export WECHAT_APP_SECRET="your-app-secret"
export SMART_FORMAT_API_KEY="your-api-key"  # Only needed for --smart
```

也支持 `SMART_API_KEY`、`OPENAI_API_KEY` 和 `AI_API_KEY`。环境变量优先于本地配置。公众号凭据只在上传图片或创建草稿时需要。

### 🖼️ 图片来源与安全

- 文章图片必须位于当前论文的 `images/` 目录，并与 `work/images-manifest.json` 中的来源和 SHA-256 一致。
- 排版和推送时拒绝目录外路径、路径穿越和外部远程图片；不会自动抓取网页装饰图。
- 生成的文章、图片、调试文件和本地配置均不应提交到仓库。

### 🧪 测试

```bash
python -m pip install -e ".[test]"
python -m pytest -q
```

### 📁 项目结构

```text
paper2wechat/
├── SKILL.md          # 单一 Skill 入口和完整论文分析工作流
├── scripts/          # 图片校验、排版、验证、统一流水线和公众号发布工具
├── themes/           # 85 款 JSON 排版主题
├── templates/        # 主题图库和预览模板
├── styles/           # 故事化、学术、公式与代码分析写作约定
└── tests/            # 自动化测试与主题清单
```

### 📄 许可证

本项目采用 [MIT License](LICENSE)。

---

## English

**From a paper URL to a WeChat draft in one workflow.** Paper2WeChat combines paper analysis, evidence-grounded Chinese storytelling, paper-figure validation, WeChat formatting, and optional draft creation in one Agent Skill for Claude Code and Codex.

Give the workflow an arXiv link, paper URL, or PDF. The root [`SKILL.md`](SKILL.md) guides source reading and article writing, then produces a WeChat-ready preview. A draft is created only when you explicitly request it.

> **How it works:** The Skill reads the paper and writes the article. `scripts/paper2wechat.py` starts from drafted Markdown and handles punctuation, validation, formatting, and optional publishing.

### ✨ Features

- 🧠 Reader-focused storytelling by default, with opt-in code analysis and formula explanations.
- 🖼️ Paper-specific figures only. A per-paper manifest records image provenance and SHA-256 hashes to prevent unrelated logos, avatars, or figures from being mixed in.
- 🎨 **85 formatting themes**, a theme gallery and preview, plus WeChat-compatible inline HTML, standard HTML, and plain-text output.
- 🪄 Preserved formatter features: Markdown and Obsidian images, footnotes, callouts, dialogue, galleries, long-image blocks, quote cards, heading decorations, smart semantic formatting, and font sizing.
- 🚀 Optional media upload and WeChat draft creation. Analysis and formatting never publish automatically.

### ⚡ Quick start

#### Install one Skill shared by Claude Code and Codex

Clone one copy into the shared Agent Skills directory used by Codex, then link Claude Code's skill directory to that same checkout. Updates only require one `git pull`.

**Windows PowerShell**

```powershell
$agentSkills = Join-Path $HOME ".agents/skills"
$claudeSkills = Join-Path $HOME ".claude/skills"
$skill = Join-Path $agentSkills "paper2wechat"
New-Item -ItemType Directory -Force $agentSkills, $claudeSkills | Out-Null
git clone https://github.com/sunhj050623/paper2wechat.git $skill
New-Item -ItemType Junction -Path (Join-Path $claudeSkills "paper2wechat") -Target $skill
```

**macOS / Linux**

```bash
git clone https://github.com/sunhj050623/paper2wechat.git "$HOME/.agents/skills/paper2wechat"
mkdir -p "$HOME/.claude/skills"
ln -s "$HOME/.agents/skills/paper2wechat" "$HOME/.claude/skills/paper2wechat"
```

Codex discovers skills from `~/.agents/skills/`; Claude Code discovers them from `~/.claude/skills/`. Both entries point to the same `SKILL.md` and scripts. Restart or refresh the agents after installation. To update, run `git pull` once in `$HOME/.agents/skills/paper2wechat`.

#### Install script dependencies

```powershell
python -m pip install -e "$HOME/.agents/skills/paper2wechat"
```

```bash
python3 -m pip install -e "$HOME/.agents/skills/paper2wechat"
```

Python 3.8 or newer is supported. WeChat credentials are not needed for paper analysis or formatting.

### 📝 Workflow

1. Provide a paper URL, PDF, HTML page, or local paper file.
2. Read the paper and write a source-grounded Chinese article. Extract figures from that paper only and validate their paths and provenance manifest.
3. Generate `article.html` and `preview.html`, then check the rendered layout and image references.
4. To create a WeChat draft, explicitly request publishing and configure WeChat credentials.

### 🛠️ Command line

First use the Skill workflow to analyze the paper and save a Markdown article. The examples below assume it is saved under the current project at `outputs/paper2wechat/<paper-slug>/<paper-slug>.md`. Use the installed Skill's absolute script path and keep outputs in the current project.

**Format and preview** (does not publish):

```bash
python "/path/to/paper2wechat/scripts/paper2wechat.py" --input "/path/to/project/outputs/paper2wechat/<paper-slug>/<paper-slug>.md" --output "/path/to/project/outputs/wechat-format" --source-url "https://arxiv.org/abs/<paper-id>" --theme bytedance
```

**Compare themes** (all 85 themes are available through `--theme`; the gallery shows a curated selection):

```bash
python "/path/to/paper2wechat/scripts/format.py" --input "/path/to/project/outputs/paper2wechat/<paper-slug>/<paper-slug>.md" --output "/path/to/project/outputs/wechat-format" --gallery --no-open
```

**Explicitly create a WeChat draft:**

```bash
python "/path/to/paper2wechat/scripts/paper2wechat.py" --input "/path/to/project/outputs/paper2wechat/<paper-slug>/<paper-slug>.md" --output "/path/to/project/outputs/wechat-format" --source-url "https://arxiv.org/abs/<paper-id>" --theme bytedance --push
```

`--push` uploads media and creates a draft. `--dry-run` validates the publishing flow and may upload media, but does not create a draft. The cover defaults to an image in the current paper's manifest; use `--cover` to select one explicitly. Review the title, author, source URL, and cover before publishing.

Run `python "/path/to/paper2wechat/scripts/paper2wechat.py" --help`, `python "/path/to/paper2wechat/scripts/format.py" --help`, or `python "/path/to/paper2wechat/scripts/publish.py" --help` for all options. The formatter also retains options such as `--format {wechat,html,plain}`, `--smart`, `--font-size`, and `--recommend`.

### 🔐 Configuration

Copy `config.example.json` to `config.json` in the repository root, or supply secrets through environment variables. `config.json` is ignored by Git; never commit real credentials.

```powershell
$env:WECHAT_APP_ID = "your-app-id"
$env:WECHAT_APP_SECRET = "your-app-secret"
$env:SMART_FORMAT_API_KEY = "your-api-key"  # Only needed when using --smart
```

macOS / Linux:

```bash
export WECHAT_APP_ID="your-app-id"
export WECHAT_APP_SECRET="your-app-secret"
export SMART_FORMAT_API_KEY="your-api-key"  # Only needed for --smart
```

`SMART_API_KEY`, `OPENAI_API_KEY`, and `AI_API_KEY` are also supported. Environment variables take precedence over local configuration. WeChat credentials are only needed to upload media or create a draft.

### 🖼️ Image provenance and safety

- Article images must be inside the current paper's `images/` directory and match the source and SHA-256 recorded in `work/images-manifest.json`.
- Formatting and publishing reject paths outside the article, path traversal, and remote images. The tools do not fetch decorative webpage images.
- Do not commit generated articles, images, debug files, or local configuration.

### 🧪 Tests

```bash
python -m pip install -e ".[test]"
python -m pytest -q
```

### 📁 Project structure

```text
paper2wechat/
├── SKILL.md          # One portable Claude Code + Codex Skill entry point
├── references/       # Detailed paper analysis, formatting, and Obsidian guidance
├── scripts/          # Image validation, formatting, validation, pipeline, and publisher
├── themes/           # 85 JSON formatting themes
├── templates/        # Theme gallery and preview templates
├── styles/           # Storytelling, academic, formula, and code-analysis guidance
└── tests/            # Automated tests and theme inventory
```

### 📄 License

This project is licensed under the [MIT License](LICENSE).
