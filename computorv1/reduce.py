from .errors import ComputorError
from .fraction import Fraction


MAX_REDUCED_DISP = 3

def reduce(left_terms, right_terms, name):
    coefficients = add_terms(left_terms, right_terms)
    degrees = [d for d, coefficient in coefficients.items() if coefficient != 0]
    if not degrees:
        return {}, -1
    if min(degrees) < 0:
        message = "negative exponent %s^%d after reduction" % (name, min(degrees))
        raise ComputorError(message)
    return coefficients, max(degrees)


def dense(coefficients, degree):
    return [coefficients.get(d, Fraction(0)) for d in range(degree + 1)]


def add_terms(left_terms, right_terms):
    coefficients = {}
    for coefficient, degree in left_terms:
        coefficients[degree] = coefficients.get(degree, Fraction(0)) + coefficient
    for coefficient, degree in right_terms:
        coefficients[degree] = coefficients.get(degree, Fraction(0)) - coefficient
    return coefficients
