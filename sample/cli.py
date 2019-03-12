import click

from sample.new_project import NewProject
from sample.zen_of_python import the_zen_of_python


@click.group(help=click.style("PYTHON PACKAGE SAMPLE PROJECT", fg="green"))
def cli():
    """CLi starting point."""


@cli.command(help=click.style("The Zen of Python, by Tim Peters.", fg="green"))
def zen():
    """Pretty print The Zen of Python by Tim Peters."""

    the_zen_of_python()


@cli.command(help=click.style("Create new project skeleton.", fg="green"))
@click.argument('destination_path', type=click.Path(exists=True))
def new_project(destination_path):
    """Create skeleton for new new python package."""

    NewProject(destination_path).run()
