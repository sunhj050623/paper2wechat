import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_all_source_themes_and_templates_are_bundled():
    inventory = json.loads(
        (ROOT / "tests" / "fixtures" / "theme-inventory.json").read_text(
            encoding="utf-8"
        )
    )
    actual = sorted(path.name for path in (ROOT / "themes").glob("*.json"))
    assert actual == inventory["files"]
    assert len(actual) == 85
    assert (ROOT / "templates" / "gallery.html").is_file()
    assert (ROOT / "templates" / "preview.html").is_file()


def test_every_theme_is_valid_json_and_matches_source_hashes():
    inventory = json.loads(
        (ROOT / "tests" / "fixtures" / "theme-inventory.json").read_text(
            encoding="utf-8"
        )
    )
    for name, expected_sha256 in inventory["sha256"].items():
        path = ROOT / "themes" / name
        value = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(value, dict), name
        import hashlib
        actual_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual_sha256 == expected_sha256, name
