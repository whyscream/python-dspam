import os
from pathlib import Path as SyncPath
from typing import Literal

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


def get_config_root() -> SyncPath:
    """Return the path to the root of the configuration directory."""
    xdg_config_home = os.getenv("XDG_CONFIG_HOME", "~/.config")
    return SyncPath(xdg_config_home).expanduser().resolve() / "python-dspam"


class ParserSettings(BaseSettings):
    plugin: str = "plaintext"
    """The plugin to use for parsing."""


class TokenizerSettings(BaseSettings):
    plugin: str = "word"
    """The plugin to use for tokenization."""

    delimiters: str = '.,!?;:"@()[]{}<>=*/\\'
    """The list of delimiters that a tokenizer uses to separate content into basic word-tokens."""


class StorageSettings(BaseSettings):
    pass


class ClassifierSettings(BaseSettings):
    pass


class TrainerSettings(BaseSettings):
    pass


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DSPAM_", env_nested_delimiter="_")

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "WARNING"
    """The log level to use."""

    # Nested settings
    parser: ParserSettings = ParserSettings()
    tokenizer: TokenizerSettings = TokenizerSettings()
    storage: StorageSettings = StorageSettings()
    classifier: ClassifierSettings = ClassifierSettings()
    trainer: TrainerSettings = TrainerSettings()

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
        Add a TOML file to the options for reading configuration. It's read from a file named 'config.toml'
        in the default configuration dir.
        """
        config_root = get_config_root()
        config_path = config_root / "config.toml"
        toml_settings = TomlConfigSettingsSource(
            settings_cls, toml_file=config_path, toml_table_header=("dspam",)
        )
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            toml_settings,
        )
