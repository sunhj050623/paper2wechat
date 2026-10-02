#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the default reader-facing paper-analyzer deliverable.

This is intentionally a small gate: it catches accidental code-analysis or
unresolved image paths before the article reaches the formatter.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
FORBIDDEN_DEFAULT = {
    "code_path": re.compile(
        r"(?:core_algos\.py|reward_fn\.py|train_slca_grpo|\.py:\d|"
        r"代码已公开|仓库提供测试|实现位于|源码路径|函数名|命令行)"
    ),
    "code_fence": re.compile(r"^\s*```", re.MULTILINE),
    "repo_link": re.compile(r"\[[^\]]*(?:GitHub|代码|仓库)[^\]]*\]\(") ,
}
# The default reader-facing article must not leak TeX source.  Checking only
# ``$$...$$`` misses inline math and command fragments that a Markdown
# renderer leaves as visible text (for example ``$H_\theta$`` or
# ``\\frac{...}{...}``).
FORMULA_RE = re.compile(
    r"\$\$|(?<!\\)\$[^$\n]+\$|"
    r"\\(?:frac|dfrac|tfrac|text|hat|bar|vec|sum|prod|alpha|beta|gamma|theta|mu|sigma|epsilon|qquad|cdot|times|mathbb|mathrm|mathbf|left|right)\b|"
    r"\\[\(\[\{]|\\[\)\]\}]"
)
TITLE_FORBIDDEN = re.compile(
    r"错奖|分开两类反馈|跨片段信用分配|奖励路由|结构性故障|"
    r"一个意外的发现|重新思考智能体|别让总结替工具调用背锅"
)


def validate(path: Path, allow_code: bool, allow_formulas: bool) -> dict:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    warnings: list[str] = []

    refs = IMAGE_RE.findall(text)
    if len(refs) < 3:
        errors.append(f"至少需要 3 张论文图片，当前为 {len(refs)} 张")
    for ref in refs:
        if not ref.startswith("images/"):
            errors.append(f"图片必须使用 images/ 相对路径: {ref}")
        elif not (path.parent / ref).exists():
            errors.append(f"图片不存在: {ref}")

    if not allow_code:
        for label, pattern in FORBIDDEN_DEFAULT.items():
            if pattern.search(text):
                errors.append(f"默认 storytelling 禁止代码分析内容: {label}")

    if not allow_formulas and FORMULA_RE.search(text):
        errors.append("默认 storytelling 不保留裸公式，请改写为自然语言")

    # The H1 is a reader-facing contract: concrete object + concrete tension.
    # Keep the semantic checks here deliberately small; the writing skill owns
    # the human judgment, while this gate catches the recurring opaque titles.
    title_match = re.search(r"(?m)^#\s+(.+?)\s*$", text)
    if not title_match:
        errors.append("文章必须有一个主标题（一级标题）")
    else:
        title = title_match.group(1).strip()
        if not 18 <= len(title) <= 30:
            errors.append(f"主标题长度应控制在 18–30 个汉字左右，当前为 {len(title)} 个字符")
        if TITLE_FORBIDDEN.search(title):
            errors.append("主标题含有未解释的抽象术语或口号，请改成具体对象与冲突")
        if not any(mark in title for mark in ("？", "?", "：", ":")):
            warnings.append("主标题缺少问题或冲突结构（建议使用问号或冒号连接具体场景）")

    # Metadata should read as three deliberate rows above a visual divider.
    metadata = re.search(
        r"(?ms)^# .+\n\n(?P<meta>.*?)\n\n---\s*$",
        text,
    )
    if not metadata:
        errors.append("标题元信息后缺少分隔线；作者、论文、数据应逐行列出")
    else:
        meta = metadata.group("meta")
        for field in ("作者", "论文", "数据"):
            if not re.search(rf"(?m)^\*\*{field}[：:]\*\*", meta):
                errors.append(f"开头元信息缺少单独一行：{field}")

    # A clearly enumerated method must be authored as one ordered list, not
    # as one subheading followed by prose paragraphs or a second summary list.
    method = re.search(r"(?ms)^## 方法[^\n]*\n(?P<body>.*?)(?=^## |\Z)", text)
    if method:
        body = method.group("body")
        entries = re.findall(r"(?m)^([1-9])\.\s+(.+)$", body)
        if [number for number, _ in entries] != ["1", "2", "3"]:
            errors.append("方法三步必须写成同一组连续有序列表 1、2、3")
        elif any(len(item.strip()) < 45 for _, item in entries):
            errors.append("方法有序列表每一步都要保留完整解释，不能只留短标签")
        if re.search(r"(?m)^#{3,6}\s*(?:第一步|第二步|第三步)", body):
            errors.append("方法步骤不能把第一步单独提升为标题，其余步骤留在正文")
        if re.search(r"(?m)^\s*(?:第一步|第二步|第三步)(?:是|才是|，|：)", body):
            errors.append("方法有序列表后仍有重复的步骤段落，请合并去重")
        if re.search(r"三层反馈各自负责什么", body):
            errors.append("方法段落重复概括三步，请保留一组完整步骤即可")

    if re.search(r"\*\*(?:关键句|金句|重点|核心观点)[:：]", text):
        errors.append("不要把‘关键句：’等说明标签写进正文加粗，直接加粗观点本身")
    if len(re.findall(r"\*\*[^*\n]+\*\*", text)) < 12:
        errors.append("正文重点强调不足：至少 12 处有意义的短语或判断需要加粗")
    for section in re.split(r"(?m)(?=^## )", text):
        if section.startswith("## ") and not re.search(r"\*\*[^*\n]+\*\*", section):
            heading = section.splitlines()[0]
            errors.append(f"主要章节缺少正文重点强调：{heading}")

    if len(re.findall(r"^##\s+", text, re.MULTILINE)) < 4:
        warnings.append("章节较少，检查是否真的完成了深度 storytelling")
    if len(re.findall(r"^##\s+", text, re.MULTILINE)) < 5:
        errors.append("默认 storytelling 至少需要 5 个主要章节")
    if len(re.findall(r"^###\s+", text, re.MULTILINE)) < 3:
        errors.append("缺少标题层级：至少需要 3 个 ### 子标题")
    if len(re.findall(r"^>\s*\S", text, re.MULTILINE)) < 2:
        errors.append("缺少至少 2 个论文原句引用块（>）")
    if len(re.findall(r"^(?:[-*]|\d+\.)\s+", text, re.MULTILINE)) < 4:
        errors.append("缺少分点列表：方法、实验或局限需要使用 Markdown 列表")
    if len([p for p in re.split(r"\n\s*\n", text) if p.strip()]) < 15:
        warnings.append("自然段少于 15 段")
    if not re.search(r"\|.+\|\n\|[- :|]+\|", text):
        errors.append("缺少至少一个 Markdown 数据表格")
    if not re.search(r"局限|边界|限制", text):
        errors.append("缺少局限或适用边界段落")
    if ":::end[💡 实时了解更多AI论文，关注 Tau Lab]" not in text:
        errors.append("缺少固定结尾标记")

    return {
        "path": str(path),
        "ok": not errors,
        "image_count": len(refs),
        "errors": errors,
        "warnings": warnings,
    }


def validate_rendered_html(markdown_path: Path, html_path: Path) -> dict:
    """Check that semantic structure survived Markdown-to-WeChat conversion."""
    html = html_path.read_text(encoding="utf-8")
    errors: list[str] = []
    md_images = len(IMAGE_RE.findall(markdown_path.read_text(encoding="utf-8")))
    html_images = len(re.findall(r"<img\b", html, re.IGNORECASE))
    if html_images != md_images:
        errors.append(f"HTML 图片数 {html_images} 与 Markdown 图片数 {md_images} 不一致")

    metadata = re.search(
        r"(?is)<h1\b[^>]*>.*?</h1>\s*<p\b[^>]*>(.*?)</p>\s*<hr\b",
        html,
    )
    if not metadata:
        errors.append("HTML 开头缺少独立元信息行或分隔线")
    else:
        block = metadata.group(1)
        if len(re.findall(r"<br\s*/?>", block, re.IGNORECASE)) < 2:
            errors.append("HTML 作者、论文、数据未保留为逐行元信息")
        for field in ("作者", "论文", "数据"):
            if field not in block:
                errors.append(f"HTML 开头元信息缺少：{field}")

    method_heading = re.search(r"(?is)<h2\b[^>]*>方法怎样工作.*?</h2>", html)
    if method_heading:
        rest = html[method_heading.end():]
        next_heading = re.search(r"(?is)<h2\b", rest)
        method_html = rest[:next_heading.start()] if next_heading else rest
        numbers = re.findall(r"<span\b[^>]*>\s*([123])\s*</span>", method_html)
        if numbers[:3] != ["1", "2", "3"]:
            errors.append("HTML 方法列表未保留连续数字圆点 1、2、3")
        if re.search(r"(?is)<h[3-6]\b[^>]*>\s*(?:第一步|第二步|第三步)", method_html):
            errors.append("HTML 方法步骤出现重复层级标题")
    else:
        errors.append("HTML 缺少方法章节标题")

    quote_count = len(re.findall(r"data-role=[\"']blockquote[\"']", html, re.IGNORECASE))
    if quote_count < 2:
        errors.append(f"HTML 原句引用卡片不足 2 个，当前为 {quote_count} 个")
    strong_count = len(re.findall(r"<strong\b[^>]*style=[\"'][^\"']*color:\s*#1677FF", html, re.IGNORECASE))
    if strong_count < 12:
        errors.append(f"HTML 蓝色粗体强调不足 12 处，当前为 {strong_count} 处")
    if "关键句：" in html or "关键句:</strong>" in html:
        errors.append("HTML 仍显示说明性标签‘关键句：’")

    # A second gate is required after formatting: an old or hand-edited HTML
    # file must not bypass the Markdown check and publish visible TeX source.
    visible_html = re.sub(r"<[^>]+>", " ", html)
    formula_hits = FORMULA_RE.findall(visible_html)
    if formula_hits:
        errors.append(f"HTML 仍包含 {len(formula_hits)} 处公式源码，请改写为自然语言")

    return {
        "path": str(html_path),
        "ok": not errors,
        "image_count": html_images,
        "blockquote_count": quote_count,
        "blue_strong_count": strong_count,
        "formula_like_count": len(formula_hits),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("markdown", type=Path)
    parser.add_argument("--html", type=Path, help="Also validate rendered WeChat article HTML")
    parser.add_argument("--allow-code", action="store_true")
    parser.add_argument("--allow-formulas", action="store_true")
    args = parser.parse_args()

    result = validate(args.markdown, args.allow_code, args.allow_formulas)
    if args.html:
        rendered = validate_rendered_html(args.markdown, args.html)
        result["rendered_html"] = rendered
        result["ok"] = result["ok"] and rendered["ok"]
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
