import sys

from .display import render
from .parser import ComputorError, parse
from .solver import solve


def main(argv):
    if argv:
        sources = [" ".join(argv)]
    else:
        sources = read_stdin()
    status = 0
    first = True
    try:
        for source in sources:
            if not first:
                print()
            first = False
            if not answer(source):
                status = 1
    except KeyboardInterrupt:
        return 130
    except BrokenPipeError:
        return close_quietly()
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
        p = parse(source)
    except ComputorError as error:
        print("computor: %s" % error, file=sys.stderr)
        if error.position is not None:
            text = error.text or source
            print("    %s\n    %s^" % (text, " " * error.position), file=sys.stderr)
        return False
    print("\n".join(render(p, solve(p))), flush=True)
    return True


# doc: https://docs.python.org/3/library/signal.html#note-on-sigpipe
def close_quietly():
    devnull = open("/dev/null", "w")
    sys.stdout = devnull
    return 120
