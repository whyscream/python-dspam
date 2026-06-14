import os
import pathlib

import pytest

# IMPORTANT: don't add imports for dspam.settings to this file, as it will cause
# external set environment settings to be loaded before the environment variables are cleared.


def pytest_sessionstart(session):
    """Hook to run before the test session starts."""
    # Clear all environment variables that would conflict with the tests.
    for env_var in os.environ:
        if env_var.startswith("DSPAM_"):
            del os.environ[env_var]
        if env_var in [
            "XDG_CONFIG_HOME",
            "XDG_DATA_HOME",
        ]:
            del os.environ[env_var]


@pytest.fixture
def empty_config(tmp_path, monkeypatch):
    """Set the default config root to an empty directory."""
    config_path = tmp_path / ".config"
    monkeypatch.setenv("XDG_CONFIG_HOME", str(config_path))
    return config_path


@pytest.fixture
def empty_storage(tmp_path, monkeypatch):
    """Set the default storage root to an empty directory."""
    storage_path = tmp_path / ".storage"
    monkeypatch.setenv("XDG_DATA_HOME", str(storage_path))
    return storage_path


@pytest.fixture
def storage(tmp_path):
    from dspam.settings import StorageSettings
    from dspam.storage import JSONStorage

    json_storage = JSONStorage(StorageSettings(), tmp_path)
    yield json_storage
    json_storage_path = pathlib.Path(json_storage.path)
    if json_storage_path.exists():
        json_storage_path.unlink()
