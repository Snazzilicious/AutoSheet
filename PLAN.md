# Implementation Plan for AutoSheet

This plan outlines incremental steps to implement the remaining requirements from `@DESIGN.md`. Each step is self-contained with verification tests.

---

### Step 1: Combat Statistics & Proficiency Bonus
* **Goal**: Implement proficiency bonus calculation, Armor Class (AC), and Initiative.
* **Tasks**:
  1. Calculate proficiency bonus based on total character level (`(total_level - 1) // 4 + 2` or standard D&D progression).
  2. Implement AC calculation rules (Base armor, dex modifier handling for medium/heavy/no armor, shield bonus).
  3. Implement Initiative calculation (Dexterity modifier + any feature bonuses).
  4. Add corresponding tests in `test_character.py`.

### Step 2: Saving Throws & Skills
* **Goal**: Calculate saving throw and skill proficiencies/bonuses.
* **Tasks**:
  1. Determine proficient saving throws from class data and proficiencies section.
  2. Calculate saving throw bonuses (ability modifier + proficiency bonus if proficient).
  3. Calculate skill bonuses (ability modifier + proficiency bonus if proficient, double if expertise).
  4. Add corresponding tests in `test_character.py`.

### Step 3: HP & Hit Dice
* **Goal**: Calculate maximum hit points and initialize/track hit dice.
* **Tasks**:
  1. Calculate Max HP based on class hit dice and Constitution modifier.
  2. Track hit dice per class/die type in effective character/combat stats.
  3. Add corresponding tests in `test_character.py`.

### Step 4: Resources & Spell Slots
* **Goal**: Track resources and spell slots from class features and rules.
* **Tasks**:
  1. Implement max resource limits and initial spell slot mapping from class levels.
  2. Expose resources and spell slots in `EffectiveCharacter`.
  3. Add corresponding tests in `test_character.py`.

### Step 5: Spells & Features Registries
* **Goal**: Fully populate and integrate `FEATURES`, `CLASSES`, `SUBCLASSES`, `SPELLS`, and `SPECIES` registries.
* **Tasks**:
  1. Implement feature rule classes (e.g., Agonizing Blast, Eldritch Mind, etc.) with updates.
  2. Implement class/subclass feature collection.
  3. Add corresponding tests in `test_character.py`.

### Step 6: Conditions & Temporary Effects
* **Goal**: Support active conditions and temporary effects in calculation.
* **Tasks**:
  1. Process active conditions (e.g., poisoned disadvantage/effects) and temporary effects.
  2. Add corresponding tests in `test_character.py`.

### Step 7: Actions & State Mutators
* **Goal**: Implement player actions that mutate persistent state and save back to YAML.
* **Tasks**:
  1. Implement actions: short rest, long rest, cast spell, spend hit die, equip/unequip items.
  2. Mutate `SavedCharacter` state and inventory/equipment.
  3. Implement character saving to YAML.
  4. Add end-to-end integration tests.
