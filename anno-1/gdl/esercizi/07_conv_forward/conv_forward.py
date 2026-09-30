"""Esercizio GDL15-16 - "Convolutional Neural Networks": forward di una CNN da zero.

Implementa le funzioni marcate `# TODO`.  Tutto il resto (l'oracolo lento
`conv2d_naive`, il generatore di parametri `make_lenet_params`) e' gia' fornito
e NON va toccato.

Vincoli
-------
Solo numpy + stdlib.  In particolare sono VIETATI `np.convolve`,
`np.correlate`, `scipy.signal`, `scipy.ndimage`, `torch`: la convoluzione la
scrivi tu.  Ogni sorgente di casualita' passa da un `rng`
(`numpy.random.Generator`): niente `np.random.seed`, niente `random`.

Convenzioni di layout (le stesse di PyTorch)
--------------------------------------------
  input   x        : (N, C_in, H, W)          NCHW
  kernel  weight   : (C_out, C_in, KH, KW)
  output           : (N, C_out, H_out, W_out)
  bias             : (C_out,)   oppure None

Tutti gli array sono `float`.  `stride`, `padding`, `dilation`, `kernel_size`
sono interi (stesso valore sulle due dimensioni spaziali).
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Oracolo fornito - NON modificare, NON e' parte dell'esercizio.
# ---------------------------------------------------------------------------


def conv2d_naive(x, weight, bias=None, stride=1, padding=0, dilation=1):
    """Cross-correlazione 2D scritta con quattro cicli Python annidati.

    Lenta e ovviamente corretta: e' la definizione trascritta, e serve come
    ORACOLO indipendente contro cui validare `conv2d`.  Non usarla dentro
    `conv2d` e non modificarla.

    Calcola, per ogni n, c_out, i, j:

        out[n, co, i, j] = bias[co]
                         + sum_{ci, u, v} weight[co, ci, u, v]
                                          * xpad[n, ci, i*s + u*d, j*s + v*d]

    dove `xpad` e' `x` con `padding` zeri per lato su H e W.

    Parametri
    ---------
    x : ndarray (N, C_in, H, W)
    weight : ndarray (C_out, C_in, KH, KW)
    bias : ndarray (C_out,) oppure None
    stride, padding, dilation : int

    Ritorna
    -------
    ndarray (N, C_out, H_out, W_out)
    """
    x = np.asarray(x, dtype=float)
    weight = np.asarray(weight, dtype=float)
    N, C_in, H, W = x.shape
    C_out, C_in_w, KH, KW = weight.shape
    if C_in != C_in_w:
        raise ValueError(f"canali incompatibili: x ha {C_in}, weight ne vuole {C_in_w}")

    Hp, Wp = H + 2 * padding, W + 2 * padding
    xpad = np.zeros((N, C_in, Hp, Wp), dtype=float)
    xpad[:, :, padding : padding + H, padding : padding + W] = x

    KH_eff = dilation * (KH - 1) + 1
    KW_eff = dilation * (KW - 1) + 1
    H_out = (Hp - KH_eff) // stride + 1
    W_out = (Wp - KW_eff) // stride + 1
    if H_out <= 0 or W_out <= 0:
        raise ValueError("configurazione degenere: output di dimensione nulla")

    out = np.zeros((N, C_out, H_out, W_out), dtype=float)
    for n in range(N):                      # 1
        for co in range(C_out):             # 2
            for i in range(H_out):          # 3
                for j in range(W_out):      # 4
                    i0, j0 = i * stride, j * stride
                    region = xpad[
                        n,
                        :,
                        i0 : i0 + KH_eff : dilation,
                        j0 : j0 + KW_eff : dilation,
                    ]
                    out[n, co, i, j] = float(np.sum(region * weight[co]))
    if bias is not None:
        out += np.asarray(bias, dtype=float).reshape(1, C_out, 1, 1)
    return out


def make_lenet_params(rng, in_channels=1, image_size=28, c1=4, c2=8, hidden=16,
                      n_classes=5, k=3, pool=2, scale=0.2):
    """Genera un dizionario di parametri COERENTE per `forward_lenet`.

    Fornito: serve solo a costruire dati di prova deterministici, non e' parte
    dell'esercizio.  Le convoluzioni usano padding `k // 2` (quindi la
    dimensione spaziale non cambia) e i pooling hanno stride pari a `pool`.

    Parametri
    ---------
    rng : numpy.random.Generator
    in_channels, image_size, c1, c2, hidden, n_classes, k, pool : int
    scale : float, deviazione standard dei pesi

    Ritorna
    -------
    dict con le chiavi documentate in `forward_lenet`.
    """
    p = k // 2
    h1 = (image_size + 2 * p - k) // 1 + 1      # dopo conv1
    h1 = (h1 - pool) // pool + 1                # dopo pool1
    h2 = (h1 + 2 * p - k) // 1 + 1              # dopo conv2
    h2 = (h2 - pool) // pool + 1                # dopo pool2
    flat = c2 * h2 * h2
    return {
        "conv1_w": scale * rng.standard_normal((c1, in_channels, k, k)),
        "conv1_b": scale * rng.standard_normal(c1),
        "conv2_w": scale * rng.standard_normal((c2, c1, k, k)),
        "conv2_b": scale * rng.standard_normal(c2),
        "fc1_w": scale * rng.standard_normal((hidden, flat)),
        "fc1_b": scale * rng.standard_normal(hidden),
        "fc2_w": scale * rng.standard_normal((n_classes, hidden)),
        "fc2_b": scale * rng.standard_normal(n_classes),
        "conv1_padding": p,
        "conv2_padding": p,
        "pool_size": pool,
        "pool_stride": pool,
    }


# ---------------------------------------------------------------------------
# 1. Geometria: le due formule che devi sapere a memoria.
# ---------------------------------------------------------------------------


def output_shape(H, K, stride=1, padding=0, dilation=1):
    """Dimensione spaziale in uscita da una convoluzione (o da un pooling).

        H_out = floor( (H + 2*padding - dilation*(K - 1) - 1) / stride ) + 1

    Il termine `dilation*(K-1) + 1` e' il kernel EFFETTIVO: un kernel 3x3 con
    dilation 2 copre 5 pixel, ma ne usa solo 3.

    Parametri
    ---------
    H : int    dimensione di ingresso lungo un asse spaziale
    K : int    dimensione del kernel lungo quello stesso asse
    stride, padding, dilation : int (>= 1, >= 0, >= 1)

    Ritorna
    -------
    int (>= 1 per configurazioni valide)
    """
    # TODO
    raise NotImplementedError


def receptive_field(layers):
    """Campo recettivo complessivo di una pila di layer, lungo un asse.

    `layers` e' una sequenza di triple `(kernel_size, stride, dilation)`, dal
    layer piu' vicino all'input a quello piu' vicino all'output.  Il valore
    restituito e' il numero di pixel di input che influenzano UN pixel di
    output.

    Ricorrenza (r = campo recettivo corrente, j = "jump", cioe' di quanti pixel
    di input ci si sposta quando ci si sposta di 1 pixel su questo layer):

        r = 1, j = 1
        per ogni layer (k, s, d):
            k_eff = d * (k - 1) + 1
            r = r + (k_eff - 1) * j
            j = j * s

    Il padding NON compare: sposta la posizione del campo recettivo, non la sua
    ampiezza.

    Parametri
    ---------
    layers : sequenza di tuple (int, int, int)

    Ritorna
    -------
    int.  Con `layers` vuota vale 1 (l'identita' vede un solo pixel).
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 2. Convoluzione
# ---------------------------------------------------------------------------


def pad2d(x, pad):
    """Zero-padding simmetrico sulle sole dimensioni spaziali.

    Parametri
    ---------
    x : ndarray (N, C, H, W)
    pad : int >= 0, numero di zeri aggiunti PER LATO su H e su W

    Ritorna
    -------
    ndarray (N, C, H + 2*pad, W + 2*pad), nuovo array (mai una vista su `x`).
    Con `pad == 0` restituisce comunque una copia.
    """
    # TODO
    raise NotImplementedError


def im2col(x, KH, KW, stride=1, padding=0, dilation=1):
    """Matrice delle patch: ogni COLONNA e' una finestra di input appiattita.

    E' la trasformazione che riduce la convoluzione a un prodotto matriciale.

    Parametri
    ---------
    x : ndarray (N, C, H, W)
    KH, KW : int, dimensioni del kernel
    stride, padding, dilation : int

    Ritorna
    -------
    ndarray di shape `(C * KH * KW, N * H_out * W_out)`, dove `H_out` e `W_out`
    vengono da `output_shape`.

    Convenzioni di indicizzazione, da rispettare ALLA LETTERA (i test le
    verificano, e sono quelle che rendono corretto il prodotto con
    `weight.reshape(C_out, -1)`):

      riga    (c, u, v)  ->  (c * KH + u) * KW + v        [ordine C-major]
      colonna (n, i, j)  ->  (n * H_out + i) * W_out + j  [ordine C-major]

    e l'elemento corrispondente vale

        cols[(c*KH + u)*KW + v, (n*H_out + i)*W_out + j]
            = xpad[n, c, i*stride + u*dilation, j*stride + v*dilation]

    con `xpad = pad2d(x, padding)`.
    """
    # TODO
    raise NotImplementedError


def conv2d(x, weight, bias=None, stride=1, padding=0, dilation=1):
    """Cross-correlazione 2D, via `im2col` + UN SOLO prodotto matriciale.

    Deve produrre esattamente lo stesso risultato di `conv2d_naive` (che e' la
    definizione scritta a cicli), ma senza cicli sui pixel: costruisci la
    matrice delle patch con `im2col`, appiattisci `weight` in una matrice
    `(C_out, C_in*KH*KW)`, moltiplica una volta sola e rimetti in forma.

    ATTENZIONE: come in PyTorch questa e' la CROSS-CORRELAZIONE

        out[n, co, i, j] = sum_{ci,u,v} w[co,ci,u,v] * xpad[n,ci, i*s+u*d, j*s+v*d]

    e NON la convoluzione matematica, che avrebbe il kernel ribaltato
    (`w[co,ci,KH-1-u,KW-1-v]`).  Vedi il README.

    Parametri
    ---------
    x : ndarray (N, C_in, H, W)
    weight : ndarray (C_out, C_in, KH, KW)
    bias : ndarray (C_out,) oppure None
    stride, padding, dilation : int

    Ritorna
    -------
    ndarray (N, C_out, H_out, W_out)

    Vietato: `np.convolve`, `np.correlate`, `scipy`, e chiamare `conv2d_naive`.
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 3. Pooling
# ---------------------------------------------------------------------------


def max_pool2d(x, kernel_size, stride=None, padding=0):
    """Max pooling 2D, finestre quadrate.

    Parametri
    ---------
    x : ndarray (N, C, H, W)
    kernel_size : int
    stride : int oppure None.  Se None vale `kernel_size` (finestre disgiunte:
        e' il default di PyTorch e la ragione per cui il pooling dimezza).
    padding : int >= 0

    Ritorna
    -------
    ndarray (N, C, H_out, W_out) con le dimensioni date da `output_shape`
    (dilation = 1).

    IMPORTANTE: il padding del max pooling e' a `-inf`, non a zero.  `-inf` e'
    l'elemento neutro del massimo, come `0` lo e' della somma; con zeri, un
    input tutto negativo produrrebbe uno spurio `0` sui bordi.
    """
    # TODO
    raise NotImplementedError


def avg_pool2d(x, kernel_size, stride=None, padding=0):
    """Average pooling 2D, finestre quadrate.

    Stesse convenzioni di `max_pool2d`, ma il padding e' a ZERO e le celle di
    padding CONTANO nel denominatore: si divide sempre per `kernel_size**2`
    (equivale a `count_include_pad=True`, il default di PyTorch).

    Parametri
    ---------
    x : ndarray (N, C, H, W)
    kernel_size : int
    stride : int oppure None (None -> `kernel_size`)
    padding : int >= 0

    Ritorna
    -------
    ndarray (N, C, H_out, W_out)
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 4. Il resto della pipeline
# ---------------------------------------------------------------------------


def relu(x):
    """ReLU elemento per elemento: max(x, 0).  Shape invariata."""
    # TODO
    raise NotImplementedError


def batchnorm2d_inference(x, gamma, beta, running_mean, running_var, eps=1e-5):
    """BatchNorm 2D in INFERENZA: statistiche per canale, gia' stimate.

        y[n, c, i, j] = gamma[c] * (x[n,c,i,j] - mu[c]) / sqrt(var[c] + eps)
                        + beta[c]

    In inferenza NON si ricalcola nulla dal batch: si usano le statistiche
    accumulate durante il training.  E' la ragione per cui il forward diventa
    una trasformazione affine fissa per canale (e si puo' fondere nel kernel
    della convoluzione precedente).

    Parametri
    ---------
    x : ndarray (N, C, H, W)
    gamma, beta, running_mean, running_var : ndarray (C,)
    eps : float

    Ritorna
    -------
    ndarray (N, C, H, W)
    """
    # TODO
    raise NotImplementedError


def flatten(x):
    """Appiattisce le mappe di attivazione mantenendo la dimensione di batch.

    Parametri
    ---------
    x : ndarray (N, C, H, W)

    Ritorna
    -------
    ndarray (N, C*H*W), in ordine C-major: l'indice che scorre piu' in fretta
    e' W, poi H, poi C.  E' lo stesso ordine di `torch.flatten(x, 1)` su un
    tensore contiguo, e deve essere coerente con il modo in cui sono ordinate
    le colonne di `fc1_w`.
    """
    # TODO
    raise NotImplementedError


def linear(x, weight, bias=None):
    """Layer completamente connesso: y = x @ weight.T + bias.

    Parametri
    ---------
    x : ndarray (N, in_features)
    weight : ndarray (out_features, in_features)   <- nota l'ordine, e' quello
        di `torch.nn.Linear.weight`
    bias : ndarray (out_features,) oppure None

    Ritorna
    -------
    ndarray (N, out_features)
    """
    # TODO
    raise NotImplementedError


def forward_lenet(x, params):
    """Forward completo di una CNN in stile LeNet.

    Sequenza esatta:

        conv1 -> relu -> max_pool
        conv2 -> relu -> max_pool
        flatten
        fc1 -> relu
        fc2                       (nessuna attivazione finale: sono logit)

    Parametri
    ---------
    x : ndarray (N, C_in, H, W)
    params : dict con chiavi

        obbligatorie
          "conv1_w" : (C1, C_in, K1, K1)      "conv1_b" : (C1,) o None
          "conv2_w" : (C2, C1, K2, K2)        "conv2_b" : (C2,) o None
          "fc1_w"   : (Hh, C2*H2*W2)          "fc1_b"   : (Hh,) o None
          "fc2_w"   : (n_classes, Hh)         "fc2_b"   : (n_classes,) o None

        opzionali (con i rispettivi default)
          "conv1_padding" : int, default 0
          "conv2_padding" : int, default 0
          "conv1_stride"  : int, default 1
          "conv2_stride"  : int, default 1
          "pool_size"     : int, default 2
          "pool_stride"   : int, default = "pool_size"

    Ritorna
    -------
    ndarray (N, n_classes), i logit.

    Usa le funzioni che hai appena scritto: e' il punto dell'esercizio.
    """
    # TODO
    raise NotImplementedError
