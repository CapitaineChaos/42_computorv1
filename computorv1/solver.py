from .eq_linear import Linear
from .eq_quaddratic import quadratic
from .equation import AllReals, NoSolution, TooHigh


def solve(p, degree, name):
    if degree < 0:
        return AllReals(name)
    if degree == 0:
        return NoSolution(name)
    if degree == 1:
        return Linear(p, name)
    if degree == 2:
        return quadratic(p, name)
    return TooHigh(name)
