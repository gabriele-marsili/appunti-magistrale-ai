"""Two layout variants for box 3 (Experiments) — A0 poster, half-width column.

A = single composite figure (Table 2 + Fig 3 + Table 3 stitched, one anchor).
B = three figures stacked vertically (Table 2, Fig 3, Table 3 separate).

Both share the same humanized text. Outputs:
    mockup_box3_A.pptx / mockup_box3_B.pptx

Run:
    ~/.pyenv/versions/3.12.6/bin/python3 mockup_box3_v2.py
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from PIL import Image

CYAN = RGBColor(0x0E, 0x74, 0x90)
CYAN_BG = RGBColor(0xEC, 0xFE, 0xFF)
DARK = RGBColor(0x0F, 0x17, 0x2A)
SLATE = RGBColor(0x33, 0x41, 0x5B)

# Half of an A0 poster (A0 = 33.1 x 46.8 in landscape, so half-width column
# ~ 16 x 23 in portrait). Slide proxies that column.
SLIDE_W = 16
SLIDE_H = 23


def textbox(slide, left, top, width, height, blocks, anchor=MSO_ANCHOR.TOP):
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


def add_img(slide, path, left, top, max_w, max_h, caption=None):
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
        textbox(slide, left, bottom + 0.05, max_w, 0.55,
                [(caption, {"size": 13, "italic": True, "color": SLATE,
                            "align": PP_ALIGN.CENTER, "after": 0})])
        bottom += 0.55
    return bottom


# ---- humanized text (shared) ---------------------------------------------
BODY = [
    ("Setup",
     {"size": 26, "bold": True, "color": DARK, "before": 4, "after": 2}),
    ("QM9 (small organics, up to 9 atoms) and ZINC-250k (drug-like). 500 "
     "diffusion steps; classifier-free guidance, λ = 3 on QM9, λ = 2 on ZINC. "
     "Two tasks. Targeting: 100 property values × 10 molecules each, scored "
     "by MAE. Optimization (Jin et al.): corrupt for 100 steps, denoise "
     "toward the target, keep the best candidate above a Tanimoto threshold.",
     {"size": 19, "color": SLATE, "after": 12}),

    ("Baselines",
     {"size": 26, "bold": True, "color": DARK, "after": 2}),
    ("FreeGress and DiGress for targeting; JT-VAE, CG-VAE, GCPN for "
     "optimization. All operate on a fixed graph size. GrIDDD is the only "
     "model that can insert and delete atoms while sampling.",
     {"size": 19, "color": SLATE, "after": 12}),

    ("Targeting accuracy",
     {"size": 26, "bold": True, "color": DARK, "after": 2}),
    ("GrIDDD lowers MAE on both targeting benchmarks. QM9 dipole moment μ: "
     "0.66 vs 0.74 (FreeGress). ZINC molecular weight: 4.89 vs 8.96, roughly "
     "half the error of the strongest baseline, with no target size supplied "
     "to the model at inference.",
     {"size": 19, "color": SLATE, "after": 12}),

    ("Optimization, OOD, ablation",
     {"size": 26, "bold": True, "color": DARK, "after": 2}),
    ("On graph-property optimization, QED success reaches 45.1% against 9.4% "
     "for GCPN, and LogP improvement is 2.70. Out of distribution, where "
     "models are trained up to 14 atoms, GrIDDD still produces 35% valid "
     "molecules at size 15; DiGress collapses to near zero. Removing "
     "insertion and deletion takes QED success from 45.1% to 33.8%, so size "
     "control, not the diffusion backbone alone, is what produces the gains.",
     {"size": 19, "color": SLATE, "after": 6}),
]

TITLE = [
    ("3 · Experiments",
     {"size": 44, "bold": True, "color": CYAN, "after": 4}),
    ("Datasets, baselines, and key results.",
     {"size": 22, "bold": True, "color": DARK}),
]


def build(layout):
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_W)
    prs.slide_height = Inches(SLIDE_H)
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # outer box
    pad = 0.4
    box = slide.shapes.add_shape(
        1, Inches(pad), Inches(pad),
        Inches(SLIDE_W - 2 * pad), Inches(SLIDE_H - 2 * pad))
    box.fill.solid()
    box.fill.fore_color.rgb = CYAN_BG
    box.line.color.rgb = CYAN
    box.line.width = Pt(3)
    box.shadow.inherit = False

    # title
    textbox(slide, 0.8, 0.7, SLIDE_W - 1.6, 1.4, TITLE)

    # body
    textbox(slide, 0.8, 2.4, SLIDE_W - 1.6, 7.0, BODY)

    if layout == "A":
        # single composite figure
        y0 = 10.0
        add_img(slide, "figs/composite_results.png",
                0.8, y0, SLIDE_W - 1.6, SLIDE_H - y0 - 1.2,
                "Quantitative results: (a) ZINC-250k targeting; "
                "(b) out-of-distribution validity vs molecule size; "
                "(c) graph-property optimization (Ninniri et al., 2025).")
        out = "mockup_box3_A.pptx"

    elif layout == "B":
        # three stacked figures
        y = 10.0
        avail = SLIDE_W - 1.6
        y = add_img(slide, "figs/orig_table2_zinc.png",
                    0.8, y, avail, 3.6,
                    "Table 2 — property targeting on ZINC-250k.")
        y = add_img(slide, "figs/orig_fig3_ood.png",
                    0.8, y + 0.3, avail, 4.0,
                    "Fig. 3 — out-of-distribution validity.")
        add_img(slide, "figs/orig_table3_optim.png",
                0.8, y + 0.3, avail, 3.8,
                "Table 3 — graph-property optimization.")
        out = "mockup_box3_B.pptx"

    prs.save(out)
    print(f"wrote {out}")


for variant in ("A", "B"):
    build(variant)
