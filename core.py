from dataclasses import dataclass, field
from typing import Callable


@dataclass
class SavedCharacter:
    name: str
    classes: list
    abilities: dict
    proficiencies: dict
    inventory: dict
    equipment: dict
    features: list
    spells: dict
    state: dict


@dataclass
class EffectiveCharacter:
    abilities: dict
    proficiencies: dict
    combat: dict
    spells: dict
    features: set
    # More derived sections get added as needed.

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class SavedCharacter:
    """
    Persistent representation of a character.

    This object should contain only information that is stored in
    the character file. Derived values belong in EffectiveCharacter.
    """

    name: str
    classes: list[dict[str, Any]]
    abilities: dict[str, Any]
    proficiencies: dict[str, Any]
    inventory: dict[str, Any]
    equipment: dict[str, Any]
    features: list[str]
    spells: dict[str, Any]
    state: dict[str, Any]

    def active_sources(self):
        sources = []

        # Classes
        for class_data in self.classes:
            sources.append(
                CLASSES[class_data["name"]](class_data)
            )

        # Features
        for feature_id in self.features:
            sources.append(FEATURES[feature_id]())

        # Equipped items
        for item_id in self.equipment.get("worn", []):
            sources.append(ITEMS[item_id]())

        armor = self.equipment.get("armor")
        if armor:
            sources.append(ITEMS[armor]())

        shield = self.equipment.get("shield")
        if shield:
            sources.append(ITEMS[shield]())

        return sources


@dataclass
class EffectiveCharacter:
    """
    Temporary, calculated representation of a character.

    This object is rebuilt from SavedCharacter whenever the character
    needs to be recalculated. It should never be serialized.
    """

    abilities: dict[str, int] = field(default_factory=dict)

    # These will be populated as we implement later steps.
    proficiencies: dict[str, Any] = field(default_factory=dict)
    combat: dict[str, Any] = field(default_factory=dict)
    spells: dict[str, Any] = field(default_factory=dict)
    features: set[str] = field(default_factory=set)


def load_character(path: str | Path) -> SavedCharacter:
    """
    Load a character from a Markdown file containing YAML front matter.

    For now, this expects the entire file to be YAML. We'll add Markdown
    front-matter handling separately if desired.
    """

    path = Path(path)

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise ValueError(f"Character file must contain a YAML mapping: {path}")

    return SavedCharacter(
        name=data.get("name", ""),
        classes=data.get("classes", []),
        abilities=data.get("abilities", {}),
        proficiencies=data.get("proficiencies", {}),
        inventory=data.get("inventory", {}),
        equipment=data.get("equipment", {}),
        features=data.get("features", []),
        spells=data.get("spells", {}),
        state=data.get("state", {}),
    )


def create_effective_character(
    character: SavedCharacter,
) -> EffectiveCharacter:
    """
    Create the initial effective character from persistent character data.

    At this stage we only copy the base ability scores. Rules/effects
    will modify the effective character in later steps.
    """

    base_abilities = character.abilities.get("base", {})

    return EffectiveCharacter(
        abilities=base_abilities.copy(),
    )


@dataclass
class CalculationContext:
    saved: SavedCharacter
    effective: EffectiveCharacter


@dataclass
class Update:
    priority: int
    source: str
    function: Callable[[CalculationContext], None]


def calculate(character: SavedCharacter) -> EffectiveCharacter:

    effective = EffectiveCharacter(
        abilities=character.abilities["base"].copy(),
        proficiencies={},
        combat={},
        spells={},
        features=set(),
    )

    context = CalculationContext(
        saved=character,
        effective=effective,
    )

    updates = standard_updates(character)

    for source in character.active_sources():
        updates.extend(source.get_updates())

    updates.sort(key=lambda update: update.priority)

    for update in updates:
        update.function(context)

    return effective





from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml


# ---------------------------------------------------------------------------
# Priority levels
# ---------------------------------------------------------------------------

BASE = 100
MODIFIERS = 200
DERIVED = 300
FINAL = 400


# ---------------------------------------------------------------------------
# Persistent character
# ---------------------------------------------------------------------------

@dataclass
class SavedCharacter:
    """
    Persistent representation of a character.

    This is the data that gets saved to YAML.
    """

    name: str
    classes: list[dict[str, Any]]
    abilities: dict[str, Any]
    proficiencies: dict[str, Any]
    inventory: dict[str, Any]
    equipment: dict[str, Any]
    features: list[str]
    spells: dict[str, Any]
    state: dict[str, Any]


# ---------------------------------------------------------------------------
# Effective character
# ---------------------------------------------------------------------------

@dataclass
class Abilities:
    """
    Ability scores and their calculated modifiers.
    """

    strength: int = 0
    dexterity: int = 0
    constitution: int = 0
    intelligence: int = 0
    wisdom: int = 0
    charisma: int = 0

    strength_modifier: int = 0
    dexterity_modifier: int = 0
    constitution_modifier: int = 0
    intelligence_modifier: int = 0
    wisdom_modifier: int = 0
    charisma_modifier: int = 0


@dataclass
class EffectiveCharacter:
    """
    Temporary calculated representation.

    This object is recreated whenever the character is recalculated.
    It is never saved directly.
    """

    abilities: Abilities

    proficiencies: dict[str, Any] = field(default_factory=dict)
    combat: dict[str, Any] = field(default_factory=dict)
    spells: dict[str, Any] = field(default_factory=dict)
    features: set[str] = field(default_factory=set)


# ---------------------------------------------------------------------------
# Calculation system
# ---------------------------------------------------------------------------

@dataclass
class CalculationContext:
    saved: SavedCharacter
    effective: EffectiveCharacter


@dataclass
class Update:
    """
    A single modification to the effective character.
    """

    priority: int
    source: str
    function: Callable[[CalculationContext], None]


# ---------------------------------------------------------------------------
# YAML loading
# ---------------------------------------------------------------------------

def load_character(path: str | Path) -> SavedCharacter:
    path = Path(path)

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise ValueError(
            f"Character file must contain a YAML mapping: {path}"
        )

    return SavedCharacter(
        name=data.get("name", ""),
        classes=data.get("classes", []),
        abilities=data.get("abilities", {}),
        proficiencies=data.get("proficiencies", {}),
        inventory=data.get("inventory", {}),
        equipment=data.get("equipment", {}),
        features=data.get("features", []),
        spells=data.get("spells", {}),
        state=data.get("state", {}),
    )


# ---------------------------------------------------------------------------
# Effective character creation
# ---------------------------------------------------------------------------

def create_effective_character(
    character: SavedCharacter,
) -> EffectiveCharacter:

    base = character.abilities.get("base", {})

    abilities = Abilities(
        strength=base.get("strength", 0),
        dexterity=base.get("dexterity", 0),
        constitution=base.get("constitution", 0),
        intelligence=base.get("intelligence", 0),
        wisdom=base.get("wisdom", 0),
        charisma=base.get("charisma", 0),
    )

    return EffectiveCharacter(
        abilities=abilities,
    )


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------

def ability_modifier(score: int) -> int:
    """
    D&D ability modifier.

    Python's // operator gives the desired behavior for negative values.
    """

    return (score - 10) // 2


def update_ability_modifiers(ctx: CalculationContext) -> None:
    """
    Calculate all six ability modifiers.

    This deliberately runs after effects that modify ability scores.
    """

    abilities = ctx.effective.abilities

    abilities.strength_modifier = ability_modifier(
        abilities.strength
    )

    abilities.dexterity_modifier = ability_modifier(
        abilities.dexterity
    )

    abilities.constitution_modifier = ability_modifier(
        abilities.constitution
    )

    abilities.intelligence_modifier = ability_modifier(
        abilities.intelligence
    )

    abilities.wisdom_modifier = ability_modifier(
        abilities.wisdom
    )

    abilities.charisma_modifier = ability_modifier(
        abilities.charisma
    )


# ---------------------------------------------------------------------------
# Item rules
# ---------------------------------------------------------------------------

class AmuletOfHealth:
    """
    Amulet of Health:

    Your Constitution score is 19 while wearing the amulet.
    """

    def get_updates(self) -> list[Update]:
        return [
            Update(
                priority=BASE,
                source="Amulet of Health",
                function=self.update_constitution,
            )
        ]

    @staticmethod
    def update_constitution(ctx: CalculationContext) -> None:
        ctx.effective.abilities.constitution = max(
            ctx.effective.abilities.constitution,
            19,
        )


# ---------------------------------------------------------------------------
# Rules registry
# ---------------------------------------------------------------------------

ITEMS = {
    "amulet_of_health": AmuletOfHealth,
}


# ---------------------------------------------------------------------------
# Active sources
# ---------------------------------------------------------------------------

def get_active_sources(
    character: SavedCharacter,
) -> list[Any]:
    """
    Return rule objects representing things currently affecting
    the character.

    At this stage we only implement equipped worn items.
    """

    sources = []

    for item_id in character.equipment.get("worn", []):
        item_class = ITEMS.get(item_id)

        if item_class is None:
            continue

        sources.append(item_class())

    return sources


# ---------------------------------------------------------------------------
# Standard updates
# ---------------------------------------------------------------------------

def standard_updates(
    character: SavedCharacter,
) -> list[Update]:

    return [
        Update(
            priority=MODIFIERS,
            source="Ability modifiers",
            function=update_ability_modifiers,
        )
    ]


# ---------------------------------------------------------------------------
# Collect updates
# ---------------------------------------------------------------------------

def collect_updates(
    character: SavedCharacter,
) -> list[Update]:

    updates = []

    # Rules that are always part of the character calculation.
    updates.extend(standard_updates(character))

    # Rules supplied by active character sources.
    for source in get_active_sources(character):
        updates.extend(source.get_updates())

    # Lower priority numbers run first.
    updates.sort(key=lambda update: update.priority)

    return updates


# ---------------------------------------------------------------------------
# Calculate
# ---------------------------------------------------------------------------

def calculate(
    character: SavedCharacter,
) -> EffectiveCharacter:

    effective = create_effective_character(character)

    context = CalculationContext(
        saved=character,
        effective=effective,
    )

    for update in collect_updates(character):
        update.function(context)

    return effective