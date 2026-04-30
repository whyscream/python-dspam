class BaseTokenizer:
    API_VERSION: str

    def __init__(self, content: str, metadata: dict[str, str]) -> None:
        self.content = content
        self.metadata = metadata

    async def __call__(self, *args, **kwargs) -> list[str]:
        raise NotImplementedError("Subclasses must implement the __call__ method.")


class WordTokenizer(BaseTokenizer):
    """
    A simple tokenizer that splits the input text into words based on whitespace.

    It removes all punctuation from the input text.
    """

    API_VERSION: str = "1.0"

    async def __call__(self, *args, **kwargs) -> list[str]:
        for char in '.,!?;:"()[]{}<>=*/\\':
            self.content = self.content.replace(char, "")
        return self.content.split()
