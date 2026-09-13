# Implementation Status of @DESIGN.md

## Implemented
1. **YAML Loading & Persistent Model (`SavedCharacter`)**: Loads character YAML files (e.g., `Northstar.yaml`) into a structured persistent dataclass (`name`, `classes`, `abilities`, `proficiencies`, `inventory`, `equipment`, `features`, `spells`, `state`).
2. **Effective Model (`EffectiveCharacter` & `Abilities`)**: Represents temporary calculated state, separating persistent data from derived values.
3. **Calculation Pipeline & Priorities**: 
   - Supports priority levels (`BASE = 100`, `MODIFIERS = 200`, `DERIVED = 300`, `FINAL = 400`).
   - Implements `CalculationContext`, `Update`, and `calculate()` pipeline.
4. **Active Sources & Registries**:
   - `active_sources()` collects active items/features.
   - `ITEMS` registry with `Amulet of Health`, `Scale Mail`, and `Shield` rules.
5. **Combat Statistics & Proficiency Bonus**:
   - Proficiency bonus calculation based on total character level (`(total_level - 1) // 4 + 2`).
   - Armor Class (AC) calculation incorporating base unarmored AC, medium armor (Scale Mail with Dex cap), and shields.
   - Initiative calculation based on Dexterity modifier.
6. **Test Suite**:
   - 8 passing unit tests covering loading, effective stats, rules, active sources, and combat statistics.

## Not Yet Implemented / Planned
1. **Saving Throws & Skills**: Proficiency bonus application to saving throws and skills (including expertise).
2. **HP & Hit Dice**: Maximum HP calculation, hit dice tracking, and expenditure.
3. **Resources & Spell Slots**: Tracking and recharging resources/spell slots on short/long rests.
4. **Spells & Features**: Full integration of `FEATURES`, `CLASSES`, `SUBCLASSES`, `SPELLS`, and `SPECIES` registries with spellcasting mechanics and active effects/concentration.
5. **Actions & State Mutators**: Player actions (attacking, casting, resting, equipping/unequipping) that mutate `SavedCharacter` persistent state and serialize back to YAML.
6. **Conditions & Temporary Effects**: Poisoned, active effects, and duration tracking.
