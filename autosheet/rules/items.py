from autosheet.core import Update, CalculationContext, BASE, DERIVED


class AmuletOfHealth:
    """
    Amulet of Health: Your Constitution score is 19 while wearing the amulet.
    """

    def get_updates(self) -> list[Update]:
        return [
            Update(
                priority=BASE,
                source="Amulet of Health",
                function=self.update_constitution,
            )
        ]

    @staticmethod
    def update_constitution(ctx: CalculationContext) -> None:
        ctx.effective.abilities.constitution = max(
            ctx.effective.abilities.constitution,
            19,
        )


class ScaleMail:
    """
    Scale Mail: Medium armor, AC 14 + Dex modifier (max +2).
    """

    def get_updates(self) -> list[Update]:
        return [
            Update(
                priority=DERIVED,
                source="Scale Mail",
                function=self.update_ac,
            )
        ]

    @staticmethod
    def update_ac(ctx: CalculationContext) -> None:
        dex_mod = ctx.effective.abilities.dexterity_modifier
        armor_ac = 14 + min(dex_mod, 2)
        current_ac = ctx.effective.combat.get("ac", 10 + dex_mod)
        ctx.effective.combat["ac"] = max(current_ac, armor_ac)


class Shield:
    """
    Shield: +2 AC.
    """

    def get_updates(self) -> list[Update]:
        return [
            Update(
                priority=DERIVED + 10,
                source="Shield",
                function=self.update_shield,
            )
        ]

    @staticmethod
    def update_shield(ctx: CalculationContext) -> None:
        ctx.effective.combat["ac"] = ctx.effective.combat.get("ac", 10) + 2


ITEMS = {
    "amulet_of_health": AmuletOfHealth,
    "scale_mail": ScaleMail,
    "shield": Shield,
}
