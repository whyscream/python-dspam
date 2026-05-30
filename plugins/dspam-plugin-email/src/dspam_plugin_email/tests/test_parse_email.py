import io

import pytest
from anyio import wrap_file

from dspam_plugin_email.parse import EmailParser


@pytest.fixture
def message():
    lines = (
        "From: Bob < bob @ example.com >\n"
        "To: Alice < alice @ example.com >\n"
        "Subject: Test\n"
        "Date: Wed, 1 Jan 2020 12:00:00 +0000\n"
        "\n"
        "Hi Alice, \n"
        "\n"
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n"
    )
    file = io.StringIO(lines)
    return wrap_file(file)


@pytest.mark.asyncio
async def test_parse_email(message):
    parser = EmailParser()
    result = await parser(message)
    assert list(result.metadata.keys()) == ["From", "To", "Subject", "Date"]
    assert result.content is not None
