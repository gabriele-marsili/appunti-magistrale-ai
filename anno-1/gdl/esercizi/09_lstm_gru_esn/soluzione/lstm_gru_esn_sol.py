"""Soluzione di riferimento - GDL18 "Gated Recurrent Models".

LSTM, GRU, constant error carousel, Echo State Network.

Solo numpy + stdlib. Ogni sorgente di casualita' passa da
`np.random.default_rng(seed)`: niente `np.random.seed`, niente `random`,
niente `time`.
"""

from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Utilita' fornite dallo skeleton - NON sono esercizio.
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

    Parametri
    ---------
    x : array_like, shape qualsiasi

    Ritorna
    -------
    ndarray della stessa shape di `x`, valori in (0, 1).
    """
    z = np.asarray(x, dtype=float)
    # Si valuta SEMPRE exp(-|z|), che sta in (0, 1] e non puo' mai andare in
    # overflow. Per z >= 0:  1 / (1 + exp(-z)).
    # Per z <  0:  exp(z) / (1 + exp(z)), che e' exp(-|z|)/(1+exp(-|z|)).
    e = np.exp(-np.abs(z))
    return np.where(z >= 0.0, 1.0 / (1.0 + e), e / (1.0 + e))


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
    x_t = np.asarray(x_t, dtype=float).ravel()
    h_prev = np.asarray(h_prev, dtype=float).ravel()
    c_prev = np.asarray(c_prev, dtype=float).ravel()

    z = np.concatenate([x_t, h_prev])

    i = sigmoid(params["Wi"] @ z + params["bi"])
    f = sigmoid(params["Wf"] @ z + params["bf"])
    o = sigmoid(params["Wo"] @ z + params["bo"])
    g = np.tanh(params["Wg"] @ z + params["bg"])

    c = f * c_prev + i * g
    h = o * np.tanh(c)

    return h, c, {"i": i, "f": f, "o": o, "g": g}


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
    X = np.asarray(X, dtype=float)
    T = X.shape[0]
    Hdim = np.asarray(params["Wi"]).shape[0]

    h = np.zeros(Hdim) if h0 is None else np.asarray(h0, dtype=float).ravel().copy()
    c = np.zeros(Hdim) if c0 is None else np.asarray(c0, dtype=float).ravel().copy()

    H = np.empty((T, Hdim))
    C = np.empty((T, Hdim))
    gates_seq = {k: np.empty((T, Hdim)) for k in ("i", "f", "o", "g")}

    for t in range(T):
        h, c, gates = lstm_cell(X[t], h, c, params)
        H[t] = h
        C[t] = c
        for k in gates_seq:
            gates_seq[k][t] = gates[k]

    return H, C, gates_seq


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
    x_t = np.asarray(x_t, dtype=float).ravel()
    h_prev = np.asarray(h_prev, dtype=float).ravel()

    zin = np.concatenate([x_t, h_prev])

    z = sigmoid(params["Wz"] @ zin + params["bz"])
    r = sigmoid(params["Wr"] @ zin + params["br"])
    # il reset gate agisce sullo STATO dentro il candidato, non sull'input
    n = np.tanh(params["Wn"] @ np.concatenate([x_t, r * h_prev]) + params["bn"])

    h = (1.0 - z) * n + z * h_prev

    return h, {"z": z, "r": r, "n": n}


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
    X = np.asarray(X, dtype=float)
    T = X.shape[0]
    Hdim = np.asarray(params["Wz"]).shape[0]

    h = np.zeros(Hdim) if h0 is None else np.asarray(h0, dtype=float).ravel().copy()

    H = np.empty((T, Hdim))
    gates_seq = {k: np.empty((T, Hdim)) for k in ("z", "r", "n")}

    for t in range(T):
        h, gates = gru_cell(X[t], h, params)
        H[t] = h
        for k in gates_seq:
            gates_seq[k][t] = gates[k]

    return H, gates_seq


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
    f = np.asarray(f_gates, dtype=float)
    # cumprod dal fondo verso l'inizio: flip, cumprod, flip.
    return np.flip(np.cumprod(np.flip(f, axis=0), axis=0), axis=0)


# ---------------------------------------------------------------------------
# 5. Echo State Network
# ---------------------------------------------------------------------------


def esn_reservoir(D, Nres, spectral_radius=0.9, input_scaling=1.0, sparsity=0.0,
                  seed=0):
    """Costruisce (Win, Wres) di un Echo State Network. NON si addestrano.

    Procedura (ordine fisso, cosi' il risultato e' riproducibile bit a bit):

      1. `Win ~ Uniform(-input_scaling, +input_scaling)`, shape (Nres, D), DENSA.
      2. `Wres ~ Uniform(-1, +1)`, shape (Nres, Nres).
      3. si azzerano ESATTAMENTE `round(sparsity * Nres * Nres)` entrate,
         scelte senza reinserimento con `rng.permutation` (non con una maschera
         di Bernoulli: cosi' la frazione di zeri e' esatta, non attesa).
      4. si calcola il raggio spettrale `rho = max |eig(Wres)|` e si riscala
         `Wres <- Wres * spectral_radius / rho`.

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
    D = int(D)
    Nres = int(Nres)
    rng = np.random.default_rng(seed)

    Win = rng.uniform(-input_scaling, input_scaling, size=(Nres, D))
    Wres = rng.uniform(-1.0, 1.0, size=(Nres, Nres))

    n_total = Nres * Nres
    n_zero = int(round(float(sparsity) * n_total))
    if n_zero > 0:
        idx = rng.permutation(n_total)[:n_zero]
        Wres.flat[idx] = 0.0

    rho = float(np.max(np.abs(np.linalg.eigvals(Wres))))
    if rho <= 0.0:
        raise ValueError(
            "reservoir nilpotente (raggio spettrale nullo): impossibile "
            "riscalare al raggio spettrale richiesto"
        )
    Wres = Wres * (float(spectral_radius) / rho)
    return Win, Wres


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
    X = np.asarray(X, dtype=float)
    Win = np.asarray(Win, dtype=float)
    Wres = np.asarray(Wres, dtype=float)

    T = X.shape[0]
    Nres = Wres.shape[0]
    a = float(leak_rate)

    h = np.zeros(Nres)
    S = np.empty((T, Nres))
    for t in range(T):
        h = (1.0 - a) * h + a * np.tanh(Win @ X[t] + Wres @ h)
        S[t] = h

    return S[int(washout):]


def esn_fit_readout(states, targets, ridge=1e-6):
    """Readout lineare per ridge regression in forma chiusa.

    E' l'UNICA cosa che si addestra in un ESN: Win e Wres restano fissi.
    Si minimizza  ||S W - Y||_F^2 + ridge * ||W||_F^2, la cui soluzione e'

        Wout = (S^T S + ridge * I)^{-1} S^T Y

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
    S = np.asarray(states, dtype=float)
    Y = np.asarray(targets, dtype=float)

    one_d = Y.ndim == 1
    if one_d:
        Y = Y[:, None]

    Nres = S.shape[1]
    A = S.T @ S + float(ridge) * np.eye(Nres)
    B = S.T @ Y
    Wout = np.linalg.solve(A, B)

    return Wout[:, 0] if one_d else Wout


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
    return np.asarray(states, dtype=float) @ np.asarray(Wout, dtype=float)


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

      * CONDIZIONE NECESSARIA (quella implementata qui):
            rho(W_eff) < 1,   rho = max |autovalore|
        Se rho(W_eff) > 1 lo stato nullo e' un punto fisso instabile per input
        nullo, quindi esistono traiettorie che non convergono e la ESP NON vale
        (per insiemi di input che contengono lo zero). Il caso rho = 1 e' un
        caso limite indecidibile con questo solo criterio.

      * CONDIZIONE SUFFICIENTE (piu' forte, NON e' quella qui implementata):
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
    """
    W = np.asarray(Wres, dtype=float)
    a = float(leak_rate)
    W_eff = (1.0 - a) * np.eye(W.shape[0]) + a * W
    rho = float(np.max(np.abs(np.linalg.eigvals(W_eff))))
    return bool(rho < 1.0)
