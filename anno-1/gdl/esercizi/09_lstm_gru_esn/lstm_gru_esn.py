"""Esercizio GDL18 - "Gated Recurrent Models".

Implementa le funzioni marcate `# TODO`. Tutto il resto (generatore del memory
task, gradiente numerico) e' gia' fornito e non va toccato: i test lo usano.

Solo numpy + stdlib. Ogni sorgente di casualita' passa da
`np.random.default_rng(seed)`: niente `np.random.seed`, niente `random`,
niente `time`.
"""

from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Utilita' fornite - NON modificare, NON sono esercizio.
# ---------------------------------------------------------------------------


def make_memory_task(T, delay, seed):
    """Task di memoria a ritardo fissato: la rete deve ricordare l'input di `delay` passi fa.

    Parametri
    ---------
    T : int          lunghezza della sequenza
    delay : int      ritardo (>= 0)
    seed : int       seme per `np.random.default_rng`

    Ritorna
    -------
    (X, Y) : tuple di ndarray
        X : shape (T, 1), i.i.d. Uniform(-1, 1)  -> media nulla, varianza 1/3
        Y : shape (T, 1), Y[t] = X[t - delay] per t >= delay, 0 per t < delay

    E' il benchmark canonico per la memoria di un modello ricorrente: una RNN
    vanilla lo risolve solo per `delay` piccolo, un ESN con reservoir grande
    lo risolve fino a un ritardo dell'ordine della dimensione del reservoir.
    """
    rng = np.random.default_rng(seed)
    X = rng.uniform(-1.0, 1.0, size=(int(T), 1))
    Y = np.zeros_like(X)
    d = int(delay)
    if d > 0:
        Y[d:, 0] = X[:-d, 0]
    else:
        Y[:, 0] = X[:, 0]
    return X, Y


def numerical_gradient(f, theta, eps=1e-5):
    """Gradiente di `f` in `theta` per differenze finite centrate.

    Parametri
    ---------
    f : callable      f(theta) -> float (scalare)
    theta : array_like, shape qualsiasi
    eps : float       passo delle differenze finite

    Ritorna
    -------
    ndarray della stessa shape di `theta`, con
        grad[k] = (f(theta + eps e_k) - f(theta - eps e_k)) / (2 eps)

    L'array viene copiato: `theta` del chiamante non viene modificato.
    """
    theta = np.array(theta, dtype=float)
    grad = np.zeros_like(theta)
    it = np.nditer(theta, flags=["multi_index"])
    while not it.finished:
        idx = it.multi_index
        old = theta[idx]
        theta[idx] = old + eps
        fp = float(f(theta))
        theta[idx] = old - eps
        fm = float(f(theta))
        theta[idx] = old
        grad[idx] = (fp - fm) / (2.0 * eps)
        it.iternext()
    return grad


# ---------------------------------------------------------------------------
# 1. Sigmoide stabile
# ---------------------------------------------------------------------------


def sigmoid(x):
    """Sigmoide logistica, numericamente stabile.

    L'implementazione ingenua `1 / (1 + np.exp(-x))` va in overflow per x molto
    negativo (exp(710) = inf) e stampa warning. Serve una forma che non valuti
    mai l'esponenziale di un argomento positivo grande.

    Parametri
    ---------
    x : array_like, shape qualsiasi

    Ritorna
    -------
    ndarray della stessa shape di `x`, valori in (0, 1).
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 2. LSTM
# ---------------------------------------------------------------------------


def lstm_cell(x_t, h_prev, c_prev, params):
    """Un passo di cella LSTM.

    Convenzione (quella del corso, e di PyTorch):

        z_t = [x_t ; h_{t-1}]                shape (D + Hdim,)
        i_t = sigma(Wi z_t + bi)             input gate
        f_t = sigma(Wf z_t + bf)             forget gate
        o_t = sigma(Wo z_t + bo)             output gate
        g_t = tanh (Wg z_t + bg)             candidato ("cell input")
        c_t = f_t * c_{t-1} + i_t * g_t      stato della cella (CEC)
        h_t = o_t * tanh(c_t)                stato nascosto / output

    Tutti i prodotti sono elemento per elemento.

    Parametri
    ---------
    x_t : array_like, shape (D,)
    h_prev : array_like, shape (Hdim,)
    c_prev : array_like, shape (Hdim,)
    params : dict con
        "Wi", "Wf", "Wo", "Wg" : ndarray shape (Hdim, D + Hdim)
            Ogni matrice CONCATENA la parte input e la parte stato: le prime D
            colonne moltiplicano x_t, le ultime Hdim moltiplicano h_{t-1}.
        "bi", "bf", "bo", "bg" : ndarray shape (Hdim,)

    Ritorna
    -------
    (h, c, gates)
        h : ndarray shape (Hdim,)
        c : ndarray shape (Hdim,)
        gates : dict con chiavi "i", "f", "o", "g", ognuna ndarray shape (Hdim,)
                (serve per ispezione: e' cio' che i test guardano)
    """
    # TODO
    raise NotImplementedError


def lstm_forward(X, params, h0=None, c0=None):
    """Srotola `lstm_cell` su tutta la sequenza.

    Parametri
    ---------
    X : array_like, shape (T, D)
    params : dict come in `lstm_cell`
    h0, c0 : array_like shape (Hdim,) oppure None (= vettori nulli)

    Ritorna
    -------
    (H, C, gates_seq)
        H : ndarray shape (T, Hdim), H[t] = h_t
        C : ndarray shape (T, Hdim), C[t] = c_t
        gates_seq : dict con chiavi "i", "f", "o", "g",
                    ognuna ndarray shape (T, Hdim)
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 3. GRU
# ---------------------------------------------------------------------------


def gru_cell(x_t, h_prev, params):
    """Un passo di cella GRU.

    Convenzione usata QUI (la stessa di Cho et al. 2014 e di `torch.nn.GRU`):

        z_t = sigma(Wz [x_t ; h_{t-1}] + bz)      update gate
        r_t = sigma(Wr [x_t ; h_{t-1}] + br)      reset gate
        n_t = tanh (Wn [x_t ; r_t * h_{t-1}] + bn)  candidato
        h_t = (1 - z_t) * n_t + z_t * h_{t-1}

    ATTENZIONE ALLE DUE CONVENZIONI. In letteratura il gate `z` compare con
    entrambi i segni:

      (A) h_t = (1 - z_t) * n_t + z_t * h_{t-1}   -> z = 1 CONSERVA lo stato
      (B) h_t = (1 - z_t) * h_{t-1} + z_t * n_t   -> z = 1 SOSTITUISCE lo stato

    Sono la stessa architettura a meno di z -> 1 - z (cioe' del segno di bz e
    dei pesi Wz): non cambiano l'insieme delle funzioni rappresentabili, ma
    cambiano l'interpretazione del gate e quindi il risultato di ogni test.
    In questo esercizio si usa la (A): `z` e' il "keep gate", e con z = 1 la
    GRU si comporta come un LSTM con forget gate saturato a 1 e input gate a 0.

    Nota sul reset gate: `r` moltiplica lo STATO PRECEDENTE dentro il
    candidato, non l'input e non il risultato finale.

    Parametri
    ---------
    x_t : array_like, shape (D,)
    h_prev : array_like, shape (Hdim,)
    params : dict con
        "Wz", "Wr", "Wn" : ndarray shape (Hdim, D + Hdim)
        "bz", "br", "bn" : ndarray shape (Hdim,)

    Ritorna
    -------
    (h, gates)
        h : ndarray shape (Hdim,)
        gates : dict con chiavi "z", "r", "n", ognuna ndarray shape (Hdim,)
    """
    # TODO
    raise NotImplementedError


def gru_forward(X, params, h0=None):
    """Srotola `gru_cell` su tutta la sequenza.

    Parametri
    ---------
    X : array_like, shape (T, D)
    params : dict come in `gru_cell`
    h0 : array_like shape (Hdim,) oppure None (= vettore nullo)

    Ritorna
    -------
    (H, gates_seq)
        H : ndarray shape (T, Hdim)
        gates_seq : dict con chiavi "z", "r", "n", ognuna ndarray shape (T, Hdim)
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 4. Constant Error Carousel
# ---------------------------------------------------------------------------


def constant_error_carousel_gradient(f_gates):
    """Fattore con cui il gradiente attraversa la cella LSTM lungo il tempo.

    Dalla ricorrenza `c_t = f_t * c_{t-1} + i_t * g_t` segue immediatamente
    `d c_t / d c_{t-1} = f_t` (il termine `i_t g_t` non dipende da c_{t-1}),
    quindi il cammino diretto lungo la cella vale

        d c_T / d c_t = prod_{s = t+1}^{T} f_s

    Questo e' il "constant error carousel": se i forget gate valgono 1 il
    prodotto vale 1 per QUALSIASI orizzonte e il gradiente non svanisce.

    Parametri
    ---------
    f_gates : array_like, shape (T,) oppure (T, Hdim)
        Valori del forget gate nel tempo: `f_gates[k]` e' f_{k+1}, cioe' il
        forget gate applicato al passo k+1 (indici 0-based: la riga 0 e' il
        primo passo della sequenza).

    Ritorna
    -------
    ndarray della STESSA shape di `f_gates`, con

        out[t] = prod_{s = t+1}^{T} f_s = prod_{j = t}^{T-1} f_gates[j]

    cioe' il prodotto cumulativo AL CONTRARIO lungo l'asse 0. In particolare
    `out[0]` e' il prodotto di tutti i forget gate (il fattore che collega
    c_T a c_0) e `out[T-1]` e' l'ultimo forget gate.
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 5. Echo State Network
# ---------------------------------------------------------------------------


def esn_reservoir(D, Nres, spectral_radius=0.9, input_scaling=1.0, sparsity=0.0,
                  seed=0):
    """Costruisce (Win, Wres) di un Echo State Network. NON si addestrano.

    Procedura RICHIESTA (ordine fisso, cosi' il risultato e' riproducibile
    bit a bit e i test possono controllarlo):

      1. `Win ~ Uniform(-input_scaling, +input_scaling)`, shape (Nres, D), DENSA.
      2. `Wres ~ Uniform(-1, +1)`, shape (Nres, Nres).
      3. si azzerano ESATTAMENTE `round(sparsity * Nres * Nres)` entrate,
         scelte senza reinserimento con `rng.permutation` (non con una maschera
         di Bernoulli: cosi' la frazione di zeri e' esatta, non attesa).
      4. si calcola il raggio spettrale `rho = max |eig(Wres)|` e si riscala
         `Wres <- Wres * spectral_radius / rho`.

    Un solo `rng = np.random.default_rng(seed)` per tutti e tre i sorteggi,
    consumati in quest'ordine.

    Parametri
    ---------
    D : int                dimensione dell'input
    Nres : int             dimensione del reservoir
    spectral_radius : float  raggio spettrale RICHIESTO (> 0)
    input_scaling : float  semiampiezza dell'uniforme di Win
    sparsity : float in [0, 1]  frazione di entrate NULLE di Wres (0 = densa)
    seed : int             seme per `np.random.default_rng`

    Ritorna
    -------
    (Win, Wres) : ndarray shape (Nres, D) e (Nres, Nres)
        `Wres` ha raggio spettrale pari a `spectral_radius` a meno
        dell'errore numerico di `np.linalg.eigvals`.

    Solleva
    -------
    ValueError se la matrice sparsa estratta e' nilpotente (rho = 0) e quindi
    non riscalabile.
    """
    # TODO
    raise NotImplementedError


def esn_states(X, Win, Wres, leak_rate=1.0, washout=0):
    """Stati del reservoir (leaky integrator), a partire dallo stato nullo.

        h_0 = 0
        h_t = (1 - a) h_{t-1} + a * tanh(Win x_t + Wres h_{t-1}),  t = 1..T

    con `a = leak_rate`. Con `a = 1` si ricade nell'ESN classico
    `h_t = tanh(Win x_t + Wres h_{t-1})`.

    Parametri
    ---------
    X : array_like, shape (T, D)
    Win : ndarray, shape (Nres, D)
    Wres : ndarray, shape (Nres, Nres)
    leak_rate : float in (0, 1]
    washout : int   numero di stati iniziali da SCARTARE (transitorio)

    Ritorna
    -------
    ndarray shape (T - washout, Nres), le righe sono h_{washout+1} .. h_T.
    Con `washout = 0` la shape e' (T, Nres).
    """
    # TODO
    raise NotImplementedError


def esn_fit_readout(states, targets, ridge=1e-6):
    """Readout lineare per ridge regression in forma chiusa.

    E' l'UNICA cosa che si addestra in un ESN: Win e Wres restano fissi.
    Si minimizza  ||S W - Y||_F^2 + ridge * ||W||_F^2, la cui soluzione e'

        Wout = (S^T S + ridge * I)^{-1} S^T Y

    con I di dimensione Nres.

    Parametri
    ---------
    states : array_like, shape (N, Nres)
    targets : array_like, shape (N,) oppure (N, K)
    ridge : float >= 0   coefficiente di regolarizzazione (Tikhonov)

    Ritorna
    -------
    Wout : ndarray shape (Nres,) se `targets` e' 1-D, (Nres, K) se e' 2-D.

    Nota: non c'e' un termine di bias. Se serve, si aggiunge a mano una colonna
    di 1 a `states`. Il memory task di questo esercizio ha media nulla, quindi
    il bias non serve.
    """
    # TODO
    raise NotImplementedError


def esn_predict(states, Wout):
    """Output del readout lineare.

    Parametri
    ---------
    states : array_like, shape (N, Nres)
    Wout : array_like, shape (Nres,) oppure (Nres, K)

    Ritorna
    -------
    ndarray shape (N,) se `Wout` e' 1-D, (N, K) se e' 2-D.
    """
    # TODO
    raise NotImplementedError


def echo_state_property_holds(Wres, leak_rate=1.0):
    """Test (necessario) di Echo State Property basato sul raggio spettrale.

    La ECHO STATE PROPERTY dice che lo stato del reservoir dimentica lo stato
    iniziale: per ogni coppia di stati iniziali h, h' e per ogni sequenza di
    input, ||h_t - h'_t|| -> 0. Equivalentemente lo stato e' funzione (echo)
    della sola storia degli input.

    Con l'aggiornamento leaky la matrice che governa la dinamica linearizzata
    nell'origine e'

        W_eff = (1 - a) I + a * Wres        (a = leak_rate)

    perche' tanh'(0) = 1. Due condizioni classiche (Jaeger, 2001):

      * CONDIZIONE NECESSARIA (quella da implementare qui):
            rho(W_eff) < 1,   rho = max |autovalore|
        Se rho(W_eff) > 1 lo stato nullo e' un punto fisso instabile per input
        nullo, quindi esistono traiettorie che non convergono e la ESP NON vale
        (per insiemi di input che contengono lo zero). Il caso rho = 1 e' un
        caso limite indecidibile con questo solo criterio.

      * CONDIZIONE SUFFICIENTE (piu' forte, NON e' quella da implementare):
            ||W_eff||_2 = sigma_max(W_eff) < 1
        Poiche' tanh e' 1-Lipschitz, questo rende la mappa di stato una
        contrazione uniforme in TUTTO lo spazio, per QUALSIASI input; per il
        teorema delle contrazioni la ESP vale. Vale sempre
        rho(W) <= ||W||_2, quindi la condizione sufficiente implica la
        necessaria, ma non viceversa: c'e' una zona (rho < 1 <= sigma_max) in
        cui nessuna delle due decide.

    In pratica gli ESN si usano proprio in quella zona, con rho appena sotto 1
    ("edge of stability"): la condizione sufficiente sulla norma sarebbe troppo
    conservativa e darebbe reservoir con memoria cortissima.

    Parametri
    ---------
    Wres : array_like, shape (Nres, Nres)
    leak_rate : float in (0, 1]

    Ritorna
    -------
    bool : True se rho((1 - a) I + a Wres) < 1.
           Deve essere un `bool` Python, non un `np.bool_`: i test usano `is True`.
    """
    # TODO
    raise NotImplementedError
