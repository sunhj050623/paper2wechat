"""Local configuration loading with environment-first secrets and diagnostics redaction."""

import json
import os
import re
from pathlib import Path

from scripts.paths import local_config_path


DEFAULTS = {
    "output_dir": "outputs/wechat-format",
    "vault_root": "",
    "image_search_paths": [],
    "settings": {
        "default_theme": "bytedance",
        "auto_open_browser": True,
        "header_author_label": "",
    },
    "wechat": {"app_id": "", "app_secret": "", "author": "Tau Lab"},
    "smart_api": {"base_url": "", "api_key": "", "model": "gpt-4o-mini"},
    "ai": {"url": "", "api_key": "", "model": ""},
}

SECRET_KEYS = {
    "app_id",
    "app_secret",
    "api_key",
    "access_token",
    "token",
    "secret",
}
SECRET_ENV = {
    "WECHAT_APP_ID": ("wechat", "app_id"),
    "WECHAT_APP_SECRET": ("wechat", "app_secret"),
    "SMART_FORMAT_API_KEY": ("smart_api", "api_key"),
    "OPENAI_API_KEY": ("smart_api", "api_key"),
    "SMART_API_KEY": ("smart_api", "api_key"),
    "AI_API_KEY": ("ai", "api_key"),
}


def _merge(base, overlay):
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _merge(base[key], value)
        else:
            base[key] = value
    return base


def _is_placeholder(value):
    if not isinstance(value, str):
        return False
    lowered = value.strip().lower()
    return not lowered or lowered.startswith(
        ("your_", "请填写", "your ", "replace_me", "changeme", "<")
    )


def load_config(config_path=None):
    """Read defaults, local config, then sensitive environment overrides."""
    config = json.loads(json.dumps(DEFAULTS))
    path = Path(config_path) if config_path else local_config_path()
    if path.is_file():
        local = json.loads(path.read_text(encoding="utf-8"))
        _merge(config, local)
    for env_name, (section, key) in SECRET_ENV.items():
        value = os.environ.get(env_name)
        if value and not _is_placeholder(value):
            config.setdefault(section, {})[key] = value
    for section, key in (("wechat", "app_id"), ("wechat", "app_secret"),
                         ("smart_api", "api_key"), ("ai", "api_key")):
        value = config.get(section, {}).get(key)
        if _is_placeholder(value):
            config[section][key] = ""
    return config


def redact(value, config=None):
    """Remove known credentials and token-shaped values from diagnostic text."""
    text = str(value)
    config = config or load_config()
    secrets = set()

    def collect(obj, key=""):
        if isinstance(obj, dict):
            for child_key, child in obj.items():
                collect(child, child_key.lower())
        elif isinstance(obj, (list, tuple)):
            for child in obj:
                collect(child, key)
        elif key in SECRET_KEYS and isinstance(obj, str) and len(obj) >= 4:
            secrets.add(obj)

    collect(config)
    for secret in sorted(secrets, key=len, reverse=True):
        text = text.replace(secret, "[REDACTED]")
    text = re.sub(
        r"(?i)(access_token|appsecret|app_secret|api_key|authorization)"
        r"([=:\s]+)([^&\s,;\"']+)",
        r"\1\2[REDACTED]",
        text,
    )
    return text
