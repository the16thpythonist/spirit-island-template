"""Bootstrap commands mixin — scaffold new spirit folders."""

from __future__ import annotations

from pathlib import Path

import rich_click as click


class BootstrapCommandsMixin:
    """Commands for scaffolding new spirit projects."""

    @click.command("bootstrap-spirit")
    @click.pass_obj
    @click.argument("name")
    @click.option(
        "--cards",
        default=4,
        help="Number of power card templates to create.",
        show_default=True,
    )
    @click.option(
        "--output-dir",
        default=".",
        type=click.Path(file_okay=False, path_type=Path),
        help="Base directory for the spirit folder.",
        show_default=True,
    )
    def bootstrap_spirit_command(self, name: str, cards: int, output_dir: Path) -> None:
        """Scaffold a new spirit folder with template YAML files."""
        from rich.console import Console

        from spirit_cli.bootstrap import bootstrap_spirit

        console = Console()
        try:
            spirit_dir = bootstrap_spirit(name, cards, output_dir)
            console.print(f"[green]Done![/green] Spirit scaffolded at [cyan]{spirit_dir}[/cyan]")
            console.print()
            console.print("[dim]Created files:[/dim]")
            for f in sorted(spirit_dir.glob("*.yaml")):
                console.print(f"  [cyan]{f.name}[/cyan]")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise SystemExit(1)
