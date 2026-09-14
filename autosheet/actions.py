from autosheet.core import SavedCharacter
from autosheet.calculation import calculate


def equip_item(character: SavedCharacter, item_id: str) -> None:
    """
    Equip an item from inventory.
    """
    if item_id in character.inventory and item_id not in character.equipment:
        character.equipment.append(item_id)


def unequip_item(character: SavedCharacter, item_id: str) -> None:
    """
    Unequip an item.
    """
    if item_id in character.equipment:
        character.equipment.remove(item_id)


def cast_spell(character: SavedCharacter, spell_level: int) -> bool:
    """
    Cast a spell of given level, consuming a spell slot.
    """
    slots = character.state.setdefault("spell_slots", {})
    slot_key = str(spell_level)
    if slots.get(slot_key, 0) > 0:
        slots[slot_key] -= 1
        return True
    return False


def short_rest(character: SavedCharacter) -> None:
    """
    Perform a short rest.
    """
    pass


def long_rest(character: SavedCharacter) -> None:
    """
    Perform a long rest, restoring HP to max, resetting spell slots, and clearing conditions.
    """
    effective = calculate(character)
    max_hp = effective.combat.get("hit_point_max", 0)
    character.state.setdefault("hp", {})["current"] = max_hp
    character.state["hp"]["temporary"] = 0

    max_slots = effective.combat.get("spell_slots_max", {})
    character.state["spell_slots"] = dict(max_slots)

    character.state["conditions"] = []
    character.state["concentration"] = None
