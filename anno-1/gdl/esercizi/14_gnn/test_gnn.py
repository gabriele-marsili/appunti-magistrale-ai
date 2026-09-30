"""Test di autovalutazione - GDL32/GDL33 "Deep Learning for Graphs".

Esecuzione:
    pytest test_gnn.py -v                # sullo skeleton
    GDL_SOL=1 pytest test_gnn.py -v      # sulla soluzione di riferimento
"""

import os, sys, pathlib, importlib

HERE = pathlib.Path(__file__).parent
if os.environ.get("GDL_SOL"):
    sys.path.insert(0, str(HERE / "soluzione"))
    m = importlib.import_module("gnn_sol")
else:
    sys.path.insert(0, str(HERE))
    m = importlib.import_module("gnn")

import numpy as np
from numpy.testing import assert_allclose


# ---------------------------------------------------------------------------
# helper locali ai test (non fanno parte dell'API da implementare)
# ---------------------------------------------------------------------------

def _liste_di_adiacenza(A, con_self_loop):
    """Liste di vicini costruite a mano da A, ignorando qualsiasi funzione del
    modulo. Servono agli oracoli: se le ricavassi da ``normalized_adjacency``
    l'oracolo non sarebbe indipendente."""
    n = A.shape[0]
    vicini = []
    for i in range(n):
        v = [j for j in range(n) if j != i and A[i, j] != 0.0]
        if con_self_loop:
            v.append(i)
        vicini.append(sorted(v))
    return vicini


def _distanza_massima_fra_nodi(X):
    """Massima distanza euclidea fra due righe: quanto sono distinguibili i nodi."""
    D = np.linalg.norm(X[:, None, :] - X[None, :, :], axis=-1)
    return float(D.max())


def _distanza_massima_direzionale(X):
    """Come sopra ma dopo aver normalizzato ogni riga: misura la collassabilita'
    delle DIREZIONI, insensibile a un riscalamento globale."""
    norme = np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-300)
    return _distanza_massima_fra_nodi(X / norme)


def _matrice_dei_coefficienti(alpha, edge_index, n):
    """Da (E,) coefficienti per arco a (N, N) con M[i, j] = alpha_{i<-j}."""
    M = np.zeros((n, n))
    M[np.asarray(edge_index[1]), np.asarray(edge_index[0])] = alpha
    return M


# ---------------------------------------------------------------------------
# 1. normalized_adjacency: definizione e autovettore di grado
# ---------------------------------------------------------------------------

def test_normalized_adjacency_definizione_e_autovettore_di_grado():
    """A^ = D~^{-1/2}(A+I)D~^{-1/2} entrata per entrata, simmetrica, con
    autovalori in [-1, 1] e con D~^{1/2}1 come autovettore di autovalore 1.
    Quest'ultimo fatto NON e' un dettaglio: e' la ragione strutturale per cui
    impilare layer GCN porta all'oversmoothing."""
    rng = np.random.default_rng(3201)
    n = 10
    A = m.erdos_renyi_graph(n, 0.4, rng)
    assert A.sum() > 0, "il grafo di prova e' degenere, cambia seed"

    A_hat = m.normalized_adjacency(A, add_self_loops=True)
    assert A_hat.shape == (n, n), \
        f"normalized_adjacency deve restituire (N, N), ottenuto {A_hat.shape}"

    d_til = A.sum(axis=1) + 1.0  # il +1 e' il self-loop
    atteso = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            a_ij = A[i, j] + (1.0 if i == j else 0.0)
            if a_ij != 0.0:
                atteso[i, j] = a_ij / np.sqrt(d_til[i] * d_til[j])
    assert_allclose(A_hat, atteso, rtol=1e-6, atol=1e-9,
                    err_msg="A^[i,j] deve valere 1/sqrt(d~_i d~_j) sugli archi del grafo "
                            "CON self-loop e 0 altrove; controlla di aver aggiunto I PRIMA "
                            "di calcolare i gradi, non dopo")

    assert_allclose(A_hat, A_hat.T, rtol=1e-6, atol=1e-9,
                    err_msg="la normalizzazione simmetrica deve preservare la simmetria; "
                            "se hai diviso solo per le righe (D^{-1} A~, row-normalization) "
                            "il risultato non e' simmetrico")

    assert np.all(np.diag(A_hat) > 0.0), \
        "con add_self_loops=True la diagonale di A^ non puo' essere nulla: vale 1/d~_i"

    lam = np.linalg.eigvalsh(A_hat)
    assert lam.max() <= 1.0 + 1e-9 and lam.min() >= -1.0 - 1e-9, \
        f"gli autovalori di A^ devono stare in [-1, 1], ottenuto [{lam.min():.4f}, {lam.max():.4f}]"

    u = np.sqrt(d_til)
    assert_allclose(A_hat @ u, u, rtol=1e-6, atol=1e-9,
                    err_msg="D~^{1/2}1 deve essere autovettore di A^ con autovalore 1: "
                            "e' la direzione verso cui la propagazione fa collassare tutto")


# ---------------------------------------------------------------------------
# 2. normalized_adjacency: grado 0 e divisione per zero (caso limite)
# ---------------------------------------------------------------------------

def test_normalized_adjacency_grado_zero_e_grafo_senza_archi():
    """Senza self-loop un nodo isolato ha grado 0 e 1/sqrt(0) e' inf: la
    convenzione e' d^{-1/2} = 0. Con self-loop il problema non esiste, e sul
    grafo completamente privo di archi A^ e' esattamente l'identita'."""
    n = 5
    A = np.zeros((n, n))
    A[0, 1] = A[1, 0] = 1.0
    A[1, 2] = A[2, 1] = 1.0
    A[2, 3] = A[3, 2] = 1.0
    # il nodo 4 e' isolato

    senza = m.normalized_adjacency(A, add_self_loops=False)
    assert np.all(np.isfinite(senza)), \
        "grado 0 senza self-loop: 1/sqrt(0) = inf e poi 0*inf = NaN. Vanno mascherati " \
        "i nodi di grado nullo, non calcolata la radice e basta"
    assert_allclose(senza[4], np.zeros(n), rtol=1e-6, atol=1e-9,
                    err_msg="la riga di un nodo isolato deve essere nulla")
    assert_allclose(senza[:, 4], np.zeros(n), rtol=1e-6, atol=1e-9,
                    err_msg="la colonna di un nodo isolato deve essere nulla")
    assert_allclose(np.diag(senza), np.zeros(n), rtol=1e-6, atol=1e-9,
                    err_msg="con add_self_loops=False la diagonale resta nulla: "
                            "l'argomento viene ignorato")

    con = m.normalized_adjacency(A, add_self_loops=True)
    assert np.all(np.isfinite(con)), "con i self-loop nessun grado puo' essere nullo"
    assert_allclose(con[4], np.eye(n)[4], rtol=1e-6, atol=1e-9,
                    err_msg="un nodo isolato con self-loop ha d~ = 1: la sua riga di A^ e' e_4")

    vuoto = m.normalized_adjacency(np.zeros((n, n)), add_self_loops=True)
    assert_allclose(vuoto, np.eye(n), rtol=1e-6, atol=1e-9,
                    err_msg="grafo senza archi + self-loop: A~ = I, d~ = 1, quindi A^ = I")


# ---------------------------------------------------------------------------
# 3. ORACOLO INDIPENDENTE: il layer GCN sommato a mano sui vicini
# ---------------------------------------------------------------------------

def test_gcn_layer_contro_somma_esplicita_sui_vicini():
    """Il test centrale. La forma matriciale activation(A^ H W) deve coincidere
    con la definizione locale

        h'_i = activation( sum_{j in N(i) U {i}} 1/sqrt(d~_i d~_j) * (h_j W) )

    calcolata con un ciclo Python sulle liste di adiacenza, con i gradi contati
    a mano e senza mai toccare A^."""
    rng = np.random.default_rng(3203)
    n, f_in, f_out = 9, 4, 3
    A = m.erdos_renyi_graph(n, 0.35, rng)
    H = rng.normal(size=(n, f_in))
    W = rng.normal(size=(f_in, f_out))

    A_hat = m.normalized_adjacency(A, add_self_loops=True)
    ottenuto = m.gcn_layer(H, A_hat, W, m.relu)
    assert ottenuto.shape == (n, f_out), \
        f"gcn_layer deve restituire (N, F_out) = ({n}, {f_out}), ottenuto {ottenuto.shape}"

    vicini = _liste_di_adiacenza(A, con_self_loop=True)
    d_til = np.array([len(v) for v in vicini], dtype=float)

    atteso = np.zeros((n, f_out))
    for i in range(n):
        acc = np.zeros(f_in)
        for j in vicini[i]:
            acc = acc + H[j] / np.sqrt(d_til[i] * d_til[j])
        atteso[i] = np.maximum(acc @ W, 0.0)

    assert_allclose(ottenuto, atteso, rtol=1e-6, atol=1e-9,
                    err_msg="la forma matriciale non coincide con la somma esplicita sui vicini. "
                            "Cause tipiche: aver dimenticato il self-loop nella somma, aver usato "
                            "1/d~_i invece di 1/sqrt(d~_i d~_j), oppure aver applicato "
                            "l'attivazione prima dell'aggregazione invece che dopo")

    # senza attivazione il layer e' lineare in H: controprova su un secondo caso
    atteso_lin = np.zeros((n, f_out))
    for i in range(n):
        for j in vicini[i]:
            atteso_lin[i] += (H[j] @ W) / np.sqrt(d_til[i] * d_til[j])
    assert_allclose(m.gcn_layer(H, A_hat, W, m.identity), atteso_lin, rtol=1e-6, atol=1e-9,
                    err_msg="con activation=identity il layer e' A^ H W e nient'altro")


# ---------------------------------------------------------------------------
# 4. Il GCN come caso particolare del message passing
# ---------------------------------------------------------------------------

def test_gcn_e_un_caso_particolare_di_message_passing():
    """Lo schema message/aggregate/update e' generale, il GCN e' una sua
    istanza: messaggio = vicino trasformato e pesato per A^[i,j], aggregazione
    = somma, update = attivazione. I due percorsi devono dare lo STESSO array."""
    rng = np.random.default_rng(3204)
    n, f_in, f_out = 11, 5, 4
    A = m.erdos_renyi_graph(n, 0.3, rng)
    H = rng.normal(size=(n, f_in))
    W = rng.normal(size=(f_in, f_out))
    A_hat = m.normalized_adjacency(A, add_self_loops=True)

    diretto = m.gcn_layer(H, A_hat, W, m.relu)
    via_mp = m.gcn_as_message_passing(H, A_hat, W, m.relu)
    assert via_mp.shape == diretto.shape, \
        f"shape diverse: message passing {via_mp.shape}, gcn_layer {diretto.shape}"
    assert_allclose(via_mp, diretto, rtol=1e-6, atol=1e-9,
                    err_msg="il GCN riscritto come message passing non coincide con la forma "
                            "matriciale. Controlla il verso del peso: sull'arco j -> i il "
                            "coefficiente e' A^[i, j], cioe' riga = DESTINATARIO")

    # message_passing usato da solo, contro un oracolo a cicli: media dei vicini
    edge_index = m.edge_index_from_adjacency(A, add_self_loops=False)
    media = m.message_passing(
        H, edge_index,
        lambda H_src, H_dst, ei: H_src,
        m.aggregate_mean,
        lambda H_prev, Agg: Agg,
    )
    vicini = _liste_di_adiacenza(A, con_self_loop=False)
    atteso = np.zeros((n, f_in))
    for i in range(n):
        if vicini[i]:
            atteso[i] = np.mean([H[j] for j in vicini[i]], axis=0)
    assert_allclose(media, atteso, rtol=1e-6, atol=1e-9,
                    err_msg="con message_fn = identita' sul mittente e aggregazione media, "
                            "message_passing deve dare la media dei vicini. Se hai invertito "
                            "mittente e destinatario in edge_index il risultato e' un altro grafo")


# ---------------------------------------------------------------------------
# 5. L'aggregazione e' invariante all'ordine degli archi
# ---------------------------------------------------------------------------

def test_aggregazione_invariante_all_ordine_degli_archi():
    """Un vicinato e' un INSIEME, non una sequenza: non esiste un ordinamento
    canonico dei vicini di un nodo in un grafo. Rimescolando le colonne di
    edge_index il risultato non deve muoversi. Chi implementa l'aggregazione
    con una concatenazione, o accumulando in un array indicizzato dall'ordine
    di arrivo, fallisce qui."""
    rng = np.random.default_rng(3205)
    n, f_in = 12, 4
    A = m.erdos_renyi_graph(n, 0.35, rng)
    H = rng.normal(size=(n, f_in))
    edge_index = m.edge_index_from_adjacency(A, add_self_loops=True)

    perm_archi = rng.permutation(edge_index.shape[1])
    mescolato = edge_index[:, perm_archi]

    def messaggio(H_src, H_dst, ei):
        return np.tanh(H_src - 0.5 * H_dst)

    def aggiorna(H_prev, Agg):
        return 0.5 * H_prev + Agg

    for nome, agg in (("somma", m.aggregate_sum),
                      ("media", m.aggregate_mean),
                      ("massimo", m.aggregate_max)):
        a = m.message_passing(H, edge_index, messaggio, agg, aggiorna)
        b = m.message_passing(H, mescolato, messaggio, agg, aggiorna)
        assert_allclose(a, b, rtol=1e-9, atol=1e-12,
                        err_msg=f"l'aggregazione '{nome}' dipende dall'ordine degli archi: "
                                "non e' permutation invariant e il modello non e' ben definito "
                                "su un grafo")


# ---------------------------------------------------------------------------
# 6. PROPRIETA' MATEMATICA: equivarianza a permutazione dei nodi
# ---------------------------------------------------------------------------

def test_equivarianza_a_permutazione_dei_nodi():
    """Rinumerare i nodi non cambia il grafo. Se A -> PAP^T e H -> PH, allora
    l'output deve diventare P(output): equivarianza, non invarianza. Vale per
    normalized_adjacency, per il GCN, per il message passing generico e per il
    GAT, e vale per QUALSIASI valore dei pesi (e' strutturale)."""
    rng = np.random.default_rng(3206)
    n, f_in, f_out = 10, 4, 3
    A = m.erdos_renyi_graph(n, 0.4, rng)
    H = rng.normal(size=(n, f_in))
    W = rng.normal(size=(f_in, f_out))
    a_att = rng.normal(size=2 * f_out)

    perm = rng.permutation(n)
    inv = np.argsort(perm)          # il vecchio nodo u finisce in posizione inv[u]
    A_p = A[perm][:, perm]
    H_p = H[perm]

    A_hat = m.normalized_adjacency(A)
    A_hat_p = m.normalized_adjacency(A_p)
    assert_allclose(A_hat_p, A_hat[perm][:, perm], rtol=1e-6, atol=1e-9,
                    err_msg="normalized_adjacency non commuta con la permutazione dei nodi: "
                            "stai usando informazione legata all'indice e non alla topologia")

    out = m.gcn_layer(H, A_hat, W, m.relu)
    out_p = m.gcn_layer(H_p, A_hat_p, W, m.relu)
    assert_allclose(out_p, out[perm], rtol=1e-6, atol=1e-9,
                    err_msg="il GCN non e' equivariante a permutazione: rinumerando i nodi "
                            "l'output deve solo riordinarsi, non cambiare valore")

    edge_index = m.edge_index_from_adjacency(A, add_self_loops=True)
    edge_index_p = inv[edge_index]   # stessi archi, nodi rinumerati, stesso ordine

    def messaggio(H_src, H_dst, ei):
        return np.tanh(H_src - H_dst)

    def aggiorna(H_prev, Agg):
        return np.concatenate([H_prev, Agg], axis=1)

    mp = m.message_passing(H, edge_index, messaggio, m.aggregate_mean, aggiorna)
    mp_p = m.message_passing(H_p, edge_index_p, messaggio, m.aggregate_mean, aggiorna)
    assert_allclose(mp_p, mp[perm], rtol=1e-6, atol=1e-9,
                    err_msg="message_passing non e' equivariante: il risultato del nodo i "
                            "deve dipendere solo dal suo vicinato, mai dall'indice i")

    alpha = m.gat_attention(H, edge_index, W, a_att)
    alpha_p = m.gat_attention(H_p, edge_index_p, W, a_att)
    assert_allclose(alpha_p, alpha, rtol=1e-6, atol=1e-9,
                    err_msg="i coefficienti di attenzione sono attributi degli ARCHI: "
                            "rinumerando i nodi senza cambiare l'ordine degli archi devono "
                            "restare identici")

    gat = m.gat_layer(H, edge_index, W, a_att)
    gat_p = m.gat_layer(H_p, edge_index_p, W, a_att)
    assert_allclose(gat_p, gat[perm], rtol=1e-6, atol=1e-9,
                    err_msg="il GAT non e' equivariante a permutazione dei nodi")


# ---------------------------------------------------------------------------
# 7. GAT: normalizzazione per vicinato, asimmetria, ruolo di LeakyReLU
# ---------------------------------------------------------------------------

def test_gat_attention_normalizzata_per_vicinato_e_asimmetrica():
    """Il softmax del GAT e' LOCALE: si normalizza sugli archi che entrano
    nello stesso nodo, non su tutti gli archi del grafo. E il coefficiente e'
    asimmetrico (alpha_{ij} != alpha_{ji}), a differenza del peso
    1/sqrt(d~_i d~_j) del GCN che e' simmetrico per costruzione."""
    rng = np.random.default_rng(3207)
    n, f_in, f_out = 9, 4, 3
    A = m.erdos_renyi_graph(n, 0.45, rng)
    H = rng.normal(size=(n, f_in))
    W = rng.normal(size=(f_in, f_out))
    a_att = rng.normal(size=2 * f_out)
    edge_index = m.edge_index_from_adjacency(A, add_self_loops=True)
    n_archi = edge_index.shape[1]

    alpha = m.gat_attention(H, edge_index, W, a_att, negative_slope=0.2)
    assert alpha.shape == (n_archi,), \
        f"gat_attention deve dare un coefficiente per ARCO: attesa ({n_archi},), ottenuta {alpha.shape}"
    assert np.all(alpha > 0.0), "i coefficienti di un softmax sono strettamente positivi"

    somme = np.zeros(n)
    np.add.at(somme, edge_index[1], alpha)
    assert_allclose(somme, np.ones(n), rtol=1e-6, atol=1e-9,
                    err_msg="i coefficienti devono sommare a 1 SU OGNI VICINATO. Se sommano a 1 "
                            "solo globalmente hai fatto un softmax su tutti gli archi insieme")

    M = _matrice_dei_coefficienti(alpha, edge_index, n)
    assert np.abs(M - M.T).max() > 1e-3, \
        "i coefficienti del GAT sono risultati simmetrici: hai usato a^T[z_i || z_j] con le due " \
        "meta' di 'a' scambiate o identiche. L'asimmetria e' proprio cio' che distingue " \
        "l'attenzione dalla normalizzazione fissa del GCN"

    piatta = m.gat_attention(H, edge_index, W, a_att, negative_slope=0.01)
    assert not np.allclose(alpha, piatta, rtol=1e-6, atol=1e-9), \
        "cambiare negative_slope non cambia nulla: la non linearita' usata non e' una LeakyReLU " \
        "(con ReLU o identita' il parametro sparisce dal calcolo)"

    # invarianza del softmax per traslazione dei punteggi -> non un test di forma:
    # raddoppiare 'a' cambia i punteggi in modo non costante, i pesi devono muoversi
    assert not np.allclose(alpha, m.gat_attention(H, edge_index, W, 2.0 * a_att)), \
        "i coefficienti non dipendono da 'a': l'attenzione non e' appresa"


# ---------------------------------------------------------------------------
# 8. CASO LIMITE IN CHIUSO: con a = 0 il GAT e' la media dei vicini
# ---------------------------------------------------------------------------

def test_gat_con_a_nullo_degenera_nella_media_dei_vicini():
    """Con a = 0 tutti i punteggi valgono LeakyReLU(0) = 0, il softmax su ogni
    vicinato e' uniforme e il GAT collassa in un aggregatore 'mean' sui vicini
    trasformati. E' il caso limite verificabile in forma chiusa, e mostra che
    l'attenzione e' una generalizzazione della media, non un'altra cosa."""
    rng = np.random.default_rng(3208)
    n, f_in, f_out = 10, 5, 3
    A = m.erdos_renyi_graph(n, 0.4, rng)
    H = rng.normal(size=(n, f_in))
    W = rng.normal(size=(f_in, f_out))
    edge_index = m.edge_index_from_adjacency(A, add_self_loops=True)

    alpha = m.gat_attention(H, edge_index, W, np.zeros(2 * f_out))
    grado_entrante = np.zeros(n)
    np.add.at(grado_entrante, edge_index[1], 1.0)
    assert_allclose(alpha, 1.0 / grado_entrante[edge_index[1]], rtol=1e-6, atol=1e-9,
                    err_msg="con a = 0 i punteggi sono tutti uguali e il softmax per vicinato "
                            "deve dare esattamente 1/|N(i)|")

    uscita = m.gat_layer(H, edge_index, W, np.zeros(2 * f_out), activation=m.identity)
    A_loop = m.adjacency_from_edge_index(edge_index, n)
    atteso = (A_loop @ (H @ W)) / A_loop.sum(axis=1)[:, None]
    assert_allclose(uscita, atteso, rtol=1e-6, atol=1e-9,
                    err_msg="con a = 0 il layer GAT deve coincidere con la media dei vicini "
                            "(self-loop compreso) DOPO la trasformazione W. Se hai mediato H e "
                            "poi moltiplicato per W il risultato coincide solo perche' W e' "
                            "lineare; se non coincide hai aggregato i vettori sbagliati")

    # con d~ costante il GCN normalizzato coincide con la media: su un grafo
    # regolare i due modelli degenerano nello stesso operatore
    A_reg = m.circulant_graph(8, (1, 2))
    ei_reg = m.edge_index_from_adjacency(A_reg, add_self_loops=True)
    H_reg = rng.normal(size=(8, f_in))
    gat_reg = m.gat_layer(H_reg, ei_reg, W, np.zeros(2 * f_out), activation=m.identity)
    gcn_reg = m.gcn_layer(H_reg, m.normalized_adjacency(A_reg), W, m.identity)
    assert_allclose(gat_reg, gcn_reg, rtol=1e-6, atol=1e-9,
                    err_msg="su un grafo REGOLARE con a = 0, GAT e GCN sono lo stesso operatore "
                            "(1/sqrt(d~ d~) = 1/d~ = 1/|N(i)|): se non coincidono, uno dei due "
                            "sbaglia la normalizzazione")


# ---------------------------------------------------------------------------
# 9. Energia di Dirichlet contro la definizione
# ---------------------------------------------------------------------------

def test_dirichlet_energy_contro_la_definizione():
    """Oracolo: la doppia sommatoria sugli archi, a cicli. Piu' le proprieta'
    che la rendono una misura di smoothness: non negativa, e nulla esattamente
    sui segnali armonici h_i = sqrt(d_i) v (che su un grafo regolare sono i
    segnali costanti)."""
    rng = np.random.default_rng(3209)
    n, f = 9, 4
    A = m.erdos_renyi_graph(n, 0.4, rng) + np.eye(n)  # grafo con self-loop
    H = rng.normal(size=(n, f))

    d = A.sum(axis=1)
    atteso = 0.0
    for i in range(n):
        for j in range(n):
            if A[i, j] != 0.0:
                diff = H[i] / np.sqrt(d[i]) - H[j] / np.sqrt(d[j])
                atteso += 0.5 * A[i, j] * float(diff @ diff)

    ottenuto = m.dirichlet_energy(H, A)
    assert np.isscalar(ottenuto) or np.ndim(ottenuto) == 0, \
        "dirichlet_energy deve restituire uno scalare, non un array"
    assert_allclose(ottenuto, atteso, rtol=1e-6, atol=1e-9,
                    err_msg="l'energia non coincide con 1/2 sum_ij A_ij ||h_i/sqrt(d_i) - "
                            "h_j/sqrt(d_j)||^2. Errori tipici: dimenticare il fattore 1/2 "
                            "(ogni arco non orientato compare due volte in A), oppure "
                            "normalizzare la differenza invece dei singoli h")

    assert m.dirichlet_energy(H, A) >= -1e-12, \
        "l'energia di Dirichlet e' una forma quadratica semidefinita positiva: non puo' essere negativa"

    v = rng.normal(size=f)
    H_armonico = np.sqrt(d)[:, None] * v[None, :]
    assert abs(m.dirichlet_energy(H_armonico, A)) < 1e-9, \
        "il segnale h_i = sqrt(d_i) v e' l'autovettore di autovalore 1 di A^: e' il punto fisso " \
        "della propagazione e la sua energia deve essere esattamente 0"

    A_reg = m.circulant_graph(12, (1, 2)) + np.eye(12)
    costante = np.ones((12, 1)) @ np.array([[1.0, 2.0, 3.0]])
    assert abs(m.dirichlet_energy(costante, A_reg)) < 1e-9, \
        "su un grafo regolare un segnale costante ha energia nulla per definizione"


# ---------------------------------------------------------------------------
# 10. stack_layers: tutti gli stati, nell'ordine giusto
# ---------------------------------------------------------------------------

def test_stack_layers_restituisce_tutti_gli_stati():
    """K+1 stati: l'ingresso e poi uno per layer. Serve a poter misurare
    l'energia in funzione della profondita', che e' il punto dell'esercizio."""
    rng = np.random.default_rng(3210)
    n, f = 8, 3
    A = m.erdos_renyi_graph(n, 0.4, rng)
    A_hat = m.normalized_adjacency(A)
    H = rng.normal(size=(n, f))
    Ws = [rng.normal(size=(f, f)) * 0.5 for _ in range(4)]

    stati = m.stack_layers(H, A_hat, Ws, m.relu)
    assert isinstance(stati, (list, tuple)), \
        f"stack_layers deve restituire una lista di stati, ottenuto {type(stati)}"
    assert len(stati) == len(Ws) + 1, \
        f"servono K+1 = {len(Ws) + 1} stati (l'ingresso piu' uno per layer), ottenuti {len(stati)}"
    assert_allclose(stati[0], H, rtol=1e-6, atol=1e-9,
                    err_msg="stati[0] deve essere l'INGRESSO non trasformato: senza di lui non si "
                            "puo' misurare l'energia a profondita' 0")

    for k, W in enumerate(Ws):
        assert_allclose(stati[k + 1], m.gcn_layer(stati[k], A_hat, W, m.relu),
                        rtol=1e-6, atol=1e-9,
                        err_msg=f"stati[{k + 1}] non e' gcn_layer(stati[{k}], A^, Ws[{k}], act): "
                                "controlla che i pesi siano usati in ordine e uno per layer")


# ---------------------------------------------------------------------------
# 11. OVERSMOOTHING: l'energia decade e i nodi diventano indistinguibili
# ---------------------------------------------------------------------------

def test_oversmoothing_energia_decade_e_i_nodi_convergono():
    """Con pesi che non lo impediscono (qui W = I) uno stack di GCN e'
    l'iterazione di A^, e A^ e' un operatore di media: l'energia di Dirichlet
    decade in modo MONOTONO verso 0 e le rappresentazioni dei nodi collassano
    l'una sull'altra. Con lo stesso grafo e pesi di norma grande l'energia non
    decade piu' -- ma i nodi collassano lo stesso in direzione, il che dice che
    la sola energia non basta a diagnosticare l'oversmoothing."""
    rng = np.random.default_rng(4207)
    n, f, K = 12, 5, 20
    A = m.circulant_graph(n, (1, 2))         # 4-regolare, connesso, non bipartito
    A_loop = A + np.eye(n)                   # il grafo su cui A^ media davvero
    A_hat = m.normalized_adjacency(A, add_self_loops=True)
    H = rng.normal(size=(n, f))

    stati = m.stack_layers(H, A_hat, [np.eye(f) for _ in range(K)], m.identity)
    E = np.array([m.dirichlet_energy(S, A_loop) for S in stati])

    assert np.all(E[1:] < E[:-1]), \
        "l'energia di Dirichlet deve decrescere STRETTAMENTE a ogni layer: A^ ha tutti gli " \
        f"autovalori in [-1, 1], quindi ogni applicazione contrae le componenti non costanti. " \
        f"Energie ottenute: {np.array2string(E, precision=4)}"
    assert E[5] < 0.1 * E[1], \
        f"dopo 5 layer l'energia deve essere gia' un ordine di grandezza sotto quella del primo " \
        f"layer: E1={E[1]:.6g}, E5={E[5]:.6g}"
    assert E[20] < 1e-3 * E[1], \
        f"dopo 20 layer l'energia deve essere crollata di almeno tre ordini di grandezza: " \
        f"E1={E[1]:.6g}, E20={E[20]:.6g}"

    d0 = _distanza_massima_fra_nodi(stati[0])
    d20 = _distanza_massima_fra_nodi(stati[K])
    assert d20 < 0.01 * d0, \
        f"le rappresentazioni dei nodi devono diventare indistinguibili: la distanza massima fra " \
        f"due nodi passa da {d0:.4f} a {d20:.4f}, ci si aspetta almeno due ordini di grandezza"

    # la stessa cosa con ReLU: l'attivazione e' 1-Lipschitz, non salva nulla
    stati_relu = m.stack_layers(H, A_hat, [np.eye(f) for _ in range(K)], m.relu)
    E_relu = np.array([m.dirichlet_energy(S, A_loop) for S in stati_relu])
    assert np.all(E_relu[1:] <= E_relu[:-1] + 1e-12), \
        "con ReLU l'energia deve restare non crescente: |relu(a) - relu(b)| <= |a - b|, " \
        "quindi l'attivazione non puo' aumentare l'energia"
    assert E_relu[K] < 1e-3 * E_relu[1], \
        "la ReLU rallenta ma non impedisce l'oversmoothing"

    # controprova: pesi di norma grande fanno esplodere l'energia, ma i nodi
    # collassano lo stesso in direzione
    stati_grandi = m.stack_layers(H, A_hat, [3.0 * np.eye(f) for _ in range(K)], m.identity)
    E_grandi = np.array([m.dirichlet_energy(S, A_loop) for S in stati_grandi])
    assert E_grandi[K] > E_grandi[1], \
        "con W = 3I l'energia NON deve decadere: e' una forma quadratica, non e' invariante di " \
        "scala, e un riscalamento la moltiplica per 9 a ogni layer"
    assert _distanza_massima_direzionale(stati_grandi[K]) < 0.1 * _distanza_massima_direzionale(stati_grandi[0]), \
        "anche con pesi grandi le DIREZIONI dei nodi collassano: l'oversmoothing e' avvenuto lo " \
        "stesso e l'energia non lo ha visto"


# ---------------------------------------------------------------------------
# 12. CASO LIMITE: grafo senza archi e nodo isolato
# ---------------------------------------------------------------------------

def test_nodo_isolato_e_grafo_senza_archi():
    """Senza archi (ma con self-loop) A^ = I e il layer GCN degenera in una
    trasformazione lineare per nodo, indipendente dagli altri: un MLP. Un nodo
    isolato dentro un grafo piu' grande si comporta allo stesso modo, e nel
    message passing senza self-loop non riceve alcun messaggio."""
    rng = np.random.default_rng(3212)
    n, f_in, f_out = 6, 4, 3
    H = rng.normal(size=(n, f_in))
    W = rng.normal(size=(f_in, f_out))

    A_vuoto = np.zeros((n, n))
    A_hat = m.normalized_adjacency(A_vuoto, add_self_loops=True)
    assert_allclose(m.gcn_layer(H, A_hat, W, m.identity), H @ W, rtol=1e-6, atol=1e-9,
                    err_msg="senza archi A^ = I e il GCN si riduce a H W, cioe' a un layer denso "
                            "applicato a ogni nodo separatamente: nessuna informazione strutturale")

    ei_vuoto = m.edge_index_from_adjacency(A_vuoto, add_self_loops=False)
    assert ei_vuoto.shape == (2, 0), \
        f"un grafo senza archi ha edge_index di shape (2, 0), ottenuto {ei_vuoto.shape}"
    agg = m.message_passing(H, ei_vuoto,
                            lambda H_src, H_dst, ei: H_src,
                            m.aggregate_sum,
                            lambda H_prev, Agg: Agg)
    assert_allclose(agg, np.zeros((n, f_in)), rtol=1e-6, atol=1e-9,
                    err_msg="senza archi nessun nodo riceve messaggi: l'aggregato e' il vettore "
                            "nullo per tutti (non NaN, non H)")

    # nodo isolato dentro un grafo connesso altrove
    A = np.zeros((n, n))
    A[0, 1] = A[1, 0] = 1.0
    A[1, 2] = A[2, 1] = 1.0
    A[3, 4] = A[4, 3] = 1.0
    # il nodo 5 e' isolato
    A_hat2 = m.normalized_adjacency(A, add_self_loops=True)
    uscita = m.gcn_layer(H, A_hat2, W, m.identity)
    assert_allclose(uscita[5], H[5] @ W, rtol=1e-6, atol=1e-9,
                    err_msg="un nodo isolato con self-loop ha d~ = 1: la sua uscita e' esattamente "
                            "h_5 W, nessun contributo dagli altri nodi")

    ei = m.edge_index_from_adjacency(A, add_self_loops=False)
    ricevuto = m.message_passing(H, ei,
                                 lambda H_src, H_dst, ei_: H_src,
                                 m.aggregate_sum,
                                 lambda H_prev, Agg: Agg)
    assert_allclose(ricevuto[5], np.zeros(f_in), rtol=1e-6, atol=1e-9,
                    err_msg="senza self-loop il nodo isolato non riceve nulla")

    # GAT su soli self-loop: un vicinato di cardinalita' 1 -> alpha = 1 sempre
    ei_loop = m.edge_index_from_adjacency(A_vuoto, add_self_loops=True)
    a_att = rng.normal(size=2 * f_out)
    alpha = m.gat_attention(H, ei_loop, W, a_att)
    assert_allclose(alpha, np.ones(n), rtol=1e-6, atol=1e-9,
                    err_msg="il softmax su un vicinato di un solo elemento vale 1, qualunque sia "
                            "il punteggio: se ottieni valori diversi stai normalizzando su tutti "
                            "gli archi del grafo invece che per vicinato")
    assert_allclose(m.gat_layer(H, ei_loop, W, a_att, activation=m.identity), H @ W,
                    rtol=1e-6, atol=1e-9,
                    err_msg="con i soli self-loop il GAT si riduce anch'esso a H W")
