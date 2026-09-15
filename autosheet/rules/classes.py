from typing import Any
from autosheet.core import Update


class BaseRule:
    def __init__(self, data: dict[str, Any]):
        self.data = data

    def get_updates(self) -> list[Update]:
        return []


CLASSES = {"Warlock": BaseRule}
SUBCLASSES = {"Celestial": BaseRule}

