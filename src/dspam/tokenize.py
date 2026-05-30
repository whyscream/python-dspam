DELIMITERS = '.,!?;:"@()[]{}<>=*/\\'
"""The list of delimiters that a tokenizer uses to separate content into basic word-tokens."""


class BaseTokenizer:
    API_VERSION: str

    def __init__(self, content: str, metadata: dict[str, str]) -> None:
        self.content = content
        self.metadata = metadata

    async def __call__(self, *args, **kwargs) -> list[str]:
        raise NotImplementedError("Subclasses must implement the __call__ method.")

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(API_VERSION={self.API_VERSION})"


class WordTokenizer(BaseTokenizer):
    """
    A simple tokenizer that splits the input text into words based on whitespace.

    It removes all punctuation from the input text.
    """

    API_VERSION: str = "1.0"

    async def __call__(self, *args, **kwargs) -> list[str]:
        for char in DELIMITERS:
            self.content = self.content.replace(char, " ")
        return self.content.split()
