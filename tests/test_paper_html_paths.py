from pathlib import Path

from scripts.generate_html import process_images
from scripts.validate_storytelling import validate_image_manifest


def test_html_generator_embeds_only_images_inside_article(tmp_path):
    article_dir = tmp_path / "article"
    (article_dir / "images").mkdir(parents=True)
    (article_dir / "images" / "figure1.png").write_bytes(b"paper-image")
    (tmp_path / "other.png").write_bytes(b"unrelated")
    markdown = (
        "![paper](images/figure1.png)\n"
        "![other](../other.png)\n"
    )

    result = process_images(markdown, article_dir)

    assert "data:image/png;base64," in result
    assert "![other](../other.png)" in result


def test_manifest_validation_requires_exact_current_article_image_set(tmp_path):
    article_dir = tmp_path / "article"
    images_dir = article_dir / "images"
    images_dir.mkdir(parents=True)
    (images_dir / "figure1.png").write_bytes(b"paper-image")
    markdown_path = article_dir / "article.md"
    markdown_path.write_text("![figure](images/figure1.png)\n", encoding="utf-8")

    errors = validate_image_manifest(markdown_path)

    assert errors == ["图片来源清单不存在: work/images-manifest.json"]


def test_manifest_validation_rejects_parent_traversal(tmp_path):
    article_dir = tmp_path / "article"
    (article_dir / "work").mkdir(parents=True)
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"unrelated")
    markdown_path = article_dir / "article.md"
    markdown_path.write_text("![figure](images/../outside.png)\n", encoding="utf-8")

    errors = validate_image_manifest(markdown_path)

    assert any("图片必须位于本论文 images/ 目录" in error for error in errors)
