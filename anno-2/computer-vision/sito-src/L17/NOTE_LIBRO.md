# L17 ViT, U-Net, Dense Prediction (Donald Shenaj, 22 ottobre 2026) – note di lavoro dal libro (24/10)

PDF: /tmp/cv/L17/L17.pdf, 43 pagine. Footer "n / 43" con n = pagina PDF, copertina compresa ("1 / 43"): nelle schede printed=' · pag. n/43' su tutte. Segnalibri del PDF: Dense Prediction Tasks (pag. 3), Encoder-Decoder Architectures (pag. 11), Vision Transformers (pag. 24). Unica divisoria: pag. 24 (titolo + prima pagina dell'articolo ViT con abstract). Pag. 43 = indice a miniature delle pagine 1–42 (non è una slide).
Sezioni nel sito: l17-intro (1–2), l17-task (3–10), l17-encdec (11–23), l17-vit (24–39), l17-concl (40–43).
Render a 80 dpi e montaggi 2x3: /tmp/claude-0/r80/ (m0..m7.png); U-Net ad alta risoluzione verificata (vh-16.png).

## Mappa pagine PDF -> titolo
1 copertina; 2 Lecture Outline; 3 Beyond Classification (6 compiti, fig. Cityscapes/MiDaS/Sintel/OpenPose); 4 Semantic/Instance/Panoptic (fig. PSPNet fig. 8 Cityscapes: input, GT, predizione); 5 Monocular Depth (fig. Eigen 2014 fig. 3 NYU); 6 Optical Flow (fig. visionbook 48.1 con ruota dei colori); 7 Keypoint/Pose (OpenPose fig. 2, ballerini); 8 Same Shape, Different Content (tabella); 9 Why Plain CNNs Are Not Enough (224×224×3 → 7×7×2048); 10 Shape Arithmetic (H_out, r_L, disegni); 11 Encoder-Decoder (fig. SegNet); 12 1×1 conv; 13 "Fully Connected Layers" (post di LeCun 2015); 14 FCN (Long et al. fig. 1, AlexNet convolutionalizzata, 21 classi); 15 FCN-32s/16s/8s; 16 U-Net (fig. 1 originale); 17 U-Net building blocks; 18 Deconv vs resize+conv (Distill, Odena et al.); 19 Sub-pixel (ESPCN fig. 1); 20 MiDaS; 21 RAFT (fig. 1); 22 Losses (CE, focal, Dice); 23 Metriche (mIoU, AbsRel, RMSE, EPE, PCK); 24 divisoria ViT; 25 ViT (fig. 1 ViT); 26 Patch embedding (Pisa, z0); 27 Positional embeddings (sinusoidali vs apprese); 28 Positional 2D (fattorizzate, Swin bias, RoPE); 29 Self-attention intuizione (Pisa, t1 t2 t3: rifacimento della fig. 26.11 del visionbook); 30 Self-attention formula (√d_k, multi-head, W_QKV); 31 Residual blocks (pre-norm); 32 Compute & params (12D², 25/8/67%, 85M); 33 BN/LN/IN/GN (Wu & He fig. 2); 34 Why LayerNorm; 35 What ViT learns (fig. 7 e 10 ViT: similarità posizionali 7×7, distanza media di attenzione ViT-L/16); 36 Attention rollout (fig. 6 ViT, cane e aereo); 37 CNNs in disguise; 38 Patch tokens as feature grid (9 token → 3×3); 39 ViT vs CNN (tabella + fig. 5 ViT); 40 One architecture many tasks; 41 Summary; 42 References (24 voci); 43 miniature.

## Libro letto (visionbook.txt locale + pagine del PDF renderizzate per le formule)
- Cap. 24: § 24.1, 24.2.5 (eq. 24.7 dilata-poi-convolvi, UpConv/deconvolution), 24.7, 24.8 (fig. 24.27), 24.9 (FCN = filtro non lineare scorrevole, fig. 24.28), 24.10, 24.11.1 (encoder/decoder = piramidi di analisi/sintesi; vantaggi: memoria, collo di bottiglia; fig. 24.29–24.30), 24.11.2 (U-Net: skip a specchio l ↔ L−l, concatenazione sui canali, somiglianza con le piramidi steerable, fig. 24.31). Nessuna formula chiusa del campo recettivo; nessun "transposed convolution".
- Cap. 21 § 21.4.1–21.4.5: espansione = trasposta della decimazione, filtri nearest e bilineare, k=2 → binomiale [1/2, 1, 1/2], fig. 21.21 (il binomiale non toglie del tutto le copie dello spettro).
- Cap. 26 tutto (vedi anche /tmp/cv/libri/NOTE_L16_L17.md). Verificati sul PDF: eq. 26.9 (pag. PDF 569: T[n(N/K)+m, c2] = b[c2] + Σ_{c1} Σ_{k1,k2=−K}^{K} w[c1,c2,k1,k2] x_in[c1, Kn−k1, Km−k2]; pseudocodice conv(x_in, 3, d, kernel=K, stride=K)); eq. 26.12 (pag. 573: p_x = [sin x, sin(x/B), …, sin(x/B^P)]ᵀ, p = [p_x; p_y], CONCATENATO). Fig. 26.11 (pag. 564) = schema t1 t2 t3 "attention/sum" ripreso dalla slide 29 con la torre di Pisa; fig. 26.2 tokenizzazione ripresa dalla slide 26.
- Cap. 12 § 12.7.3 (batchnorm, L2-norm, layernorm con γ, β; trasposta della batchnorm).
- Cap. 50 § 50.5 (CE per pixel su esempi, classi e posizioni; pesi di classe per area; pixel accuracy dominata dagli oggetti grandi, meglio IoU medio per classe), § 50.5.1 (non conta le istanze, niente trasparenze), § 50.6 (Mask R-CNN-like, loss L_cls + 1(y≠0)(λ1 L_loc + λ2 L_seg)). Pag. PDF 1046–1047.
- Cap. 43 § 43.4.1–43.4.3 (fonti GT, loss L2 e "scale-invariant", log o disparità, encoder-decoder con skip fig. 43.4).
- Cap. 48 § 48.2 (definizione, fig. 48.1 = figura della slide 6), cap. 49 § 49.2.1 (FlowNet, pipeline con 3D cost volume fig. 49.2, endpoint error, dataset Middlebury/KITTI/Sintel/Flying Chairs; GT "probabilmente il limite principale").
- Prince: § 10.4.1–10.4.3 (upsampling: duplicazione, max unpooling, bilineare, conv trasposta fig. 10.13 = matrice trasposta; conv 1×1 = stessa FC sui canali in ogni posizione), § 10.5.3 (rete di Noh et al. 2015, encoder-decoder/hourglass), § 11.4 BatchNorm e note del cap. 11 (LayerNorm, GroupNorm, InstanceNorm, fig. 11.14 da Wu & He; scala e offset per canale in tutte), § 11.5.3 U-Nets and hourglass networks (valid conv e crop, concatenazione; hourglass somma; heatmap per la pose), § 12.2–12.4 (self-attention, 12.3.1 codifiche assolute/relative, 12.3.2 scala √D_q per la saturazione della softmax, 12.3.3 multi-testa con D/H, 12.4 strato post-norm eq. 12.13), note cap. 12 (LayerNorm scelta da Vaswani perché le statistiche NLP variano fra batch; LayerNorm fuori dal residuo fa ridurre i gradienti, Xiong et al. 2020), § 12.10.2 ViT (token <cls>, JFT 303M immagini 18k classi, 11,45% top-1 error, serve tanto pre-training), § 12.10.3 transformer multi-scala.
- Szeliski 2a ed.: § 5.4.1 (pooling/unpooling, transposed convolution fig. 5.36 = zeri + conv, "U-Nets and Feature Pyramid Networks"), § 5.5.3 (fig. 5.57 ViT), § 6.4 (6.4.1 medicale, 6.4.2 istanza, 6.4.3 panottica, 6.4.5 pose; FCN, CRF, U-Net, PSPNet, Cityscapes), § 9.3.1 (RAFT: volume di correlazione (W×H)² multi-risoluzione), § 12.8 (MiDaS, film 3D, protocollo zero-shot).

## Non nei libri
[CLS] (solo Prince), RoPE, bias relativo di Swin (Prince 12.3.1 ne dà l'idea generale), GroupNorm/InstanceNorm (solo Prince note cap. 11), Dice, focal, AbsRel, RMSE, PCK, pixel shuffle, attention rollout, MiDaS loss in dettaglio (Ranftl et al.), RAFT (solo Szeliski in breve), SETR/DPT/SegFormer, panottica nel visionbook (Szeliski 6.4.3 sì).

## Errori delle slide (verificati, con riquadro Attenzione)
- Pag. 22: «Dice loss / Soft-IoU loss … from the IoU overlap formula»: la formula è il coefficiente di Dice 2|A∩B|/(|A|+|B|), non l'IoU; relazione D = 2J/(1+J); la soft-IoU è un'altra loss.
- Pag. 33: «All three normalize…» ma ne elenca quattro (BN, LN, IN, GN), anche in figura.

## Imprecisioni chiarite senza Attenzione
- Pag. 22 focal: nella formula p̂_i va letto come p_t (probabilità della classe vera); manca il peso α_t di Lin et al. (la prima formula del paper è senza α: non è un errore). Dice con i quadrati al denominatore = versione V-Net (citata nei riferimenti); ε corretta.
- Pag. 28 RoPE: «qᵀk depends only on the relative offset» = la posizione entra solo come offset relativo (il prodotto dipende anche dal contenuto).
- Pag. 19: il pixel shuffle evita la sovrapposizione disuguale ma con inizializzazione casuale può dare scacchiera (Aitken et al. 2017, ICNR).
- Pag. 21: «it never compares the two images»: FlowNetS impara comunque; il cost volume esplicito funziona meglio.
- Pag. 35: la griglia 7×7 di similarità posizionali nel paper è di ViT-L/32 (224/32 = 7); il grafico delle distanze è ViT-L/16.

## Conti verificati
- Pag. 10: H_out = ⌊(7 + 2 − 2 − 1)/2⌋ + 1 = 4 ✓; r = 1 + 2 + 2 = 5 con due 3×3 s=1 ✓; formula r_L = r0 + Σ (k_l−1) Π_{i<l} s_i ✓; k_eff = d(k−1)+1 ✓.
- U-Net (pag. 16, fig. ad alta risoluzione): 572→570→568 | 284→282→280 | 140→138→136 | 68→66→64 | 32→30→28 | up 56→54→52 | 104→102→100 | 200→198→196 | 392→390→388; canali 64,128,256,512,1024 e ritorno, uscita 388×388×2; crop 64→56, 136→104, 280→200, 568→392 ✓.
- FCN: pool3/4/5 stride 8/16/32; a 224: 28, 14, 7 ✓.
- CE, Dice (V-Net), AbsRel, RMSE, EPE, PCK: definizioni standard ✓.
- Patch embedding: 224/16 = 14, N = 196, 197 token ✓; E ∈ R^{(P²C)×D} ✓ (768×768 = 589.824 per ViT-B/16), E_pos 197×768 = 151.296.
- Var(qᵀk) = d_k ✓ (indipendenza, media 0, varianza 1); d_k = 64 per ViT-B → std 8 senza scala.
- Multi-head: h·N²·(D/h) = N²D ✓.
- 12D²: 3D² + D² + 8D² ✓; 25% / 8,3% / 66,7% ✓; 12·768² = 7.077.888 ≈ 7,1M ✓; ×12 = 84,9M ≈ 85M ✓; ViT-B/16 reale ≈ 86M (bias, LN, embedding 0,59M, pos 0,15M, testa 0,77M).
- «halving P quadruples N, compute grows 16×»: vero per la parte di attenzione (∝ N²D); la parte lineare (≈ 12ND²) cresce 4×. ViT-B/16 a 224: lineare 1,39 G MAC/blocco vs attenzione 2N²D = 0,06 G; totale ≈ 17,5 G per 12 blocchi (dichiarati 17,6 GFLOPs). L'attenzione domina per N > 6D.
- Tokenizzazione = conv kernel P stride P senza padding ✓; QKV e MLP = conv 1×1 ✓.
- Permutation-equivariance (pag. 27): vera per attenzione + MLP senza posizioni; il [CLS] non permutato dà uscita invariante.

## Refusi/incoerenze del libro (riportati in "Studia dal libro")
- 26.7 pseudocodice softmax(..., dim=0) contro "per riga" dell'eq. 26.6; 26.7 "token norm" senza parametri contro 12.7.3 layernorm con γ, β; 26.8 "ogni strato equivariante alle permutazioni è equivariante alle traslazioni" (vale senza posizioni); 26.9 eq. 26.9 somma da −K a K; 26.4.4, 26.9.4, 26.9.5.1 refusi minori; 49.2.1.2 endpoint error "media delle distanze" ma formula = somma dei quadrati (pag. PDF 1016); 43.4.2 loss "scale-invariant" senza log = solo shift-invariant (già in L13).

## Collegamenti usati
L15 (campo recettivo, stride/aliasing, 1×1, BN/LN, ResNet), L6 (espansione con zeri, interpolazione, piramide laplaciana analisi/sintesi), L13 (stanza di Ames, cost volume, scala), L14 (mIoU della segmentazione LiDAR), L3 (composizione di convoluzioni, matrice della conv).
