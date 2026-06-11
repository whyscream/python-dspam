import os
import pathlib

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from dspam.types import LogLevel


def get_config_root() -> pathlib.Path:
    """Return the path to the root of the configuration directory."""
    xdg_config_home = os.getenv("XDG_CONFIG_HOME", "~/.config")
    return pathlib.Path(xdg_config_home).expanduser().resolve() / "python-dspam"


class ParserSettings(BaseModel):
    plugin: str = "plaintext"
    """The plugin to use for parsing."""


class TokenizerSettings(BaseModel):
    plugin: str = "word"
    """The plugin to use for tokenization."""

    delimiters: str = '.,!?;:"@()[]{}<>=*/\\'
    """The list of delimiters that a tokenizer uses to separate content into basic word-tokens."""


class StorageSettings(BaseModel):
    plugin: str = "json"
    """The plugin to use for storing data."""


class ClassifierSettings(BaseModel):
    plugin: str = "simple"
    """The plugin to use for classification."""


class TrainerSettings(BaseModel):
    plugin: str = "simple"
    """The plugin to use for training."""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DSPAM_", env_nested_delimiter="_", env_nested_max_split=1
    )

    log_level: LogLevel = "WARNING"
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
        if config_path.exists():
            # TODO: remove type annotation ignore after release of https://github.com/pydantic/pydantic-settings/pull/882
            toml_settings = TomlConfigSettingsSource(  # type: ignore[call-arg, unused-ignore]
                settings_cls, toml_file=config_path, toml_table_header=("dspam",)
            )
            settings_sources.append(toml_settings)

        return tuple(settings_sources)
