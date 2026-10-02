#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""微信公众号草稿箱发布工具

将 format.py 排版后的文章推送到微信公众号草稿箱。

用法:
    # 发布排版好的文章目录
    python3 publish.py --dir /path/to/formatted/article/

    # 指定封面图
    python3 publish.py --dir /path/to/formatted/article/ --cover cover.jpg

    # 直接从 Markdown 一步到位（自动排版+发布）
    python3 publish.py --input article.md --theme elegant
"""

import argparse
import json
import os
import re
import subprocess
import sys
import base64
from pathlib import Path
import io

import html as html_module
import tempfile
import tempfile as tempfile_module
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import requests
from scripts.config import load_config, redact
from scripts.paths import REPO_ROOT, resolve_output_path

# ── 路径 ──────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent

CONFIG = load_config()

# Reader-facing articles use natural-language explanations by default.  Keep a
# final publish gate so an old or hand-edited HTML file cannot leak TeX source
# into the公众号正文.  Explicit formula-mode publishing can opt out with
# ``--allow-formulas``.
FORMULA_RE = re.compile(
    r"\$\$|(?<!\\)\$[^$\n]+\$|"
    r"\\(?:frac|dfrac|tfrac|text|hat|bar|vec|sum|prod|alpha|beta|gamma|theta|mu|sigma|epsilon|qquad|cdot|times|mathbb|mathrm|mathbf|left|right)\b|"
    r"\\[\(\[\{]|\\[\)\]\}]"
)


# ── 微信 API ─────────────────────────────────────────────────────────
def get_access_token():
    """获取微信 API access_token"""
    wechat = CONFIG.get("wechat", {})
    app_id = wechat.get("app_id")
    app_secret = wechat.get("app_secret")

    if not app_id or not app_secret:
        print("错误: config.json 中未配置 wechat.app_id 或 wechat.app_secret")
        sys.exit(1)

    url = (
        "https://api.weixin.qq.com/cgi-bin/token"
        f"?grant_type=client_credential&appid={app_id}&secret={app_secret}"
    )
    try:
        resp = requests.get(url, timeout=15)
    except Exception as error:
        print("错误: 获取 access_token 请求失败: {}".format(redact(error, CONFIG)))
        sys.exit(1)
    data = resp.json()

    if "access_token" in data:
        print(f"  token 有效期: {data.get('expires_in', '?')} 秒")
        return data["access_token"]
    else:
        errcode = data.get("errcode", "?")
        errmsg = data.get("errmsg", "未知错误")
        print(f"错误: 获取 access_token 失败 (errcode={errcode}: {errmsg})")
        if errcode == 40164:
            print("  → IP 不在白名单中，请到公众号后台添加当前 IP")
        elif errcode in (40001, 40125):
            print("  → AppSecret 无效，请检查 config.json 中的 app_secret")
        sys.exit(1)


def upload_thumb_image(token, image_path):
    """上传封面图到永久素材库，返回 media_id"""
    url = (
        "https://api.weixin.qq.com/cgi-bin/material/add_material"
        f"?access_token={token}&type=image"
    )

    filename = os.path.basename(image_path)
    ext = Path(image_path).suffix.lower()
    content_type = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
    }.get(ext, "image/jpeg")

    with open(image_path, "rb") as f:
        files = {"media": (filename, f, content_type)}
        resp = requests.post(url, files=files, timeout=30)

    data = resp.json()
    if "media_id" in data:
        return data["media_id"]
    else:
        print("错误: 上传封面图失败 - {}".format(redact(data, CONFIG)))
        return None


def upload_content_image(token, image_path, max_retries=3):
    """上传正文图片（返回 CDN URL），失败自动重试"""
    import time
    url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={token}"

    filename = os.path.basename(image_path)
    ext = Path(image_path).suffix.lower()
    content_type = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
    }.get(ext, "image/jpeg")

    for attempt in range(1, max_retries + 1):
        try:
            with open(image_path, "rb") as f:
                files = {"media": (filename, f, content_type)}
                resp = requests.post(url, files=files, timeout=30)

            data = resp.json()
            if "url" in data:
                # 微信API返回http，需要改成https才能在公众号后台显示
                url = data["url"].replace("http://", "https://")
                return url
            else:
                print("  [X] 上传失败 ({}/{}) - {}".format(
                    attempt, max_retries, redact(data, CONFIG)
                ))
        except Exception as e:
            print("  [X] 上传异常 ({}/{}) - {}".format(
                attempt, max_retries, redact(e, CONFIG)
            ))

        if attempt < max_retries:
            time.sleep(2 * attempt)  # 递增等待

    print(f"  [X] 上传彻底失败 - {filename}")
    return None


def download_external_image(url):
    """下载外部图片到临时文件，返回本地路径"""
    try:
        # 还原 HTML 实体（&amp; → &）
        url = html_module.unescape(url)
        resp = requests.get(url, timeout=30, headers={
            "User-Agent": "Mozilla/5.0"
        })
        resp.raise_for_status()

        # 从 URL 或 Content-Type 推断扩展名
        content_type = resp.headers.get("Content-Type", "")
        if "png" in content_type:
            ext = ".png"
        elif "gif" in content_type:
            ext = ".gif"
        elif "webp" in content_type:
            ext = ".webp"
        else:
            ext = ".jpg"

        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        tmp.write(resp.content)
        tmp.close()
        return tmp.name
    except Exception as e:
        print("  [X] 下载失败，远程图片资源无法读取: {}".format(redact(e, CONFIG)))
        return None


def replace_all_images(html, article_dir, token, save_debug=False):
    """替换 HTML 中的所有图片（本地+外部）为微信 CDN URL。

    调试 HTML 默认不落盘，避免用户把仅用于排查上传结果的 HTML
    误当成公众号预览或正文。需要排查时显式传入 ``save_debug=True``。
    """
    article_root = Path(article_dir).resolve()
    image_dir = article_root / "images"
    replaced = 0
    failed = 0

    def replace_src(match):
        nonlocal replaced, failed
        src = match.group(1)

        # 已经是微信 CDN 的图片，跳过
        if "mmbiz.qpic.cn" in src:
            return match.group(0)

        # External image URLs are deliberately not fetched: paper articles may
        # only upload assets copied into this article's own images/ directory.
        if src.startswith("http://") or src.startswith("https://"):
            failed += 1
            print("  [X] 拒绝上传文章目录外的远程图片")
            return match.group(0)

        if not src.startswith("images/") or any(
            part in {"", ".", ".."} for part in src.replace("\\", "/").split("/")
        ):
            failed += 1
            print("  [X] 图片路径必须位于当前文章 images/ 目录")
            return match.group(0)
        local_path = (article_root / src).resolve()
        try:
            local_path.relative_to((article_root / "images").resolve())
        except ValueError:
            failed += 1
            print("  [X] 图片路径超出当前文章目录")
            return match.group(0)

        if local_path.is_file():
            cdn_url = upload_content_image(token, str(local_path))
            if cdn_url:
                replaced += 1
                print(f"  [OK] {os.path.basename(src)}")
                return f'src="{cdn_url}"'
            else:
                failed += 1
                return match.group(0)
        else:
            print(f"  [X] 未找到: {src}")
            failed += 1
            return match.group(0)

    html = re.sub(r'src="([^"]+)"', replace_src, html)

    if save_debug:
        debug_path = article_dir / "debug_wechat.html"
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  [DEBUG] 已保存替换后的HTML: {debug_path}")

    return html, replaced, failed


def push_draft(token, title, content, thumb_media_id, author="Tau Lab", source_url="", album_id=None):
    """推送文章到草稿箱

    Args:
        album_id: 合集ID（可选），如果指定则自动添加到该合集
    """
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"

    article_data = {
        "title": title,
        "author": author,
        "content": content,
        "content_source_url": source_url,
        "thumb_media_id": thumb_media_id,
        "need_open_comment": 1,  # 自动开启留言
        "only_fans_can_comment": 0,
        "is_original": 1,  # 自动声明原创
    }

    # 如果指定了合集ID，添加到合集
    if album_id:
        article_data["album_id"] = album_id

    data = {"articles": [article_data]}

    # 必须用 ensure_ascii=False，否则中文被转义为 \uXXXX 导致微信计算标题长度错误
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    resp = requests.post(url, data=body,
                         headers={"Content-Type": "application/json"}, timeout=30)
    result = resp.json()

    if "media_id" in result:
        return result["media_id"]
    else:
        errcode = result.get("errcode", "?")
        errmsg = result.get("errmsg", "未知错误")
        print("错误: 推送草稿箱失败 (errcode={}: {})".format(
            errcode, redact(errmsg, CONFIG)
        ))
        return None


# ── 辅助函数 ──────────────────────────────────────────────────────────
def extract_title_from_html(html):
    """从 HTML 中提取 h1 标题"""
    match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.DOTALL)
    if match:
        return re.sub(r"<[^>]+>", "", match.group(1)).strip()
    return None


def extract_market_overview(markdown_path):
    """从Markdown文件提取今日市场概览内容"""
    try:
        with open(markdown_path, encoding="utf-8") as f:
            content = f.read()

        # 匹配 ## 📊 今日市场概览 后的引用块内容
        match = re.search(
            r'##\s*📊\s*今日市场概览\s*\n\s*>\s*(.+?)(?=\n\n|\n###|\n##|$)',
            content,
            re.DOTALL
        )

        if match:
            overview = match.group(1).strip()
            # 清理Markdown格式标记
            overview = re.sub(r'\*\*<u>|</u>\*\*|\*\*|__', '', overview)
            overview = re.sub(r'<u>|</u>', '', overview)
            return overview
        return None
    except Exception as e:
        print("  [X] 提取市场概览失败: {}".format(redact(e, CONFIG)))
        return None


def generate_cover_image(overview_text, output_path):
    """使用AI生成封面图"""
    ai_config = CONFIG.get("ai", {})
    base_url = ai_config.get("url", "").rstrip("/")
    api_key = ai_config.get("api_key", "")
    model = ai_config.get("model", "")
    if not base_url or not api_key or not model:
        print("  [提示] 未配置封面生成 API，跳过生成")
        return False

    # 构建提示词（保留中文内容，更符合市场报告风格）
    prompt = f"{overview_text}\n\n请生成一张专业的股市概览图表，体现市场走势和重点板块表现，商务专业风格。"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024"
    }

    try:
        print(f"  正在生成AI封面图...")
        response = requests.post(
            f"{base_url}/images/generations",
            headers=headers,
            json=data,
            timeout=180
        )

        if response.status_code == 200:
            result = response.json()
            if "data" in result and len(result["data"]) > 0:
                image_data = result["data"][0]

                # 处理URL返回
                if "url" in image_data:
                    image_url = image_data["url"]
                    print(f"  [OK] 图片生成成功，正在下载...")

                    img_response = requests.get(image_url, timeout=30)
                    if img_response.status_code == 200:
                        with open(output_path, "wb") as f:
                            f.write(img_response.content)
                        print(f"  [OK] AI封面图已保存: {output_path}")
                        return True

                # 处理base64返回
                elif "b64_json" in image_data:
                    image_bytes = base64.b64decode(image_data["b64_json"])
                    with open(output_path, "wb") as f:
                        f.write(image_bytes)
                    print(f"  [OK] AI封面图已保存: {output_path}")
                    return True

        print(f"  [X] 图片生成失败: {response.status_code}")
        return False

    except Exception as e:
        print("  [X] 图片生成异常: {}".format(redact(e, CONFIG)))
        return False


def find_cover_image(article_dir, cover_arg=None):
    """找到封面图路径（仅在当前文章目录中查找）"""
    article_root = Path(article_dir).resolve()
    image_dir = (article_root / "images").resolve()

    def is_article_image(path):
        try:
            path.resolve().relative_to(image_dir)
        except ValueError:
            return False
        return path.is_file()

    if cover_arg:
        supplied = Path(cover_arg)
        p = supplied.resolve() if supplied.is_absolute() else (article_root / supplied).resolve()
        try:
            p.relative_to(image_dir)
        except ValueError:
            print("警告: 封面图必须位于当前文章的 images/ 目录内")
            return None
        if p.is_file():
            return p
        print(f"警告: 指定的封面图不存在: {cover_arg}")

    # 仅在当前文章的 images/ 目录下找封面图
    if image_dir.exists():
        # 优先找 cover.png/jpg
        for name in ("cover.png", "cover.jpg", "cover.jpeg"):
            cover_path = image_dir / name
            if is_article_image(cover_path):
                return cover_path

        # 没有 cover.* 文件，取第一张图片
        for ext in ("*.jpg", "*.jpeg", "*.png", "*.gif"):
            images = [path for path in sorted(image_dir.glob(ext)) if is_article_image(path)]
            if images:
                return images[0]

    return None


# ── 主流程 ────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="微信公众号草稿箱发布工具")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dir", "-d", help="format.py 的输出目录（含 article.html 和 images/）")
    group.add_argument("--input", "-i", help="Markdown 文件路径（自动调用 format.py 排版后发布）")
    parser.add_argument("--cover", "-c", help="封面图片路径")
    parser.add_argument("--title", "-t", help="文章标题（默认从 HTML 提取）")
    parser.add_argument("--theme", default=None,
                        help="排版主题（仅 --input 模式有效，默认读取 gallery 选中的主题）")
    parser.add_argument("--author", "-a",
                        default=CONFIG.get("wechat", {}).get("author", "Tau Lab"),
                        help="作者名")
    parser.add_argument("--source-url", "-s", default="",
                        help="原文链接（content_source_url，公众号文末「阅读原文」按钮指向）")
    parser.add_argument("--dry-run", action="store_true",
                        help="只做排版和图片上传，不推送草稿箱（用于测试）")
    parser.add_argument("--save-debug", action="store_true",
                        help="保存图片替换后的调试 HTML；默认不生成，避免与正文预览混淆")
    parser.add_argument("--allow-formulas", action="store_true",
                        help="允许显式公式模式；默认拒绝残留的 LaTeX 源码")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="非交互模式：所有确认提示自动回 y（部分图片上传失败继续、其他）")
    parser.add_argument("--album-id", default=None,
                        help="合集ID（指定后自动添加到该合集）")
    args = parser.parse_args()

    # ── 1. 确定文章目录 ──────────────────────────────────────────────
    if args.input:
        # 确定主题：优先命令行指定 > gallery 选中 > 默认
        theme = args.theme
        if not theme:
            gallery_theme_file = (
                Path(tempfile_module.gettempdir()) / "paper2wechat" / "selected-theme.txt"
            )
            if gallery_theme_file.exists():
                saved = gallery_theme_file.read_text(encoding="utf-8").strip()
                if saved:
                    theme = saved
                    print(f"  使用 gallery 选中的主题: {theme}")
        if not theme:
            theme = CONFIG["settings"]["default_theme"]

        # 先调用 format.py 排版
        input_path = Path(args.input).resolve()
        print(f"=== 第一步：排版 ===")
        format_cmd = [
            sys.executable, str(SCRIPT_DIR / "format.py"),
            "--input", str(input_path),
            "--theme", theme,
            "--no-open",
        ]
        result = subprocess.run(format_cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        if result.returncode != 0:
            print(f"排版失败:\n{result.stderr}")
            sys.exit(1)
        print(result.stdout)

        # 从 format.py 输出中找到目录
        output_base = resolve_output_path(CONFIG["output_dir"])
        file_stem = re.sub(r"-(公众号|小红书|微博)$", "", input_path.stem)
        article_dir = output_base / file_stem
    else:
        article_dir = Path(args.dir)

    if not article_dir.exists():
        print(f"错误: 目录不存在 - {article_dir}")
        sys.exit(1)

    # ── 生成AI封面图 ──────────────────────────────────────────────
    if args.input:  # 只在使用markdown输入时自动生成
        markdown_path = Path(args.input).resolve()
        overview = extract_market_overview(str(markdown_path))

        if overview:
            print(f"\n=== 生成AI封面图 ===")
            image_dir = article_dir / "images"
            image_dir.mkdir(parents=True, exist_ok=True)
            cover_output = image_dir / "cover.png"

            generate_cover_image(overview, str(cover_output))

    # ── 2. 读取文章 HTML ─────────────────────────────────────────────
    print(f"\n=== {'第二步' if args.input else '第一步'}：准备发布 ===")
    article_path = article_dir / "article.html"

    if not article_path.exists():
        # 兼容旧版：从 preview.html 提取
        preview_path = article_dir / "preview.html"
        if preview_path.exists():
            print("未找到 article.html，从 preview.html 提取...")
            preview_content = preview_path.read_text(encoding="utf-8")
            match = re.search(
                r'<div id="wechatHtml">(.*?)</div>\s*<script>',
                preview_content, re.DOTALL
            )
            if match:
                html = match.group(1).strip()
            else:
                print("错误: 无法从 preview.html 提取文章内容")
                sys.exit(1)
        else:
            print(f"错误: 未找到 article.html 或 preview.html")
            sys.exit(1)
    else:
        html = article_path.read_text(encoding="utf-8")

    if not args.allow_formulas:
        visible_html = re.sub(r"<[^>]+>", " ", html)
        formula_hits = FORMULA_RE.findall(visible_html)
        if formula_hits:
            print(f"错误: 正文仍包含 {len(formula_hits)} 处公式源码，已阻止推送。")
            print("  请在 Markdown 中改写为自然语言后重新排版；只有明确公式模式才使用 --allow-formulas")
            sys.exit(1)

    # ── 2.5. 插入封面图到【今日市场概览】区域 ──────────────────────────
    # 检查是否有cover.png，如果有则插入到市场概览标题后
    image_dir = article_dir / "images"
    cover_path = image_dir / "cover.png" if image_dir.exists() else None

    if cover_path and cover_path.exists():
        # 查找【今日市场概览】或类似的市场概览标题
        # 匹配 h2 标签包含"市场概览"的位置
        market_overview_pattern = r'(<h2[^>]*>.*?市场概览.*?</h2>)'
        match = re.search(market_overview_pattern, html, re.IGNORECASE)

        if match:
            # 在h2标题后插入图片
            h2_tag = match.group(1)
            # 构建图片HTML（使用本地相对路径，后续会被替换为CDN URL）
            img_html = f'\n<p style="text-align: center;"><img src="images/cover.png" style="max-width: 100%; height: auto;" /></p>\n'

            # 替换：h2标题 -> h2标题 + 图片
            html = html.replace(h2_tag, h2_tag + img_html)
            print(f"  [OK] 封面图已插入到【今日市场概览】区域")
        else:
            print(f"  [提示] 未找到【今日市场概览】标题，跳过插入")

    # ── 3. 提取标题 ──────────────────────────────────────────────────
    title = args.title or extract_title_from_html(html) or article_dir.name
    author = args.author
    print(f"标题: {title}")
    print(f"作者: {author}")

    # 标题长度预检：公众号标题硬限 64 字符，超过 30 字会影响展示
    title_len = len(title)
    if title_len > 64:
        print(f"\n❌ 标题过长: {title_len} 字符 > 64（公众号 API 硬限）")
        print(f"   请缩短标题再发布。建议 30 字以内，保留 2-3 个核心锚点。")
        sys.exit(1)
    elif title_len > 30:
        print(f"\n⚠️  标题偏长: {title_len} 字符 > 30（公众号展示可能截断）")
        if not args.yes:
            resp = input("  继续用这个标题？(y/N) ").strip().lower()
            if resp != "y":
                print("  已中止，请缩短标题后重试")
                sys.exit(0)

    # ── 4. 获取 token ────────────────────────────────────────────────
    print(f"\n获取 access_token...")
    token = get_access_token()
    print("[OK] token 获取成功")

    # ── 5. 上传正文图片 ──────────────────────────────────────────────
    # 统计图片数量（本地 + 外部）
    image_dir = article_dir / "images"
    local_count = len(list(image_dir.iterdir())) if image_dir.exists() else 0
    external_count = len(re.findall(r'src="(https?://[^"]+)"', html))
    # 排除已是微信 CDN 的
    external_count -= len(re.findall(r'src="https?://mmbiz\.qpic\.cn[^"]*"', html))
    total_images = local_count + external_count

    if total_images > 0:
        print(f"\n上传正文图片 ({local_count} 本地 + {external_count} 外部)...")
        html, replaced, failed = replace_all_images(
            html, article_dir, token, save_debug=args.save_debug
        )
        print(f"  上传完成: {replaced} 成功, {failed} 失败")
        if failed > 0 and replaced == 0:
            print("  错误: 所有图片上传失败，中止发布（不推空图草稿）")
            sys.exit(1)
        elif failed > 0:
            print("  警告: 部分图片上传失败，文章中对应位置可能显示空白")
            if args.yes:
                print("  (--yes 已启用，自动继续)")
            else:
                resp = input("  继续发布？(y/N) ").strip().lower()
                if resp != "y":
                    print("  已中止")
                    sys.exit(0)
    else:
        print("\n无正文图片需上传")

    # ── 6. 上传封面图 ────────────────────────────────────────────────
    cover_path = find_cover_image(article_dir, args.cover)
    if cover_path:
        print(f"\n上传封面图: {cover_path.name}")
        thumb_media_id = upload_thumb_image(token, str(cover_path))
        if thumb_media_id:
            print(f"  [OK] media_id: {thumb_media_id[:20]}...")
        else:
            print("  [X] 封面上传失败")
            thumb_media_id = None
    else:
        print("\n未找到封面图")
        thumb_media_id = None

    if not thumb_media_id:
        print("\n错误: 微信要求必须有封面图。")
        print("  请用 --cover 指定封面图路径，或在 images/ 目录放一张图片")
        sys.exit(1)

    # ── 7. 推送草稿箱 ────────────────────────────────────────────────
    if args.dry_run:
        print(f"\n[dry-run] 跳过推送草稿箱")
        print(f"  标题: {title}")
        print(f"  封面 media_id: {thumb_media_id}")
        print(f"  HTML 长度: {len(html)} 字符")
        return

    print(f"\n推送到草稿箱...")

    # 如果未指定合集ID，尝试从配置读取默认合集
    album_id = args.album_id
    if not album_id:
        album_id = CONFIG.get("wechat", {}).get("default_album_id")
    # 配置模板里的提示语不是合法合集 ID，不能发送给微信 API。
    # 保留兼容性：旧配置仍可使用，但会按“未指定合集”处理。
    if album_id and (album_id.startswith("请填写") or album_id in {"YOUR_ALBUM_ID", "<album_id>"}):
        print("  [提示] 未配置有效合集 ID，跳过合集绑定")
        album_id = None

    media_id = push_draft(token, title, html, thumb_media_id, author, args.source_url, album_id)

    if media_id:
        print(f"\n{'='*40}")
        print(f"  发布成功!")
        print(f"  草稿 media_id: {media_id}")
        if album_id:
            print(f"  已添加到合集: {album_id}")
        print(f"  留言功能: 已开启")
        print(f"  → 请到微信公众号后台 → 草稿箱 查看和发布")
        print(f"{'='*40}")
    else:
        print(f"\n发布失败")
        sys.exit(1)


if __name__ == "__main__":
    if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", errors="replace"
        )
    main()
