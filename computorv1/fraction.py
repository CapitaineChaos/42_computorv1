# Nombre rationnel exact a/b, a et b entiers. Chaque opération applique la formule de la
# section du même nom de l'article Rational_number, révision 1357066562.
# Avec un float, le résultat est un float : c'est le cas des solutions calculées avec une
# racine carrée irrationnelle.


# code: https://en.wikipedia.org/w/index.php?title=Euclidean_algorithm&oldid=1375335874#Implementations
# La dernière ligne est « return abs(a) », comme l'article le demande quand a ou b peut
# être négatif.
def gcd(a, b):
    while b != 0:
        t = b
        b = a % b
        a = t
    return abs(a)


# formule: https://en.wikipedia.org/w/index.php?title=Decimal&oldid=1375686107#Decimal_fractions
# n chiffres après le point : dénominateur 10ⁿ, numérateur sans le point. "9.3" -> 93/10.
def from_decimal(text):
    whole, _, decimals = text.partition(".")
    return Fraction(int(whole + decimals), 10 ** len(decimals))


# formule: https://en.wikipedia.org/w/index.php?title=Rational_number&oldid=1357066562#Embedding_of_integers
# Un entier n est la fraction n/1.
def to_fraction(x):
    if isinstance(x, Fraction):
        return x
    return Fraction(x)


class Fraction:
    # formule: https://en.wikipedia.org/w/index.php?title=Rational_number&oldid=1357066562#Irreducible_fraction
    # Forme canonique : divisée par le pgcd, dénominateur positif. 6/-4 -> -3/2.
    def __init__(self, numerator, denominator=1):
        if denominator == 0:
            raise ZeroDivisionError("division by zero")
        g = gcd(numerator, denominator)
        if denominator < 0:
            g = -g
        self.numerator = numerator // g
        self.denominator = denominator // g

    def __repr__(self):
        return "Fraction(%d, %d)" % (self.numerator, self.denominator)

    # formule: https://en.wikipedia.org/w/index.php?title=Rational_number&oldid=1357066562#Addition
    def __add__(a, b):
        if isinstance(b, float):
            return float(a) + b
        b = to_fraction(b)
        return Fraction(
            a.numerator * b.denominator + b.numerator * a.denominator,
            a.denominator * b.denominator,
        )

    __radd__ = __add__

    # formule: https://en.wikipedia.org/w/index.php?title=Rational_number&oldid=1357066562#Subtraction
    def __sub__(a, b):
        if isinstance(b, float):
            return float(a) - b
        b = to_fraction(b)
        return Fraction(
            a.numerator * b.denominator - b.numerator * a.denominator,
            a.denominator * b.denominator,
        )

    def __rsub__(a, b):
        return -a + b

    # formule: https://en.wikipedia.org/w/index.php?title=Rational_number&oldid=1357066562#Multiplication
    def __mul__(a, b):
        if isinstance(b, float):
            return float(a) * b
        b = to_fraction(b)
        return Fraction(a.numerator * b.numerator, a.denominator * b.denominator)

    __rmul__ = __mul__

    # formule: https://en.wikipedia.org/w/index.php?title=Rational_number&oldid=1357066562#Division
    def __truediv__(a, b):
        if isinstance(b, float):
            return float(a) / b
        b = to_fraction(b)
        return Fraction(a.numerator * b.denominator, a.denominator * b.numerator)

    def __rtruediv__(a, b):
        if isinstance(b, float):
            return b / float(a)
        return to_fraction(b) / a

    # formule: https://en.wikipedia.org/w/index.php?title=Rational_number&oldid=1357066562#Exponentiation_to_integer_power
    def __pow__(a, n):
        if n < 0:
            return Fraction(a.denominator**-n, a.numerator**-n)
        return Fraction(a.numerator**n, a.denominator**n)

    # formule: https://en.wikipedia.org/w/index.php?title=Rational_number&oldid=1357066562#Inverse
    def __neg__(a):
        return Fraction(-a.numerator, a.denominator)

    def __abs__(a):
        return -a if a < 0 else a

    # formule: https://en.wikipedia.org/w/index.php?title=Rational_number&oldid=1357066562#Equality
    # Deux formes canoniques sont égales si et seulement si leurs termes le sont.
    def __eq__(a, b):
        b = to_fraction(b)
        return a.numerator == b.numerator and a.denominator == b.denominator

    # formule: https://en.wikipedia.org/w/index.php?title=Rational_number&oldid=1357066562#Ordering
    # Dénominateurs positifs : a/b < c/d si et seulement si ad < bc.
    def __lt__(a, b):
        b = to_fraction(b)
        return a.numerator * b.denominator < b.numerator * a.denominator

    def __gt__(a, b):
        return to_fraction(b) < a

    # code: https://github.com/python/cpython/blob/v3.13.0/Lib/numbers.py#L308-L316
    # Division des deux entiers, sans les convertir en float d'abord : pas de dépassement
    # quand numérateur et dénominateur sont trop grands pour un float, si leur rapport ne
    # l'est pas.
    def __float__(self):
        return int(self.numerator) / int(self.denominator)
