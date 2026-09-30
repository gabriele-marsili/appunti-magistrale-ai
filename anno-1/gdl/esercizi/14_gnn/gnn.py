"""Esercizio GDL32/GDL33 - "Deep Learning for Graphs": message passing, GCN,
GAT e oversmoothing.

Implementa le funzioni marcate `# TODO`. Tutto il resto (attivazioni,
conversioni fra adiacenza e edge_index, aggregatori, generatori di grafi) e'
gia' fornito e non va toccato.

Solo numpy + stdlib. Ogni sorgente di casualita' passa da `rng`
(`numpy.random.Generator`): niente `np.random.seed`, niente `random`.

Convenzioni valide per tutto il file
------------------------------------
- Un grafo su N nodi e' descritto o da una matrice di adiacenza `A` di shape
  (N, N), simmetrica, con zeri sulla diagonale (i self-loop si aggiungono
  esplicitamente quando servono), o da un `edge_index` di shape (2, E).
- In `edge_index` la colonna `e` e' l'arco `edge_index[0, e] -> edge_index[1, e]`:
  la PRIMA riga sono i MITTENTI (il vicino j), la SECONDA i DESTINATARI (il
  nodo i che aggrega). Un grafo non orientato ha entrambe le direzioni.
- Le feature dei nodi stanno in `H` di shape (N, F): una riga per nodo.
- `A[i, j] != 0` significa "esiste l'arco j -> i", cioe' l'indice di RIGA e'
  il destinatario. Sulle matrici simmetriche non fa differenza, ma sui pesi
  del message passing si'.
"""

from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Utilita' fornite - NON modificare.
# ---------------------------------------------------------------------------


def identity(x):
    """Attivazione identita' (lineare)."""
    return np.asarray(x, dtype=float)


def relu(x):
    """ReLU elemento per elemento."""
    return np.maximum(np.asarray(x, dtype=float), 0.0)


def leaky_relu(x, negative_slope=0.2):
    """LeakyReLU elemento per elemento: x se x >= 0, negative_slope * x altrimenti."""
    x = np.asarray(x, dtype=float)
    return np.where(x >= 0.0, x, negative_slope * x)


def edge_index_from_adjacency(A, add_self_loops=False):
    """Da matrice di adiacenza (N, N) a ``edge_index`` (2, E).

    ``A[i, j] != 0`` genera l'arco ``j -> i``: il nodo ``i`` RICEVE dal nodo
    ``j``. Quindi ``edge_index[0]`` sono i mittenti e ``edge_index[1]`` i
    destinatari. Su grafo non orientato (A simmetrica) compaiono entrambe le
    direzioni, una per verso.

    Con ``add_self_loops=True`` la diagonale viene forzata a 1 prima
    dell'estrazione (i self-loop mancanti vengono aggiunti, quelli presenti
    restano uno solo).

    Ritorna un array di interi di shape (2, E), ordinato per destinatario e
    poi per mittente.
    """
    B = np.array(A, dtype=float, copy=True)
    if add_self_loops:
        np.fill_diagonal(B, 1.0)
    dst, src = np.nonzero(B)
    return np.stack([src.astype(int), dst.astype(int)], axis=0)


def adjacency_from_edge_index(edge_index, num_nodes):
    """Inversa di ``edge_index_from_adjacency``: (2, E) -> (N, N) binaria.

    ``A[i, j] = 1`` se e solo se esiste l'arco ``j -> i``.
    """
    A = np.zeros((num_nodes, num_nodes), dtype=float)
    src = np.asarray(edge_index[0], dtype=int)
    dst = np.asarray(edge_index[1], dtype=int)
    A[dst, src] = 1.0
    return A


def aggregate_sum(messages, dst, num_nodes):
    """Somma dei messaggi entranti, per nodo destinatario.

    messages : (E, F)   un messaggio per arco
    dst      : (E,)     indice del destinatario di ciascun arco
    Ritorna  : (N, F).  I nodi senza archi entranti ricevono il vettore nullo.
    """
    messages = np.asarray(messages, dtype=float)
    out = np.zeros((num_nodes, messages.shape[1]), dtype=float)
    np.add.at(out, np.asarray(dst, dtype=int), messages)
    return out


def aggregate_mean(messages, dst, num_nodes):
    """Media dei messaggi entranti, per nodo destinatario. (N, F).

    Un nodo senza archi entranti riceve il vettore nullo (la media di un
    insieme vuoto non esiste: la convenzione e' 0, non NaN).
    """
    messages = np.asarray(messages, dtype=float)
    dst = np.asarray(dst, dtype=int)
    tot = aggregate_sum(messages, dst, num_nodes)
    cnt = np.zeros(num_nodes, dtype=float)
    np.add.at(cnt, dst, 1.0)
    cnt[cnt == 0.0] = 1.0
    return tot / cnt[:, None]


def aggregate_max(messages, dst, num_nodes):
    """Massimo componente per componente dei messaggi entranti. (N, F).

    Un nodo senza archi entranti riceve il vettore nullo.
    """
    messages = np.asarray(messages, dtype=float)
    dst = np.asarray(dst, dtype=int)
    out = np.full((num_nodes, messages.shape[1]), -np.inf, dtype=float)
    np.maximum.at(out, dst, messages)
    visto = np.zeros(num_nodes, dtype=bool)
    visto[dst] = True
    out[~visto] = 0.0
    return out


def erdos_renyi_graph(n, p, rng):
    """Grafo non orientato Erdos-Renyi G(n, p), senza self-loop. (n, n) 0/1."""
    U = rng.random((n, n))
    A = np.triu((U < p).astype(float), 1)
    return A + A.T


def circulant_graph(n, offsets):
    """Grafo circolante su n nodi: i e' collegato a i +/- k per ogni k in offsets.

    E' REGOLARE (tutti i nodi hanno lo stesso grado) e connesso se 1 in offsets.
    Con ``offsets=(1, 2)`` il grado e' 4 e il grafo contiene triangoli (quindi
    non e' bipartito). Nessun self-loop.
    """
    A = np.zeros((n, n), dtype=float)
    for k in offsets:
        for i in range(n):
            j = (i + k) % n
            if j != i:
                A[i, j] = 1.0
                A[j, i] = 1.0
    return A


# ---------------------------------------------------------------------------
# 1. Normalizzazione dell'adiacenza
# ---------------------------------------------------------------------------


def normalized_adjacency(A, add_self_loops=True):
    """Adiacenza normalizzata simmetricamente (Kipf & Welling).

        A~      = A + I           (solo se add_self_loops)
        d~_i    = sum_j A~[i, j]
        A^[i,j] = A~[i, j] / sqrt(d~_i d~_j)

    Parametri
    ---------
    A : (N, N) adiacenza simmetrica, tipicamente 0/1 e con diagonale nulla
    add_self_loops : bool. Se True si somma l'identita' PRIMA di calcolare i
        gradi: e' l'ordine che conta, non il gesto.

    Ritorna
    -------
    (N, N) simmetrica.

    Attenzione al grado nullo. Con ``add_self_loops=True`` non puo' capitare
    (ogni nodo ha almeno se stesso, d~_i >= 1). Senza self-loop un nodo isolato
    ha grado 0 e ``1/sqrt(0)`` e' ``inf``: la convenzione richiesta e' porre
    ``d^{-1/2} = 0`` su quei nodi, cosi' riga e colonna restano nulle e il
    risultato resta finito. Nessun ``NaN``, nessun ``inf``.
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 2. Il layer convoluzionale
# ---------------------------------------------------------------------------


def gcn_layer(H, A_hat, W, activation):
    """Un layer GCN:  H' = activation(A^ H W).

    Parametri
    ---------
    H : (N, F_in)          feature dei nodi in ingresso
    A_hat : (N, N)         adiacenza normalizzata, gia' con i self-loop
    W : (F_in, F_out)      pesi del layer
    activation : callable applicata elemento per elemento all'uscita

    Ritorna
    -------
    (N, F_out)

    La forma matriciale nasconde la definizione locale, che e' quella da avere
    in testa e che il test confronta esplicitamente:

        h'_i = activation( sum_{j in N(i) U {i}} 1/sqrt(d~_i d~_j) * (h_j W) )

    L'attivazione sta FUORI dall'aggregazione: prima si media, poi si schiaccia.
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 3. Message passing generico
# ---------------------------------------------------------------------------


def message_passing(H, edge_index, message_fn, aggregate_fn, update_fn):
    """Schema generico di message passing (GDL32, "A Message-Passing view on
    Deep Graph Networks").

        m_{j->i} = message_fn(h_j, h_i)                 per ogni arco j -> i
        a_i      = aggregate_fn({m_{j->i} : j in N(i)})  aggregazione INVARIANTE
        h'_i     = update_fn(h_i, a_i)

    Parametri
    ---------
    H : (N, F_in)
    edge_index : (2, E) interi. Riga 0 = mittenti j, riga 1 = destinatari i.
    message_fn : callable ``(H_src, H_dst, edge_index) -> (E, F_msg)``
        Riceve gia' allineate per ARCO le feature del mittente
        ``H_src = H[edge_index[0]]`` e del destinatario
        ``H_dst = H[edge_index[1]]``, entrambe di shape (E, F_in), piu'
        ``edge_index`` stesso per chi ha bisogno degli indici (per esempio per
        pesare il messaggio con un coefficiente che dipende dall'arco).
    aggregate_fn : callable ``(messages, dst, num_nodes) -> (N, F_msg)``
        Una delle ``aggregate_*`` fornite, o qualunque riduzione
        PERMUTATION INVARIANT rispetto all'ordine degli archi.
    update_fn : callable ``(H, aggregated) -> (N, F_out)``
        Combina lo stato precedente del nodo con quanto ha ricevuto.

    Ritorna
    -------
    (N, F_out), quello che restituisce ``update_fn``.

    L'invarianza dell'aggregazione non e' un dettaglio implementativo: un
    vicinato e' un INSIEME e in un grafo generico non esiste un ordinamento
    canonico dei vicini di un nodo (la slide "The graph convolutional layer" la
    chiama "perm. invariant function"). Da qui discende l'equivarianza a
    permutazione dell'intero layer.
    """
    # TODO
    raise NotImplementedError


def gcn_as_message_passing(H, A_hat, W, activation):
    """Lo stesso identico calcolo di ``gcn_layer``, ottenuto pero' CHIAMANDO
    ``message_passing``.

    Serve a rendere concreta l'affermazione della lezione: il GCN e' un'istanza
    dello schema message/aggregate/update, non un modello a parte. Le tre
    scelte da fare sono

        archi        (j, i) per ogni A^[i, j] != 0, self-loop COMPRESI
                     (sono gia' dentro A^, non vanno aggiunti una seconda volta)
        messaggio    m_{j->i} = A^[i, j] * (h_j W)
        aggregazione somma
        update       h'_i = activation(a_i)   -- lo stato precedente non entra
                     separatamente, ci pensa il self-loop

    Parametri e ritorno identici a ``gcn_layer``. Il risultato deve coincidere
    con ``gcn_layer(H, A_hat, W, activation)`` entro la tolleranza numerica.
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 4. Graph attention (GAT)
# ---------------------------------------------------------------------------


def gat_attention(H, edge_index, W, a, negative_slope=0.2):
    """Coefficienti di attenzione di GAT (Velickovic et al., ICLR 2018).

        z_i        = h_i W
        e_{ij}     = LeakyReLU( a^T [z_i || z_j] )
        alpha_{ij} = softmax_{j in N(i)} e_{ij}

    dove ``i`` e' il nodo che RICEVE e ``j`` quello che MANDA, e ``||`` e' la
    concatenazione. La prima meta' di ``a`` (le prime F_out componenti)
    moltiplica ``z_i``, la seconda meta' moltiplica ``z_j``: e' l'ordine del
    paper e i test lo verificano.

    Parametri
    ---------
    H : (N, F_in)
    edge_index : (2, E). I self-loop, se li vuoi nel vicinato, devono essere
        gia' presenti fra gli archi: questa funzione non li aggiunge.
    W : (F_in, F_out)
    a : (2 * F_out,) vettore di attenzione
    negative_slope : float, pendenza della LeakyReLU sui valori negativi

    Ritorna
    -------
    (E,) un coefficiente per ARCO, non per nodo.

    Il softmax e' per VICINATO: si normalizza sugli archi che condividono lo
    stesso DESTINATARIO, quindi ``sum_{e : dst(e) = i} alpha_e = 1`` per ogni
    nodo i con almeno un arco entrante. Non e' un softmax globale su tutti gli
    archi del grafo. Serve la solita versione stabile (sottrazione del massimo),
    ma il massimo va preso per destinatario.

    Nota concettuale: a differenza del coefficiente 1/sqrt(d~_i d~_j) del GCN,
    che e' simmetrico e fissato dalla topologia, alpha_{ij} != alpha_{ji} ed e'
    appreso dai dati.
    """
    # TODO
    raise NotImplementedError


def gat_layer(H, edge_index, W, a, negative_slope=0.2, activation=identity):
    """Un layer GAT a testa singola.

        h'_i = activation( sum_{j in N(i)} alpha_{ij} z_j ),   z_j = h_j W

    Parametri come ``gat_attention``, piu' l'attivazione finale.

    Ritorna
    -------
    (N, F_out)

    I vettori che si mediano sono le PROIEZIONI ``z_j = h_j W``, gli stessi che
    entrano nel calcolo dei punteggi, non le feature grezze ``h_j``.
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 5. Energia di Dirichlet e stack profondo
# ---------------------------------------------------------------------------


def dirichlet_energy(H, A):
    """Energia di Dirichlet normalizzata del segnale H sul grafo A.

        E(H) = 1/2 sum_{i,j} A[i,j] || h_i/sqrt(d_i) - h_j/sqrt(d_j) ||^2

    equivalentemente ``tr( H^T (I - D^{-1/2} A D^{-1/2}) H )``, cioe' la forma
    quadratica del Laplaciano normalizzato.

    Parametri
    ---------
    H : (N, F)
    A : (N, N) simmetrica. Se la propagazione usa i self-loop, passa qui il
        grafo CON i self-loop: i termini i = j valgono 0 per definizione, ma i
        gradi cambiano e con essi la normalizzazione.

    Ritorna
    -------
    float (uno scalare, non un array).

    E' la misura standard di oversmoothing: e' non negativa, vale 0 esattamente
    quando il segnale e' armonico (h_i proporzionale a sqrt(d_i), quindi
    costante sui grafi regolari) e decresce quando i nodi adiacenti si
    assomigliano. Il fattore 1/2 c'e' perche' su un grafo non orientato ogni
    arco compare due volte nella doppia sommatoria.

    Come sempre, i nodi di grado 0 vanno trattati con d^{-1/2} = 0.
    """
    # TODO
    raise NotImplementedError


def stack_layers(H, A_hat, Ws, activation):
    """Applica ``K = len(Ws)`` layer GCN e restituisce TUTTI gli stati.

    Parametri
    ---------
    H : (N, F_0)
    A_hat : (N, N) adiacenza normalizzata, la stessa a ogni layer
    Ws : lista di K matrici, ``Ws[l]`` di shape (F_l, F_{l+1})
    activation : callable, la stessa a ogni layer

    Ritorna
    -------
    lista di K+1 array: ``[H^(0), H^(1), ..., H^(K)]`` con ``H^(0) = H``
    (l'ingresso, NON trasformato) e
    ``H^(l) = gcn_layer(H^(l-1), A_hat, Ws[l-1], activation)``.

    Restituire anche lo stato iniziale serve a poter misurare l'energia di
    Dirichlet in funzione della profondita' partendo da 0 layer.
    """
    # TODO
    raise NotImplementedError
