"""Soluzione di riferimento - GDL27-28 "Tractable density models: Normalizing Flows".

Convenzione di direzione (la stessa dello skeleton, si veda il README):

    f : x -> z     direzione NORMALIZZANTE, qui `flow_forward`
    f^-1 : z -> x  direzione GENERATIVA,    qui `flow_inverse`

    log P(x) = log P(f(x)) + log |det J_x f|

che e' esattamente la formula della slide "Designing scalable flows".
"""

from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Utilita' fornite - identiche allo skeleton.
# ---------------------------------------------------------------------------


def softplus(a):
    """softplus(a) = log(1 + exp(a)), implementazione numericamente stabile."""
    a = np.asarray(a, dtype=float)
    return np.logaddexp(0.0, a)


def standard_normal_logpdf(z):
    """log P(z) = -0.5 ||z||^2 - (D/2) log(2 pi), per z di shape (N, D) -> (N,)."""
    z = np.asarray(z, dtype=float)
    D = z.shape[-1]
    return -0.5 * np.sum(z * z, axis=-1) - 0.5 * D * np.log(2.0 * np.pi)


def alternating_mask(D, parity):
    """Maschera a scacchiera, shape (D,): 1 = copiata, 0 = trasformata."""
    mask = np.zeros(D, dtype=float)
    mask[parity % 2 :: 2] = 1.0
    return mask


def random_coupling_params(D, hidden, rng, w_scale=0.35):
    """Pesi casuali delle due MLP (log-scala theta_A e traslazione theta_B)."""
    out_scale = w_scale / np.sqrt(hidden)
    p = {}
    for tag in ("s", "t"):
        p["W1" + tag] = w_scale * rng.standard_normal((D, hidden))
        p["b1" + tag] = w_scale * rng.standard_normal(hidden)
        p["W2" + tag] = out_scale * rng.standard_normal((hidden, D))
        p["b2" + tag] = out_scale * rng.standard_normal(D)
    return p


def make_flow(D, n_layers, rng, hidden=6, w_scale=0.35):
    """Flusso di ``n_layers`` coupling con maschere alternate."""
    return [
        {
            "params": random_coupling_params(D, hidden, rng, w_scale),
            "mask": alternating_mask(D, i),
        }
        for i in range(n_layers)
    ]


def mlp(x, W1, b1, W2, b2):
    """MLP D -> hidden -> D: tanh sullo strato nascosto, uscita lineare."""
    return np.tanh(x @ W1 + b1) @ W2 + b2


# ---------------------------------------------------------------------------
# 1. Coupling layer affine (RealNVP)
# ---------------------------------------------------------------------------


def _coupling_st(x, params, mask):
    """(log_scale, shift), entrambi shape (N, D), funzione della sola meta' mascherata.

    Il punto centrale del coupling: l'ingresso delle due reti e' ``mask * x``,
    cioe' la meta' che passa identica. Le componenti da trasformare sono
    azzerate e non influenzano ne' la scala ne' la traslazione. E' questo che
    rende lo Jacobiano triangolare a blocchi e l'inversa esplicita.
    """
    x = np.asarray(x, dtype=float)
    mask = np.asarray(mask, dtype=float)
    xm = mask * x  # la "b (*) z" della slide RealNVP
    log_s = mlp(xm, params["W1s"], params["b1s"], params["W2s"], params["b2s"])
    t = mlp(xm, params["W1t"], params["b1t"], params["W2t"], params["b2t"])
    return log_s, t


def affine_coupling_forward(x, params, mask):
    """y = b (*) x + (1 - b) (*) { exp(theta_A(b (*) x)) (*) x + theta_B(b (*) x) }."""
    x = np.asarray(x, dtype=float)
    mask = np.asarray(mask, dtype=float)
    log_s, t = _coupling_st(x, params, mask)
    return mask * x + (1.0 - mask) * (np.exp(log_s) * x + t)


def affine_coupling_inverse(y, params, mask):
    """x = b (*) y + (1 - b) (*) (y - theta_B(b (*) y)) * exp(-theta_A(b (*) y)).

    Si sfrutta ``mask * y == mask * x``: le reti si rivalutano sullo stesso
    identico input del forward, quindi ``log_s`` e ``t`` sono gli stessi e
    l'inversione e' un'operazione elementare, non un problema di punto fisso.
    """
    y = np.asarray(y, dtype=float)
    mask = np.asarray(mask, dtype=float)
    log_s, t = _coupling_st(y, params, mask)
    return mask * y + (1.0 - mask) * ((y - t) * np.exp(-log_s))


def affine_coupling_log_det(x, params, mask):
    """Somma dei log_scale sulle sole dimensioni trasformate (mask == 0).

    Lo Jacobiano, riordinando le coordinate in [copiate | trasformate], e'

        [ I                       0                     ]
        [ d(exp(s) x + t)/dx_1    diag(exp(log_scale))   ]

    triangolare a blocchi: il determinante e' il prodotto della diagonale e il
    blocco in basso a sinistra (le derivate delle due reti) non entra affatto.
    La traslazione theta_B non compare: traslare non cambia i volumi.
    """
    mask = np.asarray(mask, dtype=float)
    log_s, _ = _coupling_st(x, params, mask)
    return np.sum((1.0 - mask) * log_s, axis=-1)


# ---------------------------------------------------------------------------
# 2. Composizione dei layer
# ---------------------------------------------------------------------------


def flow_forward(x, layers):
    """x -> z: layer applicati NELL'ORDINE della lista."""
    z = np.asarray(x, dtype=float)
    for layer in layers:
        z = affine_coupling_forward(z, layer["params"], layer["mask"])
    return z


def flow_inverse(z, layers):
    """z -> x: layer applicati in ordine INVERSO, ciascuno con la sua inversa."""
    x = np.asarray(z, dtype=float)
    for layer in reversed(layers):
        x = affine_coupling_inverse(x, layer["params"], layer["mask"])
    return x


def flow_log_det(x, layers):
    """Somma dei log-det, ognuno valutato SULL'INGRESSO DEL PROPRIO LAYER.

    Trappola classica: valutare tutti i log-det in x. Il log-det del layer i va
    calcolato in z_{i-1}, cioe' sul valore che il layer i riceve davvero.
    Per questo stato e accumulatore avanzano insieme.
    """
    z = np.asarray(x, dtype=float)
    total = np.zeros(z.shape[0], dtype=float)
    for layer in layers:
        total = total + affine_coupling_log_det(z, layer["params"], layer["mask"])
        z = affine_coupling_forward(z, layer["params"], layer["mask"])
    return total


# ---------------------------------------------------------------------------
# 3. Densita' esplicita e campionamento
# ---------------------------------------------------------------------------


def log_prob(x, layers):
    """log P(x) = log P(f(x)) + log |det J_x f|, con P(z) = N(0, I).

    Segno PIU' perche' f e' la direzione normalizzante x -> z. Se si usasse la
    direzione generativa il segno sarebbe meno: e' l'errore che produce una
    "densita'" che integra a un valore diverso da 1.
    """
    z = flow_forward(x, layers)
    return standard_normal_logpdf(z) + flow_log_det(x, layers)


def sample(layers, n, rng):
    """z ~ N(0, I), poi direzione generativa f^-1. Nessuna catena, nessun rifiuto."""
    D = int(np.asarray(layers[0]["mask"]).shape[0])
    z = rng.standard_normal((n, D))
    return flow_inverse(z, layers)


# ---------------------------------------------------------------------------
# 4. Flusso planare (Rezende & Mohamed 2015)
# ---------------------------------------------------------------------------


def planar_flow_forward(x, u, w, b):
    """f(x) = x + u * h(w^T x + b), con h = tanh."""
    x = np.asarray(x, dtype=float)
    u = np.asarray(u, dtype=float)
    w = np.asarray(w, dtype=float)
    a = x @ w + b  # (N,)
    return x + np.outer(np.tanh(a), u)


def planar_flow_log_det(x, u, w, b):
    """log(1 + u^T psi(x)), con psi(x) = h'(w^T x + b) * w e h' = 1 - tanh^2.

    Lo Jacobiano e' I + u psi(x)^T, aggiornamento di rango 1: per il lemma del
    determinante matriciale det(I + u psi^T) = 1 + psi^T u. Costo O(D), senza
    mai costruire la matrice D x D.

    Il logaritmo e' senza valore assoluto di proposito: se il flusso e'
    invertibile l'argomento e' positivo; se esce negativo il NaN e' il segnale
    che quella trasformazione non e' una bigezione.
    """
    x = np.asarray(x, dtype=float)
    u = np.asarray(u, dtype=float)
    w = np.asarray(w, dtype=float)
    a = x @ w + b
    hprime = 1.0 - np.tanh(a) ** 2  # h'(a), in (0, 1]
    psi = hprime[:, None] * w[None, :]  # (N, D)
    return np.log(1.0 + psi @ u)


def enforce_invertibility(u, w):
    """u_hat = u + (m(w^T u) - w^T u) * w / ||w||^2, con m(a) = -1 + softplus(a).

    Si sposta u lungo w esattamente quanto basta perche' la proiezione su w
    valga m(w^T u) >= -1, lasciando intatta la componente ortogonale a w
    (quella non influenza il determinante).

    Poi, poiche' h' = 1 - tanh^2 sta in (0, 1]:
        1 + u_hat^T psi(x) = 1 + h' (w^T u_hat)
    che vale >= 1 se w^T u_hat >= 0, e >= 1 + w^T u_hat >= 0 altrimenti.
    """
    u = np.asarray(u, dtype=float)
    w = np.asarray(w, dtype=float)
    a = float(w @ u)
    m = -1.0 + float(softplus(a))
    return u + (m - a) * w / float(w @ w)
