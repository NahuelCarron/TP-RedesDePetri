#!/usr/bin/env python
#
# Tokens module
#


"""Token module"""


# Standard packages
from enum import Enum

# Installed packages
## NOTE: this is empty for now

# Local packages
## NOTE: this is empty for now


class AnnotationTokenTypes(Enum):
    """Annotation token types enum"""
    # Petri net elements
    PLACES = 'P'
    PLACE = 'pn'
    TRANSITIONS = 'T'
    TRANSITION = 'tn'
    AWN = 'A'
    MOMENT_ZERO = 'm0'
    # Others
    LPAREN = '('
    RPAREN = ')'
    LBRACE = '{'
    RBRACE = '}'
    EQUAL = '='
    NUMBER = '0-9'
    COMMA = ','


class AnnotationToken:
    """Petri net annotation token, not confuse with thread token!"""

    def __init__(
            self,
            ttype: AnnotationTokenTypes,
            tvalue: any
            ) -> None:
        # Extra 't' avoids override type attribute
        self.ttype = ttype
        self.tvalue = tvalue


if __name__ == '__main__':
    print('Este modulo no debe ejecutarse desde consola')
