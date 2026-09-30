# Esercizi di codice — AGT (Bigi, Pisa)

## Tempo totale realistico: 8-9 ore

Non 7-8 come avevo stimato a occhio prima di scriverli. La ripartizione onesta,
assumendo che tu implementi davvero e non copi la soluzione:

| esercizio | argomento | lezioni | ore | test |
|---|---|---|---|---|
| `01_minimax_alfabeta` | minimax, alfa-beta pruning, ordinamento best-first | L11-L12 | ~1.5 | 10 |
| `02_shapley_indici` | valore di Shapley, assiomi, Shapley-Shubik, Banzhaf | L24 | ~2 | 13 |
| `03_core_nucleolo` | core, vertici, least core, nucleolo (schema di Maschler) | L20-L23 | ~2.5-3 | 15 |
| `04_gale_shapley` | deferred acceptance, stabilità, proposer-optimality | L18 | ~2 | 12 |
| | | | **~8-9** | **50** |

Il terzo è quello che sfora: se hai poco tempo, fai i primi due e il quarto e
del terzo implementa solo fino a `least_core_epsilon`, lasciando `nucleolus`.
Perdi il pezzo più istruttivo ma resti dentro le 6 ore.

## Dove NON ho scritto esercizi, e perché

Hai chiesto 4, quindi queste sono esclusioni deliberate. Le motivazioni, una per una:

- **Bargaining assiomatico (L14-L15, Nash bargaining solution).** È dimostrazione
  pura. Implementare `argmax ∏(u_i − u*_i)` su un politopo non insegna niente sul
  teorema di caratterizzazione, che è l'unica cosa che ti chiederanno. Scrivere
  codice qui sarebbe tempo sottratto al ripasso della dimostrazione.
- **Rubinstein / Baron-Ferejohn (L16).** L'equilibrio si ricava in tre righe con
  la condizione di indifferenza e il fattore di sconto. Un simulatore di offerte
  alternate produce numeri che *confermano* la formula, non un oracolo
  indipendente — è la stessa formula scritta due volte.
- **Regret matching e fictitious play (L9).** Era nella tua lista degli oracoli
  buoni e in astratto lo è. Il problema è pratico: la convergenza `O(1/√T)` del
  regret medio è asintotica e stocastica, quindi qualunque soglia numerica in un
  test è o troppo lasca (passa anche un'implementazione sbagliata) o troppo
  stretta (fallisce con un altro seed). Un test che dipende dal seed è peggio di
  nessun test. Se lo vuoi comunque, va scritto come *esperimento con grafico*, non
  come suite pytest — dimmelo e lo faccio in quella forma.
- **Potential games e best response dynamics (L7-L8).** Buon candidato, tagliato
  solo per il vincolo dei 4. Sarebbe il quinto: monotonia del potenziale lungo la
  BRD e punto fisso = NE verificato per enumerazione. Se recuperi tempo ad agosto,
  è quello da aggiungere.
- **Zero-sum via LP vs maximin enumerato (L6).** Anche questo era nella tua lista.
  Tagliato perché `03_core_nucleolo` già contiene un solutore LP scritto a mano:
  il valore didattico si sovrappone, e la parte specifica (il minimax di von
  Neumann) si verifica meglio a mano su matrici 3×3.
- **Stackelberg-Nash (L13), IESDS, Hotelling.** Contenuto matematico, non
  algoritmico. IESDS in particolare è un ciclo `while` su una matrice: cinque
  minuti di codice, zero insight.

## Struttura

Ogni cartella `NN_slug/` contiene:

```
README.md              la consegna: cosa implementare, perché, cosa verifica la suite
slug.py                lo scheletro, con le funzioni da fare marcate # TODO
test_slug.py           la suite pytest
soluzione/slug_sol.py  la soluzione di riferimento
soluzione/NOTE.md      idee chiave, trappole, costi, e i fatti da avere pronti all'orale
```

`03_core_nucleolo` contiene anche `lp.py`, un mini solutore LP fornito
(enumerazione dei vertici, niente scipy): **non fa parte dell'esercizio**.

## Esecuzione

```bash
cd esercizi
./run_tests.sh              # scheletro  -> 0 passati, 50 falliti  (è il risultato atteso)
AGT_SOL=1 ./run_tests.sh    # soluzione  -> 50 passati, 0 falliti
```

Oppure una suite sola:

```bash
cd 03_core_nucleolo && python3 -m pytest -q
```

`run_tests.sh` controlla **prima di tutto** che `numpy` e `pytest` siano
importabili e, se manca qualcosa, stampa come sistemare invece di lasciarti in
mano una pila di `ModuleNotFoundError`. Se il tuo venv dei corsi ha numpy ma non
pytest:

```bash
source /percorso/al/venv/bin/activate
pip install pytest
```

oppure senza attivare niente:

```bash
PYTHON=/percorso/al/venv/bin/python ./run_tests.sh
```

## Regole con cui sono scritti

Il contratto completo è in `_SPEC.md`. In sintesi: solo `numpy` e stdlib;
determinismo via `np.random.default_rng(seed)` e mai `np.random.seed`, `random`
o `time`; ogni suite tutta rossa sullo scheletro e tutta verde sulla soluzione
(verificato eseguendola davvero in entrambe le modalità); e **almeno un oracolo
indipendente per esercizio** — lo stesso risultato ricalcolato per forza bruta o
direttamente dalla definizione, non la stessa formula riscritta.

Gli oracoli, in concreto:

| esercizio | oracolo indipendente |
|---|---|
| 01 | il minimax **non potato**: su 300 alberi casuali deve dare lo stesso valore dell'alfa-beta; più il bound di Knuth-Moore come test di sanità |
| 02 | la media sulle **n! permutazioni** contro la formula dei contributi marginali pesati (n fino a 7); più le forme chiuse dei giochi di unanimità e additivi |
| 03 | `θ(nucleolo) ≤_lex θ(y)` per 4000 preimputazioni casuali e per tutti i vertici del core — con `θ` **ricalcolato dentro il file di test**, non importato dal modulo sotto esame |
| 04 | l'enumerazione per forza bruta di tutti gli `n!` matching: DA deve coincidere con il best-stable-partner costruito componente per componente |

## Come usarli

Non sono un compito: sono un modo per non scoprire all'orale che una definizione
che sapevi recitare non la sapevi applicare. L'ordine consigliato è quello
numerico, ma `02` e `04` sono indipendenti e si possono fare per primi.

Il momento in cui questi esercizi rendono di più è il **09/09**, sul task
"Esercizi tipo esame + practicetest": usa le tue implementazioni come oracolo per
correggere i conti fatti a mano sul `practicetest.pdf`.
