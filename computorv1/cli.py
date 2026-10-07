import os
import sys

from .builder import build_eq
from .errors import ComputorError
from .parser import parse

STEPS_FLAGS = ("-s", "--steps")


def main(argv):

    show_steps = any(arg in STEPS_FLAGS for arg in argv)
    argv = [arg for arg in argv if arg not in STEPS_FLAGS]
    sources = read_args(argv) if argv else read_stdin()

    status = 0
    position = 0

    try:
        for source in sources:
            position += 1
            print(f"computor: equation {position}: {source}\n")
            if not answer(source, show_steps):
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


# doc: https://docs.python.org/3/library/os.html#os.fsencode
def read_args(argv):
    for arg in argv:
        yield os.fsencode(arg).decode(errors="replace")


# doc: https://docs.python.org/3/library/sys.html#sys.stdin
def read_stdin():
    for raw in sys.stdin.buffer:
        line = raw.decode(errors="replace").strip()
        if line:
            yield line


def answer(source, show_steps):
    try:
        # coeffs, degree, name = parse(source)
        # eq = build_eq(coeffs, degree, name)
        # lines = eq.lines(show_steps)
        parse(source)
    except (ComputorError, ValueError, ZeroDivisionError) as error:
        print(f"computor: {error}", file=sys.stderr)
        return False
    except (OverflowError, MemoryError):
        print("computor: number too large", file=sys.stderr)
        return False
    # print("\n".join(lines), flush=True)
    return True
