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
#   - parenthèses et division refusées (INP_02)
#   - signes `+` et `-` unaires acceptés partout où un opérande est attendu, seuls ou
#     répétés, collés ou séparés : `+1`, `3 * +-x`, `1--1`, `x = ---1`. bc refuse le `+`
#     unaire et lit `--` comme un décrément. Seule exception : derrière `^` (POW_01).
#   - multiplication implicite acceptée, le nombre devant l'inconnue : `3x`, `3 x`, `xx` ;
#     un nombre derrière l'inconnue est refusé (`x3`, `2x3`, OPR_07)
#   - exposants chaînés refusés : `2^3^2`, `x^2^3` (`9^9^9` incalculable)
#   - refusés parce qu'un polynôme l'exige : une seconde inconnue, la casse comptant
#     (`x = X`), un exposant non entier (`x^1.5`, que bc tronque avec un avertissement)
#     ou contenant l'inconnue (`2^x`), un exposant signé (`x^-1`, `x^+2`, POW_01), ce qui
#     rend zéro à une puissance négative impossible à écrire.
#
# Le code attendu est celui du premier défaut lu de gauche à droite : `x^1.5 + y` est un
# POW_06, pas un CPT_03, et `x^-1.5` un POW_01. Sur un même élément : POW_02 avant CPT_03.
# Un '*' ou un '^' en tête de saisie est jugé sur ce qui le suit : `*. = 1` est un INP_03, mais
# `x = *.` un OPR_05.
# Là où un opérande est attendu :
#   - `*` : POW_01 derrière `^`, OPR_06 en tête de saisie, OPR_05 derrière `=`, POW_09
#     devant `^`, OPR_01 ailleurs ;
#   - `^` : POW_07 après `^`, POW_04 après `+`, `-`, `*` ou en tête de membre ;
#   - `+` ou `-` : POW_01 derrière `^`, accepté ailleurs ;
#   - `=` : POW_01 après `^`, OPR_01 après un opérateur, EQL_01 en tête de saisie ;
#   - la fin : POW_03 après `^`, OPR_02 après un opérateur, EQL_02 après `=`.
# Signe seul dans un membre : OPR_03 ; `*` seul : OPR_06 ou OPR_05 selon le membre ; `^` seul :
# POW_04. Opérateur seul dans toute la saisie : OPR_04.
#
#   INP_02    caractère inconnu
#   INP_03    point sans chiffre
#   OPR_01    opérateur derrière un opérateur, ou suivi de '='
#   OPR_02    opérateur en fin de saisie
#   OPR_03    signe seul dans un membre
#   OPR_04    opérateur seul dans la saisie
#   OPR_05    '*' juste après '='
#   OPR_06    '*' en tête de saisie
#   OPR_07    deux nombres sans opérateur, nombre derrière l'inconnue, ou '**' après un opérande
#   POW_01    autre chose qu'une valeur après '^' : '=', '+', '-' ou '*'
#   POW_02    inconnue en exposant
#   POW_03    rien après '^'
#   POW_04    pas de base avant '^' : en tête de membre ou derrière '+', '-' ou '*'
#   POW_06    exposant non entier
#   POW_07    '^' derrière '^'
#   POW_08    exposants chaînés
#   POW_09    '*' en tête de membre devant '^'
#   CPT_03    seconde inconnue
#   EQL_01    côté gauche vide
#   EQL_02    côté droit vide
#   EQL_03    second '='
#   EQL_04    pas de '='
#   INP_01    saisie vide ou blanche
#   CPT_02    plus de MAX_LEN caractères, prioritaire sur tout autre défaut

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
from computorv1.errors import ComputorException  # noqa: E402
from computorv1.parser import MAX_LEN, Parser  # noqa: E402

# unittest masque la pile des modules qui définissent __unittest : un échec n'affiche que
# le tableau des écarts.
__unittest = True


# Code du refus, None si la saisie est acceptée. Toute autre exception est un plantage :
# elle sortirait en « internal error » au lieu d'un message.
def verdict(source):
    try:
        with redirect_stdout(io.StringIO()):
            Parser(source).equation()
    except ComputorException as error:
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


ACCEPTED = None

# Attendu « refusé, peu importe le code » : pour les bizarreries, seul compte le refus.
REJECTED = "refusé"

# Codes pas encore tranchés : saisie → question. L'attendu provisoire reste celui de son
# groupe ; make test_common affiche la question sur la ligne et en fin de sortie.
PENDING = {}


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


# Au-delà de MAX_LEN, CPT_02 masquerait le défaut testé.
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

    # (attendu, saisies) par bloc, en un seul check : un second check ne s'exécuterait pas
    # après l'échec du premier.
    def expect(self, *blocks):
        self.check([(source, expected) for expected, sources in blocks for source in sources])


# Une classe par sujet, un groupe par situation ; un groupe mêle saisies acceptées et refusées.
# Une saisie refusée est rangée au sujet de son code attendu, même quand elle porte un second
# défaut. REJECTED : bizarreries dont seul compte le refus.


class Equation(Input):
    def test_valid(self):
        """Équations valides : formes du sujet, triviales, espacées ou non."""
        self.accepted(
            [
                "5 * X^0 + 4 * X^1 - 9.3 * X^2 = 1 * X^0",
                "5 + 4 * X + X^2= X^2",
                "0 = 0",
                "1 = 2",
                "x = x",
                "x^2 = x^2",
                "0 * x = 0",
                "x=1",
                "  x  =  1  ",
                "\tx\t=\t1",
                "2*x^2-x=0",
            ]
        )

    def test_empty_input(self):
        """Saisie vide ou blanche."""
        self.refused("INP_01", ["", "   ", "\t", " "])

    def test_empty_side(self):
        """Membre vide, à gauche ou à droite de '='."""
        self.expect(
            ("EQL_01", ["= x", "= 1 * X^0", "= = x", "=. x", "=", "==", "= =", " = "]),
            ("EQL_02", ["x =", "x =   ", "x =\t"]),
        )

    def test_several_equals(self):
        """Plusieurs '=', collés ou séparés."""
        self.refused(
            "EQL_03", ["x = 1 = 2", "x == 1", "x = = 1", "x = 1 = %", "x = =", "x == .", "x = 1 = "]
        )

    def test_no_equals(self):
        """Pas de '='."""
        self.refused("EQL_04", ["5 * X^0", "x"])


class Characters(Input):
    def test_invalid_character(self):
        """Caractère hors grammaire, retour à la ligne et sosies Unicode d'opérateurs compris."""
        self.refused(
            "INP_02",
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
                "x % 2 = y",
                "x = 1 % = 2",
                "% = 1.2.",
                "x^% = 1",
                "x^(2) = 1",
            ],
        )

    def test_lone_point(self):
        """Point sans chiffre, derrière des signes compris."""
        self.refused(
            "INP_03",
            [
                "2.5. = x",
                "..5 = x",
                ". = x",
                "+. = x",
                "1*+. = x",
                "1++. = x",
                "+ +. = x",
                "x^. = 1",
            ],
        )

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


class Numbers(Input):
    def test_valid(self):
        """Décimaux sans partie entière ou sans décimales, zéros, démesurés, à chaque place."""
        self.accepted(
            [
                ".5 * x = 5.",
                "0.5 * x = 05",
                "x = 0.000000001",
                "x = 1.",
                "x = .5",
                "x = 007",
                "x = 0.0",
                "x = -0",
                "x = 000.000",
                "x = " + "9" * 196,
                "x = 0." + "0" * 193 + "1",
                "9" * 192 + " * x = 1",
                "1. + x = 0",
                ".5 - x = 0",
                "-.5 = x",
                "x + 1.5 = 0",
                "x - .5 = 2.",
                "x * 2. = 3.0",
                "x = 1.5 * x",
                "x = -1.5 + x",
                "x^2 = 0.25",
                "1.5x = 3",
                ".5x = 1",
                "2.x = 1",
            ]
        )

    def test_malformed(self):
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


class Juxtaposition(Input):
    def test_implicit(self):
        """Multiplication implicite, le nombre devant l'inconnue, à chaque place d'un terme."""
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
                "-3x = 1",
                "1 + 2x = 0",
                "1 - 3 x = 0",
                "2 * 3x = 1",
                "2x * 3 = 1",
                "2x + 3x = 1",
                "x = 3x",
                "x = -2x^2",
                "0 = 1 + 2x - x x",
                "3 x x = 1",
            ]
        )

    def test_numbers(self):
        """Deux nombres sans opérateur, collés ou séparés."""
        self.expect(
            (
                "OPR_07",
                ["2 3 = x", "X^1 0 = 1", "2..5 = x", "1.2.3 = x", "2 3 = x + y", ".1.1. = x"],
            ),
            (REJECTED, ["2\t3 = x", "x^2 3 = 1", "2.5.5 = x", "x = 1 2", "0.5 .5 = x"]),
        )

    def test_number_after_unknown(self):
        """Nombre derrière l'inconnue, collé ou séparé."""
        self.refused(
            "OPR_07",
            ["x3 = 6", "X.5 = 1", "x2^3 = 1", "2x3 = 1", "x2 = 1", "x = 2x 3", "x.5. = 1"],
        )


class Unknown(Input):
    def test_valid(self):
        """Une seule inconnue, n'importe quelle lettre, répétée, à chaque place d'un terme."""
        self.accepted(
            [
                "y^2 = 4",
                "B^2 = B",
                "x * x = 4",
                "xx = 1",
                "x x = 1",
                "X = 1",
                "z = 1",
                "1 = x",
                "1 + x = 0",
                "1 - x = 0",
                "2 * x = 1",
                "-x = 1",
                "x - -x = 1",
                "x + 1 = x",
                "x * 2 = x - 1",
                "x = 1 * x",
            ]
        )

    def test_several_unknowns(self):
        """Plusieurs inconnues, la casse comptant, lettres collées comprises."""
        self.expect(
            (
                "CPT_03",
                [
                    "x + y = 0",
                    "x^2 = X",
                    "x * y = 1",
                    "a * X^0 + b * X^1 = 0",
                    "x + y = 2 3",
                    "y = x^1.5",
                    "x + y = 2 % 3",
                    "x = y++",
                    "xy. = 1",
                    "x*+-y = 0",
                ],
            ),
            (REJECTED, ["xy = 1", "x = X", "ab = 1", "x2y = 1", "x = 1 + y", "Xx = 1"]),
        )


class Operators(Input):
    def test_signs(self):
        """'+' et '-' unaires, seuls ou répétés, collés ou séparés."""
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
                "- - - x = 1",
                "x = - - - 1",
                "-x = -1",
                "x = ---1",
                "x = -+1",
                "x = +-1",
                "x = - + 1",
                "x = 1*+-1",
                "x = 1*+-+1",
                "+ +-1 = x",
                "x = 1 + + -1",
                "x = 2+-- 7",
                "x*-- 1 = 0",
                "1+++x = 0",
                "+ ++x = 1",
            ]
        )

    def test_missing_left_operand(self):
        """'*' sans opérande devant : en tête de saisie, après '=', un signe ou un '*'.
        Un caractère invalide derrière le '*' est signalé avant l'opérande manquant."""
        self.expect(
            (
                "OPR_06",
                [
                    "*x = 1",
                    "* x = 1",
                    "**x = 1",
                    "*+x = 1",
                    "*-1 = x",
                ],
            ),
            ("INP_02", ["*(x) = 1"]),
            ("INP_03", ["*. = 1"]),
            ("OPR_05", ["x = * 2", "x = **2", "x = *-2", "x = *%", "x = *."]),
            (
                "OPR_01",
                [
                    "x + * 2 = 0",
                    "x - * 2 = 0",
                    "++*x = 1",
                    "+*x = 1",
                    "1*+*x = 0",
                    "--*x = 1",
                    "+**x = 1",
                    "1+**x = 1",
                    "x = -**2",
                    "x = 1 + * = 2",
                    "+*^2 = x",
                    "+*. = 1",
                    "+*% = 1",
                    "3 * * x = 1",
                    "4**2 = x",
                ],
            ),
        )

    def test_operator_before_equals(self):
        """Opérateur ou signe suivi de '=', après un opérande ou un autre signe."""
        self.refused(
            "OPR_01",
            [
                "x + = 0",
                "x - = 0",
                "x * = 0",
                "x = 1 + = 2",
                "x + = = 1",
                "x + = .",
                "x++ = 1",
                "x-- = 1",
                "2 * x++ = 0",
                "-- = 0",
                "x++ = y",
                "++ = .",
                "1++ = x",
            ],
        )

    def test_missing_right_operand(self):
        """Opérateur ou signe en fin de saisie."""
        self.refused(
            "OPR_02",
            ["x = 1 +", "x = 1 -", "x = 1 *", "x = 1*+", "x = 1 + +", "x +", "x *", "x = 1+ +"],
        )

    def test_orphan(self):
        """Opérateur seul entre le début ou '=' et '=' ou la fin."""
        self.expect(
            ("OPR_03", ["+ = 1", "- = 1", "+ = .", "x = +", "x = -"]),
            ("OPR_06", ["* = 1"]),
            ("OPR_05", ["x = *", "x = * = 1"]),
            ("OPR_01", ["x = + = 1"]),
            ("OPR_02", ["--"]),
            ("OPR_04", ["+", "-", "*"]),
        )

    def test_consecutive(self):
        """Deux opérateurs de suite, collés ou séparés : seul un signe peut suivre."""
        cases = []
        for first, second in product("+-*", repeat=2):
            for before, gap, after in product(("", " "), repeat=3):
                source = f"2{before}{first}{gap}{second}{after}1 = x"
                cases.append((source, ACCEPTED if second in "+-" else "OPR_01"))
        self.check(cases)

    def test_at_edges(self):
        """Opérateur en tête ou en fin de membre, pour chaque opérateur et chaque membre."""
        cases = []
        for op in "+-*":
            cases.append((f"{op} 1 = x", ACCEPTED if op in "+-" else "OPR_06"))
            cases.append((f"x = {op} 1", ACCEPTED if op in "+-" else "OPR_05"))
            cases.append((f"1 {op} = x", "OPR_01"))
            cases.append((f"x = 1 {op}", "OPR_02"))
        self.check(cases)

    def test_foreign_operators(self):
        """Opérateurs d'autres langages : puissance, comparaison, affectation."""
        self.check(
            [
                ("x ** 2 = 1", "OPR_01"),
                ("x // 2 = 1", "INP_02"),
                ("x == 1", "EQL_03"),
                ("x != 1", "INP_02"),
                ("x <= 1", "INP_02"),
                ("x >= 1", "INP_02"),
                ("x < 1", "INP_02"),
                ("x > 1", "INP_02"),
                ("x := 1", "INP_02"),
                ("x += 1", "OPR_01"),
                ("x -= 1", "OPR_01"),
                ("x *= 1", "OPR_01"),
                ("x ^= 1", "POW_01"),
                ("x -> 1", "INP_02"),
                ("x => 1", "INP_02"),
            ]
        )


class Exponent(Input):
    def test_valid(self):
        """Exposant entier sans signe, à chaque place d'un terme, suivi de chaque opérateur."""
        self.accepted(
            [
                "x^2 = 4",
                "x ^ 2 = 4",
                "x ^ 2 = 1",
                "x ^2 = 1",
                "x^ 2 = 1",
                "x^0 = 1",
                "x^1 = 1",
                "x^00 = 1",
                "x^02 = 4",
                "x^999999999999 = 1",
                "x^" + "9" * 50 + " = 1",
                "X^2 = 1",
                "2^9999 = x",
                "2.5^2 = x",
                ".5^2 = x",
                "2.^2 = x",
                "0^0 = x",
                "0^00 = x",
                "0^2 = x",
                "0x^2 = 1",
                "1 + x^2 = 0",
                "1 - x^2 = 0",
                "3 * x^2 = 1",
                "-x^2 = 1",
                "+x^2 = 1",
                "-2^2 + x = 0",
                "1 - -x^2 = 0",
                "3 * -x^2 = 1",
                "1 = x^2",
                "x = 2^3",
                "x = -x^2",
                "0 = 1 + x^2",
                "x = 3 * x^2 - 1",
                "x^2 + 1 = 0",
                "x^2 - 1 = 0",
                "x^2 * 3 = 1",
                "x^0 * 8 = 2 * x",
                "x^2x = 1",
                "x^2 x = 1",
                "x^2 x^3 = 1",
                "x^2 * x^3 = x^5",
                "x^2 + x^1 + x^0 = 0",
            ]
        )

    def test_missing_exponent(self):
        """Pas d'exposant après '^' : '=', '*' ou fin de saisie."""
        self.expect(
            ("POW_01", ["x^ = 1", "1 ^ = 0", "x = x^ = 1", "x^= .", "x^*2 = 0", "x ^ *2 = 0"]),
            ("POW_03", ["x = 2^", "x^"]),
        )

    def test_missing_base(self):
        """Pas de base avant '^' : en tête de membre, derrière un opérateur ; '^' seul."""
        self.expect(
            (
                "POW_04",
                [
                    "^2 = x",
                    "^ 1 = 0",
                    "x +^2 = 0",
                    "3x-^2 = 0",
                    "4*^2 = x",
                    "--^2 = x",
                    "x +^. = 1",
                    "+^2 = x",
                    "1*+^2 = x",
                    "++^2 = x",
                    "^",
                    "^ = 1",
                ],
            ),
            ("POW_05", ["x = ^2", "x = ^", "x = ^ = 1", "x = ^%", "x = ^."]),
            ("POW_09", ["*^2 = x", "x = *^2"]),
            ("INP_02", ["^% = 1"]),
            ("INP_03", ["^. = 1"]),
        )

    def test_signed_exponent(self):
        """Exposant précédé de signes : refusé sur le signe, avant ce qui suit."""
        self.refused(
            "POW_01",
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
                "x = 2^-y",
                "0^-1.5 = x",
                "0^-1^2 = x",
                "x^- - 2.5 = 1",
                "x^- -x = 1",
                "x^- -2^3 = 1",
                "x^- - -2 = 1",
                "x^- --x = 1",
                "x^- - -2.5 = 1",
                "x^- - -x = 1",
                "x^- - -2^3 = 1",
                "0^- - -1 = x",
            ],
        )

    def test_operator_after_caret(self):
        """Signes derrière '^' sans exposant ensuite."""
        self.refused(
            "POW_01",
            [
                "x^-^2 = 0",
                "x^+^2 = 0",
                "x^- = 1",
                "x = 2^-",
                "x^+ = 1",
                "x^- - = 1",
                "x = x^+-",
                "x^-",
                "x^-. = 1",
                "x = x^- -",
                "x^- - - = 1",
                "x = x^- - -",
            ],
        )

    def test_chained(self):
        """'^' derrière '^' ou derrière un exposant."""
        self.expect(
            ("POW_07", ["x^^2 = 0", "x^^. = 1"]),
            (
                "POW_08",
                [
                    "x^2^3 = 0",
                    "x ^ 2 ^ 3 = 0",
                    "2^3^2 = x",
                    "9^9^9 = x",
                    "0.5^9^9^9^9 = x",
                    "x^2^ = 0",
                    "x^2^y = 1",
                    "x^1^. = 1",
                ],
            ),
        )

    def test_non_integer_exponent(self):
        """Exposant écrit en décimal, même entier, que bc tronque avec un avertissement."""
        self.refused(
            "POW_06",
            [
                "x^1.5 = 0",
                "2^0.5 = x",
                "x^.5 = 1",
                "x^2.0 = 4",
                "x^2. = 4",
                "x^1.5 = y",
                "2^.5 0 = x",
                "2^3.5% = x",
                "2^.5. = x",
            ],
        )

    def test_unknown_in_exponent(self):
        """Inconnue en exposant."""
        self.refused(
            "POW_02",
            [
                "2^x = 4",
                "x^x = 1",
                "1^X = 0",
                "2^x^2 = 1",
                "2^x3 = 1",
                "x^x) = 1",
                "2^x. = 1",
                "x = 2^y",
            ],
        )

    def test_beside_operator(self):
        """'^' contre un autre opérateur, collés ou séparés, ou en bord de membre."""
        cases = []
        for first, second in product("+-*^", repeat=2):
            if "^" not in (first, second):
                continue
            code = "POW_07" if first == second else "POW_01" if first == "^" else "POW_04"
            for before, gap, after in product(("", " "), repeat=3):
                cases.append((f"2{before}{first}{gap}{second}{after}1 = x", code))
        cases += [
            ("^ 1 = x", "POW_04"),
            ("x = ^ 1", "POW_05"),
            ("1 ^ = x", "POW_01"),
            ("x = 1 ^", "POW_03"),
        ]
        self.check(cases)

    def test_oddities(self):
        """Exposants : décimal, négatif, signé, inconnue, chaîné, vide, doublé."""
        self.check(
            [
                ("x^1.5 = 1", "POW_06"),
                ("x^-1.5 = 1", "POW_01"),
                ("x^.5 = 1", "POW_06"),
                ("x^2. = 1", "POW_06"),
                ("x^-1 = 1", "POW_01"),
                ("x^+2 = 1", "POW_01"),
                ("x^--2 = 1", "POW_01"),
                ("x^x = 1", "POW_02"),
                ("2^x = 1", "POW_02"),
                ("x^-x = 1", "POW_01"),
                ("x^2^3 = 1", "POW_08"),
                ("x^ = 1", "POW_01"),
                ("x = x^", "POW_03"),
                ("x^ - = 1", "POW_01"),
                ("x^^2 = 1", "POW_07"),
                ("x^*2 = 1", "POW_01"),
            ]
        )


class Length(Input):
    def test_max_length(self):
        """MAX_LEN caractères au plus ; au-delà, CPT_02 avant tout autre défaut."""
        self.expect(
            (ACCEPTED, ["x = " + "1" * (MAX_LEN - 4)]),
            (
                "CPT_02",
                [
                    "x = " + "1" * (MAX_LEN - 3),
                    "(" * (MAX_LEN + 1),
                    "+" * (MAX_LEN + 1),
                    "x = " + "9" * 500,
                    "x = 0." + "0" * 500 + "1",
                    "9" * 500 + " * x = 1",
                    "x = " + " + ".join(["1"] * 10_000),
                    "x" + " " * 100_000 + "= 1",
                    "x = " + "- " * 10_000 + "1",
                    "x = " + "+" * 10_000 + "1",
                    "x = 1" + " + " * 10_000,
                ],
            ),
        )


if __name__ == "__main__":
    unittest.main()
