import pathlib

import pytest
from anyio import wrap_file

from dspam.settings import ParserSettings

from dspam_plugin_email.parse import EmailParser, EmailParserSettings


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
