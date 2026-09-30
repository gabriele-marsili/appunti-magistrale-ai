"""Test di autovalutazione - GDL25 "Generative Adversarial Networks".

Esecuzione:
    pytest test_gan.py -v                # sullo skeleton
    GDL_SOL=1 pytest test_gan.py -v      # sulla soluzione di riferimento
"""

import os, sys, pathlib, importlib

HERE = pathlib.Path(__file__).parent
if os.environ.get("GDL_SOL"):
    sys.path.insert(0, str(HERE / "soluzione"))
    m = importlib.import_module("gan_sol")
else:
    sys.path.insert(0, str(HERE))
    m = importlib.import_module("gan")

import numpy as np
from numpy.testing import assert_allclose

LOG2 = float(np.log(2.0))
LOG4 = float(np.log(4.0))


# ---------------------------------------------------------------------------
# helper locali ai test (non fanno parte dell'API da implementare)
# ---------------------------------------------------------------------------

def _logistic_D(x):
    """Un discriminatore qualunque, liscio e mai 0 ne' 1: sigma(0.8 x + 0.3)."""
    return 1.0 / (1.0 + np.exp(-(0.8 * np.asarray(x, dtype=float) + 0.3)))


def _disjoint_pair():
    """Due densita' uniformi a supporto DAVVERO disgiunto sulla stessa griglia."""
    p = m.uniform_density(m.GRID, -3.0, -1.0)
    q = m.uniform_density(m.GRID, 1.0, 3.0)
    return p, q


# ---------------------------------------------------------------------------
# 1. Discriminatore ottimo
# ---------------------------------------------------------------------------

def test_optimal_discriminator_forma_chiusa_range_e_caso_0_su_0():
    """D* = p_data/(p_data+p_g): sta in [0,1], vale 0.5 se le due densita'
    coincidono, e non produce nan dove entrambe sono nulle."""
    p_data = np.array([0.0, 0.2, 0.5, 1.0, 0.0, 3.0])
    p_g = np.array([0.0, 0.6, 0.5, 0.0, 2.0, 1.0])
    D = np.asarray(m.optimal_discriminator(p_data, p_g), dtype=float)

    assert D.shape == p_data.shape, f"shape attesa {p_data.shape}, ottenuta {D.shape}"
    assert np.all(np.isfinite(D)), (
        "D* contiene nan/inf: il punto in cui p_data = p_g = 0 va gestito "
        "esplicitamente, la divisione 0/0 non e' un caso da lasciare a numpy"
    )
    assert np.all((D >= 0.0) & (D <= 1.0)), (
        "D* e' una probabilita' (verosimiglianza che x sia reale): deve stare in [0,1]"
    )
    assert_allclose(D[0], 0.5, rtol=0, atol=0,
                    err_msg="dove p_data + p_g = 0 la convenzione richiesta e' D* = 0.5")
    assert_allclose(D[1:], [0.25, 0.5, 1.0, 0.0, 0.75], rtol=1e-6, atol=1e-9,
                    err_msg="D* non segue p_data/(p_data + p_g)")

    # Il caso che conta davvero: generatore perfetto -> discriminatore inutile.
    D_eq = np.asarray(m.optimal_discriminator(m.P_DATA, m.P_DATA), dtype=float)
    assert_allclose(D_eq, np.full_like(D_eq, 0.5), rtol=1e-12, atol=1e-12,
                    err_msg="con p_g == p_data il discriminatore ottimo deve valere 0.5 ovunque")


def test_optimal_discriminator_oracolo_massimizzazione_puntuale():
    """ORACOLO INDIPENDENTE: l'integrando di C(D,G) e' separabile in x, quindi
    D* si puo' trovare massimizzando a forza bruta ``p_d log d + p_g log(1-d)``
    punto per punto su una griglia fitta di d. Deve coincidere con la formula
    chiusa, che qui non viene mai usata dall'oracolo."""
    p_data = m.P_DATA
    p_g = m.generator_density(m.GRID, m.THETA_OVERLAP)

    idx = np.arange(0, m.GRID.size, 40)          # 41 ascisse
    pd_s = p_data[idx]
    pg_s = p_g[idx]

    d_grid = np.linspace(1e-6, 1.0 - 1e-6, 20001)          # passo 5e-5
    obj = (pd_s[:, None] * np.log(d_grid)[None, :]
           + pg_s[:, None] * np.log1p(-d_grid)[None, :])
    d_brute = d_grid[np.argmax(obj, axis=1)]

    D = np.asarray(m.optimal_discriminator(p_data, p_g), dtype=float)[idx]

    assert np.all(np.isfinite(D)), "D* non deve contenere nan/inf"
    assert_allclose(D, d_brute, rtol=0, atol=2e-4, err_msg=(
        "il massimizzatore numerico punto per punto di p_data*log d + "
        "p_g*log(1-d) non coincide con il D* restituito: la forma chiusa "
        "p_data/(p_data+p_g) NON e' quella implementata"
    ))
    interior = (d_brute > 0.05) & (d_brute < 0.95)
    assert interior.sum() >= 10, (
        "lo scenario di test degenera: servono ascisse in cui D* e' davvero "
        "interno a (0,1) perche' l'oracolo sia informativo"
    )


# ---------------------------------------------------------------------------
# 2. Il valore del gioco
# ---------------------------------------------------------------------------

def test_valore_del_gioco_oracolo_montecarlo():
    """ORACOLO INDIPENDENTE: C(D,G) e' una somma di due valori attesi. Li
    stimiamo campionando da p_data e da p_g (niente quadratura) e confrontiamo
    con l'integrale. Metodo diverso, stesso numero."""
    n = 200000
    for theta in (m.THETA_OVERLAP, m.THETA_FAR):
        p_g = m.generator_density(m.GRID, theta)
        D = _logistic_D(m.GRID)
        exact = m.discriminator_loss(D, m.P_DATA, p_g, m.GRID)

        rng = np.random.default_rng(20250425)
        x_real = m.sample_from_grid_density(m.GRID, m.P_DATA, n, rng)
        x_fake = m.sample_from_grid_density(m.GRID, p_g, n, rng)
        mc = float(np.mean(np.log(_logistic_D(x_real)))
                   + np.mean(np.log1p(-_logistic_D(x_fake))))

        assert abs(exact - mc) < 1e-2, (
            f"quadratura {exact:.5f} vs Monte Carlo {mc:.5f} (theta={theta}): "
            "il valore del gioco non e' E_pdata[log D] + E_pg[log(1-D)]; "
            "controlla di aver pesato ciascun logaritmo con la SUA densita'"
        )


def test_D_ottimo_massimizza_il_valore_del_gioco():
    """PROPRIETA': D* e' il massimo di C(D,G) a G fisso. Nessun altro
    discriminatore, casuale o "ragionevole", puo' fare meglio."""
    p_g = m.generator_density(m.GRID, m.THETA_OVERLAP)
    D_star = np.asarray(m.optimal_discriminator(m.P_DATA, p_g), dtype=float)
    v_star = m.discriminator_loss(D_star, m.P_DATA, p_g, m.GRID)

    assert np.isfinite(v_star), "C(D*,G) deve essere finito"

    rng = np.random.default_rng(31415)
    candidati = [_logistic_D(m.GRID), np.full(m.GRID.size, 0.5)]
    for _ in range(8):
        candidati.append(rng.uniform(1e-3, 1.0 - 1e-3, size=m.GRID.size))
    for scale in (0.05, 0.2):
        candidati.append(np.clip(D_star + rng.normal(0.0, scale, size=m.GRID.size),
                                 1e-3, 1.0 - 1e-3))

    for k, D in enumerate(candidati):
        v = m.discriminator_loss(D, m.P_DATA, p_g, m.GRID)
        assert v < v_star, (
            f"il candidato {k} ottiene C = {v:.6f} > C(D*,G) = {v_star:.6f}: "
            "o D* non e' il massimizzatore, o discriminator_loss ha il segno "
            "sbagliato (il discriminatore MASSIMIZZA C, non la minimizza)"
        )


def test_loss_del_generatore_valori_analitici_e_segni():
    """Con D costante gli integrali si fanno a mano: se p_g e' normalizzata,
    E_pg[log(1-c)] = log(1-c) e -E_pg[log c] = -log c. Verifica anche il segno,
    che e' la convenzione su cui si confrontano i due gradienti."""
    p_g = m.generator_density(m.GRID, m.THETA_OVERLAP)
    for c in (0.5, 0.2, 0.9):
        D = np.full(m.GRID.size, c)
        mm = m.generator_loss_minimax(D, p_g, m.GRID)
        ns = m.generator_loss_nonsaturating(D, p_g, m.GRID)
        assert_allclose(mm, np.log(1.0 - c), rtol=1e-6, atol=1e-9, err_msg=(
            f"con D costante = {c} la loss minimax deve valere log(1-D) = "
            f"{np.log(1.0 - c):.6f}; hai forse usato log D al posto di log(1-D)"
        ))
        assert_allclose(ns, -np.log(c), rtol=1e-6, atol=1e-9, err_msg=(
            f"con D costante = {c} la loss non-saturating deve valere -log D = "
            f"{-np.log(c):.6f}; il segno meno serve a renderla una MINIMIZZAZIONE"
        ))
        assert mm <= 0.0 < ns, (
            "con D in (0,1) la minimax e' <= 0 e la non-saturating e' > 0: "
            "se non lo sono hai scambiato le due varianti o omesso il segno"
        )


# ---------------------------------------------------------------------------
# 3. Divergenze
# ---------------------------------------------------------------------------

def test_kl_convenzione_zero_log_zero_e_non_negativita():
    """La KL fra densita' con zeri esatti non deve produrre nan: dove p = 0 il
    contributo e' 0 per convenzione, qualunque cosa faccia q."""
    p, q = _disjoint_pair()
    mix = 0.5 * (p + q)

    assert_allclose(m.kl_divergence(p, p, m.GRID), 0.0, rtol=0, atol=1e-10,
                    err_msg="KL(p||p) deve essere esattamente 0")
    assert_allclose(m.kl_divergence(m.P_DATA, m.P_DATA, m.GRID), 0.0,
                    rtol=0, atol=1e-10, err_msg="KL(p||p) deve essere esattamente 0")

    k_pm = m.kl_divergence(p, mix, m.GRID)
    assert np.isfinite(k_pm), (
        "KL(p || m) e' diventata nan: sui punti dove p = 0 e m = 0 stai "
        "calcolando 0 * log(0/0) invece di applicare la convenzione 0 log 0 = 0"
    )
    assert_allclose(k_pm, LOG2, rtol=1e-6, atol=1e-9, err_msg=(
        "con supporti disgiunti si ha m = p/2 sul supporto di p, quindi "
        "KL(p||m) = log 2 esatto"
    ))

    k_pq = m.kl_divergence(p, q, m.GRID)
    assert np.isfinite(k_pq), (
        "con supporti disgiunti la KL e' matematicamente +inf, ma qui il "
        "logaritmo pavimentato (safe_log) deve restituire un numero grande e "
        "FINITO, non nan"
    )
    assert k_pq > 100.0, "KL fra supporti disgiunti deve essere enorme, non ~0"

    for a, b in [(m.P_DATA, m.generator_density(m.GRID, m.THETA_OVERLAP)),
                 (m.generator_density(m.GRID, m.THETA_FAR), m.P_DATA)]:
        assert m.kl_divergence(a, b, m.GRID) >= -1e-9, "la KL non puo' essere negativa"


def test_jsd_simmetrica_non_negativa_limitata_da_log2():
    """PROPRIETA': la JSD e' simmetrica, non negativa e <= log 2. Sono le tre
    proprieta' che rendono sensato dire che il GAN "minimizza una distanza"."""
    coppie = [
        (m.P_DATA, m.generator_density(m.GRID, m.THETA_OVERLAP)),
        (m.P_DATA, m.generator_density(m.GRID, m.THETA_FAR)),
        (m.generator_density(m.GRID, [1.0, np.log(0.7)]),
         m.gaussian_mixture_density(m.GRID, [-2.0, 2.5], [0.6, 0.9], [0.3, 0.7])),
        _disjoint_pair(),
    ]
    for k, (p, q) in enumerate(coppie):
        a = m.jsd(p, q, m.GRID)
        b = m.jsd(q, p, m.GRID)
        assert np.isfinite(a) and np.isfinite(b), f"JSD non finita sulla coppia {k}"
        assert_allclose(a, b, rtol=1e-9, atol=1e-12, err_msg=(
            f"JSD(p||q) = {a:.9f} != JSD(q||p) = {b:.9f} sulla coppia {k}: la "
            "JSD e' simmetrica per costruzione, la misclatura m = (p+q)/2 deve "
            "essere la STESSA nei due termini"
        ))
        assert a >= -1e-9, f"JSD negativa ({a}) sulla coppia {k}"
        assert a <= LOG2 + 1e-9, (
            f"JSD = {a:.9f} > log 2 sulla coppia {k}: il limite superiore log 2 "
            "e' violato, probabilmente m non e' la media (p+q)/2 o mancano i "
            "coefficienti 1/2 davanti alle due KL"
        )
    assert m.jsd(m.P_DATA, m.P_DATA, m.GRID) < 1e-10, "JSD(p||p) deve essere 0"


def test_value_at_optimum_coincide_col_percorso_numerico():
    """PROPRIETA' CENTRALE: C(D*,G) = -log 4 + 2 JSD(p_data||p_g). I due lati
    dell'identita' vengono calcolati per strade diverse (uno sostituisce D*
    nell'integrale, l'altro passa dalle KL) e devono dare lo stesso numero."""
    scenari = [
        m.generator_density(m.GRID, m.THETA_OVERLAP),
        m.generator_density(m.GRID, m.THETA_FAR),
        m.generator_density(m.GRID, [-1.5, np.log(0.5)]),
        m.gaussian_mixture_density(m.GRID, [-1.5, 1.5], [0.8, 0.4], [0.4, 0.6]),
        m.P_DATA,
    ]
    for k, p_g in enumerate(scenari):
        numerico = m.discriminator_loss(
            m.optimal_discriminator(m.P_DATA, p_g), m.P_DATA, p_g, m.GRID)
        chiuso = m.value_at_optimum(m.P_DATA, p_g, m.GRID)
        assert_allclose(chiuso, numerico, rtol=1e-6, atol=1e-9, err_msg=(
            f"scenario {k}: -log4 + 2*JSD = {chiuso:.9f} ma "
            f"C(D*,G) integrato vale {numerico:.9f}. Se la differenza e' "
            "circa log 4 = 1.386 hai dimenticato il termine costante; se e' un "
            "fattore 2 hai confuso 2*JSD con JSD"
        ))
        assert chiuso >= -LOG4 - 1e-9, (
            f"scenario {k}: C(D*,G) = {chiuso:.9f} < -log 4 = {-LOG4:.9f}. "
            "-log 4 e' il MINIMO globale su G, nessun generatore puo' scendere sotto"
        )


# ---------------------------------------------------------------------------
# 4. Casi limite
# ---------------------------------------------------------------------------

def test_caso_limite_pg_uguale_a_pdata():
    """CASO LIMITE: generatore perfetto. D* = 1/2 ovunque, JSD = 0, il valore
    del gioco vale ESATTAMENTE -log 4 = -1.386... ed e' il minimo su G."""
    D = np.asarray(m.optimal_discriminator(m.P_DATA, m.P_DATA), dtype=float)
    assert_allclose(D, 0.5, rtol=1e-12, atol=1e-12,
                    err_msg="con p_g == p_data il discriminatore non puo' fare meglio del caso")

    j = m.jsd(m.P_DATA, m.P_DATA, m.GRID)
    assert abs(j) < 1e-10, f"JSD(p||p) = {j:.3e}, deve essere 0"

    v_chiuso = m.value_at_optimum(m.P_DATA, m.P_DATA, m.GRID)
    v_num = m.discriminator_loss(D, m.P_DATA, m.P_DATA, m.GRID)
    assert_allclose(v_chiuso, -LOG4, rtol=0, atol=1e-9, err_msg=(
        f"con p_g = p_data il valore all'ottimo deve essere -log 4 = {-LOG4:.9f}"))
    assert_allclose(v_num, -LOG4, rtol=0, atol=1e-9, err_msg=(
        "anche per la via numerica: 2 * log(1/2) = -log 4"))

    # e' davvero il minimo: qualunque altro p_g da' un valore piu' alto
    for theta in ([0.3, np.log(0.9)], [1.0, np.log(1.4)], m.THETA_FAR):
        alt = m.value_at_optimum(m.P_DATA, m.generator_density(m.GRID, theta), m.GRID)
        assert alt > v_chiuso, (
            f"theta={theta} da' {alt:.9f} <= {-LOG4:.9f}: il minimo su G del "
            "valore all'ottimo si raggiunge SOLO in p_g = p_data"
        )


def test_caso_limite_supporti_disgiunti():
    """CASO LIMITE: supporti disgiunti. D* e' 1 dove c'e' solo p_data, 0 dove
    c'e' solo p_g, 0.5 dove non c'e' nulla; JSD satura a log 2 e il valore del
    gioco vale 0. Nessun nan, nessun log(0) non gestito."""
    p, q = _disjoint_pair()
    D = np.asarray(m.optimal_discriminator(p, q), dtype=float)

    assert np.all(np.isfinite(D)), "D* contiene nan/inf sui punti a massa nulla"
    solo_dati = p > 0
    solo_gen = q > 0
    nessuno = ~(solo_dati | solo_gen)
    assert_allclose(D[solo_dati], 1.0, rtol=0, atol=0,
                    err_msg="dove c'e' solo p_data il discriminatore ottimo vale 1")
    assert_allclose(D[solo_gen], 0.0, rtol=0, atol=0,
                    err_msg="dove c'e' solo p_g il discriminatore ottimo vale 0")
    assert_allclose(D[nessuno], 0.5, rtol=0, atol=0,
                    err_msg="dove p_data = p_g = 0 la convenzione richiesta e' 0.5")

    j = m.jsd(p, q, m.GRID)
    assert_allclose(j, LOG2, rtol=1e-6, atol=1e-9, err_msg=(
        f"con supporti disgiunti la JSD satura al suo massimo log 2 = "
        f"{LOG2:.9f}, ottenuto {j:.9f}"))

    v_num = m.discriminator_loss(D, p, q, m.GRID)
    v_chiuso = m.value_at_optimum(p, q, m.GRID)
    assert np.isfinite(v_num), (
        "C(D*,G) e' inf/nan: dove p_data = 0 il termine p_data*log D deve fare "
        "0 anche se D = 0 (convenzione 0 log 0 = 0), non -inf"
    )
    assert_allclose(v_num, 0.0, rtol=0, atol=1e-9, err_msg=(
        "a supporti disgiunti D* azzecca tutto: log D* = 0 sui dati e "
        "log(1-D*) = 0 sui falsi, quindi C(D*,G) = 0"))
    assert_allclose(v_chiuso, 0.0, rtol=0, atol=1e-9, err_msg=(
        "-log 4 + 2 log 2 = 0: le due strade devono coincidere anche qui"))

    # e' proprio la situazione in cui il generatore non riceve segnale
    g_mm = m.generator_gradient([2.0, np.log(0.3)], p, m.GRID, "minimax")
    assert np.all(np.isfinite(g_mm)), "il gradiente minimax non deve essere nan"


# ---------------------------------------------------------------------------
# 5. Saturazione del gradiente
# ---------------------------------------------------------------------------

def test_generator_gradient_congela_il_discriminatore():
    """Il gradiente del generatore si calcola a D FISSO. Se D venisse
    ricalcolato per ogni theta perturbato si differenzierebbe -log4 + 2*JSD,
    che e' un'altra funzione: il test distingue i due casi."""
    theta = np.asarray(m.THETA_OVERLAP, dtype=float)
    h = 1e-4
    p_g0 = m.generator_density(m.GRID, theta)
    D_fisso = m.optimal_discriminator(m.P_DATA, p_g0)

    for variante, loss in (("minimax", m.generator_loss_minimax),
                           ("nonsaturating", m.generator_loss_nonsaturating)):
        atteso = np.zeros(2)
        mobile = np.zeros(2)
        for i in range(2):
            tp = theta.copy(); tp[i] += h
            tm = theta.copy(); tm[i] -= h
            pgp = m.generator_density(m.GRID, tp)
            pgm = m.generator_density(m.GRID, tm)
            atteso[i] = (loss(D_fisso, pgp, m.GRID)
                         - loss(D_fisso, pgm, m.GRID)) / (2.0 * h)
            mobile[i] = (loss(m.optimal_discriminator(m.P_DATA, pgp), pgp, m.GRID)
                         - loss(m.optimal_discriminator(m.P_DATA, pgm), pgm, m.GRID)) / (2.0 * h)

        g = np.asarray(m.generator_gradient(theta, m.P_DATA, m.GRID, variante, h=h),
                       dtype=float)
        assert g.shape == (2,), f"gradiente di shape {g.shape}, attesa (2,)"
        assert_allclose(g, atteso, rtol=1e-5, atol=1e-9, err_msg=(
            f"[{variante}] il gradiente non coincide con quello a D congelato "
            f"({atteso}); ottenuto {g}, mentre a D ricalcolato verrebbe {mobile}"
        ))
        assert np.max(np.abs(atteso - mobile)) > 1e-3, (
            "il test degenera: su questo scenario le due varianti di gradiente "
            "coincidono e non distinguono nulla"
        )


def test_saturazione_del_gradiente_minimax():
    """IL PUNTO DELL'ESERCIZIO. Con p_g quasi disgiunta da p_data il
    discriminatore e' quasi perfetto: la loss minimax si appiattisce e il suo
    gradiente crolla di ordini di grandezza, mentre quello non-saturating
    resta di ordine 1. Controprova: con distribuzioni sovrapposte i due
    gradienti sono confrontabili."""
    p_g = m.generator_density(m.GRID, m.THETA_FAR)
    D = np.asarray(m.optimal_discriminator(m.P_DATA, p_g), dtype=float)
    massa_media_D = m.integrate(p_g * D, m.GRID)
    assert massa_media_D < 1e-5, (
        f"E_pg[D*] = {massa_media_D:.3e}: lo scenario THETA_FAR dovrebbe avere "
        "il discriminatore quasi perfetto sui campioni falsi"
    )

    g_mm = np.asarray(m.generator_gradient(m.THETA_FAR, m.P_DATA, m.GRID, "minimax"),
                      dtype=float)
    g_ns = np.asarray(m.generator_gradient(m.THETA_FAR, m.P_DATA, m.GRID, "nonsaturating"),
                      dtype=float)
    n_mm = float(np.linalg.norm(g_mm))
    n_ns = float(np.linalg.norm(g_ns))

    assert np.all(np.isfinite(g_mm)) and np.all(np.isfinite(g_ns)), (
        "gradienti non finiti: log D con D ~ 0 va gestito con safe_log")
    assert n_mm < 1e-3, (
        f"|grad minimax| = {n_mm:.3e}: dovrebbe essere numericamente nullo. "
        "Se e' di ordine 1 stai probabilmente ricalcolando D dentro le "
        "differenze finite, oppure hai scambiato le due varianti"
    )
    assert n_ns > 1.0, (
        f"|grad non-saturating| = {n_ns:.3e}: dovrebbe restare di ordine 1. "
        "Se e' minuscolo hai usato log(1-D) al posto di log D"
    )
    assert n_ns / n_mm > 1e4, (
        f"rapporto |grad ns| / |grad mm| = {n_ns / n_mm:.3e}: la saturazione "
        "della minimax deve essere di ORDINI DI GRANDEZZA, non di un fattore 2"
    )
    assert g_ns[0] > 0.0, (
        "il gradiente non-saturating rispetto alla media del generatore deve "
        "essere positivo (la discesa deve spostare p_g verso sinistra, dove "
        "stanno i dati); se e' negativo il segno della loss e' invertito"
    )

    # controprova: con buona sovrapposizione la minimax NON e' saturata
    o_mm = float(np.linalg.norm(
        m.generator_gradient(m.THETA_OVERLAP, m.P_DATA, m.GRID, "minimax")))
    o_ns = float(np.linalg.norm(
        m.generator_gradient(m.THETA_OVERLAP, m.P_DATA, m.GRID, "nonsaturating")))
    assert 0.05 < o_mm / o_ns < 20.0, (
        f"con distribuzioni sovrapposte il rapporto vale {o_mm / o_ns:.3f}: "
        "li' i due gradienti devono essere confrontabili, la saturazione e' un "
        "fenomeno del regime 'discriminatore quasi perfetto', non una proprieta' "
        "generale della minimax"
    )


def test_train_generator_solo_il_nonsaturating_si_muove():
    """Partendo da un generatore lontano dai dati, la discesa minimax resta
    inchiodata mentre quella non-saturating raggiunge una moda dei dati."""
    lr, n_steps = 0.01, 60

    th_mm, loss_mm, gn_mm = m.train_generator(
        m.THETA_FAR, m.P_DATA, m.GRID, "minimax", lr=lr, n_steps=n_steps)
    th_ns, loss_ns, gn_ns = m.train_generator(
        m.THETA_FAR, m.P_DATA, m.GRID, "nonsaturating", lr=lr, n_steps=n_steps)

    for nome, th, loss, gn in (("minimax", th_mm, loss_mm, gn_mm),
                               ("nonsaturating", th_ns, loss_ns, gn_ns)):
        assert th.shape == (n_steps + 1, 2), (
            f"[{nome}] thetas di shape {th.shape}, attesa ({n_steps + 1}, 2): "
            "la traiettoria include lo stato iniziale")
        assert loss.shape == (n_steps + 1,), (
            f"[{nome}] losses di shape {loss.shape}, attesa ({n_steps + 1},)")
        assert gn.shape == (n_steps,), (
            f"[{nome}] grad_norms di shape {gn.shape}, attesa ({n_steps},)")
        assert_allclose(th[0], np.asarray(m.THETA_FAR, dtype=float),
                        rtol=0, atol=0,
                        err_msg=f"[{nome}] thetas[0] deve essere theta0")
        assert np.all(np.isfinite(th)) and np.all(np.isfinite(loss)), (
            f"[{nome}] traiettoria con nan/inf")

    spost_mm = abs(float(th_mm[-1, 0] - th_mm[0, 0]))
    spost_ns = abs(float(th_ns[-1, 0] - th_ns[0, 0]))
    assert spost_mm < 1e-3, (
        f"la media del generatore si e' spostata di {spost_mm:.3e} con la "
        "minimax: dovrebbe essere praticamente ferma, il gradiente e' saturo"
    )
    assert spost_ns > 2.0, (
        f"la media del generatore si e' spostata solo di {spost_ns:.3f} con la "
        "non-saturating: quella variante il segnale ce l'ha e deve usarlo"
    )
    assert spost_ns / max(spost_mm, 1e-300) > 1e3, (
        "le due varianti devono differire di ordini di grandezza, non di poco")

    mode = min(abs(float(th_ns[-1, 0]) - 1.5), abs(float(th_ns[-1, 0]) + 1.5))
    assert mode < 1.0, (
        f"la non-saturating ha portato la media a {float(th_ns[-1, 0]):.3f}, "
        "lontano da entrambe le mode dei dati (-1.5 e +1.5)"
    )
    assert loss_ns[-1] < 0.2 * loss_ns[0], (
        f"la loss non-saturating e' passata da {loss_ns[0]:.3f} a "
        f"{loss_ns[-1]:.3f}: deve calare in modo netto")
    assert abs(loss_mm[-1] - loss_mm[0]) < 1e-6, (
        f"la loss minimax e' passata da {loss_mm[0]:.3e} a {loss_mm[-1]:.3e}: "
        "in regime saturo non deve muoversi")
    assert float(np.max(gn_mm)) < float(np.min(gn_ns)) * 1e-3, (
        f"norma massima del gradiente minimax {float(np.max(gn_mm)):.3e} vs "
        f"minima del non-saturating {float(np.min(gn_ns)):.3e}: la separazione "
        "deve valere lungo TUTTA la traiettoria")
