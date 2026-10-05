import re

from .errors import ComputorError

# Étapes 1 à 3 : du texte tapé à deux côtés réécrits, un terme signé par mot.
# " 3x² - x = 1 " -> (' +3*X^2 -X^1', ' +1', 'x'), le dernier étant le nom de l'inconnue.

# Étape 1, un seul '=' avec deux côtés non vides : " 3x + 1 = 4 " -> ('3x + 1 ', '4 ')
SIDES = re.compile(r"\s*([^=\s][^=]*)=\s*([^=\s][^=]*)")

# Les douze caractères en exposant unicode, et leur équivalent normal.
SUPERSCRIPTS = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻", "0123456789+-")

# Étape 2, tout caractère autre que chiffre, lettre, exposant, point, + - * ^ = ou espace
FORBIDDEN = re.compile(r"[^0-9A-Za-z⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻.+\-*^=\s]")

# Étape 2, une parenthèse, qu'il faudrait développer : "2(x+1)" -> '('
PARENTHESIS = re.compile(r"[()]")

# Étape 2, la première lettre, qui nomme l'inconnue : "3y + 1 = 0" -> 'y'
UNKNOWN = re.compile(r"[A-Za-z]")

# Étape 2, la première lettre, puis une lettre différente, casse comprise :
# "x + y = 0" -> ('x', 'y'), "x = X" -> ('x', 'X')
SECOND_UNKNOWN = re.compile(r"([A-Za-z])(?:[^A-Za-z]|\1)*((?!\1)[A-Za-z])")

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
    # Exposant écrit en chiffres unicode : "3x²" -> "3x^2", "X¹⁰" -> "X^10", "X⁻¹" -> "X^-1",
    # "X⁺²" -> "X^+2"
    (r"[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻]+", lambda run: "^" + run.group().translate(SUPERSCRIPTS)),
    # Inconnue ramenée à X en interne, son nom est gardé à part : "y" -> "X"
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


def normalize(source):
    left, right = split_sides(source)
    check_characters(source)
    return normalize_side(left), normalize_side(right), unknown_name(source)


# Sans lettre, "1 = 2", l'inconnue garde le nom du sujet.
def unknown_name(source):
    letter = UNKNOWN.search(source)
    if letter is None:
        return "X"
    return letter.group()


# doc: https://docs.python.org/3/library/re.html#re.Pattern.fullmatch
def split_sides(source):
    sides = SIDES.fullmatch(source)
    if sides is None:
        raise ComputorError("expected one '=' between two sides")
    return sides.group(1), sides.group(2)


# doc: https://docs.python.org/3/library/re.html#re.Pattern.search
def check_characters(source):
    parenthesis = PARENTHESIS.search(source)
    if parenthesis is not None:
        raise ComputorError("parentheses are not supported")
    forbidden = FORBIDDEN.search(source)
    if forbidden is not None:
        raise ComputorError(f"unexpected character '{forbidden.group()}'")
    missing_operator = MISSING_OPERATOR.search(source)
    if missing_operator is not None:
        raise ComputorError("missing operator between numbers")
    bad_exponent = BAD_EXPONENT.search(source)
    if bad_exponent is not None:
        raise ComputorError("exponent must be an integer")
    second = SECOND_UNKNOWN.search(source)
    if second is not None:
        first, other = second.groups()
        raise ComputorError(f"second unknown '{other}', '{first}' is already the unknown")


# doc: https://docs.python.org/3/library/re.html#re.sub
def normalize_side(side):
    text = side
    for pattern, replacement in NORMALIZATIONS:
        text = re.sub(pattern, replacement, text)
    return text
