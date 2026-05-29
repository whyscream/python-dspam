"""
CLI interface for python DSPAM

"""

from importlib.metadata import version
from pathlib import Path
from typing import Annotated

from cyclopts import App, Parameter
from rich.console import Console
from rich.table import Table

from dspam.plugins import PluginManager
from dspam.main import classify, train

cli = App(help=__doc__, version=version("python-dspam"))


def validate_path(type_, value):
    if not value.is_file():
        raise ValueError(f"Path {value} is not a valid file.")


def get_plugin_manager() -> PluginManager:
    pm = PluginManager()
    pm.load_all_plugins()
    return pm


@cli.command(name="classify", help="Classify a file")
async def classify_file(
    file_path: Annotated[
        Path,
        Parameter(
            validator=validate_path, alias="-f", help="Path to the file to classify"
        ),
    ],
):
    pm = get_plugin_manager()
    await classify(pm=pm, file_path=file_path)


@cli.command(name="train", help="Train the classifier")
async def train_from_file(
    file_path: Annotated[
        Path,
        Parameter(
            validator=validate_path, alias="-f", help="Path to the file to train"
        ),
    ],
    classification: Annotated[
        str | None,
        Parameter(alias="-c", help="Classification of the file (ham or spam)"),
    ] = None,
):
    pm = get_plugin_manager()
    await train(pm=pm, file_path=file_path, classification=classification)


plugins = App(name="plugins", help="Manage plugins", group="Subcommands")
cli.command(plugins)


@plugins.command(name="list", help="List available plugins")
def plugins_list():
    pm = get_plugin_manager()
    plugins = pm.list_plugins()

    console = Console()
    table = Table(show_header=True, header_style="bold magenta", title="Plugins")
    table.add_column("Group")
    table.add_column("Name")
    table.add_column("Package")
    table.add_column("Version")
    table.add_column("API version")

    for plugin in plugins:
        table.add_row(
            plugin.group,
            plugin.name,
            plugin.package,
            plugin.version,
            plugin.api_version,
        )
    console.print(table)


if __name__ == "__main__":
    cli()
