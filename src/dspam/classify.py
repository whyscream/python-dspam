# SPDX-License-Identifier: BSD-3-Clause

import logging
from abc import ABC, abstractmethod

from dspam import IS_INNOCENT, IS_SPAM
from dspam.settings import ClassifierSettings
from dspam.storage import Storage

logger = logging.getLogger(__name__)


class Classifier(ABC):
    API_VERSION: str

    def __init__(self, settings: ClassifierSettings, storage: Storage) -> None:
        self.settings = settings
        self.storage = storage

    @abstractmethod
    async def __call__(self, tokens: list[str]) -> str:
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(API_VERSION={self.API_VERSION})"


class DummyClassifier(Classifier):
    """
    A dummy classifier that classifies a message as spam if it finds the word "spam" in any of its tokens, and as innocent otherwise.
    """

    API_VERSION: str = "1.0"

    async def __call__(self, tokens: list[str]) -> str:
        for token in tokens:
            if "spam" in token:
                return IS_SPAM
        return IS_INNOCENT


class SimpleClassifier(Classifier):
    """
    A simple classifier that simply compares the token counts from the storage.
    """

    API_VERSION: str = "1.0"

    async def __call__(self, tokens: list[str]) -> str:
        token_results = []
        for token in tokens:
            token_data = await self.storage.get_token(token)
            if token_data is None:
                continue
            if token_data.spam_hits > token_data.innocent_hits:
                token_results.append(IS_SPAM)
            elif token_data.spam_hits < token_data.innocent_hits:
                token_results.append(IS_INNOCENT)

        spam_count = token_results.count(IS_SPAM)
        innocent_count = token_results.count(IS_INNOCENT)
        logger.info(
            "Classifier token results: %d spam, %d innocent", spam_count, innocent_count
        )
        if spam_count > innocent_count:
            return IS_SPAM
        else:
            return IS_INNOCENT
