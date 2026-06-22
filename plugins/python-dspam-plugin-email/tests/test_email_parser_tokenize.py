# SPDX-License-Identifier: BSD-3-Clause

from dspam.settings import TokenizerSettings
from dspam.tokenize import WordTokenizer


async def test_tokenize_email_words(email_parser, message):
    tokenizer = WordTokenizer(TokenizerSettings())

    result = await email_parser(message)
    tokens = await tokenizer(result.content, result.metadata)
    assert "Received*spamfilter.example.org" in tokens
    assert "Received*IPv6:2a01:518:1:42:8::133" in tokens
    assert "Received*21:33:25" in tokens
    assert "Received*bigdog.frenkelfirm.com" in tokens


async def test_tokenize_unicode(email_parser, mf):
    tokenizer = WordTokenizer(TokenizerSettings())

    message = await mf("spam-html-utf8-zh-cn.eml")
    result = await email_parser(message)
    tokens = await tokenizer(result.content, result.metadata)

    assert "Subject*可能的非本人操作请立即完成核验" in tokens, (
        "Token from Subject header should contain original unicode chars"
    )
    assert "您的邮箱账号" in tokens, "Token from message body should contain original unicode chars"
