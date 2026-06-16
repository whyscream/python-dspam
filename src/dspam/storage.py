# SPDX-License-Identifier: BSD-3-Clause

"""
Token storage is basically saving each token with 2 counts:
- the number of innocent hits
- and the number of spam hits

Additional metadata can be added:
- timestamp of last update (while training)
- timestamp when the token was last seen (while classifying)
- hash of the token, to speed up lookups for large tokens
- token statistics: probablity, innocent/spam ratio, etc
"""

import os
import pathlib
from abc import ABC, abstractmethod

import anyio
import orjson
from dataclasses import asdict, dataclass
from datetime import datetime, timezone

from dspam.settings import StorageSettings


def get_storage_root() -> pathlib.Path:
    """Get the root directory for storage files. This is typically a hidden directory in the user's home directory."""
    xdg_data_home = os.getenv("XDG_DATA_HOME", "~/.local/share")
    return pathlib.Path(xdg_data_home).expanduser().resolve() / "python-dspam"


@dataclass
class TokenData:
    """Internal token data format."""

    token: str
    token_hash: str = ""
    spam_hits: int = 0
    innocent_hits: int = 0
    seen_hits: int = 0
    last_seen: datetime | None = None
    last_updated: datetime | None = None

    def __str__(self) -> str:
        return f"'{self.token}' spam_hits={self.spam_hits} innocent_hits={self.innocent_hits}"

    def add_spam_hit(self) -> None:
        self.spam_hits += 1
        self.last_updated = datetime.now(timezone.utc)

    def add_innocent_hit(self) -> None:
        self.innocent_hits += 1
        self.last_updated = datetime.now(timezone.utc)

    def seen(self) -> None:
        self.seen_hits += 1
        self.last_seen = datetime.now(timezone.utc)


class Storage(ABC):
    API_VERSION: str

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(API_VERSION={self.API_VERSION})"

    def __init__(self, settings: StorageSettings, storage_root: pathlib.Path) -> None:
        """Initialize the storage with the given root directory. The storage may create files or directories under this root as needed."""
        self.settings = settings
        self.storage_root = storage_root

    @abstractmethod
    async def store_spam_token(self, token: str) -> None:
        """
        Save a spam token to the storage. This adds new tokens or updates spam count for existing tokens.

        This method may keep the data in memory, use persist() to save.
        """
        pass

    @abstractmethod
    async def store_innocent_token(self, token: str) -> None:
        """
        Save an innocent token to the storage. This adds new tokens or updates innocent count for existing tokens.

        This method may keep the data in memory, use persist() to save.
        """
        pass

    @abstractmethod
    async def store_token_seen(self, token: str) -> None:
        """
        Update the last seen timestamp for the token. This only updates the last seen timestamp for existing tokens, and does not add new tokens.

        This method may keep the data in memory, use persist() to save.
        """
        pass

    @abstractmethod
    async def persist(self) -> None:
        """Persist all unsaved data to the storage backend."""
        pass

    @abstractmethod
    async def get_token(self, token: str) -> TokenData | None:
        """Find a token from the storage."""
        pass


class JSONStorage(Storage):
    API_VERSION = "1.0"

    data: dict[str, TokenData]
    """In-memery version of the stored token data."""
    path: anyio.Path
    """Path to the stored token data."""

    def __init__(self, settings: StorageSettings, storage_root: pathlib.Path) -> None:
        super().__init__(settings, storage_root)
        self.path = anyio.Path(self.storage_root) / "storage.json"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(API_VERSION={self.API_VERSION}, path={self.path})"

    async def open(self) -> None:
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

    async def persist(self) -> None:
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

    async def store_innocent_token(self, token: str) -> None:
        await self.open()

        token_data = self.data.get(token, TokenData(token=token))
        token_data.add_innocent_hit()
        self.data[token] = token_data

    async def store_token_seen(self, token: str) -> None:
        await self.open()

        token_data = self.data.get(token)
        if token_data:
            token_data.seen()
            self.data[token] = token_data

    async def get_token(self, token: str) -> TokenData | None:
        await self.open()
        return self.data.get(token)
