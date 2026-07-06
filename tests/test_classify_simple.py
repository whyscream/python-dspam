# SPDX-License-Identifier: BSD-3-Clause

from dspam.classify import SimpleClassifier
from dspam.settings import ClassifierSettings
from dspam.types import Classification


async def test_simple_classifier(storage):
    settings = ClassifierSettings()
    classifier = SimpleClassifier(settings, storage)

    for token in ["spam1", "spam2", "spam3"]:
        await storage.store_spam_token(token)
    for token in ["innocent1", "innocent2", "innocent3"]:
        await storage.store_innocent_token(token)

    assert await classifier(["spam1", "spam2", "spam3"]) == Classification.SPAM
    assert await classifier(["innocent1", "innocent2", "innocent3"]) == Classification.INNOCENT

    assert await classifier(["spam1", "spam2", "innocent3"]) == Classification.SPAM
    assert await classifier(["spam1", "innocent2", "innocent3"]) == Classification.INNOCENT

    assert await classifier(["unknown1", "unknown2", "unknown3"]) == Classification.INNOCENT
    assert await classifier(["unknown1", "spam2", "innocent3"]) == Classification.INNOCENT
    assert await classifier(["unknown1", "spam2", "spam3"]) == Classification.SPAM
