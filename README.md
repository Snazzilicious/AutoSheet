# D&D Character Sheet

A lightweight, automated D&D character sheet implemented in Python with a simple YAML character file.

The project is intended primarily for personal use and experimentation rather than as a full virtual tabletop.

## Features

The architecture supports:

- YAML-based character storage
- Multiclass characters
- Base ability scores
- Persistent inventory and equipment
- Persistent game state
- Calculated effective character state
- Python-based rules
- Automatic ability modifiers
- Rule updates with priorities
- Equipment-driven effects
- Automatic AC and combat calculations
- Saving throws and skill bonuses
- Proficiency bonus calculation
- HP and hit dice calculation
- Spell slot tracking and casting
- Short and long rests
- Conditions and temporary effects
- Item equipping/unequipping and state mutation/saving

## Core Concept

The character file contains:

> What the player says is true about the character.

The application calculates:

> What the game engine can derive from that information.

For example:

```yaml
abilities:
  base:
    constitution: 16

equipment:
  worn:
    - amulet_of_health
```

The saved character has Constitution 16. The calculated effective character has Constitution 19 because the amulet is equipped.

Unequip the amulet and recalculate: Constitution returns to 16.

This avoids storing derived values and avoids complicated rollback logic.

## Project Structure

A planned structure is:

```text
dnd-character/
├── characters/
│   └── northstar.yaml
├── dnd/
│   ├── character.py
│   ├── calculation.py
│   ├── rules.py
│   ├── items.py
│   ├── classes.py
│   ├── features.py
│   └── spells.py
├── tests/
└── main.py
```

The exact structure may evolve.

## Character Files

Characters are currently stored as pure YAML.

Example:

```yaml
name: Northstar

classes:
  - name: Warlock
    level: 6
    subclass: Celestial

abilities:
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

inventory:
  dagger: 2
  amulet_of_health: 1

equipment:
  - scale_mail
  - shield
  - amulet_of_health

features:
  - agonizing_blast
  - repelling_blast

spells:
  learned:
    - hex
    - cure_wounds
  readied:
    - hex

state:
  hp:
    current: 37
    temporary: 0
  conditions: []
  concentration: null
```

### Stable IDs

Rules-bearing entities use stable IDs such as:

```yaml
- amulet_of_health
- agonizing_blast
- hex
```

Python maps those IDs to their implementations.

This keeps character files independent from Python implementation details.

## Calculated Values

Values such as these should not normally be written into the YAML file:

- Ability modifiers
- Proficiency bonus
- Armor Class
- Initiative
- Attack bonuses
- Spell save DC
- Effective ability scores
- Resistances
- Darkvision

They are calculated when needed.

This prevents stale derived values.

## Persistent Game State

Some values cannot be reconstructed from character definition and rules, so they must be saved.

Example:

```yaml
state:
  hp:
    current: 23
    temporary: 4

  spell_slots:
    "1": 2
    "2": 0

  conditions:
    - poisoned
```

If the character has three healing potions and uses one, the saved inventory changes from three to two.

## Equipment

Inventory means what the character owns.

Equipment means what is currently equipped.

```yaml
inventory:
  amulet_of_health: 1
  dagger: 2

equipment:
  armor: scale_mail
  shield: shield
  worn:
    - amulet_of_health
```

Only equipped items contribute equipment effects.

## Rules

D&D rules are implemented directly in Python.

There is intentionally no custom rules language.

For example:

```python
Update(
    priority=100,
    source="Amulet of Health",
    function=update_constitution,
)
```

The update modifies the temporary effective character.

## Calculation

The calculation pipeline is:

```text
YAML
  |
  v
SavedCharacter
  |
  v
collect active rules
  |
  v
sort updates by priority
  |
  v
apply Python updates
  |
  v
EffectiveCharacter
```

The effective character is disposable and can always be recreated from the saved character and rules.

## Why Recalculate?

Suppose:

```text
Base CON = 16
Amulet equipped -> effective CON = 19
Amulet unequipped -> effective CON = 16
```

The application never has to undo the amulet.

It starts from the saved character and applies whatever rules are currently active.

## Multiclassing

Classes are represented independently:

```yaml
classes:
  - name: Fighter
    level: 3
    subclass: Champion

  - name: Warlock
    level: 4
    subclass: Celestial
```

Total character level and proficiency bonus are calculated.

Class-specific mechanics depend on the relevant class level.

## Spells

Learned/prepared spells are character data:

```yaml
spells:
  learned:
    - hex
    - cure_wounds
  readied:
    - hex
```

Spell mechanics live in Python.

Knowing a spell does not mean it is currently active.

Casting a spell may:
- Consume a spell slot.
- Require an attack roll or saving throw.
- Create an active effect.
- Set concentration.
- Modify game state.

## Actions and State

Calculation answers:

> What is true about the character right now?

An action answers:

> What happens when the player does something?

Examples:
- Attack
- Cast a spell
- Drink a potion
- Use a class feature
- Equip an item
- Unequip an item
- Take a short rest
- Take a long rest
- Spend a hit die

Actions modify persistent state, then the character is recalculated.

## Development Philosophy

The project favors:

- Simple data structures
- Plain Python
- Small functions
- Explicit rules
- Deterministic calculation
- Easy debugging
- Incremental development

It deliberately avoids premature abstraction.

If one D&D rule needs a special case, implement the special case in Python. Generalize only when several real rules demonstrate that a common abstraction is useful.

## Installation

The current implementation uses PyYAML:

```bash
pip install pyyaml
```

## Running

The initial test application can be run with:

```bash
python main.py
```

The exact entry point may change as a user interface is added.

## Development

Start with a small vertical slice:

1. Load a YAML character.
2. Build a `SavedCharacter`.
3. Build an `EffectiveCharacter`.
4. Calculate ability modifiers.
5. Apply one equipment rule.
6. Verify equipping and unequipping.
7. Add tests.
8. Expand to AC and other derived statistics.

Do not attempt to implement the entire D&D ruleset at once.

## Testing

Tests can be run using `pytest`:

```bash
pytest
```

Tests correspond to real rules and user-visible behavior.

Examples:

```text
8 Strength -> -1 modifier
17 Dexterity -> +3 modifier
19 Constitution -> +4 modifier

Amulet equipped -> CON 19
Amulet unequipped -> base CON

Using a potion -> inventory decreases
Casting a spell -> slot decreases
Short rest -> short-rest resource restored
Long rest -> long-rest resource restored
```

## Status

This is an evolving personal project.

The architecture is intentionally small so that new D&D mechanics can be added as they become useful.
