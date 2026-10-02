from pathlib import Path

from scripts.paths import REPO_ROOT, resolve_repo_path


def test_repo_root_is_portable():
    assert (REPO_ROOT / "SKILL.md").is_file()
    assert "paper2wechat" in REPO_ROOT.name


def test_resolve_repo_path_stays_inside_repo():
    candidate = resolve_repo_path("themes", "bytedance.json")
    assert candidate.relative_to(REPO_ROOT) == Path("themes") / "bytedance.json"
