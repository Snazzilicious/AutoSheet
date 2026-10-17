from autosheet.core import Rule, SavedCharacter, EffectiveCharacter, Feature as CoreFeature, FINAL, DERIVED


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
        desc = self.__doc__.strip() if self.__doc__ else ""
        effective.features[self.name] = CoreFeature(name=self.name, description=desc)


class AgonizingBlast(Feature):
    name = "Agonizing Blast"

class RepellingBlast(Feature):
    name = "Repelling Blast"

class EldritchMind(Feature):
    name = "Eldritch Mind"

class DevilsSight(Feature):
    name = "Devil's Sight"

class LessonsOfTheFirstOnes(Feature):
    def __init__(self, feat_name: str):
        self.name = f"Lessons of the First Ones: {feat_name}"
        super().__init__()
    

class Resistance(Feature):
    def __init__(self, damage_type: str):
        self.name = f"Resistance: {damage_type}"
        super().__init__()

class Darkvision(Feature):
    def __init__(self, range: int):
        self.name = f"Darkvision: {range} ft"
        super().__init__()

class PietyScore(Feature):
    def __init__(self, diety: str, value: int):
        self.name = f"Piety Score ({diety}): {value}"
        super().__init__()


class FeatNotAFeat(Feature):
    name = "Feat that is not a Feat"
    priority = DERIVED
    
    def add_to_character(self, saved: SavedCharacter, effective: EffectiveCharacter) -> None:
        super().add_to_character(saved, effective)
        effective.saving_throws["constitution"] += 2
        effective.saving_throws["dexterity"] += 1

"""TODO
Shadow Coil
Grave Murmurs
Moderately armored
Radiant Soul
Boon of Judgement
"""

FEATURES = {
    "agonizing_blast": AgonizingBlast,
    "repelling_blast": RepellingBlast,
    "eldritch_mind": EldritchMind,
    "devils_sight": DevilsSight,
}
