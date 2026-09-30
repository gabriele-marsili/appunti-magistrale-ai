# 07 — Forward di una CNN da zero: convoluzione, pooling, campo recettivo

## Lezione di riferimento

`Lessons/GDL15-16 CNN.txt` — *Convolutional Neural Networks*. Nello specifico la
parte "Dissecting the components of a CNN": convoluzione, stride, pooling; poi
"Putting components back together" (da LeNet in avanti) e l'argomento avanzato
delle **dilated convolutions**. È l'esercizio che ricalca il Midterm 2 del
corso: scrivere il forward pass di una CNN senza framework.

## Il problema

Una CNN non è "una rete con dei filtri dentro". È una rete densa a cui sono
stati imposti due vincoli strutturali:

- **connettività locale**: ogni unità guarda solo una finestra di input;
- **condivisione dei pesi**: la stessa finestra di pesi è applicata in ogni
  posizione.

Il secondo vincolo è quello che conta, ed è ciò che rende l'operazione
**equivariante alla traslazione**: se trasli l'input, l'output si trasla nello
stesso modo. Se una feature è utile in un punto dell'immagine, lo è ovunque, e
la rete non deve reimpararla per ogni posizione. Tutto il resto (stride,
pooling, dilation) sono modi di controllare la geometria del campo recettivo e
il costo computazionale.

Qui implementi il forward completo con il solo numpy, e i test verificano che le
proprietà strutturali valgano davvero, non solo che i numeri tornino.

## Cosa devi implementare

Layout **NCHW**, come PyTorch: input `(N, C_in, H, W)`, kernel
`(C_out, C_in, KH, KW)`, output `(N, C_out, H_out, W_out)`.

| funzione | cosa fa |
| --- | --- |
| `output_shape(H, K, stride, padding, dilation)` | la formula della dimensione in uscita |
| `receptive_field(layers)` | campo recettivo di una pila di `(kernel, stride, dilation)` |
| `pad2d(x, pad)` | zero-padding sulle due dimensioni spaziali |
| `im2col(x, KH, KW, stride, padding, dilation)` | matrice delle patch, una patch per colonna |
| `conv2d(x, weight, bias, stride, padding, dilation)` | cross-correlazione via `im2col` + **un solo** prodotto matriciale |
| `max_pool2d(x, kernel_size, stride, padding)` | max pooling, padding a `-inf` |
| `avg_pool2d(x, kernel_size, stride, padding)` | average pooling, padding a zero contato nel denominatore |
| `relu(x)` | `max(x, 0)` |
| `batchnorm2d_inference(x, gamma, beta, running_mean, running_var, eps)` | BN in inferenza, statistiche per canale |
| `flatten(x)` | `(N, C, H, W) -> (N, C*H*W)`, C-major |
| `linear(x, weight, bias)` | `x @ weight.T + bias`, con `weight` di shape `(out, in)` |
| `forward_lenet(x, params)` | conv-relu-pool, conv-relu-pool, flatten, linear-relu, linear |

`conv2d_naive` e `make_lenet_params` sono **già scritte** e non vanno toccate.
`conv2d_naive` è la definizione trascritta in quattro cicli Python annidati:
lenta, ovviamente corretta, e usata dai test come oracolo indipendente contro
cui misurare la tua `conv2d`.

## Specifica matematica

**Cross-correlazione (quello che devi implementare).** Con `xpad` l'input
zero-paddato:

    out[n, co, i, j] = b[co] + Σ_{ci,u,v} w[co,ci,u,v] · xpad[n, ci, i·s + u·d, j·s + v·d]

**Convoluzione matematica vera.** La definizione classica ribalta il kernel su
entrambi gli assi:

    (f * g)[i, j] = Σ_{u,v} f[u, v] · g[i − u, j − v]

cioè `w[co, ci, KH−1−u, KW−1−v]` al posto di `w[co, ci, u, v]`. La differenza
pratica è solo un ribaltamento dei pesi. Poiché i pesi sono *appresi*, una rete
addestrata con la cross-correlazione impara semplicemente il kernel ribaltato
rispetto a una addestrata con la convoluzione: il modello ha esattamente lo
stesso potere espressivo. Per questo PyTorch, TensorFlow e Keras chiamano
"convolution" un'operazione che è tecnicamente una cross-correlazione — il flip
costerebbe tempo e non comprerebbe nulla. Cambia però in due casi: quando i
kernel sono fissati a mano (un filtro di Sobel va ribaltato per ottenere il
segno atteso) e quando si invocano le proprietà algebriche della convoluzione
(commutatività, teorema di convoluzione), che la cross-correlazione **non** ha.
Il test sul delta di Dirac non centrato rende visibile la differenza: la
direzione in cui l'immagine si sposta è opposta nei due casi.

**Geometria dell'uscita.**

    H_out = floor( (H + 2p − d·(K − 1) − 1) / s ) + 1

Il termine `K_eff = d·(K − 1) + 1` è il **kernel effettivo**: la dilation
allarga il supporto senza aggiungere un solo parametro. La divisione è un floor:
le finestre parziali in coda vengono scartate, non riempite.

**Campo recettivo.** Con `r` ampiezza corrente e `j` il *jump* (di quanti pixel
di input ci si sposta muovendosi di 1 pixel sull'uscita di quel layer):

    r ← 1,  j ← 1
    per ogni layer (k, s, d):   k_eff = d·(k−1)+1;   r ← r + (k_eff − 1)·j;   j ← j·s

Il padding non compare: sposta *dove* sta il campo recettivo, non *quanto* è
largo. Le conseguenze da saper leggere: due 3×3 impilate vedono 5 pixel come una
5×5 ma con meno parametri e una nonlinearità in mezzo; lo stride fa crescere il
campo recettivo in modo **moltiplicativo** con la profondità; la dilation lo
allarga a parità di parametri e di risoluzione, che è il motivo per cui si usa
nella segmentazione densa.

**im2col.** La convoluzione è un prodotto matriciale mascherato. Costruita la
matrice `C` di shape `(C_in·KH·KW, N·H_out·W_out)` in cui ogni **colonna** è una
finestra di input appiattita, e appiattito il kernel in `W` di shape
`(C_out, C_in·KH·KW)`, l'intera convoluzione è

    out = W · C

più il reshape. Le convenzioni esatte di ordinamento di righe e colonne sono
nella docstring di `im2col` e vanno rispettate alla lettera: sono ciò che rende
compatibile `weight.reshape(C_out, −1)` con la matrice delle patch.

**Pooling.** Se `stride` è `None` vale `kernel_size`, quindi le finestre sono
disgiunte e il pooling sottocampiona. Il padding del **max** pooling è a `-inf`,
non a zero: `-inf` è l'elemento neutro del massimo come `0` lo è della somma.
Con zeri, un input tutto negativo produrrebbe degli zeri spuri sui bordi, cioè
un valore che non compare da nessuna parte nell'input. L'average pooling invece
padda a zero e conta le celle di padding nel denominatore (`count_include_pad`,
il default di PyTorch).

**BatchNorm in inferenza.** Per canale `c`:

    y = gamma[c] · (x − running_mean[c]) / sqrt(running_var[c] + eps) + beta[c]

Nulla viene ricalcolato dal batch: in inferenza la BN è una trasformazione
affine fissa per canale (e infatti si può fondere nei pesi della convoluzione
precedente).

## Perché questo esercizio

Perché la domanda d'orale non è "come si scrive il ciclo della convoluzione", è
"perché la convoluzione". Due test rispondono a quella domanda in modo
verificabile.

Il primo mostra che `conv(traslazione(x)) = traslazione(conv(x))` nella regione
interna: è l'equivarianza, la proprietà che giustifica l'esistenza dell'operazione
e che scompare non appena i pesi smettono di essere condivisi. Accanto c'è il
controcanto: il max pooling **non** è equivariante per shift che non siano
multipli dello stride, mentre lo è esattamente per gli shift multipli — che è il
motivo per cui il pooling compra invarianza locale al prezzo della risoluzione.

Il secondo misura il campo recettivo perturbando un pixel dell'input e contando
chi si muove a valle. Se il tuo `receptive_field` somma gli stride invece di
moltiplicarli, o ignora la dilation, il test lo dice con un numero.

Il resto scopre le confusioni classiche: `dilation` applicata agli indici di
input invece che a quelli del kernel, `stride` e `dilation` che si mescolano
appena compaiono insieme, il floor della formula dimenticato, l'ordine C-major
del flatten incoerente con l'orientamento di `fc1_w`, e `weight` di `linear`
usato senza trasporre.

## Vincoli

Solo `numpy` e la standard library. **Vietati** `np.convolve`, `np.correlate`,
`scipy.signal`, `scipy.ndimage`, `torch`: la convoluzione la scrivi tu. Vietato
anche chiamare `conv2d_naive` dentro `conv2d`, per ovvie ragioni: è l'oracolo.
`conv2d` deve passare da `im2col` e da **un solo** prodotto matriciale, senza
cicli sui pixel (un ciclo sui `KH·KW` offset del kernel va benissimo: è
indipendente dalla dimensione dell'immagine).

Ogni sorgente di casualità passa da un `rng` (`numpy.random.Generator`): mai
`np.random.seed`, mai il modulo `random`, mai `time`.

## Come autovalutarti

```bash
cd /home/claude/gdl/esercizi/07_conv_forward
python3 -m pytest test_conv_forward.py -v
```

Tutti i test devono passare. Ogni asserzione ha un messaggio che indica quale
errore concettuale l'ha fatta fallire; leggilo prima di correggere a caso.
Ordine consigliato: `output_shape` e `pad2d`, poi `im2col` (il test sulle patch
è quello che ti dice se le convenzioni di indice sono giuste), poi `conv2d`
contro l'oracolo, poi pooling e pipeline.

## Tempo stimato

2 ore. `output_shape`, `pad2d`, `relu`, `flatten`, `linear` e la BN sono
quindici minuti in tutto. `im2col` con stride e dilation insieme è la parte
difficile e vale metà del tempo. `receptive_field` sono quattro righe, ma
capire perché il jump si moltiplica ne richiede molte di più.

## Domande d'orale collegate

1. Cosa distingue una convoluzione da un layer completamente connesso, e quale
   dei due vincoli (località, condivisione dei pesi) produce l'equivarianza alla
   traslazione?
2. Il pooling rende la rete invariante o equivariante alla traslazione? Rispetto
   a quali traslazioni esattamente, e cosa si perde in cambio?
3. Perché due convoluzioni 3×3 impilate sono preferibili a una 5×5, a parità di
   campo recettivo?
4. A cosa serve una convoluzione dilated, e in cosa differisce dall'aumentare lo
   stride o la dimensione del kernel per ottenere lo stesso campo recettivo?
5. Cosa fa una convoluzione 1×1, visto che non aggrega nulla spazialmente?
6. Perché i framework implementano la cross-correlazione e la chiamano
   convoluzione? Quando la differenza conta davvero?
