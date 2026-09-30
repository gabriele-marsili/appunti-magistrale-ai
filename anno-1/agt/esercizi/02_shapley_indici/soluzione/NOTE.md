# Note sulla soluzione — 02 Shapley e indici di potere

## Perché i pesi sono quelli

`|S|! (n−|S|−1)! / n!` è la probabilità che, in una permutazione uniforme dei
giocatori, **i membri di S arrivino tutti prima di i e tutti gli altri dopo**:
`|S|!` ordinamenti interni a S, `(n−|S|−1)!` ordinamenti del resto, su `n!` totali.
Da qui l'identità con la media sulle permutazioni: è la stessa somma raggruppata
per coalizione di predecessori invece che per permutazione.

Detta così è anche la risposta all'orale. Il conto non serve: serve la frase.

## Costo

- `shapley_marginal`: `O(n · 2^n)`.
- `shapley_permutations`: `O(n · n!)` — a n=7 sono 35280 operazioni, istantaneo;
  a n=10 sarebbe 36 milioni. Per questo l'oracolo si ferma a 7, come da consegna.

Il fatto che la formula pesata sia esponenziale ma **molto** meno esponenziale
della media sulle permutazioni è già di per sé un'osservazione da fare:
il valore di Shapley è #P-hard da calcolare in generale, ma su giochi con `n`
piccolo (quelli d'esame) entrambe le strade sono praticabili.

## Trappole

1. **`v[0]` non azzerato.** Se il gioco casuale non impone `v(∅)=0` l'efficienza
   salta e non si capisce perché. `random_game` lo fa già.
2. **Overflow/precisione dei fattoriali.** Con `math.factorial` in Python sono
   interi esatti; precalcolare i pesi una volta per `|S| = 0..n−1` evita `n·2^n`
   chiamate a `factorial`.
3. **Banzhaf normalizzato quando la somma è 0.** Su un gioco costantemente nullo
   `banzhaf_raw().sum() == 0` e la normalizzazione dà NaN. La suite non lo
   esercita, ma vale la pena saperlo.
4. **Confondere "grezzo" e "normalizzato".** L'indice di Banzhaf *normalizzato*
   somma a 1 come Shapley-Shubik, ma non è il valore di Shapley del gioco: la
   normalizzazione non ripristina l'efficienza in senso assiomatico, la impone a
   mano. È esattamente la ragione per cui Shapley è caratterizzato dai quattro
   assiomi e Banzhaf no.

## L'esempio `[6; 4, 3, 2]` a mano

Coalizioni vincenti: `{A,B}=7`, `{A,C}=6`, `{A,B,C}=9`. Perdenti: tutte le altre.

**Shapley-Shubik** — pivot nelle 6 permutazioni:

| ordine | pivot |
|---|---|
| A B C | B (4→7) |
| A C B | C (4→6) |
| B A C | A (3→7) |
| B C A | A (5→9) |
| C A B | A (2→6) |
| C B A | A (5→9) |

→ `(4/6, 1/6, 1/6)`.

**Banzhaf** — swing (giocatore critico) per coalizione vincente:
A è critico in `{A,B}`, `{A,C}`, `{A,B,C}` → 3.
B è critico solo in `{A,B}` (in `{A,B,C}` togliendo B resta `{A,C}=6 ≥ 6`) → 1.
C è critico solo in `{A,C}` → 1.
Grezzo: `3/4, 1/4, 1/4` (denominatore `2^{n−1} = 4`). Normalizzato: `3/5, 1/5, 1/5`.

Nota la differenza qualitativa: Shapley-Shubik dà ad A i **due terzi** del potere,
Banzhaf solo i **tre quinti**. Stessa struttura di potere, pesi diversi sulle
coalizioni, risposte diverse. Chi ha ragione dipende dal modello di formazione
delle coalizioni che si ha in mente — ed è la risposta giusta se lo chiedono.
