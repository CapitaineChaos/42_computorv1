import os
import sys

from .display import render
from .errors import ComputorError
from .parser import parse
from .reduce import MAX_REDUCED_DISP, dense
from .solver import solve

def main(argv):
    sources = argv if argv else read_stdin()

    status = 0
    position = 0

    try:
        for source in sources:
            position += 1
            print(f"computor: equation {position}: {source}\n")
            if not answer(source):
                status = 1

    # https://docs.python.org/fr/3.14/builtins/exceptions.html#KeyboardInterrupt
    except KeyboardInterrupt:
        print(file=sys.stderr)
        return 130

    # https://docs.python.org/fr/3.14/library/signal.html#note-on-sigpipe
    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        return 1

    if position == 0:
        print("computor: no equation", file=sys.stderr)
        return 1
    return status


# doc: https://docs.python.org/3/library/sys.html#sys.stdin
def read_stdin():
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(errors="replace")
    for line in sys.stdin:
        line = line.strip()
        if line:
            yield line


def answer(source):
    try:
        coefficients, degree, name = parse(source)
        p = dense(coefficients, degree) if degree <= MAX_REDUCED_DISP else None
        lines = render(p, degree, solve(p, degree), name)
    except (ComputorError, ValueError, ZeroDivisionError) as error:
        print(f"computor: {error}", file=sys.stderr)
        return False
    except (OverflowError, MemoryError):
        print("computor: number too large", file=sys.stderr)
        return False
    print("\n".join(lines), flush=True)
    return True
