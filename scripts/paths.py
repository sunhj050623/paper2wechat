"""Portable repository paths shared by Paper2WeChat scripts."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def resolve_repo_path(*parts: str) -> Path:
    """Resolve a path inside the repository and reject traversal outside it."""
    candidate = REPO_ROOT.joinpath(*parts).resolve()
    try:
        candidate.relative_to(REPO_ROOT)
    except ValueError:
        raise ValueError(f"Path escapes repository: {parts!r}")
    return candidate


def output_root() -> Path:
    return resolve_repo_path("outputs")


def local_config_path() -> Path:
    return resolve_repo_path("config.json")


def ensure_output_dir(slug: str) -> Path:
    if not slug or Path(slug).name != slug or slug in {".", ".."}:
        raise ValueError("slug must be one safe directory name")
    destination = output_root() / slug
    destination.mkdir(parents=True, exist_ok=True)
    return destination
