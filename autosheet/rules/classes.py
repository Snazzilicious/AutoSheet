from autosheet.core import Rule, SavedCharacter, EffectiveCharacter, BASE


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


class CharacterClass(Rule):
    """
    Primary source of a character's features.
    """
    priority = BASE

    def __init__(self, level: int = 1, subclass: str | None = None):
        self.level = level
        self.subclass = subclass
        super().__init__(priority=self.priority, source=self.name, function=self.apply_features)

    @property
    def hit_die(self) -> int:
        return CLASS_HIT_DIE.get(self.name.lower(), 8)

    def apply_features(self, saved: SavedCharacter, effective: EffectiveCharacter):
        from autosheet.rules.resources import HitDie
        die = self.hit_die
        die_key = f"d{die}"
        state_hit_dice = saved.state.get("hit_dice", {})
        remaining = state_hit_dice.get(die_key, -1)

        if die_key in effective.resources:
            existing = effective.resources[die_key]
            existing.max_uses += self.level
            if remaining >= 0:
                existing.remaining_uses = remaining
            else:
                existing.remaining_uses = existing.max_uses
        else:
            effective.resources[die_key] = HitDie(die, self.level, remaining_uses=remaining)


class Warlock(CharacterClass):
    name = "Warlock"

    def apply_features(self, saved: SavedCharacter, effective: EffectiveCharacter):
        super().apply_features(saved, effective)
        slot_level = min(5, (self.level + 1) // 2)
        slot_count = 3 if self.level >= 11 else (4 if self.level >= 17 else 2)
        slot_key = str(slot_level)
        state_slots = saved.state.get("spell_slots", {})
        remaining = state_slots.get(slot_key, -1)

        from autosheet.rules.resources import WarlockSpellSlot
        if slot_key in effective.resources:
            existing = effective.resources[slot_key]
            existing.max_uses += slot_count
            if remaining >= 0:
                existing.remaining_uses = remaining
            else:
                existing.remaining_uses = existing.max_uses
        else:
            effective.resources[slot_key] = WarlockSpellSlot(slot_level, slot_count, remaining_uses=remaining)


CLASSES = {"Warlock": Warlock}
