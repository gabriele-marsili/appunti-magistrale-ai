"""Esercizio GDL24 - "Variational Autoencoders" - SOLUZIONE DI RIFERIMENTO.

ELBO, KL in forma chiusa, reparameterization trick e confronto fra lo stimatore
pathwise (reparam) e lo stimatore score function (REINFORCE).

Solo numpy + stdlib. Ogni sorgente di casualita' passa da `rng`
(`numpy.random.Generator`): niente `np.random.seed`, niente `random`.

Notazione della lezione (slide 21-26):

    log P(x|theta) >= E_Q[log P(x,z)] - E_Q[log Q(z)] = L(x, theta, phi)
    L(x, theta, phi) = E_Q[log P(x|z)] - KL( Q(z|x,phi) || P(z) )
    z = mu(x) + sigma^{1/2}(x) * eps,      eps ~ N(0, I)

Qui `log_var` e' il logaritmo della VARIANZA (quello che nella slide e' scritto
sigma(x)), quindi la deviazione standard e' exp(0.5 * log_var).
"""

from __future__ import annotations

import numpy as np

LOG_2PI = float(np.log(2.0 * np.pi))

# ---------------------------------------------------------------------------
# Modello giocattolo fornito - NON modificare.
#
# Latente z scalare, osservabile x scalare, prior P(z) = N(0, 1) e decoder
# LINEARE-gaussiano
#
#     P(x | z) = N(x ; TOY_A * z + TOY_B, exp(TOY_X_LOG_VAR))
#
# E' l'unico caso in cui la marginale P(x) = int P(x|z) P(z) dz e la posterior
# P(z|x) si scrivono in forma chiusa: serve da oracolo esatto per l'ELBO.
# ---------------------------------------------------------------------------

TOY_A = 1.2
TOY_B = -0.3
TOY_X_LOG_VAR = float(np.log(0.49))  # deviazione standard 0.7


def toy_decoder(z):
    """Decoder del modello giocattolo: mappa z nei parametri di P(x|z).

    Parametri
    ---------
    z : ndarray, shape (..., 1)

    Ritorna
    -------
    (x_mean, x_log_var) : due ndarray di shape (..., 1)
        media e log-varianza della gaussiana P(x|z). La log-varianza e'
        costante (decoder a rumore omoschedastico).
    """
    z = np.asarray(z, dtype=float)
    return TOY_A * z + TOY_B, np.full_like(z, TOY_X_LOG_VAR)


def toy_log_evidence(x, lo=-14.0, hi=14.0, n_grid=200001):
    """log P(x) del modello giocattolo, calcolata per QUADRATURA.

        P(x) = int N(x ; TOY_A z + TOY_B, exp(TOY_X_LOG_VAR)) N(z ; 0, 1) dz

    Regola dei trapezi su una griglia fittissima in z. E' l'oracolo esatto
    contro cui si misura l'ELBO: nessun campionamento coinvolto.

    Parametri
    ---------
    x : array_like, shape (B,)
    lo, hi, n_grid : estremi e risoluzione della griglia di quadratura.

    Ritorna
    -------
    ndarray, shape (B,)
    """
    x = np.asarray(x, dtype=float).reshape(-1)
    grid = np.linspace(lo, hi, n_grid)                       # (G,)
    var_x = np.exp(TOY_X_LOG_VAR)
    mu_x = TOY_A * grid + TOY_B                              # (G,)
    cond = np.exp(-0.5 * (x[:, None] - mu_x[None, :]) ** 2 / var_x) / np.sqrt(
        2.0 * np.pi * var_x
    )                                                        # (B, G)
    prior = np.exp(-0.5 * grid ** 2) / np.sqrt(2.0 * np.pi)  # (G,)
    return np.log(np.trapezoid(cond * prior[None, :], grid, axis=1))


def toy_posterior(x):
    """Posterior esatta P(z|x) del modello giocattolo (lineare-gaussiano).

    Con prior N(0,1) e verosimiglianza N(x ; a z + b, s^2) la posterior e'
    gaussiana con varianza s^2 / (s^2 + a^2) e media a (x - b) / (s^2 + a^2).

    Parametri
    ---------
    x : array_like, shape (B,)

    Ritorna
    -------
    (mean, log_var) : due ndarray di shape (B, 1)
    """
    x = np.asarray(x, dtype=float).reshape(-1)
    var_x = np.exp(TOY_X_LOG_VAR)
    denom = var_x + TOY_A ** 2
    post_var = var_x / denom
    post_mean = TOY_A * (x - TOY_B) / denom
    return post_mean[:, None], np.full((x.size, 1), np.log(post_var))


# ---------------------------------------------------------------------------
# 1. Log-densita' gaussiana diagonale
# ---------------------------------------------------------------------------


def gaussian_log_prob(x, mean, log_var):
    """log N(x ; mean, diag(exp(log_var))), sommata sulle dimensioni.

    Parametri
    ---------
    x : array_like, shape (..., D)
    mean, log_var : array_like, broadcastabili contro ``x``.

    Ritorna
    -------
    ndarray, shape (...) - l'ultimo asse (le D dimensioni) e' SOMMATO via.
    """
    x = np.asarray(x, dtype=float)
    mean = np.asarray(mean, dtype=float)
    log_var = np.asarray(log_var, dtype=float)
    # exp(-log_var) invece di 1/exp(log_var): stessa cosa in aritmetica esatta,
    # ma non passa da un exp che puo' andare in underflow a 0.
    quad = (x - mean) ** 2 * np.exp(-log_var)
    return -0.5 * np.sum(LOG_2PI + log_var + quad, axis=-1)


# ---------------------------------------------------------------------------
# 2. KL in forma chiusa contro il prior standard
# ---------------------------------------------------------------------------


def kl_diag_gaussian_standard(mean, log_var):
    """KL( N(mean, diag(exp(log_var))) || N(0, I) ), in forma chiusa.

        KL = 0.5 * sum_d ( exp(log_var_d) + mean_d^2 - 1 - log_var_d )

    E' il termine di regolarizzazione dell'ELBO (slide 25): non serve
    campionare nulla, si calcola esattamente.

    Parametri
    ---------
    mean, log_var : array_like, shape (..., D)

    Ritorna
    -------
    ndarray, shape (...) - una KL per esempio, dimensioni latenti sommate.
    """
    mean = np.asarray(mean, dtype=float)
    log_var = np.asarray(log_var, dtype=float)
    return 0.5 * np.sum(np.exp(log_var) + mean ** 2 - 1.0 - log_var, axis=-1)


# ---------------------------------------------------------------------------
# 3. Reparameterization trick
# ---------------------------------------------------------------------------


def reparameterize(mean, log_var, rng):
    """z = mean + exp(0.5 * log_var) * eps, con eps ~ N(0, I).

    Il rumore eps NON dipende dai parametri: e' esattamente cio' che rende
    l'espressione derivabile rispetto a ``mean`` e ``log_var`` (slide 22).

    Parametri
    ---------
    mean, log_var : ndarray, stessa shape (..., D)
    rng : numpy.random.Generator

    Ritorna
    -------
    ndarray, stessa shape di ``mean``.
    """
    mean = np.asarray(mean, dtype=float)
    log_var = np.asarray(log_var, dtype=float)
    eps = rng.standard_normal(mean.shape)
    return mean + np.exp(0.5 * log_var) * eps


# ---------------------------------------------------------------------------
# 4. ELBO
# ---------------------------------------------------------------------------


def elbo(x, mean, log_var, decoder_fn, rng, n_samples=1):
    """Stima Monte Carlo dell'ELBO, per esempio del batch.

        L = (1/S) sum_s log P(x | z_s)  -  KL( Q(z|x) || N(0,I) )
        z_s = mean + exp(0.5 * log_var) * eps_s,   eps_s ~ N(0, I)

    Solo il primo termine e' stimato per campionamento; la KL e' analitica.

    Parametri
    ---------
    x : ndarray, shape (B, Dx)
    mean, log_var : ndarray, shape (B, D) - parametri di Q(z|x) per esempio.
    decoder_fn : callable
        ``decoder_fn(z) -> (x_mean, x_log_var)`` con ``z`` di shape
        ``(S, B, D)`` e le due uscite di shape ``(S, B, Dx)``.
    rng : numpy.random.Generator
    n_samples : int
        numero S di campioni Monte Carlo. Nel VAE standard vale 1.

    Ritorna
    -------
    ndarray, shape (B,) - un ELBO per esempio.
    """
    x = np.asarray(x, dtype=float)
    mean = np.asarray(mean, dtype=float)
    log_var = np.asarray(log_var, dtype=float)
    B, D = mean.shape
    S = int(n_samples)

    # Un solo blocco di rumore (S, B, D): reparameterize sceglie la shape del
    # rumore in base a quella di mean, quindi basta replicare i parametri.
    mean_rep = np.broadcast_to(mean, (S, B, D))
    log_var_rep = np.broadcast_to(log_var, (S, B, D))
    z = reparameterize(mean_rep, log_var_rep, rng)            # (S, B, D)

    x_mean, x_log_var = decoder_fn(z)                          # (S, B, Dx)
    rec = gaussian_log_prob(x[None, :, :], x_mean, x_log_var)  # (S, B)

    return rec.mean(axis=0) - kl_diag_gaussian_standard(mean, log_var)


# ---------------------------------------------------------------------------
# 5. Due stimatori del gradiente di E_q[f(z)]
# ---------------------------------------------------------------------------


def reparam_grad_estimator(grad_f, mean, log_var, rng, n_samples):
    """Stimatore PATHWISE del gradiente di E_q[f(z)] (reparameterization trick).

    Scrivendo z = mean + std * eps con std = exp(0.5 * log_var) e eps ~ N(0,I),
    l'attesa e' rispetto a una distribuzione che NON dipende dai parametri,
    quindi il gradiente entra dentro l'attesa (slide 26):

        d/d mean    E_q[f(z)] = E_eps[ f'(z) * d z / d mean ]    = E_eps[ f'(z) ]
        d/d log_var E_q[f(z)] = E_eps[ f'(z) * d z / d log_var ]
                              = E_eps[ f'(z) * 0.5 * std * eps ]

    Richiede il gradiente di f: e' il prezzo del basso rumore.

    Parametri
    ---------
    grad_f : callable
        ``grad_f(z) -> ndarray (S, D)``, gradiente di f rispetto a z, con
        ``z`` di shape ``(S, D)``.
    mean, log_var : ndarray, shape (D,)
    rng : numpy.random.Generator
    n_samples : int, numero S di campioni.

    Ritorna
    -------
    (grad_mean, grad_log_var) : due ndarray di shape (D,).
    """
    mean = np.asarray(mean, dtype=float)
    log_var = np.asarray(log_var, dtype=float)
    D = mean.shape[-1]
    S = int(n_samples)

    eps = rng.standard_normal((S, D))
    std = np.exp(0.5 * log_var)
    z = mean + std * eps                       # (S, D)

    g = np.asarray(grad_f(z), dtype=float)     # (S, D)
    grad_mean = g.mean(axis=0)
    # dz/d log_var = 0.5 * exp(0.5*log_var) * eps = 0.5 * std * eps
    grad_log_var = (g * (0.5 * std * eps)).mean(axis=0)
    return grad_mean, grad_log_var


def score_function_grad_estimator(f, mean, log_var, rng, n_samples, baseline=None):
    """Stimatore SCORE FUNCTION (REINFORCE) del gradiente di E_q[f(z)].

    Identita' del log-derivative: poiche' d q / d phi = q * d log q / d phi,

        d/d phi E_q[f(z)] = E_q[ f(z) * d log q(z) / d phi ]

    Per q gaussiana diagonale con std = exp(0.5 * log_var):

        d log q / d mean    = (z - mean) / exp(log_var) = eps / std
        d log q / d log_var = 0.5 * ( (z-mean)^2 / exp(log_var) - 1 )
                            = 0.5 * ( eps^2 - 1 )

    Poiche' E_q[ d log q / d phi ] = 0, si puo' sottrarre a f(z) una costante
    ``baseline`` senza introdurre distorsione: cambia solo la varianza.

    NON richiede il gradiente di f: funziona anche con f non differenziabile
    (indicatrici, ricompense, output discreti). Ma ha varianza molto piu' alta.

    Parametri
    ---------
    f : callable
        ``f(z) -> ndarray (S,)``, con ``z`` di shape ``(S, D)``.
    mean, log_var : ndarray, shape (D,)
    rng : numpy.random.Generator
    n_samples : int, numero S di campioni.
    baseline : float oppure None
        costante da sottrarre a f(z). ``None`` equivale a 0.0.

    Ritorna
    -------
    (grad_mean, grad_log_var) : due ndarray di shape (D,).
    """
    mean = np.asarray(mean, dtype=float)
    log_var = np.asarray(log_var, dtype=float)
    D = mean.shape[-1]
    S = int(n_samples)

    eps = rng.standard_normal((S, D))
    std = np.exp(0.5 * log_var)
    z = mean + std * eps                       # (S, D)

    # Qui eps serve solo come modo di campionare da q: lo stimatore score
    # function non usa mai la derivabilita' del percorso mean -> z.
    fv = np.asarray(f(z), dtype=float).reshape(S, 1)
    b = 0.0 if baseline is None else float(baseline)
    advantage = fv - b                         # (S, 1)

    dlogq_dmean = eps / std                    # (S, D)
    dlogq_dlogvar = 0.5 * (eps ** 2 - 1.0)     # (S, D)

    grad_mean = (advantage * dlogq_dmean).mean(axis=0)
    grad_log_var = (advantage * dlogq_dlogvar).mean(axis=0)
    return grad_mean, grad_log_var
