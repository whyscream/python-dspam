# SPDX-License-Identifier: BSD-3-Clause

import logging
import random
from abc import ABC, abstractmethod

from dspam import IS_INNOCENT, IS_SPAM, IS_UNKNOWN
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

    async def log_debug_tokens(self, tokens: list[str], verdict: str, debug_token_count: int = 0) -> None:
        """
        Utility method to log some tokens for debugging purposes.

        From the list of passed tokens, it will log up to `debug_token_count` tokens at level DEBUG,
        along with their verdict and token data. The token data is retrieved from the storage.
        """
        debug_token_count = max(debug_token_count, 0)
        token_count = len(tokens)
        tokens = random.sample(tokens, min(debug_token_count, token_count))  # noqa: S2245 non-cryptographic random sampling is fine for logging
        tokens_data = await self.storage.get_tokens(tokens)
        for token in tokens:
            token_data = tokens_data.get(token)
            if token_data:
                logger.debug(f"Token: {verdict=} {token_data}")
            else:
                logger.debug(f"Token: {verdict=} '{token}'")


class DummyClassifier(Classifier):
    """
    A dummy classifier that classifies a message as spam if it finds the word "spam" in any of its tokens,
    and as innocent otherwise.
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

    DEBUG_TOKEN_COUNT: int = 10
    """
    The number of tokens to log for debugging purposes.

    The tokens are logged at level DEBUG. For each verdict (innocent, ham), this number of tokens will be logged.
    """

    async def __call__(self, tokens: list[str]) -> str:
        spam_tokens = []
        innocent_tokens = []
        unknown_tokens = []

        tokens_data = await self.storage.get_tokens(tokens)
        for token in tokens:
            token_data = tokens_data.get(token)
            await self.storage.store_token_seen(token)
            if token_data is None:
                unknown_tokens.append(token)
            elif token_data.spam_hits > token_data.innocent_hits:
                spam_tokens.append(token)
            else:
                innocent_tokens.append(token)

        # Log some tokens for debugging purposes
        await self.log_debug_tokens(spam_tokens, IS_SPAM, self.DEBUG_TOKEN_COUNT)
        await self.log_debug_tokens(innocent_tokens, IS_INNOCENT, self.DEBUG_TOKEN_COUNT)
        await self.log_debug_tokens(unknown_tokens, IS_UNKNOWN, self.DEBUG_TOKEN_COUNT)

        spam_count = len(spam_tokens)
        innocent_count = len(innocent_tokens)
        unknown_count = len(unknown_tokens)

        logger.info(f"Classifier token results: spam={spam_count}, innocent={innocent_count}, unknown={unknown_count}")
        if spam_count > innocent_count:
            return IS_SPAM
        else:
            return IS_INNOCENT
