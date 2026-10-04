import re

from .errors import ComputorError
from .fraction import Fraction, from_decimal
from .normalize import normalize
from .reduce import reduce

# Étape 4, lecture des côtés normalisés : un couple (coefficient, degré) par terme.
# " +3*X^2 -X^1" -> [(3, 2), (-1, 1)]

# Un facteur, nombre ou X, avec un seul exposant :
# "9.3" -> ('9.3', None, None), "2^3" -> ('2', '3', None), "X^-1" -> (None, None, '-1')
FACTOR = re.compile(r"(\d+(?:\.\d+)?)(?:\^([+-]?\d+))?|X\^([+-]?\d+)")


# Étapes 1 à 5 : texte tapé -> coefficients par degré, degré, nom de l'inconnue.
def parse(source):
    left, right, name = normalize(source)
    coefficients, degree = reduce(read_terms(left), read_terms(right), name)
    return coefficients, degree, name


# doc: https://docs.python.org/3/library/stdtypes.html#str.split
def read_terms(text):
    terms = []
    for term in text.split():
        terms.append(read_term(term))
    return terms


def read_term(term):
    sign = term[0]
    if sign not in "+-":
        raise ComputorError("missing sign before the term")
    coefficient, degree = multiply_factors(term)
    if sign == "-":
        coefficient = -coefficient
    return coefficient, degree


# formule: https://en.wikipedia.org/w/index.php?title=Exponentiation&oldid=1375737168#Identities_and_properties
def multiply_factors(term):
    coefficient = Fraction(1)
    degree = 0
    for piece in term[1:].split("*"):
        if piece[:1] in ("+", "-"):
            if piece[0] == "-":
                coefficient = -coefficient
            piece = piece[1:]
        factor = FACTOR.fullmatch(piece)
        if factor is None:
            if piece.count("^") > 1:
                raise ComputorError("chained exponent is ambiguous, 2^3^2 is either 64 or 512")
            raise ComputorError("invalid factor")
        number, number_exponent, exponent = factor.groups()
        if number is not None:
            coefficient = coefficient * read_number(number, number_exponent)
        else:
            degree = degree + int(exponent)
    return coefficient, degree


# formule: https://en.wikipedia.org/w/index.php?title=Exponentiation&oldid=1375737168#Identities_and_properties
# Lecture exacte : "9.3" -> 93/10, "2^-3" -> 1/8.
def read_number(number, exponent):
    value = from_decimal(number)
    if exponent is not None:
        value = value ** int(exponent)
    return value
