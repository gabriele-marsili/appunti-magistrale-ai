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
<li>Nel nostro esempio 95 delle 100 query dicono «nessun oggetto» con probabilità maggiore di 0,5; rimangono 4 box: le due persone, uno zaino (backpack, 0,91) e una borsa (handbag, 0,87) nella zona dello zaino: DETR dà qui <b>due classi diverse</b> dove Faster R-CNN dava due box backpack.</li>
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

# ---------------------------------------------------------------- parte 2 segmentazione semantica

s(13, "SegFormer: caricare il modello", """
<pre>from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation
SEG_CHECKPOINT = "nvidia/segformer-b0-finetuned-cityscapes-1024-1024"
seg_processor = SegformerImageProcessor.from_pretrained(SEG_CHECKPOINT)
seg_model = SegformerForSemanticSegmentation.from_pretrained(SEG_CHECKPOINT).to(device).eval()
print("Number of classes:", seg_model.config.num_labels)      # 19</pre>
<ul>
<li><b>SegFormer</b> (Xie et al. 2021) è un modello di segmentazione semantica con un <b>encoder transformer gerarchico</b> (Mix Transformer: quattro stadi a risoluzioni 1/4, 1/8, 1/16, 1/32 dell'ingresso, con attenzione a riduzione spaziale) e un <b>decoder leggero formato solo da MLP</b> («all-MLP»), molto più economico dell'ASPP di DeepLabv3+ a parità di mIoU.</li>
<li>La versione <b>b0</b> è la più piccola: 3,7 milioni di parametri (stadi con 32, 64, 160 e 256 canali, 2 blocchi ciascuno; decoder a 256 canali).</li>
<li>Il checkpoint è addestrato (<i>fine-tuned</i>) su <b>Cityscapes</b>: foto di guida in città, <b>19 classi</b> (road, sidewalk, building, wall, fence, pole, traffic light, traffic sign, vegetation, terrain, sky, person, rider, car, truck, bus, train, motorcycle, bicycle).</li>
<li>Il <b>processore</b> prepara l'immagine (ridimensiona, normalizza con media e deviazione standard di ImageNet); il modello restituisce i <b>logit</b> di ciascuna classe.</li>
</ul>
<div class="box w"><b>Attenzione: il nome «1024-1024» non è la risoluzione che usa il notebook</b><p>Il checkpoint è chiamato <code>…cityscapes-1024-1024</code> perché è stato addestrato su ritagli 1024×1024, ma il suo file di configurazione del processore (<code>preprocessor_config.json</code>) fissa un ridimensionamento a <b>512×512</b>. Lo abbiamo verificato: il tensore in ingresso è (1, 3, 512, 512) e i logit sono (1, 19, 128, 128). Dettagli e conseguenze nella scheda 15.</p></div>
""", sec=("l20-p2", "Parte 2 · Segmentazione semantica", 'schede 13–19'), printed=NB + 'celle 29–30')

s(14, "Palette dei colori e legenda", """
<pre>CITYSCAPES_COLORS = np.array([[128, 64, 128], [244, 35, 232], [70, 70, 70], ...], dtype=np.uint8)  # 19 righe
def decode_labels(class_map, palette=CITYSCAPES_COLORS):
    return palette[class_map]              # (H, W) di interi -> (H, W, 3) uint8
def overlay_mask(image_rgb, colored_mask, alpha=0.5):
    return cv2.addWeighted(image_rgb, 1 - alpha, colored_mask, alpha, 0)</pre>
<ul>
<li>Una <b>palette</b> fissa associa a ogni classe un colore RGB: strada viola scuro (128, 64, 128), marciapiede rosa (244, 35, 232), edificio grigio (70, 70, 70), cielo azzurro (0, 130, 180), persona rosso (220, 20, 60), auto blu scuro (0, 0, 142), vegetazione verde (107, 142, 35)…, i colori standard di Cityscapes.</li>
<li><code>decode_labels</code> usa l'<b>indicizzazione avanzata</b> di numpy: <code>palette[class_map]</code> sostituisce ogni id con la sua riga della tabella, e dà in un colpo un'immagine (H, W, 3) senza cicli.</li>
<li>La legenda disegna un riquadro colorato per ogni classe: il commento spiega di non usare <code>imshow</code> con una colormap automatica, che normalizzerebbe i valori e potrebbe «spostare» la classe 0 nel colore sbagliato.</li>
<li>Fissare la palette all'inizio garantisce che <b>lo stesso colore voglia sempre dire la stessa classe</b> in tutte le figure del notebook.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Spiegare l'indicizzazione <code>palette[class_map]</code>: se <code>class_map</code> è (H, W) con valori in 0..18 e <code>palette</code> è (19, 3), il risultato è (H, W, 3) e <code>risultato[y, x] = palette[class_map[y, x]]</code>.</p></div>
""", img='img/nb_legenda.png', printed=NB + 'celle 31–33')

s(15, "La pipeline di inferenza", """
<pre>@torch.no_grad()
def segment_image(model, processor, pil_image):
    orig_w, orig_h = pil_image.size
    inputs = processor(images=pil_image, return_tensors="pt").to(device)
    logits = model(**inputs).logits                     # (1, 19, H/4, W/4) dell'immagine ridimensionata
    upsampled = F.interpolate(logits, size=(orig_h, orig_w), mode="bilinear", align_corners=False)
    return upsampled.argmax(dim=1).squeeze(0).cpu().numpy()    # (H, W) di id di classe
# nostra uscita: class_map shape: (498, 652); classes present: [0, 1, 2, 11]</pre>
<ul>
<li>Tre passi: (1) <b>preprocessing</b> (resize, normalizzazione); (2) <b>forward</b>: il decoder produce i logit a <b>1/4</b> della risoluzione dell'ingresso (è molto più economico che decodificare a piena risoluzione); (3) <b>upsampling dei logit</b> con interpolazione bilineare alla dimensione dell'immagine originale e <code>argmax</code> sulle classi.</li>
<li>Importante: si fa l'upsampling dei <b>logit</b> e poi l'argmax, non il contrario. Interpolare gli id di classe non avrebbe senso (la media di «strada» e «cielo» non è una classe); interpolare i logit dà confini più morbidi.</li>
<li>Sulla foto di esempio le classi trovate sono 0 (road), 1 (sidewalk), 2 (building) e 11 (person): il piazzale è stato letto come <b>sidewalk</b> (rosa), l'asfalto in basso come <b>road</b>, la facciata come <b>building</b>.</li>
</ul>
<div class="box k"><b>Da saper fare · le forme nella pipeline</b><p>Nostra esecuzione: ingresso del modello (1, 3, 512, 512) → logit (1, 19, 128, 128) → dopo <code>interpolate</code> (1, 19, 498, 652) → dopo <code>argmax</code> (1, 498, 652). Nota che il passaggio a 512×512 <b>stira</b> l'immagine (652×498 diventa quadrata): per questo il modello vede persone più «strette».</p></div>
<div class="box w"><b>Attenzione: 512×512 perde i dettagli sulle immagini di guida</b><p>Il processore riduce <b>qualsiasi</b> immagine a 512×512. Sulla foto Cityscapes 2048×1024 (aspect 2:1) questo la schiaccia a un quadrato e fa lavorare il modello a un quarto della risoluzione su cui è stato addestrato. Misurato sulla foto di Aquisgrana: con 512×512 il modello vede <b>61 427 pixel di «pole»</b> contro 16 314 con ingresso 1024×512 (che rispetta l'aspetto) e solo 339 pixel di «person» contro 1428. Costo: 0,5 s contro 1,4 s a immagine su CPU. Se serve precisione su oggetti piccoli e sottili, va passato <code>size={"height": 512, "width": 1024}</code> (o 1024×1024) al processore.</p></div>
""", img='img/nb_classmap.png', printed=NB + 'celle 34–35')

s(16, "L'overlay e la domanda su mIoU", """
<pre>colored_mask = decode_labels(class_map)
overlay = overlay_mask(sample_pil, colored_mask, alpha=0.5)   # (1 - alpha) * foto + alpha * maschera</pre>
<ul>
<li>L'<b>overlay</b> è una <b>miscela alfa</b> pixel per pixel: <span class="f">uscita = (1 − α) · foto + α · maschera colorata</span>. Con α = 0 si vede solo la foto, con α = 1 solo la maschera; 0,5 è un buon compromesso per giudicare a occhio se i confini coincidono con gli oggetti.</li>
<li>Cosa si vede sulla foto: la ragazza è segmentata bene come <b>person</b> (rosso, con lo zaino incluso), il piazzale e la scalinata come <b>sidewalk</b>, l'asfalto come <b>road</b>, la facciata come <b>building</b>. Errori tipici: nei gradini la rete alterna sidewalk e building, la persona piccola dietro i vetri <b>non viene vista</b>, le colonne e le vetrate sono comunque «building».</li>
<li>Per leggere un errore sui bordi: l'overlay mostra se il confine passa sul bordo vero dell'oggetto (risoluzione 1/4 dei logit → bordi leggermente smussati).</li>
</ul>
<div class="box k"><b>Da saper fare · domanda della cella 38: mIoU o pixel accuracy?</b><p>La <b>pixel accuracy</b> conta la frazione di pixel giusti: in una scena dominata da strada, cielo ed edifici è già alta anche se il modello non vede mai una persona, perché le persone coprono pochi pixel. L'<b>IoU medio per classe (mIoU)</b> calcola IoU = TP / (TP + FP + FN) per ogni classe e poi la media: ogni classe pesa uguale, quindi una classe mancata (IoU 0) abbassa molto la media. Esempio numerico nella dispensa (sezione 9): 95% di accuracy ma mIoU 0,64.</p></div>
<div class="box b"><b>Dal libro · cap. 50, § 50.5</b><p>Il visionbook dice proprio questo: la loss per pixel dà troppo peso agli oggetti grandi (si possono usare pesi per classe in base all'area media) e la percentuale di pixel corretti è dominata da questi oggetti; «più informativo» è l'IoU medio per classe, perché invariante alla scala.</p></div>
""", img='img/nb_overlay.png', printed=NB + 'celle 36–38')

s(17, "Il domain gap: SegFormer addestrato solo su GTA5", """
<pre>GTA5_CHECKPOINT = "guimCC/segformer-v0-gta"
gta5_model = SegformerForSemanticSegmentation.from_pretrained(GTA5_CHECKPOINT).to(device).eval()
class ManualSegformerProcessor:     # nessun preprocessor_config.json nel checkpoint
    def __init__(self, size=(512, 512)):
        self.tf = T.Compose([T.Resize(size), T.ToTensor(), T.Normalize(mean, std)])
    def __call__(self, images, return_tensors="pt"):
        return BatchFeature({"pixel_values": self.tf(images).unsqueeze(0)})
# nostra uscita: Loaded guimCC/segformer-v0-gta: 20 classes ({0: 'road', ..., 18: 'bicycle', 19: 'ignore'})</pre>
<ul>
<li><b>Domain gap</b>: un modello addestrato su un dominio (immagini <b>sintetiche</b> del videogioco GTA5) perde accuratezza su un altro (foto <b>reali</b>), perché cambiano texture, illuminazione, rumore e stile, anche se le classi sono le stesse. Qui entrambi i modelli sono SegFormer-b0 con le stesse 19 classi: cambia solo il dato di training.</li>
<li>Il checkpoint GTA5 non ha un file di configurazione del processore: il notebook ricostruisce a mano il preprocessing standard (resize a 512×512, ToTensor, normalizzazione ImageNet) con una classe <code>ManualSegformerProcessor</code> che restituisce un <code>BatchFeature</code>, così <code>segment_image</code> funziona senza modifiche.</li>
<li>Ha <b>20 classi</b>: le 19 di Cityscapes più <code>ignore</code> (id 19). Il notebook colora «ignore» di <b>nero</b> aggiungendo una riga alla palette.</li>
<li>Tutto è dentro un <code>try/except</code>: se il download fallisce, il notebook salta la sezione e prosegue.</li>
<li>Risultato sulla foto di Penn-Fudan: nel modello GTA5 la scalinata diventa tutta sidewalk (rosa) e la <b>gamba sinistra</b> della ragazza è etichettata come <b>road</b> (viola), con la persona che «si spezza»; il modello reale invece tiene la persona unita.</li>
</ul>
<div class="box k"><b>Da saper fare · domanda della cella 41</b><p>Cosa peggiora concretamente? Nell'immagine di esempio non le <b>forme</b> (la sagoma della persona è quasi giusta), ma l'<b>attribuzione di classe</b> nelle zone ambigue per un modello che ha visto solo la grafica di GTA5: texture e illuminazione reali (cemento, vetri, riflessi) non assomigliano a nulla di ciò che ha visto, e, è un'ipotesi ragionevole, assegna alla gamba scura la classe più vicina alla sua esperienza (asfalto). A cambiare fra i due domini sono soprattutto le statistiche di basso livello (colore, contrasto, rumore): è il motivo per cui si usano <b>augmentation</b> e <b>domain adaptation</b>.</p></div>
<div class="box w"><b>Attenzione: titolo con parentesi di troppo</b><p>Il titolo della figura (cella 40) è «Fine-tuned on real Cityscapes photos)», con una parentesi chiusa in eccesso.</p></div>
""", img='img/nb_gta_cs.png', printed=NB + 'celle 38–41')

s(18, "GTA5 contro una foto Cityscapes vera", """
<pre>GTA5_IMG_PATH = "./media/00140.png"                                   # frame di GTA5, 1914×1052
CITYSCAPES_IMG_PATH = "./media/aachen_000000_000019_leftImg8bit.png"  # Cityscapes reale, 2048×1024
rows = [("Cityscapes-finetuned SegFormer", seg_model, seg_processor),
        ("GTA5-finetuned SegFormer", gta5_model, gta5_processor)]
# 2 modelli x 2 immagini = griglia 2x2 di overlay</pre>
<ul>
<li>Il confronto è completo: due modelli, due immagini (un frame sintetico di GTA5 e una foto di strada di Aquisgrana). Sulle <b>due diagonali</b> ci sono i modelli «a casa» (Cityscapes sul reale, GTA5 sul sintetico), sulle altre i casi di domain gap.</li>
<li>Cosa si osserva: il modello reale sul frame GTA5 se la cava (auto blu, strada viola, cielo azzurro, persone rosse, vegetazione verde) con errori sul fondo; il modello GTA5 sulla <b>foto reale</b> lascia <b>macchie nere</b> («ignore») sull'asfalto e ai bordi, cambia la forma del marciapiede e del cartello a sinistra. Il modello GTA5 sul suo dominio dà invece una strada viola uniforme e auto con bordi netti, con qualche macchia nera sui palazzi.</li>
<li>Misura nostra (accordo pixel per pixel fra i due modelli, non è un'accuratezza): 61% sul frame GTA5, 77% sulla foto di Aquisgrana, 80% sulla foto Penn-Fudan, 44% sulla foto affollata.</li>
</ul>
<div class="box w"><b>Attenzione: la griglia 2×2 deforma le immagini</b><p>Le immagini 2:1 vengono disegnate con <code>imshow(..., aspect="auto")</code> in assi quasi quadrati (figsize 12×6 per riga): risultano <b>schiacciate in verticale</b>, in modo diverso da come le vede la rete (che le riduce comunque a 512×512). Per giudicare le forme meglio togliere <code>aspect="auto"</code>.</p></div>
<div class="box x"><b>Approfondimento</b><p>Il gap sintetico → reale è un tema centrale per la guida autonoma: i dati sintetici costano poco (le etichette sono gratis), ma servono tecniche come domain randomization, adversarial adaptation, self-training sul target e pre-training su dati reali. Con il solo GTA5 una SegFormer-b0 non arriva alla qualità del modello addestrato su Cityscapes.</p></div>
""", img='img/nb_2x2.png', printed=NB + 'celle 42–44')

s(19, "Faster R-CNN su una foto COCO", """
<pre>coco_boxes, coco_labels, coco_scores = detect(detector, coco_uint8, score_thresh=0.7)
coco_classes_found = sorted(set(COCO_CLASSES[l] for l in coco_labels.tolist()))
# nostra uscita: 4 detections, ['cat', 'remote']</pre>
<ul>
<li>Una pausa nella segmentazione: la cella 46 riprende il Faster R-CNN della Parte 1 sulla foto COCO con una soglia più bassa (0,7): <b>2 gatti</b> e <b>2 telecomandi</b> (il secondo, quello fra i gatti, entra solo con soglia 0,7).</li>
<li>Il titolo ricorda la sezione: è la <b>detection</b> (box e classe, nessuna maschera) a fare da riferimento per la segmentazione d'istanza che arriva nella Parte 4.</li>
<li>È anche un buon controllo sul <b>formato dei dati</b>: si è passati da PIL a tensori e di nuovo a PIL; il box del gatto di sinistra comprende anche una parte del divano e un telecomando, perché i due oggetti si sovrappongono (i box sono rettangoli, non contorni).</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Spiegare perché i box dei due gatti e del telecomando non si cancellano con la NMS: sono di <b>classi diverse</b> (cat e remote), oppure di <b>oggetti separati</b> con IoU bassa.</p></div>
""", img='img/nb_coco_frcnn.png', printed=NB + 'celle 45–46')

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
<li>Le due persone sono la <b>ragazza</b> (rosso) e la <b>persona piccola</b> dietro i vetri (verde), che SegFormer non aveva visto; è plausibile che l'approccio a box la trovi perché la RPN propone regioni a più scale (le anchor più piccole sono 32×32 pixel sull'immagine ingrandita a 800) mentre SegFormer lavora su una griglia di logit a 1/4 di un ingresso 512×512.</li>
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
""", printed=NB + 'celle 60–62')

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
