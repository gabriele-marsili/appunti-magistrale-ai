# Note sulla soluzione — 13_flow

## L'unica idea non ovvia: perché il coupling funziona

Tutta la costruzione di RealNVP serve a rendere simultaneamente vere due cose
che di solito sono in conflitto: la trasformazione deve essere espressiva, e il
determinante del suo Jacobiano deve costare `O(D)`.

La soluzione è spezzare `x` in due metà con una maschera binaria e far dipendere
la trasformazione della seconda metà **solo** dalla prima, che passa identica.
Nel codice questo è concentrato in una riga di `_coupling_st`:

    xm = mask * x

Le componenti da trasformare vengono azzerate prima di entrare nelle reti. È
questo azzeramento — non la struttura delle reti — che rende lo Jacobiano
triangolare a blocchi. Se lo si dimentica e si passa `x` intero, il codice gira,
il forward produce numeri, ma il blocco in alto a destra dello Jacobiano non è
più nullo e la formula `log |det J| = Σ log_scale` diventa semplicemente falsa.
Il test `test_flow_log_det_contro_jacobiano_numerico` se ne accorge subito,
mentre nessun test di invertibilità lo farebbe: una trasformazione può essere
invertibile e avere comunque un determinante diverso da quello che credi.

Il secondo punto è l'inversa. Non serve invertire `θ_A` e `θ_B`, e non serve
nemmeno conoscere `x`: siccome la metà mascherata è copiata, `mask * y` è
letteralmente uguale a `mask * x`, quindi le stesse reti valutate su `y`
producono gli *stessi identici* `log_scale` e `shift` del forward. L'inversione
si riduce a una sottrazione e una divisione. Questo è il motivo per cui i
coupling flow si addestrano: entrambe le direzioni costano una forward pass.

## Le trappole, in ordine di frequenza

**Valutare tutti i log-det nello stesso punto.** In `flow_log_det` lo stato e
l'accumulatore devono avanzare insieme:

    total += log_det_layer_i(z);  z = forward_layer_i(z)

Scrivere invece `sum(log_det_layer_i(x) for i in layers)` è l'errore più comune
e il più difficile da vedere, perché con un solo layer è corretto, con più layer
il flusso resta invertibile, la log-verosimiglianza resta finita e i campioni
sembrano ragionevoli. L'unica cosa che si rompe è la normalizzazione: la
"densità" integra a un numero qualsiasi. Per questo qui ci sono tre test diversi
a coprirlo (Jacobiano numerico, integrale a 1, istogramma contro densità).

**Non invertire l'ordine dei layer in `flow_inverse`.** `(f_N ∘ … ∘ f_1)^{-1} =
f_1^{-1} ∘ … ∘ f_N^{-1}`. Con maschere alternate, applicare le inverse
nell'ordine sbagliato dà un risultato numericamente diverso ma non assurdo, e
`test_flow_invertibilita_esatta_su_piu_layer` è costruito apposta con configurazioni
da 1 a 8 layer: con un solo layer l'errore non si manifesta.

**Il segno del log-det in `log_prob`.** Con `f : x → z` (normalizzante) il segno
è più. Con `f : z → x` (generativa) sarebbe meno. Il deck scrive entrambe le
versioni in slide diverse — `General Multistep Case` mostra i due prodotti, uno
elevato a `−1` e uno no — e chi copia la formula sbagliata ottiene una densità
che integra a qualcosa di molto lontano da 1. `test_densita_integra_a_uno` è la
diagnosi immediata.

**Sommare i log-scala su tutte le dimensioni.** Solo le componenti con
`mask == 0` contribuiscono: le altre hanno derivata 1, che in log fa 0. La rete
di traslazione non contribuisce mai — una traslazione ha determinante 1.

**Applicare `np.exp` prima di sommare.** Il determinante è il *prodotto* della
diagonale, quindi il log-determinante è la *somma* dei `log_scale`. Chi somma
`exp(log_scale)` ottiene un numero sempre positivo e sempre sbagliato.

## Volume preservato ≠ identità

`test_caso_limite_log_scala_nulla_preserva_i_volumi` è la parte
dell'esercizio che vale la pena leggere due volte. Azzerando lo strato di uscita
della sola rete di scala si ottiene esattamente NICE (slide *Non-linear
Independent Components Estimation*): il flusso è tutto traslazioni, quindi
`log |det J| = 0` **esattamente**, in aritmetica floating point, non a meno di
`1e-16`. Ma la trasformazione non è affatto l'identità: sposta i punti, deforma
la densità in modo non banale, e il modello impara. È il contro-esempio che
smonta l'idea che il fattore di volume misuri "quanto la trasformazione fa
qualcosa". Misura solo quanto comprime o dilata.

Il test verifica l'uguaglianza esatta a `0.0`, non `allclose`, per due motivi:
perché matematicamente lo è, e perché blocca la scorciatoia di implementare il
log-det tramite lo Jacobiano numerico (che darebbe `~1e-16`).

## Flusso planare: dove finisce la struttura e comincia il vincolo

Il flusso planare è nel deck solo implicitamente (è il capostipite dei
normalizing flow, Rezende & Mohamed 2015), ma serve a isolare un punto che nei
coupling non si vede: lì l'invertibilità è **strutturale** — vale per qualunque
valore dei pesi, sempre, anche a inizializzazione casuale, anche a metà
addestramento. Nel planare va **imposta sui parametri**, e il flusso ne esce
invertibile solo in una regione dello spazio dei parametri.

`enforce_invertibility` sposta `u` lungo `w` e basta: la componente ortogonale a
`w` non entra in `wᵀu` e quindi non influenza il determinante, e va lasciata
intatta per non perdere espressività. Il test lo verifica esplicitamente. Il
`−1 + softplus(a)` è una funzione che manda `ℝ` in `(−1, +∞)` ed è vicina
all'identità per `a` grande: vincola senza distorcere i casi già validi.

Nota implementativa deliberata: `planar_flow_log_det` calcola
`np.log(1 + ψᵀu)` **senza** valore assoluto. Formalmente `log |det J|`
vorrebbe il modulo, ma metterlo qui nasconderebbe esattamente ciò che
l'esercizio vuole mostrare — un `1 + uᵀψ(x)` negativo non è un dettaglio di
segno, è la mappa che ha smesso di essere una bigezione (piega lo spazio su se
stesso) e la densità che ne deriverebbe non esiste. Il NaN è l'informazione
corretta. Nel caso peggiore, `x` sull'iperpiano `wᵀx + b = 0`, si ha `h' = 1` e
il termine vale `1 + wᵀu`: è da lì che esce la condizione `wᵀu ≥ −1`, ed è
perché `h' = 1 − tanh² ∈ (0, 1]` che quel caso è davvero il peggiore.

## L'oracolo

`numerical_jacobian` vive nel file dei test, non nel modulo, di proposito: deve
essere un metodo *diverso e più lento* di calcolare la stessa cosa, senza
condividere una riga con l'implementazione. Costruisce lo Jacobiano colonna per
colonna con differenze centrate (`eps = 1e-5`, errore misurato `~5e-10`) e ne
prende `np.linalg.slogdet`. È `O(D)` forward pass per punto — inutilizzabile in
pratica, ed è esattamente il costo che le architetture di questa lezione
esistono per evitare.

## Efficienza

`log_prob` chiama `flow_forward` e `flow_log_det` separatamente, quindi esegue
la forward pass due volte. È scritto così per chiarezza. Un'implementazione
reale restituisce `(z, log_det)` in una sola passata: nel training loop di un
flusso questa è la differenza fra un fattore 1 e un fattore 2 sul tempo per
epoca.
