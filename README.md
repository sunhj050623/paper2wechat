# Paper2WeChat

Paper2WeChat is one installable skill for turning an academic paper URL or PDF into a source-grounded Chinese article, a WeChat-ready preview, and—only when explicitly requested—a draft in the WeChat Official Account backend.

The repository combines the paper-analysis workflow, Markdown formatter, 85 theme files, HTML gallery and preview templates, punctuation and LaTeX helpers, and draft publisher. The root SKILL.md is the single user-facing entry point.

## Workflow

1. Start from an arXiv URL, paper URL, PDF, or local paper. Read the source and record title, authors, date/version, and URL.
2. Extract only this paper's figures. Store them below that paper's images/ directory and verify work/images-manifest.json; do not use logos, avatars, search images, or images from another paper.
3. Write and validate a reader-facing Chinese article. The default is storytelling; code analysis and formulas are opt-in.
4. Fix Chinese punctuation, select a theme or open the theme gallery, and generate article.html and preview.html.
5. Validate the rendered HTML and image paths. Call the publisher only when the user explicitly asks to push a draft.

## Install as a single Codex skill

Copy or clone this repository into the Codex skills directory as paper2wechat, then restart or refresh Codex skills:

~~~powershell
git clone <repository-url> "$HOME/.codex/skills/paper2wechat"
~~~

If you already have the repository locally, use its folder as the skill folder. There is no second formatter skill to install.

## Requirements

- Python 3.8 or newer.
- Install runtime dependencies with python -m pip install -e .
- For tests, install `python -m pip install -e ".[test]"`, then run `python -m pytest -q`.
- WeChat credentials are only needed to upload media or create a draft.

## Configuration

Copy config.example.json to a root-level config.json. The local file is ignored by Git. Analysis and formatting do not require credentials.

Set secrets in the environment when possible:

~~~powershell
$env:WECHAT_APP_ID = "your-app-id"
$env:WECHAT_APP_SECRET = "your-app-secret"
$env:SMART_FORMAT_API_KEY = "your-api-key"
~~~

Sensitive environment variables override local values. Supported names include WECHAT_APP_ID, WECHAT_APP_SECRET, SMART_FORMAT_API_KEY, SMART_API_KEY, OPENAI_API_KEY, and AI_API_KEY. The smart-format API key is only used when --smart is requested.

## Format and preview

Run commands from the repository root:

~~~powershell
python scripts/zh_punctuation_fix.py "outputs/paper-analyzer/<paper-slug>/<paper-slug>.md" --write
python scripts/format.py --input "outputs/paper-analyzer/<paper-slug>/<paper-slug>.md" --theme bytedance --no-open
~~~

The formatter preserves its CLI options: --input, --theme, --vault-root, --output, --no-open, --gallery, --recommend, --format {wechat,html,plain}, --smart, and --font-size. Use --gallery to compare the curated set; all 85 themes can be selected directly with --theme. Generated formatter files go to outputs/wechat-format/ by default.

## Validate and push a draft

Both Markdown and rendered HTML checks must pass before a push:

~~~powershell
python scripts/validate_storytelling.py "outputs/paper-analyzer/<paper-slug>/<paper-slug>.md"
python scripts/validate_storytelling.py "outputs/paper-analyzer/<paper-slug>/<paper-slug>.md" --html "outputs/wechat-format/<paper-slug>/article.html"
~~~

An explicit dry-run can upload images to the WeChat media library, but it never creates a draft:

~~~powershell
python scripts/publish.py --dir "outputs/wechat-format/<paper-slug>" --cover "images/figure1.png" --title "<title>" --author "Tau Lab" --source-url "<paper-url>" --dry-run
~~~

Create a draft only after the user explicitly asks for a push:

~~~powershell
python scripts/publish.py --dir "outputs/wechat-format/<paper-slug>" --cover "images/figure1.png" --title "<title>" --author "Tau Lab" --source-url "<paper-url>" --yes
~~~

The publisher retains --dir/--input, --cover, --title, --theme, --author, --source-url, --dry-run, --save-debug, --allow-formulas, --yes, and --album-id. It uploads only images inside the current article directory and refuses remote or traversal image paths. A successful command reports draft creation; an upload or local build alone is not a created draft.

## Run checks

~~~powershell
python -m pytest -q
python scripts/format.py --help
python scripts/publish.py --help
python scripts/latex2img.py --help
~~~

## Repository safety

config.json, environment files, generated outputs/, debug HTML, local caches, and Python bytecode are ignored. Do not add account credentials, generated paper articles, or paper images to commits.
