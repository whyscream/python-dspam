import logging

from anyio import Path

from dspam.classify import Classifier
from dspam.di import container
from dspam.parse import Parser
from dspam.tokenize import Tokenizer
from dspam.train import Trainer

logger = logging.getLogger(__name__)


async def _parse_and_tokenize(file_path: Path) -> list[str]:
    async with await file_path.open() as fp:
        parser = container.resolve(Parser)
        result = await parser(fp)

    tokenizer = container.resolve(Tokenizer)
    tokens = await tokenizer(result.content, result.metadata)
    logger.info(f"Extracted {len(tokens)} tokens from {file_path}")
    return tokens


async def classify(file_path: Path):
    """Process the given file."""
    tokens = await _parse_and_tokenize(file_path)

    classifier = container.resolve(Classifier)
    classification = await classifier(tokens)

    print(f"Classification result for {file_path}: {classification}")


async def train(file_path: Path, classification: str | None = None):
    """Train the classifier with the given file and classification."""
    tokens = await _parse_and_tokenize(file_path)

    if not classification:
        logger.info(
            "No classification provided, using classifier to determine classification for training"
        )
        classifier = container.resolve(Classifier)
        classification = await classifier(tokens)

    trainer = container.resolve(Trainer)
    await trainer(tokens=tokens, classification=classification)

    print(f"Trained {file_path} as: {classification}")
