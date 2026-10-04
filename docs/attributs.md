# Attributs

## Globales de module

Posées par Python dans chaque fichier `.py` avant sa première ligne.
On peut les consulter directement dans le module, ou via `globals()`...

- `__name__` : nom du module, ou `"__main__"` si le fichier est lancé directement
- `__file__` : chemin du fichier source
- `__doc__` : docstring du module, `None` si absente
- `__package__` : package contenant le module, `None` si lancé en script
- `__path__` : dossiers des sous-modules, seulement dans le `__init__.py` d'un package

Import :

- `__spec__` : objet `ModuleSpec`, comment le module a été trouvé
- `__loader__` : objet qui a chargé le module (`SourceFileLoader` pour un `.py`)
- `__cached__` : chemin du `.pyc` dans `__pycache__`
- `__builtins__` : accès aux noms intégrés (`print`, `len`, exceptions)

## Globale définie par le développeur

- `__all__` : liste des noms exportés par `from module import *`

## Spécial

- `__main__` : valeur de `__name__` pour le fichier lancé, et nom du fichier
  `__main__.py` exécuté par `python3 -m package`

## Attributs d'objets

Accès sur un objet : `obj.__class__`.

- `__class__` : classe de l'objet
- `__dict__` : dictionnaire des attributs de l'objet
- `__annotations__` : annotations de type d'une fonction, d'une classe ou d'un module
- `__slots__` : défini dans une classe, fixe la liste des attributs autorisés (économie de mémoire)

```python
class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

p = Point(1, 2)
p.__class__                     # <class '__main__.Point'>
p.__dict__                      # {'x': 1, 'y': 2}
Point.__init__.__annotations__  # {'x': <class 'int'>, 'y': <class 'int'>}
p.z = 3                         # OK, ajouté au __dict__ : {'x': 1, 'y': 2, 'z': 3}
```

```python
class Slot:
    __slots__ = ("x", "y")

s = Slot()
s.z = 3                         # KO, AttributeError
```

