# Note sulla soluzione

## Il filo conduttore

Tutte le funzioni di questo esercizio esistono per la stessa ragione: `Z` non si
calcola. La lezione GDL13 introduce il campionamento come sostituto
dell'integrazione, e ogni metodo qui dentro è un modo diverso di aggirare la
costante di normalizzazione. Rejection la aggira accettando con probabilità
proporzionale a `p~/(M q)`; importance sampling la stima implicitamente col
denominatore `Σ w`; Metropolis-Hastings la fa sparire perché appare al
numeratore e al denominatore del rapporto. Se uno studente ha capito questo, il
resto è aritmetica.

## Rejection sampling

Due dettagli fanno la differenza fra un'implementazione giusta e una che sembra
giusta.

Il primo è la firma: `n` è il numero di campioni **accettati** da restituire, non
il numero di proposte da generare. Quindi serve un ciclo. La soluzione genera
blocchi di dimensione `⌈(n − accettati) · M · 1.05⌉`: in un colpo solo si copre
quasi sempre il fabbisogno, senza il ciclo Python campione per campione che
renderebbe il test da 200 000 campioni lento. Il fattore `1.05` è margine, non
matematica; il `max(64, ·)` evita blocchi minuscoli nelle ultime iterazioni.

Il secondo è che `acceptance_rate` deve contare **tutte** le proposte generate e
**tutte** quelle accettate, comprese quelle in eccesso che poi vengono scartate
dal troncamento `[:n]`. Se conti solo `n / proposte`, con blocchi che
sovradimensionano ottieni una stima distorta verso il basso. Il test `(b)`
confronta contro `1/M` con `rtol=0.02` proprio per prendere questo errore.

L'identità `P(accetto) = 1/M` vale solo se **entrambe** le densità sono
normalizzate. Con `p~` non normalizzata la probabilità è `Z/M`. È una buona
domanda d'orale: l'acceptance rate della rejection su una posterior non
normalizzata è un stimatore (a meno di `M`) di `Z`.

Errore tipico: confrontare `u ≤ p~(x) / (M q(x))` calcolando esplicitamente il
rapporto. Matematicamente identico, ma se `q(x)` va in underflow lontano dalle
code si ottiene `0/0`. La forma `u · M · q(x) ≤ p~(x)` non ha questo problema.

## Importance sampling

`importance_weights` deve restituire i pesi **grezzi**. La tentazione di
normalizzarli dentro è forte perché "tanto poi si normalizzano lo stesso", ma
allora `effective_sample_size` perde significato (con pesi normalizzati
`(Σw)² = 1` e l'ESS diventa `1/Σw²`, che è la stessa cosa solo per caso — e la
funzione non è più riutilizzabile per stimare `Z`). Il test asserisce
esplicitamente che `Σ w ≠ 1`.

L'errore concettuale grosso è in `self_normalized_importance_estimate`: dividere
per `n` invece che per `Σ w`. Con `p~` non normalizzata sbagli di un fattore `Z`
(qui `Z ≈ 3.71`, quindi la media stimata è fuori di quasi un fattore quattro).
Il test lo verifica sia direttamente contro `MU_TRUE`, sia con la proprietà di
invarianza: moltiplicando `p~` per 137 la stima non deve cambiare di un bit.
Quella proprietà è vera *solo* per lo stimatore self-normalized ed è il modo più
economico di controllare di averlo scritto giusto.

Lo stimatore self-normalized è consistente ma **distorto** per `n` finito
(rapporto di due medie): è il prezzo di non conoscere `Z`. Vale la pena saperlo
dire all'orale.

## Metropolis-Hastings

Tre punti.

Primo, tutto in spazio log. `p~` per una posterior realistica vale `1e-300` e
il rapporto in spazio densità dà `0/0`. In log il rapporto è una sottrazione e
la condizione di accettazione diventa `log u < log p~(y) − log p~(x)`. Il
`min(1, ·)` non serve scriverlo: se `log p~(y) ≥ log p~(x)` allora la differenza
è `≥ 0 > log u` e si accetta sempre, perché `log u < 0`. Quando `log_target`
restituisce `-inf` la differenza è `-inf` e si rifiuta, senza casi speciali.
`np.log(0)` va protetto con `np.errstate(divide="ignore")` per non stampare
warning.

Secondo: **quando si rifiuta, lo stato si ripete**. `chain[t] = x` sta fuori
dall'`if`. Chi scrive `chain[t] = y` solo in caso di accettazione e lascia il
resto a zero, o chi tiene solo gli stati accettati, non ha una catena di Markov
con la distribuzione invariante giusta — ha un campione dalle regioni ad alta
densità, con varianza sottostimata.

Terzo: la simmetria della proposal è ciò che permette di scrivere `α` senza i
termini `q`. Con un random walk gaussiano `q(y|x) = N(y; x, σ²) = N(x; y, σ²) =
q(x|y)`. Se si usasse una proposal asimmetrica (per esempio un'estrazione
indipendente da `N(0,1)`) e si tenesse la stessa formula, la catena
convergerebbe alla distribuzione sbagliata. Il test `(f)` è costruito per
prenderlo: partendo da 60 000 punti già distribuiti come `N(0,1)`, dopo un passo
si controllano i primi quattro momenti. Se si accetta sempre, la varianza sale
verso `1 + σ² = 1.81` e il momento quarto verso `9.9` invece di `3`. Se si
inverte il rapporto, la catena si contrae verso la moda. È il test più
informativo della suite dopo quello su Gibbs, perché controlla la proprietà che
*definisce* un sampler MCMC corretto — l'invarianza — e non la semplice
ergodicità (che è quello che verifica il test `(e)` con la media e la varianza di
una catena lunga).

Il valore atteso dell'acceptance rate: per un random walk su `N(0,1)` con
`σ = 2.4` è circa `0.44`, che è anche l'ottimo asintotico noto in dimensione 1.
Con `σ = 0.5` sale a `0.84` ma la catena si muove pochissimo (autocorrelazione
altissima); con `σ = 5` scende a `0.25` e la catena resta ferma spesso. È il
compromesso classico: acceptance rate alto non significa buon sampler.

## Gibbs

L'aggiornamento è **sequenziale**: `x2` va aggiornato usando l'`x1` appena
calcolato, non quello del passo precedente. La versione "Jacobi" (entrambi
dal vecchio stato) è un errore silenzioso: produce comunque una catena, le
marginali sembrano ragionevoli, ma la correlazione empirica non torna. Il test
`(g)` con `ρ = 0.8` la scarta.

L'altro errore è confondere varianza condizionale e varianza marginale. La
condizionale ha varianza `1 − ρ² = 0.36`, la marginale ha varianza `1`. Chi usa
`sd = 1` nella condizionale ottiene marginali con varianza `1/(1−ρ²)`.

## Il test chiave: Gibbs è Metropolis-Hastings

Sia `x = (x_i, x_{−i})` e la proposta `x' = (x'_i, x_{−i})`, che tocca una sola
coordinata. Se come proposal usiamo la condizionale completa
`q(x' | x) = p(x'_i | x_{−i})`, il rapporto di Metropolis-Hastings è

    α = [ p(x') · q(x | x') ] / [ p(x) · q(x' | x) ]

Adesso il punto: `x'` e `x` hanno le **stesse** componenti `x_{−i}`, quindi
`q(x | x') = p(x_i | x'_{−i}) = p(x_i | x_{−i})`. Fattorizzando la congiunta,

    p(x')  = p(x'_i | x_{−i}) · p(x_{−i})
    p(x)   = p(x_i  | x_{−i}) · p(x_{−i})

e sostituendo:

    α = [ p(x'_i | x_{−i}) p(x_{−i}) · p(x_i | x_{−i}) ]
        ────────────────────────────────────────────────  = 1
        [ p(x_i  | x_{−i}) p(x_{−i}) · p(x'_i | x_{−i}) ]

Numeratore e denominatore contengono gli stessi quattro fattori. Gibbs è quindi
un MH che accetta sempre, e non è un caso fortunato: è la conseguenza di aver
scelto come proposal esattamente la condizionale della target.

Il test `test_gibbs_e_metropolis_hastings_con_ratio_uno` lo verifica
numericamente. Due scelte di progetto meritano una parola. Primo, i punti in cui
si valuta il rapporto sono stati veri della catena prodotta da
`gibbs_bivariate_normal`, non punti arbitrari: così il test dipende
dall'implementazione dello studente (e fallisce sullo skeleton) e i punti sono
distribuiti secondo la target. Secondo, il test contiene la **controprova**: con
una proposal indipendente `N(0,1)` al posto della condizionale completa, il
rapporto si allontana da 1. Senza quella parte, `assert_allclose(ratio, 1.0)`
sarebbe sospettabile di essere una tautologia algebrica scritta male.

Da qui discende anche il modo giusto di rispondere all'orale a "Gibbs converge?":
converge perché è MH, e MH lascia invariata la target per costruzione
(bilancio dettagliato); Gibbs eredita l'invarianza, non la dimostra da capo. E
il fatto che accetti sempre non lo rende automaticamente migliore — un sampler
che accetta sempre ma si muove poco (ρ vicino a 1) ha ESS pessima.

## Diagnostica

Il denominatore dell'autocorrelazione è `N` per **ogni** lag, non `N − k`. Usare
`N − k` sembra più corretto (è la media su quei termini) ma produce uno
stimatore a varianza esplosiva ai lag alti e può dare `|ρ_k| > 1`: la
convenzione MCMC standard è `N`. L'oracolo del test ricalcola la definizione a
doppio ciclo Python e scarta la variante `N − k`.

Nella ESS MCMC la somma va troncata al primo `ρ_k ≤ 0` (*initial positive
sequence* di Geyer). Sommare tutti i `max_lag` lag significa sommare rumore: per
una catena i.i.d. le `ρ_k` sono `O(1/√N)` con segno casuale e il risultato
diventa instabile. Con il troncamento, campioni i.i.d. danno `ESS ≈ N` (nel test
`19 922` su `20 000`), mentre una catena di Gibbs con `ρ = 0.95` dà `≈ 980`, cioè
il 5%: l'autocorrelazione per sweep è `ρ² = 0.9025` e il tempo integrato è
`(1+0.9025)/(1−0.9025) ≈ 19.5`. Il clamp finale a `[1, N]` evita valori assurdi
su catene degeneri.

Nota terminologica che vale la pena tenere ferma: `effective_sample_size` (pesi
di importanza) e `mcmc_effective_sample_size` (catena) misurano cose diverse —
degenerazione dei pesi contro correlazione temporale — e per questo sono due
funzioni separate con due formule diverse.

## Collegamento alle slide

GDL13 introduce il campionamento come strumento per approssimare attese
intrattabili, elenca le proprietà dei sampler, passa dalle univariate (inverse
transform, rejection) alle multivariate (ancestor sampling, Gibbs) e chiude con
MCMC e con l'inferenza approssimata per LDA. L'esercizio ricalca quella
progressione e si ferma esattamente sul punto che la lezione usa come cerniera
fra Gibbs e MCMC: Gibbs non è un metodo a sé, è MH con la proposal giusta.
