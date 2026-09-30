"""Test di autovalutazione - GDL19/GDL20 "Attention, cross-attention, Transformer".

Esecuzione:
    pytest test_attention.py -v                # sullo skeleton
    GDL_SOL=1 pytest test_attention.py -v      # sulla soluzione di riferimento
"""

import os, sys, pathlib, importlib

HERE = pathlib.Path(__file__).parent
if os.environ.get("GDL_SOL"):
    sys.path.insert(0, str(HERE / "soluzione"))
    m = importlib.import_module("attention_sol")
else:
    sys.path.insert(0, str(HERE))
    m = importlib.import_module("attention")

import numpy as np
from numpy.testing import assert_allclose


# ---------------------------------------------------------------------------
# helper locali ai test (non fanno parte dell'API da implementare)
# ---------------------------------------------------------------------------

def _entropia(p):
    """Entropia in nat lungo l'ultimo asse. Massima = log(numero di posizioni)."""
    p = np.clip(np.asarray(p, dtype=float), 1e-300, None)
    return -np.sum(p * np.log(p), axis=-1)


def _pesi_proiezione(d_model, rng):
    """Quattro matrici (d_model, d_model) con scala ragionevole."""
    s = 1.0 / np.sqrt(d_model)
    return [rng.normal(0.0, s, size=(d_model, d_model)) for _ in range(4)]


def _batch_norm(x, eps=1e-5):
    """BatchNorm di riferimento: normalizza ogni FEATURE sull'asse del BATCH.

    Serve solo come contrasto per il test su ``layer_norm``: qui le statistiche
    di un esempio dipendono dagli altri esempi del minibatch.
    """
    x = np.asarray(x, dtype=float)
    mu = x.mean(axis=0, keepdims=True)
    var = x.var(axis=0, keepdims=True)
    return (x - mu) / np.sqrt(var + eps)


# ---------------------------------------------------------------------------
# 1. Softmax: normalizzazione, stabilita', caso limite
# ---------------------------------------------------------------------------

def test_softmax_normalizza_ed_e_stabile():
    """Il softmax deve sommare a 1, non andare in overflow su logit enormi, e
    comportarsi correttamente sul caso degenere di una sola alternativa."""
    rng = np.random.default_rng(1001)

    x = rng.normal(0.0, 2.0, size=(4, 6, 9))
    p = m.softmax(x, axis=-1)
    assert p.shape == x.shape, f"softmax deve preservare la shape, ottenuto {p.shape}"
    assert_allclose(p.sum(axis=-1), np.ones((4, 6)), rtol=1e-6, atol=1e-9,
                    err_msg="il softmax non somma a 1 sull'asse indicato")
    assert np.all(p >= 0.0), "il softmax non puo' produrre valori negativi"

    # asse diverso da -1: se e' cablato a -1 questo fallisce
    p0 = m.softmax(x, axis=0)
    assert_allclose(p0.sum(axis=0), np.ones((6, 9)), rtol=1e-6, atol=1e-9,
                    err_msg="l'argomento axis viene ignorato: softmax cablato sull'ultimo asse")

    # stabilita': senza la sottrazione del massimo exp(1000) e' inf e il
    # risultato diventa NaN
    grandi = np.array([1000.0, 1000.0, 1000.0])
    pg = m.softmax(grandi)
    assert np.all(np.isfinite(pg)), \
        "overflow: manca la sottrazione del massimo prima dell'esponenziale"
    assert_allclose(pg, np.full(3, 1.0 / 3.0), rtol=1e-6, atol=1e-9,
                    err_msg="logit identici devono dare probabilita' uniformi")

    # invarianza per traslazione: softmax(x + c) = softmax(x)
    assert_allclose(m.softmax(x[0] + 137.0, axis=-1), m.softmax(x[0], axis=-1),
                    rtol=1e-6, atol=1e-9,
                    err_msg="il softmax deve essere invariante a una costante additiva")

    # caso limite: una sola alternativa -> probabilita' 1, sempre
    assert_allclose(m.softmax(np.array([[-42.0], [0.0], [42.0]]), axis=-1),
                    np.ones((3, 1)), rtol=1e-6, atol=1e-9,
                    err_msg="con una sola alternativa il softmax vale esattamente 1")


# ---------------------------------------------------------------------------
# 2. Bahdanau e Luong contro la definizione (oracolo indipendente)
# ---------------------------------------------------------------------------

def test_bahdanau_e_luong_contro_la_definizione():
    """Oracolo indipendente: i punteggi calcolati posizione per posizione con un
    ciclo Python, direttamente dalla formula delle slide."""
    rng = np.random.default_rng(1002)
    L, d_dec, d_enc, d_attn = 6, 3, 4, 7

    h_dec = rng.normal(size=d_dec)
    H_enc = rng.normal(size=(L, d_enc))
    Wa = rng.normal(size=(d_attn, d_dec))
    Ua = rng.normal(size=(d_attn, d_enc))
    va = rng.normal(size=d_attn)

    atteso = np.array([va @ np.tanh(Wa @ h_dec + Ua @ H_enc[i]) for i in range(L)])
    ottenuto = m.bahdanau_score(h_dec, H_enc, Wa, Ua, va)
    assert ottenuto.shape == (L,), \
        f"bahdanau_score deve dare un punteggio per stato di encoder: attesa ({L},), ottenuta {ottenuto.shape}"
    assert_allclose(ottenuto, atteso, rtol=1e-6, atol=1e-9,
                    err_msg="bahdanau_score non corrisponde a va^T tanh(Wa h + Ua H_i); "
                            "controlla di NON aver applicato tanh dopo la proiezione su va")

    # Luong, variante dot
    H_same = rng.normal(size=(L, d_dec))
    atteso_dot = np.array([H_same[i] @ h_dec for i in range(L)])
    assert_allclose(m.luong_score(h_dec, H_same), atteso_dot, rtol=1e-6, atol=1e-9,
                    err_msg="la variante dot di Luong e' il semplice prodotto scalare H_i . h")

    # Luong, variante general: con Wa = identita' deve ridursi alla variante dot
    assert_allclose(m.luong_score(h_dec, H_same, np.eye(d_dec)), atteso_dot,
                    rtol=1e-6, atol=1e-9,
                    err_msg="con Wa = I la variante general deve coincidere con la variante dot; "
                            "se non succede stai moltiplicando Wa dalla parte sbagliata")

    Wa_gen = rng.normal(size=(d_enc, d_dec))
    atteso_gen = np.array([H_enc[i] @ (Wa_gen @ h_dec) for i in range(L)])
    assert_allclose(m.luong_score(h_dec, H_enc, Wa_gen), atteso_gen, rtol=1e-6, atol=1e-9,
                    err_msg="la variante general di Luong e' H_i^T Wa h")


# ---------------------------------------------------------------------------
# 3. (a) I pesi di attenzione sommano a 1 su ogni riga
# ---------------------------------------------------------------------------

def test_pesi_di_attenzione_sommano_a_uno():
    """L'attenzione e' una media pesata convessa: ogni riga dei pesi e' una
    distribuzione di probabilita' sulle posizioni sorgente. Vale anche, e
    soprattutto, in presenza di maschera."""
    rng = np.random.default_rng(1003)
    N, H, Lq, Lk, d_k, d_v = 3, 2, 5, 7, 8, 4

    Q = rng.normal(size=(N, H, Lq, d_k))
    K = rng.normal(size=(N, H, Lk, d_k))
    V = rng.normal(size=(N, H, Lk, d_v))

    out, attn = m.scaled_dot_product_attention(Q, K, V)
    assert out.shape == (N, H, Lq, d_v), \
        f"output atteso {(N, H, Lq, d_v)}, ottenuto {out.shape}: l'output vive nello spazio dei VALORI"
    assert attn.shape == (N, H, Lq, Lk), \
        f"pesi attesi {(N, H, Lq, Lk)}, ottenuti {attn.shape}"
    assert_allclose(attn.sum(axis=-1), np.ones((N, H, Lq)), rtol=1e-6, atol=1e-9,
                    err_msg="i pesi devono sommare a 1 sulle CHIAVI (ultimo asse), non sulle query")
    assert np.all(attn >= 0.0), "i pesi di attenzione non possono essere negativi"

    # con maschera di padding: la normalizzazione deve restare esatta e i pesi
    # sulle posizioni di padding devono essere esattamente 0
    lengths = np.array([7, 4, 1])
    pad = m.padding_mask(lengths, Lk)
    assert pad.shape == (N, Lk) and pad.dtype == bool, \
        f"padding_mask deve dare una maschera booleana (N, L), ottenuto {pad.shape} {pad.dtype}"
    assert not pad[0].any(), "una sequenza lunga quanto L non ha posizioni di padding"
    assert pad[2, 1:].all() and not pad[2, 0], \
        "con lunghezza 1 solo la posizione 0 e' valida: True = posizione DA MASCHERARE"

    out_p, attn_p = m.scaled_dot_product_attention(Q, K, V, mask=pad[:, None, None, :])
    assert_allclose(attn_p.sum(axis=-1), np.ones((N, H, Lq)), rtol=1e-6, atol=1e-9,
                    err_msg="dopo il mascheramento i pesi devono essere RInormalizzati: "
                            "il -inf va messo PRIMA del softmax, non azzerato dopo")
    assert np.all(attn_p[1, :, :, 4:] == 0.0), \
        "le posizioni di padding devono ricevere peso esattamente 0"
    # controprova: la sequenza 0 non ha padding, il risultato deve essere identico
    assert_allclose(attn_p[0], attn[0], rtol=1e-6, atol=1e-9,
                    err_msg="una maschera tutta False non deve cambiare nulla")


# ---------------------------------------------------------------------------
# 4. (b) La maschera causale blocca DAVVERO il futuro  [test chiave]
# ---------------------------------------------------------------------------

def test_maschera_causale_blocca_il_futuro():
    """Verifica EMPIRICA della causalita': si perturba un input futuro e si
    controlla che l'output alle posizioni passate non cambi di un bit.

    E' il test che scopre la maschera invertita (`j < i` invece di `j > i`, o
    True/False scambiati): una maschera invertita produce comunque pesi che
    sommano a 1 e output della shape giusta, ma fa dipendere il presente dal
    futuro. Nessun controllo di forma se ne accorge."""
    rng = np.random.default_rng(1004)
    N, L, d_model, n_heads, t = 2, 8, 8, 2, 3

    mask = m.causal_mask(L)
    assert mask.shape == (L, L) and mask.dtype == bool, \
        f"causal_mask deve dare una (L, L) booleana, ottenuto {mask.shape} {mask.dtype}"
    assert not mask[0, 0] and not np.any(np.diag(mask)), \
        "la diagonale non va mascherata: ogni posizione deve poter guardare se stessa"
    assert mask[0, 1] and not mask[1, 0], \
        "convenzione sbagliata: mask[i, j] deve essere True per j > i (il FUTURO e' mascherato)"
    assert not mask[L - 1].any(), \
        "l'ultima posizione vede tutto il passato: la sua riga non ha nulla da mascherare"

    X = rng.normal(size=(N, L, d_model))
    Wq, Wk, Wv, Wo = _pesi_proiezione(d_model, rng)

    out_orig, _ = m.multi_head_attention(X, X, Wq, Wk, Wv, Wo, n_heads, mask=mask)

    # perturbazione MASSICCIA di tutti gli input strettamente dopo t
    X_pert = X.copy()
    X_pert[:, t + 1:, :] += 5.0
    out_pert, _ = m.multi_head_attention(X_pert, X_pert, Wq, Wk, Wv, Wo, n_heads, mask=mask)

    assert_allclose(out_pert[:, :t + 1, :], out_orig[:, :t + 1, :], rtol=1e-9, atol=1e-12,
                    err_msg=f"l'output alle posizioni 0..{t} e' cambiato perturbando gli input "
                            f"a partire da {t + 1}: la maschera causale e' invertita o non "
                            f"viene applicata prima del softmax")

    # controprova: la perturbazione deve fare qualcosa, altrimenti il test
    # passerebbe anche con una funzione costante
    delta_futuro = np.abs(out_pert[:, t + 1:, :] - out_orig[:, t + 1:, :]).max()
    assert delta_futuro > 1e-3, \
        "la perturbazione non ha cambiato nemmeno l'output futuro: il test e' vacuo"

    # e i pesi devono essere strettamente triangolari inferiori
    _, attn = m.multi_head_attention(X, X, Wq, Wk, Wv, Wo, n_heads, mask=mask)
    assert np.all(attn[:, :, mask] == 0.0), \
        "i pesi verso posizioni future devono essere esattamente 0"


# ---------------------------------------------------------------------------
# 5. (c) Equivarianza alle permutazioni, e come il PE la rompe  [test chiave]
# ---------------------------------------------------------------------------

def test_permutation_equivariance_e_rottura_col_positional_encoding():
    """La self-attention, da sola, NON sa nulla dell'ordine: permutare gli input
    permuta gli output allo stesso modo. E' una proprieta' esatta, non
    approssimata, e vale per qualsiasi valore dei pesi.

    Poi la controprova: sommando il positional encoding l'equivarianza si
    ROMPE. Questa e' l'intera ragione d'essere del PE. Se il primo blocco
    fallisce, da qualche parte c'e' una dipendenza dall'indice che non
    dovrebbe esserci; se fallisce il secondo, il PE non sta entrando nel
    calcolo (o e' costante rispetto alla posizione)."""
    rng = np.random.default_rng(1005)
    N, L, d_model, n_heads = 1, 6, 8, 2

    X = rng.normal(size=(N, L, d_model))
    Wq, Wk, Wv, Wo = _pesi_proiezione(d_model, rng)
    perm = rng.permutation(L)
    assert not np.array_equal(perm, np.arange(L)), "il seed ha prodotto la permutazione identica"

    out, _ = m.multi_head_attention(X, X, Wq, Wk, Wv, Wo, n_heads)
    out_perm, _ = m.multi_head_attention(X[:, perm, :], X[:, perm, :],
                                         Wq, Wk, Wv, Wo, n_heads)

    assert_allclose(out_perm, out[:, perm, :], rtol=1e-6, atol=1e-9,
                    err_msg="la self-attention senza positional encoding DEVE essere equivariante "
                            "alle permutazioni: f(P X) = P f(X). Se non lo e', qualcosa nel "
                            "calcolo dipende dall'indice di posizione")

    # ------- ora aggiungiamo il positional encoding: deve rompersi -------
    PE = m.positional_encoding(L, d_model)
    assert PE.shape == (L, d_model), \
        f"positional_encoding deve dare (L, d_model), ottenuto {PE.shape}"
    assert np.abs(PE[0] - PE[1]).max() > 1e-3, \
        "il positional encoding e' (quasi) costante nella posizione: non codifica niente"

    Xpe = X + PE                              # sequenza originale + posizioni
    Xpe_perm = X[:, perm, :] + PE             # token permutati, posizioni NO

    out_pe, _ = m.multi_head_attention(Xpe, Xpe, Wq, Wk, Wv, Wo, n_heads)
    out_pe_perm, _ = m.multi_head_attention(Xpe_perm, Xpe_perm, Wq, Wk, Wv, Wo, n_heads)

    scarto = np.abs(out_pe_perm - out_pe[:, perm, :]).max()
    scala = np.abs(out_pe).max()
    assert scarto > 0.05 * scala, \
        ("con il positional encoding l'equivarianza alle permutazioni deve ROMPERSI, "
         f"invece lo scarto relativo e' {scarto / scala:.2e}: il PE non sta entrando nel "
         "calcolo, oppure non dipende dalla posizione")


# ---------------------------------------------------------------------------
# 6. (d) split_heads e merge_heads sono l'una l'inversa dell'altra
# ---------------------------------------------------------------------------

def test_split_e_merge_heads_sono_inverse():
    """Round-trip esatto nei due versi. E' una proprieta' di invertibilita': se
    l'ordine di reshape e transpose e' sbagliato il round-trip resta esatto
    solo in un verso, o mescola le teste."""
    rng = np.random.default_rng(1006)
    N, L, d_model, n_heads = 3, 7, 12, 4
    d_head = d_model // n_heads

    x = rng.normal(size=(N, L, d_model))
    xs = m.split_heads(x, n_heads)
    assert xs.shape == (N, n_heads, L, d_head), \
        f"split_heads deve dare {(N, n_heads, L, d_head)}, ottenuto {xs.shape}"
    assert_allclose(m.merge_heads(xs), x, rtol=1e-6, atol=1e-9,
                    err_msg="merge_heads(split_heads(x)) deve essere l'identita'")

    y = rng.normal(size=(N, n_heads, L, d_head))
    assert_allclose(m.split_heads(m.merge_heads(y), n_heads), y, rtol=1e-6, atol=1e-9,
                    err_msg="split_heads(merge_heads(y)) deve essere l'identita': "
                            "transpose e reshape vanno applicati in ordine inverso")

    # le teste sono fette CONTIGUE dell'ultima dimensione
    assert_allclose(xs[:, 2, :, :], x[:, :, 2 * d_head:3 * d_head], rtol=1e-6, atol=1e-9,
                    err_msg="la testa h deve prendere le colonne [h*d_head, (h+1)*d_head): "
                            "hai fatto reshape e transpose nell'ordine sbagliato (stride interleaved)")

    # caso limite: una sola testa non deve cambiare nulla se non aggiungere un asse
    assert_allclose(m.split_heads(x, 1)[:, 0], x, rtol=1e-6, atol=1e-9,
                    err_msg="con n_heads=1 split_heads deve solo inserire un asse di dimensione 1")


# ---------------------------------------------------------------------------
# 7. (e) Multi-head con una sola testa = scaled dot-product attention
# ---------------------------------------------------------------------------

def test_multihead_con_una_testa_coincide_con_scaled_dot_product():
    """Con n_heads=1 il multi-head si riduce esattamente all'attenzione singola
    applicata alle proiezioni, seguita dalla proiezione di output. Se non
    coincide, lo scaling usa d_model invece di d_head, oppure Wo viene applicata
    prima della concatenazione."""
    rng = np.random.default_rng(1007)
    N, L, d_model = 2, 5, 8

    X = rng.normal(size=(N, L, d_model))
    Wq, Wk, Wv, Wo = _pesi_proiezione(d_model, rng)

    out_mha, attn_mha = m.multi_head_attention(X, X, Wq, Wk, Wv, Wo, 1)

    Q, K, V = X @ Wq, X @ Wk, X @ Wv
    out_ref, attn_ref = m.scaled_dot_product_attention(Q, K, V)

    assert attn_mha.shape == (N, 1, L, L), \
        f"con n_heads=1 i pesi devono avere shape {(N, 1, L, L)}, ottenuto {attn_mha.shape}"
    assert_allclose(attn_mha[:, 0], attn_ref, rtol=1e-6, atol=1e-9,
                    err_msg="con una sola testa i pesi devono coincidere con quelli della "
                            "scaled dot-product attention sulle proiezioni")
    assert_allclose(out_mha, out_ref @ Wo, rtol=1e-6, atol=1e-9,
                    err_msg="con una sola testa l'output deve essere Attention(XWq, XWk, XWv) Wo")

    # con piu' teste il risultato deve invece essere DIVERSO: le teste
    # partizionano lo spazio e ciascuna normalizza il proprio softmax
    n_heads = 4
    out_4, attn_4 = m.multi_head_attention(X, X, Wq, Wk, Wv, Wo, n_heads)
    assert attn_4.shape == (N, n_heads, L, L), \
        f"pesi attesi {(N, n_heads, L, L)}, ottenuti {attn_4.shape}"
    assert np.abs(out_4 - out_mha).max() > 1e-6, \
        "4 teste danno lo stesso risultato di 1: le teste non stanno venendo separate"

    # oracolo indipendente sull'assemblaggio multi-testa: ogni testa ricostruita
    # a mano affettando le proiezioni, senza passare da split_heads. Verifica
    # anche che il denominatore dello scaling sia d_head e NON d_model.
    d_head = d_model // n_heads
    Qf, Kf, Vf = X @ Wq, X @ Wk, X @ Wv
    teste = []
    for h in range(n_heads):
        sl = slice(h * d_head, (h + 1) * d_head)
        Qh, Kh, Vh = Qf[..., sl], Kf[..., sl], Vf[..., sl]
        a_h = m.softmax(Qh @ np.swapaxes(Kh, -1, -2) / np.sqrt(d_head), axis=-1)
        assert_allclose(attn_4[:, h], a_h, rtol=1e-6, atol=1e-9,
                        err_msg=f"i pesi della testa {h} non corrispondono a "
                                f"softmax(Q_h K_h^T / sqrt(d_head)): o le teste sono affettate "
                                f"diversamente, o lo scaling usa d_model={d_model} invece di "
                                f"d_head={d_head}")
        teste.append(a_h @ Vh)
    assert_allclose(out_4, np.concatenate(teste, axis=-1) @ Wo, rtol=1e-6, atol=1e-9,
                    err_msg="l'output multi-testa e' concat(head_1..head_H) Wo: le teste vanno "
                            "concatenate sull'ultima dimensione e Wo applicata DOPO")


# ---------------------------------------------------------------------------
# 8. (f) Senza 1/sqrt(d_k) il softmax satura
# ---------------------------------------------------------------------------

def test_lo_scaling_evita_la_saturazione_del_softmax():
    """Con Q e K a componenti indipendenti di varianza 1, il prodotto scalare su
    d_k dimensioni ha deviazione standard sqrt(d_k). Senza dividere per
    sqrt(d_k) i logit hanno scala 8 (per d_k=64), il softmax collassa su una
    sola posizione e l'entropia dei pesi crolla.

    Lo quantifichiamo: con lo scaling l'entropia resta vicina al massimo
    log(Lk); senza, scende sotto un quarto di quel valore."""
    rng = np.random.default_rng(1008)
    Lq, Lk, d_k, d_v = 8, 64, 64, 5

    Q = rng.normal(size=(Lq, d_k))
    K = rng.normal(size=(Lk, d_k))
    V = rng.normal(size=(Lk, d_v))

    _, attn_scalata = m.scaled_dot_product_attention(Q, K, V)
    attn_non_scalata = m.softmax(Q @ K.T, axis=-1)      # esattamente senza 1/sqrt(d_k)

    H_max = np.log(Lk)
    H_scalata = _entropia(attn_scalata).mean()
    H_non_scalata = _entropia(attn_non_scalata).mean()

    assert H_scalata > 0.80 * H_max, \
        (f"con lo scaling l'entropia media dei pesi e' {H_scalata:.3f} contro un massimo di "
         f"{H_max:.3f}: l'attenzione dovrebbe restare diffusa")
    assert H_non_scalata < 0.25 * H_scalata, \
        (f"senza scaling l'entropia dovrebbe crollare, invece vale {H_non_scalata:.3f} contro "
         f"{H_scalata:.3f} con scaling. Se i due numeri coincidono, la tua "
         f"scaled_dot_product_attention NON sta dividendo per sqrt(d_k)")
    assert attn_non_scalata.max() > 0.99 and attn_scalata.max() < 0.5, \
        (f"senza scaling il peso massimo e' {attn_non_scalata.max():.3f} (atteso ~1, softmax "
         f"saturo); con scaling e' {attn_scalata.max():.3f} (atteso < 0.5)")

    # controprova diretta sulla formula: riscalando Q di sqrt(d_k) si deve
    # ottenere esattamente il softmax non scalato
    _, attn_riscalata = m.scaled_dot_product_attention(Q * np.sqrt(d_k), K, V)
    assert_allclose(attn_riscalata, attn_non_scalata, rtol=1e-6, atol=1e-9,
                    err_msg="il denominatore non e' sqrt(d_k): moltiplicare Q per sqrt(d_k) deve "
                            "cancellare esattamente lo scaling")


# ---------------------------------------------------------------------------
# 9. (g) PE[pos+k] e' una rotazione fissa di PE[pos]  (oracolo indipendente)
# ---------------------------------------------------------------------------

def test_positional_encoding_shift_e_una_rotazione_fissa():
    """Proprieta' centrale del PE sinusoidale: per ogni offset k esiste una
    matrice M_k, INDIPENDENTE da pos, tale che PE[pos+k] = M_k PE[pos]. E' il
    motivo per cui il modello puo' apprendere posizioni RELATIVE.

    L'oracolo e' doppio. Primo: la matrice ricavata dall'identita'
    trigonometrica di somma, costruita qui e mai dentro l'implementazione.
    Secondo, e indipendente dalla struttura a blocchi: si cerca ai minimi
    quadrati una qualunque matrice lineare che porti PE[:-k] in PE[k:] e si
    verifica che il residuo sia nullo, cosa che per un encoding arbitrario non
    accade."""
    L, d_model, k = 64, 16, 5
    PE = m.positional_encoding(L, d_model)

    # --- primo oracolo: la rotazione a blocchi 2x2, dalla formula di somma ---
    i = np.arange(d_model // 2, dtype=float)
    omega = np.exp(-(2.0 * i / d_model) * np.log(10000.0))
    M = np.zeros((d_model, d_model))
    for j, w in enumerate(omega):
        c, s = np.cos(w * k), np.sin(w * k)
        M[2 * j, 2 * j], M[2 * j, 2 * j + 1] = c, s
        M[2 * j + 1, 2 * j], M[2 * j + 1, 2 * j + 1] = -s, c

    assert_allclose(PE[k:], PE[:L - k] @ M.T, rtol=1e-6, atol=1e-9,
                    err_msg="PE[pos+k] non e' M_k PE[pos] con la rotazione attesa: controlla "
                            "l'alternanza sin sulle colonne PARI e cos sulle DISPARI, e la "
                            "base 10000^(2i/d_model)")
    assert_allclose(M @ M.T, np.eye(d_model), rtol=1e-6, atol=1e-9,
                    err_msg="M_k deve essere ortogonale: e' una rotazione, non deforma le norme")
    assert_allclose(np.linalg.norm(PE, axis=1),
                    np.full(L, np.sqrt(d_model / 2.0)), rtol=1e-6, atol=1e-9,
                    err_msg="sin^2 + cos^2 = 1 su ogni coppia: tutte le righe del PE devono avere "
                            "norma sqrt(d_model/2)")

    # --- secondo oracolo: esiste UNA trasformazione lineare, trovata ai minimi quadrati ---
    A, B = PE[:L - k], PE[k:]
    Mhat = np.linalg.lstsq(A, B, rcond=None)[0]
    residuo = np.abs(A @ Mhat - B).max()
    assert residuo < 1e-8, \
        (f"non esiste alcuna mappa lineare fissa che porti PE[pos] in PE[pos+k] "
         f"(residuo ai minimi quadrati {residuo:.2e})")

    # controprova: per un encoding qualunque la stessa ricerca fallisce
    rng = np.random.default_rng(1009)
    PE_finto = rng.normal(size=(L, d_model))
    A2, B2 = PE_finto[:L - k], PE_finto[k:]
    residuo_finto = np.abs(A2 @ np.linalg.lstsq(A2, B2, rcond=None)[0] - B2).max()
    assert residuo_finto > 0.1, \
        "il test e' vacuo: anche un encoding casuale supererebbe il controllo ai minimi quadrati"


# ---------------------------------------------------------------------------
# 10. (h) LayerNorm: statistiche per riga, e indipendenza dal batch
# ---------------------------------------------------------------------------

def test_layer_norm_normalizza_per_riga_e_non_dipende_dal_batch():
    """Con gamma=1 e beta=0 la LayerNorm produce media 0 e varianza 1
    sull'ULTIMA dimensione, ed e' invariante a shift e scala dell'input.

    La differenza con BatchNorm e' verificata direttamente: applicare la
    LayerNorm a un batch da lo stesso risultato che applicarla a ogni elemento
    da solo, mentre la BatchNorm cambia se cambiano gli ALTRI elementi del
    batch."""
    rng = np.random.default_rng(1010)
    N, L, d = 4, 5, 16
    gamma, beta = np.ones(d), np.zeros(d)

    X = rng.normal(0.0, 3.0, size=(N, L, d)) + 7.0
    Y = m.layer_norm(X, gamma, beta)

    assert Y.shape == X.shape, f"layer_norm deve preservare la shape, ottenuto {Y.shape}"
    assert_allclose(Y.mean(axis=-1), np.zeros((N, L)), rtol=0, atol=1e-8,
                    err_msg="media non nulla sull'ultima dimensione: stai normalizzando "
                            "sull'asse sbagliato")
    assert_allclose(Y.var(axis=-1), np.ones((N, L)), rtol=0, atol=1e-4,
                    err_msg="varianza diversa da 1 sull'ultima dimensione (la tolleranza tiene "
                            "gia' conto di eps)")

    # invarianza affine dell'input: LN(a x + b) = LN(x)
    assert_allclose(m.layer_norm(3.5 * X + 12.0, gamma, beta), Y, rtol=0, atol=1e-4,
                    err_msg="la LayerNorm deve essere invariante a shift e scala dell'input")

    # gamma e beta agiscono dopo la normalizzazione, per feature
    g, b = rng.normal(size=d), rng.normal(size=d)
    assert_allclose(m.layer_norm(X, g, b), Y * g + b, rtol=1e-6, atol=1e-9,
                    err_msg="gamma e beta vanno applicati DOPO la normalizzazione, "
                            "elemento per elemento sull'ultima dimensione")

    # --- il punto: LayerNorm e' locale alla riga, BatchNorm no ---
    uno_alla_volta = np.stack([np.stack([m.layer_norm(X[n, t], gamma, beta)
                                         for t in range(L)]) for n in range(N)])
    assert_allclose(Y, uno_alla_volta, rtol=1e-6, atol=1e-9,
                    err_msg="la LayerNorm su un batch deve coincidere con la LayerNorm applicata "
                            "a ogni riga da sola: se non succede stai usando statistiche di batch")

    # cambiare gli ALTRI elementi del batch non tocca il primo...
    X_alt = X.copy()
    X_alt[1:] = rng.normal(0.0, 50.0, size=(N - 1, L, d))
    assert_allclose(m.layer_norm(X_alt, gamma, beta)[0], Y[0], rtol=1e-6, atol=1e-9,
                    err_msg="la LayerNorm dell'esempio 0 e' cambiata modificando gli altri "
                            "esempi del batch: e' esattamente cio' che NON deve fare")
    # ...mentre per la BatchNorm cambia eccome (controprova sul concetto)
    bn_a = _batch_norm(X.reshape(N, -1))[0]
    bn_b = _batch_norm(X_alt.reshape(N, -1))[0]
    assert np.abs(bn_a - bn_b).max() > 1.0, \
        "il contrasto con la BatchNorm e' vacuo: i dati alternativi non sono abbastanza diversi"


# ---------------------------------------------------------------------------
# 11. (i) Il costo cresce quadraticamente in L
# ---------------------------------------------------------------------------

def test_attention_complexity_cresce_quadraticamente():
    """Raddoppiando L, con d fisso, FLOP e memoria devono tendere a
    quadruplicare: e' l'O(L^2 d) che rende il Transformer impraticabile sulle
    sequenze lunghe. Con d fisso e L grande il termine 8 L d^2 e' trascurabile."""
    d = 64

    flops, mem = m.attention_complexity(128, d)
    assert isinstance(flops, (int, np.integer)) and isinstance(mem, (int, np.integer)), \
        f"attention_complexity deve restituire due interi, ottenuto {type(flops)}, {type(mem)}"
    assert flops > 0 and mem > 0, "costi non positivi"

    # convenzione documentata: flops = 4 L^2 d + 8 L d^2, memoria = L^2 + 3 L d
    assert (flops, mem) == (4 * 128 * 128 * d + 8 * 128 * d * d, 128 * 128 + 3 * 128 * d), \
        (f"conteggio diverso da quello documentato nella docstring "
         f"(4 L^2 d + 8 L d^2, L^2 + 3 L d): ottenuto {(flops, mem)}")

    for L in (1000, 10000, 100000):
        f1, m1 = m.attention_complexity(L, d)
        f2, m2 = m.attention_complexity(2 * L, d)
        assert f2 > 2 * f1, \
            f"a L={L} il costo raddoppiando L cresce solo di {f2 / f1:.2f}x: non e' superlineare"
        assert m2 > 2 * m1, \
            f"a L={L} la memoria raddoppiando L cresce solo di {m2 / m1:.2f}x: non e' superlineare"

    f1, m1 = m.attention_complexity(100000, d)
    f2, m2 = m.attention_complexity(200000, d)
    assert 3.9 < f2 / f1 <= 4.0, \
        f"per L >> d il rapporto FLOP deve tendere a 4, ottenuto {f2 / f1:.3f}"
    assert 3.9 < m2 / m1 <= 4.0, \
        f"per L >> d il rapporto di memoria deve tendere a 4, ottenuto {m2 / m1:.3f}"

    # a L fisso il costo e' invece lineare nella dimensione delle chiavi solo
    # nel termine dei punteggi: raddoppiando d si resta ben sotto il 4x
    f_d, _ = m.attention_complexity(100000, d)
    f_2d, _ = m.attention_complexity(100000, 2 * d)
    assert f_2d / f_d < 2.5, \
        f"raddoppiando d il costo dovrebbe circa raddoppiare, ottenuto {f_2d / f_d:.2f}x"


# ---------------------------------------------------------------------------
# 12. (j) Cross-attention: lunghezze diverse fra query e key/value
# ---------------------------------------------------------------------------

def test_cross_attention_con_lunghezze_diverse():
    """Stessa funzione, due usi. In cross-attention le query vengono dal decoder
    (lunghezza 3) e chiavi/valori dall'encoder (lunghezza 7): l'output ha la
    lunghezza delle QUERY, i pesi hanno shape (Lq, Lkv). E' la differenza che
    fa capire perche' un decoder puo' produrre una frase piu' corta o piu'
    lunga della sorgente."""
    rng = np.random.default_rng(1012)
    d_model, n_heads = 8, 2
    Lq, Lkv = 3, 7

    X_q = rng.normal(size=(1, Lq, d_model))
    X_kv = rng.normal(size=(1, Lkv, d_model))
    Wq, Wk, Wv, Wo = _pesi_proiezione(d_model, rng)

    out, attn = m.multi_head_attention(X_q, X_kv, Wq, Wk, Wv, Wo, n_heads)

    assert out.shape == (1, Lq, d_model), \
        (f"in cross-attention l'output ha la lunghezza delle QUERY: attesa {(1, Lq, d_model)}, "
         f"ottenuta {out.shape}. Se hai ottenuto lunghezza {Lkv} hai scambiato X_q e X_kv")
    assert attn.shape == (1, n_heads, Lq, Lkv), \
        f"pesi attesi {(1, n_heads, Lq, Lkv)}, ottenuti {attn.shape}"
    assert_allclose(attn.sum(axis=-1), np.ones((1, n_heads, Lq)), rtol=1e-6, atol=1e-9,
                    err_msg="anche in cross-attention i pesi normalizzano sulle chiavi")

    # l'output e' una combinazione convessa dei valori dell'ENCODER: perturbare
    # X_kv cambia tutto, e X_q entra solo attraverso i pesi
    X_kv2 = X_kv.copy()
    X_kv2[0, 5] += 10.0
    out2, _ = m.multi_head_attention(X_q, X_kv2, Wq, Wk, Wv, Wo, n_heads)
    assert np.abs(out2 - out).max() > 1e-3, \
        "perturbare una posizione dell'encoder non cambia l'output: X_kv non fornisce i valori"

    # con X_q e X_kv lo stesso tensore si ricade nella self-attention: stessa
    # funzione, nessun ramo speciale
    out_self, attn_self = m.multi_head_attention(X_kv, X_kv, Wq, Wk, Wv, Wo, n_heads)
    assert out_self.shape == (1, Lkv, d_model) and attn_self.shape == (1, n_heads, Lkv, Lkv), (
        "passando lo stesso tensore come X_q e X_kv si deve ottenere self-attention, "
        "senza bisogno di un ramo di codice diverso")


# ---------------------------------------------------------------------------
# 13. Blocco encoder: post-LN e propagazione della causalita'
# ---------------------------------------------------------------------------

def test_transformer_encoder_block_post_ln():
    """Convenzione post-LN: l'ultima operazione del blocco e' una LayerNorm,
    quindi con gamma2=1 e beta2=0 l'output ha media 0 e varianza 1 sull'ultima
    dimensione. Con la convenzione pre-LN questo NON sarebbe vero.

    Inoltre la feed-forward e' position-wise: non mescola le posizioni, quindi
    la causalita' imposta nell'attenzione sopravvive fino all'uscita del
    blocco."""
    rng = np.random.default_rng(1013)
    N, L, d_model, d_ff, n_heads = 2, 6, 8, 16, 2

    params = m.make_encoder_params(d_model, d_ff, n_heads, rng)
    X = rng.normal(size=(N, L, d_model))
    Y = m.transformer_encoder_block(X, params)

    assert Y.shape == (N, L, d_model), \
        f"il blocco encoder preserva la shape: attesa {(N, L, d_model)}, ottenuta {Y.shape}"
    assert_allclose(Y.mean(axis=-1), np.zeros((N, L)), rtol=0, atol=1e-8,
                    err_msg="l'output non ha media 0 sull'ultima dimensione: con la convenzione "
                            "post-LN l'ULTIMA operazione del blocco deve essere una LayerNorm")
    assert_allclose(Y.var(axis=-1), np.ones((N, L)), rtol=0, atol=1e-4,
                    err_msg="l'output non ha varianza 1: manca la LayerNorm finale (pre-LN?) "
                            "oppure il residuo viene sommato dopo la norma")

    # il residuo conta: azzerare Wo lascia passare X attraverso il cammino
    # residuo, e l'output resta correlato con l'input normalizzato
    p0 = dict(params)
    p0["Wo"] = np.zeros((d_model, d_model))
    p0["W2"] = np.zeros((d_ff, d_model))
    Y0 = m.transformer_encoder_block(X, p0)
    assert_allclose(Y0, m.layer_norm(X, params["gamma1"], params["beta1"]),
                    rtol=0, atol=1e-4,
                    err_msg="annullando entrambi i sottomoduli deve restare solo il cammino "
                            "residuo (due LayerNorm in cascata, la seconda idempotente): "
                            "il residuo X + sottomodulo non c'e' o e' sommato male")

    # causalita' preservata attraverso il blocco intero
    mask = m.causal_mask(L)
    Y1 = m.transformer_encoder_block(X, params, mask=mask)
    Xp = X.copy()
    Xp[:, 4:, :] += 3.0
    Y2 = m.transformer_encoder_block(Xp, params, mask=mask)
    assert_allclose(Y2[:, :4], Y1[:, :4], rtol=1e-9, atol=1e-12,
                    err_msg="il blocco con maschera causale lascia filtrare informazione dal "
                            "futuro: o la maschera non viene passata alla self-attention, "
                            "o la feed-forward mescola le posizioni")
    assert np.abs(Y2[:, 4:] - Y1[:, 4:]).max() > 1e-3, \
        "la perturbazione non cambia nemmeno l'output futuro: il test e' vacuo"
