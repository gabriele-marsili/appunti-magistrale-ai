"""Suite di autovalutazione per l'esercizio MDP tabellari / RL.

    pytest test_rl.py -v              # testa il tuo skeleton
    GDL_SOL=1 pytest test_rl.py -v    # testa la soluzione di riferimento
"""

import importlib
import itertools
import os
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).parent
if os.environ.get("GDL_SOL"):
    sys.path.insert(0, str(HERE / "soluzione"))
    m = importlib.import_module("rl_sol")
else:
    sys.path.insert(0, str(HERE))
    m = importlib.import_module("rl")


# =============================================================================
# MDP di riferimento.
#
# GRID_S: gridworld 4x4 con slittamento 0.2.  Serve per tutto il model based:
#   e' asimmetrico (goal in alto a destra, trappola subito sotto) quindi
#   scambiare gli assi di P si vede, e con slip > 0 l'azione ottima e' STRETTA
#   in ogni stato non terminale (margine minimo ~0.0096 fra la prima e la
#   seconda azione), quindi confrontare due policy per uguaglianza esatta e'
#   lecito: non ci sono pareggi da rompere.
#
# GRID_D: lo stesso gridworld DETERMINISTICO (slip = 0).  Serve per il model
#   free: con transizioni e premi deterministici Q-learning a passo costante
#   e' una contrazione deterministica di modulo 1 - alpha(1 - gamma) e
#   converge a Q* fino alla precisione macchina, quindi il test non e' flaky.
# =============================================================================

GAMMA = 0.9

GRID_S = m.make_gridworld(slip=0.2)
GRID_D = m.make_gridworld(slip=0.0)

P_S, R_S, TERM_S = GRID_S["P"], GRID_S["R"], GRID_S["terminal"]
P_D, R_D, TERM_D = GRID_D["P"], GRID_D["R"], GRID_D["terminal"]

S_GRID, A_GRID = GRID_S["n_states"], GRID_S["n_actions"]

# MDP generico senza struttura di griglia e senza stati assorbenti: qui il
# tasso di convergenza di value iteration e' davvero gamma, non "gamma per la
# probabilita' di non essere ancora finiti in uno stato terminale".
_RNG_MDP = np.random.default_rng(3)
P_R, R_R = m.make_random_mdp(12, 4, _RNG_MDP)


# =============================================================================
# ORACOLI INDIPENDENTI — scritti per DEFINIZIONE, non copiando l'implementazione
# =============================================================================


def _induced_chain(pi, P, R):
    """P_pi (S,S) e R_pi (S,) per definizione, con cicli espliciti."""
    S, A = R.shape
    P_pi = np.zeros((S, S))
    R_pi = np.zeros(S)
    for s in range(S):
        for a in range(A):
            R_pi[s] += pi[s, a] * R[s, a]
            for s2 in range(S):
                P_pi[s, s2] += pi[s, a] * P[s, a, s2]
    return P_pi, R_pi


def _v_pi_esatta(pi, P, R, gamma):
    """ORACOLO: V^pi risolvendo il sistema lineare (I - gamma P_pi) V = R_pi.

    Metodo completamente diverso da quello di `policy_evaluation`: eliminazione
    di Gauss in un colpo solo invece di iterazione di punto fisso.
    """
    P_pi, R_pi = _induced_chain(pi, P, R)
    S = R_pi.shape[0]
    return np.linalg.solve(np.eye(S) - gamma * P_pi, R_pi)


def _v_star_enumerazione(P, R, gamma):
    """ORACOLO: V*(s) = max su TUTTE le A^S policy deterministiche di V^pi(s).

    Non usa nessun operatore di Bellman: enumera le policy, valuta ciascuna
    esattamente col solutore lineare, e prende il massimo componente per
    componente.  Costo A^S: usabile solo su MDP giocattolo.
    """
    S, A = R.shape
    best = np.full(S, -np.inf)
    for scelte in itertools.product(range(A), repeat=S):
        pi = np.zeros((S, A))
        pi[np.arange(S), scelte] = 1.0
        best = np.maximum(best, _v_pi_esatta(pi, P, R, gamma))
    return best


def _policy_casuale(S, A, rng):
    """Policy stocastica casuale, righe a somma 1."""
    w = rng.random((S, A)) + 0.05
    return w / w.sum(axis=1, keepdims=True)


def _pi_eps_greedy(Q, eps):
    """La policy eps-greedy delle slide, in forma di matrice (S, A)."""
    A = Q.shape[1]
    return eps / A + (1.0 - eps) * m.greedy_policy(Q)


# =============================================================================
# TEST
# =============================================================================


def test_q_from_v_oracolo_definizione():
    """ORACOLO: Q(s,a) = R[s,a] + gamma sum_{s'} P[s,a,s'] V[s'], scritto con
    tre cicli espliciti invece che con l'algebra vettoriale."""
    rng = np.random.default_rng(1)
    for nome, P, R in (("gridworld", P_S, R_S), ("mdp casuale", P_R, R_R)):
        S, A = R.shape
        V = rng.normal(size=S) * 3.0
        atteso = np.zeros((S, A))
        for s in range(S):
            for a in range(A):
                acc = 0.0
                for s2 in range(S):
                    acc += P[s, a, s2] * V[s2]
                atteso[s, a] = R[s, a] + GAMMA * acc
        ottenuto = m.q_from_v(V, P, R, GAMMA)
        assert ottenuto.shape == (S, A), (
            "q_from_v deve restituire shape (S, A) = %s, hai %s"
            % ((S, A), (ottenuto.shape,))
        )
        np.testing.assert_allclose(
            ottenuto,
            atteso,
            rtol=1e-6,
            atol=1e-9,
            err_msg=(
                "q_from_v sbagliata su '%s'. La somma su s' contrae l'ULTIMO "
                "asse di P (P @ V, oppure einsum('sat,t->sa')). Se hai la "
                "shape giusta ma i numeri sbagliati, stai contraendo il primo "
                "asse: P[s',a,s] invece di P[s,a,s']." % nome
            ),
        )


def test_greedy_policy_e_bellman_backup_coerenti():
    """greedy_policy deve essere one-hot sull'argmax; bellman_backup deve
    restituire il max di Q e la policy che lo realizza."""
    rng = np.random.default_rng(2)
    Q = rng.normal(size=(7, 4))
    pi = m.greedy_policy(Q)
    assert pi.shape == Q.shape, "greedy_policy deve restituire shape (S, A)"
    np.testing.assert_allclose(
        pi.sum(axis=1),
        np.ones(7),
        rtol=1e-6,
        atol=1e-9,
        err_msg="ogni riga di una policy e' una distribuzione su A: deve sommare a 1",
    )
    assert set(np.unique(pi)) <= {0.0, 1.0}, (
        "greedy_policy deve restituire una matrice ONE-HOT di 0 e 1, non una "
        "distribuzione morbida (niente softmax)"
    )
    np.testing.assert_allclose(
        (pi * Q).sum(axis=1),
        Q.max(axis=1),
        rtol=1e-6,
        atol=1e-9,
        err_msg=(
            "la policy greedy deve selezionare in ogni stato l'azione di Q "
            "MASSIMA: se ti torna il minimo hai un argmin, se ti torna la "
            "media stai restituendo una policy uniforme."
        ),
    )

    V = rng.normal(size=S_GRID)
    V_new, pi_b = m.bellman_backup(V, P_S, R_S, GAMMA)
    Q_ref = m.q_from_v(V, P_S, R_S, GAMMA)
    assert V_new.shape == (S_GRID,), (
        "bellman_backup deve restituire V di shape (S,), hai %s" % (V_new.shape,)
    )
    np.testing.assert_allclose(
        V_new,
        Q_ref.max(axis=1),
        rtol=1e-6,
        atol=1e-9,
        err_msg=(
            "(T*V)(s) = max_a Q(s,a): il backup di OTTIMALITA' massimizza sulle "
            "azioni. Se hai messo una media pesata da una policy hai scritto il "
            "backup di ASPETTAZIONE, che e' l'altra equazione."
        ),
    )
    np.testing.assert_allclose(
        pi_b,
        m.greedy_policy(Q_ref),
        rtol=1e-6,
        atol=1e-9,
        err_msg="la policy restituita da bellman_backup deve essere greedy rispetto a Q(V)",
    )


def test_policy_evaluation_oracolo_sistema_lineare():
    """ORACOLO CENTRALE. V^pi calcolata iterando Bellman atteso deve coincidere
    con la soluzione ESATTA del sistema lineare (I - gamma P_pi) V = R_pi,
    ottenuta con np.linalg.solve. Due algoritmi completamente diversi per lo
    stesso punto fisso."""
    rng = np.random.default_rng(4)
    Q_fittizia = rng.normal(size=(S_GRID, A_GRID))

    casi = []
    for gamma in (0.5, 0.9, 0.95):
        casi.append(("gridworld / uniforme", np.full((S_GRID, A_GRID), 0.25), P_S, R_S, gamma))
        det = np.zeros((S_GRID, A_GRID))
        det[:, 0] = 1.0
        casi.append(("gridworld / sempre N", det, P_S, R_S, gamma))
        casi.append(
            ("gridworld / eps-greedy 0.3", _pi_eps_greedy(Q_fittizia, 0.3), P_S, R_S, gamma)
        )
        casi.append(
            ("mdp casuale / stocastica", _policy_casuale(12, 4, rng), P_R, R_R, gamma)
        )

    for nome, pi, P, R, gamma in casi:
        atteso = _v_pi_esatta(pi, P, R, gamma)
        ottenuto = m.policy_evaluation(pi, P, R, gamma, 1e-12)
        assert ottenuto.shape == atteso.shape, (
            "policy_evaluation deve restituire V di shape (S,) = %s, hai %s"
            % (atteso.shape, (ottenuto.shape,))
        )
        np.testing.assert_allclose(
            ottenuto,
            atteso,
            rtol=1e-6,
            atol=1e-8,
            err_msg=(
                "V^pi iterativa != soluzione esatta di (I - gamma P_pi) V = R_pi "
                "sul caso '%s' con gamma = %.2f.\n"
                "Sospetti, in ordine: (1) hai messo un max_a al posto della "
                "media sum_a pi(a|s), cioe' hai scritto il backup di ottimalita' "
                "invece di quello di aspettazione; (2) hai marginalizzato P "
                "sull'asse sbagliato: P_pi[s,s'] = sum_a pi[s,a] P[s,a,s']; "
                "(3) hai ignorato pi in R_pi, che vale sum_a pi[s,a] R[s,a]."
                % (nome, gamma)
            ),
        )


def test_bellman_ottimalita_e_una_contrazione_gamma():
    """PROPRIETA' MATEMATICA: T* e' gamma-contrattivo in norma infinito,
    ||T*V1 - T*V2||_inf <= gamma ||V1 - V2||_inf, su ogni coppia V1, V2.
    E' l'unica ragione per cui value iteration converge."""
    rng = np.random.default_rng(5)
    for nome, P, R in (("gridworld", P_S, R_S), ("mdp casuale", P_R, R_R)):
        S = R.shape[0]
        for gamma in (0.0, 0.3, 0.9, 0.99):
            rapporto_max = 0.0
            for _ in range(120):
                V1 = rng.normal(size=S) * rng.choice([0.1, 1.0, 20.0])
                V2 = rng.normal(size=S) * rng.choice([0.1, 1.0, 20.0])
                T1, _ = m.bellman_backup(V1, P, R, gamma)
                T2, _ = m.bellman_backup(V2, P, R, gamma)
                num = np.max(np.abs(T1 - T2))
                den = np.max(np.abs(V1 - V2))
                assert num <= gamma * den + 1e-9, (
                    "violata la contrazione su '%s' con gamma = %.2f: "
                    "||T*V1 - T*V2||_inf = %.6f > gamma * ||V1 - V2||_inf = "
                    "%.6f. Se il rapporto e' ~1 invece che ~gamma, hai "
                    "dimenticato di moltiplicare per gamma il termine di "
                    "bootstrap; se e' > 1, stai sommando i valori futuri invece "
                    "di mediarli con P." % (nome, gamma, num, gamma * den)
                )
                rapporto_max = max(rapporto_max, num / den)
            if gamma >= 0.3:
                # il vincolo non deve essere soddisfatto per il motivo sbagliato
                # (p.es. T*V costante): il rapporto deve avvicinarsi a gamma
                assert rapporto_max > 0.5 * gamma, (
                    "su '%s' con gamma = %.2f il rapporto di contrazione "
                    "massimo osservato e' %.4f, troppo piccolo: T*V non "
                    "dipende abbastanza da V. Stai ignorando il termine "
                    "gamma * P @ V?" % (nome, gamma, rapporto_max)
                )


def test_value_iteration_e_punto_fisso_di_bellman():
    """La V restituita deve annullare il residuo di ottimalita' ||T*V - V||_inf,
    e la policy restituita deve essere greedy rispetto a quella V."""
    for nome, P, R, gamma in (
        ("gridworld slip 0.2", P_S, R_S, GAMMA),
        ("gridworld deterministico", P_D, R_D, GAMMA),
        ("mdp casuale", P_R, R_R, 0.95),
    ):
        V, pi, n_iter = m.value_iteration(P, R, gamma, 1e-12, 100000)
        assert V.shape == (R.shape[0],), "value_iteration deve restituire V di shape (S,)"
        assert pi.shape == R.shape, "value_iteration deve restituire pi di shape (S, A)"
        assert isinstance(n_iter, (int, np.integer)) and n_iter >= 1, (
            "n_iter deve essere il numero di backup eseguiti, un intero >= 1; hai %r"
            % (n_iter,)
        )
        TV, pi_greedy = m.bellman_backup(V, P, R, gamma)
        residuo = np.max(np.abs(TV - V))
        assert residuo < 1e-10, (
            "residuo di ottimalita' ||T*V - V||_inf = %.3e su '%s': con tol = "
            "1e-12 la V restituita deve essere un punto fisso di T*. Se il "
            "residuo e' dell'ordine di tol o piu' grande, stai uscendo dal "
            "ciclo troppo presto (criterio d'arresto sul valore invece che "
            "sull'incremento?)." % (residuo, nome)
        )
        np.testing.assert_allclose(
            pi,
            pi_greedy,
            rtol=1e-6,
            atol=1e-9,
            err_msg=(
                "su '%s' la policy restituita da value_iteration non e' greedy "
                "rispetto alla V restituita: vanno estratte dalla STESSA "
                "iterazione." % nome
            ),
        )


def test_value_iteration_oracolo_enumerazione_delle_policy():
    """ORACOLO: V*(s) = max su tutte le A^S policy deterministiche di V^pi(s),
    con ogni V^pi risolta esattamente col sistema lineare. Nessun operatore di
    Bellman coinvolto nell'oracolo."""
    rng = np.random.default_rng(6)
    for gamma in (0.5, 0.9):
        P, R = m.make_random_mdp(5, 3, rng)  # 3^5 = 243 policy deterministiche
        atteso = _v_star_enumerazione(P, R, gamma)
        V, pi, _ = m.value_iteration(P, R, gamma, 1e-12, 100000)
        np.testing.assert_allclose(
            V,
            atteso,
            rtol=1e-6,
            atol=1e-8,
            err_msg=(
                "con gamma = %.2f la V* di value_iteration non coincide con il "
                "massimo di V^pi su tutte le policy deterministiche. Cause "
                "tipiche: max sull'asse sbagliato di Q, oppure hai fermato "
                "l'iterazione prima della convergenza." % gamma
            ),
        )
        # la policy restituita deve essere una di quelle che REALIZZANO V*
        np.testing.assert_allclose(
            m.policy_evaluation(pi, P, R, gamma, 1e-12),
            atteso,
            rtol=1e-6,
            atol=1e-8,
            err_msg=(
                "la policy restituita da value_iteration, valutata, non da' V*: "
                "una V* corretta con la policy greedy sbagliata significa che "
                "stai prendendo l'argmax di una Q diversa da quella usata per "
                "il max."
            ),
        )


def test_value_iteration_e_policy_iteration_stessa_soluzione():
    """I due algoritmi model based devono arrivare alla STESSA V* e alla STESSA
    policy ottima, ma policy iteration in molte meno iterazioni."""
    for nome, P, R, gamma, rapporto_atteso in (
        ("gridworld slip 0.2", P_S, R_S, GAMMA, 5),
        ("mdp casuale", P_R, R_R, 0.95, 20),
    ):
        V_vi, pi_vi, n_vi = m.value_iteration(P, R, gamma, 1e-12, 100000)
        V_pi, pi_pi, n_pi = m.policy_iteration(P, R, gamma)
        np.testing.assert_allclose(
            V_pi,
            V_vi,
            rtol=1e-6,
            atol=1e-8,
            err_msg=(
                "su '%s' policy iteration e value iteration convergono a due V "
                "diverse. C'e' un solo V*: se differiscono, uno dei due cicli "
                "sta usando l'equazione di Bellman sbagliata (attesa al posto "
                "di ottima, o viceversa)." % nome
            ),
        )
        assert np.array_equal(pi_pi, pi_vi), (
            "su '%s' le due policy ottime differiscono negli stati %s. In "
            "questo MDP l'azione ottima e' STRETTAMENTE migliore delle altre in "
            "ogni stato non terminale, quindi non e' un problema di pareggi."
            % (nome, np.flatnonzero(pi_pi.argmax(1) != pi_vi.argmax(1)).tolist())
        )
        assert isinstance(n_pi, (int, np.integer)) and n_pi >= 1, (
            "policy_iteration deve restituire n_iter intero >= 1, hai %r" % (n_pi,)
        )
        assert n_pi * rapporto_atteso < n_vi, (
            "su '%s' policy iteration ha usato %d round e value iteration %d "
            "backup: ci si aspetta almeno un fattore %d di differenza. Policy "
            "iteration converge in un numero FINITO e piccolo di round perche' "
            "ogni round risolve esattamente V^pi e le policy deterministiche "
            "sono finite; value iteration si avvicina solo geometricamente, con "
            "ragione gamma. Se i due numeri si somigliano, molto probabilmente "
            "dentro policy_iteration stai facendo un solo backup invece di una "
            "valutazione completa." % (nome, n_pi, n_vi, rapporto_atteso)
        )


def test_valore_ottimo_domina_ogni_altra_policy():
    """PROPRIETA' MATEMATICA: V*(s) >= V^pi(s) per OGNI stato e OGNI policy.
    Verificato su policy stocastiche casuali, che l'algoritmo non ha mai visto."""
    rng = np.random.default_rng(7)
    for nome, P, R, gamma in (
        ("gridworld slip 0.2", P_S, R_S, GAMMA),
        ("mdp casuale", P_R, R_R, 0.95),
    ):
        S, A = R.shape
        V_star, pi_star, _ = m.policy_iteration(P, R, gamma)
        for _ in range(25):
            pi = _policy_casuale(S, A, rng)
            V_pi = m.policy_evaluation(pi, P, R, gamma, 1e-12)
            peggio = float(np.min(V_star - V_pi))
            assert peggio >= -1e-8, (
                "su '%s' esiste una policy casuale che batte V* di %.3e in "
                "almeno uno stato: allora quella che chiami V* non e' ottima. "
                "Se il divario e' grande, il ciclo di policy iteration si ferma "
                "troppo presto (confronta le POLICY, non le V)." % (nome, -peggio)
            )
        # e V* deve essere esattamente il valore della policy che restituisce
        np.testing.assert_allclose(
            m.policy_evaluation(pi_star, P, R, gamma, 1e-12),
            V_star,
            rtol=1e-6,
            atol=1e-8,
            err_msg=(
                "su '%s' la V restituita da policy_iteration non e' la V^pi "
                "della policy restituita: devono essere l'ultima valutazione e "
                "l'ultima policy, coerenti fra loro." % nome
            ),
        )


def test_epsilon_greedy_distribuzione():
    """La eps-greedy delle slide vale eps/m + (1-eps) sull'azione greedy e
    eps/m sulle altre. Tre regimi: eps=0 deterministica, eps=1 uniforme,
    eps=0.5 la formula completa (che e' quella che smaschera la versione
    'con probabilita' eps prendi un'azione NON greedy')."""
    Q = np.array(
        [
            [0.10, 0.90, 0.30, 0.20],
            [0.50, 0.40, 0.40, 0.40],
            [-1.00, -2.00, -0.50, -3.00],
        ]
    )
    S, A = Q.shape
    greedy = Q.argmax(axis=1)

    # eps = 0: deterministica, sempre l'argmax
    rng = np.random.default_rng(101)
    for s in range(S):
        for _ in range(50):
            a = m.epsilon_greedy(Q, s, 0.0, rng)
            assert int(a) == int(greedy[s]), (
                "con eps = 0 epsilon_greedy deve restituire SEMPRE "
                "argmax_a Q[%d, a] = %d, hai ottenuto %r" % (s, greedy[s], a)
            )

    # eps = 1 e eps = 0.5: distribuzione empirica.
    # N = 20000 estrazioni per stato: la deviazione standard di una frequenza
    # e' <= sqrt(0.25 * 0.75 / 20000) = 0.0031, quindi atol = 0.02 e' oltre 6
    # deviazioni standard: il test non e' flaky ma vede una differenza di
    # 0.125 (che e' quella fra la formula giusta e quella sbagliata).
    N = 20000
    for eps in (1.0, 0.5):
        rng = np.random.default_rng(2024)
        conteggi = np.zeros((S, A))
        for s in range(S):
            for _ in range(N):
                conteggi[s, m.epsilon_greedy(Q, s, eps, rng)] += 1
        freq = conteggi / N
        atteso = eps / A + (1.0 - eps) * m.greedy_policy(Q)
        assert np.max(np.abs(freq - atteso)) < 0.02, (
            "con eps = %.2f la distribuzione empirica delle azioni\n%s\n"
            "non corrisponde a quella delle slide\n%s\n"
            "Nota: con probabilita' eps si estrae UNIFORMEMENTE fra TUTTE le "
            "azioni, l'azione greedy compresa, quindi P(greedy) = eps/m + "
            "(1 - eps) = %.4f e non 1 - eps = %.4f. Con eps = 1 la "
            "distribuzione deve essere uniforme, non 'uniforme sulle non "
            "greedy'."
            % (eps, np.round(freq, 4), np.round(atteso, 4), eps / A + 1 - eps, 1 - eps)
        )


def test_q_learning_converge_a_q_star():
    """Model free: senza mai vedere P ne' R, Q-learning deve ricostruire Q*."""
    gamma = GAMMA
    V_star, _, _ = m.value_iteration(P_D, R_D, gamma, 1e-12, 100000)
    Q_star = m.q_from_v(V_star, P_D, R_D, gamma)

    env_step = m.make_env_step(P_D, R_D, TERM_D)
    rng = np.random.default_rng(0)
    Q = m.q_learning(env_step, S_GRID, A_GRID, gamma, 0.5, 0.3, 4000, rng, max_steps=50)

    assert Q.shape == (S_GRID, A_GRID), (
        "q_learning deve restituire Q di shape (S, A) = %s, hai %s"
        % ((S_GRID, A_GRID), (Q.shape,))
    )
    err = np.max(np.abs(Q - Q_star))
    # Tolleranza motivata: l'ambiente e' deterministico e alpha e' costante,
    # quindi ogni aggiornamento di (s,a) contrae l'errore di un fattore
    # 1 - alpha(1 - gamma) = 0.95; con 4000 episodi ed exploring starts ogni
    # coppia riceve migliaia di aggiornamenti e l'errore scende sotto la
    # precisione macchina.  1e-3 e' gia' larghissimo.
    assert err < 1e-3, (
        "||Q - Q*||_inf = %.4e, troppo grande. In un ambiente deterministico "
        "con alpha costante Q-learning converge esattamente. Controlla: il "
        "target e' r + gamma * max_a' Q[s', a'] (e solo r se done); "
        "l'aggiornamento e' Q[s,a] += alpha * (target - Q[s,a]), non "
        "Q[s,a] = alpha * target; gli exploring starts servono a coprire tutte "
        "le coppie (s, a), senza di loro alcune restano a zero.\n"
        "Errore per stato: %s" % (err, np.round(np.abs(Q - Q_star).max(axis=1), 4))
    )
    np.testing.assert_allclose(
        Q[TERM_D],
        0.0,
        rtol=1e-6,
        atol=1e-6,
        err_msg=(
            "negli stati terminali (assorbenti a premio nullo) Q*(s, a) = 0 per "
            "ogni a: se ti viene diverso da zero stai facendo bootstrap anche "
            "sulle transizioni con done = True."
        ),
    )


def test_q_learning_e_off_policy():
    """IL PUNTO CONCETTUALE. Con una policy comportamentale quasi casuale
    (eps = 0.9) Q-learning converge lo stesso a Q*, perche' il target usa
    max_a' Q(s', a') e non l'azione che verra' eseguita. Un algoritmo
    on-policy (SARSA) converge invece a Q^{pi_eps}, che qui e' un'altra cosa:
    con la trappola accanto al goal, esplorare costa parecchio."""
    gamma = GAMMA
    V_star, _, _ = m.value_iteration(P_D, R_D, gamma, 1e-12, 100000)
    Q_star = m.q_from_v(V_star, P_D, R_D, gamma)

    eps = 0.9
    pi_eps = _pi_eps_greedy(Q_star, eps)
    Q_on_policy = m.q_from_v(m.policy_evaluation(pi_eps, P_D, R_D, gamma, 1e-12), P_D, R_D, gamma)
    divario = np.max(np.abs(Q_star - Q_on_policy))
    assert divario > 0.5, (
        "il test presuppone che Q* e Q^{pi_eps} siano ben distinti, qui "
        "differiscono solo di %.4f: rifare i conti." % divario
    )

    env_step = m.make_env_step(P_D, R_D, TERM_D)
    rng = np.random.default_rng(1)
    Q = m.q_learning(env_step, S_GRID, A_GRID, gamma, 0.5, eps, 4000, rng, max_steps=50)

    err_star = np.max(np.abs(Q - Q_star))
    err_on = np.max(np.abs(Q - Q_on_policy))
    assert err_star < 1e-3, (
        "con eps = %.1f (comportamento quasi uniforme) Q-learning deve "
        "convergere lo stesso a Q*: e' off-policy. ||Q - Q*||_inf = %.4e.\n"
        "Se invece ||Q - Q^{pi_eps}||_inf = %.4e e' piccolo, hai implementato "
        "SARSA: nel target hai messo Q[s', a'] con a' campionata dalla policy "
        "eps-greedy invece di max_a' Q[s', a']. SARSA impara il valore della "
        "policy che sta ESEGUENDO (esplorazione compresa, trappola compresa), "
        "Q-learning impara il valore della policy greedy che NON sta "
        "eseguendo." % (eps, err_star, err_on)
    )
    assert err_on > 0.5 * divario, (
        "Q deve essere vicina a Q* e LONTANA da Q^{pi_eps}: qui dista %.4f da "
        "quest'ultima mentre le due target distano %.4f fra loro. Se sei "
        "vicino a entrambe, il divario costruito nel test non regge; se sei "
        "vicino solo a Q^{pi_eps}, e' SARSA." % (err_on, divario)
    )


def test_caso_limite_gamma_zero_e_stati_terminali():
    """CASO LIMITE: con gamma = 0 il futuro non conta, quindi V* = max_a R[s,a]
    ESATTAMENTE, la policy ottima e' miope e ogni stato terminale vale 0."""
    for nome, P, R, terminal in (
        ("gridworld deterministico", P_D, R_D, TERM_D),
        ("gridworld slip 0.2", P_S, R_S, TERM_S),
    ):
        V, pi, n_iter = m.value_iteration(P, R, 0.0, 1e-12, 100000)
        np.testing.assert_allclose(
            V,
            R.max(axis=1),
            rtol=1e-6,
            atol=1e-9,
            err_msg=(
                "con gamma = 0 su '%s' deve valere V*(s) = max_a R[s,a] "
                "esattamente: il termine gamma * P @ V si annulla e resta solo "
                "il premio immediato. Se non torna, gamma non moltiplica il "
                "termine di bootstrap ma qualcos'altro." % nome
            ),
        )
        np.testing.assert_allclose(
            pi,
            m.greedy_policy(R),
            rtol=1e-6,
            atol=1e-9,
            err_msg=(
                "con gamma = 0 la policy ottima e' MIOPE: argmax_a R[s,a], "
                "senza guardare dove si finisce."
            ),
        )
        assert n_iter <= 3, (
            "con gamma = 0 il punto fisso si raggiunge al primo backup e il "
            "secondo lo conferma: n_iter dovrebbe essere 2, hai %d. Se e' "
            "grande, il criterio d'arresto non guarda ||V_{k+1} - V_k||_inf."
            % n_iter
        )
        np.testing.assert_allclose(
            m.q_from_v(V, P, R, 0.0),
            R,
            rtol=1e-6,
            atol=1e-9,
            err_msg="con gamma = 0 vale Q(s,a) = R[s,a] identicamente",
        )

        # stati terminali: assorbenti a premio nullo => V* = 0 per ogni gamma
        for gamma in (0.0, 0.5, GAMMA, 0.99):
            V_g, _, _ = m.value_iteration(P, R, gamma, 1e-12, 100000)
            np.testing.assert_allclose(
                V_g[terminal],
                0.0,
                rtol=1e-6,
                atol=1e-9,
                err_msg=(
                    "gli stati terminali sono assorbenti con R = 0, quindi "
                    "V*(s) = 0 per ogni gamma (qui %.2f); hai %s. Un valore "
                    "non nullo li' significa che stai incassando il premio "
                    "d'ingresso una seconda volta." % (gamma, V_g[terminal])
                ),
            )
            uniforme = np.full(R.shape, 1.0 / R.shape[1])
            V_u = m.policy_evaluation(uniforme, P, R, gamma, 1e-12)
            np.testing.assert_allclose(
                V_u[terminal],
                0.0,
                rtol=1e-6,
                atol=1e-9,
                err_msg="anche V^pi vale 0 negli stati terminali, per ogni pi e ogni gamma",
            )
