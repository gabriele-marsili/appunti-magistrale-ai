"""MDP tabellari: value iteration, policy iteration, Q-learning.

Esercizio per GDL34 ((Deep) Reinforcement Learning — Fundamentals) — corso
Generative and Deep Learning, UNIPI, prof. Bacciu.

================================================================================
CONVENZIONI — LEGGERE PRIMA DI SCRIVERE UNA SOLA RIGA
================================================================================

Un MDP e' la tupla (S, A, P, R, gamma) delle slide.  Qui `S` e `A` sono
interi (numero di stati, numero di azioni), gli stati sono {0..S-1} e le
azioni {0..A-1}.

  P    ndarray shape (S, A, S)          <-- QUI SI SBAGLIA
       P[s, a, s'] = P(S_{t+1} = s' | S_t = s, A_t = a)   (la P^a_{ss'} delle
       slide).  IL PRIMO ASSE E' LO STATO DI PARTENZA, L'ULTIMO E' LO STATO DI
       ARRIVO.  Normalizzazione: P[s, a, :].sum() == 1 per ogni (s, a), cioe'
       P.sum(axis=2) e' una matrice di tutti 1.
       Conseguenza operativa: l'unica contrazione lecita con un vettore di
       valori V (shape (S,)) e' sull'ULTIMO asse, e da' shape (S, A):
             P @ V          oppure   np.einsum("sat,t->sa", P, V)
       Contrarre il primo asse (`np.einsum("tas,t->sa", P, V)`) produce shape
       (S, A) anche lui: nessuna eccezione, nessun warning, solo numeri
       sbagliati.  Il gridworld dei test e' asimmetrico apposta.

  R    ndarray shape (S, A)
       R[s, a] = E[R_{t+1} | S_t = s, A_t = a]            (la R^a_s delle
       slide).  E' gia' un valore ATTESO sul prossimo stato: non va rimediata
       nessuna somma su s'.  Il premio e' associato alla COPPIA (s, a), cioe'
       si incassa USCENDO da s, non entrando in s.

  gamma  float in [0, 1).  Sconto.  gamma ~ 0 = valutazione miope, gamma ~ 1 =
       lungimirante.  Il return e' G_t = sum_{k>=0} gamma^k R_{t+k+1}.

  V    ndarray shape (S,)     V[s] = valore dello stato s.
  Q    ndarray shape (S, A)   Q[s, a] = valore della coppia (s, a).

  pi   ndarray shape (S, A)   POLICY STOCASTICA: pi[s, a] = pi(a | s).
       Ogni RIGA somma a 1.  Una policy deterministica si rappresenta come
       matrice ONE-HOT: pi[s, a] = 1 se a = pi(s), 0 altrimenti.  Tutte le
       funzioni che restituiscono una policy restituiscono questa forma, anche
       quando la policy e' deterministica: cosi' `policy_evaluation` ha un solo
       tipo di input da gestire.

Stati TERMINALI: sono assorbenti a premio nullo, cioe' P[s, a, s] = 1 e
R[s, a] = 0 per ogni a.  Ne segue V*(s) = 0 esattamente, per qualunque gamma.

================================================================================
LE TRE EQUAZIONI (notazione delle slide)
================================================================================

Bellman ATTESO (valuta una policy data):

    V^pi(s) = sum_a pi(a|s) [ R[s,a] + gamma sum_{s'} P[s,a,s'] V^pi(s') ]
            = (T^pi V^pi)(s)

Bellman OTTIMO (valuta la policy migliore):

    V*(s)   = max_a  [ R[s,a] + gamma sum_{s'} P[s,a,s'] V*(s') ]
            = (T* V*)(s)

La differenza fra i due e' UNA parola: `sum_a pi(a|s)` contro `max_a`.  Non
sono la stessa cosa e non danno la stessa risposta; l'errore piu' comune
dell'esercizio e' mettere un `max` dentro `policy_evaluation`.

Q-learning (model free, off-policy):

    Q(s,a) <- Q(s,a) + alpha [ r + gamma max_{a'} Q(s',a') - Q(s,a) ]

Il target usa `max_{a'}`, NON la Q dell'azione che la policy comportamentale
eseguira' davvero al passo successivo.  Mettere li' l'azione eseguita da'
SARSA, che e' un algoritmo diverso e converge a un'altra cosa.

================================================================================
COSA IMPLEMENTARE
================================================================================
Le funzioni marcate `# TODO`.  `make_gridworld`, `make_env_step`,
`make_random_mdp` e `render_policy` sono gia' fatte: sono l'ambiente e gli
strumenti di debug, non l'esercizio.

Vincoli: solo numpy e stdlib.  Niente torch, niente gym, niente scipy.
Determinismo: `np.random.default_rng(seed)`, mai `np.random.seed`.
"""

import numpy as np

# =============================================================================
# CODICE GIA' FORNITO — non e' l'esercizio
# =============================================================================

ACTION_NAMES = ("N", "E", "S", "W")
_DELTAS = ((-1, 0), (0, 1), (1, 0), (0, -1))
_ARROWS = ("^", ">", "v", "<")


def make_gridworld(
    n_rows=4,
    n_cols=4,
    goal=(0, 3),
    trap=(1, 3),
    step_reward=-0.04,
    goal_reward=1.0,
    trap_reward=-1.0,
    slip=0.0,
):
    """Costruisce un gridworld come MDP tabellare.

    Griglia `n_rows` x `n_cols`, stato s = riga * n_cols + colonna (la riga 0
    e' quella in alto).  Quattro azioni, nell'ordine N, E, S, W (indici 0,1,2,3
    — e' l'ordine ciclico orario, quindi le due azioni PERPENDICOLARI ad `a`
    sono `(a-1) % 4` e `(a+1) % 4`).  Sbattere contro il bordo lascia fermi.

    Parameters
    ----------
    n_rows, n_cols : int         dimensioni della griglia
    goal : (int, int)            cella terminale "buona", coordinate (riga, col)
    trap : (int, int)            cella terminale "cattiva"
    step_reward : float          premio per ogni transizione ordinaria
    goal_reward : float          premio per la transizione che ENTRA nel goal
    trap_reward : float          premio per la transizione che ENTRA nella trap
    slip : float in [0, 1]       probabilita' totale di slittamento: con prob.
        `1 - slip` si esegue l'azione scelta, con prob. `slip / 2` ciascuna si
        esegue una delle due azioni perpendicolari.  `slip = 0` da' un
        ambiente deterministico.

    Returns
    -------
    dict con chiavi:
      "P"        ndarray (S, A, S)  P[s, a, s'] = P(S_{t+1}=s' | S_t=s, A_t=a).
                                    P.sum(axis=2) == 1.
      "R"        ndarray (S, A)     R[s, a] = E[R_{t+1} | S_t=s, A_t=a],
                                    gia' mediata sulle transizioni.
      "terminal" ndarray (S,) bool  True per goal e trap.  Gli stati terminali
                                    sono ASSORBENTI a premio nullo:
                                    P[s, a, s] = 1 e R[s, a] = 0.
      "n_rows", "n_cols" : int
      "goal", "trap"     : int      indici di stato (non coordinate)
      "n_states", "n_actions" : int
    """
    S = n_rows * n_cols
    A = 4

    def idx(r, c):
        return r * n_cols + c

    goal_s = idx(*goal)
    trap_s = idx(*trap)
    terminal = np.zeros(S, dtype=bool)
    terminal[goal_s] = True
    terminal[trap_s] = True

    reward_entering = np.full(S, float(step_reward))
    reward_entering[goal_s] = float(goal_reward)
    reward_entering[trap_s] = float(trap_reward)

    P = np.zeros((S, A, S))
    R = np.zeros((S, A))

    for r in range(n_rows):
        for c in range(n_cols):
            s = idx(r, c)
            if terminal[s]:
                P[s, :, s] = 1.0
                continue
            for a in range(A):
                effettive = (
                    (a, 1.0 - slip),
                    ((a - 1) % 4, slip / 2.0),
                    ((a + 1) % 4, slip / 2.0),
                )
                for d, w in effettive:
                    if w == 0.0:
                        continue
                    dr, dc = _DELTAS[d]
                    rr, cc = r + dr, c + dc
                    if not (0 <= rr < n_rows and 0 <= cc < n_cols):
                        rr, cc = r, c
                    P[s, a, idx(rr, cc)] += w
                R[s, a] = float(P[s, a] @ reward_entering)

    return {
        "P": P,
        "R": R,
        "terminal": terminal,
        "n_rows": n_rows,
        "n_cols": n_cols,
        "goal": goal_s,
        "trap": trap_s,
        "n_states": S,
        "n_actions": A,
    }


def make_env_step(P, R, terminal):
    """Chiude (P, R, terminal) dentro un simulatore MODEL-FREE.

    Restituisce una funzione

        env_step(s, a, rng) -> (s_next, reward, done)

    che campiona `s_next` da P[s, a, :], restituisce il premio R[s, a] e il
    flag `done = terminal[s_next]`.  E' l'UNICO accesso all'ambiente che
    `q_learning` puo' usare: dentro `q_learning` non devono comparire ne' `P`
    ne' `R`, altrimenti non e' model free.

    Il premio e' deterministico data la coppia (s, a) — vale R[s, a], che per
    definizione e' gia' il valore atteso E[R_{t+1} | s, a].  La stocasticita'
    dell'ambiente sta tutta nella transizione.

    Parameters
    ----------
    P : ndarray (S, A, S)
    R : ndarray (S, A)
    terminal : ndarray (S,) bool

    Returns
    -------
    callable env_step(s: int, a: int, rng: np.random.Generator)
        -> (s_next: int, reward: float, done: bool)
    """
    S = P.shape[2]
    cum = np.cumsum(P, axis=2)

    def env_step(s, a, rng):
        u = rng.random()
        s_next = int(np.searchsorted(cum[s, a], u))
        if s_next >= S:
            s_next = S - 1
        return s_next, float(R[s, a]), bool(terminal[s_next])

    return env_step


def make_random_mdp(S, A, rng, reward_scale=1.0, sparsity=0.35):
    """MDP tabellare casuale ma valido (nessuno stato terminale).

    Serve nei test come MDP "generico": niente struttura di griglia, premi di
    segno misto, transizioni sparse.

    Returns
    -------
    P : ndarray (S, A, S)   righe P[s, a, :] normalizzate a 1
    R : ndarray (S, A)      uniformi in [-reward_scale, reward_scale]
    """
    logits = rng.random((S, A, S))
    mask = rng.random((S, A, S)) < sparsity
    logits = np.where(mask, 0.0, logits + 0.05)
    dead = logits.sum(axis=2) == 0.0
    logits[dead] = 1.0
    P = logits / logits.sum(axis=2, keepdims=True)
    R = reward_scale * (2.0 * rng.random((S, A)) - 1.0)
    return P, R


def render_policy(pi, n_rows, n_cols, terminal=None):
    """Rende una policy (S, A) one-hot come griglia di frecce. Solo per debug.

    Restituisce una stringa: `^` = N, `>` = E, `v` = S, `<` = W, `T` = stato
    terminale.
    """
    a_star = np.asarray(pi).argmax(axis=1)
    righe = []
    for r in range(n_rows):
        cella = []
        for c in range(n_cols):
            s = r * n_cols + c
            if terminal is not None and terminal[s]:
                cella.append("T")
            else:
                cella.append(_ARROWS[a_star[s]])
        righe.append(" ".join(cella))
    return "\n".join(righe)


# =============================================================================
# DA IMPLEMENTARE
# =============================================================================


def q_from_v(V, P, R, gamma):
    """Action-value function indotta da una state-value function.

        Q(s, a) = R[s, a] + gamma * sum_{s'} P[s, a, s'] V[s']

    (E' la q_pi(s,a) = R^a_s + gamma sum_{s'} P^a_{ss'} v_pi(s') delle slide.)

    Parameters
    ----------
    V : ndarray (S,)
    P : ndarray (S, A, S)     P[s, a, s'], somma 1 sull'ULTIMO asse
    R : ndarray (S, A)
    gamma : float

    Returns
    -------
    Q : ndarray (S, A)

    Note
    ----
    La somma su s' contrae l'ULTIMO asse di P.  Se ti viene la shape giusta ma
    i numeri sbagliati, hai contratto il primo.
    """
    # TODO
    raise NotImplementedError


def greedy_policy(Q):
    """Policy deterministica greedy rispetto a Q, in forma ONE-HOT.

        pi(s) = argmax_a Q[s, a]

    Parameters
    ----------
    Q : ndarray (S, A)

    Returns
    -------
    pi : ndarray (S, A)
        pi[s, argmax_a Q[s, a]] = 1.0, tutto il resto 0.0.  Ogni riga somma
        a 1.  I pareggi si rompono con l'indice piu' PICCOLO (la convenzione
        di `np.argmax`): serve perche' i test confrontino policy uguali.
    """
    # TODO
    raise NotImplementedError


def bellman_backup(V, P, R, gamma):
    """UN passo di backup di OTTIMALITA' (Bellman optimality backup).

        (T* V)(s) = max_a [ R[s, a] + gamma * sum_{s'} P[s, a, s'] V[s'] ]

    Parameters
    ----------
    V : ndarray (S,)
    P : ndarray (S, A, S)
    R : ndarray (S, A)
    gamma : float

    Returns
    -------
    V_new : ndarray (S,)   il valore aggiornato T*V
    pi    : ndarray (S, A) la policy greedy rispetto a Q(V), in forma one-hot

    Note
    ----
    T* e' una contrazione di modulo gamma in norma infinito:
    ||T*V1 - T*V2||_inf <= gamma ||V1 - V2||_inf.  E' questo, e nient'altro,
    che garantisce la convergenza di value iteration.
    """
    # TODO
    raise NotImplementedError


def value_iteration(P, R, gamma, tol=1e-12, max_iter=100000):
    """Value iteration: itera il backup di ottimalita' fino a punto fisso.

        V_{k+1}(s) = max_a [ R[s,a] + gamma sum_{s'} P[s,a,s'] V_k(s') ]

    Parameters
    ----------
    P : ndarray (S, A, S)
    R : ndarray (S, A)
    gamma : float
    tol : float      criterio d'arresto su ||V_{k+1} - V_k||_inf
    max_iter : int   tetto sul numero di backup

    Returns
    -------
    V : ndarray (S,)     stima di V*
    pi : ndarray (S, A)  policy greedy rispetto all'ULTIMA V, one-hot
    n_iter : int         numero di backup effettivamente eseguiti

    Note
    ----
    Inizializzare V a zero.  Il conteggio: `n_iter` cresce di 1 a ogni backup,
    compreso quello che fa scattare il criterio d'arresto (quindi n_iter >= 1
    sempre).  Fermarsi quando ||V_{k+1} - V_k||_inf < tol.
    """
    # TODO
    raise NotImplementedError


def policy_evaluation(pi, P, R, gamma, tol=1e-12, max_iter=100000):
    """Iterative policy evaluation: calcola V^pi iterando Bellman ATTESO.

        V_{k+1}(s) = sum_a pi(a|s) [ R[s,a] + gamma sum_{s'} P[s,a,s'] V_k(s') ]

    Equivalentemente, in forma matriciale con

        P_pi[s, s'] = sum_a pi[s, a] P[s, a, s']       shape (S, S)
        R_pi[s]     = sum_a pi[s, a] R[s, a]           shape (S,)

    si itera  V <- R_pi + gamma * (P_pi @ V).

    Parameters
    ----------
    pi : ndarray (S, A)   policy stocastica, righe a somma 1 (one-hot se
                          deterministica)
    P : ndarray (S, A, S)
    R : ndarray (S, A)
    gamma : float
    tol : float           arresto su ||V_{k+1} - V_k||_inf
    max_iter : int

    Returns
    -------
    V : ndarray (S,)      V^pi

    Note
    ----
    QUI NON CI VA NESSUN `max`.  Il punto fisso di questa iterazione risolve il
    sistema lineare (I - gamma P_pi) V = R_pi, che per gamma < 1 ha soluzione
    unica: il test centrale confronta proprio con `np.linalg.solve` su quel
    sistema.  Inizializzare V a zero.
    """
    # TODO
    raise NotImplementedError


def policy_iteration(P, R, gamma, tol=1e-12, max_iter=1000):
    """Policy iteration: valutazione + miglioramento greedy, alternati.

        1. valuta:   V <- V^pi              (con `policy_evaluation`)
        2. migliora: pi' <- greedy(Q(V))    (con `q_from_v` + `greedy_policy`)
        3. se pi' == pi ci si ferma, altrimenti si ricomincia

    Parameters
    ----------
    P : ndarray (S, A, S)
    R : ndarray (S, A)
    gamma : float
    tol : float      tolleranza passata a `policy_evaluation`
    max_iter : int   tetto sul numero di round valutazione+miglioramento

    Returns
    -------
    V : ndarray (S,)     V^pi della policy finale, che e' V*
    pi : ndarray (S, A)  policy ottima, one-hot
    n_iter : int         numero di round eseguiti

    Note
    ----
    Policy INIZIALE OBBLIGATORIA per riproducibilita': azione 0 in ogni stato,
    cioe' `pi = np.zeros((S, A)); pi[:, 0] = 1.0`.
    `n_iter` conta i round: incrementarlo a ogni miglioramento tentato,
    compreso quello finale che trova la policy gia' stabile.
    Il numero di round e' tipicamente di UN ORDINE DI GRANDEZZA piu' piccolo
    del numero di backup di value iteration: e' il motivo per cui l'algoritmo
    esiste, e un test lo verifica.
    """
    # TODO
    raise NotImplementedError


def epsilon_greedy(Q, s, eps, rng):
    """Campiona un'azione dalla policy eps-greedy delle slide.

        pi'(a|s) = eps/m + (1 - eps)   se a = argmax_{a'} Q(s, a')
                 = eps/m               altrimenti

    dove m = numero di azioni.  Leggila cosi': con probabilita' `eps` si
    estrae UNIFORMEMENTE fra TUTTE le m azioni (l'azione greedy COMPRESA), con
    probabilita' `1 - eps` si prende la greedy.  Non e' la stessa cosa di
    "con probabilita' eps prendi un'azione non greedy": quella darebbe
    pi'(a*|s) = 1 - eps, e con eps = 1 non sceglierebbe MAI la greedy.

    Parameters
    ----------
    Q : ndarray (S, A)
    s : int                      stato corrente
    eps : float in [0, 1]
    rng : np.random.Generator

    Returns
    -------
    a : int    l'azione campionata, in {0..A-1}

    Note
    ----
    Con eps = 0 la funzione e' deterministica e restituisce sempre
    `argmax_a Q[s, a]`.  Con eps = 1 le m azioni sono equiprobabili.
    Usare solo `rng`, mai `np.random`.
    """
    # TODO
    raise NotImplementedError


def q_learning(env_step, S, A, gamma, alpha, eps, n_episodes, rng, max_steps=100):
    """Q-learning tabellare (model free, OFF-POLICY) con exploring starts.

    Aggiornamento a ogni transizione (s, a, r, s'):

        Q(s,a) <- Q(s,a) + alpha [ r + gamma * max_{a'} Q(s',a') - Q(s,a) ]

    e sulle transizioni TERMINALI (done = True) il termine di bootstrap
    sparisce: il target e' semplicemente `r`.

    Parameters
    ----------
    env_step : callable
        `env_step(s, a, rng) -> (s_next, reward, done)`, prodotto da
        `make_env_step`.  E' l'unico accesso all'ambiente consentito: P e R
        non devono comparire qui dentro.
    S : int           numero di stati
    A : int           numero di azioni
    gamma : float     sconto
    alpha : float     learning rate, costante
    eps : float       esplorazione della policy COMPORTAMENTALE
    n_episodes : int  numero di episodi
    rng : np.random.Generator
    max_steps : int   tetto sulla lunghezza di un episodio

    Returns
    -------
    Q : ndarray (S, A)   stima di Q*

    Note
    ----
    Protocollo OBBLIGATORIO, i test ci contano:
      - Q inizializzata a zero, shape (S, A);
      - EXPLORING STARTS: ogni episodio parte da uno stato estratto
        UNIFORMEMENTE con `rng.integers(S)`.  Serve a garantire che ogni
        coppia (s, a) venga visitata infinite volte, condizione di
        convergenza di Q-learning; senza, gli stati mai visitati restano a
        zero e i test falliscono;
      - l'azione da ESEGUIRE si sceglie con `epsilon_greedy(Q, s, eps, rng)`;
      - l'episodio finisce quando `done` e' True o dopo `max_steps` passi.

    Il punto delicato e' UNO SOLO: il target contiene `max_{a'} Q(s', a')`,
    non `Q(s', a')` per l'azione a' che al passo dopo verra' effettivamente
    eseguita.  Con la seconda scrittura si ottiene SARSA, che e' on-policy e
    converge a Q^{pi_eps} (il valore della policy esplorativa) invece che a
    Q*.  Con eps grande le due cose sono clamorosamente diverse, ed e' quello
    che il test off-policy misura.
    """
    # TODO
    raise NotImplementedError
