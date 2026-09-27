from .fraction import Fraction
from .normalize import ComputorError

# Étape 5 : des termes lus des deux côtés au polynôme réduit, ax^0 + bx^1 + ... = 0.
# [(3, 2), (-1, 1)] et [(1, 0)] -> [-1, -1, 3]

MAX_DEGREE = 10

# Les calculs sont exacts, mais l'affichage passe par des floats : hors de ces bornes,
# b², -Δ / 4a ou -b / 2a dépasseraient leur capacité, environ 1.8e308.
MAX_VALUE = Fraction(10**100)
MIN_VALUE = Fraction(1, 10**100)


def check_magnitude(value, position=None, text=None):
    if abs(value) > MAX_VALUE:
        raise ComputorError("number too large", position, text)
    if value != 0 and abs(value) < MIN_VALUE:
        raise ComputorError("number too small", position, text)


def reduce(left_terms, right_terms, name):
    coefficients = add_terms(left_terms, right_terms)
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


# Somme exacte des termes de même degré, ceux de droite soustraits : 0.1 + 0.2 - 0.3 = 0.
def add_terms(left_terms, right_terms):
    coefficients = {}
    for coefficient, degree in left_terms:
        coefficients[degree] = coefficients.get(degree, Fraction(0)) + coefficient
    for coefficient, degree in right_terms:
        coefficients[degree] = coefficients.get(degree, Fraction(0)) - coefficient
    return coefficients
