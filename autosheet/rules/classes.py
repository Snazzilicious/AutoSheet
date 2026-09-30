from autosheet.core import Rule, SavedCharacter, EffectiveCharacter, BASE


class CharacterClass(Rule):
    """
    Primary source of a character's features.
    """
    priority = BASE

    def __init__(self, level: int = 1, subclass: str | None = None):
        self.level = level
        self.subclass = subclass
        super().__init__(priority=self.priority, source=self.name, function=self.apply_features)

    def apply_features(self, saved: SavedCharacter, effective: EffectiveCharacter):
        pass


class Warlock(CharacterClass):
    self.name = "Warlock"


CLASSES = {"Warlock": Warlock}
