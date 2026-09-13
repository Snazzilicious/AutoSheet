from pathlib import Path
from character import (
    load_character,
    SavedCharacter,
    create_effective_character,
    EffectiveCharacter,
    Update,
    CalculationContext,
    BASE,
    MODIFIERS,
    DERIVED,
    FINAL,
    ITEMS,
    AmuletOfHealth,
    get_active_sources,
    collect_updates,
    calculate,
)


def test_load_northstar():
    yaml_path = Path(__file__).parent / "Northstar.yaml"
    character = load_character(yaml_path)

    assert isinstance(character, SavedCharacter)
    assert character.name == "Northstar"
    assert character.classes[0]["name"] == "Warlock"
    assert character.classes[0]["level"] == 6
    assert character.abilities["constitution"] == 16
    assert character.inventory["amulet_of_health"] == 1
    assert character.state["hp"]["current"] == 37


def test_spells_specification():
    yaml_path = Path(__file__).parent / "Northstar.yaml"
    character = load_character(yaml_path)

    assert "learned" in character.spells
    assert "readied" in character.spells
    assert "hex" in character.spells["learned"]
    assert "bless" in character.spells["learned"]
    assert "cure_wounds" in character.spells["learned"]
    assert "hex" in character.spells["readied"]
    assert "bless" in character.spells["readied"]
    assert "cure_wounds" not in character.spells["readied"]


def test_create_effective_character():
    yaml_path = Path(__file__).parent / "Northstar.yaml"
    character = load_character(yaml_path)
    effective = create_effective_character(character)

    assert isinstance(effective, EffectiveCharacter)
    assert effective.abilities.constitution == 16
    assert effective.abilities.dexterity == 17
    assert effective.abilities.strength == 8


def test_update_and_priorities():
    assert BASE == 100
    assert MODIFIERS == 200
    assert DERIVED == 300
    assert FINAL == 400

    yaml_path = Path(__file__).parent / "Northstar.yaml"
    character = load_character(yaml_path)
    effective = create_effective_character(character)

    ctx = CalculationContext(saved=character, effective=effective)
    
    def dummy_func(context: CalculationContext):
        context.effective.abilities.constitution = 19

    update = Update(priority=BASE, source="Test Source", function=dummy_func)
    assert update.priority == BASE
    assert update.source == "Test Source"
    
    update.function(ctx)
    assert ctx.effective.abilities.constitution == 19


def test_rule_registries_and_amulet():
    assert "amulet_of_health" in ITEMS
    item_class = ITEMS["amulet_of_health"]
    amulet = item_class()
    assert isinstance(amulet, AmuletOfHealth)

    updates = amulet.get_updates()
    assert len(updates) == 1
    assert updates[0].priority == BASE
    assert updates[0].source == "Amulet of Health"


def test_active_sources():
    yaml_path = Path(__file__).parent / "Northstar.yaml"
    character = load_character(yaml_path)
    sources = get_active_sources(character)
    
    assert len(sources) == 3


def test_collect_updates_and_calculate():
    yaml_path = Path(__file__).parent / "Northstar.yaml"
    character = load_character(yaml_path)

    updates = collect_updates(character)
    # Should have Amulet of Health (BASE=100), Ability modifiers (MODIFIERS=200),
    # Proficiency bonus (MODIFIERS=200), Base combat (250), Saving throws (DERIVED=300),
    # Skills (DERIVED=300), Scale Mail (DERIVED=300), Shield (DERIVED=310)
    assert len(updates) == 8
    assert updates[0].priority == BASE

    effective = calculate(character)
    # Constitution should be 19 due to Amulet of Health, modifier +4
    assert effective.abilities.constitution == 19
    assert effective.abilities.constitution_modifier == +4
    # Dexterity should remain 17 (base), modifier +3
    assert effective.abilities.dexterity == 17
    assert effective.abilities.dexterity_modifier == +3


def test_combat_statistics():
    yaml_path = Path(__file__).parent / "Northstar.yaml"
    character = load_character(yaml_path)
    effective = calculate(character)

    assert effective.combat.get("proficiency_bonus") == 3
    assert effective.combat.get("initiative") == 3
    assert effective.combat.get("ac") == 18


def test_saving_throws_and_skills():
    yaml_path = Path(__file__).parent / "Northstar.yaml"
    character = load_character(yaml_path)
    effective = calculate(character)

    saves = effective.combat.get("saving_throws", {})
    assert saves.get("wisdom") == 5     # +2 mod + 3 pb
    assert saves.get("charisma") == 7   # +4 mod + 3 pb
    assert saves.get("strength") == -1  # -1 mod

    skills = effective.combat.get("skill_bonuses", {})
    assert skills.get("religion") == 4  # Intelligence +1 + 3 pb
    assert skills.get("insight") == 5   # Wisdom +2 + 3 pb
    assert skills.get("acrobatics") == 3 # Dexterity +3 (not proficient)
