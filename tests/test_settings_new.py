# SPDX-License-Identifier: BSD-3-Clause

import pytest
from pydantic import ValidationError
from rodi import Container

from dspam.settings import ParserSettings, Settings


class CustomParserSettings(ParserSettings):
    """Subclassed ParserSettings, as used in plugins."""

    ignore_headers: list[str] = []


def test_settings_default():
    settings = Settings()
    assert settings.log_level == "WARNING"
    assert settings.parser.plugin == "plaintext"


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("DSPAM_PARSER_PLUGIN", "custom")

    settings = Settings()
    assert settings.parser.plugin == "custom"
    with pytest.raises(AttributeError):
        assert settings.parser.ignore_header


def test_settings_validate(monkeypatch):
    monkeypatch.setenv("DSPAM_LOG_LEVEL", "INVALID")

    with pytest.raises(ValidationError):
        Settings()


def test_settings_compose_explicit():
    settings = Settings(parser=CustomParserSettings())
    assert settings.parser.plugin == "plaintext"
    assert settings.parser.ignore_headers == []


def test_settings_compose_explicit_from_env(monkeypatch):
    monkeypatch.setenv("DSPAM_PARSER_PLUGIN", "custom")
    monkeypatch.setenv("DSPAM_PARSER_IGNORE_HEADERS", '["from-env"]')
    settings = Settings(parser=CustomParserSettings())
    assert settings.parser.plugin == "custom"
    assert settings.parser.ignore_headers == ["from-env"]
    assert isinstance(settings.parser, CustomParserSettings)


@pytest.fixture
def provider():
    def settings_factory() -> Settings:
        tmp_settings = Settings()
        kwargs = {}
        if tmp_settings.parser.plugin == "custom":
            kwargs["parser"] = CustomParserSettings()

        return Settings(**kwargs)

    container = Container()
    container.add_transient_by_factory(settings_factory)

    return container.build_provider()


def test_provider_settings_defaults(provider):
    settings = provider.get(Settings)
    assert settings.parser.plugin == "plaintext"
    with pytest.raises(AttributeError):
        assert settings.parser.ignore_headers


def test_provider_settings_from_env(monkeypatch, provider):
    monkeypatch.setenv("DSPAM_PARSER_PLUGIN", "custom")

    settings = provider.get(Settings)
    assert settings.parser.plugin == "custom"
    assert settings.parser.ignore_headers == []
    assert isinstance(settings.parser, CustomParserSettings)


def test_provider_settings_from_env_with_plugin_settings(monkeypatch, provider):
    monkeypatch.setenv("DSPAM_PARSER_PLUGIN", "custom")
    monkeypatch.setenv("DSPAM_PARSER_IGNORE_HEADERS", '["from-env"]')

    di_settings = provider.get(Settings)
    assert di_settings.parser.plugin == "custom"
    assert di_settings.parser.ignore_headers == ["from-env"]


def test_provider_settings_from_file(empty_config, monkeypatch, provider):
    config_file = empty_config / "config.toml"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text("""
    [dspam]
    log_level = "CRITICAL"
    [dspam.parser]
    plugin = "custom"
    ignore_headers = ["from-config-file"]
    """)

    monkeypatch.setitem(Settings.model_config, "toml_file", config_file)
    monkeypatch.setitem(CustomParserSettings.model_config, "toml_file", config_file)

    settings = provider.get(Settings)
    assert settings.log_level == "CRITICAL"
    assert settings.parser.plugin == "custom"
    assert settings.parser.ignore_headers == ["from-config-file"]


def test_provider_settings_env_overrides_file(tmp_path, provider, monkeypatch):
    config_file = tmp_path / "config.toml"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text("""
    [dspam]
    log_level = "DEBUG"
    [dspam.parser]
    plugin = "email"
    ignore_headers = ["from-config-file"]
    """)

    monkeypatch.setitem(Settings.model_config, "toml_file", config_file)
    monkeypatch.setitem(CustomParserSettings.model_config, "toml_file", config_file)

    monkeypatch.setenv("DSPAM_LOG_LEVEL", "CRITICAL")
    monkeypatch.setenv("DSPAM_PARSER_PLUGIN", "custom")

    settings = provider.get(Settings)
    assert settings.log_level == "CRITICAL"
    assert settings.parser.plugin == "custom"
    assert settings.parser.ignore_headers == ["from-config-file"]
