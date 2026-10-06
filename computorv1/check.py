import re

from .errors import ComputorError


# Obtenir la première lettre
UNKNOWN = re.compile(r"[A-Za-z]")

# Un seul '=' entre deux côtés  => " 3x + 1 = 4 " -> (' 3x + 1 ', ' 4 ')
SIDES = re.compile(r"([^=]*)=([^=]*)")

# Seulement chiffres lettres point + - * ^ = et espace
FORBIDDEN = re.compile(r"[^0-9A-Za-z.+\-*^=\s]")

# Parenthèses interdites
PARENTHESIS = re.compile(r"[()]")

# Espaces bizarres entre nombres "2 3", "2 .5", "2. 5"
MISSING_OPERATOR = re.compile(r"[\d.]\s+[\d.]")

# Pas de point dans l'exposant "x^0.5", "x^.5", "x^2."
BAD_EXPONENT = re.compile(r"\^\s*\d*\.\d*")

# Pas de signe dans l'exposant
SIGNED_EXPONENT = re.compile(r"\^\s*[+-]")

# Exposant enchaîné ou doublé "x^2^3", "x^^2"
CHAINED_EXPONENT = re.compile(r"\^[\d\s]*\^")

# Exposant absent ou non numérique "x^", "x^ = 1", "1^X", "x^*2"
MISSING_EXPONENT = re.compile(r"\^\s*([^\d\s]|$)")

# Un seul point par nombre "2..5", "2.5.", "1.2.3"
SEVERAL_POINTS = re.compile(r"\.\d*\.")

# Pas deux signes à la suite "--x", "x - - 2", "1 + -3"
CONSECUTIVE_SIGNS = re.compile(r"[+-]\s*[+-]")

# Signe sans terme "x + = 1", "1 * X^0 +", "3x+^2", "- * X"
LONE_SIGN = re.compile(r"[+-]\s*([^\d.A-Za-z\s]|$)")


# Saisie valide => nom de l'inconnue
def check(source):
    name = check_characters(source)
    check_sides(source)
    return name


# Pas de lettre => inconnue X
def variable_name(source):
    letter = UNKNOWN.search(source)
    if letter is None:
        return "X"
    return letter.group()


# doc: https://docs.python.org/3/library/re.html#re.Pattern.fullmatch
def check_sides(source):
    sides = SIDES.fullmatch(source)
    if sides is None or not sides.group(1).strip() or not sides.group(2).strip():
        raise ComputorError("expected one '=' between two sides")


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
        raise ComputorError(f"missing operator between numbers : {missing_operator.group()}")
    bad_exponent = BAD_EXPONENT.search(source)
    if bad_exponent is not None:
        raise ComputorError(f"exponent must be an integer : {bad_exponent.group()}")
    signed_exponent = SIGNED_EXPONENT.search(source)
    if signed_exponent is not None:
        raise ComputorError(f"exponent must not have a sign : {signed_exponent.group()}")
    chained_exponent = CHAINED_EXPONENT.search(source)
    if chained_exponent is not None:
        raise ComputorError(f"chained exponent is ambiguous : {chained_exponent.group()}")
    missing_exponent = MISSING_EXPONENT.search(source)
    if missing_exponent is not None:
        raise ComputorError(f"exponent must be an integer : {missing_exponent.group()}")
    several_points = SEVERAL_POINTS.search(source)
    if several_points is not None:
        raise ComputorError(f"number with more than one point : {several_points.group()}")
    consecutive_signs = CONSECUTIVE_SIGNS.search(source)
    if consecutive_signs is not None:
        raise ComputorError(f"consecutive signs : {consecutive_signs.group()}")
    lone_sign = LONE_SIGN.search(source)
    if lone_sign is not None:
        raise ComputorError(f"missing term after sign : {lone_sign.group()}")
    name = variable_name(source)
    test = UNKNOWN.search(source.replace(name, ""))
    if test is not None:
        raise ComputorError("Only one unknown is allowed")
    return name
