"""Riesegue filter_bank.ipynb (L7) con le soluzioni ricostruite; confronta con gli output salvati."""
import os, gzip, time, urllib.request, sys, json
import numpy as np
from scipy import signal
from sklearn.linear_model import RidgeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import warnings
from scipy.linalg import LinAlgWarning
warnings.filterwarnings("ignore", category=LinAlgWarning)

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(HERE, "..", "lab"))  # come il notebook: scarica in lab/data
SEED = 1234567
DATA_DIR = "data"
URL = "https://raw.githubusercontent.com/zalandoresearch/fashion-mnist/master/data/fashion/"
FILES = {"train_x": "train-images-idx3-ubyte.gz", "train_y": "train-labels-idx1-ubyte.gz",
         "test_x": "t10k-images-idx3-ubyte.gz", "test_y": "t10k-labels-idx1-ubyte.gz"}

def load_data(name):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, FILES[name])
    if not os.path.exists(path):
        print("downloading", FILES[name]); urllib.request.urlretrieve(URL + FILES[name], path)
    with gzip.open(path) as f: raw = f.read()
    if name.endswith("_x"):
        return np.frombuffer(raw, np.uint8, offset=16).reshape(-1, 28, 28).astype(np.float32) / 255.0
    return np.frombuffer(raw, np.uint8, offset=8).astype(np.int64)

X_all, y_all = load_data("train_x"), load_data("train_y")
X_test, y_test = load_data("test_x"), load_data("test_y")
perm = np.random.default_rng(SEED).permutation(len(X_all))
X_train, y_train = X_all[perm[:20000]], y_all[perm[:20000]]
X_val, y_val = X_all[perm[50000:]], y_all[perm[50000:]]

NONLINEARITIES = {"none": lambda r: [r], "abs": lambda r: [np.abs(r)], "square": lambda r: [r ** 2],
                  "rectify": lambda r: [np.maximum(r, 0)]}
def convolve(X, kernel):
    return signal.fftconvolve(X, np.asarray(kernel, np.float32)[None], mode="same", axes=(1, 2))
def pool(R, size, kind="avg"):
    N, H, W = R.shape
    R = R[:, :H // size * size, :W // size * size].reshape(N, H // size, size, W // size, size)
    R = R.mean(axis=(2, 4)) if kind == "avg" else R.max(axis=(2, 4))
    return R.reshape(N, -1)
def extract_features(X, bank, nonlinearity="abs", pool_size=4, pool_type="avg", power=1.0):
    feats = []
    for k in bank:
        for r in NONLINEARITIES[nonlinearity](convolve(X, k)):
            feats.append(pool(r, pool_size, pool_type))
    F = np.concatenate(feats, axis=1)
    if power != 1.0: F = np.sign(F) * np.abs(F) ** power
    return F
def fit_and_score(F_tr, y_tr, F_ev, y_ev, alpha=1.0):
    clf = make_pipeline(StandardScaler(), RidgeClassifier(alpha=alpha)); clf.fit(F_tr, y_tr); return clf.score(F_ev, y_ev)
RES = {}
def evaluate(bank, name, **cfg):
    t = time.time()
    F_tr, F_val = extract_features(X_train, bank, **cfg), extract_features(X_val, bank, **cfg)
    acc = fit_and_score(F_tr, y_train, F_val, y_val)
    print(f"{name:<45s} val acc = {acc:.4f}   #features = {F_tr.shape[1]:5d}   ({time.time()-t:.1f}s)", flush=True)
    RES[name] = (acc, F_tr.shape[1]); return acc

identity = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]], float)
box = np.ones((3, 3)) / 9
sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], float)
sobel_y = sobel_x.T
baseline_bank = [identity, box, sobel_x, sobel_y]
sobel_d45 = np.array([[0, 1, 2], [-1, 0, 1], [-2, -1, 0]], float)
sobel_d135 = np.array([[-2, -1, 0], [-1, 0, 1], [0, 1, 2]], float)
lap4 = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], float)
lap8 = np.array([[1, 1, 1], [1, -8, 1], [1, 1, 1]], float)

def gaussian_kernel(sigma):
    R = int(np.ceil(3 * sigma)); X, Y = np.meshgrid(np.arange(-R, R + 1), np.arange(-R, R + 1))
    G = np.exp(-(X**2 + Y**2) / (2 * sigma**2)); return G / G.sum()
def gaussian_derivative_kernel(sigma, order):
    R = int(np.ceil(3 * sigma)); X, Y = np.meshgrid(np.arange(-R, R + 1), np.arange(-R, R + 1))
    G = gaussian_kernel(sigma); s2 = sigma**2
    return {"x": -X / s2 * G, "y": -Y / s2 * G, "xx": (X**2 / s2**2 - 1 / s2) * G,
            "yy": (Y**2 / s2**2 - 1 / s2) * G, "xy": X * Y / s2**2 * G}[order]
def gd(sigmas):
    b = []
    for s in sigmas:
        b += [gaussian_kernel(s)] + [gaussian_derivative_kernel(s, o) for o in ["x", "y", "xx", "yy", "xy"]]
    return [identity] + b
def gabor_kernel(sigma, theta, wavelength, phase=0.0):
    R = int(np.ceil(3 * sigma)); X, Y = np.meshgrid(np.arange(-R, R + 1), np.arange(-R, R + 1))
    Xr = X * np.cos(theta) + Y * np.sin(theta); Yr = -X * np.sin(theta) + Y * np.cos(theta)
    g = np.exp(-(Xr**2 + Yr**2) / (2 * sigma**2)) * np.cos(2 * np.pi * Xr / wavelength + phase)
    g = g - g.mean(); return g / np.abs(g).sum()
def gabor_bank(n_orient, scales=((1.5, 4), (3, 8)), phases=(0, np.pi / 2)):
    return [gabor_kernel(s, th, lam, p) for s, lam in scales for th in np.arange(n_orient) * np.pi / n_orient for p in phases]

part = sys.argv[1] if len(sys.argv) > 1 else "all"
if part in ("A", "all"):
    evaluate([identity], "pixels (identity, none, pool 1)", nonlinearity="none", pool_size=1)
    evaluate(baseline_bank, "baseline (id, box, sobel x/y)")
    evaluate(baseline_bank[1:], "baseline senza identity")
    evaluate([identity], "solo identity, abs, pool 4")
    evaluate(baseline_bank + [sobel_d45, sobel_d135], "baseline + diagonals")
    evaluate(baseline_bank + [lap4], "baseline + laplacian (4-vicini)")
    evaluate(baseline_bank + [lap8], "baseline + laplacian (8-vicini)")
    evaluate(baseline_bank + [sobel_d45, sobel_d135, lap4], "baseline + diagonals + laplacian4")
    evaluate(baseline_bank + [sobel_d45, sobel_d135, lap8], "baseline + diagonals + laplacian8")
if part in ("B", "all"):
    evaluate(gd([1, 2]), "gauss-deriv s={1,2}")
    evaluate(gd([1]), "gauss-deriv s=1")
    evaluate(gd([2]), "gauss-deriv s=2")
    evaluate(gd([0.7, 1, 2, 3]), "gauss-deriv s={0.7,1,2,3}")
    for n in [2, 4, 8]:
        evaluate([identity] + gabor_bank(n), f"gabor {n} orient")
if part in ("C", "all"):
    ex1 = baseline_bank + [sobel_d45, sobel_d135, lap4]
    for nl in ["none", "abs", "square", "rectify"]:
        evaluate(ex1, f"ex1 bank, {nl}, pool 4", nonlinearity=nl)
    evaluate(ex1, "ex1 bank, none, pool 1", nonlinearity="none", pool_size=1)
    evaluate(ex1, "ex1 bank, abs, pool 1", nonlinearity="abs", pool_size=1)
    for p in [1, 2, 4, 7, 14, 28]:
        evaluate(ex1, f"ex1 bank, abs, avg pool {p}", pool_size=p)
    for p in [2, 4, 7]:
        evaluate(ex1, f"ex1 bank, abs, max pool {p}", pool_size=p, pool_type="max")
    evaluate(ex1, "ex1 bank, abs, pool 4, power 0.5", power=0.5)
if part in ("D", "all"):
    rng = np.random.default_rng(0)
    def random_bank(n, size=5):
        return [rng.standard_normal((size, size)) for _ in range(n)]
    for n in [4, 13, 34]:
        evaluate(random_bank(n), f"random {n} filters 5x5 (seed 0)")
    evaluate([identity] + gabor_bank(8), "gabor 8 | power 0.5", power=0.5)
if part in ("E", "all"):
    X_trval, y_trval = np.concatenate([X_train, X_val]), np.concatenate([y_train, y_val])
    for name, bank, cfg in [("pixels", [identity], dict(nonlinearity="none", pool_size=1)),
                            ("baseline", baseline_bank, {}),
                            ("baseline power .5", baseline_bank, dict(power=0.5)),
                            ("gabor 8 power .5", [identity] + gabor_bank(8), dict(power=0.5))]:
        acc = fit_and_score(extract_features(X_trval, bank, **cfg), y_trval, extract_features(X_test, bank, **cfg), y_test)
        print(f"{name:<20s} TEST accuracy = {acc:.4f}", flush=True); RES["TEST " + name] = (acc, None)
json.dump(RES, open(os.path.join(HERE, f"risultati_filter_bank_{part}.json"), "w"), indent=1)
