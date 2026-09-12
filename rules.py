

BASE = 100 # Modify raw character properties
MODIFIERS = 200 # Calculate modifiers/proficiencies
DERIVED = 300 # Calculate derived statistics
FINAL = 400 # Final adjustments

FEATURES = {
    "agonizing_blast": AgonizingBlast,
    "repelling_blast": RepellingBlast,
    "eldritch_mind": EldritchMind,
    "devils_sight": DevilsSight,
}

ITEMS = {
    "amulet_of_health": AmuletOfHealth,
    "scale_mail": ScaleMail,
    "shield": Shield,
}

"""
SPELLS = {...}
CLASSES = {...}
SUBCLASSES = {...}
SPECIES = {...}
"""