"""Spirit CLI — mixin-based CLI assembly."""

from __future__ import annotations

import rich_click as click
from dotenv import find_dotenv, load_dotenv

from spirit_cli.cli.art import ArtCommandsMixin
from spirit_cli.cli.base import BaseCLI
from spirit_cli.cli.bootstrap import BootstrapCommandsMixin
from spirit_cli.cli.compile import CompileCommandsMixin
from spirit_cli.cli.print_layout import PrintLayoutCommandsMixin


class CLI(
    CompileCommandsMixin,
    ArtCommandsMixin,
    PrintLayoutCommandsMixin,
    BootstrapCommandsMixin,
    BaseCLI,
):
    COMMAND_GROUPS = [
        {"name": "Setup", "commands": ["bootstrap-spirit"]},
        {"name": "Build", "commands": ["compile", "compile-all"]},
        {"name": "Print", "commands": ["print-layout"]},
        {"name": "AI", "commands": ["generate-art"]},
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_command(self.bootstrap_spirit_command)
        self.add_command(self.compile_command)
        self.add_command(self.compile_all_command)
        self.add_command(self.print_layout_command)
        self.add_command(self.generate_art_command)


def create_cli():
    @click.group(cls=CLI)
    @click.version_option(package_name="spirit-island-cli")
    @click.pass_context
    def _cli(ctx: click.Context) -> None:
        """Spirit Island Template CLI."""
        load_dotenv(find_dotenv(usecwd=True))
        ctx.obj = ctx.command

        if ctx.invoked_subcommand is None:
            click.echo(ctx.get_help())

    return _cli


cli = create_cli()
