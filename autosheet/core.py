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
        from autosheet.rules import CLASSES, FEATURES, ITEMS

        sources = []

        # Classes and Subclasses
        for class_data in self.classes:
            class_name = class_data.get("name")
            if class_name in CLASSES:
                sources.append(CLASSES[class_name](class_data['level'],class_data['subclass']))
            else:
                print(f"Unknown class: {class_name}")

        # Features
        for feature_id in self.features:
            if feature_id in FEATURES:
                sources.append(FEATURES[feature_id]())
            else:
                print(f"Unknown feature: {feature_id}")

        # Equipped items
        for item_id in self.equipment:
            if item_id in ITEMS:
                sources.append(ITEMS[item_id]())
            else:
                print(f"Unknown item: {item_id}")

        return sources


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
    This object is to be displayed to the player.
    """
    abilities: Abilities
    skills: Skills
    saving_throws: SavingThrows
    armor_class: int
    
    proficiencies: dict[str, Any] = field(default_factory=dict)
    combat: dict[str, Any] = field(default_factory=dict)
    spells: dict[str, Any] = field(default_factory=dict)
    features: set[str] = field(default_factory=set)


@dataclass
class Rule:
    """
    A single modification to the effective character.
    """
    priority: int
    source: str
    function: Callable[[SavedCharacter,EffectiveCharacter], None]


def save_character(character: SavedCharacter, path: str | Path) -> None:
    """
    Save character state to a YAML file.
    """
    path = Path(path)
    data = {
        "name": character.name,
        "classes": character.classes,
        "abilities": character.abilities,
        "proficiencies": character.proficiencies,
        "inventory": character.inventory,
        "equipment": character.equipment,
        "features": character.features,
        "spells": character.spells,
        "state": character.state,
    }
    with path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(data, file, sort_keys=False)


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

