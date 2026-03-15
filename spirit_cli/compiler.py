"""Compiler pipeline: YAML -> validated model -> HTML -> PNG."""

from __future__ import annotations

import asyncio
import re
import shutil
from pathlib import Path

import yaml

from spirit_cli.html_builder import build_html
from spirit_cli.models import (
    AdversaryModel,
    AspectModel,
    BoardFrontModel,
    BoardLoreModel,
    CardBackModel,
    CardModel,
    ComponentModel,
    parse_component,
)

# Fields that reference image files, per model type
IMAGE_FIELDS: dict[str, list[str | tuple[str, str]]] = {
    "card": ["image"],
    "board_front": ["spirit_image", "spirit_border"],
    "board_lore": ["spirit_image"],
    "adversary": ["flag_image"],
    "aspect": [],
    "card_back": ["image"],
}

# Viewport sizes for Playwright rendering
VIEWPORTS: dict[str, dict[str, int]] = {
    "card": {"width": 800, "height": 1200},
    "board_front": {"width": 1800, "height": 1200},
    "board_lore": {"width": 1800, "height": 1200},
    "adversary": {"width": 1200, "height": 1600},
    "aspect": {"width": 1200, "height": 800},
    "card_back": {"width": 800, "height": 1200},
}

# CSS selectors for element-level screenshots
SELECTORS: dict[str, str] = {
    "card": "card",
    "board_front": "board",
    "board_lore": "board",
    "adversary": "adversary",
    "aspect": "body",
    "card_back": "card-back",
}


def slugify(name: str) -> str:
    """Convert a name to a filesystem-friendly slug."""
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def get_component_name(model: ComponentModel) -> str:
    """Extract the display name from a component model."""
    if isinstance(model, CardModel):
        return model.name
    if isinstance(model, BoardFrontModel):
        return model.spirit_name
    if isinstance(model, BoardLoreModel):
        return model.spirit_name
    if isinstance(model, AdversaryModel):
        return model.name
    if isinstance(model, AspectModel):
        return model.aspect_name
    if isinstance(model, CardBackModel):
        return model.name
    return "component"


# Type suffixes to disambiguate components that share the same name
_TYPE_SUFFIXES: dict[str, str] = {
    "board_front": "-front",
    "board_lore": "-lore",
}


def get_output_slug(model: ComponentModel) -> str:
    """Get a unique output slug including type suffix where needed."""
    name = get_component_name(model)
    suffix = _TYPE_SUFFIXES.get(model.type, "")
    return slugify(name) + suffix


def _collect_image_paths(model: ComponentModel) -> list[str]:
    """Collect all image file paths referenced by the model."""
    paths: list[str] = []
    component_type = model.type

    for field_name in IMAGE_FIELDS.get(component_type, []):
        value = getattr(model, field_name, None)
        if value:
            paths.append(value)

    # Presence track banners (board_front)
    if isinstance(model, BoardFrontModel):
        for track in [
            model.presence_tracks.energy_track,
            model.presence_tracks.card_play_track,
        ]:
            if track.banner:
                paths.append(track.banner)

    # Aspect back image
    if isinstance(model, AspectModel) and model.aspect_back:
        paths.append(model.aspect_back.src)

    return paths


def _rewrite_image_paths(model: ComponentModel) -> None:
    """Rewrite image paths on the model to just basenames (after copying)."""
    component_type = model.type
    for field_name in IMAGE_FIELDS.get(component_type, []):
        value = getattr(model, field_name, None)
        if value and not value.startswith(("http://", "https://", "data:")):
            setattr(model, field_name, Path(value).name)

    if isinstance(model, BoardFrontModel):
        for track in [
            model.presence_tracks.energy_track,
            model.presence_tracks.card_play_track,
        ]:
            if track.banner and not track.banner.startswith(("http://", "https://", "data:")):
                track.banner = Path(track.banner).name

    if isinstance(model, AspectModel) and model.aspect_back:
        if not model.aspect_back.src.startswith(("http://", "https://", "data:")):
            model.aspect_back.src = Path(model.aspect_back.src).name


def copy_assets(
    model: ComponentModel,
    yaml_dir: Path,
    output_dir: Path,
) -> None:
    """Copy referenced image files from the YAML directory to the output directory."""
    for rel_path in _collect_image_paths(model):
        if rel_path.startswith(("http://", "https://", "data:")):
            continue
        src = yaml_dir / rel_path
        if src.exists():
            dst = output_dir / src.name
            if src.resolve() != dst.resolve():
                shutil.copy2(src, dst)

    # Copy custom icon images
    custom_icons = getattr(model, "custom_icons", {})
    for icon_path in custom_icons.values():
        if icon_path.startswith(("http://", "https://", "data:")):
            continue
        src = yaml_dir / icon_path
        if src.exists():
            dst = output_dir / src.name
            if src.resolve() != dst.resolve():
                shutil.copy2(src, dst)


def _build_custom_icon_css(model: ComponentModel) -> str:
    """Generate CSS rules for custom icons."""
    custom_icons = getattr(model, "custom_icons", {})
    if not custom_icons:
        return ""
    rules = []
    for icon_name, icon_path in custom_icons.items():
        filename = Path(icon_path).name
        rules.append(f"icon.{icon_name}{{background-image: url('{filename}'); }}")
    return "\n".join(rules)


def find_project_root(from_path: Path) -> Path:
    """Walk up from a path to find the project root (contains _global/)."""
    current = from_path.resolve()
    if current.is_file():
        current = current.parent
    while current != current.parent:
        if (current / "_global").is_dir():
            return current
        current = current.parent
    raise FileNotFoundError(
        "Could not find project root (directory containing _global/)"
    )


async def _render_png(html_path: Path, png_path: Path, component_type: str) -> None:
    """Render HTML to PNG using Playwright headless Chromium."""
    from playwright.async_api import async_playwright

    viewport = VIEWPORTS.get(component_type, {"width": 1600, "height": 1200})

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_viewport_size(viewport)
        await page.goto(f"file://{html_path.resolve()}")

        # Wait for JS rendering (existing JS uses setTimeout for dynamic sizing)
        await page.wait_for_timeout(2000)

        selector = SELECTORS.get(component_type, "body")
        element = await page.query_selector(selector)
        if element:
            await element.screenshot(path=str(png_path))
        else:
            await page.screenshot(path=str(png_path))

        await browser.close()


def render_png(html_path: Path, png_path: Path, component_type: str) -> None:
    """Synchronous wrapper for PNG rendering."""
    asyncio.run(_render_png(html_path, png_path, component_type))


def compile_component(
    yaml_path: Path,
    project_root: Path | None = None,
    output_dir: Path | None = None,
) -> Path:
    """Full pipeline: YAML -> validated model -> HTML -> copy assets -> PNG.

    Args:
        yaml_path: Path to the YAML component file.
        project_root: Project root (auto-detected if None).
        output_dir: Override output directory. If None, uses output/<slug>/.

    Returns the output directory path.
    """
    yaml_path = yaml_path.resolve()
    if project_root is None:
        project_root = find_project_root(yaml_path)

    # 1. Load and validate YAML
    raw = yaml.safe_load(yaml_path.read_text())
    model = parse_component(raw)

    # 2. Determine output directory and file slug
    slug = get_output_slug(model)
    if output_dir is None:
        output_dir = project_root / "output" / slug
    output_dir.mkdir(parents=True, exist_ok=True)

    # 3. Copy referenced images from YAML dir to output dir
    copy_assets(model, yaml_path.parent, output_dir)

    # 3b. Rewrite image paths to basenames (since assets are now in output dir)
    _rewrite_image_paths(model)

    # 4. Generate HTML (adjust global_prefix based on output depth)
    depth = len(output_dir.relative_to(project_root).parts)
    global_prefix = "/".join([".."] * depth) + "/_global"
    custom_styles = _build_custom_icon_css(model)
    html_content = build_html(model, global_prefix=global_prefix, custom_styles=custom_styles)

    html_path = output_dir / f"{slug}.html"
    html_path.write_text(html_content)

    # 5. Render PNG via Playwright
    png_path = output_dir / f"{slug}.png"
    render_png(html_path, png_path, model.type)

    return output_dir
