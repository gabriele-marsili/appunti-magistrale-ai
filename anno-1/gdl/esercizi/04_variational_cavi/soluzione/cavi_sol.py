"""
Soluzione di riferimento — CAVI per una mixture di gaussiane univariate
a varianza nota (modello canonico di Blei et al., "Variational Inference:
A Review for Statisticians", sezione 3).

Modello generativo
    mu_k        ~ N(0, sigma0^2)          k = 1..K
    c_i         ~ Cat(1/K, ..., 1/K)      i = 1..N
    x_i | c_i=k ~ N(mu_k, 1)

Famiglia variazionale mean-field
    q(mu, c) = prod_k N(mu_k; m_k, s2_k) * prod_i Cat(c_i; phi_i)

Solo numpy. Determinismo via np.random.default_rng(seed).
"""

import numpy as np

LOG_2PI = float(np.log(2.0 * np.pi))


# ---------------------------------------------------------------------------
# Codice fornito nello skeleton (NON parte dell'esercizio)
# ---------------------------------------------------------------------------

def _lognorm(x, mu, var):
    """Log-densita' gaussiana, uso interno.

    Volutamente DUPLICATA rispetto a `log_norm_pdf`: gli helper "oracolo"
    (`elbo_monte_carlo`, `make_mixture_data`) non devono dipendere dal codice
    dello studente, altrimenti un errore si cancellerebbe da solo.
    """
    return -0.5 * (LOG_2PI + np.log(var) + (x - mu) ** 2 / var)


def make_mixture_data(N, K, true_means=None, seed=0):
    """Genera un dataset dalla mixture di gaussiane univariate.

    Parametri
    ---------
    N : int
        Numero di osservazioni.
    K : int
        Numero di componenti.
    true_means : array_like shape (K,) oppure None
        Medie vere delle componenti. Se None, usa K medie equispaziate di
        passo 5 centrate in 0.
    seed : int
        Seed per np.random.default_rng.

    Ritorna
    -------
    x : ndarray shape (N,)
        Osservazioni.
    c : ndarray shape (N,) dtype int
        Assegnazioni vere (etichette in 0..K-1), utili solo per la diagnostica.
    """
    rng = np.random.default_rng(seed)
    if true_means is None:
        true_means = 5.0 * (np.arange(K) - (K - 1) / 2.0)
    true_means = np.asarray(true_means, dtype=float)
    assert true_means.shape == (K,), "true_means deve avere shape (K,)"
    c = rng.integers(0, K, size=N)
    x = true_means[c] + rng.standard_normal(N)
    return x, c


def elbo_monte_carlo(x, phi, m, s2, sigma0_sq, n_samples, rng):
    """Stima Monte Carlo dell'ELBO. FORNITA: serve da oracolo indipendente.

    Campiona S volte (mu, c) ~ q e media log p(x, c, mu) - log q(mu, c).
    Non usa nessuna delle funzioni che devi implementare.

    Parametri
    ---------
    x : ndarray shape (N,)
    phi : ndarray shape (N, K), righe normalizzate
    m, s2 : ndarray shape (K,)
    sigma0_sq : float
    n_samples : int
    rng : np.random.Generator

    Ritorna
    -------
    float
        Stima dell'ELBO. L'errore standard scala come 1/sqrt(n_samples).
    """
    x = np.asarray(x, dtype=float)
    phi = np.asarray(phi, dtype=float)
    m = np.asarray(m, dtype=float)
    s2 = np.asarray(s2, dtype=float)
    N = x.shape[0]
    K = m.shape[0]

    # mu ~ q(mu): (S, K)
    mu_s = m[None, :] + np.sqrt(s2)[None, :] * rng.standard_normal((n_samples, K))

    # c ~ q(c): (S, N), campionamento per inversione della CDF riga per riga
    cdf = np.cumsum(phi, axis=1)
    u = rng.random((n_samples, N))
    c = np.empty((n_samples, N), dtype=np.int64)
    for i in range(N):
        c[:, i] = np.clip(np.searchsorted(cdf[i], u[:, i], side="right"), 0, K - 1)

    rows = np.arange(n_samples)[:, None]
    mu_sel = mu_s[rows, c]                      # (S, N): mu della componente scelta

    log_p = (_lognorm(mu_s, 0.0, sigma0_sq).sum(axis=1)      # log p(mu)
             - N * np.log(K)                                  # log p(c)
             + _lognorm(x[None, :], mu_sel, 1.0).sum(axis=1))  # log p(x | c, mu)
    log_q = (_lognorm(mu_s, m[None, :], s2[None, :]).sum(axis=1)
             + np.log(np.maximum(phi[np.arange(N)[None, :], c], 1e-300)).sum(axis=1))
    return float(np.mean(log_p - log_q))


# ---------------------------------------------------------------------------
# Da implementare
# ---------------------------------------------------------------------------

def log_norm_pdf(x, mu, var):
    """Log-densita' di una gaussiana univariata, vettorizzata.

    log N(x; mu, var) = -0.5 * (log(2*pi) + log(var) + (x - mu)^2 / var)

    Parametri
    ---------
    x, mu, var : array_like
        Broadcastabili fra loro. `var` > 0.

    Ritorna
    -------
    ndarray
        Shape data dal broadcasting di x, mu, var.
    """
    x = np.asarray(x, dtype=float)
    mu = np.asarray(mu, dtype=float)
    var = np.asarray(var, dtype=float)
    return -0.5 * (LOG_2PI + np.log(var) + (x - mu) ** 2 / var)


def elbo(x, phi, m, s2, sigma0_sq):
    """ELBO analitico del modello, per un q mean-field qualsiasi.

    ELBO(q) = E_q[log p(mu)] + E_q[log p(c)] + E_q[log p(x | c, mu)]
              + H[q(mu)] + H[q(c)]

    con, usando E[mu_k] = m_k ed E[mu_k^2] = m_k^2 + s2_k:

      E_q[log p(mu)]       = sum_k [ -0.5*log(2*pi*sigma0^2)
                                     - (m_k^2 + s2_k) / (2*sigma0^2) ]
      E_q[log p(c)]        = sum_i sum_k phi_ik * log(1/K)
      E_q[log p(x|c,mu)]   = sum_i sum_k phi_ik * [ -0.5*log(2*pi)
                              - 0.5*(x_i^2 - 2*x_i*m_k + m_k^2 + s2_k) ]
      H[q(mu)]             = sum_k 0.5*(log(2*pi*s2_k) + 1)
      H[q(c)]              = - sum_i sum_k phi_ik * log phi_ik

    Nessun campionamento: e' una formula chiusa.

    Parametri
    ---------
    x : ndarray shape (N,)
    phi : ndarray shape (N, K)
        Righe normalizzate. Sono ammessi zeri esatti (0*log 0 := 0).
    m, s2 : ndarray shape (K,)
        Medie e varianze di q(mu_k). s2 > 0.
    sigma0_sq : float
        Varianza del prior sulle medie.

    Ritorna
    -------
    float
    """
    x = np.asarray(x, dtype=float)
    phi = np.asarray(phi, dtype=float)
    m = np.asarray(m, dtype=float)
    s2 = np.asarray(s2, dtype=float)
    K = m.shape[0]

    # Momenti primo e secondo di q(mu_k). Il secondo momento e' il punto in cui
    # si sbaglia piu' spesso: NON e' m_k^2, e' m_k^2 + s2_k.
    e_mu = m
    e_mu2 = m ** 2 + s2

    # E_q[log p(mu)]
    t_prior = np.sum(-0.5 * (LOG_2PI + np.log(sigma0_sq)) - e_mu2 / (2.0 * sigma0_sq))

    # E_q[log p(c)]; scritto come somma su phi cosi' resta corretto anche se le
    # righe non sommassero esattamente a 1 per errore numerico.
    t_c = -np.log(K) * np.sum(phi)

    # E_q[log p(x | c, mu)]
    e_loglik = -0.5 * (LOG_2PI
                       + x[:, None] ** 2
                       - 2.0 * x[:, None] * e_mu[None, :]
                       + e_mu2[None, :])
    t_lik = np.sum(phi * e_loglik)

    # H[q(mu)] : entropia di una gaussiana
    t_ent_mu = np.sum(0.5 * (np.log(2.0 * np.pi * s2) + 1.0))

    # H[q(c)] : entropia di categoriche, con la convenzione 0*log 0 = 0
    safe = np.where(phi > 0.0, phi, 1.0)
    t_ent_c = -np.sum(phi * np.log(safe))

    return float(t_prior + t_c + t_lik + t_ent_mu + t_ent_c)


def update_phi(x, m, s2):
    """Aggiornamento coordinato di q(c), tenendo (m, s2) fissi.

    La regola generica del mean-field e'
        log q*(c_i) = E_{q(-c_i)}[ log p(x, c, mu) ] + const
    che qui da'
        phi_ik  propto  exp( E[mu_k] * x_i - 0.5 * E[mu_k^2] )
                =       exp( m_k * x_i - 0.5 * (m_k^2 + s2_k) )
    (il termine -0.5*x_i^2, il log(1/K) e il -0.5*log(2*pi) non dipendono da k
    e spariscono nella normalizzazione).

    Parametri
    ---------
    x : ndarray shape (N,)
    m, s2 : ndarray shape (K,)

    Ritorna
    -------
    phi : ndarray shape (N, K)
        Ogni riga somma a 1.
    """
    x = np.asarray(x, dtype=float)
    m = np.asarray(m, dtype=float)
    s2 = np.asarray(s2, dtype=float)

    logits = x[:, None] * m[None, :] - 0.5 * (m ** 2 + s2)[None, :]
    # log-sum-exp trick: senza, con x grandi si va in overflow.
    logits = logits - logits.max(axis=1, keepdims=True)
    p = np.exp(logits)
    return p / p.sum(axis=1, keepdims=True)


def update_mu(x, phi, sigma0_sq):
    """Aggiornamento coordinato di q(mu), tenendo phi fisso.

    q*(mu_k) resta gaussiana (coniugazione), con precisione data dalla somma
    della precisione del prior e delle responsabilita':

        1/s2_k = 1/sigma0^2 + sum_i phi_ik
        m_k    = ( sum_i phi_ik * x_i ) / ( 1/sigma0^2 + sum_i phi_ik )

    Parametri
    ---------
    x : ndarray shape (N,)
    phi : ndarray shape (N, K)
    sigma0_sq : float

    Ritorna
    -------
    m : ndarray shape (K,)
    s2 : ndarray shape (K,)
    """
    x = np.asarray(x, dtype=float)
    phi = np.asarray(phi, dtype=float)

    n_k = phi.sum(axis=0)                    # responsabilita' totali per componente
    prec = 1.0 / sigma0_sq + n_k             # precisione a posteriori
    s2 = 1.0 / prec
    m = (phi * x[:, None]).sum(axis=0) / prec
    return m, s2


def cavi(x, K, sigma0_sq=10.0, n_iter=200, tol=1e-8, seed=0):
    """Coordinate Ascent Variational Inference.

    Inizializzazione (FISSATA, non modificarla: i test ci contano):
        rng = np.random.default_rng(seed)
        idx = rng.choice(N, size=K, replace=(N < K))
        m   = x[idx].copy()
        s2  = np.ones(K)
    Poi, a ogni iterazione: prima `update_phi`, poi `update_mu`, infine si
    registra l'ELBO. Stop quando |ELBO_t - ELBO_{t-1}| < tol.

    Parametri
    ---------
    x : ndarray shape (N,)
    K : int
    sigma0_sq : float
    n_iter : int
        Numero massimo di iterazioni.
    tol : float
        Soglia di convergenza sulla variazione assoluta dell'ELBO.
    seed : int

    Ritorna
    -------
    dict con chiavi
        "m"            : ndarray (K,)
        "s2"           : ndarray (K,)
        "phi"          : ndarray (N, K)
        "elbo_history" : ndarray (T,), un valore per iterazione eseguita
        "n_iter"       : int, T (numero di iterazioni effettivamente eseguite)
    """
    x = np.asarray(x, dtype=float)
    N = x.shape[0]
    rng = np.random.default_rng(seed)

    # Init: K punti dati come medie iniziali. Piu' robusto che campionare dal
    # prior, perche' parte gia' nel supporto dei dati.
    idx = rng.choice(N, size=K, replace=(N < K))
    m = x[idx].copy()
    s2 = np.ones(K)
    phi = np.full((N, K), 1.0 / K)

    history = []
    prev = -np.inf
    for _ in range(n_iter):
        phi = update_phi(x, m, s2)           # ottimo esatto in phi dato (m, s2)
        m, s2 = update_mu(x, phi, sigma0_sq)  # ottimo esatto in (m, s2) dato phi
        val = elbo(x, phi, m, s2, sigma0_sq)
        history.append(val)
        if abs(val - prev) < tol:
            break
        prev = val

    return {
        "m": m,
        "s2": s2,
        "phi": phi,
        "elbo_history": np.asarray(history, dtype=float),
        "n_iter": len(history),
    }


def kl_gaussians(m1, v1, m2, v2):
    """KL( N(m1, v1) || N(m2, v2) ) in forma chiusa, caso univariato.

        KL = 0.5 * ( log(v2/v1) + (v1 + (m1 - m2)^2)/v2 - 1 )

    Attenzione all'ordine: e' E_{p1}[log p1 - log p2], NON simmetrica.

    Parametri
    ---------
    m1, v1 : float
        Media e varianza della distribuzione su cui si prende l'aspettazione.
    m2, v2 : float
        Media e varianza della distribuzione di riferimento.

    Ritorna
    -------
    float
        Sempre >= 0, con uguaglianza sse (m1, v1) == (m2, v2).
    """
    return float(0.5 * (np.log(v2 / v1) + (v1 + (m1 - m2) ** 2) / v2 - 1.0))


def log_marginal_bound_gap(x, phi, m, s2, sigma0_sq, log_evidence):
    """Gap fra log-evidenza e ELBO, cioe' KL( q || p(mu, c | x) ).

    Da log p(x) = ELBO(q) + KL(q || p(. | x)) segue

        gap = log p(x) - ELBO(q) = KL( q || posterior ) >= 0

    Il gap e' zero solo se q coincide con la posterior esatta.

    Parametri
    ---------
    x : ndarray shape (N,)
    phi : ndarray shape (N, K)
    m, s2 : ndarray shape (K,)
    sigma0_sq : float
    log_evidence : float
        log p(x) calcolata esattamente per altra via.

    Ritorna
    -------
    float
        Non negativo (a meno dell'errore di arrotondamento).
    """
    return float(log_evidence - elbo(x, phi, m, s2, sigma0_sq))
