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
from re import match as re_match
from enum import Enum
import threading
import time

# Installed packages
## NOTE: this is empty for now

# Local packages
## NOTE: this is empty for now


# Constants
DEBUG = False


###############################################
# Tokenization                                #
###############################################


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


class Lexer:
    """This is responsive of break Petri nets annotation into tokens"""

    def __init__(self) -> None:
        self.index = 0
        self.text = ''

    def advance(self, number: int=1) -> None:
        """Advance index NUMBER amount of chars"""
        self.index += number

    def advance_line(self) -> None:
        """Advance index to next line"""
        while not self.get_current_text().startswith('\n'):
            self.advance()
        self.advance()

    def get_current_text(self) -> str:
        """Get current text left"""
        if self.index < len(self.text):
            return self.text[self.index:]
        else:
            return ''

    def skip_whitespaces(self) -> None:
        """Advance until no whitespaces are left"""
        while self.get_current_text().startswith(' '):
            self.advance(1)

    def tokenize_number(self) -> AnnotationToken:
        """Tokenize number"""
        number = ''
        while self.get_current_text()[0].isdigit():
            number += self.get_current_text()[0]
            self.advance()
        number = int(number)
        return AnnotationToken(AnnotationTokenTypes.NUMBER, number)

    def tokenize(self, annotation: str) -> list:
        """Break Petri ANNOTATION into tokens"""
        assert annotation
        self.text = annotation

        result = []

        while self.get_current_text():

            # Skip comments
            if self.get_current_text().startswith('#'):
                self.advance_line()
                continue

            # Skip whitespaces
            if self.get_current_text().startswith(' '):
                self.skip_whitespaces()
                continue

            # Skip new lines
            if self.get_current_text().startswith('\n'):
                self.advance_line()
                continue

            # Tokenize PLACES
            if self.get_current_text().startswith('P'):
                result.append(
                    AnnotationToken(
                        AnnotationTokenTypes.PLACES,
                        'P'
                        )
                    )
                self.advance(1)
                continue

            # Tokenize PLACE
            match = re_match(r'p[0-9]+', self.get_current_text())
            if match:
                result.append(
                    AnnotationToken(AnnotationTokenTypes.PLACE, match.group())
                )
                self.advance(len(match.group()))
                continue

            # Tokenize TRANSITIONS
            if self.get_current_text().startswith('T'):
                result.append(
                    AnnotationToken(
                        AnnotationTokenTypes.TRANSITIONS,
                        'T'
                        )
                    )
                self.advance(1)
                continue

            # Tokenize TRANSITION
            match = re_match(r't[0-9]+', self.get_current_text())
            if match:
                result.append(
                    AnnotationToken(AnnotationTokenTypes.TRANSITION, match.group())
                )
                self.advance(len(match.group()))
                continue

            # Tokenize AWN
            if self.get_current_text().startswith('A'):
                result.append(
                    AnnotationToken(
                        AnnotationTokenTypes.AWN,
                        'A'
                        )
                    )
                self.advance(1)
                continue

            # Tokenize MOMENTS_ZERO
            if self.get_current_text().startswith('m0'):
                result.append(
                    AnnotationToken(
                        AnnotationTokenTypes.MOMENT_ZERO,
                        'M0'
                        )
                    )
                self.advance(2)
                continue

            # Tokenize LPAREN
            if self.get_current_text().startswith('('):
                result.append(AnnotationToken(
                    AnnotationTokenTypes.LPAREN,
                    '('
                ))
                self.advance(1)
                continue

            # Tokenize RPAREN
            if self.get_current_text().startswith(')'):
                result.append(AnnotationToken(
                    AnnotationTokenTypes.RPAREN,
                    '('
                ))
                self.advance(1)
                continue

            # Tokenize LBRACE
            if self.get_current_text().startswith('{'):
                result.append(AnnotationToken(
                    AnnotationTokenTypes.LBRACE,
                    '{'
                ))
                self.advance(1)
                continue

            # Tokenize RBRACE
            if self.get_current_text().startswith('}'):
                result.append(AnnotationToken(
                    AnnotationTokenTypes.RBRACE,
                    '}'
                ))
                self.advance(1)
                continue

            # Tokenize EQUAL
            if self.get_current_text().startswith('='):
                result.append(AnnotationToken(
                    AnnotationTokenTypes.EQUAL,
                    '='
                ))
                self.advance(1)
                continue

            # Tokenize NUMBER
            if self.get_current_text()[0].isdigit():
                result.append(self.tokenize_number())
                continue

            # Tokenize COMMA
            if self.get_current_text().startswith(','):
                result.append(AnnotationToken(
                    AnnotationTokenTypes.COMMA,
                    ','
                ))
                self.advance(1)
                continue

            raise Exception(f'Invalid syntax! =>\n{self.get_current_text()}')

        return result


###############################################
# Parsing                                     #
###############################################


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


class Parser:
    """This is responsive of convert tokens into Petri transition nodes"""

    def __init__(self) -> None:
        self.index = 0
        self.tokens = []
        self.places_list = []
        self.transitions_list = []

    def get_current_token(self) -> AnnotationToken:
        """Returns current token"""
        return self.tokens[self.index] if self.index < len(self.tokens) else None

    def eat(self, token_type: AnnotationTokenTypes) -> None:
        """Eat current token, if types matchs, advance otherwise raise exception"""
        current_token_type = self.get_current_token().ttype
        if current_token_type is token_type:
            self.index += 1
        else:
            raise SyntaxError(f'Expected {token_type} but founded {current_token_type}')

    def eat_optional_comma(self) -> None:
        """Optionally eat comma"""
        if self.get_current_token().ttype is AnnotationTokenTypes.COMMA:
            self.eat(AnnotationTokenTypes.COMMA)

    def append_transition_nodes_to_list(self) -> None:
        """
        Push T = {...} related tokens to stack
        transitions : TRANSITIONS EQUAL LBRACE (TRANSITION COMMA?)+ RBRACE
        """
        self.eat(AnnotationTokenTypes.TRANSITIONS)
        self.eat(AnnotationTokenTypes.EQUAL)
        self.eat(AnnotationTokenTypes.LBRACE)

        while self.get_current_token().ttype is not AnnotationTokenTypes.RBRACE:
            node = self.build_trainsition_node()
            self.transitions_list.append(node)
            self.eat_optional_comma()

        self.eat(AnnotationTokenTypes.RBRACE)

    def build_trainsition_node(self) -> TransitionNode:
        """Returns transition ast node"""
        name = self.get_current_token().tvalue
        self.eat(AnnotationTokenTypes.TRANSITION)
        return TransitionNode(name)

    def append_place_nodes_to_list(self) -> None:
        """
        Push P = {...} related tokens to stack
        places : PLACES EQUAL LBRACE (PLACE COMMA?)+ RBRACE
        """
        self.eat(AnnotationTokenTypes.PLACES)
        self.eat(AnnotationTokenTypes.EQUAL)
        self.eat(AnnotationTokenTypes.LBRACE)

        while self.get_current_token().ttype is not AnnotationTokenTypes.RBRACE:
            node = self.build_place_node()
            self.places_list.append(node)
            self.eat_optional_comma()

        self.eat(AnnotationTokenTypes.RBRACE)

    def build_place_node(self) -> PlaceNode:
        """Returns place ast node"""
        name = self.get_current_token().tvalue
        self.eat(AnnotationTokenTypes.PLACE)
        return PlaceNode(name, 1)

    def build_place_or_transition_node(self):
        """Returns Place or Transition node"""
        if self.get_current_token().ttype is AnnotationTokenTypes.TRANSITION:
            return self.build_trainsition_node()
        elif self.get_current_token().ttype is AnnotationTokenTypes.PLACE:
            return self.build_place_node()
        else:
            raise SyntaxError(
                f'Expected "transition" or "place" but founded "{self.get_current_token().tvalue}"'
            )

    def assign_awn_nodes(self) -> None:
        """
        Assign awn node to transitions nodes
        """
        self.eat(AnnotationTokenTypes.AWN)
        self.eat(AnnotationTokenTypes.EQUAL)
        self.eat(AnnotationTokenTypes.LBRACE)

        while self.get_current_token().ttype is AnnotationTokenTypes.LBRACE:
            self.assign_single_awn_node()
            self.eat_optional_comma()

        self.eat(AnnotationTokenTypes.RBRACE)

    def get_refereced_transition_or_place(self) -> str:
        """Returns next transition or place node using reference name"""
        next_node = self.build_place_or_transition_node()
        return self.search_node_by_name(next_node.name)

    def assign_single_awn_node(self) -> AwnNode:
        """Build awn ast node"""
        # Extract input and output nodes
        #
        # These extracted nodes arent the real nodes,
        # remember that nodes are repeated in "T"/"P" and in "A"
        #
        # Nodes are "input" and "output" from the view of the awn
        #
        # Maybe in a future could be implemented a symbols table for this
        self.eat(AnnotationTokenTypes.LBRACE)
        input_node = self.get_refereced_transition_or_place()
        self.eat(AnnotationTokenTypes.COMMA)
        output_node = self.get_refereced_transition_or_place()
        self.eat(AnnotationTokenTypes.RBRACE)

        # Check that the nodes arent the same type
        if isinstance(input_node, type(output_node)):
            raise Exception('Awns only can be t->p or p->t')

        name = f'{input_node.name}->{output_node.name}'

        # Assign Awn node to transition
        ## TODO: check how awns with more weight are annotated and implement it
        awn_new_node = AwnNode(name, 1, input_node, output_node)
        if isinstance(input_node, TransitionNode):
            input_node.output_awns.append(awn_new_node)
        else:
            output_node.input_awns.append(awn_new_node)

    def search_node_by_name(self, name:str):
        """Return transition or place node with same name"""
        result = None
        for node in (self.transitions_list + self.places_list):
            if node.name == name:
                result = node
                break
        if result is None:
            raise Exception(f'{name} referenced before assignment')
        return result

    def assign_place_starting_amounts(self) -> None:
        """Assign starting amounts to places in list"""
        self.eat(AnnotationTokenTypes.MOMENT_ZERO)
        self.eat(AnnotationTokenTypes.EQUAL)
        self.eat(AnnotationTokenTypes.LBRACE)

        # Maybe in a future could be implemented a
        # symbols table to assign these amounts

        while self.get_current_token().ttype is AnnotationTokenTypes.MOMENT_ZERO:
            self.eat(AnnotationTokenTypes.MOMENT_ZERO)
            self.eat(AnnotationTokenTypes.LPAREN)
            place_node = self.get_refereced_transition_or_place()
            self.eat(AnnotationTokenTypes.RPAREN)
            self.eat(AnnotationTokenTypes.EQUAL)
            number = self.get_current_token().tvalue
            place_node.starting_amounts = number
            self.eat(AnnotationTokenTypes.NUMBER)
            self.eat_optional_comma()

        self.eat(AnnotationTokenTypes.RBRACE)

    def build_petri_net_node(self) -> PetriNetNode:
        """
        Build Petri net ast node
        """
        while self.get_current_token() is not None:
            if self.get_current_token().ttype is AnnotationTokenTypes.PLACES:
                self.append_place_nodes_to_list()
            elif self.get_current_token().ttype is AnnotationTokenTypes.TRANSITIONS:
                self.append_transition_nodes_to_list()
            elif self.get_current_token().ttype is AnnotationTokenTypes.AWN:
                self.assign_awn_nodes()
            elif self.get_current_token().ttype is AnnotationTokenTypes.MOMENT_ZERO:
                self.assign_place_starting_amounts()
        return PetriNetNode(self.transitions_list)

    def parse(self, tokens: list) -> PetriNetNode:
        """
        Parse Petri nets TOKENS into PetriNetNode
        """
        assert tokens
        self.tokens = tokens
        return self.build_petri_net_node()


###############################################
# Interpretation                              #
###############################################


class ResourceToken:
    """Resource Token for thread"""


class ThreadedPlace:
    """Place with useful methods to run Petri net threads"""

    def __init__(self, name: str, starting_tokens_count:int) -> None:
        self.name = name
        self.tokens_stack = []
        self.create(starting_tokens_count)

    def create(self, amount: int) -> None:
        """Create AMOUNT of new resource tokens"""
        for _ in range(amount):
            self.tokens_stack.append(ResourceToken())

    def consume(self, amount:int) -> list:
        """Return AMOUNT of resource tokens"""
        if self.count() >= amount:
            return self.tokens_stack[:amount]
        raise Exception('Resources not available')

    def produce(self, tokens: list) -> None:
        """Add resources TOKENS to this place"""
        self.tokens_stack += tokens

    def count(self) -> int:
        """Return count of resource tokens"""
        return len(self.tokens_stack)


class ThreadedTransition:
    """Transition with useful methods to run Petri net threads"""

    def __init__(self, name: str, input_awns: list, output_awns: list) -> None:
        self.name = name
        self.input_awns = input_awns
        self.output_awns = output_awns
        self.resources_token_stack = []

    def are_all_inputs_enabled(self) -> bool:
        """Check that all input awns are enabled"""
        result = True
        for input_awn in self.input_awns:
            if not input_awn.is_enabled():
                result = False
        return result

    def get_all_resources(self) -> None:
        """Get all resources from awns to resources stack"""
        for input_awn in self.input_awns:
            self.resources_token_stack += input_awn.get_resources()

    def pass_all_resources(self) -> None:
        """Pass all resources to output awns"""
        for output_awns in self.output_awns:
            tokens_to_pass = self.resources_token_stack[:output_awns.weight]
            output_awns.pass_resources(tokens_to_pass)
        self.resources_token_stack = []

    def critical_section(self) -> None:
        """Thread critical section"""
        # NOTE: this print is not critical, but is useful as example
        input_names = [awn.get_input_name() for awn in self.input_awns]
        output_names = [awn.get_output_name() for awn in self.output_awns]
        print(
            'running:'
            f'\t[{",".join(input_names)}] => {self.name} => [{",".join(output_names)}]'
            f'\t({len(self.resources_token_stack)} resource tokens used)'
        )
        time.sleep(0.5)

    def run(self) -> None:
        """Run transition infinite loop"""
        while True:
            if self.are_all_inputs_enabled():
                self.get_all_resources()
                self.critical_section()
                self.pass_all_resources()


class ThreadedAwn:
    """Awn with useful methods to run Petri net threads"""

    def __init__(self, name: str, weight:int, input, output) -> None:
        self.name = name
        self.weight = weight
        self.input = input
        self.output = output

    def get_input_name(self) -> str:
        """Returns input name"""
        return self.input.name

    def get_output_name(self) -> str:
        """Returns output name"""
        return self.output.name

    def is_enabled(self) -> bool:
        """Check if the awn is enabled"""
        if not isinstance(self.input, ThreadedPlace):
            raise Exception(f'{self.name}: cannot extract resources from {self.input.name}, must be a Place')
        return self.input.count() >= self.weight

    def pass_resources(self, tokens:list) -> None:
        """Pass resources to output"""
        if not isinstance(self.output, ThreadedPlace):
            raise Exception(f'{self.name}: cannot pass resources to {self.output.name}, must be a Place')
        # Create new tokens
        while len(tokens) < self.weight:
            tokens.append(ResourceToken())
        self.output.produce(tokens)

    def get_resources(self) -> list:
        """Get resources from input"""
        if not isinstance(self.input, ThreadedPlace):
            raise Exception(f'{self.name}: cannot extract resources from Transition {self.input.name}')
        return self.input.consume(self.weight)


class NodeVisitor:
    """Implements a generic method visit"""

    def visit(self, node):
        """Generic method to visit NODE"""
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visitor)
        return visitor(node)

    def generic_visitor(self, node) -> None:
        """Raise exception if the visit method to NODE not exist"""
        raise Exception(f'No visit_{type(node).__name__} method founded')


class Interpreter(NodeVisitor):
    """This is responsive for interpret Petri ast nodes into threads"""

    def __init__(self) -> None:
        # Global states used to reference
        self.transitions_references = []
        self.places_references = []

    # pylint: disable=invalid-name
    def visit_PetriNetNode(self, node: PetriNetNode) -> list:
        """Visit PetriNetNode NODE"""
        return [self.visit(transition) for transition in node.transitions]

    # pylint: disable=invalid-name
    def visit_PlaceNode(self, node: PlaceNode):
        """Visit PlaceNode NODE"""
        new_place = ThreadedPlace(node.name, node.starting_amount)
        self.places_references.append(new_place)
        return new_place

    # pylint: disable=invalid-name
    def visit_TransitionNode(self, node: TransitionNode):
        """Visit TransitionNode NODE"""
        transition = ThreadedTransition(node.name, None, None)
        self.transitions_references.append(transition)
        transition.input_awns = [self.visit(awn) for awn in node.input_awns]
        transition.output_awns = [self.visit(awn) for awn in node.output_awns]
        return threading.Thread(target=transition.run)

    # pylint: disable=invalid-name
    def visit_AwnNode(self, node: AwnNode):
        """Visit AwnNode NODE"""
        new_input = self.search_by_name(node.input.name)
        new_input = new_input if new_input else self.visit(node.input)
        new_output = self.search_by_name(node.output.name)
        new_output = new_output if new_output else self.visit(node.output)
        return ThreadedAwn(
            node.name,
            node.weight,
            new_input,
            new_output
            )

    def search_by_name(self, name):
        """Search threaded node by name"""
        result = None
        for node in (self.transitions_references + self.places_references):
            if node.name == name:
                result = node
        return result

    def interpret(self, petri_ast: PetriNetNode) -> list:
        """Interprets PETRI_AST nodes into threads"""
        assert petri_ast
        return self.visit(petri_ast)


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
