"""Esercizio GDL14 - "Undirected Graphical Models".

Restricted Boltzmann Machine binaria, energia libera, campionamento di Gibbs a
blocchi e contrastive divergence.

Implementa le funzioni marcate `# TODO`. Tutto il resto (dataset
Bars-and-Stripes, enumerazione esatta di Z, log-likelihood esatta, utilita'
combinatorie) e' gia' fornito e NON va toccato: serve come oracolo ai test.

Solo numpy + stdlib. Ogni sorgente di casualita' passa da `rng`
(`numpy.random.Generator`) che ricevi come argomento: niente `np.random.seed`,
niente `random`, niente `time`.

Convenzioni globali
-------------------
- ``v`` visibili in {0,1}^D, ``h`` nascoste in {0,1}^H (array float, non bool).
- ``W`` shape (D, H), ``b`` shape (D,) bias visibili, ``c`` shape (H,) bias nascosti.
- Energia:   E(v, h) = -v@b - h@c - v@W@h
- Congiunta: p(v, h) = exp(-E(v, h)) / Z,   Z = sum_{v,h} exp(-E(v, h))
- Un batch e' sempre (N, D) / (N, H); N e' l'asse 0.
"""

from __future__ import annotations

import itertools

import numpy as np

# ---------------------------------------------------------------------------
# Utilita' fornite - NON modificare, i test le usano come oracolo.
# ---------------------------------------------------------------------------


def make_bars_and_stripes(seed=0, n=3):
    """Dataset Bars-and-Stripes n x n, appiattito in vettori di D = n*n bit.

    Un pattern e' o "tutte righe piene/vuote" (bars) o "tutte colonne
    piene/vuote" (stripes). Ci sono 2^n pattern per tipo; ``tutto 0`` e
    ``tutto 1`` compaiono in entrambi, quindi i pattern DISTINTI sono
    2^(n+1) - 2 (14 per n = 3).

    E' il benchmark classico delle RBM proprio perche' D = 9 e' abbastanza
    piccolo da permettere l'enumerazione esatta di Z, e quindi il calcolo della
    log-likelihood vera: si puo' verificare se il training funziona davvero
    invece di fidarsi dell'errore di ricostruzione.

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

    NON e' esercizio: e' l'oracolo. Costo 2^(D+H), quindi utilizzabile solo su
    modelli giocattolo (indicativamente D + H <= 20). In un modello reale Z e'
    intrattabile, ed e' esattamente il motivo per cui esiste la contrastive
    divergence.

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

    NON e' esercizio: e' l'oracolo.
    log p(v) = logsumexp_h(-E(v, h)) - log Z, con log Z per enumerazione.

    Parametri
    ---------
    V : (N, D) in {0,1}; W : (D, H); b : (D,); c : (H,)

    Ritorna
    -------
    float : media su n di log p(v_n)  (negativo; piu' vicino a 0 = meglio)
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
    """Sigmoide logistica 1 / (1 + exp(-x)), STABILE per |x| grande.

    Requisito: con input di modulo 1000 non deve produrre overflow, inf o NaN.
    Attenzione: ``np.where(cond, ramo_a, ramo_b)`` valuta ENTRAMBI i rami prima
    di scegliere, quindi non basta a evitare l'overflow.

    Parametri
    ---------
    x : array_like, shape qualsiasi

    Ritorna
    -------
    ndarray float della stessa shape di ``x``, valori in [0, 1].
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 2. Energia
# ---------------------------------------------------------------------------


def energy(v, h, W, b, c):
    """Energia congiunta E(v, h) = -v@b - h@c - v@W@h.

    Deve essere vettorizzata con BROADCASTING sugli assi che precedono
    l'ultimo:
    - v (N, D) e h (N, H)          -> (N,)
    - v (N, 1, D) e h (1, M, H)    -> (N, M)   [tutte le coppie]
    - v (D,) e h (H,)              -> array 0-d

    Parametri
    ---------
    v : (..., D) in {0,1}; h : (..., H) in {0,1}; W : (D, H); b : (D,); c : (H,)

    Ritorna
    -------
    ndarray con la shape ottenuta dal broadcasting dei prefissi di v e h.
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 3. Energia libera (marginalizzazione ANALITICA sulle nascoste)
# ---------------------------------------------------------------------------


def free_energy(v, W, b, c):
    """Energia libera F(v) = -log sum_h exp(-E(v, h)).

    La somma corre su tutte le 2^H configurazioni nascoste, eppure si calcola
    in forma chiusa:

        F(v) = -v@b - sum_j softplus(c_j + v@W[:, j]),   softplus(z) = log(1+e^z)

    DEVI SAPER DERIVARE QUESTA FORMULA, ed e' quello che il test principale
    verifica. Domanda guida: fissato v, che forma ha E(v, h) come funzione di
    h? Che cosa permette di spezzare una somma su 2^H termini in H somme da 2
    termini? Quale caratteristica del grafo la rende possibile?
    Scrivi la risposta qui sotto, in due righe, prima di scrivere il codice.

    Nota: ``np.logaddexp(0.0, z)`` calcola softplus in modo gia' stabile.
    Nota: F NON contiene log Z. Vale p(v) = exp(-F(v)) / Z, e Z resta
    intrattabile: l'energia libera e' trattabile, la likelihood no.

    Parametri
    ---------
    v : (N, D) in {0,1}; W : (D, H); b : (D,); c : (H,)

    Ritorna
    -------
    ndarray shape (N,)
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 4. Condizionali complete (fattorizzate: e' la "R" di RBM)
# ---------------------------------------------------------------------------


def p_h_given_v(v, W, c):
    """p(h_j = 1 | v) per ogni j. PROBABILITA', non campioni.

        p(h_j = 1 | v) = sigmoid(c_j + v @ W[:, j])

    Le H unita' sono condizionalmente indipendenti dato v: il grafo e'
    bipartito, quindi v separa tutte le nascoste fra loro.

    Parametri
    ---------
    v : (N, D); W : (D, H); c : (H,)

    Ritorna
    -------
    ndarray (N, H) con valori in (0, 1).
    """
    # TODO
    raise NotImplementedError


def p_v_given_h(h, W, b):
    """p(v_i = 1 | h) per ogni i. PROBABILITA', non campioni.

        p(v_i = 1 | h) = sigmoid(b_i + h @ W[i, :])

    Attenzione a quale verso di W serve qui rispetto a ``p_h_given_v``.

    Parametri
    ---------
    h : (N, H); W : (D, H); b : (D,)

    Ritorna
    -------
    ndarray (N, D) con valori in (0, 1).
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 5. Campionamento
# ---------------------------------------------------------------------------


def sample_bernoulli(p, rng):
    """Campioni binari indipendenti con P(1) = p, elemento per elemento.

    Requisito sui casi limite: con p esattamente 0 il campione deve essere 0 e
    con p esattamente 1 deve essere 1, sempre.

    Parametri
    ---------
    p : array_like di probabilita' in [0, 1]
    rng : numpy.random.Generator

    Ritorna
    -------
    ndarray float della stessa shape di ``p``, valori in {0.0, 1.0}.
    """
    # TODO
    raise NotImplementedError


def gibbs_step(v, W, b, c, rng):
    """Un passo completo di Gibbs A BLOCCHI: v -> h -> v.

    Ordine dei consumi di ``rng`` (fissato): prima il blocco h, poi il blocco v.

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
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 6. Contrastive divergence
# ---------------------------------------------------------------------------


def cd_k(v_data, W, b, c, k, rng):
    """Gradienti CD-k della log-likelihood. SEGNO: sono direzioni di ASCESA.

    Il gradiente esatto della log-likelihood media e'

        d mean_n log p(v_n) / dW = <v h^T>_dati - <v h^T>_modello
        d ... / db              = <v>_dati      - <v>_modello
        d ... / dc              = <h>_dati      - <h>_modello

    fase positiva meno fase negativa; il secondo termine viene da -d logZ/d(.).
    La fase negativa richiederebbe di campionare dalla congiunta del modello,
    cioe' una catena di Gibbs fatta girare fino a convergenza. CD-k la tronca a
    k passi e la fa PARTIRE DAI DATI.

    Specifica precisa:
    - fase positiva: usa le PROBABILITA' p(h=1 | v_data), non i bit campionati
      (aspettazione condizionale esatta: stessa media, varianza minore);
    - fase negativa: k passi di ``gibbs_step`` a partire da ``v_data``, poi le
      PROBABILITA' p(h=1 | v_model) calcolate sullo stato finale della catena;
    - i gradienti sono gia' mediati sul batch (divisi per N);
    - ``v_model`` e' lo stato VISIBILE BINARIO dopo i k passi, non una
      probabilita'.

    L'aggiornamento e' quindi  W <- W + lr * grad_W  (ASCESA), non una discesa.

    Parametri
    ---------
    v_data : (N, D) in {0,1}; W : (D, H); b : (D,); c : (H,)
    k : int >= 1, numero di passi di Gibbs della fase negativa
    rng : numpy.random.Generator

    Ritorna
    -------
    (grad_W, grad_b, grad_c, v_model)
        grad_W  : (D, H); grad_b : (D,); grad_c : (H,)
        v_model : (N, D) in {0,1}
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 7. Training
# ---------------------------------------------------------------------------


def train_rbm(X, H, epochs, lr, k=1, batch_size=10, seed=0):
    """Addestra una RBM binaria con CD-k e SGD a minibatch.

    Inizializzazione (FISSATA, i test ci contano - rispetta anche l'ordine):
        rng = np.random.default_rng(seed)
        W = 0.01 * rng.standard_normal((D, H)); b = zeros(D); c = zeros(H)
        X_noise = (rng.random(X.shape) < 0.5)      # riferimento per il gap

    Ogni epoca: ``perm = rng.permutation(N)``, poi minibatch consecutivi di
    ``batch_size`` indici di ``perm`` (l'ultimo puo' essere piu' corto), un
    aggiornamento di ASCESA per minibatch.

    Diagnostiche registrate a FINE EPOCA (una per epoca):
    - ``recon_error``: MSE fra X e la ricostruzione deterministica
      p(v | p(h | X)), cioe' senza campionare. NB: e' un PROXY, non la
      log-likelihood; puo' scendere anche mentre la log-likelihood peggiora.
    - ``free_energy_gap``: mean F(X) - mean F(X_noise). Diventa sempre piu'
      negativo man mano che il modello impara a dare energia bassa ai dati e
      alta al rumore.

    Parametri
    ---------
    X : (N, D) in {0,1}
    H : int, numero di unita' nascoste
    epochs : int (puo' essere 0: in quel caso restituisce i parametri iniziali
             e history vuote); lr : float; k : int; batch_size : int; seed : int

    Ritorna
    -------
    dict con chiavi
        "W" : (D, H), "b" : (D,), "c" : (H,)
        "recon_error_history"     : ndarray (epochs,)
        "free_energy_gap_history" : ndarray (epochs,)
    """
    # TODO
    raise NotImplementedError
