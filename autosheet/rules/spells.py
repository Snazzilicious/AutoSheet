

class Spell(Rule):
    """
    An entry in the EffectiveCharacter's readied spell list
    Has a short name for display
    Provides a description of the spell
    Includes 'cost'
    """
    def __init__( self, readied: bool = False ):
        self.readied = readied
        super()__init__( priority=self.priority, source=self.name, function=self.apply_effect_if_readied )
    
    def apply_effect_if_readied( self, saved: SavedCharacter, effective: EffectiveCharacter ) -> None :
        if self.readied:
            self.apply_effect( saved, effective )
    
    def apply_effect( self, saved: SavedCharacter, effective: EffectiveCharacter ) -> None :
        pass
    
    def ready(self):
        self.readied = True
    
    def unready(self):
        self.readied = False


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
