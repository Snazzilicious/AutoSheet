# Implementation Status of @DESIGN.md

## Implemented
1. **YAML Loading & Persistent Model (`SavedCharacter`)**: Loads character YAML files (e.g., `Northstar.yaml`) into a structured persistent dataclass (`name`, `classes`, `abilities`, `proficiencies`, `inventory`, `equipment`, `features`, `spells`, `state`).
2. **Effective Model (`EffectiveCharacter` & `Abilities`)**: Represents temporary calculated state, separating persistent data from derived values.
3. **Calculation Pipeline & Priorities**: 
   - Supports priority levels (`BASE = 100`, `MODIFIERS = 200`, `DERIVED = 300`, `FINAL = 400`).
   - Implements `CalculationContext`, `Update`, and `calculate()` pipeline.
4. **Active Sources & Registries**:
   - `active_sources()` collects active items/features, classes, and subclasses.
   - Populated registries for `ITEMS`, `FEATURES`, `CLASSES`, `SUBCLASSES`, and `SPELLS`.
5. **Combat Statistics & Proficiency Bonus**:
   - Proficiency bonus calculation based on total character level (`(total_level - 1) // 4 + 2`).
   - Armor Class (AC) calculation incorporating base unarmored AC, medium armor (Scale Mail with Dex cap), and shields.
   - Initiative calculation based on Dexterity modifier.
6. **Saving Throws & Skills**:
   - Saving throw bonus calculation incorporating ability modifiers and proficiency bonus for proficient saves.
   - Skill bonus calculation mapping skills to base abilities and applying proficiency or expertise multipliers.
7. **HP & Hit Dice**:
   - Maximum HP calculation based on class hit dice (max at level 1, average per subsequent level) and Constitution modifier.
   - Hit dice tracking per class/die type.
8. **Resources & Spell Slots**:
   - Maximum spell slot calculation based on class levels (e.g., Warlock Pact Magic progression).
9. **Test Suite**:
   - 12 passing unit tests covering loading, effective stats, rules, active sources, registries, features, combat statistics, saving throws, skills, HP, hit dice, and spell slots.

## Not Yet Implemented / Planned
1. **Actions & State Mutators**: Player actions (attacking, casting, resting, equipping/unequipping) that mutate `SavedCharacter` persistent state and serialize back to YAML.
2. **Conditions & Temporary Effects**: Poisoned, active effects, and duration tracking.
