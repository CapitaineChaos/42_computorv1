from .eq_linear import Linear
from .eq_quaddratic import TwoRoots, DoubleRoot, ComplexRoots
from .eq import AllReals, NoSolution, TooHigh


def solve(p, degree, name):
    if degree < 0:
        return AllReals(p, degree, name)
    if degree == 0:
        return NoSolution(p, degree, name)
    if degree == 1:
        return Linear(p, degree, name)
    if degree == 2:
        c, b, a = p
        delta = b * b - 4 * a * c
        if delta > 0:
            return TwoRoots(p, degree, name, delta)
        if delta < 0:
            return ComplexRoots(p, degree, name, delta)
        return DoubleRoot(p, degree, name, delta)
    return TooHigh(p, degree, name)
