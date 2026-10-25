# yield


Générateur synchrone pour faire quelques trucs cool.
On pourrait faire des listes infinies si on ne met pas de limites.

## Utilisattion classique

```python
def compteur(n):
    i = 0
    while i < n:
        yield i
        i += 1

g = compteur(3)
next(g)  # 0
next(g)  # 1
next(g)  # 2
next(g)  # Exception

try:
    next(g)
except StopIteration:
    print("On a exagéré sur les next")
```



```python
def compteur(n):
    i = 0
    while i < n:
        yield i
        i += 1

for x in compteur(3):
    # On s'attend à 0 1 2
    print(x)

list(compteur(3))
# Donne [0, 1, 2]
```


## Récursion avec yield

```python
def aplatir(x):
    if isinstance(x, list):
        for e in x:
            yield from aplatir(e)
    else:
        yield x

list(aplatir([1, [2, [3, 4]], 5])) 
# Donne [1, 2, 3, 4, 5]
```

## Découpage (batch)

```python
def paquets(iterable, n):
    lot = []
    for x in iterable:
        lot.append(x)
        if len(lot) == n:
            yield lot
            lot = []
    if lot:
        yield lot

list(paquets(range(7), 3))
# Donne [[0, 1, 2], [3, 4, 5], [6]]
```