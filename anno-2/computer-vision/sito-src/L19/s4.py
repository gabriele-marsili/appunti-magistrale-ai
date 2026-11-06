
# ===================== INSTANCE E PANOPTIC =====================

s(49, "Instance & Panoptic Segmentation (divisoria)", """
<p>Sottotitolo: «Combining object localization with pixel-level understanding»: unire la <b>localizzazione degli oggetti</b> (scatole) con la <b>comprensione a livello di pixel</b> (maschere).</p>
""", kind='div', sec=("l19-inst", "Instance e panoptic segmentation", "slide 49–56"))

s(50, "Mask R-CNN: From Boxes to Instance Masks", R("""
<p>Figura (He et al. 2017, fig. 1): la foto di una partita di calcio entra nella backbone; <b>RoIAlign</b> estrae le feature di ogni RoI; da lì partono due rami: uno dà <b>classe e scatola</b>, l'altro, con due conv, dà una <b>maschera</b> per ogni persona (colori diversi sul risultato a destra).</p>
<ul>
<li>Aggiunge una <b>testa di maschera</b> (una piccola FCN) sopra ogni RoI di Faster R-CNN: stessa RPN, stesse ancore, stessa testa di scatola; scatola + classe + maschera per istanza <b>è</b> la segmentazione d'istanza.</li>
<li><b>RoIAlign</b>: campionamento bilineare, così la maschera si allinea ai pixel reali.</li>
<li><b>Quale scatola è quale</b>: le scatole di ground truth supervisionano l'addestramento della RPN; le <b>proposte</b> della RPN alimentano RoIAlign; le maschere di ground truth supervisionano <b>solo la testa di maschera</b>; in inferenza entrambe le teste predicono da zero.</li>
</ul>
<div class="box b"><b>Dal libro · {C50}, § 50.6</b><p>Il libro descrive esattamente questa scelta: dopo aver proposto ed etichettato le scatole, si dà il ritaglio dentro ogni scatola a una funzione di <b>segmentazione binaria</b> che predice, per ogni pixel, se appartiene all'oggetto. La loss è somma di classificazione (il ritaglio contiene l'oggetto?), localizzazione (solo se l'oggetto c'è) e segmentazione (la maschera corrisponde alla ground truth dell'istanza), con due pesi λ che le bilanciano. Il libro osserva che la formulazione si può estendere (coordinate per pixel, parti degli oggetti) e che in un certo senso «cerca di fare troppo»: la segmentazione precisa può essere difficile anche per le persone.</p></div>
"""), printed=P(50))

s(51, "RoIAlign: Bilinear Sampling in Detail", R("""
<ul>
<li><b>RoI Pooling</b> (Fast/Faster R-CNN) <b>arrotonda</b> il bordo della RoI e poi il bordo di ogni bin alle celle intere della feature map: due arrotondamenti disallineano le feature estratte dalla RoI vera.</li>
<li><b>RoIAlign</b> mantiene tutte le coordinate <b>continue</b>, senza nessun arrotondamento: si divide la RoI in k × k bin; in ogni bin si campionano r punti (x, y) regolarmente spaziati; ogni punto si legge dalla feature map per <b>interpolazione bilineare</b> dai suoi 4 vicini:</li>
</ul>
<span class="f">F(x, y) = ∑<sub>i,j ∈ {0,1}</sub> w<sub>ij</sub> F[x<sub>0</sub> + i, y<sub>0</sub> + j],   x<sub>0</sub> = ⌊x⌋, y<sub>0</sub> = ⌊y⌋</span>
<span class="f">w<sub>00</sub> = (1 − dx)(1 − dy),  w<sub>10</sub> = dx (1 − dy),  w<sub>01</sub> = (1 − dx) dy,  w<sub>11</sub> = dx dy,   dx = x − x<sub>0</sub>, dy = y − y<sub>0</sub></span>
<ul>
<li>L'uscita di ogni bin è la <b>media</b> (o il massimo) dei suoi r valori campionati. Questa precisione sotto il pixel è ciò che permette alla maschera predetta di allinearsi ai pixel veri dell'oggetto.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Esempio: punto (x, y) = (3.4, 5.7): x<sub>0</sub> = 3, y<sub>0</sub> = 5, dx = 0.4, dy = 0.7. Pesi: w<sub>00</sub> = 0.6 · 0.3 = 0.18, w<sub>10</sub> = 0.4 · 0.3 = 0.12, w<sub>01</sub> = 0.6 · 0.7 = 0.42, w<sub>11</sub> = 0.4 · 0.7 = 0.28; somma 1. Quindi F è la media pesata dei quattro vicini, più vicina al vicino (3, 6) (peso 0.42). Per capire il danno dell'arrotondamento: con stride 16 un errore di 0.5 celle sono 8 pixel dell'immagine, enorme per una maschera.</p></div>
"""), printed=P(51))

s(52, "Mask R-CNN: Multi-Task Loss", R("""
<p>Per ogni RoI si addestrano <b>tre loss insieme</b> (stesse ℒ<sub>cls</sub> e ℒ<sub>box</sub> di Faster R-CNN, più un termine nuovo):</p>
<span class="f">ℒ = ℒ<sub>cls</sub> + ℒ<sub>box</sub> + ℒ<sub>mask</sub></span>
<ul>
<li>Per C classi, la testa di maschera produce <b>C maschere binarie m × m</b> per RoI (una per classe). ℒ<sub>mask</sub> è la <b>cross-entropy binaria media per pixel</b>, calcolata <b>solo sul canale della classe di ground truth</b>: gli altri C − 1 canali non contribuiscono alla loss di quella RoI.</li>
<li><b>Perché è importante</b>: la predizione della maschera è <b>disaccoppiata dalla classificazione</b>. La maschera di ogni classe è una <b>sigmoide per pixel</b>, non una softmax in competizione con le altre classi, perché il ramo di classificazione decide già <i>quale</i> classe; il ramo di maschera risponde solo a «oggetto o sfondo» per quella classe, e funziona meglio, empiricamente, di una softmax per pixel su tutte le classi (come nella segmentazione semantica).</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>A inferenza si usa la maschera del canale della classe <b>predetta</b> dal ramo di classificazione, si ridimensiona a quella della scatola e si binarizza con soglia 0.5. Dimensioni tipiche: m = 28, C = 80 (COCO): la testa produce 28 × 28 × 80 numeri per RoI, ma la loss ne usa solo 28 × 28.</p></div>
"""), printed=P(52))

s(53, "Panoptic Segmentation: Unifying Everything", R("""
<p>Figura (Kirillov et al. 2019) su una strada cittadina: <b>Image</b>, <b>Semantic (stuff)</b> (mappa a colori: cielo, strada, edifici…), <b>Instance (things)</b> (maschere solo per auto e persone, su sfondo nero), <b>Panoptic</b> (la sintesi: ogni pixel ha classe e, se è una cosa, un'istanza).</p>
<ul>
<li><b>Stuff</b> (cielo, strada: non numerabili, senza istanze): una testa di segmentazione semantica. <b>Things</b> (oggetti numerabili): una testa di segmentazione d'istanza (Mask R-CNN).</li>
<li><b>Fusione, pixel per pixel</b>: (1) si ordinano le maschere d'istanza per confidenza e le si «incollano» sulla tela dalla più alta, così ogni pixel è rivendicato da <b>al più un'istanza</b>, evitando le sovrapposizioni; (2) ogni pixel non rivendicato da un'istanza ricade sulla predizione della testa semantica (una classe di stuff, oppure <i>void</i>).</li>
<li>Ogni pixel finisce con <b>esattamente una coppia (classe, id d'istanza)</b>; l'id d'istanza ha significato solo per le things.</li>
</ul>
<div class="box b"><b>Dal libro · Szeliski § 6.4.3 (il visionbook non la tratta)</b><p>Il cap. 50 si ferma alla segmentazione d'istanza (§ 50.6) e osserva solo che quella semantica «non sa contare». La segmentazione panottica è in Szeliski § 6.4.3 (Panoptic segmentation; sottoparagrafo non verificato): la proposta di Kirillov et al. 2019 e le architetture successive che predicono insieme le due uscite, con una sola rete.</p></div>
<div class="box x"><b>Approfondimento</b><p>La regola di fusione per «più sicura per prima» è un'euristica; i modelli successivi (Panoptic FPN, Mask2Former) predicono le due cose con una rete sola e fanno la fusione dentro il modello. In caso di conflitto, la regola della slide dà priorità alle istanze sullo stuff.</p></div>
"""), printed=P(53))

s(54, "Panoptic Quality (PQ)", R("""
<p>Sui segmenti: coppie (predizione p, ground truth g) con <b>IoU &gt; 0.5</b> sono <b>TP</b>; predizioni senza coppia sono <b>FP</b>; ground truth senza coppia sono <b>FN</b>.</p>
<span class="f">PQ = [ ∑<sub>(p,g) ∈ TP</sub> IoU(p, g) / |TP| ] × [ |TP| / (|TP| + ½|FP| + ½|FN|) ]  =  SQ × RQ</span>
<ul>
<li><b>SQ</b> (Segmentation Quality): quanto bene si sovrappongono i segmenti abbinati (IoU medio dei TP).</li>
<li><b>RQ</b> (Recognition Quality): quale frazione dei segmenti è stata abbinata (come una <b>F1</b> per la detection).</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Esempio: 3 coppie abbinate con IoU 0.9, 0.8, 0.7 (TP = 3), 1 FP, 2 FN. SQ = (0.9 + 0.8 + 0.7)/3 = 0.80; RQ = 3 / (3 + 0.5 + 1) = 0.667; PQ = 0.80 · 0.667 ≈ 0.53. Perché IoU &gt; 0.5 basta a rendere unico l'abbinamento: i segmenti panottici non si sovrappongono, quindi una ground truth non può avere due predizioni con IoU sopra 0.5. PQ si calcola per classe e poi si media, in genere anche separatamente per things e stuff (PQ<sup>Th</sup>, PQ<sup>St</sup>).</p></div>
"""), printed=P(54))

s(55, "Recap: Classification vs. Detection vs. Segmentation", R("""
<table>
<tr><th>Compito</th><th>Uscita</th><th>Etichetta (GT)</th><th>Loss di training</th><th>In inferenza</th></tr>
<tr><td>Classification</td><td>1 classe per tutta l'immagine</td><td>id di classe</td><td>cross-entropy</td><td>argmax della softmax</td></tr>
<tr><td>Object detection</td><td>insieme di (scatola, classe, punteggio)</td><td>scatole + classe per oggetto</td><td>CE (cls) + smooth-L1 (scatola), per ancora/RoI</td><td>NMS sulle scatole candidate</td></tr>
<tr><td>Semantic seg.</td><td>classe per pixel</td><td>maschera di classe per pixel</td><td>CE per pixel (+ Dice)</td><td>argmax per pixel</td></tr>
<tr><td>Instance seg.</td><td>scatola + maschera binaria per oggetto</td><td>scatole + maschere per istanza</td><td>CE + scatola + maschera (Mask R-CNN)</td><td>NMS, poi soglia della maschera per ogni scatola tenuta</td></tr>
<tr><td>Panoptic seg.</td><td>classe <i>e</i> id d'istanza per pixel</td><td>GT semantica + d'istanza fuse</td><td>loss semantiche + d'istanza, combinate</td><td>fusione dell'argmax semantico con le proposte d'istanza</td></tr>
</table>
<p>La tabella riassume l'intera lezione: cambiano <b>uscita, annotazioni, loss e post-elaborazione</b>, mentre la <b>backbone</b> (CNN o transformer) resta lo strumento comune.</p>
"""), printed=P(55))

s(56, "Summary", R("""
<p>La slide invita a confrontare le architetture per <b>meccanismo di fondo</b>, non per ordine di pubblicazione:</p>
<ul>
<li><b>Localizzazione</b>: finestre scorrevoli esaustive (Viola-Jones) → proposte di regioni a mano (Selective Search) → proposte <b>apprese</b> (RPN) → regressione diretta (YOLO).</li>
<li><b>Rappresentazione delle predizioni</b>: basata su proposte (Faster R-CNN), a griglia densa / one-stage (YOLO, SSD, FCOS), a insieme di query (DETR).</li>
<li><b>Gestione della scala</b>: ancore (Faster R-CNN, YOLOv2+, SSD), mappe di feature multi-scala (SSD, YOLOv3+) e regressione per posizione senza ancore (FCOS, YOLO moderno).</li>
<li><b>Raffinamento dell'uscita</b>: NMS greedy per la maggior parte dei detector, contro il matching bipartito end-to-end di DETR (senza NMS).</li>
<li><b>Segmentazione densa</b>: convoluzione atrous / ASPP (DeepLab) e decoder basati su ViT (SETR, SegFormer, DPT): entrambi spingono più in là risoluzione e contesto rispetto a FCN/U-Net.</li>
<li><b>Comprensione unificata della scena</b>: scatole (detection) + maschere (Mask R-CNN) + classi per pixel (segmentazione semantica) = segmentazione panottica.</li>
</ul>
<p><b>Valutazione</b>: mAP per la detection, mIoU per la segmentazione, PQ = SQ × RQ per la panottica.</p>
"""), printed=P(56))

s(57, "References", R("""
<p>Ventisette riferimenti, in due colonne. Per tema:</p>
<ul>
<li><b>Detection classica</b>: Viola e Jones 2001 (cascata boosted); Felzenszwalb e Huttenlocher 2004 (segmentazione basata su grafo, i superpixel); Uijlings et al. 2013 (Selective Search).</li>
<li><b>Two-stage</b>: Girshick et al. 2014 (R-CNN); Girshick 2015 (Fast R-CNN); Ren, He, Girshick e Sun 2015 (Faster R-CNN); He, Gkioxari, Dollár e Girshick 2017 (Mask R-CNN).</li>
<li><b>One-stage</b>: Redmon et al. 2016 (YOLO); Liu et al. 2016 (SSD); Wang et al. 2024 (YOLOv10); Tian, Shen, Chen e He 2019 (FCOS); Neubeck e Van Gool 2006 (Efficient NMS); Tan, Pang e Le 2020 (EfficientDet).</li>
<li><b>Transformer per la detection</b>: Carion et al. 2020 (DETR); Fang et al. 2021 (YOLOS).</li>
<li><b>Segmentazione</b>: Yu e Koltun 2016 (convoluzioni dilatate); Chen et al. 2017 (DeepLabv3); Chen et al. 2018 (DeepLabv3+); Zhao et al. 2017 (PSPNet); Zheng et al. 2021 (SETR); Xie et al. 2021 (SegFormer); Ranftl et al. 2021 (DPT); Kirillov et al. 2019 (panottica).</li>
<li><b>Dataset</b>: Everingham et al. 2010 (PASCAL VOC); Lin et al. 2014 (COCO); Cordts et al. 2016 (Cityscapes); Zhou et al. 2017 (ADE20K).</li>
</ul>
<p>Nota: PSPNet è nei riferimenti ma non compare nelle slide di questa lezione (era nella L17, slide 4).</p>
"""), sec=("l19-app", "Riferimenti e appendice", "slide 57–63"), printed=P(57))

s(58, "Appendix: Supplementary Formulas (divisoria)", """
<p>Slide divisoria: «Appendix, Supplementary derivations». Le quattro slide successive (59–62) contengono materiale di supporto: lo pseudocodice completo della Selective Search, l'algoritmo completo di calcolo dell'AP, la formula dei pesi di AdaBoost e i dettagli degli istogrammi.</p>
""", kind='div')

s(59, "Selective Search: Full Merge Pseudocode", R("""
<p>Pseudocodice dell'algoritmo di fusione (Uijlings et al. 2013, Algorithm 1). Ingresso: regioni iniziali R = {r<sub>1</sub>, …, r<sub>n</sub>} (superpixel di Felzenszwalb-Huttenlocher) e una funzione di similarità s(·, ·).</p>
<ol>
<li>S ← insieme di tutte le similarità s(r<sub>i</sub>, r<sub>j</sub>) fra regioni <b>adiacenti</b>.</li>
<li>Finché S non è vuoto: (r<sub>i</sub>, r<sub>j</sub>) ← argmax S (la coppia più simile); r<sub>t</sub> ← r<sub>i</sub> ∪ r<sub>j</sub>; R ← R ∪ {r<sub>t</sub>}.</li>
<li>Togli da S ogni similarità che coinvolge r<sub>i</sub> o r<sub>j</sub>; aggiungi a S le similarità s(r<sub>t</sub>, r<sub>k</sub>) con le regioni r<sub>k</sub> adiacenti a r<sub>t</sub>.</li>
<li>Restituisci la scatola che racchiude <b>ogni regione mai aggiunta a R</b> (superpixel iniziali compresi).</li>
</ol>
<div class="box k"><b>Da saper fare</b><p>Se i superpixel iniziali sono n, l'algoritmo fa esattamente n − 1 fusioni e produce 2n − 1 regioni (n iniziali + n − 1 fuse), quindi 2n − 1 scatole. Con n ≈ 1000 superpixel si arriva alle ~2000 proposte citate nella slide 15.</p></div>
"""), printed=P(59))

s(60, "Computing AP: The Full Ranking Algorithm", R("""
<p>Algoritmo completo del calcolo dell'AP per una classe. Ingresso: n detection ordinate per confidenza decrescente, g scatole di ground truth.</p>
<ol>
<li>tp, fp ← vettori di zeri lunghi n; matched ← ∅.</li>
<li>Per k = 1..n: j* ← argmax<sub>j ∉ matched</sub> IoU(det<sub>k</sub>, gt<sub>j</sub>) (la ground truth non ancora abbinata con IoU massimo).</li>
<li>Se IoU(det<sub>k</sub>, gt<sub>j*</sub>) ≥ 0.5: tp[k] ← 1 e matched ← matched ∪ {j*}; altrimenti fp[k] ← 1.</li>
<li>Somme cumulative: TP<sub>k</sub> = ∑<sub>l ≤ k</sub> tp[l], FP<sub>k</sub> = ∑<sub>l ≤ k</sub> fp[l].</li>
<li>P<sub>k</sub> = TP<sub>k</sub> / (TP<sub>k</sub> + FP<sub>k</sub>), R<sub>k</sub> = TP<sub>k</sub> / g, per k = 1..n.</li>
</ol>
<div class="box w"><b>Attenzione: rimando a un esempio che nella slide 35 non c'è</b><p>La slide dice «This produces exactly the P<sub>k</sub>, R<sub>k</sub> columns of the worked example on the main lecture slide»: ma la slide 35 contiene solo l'elenco dei passi, le formule e il disegno della curva, <b>nessuna tabella di esempio svolto</b>. Probabilmente la tabella è stata tolta. Per l'esame conviene rifare un esempio a mano, come quello della scheda 35 e della dispensa.</p></div>
<div class="box x"><b>Approfondimento</b><p>Piccola differenza con PASCAL VOC: lì si prende il massimo IoU fra <i>tutte</i> le ground truth; se quella è già abbinata, la detection è un FP. Qui si cerca solo fra le non abbinate, quindi una detection duplicata può abbinarsi a un'altra ground truth vicina. Con soglie 0.5 e oggetti ben separati i risultati coincidono; il libro (§ 50.4.3) descrive la variante PASCAL.</p></div>
"""), printed=P(60))

s(61, "Viola-Jones: Combining Weak Classifiers", R("""
<p>AdaBoost combina molti classificatori deboli h<sub>t</sub> (ognuno una soglia su una sola feature di Haar) in un unico classificatore forte:</p>
<span class="f">H(x) = sign( ∑<sub>t</sub> α<sub>t</sub> h<sub>t</sub>(x) ),   α<sub>t</sub> = ½ ln( (1 − ε<sub>t</sub>) / ε<sub>t</sub> )</span>
<p>ε<sub>t</sub> è l'<b>errore pesato di addestramento</b> di h<sub>t</sub>: più è basso, più alto è il voto α<sub>t</sub> del classificatore nella somma finale.</p>
<div class="box w"><b>Attenzione: sign con h ∈ {0, 1} non funziona</b><p>La slide 13 definisce h<sub>t</sub>(x) ∈ {0, 1}, ma qui scrive H(x) = sign(∑ α<sub>t</sub> h<sub>t</sub>(x)): con h ∈ {0, 1} e α<sub>t</sub> &gt; 0 la somma è sempre ≥ 0, quindi il segno darebbe «volto» per qualunque finestra. La forma con sign (e α<sub>t</sub> = ½ ln((1 − ε<sub>t</sub>)/ε<sub>t</sub>)) è l'AdaBoost standard con h<sub>t</sub> ∈ {−1, +1}. Nell'articolo di Viola e Jones, con h ∈ {0, 1}, si dichiara «volto» se ∑ α<sub>t</sub> h<sub>t</sub>(x) ≥ ½ ∑ α<sub>t</sub> (i pesi sono α<sub>t</sub> = ln((1 − ε<sub>t</sub>)/ε<sub>t</sub>), senza il ½). Le due versioni sono equivalenti a meno di come si codifica l'uscita.</p></div>
<div class="box k"><b>Da saper fare</b><p>ε = 0.5 (classificatore a caso) → α = ½ ln 1 = 0: nessun voto. ε = 0.1 → α = ½ ln 9 ≈ 1.10. ε = 0.01 → α ≈ 2.30. Un classificatore peggiore del caso (ε &gt; 0.5) avrebbe α negativo: AdaBoost lo userebbe «al contrario».</p></div>
"""), printed=P(61))

s(62, "Selective Search: Histogram Details & Efficiency", R("""
<ul>
<li><b>Istogramma di colore</b> c<sub>i</sub>: per ognuno dei 3 canali, un istogramma a <b>25 bin</b> di intensità sui pixel della regione r<sub>i</sub>; concatenati (75 bin) e normalizzati L1.</li>
<li><b>Istogramma di texture</b> t<sub>i</sub>: derivate gaussiane a <b>8 orientazioni</b>, per ogni canale, 10 bin per orientazione; stessa formula di intersezione del colore.</li>
<li><b>Efficiente da fondere</b>: l'istogramma di una regione fusa si ottiene <b>direttamente</b> da quelli delle parti, senza riscansionare i pixel:</li>
</ul>
<span class="f">C<sub>t</sub> = ( size(r<sub>i</sub>) C<sub>i</sub> + size(r<sub>j</sub>) C<sub>j</sub> ) / ( size(r<sub>i</sub>) + size(r<sub>j</sub>) )</span>
<ul>
<li><b>Diversificazione</b>: ripetere tutta la pipeline in più spazi di colore (RGB, HSV, Lab, …) aiuta perché ciascuno spazio è invariante a un insieme diverso e limitato di condizioni di ripresa (illuminazione, ombre).</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Media pesata: una regione da 100 pixel con una componente di istogramma 0.6 e una da 300 pixel con 0.2 danno (100 · 0.6 + 300 · 0.2)/400 = 0.3. È l'istogramma che si otterrebbe contando direttamente i pixel dell'unione, per questo la fusione è economica.</p></div>
"""), printed=P(62))

s(63, "Indice a miniature (non è una slide)", """
<p>L'ultima pagina del PDF non è una slide: è un indice a miniature delle pagine 1–62, generato dal PDF (le miniature sono quelle delle schede di questa pagina). Non ha contenuto nuovo.</p>
""", printed='')
