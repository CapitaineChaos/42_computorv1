import logging

from .errors import ComputorError
from .fraction import Fraction, from_decimal
from .lexer import tokenize
from .reduce import reduce


def parse(source):
    logging.basicConfig(level=logging.DEBUG, format="\033[36mPARSER:\033[0m \033[35m%(message)s\033[0m")
    parser = Parser(source)
    # left, right = parser.eq_sides()
    left, right = parser.parse()
    coefficients, degree = reduce(left, right)
    return coefficients, degree, parser.name

# À 42 on aime le parsing alors on parse à fond....
class Parser:
    def __init__(self, source):
        self.tokens = list(tokenize(source))
        self.position = 1
        self.var = None

    @property
    def name(self):
        return self.var or "X"

    # Élément en cours = Prochain token à traiter
    def tk_peek(self):
        return self.tokens[self.position]

    def tk_peek_rel(self, offset):
        return self.tokens[self.position + offset]
    
    # Retourner le token á traiter ; avancer sur le prochain
    def tk_adv(self):
        token = self.tk_peek()
        self.position += 1
        return token

    # Si le token correspond on avance
    def tk_adv_if(self, *texts):
        if self.tk_peek().text in texts:
            return self.tk_adv()
        return None

    def parse(self):
        nb_eq = 0
        prv = self.tk_adv()
        cur = self.tk_adv()
        while cur.kind != "END" and prv.kind != "END":

            if cur.kind == "EQ":
                nb_eq += 1
                if nb_eq > 1:
                    raise ComputorError(
                        f"multiple equal signs at column {cur.column + 1}",
                        "EQL_01"
                    )
                if prv.count == 0:
                    raise ComputorError(
                        f"missing left side of equation at column {cur.column + 1}",
                        "EQL_02"
                    )
            if cur.text == "END" and cur.count == prv.count:
                raise ComputorError(
                    f"missing right side of equation at column {cur.column + 1}",
                    "EQL_03"
                ) 
            if prv.kind == "NB" and cur.kind == "NB":
                raise ComputorError(
                    f"missing operator between numbers at column {cur.column - 1}",
                    "NBR_01"
                )
            if prv.text == "^" and cur.kind == "OP_D":
                raise ComputorError(
                    f"exponent must not have a sign at column {cur.column + 1}",
                    "EXP_01"
                )
        if nb_eq == 0:
            raise ComputorError(f"missing equal sign", "EQL_02")
        prv = cur
        cur = self.tk_adv()

    # Recup des 2 parties gauche/droite du signe "=", erreur 1 partie vide
    def eq_sides(self):
        if self.tk_peek().text == "=":
            raise ComputorError(f"missing left side of equation", "EQ01")
        left = self.side()
        logging.debug(f"left side: {left}")
        if not self.tk_adv_if("="):
            raise ComputorError(f"missing equal sign at column {self.tk_peek().column + 1}", "EQ02")
        if self.tk_peek().kind == "END":
            raise ComputorError(f"missing right side of equation", "EQ04")
        right = self.side()
        logging.debug(f"right side: {right}")
        if self.tk_peek().kind != "END":
            raise unexpected(self.tk_peek(), "EQ03")
        return left, right

    def side(self):
        terms = [self.signed_term()]
        while self.tk_peek().text in ("+", "-"):
            terms.append(self.signed_term())
        return terms

    def signed_term(self):
        sign = self.tk_adv_if("+", "-")
        if sign and self.tk_peek().text in ("+", "-"):
            raise ComputorError(f"consecutive signs at column {self.tk_peek().column + 1}", "ST01")
        coefficient, degree = self.monomial()
        if sign and sign.text == "-":
            coefficient = -coefficient
        return coefficient, degree

    def monomial(self):
        coeff, deg = self.factor()
        # Tant qu'on est dans un monome on multiplie les coefficients et on additionne les degrés
        while True:
            if self.tk_adv_if("*"):
                sign = self.tk_adv_if("+", "-")
                if sign and not sign.prevsp:
                    raise ComputorError(
                        f"ambigous usage of operator at column {sign.column}, '{sign.text}' ",
                        "TE01"
                    )
            # Pas de nombre suivi d'un nombre sans op
            elif self.tk_peek().kind == "NUMBER" and self.tokens[self.position - 1].kind == "NUMBER":
                raise ComputorError(
                    f"missing operator between numbers at column {self.tk_peek().column + 1}",
                    "TE02"
                )
            elif self.tk_peek().kind in ("NUMBER", "VAR"):
                sign = None
            # Au final on retombe sur OP EQUAL ou END et on sort proprement
            else:
                logging.debug(f"term: {coeff}, {deg}")
                return coeff, deg
    
            factor_coefficient, factor_degree = self.factor()
            if sign and sign.text == "-":
                factor_coefficient = -factor_coefficient

            coeff = coeff * factor_coefficient
            deg = deg + factor_degree

    def exponent_1(self):
        ex = self.tk_peek_rel(-1)
        token = self.tk_peek()
        if ex.kind == "START":
            raise ComputorError(f"missing base for exponent at column {token.column + 1}", "EX05")
        if ex.kind in ("OP", "EQUAL"):
            raise ComputorError(f"exponent cannot be applied to operator at column {ex.column + 1}", "EX06")

    def factor(self):
        if self.tk_peek().text == "^":
            self.exponent_1()
        token = self.tk_adv()
        if token.kind in "END" or token.text in ("*", "/", "="):
            raise ComputorError(f"factor expected at column {token.column + 1}", "FA01")
        exponent = self.exponent_2() if self.tk_adv_if("^") else None
        if token.kind not in ("NUMBER", "VAR"):
            raise unexpected(token, "FA02")
        if token.kind == "NUMBER":
            value = from_decimal(token.text)
            return (value if exponent is None else value**exponent), 0
        if self.var is None:
            self.var = token.text
        elif token.text != self.var:
            raise ComputorError(f"unknown already defined, illegal name '{token.text}'", "FA03")
        return Fraction(1), 1 if exponent is None else exponent

    def exponent_2(self):
        token = self.tk_adv()
        if token.text == "^":
            raise ComputorError(f"exponent error: missing number at column {token.column + 1}", "EX01")
        if token.text in ("+", "-"):
            raise ComputorError(f"exponent must not have a sign at column {token.column + 1}", "EX02")
        if token.kind != "NUMBER" or "." in token.text:
            raise ComputorError(f"exponent must be an integer at column {token.column + 1}", "EX03")
        if self.tk_peek().text == "^":
            raise ComputorError(f"chained exponent is ambiguous at column {self.tk_peek().column + 1}", "EX04")
        return int(token.text)


def unexpected(token, code=None):
    if token.kind == "END":
        return ComputorError(f"something is missing in the equation", code)
    return ComputorError(f"unexpected '{token.text}' at column {token.column + 1}", code)
