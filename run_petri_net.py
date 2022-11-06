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
from src.tokenization import Lexer
from src.parsing import Parser
import src.interpretation as interpretation
import sys

# Installed packages
import keyboard

# Local packages
sys.path.insert(0, './src/')

# Constants
DEBUG = False


###############################################
# Argument processing                         #
###############################################


def run_petri_net(annotation: str) -> None:
    """Run concurrent threads using Petri net ANNOTATION"""
    # Process
    tokens = Lexer().tokenize(annotation)
    if DEBUG:
        for token in tokens:
            print(f'> {token.ttype}\t\t{token.tvalue}')
    tree = Parser().parse(tokens)
    threads = interpretation.Interpreter().interpret(tree)
    # Start
    for thread in threads:
        thread.start()
    # Stop
    while True:
        if keyboard.is_pressed('a'):
            print('Pressed key, stopping threads...')
            interpretation.KEEP_RUNNING = False # workaround to stop threads, join doesnt works
            break


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
