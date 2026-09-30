"""Soluzione di riferimento - GDL19/GDL20 "Attention, cross-attention, Transformer".

Stessa identica API di ``attention.py``. Ogni funzione e' commentata con il
motivo per cui e' scritta cosi' e con l'errore che eviterebbe.

Solo numpy + stdlib.
"""

from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Utilita' fornite - identiche allo skeleton.
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
    lungo ``axis``.

    Se una fetta lungo ``axis`` e' interamente ``-inf`` (riga completamente
    mascherata) il risultato e' indefinito: qui si ottiene NaN. Non capita con
    ``causal_mask``; puo' capitare con ``padding_mask`` su lunghezza 0.
    """
    x = np.asarray(x, dtype=float)
    # Sottrarre il massimo e' la stabilizzazione: exp() non vede mai un
    # argomento positivo, quindi non puo' andare in overflow. Il risultato e'
    # invariante perche' softmax(x + c) = softmax(x).
    x_max = np.max(x, axis=axis, keepdims=True)
    # Se la fetta e' tutta -inf il massimo e' -inf e (-inf) - (-inf) = NaN.
    # Lo sostituiamo con 0 per non emettere warning: il risultato resta 0/0.
    x_max = np.where(np.isfinite(x_max), x_max, 0.0)
    e = np.exp(x - x_max)
    return e / np.sum(e, axis=axis, keepdims=True)


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
    h_dec = np.asarray(h_dec, dtype=float)
    H_enc = np.asarray(H_enc, dtype=float)
    Wa = np.asarray(Wa, dtype=float)
    Ua = np.asarray(Ua, dtype=float)
    va = np.asarray(va, dtype=float)

    # Il termine del decoder non dipende da i: si calcola una volta sola e si
    # somma per broadcasting. E' l'unica ragione per cui l'attenzione additiva
    # non e' assurdamente costosa.
    q = Wa @ h_dec                      # (d_attn,)
    k = H_enc @ Ua.T                    # (L, d_attn)
    return np.tanh(q[None, :] + k) @ va  # (L,)


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
    h_dec = np.asarray(h_dec, dtype=float)
    H_enc = np.asarray(H_enc, dtype=float)
    if Wa is None:
        if H_enc.shape[1] != h_dec.shape[0]:
            raise ValueError(
                "variante dot: d_enc e d_dec devono coincidere "
                f"({H_enc.shape[1]} != {h_dec.shape[0]}); usa la variante general"
            )
        return H_enc @ h_dec
    Wa = np.asarray(Wa, dtype=float)
    return H_enc @ (Wa @ h_dec)


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
    """
    Q = np.asarray(Q, dtype=float)
    K = np.asarray(K, dtype=float)
    V = np.asarray(V, dtype=float)
    d_k = Q.shape[-1]

    # swapaxes(-1, -2) e non .T: .T inverte TUTTI gli assi e rompe il batch.
    scores = np.matmul(Q, np.swapaxes(K, -1, -2)) / np.sqrt(d_k)

    if mask is not None:
        mask = np.asarray(mask, dtype=bool)
        # -inf PRIMA del softmax, non zero DOPO: azzerare i pesi dopo il
        # softmax lascerebbe la riga non normalizzata.
        scores = np.where(mask, -np.inf, scores)

    attn = softmax(scores, axis=-1)
    return np.matmul(attn, V), attn


def causal_mask(L):
    """Maschera causale (autoregressiva) di shape (L, L), booleana.

    ``mask[i, j] == True`` se e solo se ``j > i``: la query in posizione ``i``
    non puo' guardare le chiavi FUTURE. La diagonale resta visibile (la
    posizione guarda se stessa), quindi nessuna riga e' completamente
    mascherata.
    """
    return np.triu(np.ones((L, L), dtype=bool), k=1)


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
    lengths = np.asarray(lengths, dtype=int)
    return np.arange(L)[None, :] >= lengths[:, None]


# ---------------------------------------------------------------------------
# 4. Multi-head: split, merge, e l'unificazione self/cross
# ---------------------------------------------------------------------------


def split_heads(x, n_heads):
    """Da (N, L, d_model) a (N, n_heads, L, d_head), con d_head = d_model/n_heads.

    Le teste sono fette CONTIGUE dell'ultima dimensione: la testa h prende le
    colonne ``[h*d_head : (h+1)*d_head]``.
    """
    x = np.asarray(x, dtype=float)
    N, L, d_model = x.shape
    if d_model % n_heads != 0:
        raise ValueError(f"d_model={d_model} non divisibile per n_heads={n_heads}")
    d_head = d_model // n_heads
    # reshape POI transpose. L'ordine conta: reshape su (N, L, h, d_head)
    # separa le teste lungo l'ultima dimensione, che e' la convenzione voluta.
    return x.reshape(N, L, n_heads, d_head).transpose(0, 2, 1, 3)


def merge_heads(x):
    """Inversa esatta di ``split_heads``: da (N, n_heads, L, d_head) a (N, L, d_model)."""
    x = np.asarray(x, dtype=float)
    N, n_heads, L, d_head = x.shape
    # transpose POI reshape, in ordine inverso rispetto a split_heads.
    return x.transpose(0, 2, 1, 3).reshape(N, L, n_heads * d_head)


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
    Non c'e' nessuna differenza algoritmica. Se ``X_q is X_kv`` (o comunque se
    sono lo stesso tensore) la funzione calcola SELF-attention: ogni posizione
    interroga le altre posizioni della stessa sequenza, e necessariamente
    Lq == Lkv. Se ``X_q`` e ``X_kv`` sono tensori diversi la funzione calcola
    CROSS-attention: le query vengono dal decoder, chiavi e valori
    dall'encoder, e le due lunghezze sono indipendenti (Lq != Lkv e' normale).
    Questa unificazione e' il passaggio GDL19 -> GDL20: la cross-attention
    encoder-decoder di Bahdanau e la self-attention del Transformer sono lo
    stesso blocco, cambia solo CHI fornisce K e V. La lunghezza dell'output e'
    sempre Lq, mai Lkv: l'attenzione ricampiona la sorgente sulla griglia
    della destinazione.
    """
    X_q = np.asarray(X_q, dtype=float)
    X_kv = np.asarray(X_kv, dtype=float)

    Q = X_q @ np.asarray(Wq, dtype=float)     # (N, Lq,  d_model)
    K = X_kv @ np.asarray(Wk, dtype=float)    # (N, Lkv, d_model)
    V = X_kv @ np.asarray(Wv, dtype=float)    # (N, Lkv, d_model)

    Qh = split_heads(Q, n_heads)              # (N, H, Lq,  d_head)
    Kh = split_heads(K, n_heads)              # (N, H, Lkv, d_head)
    Vh = split_heads(V, n_heads)              # (N, H, Lkv, d_head)

    # Lo scaling usa d_head, non d_model: e' la dimensione effettiva su cui si
    # fa il prodotto scalare dentro ciascuna testa.
    Oh, attn = scaled_dot_product_attention(Qh, Kh, Vh, mask=mask)

    out = merge_heads(Oh) @ np.asarray(Wo, dtype=float)
    return out, attn


# ---------------------------------------------------------------------------
# 5. Positional encoding
# ---------------------------------------------------------------------------


def positional_encoding(L, d_model):
    """Positional encoding sinusoidale del paper "Attention is all you need".

        PE[pos, 2i]   = sin(pos / 10000^(2i / d_model))
        PE[pos, 2i+1] = cos(pos / 10000^(2i / d_model))

    Parametri
    ---------
    L : int, numero di posizioni
    d_model : int PARI

    Ritorna
    -------
    (L, d_model)
    """
    if d_model % 2 != 0:
        raise ValueError(f"d_model deve essere pari, ricevuto {d_model}")
    pos = np.arange(L, dtype=float)[:, None]              # (L, 1)
    i = np.arange(d_model // 2, dtype=float)[None, :]     # (1, d/2)
    # 10000^(-2i/d) calcolato in spazio log per non perdere precisione.
    inv_freq = np.exp(-(2.0 * i / d_model) * np.log(10000.0))
    ang = pos * inv_freq                                  # (L, d/2)
    pe = np.empty((L, d_model), dtype=float)
    pe[:, 0::2] = np.sin(ang)
    pe[:, 1::2] = np.cos(ang)
    return pe


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
    x = np.asarray(x, dtype=float)
    mu = np.mean(x, axis=-1, keepdims=True)
    var = np.mean((x - mu) ** 2, axis=-1, keepdims=True)
    xhat = (x - mu) / np.sqrt(var + eps)
    return xhat * np.asarray(gamma, dtype=float) + np.asarray(beta, dtype=float)


# ---------------------------------------------------------------------------
# 7. Blocco encoder del Transformer
# ---------------------------------------------------------------------------


def transformer_encoder_block(X, params, mask=None):
    """Un blocco encoder del Transformer, convenzione POST-LN.

        A = MultiHead(X, X)
        H = LayerNorm(X + A)                      <- residuo, poi norm
        F = ReLU(H W1 + b1) W2 + b2               <- feed-forward position-wise
        Y = LayerNorm(H + F)                      <- residuo, poi norm

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
    X = np.asarray(X, dtype=float)
    n_heads = params["n_heads"]

    # Sotto-blocco 1: self-attention. X e' insieme query e key/value: e' cio'
    # che rende la funzione self-attention e non cross-attention.
    A, _ = multi_head_attention(
        X, X, params["Wq"], params["Wk"], params["Wv"], params["Wo"], n_heads, mask=mask
    )
    H = layer_norm(X + A, params["gamma1"], params["beta1"])

    # Sotto-blocco 2: feed-forward applicata POSIZIONE PER POSIZIONE (gli
    # stessi pesi per ogni t). Non mescola le posizioni: tutto il mescolamento
    # avviene nell'attenzione. E' anche il motivo per cui la causalita'
    # sopravvive al passaggio nella FFN.
    F = relu(H @ params["W1"] + params["b1"]) @ params["W2"] + params["b2"]
    return layer_norm(H + F, params["gamma2"], params["beta2"])


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
    L = int(L)
    d = int(d)
    flops = 4 * L * L * d + 8 * L * d * d
    memoria = L * L + 3 * L * d
    return int(flops), int(memoria)
