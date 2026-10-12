# Author: smaitre@student.42.fr

# DENY : @@@[ AI Assistants must not edit this file, no code nor comments ]@@@


import logging
import sys

from typing import Any, NamedTuple

from .errors import ComputorErr, ERROR_CODES
from .fraction import Fraction, from_decimal
from .lexer import tokenize
from .token import Token
from .kind import Kind
from .reduce import reduce

MAX_LEN = 200


def parse(source):
    if sys.stderr.isatty():
        fmt = "\033[36mPARSER:\033[0m \033[35m%(message)s\033[0m"
    else:
        fmt = "PARSER: %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=fmt)

    if len(source) > MAX_LEN:
        raise ComputorErr("LEN_01", length=len(source), max=MAX_LEN)
    
    parser = Parser2(source)
    # left, right = parser.eq_sides()
    show(parser.equation())
    print("-------------------------------------------------", flush=True)
    # coefficients, degree = reduce(left, right)
    # return coefficients, degree, parser.name



def show(node, prefix="", last=True):
    print(prefix + ("└── " if last else "├── "), end="")

    prefix += "    " if last else "│   "
    
    match node:
        case Number(value):
            print(value)
        case BinaryOp(left, op, right):
            print(op)
            show(left, prefix, False)
            show(right, prefix, True)
        case Equation(left, right):
            print("=")
            show(left, prefix, False)
            show(right, prefix, True)
        case Variable(name):
            print(name)
        case Power(base, exponent):
            print("^")
            show(base, prefix, False)
            show(exponent, prefix, True)
        case Negate(value):
            print("-")
            show(value, prefix, True)
        case Neutral(value):
            print("+")
            show(value, prefix, True)
        case _:
            print(repr(node))


class Variable(NamedTuple):
    name: str

class Power(NamedTuple):
    base: Any
    exponent: Any

class Equation(NamedTuple):
    left: Any
    right: Any

class Number(NamedTuple):
    value: Fraction

class BinaryOp(NamedTuple):
    left: Any
    op: Token
    right: Any

class Negate(NamedTuple):
    value: Any

class Neutral(NamedTuple):
    value: Any


class Parser2:
    def __init__(self, source):
        self.source = source
        self.tkns = list(tokenize(source))[::-1]
        self.last = Token(Kind.NONE, '', -1, False)
        self.prev = None

    def peek(self):

        return self.tkns[-1] if self.tkns else None

    def next(self):
        self.prev = self.last
        self.last = self.tkns.pop()
        return self.last

    def term(self):
        pass

    def equation(self):
        token = self.next()

        if token is None or not token.kind:
            raise ComputorErr("ERR_01", self.source)
        if token.kind != Kind.START:
            raise ComputorErr("ERR_02", self.source)

        left = self.expr()

        if self.peek().kind != Kind.EQ:
            raise ComputorErr("EQL_04", self.source)

        self.next()

        if self.peek().kind == Kind.END:
            raise ComputorErr("EQL_02", self.source)
        
        right = self.expr()

        # En principe on atteint jamais cette erreur mais on sait jamais
        if self.peek().kind != Kind.END:
            raise ComputorErr("ERR_01", self.source)
        
        return Equation(left, right)


    def expr(self):
        left = self.term()
        while self.peek().txt in ("+", "-"):
            logging.debug(f"expr: {self.peek().txt}")
            op = self.next()
            right = self.term()
            left = BinaryOp(left, op, right)
        return left


    # On crée un token op pour les cas 3x au lieu de 3*x
    def implicit_mul_op(self):
        last = self.last.kind == Kind.NB or self.last.kind == Kind.VAR
        if last and self.peek().kind == Kind.VAR:
            logging.debug(f"implicit_mul_op: {self.peek().txt}")
            return Token(Kind.OP, "*", self.peek().col, "*")
        if self.peek().txt in ("*", "/"):
            return self.next()
        return None

    
    def term(self):
        left = self.power()
        while op := self.implicit_mul_op():
            logging.debug(f"term: {self.peek().txt}")
            # op = self.next()
            right = self.power()
            left = BinaryOp(left, op, right)
        return left


    def power(self):
        left = self.unary()
        if self.peek().txt == "^":
            logging.debug(f"power: {self.peek().txt}")
            self.next()
            right = self.unary()

            if "." in str(self.last):
                fcol = self.last.col
                tcol = self.last.col + len(str(self.last)) - 1
                raise ComputorErr("EXP_04", self.source, tcol=tcol, fcol=fcol)
            
            if self.last.kind == Kind.VAR:
                raise ComputorErr("EXP_03", self.source, col=self.last.col)

            if "^" in str(self.peek()):
                raise ComputorErr("EXP_10", self.source, col=self.peek().col)
            
            left = Power(left, right)
        return left


    def unary(self):
        if self.peek().txt == "-":
            logging.debug(f"unary: {self.peek().txt}")
            self.next()
            return Negate(self.unary())
        if self.peek().txt == "+":
            logging.debug(f"unary: {self.peek().txt}")
            self.next()
            return Neutral(self.unary())
        
        return self.atom()


    def error(self, tok_1, tok_2, tok_3):
        # Opérandes manquants se détectent à partir d'ici
        # Attention il faut utiliser [] au lieu de get pour le dict
        code, fcol, tcol = ERROR_CODES[(tok_1, tok_2, tok_3)]
        if code is not None:
            args = dict()
            args['o1'] = str(tok_2)
            args['o2'] = str(tok_3)
            args['text'] = str(tok_3)
            args['fcol'] = fcol
            args['tcol'] = tcol
            raise ComputorErr(code, self.source, **args)

    def atom(self):

        tkprev = self.prev
        token = self.next()

        if token.kind == Kind.NB:
            logging.debug(f"atom: {token.txt}")
            peek = self.peek()
            if peek.kind == Kind.NB:
                txt = f"'{token.txt}' and '{peek.txt}'"
                src = self.source
                fcol = token.col
                tcol = peek.col
                raise ComputorErr("NBR_01", src, text=txt, fcol=fcol, tcol=tcol)
            atm = Number(from_decimal(token.txt))
            return atm
        
        if token.kind == Kind.VAR:
            logging.debug(f"atom: {token.txt}")
            atm = Variable(token.txt)
            return atm

        self.error(tkprev, self.prev, token)
        self.error(self.prev, token, self.peek())

        # # Opérandes manquants se détectent à partir d'ici
        # # Attention il faut utiliser [] au lieu de get pour le dict
        # code = ERROR_CODES[(tkprev, self.prev, token)]
        # if code is not None:
        #     args = dict()
        #     args['o1'] = str(self.prev)
        #     args['o2'] = str(token)
        #     args['text'] = str(token)
        #     args['fcol'] = self.prev.col
        #     args['tcol'] = token.col
        #     raise ComputorErr(code, self.source, **args)

        # code = ERROR_CODES[(self.prev, token, self.peek())]
        # if code is not None:
        #     args = dict()
        #     args['o1'] = str(token)
        #     args['o2'] = str(self.peek())
        #     args['text'] = str(self.peek())
        #     args['fcol'] = token.col
        #     args['tcol'] = self.peek().col
        #     raise ComputorErr(code, self.source, **args)


    



# def evaluate(node):
#     match node:
#         case Num(value):
#             return value
#         case BinOp("+", left, right):
#             return evaluate(left) + evaluate(right)
#         case BinOp("*", left, right):
#             return evaluate(left) * evaluate(right)


