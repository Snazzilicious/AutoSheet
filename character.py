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

        # Classes and Subclasses
        for class_data in self.classes:
            class_name = class_data.get("name")
            if class_name in CLASSES:
                sources.append(CLASSES[class_name](class_data))
            subclass_name = class_data.get("subclass")
            if subclass_name in SUBCLASSES:
                sources.append(SUBCLASSES[subclass_name](class_data))

        # Features
        for feature_id in self.features:
            if feature_id in FEATURES:
                sources.append(FEATURES[feature_id]())

        # Equipped items
        for item_id in self.equipment:
            item_class = ITEMS.get(item_id)
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
    abilities = Abilities(
        strength=character.abilities.get("strength", 0),
        dexterity=character.abilities.get("dexterity", 0),
        constitution=character.abilities.get("constitution", 0),
        intelligence=character.abilities.get("intelligence", 0),
        wisdom=character.abilities.get("wisdom", 0),
        charisma=character.abilities.get("charisma", 0),
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


class ScaleMail:
    """
    Scale Mail: Medium armor, AC 14 + Dex modifier (max +2).
    """

    def get_updates(self) -> list[Update]:
        return [
            Update(
                priority=DERIVED,
                source="Scale Mail",
                function=self.update_ac,
            )
        ]

    @staticmethod
    def update_ac(ctx: CalculationContext) -> None:
        dex_mod = ctx.effective.abilities.dexterity_modifier
        armor_ac = 14 + min(dex_mod, 2)
        current_ac = ctx.effective.combat.get("ac", 10 + dex_mod)
        ctx.effective.combat["ac"] = max(current_ac, armor_ac)


class Shield:
    """
    Shield: +2 AC.
    """

    def get_updates(self) -> list[Update]:
        return [
            Update(
                priority=DERIVED + 10,
                source="Shield",
                function=self.update_shield,
            )
        ]

    @staticmethod
    def update_shield(ctx: CalculationContext) -> None:
        ctx.effective.combat["ac"] = ctx.effective.combat.get("ac", 10) + 2


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


def update_proficiency_bonus(ctx: CalculationContext) -> None:
    """
    Calculate proficiency bonus based on total character level.
    """
    total_level = sum(c.get("level", 0) for c in ctx.saved.classes)
    pb = (total_level - 1) // 4 + 2 if total_level > 0 else 2
    ctx.effective.combat["proficiency_bonus"] = pb


def update_base_combat(ctx: CalculationContext) -> None:
    """
    Calculate base unarmored AC and initiative.
    """
    dex_mod = ctx.effective.abilities.dexterity_modifier
    ctx.effective.combat["ac"] = 10 + dex_mod
    ctx.effective.combat["initiative"] = dex_mod


SKILL_ABILITIES = {
    "athletics": "strength",
    "acrobatics": "dexterity",
    "sleight_of_hand": "dexterity",
    "stealth": "dexterity",
    "arcana": "intelligence",
    "history": "intelligence",
    "investigation": "intelligence",
    "nature": "intelligence",
    "religion": "intelligence",
    "animal_handling": "wisdom",
    "insight": "wisdom",
    "medicine": "wisdom",
    "perception": "wisdom",
    "survival": "wisdom",
    "deception": "charisma",
    "intimidation": "charisma",
    "performance": "charisma",
    "persuasion": "charisma",
}


def update_saving_throws(ctx: CalculationContext) -> None:
    """
    Calculate saving throw bonuses.
    """
    abilities = ctx.effective.abilities
    pb = ctx.effective.combat.get("proficiency_bonus", 2)
    prof_saves = set(ctx.saved.proficiencies.get("saving_throws", []))

    ability_map = {
        "strength": abilities.strength_modifier,
        "dexterity": abilities.dexterity_modifier,
        "constitution": abilities.constitution_modifier,
        "intelligence": abilities.intelligence_modifier,
        "wisdom": abilities.wisdom_modifier,
        "charisma": abilities.charisma_modifier,
    }

    saves = {}
    for ability, mod in ability_map.items():
        bonus = mod + (pb if ability in prof_saves else 0)
        saves[ability] = bonus

    ctx.effective.combat["saving_throws"] = saves


def update_skills(ctx: CalculationContext) -> None:
    """
    Calculate skill bonuses.
    """
    abilities = ctx.effective.abilities
    pb = ctx.effective.combat.get("proficiency_bonus", 2)
    skills_data = ctx.saved.proficiencies.get("skills", {})
    prof_skills = set(skills_data.get("proficient", []))
    exp_skills = set(skills_data.get("expertise", []))

    ability_map = {
        "strength": abilities.strength_modifier,
        "dexterity": abilities.dexterity_modifier,
        "constitution": abilities.constitution_modifier,
        "intelligence": abilities.intelligence_modifier,
        "wisdom": abilities.wisdom_modifier,
        "charisma": abilities.charisma_modifier,
    }

    skill_bonuses = {}
    for skill, ability_name in SKILL_ABILITIES.items():
        mod = ability_map.get(ability_name, 0)
        mult = 0
        if skill in exp_skills:
            mult = 2
        elif skill in prof_skills:
            mult = 1
        skill_bonuses[skill] = mod + (mult * pb)

    ctx.effective.combat["skill_bonuses"] = skill_bonuses


CLASS_HIT_DIE = {
    "barbarian": 12,
    "fighter": 10,
    "paladin": 10,
    "ranger": 10,
    "bard": 8,
    "cleric": 8,
    "druid": 8,
    "monk": 8,
    "rogue": 8,
    "warlock": 8,
    "sorcerer": 6,
    "wizard": 6,
}


def update_hp_and_hit_dice(ctx: CalculationContext) -> None:
    """
    Calculate maximum hit points and hit dice.
    """
    con_mod = ctx.effective.abilities.constitution_modifier
    total_hp = 0
    hit_dice = {}

    first_level = True
    for class_data in ctx.saved.classes:
        class_name = class_data.get("name", "").lower()
        level = class_data.get("level", 1)
        die = CLASS_HIT_DIE.get(class_name, 8)
        die_avg = (die // 2) + 1

        class_hp = 0
        for lvl in range(1, level + 1):
            if first_level and lvl == 1:
                class_hp += max(1, die + con_mod)
            else:
                class_hp += max(1, die_avg + con_mod)
        first_level = False
        total_hp += class_hp

        die_key = f"d{die}"
        hit_dice[die_key] = hit_dice.get(die_key, 0) + level

    ctx.effective.combat["hit_point_max"] = total_hp
    ctx.effective.combat["hit_dice"] = hit_dice


def update_spell_slots_and_resources(ctx: CalculationContext) -> None:
    """
    Calculate maximum spell slots and resource maximums.
    """
    spell_slots_max = {}

    for class_data in ctx.saved.classes:
        class_name = class_data.get("name", "").lower()
        level = class_data.get("level", 1)
        if class_name == "warlock":
            slot_level = min(5, (level + 1) // 2)
            slot_count = 3 if level >= 11 else (4 if level >= 17 else 2)
            spell_slots_max[str(slot_level)] = slot_count

    ctx.effective.combat["spell_slots_max"] = spell_slots_max
    ctx.effective.combat["resources_max"] = {}


def update_conditions_and_effects(ctx: CalculationContext) -> None:
    """
    Process active conditions and temporary effects from saved character state.
    """
    state = ctx.saved.state
    conditions = state.get("conditions", [])
    active_effects = state.get("active_effects", [])

    ctx.effective.combat["conditions"] = list(conditions)
    ctx.effective.combat["active_effects"] = list(active_effects)


def standard_updates(character: SavedCharacter) -> list[Update]:
    return [
        Update(
            priority=MODIFIERS,
            source="Ability modifiers",
            function=update_ability_modifiers,
        ),
        Update(
            priority=MODIFIERS,
            source="Proficiency bonus",
            function=update_proficiency_bonus,
        ),
        Update(
            priority=250,
            source="Base combat",
            function=update_base_combat,
        ),
        Update(
            priority=DERIVED,
            source="Saving throws",
            function=update_saving_throws,
        ),
        Update(
            priority=DERIVED,
            source="Skills",
            function=update_skills,
        ),
        Update(
            priority=DERIVED,
            source="HP and Hit Dice",
            function=update_hp_and_hit_dice,
        ),
        Update(
            priority=DERIVED,
            source="Spell Slots and Resources",
            function=update_spell_slots_and_resources,
        ),
        Update(
            priority=DERIVED,
            source="Conditions and Effects",
            function=update_conditions_and_effects,
        ),
    ]


def collect_updates(character: SavedCharacter) -> list[Update]:
    updates = []

    updates.extend(standard_updates(character))

    for source in character.active_sources():
        updates.extend(source.get_updates())

    updates.sort(key=lambda update: update.priority)

    return updates


def calculate(character: SavedCharacter) -> EffectiveCharacter:
    effective = create_effective_character(character)

    context = CalculationContext(
        saved=character,
        effective=effective,
    )

    for update in collect_updates(character):
        update.function(context)

    return effective


class AgonizingBlast:
    def get_updates(self) -> list[Update]:
        return [
            Update(
                priority=FINAL,
                source="Agonizing Blast",
                function=lambda ctx: ctx.effective.features.add("agonizing_blast"),
            )
        ]


class RepellingBlast:
    def get_updates(self) -> list[Update]:
        return [
            Update(
                priority=FINAL,
                source="Repelling Blast",
                function=lambda ctx: ctx.effective.features.add("repelling_blast"),
            )
        ]


class EldritchMind:
    def get_updates(self) -> list[Update]:
        return [
            Update(
                priority=FINAL,
                source="Eldritch Mind",
                function=lambda ctx: ctx.effective.features.add("eldritch_mind"),
            )
        ]


class DevilsSight:
    def get_updates(self) -> list[Update]:
        return [
            Update(
                priority=FINAL,
                source="Devil's Sight",
                function=lambda ctx: ctx.effective.features.add("devils_sight"),
            )
        ]


class WarlockClass:
    def __init__(self, data: dict[str, Any]):
        self.data = data

    def get_updates(self) -> list[Update]:
        return []


class CelestialSubclass:
    def __init__(self, data: dict[str, Any]):
        self.data = data

    def get_updates(self) -> list[Update]:
        return []


ITEMS = {
    "amulet_of_health": AmuletOfHealth,
    "scale_mail": ScaleMail,
    "shield": Shield,
}

FEATURES = {
    "agonizing_blast": AgonizingBlast,
    "repelling_blast": RepellingBlast,
    "eldritch_mind": EldritchMind,
    "devils_sight": DevilsSight,
}

CLASSES = {
    "Warlock": WarlockClass,
}

SUBCLASSES = {
    "Celestial": CelestialSubclass,
}

SPELLS = {
    "hex": "Hex",
    "bless": "Bless",
    "cure_wounds": "Cure Wounds",
}

SPECIES: dict[str, Any] = {}
