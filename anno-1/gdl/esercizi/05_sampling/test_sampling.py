"""Test di autovalutazione - GDL13 "Sampling methods and approximations".

Esecuzione:
    pytest test_sampling.py -v                # sullo skeleton
    GDL_SOL=1 pytest test_sampling.py -v      # sulla soluzione di riferimento
"""

import os, sys, pathlib, importlib

HERE = pathlib.Path(__file__).parent
if os.environ.get("GDL_SOL"):
    sys.path.insert(0, str(HERE / "soluzione"))
    m = importlib.import_module("sampling_sol")
else:
    sys.path.insert(0, str(HERE))
    m = importlib.import_module("sampling")

import numpy as np
from numpy.testing import assert_allclose


# ---------------------------------------------------------------------------
# helper locali ai test (non fanno parte dell'API da implementare)
# ---------------------------------------------------------------------------

def _log_std_normal(x):
    """log-densita' NON normalizzata di N(0, 1): la costante si cancella in MH."""
    return -0.5 * float(x) * float(x)


def _biv_normal_unnorm(x1, x2, rho):
    """Densita' congiunta NON normalizzata di N(0, [[1, rho], [rho, 1]])."""
    q = (x1 * x1 - 2.0 * rho * x1 * x2 + x2 * x2) / (1.0 - rho * rho)
    return np.exp(-0.5 * q)


# ---------------------------------------------------------------------------
# 1. Inverse transform sampling
# ---------------------------------------------------------------------------

def test_inverse_transform_riproduce_la_cdf():
    """F^{-1}(U) deve avere ESATTAMENTE la CDF F: lo verifichiamo con la
    statistica di Kolmogorov-Smirnov contro la CDF teorica."""
    lam = 1.5
    rng = np.random.default_rng(20240101)
    n = 50000
    x = m.inverse_transform_sample(lambda u: -np.log1p(-u) / lam, n, rng)

    assert x.shape == (n,), f"shape attesa ({n},), ottenuta {x.shape}"
    assert np.all(x >= 0.0), "una Exp(lambda) non puo' produrre valori negativi"

    xs = np.sort(x)
    ecdf = (np.arange(1, n + 1)) / n
    cdf = 1.0 - np.exp(-lam * xs)
    ks = float(np.max(np.abs(ecdf - cdf)))
    # soglia KS al 99% circa: 1.63 / sqrt(n)
    assert ks < 1.63 / np.sqrt(n), (
        f"la CDF empirica dista {ks:.5f} da quella teorica: la trasformazione "
        "inversa non sta mappando uniformi su F^-1 (o non usa rng.random)"
    )
    assert_allclose(x.mean(), 1.0 / lam, atol=0.02,
                    err_msg="media campionaria incompatibile con Exp(1.5)")


# ---------------------------------------------------------------------------
# 2. Rejection sampling
# ---------------------------------------------------------------------------

def test_rejection_media_e_varianza_corrette():
    """(a) target gaussiana, proposal gaussiana piu' larga: i campioni accettati
    devono avere media 0 e varianza 1."""
    rng = np.random.default_rng(20240202)
    target = lambda x: m.normal_pdf(x, 0.0, 1.0)
    prop_pdf = lambda x: m.normal_pdf(x, 0.0, 2.0)
    prop_sample = lambda size, r: r.normal(0.0, 2.0, size=size)
    # sup_x p(x)/q(x) = 2 (raggiunto in x = 0), quindi M = 2 e' valida.
    n = 200000
    s, acc = m.rejection_sample(target, prop_sample, prop_pdf, 2.0, n, rng)

    assert s.shape == (n,), f"devono essere restituiti esattamente n={n} campioni ACCETTATI, non {s.shape}"
    assert_allclose(s.mean(), 0.0, atol=0.02,
                    err_msg="media dei campioni accettati != 0: la regola di accettazione e' sbagliata")
    assert_allclose(s.var(), 1.0, rtol=0.03,
                    err_msg="varianza dei campioni accettati != 1: probabilmente stai accettando "
                            "in base a q invece che al rapporto p~/(M q)")
    assert 0.0 < acc <= 1.0, f"acceptance rate fuori da (0, 1]: {acc}"


def test_rejection_acceptance_rate_e_uno_su_M():
    """(b) con p e q entrambe NORMALIZZATE, la probabilita' di accettazione vale
    esattamente 1/M, qualunque sia M valida. Caso in forma chiusa:
    p = N(0,1), q = N(0, s^2), sup p/q = s, quindi M = s e acc = 1/s."""
    s_prop = 1.6
    rng = np.random.default_rng(20240303)
    target = lambda x: m.normal_pdf(x, 0.0, 1.0)
    prop_pdf = lambda x: m.normal_pdf(x, 0.0, s_prop)
    prop_sample = lambda size, r: r.normal(0.0, s_prop, size=size)
    _, acc = m.rejection_sample(target, prop_sample, prop_pdf, s_prop, 200000, rng)
    assert_allclose(acc, 1.0 / s_prop, rtol=0.02,
                    err_msg=f"acceptance rate {acc:.4f} contro 1/M = {1.0/s_prop:.4f}: "
                            "o non conti TUTTE le proposte generate, o la soglia di "
                            "accettazione non e' u*M*q(x) <= p~(x)")

    # M piu' grande => proporzionalmente meno accettazioni (spreco di campioni).
    rng2 = np.random.default_rng(20240304)
    _, acc4 = m.rejection_sample(target, prop_sample, prop_pdf, 4.0 * s_prop, 100000, rng2)
    assert_allclose(acc4, 1.0 / (4.0 * s_prop), rtol=0.03,
                    err_msg="raddoppiando/quadruplicando M l'acceptance rate deve scalare come 1/M")


# ---------------------------------------------------------------------------
# 3. Importance sampling
# ---------------------------------------------------------------------------

def test_importance_weights_sono_non_normalizzati():
    """Proprieta' esatta: w_i * q(x_i) == p~(x_i). E i pesi NON sommano a 1."""
    rng = np.random.default_rng(20240404)
    x = rng.normal(0.0, 3.5, size=2000)
    q = lambda z: m.normal_pdf(z, 0.0, 3.5)
    w = m.importance_weights(x, m.TARGET_BIMODAL, q)

    assert w.shape == x.shape, f"i pesi devono avere shape {x.shape}, non {w.shape}"
    assert_allclose(w * q(x), m.TARGET_BIMODAL(x), rtol=1e-9, atol=1e-12,
                    err_msg="w_i deve essere p~(x_i)/q(x_i): il prodotto w_i*q(x_i) "
                            "deve restituire la target non normalizzata")
    assert abs(float(w.sum()) - 1.0) > 1e-6, (
        "importance_weights deve restituire i pesi GREZZI, non normalizzati: qui "
        f"la somma vale {w.sum():.4f} e non deve essere forzata a 1"
    )


def test_self_normalized_recupera_i_momenti_della_bimodale():
    """(c) la stima self-normalized deve recuperare media e varianza della
    bimodale calcolate per quadratura, senza mai conoscere Z."""
    rng = np.random.default_rng(20240505)
    n = 200000
    x = rng.normal(0.0, 3.5, size=n)
    q = lambda z: m.normal_pdf(z, 0.0, 3.5)

    mu_hat = m.self_normalized_importance_estimate(lambda z: z, x, m.TARGET_BIMODAL, q)
    assert_allclose(mu_hat, m.MU_TRUE, atol=0.03,
                    err_msg=f"media stimata {mu_hat:.4f} contro quadratura {m.MU_TRUE:.4f}: "
                            "manca la divisione per sum(w) (o stai dividendo per n)")

    var_hat = m.self_normalized_importance_estimate(
        lambda z: (z - m.MU_TRUE) ** 2, x, m.TARGET_BIMODAL, q)
    assert_allclose(var_hat, m.VAR_TRUE, rtol=0.03,
                    err_msg=f"varianza stimata {var_hat:.4f} contro quadratura {m.VAR_TRUE:.4f}")

    # Proprieta': la stima e' invariante se p~ viene riscalata di una costante.
    scaled = lambda z: 137.0 * m.TARGET_BIMODAL(z)
    mu_scaled = m.self_normalized_importance_estimate(lambda z: z, x, scaled, q)
    assert_allclose(mu_scaled, mu_hat, rtol=1e-9, atol=1e-12,
                    err_msg="la stima self-normalized deve essere invariante al riscalamento "
                            "di p~: e' proprio il motivo per cui si divide per sum(w)")


def test_effective_sample_size_casi_limite():
    """(d) casi degeneri: pesi tutti uguali -> ESS = n; un solo peso non nullo -> ESS = 1."""
    n = 37
    assert_allclose(m.effective_sample_size(np.ones(n)), float(n), rtol=1e-12,
                    err_msg="con pesi tutti uguali l'ESS deve valere esattamente n")
    assert_allclose(m.effective_sample_size(np.full(n, 0.017)), float(n), rtol=1e-12,
                    err_msg="l'ESS deve essere invariante al riscalamento dei pesi")

    degenere = np.zeros(n)
    degenere[9] = 5.0
    assert_allclose(m.effective_sample_size(degenere), 1.0, rtol=1e-12,
                    err_msg="se un solo peso e' non nullo tutta la massa e' su un campione: ESS = 1")

    misto = np.array([1.0, 1.0, 2.0, 4.0, 8.0])
    ess = m.effective_sample_size(misto)
    assert 1.0 <= ess <= misto.size, f"ESS deve stare in [1, n], ottenuto {ess}"
    assert_allclose(ess, misto.sum() ** 2 / (misto ** 2).sum(), rtol=1e-12,
                    err_msg="ESS = (sum w)^2 / sum(w^2)")


# ---------------------------------------------------------------------------
# 4. Metropolis-Hastings
# ---------------------------------------------------------------------------

def test_mh_campiona_la_gaussiana_standard():
    """(e) MH random walk su N(0,1): dopo il burn-in media ~ 0 e varianza ~ 1,
    con acceptance rate plausibile per proposal_std = 2.4."""
    rng = np.random.default_rng(20240606)
    n = 80000
    chain, acc = m.metropolis_hastings(_log_std_normal, 0.0, n, 2.4, rng)

    assert chain.shape == (n,), f"shape attesa ({n},), ottenuta {chain.shape}"
    assert_allclose(chain[0], 0.0, atol=0.0,
                    err_msg="chain[0] deve essere lo stato iniziale x0")

    burned = chain[5000:]
    assert_allclose(burned.mean(), 0.0, atol=0.05,
                    err_msg="media della catena != 0: la catena non sta campionando N(0,1)")
    assert_allclose(burned.var(), 1.0, atol=0.08,
                    err_msg="varianza della catena != 1: sospetta accettazione sempre vera "
                            "(varianza gonfiata) o rapporto invertito (varianza compressa)")
    assert 0.30 < acc < 0.60, (
        f"acceptance rate {acc:.3f} implausibile: per un random walk gaussiano su N(0,1) "
        "con proposal_std = 2.4 ci si aspetta circa 0.44"
    )

    # la catena si muove: non e' bloccata sullo stato iniziale
    assert np.unique(burned).size > n // 10, "la catena e' quasi sempre ferma: nulla viene accettato"


def test_mh_lascia_invariata_la_target():
    """(f) INVARIANZA: se lo stato di partenza e' gia' distribuito come la target,
    dopo un passo di MH la distribuzione deve essere ancora quella.
    Confronto sui primi quattro momenti di N(0,1): 0, 1, 0, 3."""
    rng = np.random.default_rng(20240707)
    n_chains = 60000
    x0 = rng.standard_normal(n_chains)  # gia' ~ N(0,1) = target

    dopo = np.empty(n_chains)
    for i in range(n_chains):
        chain, _ = m.metropolis_hastings(_log_std_normal, float(x0[i]), 2, 0.9, rng)
        dopo[i] = chain[-1]

    assert_allclose(dopo.mean(), 0.0, atol=0.03,
                    err_msg="dopo un passo di MH la media non e' piu' 0: la catena non e' invariante")
    assert_allclose(dopo.var(), 1.0, atol=0.06,
                    err_msg="dopo un passo di MH la varianza si e' spostata da 1: se e' cresciuta "
                            "verso 1 + proposal_std^2 stai accettando SEMPRE (manca il test di "
                            "Metropolis); se e' calata stai usando il rapporto invertito")
    assert_allclose((dopo ** 4).mean(), 3.0, atol=0.30,
                    err_msg="il momento quarto si e' spostato da 3: la distribuzione invariante "
                            "della catena non e' N(0,1)")


# ---------------------------------------------------------------------------
# 5. Gibbs sampling
# ---------------------------------------------------------------------------

def test_gibbs_recupera_rho():
    """(g) la catena di Gibbs deve riprodurre la correlazione rho della bivariata,
    e marginali standard."""
    rho = 0.8
    rng = np.random.default_rng(20240808)
    n = 60000
    chain = m.gibbs_bivariate_normal(rho, n, [4.0, -4.0], rng)

    assert chain.shape == (n, 2), f"shape attesa ({n}, 2), ottenuta {chain.shape}"
    assert_allclose(chain[0], [4.0, -4.0], atol=0.0,
                    err_msg="chain[0] deve essere lo stato iniziale x0")

    b = chain[1000:]
    corr = float(np.corrcoef(b[:, 0], b[:, 1])[0, 1])
    assert_allclose(corr, rho, atol=0.02,
                    err_msg=f"correlazione empirica {corr:.4f} contro rho = {rho}: controlla che "
                            "la condizionale sia N(rho*x_altro, 1 - rho^2) e che l'aggiornamento "
                            "di x2 usi il valore GIA' aggiornato di x1")
    assert_allclose(b.mean(axis=0), [0.0, 0.0], atol=0.05,
                    err_msg="le marginali devono avere media 0")
    assert_allclose(b.var(axis=0), [1.0, 1.0], atol=0.06,
                    err_msg="le marginali devono avere varianza 1: se ottieni 1 - rho^2 stai "
                            "dimenticando che la condizionale ha varianza ridotta ma la marginale no")

    # caso limite rho = 0: le due componenti sono indipendenti
    rng0 = np.random.default_rng(20240809)
    c0 = m.gibbs_bivariate_normal(0.0, 40000, [0.0, 0.0], rng0)
    assert abs(float(np.corrcoef(c0[1:, 0], c0[1:, 1])[0, 1])) < 0.02, \
        "con rho = 0 le componenti devono risultare scorrelate"


def test_gibbs_e_metropolis_hastings_con_ratio_uno():
    """(h) TEST CHIAVE: Gibbs E' Metropolis-Hastings.

    Se la proposal di MH e' la condizionale completa p(x_i | x_{-i}), il rapporto
    di accettazione

        a = [ p~(x') q(x | x') ] / [ p~(x) q(x' | x) ]

    vale IDENTICAMENTE 1, perche' p~(x') = p(x'_i | x_{-i}) * p(x_{-i}) * Z e
    q(x | x') = p(x_i | x_{-i}): numeratore e denominatore contengono gli stessi
    quattro fattori. Quindi Gibbs non rifiuta mai.
    """
    rho = 0.7
    var_c = 1.0 - rho * rho          # varianza della condizionale completa
    sd_c = np.sqrt(var_c)
    rng = np.random.default_rng(20240909)

    # i punti in cui valutiamo il rapporto sono stati veri della catena di Gibbs
    chain = m.gibbs_bivariate_normal(rho, 300, [2.0, -1.0], rng)
    pts = chain[50::10]
    assert pts.shape[0] >= 20

    ratios = []
    for a, b in pts:
        # --- aggiornamento della coordinata 0: x = (a, b) -> x' = (a', b)
        a_new = float(rng.normal(rho * b, sd_c))     # proposta = condizionale completa
        num = _biv_normal_unnorm(a_new, b, rho) * m.normal_pdf(a, rho * b, sd_c)
        den = _biv_normal_unnorm(a, b, rho) * m.normal_pdf(a_new, rho * b, sd_c)
        ratios.append(num / den)

        # --- aggiornamento della coordinata 1: x = (a, b) -> x' = (a, b')
        b_new = float(rng.normal(rho * a, sd_c))
        num = _biv_normal_unnorm(a, b_new, rho) * m.normal_pdf(b, rho * a, sd_c)
        den = _biv_normal_unnorm(a, b, rho) * m.normal_pdf(b_new, rho * a, sd_c)
        ratios.append(num / den)

    ratios = np.asarray(ratios, dtype=float)
    assert_allclose(ratios, 1.0, rtol=1e-10, atol=1e-12,
                    err_msg="il rapporto di accettazione di MH con proposal = condizionale "
                            "completa deve valere esattamente 1 in OGNI punto: Gibbs e' un MH "
                            "che accetta sempre")

    # controprova: con una proposal che NON e' la condizionale completa il
    # rapporto smette di valere 1 (il test qui sopra non e' una tautologia).
    sbagliati = []
    for a, b in pts[:20]:
        a_new = float(rng.normal(0.0, 1.0))          # proposal indipendente N(0,1)
        num = _biv_normal_unnorm(a_new, b, rho) * m.normal_pdf(a, 0.0, 1.0)
        den = _biv_normal_unnorm(a, b, rho) * m.normal_pdf(a_new, 0.0, 1.0)
        sbagliati.append(num / den)
    sbagliati = np.asarray(sbagliati)
    assert np.max(np.abs(sbagliati - 1.0)) > 0.05, \
        "con una proposal diversa dalla condizionale completa il rapporto non deve valere 1"


# ---------------------------------------------------------------------------
# 6. Diagnostica MCMC
# ---------------------------------------------------------------------------

def test_autocorrelation_lag0_e_oracolo_forza_bruta():
    """(i) rho_0 = 1 per definizione; e il resto va confrontato con un oracolo
    indipendente calcolato a doppio ciclo dalla definizione."""
    rng = np.random.default_rng(20241010)
    # AR(1): x_t = phi x_{t-1} + eps  ->  autocorrelazione teorica phi^k
    phi = 0.75
    N = 4000
    eps = rng.standard_normal(N)
    x = np.empty(N)
    x[0] = eps[0]
    for t in range(1, N):
        x[t] = phi * x[t - 1] + eps[t]

    max_lag = 12
    ac = m.autocorrelation(x, max_lag)
    assert ac.shape == (max_lag + 1,), f"shape attesa ({max_lag+1},), ottenuta {ac.shape}"
    assert_allclose(ac[0], 1.0, rtol=1e-12,
                    err_msg="l'autocorrelazione a lag 0 vale 1 per definizione (c_0/c_0)")

    # oracolo: definizione, doppio ciclo Python, denominatore N per ogni lag
    xbar = float(np.sum(x) / N)
    c = []
    for k in range(max_lag + 1):
        acc = 0.0
        for t in range(N - k):
            acc += (x[t] - xbar) * (x[t + k] - xbar)
        c.append(acc / N)
    oracolo = np.array(c) / c[0]
    assert_allclose(ac, oracolo, rtol=1e-8, atol=1e-10,
                    err_msg="l'autocorrelazione non coincide con la definizione calcolata a mano "
                            "(attenzione al denominatore: N per ogni lag, non N-k)")

    # e il decadimento e' quello teorico di un AR(1)
    assert_allclose(ac[1], phi, atol=0.04,
                    err_msg="per un AR(1) con phi=0.75 l'autocorrelazione a lag 1 vale circa phi")
    assert np.all(np.diff(ac[:8]) < 0), "l'autocorrelazione di un AR(1) deve decadere monotonamente"


def test_mcmc_ess_distingue_iid_da_catena_correlata():
    """L'ESS di una catena MCMC deve crollare quando l'autocorrelazione e' alta,
    e valere quasi N per campioni indipendenti."""
    rng = np.random.default_rng(20241111)
    N = 20000

    iid = rng.standard_normal(N)
    ess_iid = m.mcmc_effective_sample_size(iid, max_lag=50)
    assert 0.8 * N <= ess_iid <= N, (
        f"per campioni i.i.d. l'ESS deve essere ~ N = {N}, ottenuto {ess_iid:.0f}"
    )

    # Gibbs con rho = 0.95: autocorrelazione per sweep ~ rho^2 = 0.9025,
    # tempo integrato ~ (1+0.9025)/(1-0.9025) ~ 19.5
    chain = m.gibbs_bivariate_normal(0.95, N, [0.0, 0.0], rng)
    ess_mcmc = m.mcmc_effective_sample_size(chain[:, 0], max_lag=50)
    assert 1.0 <= ess_mcmc <= N, f"l'ESS deve stare in [1, N], ottenuto {ess_mcmc}"
    assert ess_mcmc < 0.15 * N, (
        f"l'ESS di una catena fortemente correlata deve essere molto minore di N: "
        f"ottenuto {ess_mcmc:.0f} su {N} (stai forse ignorando le autocorrelazioni?)"
    )
    assert ess_mcmc > 0.01 * N, f"ESS troppo piccolo, {ess_mcmc:.0f}: la somma delle rho_k e' esplosa"
    assert ess_iid > 5.0 * ess_mcmc, (
        "N campioni i.i.d. devono valere molto piu' di N stati di una catena correlata"
    )
