"""Esercizio GDL27-28 - "Tractable density models: Normalizing Flows".

Implementa le funzioni marcate `# TODO`. Tutto il resto (base gaussiana,
maschere, generatori di pesi casuali, softplus) e' gia' fornito e non va
toccato: i test lo usano per costruire flussi identici sullo skeleton e sulla
soluzione.

CONVENZIONE DI DIREZIONE (leggila due volte, e' la meta' dell'esercizio).
Il deck usa "forward/generative" per z -> x e "inverse/normalizing" per x -> z,
ma la formula della log-verosimiglianza della slide "Designing scalable flows"
e' scritta rispetto alla mappa che porta i dati nel rumore:

    log P(x) = log P(f(x)) + log |det J_x f|

Qui adottiamo quella: `f` e' la mappa x -> z e la chiamiamo `flow_forward`.
La direzione generativa z -> x e' `flow_inverse`, ed e' quella usata da
`sample`. Se inverti le due, l'invertibilita' continua a valere ma il segno del
log-determinante nella log-verosimiglianza si ribalta.

Solo numpy + stdlib. Ogni sorgente di casualita' passa da `rng`
(`numpy.random.Generator`): niente `np.random.seed`, niente `random`.
"""

from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Utilita' fornite - NON modificare.
# ---------------------------------------------------------------------------


def softplus(a):
    """softplus(a) = log(1 + exp(a)), implementazione numericamente stabile.

    Parametri
    ---------
    a : array_like, shape qualsiasi

    Ritorna
    -------
    ndarray della stessa shape di ``a``.
    """
    a = np.asarray(a, dtype=float)
    return np.logaddexp(0.0, a)


def standard_normal_logpdf(z):
    """log-densita' della distribuzione base P(z) = N(0, I), riga per riga.

        log P(z) = -0.5 * ||z||^2 - (D/2) * log(2 pi)

    Parametri
    ---------
    z : ndarray, shape (N, D)

    Ritorna
    -------
    ndarray, shape (N,)
    """
    z = np.asarray(z, dtype=float)
    D = z.shape[-1]
    return -0.5 * np.sum(z * z, axis=-1) - 0.5 * D * np.log(2.0 * np.pi)


def alternating_mask(D, parity):
    """Maschera binaria a scacchiera 1D, shape (D,), valori in {0.0, 1.0}.

    ``parity=0`` marca con 1 le posizioni pari, ``parity=1`` quelle dispari.
    Convenzione usata ovunque in questo file: le posizioni con maschera **1**
    sono COPIATE identiche (sono le condizionanti, la "b (*) z" della slide
    RealNVP), quelle con maschera **0** sono TRASFORMATE.

    Parametri
    ---------
    D : int, dimensione dello spazio.
    parity : int

    Ritorna
    -------
    ndarray, shape (D,), dtype float.
    """
    mask = np.zeros(D, dtype=float)
    mask[parity % 2 :: 2] = 1.0
    return mask


def random_coupling_params(D, hidden, rng, w_scale=0.35):
    """Pesi casuali per le due MLP (log-scala e traslazione) di un coupling layer.

    Ogni rete e' ``D -> hidden -> D``, con ``tanh`` sullo strato nascosto e
    uscita lineare.

    Parametri
    ---------
    D : int
    hidden : int, ampiezza dello strato nascosto.
    rng : numpy.random.Generator
    w_scale : float, ampiezza dell'inizializzazione.

    Ritorna
    -------
    dict con chiavi
        ``W1s`` (D, hidden), ``b1s`` (hidden,), ``W2s`` (hidden, D), ``b2s`` (D,)
            rete della LOG-SCALA (theta_A nella slide RealNVP)
        ``W1t``, ``b1t``, ``W2t``, ``b2t``
            rete della TRASLAZIONE (theta_B nella slide RealNVP)
    """
    out_scale = w_scale / np.sqrt(hidden)
    p = {}
    for tag in ("s", "t"):
        p["W1" + tag] = w_scale * rng.standard_normal((D, hidden))
        p["b1" + tag] = w_scale * rng.standard_normal(hidden)
        p["W2" + tag] = out_scale * rng.standard_normal((hidden, D))
        p["b2" + tag] = out_scale * rng.standard_normal(D)
    return p


def make_flow(D, n_layers, rng, hidden=6, w_scale=0.35):
    """Costruisce un flusso di ``n_layers`` coupling con maschere ALTERNATE.

    Parametri
    ---------
    D : int
    n_layers : int
    rng : numpy.random.Generator
    hidden, w_scale : vedi ``random_coupling_params``.

    Ritorna
    -------
    list di dict, uno per layer, con chiavi ``"params"`` (dict di pesi, vedi
    ``random_coupling_params``) e ``"mask"`` (ndarray shape (D,)). E' esattamente
    il formato che ``flow_forward`` / ``flow_inverse`` / ``flow_log_det`` /
    ``log_prob`` / ``sample`` ricevono nell'argomento ``layers``.
    """
    return [
        {
            "params": random_coupling_params(D, hidden, rng, w_scale),
            "mask": alternating_mask(D, i),
        }
        for i in range(n_layers)
    ]


def mlp(x, W1, b1, W2, b2):
    """MLP ``D -> hidden -> D``: ``tanh(x @ W1 + b1) @ W2 + b2``.

    Parametri
    ---------
    x : ndarray, shape (N, D)
    W1 : ndarray (D, hidden), b1 : ndarray (hidden,)
    W2 : ndarray (hidden, D), b2 : ndarray (D,)

    Ritorna
    -------
    ndarray, shape (N, D).
    """
    return np.tanh(x @ W1 + b1) @ W2 + b2


# ---------------------------------------------------------------------------
# 1. Coupling layer affine (RealNVP)
# ---------------------------------------------------------------------------


def affine_coupling_forward(x, params, mask):
    """Un coupling affine alla RealNVP, direzione x -> y.

    Con ``b = mask`` e le due reti theta_A (log-scala) e theta_B (traslazione),
    entrambe valutate sulla SOLA meta' mascherata ``b (*) x``:

        y = b (*) x + (1 - b) (*) { exp(theta_A(b (*) x)) (*) x + theta_B(b (*) x) }

    Le componenti con ``mask == 1`` escono identiche. Le componenti con
    ``mask == 0`` vengono scalate per ``exp(log_scale)`` e traslate. Entrambe
    le reti sono ``mlp(mask * x, W1?, b1?, W2?, b2?)``: producono un vettore di
    D componenti, ma solo quelle con maschera 0 vengono usate.

    Parametri
    ---------
    x : ndarray, shape (N, D)
    params : dict, pesi come da ``random_coupling_params``.
    mask : ndarray, shape (D,), valori in {0.0, 1.0}.

    Ritorna
    -------
    ndarray, shape (N, D).
    """
    # TODO
    raise NotImplementedError


def affine_coupling_inverse(y, params, mask):
    """Inversa ESATTA di ``affine_coupling_forward``, direzione y -> x.

        x = b (*) y + (1 - b) (*) (y - theta_B(b (*) y)) / exp(theta_A(b (*) y))

    Il motivo per cui l'inversa e' in forma chiusa: ``mask * y == mask * x``,
    quindi le due reti si rivalutano sullo STESSO input del forward pur non
    conoscendo x. Non serve nessuna iterazione, nessun solver.

    Parametri
    ---------
    y : ndarray, shape (N, D)
    params : dict, gli stessi pesi passati al forward.
    mask : ndarray, shape (D,), la stessa maschera passata al forward.

    Ritorna
    -------
    ndarray, shape (N, D).
    """
    # TODO
    raise NotImplementedError


def affine_coupling_log_det(x, params, mask):
    """log |det J| del coupling, valutato in ``x`` (input del forward).

    Lo Jacobiano di ``affine_coupling_forward`` e' triangolare a blocchi con
    diagonale ``[1, ..., 1, exp(log_scale)]``: il blocco fuori diagonale che
    contiene le derivate delle reti non entra nel determinante. Quindi

        log |det J| = somma dei log_scale sulle sole dimensioni con mask == 0

    La rete di traslazione theta_B non compare: una traslazione non cambia i
    volumi.

    Parametri
    ---------
    x : ndarray, shape (N, D)
    params : dict, pesi come da ``random_coupling_params``.
    mask : ndarray, shape (D,), valori in {0.0, 1.0}.

    Ritorna
    -------
    ndarray, shape (N,), un log-determinante per riga di ``x``.
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 2. Composizione dei layer
# ---------------------------------------------------------------------------


def flow_forward(x, layers):
    """Direzione NORMALIZZANTE f: x -> z, composizione di tutti i coupling.

    I layer vanno applicati nell'ordine in cui compaiono in ``layers``:
    ``z = f_N( ... f_2( f_1(x) ) ... )``.

    Parametri
    ---------
    x : ndarray, shape (N, D)
    layers : list di dict con chiavi ``"params"`` e ``"mask"`` (vedi ``make_flow``).

    Ritorna
    -------
    ndarray, shape (N, D).
    """
    # TODO
    raise NotImplementedError


def flow_inverse(z, layers):
    """Direzione GENERATIVA f^-1: z -> x, inversa di ``flow_forward``.

    Attenzione all'ordine: l'inversa di una composizione inverte anche la
    sequenza, ``f^-1 = f_1^-1 o ... o f_N^-1``. I layer vanno percorsi
    all'indietro.

    Parametri
    ---------
    z : ndarray, shape (N, D)
    layers : list di dict (vedi ``make_flow``).

    Ritorna
    -------
    ndarray, shape (N, D), tale che ``flow_forward(flow_inverse(z)) == z``.
    """
    # TODO
    raise NotImplementedError


def flow_log_det(x, layers):
    """log |det J_x f| dell'INTERA composizione, valutato in ``x``.

        log |det J_x f| = somma_i log |det J_{z_{i-1}} f_i|,   z_0 = x

    Il log-determinante del layer i-esimo va calcolato sul valore che quel
    layer riceve davvero, cioe' sull'uscita del layer i-1: bisogna far avanzare
    lo stato mentre si accumula la somma. Valutare tutti i log-det in ``x`` da'
    un risultato sbagliato appena i layer sono piu' di uno.

    Parametri
    ---------
    x : ndarray, shape (N, D)
    layers : list di dict (vedi ``make_flow``).

    Ritorna
    -------
    ndarray, shape (N,).
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 3. Densita' esplicita e campionamento
# ---------------------------------------------------------------------------


def log_prob(x, layers):
    """Log-verosimiglianza esatta dei dati sotto il flusso.

        log P(x) = log P(f(x)) + log |det J_x f|,    P(z) = N(0, I)

    Usa ``standard_normal_logpdf`` per il primo termine. Il segno del secondo
    termine e' PIU' perche' ``f`` e' la direzione normalizzante x -> z: e' la
    stessa formula della slide "Designing scalable flows".

    Parametri
    ---------
    x : ndarray, shape (N, D)
    layers : list di dict (vedi ``make_flow``).

    Ritorna
    -------
    ndarray, shape (N,).
    """
    # TODO
    raise NotImplementedError


def sample(layers, n, rng):
    """Campiona ``n`` punti dal modello.

    Si estrae ``z ~ N(0, I)`` di shape (n, D) con ``rng.standard_normal`` e si
    applica la direzione generativa ``flow_inverse``. La dimensione D si legge
    dalla maschera di un layer qualsiasi.

    Parametri
    ---------
    layers : list di dict (vedi ``make_flow``), non vuota.
    n : int
    rng : numpy.random.Generator

    Ritorna
    -------
    ndarray, shape (n, D).
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 4. Flusso planare (Rezende & Mohamed 2015)
# ---------------------------------------------------------------------------


def planar_flow_forward(x, u, w, b):
    """Flusso planare: ``f(x) = x + u * h(w^T x + b)``, con ``h = tanh``.

    E' una perturbazione di rango 1 dell'identita': deforma lo spazio solo
    lungo la direzione ``u``, in funzione della distanza dall'iperpiano
    ``w^T x + b = 0``.

    Parametri
    ---------
    x : ndarray, shape (N, D)
    u : ndarray, shape (D,)
    w : ndarray, shape (D,)
    b : float

    Ritorna
    -------
    ndarray, shape (N, D).
    """
    # TODO
    raise NotImplementedError


def planar_flow_log_det(x, u, w, b):
    """log |det J| del flusso planare.

        psi(x) = h'(w^T x + b) * w,      h' = 1 - tanh^2
        log |det J| = log(1 + u^T psi(x))

    Lo Jacobiano e' ``I + u psi(x)^T``, un aggiornamento di rango 1: per il
    lemma del determinante matriciale il determinante vale ``1 + psi(x)^T u``,
    calcolabile in O(D) senza mai costruire la matrice.

    Il logaritmo va preso SENZA valore assoluto, di proposito: se il flusso e'
    invertibile il termine ``1 + u^T psi(x)`` e' strettamente positivo e il
    valore assoluto sarebbe superfluo; se esce negativo il risultato e' NaN, ed
    e' l'informazione che serve, perche' quella trasformazione non e' una
    bigezione e la "densita'" che se ne ricava non ha senso.

    Parametri
    ---------
    x : ndarray, shape (N, D)
    u : ndarray, shape (D,)
    w : ndarray, shape (D,)
    b : float

    Ritorna
    -------
    ndarray, shape (N,). Puo' contenere NaN se il vincolo di invertibilita'
    non e' rispettato.
    """
    # TODO
    raise NotImplementedError


def enforce_invertibility(u, w):
    """Riparametrizza ``u`` in modo che il flusso planare sia invertibile.

    Condizione sufficiente (con ``h = tanh``, per cui ``h' in (0, 1]``):

        w^T u >= -1

    Si ottiene spostando ``u`` lungo ``w`` quel tanto che basta, senza toccare
    la componente ortogonale a ``w``:

        m(a) = -1 + softplus(a)
        u_hat = u + (m(w^T u) - w^T u) * w / ||w||^2

    Per costruzione ``w^T u_hat = m(w^T u) >= -1``, e quindi
    ``1 + u_hat^T psi(x) >= 0`` per ogni x.

    Parametri
    ---------
    u : ndarray, shape (D,)
    w : ndarray, shape (D,), non nullo.

    Ritorna
    -------
    ndarray, shape (D,).
    """
    # TODO
    raise NotImplementedError
