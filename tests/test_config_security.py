import json

from scripts.config import load_config, redact


def test_environment_secret_overrides_local_config(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"wechat": {"app_id": "local-id", "app_secret": "local-secret"}}),
        encoding="utf-8",
    )
    monkeypatch.setenv("WECHAT_APP_ID", "env-id")
    monkeypatch.setenv("WECHAT_APP_SECRET", "env-secret")

    config = load_config(config_path)

    assert config["wechat"]["app_id"] == "env-id"
    assert config["wechat"]["app_secret"] == "env-secret"


def test_redact_removes_values_for_known_secret_keys():
    config = {
        "wechat": {"app_id": "id-value", "app_secret": "secret-value"},
        "smart_api": {"api_key": "key-value"},
    }

    result = redact(
        "id-value secret-value key-value",
        config=config,
    )

    assert all(value not in result for value in ("id-value", "secret-value", "key-value"))
