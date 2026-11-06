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
