"""
Token storage is basically saving each token with 2 counts:
- the number of ham hits
- and the number of spam hits

Additional metadata can be added:
- timestamp of last update (while training)
- timestamp when the token was last seen (while classifying)
- hash of the token, to speed up lookups for large tokens
- token statistics: probablity, ham/spam ratio, etc
"""

import os

import orjson
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from anyio import Path


async def get_storage_root() -> Path:
    """Get the root directory for storage files. This is typically a hidden directory in the user's home directory."""
    xdg_data_home = os.getenv("XDG_DATA_HOME", "~/.local/share")
    return await Path(xdg_data_home).expanduser() / "python-dspam"


@dataclass
class TokenData:
    """Internal token data format."""

    token: str
    token_hash: str = ""
    spam_hits: int = 0
    ham_hits: int = 0
    last_seen: datetime = None
    last_updated: datetime = None

    def add_spam_hit(self):
        self.spam_hits += 1
        self.last_updated = datetime.now(timezone.utc)

    def add_ham_hit(self):
        self.ham_hits += 1
        self.last_updated = datetime.now(timezone.utc)


class BaseStorage:
    API_VERSION: str

    def __str__(self):
        return f"{self.__class__.__name__}(API_VERSION={self.API_VERSION})"

    async def store_spam_token(self, token: str) -> None:
        """
        Add a spam token to the storage.

        This method may keep the data in memory, use persist() to save.
        """
        raise NotImplementedError(
            "Subclasses must implement the store_spam_token method."
        )

    async def store_ham_token(self, token: str) -> None:
        """
        Add a ham token to the storage.

        This method may keep the data in memory, use persist() to save.
        """
        raise NotImplementedError(
            "Subclasses must implement the store_ham_token method."
        )

    async def persist(self):
        """Persist all unsaved data to the storage backend."""
        raise NotImplementedError("Subclasses must implement the persist method.")

    async def get_token(self, token: str) -> TokenData | None:
        """Find a token from the storage."""
        raise NotImplementedError("Subclasses must implement the get_token method.")


class JSONStorage(BaseStorage):
    API_VERSION = "1.0"

    data: dict[str, TokenData]
    path: Path

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def __str__(self):
        return f"{self.__class__.__name__}(API_VERSION={self.API_VERSION}, path={self.path})"

    async def open(self):
        if hasattr(self, "data"):
            return

        try:
            async with await self.path.open("rb") as f:
                raw = await f.read()
                data = orjson.loads(raw)
        except FileNotFoundError:
            data = {}

        self.data = {}
        for token, token_data in data.items():
            self.data[token] = TokenData(**token_data)

    async def persist(self):
        if not hasattr(self, "data"):
            return

        data = {}
        for token, token_data in self.data.items():
            data[token] = asdict(token_data)

        await self.path.parent.mkdir(parents=True, exist_ok=True)
        async with await self.path.open("wb") as f:
            dumped = orjson.dumps(data)
            await f.write(dumped)

    async def store_spam_token(self, token: str) -> None:
        await self.open()

        token_data = self.data.get(token, TokenData(token=token))
        token_data.add_spam_hit()
        self.data[token] = token_data

    async def store_ham_token(self, token: str) -> None:
        await self.open()

        token_data = self.data.get(token, TokenData(token=token))
        token_data.add_ham_hit()
        self.data[token] = token_data

    async def get_token(self, token: str) -> TokenData | None:
        await self.open()
        return self.data.get(token)
