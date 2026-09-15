from autosheet.core import Update, FINAL


def _feature_rule(source: str, feature_id: str):
    class Rule:
        def get_updates(self) -> list[Update]:
            return [
                Update(
                    priority=FINAL,
                    source=source,
                    function=lambda ctx: ctx.effective.features.add(feature_id),
                )
            ]
    return Rule


FEATURES = {
    "agonizing_blast": _feature_rule("Agonizing Blast", "agonizing_blast"),
    "repelling_blast": _feature_rule("Repelling Blast", "repelling_blast"),
    "eldritch_mind": _feature_rule("Eldritch Mind", "eldritch_mind"),
    "devils_sight": _feature_rule("Devil's Sight", "devils_sight"),
}

