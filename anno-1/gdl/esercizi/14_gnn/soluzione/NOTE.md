# Note sulla soluzione

## Il filo conduttore

GDL32 costruisce un operatore, GDL33 spiega perché applicarlo molte volte lo
rompe. L'esercizio è scritto per far incontrare le due cose nello stesso file:
`normalized_adjacency` produce `Â`, `stack_layers` la applica venti volte e
`dirichlet_energy` misura quello che resta. La frase della slide
sull'oversmoothing — *"the model cannot learn distinctive embeddings
irrespectively of the propagation length required"* — diventa una successione
di venti numeri che scende monotonamente.

La ragione sta tutta in una riga del test `(1)`: `Â u = u` con `u = D̃^{1/2}1`.
`Â` è simmetrica con spettro contenuto in `[-1, 1]` e ha `1` come autovalore
massimo, con autovettore noto in forma chiusa. Iterare `Â` è una power
iteration: tutte le componenti con `|λ| < 1` si spengono e sopravvive solo la
proiezione su `u`, cioè un segnale in cui le righe differiscono solo per il
fattore `sqrt(d̃_i)`. Su un grafo regolare significa: tutte le righe uguali.
L'oversmoothing non è un difetto dell'ottimizzazione, è quello che
quell'operatore fa per costruzione.

## L'ordine delle operazioni in `normalized_adjacency`

`A + I` prima, gradi dopo. Chi calcola `d = A.sum(1)` e poi aggiunge
l'identità ottiene `Ã[i,j]/sqrt(d_i d_j)` con i gradi sbagliati di 1: la
matrice resta simmetrica, resta plausibile, e `Â u = u` smette di valere per
qualsiasi `u`. Nessun controllo di forma se ne accorge, e il modello si allena
lo stesso — un po' peggio.

La normalizzazione è **simmetrica**, non per riga. `D^{-1}Ã` (la row
normalization, cioè la media aritmetica dei vicini) è una scelta legittima —
è quella di GraphSAGE-mean — ma non è simmetrica, non ha spettro reale
garantito e non è quella della slide *"Laplacian-normalized"*. Il test `(1)`
la scarta con l'asserzione sulla simmetria.

Il grado nullo va mascherato, non aggirato. `1.0 / np.sqrt(d)` con `d = 0`
produce `inf` senza sollevare eccezioni (solo un RuntimeWarning), e il
successivo `0 * inf` produce `NaN` che si propaga silenziosamente per tutta la
rete. La maschera booleana `nz = d > 0` costa una riga e chiude il problema.
Con `add_self_loops=True` il caso non esiste — ed è uno dei motivi per cui i
self-loop ci sono.

## `edge_index`: il verso è la metà dell'esercizio

La convenzione è `edge_index[0] = mittenti`, `edge_index[1] = destinatari`, e
di conseguenza il peso dell'arco `j → i` è `A_hat[i, j]`, con la riga uguale al
**destinatario**. Su un grafo non orientato `Â` è simmetrica e sbagliare non si
vede; su un grafo orientato, o appena si aggiungono pesi asimmetrici, il
modello aggrega dal vicinato sbagliato. Nel GAT l'errore si vede subito, perché
`α` è asimmetrica per costruzione: è quello che controlla il test `(7)`
confrontando `M` con `M^T`.

Il resto di `message_passing` sono tre righe: gather (`H[src]`, `H[dst]`),
scatter (`aggregate_fn`), update. Vale la pena notare che il gather produce
array di shape `(E, F)`, non `(N, F)`: le righe sono indicizzate dagli **archi**.
Chi tiene tutto in shape `(N, ·)` finisce a scrivere cicli espliciti sui nodi e
a perdere la struttura che rende evidente l'invarianza.

## Perché `gcn_as_message_passing` è una funzione a sé

Perché senza l'obbligo di *chiamare* `message_passing` si può sempre riscrivere
`Â H W` e dichiarare che sono la stessa cosa. La funzione forza a esplicitare
le tre scelte — messaggio pesato, somma, update che ignora lo stato precedente
— e in particolare a rendersi conto che nel GCN il termine `Ŵ h_v` della slide
*non* compare separatamente: è già dentro l'aggregazione grazie al self-loop,
con peso `1/d̃_v`. È la differenza con GIN, dove il contributo del nodo stesso
ha un peso `(1 + ε)` distinto proprio perché la somma non lo distinguerebbe.

Il self-loop non va contato una seconda volta dentro
`gcn_as_message_passing`: `Â` ce l'ha già sulla diagonale con peso `1/d̃_i`, e
l'`update_fn` deve quindi ignorare `h_i`. Un `update_fn` scritto come
`activation(Agg + H @ W)`, per analogia con la formula della slide che tiene
separato il termine `Ŵ h_v`, somma il nodo a se stesso due volte con pesi
diversi: il risultato ha la shape giusta, è sbagliato solo sul contributo del
nodo stesso, ed è esattamente il tipo di errore che sopravvive a un training
completo.

## Il softmax segmentato del GAT

È l'unico punto tecnicamente non banale. Serve un softmax per **gruppo di
archi** con lo stesso destinatario, e la versione stabile richiede il massimo
per gruppo:

```python
mx = np.full(n, -np.inf); np.maximum.at(mx, dst, e)
ex = np.exp(e - mx[dst])
den = np.zeros(n);        np.add.at(den, dst, ex)
alpha = ex / den[dst]
```

Il doppio indirizzamento `mx[dst]` e `den[dst]` (da `(N,)` a `(E,)`) è la parte
che si sbaglia: si calcola il massimo per nodo e poi lo si sottrae per nodo
invece che per arco. Le `.at` sono lente ma sono l'unico modo di fare scatter
con indici ripetuti in numpy puro: `mx[dst] = np.maximum(mx[dst], e)` non
funziona, perché l'assegnamento fancy-indexed con indici duplicati tiene solo
l'ultima scrittura.

L'altro errore ricorrente è mediare `H[src]` invece di `Z[src]`: i vettori che
si combinano con `α` sono le stesse proiezioni `z_j = h_j W` usate per i
punteggi, altrimenti la dimensione di uscita non torna nemmeno.

`negative_slope` esiste per una ragione: con una ReLU al posto della LeakyReLU
tutti i punteggi negativi diventerebbero 0 e collasserebbero sullo stesso
valore, cioè metà del vicinato riceverebbe lo stesso peso a prescindere. Il
test `(7)` verifica che il parametro incida davvero sul risultato — con
`identity` o `relu` sparirebbe dal calcolo.

## I numeri dell'oversmoothing

Grafo circolante su 12 nodi con offset `{1, 2}`: 4-regolare, connesso, non
bipartito (contiene triangoli). `H` gaussiano `(12, 5)`, seed `4207`,
`W = I` a ogni layer, attivazione identità. Energia di Dirichlet misurata sul
grafo **con** self-loop, cioè con `I − Â` come Laplaciano:

| profondità | 0 | 1 | 5 | 10 | 20 |
| --- | --- | --- | --- | --- | --- |
| `E(H^(l))` | 36.3996 | 2.212431 | 0.110104 | 5.910e-03 | 1.703e-05 |

Il rapporto `E_{l+1}/E_l` si stabilizza a `0.5571`, che è esattamente `λ₂²`
con `λ₂ = 0.7464` secondo autovalore di `Â`: il decadimento è geometrico con
ragione data dal gap spettrale, non c'è nulla di stocastico. La distanza
massima fra due rappresentazioni di nodo passa da `4.6184` a `0.006061`.

Con ReLU al posto dell'identità: `E_1 = 0.971959`, `E_5 = 0.032161`,
`E_20 = 4.973e-06`. L'attivazione non salva nulla, e non può: essendo
1-Lipschitz componente per componente e commutando con il riscalamento
positivo `h_i ↦ h_i/sqrt(d_i)`, vale `E(relu(H)) ≤ E(H)`. La ReLU può solo
abbassare l'energia, mai alzarla.

## La controprova che vale la pena leggere

Con `W = 3I` l'energia **non** decade: `E_1 = 19.91`, `E_5 = 6502`,
`E_20 = 2.07e+14`. Sarebbe comodo concluderne che i pesi grandi risolvono
l'oversmoothing. Non è così: la distanza massima fra le righe *normalizzate*
passa comunque da `1.9784` a `0.01328`, cioè i nodi collassano lo stesso, in
direzione, e a cambiare è solo la scala globale. L'energia di Dirichlet è una
forma quadratica e non è invariante di scala: un riscalamento la moltiplica per
`9` a ogni layer e maschera il collasso.

È il motivo per cui in letteratura si usano misure normalizzate (energia
divisa per `‖H‖²`, o la *mean average distance* fra rappresentazioni). Il test
`(11)` tiene dentro entrambe le diagnosi apposta: chi legge solo il numero
dell'energia si convince che basta far crescere la norma dei pesi, e la
condizione "con pesi che non lo impediscono" del testo dell'esercizio diventa
una scorciatoia invece che un'ipotesi.

Il legame con GDL33 è diretto. La slide *"A Dynamical Systems View on Deep
Graph Networks"* legge lo stack come discretizzazione di una ODE, e
l'oversmoothing come **dissipazione**: le soluzioni convergono a un punto fisso
e perdono memoria della condizione iniziale. Le risposte proposte — pesi
antisimmetrici (Gravina et al., ICLR 2023), formulazioni port-Hamiltoniane —
sono tutte modi di imporre alla Jacobiana autovalori a parte reale nulla,
cioè di impedire proprio il decadimento che questi venti numeri mostrano.

## Sull'equivarianza

I test `(5)` e `(6)` sono la stessa proprietà vista da due lati. `(5)` dice che
rimescolare le colonne di `edge_index` non cambia nulla: è l'invarianza
dell'aggregatore. `(6)` dice che rinumerare i nodi (`A ↦ PAP^T`, `H ↦ PH`) fa
permutare l'output allo stesso modo (`out ↦ P·out`): è l'equivarianza del layer,
e discende dalla prima. La distinzione fra le due parole conta all'orale:
il **layer** è equivariante, la lettura a livello di **grafo** (la somma finale
`y_g = W_o Σ_v h(v)` della slide sui reservoir) è invariante.

Nel test l'unico punto delicato è la rinumerazione di `edge_index`. Se
`H' = H[perm]`, il vecchio nodo `u` si trova in posizione `inv[u]` con
`inv = np.argsort(perm)`, quindi `edge_index' = inv[edge_index]`. Usare `perm`
al posto di `inv` applica la permutazione inversa: il test passerebbe comunque
per `perm` che sono involuzioni, e fallirebbe per tutte le altre — un ottimo
modo di perdere mezz'ora.

## Errori tipici, in breve

Aggiungere `I` dopo aver calcolato i gradi. Usare `D^{-1}` invece di
`D^{-1/2}·D^{-1/2}`. Applicare l'attivazione prima dell'aggregazione invece che
dopo. Invertire mittente e destinatario in `edge_index` (invisibile su grafi non
orientati con pesi simmetrici, letale sul GAT). Normalizzare i coefficienti di
attenzione su tutti gli archi invece che per vicinato. Dimenticare il fattore
`1/2` nell'energia di Dirichlet, oppure normalizzare la differenza
`h_i − h_j` invece dei singoli `h_i/sqrt(d_i)`. Restituire `K` stati invece di
`K+1` da `stack_layers`, perdendo l'ingresso e con esso il punto di partenza
della curva di energia.
