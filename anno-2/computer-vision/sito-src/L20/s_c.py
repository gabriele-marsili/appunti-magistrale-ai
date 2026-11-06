
# ---------------------------------------------------------------- parte 3 video

s(20, "Il video di guida: apertura", """
<pre>VIDEO_PATH = "./media/cityscapes_heidelberg.mp4"
if not os.path.exists(VIDEO_PATH):
    urllib.request.urlretrieve(VIDEO_ZIP_URL, zip_path)      # VIDEO_ZIP_URL non è definita!
cap = cv2.VideoCapture(VIDEO_PATH)
video_fps = cap.get(cv2.CAP_PROP_FPS)
# nostra uscita: video: 2048x1024 @ 10.0 FPS, 201 frames total</pre>
<ul>
<li>La Parte 3 applica SegFormer a un <b>video reale di guida</b> (Heidelberg, da Cityscapes): 2048×1024 pixel, <b>10 FPS</b>, 201 frame (20 secondi).</li>
<li><code>cv2.VideoCapture</code> legge il file; le sue proprietà (<code>CAP_PROP_FPS</code>, larghezza, altezza, numero di frame) servono per configurare l'uscita.</li>
<li>Un video è solo una <b>sequenza di immagini</b>: la segmentazione di un video «semplice» è la segmentazione di ogni frame, senza usare l'informazione temporale fra frame vicini.</li>
</ul>
<div class="box w"><b>Attenzione: bug se il video non c'è</b><p>Se il file non esiste, il ramo di download usa la variabile <code>VIDEO_ZIP_URL</code> che <b>non è definita da nessuna parte</b>: si ottiene un <code>NameError</code>. Con il video già in <code>./media/</code> (come nella cartella del lab) il ramo non viene eseguito e il problema non si vede. Soluzione: definire l'URL (o rimuovere il ramo) e scrivere quale zip contiene la cartella <code>media/</code>.</p></div>
""", sec=("l20-p3", "Parte 3 · Segmentazione su video", 'schede 20–22'), printed=NB + 'celle 47–48')

s(21, "SegFormer frame per frame e scrittura del video", """
<pre>N_FRAMES = 20
writer = cv2.VideoWriter("processed_video.mp4", cv2.VideoWriter_fourcc(*"mp4v"), 5.0, (video_w, video_h))
while cap.isOpened() and frame_id < N_FRAMES:
    ret, frame_bgr = cap.read()
    if not ret: break
    frame_pil = Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))   # OpenCV legge in BGR
    t0 = time.perf_counter()
    frame_overlay = overlay_mask(frame_pil, decode_labels(segment_image(seg_model, seg_processor, frame_pil)), 0.5)
    frame_latencies.append(time.perf_counter() - t0)
    writer.write(cv2.cvtColor(frame_overlay, cv2.COLOR_RGB2BGR))               # il writer vuole BGR
# poi ffmpeg ricodifica in H.264 yuv420p (+faststart) per il browser, e IPython mostra il video</pre>
<ul>
<li><b>Colori</b>: OpenCV legge e scrive in <b>BGR</b>, il resto della pipeline (PIL, SegFormer, matplotlib) usa <b>RGB</b>: bisogna convertire in entrata e in uscita (<code>cvtColor</code>), altrimenti i colori risultano scambiati (rosso e blu).</li>
<li><b>Misura del tempo</b>: il cronometro include segmentazione, decodifica dei colori e overlay (non la lettura del video).</li>
<li><code>N_FRAMES = 20</code> serve a non aspettare: solo i primi 2 secondi di video. Ogni frame costa circa 1 secondo su CPU.</li>
<li>La codifica <code>mp4v</code> di OpenCV non si riproduce nei browser: <code>ffmpeg</code> la ricodifica in <b>H.264</b> con <code>-pix_fmt yuv420p</code> (richiesto dai browser) e <code>-movflags +faststart</code> (il file parte prima di essere scaricato per intero); <code>-crf 23</code> è la qualità (più basso = migliore).</li>
</ul>
<div class="box w"><b>Attenzione: il video di uscita va a metà velocità</b><p>Il <code>VideoWriter</code> è creato con <b>5.0 FPS</b>, ma il video di ingresso è a <b>10 FPS</b>: il video elaborato dura il doppio (20 frame a 5 FPS = 4 secondi invece di 2) e sembra al rallentatore. Va usato <code>video_fps</code>, letto dalle proprietà nella cella 48. Inoltre il notebook richiede che <code>ffmpeg</code> sia installato (<code>subprocess.run(..., check=True)</code> fallisce altrimenti).</p></div>
<div class="box k"><b>Da saper fare</b><p>Spiegare perché in un loop di inferenza si usa <code>torch.no_grad()</code> (già dentro <code>segment_image</code>): non servono i gradienti, il che risparmia memoria e tempo.</p></div>
""", img='img/nb_video_frame.png', printed=NB + 'celle 49–51')

s(22, "Analisi della latenza per frame", """
<pre>steady_state = frame_latencies[1:]                    # si scarta il primo frame (riscaldamento)
mean_fps = 1.0 / np.mean(steady_state)
# nostra uscita:
# First frame: 997.5 ms
# Steady-state mean latency: 1087.3 ms -> 0.9 FPS</pre>
<ul>
<li>Il grafico mostra la latenza di ciascun frame. L'idea del notebook: <b>il primo frame è più lento</b> (compilazione dei kernel CUDA, cache), poi la latenza si assesta.</li>
<li>Sulla nostra <b>CPU</b> non è così: primo frame 998 ms, media degli altri 1087 ms (<b>0,9 FPS</b>), con picchi a 1220 e 1504 ms, che sono rumore di una CPU condivisa. Lo scarto del primo frame è una scelta legittima su GPU, ma qui toglie solo un frame un po' più veloce.</li>
<li>Per leggere la figura delle anteprime (frame 0, 6, 12, 19): la strada è viola, i marciapiedi rosa, i cartelli gialli, le auto blu, i ciclisti rossi; la rete è <b>stabile</b> da un frame all'altro, ma senza un vincolo temporale ci può essere <i>flickering</i> (un pixel che cambia classe da un frame all'altro).</li>
<li>Per il <b>tempo reale</b> servono circa 30 FPS (33 ms per frame); a 10 FPS, come il video, bastano 100 ms. Il nostro SegFormer-b0 su CPU è 10 volte sopra il budget a 10 FPS.</li>
</ul>
<div class="box k"><b>Da saper fare · domanda 5 del notebook</b><p>Riportare gli FPS a regime sul video: nel nostro caso <b>0,9 FPS su CPU a 2 core</b> (risoluzione 512×512 in ingresso). Il valore su GPU dipende dalla scheda: con una GPU moderna un SegFormer-b0 a 512×512 va ordini di grandezza più veloce. Il numero da citare è sempre accompagnato da <b>hardware e risoluzione</b>.</p></div>
""", img='img/nb_latenza.png', printed=NB + 'celle 52–53')

# ---------------------------------------------------------------- parte 4 istanze

s(23, "Mask R-CNN: segmentazione d'istanza reale", """
<pre>mask_model = torchvision.models.detection.maskrcnn_resnet50_fpn(weights="DEFAULT").to(device).eval()
inst_boxes, inst_labels, inst_scores, inst_masks = instance_segment(mask_model, sample_uint8)
person_keep = inst_labels == PERSON_COCO_ID
binary_masks = (inst_masks[person_keep] > 0.5).squeeze(1).bool()
drawn = draw_segmentation_masks(sample_uint8, binary_masks, alpha=0.6, colors=palette[:n])
# nostra uscita: Mask R-CNN finds 2 'person' instances (score > 0.8)</pre>
<ul>
<li><b>Mask R-CNN</b> (He et al. 2017) estende Faster R-CNN con un <b>terzo ramo</b> che predice una <b>maschera binaria per ogni box</b>. Per ogni proposta: <b>RoIAlign</b> ritaglia le feature in una griglia fissa (14×14), quattro convoluzioni 3×3 e una convoluzione trasposta le portano a <b>28×28</b>, e una conv 1×1 dà una maschera per classe (91).</li>
<li>Il modello restituisce per ogni detection una maschera <code>(1, H, W)</code> di probabilità in [0, 1] (già riportata alla risoluzione dell'immagine): la soglia 0,5 la rende binaria. Sulla nostra foto: 6 maschere totali, 4 sopra soglia 0,8 (2 person, 2 backpack), delle quali <b>2 persone</b>.</li>
<li>Le due persone sono la <b>ragazza</b> (rosso) e la <b>persona piccola</b> dietro i vetri (verde), che SegFormer non aveva visto: l'approccio con box è più sensibile agli oggetti piccoli perché la RPN guarda direttamente a quella scala.</li>
<li>Differenza con la semantica: <b>ogni istanza ha la sua maschera</b>, quindi si possono <b>contare</b> le persone e separare due persone che si toccano.</li>
</ul>
<div class="box w"><b>Attenzione: crash con più di 8 persone</b><p>La palette ha solo 8 colori e il codice usa <code>palette[:n_maskrcnn_people]</code>: se le persone sono più di 8 (per esempio sulla foto affollata, dove Mask R-CNN ne trova 9) <code>draw_segmentation_masks</code> lancia <code>ValueError: Number of colors must be equal or larger than the number of objects, but got 8 &lt; 9</code>. Lo abbiamo verificato. Correzione: <code>colors = (palette * ((n // 8) + 1))[:n]</code>.</p></div>
<div class="box b"><b>Dal libro · cap. 50, § 50.6 e Szeliski § 6.4.2</b><p>Il visionbook descrive la stessa idea: dopo che i box sono stati proposti e classificati, un <b>classificatore binario per pixel</b> dentro il box dice quali pixel appartengono all'oggetto (riferimento: Mask R-CNN); la loss è la somma di classificazione, localizzazione e segmentazione con pesi λ. Szeliski aggiunge che Mask R-CNN usa la stessa RPN di Faster R-CNN, che le loss dei rami vanno bilanciate e che è il lavoro che ha introdotto i termini <i>backbone</i> e <i>head</i>.</p></div>
""", sec=("l20-p4", "Parte 4 · Segmentazione d'istanza", 'schede 23–28'), img='img/nb_maskrcnn.png', printed=NB + 'celle 54–55')

s(24, "Panottica «fatta in casa»", """
<pre>panoptic = colored_mask.copy()                      # lo "stuff" (e le cose) da SegFormer
rng = np.random.default_rng(1)
for i in range(len(inst_masks)):
    binary_mask = (inst_masks[i, 0] > 0.5).numpy()
    panoptic[binary_mask] = rng.integers(40, 256, size=3, dtype=np.uint8)   # un colore casuale per istanza</pre>
<ul>
<li>La <b>segmentazione panottica</b> unisce le due viste: ogni pixel ha una classe (come nella semantica) e i pixel delle «<b>cose</b>» (<i>things</i>: persone, auto, biciclette) hanno anche un identificativo di istanza; lo «<b>stuff</b>» (strada, cielo, vegetazione) non ha istanze.</li>
<li>Modelli recenti (Panoptic FPN, Mask2Former) predicono tutto insieme in un unico spazio di etichette. Il notebook ne imita il risultato con <b>due modelli separati</b>: SegFormer (Cityscapes, 19 classi) per lo stuff e Mask R-CNN (COCO, 91 classi) per le istanze, sovrapposte con colori a caso.</li>
<li>Nell'immagine: strada viola, marciapiede rosa, edificio grigio da SegFormer; la ragazza gialla, lo zaino arancione, la persona lontana in rosa da Mask R-CNN.</li>
</ul>
<div class="box w"><b>Attenzione: non è una vera panottica</b><p>(1) La mappa di partenza (<code>colored_mask</code>) contiene già i pixel <i>person</i> di SegFormer, che non vengono tolti: restano visibili come <b>bordo rosso</b> attorno alla persona dove le due maschere non coincidono. (2) Il titolo dice «4 'thing' instances», ma sono 4 <b>istanze</b> qualunque: 2 persone e 2 zaini (<i>backpack</i> non è una classe di Cityscapes): l'etichetta dello zaino non ha nulla in comune con le 19 classi. (3) I due modelli hanno <b>spazi di classi diversi</b>: non c'è un'etichetta panottica coerente (id di classe + id di istanza per ogni pixel) né una regola per risolvere i conflitti (come in Panoptic FPN, dove un pixel contestato viene assegnato in base al punteggio). (4) I colori casuali non permettono di riconoscere la classe. Il risultato è utile per <b>vedere</b> il concetto, non per misurare una PQ.</p></div>
<div class="box b"><b>Dal libro · Szeliski § 6.4.3 (il visionbook non la tratta)</b><p>La panottica etichetta tutti gli oggetti correttamente segmentati e lo stuff rimanente; per misurarla serve una metrica che bilanci le due parti, la <b>panoptic quality (PQ)</b> di Kirillov et al. 2019. Szeliski cita il Panoptic Feature Pyramid Network, che aggiunge a una FPN due rami, istanza e semantica.</p></div>
""", img='img/nb_panoptic.png', printed=NB + 'celle 56–57')

s(25, "Componenti connesse da zero (TODO)", """
<pre>from collections import deque
def connected_components_from_scratch(binary_mask):
    mask = np.asarray(binary_mask).astype(bool)
    H, W = mask.shape
    labels = np.zeros((H, W), dtype=np.int32); n = 0
    for y in range(H):
        for x in range(W):
            if mask[y, x] and labels[y, x] == 0:          # pixel acceso e non ancora etichettato
                n += 1; labels[y, x] = n
                q = deque([(y, x)])
                while q:                                  # BFS sui vicini a 4
                    cy, cx = q.popleft()
                    for ny, nx in ((cy-1, cx), (cy+1, cx), (cy, cx-1), (cy, cx+1)):
                        if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and labels[ny, nx] == 0:
                            labels[ny, nx] = n; q.append((ny, nx))
    return labels, n
# nostra uscita: 20201 'person' pixels; from-scratch BFS: 1 components in 41.9 ms</pre>
<ul>
<li>Alternativa <b>non appresa</b> alla segmentazione d'istanza: dalla maschera <b>semantica</b> dei pixel «person» si cercano i <b>blob</b> separati con le <b>componenti connesse</b>. Due pixel sono nella stessa componente se si può passare dall'uno all'altro attraverso pixel acceso adiacenti (<b>4-connessione</b>: su, giù, sinistra, destra).</li>
<li>L'algoritmo è un classico da colloquio: scorrere l'immagine, e ogni volta che si trova un pixel acceso non ancora etichettato, <b>nuova etichetta</b> e <b>visita in ampiezza (BFS)</b> o in profondità che etichetta tutti i pixel raggiungibili. Costo <b>O(H·W)</b>: ogni pixel è inserito nella coda al massimo una volta.</li>
<li>Con una coda <code>deque</code> l'estrazione da sinistra è O(1); con una lista Python sarebbe O(n). Meglio non usare ricorsione (DFS ricorsiva) su immagini grandi: supererebbe il limite di profondità.</li>
<li>Sulla persona della foto: 20 201 pixel «person» formano <b>1 componente</b>, calcolata in 42 ms.</li>
</ul>
<div class="box x"><b>Approfondimento</b><p>OpenCV usa un algoritmo a <b>due passate con union-find</b> (etichetta provvisoria a ogni pixel in base ai vicini già visti, poi unisce le etichette equivalenti): evita la coda e ha migliore località di memoria. È il motivo per cui è 22 volte più veloce (scheda 26).</p></div>
""", img='img/nb_ccl.png', printed=NB + 'celle 58–59')

s(26, "Verifica con OpenCV e visualizzazione", """
<pre>n_components_cv2, label_map_cv2 = cv2.connectedComponents(person_mask.astype(np.uint8), connectivity=4)
n_components_cv2 -= 1                           # cv2 conta anche lo sfondo come componente 0
same_partition = partition_signature(label_map_scratch) == partition_signature(label_map_cv2)
# nostra uscita: from-scratch: 1 components, 41.9 ms; cv2: 1 components, 1.9 ms; identical partitions: True; cv2 ~22x più veloce</pre>
<ul>
<li>I numeri delle etichette possono differire fra le due implementazioni (l'ordine è arbitrario), quindi non si confrontano le mappe: si confrontano le <b>partizioni</b>, cioè gli insiemi di insiemi di pixel (<code>partition_signature</code> restituisce un <code>frozenset</code> di <code>frozenset</code>, indipendente dalla numerazione).</li>
<li><code>cv2.connectedComponents</code> restituisce <b>n + 1</b> componenti, perché lo sfondo è la componente 0: da qui <code>-= 1</code>. <code>connectivity=4</code> è indispensabile per confrontare con la nostra BFS a 4 vicini (OpenCV usa 8 per default).</li>
<li>Risultato: <b>stessa partizione</b>, 22 volte più veloce (1,9 ms contro 41,9 ms).</li>
<li>La figura successiva colora ogni componente con un colore a caso.</li>
</ul>
<div class="box w"><b>Attenzione: l'overlay scurisce tutta la foto</b><p>Il codice fa <code>instance_overlay = overlay_mask(sample_pil, instance_rgb, alpha=0.6)</code> con <code>instance_rgb</code> <b>nero</b> (0, 0, 0) per lo sfondo: la miscela alfa si applica a <b>tutti</b> i pixel e abbassa la luminosità dello sfondo al 40%: nella figura la foto è visibilmente scura. Correzione: miscelare solo dove l'etichetta è maggiore di 0, per esempio <code>out = img.copy(); m = label_map > 0; out[m] = ((1-α)*img[m] + α*instance_rgb[m]).astype(np.uint8)</code>.</p></div>
<div class="box x"><b>Approfondimento: 4 o 8 vicini?</b><p>Con 8-connessione due pixel in diagonale sono vicini. Il risultato può cambiare: due blob toccati solo per uno spigolo sono due componenti a 4 e una sola a 8. Figura nella dispensa.</p></div>
""", img='img/nb_ccl.png', printed=NB + 'celle 60–62')

s(27, "Confronto fra i due conteggi", """
<pre>print(f"Mask R-CNN (learned instance segmentation):  {n_maskrcnn_people} person instances")
print(f"Connected components (non-learned trick)): {n_components_scratch} person components")
# nostra uscita: Mask R-CNN 2 persone; componenti connesse 1</pre>
<ul>
<li>Sulla foto di esempio i conteggi <b>non coincidono</b>: Mask R-CNN trova <b>2 persone</b>, le componenti connesse <b>1</b>. La differenza qui non viene da persone che si toccano, ma dal fatto che SegFormer (a 512×512 e a 1/4 di risoluzione dei logit) <b>non ha segmentato la persona lontana</b>: non ci sono pixel «person» da raggruppare.</li>
<li>Sulla foto <b>affollata</b> (8 pedoni annotati) abbiamo misurato: Mask R-CNN 9 persone (8 più una in più), SegFormer + componenti connesse 7 componenti, di cui 5 con più di 200 pixel. Alcune persone vicine <b>si fondono in un blocco</b> (il blob più grande ha 32 610 pixel, il secondo 15 452). Vedi la dispensa, sezione 10.</li>
<li>Il confronto illustra la differenza concettuale: la <b>semantica</b> non conta le istanze (nel visionbook, § 50.5.1: «non può separare due istanze della stessa classe a contatto»); l'<b>istanza</b> sì.</li>
</ul>
<div class="box k"><b>Da saper fare · domanda della cella 65</b><p>Quando le componenti connesse sbagliano il conteggio: (1) <b>persone che si toccano o si sovrappongono</b> (un gruppo di persone diventa un solo blob: conteggio <b>per difetto</b>); (2) una <b>persona spezzata</b> da un occlusore (palo, auto) in due blob: conteggio <b>per eccesso</b>; (3) piccoli blob di errore della segmentazione (rumore) contati come persone. Mask R-CNN non ha questo problema perché parte da <b>box separati</b> proposti dalla RPN, uno per ogni oggetto, e la maschera è predetta <b>dentro ciascun box</b> con RoIAlign: due persone vicine hanno due proposte e due maschere, anche se i box si sovrappongono (e con la NMS al 0,5 non si cancellano se l'IoU è minore).</p></div>
""", img='img/nb_affollata_istanze.png', printed=NB + 'celle 63–65')

s(28, "Domande ed esercizi finali", """
<p>Il notebook chiude con <b>6 domande</b> e <b>4 esercizi</b> (celle 66–67, quest'ultima vuota). Le risposte con i nostri numeri sono nella sezione <a href="#l20-soluzioni">Soluzioni</a>; qui l'elenco.</p>
<ul>
<li><b>Domanda 1</b> – soglia NMS: come variano conteggio e falsi positivi/negativi? (scheda 8: 4, 5, 5, 9, 40 box.)</li>
<li><b>Domanda 2</b> – NMS da zero contro torchvision: stesso insieme? speedup? (scheda 9: sì, 16×.)</li>
<li><b>Domanda 3</b> – SegFormer: dove sbaglia e quali classi sono più difficili? (schede 15–16.)</li>
<li><b>Domanda 4</b> – il modello solo sintetico: cosa peggiora? (schede 17–18.)</li>
<li><b>Domanda 5</b> – FPS a regime sul video. (scheda 22: 0,9 su CPU.)</li>
<li><b>Domanda 6</b> – Mask R-CNN contro componenti connesse: coincidono? (scheda 27.)</li>
<li><b>Esercizio 1</b> – stessi modelli su un altro dataset di detection. <b>Esercizio 2</b> – benchmark di altri approcci visti a lezione, per accuratezza e velocità. <b>Esercizio 3</b> – cambiare il checkpoint di SegFormer con <code>nvidia/segformer-b0-finetuned-ade-512-512</code> (150 classi ADE20K). <b>Esercizio 4</b> – il checkpoint GTA5 su un'altra foto reale.</li>
</ul>
<div class="box w"><b>Attenzione: cella finale vuota e piccoli refusi</b><p>La cella 67 è un blocco di codice vuoto. Nel testo: «becnhmark» (cella 66, esercizi), la doppia parentesi in «non-learned trick))» (cella 64), «Fine-tuned on real Cityscapes photos)» (cella 40).</p></div>
""", printed=NB + 'celle 66–67')
