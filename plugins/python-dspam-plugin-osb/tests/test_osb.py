# SPDX-License-Identifier: BSD-3-Clause

import pytest
from dspam_plugin_osb.osb import OsbTokenizer

from dspam.settings import TokenizerSettings


@pytest.fixture
def content():
    return "The quick brown fox jumps over the lazy dog"


@pytest.fixture
def tokenizer():
    return OsbTokenizer(TokenizerSettings())


def test_osb_tokenize_content_success(tokenizer, content):
    tokens = tokenizer.osb_tokenize_content(content)
    assert "The+#+#+#+jumps" in tokens
    assert "lazy+dog" in tokens
    assert len(tokens) == 5 * 4  # 5 different windows, each window yields 4 tokens


@pytest.mark.parametrize(
    "content_length, num_osb_tokens",
    [
        (5, 4),
        (4, 3),
        (3, 2),
        (2, 1),
        (1, 0),
        (0, 0),
    ],
)
def test_osb_tokenize_content_token_count(content, content_length, tokenizer, num_osb_tokens):
    content = " ".join(content.split()[:content_length])

    tokens = tokenizer.osb_tokenize_content(content)
    assert len(tokens) == num_osb_tokens, f"Expected {num_osb_tokens} OSB tokens, result was: {tokens}"
