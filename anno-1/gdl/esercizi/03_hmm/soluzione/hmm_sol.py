"""
SOLUZIONE DI RIFERIMENTO — HMM discreto: forward-backward scalato, Viterbi,
Baum-Welch.  GDL9-10, corso Generative and Deep Learning (UNIPI, Bacciu).

Convenzioni (identiche allo skeleton, ripetute perche' sono meta' del lavoro):

  pi (K,)     pi[k] = P(z_1 = k)
  A  (K, K)   A[i, j] = P(z_t = j | z_{t-1} = i).  RIGA = da, COLONNA = a.
              A.sum(axis=1) == 1.
              In avanti:    p_next = p @ A
              All'indietro: v_prev = A @ v
  B  (K, M)   B[k, o] = P(x_t = o | z_t = k).  B.sum(axis=1) == 1.
  obs (T,)    interi in {0..M-1}

Scaling (Rabiner):
  alpha[t, k] = P(z_t = k | obs[0..t])                      righe a somma 1
  scaling[t]  = P(obs[t] | obs[0..t-1])                     scaling[0]=P(obs[0])
  beta[t, k]  = P(obs[t+1..T-1] | z_t = k) / prod_{s>t} scaling[s]
  => log P(obs) = sum_t log scaling[t]
  => gamma = alpha * beta   (i fattori si cancellano da soli)
"""

import itertools

import numpy as np

# =============================================================================
# CODICE GIA' FORNITO NELLO SKELETON — non e' l'esercizio
# =============================================================================


def random_hmm(K, M, rng):
    """Genera parametri HMM casuali ma validi (righe normalizzate).

    Returns
    -------
    pi : ndarray (K,), A : ndarray (K, K), B : ndarray (K, M)
    """
    pi = rng.random(K) + 0.1
    pi /= pi.sum()
    A = rng.random((K, K)) + 0.1
    A /= A.sum(axis=1, keepdims=True)
    B = rng.random((K, M)) + 0.1
    B /= B.sum(axis=1, keepdims=True)
    return pi, A, B


def sample_hmm(pi, A, B, T, rng):
    """Campiona una sequenza di lunghezza T dall'HMM (pi, A, B).

    Returns
    -------
    states : ndarray (T,) int, obs : ndarray (T,) int
    """
    K = pi.shape[0]
    M = B.shape[1]
    states = np.zeros(T, dtype=int)
    obs = np.zeros(T, dtype=int)
    states[0] = rng.choice(K, p=pi)
    obs[0] = rng.choice(M, p=B[states[0]])
    for t in range(1, T):
        states[t] = rng.choice(K, p=A[states[t - 1]])
        obs[t] = rng.choice(M, p=B[states[t]])
    return states, obs


def forward_naive(obs, pi, A, B):
    """ORACOLO brute-force: P(obs) per enumerazione delle K^T traiettorie."""
    T = len(obs)
    K = pi.shape[0]
    total = 0.0
    for z in itertools.product(range(K), repeat=T):
        p = pi[z[0]] * B[z[0], obs[0]]
        for t in range(1, T):
            p *= A[z[t - 1], z[t]] * B[z[t], obs[t]]
        total += p
    return float(total)


# =============================================================================
# SOLUZIONE
# =============================================================================


def forward(obs, pi, A, B):
    """Ricorsione forward scalata.

    Returns
    -------
    alpha : ndarray (T, K)   alpha[t, k] = P(z_t = k | obs[0..t]), righe a 1
    scaling : ndarray (T,)   scaling[t] = P(obs[t] | obs[0..t-1])
    """
    obs = np.asarray(obs)
    T = obs.shape[0]
    K = pi.shape[0]
    alpha = np.zeros((T, K))
    scaling = np.zeros(T)

    # t = 0: il "prior propagato" e' pi stesso, non c'e' transizione.
    a = pi * B[:, obs[0]]              # P(z_0 = k, obs[0])
    scaling[0] = a.sum()               # = P(obs[0])
    alpha[0] = a / scaling[0]

    for t in range(1, T):
        # alpha[t-1] @ A : distribuzione predittiva P(z_t = j | obs[0..t-1]).
        # E' un vettore RIGA moltiplicato a sinistra: si somma sullo stato di
        # partenza, cioe' sulle RIGHE di A.  A @ alpha[t-1] sarebbe A^T.
        a = (alpha[t - 1] @ A) * B[:, obs[t]]
        scaling[t] = a.sum()           # = P(obs[t] | obs[0..t-1])
        alpha[t] = a / scaling[t]

    return alpha, scaling


def backward(obs, pi, A, B, scaling):
    """Ricorsione backward scalata con gli stessi fattori del forward.

    Returns
    -------
    beta : ndarray (T, K)
    """
    obs = np.asarray(obs)
    T = obs.shape[0]
    K = pi.shape[0]
    beta = np.zeros((T, K))
    beta[T - 1] = 1.0

    for t in range(T - 2, -1, -1):
        # v[j] = B[j, obs[t+1]] * beta[t+1, j]  e' il messaggio che arriva in
        # z_{t+1}.  Per portarlo su z_t si somma sullo stato di ARRIVO j,
        # cioe' sulle COLONNE di A  ->  A @ v  (matrice per vettore colonna).
        beta[t] = (A @ (B[:, obs[t + 1]] * beta[t + 1])) / scaling[t + 1]

    return beta


def log_likelihood(obs, pi, A, B):
    """log P(obs) = somma dei log dei fattori di scaling."""
    _, scaling = forward(obs, pi, A, B)
    return float(np.log(scaling).sum())


def posterior_marginals(obs, pi, A, B):
    """gamma[t, k] = P(z_t = k | obs[0..T-1]), shape (T, K)."""
    alpha, scaling = forward(obs, pi, A, B)
    beta = backward(obs, pi, A, B, scaling)
    # Con lo scaling di Rabiner il prodotto e' gia' normalizzato: il fattore
    # prod_{s<=t} scaling[s] del forward e prod_{s>t} scaling[s] del backward
    # si combinano in prod_s scaling[s] = P(obs), che e' esattamente il
    # denominatore che servirebbe.  Nessuna normalizzazione ulteriore.
    return alpha * beta


def xi(obs, pi, A, B):
    """xi[t, i, j] = P(z_t = i, z_{t+1} = j | obs), shape (T-1, K, K)."""
    obs = np.asarray(obs)
    T = obs.shape[0]
    K = pi.shape[0]
    alpha, scaling = forward(obs, pi, A, B)
    beta = backward(obs, pi, A, B, scaling)

    out = np.zeros((T - 1, K, K))
    for t in range(T - 1):
        # outer product: riga i = stato al tempo t, colonna j = stato a t+1.
        # alpha[t][:, None] varia lungo le righe, il messaggio all'indietro
        # varia lungo le colonne.  Invertire i due None trasporrebbe xi.
        out[t] = (
            alpha[t][:, None]
            * A
            * (B[:, obs[t + 1]] * beta[t + 1])[None, :]
            / scaling[t + 1]
        )
    return out


def viterbi(obs, pi, A, B):
    """Sequenza MAP in spazio logaritmico.

    Returns
    -------
    path : ndarray (T,) int
    logprob : float   log P(path, obs)
    """
    obs = np.asarray(obs)
    T = obs.shape[0]
    K = pi.shape[0]

    # log(0) = -inf e' il valore giusto per una transizione impossibile:
    # va lasciato -inf, non sostituito con un epsilon.  Silenziamo solo il
    # RuntimeWarning di numpy.
    with np.errstate(divide="ignore"):
        log_pi = np.log(pi)
        log_A = np.log(A)
        log_B = np.log(B)

    delta = np.full((T, K), -np.inf)   # delta[t, k] = max log P(z_0..z_t=k, obs[0..t])
    psi = np.zeros((T, K), dtype=int)  # backpointer

    delta[0] = log_pi + log_B[:, obs[0]]

    for t in range(1, T):
        # score[i, j] = delta[t-1, i] + log A[i, j]: riga = stato precedente.
        score = delta[t - 1][:, None] + log_A
        psi[t] = np.argmax(score, axis=0)          # max sullo stato PRECEDENTE
        delta[t] = score[psi[t], np.arange(K)] + log_B[:, obs[t]]

    path = np.zeros(T, dtype=int)
    path[T - 1] = int(np.argmax(delta[T - 1]))
    for t in range(T - 2, -1, -1):
        path[t] = psi[t + 1][path[t + 1]]

    return path, float(delta[T - 1].max())


def baum_welch(obs, K, M, n_iter=100, tol=1e-6, seed=0):
    """EM per HMM discreto su una singola sequenza.

    Returns
    -------
    dict con "pi", "A", "B", "loglik_history" (ndarray), "n_iter" (int).
    """
    obs = np.asarray(obs)
    T = obs.shape[0]

    rng = np.random.default_rng(seed)
    pi, A, B = random_hmm(K, M, rng)

    history = [log_likelihood(obs, pi, A, B)]
    n_done = 0

    # maschera one-hot dei simboli: onehot[t, o] = 1 se obs[t] == o.
    # Serve per l'M-step di B senza loop su t.
    onehot = np.zeros((T, M))
    onehot[np.arange(T), obs] = 1.0

    for _ in range(n_iter):
        # ---- E-step: responsabilita' sotto i parametri CORRENTI -----------
        gamma = posterior_marginals(obs, pi, A, B)          # (T, K)
        xis = xi(obs, pi, A, B)                             # (T-1, K, K)

        # ---- M-step -------------------------------------------------------
        pi = gamma[0].copy()

        if T > 1:
            num_A = xis.sum(axis=0)                         # (K, K)
            # ATTENZIONE: il denominatore somma gamma solo fino a T-2, perche'
            # dall'ultimo istante non parte nessuna transizione.
            den_A = gamma[:-1].sum(axis=0)                  # (K,)
            safe = den_A > 0
            A_new = A.copy()
            A_new[safe] = num_A[safe] / den_A[safe, None]
            A = A_new
        # con T == 1 non ci sono transizioni osservate: A resta invariata.

        num_B = gamma.T @ onehot                            # (K, M)
        den_B = gamma.sum(axis=0)                           # (K,)
        safe = den_B > 0
        B_new = B.copy()
        B_new[safe] = num_B[safe] / den_B[safe, None]
        B = B_new

        n_done += 1
        ll = log_likelihood(obs, pi, A, B)
        history.append(ll)

        if ll - history[-2] < tol:
            break

    return {
        "pi": pi,
        "A": A,
        "B": B,
        "loglik_history": np.array(history),
        "n_iter": n_done,
    }
