# D&D Character Sheet Application — Design Document

## 1. Purpose

Build a lightweight, automated D&D character sheet application for personal/fun use.

Goals:
- Store characters in simple YAML files.
- Calculate derived statistics automatically.
- Implement D&D rules directly in Python, not a custom rules DSL.
- Track mutable game state such as HP, spell slots, conditions, and resources.
- Eventually automate actions, spells, items, and rests.
- Keep the code small, transparent, and easy to modify with a coding agent.

This is not intended to be a full commercial virtual tabletop.

## 2. Core Architecture

The key distinction is:

> **What the player says is true about the character** vs. **what the game engine is currently tracking.**

A second distinction is:

> **Persistent values** vs. **calculated values.**

Rule:

> If the application can reproduce a value from the saved character plus rules, do not save it. If it cannot be reproduced and must survive closing the application, save it.

Persistent examples:
- Name
- Classes/subclasses/levels
- Base ability scores
- Proficiencies
- Inventory and quantities
- Equipment
- Features
- Learned/prepared spells
- Current HP and temporary HP
- Remaining resources and spell slots
- Hit dice
- Conditions
- Death saves
- Concentration/active effects

Calculated examples:
- Effective ability scores
- Ability modifiers
- Saving throw bonuses
- Skill bonuses
- Proficiency bonus
- Maximum HP
- AC
- Initiative
- Attack bonuses
- Spell save DC
- Resistances
- Darkvision

Do not persist duplicate derived values.

## 3. Data Flow

```text
YAML character file
        |
        v
 SavedCharacter
        |
        | rules registry
        v
 collect updates
        |
        v
 sort by priority
        |
        v
 apply Python updates
        |
        v
EffectiveCharacter
        |
   +----+----+
   |    |    |
   v    v    v
  UI Actions Validation
```

`SavedCharacter` is persistent.

`EffectiveCharacter` is temporary and rebuilt whenever calculation occurs.

Rules are Python implementations associated with stable IDs through registries.

## 4. YAML Format

Pure YAML is the initial format.

Example:

```yaml
name: Northstar

classes:
  - name: Warlock
    level: 6
    subclass: Celestial

abilities:
  base:
    strength: 8
    dexterity: 17
    constitution: 16
    intelligence: 12
    wisdom: 14
    charisma: 18

proficiencies:
  saving_throws:
    - wisdom
    - charisma
  skills:
    proficient:
      - religion
      - insight
    expertise: []

inventory:
  dagger: 2
  amulet_of_health: 1
  scale_mail: 1
  shield: 1

equipment:
  armor: scale_mail
  shield: shield
  worn:
    - amulet_of_health

features:
  - agonizing_blast
  - repelling_blast
  - eldritch_mind
  - devils_sight

spells:
  learned:
    - hex
    - bless
    - cure_wounds

state:
  hp:
    current: 37
    temporary: 0
  death_saves:
    successes: 0
    failures: 0
  conditions: []
  concentration: null
  inspiration: false
```

Rules-bearing entities use stable IDs.

## 5. Persistent Model

Initial model:

```python
@dataclass
class SavedCharacter:
    name: str
    classes: list[dict]
    abilities: dict
    proficiencies: dict
    inventory: dict
    equipment: dict
    features: list[str]
    spells: dict
    state: dict
```

This is a representation of saved data, not a rules engine.

## 6. Effective Model

Initial model:

```python
@dataclass
class Abilities:
    strength: int = 0
    dexterity: int = 0
    constitution: int = 0
    intelligence: int = 0
    wisdom: int = 0
    charisma: int = 0

    strength_modifier: int = 0
    dexterity_modifier: int = 0
    constitution_modifier: int = 0
    intelligence_modifier: int = 0
    wisdom_modifier: int = 0
    charisma_modifier: int = 0


@dataclass
class EffectiveCharacter:
    abilities: Abilities
    proficiencies: dict = field(default_factory=dict)
    combat: dict = field(default_factory=dict)
    spells: dict = field(default_factory=dict)
    features: set[str] = field(default_factory=set)
```

Do not model every D&D statistic in advance. Add fields as real rules require them.

## 7. Calculation Context

```python
@dataclass
class CalculationContext:
    saved: SavedCharacter
    effective: EffectiveCharacter
```

Rules can read persistent data and modify effective data.

## 8. Updates

```python
@dataclass
class Update:
    priority: int
    source: str
    function: Callable[[CalculationContext], None]
```

Example:

```python
Update(
    priority=100,
    source="Amulet of Health",
    function=update_constitution,
)
```

Python itself is the rules language. Do not embed Python in YAML or build a custom effect DSL.

## 9. Priority Levels

Start with:

```python
BASE = 100
MODIFIERS = 200
DERIVED = 300
FINAL = 400
```

Intended use:
- BASE: modify raw effective properties.
- MODIFIERS: ability modifiers and proficiency-related values.
- DERIVED: AC, HP, attacks, spell DC, etc.
- FINAL: modifications to already-derived values.

Add complexity only when an actual rule requires it.

## 10. Rules Registry

The character file contains IDs; Python registries map IDs to implementations.

```python
ITEMS = {
    "amulet_of_health": AmuletOfHealth,
}

FEATURES = {}
CLASSES = {}
SUBCLASSES = {}
SPELLS = {}
SPECIES = {}
```

Do not store Python implementation details in character files.

This also makes homebrew easy: add an implementation and register its ID.

## 11. Active Sources

Always active:
- Class/subclass
- Species/background
- Features
- Proficiencies

Active when equipped:
- Armor
- Shields
- Weapons
- Worn magic items

Active when currently present:
- Conditions
- Concentration effects
- Temporary buffs/debuffs

Not inherently active:
- Learned spells
- Unused inventory items
- Available abilities that are not currently producing an effect

Knowing Hex does not apply Hex. Casting Hex creates an active effect.

## 12. Calculation

```python
def calculate(character):
    effective = create_effective_character(character)

    context = CalculationContext(
        saved=character,
        effective=effective,
    )

    updates = standard_updates(character)

    for source in get_active_sources(character):
        updates.extend(source.get_updates())

    updates.sort(key=lambda update: update.priority)

    for update in updates:
        update.function(context)

    return effective
```

This is the core rules pipeline.

## 13. Initial Vertical Slice

Prove the architecture with:

```text
YAML
  -> SavedCharacter
  -> base CON = 16
  -> Amulet of Health
  -> effective CON = 19
  -> modifier = +4
```

Unequipping the amulet and recalculating must produce CON 16 and modifier +3.

No rollback logic is needed.

## 14. Implementation Order

1. YAML loading.
2. SavedCharacter.
3. EffectiveCharacter.
4. Base ability initialization.
5. Update abstraction.
6. Rules registry.
7. Active-source collection.
8. Priority sorting/application.
9. Ability modifiers.
10. Amulet of Health.
11. Debugging/output.
12. Armor Class.
13. Saving throws and skills.
14. HP and hit dice.
15. Resources and spell slots.
16. Spells.
17. Actions.
18. Short/long rests.
19. Conditions and temporary effects.
20. Persistence of state changes.

Implement incrementally and test each layer.

## 15. Actions vs. Calculation

Calculation answers:

> What is true about this character right now?

Actions answer:

> What happens when the player does something?

Examples:
- Cast a spell.
- Attack.
- Use an ability.
- Drink a potion.
- Equip/unequip an item.
- Short rest.
- Long rest.
- Spend a hit die.

Actions mutate persistent `SavedCharacter` data/state. Then the effective character is recalculated.

Example:

```text
cast spell
   -> consume spell slot
   -> create active effect
   -> set concentration
   -> save
   -> recalculate
```

Do not treat `EffectiveCharacter` as authoritative game state.

## 16. Inventory and Equipment

Inventory represents ownership.

Equipment represents what is currently equipped.

Using a potion changes persistent inventory. Equipping an item changes persistent equipment. The effects of those choices are calculated.

## 17. Spells

Character data stores learned/prepared selections and mutable slot state.

Spell mechanics live in Python.

Casting can:
- Consume a slot.
- Require an attack roll or saving throw.
- Create an active effect.
- Set concentration.
- Modify conditions/state.

Known spells are not automatically active effects.

## 18. Multiclassing

Represent classes independently:

```yaml
classes:
  - name: Fighter
    level: 3
    subclass: Champion
  - name: Warlock
    level: 4
    subclass: Celestial
```

Total character level and proficiency bonus are calculated. Class-specific features depend on the relevant class level.

## 19. Resources

Mutable resources belong in state:

```yaml
state:
  resources:
    second_wind: 1
    action_surge: 1
    celestial_revelation: 1
  spell_slots:
    "1": 3
    "2": 2
    "3": 0
  hit_dice:
    d8: 6
```

Maximums and recharge rules generally come from Python rules.

Initial recharge types:
- `short_rest`
- `long_rest`
- `never`

## 20. Conditions and Active Effects

Conditions:

```yaml
state:
  conditions:
    - poisoned
```

Temporary effects may be represented as:

```yaml
state:
  active_effects:
    - id: hex
      duration_remaining: 47
```

Keep these structures simple. Interpret them with Python rather than creating a DSL.

## 21. Persistence

Only `SavedCharacter` is authoritative and serialized.

Normal cycle:

```text
load YAML
 -> SavedCharacter
 -> calculate
 -> EffectiveCharacter
 -> player action
 -> mutate SavedCharacter
 -> save YAML
 -> recalculate
```

Never serialize `EffectiveCharacter`.

## 22. Debugging

Every update should have a human-readable source.

At minimum:

```text
[100] Amulet of Health
[200] Ability modifiers
[300] Armor Class
```

Eventually support explanations such as:

```text
Constitution
    Base: 16
    Amulet of Health: 19
    Final: 19

Constitution modifier
    Constitution: 19
    Modifier: +4
```

Transparency is more important than cleverness.

## 23. Testing

Tests should correspond to actual rules and user-visible behavior.

Examples:
- 8 -> -1 modifier
- 17 -> +3 modifier
- 19 -> +4 modifier
- Equipped Amulet -> CON 19
- Unequipped Amulet -> base CON
- Using potion -> inventory decreases
- Casting spell -> slot decreases
- Short rest -> short-rest resource restored
- Long rest -> long-rest resource restored

Prefer end-to-end pipeline tests where practical.

## 24. Non-Goals

Initially avoid:
- Full VTT functionality.
- Network multiplayer.
- Complex GUI frameworks.
- Custom rules DSL.
- General dependency graphs.
- Automatic natural-language interpretation of every rule.
- Persisting derived values.
- Supporting every D&D book.
- Perfect automation of ambiguous rules.

## 25. Coding-Agent Rules

When extending the project:

1. Read this document first.
2. Inspect existing code before adding abstractions.
3. Prefer the smallest implementation satisfying the new rule.
4. Keep persistent and calculated data separate.
5. Put D&D mechanics in Python.
6. Use stable IDs for rules-bearing entities.
7. Do not put Python or expressions in YAML.
8. Do not persist values that can be recalculated.
9. Give every update a useful source name.
10. Add a focused test for every new rule.
11. Do not generalize until multiple real rules demonstrate the need.
12. Preserve existing YAML compatibility where practical.

The goal is a small, understandable rules engine that is easy for its owner and coding agents to modify.
