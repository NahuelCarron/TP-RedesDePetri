#!/usr/bin/env python
#
# Node module
#


"""Node module"""


# Standard packages
## NOTE: this is empty for now

# Installed packages
## NOTE: this is empty for now

# Local packages
## NOTE: this is empty for now


class PetriNetNode:
    """Petri net node class"""

    def __init__(self, transitions: list) -> None:
        self.transitions = transitions


class PlaceNode:
    """Petri place node class"""

    def __init__(self, name: str, starting_amount:int=1) -> None:
        self.name = name
        self.starting_amount = starting_amount


class TransitionNode:
    """Petri place node class"""

    def __init__(
            self,
            name: str,
            input_awns: list = None,
            output_awns: list = None
            ) -> None:
        self.name = name
        self.input_awns = input_awns if input_awns else []
        self.output_awns = output_awns if output_awns else []


class AwnNode:
    """Petri awn node class"""

    def __init__(self, name, weight:int, ainput, aoutput) -> None:
        # Extra 'a' avoids redefined-builtin
        self.name = name
        self.weight = weight
        self.input = ainput
        self.output = aoutput


if __name__ == '__main__':
    print('Este modulo no debe ejecutarse desde consola')
