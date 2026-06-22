# SPDX-License-Identifier: BSD-3-Clause

import io

import pytest
from anyio import wrap_file
from dspam_plugin_email.parse import EmailParser, EmailParserSettings

from dspam.exceptions import DspamParseError


async def test_parse_email_headers(email_parser, message):
    result = await email_parser(message)
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
    assert result.metadata["Subject"] == "I saw your name on the list", "Single line subject should be parsed correctly"

    received = result.metadata["Received"]
    assert isinstance(received, list), "Received should be a list of multiple headers"
    assert len(received) == 5, "Received should be a list of five headers"


async def test_parse_email_body(email_parser, message):
    result = await email_parser(message)
    assert result.content.splitlines()[0] == "Hello,"
    assert "Subject: I saw your name on the list" not in result.content
    assert "Return-Path:" not in result.content
    assert "Thank you & God bless you." in result.content


async def test_parse_email_error(email_parser):
    """Test that parsing a non-email file raises an error."""
    with io.BytesIO(b"no text") as fp:
        async_fp = wrap_file(fp)

        with pytest.raises(DspamParseError, match="Failed to parse email"):
            await email_parser(async_fp)


async def test_parse_email_multipart_mime_should_prefer_html(mf, email_parser):
    mime_message = await mf("multipart-mime.eml")
    result = await email_parser(mime_message)
    assert result.content.strip() == "this is the body html", (
        "The HTML body should be preferred over the plain text body"
    )
    assert "Subject: Multipart MIME Email" not in result.content


async def test_parse_email_mime_html_only(mf, email_parser):
    mime_message = await mf("mime-html-only.eml")
    result = await email_parser(mime_message)
    assert result.content.strip() == "this is the body html"


async def test_parse_email_html_only(mf, email_parser):
    html_only_message = await mf("html-only.eml")
    result = await email_parser(html_only_message)
    assert result.content.strip() == "this is the body html"


async def test_parse_email_attachment_error(mf, email_parser):
    attachment_message = await mf("mime-attachment-only.eml")
    with pytest.raises(DspamParseError, match="Email does not contain a supported body part"):
        await email_parser(attachment_message)


async def test_parse_email_ignore_headers(mf, email_parser):
    message = await mf("html-only.eml")
    result = await email_parser(message)
    assert list(result.metadata.keys()) == [
        "From",
        "Date",
        "MIME-Version",
        "Content-Type",
    ]

    # Note: the 'Mime-Version' header is ignored case-insensitively.
    await message.seek(0)
    email_parser = EmailParser(EmailParserSettings(ignore_headers=["Date", "mime-version"]))
    result = await email_parser(message)
    assert list(result.metadata.keys()) == ["From", "Content-Type"]
