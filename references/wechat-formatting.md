## Integrated WeChat formatting and draft publishing

Paper2WeChat is one skill with one user-facing workflow. Use the formatter and publisher scripts as internal stages; do not ask the user to install a second formatter skill.

### Format a validated article

Before formatting, run the Chinese punctuation check and fix violations on the article Markdown:

```text
python "{skill-root}/scripts/zh_punctuation_fix.py" "{workspace-root}/outputs/paper2wechat/{paper-slug}/{paper-slug}.md" --write
```

Then create a WeChat article and preview using a selected theme:

```text
python "{skill-root}/scripts/format.py" --input "{workspace-root}/outputs/paper2wechat/{paper-slug}/{paper-slug}.md" --theme bytedance --no-open
```

To open the gallery and compare its curated theme set using the real article, pass `--gallery`; all 85 JSON themes remain selectable directly with `--theme`. The output is stored below `outputs/wechat-format/` by default. Preserve the paper article's `images/` directory and its `work/images-manifest.json`; never add a page logo, avatar, image from another paper, or decorative search result.

The formatter retains inline WeChat-compatible HTML, standard HTML and plain output; Obsidian wikilinks and Markdown images; footnotes for external links; callouts; dialogue, gallery, long-image, intro, end, history and video containers; quotation cards; heading decorators; configurable themes; smart semantic enhancement; and font sizing. Its helper scripts include Chinese punctuation checking and LaTeX-to-image conversion. For Obsidian-specific content-design guidance, read [`obsidian-layout.md`](obsidian-layout.md).

The CLI also keeps `--format {wechat,html,plain}`, `--gallery`, `--recommend`, `--smart`, `--font-size`, `--vault-root`, `--output`, and `--no-open`. Use `python "{skill-root}/scripts/format.py" --help` for the complete option list. These standalone formatter options remain available alongside the paper-to-WeChat unified runner.

After the article is drafted from the paper and the source images are verified, use the unified runner for punctuation repair, validation, formatting, and optional publishing:

~~~text
python "{skill-root}/scripts/paper2wechat.py" --input "{workspace-root}/outputs/paper2wechat/{paper-slug}/{paper-slug}.md" --output "{workspace-root}/outputs/wechat-format" --theme bytedance --source-url "{paper-url}"
~~~

Add --push only when the user explicitly asks to create a WeChat draft. Use --dry-run only when they request a publishing test; this may upload article images to the WeChat media library while skipping draft creation. The unified runner covers the post-analysis stages; it does not replace reading the paper or writing the evidence-grounded article.

### Verify before any draft push

Run the storytelling validator on the Markdown and then on the rendered article HTML. Both checks must report `"ok": true`. Confirm each article image is inside the current paper's own `images/` folder and matches `work/images-manifest.json` by path and SHA-256.

Only when the user explicitly asks to push, run the publisher. A dry-run performs article validation and may upload images to the WeChat media library, but it never creates a draft. Draft creation requires a non-dry-run invocation and explicit confirmation (`--yes` for non-interactive use). Never call the publisher as an implicit step.

```text
python "{skill-root}/scripts/publish.py" --dir "{workspace-root}/outputs/wechat-format/{paper-slug}" --cover "images/figure1.png" --title "{chosen-title}" --author "Tau Lab" --source-url "{paper-url}" --yes
```

For a dry-run, add `--dry-run` and omit `--yes`. Do not claim a draft was created unless the publisher confirms the WeChat draft API succeeded. Do not print secrets, access tokens, or unredacted API diagnostics.

### Portable local configuration

Copy `config.example.json` to the ignored root-level `config.json`. Paper analysis and formatting require no account credentials. Use `WECHAT_APP_ID` and `WECHAT_APP_SECRET` environment variables for publishing; they take precedence over local secrets. Use `SMART_FORMAT_API_KEY` (or `OPENAI_API_KEY`) only when requesting `--smart`. Never commit `config.json`, generated articles, debug HTML, caches, or local images.

---

## Preserved formatter guidance

公众号一键排版技能。把任意文本内容（Markdown、纯文本、格式粗糙的笔记）转成微信公众号兼容的排版 HTML，AI 自动理解内容结构并增强排版，可视化选择主题后一键复制粘贴到微信后台。

把文章转为微信公众号兼容的内联样式 HTML。支持 Markdown 和纯文本输入，AI 自动补充结构和排版增强。当用户说"排版""微信排版""格式化文章""format"时使用。

## Instructions

### 触发条件

用户说以下任何一种：
- `/format 文件路径`
- `排版这篇文章`
- `微信排版`
- `格式化为公众号格式`
- `把这篇转成微信格式`

### 完整工作流

#### 第 1 步：确认文章

1. 如果用户给了文件路径，直接读取
2. 如果没给路径，问用户要文章路径
3. 读取文章内容，确认标题和字数

#### 第 1.2 步：标点质检（必跑，阻断式）

读取文章后、进入排版前,**必须**跑一次中文正文半角标点修复:

```text
python "{skill-root}/scripts/zh_punctuation_fix.py" "文章路径.md" --write
```

脚本自动把中文字符旁的半角 `, : ; ? ! . ( )` 换成全角 `,:;?!。()`,保护代码块/行内 code/URL/Markdown 链接段不误伤。

输出会打印「违规: N → 0」。N > 0 = 原文有违规,已写回修复后内容。N = 0 = 已干净,零改动。

**此步不能跳过**——半角英文标点挤在中文字之间是典型 AI 味,读者第一眼就看出代码注释感。中文段落应使用中文标点；英文术语、代码、URL 和 Markdown 链接中的标点保持原样。

---

#### 第 1.5 步：结构化预处理（仅在需要时）

读取文章后，先检测输入内容的 Markdown 结构完整度，决定是否需要 AI 结构化预处理。

**检测方法**：扫描全文，统计 `##` 标题、`**加粗**`、`- 列表`、`> 引用`、`` ` 代码 ` `` 等格式标记的数量。

**判断规则**：
- 有 `##` 标题且格式标记分布合理 → **跳过**，直接进入第 2 步
- 缺少 `##` 标题，或几乎没有格式标记（纯文本/粗糙笔记）→ **执行结构化**

**结构化规则（底线：只加标记，不改内容）**：

1. **加标题**：识别文章的逻辑段落和主题转换点，在转换处插入 `##` 标题。标题从内容中提炼，不编造。三段内容不硬拆五个标题——尊重原文信息密度
2. **分段落**：确保段落之间有空行分隔，长段落在语义转换处拆分
3. **加列表**：识别并列/枚举性质的内容，加 `- ` 或 `1. ` 标记
4. **加强调**：识别关键词、产品名、核心概念，加 `**加粗**`
5. **清理格式**：去除多余空行、修正缩进、统一标点
6. **不改措辞**：不调语序、不增删内容、不润色文字。用户写什么就是什么，只加结构标记

**保存与告知**：
- 结构化后保存为 `outputs/tmp/xxx-structured.md`
- 告知用户："检测到输入缺少 Markdown 格式标记，已自动补充标题和结构，保存在 xxx-structured.md，可检查调整"
- 后续第 2 步基于 structured.md 继续处理

---

#### 第 2 步：AI 内容分析 + 自动套格式

读取文章（或上一步输出的 structured.md），AI 分析内容结构，在 Markdown 层面自动套用合适的排版容器。核心是理解内容后再匹配呈现方式，而不是机械套模板。

**分析维度**：文章类型（访谈/教程/产品介绍/深度分析）、内容元素（对话/图片/代码/数据）、节奏感（密集段 vs 留白段）。

**自动套用规则**（按优先级）：

1. **对话/访谈** → `:::dialogue[标题]`
   - 检测到 `**名字：**` 或 `名字：` 交替出现 → 用 `:::dialogue` 包裹
   - 格式：`名字: 对话内容`（中英文冒号都支持）
   - 不是所有对话都要套——独白段落、叙述性段落保持原样
   - 同一场景的连续对话放一个 dialogue 块，换场景换一个新块

2. **连续多图** → `:::gallery[标题]`
   - 3张以上连续图片 → 自动套 `:::gallery`，横向滚动浏览
   - 适合产品截图、对比图、系列图

3. **超长图片** → `:::longimage[标题]`
   - 流程图、架构图、长截图 → 固定高度容器，纵向滚动
   - 一般需要用户标注或 AI 判断图片内容

4. **核心观点/金句** → callout 格式
   - 核心观点 → `> [!important] 标题`
   - 小技巧/提示 → `> [!tip] 标题`
   - 注意事项 → `> [!warning] 标题`
   - 普通引用 → `> [!callout] 标题`（使用主题色）
   - 不要过度使用，一篇文章 1-3 处即可

5. **分隔符** → 在章节转换处确保有 `---` 分隔

6. **图说标记** → 图片后紧跟的说明用斜体：`*这是图片说明*`

7. **外部链接** → 无需处理（脚本自动转脚注）

**处理完成后**，把增强后的 Markdown 保存为临时文件（`outputs/tmp/xxx-enhanced.md`）。

#### 第 2.5 步：推荐主题

根据内容分析结果，推荐 3 个最适合的主题：

| 内容类型 | 推荐主题 |
|----------|----------|
| 深度长文/分析 | newspaper, magazine, ink |
| 科技产品/AI工具 | bytedance, github, sspai |
| 访谈/对话体 | terracotta, coffee-house, mint-fresh |
| 教程/操作指南 | github, sspai, bytedance |
| 文艺/随笔/观点 | terracotta, sunset-amber, lavender-dream |
| 活力/动态/速报 | sports, bauhaus, chinese |

推荐的主题 ID 通过 `--recommend` 参数传给脚本，在 gallery 中高亮显示。

#### 第 3 步：打开主题画廊（默认流程）

```text
python "{skill-root}/scripts/format.py" --input "文章路径.md" --gallery --recommend newspaper magazine ink
```

这会用用户的**真实文章**渲染 34 个精选主题（完整主题库共 85 个），在浏览器打开画廊页面。用户点按钮切换主题预览，选中后点「用这个风格排版」一键复制到剪贴板。

#### 第 3 步（备选）：直接指定主题排版

如果用户已经知道想用哪个主题，可以跳过画廊直接排版：

```text
python "{skill-root}/scripts/format.py" --input "文章路径.md" --theme terracotta
```

#### 第 4 步：确认结果

告诉用户：
- Gallery 模式：在浏览器中切换主题预览，选中后点按钮复制，粘贴到公众号后台
- 直接模式：在浏览器中检查预览，点「复制到微信」按钮

### 参数说明

- `--input` / `-i`：Markdown 文件路径（必须）
- `--gallery`：打开主题画廊（推荐，默认使用）
- `--theme` / `-t`：直接指定主题名（跳过画廊）
- `--output` / `-o`：输出目录（默认 outputs/tmp）
- `--recommend`：推荐的主题 ID 列表，gallery 中高亮显示（如 `--recommend newspaper magazine ink`）
- `--no-open`：不自动打开浏览器

### 可用主题（完整主题库共 85 个；下表为常用主题）

#### 独立风格（9 个，差异最大）

| 主题 | 命令值 | 风格 |
|------|--------|------|
| 赤陶 | terracotta | 暖橙色，满底圆角标题，左边框渐变 |
| 字节蓝 | bytedance | 蓝青渐变、窄栏高行距、胶囊章节标题，适合技术长文 |
| 中国风 | chinese | 朱砂红，古典雅致 |
| 报纸 | newspaper | 纽约时报风，严肃深度 |
| GitHub | github | 开发者风，浅色代码块 |
| 少数派 | sspai | 中文科技媒体红 |
| 包豪斯 | bauhaus | 红蓝黄三原色，先锋几何 |
| 墨韵 | ink | 纯黑水墨，极简留白 |
| 暗夜 | midnight | 深色底+霓虹色，赛博朋克 |

#### 精选风格（7 个）

| 主题 | 命令值 | 风格 |
|------|--------|------|
| 运动 | sports | 渐变色带，活力动感 |
| 薄荷 | mint-fresh | 薄荷绿，清爽健康 |
| 日落 | sunset-amber | 琥珀暖调，温暖感性 |
| 薰衣草 | lavender-dream | 紫色梦幻，浪漫诗意 |
| 咖啡 | coffee-house | 棕色暖调，稳重温馨 |
| 微信原生 | wechat-native | 微信绿，传统阅读 |

#### 字节蓝正文基线

`bytedance` 面向公众号技术长文时，正文按“窄栏、松行距、强层级”处理：桌面预览约 645px 正文宽度，正文 17px、行距约 2.0；章节标题采用蓝到青的渐变胶囊，关键句使用亮蓝粗体，引用采用青色左边框卡片，列表使用青色圆点或蓝色数字圆点。预览壳应模拟真实公众号文章栏，不使用手机屏幕宽度压缩正文。

排版前先检查 Markdown 是否真的表达出这些结构，不能指望 CSS 从普通段落中猜出层级：

- 作者、论文、数据等开头元信息逐项换行；元信息与正文之间用分隔线和留白。
- “第一步/第二步/第三步”等连续步骤必须已写成同一组 Markdown 有序列表；不要保留重复的步骤小标题和重复概括列表。
- 引用原句必须是 Markdown `>` 引用块，关键句必须直接用 `**观点本身**` 强调，不把“关键句：”当作正文内容。
- 转换后核对文章 HTML：元信息有换行、列表保留编号/圆点、引用为独立卡片、`strong` 使用主题强调蓝色。结构缺失时先回到 Markdown 修正，再重新排版。
| 杂志 | magazine | 超大留白，品质长文 |

#### 模板系列（14 个，布局×配色）

四种布局（简约/聚焦/精致/醒目）× 多种配色（金/蓝/红/绿/藏青/灰）

### 微信兼容说明

脚本自动处理以下微信限制：
- **纯内联样式**：所有 CSS 直接写在每个标签的 `style="..."` 属性上
- **列表模拟**：`<ul>/<ol>` 改为 `<section>` + flexbox 模拟
- **引用块转 section**：输出端 `<blockquote>` 统一换成 `<section>`（2024-11 起微信新版编辑器会重写 blockquote 剥掉样式，doocs/md #447）
- **margin 简写**：margin-top/bottom 分拆写法自动合并（分拆写法有被编辑器丢弃的报告）
- **外链转脚注**：`[text](url)` 自动变成正文 `text[1]` + 文末脚注列表
- **图片处理**：`![[image.jpg]]` 自动搜索 Vault 并复制到输出目录
- **SVG 自动转 PNG**：公众号素材库不收 SVG，本地 `.svg` 图自动经 qlmanage 转 PNG；外链 SVG 打警告
- **视频自动识别**：独占一行的 YouTube/B站/视频号/.mp4 链接自动转"视频卡片"（▶ 徽章+标题+脚注链接）。公众号不支持外链视频，需播放器请在后台手动插视频号/腾讯视频
- **多类型提示框**：`[!tip]`/`[!note]`/`[!important]`/`[!warning]`/`[!caution]` 各有独立配色
- **图说识别**：图片后紧跟的斜体段落自动变为居中灰色图说
- **对话气泡**：`:::dialogue[标题]` → 左右交替聊天气泡，右侧用主题色
- **图片画廊**：`:::gallery[标题]` → 横向滚动多图容器
- **长图展示**：`:::longimage[标题]` → 固定高度纵向滚动容器（内部可上下滑动看全长图）

### 金句卡片与头尾槽位（2026-06-12 新增）

- **金句卡片**：`>> 文字` → 白底阴影卡；`>>> 文字` → 居中金句卡（主题色顶线）。主题可用 `styles.quote_card / quote_card_center / quote_card_p` 覆盖
- **`:::intro` 导读块**：文首彩底导读（科技号报道头式），`:::intro[自定义标签]` 改标签文字
- **`:::end[可选CTA文案]`**：— END — 结束符 + 可选"点赞在看"引导文案
- **`:::history[往期回顾]`**：文末往期文章卡，内容写 `- [标题](链接)` 列表，链接自动转脚注
- **`:::video[标题]`**：手动视频卡片，内容第一行 URL、第二行可选说明

### 主题三层标题结构（2026-06-12 新增，治"换色游戏"的根）

主题 JSON 里声明 `h2_inner` / `h2_prefix` / `h2_suffix`（h1-h6 同理）即触发三层渲染：

```html
<h2 style="外层只管布局"><span style="prefix">01</span><span style="inner">标题文字</span></h2>
```

- 视觉挂在 inner 上（inline-block 自动收缩 → **色块宽度=文字宽度**）
- prefix/suffix 是伪元素的实体替身：编号、楔子、装饰符号；文本配在根级 `decor.h2.prefix_text`，`{n}` 自动替换为 01、02 递增序号
- `blockquote_prefix` 同理（引用块大引号 ❝，文本在 `decor.blockquote.prefix_text`）
- 老主题不写新字段走原单层逻辑，零破坏
- 参考实现：data-report（编号标题）、interview（吊牌标题+居中短下划线+大引号）、glass-light（渐变圆点+玻璃药丸）
- 展示型主题（大标题是风格本体）在 JSON 根加 `"lint": {"display_type": true}` 豁免 theme_lint 的 H1/H2 上限检查

### 注意事项

- 依赖 Python `markdown` 库（系统已安装）
- 图片在预览中可见，但粘贴到微信后需要手动上传
- 如果用户对排版不满意，可以切换主题重新生成

### 推送草稿箱

用户明确说“推送”时，使用 `scripts/publish.py` 将已经通过校验的 `article.html` 推送到微信公众号草稿箱。推送只使用当前文章目录中的图片；封面优先使用该论文的第一张最终图片，不生成额外网络图片：

```text
python "{skill-root}/scripts/publish.py" --dir "wechat/{paper-slug}" --cover "images/figure1.png" --title "文章标题" --author "Tau Lab" --source-url "论文原文链接" --yes
```

推送前必须完成 Markdown 和 HTML 两次结构校验；默认推送脚本还会拒绝 `$$...$$`、`$...$` 和 LaTeX 命令残留，只有明确公式模式才传 `--allow-formulas`。推送后报告标题、作者、正文图片数量、留言状态、草稿是否成功和本地预览路径；不得输出 app secret、access token 或其他密钥。配置中的“请填写……”等合集占位符按未配置处理，只有有效 `--album-id` 才绑定合集。

---
