"""Visual mock-up of box 3 (Experiments) for the GrIDDD poster.

Standalone preview so the student can see how the humanized text + the original
paper figures look together inside one A0 poster box. NOT the deliverable -- the
real work goes into the Group5 SharePoint deck. Exported to mockup_box3.pdf.

Run:
    ~/.pyenv/versions/3.12.6/bin/python3 mockup_box3.py
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from PIL import Image

CYAN = RGBColor(0x0E, 0x74, 0x90)
CYAN_BG = RGBColor(0xEC, 0xFE, 0xFF)
DARK = RGBColor(0x0F, 0x17, 0x2A)
SLATE = RGBColor(0x33, 0x41, 0x5B)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
INCH = 914400

# A single box from the A0 poster: roughly half-width, full-height column.
prs = Presentation()
prs.slide_width = Inches(15)
prs.slide_height = Inches(20)
slide = prs.slides.add_slide(prs.slide_layouts[6])

# ---- box background -------------------------------------------------------
box = slide.shapes.add_shape(1, Inches(0.4), Inches(0.4),
                             Inches(14.2), Inches(19.2))
box.fill.solid()
box.fill.fore_color.rgb = CYAN_BG
box.line.color.rgb = CYAN
box.line.width = Pt(3)
box.shadow.inherit = False


def textbox(left, top, width, height, blocks, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top),
                                  Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for i, (text, opts) in enumerate(blocks):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = opts.get("align", PP_ALIGN.LEFT)
        p.space_after = Pt(opts.get("after", 6))
        p.space_before = Pt(opts.get("before", 0))
        run = p.add_run()
        run.text = text
        f = run.font
        f.size = Pt(opts["size"])
        f.bold = opts.get("bold", False)
        f.italic = opts.get("italic", False)
        f.color.rgb = opts.get("color", SLATE)
        f.name = "Calibri"
    return tb


def add_img(path, left, top, max_w, max_h, caption=None):
    im = Image.open(path)
    ar = im.width / im.height
    w, h = max_w, max_w / ar
    if h > max_h:
        h, w = max_h, max_h * ar
    pic_left = left + (max_w - w) / 2
    slide.shapes.add_picture(path, Inches(pic_left), Inches(top),
                             Inches(w), Inches(h))
    bottom = top + h
    if caption:
        textbox(left, bottom + 0.04, max_w, 0.7,
                [(caption, {"size": 12, "italic": True, "color": SLATE,
                            "align": PP_ALIGN.CENTER, "after": 0})])
        bottom += 0.55
    return bottom


# ---- section title --------------------------------------------------------
textbox(0.8, 0.7, 13.4, 1.4, [
    ("3 · Experiments", {"size": 40, "bold": True, "color": CYAN, "after": 4}),
    ("Datasets, baselines, metrics, and key results.",
     {"size": 22, "bold": True, "color": DARK}),
])

# ---- body text (humanized) ------------------------------------------------
body = [
    ("Datasets & protocol", {"size": 24, "bold": True, "color": DARK, "before": 4, "after": 2}),
    ("QM9 (≤9 atoms) and ZINC-250k (drug-like). 500 diffusion steps, "
     "classifier-free guidance (λ = 3 on QM9, 2 on ZINC). Targeting: 100 "
     "target properties × 10 molecules, scored by MAE. Optimization (Jin et "
     "al.): corrupt for 100 steps, denoise toward the target, keep the best "
     "candidate above a Tanimoto threshold.",
     {"size": 19, "color": SLATE, "after": 10}),

    ("Baselines", {"size": 24, "bold": True, "color": DARK, "after": 2}),
    ("FreeGress and DiGress for targeting; JT-VAE, CG-VAE, GCPN for "
     "optimization. All use a fixed-size denoiser. GrIDDD is the only one that "
     "can insert and delete atoms.",
     {"size": 19, "color": SLATE, "after": 10}),

    ("Property targeting (MAE ↓)", {"size": 24, "bold": True, "color": DARK, "after": 2}),
    ("QM9 μ: 0.66 vs 0.74 (FreeGress). ZINC MW: 4.89 vs 8.96, roughly half the "
     "error, and without giving the model the target size in advance. Validity "
     "holds or improves in most settings.",
     {"size": 19, "color": SLATE, "after": 10}),

    ("Optimization, OOD & ablation", {"size": 24, "bold": True, "color": DARK, "after": 2}),
    ("QED success 45.1% vs 9.4% (GCPN), about 5×. LogP improvement 2.70. Out "
     "of distribution, GrIDDD stays 35% valid at 15 atoms (trained only up to "
     "14); DiGress drops to near zero. Switch insertion/deletion off and QED "
     "success falls 45.1 → 33.8%, so the size control is doing the work.",
     {"size": 19, "color": SLATE, "after": 6}),
]
textbox(0.8, 2.3, 13.4, 6.2, body)

# ---- figures (originals from the paper) -----------------------------------
y = 8.9
y = add_img("figs/orig_table1_qm9.png", 0.8, y, 6.5, 2.4,
            "Table 1 — property targeting on QM9 (Ninniri et al., 2025).")
y2 = add_img("figs/orig_table2_zinc.png", 7.6, 8.9, 6.6, 2.4,
             "Table 2 — property targeting on ZINC-250k.")
y = max(y, y2)

y = add_img("figs/orig_fig3_ood.png", 0.8, y + 0.2, 6.7, 3.6,
            "Fig. 3 — out-of-distribution validity vs molecule size.")
add_img("figs/orig_table3_optim.png", 7.6, 11.7, 6.6, 3.4,
        "Table 3 — property optimization on ZINC-250k.")

prs.save("mockup_box3.pptx")
print("wrote mockup_box3.pptx")
