NB = 'NOTEBOOK lab_obj_det_seg.ipynb · '
V50 = '<a href="https://visionbook.mit.edu/object_recognition_v3.html">visionbook.mit.edu · cap. 50</a>'

# ---------------------------------------------------------------- setup e dati

s(1, "Obiettivi e setup", """
<p>Il notebook non addestra nulla: usa <b>pesi preaddestrati</b> per far girare detector e segmentatori in sola inferenza, scrive a mano i pezzi classici (<b>NMS</b>, <b>IoU</b>, <b>componenti connesse</b>) e li confronta con le versioni delle librerie, poi mette tutto su un video reale. È il laboratorio della parte di riconoscimento della <a href="#L17">L17</a>.</p>
<ul>
<li><b>Parte 1</b> – detection con un <b>Faster R-CNN</b> preaddestrato su COCO; <b>NMS</b> da zero confrontata con <code>torchvision.ops.nms</code>; Soft-NMS; DETR (detection come predizione di un insieme, senza NMS); confronto fra quattro famiglie di detector.</li>
<li><b>Parte 2</b> – segmentazione semantica con <b>SegFormer</b>: pipeline di inferenza scritta a mano, overlay sull'immagine, il <b>domain gap</b> fra un modello addestrato su immagini sintetiche (GTA5) e uno su foto reali (Cityscapes).</li>
<li><b>Parte 3</b> – SegFormer frame per frame su un video di guida.</li>
<li><b>Parte 4</b> – segmentazione d'istanza con <b>Mask R-CNN</b>, una panottica «fatta in casa» e le <b>componenti connesse</b> scritte da zero.</li>
</ul>
<pre>pip install transformers opencv-python-headless ultralytics timm
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# nostra uscita: Using device: cpu</pre>
<ul>
<li>Il notebook sceglie da solo GPU o CPU. Noi lo abbiamo eseguito su <b>CPU</b> (2 core, PyTorch 2.15, torchvision 0.29, transformers 5.22): le <b>latenze</b> sono molto più alte di quelle che si leggono su GPU (un Faster R-CNN impiega circa 2,3 s a immagine), ma conteggi e immagini sono gli stessi.</li>
<li>Servono quattro pacchetti oltre a PyTorch: <code>transformers</code> (SegFormer, DETR), <code>opencv-python-headless</code> (overlay, video, componenti connesse), <code>ultralytics</code> (YOLOv8) e <code>timm</code>. I pesi si scaricano la prima volta (Faster R-CNN 160 MB, Mask R-CNN 170 MB, YOLOv8n 6 MB, DETR e SegFormer da Hugging Face).</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Distinguere i quattro compiti del lab: <b>detection</b> (box + classe per ogni oggetto), <b>segmentazione semantica</b> (una classe per pixel, niente istanze), <b>segmentazione d'istanza</b> (una maschera per oggetto), <b>panottica</b> (tutti i pixel etichettati e le «cose» separate in istanze). La figura della dispensa (sezione 1) li mette a confronto.</p></div>
""", sec=("l20-p1", "Parte 1 · Object detection", 'schede 1–12'), printed=NB + 'celle 1–3')

s(2, "Le foto di esempio: Penn-Fudan", """
<pre>DATA_ROOT = "./data/PennFudanPed"
# scarica PennFudanPed.zip da cis.upenn.edu se la cartella non c'è
image_files = sorted(os.listdir(IMG_DIR))   # 170 immagini
sample_pil, sample_uint8 = load_sample(12)  # PIL RGB + tensore uint8 (3, H, W)
plt.title(f"{image_files[0]}: {sample_pil.size[0]}x{sample_pil.size[1]}")</pre>
<ul>
<li><b>Penn-Fudan Pedestrian</b> è un piccolo dataset di foto reali di strada e campus con persone, usato qui solo come fonte comoda di immagini. Contiene anche le <b>maschere di istanza</b> dei pedoni (cartella <code>PedMasks</code>), che servono nella cella 15 per contare i pedoni veri.</li>
<li><code>read_image(path)[:3]</code> legge un tensore <b>uint8 di forma (C, H, W)</b> e scarta l'eventuale canale alpha; <code>Image.fromarray(img.permute(1, 2, 0).numpy())</code> lo riporta a una immagine PIL (H, W, C), il formato che vogliono i processori di Hugging Face.</li>
<li>Due rappresentazioni dello stesso dato: i detector di torchvision vogliono un <b>tensore float in [0, 1]</b> (si divide per 255), quelli di Hugging Face una <b>immagine PIL</b>.</li>
<li>L'immagine 12 è <code>FudanPed00013.png</code>, 652×498 pixel: una ragazza che attraversa il piazzale davanti a un edificio, con uno zaino; <b>un solo pedone</b> annotato (ma c'è una seconda persona, piccola e lontana, dietro le porte a vetri: la ritroveremo).</li>
</ul>
<div class="box w"><b>Attenzione: il titolo della figura è sbagliato</b><p>Il titolo usa <code>image_files[0]</code>, cioè <code>FudanPed00001.png</code>, mentre l'immagine mostrata è la numero 12 (<code>FudanPed00013.png</code>). Correzione: <code>image_files[12]</code>.</p></div>
<div class="box x"><b>Dataset non scaricabile?</b><p>Il sito dell'università di Pennsylvania ha dato a noi un errore di certificato SSL (la <code>urlretrieve</code> fallisce). Il file <code>PennFudanPed.zip</code> è reperibile anche sul mirror Hugging Face <code>jiaxiaolei/Penn-Fudan</code>; basta metterlo in <code>./data/</code> e il notebook lo estrae da solo.</p></div>
""", img='img/nb_penn.png', printed=NB + 'celle 4–5')

s(3, "Faster R-CNN preaddestrato", """
<pre>detector = torchvision.models.detection.fasterrcnn_resnet50_fpn(weights="DEFAULT")
detector = detector.to(device).eval()
detector.rpn.anchor_generator.sizes          # ((32,), (64,), (128,), (256,), (512,))
detector.rpn.anchor_generator.aspect_ratios  # (0.5, 1.0, 2.0) per ogni livello

@torch.no_grad()
def detect(model, img_uint8, score_thresh=0.8):
    pred = model([img_uint8.float() / 255.0])[0]
    keep = pred["scores"] > score_thresh
    return pred["boxes"][keep], pred["labels"][keep], pred["scores"][keep]</pre>
<ul>
<li><b>Faster R-CNN</b> è un detector <b>a due stadi</b>. Nel primo la <b>RPN</b> (<i>Region Proposal Network</i>) guarda le feature della rete e propone regioni «dove potrebbe esserci qualcosa»; nel secondo ogni proposta viene ritagliata dalle feature, classificata (91 classi COCO, di cui 80 usate) e il suo box viene raffinato.</li>
<li>Il backbone è un <b>ResNet-50 con FPN</b> (<i>Feature Pyramid Network</i>): 5 mappe a risoluzioni diverse, tutte con 256 canali. Il codice legge dal modello la lista dei <b>generatori di anchor</b>: una sola <b>area</b> per livello (32², 64², 128², 256², 512²) e tre <b>rapporti d'aspetto</b> h/w = 0,5, 1, 2. Sono <b>15 anchor</b> per posizione (5 livelli × 3 forme, tre per livello).</li>
<li><code>detect</code>: il modello vuole una <b>lista di tensori float</b> (uno per immagine, valori in [0, 1]) e restituisce una lista di dizionari con <code>boxes</code> (formato <b>xyxy</b>, in pixel dell'immagine originale), <code>labels</code> (id COCO), <code>scores</code>. Si tengono solo le detection con punteggio maggiore di 0,8.</li>
<li>Risultato sulla foto di esempio: <b>4 detection</b> a soglia 0,8. Nell'ordine: person 1,00 (la ragazza), person 0,97 (la persona piccola dietro i vetri), backpack 0,89 e backpack 0,82 (lo zaino, due volte).</li>
<li>Gli id delle classi sono quelli «a buchi» di COCO (91 numeri per 80 classi vere): per leggerli si usa <code>weights.meta["categories"]</code>, qui <code>COCO_CLASSES</code>; l'indice 0 è lo sfondo.</li>
</ul>
<div class="box b"><b>Dal libro · Szeliski § 6.3.3; visionbook § 50.4.1</b><p>Il visionbook descrive lo schema generale dei detector con tre passi: (1) proporre candidati, (2) classificare ciascuno, (3) rimuovere i duplicati. Faster R-CNN è esattamente questo schema, con la particolarità che la proposta (RPN) è una rete che condivide il backbone con il classificatore. Szeliski descrive R-CNN (selective search, circa 2000 proposte), Fast R-CNN (feature condivise e teste FC) e Faster R-CNN (la RPN al posto di selective search, con <i>anchor box</i> a ogni posizione grossolana e NMS finale).</p></div>
""", img='img/nb_frcnn.png', printed=NB + 'celle 6–7')

s(4, "Dalle anchor alle proposte alle detection", """
<pre>images, _ = detector.transform([img], None)            # ridimensiona (lato corto 800) e raggruppa
features = detector.backbone(images.tensors)           # dict di 5 mappe FPN
anchors = detector.rpn.anchor_generator(images, list(features.values()))[0]
proposals, _ = detector.rpn(images, features)          # dopo l'NMS della RPN
predictions = detector([img])[0]                       # detection finali
# nostra uscita:
# Total original anchors: 211038
# RPN proposals after RPN NMS: 1000
# Final detections above 0.8: 4</pre>
<ul>
<li>La cella percorre la pipeline a pezzi. <code>detector.transform</code> riporta l'immagine a 800 pixel di lato corto (e la normalizza): la nostra foto 498×652 diventa 800×1047, poi riempita fino a 800×1056 (multiplo di 32).</li>
<li><b>Anchor</b>: 211 038 box fissi, tutti i livelli. Si contano così: i cinque livelli hanno 200×264, 100×132, 50×66, 25×33 e 13×17 posizioni (stride 4, 8, 16, 32, 64) cioè 70 346 posizioni, per <b>3 forme</b> = 211 038. Dipendono solo dalla <b>dimensione</b> dell'immagine, non dal suo <b>contenuto</b>.</li>
<li><b>Proposte</b>: la RPN dà a ogni anchor un punteggio di <i>objectness</i> e uno spostamento (<i>offset</i>) del box; tiene le migliori e applica una <b>prima NMS</b> con soglia 0,7, lasciando <b>1000 proposte</b> (il valore predefinito in test).</li>
<li><b>Detection finali</b>: la testa classifica ogni proposta e raffina il box; segue una <b>seconda NMS</b> (soglia 0,5, per classe) e il taglio sul punteggio. Dai 211 038 anchor ai 4 box finali.</li>
<li>La funzione <code>to_original_coords</code> riporta i box dalle coordinate dell'immagine ridimensionata (800×1056) a quelle originali, scalando x e y separatamente, e <code>valid_boxes</code> scarta i box degenerati dopo il clipping.</li>
</ul>
<div class="box w"><b>Attenzione: la figura sulle anchor mostra un campione, non «le anchor»</b><p>La cella disegna 150 anchor <b>campionate a caso</b> fra 211 038 (con <code>linspace</code> sugli indici): la maggior parte viene dal livello più fine (52 800 anchor su 70 346 posizioni), per cui si vedono soprattutto box piccoli. Non è un difetto, ma la figura non dice «le anchor sono sparse a caso»: dice che coprono tutta l'immagine con forme e dimensioni fisse.</p></div>
<div class="box k"><b>Da saper fare</b><p>Spiegare i tre stadi del grafico: <b>blu</b> (anchor, indipendenti dall'immagine), <b>arancione</b> (proposte, anchor spostate e filtrate dalla RPN: si addensano sulla persona e sui bordi dell'edificio), <b>rosso</b> (detection finali: 4 box etichettati). Calcolare il numero di anchor da dimensioni e stride.</p></div>
""", img='img/nb_stadi.png', printed=NB + 'celle 8–9')

s(5, "I box grezzi prima della NMS", """
<pre>@torch.no_grad()
def predict_raw_boxes(model, img_uint8, score_thresh=0.3):
    old_nms, old_score = model.roi_heads.nms_thresh, model.roi_heads.score_thresh
    model.roi_heads.nms_thresh = 1.0         # IoU > 1.0 non succede mai: nessun box soppresso
    model.roi_heads.score_thresh = score_thresh
    pred = model([img_uint8.float() / 255.0])[0]
    model.roi_heads.nms_thresh, model.roi_heads.score_thresh = old_nms, old_score
    return pred["boxes"], pred["labels"], pred["scores"]
raw_score_threshs = [0.9, 0.5, 0.3, 0.1]
# nostre uscite: 29, 82, 100, 100 box grezzi</pre>
<ul>
<li>Per applicare la <b>nostra</b> NMS servono i candidati <b>prima</b> della soppressione della testa. Trucco: porre <code>nms_thresh = 1.0</code>. La NMS di torchvision toglie i box con IoU <b>maggiore</b> della soglia; l'IoU non supera mai 1, quindi con 1,0 non toglie nulla. Si ripristinano poi i valori originali.</li>
<li><code>score_thresh</code> controlla quanti candidati sopravvivono: più è basso, più box a bassa confidenza restano (soglie 0,9 / 0,5 / 0,3 / 0,1 danno 29 / 82 / <b>100</b> / <b>100</b> box).</li>
<li>La <b>NMS della RPN</b> resta attiva: i candidati vengono comunque da 1000 proposte già filtrate.</li>
<li>Nella figura, 29 box a soglia 0,9: già quasi tutti sovrapposti sullo stesso pedone (e sul piccolo pedone dietro i vetri); a soglia più bassa si aggiungono box sul torso/zaino.</li>
</ul>
<div class="box w"><b>Attenzione: il conteggio satura a 100</b><p>Il commento della cella lo accenna (<code>detections_per_img</code>, per default 100), ma il testo markdown no: con soglia 0,3 e con 0,1 il numero è identico, 100, perché il modello restituisce <b>al massimo 100 box</b> per immagine, ordinati per punteggio. Per vedere davvero come cresce il numero di candidati abbassando la soglia, va alzato <code>model.roi_heads.detections_per_img</code> (per esempio a 300, la riga è già nel codice, commentata).</p></div>
""", img='img/nb_raw_soglie.png', printed=NB + 'celle 10–13')

s(6, "Una foto affollata e una con più classi", """
<pre>mask_files = sorted(os.listdir(mask_dir))
instance_counts = [len(np.unique(np.array(Image.open(os.path.join(mask_dir, mf))))) - 1
                   for mf in mask_files]           # -1: l'id 0 è lo sfondo
crowded_idx = int(np.argmax(instance_counts))      # FudanPed00058.png, 8 pedoni annotati
# per ogni immagine: box grezzi (arancio) e dopo la NMS di torchvision (rosso)</pre>
<ul>
<li>Cerca nel dataset l'immagine con più <b>pedoni veri</b>: ogni pedone ha una maschera con un id diverso (0 = sfondo), quindi il numero di istanze è il numero di valori distinti meno uno. Risultato: <b>FudanPed00058.png con 8 pedoni</b>.</li>
<li>Come seconda immagine, una foto <b>COCO</b> (<code>000000039769.jpg</code>: due gatti e due telecomandi su un divano rosa) per avere più classi.</li>
<li>Per ciascuna si confrontano i box <b>grezzi</b> (riga sopra) e quelli dopo la NMS interna di torchvision (riga sotto, con score 0,8): foto affollata 100 box grezzi → <b>12</b> detection (persone, ma anche una borsa e un'auto); COCO 97 → <b>3</b> detection a soglia 0,8 (due gatti e un telecomando; il secondo telecomando ha punteggio minore e si recupera con soglia 0,7, cella 46).</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Leggere questa figura: i box grezzi si <b>addensano</b> attorno a ogni oggetto vero (decine di box quasi uguali), perché il detector risponde in modo simile a posizioni vicine. Un detector senza NMS stamperebbe un oggetto cento volte. L'NMS riduce un «mucchio» di box a <b>un box per oggetto</b>.</p></div>
""", img='img/nb_affollata_coco.png', printed=NB + 'celle 14–15')

s(7, "IoU e NMS da zero", """
<p>Il notebook propone due TODO: <code>box_iou_manual</code> e <code>nms_from_scratch</code>. Ecco una soluzione, verificata contro torchvision.</p>
<pre>def box_iou_manual(boxes1, boxes2):
    area1 = (boxes1[:, 2] - boxes1[:, 0]) * (boxes1[:, 3] - boxes1[:, 1])
    area2 = (boxes2[:, 2] - boxes2[:, 0]) * (boxes2[:, 3] - boxes2[:, 1])
    lt = torch.maximum(boxes1[:, None, :2], boxes2[None, :, :2])   # angolo alto-sinistra dell'intersezione
    rb = torch.minimum(boxes1[:, None, 2:], boxes2[None, :, 2:])   # angolo basso-destra
    wh = (rb - lt).clamp(min=0)                                    # larghezza e altezza, 0 se disgiunti
    inter = wh[..., 0] * wh[..., 1]
    return inter / (area1[:, None] + area2[None, :] - inter)       # (N, M)

def nms_from_scratch(boxes, scores, iou_threshold):
    order = scores.argsort(descending=True)
    keep = []
    while order.numel() > 0:
        i = order[0]; keep.append(i.item())                        # il migliore si tiene
        if order.numel() == 1: break
        ious = box_iou_manual(boxes[i:i+1], boxes[order[1:]])[0]
        order = order[1:][ious <= iou_threshold]                   # via chi ha IoU > soglia
    return torch.tensor(keep, dtype=torch.long)</pre>
<ul>
<li><b>IoU</b> (<i>intersection over union</i>) = area dell'intersezione divisa per area dell'unione = <span class="f">IoU = |A ∩ B| / (|A| + |B| − |A ∩ B|)</span>. Vale 0 per box disgiunti, 1 per box identici. Con il broadcasting <code>[:, None]</code> contro <code>[None, :]</code> si calcolano <b>tutte le coppie</b> in una volta (matrice N×M).</li>
<li><b>NMS greedy</b> (<i>non-maximum suppression</i>): ordina per punteggio, tieni il migliore, scarta tutti quelli con IoU <b>maggiore</b> della soglia τ con lui, ripeti sui rimasti.</li>
<li>Verifica del notebook: differenza massima fra il nostro IoU e <code>box_iou</code> di torchvision = <b>0,0</b> (identici); su un esempio giocattolo (3 box) la nostra NMS tiene lo stesso insieme di <code>torchvision.ops.nms</code>.</li>
<li>Dettaglio di confine: il test è <code>ious &lt;= iou_threshold</code> per <b>tenere</b>, cioè si scarta solo se l'IoU è strettamente maggiore; è la convenzione di torchvision.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 50, § 50.4.1.2 (visionbook) e Szeliski § 6.3.3</b><p>Il visionbook descrive l'NMS in tre passi: prendi il box a confidenza massima e mettilo nell'insieme finale; togli dall'insieme di partenza il box scelto e tutti quelli con IoU sopra una soglia; ripeti finché è vuoto. Szeliski la chiama «greedy most-confident-first». È lo stesso algoritmo del codice sopra.</p></div>
""", printed=NB + 'celle 16–17')

s(8, "NMS per classe e variazione della soglia", """
<pre>def nms_per_class(boxes, labels, scores, iou_threshold):
    keep_all = []
    for c in labels.unique():
        idx = (labels == c).nonzero(as_tuple=True)[0]
        keep_c = nms_from_scratch(boxes[idx], scores[idx], iou_threshold)
        keep_all.append(idx[keep_c])
    return torch.cat(keep_all)
thresholds = [0.1, 0.3, 0.5, 0.7, 0.9]
# nostra uscita su raw_boxes: 4, 5, 5, 9, 40 box tenuti</pre>
<ul>
<li>La NMS si applica <b>una classe alla volta</b>: un box «backpack» non deve sopprimere un box «person» solo perché si sovrappongono (lo zaino sta <b>dentro</b> la persona: IoU piccolo ma presente). Si usano gli indici di ogni classe e poi si torna agli indici globali con <code>idx[keep_c]</code>.</li>
<li>Con 100 box grezzi sulla foto di esempio il numero di box finali al variare di τ: <b>4 (0,1), 5 (0,3), 5 (0,5), 9 (0,7), 40 (0,9)</b>. Con τ piccolo si toglie molto, anche box giusti; con τ grande si tiene quasi tutto (per τ = 0,9 la NMS «quasi non agisce»).</li>
<li>Compromesso: <b>τ basso</b> → pochi duplicati, ma due oggetti vicini rischiano di fondersi in uno (falsi negativi); <b>τ alto</b> → molti duplicati (falsi positivi) ma si salvano oggetti molto vicini.</li>
<li>Con 5 box a τ = 0,3 e 0,5 sulla foto: person, person lontana, backpack, handbag e una seconda backpack. Il valore tipico dei detector è <b>τ = 0,5</b> (quello della testa di Faster R-CNN).</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Rispondere alla domanda 1 del notebook (soglia della NMS) con i numeri: da τ = 0,7 a 0,9 i box salgono da 9 a 40, quasi tutti falsi positivi sovrapposti; da τ = 0,5 a 0,1 il conteggio cambia di uno. Il punto di funzionamento sensato è τ = 0,3–0,5 per foto con pochi oggetti vicini; in una folla serve di più o un'altra tecnica (scheda 10).</p></div>
""", img='img/nb_nms_tau.png', printed=NB + 'celle 18–19')

s(9, "Confronto con torchvision e domande", """
<pre>bench_boxes = torch.rand(3000, 2) * 900          # 3000 box casuali
keep_scratch = nms_from_scratch(bench_boxes, bench_scores, 0.5)
keep_torch = nms(bench_boxes, bench_scores, 0.5)
# nostra uscita: ours keeps 2664 boxes, torchvision keeps 2664 boxes, same set: True
# ours: 327.80 ms/call   torchvision.ops.nms: 20.56 ms/call   -> circa 16x più veloce</pre>
<ul>
<li><b>Correttezza</b>: su 3000 box casuali le due NMS tengono lo <b>stesso insieme</b> di 2664 box.</li>
<li><b>Velocità</b>: la nostra impiega 328 ms, quella di torchvision 21 ms: circa <b>16 volte</b> più veloce (il rapporto è stampato dalla cella; dipende dalla macchina e dall'implementazione dei TODO). Torchvision usa codice C++ compilato e calcola tutto in blocco, senza il ciclo Python per ogni box tenuto.</li>
<li>Il costo: nel caso peggiore (nessun box soppresso) la NMS greedy confronta ogni box con tutti gli altri, <b>O(N²)</b> IoU; in pratica meno, perché a ogni iterazione l'insieme si riduce.</li>
</ul>
<div class="box k"><b>Da saper fare · le due domande della cella 22</b><p><b>Perché per classe?</b> Un box «cane» e uno «persona» che si sovrappongono sono entrambi corretti (la persona porta il cane in braccio). Una NMS globale sopprimerebbe il box a punteggio minore anche se è di un'altra classe. Per questo la NMS si fa per classe (nelle librerie, con il trucco di sommare un offset di classe ai box).<br><b>Fallimento nella folla</b>: due persone vicine hanno box che si sovrappongono molto (IoU 0,5–0,7). La NMS greedy tiene la più sicura e <b>cancella l'altra</b> perché l'IoU supera τ: il detector «perde» una persona anche se l'aveva vista. Rimedi: <b>Soft-NMS</b> (non cancella, abbassa il punteggio), soglie adattive, oppure un detector che non usa NMS come <b>DETR</b> (predizione di insieme con matching uno-a-uno).</p></div>
""", printed=NB + 'celle 20–22')

s(10, "Soft-NMS (esercizio facoltativo)", """
<pre>def soft_nms_from_scratch(boxes, scores, iou_threshold=0.3, score_thresh=0.05):
    boxes, scores = boxes.clone(), scores.clone()
    kept_b, kept_s = [], []
    while len(scores) > 0:
        i = scores.argmax()
        kept_b.append(boxes[i]); kept_s.append(scores[i])        # il migliore si tiene
        mask = torch.ones(len(scores), dtype=torch.bool); mask[i] = False
        top = boxes[i:i+1]; boxes, scores = boxes[mask], scores[mask]
        if len(scores) == 0: break
        iou = box_iou_manual(top, boxes)[0]
        scores = torch.where(iou > iou_threshold, scores * (1 - iou), scores)   # decadimento lineare
        ok = scores >= score_thresh
        boxes, scores = boxes[ok], scores[ok]
    return torch.stack(kept_b), torch.stack(kept_s)
# nostra uscita: hard NMS (0.3): 4 box tenuti; soft NMS (0.3): 8 box, punteggi da 0,07 a 1,00</pre>
<ul>
<li>Idea (Bodla et al. 2017): invece di <b>cancellare</b> un box che si sovrappone a uno migliore, ne <b>riduce il punteggio</b>: s ← s · (1 − IoU). Più si sovrappone, più perde; se la sovrapposizione è piccola, il punteggio quasi non cambia. I box non spariscono finché il punteggio non scende sotto una soglia minima (0,05).</li>
<li>Vantaggio: in una folla il secondo pedone sopravvive con un punteggio ridotto invece di sparire. Svantaggio: dopo il Soft-NMS restano <b>più box</b> (qui 8 contro 4 della NMS dura): serve comunque una soglia finale sul punteggio.</li>
<li>La versione lineare originale applica il decadimento solo ai box con IoU <b>maggiore della soglia</b> (come sopra); esiste anche la versione gaussiana, s ← s · exp(−IoU²/σ).</li>
</ul>
<div class="box w"><b>Attenzione: la descrizione del notebook è un po' ambigua</b><p>La cella 23 scrive «s<sub>i</sub> ← s<sub>i</sub> · (1 − IoU)» per tutti i box; con la soglia <code>iou_threshold</code> in firma, la versione di riferimento applica il decadimento solo se IoU supera la soglia. Le due varianti differiscono poco, ma conviene saperlo. Nel notebook la funzione è chiamata senza separare le classi: su box di classi diverse il Soft-NMS va comunque applicato per classe.</p></div>
""", printed=NB + 'celle 23–24')

s(11, "DETR: detection senza NMS", """
<pre>from transformers import DetrImageProcessor, DetrForObjectDetection
detr_model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50").to(device).eval()
inputs = processor(images=pil_image, return_tensors="pt")
outputs = model(**inputs)                           # logits (1, 100, 92), pred_boxes (1, 100, 4)
result = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.8)[0]
# nostra uscita: 4 DETR detections: backpack 0,91 · handbag 0,87 · person 0,96 · person 1,00</pre>
<ul>
<li><b>DETR</b> (<i>DEtection TRansformer</i>, Carion et al. 2020) vede la detection come <b>predizione di un insieme</b>: un backbone ResNet-50 produce feature, un <b>transformer encoder-decoder</b> riceve <b>100 query</b> (vettori appresi) e ognuna produce <b>un box e una classe</b> (91 classi più «nessun oggetto»: 92 logit).</li>
<li>In training un <b>accoppiamento uno-a-uno</b> (algoritmo ungherese) lega ogni oggetto vero a una sola query; le altre query imparano «nessun oggetto». Quindi <b>non ci sono duplicati da togliere</b>: niente NMS, niente anchor.</li>
<li>Nel nostro esempio 95 delle 100 query dicono «nessun oggetto» con probabilità maggiore di 0,5; rimangono 4 box: le due persone, lo zaino (backpack, 0,91) e una borsa (handbag, 0,87) sullo stesso oggetto: sulla stessa zona DETR ha dato <b>due classi diverse</b> (Faster R-CNN dava due backpack).</li>
<li>Il post-processing è solo: softmax sulle classi, scarta «nessun oggetto», soglia sul punteggio, converte i box da (cx, cy, w, h) normalizzati a xyxy in pixel.</li>
</ul>
<div class="box b"><b>Dal libro · Szeliski § 6.3.3</b><p>Szeliski descrive DETR come architettura più semplice, che «elimina l'uso della non-maximum suppression e della generazione di anchor»: N predizioni (alcune con classe «no object»), ground truth completato con «no object» fino a N, <b>bipartite matching</b> a costo minimo e loss data dalla somma delle loss sulle coppie. Il visionbook non tratta DETR.</p></div>
<div class="box x"><b>Approfondimento</b><p>Il costo dell'accoppiamento si calcola con una matrice (query × oggetti) di costi (classe sbagliata + distanza fra box + IoU) e <code>scipy.optimize.linear_sum_assignment</code>; DETR addestra lentamente (centinaia di epoche) e va peggio sugli oggetti piccoli; le varianti successive (Deformable DETR) risolvono entrambi i problemi.</p></div>
""", img='img/nb_detr.png', printed=NB + 'celle 25–26')

s(12, "Detector shootout: quattro famiglie", """
<pre>shootout = []   # (nome, latenza ms, n. detection, parametri in milioni)
# Faster R-CNN (due stadi, anchor)  | FCOS (uno stadio, senza anchor)
# YOLOv8n (uno stadio, senza anchor) | DETR (predizione di insieme, senza NMS)
t, out = time_call(lambda: detect(detector, sample_uint8))     # 1 chiamata di riscaldamento + 3 misure
# nostra uscita (CPU):
# Faster R-CNN   41.8M params  2299.5 ms  4 detections
# FCOS           32.3M params  2028.6 ms  1 detections
# YOLOv8n         3.2M params    95.3 ms  2 detections
# DETR           41.5M params  1910.5 ms  4 detections</pre>
<ul>
<li><b>Faster R-CNN</b>: due stadi, proposte da anchor, la più accurata fra le «classiche» ma la più pesante. <b>FCOS</b>: un solo stadio, <b>senza anchor</b>, predice per ogni posizione la distanza dai quattro lati del box. <b>YOLOv8n</b>: un solo stadio, la versione più piccola (3,2 M di parametri, 95 ms su CPU). <b>DETR</b>: nessuna NMS.</li>
<li>La funzione <code>time_call</code> fa una <b>chiamata di riscaldamento</b> (la prima è lenta per compilazioni e cache) e poi la media su 3. Su GPU usa anche <code>torch.cuda.synchronize()</code>, perché le chiamate CUDA sono asincrone: senza sincronizzare si misurerebbe solo il lancio dei kernel.</li>
<li>Le latenze dei tre modelli «grandi» sono circa 2 secondi su CPU a 2 core: sono confrontabili fra loro (41,8 / 32,3 / 41,5 M di parametri) ma <b>YOLOv8n è 20 volte più veloce</b>, con 13 volte meno parametri.</li>
<li>Numero di detection: 4 / 1 / 2 / 4 con la stessa soglia 0,8 per tutti.</li>
</ul>
<div class="box w"><b>Attenzione: il confronto sul «numero di detection» non è equo, e c'è una contraddizione nel markdown</b><p>(1) Il markdown della cella 27 dice YOLOv8n «one-stage, <b>anchor-based</b>», il codice nel grafico dice «anchor-free»: la seconda è giusta (da YOLOv8 in poi la testa è senza anchor). (2) I punteggi dei vari modelli non sono calibrati allo stesso modo: FCOS, con la stessa soglia 0,8, trova <b>una sola persona</b> perché i suoi punteggi (sigmoide con focal loss) sono più bassi; sulla stessa foto la sua seconda detection ha punteggio 0,65. Per un confronto di accuratezza serve una metrica come l'<b>AP</b> su un dataset annotato, non il conteggio a soglia fissa. (3) Le latenze includono pre- e post-processing diversi (YOLO fa il resize e la NMS dentro la chiamata).</p></div>
""", img='img/nb_shootout.png', printed=NB + 'celle 27–28')
