from pathlib import Path as SyncPath

import pytest

from dspam.settings import StorageSettings
from dspam.storage import JSONStorage


@pytest.fixture
def storage(tmp_path):
    json_storage = JSONStorage(StorageSettings(), tmp_path)
    yield json_storage
    json_storage_path = SyncPath(json_storage.path)
    if json_storage_path.exists():
        json_storage_path.unlink()
