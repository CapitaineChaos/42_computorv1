# Author    : CLAUDE OPUS 5.5
# Maintener : CLAUDE OPUS 5.5

# Saisie seule : acceptée ou refusée, et avec quel code. Ni forme réduite, ni discriminant,
# ni solutions ici, voir test_resolution.py.
#
# Référence : bc, l'inconnue tenant lieu de variable. Chaque côté de l'équation doit être
# une expression que bc accepte. bc refuse :
#   - deux nombres côte à côte : `2 3`, `1.2.3`
#   - un opérateur sans opérande : `x * = 1`, `^2 = x`
#   - zéro à une puissance négative : `0^-1`, divide by zero
#
# Blancs significatifs seulement dans un nombre.
#
# Écarts à bc :
#   - parenthèses et division refusées (CHR_01)
#   - signes `+` et `-` unaires acceptés partout où un opérande est attendu, seuls ou
#     répétés, collés ou séparés : `+1`, `3 * +-x`, `1--1`, `x = ---1`. bc refuse le `+`
#     unaire et lit `--` comme un décrément. Seule exception : derrière `^` (EXP_14).
#   - multiplication implicite acceptée, le nombre devant l'inconnue : `3x`, `3 x`, `xx` ;
#     un nombre derrière l'inconnue est refusé (`x3`, `2x3`, NBR_02)
#   - exposants chaînés refusés : `2^3^2`, `x^2^3` (`9^9^9` incalculable)
#   - refusés parce qu'un polynôme l'exige : une seconde inconnue, la casse comptant
#     (`x = X`), un exposant non entier (`x^1.5`, que bc tronque avec un avertissement)
#     ou contenant l'inconnue (`2^x`), un exposant signé (`x^-1`, `x^+2`, EXP_14), ce qui
#     rend zéro à une puissance négative impossible à écrire.
#
# Le code attendu est celui du premier défaut lu de gauche à droite : `x^1.5 + y` est un
# EXP_04, pas un VAR_01, et `x^-1.5` un EXP_14. Sur un même élément : VAR_01 avant EXP_03.
# Là où un opérande est attendu :
#   - `*` : EXP_14 derrière `^`, OPR_01 ailleurs ;
#   - `^` : EXP_07 après `^`, EXP_02 après `+`, `-`, `*` ou en tête de membre ;
#   - `+` ou `-` : EXP_14 derrière `^`, accepté ailleurs ;
#   - `=` ou la fin : EXP_01 après `^` ; VAL_01 devant `=` après un opérateur précédé d'un
#     opérande ; OPR_02 dans les autres cas d'opérateur ; EQL_0x après `=` ou en début de
#     saisie, avant EQL_04 : `x +` est un OPR_02.
#
#   CHR_01    caractère inconnu
#   CHR_02    point sans chiffre
#   OPR_01    '*' sans opérande devant : en tête de membre, derrière un signe ou un '*'
#   OPR_02    pas d'opérande après un opérateur : en fin de saisie, ou après un signe
#   VAL_01    opérateur suivi de '=', après un opérande
#   OPR_10    opérateur seul à gauche de '='
#   OPR_11    opérateur seul à droite de '='
#   EXP_01    pas d'opérande après '^'
#   EXP_02    pas de base avant '^' : en tête de membre ou derrière '+', '-' ou '*'
#   EXP_03    inconnue en exposant
#   EXP_04    exposant non entier
#   EXP_07    '^' derrière '^'
#   EXP_10    exposants chaînés
#   EXP_14    '+', '-' ou '*' derrière '^'
#   NBR_01    deux nombres sans opérateur
#   NBR_02    nombre derrière l'inconnue
#   VAR_01    seconde inconnue
#   EQL_01    côté gauche vide
#   EQL_02    côté droit vide
#   EQL_03    second '='
#   EQL_04    pas de '='
#   EMP_01    saisie vide ou blanche
#   LEN_01    plus de MAX_LEN caractères, prioritaire sur tout autre défaut

import io
import re
import sys
import traceback
import unittest
from contextlib import redirect_stdout
from itertools import product
from os.path import abspath, dirname, join, relpath

ROOT = dirname(dirname(abspath(__file__)))
sys.path.insert(0, ROOT)

import tests.common  # noqa: E402, F401
from computorv1.errors import ComputorErr  # noqa: E402
from computorv1.parser import MAX_LEN, parse  # noqa: E402

# unittest masque la pile des modules qui définissent __unittest : un échec n'affiche que
# le tableau des écarts.
__unittest = True


# Code du refus, None si la saisie est acceptée. Toute autre exception est un plantage :
# elle sortirait en « internal error » au lieu d'un message.
def verdict(source):
    try:
        with redirect_stdout(io.StringIO()):
            parse(source)
    except ComputorErr as error:
        return error.code
    except Exception as error:
        return crash(error)
    return None


# Situé à la dernière ligne exécutée du paquet, pas dans la bibliothèque standard.
def crash(error):
    frames = traceback.extract_tb(error.__traceback__)
    package = [frame for frame in frames if frame.filename.startswith(join(ROOT, "computorv1"))]
    frame = (package or frames)[-1]
    where = f"{relpath(frame.filename, ROOT)}:{frame.lineno}"
    return f"plantage {type(error).__name__} {where} {error}"


# Attendu « refusé, peu importe le code » : pour les bizarreries, seul compte le refus.
REJECTED = "refusé"


def conforms(got, expected):
    if expected == REJECTED:
        return got is not None and not got.startswith("plantage")
    return got == expected


# Saisie affichée tronquée au-delà de 44 caractères, avec sa longueur.
def shown(source):
    text = repr(source)
    return text if len(text) <= 44 else f"{text[:32]}… ({len(source)} car.)"


NUMBER_CHARS = "0123456789."


# pieces[i] : (blancs, caractère). Le blanc testé est celui de pieces[i].
def significant(pieces, i):
    left, right = pieces[i - 1][1], pieces[i][1]
    return left in NUMBER_CHARS and right in NUMBER_CHARS


# Au-delà de MAX_LEN, LEN_01 masquerait le défaut testé.
def respaced(source):
    pieces = re.findall(r"([ \t]*)([^ \t])", source)
    if not pieces or len(source) > MAX_LEN:
        return []
    compact, spaced = pieces[0][1], " " + pieces[0][1]
    for i in range(1, len(pieces)):
        blank, right = pieces[i]
        kept = significant(pieces, i)
        compact += (blank if kept else "") + right
        spaced += (blank if kept else " ") + right
    spaced += " "
    return [form for form in sorted({compact, spaced} - {source}) if len(form) <= MAX_LEN]


class Input(unittest.TestCase):
    # Passe toutes les saisies avant d'échouer, pour lister chaque écart avec le code obtenu
    # et le code attendu. Une variante n'est listée que si son verdict diffère de l'original.
    def check(self, cases):
        seen, lines = set(), []
        for source, expected in cases:
            original = verdict(source)
            for form in [source, *respaced(source)]:
                if form in seen:
                    continue
                seen.add(form)
                got = original if form == source else verdict(form)
                if not conforms(got, expected) and (form == source or got != original):
                    lines.append(
                        f"  {shown(form):44} obtenu {got or 'accepté':20}"
                        f" attendu {expected or 'accepté'}"
                    )
        if lines:
            self.fail(f"{len(lines)} saisies sur {len(seen)}\n" + "\n".join(lines))

    def accepted(self, sources):
        self.check([(source, None) for source in sources])

    def rejected(self, sources):
        self.check([(source, REJECTED) for source in sources])

    def refused(self, code, sources):
        self.check([(source, code) for source in sources])


class Accepted(Input):
    def test_subject(self):
        """Formes du sujet."""
        self.accepted(["5 * X^0 + 4 * X^1 - 9.3 * X^2 = 1 * X^0", "5 + 4 * X + X^2= X^2"])

    def test_signs(self):
        """'+' et '-' unaires, seuls ou répétés, collés ou séparés, partout où un opérande
        est attendu."""
        self.accepted(
            [
                "-x = 1",
                "+x = 1",
                "x = -1",
                "x = +1",
                "x - -2 = 0",
                "x+-1 = 0",
                "1-+x = 0",
                "1 + +x = 0",
                "1++1 = x",
                "1--1 = x",
                "x--x = 0",
                "x++2 = 0",
                "1.--.5 = x",
                "1 + -3 * x = 0",
                "3 * -x = 1",
                "3 * +x = 1",
                "3*--x = 1",
                "3 * ++x = 1",
                "x = --1",
                "++x = 1",
                "---x = 1",
                "+-+-1 = x",
                "x = 1 - --1",
                "x+++1 = 0",
            ]
        )

    def test_exponents(self):
        """Exposants entiers positifs, sans signe."""
        self.accepted(
            [
                "x^2 = 4",
                "x ^ 2 = 4",
                "x^02 = 4",
                "x^0 * 8 = 2 * x",
                "2.5^2 = x",
                "-2^2 + x = 0",
                "x^999999999999 = 1",
            ]
        )

    def test_implicit(self):
        """Multiplication implicite, avec ou sans espace, le nombre devant l'inconnue."""
        self.accepted(
            [
                "3x = 1",
                "3 x = 1",
                "xx = 1",
                "x x = 1",
                "2x^2 = 1",
                "x^2x = 1",
                "X^1X^1 = 4",
                "3.1^2x^2 = 0",
            ]
        )

    def test_numbers(self):
        """Décimaux sans partie entière ou sans décimales."""
        self.accepted([".5 * x = 5.", "0.5 * x = 05", "x = 0.000000001"])

    def test_unknown(self):
        """N'importe quelle lettre, ou aucune."""
        self.accepted(["y^2 = 4", "B^2 = B", "x * x = 4", "0 = 0", "1 = 2"])

    def test_spacing(self):
        """Espaces et tabulations partout, ou nulle part."""
        self.accepted(["x=1", "  x  =  1  ", "\tx\t=\t1", "2*x^2-x=0"])

    def test_zero_powers(self):
        """Puissances de zéro."""
        self.accepted(["0^0 = x", "0^00 = x", "0^2 = x", "0x^2 = 1"])

    def test_max_length(self):
        """Exactement MAX_LEN caractères."""
        self.accepted(["x = " + "1" * (MAX_LEN - 4)])


# Une situation de rejet par groupe, essayée à chaque place où elle peut se produire : en tête
# de membre, après '=', après chaque opérateur, devant '=' ou en fin de saisie.
class Refused(Input):
    def test_invalid_character(self):
        """Caractère invalide, retour à la ligne et sosies Unicode d'opérateurs compris."""
        self.refused(
            "CHR_01",
            [
                "x % 2 = 0",
                "(x + 1) = 0",
                "2/3 * x = 1",
                "x = 1,5",
                "3x² = 1",
                "x⁻¹ = 1",
                "x − 1 = 0",
                "2 × x = 1",
                "é = 1",
                "x� = 0",
                "x=1\x00",
                "x\n= 1",
                "x = 1\n",
                "x\r= 1",
                "x = 1",
            ],
        )

    def test_lone_point(self):
        """Point sans chiffre."""
        self.refused("CHR_02", ["2.5. = x", "..5 = x", ". = x"])

    def test_missing_left_operand(self):
        """Opérande gauche manquant : '*' ou '^' en tête de membre ou derrière un opérateur."""
        self.check(
            [
                ("*x = 1", "OPR_01"),
                ("* x = 1", "OPR_01"),
                ("x = * 2", "OPR_01"),
                ("x + * 2 = 0", "OPR_01"),
                ("x - * 2 = 0", "OPR_01"),
                ("3 * * x = 1", "OPR_01"),
                ("4**2 = x", "OPR_01"),
                ("x^*2 = 0", "EXP_14"),
                ("x ^ *2 = 0", "EXP_14"),
                ("^2 = x", "EXP_02"),
                ("^ 1 = 0", "EXP_02"),
                ("x = ^2", "EXP_02"),
                ("x +^2 = 0", "EXP_02"),
                ("3x-^2 = 0", "EXP_02"),
                ("4*^2 = x", "EXP_02"),
                ("x^-^2 = 0", "EXP_14"),
                ("x^+^2 = 0", "EXP_14"),
                ("--^2 = x", "EXP_02"),
                ("++*x = 1", "OPR_01"),
                ("x^^2 = 0", "EXP_07"),
                ("**x = 1", "OPR_01"),
                ("*+x = 1", "OPR_01"),
                ("*-1 = x", "OPR_01"),
                ("x = **2", "OPR_01"),
                ("x = *-2", "OPR_01"),
            ]
        )

    def test_missing_right_operand(self):
        """Opérande droit manquant : opérateur suivi de '=' ou de la fin de saisie."""
        self.check(
            [
                ("x + = 0", "VAL_01"),
                ("x - = 0", "VAL_01"),
                ("x * = 0", "VAL_01"),
                ("x^ = 1", "EXP_01"),
                ("1 ^ = 0", "EXP_01"),
                ("x = 1 +", "OPR_02"),
                ("x = 1 -", "OPR_02"),
                ("x = 1 *", "OPR_02"),
                ("x = 2^", "EXP_01"),
                ("x^- = 1", "EXP_14"),
                ("x = 2^-", "EXP_14"),
                ("x^+ = 1", "EXP_14"),
                ("x^- - = 1", "EXP_14"),
                ("x = x^+-", "EXP_14"),
                ("x = 1 + = 2", "VAL_01"),
                ("x++ = 1", "OPR_02"),
                ("x-- = 1", "OPR_02"),
                ("2 * x++ = 0", "OPR_02"),
                ("x = 1*+", "OPR_02"),
                ("x = 1 + +", "OPR_02"),
                ("-- = 0", "OPR_02"),
            ]
        )

    def test_juxtaposed_numbers(self):
        """Deux nombres sans opérateur entre eux."""
        self.refused("NBR_01", ["2 3 = x", "X^1 0 = 1", "2..5 = x", "1.2.3 = x"])

    def test_number_after_unknown(self):
        """Nombre derrière l'inconnue, collé ou séparé."""
        self.refused("NBR_02", ["x3 = 6", "X.5 = 1", "x2^3 = 1", "2x3 = 1", "x2 = 1", "x = 2x 3"])

    def test_empty_side(self):
        """Membre vide, à gauche ou à droite de '='."""
        self.check(
            [
                ("= x", "EQL_01"),
                ("= 1 * X^0", "EQL_01"),
                ("x =", "EQL_02"),
                ("x =   ", "EQL_02"),
            ]
        )

    def test_several_equals(self):
        """Plusieurs '='."""
        self.refused("EQL_03", ["x = 1 = 2", "x == 1", "x = = 1"])

    def test_no_equals(self):
        """Pas de '='."""
        self.refused("EQL_04", ["5 * X^0", "x"])

    def test_empty_input(self):
        """Saisie vide ou blanche."""
        self.refused("EMP_01", ["", "   ", "\t"])

    def test_non_integer_exponent(self):
        """Exposant écrit en décimal, même entier, que bc tronque avec un avertissement."""
        self.refused(
            "EXP_04",
            [
                "x^1.5 = 0",
                "2^0.5 = x",
                "x^.5 = 1",
                "x^2.0 = 4",
                "x^2. = 4",
            ],
        )

    def test_unknown_in_exponent(self):
        """Inconnue en exposant."""
        self.refused("EXP_03", ["2^x = 4", "x^x = 1", "1^X = 0"])

    def test_chained_exponents(self):
        """Exposants chaînés : a^b^c."""
        self.refused(
            "EXP_10",
            [
                "x^2^3 = 0",
                "x ^ 2 ^ 3 = 0",
                "2^3^2 = x",
                "9^9^9 = x",
                "0.5^9^9^9^9 = x",
                "x^2^ = 0",
            ],
        )

    def test_several_unknowns(self):
        """Plusieurs inconnues, la casse compte."""
        self.refused("VAR_01", ["x + y = 0", "x^2 = X", "x * y = 1", "a * X^0 + b * X^1 = 0"])

    def test_too_long(self):
        """Plus de MAX_LEN caractères, refusé avant tout autre défaut."""
        self.check(
            [
                ("x = " + "1" * (MAX_LEN - 3), "LEN_01"),
                ("(" * (MAX_LEN + 1), "LEN_01"),
                ("+" * (MAX_LEN + 1), "LEN_01"),
            ]
        )

    def test_signed_exponent(self):
        """Signe derrière '^', refusé avant ce qui suit : zéro à une puissance négative,
        exposant décimal, inconnue ou chaîné."""
        self.refused(
            "EXP_14",
            [
                "x^-1 = 0",
                "x^+2 = 1",
                "x^ -2 = 1",
                "x^--2 = 1",
                "x^+-1 = 0",
                "3x^-2 = 0",
                "x^-2x = 1",
                "1 * X^-1 + 1 * X^0 = 0",
                "0^-1 = x",
                "x = 0^-2",
                "0.0^-1 = x",
                ".0^-1 = x",
                "00^-01 = x",
                "-0^-1 = x",
                "x * 0^-1 = 1",
                "0^-0 = x",
                "0^+-1 = x",
                "0^---1 = x",
                "x^-1.5 = 0",
                "x^ - 2.5 = 0",
                "2^-x = 4",
                "x^-2^3 = 0",
            ],
        )

    def test_priority(self):
        """Deux défauts : le premier lu l'emporte."""
        self.check(
            [
                ("2 3 = x + y", "NBR_01"),
                ("x + y = 2 3", "VAR_01"),
                ("x^1.5 = y", "EXP_04"),
                ("y = x^1.5", "VAR_01"),
                ("x % 2 = y", "CHR_01"),
                ("x + y = 2 % 3", "VAR_01"),
                ("x = 1 = %", "EQL_03"),
                ("x = 1 % = 2", "CHR_01"),
                ("x++ = y", "OPR_02"),
                ("x = y++", "VAR_01"),
                ("x^2^y = 1", "EXP_10"),
                ("2^x^2 = 1", "EXP_03"),
                ("0^-1^2 = x", "EXP_14"),
                ("x + = = 1", "VAL_01"),
                ("x = x^ = 1", "EXP_01"),
                ("= = x", "EQL_01"),
                ("x = =", "EQL_03"),
            ]
        )

    def test_same_element(self):
        """Deux défauts sur un même élément ou en fin de saisie."""
        self.check(
            [
                ("x = 2^y", "VAR_01"),
                ("x = 2^-y", "EXP_14"),
                ("0^-1.5 = x", "EXP_14"),
                ("x +", "OPR_02"),
                ("x *", "OPR_02"),
                ("x^", "EXP_01"),
                ("x^-", "EXP_14"),
                ("x", "EQL_04"),
            ]
        )

    def test_orphan(self):
        """Opérateur seul entre le début ou '=' et '=' ou la fin."""
        self.check(
            [
                ("+ = 1", "OPR_10"),
                ("- = 1", "OPR_10"),
                ("* = 1", "OPR_10"),
                ("x = +", "OPR_11"),
                ("x = -", "OPR_11"),
                ("x = *", "OPR_11"),
                ("x = + = 1", "OPR_02"),
                ("+", "OPR_02"),
                ("-", "OPR_02"),
                ("^ = 1", "EXP_13"),
                ("x = ^", "EXP_13"),
            ]
        )

    def test_current_before_next(self):
        """Défaut d'un élément suivi d'un défaut sur l'élément d'après : le premier l'emporte."""
        self.check(
            [
                ("2^x3 = 1", "EXP_03"),
                ("2^.5 0 = x", "EXP_04"),
                ("2^3.5% = x", "EXP_04"),
                ("x^x) = 1", "EXP_03"),
                ("*^2 = x", "OPR_01"),
                ("x = *^2", "OPR_01"),
                ("*(x) = 1", "OPR_01"),
            ]
        )

    def test_lone_point_after_defect(self):
        """Point sans chiffre placé après un premier défaut : le premier défaut l'emporte."""
        self.check(
            [
                ("=. x", "EQL_01"),
                ("x == .", "EQL_03"),
                ("xy. = 1", "VAR_01"),
                (".1.1. = x", "NBR_01"),
                ("x.5. = 1", "NBR_02"),
                ("x^-. = 1", "EXP_14"),
                ("x^^. = 1", "EXP_07"),
                ("x^= .", "EXP_01"),
                ("x^1^. = 1", "EXP_10"),
                ("2^.5. = x", "EXP_04"),
                ("2^x. = 1", "EXP_03"),
                ("x +^. = 1", "EXP_02"),
                ("*. = 1", "OPR_01"),
                ("+ = .", "OPR_10"),
                ("x + = .", "VAL_01"),
                ("++ = .", "OPR_02"),
                ("% = 1.2.", "CHR_01"),
            ]
        )

    def test_fuzz(self):
        """Écarts trouvés par le fuzz, réduits."""
        self.check(
            [
                ("+*x = 1", "OPR_01"),
                ("+^2 = x", "EXP_02"),
                ("+. = x", "CHR_02"),
                ("x = 1*+", "OPR_02"),
                ("1*+*x = 0", "OPR_01"),
                ("1*+^2 = x", "EXP_02"),
                ("1*+. = x", "CHR_02"),
                ("x = 1*+-1", None),
                ("x = 1*+-+1", None),
                ("x*+-y = 0", "VAR_01"),
                ("++*x = 1", "OPR_01"),
                ("--*x = 1", "OPR_01"),
                ("++^2 = x", "EXP_02"),
                ("--^2 = x", "EXP_02"),
                ("1++ = x", "OPR_02"),
                ("1++. = x", "CHR_02"),
                ("x = 1+ +", "OPR_02"),
                ("+ +. = x", "CHR_02"),
                ("+ +-1 = x", None),
                ("x = 1 + + -1", None),
                ("x = 2+-- 7", None),
                ("x*-- 1 = 0", None),
                ("1+++x = 0", None),
                ("+ ++x = 1", None),
                ("x^- - = 1", "EXP_14"),
                ("x = x^- -", "EXP_14"),
                ("x^- - 2.5 = 1", "EXP_14"),
                ("x^- -x = 1", "EXP_14"),
                ("x^- -2^3 = 1", "EXP_14"),
                ("x^- - -2 = 1", "EXP_14"),
                ("x^- --x = 1", "EXP_14"),
                ("x^- - -2.5 = 1", "EXP_14"),
                ("x^- - -x = 1", "EXP_14"),
                ("x^- - -2^3 = 1", "EXP_14"),
                ("0^- - -1 = x", "EXP_14"),
                ("x^- - - = 1", "EXP_14"),
                ("x = x^- - -", "EXP_14"),
            ]
        )


# Bizarreries : ce qu'un utilisateur peut taper de travers, classé par nature de l'anomalie et
# non par code d'erreur. Seul compte le verdict, accepté ou refusé, quel que soit le code :
# une bizarrerie qu'aucun code ne couvre encore doit quand même être refusée.
class Oddities(Input):
    def test_control_characters(self):
        """Caractères de contrôle : retour à la ligne, retour chariot, nul, échappement."""
        self.rejected(
            [
                "x\n= 1",
                "x = 1\n",
                "\nx = 1",
                "x\r\n= 1",
                "x\0 = 1",
                "x\x1b[31m = 1",
                "x\v= 1",
                "x\f= 1",
                "x\x7f = 1",
            ]
        )

    def test_exotic_blanks(self):
        """Blancs exotiques : espace insécable, espaces Unicode, largeur nulle, BOM."""
        self.rejected(["x = 1", "x = 1", "x​= 1", "x　= 1", "﻿x = 1"])

    def test_unicode_lookalikes(self):
        """Sosies Unicode d'opérateurs, de chiffres et de lettres."""
        self.rejected(
            [
                "x − 1 = 0",
                "2 × x = 1",
                "2 · x = 1",
                "x ＝ 1",
                "x = １",
                "x² = 1",
                "x⁻¹ = 1",
                "x = ½",
                "x = ٣",
                "ｘ = 1",
            ]
        )

    def test_non_ascii_letters(self):
        """Lettres hors ASCII."""
        self.rejected(["é = 1", "π = 3", "ß = 1", "x = π", "Ω^2 = 1"])

    def test_punctuation(self):
        """Ponctuation et symboles étrangers à la grammaire."""
        self.rejected(
            [
                "(x) = 1",
                "[x] = 1",
                "{x} = 1",
                "|x| = 1",
                "x / 2 = 1",
                "x % 2 = 0",
                "x! = 1",
                "x, = 1",
                "x = 1;",
                "x : 1",
                "x = 1 # commentaire",
                "x = '1'",
                'x = "1"',
                "x & 1 = 0",
                "x ~ 1",
                "x = $1",
                "x @ 1 = 0",
                "x = 1\\",
                "x_1 = 0",
                "x = 1`",
            ]
        )

    def test_foreign_operators(self):
        """Opérateurs d'autres langages : puissance, comparaison, affectation."""
        self.rejected(
            [
                "x ** 2 = 1",
                "x // 2 = 1",
                "x == 1",
                "x != 1",
                "x <= 1",
                "x >= 1",
                "x < 1",
                "x > 1",
                "x := 1",
                "x += 1",
                "x -= 1",
                "x *= 1",
                "x ^= 1",
                "x -> 1",
                "x => 1",
            ]
        )

    def test_malformed_numbers(self):
        """Nombres mal formés : points en trop, séparateurs de milliers, autres bases."""
        self.rejected(
            [
                "1..2 = x",
                "1.2.3 = x",
                ". = x",
                ".. = x",
                "x = 1.2.",
                "1 000 = x",
                "1_000 = x",
                "1,5 = x",
                "1'000 = x",
                "2 .5 = x",
                "inf = x",
                "nan = x",
            ]
        )

    def test_unusual_valid_numbers(self):
        """Nombres inhabituels mais valides : sans partie entière, sans décimales, zéros."""
        self.accepted(["x = 1.", "x = .5", "x = 007", "x = 0.0", "x = -0", "x = 000.000"])

    def test_huge_numbers(self):
        """Nombres démesurés : centaines de chiffres, décimales minuscules."""
        self.check(
            [
                ("x = " + "9" * 196, None),
                ("x = 0." + "0" * 193 + "1", None),
                ("x^" + "9" * 50 + " = 1", None),
                ("9" * 192 + " * x = 1", None),
                ("2^9999 = x", None),
                ("x = " + "9" * 500, "LEN_01"),
                ("x = 0." + "0" * 500 + "1", "LEN_01"),
                ("9" * 500 + " * x = 1", "LEN_01"),
            ]
        )

    def test_unknown_names(self):
        """Noms d'inconnue : plusieurs lettres, casse différente, lettres collées."""
        self.rejected(["xy = 1", "x = X", "ab = 1", "x2y = 1", "x = 1 + y", "Xx = 1"])

    def test_single_unknown_forms(self):
        """Une seule inconnue sous des formes inhabituelles : répétée, collée, majuscule."""
        self.accepted(["xx = 1", "x x = 1", "X = 1", "z = 1"])

    def test_consecutive_operators(self):
        """Deux opérateurs de suite."""
        cases = []
        for first in "+-*^":
            for second in "+-*^":
                for before, gap, after in product(("", " "), repeat=3):
                    source = f"2{before}{first}{gap}{second}{after}1 = x"
                    # Seul un signe peut suivre un opérateur, sauf '^'.
                    valid = second in "+-" and first != "^"
                    cases.append((source, None if valid else REJECTED))
        self.check(cases)

    def test_repeated_signs(self):
        """Signes répétés, collés ou séparés."""
        self.accepted(
            [
                "- - - x = 1",
                "x = - - - 1",
                "-x = -1",
                "---x = 1",
                "x = ---1",
                "+-+-1 = x",
                "x = -+1",
                "x = +-1",
                "x = - + 1",
            ]
        )

    def test_operator_at_edges(self):
        """Opérateur en tête ou en fin de membre, pour chaque opérateur et chaque membre."""
        cases = []
        for op in "+-*^":
            cases.append((f"{op} 1 = x", None if op in "+-" else REJECTED))
            cases.append((f"x = {op} 1", None if op in "+-" else REJECTED))
            cases.append((f"1 {op} = x", REJECTED))
            cases.append((f"x = 1 {op}", REJECTED))
        self.check(cases)

    def test_juxtaposed_terms(self):
        """Termes juxtaposés : deux nombres sans opérateur, collés ou séparés."""
        self.rejected(["2 3 = x", "2\t3 = x", "x^2 3 = 1", "2.5.5 = x", "x = 1 2", "0.5 .5 = x"])

    def test_equation_structure(self):
        """Structure : signe égal absent, isolé ou multiple, membres vides ou blancs."""
        self.rejected(
            [
                "",
                " ",
                "\t",
                "x",
                "=",
                "==",
                "= =",
                " = ",
                "x =",
                "= x",
                "x =\t",
                "x = = 1",
                "x = 1 = 2",
                "x = 1 = ",
            ]
        )

    def test_trivial_equations(self):
        """Équations triviales, valides à la lecture : sans inconnue, identiques, x = x."""
        self.accepted(["0 = 0", "1 = 2", "x = x", "x^2 = x^2", "0 * x = 0"])

    def test_exponent_oddities(self):
        """Exposants : décimal, négatif, signé, inconnue, chaîné, vide, doublé."""
        self.rejected(
            [
                "x^1.5 = 1",
                "x^-1.5 = 1",
                "x^.5 = 1",
                "x^2. = 1",
                "x^-1 = 1",
                "x^+2 = 1",
                "x^--2 = 1",
                "x^x = 1",
                "2^x = 1",
                "x^-x = 1",
                "x^2^3 = 1",
                "x^ = 1",
                "x = x^",
                "x^ - = 1",
                "x^^2 = 1",
                "x^*2 = 1",
            ]
        )

    def test_unusual_valid_exponents(self):
        """Exposants inhabituels mais valides : nul, espacé, zéros en tête."""
        self.accepted(["x^0 = 1", "x ^ 2 = 1", "x^ 2 = 1", "x^00 = 1", "x^2x = 1"])

    def test_long_inputs(self):
        """Saisies très longues : milliers de termes, de blancs ou de signes."""
        self.refused(
            "LEN_01",
            [
                "x = " + " + ".join(["1"] * 10_000),
                "x" + " " * 100_000 + "= 1",
                "x = " + "- " * 10_000 + "1",
                "x = " + "+" * 10_000 + "1",
                "x = 1" + " + " * 10_000,
            ],
        )


if __name__ == "__main__":
    unittest.main()
