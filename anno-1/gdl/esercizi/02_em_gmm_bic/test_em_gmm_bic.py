"""Suite di autovalutazione per l'esercizio `em_gmm_bic`.

    pytest test_em_gmm_bic.py -v            # gira sullo skeleton (deve fallire)
    GDL_SOL=1 pytest test_em_gmm_bic.py -v  # gira sulla soluzione (deve passare)
"""

import os, sys, pathlib, importlib

HERE = pathlib.Path(__file__).parent
if os.environ.get("GDL_SOL"):
    sys.path.insert(0, str(HERE / "soluzione"))
    m = importlib.import_module("em_gmm_bic_sol")
else:
    sys.path.insert(0, str(HERE))
    m = importlib.import_module("em_gmm_bic")

import math
import numpy as np


# --------------------------------------------------------------------------- #
# Dataset condivisi (deterministici)                                           #
# --------------------------------------------------------------------------- #
COV_ISO = np.eye(2) * 0.8

# tre blob ben separati
X_TRE, Y_TRE = m.make_blobs_like(
    120, [[0.0, 0.0], [6.0, 0.0], [3.0, 5.0]], COV_ISO, seed=0
)
# due blob sovrapposti, covarianza correlata
X_DUE, Y_DUE = m.make_blobs_like(
    100, [[0.0, 0.0], [1.5, 0.8]], np.array([[[1.0, 0.5], [0.5, 1.0]]] * 2), seed=4
)
# 3D
X_3D, Y_3D = m.make_blobs_like(
    90, [[0.0, 0.0, 0.0], [2.0, 2.0, -1.0]], np.eye(3) * 1.2, seed=2
)


# --------------------------------------------------------------------------- #
# 1. Densita' gaussiana                                                        #
# --------------------------------------------------------------------------- #
def test_log_gaussian_pdf_contro_definizione():
    """ORACOLO: confronto con la formula ingenua che usa inv() e det().

    La formula di riferimento e' scritta in modo diverso dall'implementazione
    attesa (inversa esplicita + determinante, invece di Cholesky): su un caso
    ben condizionato le due devono coincidere fino alla precisione macchina.
    """
    rng = np.random.default_rng(11)
    D = 3
    A = rng.normal(size=(D, D))
    Sigma = A @ A.T + 2.0 * np.eye(D)
    mu = rng.normal(size=D)
    X = rng.normal(size=(25, D)) * 2.0

    inv = np.linalg.inv(Sigma)
    det = np.linalg.det(Sigma)
    atteso = np.empty(X.shape[0])
    for n in range(X.shape[0]):
        d = X[n] - mu
        atteso[n] = -0.5 * (
            D * math.log(2.0 * math.pi) + math.log(det) + float(d @ inv @ d)
        )

    ottenuto = m.log_gaussian_pdf(X, mu, Sigma)
    assert ottenuto.shape == (X.shape[0],), (
        f"log_gaussian_pdf deve restituire shape (N,), ottenuto {ottenuto.shape}"
    )
    np.testing.assert_allclose(
        ottenuto,
        atteso,
        rtol=1e-6,
        atol=1e-9,
        err_msg="log_gaussian_pdf non coincide con -0.5*(D log 2pi + log|Sigma| + Mahalanobis)",
    )
    np.testing.assert_allclose(
        m.gaussian_pdf(X, mu, Sigma),
        np.exp(atteso),
        rtol=1e-6,
        atol=1e-12,
        err_msg="gaussian_pdf deve essere esattamente exp(log_gaussian_pdf)",
    )


def test_gaussian_pdf_integra_a_uno():
    """PROPRIETA': la densita' e' normalizzata, l'integrale su R^D vale 1.

    Se manca il fattore 1/sqrt((2pi)^D |Sigma|), o se |Sigma| e' usato al posto
    di sqrt(|Sigma|), questo test lo scopre subito.
    """
    # caso 1D
    a, b, n = -14.0, 14.0, 20001
    bordi = np.linspace(a, b, n + 1)
    centri = 0.5 * (bordi[:-1] + bordi[1:])
    dx = (b - a) / n
    p1 = m.gaussian_pdf(centri.reshape(-1, 1), np.array([0.7]), np.array([[1.3]]))
    massa1 = float(np.sum(p1) * dx)
    assert abs(massa1 - 1.0) < 1e-6, (
        f"la gaussiana 1D non integra a 1 (ottenuto {massa1:.8f}): "
        "controlla la costante di normalizzazione"
    )

    # caso 2D con covarianza correlata
    mu = np.array([0.5, -1.0])
    Sigma = np.array([[1.0, 0.4], [0.4, 0.8]])
    lo, hi, g = -9.0, 9.0, 400
    bordi = np.linspace(lo, hi, g + 1)
    c = 0.5 * (bordi[:-1] + bordi[1:])
    dA = ((hi - lo) / g) ** 2
    G1, G2 = np.meshgrid(c, c, indexing="ij")
    P = np.stack([G1.ravel(), G2.ravel()], axis=1)
    massa2 = float(np.sum(m.gaussian_pdf(P, mu, Sigma)) * dA)
    assert abs(massa2 - 1.0) < 1e-6, (
        f"la gaussiana 2D non integra a 1 (ottenuto {massa2:.8f}): "
        "il determinante di Sigma va sotto radice"
    )


# --------------------------------------------------------------------------- #
# 2. E-step                                                                    #
# --------------------------------------------------------------------------- #
def test_responsabilita_sommano_a_uno():
    """PROPRIETA': gamma[n, :] e' una distribuzione di probabilita' su K.

    Le responsabilita' sono la posterior p(z_n = k | x_n): devono essere non
    negative e sommare esattamente a 1 su ogni RIGA (asse 1), non su ogni
    colonna. Confondere axis=0 con axis=1 e' l'errore piu' comune qui.
    """
    pis = np.array([0.2, 0.5, 0.3])
    mus = np.array([[0.0, 0.0], [6.0, 0.0], [3.0, 5.0]])
    Sigmas = np.array([np.eye(2) * 0.8, np.eye(2) * 2.0, np.eye(2) * 0.3])

    resp, loglik = m.e_step(X_TRE, pis, mus, Sigmas)
    assert resp.shape == (X_TRE.shape[0], 3), (
        f"resp deve avere shape (N, K) = {(X_TRE.shape[0], 3)}, ottenuto {resp.shape}"
    )
    assert np.all(resp >= 0.0), "le responsabilita' sono probabilita': non possono essere negative"
    np.testing.assert_allclose(
        resp.sum(axis=1),
        np.ones(X_TRE.shape[0]),
        rtol=0,
        atol=1e-12,
        err_msg="ogni riga di resp deve sommare a 1 (normalizzazione sulle componenti, axis=1)",
    )
    assert np.isscalar(loglik) or np.ndim(loglik) == 0, (
        "loglik deve essere uno scalare (log-likelihood TOTALE del dataset), non un vettore per campione"
    )


def test_e_step_loglik_contro_somma_diretta():
    """ORACOLO: loglik ricalcolata in spazio lineare, componente per componente.

    Su un problema ben scalato sum_k pi_k N(x|mu_k,Sigma_k) non underflowa,
    quindi la somma diretta e' valida e fa da riferimento indipendente per la
    versione con log-sum-exp. Verifica anche che loglik sia una SOMMA su n e
    non una media.
    """
    pis = np.array([0.3, 0.7])
    mus = np.array([[0.0, 0.0], [1.5, 0.8]])
    Sigmas = np.array([[[1.0, 0.5], [0.5, 1.0]], [[1.2, -0.2], [-0.2, 0.9]]])

    resp, loglik = m.e_step(X_DUE, pis, mus, Sigmas)

    mix = np.zeros(X_DUE.shape[0])
    num = np.zeros((X_DUE.shape[0], 2))
    for k in range(2):
        num[:, k] = pis[k] * m.gaussian_pdf(X_DUE, mus[k], Sigmas[k])
        mix += num[:, k]
    loglik_atteso = float(np.sum(np.log(mix)))
    resp_atteso = num / mix[:, None]

    assert abs(loglik - loglik_atteso) < 1e-7 * max(1.0, abs(loglik_atteso)), (
        f"loglik = {loglik} ma la somma diretta di log(sum_k pi_k N_k) da' {loglik_atteso}: "
        "deve essere la somma su TUTTI i campioni, non la media"
    )
    np.testing.assert_allclose(
        resp,
        resp_atteso,
        rtol=1e-8,
        atol=1e-12,
        err_msg="resp non coincide con pi_k N_k / sum_j pi_j N_j",
    )


# --------------------------------------------------------------------------- #
# 3. M-step                                                                    #
# --------------------------------------------------------------------------- #
def test_m_step_oracolo_con_cicli_espliciti():
    """ORACOLO: medie e covarianze pesate ricalcolate con cicli Python espliciti.

    Punto delicato: nella covarianza va usata la media NUOVA (quella appena
    aggiornata dal M-step), non quella dell'iterazione precedente.
    """
    rng = np.random.default_rng(5)
    X = X_DUE
    N, D = X.shape
    K = 3
    W = rng.random((N, K)) + 0.05
    resp = W / W.sum(axis=1, keepdims=True)
    reg = 1e-4

    pis, mus, Sigmas = m.m_step(X, resp, reg=reg)

    for k in range(K):
        Nk = float(sum(resp[n, k] for n in range(N)))
        assert abs(pis[k] - Nk / N) < 1e-10, (
            f"pi_{k} deve valere N_k/N = {Nk / N}, ottenuto {pis[k]}"
        )
        mu_k = np.zeros(D)
        for n in range(N):
            mu_k += resp[n, k] * X[n]
        mu_k /= Nk
        np.testing.assert_allclose(
            mus[k], mu_k, rtol=1e-8, atol=1e-12,
            err_msg=f"mu_{k} non e' la media pesata dalle responsabilita'",
        )
        S_k = np.zeros((D, D))
        for n in range(N):
            d = (X[n] - mu_k).reshape(D, 1)
            S_k += resp[n, k] * (d @ d.T)
        S_k = S_k / Nk + reg * np.eye(D)
        np.testing.assert_allclose(
            Sigmas[k], S_k, rtol=1e-8, atol=1e-12,
            err_msg=f"Sigma_{k} sbagliata: usa la media NUOVA e aggiungi reg sulla diagonale",
        )

    assert abs(float(pis.sum()) - 1.0) < 1e-12, "i pesi di mixing devono sommare a 1"


# --------------------------------------------------------------------------- #
# 4. La proprieta' centrale: monotonia di EM                                   #
# --------------------------------------------------------------------------- #
def test_monotonia_loglikelihood():
    """PROPRIETA' CENTRALE: la log-likelihood non decresce MAI fra iterazioni EM.

    E' il teorema che giustifica l'algoritmo: ogni coppia (E, M) massimizza un
    lower bound stretto sulla log-likelihood dei dati osservati, quindi
    log p(X | theta^{t+1}) >= log p(X | theta^t). Se la history scende, il bug
    e' quasi sempre uno di questi: covarianze aggiornate con le medie vecchie,
    responsabilita' normalizzate sull'asse sbagliato, oppure la log-likelihood
    calcolata sul modello a variabili complete invece che marginalizzando su z.

    Il controllo gira su 30 combinazioni (dataset, K, seed) diverse: la
    monotonia non e' una proprieta' fortunata di un run, e' una garanzia.
    """
    configurazioni = (
        [("X_TRE", X_TRE, K, s) for K in (1, 2, 3, 4) for s in (0, 1, 2)]
        + [("X_DUE", X_DUE, K, s) for K in (1, 2, 3) for s in (0, 1, 2)]
        + [("X_3D", X_3D, K, s) for K in (1, 2, 3) for s in (0, 1, 2)]
    )
    for nome, X, K, seed in configurazioni:
        modello = m.fit_gmm(X, K, seed=seed)
        assert isinstance(modello["loglik_history"], list), (
            "loglik_history deve essere una lista Python"
        )
        storia = np.asarray(modello["loglik_history"], dtype=float)
        assert storia.size >= 2, (
            "la history deve contenere almeno il valore iniziale e uno aggiornato"
        )
        assert np.all(np.isfinite(storia)), (
            f"[{nome} K={K} seed={seed}] log-likelihood non finita nella history: {storia[:5]}"
        )

        diffs = np.diff(storia)
        # tolleranza numerica minima: solo il round-off in doppia precisione
        atol = 1e-10 * max(1.0, float(np.abs(storia).max()))
        peggiore = float(diffs.min())
        assert peggiore >= -atol, (
            f"[{nome} K={K} seed={seed}] la log-likelihood DECRESCE di {peggiore} "
            f"all'iterazione {int(np.argmin(diffs))}: EM garantisce che non possa mai succedere"
        )
        assert storia[-1] >= storia[0] - atol, (
            f"[{nome} K={K} seed={seed}] la log-likelihood finale ({storia[-1]}) "
            f"e' peggiore di quella iniziale ({storia[0]})"
        )
        assert modello["n_iter"] == len(storia) - 1, (
            f"[{nome} K={K} seed={seed}] n_iter ({modello['n_iter']}) deve contare gli "
            f"aggiornamenti EM effettivi, cioe' len(loglik_history) - 1 = {len(storia) - 1}"
        )


# --------------------------------------------------------------------------- #
# 5. Oracolo in forma chiusa: K = 1                                            #
# --------------------------------------------------------------------------- #
def test_k1_coincide_con_mle_in_forma_chiusa():
    """ORACOLO: con K=1 la GMM degenera in una singola gaussiana.

    Non c'e' piu' nessuna variabile latente da marginalizzare: le
    responsabilita' valgono identicamente 1 e il M-step riproduce esattamente
    lo stimatore di massima verosimiglianza in forma chiusa,

        mu    = (1/N) sum_n x_n
        Sigma = (1/N) sum_n (x_n - mu)(x_n - mu)^T     <- denominatore N, non N-1

    Il fit viene fatto con reg=0 perche' il ridge sposterebbe la covarianza.
    """
    X = X_DUE
    modello = m.fit_gmm(X, 1, reg=0.0, seed=0)

    np.testing.assert_allclose(
        modello["pis"], np.array([1.0]), rtol=0, atol=1e-12,
        err_msg="con K=1 l'unico peso di mixing deve valere 1",
    )
    np.testing.assert_allclose(
        modello["mus"][0], X.mean(axis=0), rtol=1e-6, atol=1e-9,
        err_msg="con K=1 la media stimata deve essere la media empirica del dataset",
    )
    Sigma_mle = np.cov(X, rowvar=False, bias=True)  # bias=True -> divisione per N (MLE)
    np.testing.assert_allclose(
        modello["Sigmas"][0], Sigma_mle, rtol=1e-6, atol=1e-9,
        err_msg="con K=1 la covarianza stimata deve essere quella empirica con denominatore N (MLE), non N-1",
    )
    ll_atteso = float(np.sum(m.log_gaussian_pdf(X, X.mean(axis=0), Sigma_mle)))
    assert abs(modello["loglik_history"][-1] - ll_atteso) < 1e-8 * max(1.0, abs(ll_atteso)), (
        "con K=1 la log-likelihood finale deve essere la somma delle log-densita' gaussiane"
    )
    np.testing.assert_allclose(
        modello["resp"], np.ones((X.shape[0], 1)), rtol=0, atol=1e-12,
        err_msg="con K=1 ogni punto appartiene con probabilita' 1 all'unica componente",
    )


# --------------------------------------------------------------------------- #
# 6. Model selection                                                           #
# --------------------------------------------------------------------------- #
def test_n_params_gmm_conteggio_manuale():
    """Conteggio dei parametri liberi, verificato a mano e per enumerazione.

    K=2, D=2: 1 peso libero (il secondo e' 1 meno il primo) + 2 medie da 2
    numeri + 2 covarianze simmetriche 2x2 da 3 numeri liberi = 1 + 4 + 6 = 11.
    """
    assert m.n_params_gmm(2, 2) == 11, (
        f"n_params_gmm(2, 2) deve valere 11 (1 peso + 4 medie + 6 covarianze), ottenuto {m.n_params_gmm(2, 2)}"
    )
    assert m.n_params_gmm(3, 2) == 17, (
        f"n_params_gmm(3, 2) deve valere 17 (2 + 6 + 9), ottenuto {m.n_params_gmm(3, 2)}"
    )
    assert m.n_params_gmm(1, 1) == 2, (
        f"n_params_gmm(1, 1) deve valere 2 (0 pesi liberi + 1 media + 1 varianza), ottenuto {m.n_params_gmm(1, 1)}"
    )

    # ORACOLO: enumerazione esplicita delle entrate indipendenti
    for K in (1, 2, 4, 7):
        for D in (1, 2, 3, 5):
            triu = sum(1 for i in range(D) for j in range(D) if i <= j)
            atteso = (K - 1) + K * D + K * triu
            assert m.n_params_gmm(K, D) == atteso, (
                f"n_params_gmm({K}, {D}) = {m.n_params_gmm(K, D)}, atteso {atteso}: "
                "le covarianze sono simmetriche, si contano solo le entrate del triangolo superiore"
            )


def test_bic_convenzione_e_confronto_con_aic():
    """La convenzione di segno del BIC: -2*loglik + p*log(N), PIU' BASSO E' MEGLIO."""
    ll, p, N = -100.0, 5, 50
    assert abs(m.bic(ll, p, N) - (-2.0 * ll + p * math.log(N))) < 1e-9, (
        "bic deve valere -2*loglik + n_params*log(N)"
    )
    assert abs(m.aic(ll, p) - (-2.0 * ll + 2.0 * p)) < 1e-9, (
        "aic deve valere -2*loglik + 2*n_params"
    )

    # a parita' di fit, piu' parametri -> BIC piu' alto (peggiore)
    assert m.bic(ll, 5, N) < m.bic(ll, 9, N), (
        "con la stessa log-likelihood il modello con piu' parametri deve avere BIC MAGGIORE: "
        "il BIC si minimizza, non si massimizza"
    )
    # a parita' di complessita', fit migliore -> BIC piu' basso
    assert m.bic(-90.0, p, N) < m.bic(-100.0, p, N), (
        "una log-likelihood piu' alta deve dare un BIC piu' BASSO"
    )
    # per N > e^2 il BIC penalizza piu' dell'AIC
    assert m.bic(ll, p, 1000) > m.aic(ll, p), (
        "per N grande la penalita' del BIC (p*log N) supera quella dell'AIC (2p)"
    )
    assert m.bic(ll, p, 5) < m.aic(ll, p), (
        "per N < e^2 ~ 7.4 la penalita' del BIC e' piu' leggera di quella dell'AIC"
    )


def test_select_k_su_tre_gaussiane_separate():
    """Su dati generati da 3 gaussiane ben separate, il BIC deve scegliere K=3."""
    X, _ = m.make_blobs_like(
        300, [[0.0, 0.0], [10.0, 0.0], [5.0, 9.0]], np.eye(2) * 0.5, seed=1
    )
    k_values = [1, 2, 3, 4, 5]
    res = m.select_k(X, k_values, seed=0)

    assert set(res.keys()) >= {"best_k", "bic_per_k", "models"}, (
        f"select_k deve restituire le chiavi best_k, bic_per_k, models; ottenute {sorted(res.keys())}"
    )
    assert set(res["bic_per_k"].keys()) == set(k_values), (
        "bic_per_k deve contenere un valore per ogni k richiesto"
    )
    assert res["best_k"] == 3, (
        f"i dati vengono da 3 gaussiane ben separate ma select_k ha scelto k={res['best_k']}; "
        f"BIC per k: { {k: round(v, 1) for k, v in res['bic_per_k'].items()} }. "
        "Se ha scelto il k massimo stai probabilmente massimizzando il BIC invece di minimizzarlo"
    )
    assert res["bic_per_k"][3] == min(res["bic_per_k"].values()), (
        "best_k deve essere l'argmin di bic_per_k"
    )
    # coerenza interna: il BIC riportato deve essere ricalcolabile dal modello
    for k in k_values:
        mod = res["models"][k]
        atteso = m.bic(mod["loglik_history"][-1], m.n_params_gmm(k, X.shape[1]), X.shape[0])
        assert abs(res["bic_per_k"][k] - atteso) < 1e-6 * max(1.0, abs(atteso)), (
            f"il BIC riportato per k={k} non corrisponde a quello ricalcolato dal modello salvato"
        )


# --------------------------------------------------------------------------- #
# 7. Stabilita' numerica e casi limite                                         #
# --------------------------------------------------------------------------- #
def test_stabilita_numerica_punti_lontanissimi():
    """CASO LIMITE: punti a distanza enorme dalle componenti non devono dare NaN.

    Sotto la soglia di underflow tutte le densita' valgono 0 in spazio lineare:
    un E-step che calcola pi_k * N_k e poi divide per la somma produce 0/0 = NaN.
    In spazio log, invece, log-sum-exp normalizza sottraendo il massimo e le
    responsabilita' restano ben definite.
    """
    mus = np.array([[0.0, 0.0], [1.0, 1.0]])
    Sigmas = np.array([np.eye(2) * 1e-4, np.eye(2)])
    pis = np.array([0.5, 0.5])
    X = np.array([[1.0e5, 1.0e5], [-3.0e4, 2.0e4], [0.0, 0.0], [1.0, 1.0]])

    lp = m.log_gaussian_pdf(X, mus[0], Sigmas[0])
    assert np.all(np.isfinite(lp)), (
        f"log_gaussian_pdf produce valori non finiti su punti lontani: {lp}"
    )

    resp, loglik = m.e_step(X, pis, mus, Sigmas)
    assert not np.any(np.isnan(resp)), (
        f"e_step produce NaN nelle responsabilita' su punti lontani:\n{resp}\n"
        "va normalizzato in spazio log (log-sum-exp), non moltiplicando le densita'"
    )
    np.testing.assert_allclose(
        resp.sum(axis=1), np.ones(X.shape[0]), rtol=0, atol=1e-10,
        err_msg="anche su punti estremi ogni riga di resp deve sommare a 1",
    )
    assert np.isfinite(loglik), f"loglik non finita su punti lontani: {loglik}"

    # fit completo su dataset con outlier estremi
    X_out = np.vstack([X_TRE, np.array([[1.0e4, -1.0e4], [-5.0e3, 8.0e3]])])
    mod = m.fit_gmm(X_out, 3, seed=0, n_iter=60)
    for chiave in ("pis", "mus", "Sigmas", "resp"):
        assert np.all(np.isfinite(np.asarray(mod[chiave], dtype=float))), (
            f"fit_gmm produce valori non finiti in '{chiave}' in presenza di outlier estremi"
        )
    assert np.all(np.isfinite(np.asarray(mod["loglik_history"], dtype=float))), (
        "la loglik_history contiene NaN o inf in presenza di outlier estremi"
    )


def test_caso_limite_k_uguale_n():
    """CASO LIMITE: K = N, una componente per campione.

    E' la situazione degenere in cui la likelihood delle misture diverge: ogni
    gaussiana puo' collassare su un punto e la sua covarianza andare a zero. Il
    ridge `reg` sulla diagonale e' esattamente cio' che impedisce alla
    log-likelihood di esplodere a +infinito.
    """
    X, _ = m.make_blobs_like(4, [[0.0, 0.0], [3.0, 3.0]], np.eye(2), seed=7)
    N, D = X.shape
    assert N == 8

    mod = m.fit_gmm(X, N, seed=0, reg=1e-3, n_iter=50)
    assert mod["pis"].shape == (N,), f"pis deve avere shape (K,) = ({N},), ottenuto {mod['pis'].shape}"
    assert mod["mus"].shape == (N, D), f"mus deve avere shape (K, D) = {(N, D)}, ottenuto {mod['mus'].shape}"
    assert mod["Sigmas"].shape == (N, D, D), (
        f"Sigmas deve avere shape (K, D, D) = {(N, D, D)}, ottenuto {mod['Sigmas'].shape}"
    )
    assert np.all(np.isfinite(mod["mus"])) and np.all(np.isfinite(mod["Sigmas"])), (
        "con K = N i parametri devono restare finiti: e' il ridge reg a impedire il collasso"
    )
    assert abs(float(mod["pis"].sum()) - 1.0) < 1e-10, "i pesi di mixing devono sommare a 1 anche con K = N"
    np.testing.assert_allclose(
        mod["resp"].sum(axis=1), np.ones(N), rtol=0, atol=1e-10,
        err_msg="le responsabilita' devono restare normalizzate anche con K = N",
    )
    assert np.all(np.isfinite(np.asarray(mod["loglik_history"], dtype=float))), (
        "con K = N la log-likelihood deve restare finita (senza reg divergerebbe a +inf)"
    )
    for k in range(N):
        S = mod["Sigmas"][k]
        np.testing.assert_allclose(
            S, S.T, rtol=1e-10, atol=1e-12,
            err_msg=f"Sigma_{k} non e' simmetrica",
        )
        np.linalg.cholesky(S)  # solleva LinAlgError se non e' definita positiva


def test_predict_hard_assignment():
    """predict e' l'argmax delle responsabilita', e su blob separati ritrova i cluster."""
    X, Y = m.make_blobs_like(
        100, [[0.0, 0.0], [12.0, 0.0], [6.0, 10.0]], np.eye(2) * 0.4, seed=3
    )
    mod = m.fit_gmm(X, 3, seed=0)
    etichette = m.predict(X, mod)

    assert etichette.shape == (X.shape[0],), (
        f"predict deve restituire shape (N,), ottenuto {etichette.shape}"
    )
    assert np.issubdtype(etichette.dtype, np.integer), (
        f"predict deve restituire indici interi, ottenuto dtype {etichette.dtype}"
    )
    assert etichette.min() >= 0 and etichette.max() < 3, "gli indici devono stare in [0, K)"

    resp, _ = m.e_step(X, mod["pis"], mod["mus"], mod["Sigmas"])
    np.testing.assert_array_equal(
        etichette,
        np.argmax(resp, axis=1),
        err_msg="predict deve essere l'argmax sulle componenti (axis=1) delle responsabilita'",
    )

    # su blob ben separati il partizionamento coincide con la ground truth,
    # a meno di una permutazione delle etichette
    mappa = {}
    for c in range(3):
        trovate = np.unique(etichette[Y == c])
        assert trovate.size == 1, (
            f"il cluster vero {c} viene spezzato su piu' componenti {trovate}: "
            "su tre blob ben separati EM deve ricostruire la partizione"
        )
        mappa[c] = int(trovate[0])
    assert len(set(mappa.values())) == 3, (
        f"due cluster veri diversi finiscono nella stessa componente stimata: {mappa}"
    )

    # predict deve funzionare anche su dati NUOVI, non solo su quelli del fit
    X_nuovi = np.array([[0.0, 0.0], [12.0, 0.0], [6.0, 10.0]])
    nuove = m.predict(X_nuovi, mod)
    assert nuove.shape == (3,), "predict deve accettare un X qualsiasi, non solo quello usato nel fit"
    assert len(set(nuove.tolist())) == 3, (
        "i tre centri veri devono finire in tre componenti diverse: "
        "predict deve ricalcolare le responsabilita' su X, non riusare model['resp']"
    )
