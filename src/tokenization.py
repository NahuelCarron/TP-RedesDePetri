#!/usr/bin/env python
#
# Tokenization module
#


"""Tokenization module"""


# Standard packages
from re import match as re_match

# Installed packages
## NOTE: this is empty for now

# Local packages
from token import (
    AnnotationTokenTypes, AnnotationToken,
    )


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


if __name__ == '__main__':
    print('Este modulo no debe ejecutarse desde consola')
