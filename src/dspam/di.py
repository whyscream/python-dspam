"""
Dependency inversion initialization.

We mainly use factories so we can query the Plugin Manager (and future Settings) for the correct plugin to use.
"""

import logging

from rodi import ActivationScope, Container

from dspam.classify import Classifier
from dspam.parse import Parser
from dspam.plugins import PluginManager
from dspam.settings import Settings
from dspam.storage import Storage, get_storage_root
from dspam.tokenize import Tokenizer
from dspam.train import Trainer

logger = logging.getLogger(__name__)


def plugin_manager_factory() -> PluginManager:
    pm = PluginManager()
    pm.load_all_plugins()
    return pm


def parser_factory(context: ActivationScope) -> Parser:
    """Factory for DI-supplied Parser instances."""
    pm = context.provider.get(PluginManager)
    settings = context.provider.get(Settings)
    parser_class: type[Parser] = pm.get_plugin(pm.PARSER, settings.parser.plugin)

    parser_instance = parser_class(settings=settings.parser)
    logger.debug(f"Initialized parser: {parser_instance}")
    return parser_instance


def tokenizer_factory(context: ActivationScope) -> Tokenizer:
    """Factory for DI-supplied Tokenizer instances."""
    pm = context.provider.get(PluginManager)
    settings = context.provider.get(Settings)
    tokenizer_class: type[Tokenizer] = pm.get_plugin(
        pm.TOKENIZER, settings.tokenizer.plugin
    )

    tokenizer_instance = tokenizer_class(settings=settings.tokenizer)
    logger.debug(f"Initialized tokenizer: {tokenizer_instance}")
    return tokenizer_instance


def storage_factory(context: ActivationScope) -> Storage:
    """Factory for DI-supplied Storage instances."""
    pm = context.provider.get(PluginManager)
    settings = context.provider.get(Settings)
    storage_class: type[Storage] = pm.get_plugin(pm.STORAGE, settings.storage.plugin)

    storage_root = get_storage_root()
    storage_instance = storage_class(
        settings=settings.storage, storage_root=storage_root
    )
    logger.debug(f"Initialized storage: {storage_instance}")
    return storage_instance


def classify_factory(context: ActivationScope) -> Classifier:
    """Factory for DI-supplied Classifier instances."""
    pm = context.provider.get(PluginManager)
    settings = context.provider.get(Settings)
    classification_class: type[Classifier] = pm.get_plugin(
        pm.CLASSIFIER, settings.classifier.plugin
    )
    storage = context.provider.get(Storage)

    classifier_instance = classification_class(settings.classifier, storage)
    logger.debug(f"Initialized classifier: {classifier_instance}")
    return classifier_instance


def trainer_factory(context: ActivationScope) -> Trainer:
    """Factory for DI-supplied Trainer instances."""
    pm = context.provider.get(PluginManager)
    settings = context.provider.get(Settings)
    trainer_class: type[Trainer] = pm.get_plugin(pm.TRAINER, settings.trainer.plugin)
    storage = context.provider.get(Storage)

    trainer_instance = trainer_class(settings.trainer, storage)
    logger.debug(f"Initialized trainer: {trainer_instance}")
    return trainer_instance


_container = Container()
_container.add_singleton_by_factory(plugin_manager_factory)
_container.add_singleton_by_factory(storage_factory)
_container.register(Settings, instance=Settings())

_container.add_transient_by_factory(parser_factory)
_container.add_transient_by_factory(tokenizer_factory)
_container.add_transient_by_factory(classify_factory)
_container.add_transient_by_factory(trainer_factory)

provider = _container.build_provider()
