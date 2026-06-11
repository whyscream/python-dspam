"""
CLI interface for python DSPAM

"""

import logging
from importlib.metadata import version
from typing import Annotated

import anyio
from cyclopts import App, Parameter, validators
from rich.console import Console
from rich.table import Table

from dspam import Verdict
from dspam.di import provider
from dspam.main import classify, train
from dspam.plugins import PluginManager
from dspam.settings import Settings

cli = App(help=__doc__, version=version("python-dspam"))


@cli.command(name="classify", help="Classify a file")
async def classify_file(
    file_path: Annotated[
        anyio.Path,
        Parameter(
            validator=validators.Path(exists=True, dir_okay=False),
            alias="-f",
            help="Path to the file to classify",
        ),
    ],
) -> None:
    await classify(file_path=file_path)


@cli.command(name="train", help="Train the classifier")
async def train_from_file(
    file_path: Annotated[
        anyio.Path,
        Parameter(
            validator=validators.Path(exists=True, dir_okay=False),
            alias="-f",
            help="Path to the file to train",
        ),
    ],
    classification: Annotated[
        Verdict,
        Parameter(alias="-c", help="Classification of the file (ham or spam)"),
    ],
) -> None:
    await train(file_path=file_path, classification=classification)


plugins = App(name="plugins", help="Manage plugins", group="Subcommands")
cli.command(plugins)


@plugins.command(name="list", help="List available plugins")
def plugins_list() -> None:
    pm = provider.get(PluginManager)
    plugins_ = pm.list_plugins()
    settings = provider.get(Settings)
    settings_dict = settings.dict()

    console = Console()
    table = Table(show_header=True, header_style="bold magenta", title="Plugins")
    table.add_column("Group")
    table.add_column("Name")
    table.add_column("In use")
    table.add_column("Package")
    table.add_column("Version")
    table.add_column("API version")

    for plugin in plugins_:
        in_use = settings_dict.get(plugin.group, {}).get("plugin") == plugin.name

        table.add_row(
            plugin.group,
            plugin.name,
            str(in_use),
            plugin.package,
            plugin.version,
            plugin.api_version,
        )
    console.print(table)


@cli.command(name="config")
def dump_config() -> None:
    settings = Settings()
    console = Console()
    console.print(settings.model_dump_json(indent=4))


def main() -> None:
    settings = provider.get(Settings)
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    )
    cli()


if __name__ == "__main__":
    main()
