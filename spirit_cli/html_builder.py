"""Generate standalone HTML from validated component models."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from jinja2 import Environment, FileSystemLoader

if TYPE_CHECKING:
    from spirit_cli.models import ComponentModel

TEMPLATES_DIR = Path(__file__).parent / "templates"

# Map component type -> (template file, css files, js files)
COMPONENT_CONFIG: dict[str, tuple[str, list[str], list[str]]] = {
    "card": ("card.html.j2", ["card.css"], ["card.js"]),
    "board_front": ("board_front.html.j2", ["board_front.css"], ["board_front.js"]),
    "board_lore": ("board_lore.html.j2", ["board_lore.css"], ["board_lore.js"]),
    "adversary": ("adversary.html.j2", ["adversary.css"], ["adversary.js"]),
    "aspect": ("aspect.html.j2", ["aspect.css"], ["board_front.js", "aspect.js"]),
    "card_back": ("card_back.html.j2", ["card-back.css"], []),
}


def build_html(
    model: ComponentModel,
    global_prefix: str = "../../_global",
    custom_styles: str = "",
) -> str:
    """Render a component model to standalone HTML."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,
        keep_trailing_newline=True,
    )

    component_type = model.type
    config = COMPONENT_CONFIG[component_type]
    template_name, css_files, js_files = config

    template = env.get_template(template_name)
    return template.render(
        component=model,
        global_prefix=global_prefix,
        css_files=css_files,
        js_files=js_files,
        custom_styles=custom_styles,
    )
