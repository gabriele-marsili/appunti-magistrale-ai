"""Soluzione di riferimento - GDL15-16 "Convolutional Neural Networks".

Stessa identica API di `conv_forward.py`.  Solo numpy: nessun `np.convolve`,
nessun `scipy`.
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Oracolo fornito - identico allo skeleton.
# ---------------------------------------------------------------------------


def conv2d_naive(x, weight, bias=None, stride=1, padding=0, dilation=1):
    """Cross-correlazione 2D scritta con quattro cicli Python annidati.

    Lenta e ovviamente corretta: e' la definizione trascritta, e serve come
    ORACOLO indipendente contro cui validare `conv2d`.

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
    """Genera un dizionario di parametri COERENTE per `forward_lenet`."""
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
# 1. Geometria
# ---------------------------------------------------------------------------


def output_shape(H, K, stride=1, padding=0, dilation=1):
    """floor((H + 2p - d*(K-1) - 1)/s) + 1.

    Il kernel effettivo e' `d*(K-1) + 1`: la dilation allarga il supporto senza
    aggiungere parametri.  La divisione e' un floor: quando il passo non e'
    commensurabile con la dimensione, gli ultimi pixel vengono semplicemente
    scartati (non c'e' nessuna finestra parziale).
    """
    K_eff = dilation * (K - 1) + 1
    num = H + 2 * padding - K_eff
    if num < 0:
        raise ValueError(
            f"kernel effettivo {K_eff} piu' grande dell'input paddato {H + 2*padding}"
        )
    return num // stride + 1


def receptive_field(layers):
    """Campo recettivo lungo un asse, per una pila di layer.

    r e' l'ampiezza corrente, j il "jump" (passo in pixel di input corrispondente
    a un passo di 1 pixel sull'uscita del layer corrente).  Ogni layer aggiunge
    `(k_eff - 1)` posizioni, ciascuna larga `j` pixel di input; poi il proprio
    stride moltiplica il jump per i layer successivi.
    """
    r = 1
    j = 1
    for k, s, d in layers:
        k_eff = d * (k - 1) + 1
        r = r + (k_eff - 1) * j
        j = j * s
    return int(r)


# ---------------------------------------------------------------------------
# 2. Convoluzione
# ---------------------------------------------------------------------------


def pad2d(x, pad):
    """Zero-padding sulle sole dimensioni spaziali; restituisce sempre un nuovo array."""
    x = np.asarray(x, dtype=float)
    N, C, H, W = x.shape
    if pad == 0:
        return x.copy()
    out = np.zeros((N, C, H + 2 * pad, W + 2 * pad), dtype=float)
    out[:, :, pad : pad + H, pad : pad + W] = x
    return out


def im2col(x, KH, KW, stride=1, padding=0, dilation=1):
    """Matrice delle patch, shape (C*KH*KW, N*H_out*W_out).

    Il ciclo e' sui KH*KW offset del kernel (poche iterazioni, indipendenti
    dalla dimensione dell'immagine), non sui pixel: per ogni offset (u, v) si
    estrae in un colpo solo, con uno slicing strided, il pixel che quel peso
    incontra in TUTTE le finestre.  Questo e' il punto: lo stride della
    convoluzione diventa lo step di uno slice numpy.
    """
    x = np.asarray(x, dtype=float)
    N, C, H, W = x.shape
    H_out = output_shape(H, KH, stride, padding, dilation)
    W_out = output_shape(W, KW, stride, padding, dilation)

    xpad = pad2d(x, padding)
    cols = np.empty((C * KH * KW, N * H_out * W_out), dtype=float)
    for u in range(KH):
        u0 = u * dilation
        for v in range(KW):
            v0 = v * dilation
            # (N, C, H_out, W_out): il pixel visto dal peso (u, v) in ogni finestra
            patch = xpad[
                :,
                :,
                u0 : u0 + stride * H_out : stride,
                v0 : v0 + stride * W_out : stride,
            ]
            # -> (C, N*H_out*W_out): il canale diventa la riga, il resto la colonna
            rows = np.arange(C) * (KH * KW) + u * KW + v
            cols[rows, :] = patch.transpose(1, 0, 2, 3).reshape(C, -1)
    return cols


def conv2d(x, weight, bias=None, stride=1, padding=0, dilation=1):
    """Cross-correlazione 2D via im2col + un singolo prodotto matriciale.

    Tutta la convoluzione e' `W_mat @ cols`.  Il resto e' contabilita' di
    indici: `out` esce come (C_out, N*H_out*W_out) e va rimesso in NCHW.
    """
    x = np.asarray(x, dtype=float)
    weight = np.asarray(weight, dtype=float)
    N, C_in, H, W = x.shape
    C_out, C_in_w, KH, KW = weight.shape
    if C_in != C_in_w:
        raise ValueError(f"canali incompatibili: x ha {C_in}, weight ne vuole {C_in_w}")

    H_out = output_shape(H, KH, stride, padding, dilation)
    W_out = output_shape(W, KW, stride, padding, dilation)

    cols = im2col(x, KH, KW, stride, padding, dilation)   # (C_in*KH*KW, N*H_out*W_out)
    W_mat = weight.reshape(C_out, C_in * KH * KW)         # stesso ordine C-major
    out = W_mat @ cols                                    # <- il prodotto, uno solo

    out = out.reshape(C_out, N, H_out, W_out).transpose(1, 0, 2, 3)
    out = np.ascontiguousarray(out)
    if bias is not None:
        out += np.asarray(bias, dtype=float).reshape(1, C_out, 1, 1)
    return out


# ---------------------------------------------------------------------------
# 3. Pooling
# ---------------------------------------------------------------------------


def _pool_geometry(x, kernel_size, stride, padding):
    """Shape di uscita + stride effettivo, comune a max e avg."""
    if stride is None:
        stride = kernel_size
    N, C, H, W = x.shape
    H_out = output_shape(H, kernel_size, stride, padding, 1)
    W_out = output_shape(W, kernel_size, stride, padding, 1)
    return stride, N, C, H_out, W_out


def max_pool2d(x, kernel_size, stride=None, padding=0):
    """Max pooling con padding a -inf (elemento neutro del massimo)."""
    x = np.asarray(x, dtype=float)
    stride, N, C, H_out, W_out = _pool_geometry(x, kernel_size, stride, padding)
    H, W = x.shape[2], x.shape[3]

    xpad = np.full((N, C, H + 2 * padding, W + 2 * padding), -np.inf, dtype=float)
    xpad[:, :, padding : padding + H, padding : padding + W] = x

    out = np.full((N, C, H_out, W_out), -np.inf, dtype=float)
    for u in range(kernel_size):
        for v in range(kernel_size):
            out = np.maximum(
                out,
                xpad[
                    :,
                    :,
                    u : u + stride * H_out : stride,
                    v : v + stride * W_out : stride,
                ],
            )
    return out


def avg_pool2d(x, kernel_size, stride=None, padding=0):
    """Average pooling con padding a zero, contato nel denominatore."""
    x = np.asarray(x, dtype=float)
    stride, N, C, H_out, W_out = _pool_geometry(x, kernel_size, stride, padding)

    xpad = pad2d(x, padding)
    acc = np.zeros((N, C, H_out, W_out), dtype=float)
    for u in range(kernel_size):
        for v in range(kernel_size):
            acc += xpad[
                :,
                :,
                u : u + stride * H_out : stride,
                v : v + stride * W_out : stride,
            ]
    return acc / float(kernel_size * kernel_size)


# ---------------------------------------------------------------------------
# 4. Il resto della pipeline
# ---------------------------------------------------------------------------


def relu(x):
    """max(x, 0) elemento per elemento."""
    return np.maximum(np.asarray(x, dtype=float), 0.0)


def batchnorm2d_inference(x, gamma, beta, running_mean, running_var, eps=1e-5):
    """Affine per canale con le statistiche accumulate: broadcast su (1, C, 1, 1)."""
    x = np.asarray(x, dtype=float)
    C = x.shape[1]
    g = np.asarray(gamma, dtype=float).reshape(1, C, 1, 1)
    b = np.asarray(beta, dtype=float).reshape(1, C, 1, 1)
    mu = np.asarray(running_mean, dtype=float).reshape(1, C, 1, 1)
    var = np.asarray(running_var, dtype=float).reshape(1, C, 1, 1)
    return g * (x - mu) / np.sqrt(var + eps) + b


def flatten(x):
    """(N, C, H, W) -> (N, C*H*W), ordine C-major (W scorre piu' in fretta)."""
    x = np.asarray(x, dtype=float)
    return x.reshape(x.shape[0], -1)


def linear(x, weight, bias=None):
    """y = x @ weight.T + bias, con weight di shape (out, in)."""
    x = np.asarray(x, dtype=float)
    weight = np.asarray(weight, dtype=float)
    out = x @ weight.T
    if bias is not None:
        out = out + np.asarray(bias, dtype=float).reshape(1, -1)
    return out


def forward_lenet(x, params):
    """conv-relu-pool, conv-relu-pool, flatten, linear-relu, linear."""
    pool_k = int(params.get("pool_size", 2))
    pool_s = params.get("pool_stride", pool_k)

    h = conv2d(
        x,
        params["conv1_w"],
        params.get("conv1_b"),
        stride=int(params.get("conv1_stride", 1)),
        padding=int(params.get("conv1_padding", 0)),
    )
    h = relu(h)
    h = max_pool2d(h, pool_k, pool_s)

    h = conv2d(
        h,
        params["conv2_w"],
        params.get("conv2_b"),
        stride=int(params.get("conv2_stride", 1)),
        padding=int(params.get("conv2_padding", 0)),
    )
    h = relu(h)
    h = max_pool2d(h, pool_k, pool_s)

    h = flatten(h)
    h = relu(linear(h, params["fc1_w"], params.get("fc1_b")))
    return linear(h, params["fc2_w"], params.get("fc2_b"))
