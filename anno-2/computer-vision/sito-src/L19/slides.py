VB = 'https://visionbook.mit.edu/'
def L(slug, txt): return f'<a href="{VB}{slug}" target="_blank">{txt}</a>'
LK = {
 '{C50}': L('object_recognition_v3.html', 'cap. 50'),
 '{C24}': L('convolutional_neural_nets.html', 'cap. 24'),
 '{C26}': L('transformers.html', 'cap. 26'),
 '{C12}': L('neural_nets.html', 'cap. 12'),
 '{C43}': L('3d_learning.html', 'cap. 43'),
 '{C23}': L('pyramids_new_notation.html', 'cap. 23'),
}
def P(n): return f' <em>· pag. {n}/63</em>'
def R(t):
    for k, v in LK.items(): t = t.replace(k, v)
    return t

# ===================== INTRODUZIONE =====================

s(1, "Object Detection and Segmentation: copertina", R("""
<p>Lezione del 28 ottobre 2026, tenuta da <b>Donald Shenaj</b> (non dal prof. Carta). Continua la <a href="#L17">L17</a> (predizione densa, U-Net, ViT): lì l'uscita era una <b>mappa a risoluzione fissa</b> con un'etichetta per pixel; qui l'uscita diventa un <b>insieme di oggetti</b> in numero sconosciuto, ognuno con una scatola (bounding box), una classe e un punteggio. Poi si torna alla segmentazione con architetture più potenti (DeepLab, SETR, SegFormer, DPT) e si chiude con l'unione dei due mondi: segmentazione d'istanza (Mask R-CNN) e panottica.</p>
<p>Il PDF ha 63 pagine e il footer stampa «n / 63» con n = numero di pagina del PDF, copertina compresa. Le pagine 8, 38, 49, 58 sono divisorie (senza numero). La pag. 63 non è una slide: è un indice a miniature delle pagine 1–62. Le pagine 58–62 sono un'appendice con formule supplementari.</p>
"""), sec=("l19-intro", "Introduzione", "slide 1–7"), printed=P(1))

s(2, "Lecture Outline", R("""
<p>Tre parti:</p>
<ol>
<li><b>Object Detection</b> (slide 8–37): problema, famiglie one-stage e two-stage, dai sliding window a Faster R-CNN, YOLO, SSD, FCOS, NMS, DETR, metriche (AP, mAP).</li>
<li><b>Advanced Architectures for Semantic Segmentation</b> (slide 38–48): convoluzione dilatata, ASPP e DeepLabv3+, poi i modelli basati su ViT (SETR, SegFormer, DPT).</li>
<li><b>Instance and Panoptic Segmentation</b> (slide 49–56): Mask R-CNN con RoIAlign, segmentazione panottica e Panoptic Quality.</li>
</ol>
<p>Poi riassunto (56), riferimenti (57) e appendice (58–62).</p>
"""), printed=P(2))

s(3, "Recap", R("""
<p>Richiama la L17: le reti per <b>uscite strutturate nello spazio</b> (FCN, U-Net) producono una griglia di uscita di dimensione <b>fissa</b>, uguale a quella dell'ingresso, con un'etichetta per pixel. La domanda di oggi: <b>come fa una rete a predire una scatola e una classe separate per ogni oggetto quando il numero di oggetti non è noto in anticipo?</b></p>
<p>Il percorso, in una riga: detection → one-stage contro two-stage → NMS → DETR → valutazione; poi segmentazione avanzata (DeepLab, decoder basati su ViT); poi segmentazione d'istanza (che riusa gli strumenti della detection); infine la panottica, che unisce tutto.</p>
<div class="box k"><b>Da saper fare</b><p>Dire in una frase perché la detection è più difficile della segmentazione semantica: l'uscita è un <b>insieme</b> (senza ordine, di lunghezza variabile), quindi mancano due cose che la cross-entropy per pixel dava per scontate, cioè <b>quante</b> predizioni ci sono e <b>quale predizione corrisponde a quale oggetto</b>. Tutta la lezione è fatta di risposte diverse a queste due domande (ancore e proposte, griglie, query con matching ungherese).</p></div>
"""), printed=P(3))

s(4, "Classification, Detection, and Segmentation", R("""
<p>La stessa immagine con <b>quattro forme di uscita</b> diverse (figura a quattro pannelli):</p>
<ul>
<li><b>Semantic segmentation</b> (sinistra): una mappa colorata, un'etichetta per pixel (erba, cane, albero, cielo). «No objects, just pixels»: non c'è nozione di oggetto.</li>
<li><b>Classification + localization</b>: un solo oggetto, quindi una sola scatola e una sola classe (cane).</li>
<li><b>Object detection</b>: più oggetti, una scatola per ciascuno, con la sua classe (gatto, cane, cane).</li>
<li><b>Instance segmentation</b>: come la detection, ma al posto della scatola una <b>maschera</b> per pixel, di colore diverso per ogni istanza.</li>
</ul>
<p>Il punto: stesso ingresso, ma uscite di tipo diverso: <b>un'etichetta, un insieme di scatole, una mappa per pixel</b>.</p>
<div class="box b"><b>Dal libro · {C50}, § 50.4–50.6</b><p>Il capitolo 50 percorre esattamente questa scala di rappresentazioni, dall'immagine intera (classificazione, § 50.3) alla scatola (localizzazione, § 50.4), al pixel (segmentazione di classe, § 50.5) fino alla maschera per istanza (§ 50.6). Ogni passo aggiunge un'informazione che il precedente non aveva, e ha un limite che il successivo risolve: la scatola non descrive oggetti sottili o senza bordi netti («stuff» come erba, acqua, cielo), la mappa semantica non sa contare oggetti a contatto.</p></div>
"""), printed=P(4))

s(5, "Classification, Detection, and Segmentation: i formati", R("""
<p>La tabella riassume cosa produce la rete f<sub>θ</sub> su un'immagine x ∈ ℝ<sup>H×W×3</sup> con C classi:</p>
<ul>
<li><b>Semantic seg.</b>: ŷ<sub>h,w</sub> ∈ [0,1]<sup>C</sup> per ogni pixel, tensore H × W × C, <b>dimensione fissa</b>.</li>
<li><b>Classif. + loc.</b>: una classe e una scatola b̂ = (x, y, w, h): C + 4 numeri, <b>dimensione fissa</b>.</li>
<li><b>Detection</b>: un insieme {(ŷ<sub>i</sub>, b̂<sub>i</sub>)}, i = 1..N̂, con N̂ <b>sconosciuto</b>.</li>
<li><b>Instance seg.</b>: un insieme {(ŷ<sub>i</sub>, b̂<sub>i</sub>, M̂<sub>i</sub>)} con M̂<sub>i</sub> ∈ [0,1]<sup>H×W</sup>, N̂ sconosciuto.</li>
</ul>
<p>Due righe conclusive: con un'<b>uscita di dimensione fissa</b> ogni unità d'uscita ha un bersaglio ovvio (il pixel o la classe giusta), quindi bastano cross-entropy e regressione. Con un'<b>uscita-insieme</b> ci si deve chiedere <i>quante</i> scatole ci sono e <i>quale predizione va con quale oggetto</i>.</p>
<div class="box k"><b>Da saper fare</b><p>Questo è il problema di <b>assegnamento</b> (matching) della detection: il numero di predizioni è scelto dall'architettura (migliaia di ancore, S × S × B celle, N query), quello degli oggetti dipende dall'immagine. Prima di poter calcolare una loss bisogna decidere quali predizioni sono «positive» (assegnate a un oggetto reale) e quali «negative» (sfondo). Faster R-CNN lo fa con l'IoU fra ancore e GT, YOLO col centro dell'oggetto, DETR con l'algoritmo ungherese.</p></div>
"""), printed=P(5))

s(6, "What Supervision Does Each Task Require?", R("""
<p>Tre pannelli con la <b>supervisione</b> (le annotazioni) richiesta da ogni compito:</p>
<ul>
<li><b>Detection</b>: una scatola e un'etichetta di classe per oggetto, D<sub>det</sub> = {(x<sub>n</sub>, {(b<sub>i</sub>, c<sub>i</sub>)}<sub>i=1..N<sub>n</sub></sub>)}<sub>n=1..M</sub>. Il numero di oggetti N<sub>n</sub> cambia da immagine a immagine.</li>
<li><b>Semantic seg.</b>: una classe per pixel, nessuna identità d'oggetto: D<sub>sem</sub> = {(x<sub>n</sub>, y<sub>n</sub>)}.</li>
<li><b>Instance seg.</b>: una maschera per oggetto, ciascuna con la sua classe: D<sub>inst</sub> = {(x<sub>n</sub>, {(b<sub>i</sub>, c<sub>i</sub>, M<sub>i</sub>)})}.</li>
</ul>
<p>La <b>panottica</b> combina i due approcci: classe per pixel per lo «stuff», maschera per istanza per le «things». Conclusione della slide: compiti diversi richiedono <b>strutture di annotazione</b> diverse, e annotare costa molto di più passando da scatole a maschere.</p>
"""), printed=P(6))

s(7, "Major Datasets for Detection and Segmentation", R("""
<p>Quattro dataset standard (le immagini mostrano un esempio con le sue annotazioni):</p>
<ul>
<li><b>PASCAL VOC</b> (Everingham et al. 2010): 20 classi; scatole per ogni immagine, maschere solo per un sottoinsieme annotato.</li>
<li><b>MS COCO</b> (Lin et al. 2014): 80 classi di «thing» (più 53 di «stuff» per la panottica); scatole, maschere d'istanza e panottiche. È il dataset su cui si misura la mAP@[.5:.95].</li>
<li><b>Cityscapes</b> (Cordts et al. 2016): scene urbane, 19 classi di valutazione; etichette semantiche dense e d'istanza.</li>
<li><b>ADE20K</b> (Zhou et al. 2017): 150 classi nel benchmark; maschere semantiche dense (più istanze).</li>
</ul>
<p>Servono a sapere su che cosa sono addestrati i modelli delle slide dopo: i detector su COCO/VOC, i segmentatori semantici su Cityscapes/ADE20K (SegFormer e SETR nella slide 48 sono valutati su ADE20K).</p>
"""), printed=P(7))

# ===================== OBJECT DETECTION =====================

s(8, "Object Detection (divisoria)", """
<p>Sottotitolo: «From region proposals to direct and set-based prediction», cioè dalle <b>proposte di regioni</b> alla predizione <b>diretta</b> (YOLO, SSD, FCOS) e <b>per insiemi</b> (DETR).</p>
""", kind='div', sec=("l19-det", "Object detection", "slide 8–37"))

s(9, "Object Detection: Problem Definition", R("""
<p>La detection predice un <b>insieme di scatole</b>, ognuna con una classe e un <b>punteggio di confidenza</b>. L'uscita è un insieme di lunghezza variabile: la rete deve decidere <i>quanti</i> oggetti ci sono e <i>dove</i>. Figura: un risultato qualitativo di Faster R-CNN (cavallo, persone, auto, con scatole etichettate «person: 0.988» ecc.).</p>
<p>Due grandi famiglie:</p>
<ul>
<li><b>Two-stage</b>: prima si <b>propongono</b> regioni candidate, poi le si classifica e si raffinano;</li>
<li><b>One-stage</b>: si predicono le scatole direttamente, in modo denso, in un solo passaggio.</li>
</ul>
<div class="box b"><b>Dal libro · {C50}, § 50.4.1</b><p>Il libro descrive la stessa struttura in tre passi: (1) si <b>propone</b> un insieme di scatole candidate; (2) si fa girare un <b>classificatore</b> sul contenuto di ciascuna; (3) si <b>post-elaborano</b> le scatole per togliere le detection ridondanti (NMS). Le due famiglie delle slide differiscono nel passo 1: le two-stage lo fanno in modo esplicito, le one-stage lo fondono con il 2 predicendo scatole e classi insieme. Il libro cita YOLO come esempio dell'approccio «globale» (§ 50.4.1.4), meno preciso dei metodi a scansione ma più efficiente.</p></div>
"""), printed=P(9))

s(10, "Object Detection: One-Stage vs. Two-Stage", R("""
<p>Figura (adattata da Raza et al. 2025) con due percorsi sulla foto di un gatto:</p>
<ul>
<li><b>Two-stage</b> (riquadro blu): feature map → <b>Region Proposal Network</b> (oggettività + regressione della scatola) → ritagli delle regioni → <b>classificatore e regressore</b> che raffinano.</li>
<li><b>One-stage</b> (riquadro rosso tratteggiato): feature map → un'unica rete di detection che fa <b>classificazione e regressione delle scatole</b> insieme, su tutte le posizioni.</li>
</ul>
<p>Entrambe risolvono lo <b>stesso problema di predizione di insiemi</b>: differiscono solo per il fatto che le regioni candidate vengano proposte esplicitamente prima della classificazione. La <b>supervisione</b> è la stessa: un insieme di coppie (scatola, classe) per immagine.</p>
<div class="box x"><b>Approfondimento</b><p>Regola pratica storica: le two-stage erano più accurate, specie su oggetti piccoli, e più lente; le one-stage più veloci. Il divario si è chiuso: con la focal loss (RetinaNet), le feature pyramid e le teste anchor-free le one-stage raggiungono la stessa accuratezza (vedi slide 37).</p></div>
"""), printed=P(10))

s(11, "Sliding Window Detection", R("""
<p>I primi detector usavano la <b>finestra scorrevole</b>: si fa scorrere sull'immagine una finestra di dimensione fissa e si classifica ogni finestra come «oggetto» o «sfondo». Per oggetti di taglia diversa si ripete l'operazione a più scale (<b>piramide d'immagini</b>, vedi <a href="#L6">L6</a>). Figura (Nieto et al. 2014): a sinistra la scansione a forza bruta, a destra una versione che adatta la taglia della finestra alla prospettiva.</p>
<p>Il problema: <b>troppe finestre</b>, dell'ordine di 10<sup>5</sup>–10<sup>6</sup> per immagine, quasi tutte sfondo. Il classificatore dev'essere economicissimo, oppure bisogna scartare in fretta quasi tutte le finestre (cascata, slide seguente).</p>
<div class="box b"><b>Dal libro · {C50}, § 50.4.1.1</b><p>È l'«Algorithm 50.1» del libro: si fa scorrere un classificatore binario (oggetto contro sfondo) su una piramide multi-scala. L'invarianza alla traslazione e alla scala non sta nel classificatore ma nel <b>meccanismo che propone le scatole</b>: provando ogni posizione e ogni scala, si aggira il problema. Si può aggiungere l'invarianza alla rotazione proponendo anche scatole ruotate. Il costo è l'enorme numero di applicazioni del classificatore.</p></div>
"""), printed=P(11))

s(12, "Object Detection Before Deep Learning: Viola-Jones", R("""
<p>Il primo detector in tempo reale (volti, 2001). Ingredienti:</p>
<ul>
<li><b>Feature di Haar</b>: rettangoli adiacenti, uno «bianco» e uno «nero», di cui si confrontano le somme di intensità dei pixel (esempio: la zona scura degli occhi contro le guance chiare). Si calcolano in tempo costante con l'<b>immagine integrale</b> (slide seguente).</li>
<li><b>AdaBoost</b>: sceglie da un enorme insieme fisso un piccolo numero di <b>classificatori deboli</b> (una feature di Haar + una soglia ciascuno) e impara un peso per ciascuno.</li>
<li><b>Supervisione</b>: patch di volti / non volti etichettate; <b>nessuna regressione della scatola</b>.</li>
<li><b>Cascata</b>: gli stadi sono concatenati; i primi sono economici e scartano subito quasi tutte le finestre di sfondo, solo le sopravvissute arrivano agli stadi più severi e costosi.</li>
</ul>
<p>Figura: due feature di Haar (una a due rettangoli sulla zona occhi/guance, una a tre rettangoli sul naso) sovrapposte a un volto in bassa risoluzione.</p>
<div class="box b"><b>Dal libro · {C50}, § 50.4.1.3</b><p>Il libro presenta la cascata come il caso estremo di «cerca l'ago nel pagliaio»: una sequenza di classificatori di costo e precisione crescenti, così che la potenza di calcolo vada dove l'oggetto è probabile. La finestra scorrevole (uno stadio solo) e la selective search (due stadi) ne sono casi particolari. Cita anche Fleuret e Geman come lavoro parallelo e mostra la mappa del carico di calcolo per ogni punto dell'immagine (fig. 50.16).</p></div>
"""), printed=P(12))

s(13, "Viola-Jones: A Haar Feature", R("""
<p>Quattro passi, da sinistra a destra nella figura:</p>
<ol>
<li><b>Feature di Haar</b>: due rettangoli adiacenti, uno bianco e uno nero.</li>
<li><b>Somma sul rettangolo</b> con l'immagine integrale: S<sub>R</sub> = II(D) − II(B) − II(C) + II(A), dove A, B, C, D sono i quattro angoli del rettangolo.</li>
<li><b>Risposta della feature</b>: f = S<sub>bianco</sub> − S<sub>nero</sub>.</li>
<li><b>Classificatore debole</b>: h(x) = 1[p f(x) &gt; p θ], con θ soglia appresa e p ∈ {−1, +1} la <b>polarità</b> (che cambia il verso della disuguaglianza). h(x) ∈ {0, 1}.</li>
</ol>
<p>L'<b>immagine integrale</b> è la somma cumulativa dei pixel: II(x, y) = ∑<sub>x′≤x, y′≤y</sub> I(x′, y′), calcolata una volta per immagine. Con quella, qualunque somma su un rettangolo costa 4 accessi, qualunque sia la sua taglia.</p>
<div class="box k"><b>Da saper fare</b><p>Verificare la formula dei quattro angoli: II(D) è la somma di tutto ciò che sta sopra e a sinistra di D; togliendo II(B) e II(C) si tolgono due fasce, ma la zona sopra-sinistra di A è stata tolta due volte, quindi si aggiunge II(A). Esempio: su un'immagine di soli 1 il rettangolo di 3 × 4 pixel vale 12 sia contando i pixel sia con 4 accessi. Questa è la stessa idea della <i>summed-area table</i> delle texture.</p></div>
"""), printed=P(13))

s(14, "Two-Stage Detectors", R("""
<p>Le two-stage propongono un insieme <b>sparso</b> di regioni candidate, poi classificano e raffinano ciascuna. Ogni modello risolve un limite del precedente (tabella):</p>
<ul>
<li><b>R-CNN</b>: proposte con Selective Search; addestramento in <b>3 passi separati</b>.</li>
<li><b>Fast R-CNN</b>: proposte ancora con Selective Search; addestramento in <b>1 passo congiunto</b>; risolve il doppio problema di «una passata della CNN per ogni regione» e degli SVM separati.</li>
<li><b>Faster R-CNN</b>: proposte con una <b>RPN appresa</b>; addestramento in 4 passi nell'articolo originale, in 1 nelle implementazioni moderne; risolve le proposte esterne e fisse.</li>
</ul>
<p>La slide dopo introduce le proposte, poi i tre modelli in ordine.</p>
"""), printed=P(14))

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
