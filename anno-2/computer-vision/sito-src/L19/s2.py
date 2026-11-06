
s(15, "Region Proposals: Selective Search", R("""
<p>Come ottenere ~2000 scatole candidate <b>senza addestrare niente</b>, in tre passi (figura di Uijlings et al. 2013: segmentazioni a più scale in alto, le scatole risultanti in basso):</p>
<ol>
<li><b>Regioni piccole e coerenti</b>: si sovrasegmenta l'immagine in <b>superpixel</b> (con l'algoritmo di Felzenszwalb e Huttenlocher).</li>
<li><b>Fusione per somiglianza</b>: si fonde ripetutamente la coppia di regioni adiacenti più simile, secondo un punteggio s(r<sub>i</sub>, r<sub>j</sub>).</li>
<li><b>Estrazione delle scatole</b>: si prende la scatola che racchiude ogni regione della gerarchia di fusioni: ~2000 proposte per immagine.</li>
</ol>
<p>È <b>non supervisionato e bottom-up</b>: un algoritmo fisso, non appreso dai dati. Faster R-CNN lo sostituirà con una rete appresa (la RPN).</p>
<p><b>Definizione (Region proposal)</b>: una regione rettangolare candidata, probabile contenitore di un oggetto, che viene punteggiata e raffinata in seguito invece di scansionare ogni finestra possibile.</p>
<div class="box b"><b>Dal libro · {C50}, § 50.4.1.2</b><p>Nel libro «selective search» indica più in generale la strategia a due stadi: un meccanismo economico propone candidati, un classificatore costoso li verifica solo lì (ispirata all'attenzione visiva: prima si guarda dove è probabile). L'algoritmo specifico di Uijlings et al. (fusione gerarchica di superpixel) è solo uno dei modi di generare le proposte; il libro cita anche segmentazione, reti neurali e finestre scorrevoli economiche.</p></div>
"""), sec=None, printed=P(15))

s(16, "Selective Search: la similarità", R("""
<p>La similarità fra due regioni mescola quattro indizi, perché nessuno basta da solo (le foto sono i casi in cui ciascuno funziona):</p>
<ul>
<li><b>Colore</b>: due gatti diversi per colore ma con lo stesso pelo → il colore li separa.</li>
<li><b>Texture</b>: un camaleonte mimetizzato nel colore ma con una texture diversa dallo sfondo.</li>
<li><b>Dimensione</b>: nessuna scala singola va bene (ciotola, insalata e tavolo sono tre oggetti di scale diverse).</li>
<li><b>Riempimento</b> (fill): le ruote sono incluse nell'auto anche se diverse per colore e texture.</li>
</ul>
<span class="f">s(r<sub>i</sub>, r<sub>j</sub>) = a<sub>1</sub> s<sub>colore</sub> + a<sub>2</sub> s<sub>texture</sub> + a<sub>3</sub> s<sub>dim</sub> + a<sub>4</sub> s<sub>fill</sub>,   s<sub>•</sub> ∈ [0, 1]</span>
<ul>
<li><b>Colore e texture</b>: ogni regione ha un istogramma L1-normalizzato (c<sub>i</sub><sup>k</sup> = frazione dei pixel della regione i nel bin k di colore; t<sub>i</sub><sup>k</sup> lo stesso per la texture, per esempio con risposte a derivate gaussiane). Si confrontano per <b>intersezione di istogrammi</b>: s<sub>colore</sub> = ∑<sub>k</sub> min(c<sub>i</sub><sup>k</sup>, c<sub>j</sub><sup>k</sup>), stessa forma per la texture.</li>
<li><b>Dimensione</b>: s<sub>dim</sub> = 1 − (size(r<sub>i</sub>) + size(r<sub>j</sub>)) / size(im): favorisce la fusione delle regioni piccole per prime.</li>
<li><b>Fill</b>: s<sub>fill</sub> = 1 − (size(BB<sub>ij</sub>) − size(r<sub>i</sub>) − size(r<sub>j</sub>)) / size(im), con BB<sub>ij</sub> la scatola stretta attorno a r<sub>i</sub> ∪ r<sub>j</sub>: premia le unioni compatte (poco spazio vuoto nella scatola).</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Conto con l'intersezione di istogrammi: c<sub>i</sub> = (0.5, 0.3, 0.2), c<sub>j</sub> = (0.2, 0.3, 0.5) → s = min(0.5, 0.2) + min(0.3, 0.3) + min(0.2, 0.5) = 0.2 + 0.3 + 0.2 = 0.7. Due istogrammi identici danno 1, due disgiunti danno 0. Dettagli (25 bin per canale, spazi di colore diversi) nella slide 62.</p></div>
"""), printed=P(16))

s(17, "Selective Search: The Merge Algorithm", R("""
<p>Figura in tre pannelli su un disegno di poche regioni:</p>
<ol>
<li><b>Oversegment</b>: i superpixel iniziali, da un algoritmo fisso e non supervisionato.</li>
<li><b>Merge</b>: si fonde la coppia adiacente più simile (evidenziata), per colore, texture, dimensione e fill.</li>
<li><b>Repeat</b> finché resta una sola regione: ogni regione intermedia diventa una proposta.</li>
</ol>
<p>A ogni passo si fonde l'<b>unica</b> coppia con il punteggio massimo, poi si ricalcolano le similarità della nuova regione con le sue vicine, e si ripete. Ogni regione creata a ogni passo (e anche ogni superpixel iniziale) dà una scatola: la gerarchia produce ~2000 scatole che coprono <b>tutte le scale</b>, dal singolo superpixel all'immagine intera. Lo pseudocodice completo è nell'appendice (slide 59).</p>
"""), printed=P(17))

s(18, "R-CNN: Regions with CNN Features", R("""
<p>Figura: la pipeline di R-CNN in quattro passi: (1) immagine in ingresso; (2) estrazione di ~2000 proposte; (3) calcolo delle feature con una CNN su ciascuna regione <b>deformata</b> (warped) a dimensione fissa; (4) classificazione («aeroplane? no. … person? yes. … tvmonitor? no.»).</p>
<p><b>Cosa risolve</b>: sostituisce le feature costruite a mano (HOG, Haar) con feature <b>apprese</b> da una CNN.</p>
<p><b>A test time</b>: per ogni classe c uno <b>SVM lineare</b> sulla feature congelata φ(r) ∈ ℝ<sup>4096</sup> della regione r: punteggio s<sub>c</sub>(r) = w<sub>c</sub><sup>⊤</sup> φ(r). Sono ~2000 passate in avanti <b>indipendenti</b> per immagine, senza alcuna computazione condivisa.</p>
<p><b>Addestramento in 3 passi separati</b>, sugli stessi ritagli deformati:</p>
<ol>
<li>fine-tuning della CNN come classificatore softmax a (C+1) classi (classi di oggetto + sfondo; le etichette vengono dall'IoU con la ground truth); poi la testa softmax viene <b>scartata</b>;</li>
<li>CNN congelata: un SVM lineare per classe sulle sue feature (soglia di negativi più severa);</li>
<li>CNN congelata: un <b>regressore di scatola</b> separato.</li>
</ol>
<div class="box k"><b>Da saper fare</b><p>Perché R-CNN è lento: 2000 regioni × una passata di una CNN pesante (es. AlexNet o VGG) ≈ decine di secondi per immagine, e l'addestramento in tre fasi richiede di salvare su disco le feature di tutte le regioni. Fast R-CNN taglia entrambi i problemi con una sola passata sull'immagine intera.</p></div>
"""), printed=P(18))

s(19, "Fast R-CNN: Sharing Computation via RoI Pooling", R("""
<p>Figura: l'intera immagine passa <b>una volta</b> nella ConvNet; ogni proposta (RoI) viene <b>proiettata</b> sulla feature map condivisa; uno strato di <b>RoI pooling</b> ne estrae un vettore di feature di dimensione fissa; due strati FC alimentano due uscite: un <b>softmax</b> di classe e un <b>regressore</b> di scatola.</p>
<ul>
<li><b>Idea chiave</b>: la feature map della CNN si calcola <b>una volta per immagine</b>, non una volta per proposta.</li>
<li><b>RoI pooling</b>: proietta ogni proposta sulla feature map condivisa e ne estrae una rappresentazione di dimensione fissa (per esempio 7 × 7).</li>
<li><b>Addestramento congiunto</b> di classificatore softmax e regressore, insieme alla CNN, con una loss multi-task:</li>
</ul>
<span class="f">ℒ = ℒ<sub>cls</sub>(p, u) + λ 𝟙[u ≥ 1] ℒ<sub>loc</sub>(t<sup>u</sup>, v)</span>
<p>La loss di localizzazione conta <b>solo per le RoI di primo piano</b> (u ≥ 1); lo sfondo ha etichetta u = 0. Simboli spiegati nella slide 23.</p>
<div class="box x"><b>Approfondimento</b><p>Il RoI pooling <b>arrotonda</b> le coordinate della RoI e dei suoi bin alla griglia intera della feature map: va bene per classificare, non per maschere pixel-precise. Per questo Mask R-CNN lo sostituisce con RoIAlign (slide 51).</p></div>
"""), printed=P(19))

s(20, "Faster R-CNN: Learned Proposals via RPN", R("""
<p>Fast R-CNN richiede ancora proposte <b>esterne e lente</b>. Faster R-CNN le sostituisce con una piccola <b>Region Proposal Network</b> (RPN) che scorre sulla <b>stessa feature map condivisa</b> e predice, per ogni posizione, un punteggio di <b>oggettività</b> («c'è un oggetto qui?») e gli <b>offset della scatola rispetto alle ancore</b> (slide seguente).</p>
<p>Figura: l'immagine entra negli strati conv; la feature map alimenta la RPN, che produce le proposte; le proposte vanno a RoI pooling e a un classificatore.</p>
<p><b>Ottimizzazione</b>: l'articolo originale alterna <b>4 passi</b> (addestra la RPN; addestra Fast R-CNN sulle sue proposte; riaddestra la RPN con gli strati condivisi congelati; riaddestra Fast R-CNN). Le implementazioni moderne addestrano tutta la pipeline <b>congiuntamente, end-to-end, in un passo</b>.</p>
<div class="box k"><b>Da saper fare</b><p>Distinguere le due reti dentro Faster R-CNN: la <b>RPN</b> (classe-agnostica: oggetto sì/no + scatola) e la <b>testa di Fast R-CNN</b> (classe vera + scatola raffinata). Entrambe riusano la feature map della backbone; per questo la stima delle proposte costa poco. La RPN ha una sua NMS interna sulle proposte, la testa ne ha una seconda sulle detection finali (vedi il lab, L20).</p></div>
"""), printed=P(20))

s(21, "Anchors", R("""
<p><b>Definizione (Anchor)</b>: un riquadro di riferimento fisso, centrato in una posizione della feature map, con una scala e un rapporto d'aspetto predefiniti. La rete <b>regredisce uno scostamento</b> da questo riquadro verso l'oggetto più vicino invece di predire coordinate assolute.</p>
<p>Figura (Ren et al. 2015): a sinistra lo schema della RPN: una <b>finestra scorrevole 3 × 3</b> sulla feature map produce un vettore intermedio di 256 numeri, da cui due strati: <b>cls</b> (2k punteggi: oggetto / non oggetto per ognuna delle k ancore) e <b>reg</b> (4k coordinate: un offset per ancora). A destra esempi di detection con i punteggi (persona 0.992, auto 1.000, cavallo 0.993, …).</p>
<ul>
<li>Scale e rapporti d'aspetto sono <b>predefiniti</b>; la rete impara solo scostamenti e punteggi di oggettività per ancora.</li>
<li><b>Perché funziona</b>: un piccolo scostamento da un riferimento noto è più facile da regredire di coordinate assolute, <b>ma solo se</b> l'insieme di ancore copre le scale e i rapporti d'aspetto degli oggetti del dataset.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Quante ancore? Nell'articolo k = 9 (3 scale × 3 rapporti: 1:1, 1:2, 2:1) su ogni posizione. Con una feature map 40 × 60 sono 40 · 60 · 9 = 21 600 ancore, e la RPN emette 2k = 18 punteggi e 4k = 36 offset per posizione. Con una FPN (più livelli) le ancore diventano decine di migliaia: nel lab (L20) ne vedrai un campione.</p></div>
"""), printed=P(21))

s(22, "From Offsets to Boxes: Encode vs. Decode", R("""
<p><b>Encode</b> (per costruire il bersaglio di training): data un'ancora (x<sub>a</sub>, y<sub>a</sub>, w<sub>a</sub>, h<sub>a</sub>) e la ground truth associata (x, y, w, h), entrambe in forma centro-dimensioni:</p>
<span class="f">t<sub>x</sub> = (x − x<sub>a</sub>)/w<sub>a</sub>,   t<sub>y</sub> = (y − y<sub>a</sub>)/h<sub>a</sub>,   t<sub>w</sub> = log(w/w<sub>a</sub>),   t<sub>h</sub> = log(h/h<sub>a</sub>)</span>
<p><b>Perché il logaritmo per w e h</b>: un rapporto di dimensioni w/w<sub>a</sub> è sempre positivo e moltiplicativo; il log lo trasforma in un bersaglio <b>illimitato</b> e circa simmetrico attorno a 0, come t<sub>x</sub> e t<sub>y</sub>, che un regressore lineare può predire direttamente. Decodificando con l'esponenziale si ha automaticamente ŵ, ĥ &gt; 0, e passi uguali in t<sub>w</sub> significano variazioni di dimensione relative uguali a qualunque scala dell'oggetto.</p>
<p><b>Decode</b> (inferenza): la rete predice (t̂<sub>x</sub>, t̂<sub>y</sub>, t̂<sub>w</sub>, t̂<sub>h</sub>) per ogni ancora e si invertono le formule:</p>
<span class="f">x̂ = t̂<sub>x</sub> w<sub>a</sub> + x<sub>a</sub>,   ŷ = t̂<sub>y</sub> h<sub>a</sub> + y<sub>a</sub>,   ŵ = e<sup>t̂<sub>w</sub></sup> w<sub>a</sub>,   ĥ = e<sup>t̂<sub>h</sub></sup> h<sub>a</sub></span>
<p><b>Da centro a angoli</b>, per il passo di NMS e IoU: x<sub>1</sub> = x̂ − ŵ/2, y<sub>1</sub> = ŷ − ĥ/2, x<sub>2</sub> = x̂ + ŵ/2, y<sub>2</sub> = ŷ + ĥ/2.</p>
<div class="box k"><b>Da saper fare</b><p>Esempio numerico. Ancora (x<sub>a</sub>, y<sub>a</sub>, w<sub>a</sub>, h<sub>a</sub>) = (100, 80, 40, 80), ground truth (x, y, w, h) = (110, 90, 60, 72). Allora t<sub>x</sub> = 10/40 = 0.25, t<sub>y</sub> = 10/80 = 0.125, t<sub>w</sub> = ln(60/40) = ln 1.5 ≈ 0.405, t<sub>h</sub> = ln(72/80) = ln 0.9 ≈ −0.105. Decodificando: ŵ = e<sup>0.405</sup> · 40 = 60 e ĥ = e<sup>−0.105</sup> · 80 = 72. Gli angoli: x<sub>1</sub> = 110 − 30 = 80, x<sub>2</sub> = 140, y<sub>1</sub> = 90 − 36 = 54, y<sub>2</sub> = 126.</p></div>
<div class="box x"><b>Approfondimento</b><p>Nelle implementazioni reali (torchvision) gli offset sono anche divisi per pesi fissi (es. 10, 10, 5, 5) per normalizzarne la scala: dettaglio che non cambia l'idea.</p></div>
"""), printed=P(22))

s(23, "Box Regression & Multi-Task Losses", R("""
<p>Le loss di Fast R-CNN e della RPN seguono la stessa ricetta: un termine di <b>classificazione</b> (per ogni scatola) più un termine di <b>localizzazione</b> che conta solo per le scatole <b>positive</b> (di primo piano). Figura a sinistra: una ground truth (riquadro pieno), un'ancora/proposta (tratteggiato) e le quattro quantità t<sub>x</sub>, t<sub>y</sub>, t<sub>w</sub>, t<sub>h</sub>; sotto, la tabella: positive (fg) → cls ✓ loc ✓; background (bg) → cls ✓ loc ✗. Lo sfondo continua ad addestrare il classificatore («non è un oggetto») ma <b>non contribuisce mai</b> alla loss di localizzazione.</p>
<p><b>Fast R-CNN</b> (per RoI; p = distribuzione di classe predetta; u = classe vera, con u = 0 sfondo; t<sup>u</sup> = offset predetto per la classe u; v = offset bersaglio):</p>
<span class="f">ℒ(p, u, t<sup>u</sup>, v) = − log p<sub>u</sub> + λ [u ≥ 1] ∑<sub>i</sub> smL1(t<sub>i</sub><sup>u</sup> − v<sub>i</sub>)</span>
<p><b>RPN di Faster R-CNN</b> (per ancora i; p<sub>i</sub> ∈ [0,1] oggettività predetta, p<sub>i</sub>* ∈ {0,1} etichetta vera; t<sub>i</sub>, t<sub>i</sub>* ∈ ℝ<sup>4</sup> offset predetto e bersaglio):</p>
<span class="f">ℒ = (1/N<sub>cls</sub>) ∑<sub>i</sub> ℒ<sub>cls</sub>(p<sub>i</sub>, p<sub>i</sub>*) + λ (1/N<sub>reg</sub>) ∑<sub>i</sub> p<sub>i</sub>* smL1(t<sub>i</sub> − t<sub>i</sub>*)</span>
<p><b>Smooth L1</b>: smL1(x) = 0.5 x<sup>2</sup> se |x| &lt; 1, altrimenti |x| − 0.5: quadratica vicino allo zero, lineare lontano, quindi <b>robusta agli offset anomali</b>.</p>
<div class="box k"><b>Da saper fare</b><p>smL1(0.3) = 0.5 · 0.09 = 0.045; smL1(2) = 2 − 0.5 = 1.5 (una L2 darebbe 2). La derivata è x vicino a 0 e ±1 lontano: il gradiente è limitato, quindi una scatola molto sbagliata non domina l'addestramento.</p></div>
<div class="box b"><b>Dal libro · {C50}, § 50.4.2</b><p>Il libro scrive lo stesso schema: cross-entropy per la classe e, per la localizzazione, una loss moltiplicata da un indicatore che la azzera per le scatole che non si sovrappongono ad alcuna ground truth (quelle vanno all'assegnamento «sfondo»). Confronta due scelte per la loss di scatola: la <b>loss IoU</b> (1 − IoU, invariante a traslazione e scala) e la <b>L2</b> (invariante alla traslazione ma non alla scala: più grande per scatole grandi). Un limite importante della loss IoU: vale 1 quando le scatole <b>non si sovrappongono</b>, quindi non dà gradiente (fig. 50.18). Per questo i detector usano regressioni su offset (L1 liscia) o varianti come GIoU, e DETR usa L1 + loss IoU insieme (slide 33).</p></div>
"""), printed=P(23))

s(24, "From Feature Maps to Detection Predictions", R("""
<p>Una figura a tre riquadri e una tabella di termini per non confondere le parole:</p>
<ul>
<li><b>Immagine</b> H × W pixel → la CNN produce una <b>feature map più grossolana</b> (griglia di posizioni, stride &gt; 1);</li>
<li>da ogni posizione si predicono punteggi di classe e una scatola (x, y, w, h);</li>
<li>la scatola predetta viene <b>riportata nello spazio dell'immagine</b> e può <b>estendersi ben oltre</b> la sua posizione d'origine.</li>
</ul>
<table>
<tr><th>Termine</th><th>Significato</th></tr>
<tr><td>Pixel</td><td>un elemento dell'immagine in ingresso</td></tr>
<tr><td>Posizione / cella della feature map</td><td>una posizione spaziale nella griglia d'uscita (più grossolana) della CNN</td></tr>
<tr><td>Anchor box</td><td>una scatola di riferimento predefinita in una posizione (solo nei metodi anchor-based)</td></tr>
<tr><td>Predicted bounding box</td><td>la (x, y, w, h) finale decodificata; non è confinata nella sua cella</td></tr>
<tr><td>Receptive field</td><td>la regione dell'<i>immagine</i> che influenza il valore di una posizione</td></tr>
</table>
<div class="box k"><b>Da saper fare</b><p>Non confondere cella e scatola: la cella decide <i>chi</i> è responsabile di predire un oggetto, la scatola è la <i>risposta</i>, e può essere enorme rispetto alla cella (un'auto che occupa metà immagine è predetta da una sola cella, quella del suo centro). Il campo recettivo dice quanta immagine «vede» la cella: se è più piccolo dell'oggetto, la predizione è difficile (richiama <a href="#L17">L17</a>, slide 10).</p></div>
"""), printed=P(24))

s(25, "YOLO: You Only Look Once", R("""
<p>Figura (Redmon et al. 2016): tre passi: (1) ridimensiona l'immagine; (2) passa una rete convoluzionale; (3) NMS. Idea: <b>saltare le proposte</b> e predire le scatole <b>direttamente</b> con un'unica regressione, comunque seguita da NMS.</p>
<ul>
<li>Griglia <b>S × S</b>: ogni cella predice <b>B scatole</b> con la loro confidenza e <b>un solo insieme di C probabilità di classe</b> (condiviso dalle B scatole).</li>
<li><b>Definizione (Grid cell)</b>: una delle S × S regioni in cui è divisa l'immagine; una cella è <b>responsabile</b> di un oggetto se il centro dell'oggetto cade al suo interno (al massimo un oggetto per cella). La scatola predetta non è confinata nella cella: il suo centro (x, y) è relativo alla cella, ma (w, h) può estendersi molto oltre (slide precedente).</li>
</ul>
<p><b>Loss</b> a somma di quadrati in tre parti: ℒ = ℒ<sub>box</sub> + ℒ<sub>conf</sub> + ℒ<sub>cls</sub>.</p>
<ul>
<li><b>Box</b>: errore su (x, y, √w, √h), solo per la scatola responsabile di un oggetto (la radice rende l'errore meno dominato dalle scatole grandi).</li>
<li><b>Confidenza</b>: calcolata per ogni scatola; le scatole di sfondo hanno peso ridotto (sono molte più di quelle con oggetti).</li>
<li><b>Classe</b>: un vettore di probabilità per cella.</li>
</ul>
<div class="box b"><b>Dal libro · Prince § 10.5.2; {C50}, § 50.4.1.4</b><p>Prince descrive la versione originale: immagine 448 × 448, 24 strati conv simili a VGG, ultimo strato 7 × 7 × 1024, uno strato FC a 4096 e uno finale; l'uscita codifica, per ogni cella della griglia 7 × 7, la classe più probabile e due scatole con 5 parametri ciascuna (x, y, altezza, larghezza, confidenza). Poi un'euristica elimina scatole a bassa confidenza e sopprime quelle sullo stesso oggetto (NMS). La rete è pre-addestrata su ImageNet. Il visionbook lo cita come metodo che guarda l'immagine «globalmente», meno accurato dei metodi a scansione ma più efficiente.</p></div>
<div class="box k"><b>Da saper fare</b><p>Dimensione dell'uscita di YOLOv1 con S = 7, B = 2, C = 20 (VOC): 7 · 7 · (B · 5 + C) = 7 · 7 · 30 = 1470 numeri. Limite della griglia: <b>un solo oggetto per cella</b>, quindi gruppi di oggetti piccoli vicini (uno stormo) vengono persi.</p></div>
"""), printed=P(25))

s(26, "From YOLOv1 to Modern YOLO", R("""
<p>Figura: quattro griglie che mostrano come cambia cosa viene predetto in ogni posizione:</p>
<ul>
<li><b>YOLOv1 (2016)</b>: la cella predice scatole <b>direttamente</b> (una griglia con una cella evidenziata e il suo oggetto).</li>
<li><b>YOLOv2 (2017)</b>: <b>prior di ancora</b> ottenute con <b>k-means</b> sulle scatole del dataset, centrate su ogni cella.</li>
<li><b>YOLOv3 (2018)</b>: <b>anchor-based</b>, più scatole per posizione, in tutte e <b>3 le scale</b>: griglie 13 × 13 (grande), 26 × 26 (medio), 52 × 52 (piccolo) per oggetti di dimensioni diverse.</li>
<li><b>YOLOv8 (Ultralytics, 2023)</b>: <b>anchor-free</b> con teste <b>disaccoppiate</b> (classificazione e regressione separate); la figura mostra le distanze (l, t, r, b) dal punto agli angoli. Non tutte le varianti sono identiche.</li>
</ul>
<p>Lezione di fondo: l'evoluzione va verso <b>predizioni multi-scala</b> e, più recentemente, <b>senza ancore predefinite</b>.</p>
"""), printed=P(26))

s(27, "Anchor-Based vs. Anchor-Free Detection", R("""
<p>Due pannelli a confronto:</p>
<table>
<tr><th>Anchor-based</th><th>Anchor-free</th></tr>
<tr><td>Scatole di riferimento (ancore) predefinite in ogni posizione</td><td>Predizioni legate direttamente alle posizioni della feature map, nessuna forma predefinita</td></tr>
<tr><td>La rete predice <b>offset</b> rispetto all'ancora più vicina</td><td>Per esempio FCOS regredisce (l, t, r, b): le <b>distanze dal punto ai 4 lati</b> della scatola</td></tr>
<tr><td>La ground truth è assegnata all'ancora che si sovrappone meglio</td><td>La ground truth è assegnata direttamente alle posizioni rilevanti (dentro la scatola, vicino al centro)</td></tr>
</table>
<div class="box k"><b>Da saper fare</b><p>Vantaggio anchor-free: niente iperparametri di ancore (scale, rapporti, soglie di assegnamento) da tarare per ogni dataset. Costo: più posizioni sono «positive» per lo stesso oggetto, quindi servono regole di assegnamento e correzioni di qualità (la center-ness della slide 29) e comunque l'NMS finale.</p></div>
"""), printed=P(27))

s(28, "SSD: Multi-Scale Single-Shot Detection", R("""
<p>Figura (Liu et al. 2016) che confronta l'architettura di SSD (in alto: backbone VGG-16 fino a conv5_3, poi strati extra di feature sempre più piccole; da diverse mappe, 38 × 38, 19 × 19, 10 × 10, 5 × 5, 3 × 3, 1 × 1, partono classificatori conv 3 × 3) con quella di YOLO (in basso: griglia 7 × 7, strati FC). SSD: <b>74.3 mAP a 59 FPS</b>; YOLO: 63.4 mAP a 45 FPS (VOC). SSD produce 8732 detection per classe prima della NMS, YOLO 98.</p>
<ul>
<li><b>Più scatole di default</b> (ancore), con diversi rapporti d'aspetto, predette in <b>ogni posizione di diverse risoluzioni del backbone</b> in un solo passaggio. L'idea multi-scala sarà adottata da YOLOv3.</li>
<li>Le mappe <b>poco profonde e ad alta risoluzione</b> rilevano oggetti <b>piccoli</b>; quelle <b>profonde e a bassa risoluzione</b> rilevano oggetti <b>grandi</b>.</li>
<li>A differenza di YOLOv1 (una sola griglia), SSD predice da <b>più griglie</b> di dimensioni diverse insieme.</li>
</ul>
<p>Scala della scatola di default al livello k di m: s<sub>k</sub> = s<sub>min</sub> + (s<sub>max</sub> − s<sub>min</sub>)/(m − 1) · (k − 1); per un rapporto d'aspetto a<sub>r</sub>: (w<sub>k</sub>, h<sub>k</sub>) = (s<sub>k</sub> √a<sub>r</sub>, s<sub>k</sub>/√a<sub>r</sub>).</p>
<div class="box k"><b>Da saper fare</b><p>Con s<sub>min</sub> = 0.2, s<sub>max</sub> = 0.9, m = 6: le scale sono 0.2, 0.34, 0.48, 0.62, 0.76, 0.9 (frazione dell'immagine); a<sub>r</sub> = 2 dà una scatola larga s√2 e alta s/√2, con area invariata s<sup>2</sup>.</p></div>
"""), printed=P(28))

s(29, "Fully Convolutional One-Stage Object Detection (FCOS)", R("""
<p><b>Anchor-free</b>: ogni posizione «positiva» (che cade <b>dentro una scatola</b> di ground truth) regredisce direttamente (l, t, r, b), le distanze dai 4 lati dell'oggetto; nessuna forma predefinita.</p>
<ul>
<li>Più posizioni cadono tipicamente nella stessa scatola, quindi <b>più posizioni predicono lo stesso oggetto</b> (poi ci pensa l'NMS).</li>
<li>Un ramo di <b>center-ness</b> riduce il peso delle scatole regredite da posizioni <b>lontane dal centro</b> dell'oggetto, sopprimendo le predizioni di bassa qualità vicino ai bordi.</li>
</ul>
<p>Figura (Tian et al. 2019): backbone (C3, C4, C5) → piramide di feature (P3–P7) → <b>teste condivise tra i livelli</b> con tre uscite per posizione: Classification (H × W × C), Center-ness (H × W × 1) e Regression (H × W × 4).</p>
<span class="f">centerness* = √( min(l*, r*)/max(l*, r*) · min(t*, b*)/max(t*, b*) )</span>
<p>con l*, t*, r*, b* le distanze della posizione dai lati della scatola.</p>
<div class="box k"><b>Da saper fare</b><p>Esempio: un punto a l* = 10, r* = 30, t* = 20, b* = 20 → √(10/30 · 20/20) = √(1/3) ≈ 0.58. Al centro esatto vale 1, sul bordo tende a 0. A inferenza il punteggio finale è punteggio di classe × center-ness, così le scatole mal centrate scendono in classifica e vengono eliminate dalla NMS.</p></div>
"""), printed=P(29))
