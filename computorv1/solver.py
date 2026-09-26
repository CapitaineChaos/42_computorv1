"""Degree 0 to 2 solving, with exact roots."""

from collections import namedtuple

from .rational import ONE, ZERO, Rational, gcd, square_free

IDENTITY = "identity"
IMPOSSIBLE = "impossible"
LINEAR = "linear"
DOUBLE = "double"
REAL = "real"
COMPLEX = "complex"
HIGH = "high"

Solution = namedtuple("Solution", "kind degree discriminant roots steps")


class Root:
    """a + b*sqrt(r), imaginary when the discriminant was negative."""

    __slots__ = ("a", "b", "r", "imaginary")

    def __init__(self, a, b=ZERO, r=1, imaginary=False):
        if b.is_zero:
            r, imaginary = 1, False
        elif r == 1 and not imaginary:
            a, b = a + b, ZERO
        self.a, self.b, self.r, self.imaginary = a, b, r, imaginary

    @classmethod
    def from_delta(cls, a, scale, delta):
        """a + scale*sqrt(delta), delta of any sign. sqrt(p/q) = sqrt(p*q)/q."""
        if delta.is_zero:
            return cls(a)
        magnitude = abs(delta)
        square, rest = square_free(magnitude.num * magnitude.den)
        return cls(a, scale * Rational(square, magnitude.den), rest, delta.sign < 0)

    def exact(self):
        if self.b.is_zero:
            return str(self.a)
        if self.imaginary:
            return self._algebraic()
        return self._radical()

    def _radical(self):
        """(A + B*sqrt(r)) / d."""
        d = self.a.den * self.b.den // gcd(self.a.den, self.b.den)
        a, b = self.a.num * (d // self.a.den), self.b.num * (d // self.b.den)
        common = gcd(gcd(a, b), d)
        a, b, d = a // common, b // common, d // common
        root = ("" if abs(b) == 1 else str(abs(b))) + "√%d" % self.r
        if a == 0:
            body = ("-" if b < 0 else "") + root
            return body if d == 1 else "%s / %d" % (body, d)
        body = "%d %s %s" % (a, "-" if b < 0 else "+", root)
        return body if d == 1 else "(%s) / %d" % (body, d)

    def _algebraic(self):
        """a + b*i, the form the subject prints."""
        magnitude = abs(self.b)
        head = "" if magnitude.num == 1 else str(magnitude.num)
        root = "" if self.r == 1 else "√%d" % self.r
        term = head + "i" + root + ("" if magnitude.den == 1 else "/%d" % magnitude.den)
        if self.a.is_zero:
            return ("-" if self.b.sign < 0 else "") + term
        return "%s %s %s" % (self.a, "-" if self.b.sign < 0 else "+", term)

    def decimal(self, digits):
        if self.b.is_zero:
            return self.a.decimal(digits)
        offset = self.b * Rational(self.r).sqrt(digits + 4)
        if not self.imaginary:
            return (self.a + offset).decimal(digits)
        return "%s %s %si" % (
            self.a.decimal(digits),
            "-" if offset.sign < 0 else "+",
            abs(offset).decimal(digits),
        )


def solve(poly, variable="X", digits=6):
    degree = len(poly) - 1
    if degree < 0:
        return Solution(IDENTITY, 0, None, (), ())
    if degree == 0:
        return Solution(IMPOSSIBLE, 0, None, (), ())
    if degree == 1:
        return _linear(poly, variable, digits)
    if degree == 2:
        return _quadratic(poly, variable, digits)
    return Solution(HIGH, degree, None, (), ())


def _linear(poly, variable, digits):
    b, a = poly
    root = -b / a
    steps = (
        "a = %s, b = %s" % (a.text(digits), b.text(digits)),
        "%s = -b / a = %s / %s = %s"
        % (variable, _term(-b, digits), _term(a, digits), root.text(digits)),
    )
    return Solution(LINEAR, 1, None, (Root(root),), steps)


def _quadratic(poly, variable, digits):
    c, b, a = poly
    delta = b * b - 4 * a * c
    vertex = -b / (2 * a)
    steps = [
        "a = %s, b = %s, c = %s" % (a.text(digits), b.text(digits), c.text(digits)),
        "delta = b^2 - 4ac = %s^2 - 4 * %s * %s = %s"
        % (_term(b, digits), _term(a, digits), _term(c, digits), delta.text(digits)),
    ]

    if delta.is_zero:
        steps.append("%s = -b / 2a = %s" % (variable, vertex.text(digits)))
        return Solution(DOUBLE, 2, delta, (Root(vertex),), tuple(steps))

    sqrt_delta = Root.from_delta(ZERO, ONE, delta)
    steps.append("sqrt(delta) = %s" % sqrt_delta.exact())
    steps.append(
        "%s = (-b +/- sqrt(delta)) / 2a = (%s +/- %s) / %s"
        % (variable, _term(-b, digits), sqrt_delta.exact(), _term(2 * a, digits))
    )
    # Positive coefficient first: subject prints the greater root first.
    spread = abs(ONE / (2 * a))
    roots = (Root.from_delta(vertex, spread, delta), Root.from_delta(vertex, -spread, delta))
    return Solution(REAL if delta.sign > 0 else COMPLEX, 2, delta, roots, tuple(steps))


def _term(value, digits):
    text = value.text(digits)
    return "(%s)" % text if value.sign < 0 else text
