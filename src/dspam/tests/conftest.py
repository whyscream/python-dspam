import pytest

from dspam.storage import JSONStorage


@pytest.fixture
def storage(tmp_path):
    json_storage_path = tmp_path / "storage.json"
    yield JSONStorage(json_storage_path)
    if json_storage_path.exists():
        json_storage_path.unlink()
