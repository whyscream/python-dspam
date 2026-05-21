from pathlib import Path

from dspam.classify import SimpleClassifier
from dspam.parse import PlainTextParser
from dspam.plugins import PluginManager
from dspam.storage import JSONStorage, get_storage_root
from dspam.tokenize import WordTokenizer
from dspam.train import SimpleTrainer


async def classify(pm: PluginManager, file_path: Path):
    """Process the given file."""
    with file_path.open() as f:
        parser = PlainTextParser(f)
        content, metadata = await parser()

    tokenizer = WordTokenizer(content, metadata)
    tokens = await tokenizer()

    storage_path = get_storage_root() / "storage.json"
    storage = JSONStorage(storage_path)

    classifier = SimpleClassifier(tokens, storage)
    classification = await classifier()

    print(f"Classification result for {file_path}: {classification}")


async def train(pm: PluginManager, file_path: Path, classification: str | None = None):
    """Train the classifier with the given file and classification."""
    with file_path.open() as f:
        parser = PlainTextParser(f)
        content, metadata = await parser()

    tokenizer = WordTokenizer(content, metadata)
    tokens = await tokenizer()

    storage_path = get_storage_root() / "storage.json"
    storage = JSONStorage(storage_path)

    if not classification:
        classifier = SimpleClassifier(tokens, storage)
        classification = await classifier()

    trainer = SimpleTrainer(tokens, storage, classification)
    await trainer(classification=classification)

    print(f"Trained {file_path} as: {classification}")
