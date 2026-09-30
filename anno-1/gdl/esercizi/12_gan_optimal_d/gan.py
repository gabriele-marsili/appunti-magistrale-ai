"""Esercizio GDL25 - "Generative Adversarial Networks".

Il discriminatore ottimo e che cosa minimizza davvero il generatore.

Tutto vive su una griglia 1D: ``p_data`` e ``p_g`` sono densita' gia' valutate
sui punti di ``grid`` (array di shape ``(n,)``), gli integrali si fanno per
quadratura. Non serve nessun framework di deep learning, e ogni quantita' del
deck (valore del gioco, D*, JSD, gradiente del generatore) diventa calcolabile
in modo esatto.

Implementa le funzioni marcate ``# TODO``. Tutto il resto (griglia, costruttori
di densita', logaritmo protetto, quadratura, campionatore) e' gia' fornito e
non va toccato: i test lo usano.

Solo numpy + stdlib. Ogni sorgente di casualita' passa da ``rng``
(``numpy.random.Generator``): niente ``np.random.seed``, niente ``random``.
"""

from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Utilita' fornite - NON modificare.
# ---------------------------------------------------------------------------

LOG_FLOOR = 1e-300
"""Pavimento per gli argomenti dei logaritmi (vedi ``safe_log``)."""


def integrate(values, grid):
    """Integrale sulla griglia con la regola dei trapezi.

    Usa SEMPRE questa funzione per gli integrali: i test confrontano risultati
    ottenuti con la stessa quadratura e le tolleranze sono tarate su di essa.

    Parametri
    ---------
    values : array_like, shape (n,) - integrando gia' valutato su ``grid``.
    grid : array_like, shape (n,) - ascisse crescenti.

    Ritorna
    -------
    float
    """
    return float(np.trapezoid(np.asarray(values, dtype=float),
                              np.asarray(grid, dtype=float)))


def safe_log(t):
    """``log`` con l'argomento pavimentato a ``LOG_FLOOR``.

    Serve a implementare la convenzione ``0 * log 0 = 0``: ``log(0)`` diventa
    ``log(1e-300) ~ -690.8``, un numero finito, e moltiplicato per una densita'
    nulla da' esattamente 0 invece di ``nan``. Usala ovunque compaia un
    logaritmo di una densita' o di una probabilita'.

    Parametri
    ---------
    t : array_like, valori >= 0.

    Ritorna
    -------
    ndarray della stessa shape di ``t``, sempre finito.
    """
    return np.log(np.clip(np.asarray(t, dtype=float), LOG_FLOOR, None))


def make_grid(lo=-8.0, hi=8.0, n=1601):
    """Griglia equispaziata su ``[lo, hi]``. Ritorna ndarray shape ``(n,)``."""
    return np.linspace(float(lo), float(hi), int(n))


GRID = make_grid()
"""Griglia di default: 1601 punti su [-8, 8], passo 0.01."""


def gaussian_mixture_density(grid, means, stds, weights=None):
    """Miscela di gaussiane valutata su ``grid`` e RINORMALIZZATA per quadratura.

    La rinormalizzazione garantisce ``integrate(p, grid) == 1`` a meno
    dell'epsilon macchina: e' quello che rende esatte le identita' testate
    (che usano ``int p_data = int p_g = 1``).

    Parametri
    ---------
    grid : ndarray, shape (n,)
    means, stds : array_like, shape (k,)
    weights : array_like, shape (k,) o None (uniformi). Vengono rinormalizzati.

    Ritorna
    -------
    ndarray, shape (n,), valori > 0.
    """
    grid = np.asarray(grid, dtype=float)
    means = np.atleast_1d(np.asarray(means, dtype=float))
    stds = np.atleast_1d(np.asarray(stds, dtype=float))
    if weights is None:
        w = np.full(means.shape, 1.0 / means.size)
    else:
        w = np.atleast_1d(np.asarray(weights, dtype=float))
        w = w / w.sum()
    z = (grid[None, :] - means[:, None]) / stds[:, None]
    comp = np.exp(-0.5 * z * z) / (stds[:, None] * np.sqrt(2.0 * np.pi))
    p = (w[:, None] * comp).sum(axis=0)
    return p / integrate(p, grid)


def uniform_density(grid, lo, hi):
    """Densita' uniforme su ``[lo, hi]``, ZERO ESATTO fuori, rinormalizzata.

    Serve per costruire supporti davvero disgiunti (le gaussiane non lo sono
    mai). Ritorna ndarray shape ``(n,)``.
    """
    grid = np.asarray(grid, dtype=float)
    p = np.where((grid >= lo) & (grid <= hi), 1.0, 0.0)
    return p / integrate(p, grid)


def generator_density(grid, theta):
    """Densita' del generatore giocattolo: ``N(theta[0], exp(theta[1])^2)``.

    Il generatore ha due soli parametri: la media e il LOGARITMO della
    deviazione standard (cosi' theta vive in R^2 senza vincoli). E' il
    ``p_g`` indotto da ``G_theta(z) = theta[0] + exp(theta[1]) * z``, con
    ``z ~ N(0, 1)``: e' il push-forward del rumore, esattamente la
    "differentiable deterministic function" della slide 7.

    Parametri
    ---------
    grid : ndarray, shape (n,)
    theta : array_like, shape (2,)

    Ritorna
    -------
    ndarray, shape (n,).
    """
    theta = np.asarray(theta, dtype=float)
    return gaussian_mixture_density(grid, [theta[0]], [np.exp(theta[1])])


def sample_from_grid_density(grid, p, n, rng):
    """Campiona ``n`` punti da una densita' data su griglia, via CDF inversa.

    Usato SOLO dai test, come oracolo Monte Carlo indipendente dalla
    quadratura. Ritorna ndarray shape ``(n,)``.
    """
    grid = np.asarray(grid, dtype=float)
    p = np.asarray(p, dtype=float)
    dx = np.diff(grid)
    cdf = np.concatenate([[0.0], np.cumsum(0.5 * (p[1:] + p[:-1]) * dx)])
    cdf = cdf / cdf[-1]
    u = rng.random(int(n))
    return np.interp(u, cdf, grid)


P_DATA = gaussian_mixture_density(GRID, [-1.5, 1.5], [0.5, 0.5])
"""Distribuzione dei dati: bimodale, 0.5 N(-1.5, 0.5^2) + 0.5 N(1.5, 0.5^2)."""

THETA_OVERLAP = np.array([0.0, np.log(1.2)])
"""Generatore che copre bene i dati: N(0, 1.2^2). D* resta lontano da 0 e 1."""

THETA_FAR = np.array([5.5, np.log(0.3)])
"""Generatore quasi disgiunto dai dati: N(5.5, 0.3^2). D* ~ 0 dove p_g ha massa."""


# ---------------------------------------------------------------------------
# 1. Discriminatore ottimo
# ---------------------------------------------------------------------------


def optimal_discriminator(p_data, p_g):
    """Discriminatore ottimo per G fisso, valutato sulla griglia.

        D*(x) = p_data(x) / (p_data(x) + p_g(x))

    Convenzione: dove ``p_data(x) + p_g(x) == 0`` (nessuna delle due
    distribuzioni mette massa nel punto) il valore non e' determinato dal
    problema di massimo; restituisci ``0.5``. Non devono comparire ``nan``.

    Parametri
    ---------
    p_data : ndarray, shape (n,), densita' dei dati sulla griglia, valori >= 0.
    p_g : ndarray, shape (n,), densita' del generatore, valori >= 0.

    Ritorna
    -------
    ndarray, shape (n,), valori in [0, 1].
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 2. Il valore del gioco
# ---------------------------------------------------------------------------


def discriminator_loss(D, p_data, p_g, grid):
    """Valore del gioco per una coppia (D, G), integrato per quadratura.

        C(D, G) = E_{x~p_data}[log D(x)] + E_{x~p_g}[log(1 - D(x))]
                = int p_data(x) log D(x) dx + int p_g(x) log(1 - D(x)) dx

    E' la quantita' che il discriminatore MASSIMIZZA (slide 9-10). Usa
    ``safe_log`` per i logaritmi e ``integrate`` per gli integrali.

    Parametri
    ---------
    D : ndarray, shape (n,), valori in [0, 1].
    p_data, p_g : ndarray, shape (n,).
    grid : ndarray, shape (n,).

    Ritorna
    -------
    float (finito: nessun ``inf``, nessun ``nan``).
    """
    # TODO
    raise NotImplementedError


def generator_loss_minimax(D, p_g, grid):
    """Loss minimax del generatore, DA MINIMIZZARE.

        C_G = E_{x~p_g}[log(1 - D(x))] = int p_g(x) log(1 - D(x)) dx

    E' il secondo addendo di ``discriminator_loss``, l'unico che dipende da G
    (slide 10, "Optimizing this doesn't really work").

    Parametri
    ---------
    D : ndarray, shape (n,), valori in [0, 1].
    p_g : ndarray, shape (n,).
    grid : ndarray, shape (n,).

    Ritorna
    -------
    float, <= 0.
    """
    # TODO
    raise NotImplementedError


def generator_loss_nonsaturating(D, p_g, grid):
    """Loss non-saturating del generatore, DA MINIMIZZARE.

        C_G = - E_{x~p_g}[log D(x)] = - int p_g(x) log D(x) dx

    La slide 11 la scrive come massimizzazione di ``E[log D]``; qui viene
    restituita col segno cambiato, cosi' che ENTRAMBE le varianti si
    minimizzino e i due gradienti siano confrontabili sulla stessa
    convenzione. Attenzione al segno: con ``D < 1`` ovunque il valore e'
    positivo.

    Parametri
    ---------
    D : ndarray, shape (n,), valori in [0, 1].
    p_g : ndarray, shape (n,).
    grid : ndarray, shape (n,).

    Ritorna
    -------
    float, >= 0.
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 3. Divergenze
# ---------------------------------------------------------------------------


def kl_divergence(p, q, grid):
    """Kullback-Leibler fra densita' su griglia.

        KL(p || q) = int p(x) log(p(x) / q(x)) dx

    Convenzione ``0 log 0 = 0``: dove ``p(x) == 0`` il contributo e' nullo
    qualunque sia ``q(x)``. Usa ``safe_log`` (il logaritmo pavimentato rende
    finito anche il caso ``p > 0, q == 0``, che matematicamente sarebbe +inf).

    Parametri
    ---------
    p, q : ndarray, shape (n,), valori >= 0.
    grid : ndarray, shape (n,).

    Ritorna
    -------
    float, >= 0 se p e q sono entrambe normalizzate.
    """
    # TODO
    raise NotImplementedError


def jsd(p, q, grid):
    """Divergenza di Jensen-Shannon, in NAT.

        m = (p + q) / 2
        JSD(p || q) = 0.5 KL(p || m) + 0.5 KL(q || m)

    Simmetrica, non negativa, e limitata superiormente da ``log 2`` (valore
    raggiunto esattamente quando i supporti sono disgiunti).

    Parametri
    ---------
    p, q : ndarray, shape (n,), densita' normalizzate sulla griglia.
    grid : ndarray, shape (n,).

    Ritorna
    -------
    float in [0, log 2].
    """
    # TODO
    raise NotImplementedError


def value_at_optimum(p_data, p_g, grid):
    """Valore del gioco quando il discriminatore e' ottimo, in FORMA CHIUSA.

        C(D*, G) = -log 4 + 2 JSD(p_data || p_g)

    E' il risultato centrale della lezione: una volta che il discriminatore ha
    fatto la sua ascesa, cio' che il generatore sta minimizzando NON e' una
    generica "loss adversarial" ma una divergenza fra p_g e p_data. Il minimo
    vale ``-log 4`` ed e' raggiunto solo per ``p_g == p_data``.

    IMPORTANTE: implementala dalla formula chiusa (via ``jsd``), NON chiamando
    ``optimal_discriminator`` + ``discriminator_loss``. Il test confronta i due
    percorsi e se sono lo stesso codice non verifica nulla.

    Parametri
    ---------
    p_data, p_g : ndarray, shape (n,), densita' normalizzate.
    grid : ndarray, shape (n,).

    Ritorna
    -------
    float, >= -log 4.
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 4. Gradiente del generatore e discesa giocattolo
# ---------------------------------------------------------------------------


def generator_gradient(theta, p_data, grid, variant, h=1e-4):
    """Gradiente della loss del generatore rispetto a ``theta``, D TENUTO FISSO.

    Procedura:

    1. calcola ``p_g`` corrente con ``generator_density(grid, theta)`` e da li'
       il discriminatore ottimo ``D``. Questo D e' il risultato dell'ascesa del
       discriminatore (passo 1 della slide 10) e va CONGELATO;
    2. per ogni componente ``i`` di ``theta``, differenze finite CENTRALI di
       passo ``h`` sulla loss scelta, ricalcolando SOLO ``p_g`` in
       ``theta +/- h e_i`` e riusando lo stesso ``D`` del punto 1.

    Il punto 2 e' l'intero esercizio: se ricalcolassi D a ogni theta perturbato
    staresti differenziando ``-log 4 + 2 JSD``, cioe' il valore all'ottimo, che
    e' un'altra funzione e non satura.

    Parametri
    ---------
    theta : array_like, shape (2,).
    p_data : ndarray, shape (n,).
    grid : ndarray, shape (n,).
    variant : str, ``"minimax"`` oppure ``"nonsaturating"``.
    h : float, passo delle differenze finite.

    Ritorna
    -------
    ndarray, shape (2,).
    """
    # TODO
    raise NotImplementedError


def train_generator(theta0, p_data, grid, variant, lr=0.01, n_steps=60, h=1e-4):
    """Discesa a gradiente giocattolo sul generatore, discriminatore all'ottimo.

    A ogni iterazione:

    1. ricalcola ``p_g`` e il discriminatore ottimo per il ``theta`` corrente
       (l'ascesa del discriminatore, qui in forma chiusa e a convergenza);
    2. registra la loss corrente del generatore;
    3. un passo di discesa ``theta <- theta - lr * generator_gradient(...)``.

    Dopo l'ultimo passo va registrata anche la loss finale, quindi ``losses``
    ha un elemento in piu' di ``grad_norms``.

    Parametri
    ---------
    theta0 : array_like, shape (2,).
    p_data : ndarray, shape (n,).
    grid : ndarray, shape (n,).
    variant : str, ``"minimax"`` oppure ``"nonsaturating"``.
    lr : float, learning rate.
    n_steps : int, numero di passi di discesa.
    h : float, passo delle differenze finite.

    Ritorna
    -------
    thetas : ndarray, shape (n_steps + 1, 2), con ``thetas[0] == theta0``.
    losses : ndarray, shape (n_steps + 1,).
    grad_norms : ndarray, shape (n_steps,), norma euclidea del gradiente usato
        a ogni passo.
    """
    # TODO
    raise NotImplementedError
