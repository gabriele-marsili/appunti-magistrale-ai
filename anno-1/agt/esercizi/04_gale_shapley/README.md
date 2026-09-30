# 04 — Gale-Shapley, deferred acceptance e stabilità

**Lezioni**: L17 (matching, mercati di scambio), L18 (matching two-sided,
problema del matrimonio, deferred acceptance, stabilità, ottimalità per il lato
proponente).
**Tempo stimato**: ~2h.

## Perché questo esercizio esiste

Su Gale-Shapley ci sono due enunciati che all'orale vanno separati con chiarezza,
e che a parole si confondono continuamente:

1. **L'output di DA è stabile** — non esistono coppie bloccanti.
2. **L'output di DA è proposer-optimal** — ogni proponente ottiene il *migliore*
   partner che può avere in *qualunque* matching stabile; e simmetricamente è
   receiver-pessimal.

Il primo si verifica in `O(n²)` cercando tutte le coppie. Il secondo richiede di
conoscere *tutti* i matching stabili: qui si enumerano per forza bruta tutte le
`n!` biiezioni, si costruisce il vettore "miglior partner stabile" componente per
componente, e si verifica che coincida con l'output di DA. Fare questo confronto
è il modo per accorgersi che il secondo enunciato è molto più forte del primo —
e non deducibile da esso.

Bonus non ovvio che la suite verifica: il vettore dei migliori partner stabili è
*esso stesso* un matching (è il teorema del reticolo). A priori non c'è nessuna
ragione perché assegnare a ciascun proponente il suo optimum individuale produca
una biiezione.

## Convenzioni

- Due lati di uguale cardinalità `n`, preferenze strette e complete.
- `prop_prefs[p]` = lista ordinata dei riceventi (migliore per primo);
  `recv_prefs[r]` = lista ordinata dei proponenti.
- Un matching è `mu` con `mu[p] = r`.
- Forniti: `random_instance(rng, n)` e `inverti(mu)`.

## Da implementare in `gale_shapley.py`

| funzione | cosa deve fare |
|---|---|
| `rank_matrix(prefs)` | `R[i,j]` = posizione di `j` nella lista di `i` (0 = migliore) |
| `deferred_acceptance(prop_prefs, recv_prefs)` | `(mu, n_proposte)` |
| `blocking_pairs(mu, ...)` | **tutte** le coppie bloccanti, scansione esaustiva |
| `is_stable(mu, ...)` | nessuna coppia bloccante |
| `all_stable_matchings(...)` | forza bruta sulle `n!` biiezioni (n ≤ 6) |
| `best_stable_partner(stabili, prop_prefs)` | miglior partner stabile, per componente |
| `worst_stable_partner(stabili, prop_prefs)` | peggior partner stabile, per componente |

`best_stable_partner` va costruito **componente per componente** senza assumere
che il risultato sia un matching: è proprio quello che la suite verifica.

## Cosa verifica la suite

- **Oracolo 1**: l'output di DA non ha coppie bloccanti, controllate su tutte le
  `n²` coppie, per `n = 2..6` su 200 istanze. La stabilità è ricalcolata **dentro
  il test** con `.index()` sulle liste, senza usare `rank_matrix` né
  `blocking_pairs`.
- **Oracolo 2**: `all_stable_matchings` coincide con l'enumerazione delle
  permutazioni filtrata dal criterio di stabilità di riferimento.
- **Oracolo 3**: `deferred_acceptance(...) == best_stable_partner(all_stable, ...)`.
  Il test pretende che almeno 10 istanze abbiano più di un matching stabile,
  altrimenti si dichiara vacuo e fallisce.
- Il vettore dei migliori partner stabili è una biiezione ed è stabile.
- Scambiando i ruoli (riceventi che propongono) si ottiene esattamente il
  matching **peggiore** per i proponenti.
- DA termina in `≤ n²` proposte.
- DA è indipendente dall'ordine in cui si servono i proponenti liberi: rinominando
  i proponenti con una permutazione, l'output si rinomina di conseguenza.
- L'istanza classica a 2 con esattamente due matching stabili.

## Esecuzione

```bash
python3 -m pytest -q            # scheletro → 12 rossi
AGT_SOL=1 python3 -m pytest -q  # soluzione → 12 verdi
```
