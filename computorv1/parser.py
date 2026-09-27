import re

from .number import MAX_VALUE, MIN_VALUE, cancels

MAX_DEGREE = 10

# Étape 1, un seul '=' avec deux côtés non vides : " 3x + 1 = 4 " -> ('3x + 1 ', '4 ')
SIDES = re.compile(r"\s*([^=\s][^=]*)=\s*([^=\s][^=]*)")

# Les onze caractères en exposant unicode, et leur équivalent normal.
SUPERSCRIPTS = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")

# Étape 2, tout caractère autre que chiffre, lettre, exposant, point, + - * ^ = ou espace
FORBIDDEN = re.compile(r"[^0-9A-Za-z⁰¹²³⁴⁵⁶⁷⁸⁹⁻.+\-*^=\s]")

# Étape 2, une parenthèse, qu'il faudrait développer : "2(x+1)" -> '('
PARENTHESIS = re.compile(r"[()]")

# Étape 2, la première lettre, puis une lettre différente : "x + y = 0" -> ('x', 'y')
SECOND_UNKNOWN = re.compile(r"([A-Za-z])(?:[^A-Za-z]|\1)*((?!\1)[A-Za-z])", re.IGNORECASE)

# Étape 2, des espaces entre deux nombres, qui les colleraient une fois retirées : "2 3" -> ' '
MISSING_OPERATOR = re.compile(r"(?<=[\d.])\s+(?=[\d.])")

# Étape 2, un exposant décimal, que le sujet n'autorise pas : "X^1.5" -> '^1.'
BAD_EXPONENT = re.compile(r"\^\s*[+-]?\d+\s*\.")


# Étape 3, réécritures appliquées dans l'ordre à chaque côté.


def merge_signs(signs):
    minus_count = signs.group().count("-")
    if minus_count % 2 == 1:
        return "-"
    return "+"


NORMALIZATIONS = [
    # Nettoyage
    # Espaces supprimés : "3 * X" -> "3*X"
    (r"\s+", ""),
    # Exposant écrit en chiffres unicode : "3x²" -> "3x^2", "X¹⁰" -> "X^10", "X⁻¹" -> "X^-1"
    (r"[⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+", lambda run: "^" + run.group().translate(SUPERSCRIPTS)),
    # Inconnue ramenée à X, quelle que soit la lettre : "y" -> "X"
    (r"[A-Za-z]", "X"),
    # Nombres
    # Zéro manquant devant le point : ".5" -> "0.5"
    (r"(?<!\d)\.(?=\d)", "0."),
    # Point final sans décimale : "5." -> "5"
    (r"(\d)\.(?!\d)", r"\1"),
    # Termes
    # Nombre après X sans opérateur : "X3" -> "X*3"
    (r"X(?=\d)", "X*"),
    # Exposant absent, X non suivi de '^' : "X" -> "X^1", "XX" -> "X^1X^1"
    (r"X(?!\^)", "X^1"),
    # Multiplication implicite, chiffre suivi de X : "3X^1" -> "3*X^1", "X^1X^1" -> "X^1*X^1"
    (r"(\d)X", r"\1*X"),
    # Signes
    # Signes consécutifs fusionnés : "+-" -> "-", "--" -> "+"
    (r"[+-]{2,}", merge_signs),
    # Signe explicite en tête du côté : "X^1" -> "+X^1"
    (r"^(?=[\dX])", "+"),
    # Espace devant chaque signe sauf après '*' ou '^' : "-1*-X^1" et "X^-1" restent un terme
    (r"(?<![*^])[+-]", r" \g<0>"),
]


# Étape 4, lecture d'un côté normalisé.

# Un facteur, nombre ou X, avec un seul exposant :
# "9.3" -> ('9.3', None, None), "2^3" -> ('2', '3', None), "X^-1" -> (None, None, '-1')
FACTOR = re.compile(r"(\d+(?:\.\d+)?)(?:\^([+-]?\d+))?|X\^([+-]?\d+)")


class ComputorError(Exception):
    def __init__(self, message, position=None, text=None):
        super().__init__(message)
        self.position = position
        self.text = text


def parse(source):
    left, right = split_sides(source)
    check_characters(source)
    left_terms = read_terms(normalize(left))
    right_terms = read_terms(normalize(right))
    coefficients = add_terms(left_terms, right_terms)
    return reduce(coefficients)


# doc: https://docs.python.org/3/library/re.html#re.Pattern.fullmatch
def split_sides(source):
    sides = SIDES.fullmatch(source)
    if sides is None:
        message = "expected one '=' between two sides"
        raise ComputorError(message, equals_error_position(source))
    return sides.group(1), sides.group(2)


def equals_error_position(source):
    first = source.find("=")
    if first == -1:
        return len(source)
    second = source.find("=", first + 1)
    if second == -1:
        return first
    return second


# doc: https://docs.python.org/3/library/re.html#re.Pattern.search
def check_characters(source):
    parenthesis = PARENTHESIS.search(source)
    if parenthesis is not None:
        message = "parentheses are not supported, expand the product first"
        raise ComputorError(message, parenthesis.start())
    forbidden = FORBIDDEN.search(source)
    if forbidden is not None:
        raise ComputorError("unexpected character '%s'" % forbidden.group(), forbidden.start())
    missing_operator = MISSING_OPERATOR.search(source)
    if missing_operator is not None:
        raise ComputorError("missing operator between numbers", missing_operator.start())
    bad_exponent = BAD_EXPONENT.search(source)
    if bad_exponent is not None:
        raise ComputorError("exponent must be an integer", bad_exponent.start())
    second = SECOND_UNKNOWN.search(source)
    if second is not None:
        first, other = second.groups()
        message = "second unknown '%s', '%s' is already the unknown" % (other, first)
        raise ComputorError(message, second.start(2))


# doc: https://docs.python.org/3/library/re.html#re.sub
def normalize(side):
    text = side
    for pattern, replacement in NORMALIZATIONS:
        text = re.sub(pattern, replacement, text)
    return text


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
    coefficient = 1.0
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
def read_number(number, exponent, position, text):
    value = float(number)
    if exponent is not None:
        exponent = int(exponent)
        if value == 0.0 and exponent < 0:
            raise ComputorError("division by zero", position, text)
        try:
            value = value**exponent
        except OverflowError:
            raise ComputorError("number too large", position, text) from None
    if number.strip("0.") == "":
        return value
    check_magnitude(value, position, text)
    return value


def check_magnitude(value, position, text):
    if abs(value) > MAX_VALUE:
        raise ComputorError("number too large", position, text)
    if value != 0.0 and abs(value) < MIN_VALUE:
        raise ComputorError("number too small", position, text)


def add_terms(left_terms, right_terms):
    positives = {}
    negatives = {}
    for coefficient, degree in left_terms:
        add_contribution(positives, negatives, degree, coefficient)
    for coefficient, degree in right_terms:
        add_contribution(positives, negatives, degree, -coefficient)

    coefficients = {}
    for degree in positives.keys() | negatives.keys():
        up = positives.get(degree, 0.0)
        down = negatives.get(degree, 0.0)
        if cancels(up, down):
            coefficients[degree] = 0.0
        else:
            coefficients[degree] = up - down
    return coefficients


def add_contribution(positives, negatives, degree, coefficient):
    if coefficient < 0:
        negatives[degree] = negatives.get(degree, 0.0) - coefficient
    else:
        positives[degree] = positives.get(degree, 0.0) + coefficient


def reduce(coefficients):
    degrees = [d for d, coefficient in coefficients.items() if coefficient != 0.0]
    if not degrees:
        return []
    if min(degrees) < 0:
        message = "negative exponent X^%d after reduction" % min(degrees)
        raise ComputorError(message)
    degree = max(degrees)
    if degree > MAX_DEGREE:
        raise ComputorError("reduced degree %d greater than %d" % (degree, MAX_DEGREE))

    reduced = []
    for d in range(degree + 1):
        reduced.append(coefficients.get(d, 0.0))
    return reduced
