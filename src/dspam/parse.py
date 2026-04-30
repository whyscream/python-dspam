from typing import TextIO


class BaseParser:
    def __init__(self, fp: TextIO) -> None:
        self.fp = fp

    async def __call__(self, *args, **kwargs) -> tuple[str, dict[str, str]]:
        raise NotImplementedError("Subclasses must implement the __call__ method.")


class PlainTextParser(BaseParser):
    """
    A simple parser that reads the input text file and returns its content.

    No metadata is retrieved in this implementation, but the method signature allows for future extensions where metadata can be extracted from the file.
    """

    async def __call__(self, *args, **kwargs) -> tuple[str, dict[str, str]]:
        content = self.fp.read()
        return content, {}
