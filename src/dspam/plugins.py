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
from dataclasses import dataclass
from collections.abc import Generator


@dataclass
class PluginInfo:
    name: str
    entry_point_group: str
    package: str
    version: str
    api_version: str


class PluginManager:
    PLUGIN_ENTRY_POINTS = [
        "dspam.parser",
        "dspam.tokenizer",
        "dspam.classifier",
        "dspam.storage",
    ]

    def __init__(self):
        self.plugins = {ep: {} for ep in self.PLUGIN_ENTRY_POINTS}

    def load_all_plugins(self):
        """
        Load all plugins from all entry point groups.
        """
        self.load_builtin_plugins()
        for entry_point_group in self.PLUGIN_ENTRY_POINTS:
            self.load_plugins(entry_point_group)

    def load_builtin_plugins(self):
        parse_module = importlib.import_module("dspam.parse")
        tokenize_module = importlib.import_module("dspam.tokenize")
        classify_module = importlib.import_module("dspam.classify")
        self.plugins["dspam.parser"]["plain-text"] = parse_module.PlainTextParser
        self.plugins["dspam.tokenizer"]["word"] = tokenize_module.WordTokenizer
        self.plugins["dspam.classifier"]["dummy"] = classify_module.DummyClassifier

    def load_plugins(self, entry_point_group: str) -> None:
        """
        Load plugins from the specified entry point group.

        :param entry_point_group: The entry point group to load plugins from.
        """
        for entry_point in importlib.metadata.entry_points(group=entry_point_group):
            self.load_plugin(entry_point)

    def load_plugin(self, entry_point: importlib.metadata.EntryPoint) -> None:
        try:
            plugin_class = entry_point.load()
            self.plugins[entry_point.group][entry_point.name] = plugin_class
        except Exception as err:
            print(f"Error loading plugin {entry_point.name}: {err}")

    def list_plugins(self) -> Generator[PluginInfo]:
        """
        List all loaded plugins.

        :return: A generator of PluginInfo objects containing information about each loaded plugin.
        """
        for entry_point_group, plugins in self.plugins.items():
            for plugin, plugin_class in plugins.items():
                module = plugin_class.__module__
                package = module.split(".")[0]
                try:
                    version = importlib.metadata.version(package)
                except importlib.metadata.PackageNotFoundError:
                    module = importlib.import_module(package)
                    version = module.__version__
                api_version = getattr(plugin_class, "API_VERSION", "0.0")

                yield PluginInfo(
                    name=plugin,
                    entry_point_group=entry_point_group,
                    package=package,
                    version=version,
                    api_version=api_version,
                )
