from typing import NamedTuple
import re

from .errors import ComputorError

# doc: https://docs.python.org/3/library/re.html#writing-a-tokenizer

class Token(NamedTuple):
    kind: str
    text: str
    column: int
    position: int
    prevsp: bool = False

def tokenize(code):
    token_specification = [
        # Integer or decimal number
        ('NB',   r'[0-9]+(\.[0-9]*)?|\.[0-9]+'),  
        # Equal operator    
        ('EQ',   r'='),     
        # Identifiers                       
        ('VAR',       r'[A-Za-z]'),  
        # Arithmetic operators  
        ('OP_D',       r'[+\-]'),
        # Arithmetic operators  
        ('OP_B',       r'[*^]'),
        # Skip over spaces and tabs     
        ('SKIP',     r'[ \t]+'),
        # Any other character       
        ('MISMATCH', r'.'),           
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    prevsp = False
    count = 0
    yield Token('START', '', 0, 0, prevsp)
    for mo in re.finditer(tok_regex, code):
        count += 1
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start()
        if kind == 'VAR':
            value = mo.group()
        elif kind == 'SKIP':
            prevsp = True
            continue
        elif kind == 'MISMATCH':
            raise ComputorError(
                f"unexpected character '{mo.group()}' at column {mo.start() + 1}",
                "LXR_01"
            )
        yield Token(kind, value, column, count, prevsp)
        prevsp = False
    yield Token('END', '', len(code), count, prevsp)
