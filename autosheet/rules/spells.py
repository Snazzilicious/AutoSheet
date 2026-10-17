from autosheet.core import Rule, SavedCharacter, EffectiveCharacter, Spell as CoreSpell, BASE


class Spell(Rule, CoreSpell):
    """
    An entry in the EffectiveCharacter's readied spell list
    Has a short name for display
    Provides a description of the spell
    Includes 'cost'
    """
    priority = BASE

    def __init__(self):
        CoreSpell.__init__(self, name=self.name, range="60 ft", level=1)
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


class Bless(Spell):
    name = "Bless"
    priority = BASE


class CureWounds(Spell):
    name = "Cure Wounds"
    priority = BASE


SPELLS = {
    "hex": Hex,
    "bless": Bless,
    "cure_wounds": CureWounds,
}


from typing import Any

SPECIES: dict[str, Any] = {}
