import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_formatter_help_keeps_every_legacy_option():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "format.py"), "--help"],
        cwd=str(ROOT),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=True,
    )
    for flag in (
        "--input", "--theme", "--vault-root", "--output", "--no-open",
        "--gallery", "--recommend", "--format", "--smart", "--font-size",
    ):
        assert flag in result.stdout


def test_punctuation_and_latex_helpers_keep_their_cli():
    for script, flags in (
        ("zh_punctuation_fix.py", ("--write", "--check")),
        ("latex2img.py", ("--output", "--image-dir")),
    ):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / script), "--help"],
            cwd=str(ROOT),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=True,
        )
        for flag in flags:
            assert flag in result.stdout
