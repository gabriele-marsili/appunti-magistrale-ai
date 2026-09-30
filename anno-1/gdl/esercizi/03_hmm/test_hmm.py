"""Suite di autovalutazione per l'esercizio HMM.

    pytest test_hmm.py -v              # testa il tuo skeleton
    GDL_SOL=1 pytest test_hmm.py -v    # testa la soluzione di riferimento
"""

import itertools
import os
import pathlib
import sys
import importlib

import numpy as np

HERE = pathlib.Path(__file__).parent
if os.environ.get("GDL_SOL"):
    sys.path.insert(0, str(HERE / "soluzione"))
    m = importlib.import_module("hmm_sol")
else:
    sys.path.insert(0, str(HERE))
    m = importlib.import_module("hmm")


# =============================================================================
# HMM di riferimento.  A e B sono DELIBERATAMENTE asimmetriche: se trasponi A
# da qualche parte, i test se ne accorgono.
# =============================================================================

PI = np.array([0.6, 0.3, 0.1])
A = np.array(
    [
        [0.7, 0.2, 0.1],
        [0.1, 0.6, 0.3],
        [0.2, 0.3, 0.5],
    ]
)
B = np.array(
    [
        [0.5, 0.3, 0.2],
        [0.1, 0.2, 0.7],
        [0.3, 0.5, 0.2],
    ]
)
OBS = np.array([0, 2, 1, 1, 2, 0])  # T = 6, K = 3  ->  729 traiettorie


# --- HMM quasi deterministico: ciclo 0 -> 1 -> 2 -> 0, emissione ~ identita' --
_EPS = 1e-3
PI_DET = np.array([1.0 - 2 * _EPS, _EPS, _EPS])
A_DET = np.array(
    [
        [_EPS, 1.0 - 2 * _EPS, _EPS],
        [_EPS, _EPS, 1.0 - 2 * _EPS],
        [1.0 - 2 * _EPS, _EPS, _EPS],
    ]
)
B_DET = np.array(
    [
        [1.0 - 2 * _EPS, _EPS, _EPS],
        [_EPS, 1.0 - 2 * _EPS, _EPS],
        [_EPS, _EPS, 1.0 - 2 * _EPS],
    ]
)


# =============================================================================
# CONTROESEMPIO Viterbi vs argmax(gamma) — il cuore dell'esercizio.
#
# Costruzione.  Tre stati.  La transizione 1 -> 2 e' VIETATA (A[1, 2] = 0).
# Il simbolo 0 e' informativo (lo stato 1 lo emette piu' spesso degli altri),
# il simbolo 2 e' completamente NON informativo (tutti gli stati lo emettono
# con probabilita' 0.2, quindi non sposta le credenze).
#
# Osservando obs = [0, 2, 2]:
#   - al tempo 0 il marginale posteriore preferisce lo stato 1 (0.45);
#   - ai tempi 1 e 2 il marginale preferisce lo stato 2, perche' gli stati 0
#     e 2 ci finiscono con probabilita' alta (0.90 e 0.60) e sono comunque
#     molto probabili a priori;
#   - ma la traiettoria [1, 2, 2] ha probabilita' ESATTAMENTE ZERO.
# Il MAP congiunto e' [1, 0, 2]: sacrifica il secondo istante per restare
# ammissibile.
# =============================================================================

PI_CE = np.array([1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0])
A_CE = np.array(
    [
        [0.05, 0.05, 0.90],
        [0.50, 0.50, 0.00],  # <- da 1 non si puo' andare in 2
        [0.20, 0.20, 0.60],
    ]
)
B_CE = np.array(
    [
        [0.24, 0.56, 0.20],
        [0.36, 0.44, 0.20],
        [0.20, 0.60, 0.20],
    ]
)
OBS_CE = np.array([0, 2, 2])


# =============================================================================
# Oracoli indipendenti, scritti per DEFINIZIONE (enumerazione), non copiando
# l'implementazione.
# =============================================================================


def _joint_logprob(obs, states, pi, A, B):
    """log P(z_0..z_{T-1}, obs) per una traiettoria esplicita. -inf se vietata."""
    with np.errstate(divide="ignore"):
        v = np.log(pi[states[0]]) + np.log(B[states[0], obs[0]])
        for t in range(1, len(obs)):
            v += np.log(A[states[t - 1], states[t]]) + np.log(B[states[t], obs[t]])
    return float(v)


def _brute_map(obs, pi, A, B):
    """Enumera tutte le K^T traiettorie e restituisce (argmax, max log-prob)."""
    K = pi.shape[0]
    best, best_lp = None, -np.inf
    for z in itertools.product(range(K), repeat=len(obs)):
        lp = _joint_logprob(obs, z, pi, A, B)
        if lp > best_lp:
            best_lp, best = lp, z
    return np.array(best), best_lp


def _brute_gamma(obs, pi, A, B):
    """gamma per enumerazione: somma le congiunte delle traiettorie, normalizza."""
    K = pi.shape[0]
    T = len(obs)
    g = np.zeros((T, K))
    for z in itertools.product(range(K), repeat=T):
        p = pi[z[0]] * B[z[0], obs[0]]
        for t in range(1, T):
            p *= A[z[t - 1], z[t]] * B[z[t], obs[t]]
        for t in range(T):
            g[t, z[t]] += p
    return g / g.sum(axis=1, keepdims=True)


# =============================================================================
# TEST
# =============================================================================


def test_forward_alpha_normalizzata_e_shape():
    alpha, scaling = m.forward(OBS, PI, A, B)
    assert alpha.shape == (len(OBS), PI.shape[0]), (
        "alpha deve avere shape (T, K); hai restituito %s" % (alpha.shape,)
    )
    assert scaling.shape == (len(OBS),), (
        "scaling deve avere shape (T,), un fattore per istante; hai %s"
        % (scaling.shape,)
    )
    np.testing.assert_allclose(
        alpha.sum(axis=1),
        np.ones(len(OBS)),
        rtol=1e-6,
        atol=1e-9,
        err_msg=(
            "ogni riga di alpha deve sommare a 1: alpha[t] e' la distribuzione "
            "filtrata P(z_t | obs[0..t]). Se non somma a 1 non hai diviso per "
            "scaling[t], o stai restituendo l'alpha grezzo non scalato."
        ),
    )
    assert np.all(scaling > 0), "i fattori di scaling devono essere positivi"


def test_scaling_sono_predittive_one_step():
    """scaling[t] = P(obs[t] | obs[0..t-1]): il prodotto dei primi t+1 fattori
    deve dare la likelihood del prefisso, calcolata con l'oracolo brute-force."""
    _, scaling = m.forward(OBS, PI, A, B)
    for t in range(len(OBS)):
        atteso = m.forward_naive(OBS[: t + 1], PI, A, B)
        np.testing.assert_allclose(
            scaling[: t + 1].prod(),
            atteso,
            rtol=1e-6,
            atol=1e-9,
            err_msg=(
                "prod(scaling[:%d]) deve essere P(obs[0..%d]) ma non lo e'. "
                "Ogni scaling[t] deve essere la SOMMA di (alpha[t-1] @ A) * "
                "B[:, obs[t]], cioe' la predittiva a un passo." % (t + 1, t)
            ),
        )


def test_loglikelihood_oracolo_enumerazione():
    """ORACOLO: la log-likelihood del forward scalato deve coincidere con il
    logaritmo della somma esplicita su tutte le 3^6 = 729 traiettorie."""
    atteso = np.log(m.forward_naive(OBS, PI, A, B))
    ottenuto = m.log_likelihood(OBS, PI, A, B)
    np.testing.assert_allclose(
        ottenuto,
        atteso,
        rtol=1e-6,
        atol=1e-9,
        err_msg=(
            "log_likelihood non coincide con log(sum su tutte le K^T "
            "traiettorie). Cause tipiche: A trasposta (hai usato A @ p invece "
            "di p @ A nel forward), oppure hai sommato i fattori di scaling "
            "invece dei loro logaritmi."
        ),
    )


def test_backward_beta_finale_uno_e_gamma_prodotto():
    alpha, scaling = m.forward(OBS, PI, A, B)
    beta = m.backward(OBS, PI, A, B, scaling)
    assert beta.shape == alpha.shape, "beta deve avere la stessa shape di alpha, (T, K)"
    np.testing.assert_allclose(
        beta[-1],
        np.ones(PI.shape[0]),
        rtol=1e-6,
        atol=1e-9,
        err_msg="beta[T-1] deve essere il vettore di tutti 1 (condizione al bordo)",
    )
    gamma = m.posterior_marginals(OBS, PI, A, B)
    np.testing.assert_allclose(
        gamma,
        alpha * beta,
        rtol=1e-6,
        atol=1e-9,
        err_msg=(
            "con lo scaling di Rabiner deve valere gamma = alpha * beta senza "
            "dividere per P(obs): se hai dovuto normalizzare a mano, il beta "
            "non usa gli stessi fattori di scaling del forward."
        ),
    )


def test_gamma_somma_a_uno():
    """Proprieta' matematica: gamma[t] e' una distribuzione su K stati."""
    for obs in (OBS, np.array([2, 2, 2, 2]), np.array([0, 1])):
        gamma = m.posterior_marginals(obs, PI, A, B)
        assert gamma.shape == (len(obs), PI.shape[0]), "gamma deve avere shape (T, K)"
        np.testing.assert_allclose(
            gamma.sum(axis=1),
            np.ones(len(obs)),
            rtol=1e-6,
            atol=1e-9,
            err_msg=(
                "ogni riga di gamma deve sommare a 1: e' P(z_t = . | obs). "
                "Se non ci somma, o beta non e' scalato con i fattori del "
                "forward, o hai dimenticato di dividere per P(obs)."
            ),
        )
        assert np.all(gamma >= -1e-12), "gamma non puo' avere componenti negative"


def test_gamma_oracolo_enumerazione():
    """ORACOLO: gamma calcolato per definizione, sommando le congiunte."""
    atteso = _brute_gamma(OBS, PI, A, B)
    ottenuto = m.posterior_marginals(OBS, PI, A, B)
    np.testing.assert_allclose(
        ottenuto,
        atteso,
        rtol=1e-6,
        atol=1e-9,
        err_msg=(
            "gamma non coincide con la marginalizzazione esplicita su tutte le "
            "traiettorie. Se somma a 1 ma i valori sono sbagliati, il sospetto "
            "numero uno e' A trasposta nel backward (serve A @ v, non v @ A)."
        ),
    )


def test_xi_marginalizza_a_gamma():
    """Proprieta' matematica: sum_j xi[t, i, j] = gamma[t, i]."""
    xis = m.xi(OBS, PI, A, B)
    gamma = m.posterior_marginals(OBS, PI, A, B)
    K = PI.shape[0]
    assert xis.shape == (len(OBS) - 1, K, K), (
        "xi deve avere shape (T-1, K, K); hai %s" % (xis.shape,)
    )
    np.testing.assert_allclose(
        xis.sum(axis=2),
        gamma[:-1],
        rtol=1e-6,
        atol=1e-9,
        err_msg=(
            "sommando xi[t] sull'asse 2 (lo stato di ARRIVO j) si deve "
            "riottenere gamma[t]. Se invece torna sommando sull'asse 1, hai "
            "xi trasposta: la riga e' lo stato al tempo t, la colonna quello "
            "al tempo t+1."
        ),
    )
    # coerenza anche dall'altro lato: sum_i xi[t, i, j] = gamma[t+1, j]
    np.testing.assert_allclose(
        xis.sum(axis=1),
        gamma[1:],
        rtol=1e-6,
        atol=1e-9,
        err_msg="sommando xi[t] sull'asse 1 (lo stato di partenza) deve tornare gamma[t+1]",
    )


def test_viterbi_recupera_stati_quasi_deterministico():
    """Con transizioni ed emissioni quasi deterministiche, il MAP congiunto
    deve ricostruire esattamente la traiettoria latente vera."""
    rng = np.random.default_rng(7)
    stati_veri, obs = m.sample_hmm(PI_DET, A_DET, B_DET, 20, rng)
    path, _ = m.viterbi(obs, PI_DET, A_DET, B_DET)
    assert path.shape == stati_veri.shape, "il path di Viterbi deve avere shape (T,)"
    assert np.array_equal(path, stati_veri), (
        "su un HMM quasi deterministico (ciclo 0->1->2->0, emissione ~ "
        "identita') Viterbi deve recuperare la sequenza vera %s, hai ottenuto "
        "%s. Se il path e' 'ruotato' rispetto a quello vero, stai usando A "
        "trasposta nella ricorsione: serve max_i (delta[t-1, i] + log A[i, j])."
        % (stati_veri.tolist(), path.tolist())
    )


def test_viterbi_e_il_massimo_globale():
    """(1) logprob >= log-prob della traiettoria vera, per definizione di
    massimo; (2) coincide col massimo trovato per enumerazione esplicita."""
    rng = np.random.default_rng(0)
    stati_veri, obs = m.sample_hmm(PI, A, B, 6, rng)

    path, logprob = m.viterbi(obs, PI, A, B)
    lp_veri = _joint_logprob(obs, stati_veri, PI, A, B)
    assert logprob >= lp_veri - 1e-9, (
        "il path di Viterbi deve avere log P(z, obs) >= quello di QUALSIASI "
        "altra traiettoria, inclusa quella vera: %.6f < %.6f significa che "
        "non stai massimizzando." % (logprob, lp_veri)
    )

    # ORACOLO: massimo per enumerazione delle K^T traiettorie
    path_bf, lp_bf = _brute_map(obs, PI, A, B)
    np.testing.assert_allclose(
        logprob,
        lp_bf,
        rtol=1e-6,
        atol=1e-9,
        err_msg=(
            "logprob restituito da viterbi non e' il massimo vero. Deve essere "
            "log P(path, obs) CONGIUNTA (non divisa per P(obs)) e in spazio "
            "logaritmico."
        ),
    )
    assert np.array_equal(path, path_bf), (
        "il path di Viterbi %s non e' l'argmax trovato per enumerazione %s: "
        "il backtracking dei backpointer e' sbagliato."
        % (path.tolist(), path_bf.tolist())
    )
    np.testing.assert_allclose(
        logprob,
        _joint_logprob(obs, path, PI, A, B),
        rtol=1e-6,
        atol=1e-9,
        err_msg="logprob deve essere la log-prob congiunta del path che restituisci",
    )


def test_viterbi_diverso_da_argmax_gamma():
    """IL PUNTO CONCETTUALE. La sequenza degli argmax dei marginali posteriori
    NON e' la sequenza MAP: qui non e' nemmeno una sequenza legale."""
    gamma = m.posterior_marginals(OBS_CE, PI_CE, A_CE, B_CE)
    path_marginale = gamma.argmax(axis=1)
    path_viterbi, logprob_viterbi = m.viterbi(OBS_CE, PI_CE, A_CE, B_CE)

    # il controesempio deve essere davvero un controesempio
    assert not np.array_equal(path_marginale, path_viterbi), (
        "su questo HMM costruito apposta l'argmax dei marginali (%s) e il path "
        "di Viterbi (%s) DEVONO differire: se coincidono, uno dei due e' "
        "sbagliato." % (path_marginale.tolist(), path_viterbi.tolist())
    )

    # l'argmax dei marginali usa la transizione vietata 1 -> 2: prob. zero
    lp_marginale = _joint_logprob(OBS_CE, path_marginale, PI_CE, A_CE, B_CE)
    assert lp_marginale == -np.inf, (
        "l'argmax dei marginali doveva essere la traiettoria IMPOSSIBILE "
        "[1, 2, 2] (A[1,2] = 0), hai ottenuto %s con log-prob %.4f: il tuo "
        "gamma e' sbagliato." % (path_marginale.tolist(), lp_marginale)
    )
    assert logprob_viterbi > -np.inf, (
        "il path di Viterbi deve avere probabilita' positiva: se ti viene -inf "
        "stai propagando male gli zeri di A in spazio logaritmico."
    )

    # e Viterbi deve trovare il vero MAP, che l'enumerazione conferma
    path_bf, lp_bf = _brute_map(OBS_CE, PI_CE, A_CE, B_CE)
    assert np.array_equal(path_viterbi, path_bf), (
        "il MAP congiunto e' %s (verificato per enumerazione), hai restituito %s"
        % (path_bf.tolist(), path_viterbi.tolist())
    )
    np.testing.assert_allclose(logprob_viterbi, lp_bf, rtol=1e-6, atol=1e-9)

    # ogni singolo istante: il marginale e' comunque calcolato bene
    np.testing.assert_allclose(
        gamma,
        _brute_gamma(OBS_CE, PI_CE, A_CE, B_CE),
        rtol=1e-6,
        atol=1e-9,
        err_msg="gamma sul controesempio non coincide con l'enumerazione esplicita",
    )


def test_baum_welch_loglik_monotona():
    """Proprieta' matematica: EM non puo' far scendere la log-likelihood."""
    rng = np.random.default_rng(11)
    _, obs = m.sample_hmm(PI, A, B, 80, rng)
    res = m.baum_welch(obs, K=3, M=3, n_iter=40, tol=1e-9, seed=1)

    hist = np.asarray(res["loglik_history"])
    assert hist.ndim == 1 and hist.size >= 2, (
        "loglik_history deve essere una sequenza 1-D con almeno il valore "
        "iniziale e uno dopo il primo aggiornamento"
    )
    assert res["n_iter"] == hist.size - 1, (
        "n_iter (%d) deve essere il numero di aggiornamenti effettuati, cioe' "
        "len(loglik_history) - 1 (%d)" % (res["n_iter"], hist.size - 1)
    )
    diffs = np.diff(hist)
    assert np.all(diffs >= -1e-9), (
        "la log-likelihood di Baum-Welch deve essere non decrescente; il "
        "decremento peggiore e' %.3e all'iterazione %d. Cause tipiche: E-step "
        "e M-step calcolati con parametri diversi, oppure denominatore di A "
        "sommato fino a T-1 invece che a T-2."
        % (diffs.min(), int(np.argmin(diffs)))
    )
    np.testing.assert_allclose(
        hist[-1],
        m.log_likelihood(obs, res["pi"], res["A"], res["B"]),
        rtol=1e-6,
        atol=1e-9,
        err_msg="l'ultimo valore di loglik_history deve essere quello dei parametri restituiti",
    )


def test_baum_welch_righe_normalizzate_ogni_iterazione():
    """Dopo OGNI iterazione i parametri devono restare distribuzioni valide."""
    rng = np.random.default_rng(23)
    _, obs = m.sample_hmm(PI, A, B, 50, rng)
    for it in range(1, 7):
        res = m.baum_welch(obs, K=3, M=4, n_iter=it, tol=0.0, seed=2)
        pi_h, A_h, B_h = res["pi"], res["A"], res["B"]
        assert pi_h.shape == (3,) and A_h.shape == (3, 3) and B_h.shape == (3, 4), (
            "shape sbagliate dopo %d iterazioni: pi (K,), A (K,K), B (K,M)" % it
        )
        np.testing.assert_allclose(
            pi_h.sum(), 1.0, rtol=1e-6, atol=1e-9,
            err_msg="pi deve sommare a 1 dopo %d iterazioni" % it,
        )
        np.testing.assert_allclose(
            A_h.sum(axis=1), np.ones(3), rtol=1e-6, atol=1e-9,
            err_msg=(
                "le RIGHE di A devono sommare a 1 dopo %d iterazioni (A[i,:] e' "
                "P(z_t = . | z_{t-1} = i)). Se sommano a 1 le colonne, l'M-step "
                "normalizza lungo l'asse sbagliato." % it
            ),
        )
        np.testing.assert_allclose(
            B_h.sum(axis=1), np.ones(3), rtol=1e-6, atol=1e-9,
            err_msg=(
                "le RIGHE di B devono sommare a 1 dopo %d iterazioni (B[k,:] e' "
                "la distribuzione di emissione dello stato k sui M simboli)." % it
            ),
        )
        assert np.all(A_h >= -1e-12) and np.all(B_h >= -1e-12) and np.all(pi_h >= -1e-12), (
            "nessun parametro puo' diventare negativo"
        )


def test_caso_limite_T_uguale_uno():
    """Caso degenere: una sola osservazione. Nessuna transizione in gioco."""
    obs = np.array([1])
    K = PI.shape[0]

    alpha, scaling = m.forward(obs, PI, A, B)
    assert alpha.shape == (1, K) and scaling.shape == (1,), (
        "con T=1 alpha deve essere (1, K) e scaling (1,)"
    )
    atteso = PI * B[:, 1]
    np.testing.assert_allclose(
        scaling[0], atteso.sum(), rtol=1e-6, atol=1e-9,
        err_msg="con T=1 scaling[0] = P(obs[0]) = sum_k pi[k] B[k, obs[0]]",
    )
    np.testing.assert_allclose(
        alpha[0], atteso / atteso.sum(), rtol=1e-6, atol=1e-9,
        err_msg="con T=1 alpha[0] e' pi * B[:, obs[0]] normalizzato: A non entra affatto",
    )

    beta = m.backward(obs, PI, A, B, scaling)
    np.testing.assert_allclose(
        beta[0], np.ones(K), rtol=1e-6, atol=1e-9,
        err_msg="con T=1 beta e' tutto 1: il ciclo all'indietro non deve girare nemmeno una volta",
    )

    np.testing.assert_allclose(
        m.log_likelihood(obs, PI, A, B),
        np.log(m.forward_naive(obs, PI, A, B)),
        rtol=1e-6, atol=1e-9,
        err_msg="con T=1 la log-likelihood e' log(sum_k pi[k] B[k, obs[0]])",
    )

    gamma = m.posterior_marginals(obs, PI, A, B)
    np.testing.assert_allclose(
        gamma[0], atteso / atteso.sum(), rtol=1e-6, atol=1e-9,
        err_msg="con T=1 gamma coincide con alpha",
    )

    xis = m.xi(obs, PI, A, B)
    assert xis.shape == (0, K, K), (
        "con T=1 non esistono coppie (z_t, z_{t+1}): xi deve avere shape "
        "(0, K, K), hai %s" % (xis.shape,)
    )

    path, logprob = m.viterbi(obs, PI, A, B)
    assert path.shape == (1,) and path[0] == int(np.argmax(atteso)), (
        "con T=1 il MAP e' semplicemente argmax_k pi[k] B[k, obs[0]] = %d, hai %s"
        % (int(np.argmax(atteso)), path.tolist())
    )
    np.testing.assert_allclose(
        logprob, np.log(atteso.max()), rtol=1e-6, atol=1e-9,
        err_msg="con T=1 logprob = log(max_k pi[k] B[k, obs[0]])",
    )

    res = m.baum_welch(obs, K=3, M=3, n_iter=5, tol=1e-9, seed=4)
    np.testing.assert_allclose(
        res["A"].sum(axis=1), np.ones(3), rtol=1e-6, atol=1e-9,
        err_msg=(
            "con T=1 non c'e' nessuna transizione da stimare: A va lasciata "
            "invariata (righe ancora normalizzate), non divisa per zero."
        ),
    )
    assert np.all(np.isfinite(res["A"])), (
        "con T=1 il denominatore dell'M-step di A e' vuoto: se non lo proteggi "
        "ottieni NaN"
    )
    assert np.all(np.diff(np.asarray(res["loglik_history"])) >= -1e-9), (
        "anche con T=1 la log-likelihood deve essere non decrescente"
    )
