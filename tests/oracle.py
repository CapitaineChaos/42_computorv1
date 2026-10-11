# Author     : CLAUDE OPUS 5.5
# Maintainer : CLAUDE OPUS 5.5

# Oracle : verdict attendu pour une saisie, écrit d'après les règles de test_saisie.py et
# indépendant du parser (il a son propre découpage). Le fuzz compare le parser à l'oracle.
#
# Lecture de gauche à droite, le premier défaut rencontré l'emporte. Quand plusieurs défauts
# tombent sur le même élément, l'ordre est celui des contrôles ci-dessous : caractère invalide,
# `-+`, `^+` et `*+`, paire `++` ou `--`, puis le défaut propre à l'élément, puis inconnue
# multiple ou second signe égal.

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


def letter(char):
    return char.isascii() and char.isalpha()


def operand(char):
    return letter(char) or (char != "" and char in "0123456789.")


def starts_operand(text):
    return (
        letter(text[:1])
        or (text[:1] != "" and text[:1] in "0123456789")
        or (text[:1] == "." and text[1:2] != "" and text[1:2] in "0123456789")
    )


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
    exponent_signs = 0  # '-' lus depuis le dernier '^'
    previous_text = ""

    for match in ELEMENT.finditer(source):
        kind, text, at = match.lastgroup, match.group(), match.start()
        if kind == "blank":
            glued = False
            continue
        if kind == "invalid":
            return "CHR_02" if text == "." else "CHR_01"

        # Avant la paire : `-++x` est un `-+`, `x^++1` un `^+`, `3*++x` un `*+`, `1+ ++x` un
        # `+ +`, `1*--x` un `*--`.
        if text == "+" and previous in ("-", "+"):
            return "SEQ_01"
        if text == "+" and previous == "^":
            return "EXP_09" if glued else "EXP_01"
        if text == "+" and previous == "*":
            return "SEQ_01"
        # La première paire collée, lue de gauche à droite, est toujours un défaut.
        if text in "+-" and source[at + 1 : at + 2] == text:
            before = source[at - 1 : at] if at else ""
            after = source[at + 2 : at + 4]
            if before in ("+", "*") or (operand(before) and starts_operand(after)):
                return "SEQ_01"
            if text == "-" and in_exponent and exponent_signs >= 1:
                return "SEQ_01"
            if letter(before) or letter(after[:1]):
                return "VAR_02" if text == "+" else "VAR_03"
            return "SEQ_01"

        exponent_operand = False
        if kind == "number":
            if previous == "number":
                return "OPR_05"
            if in_exponent and "." in text:
                return "EXP_04"
            # Zéro à une puissance négative : bc s'arrête sur « divide by zero ».
            if in_exponent and zero_base and negative and float(text):
                return "EXP_06"
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
            if in_exponent:
                return "SEQ_01" if exponent_signs >= 2 else "EXP_01"
            if previous in "+-*":
                return "OPR_07"
            if equals:
                return "EQL_03"
            equals = True
        elif text == "+":
            if previous in ("start", "="):
                # Le défaut dépend de ce qui suit : `+*`, `+^`, `+ =`, `+.`.
                following = source[at + 1 :].lstrip(" \t")
                if starts_operand(following):
                    return "SGN_04"
                if following[:1] in ("+", "-"):
                    return "SEQ_01"
        elif text == "-":
            if in_exponent and exponent_signs >= 2:
                return "SEQ_01"
        elif text == "*":
            if previous == "^":
                return "EXP_09" if glued else "EXP_01"
            if previous in ("start", "="):
                return "OPR_01"
            if previous in "+-*":
                return "SEQ_01"
        elif text == "^":
            if previous in ("start", "="):
                return "EXP_02"
            if previous == "^":
                return "EXP_07"
            if previous in "+-*":
                return "EXP_08"
            if after_exponent:
                return "EXP_05"

        if text == "^":
            zero_base, negative = previous == "number" and not float(previous_text), False
            exponent_signs = 0
        elif in_exponent and text == "-":
            negative = not negative
            exponent_signs += 1
        in_exponent = text == "^" or (in_exponent and text == "-")
        after_exponent = exponent_operand
        previous_text = text
        previous = "number" if kind == "number" else "unknown" if kind == "unknown" else text
        glued = True

    if previous == "start":
        return "EQL_04"
    if previous == "=":
        return "EQL_02"
    if in_exponent:
        return "SEQ_01" if exponent_signs >= 2 else "EXP_01"
    if previous in "+-*":
        return "OPR_07"
    if not equals:
        return "EQL_04"
    return None
