import importlib.metadata

__version__ = importlib.metadata.version("python-dspam")

# Some constants used throughout the application
IS_HAM: str = "ham"
IS_SPAM: str = "spam"
