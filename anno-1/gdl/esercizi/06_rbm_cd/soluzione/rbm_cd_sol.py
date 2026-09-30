"""Soluzione di riferimento - GDL14 "Undirected Graphical Models".

Restricted Boltzmann Machine binaria e contrastive divergence.
Stessa API di ``rbm_cd.py``. Commentata: le note di ragionamento stanno in
``NOTE.md``.

Convenzioni globali
-------------------
- ``v`` visibili in {0,1}^D, ``h`` nascoste in {0,1}^H (array float, non bool).
- ``W`` shape (D, H), ``b`` shape (D,) bias visibili, ``c`` shape (H,) bias nascosti.
- Energia:  E(v, h) = -v@b - h@c - v@W@h
- Congiunta: p(v, h) = exp(-E(v, h)) / Z
- Un batch e' sempre (N, D) / (N, H); N e' l'asse 0.
"""

from __future__ import annotations

import itertools

import numpy as np

# ---------------------------------------------------------------------------
# Utilita' fornite gia' nello skeleton - NON sono esercizio.
# ---------------------------------------------------------------------------


def make_bars_and_stripes(seed=0, n=3):
    """Dataset Bars-and-Stripes n x n, appiattito in vettori di D = n*n bit.

    Un pattern e' o "tutte righe piene/vuote" (bars) o "tutte colonne
    piene/vuote" (stripes). Ci sono 2^n pattern per tipo; ``tutto 0`` e
    ``tutto 1`` compaiono in entrambi, quindi i pattern DISTINTI sono
    2^(n+1) - 2 (14 per n = 3).

    E' il benchmark classico delle RBM proprio perche' D = 9 e' abbastanza
    piccolo da permettere l'enumerazione esatta di Z, e quindi il calcolo
    della log-likelihood vera: si puo' verificare se il training funziona
    davvero invece di fidarsi dell'errore di ricostruzione.

    Parametri
    ---------
    seed : int
        Controlla SOLO l'ordine delle righe (il contenuto e' deterministico).
    n : int
        Lato della griglia. n = 3 -> D = 9, 14 pattern.

    Ritorna
    -------
    X : ndarray shape (2^(n+1) - 2, n*n), valori in {0.0, 1.0}
    """
    pats = []
    for bits in itertools.product([0, 1], repeat=n):
        col = np.asarray(bits, dtype=float)
        pats.append(np.repeat(col[:, None], n, axis=1))  # bars: righe piene
        pats.append(np.repeat(col[None, :], n, axis=0))  # stripes: colonne piene
    X = np.asarray([p.reshape(-1) for p in pats], dtype=float)
    X = np.unique(X, axis=0)  # rimuove i due duplicati
    rng = np.random.default_rng(seed)
    return X[rng.permutation(X.shape[0])]


def _all_binary(n):
    """Tutte le 2^n configurazioni binarie di lunghezza ``n``, shape (2^n, n)."""
    idx = np.arange(2**n, dtype=np.int64)[:, None]
    return ((idx >> np.arange(n - 1, -1, -1, dtype=np.int64)) & 1).astype(float)


def _logsumexp(a, axis=None):
    """log(sum(exp(a))) numericamente stabile (niente scipy in questo container)."""
    a = np.asarray(a, dtype=float)
    amax = np.max(a, axis=axis, keepdims=True)
    out = np.log(np.sum(np.exp(a - amax), axis=axis, keepdims=True)) + amax
    return np.squeeze(out, axis=axis) if axis is not None else float(np.squeeze(out))


def log_partition_exact(W, b, c):
    """log Z per ENUMERAZIONE ESATTA di tutti i 2^D * 2^H stati (v, h).

    Serve solo come oracolo su modelli giocattolo: il costo e' 2^(D+H).
    Non usa nessuna delle funzioni da implementare, cosi' resta un
    riferimento indipendente anche quando lo skeleton solleva
    NotImplementedError.

    Parametri
    ---------
    W : (D, H); b : (D,); c : (H,)

    Ritorna
    -------
    float : log Z = log sum_{v,h} exp(-E(v, h))
    """
    D, H = W.shape
    Vs = _all_binary(D)  # (2^D, D)
    Hs = _all_binary(H)  # (2^H, H)
    neg_E = (Vs @ b)[:, None] + (Hs @ c)[None, :] + (Vs @ W) @ Hs.T
    return _logsumexp(neg_E)


def exact_log_likelihood(V, W, b, c):
    """Log-likelihood ESATTA MEDIA per esempio: mean_n [ log p(v_n) ].

    log p(v) = logsumexp_h(-E(v, h)) - log Z, con log Z per enumerazione.
    Anche questa e' oracolo: costo 2^(D+H), niente dipendenze dalle funzioni
    da implementare.

    Parametri
    ---------
    V : (N, D) in {0,1}; W : (D, H); b : (D,); c : (H,)

    Ritorna
    -------
    float : media su n di log p(v_n)  (valore negativo; piu' vicino a 0 = meglio)
    """
    V = np.asarray(V, dtype=float)
    H = W.shape[1]
    Hs = _all_binary(H)
    neg_E = (V @ W) @ Hs.T + (Hs @ c)[None, :]  # (N, 2^H), senza il termine v@b
    neg_free = (V @ b) + _logsumexp(neg_E, axis=1)  # = -F(v)
    return float(np.mean(neg_free - log_partition_exact(W, b, c)))


# ---------------------------------------------------------------------------
# 1. Sigmoide stabile
# ---------------------------------------------------------------------------


def sigmoid(x):
    """Sigmoide logistica 1 / (1 + exp(-x)), stabile per |x| grande.

    Il punto: ``1/(1+exp(-x))`` esplode per x molto negativo e
    ``exp(x)/(1+exp(x))`` esplode per x molto positivo. Si usa la forma giusta
    su ciascuna meta' del dominio, e la si sceglie con MASCHERE BOOLEANE, non
    con ``np.where``: ``np.where`` valuta entrambi i rami prima di scegliere,
    quindi l'overflow avviene comunque.

    Parametri
    ---------
    x : array_like, shape qualsiasi

    Ritorna
    -------
    ndarray float della stessa shape di ``x``, valori in (0, 1).
    """
    x = np.asarray(x, dtype=float)
    flat = x.ravel()
    out = np.empty_like(flat)
    pos = flat >= 0.0
    # ramo x >= 0: exp(-x) in (0, 1], nessun overflow
    out[pos] = 1.0 / (1.0 + np.exp(-flat[pos]))
    # ramo x < 0: exp(x) in (0, 1), al piu' underflow a 0 (innocuo)
    ex = np.exp(flat[~pos])
    out[~pos] = ex / (1.0 + ex)
    return out.reshape(x.shape)


# ---------------------------------------------------------------------------
# 2. Energia
# ---------------------------------------------------------------------------


def energy(v, h, W, b, c):
    """Energia congiunta E(v, h) = -v@b - h@c - v@W@h.

    Vettorizzata con broadcasting sugli assi che precedono l'ultimo:
    - v (N, D) e h (N, H)          -> (N,)
    - v (N, 1, D) e h (1, M, H)    -> (N, M)   [tutte le coppie]
    - v (D,) e h (H,)              -> scalare 0-d

    Parametri
    ---------
    v : (..., D) in {0,1}; h : (..., H) in {0,1}; W : (D, H); b : (D,); c : (H,)

    Ritorna
    -------
    ndarray con la shape ottenuta dal broadcasting dei prefissi di v e h.
    """
    v = np.asarray(v, dtype=float)
    h = np.asarray(h, dtype=float)
    # v @ W ha shape (..., H); il prodotto elemento-per-elemento con h e la
    # somma sull'ultimo asse realizzano il termine bilineare v^T W h.
    return -(v @ b) - (h @ c) - np.sum((v @ W) * h, axis=-1)


# ---------------------------------------------------------------------------
# 3. Energia libera (marginalizzazione ANALITICA sulle nascoste)
# ---------------------------------------------------------------------------


def free_energy(v, W, b, c):
    """Energia libera F(v) = -log sum_h exp(-E(v, h)).

    Derivazione (e' il cuore dell'esercizio). Fissato v, l'energia e' AFFINE
    in h: E(v, h) = -v@b - sum_j h_j * (c_j + v@W[:, j]). Quindi

        sum_h exp(-E(v,h))
          = exp(v@b) * sum_h prod_j exp(h_j * (c_j + v@W[:,j]))
          = exp(v@b) * prod_j sum_{h_j in {0,1}} exp(h_j * (c_j + v@W[:,j]))
          = exp(v@b) * prod_j (1 + exp(c_j + v@W[:,j]))

    La somma su 2^H termini si fattorizza in H somme da 2 termini: e' possibile
    SOLO perche' non ci sono archi h-h, cioe' perche' la RBM e' bipartita.
    Prendendo -log:

        F(v) = -v@b - sum_j softplus(c_j + v@W[:, j]),   softplus(z)=log(1+e^z)

    Nota: F NON contiene log Z. p(v) = exp(-F(v)) / Z, e Z resta intrattabile.

    Parametri
    ---------
    v : (N, D) in {0,1}; W : (D, H); b : (D,); c : (H,)

    Ritorna
    -------
    ndarray shape (N,)
    """
    v = np.asarray(v, dtype=float)
    pre_h = c + v @ W  # (N, H): attivazione totale di ciascuna nascosta
    # np.logaddexp(0, z) = log(1 + e^z) = softplus(z), gia' stabile.
    return -(v @ b) - np.sum(np.logaddexp(0.0, pre_h), axis=-1)


# ---------------------------------------------------------------------------
# 4. Condizionali complete (fattorizzate: e' la "R" di RBM)
# ---------------------------------------------------------------------------


def p_h_given_v(v, W, c):
    """p(h_j = 1 | v) per ogni j, in PROBABILITA' (non campioni).

    Dalla congiunta: p(h_j=1|v) / p(h_j=0|v) = exp(c_j + v@W[:,j]), da cui la
    sigmoide. Le H unita' sono condizionalmente indipendenti dato v perche' il
    grafo e' bipartito: v e' un separatore per tutte le h.

    Parametri
    ---------
    v : (N, D); W : (D, H); c : (H,)

    Ritorna
    -------
    ndarray (N, H) con valori in (0, 1).
    """
    v = np.asarray(v, dtype=float)
    return sigmoid(c + v @ W)


def p_v_given_h(h, W, b):
    """p(v_i = 1 | h) per ogni i. Simmetrico a ``p_h_given_v`` con W trasposta.

    Parametri
    ---------
    h : (N, H); W : (D, H); b : (D,)

    Ritorna
    -------
    ndarray (N, D) con valori in (0, 1).
    """
    h = np.asarray(h, dtype=float)
    return sigmoid(b + h @ W.T)


# ---------------------------------------------------------------------------
# 5. Campionamento
# ---------------------------------------------------------------------------


def sample_bernoulli(p, rng):
    """Campioni binari indipendenti con P(1) = p, elemento per elemento.

    ``rng.random()`` sta in [0, 1): il confronto ``u < p`` da' quindi
    esattamente 0 quando p = 0 e esattamente 1 quando p = 1.

    Parametri
    ---------
    p : array_like di probabilita' in [0, 1]
    rng : numpy.random.Generator

    Ritorna
    -------
    ndarray float della stessa shape di ``p``, valori in {0.0, 1.0}.
    """
    p = np.asarray(p, dtype=float)
    return (rng.random(p.shape) < p).astype(float)


def gibbs_step(v, W, b, c, rng):
    """Un passo completo di Gibbs A BLOCCHI: v -> h -> v.

    Ordine dei consumi di ``rng`` (fissato, i test ci contano):
    prima si campiona il blocco h, poi il blocco v.

    Tutte le h si campionano in parallelo perche' sono condizionalmente
    indipendenti dato v (e viceversa): in una Boltzmann machine NON ristretta
    servirebbe un aggiornamento per unita' alla volta.

    Parametri
    ---------
    v : (N, D) in {0,1}; W : (D, H); b : (D,); c : (H,); rng : Generator

    Ritorna
    -------
    (v_new, h_sample, h_prob)
        v_new    : (N, D) in {0,1}, campionato da p(v | h_sample)
        h_sample : (N, H) in {0,1}, campionato da p(h | v)
        h_prob   : (N, H) in (0,1), le probabilita' p(h=1 | v) usate sopra
    """
    h_prob = p_h_given_v(v, W, c)
    h_sample = sample_bernoulli(h_prob, rng)
    v_prob = p_v_given_h(h_sample, W, b)
    v_new = sample_bernoulli(v_prob, rng)
    return v_new, h_sample, h_prob


# ---------------------------------------------------------------------------
# 6. Contrastive divergence
# ---------------------------------------------------------------------------


def cd_k(v_data, W, b, c, k, rng):
    """Gradienti CD-k della log-likelihood. SEGNO: sono direzioni di ASCESA.

    Il gradiente esatto della log-likelihood media e'

        d mean_n log p(v_n) / dW = <v h^T>_data - <v h^T>_model
        d ... / db              = <v>_data     - <v>_model
        d ... / dc              = <h>_data     - <h>_model

    (fase positiva meno fase negativa: il secondo termine viene da -d logZ/d.).
    Il termine di modello richiederebbe di campionare dalla congiunta, cioe'
    una catena di Gibbs fatta girare fino a convergenza. CD-k la tronca a k
    passi e la fa PARTIRE DAI DATI. Questo introduce un BIAS che non sparisce
    aumentando il numero di campioni: CD non e' uno stimatore non distorto del
    gradiente, e per k finito non massimizza la log-likelihood.

    Rao-Blackwellizzazione: nelle statistiche si usa p(h=1|v) invece del bit
    campionato. E' un'aspettazione condizionale esatta, quindi riduce la
    varianza senza aggiungere bias.

    L'aggiornamento e' quindi  W <- W + lr * grad_W  (ascesa), NON una discesa.

    Parametri
    ---------
    v_data : (N, D) in {0,1}; W : (D, H); b : (D,); c : (H,)
    k : int >= 1, numero di passi di Gibbs della fase negativa
    rng : numpy.random.Generator

    Ritorna
    -------
    (grad_W, grad_b, grad_c, v_model)
        grad_W  : (D, H); grad_b : (D,); grad_c : (H,)  [gia' divisi per N]
        v_model : (N, D) in {0,1}, stato visibile della catena dopo k passi
    """
    v_data = np.asarray(v_data, dtype=float)
    n = v_data.shape[0]

    # ---- fase positiva: aspettazione sotto p(h | v_data), esatta ----
    ph_data = p_h_given_v(v_data, W, c)

    # ---- fase negativa: k passi di Gibbs partendo dai dati ----
    v_model = v_data
    for _ in range(k):
        v_model, _, _ = gibbs_step(v_model, W, b, c, rng)
    ph_model = p_h_given_v(v_model, W, c)

    grad_W = (v_data.T @ ph_data - v_model.T @ ph_model) / n
    grad_b = np.mean(v_data - v_model, axis=0)
    grad_c = np.mean(ph_data - ph_model, axis=0)
    return grad_W, grad_b, grad_c, v_model


# ---------------------------------------------------------------------------
# 7. Training
# ---------------------------------------------------------------------------


def train_rbm(X, H, epochs, lr, k=1, batch_size=10, seed=0):
    """Addestra una RBM binaria con CD-k e SGD a minibatch.

    Inizializzazione (fissata, i test ci contano):
        rng = np.random.default_rng(seed)
        W = 0.01 * rng.standard_normal((D, H)); b = zeros(D); c = zeros(H)
        X_noise = bernoulli(0.5) della stessa shape di X   [per la diagnostica]

    Ogni epoca: permutazione di ``X`` con ``rng.permutation(N)``, minibatch
    consecutivi di ``batch_size`` (l'ultimo puo' essere piu' corto), un
    aggiornamento di ASCESA per minibatch.

    Diagnostiche registrate a fine epoca:
    - errore di ricostruzione: MSE fra X e p(v|p(h|X)) (ricostruzione
      deterministica, senza campionare: e' una quantita' riproducibile).
      NB: e' un proxy, NON la log-likelihood. Puo' scendere anche mentre la
      log-likelihood peggiora.
    - free energy gap: mean F(X) - mean F(X_noise). Diventa sempre piu'
      negativo se il modello impara a dare energia bassa ai dati e alta al
      rumore.

    Parametri
    ---------
    X : (N, D) in {0,1}
    H : int, numero di unita' nascoste
    epochs : int; lr : float; k : int; batch_size : int; seed : int

    Ritorna
    -------
    dict con chiavi
        "W" : (D, H), "b" : (D,), "c" : (H,)
        "recon_error_history"     : ndarray (epochs,)
        "free_energy_gap_history" : ndarray (epochs,)
    """
    X = np.asarray(X, dtype=float)
    n, D = X.shape
    rng = np.random.default_rng(seed)

    W = 0.01 * rng.standard_normal((D, H))
    b = np.zeros(D)
    c = np.zeros(H)
    X_noise = (rng.random(X.shape) < 0.5).astype(float)

    recon_hist = np.empty(epochs)
    gap_hist = np.empty(epochs)

    for ep in range(epochs):
        perm = rng.permutation(n)
        for start in range(0, n, batch_size):
            batch = X[perm[start : start + batch_size]]
            gW, gb, gc, _ = cd_k(batch, W, b, c, k, rng)
            # ASCESA sulla log-likelihood: += , non -=
            W += lr * gW
            b += lr * gb
            c += lr * gc

        v_rec = p_v_given_h(p_h_given_v(X, W, c), W, b)
        recon_hist[ep] = float(np.mean((X - v_rec) ** 2))
        gap_hist[ep] = float(
            np.mean(free_energy(X, W, b, c)) - np.mean(free_energy(X_noise, W, b, c))
        )

    return {
        "W": W,
        "b": b,
        "c": c,
        "recon_error_history": recon_hist,
        "free_energy_gap_history": gap_hist,
    }
