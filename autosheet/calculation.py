from typing import Any
from autosheet.core import (
    SavedCharacter,
    EffectiveCharacter,
    AbilityScores,
    AbilityModifiers,
    HitPoints,
    Rule,
    MODIFIERS,
    DERIVED,
)

ABILITIES_LIST = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]


def create_effective_character(character: SavedCharacter) -> EffectiveCharacter:
    """
    Create initial effective character from persistent character data.
    """
    total_level = sum(c.get("level", 0) for c in character.classes)
    scores = {name: character.abilities.get(name, 0) for name in ABILITIES_LIST}
    return EffectiveCharacter(
        name=character.name,
        level=total_level,
        abilities=AbilityScores(**scores),
        ability_modifiers=AbilityModifiers(**{name: ability_modifier(score) for name, score in scores.items()})
    )


def ability_modifier(score: int) -> int:
    """
    D&D ability modifier calculation.
    """
    return (score - 10) // 2


def update_ability_modifiers(saved: SavedCharacter, effective: EffectiveCharacter) -> None:
    """
    Calculate all six ability modifiers.
    """
    ab = effective.abilities
    mods = effective.ability_modifiers
    for name in ABILITIES_LIST:
        score = getattr(ab, name)
        mod = ability_modifier(score)
        setattr(mods, name, mod)


def update_proficiency_bonus(saved: SavedCharacter, effective: EffectiveCharacter) -> None:
    """
    Calculate proficiency bonus based on total character level.
    """
    total_level = effective.level
    pb = (total_level - 1) // 4 + 2 if total_level > 0 else 2
    effective.proficiency_bonus = pb


def update_base_combat(saved: SavedCharacter, effective: EffectiveCharacter) -> None:
    """
    Calculate base unarmored AC and initiative.
    """
    dex_mod = effective.ability_modifiers.dexterity
    effective.armor_class = 10 + dex_mod
    effective.initiative = dex_mod


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


def update_saving_throws(saved: SavedCharacter, effective: EffectiveCharacter) -> None:
    """
    Calculate saving throw bonuses.
    """
    mods = effective.ability_modifiers
    pb = effective.proficiency_bonus
    prof_saves = set(saved.proficiencies.get("saving_throws", []))

    effective.saving_throws = {
        name: getattr(mods, name) + (pb if name in prof_saves else 0)
        for name in ABILITIES_LIST
    }


def update_skills(saved: SavedCharacter, effective: EffectiveCharacter) -> None:
    """
    Calculate skill bonuses.
    """
    mods = effective.ability_modifiers
    pb = effective.proficiency_bonus
    skills_data = saved.proficiencies.get("skills", {})
    prof_skills = set(skills_data.get("proficient", []))
    exp_skills = set(skills_data.get("expertise", []))

    skill_bonuses = {}
    for skill, ability_name in SKILL_ABILITIES.items():
        mod = getattr(mods, ability_name, 0)
        mult = 2 if skill in exp_skills else (1 if skill in prof_skills else 0)
        skill_bonuses[skill] = mod + (mult * pb)

    effective.skills = skill_bonuses


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


def update_hp_and_hit_dice(saved: SavedCharacter, effective: EffectiveCharacter) -> None:
    """
    Calculate maximum hit points and hit dice.
    """
    con_mod = effective.ability_modifiers.constitution
    total_hp = 0
    hit_dice = {}

    first_level = True
    for class_data in saved.classes:
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

    effective.hit_points.max = total_hp
    effective.hit_points.current = saved.state.get("hp", {}).get("current", total_hp)
    effective.hit_dice = hit_dice


def update_spell_slots_and_resources(saved: SavedCharacter, effective: EffectiveCharacter) -> None:
    """
    Calculate maximum spell slots and resource maximums.
    """
    spell_slots_max = {}

    for class_data in saved.classes:
        class_name = class_data.get("name", "").lower()
        level = class_data.get("level", 1)
        if class_name == "warlock":
            slot_level = min(5, (level + 1) // 2)
            slot_count = 3 if level >= 11 else (4 if level >= 17 else 2)
            spell_slots_max[str(slot_level)] = slot_count

    effective.spell_slots_max = spell_slots_max


def update_conditions_and_effects(saved: SavedCharacter, effective: EffectiveCharacter) -> None:
    """
    Process active conditions and temporary effects from saved character state.
    """
    state = saved.state
    conditions = state.get("conditions", [])
    active_effects = state.get("active_effects", [])

    effective.conditions = list(conditions)
    effective.active_effects = list(active_effects)


def standard_updates(character: SavedCharacter) -> list[Rule]:
    return [
        Rule(
            priority=MODIFIERS,
            source="Ability modifiers",
            function=update_ability_modifiers,
        ),
        Rule(
            priority=MODIFIERS,
            source="Proficiency bonus",
            function=update_proficiency_bonus,
        ),
        Rule(
            priority=250,
            source="Base combat",
            function=update_base_combat,
        ),
        Rule(
            priority=DERIVED,
            source="Saving throws",
            function=update_saving_throws,
        ),
        Rule(
            priority=DERIVED,
            source="Skills",
            function=update_skills,
        ),
        Rule(
            priority=DERIVED,
            source="HP and Hit Dice",
            function=update_hp_and_hit_dice,
        ),
        Rule(
            priority=DERIVED,
            source="Spell Slots and Resources",
            function=update_spell_slots_and_resources,
        ),
        Rule(
            priority=DERIVED,
            source="Conditions and Effects",
            function=update_conditions_and_effects,
        ),
    ]


def collect_updates(character: SavedCharacter) -> list[Rule]:
    updates = []

    updates.extend(standard_updates(character))
    updates.extend(character.active_sources())

    updates.sort(key=lambda update: update.priority)

    return updates


def get_active_sources(character: SavedCharacter) -> list[Any]:
    return character.active_sources()


def calculate(character: SavedCharacter) -> EffectiveCharacter:
    effective = create_effective_character(character)

    for update in collect_updates(character):
        update.function(character, effective)

    return effective
