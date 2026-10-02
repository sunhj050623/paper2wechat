---
name: paper2wechat
description: Use when turning an academic paper URL, PDF, or local paper into a source-grounded Chinese storytelling article and an optional WeChat draft. The default output is reader-facing prose; source-code analysis is opt-in only.
---

# Paper2WeChat

把论文变成一篇可以直接阅读和排版的中文深度文章。默认目标是 **storytelling（故事型）**，不是代码审查报告，也不是论文源码说明。

## 写作总契约

读者读完后，应该能用三句话复述：论文在什么具体场景里遇到什么问题、作者改变了哪一个环节、图表和实验提供了什么证据。文章不能把图片当装饰，也不能用一个听起来有气势但没有对象的口号代替标题。

每张入选论文图都必须完成一条完整的信息链：**为什么此处需要这张图 → 图中观察到什么 → 这说明什么 → 证据不能说明什么**。这条链写进正文的自然段，不写成生硬的“图表分析：”模板，也不把分析藏在图注里。

## 默认边界

- 默认只分析论文正文、图表、实验和作者明确写出的局限。
- 可以查看公开代码来确认论文中的方法是否有实现，但代码只作为内部核对材料，不写入正文。
- 只有用户明确要求“分析代码、实现细节、仓库结构、复现步骤”时，才启用代码分析模式；启用后要先说明这会改变文章风格。
- 默认正文禁止出现代码块、函数名、文件路径、行号、命令、仓库目录、源码截图和“代码已公开……”类段落。
- 默认不写公式推导。需要解释公式时，改写成读者能理解的自然语言；只有用户明确要求公式时才保留公式。默认模式同时禁止 `$$...$$`、`$...$`、`\\frac`、`\\hat`、`\\text{}` 等残留的 LaTeX 源码，不能让排版器把公式源码当普通正文输出。改写时要保留公式表达的比较、条件或因果关系，不能只删公式留下空洞；例如将两项奖励解释为“工具奖励检查调用是否合规，回答奖励检查最终回复是否满足目标”。无法确认符号含义时，回到论文定义核实，不自行猜解。
- 不把论文外的新闻、旧论文、模板素材或搜索结果混入正文。事实必须能追溯到论文、论文补充材料或明确标注的外部来源。

## 默认参数

```text
style = storytelling
include_code = false
include_formulas = false
publish_wechat = true  # 用户说“推送”时
theme = bytedance
author = Tau Lab
```

用户的明确要求优先于这些默认值。

## 工作流

### 1. 获取和冻结来源

1. 获取论文 HTML、PDF 或本地文件，记录标题、作者、日期、版本和原文链接。
2. 如论文提供公开代码，只在内部用于交叉核对；不要因为存在代码仓库就自动写代码分析。
3. 创建独立输出目录：

```text
outputs/paper-analyzer/{paper-slug}/
├─ work/          # 下载源文件、分析记录、审计结果
├─ images/        # 只放本论文的最终图片
├─ {paper-slug}.md
└─ wechat/{paper-slug}/
   ├─ article.html
   └─ preview.html
```

### 2. 选择论文图片

只从这篇论文的 HTML、PDF 或 arXiv source archive 提取图片。优先选择：

1. 方法框架图；
2. 问题或失败案例图；
3. 主要实验结果图；
4. 消融或泛化结果图。

图片规则：

- 最终文章通常使用 3–6 张图，全部保存到本文章目录的 `images/`。
- 不使用论文网页 logo、作者头像、机构 logo、装饰图、搜索结果图片或其他文章的图片。
- Markdown 只使用相对路径，例如 `images/figure1-framework.png`。
- 为每张图写清楚论文 Figure 编号或来源文件，并生成 `work/images-manifest.json`，记录源文件、尺寸和 SHA-256。
- 在排版前检查每个图片引用都能解析到本文章目录；图片数量和 manifest 必须一致。
- 如果 arXiv HTML 图片下载失败，优先从同一论文的 PDF/source archive 提取，不要用网络搜索图片替代。

### 3. 内部分析

内部回答以下问题，但不要把内部过程原样暴露给读者：

- 论文试图解决什么具体问题？
- 现有做法为什么会失败？
- 本文最关键的一个转变是什么？
- 方法从输入到输出经历了哪些步骤？每一步解决什么困难？
- 哪个实验最能支持主张？数字说明了什么，又没有说明什么？
- 作者承认的局限是什么？根据实验设计还能推断出哪些边界？

若查看代码，只把它当作“论文描述与公开实现是否一致”的内部证据。默认文章不提代码路径、函数、类、配置和测试。

### 4. 撰写 storytelling 文章

文章长度建议 2500–4000 个中文字符，至少 15 个自然段。按下列顺序组织：

1. **钩子**：从一个具体场景、反常识结果或读者熟悉的失败开始，不要第一句就堆术语。
2. **问题**：用一个简单例子解释旧方法为什么会把不同目标混在一起。
3. **核心洞察**：用一句人话说清论文真正改变了什么，再给一个贴切类比。
4. **方法**：按“怎么做 → 为什么这样做 → 与旧方法差在哪”展开，技术词出现后立即翻译成人话。
5. **实验**：选择最有说服力的结果，给表格和图，但必须解释结果含义；不要只罗列数字。
6. **边界**：区分作者明确承认的局限和基于实验设计的独立判断。
7. **收束**：回到开头的场景，给出一句读者可以复述的结论。

#### 标题先让读者看懂，再让读者想点开

标题是读者判断“这篇文章在讲什么”的第一条证据，也是点击前能看到的最短故事。不要直译论文标题，也不要把方法名、奖励名和抽象结论拼在一起。标题必须先交代一个**具体对象或场景**，再给出一个**反常结果、冲突或读者问题**；论文方法名放在副标题里，用一句人话解释它改变了什么。

标题有两个职责，不能互相替代：**主标题负责让人想点开，副标题负责让人知道论文做了什么**。主标题不用塞进全部技术细节，但必须让不读正文的人看懂“谁在什么场景里遇到了什么不对劲”；副标题必须把方法名翻译成动作或结果，不能只重复缩写。

标题生成固定走四步，不能跳过前两步直接写缩写：

1. **找出可视化的具体场景**：把论文中的抽象对象改成读者能想象的动作，例如“工具调用”“退款对话”“模型的最终回答”，不要只写“智能体能力”或“奖励设计”。
2. **找出真正的反常点**：写清楚什么地方对不上，例如“工具调用做错、回答却说对”“总分把两种行为混在一起”。反常点必须来自论文的案例、定义或实验，不能为了吸睛虚构失败。
3. **把冲突写成读者问题**：优先使用“为什么会……？”“到底奖励了什么？”“怎样分别判断……？”等句式，让读者在标题中就知道文章要解决的疑问。
4. **把方法降级为解释**：主标题先讲冲突，副标题再写 `SLCA-GRPO：分别评价工具是否用对、答案是否说对` 这类平实解释。缩写最多保留一个，第一次出现必须紧跟中文含义。

候选必须覆盖五种角度，避免只把同一个术语换五种说法：

- **冲突提问**：`具体动作做错、结果却正确：为什么会这样？`
- **反常结果**：`工具做错了却拿高分：训练到底奖励了什么？`
- **责任追问**：`工具和答案表现不一致：这次反馈该算给谁？`
- **读者场景**：`一次退款对话，为什么暴露出训练漏洞？`
- **方法承诺**：`怎样让工具执行和最终回答各自得到正确反馈？`

先生成 5 个候选标题，再用下面四项各打 0–2 分：读者能否看懂对象、冲突是否具体、是否忠于论文、是否有记忆点。任一项为 0 的候选不进入成稿；最高分相同则选更短、更少术语的一条。公众号主标题控制在约 18–30 个汉字，副标题控制在一行内。标题候选、评分、淘汰原因和最终选择写入 `work/title-candidates.md`，但不要把候选列表放进文章正文。

标题必须通过下面的五秒测试：读者只看主标题，能说出研究对象；能指出发生了什么冲突；能猜到文章会回答一个什么问题。若只能看出“这是一篇讲 AI 的文章”，就退回重写。吸引力来自**具体反差和未解决的问题**，不能来自夸大、恐吓或制造论文没有报告的结果。

推荐句式（按论文事实改写，不要机械套用）：

- `工具调用做错、回答说对：AI 训练到底该给谁打分？`
- `工具做错了却拿高分：AI 训练到底奖励了什么？`
- `同一条回答两种表现，工具和总结该怎样分别评价？`

下面这些词不能单独承担主标题的含义：**错奖、分开两类反馈、跨片段信用分配、奖励路由、结构性故障**。它们可以在正文中作为术语，或在副标题中紧跟具体解释；不能让读者看到标题后还要猜“谁做错了、错在哪里”。“一个意外的发现”“重新思考智能体”“别让总结替工具调用背锅”也只能作为导语或小标题，不能替代对象和冲突。选中的主标题必须让读者脱离正文也能回答“研究对象是什么、发生了什么问题”，并至少回答“论文改变了哪一环”的一部分。

标题中的强词要有证据门槛：论文只展示“可能混淆”时，不能写成“必然失败”；论文没有报告“拿高分”时，不能凭感觉写“做错却得高分”；论文没有比较“更快/更强”时，不能把方法写成性能承诺。遇到术语时，优先做下面的白话转换，再决定它是否需要出现在副标题：

| 论文术语 | 标题可用的白话 | 不应直接使用的写法 |
|---|---|---|
| credit assignment | 哪一段行为该得到哪一份反馈 | 跨片段信用分配 |
| reward misattribution | 反馈算错了对象 / 总分把两种表现混在一起 | 错奖 |
| separate rewards | 工具执行和最终回答分别评价 | 分开两类反馈 |
| token-level routing | 让反馈只更新对应的生成片段 | 奖励路由 |

最终文章只保留一个主标题和一个副标题。禁止把论文原题、候选标题、方法缩写标题同时堆在开头；也禁止为了点击把结论写成问题后，正文却没有回答这个问题。

#### 每张图都要在正文里完成解读

图片不是段落的终点。每一张最终保留的图，按以下顺序嵌入正文：

1. **引入问题**：在图片前用一两句说明读者此刻要看什么，以及它和上一段的关系。
2. **图注定位**：图注写明论文 Figure 编号、图展示的对象和读者应关注的维度；不要只写“论文 Figure 3”。
3. **自然解读**：图片和图注之后紧跟 2–4 句正文。至少说出一个可观察关系（趋势、差距、流程分工、正反案例或组件变化），再把它翻译成对主线有用的含义。不要只复述坐标轴和图例。
4. **证据边界**：在同一段或下一句说明这张图支持到哪里，不能推出什么，例如代表性运行不能替代多随机种子显著性、相关变化不能直接证明因果、单一基准不能代表所有任务。

这是硬性闭环：图片之后、下一个标题之前必须有这段自然解读；不能让图成为段落终点，也不能把分析只放在图片之前。若相邻的多个面板作为一张组合图呈现，可以合并解读，但要明确比较面板及其关系。表格同样需要在表后解释最重要的比较及其适用范围。

不同图形按不同问题来读：

| 图形 | 正文要回答的问题 | 合格的解读方向 |
|---|---|---|
| 方法框架图 | 信息从哪里来，经过哪些环节，最后反馈到哪里？ | 沿箭头讲输入、交互、评价和输出，指出责任边界或信息流向 |
| 失败/案例图 | 两种行为怎样产生不同结果？ | 对照正反案例，说明哪一步错、哪一步仍然正确，以及统一评分为何会误判 |
| 折线图 | 训练或测试过程中什么在上升、下降或分叉？ | 指出起点、拐点、最终差距或稳定区间，并解释它与主张的关系 |
| 柱状图/表格 | 哪些模型、任务或设置之间有稳定差异？ | 选关键比较，报告清晰可读的数值或百分点差，再说明范围和限制 |
| 消融图 | 去掉哪个组件后损失最大，说明了什么？ | 先比较变化，再说明它支持“组件有用”到什么程度；不要把一次消融写成独立因果证明 |

图表解读必须来自论文图、图注、正文或表格。看不清的数值不要猜；需要精确数字时回到论文原始表格核对。不要把“曲线更高”写成“必然更好”，也不要把“同时上升”写成“因此导致”。

正文中要让读者分清证据来自哪里：用“论文报告”介绍作者给出的结论，用“图中可以看到”描述直接可见的关系，用“这提示/这可能说明”标出作者没有直接验证的推断，并紧接着限定范围。图注只负责说明图号、对象和来源，不能代替正文解读；不要用“如图所示”或“图表分析：”充当分析本身。

写作要求：

- 多用“你有没有想过”“换个场景看”等自然的读者对话，但不要过度口语化。
- 每段 2–4 句，避免连续大段定义、公式或术语。
- 至少使用 2 个自然类比，至少引用 3 处论文中的关键表述或结论（用中文转述或短引用）。
- 标题下的作者、论文、数据等元信息必须分行呈现，每项单独一行；元信息结束后加 `---` 分隔线和留白，再开始正文。禁止用一个长段落把作者、论文和数据挤在同一行。
- 必须把内容写成可视化层级：至少 5 个 `##` 章节、至少 3 个 `###` 子标题；实验维度和局限使用 Markdown 列表，方法步骤按下一条规则处理。
- 方法若有“第一步/第二步/第三步”等明显顺序，必须在同一处写成一组连续有序列表（`1.`、`2.`、`3.`），每项都包含步骤名称和完整解释。不要把第一步单独做成 `###`、把第二三步留在普通段落里，也不要在后面再重复一组同义步骤清单。
- 至少保留 2 个论文原句或短语作为 `>` 引用块，并在引用后标明“论文摘要”“论文方法概述”或对应来源；引用总长度保持克制。
- 每个主要章节至少有一处有意义的判断、发现或关键术语加粗；整篇应有稳定但克制的强调节奏。直接加粗观点本身，禁止写 `**关键句：**`、`**重点：**` 这类解释性标签，也不要整段加粗。
- 表格只呈现读者真正需要比较的数据；表格后必须有解释段落。
- 每张入选图都必须有“前文引入 + 图注定位 + 图后 2–4 句自然解读 + 证据边界”；不能只放图，也不能用“图表分析：”作为机械标签。
- 图后解读的首句说清直接观察到的结构、对照或趋势，随后说明它如何回答当前问题；必要时再用一句话限定证据边界。不要让读者在图后还要猜这张图为什么出现。
- 图前后正文要回答“看到什么、意味着什么、不能说明什么”，让读者不看图注也能理解图在故事中的作用。
- 不得只写“如图所示”并复述图注；框架图不是实验结果，示意图不能被写成量化证据；图中没有明确标注的精确数值不得臆测。
- 解读时区分“论文报告”“图中可见”和“本文推断”；推断必须带适用范围或限制，不能把相关变化写成必然因果。
- 公式若需转述，必须把符号关系译成具体语义；默认正文不得残留数学源码、孤立变量或公式片段。
- 结尾保留：`:::end[💡 实时了解更多AI论文，关注 Tau Lab]`。

### 5. 正文禁写检查

在生成 Markdown 后执行检查。默认文章必须满足：

- 不含围栏代码块；
- 不含 `core_algos.py`、`reward_fn.py`、函数名、行号、命令行和源码路径；
- 不含“代码已公开”“仓库提供测试”“实现位于”等实现说明；
- 不含裸的 `$$...$$`、`$...$`、LaTeX 命令或公式分隔符；
- 图片引用全部以 `images/` 开头，并且文件存在；
- 至少包含 1 个表格、3 张论文图片、1 个局限段落和 1 个收束金句。
- 作者/论文/数据元信息逐行且其后有分隔线；若存在三步法，三步只出现为同一组有序列表；关键句直接加粗，不出现“关键句”提示标签。

发现违规时，先改写正文再排版，不要把违规内容交给 formatter 让它“自动处理”。

使用结构校验器作为硬门槛：

```powershell
python scripts/validate_storytelling.py `
  "{paper-slug}.md"
```

排版生成 `article.html` 后，再带 `--html` 参数校验一次；Markdown 和 HTML 两次都必须返回 `"ok": true` 才能交付：

```powershell
python scripts/validate_storytelling.py `
  "{paper-slug}.md" `
  --html "outputs/wechat-format\{paper-slug}\article.html"
```

### 6. 微信排版

使用本仓库内置的 Paper2WeChat 排版阶段：

```powershell
python scripts/format.py `
  --input "{paper-slug}.md" `
  --theme bytedance `
  --output "outputs/wechat-format" `
  --no-open `
  --format wechat
```

排版后必须检查：

- `preview.html` 是给人看的完整预览，包含标题、正文、表格、图片和结尾；
- `article.html` 是复制到公众号的正文 HTML；
- 两个文件都包含可见正文文本，不得只有图片；
- HTML 中不得出现 `$$`、成对 `$` 或 LaTeX 命令；公式残留时必须回到 Markdown 改写后重新排版，不能直接推送；
- 图片数量与 Markdown 一致，图片路径全部来自本文章 `images/`；
- 元信息在 HTML 中仍分行，方法步骤渲染成数字圆点 1、2、3，不能丢编号或出现重复步骤标题；
- 原句引用显示为独立青色引用卡片，正文重点显示为蓝色粗体；
- 不把 `debug_wechat.html` 当预览或交付文件。

`bytedance` 主题按参考公众号文章的正文视觉执行：

- 预览正文使用约 645px 的窄栏，不套手机壳宽度；桌面页面居中，移动端再自适应收窄。
- 正文约 17px，行距约 2.0，段落之间保留明显呼吸；正文颜色使用蓝灰色，避免整篇黑字挤成一团。
- 一级标题保留蓝色上边线和青色下边线；章节标题使用蓝到青的渐变胶囊，白色居中粗体。
- 关键句用亮蓝色粗体；引用使用浅蓝背景、青色左边框和较宽内边距；无序列表使用青色圆点，有序列表使用蓝色数字圆点。
- 论文图片居中、圆角、带轻微阴影；图片说明使用青绿色斜体，与正文保持清晰间距。
- `preview.html` 的视觉壳只服务于检查，不改变 `article.html` 中的内联微信样式；两者都必须保留完整正文。

### 7. 推送草稿

用户明确说“推送”时，推送到公众号草稿箱，不代表直接发布。封面使用本论文第一张最终图片，不生成额外的网络图片：

```powershell
python scripts/publish.py `
  --dir "outputs/wechat-format\{paper-slug}" `
  --cover "images\figure1.png" `
  --title "{不超过 30 字的标题}" `
  --author "Tau Lab" `
  --source-url "{paper-url}" `
  --yes
```

发布脚本默认不生成调试 HTML。只有排查图片上传问题时才显式添加 `--save-debug`；该文件只用于内部审计，不应打开给用户阅读，也不应作为公众号正文。

推送后报告：标题、作者、主题、图片数量、留言状态、草稿是否成功，以及本地预览文件路径。不要输出 app secret、access token 或其他密钥。

## 交付前硬检查

```text
[ ] 文章是 storytelling，而不是代码审查
[ ] 默认正文没有代码、源码路径、函数名、命令和裸公式
[ ] 只使用本论文图片，图片 manifest 与引用一致
[ ] preview.html 和 article.html 都有完整可见正文
[ ] debug_wechat.html 未被当作预览或正文
[ ] 标题长度适合公众号展示
[ ] 如用户要求推送，草稿 media_id 已返回或明确报告失败原因
```

## 可选模式

只有用户明确要求时才切换：

- **代码分析模式**：允许源码路径、函数、配置和复现说明，并在标题或小节中明确标识“实现分析”。
- **公式模式**：允许 KaTeX 公式，但每个公式后必须有自然语言解释。
- **学术模式**：增加方法定义、公式和更密集的实验表格，但仍遵守图片来源和证据边界。

不要因为论文提供代码或公式就自动启用这些模式。

---

## Integrated WeChat formatting and draft publishing

Paper2WeChat is one skill with one user-facing workflow. Use the formatter and publisher scripts as internal stages; do not ask the user to install a second formatter skill.

### Format a validated article

Before formatting, run the Chinese punctuation check and fix violations on the article Markdown:

```powershell
python scripts/zh_punctuation_fix.py "outputs/paper-analyzer/{paper-slug}/{paper-slug}.md" --write
```

Then create a WeChat article and preview using a selected theme:

```powershell
python scripts/format.py --input "outputs/paper-analyzer/{paper-slug}/{paper-slug}.md" --theme bytedance --no-open
```

To open the gallery and compare its curated theme set using the real article, pass `--gallery`; all 85 JSON themes remain selectable directly with `--theme`. The output is stored below `outputs/wechat-format/` by default. Preserve the paper article's `images/` directory and its `work/images-manifest.json`; never add a page logo, avatar, image from another paper, or decorative search result.

The formatter retains inline WeChat-compatible HTML, standard HTML and plain output; Obsidian wikilinks and Markdown images; footnotes for external links; callouts; dialogue, gallery, long-image, intro, end, history and video containers; quotation cards; heading decorators; configurable themes; smart semantic enhancement; and font sizing. Its helper scripts include Chinese punctuation checking and LaTeX-to-image conversion.

After the article is drafted from the paper and the source images are verified, use the unified runner for punctuation repair, validation, formatting, and optional publishing:

~~~powershell
python scripts/paper2wechat.py --input "outputs/paper-analyzer/{paper-slug}/{paper-slug}.md" --output "outputs/wechat-format" --theme bytedance --source-url "{paper-url}"
~~~

Add --push only when the user explicitly asks to create a WeChat draft. Use --dry-run only when they request a publishing test; this may upload article images to the WeChat media library while skipping draft creation. The unified runner covers the post-analysis stages; it does not replace reading the paper or writing the evidence-grounded article.

### Verify before any draft push

Run the storytelling validator on the Markdown and then on the rendered article HTML. Both checks must report `"ok": true`. Confirm each article image is inside the current paper's own `images/` folder and matches `work/images-manifest.json` by path and SHA-256.

Only when the user explicitly asks to push, run the publisher. A dry-run performs article validation and may upload images to the WeChat media library, but it never creates a draft. Draft creation requires a non-dry-run invocation and explicit confirmation (`--yes` for non-interactive use). Never call the publisher as an implicit step.

```powershell
python scripts/publish.py --dir "outputs/wechat-format/{paper-slug}" --cover "images/figure1.png" --title "{chosen-title}" --author "Tau Lab" --source-url "{paper-url}" --yes
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

```bash
python scripts/zh_punctuation_fix.py "文章路径.md" --write
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

```bash
python scripts/format.py \
  --input "文章路径.md" \
  --gallery \
  --recommend newspaper magazine ink
```

这会用用户的**真实文章**渲染 34 个精选主题（完整主题库共 85 个），在浏览器打开画廊页面。用户点按钮切换主题预览，选中后点「用这个风格排版」一键复制到剪贴板。

#### 第 3 步（备选）：直接指定主题排版

如果用户已经知道想用哪个主题，可以跳过画廊直接排版：

```bash
python scripts/format.py \
  --input "文章路径.md" \
  --theme terracotta
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

```powershell
python scripts/publish.py `
  --dir "wechat\\{paper-slug}" `
  --cover "images\\figure1.png" `
  --title "文章标题" `
  --author "Tau Lab" `
  --source-url "论文原文链接" `
  --yes
```

推送前必须完成 Markdown 和 HTML 两次结构校验；默认推送脚本还会拒绝 `$$...$$`、`$...$` 和 LaTeX 命令残留，只有明确公式模式才传 `--allow-formulas`。推送后报告标题、作者、正文图片数量、留言状态、草稿是否成功和本地预览路径；不得输出 app secret、access token 或其他密钥。配置中的“请填写……”等合集占位符按未配置处理，只有有效 `--album-id` 才绑定合集。

---

## Obsidian 排版工具箱（写作时主动使用，写作 SKILL 共享参考）

### 三条硬规则（高于一切）

1. **形态决定形式**：写之前不预设排版结构。一段一段写，写到哪段问"这段内容本质是什么形态（清单/对比/流程/故事/数据/引用/关系）"，再选最契合的元素。**禁止**先决定"这篇要有 N 个 bullet list、N 个 callout"再去找内容塞
2. **反炫技自检**：每加一个 callout/高亮/表格/特殊容器，问"去掉它读者损失什么"。答不上来 → 删
3. **密度交替**：连续 3 段不许同结构。长段后接短段，列表后接散文，密集元素后留呼吸位

**⚠️ `:::xxx` 容器特殊规则**：`:::byline / :::stat / :::gallery / :::longimage / :::dialogue` 仅 Paper2WeChat formatter 排版转换时识别。Obsidian 原生预览 / 本地 preview.py / 其他 Markdown 阅读器**不渲染**，会裸字显示 `:::byline[小互说]` / `:::`。**只在公众号最终稿用**，且必须经 format.py 转换后再发布。能用 H2 / callout / blockquote 替代的尽量替代。

### 内容形态 → 元素选择决策表

带 ⚡ 的元素经 Paper2WeChat formatter 转换后在公众号显示美观；不带的是公众号原生支持。

| 内容形态 | 推荐元素 | 公众号 | 不要用 |
|---------|---------|----------|-------|
| ≥3 项**并列要点**（无先后） | 无序列表 `-` | 原生 | 各项有强对比→改表格；只有 2 项→写成句子 |
| **有先后/因果/步骤** | 有序列表 `1. 2. 3.` 或动词式标题 | 原生 | 步骤 ≤2→写句子 |
| **教程操作清单** | 任务列表 `- [ ]` | ⚠️ 公众号勾选框不渲染 | 非操作类别用 |
| **场景化举例**（"假设你..."） | 引用块 `>` | 原生 | 不要每段都套 |
| **引用原话/CEO 表态** | 引用块 `>` + `> — 来源` | 原生 | 没真出处别用 |
| **多人对话/访谈** | `:::dialogue` ⚡ | 转 HTML | 独白别套 |
| **关键判断/反直觉结论** | `> [!important]` ⚡ | 转色块 | 全文 ≤2 处 |
| **小技巧/巧妙用法** | `> [!tip]` ⚡ | 转色块 | 一篇 ≤1 个 |
| **风险/已知坑/局限** | bullet list 默认；`> [!warning]` ⚡ 只留给单条高危 | 列表原生 / callout 转色块 | warning 一篇 ≤1 处 |
| **背景补充/扩展** | `> [!note]` ⚡ | 转色块 | 跟主线无关考虑直接删 |
| **2+ 选项参数对照** | 表格 | 原生（最多 4 列） | 只 2 项弱对比写句子 |
| **可复制命令/代码** | ``` 代码块 + 语言 | ⚠️ 公众号无语法高亮 | 截图代码（绝对不行） |
| **核心数据/百分比** | `==高亮==` ⚡ | 转 `<mark>` | 全文 ≤5 处 |
| **文章级大数字** | `:::stat` ⚡ | 转大字块 | 全文 ≤1 个 |
| **段落关键词** | `**加粗**` | 原生 | 不能整句加粗、每段 ≤2 处 |
| **反差句式** | `~~X~~ Y` 删除线 | 原生 | 一篇 ≤2 次 |
| **连续 ≥3 图** | `:::gallery` ⚡ | 转横滑 | ≤2 图直接 `![]()` |
| **超长流程图/架构图** | `:::longimage` ⚡ | 转固定高度纵滑 | 普通图别用 |
| **作者点睛收尾**（小互说） | `:::byline[小互说]` ⚡ | 转署名块 | 一篇 ≤1 处 |
| **章节切换** | `## 标题` 或 `---` 分隔线 | 原生 | 短文（<800 字）连续叙述别切 |

### 小标题前缀变体池

| 前缀样式 | 适合场景 | 例 |
|---------|---------|----|
| **裸标题（无前缀）** | 章节本身有完整名词，散文式叙述 | `## 这事为什么重要` |
| `①②③④⑤⑥` 圆圈数字 | 严肃技术分点；**一篇至多用一处** | `### ① 流式 LoD` |
| `1. 2. 3.` 阿拉伯 | 步骤、操作 | `1. 抓取 2. 写初稿 3. 扫描` |
| `一、二、三、` 中文序号 | 偏正式、报告感、深度解读 | `## 一、问题的根源` |
| **动词+名词式**（坑一/招一/症状一） | 病症清单、避坑指南 | `## 坑一：偷改测试` |
| **emoji 前缀**（🚨⚠️🔥💡🎯） | 警示、亮点；**不滥用** | `## 🚨 最严重的那条` |
| **疑问句标题** | 痛点引入 | `## 数字里到底藏着什么` |
| **数字式断言**（"3 个核心""6 个关键变化"） | 强观点、列举式 | `## 这项方法的三个关键变化` |

**选择规则**：① 一篇文章只用 1-2 种前缀样式，**绝对禁止**全篇 6 个章节都用 `①②③④⑤⑥`；② 严肃技术 → 圆圈/中文序号；吐槽/避坑 → 动词式或 emoji；对比陈述 → 裸标题；③ 同一篇上下章节交替

### 反炫技自检（写完通读）

- callout 总数 > 4 → 砍
- 高亮 > 5 处 → 砍
- 表格能改成 2-3 句话讲完？能 → 改
- emoji 标题 > 3 → 砍
- 6 个连续章节都用 `①②③④⑤⑥` → **必须改**
- 跟上一篇文章对比：开头方式/章节切法/收尾方式雷同？有 → 换

### 元素使用边界

- callout 是重武器：tip / important / warning / note 全文 ≤ 4 个
- 高亮 ≤ 5 处：满屏黄色就是没重点
- 加粗 ≤ 每段 2 处：是"扫读视觉锚点"，不是"我觉得这很重要"
- 任务列表只用于操作清单
- 引用块不要嵌套引用块
- 表格不超过 4 列（移动端撑爆）
- 代码块必须带语言标签

### 反模式

- ❌ 整段加粗代替结构 → 拆成无序列表
- ❌ callout 套娃 → 5 个 important 等于没有
- ❌ 罗列式短句 → 3 个 4 字 bullet 直接写段落更好
- ❌ 表格只有 2 行 → 信息密度低，写两段更省地方
- ❌ 截图代码 → 所有命令和代码用代码块

**不能用的**：Mermaid 图表（微信不支持 JS）

### Obsidian 进阶语法（知识库档案/长文收纳）

**完整 callout 13 种**：note / info / abstract / tip / success / question / warning / failure / danger / bug / example / quote / todo

**折叠 callout**：`> [!faq]-` 默认收起，`> [!example]+` 默认展开。

**wikilink 完整**：`[[Note]]` / `[[Note|显示文字]]` / `[[Note#标题]]` / `[[Note#^block-id]]` / `[[#标题]]`

**图片尺寸**：`![[image.png|640]]` 或 `![[image.png|640x480]]`

完整 Obsidian 语法字典：`知识库/写作参考/obsidian-语法字典.md`

**克制原则**：上面这些规则是"什么时候**该**用"，不是"什么时候**必须**用"。每篇文章用 3-5 类元素就够丰富了。
- 画廊模式渲染 34 个精选主题（完整主题库共 85 个），用的是用户的真实文章
