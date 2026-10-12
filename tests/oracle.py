# Author     : CLAUDE OPUS 5.5
# Maintainer : CLAUDE OPUS 5.5

# Oracle : verdict attendu pour une saisie, écrit d'après les règles de test_saisie.py et
# indépendant du parser (il a son propre découpage). Le fuzz compare le parser à l'oracle.
#
# Lecture de gauche à droite, le premier défaut rencontré l'emporte. Quand plusieurs défauts
# tombent sur le même élément, l'ordre est celui des contrôles ci-dessous : caractère invalide,
# puis le défaut propre à l'élément, puis inconnue multiple ou second signe égal. Une seconde
# inconnue passe avant l'inconnue en exposant.

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


# Premier élément non blanc à partir de `at`, "end" en fin de saisie.
def following(source, at):
    rest = source[at:].lstrip(" \t")
    return rest[:1] or "end"


def expected(source):
    if len(source) > MAX_LEN:
        return "LEN_01"
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
            return "CHR_02" if text == "." else "CHR_01"

        in_exponent = previous == "^"
        exponent_operand = False
        if kind == "number":
            if previous == "number":
                return "NBR_01"
            if previous == "unknown":
                return "NBR_02"
            if in_exponent and "." in text:
                return "EXP_04"
            exponent_operand = in_exponent
        elif kind == "unknown":
            if unknown is not None and unknown != text:
                return "VAR_01"
            if in_exponent:
                return "EXP_03"
            unknown = text
        elif text == "=":
            if previous == "start":
                return "EQL_01"
            if in_exponent:
                return "EXP_01"
            if previous in OPERATORS:
                if before == "start":
                    return "OPR_10"
                if before in ("number", "unknown"):
                    return "VAL_01"
                return "OPR_02"
            if equals:
                return "EQL_03"
            equals = True
        elif text in ("+", "-"):
            if in_exponent:
                return "EXP_14"
        elif text == "*":
            if in_exponent:
                return "EXP_14"
            # Seul entre le début ou '=' et '=' ou la fin : orphelin, jugé sur ce qui suit.
            orphan = following(source, match.end()) in ("=", "end")
            if previous in ("start", "=") and not orphan:
                return "OPR_01"
            if previous in OPERATORS:
                return "OPR_01"
        elif text == "^":
            if previous in ("start", "="):
                next_element = following(source, match.end())
                if (previous, next_element) in (("start", "="), ("=", "end")):
                    return "EXP_13"
                return "EXP_02"
            if previous == "^":
                return "EXP_07"
            if previous in OPERATORS:
                return "EXP_02"
            if after_exponent:
                return "EXP_10"

        after_exponent = exponent_operand
        before = previous
        previous = kind if kind in ("number", "unknown") else text

    if previous == "start":
        return "EMP_01"
    if previous == "=":
        return "EQL_02"
    if previous == "^":
        return "EXP_01"
    if previous in OPERATORS:
        return "OPR_11" if before == "=" else "OPR_02"
    if not equals:
        return "EQL_04"
    return None
