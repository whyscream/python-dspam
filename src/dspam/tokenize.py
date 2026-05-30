from abc import ABC

DELIMITERS = '.,!?;:"@()[]{}<>=*/\\'
"""The list of delimiters that a tokenizer uses to separate content into basic word-tokens."""


class Tokenizer(ABC):
    API_VERSION: str

    async def __call__(self, content: str, metadata: dict[str, str]) -> list[str]:
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(API_VERSION={self.API_VERSION})"


class WordTokenizer(Tokenizer):
    """
    A simple tokenizer that splits the input text into words based on whitespace and punctuation.

    It removes all punctuation from the input text.
    """

    API_VERSION: str = "1.0"

    async def __call__(self, content: str, metadata: dict[str, str]) -> list[str]:
        for char in DELIMITERS:
            content = content.replace(char, " ")
        return content.split()
