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
            subclass_name = class_data.get("subclass")
            level = class_data.get("level", 1)
            if class_name in CLASSES:
                sources.append(CLASSES[class_name](level, subclass_name))
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
                sources.append(ITEMS[item_id](equipped=True))
            else:
                print(f"Unknown item: {item_id}")

        return sources


@dataclass
class AbilityScores:
    strength: int = 0
    dexterity: int = 0
    constitution: int = 0
    intelligence: int = 0
    wisdom: int = 0
    charisma: int = 0


@dataclass
class AbilityModifiers:
    strength: int = 0
    dexterity: int = 0
    constitution: int = 0
    intelligence: int = 0
    wisdom: int = 0
    charisma: int = 0


@dataclass
class HitPoints:
    max: int = 0
    current: int = 0
    temporary: int = 0


@dataclass
class EffectiveCharacter:
    """
    Calculated representation of a character mapped directly to display and YAML output.
    """
    name: str = ""
    level: int = 0
    proficiency_bonus: int = 2
    armor_class: int = 10
    initiative: int = 0
    
    hit_points: HitPoints = field(default_factory=HitPoints)
    hit_dice: dict[str, int] = field(default_factory=dict)
    
    abilities: AbilityScores = field(default_factory=AbilityScores)
    ability_modifiers: AbilityModifiers = field(default_factory=AbilityModifiers)
    
    saving_throws: dict[str, int] = field(default_factory=dict)
    skills: dict[str, int] = field(default_factory=dict)
    spell_slots_max: dict[str, int] = field(default_factory=dict)
    
    features: set[str] = field(default_factory=set)
    conditions: list[str] = field(default_factory=list)
    active_effects: list[dict[str, Any]] = field(default_factory=list)


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


def save_character_with_effective(character: SavedCharacter, effective: EffectiveCharacter, path: str | Path) -> None:
    """
    Save both the saved character and calculated effective character as a multi-document YAML file.
    """
    path = Path(path)
    saved_data = {
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
    effective_data = {
        "name": effective.name,
        "level": effective.level,
        "proficiency_bonus": effective.proficiency_bonus,
        "armor_class": effective.armor_class,
        "initiative": effective.initiative,
        "hit_points": {
            "max": effective.hit_points.max,
            "current": effective.hit_points.current,
            "temporary": effective.hit_points.temporary,
        },
        "hit_dice": effective.hit_dice,
        "abilities": {
            "strength": effective.abilities.strength,
            "dexterity": effective.abilities.dexterity,
            "constitution": effective.abilities.constitution,
            "intelligence": effective.abilities.intelligence,
            "wisdom": effective.abilities.wisdom,
            "charisma": effective.abilities.charisma,
        },
        "ability_modifiers": {
            "strength": effective.ability_modifiers.strength,
            "dexterity": effective.ability_modifiers.dexterity,
            "constitution": effective.ability_modifiers.constitution,
            "intelligence": effective.ability_modifiers.intelligence,
            "wisdom": effective.ability_modifiers.wisdom,
            "charisma": effective.ability_modifiers.charisma,
        },
        "saving_throws": effective.saving_throws,
        "skills": effective.skills,
        "spell_slots_max": effective.spell_slots_max,
        "features": sorted(list(effective.features)),
        "conditions": effective.conditions,
        "active_effects": effective.active_effects,
    }
    with path.open("w", encoding="utf-8") as file:
        yaml.safe_dump_all([saved_data, effective_data], file, sort_keys=False)


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

