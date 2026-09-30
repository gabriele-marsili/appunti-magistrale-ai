# 14 — Message passing, GCN, GAT e oversmoothing

## Lezione di riferimento

`Lessons/GDL32 graph fundamentals.pdf` — *Deep Learning for Graphs:
Fundamentals*: la convoluzione su grafo nel dominio spaziale, lo schema
message passing ("Neighborhood Aggregation & Layering", "What is inside of the
Box?", "The graph convolutional layer"), la graph attention di Veličković.

`Lessons/GDL33 graph advanced.pdf` — *Deep Learning for Graphs: Advanced*: la
sezione *Information Propagation in Graphs*, cioè under-reaching,
over-squashing e **over-smoothing**, e la lettura della propagazione come
sistema dinamico dissipativo.

I due deck vanno letti in sequenza perché raccontano una cosa sola: GDL32
costruisce l'operatore, GDL33 spiega perché applicarlo molte volte lo rompe.
La slide di GDL32 chiama il cuore del layer *"perm. invariant function"* e
quella di GDL33 definisce l'oversmoothing come l'incapacità del modello di
"learn distinctive embeddings" a prescindere da quanto lontano debba
propagare. Questo esercizio rende entrambe le frasi verificabili con
`assert`.

## Il problema

Su una griglia regolare la convoluzione ha un senso perché il vicinato ha
sempre la stessa forma e i pixel hanno un ordinamento totale. Su un grafo non
è così: il vicinato `N(v)` ha cardinalità variabile ed è un **insieme**, senza
un primo e un ultimo elemento. Il modello della slide *"What is inside of the
Box?"* è

    h_v^l = σ( W^l AGG({ h_i^{l-1} : i ∈ N(v) }), Ŵ^l h_v^{l-1} )

e tutto il resto della lezione consiste nello scegliere `AGG`.

## Cosa devi implementare

| funzione | cosa fa |
| --- | --- |
| `normalized_adjacency(A, add_self_loops=True)` | `Â = D̃^{-1/2}(A+I)D̃^{-1/2}`, con la convenzione sul grado nullo |
| `gcn_layer(H, A_hat, W, activation)` | un layer GCN, forma matriciale |
| `message_passing(H, edge_index, message_fn, aggregate_fn, update_fn)` | lo schema generico message / aggregate / update |
| `gcn_as_message_passing(H, A_hat, W, activation)` | lo stesso GCN, ma espresso *chiamando* `message_passing` |
| `gat_attention(H, edge_index, W, a, negative_slope=0.2)` | i coefficienti `α_ij` di GAT, uno per arco |
| `gat_layer(H, edge_index, W, a, negative_slope=0.2, activation=identity)` | il layer di attenzione a testa singola |
| `dirichlet_energy(H, A)` | l'energia di Dirichlet del segnale sul grafo |
| `stack_layers(H, A_hat, Ws, activation)` | K layer GCN, restituisce tutti gli stati |

## Specifica matematica

**Rappresentazione.** Un grafo su `N` nodi è dato o dalla matrice di adiacenza
`A` di shape `(N, N)`, simmetrica e a diagonale nulla, o da un `edge_index` di
shape `(2, E)`. La convenzione, non negoziabile perché i test la verificano:

    edge_index[0, e] = MITTENTE j        edge_index[1, e] = DESTINATARIO i
    A[i, j] != 0     ⟺  esiste l'arco j → i   (l'indice di RIGA riceve)

Le feature stanno in `H` di shape `(N, F)`, una riga per nodo. Su un grafo non
orientato `edge_index` contiene entrambe le direzioni di ogni arco.

**Convoluzione normalizzata (Kipf & Welling).**

    Ã = A + I          d̃_i = Σ_j Ã[i,j]          Â[i,j] = Ã[i,j] / sqrt(d̃_i d̃_j)
    H^(l) = σ( Â H^(l-1) W^(l) )

La forma matriciale nasconde la definizione locale, che è quella da avere in
testa:

    h'_i = σ( Σ_{j ∈ N(i) ∪ {i}} 1/sqrt(d̃_i d̃_j) · (h_j W) )

Il self-loop va aggiunto **prima** di calcolare i gradi. La normalizzazione è
simmetrica (`D^{-1/2} · D^{-1/2}`), non per riga (`D^{-1}`): la prima
mantiene `Â` simmetrica e con spettro in `[-1, 1]`, la seconda no.

Il grado nullo va gestito. Con i self-loop non può capitare, perché `d̃_i ≥ 1`
sempre. Senza self-loop un nodo isolato ha grado 0 e `1/sqrt(0)` è `inf`: la
convenzione richiesta è `d^{-1/2} = 0`, che lascia riga e colonna nulle senza
produrre `NaN`.

**Message passing.** Lo schema generale della slide *"A Message-Passing view on
Deep Graph Networks"*:

    m_{j→i} = message(h_j, h_i)                    un messaggio per ARCO
    a_i     = AGG({ m_{j→i} : j ∈ N(i) })          riduzione per NODO
    h'_i    = update(h_i, a_i)

`AGG` deve essere invariante a permutazione (somma, media, massimo). Il GCN si
ottiene con `message = Â[i,j] · (h_j W)`, `AGG = somma`, `update = σ(a_i)`.

**Graph attention (Veličković et al., ICLR 2018).**

    z_i        = h_i W
    e_ij       = LeakyReLU( a^T [ z_i ‖ z_j ] )         i riceve, j manda
    α_ij       = softmax_{j ∈ N(i)}  e_ij
    h'_i       = σ( Σ_{j ∈ N(i)} α_ij z_j )

La prima metà di `a` (le prime `F_out` componenti) moltiplica `z_i`, la seconda
metà `z_j`. Il softmax è **per vicinato**: si normalizza sugli archi che
condividono lo stesso destinatario, quindi `Σ_{e: dst(e)=i} α_e = 1` per ogni
nodo con almeno un arco entrante. Non è un softmax globale sugli `E` archi.
I self-loop, se li vuoi nel vicinato, devono già essere in `edge_index`.

Due casi limite valgono in forma chiusa: con `a = 0` tutti i punteggi sono
`LeakyReLU(0) = 0`, i pesi diventano uniformi e il GAT degenera nella media dei
vicini; su un grafo **regolare**, con `a = 0`, GAT e GCN sono lo stesso
operatore, perché `1/sqrt(d̃ d̃) = 1/d̃ = 1/|N(i)|`.

**Energia di Dirichlet.**

    E(H) = 1/2 Σ_{i,j} A[i,j] ‖ h_i/sqrt(d_i) − h_j/sqrt(d_j) ‖²
         = tr( H^T (I − D^{-1/2} A D^{-1/2}) H )

È la forma quadratica del Laplaciano normalizzato: non negativa, e nulla
esattamente sui segnali armonici `h_i ∝ sqrt(d_i)` (quindi sui segnali costanti,
se il grafo è regolare). Il fattore `1/2` c'è perché su un grafo non orientato
ogni arco compare due volte nella doppia sommatoria. Se la propagazione usa i
self-loop, l'energia va misurata sul grafo **con** i self-loop: i termini `i = j`
valgono 0, ma i gradi cambiano e con essi la normalizzazione.

Con `A` uguale al grafo con self-loop si ha `I − D̃^{-1/2}ÃD̃^{-1/2} = I − Â`, e
quindi, decomponendo `H` sugli autovettori di `Â` con autovalori `λ_k`,

    E(Â H) = Σ_k λ_k² (1 − λ_k) c_k   ≤   Σ_k (1 − λ_k) c_k = E(H)

perché `|λ_k| ≤ 1`. Il decadimento non è un fenomeno empirico: è un teorema, e
il test `(11)` lo verifica come tale.

## Perché questo esercizio

Scopre tre confusioni, in ordine di gravità.

1. **Che la profondità su un grafo funzioni come la profondità su un'immagine.**
   In una CNN aggiungere layer allarga il campo recettivo e basta. In un DGN
   con `Â` aggiungere layer allarga il campo recettivo *e* applica un'altra
   volta un operatore di media, che ha `1` come autovalore massimo e contrae
   tutto il resto: dopo abbastanza layer i nodi hanno la stessa
   rappresentazione e il task diventa irrisolvibile. Il test `(11)` misura il
   crollo con l'energia di Dirichlet.
2. **Che l'aggregazione sia un dettaglio di implementazione.** Il vicinato è un
   insieme; qualunque cosa dipenda dall'ordine dei vicini definisce un modello
   diverso su un grafo isomorfo. I test `(5)` e `(6)` separano le due facce
   della stessa medaglia: invarianza rispetto all'ordine degli archi ed
   equivarianza rispetto alla rinumerazione dei nodi.
3. **Che GAT e GCN siano meccanismi diversi.** Sono lo stesso schema con un
   coefficiente diverso sull'arco: fisso e simmetrico (`1/sqrt(d̃_i d̃_j)`) nel
   GCN, appreso e asimmetrico (`α_ij ≠ α_ji`) nel GAT. Il test `(8)` fa
   collassare il secondo nel primo mettendo `a = 0` su un grafo regolare.

## Vincoli

Solo `numpy` e la standard library. Niente `torch`, `torch_geometric`, `scipy`,
`sklearn`, `matplotlib`. Ogni sorgente di casualità passa dal `rng`
(`numpy.random.Generator`) ricevuto come argomento: mai `np.random.seed`, mai
il modulo `random`, mai `time`.

Non toccare `identity`, `relu`, `leaky_relu`, `edge_index_from_adjacency`,
`adjacency_from_edge_index`, `aggregate_sum`, `aggregate_mean`,
`aggregate_max`, `erdos_renyi_graph`, `circulant_graph`: sono già forniti e i
test li usano.

`gcn_as_message_passing` deve **chiamare** `message_passing`: riscrivere
`Â H W` non dimostra niente.

Le convenzioni su `edge_index` (riga 0 mittenti, riga 1 destinatari), sulla
normalizzazione per vicinato dei coefficienti di attenzione e sul contenuto di
`stack_layers` (K+1 stati, il primo è l'ingresso) sono verificate dai test.

## Come autovalutarti

```bash
cd /home/claude/gdl/esercizi/14_gnn
python3 -m pytest test_gnn.py -v
```

Tutti i test devono passare. Ogni asserzione ha un messaggio che indica quale
errore concettuale l'ha fatta fallire; leggilo prima di correggere a caso.

## Tempo stimato

2 ore e mezza. `normalized_adjacency`, `gcn_layer` e `stack_layers` sono poche
righe. Il tempo vero se ne va in tre punti: capire il verso di `edge_index` e
non invertire mittente e destinatario nel peso `Â[i, j]`; scrivere il softmax
**segmentato** del GAT (massimo e somma per destinatario, non globali) con
`np.add.at` / `np.maximum.at`; e convincersi che il decadimento dell'energia è
una conseguenza dello spettro di `Â`, non un artefatto del seed.

## Domande d'orale collegate

1. Perché la convoluzione su griglia non si trasferisce direttamente su un
   grafo? Quali due assunzioni saltano?
2. Che cosa deve avere di speciale la funzione di aggregazione di un layer
   convoluzionale su grafo, e che proprietà ne discende per il layer intero?
3. Che cos'è l'oversmoothing, perché nasce dallo spettro di `Â` e come si
   distingue da under-reaching e over-squashing?
4. In che senso GCN, GraphSAGE e GAT sono lo stesso modello? Che cosa cambia
   esattamente da uno all'altro?
5. Perché nel GAT il softmax è calcolato sul vicinato e non su tutti i nodi?
   Che differenza fa rispetto a un graph transformer con attenzione globale?
6. Perché `Â = D̃^{-1/2}(A+I)D̃^{-1/2}` e non `D^{-1}A`? A cosa servono i
   self-loop e a cosa serve la normalizzazione simmetrica?
