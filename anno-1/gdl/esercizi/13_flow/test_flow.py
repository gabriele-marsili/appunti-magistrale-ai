"""Test suite - GDL27-28 Normalizing Flows.

    cd 13_flow && python3 -m pytest test_flow.py -v          # skeleton
    cd 13_flow && GDL_SOL=1 python3 -m pytest test_flow.py -v # soluzione
"""

import os
import sys
import pathlib
import importlib

import numpy as np

HERE = pathlib.Path(__file__).parent
if os.environ.get("GDL_SOL"):
    sys.path.insert(0, str(HERE / "soluzione"))
    m = importlib.import_module("flow_sol")
else:
    sys.path.insert(0, str(HERE))
    m = importlib.import_module("flow")


# ---------------------------------------------------------------------------
# Oracolo indipendente: lo Jacobiano per differenze finite centrate.
# Deliberatamente lento e stupido, costruito colonna per colonna. Non usa
# nessuna delle funzioni di log-determinante che stiamo testando: chiama solo
# la mappa diretta.
# ---------------------------------------------------------------------------

FD_EPS = 1e-5


def numerical_jacobian(f, x0, eps=FD_EPS):
    """J[i, j] = d f_i / d x_j in x0, per differenze centrate.

    ``f`` accetta un array (N, D) e restituisce (N, D); ``x0`` ha shape (D,).
    """
    x0 = np.asarray(x0, dtype=float)
    D = x0.shape[0]
    out_dim = np.asarray(f(x0[None, :])).shape[1]
    J = np.empty((out_dim, D), dtype=float)
    for j in range(D):
        e = np.zeros(D)
        e[j] = eps
        plus = np.asarray(f((x0 + e)[None, :]))[0]
        minus = np.asarray(f((x0 - e)[None, :]))[0]
        J[:, j] = (plus - minus) / (2.0 * eps)
    return J


def numerical_log_abs_det(f, x0, eps=FD_EPS):
    """log |det J_f(x0)| ottenuto dallo Jacobiano numerico."""
    sign, logabsdet = np.linalg.slogdet(numerical_jacobian(f, x0, eps))
    assert sign != 0.0, "Jacobiano numericamente singolare: la mappa non e' invertibile"
    return float(logabsdet)


# Tolleranza dell'oracolo: sui casi di questo file l'errore delle differenze
# centrate con eps=1e-5 e' misurato intorno a 5e-10, quindi 1e-7 lascia due
# ordini di grandezza di margine ma non perdona un errore analitico vero.
FD_ATOL = 1e-7


def _flow2d(n_layers=4, seed=20260427):
    """Flusso 2D di riferimento, deterministico, usato dai test di densita'."""
    return m.make_flow(2, n_layers, np.random.default_rng(seed))


# ---------------------------------------------------------------------------
# 1. Coupling layer
# ---------------------------------------------------------------------------


def test_coupling_copia_meta_mascherata_e_trasforma_laltra():
    rng = np.random.default_rng(1)
    D, N = 6, 12
    mask = m.alternating_mask(D, 0)
    params = m.random_coupling_params(D, 5, rng)
    x = rng.standard_normal((N, D))
    y = m.affine_coupling_forward(x, params, mask)

    keep = mask == 1.0
    np.testing.assert_allclose(
        y[:, keep],
        x[:, keep],
        rtol=0,
        atol=0,
        err_msg=(
            "Le dimensioni con mask == 1 devono uscire IDENTICHE dal coupling: "
            "sono la meta' condizionante che viene copiata. Se le hai trasformate, "
            "lo Jacobiano non e' piu' triangolare e il log-det che calcoli e' falso."
        ),
    )
    moved = np.abs(y[:, ~keep] - x[:, ~keep]).max()
    assert moved > 1e-6, (
        "Le dimensioni con mask == 0 devono essere scalate e traslate. Se restano "
        "uguali, hai applicato la trasformazione alla meta' sbagliata (maschera "
        "invertita) oppure non l'hai applicata affatto."
    )


def test_coupling_inverso_ricostruisce_esattamente_lingresso():
    rng = np.random.default_rng(2)
    D, N = 6, 32
    x = 2.0 * rng.standard_normal((N, D))
    for parity in (0, 1):
        mask = m.alternating_mask(D, parity)
        params = m.random_coupling_params(D, 5, rng)
        y = m.affine_coupling_forward(x, params, mask)
        x_back = m.affine_coupling_inverse(y, params, mask)
        err = np.abs(x_back - x).max()
        assert err < 1e-12, (
            f"Coupling non invertibile (errore {err:.2e}, parity={parity}). Ricorda "
            "che mask*y == mask*x: le reti di scala e traslazione vanno rivalutate "
            "sull'input MASCHERATO di y, non su y intero, e la scala va DIVISA "
            "(exp(-log_scale)), non moltiplicata."
        )


# ---------------------------------------------------------------------------
# 2. Invertibilita' della composizione
# ---------------------------------------------------------------------------


def test_flow_invertibilita_esatta_su_piu_layer():
    rng = np.random.default_rng(3)
    for D, n_layers in ((2, 1), (4, 3), (5, 6), (8, 8)):
        layers = m.make_flow(D, n_layers, rng)
        x = 3.0 * rng.standard_normal((40, D))

        z = m.flow_forward(x, layers)
        x_back = m.flow_inverse(z, layers)
        err_xzx = np.abs(x_back - x).max()
        assert err_xzx < 1e-10, (
            f"flow_inverse(flow_forward(x)) != x (errore {err_xzx:.2e}, D={D}, "
            f"{n_layers} layer). Con un layer solo funziona anche sbagliando: "
            "l'inversa di una composizione percorre i layer AL CONTRARIO."
        )

        z0 = rng.standard_normal((40, D))
        z_back = m.flow_forward(m.flow_inverse(z0, layers), layers)
        err_zxz = np.abs(z_back - z0).max()
        assert err_zxz < 1e-10, (
            f"flow_forward(flow_inverse(z)) != z (errore {err_zxz:.2e}, D={D}, "
            f"{n_layers} layer): l'inversa deve valere in entrambi i versi."
        )


# ---------------------------------------------------------------------------
# 3. Oracolo indipendente: Jacobiano per differenze finite
# ---------------------------------------------------------------------------


def test_log_det_coupling_contro_jacobiano_numerico():
    rng = np.random.default_rng(4)
    D = 5
    mask = m.alternating_mask(D, 1)
    params = m.random_coupling_params(D, 6, rng, w_scale=0.6)
    X = 1.5 * rng.standard_normal((8, D))

    analitico = np.asarray(m.affine_coupling_log_det(X, params, mask))
    assert analitico.shape == (8,), (
        f"affine_coupling_log_det deve restituire shape (N,), ha dato {analitico.shape}: "
        "un log-determinante per ogni riga di x, non una matrice."
    )

    def f(t):
        return m.affine_coupling_forward(t, params, mask)

    numerico = np.array([numerical_log_abs_det(f, x) for x in X])
    np.testing.assert_allclose(
        analitico,
        numerico,
        rtol=1e-6,
        atol=FD_ATOL,
        err_msg=(
            "Il log-det analitico non coincide con log|det J| dello Jacobiano "
            "calcolato per differenze finite. Errori tipici: sommare i log_scale su "
            "TUTTE le dimensioni invece che sulle sole mask == 0; sommare la "
            "traslazione (che non cambia i volumi); sommare exp(log_scale) invece "
            "del log."
        ),
    )


def test_flow_log_det_contro_jacobiano_numerico():
    rng = np.random.default_rng(5)
    D, n_layers = 4, 5
    layers = m.make_flow(D, n_layers, rng, hidden=6, w_scale=0.6)
    X = 1.5 * rng.standard_normal((8, D))

    analitico = np.asarray(m.flow_log_det(X, layers))

    def f(t):
        return m.flow_forward(t, layers)

    numerico = np.array([numerical_log_abs_det(f, x) for x in X])
    np.testing.assert_allclose(
        analitico,
        numerico,
        rtol=1e-6,
        atol=FD_ATOL,
        err_msg=(
            "Il log-det della composizione non coincide con lo Jacobiano numerico "
            "dell'intera mappa. L'errore quasi sempre e' valutare tutti i log-det "
            "nello stesso punto x: il log-det del layer i va calcolato in z_{i-1}, "
            "cioe' sull'uscita del layer precedente."
        ),
    )


def test_log_det_dellinversa_e_lopposto_di_quello_diretto():
    rng = np.random.default_rng(6)
    D, n_layers = 4, 4
    layers = m.make_flow(D, n_layers, rng, hidden=6, w_scale=0.6)
    X = 1.2 * rng.standard_normal((6, D))
    Z = m.flow_forward(X, layers)

    diretto = np.asarray(m.flow_log_det(X, layers))

    def g(t):
        return m.flow_inverse(t, layers)

    inverso = np.array([numerical_log_abs_det(g, z) for z in Z])
    np.testing.assert_allclose(
        inverso,
        -diretto,
        rtol=1e-6,
        atol=FD_ATOL,
        err_msg=(
            "Deve valere log|det J_z f^-1| = -log|det J_x f| con z = f(x): e' il "
            "teorema della funzione inversa, ed e' la ragione per cui nella slide la "
            "stessa formula compare una volta col piu' e una col meno. Se questo test "
            "fallisce mentre gli altri passano, flow_inverse non e' l'inversa del "
            "flow_forward su cui calcoli il log-det."
        ),
    )


# ---------------------------------------------------------------------------
# 4. Densita' esplicita
# ---------------------------------------------------------------------------


def test_log_prob_e_log_base_piu_log_det_col_segno_giusto():
    rng = np.random.default_rng(7)
    layers = _flow2d()
    X = rng.standard_normal((20, 2))

    atteso = m.standard_normal_logpdf(m.flow_forward(X, layers)) + m.flow_log_det(
        X, layers
    )
    np.testing.assert_allclose(
        m.log_prob(X, layers),
        atteso,
        rtol=1e-12,
        atol=1e-12,
        err_msg=(
            "log_prob deve essere log P(f(x)) + log|det J_x f| (segno PIU', perche' f "
            "e' la direzione normalizzante x -> z). Col segno meno ottieni comunque "
            "numeri plausibili, ma la 'densita'' non integra a 1."
        ),
    )


def test_densita_integra_a_uno():
    layers = _flow2d()
    L, n = 12.0, 401
    g = np.linspace(-L, L, n)
    G1, G2 = np.meshgrid(g, g, indexing="ij")
    pts = np.stack([G1.ravel(), G2.ravel()], axis=1)

    P = np.exp(m.log_prob(pts, layers)).reshape(n, n)
    massa = float(np.trapezoid(np.trapezoid(P, g, axis=1), g))
    assert abs(massa - 1.0) < 1e-3, (
        f"La densita' trasformata integra a {massa:.6f} invece che a 1. Il cambio di "
        "variabile CONSERVA la massa: se il fattore di volume ha il segno sbagliato "
        "o e' valutato nel punto sbagliato, l'integrale se ne accorge subito. "
        "(Un segno invertito nel log-det tipicamente da' un valore lontanissimo da 1.)"
    )


def test_massa_conservata_istogramma_vs_densita():
    """Conservazione della massa: campionare col flusso e valutare la densita'
    devono dare la stessa distribuzione."""
    layers = _flow2d()
    n_samples = 200_000
    S = np.asarray(m.sample(layers, n_samples, np.random.default_rng(2026)))
    assert S.shape == (n_samples, 2), (
        f"sample deve restituire shape (n, D) = ({n_samples}, 2), ha dato {S.shape}."
    )

    edges = np.array([-8.0, -1.5, -0.5, 0.5, 1.5, 8.0])
    K = len(edges) - 1
    counts, _, _ = np.histogram2d(S[:, 0], S[:, 1], bins=[edges, edges])
    frazioni = counts / n_samples

    # Massa teorica di ogni cella per quadratura su exp(log_prob).
    teoriche = np.zeros((K, K))
    for i in range(K):
        for j in range(K):
            g1 = np.linspace(edges[i], edges[i + 1], 121)
            g2 = np.linspace(edges[j], edges[j + 1], 121)
            G1, G2 = np.meshgrid(g1, g2, indexing="ij")
            P = np.exp(
                m.log_prob(np.stack([G1.ravel(), G2.ravel()], axis=1), layers)
            ).reshape(121, 121)
            teoriche[i, j] = np.trapezoid(np.trapezoid(P, g2, axis=1), g1)

    # Tolleranza: con n = 2e5 la deviazione standard binomiale di una frazione di
    # cella e' al piu' sqrt(0.25/2e5) ~ 1.1e-3, e nelle celle di questa griglia
    # e' <= 7.6e-4. 4e-3 sono oltre 5 sigma, e il seed e' fissato.
    scarto = np.abs(frazioni - teoriche).max()
    assert scarto < 4e-3, (
        f"Istogramma dei campioni e densita' non coincidono (scarto massimo per cella "
        f"{scarto:.2e}). sample() e log_prob() devono descrivere la STESSA legge: "
        "il primo passa da f^-1, il secondo da f e dal log-det. Se divergono, una "
        "delle due direzioni non e' l'inversa dell'altra, oppure il log-det e' "
        "valutato nel punto sbagliato."
    )


# ---------------------------------------------------------------------------
# 5. Caso limite: scala nulla
# ---------------------------------------------------------------------------


def test_caso_limite_log_scala_nulla_preserva_i_volumi():
    """log_scale identicamente 0 => log-det ESATTAMENTE 0 (non ~0)."""
    rng = np.random.default_rng(8)
    D, n_layers = 6, 3
    layers = m.make_flow(D, n_layers, rng)
    X = 2.0 * rng.standard_normal((16, D))

    # (a) Azzero solo l'ULTIMO strato della rete di log-scala: il flusso resta un
    #     NICE (solo traslazioni), quindi muove i punti ma non i volumi.
    vol = [
        {
            "mask": lay["mask"],
            "params": {
                **lay["params"],
                "W2s": np.zeros_like(lay["params"]["W2s"]),
                "b2s": np.zeros_like(lay["params"]["b2s"]),
            },
        }
        for lay in layers
    ]
    ld = np.asarray(m.flow_log_det(X, vol))
    assert np.abs(ld).max() == 0.0, (
        f"Con log_scale identicamente 0 il log-det deve essere ESATTAMENTE 0.0, non "
        f"{np.abs(ld).max():.3e}. Un flusso di sole traslazioni (NICE) conserva i "
        "volumi: se ottieni un valore non nullo stai sommando anche la traslazione, "
        "oppure stai passando per exp/log inutili."
    )
    spostamento = np.abs(np.asarray(m.flow_forward(X, vol)) - X).max()
    assert spostamento > 1e-6, (
        "Attenzione: log-det nullo NON significa trasformazione identita'. Con sole "
        "traslazioni il flusso sposta eccome i punti, pur preservando i volumi. Qui "
        "il flusso non ha mosso nulla, quindi la traslazione non e' stata applicata."
    )

    # (b) Azzero anche la traslazione: ora e' davvero l'identita'.
    ident = [
        {
            "mask": lay["mask"],
            "params": {k: np.zeros_like(v) for k, v in lay["params"].items()},
        }
        for lay in layers
    ]
    np.testing.assert_allclose(
        m.flow_forward(X, ident),
        X,
        rtol=0,
        atol=1e-15,
        err_msg=(
            "Con scala e traslazione entrambe nulle il coupling e' l'identita': "
            "exp(0) = 1 e shift = 0."
        ),
    )
    np.testing.assert_allclose(
        m.flow_inverse(X, ident),
        X,
        rtol=0,
        atol=1e-15,
        err_msg="Anche l'inversa dell'identita' deve essere l'identita'.",
    )
    assert np.abs(np.asarray(m.flow_log_det(X, ident))).max() == 0.0, (
        "Il log-det dell'identita' e' esattamente 0."
    )
    np.testing.assert_allclose(
        m.log_prob(X, ident),
        m.standard_normal_logpdf(X),
        rtol=1e-12,
        atol=1e-12,
        err_msg=(
            "Se il flusso e' l'identita', log_prob deve ridursi alla log-densita' "
            "della base N(0, I). Se non succede, il termine di log-det e' entrato con "
            "un valore o un segno sbagliato."
        ),
    )


# ---------------------------------------------------------------------------
# 6. Flusso planare e vincolo di invertibilita'
# ---------------------------------------------------------------------------


def test_planar_log_det_contro_jacobiano_numerico():
    rng = np.random.default_rng(9)
    D = 4
    X = 1.2 * rng.standard_normal((8, D))
    for _ in range(4):
        u = rng.standard_normal(D)
        w = rng.standard_normal(D)
        b = float(rng.standard_normal())
        u = m.enforce_invertibility(u, w)

        analitico = np.asarray(m.planar_flow_log_det(X, u, w, b))

        def f(t, u=u, w=w, b=b):
            return m.planar_flow_forward(t, u, w, b)

        numerico = np.array([numerical_log_abs_det(f, x) for x in X])
        np.testing.assert_allclose(
            analitico,
            numerico,
            rtol=1e-6,
            atol=FD_ATOL,
            err_msg=(
                "log(1 + u^T psi(x)) non coincide con log|det J| numerico del flusso "
                "planare. Controlla psi(x) = h'(w^T x + b) * w con h' = 1 - tanh^2 "
                "(non tanh), e che il prodotto scalare sia u^T psi e non w^T psi."
            ),
        )


def test_enforce_invertibility_garantisce_vincolo():
    rng = np.random.default_rng(10)
    D = 5
    peggiore = np.inf
    for _ in range(200):
        # Scala grande apposta: senza vincolo w^T u finisce spesso ben sotto -1.
        u = 4.0 * rng.standard_normal(D)
        w = 4.0 * rng.standard_normal(D)
        u_hat = np.asarray(m.enforce_invertibility(u, w))
        assert u_hat.shape == (D,), (
            f"enforce_invertibility deve restituire un vettore (D,), ha dato {u_hat.shape}."
        )
        valore = 1.0 + float(w @ u_hat)
        peggiore = min(peggiore, valore)
        # -1e-9: quando w^T u e' molto negativo softplus lo schiaccia a 0 e la
        # ricostruzione di w^T u_hat vale -1 a meno dell'errore di arrotondamento.
        assert valore >= -1e-9, (
            f"Dopo il vincolo deve valere 1 + w^T u_hat >= 0, invece vale {valore:.4f}. "
            "La riparametrizzazione sposta u LUNGO w di (m(a) - a) * w / ||w||^2 con "
            "a = w^T u e m(a) = -1 + softplus(a); dividere per ||w|| invece che per "
            "||w||^2, o dimenticare il -1, rompe esattamente questa garanzia."
        )
        # La componente ortogonale a w non deve essere toccata: il vincolo agisce
        # solo sulla proiezione lungo w.
        proj = (w @ u) / (w @ w) * w
        proj_hat = (w @ u_hat) / (w @ w) * w
        np.testing.assert_allclose(
            u_hat - proj_hat,
            u - proj,
            rtol=1e-9,
            atol=1e-9,
            err_msg=(
                "enforce_invertibility deve muovere u SOLO lungo w: la componente "
                "ortogonale a w non influenza il determinante e va lasciata stare."
            ),
        )
    assert peggiore < 0.5, (
        "Il test non ha mai avvicinato il vincolo: i casi generati sono troppo blandi "
        "per dire qualcosa (non e' un errore della tua implementazione)."
    )


def test_planar_senza_vincolo_il_log_det_si_rompe():
    D = 3
    w = np.array([1.0, -0.5, 0.25])
    b = 0.0
    # Punto sull'iperpiano w^T x + b = 0: li' h' = 1, il caso peggiore.
    x0 = np.zeros((1, D))

    # (a) u scelto in modo che w^T u = -5 << -1: il flusso NON e' invertibile.
    u_cattivo = -5.0 * w / (w @ w)
    termine = 1.0 + float((1.0 - np.tanh(b) ** 2) * (w @ u_cattivo))
    assert termine < 0.0, "setup del test: il termine 1 + u^T psi deve essere negativo"
    with np.errstate(invalid="ignore", divide="ignore"):
        rotto = np.asarray(m.planar_flow_log_det(x0, u_cattivo, w, b))
    assert not np.all(np.isfinite(rotto)), (
        f"Senza il vincolo di invertibilita' il termine 1 + u^T psi(x) qui vale "
        f"{termine:.3f} <= 0 e il log-det deve risultare NaN / -inf: quel flusso non "
        "e' una bigezione e non definisce nessuna densita'. Se ottieni un numero "
        "finito hai messo un valore assoluto (o un clip) che nasconde il problema "
        "invece di segnalarlo."
    )

    # (b) Stesso u, passato per il vincolo: log-det finito e positivo.
    u_buono = m.enforce_invertibility(u_cattivo, w)
    assert 1.0 + float(w @ u_buono) >= 0.0, "il vincolo deve dare 1 + w^T u_hat >= 0"
    sano = np.asarray(m.planar_flow_log_det(x0, u_buono, w, b))
    assert np.all(np.isfinite(sano)), (
        "Dopo enforce_invertibility il log-det deve essere finito su ogni x."
    )

    # Su tutto un campione di punti resta finito, e nel punto peggiore l'argomento
    # del logaritmo resta >= 0.
    rng = np.random.default_rng(11)
    X = 3.0 * rng.standard_normal((500, D))
    tutti = np.asarray(m.planar_flow_log_det(X, u_buono, w, b))
    assert np.all(np.isfinite(tutti)), (
        "Il vincolo w^T u_hat >= -1 deve garantire 1 + u^T psi(x) >= 0 per OGNI x, "
        "non solo per quelli vicini all'origine: h' = 1 - tanh^2 sta in (0, 1], quindi "
        "il caso peggiore e' h' = 1, cioe' x sull'iperpiano."
    )
