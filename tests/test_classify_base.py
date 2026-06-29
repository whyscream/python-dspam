# SPDX-License-Identifier: BSD-3-Clause

import logging

from dspam.classify import DummyClassifier
from dspam.settings import ClassifierSettings


async def test_classify_dummy(storage):
    settings = ClassifierSettings()
    classifier = DummyClassifier(settings, storage)

    assert await classifier(["this", "is", "a", "test"]) == "innocent"
    assert await classifier(["this", "is", "a", "spam", "test"]) == "spam"


async def test_classifier_log_debug_settings_success(storage, caplog):
    settings = ClassifierSettings()
    classifier = DummyClassifier(settings, storage)
    await storage.store_innocent_token("token1")  # token1 is available in storage

    with caplog.at_level(logging.DEBUG, logger="dspam"):
        await classifier.log_debug_tokens(["token1", "token2"], verdict="innocent", debug_token_count=2)

    assert "Token: verdict='innocent' token='token1' spam_hits=0 innocent_hits=1" in caplog.messages
    assert "Token: verdict='innocent' token='token2'" in caplog.messages


async def test_classifier_log_debug_settings_limit_count(storage, caplog):
    settings = ClassifierSettings()
    classifier = DummyClassifier(settings, storage)

    tokens = [f"token{n}" for n in range(10)]

    with caplog.at_level(logging.DEBUG, logger="dspam"):
        await classifier.log_debug_tokens(tokens, verdict="innocent", debug_token_count=2)

    # Check that only 2 tokens are logged
    assert len(caplog.messages) == 2
