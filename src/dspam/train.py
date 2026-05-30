from abc import ABC, abstractmethod
from typing import LiteralString

from dspam import IS_HAM, IS_SPAM
from dspam.storage import Storage


class Trainer(ABC):
    API_VERSION: str

    def __init__(self, storage: Storage) -> None:
        self.storage = storage

    @abstractmethod
    async def __call__(
        self, tokens: list[str], classification: LiteralString[IS_HAM, IS_SPAM]
    ) -> None:
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(API_VERSION={self.API_VERSION})"


class SimpleTrainer(Trainer):
    """
    Train the classifier by adding token hits based on the classification.
    """

    API_VERSION: str = "1.0"

    async def __call__(self, tokens, classification):
        # Update the storage with the new hits
        for token in tokens:
            if classification == IS_SPAM:
                await self.storage.store_spam_token(token)
            else:
                await self.storage.store_ham_token(token)

        await self.storage.persist()
