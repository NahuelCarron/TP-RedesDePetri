#!/usr/bin/env python
#
# Runs concurrents threads from Petri nets annotations
#
# Thanks to professor Ariel Arbiser
# for teaching us concurrent programming
#
# TODO:
# - implement mN tokens amount for each moment.
#


"""Runs concurrents threads from Petri nets annotations"""


# Standard packages
import sys

# Installed packages
## NOTE: this is empty for now

# Local packages
sys.path.insert(0, './src/')
from src.interpretation import Interpreter
from src.parsing import Parser
from src.tokenization import Lexer

# Constants
DEBUG = False


###############################################
# Argument processing                         #
###############################################


def run_petri_net(annotation: str) -> None:
    """Run concurrent threads using Petri net ANNOTATION"""
    tokens = Lexer().tokenize(annotation)
    if DEBUG:
        for token in tokens:
            print(f'> {token.ttype}\t\t{token.tvalue}')
    tree = Parser().parse(tokens)
    threads = Interpreter().interpret(tree)
    for thread in threads:
        thread.start()


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print(
            '\nRun threads using Petri nets\n\n'
            'Usage:\n'
            '- $ python ./run_petri_net.py ./example_petri_net.pn\n'
        )
    else:
        with open(sys.argv[1], encoding='UTF-8') as f:
            content = f.read()
        run_petri_net(content)
