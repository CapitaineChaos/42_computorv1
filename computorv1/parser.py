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
        self.var = None
        self.prev = None

    def peek(self) -> Token:
        return self.tkns[-1] if self.tkns else self.last

    def next(self):
        self.prev = self.last
        self.last = self.tkns.pop()
        return self.last

    def equation(self):
        token = self.next()

        if token is None or not token.kind:
            raise ComputorErr("ERR_01", self.source)
        if token.kind != Kind.ST:
            raise ComputorErr("ERR_01", self.source)

        if self.peek().kind == Kind.EQ:
            raise ComputorErr("EQL_01", self.source)
        
        left = self.expr()

        if self.peek().kind != Kind.EQ:
            raise ComputorErr("EQL_04", self.source)

        self.next()

        if self.peek().kind == Kind.ND:
            raise ComputorErr("EQL_02", self.source)
        
        right = self.expr()

        if self.peek().kind == Kind.EQ:
            fcol = tcol = self.peek().col
            raise ComputorErr("EQL_03", self.source, fcol=fcol, tcol=tcol)
        
        # En principe on atteint jamais cette erreur mais on sait jamais
        if self.peek().kind != Kind.ND:
            raise ComputorErr("ERR_02", self.source)
        
        return Equation(left, right)


    def expr(self):
        left = self.term()
        while self.peek().txt in ("+", "-"):
            logging.debug(f"expr: {self.peek().txt}")
            op = self.next()
            self.error("e", None, None, self.peek())
            right = self.term()
            left = BinaryOp(left, op, right)
        return left
    

    def term(self):
        left = self.power()
        while self.peek().txt in ("*", "/"):
            logging.debug(f"term: {self.peek().txt}")
            op = self.next()
            self.error("t", None, None, self.peek())
            right = self.power()
            left = BinaryOp(left, op, right)
        return left

    def power(self):
        left = self.unary()
        if self.peek().txt == "^":
            logging.debug(f"power: {self.peek().txt}")
            self.next()
            self.error("p", None, self.last, self.peek())

            right = self.unary()

            if "." in str(self.last):
                fcol = self.last.col
                tcol = self.last.col + len(str(self.last)) - 1
                raise ComputorErr("EXP_04", self.source, tcol=tcol, fcol=fcol)
            
            if self.last.kind == Kind.VR:
                raise ComputorErr("EXP_03", self.source, col=self.last.col)

            self.error("p", None, None, self.peek())
            
            left = Power(left, right)
        return left


    def unary(self):
        if self.peek().txt == "-":
            logging.debug(f"unary: {self.peek().txt}")
            self.next()
            self.error("u", None, None, self.peek())
            return Negate(self.unary())
        if self.peek().txt == "+":
            logging.debug(f"unary: {self.peek().txt}")
            self.next()
            self.error("u", None, None, self.peek())
            return Neutral(self.unary())
        
        return self.atom()


    def error(self, type, tok_1, tok_2, tok_3):
        # Opérandes manquants se détectent à partir d'ici
        # Attention il faut utiliser [] au lieu de get pour le dict
        ret = ERROR_CODES[(type, tok_1, tok_2, tok_3)]

        if ret is None:
            return

        code, (fcol, tcol) = ret

        if code is not None:
            args = dict()
            args['o1'] = str(tok_2)
            args['o2'] = str(tok_3)
            args['text'] = str(tok_3)
            args['fcol'] = fcol
            args['tcol'] = tcol
            raise ComputorErr(code, self.source, **args)

    def add_mul_token(self, tk):
        if tk.kind == Kind.VR:
            logging.debug(f"implicit mul: {tk.txt}")
            self.tkns.append(Token(Kind.OP, "*", tk.col, False))

    def atom(self):

        tkprev = self.prev
        token = self.next()

        if token.txt == ".":
            self.error("d", None, None, token)
        self.error("a", None, None, token)

        if token.kind == Kind.NB:
            logging.debug(f"atom: {token.txt}")
            self.error("a", None, token, self.peek())
            atm = Number(from_decimal(token.txt))
            self.add_mul_token(self.peek())
            return atm
        
        if token.kind == Kind.VR:
            logging.debug(f"atom: {token.txt}")
            if not self.var:
                self.var = self.last.txt
            elif self.var != self.last.txt:
                self.error("v", None, self.last, token)
            
            self.error("a", None, token, self.peek())
            atm = Variable(token.txt)
            self.add_mul_token(self.peek())
            return atm

        self.error("a", tkprev, self.prev, token)
        self.error("a", self.prev, token, self.peek())

        raise ComputorErr("UNK_00", col=token.col)




# def evaluate(node):
#     match node:
#         case Num(value):
#             return value
#         case BinOp("+", left, right):
#             return evaluate(left) + evaluate(right)
#         case BinOp("*", left, right):
#             return evaluate(left) * evaluate(right)


