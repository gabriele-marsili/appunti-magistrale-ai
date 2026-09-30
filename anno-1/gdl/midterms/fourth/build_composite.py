"""Stitch the three priority paper figures (Table 2, Fig 3, Table 3) into one
composite PNG with panel letters and uniform spacing.

Layout:
    +------------------------------------------------+
    | (a) Table 2 - ZINC-250k targeting (full width) |
    +---------------------+--------------------------+
    | (b) Fig. 3 OOD      | (c) Table 3 optimization |
    +---------------------+--------------------------+

Originals are 600 DPI paper crops; the composite preserves them pixel-for-pixel
(no resizing of content, only canvas placement). White background, slate panel
letters. Run:
    ~/.pyenv/versions/3.12.6/bin/python3 build_composite.py
"""
from PIL import Image, ImageDraw, ImageFont

PAD = 40           # outer padding
GAP = 50           # gap between panels
LETTER_H = 70      # space reserved above each panel for the (a)/(b)/(c) label

# load originals
t2 = Image.open("figs/orig_table2_zinc.png")  # 3800 x 840
f3 = Image.open("figs/orig_fig3_ood.png")     # 3600 x 1100
t3 = Image.open("figs/orig_table3_optim.png") # 3500 x 1076

# canvas width = max(t2 width, f3+t3 widths + gap) + 2*PAD
bottom_w = f3.width + t3.width + GAP
canvas_w = max(t2.width, bottom_w) + 2 * PAD

# pad t2 horizontally to canvas, then bottom row scaled to canvas inner width
# To keep panels at their native resolution we set inner width = bottom_w and
# pad/center accordingly.
inner_w = max(t2.width, bottom_w)
canvas_w = inner_w + 2 * PAD

# heights
bottom_h = max(f3.height, t3.height)
canvas_h = PAD + LETTER_H + t2.height + GAP + LETTER_H + bottom_h + PAD

canvas = Image.new("RGB", (canvas_w, canvas_h), "white")
draw = ImageDraw.Draw(canvas)

try:
    font = ImageFont.truetype(
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf", 54
    )
except OSError:
    font = ImageFont.load_default()

SLATE = (51, 65, 91)


def place(img, x, y):
    canvas.paste(img, (x, y))


# (a) Table 2 - centered horizontally
y = PAD
draw.text((PAD, y), "(a)  ZINC-250k targeting", fill=SLATE, font=font)
y += LETTER_H
x_t2 = PAD + (inner_w - t2.width) // 2
place(t2, x_t2, y)

# (b) Fig 3 + (c) Table 3 row
y_bottom_label = y + t2.height + GAP
draw.text((PAD, y_bottom_label),
          "(b)  OOD validity", fill=SLATE, font=font)
draw.text((PAD + f3.width + GAP, y_bottom_label),
          "(c)  Graph-property optimization", fill=SLATE, font=font)

y_bottom = y_bottom_label + LETTER_H
# vertically center each within bottom_h
place(f3, PAD, y_bottom + (bottom_h - f3.height) // 2)
place(t3, PAD + f3.width + GAP, y_bottom + (bottom_h - t3.height) // 2)

out = "figs/composite_results.png"
canvas.save(out, optimize=True)
print(f"wrote {out} -- {canvas.size}")
