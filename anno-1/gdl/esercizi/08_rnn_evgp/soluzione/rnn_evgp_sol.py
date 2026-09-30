"""
SOLUZIONE DI RIFERIMENTO — RNN vanilla, BPTT, exploding/vanishing gradient.
GDL17 "Information Propagation in Deep Networks", corso Generative and Deep
Learning (UNIPI, Bacciu).

Convenzioni (identiche allo skeleton, ripetute perche' sono meta' del lavoro):

  X    (T, D)      X[i] = input al timestep i,  i = 0..T-1
  H    (T+1, Hdim) H[i] = stato DOPO aver processato i timestep.
                   H[0] = stato iniziale (nullo in rnn_forward).
  A    (T, Hdim)   A[i] = pre-attivato del timestep i:
                          A[i] = Whh @ H[i] + Wxh @ X[i] + bh
                   e quindi                H[i+1] = tanh(A[i]).
  Y    (T, O)      Y[i] = Why @ H[i+1] + by

  Wxh (Hdim, D)   Whh (Hdim, Hdim)   bh (Hdim,)
  Why (O, Hdim)   by  (O,)

Lo sfasamento di uno fra H e (X, A, Y) e' l'unica cosa da tenere a mente:
X[i], A[i], Y[i] parlano dello STESSO timestep, H[i] e' lo stato PRIMA e
H[i+1] lo stato DOPO quel timestep.

La jacobiana della ricorrenza e'

    dH[i+1]/dH[i] = diag(tanh'(A[i])) @ Whh

e tutto l'EVGP e' contenuto nel prodotto di queste jacobiane lungo la
sequenza: il fattore diag(tanh'(...)) ha entrate in (0, 1], quindi puo' solo
ATTENUARE cio' che Whh fa. rho(Whh) < 1 => vanishing garantito;
rho(Whh) > 1 => vanishing NON garantito, ma esplosione possibile;
rho(Whh) = 1 => con tanh si vanish comunque. Condizione necessaria, non
sufficiente.
"""

from __future__ import annotations

import numpy as np

# Ordine canonico dei parametri: serve a impacchettarli in un vettore piatto
# per il gradient check.
PARAM_KEYS = ("Wxh", "Whh", "bh", "Why", "by")


# =============================================================================
# CODICE GIA' FORNITO NELLO SKELETON — non e' l'esercizio
# =============================================================================


def numerical_gradient(f, theta, eps=1e-5):
    """Gradiente per differenze finite centrali. ORACOLO del gradient check.

    Parametri
    ---------
    f : callable
        ``f(theta) -> float``. Deve accettare un ndarray della stessa shape di
        ``theta`` e restituire uno scalare (la loss).
    theta : ndarray, shape qualsiasi
        punto in cui valutare il gradiente. NON viene modificato.
    eps : float
        passo delle differenze finite.

    Ritorna
    -------
    ndarray della stessa shape di ``theta``, con
    ``g[i] = (f(theta + eps e_i) - f(theta - eps e_i)) / (2 eps)``.

    L'errore delle differenze centrali e' O(eps^2) di troncamento piu'
    O(eps_macchina / eps) di cancellazione: con eps=1e-5 si sta intorno a
    1e-10 assoluto, che basta per un confronto a rtol=1e-5.
    """
    theta = np.array(theta, dtype=float)  # copia: non tocchiamo l'originale
    grad = np.zeros_like(theta)
    it = np.nditer(theta, flags=["multi_index"])
    while not it.finished:
        idx = it.multi_index
        old = theta[idx]
        theta[idx] = old + eps
        f_plus = float(f(theta))
        theta[idx] = old - eps
        f_minus = float(f(theta))
        theta[idx] = old
        grad[idx] = (f_plus - f_minus) / (2.0 * eps)
        it.iternext()
    return grad


def make_copy_task(T, n_symbols, seed):
    """Copy task classico: memorizza n_symbols simboli, ripetili in fondo.

    L'alfabeto ha ``n_symbols`` simboli piu' due token speciali: BLANK
    (indice ``n_symbols``) e DELIMITER / "go" (indice ``n_symbols + 1``).

    Struttura della sequenza (lunghezza T, richiede ``T >= 2*n_symbols + 1``):

        step 0 .. S-1         i simboli da memorizzare (one-hot)
        step S .. T-S-2       BLANK
        step T-S-1            DELIMITER: "adesso ripetili"
        step T-S .. T-1       BLANK

    con ``S = n_symbols``. Il target e' BLANK-output fino allo step T-S-1
    incluso, poi i simboli memorizzati nello stesso ordine.

    E' il banco di prova canonico della dipendenza a lungo termine: per
    rispondere al passo T-1 la rete deve ricordare l'input del passo 0, cioe'
    il gradiente deve sopravvivere a T passi di BPTT.

    Parametri
    ---------
    T : int, lunghezza della sequenza.
    n_symbols : int, cardinalita' dell'alfabeto (e numero di simboli da copiare).
    seed : int, seed per ``np.random.default_rng``.

    Ritorna
    -------
    X : ndarray (T, n_symbols + 2), one-hot, dtype float.
    targets : ndarray (T, n_symbols + 1), one-hot, dtype float.
    """
    S = int(n_symbols)
    T = int(T)
    if T < 2 * S + 1:
        raise ValueError(f"serve T >= 2*n_symbols+1 = {2 * S + 1}, ricevuto T={T}")
    rng = np.random.default_rng(seed)
    D = S + 2
    O = S + 1
    blank_in, delim_in, blank_out = S, S + 1, S

    symbols = rng.integers(0, S, size=S)

    X = np.zeros((T, D))
    X[:, blank_in] = 1.0
    for j in range(S):
        X[j, blank_in] = 0.0
        X[j, symbols[j]] = 1.0
    X[T - S - 1, blank_in] = 0.0
    X[T - S - 1, delim_in] = 1.0

    targets = np.zeros((T, O))
    targets[:, blank_out] = 1.0
    for j in range(S):
        targets[T - S + j, blank_out] = 0.0
        targets[T - S + j, symbols[j]] = 1.0

    return X, targets


def make_recurrent_matrix(Hdim, rho, seed, orthogonal=True):
    """Matrice ricorrente Whh con raggio spettrale ESATTAMENTE ``rho``.

    Con ``orthogonal=True`` si parte da una matrice ortogonale (QR di una
    gaussiana, con correzione di segno per l'unicita'): tutti gli autovalori
    hanno modulo 1, quindi ``rho * Q`` ha TUTTI gli autovalori di modulo
    ``rho`` e per di piu' ``||rho Q v|| = rho ||v||`` per ogni v. E' il caso
    pulito: nessun transiente dovuto alla non-normalita' della matrice, il
    decadimento e' esattamente geometrico fin dal primo passo.

    Con ``orthogonal=False`` si riscala una gaussiana, che e' fortemente non
    normale: il raggio spettrale resta ``rho`` ma la norma puo' crescere per
    parecchi passi prima di decadere.

    Parametri
    ---------
    Hdim : int
    rho : float, raggio spettrale desiderato.
    seed : int
    orthogonal : bool

    Ritorna
    -------
    ndarray (Hdim, Hdim).
    """
    rng = np.random.default_rng(seed)
    M = rng.standard_normal((Hdim, Hdim))
    if orthogonal:
        Q, R = np.linalg.qr(M)
        s = np.sign(np.diag(R))
        s[s == 0.0] = 1.0
        M = Q * s  # correzione di segno: rende la QR unica
    r = float(np.max(np.abs(np.linalg.eigvals(M))))
    return rho * M / r


def init_params(D, Hdim, O, seed, rho=0.9, in_scale=0.5, out_scale=0.5,
                bias_scale=0.0, orthogonal=True):
    """Dizionario di parametri con ``Whh`` a raggio spettrale ``rho``.

    Ritorna
    -------
    dict con chiavi ``"Wxh" (Hdim, D)``, ``"Whh" (Hdim, Hdim)``,
    ``"bh" (Hdim,)``, ``"Why" (O, Hdim)``, ``"by" (O,)``.
    """
    rng = np.random.default_rng(seed)
    return {
        "Wxh": in_scale * rng.standard_normal((Hdim, D)),
        "Whh": make_recurrent_matrix(Hdim, rho, seed + 977, orthogonal),
        "bh": bias_scale * rng.standard_normal(Hdim),
        "Why": out_scale * rng.standard_normal((O, Hdim)),
        "by": bias_scale * rng.standard_normal(O),
    }


def pack_params(params):
    """Concatena i parametri in un unico vettore piatto, ordine ``PARAM_KEYS``."""
    return np.concatenate(
        [np.asarray(params[k], dtype=float).ravel() for k in PARAM_KEYS]
    )


def unpack_params(theta, like):
    """Inverso di ``pack_params``. ``like`` fornisce le shape."""
    out = {}
    i = 0
    for k in PARAM_KEYS:
        shape = np.shape(like[k])
        n = int(np.prod(shape)) if shape else 1
        out[k] = np.asarray(theta[i:i + n], dtype=float).reshape(shape).copy()
        i += n
    return out


def mse_loss_and_grad(Y, targets):
    """Loss quadratica ``0.5 * sum((Y - targets)^2)`` e il suo gradiente su Y.

    Ritorna
    -------
    loss : float
    dY : ndarray (T, O), pari a ``Y - targets``.
    """
    Y = np.asarray(Y, dtype=float)
    targets = np.asarray(targets, dtype=float)
    diff = Y - targets
    return 0.5 * float(np.sum(diff * diff)), diff


def format_decay_profile(norms, width=48):
    """Barre testuali in scala log10 del profilo ``||dL/dh_t||`` (aiuto visivo).

    Parametri
    ---------
    norms : ndarray (T+1,), tipicamente l'uscita di ``gradient_norms_over_time``.
    width : int, larghezza massima della barra.

    Ritorna
    -------
    str multilinea, una riga per timestep.
    """
    norms = np.asarray(norms, dtype=float)
    safe = np.where(norms > 0.0, norms, np.nan)
    logs = np.log10(safe)
    lo = np.nanmin(logs)
    hi = np.nanmax(logs)
    span = max(hi - lo, 1e-12)
    lines = []
    for t, (n, lg) in enumerate(zip(norms, logs)):
        k = 0 if not np.isfinite(lg) else int(round(width * (lg - lo) / span))
        lines.append(f"t={t:3d} |{'#' * k:<{width}}| {n:.3e}")
    return "\n".join(lines)


# =============================================================================
# L'ESERCIZIO
# =============================================================================


def tanh_prime(a):
    """Derivata di tanh valutata sul PRE-attivato ``a``.

    CONVENZIONE (fonte classica di bug): l'argomento e' il pre-attivato
    ``a``, NON lo stato ``h = tanh(a)``. Quindi

        tanh'(a) = 1 - tanh(a)^2

    Se hai gia' ``h = tanh(a)`` la derivata vale ``1 - h^2``: e' la stessa
    quantita', ma NON va ottenuta passando ``h`` a questa funzione (daresti
    ``1 - tanh(h)^2``, che e' sbagliato ovunque tranne che in 0).

    Parametri
    ---------
    a : array_like, shape qualsiasi (pre-attivati).

    Ritorna
    -------
    ndarray della stessa shape, con valori in (0, 1].
    """
    a = np.asarray(a, dtype=float)
    t = np.tanh(a)
    return 1.0 - t * t


def rnn_forward(X, Wxh, Whh, bh, Why, by):
    """Forward di una RNN vanilla con stato iniziale nullo.

        A[i] = Whh @ H[i] + Wxh @ X[i] + bh
        H[i+1] = tanh(A[i])
        Y[i] = Why @ H[i+1] + by            i = 0..T-1,  H[0] = 0

    Parametri
    ---------
    X : ndarray (T, D)
    Wxh : ndarray (Hdim, D)
    Whh : ndarray (Hdim, Hdim)
    bh : ndarray (Hdim,)
    Why : ndarray (O, Hdim)
    by : ndarray (O,)

    Ritorna
    -------
    H : ndarray (T+1, Hdim)
        ``H[0]`` e' lo stato iniziale, identicamente nullo. ``H[i+1]`` e' lo
        stato dopo il timestep i.
    Y : ndarray (T, O)
    cache : dict
        ``{"X": X (T, D), "H": H (T+1, Hdim), "A": A (T, Hdim)}`` con ``A``
        i PRE-attivati, allineati a X e Y (``A[i]`` produce ``H[i+1]``).
        E' tutto e solo cio' che serve al backward.
    """
    X = np.asarray(X, dtype=float)
    T = X.shape[0]
    Hdim = Whh.shape[0]
    O = Why.shape[0]

    H = np.zeros((T + 1, Hdim))
    A = np.zeros((T, Hdim))
    Y = np.zeros((T, O))

    for i in range(T):
        A[i] = Whh @ H[i] + Wxh @ X[i] + bh
        H[i + 1] = np.tanh(A[i])
        Y[i] = Why @ H[i + 1] + by

    cache = {"X": X, "H": H, "A": A}
    return H, Y, cache


def rnn_backward(dY, cache, Wxh, Whh, Why):
    """BPTT completo: gradienti della loss rispetto a parametri e stati.

    Riceve ``dY[i] = dL/dY[i]`` e propaga all'indietro lungo TUTTA la
    sequenza. Non assume che ``cache["H"][0]`` sia nullo: cosi' la funzione si
    puo' applicare anche a una FINESTRA della sequenza (basta affettare la
    cache), che e' esattamente cio' che serve al BPTT troncato.

    Ricorsione, per i da T-1 a 0:

        dH[i+1] += Why^T dY[i]
        dA[i]    = dH[i+1] * tanh'(A[i])
        dH[i]    = Whh^T dA[i]

    Parametri
    ---------
    dY : ndarray (T, O)
    cache : dict con ``"X" (T, D)``, ``"H" (T+1, Hdim)``, ``"A" (T, Hdim)``.
    Wxh : ndarray (Hdim, D)      (non usata nel calcolo, tenuta per simmetria)
    Whh : ndarray (Hdim, Hdim)
    Why : ndarray (O, Hdim)

    Ritorna
    -------
    dict con chiavi
      "dWxh" (Hdim, D), "dWhh" (Hdim, Hdim), "dbh" (Hdim,),
      "dWhy" (O, Hdim), "dby" (O,),
      "dh0"  (Hdim,)          gradiente rispetto allo stato iniziale,
      "dh_per_step" (T+1, Hdim)
          ``dh_per_step[t] = dL/dH[t]``, gradiente della loss TOTALE rispetto
          allo stato al tempo t. Vale ``dh_per_step[0] == dh0``. La norma di
          queste righe, al variare di t, e' la curva del vanishing.
    """
    X = np.asarray(cache["X"], dtype=float)
    H = np.asarray(cache["H"], dtype=float)
    A = np.asarray(cache["A"], dtype=float)
    dY = np.asarray(dY, dtype=float)

    T, Hdim = A.shape

    dWxh = np.zeros_like(Wxh, dtype=float)
    dWhh = np.zeros_like(Whh, dtype=float)
    dbh = np.zeros(Hdim)
    dWhy = np.zeros_like(Why, dtype=float)
    dby = np.zeros(Why.shape[0])
    dh_per_step = np.zeros((T + 1, Hdim))

    dh = np.zeros(Hdim)  # contributo che arriva dal futuro
    for i in range(T - 1, -1, -1):
        # ramo di output del timestep i: dipende da H[i+1]
        dWhy += np.outer(dY[i], H[i + 1])
        dby += dY[i]
        dh = dh + Why.T @ dY[i]
        dh_per_step[i + 1] = dh

        # attraversamento della non linearita'
        da = dh * tanh_prime(A[i])
        dWxh += np.outer(da, X[i])
        dWhh += np.outer(da, H[i])
        dbh += da

        # un passo indietro nel tempo
        dh = Whh.T @ da

    dh_per_step[0] = dh
    return {
        "dWxh": dWxh,
        "dWhh": dWhh,
        "dbh": dbh,
        "dWhy": dWhy,
        "dby": dby,
        "dh0": dh.copy(),
        "dh_per_step": dh_per_step,
    }


def bptt_truncated(X, targets, params, k1, k2):
    """BPTT troncato: aggiorna ogni ``k1`` passi propagando indietro ``k2`` passi.

    E' lo schema BPTT(k1, k2) di Williams & Peng. La sequenza viene divisa in
    blocchi consecutivi di ``k1`` timestep (l'ultimo puo' essere piu' corto).
    Per il blocco che finisce al timestep ``hi`` (escluso) si iniettano SOLO
    gli errori dei timestep del blocco e si propaga all'indietro fino al
    timestep ``max(0, hi - k2)``, dopodiche' il gradiente viene troncato.
    I contributi dei blocchi si sommano.

    Poiche' la loss e' una somma sui timestep e il gradiente e' lineare nella
    loss, con ``k2 >= T`` i blocchi partizionano esattamente i termini di loss
    e nessuno viene troncato: il risultato coincide con il BPTT completo. Con
    ``k2`` piccolo si perdono i cammini lunghi e si introduce un BIAS (non
    rumore: e' un errore sistematico, sempre nella stessa direzione).

    Parametri
    ---------
    X : ndarray (T, D)
    targets : ndarray (T, O), target su OGNI timestep (loss quadratica).
    params : dict con "Wxh", "Whh", "bh", "Why", "by".
    k1 : int >= 1, ogni quanti passi si fa un aggiornamento.
    k2 : int >= k1, quanti passi si propaga indietro.

    Ritorna
    -------
    dict con "dWxh", "dWhh", "dbh", "dWhy", "dby" (gradienti ACCUMULATI su
    tutti i blocchi, stesse shape dei parametri) e "loss" (float, loss totale
    sull'intera sequenza, non troncata).
    """
    X = np.asarray(X, dtype=float)
    T = X.shape[0]
    k1 = int(k1)
    k2 = int(k2)
    if k1 < 1:
        raise ValueError("k1 deve essere >= 1")
    if k2 < k1:
        raise ValueError("BPTT(k1, k2) richiede k2 >= k1")

    Wxh, Whh, bh = params["Wxh"], params["Whh"], params["bh"]
    Why, by = params["Why"], params["by"]

    # Un solo forward sull'intera sequenza: il troncamento riguarda il
    # backward, non il forward (lo stato viene comunque portato avanti).
    _, Y, cache = rnn_forward(X, Wxh, Whh, bh, Why, by)
    loss, dY = mse_loss_and_grad(Y, targets)

    acc = {
        "dWxh": np.zeros_like(Wxh, dtype=float),
        "dWhh": np.zeros_like(Whh, dtype=float),
        "dbh": np.zeros_like(bh, dtype=float),
        "dWhy": np.zeros_like(Why, dtype=float),
        "dby": np.zeros_like(by, dtype=float),
    }

    lo = 0
    while lo < T:
        hi = min(lo + k1, T)              # blocco di loss [lo, hi)
        start = max(0, hi - k2)           # troncamento del backward
        # Finestra della cache: rnn_backward la tratta come una sequenza a se',
        # con H[start] nel ruolo di stato iniziale. Cosi' il gradiente non
        # scende sotto start: e' esattamente il troncamento.
        sub_cache = {
            "X": cache["X"][start:hi],
            "H": cache["H"][start:hi + 1],
            "A": cache["A"][start:hi],
        }
        sub_dY = np.zeros((hi - start, dY.shape[1]))
        sub_dY[lo - start:hi - start] = dY[lo:hi]

        g = rnn_backward(sub_dY, sub_cache, Wxh, Whh, Why)
        for key in acc:
            acc[key] += g[key]
        lo = hi

    acc["loss"] = loss
    return acc


def gradient_norms_over_time(X, targets, params):
    """Norma di ``dL/dh_t`` per ogni t, con loss applicata SOLO all'ultimo passo.

    E' la curva che rende il vanishing una misura invece che un'affermazione:
    si inietta un errore soltanto in ``Y[T-1]`` e si guarda quanto ne
    sopravvive risalendo la sequenza. La loss e' ``0.5 ||Y[T-1] - targets[T-1]||^2``.

    Parametri
    ---------
    X : ndarray (T, D)
    targets : ndarray (T, O). Viene usata SOLO l'ultima riga, ``targets[T-1]``;
        le altre sono ignorate (la firma resta uniforme al resto dell'API).
    params : dict con "Wxh", "Whh", "bh", "Why", "by".

    Ritorna
    -------
    ndarray (T+1,), ``out[t] = ||dL/dH[t]||_2``. ``out[T]`` e' il gradiente
    appena iniettato, ``out[0]`` quello che arriva allo stato iniziale.
    """
    X = np.asarray(X, dtype=float)
    targets = np.asarray(targets, dtype=float)
    Wxh, Whh, bh = params["Wxh"], params["Whh"], params["bh"]
    Why, by = params["Why"], params["by"]

    _, Y, cache = rnn_forward(X, Wxh, Whh, bh, Why, by)

    dY = np.zeros_like(Y)
    dY[-1] = Y[-1] - targets[-1]  # loss solo sull'ultimo timestep

    grads = rnn_backward(dY, cache, Wxh, Whh, Why)
    return np.linalg.norm(grads["dh_per_step"], axis=1)


def jacobian_product_spectral_radius(Whh, H, cache):
    """Raggio spettrale del prodotto cumulativo delle jacobiane, all'indietro.

    La jacobiana di un passo di ricorrenza e'

        J_i = dH[i+1]/dH[i] = diag(tanh'(A[i])) @ Whh

    (in numpy: ``tanh_prime(A[i])[:, None] * Whh``). Il gradiente che dal
    timestep finale risale a k passi di distanza passa per il prodotto
    ``J_{T-1} J_{T-2} ... J_{T-k}``: questa funzione ne restituisce il raggio
    spettrale al crescere di k.

    Parametri
    ---------
    Whh : ndarray (Hdim, Hdim)
    H : ndarray (T+1, Hdim)
        stati. Non e' strettamente necessario (i pre-attivati bastano), ma
        ``tanh'(A[i]) == 1 - H[i+1]^2``: le due strade devono dare lo stesso
        risultato ed e' un buon controllo della convenzione di ``tanh_prime``.
    cache : dict del forward, si usa ``cache["A"] (T, Hdim)``.

    Ritorna
    -------
    ndarray (T,), ``out[k] = rho(J_{T-1} J_{T-2} ... J_{T-1-k})``, cioe'
    ``out[0]`` e' il raggio spettrale della jacobiana dell'ULTIMO passo e
    ``out[T-1]`` quello del prodotto su tutta la sequenza.
    """
    A = np.asarray(cache["A"], dtype=float)
    T, Hdim = A.shape
    D = tanh_prime(A)

    P = np.eye(Hdim)
    out = np.zeros(T)
    for k in range(T):
        i = T - 1 - k
        J = D[i][:, None] * Whh          # diag(tanh'(A[i])) @ Whh
        P = P @ J
        out[k] = spectral_radius(P)
    return out


def spectral_radius(M):
    """Massimo modulo degli autovalori di ``M``.

    NON e' una norma: puo' valere 0 su matrici non nulle (es. la nilpotente
    ``[[0, 1], [0, 0]]``) e non e' sub-moltiplicativo. E' proprio per questo
    che ``rho(Whh) < 1`` non implica un decadimento monotono passo per passo,
    e ``rho(Whh) > 1`` non implica esplosione: sono condizioni asintotiche.

    Parametri
    ---------
    M : ndarray (n, n)

    Ritorna
    -------
    float >= 0.
    """
    M = np.asarray(M, dtype=float)
    return float(np.max(np.abs(np.linalg.eigvals(M))))


def clip_gradients(grads, max_norm):
    """Gradient clipping GLOBALE sulla norma L2 di tutti i gradienti concatenati.

    Si calcola ``total = sqrt(sum_k ||grads[k]||_F^2)`` su TUTTE le voci del
    dizionario, come se fossero un unico vettore. Se ``total > max_norm`` si
    riscala ogni voce per ``max_norm / total``, altrimenti non si tocca nulla.
    Il riscalamento e' un singolo scalare comune: la DIREZIONE del gradiente
    nello spazio dei parametri e' preservata, cambia solo il passo. E' la
    differenza fra clipping globale e clipping per-componente (che invece
    storce la direzione).

    Parametri
    ---------
    grads : dict di ndarray. Passare solo i gradienti dei PARAMETRI: se ci
        infili anche "dh_per_step" la norma totale non e' piu' quella
        dell'aggiornamento.
    max_norm : float > 0.

    Ritorna
    -------
    grads_clipped : dict con le stesse chiavi e shape, array NUOVI (l'input
        non viene modificato).
    total_norm : float, la norma PRIMA del clipping (e' la diagnostica utile:
        dice quanto stava esplodendo).
    """
    total_sq = 0.0
    for v in grads.values():
        arr = np.asarray(v, dtype=float)
        total_sq += float(np.sum(arr * arr))
    total_norm = float(np.sqrt(total_sq))

    if total_norm > max_norm:
        scale = max_norm / total_norm
    else:
        scale = 1.0

    clipped = {k: np.asarray(v, dtype=float) * scale for k, v in grads.items()}
    return clipped, total_norm


# =============================================================================
# Demo (non fa parte dei test): il vanishing come curva, non come frase.
# =============================================================================

def _demo():
    T, Hdim, D, O = 20, 6, 3, 2
    targets = np.zeros((T, O))
    # (raggio spettrale, scala degli input, etichetta)
    regimi = [
        (0.5, 0.05, "contrazione: vanishing al tasso rho"),
        (1.0, 0.80, "confine critico: vanishing LO STESSO, per colpa di tanh'"),
        (2.0, 1e-6, "espansione vicino all'origine: exploding al tasso rho"),
    ]
    for rho, xs, etichetta in regimi:
        X = xs * np.random.default_rng(0).standard_normal((T, D))
        params = init_params(D, Hdim, O, seed=1, rho=rho, bias_scale=0.0)
        norms = gradient_norms_over_time(X, targets, params)
        tasso = (norms[0] / norms[T]) ** (1.0 / T)
        print(f"\n--- rho(Whh) = {rho}  |  {etichetta} ---")
        print(f"    tasso per passo misurato = {tasso:.4f}"
              f"   ||dL/dh_0|| / ||dL/dh_T|| = {norms[0] / norms[T]:.3e}")
        print(format_decay_profile(norms))


if __name__ == "__main__":
    _demo()
