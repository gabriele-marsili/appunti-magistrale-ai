# L22 Self-supervised learning and vision foundation models – note di lavoro (6/11/2026)

Materiale: slide /mnt/user-data/uploads/CV/Lessons/L22.pdf (59 pagine, Giacomo Cignoni, dottorando, 5/11/2026). Footer "n / 59" con n = pagina del PDF, copertina compresa. Divisorie di parte senza numero: 2 (Part 1) e 41 (Part 2). Divisorie di sezione CON numero: 10 (Instance Discrimination Methods), 28 (Reconstruction Models). Quindi printed=P(n) su tutte tranne 2 e 41 (printed=''). Testo: /tmp/cv/pdf/L22.txt. Lezione precedente: L21 (contrastivo, SimCLR, SimSiam), collegata con link #L21.

## Mappa sezioni
l22-intro (1–9), l22-istanze (10–22: BYOL, MoCo), l22-ridondanza (23–27: Barlow Twins, VICReg), l22-mim (28–40: autoencoder, SimMIM, MAE, BEiT, confronto Park et al.), l22-foundation (41–59: DINO, DINOv2, Depth Anything, DINOv3, JEPA). extra.html: l22-libro, l22-guida (con tabella riassuntiva dei metodi e 13 domande).

## Capitoli usati
- visionbook cap. 30 (representation_learning.html): § 30.3 e Tab. 30.1 (compressione/predizione), § 30.4 e 30.4.1 (autoencoder, 1-NN per strato: colore nei pixel, forma in profondità; AE lineare = PCA), § 30.5.1 e 30.7 (rilevatori di oggetti emergenti, fig. 30.7 e 30.9), § 30.6 (V1(X) → V2(X)), § 30.8 (rotazione, posizione relativa), § 30.10 (alignment loss, collasso), § 30.10.1 (uniformity), § 30.10.2 (crop → colore, crop + jitter → forma), § 30.11 (general-purpose).
- cap. 37 (transfer_learning.html): § 37.2, 37.3 (finetuning, sostituire l'ultimo strato), 37.3.1 (moduli congelati, DINO come featurizer, fig. 37.3, basso rango), 37.3.2 (linear probe), 37.4, 37.4.1 (distillazione con pmf).
- cap. 31 (perceptual_organization.html) § 31.3.2: DINO denso + k-means, fig. 31.7.
- cap. 26 § 26.4.1 (tokenizzazione), § 26.8 (permutazioni), § 26.10 (cita il masked autoencoding).
- cap. 43 § 43.4 (profondità monoculare; refuso loss scale-invariant senza log già noto da L13/L17).
- cap. 33 § 33.4 (VAE) solo per il tokenizer di BEiT. cap. 12 § 12.7.4 (softmax e^{−τx}).
- Szeliski 2a ed. § 5.4.7 (BYOL e SimSiam senza negativi, memory bank → MoCo → MoCo v2, Tian et al. 2021, distillazione). Prince § 9.3.7 (generativo vs contrastivo).

## Imprecisioni del libro notate
- § 31.3.2 mette DINO fra i metodi contrastivi che allontanano patch di immagini diverse: DINO non ha negativi espliciti.
- (già note) § 30.4 radice spuria nella L2; § 12.7.4 softmax con e^{−τx}; eq. 30.3 1/N; refusi di § 30.10 per L21.

## Errori e imprecisioni delle slide (segnalati nelle schede)
1. Slide 37: ℒ_BEiT = E_M[Σ log p_MIM] senza segno meno: è una log-verosimiglianza (nell'articolo è un max); come loss serve −. (box w)
2. Slide 35: "Train the tokenizer and decoder with VAE": BEiT usa il dVAE pubblico di DALL-E (|V| = 8192), non lo addestra (verificato su arXiv 2106.08254). (box w)
3. Slide 54: "Why: keep." frase troncata (segnalato nel testo).
4. Slide 16: "How can change over time…" manca il soggetto (the teacher).
5. Slide 13: footer "SimCLR · MoCo · SimSiam" ma MoCo non è nella tabella.
Precisazioni (non errori): slide 24 normalizzazione lungo il batch per feature (verificato: z_norm = (z − mean(0))/std(0), C = z_aᵀ z_b / N); slide 27 VICReg usa √(Var + ε), ε = 1e-4, c(Z) con 1/(n−1) (verificato arXiv 2105.04906); slide 48 la "masked reconstruction" è iBOT (bersagli = uscite del teacher), più KoLeo e Sinkhorn-Knopp.
Controllati e giusti: EMA 2,01; ∂L/∂s = 2(s − t); BYOL normalizzata = 2 − 2cos; N = 196; MAE 75% e loss sulle mascherate; DINO centering/sharpening (tabella coerente con l'articolo); DINOv2 21M/86M/300M/1.1B; DINOv3 7B (6,7B effettivi) e LVD-1689M; SAT-493M.

## Numeri dagli articoli (verificati con WebFetch salvo dove indicato)
- Barlow Twins: λ = 5·10⁻³, projector 3 × 8192, batch 2048 (arXiv 2103.03230).
- VICReg: λ = μ = 25, ν = 1, γ = 1, ε = 1e-4, expander 3 × 8192, batch 2048.
- BEiT: 224, patch 16, 14 × 14 token, vocabolario 8192, ~40% a blocchi (max 75 patch), blocchi ≥ 16 patch, aspetto [0.3, 1/0.3]; obiettivo come max.
- DINO: τ_t 0.04 → 0.07 (30 epoche), τ_s 0.1, K = 65 536, momentum 0.996 → 1 coseno, centro m = 0.9 ok e 0.999 collassa, 2 globali 224 + locali 96 (6 nell'ablazione), ViT-S/16 77,0 linear / 74,5 k-NN, ViT-B/8 80,1 / 77,4.
- DINOv3: ViT-7B (~6,7B, 40 blocchi, patch 16), LVD-1689M, Gram dopo ~1M iterazioni (emergentmind). Intervallo di refresh del Gram teacher NON verificato, non scritto.
- Da conoscenza standard, non rifetchati: MoCo K = 65 536, m = 0.999, T = 0.07; BYOL τ 0.996 → 1, proiezione 256; MAE decoder 8 blocchi × 512, ≥3× più veloce; SimMIM patch di maschera 32, ~60%; Depth Anything 1,5M etichettate + ~62M non etichettate, DPT; I-JEPA 4 blocchi bersaglio 15–20%, contesto 85–100%; DINOv2 pool ~1,2 B immagini (non scritto il numero nelle schede).

## Conti fatti (python)
- EMA: ξ_k = 3 − 0.99^k: 2.01, 2.096 (k=10), 2.50 (k=69), 2.634 (k=100), 2.951 (k=300); dimezzamento 69 (τ=0.99), 173 (0.996), 693 (0.999).
- BYOL: p = (3,4), z = (1,0): 0.80 sia come distanza sia come 2 − 2cos.
- Stop-gradient, toy lineare: senza sg L = w²σ_n²; con sg ∂L/∂w = 2(w − ξ).
- Barlow Twins B = 4, d = 2: C = [[1,0],[0,0]], L = 1; collassi: L = d e L = λd(d−1).
- MAE ViT-L, D = 1024: 12ND² + 2N²D = 2.545e9 (N=196) contro 6.21e8 (N=49), rapporto 4.09.
- DINO: logit (5,1,0), (5,0,1): raw τ=1 (0.976, 0.018, 0.007); centrati τ=1 (0.307, 0.507, 0.186); centrati τ=0.04 ≈ (0,1,0), (0,0,1).
- Gram: esempio 3 patch, invarianza a rotazioni, loss 4 se la patch 3 diventa uguale alle altre.
- DINO multi-crop 2 + 6: 14 termini. DINOv2: 1.1e9/21e6 ≈ 52. DINOv3 vs v2: dati ×12, parametri ×6.

## Dubbi
- La descrizione delle figure di slide 11 (immagini dietro le viste) e 40 (posizione dei punti) è dalla miniatura a 50 dpi: dettagli fini non certi.
- Video non cercati per le schede (li gestisce la dispensa).
