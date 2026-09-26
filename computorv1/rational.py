"""Exact rational arithmetic. The subject bans math library calls."""


def gcd(a, b):
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def isqrt(n):
    """Integer square root, Heron's iteration."""
    if n < 2:
        return n
    x = 1 << ((n.bit_length() + 1) // 2)
    while True:
        y = (x + n // x) // 2
        if y >= x:
            return x
        x = y


def square_free(n):
    """n -> (k, r) with n == k * k * r and r square free."""
    k, r, f = 1, n, 2
    while f * f <= r:
        while r % (f * f) == 0:
            r //= f * f
            k *= f
        f += 1 if f == 2 else 2
    return k, r


class Rational:
    __slots__ = ("num", "den")

    def __init__(self, num=0, den=1):
        if den == 0:
            raise ZeroDivisionError("division by zero")
        if den < 0:
            num, den = -num, -den
        d = gcd(num, den) or 1
        self.num, self.den = num // d, den // d

    @classmethod
    def parse(cls, text):
        """Integer or decimal literal, without sign."""
        whole, _, frac = text.partition(".")
        return cls(int(whole + frac), 10 ** len(frac))

    @property
    def is_zero(self):
        return self.num == 0

    @property
    def sign(self):
        return (self.num > 0) - (self.num < 0)

    def __add__(self, other):
        other = _rational(other)
        return Rational(self.num * other.den + other.num * self.den, self.den * other.den)

    __radd__ = __add__

    def __sub__(self, other):
        other = _rational(other)
        return Rational(self.num * other.den - other.num * self.den, self.den * other.den)

    def __rsub__(self, other):
        return _rational(other) - self

    def __mul__(self, other):
        other = _rational(other)
        return Rational(self.num * other.num, self.den * other.den)

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = _rational(other)
        return Rational(self.num * other.den, self.den * other.num)

    def __neg__(self):
        return Rational(-self.num, self.den)

    def __abs__(self):
        return Rational(abs(self.num), self.den)

    def __eq__(self, other):
        other = _rational(other)
        return self.num == other.num and self.den == other.den

    def __hash__(self):
        return hash((self.num, self.den))

    def __repr__(self):
        return "Rational(%d, %d)" % (self.num, self.den)

    def __str__(self):
        return str(self.num) if self.den == 1 else "%d/%d" % (self.num, self.den)

    def text(self, digits):
        """Decimal when it terminates, irreducible fraction otherwise."""
        den = self.den
        for prime in (2, 5):
            while den % prime == 0:
                den //= prime
        return self.decimal(digits) if den == 1 else str(self)

    def decimal(self, digits):
        """Nearest decimal writing, trailing zeros dropped."""
        scaled = self.num * 10**digits
        quotient, rest = divmod(abs(scaled), self.den)
        if 2 * rest >= self.den:
            quotient += 1
        text = str(quotient).rjust(digits + 1, "0")
        if digits:
            whole, frac = text[:-digits], text[-digits:].rstrip("0")
            text = whole + ("." + frac if frac else "")
        return ("-" if self.num < 0 and quotient else "") + text

    def sqrt(self, digits):
        """Square root rounded to `digits` decimals: sqrt(p/q) = sqrt(p*q)/q."""
        guard = 10 ** (digits + 2)
        truncated = isqrt(self.num * self.den * guard * guard) // self.den
        quotient, rest = divmod(truncated * 10**digits, guard)
        return Rational(quotient + (2 * rest >= guard), 10**digits)


def _rational(value):
    return value if isinstance(value, Rational) else Rational(value)


ZERO = Rational(0)
ONE = Rational(1)
