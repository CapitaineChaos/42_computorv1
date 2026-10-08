# Author : CLAUDE OPUS 5.5

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
# EXP_03, pas un VAR_01. Là où un opérande est attendu :
#   - `+` : OPR_04 après `*` ou `^`, SGN_04 ailleurs ;
#   - `*` : OPR_04 après `*` ou `^`, OPR_01 ailleurs ;
#   - `^` : OPR_04 après `*` ou `^`, EXP_02 ailleurs ;
#   - `-` : SGN_03 collé derrière un `-`, accepté ailleurs ;
#   - `=` ou la fin : EXP_01 après `^`, OPR_02 après un autre opérateur, EQL_0x après `=`
#     ou en début de saisie.
#
# Codes marqués * : proposés, absents de errors.py.
#   CHR_01    caractère inconnu
#   OPR_01    pas d'opérande avant '*'
#   OPR_02    pas d'opérande après un opérateur autre que '^'
#   OPR_04    '*', '^' ou '+' derrière '*' ou '^'
#   OPR_05    deux nombres sans opérateur
#   EXP_01    pas d'opérande après '^'
#   EXP_02    pas de base avant '^'
#   EXP_03 *  exposant non entier
#   EXP_05 *  inconnue en exposant
#   EXP_06 *  exposants chaînés
#   SGN_03    '--' collé
#   SGN_04    '+' unaire
#   VAR_01    seconde inconnue
#   EQL_01    côté gauche vide
#   EQL_02    côté droit vide
#   EQL_03    second '='
#   EQL_04    pas de '='

import io
import sys
import unittest
from contextlib import redirect_stdout
from os.path import abspath, dirname

sys.path.insert(0, dirname(dirname(abspath(__file__))))

import tests.common  # noqa: E402, F401
from computorv1.errors import ComputorErr  # noqa: E402
from computorv1.parser import parse  # noqa: E402
from tests.corpus import EQUATIONS, IMPLICIT, REFUSED, UNSOLVED  # noqa: E402

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


class Input(unittest.TestCase):
    # Passe toutes les saisies avant d'échouer, pour lister chaque écart avec le code obtenu
    # et le code attendu.
    def check(self, cases):
        wrong = [(source, verdict(source), expected) for source, expected in cases]
        wrong = [(source, got, expected) for source, got, expected in wrong if got != expected]
        lines = [
            f"  {source!r:44} obtenu {got or 'accepté':20} attendu {expected or 'accepté'}"
            for source, got, expected in wrong
        ]
        if wrong:
            self.fail(f"{len(wrong)} saisies sur {len(cases)}\n" + "\n".join(lines))

    def accepted(self, sources):
        self.check([(source, None) for source in sources])

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
                "x^2. = 4",
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

    def test_students_42(self):
        """Corpus 42 : saisies valides."""
        self.accepted([source for source, _ in EQUATIONS + IMPLICIT + UNSOLVED])


class Refused(Input):
    def test_CHR_01(self):
        """Caractère inconnu, parenthèses comprises."""
        self.refused(
            "CHR_01",
            [
                "x % 2 = 0",
                "(x + 1) = 0",
                "2/3 * x = 1",
                "3x² = 1",
                "x⁻¹ = 1",
                "2.5. = x",
                "..5 = x",
                "x� = 0",
            ],
        )

    def test_OPR_01(self):
        """Pas d'opérande avant '*'."""
        self.refused("OPR_01", ["* x = 1", "*x = 1", "x = * 2", "x - * 2 = 0"])

    def test_OPR_02(self):
        """Pas d'opérande après un opérateur autre que '^'."""
        self.refused(
            "OPR_02", ["x * = 0", "x = 1 *", "x + = 0", "x - = 0", "- = 1", "x = 1 -"]
        )

    def test_OPR_04(self):
        """'*', '^' ou '+' derrière '*' ou '^'."""
        self.refused(
            "OPR_04",
            [
                "3 * * x = 1",
                "4**2 = x",
                "4*^2 = x",
                "x^^2 = 0",
                "x^*2 = 0",
                "3 * +x = 1",
                "x^+2 = 1",
            ],
        )

    def test_OPR_05(self):
        """Deux nombres sans opérateur."""
        self.refused("OPR_05", ["2 3 = x", "X^1 0 = 1", "2..5 = x", "1.2.3 = x"])

    def test_EXP_01(self):
        """Pas d'opérande après '^'."""
        self.refused("EXP_01", ["x^ = 1", "1 ^ = 0", "x = 2^"])

    def test_EXP_02(self):
        """Pas de base avant '^'."""
        self.refused("EXP_02", ["^2 = x", "^ 1 = 0", "x = ^2", "x +^2 = 0"])

    def test_EXP_03(self):
        """Exposant non entier, bc le tronque avec un avertissement."""
        self.refused("EXP_03", ["x^1.5 = 0", "2^0.5 = x", "x^.5 = 1", "x^2.0 = 4"])

    def test_EXP_05(self):
        """Inconnue en exposant."""
        self.refused("EXP_05", ["2^x = 4", "x^x = 1", "1^X = 0"])

    def test_EXP_06(self):
        """Exposants chaînés."""
        self.refused("EXP_06", ["x^2^3 = 0", "2^3^2 = x", "9^9^9 = x", "0.5^9^9^9^9 = x"])

    def test_SGN_03(self):
        """'--' collé, que bc lit comme un décrément."""
        self.refused("SGN_03", ["--x = 1", "-- = 0", "x --1 = 0", "x-- = 1", "2^--1 = x"])

    def test_SGN_04(self):
        """'+' unaire."""
        self.refused(
            "SGN_04", ["+ 1 = 0", "+x = 1", "x = +1", "1 + +x = 0", "1 -+ x = 0", "+- 1 = x"]
        )

    def test_VAR_01(self):
        """Seconde inconnue, la casse compte."""
        self.refused("VAR_01", ["x + y = 0", "x^2 = X", "x * y = 1", "a * X^0 + b * X^1 = 0"])

    def test_EQL_01(self):
        """Côté gauche vide."""
        self.refused("EQL_01", ["= x", "= 1 * X^0"])

    def test_EQL_02(self):
        """Côté droit vide."""
        self.refused("EQL_02", ["x =", "x =   "])

    def test_EQL_03(self):
        """Second '='."""
        self.refused("EQL_03", ["x = 1 = 2", "x == 1", "x = = 1"])

    def test_EQL_04(self):
        """Pas de '=', ou rien du tout."""
        self.refused("EQL_04", ["5 * X^0", "x", "", "   "])

    def test_students_42(self):
        """Corpus 42 : saisies refusées."""
        self.check(REFUSED)


if __name__ == "__main__":
    unittest.main()
