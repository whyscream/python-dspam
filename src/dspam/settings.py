import os
import pathlib
from abc import ABC
from functools import cached_property

from pydantic import BaseModel, computed_field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from dspam.plugins import PluginManager
from dspam.types import LogLevel


def get_config_root() -> pathlib.Path:
    """Return the path to the root of the configuration directory."""
    xdg_config_home = os.getenv("XDG_CONFIG_HOME", "~/.config")
    return pathlib.Path(xdg_config_home).expanduser().resolve() / "python-dspam"


def get_config_file() -> pathlib.Path | None:
    """Return the path to the configuration file if it exists, otherwise None."""
    config_file = get_config_root() / "config.toml"
    if config_file.is_file():
        return config_file
    return None


def get_plugin_settings(group_name: str, plugin_name: str) -> type[BaseSettings] | None:
    from dspam.di import provider

    pm = provider.get(PluginManager)
    settings_class = pm.get_plugin_settings(group_name, plugin_name)
    return settings_class


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
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            TomlConfigSettingsSource(settings_cls),
        )


class ParserSettings(BaseParserSettings, BaseSettings):
    # TODO: Remove type ignore after release of: https://github.com/pydantic/pydantic-settings/pull/882
    model_config = SettingsConfigDict(  # type: ignore[typeddict-unknown-key, unused-ignore]
        env_prefix="DSPAM_PARSER_",
        env_nested_delimiter="_",
        env_nested_max_split=1,
        extra="ignore",
        polymorphic_serialization=True,
        toml_file=get_config_file(),
        toml_table_header=("dspam", "parser"),
    )

    plugin: str = "plaintext"
    """The plugin to use for parsing."""


class TokenizerSettings(BaseModel):
    plugin: str = "word"
    """The plugin to use for tokenization."""

    delimiters: str = '.,!?;:"@()[]{}<>=*/\\'
    """The list of delimiters that a tokenizer uses to separate content into basic word-tokens."""

    @computed_field(exclude_if=lambda x: x is None)  # type: ignore[prop-decorator]
    @cached_property
    def plugin_settings(self) -> type[BaseSettings] | None:
        settings = get_plugin_settings(PluginManager.TOKENIZER, self.plugin)
        return settings


class StorageSettings(BaseModel):
    plugin: str = "json"
    """The plugin to use for storing data."""

    @computed_field(exclude_if=lambda x: x is None)  # type: ignore[prop-decorator]
    @cached_property
    def plugin_settings(self) -> type[BaseSettings] | None:
        settings = get_plugin_settings(PluginManager.STORAGE, self.plugin)
        return settings


class ClassifierSettings(BaseModel):
    plugin: str = "simple"
    """The plugin to use for classification."""

    @computed_field(exclude_if=lambda x: x is None)  # type: ignore[prop-decorator]
    @cached_property
    def plugin_settings(self) -> type[BaseSettings] | None:
        settings = get_plugin_settings(PluginManager.CLASSIFIER, self.plugin)
        return settings


class TrainerSettings(BaseModel):
    plugin: str = "simple"
    """The plugin to use for training."""

    @computed_field(exclude_if=lambda x: x is None)  # type: ignore[prop-decorator]
    @cached_property
    def plugin_settings(self) -> type[BaseSettings] | None:
        settings = get_plugin_settings(PluginManager.TRAINER, self.plugin)
        return settings


class Settings(BaseParserSettings, BaseSettings):
    # TODO: Remove type ignore after release of: https://github.com/pydantic/pydantic-settings/pull/882
    model_config = SettingsConfigDict(  # type: ignore[typeddict-unknown-key, unused-ignore]
        env_prefix="DSPAM_",
        env_nested_delimiter="_",
        env_nested_max_split=1,
        extra="ignore",
        polymorphic_serialization=True,
        toml_file=get_config_file(),
        toml_table_header=("dspam",),
    )

    log_level: LogLevel = "WARNING"
    """The log level to use."""

    # Nested settings
    parser: ParserSettings = ParserSettings()
    tokenizer: TokenizerSettings = TokenizerSettings()
    storage: StorageSettings = StorageSettings()
    classifier: ClassifierSettings = ClassifierSettings()
    trainer: TrainerSettings = TrainerSettings()
