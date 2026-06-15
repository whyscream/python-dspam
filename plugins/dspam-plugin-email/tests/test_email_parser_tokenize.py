# SPDX-License-Identifier: BSD-3-Clause

from dspam.tokenize import WordTokenizer
from dspam.settings import TokenizerSettings


async def test_tokenize_email_words(email_parser, message):
    tokenizer = WordTokenizer(TokenizerSettings())

    result = await email_parser(message)
    tokens = await tokenizer(result.content, result.metadata)
    assert "Received*spamfilter.example.org" in tokens
    assert "Received*IPv6:2a01:518:1:42:8::133" in tokens
    assert "Received*21:33:25" in tokens
    assert "Received*bigdog.frenkelfirm.com" in tokens
