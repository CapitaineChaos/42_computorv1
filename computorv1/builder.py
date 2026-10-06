from .eq import AllReals, NoSolution, TooHigh
from .eq_linear import Linear
from .eq_quaddratic import ComplexRoots, DoubleRoot, TwoRoots
from .reduce import coeffs_to_array


def build_eq(coeffs, degree, name):
    if degree < 0:
        return AllReals(coeffs, degree, name)
    if degree == 0:
        return NoSolution(coeffs, degree, name)
    if degree == 1:
        return Linear(coeffs, degree, name)
    if degree == 2:
        c, b, a = coeffs_to_array(coeffs, 2)
        delta = b * b - 4 * a * c
        if delta > 0:
            return TwoRoots(coeffs, degree, name, delta)
        if delta < 0:
            return ComplexRoots(coeffs, degree, name, delta)
        return DoubleRoot(coeffs, degree, name, delta)
    return TooHigh(coeffs, degree, name)
