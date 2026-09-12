"""
CharacterDefinition:
    "I own an Amulet of Health."

CharacterState:
    "I currently have 23 HP."

EffectiveCharacter:
    = "What does this character effectively have?"
    "My Constitution is 19."

DerivedStats:
    = "What numbers result from that?"
    "My Constitution modifier is +4."
"""


"""TODO
Add "actions"
    cost
    description
    state_update
Distinction between saved state and state created at startup
Class, Proficiencies, Equipment can add features
    features add actions, bonuses, conditions, etc
    spells add actions
Decide everything adds a feature? vs additional update_derived loops and feature is the final catch-all?
for each feature (and spell) in sorted_features:
    feature.update_derived( derived )
self.priority = standard_priorities["AttackBonus"]
can add checks for before and after other stages to prevent circular dependencies
Phase 1 UI can just be a text file that gets updated
actions change CharacterState
combine EffectiveCharacter and DerivedStats into 1?
also combine CharacterDefinition and CharacterState into 1?
    both are technically mutable
clarify mutable character state vs derived quantities
save is broken right now b/c of multiple definitions of fields
    only base values should be saved
    persistent vs volatile?
Define UI
    i.e. categories
"""



@dataclass
class CharacterDefinition:
    """This is the canonical representation of the Markdown/YAML file of player-owned information
    """
    name: str
    background: str
    species: str
    alignment: str

    classes: list[ClassDefinition]

    abilities: AbilityScores

    proficiencies: Proficiencies

    inventory: dict[str, int]
    equipment: Equipment

    features: list[FeatureReference]
    spells: SpellSelection

@dataclass
class EffectiveCharacter:
    """Character after various rules have been applied
    """
    abilities: AbilityScores
    proficiencies: Proficiencies

    speed: int

    senses: Senses
    resistances: set[str]

    # Other effects can add fields as needed.

@dataclass
class DerivedStats:
    """Quantities affecting play, derived from EffectiveCharacter
    """
    # Ability modifiers
    ability_modifiers: AbilityScores

    # Core combat
    proficiency_bonus: int
    armor_class: int
    initiative: int
    hit_point_max: int
    hit_dice: dict[str, int]

    # Saves
    saving_throw_bonuses: dict[str, int]

    # Skills
    skill_bonuses: dict[str, int]

    # Spellcasting
    spell_attack_bonus: int | None
    spell_save_dc: int | None

    # Attacks
    attacks: list[Attack]

    # Potentially later:
    # passive_perception
    # passive_investigation
    # etc.

@dataclass
class CharacterState:
    """Session-mutable Character values; what is happening to the character right now?
    """
    hp_current: int
    hp_temporary: int

    death_save_successes: int
    death_save_failures: int

    conditions: list[str]

    concentration: str | None

    inspiration: bool

    resources: dict[str, int]
    spell_slots: dict[int, int]
    hit_dice: dict[str, int]


standard_priorities = {
    "EffectiveAbilityScores" : 10.0,
    "Proficiencies" : 20.0,
    "AbilityModifiers" : 30.0,
    "CombatStatistics" : 40.0,
    "SkillBonuses" : 50.0,
    "Attacks" : 60.0,
    "Spellcasting" : 70.0
}

saved_state = load_character("northstar.md")
current_state = EffectiveCharacter( saved_state )

update_queue = standard_feature_list() # e.g. sets modifier based on ability scores
for c in saved_state.classes:
    for f in c.feature_list():
        update_queue.append( f.get_update() )
for p in saved_state.proficiencies:
    update_queue.append( p.get_update() )
for e in saved_state.equipment:
    for f in e.feature_list():
    update_queue.append( f.get_update() )
for s in saved_state.spells:
    update_queue.append( s.get_update() )

update_queue.sort( key = lambda x : x.priority )

for u in update_queue:
    u( current_state )

ui.display( current_state )


def perform_action( action, current_state ):
    action( current_state ) # should print something
    save( current_state )
    ui.display( current_state )

def cast_spell( level, current_state ):
    perform_action( SpellCast(level), current_state )

def short_rest( current_state ):
    for r in current_state.resources:
        if "short_rest" in r.recharge:
            r.reset()

