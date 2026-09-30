"""Soluzione di riferimento - GDL25 "Generative Adversarial Networks".

Discriminatore ottimo, valore del gioco all'ottimo, saturazione del gradiente
del generatore. Tutto su griglia 1D, integrali per quadratura: nessun
framework, nessun campionamento, nessuna stocasticita' nelle quantita' chiave.

Solo numpy + stdlib.
"""

from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Utilita' fornite - identiche a quelle dello skeleton.
# ---------------------------------------------------------------------------

LOG_FLOOR = 1e-300
"""Pavimento per gli argomenti dei logaritmi (vedi ``safe_log``)."""


def integrate(values, grid):
    """Integrale sulla griglia con la regola dei trapezi."""
    return float(np.trapezoid(np.asarray(values, dtype=float),
                              np.asarray(grid, dtype=float)))


def safe_log(t):
    """``log`` con l'argomento pavimentato a ``LOG_FLOOR``."""
    return np.log(np.clip(np.asarray(t, dtype=float), LOG_FLOOR, None))


def make_grid(lo=-8.0, hi=8.0, n=1601):
    """Griglia equispaziata su ``[lo, hi]``."""
    return np.linspace(float(lo), float(hi), int(n))


GRID = make_grid()
"""Griglia di default: 1601 punti su [-8, 8], passo 0.01."""


def gaussian_mixture_density(grid, means, stds, weights=None):
    """Miscela di gaussiane valutata su ``grid`` e RINORMALIZZATA per quadratura."""
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
    """Densita' uniforme su ``[lo, hi]``, ZERO ESATTO fuori, rinormalizzata."""
    grid = np.asarray(grid, dtype=float)
    p = np.where((grid >= lo) & (grid <= hi), 1.0, 0.0)
    return p / integrate(p, grid)


def generator_density(grid, theta):
    """Densita' del generatore giocattolo: N(theta[0], exp(theta[1])^2)."""
    theta = np.asarray(theta, dtype=float)
    return gaussian_mixture_density(grid, [theta[0]], [np.exp(theta[1])])


def sample_from_grid_density(grid, p, n, rng):
    """Campiona ``n`` punti da una densita' data su griglia (CDF inversa)."""
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
    """D*(x) = p_data(x) / (p_data(x) + p_g(x)), con 0/0 -> 0.5.

    L'integrando di C(D, G) e' ``p_data(x) log d + p_g(x) log(1 - d)``: e'
    separabile in x, quindi il massimo si trova punto per punto derivando in d,

        p_data/d - p_g/(1 - d) = 0   =>   d = p_data / (p_data + p_g)

    La derivata seconda e' ``-p_data/d^2 - p_g/(1-d)^2 <= 0``: e' un massimo.
    Dove entrambe le densita' sono nulle l'integrando e' identicamente zero e
    ogni valore di d va bene: si adotta 0.5 (il "non so" del classificatore).
    """
    p_data = np.asarray(p_data, dtype=float)
    p_g = np.asarray(p_g, dtype=float)
    s = p_data + p_g
    # np.where valuta entrambi i rami: il denominatore fittizio 1.0 evita
    # il warning e il nan sui punti in cui s == 0.
    safe_s = np.where(s > 0.0, s, 1.0)
    return np.where(s > 0.0, p_data / safe_s, 0.5)


# ---------------------------------------------------------------------------
# 2. Il valore del gioco
# ---------------------------------------------------------------------------


def discriminator_loss(D, p_data, p_g, grid):
    """C(D, G) = int p_data log D dx + int p_g log(1 - D) dx.

    ``safe_log`` implementa la convenzione ``0 * log 0 = 0``: dove la densita'
    che pesa il logaritmo e' nulla il prodotto e' ``0 * (-690.8) = 0``, non nan.
    """
    D = np.asarray(D, dtype=float)
    p_data = np.asarray(p_data, dtype=float)
    p_g = np.asarray(p_g, dtype=float)
    real_term = integrate(p_data * safe_log(D), grid)
    fake_term = integrate(p_g * safe_log(1.0 - D), grid)
    return real_term + fake_term


def generator_loss_minimax(D, p_g, grid):
    """Loss minimax del generatore: E_{p_g}[log(1 - D(x))], DA MINIMIZZARE."""
    D = np.asarray(D, dtype=float)
    p_g = np.asarray(p_g, dtype=float)
    return integrate(p_g * safe_log(1.0 - D), grid)


def generator_loss_nonsaturating(D, p_g, grid):
    """Loss non-saturating: -E_{p_g}[log D(x)], DA MINIMIZZARE.

    Massimizzare ``E[log D]`` (slide 11: "maximize likelihood of discriminator
    being wrong") equivale a minimizzare il suo opposto. Il segno meno serve a
    poter confrontare i due gradienti sulla stessa convenzione di discesa.
    """
    D = np.asarray(D, dtype=float)
    p_g = np.asarray(p_g, dtype=float)
    return -integrate(p_g * safe_log(D), grid)


# ---------------------------------------------------------------------------
# 3. Divergenze
# ---------------------------------------------------------------------------


def kl_divergence(p, q, grid):
    """KL(p || q) = int p log(p/q) dx, con 0 log 0 = 0.

    Il logaritmo viene spezzato in ``log p - log q`` (entrambi pavimentati):
    dove ``p == 0`` il fattore davanti annulla comunque il termine, dove
    ``p > 0`` e ``q == 0`` la KL e' matematicamente +inf ma qui viene
    troncata a ``p * (log p + 690.8)``, un numero grande e finito.
    """
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    return integrate(p * (safe_log(p) - safe_log(q)), grid)


def jsd(p, q, grid):
    """Jensen-Shannon: JSD(p||q) = 0.5 KL(p||m) + 0.5 KL(q||m), m = (p+q)/2.

    Simmetrica per costruzione, non negativa, e limitata da log 2: infatti
    ``m >= p/2`` puntualmente, quindi ``log(p/m) <= log 2`` e ogni KL vale al
    piu' log 2. Il massimo si raggiunge esattamente a supporti disgiunti.
    """
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    mix = 0.5 * (p + q)
    return 0.5 * kl_divergence(p, mix, grid) + 0.5 * kl_divergence(q, mix, grid)


def value_at_optimum(p_data, p_g, grid):
    """C(D*, G) = -log 4 + 2 JSD(p_data || p_g), in FORMA CHIUSA.

    Sostituendo D* nell'integrando e aggiungendo/togliendo log 2:

        p_d log(p_d/(p_d+p_g)) + p_g log(p_g/(p_d+p_g))
          = p_d log(p_d/m) + p_g log(p_g/m) - (p_d + p_g) log 2,   m=(p_d+p_g)/2

    integrando (e usando int p_d = int p_g = 1) si ottiene
    ``2 JSD - 2 log 2 = -log 4 + 2 JSD``. Il minimo su G vale -log 4 ed e'
    raggiunto solo per p_g = p_data, dove la JSD si annulla.

    NB: questa funzione NON deve chiamare ``discriminator_loss``: e' l'altro
    lato dell'identita' e il test confronta i due percorsi.
    """
    return -np.log(4.0) + 2.0 * jsd(p_data, p_g, grid)


# ---------------------------------------------------------------------------
# 4. Gradiente del generatore e discesa giocattolo
# ---------------------------------------------------------------------------


_GEN_LOSSES = {
    "minimax": generator_loss_minimax,
    "nonsaturating": generator_loss_nonsaturating,
}


def generator_gradient(theta, p_data, grid, variant, h=1e-4):
    """Gradiente della loss del generatore rispetto a theta, D TENUTO FISSO.

    Il punto delicato: D viene calcolato UNA VOLTA sul p_g corrente e poi
    congelato. Le differenze finite perturbano theta solo dentro p_g. E'
    esattamente il passo 2 della slide 10 (il discriminatore ha gia' fatto la
    sua ascesa e non si muove mentre il generatore scende). Se si ricalcolasse
    D a ogni theta perturbato si differenzierebbe il valore all'ottimo
    ``-log 4 + 2 JSD``, che e' un'altra funzione e non satura affatto.
    """
    theta = np.asarray(theta, dtype=float)
    if variant not in _GEN_LOSSES:
        raise ValueError(f"variant sconosciuta: {variant!r}")
    loss = _GEN_LOSSES[variant]

    D = optimal_discriminator(p_data, generator_density(grid, theta))

    grad = np.zeros_like(theta)
    for i in range(theta.size):
        tp = theta.copy()
        tp[i] += h
        tm = theta.copy()
        tm[i] -= h
        lp = loss(D, generator_density(grid, tp), grid)
        lm = loss(D, generator_density(grid, tm), grid)
        grad[i] = (lp - lm) / (2.0 * h)
    return grad


def train_generator(theta0, p_data, grid, variant, lr=0.01, n_steps=60, h=1e-4):
    """Ciclo giocattolo: discriminatore all'ottimo + un passo di discesa su G.

    A ogni iterazione il discriminatore e' gia' al suo massimo (forma chiusa,
    e' l'ascesa del passo 1), quindi si registra la loss corrente del
    generatore e si fa un passo di discesa ``theta <- theta - lr * grad``.
    """
    theta = np.asarray(theta0, dtype=float).copy()
    loss = _GEN_LOSSES[variant]

    thetas = [theta.copy()]
    losses = []
    grad_norms = []
    for _ in range(int(n_steps)):
        p_g = generator_density(grid, theta)
        D = optimal_discriminator(p_data, p_g)
        losses.append(loss(D, p_g, grid))
        g = generator_gradient(theta, p_data, grid, variant, h=h)
        grad_norms.append(float(np.linalg.norm(g)))
        theta = theta - lr * g
        thetas.append(theta.copy())

    p_g = generator_density(grid, theta)
    losses.append(loss(optimal_discriminator(p_data, p_g), p_g, grid))
    return np.array(thetas), np.array(losses), np.array(grad_norms)
