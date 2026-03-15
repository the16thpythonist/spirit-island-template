"""BaseCLI — custom Rich-formatted help with grouped command panels."""

from __future__ import annotations

import rich
import rich_click as click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from spirit_cli.cli.display import RichHelp, RichLogo


class BaseCLI(click.RichGroup):
    """Base CLI group with branded help output."""

    COMMAND_GROUPS: list[dict] = []

    def __init__(self, *args, **kwargs):
        click.RichGroup.__init__(self, *args, invoke_without_command=True, **kwargs)
        self.cons = Console()

    def get_help(self, ctx):
        rich.print(RichLogo())
        rich.print(RichHelp())
        self.cons.print()
        self.cons.print(f"  Usage: {ctx.command_path} [OPTIONS] COMMAND [ARGS]...")
        self.cons.print()
        self._format_command_groups(ctx)
        return ""

    def _format_command_groups(self, ctx) -> None:
        commands = self.list_commands(ctx)
        command_objs = {name: self.get_command(ctx, name) for name in commands}

        for group in self.COMMAND_GROUPS:
            table = Table(
                show_header=False, box=None, padding=(0, 1), expand=True
            )
            table.add_column(
                "Command", style="cyan", min_width=20, max_width=20, no_wrap=True
            )
            table.add_column("Description", style="white", ratio=1)

            has_commands = False
            for cmd_name in group["commands"]:
                if cmd_name in command_objs:
                    cmd = command_objs[cmd_name]
                    help_text = cmd.get_short_help_str(limit=100) if cmd else ""
                    table.add_row(cmd_name, help_text)
                    has_commands = True

            if not has_commands:
                table.add_row("[dim]No commands yet[/dim]", "")

            panel = Panel(
                table,
                title=f"[bold]{group['name']}[/bold]",
                title_align="left",
                border_style="bright_black",
                padding=(0, 1),
                expand=True,
            )
            rich.print(panel)
