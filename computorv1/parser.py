import re

from .fraction import Fraction, from_decimal
from .normalize import ComputorError, normalize

MAX_DEGREE = 10

# Les calculs sont exacts, mais l'affichage passe par des floats : hors de ces bornes,
# b², -Δ / 4a ou -b / 2a dépasseraient leur capacité, environ 1.8e308.
MAX_VALUE = Fraction(10**100)
MIN_VALUE = Fraction(1, 10**100)

# Au-delà, une puissance exacte serait trop longue à calculer : 10^999999999 a un milliard
# de chiffres.
MAX_EXPONENT = 1000

# Étape 4, lecture des côtés normalisés, puis réduction.

# Un facteur, nombre ou X, avec un seul exposant :
# "9.3" -> ('9.3', None, None), "2^3" -> ('2', '3', None), "X^-1" -> (None, None, '-1')
FACTOR = re.compile(r"(\d+(?:\.\d+)?)(?:\^([+-]?\d+))?|X\^([+-]?\d+)")


def parse(source):
    left, right, name = normalize(source)
    coefficients = add_terms(read_terms(left), read_terms(right))
    return reduce(coefficients, name), name


# doc: https://docs.python.org/3/library/stdtypes.html#str.split
def read_terms(text):
    terms = []
    for term in text.split():
        terms.append(read_term(term))
    return terms


def read_term(term):
    sign = term[0]
    if sign not in "+-":
        raise ComputorError("missing sign before the term", 0, term)
    coefficient, degree = multiply_factors(term)
    if sign == "-":
        coefficient = -coefficient
    return coefficient, degree


# formule: https://en.wikipedia.org/w/index.php?title=Exponentiation&oldid=1375737168#Identities_and_properties
def multiply_factors(term):
    coefficient = Fraction(1)
    degree = 0
    position = 1
    for piece in term[1:].split("*"):
        if piece[:1] in ("+", "-"):
            if piece[0] == "-":
                coefficient = -coefficient
            piece = piece[1:]
            position = position + 1
        factor = FACTOR.fullmatch(piece)
        if factor is None:
            if piece.count("^") > 1:
                message = "chained exponent is ambiguous, 2^3^2 is either 64 or 512"
                raise ComputorError(message, position, term)
            raise ComputorError("invalid factor", position, term)
        number, number_exponent, exponent = factor.groups()
        if number is not None:
            coefficient = coefficient * read_number(number, number_exponent, position, term)
        else:
            degree = degree + int(exponent)
        position = position + len(piece) + 1
    check_magnitude(coefficient, 1, term)
    return coefficient, degree


# formule: https://en.wikipedia.org/w/index.php?title=Exponentiation&oldid=1375737168#Identities_and_properties
# Lecture exacte : "9.3" -> 93/10, "2^-3" -> 1/8.
def read_number(number, exponent, position, text):
    value = from_decimal(number)
    if exponent is not None:
        exponent = int(exponent)
        if value == 0 and exponent < 0:
            raise ComputorError("division by zero", position, text)
        if abs(exponent) > MAX_EXPONENT:
            raise ComputorError("exponent greater than %d" % MAX_EXPONENT, position, text)
        value = value**exponent
    check_magnitude(value, position, text)
    return value


def check_magnitude(value, position=None, text=None):
    if abs(value) > MAX_VALUE:
        raise ComputorError("number too large", position, text)
    if value != 0 and abs(value) < MIN_VALUE:
        raise ComputorError("number too small", position, text)


# Somme exacte des termes de même degré, ceux de droite soustraits : 0.1 + 0.2 - 0.3 = 0.
def add_terms(left_terms, right_terms):
    coefficients = {}
    for coefficient, degree in left_terms:
        coefficients[degree] = coefficients.get(degree, Fraction(0)) + coefficient
    for coefficient, degree in right_terms:
        coefficients[degree] = coefficients.get(degree, Fraction(0)) - coefficient
    return coefficients


def reduce(coefficients, name):
    degrees = [d for d, coefficient in coefficients.items() if coefficient != 0]
    if not degrees:
        return []
    if min(degrees) < 0:
        message = "negative exponent %s^%d after reduction" % (name, min(degrees))
        raise ComputorError(message)
    degree = max(degrees)
    if degree > MAX_DEGREE:
        raise ComputorError("reduced degree %d greater than %d" % (degree, MAX_DEGREE))

    reduced = []
    for d in range(degree + 1):
        coefficient = coefficients.get(d, Fraction(0))
        check_magnitude(coefficient)
        reduced.append(coefficient)
    return reduced
