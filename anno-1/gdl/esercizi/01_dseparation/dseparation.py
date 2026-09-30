"""d-separazione, Markov blanket e fattorizzazione in una Bayesian Network.

SKELETON — implementa tu le funzioni marcate `# TODO`.

Rappresentazione del grafo
--------------------------
Un DAG e' un `dict[str, list[str]]` che mappa OGNI nodo alla lista dei suoi
GENITORI (non dei figli!).  Ogni nodo deve comparire come chiave, anche se non
ha genitori:

    {"A": [], "B": ["A"], "C": ["B"]}      # A -> B -> C

I figli non sono memorizzati da nessuna parte: vanno ricavati.

Promemoria: cammino bloccato
----------------------------
Sia r = (Y1 ... Y2) un cammino NON ORIENTATO fra Y1 e Y2.  Il cammino r e'
bloccato da Z se esiste almeno un nodo interno Yc per cui vale una di queste:

  * r contiene una catena (head-to-tail)  Yi -> Yc -> Yj   con Yc in Z
  * r contiene un fork (tail-to-tail)     Yi <- Yc -> Yj   con Yc in Z
  * r contiene un collider (head-to-head) Yi -> Yc <- Yj   con ne' Yc ne'
    alcun suo discendente in Z

X e' d-separato da Y dato Z se TUTTI i cammini non orientati fra un nodo di X
e un nodo di Y sono bloccati.
"""

import heapq
import itertools

import numpy as np

# ======================================================================
# CODICE GIA' FORNITO — non devi toccarlo, ti serve per i test.
# ======================================================================

# Catena (head-to-tail):  A -> B -> C
CHAIN = {"A": [], "B": ["A"], "C": ["B"]}
CHAIN_CARDS = {"A": 2, "B": 3, "C": 2}

# Collider (head-to-head) con un discendente:  X -> Z <- Y ,  Z -> W
COLLIDER = {"X": [], "Y": [], "Z": ["X", "Y"], "W": ["Z"]}
COLLIDER_CARDS = {"X": 2, "Y": 2, "Z": 3, "W": 2}

# Rete "Student" di Koller:
#   D (Difficulty) -> G,  I (Intelligence) -> G,  I -> S (SAT),  G -> L (Letter)
STUDENT = {"D": [], "I": [], "G": ["D", "I"], "S": ["I"], "L": ["G"]}
STUDENT_CARDS = {"D": 2, "I": 2, "G": 3, "S": 2, "L": 2}


def topological_order(dag):
    """Ordinamento topologico canonico (Kahn con coda a priorita' alfabetica).

    Parameters
    ----------
    dag : dict[str, list[str]]
        nodo -> lista dei genitori.

    Returns
    -------
    list[str]
        I nodi ordinati in modo che ogni nodo compaia dopo tutti i suoi
        genitori.  A parita' di vincoli si sceglie il nodo alfabeticamente
        minore, quindi l'ordine e' unico e riproducibile.

    Raises
    ------
    ValueError
        Se il grafo contiene un ciclo.
    """
    indeg = {n: len(dag[n]) for n in dag}
    ch = {n: [] for n in dag}
    for node, pas in dag.items():
        for p in pas:
            if p not in dag:
                raise ValueError(f"genitore '{p}' di '{node}' non e' un nodo del DAG")
            ch[p].append(node)

    heap = [n for n in dag if indeg[n] == 0]
    heapq.heapify(heap)
    order = []
    while heap:
        n = heapq.heappop(heap)
        order.append(n)
        for c in sorted(ch[n]):
            indeg[c] -= 1
            if indeg[c] == 0:
                heapq.heappush(heap, c)
    if len(order) != len(dag):
        raise ValueError("il grafo contiene un ciclo: non e' un DAG")
    return order


def random_cpts(dag, cards, seed=0):
    """CPT casuali ma deterministiche, una per nodo.

    Parameters
    ----------
    dag : dict[str, list[str]]
    cards : dict[str, int]
        Numero di valori discreti di ogni variabile.
    seed : int
        Seed di `np.random.default_rng`.

    Returns
    -------
    dict[str, np.ndarray]
        `cpts[node]` ha shape `(cards[p] for p in dag[node]) + (cards[node],)`,
        cioe' gli assi dei genitori NELL'ORDINE DI `dag[node]` e come ultimo
        asse la variabile stessa.  L'ultimo asse somma a 1.
    """
    rng = np.random.default_rng(seed)
    cpts = {}
    for node in sorted(dag):
        shape = tuple(cards[p] for p in dag[node]) + (cards[node],)
        # +0.1 evita CPT quasi degeneri: con probabilita' vicine a 0 la rete
        # rischierebbe di essere non "faithful" e le dipendenze diventerebbero
        # numericamente invisibili.
        tab = rng.random(shape) + 0.1
        tab /= tab.sum(axis=-1, keepdims=True)
        cpts[node] = tab
    return cpts


def enumerate_joint(dag, cards, cpts=None, seed=0):
    """Costruisce per enumerazione la tabella congiunta completa.

    Moltiplica tutte le CPT secondo la fattorizzazione della BN
    `P(V) = prod_v P(v | pa(v))`, senza approssimazioni: e' la distribuzione
    esatta rappresentata dalla rete.

    Parameters
    ----------
    dag : dict[str, list[str]]
    cards : dict[str, int]
    cpts : dict[str, np.ndarray] | None
        Se None vengono generate con `random_cpts(dag, cards, seed)`.
    seed : int

    Returns
    -------
    (joint, order) : (np.ndarray, list[str])
        `joint` ha shape `tuple(cards[n] for n in order)` e somma a 1;
        `order` e' `topological_order(dag)` e dice a quale variabile
        corrisponde ciascun asse.
    """
    order = topological_order(dag)
    if cpts is None:
        cpts = random_cpts(dag, cards, seed)
    pos = {n: i for i, n in enumerate(order)}
    shape = tuple(cards[n] for n in order)

    joint = np.ones(shape, dtype=float)
    for node in order:
        names = list(dag[node]) + [node]          # assi della CPT, in ordine
        axes = [pos[n] for n in names]            # loro posizione nel joint
        perm = sorted(range(len(axes)), key=lambda k: axes[k])
        tab = np.transpose(cpts[node], perm)      # assi in ordine crescente
        view_shape = [1] * len(order)
        for n in names:
            view_shape[pos[n]] = cards[n]
        joint = joint * tab.reshape(view_shape)   # broadcasting sul resto
    return joint, order


# ======================================================================
# FUNZIONI DA IMPLEMENTARE
# ======================================================================


def parents(dag, node):
    """Genitori di `node`.

    Returns
    -------
    list[str]
        COPIA di `dag[node]`, nell'ordine in cui e' memorizzata (chi la
        modifica non deve poter corrompere il DAG).

    Raises
    ------
    KeyError
        Se `node` non e' nel DAG.
    """
    # TODO
    raise NotImplementedError


def children(dag, node):
    """Figli di `node`, in ordine alfabetico.

    I figli non sono memorizzati: vanno ricavati scandendo le liste di
    genitori di tutti i nodi.

    Returns
    -------
    list[str]
        Nodi `c` tali che `node in dag[c]`, ordinati alfabeticamente per
        rendere il risultato deterministico.
    """
    # TODO
    raise NotImplementedError


def ancestors(dag, nodes):
    """Chiusura ancestrale di un insieme di nodi, An(nodes).

    Parameters
    ----------
    nodes : iterable[str]

    Returns
    -------
    set[str]
        Tutti i nodi da cui esiste un cammino diretto verso almeno un nodo di
        `nodes`, PIU' i nodi di `nodes` stessi.  Con `nodes` vuoto si ottiene
        l'insieme vuoto.
    """
    # TODO
    raise NotImplementedError


def markov_blanket(dag, node):
    """Markov blanket di `node`: genitori, figli e co-genitori dei figli.

    E' l'insieme minimale che rende `node` condizionalmente indipendente da
    tutto il resto della rete.

    Returns
    -------
    set[str]
        NON contiene `node` stesso (che pure e' genitore dei propri figli).
    """
    # TODO
    raise NotImplementedError


def is_dseparated(dag, X, Y, Z):
    """True se X e' d-separato da Y dato Z.

    Parameters
    ----------
    X, Y, Z : iterable[str]
        Insiemi (liste, set, tuple) di nodi.  Possono essere vuoti; con X o Y
        vuoto il risultato e' True (vacuamente separati).

    Returns
    -------
    bool
        True se OGNI cammino non orientato fra un nodo di X e un nodo di Y e'
        bloccato da Z.

    Note
    ----
    Puoi implementarlo come preferisci — Bayes-Ball (raggiungibilita' con
    stato di direzione) oppure grafo morale ancestrale — ma DOCUMENTA quale
    algoritmo hai scelto.  Attenzione a non enumerare tutti i cammini se il
    grafo cresce: sono esponenzialmente tanti.
    """
    # TODO
    raise NotImplementedError


def active_paths(dag, x, y, Z):
    """Tutti i cammini attivi (non bloccati da Z) fra i due nodi `x` e `y`.

    Serve a mostrare PERCHE' due nodi non sono d-separati: ogni cammino
    restituito e' una prova di dipendenza residua.

    Parameters
    ----------
    x, y : str
        Due nodi singoli (non insiemi).
    Z : iterable[str]
        Insieme condizionante.

    Returns
    -------
    list[list[str]]
        Ogni cammino e' la lista dei nodi attraversati, da `x` a `y` inclusi.
        I cammini sono NON ORIENTATI (si possono percorrere archi in entrambi
        i versi) e semplici (nessun nodo ripetuto).  L'ordine della lista
        esterna e' quello di una DFS che visita i vicini in ordine alfabetico.
        Se `x == y` il risultato e' `[[x]]`.
    """
    # TODO
    raise NotImplementedError


def factorization(dag):
    """Fattorizzazione della congiunta come stringa.

    Applica catena + local Markov property: `P(V) = prod_v P(v | pa(v))`.

    Returns
    -------
    str
        Un fattore per nodo, nodi in `topological_order(dag)`, genitori
        nell'ordine in cui compaiono in `dag[node]`, separati da virgola,
        senza spazi.  Esempio: `"P(A)P(B)P(C|A,B)"`.
    """
    # TODO
    raise NotImplementedError


def implies_independence(dag, X, Y, Z):
    """Alias semantico di `is_dseparated`, con validazione degli argomenti.

    Il nome ricorda la GLOBAL MARKOV PROPERTY: se il grafo d-separa X e Y dato
    Z, allora ogni distribuzione che fattorizza secondo il grafo soddisfa
    X indipendente da Y dato Z.  Il viceversa (indipendenza => d-separazione)
    vale solo sotto ipotesi di FAITHFULNESS.

    Raises
    ------
    ValueError
        Se un nodo non esiste nel DAG, oppure se X, Y, Z non sono a due a due
        disgiunti.
    """
    # TODO
    raise NotImplementedError
