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

import orjson
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import aiofiles


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

    async def store_spam_token(self, token: str) -> None:
        """
        Add a spam token to the storage.

        This method may keep the data in memory, use persist() to save.
        """
        ...

    async def store_ham_token(self, token: str) -> None:
        """
        Add a ham token to the storage.

        This method may keep the data in memory, use persist() to save.
        """
        ...

    async def persist(self):
        """Persist all unsaved data to the storage backend."""
        ...


class JSONStorage(BaseStorage):
    API_VERSION = "1.0"

    data: dict[str, TokenData]
    path: Path

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    async def open(self):
        if hasattr(self, "data"):
            return

        try:
            async with aiofiles.open(self.path, "rb") as f:
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

        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {}
        for token, token_data in self.data.items():
            data[token] = asdict(token_data)
        async with aiofiles.open(self.path, "wb") as f:
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
