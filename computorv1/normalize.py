import re

NORMALIZATIONS = [

    # Espaces supprimés : "3 * X" -> "3*X"
    (r"\s+", ""),
    # Remplacer les inconnues par X pour mieux identifier
    (r"[A-Za-z]", "X"),

    # Zéro manquant devant le point : ".5" -> "0.5"
    (r"(?<!\d)\.(?=\d)", "0."),
    # Point final sans décimale : "5." -> "5"
    (r"(\d)\.(?!\d)", r"\1"),

    # Nombre après X sans opérateur : "X3" -> "X*3"
    (r"X(?=\d)", "X*"),
    # Exposant absent, X non suivi de '^' : "X" -> "X^1", "XX" -> "X^1X^1"
    (r"X(?!\^)", "X^1"),
    # Multiplication implicite, chiffre suivi de X : "3X^1" -> "3*X^1", "X^1X^1" -> "X^1*X^1"
    (r"(\d)X", r"\1*X"),

    # Signe explicite en tête du côté : "X^1" -> "+X^1"
    (r"^(?=[\dX])", "+"),
    # Espace devant chaque signe sauf après '*' : "-1*-X^1" reste un terme
    (r"(?<!\*)[+-]", r" \g<0>"),
]


# Saisie déjà validée par check : un seul '=' entre deux côtés non vides.
def normalize(source):
    left, right = source.split("=")
    return normalize_side(left), normalize_side(right)


# doc: https://docs.python.org/3/library/re.html#re.sub
def normalize_side(side):
    text = side
    for pattern, replacement in NORMALIZATIONS:
        text = re.sub(pattern, replacement, text)
    return text
