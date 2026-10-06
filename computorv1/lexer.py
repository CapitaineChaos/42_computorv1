from typing import NamedTuple
import re

from .errors import ComputorError

# doc: https://docs.python.org/3/library/re.html#writing-a-tokenizer

class Token(NamedTuple):
    kind: str
    text: str
    column: int

def tokenize(code):
    token_specification = [
        # Integer or decimal number
        ('NUMBER', r'[0-9]+(\.[0-9]*)?|\.[0-9]+'),  
        # Equal operator    
        ('EQUAL',   r'='),     
        # Identifiers                       
        ('VAR',       r'[A-Za-z]'),  
        # Arithmetic operators  
        ('OP',       r'[+\-*^/]'),
        # Skip over spaces and tabs     
        ('SKIP',     r'[ \t]+'),
        # Any other character       
        ('MISMATCH', r'.'),           
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start()
        if kind == 'VAR':
            value = mo.group()
        elif kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise ComputorError(
                f"unexpected character '{mo.group()}' at column {mo.start() + 1}"
            )
        yield Token(kind, value, column)
    yield Token('END', '', len(code))
