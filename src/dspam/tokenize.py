from abc import ABC, abstractmethod
from typing import ClassVar

from dspam.types import Metadata, TokenList

from dspam.settings import TokenizerSettings


class Tokenizer(ABC):
    API_VERSION: ClassVar[str]

    def __init__(self, settings: TokenizerSettings) -> None:
        self.settings = settings

    @abstractmethod
    async def __call__(self, content: str, metadata: Metadata) -> list[str]:
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(API_VERSION={self.API_VERSION})"


class WordTokenizer(Tokenizer):
    """
    A simple tokenizer that splits the input text into words based on whitespace and punctuation.

    It removes all punctuation from the input text.
    """

    API_VERSION = "1.0"

    METADATA_IGNORE_DELIMITERS: str = ".:"
    """The delimiters to filter from the default set when tokenizing metadata values."""

    METADATA_TOKEN_SEPARATOR: str = "*"
    """The separator that is used when composing key-value tokens from metadata."""

    async def __call__(self, content: str, metadata: Metadata) -> TokenList:
        """Tokenize content and metadata into words based on whitespace and punctuation."""
        content_tokens = self.tokenize_content(content)
        metadata_tokens = self.tokenize_metadata(metadata)
        return content_tokens + metadata_tokens

    def tokenize_content(self, content: str, ignore_delimiters: str = "") -> TokenList:
        """Generate a list of word tokens from the content string."""
        for char in self.settings.delimiters:
            if char not in ignore_delimiters:
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
                value_tokens = self.tokenize_content(
                    value, self.METADATA_IGNORE_DELIMITERS
                )
                metadata_tokens.extend(self.make_metadata_token(key, value_tokens))

            elif isinstance(value, list):
                for item in value:
                    value_tokens = self.tokenize_content(item)
                    metadata_tokens.extend(self.make_metadata_token(key, value_tokens))

        return metadata_tokens

    def make_metadata_token(self, key: str, value_tokens: TokenList) -> TokenList:
        return [
            f"{key}{self.METADATA_TOKEN_SEPARATOR}{token}" for token in value_tokens
        ]
