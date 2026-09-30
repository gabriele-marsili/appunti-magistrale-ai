"""Genera le figure degli appunti L7 e stampa i numeri citati nel PDF.
Il codice replica le celle dei notebook in Lessons/L7/lab (demo, filter_bank).
Uso: python figs.py   (serve lab/data con Fashion-MNIST: lo scarica verifica_filter_bank.py o il notebook)."""
import os, gzip, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import signal
from skimage import data, img_as_float
from skimage.color import rgb2gray
from skimage.transform import resize

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.join(HERE, "..", "lab")
OUT = os.path.join(HERE, "fig")
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.size": 9, "axes.titlesize": 9.5, "figure.dpi": 150,
                     "axes.spines.top": False, "axes.spines.right": False})

def save(name):
    plt.tight_layout(); plt.savefig(f"{OUT}/{name}.pdf"); plt.close()

def frequency_grid(shape):
    fy = np.fft.fftfreq(shape[0]); fx = np.fft.fftfreq(shape[1])
    return np.meshgrid(fx, fy)

def spectrum(ax, F, title, vmax=None):
    values = np.log1p(np.abs(np.fft.fftshift(F)))
    h, w = F.shape
    fx = np.fft.fftshift(np.fft.fftfreq(w)); fy = np.fft.fftshift(np.fft.fftfreq(h))
    extent = [fx[0] - .5/w, fx[-1] + .5/w, fy[-1] + .5/h, fy[0] - .5/h]
    ax.imshow(values, cmap="magma", extent=extent, vmin=0, vmax=vmax)
    ax.set(title=title, xlabel="fx (cicli/pixel)", ylabel="fy (cicli/pixel)")

def show(ax, a, title, **kw):
    ax.imshow(a, cmap="gray", vmin=kw.get("vmin", 0), vmax=kw.get("vmax", 1)); ax.set_title(title); ax.set_axis_off()

mse = lambda a, b: float(np.mean((a - b) ** 2))
psnr = lambda a, b: 10*np.log10(1/mse(a, b))

# ================= demo.ipynb =================
image = img_as_float(data.camera())[96:352, 128:384]
H, W = image.shape
y, x = np.indices(image.shape)
FX, FY = frequency_grid(image.shape)
radius = np.hypot(FX, FY)
F = np.fft.fft2(image)

# 1. onde e spettri
fig, ax = plt.subplots(2, 4, figsize=(10, 5))
for col, (kx, ky) in enumerate([(12, 0), (0, 12), (12, 8), (12.5, 0)]):
    g = np.cos(2*np.pi*(kx*x/W + ky*y/H)); G = np.fft.fft2(g)
    show(ax[0, col], g, f"kx={kx}, ky={ky}", vmin=-1, vmax=1)
    spectrum(ax[1, col], G, "due picchi coniugati" if col < 3 else "kx non intero: leakage", vmax=np.log1p(H*W/2))
    ax[1, col].set_xlim(-.1, .1); ax[1, col].set_ylim(.1, -.1)
save("gratings")

# 2. immagine e spettro
fig, ax = plt.subplots(1, 2, figsize=(7, 3))
show(ax[0], image, "immagine (camera, 256x256)")
spectrum(ax[1], F, "log(1 + |F|), centrato con fftshift")
save("spectrum")

# 3. bordi
def gaussian_kernel_demo(sigma, truncate=3):
    r = int(np.ceil(truncate*sigma)); t = np.arange(-r, r+1)
    q = np.exp(-t**2/(2*sigma**2)); q /= q.sum(); return np.outer(q, q)
hws = np.ones((16, 16)); hws[:, 8:] = 0
fig, ax = plt.subplots(1, 4, figsize=(10, 2.8))
show(ax[0], hws, "ingresso")
for a, b, t in zip(ax[1:], ["fill", "wrap", "symm"], ["fill: zeri fuori", "wrap: periodica", "symm: specchio"]):
    show(a, signal.convolve2d(hws, gaussian_kernel_demo(3), mode="same", boundary=b), t)
save("boundary")

# 4. passa-basso ideale vs gaussiano
cutoff, sigma = 0.08, 2.0
ideal = (radius <= cutoff).astype(float)
smooth = np.exp(-2*np.pi**2*sigma**2*radius**2)
step = np.zeros_like(image); step[:, W//4:3*W//4] = 1
si = np.fft.ifft2(np.fft.fft2(step)*ideal).real; ss = np.fft.ifft2(np.fft.fft2(step)*smooth).real
fig = plt.figure(figsize=(10, 5.4))
gs = fig.add_gridspec(2, 3)
show(fig.add_subplot(gs[0, 0]), image, "originale")
show(fig.add_subplot(gs[0, 1]), np.clip(np.fft.ifft2(F*ideal).real, 0, 1), "passa-basso ideale (r <= 0.08)")
show(fig.add_subplot(gs[0, 2]), np.fft.ifft2(F*smooth).real, "passa-basso gaussiano (sigma = 2)")
a = fig.add_subplot(gs[1, 0]); a.imshow(np.fft.fftshift(ideal), cmap="gray"); a.set_title("maschera ideale (centrata)"); a.set_axis_off()
a = fig.add_subplot(gs[1, 1]); a.imshow(np.fft.fftshift(smooth), cmap="gray"); a.set_title("maschera gaussiana (centrata)"); a.set_axis_off()
a = fig.add_subplot(gs[1, 2])
for s, lab in [(step, "ingresso"), (si, "ideale"), (ss, "gaussiano")]:
    a.plot(s[H//2], label=lab)
a.set(xlim=(W//4-25, W//4+35), xlabel="colonna", title="risposta a un bordo"); a.legend(fontsize=7)
save("lowpass")
print(f"step ideale [{si.min():.3f}, {si.max():.3f}], gaussiano [{ss.min():.4f}, {ss.max():.4f}]")

# 5. passa-alto
high = np.fft.ifft2(F*(1-smooth)).real
fig, ax = plt.subplots(1, 3, figsize=(9, 3))
show(ax[0], image, "originale")
show(ax[1], np.fft.ifft2(F*smooth).real, "basse frequenze")
m = np.abs(high).max(); ax[2].imshow(high, cmap="RdBu_r", vmin=-m, vmax=m); ax[2].set_title("residuo alte (con segno)"); ax[2].set_axis_off()
save("highpass")

# 6. interferenza del notebook
def notch_mask(shape, fx0, fy0, width):
    fx, fy = frequency_grid(shape); m = np.ones(shape)
    for s in [-1, 1]:
        m *= 1 - np.exp(-((fx - s*fx0)**2 + (fy - s*fy0)**2)/(2*width**2))
    return m
kx, ky = 37, 21
corrupted = image + .20*np.cos(2*np.pi*(kx*x/W + ky*y/H) + .4)
Fc = np.fft.fft2(corrupted)
cleaned = np.fft.ifft2(Fc*notch_mask(image.shape, kx/W, ky/H, 1/W)).real
lp = np.fft.ifft2(Fc*smooth).real
fig, ax = plt.subplots(1, 4, figsize=(11, 2.9))
show(ax[0], np.clip(corrupted, 0, 1), f"corrotta, MSE {mse(corrupted, image):.4f}")
spectrum(ax[1], Fc, "picchi dell'onda")
for s in [-1, 1]:
    ax[1].plot(s*kx/W, s*ky/H, "co", fillstyle="none", markersize=11)
show(ax[2], cleaned, f"notch, MSE {mse(cleaned, image):.6f}")
show(ax[3], lp, f"passa-basso, MSE {mse(lp, image):.4f}")
save("notch_demo")
print(f"notebook: MSE corrotta {mse(corrupted, image):.6f} notch {mse(cleaned, image):.6f} passa-basso {mse(lp, image):.6f}")

# 7. esercizio: corrupted_photo.npy
obs = np.load(os.path.join(LAB, "corrupted_photo.npy"))
Fo = np.fft.fft2(obs)
fx_o, fy_o = frequency_grid(obs.shape); rr = np.hypot(fx_o, fy_o)
cand = np.abs(Fo).copy(); cand[rr < 0.05] = 0
r0, c0 = np.unravel_index(np.argmax(cand), obs.shape)
KY, KX = int(round(np.fft.fftfreq(obs.shape[0])[r0]*obs.shape[0])), int(round(np.fft.fftfreq(obs.shape[1])[c0]*obs.shape[1]))
amp = 2*np.abs(Fo[r0, c0])/obs.size
print(f"esercizio: picco in (ky,kx) = ({KY},{KX}) e coniugato, ampiezza onda {amp:.3f}, fase {np.angle(Fo[r0, c0]):.2f} rad")
ref = rgb2gray(img_as_float(data.coffee()))
ref = resize(ref, obs.shape, anti_aliasing=True)
clean_o = np.fft.ifft2(Fo*notch_mask(obs.shape, KX/obs.shape[1], KY/obs.shape[0], 1/obs.shape[1])).real
blur_o = np.fft.ifft2(Fo*smooth).real
print(f"esercizio: MSE vs coffee ridimensionata: osservata {mse(obs, ref):.6f}, notch {mse(clean_o, ref):.2e}, gaussiano {mse(blur_o, ref):.6f}")
fig, ax = plt.subplots(1, 4, figsize=(11, 2.9))
show(ax[0], np.clip(obs, 0, 1), "corrupted_photo.npy")
spectrum(ax[1], Fo, f"picchi in (ky,kx) = ±({KY},{KX})")
ax[1].plot([KX/obs.shape[1], -KX/obs.shape[1]], [KY/obs.shape[0], -KY/obs.shape[0]], "co", fillstyle="none", markersize=11)
show(ax[2], clean_o, f"notch, MSE {mse(clean_o, ref):.1e}")
show(ax[3], blur_o, f"gaussiano, MSE {mse(blur_o, ref):.4f}")
save("notch_exercise")

# 8. esercizio: compressione (Fig 16.8 visionbook)
fig, ax = plt.subplots(1, 5, figsize=(11, 2.6))
show(ax[0], image, "originale")
comp = []
mag = np.abs(F).ravel(); order = np.sort(mag)[::-1]
for a, keep in zip(ax[1:], [0.20, 0.05, 0.01, 0.002]):
    thr = order[int(keep*mag.size) - 1]
    rec = np.fft.ifft2(np.where(np.abs(F) >= thr, F, 0)).real
    comp.append((keep, mse(rec, image), psnr(np.clip(rec, 0, 1), image)))
    show(a, np.clip(rec, 0, 1), f"tengo {keep*100:g}% ({int(keep*mag.size)} coeff.)")
save("compression")
for keep, e, p in comp:
    print(f"compressione: tengo {keep*100:g}% -> MSE {e:.5f}, PSNR {p:.1f} dB")

# ================= filter_bank.ipynb =================
def load(name):
    f = {"x": "train-images-idx3-ubyte.gz", "y": "train-labels-idx1-ubyte.gz"}[name]
    raw = gzip.open(os.path.join(LAB, "data", f)).read()
    if name == "x": return np.frombuffer(raw, np.uint8, offset=16).reshape(-1, 28, 28).astype(np.float32)/255
    return np.frombuffer(raw, np.uint8, offset=8).astype(np.int64)
X_all, y_all = load("x"), load("y")
perm = np.random.default_rng(1234567).permutation(len(X_all))
X_train, y_train = X_all[perm[:20000]], y_all[perm[:20000]]
CLASSES = ["T-shirt/top", "Trouser", "Pullover", "Dress", "Coat", "Sandal", "Shirt", "Sneaker", "Bag", "Ankle boot"]

identity = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]], float)
box = np.ones((3, 3))/9
sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], float); sobel_y = sobel_x.T
sobel_d45 = np.array([[0, 1, 2], [-1, 0, 1], [-2, -1, 0]], float)
sobel_d135 = np.array([[-2, -1, 0], [-1, 0, 1], [0, 1, 2]], float)
lap = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], float)

def gaussian_kernel(sigma):
    R = int(np.ceil(3*sigma)); X, Y = np.meshgrid(np.arange(-R, R+1), np.arange(-R, R+1))
    G = np.exp(-(X**2 + Y**2)/(2*sigma**2)); return G/G.sum()
def gaussian_derivative_kernel(sigma, order):
    R = int(np.ceil(3*sigma)); X, Y = np.meshgrid(np.arange(-R, R+1), np.arange(-R, R+1))
    G = gaussian_kernel(sigma); s2 = sigma**2
    return {"x": -X/s2*G, "y": -Y/s2*G, "xx": (X**2/s2**2 - 1/s2)*G, "yy": (Y**2/s2**2 - 1/s2)*G, "xy": X*Y/s2**2*G}[order]
def gabor_kernel(sigma, theta, wavelength, phase=0.0):
    R = int(np.ceil(3*sigma)); X, Y = np.meshgrid(np.arange(-R, R+1), np.arange(-R, R+1))
    Xr = X*np.cos(theta) + Y*np.sin(theta); Yr = -X*np.sin(theta) + Y*np.cos(theta)
    g = np.exp(-(Xr**2 + Yr**2)/(2*sigma**2))*np.cos(2*np.pi*Xr/wavelength + phase)
    g = g - g.mean(); return g/np.abs(g).sum()

def kshow(ax, k, t):
    m = np.abs(k).max() + 1e-12; ax.imshow(k, cmap="RdBu_r", vmin=-m, vmax=m); ax.set_title(t, fontsize=7); ax.set_axis_off()

# 9. banchi di filtri
bank1 = [(identity, "identity"), (box, "box"), (sobel_x, "sobel x"), (sobel_y, "sobel y"),
         (sobel_d45, "sobel 45"), (sobel_d135, "sobel 135"), (lap, "laplaciano")]
gdb = [(gaussian_kernel(2), "G s=2")] + [(gaussian_derivative_kernel(2, o), f"G{o} s=2") for o in ["x", "y", "xx", "yy", "xy"]]
gab = [(gabor_kernel(3, th, 8, p), f"{np.degrees(th):.0f}° {'pari' if p == 0 else 'dispari'}")
       for th in np.arange(4)*np.pi/4 for p in (0, np.pi/2)]
fig, ax = plt.subplots(3, 8, figsize=(10, 4.3))
for r, row in enumerate([bank1, gdb, gab]):
    for c in range(8):
        if c < len(row): kshow(ax[r, c], *row[c])
        else: ax[r, c].set_axis_off()
ax[0, 7].text(0, .5, "3x3\n(baseline +\nesercizio 1)", fontsize=7, transform=ax[0, 7].transAxes)
ax[1, 7].text(0, .5, "derivate\ngaussiane\n(13x13)", fontsize=7, transform=ax[1, 7].transAxes)
save("banks")

# 10. risposte su un'immagine: filtro -> |.| -> pool 4
img = X_train[np.where(y_train == 1)[0][0]]  # un pantalone
def conv(im, k): return signal.fftconvolve(im, k, mode="same")
def pool4(r): return r.reshape(7, 4, 7, 4).mean(axis=(1, 3))
sel = [(identity, "identity"), (sobel_x, "sobel x"), (sobel_y, "sobel y"), (sobel_d45, "sobel 45"), (lap, "laplaciano")]
fig, ax = plt.subplots(3, 6, figsize=(9, 4.8))
ax[0, 0].imshow(img, cmap="gray"); ax[0, 0].set_title("ingresso (Trouser)", fontsize=8)
for a in ax.flat: a.set_xticks([]); a.set_yticks([])
ax[1, 0].set_axis_off(); ax[2, 0].set_axis_off()
for i, (k, t) in enumerate(sel):
    r = conv(img, k); m = np.abs(r).max() + 1e-12
    ax[0, i+1].imshow(r, cmap="RdBu_r", vmin=-m, vmax=m); ax[0, i+1].set_title(t, fontsize=8)
    ax[1, i+1].imshow(np.abs(r), cmap="magma")
    ax[2, i+1].imshow(pool4(np.abs(r)), cmap="magma")
ax[0, 1].set_ylabel("x * w", fontsize=8); ax[1, 1].set_ylabel("|x * w|", fontsize=8); ax[2, 1].set_ylabel("avg pool 4 (7x7)", fontsize=8)
save("responses")

# 11. risultati (dal json prodotto da verifica_filter_bank.py)
R = json.load(open(os.path.join(HERE, "risultati_filter_bank.json")))
for p in "ABCDE":  # eventuali riesecuzioni parziali sovrascrivono i valori salvati
    fp = os.path.join(HERE, f"risultati_filter_bank_{p}.json")
    if os.path.exists(fp): R.update(json.load(open(fp)))
pool_sizes = [1, 2, 4, 7, 14, 28]
fig, ax = plt.subplots(1, 2, figsize=(10, 3.2))
accs = [R[f"ex1 bank, abs, avg pool {p}"][0] for p in pool_sizes]
feats = [R[f"ex1 bank, abs, avg pool {p}"][1] for p in pool_sizes]
ax[0].plot(pool_sizes, accs, "o-", label="avg pool")
ax[0].plot([2, 4, 7], [R[f"ex1 bank, abs, max pool {p}"][0] for p in [2, 4, 7]], "s--", label="max pool")
ax[0].axhline(R["pixels (identity, none, pool 1)"][0], color="0.5", ls=":", label="pixel grezzi")
for p, a_, f_ in zip(pool_sizes, accs, feats):
    ax[0].annotate(f"{f_}", (p, a_), textcoords="offset points", xytext=(4, -10), fontsize=6.5)
ax[0].set_xscale("log"); ax[0].set_xticks(pool_sizes); ax[0].set_xticklabels(pool_sizes)
ax[0].set(xlabel="pool size (numeri = n. feature)", ylabel="val accuracy", title="banco 7 filtri 3x3, abs")
ax[0].legend(fontsize=7)
nl = ["none", "abs", "square", "rectify"]
ax[1].bar(nl, [R[f"ex1 bank, {n}, pool 4"][0] for n in nl], color=["0.6", "C0", "C1", "C2"])
ax[1].axhline(R["pixels (identity, none, pool 1)"][0], color="0.3", ls=":", label="pixel grezzi")
ax[1].set_ylim(0.78, 0.88); ax[1].set(title="non linearità (pool 4)", ylabel="val accuracy"); ax[1].legend(fontsize=7)
for i, n in enumerate(nl):
    ax[1].text(i, R[f"ex1 bank, {n}, pool 4"][0] + 0.002, f"{R[f'ex1 bank, {n}, pool 4'][0]:.3f}", ha="center", fontsize=7)
save("pooling")
print("OK")
