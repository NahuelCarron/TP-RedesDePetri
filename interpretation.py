###############################################
# Interpretation                              #
###############################################


import threading
import time
from parsing import AwnNode, PetriNetNode, PlaceNode, TransitionNode


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
        tokens_input = [ str(awn.get_weight()) for awn in self.input_awns]
        message_input =  [place + " releases " + token + " tokens" for place, token in zip(input_names,tokens_input)]
        tokens_output = [ str(awn.get_weight()) for awn in self.output_awns]
        message_output = [ place + " received " + token + " tokens" for place, token in zip(output_names,tokens_output)]
        print(
            '\033[;32m running:'
            f'\t \033[;35m [{",".join(input_names)}] => \033[;33m {self.name} \033[;34m => [{",".join(output_names)}]'
            f'\t \033[;35m {message_input}'
            f'\t \033[;34m {message_output} \033[;37m'
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
    def get_weight(self) -> int:
        return self.weight

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
