from autosheet.core import Rule


class BaseRule:
    def __init__(self, data: dict[str, Any]):
        self.data = data

    def get_updates(self) -> list[Update]:
        return []

class CharacterClass(Rule):
    """
    Primary source of a character's features.
    """
    def __init__( self, level: int = 1 ):
        self.level = level
        super()__init__( priority=self.priority, source=self.name, function=self.apply_features )
    
    def apply_features( self, saved: SavedCharacter, effective: EffectiveCharacter ):
        pass
    


CLASSES = {"Warlock": BaseRule}
SUBCLASSES = {"Celestial": BaseRule}

