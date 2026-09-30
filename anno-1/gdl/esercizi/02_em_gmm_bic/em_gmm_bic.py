"""Esercizio: EM per Gaussian Mixture Models + model selection (BIC/AIC).

Riferimento teorico: `Lessons/GDL8 learning hidden.pdf` (Expectation-Maximization,
exact maximum likelihood learning in mixture models) e `Lessons/GDL2 prob refresh.pdf`
(gaussiana multivariata). Ricalca il Midterm 1 del corso.

Implementa tutte le funzioni marcate `# TODO`. Il generatore di dati sintetici
e' gia' fornito: non va toccato.

Convenzioni globali usate ovunque nel modulo:
    N = numero di campioni, D = dimensionalita', K = numero di componenti.
    X       -> (N, D)
    pis     -> (K,)      pesi di mixing, sommano a 1
    mus     -> (K, D)    medie
    Sigmas  -> (K, D, D) covarianze piene, simmetriche definite positive
    resp    -> (N, K)    responsabilita' gamma[n, k] = p(z_n = k | x_n, theta)

Vincoli: solo numpy e stdlib. Niente scipy, sklearn, torch, matplotlib.
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
# Codice fornito (non didattico): generatore di dati sintetici. NON MODIFICARE. #
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
    """TODO: log(sum(exp(A))) lungo `axis`, calcolato in modo NUMERICAMENTE STABILE.

    Non e' fornita di proposito: scriverla stabile fa parte dell'esercizio.
    `np.log(np.sum(np.exp(A), axis=axis))` non e' una risposta accettabile.

    Ricorda che vale l'identita', per ogni costante m:

        log(sum_i exp(a_i)) = m + log(sum_i exp(a_i - m))

    e che la scelta giusta di m elimina l'overflow. Pensa anche a cosa succede
    quando tutti gli elementi lungo l'asse valgono -inf.

    Parametri
    ---------
    A : ndarray
    axis : int

    Ritorna
    -------
    ndarray con `axis` ridotto (NON tenuto: l'output ha una dimensione in meno).
    """
    # TODO
    raise NotImplementedError


# --------------------------------------------------------------------------- #
# 1. Densita' gaussiana multivariata                                           #
# --------------------------------------------------------------------------- #
def log_gaussian_pdf(X, mu, Sigma):
    """TODO: log-densita' gaussiana multivariata, valutata su tutte le righe di X.

        log N(x | mu, Sigma) = -0.5 * ( D*log(2*pi) + log|Sigma| + (x-mu)^T Sigma^-1 (x-mu) )

    Va calcolata in modo numericamente stabile, cioe' passando dalla
    fattorizzazione di Cholesky Sigma = L L^T (`np.linalg.cholesky`, L
    triangolare bassa) invece di invertire Sigma e calcolarne il determinante:
        - il log-determinante si ottiene dalla diagonale di L;
        - la forma quadratica di Mahalanobis si ottiene risolvendo un sistema
          triangolare (`np.linalg.solve`) e prendendo la norma al quadrato.

    Parametri
    ---------
    X : ndarray (N, D)
    mu : ndarray (D,)
    Sigma : ndarray (D, D) simmetrica definita positiva

    Ritorna
    -------
    ndarray (N,) di log-densita'.
    """
    # TODO
    raise NotImplementedError


def gaussian_pdf(X, mu, Sigma):
    """TODO: densita' gaussiana multivariata su tutte le righe di X.

    Deve essere calcolata passando per la log-densita' (vedi `log_gaussian_pdf`)
    e poi esponenziando: e' l'unica strada sensata anche in dimensione moderata,
    perche' il termine di Mahalanobis puo' valere migliaia e la forma diretta
    va in overflow/underflow molto prima.

    Parametri
    ---------
    X : ndarray (N, D)
    mu : ndarray (D,)
    Sigma : ndarray (D, D)

    Ritorna
    -------
    ndarray (N,) di densita' >= 0.
    """
    # TODO
    raise NotImplementedError


# --------------------------------------------------------------------------- #
# 2. Inizializzazione (k-means++)                                              #
# --------------------------------------------------------------------------- #
def init_params(X, K, rng):
    """TODO: inizializza (pis, mus, Sigmas) con k-means++ sulle medie.

    k-means++ va implementato a mano (niente sklearn):
      1. il primo centro e' un punto scelto uniformemente fra le righe di X;
      2. ogni centro successivo e' un punto estratto con probabilita'
         proporzionale a D(x)^2, dove D(x) e' la distanza euclidea di x dal
         centro gia' scelto piu' vicino.
    Attenzione al caso in cui la somma delle D(x)^2 sia zero (punti duplicati):
    serve un fallback, altrimenti `rng.choice` con p non normalizzabile esplode.

    - pis: uniformi, 1/K ciascuno.
    - Sigmas: covarianza empirica dell'INTERO dataset, la stessa per tutte le K
      componenti (usa `np.cov(..., rowvar=False, bias=True)`; aggiungici un
      ridge minimo sulla diagonale per garantirne la definita positivita').

    Tutta la casualita' deve passare da `rng`: nessun `np.random.seed`.

    Parametri
    ---------
    X : ndarray (N, D)
    K : int
    rng : np.random.Generator

    Ritorna
    -------
    (pis (K,), mus (K, D), Sigmas (K, D, D))
    """
    # TODO
    raise NotImplementedError


# --------------------------------------------------------------------------- #
# 3. E-step                                                                    #
# --------------------------------------------------------------------------- #
def e_step(X, pis, mus, Sigmas):
    """TODO: E-step, responsabilita' e log-likelihood del dataset.

        gamma[n, k] = pi_k N(x_n | mu_k, Sigma_k) / sum_j pi_j N(x_n | mu_j, Sigma_j)
        loglik      = sum_n log( sum_k pi_k N(x_n | mu_k, Sigma_k) )

    Da fare interamente in spazio log: costruisci la matrice (N, K) dei
    log-numeratori log(pi_k) + log N(x_n | mu_k, Sigma_k), riducila con
    `logsumexp` sulle componenti per ottenere log p(x_n), e ricava le
    responsabilita' esponenziando la differenza. Il rapporto fra densita'
    calcolate in spazio lineare produce 0/0 = NaN non appena i punti sono
    lontani dalle componenti.

    `loglik` e' la log-likelihood TOTALE (somma su tutti gli n), non la media.

    Parametri
    ---------
    X : ndarray (N, D)
    pis : ndarray (K,)
    mus : ndarray (K, D)
    Sigmas : ndarray (K, D, D)

    Ritorna
    -------
    resp : ndarray (N, K), ogni riga somma a 1.
    loglik : float
    """
    # TODO
    raise NotImplementedError


# --------------------------------------------------------------------------- #
# 4. M-step                                                                    #
# --------------------------------------------------------------------------- #
def m_step(X, resp, reg=1e-6):
    """TODO: M-step, massimizzazione in forma chiusa della Q function.

        N_k     = sum_n gamma[n, k]
        pi_k    = N_k / N
        mu_k    = (1 / N_k) sum_n gamma[n, k] x_n
        Sigma_k = (1 / N_k) sum_n gamma[n, k] (x_n - mu_k)(x_n - mu_k)^T + reg * I

    Nella formula di Sigma_k compare la mu_k NUOVA: le medie vanno aggiornate
    prima delle covarianze. Attenzione anche alle componenti "morte"
    (N_k ~ 0): la divisione va protetta.

    `reg` e' aggiunto alla diagonale di ogni covarianza. Serve contro la
    degenerazione della likelihood delle misture: se una componente collassa su
    un singolo punto la sua covarianza tende a zero e la likelihood diverge.

    Parametri
    ---------
    X : ndarray (N, D)
    resp : ndarray (N, K), assunta normalizzata per riga
    reg : float

    Ritorna
    -------
    (pis (K,), mus (K, D), Sigmas (K, D, D))
    """
    # TODO
    raise NotImplementedError


# --------------------------------------------------------------------------- #
# 5. Ciclo EM completo                                                         #
# --------------------------------------------------------------------------- #
def fit_gmm(X, K, n_iter=200, tol=1e-6, seed=0, reg=1e-6):
    """TODO: stima una GMM a K componenti con EM.

    Schema richiesto (l'ordine conta per la coerenza del risultato):
        init  -> E                     : loglik_history[0] = loglik ai parametri iniziali
        ripeti: M -> E, registra loglik
        stop quando l'incremento di log-likelihood scende sotto `tol`
             oppure dopo `n_iter` aggiornamenti.

    Con questo schema i parametri restituiti, `resp` e l'ultimo elemento di
    `loglik_history` si riferiscono sempre agli STESSI parametri (la E finale e'
    calcolata dopo l'ultima M). Se inverti l'ordine, `resp` finisce per essere
    quello dei parametri precedenti.

    `loglik_history` deve risultare non decrescente: e' la garanzia teorica di
    EM, non un'opzione. Se scende, c'e' un bug.

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
    # TODO
    raise NotImplementedError


# --------------------------------------------------------------------------- #
# 6. Model selection                                                           #
# --------------------------------------------------------------------------- #
def n_params_gmm(K, D):
    """TODO: numero di parametri liberi di una GMM a covarianze piene.

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
    # TODO
    raise NotImplementedError


def bic(loglik, n_params, N):
    """TODO: Bayesian Information Criterion.

    CONVENZIONE DA USARE QUI (e' la fonte classica di confusione):

        BIC = -2 * loglik + n_params * log(N)

    quindi **piu' basso e' meglio**: il primo termine premia il fit, il secondo
    penalizza la complessita'. Esiste in giro anche la convenzione con il segno
    opposto (BIC = loglik - 0.5 * n_params * log(N), da MASSIMIZZARE): e' la
    stessa quantita' cambiata di segno e riscalata, ma se all'orale si dice
    "si prende il BIC piu' alto" senza dichiarare la convenzione, e' sbagliato
    meta' delle volte. Qui: si sceglie il modello con BIC MINIMO.

    `loglik` e' la log-likelihood TOTALE del dataset (somma su tutti gli N
    campioni), non la media per campione.

    Parametri
    ---------
    loglik : float
    n_params : int
    N : int

    Ritorna
    -------
    float
    """
    # TODO
    raise NotImplementedError


def aic(loglik, n_params):
    """TODO: Akaike Information Criterion, stessa convenzione di segno del BIC.

        AIC = -2 * loglik + 2 * n_params

    Piu' basso e' meglio. Rispetto al BIC la penalita' non dipende da N.

    Parametri
    ---------
    loglik : float
    n_params : int

    Ritorna
    -------
    float
    """
    # TODO
    raise NotImplementedError


def select_k(X, k_values, seed=0, **kw):
    """TODO: sceglie il numero di componenti con il BIC.

    Per ogni k in `k_values` stima una GMM con `fit_gmm(X, k, seed=seed, **kw)`,
    calcola il BIC usando l'ULTIMA log-likelihood della history (quella dei
    parametri finali) e sceglie il k con BIC MINIMO. In caso di pareggio esatto
    vince il k che compare prima in `k_values`.

    Lo stesso `seed` va usato per tutti i k: il confronto fra modelli deve
    dipendere da k, non dalla fortuna dell'inizializzazione.

    Parametri
    ---------
    X : ndarray (N, D)
    k_values : iterable di int
    seed : int, passato a fit_gmm
    **kw : altri argomenti inoltrati a fit_gmm (n_iter, tol, reg)

    Ritorna
    -------
    dict con chiavi:
        "best_k"    int
        "bic_per_k" dict {k: bic}
        "models"    dict {k: dict restituito da fit_gmm}
    """
    # TODO
    raise NotImplementedError


def predict(X, model):
    """TODO: hard assignment, componente piu' probabile a posteriori per ogni punto.

        z_n = argmax_k gamma[n, k]

    Le responsabilita' vanno RICALCOLATE su X con i parametri di `model`, cosi'
    la funzione lavora anche su dati nuovi e non solo su quelli usati per il fit
    (per i quali si potrebbe riusare model["resp"]).

    Parametri
    ---------
    X : ndarray (N, D)
    model : dict con almeno le chiavi "pis", "mus", "Sigmas"

    Ritorna
    -------
    ndarray (N,) di int in [0, K).
    """
    # TODO
    raise NotImplementedError
