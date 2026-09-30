"""
Hidden Markov Model discreto: forward-backward scalato, Viterbi, Baum-Welch.

Esercizio per GDL9-10 (Hidden Markov Models) — corso Generative and Deep
Learning, UNIPI, prof. Bacciu.

================================================================================
CONVENZIONI — LEGGERE PRIMA DI SCRIVERE UNA SOLA RIGA
================================================================================

Un HMM discreto e' la tripla (pi, A, B) con K stati latenti e M simboli
osservabili.  Gli stati sono z_1..z_T (valori in {0..K-1}), le osservazioni
sono x_1..x_T (valori in {0..M-1}).

  pi   ndarray shape (K,)
       pi[k] = P(z_1 = k).                       Somma a 1.

  A    ndarray shape (K, K)     <-- QUI SI SBAGLIA
       A[i, j] = P(z_t = j | z_{t-1} = i).
       LA RIGA E' LO STATO DI PARTENZA, LA COLONNA E' LO STATO DI ARRIVO.
       Ogni RIGA somma a 1:  A.sum(axis=1) == 1.
       Conseguenze operative:
         - propagare in avanti una distribuzione riga p (shape (K,)):
               p_next = p @ A          (NON A @ p)
         - propagare all'indietro un vettore di "messaggi" v (shape (K,)):
               v_prev = A @ v          (NON v @ A)
       Se scambi le due cose il codice gira lo stesso e ti restituisce numeri
       plausibili: sbagliata solo la risposta.  Con A simmetrica i test non se
       ne accorgono, quindi tutte le A usate nei test sono ASIMMETRICHE.

  B    ndarray shape (K, M)
       B[k, o] = P(x_t = o | z_t = k).           Ogni RIGA somma a 1.
       La colonna che serve al tempo t e' B[:, obs[t]], shape (K,).

  obs  ndarray shape (T,), dtype intero, valori in {0..M-1}.
       Una singola sequenza.  Indicizzata da 0: obs[0] e' x_1.

================================================================================
SCALING (fattori di normalizzazione) — LA CONVENZIONE ESATTA
================================================================================

L'alpha "grezzo" alpha_t(k) = P(x_1..x_t, z_t = k) va a zero
esponenzialmente in T e a T ~ 300 e' underflow puro.  Si usa quindi la
ricorsione SCALATA di Rabiner:

  alpha[t, k] = P(z_t = k | x_1..x_t)          <-- ogni riga somma a 1
  scaling[t]  = P(x_t | x_1..x_{t-1})          <-- con scaling[0] = P(x_1)

da cui, per la regola della catena,

  P(x_1..x_T) = prod_t scaling[t]      =>   log P(x) = sum_t log(scaling[t]).

Il beta scalato usa GLI STESSI fattori:

  beta[t, k] = P(x_{t+1}..x_T | z_t = k) / prod_{s=t+1}^{T} scaling[s],
  beta[T-1, :] = 1.

Con questa scelta (e SOLO con questa) vale l'identita' comoda

  gamma[t, k] = alpha[t, k] * beta[t, k]

senza dividere per la likelihood: i fattori si cancellano da soli.  Se il tuo
gamma non somma a 1 su ogni riga, hai sbagliato lo scaling di beta.

================================================================================
COSA IMPLEMENTARE
================================================================================
Le funzioni marcate `# TODO`.  `sample_hmm`, `random_hmm` e `forward_naive`
sono gia' fatte: non sono l'esercizio, servono come generatori di dati e come
oracolo indipendente.

Vincoli: solo numpy e stdlib.  Determinismo: `np.random.default_rng(seed)`.
"""

import itertools

import numpy as np

# =============================================================================
# CODICE GIA' FORNITO — non e' l'esercizio
# =============================================================================


def random_hmm(K, M, rng):
    """Genera parametri HMM casuali ma validi (righe normalizzate).

    Parameters
    ----------
    K : int      numero di stati latenti
    M : int      numero di simboli osservabili
    rng : np.random.Generator

    Returns
    -------
    pi : ndarray (K,)    somma 1
    A  : ndarray (K, K)  righe che sommano a 1, A[i, j] = P(z_t=j | z_{t-1}=i)
    B  : ndarray (K, M)  righe che sommano a 1, B[k, o] = P(x=o | z=k)
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

    Parameters
    ----------
    pi : ndarray (K,)
    A  : ndarray (K, K)   A[i, j] = P(z_t = j | z_{t-1} = i)
    B  : ndarray (K, M)   B[k, o] = P(x = o | z = k)
    T  : int              lunghezza della sequenza, T >= 1
    rng : np.random.Generator

    Returns
    -------
    states : ndarray (T,) int   la traiettoria latente vera z_1..z_T
    obs    : ndarray (T,) int   le osservazioni x_1..x_T
    """
    K = pi.shape[0]
    M = B.shape[1]
    states = np.zeros(T, dtype=int)
    obs = np.zeros(T, dtype=int)
    states[0] = rng.choice(K, p=pi)
    obs[0] = rng.choice(M, p=B[states[0]])
    for t in range(1, T):
        # riga = stato corrente, colonna = stato successivo
        states[t] = rng.choice(K, p=A[states[t - 1]])
        obs[t] = rng.choice(M, p=B[states[t]])
    return states, obs


def forward_naive(obs, pi, A, B):
    """ORACOLO brute-force: P(x_1..x_T) per enumerazione esplicita.

    Somma la probabilita' congiunta P(x, z) su TUTTE le K^T traiettorie
    latenti possibili.  Costo O(K^T * T): usabile solo per T molto piccolo
    (diciamo K^T <= 10^5).  Serve a verificare che il forward scalato dia la
    stessa risposta dell'algoritmo che NON e' un algoritmo.

    Returns
    -------
    float : P(x_1..x_T), una probabilita' (NON un logaritmo)
    """
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
# DA IMPLEMENTARE
# =============================================================================


def forward(obs, pi, A, B):
    """Ricorsione forward SCALATA.

    Parameters
    ----------
    obs : ndarray (T,) int
    pi  : ndarray (K,)
    A   : ndarray (K, K)   A[i, j] = P(z_t = j | z_{t-1} = i)
    B   : ndarray (K, M)   B[k, o] = P(x = o | z = k)

    Returns
    -------
    alpha : ndarray (T, K)
        alpha[t, k] = P(z_t = k | obs[0..t]).  OGNI RIGA SOMMA A 1.
        (In notazione 1-based delle slide: P(z_t = k | x_1..x_t).)
    scaling : ndarray (T,)
        scaling[t] = P(obs[t] | obs[0..t-1]), con scaling[0] = P(obs[0]).
        Tutti strettamente positivi se il modello puo' generare `obs`.

    Note
    ----
    Ricorsione:  a = (alpha[t-1] @ A) * B[:, obs[t]];
                 scaling[t] = a.sum();  alpha[t] = a / scaling[t].
    Il caso t = 0 usa pi al posto di (alpha[-1] @ A).
    """
    # TODO
    raise NotImplementedError


def backward(obs, pi, A, B, scaling):
    """Ricorsione backward SCALATA, con i fattori prodotti da `forward`.

    Parameters
    ----------
    obs : ndarray (T,) int
    pi  : ndarray (K,)          (non usato: sta in firma per simmetria)
    A   : ndarray (K, K)
    B   : ndarray (K, M)
    scaling : ndarray (T,)      esattamente l'output di `forward`

    Returns
    -------
    beta : ndarray (T, K)
        beta[T-1, :] = 1 e
        beta[t, k] = P(x_{t+1}..x_T | z_t = k) / prod_{s=t+1}^{T} scaling[s].

    Note
    ----
    Ricorsione all'indietro: beta[t] = (A @ (B[:, obs[t+1]] * beta[t+1]))
                                       / scaling[t+1].
    Attenzione: qui A moltiplica A SINISTRA il vettore (A @ v), perche' si
    somma sullo stato di ARRIVO, cioe' sulle colonne di A.  Il divisore e'
    scaling[t+1], NON scaling[t].
    """
    # TODO
    raise NotImplementedError


def log_likelihood(obs, pi, A, B):
    """log P(x_1..x_T | pi, A, B).

    Returns
    -------
    float : sum_t log(scaling[t]).
    """
    # TODO
    raise NotImplementedError


def posterior_marginals(obs, pi, A, B):
    """Marginali posteriori per singolo istante (smoothing).

    Returns
    -------
    gamma : ndarray (T, K)
        gamma[t, k] = P(z_t = k | x_1..x_T).  Ogni riga somma a 1.

    Note
    ----
    Con lo scaling definito sopra vale gamma = alpha * beta, elemento per
    elemento, senza ulteriori normalizzazioni.
    """
    # TODO
    raise NotImplementedError


def xi(obs, pi, A, B):
    """Marginali posteriori di coppia (per l'M-step su A).

    Returns
    -------
    xi : ndarray (T-1, K, K)
        xi[t, i, j] = P(z_t = i, z_{t+1} = j | x_1..x_T).
        Ogni fetta xi[t] somma a 1 sul totale, e sommata sull'indice j
        (l'asse 2, lo stato di ARRIVO) restituisce gamma[t].
        Con T = 1 la shape e' (0, K, K).

    Note
    ----
    xi[t, i, j] = alpha[t, i] * A[i, j] * B[j, obs[t+1]] * beta[t+1, j]
                  / scaling[t+1].
    """
    # TODO
    raise NotImplementedError


def viterbi(obs, pi, A, B):
    """Sequenza di stati MAP (max-product), IN SPAZIO LOGARITMICO.

    Returns
    -------
    path : ndarray (T,) int
        argmax_{z_1..z_T} P(z_1..z_T | x_1..x_T).
    logprob : float
        log P(path, obs), cioe' il log della probabilita' CONGIUNTA della
        traiettoria migliore e delle osservazioni (non condizionata, non
        normalizzata per P(x)).

    Note
    ----
    Va fatto in log: delta[t, j] = max_i (delta[t-1, i] + log A[i, j])
                                   + log B[j, obs[t]].
    Serve una tabella di backpointer per ricostruire il path all'indietro.
    Zeri in pi/A/B danno -inf: e' corretto, va gestito senza warning
    (`np.errstate(divide='ignore')`), non sostituito con epsilon.
    """
    # TODO
    raise NotImplementedError


def baum_welch(obs, K, M, n_iter=100, tol=1e-6, seed=0):
    """EM per HMM discreti (Baum-Welch) su una singola sequenza.

    Parameters
    ----------
    obs : ndarray (T,) int
    K : int          numero di stati latenti da stimare
    M : int          numero di simboli (alfabeto)
    n_iter : int     numero MASSIMO di iterazioni EM
    tol : float      stop quando l'incremento di log-likelihood e' < tol
    seed : int       seed per l'inizializzazione casuale dei parametri

    Returns
    -------
    dict con chiavi:
      "pi" : ndarray (K,)
      "A"  : ndarray (K, K)
      "B"  : ndarray (K, M)
      "loglik_history" : ndarray (n_iter + 1,)
          loglik_history[0] = log-likelihood dei parametri INIZIALI;
          loglik_history[i] = log-likelihood DOPO l'i-esimo aggiornamento.
          Deve essere non decrescente (e' il teorema di EM).
      "n_iter" : int
          numero di aggiornamenti effettivamente eseguiti
          (= len(loglik_history) - 1).

    Note
    ----
    Inizializzazione OBBLIGATORIA per riproducibilita':
        rng = np.random.default_rng(seed)
        pi, A, B = random_hmm(K, M, rng)

    M-step (con gamma e xi calcolati sui parametri CORRENTI):
        pi_new     = gamma[0]
        A_new[i,j] = sum_{t=0}^{T-2} xi[t,i,j] / sum_{t=0}^{T-2} gamma[t,i]
        B_new[k,o] = sum_{t : obs[t]==o} gamma[t,k] / sum_t gamma[t,k]
    Attenzione al denominatore di A: la somma di gamma si ferma a T-2, NON a
    T-1.  Con T = 1 non ci sono transizioni: A va lasciata invariata.
    """
    # TODO
    raise NotImplementedError
