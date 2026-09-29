
1. core.py
2. Display effective character
3. Fill out character sheet
4. Create all Rules
    1. Class
        1. move spell slots and resources and class-specific features to class
    2. Resource (mainly for recharge mechanism)
5. Design and Add character actions

```Python
# load saved character
# compute effective character
# display effective character
while true:
    # do an action
    # save base character
    # display effective character
```

### Spec for display

TODO


### Additional rules infrastructure

```Python
class CharacterAction(Rule):
    """
    An entry in the EffectiveCharacter's action list
    Has a short name for display
    Provides a description of the action
    Includes 'cost'
    """

class CharacterClass(Rule):
    def __init__( self, level ):
        pass
```