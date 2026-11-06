# L21 Self-Supervised Contrastive Learning – note di lavoro (6/11/2026)

Materiale: slide /mnt/user-data/uploads/CV/Lessons/L21.pdf (51 pagine, Antonio Carta, 4/11/2026). Footer "x / 50" con x = pagina PDF − 1 su tutte le pagine numerate (verificato pagina per pagina con pdftotext); copertina e divisorie senza numero. Divisorie: 6 Finetuning, 12 (Early Historical) Examples of Pretext Tasks, 20 Self-Supervised Contrastive Learning, 27 Augmentations and Invariance in SSL, 31 InfoNCE Loss, 36 SimCLR, 42 SimSiam, 45 Conclusions. Nessun `printed=` necessario (PRINTED_TOTAL = 50).

## Mappa sezioni
l21-intro (1–5), l21-finetuning (6–11), l21-pretext (12–19), l21-contrastivo (20–26), l21-aug (27–30), l21-infonce (31–35), l21-simclr (36–41), l21-simsiam (42–44), l21-concl (45–51). Extra: l21-libro, l21-guida.

## Capitoli usati
- visionbook cap. 30 (representation_learning.html): 30.2–30.3 (compressione, predizione, Tab. 30.1), 30.4.1 (1-NN per strato: colore nei pixel, forma in profondità), 30.5 e 30.5.1 (detector emergenti), 30.6 (V1(X), V2(X)), 30.7 (imputation, colorizzazione, fig. 30.9), 30.8 (rotazione, posizione relativa), 30.10 (alignment loss, collasso, positivi/negativi, trasformazioni e co-occorrenza, eq. 30.4), 30.10.1 (L_align, L_unif con α, t, λ), 30.10.2 (M = 2: crop → colore; crop + tinta/luminosità/saturazione → forma), 30.11. Formule verificate con WebFetch sulla pagina web.
- visionbook cap. 37 (transfer_learning.html): 37.2, 37.3 (Algorithm 37.1, fig. 37.2), 37.3.1 (DINO congelato, LoRA), 37.3.2 (heads and probes), 37.4.1 (distillazione, per L22).
- visionbook cap. 36 § 36.2 (invarianza dell'etichetta), cap. 12 § 12.7.4 (temperatura), cap. 24 (invarianza per architettura): solo richiami.
- Szeliski 2a ed. § 5.3.4 (eq. 5.57 Hadsell, eq. 5.58 InfoNCE/NT-Xent, τ "quanto stretti i cluster", Sohn 2016), § 5.4.7 (pretext task, Wu, MoCo, PIRL, SimCLR, MoCo v2, CLIP, BYOL, SimSiam con solo stop-gradient).
- Prince § 9.3.6–9.3.7 (generativo contro contrastivo; posizione relativa classificata come contrastiva) e note del cap. 9 (SimCLR).

## Refusi del libro (verificati sulla pagina web)
- Eq. 30.4 Hadsell: parentesi fuori posto (−m_pos dentro D) e segno − davanti al secondo max (va +).
- Eq. 30.3 k-means: 1/N invece di 1/|cluster j|.
- Testo dopo fig. 30.13: "x = V1(X), y = V1(X)", va y = V2(X).
- La radice quadrata spuria in § 30.4 indicata nel brief NON compare nella versione web attuale (eq. 30.1 e L_recon sono ‖·‖²): non segnalata.
- Szeliski 5.57 in forma log L_S/log L_D, non quella dell'articolo (somma di quadrati): segnalato solo come differenza.

## Errori e imprecisioni delle slide (segnalati nelle schede)
1. Pag. 3: refusi "eng goal" (end) e "fing" (find).
2. Pag. 34: "SimCLR uses batches > 4096": nell'articolo default 4096, esperimenti 256–8192 (32K in appendice). Precisazione.
3. Pag. 35: "Positive pairs are perfectly aligned, the loss is zero" vale per loss di solo allineamento (e SimSiam arriva a −1); con InfoNCE il collasso dà ℒ = log N.
4. Pag. 43: SimSiam chiamato "contrastive": non usa negativi (didascalia fig. 1 dell'articolo; Szeliski § 5.4.7). "Projector only in the first augmentation": è il predictor h; il projector fa parte di f su entrambi i rami; con la loss simmetrizzata h agisce a turno su entrambe le viste.
Controllati e corretti: triplet a pag. 23 con distanze al quadrato (come FaceNet, α = 0.2); NT-Xent a pag. 38 con 2B − 2 negativi; k-NN pesato pag. 9; NCM pag. 10 (equivalenza lineare dimostrata nella scheda).

## Conti verificati (numpy)
- Figura temperatura (pag. 33) riprodotta con s = (0.8, 0, −0.3, 0.2): τ = 0.1 → p = (0.997, 0.0003, 0.00002, 0.0025), L = 0.003; τ = 0.5 → (0.620, 0.125, 0.069, 0.187), L = 0.479; τ = 2 → (0.335, 0.224, 0.193, 0.248), L = 1.095. Quota del negativo più difficile (s = 0.2) sul peso dei negativi: 0.876, 0.491, 0.373. Gradienti (p − 1[+])/τ: τ = 2 (−0.333, 0.112, 0.097, 0.124); τ = 0.5 (−0.761, 0.25, 0.137, 0.373); τ = 0.1 (−0.028, 0.003, 0.0002, 0.025).
- log 4 = 1.386; log 8191 = 9.01 (collasso con B = 4096).
- B = 4096: 8192² = 67 108 864 similarità ≈ 268 MB in float32; 2B − 2 = 8190 negativi.
- Triplet: α = 0.2, d_p = 0.5, d_n = 0.6 → 0.1; d_n = 1.0 → 0.
- Jigsaw: 9! = 362 880 permutazioni, 1000 usate.
- SimSiam: std attesa 1/√2048 ≈ 0.022.

## Numeri dagli articoli (WebFetch su arXiv)
- SimCLR (2002.05709): batch default 4096 (256–8192), Tab. 5 τ: 0.05 → 59.7, 0.1 → 64.4, 0.5 → 60.7, 1 → 58.0; testa MLP 1 strato nascosto, z a 128 dim, h > z di oltre 10 punti; R50 69.3%, R50(4×) 76.5%; crop 0.08–1, jitter s = 1 (0.8/0.8/0.8/0.2) p = 0.8, grigio p = 0.2, blur p = 0.5 σ ∈ [0.1, 2]; LARS lr 0.3·B/256; BN globale; loss su (i, j) e (j, i).
- SimSiam (2011.10566): projector 3 strati (2048), predictor 2048-512-2048; senza stop-grad o senza predictor 0.1%; batch 512 default, SGD lr 0.05·B/256; 67.7% (default) / 68.1% (Tab. 4) a 100 epoche, 71.3% a 800.
- Da conoscenza standard non rifetchata: MoCo coda 65 536, m = 0.999, τ = 0.07; Wu et al. 2018 k = 200, τ = 0.07; CPC I ≥ log N − L; Wang-Isola α = 2, t = 2; Colorful Colorization Q = 313; Noroozi 1000 permutazioni; FaceNet α = 0.2.

## Dubbi
- Nella fig. di pag. 11 il prototipo arancione è solo di poco più vicino del verde (stima a occhio dai pixel): scritto con cautela.
- Righe della figura ExemplarCNN (pag. 24): tipo di trasformazione per riga descritto in modo generico (geometriche sopra, fotometriche sotto).
- Il supervisionato R50 di riferimento nella fig. 7 di SimCLR (≈ 76%): non riportato con decimali.
