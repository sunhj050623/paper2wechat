#!/usr/bin/env python3
"""Run validated article formatting and optional WeChat draft creation."""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.paths import REPO_ROOT, resolve_output_path


@dataclass
class PipelineOptions:
    output_dir: Path = Path("outputs/wechat-format")
    theme: str = "bytedance"
    author: str = "Tau Lab"
    source_url: str = ""
    cover: str = ""
    title: str = ""
    push: bool = False
    dry_run: bool = False
    no_open: bool = True
    font_size: int = 15


@dataclass
class PipelineResult:
    paper_slug: str
    markdown_path: Path
    article_html_path: Path
    preview_html_path: Path
    image_manifest_path: Path
    publish_result: str = None


def _run(command, runner, cwd=None):
    result = runner(
        command,
        cwd=str(cwd or Path.cwd()),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode:
        message = (result.stderr or result.stdout or "命令执行失败").strip()
        raise RuntimeError(message)
    return result


def run_pipeline(source, options=None, runner=subprocess.run):
    """Validate a drafted Markdown article, format it, then optionally publish."""
    options = options or PipelineOptions()
    working_directory = Path.cwd().resolve()
    markdown_path = Path(source).resolve()
    if not markdown_path.is_file():
        raise FileNotFoundError("文章 Markdown 不存在: {}".format(markdown_path))
    paper_slug = re.sub(r"-(公众号|小红书|微博)$", "", markdown_path.stem)
    image_manifest_path = markdown_path.parent / "work" / "images-manifest.json"

    _run(
        [sys.executable, str(REPO_ROOT / "scripts" / "zh_punctuation_fix.py"),
         str(markdown_path), "--write"],
        runner,
        cwd=working_directory,
    )
    _run(
        [sys.executable, str(REPO_ROOT / "scripts" / "validate_storytelling.py"),
         str(markdown_path)],
        runner,
        cwd=working_directory,
    )

    output_dir = resolve_output_path(options.output_dir, working_directory)
    format_command = [
        sys.executable, str(REPO_ROOT / "scripts" / "format.py"),
        "--input", str(markdown_path),
        "--theme", options.theme,
        "--output", str(output_dir),
        "--format", "wechat",
        "--font-size", str(options.font_size),
    ]
    if options.no_open:
        format_command.append("--no-open")
    _run(format_command, runner, cwd=working_directory)

    article_dir = output_dir / paper_slug
    article_html_path = article_dir / "article.html"
    preview_html_path = article_dir / "preview.html"
    if not article_html_path.is_file() or not preview_html_path.is_file():
        raise RuntimeError("格式器没有生成 article.html 和 preview.html")
    _run(
        [sys.executable, str(REPO_ROOT / "scripts" / "validate_storytelling.py"),
         str(markdown_path), "--html", str(article_html_path)],
        runner,
        cwd=working_directory,
    )

    publish_result = None
    if options.push or options.dry_run:
        title = options.title or _extract_title(markdown_path)
        cover = options.cover or _first_manifest_image(image_manifest_path)
        command = [
            sys.executable, str(REPO_ROOT / "scripts" / "publish.py"),
            "--dir", str(article_dir),
            "--title", title,
            "--author", options.author,
            "--source-url", options.source_url,
        ]
        if cover:
            command.extend(["--cover", cover])
        if options.dry_run:
            command.append("--dry-run")
        else:
            command.append("--yes")
        result = _run(command, runner, cwd=working_directory)
        publish_result = result.stdout.strip()

    return PipelineResult(
        paper_slug=paper_slug,
        markdown_path=markdown_path,
        article_html_path=article_html_path,
        preview_html_path=preview_html_path,
        image_manifest_path=image_manifest_path,
        publish_result=publish_result,
    )


def _extract_title(markdown_path):
    for line in markdown_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return markdown_path.stem


def _first_manifest_image(manifest_path):
    if not manifest_path.is_file():
        return ""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    images = manifest.get("images", [])
    if not images:
        return ""
    return images[0].get("path", "")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", "-i", required=True, help="已完成分析的文章 Markdown")
    parser.add_argument("--output", "-o", default="outputs/wechat-format")
    parser.add_argument("--theme", "-t", default="bytedance")
    parser.add_argument("--author", default="Tau Lab")
    parser.add_argument("--source-url", default="")
    parser.add_argument("--cover", default="")
    parser.add_argument("--title", default="")
    parser.add_argument("--font-size", type=int, default=15)
    publish_mode = parser.add_mutually_exclusive_group()
    publish_mode.add_argument("--push", action="store_true", help="明确创建公众号草稿")
    publish_mode.add_argument("--dry-run", action="store_true",
                              help="验证发布链路并上传素材，但不创建草稿")
    parser.add_argument("--open", action="store_true", help="完成排版后打开预览")
    args = parser.parse_args(argv)

    result = run_pipeline(
        args.input,
        PipelineOptions(
            output_dir=Path(args.output),
            theme=args.theme,
            author=args.author,
            source_url=args.source_url,
            cover=args.cover,
            title=args.title,
            push=args.push,
            dry_run=args.dry_run,
            no_open=not args.open,
            font_size=args.font_size,
        ),
    )
    print("Markdown: {}".format(result.markdown_path))
    print("文章 HTML: {}".format(result.article_html_path))
    print("预览 HTML: {}".format(result.preview_html_path))
    print("图片来源清单: {}".format(result.image_manifest_path))
    if result.publish_result:
        print(result.publish_result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
