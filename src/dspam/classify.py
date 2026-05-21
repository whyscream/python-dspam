from dspam import IS_HAM, IS_SPAM
from dspam.storage import BaseStorage


class BaseClassifier:
    API_VERSION: str

    def __init__(self, tokens: list[str], storage: BaseStorage) -> None:
        self.tokens = tokens
        self.storage = storage

    async def __call__(self, *args, **kwargs) -> str:
        raise NotImplementedError("Subclasses must implement the __call__ method.")


class DummyClassifier(BaseClassifier):
    """
    A dummy classifier that classifies a message as spam if it finds the word "spam" in any of its tokens, and as ham otherwise.
    """

    API_VERSION: str = "1.0"

    async def __call__(self, *args, **kwargs) -> str:
        for token in self.tokens:
            if "spam" in token:
                return IS_SPAM
        return IS_HAM


class SimpleClassifier(BaseClassifier):
    """
    A simple classifier that simply compares the token counts from the storage.
    """

    API_VERSION: str = "1.0"

    async def __call__(self, *args, **kwargs) -> str:
        token_results = []
        for token in self.tokens:
            token_data = await self.storage.get_token(token)
            if token_data is None:
                continue
            if token_data.spam_hits > token_data.ham_hits:
                token_results.append(IS_SPAM)
            elif token_data.spam_hits < token_data.ham_hits:
                token_results.append(IS_HAM)

        if token_results.count(IS_SPAM) > token_results.count(IS_HAM):
            return IS_SPAM
        else:
            return IS_HAM
