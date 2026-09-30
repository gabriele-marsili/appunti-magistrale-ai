"""Riesegue il codice di demo.ipynb (L7) e prova gli esercizi."""
import numpy as np
from scipy import signal
from skimage import data, img_as_float

import os
LAB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lab")

def frequency_grid(shape):
    fy = np.fft.fftfreq(shape[0]); fx = np.fft.fftfreq(shape[1])
    return np.meshgrid(fx, fy)

image = img_as_float(data.camera())[96:352, 128:384]
H, W = image.shape
y, x = np.indices(image.shape)
FX, FY = frequency_grid(image.shape)
radius = np.hypot(FX, FY)
print("shape", image.shape)

# cella 4: gratings
for kx, ky in [(12, 0), (0, 12), (12, 8)]:
    g = np.cos(2*np.pi*(kx*x/W + ky*y/H)); G = np.fft.fft2(g)
    big = np.argwhere(np.abs(G) > 1)
    print("grating", (kx, ky), "peaks (row,col)", big.tolist(), "mag", abs(G[ky % H, kx % W]), "HW/2", H*W/2)
# leakage con frequenza non intera
g = np.cos(2*np.pi*(12.5*x/W)); G = np.abs(np.fft.fft2(g))
print("leakage kx=12.5: bins >1% del max:", int((G > 0.01*G.max()).sum()), " contro 2 per kx=12")

# cella 7
F = np.fft.fft2(image)
rec = np.fft.ifft2(F).real
print("reco max err", np.max(abs(rec-image)), "DC/HW", F[0, 0].real/image.size, "mean", image.mean(),
      "Parseval", np.sum(image**2), np.sum(abs(F)**2)/image.size)

# cella 9
dy, dx = 27, -19
shifted = np.roll(image, (dy, dx), axis=(0, 1))
pred = np.fft.ifft2(F*np.exp(-2j*np.pi*(FY*dy + FX*dx))).real
print("shift ok", np.allclose(pred, shifted, atol=1e-12), np.allclose(abs(np.fft.fft2(shifted)), abs(F), atol=1e-10))

# cella 12: boundary. symm include il pixel di bordo?
a = np.array([[1., 2., 3.]])
k = np.zeros((1, 3)); k[0, 2] = 1  # con la convoluzione legge il vicino a sinistra
print("symm, vicino a sinistra del primo pixel:", signal.convolve2d(a, k, mode="same", boundary="symm")[0, 0],
      "(1 = ripete il bordo come np.pad symmetric, 2 = reflect)")
print("np.pad symmetric", np.pad([1, 2, 3], 2, mode="symmetric"), "reflect", np.pad([1, 2, 3], 2, mode="reflect"))
def gk(sigma, truncate=3):
    r = int(np.ceil(truncate*sigma)); t = np.arange(-r, r+1); q = np.exp(-t**2/(2*sigma**2)); q /= q.sum(); return np.outer(q, q)
hws = np.ones((16, 16)); hws[:, 8:] = 0
for b in ["fill", "wrap", "symm"]:
    bl = signal.convolve2d(hws, gk(3), mode="same", boundary=b)
    print(f"boundary {b}: pixel (8,0)={bl[8,0]:.3f} (8,15)={bl[8,15]:.3f} (0,0)={bl[0,0]:.3f}")

# cella 14
cutoff, sigma = 0.08, 2.0
ideal = (radius <= cutoff).astype(float)
smooth = np.exp(-2*np.pi**2*sigma**2*radius**2)
# la maschera gaussiana corrisponde a un kernel gaussiano spaziale sigma=2?
imp = np.zeros_like(image); imp[0, 0] = 1
ker = np.fft.ifft2(np.fft.fft2(imp)*smooth).real
ker_c = np.fft.fftshift(ker)
t = np.arange(W) - W//2
row = ker_c[H//2]; row = row/row.sum()
print("std del kernel spaziale della maschera gaussiana:", np.sqrt((row*t**2).sum()))
step = np.zeros_like(image); step[:, W//4:3*W//4] = 1
si = np.fft.ifft2(np.fft.fft2(step)*ideal).real
ss = np.fft.ifft2(np.fft.fft2(step)*smooth).real
print(f"ideal step range [{si.min():.3f},{si.max():.3f}]  gaussian [{ss.min():.4f},{ss.max():.4f}]")
print("frazione di coefficienti tenuti dal passa-basso ideale", ideal.mean())

# cella 16
high = np.fft.ifft2(F*(1-smooth)).real
sm_img = np.fft.ifft2(F*smooth).real
print("high+low=img", np.allclose(high+sm_img, image), "mean high", high.mean())

# cella 18
kx, ky = 37, 21
noise = .20*np.cos(2*np.pi*(kx*x/W + ky*y/H) + .4)
corr = image + noise
Fc = np.fft.fft2(corr)
def notch_mask(shape, fx0, fy0, width):
    fx, fy = frequency_grid(shape); m = np.ones(shape)
    for s in [-1, 1]:
        m *= 1 - np.exp(-((fx-s*fx0)**2 + (fy-s*fy0)**2)/(2*width**2))
    return m
mse = lambda a, b: float(np.mean((a-b)**2))
cl = np.fft.ifft2(Fc*notch_mask(image.shape, kx/W, ky/H, 1/W)).real
lp = np.fft.ifft2(Fc*smooth).real
print(f"MSE corrupted {mse(corr,image):.6f} notch {mse(cl,image):.6f} lowpass {mse(lp,image):.6f}  noise var teorica {0.2**2/2}")

# ===== Esercizio 1: corrupted_photo.npy
obs = np.load(f"{LAB}/corrupted_photo.npy")
print("corrupted_photo", obs.shape, obs.dtype, obs.min(), obs.max())
Fo = np.fft.fft2(obs - obs.mean())
mag = np.abs(Fo)
# confronto con camera crop: stessa immagine?
if obs.shape == image.shape:
    print("MSE vs camera crop", mse(obs, image))
fxg, fyg = frequency_grid(obs.shape)
rr = np.hypot(fxg, fyg)
cand = mag.copy(); cand[rr < 0.03] = 0
idx = np.argsort(cand.ravel())[::-1][:12]
Ho, Wo = obs.shape
for i in idx:
    r, c = np.unravel_index(i, obs.shape)
    print(f"  picco bin (ky,kx)=({np.fft.fftfreq(Ho)[r]*Ho:+.0f},{np.fft.fftfreq(Wo)[c]*Wo:+.0f}) |F|={mag[r,c]:.1f}")
# mediana dei moduli alla stessa distanza, per capire quanto sono anomali
print("mediana |F| a r in [0.1,0.4]:", np.median(mag[(rr > 0.1) & (rr < 0.4)]))
