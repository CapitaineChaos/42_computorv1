# stdin

[Doc Python](https://docs.python.org/3/library/sys.html#sys.stdin)

- stdin : flux d'entrée standard, descripteur de fichier `0`
- En Python : `sys.stdin`, objet fichier texte

## Sources

| Commande                      | contenu de stdin                       |
|-------------------------------|----------------------------------------|
| `python3 prog.py`             | le terminal                            |
| `echo "a" \| python3 prog.py` | la sortie de la commande de gauche     |
| `python3 prog.py < f.txt`     | le contenu du fichier                  |
| `python3 prog.py < /dev/null` | rien                                   |

## Au clavier

- Shell lance le processus avec stdin déjà relié au terminal, c'est `sys.stdin` au démarrage
- Lecture et blocage jusqu'à la saisie : `input()` ou `sys.stdin.read*()`
- Mode ligne, par défaut : le terminal garde la ligne (Backspace compris) jusqu'à ce que l'utilisateur tape Entrée
- Ctrl-D sur une ligne vide : fin de flux.
- Ctrl-D au milieu d'une ligne : envoie la ligne sans `\n`
- Si on veut lire touche par touche : passer le terminal en mode brut (`tty.setraw`)


## Lire

| Lecture                  | Renvoie                       | En fin de flux    |
|--------------------------|-------------------------------|-------------------|
| `input()`                | une ligne, sans `\n`          | raise `EOFError`  |
| `sys.stdin.readline()`   | une ligne, avec `\n`          | `""`              |
| `for line in sys.stdin:` | une ligne par tour, avec `\n` | sort de la boucle |
| `sys.stdin.read()`       | tout le flux                  | `""`              |


## Capturer Ctrl-D

Ctrl-D est juste une fin de flux pour Python, comme la fin d'un pipe


```python
while True:
    try:
        ligne = input("> ")
    except EOFError:        # Ctrl-D
        print("\nfin")      # \n : le curseur est resté après le prompt
        break
    print("lu :", ligne)
```

```python
import sys

while True:
    ligne = sys.stdin.readline()
    if ligne == "":         # Ctrl-D ; une ligne vide tapée vaut "\n", pas ""
        break
```

### Exemple 1a : `input()` enlève le `\n`

```python
nom = input()
print("Bonjour", nom, "!")
```

```
$ echo "Coucou" | python3 prog.py
Bonjour Coucou !
```

### Exemple 1b : `readline()` garde le `\n`

```python
import sys

nom = sys.stdin.readline()      # "Hello\n"
print("Bonjour", nom, "!")
```

```
# echo ajoute un \n à la fin
$ echo "Hello" | python3 prog.py
Bonjour Hello
 !
```

### Exemple 1c : `read()` prend tout

```python
import sys

texte = sys.stdin.read()        # "a\nb\nc\n"
print(len(texte.splitlines()), "lignes")
```

```
$ printf 'a\nb\nc\n' | python3 prog.py
3 lignes
```


### Exemple 2 : Somme

```python
import sys

# À savoir : int() ignore le \n donc ça tombe bien
total = sum(int(line) for line in sys.stdin)
```

```
$ printf '1\n2\n3\n' | python3 somme.py
6
```

Une ligne vide donne `int('\n')` : `ValueError`.

## Terminal ou pipe

```python
sys.stdin.isatty()      # True avec clavier sinon False depuis pipe ou fichier
```

## Binaire

```python
sys.stdin.buffer.read()     # b'a\n' : bytes, sans décodage
```
