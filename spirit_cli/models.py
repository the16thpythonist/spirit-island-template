"""Pydantic models for YAML component validation."""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, Field


class Speed(str, Enum):
    FAST = "fast"
    SLOW = "slow"


# --- Shared sub-models ---


class SpecialRule(BaseModel):
    subtitle: str
    rule: str


class InnateLevel(BaseModel):
    threshold: str
    content: str
    long: bool = False
    text: bool = False


class InnatePower(BaseModel):
    name: str
    speed: Speed
    range: str
    target: str
    target_title: str = "TARGET LAND"
    note: Optional[str] = None
    levels: list[InnateLevel]


# --- Card ---


class ThresholdData(BaseModel):
    condition: str
    text: Optional[str] = None
    content: str


class CardModel(BaseModel):
    type: Literal["card"]
    name: str
    speed: Speed
    cost: int
    image: str = ""
    elements: list[str] = Field(default_factory=list)
    range: str = "none"
    target: str = "ANY"
    target_title: str = "TARGET LAND"
    artist_name: str = ""
    print_friendly: bool = False
    rules: str = ""
    threshold: Optional[ThresholdData] = None
    custom_icons: dict[str, str] = Field(default_factory=dict)
    art_prompt: Optional[str] = None


# --- Board Front ---


class GrowthGroup(BaseModel):
    values: str
    cost: Optional[int] = None
    tint: Optional[str] = None


class SubGrowth(BaseModel):
    title: str
    bordered: bool = False
    groups: list[GrowthGroup]


class GrowthConfig(BaseModel):
    title: str = "Growth"
    groups: Optional[list[GrowthGroup]] = None
    sub_groups: Optional[list[SubGrowth]] = None


class PresenceTrack(BaseModel):
    values: str
    banner: Optional[str] = None
    banner_v_scale: Optional[str] = None


class PresenceTracks(BaseModel):
    energy_track: PresenceTrack
    card_play_track: PresenceTrack


class BoardFrontModel(BaseModel):
    type: Literal["board_front"]
    spirit_name: str
    artist_name: str = ""
    spirit_image: str = ""
    spirit_image_scale: str = "100%"
    spirit_image_position: str = "left top"
    spirit_border: Optional[str] = None
    special_rules: list[SpecialRule] = Field(default_factory=list)
    growth: GrowthConfig
    presence_tracks: PresenceTracks
    innate_powers: list[InnatePower] = Field(default_factory=list)
    custom_icons: dict[str, str] = Field(default_factory=dict)
    art_prompt: Optional[str] = None


# --- Board Lore ---


class SetupSection(BaseModel):
    title: str = "SETUP:"
    description: str


class PlayStyleSection(BaseModel):
    title: str = "Play Style:"
    description: str


class Complexity(BaseModel):
    value: int
    descriptor: str


class SummaryOfPowers(BaseModel):
    values: list[int] = Field(min_length=5, max_length=5)
    uses: Optional[str] = None


class BoardLoreModel(BaseModel):
    type: Literal["board_lore"]
    spirit_name: str
    spirit_image: str = ""
    lore_description: str = ""
    setup: Optional[SetupSection] = None
    play_style: Optional[PlayStyleSection] = None
    complexity: Optional[Complexity] = None
    summary_of_powers: Optional[SummaryOfPowers] = None
    custom_icons: dict[str, str] = Field(default_factory=dict)
    art_prompt: Optional[str] = None


# --- Adversary ---


class LossCondition(BaseModel):
    name: str
    rules: str


class EscalationEffect(BaseModel):
    name: str
    rules: str


class AdversaryLevel(BaseModel):
    difficulty: int
    fear_cards: str
    name: str
    rules: str


class AdversaryModel(BaseModel):
    type: Literal["adversary"]
    name: str
    base_difficulty: int
    flag_image: str = ""
    loss_condition: LossCondition
    escalation_effect: EscalationEffect
    levels: list[AdversaryLevel] = Field(min_length=1, max_length=6)
    custom_icons: dict[str, str] = Field(default_factory=dict)
    art_prompt: Optional[str] = None


# --- Aspect ---


class AspectBack(BaseModel):
    spirit_name: str
    src: str


class AspectModel(BaseModel):
    type: Literal["aspect"]
    aspect_name: str
    aspect_subtext: str = ""
    special_rules: list[SpecialRule] = Field(default_factory=list)
    innate_powers: list[InnatePower] = Field(default_factory=list)
    aspect_back: Optional[AspectBack] = None
    custom_icons: dict[str, str] = Field(default_factory=dict)
    art_prompt: Optional[str] = None


# --- Card Back ---


class CardBackModel(BaseModel):
    type: Literal["card_back"]
    name: str = "card-back"
    image: str
    image_position: str = "center center"
    art_prompt: Optional[str] = None


# --- Discriminated union ---

ComponentModel = Annotated[
    Union[CardModel, BoardFrontModel, BoardLoreModel, AdversaryModel, AspectModel, CardBackModel],
    Field(discriminator="type"),
]


def parse_component(data: dict) -> ComponentModel:
    """Parse a raw dict (from YAML) into a validated component model."""
    # Use the adapter approach for discriminated unions
    from pydantic import TypeAdapter

    adapter = TypeAdapter(ComponentModel)
    return adapter.validate_python(data)
