from autosheet.core import SavedCharacter, EffectiveCharacter
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


def sync_resources_to_state(character: SavedCharacter, effective: EffectiveCharacter) -> None:
    spell_slots = character.state.setdefault("spell_slots", {})
    hit_dice = character.state.setdefault("hit_dice", {})
    from autosheet.rules.resources import SpellSlot, HitDie
    for v in effective.resources.values():
        if isinstance(v, SpellSlot):
            spell_slots[str(v.level)] = v.remaining_uses
        elif isinstance(v, HitDie):
            hit_dice[f"d{v.d}"] = v.remaining_uses


def short_rest(character: SavedCharacter) -> None:
    """
    Perform a short rest.
    """
    effective = calculate(character)
    for v in effective.resources.values():
        v.recharge("Short Rest")
    sync_resources_to_state(character, effective)


def long_rest(character: SavedCharacter) -> None:
    """
    Perform a long rest, restoring HP to max, resetting resources, and clearing conditions.
    """
    effective = calculate(character)
    max_hp = effective.hit_points.max
    character.state.setdefault("hp", {})["current"] = max_hp
    character.state["hp"]["temporary"] = 0

    for v in effective.resources.values():
        v.recharge("Long Rest")
    sync_resources_to_state(character, effective)

    character.state["conditions"] = []
    character.state["concentration"] = None
