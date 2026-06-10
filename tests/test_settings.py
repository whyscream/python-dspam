import pytest
from pydantic import ValidationError

from dspam.settings import Settings


def test_settings_defaults():
    settings = Settings()
    assert settings.log_level == "INFO"
    assert settings.parser.plugin == "plaintext"


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("DSPAM_LOG_LEVEL", "CRITICAL")
    monkeypatch.setenv("DSPAM_PARSER_PLUGIN", "foo")

    settings = Settings()
    assert settings.log_level == "CRITICAL"
    assert settings.parser.plugin == "foo"


def test_settings_validate(monkeypatch):
    monkeypatch.setenv("DSPAM_LOG_LEVEL", "INVALID")

    with pytest.raises(ValidationError):
        Settings()


def test_settings_from_toml_config(tmp_path, monkeypatch):
    config_path = tmp_path / "python-dspam/config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text("""
    [dspam]
    log_level = "CRITICAL"
    [dspam.parser]
    plugin = "foo"
    """)

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    settings = Settings()
    assert settings.log_level == "CRITICAL"
    assert settings.parser.plugin == "foo"


def test_settings_env_overrides_file(tmp_path, monkeypatch):
    config_path = tmp_path / "python-dspam/config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text("""
    [dspam.parser]
    plugin = "from-toml"
    """)

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    monkeypatch.setenv("DSPAM_PARSER_PLUGIN", "from-env")

    settings = Settings()
    assert settings.parser.plugin == "from-env"
