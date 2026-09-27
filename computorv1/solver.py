from collections import namedtuple

from .number import real, sqrt

Solution = namedtuple("Solution", "kind roots steps")


def solve(p, name):
    degree = len(p) - 1
    if degree < 0:
        return Solution("all", [], [])
    if degree == 0:
        return Solution("none", [], [])
    if degree == 1:
        return linear(p, name)
    if degree == 2:
        return quadratic(p, name)
    return Solution("high", [], [])


# formule: https://en.wikipedia.org/w/index.php?title=Linear_equation&oldid=1359797583#One_variable
def linear(p, name):
    b, a = p
    x = -b / a
    steps = [
        "a = %s, b = %s" % (real(a), real(b)),
        "%s = -b / a = %s / %s = %s" % (name, real(-b), wrap(a), real(x)),
    ]
    return Solution("linear", [x], steps)


# formule: https://en.wikipedia.org/w/index.php?title=Quadratic_formula&oldid=1376700315
# formule: https://en.wikipedia.org/w/index.php?title=Quadratic_equation&oldid=1368768952#Discriminant
# Δ est exact, le cas se choisit sans tolérance. Seul √Δ peut être irrationnel : il est
# alors un float, et les solutions qui en dépendent aussi.
def quadratic(p, name):
    c, b, a = p
    delta = b * b - 4 * a * c
    steps = [
        "a = %s, b = %s, c = %s" % (real(a), real(b), real(c)),
        "Δ = b² - 4ac = %s² - 4 * %s * %s = %s" % (wrap(b), wrap(a), wrap(c), real(delta)),
        vertex(b, a, delta),
    ]
    if delta == 0:
        x = -b / (2 * a)
        steps.append("%s = -b / 2a = %s / %s = %s" % (name, real(-b), wrap(2 * a), real(x)))
        return Solution("double", [x], steps)
    if delta > 0:
        x1 = (-b + sqrt(delta)) / (2 * a)
        x2 = (-b - sqrt(delta)) / (2 * a)
        steps.append(
            "%s1 = (-b + √Δ) / 2a = (%s + √%s) / %s = %s"
            % (name, real(-b), real(delta), wrap(2 * a), real(x1))
        )
        steps.append(
            "%s2 = (-b - √Δ) / 2a = (%s - √%s) / %s = %s"
            % (name, real(-b), real(delta), wrap(2 * a), real(x2))
        )
        return Solution("positive", [x1, x2], steps)
    re = -b / (2 * a)
    im = sqrt(-delta) / (2 * a)
    steps.append("-b / 2a = %s / %s = %s" % (real(-b), wrap(2 * a), real(re)))
    steps.append("√-Δ / 2a = √%s / %s = %s" % (real(-delta), wrap(2 * a), real(im)))
    return Solution("negative", [(re, im), (re, -im)], steps)


# formule: https://en.wikipedia.org/w/index.php?title=Quadratic_function&oldid=1360283093#Vertex
def vertex(b, a, delta):
    h = -b / (2 * a)
    k = -delta / (4 * a)
    extremum = "minimum" if a > 0 else "maximum"
    return "vertex = (-b / 2a, -Δ / 4a) = (%s, %s), %s" % (real(h), real(k), extremum)


def wrap(x):
    return "(%s)" % real(x) if x < 0 else real(x)
