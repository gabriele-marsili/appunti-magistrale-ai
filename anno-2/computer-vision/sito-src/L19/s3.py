
s(30, "Non-Maximum Suppression", R("""
<p>Un detector produce molte scatole sovrapposte per lo stesso oggetto. La <b>NMS</b> (non-maximum suppression) ne tiene una sola. Figura in tre pannelli con tre scatole sovrapposte di punteggio 0.95, 0.87 e 0.72:</p>
<ol>
<li><b>Ordina e scegli</b>: la scatola a confidenza più alta (0.95) viene tenuta per prima.</li>
<li><b>Calcola l'IoU</b> con ognuna delle rimanenti (zona grigia = intersezione A ∩ B).</li>
<li><b>Sopprimi</b> le scatole con IoU &gt; soglia e <b>ripeti dal punto 1</b> con quelle che restano.</li>
</ol>
<span class="f">IoU(A, B) = Area(A ∩ B) / Area(A ∪ B) ≈ 3.0 / 4.3 ≈ 0.70</span>
<p>Con soglia 0.50: IoU(0.95, 0.87) ≈ 0.70 &gt; 0.50, quindi la scatola 0.87 viene soppressa (e lo stesso la 0.72).</p>
<div class="box b"><b>Dal libro · {C50}, § 50.4.1.2 e 50.4.2</b><p>Il libro dà lo stesso algoritmo in tre righe: (1) prendi la scatola a confidenza massima dall'insieme e aggiungila a quello finale; (2) togli dall'insieme quella scatola e tutte le altre con IoU sopra una soglia; (3) torna al punto 1 finché l'insieme è vuoto. L'IoU è un numero fra 0 (nessuna sovrapposizione) e 1 (scatole identiche), invariante a traslazione e scala.</p></div>
<div class="box k"><b>Da saper fare</b><p>Calcolare l'IoU a mano. A = [0, 0, 10, 10], B = [5, 5, 15, 15] (x<sub>1</sub>, y<sub>1</sub>, x<sub>2</sub>, y<sub>2</sub>): intersezione [5, 5, 10, 10] = 25; unione = 100 + 100 − 25 = 175; IoU = 25/175 ≈ 0.14. Se le scatole sono disgiunte l'intersezione è 0 e quindi IoU = 0.</p></div>
"""), printed=P(30))

s(31, "Greedy Non-Maximum Suppression", R("""
<p>Pseudocodice dell'algoritmo, eseguito <b>una volta per classe</b>. Ingresso: scatole (x<sub>1</sub>, y<sub>1</sub>, x<sub>2</sub>, y<sub>2</sub>), punteggi s<sub>i</sub> e soglia IoU τ.</p>
<ol>
<li>D ← ∅ (scatole tenute); I ← indici ordinati per s<sub>i</sub> decrescente.</li>
<li>Finché I non è vuoto: m ← I[0] (il punteggio più alto rimasto); aggiungi m a D e toglilo da I.</li>
<li>Per ogni i in I: calcola gli angoli dell'intersezione (xx<sub>1</sub>, yy<sub>1</sub> = massimo degli angoli in alto a sinistra; xx<sub>2</sub>, yy<sub>2</sub> = minimo degli angoli in basso a destra); inter = max(0, xx<sub>2</sub> − xx<sub>1</sub>) · max(0, yy<sub>2</sub> − yy<sub>1</sub>); IoU = inter/(area<sub>m</sub> + area<sub>i</sub> − inter); se IoU &gt; τ, togli i da I.</li>
<li>Restituisci D.</li>
</ol>
<ul>
<li><b>τ basso</b>: più aggressiva, rischia di sopprimere oggetti vicini; <b>τ alto</b>: sopravvivono più duplicati. Costo ingenuo O(n²). È <code>torchvision.ops.nms</code>.</li>
<li><b>DETR</b> evita questo passo grazie all'addestramento uno-a-uno; <b>YOLOv10</b> esplora un'inferenza senza NMS con «consistent dual assignments» (Wang et al. 2024), non condivisa da tutte le varianti di YOLO.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Il difetto classico della NMS greedy (domanda del lab): in una <b>folla</b> due persone vicine hanno scatole con IoU alto; la scatola della persona con punteggio più basso viene soppressa anche se è un oggetto diverso, quindi si perdono detection vere (recall più basso). Rimedi: Soft-NMS (si attenua il punteggio invece di cancellare), NMS adattiva, oppure evitare la NMS come DETR. La NMS va fatta <b>per classe</b>: un'auto non deve sopprimere la persona seduta davanti.</p></div>
"""), printed=P(31))

s(32, "DETR: Detection as Set Prediction", R("""
<p>Figura (Carion et al. 2020): immagine → <b>CNN</b> → insieme di feature → <b>encoder-decoder transformer</b> → insieme di predizioni di scatole → <b>bipartite matching loss</b> con la ground truth (le predizioni non assegnate valgono «no object (∅)»).</p>
<ol>
<li>Una <b>backbone CNN</b> estrae una feature map, appiattita in una sequenza con <b>codifiche posizionali fisse</b>.</li>
<li>Un <b>encoder transformer</b> applica self-attention alla sequenza (contesto globale, a differenza del campo recettivo locale della CNN).</li>
<li>Un <b>decoder transformer</b> prende N <b>object query</b> fisse e apprese e fa <b>cross-attention</b> sull'uscita dell'encoder.</li>
<li>Una <b>FFN condivisa</b> trasforma ogni embedding d'uscita q<sub>i</sub> in una predizione (p̂<sub>i</sub>(c), b̂<sub>i</sub>) = FFN(q<sub>i</sub>): distribuzione di classe (incluso «no object») e una scatola, per i = 1..N.</li>
</ol>
<p><b>Niente ancore, nessuna NMS convenzionale</b>: esattamente N predizioni per immagine, una <b>predizione di insieme</b> diretta, abbinata uno-a-uno alla ground truth (algoritmo ungherese) durante l'addestramento.</p>
<p>Attenzione alla terminologia: la backbone di DETR (passo 1) è una <b>CNN</b>, non un Vision Transformer; il transformer elabora solo la sequenza di feature risultante. <b>YOLOS</b> (Fang et al. 2021) è invece un detector nativo ViT: un ViT puro con query di tipo DETR.</p>
<div class="box b"><b>Dal libro · {C26}</b><p>Il visionbook non tratta DETR (fonte: l'articolo, ECCV 2020), ma lo strumento è quello del cap. 26: <b>attenzione</b> come combinazione dinamica di token. L'encoder è self-attention sui token-patch della feature map (come in un ViT, <a href="#L17">L17</a> slide 30); il decoder usa <b>cross-attention</b>: le N query fanno da «query» (Q) e i token dell'encoder da chiavi e valori (K, V) (§ 26.6.1). Le object query sono N vettori appresi, uno per «slot» d'oggetto: ciascuna impara a specializzarsi su una zona o una taglia.</p></div>
"""), printed=P(32))

s(33, "DETR: Why One-to-One Matching Removes NMS", R("""
<p>La ground truth y = (y<sub>1</sub>, …, y<sub>N</sub>) è <b>riempita con ∅</b> fino a N elementi. L'<b>algoritmo ungherese</b> sceglie l'assegnamento σ̂ delle query agli oggetti che minimizza il costo totale:</p>
<span class="f">σ̂ = argmin<sub>σ ∈ 𝔖<sub>N</sub></sub> ∑<sub>i=1..N</sub> ℒ<sub>match</sub>(y<sub>i</sub>, ŷ<sub>σ(i)</sub>)</span>
<span class="f">ℒ<sub>match</sub> = − 𝟙<sub>{c<sub>i</sub> ≠ ∅}</sub> p̂<sub>σ(i)</sub>(c<sub>i</sub>) + 𝟙<sub>{c<sub>i</sub> ≠ ∅}</sub> ℒ<sub>box</sub>(b<sub>i</sub>, b̂<sub>σ(i)</sub>)</span>
<p>Figura piccola: 3 query, 2 oggetti: q<sub>1</sub> → A, q<sub>2</sub> → B, q<sub>3</sub> → ∅.</p>
<ul>
<li><b>Loss di addestramento</b>: si minimizza lo stesso costo con l'assegnamento ottimo σ̂ (la «Hungarian loss»). Il termine di <b>classificazione</b> riguarda <b>tutte le N query</b>, anche quelle assegnate a ∅ (addestrate a predire «no object»); il termine di <b>scatola</b> (ℒ<sub>box</sub> = λ<sub>L1</sub> ‖b − b̂‖<sub>1</sub> + λ<sub>iou</sub> ℒ<sub>iou</sub>) solo per le query assegnate a oggetti veri.</li>
<li>Due query che predicono lo <b>stesso</b> oggetto sono penalizzate direttamente dalla loss: i duplicati sono <b>scoraggiati in addestramento</b>, non rimossi in inferenza come fa la NMS.</li>
</ul>
<div class="box w"><b>Attenzione: «lo stesso costo» è un'approssimazione</b><p>La slide dice che la loss di addestramento minimizza «lo stesso costo» del matching. Nell'articolo (Carion et al. 2020, eq. 2–3) i due sono simili ma non identici: nel <b>matching</b> compare −p̂<sub>σ(i)</sub>(c<sub>i</sub>), la probabilità; nella <b>Hungarian loss</b> compare −log p̂<sub>σ̂(i)</sub>(c<sub>i</sub>), il logaritmo (cross-entropy), e il termine della classe ∅ è pesato 1/10 per bilanciare le molte query di sfondo. Nel matching si usa la probabilità (non il logaritmo) perché, come dice l'articolo, così il termine di classe è commensurabile con quello di scatola.</p></div>
<div class="box k"><b>Da saper fare</b><p>Il matching è un problema di <b>assegnamento ottimo</b> (N × N matrice dei costi, algoritmo ungherese, <code>scipy.optimize.linear_sum_assignment</code>). Esempio con 2 query e 2 oggetti: costi [[0.2, 0.9], [0.6, 0.3]]; assegnamento (q<sub>1</sub>→A, q<sub>2</sub>→B) = 0.5, l'altro 1.5: vince il primo. A inferenza non c'è più matching: si tiene ogni query con la sua classe più probabile diversa da ∅.</p></div>
"""), printed=P(33))

s(34, "Three Ways to Organize Detection Predictions", R("""
<p>La tabella confronta tre modi di <b>organizzare le predizioni</b>:</p>
<table>
<tr><th>Approccio</th><th>Come sono organizzate le predizioni</th></tr>
<tr><td><b>Faster R-CNN</b></td><td>Proposte di regioni apprese, poi classificazione e raffinamento della scatola su ognuna (two-stage)</td></tr>
<tr><td><b>YOLOv1</b></td><td>Predizioni dense legate alle <b>celle di una griglia</b>, ogni cella responsabile degli oggetti il cui centro cade al suo interno (one-stage, a griglia)</td></tr>
<tr><td><b>DETR</b></td><td>Un insieme fisso di <b>object query</b> apprese, abbinate uno-a-uno alla ground truth durante l'addestramento (one-stage, a insieme)</td></tr>
</table>
<div class="box k"><b>Da saper fare</b><p>Risposta tipo orale: «chi decide il numero di oggetti e chi è assegnato a chi?» Faster R-CNN: le proposte (numero scelto, ~300–1000) e l'assegnamento per IoU con le ancore; YOLO: le celle e il centro dell'oggetto; DETR: N query e matching ungherese. Il prezzo della post-elaborazione: NMS per le prime due, nessuna per DETR.</p></div>
"""), printed=P(34))

s(35, "Evaluating Detectors: Average Precision", R("""
<p>Come si misura un detector. Per <b>una classe</b>:</p>
<ol>
<li>Si ordinano <b>tutte le detection</b> dell'intero insieme di valutazione per confidenza decrescente.</li>
<li>Una detection è un <b>vero positivo</b> (TP) se il suo IoU con una scatola di ground truth <b>non ancora assegnata</b> di quella classe è ≥ soglia; altrimenti è un <b>falso positivo</b> (FP).</li>
<li>Scendendo nella lista, a ogni rango k si calcolano precisione e recall cumulative sulle prime k detection.</li>
<li>Si ottiene un punto per rango: la <b>curva precisione-recall</b>; l'<b>AP</b> è l'area (interpolata) sotto la curva.</li>
</ol>
<span class="f">Precision = TP / (TP + FP),   Recall = TP / (TP + FN)</span>
<p>Figura: la curva a gradini precisione (asse y) contro recall (asse x); l'AP è l'area grigia sotto la curva.</p>
<div class="box b"><b>Dal libro · {C50}, § 50.4.3</b><p>Il libro descrive la procedura di PASCAL: si ordinano le detection per punteggio, e per ognuna si calcola l'IoU con tutte le ground truth, prendendo quella con IoU massimo; se supera la soglia (tipicamente 0.5) la detection è corretta e la ground truth viene <b>rimossa dalla lista</b> (niente doppi conteggi), altrimenti è sbagliata; le ground truth rimaste sono mancate. La curva precisione-recall dipende dalla soglia di confidenza ed è <b>non monotona</b>; l'AP è un numero in [0, 1], l'area sotto la curva (fig. 50.19: nell'esempio la recall si ferma a 0.5 perché il detector non trova mai l'altra metà degli oggetti).</p></div>
<div class="box k"><b>Da saper fare</b><p>Esempio con 3 ground truth e 5 detection in ordine di confidenza: TP, FP, TP, TP, FP. Ai ranghi 1–5: precisione 1/1, 1/2, 2/3, 3/4, 3/5 e recall 1/3, 1/3, 2/3, 3/3, 3/3. I punti (recall, precisione) sono (0.33, 1.0), (0.33, 0.5), (0.67, 0.67), (1.0, 0.75), (1.0, 0.6). Con l'interpolazione (precisione massima a destra di ogni recall) l'AP è 0.33 · 1.0 + 0.33 · 0.75 + 0.33 · 0.75 ≈ 0.83. Nel dettaglio nella dispensa.</p></div>
"""), printed=P(35))

s(36, "From AP to mAP", R("""
<ul>
<li><b>mAP</b>: la media degli AP su tutte le classi.</li>
<li><b>Matching uno-a-uno</b>: ogni scatola di ground truth è abbinata al più a una predizione, la migliore fra quelle che soddisfano la soglia; ogni detection in più dello stesso oggetto è un <b>falso positivo</b>, non un altro vero positivo.</li>
<li><b>Convenzione COCO, mAP@[.5:.95]</b>: media su soglie di IoU da 0.5 a 0.95 con passo 0.05 (10 soglie); più severa della mAP@0.5 ed è oggi il numero standard.</li>
<li>Un modello può avere una mAP@0.5 alta e una mAP@[.5:.95] molto più bassa se le sue scatole sono solo grossolanamente allineate: <b>controllare sempre entrambe</b>.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Perché il matching uno-a-uno è importante: senza, un detector senza NMS che produce 5 scatole sullo stesso oggetto avrebbe 5 «veri positivi» e una precisione perfetta. Con il matching, 1 TP e 4 FP: la precisione crolla, ed è proprio per questo che prima della valutazione serve l'NMS (o un modello a matching come DETR). Nota: «AP» e «mAP» in COCO sono spesso usati come sinonimi (AP già mediata sulle classi).</p></div>
"""), printed=P(36))

s(37, "Object Detection: Accuracy vs. Efficiency", R("""
<p>Figura (Tan et al. 2020, EfficientDet, fig. 1): <b>AP su COCO</b> (asse y) contro <b>FLOPs in miliardi</b> (asse x) per diverse famiglie: YOLOv3 (in basso a sinistra, ~30 AP, pochi FLOPs), Mask R-CNN, RetinaNet, ResNet + NAS-FPN, AmoebaNet + NAS-FPN + AA (a destra, ~48 AP ma oltre 1000 miliardi di FLOPs), e la curva rossa EfficientDet D0–D7 che sta <b>in alto a sinistra</b> (più accuratezza con meno calcolo; D7 ≈ 52 AP).</p>
<ul>
<li>La slide conclude che <b>backbone e «neck» contano quanto la famiglia del detector</b>: EfficientDet vince per la scalatura congiunta di backbone, rete di fusione delle feature e risoluzione, non per essere one-stage.</li>
<li><b>FLOPs ≠ latenza</b>: la velocità reale dipende anche da risoluzione, accessi alla memoria e hardware.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Leggere il grafico: nessun punto «migliore» in assoluto, ma una <b>frontiera di Pareto</b> accuratezza-costo. Quando si confronta, bisogna dire a quale costo (FLOPs, parametri, latenza su quale GPU) e con quale metrica (AP@[.5:.95]).</p></div>
"""), printed=P(37))

# ===================== SEGMENTAZIONE AVANZATA =====================

s(38, "Advanced Semantic Segmentation (divisoria)", """
<p>Sottotitolo: «Multi-scale context and Transformer-based dense prediction»: contesto <b>multi-scala</b> (convoluzioni dilatate, ASPP, DeepLab) e predizione densa con i <b>transformer</b> (SETR, SegFormer, DPT).</p>
""", kind='div', sec=("l19-seg", "Segmentazione semantica avanzata", "slide 38–48"))

s(39, "Why Dilated (Atrous) Convolution?", R("""
<p>Figura (Yu e Koltun 2016): tre griglie con un kernel 3 × 3 a <b>dilatazione d = 1, 2, 4</b>: i nove punti rossi sono i pesi, che coprono una zona 3 × 3, poi 5 × 5, poi 9 × 9 dell'ingresso; la zona colorata mostra il campo recettivo che cresce.</p>
<span class="f">dimensione effettiva del kernel = d(k − 1) + 1</span>
<ul>
<li>Parte dalla lezione scorsa (FCN/U-Net): il <b>pooling</b> allarga il campo recettivo ma <b>riduce la risoluzione</b>.</li>
<li>Impilando strati con dilatazione crescente (d = 1, 2, 4, …) il campo recettivo cresce <b>esponenzialmente</b> con la profondità, mentre il numero di pesi per strato resta k<sup>2</sup>.</li>
<li>È un'alternativa al pooling per ottenere più contesto <b>senza perdere risoluzione spaziale</b>.</li>
</ul>
<div class="box b"><b>Dal libro · {C24}, § 24.2.3; Prince § 10.2.3</b><p>Il libro presenta la convoluzione dilatata come cugina della convoluzione con stride: lì si «distanziano» i punti in cui si applica il filtro, qui si <b>distanzia il filtro stesso</b>, con zeri fra i pesi (fig. 24.9). Permette un filtro grande con pochi pesi. Avvertimento del libro: come lo stride, la dilatazione può introdurre <b>artefatti</b>: un filtro di blur dilatato non è più un blur (campiona punti lontani e può annullare certe frequenze, e dà <b>aliasing</b>, v. <a href="#L6">L6</a>). Questo è il difetto noto del «gridding» delle atrous convolutions.</p></div>
<div class="box k"><b>Da saper fare</b><p>Tre strati 3 × 3 con d = 1, 2, 4 (stride 1): dimensioni effettive 3, 5, 9; il campo recettivo totale è r = 1 + 2·(1 + 2 + 4) = 15, contro 7 per tre strati senza dilatazione. Nota: il libro (§ 24.2.3) scrive 9 × 9 per questa cascata, ma il supporto della cascata è 15 × 15; 9 è la dimensione dell'ultimo kernel da solo (stesso refuso già segnalato in <a href="#L15">L15</a>).</p></div>
"""), printed=P(39))

s(40, "Atrous Spatial Pyramid Pooling (ASPP)", R("""
<p>Figura (Chen et al. 2018, DeepLabv3+, fig. 2, solo l'encoder): l'immagine passa in una DCNN con convoluzioni atrous; la <b>stessa feature map</b> entra in <b>5 rami paralleli</b>: una conv 1 × 1, tre conv 3 × 3 atrous con <b>rate 6, 12, 18</b> e un ramo di <b>image pooling</b> globale; le uscite si <b>concatenano</b> e una conv 1 × 1 finale le fonde.</p>
<ul>
<li>Il problema: gli oggetti nella stessa immagine appaiono a <b>scale diverse</b>; un solo campo recettivo non si adatta a tutti.</li>
<li>La soluzione: guardare la stessa feature con <b>campi recettivi diversi</b> in parallelo e unire.</li>
<li>È la stessa idea di un modulo <b>Inception</b> (rami paralleli con campi recettivi diversi, concatenati): qui i rami variano la <b>dilatazione</b> invece della dimensione del kernel.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Con un kernel 3 × 3, il campo recettivo di un ramo è 2d + 1 sulla feature map: 13, 25 e 37 per d = 6, 12, 18 (in unità della mappa a stride 16). L'image pooling aggiunge il contesto globale (un vettore per immagine, ripetuto su tutta la mappa).</p></div>
"""), printed=P(40))

s(41, "DeepLabv3+: Full Pipeline", R("""
<p>Figura completa (Chen et al. 2018, fig. 2). <b>Encoder</b> (riquadro blu): backbone atrous → ASPP → conv 1 × 1. <b>Decoder</b> (riquadro rosso): le feature a basso livello (<i>low-level features</i>) del backbone passano per una conv 1 × 1, si <b>concatenano</b> con l'uscita dell'encoder <b>sovracampionata ×4</b>, una conv 3 × 3 le raffina, un ultimo upsampling ×4 dà la predizione.</p>
<ul>
<li><b>Encoder</b>: un backbone atrous alimenta ASPP: contesto multi-scala senza perdere risoluzione spaziale.</li>
<li><b>Decoder</b>: la <b>skip connection</b> (evidenziata) porta le feature a basso livello attorno ad ASPP con una conv 1 × 1, le concatena con l'uscita ASPP sovracampionata ×4, le raffina con una conv 3 × 3 e sovracampiona ×4 ancora.</li>
<li>Questa skip «stile U-Net» distingue DeepLabv3+ dal semplice DeepLabv3 e dà <b>bordi più netti</b> agli oggetti.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Dimensioni a stride d'uscita 16 per un'immagine 512 × 512: l'encoder lavora su 32 × 32; sovracampionando ×4 si arriva a 128 × 128, dove si concatenano le feature a basso livello (stride 4, 128 × 128); poi ×4 riporta a 512 × 512. Le feature a stride 4 hanno il dettaglio dei bordi che dopo 16× di sottocampionamento sarebbe perso: stessa funzione delle skip di U-Net (<a href="#L17">L17</a>, slide 16–17).</p></div>
"""), printed=P(41))

s(42, "Recall: Evaluating Segmentation – IoU", R("""
<p>Richiamo dalla L17 (slide 23). Quattro pannelli sulla stessa scena urbana (classe «vegetazione»): <b>Ground Truth</b>, <b>Prediction</b>, <b>Intersection</b> (Ŷ ∩ Y) e <b>Union</b> (Ŷ ∪ Y). Nell'unione: <b>verde</b> = accordo (TP), <b>rosso</b> = solo predizione (FP), <b>blu</b> = solo ground truth (FN).</p>
<span class="f">IoU = |Ŷ ∩ Y| / |Ŷ ∪ Y| = TP / (TP + FP + FN) ≈ 0.78 in questo esempio</span>
<span class="f">mIoU = (1/C) ∑<sub>c=1..C</sub> IoU<sub>c</sub></span>
<p>La mIoU è <b>robusta allo sbilanciamento fra classi</b>, a differenza della pixel accuracy, che è dominata dalle classi grandi (cielo, strada).</p>
<div class="box b"><b>Dal libro · {C50}, § 50.5</b><p>Il libro dà lo stesso consiglio: la percentuale di pixel corretti è dominata dagli oggetti grandi; una misura più informativa è l'IoU medio sulle classi, invariante di scala. Per la loss, la cross-entropy per pixel rischia di concentrarsi sugli oggetti grandi, e suggerisce un peso per classe che normalizza per l'area media della classe nel training set.</p></div>
"""), printed=P(42))

s(43, "SETR: Plain ViT Encoder for Segmentation", R("""
<p>Alternativa alla convoluzione atrous: far arrivare il contesto con la <b>self-attention</b> invece che con la dilatazione. Figura (Zheng et al. 2021): a destra in basso la <b>tokenizzazione</b> (patch embedding + position embedding + proiezione lineare), poi una pila di <b>24 strati transformer</b> (Layer Norm → Multi-Head Attention → residuo → Layer Norm → MLP → residuo), poi il <b>decoder</b> che produce la mappa di segmentazione colorata.</p>
<ul>
<li><b>Tokenizza</b>: si divide l'immagine H × W in patch p × p (p = 16), si proietta ciascuna linearmente in ℝ<sup>C</sup> e si somma la codifica posizionale: L = HW/p<sup>2</sup> token in tutto.</li>
<li><b>Encoder ViT puro</b>: L<sub>e</sub> strati transformer, self-attention <b>globale già dal primo strato</b>; nessuna gerarchia, nessuna feature multi-scala (a differenza dei backbone CNN).</li>
<li><b>Reshape</b>: l'uscita dell'encoder ∈ ℝ<sup>L×C</sup> diventa una feature map ℝ<sup>(H/p)×(W/p)×C</sup>.</li>
<li><b>Decoder PUP</b> (progressive upsampling): essendo p = 16 = 2<sup>4</sup>, servono 4 stadi di (conv 3 × 3 + upsampling bilineare ×2) per tornare alla risoluzione piena.</li>
<li>Il più semplice dei tre modelli basati su ViT, ma anche il <b>più costoso</b>: self-attention O(L<sup>2</sup>) su tutti gli L token, a ogni strato.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Quanti token? Un'immagine 512 × 512 con p = 16 dà L = (512/16)<sup>2</sup> = 1024 token, quindi 1024<sup>2</sup> ≈ 10<sup>6</sup> coppie di attenzione per testa e per strato. Con p = 8 sarebbero 4096 token e 16 · 10<sup>6</sup> coppie: il costo quadratico motiva SegFormer. Per l'adattamento a risoluzioni diverse in test le codifiche posizionali apprese vanno interpolate (<a href="#L17">L17</a>, slide 27–28).</p></div>
"""), printed=P(43))

s(44, "SegFormer: Hierarchical Encoder, Lightweight Decoder", R("""
<p>Figura (Xie et al. 2021): a sinistra l'<b>encoder</b> con quattro blocchi transformer (Overlap Patch Embeddings seguiti da Transformer Block 1–4), a destra il <b>decoder</b> con quattro MLP, un upsampling, una concatenazione e un MLP finale che produce H/4 × W/4 × N<sub>cls</sub>. Sotto, il dettaglio del blocco (Efficient Self-Attn, Mix-FFN, Overlap Patch Merging, ripetuto ×N).</p>
<ul>
<li><b>Encoder MiT gerarchico</b>: 4 stadi che riducono la risoluzione come una CNN (feature map a ≈ 1/4, 1/8, 1/16, 1/32 dell'ingresso); feature multi-risoluzione F<sub>i</sub>, a differenza della scala singola di SETR.</li>
<li><b>Decoder all-MLP</b>, per ogni stadio i = 1..4: proietta a una dimensione di canali comune C, sovracampiona a 1/4 di risoluzione, fonde e predice:</li>
</ul>
<span class="f">F̂<sub>i</sub> = Upsample( Linear(C<sub>i</sub>, C)(F<sub>i</sub>) ),   M = Linear(C, N<sub>cls</sub>)( Linear(4C, C)( Concat(F̂<sub>1</sub>, …, F̂<sub>4</sub>) ) )</span>
<div class="box k"><b>Da saper fare</b><p>Perché un decoder così semplice basta: le feature profonde dei transformer hanno già un campo recettivo (quasi) globale; il decoder deve solo <b>unire</b> informazione locale (stadi 1–2, bordi) e contestuale (stadi 3–4, semantica). Il risultato è un modello piccolo: SegFormer-B0 ha 3.7 M di parametri (slide 48).</p></div>
"""), printed=P(44))

s(45, "SegFormer: Inside the Encoder Block", R("""
<p>Tre idee nel blocco dell'encoder:</p>
<ul>
<li><b>Overlapped Patch Merging</b>: finestre <b>sovrapposte</b> fra uno stadio e l'altro (a differenza del patchify non sovrapposto del ViT) preservano la continuità locale.</li>
<li><b>Efficient Self-Attention</b>: la self-attention completa su tutti gli N token è troppo costosa agli stadi iniziali ad alta risoluzione, quindi si rimodella K ∈ ℝ<sup>N×C</sup> riducendone la lunghezza di sequenza di un fattore R prima dell'attenzione, e poi si proietta di nuovo a C canali:</li>
</ul>
<span class="f">K̂ = Linear(C·R, C)( Reshape(N/R, C·R)(K) )</span>
<p>(la stessa proiezione per V). Riduce il costo dell'attenzione da O(N<sup>2</sup>) a O(N<sup>2</sup>/R).</p>
<ul>
<li><b>Mix-FFN</b>: le codifiche posizionali fisse non generalizzano quando risoluzione di training e test differiscono, quindi una <b>convoluzione depthwise 3 × 3</b> dentro l'MLP inietta direttamente l'informazione posizionale:</li>
</ul>
<span class="f">x<sub>out</sub> = MLP( GELU( Conv<sub>3×3</sub>( MLP(x<sub>in</sub>) ) ) ) + x<sub>in</sub></span>
<div class="box k"><b>Da saper fare</b><p>Esempio: N = 128 · 128 = 16 384 token allo stadio 1 (stride 4 su 512²), R = 64 (valore usato nel primo stadio): le chiavi scendono a 256 token e la matrice di attenzione da 16 384² ≈ 2.7 · 10<sup>8</sup> a 16 384 · 256 ≈ 4.2 · 10<sup>6</sup> elementi (64 volte meno, cioè proprio N<sup>2</sup>/R). Ricordare che la convoluzione dà anche <b>bias di località</b>, e che senza codifiche posizionali esplicite il modello si adatta a qualunque risoluzione.</p></div>
"""), printed=P(45))

s(46, "DPT: ViT + Convolutional Reassemble", R("""
<p>Figura (Ranftl et al. 2021, DPT): a sinistra la pila di transformer del ViT; da quattro profondità diverse partono blocchi <b>Reassemble</b> (a risoluzioni 4, 8, 16, 32) che vengono fusi da blocchi <b>Fusion</b> in cascata fino a una <b>Head</b> che produce, per esempio, una mappa di profondità. A destra il dettaglio di un blocco Reassemble (Read, Concatenate, Resample) e di uno di Fusion (Residual Conv Unit, Resample 0.5, Project).</p>
<ul>
<li><b>Reassemble</b>: trasforma i token di <b>più strati</b> del ViT di nuovo in feature map a <b>4 risoluzioni diverse</b>.</li>
<li><b>Fusion</b>: un modulo convoluzionale che fonde progressivamente queste mappe multi-scala; stato dell'arte per la <b>stima della profondità monoculare</b> (è il modello che sta dietro MiDaS v3, <a href="#L17">L17</a> slide 20).</li>
</ul>
<div class="box x"><b>Approfondimento</b><p>DPT è un'idea alla U-Net applicata a un encoder piatto: poiché il ViT non ha stadi a risoluzione decrescente, le feature «a più scale» si ricostruiscono rimodellando i token di strati diversi in griglie e ricampionandole (↑ o ↓) a risoluzioni diverse.</p></div>
"""), printed=P(46))

s(47, "DPT: Reassemble e Fusion nel dettaglio", R("""
<ul>
<li><b>Reassemble<sub>s</sub></b> (uno per profondità del ViT scelta, scala s ∈ {1/4, 1/8, 1/16, 1/32}): <b>Read</b> (si elimina o si proietta il token di lettura, cioè il [CLS]) → <b>Concatenate</b> (i token tornano in una griglia h × w) → <b>Resample</b> (conv 1 × 1 + ridimensionamento).</li>
<li><b>Fusion</b> (dal più fine in poi): due <b>residual conv unit</b>, poi upsampling ×2 + proiezione 1 × 1, <b>sommata</b> all'uscita del Reassemble successivo (più fine).</li>
<li>Le feature da <b>più profondità del ViT a più scale</b> danno una fusione multi-scala «alla CNN» senza un encoder gerarchico.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Con ViT-B/16 a 384 × 384: la griglia di token è 24 × 24. Reassemble<sub>4</sub> la porta a 96 × 96 (×4), Reassemble<sub>8</sub> a 48 × 48, Reassemble<sub>16</sub> resta 24 × 24, Reassemble<sub>32</sub> scende a 12 × 12. La fusione procede dal 12 × 12 al 96 × 96, e la Head dà la predizione a risoluzione piena.</p></div>
"""), printed=P(47))

s(48, "Semantic Segmentation: Accuracy vs. Efficiency", R("""
<p>Figura (Xie et al. 2021, fig. 1): <b>mIoU su ADE20K</b> (asse y) contro il <b>numero di parametri in milioni</b> (asse x). La tabella nella figura:</p>
<table>
<tr><th>Modello</th><th>mIoU</th><th>Parametri</th><th>FLOPs</th><th>FPS</th></tr>
<tr><td>SegFormer-B0</td><td>37.4</td><td>3.7 M</td><td>8.4 G</td><td>50.5</td></tr>
<tr><td>FCN-R50</td><td>36.1</td><td>49.6 M</td><td>198.0 G</td><td>23.5</td></tr>
<tr><td>SegFormer-B2</td><td>46.5</td><td>27.5 M</td><td>62.4 G</td><td>24.5</td></tr>
<tr><td>DeepLabv3+/R101</td><td>44.1</td><td>62.7 M</td><td>255.1 G</td><td>14.1</td></tr>
<tr><td>HRNet-W48 + OCR</td><td>43.0</td><td>70.5 M</td><td>164.8 G</td><td>17.0</td></tr>
<tr><td>SegFormer-B4</td><td>50.3</td><td>64.1 M</td><td>95.7 G</td><td>15.4</td></tr>
<tr><td>SETR</td><td>48.6</td><td>318.3 M</td><td>362.1 G</td><td>5.4</td></tr>
</table>
<p>Sintesi della slide: <b>SegFormer-B2</b> (27.5 M) ottiene 46.5 mIoU a 24.5 FPS contro i 44.1 mIoU a 14.1 FPS di <b>DeepLabV3+/R101</b> (62.7 M): meno della metà dei parametri, più accuratezza e più velocità. SETR ha un'accuratezza simile a B4 ma con 5 volte i parametri e un terzo della velocità.</p>
<div class="box k"><b>Da saper fare</b><p>Chi vince? B0 batte FCN-R50 con 13 volte meno parametri; B4 (50.3) batte SETR (48.6) con un quinto dei parametri e il triplo dei FPS. Lezione: l'<b>architettura</b> (gerarchia, attenzione efficiente) conta più della semplice taglia del modello.</p></div>
"""), printed=P(48))
