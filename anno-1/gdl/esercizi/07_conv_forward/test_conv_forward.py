"""Test di autovalutazione - GDL15-16 "Convolutional Neural Networks".

Esecuzione:
    pytest test_conv_forward.py -v                # sullo skeleton
    GDL_SOL=1 pytest test_conv_forward.py -v      # sulla soluzione di riferimento
"""

import os, sys, pathlib, importlib

HERE = pathlib.Path(__file__).parent
if os.environ.get("GDL_SOL"):
    sys.path.insert(0, str(HERE / "soluzione"))
    m = importlib.import_module("conv_forward_sol")
else:
    sys.path.insert(0, str(HERE))
    m = importlib.import_module("conv_forward")

import numpy as np
from numpy.testing import assert_allclose


# ---------------------------------------------------------------------------
# Combinazioni (stride, padding, dilation) usate dai test (a) e (b).
# Comprendono stride=2 e dilation=2 insieme, che e' il caso in cui quasi tutte
# le implementazioni sbagliate si rompono.
# ---------------------------------------------------------------------------

COMBINAZIONI = [
    (1, 0, 1),
    (1, 1, 1),
    (2, 0, 1),
    (2, 1, 1),
    (1, 2, 2),
    (2, 2, 2),   # <- stride e dilation insieme
    (3, 1, 1),
    (2, 3, 3),
]


def _dati(seed=7):
    """Input e kernel NON quadrati: cosi' uno scambio di assi si vede subito."""
    rng = np.random.default_rng(seed)
    x = rng.standard_normal((2, 3, 11, 13))
    w = rng.standard_normal((4, 3, 3, 2))
    b = rng.standard_normal(4)
    return x, w, b


# ---------------------------------------------------------------------------
# (a) ORACOLO: conv2d vettorizzata == conv2d_naive a quattro cicli.
# ---------------------------------------------------------------------------

def test_conv2d_coincide_con_oracolo_naive():
    """`conv2d` (im2col + matmul) deve dare gli stessi numeri della definizione
    scritta a cicli, su tutte le combinazioni di stride/padding/dilation."""
    x, w, b = _dati()
    for (s, p, d) in COMBINAZIONI:
        atteso = m.conv2d_naive(x, w, b, stride=s, padding=p, dilation=d)
        ottenuto = m.conv2d(x, w, b, stride=s, padding=p, dilation=d)
        assert ottenuto.shape == atteso.shape, (
            f"stride={s} padding={p} dilation={d}: shape {ottenuto.shape}, "
            f"attesa {atteso.shape} (quasi sempre e' la formula di output_shape "
            f"o uno scambio fra asse H e asse W)"
        )
        assert_allclose(
            ottenuto, atteso, rtol=1e-6, atol=1e-9,
            err_msg=(
                f"stride={s} padding={p} dilation={d}: conv2d non coincide con "
                f"conv2d_naive. Se sbaglia solo con dilation>1 stai confondendo "
                f"il kernel con il kernel EFFETTIVO d*(K-1)+1; se sbaglia solo "
                f"con stride>1 stai saltando le finestre sbagliate."
            ),
        )

    # senza bias deve funzionare uguale
    assert_allclose(
        m.conv2d(x, w, None, stride=2, padding=1, dilation=2),
        m.conv2d_naive(x, w, None, stride=2, padding=1, dilation=2),
        rtol=1e-6, atol=1e-9,
        err_msg="con bias=None il bias non va aggiunto, non va messo a zero e basta",
    )


# ---------------------------------------------------------------------------
# (b) La formula della geometria deve descrivere l'output vero.
# ---------------------------------------------------------------------------

def test_output_shape_predice_la_shape_effettiva():
    """`output_shape` non e' un promemoria: deve coincidere con la shape che
    `conv2d` produce davvero, su entrambi gli assi e su tutte le combinazioni."""
    x, w, _ = _dati()
    H, W = x.shape[2], x.shape[3]
    KH, KW = w.shape[2], w.shape[3]
    for (s, p, d) in COMBINAZIONI:
        y = m.conv2d(x, w, None, stride=s, padding=p, dilation=d)
        h_pred = m.output_shape(H, KH, s, p, d)
        w_pred = m.output_shape(W, KW, s, p, d)
        assert (h_pred, w_pred) == (y.shape[2], y.shape[3]), (
            f"stride={s} padding={p} dilation={d}: output_shape predice "
            f"{(h_pred, w_pred)} ma conv2d produce {(y.shape[2], y.shape[3])}"
        )

    # casi noti a memoria: 'same' per kernel dispari, e il dimezzamento
    assert m.output_shape(28, 3, 1, 1, 1) == 28, (
        "kernel 3, stride 1, padding 1 e' il padding 'same': la dimensione non cambia"
    )
    assert m.output_shape(28, 2, 2, 0, 1) == 14, (
        "un pooling 2x2 con stride 2 dimezza la dimensione spaziale"
    )
    assert m.output_shape(7, 3, 2, 0, 1) == 3, (
        "la divisione e' un FLOOR: le finestre parziali finali vengono scartate"
    )


# ---------------------------------------------------------------------------
# (c) EQUIVARIANZA ALLA TRASLAZIONE. E' la ragione d'essere della convoluzione.
# ---------------------------------------------------------------------------

def test_convoluzione_equivariante_alla_traslazione():
    """Se traslo l'input di (a, b) pixel, l'output si trasla di (a, b) pixel.

    La verifica e' su una regione INTERNA, lontana dai bordi: il padding rompe
    l'equivarianza solo li', perche' il bordo non e' traslato con il resto.
    """
    rng = np.random.default_rng(11)
    x = rng.standard_normal((2, 3, 17, 19))
    w = rng.standard_normal((4, 3, 3, 3))
    b = rng.standard_normal(4)

    a, c = 2, 3                      # traslazione: 2 pixel in H, 3 in W
    y = m.conv2d(x, w, b, stride=1, padding=1)
    x_shift = np.roll(np.roll(x, a, axis=2), c, axis=3)
    y_shift = m.conv2d(x_shift, w, b, stride=1, padding=1)

    interno = (slice(None), slice(None), slice(5, 15), slice(6, 17))
    atteso = np.roll(np.roll(y, a, axis=2), c, axis=3)
    assert_allclose(
        y_shift[interno], atteso[interno], rtol=1e-6, atol=1e-9,
        err_msg=(
            "conv(shift(x)) != shift(conv(x)) nell'interno: la convoluzione NON "
            "e' equivariante alla traslazione nella tua implementazione. Di "
            "solito significa che i pesi non sono condivisi allo stesso modo in "
            "tutte le posizioni, o che l'indicizzazione delle finestre e' "
            "sfasata."
        ),
    )

    # controprova: la traslazione ha spostato davvero qualcosa
    assert not np.allclose(y_shift[interno], y[interno]), (
        "il test e' vuoto se l'output traslato coincide con quello originale: "
        "l'input di prova non e' abbastanza vario"
    )


# ---------------------------------------------------------------------------
# (d) Il max pooling e' equivariante SOLO per shift multipli dello stride.
# ---------------------------------------------------------------------------

def test_maxpool_equivariante_solo_a_multipli_dello_stride():
    """Il subsampling rompe l'equivarianza a grana fine: sposta di 1 pixel e
    l'output non e' piu' una traslazione di se stesso; sposta di 2 (= stride) e
    lo e' esattamente."""
    rng = np.random.default_rng(23)
    x = rng.standard_normal((1, 2, 8, 12))

    y = m.max_pool2d(x, 2)            # stride = kernel_size = 2

    # shift multiplo dello stride -> l'output trasla esattamente di shift/stride
    x2 = np.roll(x, 2, axis=3)
    y2 = m.max_pool2d(x2, 2)
    assert_allclose(
        y2, np.roll(y, 1, axis=3), rtol=1e-6, atol=1e-9,
        err_msg=(
            "traslando l'input di 2 pixel (= stride) l'output del pooling deve "
            "traslare di esattamente 1 cella: se non succede, la griglia delle "
            "finestre non parte da 0 o lo stride di default non e' kernel_size"
        ),
    )

    # shift NON multiplo dello stride -> l'output non e' traslazione di nulla
    x1 = np.roll(x, 1, axis=3)
    y1 = m.max_pool2d(x1, 2)
    distanze = [
        float(np.max(np.abs(y1 - np.roll(y, t, axis=3)))) for t in range(y.shape[3])
    ]
    assert min(distanze) > 1e-6, (
        "traslando l'input di 1 pixel (non multiplo dello stride) l'output del "
        "max pooling coincide con una traslazione dell'output originale: e' "
        "impossibile con finestre disgiunte, il pooling sta probabilmente "
        "usando stride 1"
    )


# ---------------------------------------------------------------------------
# (e) Caso banale: 1x1 su un canale solo == moltiplicazione per uno scalare.
# ---------------------------------------------------------------------------

def test_conv_1x1_monocanale_e_una_moltiplicazione_scalare():
    """Con C_in = C_out = 1 e kernel 1x1 la convoluzione degenera in `alpha*x`
    (piu' il bias): nessuna aggregazione spaziale, nessun bordo."""
    rng = np.random.default_rng(101)
    x = rng.standard_normal((3, 1, 6, 5))
    alpha = -1.7
    w = np.array([[[[alpha]]]])

    assert_allclose(
        m.conv2d(x, w), alpha * x, rtol=1e-6, atol=1e-9,
        err_msg="conv 1x1 monocanale deve valere esattamente alpha * x",
    )
    assert_allclose(
        m.conv2d(x, w, np.array([0.5])), alpha * x + 0.5, rtol=1e-6, atol=1e-9,
        err_msg="il bias e' uno scalare per canale di USCITA, sommato a tutte le posizioni",
    )

    # una 1x1 con piu' canali e' una combinazione lineare fra canali, pixel per pixel
    x3 = rng.standard_normal((2, 3, 4, 4))
    w3 = rng.standard_normal((5, 3, 1, 1))
    atteso = np.einsum("oc,nchw->nohw", w3[:, :, 0, 0], x3)
    assert_allclose(
        m.conv2d(x3, w3), atteso, rtol=1e-6, atol=1e-9,
        err_msg="una conv 1x1 e' un layer lineare applicato indipendentemente a ogni pixel",
    )


# ---------------------------------------------------------------------------
# (f) Kernel identita' (delta di Dirac) con padding 'same'.
# ---------------------------------------------------------------------------

def test_kernel_delta_di_dirac_e_identita_e_rivela_il_ribaltamento():
    """Un delta al centro con padding 'same' lascia l'input invariato; un delta
    NON centrato trasla l'immagine, e la DIREZIONE della traslazione distingue
    la cross-correlazione dalla convoluzione matematica."""
    rng = np.random.default_rng(5)
    x = rng.standard_normal((2, 1, 7, 7))

    delta = np.zeros((1, 1, 3, 3))
    delta[0, 0, 1, 1] = 1.0
    assert_allclose(
        m.conv2d(x, delta, padding=1), x, rtol=1e-6, atol=1e-9,
        err_msg="delta di Dirac centrato + padding 1 su kernel 3x3 = identita'",
    )

    # delta in posizione (0, 0): out[i, j] = xpad[i, j] = x[i-1, j-1]
    delta00 = np.zeros((1, 1, 3, 3))
    delta00[0, 0, 0, 0] = 1.0
    y = m.conv2d(x, delta00, padding=1)
    assert_allclose(
        y[:, :, 1:, 1:], x[:, :, :-1, :-1], rtol=1e-6, atol=1e-9,
        err_msg=(
            "con un delta in (0,0) la cross-correlazione sposta l'immagine in "
            "BASSO-DESTRA di un pixel. Se ottieni lo spostamento opposto stai "
            "ribaltando il kernel, cioe' hai implementato la convoluzione "
            "matematica invece della cross-correlazione di PyTorch"
        ),
    )
    assert_allclose(
        y[:, :, 0, :], 0.0, atol=1e-12,
        err_msg="la prima riga deve venire dallo zero-padding",
    )


# ---------------------------------------------------------------------------
# (g) CAMPO RECETTIVO: la formula contro la misura empirica.
# ---------------------------------------------------------------------------

def _rf_empirico(layers, W=41):
    """Conta quante colonne di input influenzano UN pixel di output.

    Costruisce la pila di convoluzioni descritta da `layers` con pesi tutti 1 e
    padding 0 (cosi' nessun contributo puo' cancellarsi e la finestra non viene
    tagliata dai bordi), parte da un input nullo e perturba una colonna alla
    volta.  E' la definizione di campo recettivo, misurata.
    """
    x0 = np.zeros((1, 1, W, W))

    def propaga(x):
        h = x
        for (k, s, d) in layers:
            w = np.ones((1, 1, k, k))
            h = m.conv2d(h, w, None, stride=s, padding=0, dilation=d)
        return h

    y0 = propaga(x0)
    i0, j0 = y0.shape[2] // 2, y0.shape[3] // 2
    n = 0
    for j in range(W):
        xp = x0.copy()
        xp[:, :, :, j] = 1.0
        if abs(float(propaga(xp)[0, 0, i0, j0]) - float(y0[0, 0, i0, j0])) > 1e-12:
            n += 1
    return n


def test_receptive_field_coincide_con_la_misura_empirica():
    """La ricorrenza del campo recettivo deve prevedere quanti pixel di input
    toccano davvero un pixel di output: e' cio' che spiega perche' due 3x3
    valgono un 5x5, e perche' la dilation allarga la vista a parita' di pesi."""
    casi = [
        [(3, 1, 1), (3, 1, 1)],              # due 3x3 impilate -> 5
        [(3, 2, 1), (3, 1, 1)],              # lo stride moltiplica il jump -> 7
        [(3, 1, 2), (3, 1, 1)],              # dilation 2 -> 7 senza parametri in piu'
        [(3, 2, 1), (3, 1, 2), (2, 1, 1)],   # tutto insieme -> 13
    ]
    attesi = [5, 7, 7, 13]
    for layers, atteso in zip(casi, attesi):
        r = m.receptive_field(layers)
        assert r == atteso, f"receptive_field({layers}) = {r}, atteso {atteso}"
        r_emp = _rf_empirico(layers)
        assert r == r_emp, (
            f"receptive_field({layers}) dice {r} ma perturbando l'input i pixel "
            f"che influenzano un'uscita sono {r_emp}. Errore tipico: sommare gli "
            f"stride invece di moltiplicarli, o ignorare la dilation"
        )

    assert m.receptive_field([]) == 1, "senza layer un'uscita vede un solo pixel"
    assert m.receptive_field([(5, 1, 1)]) == 5, "un solo 5x5 vede 5 pixel"


# ---------------------------------------------------------------------------
# (h) im2col: le colonne sono davvero le patch.
# ---------------------------------------------------------------------------

def test_im2col_shape_e_colonne_uguali_alle_patch():
    """Ogni colonna della matrice deve essere la finestra di input appiattita,
    con l'ordine (c, u, v) C-major che rende corretto il prodotto con
    `weight.reshape(C_out, -1)`."""
    rng = np.random.default_rng(31)
    N, C, H, W = 2, 2, 5, 6
    KH, KW, s, p, d = 3, 2, 2, 1, 2
    x = rng.standard_normal((N, C, H, W))

    H_out = m.output_shape(H, KH, s, p, d)
    W_out = m.output_shape(W, KW, s, p, d)
    cols = m.im2col(x, KH, KW, s, p, d)
    assert cols.shape == (C * KH * KW, N * H_out * W_out), (
        f"im2col deve avere shape (C*KH*KW, N*H_out*W_out) = "
        f"{(C*KH*KW, N*H_out*W_out)}, ottenuta {cols.shape}"
    )

    # patch estratte a mano dall'input paddato, senza usare pad2d
    xpad = np.zeros((N, C, H + 2 * p, W + 2 * p))
    xpad[:, :, p : p + H, p : p + W] = x
    for n in range(N):
        for i in range(H_out):
            for j in range(W_out):
                col = (n * H_out + i) * W_out + j
                patch = np.empty(C * KH * KW)
                for c in range(C):
                    for u in range(KH):
                        for v in range(KW):
                            patch[(c * KH + u) * KW + v] = xpad[
                                n, c, i * s + u * d, j * s + v * d
                            ]
                assert_allclose(
                    cols[:, col], patch, rtol=1e-6, atol=1e-9,
                    err_msg=(
                        f"la colonna {col} (n={n}, i={i}, j={j}) non e' la patch "
                        f"corrispondente: controlla l'ordine degli indici "
                        f"(c*KH + u)*KW + v e il fatto che dilation moltiplica "
                        f"u e v, mentre stride moltiplica i e j"
                    ),
                )


# ---------------------------------------------------------------------------
# (i) BatchNorm in inferenza.
# ---------------------------------------------------------------------------

def test_batchnorm_inference_normalizza_per_canale():
    """Con gamma=1, beta=0 e le statistiche VERE del tensore, l'uscita ha media
    0 e varianza 1 per canale (non globalmente: per canale)."""
    rng = np.random.default_rng(77)
    x = rng.standard_normal((6, 3, 5, 4)) * np.array([0.5, 3.0, 10.0]).reshape(1, 3, 1, 1)
    x = x + np.array([-4.0, 0.0, 7.0]).reshape(1, 3, 1, 1)

    mu = x.mean(axis=(0, 2, 3))
    var = x.var(axis=(0, 2, 3))          # varianza di popolazione, ddof=0
    C = x.shape[1]
    y = m.batchnorm2d_inference(x, np.ones(C), np.zeros(C), mu, var)

    assert y.shape == x.shape, f"la BN non cambia la shape: attesa {x.shape}, ottenuta {y.shape}"
    assert_allclose(
        y.mean(axis=(0, 2, 3)), np.zeros(C), atol=1e-8,
        err_msg="media per canale non nulla: le statistiche vanno applicate PER CANALE "
                "(broadcast su (1, C, 1, 1)), non sull'intero tensore",
    )
    assert_allclose(
        y.var(axis=(0, 2, 3)), np.ones(C), atol=1e-4,
        err_msg="varianza per canale diversa da 1: probabile normalizzazione sull'asse "
                "sbagliato, o divisione per la varianza invece che per la deviazione standard",
    )

    # la parte affine: gamma e beta rimettono scala e offset scelti
    gamma = np.array([2.0, -3.0, 0.5])
    beta = np.array([1.0, 0.0, -4.0])
    y2 = m.batchnorm2d_inference(x, gamma, beta, mu, var)
    assert_allclose(
        y2.mean(axis=(0, 2, 3)), beta, atol=1e-8,
        err_msg="dopo la normalizzazione la media per canale deve valere beta",
    )
    assert_allclose(
        y2.std(axis=(0, 2, 3)), np.abs(gamma), atol=1e-4,
        err_msg="dopo la normalizzazione la deviazione standard per canale deve valere |gamma|",
    )


# ---------------------------------------------------------------------------
# (j) Caso limite: input 1x1, kernel 1x1.
# ---------------------------------------------------------------------------

def test_caso_limite_un_pixel():
    """Il caso piu' degenere possibile: una sola posizione spaziale. Tutta la
    pipeline deve reggere senza shape fantasma."""
    x = np.array([[[[3.0]]]])                 # (1, 1, 1, 1)
    w = np.array([[[[2.0]]]])                 # (1, 1, 1, 1)

    assert m.output_shape(1, 1, 1, 0, 1) == 1, "1 pixel, kernel 1, stride 1 -> 1 pixel"
    y = m.conv2d(x, w, np.array([-1.0]))
    assert y.shape == (1, 1, 1, 1), f"shape attesa (1,1,1,1), ottenuta {y.shape}"
    assert_allclose(y, np.array([[[[5.0]]]]), rtol=1e-6, atol=1e-9,
                    err_msg="2*3 - 1 = 5")

    assert m.im2col(x, 1, 1).shape == (1, 1), "im2col di un pixel e' una matrice 1x1"
    assert_allclose(m.pad2d(x, 1)[0, 0], np.array([[0.0, 0.0, 0.0],
                                                   [0.0, 3.0, 0.0],
                                                   [0.0, 0.0, 0.0]]),
                    rtol=1e-6, atol=1e-9,
                    err_msg="pad2d(1) su un pixel deve dare una 3x3 con il valore al centro")
    assert_allclose(m.max_pool2d(x, 1), x, rtol=1e-6, atol=1e-9,
                    err_msg="un max pooling 1x1 e' l'identita'")
    assert_allclose(m.avg_pool2d(x, 1), x, rtol=1e-6, atol=1e-9,
                    err_msg="un average pooling 1x1 e' l'identita'")
    assert m.flatten(x).shape == (1, 1), "flatten di (1,1,1,1) e' (1,1)"
    assert_allclose(m.relu(np.array([[-2.0, 0.0, 3.0]])), np.array([[0.0, 0.0, 3.0]]),
                    rtol=1e-6, atol=1e-9, err_msg="relu(x) = max(x, 0)")


# ---------------------------------------------------------------------------
# Pooling: media esatta, e il conteggio degli zeri di padding.
# ---------------------------------------------------------------------------

def test_avg_pool_media_esatta_e_maxpool_con_padding_negativo():
    """L'average pool e' una media aritmetica sulle finestre, con gli zeri di
    padding CONTATI nel denominatore; il max pool invece deve paddare a -inf."""
    x = np.arange(16, dtype=float).reshape(1, 1, 4, 4)

    atteso = np.array([[[[2.5, 4.5], [10.5, 12.5]]]])
    assert_allclose(
        m.avg_pool2d(x, 2), atteso, rtol=1e-6, atol=1e-9,
        err_msg="media 2x2 con finestre disgiunte: (0+1+4+5)/4 = 2.5",
    )
    assert_allclose(
        m.max_pool2d(x, 2), np.array([[[[5.0, 7.0], [13.0, 15.0]]]]),
        rtol=1e-6, atol=1e-9, err_msg="massimo 2x2 con finestre disgiunte",
    )

    # con padding 1, l'angolo alto-sinistro dell'avg pool vede 3 zeri e x[0,0]
    a = m.avg_pool2d(x, 2, stride=2, padding=1)
    assert_allclose(
        a[0, 0, 0, 0], 0.0, atol=1e-12,
        err_msg="con count_include_pad il primo valore e' (0+0+0+0)/4 = 0",
    )

    # max pooling su input TUTTO NEGATIVO: con padding a zero uscirebbero degli 0
    neg = -np.abs(np.arange(1, 17, dtype=float)).reshape(1, 1, 4, 4)
    p = m.max_pool2d(neg, 2, stride=2, padding=1)
    assert np.all(p < 0.0), (
        "il max pooling ha restituito uno 0 su un input tutto negativo: stai "
        "paddando con zeri invece che con -inf, e lo zero vince il massimo"
    )
    assert_allclose(
        p[0, 0, 0, 0], -1.0, rtol=1e-6, atol=1e-9,
        err_msg="la prima finestra paddata contiene solo x[0,0] = -1 e tre -inf",
    )


# ---------------------------------------------------------------------------
# Pipeline completa: forward_lenet contro una composizione lenta e indipendente.
# ---------------------------------------------------------------------------

def _lenet_lento(x, params):
    """Oracolo del forward completo: `conv2d_naive` (fornito) + cicli espliciti."""
    pk = params["pool_size"]
    ps = params["pool_stride"]

    def pool(h):
        N, C, H, W = h.shape
        Ho, Wo = (H - pk) // ps + 1, (W - pk) // ps + 1
        o = np.empty((N, C, Ho, Wo))
        for n in range(N):
            for c in range(C):
                for i in range(Ho):
                    for j in range(Wo):
                        o[n, c, i, j] = h[n, c, i*ps:i*ps+pk, j*ps:j*ps+pk].max()
        return o

    h = m.conv2d_naive(x, params["conv1_w"], params["conv1_b"],
                       stride=1, padding=params["conv1_padding"])
    h = pool(np.where(h > 0, h, 0.0))
    h = m.conv2d_naive(h, params["conv2_w"], params["conv2_b"],
                       stride=1, padding=params["conv2_padding"])
    h = pool(np.where(h > 0, h, 0.0))

    N = h.shape[0]
    f = np.empty((N, h.shape[1] * h.shape[2] * h.shape[3]))
    for n in range(N):
        k = 0
        for c in range(h.shape[1]):
            for i in range(h.shape[2]):
                for j in range(h.shape[3]):
                    f[n, k] = h[n, c, i, j]
                    k += 1
    g = np.where(f @ params["fc1_w"].T + params["fc1_b"] > 0,
                 f @ params["fc1_w"].T + params["fc1_b"], 0.0)
    return g @ params["fc2_w"].T + params["fc2_b"]


def test_forward_lenet_coincide_con_la_composizione_lenta():
    """Il forward completo deve dare gli stessi logit della stessa rete montata
    a mano con l'oracolo naive: shape intermedie, ordine del flatten e
    orientamento di `fc1_w` compresi."""
    rng = np.random.default_rng(2024)
    params = m.make_lenet_params(rng, in_channels=1, image_size=16,
                                 c1=3, c2=4, hidden=6, n_classes=5)
    x = rng.standard_normal((3, 1, 16, 16))

    y = m.forward_lenet(x, params)
    assert y.shape == (3, 5), (
        f"logit attesi di shape (3, 5), ottenuti {y.shape}: se il flatten o "
        f"l'orientamento di fc1_w sono sbagliati la shape salta prima"
    )
    assert_allclose(
        y, _lenet_lento(x, params), rtol=1e-6, atol=1e-9,
        err_msg=(
            "il forward non coincide con la composizione di riferimento. "
            "Sospetti nell'ordine: flatten non C-major, `linear` che usa "
            "weight invece di weight.T, ReLU applicata dopo il pooling invece "
            "che prima, o attivazione applicata anche all'ultimo layer"
        ),
    )
