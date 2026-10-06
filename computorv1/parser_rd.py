from .errors import ComputorError
from .fraction import Fraction, from_decimal
from .lexer import tokenize
from .reduce import reduce


def parse(source):
    parser = Parser(source)
    left, right = parser.equation()
    coefficients, degree = reduce(left, right)
    return coefficients, degree, parser.name


class Parser:
    def __init__(self, source):
        self.tokens = list(tokenize(source))
        self.position = 0
        self.var = None

    @property
    def name(self):
        return self.var or "X"

    def peek(self):
        return self.tokens[self.position]

    def advance(self):
        token = self.peek()
        self.position += 1
        return token

    def accept(self, *texts):
        if self.peek().text in texts:
            return self.advance()
        return None

    def equation(self):
        left = self.side()
        if not self.accept("="):
            raise unexpected(self.peek())
        right = self.side()
        if self.peek().kind != "END":
            raise unexpected(self.peek())
        return left, right

    def side(self):
        terms = [self.signed_term()]
        while self.peek().text in ("+", "-"):
            terms.append(self.signed_term())
        return terms

    def signed_term(self):
        sign = self.accept("+", "-")
        if sign and self.peek().text in ("+", "-"):
            raise ComputorError(f"consecutive signs at column {self.peek().column + 1}")
        coefficient, degree = self.term()
        if sign and sign.text == "-":
            coefficient = -coefficient
        return coefficient, degree

    def term(self):
        coefficient, degree = self.factor()
        while True:
            if self.accept("*"):
                sign = self.accept("+", "-")
            elif self.peek().kind == "NUMBER" and self.tokens[self.position - 1].kind == "NUMBER":
                raise ComputorError(
                    f"missing operator between numbers at column {self.peek().column + 1}"
                )
            elif self.peek().kind in ("NUMBER", "VAR"):
                sign = None
            else:
                return coefficient, degree
            factor_coefficient, factor_degree = self.factor()
            if sign and sign.text == "-":
                factor_coefficient = -factor_coefficient
            coefficient = coefficient * factor_coefficient
            degree = degree + factor_degree

    def factor(self):
        token = self.advance()
        if token.kind not in ("NUMBER", "VAR"):
            raise unexpected(token)
        exponent = self.exponent() if self.accept("^") else None
        if token.kind == "NUMBER":
            value = from_decimal(token.text)
            return (value if exponent is None else value**exponent), 0
        if self.var is None:
            self.var = token.text
        elif token.text != self.var:
            raise ComputorError(f"second unknown '{token.text}'")
        return Fraction(1), 1 if exponent is None else exponent

    def exponent(self):
        token = self.advance()
        if token.text == "^":
            raise ComputorError(f"exponent error: missing number at column {token.column + 1}")
        if token.text in ("+", "-"):
            raise ComputorError(f"exponent must not have a sign at column {token.column + 1}")
        if token.kind != "NUMBER" or "." in token.text:
            raise ComputorError(f"exponent must be an integer at column {token.column + 1}")
        if self.peek().text == "^":
            raise ComputorError(f"chained exponent is ambiguous at column {self.peek().column + 1}")
        return int(token.text)


def unexpected(token):
    if token.kind == "END":
        return ComputorError("unexpected end of equation")
    return ComputorError(f"unexpected '{token.text}' at column {token.column + 1}")
