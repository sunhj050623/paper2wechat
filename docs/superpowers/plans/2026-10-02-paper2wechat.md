# Paper2WeChat Unified Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** 将现有 paper-analyzer 与 xiaohu-wechat-format 的能力合并为一个可公开发布、路径可移植且从论文链接生成公众号草稿的 paper2wechat Skill 仓库。

**Architecture:** 仓库根目录的 SKILL.md 是唯一用户入口。论文抓取、图片审计、故事化写作校验、Markdown 排版、主题资源、HTML 预览和微信公众号草稿上传均通过仓库相对路径组织。保留原脚本 CLI，同时增加统一编排 CLI；配置通过根目录 config.json 与环境变量读取，敏感环境变量优先，所有日志与调试产物脱敏。

**Tech Stack:** Python 3.10+, markdown, requests, Pillow（按现有脚本实际依赖），标准库 pathlib/hashlib/json/re/argparse，pytest，HTML/CSS，Git。

**Spec:** docs/superpowers/specs/2026-10-02-paper2wechat-design.md

## Global Constraints

- 单一仓库名和 Skill 名称为 paper2wechat，产品文案中不再使用 xiaohu-wechat。
- 保留论文分析器的五种写作风格、图片下载/manifest/HTML/结构校验、标题候选、图片闭环和公式/代码禁写规则。
- 保留格式器的全部 85 个主题 JSON、gallery.html、preview.html、WeChat 内联样式、wikilink/Markdown 图片、callout、dialogue/gallery/longimage、视频卡片、标点修复、LaTeX 图片辅助和原 CLI 选项。
- 保留发布器的封面、作者、来源链接、合集 ID、dry-run、确认、调试 HTML、公式门控和草稿箱行为；dry-run 可上传素材但不得创建草稿。
- 路径不得依赖 C:\Users\...、~/.codex/skills/... 或个人目录；生成内容只能进入 outputs/。
- config.json、API key、access token、Python cache、临时文件、文章输出和调试材料必须被 Git 忽略；仓库只提供不含密钥的 config.example.json。
- WECHAT_APP_ID、WECHAT_APP_SECRET 和智能排版 API key 等敏感环境变量优先于本地配置；任何日志、错误、dry-run 和调试输出不得回显密钥。
- 未显式请求 --push/“推送”时只生成分析、排版和本地预览。
- 不复制历史文章、用户本地配置或其他论文图片；最终图片只能来自当前论文来源并通过 manifest 审计。

---

### Task 1: 建立可发布仓库骨架和安全边界

**Files:**
- Create: SKILL.md, README.md, pyproject.toml, config.example.json, .gitignore
- Create: scripts/__init__.py, scripts/paths.py
- Test: tests/test_repository_contract.py

**Interfaces:**
- scripts.paths.REPO_ROOT: pathlib.Path
- resolve_repo_path(*parts) -> pathlib.Path
- output_root() -> pathlib.Path
- local_config_path() -> pathlib.Path
- ensure_output_dir(slug: str) -> pathlib.Path

- [ ] **Step 1: Write failing contract tests**

    from pathlib import Path
    from scripts.paths import REPO_ROOT, resolve_repo_path

    def test_repo_root_is_portable():
        assert (REPO_ROOT / "SKILL.md").is_file()
        assert "paper2wechat" in REPO_ROOT.name

    def test_resolve_repo_path_stays_inside_repo():
        candidate = resolve_repo_path("themes", "bytedance.json")
        assert candidate.is_relative_to(REPO_ROOT)

- [ ] **Step 2: Run the tests and verify they fail**

    python -m pytest tests/test_repository_contract.py -q

    Expected: FAIL because the repository modules and metadata do not exist.

- [ ] **Step 3: Implement the skeleton and path module**

    Use Path(__file__).resolve().parents[1] as REPO_ROOT. Reject path escapes in resolve_repo_path. Add ignores for config.json, outputs/, .pytest_cache/, __pycache__/, *.pyc, .env, debug/, and tokens. Keep config.example.json placeholder-only.

- [ ] **Step 4: Run the tests and verify they pass**

    python -m pytest tests/test_repository_contract.py -q

- [ ] **Step 5: Commit**

    git add SKILL.md README.md pyproject.toml config.example.json .gitignore scripts tests
    git commit -m "chore: scaffold paper2wechat repository"

### Task 2: Port paper analysis assets and portable image provenance

**Files:**
- Create: scripts/download_paper_images.py, scripts/extract_paper_info.py, scripts/generate_html.py, scripts/validate_storytelling.py
- Create: styles/academic.md, styles/concise.md, styles/storytelling.md, styles/with-code.md, styles/with-formulas.md
- Create: cover-prompt.md, cover-prompt-simple.txt
- Test: tests/test_paper_assets.py

**Interfaces:**
- Preserve each existing paper-analyzer script CLI.
- download_paper_images emits work/images-manifest.json with source, dimensions, and SHA-256.
- generate_html resolves images relative to the current article directory.
- validate_storytelling returns JSON with ok true for valid Markdown and HTML.

- [ ] **Step 1: Copy source files only**

    Copy the listed sources from the installed paper-analyzer. Exclude __pycache__, .pyc, generated outputs, and absolute local paths.

- [ ] **Step 2: Write failing manifest tests**

    Create a temporary paper directory containing images/figure1.png, run the manifest helper, and assert that the result uses images/figure1.png, includes SHA-256, accepts that path, and rejects ../other/figure.png.

- [ ] **Step 3: Implement source restriction and path checks**

    Restrict image selection to the current paper HTML/PDF/source archive. Normalize manifest paths to forward-slash relative paths, compute SHA-256, reject images outside the article directory, and make HTML generation use the article root.

- [ ] **Step 4: Run the tests**

    python -m pytest tests/test_paper_assets.py -q

    Expected: PASS, including a test that an arXiv logo or unrelated image is never copied.

- [ ] **Step 5: Commit**

    git add scripts styles cover-prompt.md cover-prompt-simple.txt tests
    git commit -m "feat: port paper analysis and image provenance tools"

### Task 3: Preserve the complete formatter theme catalog

**Files:**
- Create: themes/*.json for all 85 source themes
- Create: templates/gallery.html, templates/preview.html
- Create: tests/fixtures/theme-inventory.json
- Test: tests/test_theme_inventory.py

- [ ] **Step 1: Snapshot the source inventory**

    Record the sorted source theme filenames and SHA-256 values in tests/fixtures/theme-inventory.json. The expected count is 85 JSON files and two HTML templates.

- [ ] **Step 2: Write the inventory test**

    Parameterize over the inventory, assert the actual theme filename list is identical, assert len(actual) == 85, assert both templates exist, and parse every theme as JSON.

- [ ] **Step 3: Copy and audit all resources**

    Copy every source theme and both templates. Rewrite only absolute paths and old product labels; preserve schemas, decorators, three-layer heading fields, and display-type lint exceptions.

- [ ] **Step 4: Run tests**

    python -m pytest tests/test_theme_inventory.py -q

- [ ] **Step 5: Commit**

    git add themes templates tests/fixtures tests/test_theme_inventory.py
    git commit -m "feat: preserve complete formatter theme catalog"

### Task 4: Refactor formatter, punctuation, LaTeX, and config safely

**Files:**
- Create: scripts/format.py, scripts/zh_punctuation_fix.py, scripts/latex2img.py, scripts/config.py
- Modify: scripts/paths.py
- Test: tests/test_formatter_cli.py, tests/test_config_security.py

**Interfaces:**
- Preserve --input/-i, --theme/-t, --vault-root, --output/-o, --no-open, --gallery, --recommend, --format {wechat,html,plain}, --smart, --font-size.
- Preserve punctuation check/write modes and the LaTeX helper CLI.
- load_config() -> dict merges defaults and local non-sensitive config, then applies sensitive environment overrides.
- redact(value: str) -> str removes secrets from diagnostics.

- [ ] **Step 1: Write failing CLI and config tests**

    Run scripts/format.py --help and assert every legacy option is present. Set WECHAT_APP_ID to a test value and assert it overrides local config. Pass a test secret to redact and assert the returned diagnostics do not contain it.

- [ ] **Step 2: Run tests to verify failure**

    python -m pytest tests/test_formatter_cli.py tests/test_config_security.py -q

- [ ] **Step 3: Port and refactor formatter**

    Resolve themes/templates through scripts.paths, load configuration through scripts.config, preserve all Markdown/Obsidian/HTML transformations, and replace user-facing xiaohu branding with paper2wechat.

- [ ] **Step 4: Implement redaction and precedence**

    Treat placeholder values such as 请填写 as unset. Never print the loaded config wholesale. Apply environment precedence only to sensitive fields and redact exception, debug, and dry-run output.

- [ ] **Step 5: Run and commit**

    python -m pytest tests/test_formatter_cli.py tests/test_config_security.py -q
    git add scripts tests
    git commit -m "feat: make formatter portable and secret-safe"

### Task 5: Refactor publisher and preserve draft semantics

**Files:**
- Create: scripts/publish.py
- Modify: scripts/config.py
- Test: tests/test_publisher_cli.py, tests/test_publish_safety.py

**Interfaces:**
- Preserve --dir|--input, --cover, --title, --theme, --author, --source-url, --dry-run, --save-debug, --allow-formulas, --yes, --album-id.
- publish_article(article_dir, cover, metadata, *, dry_run=False, allow_formulas=False) -> PublishResult.
- PublishResult exposes created_draft, uploaded_media_count, article_title, and redacted diagnostics.

- [ ] **Step 1: Write failing publisher tests**

    Mock create_draft and assert dry_run leaves created_draft false and never calls it. Give an article residual $$...$$ and assert publishing raises a message requiring --allow-formulas.

- [ ] **Step 2: Run tests to verify failure**

    python -m pytest tests/test_publisher_cli.py tests/test_publish_safety.py -q

- [ ] **Step 3: Port publisher logic and isolate side effects**

    Preserve upload order and WeChat API behavior. Resolve cover and article images only inside the article directory. Make dry-run validate and optionally upload media without draft creation; require --yes for non-interactive draft creation.

- [ ] **Step 4: Add formula and secret safety**

    Reject residual LaTeX unless --allow-formulas is supplied. Route API errors through redact and sanitize --save-debug output.

- [ ] **Step 5: Run and commit**

    python -m pytest tests/test_publisher_cli.py tests/test_publish_safety.py -q
    git add scripts tests
    git commit -m "feat: preserve safe WeChat draft publishing"

### Task 6: Add the single paper-to-draft orchestrator

**Files:**
- Create: scripts/paper2wechat.py
- Modify: SKILL.md, README.md
- Test: tests/test_pipeline_cli.py

**Interfaces:**
- CLI accepts arXiv URL, paper URL, PDF path, or local Markdown plus --output, --style, --theme, --author, --source-url, --cover, --push, --dry-run, --yes, and --no-open.
- run_pipeline(source: str, options: PipelineOptions) -> PipelineResult.
- PipelineResult contains paper_slug, markdown_path, article_html_path, preview_html_path, image_manifest_path, and optional publish_result.

- [ ] **Step 1: Write failing local end-to-end tests**

    Run a local fixture through run_pipeline and assert Markdown, article.html, preview.html, and images-manifest.json exist. Monkeypatch publish_article and assert it is not called when push is false.

- [ ] **Step 2: Run tests to verify failure**

    python -m pytest tests/test_pipeline_cli.py -q

- [ ] **Step 3: Implement the pipeline**

    For URL/PDF sources, fetch and extract into outputs/paper-analyzer/paper-slug/. Require a manifest before formatting. Run storytelling validation, the required punctuation pass, formatting, and HTML validation. Call publisher only with --push. Default cover is the first final paper image; never fetch unrelated images.

- [ ] **Step 4: Document one-command usage**

    Document analysis-only, preview, gallery, dry-run, and explicit draft push. Explain that dry-run can upload media but cannot create a draft and that credentials are unnecessary for analysis/formatting.

- [ ] **Step 5: Run and commit**

    python -m pytest tests/test_pipeline_cli.py -q
    git add scripts/paper2wechat.py SKILL.md README.md tests
    git commit -m "feat: add unified paper-to-wechat pipeline"

### Task 7: Capability matrix, migration notes, and release hygiene

**Files:**
- Modify: SKILL.md, README.md
- Create: tests/test_full_capability_matrix.py, tests/fixtures/minimal-article.md, tests/fixtures/figure1.png, CHANGELOG.md

- [ ] **Step 1: Exercise every preserved capability**

    Parameterize tests over every formatter and publisher flag, all 85 themes, both templates, punctuation check/write modes, and Markdown/HTML validator modes. Mock network requests and use figure1.png as the only article image.

- [ ] **Step 2: Run the matrix**

    python -m pytest -q

    Expected: all tests pass; fix missing flags, themes, path checks, or sanitization before release.

- [ ] **Step 3: Run static safety scans**

    rg -n --hidden --glob '!*.pyc' --glob '!__pycache__/**' 'C:\\Users\\|~/.codex/skills|xiaohu-wechat|app_secret|access_token' .

    Expected: no user-specific paths, old product name in user-facing docs, or literal credentials. A compatibility note may mention the old name only in a migration section.

- [ ] **Step 4: Verify release contents**

    git ls-files
    git status --short

    Expected: source files, themes, templates, tests, docs, and config example only; no config.json, outputs, caches, debug HTML, or historical paper images.

- [ ] **Step 5: Commit**

    git add SKILL.md README.md CHANGELOG.md tests
    git commit -m "test: verify paper2wechat capability matrix and release hygiene"

### Task 8: Final verification and handoff

**Files:**
- No source changes unless verification finds a concrete defect.

- [ ] **Step 1: Run complete checks**

    python -m pytest -q
    python scripts/paper2wechat.py --help
    python scripts/format.py --help
    python scripts/publish.py --help
    python scripts/validate_storytelling.py tests/fixtures/minimal-article.md
    git status --short

- [ ] **Step 2: Review generated artifacts**

    Confirm a fixture run has outputs/paper-analyzer/demo-paper/demo-paper.md, work/images-manifest.json, wechat/demo-paper/article.html, and wechat/demo-paper/preview.html. Confirm every image reference resolves inside the article directory.

- [ ] **Step 3: Report evidence**

    Report repository path, commits, test count, preserved theme count, CLI checks, security scan, and any remaining limitation such as missing WeChat credentials. Do not claim a public GitHub push until a configured remote push succeeds.

- [ ] **Step 4: Commit only targeted verification fixes**

    git add scripts tests SKILL.md README.md
    git commit -m "fix: address final verification findings"
