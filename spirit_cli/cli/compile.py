"""Compile commands mixin — YAML to HTML + PNG."""

from __future__ import annotations

from pathlib import Path

import rich_click as click


class CompileCommandsMixin:
    """Commands for compiling YAML components to HTML and PNG."""

    @click.command("compile")
    @click.pass_obj
    @click.argument("yaml_file", type=click.Path(exists=True, path_type=Path))
    def compile_command(self, yaml_file: Path) -> None:
        """Compile a YAML component file to standalone HTML and PNG."""
        from rich.console import Console

        from spirit_cli.compiler import compile_component, find_project_root

        console = Console()
        try:
            project_root = find_project_root(yaml_file)
            console.print(f"[dim]Project root: {project_root}[/dim]")
            console.print(f"[dim]Compiling: {yaml_file.name}[/dim]")

            output_dir = compile_component(yaml_file, project_root)

            console.print(f"[green]Done![/green] Output written to [cyan]{output_dir}[/cyan]")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise SystemExit(1)

    @click.command("compile-all")
    @click.pass_obj
    @click.argument("folder", type=click.Path(exists=True, file_okay=False, path_type=Path))
    def compile_all_command(self, folder: Path) -> None:
        """Compile all YAML files in a folder to standalone HTML and PNG."""
        from rich.console import Console

        from spirit_cli.compiler import compile_component, find_project_root, slugify

        console = Console()
        yaml_files = sorted(folder.glob("*.yaml")) + sorted(folder.glob("*.yml"))
        if not yaml_files:
            console.print(f"[yellow]No YAML files found in {folder}[/yellow]")
            raise SystemExit(1)

        try:
            project_root = find_project_root(folder)
            folder_slug = slugify(folder.resolve().name)
            shared_output_dir = project_root / "output" / folder_slug

            console.print(f"[dim]Project root: {project_root}[/dim]")
            console.print(f"[dim]Output: {shared_output_dir}[/dim]")
            console.print(f"[dim]Found {len(yaml_files)} YAML file(s) in {folder}[/dim]")
            console.print()

            failed = []
            for yaml_file in yaml_files:
                try:
                    console.print(f"  Compiling [cyan]{yaml_file.name}[/cyan]...", end=" ")
                    compile_component(yaml_file, project_root, output_dir=shared_output_dir)
                    console.print(f"[green]OK[/green]")
                except Exception as e:
                    console.print(f"[red]FAILED[/red] — {e}")
                    failed.append((yaml_file.name, str(e)))

            console.print()
            if failed:
                console.print(f"[yellow]{len(failed)} of {len(yaml_files)} failed:[/yellow]")
                for name, err in failed:
                    console.print(f"  [red]•[/red] {name}: {err}")
                raise SystemExit(1)
            else:
                console.print(f"[green]All {len(yaml_files)} component(s) compiled successfully![/green]")
        except SystemExit:
            raise
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise SystemExit(1)
