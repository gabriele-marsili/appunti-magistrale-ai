"""Soluzione di riferimento - GDL32/GDL33 "Deep Learning for Graphs".

Stessa identica API di ``gnn.py``. Ogni funzione e' commentata con il motivo
per cui e' scritta cosi' e con l'errore che eviterebbe.

Solo numpy + stdlib.
"""

from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Utilita' fornite - identiche allo skeleton.
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

        A~     = A + I           (se add_self_loops)
        d~_i   = sum_j A~[i, j]
        A^[i,j] = A~[i, j] / sqrt(d~_i d~_j)

    Il punto delicato e' il grado nullo. Con ``add_self_loops=True`` non puo'
    accadere: ogni nodo ha almeno il proprio self-loop, quindi d~_i >= 1.
    Senza self-loop un nodo isolato ha grado 0 e 1/sqrt(0) sarebbe inf: la
    convenzione e' porre d^{-1/2} = 0 su quei nodi, cosi' riga e colonna
    restano nulle e non compaiono NaN.
    """
    A = np.asarray(A, dtype=float)
    n = A.shape[0]
    A_t = A + np.eye(n) if add_self_loops else A.copy()

    d = A_t.sum(axis=1)
    inv_sqrt = np.zeros_like(d)
    nz = d > 0.0
    # La maschera e' l'unico modo pulito di evitare inf/NaN: np.sqrt(0) non
    # avvisa, ma 1/0 produce inf e 0*inf produce NaN piu' avanti.
    inv_sqrt[nz] = 1.0 / np.sqrt(d[nz])

    # D^{-1/2} A~ D^{-1/2}: scalare le righe per inv_sqrt_i e le colonne per
    # inv_sqrt_j. Il broadcasting fa esattamente questo senza costruire D.
    return A_t * inv_sqrt[:, None] * inv_sqrt[None, :]


# ---------------------------------------------------------------------------
# 2. Il layer convoluzionale
# ---------------------------------------------------------------------------


def gcn_layer(H, A_hat, W, activation):
    """Un layer GCN:  H' = activation(A^ H W).

    L'ordine delle moltiplicazioni non cambia il risultato ma cambia il costo:
    ``A_hat @ (H @ W)`` costa N*F_in*F_out + N*N*F_out, mentre
    ``(A_hat @ H) @ W`` costa N*N*F_in + N*F_in*F_out. Con F_out < F_in la
    prima e' la piu' conveniente.
    """
    H = np.asarray(H, dtype=float)
    A_hat = np.asarray(A_hat, dtype=float)
    W = np.asarray(W, dtype=float)
    return activation(A_hat @ (H @ W))


# ---------------------------------------------------------------------------
# 3. Message passing generico
# ---------------------------------------------------------------------------


def message_passing(H, edge_index, message_fn, aggregate_fn, update_fn):
    """Schema generico di message passing (GDL32, "A Message-Passing view").

        m_{j->i} = message_fn(h_j, h_i)                per ogni arco j -> i
        a_i      = aggregate_fn({m_{j->i} : j in N(i)})  aggregazione INVARIANTE
        h'_i     = update_fn(h_i, a_i)

    Tre sole righe di codice, ma la forma e' l'intero paradigma: ogni DGN
    convoluzionale della lezione (GCN, GraphSAGE, GIN, GAT) e' una scelta
    delle tre funzioni.
    """
    H = np.asarray(H, dtype=float)
    edge_index = np.asarray(edge_index, dtype=int)
    n = H.shape[0]
    src, dst = edge_index[0], edge_index[1]

    # Fase 1: un messaggio per ARCO. H[src] e H[dst] sono "gather": la riga e
    # dello stesso arco, non del nodo. Le shape sono (E, F_in), non (N, F_in).
    M = message_fn(H[src], H[dst], edge_index)

    # Fase 2: "scatter" verso i destinatari. Qui vive l'invarianza a
    # permutazione: l'aggregatore non vede l'ordine degli archi.
    Agg = aggregate_fn(M, dst, n)

    # Fase 3: combinazione con lo stato precedente del nodo destinatario.
    return update_fn(H, Agg)


def gcn_as_message_passing(H, A_hat, W, activation):
    """Lo stesso identico calcolo di ``gcn_layer``, scritto come message passing.

    Scelte:
        archi        (j, i) per ogni A^[i, j] != 0 (self-loop compresi)
        messaggio    m_{j->i} = A^[i, j] * (h_j W)
        aggregazione somma
        update       h'_i = activation(a_i), lo stato precedente NON entra
                     (e' gia' dentro grazie al self-loop)
    """
    H = np.asarray(H, dtype=float)
    A_hat = np.asarray(A_hat, dtype=float)
    W = np.asarray(W, dtype=float)

    # I self-loop non vanno aggiunti qui: sono gia' nella diagonale di A^.
    edge_index = edge_index_from_adjacency(A_hat, add_self_loops=False)

    def message_fn(H_src, H_dst, ei):
        # Peso dell'arco j -> i: A^[i, j]. L'indice di riga e' il DESTINATARIO.
        w = A_hat[ei[1], ei[0]]
        return w[:, None] * (H_src @ W)

    def update_fn(H_prev, Agg):
        return activation(Agg)

    return message_passing(H, edge_index, message_fn, aggregate_sum, update_fn)


# ---------------------------------------------------------------------------
# 4. Graph attention (GAT)
# ---------------------------------------------------------------------------


def gat_attention(H, edge_index, W, a, negative_slope=0.2):
    """Coefficienti di attenzione di GAT (Velickovic et al., ICLR 2018).

        z_i    = h_i W
        e_{ij} = LeakyReLU( a^T [z_i || z_j] )        i = destinatario, j = mittente
        alpha_{ij} = softmax_{j in N(i)} e_{ij}

    La prima meta' di ``a`` moltiplica il nodo che RICEVE, la seconda il nodo
    che MANDA: e' quello che rende l'attenzione ASIMMETRICA, a differenza del
    coefficiente 1/sqrt(d_i d_j) del GCN.

    Il softmax e' per VICINATO, non globale: si normalizza sugli archi che
    condividono lo stesso destinatario.
    """
    H = np.asarray(H, dtype=float)
    W = np.asarray(W, dtype=float)
    a = np.asarray(a, dtype=float)
    edge_index = np.asarray(edge_index, dtype=int)
    n = H.shape[0]

    Z = H @ W
    f_out = Z.shape[1]
    a_dst, a_src = a[:f_out], a[f_out:]

    src, dst = edge_index[0], edge_index[1]
    # a^T [z_i || z_j] = a_dst . z_i + a_src . z_j, senza costruire la
    # concatenazione (E, 2*F_out).
    e = leaky_relu(Z[dst] @ a_dst + Z[src] @ a_src, negative_slope)

    # Softmax segmentato, in versione stabile: massimo per destinatario.
    mx = np.full(n, -np.inf, dtype=float)
    np.maximum.at(mx, dst, e)
    ex = np.exp(e - mx[dst])
    den = np.zeros(n, dtype=float)
    np.add.at(den, dst, ex)
    return ex / den[dst]


def gat_layer(H, edge_index, W, a, negative_slope=0.2, activation=identity):
    """Un layer GAT a testa singola:  h'_i = activation( sum_j alpha_{ij} z_j )."""
    H = np.asarray(H, dtype=float)
    W = np.asarray(W, dtype=float)
    edge_index = np.asarray(edge_index, dtype=int)

    alpha = gat_attention(H, edge_index, W, a, negative_slope)
    Z = H @ W
    src, dst = edge_index[0], edge_index[1]
    # Media pesata dei vicini: gli stessi z della fase di scoring, non H.
    out = aggregate_sum(alpha[:, None] * Z[src], dst, H.shape[0])
    return activation(out)


# ---------------------------------------------------------------------------
# 5. Energia di Dirichlet e stack profondo
# ---------------------------------------------------------------------------


def dirichlet_energy(H, A):
    """Energia di Dirichlet normalizzata del segnale H sul grafo A.

        E(H) = 1/2 sum_{i,j} A[i,j] || h_i/sqrt(d_i) - h_j/sqrt(d_j) ||^2
             = tr( H^T (I - D^{-1/2} A D^{-1/2}) H )

    Misura quanto i nodi adiacenti si somigliano: 0 se e solo se il segnale e'
    "armonico" (costante su ogni componente connessa, a meno del riscalamento
    per sqrt(d)). E' la misura standard di oversmoothing.

    L'espansione del quadrato evita il ciclo sugli archi:
        E = sum_i d_i ||z_i||^2 - sum_{i,j} A[i,j] z_i . z_j,   z_i = h_i/sqrt(d_i)
    """
    H = np.asarray(H, dtype=float)
    A = np.asarray(A, dtype=float)

    d = A.sum(axis=1)
    inv_sqrt = np.zeros_like(d)
    nz = d > 0.0
    inv_sqrt[nz] = 1.0 / np.sqrt(d[nz])

    Z = H * inv_sqrt[:, None]
    termine_diag = float(np.sum(d * np.sum(Z * Z, axis=1)))
    termine_incr = float(np.sum(Z * (A @ Z)))
    return termine_diag - termine_incr


def stack_layers(H, A_hat, Ws, activation):
    """Applica ``len(Ws)`` layer GCN e restituisce TUTTI gli stati intermedi.

    Ritorna una lista di K+1 array: ``[H^(0), H^(1), ..., H^(K)]`` con
    ``H^(0) = H`` (l'ingresso) e ``H^(l) = gcn_layer(H^(l-1), A^, Ws[l-1], act)``.
    """
    stati = [np.asarray(H, dtype=float)]
    for W in Ws:
        stati.append(gcn_layer(stati[-1], A_hat, W, activation))
    return stati
