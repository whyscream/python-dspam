import importlib.metadata

__version__ = importlib.metadata.version("python-dspam")

# Some constants used throughout the application
IS_INNOCENT: str = "innocent"
IS_SPAM: str = "spam"
