# SPDX-License-Identifier: BSD-3-Clause

import logging

from anyio import Path

from dspam.types import Verdict
from dspam.classify import Classifier
from dspam.di import provider
from dspam.parse import Parser
from dspam.tokenize import Tokenizer
from dspam.train import Trainer

logger = logging.getLogger(__name__)


async def _parse_and_tokenize(file_path: Path) -> list[str]:
    async with await file_path.open() as fp:
        parser = provider.get(Parser)
        result = await parser(fp)

    tokenizer = provider.get(Tokenizer)
    tokens: list[str] = await tokenizer(result.content, result.metadata)
    logger.info(f"Extracted {len(tokens)} tokens from {file_path}")
    return tokens


async def classify(file_path: Path) -> None:
    """Process the given file."""
    tokens = await _parse_and_tokenize(file_path)

    classifier = provider.get(Classifier)
    classification = await classifier(tokens)

    print(f"Classification result for {file_path}: {classification}")


async def train(file_path: Path, classification: Verdict) -> None:
    """Train the classifier with the given file and classification."""
    tokens = await _parse_and_tokenize(file_path)

    trainer = provider.get(Trainer)
    await trainer(tokens=tokens, classification=classification)

    print(f"Trained {file_path} as: {classification}")
