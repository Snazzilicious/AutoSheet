from autosheet.core import Rule, SavedCharacter, EffectiveCharacter, FINAL


class Feature(Rule):
    """
    An entry in EffectiveCharacter's feature list
    Has a short name for display
    Provides a description of the feature
    """
    priority = FINAL

    def __init__(self):
        super().__init__(priority=self.priority, source=self.name, function=self.add_to_character)
    
    def add_to_character(self, saved: SavedCharacter, effective: EffectiveCharacter) -> None:
        effective.features.add(self.name)


class AgonizingBlast(Feature):
    name = "Agonizing Blast"

class RepellingBlast(Feature):
    name = "Repelling Blast"

class EldritchMind(Feature):
    name = "Eldritch Mind"

class DevilsSight(Feature):
    name = "Devil's Sight"


FEATURES = {
    "agonizing_blast": AgonizingBlast,
    "repelling_blast": RepellingBlast,
    "eldritch_mind": EldritchMind,
    "devils_sight": DevilsSight,
}
