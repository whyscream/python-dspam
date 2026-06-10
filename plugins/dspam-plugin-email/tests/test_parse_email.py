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


async def test_parse_email_headers(message):
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
    assert result.metadata["From"] == "Mary Benysek <workroom@frenkelfirm.com>", (
        "From header should be parsed correctly"
    )
    assert result.metadata["Subject"] == "I saw your name on the list", (
        "Single line subject should be parsed correctly"
    )

    received = result.metadata["Received"]
    assert isinstance(received, list), "Received should be a list of multiple headers"
    assert len(received) == 5, "Received should be a list of five headers"


async def test_parse_email_body(message):
    parser = EmailParser(ParserSettings())
    result = await parser(message)
    assert result.content.splitlines()[0] == "Hello,"
    assert "Subject: I saw your name on the list" not in result.content
    assert "Return-Path:" not in result.content
    assert "Thank you & God bless you." in result.content
