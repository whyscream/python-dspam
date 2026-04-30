from typing import TextIO


class BaseParser:
    API_VERSION: str

    def __init__(self, fp: TextIO) -> None:
        self.fp = fp

    async def __call__(self, *args, **kwargs) -> tuple[str, dict[str, str]]:
        raise NotImplementedError("Subclasses must implement the __call__ method.")


class PlainTextParser(BaseParser):
    """
    A simple parser that reads the input text file and returns its content.

    No metadata is retrieved in this implementation, but the method signature allows for future extensions where metadata can be extracted from the file.
    """

    API_VERSION: str = "1.0"

    async def __call__(self, *args, **kwargs) -> tuple[str, dict[str, str]]:
        content = self.fp.read()
        return content, {}
