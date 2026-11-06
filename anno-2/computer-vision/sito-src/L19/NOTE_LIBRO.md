# L19 Object detection e segmentazione – note di lavoro (29/10/2026)

Materiale: slide /mnt/user-data/uploads/CV/Lessons/L19.pdf (63 pagine, Donald Shenaj, 28/10/2026). Footer "n / 63" con n = pagina del PDF (copertina compresa). Divisorie: 8, 38, 49, 58. La pag. 63 è un indice a miniature, non una slide. Pag. 58–62 appendice. Lab collegato: L20 (altro lavoro).

## Mappa sezioni
l19-intro (1–7), l19-det (8–37), l19-seg (38–48), l19-inst (49–56), l19-app (57–63: riferimenti e appendice).

## Capitoli usati (visionbook)
- Cap. 50 (object_recognition_v3.html): § 50.4.1 (finestra scorrevole, Algorithm 50.1; selective search come strategia a due stadi; cascata, fig. 50.16; predizione globale alla YOLO § 50.4.1.4; NMS in tre righe), § 50.4.2 (loss con indicatore, loss IoU contro L2, fig. 50.18), § 50.4.3 (AP alla PASCAL, fig. 50.19), § 50.5 (class segmentation, pesi per classe, IoU medio), § 50.6 (instance segmentation: ritaglio nella scatola + funzione binaria; loss a tre termini con due λ). Panottica non trattata.
- Cap. 24 § 24.2.3 (dilatazione, fig. 24.9, avvertenza sull'aliasing). Refuso: cascata d = 1, 2, 4 scritta 9 × 9, il supporto è 15 × 15 (stesso della L15).
- Cap. 26 § 26.6.1–26.6.3 (attenzione) per DETR e SegFormer.
- Prince § 10.2.3, § 10.5.2 (YOLO), § 10.5.3. Szeliski § 6.3–6.4 (sottoparagrafi NON verificati; la panottica è indicata come § 6.4.3 nelle slide/schede).
- NON nei libri: R-CNN/Fast/Faster, SSD, FCOS, DETR, mAP COCO, DeepLab/ASPP, SETR, SegFormer, DPT, RoIAlign, PQ.

## Errori e imprecisioni delle slide (segnalati nelle schede)
1. Slide 61: H(x) = sign(∑ α_t h_t(x)) con h_t ∈ {0, 1} (slide 13) e α_t > 0: la somma è sempre ≥ 0. Corretto con h ∈ {−1, +1}; nell'articolo di Viola-Jones, con h ∈ {0, 1}, soglia ½ ∑ α_t e α_t = ln((1 − ε)/ε) senza ½.
2. Slide 33: «la loss minimizza lo stesso costo del matching». Nell'articolo (eq. 2–3) nel matching compare −p̂ (probabilità), nella Hungarian loss −log p̂, e la classe ∅ pesa 1/10. Motivo del matching con la probabilità: termine di classe commensurabile con quello di scatola.
3. Slide 60: rimanda a un «worked example on the main lecture slide» che nella slide 35 non c'è. Inoltre la ricerca è solo fra le GT non abbinate, mentre PASCAL (libro § 50.4.3) prende la GT con IoU massimo fra tutte.
4. Slide 32: va precisato che la backbone di DETR è una CNN (non un ViT); YOLOS è il detector nativo ViT.
5. Slide 57: PSPNet è nei riferimenti ma non compare nelle slide della lezione (era in L17). Conteggio riferimenti: 27.
6. Slide 39: la cascata di dilatazioni (1, 2, 4) ha supporto 15, non 9 (refuso già nel libro).
7. Slide 45 (conto controllato): la matrice di attenzione scende da N² a N·N/R = N²/R (verificato: 16384 × 256 = 4 194 304 ≈ 4.2·10⁶, 64× meno di 2.7·10⁸).

## Conti verificati (a mano o con numpy)
- IoU A = [0, 0, 10, 10], B = [5, 5, 15, 15]: 25/175 ≈ 0.143. Figura iou: 9/191, 50/150, 81/109.
- Immagine integrale (figura): rettangolo 3 × 3 = 11; 26 − 10 − 6 + 1 = 11.
- Offset: ancora (100, 80, 40, 80), GT (110, 90, 60, 72): t = (0.25, 0.125, 0.405, −0.105); decodifica 60 e 72; angoli 80, 54, 140, 126.
- Selective search: intersezione di istogrammi 0.7; n superpixel → 2n − 1 regioni.
- Ancore: 9 per posizione, 40 × 60 × 9 = 21 600; IoU delle 9 ancore dell'esempio (figura): 0.42, 0.44, 0.44, 0.55, 0.83, 0.55, 0.39, 0.39, 0.39 (soglie 0.7/0.3 dell'articolo Faster R-CNN, non scritte nelle slide).
- YOLOv1: 7 · 7 · (2 · 5 + 20) = 1470. SSD: scale 0.2, 0.34, 0.48, 0.62, 0.76, 0.9.
- FCOS: center-ness √(1/3) ≈ 0.58.
- NMS (figura): clusters 0.95/0.87/0.72 e 0.90/0.55, τ = 0.5.
- DETR (figura): matrice dei costi con colonna ∅ a costo 0; assegnamento ottimo (scipy linear_sum_assignment) q1→A 0.2, q2→B 0.3, q3→∅ 0: totale 0.5.
- AP: 3 GT, TP FP TP TP FP: precisione 1, .5, .667, .75, .6; recall .333, .333, .667, 1, 1; AP interpolato = (1 + .75 + .75)/3 = 0.833.
- Dilatazione: d = 1, 2, 4 → r = 15 (verificato con la figura: 15 posizioni distinte), contro 7.
- Attenzione SegFormer per stadio (N, R) = (16384, 64), (4096, 16), (1024, 4), (256, 1): N²: 2.7e8, 1.7e7, 1.05e6, 6.6e4; N²/R: 4.2e6, 1.05e6, 2.6e5, 6.6e4.
- RoIAlign: v = 0.7·0.4·9 + 0.3·0.4·7 + 0.7·0.6·8 + 0.3·0.6·5 = 7.62 (punto (2.3, 1.6)); slide: (3.4, 5.7) → pesi 0.18, 0.12, 0.42, 0.28.
- PQ: IoU 0.9, 0.8, 0.7; FP 1; FN 2: SQ 0.8, RQ 3/4.5 = 0.667, PQ ≈ 0.533.
- DPT ViT-B/16 a 384: griglia 24 × 24 → 96, 48, 24, 12.

## Dubbi
- Numeri di sottoparagrafo di Szeliski § 6.3–6.4 non verificati.
- Soglie 0.7/0.3 per le ancore, 1/10 sul peso di ∅ e la mAP di COCO a 10 soglie: dagli articoli, non dai libri.
- Durate dei video non verificabili (WebFetch di YouTube non le restituisce): scritto solo «Video».
- La dispensa ha circa 5900 parole di prosa (oltre le 5500 indicate): 63 pagine di slide con 16 sezioni.
