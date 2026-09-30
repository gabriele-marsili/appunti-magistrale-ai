"""Suite di autovalutazione per l'esercizio CAVI.

    python3 -m pytest test_cavi.py -v            # sul tuo skeleton
    GDL_SOL=1 python3 -m pytest test_cavi.py -v  # sulla soluzione di riferimento
"""

import os
import sys
import pathlib
import importlib
import itertools

import numpy as np

HERE = pathlib.Path(__file__).parent
if os.environ.get("GDL_SOL"):
    sys.path.insert(0, str(HERE / "soluzione"))
    m = importlib.import_module("cavi_sol")
else:
    sys.path.insert(0, str(HERE))
    m = importlib.import_module("cavi")


LOG_2PI = float(np.log(2.0 * np.pi))
SIGMA0_SQ = 10.0


# ---------------------------------------------------------------------------
# Oracoli indipendenti, scritti nel test e non riusati dal modulo
# ---------------------------------------------------------------------------

def _ref_lognorm(x, mu, var):
    """Log-densita' gaussiana di riferimento, usata solo dagli oracoli."""
    return -0.5 * (LOG_2PI + np.log(var) + (x - mu) ** 2 / var)


def _log_evidence_exact(x, K, sigma0_sq):
    """log p(x) ESATTA, per forza bruta.

    Enumera tutte le K^N assegnazioni c e per ciascuna integra mu in forma
    chiusa. Per un'assegnazione fissata, la componente k vede n_k punti con
    somma B e somma dei quadrati S; allora

        int N(mu; 0, s0^2) prod_{i in k} N(x_i; mu, 1) dmu
          = exp( -0.5*n_k*log(2pi) - 0.5*log(s0^2) - 0.5*log(A)
                 + B^2/(2A) - S/2 ),        con A = n_k + 1/s0^2

    e log p(x) = -N log K + logsumexp_c sum_k log I_k(c).

    Metodo completamente diverso dall'ELBO: nessuna approssimazione, nessuna
    fattorizzazione mean-field. Costo K^N, quindi solo per N piccolissimi.
    """
    x = np.asarray(x, dtype=float)
    N = x.shape[0]
    terms = []
    for assign in itertools.product(range(K), repeat=N):
        a = np.asarray(assign)
        tot = 0.0
        for k in range(K):
            sel = x[a == k]
            n_k = sel.size
            A = n_k + 1.0 / sigma0_sq
            B = sel.sum()
            tot += (-0.5 * n_k * LOG_2PI
                    - 0.5 * np.log(sigma0_sq)
                    - 0.5 * np.log(A)
                    + B ** 2 / (2.0 * A)
                    - 0.5 * np.sum(sel ** 2))
        terms.append(tot)
    terms = np.asarray(terms)
    mx = terms.max()
    return float(-N * np.log(K) + mx + np.log(np.sum(np.exp(terms - mx))))


def _random_q(rng, N, K):
    """Parametri variazionali casuali (validi ma lontani dall'ottimo)."""
    phi = rng.random((N, K))
    phi /= phi.sum(axis=1, keepdims=True)
    return phi, rng.normal(0.0, 3.0, K), rng.uniform(0.05, 5.0, K)


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------

def test_log_norm_pdf_contro_definizione():
    """La log-densita' e' quella giusta, si broadcasta e integra a 1."""
    x = np.array([-2.0, 0.0, 1.5, 4.0])
    got = m.log_norm_pdf(x, 0.5, 2.0)
    atteso = np.log(np.exp(-((x - 0.5) ** 2) / 4.0) / np.sqrt(4.0 * np.pi))
    np.testing.assert_allclose(got, atteso, rtol=1e-6, atol=1e-9,
                               err_msg="log_norm_pdf non coincide con log della densita' gaussiana")

    b = m.log_norm_pdf(x[:, None], np.array([0.0, 1.0, 2.0])[None, :], 1.0)
    assert np.asarray(b).shape == (4, 3), \
        "log_norm_pdf deve essere vettorizzata e rispettare il broadcasting numpy"

    g = np.linspace(-40.0, 40.0, 200001)
    massa = float(np.sum(np.exp(m.log_norm_pdf(g, -1.0, 3.0)))) * (g[1] - g[0])
    np.testing.assert_allclose(massa, 1.0, rtol=1e-6, atol=1e-9,
                               err_msg="exp(log_norm_pdf) non integra a 1: manca una costante di normalizzazione")


def test_phi_righe_normalizzate():
    """q(c_i) e' una distribuzione: righe non negative che sommano a 1."""
    x, _ = m.make_mixture_data(50, 3, [-4.0, 0.0, 4.0], seed=0)
    rng = np.random.default_rng(1)
    for _ in range(5):
        mu = rng.normal(0.0, 3.0, 3)
        s2 = rng.uniform(0.05, 4.0, 3)
        phi = np.asarray(m.update_phi(x, mu, s2))
        assert phi.shape == (50, 3), f"update_phi deve restituire shape (N, K), non {phi.shape}"
        assert np.all(phi >= 0.0), "phi contiene valori negativi: non e' una distribuzione"
        np.testing.assert_allclose(phi.sum(axis=1), np.ones(50), rtol=1e-6, atol=1e-9,
                                   err_msg="le righe di phi non sommano a 1: manca la normalizzazione per riga (axis=1)")

    # con x molto grandi la versione ingenua va in overflow
    phi = np.asarray(m.update_phi(np.array([600.0, -600.0]), np.array([600.0, -600.0]), np.ones(2)))
    assert np.all(np.isfinite(phi)), "update_phi va in overflow: serve il trucco log-sum-exp"


def test_update_phi_e_ottimo_dato_mu():
    """L'aggiornamento di q(c) massimizza l'ELBO a (m, s2) fissi.

    Questo test cade se si usa E[mu_k]^2 al posto di E[mu_k^2] = m_k^2 + s2_k:
    l'ELBO resta monotono, ma phi non e' piu' il massimo condizionato.
    """
    x, _ = m.make_mixture_data(30, 3, [-3.0, 0.0, 4.0], seed=11)
    rng = np.random.default_rng(2)
    mu = rng.normal(0.0, 2.0, 3)
    s2 = rng.uniform(0.2, 2.0, 3)          # varianze DIVERSE fra componenti

    phi_star = m.update_phi(x, mu, s2)
    e_star = m.elbo(x, phi_star, mu, s2, SIGMA0_SQ)

    for _ in range(200):
        lam = rng.uniform(0.01, 0.9)
        rumore = rng.random((30, 3))
        rumore /= rumore.sum(axis=1, keepdims=True)
        phi_pert = (1.0 - lam) * np.asarray(phi_star) + lam * rumore
        e_pert = m.elbo(x, phi_pert, mu, s2, SIGMA0_SQ)
        assert e_star >= e_pert - 1e-9, \
            "update_phi non massimizza l'ELBO in phi: rileggi quali momenti di q(mu) entrano nell'esponente"


def test_update_mu_e_ottimo_dato_phi():
    """L'aggiornamento di q(mu) massimizza l'ELBO a phi fisso."""
    x, _ = m.make_mixture_data(30, 3, [-3.0, 0.0, 4.0], seed=11)
    rng = np.random.default_rng(5)
    phi = rng.random((30, 3))
    phi /= phi.sum(axis=1, keepdims=True)

    mu_star, s2_star = m.update_mu(x, phi, SIGMA0_SQ)
    mu_star = np.asarray(mu_star)
    s2_star = np.asarray(s2_star)
    assert mu_star.shape == (3,) and s2_star.shape == (3,), \
        "update_mu deve restituire due array di shape (K,)"
    assert np.all(s2_star > 0.0), "le varianze di q(mu) devono essere positive"

    e_star = m.elbo(x, phi, mu_star, s2_star, SIGMA0_SQ)
    for _ in range(200):
        mu_p = mu_star + rng.normal(0.0, 0.3, 3)
        s2_p = s2_star * np.exp(rng.normal(0.0, 0.3, 3))
        assert e_star >= m.elbo(x, phi, mu_p, s2_p, SIGMA0_SQ) - 1e-9, \
            "update_mu non massimizza l'ELBO in (m, s2): controlla precisione del prior e responsabilita'"


def test_elbo_analitico_uguale_monte_carlo():
    """Oracolo: la formula chiusa deve coincidere con la stima MC dello stesso ELBO."""
    # (a) al punto fisso di CAVI: con dati ben separati q(mu) e' la posterior
    # condizionata esatta e lo stimatore MC ha varianza quasi nulla, quindi qui
    # la tolleranza puo' essere strettissima.
    x, _ = m.make_mixture_data(12, 2, [-4.0, 4.0], seed=1)
    r = m.cavi(x, 2, sigma0_sq=SIGMA0_SQ, seed=0)
    analitico = m.elbo(x, r["phi"], r["m"], r["s2"], SIGMA0_SQ)
    stima = m.elbo_monte_carlo(x, r["phi"], r["m"], r["s2"], SIGMA0_SQ,
                               100_000, np.random.default_rng(0))
    assert abs(analitico - stima) < 1e-4, (
        f"ELBO analitico {analitico:.6f} contro stima MC {stima:.6f}: "
        "la formula chiusa non calcola la stessa quantita'")

    # (b) lontano dall'ottimo, dove la stima MC ha varianza vera.
    # errore standard misurato ~0.019 con 400k campioni: 0.15 sono ~8 sigma,
    # e comunque il seed e' fissato quindi il test e' deterministico.
    x2, _ = m.make_mixture_data(8, 2, [-3.0, 3.0], seed=1)
    r2 = m.cavi(x2, 2, sigma0_sq=SIGMA0_SQ, seed=0)
    phi_p = 0.75 * np.asarray(r2["phi"]) + 0.125
    m_p = np.asarray(r2["m"]) + np.array([0.4, -0.3])
    s2_p = np.asarray(r2["s2"]) * 1.6
    analitico2 = m.elbo(x2, phi_p, m_p, s2_p, SIGMA0_SQ)
    stima2 = m.elbo_monte_carlo(x2, phi_p, m_p, s2_p, SIGMA0_SQ,
                                400_000, np.random.default_rng(0))
    assert abs(analitico2 - stima2) < 0.15, (
        f"ELBO analitico {analitico2:.4f} contro stima MC {stima2:.4f} fuori dall'ottimo: "
        "la formula chiusa e' sbagliata per q generici (probabile termine di entropia mancante)")


def test_elbo_monotono_in_cavi():
    """Proprieta' centrale: CAVI non fa mai scendere l'ELBO."""
    for seed_dati in range(4):
        for K in (2, 3, 5):
            x, _ = m.make_mixture_data(40, K, seed=seed_dati)
            r = m.cavi(x, K, sigma0_sq=SIGMA0_SQ, seed=0)

            assert set(r) >= {"m", "s2", "phi", "elbo_history", "n_iter"}, \
                "cavi deve restituire le chiavi m, s2, phi, elbo_history, n_iter"
            h = np.asarray(r["elbo_history"], dtype=float)
            assert h.shape == (r["n_iter"],), \
                "elbo_history deve avere un valore per ogni iterazione eseguita"
            assert np.all(np.isfinite(h)), "elbo_history contiene NaN o infiniti"
            assert np.all(np.diff(h) >= -1e-9), (
                f"ELBO non monotono (K={K}, dati seed={seed_dati}): salto minimo "
                f"{np.diff(h).min():.3e}. Ogni update coordinato e' un massimo esatto, "
                "quindi l'ELBO puo' solo salire o restare fermo")

    # versione piu' fine: anche i singoli mezzi passi non devono far scendere l'ELBO
    x, _ = m.make_mixture_data(40, 3, seed=0)
    rng = np.random.default_rng(0)
    mu = x[rng.choice(40, size=3, replace=False)].copy()
    s2 = np.ones(3)
    phi = np.full((40, 3), 1.0 / 3.0)
    prec = m.elbo(x, phi, mu, s2, SIGMA0_SQ)
    for _ in range(30):
        phi = m.update_phi(x, mu, s2)
        e1 = m.elbo(x, phi, mu, s2, SIGMA0_SQ)
        assert e1 >= prec - 1e-9, "l'aggiornamento di q(c) ha fatto scendere l'ELBO"
        mu, s2 = m.update_mu(x, phi, SIGMA0_SQ)
        e2 = m.elbo(x, phi, mu, s2, SIGMA0_SQ)
        assert e2 >= e1 - 1e-9, "l'aggiornamento di q(mu) ha fatto scendere l'ELBO"
        prec = e2


def test_cavi_recupera_cluster_ben_separati():
    """Con 3 cluster ben separati le assegnazioni sono quasi hard e le medie sono giuste."""
    medie_vere = np.array([-8.0, 0.0, 8.0])
    x, c_vere = m.make_mixture_data(180, 3, medie_vere, seed=3)
    r = m.cavi(x, 3, sigma0_sq=SIGMA0_SQ, seed=0)

    phi = np.asarray(r["phi"])
    massimi = phi.max(axis=1)
    assert np.all(massimi > 0.99), (
        f"con cluster distanti 8 deviazioni standard q(c_i) dovrebbe essere quasi degenere, "
        f"ma la responsabilita' massima piu' bassa vale {massimi.min():.3f}")

    # label switching: le componenti sono scambiabili, quindi si confronta ordinato
    stimate = np.sort(np.asarray(r["m"]))
    np.testing.assert_allclose(stimate, np.sort(medie_vere), atol=0.4,
                               err_msg=f"medie stimate (ordinate) {stimate} lontane dalle vere {np.sort(medie_vere)}")

    ordine = np.argsort(np.asarray(r["m"]))
    rango = np.empty(3, dtype=int)
    rango[ordine] = np.arange(3)
    predette = rango[phi.argmax(axis=1)]
    acc = float(np.mean(predette == c_vere))
    assert acc > 0.99, f"clustering sbagliato dopo aver risolto il label switching: accuratezza {acc:.3f}"

    assert np.all(np.asarray(r["s2"]) < 0.1), \
        "con ~60 punti per componente la varianza a posteriori di mu_k deve essere piccola"


def test_kl_gaussians_proprieta():
    """KL nulla per distribuzioni identiche, positiva altrimenti, asimmetrica."""
    for mu, v in [(0.0, 1.0), (-2.5, 0.3), (4.0, 7.0)]:
        np.testing.assert_allclose(m.kl_gaussians(mu, v, mu, v), 0.0, rtol=0, atol=1e-12,
                                   err_msg="KL fra due gaussiane identiche deve essere esattamente 0")

    rng = np.random.default_rng(4)
    for _ in range(200):
        m1, m2 = rng.normal(0.0, 3.0, 2)
        v1, v2 = rng.uniform(0.05, 5.0, 2)
        assert m.kl_gaussians(m1, v1, m2, v2) > 0.0, \
            f"KL negativa o nulla per distribuzioni diverse: N({m1},{v1}) || N({m2},{v2})"

    a = m.kl_gaussians(0.0, 1.0, 0.0, 4.0)
    b = m.kl_gaussians(0.0, 4.0, 0.0, 1.0)
    assert abs(a - b) > 1e-3, \
        "la KL non e' simmetrica: se il tuo valore lo e', hai probabilmente scambiato l'ordine degli argomenti"


def test_kl_gaussians_contro_monte_carlo():
    """Oracolo: la forma chiusa contro E_{p1}[log p1 - log p2] stimata per campionamento."""
    casi = [(0.5, 1.2, -0.3, 2.0), (0.0, 1.0, 0.0, 3.0), (2.0, 0.5, 2.0, 0.5), (-1.0, 2.0, 1.0, 1.0)]
    rng = np.random.default_rng(0)
    for m1, v1, m2, v2 in casi:
        s = m1 + np.sqrt(v1) * rng.standard_normal(2_000_000)
        stima = float(np.mean(_ref_lognorm(s, m1, v1) - _ref_lognorm(s, m2, v2)))
        esatta = m.kl_gaussians(m1, v1, m2, v2)
        assert abs(esatta - stima) < 0.01, (
            f"kl_gaussians({m1},{v1},{m2},{v2}) = {esatta:.5f} ma la stima MC vale {stima:.5f}")


def test_elbo_e_lower_bound_della_log_evidenza():
    """Il test concettuale: l'ELBO e' un LOWER bound, non un'approssimazione.

    Con N=4 e K=2 si enumerano tutte le 16 assegnazioni e si integra mu in forma
    chiusa, ottenendo log p(x) esatta. Nessun q mean-field puo' superarla.
    """
    x, _ = m.make_mixture_data(4, 2, [-2.0, 2.0], seed=5)
    log_evidenza = _log_evidence_exact(x, 2, SIGMA0_SQ)

    r = m.cavi(x, 2, sigma0_sq=SIGMA0_SQ, seed=0)
    e_cavi = m.elbo(x, r["phi"], r["m"], r["s2"], SIGMA0_SQ)
    assert e_cavi <= log_evidenza + 1e-9, (
        f"ELBO al punto fisso di CAVI ({e_cavi:.6f}) sopra la log-evidenza esatta "
        f"({log_evidenza:.6f}): impossibile, il bound e' inferiore")
    assert log_evidenza - e_cavi > 1e-3, (
        "con K=2 il mean-field spezza la dipendenza fra c e mu, quindi il gap "
        "KL(q || posterior) deve essere strettamente positivo")

    rng = np.random.default_rng(99)
    for _ in range(300):
        phi, mu, s2 = _random_q(rng, 4, 2)
        e = m.elbo(x, phi, mu, s2, SIGMA0_SQ)
        assert e <= log_evidenza + 1e-9, (
            f"ELBO {e:.6f} sopra la log-evidenza {log_evidenza:.6f} per parametri variazionali "
            "casuali: la disuguaglianza di Jensen deve valere per OGNI q, non solo all'ottimo")


def test_log_marginal_bound_gap_non_negativo():
    """Il gap restituito e' esattamente log p(x) - ELBO ed e' non negativo."""
    x, _ = m.make_mixture_data(4, 2, [-2.0, 2.0], seed=7)
    log_evidenza = _log_evidence_exact(x, 2, SIGMA0_SQ)

    rng = np.random.default_rng(21)
    for _ in range(100):
        phi, mu, s2 = _random_q(rng, 4, 2)
        gap = m.log_marginal_bound_gap(x, phi, mu, s2, SIGMA0_SQ, log_evidenza)
        atteso = log_evidenza - m.elbo(x, phi, mu, s2, SIGMA0_SQ)
        np.testing.assert_allclose(gap, atteso, rtol=1e-6, atol=1e-9,
                                   err_msg="log_marginal_bound_gap deve valere log_evidence - elbo, in quest'ordine")
        assert gap >= -1e-9, \
            f"gap negativo ({gap:.6e}): sarebbe una KL(q || posterior) negativa"


def test_caso_limite_K1():
    """Con K=1 il mean-field e' esatto: l'ELBO uguaglia la log-evidenza."""
    x, _ = m.make_mixture_data(20, 1, [1.5], seed=2)
    r = m.cavi(x, 1, sigma0_sq=SIGMA0_SQ, seed=0)

    phi = np.asarray(r["phi"])
    assert phi.shape == (20, 1), f"con K=1 phi deve avere shape (20, 1), non {phi.shape}"
    np.testing.assert_allclose(phi, np.ones((20, 1)), rtol=1e-6, atol=1e-9,
                               err_msg="con una sola componente ogni q(c_i) e' degenere su di essa")

    prec = 20.0 + 1.0 / SIGMA0_SQ
    np.testing.assert_allclose(np.asarray(r["s2"]), np.array([1.0 / prec]), rtol=1e-6, atol=1e-9,
                               err_msg="varianza a posteriori sbagliata: la precisione e' 1/sigma0^2 + N")
    np.testing.assert_allclose(np.asarray(r["m"]), np.array([x.sum() / prec]), rtol=1e-6, atol=1e-9,
                               err_msg="media a posteriori sbagliata: manca lo shrinkage verso il prior")

    # con K=1 non c'e' nulla da fattorizzare: q coincide con la posterior esatta
    log_evidenza = _log_evidence_exact(x, 1, SIGMA0_SQ)
    e = m.elbo(x, r["phi"], r["m"], r["s2"], SIGMA0_SQ)
    np.testing.assert_allclose(e, log_evidenza, rtol=1e-9, atol=1e-9,
                               err_msg=(f"con K=1 l'ELBO ({e:.9f}) deve coincidere con la log-evidenza "
                                        f"({log_evidenza:.9f}): il gap KL e' esattamente zero"))
