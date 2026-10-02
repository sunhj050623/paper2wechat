from pathlib import Path
import subprocess
import sys

from scripts.paper2wechat import PipelineOptions, run_pipeline
from scripts.paths import REPO_ROOT


def test_unified_runner_cli_is_directly_executable():
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "paper2wechat.py"), "--help"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    assert result.returncode == 0
    assert "--push" in result.stdout


def test_pipeline_builds_preview_without_pushing_by_default(tmp_path):
    article = tmp_path / "article.md"
    images = tmp_path / "images"
    images.mkdir()
    for number in range(1, 4):
        (images / "figure{}.png".format(number)).write_bytes(b"figure")
    article.write_text(
        "# 文章\n\n" + "\n".join(
            "![图{}](images/figure{}.png)".format(n, n) for n in range(1, 4)
        ),
        encoding="utf-8",
    )
    output = tmp_path / "wechat"
    calls = []

    def runner(command, **kwargs):
        calls.append(command)
        if "format.py" in command[1]:
            article_dir = output / "article"
            (article_dir / "images").mkdir(parents=True)
            (article_dir / "article.html").write_text("<article></article>", encoding="utf-8")
            (article_dir / "preview.html").write_text("<html></html>", encoding="utf-8")

        class Result:
            returncode = 0
            stdout = ""
            stderr = ""
        return Result()

    result = run_pipeline(
        article,
        PipelineOptions(output_dir=output, theme="bytedance"),
        runner=runner,
    )

    assert result.markdown_path == article
    assert result.article_html_path.is_file()
    assert result.preview_html_path.is_file()
    assert result.publish_result is None
    assert not any("publish.py" in command[1] for command in calls)


def test_pipeline_calls_publisher_only_when_push_is_explicit(tmp_path):
    article = tmp_path / "article.md"
    images = tmp_path / "images"
    images.mkdir()
    for number in range(1, 4):
        (images / "figure{}.png".format(number)).write_bytes(b"figure")
    article.write_text(
        "# 文章\n\n" + "\n".join(
            "![图{}](images/figure{}.png)".format(n, n) for n in range(1, 4)
        ),
        encoding="utf-8",
    )
    output = tmp_path / "wechat"
    calls = []

    def runner(command, **kwargs):
        calls.append(command)
        if "format.py" in command[1]:
            article_dir = output / "article"
            (article_dir / "images").mkdir(parents=True)
            (article_dir / "article.html").write_text("<article></article>", encoding="utf-8")
            (article_dir / "preview.html").write_text("<html></html>", encoding="utf-8")

        class Result:
            returncode = 0
            stdout = "draft created"
            stderr = ""
        return Result()

    result = run_pipeline(
        article,
        PipelineOptions(output_dir=output, theme="bytedance", push=True, title="文章"),
        runner=runner,
    )

    publish_calls = [command for command in calls if "publish.py" in command[1]]
    assert len(publish_calls) == 1
    assert "--yes" in publish_calls[0]
    assert result.publish_result == "draft created"
