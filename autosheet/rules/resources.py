
from autosheet.core import Resource as CoreResource


class Resource(CoreResource):
    """
    Rechargable consumable required to use abilities.
    """
    recharge_event = None

    def __init__(self, max_uses: int, remaining_uses: int = -1):
        super().__init__(name="", max_uses=max_uses, remaining_uses=remaining_uses, recharge_event=self.recharge_event)

    def recharge(self, recharge_event=None):
        if recharge_event is None or recharge_event == self.recharge_event:
            self.remaining_uses = self.max_uses
    
    def use(self, n_uses=1):
        super().use(n_uses)
    
    def __str__(self):
        return f"{self.name:<20s}{self.remaining_uses:<2d} / {self.max_uses:<2d}"


class SpellSlot(Resource):
    recharge_event = "Long Rest"

    def __init__(self, level: int, max_uses: int, remaining_uses: int = -1):
        self.name = f"Spell slot lvl {level:1d}"
        super().__init__(max_uses, remaining_uses)

class WarlockSpellSlot(SpellSlot):
    recharge_event = "Short Rest"

class HitDie(Resource):
    recharge_event = "Long Rest"

    def __init__(self, d: int, max_uses: int, remaining_uses: int = -1):
        self.name = f"Hit Die d{d:1d}"
        super().__init__(max_uses, remaining_uses)
