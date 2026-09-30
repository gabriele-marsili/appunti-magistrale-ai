"""SOLUZIONE DI RIFERIMENTO — MDP tabellari: value iteration, policy iteration,
Q-learning.

Stessa API di `rl.py`.  Le funzioni non didattiche (`make_gridworld`,
`make_env_step`, `make_random_mdp`, `render_policy`) sono identiche allo
skeleton: sono copiate perche' la suite di test gira su questo modulo con
`GDL_SOL=1` e deve trovare gli stessi nomi.
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
    """Costruisce un gridworld come MDP tabellare (S, A, P, R, gamma).

    Vedi `rl.py` per la documentazione completa delle convenzioni.
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
    """Chiude (P, R, terminal) dentro un simulatore model-free."""
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
    """MDP tabellare casuale ma valido."""
    logits = rng.random((S, A, S))
    mask = rng.random((S, A, S)) < sparsity
    logits = np.where(mask, 0.0, logits + 0.05)
    dead = logits.sum(axis=2) == 0.0
    logits[dead] = 1.0
    P = logits / logits.sum(axis=2, keepdims=True)
    R = reward_scale * (2.0 * rng.random((S, A)) - 1.0)
    return P, R


def render_policy(pi, n_rows, n_cols, terminal=None):
    """Rende una policy come griglia di frecce (debug testuale)."""
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
# SOLUZIONE
# =============================================================================


def q_from_v(V, P, R, gamma):
    """Q(s, a) = R[s, a] + gamma * sum_{s'} P[s, a, s'] V[s'].

    L'unica contrazione di indice e' sull'ULTIMO asse di P (lo stato di arrivo).
    `P @ V` farebbe esattamente questo (numpy contrae l'ultimo asse del primo
    operando con l'unico asse del secondo) e restituisce shape (S, A).
    """
    V = np.asarray(V, dtype=float)
    return np.asarray(R, dtype=float) + gamma * (np.asarray(P, dtype=float) @ V)


def greedy_policy(Q):
    """Policy deterministica greedy, rappresentata one-hot: pi[s, argmax_a Q] = 1."""
    Q = np.asarray(Q, dtype=float)
    S, A = Q.shape
    pi = np.zeros((S, A))
    pi[np.arange(S), Q.argmax(axis=1)] = 1.0
    return pi


def bellman_backup(V, P, R, gamma):
    """Un passo di backup di OTTIMALITA' (Bellman optimality):

        (T* V)(s) = max_a [ R[s, a] + gamma * sum_{s'} P[s, a, s'] V[s'] ].

    Il massimo su a e' l'unica differenza rispetto al backup di ASPETTAZIONE,
    che al suo posto mette la media pesata da pi(a|s).
    """
    Q = q_from_v(V, P, R, gamma)
    return Q.max(axis=1), greedy_policy(Q)


def value_iteration(P, R, gamma, tol=1e-12, max_iter=100000):
    """Value iteration: applica T* fino a punto fisso."""
    S = P.shape[0]
    V = np.zeros(S)
    pi = greedy_policy(q_from_v(V, P, R, gamma))
    n_iter = 0
    for _ in range(max_iter):
        V_new, pi = bellman_backup(V, P, R, gamma)
        n_iter += 1
        delta = np.max(np.abs(V_new - V))
        V = V_new
        if delta < tol:
            break
    return V, pi, n_iter


def policy_evaluation(pi, P, R, gamma, tol=1e-12, max_iter=100000):
    """Iterative policy evaluation: applica T^pi fino a punto fisso.

        P_pi[s, s'] = sum_a pi[s, a] P[s, a, s']
        R_pi[s]     = sum_a pi[s, a] R[s, a]
        V <- R_pi + gamma * P_pi V
    """
    pi = np.asarray(pi, dtype=float)
    P = np.asarray(P, dtype=float)
    R = np.asarray(R, dtype=float)
    S = P.shape[0]
    # marginalizzazione sulle azioni: pesa con pi(a|s), NON con un max
    P_pi = np.einsum("sa,sat->st", pi, P)
    R_pi = np.einsum("sa,sa->s", pi, R)
    V = np.zeros(S)
    for _ in range(max_iter):
        V_new = R_pi + gamma * (P_pi @ V)
        delta = np.max(np.abs(V_new - V))
        V = V_new
        if delta < tol:
            break
    return V


def policy_iteration(P, R, gamma, tol=1e-12, max_iter=1000):
    """Policy iteration: valutazione esatta + miglioramento greedy, alternati."""
    S, A = R.shape
    pi = np.zeros((S, A))
    pi[:, 0] = 1.0  # policy iniziale: azione 0 ovunque
    V = policy_evaluation(pi, P, R, gamma, tol)
    n_iter = 0
    for _ in range(max_iter):
        n_iter += 1
        pi_new = greedy_policy(q_from_v(V, P, R, gamma))
        V = policy_evaluation(pi_new, P, R, gamma, tol)
        stabile = np.array_equal(pi_new, pi)
        pi = pi_new
        if stabile:
            break
    return V, pi, n_iter


def epsilon_greedy(Q, s, eps, rng):
    """Azione campionata dalla policy eps-greedy delle slide:

        pi(a|s) = eps/m + (1 - eps)   se a = argmax_a' Q(s, a')
                = eps/m               altrimenti          (m = numero azioni)

    cioe': con probabilita' eps si estrae UNIFORMEMENTE fra TUTTE le m azioni
    (l'azione greedy inclusa), con probabilita' 1 - eps si prende la greedy.
    """
    A = np.asarray(Q).shape[1]
    if rng.random() < eps:
        return int(rng.integers(A))
    return int(np.argmax(Q[s]))


def q_learning(env_step, S, A, gamma, alpha, eps, n_episodes, rng, max_steps=100):
    """Q-learning tabellare, off-policy, con exploring starts.

        Q(s,a) <- Q(s,a) + alpha [ r + gamma * max_a' Q(s',a') - Q(s,a) ]

    Il target usa `max_a' Q(s', a')`, NON la Q dell'azione che verra'
    effettivamente eseguita: e' esattamente questo che rende l'algoritmo
    off-policy.  Sulle transizioni terminali il termine di bootstrap sparisce.
    """
    Q = np.zeros((S, A))
    for _ in range(n_episodes):
        s = int(rng.integers(S))
        for _ in range(max_steps):
            a = epsilon_greedy(Q, s, eps, rng)
            s_next, r, done = env_step(s, a, rng)
            if done:
                target = r
            else:
                target = r + gamma * Q[s_next].max()
            Q[s, a] += alpha * (target - Q[s, a])
            if done:
                break
            s = s_next
    return Q
