# 13 — Normalizing flows: cambio di variabile, invertibilità, log-det

## Lezione di riferimento

`Lessons/GDL27-28 flows.pdf` — *Tractable density models: Normalizing Flows*.
Slide sul cambio di variabile probabilistico (`Linear 1D — Mass conservation`,
`Multidimensional flow`, `General Multistep Case`, `Some considerations &
desiderata`) e sui coupling flow (`Coupling Flows`, `NICE`, `RealNVP —
Multiscale Nonlinear Flow`, `RealNVP — Masking and Squeezing`). È la lezione dei
modelli a **verosimiglianza esplicita e trattabile**: a differenza del VAE non
si ottimizza un bound, si calcola `log P(x)` esatta — al prezzo di richiedere
che ogni layer sia una bigezione con Jacobiano a determinante calcolabile.

## Il problema

Una densità complicata si ottiene deformando una densità semplice. Se `z` ha
densità nota `P(z)` e `x = f^{-1}(z)` con `f` invertibile e differenziabile, la
massa si conserva (`P(z) dz = P(x) dx`) e la densità trasformata è

    P(x) = P(z) · |det ∂f(x)/∂x|,        z = f(x)

cioè, in log e per una composizione di `N` layer,

    log P(x) = log P(z_0) + Σ_{i=1..N} log |det J_{z_{i-1}} f_i|

Tutto l'esercizio sta in tre cose: che `f` sia **esattamente** invertibile (non
approssimativamente), che il fattore di volume sia calcolato senza costruire lo
Jacobiano, e che sia valutato **nel punto giusto** di ogni layer.

### Convenzione di direzione — leggila prima di scrivere codice

Il deck chiama *forward/generative* la mappa `z → x` e *inverse/normalizing* la
mappa `x → z`, ma poi scrive la log-verosimiglianza rispetto alla seconda:

    log P(x) = log P(f(x)) + log det J_x f

In questo esercizio si adotta quest'ultima. Quindi:

| funzione | direzione | uso |
| --- | --- | --- |
| `flow_forward` | `f : x → z` (normalizzante) | verosimiglianza, apprendimento |
| `flow_inverse` | `f^{-1} : z → x` (generativa) | campionamento |

Se scambi le due, l'invertibilità continua a valere ma il segno del log-det
nella log-verosimiglianza si ribalta e la densità non integra più a 1.

## Cosa devi implementare

| funzione | cosa fa |
| --- | --- |
| `affine_coupling_forward(x, params, mask)` | coupling affine RealNVP, `x → y` |
| `affine_coupling_inverse(y, params, mask)` | inversa esatta in forma chiusa, `y → x` |
| `affine_coupling_log_det(x, params, mask)` | `log |det J|` del coupling, uno per riga |
| `flow_forward(x, layers)` | composizione dei coupling, `x → z` |
| `flow_inverse(z, layers)` | inversa della composizione, `z → x` |
| `flow_log_det(x, layers)` | somma dei log-det, ognuno nel proprio punto |
| `log_prob(x, layers)` | `log P(f(x)) + log |det J_x f|`, con `P(z) = N(0, I)` |
| `sample(layers, n, rng)` | `z ~ N(0, I)` seguito da `flow_inverse` |
| `planar_flow_forward(x, u, w, b)` | `f(x) = x + u h(wᵀx + b)`, `h = tanh` |
| `planar_flow_log_det(x, u, w, b)` | `log(1 + uᵀψ(x))` |
| `enforce_invertibility(u, w)` | riparametrizza `u` in modo che `wᵀu ≥ −1` |

## Specifica matematica

**Coupling affine (RealNVP).** Con maschera binaria `b ∈ {0,1}^D` e due reti
`θ_A` (log-scala) e `θ_B` (traslazione), entrambe valutate sulla sola metà
mascherata:

    y = b ⊙ x + (1 − b) ⊙ { exp(θ_A(b ⊙ x)) ⊙ x + θ_B(b ⊙ x) }

Le componenti con `b_i = 1` escono **identiche**; le altre vengono scalate e
traslate da funzioni delle prime. Riordinando le coordinate in
`[copiate | trasformate]` lo Jacobiano è triangolare a blocchi

    [ I                  0                      ]
    [ ∂(·)/∂x_copiate    diag(exp(θ_A(b ⊙ x)))  ]

quindi

    log |det J| = Σ_{i : b_i = 0} [θ_A(b ⊙ x)]_i

Il blocco fuori diagonale — che contiene tutte le derivate delle due reti — non
entra nel determinante: per questo le reti possono essere arbitrariamente
complicate senza costare niente. La traslazione `θ_B` non compare affatto.

**Inversa.** Poiché `b ⊙ y = b ⊙ x`, le due reti si rivalutano sullo stesso
identico input del forward senza conoscere `x`:

    x = b ⊙ y + (1 − b) ⊙ (y − θ_B(b ⊙ y)) / exp(θ_A(b ⊙ y))

È in forma chiusa: nessuna iterazione, nessun solver.

**Composizione.** Le maschere dei layer consecutivi vanno **alternate**
(`make_flow` lo fa già), altrimenti le stesse componenti restano copiate per
sempre e la densità in quelle dimensioni resta gaussiana. Per l'inversa i layer
si percorrono al contrario: `f^{-1} = f_1^{-1} ∘ … ∘ f_N^{-1}`.

**Densità.** Con base `P(z) = N(0, I)`:

    log P(z) = −½‖z‖² − (D/2) log(2π)
    log P(x) = log P(f(x)) + log |det J_x f|

**Flusso planare** (Rezende & Mohamed 2015, la formulazione originale dei
normalizing flow; il deck di Bacciu presenta i coupling flow, il planare è qui
per isolare il vincolo di invertibilità in un caso minimo). Con `h = tanh`:

    f(x) = x + u h(wᵀx + b)
    ψ(x) = h'(wᵀx + b) · w,      h' = 1 − tanh²
    J    = I + u ψ(x)ᵀ
    log |det J| = log(1 + uᵀψ(x))

Lo Jacobiano è una perturbazione di rango 1 dell'identità: per il lemma del
determinante matriciale `det(I + u ψᵀ) = 1 + ψᵀu`, calcolabile in `O(D)` senza
costruire la matrice.

**Vincolo di invertibilità.** `f` è invertibile solo se `1 + uᵀψ(x) > 0` per
ogni `x`. Siccome `h' ∈ (0, 1]`, una condizione sufficiente è `wᵀu ≥ −1`. Si
impone spostando `u` lungo `w`, senza toccare la componente ortogonale:

    m(a) = −1 + softplus(a)
    û = u + (m(wᵀu) − wᵀu) · w / ‖w‖²

Per costruzione `wᵀû = m(wᵀu) ≥ −1`. Senza questo vincolo `1 + uᵀψ(x)` può
diventare negativo: il logaritmo dà NaN, e giustamente — quella trasformazione
non è una bigezione e la "densità" che se ne ricava non esiste.

## Perché questo esercizio

Scopre tre confusioni.

1. **Che il log-determinante non sia un dettaglio ma il cuore del modello.**
   Chi lo tratta come un termine di regolarizzazione da aggiungere lo valuta
   tutto nello stesso punto `x` invece che, layer per layer, sull'ingresso di
   quel layer. Il flusso resta perfettamente invertibile e i numeri restano
   plausibili: solo l'integrale della densità smette di fare 1. Il test contro
   lo Jacobiano numerico è lì per questo.
2. **Che "conserva i volumi" e "è l'identità" siano la stessa cosa.** Con
   `log_scale ≡ 0` il coupling diventa un NICE: sposta i punti eccome, ma
   `log |det J| = 0` esattamente. Il fattore di volume misura la *deformazione*,
   non lo spostamento.
3. **Che l'invertibilità sia una proprietà che si ottiene "quasi sempre".** Nel
   coupling è strutturale — è garantita dall'architettura, per qualunque valore
   dei pesi, ed è per questo che si progettano flussi così. Nel flusso planare
   va imposta esplicitamente sui parametri, e se non la imponi il modello
   produce log-det negativi o NaN durante l'addestramento.

C'è poi la confusione di direzione: `forward` è quello generativo o quello
normalizzante? Il deck usa entrambe le convenzioni in slide diverse, e il segno
del log-det dipende da quale scegli.

## Vincoli

Solo `numpy` e la standard library. Niente `torch`, `scipy`, `sklearn`,
`matplotlib`. Nessuna differenziazione automatica: gli Jacobiani vanno
calcolati analiticamente, mai costruendo la matrice `D × D`. Ogni sorgente di
casualità passa dal `rng` (`numpy.random.Generator`) che ricevi come argomento:
mai `np.random.seed`, mai il modulo `random`, mai `time`.

Non toccare `softplus`, `standard_normal_logpdf`, `alternating_mask`,
`random_coupling_params`, `make_flow` e `mlp`: sono già forniti e i test li
usano per costruire flussi identici sullo skeleton e sulla soluzione.

## Come autovalutarti

```bash
cd /home/claude/gdl/esercizi/13_flow
python3 -m pytest test_flow.py -v
```

Tutti i test devono passare. Ogni asserzione ha un messaggio che indica quale
errore concettuale l'ha fatta fallire; leggilo prima di correggere a caso. Il
test più informativo è `test_flow_log_det_contro_jacobiano_numerico`: confronta
la tua formula chiusa con `log|det J|` di uno Jacobiano costruito colonna per
colonna a differenze finite.

## Tempo stimato

100 minuti. Il coupling forward è di tre righe, l'inversa di quattro; il tempo
se ne va su `flow_log_det` (capire *dove* va valutato ogni termine) e sul flusso
planare (derivare `ψ` e capire da dove esce il vincolo `wᵀu ≥ −1`).

## Domande d'orale collegate

1. Scrivi la formula del cambio di variabile per una composizione di `N` flussi
   e spiega perché il segno del log-determinante cambia a seconda che si
   consideri la direzione generativa o quella normalizzante.
2. Perché un coupling layer ha lo Jacobiano triangolare, e perché questo
   permette di usare reti neurali arbitrariamente complesse per scala e
   traslazione senza pagarne il costo nel determinante?
3. Che cosa rende un coupling layer invertibile in forma chiusa, e perché
   l'inversa non richiede di invertire le reti `θ_A` e `θ_B`?
4. Perché nei flussi le maschere dei layer consecutivi vanno alternate?
5. Un flusso residuo `z' = z + θ(z)` è invertibile solo se `θ` è Lipschitz con
   costante `< 1`. Che cosa gioca lo stesso ruolo nel flusso planare, e come si
   impone?
6. Quali sono i vantaggi e gli svantaggi dei normalizing flow rispetto a un VAE,
   in termini di verosimiglianza, campionamento e dimensione dello spazio
   latente?
