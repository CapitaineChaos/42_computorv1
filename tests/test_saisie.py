# Author    : CLAUDE OPUS 5.5
# Maintener : CLAUDE OPUS 5.5

# Saisie seule : acceptée ou refusée, et avec quel code. Ni forme réduite, ni discriminant,
# ni solutions ici, voir test_resolution.py.
#
# Référence : bc, l'inconnue tenant lieu de variable. Chaque côté de l'équation doit être
# une expression que bc accepte. bc refuse :
#   - deux nombres côte à côte : `2 3`, `1.2.3`
#   - le `+` unaire, partout : `+1`, `x = +1`, `1 - +x`, `x^+2`
#   - `--` collé, qu'il lit comme un décrément : `--x`, `x --1` ; `- -x` passe
#   - un opérateur sans opérande : `x * = 1`, `^2 = x`
# Il accepte le `-` unaire partout où un opérande est attendu : `3 * -x`, `2^-3`, `x - - 2`.
#
# Écarts à bc :
#   - parenthèses et division refusées (CHR_01)
#   - multiplication implicite acceptée : `3x`, `x3`, `3 x`, `xx`
#   - exposants chaînés refusés : `2^3^2`, `x^2^3`
#   - refusés parce qu'un polynôme l'exige : une seconde inconnue, la casse comptant
#     (`x = X`), un exposant non entier (`x^1.5`, que bc tronque avec un avertissement)
#     ou contenant l'inconnue (`2^x`). Les exposants négatifs (`x^-1`) sont acceptés.
#
# Le code attendu est celui du premier défaut lu de gauche à droite : `x^1.5 + y` est un
# EXP_04, pas un VAR_01. Là où un opérande est attendu :
#   - `+` : OPR_04 après `*` ou `^`, SGN_04 ailleurs ;
#   - `*` : MUL_01 après `*`, `+` ou `-`, OPR_01 ailleurs ;
#   - `^` : EXP_02 partout ;
#   - `-` : SGN_03 collé derrière un `-`, accepté ailleurs ;
#   - `++` ou `--` collé à l'inconnue, avant ou après : VAR_02 ou VAR_03, avant SGN_04
#     ou SGN_03.
#   - `=` ou la fin : EXP_01 après `^` ou son `-`, OPR_02 après un autre opérateur, EQL_0x
#     après `=` ou en début de saisie.
#
# Codes marqués * : proposés, absents de errors.py.
#   CHR_01    caractère inconnu
#   OPR_01    '*' en début de côté ou derrière '^'
#   OPR_02    pas d'opérande après un opérateur hors exposant
#   OPR_04    '+' derrière '*' ou '^'
#   MUL_01    '*' derrière '*', '+' ou '-'
#   OPR_05    deux nombres sans opérateur
#   EXP_01    pas d'opérande après '^' ou '^-'
#   EXP_02    pas de base avant '^'
#   EXP_03    inconnue en exposant
#   EXP_04    exposant non entier
#   EXP_05    exposants chaînés
#   SGN_03    '--' collé, hors inconnue
#   SGN_04    '+' unaire
#   VAR_01    seconde inconnue
#   VAR_02    '++' collé à l'inconnue
#   VAR_03    '--' collé à l'inconnue
#   EQL_01    côté gauche vide
#   EQL_02    côté droit vide
#   EQL_03    second '='
#   EQL_04    pas de '='
#   LEN_01    plus de MAX_LEN caractères, prioritaire sur tout autre défaut

import io
import sys
import unittest
from contextlib import redirect_stdout
from os.path import abspath, dirname

sys.path.insert(0, dirname(dirname(abspath(__file__))))

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
        return f"plantage {type(error).__name__}"
    return None


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


class Input(unittest.TestCase):
    # Passe toutes les saisies avant d'échouer, pour lister chaque écart avec le code obtenu
    # et le code attendu.
    def check(self, cases):
        wrong = [(source, verdict(source), expected) for source, expected in cases]
        wrong = [case for case in wrong if not conforms(case[1], case[2])]
        lines = [
            f"  {shown(source):44} obtenu {got or 'accepté':20} attendu {expected or 'accepté'}"
            for source, got, expected in wrong
        ]
        if wrong:
            self.fail(f"{len(wrong)} saisies sur {len(cases)}\n" + "\n".join(lines))

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

    def test_minus(self):
        """'-' unaire, seul ou répété, collé derrière un opérateur ou non."""
        self.accepted(
            [
                "-x = 1",
                "- x = 1",
                "x = -1",
                "x - -2 = 0",
                "x - - 2 = 0",
                "x+-1 = 0",
                "1 + -3 * x = 0",
                "X = - -2",
                "- - - x = 1",
                "3 * -x = 1",
                "3*-x = 1",
                "3 * - -x = 1",
            ]
        )

    def test_exponents(self):
        """Exposants entiers, positifs ou négatifs."""
        self.accepted(
            [
                "x^2 = 4",
                "x ^ 2 = 4",
                "x^02 = 4",
                "x^0 * 8 = 2 * x",
                "2.5^2 = x",
                "-2^2 + x = 0",
                "2^-3 = x",
                "1^-8 = 0",
                "x^-1 = 0",
                "x^ -2 = 1",
                "3x^-2 = 0",
                "1*X^-1 = 1*X^-1",
                "1 * X^-1 + 1 * X^0 = 0",
                "x^999999999999 = 1",
            ]
        )

    def test_implicit(self):
        """Multiplication implicite, avec ou sans espace."""
        self.accepted(
            [
                "3x = 1",
                "3 x = 1",
                "x3 = 6",
                "X.5 = 1",
                "xx = 1",
                "x x = 1",
                "2x^2 = 1",
                "x^2x = 1",
                "X^1X^1 = 4",
                "3.1^2x^2 = 0",
                "x2^3 = 1",
                "x^-2x = 1",
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
                "2.5. = x",
                "..5 = x",
                ". = x",
                "x� = 0",
                "x=1\x00",
                "x\n= 1",
                "x = 1\n",
                "x\r= 1",
                "x = 1",
            ],
        )

    def test_missing_left_operand(self):
        """Opérande gauche manquant : '*' ou '^' en tête de membre ou derrière un opérateur."""
        self.check(
            [
                ("*x = 1", "OPR_01"),
                ("* x = 1", "OPR_01"),
                ("x = * 2", "OPR_01"),
                ("x + * 2 = 0", "MUL_01"),
                ("x - * 2 = 0", "MUL_01"),
                ("3 * * x = 1", "MUL_01"),
                ("4**2 = x", "MUL_01"),
                ("x^*2 = 0", "OPR_01"),
                ("^2 = x", "EXP_02"),
                ("^ 1 = 0", "EXP_02"),
                ("x = ^2", "EXP_02"),
                ("x +^2 = 0", "EXP_02"),
                ("3x-^2 = 0", "EXP_02"),
                ("4*^2 = x", "EXP_02"),
                ("x^^2 = 0", "EXP_02"),
            ]
        )

    def test_missing_right_operand(self):
        """Opérande droit manquant : opérateur suivi de '=' ou de la fin de saisie."""
        self.check(
            [
                ("x + = 0", "OPR_02"),
                ("x - = 0", "OPR_02"),
                ("- = 1", "OPR_02"),
                ("x * = 0", "OPR_02"),
                ("x^ = 1", "EXP_01"),
                ("1 ^ = 0", "EXP_01"),
                ("x = 1 +", "OPR_02"),
                ("x = 1 -", "OPR_02"),
                ("x = 1 *", "OPR_02"),
                ("x = 2^", "EXP_01"),
                ("x^- = 1", "EXP_01"),
                ("x = 2^-", "EXP_01"),
                ("x = 1 + = 2", "OPR_02"),
            ]
        )

    def test_unary_plus(self):
        """'+' unaire, refusé partout."""
        self.check(
            [
                ("+x = 1", "SGN_04"),
                ("+ 1 = 0", "SGN_04"),
                ("+- 1 = x", "SGN_04"),
                ("x = +1", "SGN_04"),
                ("1 + +x = 0", "SGN_04"),
                ("x + + 1 = 0", "SGN_04"),
                ("1++1 = x", "SGN_04"),
                ("1 -+ x = 0", "SGN_04"),
                ("x+-+1 = 0", "SGN_04"),
                ("3 * +x = 1", "OPR_04"),
                ("x^+2 = 1", "OPR_04"),
            ]
        )

    def test_double_minus(self):
        """'--' accolé hors inconnue, que bc lit comme un décrément."""
        self.refused(
            "SGN_03",
            [
                "-- = 0",
                "x = --1",
                "x --1 = 0",
                "1--1 = x",
                "3 * --1 = x",
                "2^--1 = x",
                "x ^ -- 1 = 0",
            ],
        )

    def test_increment_decrement(self):
        """'++' ou '--' accolé à l'inconnue, que bc lit comme un incrément ou un décrément."""
        self.check(
            [
                ("x++ = 1", "VAR_02"),
                ("++x = 1", "VAR_02"),
                ("2 * x++ = 0", "VAR_02"),
                ("x-- = 1", "VAR_03"),
                ("--x = 1", "VAR_03"),
                ("2 * x-- = 0", "VAR_03"),
            ]
        )

    def test_juxtaposed_numbers(self):
        """Deux nombres sans opérateur entre eux."""
        self.refused("OPR_05", ["2 3 = x", "X^1 0 = 1", "2..5 = x", "1.2.3 = x"])

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
        """Pas de '=', ou saisie vide."""
        self.refused("EQL_04", ["5 * X^0", "x", "", "   "])

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
                "x^-1.5 = 0",
                "x^ - 2.5 = 0",
            ],
        )

    def test_unknown_in_exponent(self):
        """Inconnue en exposant."""
        self.refused("EXP_03", ["2^x = 4", "x^x = 1", "1^X = 0", "2^-x = 4"])

    def test_chained_exponents(self):
        """Exposants chaînés : a^b^c."""
        self.refused(
            "EXP_05",
            [
                "x^2^3 = 0",
                "x ^ 2 ^ 3 = 0",
                "2^3^2 = x",
                "9^9^9 = x",
                "0.5^9^9^9^9 = x",
                "x^-2^3 = 0",
                "x^2^ = 0",
            ],
        )

    def test_several_unknowns(self):
        """Plusieurs inconnues, la casse compte."""
        self.refused("VAR_01", ["x + y = 0", "x^2 = X", "x * y = 1", "a * X^0 + b * X^1 = 0"])

    def test_too_long(self):
        """Saisie trop longue, refusée avant tout autre défaut ; MAX_LEN caractères passent."""
        self.check(
            [
                ("x = " + "1" * (MAX_LEN - 4), None),
                ("x = " + "1" * (MAX_LEN - 3), "LEN_01"),
                ("(" * (MAX_LEN + 1), "LEN_01"),
                ("+" * (MAX_LEN + 1), "LEN_01"),
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
        self.accepted(["xx = 1", "x x = 1", "X = 1", "z = 1", "2x3 = 1", "x2 = 1"])

    def test_consecutive_operators(self):
        """Deux opérateurs de suite, collés ou séparés, pour chaque combinaison."""
        cases = []
        for first in "+-*^":
            for second in "+-*^":
                for gap in ("", " "):
                    source = f"2 {first}{gap}{second} 1 = x"
                    # Seul le '-' unaire peut suivre un opérateur, sauf collé à un autre '-'.
                    valid = second == "-" and not (first == "-" and gap == "")
                    cases.append((source, None if valid else REJECTED))
        self.check(cases)

    def test_repeated_signs(self):
        """Signes répétés, collés ou séparés."""
        self.check(
            [
                ("- - - x = 1", None),
                ("x = - - - 1", None),
                ("-x = -1", None),
                ("---x = 1", REJECTED),
                ("x = ---1", REJECTED),
                ("+-+-1 = x", REJECTED),
                ("x = -+1", REJECTED),
                ("x = +-1", REJECTED),
                ("x = - + 1", REJECTED),
            ]
        )

    def test_operator_at_edges(self):
        """Opérateur en tête ou en fin de membre, pour chaque opérateur et chaque membre."""
        cases = []
        for op in "+-*^":
            cases.append((f"{op} 1 = x", None if op == "-" else REJECTED))
            cases.append((f"x = {op} 1", None if op == "-" else REJECTED))
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
        """Exposants : décimal, négatif décimal, inconnue, chaîné, vide, signé, doublé."""
        self.rejected(
            [
                "x^1.5 = 1",
                "x^-1.5 = 1",
                "x^.5 = 1",
                "x^2. = 1",
                "x^x = 1",
                "2^x = 1",
                "x^-x = 1",
                "x^2^3 = 1",
                "x^ = 1",
                "x = x^",
                "x^+2 = 1",
                "x^--2 = 1",
                "x^-- 2 = 1",
                "x^ - = 1",
                "x^^2 = 1",
                "x^*2 = 1",
            ]
        )

    def test_unusual_valid_exponents(self):
        """Exposants inhabituels mais valides : négatif, nul, espacé, zéros en tête."""
        self.accepted(
            ["x^-1 = 1", "x^0 = 1", "x ^ 2 = 1", "x^ 2 = 1", "x^- 2 = 1", "x^00 = 1", "x^2x = 1"]
        )

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

    def test_division_by_zero(self):
        """Zéro à une puissance négative, que bc refuse : divide by zero."""
        self.check(
            [
                ("0^-1 = x", REJECTED),
                ("x = 0^-2", REJECTED),
                ("0.0^-1 = x", REJECTED),
                ("-0^-1 = x", REJECTED),
                ("x * 0^-1 = 1", REJECTED),
                ("0^- -1 = x", None),
                ("0^-0 = x", None),
                ("0^0 = x", None),
                ("0^2 = x", None),
            ]
        )


if __name__ == "__main__":
    unittest.main()
