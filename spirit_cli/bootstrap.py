"""Scaffold a new spirit folder with template YAML files."""

from __future__ import annotations

import re
from pathlib import Path


def _slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def _card_slug(index: int, name: str) -> str:
    return f"card-{index}"


BOARD_FRONT_TEMPLATE = """\
type: board_front
spirit_name: "{name}"
spirit_image: ""
spirit_image_scale: "100%"
spirit_image_position: "left top"

custom_icons: {{}}

special_rules:
  - subtitle: "Special Rule Name"
    rule: >
      Describe the special rule here.

growth:
  title: "Growth (Pick Two)"
  groups:
    - values: "reclaim-all"
    - values: "add-presence(1)"
    - values: "gain-power-card"
    - values: "gain-energy(2)"

presence_tracks:
  energy_track:
    values: "1,2,3,4,5"
  card_play_track:
    values: "1,2,2,3,4"

innate_powers:
  - name: "Innate Power Name"
    speed: fast
    range: "1"
    target: "ANY"
    target_title: "TARGET LAND"
    levels:
      - threshold: "1-sun"
        content: "Effect at first threshold."
      - threshold: "2-sun,1-fire"
        content: "Effect at second threshold."

art_prompt: ""
"""

BOARD_LORE_TEMPLATE = """\
type: board_lore
spirit_name: "{name}"
spirit_image: ""

lore_description: >
  Describe the spirit's lore and backstory here.

setup:
  title: "SETUP:"
  description: >
    Describe the setup instructions here.

play_style:
  title: "Play Style:"
  description: >
    Describe the play style here.

complexity:
  value: 2
  descriptor: "Moderate"

summary_of_powers:
  values: [3, 3, 3, 3, 3]
"""

CARD_TEMPLATE = """\
type: card
name: "Card Name {index}"
speed: fast
cost: 1
image: ""
artist_name: ""
elements:
  - sun
range: "1"
target: "ANY"
target_title: "TARGET LAND"
custom_icons: {{}}
rules: |
  Describe the card effect here.
art_prompt: ""
"""

CARD_BACK_TEMPLATE = """\
type: card_back
name: "{slug}-card-back"
image: ""
image_position: "center center"
art_prompt: ""
"""


def bootstrap_spirit(name: str, num_cards: int, output_dir: Path) -> Path:
    """Create a new spirit folder with template YAML files.

    Args:
        name: The spirit name (e.g., "Ember of Dawn").
        num_cards: Number of power card templates to create.
        output_dir: Base directory where the spirit folder will be created.

    Returns:
        Path to the created spirit directory.
    """
    slug = _slugify(name)
    spirit_dir = output_dir / slug
    spirit_dir.mkdir(parents=True, exist_ok=True)

    # Board front
    (spirit_dir / "board_front.yaml").write_text(
        BOARD_FRONT_TEMPLATE.format(name=name)
    )

    # Board lore
    (spirit_dir / "board_lore.yaml").write_text(
        BOARD_LORE_TEMPLATE.format(name=name)
    )

    # Card back
    (spirit_dir / "card_back.yaml").write_text(
        CARD_BACK_TEMPLATE.format(slug=slug)
    )

    # Power cards
    for i in range(1, num_cards + 1):
        filename = f"card-{i}.yaml"
        (spirit_dir / filename).write_text(
            CARD_TEMPLATE.format(index=i)
        )

    return spirit_dir
