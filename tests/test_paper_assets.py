import json

from scripts.download_paper_images import (
    build_image_manifest,
    collect_figure_images,
    write_image_manifest,
)


def test_collect_figure_images_ignores_page_decoration():
    html = """
    <img src="/static/arxiv-logo.png" alt="arXiv logo">
    <figure class="ltx_figure">
      <img src="figures/figure1.png" alt="Architecture">
      <figcaption>Figure 1: System overview.</figcaption>
    </figure>
    """
    figures = collect_figure_images(html, "https://arxiv.org/html/1234.5678")
    assert [item["url"] for item in figures] == [
        "https://arxiv.org/html/figures/figure1.png"
    ]
    assert figures[0]["caption"] == "Figure 1: System overview."


def test_manifest_contains_only_images_in_this_paper_folder(tmp_path):
    article_dir = tmp_path / "paper"
    images_dir = article_dir / "images"
    images_dir.mkdir(parents=True)
    (images_dir / "figure1.png").write_bytes(b"paper-figure")
    other_images = tmp_path / "other-paper"
    other_images.mkdir()
    (other_images / "avatar.png").write_bytes(b"unrelated")

    manifest = build_image_manifest(article_dir, "https://arxiv.org/abs/1234.5678")

    assert [item["path"] for item in manifest["images"]] == ["images/figure1.png"]
    assert manifest["images"][0]["sha256"]
    assert manifest["images"][0]["source_url"].startswith("https://arxiv.org")


def test_manifest_is_written_under_this_papers_work_directory(tmp_path):
    article_dir = tmp_path / "paper"
    (article_dir / "images").mkdir(parents=True)
    (article_dir / "images" / "figure1.png").write_bytes(b"figure")

    path = write_image_manifest(article_dir, "https://arxiv.org/abs/1234.5678")

    assert path == article_dir / "work" / "images-manifest.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["images"][0]["path"] == "images/figure1.png"
