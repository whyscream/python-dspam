from abc import ABC

from dspam.settings import TokenizerSettings


class Tokenizer(ABC):
    API_VERSION: str

    def __init__(self, settings: TokenizerSettings):
        self.settings = settings

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
        for char in self.settings.delimiters:
            content = content.replace(char, " ")
        return content.split()
