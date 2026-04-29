"""
CLI interface for python DSPAM

"""

from importlib.metadata import version
from pathlib import Path
from typing import Annotated

from cyclopts import App, Parameter

from .main import main

cli = App(help=__doc__, version=version("python-dspam"))


def validate_path(type_, value):
    if not value.is_file():
        raise ValueError(f"Path {value} is not a valid file.")


@cli.default
async def default(
    file_path: Annotated[
        Path,
        Parameter(
            validator=validate_path, alias="-f", help="Path to the file to process"
        ),
    ],
):
    await main(file_path=file_path)


plugins = App(name="plugins", help="Manage plugins", group="Subcommands")
cli.command(plugins)


@plugins.command(name="list", help="List available plugins")
def plugins_list():
    print("List of plugins: ...")


if __name__ == "__main__":
    cli()
