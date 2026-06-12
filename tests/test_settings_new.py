import os

import pytest
from pydantic import ValidationError
from rodi import Container

from dspam.settings import Settings
from dspam_plugin_email.parse import EmailParserSettings


@pytest.fixture(autouse=True)
def empty_env(mocker):
    mocker.patch.dict(os.environ, clear=True)
    yield


# @pytest.fixture(autouse=True)
# def empty_config_root(tmp_path, monkeypatch, empty_env):
#     """Set up an empty config root"""
#     # TODO: make this work
#     config_root = tmp_path / ".config"
#     config_root.mkdir(parents=True, exist_ok=True)
#     monkeypatch.setenv("XDG_CONFIG_HOME", str(config_root))
#     yield config_root


def test_settings_default():
    settings = Settings()
    assert settings.log_level == "WARNING"
    assert settings.parser.plugin == "plaintext"


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("DSPAM_PARSER_PLUGIN", "email")

    settings = Settings()
    assert settings.parser.plugin == "email"
    with pytest.raises(AttributeError):
        assert settings.parser.ignore_header


def test_settings_validate(monkeypatch):
    monkeypatch.setenv("DSPAM_LOG_LEVEL", "INVALID")

    with pytest.raises(ValidationError):
        Settings()


def test_settings_compose_explicit():
    settings = Settings(parser=EmailParserSettings())
    assert settings.parser.plugin == "plaintext"
    assert settings.parser.ignore_headers == []


def test_settings_compose_explicit_from_env(monkeypatch):
    monkeypatch.setenv("DSPAM_PARSER_PLUGIN", "email")
    monkeypatch.setenv("DSPAM_PARSER_IGNORE_HEADERS", '["from-env"]')
    settings = Settings(parser=EmailParserSettings())
    assert settings.parser.plugin == "email"
    assert settings.parser.ignore_headers == ["from-env"]
    assert isinstance(settings.parser, EmailParserSettings)


@pytest.fixture
def provider():
    def settings_factory() -> Settings:
        tmp_settings = Settings()
        kwargs = {}
        if tmp_settings.parser.plugin == "email":
            kwargs["parser"] = EmailParserSettings()

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
    monkeypatch.setenv("DSPAM_PARSER_PLUGIN", "email")

    settings = provider.get(Settings)
    assert settings.parser.plugin == "email"
    assert settings.parser.ignore_headers == []
    assert isinstance(settings.parser, EmailParserSettings)


def test_provider_settings_from_env_with_plugin_settings(monkeypatch, provider):
    monkeypatch.setenv("DSPAM_PARSER_PLUGIN", "email")
    monkeypatch.setenv("DSPAM_PARSER_IGNORE_HEADERS", '["from-env"]')

    di_settings = provider.get(Settings)
    assert di_settings.parser.plugin == "email"
    assert di_settings.parser.ignore_headers == ["from-env"]


def test_settings_from_file(tmp_path, provider):
    config_file = tmp_path / "config.toml"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text("""
    [dspam]
    log_level = "CRITICAL"
    [dspam.parser]
    plugin = "email"
    ignore_headers = ["from-config-file"]
    """)

    # Patch model_config with the correct config file
    Settings.model_config["toml_file"] = config_file
    EmailParserSettings.model_config["toml_file"] = config_file

    settings = provider.get(Settings)
    assert settings.log_level == "CRITICAL"
    assert settings.parser.plugin == "email"
    assert settings.parser.ignore_headers == ["from-config-file"]


def test_settings_env_overrides_file(tmp_path, provider, monkeypatch):
    config_file = tmp_path / "config.toml"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text("""
    [dspam]
    log_level = "DEBUG"
    [dspam.parser]
    plugin = "email"
    ignore_headers = ["from-config-file"]
    """)

    # Patch model_config with the correct config file
    Settings.model_config["toml_file"] = config_file
    EmailParserSettings.model_config["toml_file"] = config_file

    monkeypatch.setenv("DSPAM_LOG_LEVEL", "CRITICAL")
    monkeypatch.setenv("DSPAM_PARSER_PLUGIN", "email")

    settings = provider.get(Settings)
    assert settings.log_level == "CRITICAL"
    assert settings.parser.plugin == "email"
    assert settings.parser.ignore_headers == ["from-config-file"]
