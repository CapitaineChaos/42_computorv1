# Author     : CLAUDE OPUS 5.5
# Maintainer : CLAUDE OPUS 5.5

# Oracle : verdict attendu pour une saisie, écrit d'après les règles de test_saisie.py et
# indépendant du parser (il a son propre découpage). Le fuzz compare le parser à l'oracle.
#
# Lecture de gauche à droite, le premier défaut rencontré l'emporte. Quand plusieurs défauts
# tombent sur le même élément, l'ordre est celui des contrôles ci-dessous. L'inconnue en
# exposant passe avant une seconde inconnue. Un '*' ou un '^' en tête de saisie est jugé sur
# ce qui le suit : un caractère invalide derrière lui est signalé d'abord. Derrière '=', non.

import re

from computorv1.parser import MAX_LEN

ELEMENT = re.compile(
    r"(?P<number>[0-9]+(?:\.[0-9]*)?|\.[0-9]+)"
    r"|(?P<unknown>[A-Za-z])"
    r"|(?P<symbol>[=+\-*^])"
    r"|(?P<blank>[ \t]+)"
    r"|(?P<invalid>.)",
    re.DOTALL,
)

OPERATORS = ("+", "-", "*")


# Premier élément non blanc à partir de `at` : (genre, texte), ("end", "") en fin de saisie.
def following(source, at):
    match = ELEMENT.match(source, len(source) - len(source[at:].lstrip(" \t")))
    if match is None:
        return "end", ""
    return match.lastgroup, match.group()


def invalid(text):
    return "INP_03" if text == "." else "INP_02"


# '*' en tête de membre (previous : "start" ou "=").
def leading_star(previous, next_kind, next_text):
    if next_kind == "invalid" and previous == "start":
        return invalid(next_text)
    if next_text == "^":
        return "POW_09"
    if next_kind == "end" and previous == "start":
        return "OPR_04"
    return "OPR_06" if previous == "start" else "OPR_05"


# '^' en tête de membre (previous : "start" ou "="), seul compris.
def leading_caret(previous, next_kind, next_text):
    if next_kind == "invalid" and previous == "start":
        return invalid(next_text)
    return "POW_04"


def expected(source):
    if len(source) > MAX_LEN:
        return "CPT_02"
    previous = "start"  # élément précédent, blancs ignorés : start, number, unknown ou le symbole
    before = "start"  # élément encore avant
    unknown = None
    equals = False
    after_exponent = False  # l'élément précédent est l'opérande d'un exposant

    for match in ELEMENT.finditer(source):
        kind, text = match.lastgroup, match.group()
        if kind == "blank":
            continue
        if kind == "invalid":
            return invalid(text)

        in_exponent = previous == "^"
        exponent_operand = False
        if kind == "number":
            if previous in ("number", "unknown"):
                return "OPR_07"
            if in_exponent and "." in text:
                return "POW_06"
            exponent_operand = in_exponent
        elif kind == "unknown":
            if in_exponent:
                return "POW_02"
            if unknown is not None and unknown != text:
                return "CPT_03"
            unknown = text
        elif text == "=":
            if previous == "start":
                return "EQL_01"
            if in_exponent:
                return "POW_01"
            if previous in OPERATORS:
                return "OPR_03" if before == "start" else "OPR_01"
            if equals:
                return "EQL_03"
            equals = True
        elif text in ("+", "-"):
            if in_exponent:
                return "POW_01"
        elif text == "*":
            if in_exponent:
                return "POW_01"
            if previous in ("start", "="):
                return leading_star(previous, *following(source, match.end()))
            if previous == "*" and before in ("number", "unknown"):
                return "OPR_07"
            if previous in OPERATORS:
                return "OPR_01"
        elif text == "^":
            if previous == "^":
                return "POW_07"
            if previous in ("start", "="):
                return leading_caret(previous, *following(source, match.end()))
            if previous in OPERATORS:
                return "POW_04"
            if after_exponent:
                return "POW_08"

        after_exponent = exponent_operand
        before = previous
        previous = kind if kind in ("number", "unknown") else text

    if previous == "start":
        return "INP_01"
    if previous == "=":
        return "EQL_02"
    if previous == "^":
        return "POW_03"
    if previous in OPERATORS:
        if before == "start":
            return "OPR_04"
        return "OPR_03" if before == "=" else "OPR_02"
    if not equals:
        return "EQL_04"
    return None
