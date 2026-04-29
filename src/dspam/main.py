from pathlib import Path

from dspam.classify import DummyClassifier
from dspam.parse import PlainTextParser
from dspam.tokenize import WordTokenizer


async def main(file_path: Path):
    """Process the given file."""

    with file_path.open() as f:
        parser = PlainTextParser(f)
        content, metadata = await parser()

    tokenizer = WordTokenizer(content, metadata)
    tokens = await tokenizer()

    classifier = DummyClassifier(tokens)
    classification = await classifier()

    print(f"Classification result for {file_path}: {classification}")
