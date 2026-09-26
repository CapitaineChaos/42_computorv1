"""Command line entry point."""

import sys

from .parser import ComputorError, parse, sub
from .solver import COMPLEX, DOUBLE, HIGH, IDENTITY, IMPOSSIBLE, LINEAR, REAL, solve

USAGE = """usage: computor [-e] [-s] [-p N] ["equation"]

  -e, --exact          exact roots: irreducible fractions and radicals
  -s, --steps          intermediate steps
  -p, --precision N    decimals of the approximations (default 6)
  -h, --help           this message

Without an equation, equations are read from stdin, one per line."""

HEADLINES = {
    IDENTITY: "Any real number is a solution.",
    IMPOSSIBLE: "No solution.",
    LINEAR: "The solution is:",
    DOUBLE: "Discriminant is zero, the solution is:",
    REAL: "Discriminant is strictly positive, the two solutions are:",
    COMPLEX: "Discriminant is strictly negative, the two complex solutions are:",
    HIGH: "The polynomial degree is strictly greater than 2, I can't solve.",
}


class Usage(Exception):
    pass


def parse_args(argv):
    options = {"exact": False, "steps": False, "digits": 6, "help": False}
    index = 0
    while index < len(argv):
        argument = argv[index]
        if argument in ("-e", "--exact"):
            options["exact"] = True
        elif argument in ("-s", "--steps"):
            options["steps"] = True
        elif argument in ("-h", "--help"):
            options["help"] = True
        elif argument in ("-p", "--precision"):
            index += 1
            if index == len(argv):
                raise Usage("%s needs a number of decimals" % argument)
            options["digits"] = _digits(argv[index])
        else:
            break
        index += 1
    return options, argv[index:]


def _digits(text):
    if not text.isdigit() or not 0 <= int(text) <= 30:
        raise Usage("precision must be an integer between 0 and 30, got '%s'" % text)
    return int(text)


def reduced_form(poly, variable, digits):
    if not poly:
        return "0 * %s^0 = 0" % variable
    parts = []
    for degree, coefficient in enumerate(poly):
        term = "%s * %s^%d" % (abs(coefficient).text(digits), variable, degree)
        if degree == 0:
            parts.append("-" + term if coefficient.sign < 0 else term)
        else:
            parts.append(("- " if coefficient.sign < 0 else "+ ") + term)
    return " ".join(parts) + " = 0"


def render(source, options):
    left, right, variable = parse(source)
    poly = sub(left, right)
    solution = solve(poly, variable, options["digits"])
    lines = ["Reduced form: %s" % reduced_form(poly, variable, options["digits"])]
    # The subject prints no degree for the two degenerate cases.
    if solution.kind not in (IDENTITY, IMPOSSIBLE):
        lines.append("Polynomial degree: %d" % solution.degree)
    if options["steps"]:
        lines.extend("  " + step for step in solution.steps)
    lines.append(HEADLINES[solution.kind])
    lines.extend(_root(root, options) for root in solution.roots)
    return lines


def _root(root, options):
    exact, decimal = root.exact(), root.decimal(options["digits"])
    if not options["exact"]:
        # Complex roots have no decimal form in the subject's examples.
        return exact if root.imaginary else decimal
    return exact if exact == decimal else "%s ~ %s" % (exact, decimal)


def main(argv=None, out=None, err=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    out = out or sys.stdout
    err = err or sys.stderr

    try:
        options, operands = parse_args(argv)
    except Usage as error:
        print("computor: %s\n%s" % (error, USAGE), file=err)
        return 2
    if options["help"]:
        print(USAGE, file=out)
        return 0

    try:
        sources = [" ".join(operands)] if operands else _stdin()
    except KeyboardInterrupt:
        return 130

    failed = False
    for index, source in enumerate(sources):
        if index:
            print(file=out)
        try:
            print("\n".join(render(source, options)), file=out)
        except ComputorError as error:
            _report(error, source, err)
            failed = True
    return 1 if failed else 0


def _stdin():
    return [line.strip() for line in sys.stdin if line.strip()]


def _report(error, source, err):
    print("computor: %s" % error.message, file=err)
    print("    %s" % source, file=err)
    print("    %s^" % (" " * min(error.position, len(source))), file=err)
