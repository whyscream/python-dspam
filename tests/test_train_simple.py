# SPDX-License-Identifier: BSD-3-Clause

from dspam import IS_INNOCENT
from dspam.settings import TrainerSettings
from dspam.storage import TokenData
from dspam.train import SimpleTrainer


async def test_train_simple_with_classification(storage):
    """Test that the simple trainer can be called and updates the storage correctly using the classification."""
    # Simulate token data in storage
    storage.data = {
        "token1": TokenData(token="token1", spam_hits=3, innocent_hits=1),
        "token2": TokenData(token="token2", spam_hits=1, innocent_hits=1),
    }

    trainer = SimpleTrainer(TrainerSettings(), storage=storage)
    await trainer(tokens=["token1", "token2"], classification=IS_INNOCENT)

    token1_data = await storage.get_token("token1")
    assert token1_data.innocent_hits == 2, "token1 should have an additional innocent hit"
    assert token1_data.spam_hits == 3, "token1 should have unchanged spam hit"

    token2_data = await storage.get_token("token2")
    assert token2_data.innocent_hits == 2, "token2 should have an additional innocent hit"
    assert token2_data.spam_hits == 1, "token2 should have unchanged spam hit"
