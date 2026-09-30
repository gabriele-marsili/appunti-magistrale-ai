"""d-separazione, Markov blanket e fattorizzazione in una Bayesian Network.

SOLUZIONE DI RIFERIMENTO.

Rappresentazione del grafo
--------------------------
Un DAG e' un `dict[str, list[str]]` che mappa OGNI nodo alla lista dei suoi
GENITORI (non dei figli!).  Ogni nodo deve comparire come chiave, anche se non
ha genitori:

    {"A": [], "B": ["A"], "C": ["B"]}      # A -> B -> C

Algoritmo scelto per `is_dseparated`
------------------------------------
BAYES-BALL / "Reachable" (Koller & Friedman, Algoritmo 3.1).  Si esplora
l'insieme dei nodi raggiungibili da X lungo cammini ATTIVI dato Z, tenendo
traccia non solo del nodo ma anche della DIREZIONE con cui ci si e' arrivati:

  * stato (Y, "up")   -> siamo arrivati in Y da un suo FIGLIO (freccia Y -> figlio)
  * stato (Y, "down") -> siamo arrivati in Y da un suo GENITORE (freccia genitore -> Y)

Le regole di espansione codificano esattamente le tre sottostrutture
fondamentali (fork, catena, collider):

  * (Y,"up") e Y not in Z  : la palla rimbalza sia sui genitori (catena
    genitore->Y->figlio, attiva perche' Y non e' osservato) sia sugli altri
    figli (fork figlio<-Y->figlio', attiva perche' Y non e' osservato).
  * (Y,"down") e Y not in Z: la palla prosegue verso i figli (catena
    genitore->Y->figlio, attiva).
  * (Y,"down") e Y in An(Z): la palla RISALE verso gli altri genitori
    (collider genitore->Y<-genitore', attivo se e solo se Y oppure un suo
    discendente e' osservato, cioe' se e solo se Y appartiene agli antenati
    di Z).

X e' d-separato da Y dato Z se e solo se nessun nodo di Y e' raggiungibile.

`active_paths` usa invece l'ENUMERAZIONE ESPLICITA di tutti i cammini non
orientati e applica la definizione di "cammino bloccato" nodo per nodo.  Due
implementazioni indipendenti che devono concordare: e' quello che verifica il
test di consistenza.
"""

import heapq
import itertools

import numpy as np

# ======================================================================
# CODICE GIA' FORNITO — non fa parte dell'esercizio.
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
    return list(dag[node])


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
    if node not in dag:
        raise KeyError(node)
    return sorted(c for c in dag if node in dag[c])


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
    seen = set()
    stack = list(nodes)
    while stack:
        n = stack.pop()
        if n in seen:
            continue
        if n not in dag:
            raise KeyError(n)
        seen.add(n)
        stack.extend(dag[n])
    return seen


def markov_blanket(dag, node):
    """Markov blanket di `node`: genitori, figli e co-genitori dei figli.

    E' l'insieme minimale che rende `node` condizionalmente indipendente da
    tutto il resto della rete.

    Returns
    -------
    set[str]
        NON contiene `node` stesso (che pure e' genitore dei propri figli).
    """
    mb = set(parents(dag, node))
    for c in children(dag, node):
        mb.add(c)
        mb.update(dag[c])          # co-genitori: gli altri genitori del figlio
    mb.discard(node)
    return mb


def _reachable(dag, X, Z):
    """Nodi raggiungibili da X lungo cammini attivi dato Z (Bayes-Ball).

    Vedi la docstring del modulo per la semantica degli stati "up"/"down".
    """
    Zs = set(Z)
    an_z = ancestors(dag, Zs)      # An(Z), Z incluso
    ch = {n: children(dag, n) for n in dag}

    stack = [(x, "up") for x in X]
    visited = set()
    reach = set()
    while stack:
        y, d = stack.pop()
        if (y, d) in visited:
            continue
        visited.add((y, d))
        if y not in Zs:
            reach.add(y)
        if d == "up":
            if y not in Zs:
                # catena genitore -> y -> figlio  e  fork figlio <- y -> figlio'
                for p in dag[y]:
                    stack.append((p, "up"))
                for c in ch[y]:
                    stack.append((c, "down"))
        else:  # d == "down"
            if y not in Zs:
                # catena genitore -> y -> figlio
                for c in ch[y]:
                    stack.append((c, "down"))
            if y in an_z:
                # collider genitore -> y <- genitore': attivo sse y in An(Z)
                for p in dag[y]:
                    stack.append((p, "up"))
    return reach


def is_dseparated(dag, X, Y, Z):
    """True se X e' d-separato da Y dato Z.

    Parameters
    ----------
    X, Y, Z : iterable[str]
        Insiemi (liste, set, tuple) di nodi.  Possono essere vuoti.

    Returns
    -------
    bool
        True se OGNI cammino non orientato fra un nodo di X e un nodo di Y e'
        bloccato da Z.  Implementato con Bayes-Ball: e' sufficiente che
        nessun nodo di Y sia raggiungibile da X lungo cammini attivi.
    """
    Xs, Ys = set(X), set(Y)
    for n in Xs | Ys | set(Z):
        if n not in dag:
            raise KeyError(n)
    if not Xs or not Ys:
        return True
    return not (_reachable(dag, Xs, Z) & Ys)


def _undirected_neighbors(dag):
    """Lista di adiacenza dello scheletro (grafo non orientato) del DAG."""
    nb = {n: set() for n in dag}
    for node, pas in dag.items():
        for p in pas:
            nb[node].add(p)
            nb[p].add(node)
    return {n: sorted(s) for n, s in nb.items()}


def _path_is_active(dag, path, Zs, an_z):
    """True se il cammino non orientato `path` NON e' bloccato da Z."""
    for i in range(1, len(path) - 1):
        prev, mid, nxt = path[i - 1], path[i], path[i + 1]
        left_in = prev in dag[mid]      # prev -> mid ?
        right_in = nxt in dag[mid]      # nxt  -> mid ?
        if left_in and right_in:
            # collider: attivo SOLO se mid o un suo discendente e' osservato
            if mid not in an_z:
                return False
        else:
            # catena o fork: attivo SOLO se mid non e' osservato
            if mid in Zs:
                return False
    return True


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
    for n in (x, y):
        if n not in dag:
            raise KeyError(n)
    Zs = set(Z)
    an_z = ancestors(dag, Zs)
    nb = _undirected_neighbors(dag)

    out = []
    path = [x]
    on_path = {x}

    def dfs(cur):
        if cur == y:
            if _path_is_active(dag, path, Zs, an_z):
                out.append(list(path))
            return
        for nxt in nb[cur]:
            if nxt in on_path:
                continue
            on_path.add(nxt)
            path.append(nxt)
            dfs(nxt)
            path.pop()
            on_path.discard(nxt)

    dfs(x)
    return out


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
    parti = []
    for node in topological_order(dag):
        pa = parents(dag, node)
        if pa:
            parti.append(f"P({node}|{','.join(pa)})")
        else:
            parti.append(f"P({node})")
    return "".join(parti)


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
    Xs, Ys, Zs = set(X), set(Y), set(Z)
    for name, S in (("X", Xs), ("Y", Ys), ("Z", Zs)):
        sconosciuti = S - set(dag)
        if sconosciuti:
            raise ValueError(
                f"nodi non presenti nel DAG in {name}: {sorted(sconosciuti)}"
            )
    for (na, A), (nb_, B) in itertools.combinations(
        (("X", Xs), ("Y", Ys), ("Z", Zs)), 2
    ):
        if A & B:
            raise ValueError(
                f"{na} e {nb_} non sono disgiunti: {sorted(A & B)}"
            )
    return is_dseparated(dag, Xs, Ys, Zs)
