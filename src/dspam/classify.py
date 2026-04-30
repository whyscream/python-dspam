class BaseClassifier:
    API_VERSION: str

    IS_SPAM: str = "spam"
    IS_HAM: str = "ham"

    def __init__(self, tokens: list[str]) -> None:
        self.tokens = tokens

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
                return self.IS_SPAM
        return self.IS_HAM
