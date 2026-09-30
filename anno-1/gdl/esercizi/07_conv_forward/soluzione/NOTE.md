# Note sulla soluzione

## Il filo conduttore

Tutto l'esercizio ruota attorno a un'unica identità: la convoluzione è un
prodotto matriciale con i pesi condivisi fra le righe. `im2col` rende quella
frase letterale, e una volta costruita la matrice delle patch il resto del
forward è contabilità di indici. Le due proprietà che l'esercizio verifica —
equivarianza alla traslazione e campo recettivo — sono conseguenze dirette della
condivisione dei pesi e della geometria delle finestre, non dettagli
implementativi.

## im2col: dove si sbaglia

La firma restituisce `(C·KH·KW, N·H_out·W_out)`, cioè le **colonne** sono le
patch. È la convenzione storica di Caffe, e rende la convoluzione
`weight.reshape(C_out, -1) @ cols`. L'altra convenzione (patch sulle righe,
`cols @ W.T`) è altrettanto valida ma i test verificano questa: la docstring
scrive esplicitamente la mappa `(c, u, v) -> (c·KH + u)·KW + v`, ed è quella che
rende `weight.reshape(C_out, -1)` compatibile senza trasposizioni, perché numpy
appiattisce in ordine C-major e `weight` ha shape `(C_out, C_in, KH, KW)`.

Il trucco implementativo è non ciclare sui pixel. Si cicla sui `KH·KW` offset
del kernel, e per ogni offset `(u, v)` si estrae con un solo slice strided il
pixel che quel peso incontra in **tutte** le finestre:

    xpad[:, :, u*d : u*d + s*H_out : s, v*d : v*d + s*W_out : s]

Qui si vede in due caratteri la differenza fra i due parametri che tutti
confondono: `dilation` moltiplica l'indice del **kernel** (`u*d`, compare
nell'offset iniziale), `stride` moltiplica l'indice dell'**output** (compare
come passo dello slice). Chi scambia i due ruoli passa i test con stride=1 o
dilation=1 e fallisce esattamente sulla combinazione `(2, 2, 2)`, che è il
motivo per cui è in `COMBINAZIONI`.

Che lo slice produca esattamente `H_out` elementi non è fortuna: dalla formula
`H_out = floor((Hp − d(KH−1) − 1)/s) + 1` segue `d·u + s·(H_out−1) ≤ Hp − 1` per
ogni `u < KH`, cioè l'ultima finestra cade dentro l'input paddato per costruzione.

## conv2d

Un solo `@`. Il prodotto esce come `(C_out, N·H_out·W_out)` e va riportato in
NCHW con `reshape(C_out, N, H_out, W_out).transpose(1, 0, 2, 3)` — in
quest'ordine, perché l'indice di colonna è `(n·H_out + i)·W_out + j` e quindi
`N` è l'asse più lento dopo `C_out`. Un `reshape(N, C_out, H_out, W_out)` diretto
compila e dà numeri plausibili ma mescola batch e canali: è l'errore che il test
oracolo prende con `N > 1`.

Il bias è per canale di uscita e va sommato dopo, con broadcast `(1, C_out, 1, 1)`.
Metterlo dentro la matrice dei pesi (colonna di 1 aggiunta alle patch) funziona
ma complica `im2col` per niente.

## Perché `-inf` nel max pooling

Perché `-inf` è l'elemento neutro del massimo, come `0` lo è della somma. Il
padding deve introdurre valori che **non possono vincere**: con zeri, un input
tutto negativo (perfettamente normale dopo una BN, o prima di una ReLU)
produrrebbe degli zeri sui bordi dell'output, cioè un valore che non esiste da
nessuna parte nell'input. Il test lo verifica su `-|1..16|`. L'average pooling è
il caso duale: lì `0` è il neutro della somma, quindi si padda a zero — e resta
la scelta, non neutra, se contare le celle di padding nel denominatore. Qui si
conta (`count_include_pad=True`, il default di PyTorch), il che significa che i
bordi vengono attenuati.

## Equivarianza: cosa vale e dove

`conv(shift(x)) = shift(conv(x))` vale **esattamente** ovunque tranne che ai
bordi, dove il padding fornisce zeri che non sono stati traslati insieme al
resto. Per questo il test confronta una regione interna: il ritaglio è scelto in
modo che nessuna delle due finestre coinvolte tocchi il bordo. Con `roll` come
traslazione l'input non perde informazione (il contenuto rientra dall'altra
parte), ma introduce una discontinuità artificiale, che sta anch'essa fuori dal
ritaglio.

L'equivarianza vale per stride 1. Con stride `s` la convoluzione è equivariante
solo rispetto a traslazioni multiple di `s` — esattamente la stessa struttura
che il test sul max pooling verifica in entrambe le direzioni: shift di 2
(= stride) e l'output trasla di 1 cella *esattamente*; shift di 1 e l'output non
è la traslazione di sé stesso per nessun intero. Questo è il punto d'orale sul
pooling: non regala invarianza gratis, regala invarianza *locale* al prezzo
della risoluzione, e la "invarianza alla traslazione" delle CNN è in realtà
equivarianza a grana grossa più aggregazione finale.

## Campo recettivo: perché il jump si moltiplica

`r ← r + (k_eff − 1)·j`, `j ← j·s`. La parte che va capita è `j`: è il passo, in
pixel di input, corrispondente a un passo di 1 pixel sull'uscita del layer
corrente. Ogni layer aggiunge `k_eff − 1` posizioni al campo recettivo, ma
ciascuna vale `j` pixel di input, non 1. E poiché lo stride di ogni layer
moltiplica il jump per tutti i layer successivi, gli stride si **compongono
moltiplicativamente**: è la ragione per cui in una rete profonda con qualche
stride 2 il campo recettivo cresce molto più in fretta di quanto suggerisca la
somma dei kernel. L'errore tipico è `j += s`.

Il padding non compare nella ricorrenza. Sposta il centro del campo recettivo,
non la sua ampiezza — un'altra cosa che vale la pena saper dire all'orale.

Il test empirico misura la definizione: pesi tutti a 1 (nessuna cancellazione
possibile), padding 0 (così la finestra di un pixel di output centrale è
interamente dentro l'input e non viene troncata), input a zero, e si perturba
una colonna alla volta contando quali fanno muovere un pixel di output fissato.
Si perturba una colonna intera e non un singolo pixel perché così la misura
isola l'asse orizzontale: la copertura verticale è garantita comunque.

## forward_lenet

L'ordine è `conv → relu → pool`, non `conv → pool → relu`. Con il max pooling
i due ordini danno lo stesso risultato (la ReLU è monotona crescente, quindi
commuta con il massimo) — ma non con l'average pooling, e non se al posto della
ReLU c'è qualcos'altro. Scriverlo nell'ordine giusto costa zero.

Due trappole nell'ultima parte. `flatten` deve essere C-major, cioè `W` scorre
più in fretta, poi `H`, poi `C`: è l'ordine di `torch.flatten(x, 1)` su un
tensore contiguo, ed è l'ordine in cui devono essere disposte le colonne di
`fc1_w`. Un `transpose` di troppo prima del reshape non cambia la shape ma
permuta le feature, e il modello continua a girare producendo numeri diversi:
è un bug silenzioso. E `linear` usa `weight.T`, perché `weight` ha shape
`(out, in)` come `torch.nn.Linear.weight`. Infine l'ultimo layer non ha
attivazione: restituisce logit, la softmax vive nella loss.

## Collegamento alle slide

GDL15-16, sezione "Dissecting the components of a CNN": convoluzione, stride,
pooling sono esattamente le tre funzioni centrali di questo file. "Putting
components back together / From LeNet to ResNet" è `forward_lenet`, che è la
LeNet nella sua forma minima. "Advanced topics: dilated convolutions" è il
parametro `dilation`, e il senso di quel parametro sta tutto nel test sul campo
recettivo: `receptive_field([(3,1,2), (3,1,1)]) == 7` con lo stesso numero di
pesi di due 3×3 normali, che ne darebbero 5, e senza perdere risoluzione come
farebbe uno stride 2.
