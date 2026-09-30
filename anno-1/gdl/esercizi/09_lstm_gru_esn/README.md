# 09 — LSTM, GRU, Echo State Network

## Lezione di riferimento

`Lessons/GDL18 grn.txt` — *Gated Recurrent Models*. Neuroni con gating, Long
Short-Term Memory, Gated Recurrent Unit, approcci randomizzati (Echo State
Network), modellazione autoregressiva con RNN. È la lezione che risponde alla
domanda lasciata aperta da `GDL17 propagation.txt`: la RNN vanilla soffre di
exploding/vanishing gradient, e ci sono esattamente due modi di uscirne — o si
impara a controllare la propagazione (gating), o si rinuncia ad addestrare la
parte ricorrente e la si sceglie con le proprietà spettrali giuste
(randomizzazione).

## Il problema

Nella lezione precedente si è visto che in una RNN vanilla

    h_t = tanh(W h_{t-1} + U x_t)

il gradiente che risale dal passo `T` al passo `t` è

    d h_T / d h_t = prod_{s=t+1}^{T} W^T diag(tanh'(a_s))

e quel prodotto è condannato: se il fattore per passo è `< 1` il gradiente
svanisce esponenzialmente, se è `> 1` esplode. Non c'è un valore dei pesi che
lo eviti, perché il fattore è lo *stesso* per tutti i passi e per tutti i
contenuti — la rete non può decidere di ricordare una cosa e dimenticarne
un'altra. La soluzione naive `h_t = h_{t-1} + c(x_t)` (identità sulla
ricorrenza) ha le proprietà spettrali giuste ma satura la memoria: accumula
tutto, per sempre. Serve *controllare il dimenticare*.

## Cosa devi implementare

| funzione | cosa fa |
| --- | --- |
| `sigmoid(x)` | sigmoide logistica **stabile** (niente overflow per `x` molto negativo) |
| `lstm_cell(x_t, h_prev, c_prev, params)` | un passo di LSTM; restituisce anche il dict delle gate |
| `lstm_forward(X, params, h0=None, c0=None)` | srotolamento su tutta la sequenza |
| `gru_cell(x_t, h_prev, params)` | un passo di GRU; restituisce anche il dict delle gate |
| `gru_forward(X, params, h0=None)` | srotolamento su tutta la sequenza |
| `constant_error_carousel_gradient(f_gates)` | `prod_{s=t+1}^{T} f_s`, il fattore con cui il gradiente attraversa la cella |
| `esn_reservoir(D, Nres, spectral_radius, input_scaling, sparsity, seed)` | reservoir sparso, riscalato al raggio spettrale richiesto |
| `esn_states(X, Win, Wres, leak_rate, washout)` | stati del reservoir (leaky integrator), washout scartato |
| `esn_fit_readout(states, targets, ridge)` | ridge regression in forma chiusa: l'**unica** cosa che si addestra |
| `esn_predict(states, Wout)` | output del readout lineare |
| `echo_state_property_holds(Wres, leak_rate)` | condizione (necessaria) sul raggio spettrale |

`make_memory_task` e `numerical_gradient` sono già fornite. Non toccarle: i
test le usano.

## Specifica matematica

### LSTM

Con `z_t = [x_t ; h_{t-1}]` di dimensione `D + Hdim`, e ogni `W` di shape
`(Hdim, D + Hdim)` che concatena la parte input e la parte stato:

    i_t = sigma(Wi z_t + bi)          input gate    "quanto scrivo"
    f_t = sigma(Wf z_t + bf)          forget gate   "quanto conservo"
    o_t = sigma(Wo z_t + bo)          output gate   "quanto espongo"
    g_t = tanh (Wg z_t + bg)          candidato     "cosa scriverei"

    c_t = f_t * c_{t-1} + i_t * g_t
    h_t = o_t * tanh(c_t)

Tutti i prodotti sono elemento per elemento. Le tre gate sono sigmoidi perché
sono *frazioni di passaggio* e stanno in `[0,1]`; il candidato è una `tanh`
perché è *contenuto* e sta in `[-1,1]`. Sono quattro trasformazioni affini
distinte: `4 * (Hdim*(D+Hdim) + Hdim)` parametri.

### Constant error carousel

Dalla ricorrenza sulla cella segue `d c_t / d c_{t-1} = f_t`, e quindi lungo il
cammino diretto della cella

    d c_T / d c_t = prod_{s=t+1}^{T} f_s

Questa è la differenza con la RNN vanilla: qui il fattore per passo è una
quantità **appresa e dipendente dal contenuto**, non una costante strutturale.
Con `f_s = 1` il prodotto vale 1 per qualsiasi orizzonte — il gradiente scorre
senza attenuarsi, ed è per questo che si chiama *carousel* a errore costante.
Con `f_s = 0.5` si torna a un decadimento `0.5^k`: il gating non elimina il
vanishing, lo rende **controllabile**.

`constant_error_carousel_gradient(f_gates)` prende l'array dei forget gate nel
tempo (`f_gates[k]` è `f_{k+1}`, indici 0-based) e restituisce un array della
stessa shape con

    out[t] = prod_{j=t}^{T-1} f_gates[j]

cioè il prodotto cumulativo **dal fondo verso l'inizio**.

### GRU

    z_t = sigma(Wz [x_t ; h_{t-1}] + bz)          update gate
    r_t = sigma(Wr [x_t ; h_{t-1}] + br)          reset gate
    n_t = tanh (Wn [x_t ; r_t * h_{t-1}] + bn)    candidato
    h_t = (1 - z_t) * n_t + z_t * h_{t-1}

Tre blocchi invece di quattro, e un solo stato invece di due (`c` e `h`
collassano). L'input gate e il forget gate dell'LSTM sono legati da un unico
`z`: quello che si scrive è esattamente quello che non si conserva.

**Attenzione: in letteratura `z` compare con entrambi i segni.**

    (A) h_t = (1 - z_t) * n_t + z_t * h_{t-1}     z = 1 CONSERVA lo stato
    (B) h_t = (1 - z_t) * h_{t-1} + z_t * n_t     z = 1 SOSTITUISCE lo stato

Sono la stessa architettura a meno di `z -> 1 - z` (cioè del segno di `bz` e di
`Wz`) e rappresentano la stessa famiglia di funzioni, ma l'interpretazione del
gate è opposta. **Qui si usa la (A)**, che è la convenzione di Cho et al. 2014
e di `torch.nn.GRU`. Il reset gate `r` moltiplica lo stato precedente *dentro*
il candidato: non tocca l'input e non tocca l'interpolazione finale.

### Echo State Network

Un ESN è una RNN in cui `Win` e `Wres` sono estratti a caso e **mai
addestrati**. L'unica cosa che si impara è un readout lineare. Il reservoir
serve come espansione non lineare, ad alta dimensione e con memoria, della
storia degli input.

Costruzione del reservoir, nell'ordine (un solo `rng = default_rng(seed)`):

1. `Win ~ U(-input_scaling, +input_scaling)`, shape `(Nres, D)`, densa;
2. `Wres ~ U(-1, +1)`, shape `(Nres, Nres)`;
3. si azzerano **esattamente** `round(sparsity * Nres^2)` entrate, scelte con
   `rng.permutation` (non con una maschera di Bernoulli: la frazione dev'essere
   esatta, non attesa);
4. si riscala: `Wres <- Wres * spectral_radius / rho(Wres)`, con
   `rho = max |eig(Wres)|`.

Dinamica di stato (leaky integrator, `a = leak_rate`, `h_0 = 0`):

    h_t = (1 - a) h_{t-1} + a * tanh(Win x_t + Wres h_{t-1})

Readout, ridge regression in forma chiusa:

    Wout = (S^T S + ridge * I)^{-1} S^T Y            I di dimensione Nres

### Echo state property

È la condizione che rende sensato tutto il resto: lo stato del reservoir deve
essere una **funzione (un'eco) della sola storia degli input**, non dello stato
iniziale. Formalmente: per ogni coppia di stati iniziali e per ogni sequenza di
input, `||h_t - h'_t|| -> 0`.

Detta `W_eff = (1 - a) I + a Wres` la matrice della dinamica linearizzata
nell'origine (perché `tanh'(0) = 1`), le due condizioni classiche di Jaeger
(2001) sono:

* **necessaria**: `rho(W_eff) < 1`, con `rho` il massimo modulo degli
  autovalori. Se `rho > 1` lo stato nullo è un punto fisso instabile per input
  nullo, quindi esistono traiettorie che non convergono e la ESP non vale (per
  insiemi di input che contengono lo zero). `rho = 1` è indecidibile con questo
  solo criterio.
* **sufficiente**: `||W_eff||_2 = sigma_max(W_eff) < 1`. Poiché `tanh` è
  1-Lipschitz, questo rende la mappa di stato una contrazione uniforme su tutto
  lo spazio e per qualsiasi input, e la ESP segue dal teorema delle
  contrazioni.

Vale sempre `rho(W) <= ||W||_2`, quindi la sufficiente implica la necessaria ma
non viceversa: fra le due c'è una zona (`rho < 1 <= sigma_max`) in cui nessuna
decide. In pratica gli ESN si usano proprio lì, con `rho` appena sotto 1: la
condizione sufficiente sarebbe troppo conservativa e darebbe reservoir con
memoria cortissima. `echo_state_property_holds` implementa la **necessaria**.

## Perché questo esercizio

Scopre tre confusioni.

1. **Che l'LSTM "risolva" il vanishing gradient.** Non lo risolve: gli dà una
   manopola. Il gradiente lungo la cella è `prod f_s`, che vale 1 solo se i
   forget gate sono a 1 — e sono a 1 solo se la rete ha imparato a metterceli.
   Il test `(b)` mette una accanto all'altra la stessa funzione applicata ai
   forget gate saturi (prodotto = 1 su 1000 passi), a forget gate a 0.5
   (`0.5^k`) e ai fattori `w tanh'` di una RNN vanilla (`~1e-46`): sono tre
   comportamenti della *stessa* formula.

2. **Il verso dell'update gate della GRU.** Metà della letteratura scrive
   `(1-z) n + z h_prev` e metà `(1-z) h_prev + z n`. Chi non se ne accorge
   risponde all'orale che «z=1 aggiorna lo stato» quando sta usando la
   convenzione in cui z=1 lo congela. Il test `(d)` verifica entrambi i limiti.

3. **Che cosa sia davvero la echo state property.** Non è «il raggio spettrale
   deve essere minore di 1» recitato a memoria: è una proprietà di
   *dimenticanza dello stato iniziale*, e il raggio spettrale è solo un criterio
   (necessario) per verificarla. Il test `(g)` la misura per quello che è:
   stessi input, due prefissi diversi, e si guarda se le traiettorie collassano.
   Con `rho = 0.9` collassano alla precisione macchina, con `rho = 1.5` no.

C'è poi un punto trasversale: in un ESN il reservoir non si addestra. Chi non
l'ha interiorizzato cerca il gradiente rispetto a `Wres` e non trova il senso
di `esn_fit_readout`.

## Vincoli

Solo `numpy` e la standard library. Niente `torch`, `scipy`, `sklearn`,
`matplotlib`. Ogni sorgente di casualità passa da `np.random.default_rng(seed)`
con seed espliciti: mai `np.random.seed`, mai il modulo `random`, mai `time`.

`sigmoid` deve essere stabile: `1/(1+np.exp(-x))` con `x = -800` va in overflow.
I test saturano deliberatamente le gate con bias di modulo 60.

Non toccare `make_memory_task` e `numerical_gradient`.

## Come autovalutarti

```bash
cd /home/claude/gdl/esercizi/09_lstm_gru_esn
python3 -m pytest test_lstm_gru_esn.py -v
```

Tutti i test devono passare. Ogni asserzione ha un messaggio che indica quale
errore concettuale l'ha fatta fallire; leggilo prima di correggere a caso.

## Tempo stimato

100 minuti. Le celle LSTM e GRU sono dieci righe l'una e si scrivono in venti
minuti; il tempo vero se ne va su `constant_error_carousel_gradient` (capire in
che verso va il prodotto cumulativo) e sulla parte ESN, dove il riscalamento al
raggio spettrale e l'allineamento fra stati, washout e target sono i punti in
cui si sbaglia.

## Domande d'orale collegate

1. Che cos'è il constant error carousel e in che senso l'LSTM «risolve» il
   vanishing gradient? Quanto vale esattamente il gradiente lungo la cella?
2. Quali differenze ci sono fra LSTM e GRU, in numero di parametri e in
   struttura dello stato? Che cosa perde la GRU rispetto all'LSTM?
3. Che cos'è la echo state property? Enuncia la condizione necessaria e quella
   sufficiente, e spiega perché in pratica si sceglie un raggio spettrale
   appena inferiore a 1.
4. In un Echo State Network che cosa si addestra e che cosa no, e perché questo
   rende l'addestramento un problema convesso in forma chiusa?
5. A che cosa serve il washout, e a che cosa serve il leak rate?
