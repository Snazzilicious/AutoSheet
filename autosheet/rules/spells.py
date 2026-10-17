from autosheet.core import Rule, SavedCharacter, EffectiveCharacter, Spell as CoreSpell, BASE


class Spell(Rule, CoreSpell):
    """
    An entry in the EffectiveCharacter's readied spell list
    Has a short name for display
    Provides a description of the spell
    Includes 'cost'
    """
    priority = BASE

    level: int = 1
    school: str = ""
    cost: str = "1 Action"
    range: str = "60 ft"
    duration: str = "Instantaneous"
    concentration: bool = False
    atk_bonus: int | None = None
    save: str | None = None
    dmg_die: str | None = None
    dmg_mod: int = 0
    dmg_type: str | None = None

    def __init__(self):
        CoreSpell.__init__(
            self,
            name=self.name,
            level=self.level,
            school=self.school,
            cost=self.cost,
            range=self.range,
            duration=self.duration,
            concentration=self.concentration,
            atk_bonus=self.atk_bonus,
            save=self.save,
            dmg_die=self.dmg_die,
            dmg_mod=self.dmg_mod,
            dmg_type=self.dmg_type,
        )
        Rule.__init__(self, priority=self.priority, source=self.name, function=self.apply_effect)

    def apply_effect(self, saved: SavedCharacter, effective: EffectiveCharacter) -> None:
        effective.spells[self.name] = self

    def ready(self):
        pass

    def unready(self):
        pass


class Hex(Spell):
    name = "Hex"
    priority = BASE
    level = 1
    school = "Enchantment"
    cost = "1 Bonus Action"
    range = "90 ft"
    duration = "1 hour"
    concentration = True
    dmg_die = "1d6"
    dmg_type = "necrotic"


class Bless(Spell):
    name = "Bless"
    priority = BASE
    level = 1
    school = "Enchantment"
    cost = "1 Action"
    range = "30 ft"
    duration = "1 minute"
    concentration = True


class CureWounds(Spell):
    name = "Cure Wounds"
    priority = BASE
    level = 1
    school = "Evocation"
    cost = "1 Action"
    range = "Touch"
    duration = "Instantaneous"
    dmg_die = "1d8"
    dmg_type = "healing"


SPELLS = {
    "hex": Hex,
    "bless": Bless,
    "cure_wounds": CureWounds,
}


from typing import Any

SPECIES: dict[str, Any] = {}
