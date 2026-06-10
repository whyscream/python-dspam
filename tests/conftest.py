import os
import pathlib

import pytest

from dspam.settings import StorageSettings
from dspam.storage import JSONStorage


@pytest.fixture(autouse=True)
def empty_config(tmp_path, monkeypatch):
    """Set the default config root to an empty directory."""
    for env_var in os.environ.keys():
        if env_var.startswith("DSPAM_"):
            monkeypatch.delenv(env_var, raising=False)

    config_path = tmp_path / ".config"
    data_path = tmp_path / ".data"
    monkeypatch.setenv("XDG_CONFIG_HOME", str(config_path))
    monkeypatch.setenv("XDG_DATA_HOME", str(data_path))
    return config_path


@pytest.fixture
def storage(tmp_path):
    json_storage = JSONStorage(StorageSettings(), tmp_path)
    yield json_storage
    json_storage_path = pathlib.Path(json_storage.path)
    if json_storage_path.exists():
        json_storage_path.unlink()
