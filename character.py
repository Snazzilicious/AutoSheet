from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml


# Priority levels
BASE = 100
MODIFIERS = 200
DERIVED = 300
FINAL = 400


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

    def active_sources(self) -> list[Any]:
        """
        Return rule objects representing things currently affecting the character.
        """
        sources = []

        # Classes
        for class_data in self.classes:
            class_name = class_data.get("name")
            if class_name in CLASSES:
                sources.append(CLASSES[class_name](class_data))

        # Features
        for feature_id in self.features:
            if feature_id in FEATURES:
                sources.append(FEATURES[feature_id]())

        # Equipped items (worn)
        for item_id in self.equipment.get("worn", []):
            item_class = ITEMS.get(item_id)
            if item_class is not None:
                sources.append(item_class())

        # Armor
        armor = self.equipment.get("armor")
        if armor:
            item_class = ITEMS.get(armor)
            if item_class is not None:
                sources.append(item_class())

        # Shield
        shield = self.equipment.get("shield")
        if shield:
            item_class = ITEMS.get(shield)
            if item_class is not None:
                sources.append(item_class())

        return sources


def get_active_sources(character: SavedCharacter) -> list[Any]:
    return character.active_sources()


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
    Temporary calculated representation of a character.
    """

    abilities: Abilities
    proficiencies: dict[str, Any] = field(default_factory=dict)
    combat: dict[str, Any] = field(default_factory=dict)
    spells: dict[str, Any] = field(default_factory=dict)
    features: set[str] = field(default_factory=set)


def load_character(path: str | Path) -> SavedCharacter:
    """
    Load a character from a YAML file.
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


def create_effective_character(character: SavedCharacter) -> EffectiveCharacter:
    """
    Create initial effective character from persistent character data.
    """
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
# Rule implementations & Registries
# ---------------------------------------------------------------------------

class AmuletOfHealth:
    """
    Amulet of Health: Your Constitution score is 19 while wearing the amulet.
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


def ability_modifier(score: int) -> int:
    """
    D&D ability modifier calculation.
    """
    return (score - 10) // 2


def update_ability_modifiers(ctx: CalculationContext) -> None:
    """
    Calculate all six ability modifiers.
    """
    abilities = ctx.effective.abilities

    abilities.strength_modifier = ability_modifier(abilities.strength)
    abilities.dexterity_modifier = ability_modifier(abilities.dexterity)
    abilities.constitution_modifier = ability_modifier(abilities.constitution)
    abilities.intelligence_modifier = ability_modifier(abilities.intelligence)
    abilities.wisdom_modifier = ability_modifier(abilities.wisdom)
    abilities.charisma_modifier = ability_modifier(abilities.charisma)


ITEMS = {
    "amulet_of_health": AmuletOfHealth,
}

FEATURES: dict[str, Any] = {}
CLASSES: dict[str, Any] = {}
SUBCLASSES: dict[str, Any] = {}
SPELLS: dict[str, Any] = {}
SPECIES: dict[str, Any] = {}
