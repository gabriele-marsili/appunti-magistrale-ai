# 10 — Attention, cross-attention, Transformer

## Lezione di riferimento

`Lessons/GDL19 cross attention.txt` — *Attention-based architectures: recurrent
encoder-decoder*: sequence-to-sequence, il collo di bottiglia del vettore di
contesto singolo, il meccanismo di cross-attention fra decoder ed encoder.

`Lessons/GDL20 transformers.txt` — *Attention-based architectures:
Transformers*: self-attention, il blocco Transformer, inductive bias e
propagazione del gradiente.

Le due lezioni vanno lette insieme, perché il punto è che sono la stessa cosa.
GDL19 introduce l'attenzione come modo per far guardare al decoder tutti gli
stati dell'encoder invece di un solo vettore riassuntivo; GDL20 osserva che se
la sorgente delle chiavi coincide con la sorgente delle query si ottiene la
self-attention, e che a quel punto la ricorrenza non serve più. La domanda che
la slide di GDL20 lascia aperta — *"what are we losing when we gain global
dependencies and full parallelism?"* — ha una risposta precisa, ed è il test
`(c)` di questo esercizio.

## Il problema

Un encoder ricorrente comprime l'intera sorgente in un vettore di dimensione
fissa. L'attenzione sostituisce quel vettore con una media pesata degli stati
dell'encoder, con pesi che dipendono dallo stato corrente del decoder:

    e_i    = score(h_dec, h_enc_i)
    alpha  = softmax(e)
    c      = Σ_i alpha_i h_enc_i

Le tre varianti storiche di `score` sono l'additiva di Bahdanau e le
moltiplicative di Luong. La scaled dot-product del Transformer è la
moltiplicativa con un fattore `1/sqrt(d_k)`, resa parallela su tutte le query
insieme.

## Cosa devi implementare

| funzione | cosa fa |
| --- | --- |
| `softmax(x, axis=-1)` | softmax stabile (sottrazione del massimo) lungo `axis` |
| `bahdanau_score(h_dec, H_enc, Wa, Ua, va)` | attenzione additiva, un punteggio per stato di encoder |
| `luong_score(h_dec, H_enc, Wa=None)` | attenzione moltiplicativa, varianti *dot* e *general* |
| `scaled_dot_product_attention(Q, K, V, mask=None)` | il nucleo del Transformer; ritorna `(out, attn)` |
| `causal_mask(L)` | maschera triangolare booleana, `(L, L)` |
| `padding_mask(lengths, L)` | maschera booleana `(N, L)` per sequenze di lunghezza diversa |
| `split_heads(x, n_heads)` | da `(N, L, d_model)` a `(N, n_heads, L, d_head)` |
| `merge_heads(x)` | l'inversa esatta |
| `multi_head_attention(X_q, X_kv, Wq, Wk, Wv, Wo, n_heads, mask=None)` | self- **e** cross-attention, stessa funzione |
| `positional_encoding(L, d_model)` | encoding sinusoidale del paper |
| `layer_norm(x, gamma, beta, eps=1e-5)` | normalizzazione sull'ultima dimensione |
| `transformer_encoder_block(X, params, mask=None)` | blocco encoder completo, convenzione post-LN |
| `attention_complexity(L, d)` | `(flops_stimati, memoria_stimata)` di una self-attention |

## Specifica matematica

**Attenzione additiva (Bahdanau).** Con `h_dec` di dimensione `d_dec` e
`H_enc[i]` di dimensione `d_enc`:

    score_i = va^T tanh(Wa h_dec + Ua H_enc[i])

`Wa` è `(d_attn, d_dec)`, `Ua` è `(d_attn, d_enc)`, `va` è `(d_attn,)`. Il
termine `Wa h_dec` non dipende da `i`: si calcola una volta e si somma per
broadcasting.

**Attenzione moltiplicativa (Luong).**

    dot:      score_i = H_enc[i]^T h_dec               (richiede d_enc = d_dec)
    general:  score_i = H_enc[i]^T Wa h_dec            (Wa di shape (d_enc, d_dec))

**Scaled dot-product attention.**

    Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) V

con `Q` di shape `(..., Lq, d_k)`, `K` di shape `(..., Lk, d_k)`, `V` di shape
`(..., Lk, d_v)`. Gli assi iniziali sono assi di batch (batch, teste) e vanno
gestiti per broadcasting: il prodotto riguarda solo le ultime due dimensioni.
L'output è `(..., Lq, d_v)`, i pesi `(..., Lq, Lk)`.

Il fattore `1/sqrt(d_k)` non è cosmetico. Se le componenti di `q` e `k` sono
indipendenti a media 0 e varianza 1, allora `q·k` ha varianza `d_k`, quindi
deviazione standard `sqrt(d_k)`. Con `d_k = 64` i logit hanno scala 8 e il
softmax si comporta come un `argmax`: un peso vicino a 1 e tutti gli altri
vicini a 0, con gradiente quasi nullo. La divisione riporta i logit a varianza
unitaria.

**Maschere.** Convenzione di tutto l'esercizio: la maschera è **booleana** e
`True` significa *posizione da mascherare*. Il mascheramento avviene mettendo
`-inf` nei punteggi **prima** del softmax, mai azzerando i pesi dopo (azzerare
dopo lascia la riga non normalizzata).

    causal_mask(L)[i, j]   = True  sse  j > i          (il futuro è invisibile)
    padding_mask(l, L)[n, j] = True  sse  j >= l[n]    (il padding è invisibile)

`causal_mask` non maschera la diagonale: ogni posizione vede se stessa, quindi
nessuna riga resta completamente vuota. `padding_mask` produce `(N, L)` e va
espansa a `mask[:, None, None, :]` per essere broadcastata su
`(N, n_heads, Lq, Lk)`.

**Multi-head.** Con `d_head = d_model / n_heads`:

    Q = X_q Wq,   K = X_kv Wk,   V = X_kv Wv
    head_h = Attention(Q_h, K_h, V_h)          Q_h = colonne [h·d_head, (h+1)·d_head)
    out    = concat(head_1, ..., head_H) Wo

Lo scaling dentro ogni testa usa `d_head`, non `d_model`.

`multi_head_attention` è **una sola funzione** per self- e cross-attention:
non serve alcun ramo di codice che distingua i due casi. Se `X_q` e `X_kv` sono
lo stesso tensore è self-attention (e necessariamente `Lq = Lkv`); se sono
tensori diversi è cross-attention, con `Lq` e `Lkv` indipendenti. L'output ha
sempre la lunghezza delle **query**.

**Positional encoding sinusoidale.**

    PE[pos, 2i]   = sin(pos / 10000^(2i/d_model))
    PE[pos, 2i+1] = cos(pos / 10000^(2i/d_model))

Colonne pari seni, colonne dispari coseni; le due colonne di uno stesso `i`
condividono la frequenza `ω_i = 10000^(-2i/d_model)`. Da qui segue la proprietà
che il test `(g)` verifica: per ogni offset `k` esiste una matrice `M_k`
**indipendente da `pos`** tale che `PE[pos+k] = M_k PE[pos]`, ed è una
rotazione a blocchi `2×2`.

**Layer normalization.**

    LN(x) = gamma ⊙ (x − μ) / sqrt(σ² + eps) + beta

con `μ` e `σ²` calcolate lungo l'**ultima** dimensione (varianza biased,
denominatore `d`), indipendentemente per ogni riga. È la differenza con
BatchNorm, che calcola le statistiche lungo l'asse del batch: le statistiche di
LayerNorm sono locali all'esempio, quindi non c'è distinzione train/test, non
servono medie mobili e il risultato non cambia al variare della composizione
del minibatch. Per sequenze paddate di lunghezza variabile è l'unica scelta
sensata.

**Blocco encoder, convenzione post-LN** (quella del paper originale):

    A = MultiHead(X, X)
    H = LayerNorm(X + A)
    F = ReLU(H W1 + b1) W2 + b2
    Y = LayerNorm(H + F)

La normalizzazione sta **dopo** la somma residua. Conseguenza osservabile: con
`gamma = 1` e `beta = 0` l'output del blocco ha media 0 e varianza 1
sull'ultimo asse, perché l'ultima operazione è una normalizzazione. La variante
moderna **pre-LN** normalizza invece l'ingresso dei sottomoduli
(`X + MHA(LN(X))`, poi `H + FFN(LN(H))`): il cammino residuo resta
un'identità pura da un capo all'altro dello stack, i gradienti non attraversano
una LayerNorm a ogni blocco, e si può addestrare senza warmup del learning
rate. Con pre-LN l'asserzione su media 0 / varianza 1 in uscita è falsa.

La feed-forward è *position-wise*: gli stessi pesi a ogni posizione, nessun
mescolamento fra posizioni. Tutto il mescolamento avviene nell'attenzione — ed
è per questo che la causalità imposta nella maschera sopravvive fino
all'uscita del blocco.

**Costo.** Con la convenzione "una moltiplicazione più una somma = 2 FLOP":

    flops   = 4 L² d + 8 L d²        (punteggi + media pesata + 4 proiezioni)
    memoria = L² + 3 L d             (matrice di attenzione + Q, K, V)

Il termine dominante per `L ≫ d` è quadratico in `L` in entrambi i casi.

## Perché questo esercizio

Scopre tre confusioni, in ordine di gravità.

1. **Che la self-attention non sappia nulla dell'ordine.** È la cosa che si
   perde guadagnando dipendenze globali e parallelismo pieno, ed è la ragione
   per cui il positional encoding esiste. Chi crede che l'attenzione "veda la
   sequenza" non sa spiegare perché serva il PE. Il test `(c)` la rende
   verificabile: la self-attention pura è *equivariante alle permutazioni*
   in modo esatto, e sommando il PE questa equivarianza si rompe.
2. **Che la maschera causale sia una scelta di convenzione con un verso
   sbagliato.** Una maschera invertita produce comunque pesi che sommano a 1 e
   output della shape corretta: nessun controllo di forma se ne accorge. Il
   test `(b)` la verifica per quello che è, cioè un'affermazione sulla
   dipendenza funzionale — si perturba un input futuro e si controlla che
   l'output al tempo `t` non si muova di un bit.
3. **Che self-attention e cross-attention siano lo stesso blocco.** Chi le
   tratta come due meccanismi diversi scrive due funzioni e sbaglia le
   lunghezze; la differenza è soltanto chi fornisce `K` e `V`, e l'output ha
   sempre la lunghezza delle query.

Restano due dettagli che in orale vengono chiesti spesso: perché lo scaling
`1/sqrt(d_k)` non sia un'inezia (test `(f)`, misurato come entropia dei pesi) e
perché il Transformer usi LayerNorm e non BatchNorm (test `(h)`, verificato
mostrando che la LayerNorm su un batch coincide con la LayerNorm elemento per
elemento).

## Vincoli

Solo `numpy` e la standard library. Niente `torch`, `scipy`, `sklearn`,
`matplotlib`. Ogni sorgente di casualità passa dal `rng`
(`numpy.random.Generator`) ricevuto come argomento: mai `np.random.seed`, mai
il modulo `random`, mai `time`.

Non toccare `relu` e `make_encoder_params`: sono già forniti e i test li usano.

Le convenzioni sulle maschere (`True` = da mascherare), sull'asse di
normalizzazione dei pesi (l'ultimo) e sull'ordine degli assi
(`(N, n_heads, L, d_head)`) non sono negoziabili: i test le verificano
esplicitamente.

## Come autovalutarti

```bash
cd /home/claude/gdl/esercizi/10_attention
python3 -m pytest test_attention.py -v
```

Tutti i test devono passare. Ogni asserzione ha un messaggio che indica quale
errore concettuale l'ha fatta fallire; leggilo prima di correggere a caso.

## Tempo stimato

2 ore. Le prime sei funzioni sono poche righe l'una. Il tempo vero se ne va in
tre punti: gestire correttamente gli assi di batch in
`scaled_dot_product_attention` (`swapaxes(-1, -2)`, non `.T`), azzeccare
l'ordine di `reshape` e `transpose` in `split_heads`/`merge_heads`, e capire
perché il test sull'equivarianza deve passare *prima* del positional encoding e
fallire *dopo*.

## Domande d'orale collegate

1. Che differenza c'è fra attenzione additiva (Bahdanau) e moltiplicativa
   (Luong), e perché il Transformer usa la seconda?
2. A cosa serve il fattore `1/sqrt(d_k)` nella scaled dot-product attention?
   Cosa succede senza, e perché il problema peggiora al crescere di `d_k`?
3. Perché il Transformer ha bisogno del positional encoding, mentre una RNN no?
   Che proprietà della self-attention rende il PE indispensabile?
4. In che senso self-attention e cross-attention sono lo stesso meccanismo?
   Cosa cambia fra i due usi?
5. Perché nel Transformer si usa LayerNorm e non BatchNorm? E qual è la
   differenza fra post-LN e pre-LN?
6. Qual è la complessità della self-attention in tempo e memoria, e perché
   limita la lunghezza di contesto?
