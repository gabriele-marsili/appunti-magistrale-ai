"""Fill the GDL midterm 4 poster template for the GrIDDD paper."""
import subprocess
from copy import deepcopy
from pathlib import Path
from pptx import Presentation
from pptx.util import Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_AUTO_SIZE
from PIL import Image

SRC = "gdl_midterm4_poster_template.pptx"
DST = "GrIDDD_poster.pptx"

prs = Presentation(SRC)
slide = prs.slides[0]

# ---- helpers --------------------------------------------------------------

def find_by_text(slide, needle):
    """Return first shape whose text contains needle."""
    for s in slide.shapes:
        if s.has_text_frame and needle in s.text_frame.text:
            return s
    return None

def set_text(shape, paragraphs, *, base_size=15, bold_first=False,
             color=RGBColor(0x52, 0x61, 0x6B), align=None):
    """Replace shape text with given paragraphs.

    paragraphs: list of either strings or (text, opts) tuples where opts can
    set bold/size/color/italic per-paragraph.
    """
    tf = shape.text_frame
    # Disable auto-shrink: PowerPoint's default TEXT_TO_FIT silently scales
    # down fonts when content overflows. We want our explicit sizes honored.
    try:
        tf.auto_size = MSO_AUTO_SIZE.NONE
        tf.word_wrap = True
    except Exception:
        pass
    tf.clear()
    for i, p in enumerate(paragraphs):
        if isinstance(p, tuple):
            text, opts = p
        else:
            text, opts = p, {}
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        if align is not None:
            para.alignment = align
        run = para.add_run()
        run.text = text
        run.font.size = Pt(opts.get("size", base_size))
        run.font.bold = opts.get("bold", bold_first and i == 0)
        run.font.italic = opts.get("italic", False)
        c = opts.get("color", color)
        run.font.color.rgb = c

INCH = 914400

BLUE      = RGBColor(0x00, 0x5B, 0x96)
YELLOW    = RGBColor(0xF5, 0xB5, 0x1B)
CYAN      = RGBColor(0x40, 0xB7, 0xD8)
DARK      = RGBColor(0x10, 0x2A, 0x43)
SLATE     = RGBColor(0x52, 0x61, 0x6B)
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
LIGHTBG   = RGBColor(0xDD, 0xED, 0xF7)

# ---- header ---------------------------------------------------------------
# Shrink the dark-blue header band so it does not eat poster real estate.
# The template ships with a ~10% slide-height header; we cut it roughly in half.

NEW_HEADER_BOTTOM = Emu(5_500_000)  # ~6 cm down from top
for s in slide.shapes:
    # The header band sits at top=0 and is very wide. Anything resembling
    # that decorative block, plus the logos / title / authors inside it,
    # gets compressed by remapping its bottom edge to NEW_HEADER_BOTTOM.
    if s.top is None:
        continue
    if s.top < Emu(500_000) and s.height > Emu(3_000_000):
        # Decorative full-width header rectangle.
        s.height = NEW_HEADER_BOTTOM

title = find_by_text(slide, "POSTER TITLE GOES HERE")
# Widen title shape so the long title fits on two lines comfortably.
title.top    = Emu(int(0.8 * INCH))
title.left   = Emu(int(5.8 * INCH))
title.width  = Emu(int(19.4 * INCH))
title.height = Emu(int(2.6 * INCH))
set_text(title,
         [("GrIDDD: Graph Diffusion",
           {"size": 70, "bold": True, "color": WHITE}),
          ("that can Insert and Delete",
           {"size": 70, "bold": True, "color": WHITE})],
         align=PP_ALIGN.CENTER)

authors = find_by_text(slide, "Author Name 1")
authors.top    = Emu(int(4.0 * INCH))
authors.left   = Emu(int(5.8 * INCH))
authors.width  = Emu(int(19.4 * INCH))
authors.height = Emu(int(0.8 * INCH))
set_text(authors,
         [("Author Name 1 · Author Name 2 · Author Name 3 · Author Name 4",
           {"size": 40, "color": LIGHTBG})],
         align=PP_ALIGN.CENTER)

# subtitle (course) already correct in template — leave as is.

# ---- Section 1 — Introduction --------------------------------------------

intro_header = find_by_text(slide, "Motivation, context, problem statement")
set_text(intro_header,
         [("Why fixed-size graph diffusion is a bug for property-driven molecular design.",
           {"size": 28, "bold": True, "color": DARK})])

intro_body = find_by_text(slide, "What is the problem and why is it important?")
set_text(intro_body, [
    ("Task.", {"size": 26, "bold": True, "color": DARK}),
    ("Generative graph DDPMs for de-novo molecular design — two settings: property targeting (generate molecules with prescribed properties) and property optimization (edit a molecule to improve a target property).",
     {"size": 24, "color": SLATE}),
    ("The fixed-size limitation.", {"size": 26, "bold": True, "color": DARK}),
    ("All existing graph DDPMs (DiGress, FreeGress, MiDi) keep the atom count fixed throughout diffusion. This breaks down when the target property correlates with molecular size (MW, QED). Pre-sampling the size from a classifier does not help in optimization, where the size is part of what must change.",
     {"size": 24, "color": SLATE}),
    ("Contribution.", {"size": 26, "bold": True, "color": DARK}),
    ("GrIDDD is the first discrete graph DDPM that monotonically inserts and deletes nodes during both forward and reverse processes — size-adaptive molecular generation. Matches or beats SOTA on targeting; substantially outperforms specialized optimizers.",
     {"size": 24, "color": SLATE}),
])

intro_fig = find_by_text(slide, "Main figure / diagram / table placeholder")
# we'll customize each "Main figure" placeholder by location
# Strategy: find all four and patch with section-specific captions
fig_placeholders = [s for s in slide.shapes
                    if s.has_text_frame
                    and "Main figure / diagram / table placeholder" in s.text_frame.text]
# Order them by (top, left)
fig_placeholders.sort(key=lambda s: (s.top, s.left))
# expected order: intro (top-left), approach (top-right), exp (bottom-left), critique (bottom-right)
fig_intro, fig_approach, fig_exp, fig_critique = fig_placeholders

set_text(fig_intro, [
    ("Fig. 1 — qualitative behavior of GrIDDD on QM9.",
     {"size": 32, "italic": True, "bold": True, "color": BLUE}),
    ("Top: 2-atom latent → +6 atoms inserted. Bottom: 18-atom latent → −9 deleted. Graph size adapts dynamically during denoising.",
     {"size": 19, "color": SLATE}),
], align=PP_ALIGN.CENTER)

# ---- Section 2 — Approach -------------------------------------------------

app_header = find_by_text(slide, "Model, data pipeline, architecture")
set_text(app_header,
         [("Discrete diffusion on graphs, generalized to monotonic node insertions and deletions.",
           {"size": 28, "bold": True, "color": DARK})])

app_body = find_by_text(slide, "Describe the proposed method.")
set_text(app_body, [
    ("Setup.", {"size": 26, "bold": True, "color": DARK}),
    ("Molecule = graph G = (X, E): one-hot atoms X, one-hot bonds E (no-bond as a category). Discrete DDPM under classifier-free guidance on a property y.",
     {"size": 24, "color": SLATE}),
    ("Three forward regimes (Δ^T = n^T − n^0).",
     {"size": 26, "bold": True, "color": DARK}),
    ("• Δ^T = 0 → standard DiGress / FreeGress.", {"size": 24, "color": SLATE}),
    ("• Δ^T < 0 → absorbing DEL + transient DEL* (DEL* can revert to a real type in reverse → enables reinsertion).",
     {"size": 24, "color": SLATE}),
    ("• Δ^T > 0 → nodes appear at sampled timesteps with type drawn from the empirical marginal m_X.",
     {"size": 24, "color": SLATE}),
    ("Insert/delete times follow a logistic ζ'(t) with center D, steepness w.",
     {"size": 24, "color": SLATE}),
    ("Reverse — two networks + loss.", {"size": 26, "bold": True, "color": DARK}),
    ("Main net predicts (X^0, E^0) + activation time ŝ per node. Aux g_φ predicts how many DEL* to inject at step t.",
     {"size": 24, "color": SLATE}),
    ("L = λ_X·CE_X + λ_E·CE_E + λ_S·CE_S + λ_DEL·CE_DEL (eq. 10). Conditional dropout with prob. ρ.",
     {"size": 24, "color": SLATE}),
])

set_text(fig_approach, [
    ("Fig. 2 — augmented transition matrices A*, B*, C*, D*.",
     {"size": 32, "italic": True, "bold": True, "color": YELLOW}),
    ("Three forward regimes (Δ^T = 0, < 0, > 0). Auxiliary DEL* state allows reinsertion during reverse; g_φ predicts how many DEL* to inject at each step.",
     {"size": 19, "color": SLATE}),
], align=PP_ALIGN.CENTER)

# ---- Section 3 — Experiments ---------------------------------------------

exp_header = find_by_text(slide, "Datasets, setup, baselines, metrics, and key results.")
set_text(exp_header,
         [("Property targeting, property optimization, and out-of-distribution sampling.",
           {"size": 28, "bold": True, "color": DARK})])

exp_body = find_by_text(slide, "List datasets and evaluation protocol.")
set_text(exp_body, [
    ("Setup.", {"size": 26, "bold": True, "color": DARK}),
    ("QM9 + ZINC-250k. T = 500 steps. Guidance λ = 3 (QM9) / 2 (ZINC).",
     {"size": 24, "color": SLATE}),
    ("Property targeting (MAE ↓).", {"size": 26, "bold": True, "color": DARK}),
    ("• QM9 μ: 0.66 — best (FreeGress 0.74, DiGress 0.80).", {"size": 24, "color": SLATE}),
    ("• ZINC MW: 4.89 vs 8.96 — nearly halved (size matters).", {"size": 24, "color": SLATE}),
    ("Property optimization (Jin et al.).", {"size": 26, "bold": True, "color": DARK}),
    ("• QED success: 45.1% vs 9.4% GCPN (≈ 5×).", {"size": 24, "color": SLATE}),
    ("• LogP improvement: 2.70 vs 2.49 GCPN.", {"size": 24, "color": SLATE}),
    ("OOD + ablation.", {"size": 26, "bold": True, "color": DARK}),
    ("At size 15 (training cap 14): GrIDDD 35% valid, DiGress ≈ 0%. Disabling insert/delete drops QED 45.1 → 33.8 — confirms size adaptation is the source of the gain.",
     {"size": 24, "color": SLATE}),
])

set_text(fig_exp, [
    ("Tables 1–3 + Fig. 3 — consolidated results.",
     {"size": 32, "italic": True, "bold": True, "color": CYAN}),
    ("Property targeting (QM9 + ZINC) · property optimization on ZINC · OOD validity at 15 atoms.",
     {"size": 19, "color": SLATE}),
], align=PP_ALIGN.CENTER)

# ---- Section 4 — Personal considerations ---------------------------------

crit_header = find_by_text(slide, "Reflection, limitations, ethics, and lessons learned.")
set_text(crit_header,
         [("What we take from this work and how it relates to the course.",
           {"size": 28, "bold": True, "color": DARK})])

crit_body = find_by_text(slide, "Discuss assumptions and limitations.")
set_text(crit_body, [
    ("Strengths.", {"size": 26, "bold": True, "color": DARK}),
    ("Minimal extension (DEL + transient DEL*) unlocks variable graph size. Gains are largest where size matters (MW, QED); marginal elsewhere.",
     {"size": 24, "color": SLATE}),
    ("Weaknesses.", {"size": 26, "bold": True, "color": DARK}),
    ("Two networks can conflict on the same step. More disconnected molecules than FreeGress / DiGress. ~30% training overhead.",
     {"size": 24, "color": SLATE}),
    ("Course connection.", {"size": 26, "bold": True, "color": DARK}),
    ("Discrete DDPMs (GDL27) × graph message passing (GDL19–22). Denoiser is a graph transformer. Pushes diffusion past its fixed-dimension assumption.",
     {"size": 24, "color": SLATE}),
    ("Open questions.", {"size": 26, "bold": True, "color": DARK}),
    ("• Can g_φ be folded into the main net?", {"size": 24, "color": SLATE}),
    ("• Generalize beyond molecules (e.g. floor plans)?", {"size": 24, "color": SLATE}),
])

set_text(fig_critique, [
    ("Where size-adaptation pays off (MAE reduction vs FreeGress).",
     {"size": 32, "italic": True, "bold": True, "color": BLUE}),
    ("MW: −45% MAE · μ: −11% · QED ≈ flat · HOMO/LogP slightly worse. Gains track size-dependence of the property — confirming the design hypothesis.",
     {"size": 19, "color": SLATE}),
], align=PP_ALIGN.CENTER)

# ---- footer reference -----------------------------------------------------

ref = find_by_text(slide, "Insert the full reference to the original article here")
set_text(ref, [
    ("Ninniri M., Podda M., Bacciu D. — Graph Diffusion that can Insert and Delete — NeurIPS 2025 — arXiv:2506.15725 — code: https://github.com/mninniri/GrIDDD",
     {"size": 19, "color": LIGHTBG})
], align=PP_ALIGN.CENTER)

# ---- enlarge body-text frames and push figure rects down -----------------
# Template ships with body=3.2" + figure=9.9-10.4". At 24pt our condensed
# bodies need ~6". We resize the body shapes, shrink+shift the figure
# decorative rectangles, and embed images into the new figure area.

# (body_shape_text_match, figure_bg_shape_top_match_emu, new_body_h_in,
#  new_fig_top_in, new_fig_h_in)
LAYOUT = [
    # top row     body_h, fig_top, fig_h   (body starts at 10.9 / 28.55)
    ("What is the problem and why is it important?", 13167360, 7.2, 18.2, 6.0),
    ("Describe the proposed method.",                13167360, 7.2, 18.2, 6.0),
    # bottom row
    ("List datasets and evaluation protocol.",       29306520, 7.2, 35.9, 6.4),
    ("Discuss assumptions and limitations.",         29306520, 7.2, 35.9, 6.4),
]

# Resize body text frames.
for body_match, _, new_body_h, _, _ in LAYOUT:
    sh = find_by_text(slide, body_match)
    if sh is not None:
        sh.height = Emu(int(new_body_h * INCH))

# Resize + move figure decorative rectangles (the empty colored ones).
# Identify them as autoshapes whose top matches and whose text is empty.
top_targets = {13167360, 29306520}
for s in slide.shapes:
    if not s.has_text_frame:
        continue
    if s.text_frame.text.strip():
        continue
    if s.top in top_targets and s.width > Emu(10_000_000):
        # Figure bg rectangle.
        if s.top == Emu(13167360):
            s.top = Emu(int(18.2 * INCH))
            s.height = Emu(int(6.0 * INCH))
        else:
            s.top = Emu(int(35.9 * INCH))
            s.height = Emu(int(6.4 * INCH))

RECTS = {
    "intro":    (1463040,  int(18.2*INCH), 12829032, int(6.0*INCH)),
    "approach": (15983712, int(18.2*INCH), 12829032, int(6.0*INCH)),
    "exp":      (1463040,  int(35.9*INCH), 12829032, int(6.4*INCH)),
    "critique": (15983712, int(35.9*INCH), 12829032, int(6.4*INCH)),
}

FIG_MAP = [
    ("intro",    fig_intro,    "figs/fig1_qualitative.png"),
    ("approach", fig_approach, "figs/fig2_matrices.png"),
    ("exp",      fig_exp,      "figs/box3_composite.png"),
    ("critique", fig_critique, "figs/box4_mae_reduction.png"),
]

CAPTION_H = Emu(700_000)     # ~0.75" caption strip at top of fig rect
PADDING   = Emu(100_000)     # tiny inner margin

for key, shape, img_path in FIG_MAP:
    rl, rt, rw, rh = RECTS[key]
    # Move caption to top of the rectangle, force its size.
    shape.left   = Emu(rl)
    shape.top    = Emu(rt)
    shape.width  = Emu(rw)
    shape.height = CAPTION_H

    p = Path(img_path)
    if not p.exists():
        print(f"  WARN: missing {img_path}")
        continue
    im = Image.open(p)
    iw, ih = im.size
    area_left   = rl + PADDING
    area_top    = rt + CAPTION_H + PADDING
    area_width  = rw - 2 * PADDING
    area_height = rh - CAPTION_H - 2 * PADDING
    ar_img  = iw / ih
    ar_area = area_width / area_height
    if ar_img > ar_area:
        w = area_width
        h = int(w / ar_img)
    else:
        h = area_height
        w = int(h * ar_img)
    left = area_left + (area_width - w) // 2
    top  = area_top + (area_height - h) // 2
    slide.shapes.add_picture(str(p), Emu(left), Emu(top),
                             width=Emu(w), height=Emu(h))
    print(f"  embedded {img_path}  -> ({w/914400:.1f}\" x {h/914400:.1f}\")")

prs.save(DST)
print(f"Saved {DST}")

# ---- export to PDF -------------------------------------------------------
pdf_target = Path(DST).with_suffix(".pdf").resolve()
src_abs = Path(DST).resolve()

def try_soffice():
    for soffice in ("soffice", "/Applications/LibreOffice.app/Contents/MacOS/soffice"):
        try:
            r = subprocess.run(
                [soffice, "--headless", "--convert-to", "pdf", DST],
                capture_output=True, text=True, timeout=240,
            )
            if r.returncode == 0 and pdf_target.exists():
                return True
        except FileNotFoundError:
            continue
    return False

def try_keynote():
    script = f'''
    set src to POSIX file "{src_abs}"
    set dst to POSIX file "{pdf_target}"
    tell application "Keynote"
        activate
        set theDoc to open src
        delay 2
        export theDoc to dst as PDF
        close theDoc saving no
    end tell
    '''
    try:
        r = subprocess.run(["osascript", "-e", script],
                           capture_output=True, text=True, timeout=300)
        return r.returncode == 0 and pdf_target.exists()
    except FileNotFoundError:
        return False

if try_soffice():
    print(f"Saved {pdf_target.name} (via LibreOffice)")
elif try_keynote():
    print(f"Saved {pdf_target.name} (via Keynote)")
else:
    print("WARN: could not produce PDF. Install LibreOffice "
          "(`brew install --cask libreoffice`) or open the .pptx in "
          "Keynote / PowerPoint and export manually.")
