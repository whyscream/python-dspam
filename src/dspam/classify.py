class BaseClassifier:
    IS_SPAM = "spam"
    IS_HAM = "ham"

    def __init__(self, tokens: list[str]) -> None:
        self.tokens = tokens

    async def __call__(self, *args, **kwargs) -> str:
        raise NotImplementedError("Subclasses must implement the __call__ method.")


class DummyClassifier(BaseClassifier):
    """
    A dummy classifier that classifies a message as spam if it finds the word "spam" in any of its tokens, and as ham otherwise.
    """

    async def __call__(self, *args, **kwargs) -> str:
        for token in self.tokens:
            if "spam" in token:
                return self.IS_SPAM
        return self.IS_HAM
