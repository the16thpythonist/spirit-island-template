"""Print layout commands mixin — arrange components on A4 pages."""

from __future__ import annotations

from pathlib import Path

import rich_click as click


class PrintLayoutCommandsMixin:
    """Commands for generating print-ready PDFs."""

    @click.command("print-layout")
    @click.pass_obj
    @click.argument("output_folder", type=click.Path(exists=True, file_okay=False, path_type=Path))
    def print_layout_command(self, output_folder: Path) -> None:
        """Arrange compiled components onto A4 pages as a print-ready PDF."""
        from rich.console import Console

        from spirit_cli.print_layout import generate_print_layout, _classify_files

        console = Console()
        try:
            files = _classify_files(output_folder)

            board_count = len(files["board_front"]) + len(files["board_lore"])
            card_count = len(files["cards"])
            back_count = len(files["card_back"])

            console.print(f"[dim]Folder: {output_folder}[/dim]")
            console.print(f"[dim]Found: {board_count} board(s), {card_count} card(s), {back_count} card back(s)[/dim]")

            if not any(files.values()):
                console.print("[yellow]No PNG files found in folder.[/yellow]")
                raise SystemExit(1)

            pdf_path = output_folder / "print-layout.pdf"
            generate_print_layout(output_folder, pdf_path)

            console.print(f"[green]Done![/green] PDF saved to [cyan]{pdf_path}[/cyan]")
        except SystemExit:
            raise
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise SystemExit(1)
