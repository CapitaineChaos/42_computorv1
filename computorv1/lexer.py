from typing import NamedTuple
import re


class Token(NamedTuple):
    kind: str
    txt: str
    col: int
    code: str

    __repr__ = lambda self: f"Token({self.kind:<8}, {self.code}, {self.txt})"

def tokenize(code):
    token_specification = [
        # Integer or decimal number
        ('NB',       r'[0-9]+(\.[0-9]*)?|\.[0-9]+'),  
        # Equal operator    
        ('EQ',       r'='),     
        # Identifiers                       
        ('VAR',      r'[A-Za-z]'),  
        # Arithmetic operators  
        ('OP',       r'[+\-*^]'),
        # Skip over spaces and tabs     
        ('SKIP',     r'[ \t]+'),
        # Any other character       
        ('MISMATCH', r'[\s\S]'),           
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)

    yield Token('START', '', 0, 's')
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() + 1
        if kind == 'SKIP':
            tcode = ' '
        elif kind == 'NB':
            tcode = 'n'
        elif kind == 'VAR':
            tcode = 'v'
        elif kind == 'EQ' or kind == 'OP':
            tcode = value
        elif kind == 'MISMATCH':
            tcode = 'm'
        yield Token(kind, value, column, tcode)
    yield Token('END', '', len(code), 'e')

# def tokenize(code):
#     token_specification = [
#         # Integer or decimal number
#         ('NB',   r'[0-9]+(\.[0-9]*)?|\.[0-9]+'),  
#         # Equal operator    
#         ('EQ',   r'='),     
#         # Identifiers                       
#         ('VAR',       r'[A-Za-z]'),  
#         # Arithmetic operators  
#         ('OP_D',       r'[+\-]'),
#         # Arithmetic operators  
#         ('OP_B',       r'[*^]'),
#         # Skip over spaces and tabs     
#         ('SKIP',     r'[ \t]+'),
#         # Any other character       
#         ('MISMATCH', r'.'),           
#     ]
#     tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
#     prevsp = False
#     count = 0
#     yield Token('START', '', 0, 0, prevsp)
#     for mo in re.finditer(tok_regex, code):
#         count += 1
#         kind = mo.lastgroup
#         value = mo.group()
#         column = mo.start()
#         if kind == 'VAR':
#             value = mo.group()
#         elif kind == 'SKIP':
#             prevsp = True
#             continue
#         elif kind == 'MISMATCH':
#             raise ComputorError("LXR_01", text=mo.group(), col=mo.start() + 1)
#         yield Token(kind, value, column, count, prevsp)
#         prevsp = False
#     yield Token('END', '', len(code) - 1, count, prevsp)
