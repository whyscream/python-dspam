from anyio import Path

from dspam.plugins import PluginManager
from dspam.storage import get_storage_root


async def _parse_and_tokenize(pm: PluginManager, file_path: Path) -> list[str]:
    parser_class = pm.get_plugin(pm.PARSER)
    tokenizer_class = pm.get_plugin(pm.TOKENIZER)

    async with await file_path.open() as f:
        parser = parser_class(f)
        content, metadata = await parser()

    tokenizer = tokenizer_class(content, metadata)
    tokens = await tokenizer()
    return tokens


async def classify(pm: PluginManager, file_path: Path):
    """Process the given file."""
    tokens = await _parse_and_tokenize(pm, file_path)

    storage_class = pm.get_plugin(pm.STORAGE)
    storage_path = await get_storage_root() / "storage.json"
    storage = storage_class(storage_path)

    classifier_class = pm.get_plugin(pm.CLASSIFIER)
    classifier = classifier_class(tokens, storage)
    classification = await classifier()

    print(f"Classification result for {file_path}: {classification}")


async def train(pm: PluginManager, file_path: Path, classification: str | None = None):
    """Train the classifier with the given file and classification."""
    tokens = await _parse_and_tokenize(pm, file_path)

    storage_class = pm.get_plugin(pm.STORAGE)
    storage_path = await get_storage_root() / "storage.json"
    storage = storage_class(storage_path)

    if not classification:
        classifier_class = pm.get_plugin(pm.CLASSIFIER)
        classifier = classifier_class(tokens, storage)
        classification = await classifier()

    train_class = pm.get_plugin(pm.TRAIN)
    trainer = train_class(tokens, storage, classification)
    await trainer(classification=classification)

    print(f"Trained {file_path} as: {classification}")
