# SPDX-License-Identifier: BSD-3-Clause

from abc import ABC, abstractmethod
from dataclasses import dataclass

from anyio import AsyncFile

from dspam.settings import ParserSettings
from dspam.types import Metadata


@dataclass
class ParseResult:
    content: str
    metadata: Metadata


class Parser(ABC):
    API_VERSION: str

    def __init__(self, settings: ParserSettings):
        """
        Initialize a new Parser

        Args:
            settings: The settings from the [dspam.parser] section of the config.
        """
        self.settings = settings

    @abstractmethod
    async def __call__(self, fp: AsyncFile[str]) -> ParseResult:
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(API_VERSION={self.API_VERSION})"


class PlainTextParser(Parser):
    """
    A simple parser that reads the input text file and returns its content.
    """

    API_VERSION: str = "1.0"

    async def __call__(self, fp: AsyncFile[str]) -> ParseResult:
        content = await fp.read()
        return ParseResult(content=content, metadata={})
