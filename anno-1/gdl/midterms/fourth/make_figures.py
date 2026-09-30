"""Crop figures from the paper PDF and synthesize the bar chart for box 4."""
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

OUT = Path("figs")
OUT.mkdir(exist_ok=True)

# --- Crops from rasterized PDF pages (300 DPI, 2550x3300 px) ---------------
# All coords are (left, upper, right, lower).
CROPS = {
    "fig1_qualitative.png":   ("figs/page2-02.png",  (350, 230, 2300,  570)),
    "fig2_matrices.png":      ("figs/page5-05.png",  (170, 220, 2410, 1100)),
    "table1_qm9.png":         ("figs/page8-08.png",  (600, 2310, 1950, 2790)),
    "table2_zinc.png":        ("figs/page9-09.png",  (300, 680, 2200, 1100)),
    "fig3_ood.png":           ("figs/page9-09.png",  (350, 1470, 2150, 2020)),
    "table3_optim.png":       ("figs/page10-10.png", (400, 120, 2150, 650)),
}
for out_name, (src, box) in CROPS.items():
    img = Image.open(src).crop(box)
    img.save(OUT / out_name)
    print(f"  {out_name}  {img.size}")

# --- Composite for box 3: Table1 + Table2 + Table3 stacked, then Fig3 -----
def hstack(imgs, gap=20, bg=(255, 255, 255)):
    h = max(i.height for i in imgs)
    w = sum(i.width for i in imgs) + gap * (len(imgs) - 1)
    out = Image.new("RGB", (w, h), bg)
    x = 0
    for i in imgs:
        out.paste(i, (x, (h - i.height) // 2))
        x += i.width + gap
    return out

def vstack(imgs, gap=30, bg=(255, 255, 255)):
    w = max(i.width for i in imgs)
    h = sum(i.height for i in imgs) + gap * (len(imgs) - 1)
    out = Image.new("RGB", (w, h), bg)
    y = 0
    for i in imgs:
        out.paste(i, ((w - i.width) // 2, y))
        y += i.height + gap
    return out

t1 = Image.open(OUT / "table1_qm9.png")
t2 = Image.open(OUT / "table2_zinc.png")
f3 = Image.open(OUT / "fig3_ood.png")

# Layout: [ Table1 | Table2 ] on top, Fig3 spanning below.
# This gives a composite AR ~2.1 that matches the figure-box AR on the
# poster, so the image scales up to nearly fill the box.
def fit_h(im, h):
    s = h / im.height
    return im.resize((int(im.width * s), h))

row_h = max(t1.height, t2.height)
t1h = fit_h(t1, row_h)
t2h = fit_h(t2, row_h)
top_row = hstack([t1h, t2h], gap=60)
def fit_w(im, w):
    s = w / im.width
    return im.resize((w, int(im.height * s)))
f3f = fit_w(f3, top_row.width)
box3 = vstack([top_row, f3f], gap=50)
box3.save(OUT / "box3_composite.png")
print(f"  box3_composite.png  {box3.size}")

# --- Box 4: bar chart of MAE reduction vs FreeGress per property ----------
# Numbers from paper Tables 1 and 2.
# Property -> (FreeGress MAE, GrIDDD MAE)
data = [
    (r"$\mu$ (QM9)",   0.74, 0.66),
    ("HOMO (QM9)",     0.32, 0.37),
    ("LogP (ZINC)",    0.17, 0.19),
    ("QED (ZINC)",     0.04, 0.04),
    ("MW (ZINC)",      8.96, 4.89),
]
labels = [d[0] for d in data]
free   = [d[1] for d in data]
grid   = [d[2] for d in data]
reduction = [(f - g) / f * 100 for f, g in zip(free, grid)]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": [3, 2]})

x = np.arange(len(labels))
w = 0.38
ax1.bar(x - w / 2, free, w, label="FreeGress", color="#40B7D8")
ax1.bar(x + w / 2, grid, w, label="GrIDDD",    color="#F5B51B")
ax1.set_yscale("log")
ax1.set_ylabel("Target MAE (log scale)")
ax1.set_xticks(x)
ax1.set_xticklabels(labels, rotation=20, ha="right")
ax1.set_title("Property targeting: GrIDDD vs FreeGress")
ax1.legend(frameon=False)
ax1.grid(axis="y", linestyle=":", alpha=0.4)

colors = ["#52616B" if r <= 0 else "#005B96" for r in reduction]
ax2.barh(labels, reduction, color=colors)
ax2.axvline(0, color="#102A43", linewidth=0.8)
ax2.set_xlabel("MAE reduction vs FreeGress (%)")
ax2.set_title("Where size-adaptation pays off")
ax2.set_xlim(-25, 55)
for i, r in enumerate(reduction):
    # Place all labels on the right of the bar end to avoid clashing with y-tick labels.
    ax2.text(r + 1.5, i, f"{r:+.0f}%",
             va="center", ha="left",
             fontsize=11, color="#102A43", fontweight="bold")
ax2.tick_params(axis="y", labelsize=11)
ax2.grid(axis="x", linestyle=":", alpha=0.4)
ax2.invert_yaxis()

plt.tight_layout()
plt.savefig(OUT / "box4_mae_reduction.png", dpi=200, bbox_inches="tight",
            facecolor="white")
plt.close()
print(f"  box4_mae_reduction.png saved")
