

0. Misc
    2. make hit die a state resource
    3. add exp
    4. update max hp calculation to take list of rolled values
    5. change inspiration to int
    6. Add attacks
    7. add spells
    8. add other actions
    9. Don't add duplicate values e.g. class, race
    10. add race to base
    11. speed
    12. Spell DC
    13. passive perception
    14. handle case sensitivity
        1. and maybe spaces too
    17. alignment
    18. languages
    19. background
1. Fill out character sheet
    1. add all features
        1. how to pass metadata to features???
        2. including features from items
    2. Add spells
    3. add actions
2. Create all Rules
    1. Class
        1. move spell slots and resources and class-specific features to class
    2. Resource (mainly for recharge mechanism)
3. Design and Add character actions
4. Add descriptions

```Python
# load saved character
# compute effective character
# display effective character
while true:
    # do an action
    # save base character
    # display effective character
```


### Additional rules infrastructure

```Python
class CharacterAction(Rule):
    """
    An entry in the EffectiveCharacter's action list
    Has a short name for display
    Provides a description of the action
    Includes 'cost'
    """
```