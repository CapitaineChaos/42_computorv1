from collections import namedtuple

from .number import EPSILON, real, sqrt

Solution = namedtuple("Solution", "kind roots steps")


def solve(p, margins, name):
    degree = len(p) - 1
    if degree < 0:
        return Solution("all", [], [])
    if degree == 0:
        return Solution("none", [], [])
    if degree == 1:
        return linear(p, name)
    if degree == 2:
        return quadratic(p, margins, name)
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
def quadratic(p, margins, name):
    c, b, a = p
    delta = b * b - 4 * a * c
    if abs(delta) <= delta_margin(p, margins):
        delta = 0.0
    steps = [
        "a = %s, b = %s, c = %s" % (real(a), real(b), real(c)),
        "Δ = b² - 4ac = %s² - 4 * %s * %s = %s" % (wrap(b), wrap(a), wrap(c), real(delta)),
        vertex(b, a, delta),
    ]
    if delta == 0.0:
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
    return Solution("negative", [complex(re, im), complex(re, -im)], steps)


# formule: https://en.wikipedia.org/w/index.php?title=Quadratic_function&oldid=1360283093#Vertex
def vertex(b, a, delta):
    h = -b / (2 * a)
    k = -delta / (4 * a)
    extremum = "minimum" if a > 0 else "maximum"
    return "vertex = (-b / 2a, -Δ / 4a) = (%s, %s), %s" % (real(h), real(k), extremum)


# Erreur possible de b² - 4ac. Héritée : a, b et c peuvent chacun être faux de leur marge,
# le pire écart de b² est donc (|b| + mb)² - b², celui de ac (|a| + ma)(|c| + mc) - |ac|.
# Arrondis : b * b, 4 * a * c et la soustraction.
def delta_margin(p, margins):
    c, b, a = p
    mc, mb, ma = margins
    inherited = (abs(b) + mb) ** 2 - b * b + 4 * ((abs(a) + ma) * (abs(c) + mc) - abs(a * c))
    rounding = 2 * EPSILON * (b * b + 4 * abs(a * c))
    return inherited + rounding


def wrap(x):
    return "(%s)" % real(x) if x < 0 else real(x)
