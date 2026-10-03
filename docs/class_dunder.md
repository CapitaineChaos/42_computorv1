# dunder methods (Double UNDERscore)

## Cycle de vie

- `__new__(cls, ...)` : Vrai constructeur utilisé rarement, éventuellement pous singletons ou héritabes de types (int, str...)
- `__init__(self, ...)` : Initialisateur qui reçoit l'instance créée par `__new__`
- `__del__(self)` : Destructeur, juste avant le ramasse-miettes

## Affichage

- `__str__(self)` : Version lisible de l'objet. Appelé par `print(objet)` ou `str(objet)` et doit retourner une chaîne `(str)`
- `__repr__(self)` : Version "officielle" et technique de l'objet

## Comparaisons

- `__eq__(self, other)` : Égalité `(==)`
- `__ne__(self, other)` : Différent `(!=)`
- `__lt__(self, other)` : Plus petit que `(<)`
- `__le__(self, other)` : Plus petit ou égal `(<=)`
- `__gt__(self, other)` : Plus grand que `(>)`
- `__ge__(self, other)` : Plus grand ou égal `(>=)`

## Opérations mathématiques

- `__add__(self, other)` : Addition `(+)`
- `__radd__(self, other)` : Addition avec l'objet à droite
- `__sub__(self, other)` : Soustraction `(-)`
- `__rsub__(self, other)` : Soustraction avec l'objet à droite
- `__mul__(self, other)` : Multiplication `(*)`
- `__rmul__(self, other)` : Multiplication avec l'objet à droite
- `__truediv__(self, other)` : Division `(/)`
- `__rtruediv__(self, other)` : Division avec l'objet à droite
- `__floordiv__(self, other)` : Division entière `(//)`
- `__mod__(self, other)` : Modulo `(%)`è`
- `__pow__(self, other)` : Puissance `(**)`
- `__abs__(self)` : Valeur absolue
- `__neg__(self)` : Opposé

## Comlportement

- `__len__(self)` : Appelé par `len(objet)` et doit retourner un entier
- `__getitem__(self, key)` : Lire une valeur avec des crochets : `objet[key]`.`
- `__setitem__(self, key, value)` : Modifier une valeur avec des crochets : `objet[key] = value`.`
- `__delitem__(self, key)` : Supprimer un élément avec `del objet[key]`.`
- `__contains__(self, item)` : Utiliser le mot-clé in `(if item in objet:)`

## Types

- `__float__(self)` : Convertir en float
- `__int__(self)` : Convertir en int


## Gestion de contexte
Pour être utilisé proprement avec le mot-clé with

- `__enter__(self)` : S'exécute à l'entrée du bloc with. Prépare la ressource
- `__exit__(self, exc_type, exc_val, exc_tb)` : S'exécute à la sortie du bloc, même si une erreur survient. Ex : pour fermer une connexion ou un fichier

## Autre

- `__call__(self, ...)` : Appeler l'objet directement comme si c'était une fonction
- `__hash__(self)` : Permet à l'objet d'être inséré dans un ensemble (set) ou d'être utilisé comme clé dans un dictionnaire

### __call__

```python
class Multiplicateur:
    def __init__(self, facteur):
        self.facteur = facteur  # On stocke le facteur de multiplication

    def __call__(self, nombre):
        # Cette méthode s'exécute quand on utilise l'objet avec des ()
        return nombre * self.facteur

# 1. Création des instances (les configurations)
doubler = Multiplicateur(2)
tripler = Multiplicateur(3)

# 2. Utilisation des objets comme des fonctions
print(doubler(5))  # Résultat : 10
print(tripler(5))  # Résultat : 15
```

### __hash__

```python
class Employe:
    def __init__(self, id_employe, nom):
        self.id_employe = id_employe
        self.nom = nom

    def __eq__(self, other):
        # Deux employés sont considérés identiques si leur ID est le même
        if not isinstance(other, Employe):
            return False
        return self.id_employe == other.id_employe

    def __hash__(self):
        # On base le hash uniquement sur l'ID (qui ne change pas)
        return hash(self.id_employe)

    def __repr__(self):
        return f"Employe({self.nom})"

# 1. Création d'instances
emp1 = Employe(101, "Alice")
emp2 = Employe(102, "Bob")
emp3 = Employe(101, "Alice") # Même ID que emp1

# 2. Utilisation dans un set (élimine automatiquement les doublons)
registre = {emp1, emp2, emp3}
print(registre)  
# Résultat : {Employe(Alice), Employe(Bob)} -> emp3 a été ignoré car identique à emp1 !

# 3. Utilisation comme clé de dictionnaire
accès_badge = {
    emp1: "Accès Zone A",
    emp2: "Accès Zone B"
}
print(accès_badge[emp1])  # Résultat : Accès Zone A
```