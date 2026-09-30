# 02 — Valore di Shapley, assiomi e indici di potere

**Lezioni**: L24 (concetti di soluzione per giochi TU, valore di Shapley, assiomi,
marginality/monotonicity, Shapley-Shubik, Banzhaf).
**Tempo stimato**: ~2h.

## Perché questo esercizio esiste

Il valore di Shapley ha due definizioni che *sembrano* diverse — la somma pesata
sui sottoinsiemi e la media sui contributi marginali lungo le n! permutazioni — e
all'orale va detto perché coincidono. Implementarle separatamente e vederle
coincidere a 1e-9 su giochi casuali con n fino a 7 è il modo più economico per non
confondersi sui pesi `|S|!(n−|S|−1)!/n!` (che è il numero di permutazioni in cui i
membri di S precedono i, diviso n!).

Il secondo pezzo è la differenza fra Shapley-Shubik e Banzhaf: identici come
struttura, diversi per il peso attribuito a ciascuna coalizione, e con
conseguenze diverse (Banzhaf perde l'efficienza). È una domanda d'orale
classica e la risposta si vede meglio su un esempio numerico che a parole.

## Rappresentazione

Un gioco TU su `N = {0,...,n-1}` è un array numpy `v` di lunghezza `2**n`,
indicizzato dalla **maschera di bit** della coalizione: il bit `i` vale 1 se `i`
sta nella coalizione. Quindi `v[0] = 0` e `v[2**n - 1] = v(N)`.
Sono forniti `mask_of`, `players_of`, `random_game`, `unanimity_game`,
`additive_game`.

## Da implementare in `shapley.py`

| funzione | cosa deve fare |
|---|---|
| `shapley_marginal(v, n)` | formula `Σ_{S⊄i} |S|!(n−|S|−1)!/n! · [v(S∪i) − v(S)]` |
| `shapley_permutations(v, n)` | media dei contributi marginali sulle n! permutazioni |
| `banzhaf_raw(v, n)` | stessa somma con pesi **uniformi** `1/2^{n−1}` |
| `banzhaf_normalized(v, n)` | `banzhaf_raw` diviso la sua somma |
| `weighted_voting_game(weights, quota)` | gioco semplice `v(S) = 1 ⟺ w(S) ≥ q` |
| `shapley_shubik(weights, quota)` | valore di Shapley del gioco di voto pesato |
| `is_null_player(v, n, i)` | `v(S∪i) = v(S)` per ogni `S ∌ i` |
| `are_symmetric(v, n, i, j)` | `v(S∪i) = v(S∪j)` per ogni `S` che esclude entrambi |

Le due implementazioni di Shapley devono restare **indipendenti**: non chiamare
l'una dentro l'altra, altrimenti il test dell'oracolo diventa vacuo.

## Cosa verifica la suite

- **Oracolo**: `shapley_marginal == shapley_permutations` su giochi casuali con
  `n = 3..7`.
- **Forme chiuse**: gioco di unanimità `u_T` → `1/|T|` sui membri di `T`, 0 fuori;
  gioco additivo → il vettore dei valori individuali.
- **I quattro assiomi**, uno per test: efficienza, null player, simmetria,
  additività.
- **Conti a mano su `[6; 4, 3, 2]`**: Shapley-Shubik `(4/6, 1/6, 1/6)`,
  Banzhaf grezzo `(3/4, 1/4, 1/4)`, normalizzato `(3/5, 1/5, 1/5)`.
  Sono ricavabili con carta e penna in due minuti — vale la pena rifarli prima di
  guardare il codice.
- Che i due indici **non** coincidano, e che Banzhaf **non** sia efficiente.
- Il caso degenere `[3; 3, 1, 1]`: dittatore + due null player.

## Esecuzione

```bash
python3 -m pytest -q            # scheletro → 13 rossi
AGT_SOL=1 python3 -m pytest -q  # soluzione → 13 verdi
```
