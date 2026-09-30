# _SPEC.md — contratto di scrittura degli esercizi (AGT)

> **Nota di provenienza.** Questo file è una *ricostruzione* dello `esercizi/_SPEC.md`
> della cartella GDL. In questa sessione era collegata **solo** la cartella AGT, quindi
> l'originale non era leggibile: lo spec qui sotto è riscritto dalla descrizione fornita,
> con l'unico adattamento richiesto `GDL_SOL` → `AGT_SOL`. Se l'originale contiene
> clausole ulteriori, vanno riportate qui a mano.

## Struttura di un esercizio

```
NN_slug/
  README.md              # la consegna: cosa implementare, con che firma, e perché
  slug.py                # scheletro: ogni funzione da implementare è marcata # TODO
  test_slug.py           # la suite pytest
  soluzione/
    slug_sol.py          # soluzione di riferimento
    NOTE.md              # note sulla soluzione: idee chiave, trappole, complessità
```

## Regole

1. **Dipendenze**: solo `numpy` e la standard library. Niente scipy, niente pandas,
   niente networkx, niente cvxpy.
2. **Determinismo**: ogni sorgente di casualità passa da `np.random.default_rng(seed)`
   con `seed` esplicito. Vietati `np.random.seed`, il modulo `random`, `time`,
   e qualunque cosa che dipenda dall'ordine di iterazione di un `set`.
3. **Rosso/verde**: la suite deve essere **interamente rossa** sullo scheletro
   (ogni test tocca almeno una funzione `# TODO`) e **interamente verde** sulla
   soluzione di riferimento. Va verificato eseguendola davvero in entrambe le modalità.
4. **Selettore di modalità**: la variabile d'ambiente `AGT_SOL`.
   - `AGT_SOL` non impostata (o ≠ `1`) → il test importa `slug.py` (lo scheletro).
   - `AGT_SOL=1` → il test importa `soluzione/slug_sol.py`.
   L'import avviene per path esplicito (`importlib.util.spec_from_file_location`),
   non via `sys.path`, così non serve nessun `conftest.py` né pacchetto installabile.
5. **Oracolo indipendente**: almeno un test per esercizio deve confrontare il risultato
   con lo stesso valore ottenuto **per forza bruta o direttamente dalla definizione**,
   non riscrivendo la stessa formula. Su AGT quasi tutto è piccolo ed esattamente
   verificabile: è il motivo per cui questi esercizi valgono qualcosa.
6. **Tolleranze**: confronti tra float con `np.allclose` / `pytest.approx` e tolleranza
   dichiarata. Mai `==` su float.
7. **Niente API di consegne aperte**: gli esercizi sono materiale di studio; non devono
   ricalcare la firma di un homework o midterm in corso.

## Esecuzione

```bash
./run_tests.sh          # scheletro  → tutto rosso (atteso)
AGT_SOL=1 ./run_tests.sh   # soluzione → tutto verde
```
