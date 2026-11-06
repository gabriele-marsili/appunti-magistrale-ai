
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
