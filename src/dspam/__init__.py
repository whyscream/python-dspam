import importlib.metadata
from typing import Literal

__version__ = importlib.metadata.version("python-dspam")

# Some constants used throughout the application
IS_HAM: str = "ham"
IS_SPAM: str = "spam"


# Some useful types for annotations
Verdict = Literal["ham", "spam"]
