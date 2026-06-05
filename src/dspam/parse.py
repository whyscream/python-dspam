from abc import ABC, abstractmethod
from dataclasses import dataclass

from anyio import AsyncFile

from dspam.settings import ParserSettings


@dataclass
class ParseResult:
    content: str
    metadata: dict[str, str]


class Parser(ABC):
    API_VERSION: str

    def __init__(self, settings: ParserSettings):
        self.settings = settings

    @abstractmethod
    async def __call__(self, fp: AsyncFile) -> ParseResult:
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(API_VERSION={self.API_VERSION})"


class PlainTextParser(Parser):
    """
    A simple parser that reads the input text file and returns its content.
    """

    API_VERSION: str = "1.0"

    async def __call__(self, fp: AsyncFile) -> ParseResult:
        content = await fp.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        return ParseResult(content=content, metadata={})
