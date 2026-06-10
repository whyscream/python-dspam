import pathlib

import pytest
from anyio import wrap_file

from dspam.parse import ParserSettings
from dspam_plugin_email.parse import EmailParser


@pytest.fixture
def assets():
    """Return the test assets directory"""
    return pathlib.Path(__file__).parent / "assets"


@pytest.fixture
async def message(assets):
    message_path = assets / "spam-plaintext.eml"
    with message_path.open() as fp:
        yield wrap_file(fp)


async def test_parse_email(message):
    parser = EmailParser(ParserSettings())
    result = await parser(message)
    assert list(result.metadata.keys()) == [
        "Return-Path",
        "Delivered-To",
        "Received",
        "X-Virus-Scanned",
        "Reply-To",
        "From",
        "Subject",
        "Date",
        "MIME-Version",
        "Content-Type",
        "Content-Transfer-Encoding",
        "X-Priority",
        "X-MSMail-Priority",
        "X-Mailer",
        "X-MimeOLE",
        "Received-SPF",
        "X-SPF-Result",
        "Authentication-Results",
    ]
    assert result.content is not None
    # assert result.content.startswith("Hello,")
