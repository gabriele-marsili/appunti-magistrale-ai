"""Soluzione di riferimento: EM per Gaussian Mixture Models + model selection (BIC/AIC).

Riferimento teorico: `Lessons/GDL8 learning hidden.pdf` (Expectation-Maximization,
exact maximum likelihood learning in mixture models) e `Lessons/GDL2 prob refresh.pdf`
(gaussiana multivariata). Ricalca il Midterm 1 del corso.

Convenzioni globali usate ovunque nel modulo:
    N = numero di campioni, D = dimensionalita', K = numero di componenti.
    X       -> (N, D)
    pis     -> (K,)      pesi di mixing, sommano a 1
    mus     -> (K, D)    medie
    Sigmas  -> (K, D, D) covarianze piene, simmetriche definite positive
    resp    -> (N, K)    responsabilita' gamma[n, k] = p(z_n = k | x_n, theta)
"""

from __future__ import annotations

import math

import numpy as np

__all__ = [
    "make_blobs_like",
    "logsumexp",
    "log_gaussian_pdf",
    "gaussian_pdf",
    "init_params",
    "e_step",
    "m_step",
    "fit_gmm",
    "n_params_gmm",
    "bic",
    "aic",
    "select_k",
    "predict",
]


# --------------------------------------------------------------------------- #
# Codice fornito (non didattico): generatore di dati sintetici                 #
# --------------------------------------------------------------------------- #
def make_blobs_like(n_per_cluster, means, covs, seed=0):
    """Genera un dataset sintetico da una mistura di gaussiane.

    Parametri
    ---------
    n_per_cluster : int oppure sequenza di int di lunghezza K
        Numero di punti per componente.
    means : array-like (K, D)
        Medie delle componenti.
    covs : array-like (K, D, D) oppure (D, D)
        Covarianze. Se e' (D, D) la stessa matrice viene usata per tutte le componenti.
    seed : int
        Seed per `np.random.default_rng`.

    Ritorna
    -------
    X : ndarray (N, D) con N = sum(n_per_cluster), righe mescolate.
    y : ndarray (N,) di int, etichetta della componente generatrice (ground truth).

    Nota: il campionamento usa la fattorizzazione di Cholesky
    (x = mu + L z, con z ~ N(0, I) e Sigma = L L^T) per essere riproducibile
    indipendentemente dalla versione di numpy.
    """
    means = np.asarray(means, dtype=float)
    covs = np.asarray(covs, dtype=float)
    if means.ndim != 2:
        raise ValueError("means deve avere shape (K, D)")
    K, D = means.shape
    if covs.ndim == 2:
        covs = np.repeat(covs[None, :, :], K, axis=0)
    if covs.shape != (K, D, D):
        raise ValueError("covs deve avere shape (K, D, D) oppure (D, D)")

    if np.ndim(n_per_cluster) == 0:
        counts = [int(n_per_cluster)] * K
    else:
        counts = [int(c) for c in n_per_cluster]
        if len(counts) != K:
            raise ValueError("n_per_cluster deve avere lunghezza K")

    rng = np.random.default_rng(seed)
    Xs, ys = [], []
    for k in range(K):
        L = np.linalg.cholesky(covs[k])
        Z = rng.standard_normal((counts[k], D))
        Xs.append(means[k] + Z @ L.T)
        ys.append(np.full(counts[k], k, dtype=int))
    X = np.concatenate(Xs, axis=0)
    y = np.concatenate(ys, axis=0)
    perm = rng.permutation(X.shape[0])
    return X[perm], y[perm]


# --------------------------------------------------------------------------- #
# Utility numerica                                                             #
# --------------------------------------------------------------------------- #
def logsumexp(A, axis=-1):
    """log(sum(exp(A))) lungo `axis`, calcolato in modo stabile.

    Il trucco: si sottrae il massimo prima di esponenziare, cosi' l'argomento
    massimo di exp e' 0 e non si va mai in overflow; l'underflow degli altri
    termini e' innocuo (contribuiscono ~0 alla somma).

        logsumexp(a) = m + log(sum(exp(a - m)))     con m = max(a)

    Se tutti gli elementi lungo l'asse sono -inf il massimo e' -inf: in quel caso
    si usa m = 0 nello shift (evita -inf + inf = NaN) e il risultato e' -inf,
    che e' il valore corretto.

    Parametri
    ---------
    A : ndarray
    axis : int

    Ritorna
    -------
    ndarray con `axis` ridotto (non tenuto).
    """
    A = np.asarray(A, dtype=float)
    m = np.max(A, axis=axis, keepdims=True)
    # se m non e' finito (tutti -inf, oppure +inf) non lo si puo' sottrarre
    m_safe = np.where(np.isfinite(m), m, 0.0)
    out = m_safe + np.log(np.sum(np.exp(A - m_safe), axis=axis, keepdims=True))
    return np.squeeze(out, axis=axis)


def _cholesky_with_jitter(Sigma):
    """Cholesky robusta: simmetrizza e, se serve, aggiunge un jitter crescente.

    Non e' parte della didattica dell'esercizio, e' solo una rete di sicurezza
    contro covarianze che il round-off rende non-definite-positive per un pelo.
    """
    S = np.asarray(Sigma, dtype=float)
    S = 0.5 * (S + S.T)
    D = S.shape[0]
    scale = float(np.trace(S)) / D
    base = 1e-12 * max(1.0, abs(scale))
    jitter = 0.0
    for _ in range(8):
        try:
            return np.linalg.cholesky(S + jitter * np.eye(D))
        except np.linalg.LinAlgError:
            jitter = base if jitter == 0.0 else jitter * 100.0
    raise np.linalg.LinAlgError("covarianza non definita positiva nemmeno con jitter")


# --------------------------------------------------------------------------- #
# 1. Densita' gaussiana multivariata                                           #
# --------------------------------------------------------------------------- #
def log_gaussian_pdf(X, mu, Sigma):
    """Log-densita' gaussiana multivariata, valutata su tutte le righe di X.

        log N(x | mu, Sigma) = -0.5 * ( D*log(2*pi) + log|Sigma| + (x-mu)^T Sigma^-1 (x-mu) )

    Implementazione: si fattorizza Sigma = L L^T (Cholesky, L triangolare bassa).
    Allora
        log|Sigma| = 2 * sum(log(diag(L)))
        (x-mu)^T Sigma^-1 (x-mu) = ||z||^2   con   L z = (x - mu)
    Cosi' non si inverte mai Sigma e non si calcola mai il determinante come
    prodotto di autovalori: entrambe le operazioni sono molto piu' instabili.

    Parametri
    ---------
    X : ndarray (N, D)
    mu : ndarray (D,)
    Sigma : ndarray (D, D) simmetrica definita positiva

    Ritorna
    -------
    ndarray (N,) di log-densita'.
    """
    X = np.atleast_2d(np.asarray(X, dtype=float))
    mu = np.asarray(mu, dtype=float).reshape(-1)
    Sigma = np.asarray(Sigma, dtype=float)
    D = X.shape[1]
    if mu.shape[0] != D or Sigma.shape != (D, D):
        raise ValueError("shape incoerenti fra X, mu e Sigma")

    L = _cholesky_with_jitter(Sigma)
    diff = X - mu                                  # (N, D)
    # risolve L z = diff^T colonna per colonna -> z ha shape (D, N)
    z = np.linalg.solve(L, diff.T)
    maha = np.sum(z * z, axis=0)                   # (N,)
    log_det = 2.0 * np.sum(np.log(np.diag(L)))
    return -0.5 * (D * math.log(2.0 * math.pi) + log_det + maha)


def gaussian_pdf(X, mu, Sigma):
    """Densita' gaussiana multivariata su tutte le righe di X.

    Calcolata come exp(log_gaussian_pdf(...)): la forma logaritmica e' l'unica
    numericamente sensata in dimensione anche solo moderata, perche' il termine
    di Mahalanobis puo' valere migliaia e exp(-migliaia) va in underflow *dopo*
    che il prodotto 1/sqrt(|Sigma|) e' gia' andato in overflow.

    Parametri
    ---------
    X : ndarray (N, D)
    mu : ndarray (D,)
    Sigma : ndarray (D, D)

    Ritorna
    -------
    ndarray (N,) di densita' >= 0.
    """
    return np.exp(log_gaussian_pdf(X, mu, Sigma))


# --------------------------------------------------------------------------- #
# 2. Inizializzazione (k-means++)                                              #
# --------------------------------------------------------------------------- #
def init_params(X, K, rng):
    """Inizializza (pis, mus, Sigmas) con k-means++ sulle medie.

    k-means++ (implementato a mano):
      1. il primo centro e' un punto scelto uniformemente fra le righe di X;
      2. ogni centro successivo e' un punto estratto con probabilita'
         proporzionale a D(x)^2, dove D(x) e' la distanza euclidea di x dal
         centro gia' scelto piu' vicino.
    Cosi' i centri iniziali tendono a essere lontani fra loro: EM parte da un
    punto di partenza ragionevole invece che da K punti a caso che possono
    cadere tutti nello stesso blob.

    - pis: uniformi, 1/K ciascuno.
    - Sigmas: covarianza empirica dell'intero dataset, uguale per tutte le
      componenti, piu' un ridge minimo (1e-6) sulla diagonale che garantisce
      la definita positivita' anche quando N e' piccolo rispetto a D.

    Parametri
    ---------
    X : ndarray (N, D)
    K : int
    rng : np.random.Generator

    Ritorna
    -------
    (pis (K,), mus (K, D), Sigmas (K, D, D))
    """
    X = np.asarray(X, dtype=float)
    N, D = X.shape
    if not (1 <= K <= N):
        raise ValueError("serve 1 <= K <= N")

    # --- k-means++ ---------------------------------------------------------
    first = int(rng.integers(N))
    centers = [X[first]]
    d2 = np.sum((X - X[first]) ** 2, axis=1)       # (N,) distanza^2 dal centro piu' vicino
    for _ in range(1, K):
        total = float(d2.sum())
        if not np.isfinite(total) or total <= 0.0:
            # tutti i punti coincidono con un centro gia' scelto: fallback uniforme
            j = int(rng.integers(N))
        else:
            j = int(rng.choice(N, p=d2 / total))
        centers.append(X[j])
        d2 = np.minimum(d2, np.sum((X - X[j]) ** 2, axis=1))
    mus = np.asarray(centers, dtype=float)

    # --- pesi e covarianze -------------------------------------------------
    pis = np.full(K, 1.0 / K, dtype=float)
    Sigma0 = np.atleast_2d(np.cov(X, rowvar=False, bias=True))
    Sigma0 = Sigma0 + 1e-6 * np.eye(D)
    Sigmas = np.repeat(Sigma0[None, :, :], K, axis=0)
    return pis, mus, Sigmas


# --------------------------------------------------------------------------- #
# 3. E-step                                                                    #
# --------------------------------------------------------------------------- #
def e_step(X, pis, mus, Sigmas):
    """E-step: responsabilita' e log-likelihood del dataset.

        gamma[n, k] = pi_k N(x_n | mu_k, Sigma_k) / sum_j pi_j N(x_n | mu_j, Sigma_j)
        loglik      = sum_n log( sum_k pi_k N(x_n | mu_k, Sigma_k) )

    Tutto in spazio log: si costruisce la matrice dei log-numeratori
    log(pi_k) + log N(x_n | mu_k, Sigma_k), si riduce con logsumexp sulle
    componenti per ottenere log p(x_n), e le responsabilita' sono la
    esponenziale della differenza (che e' sempre <= 0, quindi mai overflow).

    Parametri
    ---------
    X : ndarray (N, D)
    pis : ndarray (K,)
    mus : ndarray (K, D)
    Sigmas : ndarray (K, D, D)

    Ritorna
    -------
    resp : ndarray (N, K), ogni riga somma a 1.
    loglik : float, log-likelihood TOTALE del dataset (somma su n, non media).
    """
    X = np.asarray(X, dtype=float)
    pis = np.asarray(pis, dtype=float).reshape(-1)
    mus = np.asarray(mus, dtype=float)
    Sigmas = np.asarray(Sigmas, dtype=float)
    N = X.shape[0]
    K = pis.shape[0]

    log_num = np.empty((N, K), dtype=float)
    with np.errstate(divide="ignore"):             # log(0) -> -inf, voluto
        log_pis = np.log(pis)
    for k in range(K):
        log_num[:, k] = log_pis[k] + log_gaussian_pdf(X, mus[k], Sigmas[k])

    log_px = logsumexp(log_num, axis=1)            # (N,) = log p(x_n)
    resp = np.exp(log_num - log_px[:, None])
    loglik = float(np.sum(log_px))
    return resp, loglik


# --------------------------------------------------------------------------- #
# 4. M-step                                                                    #
# --------------------------------------------------------------------------- #
def m_step(X, resp, reg=1e-6):
    """M-step: massimizza in forma chiusa la Q function rispetto ai parametri.

        N_k    = sum_n gamma[n, k]
        pi_k   = N_k / N
        mu_k   = (1 / N_k) sum_n gamma[n, k] x_n
        Sigma_k= (1 / N_k) sum_n gamma[n, k] (x_n - mu_k)(x_n - mu_k)^T + reg * I

    Le medie vanno aggiornate PRIMA delle covarianze: nella formula di Sigma_k
    compare la mu_k nuova, non quella vecchia.

    `reg` e' aggiunto alla diagonale delle covarianze. Serve contro la
    degenerazione della likelihood delle misture: se una componente collassa su
    un singolo punto la sua covarianza tende a zero e la likelihood diverge a
    +infinito. Il ridge mette un pavimento agli autovalori.

    Parametri
    ---------
    X : ndarray (N, D)
    resp : ndarray (N, K), assunta normalizzata per riga
    reg : float, aggiunto alla diagonale di ogni Sigma_k

    Ritorna
    -------
    (pis (K,), mus (K, D), Sigmas (K, D, D))
    """
    X = np.asarray(X, dtype=float)
    resp = np.asarray(resp, dtype=float)
    N, D = X.shape
    K = resp.shape[1]

    Nk = resp.sum(axis=0)                                  # (K,)
    Nk_safe = np.maximum(Nk, 10.0 * np.finfo(float).eps)   # evita 0/0 su componenti morte

    pis = Nk / N
    mus = (resp.T @ X) / Nk_safe[:, None]                  # (K, D)

    Sigmas = np.empty((K, D, D), dtype=float)
    eye = np.eye(D)
    for k in range(K):
        diff = X - mus[k]                                  # (N, D)
        weighted = resp[:, k][:, None] * diff              # (N, D)
        Sigmas[k] = (weighted.T @ diff) / Nk_safe[k] + reg * eye
        Sigmas[k] = 0.5 * (Sigmas[k] + Sigmas[k].T)        # simmetrizza il round-off
    return pis, mus, Sigmas


# --------------------------------------------------------------------------- #
# 5. Ciclo EM completo                                                         #
# --------------------------------------------------------------------------- #
def fit_gmm(X, K, n_iter=200, tol=1e-6, seed=0, reg=1e-6):
    """Stima una GMM a K componenti con EM.

    Schema (l'ordine conta per la coerenza del risultato):
        init  -> E                     : loglik_history[0] = loglik ai parametri iniziali
        ripeti: M -> E, registra loglik
        stop quando l'incremento di log-likelihood scende sotto `tol`
              oppure dopo `n_iter` aggiornamenti.

    Con questo schema i valori restituiti in "pis"/"mus"/"Sigmas", "resp" e
    l'ultimo elemento di "loglik_history" si riferiscono SEMPRE agli stessi
    parametri: la E finale e' calcolata dopo l'ultima M.

    `loglik_history` e' per costruzione non decrescente: e' la garanzia
    dell'algoritmo EM (ogni iterazione non puo' peggiorare la log-likelihood
    dei dati osservati). Se scende, c'e' un bug.

    Parametri
    ---------
    X : ndarray (N, D)
    K : int, numero di componenti
    n_iter : int, massimo numero di aggiornamenti EM
    tol : float, soglia sull'incremento assoluto di log-likelihood
    seed : int, per `np.random.default_rng` usato dall'inizializzazione
    reg : float, ridge sulla diagonale delle covarianze

    Ritorna
    -------
    dict con chiavi:
        "pis"            ndarray (K,)
        "mus"            ndarray (K, D)
        "Sigmas"         ndarray (K, D, D)
        "loglik_history" list[float], lunghezza n_iter_effettive + 1
        "n_iter"         int, numero di aggiornamenti EM effettivamente eseguiti
        "resp"           ndarray (N, K), responsabilita' ai parametri finali
    """
    X = np.asarray(X, dtype=float)
    rng = np.random.default_rng(seed)

    pis, mus, Sigmas = init_params(X, K, rng)
    resp, ll = e_step(X, pis, mus, Sigmas)
    history = [float(ll)]

    performed = 0
    for _ in range(int(n_iter)):
        pis, mus, Sigmas = m_step(X, resp, reg=reg)
        resp, ll = e_step(X, pis, mus, Sigmas)
        history.append(float(ll))
        performed += 1
        if history[-1] - history[-2] < tol:
            break

    return {
        "pis": pis,
        "mus": mus,
        "Sigmas": Sigmas,
        "loglik_history": history,
        "n_iter": performed,
        "resp": resp,
    }


# --------------------------------------------------------------------------- #
# 6. Model selection                                                           #
# --------------------------------------------------------------------------- #
def n_params_gmm(K, D):
    """Numero di parametri liberi di una GMM a covarianze piene.

        (K - 1)          pesi di mixing  (uno e' vincolato dalla somma a 1)
      + K * D            medie
      + K * D(D+1)/2     covarianze (simmetriche: solo il triangolo superiore)

    Parametri
    ---------
    K : int
    D : int

    Ritorna
    -------
    int
    """
    K = int(K)
    D = int(D)
    return (K - 1) + K * D + K * D * (D + 1) // 2


def bic(loglik, n_params, N):
    """Bayesian Information Criterion.

    CONVENZIONE USATA QUI (e' la fonte classica di confusione):

        BIC = -2 * loglik + n_params * log(N)

    quindi **piu' basso e' meglio**: il primo termine premia il fit, il secondo
    penalizza la complessita'. Esiste in giro anche la convenzione con il segno
    opposto (BIC = loglik - 0.5 * n_params * log(N), da massimizzare), che e'
    la stessa quantita' cambiata di segno e riscalata: se all'orale si dice
    "BIC piu' alto" senza specificare la convenzione, e' sbagliato meta' delle
    volte. Qui: si sceglie il modello con BIC MINIMO.

    `loglik` deve essere la log-likelihood TOTALE del dataset (somma su tutti
    gli N campioni), non la media per campione.

    Parametri
    ---------
    loglik : float
    n_params : int, numero di parametri liberi del modello
    N : int, numero di campioni

    Ritorna
    -------
    float
    """
    return float(-2.0 * float(loglik) + float(n_params) * math.log(float(N)))


def aic(loglik, n_params):
    """Akaike Information Criterion, stessa convenzione di segno del BIC.

        AIC = -2 * loglik + 2 * n_params

    Piu' basso e' meglio. Rispetto al BIC la penalita' non dipende da N: per
    N > e^2 ~ 7.4 il BIC penalizza piu' dell'AIC, quindi tende a scegliere
    modelli piu' semplici (il BIC e' consistente, l'AIC no).

    Parametri
    ---------
    loglik : float
    n_params : int

    Ritorna
    -------
    float
    """
    return float(-2.0 * float(loglik) + 2.0 * float(n_params))


def select_k(X, k_values, seed=0, **kw):
    """Sceglie il numero di componenti con il BIC.

    Per ogni k in `k_values` stima una GMM con `fit_gmm(X, k, seed=seed, **kw)`,
    calcola il BIC usando l'ULTIMA log-likelihood della history (quella dei
    parametri finali) e sceglie il k con BIC minimo. In caso di pareggio esatto
    vince il k che compare prima in `k_values`.

    Parametri
    ---------
    X : ndarray (N, D)
    k_values : iterable di int
    seed : int, passato a fit_gmm (stesso seed per tutti i k: il confronto fra
           modelli deve dipendere da k, non dalla fortuna dell'inizializzazione)
    **kw : altri argomenti inoltrati a fit_gmm (n_iter, tol, reg)

    Ritorna
    -------
    dict con chiavi:
        "best_k"    int
        "bic_per_k" dict {k: bic}
        "models"    dict {k: dict restituito da fit_gmm}
    """
    X = np.asarray(X, dtype=float)
    N, D = X.shape

    models = {}
    bic_per_k = {}
    for k in k_values:
        k = int(k)
        model = fit_gmm(X, k, seed=seed, **kw)
        ll = model["loglik_history"][-1]
        bic_per_k[k] = bic(ll, n_params_gmm(k, D), N)
        models[k] = model

    best_k = min(bic_per_k, key=lambda k: bic_per_k[k])
    return {"best_k": int(best_k), "bic_per_k": bic_per_k, "models": models}


def predict(X, model):
    """Hard assignment: componente piu' probabile a posteriori per ogni punto.

        z_n = argmax_k gamma[n, k]

    Le responsabilita' sono RICALCOLATE su X con i parametri di `model`: cosi'
    la funzione lavora anche su dati nuovi, non solo su quelli usati per il fit
    (per i quali si potrebbe riusare model["resp"]).

    Parametri
    ---------
    X : ndarray (N, D)
    model : dict con almeno le chiavi "pis", "mus", "Sigmas"

    Ritorna
    -------
    ndarray (N,) di int in [0, K).
    """
    resp, _ = e_step(X, model["pis"], model["mus"], model["Sigmas"])
    return np.argmax(resp, axis=1).astype(int)
