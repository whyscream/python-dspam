"""
A simple plugin system that allows switching between different implementations of the same interface. This is useful
for allowing users to choose between different algorithms or implementations of a feature, without having to change
the codebase.

Uses setuptools entry points for registration and discovery of plugins. This allows for easy installation and
management of plugins, as well as allowing for third-party plugins to be easily added to the system.

Plugins are organized into groups based on their functionality, such as parsers, tokenizers, classifiers, and storage.

Plugin API contract
-------------------

Each plugin is implemented as a class. The class must have an API_VERSION attribute that specifies the version of the
plugin API that it implements. This allows for compatibility checks when loading plugins.
"""

import importlib.metadata
import inspect
import logging
from dataclasses import dataclass
from collections.abc import Generator

from pydantic_settings import BaseSettings

from dspam.exceptions import DspamPluginNotFound

logger = logging.getLogger(__name__)


@dataclass
class PluginInfo:
    name: str
    group: str
    package: str
    version: str
    api_version: str


class PluginManager:
    # Plugin groups
    PARSER: str = "parser"
    TOKENIZER: str = "tokenizer"
    CLASSIFIER: str = "classifier"
    TRAINER: str = "trainer"
    STORAGE: str = "storage"

    GROUPS: list[str] = [
        PARSER,
        TOKENIZER,
        CLASSIFIER,
        TRAINER,
        STORAGE,
    ]

    PLUGIN_ENTRY_POINTS = {f"dspam.{group}": group for group in GROUPS}
    """Supported entry point groups for registering plugins: dspam:<group name>."""

    def __init__(self) -> None:
        self.plugins: dict[str, dict[str, type]] = {group: {} for group in self.GROUPS}

    def load_all_plugins(self) -> None:
        """
        Load all plugins from all entry point groups.
        """
        self.load_builtin_plugins()
        self.load_entrypoint_plugins()

    def load_builtin_plugins(self) -> None:
        parse_module = importlib.import_module("dspam.parse")
        tokenize_module = importlib.import_module("dspam.tokenize")
        classify_module = importlib.import_module("dspam.classify")
        training_module = importlib.import_module("dspam.train")
        storage_module = importlib.import_module("dspam.storage")
        self.plugins[self.PARSER]["plaintext"] = parse_module.PlainTextParser
        self.plugins[self.TOKENIZER]["word"] = tokenize_module.WordTokenizer
        self.plugins[self.CLASSIFIER]["simple"] = classify_module.SimpleClassifier
        self.plugins[self.CLASSIFIER]["dummy"] = classify_module.DummyClassifier
        self.plugins[self.TRAINER]["simple"] = training_module.SimpleTrainer
        self.plugins[self.STORAGE]["json"] = storage_module.JSONStorage

        plugin_names = [f"{p.group}:{p.name}" for p in self.list_plugins()]
        logger.debug(f"Loaded built-in plugins: {', '.join(plugin_names)}")

    def load_entrypoint_plugins(self) -> None:
        for entry_point_group, group in self.PLUGIN_ENTRY_POINTS.items():
            for entry_point in importlib.metadata.entry_points(group=entry_point_group):
                try:
                    plugin_class = entry_point.load()
                    self.plugins[group][entry_point.name] = plugin_class
                    logger.debug(f"Loaded plugin: {group}:{entry_point.name}")
                except Exception as err:
                    logger.error(
                        f"Error loading plugin {group}:{entry_point.name}: {err}"
                    )

    def list_plugins(self) -> Generator[PluginInfo]:
        """
        List all loaded plugins.

        :return: A generator of PluginInfo objects containing information about each loaded plugin.
        """
        for group, plugins in self.plugins.items():
            for plugin, plugin_class in plugins.items():
                module_name = plugin_class.__module__
                package_name = module_name.split(".")[0]
                try:
                    version = importlib.metadata.version(package_name)
                except importlib.metadata.PackageNotFoundError:
                    module = importlib.import_module(package_name)
                    version = module.__version__
                api_version = getattr(plugin_class, "API_VERSION", "0.0")

                yield PluginInfo(
                    name=plugin,
                    group=group,
                    package=package_name,
                    version=version,
                    api_version=api_version,
                )

    def get_plugin(self, group_name: str, plugin_name: str) -> type:
        """
        Get the plugin class for the specified group and plugin name.

        :param group_name: The entry point group to get the plugin from.
        :param plugin_name: The name of the plugin to get.
        :return: The plugin class, or None if the plugin is not found.
        """
        group = self.plugins.get(group_name, {})
        plugin: type | None = group.get(plugin_name)
        if not plugin:
            raise DspamPluginNotFound(f"Plugin {group_name}.{plugin_name} not found")
        return plugin

    def get_plugin_settings(
        self, group_name: str, plugin_name: str
    ) -> type[BaseSettings] | None:
        """
        Get the settings class from the plugin module, if available, and return it.

        We define the Settings module for the plugin as subclass of BaseSettings,
        coming from the same module as the plugin. When more are found, we always return the first.
        """
        try:
            plugin = self.get_plugin(group_name, plugin_name)
        except DspamPluginNotFound as err:
            logger.warning(err)
            return None

        module = importlib.import_module(plugin.__module__)
        settings_classes = [
            member
            for _, member in inspect.getmembers(module, inspect.isclass)
            if issubclass(member, BaseSettings)
            and member.__module__ == plugin.__module__
        ]
        if settings_classes:
            return settings_classes[0]
        return None
