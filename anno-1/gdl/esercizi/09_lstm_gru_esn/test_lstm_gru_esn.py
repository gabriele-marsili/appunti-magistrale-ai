"""Test di autovalutazione - GDL18 "Gated Recurrent Models".

Esecuzione:
    pytest test_lstm_gru_esn.py -v                # sullo skeleton
    GDL_SOL=1 pytest test_lstm_gru_esn.py -v      # sulla soluzione di riferimento
"""

import os, sys, pathlib, importlib

HERE = pathlib.Path(__file__).parent
if os.environ.get("GDL_SOL"):
    sys.path.insert(0, str(HERE / "soluzione"))
    m = importlib.import_module("lstm_gru_esn_sol")
else:
    sys.path.insert(0, str(HERE))
    m = importlib.import_module("lstm_gru_esn")

import numpy as np
from numpy.testing import assert_allclose


# ---------------------------------------------------------------------------
# helper locali ai test (non fanno parte dell'API da implementare)
# ---------------------------------------------------------------------------

_LSTM_BLOCKS = ("i", "f", "o", "g")
_GRU_BLOCKS = ("z", "r", "n")


def _random_lstm_params(D, Hdim, seed, scale=1.0):
    """params LSTM casuali ma deterministici."""
    rng = np.random.default_rng(seed)
    p = {}
    for k in _LSTM_BLOCKS:
        p["W" + k] = rng.normal(size=(Hdim, D + Hdim)) * scale
        p["b" + k] = rng.normal(size=Hdim) * scale
    return p


def _random_gru_params(D, Hdim, seed, scale=1.0):
    """params GRU casuali ma deterministici."""
    rng = np.random.default_rng(seed)
    p = {}
    for k in _GRU_BLOCKS:
        p["W" + k] = rng.normal(size=(Hdim, D + Hdim)) * scale
        p["b" + k] = rng.normal(size=Hdim) * scale
    return p


def _saturated_lstm_params(D, Hdim, seed, bf=+60.0, bi=-60.0):
    """LSTM con forget gate saturato a 1 e input gate saturato a 0.

    I pesi restano piccoli (0.1) cosi' le gate dipendono ancora dall'input, ma
    il bias enorme domina: sigma(+60) vale ESATTAMENTE 1.0 in float64 (serve
    solo un argomento > ~36.7), sigma(-60) vale ~1e-26.
    """
    rng = np.random.default_rng(seed)
    p = {}
    for k in _LSTM_BLOCKS:
        p["W" + k] = rng.normal(size=(Hdim, D + Hdim)) * 0.1
        p["b" + k] = np.zeros(Hdim)
    p["Wg"] = rng.normal(size=(Hdim, D + Hdim))  # candidato di ampiezza O(1)
    p["bf"] = np.full(Hdim, float(bf))
    p["bi"] = np.full(Hdim, float(bi))
    return p


def _lstm_params_senza_ricorrenza_nelle_gate(D, Hdim, seed, bf):
    """LSTM le cui gate NON guardano h: azzera le colonne di stato di ogni W.

    Serve al test con il gradiente numerico: cosi' c_T dipende da c_0 in modo
    esattamente lineare (le gate dipendono solo da x) e d c_T / d c_0 e'
    esattamente il prodotto dei forget gate, senza il cammino indiretto
    c -> h -> gate.
    """
    rng = np.random.default_rng(seed)
    p = {}
    for k in _LSTM_BLOCKS:
        W = np.zeros((Hdim, D + Hdim))
        W[:, :D] = rng.normal(size=(Hdim, D))
        p["W" + k] = W
        p["b" + k] = np.zeros(Hdim)
    p["Wf"] = p["Wf"] * 0.05           # forget gate vicino a sigma(0) = 0.5
    p["bf"] = np.full(Hdim, float(bf))
    return p


def _cec_bruteforce(f_gates):
    """Oracolo lento: prod_{s=t+1}^{T} f_s calcolato con due cicli Python."""
    f = np.asarray(f_gates, dtype=float)
    T = f.shape[0]
    out = np.empty_like(f)
    for t in range(T):
        acc = np.ones(f.shape[1:])
        for s in range(t, T):
            acc = acc * f[s]
        out[t] = acc
    return out


# ---------------------------------------------------------------------------
# (a) Constant error carousel: lo stato di cella non si muove di un bit
# ---------------------------------------------------------------------------

def test_a_forget_saturato_mantiene_c_esattamente_costante_1000_passi():
    """Con f = 1 e i = 0 la ricorrenza c_t = f_t c_{t-1} + i_t g_t degenera
    nell'identita' c_t = c_{t-1}: dopo 1000 passi c deve essere BIT A BIT
    uguale a c_0, non 'circa' uguale."""
    D, Hdim, T = 3, 4, 1000
    params = _saturated_lstm_params(D, Hdim, seed=20240401)
    rng = np.random.default_rng(11)
    X = rng.uniform(-1.0, 1.0, size=(T, D))
    c0 = np.array([0.7, -1.3, 2.0, 0.05])

    H, C, gates = m.lstm_forward(X, params, h0=None, c0=c0)

    assert H.shape == (T, Hdim) and C.shape == (T, Hdim), (
        f"lstm_forward deve restituire H e C di shape ({T}, {Hdim}), "
        f"ottenute {H.shape} e {C.shape}"
    )
    assert np.all(gates["f"] == 1.0), (
        "con bias +60 il forget gate deve saturare a 1.0 ESATTO: se non ci "
        "arriva, la sigmoide non e' stabile oppure il bias non viene sommato "
        "alla pre-attivazione"
    )
    assert np.max(gates["i"]) < 1e-20, (
        "con bias -60 l'input gate deve essere numericamente nullo"
    )
    assert np.all(C == c0), (
        "lo stato di cella e' cambiato: differenza massima "
        f"{np.max(np.abs(C - c0)):.3e}. Il constant error carousel richiede "
        "c = f*c_prev + i*g con f=1 e i=0; un errore tipico e' scrivere "
        "c = f*c_prev + g (senza input gate) oppure c = tanh(f*c_prev + i*g)"
    )
    assert np.max(np.abs(H)) <= 1.0, "h = o*tanh(c) non puo' uscire da [-1, 1]"


# ---------------------------------------------------------------------------
# (b) Il gradiente lungo la cella: 1 contro 0.5^k contro il vanishing vanilla
# ---------------------------------------------------------------------------

def test_b_cec_gradient_uno_contro_decadimento_esponenziale():
    """Il fattore prod f_s vale 1 su tutto l'orizzonte se i forget gate sono
    saturi, decade come 0.5^k se valgono 0.5, e la RNN vanilla non ha modo di
    evitare il secondo caso perche' i suoi fattori sono w * tanh'(.) < 1."""
    D, Hdim, T = 3, 4, 1000
    params = _saturated_lstm_params(D, Hdim, seed=20240402)
    rng = np.random.default_rng(12)
    X = rng.uniform(-1.0, 1.0, size=(T, D))
    _, _, gates = m.lstm_forward(X, params, c0=np.full(Hdim, 0.5))

    cec = m.constant_error_carousel_gradient(gates["f"])
    assert cec.shape == (T, Hdim), (
        f"constant_error_carousel_gradient deve conservare la shape: attesa "
        f"({T}, {Hdim}), ottenuta {cec.shape}"
    )
    assert np.all(cec == 1.0), (
        "con forget gate saturi a 1 il prodotto cumulativo deve valere 1 "
        "ESATTAMENTE su tutto l'orizzonte di 1000 passi: e' questo il senso di "
        "'constant' in constant error carousel"
    )

    # forget gate a 0.5: decadimento esattamente geometrico
    f_half = np.full((T, Hdim), 0.5)
    dec = m.constant_error_carousel_gradient(f_half)
    # out[t] = prod_{s=t+1}^{T} f_s ha T - t fattori
    k = np.arange(T, 0, -1)[:, None]
    atteso = np.broadcast_to(0.5 ** k, (T, Hdim))
    assert_allclose(dec, atteso, rtol=1e-12, atol=0.0,
                    err_msg="con f = 0.5 costante il fattore a distanza k deve "
                            "valere esattamente 0.5^k: probabilmente il "
                            "prodotto cumulativo va nel verso sbagliato")
    assert dec[-1, 0] == 0.5, (
        "l'ultimo elemento deve essere il solo f_T (un fattore), non il "
        "prodotto di tutti: il cumprod va fatto DAL FONDO verso l'inizio"
    )
    assert dec[0, 0] < 1e-300, "0.5^1000 deve essere in pratica zero"

    # oracolo indipendente (doppio ciclo Python) su un orizzonte corto
    f_small = np.abs(np.random.default_rng(13).uniform(0.2, 0.99, size=(40, 3)))
    assert_allclose(m.constant_error_carousel_gradient(f_small),
                    _cec_bruteforce(f_small), rtol=1e-12, atol=1e-300,
                    err_msg="il prodotto cumulativo non coincide con la "
                            "definizione calcolata a forza bruta")

    # confronto con la RNN vanilla: d h_T / d h_t = prod_s w * tanh'(a_s).
    # Anche col peso al valore piu' favorevole compatibile con la stabilita'
    # (w = 1) il fattore tanh' < 1 fa svanire il prodotto.
    rng2 = np.random.default_rng(14)
    pre_act = rng2.normal(size=T) * 0.8
    vanilla_factors = 1.0 * (1.0 - np.tanh(pre_act) ** 2)   # w = 1, tanh'
    vanilla = m.constant_error_carousel_gradient(vanilla_factors)
    assert np.all(vanilla_factors < 1.0), "tanh' e' sempre < 1 fuori dall'origine"
    assert vanilla[0] < 1e-100, (
        "la RNN vanilla deve mostrare vanishing gradient su 1000 passi: il "
        "prodotto dei fattori w*tanh' e' esponenzialmente piccolo, mentre "
        "quello dell'LSTM con f = 1 vale 1. E' l'intero punto della lezione"
    )


# ---------------------------------------------------------------------------
# (b-bis) ORACOLO INDIPENDENTE: il fattore CEC e' un vero gradiente
# ---------------------------------------------------------------------------

def test_bbis_cec_gradient_coincide_col_gradiente_numerico_di_cT_su_c0():
    """prod f_s non e' una formula decorativa: e' letteralmente d c_T / d c_0.
    Lo verifichiamo con differenze finite su lstm_forward, senza mai usare la
    formula analitica dentro il calcolo di riferimento."""
    D, Hdim, T = 2, 1, 20
    # gate che non dipendono da h: c_T e' allora funzione lineare di c_0 e le
    # differenze finite danno il fattore esatto, senza il cammino c -> h -> gate
    params = _lstm_params_senza_ricorrenza_nelle_gate(D, Hdim, seed=7, bf=0.0)
    X = np.random.default_rng(9).uniform(-1.0, 1.0, size=(T, D))

    def c_finale(c0):
        _, C, _ = m.lstm_forward(X, params, c0=c0)
        return float(C[-1, 0])

    c0 = np.array([0.3])
    grad_num = m.numerical_gradient(c_finale, c0, eps=1e-4)

    _, _, gates = m.lstm_forward(X, params, c0=c0)
    grad_cec = m.constant_error_carousel_gradient(gates["f"])[0, 0]

    assert 0.3 < float(np.mean(gates["f"])) < 0.7, (
        "configurazione del test degenere: i forget gate dovrebbero stare "
        "attorno a 0.5"
    )
    assert_allclose(grad_num[0], grad_cec, rtol=1e-5, atol=1e-30,
                    err_msg="d c_T / d c_0 misurato per differenze finite non "
                            "coincide con prod_s f_s: o la ricorrenza della "
                            "cella non e' c = f*c_prev + i*g, o il prodotto "
                            "cumulativo e' sbagliato")


# ---------------------------------------------------------------------------
# (c) Proprieta' matematica: i codomini delle gate
# ---------------------------------------------------------------------------

def test_c_gate_nei_codomini_corretti():
    """Le gate sono sigmoidi (in [0,1], sono 'quanto lascio passare'), i
    candidati sono tangenti iperboliche (in [-1,1], sono 'cosa scrivo')."""
    D, Hdim, T = 5, 6, 200
    rng = np.random.default_rng(2024)
    X = rng.normal(size=(T, D)) * 8.0   # input grandi: forza la saturazione

    _, _, gl = m.lstm_forward(X, _random_lstm_params(D, Hdim, 1, scale=4.0))
    for k in ("i", "f", "o"):
        assert gl[k].shape == (T, Hdim), f"gates['{k}'] deve avere shape (T, Hdim)"
        assert np.all((gl[k] >= 0.0) & (gl[k] <= 1.0)), (
            f"il gate '{k}' dell'LSTM esce da [0,1]: e' una sigmoide, e con "
            "pre-attivazioni grandi una sigmoide non stabile va in overflow "
            "e restituisce nan"
        )
    assert np.all((gl["g"] >= -1.0) & (gl["g"] <= 1.0)), (
        "il candidato 'g' dell'LSTM deve essere una tanh, quindi in [-1,1]"
    )
    assert np.max(gl["f"]) > 0.99 and np.min(gl["f"]) < 0.01, (
        "con input grandi le gate devono saturare a entrambi gli estremi: se "
        "no, la sigmoide non sta ricevendo le pre-attivazioni giuste"
    )

    _, gg = m.gru_forward(X, _random_gru_params(D, Hdim, 2, scale=4.0))
    for k in ("z", "r"):
        assert np.all((gg[k] >= 0.0) & (gg[k] <= 1.0)), (
            f"il gate '{k}' della GRU esce da [0,1]"
        )
    assert np.all((gg["n"] >= -1.0) & (gg["n"] <= 1.0)), (
        "il candidato 'n' della GRU deve essere una tanh, quindi in [-1,1]"
    )
    assert np.all(np.isfinite(gl["g"])) and np.all(np.isfinite(gg["n"])), (
        "nan o inf nelle attivazioni: sigmoide non stabile"
    )


# ---------------------------------------------------------------------------
# (d) CASO LIMITE: i due estremi dell'update gate della GRU
# ---------------------------------------------------------------------------

def test_d_gru_z_uguale_uno_conserva_z_uguale_zero_sostituisce():
    """Convenzione del corso: h = (1-z)*n + z*h_prev. Quindi z = 1 e' il caso
    'copia lo stato precedente' (l'analogo del forget gate saturo dell'LSTM) e
    z = 0 e' 'butta via lo stato e scrivi il candidato'. Con la convenzione
    opposta h = (1-z)*h_prev + z*n i due limiti si scambiano: questo test la
    distingue."""
    D, Hdim = 3, 4
    base = _random_gru_params(D, Hdim, seed=77)
    rng = np.random.default_rng(78)
    x = rng.uniform(-1.0, 1.0, size=D)
    h_prev = rng.uniform(-1.0, 1.0, size=Hdim)

    # z = 1 esatto: Wz nulla e bias +60 -> sigma(60) == 1.0 in float64
    p_keep = dict(base, Wz=np.zeros((Hdim, D + Hdim)), bz=np.full(Hdim, 60.0))
    h_keep, g_keep = m.gru_cell(x, h_prev, p_keep)
    assert np.all(g_keep["z"] == 1.0), "sigma(60) deve valere 1.0 esatto"
    assert np.all(h_keep == h_prev), (
        "con z = 1 la GRU deve restituire h_prev IDENTICO. Differenza massima "
        f"{np.max(np.abs(h_keep - h_prev)):.3e}. Se ottieni il candidato n "
        "invece di h_prev stai usando l'altra convenzione, "
        "h = (1-z)*h_prev + z*n"
    )
    assert np.max(np.abs(g_keep["n"] - h_prev)) > 0.1, (
        "test degenere: qui il candidato n deve essere diverso da h_prev, "
        "altrimenti l'asserzione precedente non distingue nulla"
    )

    # z = 0 (a meno di ~1e-26): lo stato viene sostituito dal candidato
    p_write = dict(base, Wz=np.zeros((Hdim, D + Hdim)), bz=np.full(Hdim, -60.0))
    h_write, g_write = m.gru_cell(x, h_prev, p_write)
    assert np.max(g_write["z"]) < 1e-20, "sigma(-60) deve essere ~1e-26"
    assert_allclose(h_write, g_write["n"], rtol=0.0, atol=1e-15,
                    err_msg="con z = 0 lo stato nuovo deve coincidere col "
                            "candidato n: h = (1-z)*n + z*h_prev")
    assert np.max(np.abs(h_write - h_prev)) > 0.1, (
        "con z = 0 lo stato precedente deve essere effettivamente sostituito"
    )

    # il reset gate agisce sul candidato, non sull'update: con r = 0 il
    # candidato non deve piu' dipendere da h_prev
    p_r0 = dict(p_write, Wr=np.zeros((Hdim, D + Hdim)), br=np.full(Hdim, -60.0))
    _, g_a = m.gru_cell(x, h_prev, p_r0)
    _, g_b = m.gru_cell(x, -h_prev, p_r0)
    assert_allclose(g_a["n"], g_b["n"], rtol=0.0, atol=1e-15,
                    err_msg="con reset gate a 0 il candidato n deve essere "
                            "indipendente da h_prev: r moltiplica h_prev "
                            "DENTRO il candidato, non l'input")


# ---------------------------------------------------------------------------
# (e) Quattro blocchi per LSTM, tre per GRU - e servono tutti
# ---------------------------------------------------------------------------

def test_e_conteggio_dei_blocchi_di_parametri_quattro_lstm_tre_gru():
    """Un LSTM ha quattro trasformazioni affini (i, f, o, g), una GRU ne ha tre
    (z, r, n). Non e' aritmetica: e' il motivo per cui la GRU e' piu' leggera e
    non separa lo stato di cella dallo stato nascosto."""
    D, Hdim = 4, 5
    per_blocco = Hdim * (D + Hdim) + Hdim

    pl = _random_lstm_params(D, Hdim, 101)
    pg = _random_gru_params(D, Hdim, 102)
    n_lstm = sum(np.asarray(v).size for v in pl.values())
    n_gru = sum(np.asarray(v).size for v in pg.values())
    assert n_lstm == 4 * per_blocco, (
        f"un LSTM deve avere 4*(Hdim*(D+Hdim) + Hdim) = {4*per_blocco} "
        f"parametri, contati {n_lstm}"
    )
    assert n_gru == 3 * per_blocco, (
        f"una GRU deve avere 3*(Hdim*(D+Hdim) + Hdim) = {3*per_blocco} "
        f"parametri, contati {n_gru}"
    )
    assert 3 * n_lstm == 4 * n_gru, "il rapporto LSTM:GRU deve essere 4:3"

    rng = np.random.default_rng(103)
    x = rng.normal(size=D)
    h_prev = rng.normal(size=Hdim) * 0.5
    c_prev = rng.normal(size=Hdim) * 0.5

    h_ref, c_ref, g_ref = m.lstm_cell(x, h_prev, c_prev, pl)
    assert set(g_ref) == set(_LSTM_BLOCKS), (
        f"gates dell'LSTM deve avere esattamente le chiavi {_LSTM_BLOCKS}, "
        f"trovate {sorted(g_ref)}"
    )
    for k in _LSTM_BLOCKS:
        pert = {kk: (vv.copy() if kk != "b" + k else vv + 0.5)
                for kk, vv in pl.items()}
        h_p, c_p, _ = m.lstm_cell(x, h_prev, c_prev, pert)
        assert not np.allclose(h_p, h_ref) or not np.allclose(c_p, c_ref), (
            f"perturbando il blocco '{k}' l'uscita della cella non cambia: "
            f"quel blocco non viene usato da lstm_cell"
        )

    h_gref, gg_ref = m.gru_cell(x, h_prev, pg)
    assert set(gg_ref) == set(_GRU_BLOCKS), (
        f"gates della GRU deve avere esattamente le chiavi {_GRU_BLOCKS}, "
        f"trovate {sorted(gg_ref)}"
    )
    for k in _GRU_BLOCKS:
        pert = {kk: (vv.copy() if kk != "b" + k else vv + 0.5)
                for kk, vv in pg.items()}
        h_p, _ = m.gru_cell(x, h_prev, pert)
        assert not np.allclose(h_p, h_gref), (
            f"perturbando il blocco '{k}' l'uscita della GRU non cambia: "
            f"quel blocco non viene usato da gru_cell"
        )


# ---------------------------------------------------------------------------
# (l) Coerenza fra la cella e il forward srotolato
# ---------------------------------------------------------------------------

def test_l_forward_coincide_con_la_cella_applicata_passo_passo():
    """`*_forward` deve essere esattamente lo srotolamento di `*_cell`, con lo
    stato che si propaga fra un passo e il successivo."""
    D, Hdim, T = 3, 4, 25
    rng = np.random.default_rng(555)
    X = rng.normal(size=(T, D))
    pl = _random_lstm_params(D, Hdim, 556)
    pg = _random_gru_params(D, Hdim, 557)
    h0 = rng.normal(size=Hdim) * 0.3
    c0 = rng.normal(size=Hdim) * 0.3

    H, C, G = m.lstm_forward(X, pl, h0=h0, c0=c0)
    h, c = h0.copy(), c0.copy()
    for t in range(T):
        h, c, g = m.lstm_cell(X[t], h, c, pl)
        assert_allclose(H[t], h, rtol=1e-12, atol=1e-15,
                        err_msg=f"H[{t}] non coincide con lstm_cell applicata "
                                "in sequenza: lo stato non si sta propagando")
        assert_allclose(C[t], c, rtol=1e-12, atol=1e-15,
                        err_msg=f"C[{t}] non coincide con lstm_cell in sequenza")
        for k in _LSTM_BLOCKS:
            assert_allclose(G[k][t], g[k], rtol=1e-12, atol=1e-15,
                            err_msg=f"gates_seq['{k}'][{t}] non coincide")

    Hg, Gg = m.gru_forward(X, pg, h0=h0)
    h = h0.copy()
    for t in range(T):
        h, g = m.gru_cell(X[t], h, pg)
        assert_allclose(Hg[t], h, rtol=1e-12, atol=1e-15,
                        err_msg=f"H[{t}] della GRU non coincide con gru_cell "
                                "applicata in sequenza")

    # h0 = None deve valere stato iniziale nullo
    H0, C0, _ = m.lstm_forward(X, pl)
    Hz, Cz, _ = m.lstm_forward(X, pl, h0=np.zeros(Hdim), c0=np.zeros(Hdim))
    assert_allclose(H0, Hz, rtol=1e-12, atol=1e-15,
                    err_msg="h0=None e c0=None devono equivalere a stati nulli")
    assert_allclose(C0, Cz, rtol=1e-12, atol=1e-15)


# ---------------------------------------------------------------------------
# (f) ESN: raggio spettrale esatto e sparsita' esatta
# ---------------------------------------------------------------------------

def test_f_reservoir_raggio_spettrale_e_sparsita_richiesti():
    """Il raggio spettrale non e' un iperparametro decorativo: e' IL parametro
    del reservoir, e va imposto riscalando la matrice dopo averla estratta."""
    for rho_target in (0.3, 0.9, 0.99, 1.5):
        Win, Wres = m.esn_reservoir(3, 80, rho_target, 0.5, 0.0, seed=4)
        assert Win.shape == (80, 3), f"Win deve avere shape (Nres, D), non {Win.shape}"
        assert Wres.shape == (80, 80), f"Wres deve avere shape (Nres, Nres)"
        rho = float(np.max(np.abs(np.linalg.eigvals(Wres))))
        assert abs(rho - rho_target) < 1e-8, (
            f"raggio spettrale richiesto {rho_target}, ottenuto {rho:.12f}. "
            "Va calcolato con np.linalg.eigvals (modulo massimo, gli "
            "autovalori sono complessi) e la matrice va MOLTIPLICATA per "
            "spectral_radius/rho"
        )
        assert np.max(np.abs(Win)) <= 0.5 + 1e-12, (
            "Win deve stare in [-input_scaling, +input_scaling]"
        )

    # sparsita': esattamente round(sparsity * Nres^2) entrate nulle
    Nres = 60
    for sp in (0.0, 0.5, 0.9):
        _, W = m.esn_reservoir(2, Nres, 0.9, 1.0, sp, seed=5)
        attesi = int(round(sp * Nres * Nres))
        ottenuti = int(np.sum(W == 0.0))
        assert ottenuti == attesi, (
            f"con sparsity={sp} servono esattamente {attesi} entrate nulle su "
            f"{Nres*Nres}, ne sono state contate {ottenuti}. Vanno scelte con "
            "rng.permutation (conteggio esatto), non con una maschera di "
            "Bernoulli (conteggio solo in media)"
        )
        rho = float(np.max(np.abs(np.linalg.eigvals(W))))
        assert abs(rho - 0.9) < 1e-8, (
            "il riscalamento al raggio spettrale va fatto DOPO aver azzerato "
            "le entrate, altrimenti la sparsificazione lo rovina"
        )

    # determinismo: stesso seed, stessa matrice
    a1, b1 = m.esn_reservoir(2, 30, 0.8, 1.0, 0.3, seed=123)
    a2, b2 = m.esn_reservoir(2, 30, 0.8, 1.0, 0.3, seed=123)
    assert np.array_equal(a1, a2) and np.array_equal(b1, b2), (
        "esn_reservoir deve essere deterministico dato il seed"
    )


# ---------------------------------------------------------------------------
# (g) IL test concettuale centrale: la echo state property
# ---------------------------------------------------------------------------

def test_g_echo_state_property_lo_stato_dimentica_lo_stato_iniziale():
    """ESP: lo stato del reservoir e' una funzione (un'eco) della sola storia
    degli input, non dello stato iniziale. Lo verifichiamo mandando due
    PREFISSI diversi (che portano il reservoir in due stati diversi) e poi lo
    STESSO input lungo: con rho = 0.9 le due traiettorie collassano fino alla
    precisione macchina, con rho = 1.5 restano separate."""
    D, Nres, T_pre, T_common = 1, 100, 60, 400
    rng = np.random.default_rng(31337)
    pre_a = rng.uniform(-1.0, 1.0, size=(T_pre, D))
    pre_b = rng.uniform(-1.0, 1.0, size=(T_pre, D))
    common = rng.uniform(-1.0, 1.0, size=(T_common, D))

    def distanza_traiettorie(rho):
        Win, Wres = m.esn_reservoir(D, Nres, rho, 0.3, 0.0, seed=7)
        Sa = m.esn_states(np.vstack([pre_a, common]), Win, Wres)
        Sb = m.esn_states(np.vstack([pre_b, common]), Win, Wres)
        d = np.linalg.norm(Sa[T_pre:] - Sb[T_pre:], axis=1)
        return d, Wres

    d_stabile, W09 = distanza_traiettorie(0.9)
    d_instabile, W15 = distanza_traiettorie(1.5)

    assert d_stabile[0] > 0.5, (
        "test degenere: dopo prefissi diversi i due stati devono partire "
        "davvero distanti"
    )
    assert np.max(d_stabile[-100:]) < 1e-10, (
        f"con raggio spettrale 0.9 le due traiettorie devono convergere; "
        f"distanza residua {np.max(d_stabile[-100:]):.3e}. Se non converge, "
        "controlla che esn_states parta SEMPRE dallo stato nullo e che la "
        "ricorrenza sia h = tanh(Win x + Wres h_prev)"
    )
    assert np.mean(d_instabile[-100:]) > 0.5, (
        f"con raggio spettrale 1.5 le traiettorie NON devono convergere "
        f"(distanza media residua {np.mean(d_instabile[-100:]):.3e}): senza "
        "echo state property lo stato dipende ancora dalla condizione "
        "iniziale e il reservoir non definisce una funzione della sequenza"
    )

    assert m.echo_state_property_holds(W09) is True, (
        "echo_state_property_holds deve essere True per rho = 0.9"
    )
    assert m.echo_state_property_holds(W15) is False, (
        "echo_state_property_holds deve essere False per rho = 1.5: la "
        "condizione necessaria e' sul RAGGIO SPETTRALE (massimo modulo degli "
        "autovalori), non sulla norma di Frobenius ne' sul massimo elemento"
    )


# ---------------------------------------------------------------------------
# (k) CASO LIMITE: leak rate e matrice effettiva (1-a)I + aW
# ---------------------------------------------------------------------------

def test_k_echo_state_property_col_leak_rate_usa_la_matrice_effettiva():
    """Con l'aggiornamento leaky la dinamica linearizzata e' governata da
    (1-a)I + aW, non da W. Un reservoir instabile puo' diventare stabile
    abbassando il leak rate, e viceversa."""
    W = np.diag([-2.0, 0.1])          # raggio spettrale 2
    assert m.echo_state_property_holds(W, 1.0) is False, (
        "con a = 1 e rho(W) = 2 la ESP non puo' valere"
    )
    # a = 0.4 -> autovalori 0.6 - 0.8 = -0.2  e  0.6 + 0.04 = 0.64, rho = 0.64
    assert m.echo_state_property_holds(W, 0.4) is True, (
        "con leak_rate = 0.4 la matrice effettiva (1-a)I + aW ha raggio "
        "spettrale 0.64 < 1: la ESP vale. Se il test fallisce, la funzione "
        "sta guardando W invece di (1-a)I + aW"
    )
    # matrice con autovalori complessi di modulo 0.5: stabile con a = 1
    R = 0.5 * np.array([[0.0, -1.0], [1.0, 0.0]])
    assert m.echo_state_property_holds(R, 1.0) is True, (
        "gli autovalori sono +-0.5i, modulo 0.5 < 1: il raggio spettrale va "
        "calcolato sul MODULO di autovalori complessi"
    )
    # rotazione di modulo 1.2: instabile
    assert m.echo_state_property_holds(1.2 * np.array([[0.0, -1.0], [1.0, 0.0]])) is False


# ---------------------------------------------------------------------------
# (h) ORACOLO INDIPENDENTE: la ridge regression del readout
# ---------------------------------------------------------------------------

def test_h_readout_risolve_esattamente_la_ridge_regression():
    """Oracolo: la ridge regression e' un minimi quadrati ordinari sul sistema
    AUMENTATO [S ; sqrt(ridge) I] w = [Y ; 0]. Lo risolviamo con
    np.linalg.lstsq, che non usa le equazioni normali."""
    rng = np.random.default_rng(999)
    N, Nres, K = 120, 25, 3
    S = rng.normal(size=(N, Nres))
    Y = rng.normal(size=(N, K))

    for ridge in (1e-6, 1e-2, 1.0, 10.0):
        Wout = m.esn_fit_readout(S, Y, ridge)
        assert Wout.shape == (Nres, K), (
            f"Wout deve avere shape (Nres, K) = ({Nres}, {K}), non {Wout.shape}"
        )
        A = np.vstack([S, np.sqrt(ridge) * np.eye(Nres)])
        b = np.vstack([Y, np.zeros((Nres, K))])
        atteso, *_ = np.linalg.lstsq(A, b, rcond=None)
        assert_allclose(Wout, atteso, rtol=1e-7, atol=1e-9,
                        err_msg=f"con ridge={ridge} la soluzione non coincide "
                                "con quella del sistema aumentato: la formula "
                                "e' (S^T S + ridge*I)^{-1} S^T Y, con "
                                "l'identita' di dimensione Nres (non N) e "
                                "senza dividere ridge per N")

    # target 1-D -> Wout 1-D, e coerenza con esn_predict
    y1 = Y[:, 0]
    w1 = m.esn_fit_readout(S, y1, 1e-3)
    assert w1.shape == (Nres,), (
        f"con targets 1-D il readout deve essere 1-D, shape {w1.shape}"
    )
    assert_allclose(m.esn_predict(S, w1), S @ w1, rtol=1e-12, atol=1e-12,
                    err_msg="esn_predict deve essere il prodotto states @ Wout")

    # caso limite: ridge -> 0 su un sistema sovradeterminato ben condizionato
    # deve coincidere con i minimi quadrati non regolarizzati
    ols, *_ = np.linalg.lstsq(S, Y, rcond=None)
    assert_allclose(m.esn_fit_readout(S, Y, 0.0), ols, rtol=1e-6, atol=1e-8,
                    err_msg="con ridge = 0 si deve ricadere nei minimi quadrati")


# ---------------------------------------------------------------------------
# (i) L'ESN risolve davvero il memory task
# ---------------------------------------------------------------------------

def test_i_esn_risolve_il_memory_task_meglio_della_baseline_sulla_media():
    """Reservoir fisso e casuale, readout lineare addestrato: e' tutto quello
    che serve per ricordare l'input di 5 passi fa molto meglio di chi predice
    sempre la media."""
    T, delay, Nres, washout, n_train = 2000, 5, 200, 100, 1200
    X, Y = m.make_memory_task(T, delay, seed=3)
    Win, Wres = m.esn_reservoir(1, Nres, 0.9, 0.5, 0.0, seed=5)
    S = m.esn_states(X, Win, Wres, leak_rate=1.0, washout=washout)
    Yw = Y[washout:]

    assert S.shape == (T - washout, Nres), (
        f"con washout={washout} gli stati devono avere shape "
        f"({T - washout}, {Nres}), non {S.shape}"
    )

    Wout = m.esn_fit_readout(S[:n_train], Yw[:n_train], ridge=1e-6)
    pred = m.esn_predict(S[n_train:], Wout)
    y_test = Yw[n_train:]

    mse_esn = float(np.mean((pred - y_test) ** 2))
    media_train = Yw[:n_train].mean(axis=0)
    mse_baseline = float(np.mean((media_train - y_test) ** 2))

    assert mse_baseline > 0.25, (
        "test degenere: la baseline sulla media dovrebbe avere MSE pari alla "
        "varianza del target, circa 1/3"
    )
    assert mse_esn < 0.05 * mse_baseline, (
        f"MSE dell'ESN {mse_esn:.5f} contro baseline {mse_baseline:.5f}: un "
        "reservoir da 200 unita' con rho = 0.9 deve ricordare un ritardo di 5 "
        "quasi esattamente. Errori tipici: addestrare anche Win/Wres, non "
        "scartare il washout, allineare male stati e target"
    )
    assert mse_esn == mse_esn, "MSE nan: readout mal condizionato"


# ---------------------------------------------------------------------------
# (j) Shape e semantica del leaky integrator
# ---------------------------------------------------------------------------

def test_j_esn_states_shape_e_integrazione_leaky():
    """Shape (T, Nres) con leak_rate = 1 e washout = 0; il washout taglia in
    testa; leak_rate < 1 rende gli stati piu' lisci."""
    D, Nres, T = 2, 40, 300
    Win, Wres = m.esn_reservoir(D, Nres, 0.9, 1.0, 0.0, seed=8)
    X = np.random.default_rng(88).uniform(-1.0, 1.0, size=(T, D))

    S = m.esn_states(X, Win, Wres, leak_rate=1.0, washout=0)
    assert S.shape == (T, Nres), (
        f"con leak_rate=1 e washout=0 la shape deve essere ({T}, {Nres}), "
        f"non {S.shape}. Si restituisce uno stato PER OGNI passo di input"
    )
    assert np.all(np.abs(S) <= 1.0), "con leak_rate=1 gli stati sono tanh, in [-1,1]"

    # il washout taglia solo la testa, non ricalcola nulla
    Sw = m.esn_states(X, Win, Wres, leak_rate=1.0, washout=50)
    assert Sw.shape == (T - 50, Nres), (
        f"con washout=50 la shape deve essere ({T-50}, {Nres}), non {Sw.shape}"
    )
    assert_allclose(Sw, S[50:], rtol=1e-12, atol=1e-15,
                    err_msg="il washout deve SCARTARE i primi stati, non "
                            "ripartire da uno stato diverso")

    # primo stato: h_1 = tanh(Win x_1) perche' h_0 = 0
    assert_allclose(S[0], np.tanh(Win @ X[0]), rtol=1e-12, atol=1e-15,
                    err_msg="lo stato iniziale h_0 deve essere il vettore "
                            "nullo, quindi h_1 = tanh(Win x_1)")

    # leaky: h_1 = a * tanh(Win x_1)
    a = 0.3
    Sl = m.esn_states(X, Win, Wres, leak_rate=a, washout=0)
    assert_allclose(Sl[0], a * np.tanh(Win @ X[0]), rtol=1e-12, atol=1e-15,
                    err_msg="con h_0 = 0 la formula leaky da' "
                            "h_1 = (1-a)*0 + a*tanh(Win x_1)")
    var_l = float(np.mean(np.var(np.diff(Sl, axis=0), axis=0)))
    var_1 = float(np.mean(np.var(np.diff(S, axis=0), axis=0)))
    assert var_l < var_1, (
        "un leak rate piccolo deve rendere la dinamica piu' lenta (incrementi "
        "di stato piu' piccoli): e' il senso dell'integratore leaky"
    )
