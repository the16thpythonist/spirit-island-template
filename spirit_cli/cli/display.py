"""Rich console protocol classes for CLI help display."""

from __future__ import annotations

from pathlib import Path

from rich.columns import Columns
from rich.padding import Padding
from rich.text import Text

ASSETS_DIR = Path(__file__).parent / "assets"


class RichLogo:
    """Renders the Spirit CLI logo with optional ANSI image."""

    STYLE = "bold white"

    # Column where "SPIRIT" starts in the block text
    SPIRIT_COL = 20

    def __rich_console__(self, console, options):
        text_path = ASSETS_DIR / "logo_text.txt"
        try:
            text_string = text_path.read_text()
        except FileNotFoundError:
            text_string = "MySpirit"
        text = Text(style=self.STYLE)
        for line in text_string.splitlines():
            my_part = line[: self.SPIRIT_COL]
            spirit_part = line[self.SPIRIT_COL :]
            text.append(my_part, style="bold cyan")
            text.append(spirit_part, style="bold white")
            text.append("\n")

        image_path = ASSETS_DIR / "logo_image.txt"
        try:
            image_string = image_path.read_text()
            ansi_string = image_string.replace("\\e", "\033")
            image = Text.from_ansi(ansi_string)
            side_by_side = Columns([image, text], equal=True, padding=(0, 3))
            yield Padding(side_by_side, (1, 3, 1, 3))
        except FileNotFoundError:
            yield Padding(text, (1, 3, 0, 3))


class RichHelp:
    """Renders the Spirit CLI help description."""

    def __rich_console__(self, console, options):
        yield "[white bold]Spirit Island Template CLI[/white bold]"
        yield ""
        yield "  Compile YAML component definitions to standalone HTML and PNG."
        yield "  Generate card artwork using Google Gemini."
