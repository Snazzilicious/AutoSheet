from character import load_character, create_effective_character


character = load_character("northstar.md")

print(character.name)
print(character.classes)
print(character.abilities)


effective = create_effective_character(character)

print(effective.abilities)


from character import calculate, load_character


def display_character(character):
    effective = calculate(character)

    abilities = effective.abilities

    print(f"Name: {character.name}")
    print()

    print("Abilities")
    print(f"  STR: {abilities.strength:2} ({abilities.strength_modifier:+d})")
    print(f"  DEX: {abilities.dexterity:2} ({abilities.dexterity_modifier:+d})")
    print(f"  CON: {abilities.constitution:2} ({abilities.constitution_modifier:+d})")
    print(f"  INT: {abilities.intelligence:2} ({abilities.intelligence_modifier:+d})")
    print(f"  WIS: {abilities.wisdom:2} ({abilities.wisdom_modifier:+d})")
    print(f"  CHA: {abilities.charisma:2} ({abilities.charisma_modifier:+d})")


character = load_character("northstar.yaml")

display_character(character)


def print_updates(character: SavedCharacter) -> None:
    print("Updates:")

    for update in collect_updates(character):
        print(
            f"  [{update.priority}] {update.source}"
        )

character = load_character("northstar.yaml")

print_updates(character)

effective = calculate(character)