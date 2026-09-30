"""Test di autovalutazione - GDL14 "Undirected Graphical Models" (RBM + CD).

Esecuzione:
    pytest test_rbm_cd.py -v                # sullo skeleton (deve fallire tutto)
    GDL_SOL=1 pytest test_rbm_cd.py -v      # sulla soluzione (deve passare tutto)
"""

import os, sys, pathlib, importlib

HERE = pathlib.Path(__file__).parent
if os.environ.get("GDL_SOL"):
    sys.path.insert(0, str(HERE / "soluzione"))
    m = importlib.import_module("rbm_cd_sol")
else:
    sys.path.insert(0, str(HERE))
    m = importlib.import_module("rbm_cd")

import itertools

import numpy as np
from numpy.testing import assert_allclose


# ---------------------------------------------------------------------------
# Oracoli locali ai test. Sono scritti DALLA DEFINIZIONE, con cicli espliciti
# e senza chiamare le funzioni da implementare: se coincidono con il codice
# dello studente, il codice dello studente e' giusto per un motivo, non per
# una coincidenza di copia-incolla.
# ---------------------------------------------------------------------------


def _energy_def(v, h, W, b, c):
    """E(v,h) = -sum_i v_i b_i - sum_j h_j c_j - sum_ij v_i W_ij h_j, a mano."""
    D, H = W.shape
    e = 0.0
    for i in range(D):
        e -= v[i] * b[i]
    for j in range(H):
        e -= h[j] * c[j]
    for i in range(D):
        for j in range(H):
            e -= v[i] * W[i, j] * h[j]
    return e


def _states(n):
    """Tutte le 2^n configurazioni binarie, come array (2^n, n) di float."""
    return np.array(list(itertools.product([0.0, 1.0], repeat=n)), dtype=float)


def _joint_table(W, b, c):
    """p(v, h) esatta per enumerazione, shape (2^D, 2^H), somma 1."""
    D, H = W.shape
    Vs, Hs = _states(D), _states(H)
    tab = np.empty((len(Vs), len(Hs)))
    for a, v in enumerate(Vs):
        for t, h in enumerate(Hs):
            tab[a, t] = -_energy_def(v, h, W, b, c)
    tab = np.exp(tab - tab.max())
    return tab / tab.sum()


def _small_model(seed=0, D=6, H=4, scale=1.0):
    rng = np.random.default_rng(seed)
    W = scale * rng.standard_normal((D, H))
    b = 0.7 * rng.standard_normal(D)
    c = 0.7 * rng.standard_normal(H)
    return W, b, c


def _flat(gW, gb, gc):
    return np.concatenate([np.asarray(gW).ravel(), np.asarray(gb), np.asarray(gc)])


def _fd_true_gradient(V, W, b, c, eps=1e-5):
    """Gradiente ESATTO della log-likelihood per differenze finite centrali.

    Usa solo ``exact_log_likelihood``, che e' fornito nello skeleton (non e'
    esercizio): e' quindi un riferimento indipendente da ``cd_k``.
    """
    gW = np.zeros_like(W)
    for i in range(W.shape[0]):
        for j in range(W.shape[1]):
            Wp, Wm = W.copy(), W.copy()
            Wp[i, j] += eps
            Wm[i, j] -= eps
            gW[i, j] = (
                m.exact_log_likelihood(V, Wp, b, c) - m.exact_log_likelihood(V, Wm, b, c)
            ) / (2 * eps)
    gb = np.zeros_like(b)
    for i in range(len(b)):
        bp, bm = b.copy(), b.copy()
        bp[i] += eps
        bm[i] -= eps
        gb[i] = (
            m.exact_log_likelihood(V, W, bp, c) - m.exact_log_likelihood(V, W, bm, c)
        ) / (2 * eps)
    gc = np.zeros_like(c)
    for j in range(len(c)):
        cp, cm = c.copy(), c.copy()
        cp[j] += eps
        cm[j] -= eps
        gc[j] = (
            m.exact_log_likelihood(V, W, b, cp) - m.exact_log_likelihood(V, W, b, cm)
        ) / (2 * eps)
    return gW, gb, gc


# ---------------------------------------------------------------------------
# 1. sigmoid: stabilita' numerica
# ---------------------------------------------------------------------------


def test_sigmoid_non_va_in_overflow():
    """(h) Stabilita'. Con input +-1000 la forma ingenua produce inf e NaN.

    ``np.errstate(over="raise", invalid="raise")`` trasforma overflow e NaN in
    eccezioni: la funzione deve scegliere il ramo con maschere booleane, perche'
    ``np.where`` valuta ENTRAMBI i rami prima di scegliere e va comunque in
    overflow.
    """
    x = np.array([-1000.0, -50.0, -1e-12, 0.0, 1e-12, 50.0, 1000.0])
    with np.errstate(over="raise", invalid="raise"):
        y = m.sigmoid(x)

    assert np.all(np.isfinite(y)), f"sigmoid ha prodotto valori non finiti: {y}"
    assert np.all((y >= 0.0) & (y <= 1.0)), "la sigmoide deve stare in [0, 1]"
    assert y[0] == 0.0 and y[-1] == 1.0, (
        "sigmoid(-1000) deve saturare a 0 e sigmoid(+1000) a 1 senza NaN"
    )
    assert_allclose(y[3], 0.5, rtol=1e-12, err_msg="sigmoid(0) deve valere 0.5")

    # proprieta' matematica: sigma(-x) = 1 - sigma(x)
    z = np.linspace(-30.0, 30.0, 601)
    assert_allclose(
        m.sigmoid(-z),
        1.0 - m.sigmoid(z),
        rtol=1e-9,
        atol=1e-12,
        err_msg="deve valere sigma(-x) = 1 - sigma(x)",
    )
    assert m.sigmoid(z).shape == z.shape, "sigmoid deve preservare la shape"


# ---------------------------------------------------------------------------
# 2. energy: definizione, broadcasting e simmetria v <-> h
# ---------------------------------------------------------------------------


def test_energy_definizione_broadcasting_e_simmetria():
    """(d) L'energia e' quella della definizione, e' vettorizzata, ed e'
    simmetrica scambiando i ruoli di v e h con W trasposta:

        E(v, h; W, b, c) = E(h, v; W^T, c, b)

    E' la traduzione algebrica del fatto che il grafo e' NON ORIENTATO: nella
    RBM non c'e' un verso 'visibili -> nascoste', c'e' un solo potenziale
    bilineare v^T W h.
    """
    W, b, c = _small_model(seed=3, D=5, H=3)
    rng = np.random.default_rng(0)
    V = (rng.random((7, 5)) < 0.5).astype(float)
    Hh = (rng.random((7, 3)) < 0.5).astype(float)

    got = m.energy(V, Hh, W, b, c)
    assert np.asarray(got).shape == (7,), (
        f"con v (7,5) e h (7,3) l'energia deve avere shape (7,), ottenuta "
        f"{np.asarray(got).shape}"
    )
    want = np.array([_energy_def(V[n], Hh[n], W, b, c) for n in range(7)])
    assert_allclose(
        got,
        want,
        rtol=1e-6,
        atol=1e-9,
        err_msg="E(v,h) non coincide con -v@b - h@c - v@W@h calcolata a mano",
    )

    # simmetria: stesso valore scambiando i ruoli e trasponendo W
    assert_allclose(
        m.energy(Hh, V, W.T, c, b),
        got,
        rtol=1e-6,
        atol=1e-9,
        err_msg=(
            "E(h, v; W^T, c, b) deve essere identica a E(v, h; W, b, c): se non "
            "lo e', hai introdotto un verso che nel grafo non orientato non esiste"
        ),
    )

    # broadcasting su tutte le coppie: v (N,1,D) x h (1,M,H) -> (N,M)
    Vs, Hs = _states(4), _states(3)
    W2, b2, c2 = _small_model(seed=5, D=4, H=3)
    tab = m.energy(Vs[:, None, :], Hs[None, :, :], W2, b2, c2)
    assert np.asarray(tab).shape == (16, 8), (
        "energy deve essere vettorizzata con broadcasting: v (16,1,4) e "
        f"h (1,8,3) devono dare shape (16,8), ottenuta {np.asarray(tab).shape}"
    )
    assert_allclose(
        tab[5, 6],
        _energy_def(Vs[5], Hs[6], W2, b2, c2),
        rtol=1e-6,
        atol=1e-9,
        err_msg="il broadcasting non sta accoppiando le v con le h giuste",
    )


# ---------------------------------------------------------------------------
# 3. free_energy: ORACOLO sulla marginalizzazione analitica
# ---------------------------------------------------------------------------


def test_free_energy_uguale_a_enumerazione_sulle_nascoste():
    """(a) IL test dell'esercizio.

    F(v) = -log sum_h exp(-E(v,h)). Qui la somma su tutti i 2^H stati nascosti
    la facciamo per FORZA BRUTA, con l'energia calcolata dalla definizione a
    cicli. La formula chiusa con la softplus deve dare lo stesso numero, bit
    per bit (a meno dell'errore macchina).

    Se questo test fallisce, non hai capito perche' la somma su 2^H termini si
    fattorizza in H somme da 2 termini.
    """
    W, b, c = _small_model(seed=11, D=6, H=4, scale=1.3)
    Hs = _states(4)
    rng = np.random.default_rng(2)
    V = (rng.random((9, 6)) < 0.5).astype(float)

    brute = np.empty(len(V))
    for n, v in enumerate(V):
        neg_E = np.array([-_energy_def(v, h, W, b, c) for h in Hs])
        mx = neg_E.max()
        brute[n] = -(np.log(np.sum(np.exp(neg_E - mx))) + mx)

    got = m.free_energy(V, W, b, c)
    assert np.asarray(got).shape == (9,), (
        f"free_energy deve restituire shape (N,) = (9,), ottenuta "
        f"{np.asarray(got).shape}"
    )
    assert_allclose(
        got,
        brute,
        rtol=1e-6,
        atol=1e-9,
        err_msg=(
            "F(v) non coincide con -logsumexp_h(-E(v,h)) enumerato: controlla il "
            "segno dei bias e che il termine softplus sia log(1+exp(c_j+v@W[:,j])) "
            "sommato su TUTTE le nascoste"
        ),
    )

    # F non contiene log Z: e' definita a meno della normalizzazione globale.
    # Verifica indiretta: p(v) = exp(-F(v)) / sum_v exp(-F(v)) deve coincidere
    # con la marginale della congiunta esatta.
    Vs = _states(6)
    p_joint = _joint_table(W, b, c).sum(axis=1)
    fv = m.free_energy(Vs, W, b, c)
    p_from_F = np.exp(-fv - np.max(-fv))
    p_from_F /= p_from_F.sum()
    assert_allclose(
        p_from_F,
        p_joint,
        rtol=1e-6,
        atol=1e-9,
        err_msg="exp(-F(v)) normalizzata deve dare la marginale esatta p(v)",
    )


# ---------------------------------------------------------------------------
# 4. condizionali complete contro la congiunta enumerata
# ---------------------------------------------------------------------------


def test_condizionali_coincidono_con_la_congiunta_enumerata():
    """(b) p(h_j=1|v) e p(v_i=1|h) ricavate per enumerazione dalla congiunta
    esatta devono coincidere con le formule sigmoidali."""
    D, H = 5, 3
    W, b, c = _small_model(seed=17, D=D, H=H, scale=1.1)
    Vs, Hs = _states(D), _states(H)
    tab = _joint_table(W, b, c)  # (2^D, 2^H)

    # p(h | v) per enumerazione: riga della congiunta, rinormalizzata
    cond_h = tab / tab.sum(axis=1, keepdims=True)  # (2^D, 2^H)
    marg_h = cond_h @ Hs  # (2^D, H) = P(h_j = 1 | v)
    got_h = m.p_h_given_v(Vs, W, c)
    assert np.asarray(got_h).shape == (2**D, H), (
        f"p_h_given_v deve dare shape (N,H) = ({2**D},{H}), ottenuta "
        f"{np.asarray(got_h).shape}"
    )
    assert_allclose(
        got_h,
        marg_h,
        rtol=1e-6,
        atol=1e-9,
        err_msg=(
            "p(h_j=1|v) non coincide con la condizionale esatta: la formula e' "
            "sigmoid(c_j + v@W[:,j]); attenzione a non usare W trasposta"
        ),
    )

    # p(v | h) per enumerazione: colonna della congiunta, rinormalizzata
    cond_v = tab / tab.sum(axis=0, keepdims=True)  # (2^D, 2^H)
    marg_v = cond_v.T @ Vs  # (2^H, D) = P(v_i = 1 | h)
    got_v = m.p_v_given_h(Hs, W, b)
    assert_allclose(
        got_v,
        marg_v,
        rtol=1e-6,
        atol=1e-9,
        err_msg=(
            "p(v_i=1|h) non coincide con la condizionale esatta: la formula e' "
            "sigmoid(b_i + h@W[i,:]), cioe' W TRASPOSTA rispetto all'altro verso"
        ),
    )


# ---------------------------------------------------------------------------
# 5. le condizionali FATTORIZZANO: e' la "R" di RBM
# ---------------------------------------------------------------------------


def test_p_h_given_v_fattorizza_solo_perche_il_grafo_e_bipartito():
    """(c) p(h|v) = prod_j p(h_j|v).

    Vale perche' nella RBM non ci sono archi h-h: dato v, le nascoste sono
    d-separate fra loro. La controprova e' nello stesso test: se aggiungiamo
    all'energia un accoppiamento h-h (cioe' una Boltzmann machine NON
    ristretta), la fattorizzazione si rompe e il campionamento a blocchi non e'
    piu' lecito.
    """
    D, H = 4, 5
    W, b, c = _small_model(seed=23, D=D, H=H, scale=1.2)
    Hs = _states(H)
    v = np.array([1.0, 0.0, 1.0, 1.0])

    # congiunta condizionale esatta p(h|v) su tutti i 2^H stati, dalla definizione
    neg_E = np.array([-_energy_def(v, h, W, b, c) for h in Hs])
    joint = np.exp(neg_E - neg_E.max())
    joint /= joint.sum()

    q = m.p_h_given_v(v[None, :], W, c)[0]  # (H,) marginali per unita'
    prod = np.prod(np.where(Hs > 0.5, q, 1.0 - q), axis=1)

    assert_allclose(
        joint,
        prod,
        rtol=1e-6,
        atol=1e-9,
        err_msg=(
            "p(h|v) enumerata NON coincide con il prodotto delle marginali per "
            "unita': o le marginali sono sbagliate, o hai perso il fatto che le "
            "nascoste sono condizionalmente indipendenti dato v"
        ),
    )

    # ---- controprova: con archi h-h la fattorizzazione salta ----
    rng = np.random.default_rng(1)
    J = rng.standard_normal((H, H))
    J = np.triu(J, 1) * 2.0
    J = J + J.T  # simmetrica, diagonale nulla
    neg_E2 = neg_E + 0.5 * np.einsum("th,hk,tk->t", Hs, J, Hs)
    joint2 = np.exp(neg_E2 - neg_E2.max())
    joint2 /= joint2.sum()
    q2 = joint2 @ Hs  # marginali per unita' della NUOVA condizionale
    prod2 = np.prod(np.where(Hs > 0.5, q2, 1.0 - q2), axis=1)
    assert np.max(np.abs(joint2 - prod2)) > 1e-2, (
        "controprova fallita: con accoppiamenti h-h la condizionale NON deve "
        "fattorizzare (se fattorizza, l'oracolo del test e' rotto)"
    )


# ---------------------------------------------------------------------------
# 6. sample_bernoulli: caso limite p in {0, 1} e frequenze
# ---------------------------------------------------------------------------


def test_sample_bernoulli_estremi_e_frequenze():
    """(caso limite) Con p esattamente 0 o 1 il campione deve essere
    deterministico; altrimenti le frequenze devono corrispondere a p."""
    rng = np.random.default_rng(0)
    p = np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 1.0]])
    for _ in range(50):
        s = m.sample_bernoulli(p, rng)
        assert s.shape == p.shape, f"shape attesa {p.shape}, ottenuta {s.shape}"
        assert_allclose(
            s,
            p,
            err_msg=(
                "con p = 0 o 1 il campione deve essere deterministico: usa "
                "u < p con u in [0,1), non u <= p"
            ),
        )

    rng = np.random.default_rng(1234)
    p2 = np.full((200000,), 0.3)
    s2 = m.sample_bernoulli(p2, rng)
    assert set(np.unique(s2).tolist()) <= {0.0, 1.0}, "i campioni devono essere binari"
    freq = float(s2.mean())
    assert abs(freq - 0.3) < 5e-3, (
        f"frequenza empirica {freq:.4f} contro p = 0.3: sample_bernoulli non sta "
        "campionando da Bernoulli(p) (errore standard atteso ~0.001)"
    )


# ---------------------------------------------------------------------------
# 7. gibbs_step: coerenza interna + p(v) e' distribuzione invariante
# ---------------------------------------------------------------------------


def test_gibbs_step_lascia_invariante_la_distribuzione_del_modello():
    """(proprieta') Un passo di Gibbs a blocchi ha p(v,h) come distribuzione
    INVARIANTE: se parti dalla distribuzione esatta ci resti, e da un punto
    qualsiasi ci converge. Confrontiamo la distribuzione empirica su tutti gli
    stati visibili con quella esatta enumerata."""
    D, H = 3, 2
    W, b, c = _small_model(seed=31, D=D, H=H, scale=1.4)
    rng = np.random.default_rng(7)

    n_chain, n_burn = 40000, 80
    v = (rng.random((n_chain, D)) < 0.5).astype(float)
    for _ in range(n_burn):
        v, h_s, h_p = m.gibbs_step(v, W, b, c, rng)

    assert v.shape == (n_chain, D) and h_s.shape == (n_chain, H), (
        "gibbs_step deve restituire (v_new (N,D), h_sample (N,H), h_prob (N,H))"
    )
    assert set(np.unique(v).tolist()) <= {0.0, 1.0}, "v_new deve essere binario"
    assert set(np.unique(h_s).tolist()) <= {0.0, 1.0}, "h_sample deve essere binario"
    assert np.all((h_p > 0.0) & (h_p < 1.0)), "h_prob sono probabilita', non campioni"

    Vs = _states(D)
    p_exact = _joint_table(W, b, c).sum(axis=1)
    codes = (v @ (2 ** np.arange(D - 1, -1, -1))).astype(int)
    p_emp = np.bincount(codes, minlength=2**D) / n_chain
    assert_allclose(
        p_emp,
        p_exact,
        atol=0.015,
        err_msg=(
            "dopo il burn-in la distribuzione empirica delle visibili deve "
            "coincidere con p(v) esatta (errore MC ~0.002 con 40000 catene): la "
            "catena di Gibbs non ha p come distribuzione invariante"
        ),
    )
    assert len(Vs) == len(p_exact)


# ---------------------------------------------------------------------------
# 8. caso limite W = 0: visibili e nascoste indipendenti
# ---------------------------------------------------------------------------


def test_W_nulla_rende_v_e_h_indipendenti():
    """(i) Con W = 0 l'energia e' -v@b - h@c: la congiunta si spezza in
    p(v)p(h), le condizionali non dipendono piu' dall'altro blocco e la RBM
    degenera in due insiemi di bit indipendenti. Nessun apprendimento
    possibile: e' il motivo per cui W va inizializzata a rumore, non a zero."""
    D, H = 4, 3
    W = np.zeros((D, H))
    rng = np.random.default_rng(5)
    b = rng.standard_normal(D)
    c = rng.standard_normal(H)
    Vs, Hs = _states(D), _states(H)

    ph = m.p_h_given_v(Vs, W, c)
    assert_allclose(
        ph,
        np.tile(m.sigmoid(c), (len(Vs), 1)),
        rtol=1e-6,
        atol=1e-9,
        err_msg="con W = 0, p(h|v) non deve dipendere da v e vale sigmoid(c)",
    )
    pv = m.p_v_given_h(Hs, W, b)
    assert_allclose(
        pv,
        np.tile(m.sigmoid(b), (len(Hs), 1)),
        rtol=1e-6,
        atol=1e-9,
        err_msg="con W = 0, p(v|h) non deve dipendere da h e vale sigmoid(b)",
    )

    # la congiunta calcolata con m.energy deve fattorizzare esattamente
    neg_E = -m.energy(Vs[:, None, :], Hs[None, :, :], W, b, c)
    joint = np.exp(neg_E - neg_E.max())
    joint /= joint.sum()
    assert_allclose(
        joint,
        np.outer(joint.sum(axis=1), joint.sum(axis=0)),
        rtol=1e-6,
        atol=1e-9,
        err_msg="con W = 0 deve valere p(v,h) = p(v) p(h)",
    )

    # e F(v) si riduce a -v@b piu' una costante indipendente da v
    fv = m.free_energy(Vs, W, b, c)
    assert_allclose(
        fv - fv[0],
        (-Vs @ b) - (-Vs[0] @ b),
        rtol=1e-6,
        atol=1e-9,
        err_msg="con W = 0, F(v) deve valere -v@b a meno di una costante",
    )


# ---------------------------------------------------------------------------
# 9. cd_k: il segno e' quello dell'ASCESA
# ---------------------------------------------------------------------------


def test_cd_k_e_una_direzione_di_ascesa():
    """Un passo nella direzione restituita da cd_k deve AUMENTARE la
    log-likelihood esatta. Se hai invertito fase positiva e fase negativa (o
    hai scritto un gradiente di discesa), questo test fallisce."""
    D, H = 5, 3
    W, b, c = _small_model(seed=13, D=D, H=H, scale=0.9)
    V = np.array([[1, 1, 0, 0, 1], [0, 0, 1, 1, 0], [1, 0, 1, 0, 1]], dtype=float)
    V = np.tile(V, (400, 1))

    rng = np.random.default_rng(99)
    gW, gb, gc, v_model = m.cd_k(V, W, b, c, 30, rng)

    assert gW.shape == W.shape and gb.shape == b.shape and gc.shape == c.shape, (
        "i gradienti devono avere le stesse shape dei parametri"
    )
    assert v_model.shape == V.shape, "v_model deve avere la shape di v_data"
    assert set(np.unique(v_model).tolist()) <= {0.0, 1.0}, (
        "v_model e' lo stato della catena di Gibbs: deve essere binario, non "
        "una probabilita'"
    )

    ll0 = m.exact_log_likelihood(V, W, b, c)
    eta = 0.05
    ll1 = m.exact_log_likelihood(V, W + eta * gW, b + eta * gb, c + eta * gc)
    assert ll1 > ll0, (
        f"muovendosi di +eta*grad la log-likelihood passa da {ll0:.5f} a "
        f"{ll1:.5f}: cd_k deve restituire un gradiente di ASCESA "
        "(<.>_dati - <.>_modello), l'aggiornamento e' W += lr*grad_W"
    )


# ---------------------------------------------------------------------------
# 10. IL test concettuale: CD e' un'approssimazione BIASED
# ---------------------------------------------------------------------------


def test_cd_k_bias_k1_molto_peggio_di_k50():
    """(e) Cuore dell'esercizio.

    Il gradiente vero della log-likelihood lo calcoliamo per differenze finite
    su ``exact_log_likelihood`` (enumerazione esatta di Z). Poi confrontiamo
    CD-1 e CD-50 sullo STESSO batch e con lo stesso seed. Il batch e' replicato
    1000 volte, quindi la varianza Monte Carlo del gradiente e' minuscola: cio'
    che resta e' BIAS, non rumore.

    Risultato atteso: l'errore di CD-1 e' dell'ordine del 40% della norma del
    gradiente vero, quello di CD-50 e' un ordine di grandezza piu' piccolo.
    Morale: CD-k NON e' uno stimatore non distorto del gradiente, e CD-1 non
    massimizza la log-likelihood. Aumentare i dati non toglie il bias;
    aumentare k si'.
    """
    D, H = 5, 3
    rng0 = np.random.default_rng(11)
    W = 3.0 * rng0.standard_normal((D, H))
    b = 0.5 * rng0.standard_normal(D)
    c = 0.5 * rng0.standard_normal(H)

    V_base = np.array(
        [[1, 1, 0, 0, 1], [0, 0, 1, 1, 0], [1, 0, 1, 0, 1], [1, 1, 1, 1, 1]], dtype=float
    )
    true_flat = _flat(*_fd_true_gradient(V_base, W, b, c))
    norm_true = float(np.linalg.norm(true_flat))

    V = np.tile(V_base, (1000, 1))  # 4000 catene parallele: varianza trascurabile
    err = {}
    for k in (1, 50):
        rng = np.random.default_rng(2024)
        gW, gb, gc, _ = m.cd_k(V, W, b, c, k, rng)
        err[k] = float(np.linalg.norm(_flat(gW, gb, gc) - true_flat))

    assert err[1] > 0.25 * norm_true, (
        f"errore CD-1 = {err[1]:.4f} contro |grad vero| = {norm_true:.4f}: qui "
        "CD-1 DEVE sbagliare parecchio; se e' gia' quasi esatto probabilmente "
        "non stai facendo partire la catena dai dati o non stai campionando"
    )
    assert err[50] < 0.2 * err[1], (
        f"errore CD-50 = {err[50]:.4f} non e' molto minore di quello di CD-1 = "
        f"{err[1]:.4f}: allungando la catena la fase negativa deve avvicinarsi "
        "all'aspettazione sotto il modello, e il bias deve calare"
    )
    assert err[50] < 0.1 * norm_true, (
        f"errore CD-50 = {err[50]:.4f} ancora grande rispetto a |grad vero| = "
        f"{norm_true:.4f}: con 50 passi e 4000 catene il gradiente dovrebbe "
        "essere quasi quello esatto"
    )


# ---------------------------------------------------------------------------
# 11. train_rbm su Bars-and-Stripes: ricostruzione e free energy gap
# ---------------------------------------------------------------------------


def test_train_rbm_ricostruzione_decresce():
    """(f) Sul dataset Bars-and-Stripes 3x3 l'errore di ricostruzione deve
    crollare rispetto al valore iniziale (che parte da ~0.25, cioe' il valore
    di un modello che non sa nulla e ricostruisce 0.5 ovunque)."""
    X = m.make_bars_and_stripes(0)
    assert X.shape == (14, 9), f"il dataset BAS 3x3 ha 14 pattern da 9 bit, non {X.shape}"

    out = m.train_rbm(X, H=8, epochs=600, lr=0.2, k=1, batch_size=7, seed=0)
    for key in ("W", "b", "c", "recon_error_history", "free_energy_gap_history"):
        assert key in out, f"train_rbm deve restituire la chiave '{key}'"
    rec = np.asarray(out["recon_error_history"])
    gap = np.asarray(out["free_energy_gap_history"])
    assert rec.shape == (600,) and gap.shape == (600,), (
        f"le history devono avere un valore per epoca: shape {rec.shape}, {gap.shape}"
    )

    start, end = float(rec[:10].mean()), float(rec[-10:].mean())
    assert end < 0.25 * start, (
        f"errore di ricostruzione: {start:.4f} all'inizio, {end:.4f} alla fine. "
        "Non sta scendendo: controlla il segno dell'update (ascesa), che i "
        "minibatch cambino a ogni epoca e che nelle statistiche del gradiente "
        "compaiano le probabilita' p(h=1|v), non i bit campionati"
    )
    assert float(gap[-10:].mean()) < float(gap[:10].mean()) - 1.0, (
        "il free energy gap F(dati) - F(rumore) deve diventare nettamente "
        "negativo: il modello deve dare energia BASSA ai dati e ALTA al rumore"
    )


# ---------------------------------------------------------------------------
# 12. la log-likelihood ESATTA cresce davvero
# ---------------------------------------------------------------------------


def test_train_rbm_log_likelihood_esatta_cresce():
    """(g) L'errore di ricostruzione e' solo un proxy. Qui misuriamo la cosa
    vera: log p(v) media, con Z enumerato su tutti i 2^9 stati visibili.

    Il training viene rilanciato con lo stesso seed e un numero crescente di
    epoche: poiche' il generatore e' consumato nello stesso ordine, la corsa
    lunga contiene quella corta come prefisso, e i checkpoint sono confrontabili.
    """
    X = m.make_bars_and_stripes(0)
    uniform_ll = -9.0 * np.log(2.0)  # modello uniforme su 2^9 stati

    lls = []
    for ep in (0, 400, 1200):
        out = m.train_rbm(X, H=8, epochs=ep, lr=0.2, k=1, batch_size=7, seed=0)
        lls.append(m.exact_log_likelihood(X, out["W"], out["b"], out["c"]))

    assert lls[0] < uniform_ll + 0.05, (
        f"a 0 epoche la log-likelihood e' {lls[0]:.4f}: con W ~ 0.01*N(0,1) e "
        f"bias nulli il modello e' quasi uniforme ({uniform_ll:.4f})"
    )
    assert lls[1] > lls[0] + 0.2, (
        f"log-likelihood: {lls[0]:.4f} -> {lls[1]:.4f} in 400 epoche. Non sta "
        "salendo"
    )
    assert lls[2] > lls[1] + 0.2, (
        f"log-likelihood: {lls[1]:.4f} -> {lls[2]:.4f} fra 400 e 1200 epoche. "
        "Il training deve continuare a migliorare il modello, non solo la "
        "ricostruzione"
    )
    assert lls[2] - lls[0] > 2.0, (
        f"la log-likelihood e' passata da {lls[0]:.4f} a {lls[2]:.4f}: un "
        "guadagno di meno di 2 nat su un problema con 14 pattern significa che "
        "il modello non ha imparato quasi nulla. Nelle statistiche del gradiente "
        "devi usare le PROBABILITA' p(h=1|v), non i bit campionati"
    )
    assert lls[2] > np.log(1.0 / 14.0) - 1.8, (
        f"log-likelihood finale {lls[2]:.4f}: il massimo raggiungibile su 14 "
        f"pattern equiprobabili e' {np.log(1/14):.4f}, si dovrebbe arrivare "
        "ragionevolmente vicini"
    )
