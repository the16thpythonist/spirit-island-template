"""Art generation commands mixin — generate artwork via Gemini API."""

from __future__ import annotations

from pathlib import Path

import rich_click as click


class ArtCommandsMixin:
    """Commands for generating component artwork."""

    @click.command("generate-art")
    @click.pass_obj
    @click.argument("yaml_file", type=click.Path(exists=True, path_type=Path))
    @click.option(
        "--timeout",
        default=300,
        help="API request timeout in seconds.",
        show_default=True,
    )
    @click.option(
        "--style-examples",
        default=0,
        help="Number of bundled style reference images to attach.",
        show_default=True,
    )
    @click.option(
        "--reference",
        multiple=True,
        type=click.Path(exists=True, path_type=Path),
        help="Custom reference image (can be used multiple times).",
    )
    def generate_art_command(
        self,
        yaml_file: Path,
        timeout: int,
        style_examples: int,
        reference: tuple[Path, ...],
    ) -> None:
        """Generate artwork for a component using its art_prompt field."""
        import yaml as pyyaml
        from rich.console import Console
        from rich.status import Status

        from spirit_cli.art import generate_art
        from spirit_cli.compiler import slugify

        console = Console()
        try:
            console.print(f"[dim]Loading: {yaml_file.name}[/dim]")
            raw = pyyaml.safe_load(yaml_file.read_text())
            prompt = raw.get("art_prompt")
            if not prompt:
                console.print("[red]Error:[/red] No art_prompt field found in YAML file.")
                raise SystemExit(1)

            name = (
                raw.get("name")
                or raw.get("spirit_name")
                or raw.get("aspect_name")
                or "art"
            )
            output_path = yaml_file.parent / f"{slugify(name)}_art.png"

            console.print(f"[dim]Component: {name}[/dim]")
            console.print(f"[dim]Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}[/dim]")
            console.print(f"[dim]Output: {output_path}[/dim]")
            console.print(f"[dim]Style examples: {style_examples}[/dim]")
            if reference:
                for ref in reference:
                    console.print(f"[dim]Reference: {ref}[/dim]")
            console.print(f"[dim]Timeout: {timeout}s[/dim]")
            console.print()

            import time

            start = time.monotonic()
            with Status(
                "[bold cyan]Generating artwork via Gemini API...[/bold cyan]",
                console=console,
                spinner="dots",
            ):
                result_path, refs_used = generate_art(
                    prompt,
                    output_path,
                    timeout=timeout,
                    num_examples=style_examples,
                    references=list(reference) if reference else None,
                )
            elapsed = time.monotonic() - start

            if refs_used:
                console.print(f"[dim]Used {refs_used} reference image(s)[/dim]")

            console.print(f"[green]Done![/green] Art saved to [cyan]{result_path}[/cyan] [dim]({elapsed:.1f}s)[/dim]")
        except SystemExit:
            raise
        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelled by user.[/yellow]")
            raise SystemExit(1)
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise SystemExit(1)
