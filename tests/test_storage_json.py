# SPDX-License-Identifier: BSD-3-Clause

import json
from dataclasses import asdict

import pytest

from dspam.settings import StorageSettings
from dspam.storage import JSONStorage, TokenData


@pytest.fixture
def token():
    yield TokenData(token="token")


async def test_json_storage_open_empty(storage):
    """Test that the storage can be opened and is empty"""
    await storage.open()
    assert storage.data == {}


async def test_json_storage_open_existing(storage, token):
    """Test that the storage can be opened and has data"""
    await storage.path.parent.mkdir(parents=True, exist_ok=True)
    data = {"token": asdict(token)}
    await storage.path.write_text(json.dumps(data))

    await storage.open()
    assert storage.data == {"token": token}


async def test_json_storage_persist(storage):
    """Test that the storage can be persisted"""
    storage.data = {}

    await storage.persist()
    assert await storage.path.is_file()


async def test_json_storage_save_token(storage):
    await storage.store_spam_token("spam-token")
    assert "spam-token" in storage.data
    assert storage.data["spam-token"].spam_hits == 1

    await storage.store_innocent_token("innocent-token")
    assert "innocent-token" in storage.data
    assert storage.data["innocent-token"].innocent_hits == 1


async def test_json_storage_save_token_repeated(storage):
    for _ in range(3):
        await storage.store_spam_token("spam-token")

    assert "spam-token" in storage.data
    assert storage.data["spam-token"].spam_hits == 3

    assert len(storage.data.keys()) == 1


async def test_json_storage_persist_and_open(storage):
    await storage.store_spam_token("spam-token")
    await storage.store_innocent_token("innocent-token")
    await storage.persist()

    # Create a new instance to test that the data is loaded correctly
    storage_root = storage.path.parent
    new_storage = JSONStorage(StorageSettings(), storage_root)
    await new_storage.open()

    assert "spam-token" in new_storage.data
    assert new_storage.data["spam-token"].spam_hits == 1

    assert "innocent-token" in new_storage.data
    assert new_storage.data["innocent-token"].innocent_hits == 1
