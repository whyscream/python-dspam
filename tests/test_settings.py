# SPDX-License-Identifier: BSD-3-Clause

import pytest
from pydantic import ValidationError

from dspam.settings import Settings


@pytest.fixture
def test_settings_defaults():
    settings = Settings()
    assert settings.log_level == "WARNING"
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


def test_settings_from_config_file(empty_config, monkeypatch):
    config_path = empty_config / "python-dspam/config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text("""
    [dspam]
    log_level = "CRITICAL"
    [dspam.parser]
    plugin = "foo"
    """)

    monkeypatch.setitem(Settings.model_config, "toml_file", config_path)

    settings = Settings()
    assert settings.log_level == "CRITICAL"
    assert settings.parser.plugin == "foo"


def test_settings_env_overrides_file(empty_config, monkeypatch):
    config_path = empty_config / "python-dspam/config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text("""
    [dspam.parser]
    plugin = "from-toml"
    """)

    monkeypatch.setenv("DSPAM_PARSER_PLUGIN", "from-env")

    settings = Settings()
    assert settings.parser.plugin == "from-env"
