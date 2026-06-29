# SPDX-License-Identifier: BSD-3-Clause

from abc import ABC, abstractmethod

from dspam import IS_SPAM
from dspam.settings import TrainerSettings
from dspam.storage import Storage
from dspam.types import Verdict


class Trainer(ABC):
    API_VERSION: str

    def __init__(self, settings: TrainerSettings, storage: Storage) -> None:
        self.settings = settings
        self.storage = storage

    @abstractmethod
    async def __call__(self, tokens: list[str], classification: Verdict) -> None:
        pass  # pragma: no cover

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(API_VERSION={self.API_VERSION})"  # pragma: no cover


class SimpleTrainer(Trainer):
    """
    Train the classifier by adding token hits based on the classification.
    """

    API_VERSION: str = "1.0"

    async def __call__(self, tokens: list[str], classification: Verdict) -> None:
        # Update the storage with the new hits
        for token in tokens:
            if classification == IS_SPAM:
                await self.storage.store_spam_token(token)
            else:
                await self.storage.store_innocent_token(token)

        await self.storage.persist()
