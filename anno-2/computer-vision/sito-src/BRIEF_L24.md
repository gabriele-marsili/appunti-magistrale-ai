# Contesto per L24 (12 novembre 2026)

Tutto si fa nel container cloud, cartella /tmp/cv. Non pubblicare nulla, non usare il tool Artifact, non toccare il Mac.

## La lezione
- **L24** · 11 novembre 2026 · "Vision-Language Models (VLMs)" · slide di **Donald Shenaj** (donald.shenaj@di.unipi.it), non del prof. Carta.
- PDF: /mnt/user-data/uploads/CV/Lessons/L24.pdf (61 pagine, 16:9). Testo: /tmp/cv/pdf/L24.txt (pdftotext -layout). Renderizza le pagine con pdftoppm per GUARDARE le figure (es. `pdftoppm -r 80 -f 14 -l 17 -png ...` e montage 2x2 con PIL), non inventare il contenuto delle figure.
- Numerazione: il footer stampa «n / 61» con n = pagina del PDF (copertina compresa). Le divisorie di sezione (pag. 7, 35, 41, 48, 54) non hanno footer. In slides.py usa `def P(n): return f' <em>· pag. {n}/61</em>'` e passa `printed=P(n)` alle slide numerate, `printed=''` alle divisorie (kind='div').
- **Pagina 61** non è una slide: è la pagina «panoramica» generata da Beamer con le miniature di tutte le 60 slide (contiene di nuovo tutte le immagini ad alta risoluzione: è il motivo per cui il PDF pesa 77 MB e OneNote non lo importa). Scheda breve che lo spiega. Accanto c'è Lessons/L24_onenote.pdf, la versione compressa (11 MB) creata da noi per OneNote.
- Sezioni (id e intervalli da usare in sec=):
  - ("l24-intro", "Introduzione", "slide 1–6")
  - ("l24-clip", "Allineare visione e linguaggio: CLIP", "slide 7–34")  (divisoria 7)
  - ("l24-caption", "Dalle immagini al testo: captioning", "slide 35–40")  (divisoria 35)
  - ("l24-vqa", "Il testo come rappresentazione e VQA", "slide 41–47")  (divisoria 41)
  - ("l24-instr", "VLM con instruction tuning", "slide 48–53")  (divisoria 48)
  - ("l24-task", "Altri compiti: ragionamento e grounding", "slide 54–56")  (divisoria 54)
  - ("l24-concl", "Sintesi e riferimenti", "slide 57–61")
- Prossime lezioni (slide 59): parameter-efficient fine-tuning (PEFT) e un lab su VLM e PEFT.
- Lezioni precedenti da collegare: L21 (InfoNCE, SimCLR, NT-Xent, temperatura, projection head), L22 (SSL, DINO, foundation model, BYOL), L23 (lab SSL: linear probe, k-NN, DINOv3 come featurizer congelato), L17-L18 (ViT, token, [CLS], self-attention), L15 (softmax, cross-entropy), L19 (detection, box: per il grounding), L16 (ResNet).

## Libro (leggere davvero)
- **Capitolo principale: visionbook cap. 51 "Vision and Language", https://visionbook.mit.edu/VLMs.html** . Report dettagliato già fatto: /tmp/cv/L24_libro_cap51.md (leggilo; per formule e dettagli puoi rileggere la pagina con WebFetch). Le figure delle slide marcate "[visionbook]" (pag. 8, 22, 23, 28, 36, 38, 42, 43) vengono da questo capitolo (fig. 51.1, 51.3, 51.4, 51.6, 51.7?, 51.11, 51.12, 51.13: verifica quali).
- Altri capitoli: cap. 30 § 30.10 contrastive learning, eq. 30.4 InfoNCE (https://visionbook.mit.edu/representation_learning.html); cap. 26 Transformers (https://visionbook.mit.edu/transformers.html: token, self-attention, § 26.10 masked/causal attention); cap. 32 § 32.7 modelli autoregressivi (https://visionbook.mit.edu/generative_models.html); cap. 34 modelli generativi condizionati, § 34.4.2 cVAE (https://visionbook.mit.edu/conditional_generative_models.html); cap. 37 transfer learning (37.3.1 moduli congelati, 37.3.2 probe) (https://visionbook.mit.edu/transfer_learning.html); cap. 13 per t-SNE (https://visionbook.mit.edu/neural_nets_as_distribution_transformers.html).
- Szeliski 2a ed. § 6.6 "Vision and language" (captioning, VQA, CLIP; non abbiamo il PDF: cita solo il paragrafo, niente numeri di pagina). Prince, Understanding Deep Learning, cap. 12 Transformers (cross-attention, decoder, encoder-decoder).
- Refusi del cap. 51 trovati (verificali prima di citarli): z_t^b = f_t(t^a) invece di f_t(t^b); "il prodotto scalare fra vettori unitari è proporzionale all'angolo" (è il coseno dell'angolo, monotono, non proporzionale); S^{d_z} descritta come ipersfera (d_z−1)-dimensionale (notazione incoerente: la sfera unitaria di R^{d_z} è S^{d_z−1}); "text encoder" al posto di "text decoder" nel testo e nella didascalia della fig. 51.11; m mai definito nella cross-attention (è la dimensione delle chiavi). Il libro non mette la temperatura nella loss di CLIP; CLIP la usa (appresa).
- Solo articoli (non nel libro): ConVIRT, LiT, OpenCLIP, LAION-5B, ALIGN, BLIP-2 (Q-Former), LLaVA e LLaVA-1.5, Qwen-VL, NLVR2, RefCOCO, "red circle" (Shtedritski et al.), Paiss et al. (counting), Yuksekgonul et al. (bag-of-words, ARO). Per i numeri usa solo quelli delle slide o verificati sugli articoli (WebSearch/WebFetch su arXiv). Non inventare numeri.

## Verifiche già fatte da me sulle slide (dati che risultano corretti rispetto agli articoli)
CLIP: text encoder 63M parametri, 12 strati, larghezza 512, 8 teste, feature del token [EOS]; proiezione lineare (niente MLP come in SimCLR); prompt "A photo of a {label}." +1,3 punti su ImageNet, ensemble di prompt (80 template) +3,5 ulteriori, quasi 5 in tutto; zero-shot meglio del linear probe su ResNet-50 in 16 dataset su 27; visual n-grams 11,5% su ImageNet zero-shot; temperatura appresa come log(1/τ) (nel pseudocodice `logits = ... * np.exp(t)`), inizializzata a 0,07 e con il fattore limitato a 100. LAION-5B: 5,85 miliardi di coppie (2,32 inglese, 2,26 multilingue, 1,27 lingua indeterminata). BLIP-2: 32 query a 768 dimensioni, Q-Former inizializzato da BERT-base, ITC+ITM+ITG con maschere diverse, stage 2 con encoder e LLM congelati; nel fine-tuning VQA si aggiornano image encoder e Q-Former, LLM congelato. LLaVA: CLIP ViT-L/14 + Vicuna, stage 1 su 595K coppie filtrate da CC3M (solo W), stage 2 su 158K istruzioni (W + LLM); precisazione: le istruzioni le ha generate GPT-4 SOLO testuale, a cui venivano dati caption e box dell'immagine, non l'immagine. Qwen-VL: ViT-bigG di OpenCLIP, Qwen-7B, 256 query, un solo strato di cross-attention con posizioni 2D, stage 224² → 448² → instruction tuning (350K dialoghi, ViT congelato).
Possibili imprecisioni (verificale sul PDF prima di segnalarle; non inventarne altre): pag. 15 chiama l'image encoder fℓ mentre altrove è f_v (è la notazione del libro, ℓ = image); pag. 18 la loss L_{I→T} è scritta come somma su k mentre il pseudocodice (pag. 20) fa la media e divide per 2 la somma delle due direzioni (pag. 19 lo dice: solo un fattore di scala); pag. 12/13 "dz" vs d_e del pseudocodice. Controlla anche le formule di pag. 9 (ConVIRT), 27 (zero-shot con τ), 30 (retrieval), 38 (cross-attention), 45 (VQA), 49 (LLaVA), 55, 56.

## Standard
- Regole: /tmp/cv/BRIEF.md, /tmp/cv/LIBRO.md (sezione "Come integrare"), /tmp/cv/DISPENSA.md, /tmp/cv/RISCRITTURA.md (standard attuale della dispensa), /tmp/cv/COPIONE.md, /tmp/cv/FIGURE.md.
- Lezione modello recente con PDF: /tmp/cv/L22/ (meta.py, slides.py con helper P/R/LK per i link ai capitoli, extra.html, dispensa.html, copione.json). Stile e densità da replicare.
- Video: SOLO verificati con WebSearch (ID reali), mai inventati.
