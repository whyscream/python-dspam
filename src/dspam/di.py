"""
Dependency inversion initialization.

We mainly use factories so we can query the Plugin Manager (and future Settings) for the correct plugin to use.
"""

import logging

from rodi import ActivationScope, Container

from dspam.classify import Classifier
from dspam.parse import Parser
from dspam.plugins import PluginManager
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
    parser_class: type[Parser] = pm.get_plugin(pm.PARSER)

    parser_instance = parser_class()
    logger.debug(f"Initialized parser: {parser_instance}")
    return parser_instance


def tokenizer_factory(context: ActivationScope) -> Tokenizer:
    """Factory for DI-supplied Tokenizer instances."""
    pm = context.provider.get(PluginManager)
    tokenizer_class: type[Tokenizer] = pm.get_plugin(pm.TOKENIZER)

    tokenizer_instance = tokenizer_class()
    logger.debug(f"Initialized tokenizer: {tokenizer_instance}")
    return tokenizer_instance


def storage_factory(context: ActivationScope) -> Storage:
    """Factory for DI-supplied Storage instances."""
    pm = context.provider.get(PluginManager)
    storage_class: type[Storage] = pm.get_plugin(pm.STORAGE)

    storage_root = get_storage_root()
    storage_instance = storage_class(storage_root)
    logger.debug(f"Initialized storage: {storage_instance}")
    return storage_instance


def classify_factory(context: ActivationScope) -> Classifier:
    """Factory for DI-supplied Classifier instances."""
    pm = context.provider.get(PluginManager)
    classification_class: type[Classifier] = pm.get_plugin(pm.CLASSIFIER)
    storage = context.provider.get(Storage)

    classifier_instance = classification_class(storage)
    logger.debug(f"Initialized classifier: {classifier_instance}")
    return classifier_instance


def trainer_factory(context: ActivationScope) -> Trainer:
    """Factory for DI-supplied Trainer instances."""
    pm = context.provider.get(PluginManager)
    trainer_class: type[Trainer] = pm.get_plugin(pm.TRAINER)
    storage = context.provider.get(Storage)

    trainer_instance = trainer_class(storage)
    logger.debug(f"Initialized trainer: {trainer_instance}")
    return trainer_instance


container = Container()
container.add_singleton_by_factory(plugin_manager_factory)
container.add_singleton_by_factory(storage_factory)

container.add_transient_by_factory(parser_factory)
container.add_transient_by_factory(tokenizer_factory)
container.add_transient_by_factory(classify_factory)
container.add_transient_by_factory(trainer_factory)
