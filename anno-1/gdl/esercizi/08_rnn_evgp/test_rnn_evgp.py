"""Test di autovalutazione - GDL17 "Information Propagation in Deep Networks".

Esecuzione:
    pytest test_rnn_evgp.py -v                # sullo skeleton
    GDL_SOL=1 pytest test_rnn_evgp.py -v      # sulla soluzione di riferimento
"""

import os, sys, pathlib, importlib

HERE = pathlib.Path(__file__).parent
if os.environ.get("GDL_SOL"):
    sys.path.insert(0, str(HERE / "soluzione"))
    m = importlib.import_module("rnn_evgp_sol")
else:
    sys.path.insert(0, str(HERE))
    m = importlib.import_module("rnn_evgp")

import numpy as np
import pytest
from numpy.testing import assert_allclose


# ---------------------------------------------------------------------------
# helper locali ai test (non fanno parte dell'API da implementare)
# ---------------------------------------------------------------------------

def _flat(grads):
    """Concatena i gradienti dei parametri in un vettore, ordine PARAM_KEYS."""
    return np.concatenate(
        [np.asarray(grads["d" + k], dtype=float).ravel() for k in m.PARAM_KEYS]
    )


def _loss_of(params, X, targets):
    """Loss quadratica totale della RNN con quei parametri (usa solo il forward)."""
    _, Y, _ = m.rnn_forward(
        X, params["Wxh"], params["Whh"], params["bh"], params["Why"], params["by"]
    )
    return m.mse_loss_and_grad(Y, targets)[0]


def _full_grads(params, X, targets):
    """BPTT completo: forward + backward con dY = Y - targets su ogni timestep."""
    _, Y, cache = m.rnn_forward(
        X, params["Wxh"], params["Whh"], params["bh"], params["Why"], params["by"]
    )
    _, dY = m.mse_loss_and_grad(Y, targets)
    return m.rnn_backward(dY, cache, params["Wxh"], params["Whh"], params["Why"])


def _loss_from_state(v, t, X, targets, p):
    """Loss TOTALE riscritta come funzione dello stato h_t, con h_t = v.

    Serve come oracolo indipendente per ``dh_per_step[t]``. I termini di loss
    che dipendono da h_t sono quelli dei timestep t-1, t, ..., T-1: il primo
    perche' Y[t-1] = Why h_t + by, gli altri perche' h_t entra nella
    ricorrenza. I termini precedenti non dipendono da h_t e non contribuiscono
    al gradiente, quindi si possono omettere.

    Questo helper NON usa nessuna funzione dell'esercizio: e' una riscrittura
    diretta della definizione di RNN.
    """
    v = np.asarray(v, dtype=float)
    T = X.shape[0]
    total = 0.0
    if t >= 1:
        y = p["Why"] @ v + p["by"]
        total += 0.5 * float(np.sum((y - targets[t - 1]) ** 2))
    h = v.copy()
    for i in range(t, T):
        h = np.tanh(p["Whh"] @ h + p["Wxh"] @ X[i] + p["bh"])
        y = p["Why"] @ h + p["by"]
        total += 0.5 * float(np.sum((y - targets[i]) ** 2))
    return total


# ---------------------------------------------------------------------------
# 1. tanh_prime: convenzione e correttezza
# ---------------------------------------------------------------------------

def test_tanh_prime_convenzione_pre_attivato_e_differenze_finite():
    """tanh_prime riceve il PRE-attivato: deve valere 1 - tanh(a)^2.

    Il test smaschera le due confusioni tipiche: passare h = tanh(a) al posto
    di a (si otterrebbe 1 - tanh(h)^2), oppure scrivere 1 - a^2.
    """
    a = np.linspace(-3.0, 3.0, 25)
    got = m.tanh_prime(a)

    assert np.shape(got) == a.shape, (
        f"tanh_prime deve conservare la shape: attesa {a.shape}, ottenuta {np.shape(got)}"
    )

    eps = 1e-6
    fd = (np.tanh(a + eps) - np.tanh(a - eps)) / (2.0 * eps)
    assert_allclose(
        got, fd, rtol=1e-6, atol=1e-9,
        err_msg="tanh_prime non coincide con la derivata numerica di tanh: "
                "la convenzione e' 1 - tanh(a)^2 sul PRE-attivato a",
    )

    # controprova esplicita sulla convenzione sbagliata
    sbagliata = 1.0 - np.tanh(np.tanh(a)) ** 2
    assert np.max(np.abs(got - sbagliata)) > 0.1, (
        "stai passando lo stato h = tanh(a) invece del pre-attivato a: "
        "1 - tanh(h)^2 non e' la derivata di tanh in a"
    )

    assert np.all(got > 0.0) and np.all(got <= 1.0 + 1e-12), (
        "tanh' ha valori in (0, 1]: e' proprio questo che fa vanishing, "
        "perche' la jacobiana ricorrente viene sempre attenuata"
    )
    assert_allclose(m.tanh_prime(np.array([0.0])), np.array([1.0]), rtol=1e-12,
                    err_msg="tanh'(0) deve valere esattamente 1")


# ---------------------------------------------------------------------------
# 2. rnn_forward contro uno srotolamento esplicito, scalare
# ---------------------------------------------------------------------------

def test_rnn_forward_contro_srotolamento_scalare():
    """Oracolo indipendente: la ricorrenza scritta a mano, componente per
    componente, su tre timestep con matrici piccole e note."""
    Wxh = np.array([[1.0, 0.0], [0.0, 2.0]])
    Whh = np.array([[0.5, -0.25], [0.0, 0.5]])
    bh = np.array([0.1, -0.1])
    Why = np.array([[1.0, -1.0]])
    by = np.array([0.5])
    X = np.array([[1.0, 0.0], [0.0, 1.0], [-1.0, 1.0]])

    H, Y, cache = m.rnn_forward(X, Wxh, Whh, bh, Why, by)

    assert H.shape == (4, 2), f"H deve avere shape (T+1, Hdim) = (4, 2), ottenuta {H.shape}"
    assert Y.shape == (3, 1), f"Y deve avere shape (T, O) = (3, 1), ottenuta {Y.shape}"
    assert_allclose(H[0], np.zeros(2), atol=0.0,
                    err_msg="H[0] deve essere lo stato iniziale NULLO")

    # srotolamento a mano, aritmetica scalare
    h0, h1 = 0.0, 0.0
    for i in range(3):
        a0 = 0.5 * h0 - 0.25 * h1 + 1.0 * X[i, 0] + 0.0 * X[i, 1] + 0.1
        a1 = 0.0 * h0 + 0.5 * h1 + 0.0 * X[i, 0] + 2.0 * X[i, 1] - 0.1
        h0, h1 = np.tanh(a0), np.tanh(a1)
        y = 1.0 * h0 - 1.0 * h1 + 0.5
        assert_allclose(
            H[i + 1], np.array([h0, h1]), rtol=1e-12, atol=1e-14,
            err_msg=f"stato al passo {i} sbagliato: controlla che sia "
                    "Whh @ H[i] (stato PRECEDENTE) e non Whh @ H[i+1]",
        )
        assert_allclose(
            Y[i], np.array([y]), rtol=1e-12, atol=1e-14,
            err_msg=f"output al passo {i} sbagliato: Y[i] = Why @ H[i+1] + by, "
                    "cioe' usa lo stato DOPO il timestep i",
        )

    A = cache["A"]
    assert A.shape == (3, 2), f"cache['A'] deve avere shape (T, Hdim) = (3, 2), ottenuta {A.shape}"
    assert_allclose(
        np.tanh(A), H[1:], rtol=1e-12, atol=1e-14,
        err_msg="cache['A'] deve contenere i PRE-attivati, con H[i+1] = tanh(A[i]): "
                "se ci hai messo gli stati il backward sara' sbagliato",
    )


# ---------------------------------------------------------------------------
# 3. GRADIENT CHECK - il test principale
# ---------------------------------------------------------------------------

def test_gradient_check_bptt_completo():
    """Tutti i gradienti di rnn_backward contro differenze finite centrali.

    E' il test che decide se il BPTT e' giusto. Se fallisce solo su dWhh, il
    bug e' quasi sempre nell'accumulo lungo il tempo (dWhh usa H[i], lo stato
    PRECEDENTE) o nella mancata somma dei contributi dei timestep successivi.
    """
    X, targets = m.make_copy_task(7, 3, seed=11)
    D, O = X.shape[1], targets.shape[1]

    configurazioni = [
        dict(seed=3, rho=0.9, in_scale=0.6, out_scale=0.7, bias_scale=0.3),
        dict(seed=17, rho=1.5, in_scale=0.4, out_scale=0.5, bias_scale=0.2),
    ]
    for cfg in configurazioni:
        params = m.init_params(D, 4, O, **cfg)
        theta = m.pack_params(params)

        def f(th):
            return _loss_of(m.unpack_params(th, params), X, targets)

        num = m.numerical_gradient(f, theta, eps=1e-5)
        ana = _flat(_full_grads(params, X, targets))

        assert ana.shape == num.shape, (
            f"il gradiente analitico ha {ana.shape} elementi, i parametri {num.shape}: "
            "qualche gradiente ha shape diversa dal parametro corrispondente"
        )
        assert_allclose(
            ana, num, rtol=1e-5, atol=1e-8,
            err_msg=f"gradient check FALLITO (config {cfg}): il BPTT non calcola "
                    "il gradiente della loss. Controlla l'accumulo di dWhh/dWxh/dbh "
                    "e il termine Why^T dY[i] iniettato su ogni timestep",
        )

    # controllo per singolo parametro, per localizzare il bug
    params = m.init_params(D, 4, O, seed=3, rho=0.9, in_scale=0.6, out_scale=0.7,
                           bias_scale=0.3)
    g = _full_grads(params, X, targets)
    for k in m.PARAM_KEYS:
        base = {kk: vv.copy() for kk, vv in params.items()}

        def fk(v, k=k, base=base):
            p = dict(base)
            p[k] = v
            return _loss_of(p, X, targets)

        num_k = m.numerical_gradient(fk, params[k], eps=1e-5)
        assert np.shape(g["d" + k]) == np.shape(params[k]), (
            f"d{k} deve avere la stessa shape di {k}: attesa {np.shape(params[k])}, "
            f"ottenuta {np.shape(g['d' + k])}"
        )
        assert_allclose(g["d" + k], num_k, rtol=1e-5, atol=1e-8,
                        err_msg=f"il gradiente d{k} non coincide con quello numerico")


# ---------------------------------------------------------------------------
# 4. dh_per_step contro il gradiente numerico rispetto allo stato
# ---------------------------------------------------------------------------

def test_dh_per_step_contro_gradiente_numerico_sullo_stato():
    """dh_per_step[t] deve essere dL/dh_t, con L la loss TOTALE.

    Oracolo: si riscrive la loss come funzione di h_t (helper `_loss_from_state`,
    che non usa nulla dell'esercizio) e si deriva per differenze finite. Senza
    questo controllo la curva del vanishing potrebbe essere una curva di
    qualcos'altro.
    """
    T = 8
    X, targets = m.make_copy_task(T, 3, seed=5)
    D, O = X.shape[1], targets.shape[1]
    params = m.init_params(D, 4, O, seed=23, rho=1.1, in_scale=0.5, out_scale=0.6,
                           bias_scale=0.2)

    g = _full_grads(params, X, targets)
    dh = g["dh_per_step"]

    assert dh.shape == (T + 1, 4), (
        f"dh_per_step deve avere shape (T+1, Hdim) = ({T + 1}, 4), ottenuta {dh.shape}"
    )
    assert_allclose(g["dh0"], dh[0], rtol=1e-12, atol=1e-14,
                    err_msg="dh0 e dh_per_step[0] sono lo stesso oggetto: "
                            "il gradiente rispetto allo stato iniziale")

    for t in range(T + 1):
        num = m.numerical_gradient(
            lambda v, t=t: _loss_from_state(v, t, X, targets, params),
            _state_at(params, X, t),
            eps=1e-5,
        )
        assert_allclose(
            dh[t], num, rtol=1e-5, atol=1e-8,
            err_msg=f"dh_per_step[{t}] non e' dL/dh_{t}. Ricorda che h_t influenza "
                    f"anche l'output Y[{t - 1}] (oltre a tutto il futuro): se hai "
                    "dimenticato il termine Why^T dY il gradiente e' sfasato di uno",
        )


def _state_at(params, X, t):
    """Stato H[t] della RNN (ricalcolato a mano, senza usare rnn_forward)."""
    h = np.zeros(params["Whh"].shape[0])
    for i in range(t):
        h = np.tanh(params["Whh"] @ h + params["Wxh"] @ X[i] + params["bh"])
    return h


# ---------------------------------------------------------------------------
# 5. VANISHING: decadimento geometrico con rho(Whh) = 0.5
# ---------------------------------------------------------------------------

def test_vanishing_decadimento_geometrico_con_raggio_spettrale_basso():
    """Con rho(Whh) = 0.5 il gradiente decade esponenzialmente andando indietro.

    Whh e' 0.5 volte una matrice ortogonale, quindi TUTTI gli autovalori hanno
    modulo 0.5 e la norma viene moltiplicata esattamente per 0.5 a ogni passo
    lineare. Con input piccoli tanh lavora nel regime quasi lineare
    (tanh' ~ 1) e il rapporto fra norme consecutive deve essere praticamente
    costante e pari al raggio spettrale.
    """
    T, Hdim, D, O = 20, 6, 3, 2
    X = 0.05 * np.random.default_rng(5).standard_normal((T, D))
    targets = np.zeros((T, O))
    params = m.init_params(D, Hdim, O, seed=5, rho=0.5, in_scale=0.5,
                           out_scale=0.5, bias_scale=0.0)
    rho = m.spectral_radius(params["Whh"])
    assert abs(rho - 0.5) < 1e-9, f"la matrice di test deve avere rho = 0.5, misurato {rho}"

    norms = m.gradient_norms_over_time(X, targets, params)
    assert norms.shape == (T + 1,), (
        f"gradient_norms_over_time deve restituire shape (T+1,) = ({T + 1},), "
        f"ottenuta {norms.shape}"
    )
    assert np.all(norms > 0.0), "nessuna norma deve essere nulla in questo regime"

    # (i) rapporto fra norme consecutive: costante e < 1
    r1 = norms[:-1] / norms[1:]
    assert np.all(r1 < 0.9), (
        f"andando indietro il gradiente deve ATTENUARSI: rapporto massimo {r1.max():.4f}"
    )
    assert r1.max() - r1.min() < 0.02, (
        f"il decadimento deve essere geometrico, quindi il rapporto deve essere "
        f"quasi costante: varia fra {r1.min():.4f} e {r1.max():.4f}"
    )

    # (ii) rapporto a distanza fissa d = 5: costante, e pari a rho^5
    d = 5
    rd = norms[:-d] / norms[d:]
    assert rd.std() / rd.mean() < 0.02, (
        "a distanza fissa il rapporto fra le norme deve essere approssimativamente "
        f"costante (decadimento esponenziale); coefficiente di variazione {rd.std() / rd.mean():.4f}"
    )
    assert_allclose(rd.mean(), rho ** d, rtol=0.05,
                    err_msg=f"il rapporto a distanza {d} deve valere circa rho^{d} = "
                            f"{rho ** d:.6f}, misurato {rd.mean():.6f}")

    # (iii) tasso di decadimento stimato contro il raggio spettrale teorico
    rate = (norms[0] / norms[T]) ** (1.0 / T)
    assert rate < 1.0, "il tasso di decadimento deve essere < 1: questo E' il vanishing"
    assert_allclose(rate, rho, rtol=0.02,
                    err_msg=f"il tasso di decadimento stimato ({rate:.6f}) deve essere "
                            f"vicino al raggio spettrale di Whh ({rho:.6f})")

    # (iv) l'effetto complessivo: 20 passi, sei ordini di grandezza persi
    assert norms[0] / norms[T] < 1e-5, (
        f"dopo {T} passi il gradiente sullo stato iniziale deve essere di ordini di "
        f"grandezza piu' piccolo; rapporto misurato {norms[0] / norms[T]:.3e}"
    )


# ---------------------------------------------------------------------------
# 6. IL PUNTO SOTTILE: rho = 1 e il gradiente vanisce lo stesso
# ---------------------------------------------------------------------------

def test_raggio_spettrale_unitario_ma_gradiente_vanisce_lo_stesso():
    """rho(Whh) = 1 e' condizione NECESSARIA ma NON SUFFICIENTE per propagare.

    Whh e' esattamente ortogonale: la parte lineare della ricorrenza conserva
    la norma, punto per punto, non solo asintoticamente. Nonostante questo il
    gradiente decade, perche' la jacobiana vera e' diag(tanh'(a_t)) Whh e
    tanh' <= 1 attenua a ogni passo. Il fattore che manca al criterio
    spettrale e' proprio la saturazione della non linearita'.
    """
    T, Hdim, D, O = 20, 6, 3, 2
    X = 0.8 * np.random.default_rng(5).standard_normal((T, D))
    targets = np.zeros((T, O))
    params = m.init_params(D, Hdim, O, seed=5, rho=1.0, in_scale=0.5,
                           out_scale=0.5, bias_scale=0.0)
    Whh = params["Whh"]

    rho = m.spectral_radius(Whh)
    assert_allclose(rho, 1.0, rtol=1e-9,
                    err_msg=f"la matrice di test deve essere al confine critico rho = 1, "
                            f"misurato {rho}")

    # la parte LINEARE conserva la norma esattamente: tutto il decadimento che
    # osserveremo e' attribuibile a tanh', non a Whh
    v = np.random.default_rng(1).standard_normal(Hdim)
    assert_allclose(np.linalg.norm(Whh.T @ v), np.linalg.norm(v), rtol=1e-10,
                    err_msg="Whh di test deve essere ortogonale (norma conservata)")

    Hstati, _, cache = m.rnn_forward(X, params["Wxh"], Whh, params["bh"],
                                     params["Why"], params["by"])
    d = m.tanh_prime(cache["A"])
    assert np.all(d <= 1.0 + 1e-12), "tanh' non puo' superare 1"
    assert d.max() < 1.0, (
        "in questo regime tanh deve essere almeno un po' saturata: se tanh' fosse "
        "identicamente 1 il gradiente si conserverebbe e il test perderebbe senso"
    )

    norms = m.gradient_norms_over_time(X, targets, params)
    assert np.all(np.diff(norms) > 0.0), (
        "le norme devono crescere con t, cioe' DECRESCERE andando indietro nel "
        "tempo: con Whh ortogonale ||dh_{t-1}|| = ||tanh'(a_t) * dh_t|| < ||dh_t|| "
        "a ogni singolo passo"
    )
    assert norms[0] / norms[T] < 1e-3, (
        f"anche a raggio spettrale 1 il gradiente deve vanire: rapporto misurato "
        f"{norms[0] / norms[T]:.3e}. Il raggio spettrale e' condizione necessaria, "
        "non sufficiente"
    )

    # il prodotto delle jacobiane vere collassa, anche se rho(Whh) = 1
    jp = m.jacobian_product_spectral_radius(Whh, Hstati, cache)
    assert jp.shape == (T,), f"jacobian_product_spectral_radius deve avere shape (T,), ottenuta {jp.shape}"
    assert jp[-1] < 0.5 * jp[0], (
        f"il raggio spettrale del prodotto cumulativo delle jacobiane deve collassare "
        f"al crescere della distanza: {jp[0]:.4f} -> {jp[-1]:.4e}"
    )


# ---------------------------------------------------------------------------
# 7. EXPLODING + clipping
# ---------------------------------------------------------------------------

def test_exploding_gradient_e_clipping_riporta_sotto_soglia():
    """Con rho(Whh) = 2 e stato vicino all'origine il gradiente raddoppia a ogni
    passo all'indietro; clip_gradients lo riporta esattamente a max_norm."""
    T, Hdim, D, O = 15, 6, 3, 2
    # input minuscoli: lo stato resta vicino all'origine, dove tanh e' quasi
    # lineare (tanh' ~ 1) e non c'e' saturazione a frenare l'esplosione
    X = 1e-6 * np.random.default_rng(5).standard_normal((T, D))
    targets = np.zeros((T, O))
    params = m.init_params(D, Hdim, O, seed=5, rho=2.0, in_scale=0.5,
                           out_scale=0.5, bias_scale=0.0)
    rho = m.spectral_radius(params["Whh"])
    assert abs(rho - 2.0) < 1e-9, f"la matrice di test deve avere rho = 2, misurato {rho}"

    norms = m.gradient_norms_over_time(X, targets, params)
    assert np.all(np.diff(norms) < 0.0), (
        "andando indietro nel tempo le norme devono CRESCERE (norms[t] > norms[t+1]): "
        "e' l'exploding gradient"
    )
    rate = (norms[0] / norms[T]) ** (1.0 / T)
    assert_allclose(rate, rho, rtol=0.01,
                    err_msg=f"il tasso di crescita ({rate:.6f}) deve essere circa il "
                            f"raggio spettrale ({rho:.6f})")
    assert norms[0] / norms[T] > 1e4, (
        f"su {T} passi ci si aspetta una crescita di circa 2^{T}; misurata "
        f"{norms[0] / norms[T]:.3e}"
    )

    # sui parametri: gradienti enormi, clipping globale a max_norm
    grads = _full_grads(params, X, np.ones((T, O)))
    solo_params = {"d" + k: grads["d" + k] for k in m.PARAM_KEYS}
    max_norm = 1.0
    clipped, total = m.clip_gradients(solo_params, max_norm)

    atteso = float(np.linalg.norm(_flat(solo_params)))
    assert_allclose(total, atteso, rtol=1e-10,
                    err_msg="total_norm deve essere la norma L2 di TUTTI i gradienti "
                            "concatenati, calcolata PRIMA del clipping")
    assert total > max_norm, (
        f"il test ha senso solo se il gradiente supera la soglia; norma {total:.3e}"
    )
    nuova = float(np.linalg.norm(_flat(clipped)))
    assert_allclose(nuova, max_norm, rtol=1e-10,
                    err_msg=f"dopo il clipping la norma globale deve valere esattamente "
                            f"max_norm = {max_norm}, misurata {nuova}")


# ---------------------------------------------------------------------------
# 8. Proprieta' del clipping: direzione preservata, no-op sotto soglia
# ---------------------------------------------------------------------------

def test_clipping_preserva_la_direzione_e_non_agisce_sotto_soglia():
    """Il clipping globale e' un riscalamento con UN solo scalare: la direzione
    nello spazio dei parametri e' invariata (coseno = 1). Sotto soglia non deve
    toccare nulla."""
    rng = np.random.default_rng(31)
    grads = {
        "dWxh": rng.standard_normal((4, 3)) * 10.0,
        "dWhh": rng.standard_normal((4, 4)) * 10.0,
        "dbh": rng.standard_normal(4) * 10.0,
        "dWhy": rng.standard_normal((2, 4)) * 10.0,
        "dby": rng.standard_normal(2) * 10.0,
    }
    originali = {k: v.copy() for k, v in grads.items()}
    v0 = _flat(grads)

    clipped, total = m.clip_gradients(grads, 1.0)
    v1 = _flat(clipped)

    assert set(clipped.keys()) == set(grads.keys()), (
        "clip_gradients deve restituire le stesse chiavi che riceve"
    )
    for k in grads:
        assert np.shape(clipped[k]) == np.shape(grads[k]), f"shape alterata su {k}"
        assert np.array_equal(grads[k], originali[k]), (
            f"clip_gradients non deve modificare il dizionario in ingresso (chiave {k})"
        )

    coseno = float(v1 @ v0 / (np.linalg.norm(v1) * np.linalg.norm(v0)))
    assert_allclose(coseno, 1.0, rtol=0, atol=1e-12,
                    err_msg=f"il clipping deve preservare la DIREZIONE del gradiente "
                            f"(coseno = 1), misurato {coseno}. Se stai clippando "
                            "componente per componente la direzione cambia")
    assert_allclose(np.linalg.norm(v1), 1.0, rtol=1e-12,
                    err_msg="dopo il clipping la norma deve essere esattamente max_norm")

    # sotto soglia: nessuna modifica, e total_norm resta la norma vera
    clipped2, total2 = m.clip_gradients(grads, 1e6)
    assert_allclose(total2, total, rtol=1e-12,
                    err_msg="total_norm non dipende da max_norm: e' sempre la norma "
                            "PRIMA del clipping")
    for k in grads:
        assert_allclose(clipped2[k], grads[k], rtol=1e-14, atol=0.0,
                        err_msg=f"con norma sotto soglia il gradiente {k} deve restare "
                                "identico: nessun riscalamento")

    # caso degenere: gradiente nullo, nessuna divisione per zero
    zeri = {k: np.zeros_like(v) for k, v in grads.items()}
    z_clip, z_total = m.clip_gradients(zeri, 1.0)
    assert z_total == 0.0, "la norma di un gradiente nullo e' 0"
    assert all(np.all(z_clip[k] == 0.0) for k in zeri), (
        "un gradiente nullo deve restare nullo (attenzione alla divisione per zero)"
    )


# ---------------------------------------------------------------------------
# 9. BPTT troncato con k2 = T coincide con il BPTT completo
# ---------------------------------------------------------------------------

def test_bptt_troncato_con_k2_uguale_T_coincide_con_bptt_completo():
    """Se non si tronca mai, spezzare la sequenza in blocchi non cambia nulla:
    la loss e' una somma sui timestep e il gradiente e' lineare nella loss."""
    T = 12
    X, targets = m.make_copy_task(T, 4, seed=21)
    D, O = X.shape[1], targets.shape[1]
    params = m.init_params(D, 5, O, seed=9, rho=1.0, in_scale=0.4, out_scale=0.5,
                           bias_scale=0.1)

    full = _full_grads(params, X, targets)
    loss_attesa = _loss_of(params, X, targets)

    for k1 in (1, 3, 5, T):
        g = m.bptt_truncated(X, targets, params, k1, T)
        for k in m.PARAM_KEYS:
            assert_allclose(
                g["d" + k], full["d" + k], rtol=1e-10, atol=1e-12,
                err_msg=f"con k2 = T il BPTT troncato deve coincidere ESATTAMENTE con "
                        f"quello completo (k1 = {k1}, parametro {k}): se non torna, "
                        "o i blocchi non coprono tutti i timestep oppure qualche "
                        "termine di loss viene contato due volte",
            )
        assert_allclose(g["loss"], loss_attesa, rtol=1e-12,
                        err_msg="la loss riportata e' quella dell'intera sequenza, "
                                "non quella di un blocco")

    # k1 = 5 non divide T = 12: l'ultimo blocco e' piu' corto e va gestito
    g = m.bptt_truncated(X, targets, params, 5, T)
    assert_allclose(_flat(g), _flat(full), rtol=1e-10, atol=1e-12,
                    err_msg="con k1 che non divide T l'ultimo blocco e' parziale: "
                            "deve comunque essere processato per intero")


# ---------------------------------------------------------------------------
# 10. Il BIAS del troncamento cresce al diminuire di k2
# ---------------------------------------------------------------------------

def test_bptt_troncato_bias_cresce_al_diminuire_di_k2():
    """Il troncamento non e' rumore: e' un errore sistematico che cancella
    esattamente i cammini lunghi, cioe' le dipendenze a lungo termine."""
    T = 12
    X, targets = m.make_copy_task(T, 4, seed=21)
    D, O = X.shape[1], targets.shape[1]
    params = m.init_params(D, 5, O, seed=9, rho=1.0, in_scale=0.4, out_scale=0.5,
                           bias_scale=0.1)

    riferimento = _flat(_full_grads(params, X, targets))
    scala = float(np.linalg.norm(riferimento))
    assert scala > 0.0, "gradiente di riferimento nullo: il test non direbbe nulla"

    ks = [1, 2, 3, 4, 6, 8, 10, T]
    errori = []
    for k2 in ks:
        g = m.bptt_truncated(X, targets, params, 1, k2)
        errori.append(float(np.linalg.norm(_flat(g) - riferimento)) / scala)

    assert errori[-1] < 1e-10, (
        f"con k2 = T l'errore deve essere nullo, misurato {errori[-1]:.3e}"
    )
    assert errori[0] > 0.05, (
        f"con k2 = 1 il gradiente deve essere sensibilmente diverso da quello vero "
        f"(errore relativo {errori[0]:.4f}): se e' ~0 non stai troncando nulla"
    )
    diffs = np.diff(errori)
    assert np.all(diffs < 0.0), (
        "l'errore di troncamento deve DIMINUIRE monotonamente al crescere di k2; "
        f"errori misurati {[round(e, 4) for e in errori]}"
    )

    # k2 < k1 non ha senso in BPTT(k1, k2)
    with pytest.raises(ValueError):
        m.bptt_truncated(X, targets, params, 4, 2)


# ---------------------------------------------------------------------------
# 11. Caso limite: T = 1
# ---------------------------------------------------------------------------

def test_caso_limite_sequenza_di_lunghezza_uno():
    """Con T = 1 non c'e' ricorrenza: dWhh deve essere ESATTAMENTE nullo perche'
    lo stato precedente e' h_0 = 0, e dWhh accumula outer(da, h_0)."""
    X = np.array([[0.3, -0.7, 1.1]])
    targets = np.array([[0.2, -0.4]])
    params = m.init_params(3, 4, 2, seed=2, rho=0.8, in_scale=0.5, out_scale=0.5,
                           bias_scale=0.2)

    H, Y, cache = m.rnn_forward(X, params["Wxh"], params["Whh"], params["bh"],
                                params["Why"], params["by"])
    assert H.shape == (2, 4), f"con T=1, H deve avere shape (2, Hdim), ottenuta {H.shape}"
    assert Y.shape == (1, 2), f"con T=1, Y deve avere shape (1, O), ottenuta {Y.shape}"
    assert cache["A"].shape == (1, 4), "cache['A'] deve avere shape (T, Hdim) = (1, 4)"

    g = _full_grads(params, X, targets)
    assert g["dWhh"].shape == params["Whh"].shape
    assert np.all(g["dWhh"] == 0.0), (
        "con T = 1 il gradiente su Whh e' identicamente nullo: l'unico prodotto "
        "Whh @ h e' con h_0 = 0, quindi Whh non influenza la loss"
    )
    assert g["dh_per_step"].shape == (2, 4), (
        f"dh_per_step deve avere shape (2, Hdim), ottenuta {g['dh_per_step'].shape}"
    )
    assert_allclose(g["dh0"], g["dh_per_step"][0], rtol=1e-12, atol=1e-14)

    # gradient check anche qui
    theta = m.pack_params(params)
    num = m.numerical_gradient(lambda th: _loss_of(m.unpack_params(th, params), X, targets),
                               theta, eps=1e-5)
    assert_allclose(_flat(g), num, rtol=1e-5, atol=1e-8,
                    err_msg="gradient check fallito nel caso degenere T = 1")

    norms = m.gradient_norms_over_time(X, targets, params)
    assert norms.shape == (2,), f"con T=1 la curva ha 2 punti, ottenuta {norms.shape}"
    assert norms[1] > 0.0, "il gradiente iniettato sull'ultimo stato non e' nullo"

    jp = m.jacobian_product_spectral_radius(params["Whh"], H, cache)
    assert jp.shape == (1,), f"con T=1 c'e' una sola jacobiana, shape attesa (1,), ottenuta {jp.shape}"
    assert jp[0] <= m.spectral_radius(params["Whh"]) + 1e-12, (
        "moltiplicare per diag(tanh') con tanh' <= 1 non puo' aumentare il raggio "
        "spettrale di una matrice ortogonale riscalata"
    )

    # BPTT troncato degenere
    g_tr = m.bptt_truncated(X, targets, params, 1, 1)
    assert_allclose(_flat(g_tr), _flat(g), rtol=1e-10, atol=1e-12,
                    err_msg="con T = 1 non c'e' niente da troncare: BPTT(1,1) = BPTT completo")


# ---------------------------------------------------------------------------
# 12. spectral_radius e prodotto di jacobiane, contro oracoli analitici
# ---------------------------------------------------------------------------

def test_spectral_radius_e_prodotto_cumulativo_di_jacobiane():
    """spectral_radius su matrici a spettro noto, e prodotto delle jacobiane su
    un caso in cui la risposta si sa a mano."""
    assert_allclose(m.spectral_radius(np.eye(3)), 1.0, rtol=1e-12,
                    err_msg="rho(I) = 1")
    assert_allclose(m.spectral_radius(np.diag([3.0, -5.0, 2.0])), 5.0, rtol=1e-12,
                    err_msg="per una diagonale rho e' il massimo MODULO, non il massimo")
    theta = 0.7
    c = 0.4
    R = c * np.array([[np.cos(theta), -np.sin(theta)],
                      [np.sin(theta), np.cos(theta)]])
    assert_allclose(m.spectral_radius(R), c, rtol=1e-12,
                    err_msg="autovalori complessi c e^{+-i theta}: rho = |c|. Se usi "
                            "solo la parte reale degli autovalori sbagli")
    assert_allclose(m.spectral_radius(np.array([[0.0, 1.0], [0.0, 0.0]])), 0.0,
                    atol=1e-12,
                    err_msg="la matrice nilpotente ha rho = 0 pur non essendo nulla: "
                            "il raggio spettrale NON e' una norma")

    # oracolo analitico: Whh = c I, input e bias nulli => lo stato resta in 0,
    # tanh'(0) = 1, quindi ogni jacobiana e' c I e il prodotto di k jacobiane
    # e' c^k I, di raggio spettrale c^k
    c, Hdim, T = 0.7, 3, 6
    params = {
        "Wxh": np.zeros((Hdim, 2)),
        "Whh": c * np.eye(Hdim),
        "bh": np.zeros(Hdim),
        "Why": np.eye(2, Hdim),
        "by": np.zeros(2),
    }
    X = np.zeros((T, 2))
    H, _, cache = m.rnn_forward(X, params["Wxh"], params["Whh"], params["bh"],
                                params["Why"], params["by"])
    assert_allclose(H, np.zeros((T + 1, Hdim)), atol=1e-15,
                    err_msg="con input, bias e stato iniziale nulli lo stato resta in 0")

    jp = m.jacobian_product_spectral_radius(params["Whh"], H, cache)
    atteso = c ** np.arange(1, T + 1)
    assert jp.shape == (T,), f"shape attesa ({T},), ottenuta {jp.shape}"
    assert_allclose(
        jp, atteso, rtol=1e-10,
        err_msg="out[k] deve essere il raggio spettrale del prodotto di k+1 jacobiane "
                "(out[0] = una sola jacobiana, quella dell'ultimo passo). Se ottieni "
                "c^k invece di c^(k+1) sei sfasato di uno; se ottieni c sempre uguale "
                "non stai accumulando il prodotto",
    )
    assert np.all(np.diff(jp) < 0.0), (
        "con c < 1 il raggio spettrale del prodotto deve decrescere: e' la forma "
        "matriciale del vanishing"
    )
