import os
import pathlib

import pytest
from anyio import wrap_file

from dspam.settings import ParserSettings

from dspam_plugin_email.parse import EmailParser, EmailParserSettings


@pytest.fixture(autouse=True)
def empty_config(tmp_path, monkeypatch):
    """Set the default config root to an empty directory."""
    for env_var in os.environ.keys():
        if env_var.startswith("DSPAM_"):
            monkeypatch.delenv(env_var, raising=False)

    config_path = tmp_path / ".config"
    data_path = tmp_path / ".data"
    monkeypatch.setenv("XDG_CONFIG_HOME", str(config_path))
    monkeypatch.setenv("XDG_DATA_HOME", str(data_path))
    return config_path


@pytest.fixture
def email_parser():
    settings = ParserSettings()
    settings.plugin_settings = EmailParserSettings()
    return EmailParser(settings)


@pytest.fixture
def assets():
    """Return the test assets directory"""
    return pathlib.Path(__file__).parent / "assets"


@pytest.fixture
async def mf(assets):
    """Factory to generate message objets from assets."""

    async def message_factory(asset_name: str):
        asset_path = assets / asset_name
        fp = asset_path.open()
        return wrap_file(fp)

    return message_factory


@pytest.fixture
async def message(mf):
    yield await mf("spam-plaintext.eml")
