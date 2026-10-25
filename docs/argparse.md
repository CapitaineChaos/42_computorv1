<!--
Author : smaitre@student.42.fr 
Type :   Doc vite fait
-->

# argparse

Exemple rapide

La fonction principale :

```python
import argparse

def parse_args(argv):
    parser = argparse.ArgumentParser(prog="computor")
    parser.add_argument("-s", "--steps", action="store_true",
                        help="affiche les étapes de résolution")
    parser.add_argument("equations", nargs="*",
                        help="équations à résoudre (stdin si absent)")
    return parser.parse_args(argv)
```

Utiliser dans main :

```python
args = parse_args(argv)
sources = read_args(args.equations) if args.equations else read_stdin()
# ...
if not answer(source, args.steps):
```

Ajouter des args facilement :

```python
parser.add_argument("-v", "--verbose", action="store_true")
parser.add_argument("-p", "--precision", type=int, default=6)
```


Utilisation :

Attention il y a un petit défaut avec argparse... si l'argument contient un "-"
il faut utiliser `--` pour signaler que c'est la fin des options

```bash
./computor -s -- "-X=0"
```

Alors on peux empêcher d'y avoir une erreur :

```python
args, unknown = parser.parse_known_args(argv)
equations = args.equations + unknown
```

Mais on perd les interceptions `bad argument`

## Sinon on parse arg nous-meme

On paume les flags combinés en en plus c'est sâle

```python
FLAGS = {
    "-s": "steps", "--steps": "steps",
    "-v": "verbose", "--verbose": "verbose",
}

def parse_args(argv):
    opts = dict.fromkeys(FLAGS.values(), False)
    equations = []
    for arg in argv:
        if arg in FLAGS:
            opts[FLAGS[arg]] = True
        else:
            equations.append(arg)
    return opts, equations

# Et on récupère les args d'un côté et les équations de l'autre
opts, equations = parse_args(argv)
sources = read_args(equations) if equations else read_stdin()
# ...
answer(source, opts["steps"])
```

