# Author     : CLAUDE OPUS 5.5
# Maintainer : CLAUDE OPUS 5.5

# Fuzz : saisies comparées à l'oracle (tests/oracle.py), écarts regroupés par (obtenu, attendu).
# Deux passes :
#   - toutes les saisies de 1 à 5 caractères pris dans SHORT_ALPHABET (environ 110 000) ;
#   - des saisies aléatoires, la moitié tirée au hasard, l'autre moitié partant d'une équation
#     valide abîmée de une à trois retouches, pour aller chercher les défauts au milieu d'une
#     saisie plausible. La graine est affichée : la repasser rejoue exactement le même tirage.
#
#   python tests/fuzz.py [--count N] [--seed S] [--examples K]

import argparse
import random
import sys
from itertools import product
from os.path import abspath, dirname

sys.path.insert(0, dirname(dirname(abspath(__file__))))

from tests.oracle import expected  # noqa: E402
from tests.test_saisie import conforms, verdict  # noqa: E402

SHORT_ALPHABET = ["1", ".", "x", "y", "=", "+", "-", "*", "^", " "]
SHORT_LENGTH = 5

NUMBERS = ["0", "1", "2", "7", "42", "3.5", ".5", "2.", "1.0", "007"]
UNKNOWNS = ["x", "x", "x", "X", "y"]
SYMBOLS = ["=", "+", "-", "*", "^"]
BLANKS = [" ", " ", "", "\t", "  "]
INVALID = ["(", ")", "/", "%", "²"]

# Fragment au hasard, pondéré pour que les caractères invalides restent rares : sinon ils
# arrêteraient presque toutes les saisies au premier défaut.
FRAGMENTS = [(NUMBERS, 6), (UNKNOWNS, 5), (SYMBOLS, 8), (BLANKS, 4), (INVALID, 1)]


def fragment(rng):
    pool = rng.choices([pool for pool, _ in FRAGMENTS], [weight for _, weight in FRAGMENTS])[0]
    return rng.choice(pool)


def random_input(rng):
    return "".join(fragment(rng) for _ in range(rng.randint(1, 16)))


def term(rng):
    coefficient = rng.choice(NUMBERS)
    exponent = rng.choice(["", "^0", "^1", "^2", "^-1", "^3"])
    return rng.choice([f"{coefficient} * x{exponent}", f"{coefficient}x{exponent}", coefficient])


def side(rng):
    text = term(rng)
    for _ in range(rng.randint(0, 3)):
        text += f" {rng.choice('+-')} {term(rng)}"
    return text


# Retouches : insérer un fragment, supprimer, doubler ou échanger des caractères.
def damage(rng, text):
    at = rng.randrange(len(text) + 1)
    action = rng.randrange(4)
    if action == 0:
        return text[:at] + fragment(rng) + text[at:]
    if action == 1:
        return text[:at] + text[at + 1 :]
    if action == 2:
        return text[:at] + text[at : at + 1] * 2 + text[at + 1 :]
    return text[:at] + text[at + 1 : at + 2] + text[at : at + 1] + text[at + 2 :]


def damaged_equation(rng):
    text = f"{side(rng)} = {side(rng)}"
    for _ in range(rng.randint(1, 3)):
        text = damage(rng, text)
    return text


def random_inputs(rng, count):
    for index in range(count):
        yield random_input(rng) if index % 2 else damaged_equation(rng)


def short_inputs():
    for length in range(1, SHORT_LENGTH + 1):
        for chars in product(SHORT_ALPHABET, repeat=length):
            yield "".join(chars)


# Écarts regroupés par (obtenu, attendu) du plus fréquent au plus rare, avec les exemples les
# plus courts : sur des milliers de saisies, une ligne par écart noierait tout.
def mismatches(sources, examples):
    groups, total = {}, 0
    for source in sources:
        total += 1
        got, want = verdict(source), expected(source)
        if not conforms(got, want):
            groups.setdefault((got, want), []).append(source)
    lines = [f"{sum(map(len, groups.values()))} écarts sur {total} saisies"]
    for (got, want), sources in sorted(groups.items(), key=lambda group: -len(group[1])):
        shortest = sorted(set(sources), key=lambda source: (len(source), source))[:examples]
        lines.append(
            f"  obtenu {got or 'accepté':20} attendu {want or 'accepté':8}"
            f" {len(sources):>7} fois   ex. {', '.join(map(repr, shortest))}"
        )
    print("\n".join(lines))
    return bool(groups)


def main():
    options = argparse.ArgumentParser(description="Fuzz du parser contre l'oracle.")
    options.add_argument("--count", type=int, default=200_000)
    options.add_argument("--seed", type=int, default=random.randrange(1_000_000))
    options.add_argument("--examples", type=int, default=3)
    args = options.parse_args()

    print(f"Saisies de 1 à {SHORT_LENGTH} caractères parmi {''.join(SHORT_ALPHABET)!r}")
    failed = mismatches(short_inputs(), args.examples)
    print(f"\nSaisies aléatoires, graine {args.seed}")
    failed |= mismatches(random_inputs(random.Random(args.seed), args.count), args.examples)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
