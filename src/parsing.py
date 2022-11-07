#!/usr/bin/env python
#
# Parsing module
#


"""Parsing module"""


# Standard packages
## NOTE: this is empty for now

# Installed packages
## NOTE: this is empty for now

# Local packages
from src.token import(
    AnnotationToken, AnnotationTokenTypes,
)
from src.node import (
    PetriNetNode, PlaceNode, TransitionNode, AwnNode,
)


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
            if self.get_current_token().ttype is not AnnotationTokenTypes.COMMA:
                break
            self.eat(AnnotationTokenTypes.COMMA)

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
            if self.get_current_token().ttype is not AnnotationTokenTypes.COMMA:
                break
            self.eat(AnnotationTokenTypes.COMMA)

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
            if self.get_current_token().ttype is not AnnotationTokenTypes.COMMA:
                break
            self.eat(AnnotationTokenTypes.COMMA)

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
        
        weight = self.eat_optional_weight()
        
        # Check that the nodes arent the same type
        if isinstance(input_node, type(output_node)):
            raise Exception('Awns only can be t->p or p->t')

        name = f'{input_node.name}->{output_node.name}'

        # Assign Awn node to transition
        ## TODO: check how awns with more weight are annotated and implement it
        awn_new_node = AwnNode(name, weight, input_node, output_node)
        if isinstance(input_node, TransitionNode):
            input_node.output_awns.append(awn_new_node)
        else:
            output_node.input_awns.append(awn_new_node)

    def eat_optional_weight(self) -> None:
        """Optionally eat weight"""
        if self.get_current_token().ttype is AnnotationTokenTypes.EQUAL:
            self.eat(AnnotationTokenTypes.EQUAL)
            weight = self.get_current_token().tvalue
            self.eat(AnnotationTokenTypes.NUMBER)
        else: 
            weight = 1
        return weight

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
            place_node.starting_amount = number
            self.eat(AnnotationTokenTypes.NUMBER)
            if self.get_current_token().ttype is not AnnotationTokenTypes.COMMA:
                break
            self.eat(AnnotationTokenTypes.COMMA)

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


if __name__ == '__main__':
    print('Este modulo no debe ejecutarse desde consola')
