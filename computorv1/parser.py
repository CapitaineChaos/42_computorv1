import logging

from .errors import ComputorError
from .fraction import Fraction, from_decimal
from .lexer import tokenize, Token
from .reduce import reduce


def parse(source):
    logging.basicConfig(level=logging.DEBUG, format="\033[36mPARSER:\033[0m \033[35m%(message)s\033[0m")
    parser = Parser(source)
    # left, right = parser.eq_sides()
    parser.parse()
    print("-------------------------------------------------")
    # coefficients, degree = reduce(left, right)
    # return coefficients, degree, parser.name


# À 42 on aime le parsing alors on parse à fond....
class Parser:
    def __init__(self, source):
        self.tokens = list(tokenize(source))
        self.position = 1
        self.var = None
        self.monomials = []

    @property
    def name(self):
        return self.var or "X"

    def get_next_token(self):
        token = self.tokens[self.position]
        self.position += 1
        return token

    def parse(self):
        nb_eq = 0
        prv = self.get_next_token()
        cur = prv
        monomial = []
        while cur.kind != "END" and prv.kind != "END":
            cur = self.get_next_token()
            ccol = cur.column
            pcol = prv.column
            if cur.kind == "END" and prv.kind == "EQ":
                raise ComputorError("EQL_03", col=ccol + 1)
            
            if prv.kind == "NB" and cur.kind == "NB":
                raise ComputorError("NBR_01", col=ccol - 1)
            
            if prv.text == "^":
                if cur.kind != "NB" and cur.kind != "VAR" and cur.text != "-":
                    raise ComputorError("EXP_01", col=pcol + 1)

            if prv.text == "*":
                if cur.kind != "NB" and cur.kind != "VAR" and cur.text != "-":
                    raise ComputorError("MUL_01", col=pcol + 1)

            if prv.kind == "OP_D" and cur.kind == "OP_D" and not cur.prevsp:
                if prv.text != "+" or cur.text != "-":
                    raise ComputorError("SGN_01", col=ccol + 1)

            side = 1 if nb_eq == 0 else -1

            if prv.kind == "EQ":
                if nb_eq > 0:
                    raise ComputorError("EQL_01", col=ccol)
                if prv.pos == 1:
                    raise ComputorError("EQL_02", col=pcol)
                nb_eq += 1

            if (cur.kind == "END" or cur.kind == "EQ"
                or (cur.kind == "OP_D" and prv.kind != "OP_B")):
                logging.debug(f"prv 1 : {prv}")
                monomial.append(prv)
                monomial.append(side)
                self.monomials.append(monomial)
                logging.debug(f"monomial: {monomial}")
                monomial = []
            elif prv.kind != "EQ":
                logging.debug(f"prv 2 : {prv}")
                monomial.append(prv)

            prv = cur

        if nb_eq == 0:
            raise ComputorError("EQL_04")
        
        
