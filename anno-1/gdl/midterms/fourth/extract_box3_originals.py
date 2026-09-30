"""Extract the ORIGINAL paper figures/tables for box 3 at print resolution.

Rasterizes the relevant paper pages at 600 DPI (vector source -> crisp) and
crops the figures/tables faithfully, so the poster shows exactly what the
authors reported (safer than redrawing, since a co-author reviews the poster).

Run:
    ~/.pyenv/versions/3.12.6/bin/python3 extract_box3_originals.py
"""
import subprocess
from pathlib import Path
from PIL import Image

DPI = 600
SCALE = DPI / 300            # crop boxes below are in 300-DPI coords
FIGS = Path("figs")
FIGS.mkdir(exist_ok=True)

# page number (1-based) -> rasterized file stem
PAGES = {8: "p8_600", 9: "p9_600", 10: "p10_600"}
for pg, stem in PAGES.items():
    subprocess.run(["pdftoppm", "-png", "-r", str(DPI),
                    "-f", str(pg), "-l", str(pg),
                    "paper.pdf", str(FIGS / stem)], check=True)

# resolve the actual filenames pdftoppm produced (zero-padded page suffix)
def page_file(stem):
    hits = sorted(FIGS.glob(stem + "*.png"))
    if not hits:
        raise FileNotFoundError(stem)
    return hits[0]

# out_name -> (page, box in 300-DPI coords)  -- refined to trim stray lines
CROPS = {
    "orig_table1_qm9.png":  (8,  (600, 2388, 1950, 2792)),
    "orig_table2_zinc.png": (9,  (300,  680, 2200, 1100)),
    "orig_fig3_ood.png":    (9,  (350, 1470, 2150, 2020)),
    "orig_table3_optim.png":(10, (400,  300, 2150,  838)),
}

for out, (pg, box) in CROPS.items():
    src = Image.open(page_file(PAGES[pg]))
    sbox = tuple(int(v * SCALE) for v in box)
    src.crop(sbox).save(FIGS / out)
    print("wrote", FIGS / out, src.crop(sbox).size)

# clean up the big full-page rasters
for stem in PAGES.values():
    page_file(stem).unlink()
