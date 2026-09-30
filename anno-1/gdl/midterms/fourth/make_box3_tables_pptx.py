"""Build native PowerPoint tables for box 3 (Experiments) of the GrIDDD poster.

Produces GrIDDD_box3_tables.pptx with two editable tables on one slide:
  - property targeting (MAE)
  - property optimization (improvement / success %)

Workflow: open this file in desktop PowerPoint (the SharePoint file syncs),
click a table border to select the whole table object, Ctrl/Cmd-C, then paste
into the Group5 deck. The table stays native and editable, picks up the deck's
theme fonts, and is NOT a screenshot (satisfies the poster "redraw" rule).

Run:
    ~/.pyenv/versions/3.12.6/bin/python3 make_box3_tables_pptx.py
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

CYAN = RGBColor(0x0E, 0x74, 0x90)
LIGHT_CYAN = RGBColor(0xCF, 0xFA, 0xFE)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK = RGBColor(0x0F, 0x17, 0x2A)
SLATE = RGBColor(0x33, 0x41, 0x5B)


def style_table(table, header_labels, rows, highlight_idx, bold_cells,
                header_pt=18, body_pt=18):
    """Fill a python-pptx table and style it (header band, GrIDDD highlight)."""
    # header
    for c, label in enumerate(header_labels):
        cell = table.cell(0, c)
        cell.fill.solid()
        cell.fill.fore_color.rgb = CYAN
        _set_cell(cell, label, WHITE, header_pt, bold=True,
                  align=PP_ALIGN.LEFT if c == 0 else PP_ALIGN.CENTER)
    # body
    for r, row in enumerate(rows, start=1):
        is_hi = (r - 1) == highlight_idx
        for c, val in enumerate(row):
            cell = table.cell(r, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = LIGHT_CYAN if is_hi else WHITE
            bold = (r, c) in bold_cells
            color = CYAN if bold else (DARK if is_hi else SLATE)
            _set_cell(cell, val, color, body_pt, bold=bold,
                      align=PP_ALIGN.LEFT if c == 0 else PP_ALIGN.CENTER)


def _set_cell(cell, text, color, size, bold=False, align=PP_ALIGN.CENTER):
    cell.margin_top = Emu(20000)
    cell.margin_bottom = Emu(20000)
    tf = cell.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    f = run.font
    f.size = Pt(size)
    f.bold = bold
    f.color.rgb = color
    f.name = "Calibri"


prs = Presentation()
prs.slide_width = Inches(13.33)
prs.slide_height = Inches(7.5)
slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank


def add_title(text, top):
    tb = slide.shapes.add_textbox(Inches(0.5), Inches(top), Inches(12.3),
                                  Inches(0.5))
    p = tb.text_frame.paragraphs[0]
    run = p.add_run()
    run.text = text
    run.font.size = Pt(20)
    run.font.bold = True
    run.font.color.rgb = DARK
    run.font.name = "Calibri"


# ---- Table 1: property targeting (MAE down) -----------------------------
add_title("Property targeting — MAE ↓  (validity % goes in the caption)", 0.3)
t1_head = ["Method", "μ (QM9)", "HOMO", "LogP", "QED", "MW"]
t1_rows = [
    ["DiGress",   "0.80", "0.61", "0.74", "0.15", "20.92"],
    ["FreeGress", "0.74", "0.32", "0.17", "0.04", "8.96"],
    ["GrIDDD",    "0.66", "0.37", "0.19", "0.04", "4.89"],
]
gt1 = slide.shapes.add_table(len(t1_rows) + 1, len(t1_head),
                             Inches(0.5), Inches(0.85),
                             Inches(12.3), Inches(2.0)).table
# column widths
for col, w in zip(gt1.columns, [3.0, 2.0, 1.9, 1.9, 1.8, 1.7]):
    col.width = Inches(w)
style_table(gt1, t1_head, t1_rows, highlight_idx=2,
            bold_cells={(3, 1), (3, 5)})

# ---- Table 2: property optimization (higher better) ---------------------
add_title("Property optimization — improvement ↑ / success % ↑", 3.5)
t2_head = ["Method", "LogP δ0.4", "LogP δ0.6", "QED succ.", "DRD2 succ."]
t2_rows = [
    ["JT-VAE", "1.03", "0.28", "8.8%", "3.4%"],
    ["CG-VAE", "0.61", "0.25", "4.8%", "4.4%"],
    ["GCPN",   "2.49", "0.79", "9.4%", "—"],
    ["GrIDDD", "2.70", "1.33", "45.1%", "5.0%"],
]
gt2 = slide.shapes.add_table(len(t2_rows) + 1, len(t2_head),
                             Inches(0.5), Inches(4.05),
                             Inches(12.3), Inches(2.5)).table
for col, w in zip(gt2.columns, [2.9, 2.4, 2.4, 2.3, 2.3]):
    col.width = Inches(w)
style_table(gt2, t2_head, t2_rows, highlight_idx=3,
            bold_cells={(4, 1), (4, 2), (4, 3), (4, 4)})

prs.save("GrIDDD_box3_tables.pptx")
print("wrote GrIDDD_box3_tables.pptx")
