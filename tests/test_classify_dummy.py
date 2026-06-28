# SPDX-License-Identifier: BSD-3-Clause

from dspam.classify import DummyClassifier
from dspam.settings import ClassifierSettings


async def test_classify_dummy(storage):
    settings = ClassifierSettings()
    classifier = DummyClassifier(settings, storage)

    assert await classifier(["this", "is", "a", "test"]) == "innocent"
    assert await classifier(["this", "is", "a", "spam", "test"]) == "spam"
