from collections import namedtuple

from .number import cancels, real, sqrt

Solution = namedtuple("Solution", "kind roots steps")


def solve(p):
    degree = len(p) - 1
    if degree < 0:
        return Solution("all", [], [])
    if degree == 0:
        return Solution("none", [], [])
    if degree == 1:
        return linear(*p)
    if degree == 2:
        return quadratic(*p)
    return Solution("high", [], [])


# formule: https://en.wikipedia.org/w/index.php?title=Linear_equation&oldid=1359797583#One_variable
def linear(b, a):
    x = -b / a
    steps = [
        "a = %s, b = %s" % (real(a), real(b)),
        "x = -b / a = %s / %s = %s" % (real(-b), wrap(a), real(x)),
    ]
    return Solution("linear", [x], steps)


# formule: https://en.wikipedia.org/w/index.php?title=Quadratic_formula&oldid=1376700315
# formule: https://en.wikipedia.org/w/index.php?title=Quadratic_equation&oldid=1368768952#Discriminant
def quadratic(c, b, a):
    delta = b * b - 4 * a * c
    steps = [
        "a = %s, b = %s, c = %s" % (real(a), real(b), real(c)),
        "Δ = b² - 4ac = %s² - 4 * %s * %s = %s" % (wrap(b), wrap(a), wrap(c), real(delta)),
        vertex(c, b, a),
    ]
    if cancels(b * b, 4 * a * c):
        x = -b / (2 * a)
        steps.append("x = -b / 2a = %s / %s = %s" % (real(-b), wrap(2 * a), real(x)))
        return Solution("double", [x], steps)
    if delta > 0:
        x1 = (-b + sqrt(delta)) / (2 * a)
        x2 = (-b - sqrt(delta)) / (2 * a)
        steps.append(
            "x1 = (-b + √Δ) / 2a = (%s + √%s) / %s = %s"
            % (real(-b), real(delta), wrap(2 * a), real(x1))
        )
        steps.append(
            "x2 = (-b - √Δ) / 2a = (%s - √%s) / %s = %s"
            % (real(-b), real(delta), wrap(2 * a), real(x2))
        )
        return Solution("positive", [x1, x2], steps)
    re = -b / (2 * a)
    im = sqrt(-delta) / (2 * a)
    steps.append("-b / 2a = %s / %s = %s" % (real(-b), wrap(2 * a), real(re)))
    steps.append("√-Δ / 2a = √%s / %s = %s" % (real(-delta), wrap(2 * a), real(im)))
    return Solution("negative", [complex(re, im), complex(re, -im)], steps)


# formule: https://en.wikipedia.org/w/index.php?title=Quadratic_function&oldid=1360283093#Vertex
def vertex(c, b, a):
    h = -b / (2 * a)
    k = c - b * b / (4 * a)
    extremum = "minimum" if a > 0 else "maximum"
    return "vertex = (-b / 2a, c - b² / 4a) = (%s, %s), %s" % (real(h), real(k), extremum)


def wrap(x):
    return "(%s)" % real(x) if x < 0 else real(x)
