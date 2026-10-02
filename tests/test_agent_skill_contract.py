from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_skill_is_discoverable_by_claude_code_and_codex_from_one_checkout():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")

    assert "Claude Code" in readme
    assert "Codex" in readme
    assert ".agents/skills/paper2wechat" in readme
    assert ".claude/skills/paper2wechat" in readme
    assert "Use when" in skill.splitlines()[2]
    assert "references/paper-analysis.md" in skill
    assert "references/wechat-formatting.md" in skill


def test_skill_commands_use_the_loaded_skill_root_and_workspace_outputs():
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")

    assert "当前加载的 `SKILL.md`" in skill
    assert "当前项目/工作区" in skill
    assert "{skill-root}/scripts/paper2wechat.py" in skill


def test_full_legacy_formatter_guidance_is_preserved_as_references():
    formatter = (ROOT / "references" / "wechat-formatting.md").read_text(encoding="utf-8")
    obsidian = (ROOT / "references" / "obsidian-layout.md").read_text(encoding="utf-8")

    for feature in ("--gallery", "--recommend", "--smart", "--font-size", "longimage", "history"):
        assert feature in formatter
    assert "内容形态 → 元素选择决策表" in obsidian
