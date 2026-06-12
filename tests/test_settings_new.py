from abc import ABC
from pathlib import Path

import pytest
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)
from rodi import Container


class BaseParserSettings(ABC):
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """
        Add an optional TOML file to the options for reading configuration. It's read from a file named 'config.toml'
        in the default configuration dir.
        """
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            TomlConfigSettingsSource(settings_cls),
        )


def get_config_file() -> Path | None:
    config_file = Path.cwd() / "new_config.toml"
    if config_file.is_file():
        return config_file

    return None


class NewParserSettings(BaseParserSettings, BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="NEW_PARSER_",
        env_nested_delimiter="_",
        env_nested_max_split=1,
        extra="ignore",
        toml_file=get_config_file(),
        toml_table_header=(
            "new",
            "parser",
        ),
    )

    plugin: str = "default"


class NewEmailParserSettings(NewParserSettings):
    ignore_headers: str = "default"


class NewSettings(BaseParserSettings, BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="NEW_",
        env_nested_delimiter="_",
        env_nested_max_split=1,
        extra="ignore",
        toml_file=get_config_file(),
        toml_table_header=("new",),
    )

    log_level: str = "default"
    parser: NewParserSettings = NewParserSettings()


def test_settings_default():

    settings = NewSettings()
    assert settings.log_level == "default"
    assert settings.parser.plugin == "default"


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("NEW_PARSER_PLUGIN", "email")

    settings = NewSettings()
    assert settings.parser.plugin == "email"


def test_settings_compose_explicit():
    # Compose settings with other class explicitly
    settings = NewSettings(parser=NewEmailParserSettings())
    assert settings.parser.plugin == "default"
    assert settings.parser.ignore_headers == "default"
    assert isinstance(settings.parser, NewEmailParserSettings)


def test_settings_compose_explicit_from_env(monkeypatch):
    monkeypatch.setenv("NEW_PARSER_PLUGIN", "email")
    monkeypatch.setenv("NEW_PARSER_IGNORE_HEADERS", "from-env")
    settings = NewSettings(parser=NewEmailParserSettings())
    assert settings.parser.plugin == "email"
    assert settings.parser.ignore_headers == "from-env"
    assert isinstance(settings.parser, NewEmailParserSettings)


@pytest.fixture
def provider():
    def new_settings_factory() -> NewSettings:
        tmp_settings = NewSettings()
        kwargs = {}
        if tmp_settings.parser.plugin == "email":
            kwargs.update({"parser": NewEmailParserSettings()})

        return NewSettings(**kwargs)

    container = Container()
    container.add_transient_by_factory(new_settings_factory)

    return container.build_provider()


def test_settings_di_defaults(provider):
    settings = provider.get(NewSettings)
    assert settings.parser.plugin == "default"
    with pytest.raises(AttributeError):
        assert settings.parser.ignore_headers


def test_settings_di_from_env(monkeypatch, provider):
    monkeypatch.setenv("NEW_PARSER_PLUGIN", "email")

    settings = provider.get(NewSettings)
    assert settings.parser.plugin == "email"
    assert settings.parser.ignore_headers == "default"


def test_settings_di_from_env_with_plugin_settings(monkeypatch, provider):
    monkeypatch.setenv("NEW_PARSER_PLUGIN", "email")
    monkeypatch.setenv("NEW_PARSER_IGNORE_HEADERS", "from-env")

    di_settings = provider.get(NewSettings)
    assert di_settings.parser.plugin == "email"
    assert di_settings.parser.ignore_headers == "from-env"


def test_settings_from_file(tmp_path, provider):
    config_file = tmp_path / "new_config.toml"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text("""
    [new]
    log_level = "from-config-file"
    [new.parser]
    plugin = "email"
    ignore_headers = "from-config-file"
    """)

    # Patch model_config with the correct config file
    NewSettings.model_config["toml_file"] = config_file
    NewEmailParserSettings.model_config["toml_file"] = config_file

    settings = provider.get(NewSettings)
    assert settings.log_level == "from-config-file"
    assert settings.parser.plugin == "email"
    assert settings.parser.ignore_headers == "from-config-file"


def test_settings_env_overrides_file(tmp_path, provider, monkeypatch):
    config_file = tmp_path / "new_config.toml"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text("""
    [new]
    log_level = "from-config-file"
    [new.parser]
    plugin = "email"
    ignore_headers = "from-config-file"
    """)

    # Patch model_config with the correct config file
    NewSettings.model_config["toml_file"] = config_file
    NewEmailParserSettings.model_config["toml_file"] = config_file

    monkeypatch.setenv("NEW_LOG_LEVEL", "from-env")
    monkeypatch.setenv("NEW_PARSER_PLUGIN", "email")

    settings = provider.get(NewSettings)
    assert settings.log_level == "from-env"
    assert settings.parser.plugin == "email"
    assert settings.parser.ignore_headers == "from-config-file"
