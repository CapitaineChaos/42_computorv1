
# GCD

[Algo wiki](https://https://fr.wikipedia.org/wiki/Algorithme_d%27Euclide#Version_it%C3%A9rative)

- EN : GCD  = Greatest Common Divisor
- FR : PGCD = Plus Grand Commun Diviseur

Fonction pour obtenir le plus grand nombre entier qui peut diviser deux nombres sans laisser de reste.

```
fonction euclide(a, b)
    tant que b ≠ 0
        t := b;
        b := a modulo b;
        a := t;
    renvoyer a;
```

Exemple avec -5 et 2 :
```
1 :     a = -5              b = 2
        t =  2
        b = -5 mod 2 = 1
        a =  2
2 :     a = 2               b = 1
        t =  1
        b = 2 mod 1 = 0
        a =  1
3 :     a = 1               b = 0
        renvoyer 1
```

Exemple avec 5 et -2 :
```
1 :     a =  5              b = -2
        t = -2
        b = 5 mod -2 = -1
        a = -2
2 :     a = -2              b = -1
        t = -1
        b = -2 mod -1 = 0
        a = -1
3 :     a = -1              b = 0
        renvoyer -1
```