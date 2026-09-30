# 01 — Minimax sequenziale e alfa-beta pruning

**Lezioni**: L11 (albero di enumerazione, backward induction), L12 (minimax
sequenziale, alfa-beta pruning, deep guessing).
**Tempo stimato**: ~1.5h.

## Perché questo esercizio esiste

È l'unico punto del corso in cui c'è un vero *algoritmo* con una proprietà non
banale da dimostrare: la potatura alfa-beta **non cambia il valore minimax**.
All'orale la domanda tipica è "perché puoi tagliare quel ramo?" e la risposta
non è memorizzabile — o hai in testa l'invariante della finestra `[alpha, beta]`
o non ce l'hai. Implementarlo e vederlo coincidere col minimax non potato su 300
alberi casuali è il modo più rapido per averlo in testa.

Il conteggio dei nodi serve a rispondere all'altra domanda tipica: *quanto* si
risparmia, e perché Bigi nelle slide scrive che «l'alfa-beta aiuta solo un po'»
quando l'albero non è ordinato bene.

## Rappresentazione

```python
Leaf = namedtuple("Leaf", "value")     # foglia con payoff
Node = namedtuple("Node", "children")  # nodo interno
```

La radice è di MAX (giocatore I), i livelli si alternano MAX/MIN. Il generatore
`random_tree(rng, depth, branching)` è già fornito ed è deterministico.

## Da implementare in `alfabeta.py`

| funzione | cosa deve fare |
|---|---|
| `count_leaves(node)` | numero di foglie del sottoalbero |
| `minimax(node, maximizing=True)` | `(valore, nodi_visitati, foglie_valutate)`, senza potatura |
| `alphabeta(node, alpha, beta, maximizing=True)` | stessa tripla, con cut-off su `alpha >= beta` |
| `best_move(node)` | indice del figlio della radice che realizza il valore (tie → indice minore); `ValueError` su foglia |
| `order_children(node, maximizing=True)` | nuovo albero coi figli riordinati best-first (MAX: valore decrescente, MIN: crescente) |

Attenzione ai contatori: dopo un cut-off i figli **non visitati non vanno
contati**. È proprio quel numero che misura il risparmio.

## Cosa verifica la suite

- **Oracolo**: su 300 alberi casuali `alphabeta(t)[0] == minimax(t)[0]`. Se la
  tua potatura è troppo aggressiva (per esempio se usi `>` invece di `>=`, o se
  aggiorni `alpha` anche nei nodi di MIN) questo test cade subito.
- Il minimax non potato visita esattamente `sum(b**k for k in range(d+1))` nodi.
- L'alfa-beta non visita mai più nodi del minimax, e in media taglia oltre il 25%
  delle foglie su alberi casuali con `b=3, d=4`.
- **Bound di Knuth-Moore**: nessun ordinamento può far scendere le foglie valutate
  sotto `b**⌈d/2⌉ + b**⌊d/2⌋ − 1`. Vale sempre, quindi è un test di sanità forte.
- Con `order_children` (ordinamento perfetto) l'alfa-beta deve avvicinarsi a quel
  bound: il test chiede di stare entro il doppio.
- Un albero a mano (il classico 3×3 con valore 3 alla radice) per cui il risultato
  è verificabile a occhio.

## Esecuzione

```bash
python3 -m pytest -q            # scheletro → 10 rossi
AGT_SOL=1 python3 -m pytest -q  # soluzione → 10 verdi
```
