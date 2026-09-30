"""Test di autovalutazione - GDL24 "Variational Autoencoders".

Esecuzione:
    pytest test_vae_elbo.py -v                # sullo skeleton
    GDL_SOL=1 pytest test_vae_elbo.py -v      # sulla soluzione di riferimento
"""

import os, sys, pathlib, importlib

HERE = pathlib.Path(__file__).parent
if os.environ.get("GDL_SOL"):
    sys.path.insert(0, str(HERE / "soluzione"))
    m = importlib.import_module("vae_elbo_sol")
else:
    sys.path.insert(0, str(HERE))
    m = importlib.import_module("vae_elbo")

import math
import numpy as np
from numpy.testing import assert_allclose


# ---------------------------------------------------------------------------
# helper locali ai test (non fanno parte dell'API da implementare)
# ---------------------------------------------------------------------------

def _log_normal_std_param(x, mean, std):
    """log-densita' gaussiana diagonale scritta con la DEVIAZIONE STANDARD.

    Percorso di calcolo diverso da quello richiesto allo studente (che riceve la
    log-varianza): serve a controllare che il fattore 0.5 sia al posto giusto.
    """
    x = np.asarray(x, dtype=float)
    z = (x - mean) / std
    return np.sum(-0.5 * z * z - np.log(std) - 0.5 * np.log(2.0 * np.pi), axis=-1)


def _kl_gauss_gauss(m1, v1, m2, v2):
    """KL( N(m1, v1) || N(m2, v2) ) scalare, in forma chiusa."""
    return 0.5 * (np.log(v2 / v1) + (v1 + (m1 - m2) ** 2) / v2 - 1.0)


def _sum_squares(z):
    """f(z) = sum_d z_d^2 : (S, D) -> (S,)."""
    return np.sum(np.asarray(z) ** 2, axis=-1)


def _grad_sum_squares(z):
    """gradiente di _sum_squares rispetto a z : (S, D) -> (S, D)."""
    return 2.0 * np.asarray(z)


# ---------------------------------------------------------------------------
# 1. gaussian_log_prob
# ---------------------------------------------------------------------------

def test_gaussian_log_prob_normalizzata_per_quadratura():
    """(a) PROPRIETA': exp(gaussian_log_prob) deve integrare a 1.

    In 1D e in 2D, per quadratura. E' il controllo che prende tutti gli errori
    sulla costante di normalizzazione: log_var scambiato con log_std, log(2 pi)
    contato una volta sola invece che per ogni dimensione, 0.5 mancante.
    """
    # --- 1D
    mu, lv = 0.7, -0.4
    sd = math.exp(0.5 * lv)
    grid = np.linspace(mu - 14.0 * sd, mu + 14.0 * sd, 400001)
    lp = m.gaussian_log_prob(grid[:, None], np.array([mu]), np.array([lv]))
    assert lp.shape == grid.shape, (
        f"con x di shape (G, 1) l'uscita deve avere shape (G,), ottenuta {lp.shape}: "
        "l'ultimo asse (le dimensioni latenti) va SOMMATO via"
    )
    mass = float(np.trapezoid(np.exp(lp), grid))
    assert_allclose(mass, 1.0, rtol=1e-8,
                    err_msg=f"la densita' 1D integra a {mass:.6f} invece che a 1: la costante di "
                            "normalizzazione e' sbagliata (ricorda che log_var e' il log della "
                            "VARIANZA, quindi log(std) = 0.5 * log_var)")

    # --- 2D: il termine log(2 pi) deve comparire una volta PER DIMENSIONE
    mu2 = np.array([0.3, -0.6])
    lv2 = np.array([0.2, -0.9])
    sd2 = np.exp(0.5 * lv2)
    g0 = np.linspace(mu2[0] - 9.0 * sd2[0], mu2[0] + 9.0 * sd2[0], 1201)
    g1 = np.linspace(mu2[1] - 9.0 * sd2[1], mu2[1] + 9.0 * sd2[1], 1201)
    G0, G1 = np.meshgrid(g0, g1, indexing="ij")
    pts = np.stack([G0, G1], axis=-1)                     # (1201, 1201, 2)
    dens = np.exp(m.gaussian_log_prob(pts, mu2, lv2))     # (1201, 1201)
    mass2 = float(np.trapezoid(np.trapezoid(dens, g1, axis=1), g0))
    assert_allclose(mass2, 1.0, rtol=1e-6,
                    err_msg=f"la densita' 2D integra a {mass2:.6f} invece che a 1: probabilmente "
                            "log(2 pi) e' sommato una volta sola invece che per ogni dimensione")


def test_gaussian_log_prob_valori_broadcast_e_fattorizzazione():
    """(b) valori esatti contro una parametrizzazione DIVERSA (deviazione
    standard), broadcasting dei parametri e fattorizzazione sulle dimensioni."""
    rng = np.random.default_rng(20240001)
    x = rng.normal(size=(5, 3))
    mean = np.array([0.4, -1.1, 2.0])
    log_var = np.array([0.0, 1.3862943611198906, -2.0])   # varianze 1, 4, exp(-2)

    got = m.gaussian_log_prob(x, mean, log_var)
    assert got.shape == (5,), f"shape attesa (5,), ottenuta {got.shape}"
    atteso = _log_normal_std_param(x, mean, np.exp(0.5 * log_var))
    assert_allclose(got, atteso, rtol=1e-9, atol=1e-12,
                    err_msg="i valori non coincidono con log N(x; mean, std) riscritta con la "
                            "deviazione standard: hai confuso log-varianza e log-deviazione "
                            "standard, oppure manca un fattore 0.5")

    # una gaussiana diagonale FATTORIZZA: la log-densita' congiunta e' la somma
    # delle log-densita' marginali, una per dimensione.
    per_dim = sum(
        m.gaussian_log_prob(x[:, d:d + 1], mean[d:d + 1], log_var[d:d + 1])
        for d in range(3)
    )
    assert_allclose(got, per_dim, rtol=1e-10, atol=1e-12,
                    err_msg="log N con covarianza diagonale deve essere la SOMMA delle "
                            "log-densita' per dimensione (non la media, non il prodotto)")

    # nel punto x = mean resta solo la costante di normalizzazione
    solo_norm = m.gaussian_log_prob(mean[None, :], mean, log_var)
    atteso_norm = float(np.sum(-0.5 * (np.log(2.0 * np.pi) + log_var)))
    assert_allclose(solo_norm, [atteso_norm], rtol=1e-12, atol=1e-14,
                    err_msg="in x = mean il termine quadratico si annulla e deve restare "
                            "-0.5 * sum_d (log(2 pi) + log_var_d)")


# ---------------------------------------------------------------------------
# 2. KL in forma chiusa
# ---------------------------------------------------------------------------

def test_kl_analitica_contro_stima_monte_carlo():
    """(c) ORACOLO INDIPENDENTE: la KL in forma chiusa deve coincidere con la
    stima Monte Carlo della sua DEFINIZIONE, E_q[log q(z) - log p(z)].

    Il campionamento e le due log-densita' sono scritti qui dentro, senza usare
    nessuna funzione dello studente.
    """
    mean = np.array([[0.5, -1.0, 0.2], [1.5, 0.0, -0.7]])
    log_var = np.array([[0.3, -0.7, 0.0], [-1.2, 0.4, 0.9]])

    analitica = m.kl_diag_gaussian_standard(mean, log_var)
    assert analitica.shape == (2,), (
        f"shape attesa (2,), ottenuta {analitica.shape}: la KL e' PER ESEMPIO, con le "
        "dimensioni latenti sommate"
    )

    rng = np.random.default_rng(20240002)
    n = 400000
    eps = rng.standard_normal((n, 2, 3))
    z = mean + np.exp(0.5 * log_var) * eps

    def logdens(zz, mu, lv):
        return -0.5 * np.sum(np.log(2.0 * np.pi) + lv + (zz - mu) ** 2 * np.exp(-lv), axis=-1)

    mc = np.mean(logdens(z, mean, log_var) - logdens(z, 0.0, 0.0), axis=0)
    # errore standard della stima MC ~ 2e-3: atol 0.01 e' ~5 deviazioni standard
    assert_allclose(analitica, mc, atol=0.01,
                    err_msg=f"forma chiusa {analitica} contro definizione stimata per "
                            f"campionamento {mc}: la formula giusta e' "
                            "0.5 * sum_d (exp(lv) + mean^2 - 1 - lv); errori tipici sono il "
                            "segno di lv, usare var invece di exp(lv), dimenticare il -1")


def test_kl_nulla_esattamente_sul_prior_standard():
    """(d) CASO LIMITE: se q coincide col prior N(0, I) la KL vale ESATTAMENTE 0.
    Ed e' comunque non negativa e crescente nell'allontanarsi dal prior."""
    zero = m.kl_diag_gaussian_standard(np.zeros((4, 6)), np.zeros((4, 6)))
    assert_allclose(zero, np.zeros(4), rtol=0.0, atol=0.0,
                    err_msg="con mean = 0 e log_var = 0 (cioe' q = N(0, I) = prior) la KL deve "
                            "essere esattamente 0.0, non un residuo numerico: se ottieni un "
                            "valore diverso manca il termine -1 oppure il -log_var")

    rng = np.random.default_rng(20240003)
    mean = rng.normal(scale=2.0, size=(200, 5))
    log_var = rng.normal(scale=1.5, size=(200, 5))
    kl = m.kl_diag_gaussian_standard(mean, log_var)
    assert np.all(kl >= 0.0), (
        "la KL e' non negativa per definizione (disuguaglianza di Gibbs): valore minimo "
        f"ottenuto {kl.min():.6f}"
    )

    # allontanando la media dal prior a log_var fisso, la KL cresce di mean^2/2
    base = m.kl_diag_gaussian_standard(np.zeros((1, 2)), np.zeros((1, 2)))
    shift = m.kl_diag_gaussian_standard(np.array([[3.0, -4.0]]), np.zeros((1, 2)))
    assert_allclose(shift - base, [12.5], rtol=1e-12,
                    err_msg="a log_var = 0 la KL vale 0.5 * sum(mean^2): spostando la media a "
                            "(3, -4) deve valere esattamente 12.5")


# ---------------------------------------------------------------------------
# 3. Reparameterization trick
# ---------------------------------------------------------------------------

def test_reparameterize_rumore_indipendente_dai_parametri():
    """(e) IL PUNTO DEL TRICK: a parita' di seed il rumore eps e' lo stesso
    qualunque siano mean e log_var, perche' eps ~ N(0, I) non dipende dai
    parametri. E' cio' che rende z derivabile rispetto a mean e log_var.
    """
    shape = (7, 4)
    mean_a = np.full(shape, 0.0)
    lv_a = np.full(shape, 0.0)
    mean_b = np.linspace(-3.0, 3.0, 28).reshape(shape)
    lv_b = np.linspace(-2.0, 1.5, 28).reshape(shape)

    za = m.reparameterize(mean_a, lv_a, np.random.default_rng(20240004))
    zb = m.reparameterize(mean_b, lv_b, np.random.default_rng(20240004))
    assert za.shape == shape and zb.shape == shape, "z deve avere la stessa shape di mean"

    eps_a = (za - mean_a) / np.exp(0.5 * lv_a)
    eps_b = (zb - mean_b) / np.exp(0.5 * lv_b)
    assert_allclose(eps_a, eps_b, rtol=1e-9, atol=1e-12,
                    err_msg="con lo stesso seed il rumore (z - mean)/exp(0.5*log_var) deve essere "
                            "IDENTICO al variare di mean e log_var: se cambia, la sorgente di "
                            "casualita' dipende dai parametri e il percorso non e' derivabile")

    # determinismo: stesso seed -> stesso z; seed diverso -> z diverso
    z1 = m.reparameterize(mean_b, lv_b, np.random.default_rng(99))
    z2 = m.reparameterize(mean_b, lv_b, np.random.default_rng(99))
    assert_allclose(z1, z2, rtol=0.0, atol=0.0,
                    err_msg="con lo stesso seed reparameterize deve restituire esattamente lo "
                            "stesso z: non usare np.random.seed o il modulo random")
    z3 = m.reparameterize(mean_b, lv_b, np.random.default_rng(100))
    assert np.max(np.abs(z3 - z1)) > 1e-6, "con un seed diverso z deve cambiare"


def test_reparameterize_riproduce_media_e_varianza():
    """(f) i campioni prodotti devono avere media `mean` e varianza
    `exp(log_var)` - non `exp(2*log_var)` ne' `exp(0.5*log_var)`."""
    mean = np.array([1.0, -2.0, 0.0, 5.0])
    log_var = np.array([-1.5, 0.0, 2.0, 0.5])
    rng = np.random.default_rng(20240005)
    n = 400000
    z = m.reparameterize(np.broadcast_to(mean, (n, 4)),
                         np.broadcast_to(log_var, (n, 4)), rng)
    assert z.shape == (n, 4), f"shape attesa ({n}, 4), ottenuta {z.shape}"

    var_attesa = np.exp(log_var)
    assert_allclose(z.mean(axis=0), mean, atol=0.02,
                    err_msg="la media empirica di z deve essere `mean`: il rumore va SOMMATO a "
                            "mean, non moltiplicato")
    assert_allclose(z.var(axis=0), var_attesa, rtol=0.02,
                    err_msg=f"varianza empirica {z.var(axis=0)} contro {var_attesa}: la scala e' "
                            "exp(0.5 * log_var) (deviazione standard), non exp(log_var) "
                            "(varianza) ne' log_var")


# ---------------------------------------------------------------------------
# 4. ELBO
# ---------------------------------------------------------------------------

def test_elbo_deterministico_e_media_su_n_samples():
    """(g) shape, determinismo a parita' di seed, e coerenza fra la stima con
    S = 1 (ripetuta) e la stima con S grande: n_samples deve MEDIARE, non
    sommare."""
    x = np.array([[0.9], [-1.4], [0.0]])
    mean = np.array([[0.3], [-0.5], [1.2]])
    log_var = np.array([[-0.4], [0.2], [-1.0]])

    e1 = m.elbo(x, mean, log_var, m.toy_decoder, np.random.default_rng(7), n_samples=16)
    e2 = m.elbo(x, mean, log_var, m.toy_decoder, np.random.default_rng(7), n_samples=16)
    assert e1.shape == (3,), f"l'ELBO e' PER ESEMPIO: shape attesa (3,), ottenuta {e1.shape}"
    assert_allclose(e1, e2, rtol=0.0, atol=0.0,
                    err_msg="con lo stesso seed l'ELBO stimato deve essere identico bit a bit")
    e3 = m.elbo(x, mean, log_var, m.toy_decoder, np.random.default_rng(8), n_samples=16)
    assert np.max(np.abs(e3 - e1)) > 1e-9, "con un seed diverso la stima deve cambiare"

    # media di 4000 stime con S = 1 contro una stima con S = 200000
    rng = np.random.default_rng(20240006)
    acc = np.zeros(3)
    for _ in range(4000):
        acc += m.elbo(x, mean, log_var, m.toy_decoder, rng, n_samples=1)
    acc /= 4000.0
    grande = m.elbo(x, mean, log_var, m.toy_decoder,
                    np.random.default_rng(20240007), n_samples=200000)
    assert_allclose(acc, grande, atol=0.06,
                    err_msg=f"media di 4000 stime a S=1 ({acc}) contro una stima a S=200000 "
                            f"({grande}): il termine di ricostruzione va MEDIATO sugli S "
                            "campioni, e la KL va sottratta una volta sola")


def test_elbo_limita_dal_basso_la_log_evidenza():
    """(h) ORACOLO INDIPENDENTE: log P(x) e' calcolata per QUADRATURA sul
    latente (nessun campionamento). L'ELBO non puo' superarla, per nessuna
    scelta di q. La quadratura viene a sua volta validata contro la forma
    chiusa della marginale del modello lineare-gaussiano.
    """
    x_vals = np.array([0.9, -1.4, 0.0])
    log_px = m.toy_log_evidence(x_vals)

    var_marg = m.TOY_A ** 2 + np.exp(m.TOY_X_LOG_VAR)
    chiusa = -0.5 * (np.log(2.0 * np.pi * var_marg) + (x_vals - m.TOY_B) ** 2 / var_marg)
    assert_allclose(log_px, chiusa, rtol=1e-10, atol=1e-12,
                    err_msg="la quadratura fornita non riproduce la marginale in forma chiusa "
                            "(problema dell'ambiente, non della tua implementazione)")

    X = x_vals[:, None]
    post_mean, post_log_var = m.toy_posterior(x_vals)
    candidati = [
        (np.zeros((3, 1)), np.zeros((3, 1))),                       # q = prior
        (post_mean + 0.8, post_log_var + 0.5),                      # q spostata e larga
        (np.full((3, 1), -2.0), np.full((3, 1), -1.0)),             # q molto sbagliata
        (post_mean, post_log_var - 1.2),                            # q troppo stretta
    ]
    for i, (qm, qlv) in enumerate(candidati):
        est = m.elbo(X, qm, qlv, m.toy_decoder,
                     np.random.default_rng(1000 + i), n_samples=200000)
        assert np.all(est <= log_px + 0.02), (
            f"candidato {i}: ELBO {est} supera log P(x) {log_px}. L'ELBO e' un limite "
            "INFERIORE: se lo superi hai sbagliato il segno della KL (va SOTTRATTA) o "
            "stai dimenticando del tutto il termine di regolarizzazione"
        )
        # e il limite non e' vuoto: la distanza e' finita e strettamente positiva
        assert np.all(est >= log_px - 40.0), f"candidato {i}: ELBO {est} implausibilmente basso"

    # q = prior e' peggiore della posterior esatta: il bound e' piu' lasco
    e_prior = m.elbo(X, np.zeros((3, 1)), np.zeros((3, 1)), m.toy_decoder,
                     np.random.default_rng(31), n_samples=200000)
    e_post = m.elbo(X, post_mean, post_log_var, m.toy_decoder,
                    np.random.default_rng(32), n_samples=200000)
    assert np.all(e_post > e_prior + 0.1), (
        "l'ELBO calcolato con la posterior esatta deve essere STRETTAMENTE maggiore di "
        "quello calcolato col prior: massimizzare l'ELBO rispetto a q avvicina q alla "
        "posterior"
    )


def test_gap_elbo_uguale_kl_dalla_posterior():
    """(i) IDENTITA' FONDAMENTALE: log P(x) - ELBO(q) = KL( q(z) || P(z|x) ).

    Nel modello lineare-gaussiano la posterior e' gaussiana, quindi la KL fra
    due gaussiane e' in forma chiusa e il gap si prevede esattamente. In
    particolare, quando q E' la posterior il gap vale 0 e il bound e' stretto.
    """
    x_vals = np.array([0.9, -1.4, 0.0])
    log_px = m.toy_log_evidence(x_vals)
    X = x_vals[:, None]
    post_mean, post_log_var = m.toy_posterior(x_vals)
    pv = np.exp(post_log_var)

    for i, (qm, qlv) in enumerate([
        (np.zeros((3, 1)), np.zeros((3, 1))),
        (post_mean + 0.8, post_log_var + 0.5),
        (post_mean, post_log_var),          # bound stretto: gap atteso 0
    ]):
        est = m.elbo(X, qm, qlv, m.toy_decoder,
                     np.random.default_rng(2000 + i), n_samples=400000)
        gap = log_px - est
        gap_atteso = _kl_gauss_gauss(qm, np.exp(qlv), post_mean, pv).ravel()
        # errore standard della stima MC dell'ELBO ~ 5e-3: atol 0.03 e' ampio
        assert_allclose(gap, gap_atteso, atol=0.03,
                        err_msg=f"candidato {i}: gap misurato {gap} contro "
                                f"KL(q || posterior) {gap_atteso}. Il difetto dell'ELBO rispetto "
                                "a log P(x) e' ESATTAMENTE la KL fra q e la posterior vera, non "
                                "la KL fra q e il prior (quella e' un termine dell'ELBO)")

    # caso stretto isolato: con q = posterior il gap e' zero entro il rumore MC
    est = m.elbo(X, post_mean, post_log_var, m.toy_decoder,
                 np.random.default_rng(2222), n_samples=400000)
    assert_allclose(log_px - est, np.zeros(3), atol=0.03,
                    err_msg="con q uguale alla posterior esatta l'ELBO deve coincidere con "
                            "log P(x): il bound e' stretto se e solo se q = P(z|x)")


# ---------------------------------------------------------------------------
# 5. Stimatori del gradiente
# ---------------------------------------------------------------------------

def test_entrambi_gli_stimatori_sono_non_distorti():
    """(l) ORACOLO ANALITICO. Con f(z) = sum_d z_d^2 e q = N(mean, diag(exp(lv)))

        E_q[f] = sum_d (mean_d^2 + exp(lv_d))
        d/d mean_d    E_q[f] = 2 * mean_d
        d/d log_var_d E_q[f] = exp(log_var_d)

    Entrambi gli stimatori devono convergere a QUESTI valori: sono due formule
    diverse per lo stesso gradiente, non due gradienti diversi.
    """
    mean = np.array([0.7, -0.4])
    log_var = np.array([0.0, -0.5])
    vero_gm = 2.0 * mean
    vero_glv = np.exp(log_var)

    R, S = 100, 20000
    r_path = np.random.default_rng(20240008)
    r_score = np.random.default_rng(20240008)
    acc = np.zeros((4, 2))
    for _ in range(R):
        a, b = m.reparam_grad_estimator(_grad_sum_squares, mean, log_var, r_path, S)
        c, d = m.score_function_grad_estimator(_sum_squares, mean, log_var, r_score, S)
        acc += np.stack([a, b, c, d])
    acc /= R

    assert acc.shape == (4, 2), "entrambi gli stimatori devono restituire due array di shape (D,)"
    assert_allclose(acc[0], vero_gm, atol=0.02,
                    err_msg=f"pathwise d/dmean = {acc[0]} contro {vero_gm}: con z = mean + std*eps "
                            "si ha dz/dmean = 1, quindi lo stimatore e' la media di f'(z)")
    assert_allclose(acc[1], vero_glv, atol=0.02,
                    err_msg=f"pathwise d/dlog_var = {acc[1]} contro {vero_glv}: "
                            "dz/dlog_var = 0.5 * exp(0.5*log_var) * eps, il fattore 0.5 e' quello "
                            "che si dimentica piu' spesso")
    assert_allclose(acc[2], vero_gm, atol=0.02,
                    err_msg=f"score function d/dmean = {acc[2]} contro {vero_gm}: "
                            "d log q/d mean = (z - mean)/exp(log_var)")
    assert_allclose(acc[3], vero_glv, atol=0.02,
                    err_msg=f"score function d/dlog_var = {acc[3]} contro {vero_glv}: "
                            "d log q/d log_var = 0.5*((z-mean)^2/exp(log_var) - 1); se manca il "
                            "-1 lo stimatore e' distorto di 0.5*E[f]")


def test_varianza_reparam_molto_minore_di_score():
    """(m) TEST CHIAVE. A PARITA' di campioni (stesso S, e con lo stesso seed
    anche gli STESSI z), i due stimatori hanno la stessa media - il gradiente
    analitico - ma varianze di ordini di grandezza diversi.

    Il pathwise usa l'informazione f'(z); lo score function usa solo i valori
    f(z) e paga con il rumore. E' il motivo per cui il VAE si addestra con il
    reparameterization trick e non con REINFORCE (slide 22 e 26).
    """
    mean = np.array([1.0, 2.0, -1.5])
    log_var = np.full(3, -3.0)              # std ~ 0.22: q stretta, score molto rumoroso
    vero_gm = 2.0 * mean
    vero_glv = np.exp(log_var)

    R, S = 8000, 32
    r_path = np.random.default_rng(20240009)
    r_score = np.random.default_rng(20240009)   # stesso seed: campioni z APPAIATI
    P_m = np.empty((R, 3)); P_v = np.empty((R, 3))
    S_m = np.empty((R, 3)); S_v = np.empty((R, 3))
    for i in range(R):
        P_m[i], P_v[i] = m.reparam_grad_estimator(_grad_sum_squares, mean, log_var, r_path, S)
        S_m[i], S_v[i] = m.score_function_grad_estimator(_sum_squares, mean, log_var, r_score, S)

    # --- (1) nessuno dei due e' distorto
    assert_allclose(P_m.mean(axis=0), vero_gm, atol=0.02,
                    err_msg="lo stimatore pathwise deve essere non distorto")
    assert_allclose(P_v.mean(axis=0), vero_glv, atol=0.02,
                    err_msg="lo stimatore pathwise deve essere non distorto anche su log_var")
    # per lo score function l'errore standard su R*S = 256000 campioni vale ~0.07:
    # atol = 0.30 sono ~4 deviazioni standard. La tolleranza larga NON e' lassismo,
    # e' esattamente la varianza che questo test sta misurando.
    assert_allclose(S_m.mean(axis=0), vero_gm, atol=0.30,
                    err_msg=f"lo score function e' non distorto: media {S_m.mean(axis=0)} contro "
                            f"{vero_gm}. Se e' fuori di molto e' un errore di formula, non rumore")
    assert_allclose(S_v.mean(axis=0), vero_glv, atol=0.05,
                    err_msg="lo score function e' non distorto anche su log_var")

    # --- (2) ma la varianza e' di ordini di grandezza diversa
    rap_m = S_m.var(axis=0) / P_m.var(axis=0)
    rap_v = S_v.var(axis=0) / P_v.var(axis=0)
    assert np.all(rap_m > 1000.0), (
        f"rapporto fra le varianze su d/dmean: {rap_m}. A parita' di campioni lo score "
        "function deve essere ordini di grandezza piu' rumoroso del pathwise; se il "
        "rapporto e' vicino a 1 i due stimatori stanno calcolando la stessa cosa e uno "
        "dei due e' scritto male"
    )
    assert np.all(rap_v > 50.0), (
        f"rapporto fra le varianze su d/dlog_var: {rap_v}, atteso >> 1"
    )
    assert np.all(P_m.var(axis=0) < 0.05), (
        f"varianza del pathwise {P_m.var(axis=0)}: con f'(z) = 2z e S = {S} campioni deve "
        "valere circa 4*exp(log_var)/S"
    )


def test_baseline_riduce_varianza_senza_distorcere():
    """(n) la baseline sottrae una costante a f(z). Poiche' E_q[grad log q] = 0,
    non introduce distorsione: cambia SOLO la varianza. Con b = E_q[f] la
    riduzione e' di oltre un ordine di grandezza.
    """
    mean = np.array([1.0, 2.0, -1.5])
    log_var = np.full(3, -3.0)
    vero_gm = 2.0 * mean
    vero_glv = np.exp(log_var)
    b = float(np.sum(mean ** 2 + np.exp(log_var)))       # = E_q[f]

    R, S = 8000, 32
    r0 = np.random.default_rng(20240010)
    r1 = np.random.default_rng(20240010)                 # stesso stream: confronto appaiato
    A_m = np.empty((R, 3)); A_v = np.empty((R, 3))
    B_m = np.empty((R, 3)); B_v = np.empty((R, 3))
    for i in range(R):
        A_m[i], A_v[i] = m.score_function_grad_estimator(_sum_squares, mean, log_var, r0, S)
        B_m[i], B_v[i] = m.score_function_grad_estimator(_sum_squares, mean, log_var, r1, S,
                                                         baseline=b)

    assert_allclose(B_m.mean(axis=0), vero_gm, atol=0.10,
                    err_msg=f"con baseline la media resta {B_m.mean(axis=0)} contro {vero_gm}: la "
                            "baseline NON deve spostare il valore atteso, perche' "
                            "E_q[grad log q] = 0. Se sposta, la stai sottraendo nel posto "
                            "sbagliato (per esempio al gradiente invece che a f(z))")
    assert_allclose(B_v.mean(axis=0), vero_glv, atol=0.03,
                    err_msg="con baseline la media di d/dlog_var non deve spostarsi")

    rid_m = A_m.var(axis=0) / B_m.var(axis=0)
    rid_v = A_v.var(axis=0) / B_v.var(axis=0)
    assert np.all(rid_m > 8.0), (
        f"la baseline b = E_q[f] deve ridurre nettamente la varianza di d/dmean, "
        f"rapporto ottenuto {rid_m}: se vale ~1 la baseline non viene usata"
    )
    assert np.all(rid_v > 5.0), (
        f"la baseline deve ridurre anche la varianza di d/dlog_var, rapporto {rid_v}"
    )

    # baseline = None deve essere identico a baseline = 0.0
    z0 = m.score_function_grad_estimator(_sum_squares, mean, log_var,
                                         np.random.default_rng(5), 256)
    z1 = m.score_function_grad_estimator(_sum_squares, mean, log_var,
                                         np.random.default_rng(5), 256, baseline=0.0)
    assert_allclose(z0[0], z1[0], rtol=0.0, atol=0.0,
                    err_msg="baseline=None deve comportarsi esattamente come baseline=0.0")


def test_score_function_funziona_con_f_non_differenziabile():
    """(o) A COSA SERVE ancora lo score function: f(z) = 1[z > 0] ha gradiente
    nullo quasi ovunque, quindi il pathwise non dice nulla. Lo score function
    invece stima il gradiente vero, che qui e' in forma chiusa:

        E_q[f] = Phi(mean/std)
        d/d mean    = phi(mean/std) / std
        d/d log_var = -0.5 * (mean/std) * phi(mean/std)
    """
    mu, lv = 0.6, 0.0
    mean = np.array([mu]); log_var = np.array([lv])
    std = math.exp(0.5 * lv)
    phi = math.exp(-0.5 * (mu / std) ** 2) / math.sqrt(2.0 * math.pi)
    vero_gm = phi / std
    vero_glv = -0.5 * (mu / std) * phi

    f_ind = lambda z: (np.asarray(z)[:, 0] > 0.0).astype(float)

    rng = np.random.default_rng(20240011)
    gm = 0.0; glv = 0.0
    for _ in range(20):
        a, b = m.score_function_grad_estimator(f_ind, mean, log_var, rng, 100000)
        gm += float(a[0]); glv += float(b[0])
    gm /= 20.0; glv /= 20.0

    assert_allclose(gm, vero_gm, atol=0.003,
                    err_msg=f"d/dmean stimato {gm:.5f} contro il valore esatto {vero_gm:.5f} "
                            "(densita' della normale standard in mean/std, diviso std)")
    assert_allclose(glv, vero_glv, atol=0.003,
                    err_msg=f"d/dlog_var stimato {glv:.5f} contro il valore esatto "
                            f"{vero_glv:.5f}")

    # controprova: il gradiente di f e' nullo quasi ovunque, quindi lo stimatore
    # pathwise costruito su di esso restituisce zero e non e' utilizzabile qui.
    zero_grad = lambda z: np.zeros_like(np.asarray(z))
    pm, plv = m.reparam_grad_estimator(zero_grad, mean, log_var,
                                       np.random.default_rng(1), 100000)
    assert_allclose(np.concatenate([pm, plv]), np.zeros(2), rtol=0.0, atol=0.0,
                    err_msg="con f' identicamente nullo il pathwise deve restituire 0: e' proprio "
                            "il caso in cui il reparameterization trick non e' applicabile e "
                            "serve lo score function")
    assert abs(vero_gm) > 0.1, "il gradiente vero non e' nullo: il pathwise su f' = 0 lo perde"
