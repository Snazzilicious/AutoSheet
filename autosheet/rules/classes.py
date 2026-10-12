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

        if die_key in effective.hit_dice:
            existing = effective.hit_dice[die_key]
            existing.max_uses += self.level
            if remaining >= 0:
                existing.remaining_uses = remaining
            else:
                existing.remaining_uses = existing.max_uses
        else:
            effective.hit_dice[die_key] = HitDie(die, self.level, remaining_uses=remaining)


class Warlock(CharacterClass):
    name = "Warlock"


CLASSES = {"Warlock": Warlock}
