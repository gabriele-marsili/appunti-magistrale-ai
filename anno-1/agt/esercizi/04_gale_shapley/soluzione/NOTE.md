# Note sulla soluzione — 04 Gale-Shapley

## Perché DA termina, e perché in ≤ n² passi

Ogni proponente propone a ciascun ricevente **al più una volta**: l'indice
`prossima[p]` non torna mai indietro. Quindi il numero totale di proposte è
limitato da `n²`. Termina quando nessuno è libero, e non può bloccarsi prima
perché un proponente ancora libero ha sempre almeno un ricevente non ancora
contattato (se li avesse contattati tutti, tutti lo avrebbero rifiutato per
qualcuno di meglio, quindi tutti i riceventi sarebbero accoppiati, quindi tutti
gli `n` proponenti sarebbero accoppiati — assurdo).

Questa è la dimostrazione da avere in testa: è breve e la chiedono.

## Perché l'output è stabile

Supponiamo `(p, r)` bloccante: `p` preferisce `r` al proprio partner. Allora `p`
ha proposto a `r` **prima** (scorre la lista in ordine) ed è stato rifiutato o
scaricato. Ma un ricevente non peggiora mai nel tempo: il partner che `r` tiene
alla fine è almeno buono quanto `p`. Quindi `r` non preferisce `p` al proprio
partner, contraddizione.

Il punto è la monotonia dal lato ricevente. Chi non la enuncia non ha la
dimostrazione.

## Proposer-optimality

Per induzione sull'ordine dei rifiuti: nessun proponente viene mai rifiutato da
un ricevente che gli sia *raggiungibile in qualche matching stabile*. Se
`r` rifiuta `p` per `p'`, e per assurdo `r` fosse raggiungibile da `p`, si
costruisce una coppia bloccante in quel matching stabile.

Corollario duale, che il test verifica numericamente: lo stesso matching è il
**peggiore** per i riceventi. Chi propone vince. È il motivo per cui nei
programmi reali di assegnazione (scuole, specializzandi) la scelta di *chi*
propone è politica, non tecnica — buona frase da avere pronta.

## Trappole

1. **`inverti` con `np.empty_like` su un array non int.** `mu` deve essere di
   dtype intero, altrimenti l'indicizzazione fallisce silenziosamente.
2. **Ricostruire `mu` da `tenuto`.** `tenuto[r] = p` è il matching dal lato
   ricevente; per ottenere `mu[p] = r` va invertito. Confondere i due lati è
   l'errore che fa fallire tutti i test a valle in modo confuso.
3. **`blocking_pairs` con scorciatoie.** Fermarsi alla prima coppia trovata va
   bene per `is_stable`, non per `blocking_pairs`, che deve restituirle tutte:
   serve a diagnosticare, non solo a decidere.
4. **`best_stable_partner` che restituisce l'indice invece del ricevente.**
   `min(..., key=rank)` deve iterare sui *partner* `mu[p]`, non sulle posizioni.
5. **Lista dei liberi come `set`.** L'ordine di iterazione di un `set` in Python
   dipende dagli hash e rompe il determinismo richiesto dallo spec. La soluzione
   usa una lista come stack. (Il risultato di DA non dipende dall'ordine — c'è un
   test apposta — ma il *conteggio delle proposte* sì.)

## Costo

- `deferred_acceptance`: `O(n²)` proposte, `O(n²)` totale con `rank_matrix`
  precalcolata.
- `blocking_pairs`: `O(n²)`.
- `all_stable_matchings`: `O(n! · n²)` — a `n = 6` sono 720 · 36 ≈ 26k
  operazioni, istantaneo; a `n = 9` sarebbe già scomodo. È forza bruta apposta:
  serve come oracolo, non come algoritmo.

Vale la pena notare che il numero di matching stabili può crescere
esponenzialmente in `n`, quindi "enumerarli tutti" non è una strategia
praticabile in generale — ed è esattamente perché serve Gale-Shapley.
