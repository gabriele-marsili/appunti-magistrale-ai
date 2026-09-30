# 03 — Core, least core e nucleolo

**Lezioni**: L20 (imputazioni, core), L21 (core di Gillies, superadditività,
bilanciamento, Bondareva-Shapley), L22 (quasi-core, strong ε-core di
Shapley-Shubik, least core), L23 (excess, vettore ordinato di insoddisfazione,
nucleolo e prenucleolo).
**Tempo stimato**: ~2.5-3h. È il più lungo dei quattro.

## Perché questo esercizio esiste

Il nucleolo è la definizione più facile da recitare e più difficile da *usare*
di tutto il corso: «il punto che minimizza lessicograficamente il vettore ordinato
degli excess». Finché non lo si calcola davvero, resta una frase. Implementando lo
schema iterativo di Maschler si scopre che il punto delicato non è la
minimizzazione di ε — è capire **quali coalizioni restano attive in tutte le
soluzioni ottime** e vanno quindi congelate prima del giro successivo. Chi non
ha implementato questo di solito all'orale dice «poi si itera» e si ferma lì.

Il core, il least core e il segno di ε* stanno tutti nello stesso LP: vederli
come lo stesso oggetto (il core è lo strong ε-core con ε = 0) è metà della
lezione L22.

## Rappresentazione e strumenti forniti

Gioco TU come array `v` di lunghezza `2**n` indicizzato dalla maschera di bit
(stessa convenzione dell'esercizio 02). Vincolo pratico: **n ≤ 4**.

`lp.py` è **fornito** e non va toccato: risolve `min c·z` con vincoli lineari per
enumerazione dei vertici (ogni vertice rende attivi `d` vincoli indipendenti →
si prova ogni combinazione di `d` righe, si risolve il sistema quadrato, si tiene
il punto se ammissibile). È esponenziale ma esatto e non richiede scipy.
Interfaccia: `lp_min(c, A_ub, b_ub, A_eq, b_eq)` e `vertici_ammissibili(...)`.

Sono forniti anche `coalizioni_proprie`, `indicatore`, `random_game`,
`random_superadditive_game`, `majority_game`, `additive_game`.

## Da implementare in `core_nucleolo.py`

| funzione | cosa deve fare |
|---|---|
| `is_preimputation(v, n, x)` | `x(N) = v(N)` |
| `is_imputation(v, n, x)` | preimputazione + `x_i ≥ v({i})` |
| `excess(v, n, x)` | array `e(S,x) = v(S) − x(S)` indicizzato dalla maschera |
| `theta(v, n, x)` | excess delle `2**n − 2` coalizioni proprie, ordine decrescente |
| `lex_leq(a, b)` | ordine lessicografico |
| `in_core(v, n, x)` | tutti gli excess propri `≤ 0` |
| `core_vertices(v, n)` | vertici del core, `(k, n)`; `(0, n)` se vuoto |
| `least_core_epsilon(v, n)` | `min ε` t.c. lo strong ε-core è non vuoto |
| `nucleolus(v, n)` | schema di Maschler (vedi sotto) |

### Lo schema di Maschler, passo per passo

1. Uguaglianze iniziali: solo `x(N) = v(N)`. Coalizioni proprie tutte "libere".
2. Risolvi `min ε  s.t.  uguaglianze,  x(S) + ε ≥ v(S)  ∀S libera`.
   Variabili dell'LP: `(x_0, …, x_{n−1}, ε)`.
3. Trova le coalizioni libere **attive in ogni soluzione ottima**: per ciascuna `S`
   massimizza `x(S)` con `ε` fissato a `ε*`; se il massimo vale ancora
   `v(S) − ε*`, allora `S` è attiva ovunque → aggiungi l'uguaglianza
   `x(S) = v(S) − ε*` e togli `S` dalle libere.
4. Ripeti finché non restano libere, oppure finché il rango delle uguaglianze
   raggiunge `n` (a quel punto il punto è determinato).

Il passo 3 è il cuore: saltarlo e congelare semplicemente le coalizioni attive
*nel vertice trovato* dà risultati sbagliati quando l'ottimo di ε non è unico.

## Cosa verifica la suite

- **Oracolo principale**: `theta(nucleolo) ≤_lex theta(y)` per 4000 preimputazioni
  casuali (n=3) e 3000 (n=4). `theta` e l'ordine lessicografico sono **ricalcolati
  dentro il file di test** dalla definizione, quindi l'oracolo non dipende dal
  codice sotto esame.
- **Oracolo strutturato**: lo stesso confronto contro i vertici del core e i loro
  punti medi — punti "difficili", non casuali.
- **Coerenza core / least core**: `ε* ≤ 0` se e solo se `core_vertices` è non
  vuoto, su un pool misto di giochi casuali e superadditivi.
- **Valori a mano**: gioco di maggioranza a 3 → `ε* = 1/3` e nucleolo `(1/3,1/3,1/3)`;
  gioco additivo → nucleolo = vettore dei valori; gioco del simplesso → i tre
  vertici del core sono le colonne dell'identità.
- Il nucleolo sta nel core ogni volta che il core non è vuoto.
- `theta` ordinato in modo decrescente e di lunghezza `2**n − 2`.

## Esecuzione

```bash
python3 -m pytest -q            # scheletro → 15 rossi
AGT_SOL=1 python3 -m pytest -q  # soluzione → 15 verdi
```
