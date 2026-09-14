from typing import Any
from autosheet.core import Update


class WarlockClass:
    def __init__(self, data: dict[str, Any]):
        self.data = data

    def get_updates(self) -> list[Update]:
        return []


class CelestialSubclass:
    def __init__(self, data: dict[str, Any]):
        self.data = data

    def get_updates(self) -> list[Update]:
        return []


CLASSES = {
    "Warlock": WarlockClass,
}

SUBCLASSES = {
    "Celestial": CelestialSubclass,
}
