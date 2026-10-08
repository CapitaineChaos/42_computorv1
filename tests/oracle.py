# Author     : CLAUDE OPUS 5.5
# Maintainer : CLAUDE OPUS 5.5

# Oracle : verdict attendu pour une saisie, écrit d'après les règles de test_saisie.py et
# indépendant du parser (il a son propre découpage). Le fuzz compare le parser à l'oracle.
#
# Lecture de gauche à droite, le premier défaut rencontré l'emporte. Quand plusieurs défauts
# tombent sur le même élément, l'ordre est celui des contrôles ci-dessous : caractère invalide,
# incrément ou décrément, puis le défaut propre à l'élément, puis inconnue multiple ou second
# signe égal.
#
# REJECTED : refus attendu sans code fixé, pour une situation qu'aucun code ne couvre encore.

import re

from computorv1.parser import MAX_LEN

REJECTED = "refusé"

ELEMENT = re.compile(
    r"(?P<number>[0-9]+(?:\.[0-9]*)?|\.[0-9]+)"
    r"|(?P<unknown>[A-Za-z])"
    r"|(?P<symbol>[=+\-*^])"
    r"|(?P<blank>[ \t]+)"
    r"|(?P<invalid>.)",
    re.DOTALL,
)

OPERATORS = "+-*^"


def expected(source):
    if len(source) > MAX_LEN:
        return "LEN_01"
    previous = "start"  # élément précédent, blancs ignorés : start, operand ou le symbole
    glued = False  # l'élément courant touche le précédent, sans blanc entre eux
    unknown = None
    equals = False
    in_exponent = False  # après '^', jusqu'à l'opérande de l'exposant
    after_exponent = False  # l'élément précédent est l'opérande d'un exposant
    zero_base = False  # l'exposant en cours s'applique à un zéro
    negative = False  # nombre impair de '-' devant l'opérande de l'exposant
    previous_text = ""

    for match in ELEMENT.finditer(source):
        kind, text, at = match.lastgroup, match.group(), match.start()
        if kind == "blank":
            glued = False
            continue
        if kind == "invalid":
            return "CHR_01"

        # '++' ou '--' accolé à une lettre, devant ou derrière : incrément ou décrément de bc.
        if text in "+-" and source[at + 1 : at + 2] == text:
            before, after = source[at - 1 : at] if at else "", source[at + 2 : at + 3]
            if before.isalpha() or after.isalpha():
                return "VAR_02" if text == "+" else "VAR_03"

        exponent_operand = False
        if kind == "number":
            if previous == "number":
                return "OPR_05"
            if in_exponent and "." in text:
                return "EXP_04"
            # Zéro à une puissance négative : bc s'arrête sur « divide by zero ».
            if in_exponent and zero_base and negative and float(text):
                return REJECTED
            exponent_operand = in_exponent
        elif kind == "unknown":
            if in_exponent:
                return "EXP_03"
            if unknown is None:
                unknown = text
            elif unknown != text:
                return "VAR_01"
        elif text == "=":
            if previous == "start":
                return "EQL_01"
            if previous in "+-*":
                return "OPR_02"
            if previous == "^":
                return "EXP_01"
            if equals:
                return "EQL_03"
            equals = True
        elif text == "+":
            if previous in ("start", "=", "+", "-"):
                return "SGN_04"
            if previous in "*^":
                return "OPR_04"
        elif text == "-":
            if previous == "-" and glued:
                return "SGN_03"
        elif text == "*":
            if previous in ("start", "=", "^"):
                return "OPR_01"
            if previous in "+-*":
                return "MUL_01"
        elif text == "^":
            if previous in ("start", "=") or previous in OPERATORS:
                return "EXP_02"
            if after_exponent:
                return "EXP_05"

        if text == "^":
            zero_base, negative = previous == "number" and not float(previous_text), False
        elif in_exponent and text == "-":
            negative = not negative
        in_exponent = text == "^" or (in_exponent and text == "-")
        after_exponent = exponent_operand
        previous_text = text
        previous = "number" if kind == "number" else "unknown" if kind == "unknown" else text
        glued = True

    if previous == "start":
        return "EQL_04"
    if previous == "=":
        return "EQL_02"
    if previous in "+-*":
        return "OPR_02"
    if previous == "^":
        return "EXP_01"
    if not equals:
        return "EQL_04"
    return None
