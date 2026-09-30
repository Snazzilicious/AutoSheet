from autosheet.core import Rule, SavedCharacter, EffectiveCharacter, BASE, DERIVED


class Item(Rule):
    """
    An entry in the EffectiveCharacter's inventory list
    Has a short name for display
    Provides a description of the item
    May grant a Feature and/or Action
    """
    name = "Item"
    priority = BASE

    def __init__(self, equipped: bool = False):
        self.equipped = equipped
        super().__init__(priority=self.priority, source=self.name, function=self.apply_effect_if_equipped)

    def apply_effect_if_equipped(self, saved: SavedCharacter, effective: EffectiveCharacter) -> None:
        if self.equipped:
            self.apply_effect(saved, effective)

    def apply_effect(self, saved: SavedCharacter, effective: EffectiveCharacter) -> None:
        pass

    def equip(self):
        self.equipped = True

    def unequip(self):
        self.equipped = False


class AmuletOfHealth(Item):
    """
    Amulet of Health: Your Constitution score is 19 while wearing the amulet.
    """
    name = "Amulet of Health"
    priority = BASE

    def apply_effect(self, saved: SavedCharacter, effective: EffectiveCharacter) -> None:
        effective.abilities.constitution = max(19, effective.abilities.constitution)


class ScaleMail(Item):
    """
    Scale Mail: Medium armor, AC 14 + Dex modifier (max +2).
    """
    name = "Scale Mail"
    priority = DERIVED

    def apply_effect(self, saved: SavedCharacter, effective: EffectiveCharacter) -> None:
        dex_mod = effective.ability_modifiers.dexterity
        armor_ac = 14 + min(dex_mod, 2)
        effective.armor_class = max(effective.armor_class, armor_ac)


class Shield(Item):
    """
    Shield: +2 AC.
    """
    name = "Shield"
    priority = DERIVED + 10

    def apply_effect(self, saved: SavedCharacter, effective: EffectiveCharacter) -> None:
        effective.armor_class += 2


ITEMS = {
    "amulet_of_health": AmuletOfHealth,
    "scale_mail": ScaleMail,
    "shield": Shield,
}
