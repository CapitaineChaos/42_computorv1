"""Free form equation parsing.

    equation := expr '=' expr
    expr     := term (('+' | '-') term)*
    term     := unary (('*' | '/')? unary)*
    unary    := ('+' | '-') unary | power
    power    := atom ('^' integer)?
    atom     := number | variable | '(' expr ')'

Juxtaposition means multiplication: "2x", "x(x + 1)", "(x - 1)(x + 1)".
Polynomials are lists of Rational indexed by degree, trailing zeros dropped.
"""

import re
from itertools import zip_longest

from .rational import ONE, ZERO, Rational

_TOKEN = re.compile(r"(\d+(?:\.\d+)?|\.\d+)|([A-Za-z]\w*)|([-+*/^()=])|(\S)", re.ASCII)
_NAMES = {"num": "a number", "var": "a variable", "end": "end of input"}


class ComputorError(Exception):
    """Input error, `position` being an index in the source."""

    def __init__(self, message, position):
        super().__init__(message)
        self.message = message
        self.position = position


def tokenize(source):
    tokens = []
    for match in _TOKEN.finditer(source):
        number, name, symbol, unknown = match.groups()
        if number:
            tokens.append(("num", Rational.parse(number), match.start()))
        elif name:
            if len(name) > 1:
                raise ComputorError(
                    "unknown name '%s', a variable is a single letter" % name, match.start()
                )
            tokens.append(("var", name.upper(), match.start()))
        elif symbol:
            tokens.append((symbol, None, match.start()))
        else:
            raise ComputorError("unexpected character '%s'" % unknown, match.start())
    tokens.append(("end", None, len(source)))
    return tokens


def add(left, right):
    return trim([a + b for a, b in zip_longest(left, right, fillvalue=ZERO)])


def sub(left, right):
    return trim([a - b for a, b in zip_longest(left, right, fillvalue=ZERO)])


def mul(left, right):
    if not left or not right:
        return []
    out = [ZERO] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] = out[i + j] + a * b
    return trim(out)


def trim(poly):
    while poly and poly[-1].is_zero:
        poly.pop()
    return poly


class _Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        self.variable = None

    @property
    def token(self):
        return self.tokens[self.index]

    def eat(self):
        self.index += 1
        return self.tokens[self.index - 1]

    def equation(self):
        left = self.expr()
        kind, _, position = self.token
        if kind != "=":
            raise ComputorError(
                "missing '=', an equation has two sides"
                if kind == "end"
                else "expected '=' but found %s" % _name(self.token),
                position,
            )
        self.eat()
        right = self.expr()
        if self.token[0] != "end":
            raise ComputorError("unexpected %s" % _name(self.token), self.token[2])
        return left, right, self.variable or "X"

    def expr(self):
        result = self.term()
        while self.token[0] in "+-":
            result = add(result, self.term()) if self.eat()[0] == "+" else sub(result, self.term())
        return result

    def term(self):
        result = self.unary()
        while True:
            kind, _, position = self.token
            if kind in "*/":
                self.eat()
                right = self.unary()
                result = mul(result, right) if kind == "*" else self.div(result, right, position)
            elif kind in ("num", "var", "("):
                result = mul(result, self.unary())
            else:
                return result

    def div(self, left, right, position):
        if not right:
            raise ComputorError("division by zero", position)
        if len(right) > 1:
            raise ComputorError("division by a variable is not a polynomial", position)
        return trim([c / right[0] for c in left])

    def unary(self):
        if self.token[0] in "+-":
            return self.unary() if self.eat()[0] == "+" else [-c for c in self.unary()]
        return self.power()

    def power(self):
        base = self.atom()
        if self.token[0] != "^":
            return base
        caret = self.eat()[2]
        result = [ONE]
        for _ in range(self.exponent(caret)):
            result = mul(result, base)
        if self.token[0] == "^":
            raise ComputorError("chained '^' is ambiguous, use parentheses", self.token[2])
        return result

    def exponent(self, caret):
        negative = False
        while self.token[0] in "+-":
            negative ^= self.eat()[0] == "-"
        kind, value, position = self.token
        if kind != "num":
            raise ComputorError("expected an integer exponent after '^'", position)
        self.eat()
        if value.den != 1:
            raise ComputorError("exponent %s is not an integer" % value, position)
        if negative and not value.is_zero:
            raise ComputorError("negative exponent is not a polynomial", caret)
        if value.num > 1000:
            raise ComputorError("exponent %s is out of range" % value, position)
        return value.num

    def atom(self):
        kind, value, position = self.token
        if kind == "num":
            self.eat()
            return trim([value])
        if kind == "var":
            self.eat()
            if self.variable is None:
                self.variable = value
            elif self.variable != value:
                raise ComputorError(
                    "two unknowns, '%s' and '%s'" % (self.variable, value), position
                )
            return [ZERO, ONE]
        if kind == "(":
            self.eat()
            inner = self.expr()
            if self.token[0] != ")":
                raise ComputorError("unclosed '(', expected ')'", self.token[2])
            self.eat()
            return inner
        raise ComputorError("expected an operand but found %s" % _name(self.token), position)


def _name(token):
    return _NAMES.get(token[0], "'%s'" % token[0])


def parse(source):
    """source -> (left side, right side, variable name)"""
    return _Parser(tokenize(source)).equation()
