# SPEC per gli autori degli esercizi — LEGGERE PRIMA DI SCRIVERE

Ogni esercizio vive in `/home/claude/gdl/esercizi/<NN_slug>/` e contiene ESATTAMENTE:

```
<NN_slug>/
  README.md              consegna, in ITALIANO
  <slug>.py              skeleton con le firme e `raise NotImplementedError`
  test_<slug>.py         pytest suite
  soluzione/
    <slug>_sol.py        soluzione di riferimento, commentata
    NOTE.md              ragionamento, trappole, collegamento alle slide
```

## Vincoli tecnici NON NEGOZIABILI

1. **Solo `numpy` e stdlib.** Niente torch, scipy, sklearn, matplotlib. Il container non li ha.
2. **Determinismo assoluto.** Usa `np.random.default_rng(seed)` con seed espliciti. Mai `np.random.seed`, mai `random`, mai `time`.
3. **`<slug>.py` e `soluzione/<slug>_sol.py` espongono la STESSA identica API** (stessi nomi, stessa firma, stesso ordine argomenti, stesso tipo di ritorno). I test girano su entrambi.
4. Lo skeleton contiene già il codice NON didattico (generatori di dati, helper di plotting testuale, costanti). Lo studente implementa solo le funzioni marcate `# TODO`.
5. Ogni funzione dello skeleton ha docstring completa: cosa fa, shape esatte di input e output, convenzioni.

## Header obbligatorio di `test_<slug>.py`

```python
import os, sys, pathlib, importlib
HERE = pathlib.Path(__file__).parent
if os.environ.get("GDL_SOL"):
    sys.path.insert(0, str(HERE / "soluzione"))
    m = importlib.import_module("<slug>_sol")
else:
    sys.path.insert(0, str(HERE))
    m = importlib.import_module("<slug>")
```

Poi tutti i test usano `m.nome_funzione(...)`. Nessun `from <slug> import *`.

## Qualità dei test

- Fra 8 e 14 test. Ogni test una asserzione concettuale, con `assert ..., "messaggio che spiega COSA è sbagliato"`.
- Almeno un test è un **oracolo indipendente**: risultato calcolato con un metodo diverso e più lento (forza bruta, enumerazione, definizione) e confrontato. Non ricopiare l'implementazione dentro il test.
- Almeno un test verifica una **proprietà matematica** (normalizzazione a 1, simmetria, monotonia della log-likelihood, invertibilità, conservazione della massa...).
- Almeno un test è un **caso limite** (input degenere, un solo elemento, matrice identità, probabilità 0/1).
- I test devono FALLIRE sullo skeleton (che solleva `NotImplementedError`) e PASSARE sulla soluzione.
- Tolleranze: `np.testing.assert_allclose(..., rtol=1e-6, atol=1e-9)` per calcoli esatti; tolleranze esplicite e motivate per stimatori stocastici (e in quel caso alza il numero di campioni finché il test non è flaky — deve passare deterministicamente col seed fissato).
- Nessun test deve superare ~5 secondi.

## README.md dell'esercizio

Sezioni, in italiano, in prosa asciutta senza fronzoli:

- **Lezione di riferimento** — quale deck di `Lessons/`, quale argomento.
- **Cosa devi implementare** — elenco delle funzioni con una riga a testa.
- **Perché questo esercizio** — quale confusione concettuale scopre. Una frase, concreta.
- **Vincoli** — cosa non puoi usare.
- **Come autovalutarti** — `pytest test_<slug>.py -v` dalla cartella dell'esercizio.
- **Tempo stimato** — onesto.
- **Domande d'orale collegate** — 2-4 domande secche a cui l'esercizio ti prepara a rispondere.

Il README **non** contiene pezzi di soluzione né pseudocodice riga-per-riga. Contiene la specifica matematica (formule sì, quelle servono).

## soluzione/NOTE.md

Perché la soluzione è fatta così, quali sono gli errori tipici (es. dimenticare lo scaling nel forward-backward, usare `detach` dove non serve, confondere `axis=0` e `axis=1`), e il collegamento alla slide. Testo, non elenco puntato lungo.

## Verifica prima di consegnare

Esegui ENTRAMBI e riporta l'esito:

```bash
cd /home/claude/gdl/esercizi/<NN_slug>
GDL_SOL=1 python3 -m pytest test_<slug>.py -q     # deve essere tutto verde
python3 -m pytest test_<slug>.py -q                # deve fallire su tutti i test
```

Se il primo non è verde, il lavoro non è finito. Non consegnare test che non passano sulla tua stessa soluzione.
