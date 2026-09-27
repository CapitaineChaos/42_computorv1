import operator
import re

# Nombres rationnels exacts : copie réduite de fractions.Fraction, CPython 3.13.0.
# Chaque partie donne les lignes copiées. Différences avec l'original :
# - math.gcd est remplacé par gcd ci-dessous, copié de Wikipedia ;
# - numbers.Rational, la classe abstraite des rationnels, int compris, devient
#   (Fraction, int) : en hériter obligerait à écrire une vingtaine de méthodes inutiles ici ;
# - docstrings retirées, ainsi que les branches pour les types que computor ne donne
#   jamais : float en entrée du constructeur et des comparaisons, complex, Decimal.


# code: https://en.wikipedia.org/w/index.php?title=Euclidean_algorithm&oldid=1375335874#Implementations
# La dernière ligne est « return abs(a) », comme l'article le demande quand a ou b peut
# être négatif.
def gcd(a, b):
    while b != 0:
        t = b
        b = a % b
        a = t
    return abs(a)


# code: https://github.com/python/cpython/blob/v3.13.0/Lib/fractions.py#L57-L69
_RATIONAL_FORMAT = re.compile(
    r"""
    \A\s*                                  # optional whitespace at the start,
    (?P<sign>[-+]?)                        # an optional sign, then
    (?=\d|\.\d)                            # lookahead for digit or .digit
    (?P<num>\d*|\d+(_\d+)*)                # numerator (possibly empty)
    (?:                                    # followed by
       (?:\s*/\s*(?P<denom>\d+(_\d+)*))?   # an optional denominator
    |                                      # or
       (?:\.(?P<decimal>\d*|\d+(_\d+)*))?  # an optional fractional part
       (?:E(?P<exp>[-+]?\d+(_\d+)*))?      # and optional exponent
    )
    \s*\Z                                  # and optional whitespace to finish
""",
    re.VERBOSE | re.IGNORECASE,
)


class Fraction:
    # code: https://github.com/python/cpython/blob/v3.13.0/Lib/fractions.py#L200
    __slots__ = ("_numerator", "_denominator")

    # code: https://github.com/python/cpython/blob/v3.13.0/Lib/fractions.py#L202-L306
    # We're immutable, so use __new__ not __init__
    def __new__(cls, numerator=0, denominator=None):
        self = super(Fraction, cls).__new__(cls)

        if denominator is None:
            if type(numerator) is int:
                self._numerator = numerator
                self._denominator = 1
                return self

            elif isinstance(numerator, Fraction):
                self._numerator = numerator.numerator
                self._denominator = numerator.denominator
                return self

            elif isinstance(numerator, str):
                # Handle construction from strings.
                m = _RATIONAL_FORMAT.match(numerator)
                if m is None:
                    raise ValueError("Invalid literal for Fraction: %r" % numerator)
                numerator = int(m.group("num") or "0")
                denom = m.group("denom")
                if denom:
                    denominator = int(denom)
                else:
                    denominator = 1
                    decimal = m.group("decimal")
                    if decimal:
                        decimal = decimal.replace("_", "")
                        scale = 10 ** len(decimal)
                        numerator = numerator * scale + int(decimal)
                        denominator *= scale
                    exp = m.group("exp")
                    if exp:
                        exp = int(exp)
                        if exp >= 0:
                            numerator *= 10**exp
                        else:
                            denominator *= 10**-exp
                if m.group("sign") == "-":
                    numerator = -numerator

            else:
                raise TypeError("argument should be a string or a Rational instance")

        elif type(numerator) is int is type(denominator):
            pass  # *very* normal case

        else:
            raise TypeError("both arguments should be Rational instances")

        if denominator == 0:
            raise ZeroDivisionError("Fraction(%s, 0)" % numerator)
        g = gcd(numerator, denominator)
        if denominator < 0:
            g = -g
        numerator //= g
        denominator //= g
        self._numerator = numerator
        self._denominator = denominator
        return self

    # code: https://github.com/python/cpython/blob/v3.13.0/Lib/fractions.py#L334-L344
    @classmethod
    def _from_coprime_ints(cls, numerator, denominator, /):
        obj = super(Fraction, cls).__new__(cls)
        obj._numerator = numerator
        obj._denominator = denominator
        return obj

    # code: https://github.com/python/cpython/blob/v3.13.0/Lib/fractions.py#L414-L420
    @property
    def numerator(a):
        return a._numerator

    @property
    def denominator(a):
        return a._denominator

    # code: https://github.com/python/cpython/blob/v3.13.0/Lib/fractions.py#L422-L425
    def __repr__(self):
        return "%s(%s, %s)" % (self.__class__.__name__, self._numerator, self._denominator)

    # code: https://github.com/python/cpython/blob/v3.13.0/Lib/fractions.py#L582-L690
    # Opération entre une Fraction et un int : l'int devient une Fraction. Entre une
    # Fraction et un float : la Fraction devient un float, le résultat est un float.
    def _operator_fallbacks(monomorphic_operator, fallback_operator):
        def forward(a, b):
            if isinstance(b, Fraction):
                return monomorphic_operator(a, b)
            elif isinstance(b, int):
                return monomorphic_operator(a, Fraction(b))
            elif isinstance(b, float):
                return fallback_operator(float(a), b)
            else:
                return NotImplemented

        forward.__name__ = "__" + fallback_operator.__name__ + "__"
        forward.__doc__ = monomorphic_operator.__doc__

        def reverse(b, a):
            if isinstance(a, int):
                return monomorphic_operator(Fraction(a), b)
            elif isinstance(a, float):
                return fallback_operator(float(a), float(b))
            else:
                return NotImplemented

        reverse.__name__ = "__r" + fallback_operator.__name__ + "__"
        reverse.__doc__ = monomorphic_operator.__doc__

        return forward, reverse

    # code: https://github.com/python/cpython/blob/v3.13.0/Lib/fractions.py#L692-L774
    # La justification de ces calculs est en commentaire dans l'original, lignes 692 à 758.
    def _add(a, b):
        na, da = a._numerator, a._denominator
        nb, db = b._numerator, b._denominator
        g = gcd(da, db)
        if g == 1:
            return Fraction._from_coprime_ints(na * db + da * nb, da * db)
        s = da // g
        t = na * (db // g) + nb * s
        g2 = gcd(t, g)
        if g2 == 1:
            return Fraction._from_coprime_ints(t, s * db)
        return Fraction._from_coprime_ints(t // g2, s * (db // g2))

    __add__, __radd__ = _operator_fallbacks(_add, operator.add)

    # code: https://github.com/python/cpython/blob/v3.13.0/Lib/fractions.py#L776-L790
    def _sub(a, b):
        na, da = a._numerator, a._denominator
        nb, db = b._numerator, b._denominator
        g = gcd(da, db)
        if g == 1:
            return Fraction._from_coprime_ints(na * db - da * nb, da * db)
        s = da // g
        t = na * (db // g) - nb * s
        g2 = gcd(t, g)
        if g2 == 1:
            return Fraction._from_coprime_ints(t, s * db)
        return Fraction._from_coprime_ints(t // g2, s * (db // g2))

    __sub__, __rsub__ = _operator_fallbacks(_sub, operator.sub)

    # code: https://github.com/python/cpython/blob/v3.13.0/Lib/fractions.py#L792-L806
    def _mul(a, b):
        na, da = a._numerator, a._denominator
        nb, db = b._numerator, b._denominator
        g1 = gcd(na, db)
        if g1 > 1:
            na //= g1
            db //= g1
        g2 = gcd(nb, da)
        if g2 > 1:
            nb //= g2
            da //= g2
        return Fraction._from_coprime_ints(na * nb, db * da)

    __mul__, __rmul__ = _operator_fallbacks(_mul, operator.mul)

    # code: https://github.com/python/cpython/blob/v3.13.0/Lib/fractions.py#L808-L828
    def _div(a, b):
        # Same as _mul(), with inversed b.
        nb, db = b._numerator, b._denominator
        if nb == 0:
            raise ZeroDivisionError("Fraction(%s, 0)" % db)
        na, da = a._numerator, a._denominator
        g1 = gcd(na, nb)
        if g1 > 1:
            na //= g1
            nb //= g1
        g2 = gcd(db, da)
        if g2 > 1:
            da //= g2
            db //= g2
        n, d = na * db, nb * da
        if d < 0:
            n, d = -n, -d
        return Fraction._from_coprime_ints(n, d)

    __truediv__, __rtruediv__ = _operator_fallbacks(_div, operator.truediv)

    # code: https://github.com/python/cpython/blob/v3.13.0/Lib/fractions.py#L851-L881
    # Exposant entier seulement : la branche des exposants non entiers est retirée.
    def __pow__(a, b):
        if isinstance(b, (Fraction, int)):
            if b.denominator == 1:
                power = b.numerator
                if power >= 0:
                    return Fraction._from_coprime_ints(a._numerator**power, a._denominator**power)
                elif a._numerator > 0:
                    return Fraction._from_coprime_ints(a._denominator**-power, a._numerator**-power)
                elif a._numerator == 0:
                    raise ZeroDivisionError("Fraction(%s, 0)" % a._denominator**-power)
                else:
                    return Fraction._from_coprime_ints(
                        (-a._denominator) ** -power, (-a._numerator) ** -power
                    )
        return NotImplemented

    # code: https://github.com/python/cpython/blob/v3.13.0/Lib/fractions.py#L901-L907
    def __neg__(a):
        return Fraction._from_coprime_ints(-a._numerator, a._denominator)

    def __abs__(a):
        return Fraction._from_coprime_ints(abs(a._numerator), a._denominator)

    # code: https://github.com/python/cpython/blob/v3.13.0/Lib/numbers.py#L308-L316
    # Division des deux entiers, sans les convertir en float d'abord : pas de dépassement
    # quand numérateur et dénominateur sont trop grands pour un float, si leur rapport ne
    # l'est pas.
    def __float__(self):
        return int(self.numerator) / int(self.denominator)

    # code: https://github.com/python/cpython/blob/v3.13.0/Lib/fractions.py#L962-L981
    def __eq__(a, b):
        if type(b) is int:
            return a._numerator == b and a._denominator == 1
        if isinstance(b, Fraction):
            return a._numerator == b.numerator and a._denominator == b.denominator
        else:
            # Since a doesn't know how to compare with b, let's give b
            # a chance to compare itself with a.
            return NotImplemented

    # code: https://github.com/python/cpython/blob/v3.13.0/Lib/fractions.py#L983-L1019
    # a/b < c/d revient à a*d < b*c, les dénominateurs étant positifs.
    def _richcmp(self, other, op):
        # convert other to a Rational instance where reasonable.
        if isinstance(other, (Fraction, int)):
            return op(self._numerator * other.denominator, self._denominator * other.numerator)
        else:
            return NotImplemented

    def __lt__(a, b):
        return a._richcmp(b, operator.lt)

    def __gt__(a, b):
        return a._richcmp(b, operator.gt)

    def __le__(a, b):
        return a._richcmp(b, operator.le)

    def __ge__(a, b):
        return a._richcmp(b, operator.ge)
