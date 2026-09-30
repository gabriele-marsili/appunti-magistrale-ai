"""Esercizio GDL13 - "Sampling methods and approximations".

Implementa le funzioni marcate `# TODO`. Tutto il resto (densita' di esempio,
costanti di riferimento calcolate per quadratura, utilita' gaussiane) e' gia'
fornito e non va toccato.

Solo numpy + stdlib. Ogni sorgente di casualita' passa da `rng`
(`numpy.random.Generator`): niente `np.random.seed`, niente `random`.
"""

from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Utilita' fornite - NON modificare.
# ---------------------------------------------------------------------------


def normal_pdf(x, mu=0.0, sigma=1.0):
    """Densita' gaussiana NORMALIZZATA N(mu, sigma^2), valutata elemento per elemento.

    Parametri
    ---------
    x : array_like, shape qualsiasi
    mu, sigma : float (sigma > 0)

    Ritorna
    -------
    ndarray della stessa shape di ``x``.
    """
    x = np.asarray(x, dtype=float)
    z = (x - mu) / sigma
    return np.exp(-0.5 * z * z) / (sigma * np.sqrt(2.0 * np.pi))


def normal_logpdf(x, mu=0.0, sigma=1.0):
    """Log-densita' gaussiana normalizzata. Stessa convenzione di ``normal_pdf``."""
    x = np.asarray(x, dtype=float)
    z = (x - mu) / sigma
    return -0.5 * z * z - np.log(sigma) - 0.5 * np.log(2.0 * np.pi)


def TARGET_BIMODAL(x):
    """Densita' target di esempio, BIMODALE e NON NORMALIZZATA.

        p~(x) = exp(-0.5 * (x + 2)^2) + 0.6 * exp(-0.5 * ((x - 3) / 0.8)^2)

    Mancano tutte le costanti 1/(sigma*sqrt(2*pi)): l'integrale non fa 1.
    E' esattamente la situazione tipica (posterior nota a meno di Z).

    Parametri
    ---------
    x : array_like

    Ritorna
    -------
    ndarray, valori >= 0, stessa shape di ``x``.
    """
    x = np.asarray(x, dtype=float)
    return np.exp(-0.5 * ((x + 2.0) / 1.0) ** 2) + 0.6 * np.exp(
        -0.5 * ((x - 3.0) / 0.8) ** 2
    )


def _quadrature_reference(lo=-25.0, hi=25.0, n_grid=400001):
    """Costante di normalizzazione, media e varianza di TARGET_BIMODAL per quadratura.

    Regola dei trapezi su una griglia fittissima: e' l'oracolo "esatto" contro
    cui si misurano gli stimatori Monte Carlo.

    Ritorna
    -------
    (Z, mu, var) : tuple di float
    """
    grid = np.linspace(lo, hi, n_grid)
    p = TARGET_BIMODAL(grid)
    Z = float(np.trapezoid(p, grid))
    mu = float(np.trapezoid(grid * p, grid) / Z)
    var = float(np.trapezoid((grid - mu) ** 2 * p, grid) / Z)
    return Z, mu, var


Z_TRUE, MU_TRUE, VAR_TRUE = _quadrature_reference()
"""Riferimenti deterministici per TARGET_BIMODAL (calcolati per quadratura)."""


# ---------------------------------------------------------------------------
# 1. Inverse transform sampling
# ---------------------------------------------------------------------------


def inverse_transform_sample(inv_cdf, n, rng):
    """Campiona per trasformazione inversa della CDF.

    Se U ~ Uniform(0, 1) e F e' la CDF di una v.a. X, allora F^{-1}(U) ~ X.

    Parametri
    ---------
    inv_cdf : callable
        ``inv_cdf(u) -> ndarray``, con ``u`` ndarray di shape (n,) e valori in
        [0, 1). Deve essere vettorizzata.
    n : int
        numero di campioni.
    rng : numpy.random.Generator

    Ritorna
    -------
    ndarray, shape (n,), dtype float.
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 2. Rejection sampling
# ---------------------------------------------------------------------------


def rejection_sample(target_unnorm, proposal_sample, proposal_pdf, M, n, rng):
    """Rejection sampling da una target non normalizzata.

    Serve una proposal q normalizzata e una costante M con
    ``M * q(x) >= p~(x)`` per ogni x. Si propone x ~ q, si estrae u ~ U(0,1) e
    si accetta se ``u * M * q(x) <= p~(x)``.

    Parametri
    ---------
    target_unnorm : callable
        ``target_unnorm(x) -> ndarray``, densita' target NON normalizzata p~,
        vettorizzata, valori >= 0.
    proposal_sample : callable
        ``proposal_sample(size, rng) -> ndarray`` di shape ``(size,)``.
    proposal_pdf : callable
        ``proposal_pdf(x) -> ndarray``, densita' della proposal NORMALIZZATA.
    M : float
        costante di dominanza (M * q >= p~ ovunque).
    n : int
        numero di campioni ACCETTATI da restituire.
    rng : numpy.random.Generator

    Ritorna
    -------
    samples : ndarray, shape (n,)
        campioni distribuiti secondo p~ / Z.
    acceptance_rate : float
        (numero di proposte accettate) / (numero di proposte generate), su tutte
        le proposte generate durante la chiamata.
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 3. Importance sampling
# ---------------------------------------------------------------------------


def importance_weights(samples, target_unnorm, proposal_pdf):
    """Pesi di importanza NON normalizzati: w_i = p~(x_i) / q(x_i).

    Parametri
    ---------
    samples : ndarray, shape (n,)
        campioni generati dalla proposal q.
    target_unnorm : callable, densita' target non normalizzata (vettorizzata).
    proposal_pdf : callable, densita' della proposal normalizzata (vettorizzata).

    Ritorna
    -------
    ndarray, shape (n,). NON sommano a 1: la normalizzazione e' a carico del
    chiamante (vedi ``self_normalized_importance_estimate``).
    """
    # TODO
    raise NotImplementedError


def self_normalized_importance_estimate(f, samples, target_unnorm, proposal_pdf):
    """Stima self-normalized di E_p[f(x)] con p = p~ / Z, Z incognita.

        E_p[f] ~= sum_i w_i f(x_i) / sum_i w_i,     w_i = p~(x_i) / q(x_i)

    La divisione per ``sum_i w_i`` stima implicitamente Z: per questo la stima
    e' invariante se si moltiplica ``target_unnorm`` per una costante.

    Parametri
    ---------
    f : callable, ``f(x) -> ndarray`` vettorizzata.
    samples : ndarray, shape (n,), campioni da q.
    target_unnorm, proposal_pdf : callable (vedi ``importance_weights``).

    Ritorna
    -------
    float
    """
    # TODO
    raise NotImplementedError


def effective_sample_size(weights):
    """Effective sample size dei pesi di importanza.

        ESS = (sum_i w_i)^2 / sum_i w_i^2

    Vale n se i pesi sono tutti uguali, 1 se un solo peso e' non nullo.
    Invariante per riscalamento dei pesi.

    Parametri
    ---------
    weights : array_like, shape (n,), valori >= 0.

    Ritorna
    -------
    float
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 4. Metropolis-Hastings (random walk gaussiano, in spazio log)
# ---------------------------------------------------------------------------


def metropolis_hastings(log_target, x0, n, proposal_std, rng):
    """MH con proposal random walk gaussiana SIMMETRICA, in spazio log.

    Proposta: ``y = x + proposal_std * z``, z ~ N(0, 1). Essendo
    ``q(y|x) = q(x|y)``, i termini di proposal si cancellano e il rapporto di
    accettazione si riduce a ``a = min(1, p~(y) / p~(x))``, che in log diventa
    ``log a = min(0, log p~(y) - log p~(x))``. Si accetta se
    ``log(u) < log p~(y) - log p~(x)`` con u ~ U(0, 1).

    Tutto in spazio log: le densita' target sono facilmente sotto/sovra-flow.
    La costante di normalizzazione di p si cancella nel rapporto, quindi
    ``log_target`` puo' essere la log-densita' NON normalizzata.

    Parametri
    ---------
    log_target : callable
        ``log_target(x) -> float`` con x scalare. Puo' valere -inf (stato
        impossibile): quello stato viene sempre rifiutato.
    x0 : float
        stato iniziale.
    n : int
        lunghezza della catena restituita, INCLUSO ``x0``. Quindi vengono
        proposti ``n - 1`` movimenti.
    proposal_std : float
        deviazione standard del random walk.
    rng : numpy.random.Generator

    Ritorna
    -------
    chain : ndarray, shape (n,), con ``chain[0] == x0``.
    acceptance_rate : float
        proposte accettate / (n - 1). Vale 0.0 se n <= 1.
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 5. Gibbs sampling (normale bivariata standard con correlazione rho)
# ---------------------------------------------------------------------------


def gibbs_bivariate_normal(rho, n, x0, rng):
    """Gibbs sampling esatto per N(0, [[1, rho], [rho, 1]]).

    Le condizionali complete di una normale bivariata standard sono

        x1 | x2 ~ N(rho * x2, 1 - rho^2)
        x2 | x1 ~ N(rho * x1, 1 - rho^2)

    Ogni riga della catena e' uno *sweep* completo: prima si aggiorna x1
    condizionatamente al valore corrente di x2, poi x2 condizionatamente al
    valore APPENA aggiornato di x1 (Gibbs sistematico, non Jacobi).

    Parametri
    ---------
    rho : float, |rho| < 1
    n : int, numero di stati restituiti, INCLUSO lo stato iniziale.
    x0 : array_like, shape (2,), stato iniziale.
    rng : numpy.random.Generator

    Ritorna
    -------
    ndarray, shape (n, 2), con ``chain[0] == x0``.
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 6. Diagnostica MCMC
# ---------------------------------------------------------------------------


def autocorrelation(chain, max_lag):
    """Autocorrelazione empirica di una catena scalare, da lag 0 a max_lag.

        c_k = (1/N) * sum_{t=0}^{N-k-1} (x_t - xbar) * (x_{t+k} - xbar)
        rho_k = c_k / c_0

    Convenzione: denominatore N per ogni lag (stimatore "biased" ma a varianza
    bassa, quello standard in MCMC). Per costruzione ``rho_0 == 1``.

    Parametri
    ---------
    chain : array_like, shape (N,) (o (N, 1): viene appiattita).
    max_lag : int, 0 <= max_lag < N.

    Ritorna
    -------
    ndarray, shape (max_lag + 1,), con ``out[0] == 1.0``.
    """
    # TODO
    raise NotImplementedError


def mcmc_effective_sample_size(chain, max_lag=50):
    """ESS di una catena MCMC via tempo di autocorrelazione integrato.

        tau = 1 + 2 * sum_{k=1}^{K} rho_k        (initial positive sequence)
        ESS = N / tau

    La somma viene troncata al primo lag con ``rho_k <= 0`` (oltre quel punto
    le autocorrelazioni sono rumore e sommarle gonfia la varianza dello
    stimatore), e comunque a ``max_lag``.

    Il risultato viene limitato all'intervallo [1, N].

    Parametri
    ---------
    chain : array_like, shape (N,).
    max_lag : int, lag massimo considerato.

    Ritorna
    -------
    float
    """
    # TODO
    raise NotImplementedError
