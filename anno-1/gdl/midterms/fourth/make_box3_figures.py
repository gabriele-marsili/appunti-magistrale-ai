"""Redraw the box-3 (Experiments) figures for the GrIDDD poster.

Outputs (high-res PNG, transparent-safe white cards) into figs/:
  - fig3_ood_redrawn.png    : OOD validity vs molecule size (Fig. 3)
  - table_targeting.png     : property-targeting MAE table (redrawn, not a screenshot)
  - table_optim.png         : property-optimization table (redrawn)

Run with the interpreter that has matplotlib:
    ~/.pyenv/versions/3.12.6/bin/python3 make_box3_figures.py

All numbers are taken from the paper (Tables 1-3, Fig. 3). The Fig. 3 series
were read off the published plot (the paper does not tabulate them) -- verify
against the original before printing.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

# ---- palette (consistent with the cyan box-3 theme) ---------------------
CYAN = "#0E7490"     # GrIDDD (highlighted)
SLATE = "#64748B"    # DiGress / baselines (muted)
DARK = "#0F172A"
LIGHT_CYAN = "#CFFAFE"
GRID = "#CBD5E1"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 22,
    "axes.edgecolor": "#334155",
    "axes.linewidth": 1.4,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.facecolor": "white",
})

# ---- Fig. 3 : OOD validity vs molecule size -----------------------------
sizes = [10, 11, 12, 13, 14, 15]
digress = [97, 85, 57, 30, 12, 6]     # read off Fig. 3
griddd = [90, 72, 54, 41, 38, 35]     # read off Fig. 3

fig, ax = plt.subplots(figsize=(11, 6.2))

# training-capacity marker for GrIDDD (forced to insert up to 14 nodes)
ax.axvspan(14, 15.4, color="#FEF3C7", alpha=0.55, zorder=0)
ax.axvline(14, color="#D97706", ls="--", lw=1.8, zorder=1)
ax.text(14, 108, "trained ≤14 atoms", color="#B45309",
        fontsize=16, va="bottom", ha="center")

ax.plot(sizes, digress, marker="o", ms=12, lw=3.5, color=SLATE,
        label="DiGress", zorder=3)
ax.plot(sizes, griddd, marker="s", ms=12, lw=3.5, color=CYAN,
        label="GrIDDD", zorder=4)

# annotate the headline number
ax.annotate("35% valid at 15 atoms\n(above training size)",
            xy=(15, 35), xytext=(12.7, 70),
            fontsize=18, color=CYAN, fontweight="bold", ha="left",
            arrowprops=dict(arrowstyle="->", color=CYAN, lw=2.2))
ax.annotate("DiGress collapses\n(~6%)", xy=(15, 6), xytext=(12.6, 14),
            fontsize=16, color=SLATE, ha="left",
            arrowprops=dict(arrowstyle="->", color=SLATE, lw=1.8))

ax.set_xlabel("Molecule size (atoms)", fontsize=24, color=DARK, labelpad=10)
ax.set_ylabel("Validity (%)", fontsize=24, color=DARK, labelpad=10)
ax.set_xlim(9.7, 15.4)
ax.set_ylim(0, 105)
ax.set_xticks(sizes)
ax.set_yticks([0, 25, 50, 75, 100])
ax.grid(True, ls="--", lw=1.0, color=GRID, alpha=0.7)
ax.set_axisbelow(True)
ax.tick_params(labelsize=20, colors=DARK)
ax.legend(fontsize=22, loc="upper right", frameon=True, framealpha=0.95,
          edgecolor="#334155")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

fig.savefig("figs/fig3_ood_redrawn.png")
plt.close(fig)
print("wrote figs/fig3_ood_redrawn.png")


# ---- table renderer (matplotlib, so it is redrawn, not a screenshot) ----
def render_table(path, title, col_labels, rows, highlight_row_idx,
                 bold_cells, col_widths, figw):
    """rows: list of [str,...]. highlight_row_idx: GrIDDD row.
    bold_cells: set of (r, c) to bold (the wins)."""
    nrows = len(rows) + 1
    fig, ax = plt.subplots(figsize=(figw, 0.52 * nrows + 0.8))
    ax.axis("off")
    ax.set_title(title, fontsize=24, fontweight="bold", color=DARK,
                 pad=10, loc="left")

    tbl = ax.table(cellText=rows, colLabels=col_labels,
                   colWidths=col_widths, cellLoc="center", loc="center",
                   bbox=[0, 0, 1, 0.86])
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(20)
    tbl.scale(1, 2.0)

    for (r, c), cell in tbl.get_cells().items() if hasattr(tbl, "get_cells") \
            else tbl.get_celld().items():
        cell.set_edgecolor("#E2E8F0")
        cell.set_linewidth(1.0)
        if r == 0:                                  # header
            cell.set_facecolor(CYAN)
            cell.get_text().set_color("white")
            cell.get_text().set_fontweight("bold")
            cell.set_height(cell.get_height() * 1.05)
        elif r == highlight_row_idx + 1:            # GrIDDD row
            cell.set_facecolor(LIGHT_CYAN)
            cell.get_text().set_color(DARK)
        else:
            cell.set_facecolor("white")
            cell.get_text().set_color("#334155")
        if c == 0 and r > 0:                        # method names left-aligned
            cell.get_text().set_ha("left")
            cell.PAD = 0.04
        if (r, c) in bold_cells:
            cell.get_text().set_fontweight("bold")
            cell.get_text().set_color(CYAN)

    fig.savefig(path)
    plt.close(fig)
    print("wrote", path)


# Property targeting -- MAE (lower is better). Values from Tables 1-2.
render_table(
    "figs/table_targeting.png",
    "Property targeting — MAE ↓  (validity % in caption)",
    ["Method", "μ (QM9)", "HOMO", "LogP", "QED", "MW"],
    [
        ["DiGress",   "0.80", "0.61", "0.74", "0.15", "20.92"],
        ["FreeGress", "0.74", "0.32", "0.17", "0.04", "8.96"],
        ["GrIDDD",    "0.66", "0.37", "0.19", "0.04", "4.89"],
    ],
    highlight_row_idx=2,
    bold_cells={(3, 1), (3, 5)},   # GrIDDD wins on mu and MW
    col_widths=[0.26, 0.16, 0.15, 0.14, 0.14, 0.15],
    figw=12.5,
)

# Property optimization -- improvement / success rate (higher is better).
render_table(
    "figs/table_optim.png",
    "Property optimization — improvement ↑ / success % ↑",
    ["Method", "LogP δ0.4", "LogP δ0.6", "QED succ.", "DRD2 succ."],
    [
        ["JT-VAE", "1.03", "0.28", "8.8%", "3.4%"],
        ["CG-VAE", "0.61", "0.25", "4.8%", "4.4%"],
        ["GCPN",   "2.49", "0.79", "9.4%", "—"],
        ["GrIDDD", "2.70", "1.33", "45.1%", "5.0%"],
    ],
    highlight_row_idx=3,
    bold_cells={(4, 1), (4, 2), (4, 3), (4, 4)},   # GrIDDD wins all
    col_widths=[0.24, 0.19, 0.19, 0.19, 0.19],
    figw=12.5,
)
