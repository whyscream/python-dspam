import os
import pathlib
from abc import ABC
from functools import cached_property
from typing import cast

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


class BaseDspamSettings(ABC):
    """Base class for settings that supports an optional TOML file"""

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
        settings_sources = [
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        ]

        config_root = get_config_root()
        config_path = config_root / "config.toml"
        print(config_path)
        if config_path.exists():
            # TODO: remove type annotation ignore after release of https://github.com/pydantic/pydantic-settings/pull/882
            toml_settings = TomlConfigSettingsSource(  # type: ignore[call-arg, unused-ignore]
                settings_cls,
                toml_file=config_path,
            )
            settings_sources.append(toml_settings)

        return tuple(settings_sources)


def get_plugin_settings(group_name: str, plugin_name: str) -> type[BaseSettings] | None:
    from dspam.di import provider

    pm = provider.get(PluginManager)
    settings_class = pm.get_plugin_settings(group_name, plugin_name)
    if settings_class:
        return cast(type[BaseSettings], settings_class())
    return None


class ParserSettings(BaseModel):
    plugin: str = "plaintext"
    """The plugin to use for parsing."""

    @computed_field(exclude_if=lambda x: x is None)  # type: ignore[prop-decorator]
    @cached_property
    def plugin_settings(self) -> type[BaseSettings] | None:
        return get_plugin_settings(PluginManager.PARSER, self.plugin)


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


class Settings(BaseDspamSettings, BaseSettings):
    # TODO: remove type annotation after release of: https://github.com/pydantic/pydantic-settings/pull/882
    model_config = SettingsConfigDict(  # type: ignore[typeddict-unknown-key, unused-ignore]
        env_prefix="DSPAM_",
        env_nested_delimiter="_",
        env_nested_max_split=1,
        toml_table_header=("dspam",),
        # TODO: the ignore is needed to allow plugin settings to be read from [dspam.plugin.*.*]
        #  without having a 'plugin' key in this model. Switching to 'forbid' would be better.
        extra="ignore",
    )

    log_level: LogLevel = "WARNING"
    """The log level to use."""

    # Nested settings
    parser: ParserSettings = ParserSettings()
    tokenizer: TokenizerSettings = TokenizerSettings()
    storage: StorageSettings = StorageSettings()
    classifier: ClassifierSettings = ClassifierSettings()
    trainer: TrainerSettings = TrainerSettings()
