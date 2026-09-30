# Midterm 4 — Work Guide

**Paper**: *Graph Diffusion that can Insert and Delete* (GrIDDD)
Ninniri M., Podda M., Bacciu D. — NeurIPS 2025 · arXiv:2506.15725
Code: <https://github.com/mninniri/GrIDDD>

**Deadline**: Wednesday May 27, 2026, 18:00 (PDF upload on Moodle).
**Poster session**: May 28, 2026, 11:00–14:00, Room C1.
**Format**: A0 in color, template provided (`gdl_midterm4_poster_template.pptx`).
**Type**: 4/5 person group — pass/fail individual grade, based on in-person discussion.

> **Note**: the authors are from our own department (Bacciu is also the course instructor). Expect pointed questions: each member must be able to answer on *every* section, not only their own.

---

## 1. What you must know about the paper in 60 seconds

**Problem**: existing graph DDPMs (DiGress, FreeGress, MiDi) generate molecules with a **fixed number of atoms** throughout the entire diffusion. This is critical when the target property correlates with size (e.g. molecular weight MW, QED).

**Solution**: GrIDDD generalizes discrete graph diffusion to support **monotonic node insertions and deletions** in both the forward and reverse processes. Three forward regimes, parameterized by $\Delta^T = n^T - n^0$:

1. $\Delta^T = 0$ → standard discrete diffusion (Vignac/FreeGress baseline).
2. $\Delta^T < 0$ (deletions) → absorbing state `DEL` + auxiliary transient state `DEL*` that enables reinsertion during the reverse process.
3. $\Delta^T > 0$ (insertions) → nodes are "activated" only after a sampled insertion timestep; their initial type is drawn from the marginal $m_X$.

Insert/delete timesteps are sampled from a logistic-shaped density $\zeta'(t)$ with hyperparameters $D$ (center) and $w$ (steepness).

**Reverse architecture**:
- **Main network**: predicts $(X^0, E^0)$ and the activation times $\hat{S}$ of each node.
- **Auxiliary network $g_\phi$**: predicts how many `DEL*` to add at each step.

**Loss** (eq. 10): weighted CE over nodes, edges, activation times, and `DEL*` count. Classifier-free guidance with *conditional dropout* on $y$.

**Key results**:
- *Property targeting QM9* (μ): MAE **0.66** vs 0.74 FreeGress (state of the art).
- *MW on ZINC-250k*: MAE **4.89** vs 8.96 FreeGress — nearly halved.
- *Property optimization*: LogP improvement **2.70** vs 2.49 GCPN; **QED success 45.1%** vs 9.4% GCPN (≈ 5×).
- *Out-of-distribution*: 35% validity at 15 atoms even though training was capped at ≤14 atoms (DiGress drops to ~0%).
- *Cost*: ~30% training overhead vs FreeGress; sampling often faster thanks to a variable number of denoising steps.

**Limitations** (acknowledged by the authors):
- The two networks may conflict (insert + delete on the same step → "illegal" by design).
- Tendency to produce more disconnected molecules than FreeGress/DiGress (nodes inserted late do not connect in time).

---

## 2. Work split (4 people)

Each poster section is an independent task, but **cross-reviews are mandatory**.

| Member | Owner of | Poster section | Estimated load |
|--------|----------|----------------|----------------|
| **A** — Theory lead | Section 1 (Introduction) + mathematical framing | Top-left blue box | 25% |
| **B** — Method lead | Section 2 (Approach): forward/reverse, DEL/DEL*, $\zeta'$ schedule, loss | Top-right yellow box | 30% |
| **C** — Experiments lead | Section 3 (Experiments): tables 1–3, OOD figure, baselines | Bottom-left cyan box | 25% |
| **D** — Critic + design | Section 4 (Personal considerations), references, final layout, A0 print | Bottom-right blue box + footer | 20% |

### Task A — Introduction (box 1, blue)
- Read §1–2 of the paper + §2.3 of [Ninniri 2024 — FreeGress] and [Vignac 2023a — DiGress] to fully understand "fixed-size graph diffusion".
- Relevant GDL lectures: **GDL27 (Diffusion)**, **GDL19–22 (GNN / message passing)**.
- Write ≤ 120 words on: (i) what property-driven molecular design is, (ii) why the fixed-size constraint is a bug, (iii) the contribution one-liner.
- Use **Fig. 1 of the paper** (qualitative: 6 insertions on QM9, 9 deletions from 18→9 atoms) as the main figure of box 1.

### Task B — Approach (box 2, yellow)
- Read §3 and Appendix B (denoiser architecture, conditional dropout).
- Relevant GDL lectures: **GDL27 (Diffusion DDPM)**, **GDL26 (Generative AE / Flows)** for the continuum, **GDL20 (Message Passing)** for the backbone.
- Draw a simplified **scheme** of the forward process in 3 regimes (Δ=0 / Δ<0 / Δ>0) + matrices $A^*, B^*, C^*, D^*$ from Fig. 2. Inkscape / draw.io is fine.
- Include only **eq. 6** ($Q^{*t}$ transition) and **eq. 10** (loss) — do not pile equations.
- Two lines on the role of `DEL*` (it prevents the absorbing `DEL` state from trapping nodes that need to be reinserted in the reverse process).

### Task C — Experiments (box 3, cyan)
- Read §4–5 + appendices B.1 (splits), B.3 (baselines), D.3 (samples).
- Consolidated table (recommended: one compact table): MAE on μ/HOMO/MW + Success% on QED/LogP/DRD2. Redrawn — no blurry screenshots.
- **OOD validity vs molecule size** plot (Fig. 3) → most striking figure, make it large and readable.
- One line on setup: T=500, λ_X=1, λ_E=2, w=0.05, D=T/2=250, guidance scale λ∈{2,3}, A100 80GB GPU.

### Task D — Personal considerations + integration (box 4, blue)
- Read §6 + appendices C (compute), D.2 (sensitivity), D.4 (failure cases QM9).
- Write the critique:
  - **strengths**: elegant generalization (absorbing + transient state), gains where size matters (MW, QED).
  - **weaknesses**: ~30% training overhead, more disconnected molecules, simultaneous insert+delete conflicts.
  - **our take**: gains are largest where the design predicts (size-correlated properties) and marginal elsewhere (μ, LogP) — the evaluation *confirms exactly the design intuition*.
  - **course connection**: the discrete DDPM seen in class (GDL27) is generalized beyond the fixed-sample-size constraint — compare with the continuous→discrete analogy.
  - **ethics**: dual-use risk in *de novo* drug design.
- Finalize layout, font, references, footer, PDF export, **A0 color print** (use a print shop, at least 2 days lead time).
- Upload the PDF on Moodle by Wed May 27, 18:00.

### Cross-reviews (mandatory, Tue May 26)
- A↔B (theory ↔ method): consistent notation ($G^t, X^t, E^t, \Delta^T$).
- B↔C (method ↔ exp): hyperparameters cited in box 2 match those used in experiments.
- C↔D (exp ↔ critique): every critical claim in box 4 is backed by a number in box 3.
- A↔D: introduction and conclusion "tell the same story".

---

## 3. Timeline

Starting point: **Fri May 22, 15:40** — all four members have read the paper once. Split call at **16:00**. Five working days to the Moodle deadline (Wed May 27, 18:00), so the plan is tight and front-loads the print buffer.

| Day | Task |
|-----|------|
| **Fri May 22, 16:00** | Split call: confirm the A/B/C/D ownership above, agree on shared notation ($G^t, X^t, E^t, \Delta^T$), pick the figure tool (Inkscape / draw.io). Each member presents their section in 5 min so everyone starts aligned. |
| **Fri May 22, evening** | A, B, C, D each produce **draft v0** of their section text (Markdown / Google Doc). Keep it rough — content over wording. |
| **Sat May 23** | Figures day: B draws the forward scheme (3 regimes + matrices $A^*, B^*, C^*, D^*$); C redraws the consolidated results table and Fig. 3 (OOD). A picks Fig. 1; D sets up the pptx skeleton. |
| **Sun May 24** | Merge v0 + figures into the pptx. First full internal review: does each box tell its part of one story? Fix structural gaps. |
| **Mon May 25** | Text revision: run ALL text through `/humanizer`, cut to ~250–350 words total for an A0 poster. Mandatory cross-reviews (A↔B, B↔C, C↔D, A↔D) — see §2. |
| **Tue May 26** | D finalizes layout, references, footer; export PDF and **send to the print shop** (≥ 1 day lead time). Rehearse the discussion: each member speaks 2 min on *each* section, not only their own. |
| **Wed May 27, 18:00** | PDF upload on Moodle (do it in the morning, not at the deadline). |
| **Thu May 28, 11–14** | Poster session in Room C1; pick up the A0 print beforehand. |

> **Risk note**: the print shop is the only hard external dependency. If Tuesday slips, the A0 may not be ready for May 28 — keep Sat/Sun on schedule so Tuesday stays free for print + rehearsal.

---

## 4. Constraints and golden rules

- **No wall of equations**: max 2 equations in the whole poster (eq. 6 and eq. 10 are the natural picks).
- **No screenshots**: redraw tables and figures (half a day of work, but it makes a huge difference).
- **Brevity**: an A0 poster is read from 1.5 m away. Body font ≥ 28 pt, headers ≥ 44 pt. Short sentences.
- **Cite the paper** in the footer with full DOI/arXiv reference: *Ninniri M., Podda M., Bacciu D. "Graph Diffusion that can Insert and Delete". NeurIPS 2025. arXiv:2506.15725.*
- **Humanizer**: run all text through `/humanizer` to scrub AI-generated patterns (em-dash overuse, "delve into", "robust framework", …).
- **Discussion**: every member must be able to answer:
  - *Why DEL\* and not just DEL?* (DEL is absorbing in forward, but in reverse the node must be able to "come back to life").
  - *How does GrIDDD pick the final size?* (during training, $n^T$ is sampled from $h_{n^0}(n)$; at inference, set a priori or read from the conditioning $y$).
  - *Why does QED break when insertions are disabled?* (QED correlates with MW → without size adaptation, the model cannot reshape the graph).
  - *What is classifier-free guidance and why here?* (eq. 11: shift toward $y$ via the difference between conditional and unconditional posteriors; $\lambda$ controls the accuracy/diversity trade-off).

---

## 5. Pre-submit sanity check

- [ ] All 4 names present as authors
- [ ] Title matches the paper
- [ ] Every box has **at least one** figure or table
- [ ] Complete reference in the footer
- [ ] Body font ≥ 28 pt
- [ ] PDF exported at 300 DPI; A0 size (841 × 1189 mm) or a proportional multiple (the template is ~84 × 119 cm in DrawingML EMU — verify and scale)
- [ ] Physical A4 test print for relative readability
- [ ] Moodle upload BEFORE 18:00 on May 27
- [ ] A0 print picked up in time for May 28, 11:00
