import pytest

from dspam.settings import TokenizerSettings
from dspam.tokenize import WordTokenizer


@pytest.fixture
def body():
    return "The quick brown fox jumps over the lazy dog"


@pytest.mark.asyncio
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


@pytest.mark.asyncio
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
