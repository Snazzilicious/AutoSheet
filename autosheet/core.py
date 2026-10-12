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
    hp_rolls: list[int] = field(default_factory=list)
    classes: list[dict[str, Any]] = field(default_factory=list)
    abilities: dict[str, Any] = field(default_factory=dict)
    proficiencies: dict[str, Any] = field(default_factory=dict)
    inventory: dict[str, Any] = field(default_factory=dict)
    equipment: dict[str, Any] = field(default_factory=dict)
    features: list[str] = field(default_factory=list)
    spells: dict[str, Any] = field(default_factory=dict)
    state: dict[str, Any] = field(default_factory=dict)

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


def _saved_character_dict(character: SavedCharacter) -> dict[str, Any]:
    return {
        "name": character.name,
        "hp_rolls": character.hp_rolls,
        "classes": character.classes,
        "abilities": character.abilities,
        "proficiencies": character.proficiencies,
        "inventory": character.inventory,
        "equipment": character.equipment,
        "features": character.features,
        "spells": character.spells,
        "state": character.state,
    }


def save_character(character: SavedCharacter, path: str | Path) -> None:
    """
    Save character state to a YAML file.
    """
    path = Path(path)
    data = _saved_character_dict(character)
    with path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(data, file, sort_keys=False)


def save_character_with_effective(character: SavedCharacter, effective: EffectiveCharacter, path: str | Path | Any) -> None:
    """
    Save both the saved character and calculated effective character as a multi-document YAML file or stream.
    """
    saved_data = _saved_character_dict(character)
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
        "hit_dice": {
            k: (v.max_uses if hasattr(v, "max_uses") else v)
            for k, v in effective.hit_dice.items()
        },
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
    if hasattr(path, "write"):
        yaml.safe_dump_all([saved_data, effective_data], path, sort_keys=False)
    else:
        path = Path(path)
        with path.open("w", encoding="utf-8") as file:
            yaml.safe_dump_all([saved_data, effective_data], file, sort_keys=False)


def load_character(path: str | Path) -> SavedCharacter:
    """
    Load a character from a YAML file.
    """
    path = Path(path)

    with path.open("r", encoding="utf-8") as file:
        documents = list(yaml.safe_load_all(file))

    if not documents or not isinstance(documents[0], dict):
        raise ValueError(f"Character file must contain a YAML mapping: {path}")

    data = documents[0]

    return SavedCharacter(
        name=data.get("name", ""),
        hp_rolls=data.get("hp_rolls", []),
        classes=data.get("classes", []),
        abilities=data.get("abilities", {}),
        proficiencies=data.get("proficiencies", {}),
        inventory=data.get("inventory", {}),
        equipment=data.get("equipment", {}),
        features=data.get("features", []),
        spells=data.get("spells", {}),
        state=data.get("state", {}),
    )

