from autosheet.core import Update, FINAL


class AgonizingBlast:
    def get_updates(self) -> list[Update]:
        return [
            Update(
                priority=FINAL,
                source="Agonizing Blast",
                function=lambda ctx: ctx.effective.features.add("agonizing_blast"),
            )
        ]


class RepellingBlast:
    def get_updates(self) -> list[Update]:
        return [
            Update(
                priority=FINAL,
                source="Repelling Blast",
                function=lambda ctx: ctx.effective.features.add("repelling_blast"),
            )
        ]


class EldritchMind:
    def get_updates(self) -> list[Update]:
        return [
            Update(
                priority=FINAL,
                source="Eldritch Mind",
                function=lambda ctx: ctx.effective.features.add("eldritch_mind"),
            )
        ]


class DevilsSight:
    def get_updates(self) -> list[Update]:
        return [
            Update(
                priority=FINAL,
                source="Devil's Sight",
                function=lambda ctx: ctx.effective.features.add("devils_sight"),
            )
        ]


FEATURES = {
    "agonizing_blast": AgonizingBlast,
    "repelling_blast": RepellingBlast,
    "eldritch_mind": EldritchMind,
    "devils_sight": DevilsSight,
}
