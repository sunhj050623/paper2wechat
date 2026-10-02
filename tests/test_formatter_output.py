import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_local_markdown_generates_wechat_article_and_preview(tmp_path):
    source = tmp_path / "paper.md"
    images = tmp_path / "images"
    images.mkdir()
    (images / "figure1.png").write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
    )
    source.write_text(
        "# 测试文章\n\n## 引言\n\n本地排版烟雾测试。\n\n"
        "![论文图](images/figure1.png)\n",
        encoding="utf-8",
    )
    output = tmp_path / "generated"
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"

    subprocess.run(
        [
            sys.executable, str(ROOT / "scripts" / "format.py"),
            "--input", str(source), "--theme", "bytedance",
            "--output", str(output), "--no-open",
        ],
        cwd=str(ROOT), env=env, check=True, capture_output=True,
        encoding="utf-8", errors="replace",
    )

    article_dir = output / "paper"
    assert (article_dir / "article.html").is_file()
    assert (article_dir / "preview.html").is_file()
    assert (article_dir / "images" / "figure1.png").is_file()
    assert "<img" in (article_dir / "article.html").read_text(encoding="utf-8")


def test_default_output_is_relative_to_calling_workspace(tmp_path):
    source = tmp_path / "paper.md"
    source.write_text("# 测试文章\n\n## 正文\n\n工作区输出路径测试。\n", encoding="utf-8")
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "format.py"), "--input", str(source), "--no-open"],
        cwd=str(tmp_path),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    expected = tmp_path / "outputs" / "wechat-format" / "paper"
    assert result.returncode == 0, result.stderr
    assert (expected / "article.html").is_file()
    assert (expected / "preview.html").is_file()
