from anyio import AsyncFile


class BaseParser:
    API_VERSION: str

    def __init__(self, fp: AsyncFile) -> None:
        self.fp = fp

    async def __call__(self, *args, **kwargs) -> tuple[str, dict[str, str]]:
        raise NotImplementedError("Subclasses must implement the __call__ method.")

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(API_VERSION={self.API_VERSION})"


class PlainTextParser(BaseParser):
    """
    A simple parser that reads the input text file and returns its content.

    No metadata is retrieved in this implementation, but the method signature allows for future extensions where metadata can be extracted from the file.
    """

    API_VERSION: str = "1.0"

    async def __call__(self, *args, **kwargs) -> tuple[str, dict[str, str]]:
        content = await self.fp.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        return content, {}
