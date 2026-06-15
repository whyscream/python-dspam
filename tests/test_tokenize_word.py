# SPDX-License-Identifier: BSD-3-Clause

import pytest

from dspam.settings import TokenizerSettings
from dspam.tokenize import WordTokenizer


@pytest.fixture
def body():
    return "The quick brown fox jumps over the lazy dog"


@pytest.fixture
def multiline_body():
    return """
The quick brown fox
jumps over the
lazy dog
"""


IPV4_RECEIVED_HEADER = """
from bigdog.frenkelfirm.com ([74.113.59.146])
\tby spamfilter.example.org with esmtps  (TLS1.2) tls TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384
\t(Exim 4.94.2)
\t(envelope-from <workroom@frenkelfirm.com>)
\tid 1wUrL8-002KEb-CU
\tfor recipient@example.org; Wed, 03 Jun 2026 21:33:23 +0200
"""

IPV6_RECEIVED_HEADER = """
Received: from spamfilter.example.org (spamfilter.example.org [IPv6:2a01:518:1:42:8::133])
\tby mail.example.org (Postfix) with ESMTPS id 8B71A3F331
\tfor <recipient@example.org>; Wed,  3 Jun 2026 21:33:25 +0200 (CEST)
"""


async def test_tokenize_sentence(body):
    tokenizer = WordTokenizer(TokenizerSettings())
    tokens = await tokenizer(content=body, metadata={})
    assert tokens == [
        "The",
        "quick",
        "brown",
        "fox",
        "jumps",
        "over",
        "the",
        "lazy",
        "dog",
    ]


async def test_tokenize_with_delimiters():
    body = "The;quick:brown,fox@jumps over\nthe\tlazy dog."
    tokenizer = WordTokenizer(TokenizerSettings())
    tokens = await tokenizer(content=body, metadata={})
    assert tokens == [
        "The",
        "quick",
        "brown",
        "fox",
        "jumps",
        "over",
        "the",
        "lazy",
        "dog",
    ]


async def test_tokenize_multiline(multiline_body):
    tokenizer = WordTokenizer(TokenizerSettings())
    tokens = await tokenizer(content=multiline_body, metadata={})
    assert tokens == [
        "The",
        "quick",
        "brown",
        "fox",
        "jumps",
        "over",
        "the",
        "lazy",
        "dog",
    ]


@pytest.mark.parametrize(
    "metadata, expected",
    [
        ({}, []),
        ({"foo": "bar"}, ["foo*bar"]),
        ({"foo": "with spaces"}, ["foo*with", "foo*spaces"]),
        ({"foo": ["bar", "baz"]}, ["foo*bar", "foo*baz"]),
        (
            {"foo": ["with spaces", "and more spaces"]},
            ["foo*with", "foo*spaces", "foo*and", "foo*more", "foo*spaces"],
        ),
    ],
)
async def test_tokenize_metadata(metadata, expected):
    tokenizer = WordTokenizer(TokenizerSettings())
    tokens = await tokenizer(content="", metadata=metadata)
    assert tokens == expected


async def test_tokenize_email_received_header():
    metadata = {"Received": IPV4_RECEIVED_HEADER}

    tokenizer = WordTokenizer(TokenizerSettings())
    tokens = await tokenizer(content="", metadata=metadata)

    assert "Received*from" in tokens
    assert "Received*bigdog.frenkelfirm.com" in tokens, (
        "Domain name should not be split"
    )
    assert "Received*74.113.59.146" in tokens, "IP address should not be split"

    metadata = {"Received": IPV6_RECEIVED_HEADER}
    tokenizer = WordTokenizer(TokenizerSettings())
    tokens = await tokenizer(content="", metadata=metadata)

    assert "Received*IPv6:2a01:518:1:42:8::133" in tokens
