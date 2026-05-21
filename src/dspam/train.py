from typing import LiteralString

from dspam import IS_HAM, IS_SPAM
from dspam.storage import BaseStorage


class BaseTrainer:
    API_VERSION: str

    def __init__(
        self,
        tokens: list[str],
        storage: BaseStorage,
        classification: LiteralString[IS_HAM, IS_SPAM],
    ) -> None:
        self.tokens = tokens
        self.storage = storage
        self.classification = classification

    async def __call__(self, *args, **kwargs) -> str:
        raise NotImplementedError("Subclasses must implement the __call__ method.")


class SimpleTrainer(BaseTrainer):
    """
    Train the classifier by adding token hits based on the classification.
    """

    API_VERSION: str = "1.0"

    async def __call__(self, *args, **kwargs) -> None:
        # Update the storage with the new hits
        for token in self.tokens:
            if self.classification == IS_SPAM:
                await self.storage.store_spam_token(token)
            else:
                await self.storage.store_ham_token(token)

        await self.storage.persist()
