# Codes d'erreur

- Format de sortie : `computor: (CODE) message`
- Préfixe = étape qui refuse : `LX` lexer, `EQ` équation, `ST` terme signé, `TE` monôme, `FA` facteur, `EX` exposant

| Code | Cause                                         | Saisie         | Message                                                  |
|------|-----------------------------------------------|----------------|----------------------------------------------------------|
| LX01 | caractère inconnu                             | `x % 2 = 0`    | `unexpected character '%' at column 3`                   |
| EQ01 | partie gauche vide                            | `= x`          | `missing left side of equation`                          |
| EQ02 | pas de `=` après la partie gauche             | `5 * X^0`      | `missing equal sign at column 8`                         |
| EQ03 | second `=`                                    | `x = 1 = 2`    | `unexpected '=' at column 7`                             |
| EQ04 | partie droite vide                            | `x =`          | `missing right side of equation`                         |
| ST01 | signes consécutifs                            | `--x = 1`      | `consecutive signs at column 2`                          |
| TE01 | signe collé derrière `*`                      | `3 *-x = 1`    | `ambigous usage of operator at column 3, '-'`            |
| TE02 | deux nombres sans opérateur                   | `2 3 = X`      | `missing operator between numbers at column 3`           |
| FA01 | facteur attendu, trouvé `*` `/` `=` ou la fin | `3 * = X`      | `factor expected at column 5`                            |
| FA02 | facteur attendu, trouvé un signe              | `3 * - -x = 1` | `unexpected '-' at column 7`                             |
| FA03 | seconde inconnue                              | `x + y = 0`    | `unknown already defined, illegal name 'y'`              |
| EX01 | `^` suivi de `^`                              | `x^^2 = 0`     | `exponent error: missing number at column 3`             |
| EX02 | exposant signé                                | `x^-1 = 0`     | `exponent must not have a sign at column 3`              |
| EX03 | exposant non entier ou absent                 | `x^1.5 = 0`    | `exponent must be an integer at column 3`                |
| EX04 | exposants chaînés                             | `x^2^3 = 0`    | `chained exponent is ambiguous at column 4`              |
| EX05 | `^` en tout début, sans base                  | `^2 = x`       | `missing base for exponent at column 1`                  |
| EX06 | `^` juste après un opérateur ou `=`           | `3x=^2`        | `exponent cannot be applied to operator at column 3`     |
