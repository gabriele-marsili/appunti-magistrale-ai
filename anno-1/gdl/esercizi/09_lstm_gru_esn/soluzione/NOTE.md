# Note sulla soluzione

## Il filo conduttore

GDL17 chiude con un problema: in una RNN vanilla il gradiente lungo il tempo è
un prodotto di fattori tutti uguali fra loro, e un prodotto di fattori tutti
uguali o svanisce o esplode. GDL18 dà le due risposte del corso, e questo
esercizio le mette una accanto all'altra perché sono più imparentate di quanto
sembri: **entrambe agiscono sulle proprietà spettrali della ricorrenza**. Il
gating le rende dipendenti dal contenuto e apprendibili (il forget gate è un
autovalore variabile, per canale e per istante); la randomizzazione rinuncia ad
apprenderle e le impone a mano una volta per tutte (il raggio spettrale del
reservoir). Chi risponde all'orale «LSTM e ESN sono due architetture diverse»
non ha visto il punto; la risposta è «sono due modi di controllare lo stesso
fattore moltiplicativo».

## sigmoid

Va scritta valutando sempre e solo `exp(-|z|)`, che sta in `(0,1]` e non può
andare in overflow:

    e = exp(-|z|)
    sigma(z) = 1/(1+e)   se z >= 0,     e/(1+e)   se z < 0

La versione con `np.where` calcola entrambi i rami ma nessuno dei due
overflowa, e funziona anche su array 0-dimensionali (l'indicizzazione booleana
su un array 0-d, che è l'altra implementazione comune, no). La versione ingenua
`1/(1+np.exp(-x))` con `x = -60` non è ancora un problema, ma i test usano bias
di modulo 60 e uno studente che li aumenti per prudenza si ritrova warning e
`nan`.

Dettaglio che serve nei test: `sigma(60)` vale **esattamente** `1.0` in float64.
Basta un argomento oltre circa 36.7, perché lì `exp(-x) < eps/2 ≈ 1.1e-16` e la
somma `1 + exp(-x)` arrotonda a 1. Simmetricamente `sigma(-60) ≈ 8.8e-27`, che
non è zero esatto ma è così piccolo da sparire in ogni somma con termini O(1).

## LSTM e il test che non ammette tolleranze

Il test `(a)` non usa `assert_allclose`: usa `np.all(C == c0)`. È voluto. Con
`f = 1.0` esatto e `i ≈ 1e-26`, la ricorrenza `c = f*c_prev + i*g` diventa
`c_prev + 1e-26`, e con `c_prev` dell'ordine di 1 quell'addendo è sotto l'ulp:
`c` resta identico bit a bit per 1000 passi. Un `assert_allclose` avrebbe
lasciato passare implementazioni sbagliate di poco; l'uguaglianza esatta no.

Perché `c0` è diverso da zero (`[0.7, -1.3, 2.0, 0.05]`)? Perché con `c0 = 0` i
`1e-26` non finirebbero sotto l'ulp — si accumulerebbero, e dopo 1000 passi
`c ≈ 1e-23 ≠ 0`. Il test fallirebbe pur essendo l'implementazione corretta. È
una trappola in cui si cade scrivendo il test, non risolvendo l'esercizio, ma
vale la pena saperla: l'esattezza in floating point è relativa alla scala.

I parametri saturi hanno pesi piccoli (`0.1`) e non nulli, di proposito: le gate
restano funzioni dell'input, ma il bias domina. Con `|W| ≤ 0.1` e ingressi in
`[-1,1]` più `|h| ≤ 1`, la deviazione della pre-attivazione è al massimo `0.7`,
lontanissima dai 60 del bias. Se avessi messo `W = 0` il test sarebbe passato
anche per un'implementazione che ignora `x_t` nelle gate.

Errori tipici sulla cella: scrivere `c = f*c_prev + g` (input gate dimenticato),
oppure `h = o * c` invece di `h = o * tanh(c)`, oppure applicare una `tanh`
anche a `c` prima di salvarlo — quest'ultimo distrugge il carousel, perché
`tanh` comprime e il prodotto dei fattori torna a essere `< 1`.

## constant_error_carousel_gradient: il verso del prodotto

È tre righe di codice e la parte difficile è tutta nell'indice.
`out[t] = d c_T / d c_t = prod_{s=t+1}^{T} f_s`. Con l'array 0-based in cui
`f_gates[j]` è `f_{j+1}`, i fattori sono quelli da `j = t` a `j = T-1`: il
prodotto cumulativo va **dal fondo verso l'inizio**, cioè
`flip -> cumprod -> flip`. Un `np.cumprod` diretto dà `out[t] = prod_{j<=t}`,
che è il fattore sbagliato (e nel test si becca subito, perché `out[-1]`
diventa il prodotto di tutto invece dell'ultimo forget gate).

Il test `(b-bis)` è quello che dimostra che questa non è una formula
decorativa. Perturba `c_0` per differenze finite dentro `lstm_forward` e
confronta `d c_T / d c_0` misurato con `prod f_s` calcolato. Perché il confronto
sia pulito, i parametri hanno le **colonne di stato azzerate**: se le gate
guardassero `h`, e `h = o tanh(c)` dipende da `c`, ci sarebbe un secondo
cammino `c -> h -> gate -> c` e la derivata totale non sarebbe più il solo
prodotto dei forget gate. Questo è anche il motivo per cui il constant error
carousel è un'affermazione sul **cammino diretto lungo la cella**, non sul
gradiente totale dell'LSTM: gli altri cammini esistono e possono ancora
svanire. Vale la pena dirlo all'orale, perché la versione da slide («l'LSTM non
ha vanishing gradient») è falsa in senso stretto.

Il confronto con la RNN vanilla nel test `(b)` usa la stessa identica funzione
applicata ai fattori `w * tanh'(a_s)` con `w = 1`, cioè il caso più favorevole
compatibile con la stabilità. Anche così `tanh' < 1` e su 1000 passi il
prodotto vale `~1e-46`. Non c'è nessuna scelta di `w` che salvi la situazione:
con `w` più grande il gradiente esplode invece di svanire. Il forget gate a 1
non è «un peso fortunato», è una struttura che rende il fattore *esattamente* 1.

## GRU: la convenzione del segno

Con la convenzione (A), `h = (1-z) n + z h_prev`, il gate `z` è un *keep gate*:
`z = 1` congela lo stato. Con la (B) è un *update gate* nel senso letterale:
`z = 1` lo sostituisce. Le due sono equivalenti a meno di `z -> 1-z`, cioè
cambiando segno a `Wz` e `bz` — la rete addestrata rappresenta la stessa
funzione, ma ogni affermazione sui *valori* del gate si ribalta. È il tipo di
dettaglio su cui una domanda d'orale può sembrare cattiva e invece sta solo
controllando che si sia letta la formula e non il riassunto.

Il test `(d)` verifica entrambi i limiti *e* il ruolo del reset gate: con
`r = 0` il candidato `n` non deve più dipendere da `h_prev`. L'errore
corrispondente è applicare `r` all'input (`Wn [r*x ; h_prev]`) o al risultato
finale; entrambi producono una rete che funziona più o meno, e sono
indistinguibili senza un test come questo.

Nota sulla saturazione a `z = 0`: `1 - 8.8e-27` arrotonda a `1.0` esatto e
`8.8e-27 * h_prev` sparisce nella somma, quindi `h` viene esattamente `n`. Il
test usa comunque `atol=1e-15` per non dipendere da questo dettaglio.

## Il conteggio dei blocchi

Quattro blocchi per LSTM, tre per GRU: `4 * (Hdim*(D+Hdim) + Hdim)` contro
`3 * (...)`, rapporto esatto 4:3. Contare i parametri non basta a testare il
codice dello studente (il dict lo costruisce il test), quindi il test `(e)`
aggiunge una verifica *funzionale*: perturba il bias di ciascun blocco e
controlla che l'uscita della cella cambi. Se qualcuno implementa l'LSTM
dimenticando l'output gate, il conteggio resta giusto e la perturbazione lo
smaschera. Lo stesso vale per il controllo che `gates` abbia esattamente le
chiavi attese.

La differenza strutturale che conta all'orale non è il numero di parametri ma
il fatto che la GRU abbia **un solo stato**. Nell'LSTM `c` è lo stato protetto
(il carousel) e `h` è ciò che viene esposto attraverso l'output gate: si può
mantenere un'informazione in `c` senza esporla. La GRU collassa i due e perde
questa separazione, in cambio di un terzo di parametri in meno e in genere di
un addestramento più rapido su dataset piccoli.

## ESN: il reservoir

Il riscalamento va fatto **dopo** la sparsificazione, altrimenti azzerare le
entrate cambia lo spettro e il raggio spettrale finale non è quello richiesto.
Il test lo controlla esplicitamente con `sparsity = 0.9`.

Il raggio spettrale è il massimo **modulo** degli autovalori, che per una
matrice non simmetrica sono complessi: `np.max(np.abs(np.linalg.eigvals(W)))`.
Chi usa `np.max(eigvals(W))` prende la parte reale del maggiore in senso
lessicografico e ottiene numeri senza senso; chi usa `np.linalg.norm(W)`
calcola la norma di Frobenius, che è un maggiorante grossolano.

La sparsità è imposta con `rng.permutation` e non con una maschera di
Bernoulli, così il conteggio è esatto e il test può usare l'uguaglianza. È una
scelta di progetto dell'esercizio, documentata nella docstring: entrambe le
implementazioni sarebbero legittime in un ESN vero, ma solo una è testabile
senza tolleranze statistiche. Vale la pena notare che nella pratica la sparsità
del reservoir serve a rendere il prodotto matrice-vettore economico, non a
migliorare le prestazioni: un reservoir denso funziona altrettanto bene.

`input_scaling` non è un dettaglio: regola quanto l'input spinge il reservoir
verso la saturazione della `tanh`. Con input molto grandi il reservoir satura,
la dinamica diventa quasi binaria e la memoria crolla; con input minuscoli il
reservoir lavora nella zona lineare della `tanh` e diventa un filtro lineare.
Nel test sulla ESP è tenuto a `0.3` proprio perché un input troppo forte può
indurre la echo state property anche con `rho > 1` (la saturazione della `tanh`
è essa stessa contrattiva): sarebbe un test che passa per il motivo sbagliato.

## Il test sulla echo state property

È il test concettuale centrale ed è costruito in modo da misurare la ESP per
quello che è, senza mai passare dal raggio spettrale. La firma di `esn_states`
non prende uno stato iniziale — parte sempre da zero — quindi due stati
iniziali diversi si ottengono mandando **due prefissi diversi**, dopodiché si
alimenta la **stessa** sequenza comune e si guarda la distanza fra le due
traiettorie. È esattamente la definizione operativa: *state forgetting*.

I numeri: con `rho = 0.9` le traiettorie partono a distanza `1.3` e dopo 300
passi di input comune stanno a `~7e-16`, cioè precisione macchina — hanno
dimenticato. Con `rho = 1.5` restano a distanza media `~1.3` indefinitamente.
Da notare che con `rho = 1.5` gli stati **non divergono** numericamente, perché
la `tanh` li tiene in `[-1,1]`: restano semplicemente diversi. La dinamica è
caotica, non esplosiva. È una precisazione utile all'orale, dove «senza ESP il
reservoir esplode» è un'affermazione che si sente spesso ed è falsa.

`echo_state_property_holds` implementa la condizione **necessaria** (raggio
spettrale della matrice effettiva `< 1`), e la docstring documenta anche quella
**sufficiente** (`sigma_max < 1`), che è più forte. La distinzione va tenuta
ferma: `rho(W) <= ||W||_2` sempre, quindi la sufficiente implica la necessaria
e fra le due c'è una fascia in cui nessuna decide. Gli ESN si usano proprio in
quella fascia, con `rho` appena sotto 1, perché la condizione sufficiente
darebbe reservoir a memoria cortissima. Se si dovesse rispondere in una riga:
«`rho < 1` non garantisce nulla in generale, ma in pratica funziona sempre e
massimizza la memoria; `sigma_max < 1` garantisce ma costa troppa memoria».

Il test `(k)` verifica il caso leaky su una matrice diagonale piccola, dove il
conto si fa a mano: `W = diag(-2, 0.1)` ha `rho = 2` e nessuna ESP con `a = 1`,
ma con `a = 0.4` la matrice effettiva `(1-a)I + aW` ha autovalori `-0.2` e
`0.64`, quindi `rho = 0.64` e la ESP vale. Il leak rate non è un dettaglio di
smoothing: **cambia lo spettro**.

## Il readout

`Wout = (S^T S + ridge I)^{-1} S^T Y`, con `I` di dimensione `Nres` (non `N`).
Il test `(h)` non ricopia questa formula: costruisce il sistema aumentato

    [ S            ]        [ Y ]
    [ sqrt(ridge) I]  w  =  [ 0 ]

e lo risolve con `np.linalg.lstsq`, che usa una SVD e non passa dalle equazioni
normali. Sono la stessa soluzione perché il funzionale dei minimi quadrati sul
sistema aumentato è `||S w - Y||² + ridge ||w||²`, cioè il funzionale ridge. È
un oracolo indipendente in senso pieno: metodo numerico diverso, e formulazione
del problema diversa.

Errori tipici: usare `ridge/N` invece di `ridge` (regolarizzazione scalata sul
numero di campioni — è una convenzione diffusa, ma non quella di questa
firma), oppure invertire la matrice con `np.linalg.inv` invece di risolvere con
`solve` (funziona, ma è meno stabile e più lento), oppure regolarizzare anche
un'eventuale colonna di bias.

`esn_fit_readout` gestisce sia target 1-D che 2-D restituendo un `Wout` della
dimensionalità corrispondente. È zucchero, ma evita che lo studente si trovi
shape `(Nres, 1)` dove si aspettava `(Nres,)` e sbagli il broadcasting nel
calcolo dell'MSE.

## Il memory task

Con `Nres = 200`, `rho = 0.9`, `washout = 100` e `delay = 5`, l'MSE sul test è
`1.2e-3` contro `0.366` della baseline che predice la media: un fattore 300. La
capacità di memoria degrada con il ritardo in modo prevedibile — allo stesso
reservoir, `delay = 1` dà `4.7e-5`, `delay = 10` dà `1.1e-2`, `delay = 20` dà
`0.28`, cioè quasi la baseline. C'è un risultato classico di Jaeger che dice che
la capacità di memoria totale di un reservoir lineare è limitata da `Nres`; con
la non linearità si compra espressività e si paga memoria.

Il punto da non perdere: `Win` e `Wres` in questo test non vengono mai
toccati. Tutto l'apprendimento è una soluzione in forma chiusa di un sistema
lineare. Nessun gradiente, nessuna epoca, nessun problema di ottimizzazione non
convessa — e quindi nemmeno vanishing gradient, che è il modo più radicale di
risolverlo: non fare backpropagation through time affatto.

L'allineamento fra stati e target è l'altro punto in cui si sbaglia: `esn_states`
scarta i primi `washout` stati, quindi anche i target vanno tagliati allo stesso
modo (`Y[washout:]`). Se ci si dimentica, si addestra il readout a predire il
target di `washout` passi dopo e l'MSE resta vicino alla baseline.

## Collegamento alle slide

GDL18 segue tre movimenti e l'esercizio li ricalca nell'ordine. Primo: i
neuroni con gating e l'idea che la soluzione naive `h_t = h_{t-1} + c(x_t)`
abbia lo spettro giusto ma saturi la memoria, da cui la necessità di
«controllare il dimenticare» — è il forget gate e il test `(a)`. Secondo: LSTM
e GRU come due punti diversi nel compromesso fra capacità e numero di
parametri — test `(c)`, `(d)`, `(e)`. Terzo: gli approcci randomizzati, dove si
rinuncia ad addestrare la ricorrenza e si controllano *solo* le proprietà di
memoria, cioè lo spettro — test `(f)`, `(g)`, `(k)`, e la parte di readout in
`(h)` e `(i)`. La lezione chiude con la modellazione autoregressiva con RNN,
che questo esercizio non tocca ma che poggia sullo stesso stato ricorrente.
