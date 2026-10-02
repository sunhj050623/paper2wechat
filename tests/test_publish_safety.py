from pathlib import Path

from scripts.publish import find_cover_image, replace_all_images


def test_publisher_never_fetches_external_images(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "scripts.publish.download_external_image",
        lambda url: (_ for _ in ()).throw(AssertionError("external fetch")),
    )
    monkeypatch.setattr("scripts.publish.upload_content_image", lambda *args: "cdn")

    result, uploaded, failed = replace_all_images(
        '<img src="https://unrelated.example/logo.png">',
        tmp_path,
        "token",
    )

    assert "https://unrelated.example/logo.png" in result
    assert uploaded == 0
    assert failed == 1


def test_publisher_rejects_local_image_path_outside_article(monkeypatch, tmp_path):
    article_dir = tmp_path / "article"
    article_dir.mkdir()
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"unrelated")
    monkeypatch.setattr(
        "scripts.publish.upload_content_image",
        lambda *args: (_ for _ in ()).throw(AssertionError("outside upload")),
    )

    result, uploaded, failed = replace_all_images(
        '<img src="../outside.png">',
        article_dir,
        "token",
    )

    assert "../outside.png" in result
    assert uploaded == 0
    assert failed == 1


def test_cover_must_be_inside_current_article(monkeypatch, tmp_path):
    article_dir = tmp_path / "article"
    images = article_dir / "images"
    images.mkdir(parents=True)
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"unrelated")
    monkeypatch.setattr("builtins.print", lambda *args, **kwargs: None)

    assert find_cover_image(article_dir, str(outside)) is None


def test_cover_must_be_inside_article_images_directory(monkeypatch, tmp_path):
    article_dir = tmp_path / "article"
    images = article_dir / "images"
    images.mkdir(parents=True)
    unrelated = article_dir / "unrelated.png"
    unrelated.write_bytes(b"not an article image")
    monkeypatch.setattr("builtins.print", lambda *args, **kwargs: None)

    assert find_cover_image(article_dir, str(unrelated)) is None
