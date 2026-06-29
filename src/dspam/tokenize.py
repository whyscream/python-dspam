# SPDX-License-Identifier: BSD-3-Clause

from abc import ABC, abstractmethod
from typing import ClassVar

import homoglyphs_fork as hg  # type: ignore[import-untyped]
from anyio.functools import lru_cache

from dspam.settings import TokenizerSettings
from dspam.types import Metadata, TokenList


class Tokenizer(ABC):
    API_VERSION: ClassVar[str]

    def __init__(self, settings: TokenizerSettings) -> None:
        self.settings = settings

    @abstractmethod
    async def __call__(self, content: str, metadata: Metadata) -> list[str]:
        pass  # pragma: no cover

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(API_VERSION={self.API_VERSION})"  # pragma: no cover


class WordTokenizer(Tokenizer):
    """
    A simple tokenizer that splits the input text into words based on whitespace and punctuation.

    It removes all punctuation from the input text.
    """

    API_VERSION = "1.0"

    METADATA_IGNORE_DELIMITERS: str = ".:"
    """The delimiters to filter from the default set when tokenizing metadata values."""

    METADATA_TOKEN_SEPARATOR: str = "*"  # noqa: S105
    """The separator that is used when composing key-value tokens from metadata."""

    HOMOGLYPH_IGNORE_DELIMITERS: str = "@"
    """
    The ascii delimiters to filter from the configured delimiters when generating homoglyphs.

    Some delimiters generate homoglyphs that are unwanted because they're too common.
    E.g. the delimiter '@' triggers the regular 'a' character as a homoglyph.
    """

    async def __call__(self, content: str, metadata: Metadata) -> TokenList:
        """Tokenize content and metadata into words based on whitespace and punctuation."""
        metadata_tokens = self.tokenize_metadata(metadata)
        content_tokens = self.tokenize_content(content)
        return metadata_tokens + content_tokens

    def tokenize_content(self, content: str, ignore_delimiters: str = "") -> TokenList:
        """Generate a list of word tokens from the content string."""
        delimiters = "".join([d for d in self.settings.delimiters if d not in ignore_delimiters])
        delimiters += self.get_homoglyph_delimiters(delimiters)

        for char in delimiters:
            content = content.replace(char, " ")
        return content.split()

    def tokenize_metadata(self, metadata: Metadata) -> TokenList:
        """
        Generate a list of word tokens from the metadata dictionary.

        The metadata key is combined with word tokens from the metadata values to add key-value context in the result.
        Word tokenization for metadata ignores a few delimiters to improve handling of email headers, so domain names
        and ip addresses are preserved.
        """
        metadata_tokens = []
        for key, value in metadata.items():
            if isinstance(value, str):
                value_tokens = self.tokenize_content(value, self.METADATA_IGNORE_DELIMITERS)
                metadata_tokens.extend(self.make_metadata_token(key, value_tokens))

            elif isinstance(value, list):
                for item in value:
                    value_tokens = self.tokenize_content(item, self.METADATA_IGNORE_DELIMITERS)
                    metadata_tokens.extend(self.make_metadata_token(key, value_tokens))

        return metadata_tokens

    def make_metadata_token(self, key: str, value_tokens: TokenList) -> TokenList:
        return [f"{key}{self.METADATA_TOKEN_SEPARATOR}{token}" for token in value_tokens]

    @lru_cache(maxsize=128)
    def get_homoglyph_delimiters(self, ascii_delimiters: str) -> str:
        """
        Generate a set of Unicode delimiter variants based on their ascii variants.
        """

        def decode_escaped(char: str) -> str:
            if char.startswith("\\u"):
                return chr(int(char, 16))
            return char

        # Filter out delimiters that we don't want homoglyphs for
        ascii_delimiters = "".join([d for d in ascii_delimiters if d not in self.HOMOGLYPH_IGNORE_DELIMITERS])

        homoglyphs = hg.Homoglyphs()

        unicode_delimiters = []
        for char in ascii_delimiters:
            for homoglyph in homoglyphs.get_combinations(char):
                homoglyph = decode_escaped(homoglyph)
                unicode_delimiters.append(homoglyph)

        return "".join(set(unicode_delimiters))
