"""Esercizio GDL19/GDL20 - "Cross-attention" e "Transformers".

Implementa le funzioni marcate `# TODO`. Tutto il resto (ReLU, generatore di
parametri per il blocco encoder) e' gia' fornito e non va toccato.

Solo numpy + stdlib. Ogni sorgente di casualita' passa da `rng`
(`numpy.random.Generator`): niente `np.random.seed`, niente `random`.

Convenzioni valide per tutto il file
------------------------------------
- Le maschere sono BOOLEANE e True significa "posizione DA MASCHERARE"
  (punteggio portato a -inf PRIMA del softmax, peso risultante 0).
- I pesi di attenzione normalizzano sempre sull'ULTIMO asse (le chiavi).
- Il batch e' sempre il primo asse; l'asse delle teste, quando c'e', e' il
  secondo.
"""

from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Utilita' fornite - NON modificare.
# ---------------------------------------------------------------------------


def relu(x):
    """ReLU elemento per elemento."""
    return np.maximum(np.asarray(x, dtype=float), 0.0)


def make_encoder_params(d_model, d_ff, n_heads, rng):
    """Costruisce un dizionario di parametri per ``transformer_encoder_block``.

    Parametri
    ---------
    d_model : int, divisibile per ``n_heads``
    d_ff    : int, dimensione interna della feed-forward position-wise
    n_heads : int
    rng     : numpy.random.Generator

    Ritorna
    -------
    dict con le chiavi:
        "Wq", "Wk", "Wv", "Wo" : (d_model, d_model)
        "W1" : (d_model, d_ff)   "b1" : (d_ff,)
        "W2" : (d_ff, d_model)   "b2" : (d_model,)
        "gamma1", "beta1"        : (d_model,)   layer norm dopo la self-attention
        "gamma2", "beta2"        : (d_model,)   layer norm dopo la feed-forward
        "n_heads" : int
    """
    s = 1.0 / np.sqrt(d_model)
    return {
        "Wq": rng.normal(0.0, s, size=(d_model, d_model)),
        "Wk": rng.normal(0.0, s, size=(d_model, d_model)),
        "Wv": rng.normal(0.0, s, size=(d_model, d_model)),
        "Wo": rng.normal(0.0, s, size=(d_model, d_model)),
        "W1": rng.normal(0.0, s, size=(d_model, d_ff)),
        "b1": np.zeros(d_ff),
        "W2": rng.normal(0.0, 1.0 / np.sqrt(d_ff), size=(d_ff, d_model)),
        "b2": np.zeros(d_model),
        "gamma1": np.ones(d_model),
        "beta1": np.zeros(d_model),
        "gamma2": np.ones(d_model),
        "beta2": np.zeros(d_model),
        "n_heads": int(n_heads),
    }


# ---------------------------------------------------------------------------
# 1. Softmax
# ---------------------------------------------------------------------------


def softmax(x, axis=-1):
    """Softmax numericamente stabile lungo ``axis``.

    Ritorna un array della stessa shape di ``x``, non negativo, che somma a 1
    lungo ``axis``. "Stabile" significa che il massimo lungo ``axis`` va
    sottratto prima dell'esponenziale: senza, ``exp(1000)`` va in overflow.
    Il risultato non cambia, perche' ``softmax(x + c) = softmax(x)``.

    Se una fetta lungo ``axis`` e' interamente ``-inf`` (riga completamente
    mascherata) il risultato e' indefinito. Non capita con ``causal_mask``;
    puo' capitare con ``padding_mask`` su lunghezza 0.
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 2. Attenzione additiva (Bahdanau) e moltiplicativa (Luong)
# ---------------------------------------------------------------------------


def bahdanau_score(h_dec, H_enc, Wa, Ua, va):
    """Punteggi di attenzione additiva (Bahdanau et al., 2015).

        score_i = va^T tanh(Wa @ h_dec + Ua @ H_enc[i])

    Parametri
    ---------
    h_dec : (d_dec,)      stato corrente del decoder
    H_enc : (L, d_enc)    stati dell'encoder, uno per riga
    Wa    : (d_attn, d_dec)
    Ua    : (d_attn, d_enc)
    va    : (d_attn,)

    Ritorna
    -------
    (L,) punteggi NON normalizzati (il softmax lo applica il chiamante).
    """
    # TODO
    raise NotImplementedError


def luong_score(h_dec, H_enc, Wa=None):
    """Punteggi di attenzione moltiplicativa (Luong et al., 2015).

    ``Wa is None``  -> variante *dot*:      score_i = H_enc[i] . h_dec
    ``Wa`` fornita  -> variante *general*:  score_i = H_enc[i] . (Wa @ h_dec)

    Parametri
    ---------
    h_dec : (d_dec,)
    H_enc : (L, d_enc)
    Wa    : (d_enc, d_dec) oppure None. Con None serve d_enc == d_dec.

    Ritorna
    -------
    (L,) punteggi NON normalizzati.
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 3. Scaled dot-product attention e maschere
# ---------------------------------------------------------------------------


def scaled_dot_product_attention(Q, K, V, mask=None):
    """Attenzione scalata a prodotto scalare.

        Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) V

    Parametri
    ---------
    Q : (..., Lq, d_k)
    K : (..., Lk, d_k)
    V : (..., Lk, d_v)
    mask : booleana, broadcastabile a (..., Lq, Lk), oppure None.
           True = posizione DA MASCHERARE (il punteggio diventa -inf e il peso 0).

    Ritorna
    -------
    (out, attn) con out di shape (..., Lq, d_v) e attn di shape (..., Lq, Lk).
    ``attn`` somma a 1 sull'ultimo asse.

    Nota: gli assi iniziali "..." sono assi di batch (batch, teste, ...) e vanno
    gestiti per broadcasting; il prodotto e' fra le ultime due dimensioni.
    """
    # TODO
    raise NotImplementedError


def causal_mask(L):
    """Maschera causale (autoregressiva) di shape (L, L), booleana.

    ``mask[i, j] == True`` se e solo se ``j > i``: la query in posizione ``i``
    non puo' guardare le chiavi FUTURE. La diagonale resta visibile (la
    posizione guarda se stessa), quindi nessuna riga e' completamente
    mascherata.
    """
    # TODO
    raise NotImplementedError


def padding_mask(lengths, L):
    """Maschera di padding, booleana, shape (N, L).

    Parametri
    ---------
    lengths : (N,) interi, lunghezza reale di ciascuna sequenza del batch
    L       : int, lunghezza paddata (L >= max(lengths))

    Ritorna
    -------
    (N, L) con True nelle posizioni di PADDING, cioe' ``j >= lengths[n]``.

    Per usarla in ``multi_head_attention``, che vuole una maschera
    broadcastabile a (N, n_heads, Lq, Lk), va espansa: ``mask[:, None, None, :]``.
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 4. Multi-head: split, merge, e l'unificazione self/cross
# ---------------------------------------------------------------------------


def split_heads(x, n_heads):
    """Da (N, L, d_model) a (N, n_heads, L, d_head), con d_head = d_model/n_heads.

    Le teste sono fette CONTIGUE dell'ultima dimensione: la testa h prende le
    colonne ``[h*d_head : (h+1)*d_head]``.
    """
    # TODO
    raise NotImplementedError


def merge_heads(x):
    """Inversa esatta di ``split_heads``: da (N, n_heads, L, d_head) a (N, L, d_model),
    con d_model = n_heads * d_head."""
    # TODO
    raise NotImplementedError


def multi_head_attention(X_q, X_kv, Wq, Wk, Wv, Wo, n_heads, mask=None):
    """Multi-head attention. UNA sola funzione per self- e cross-attention.

        Q = X_q  Wq        K = X_kv Wk        V = X_kv Wv
        head_h  = Attention(Q_h, K_h, V_h)
        out     = concat(head_1..head_H) Wo

    Parametri
    ---------
    X_q  : (N, Lq,  d_model)   da cui si ricavano le QUERY
    X_kv : (N, Lkv, d_model)   da cui si ricavano CHIAVI e VALORI
    Wq, Wk, Wv, Wo : (d_model, d_model)
    n_heads : int, divide d_model
    mask : booleana broadcastabile a (N, n_heads, Lq, Lkv), True = da mascherare

    Ritorna
    -------
    (out, attn) con out (N, Lq, d_model) e attn (N, n_heads, Lq, Lkv).

    SELF vs CROSS
    -------------
    Non c'e' nessuna differenza algoritmica, e non serve alcun ramo di codice
    che distingua i due casi. Se ``X_q is X_kv`` (o comunque se sono lo stesso
    tensore) la funzione calcola SELF-attention: ogni posizione interroga le
    altre posizioni della stessa sequenza, e necessariamente Lq == Lkv. Se
    ``X_q`` e ``X_kv`` sono tensori diversi la funzione calcola
    CROSS-attention: le query vengono dal decoder, chiavi e valori
    dall'encoder, e le due lunghezze sono indipendenti (Lq != Lkv e' normale).
    Questa unificazione e' il passaggio GDL19 -> GDL20: la cross-attention
    encoder-decoder di Bahdanau e la self-attention del Transformer sono lo
    stesso blocco, cambia solo CHI fornisce K e V. La lunghezza dell'output e'
    sempre Lq, mai Lkv: l'attenzione ricampiona la sorgente sulla griglia
    della destinazione.

    Attenzione: lo scaling dentro ciascuna testa usa d_head, non d_model.
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 5. Positional encoding
# ---------------------------------------------------------------------------


def positional_encoding(L, d_model):
    """Positional encoding sinusoidale del paper "Attention is all you need".

        PE[pos, 2i]   = sin(pos / 10000^(2i / d_model))
        PE[pos, 2i+1] = cos(pos / 10000^(2i / d_model))

    con pos = 0..L-1 e i = 0..d_model/2-1. Le colonne PARI sono seni, le
    DISPARI coseni, e le due colonne di uno stesso ``i`` condividono la
    frequenza.

    Parametri
    ---------
    L : int, numero di posizioni
    d_model : int PARI (solleva ValueError se dispari)

    Ritorna
    -------
    (L, d_model)
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 6. Layer normalization
# ---------------------------------------------------------------------------


def layer_norm(x, gamma, beta, eps=1e-5):
    """Layer normalization sull'ULTIMA dimensione.

        y = gamma * (x - mean(x)) / sqrt(var(x) + eps) + beta

    dove media e varianza sono calcolate lungo l'ultimo asse, in modo
    indipendente per ogni riga (varianza biased, denominatore d).

    Parametri
    ---------
    x     : (..., d)
    gamma : (d,) scala appresa
    beta  : (d,) shift appreso
    eps   : float

    Ritorna
    -------
    (..., d)

    DIFFERENZA CON BATCHNORM
    ------------------------
    BatchNorm normalizza ogni FEATURE sul BATCH: le statistiche di un esempio
    dipendono dagli altri esempi del minibatch, servono medie mobili a test
    time e il comportamento cambia con la dimensione del batch. LayerNorm
    normalizza ogni ESEMPIO sulle sue FEATURE: le statistiche sono locali alla
    riga, il risultato su un batch coincide esattamente con il risultato
    ottenuto elemento per elemento, e non esiste distinzione train/test. Per
    questo il Transformer usa LayerNorm: le sequenze hanno lunghezze diverse e
    il padding avvelenerebbe le statistiche di batch.
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 7. Blocco encoder del Transformer
# ---------------------------------------------------------------------------


def transformer_encoder_block(X, params, mask=None):
    """Un blocco encoder del Transformer, convenzione POST-LN.

        A = MultiHead(X, X)
        H = LayerNorm(X + A)                      <- residuo, poi norm
        F = ReLU(H W1 + b1) W2 + b2               <- feed-forward position-wise
        Y = LayerNorm(H + F)                      <- residuo, poi norm

    La prima LayerNorm usa ``gamma1``/``beta1``, la seconda ``gamma2``/``beta2``.
    La feed-forward e' position-wise: gli stessi pesi per ogni posizione, e
    nessun mescolamento fra posizioni.

    Parametri
    ---------
    X : (N, L, d_model)
    params : dict come quello prodotto da ``make_encoder_params``
    mask : booleana broadcastabile a (N, n_heads, L, L), True = da mascherare

    Ritorna
    -------
    (N, L, d_model)

    POST-LN vs PRE-LN
    -----------------
    Qui la LayerNorm sta DOPO la somma residua (post-LN, il paper originale):
    l'ultima operazione del blocco e' una normalizzazione, quindi l'output ha
    media 0 e varianza 1 sull'ultimo asse quando gamma=1, beta=0. Il prezzo e'
    che il cammino residuo non e' piu' un'identita' pura e i gradienti passano
    attraverso una LayerNorm a ogni blocco: reti profonde richiedono warmup del
    learning rate. La variante pre-LN normalizza l'INGRESSO dei sottomoduli
    (``X + MHA(LN(X))``), lascia il residuo pulito da un capo all'altro ed e'
    quella che si usa oggi per stack molto profondi.
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 8. Costo della self-attention
# ---------------------------------------------------------------------------


def attention_complexity(L, d):
    """Costo di una self-attention (batch 1, testa singola, lunghezza L, dim d).

    Convenzione di conteggio (una moltiplicazione + una somma = 2 FLOP):

        proiezioni Q, K, V, O : 4 * (2 L d d)  =  8 L d^2
        punteggi   Q K^T      :      2 L L d   =  2 L^2 d
        media pesata attn @ V :      2 L L d   =  2 L^2 d
        ----------------------------------------------------
        flops = 4 L^2 d + 8 L d^2

    Memoria, contata in numero di float vivi simultaneamente:

        matrice di attenzione : L^2
        Q, K, V               : 3 L d
        ----------------------------------------------------
        memoria = L^2 + 3 L d

    Il termine dominante per L >> d e' quadratico in L in ENTRAMBI i casi: e'
    il collo di bottiglia del Transformer sulle sequenze lunghe.

    Ritorna
    -------
    (flops_stimati, memoria_stimata), entrambi ``int``.
    """
    # TODO
    raise NotImplementedError
