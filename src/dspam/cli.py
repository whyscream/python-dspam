"""
CLI interface for python DSPAM

"""

from importlib.metadata import version

from cyclopts import App

from .main import main

cli = App(help=__doc__, version=version("python-dspam"))


@cli.default
def default():
    main()


plugins = App(name="plugins", help="Manage plugins", group="Sub commands")
cli.command(plugins)


@plugins.command(name="list", help="List available plugins")
def plugins_list():
    print("List of plugins: ...")


if __name__ == "__main__":
    cli()
