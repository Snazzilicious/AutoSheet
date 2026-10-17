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
        from autosheet.rules import CLASSES, FEATURES, ITEMS, SPELLS

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

        # Equipped items (agnostic to equipped status, only gathered if in equipment)
        for item_id in self.equipment:
            if item_id in ITEMS:
                sources.append(ITEMS[item_id]())
            else:
                print(f"Unknown item: {item_id}")

        # Readied spells (agnostic to readied status, only gathered if in readied list)
        for spell_id in self.spells.get("readied", []):
            if spell_id in SPELLS:
                sources.append(SPELLS[spell_id]())
            else:
                print(f"Unknown spell: {spell_id}")

        return sources



@dataclass
class HitPoints:
    max: int = 0
    current: int = 0
    temporary: int = 0

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
class SavingThrows:
    strength: int = 0
    dexterity: int = 0
    constitution: int = 0
    intelligence: int = 0
    wisdom: int = 0
    charisma: int = 0

@dataclass
class Skills:
    athletics: int = 0
    acrobatics: int = 0
    sleight_of_hand: int = 0
    stealth: int = 0
    arcana: int = 0
    history: int = 0
    investigation: int = 0
    nature: int = 0
    religion: int = 0
    animal_handling: int = 0
    insight: int = 0
    medicine: int = 0
    perception: int = 0
    survival: int = 0
    deception: int = 0
    intimidation: int = 0
    performance: int = 0
    persuasion: int = 0

@dataclass
class Feature:
    """
    An entry in EffectiveCharacter's feature list
    Has a short name for display
    Provides a description of the feature
    """
    name: str = ""
    description: str = ""

class Resource:
    """
    Rechargable consumable required to use abilities.
    """
    recharge_events = set()

    def __init__(self, name, max_uses: int, remaining_uses: int = -1, recharge_events: set[str] | None = None, recharge_event: str | None = None):
        self.name = name
        self.max_uses = max_uses
        self.remaining_uses = remaining_uses
        if self.remaining_uses < 0:
            self.remaining_uses = max_uses
        if recharge_events is not None:
            self.recharge_events = set(recharge_events)
        elif recharge_event is not None:
            self.recharge_events = {recharge_event}
        elif hasattr(self, "recharge_events") and isinstance(self.recharge_events, set):
            self.recharge_events = set(self.recharge_events)
        else:
            self.recharge_events = set()

    def recharge(self, recharge_event=None):
        if recharge_event is None or recharge_event in self.recharge_events:
            self.remaining_uses = self.max_uses
    
    def use(self,n_uses=1):
        self.remaining_uses -= n_uses
        self.remaining_uses = max(0, self.remaining_uses)
    
    def __str__(self):
        return f"{self.name:<20s}:{self.remaining_uses:<2d} / {self.max_uses:<2d}"

@dataclass
class CharacterAction:
    """
    An entry in the EffectiveCharacter's action list
    Has a short name for display
    Provides a description of the action
    Includes 'cost'
    """
    name: str
    cost: str = "Action"
    description: str = ""

class Attack(CharacterAction):
    def __init__(self, name, range="5 ft", atk_bonus=0, dmg_die="1d8", dmg_mod=0, dmg_type="slashing", cost="Action"):
        description = f"Range {range}, +{atk_bonus} to hit, {dmg_die}+{dmg_mod} {dmg_type} damage"
        super().__init__(name, cost, description)

class Spell(CharacterAction):
    def __init__(
        self,
        name: str,
        level: int = 1,
        cost: str = "1 Action",
        range: str = "60 ft",
        duration: str = "Instantaneous",
        concentration: bool = False,
        atk_bonus: int | None = None,
        save: str | None = None,
        dmg_die: str | None = None,
        dmg_mod: int = 0,
        dmg_type: str | None = None,
        school: str = "",
    ):
        self.level = level
        self.school = school
        self.casting_time = cost
        self.range = range
        self.duration = duration
        self.concentration = concentration
        
        parts = []
        parts.append(f"Level {level}" if level > 0 else "Cantrip")
        if school:
            parts.append(school)
        parts.append(f"Range: {range}")
        parts.append(f"Casting: {cost}")
        
        dur_str = f"Duration: {'Concentration, ' if concentration else ''}{duration}"
        parts.append(dur_str)
        
        if atk_bonus is not None:
            parts.append(f"+{atk_bonus} to hit")
        if save:
            parts.append(f"Save: {save}")
        if dmg_die and dmg_type:
            mod_str = f"+{dmg_mod}" if dmg_mod else ""
            parts.append(f"Damage: {dmg_die}{mod_str} {dmg_type}")

        description = ", ".join(parts)
        super().__init__(name, cost, description)



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
    passive_perception: int = 10
    
    hit_points: HitPoints = field(default_factory=HitPoints)
    
    abilities: AbilityScores = field(default_factory=AbilityScores)
    ability_modifiers: AbilityModifiers = field(default_factory=AbilityModifiers)
    
    saving_throws: dict[str, int] = field(default_factory=dict)
    skills: dict[str, int] = field(default_factory=dict)

    features: dict[str, Feature] = field(default_factory=dict)
    resources: dict[str, Resource] = field(default_factory=dict) # move hit dice, spell_slots in here
    actions: dict[str, CharacterAction] = field(default_factory=dict)
    attacks: dict[str, Attack] = field(default_factory=dict)
    spells: dict[str, Spell] = field(default_factory=dict)
    
    # conditions: list[str] = field(default_factory=list)
    # active_effects: list[str] = field(default_factory=list)


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
        "passive_perception": effective.passive_perception,
        "hit_points": {
            "max": effective.hit_points.max,
            "current": effective.hit_points.current,
            "temporary": effective.hit_points.temporary,
        },
        "resources": {
            k: {"max_uses": v.max_uses, "remaining_uses": v.remaining_uses}
            for k, v in effective.resources.items()
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
        "features": sorted(list(effective.features.keys())),
        "actions": {k: {"name": v.name, "cost": v.cost, "description": v.description} for k, v in effective.actions.items()},
        "attacks": {k: {"name": v.name, "cost": v.cost, "description": v.description} for k, v in effective.attacks.items()},
        "spells": {k: {"name": v.name, "cost": v.cost, "description": v.description} for k, v in effective.spells.items()},
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



# @dataclass
# class CharacterAction(Rule):
#     """
#     An entry in the EffectiveCharacter's action list
#     Has a short name for display
#     Provides a description of the action
#     Includes 'cost'
#     """
#     name: str
#     brief: str
#     cost: str
#     description: str = ""
#     # add self to actions list