import sys
import os

from .display import render
from .errors import ComputorError
from .parser import parse
from .solver import solve


def main(argv):
    sources = argv if argv else read_stdin()

    status = 0
    first = True
    try:
        for source in sources:
            if not first:
                print()
            first = False
            if not answer(source):
                status = 1

    # https://docs.python.org/fr/3.14/builtins/exceptions.html#KeyboardInterrupt
    except KeyboardInterrupt:
        print(file=sys.stderr)
        return 130

    # https://docs.python.org/fr/3.14/library/signal.html#note-on-sigpipe
    except BrokenPipeError:
        devnull = os.open("/dev/null", "w")
        os.dup2(devnull, sys.stdout.fileno())
        return 1

    if first:
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
        p, name = parse(source)
    except ComputorError as error:
        print(f"computor: {error}", file=sys.stderr)
        if error.position is not None:
            text = error.text or source
            print(f"    {text}\n    {' ' * error.position}", file=sys.stderr)
        return False
    print("\n".join(render(p, solve(p), name)), flush=True)
    return True
