from typing import Any
from autosheet.core import (
    SavedCharacter,
    EffectiveCharacter,
    Abilities,
    CalculationContext,
    Rule,
    MODIFIERS,
    DERIVED,
)

ABILITIES_LIST = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]


def create_effective_character(character: SavedCharacter) -> EffectiveCharacter:
    """
    Create initial effective character from persistent character data.
    """
    abilities = Abilities(
        **{name: character.abilities.get(name, 0) for name in ABILITIES_LIST}
    )
    return EffectiveCharacter(abilities=abilities)


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
    for name in ABILITIES_LIST:
        setattr(ab, f"{name}_modifier", ability_modifier(getattr(ab, name)))


def update_proficiency_bonus(saved: SavedCharacter, effective: EffectiveCharacter) -> None:
    """
    Calculate proficiency bonus based on total character level.
    """
    total_level = sum(c.get("level", 0) for c in saved.classes)
    pb = (total_level - 1) // 4 + 2 if total_level > 0 else 2
    effective.combat["proficiency_bonus"] = pb


def update_base_combat(saved: SavedCharacter, effective: EffectiveCharacter) -> None:
    """
    Calculate base unarmored AC and initiative.
    """
    dex_mod = effective.abilities.dexterity_modifier
    effective.combat["ac"] = 10 + dex_mod
    effective.combat["initiative"] = dex_mod


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
    ab = effective.abilities
    pb = effective.combat.get("proficiency_bonus", 2)
    prof_saves = set(saved.proficiencies.get("saving_throws", []))

    effective.combat["saving_throws"] = {
        name: getattr(ab, f"{name}_modifier") + (pb if name in prof_saves else 0)
        for name in ABILITIES_LIST
    }


def update_skills(saved: SavedCharacter, effective: EffectiveCharacter) -> None:
    """
    Calculate skill bonuses.
    """
    ab = effective.abilities
    pb = effective.combat.get("proficiency_bonus", 2)
    skills_data = saved.proficiencies.get("skills", {})
    prof_skills = set(skills_data.get("proficient", []))
    exp_skills = set(skills_data.get("expertise", []))

    skill_bonuses = {}
    for skill, ability_name in SKILL_ABILITIES.items():
        mod = getattr(ab, f"{ability_name}_modifier", 0)
        mult = 2 if skill in exp_skills else (1 if skill in prof_skills else 0)
        skill_bonuses[skill] = mod + (mult * pb)

    effective.combat["skill_bonuses"] = skill_bonuses


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
    con_mod = effective.abilities.constitution_modifier
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

    effective.combat["hit_point_max"] = total_hp
    effective.combat["hit_dice"] = hit_dice


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

    effective.combat["spell_slots_max"] = spell_slots_max
    effective.combat["resources_max"] = {}


def update_conditions_and_effects(saved: SavedCharacter, effective: EffectiveCharacter) -> None:
    """
    Process active conditions and temporary effects from saved character state.
    """
    state = saved.state
    conditions = state.get("conditions", [])
    active_effects = state.get("active_effects", [])

    effective.combat["conditions"] = list(conditions)
    effective.combat["active_effects"] = list(active_effects)


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

    for source in character.active_sources():
        updates.extend(source.get_updates())

    updates.sort(key=lambda update: update.priority)

    return updates


def calculate(character: SavedCharacter) -> EffectiveCharacter:
    effective = create_effective_character(character)

    for update in collect_updates(character):
        update.function(character,effective)

    return effective


