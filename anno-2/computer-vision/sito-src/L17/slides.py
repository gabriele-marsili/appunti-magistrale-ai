VB = 'https://visionbook.mit.edu/'
def L(slug, txt): return f'<a href="{VB}{slug}" target="_blank">{txt}</a>'
C24 = L('convolutional_neural_nets.html', 'cap. 24')
C26 = L('transformers.html', 'cap. 26')
C21 = L('upsamplig_downsampling_2.html', 'cap. 21')
C50 = L('object_recognition_v3.html', 'cap. 50')
C43 = L('3d_learning.html', 'cap. 43')
C48 = L('optical_flow.html', 'cap. 48')
C49 = L('motion_estimation.html', 'cap. 49')
C12 = L('neural_nets.html', 'cap. 12')
def P(n): return f' <em>· pag. {n}/43</em>'
def R(t): return t.replace('{C24}', C24).replace('{C26}', C26).replace('{C21}', C21).replace('{C50}', C50).replace('{C43}', C43).replace('{C48}', C48).replace('{C49}', C49).replace('{C12}', C12)

# ===================== INTRODUZIONE =====================

s(1, "ViT, U-Net, Dense Prediction: copertina", """
<p>Lezione del 22 ottobre 2026, tenuta da <b>Donald Shenaj</b> (non dal prof. Carta). Riprende le CNN di <a href="#L15">L15</a> e cambia il tipo di uscita: non più <b>un'etichetta per l'immagine</b> ma <b>una predizione per ogni pixel</b> (dense prediction). Nella seconda metà arriva il <b>Vision Transformer</b> (ViT), la prima architettura del corso che non è una CNN.</p>
<p>Il PDF ha 43 pagine e il footer stampa «n / 43» con n = numero di pagina del PDF, copertina compresa (quindi qui pagina e slide coincidono). La pag. 43 non è una slide: è un indice a miniature delle pagine 1–42.</p>
""", sec=("l17-intro", "Introduzione", "slide 1–2"), printed=P(1))

s(2, "Lecture Outline", """
<p>Tre parti (sono anche i segnalibri del PDF):</p>
<ol>
<li><b>Dense Prediction Tasks</b> (slide 3–10): quali compiti chiedono un'uscita per pixel e perché una CNN da classificazione non basta.</li>
<li><b>Encoder-Decoder Architectures</b> (slide 11–23): convoluzione 1×1, FCN, U-Net, operatori di upsampling, due casi di studio (MiDaS per la profondità, RAFT per il flusso ottico), loss e metriche.</li>
<li><b>Vision Transformers</b> (slide 24–42): patch embedding, codifiche posizionali, self-attention, blocchi, normalizzazioni, cosa impara un ViT, confronto con le CNN, uso come encoder per la predizione densa; poi sintesi e riferimenti.</li>
</ol>
""", printed=P(2))

# ===================== DENSE PREDICTION TASKS =====================

s(3, "Beyond Classification: Dense Prediction Tasks", """
<p>La <b>classificazione</b> dà un'etichetta per tutta l'immagine. Molti compiti di visione chiedono invece <b>una predizione per pixel</b>:</p>
<ul>
<li><b>segmentazione semantica</b>: una classe per ogni pixel (strada, auto, cielo…);</li>
<li><b>segmentazione d'istanza</b>: classe e <b>identità dell'oggetto</b> per ogni pixel che appartiene a un oggetto (auto n. 1, auto n. 2);</li>
<li><b>segmentazione panottica</b>: le due insieme, etichette semantiche per lo «<b>stuff</b>» (regioni amorfe e non numerabili: cielo, strada, erba) e ID d'istanza per le «<b>things</b>» (oggetti numerabili: persone, auto);</li>
<li><b>stima della profondità</b>: un valore continuo di profondità per pixel;</li>
<li><b>flusso ottico</b>: un vettore di moto 2D per pixel;</li>
<li><b>keypoint / pose</b>: una mappa di verosimiglianza (heatmap) per pixel, una per articolazione.</li>
</ul>
<p><b>Figura</b>: quattro esempi affiancati: segmentazione di una scena urbana (Cityscapes), mappa di profondità (MiDaS), flusso ottico codificato a colori (MPI-Sintel), scheletri di persone (OpenPose).</p>
<div class="box b"><b>Dal libro · {C50}, § 50.5–50.6, e {C24}, § 24.1</b><p>Il capitolo 50 presenta la segmentazione come passo successivo alla localizzazione con bounding box: molte cose (nebbia, cielo, oggetti filiformi) non stanno bene in un rettangolo, quindi si classifica ogni pixel (§ 50.5). La segmentazione semantica però <b>non sa contare</b>: due auto a contatto diventano un'unica regione «auto»; la segmentazione d'istanza (§ 50.6) restituisce una maschera per ogni oggetto. Già nel § 24.1 il libro insiste che la vera forza delle CNN è mappare un'immagine in un'<b>immagine</b> di predizioni con la stessa topologia dell'ingresso. La panottica non è nel visionbook: Szeliski § 6.4.3.</p></div>
""".replace('{C50}', C50).replace('{C24}', C24), sec=("l17-task", "Compiti di predizione densa", "slide 3–10"), printed=P(3))

s(4, "Task: Semantic / Instance / Panoptic Segmentation", """
<ul>
<li><b>Ingresso</b>: un'immagine RGB, H × W × 3.</li>
<li><b>Ground truth</b> (GT, l'annotazione corretta):
<ul><li>semantica: una mappa H × W con un <b>id di classe</b> per pixel;</li>
<li>istanza: in più un <b>id d'istanza</b> per pixel, solo per le «things» numerabili;</li>
<li>panottica: unisce le due, così ogni pixel ha una classe (stuff o thing) e, se è una thing, anche un'istanza.</li></ul></li>
<li>Un modello addestrato (a destra) dovrebbe riprodurre la GT (al centro).</li>
</ul>
<p><b>Figura</b> (Zhao et al. 2017, PSPNet, fig. 8, dataset Cityscapes): foto di una strada, la sua GT con i colori convenzionali di Cityscapes (strada viola, marciapiede rosa, vegetazione verde, auto blu) e la predizione della rete, quasi identica alla GT tranne ai bordi e sugli oggetti sottili (pali, cartelli).</p>
<div class="box k"><b>Da saper fare</b>Spiegare con un esempio la differenza fra le tre segmentazioni: in una foto con tre persone su un prato, la semantica dà «persona» e «erba»; l'istanza dà tre maschere distinte per le persone e ignora l'erba; la panottica dà entrambe le cose.</div>
""", printed=P(4))

s(5, "Task: Monocular Depth Estimation", """
<ul>
<li><b>Ingresso</b>: una <i>sola</i> immagine RGB, H × W × 3: niente coppia stereo, niente LiDAR al momento dell'inferenza.</li>
<li><b>GT</b>: un array H × W con un valore <b>continuo</b> di profondità per pixel; qui viene da un sensore RGB-D.</li>
<li>Problema dei dati: i sensori veri coprono <b>solo una parte</b> della scena (buchi su superfici riflettenti, lontane o scure) e sensori diversi <b>non concordano sulla scala</b>.</li>
</ul>
<p><b>Figura</b> (Eigen et al. 2014, fig. 3, NYU Depth): stanza interna; GT di profondità in scala di grigi (chiaro = lontano) e predizione della rete, più sfocata ma con la disposizione giusta delle superfici.</p>
<div class="box b"><b>Dal libro · {C43}, § 43.4</b><p>Con una sola immagine la profondità assoluta è ambigua (un oggetto piccolo vicino e uno grande lontano danno la stessa immagine: vedi la stanza di Ames in <a href="#L13">L13</a>). Il libro tratta la stima come <b>regressione per pixel</b> e lista le fonti di GT (§ 43.4.1): sensori RGB-D (NYUv2, Kinect in interni), LiDAR (KITTI, da un'auto), coppie stereo, ricostruzioni multi-vista (MegaDepth, structure from motion). Per l'ambiguità di scala propone una loss «invariante di scala» (§ 43.4.2) che però, scritta senza logaritmi, toglie solo uno spostamento globale: quella vera di Eigen et al. 2014 è sui log-profondità (già segnalato in L13).</p></div>
""".replace('{C43}', C43), printed=P(5))

s(6, "Task: Optical Flow", """
<ul>
<li><b>Ingresso</b>: due frame RGB consecutivi (H × W × 3 ciascuno).</li>
<li><b>GT</b>: un array H × W × 2, un vettore di moto (u, v) per pixel: dove si è spostato quel pixel nel frame successivo.</li>
<li>Visualizzazione con la <b>ruota dei colori</b>: la <b>tinta</b> codifica la direzione, la <b>saturazione</b> l'ampiezza (bianco = fermo).</li>
<li>Una GT densa del flusso su scene reali è <b>quasi impossibile da raccogliere</b>: si addestra soprattutto su dati <b>sintetici</b> (Baker et al. 2011, Middlebury).</li>
</ul>
<p><b>Figura</b> (visionbook, fig. 48.1): due frame ℓ<sub>1</sub>, ℓ<sub>2</sub> di una strada con un'auto in movimento; il campo di flusso, quasi bianco sullo sfondo (la camera è quasi ferma) e verde sull'auto; a destra la ruota dei colori con gli assi u e v e le frecce che indicano la direzione corrispondente a ogni tinta.</p>
<div class="box b"><b>Dal libro · {C48}, § 48.2</b><p>Il flusso ottico è un'<b>approssimazione</b> del campo di moto 2D (la proiezione del moto 3D), misurata dallo spostamento della luminosità. La definizione presuppone una corrispondenza uno a uno fra i due frame: salta dove un oggetto compare o viene occluso, e dove un solo moto non spiega i cambi di luminosità (trasparenze, luce che si sposta). Inoltre in una regione senza texture o lungo un bordo rettilineo il moto è ambiguo (problema dell'apertura, § 48.2.2). La codifica a colori della figura è quella introdotta da Baker et al.</p></div>
""".replace('{C48}', C48), printed=P(6))

s(7, "Task: Keypoint / Pose Estimation", """
<ul>
<li><b>Ingresso</b>: un'immagine RGB H × W × 3 con una o più persone.</li>
<li><b>GT</b>: K coordinate di keypoint (x<sub>k</sub>, y<sub>k</sub>) per persona (polsi, gomiti, ginocchia…), annotate nello stesso formato in cui è disegnata l'uscita a destra.</li>
<li>In pratica si addestra su <b>K heatmap</b> per pixel, una per articolazione, con un picco (di solito una gaussiana) nella posizione vera; la predizione si legge come argmax di ogni heatmap. Così un problema di regressione di coordinate diventa un problema denso.</li>
</ul>
<p><b>Figura</b> (Cao et al. 2017, OpenPose, fig. 2): due ballerini; a destra lo scheletro predetto, con i segmenti colorati che uniscono le articolazioni di ciascuna persona.</p>
<div class="box x"><b>Approfondimento</b>Con più persone non basta trovare i keypoint: bisogna anche capire quali appartengono alla stessa persona. OpenPose predice, oltre alle heatmap, dei «part affinity field» (campi vettoriali lungo gli arti) che servono ad assemblare gli scheletri. Prince § 11.5.3 descrive le reti stacked hourglass usate per la pose: una heatmap per articolazione, posizione stimata = massimo della heatmap.</div>
""", printed=P(7))

s(8, "Dense Prediction: Same Shape, Different Content", """
<p><b>Vincolo comune</b>: ogni compito produce un array circa alla <b>risoluzione dell'ingresso</b>; cambia completamente cosa contiene ogni pixel:</p>
<table>
<tr><th>Compito</th><th>Uscita per pixel</th><th>Tipo</th></tr>
<tr><td>segmentazione semantica</td><td>C punteggi di classe</td><td>discreto (softmax)</td></tr>
<tr><td>profondità</td><td>1 valore</td><td>continuo, &gt; 0</td></tr>
<tr><td>flusso ottico</td><td>vettore 2D (u, v)</td><td>continuo, con segno</td></tr>
<tr><td>pose / keypoint</td><td>K mappe di verosimiglianza</td><td>continuo, con picchi</td></tr>
</table>
<p><b>Conseguenza</b>: per quasi tutti i compiti si può usare la <b>stessa struttura encoder-decoder</b>; cambiano solo la <b>testa</b> (task head: una conv 1×1 al numero giusto di canali d'uscita: C, 1, 2 o K) e la <b>loss</b>.</p>
<p>Il tipo d'uscita decide anche l'attivazione finale: softmax per pixel per le classi; per la profondità un'uscita positiva (per esempio esponenziale o softplus, oppure si predice log-profondità o disparità); per il flusso un'uscita lineare con segno.</p>
""", printed=P(8))

s(9, "Why Plain CNNs Are Not Enough", """
<ul>
<li>Una CNN da classificazione (ResNet, VGG) è un <b>imbuto</b>: conv + pooling o stride <b>riducono</b> la risoluzione spaziale e <b>aumentano</b> i canali.
<span class="f">224 × 224 × 3 → ⋯ → 7 × 7 × 2048 → 1 vettore</span>
(i numeri sono quelli di ResNet-50: fattore di riduzione 32, poi global average pooling).</li>
<li>Questo compromesso (meno risoluzione, più semantica e campo recettivo) risponde bene a «<b>cosa</b> c'è nell'immagine» e male a «<b>cosa c'è dove</b>».</li>
<li>All'ultimo strato il dettaglio spaziale fine (bordi, contorni) è perso.</li>
<li>La predizione densa ha bisogno di una <b>strada per risalire</b> alla risoluzione dell'ingresso.</li>
</ul>
<div class="box b"><b>Dal libro · {C24}, § 24.8</b><p>La prima soluzione del libro è la più semplice: <b>sottocampionare meno</b> e togliere il global pooling, così l'ultimo strato è ancora una mappa con risoluzione spaziale e si fa un argmax per pixel (fig. 24.27). Funziona, ma tenere mappe grandi in tutti gli strati costa memoria e calcolo, e senza sottocampionamento il campo recettivo cresce lentamente. Da qui l'encoder-decoder (slide 11). Ripasso da <a href="#L15">L15</a>: lo stride è un sottocampionamento senza anti-aliasing (fig. 24.8), quindi l'informazione ad alta frequenza non è solo «nascosta» ma in parte distrutta.</p></div>
""".replace('{C24}', C24), printed=P(9))

s(10, "Shape Arithmetic: Conv Output Size &amp; Receptive Field", """
<p><b>Dimensione dell'uscita</b> (kernel k, stride s, padding p, dilatazione d):</p>
<span class="f">H<sub>out</sub> = ⌊ (H<sub>in</sub> + 2p − d(k − 1) − 1) / s ⌋ + 1</span>
<p>Con d = 1 diventa la formula di L15, ⌊(H<sub>in</sub> + 2p − k)/s⌋ + 1. <b>Figura</b> a sinistra: H<sub>in</sub> = 7 con padding p = 1 (celle tratteggiate ai bordi), k = 3, s = 2: (7 + 2 − 2 − 1)/2 + 1 = 3 + 1 = <b>4</b> uscite. Giusto.</p>
<p><b>Campo recettivo</b> dopo L strati (kernel k<sub>l</sub>, stride s<sub>l</sub>):</p>
<span class="f">r<sub>L</sub> = r<sub>0</sub> + ∑<sub>l=1</sub><sup>L</sup> (k<sub>l</sub> − 1) ∏<sub>i&lt;l</sub> s<sub>i</sub>,   r<sub>0</sub> = 1</span>
<p>Ogni strato allarga il campo di (k<sub>l</sub> − 1) celle <i>del proprio ingresso</i>, e una cella del proprio ingresso vale ∏<sub>i&lt;l</sub> s<sub>i</sub> pixel dell'immagine: ecco perché lo stride fa crescere il campo molto più in fretta. <b>Figura</b> a destra: due strati k = 3, s = 1: r = 1 + 2 + 2 = <b>5</b>, «1 cell sees 5 input cells» (la cella dello strato 2 vede 3 celle dello strato 1, che vedono 5 celle d'ingresso). Giusto.</p>
<ul>
<li><b>Dilatazione</b>: con d &gt; 1 il kernel effettivo è k<sub>eff</sub> = d(k − 1) + 1, senza parametri in più e senza sottocampionare (la convoluzione «atrous» di DeepLab). Nella formula del campo recettivo si usa k<sub>eff</sub> al posto di k.</li>
<li><b>Sottocampionare</b> dà contesto ma costa risoluzione spaziale.</li>
</ul>
<p>Il compromesso chiave della predizione densa: dare a ogni pixel abbastanza <b>contesto globale</b> senza perdere il <b>dettaglio spaziale</b> che serve a localizzarlo bene.</p>
<div class="box k"><b>Da saper fare</b>Calcolare a mano dimensioni e campo recettivo. Esempi: conv 3×3 «valid» (p = 0, s = 1) toglie 2 pixel: 572 → 570 (U-Net, slide 16); max pool 2×2 con s = 2 dimezza: 568 → 284. Campo recettivo di conv 3×3 s = 2 seguita da conv 3×3 s = 1: r = 1 + 2·1 + 2·2 = 7. Tre conv 3×3 con dilatazione 1, 2, 4: k<sub>eff</sub> = 3, 5, 9, quindi r = 1 + 2 + 4 + 8 = 15 (è il 15 × 15 segnalato come refuso del libro in L15).</div>
<div class="box b"><b>Dal libro · {C24}, § 24.7</b><p>Il libro non dà la formula chiusa ma le sue tre regole: comporre filtri allarga il supporto; le non linearità puntuali non cambiano il campo recettivo; dopo un sottocampionamento di fattore s il campo cresce s volte più in fretta. Un global average pooling dà subito campo recettivo pari a tutta l'immagine. Attenzione al campo recettivo <i>effettivo</i>: il peso dei pixel dentro il campo teorico decresce dal centro verso i bordi, quindi il contesto davvero usato è più piccolo.</p></div>
""".replace('{C24}', C24), printed=P(10))

# ===================== ENCODER-DECODER =====================

s(11, "Encoder-Decoder Architectures for Dense Prediction", """
<ul>
<li><b>Encoder</b>: una backbone in stile classificazione (spesso pre-addestrata su ImageNet) che sottocampiona passo dopo passo e costruisce feature <b>semantiche</b> ricche.</li>
<li><b>Decoder</b>: sovracampiona passo dopo passo quelle feature fino alla risoluzione d'ingresso.</li>
<li><b>Skip connection</b>: fondono nel decoder le feature dell'encoder ad <b>alta risoluzione e basso livello</b>, per recuperare il dettaglio spaziale fine.</li>
<li><b>Testa</b>: una conv 1×1 porta le feature del decoder all'uscita voluta (logit di classe, profondità…).</li>
</ul>
<p><b>Figura</b> (Badrinarayanan et al. 2015, SegNet): foto di strada → encoder convoluzionale (blocchi conv + BatchNorm + ReLU, pooling) → decoder speculare (upsampling) → softmax → segmentazione. Una freccia «pooling indices» collega encoder e decoder: SegNet sovracampiona riusando le <b>posizioni dei massimi</b> del max pooling (max unpooling).</p>
<div class="box b"><b>Dal libro · {C24}, § 24.11.1, e {C50}, § 50.5</b><p>Encoder e decoder sono le versioni apprese delle piramidi di <b>analisi</b> e <b>sintesi</b> del cap. 23 (<a href="#L6">L6</a>). Il libro dà due vantaggi dell'encoder-decoder rispetto a una CNN che non sottocampiona (§ 24.8): (1) mappe interne più piccole, quindi meno memoria e calcolo; (2) un <b>collo di bottiglia informativo</b>: la rappresentazione centrale è piccola e costringe la rete ad astrarre (fig. 24.30, encoder-decoder per la segmentazione). Nel § 50.5 l'encoder-decoder è la struttura «generica» per la segmentazione semantica (fig. 50.22), addestrata con la cross-entropy per pixel.</p></div>
""".replace('{C24}', C24).replace('{C50}', C50), sec=("l17-encdec", "Architetture encoder-decoder", "slide 11–23"), printed=P(11))

s(12, "What Is a 1 × 1 Convolution?", """
<p>È la solita convoluzione con k = 1: l'uscita in (h, w) dipende <b>solo</b> dall'ingresso in (h, w).</p>
<ul>
<li>una conv 3×3 mescola un intorno spaziale 3×3 (e tutti i canali);</li>
<li>una conv 1×1 mescola <b>solo i canali</b> di quel pixel:
<span class="f">y<sub>h,w</sub> = W x<sub>h,w</sub> + b,   W ∈ ℝ<sup>C<sub>out</sub>×C<sub>in</sub></sup></span>
cioè lo stesso strato lineare (fully connected) applicato al vettore dei canali in ogni posizione.</li>
</ul>
<p><b>A cosa serve</b>: cambiare il numero di canali (bottleneck o proiezione, come in Inception e nei blocchi bottleneck di ResNet, <a href="#L15">L15</a>) oppure fare la <b>testa finale</b> (feature → logit di classe, profondità, flusso) senza toccare H e W.</p>
<p><b>Figura</b>: una griglia di feature con un intorno 3×3 evidenziato che produce un pixel d'uscita (conv 3×3), e un solo pixel evidenziato che ne produce uno (conv 1×1).</p>
<div class="box k"><b>Da saper fare</b>Contare i parametri: C<sub>in</sub>·C<sub>out</sub> + C<sub>out</sub>. Per la testa di segmentazione da 64 canali a 21 classi: 64·21 + 21 = 1.365. Una conv 3×3 con gli stessi canali ne ha 9 volte tanti pesi.</div>
<div class="box b"><b>Dal libro · Prince § 10.4.3</b><p>Prince la introduce come il modo di cambiare il numero di canali senza toccare la risoluzione: i pesi hanno forma 1 × 1 × C<sub>i</sub> × C<sub>o</sub> e, con bias e attivazione, è <b>la stessa rete fully connected applicata ai canali in ogni posizione</b>. Il visionbook ci arriva nel {C26}, § 26.9.2: le proiezioni query, key, value di un transformer sono proprio convoluzioni 1×1 (slide 37).</p></div>
""".replace('{C26}', C26), printed=P(12))

s(13, "“Fully Connected Layers”", """
<p><b>Figura</b>: un post di Yann LeCun (aprile 2015). In sostanza: nelle reti convoluzionali non esistono veri strati «fully connected», ma solo convoluzioni con kernel 1×1 e una tabella di connessioni completa. Una ConvNet non ha bisogno di un ingresso di dimensione fissa: la si addestra su immagini che producono un solo vettore d'uscita (estensione spaziale 1×1), e poi la si applica a immagini più grandi; invece di un vettore si ottiene una <b>mappa spaziale</b> di vettori, ciascuno calcolato su una finestra diversa dell'ingresso.</p>
<p>Perché vale: uno strato denso che riceve una mappa 7×7×512 e produce 4096 uscite è identico a una conv con kernel <b>7×7</b> (e 4096 filtri) applicata in un solo punto; gli strati densi successivi (4096 → 4096 → classi) sono conv <b>1×1</b>. Su un'immagine più grande la stessa rete «scorre» e dà una mappa di punteggi. È l'idea su cui si basa la FCN (slide 14–15).</p>
<div class="box b"><b>Dal libro · {C24}, § 24.9</b><p>Il libro lo dimostra in generale: una CNN fatta solo di convoluzioni e non linearità puntuali è un <b>filtro non lineare scorrevole</b>. Senza non linearità sarebbe una sola grande convoluzione (la composizione di convoluzioni è una convoluzione, <a href="#L3">L3</a>); le non linearità puntuali non mescolano pixel diversi, quindi la proprietà «stessa funzione applicata in modo indipendente a ogni patch» resta (fig. 24.28). Il libro chiama questa rete <b>fully convolutional network</b>.</p></div>
""".replace('{C24}', C24), printed=P(13))

s(14, "Fully Convolutional Networks (FCN)", """
<p><b>Figura</b> (Long, Shelhamer e Darrell 2015, FCN, fig. 1): una foto di un gatto entra in una rete tipo AlexNet in cui tutti gli strati sono convoluzionali (canali 96, 256, 384, 384, 256, poi 4096, 4096 e 21: gli ex strati densi diventati conv). L'uscita non è un vettore ma un blocco di <b>21 mappe</b> (le 20 classi di PASCAL VOC più lo sfondo); sovracampionata, dà la segmentazione «pixelwise prediction» del gatto. Le frecce indicano che sia l'inferenza (forward) sia l'apprendimento (backward) avvengono sull'intera immagine, end-to-end.</p>
<p>Messaggio: lo stesso classificatore pre-addestrato su ImageNet, «convolutionalizzato», diventa un segmentatore; si fa poi fine-tuning con la cross-entropy per pixel.</p>
""", printed=P(14))

s(15, "Fully Convolutional Networks (FCN)", """
<ul>
<li><b>Idea chiave</b>: sostituire gli strati FC del classificatore con le convoluzioni equivalenti (slide 13) ⇒ la rete accetta ingressi di <b>dimensione variabile</b> e produce una <b>mappa di punteggi</b> spaziale, grossolana.</li>
<li>Una <b>convoluzione trasposta</b> inizializzata come <b>interpolazione bilineare</b> riporta la mappa alla risoluzione d'ingresso; ma sovracampionare di <b>32×</b> una predizione già ridotta di 32 volte non può recuperare il dettaglio perso.</li>
<li><b>FCN-8s</b>: fonde progressivamente le mappe di punteggio da pool5, pool4 e pool3 prima del sovracampionamento finale, combinando la semantica profonda col dettaglio spaziale degli strati bassi: uno dei primi usi delle <b>skip connection</b> per la predizione densa.</li>
</ul>
<p><b>Figura</b> (Long et al. 2015): la piramide image → pool1 … pool5 (griglie sempre più grossolane: pool3 ha stride 8, pool4 16, pool5 32).</p>
<ul>
<li><b>FCN-32s</b>: predizione da pool5 (dopo conv6–7), sovracampionata 32× in un colpo.</li>
<li><b>FCN-16s</b>: predizione di pool5 sovracampionata 2×, <b>sommata</b> alla predizione calcolata da pool4 (una conv 1×1 su pool4), poi sovracampionata 16×.</li>
<li><b>FCN-8s</b>: il risultato di prima sovracampionato 2× e sommato alla predizione da pool3, poi 8×.</li>
</ul>
<p>I contorni migliorano passando da 32s a 16s a 8s. Nota: nella FCN le skip si fondono per <b>somma</b> di mappe di punteggio; nella U-Net per <b>concatenazione</b> di feature.</p>
<div class="box k"><b>Da saper fare</b>Con ingresso 224 × 224: pool5 è 7 × 7, pool4 14 × 14, pool3 28 × 28. FCN-32s sovracampiona 7 → 224 (×32); FCN-16s fa 7 → 14, somma a pool4, poi 14 → 224 (×16); FCN-8s fa 14 → 28, somma a pool3, poi 28 → 224 (×8).</div>
<div class="box b"><b>Dal libro · {C24}, § 24.2.5, e {C21}, § 21.4</b><p>Il libro descrive lo strato di upsampling come l'analogo della strided conv: invece di «convolvi poi sottocampiona», <b>prima dilata il segnale</b> inserendo zeri fra i campioni, <b>poi convolvi</b> (eq. 24.7); a volte si chiama UpConv o «deconvolution layer», ma in elaborazione dei segnali deconvoluzione vuol dire invertire una convoluzione, un'altra cosa. È esattamente l'upsampling del cap. 21 (<a href="#L6">L6</a>): espansione con zeri (§ 21.4.3, la trasposta della decimazione) seguita da un filtro di interpolazione; per fattore 2 l'interpolazione lineare è il filtro [1/2, 1, 1/2] (§ 21.4.4–21.4.5). Inizializzare la trasposta «a bilineare» vuol dire partire da questo filtro e lasciarlo imparare.</p></div>
""".replace('{C24}', C24).replace('{C21}', C21), printed=P(15))

s(16, "U-Net: Backbone for Semantic Segmentation", """
<ul>
<li>Encoder-decoder classico <b>con skip connection</b>.</li>
<li>Proposta in origine per la segmentazione <b>biomedica</b> (cellule, membrane al microscopio), con pochissime immagini di training.</li>
<li>Il <b>percorso di contrazione</b> (sinistra) costruisce feature semantiche; il <b>percorso di espansione</b> (destra) recupera la risoluzione spaziale.</li>
<li>È diventata una backbone generica per la predizione densa, ben oltre il dominio originale (profondità, restauro di immagini, modelli di diffusione).</li>
</ul>
<p><b>Figura</b> (Ronneberger et al. 2015, U-Net, fig. 1). Encoder, dall'alto: tile d'ingresso 572 × 572 a 1 canale → conv 3×3 → 570², 64 canali → 568², 64 → max pool → 284² → 282², 128 → 280², 128 → pool → 140² → 138², 256 → 136², 256 → pool → 68² → 66², 512 → 64², 512 → pool → 32² → 30², 1024 → 28², 1024 (fondo della U). Decoder: up-conv 2×2 → 56², 512 canali, concatenati con i 512 dell'encoder ritagliati da 64² a 56² (blocchi bianchi + blu) → 54² → 52², 512 → up → 104², concatenato → 102² → 100², 256 → up → 200² → 198² → 196², 128 → up → 392² → 390² → 388², 64 → conv 1×1 → <b>388 × 388 × 2</b> (mappa di segmentazione a 2 classi). Frecce grigie «copy and crop», rosse max pool 2×2, verdi up-conv 2×2, turchese conv 1×1. Ho verificato tutte le dimensioni: sono coerenti.</p>
<div class="box k"><b>Da saper fare</b>Rifare la catena delle dimensioni: ogni conv 3×3 senza padding toglie 2 pixel, ogni max pool dimezza, ogni up-conv 2×2 con stride 2 raddoppia ((H − 1)·2 + 2 = 2H). L'uscita (388) è più piccola dell'ingresso (572) perché le conv sono «valid»: per segmentare un'immagine grande la si divide in tile sovrapposte (overlap-tile) e si riflette l'immagine ai bordi. I ritagli delle skip: 64 → 56, 136 → 104, 280 → 200, 568 → 392. Le implementazioni moderne usano padding 1 e allora uscita = ingresso, senza ritagli (Prince § 11.5.3).</div>
<div class="box b"><b>Dal libro · {C24}, § 24.11.2</b><p>Il collo di bottiglia dell'encoder-decoder è utile ma rende difficile il compito del decoder, che non riesce a produrre i <b>dettagli ad alta frequenza</b>: la mappa di etichette viene grossolana. La U-Net aggiunge <b>skip connection a specchio</b> (lo strato l è collegato allo strato L − l) e le reintegra per <b>concatenazione lungo i canali</b>: si conservano i vantaggi del collo di bottiglia (memoria, astrazione) e intanto l'informazione fine passa dalle skip. Il libro nota che la U-Net somiglia alle piramidi steerable del cap. 23 (analisi che scende, sintesi che risale, collegamenti fra stadi a specchio), con la differenza che filtri e non linearità sono appresi. Collegamento con <a href="#L6">L6</a>: nella piramide laplaciana i livelli di dettaglio servono a ricostruire l'immagine in sintesi; le skip della U-Net fanno lo stesso lavoro.</p></div>
""".replace('{C24}', C24), printed=P(16))

s(17, "U-Net: Building Blocks", """
<ul>
<li><b>Percorso di contrazione</b> (encoder): ripete [conv 3×3 + ReLU] × 2, poi max pool 2×2: a ogni stadio i canali <b>raddoppiano</b> e la risoluzione si <b>dimezza</b>.</li>
<li><b>Percorso di espansione</b> (decoder): up-conv 2×2 (convoluzione trasposta, che dimezza i canali), poi <b>concatenazione</b> con la mappa dell'encoder allo stesso livello (skip connection), poi [conv 3×3 + ReLU] × 2.</li>
<li>Conv 1×1 finale → punteggi di classe per pixel.</li>
<li>Forma a «U» simmetrica, addestrata end-to-end con una loss per pixel.</li>
</ul>
<p><b>Figura</b> (dettaglio della fig. 1 di U-Net): il primo blocco dell'encoder (tile d'ingresso, 1 → 64 → 64 canali, 572² → 570² → 568²) e l'ultimo blocco del decoder (128 canali dopo la concatenazione → 64 → 64 → 2, fino a 388²), con la legenda delle frecce.</p>
<div class="box x"><b>Approfondimento</b>Due accorgimenti del paper originale, utili per l'orale: una <b>mappa di pesi</b> per pixel nella cross-entropy, che dà più peso ai bordi sottili fra cellule a contatto, e una forte <b>data augmentation</b> con deformazioni elastiche, perché i dati annotati erano poche decine di immagini. Prince § 11.5.3 confronta la U-Net con le reti hourglass, che aggiungono le skip al decoder per <b>somma</b> invece di concatenarle.</div>
""", printed=P(17))

s(18, "Upsampling Operators: Deconv vs. Resize + Conv", """
<ul>
<li><b>Interpolazione nearest o bilineare + conv</b>: un ridimensionamento fisso, non appreso, seguito da una conv apprendibile che rifinisce. Economico, liscio, niente artefatti a scacchiera.</li>
<li><b>Convoluzione trasposta</b> («deconv»): sovracampionamento <b>apprendibile</b>, ma la <b>sovrapposizione disuguale</b> del kernel può produrre <b>artefatti a scacchiera</b> (checkerboard).</li>
<li>In pratica le varianti di U-Net e FCN usano convoluzione trasposta oppure upsample + conv, per stabilità.</li>
</ul>
<p><b>Figura</b> (Odena, Dumoulin, Olah, Distill 2016): tre schemi 1D da una riga d'ingresso a una riga d'uscita con le matrici corrispondenti. <b>Deconvolution</b> (stride 2, kernel 3): le uscite ricevono alternativamente uno o due contributi (colonne «a, c» e «b»), quindi pixel pari e dispari sono calcolati con pesi diversi. <b>NN-resize convolution</b>: ogni uscita riceve contributi bilanciati (a+b, b+c). <b>Bilinear-resize convolution</b>: coefficienti frazionari (½a, ½b…) distribuiti in modo uniforme.</p>
<div class="box k"><b>Da saper fare</b>Spiegare la scacchiera in 1D. Convoluzione trasposta con stride 2 e kernel 3 = inserire uno zero fra i campioni e poi convolvere con [w<sub>1</sub>, w<sub>2</sub>, w<sub>3</sub>]: le uscite in posizione dei campioni originali ricevono solo w<sub>2</sub>, quelle in mezzo w<sub>1</sub> + w<sub>3</sub> da due vicini. Se w<sub>2</sub> ≠ w<sub>1</sub> + w<sub>3</sub>, anche un ingresso costante dà un'uscita che alterna due valori: una scacchiera in 2D. Rimedi: kernel divisibile per lo stride (4 con stride 2), inizializzazione bilineare, oppure resize + conv.</div>
<div class="box b"><b>Dal libro · {C21}, § 21.4.3–21.4.5, e Prince § 10.4.2</b><p>Lettura «alla L6»: inserire zeri (espansione) crea copie dello spettro, e il filtro che segue deve toglierle; il filtro bilineare per fattore 2 è il binomiale [1/2, 1, 1/2], che ha somma 1 sulle posizioni pari e sulle dispari (½ + ½ = 1): per questo non fa scacchiera. Il libro mostra che anche il binomiale non sopprime del tutto le copie (fig. 21.21). Un kernel appreso qualunque non ha questo vincolo. Prince (fig. 10.13) spiega il nome: la matrice dell'upsampling è la <b>trasposta</b> di quella della conv con stride 2; elenca anche duplicazione, max unpooling e interpolazione bilineare (fig. 10.12).</p></div>
""".replace('{C21}', C21), printed=P(18))

s(19, "Upsampling Operators: Sub-Pixel Convolution", """
<ul>
<li><b>Sub-pixel / pixel shuffle</b>: si convolve a <b>bassa risoluzione</b> producendo r² volte i canali (C·r² canali per un'uscita a C canali e fattore r), poi si <b>riorganizzano</b> i canali in posizioni spaziali: ogni gruppo di r² canali di un pixel diventa un blocco r × r. Il riordino è fisso: non serve un filtro di upsampling appreso a parte.</li>
<li><b>Efficiente</b> (tutto il calcolo resta a bassa risoluzione) ed evita la sovrapposizione disuguale della convoluzione trasposta.</li>
<li>Diffusa nella <b>super-risoluzione</b>; usabile anche come blocco di upsampling generico nei decoder.</li>
</ul>
<p><b>Figura</b> (Shi et al. 2016, ESPCN, fig. 1): a sinistra una pila di r² mappe colorate a bassa risoluzione («r² channels»), a destra l'immagine ad alta risoluzione in cui i pixel dei diversi colori si alternano a mosaico: lo «strato di convoluzione sub-pixel».</p>
<div class="box x"><b>Approfondimento</b>Il pixel shuffle non elimina del tutto la scacchiera: ognuna delle r² posizioni sub-pixel è prodotta da un filtro diverso, e con un'inizializzazione casuale questi filtri sono diversi fra loro, quindi all'inizio dell'addestramento compare lo stesso motivo periodico. Il rimedio standard (Aitken et al. 2017, «ICNR») è inizializzare le r² copie con lo stesso filtro, che equivale a partire da un nearest-neighbor + conv. Shi et al. mostrano anche che il sub-pixel equivale a una convoluzione trasposta con un kernel opportuno: cambia soprattutto l'efficienza.</div>
""", printed=P(19))

s(20, "Monocular Depth Estimation: MiDaS", """
<ul>
<li><b>Compito</b>: un valore di profondità per pixel da una sola immagine: encoder-decoder con una testa di regressione a <b>1 canale</b>.</li>
<li><b>Problema della supervisione</b>: nessun sensore misura la profondità «vera» ovunque; la GT viene da fonti <b>incompatibili</b>:
<ul><li>LiDAR / RGB-D: metrica (in metri), ma sparsa o limitata agli interni;</li>
<li>stereo (per esempio da film 3D): nota a meno di <b>scala e spostamento</b> (disparità con baseline e calibrazione sconosciute);</li>
<li>structure from motion: <b>nessuna scala</b> assoluta.</li></ul></li>
<li><b>Soluzione</b> (Ranftl et al. 2022, MiDaS): addestrare su <b>molti</b> dataset insieme con una <b>loss invariante a scala e spostamento</b>: prima di calcolare la loss si allinea la predizione alla scala e allo spostamento del campione.</li>
<li><b>Risultato</b>: un modello che generalizza <b>zero-shot</b> a dataset mai visti.</li>
</ul>
<p><b>Figura</b> (MiDaS, fig. 1): foto (sopra: un autobus, un'auto in una strada) e la loro <b>profondità inversa</b> predetta (sotto: chiaro = vicino).</p>
<div class="box k"><b>Da saper fare</b>Scrivere la loss invariante a scala e spostamento. Per ogni immagine si trovano s, t che allineano la predizione d̂ alla GT d (nello spazio della disparità, 1/profondità):
<span class="f">(s, t) = argmin ∑<sub>i</sub> (s d̂<sub>i</sub> + t − d<sub>i</sub>)²,   L = (1/M) ∑<sub>i</sub> ρ(s d̂<sub>i</sub> + t − d<sub>i</sub>)</span>
I minimi quadrati hanno soluzione chiusa (regressione lineare con due parametri). MiDaS usa anche una versione robusta: scala e spostamento stimati con mediana e deviazione assoluta media, e ρ = errore assoluto con i residui più grandi scartati. La rete quindi impara la <b>forma relativa</b> della scena, non la distanza in metri.</div>
<div class="box b"><b>Dal libro · {C43}, § 43.4.2–43.4.3</b><p>Il libro motiva la loss invariante con l'ambiguità di scala e suggerisce di ottimizzare il logaritmo della profondità o la <b>disparità</b> 1/z, per non far pesare troppo gli errori sui punti lontani: MiDaS fa proprio questo (predice profondità inversa). L'architettura tipica è un encoder-decoder con skip (fig. 43.4); il libro rimanda a Ranftl et al. senza nominare MiDaS. Szeliski § 12.8 descrive MiDaS (anche i film 3D come fonte di dati) e il protocollo di valutazione zero-shot su dataset diversi da quelli di training. Collegamento con <a href="#L13">L13</a>: nello stereo la scala si recupera dalla baseline; con una sola immagine no.</p></div>
""".replace('{C43}', C43), printed=P(20))

s(21, "Optical Flow: RAFT", """
<ul>
<li><b>Compito</b>: un vettore di moto (u, v) per pixel fra due frame consecutivi.</li>
<li><b>Perché un encoder-decoder semplice non basta</b>: non <b>confronta</b> esplicitamente le due immagini. Serve un passo di <b>matching</b> esplicito: un <b>volume di correlazione 4D</b>, il prodotto scalare di ogni feature del frame 1 con ogni feature del frame 2 (dimensione H × W × H × W, calcolato a 1/8 della risoluzione).</li>
<li><b>RAFT</b> (Teed e Deng 2020): legge questo volume attorno alla stima corrente e <b>rifinisce iterativamente</b> il flusso con un aggiornamento ricorrente (10 o più iterazioni), invece di predirlo in un colpo.</li>
<li><b>Supervisione</b>: una GT reale per pixel è quasi impossibile da raccogliere: addestramento quasi tutto su dati <b>sintetici</b> (FlyingChairs, MPI-Sintel).</li>
</ul>
<p><b>Figura</b> (RAFT, fig. 1): i due frame passano in un feature encoder a pesi condivisi; un context encoder elabora solo il primo frame; dalle feature si costruisce il «4D correlation volume» (con una piramide di pooling sulle ultime due dimensioni); un blocco ricorrente parte da flusso 0 e a ogni passo consulta il volume e aggiorna il flusso, fino alla mappa a colori finale.</p>
<div class="box b"><b>Dal libro · {C49}, § 49.2.1, e {C48}, § 48.3</b><p>RAFT non è nel visionbook, ma tutti i suoi ingredienti sì. Il § 49.2.1.1 distingue l'approccio <b>diretto</b> (FlowNet: i due frame entrano in una rete e ne esce il flusso, fig. 49.1) da quello <b>modulare</b> che ricalca i metodi classici (fig. 49.2): feature con pesi condivisi, <b>cost volume</b> che misura la somiglianza per ogni spostamento possibile, aggregazione con una CNN, raffinamento coarse-to-fine con warping. È la stessa struttura del cost volume dello stereo (<a href="#L13">L13</a>), ma con spostamenti 2D invece che solo orizzontali. Il raffinamento iterativo di RAFT è la versione appresa delle iterazioni di Lucas-Kanade e Horn-Schunck (§ 48.3). Sui dati il libro concorda: la GT è «probabilmente il limite principale» (§ 49.2.1.4). RAFT è descritto in Szeliski § 9.3.1 (volume di correlazione (W × H)² multi-risoluzione).</p></div>
<div class="box x"><b>Approfondimento</b>«Non confronta mai le due immagini» va preso come intuizione: FlowNetS, un encoder-decoder sui due frame impilati, impara un flusso ragionevole, quindi il confronto può emergere implicitamente; ma un volume di correlazione esplicito funziona molto meglio e generalizza di più, ed è questo il punto della slide.</div>
""".replace('{C49}', C49).replace('{C48}', C48), printed=P(21))

s(22, "Losses for Dense Prediction", """
<ul>
<li><b>Cross-entropy per pixel</b>: la CE sommata o mediata su tutti i pixel; scelta di default per la segmentazione semantica.
<span class="f">L<sub>CE</sub> = − ∑<sub>i</sub> ∑<sub>c</sub> y<sub>i,c</sub> log p̂<sub>i,c</sub></span>
(i = pixel, c = classe, y one-hot).</li>
<li><b>Focal loss</b>: per uno <b>sbilanciamento</b> forte fra classi (una piccola lesione su uno sfondo enorme); moltiplica la CE per (1 − p<sub>t</sub>)<sup>γ</sup>, dove p<sub>t</sub> è la probabilità data alla classe giusta: i pixel facili, già sicuri, pesano poco e il gradiente è dominato da quelli difficili (spesso delle classi rare).
<span class="f">L<sub>focal</sub> = − ∑<sub>i</sub> (1 − p̂<sub>i</sub>)<sup>γ</sup> log p̂<sub>i</sub></span>
qui p̂<sub>i</sub> va letto come p<sub>t</sub> del pixel i (la probabilità della classe vera), non come la probabilità di una classe qualunque.</li>
<li><b>Dice loss</b> (e la parente soft-IoU): ottimizza un'approssimazione <b>differenziabile</b> (soft) della sovrapposizione fra maschera predetta e maschera vera; robusta allo sbilanciamento perché <b>ignora i veri negativi</b> (lo sfondo correttamente classificato non entra nella formula); spesso combinata con la CE.
<span class="f">L<sub>Dice</sub> = 1 − (2 ∑<sub>i</sub> p̂<sub>i</sub> y<sub>i</sub> + ε) / (∑<sub>i</sub> p̂<sub>i</sub>² + ∑<sub>i</sub> y<sub>i</sub>² + ε)</span>
(p̂<sub>i</sub> ∈ [0, 1] probabilità di primo piano, y<sub>i</sub> ∈ {0, 1}; ε evita 0/0 su maschere vuote. I quadrati al denominatore sono la versione di V-Net, Milletari et al. 2016; molte implementazioni usano ∑p̂<sub>i</sub> + ∑y<sub>i</sub>.)</li>
<li><b>Regressione</b> (profondità, flusso): L1/L2 o varianti robuste, loss invariante di scala per la profondità monoculare, spesso con regolarizzatori di levigatezza che rispettano i bordi dell'immagine (edge-aware smoothness).</li>
</ul>
<div class="box w"><b>Attenzione: Dice non è IoU</b>La slide chiama la formula «Dice loss / Soft-IoU loss» e dice che viene «dalla formula di sovrapposizione IoU». La formula scritta è il coefficiente di <b>Dice</b>, D = 2|A ∩ B| / (|A| + |B|) (equivalente all'F1), non l'IoU J = |A ∩ B| / |A ∪ B|. Le due misure sono legate in modo monotono, D = 2J/(1 + J) (per esempio J = 0,5 dà D ≈ 0,67), quindi hanno gli stessi ottimi, ma la soft-IoU (Jaccard) è una loss diversa: 1 − ∑p̂y / (∑p̂ + ∑y − ∑p̂y).</div>
<div class="box k"><b>Da saper fare</b>Focal loss con γ = 2: un pixel facile con p<sub>t</sub> = 0,9 ha CE = −ln 0,9 ≈ 0,105 e fattore (0,1)² = 0,01, quindi pesa 100 volte meno; un pixel difficile con p<sub>t</sub> = 0,1 ha fattore 0,81 e resta quasi intatto. Con γ = 0 si torna alla CE. La versione completa di Lin et al. 2017 ha anche un peso di classe α<sub>t</sub>: −α<sub>t</sub>(1 − p<sub>t</sub>)<sup>γ</sup> log p<sub>t</sub> (la slide lo omette, come la prima formula del paper).</div>
<div class="box b"><b>Dal libro · {C50}, § 50.5</b><p>Il libro scrive la loss di segmentazione come cross-entropy sommata su esempi, classi e posizioni (n, m), e nota subito il problema: la CE «potrebbe concentrarsi troppo sugli oggetti grandi e ignorare quelli piccoli», quindi propone di <b>pesare ogni classe</b> in base alla sua area media nel training set. Focal e Dice sono altri due modi di affrontare lo stesso sbilanciamento; non sono nel libro.</p></div>
""".replace('{C50}', C50), printed=P(22))

s(23, "Evaluating Dense Predictions", """
<ul>
<li><b>Loss ≠ metrica</b>: la loss deve essere <b>differenziabile</b> per guidare il training; la metrica deve solo essere <b>significativa</b> per confrontare i modelli.</li>
<li><b>Segmentazione, mIoU</b>: per ogni classe IoU = |Ŷ ∩ Y| / |Ŷ ∪ Y| (= TP / (TP + FP + FN)), poi media sulle classi. Più robusta allo sbilanciamento della <b>pixel accuracy</b>, che è dominata dalle classi grandi.</li>
<li><b>Profondità</b>:
<span class="f">AbsRel = media<sub>i</sub> |d̂<sub>i</sub> − d<sub>i</sub>| / d<sub>i</sub>,   RMSE = √( media<sub>i</sub> (d̂<sub>i</sub> − d<sub>i</sub>)² )</span>
spesso calcolate anche sul log della profondità (RMSE log).</li>
<li><b>Flusso ottico, EPE</b> (end-point error): distanza euclidea media fra il vettore di flusso predetto e quello vero, per pixel: media<sub>i</sub> √((û<sub>i</sub> − u<sub>i</sub>)² + (v̂<sub>i</sub> − v<sub>i</sub>)²).</li>
<li><b>Pose, PCK</b> (percentage of correct keypoints): percentuale di keypoint predetti entro una soglia di distanza dalla GT, normalizzata per la scala (per esempio una frazione della dimensione della testa o del box della persona).</li>
</ul>
<p>Formule verificate: sono le definizioni standard.</p>
<div class="box k"><b>Da saper fare</b>Esempi a mano. Profondità vera 10 m, predetta 11 m: AbsRel = 0,1. Due classi con IoU 0,9 (strada) e 0,3 (pali): mIoU = 0,6, mentre la pixel accuracy può stare sopra il 95% perché i pali sono pochi pixel. EPE per un pixel con flusso vero (3, 4) e predetto (0, 0): 5 pixel. Perché AbsRel divide per d: un errore di 1 m conta molto a 2 m, poco a 50 m.</div>
<div class="box b"><b>Dal libro · {C50}, § 50.5, e {C49}, § 49.2.1.2</b><p>Il § 50.5 dice proprio questo: la percentuale di pixel corretti è dominata dagli oggetti grandi (cielo, strada); meglio l'IoU medio sulle classi, invariante alla scala. Il mIoU è la stessa metrica della segmentazione LiDAR di <a href="#L14">L14</a>. Nel § 49.2.1.2 il libro chiama endpoint error «la media della distanza» fra flusso stimato e vero, ma la formula che scrive è una <b>somma di distanze al quadrato</b> su tutti i pixel: è una loss di tipo L2 (comoda per il training), non l'EPE delle metriche, che è una media di distanze non elevate al quadrato. Vale la definizione della slide. AbsRel, RMSE e PCK non sono nel libro.</p></div>
""".replace('{C50}', C50).replace('{C49}', C49), printed=P(23))

# ===================== VISION TRANSFORMER =====================

s(24, "Vision Transformer (ViT)", """<p>Divisoria della terza parte (slide 24–39): sotto il titolo, la prima pagina dell'articolo di Dosovitskiy et al. (ICLR 2021), «An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale», con l'abstract: un transformer puro applicato a sequenze di patch, pre-addestrato su grandi dataset, raggiunge o supera le migliori CNN in classificazione con meno calcolo di training.</p>""",
  kind='div', sec=("l17-vit", "Vision Transformer", "slide 24–39"), printed=P(24))

s(25, "Vision Transformer (ViT)", """
<p><b>Idea di base</b>:</p>
<ul>
<li>dividere l'immagine in <b>patch</b> di dimensione fissa (per esempio 16 × 16), appiattirle e <b>proiettarle linearmente</b>: ogni patch diventa un <b>token</b>;</li>
<li>anteporre un token <b>[CLS]</b> apprendibile (preso da BERT, Devlin et al. 2019) e aggiungere le <b>codifiche posizionali</b>;</li>
<li>far passare i token in blocchi standard di <b>transformer encoder</b> (self-attention multi-testa + MLP).</li>
</ul>
<p><b>Oltre la classificazione</b>: il ViT è un <b>encoder</b>, quindi si inserisce nella stessa ricetta encoder-decoder usata per FCN e U-Net. SETR, SegFormer e DPT accoppiano un encoder transformer con un decoder per la predizione densa.</p>
<p><b>Figura</b> (Dosovitskiy et al. 2021, ViT, fig. 1): a sinistra un'immagine tagliata in 9 patch, «Linear Projection of Flattened Patches», i token numerati 1–9 più il token 0 (asterisco, «extra learnable [class] embedding»), sommati alle posizioni («Patch + Position Embedding»); poi il «Transformer Encoder» e una «MLP Head» che legge solo l'uscita del token 0 e dà la classe (Bird, Ball, Car…). A destra un blocco dell'encoder, ripetuto L volte: Norm → Multi-Head Attention → somma residua, poi Norm → MLP → somma residua.</p>
<div class="box b"><b>Dal libro · {C26}, § 26.4 e 26.7</b><p>Il capitolo costruisce il transformer partendo da un nuovo tipo di dato, il <b>token</b>: un gruppo di neuroni (un vettore) su cui si opera solo con due tipi di operazioni, il <b>mescolamento fra token</b> (combinazioni lineari dei token: l'attenzione) e la <b>modifica di ogni token</b> (lo stesso MLP applicato a ciascuno). La fig. 26.14 è proprio l'architettura ViT. Differenza importante: il libro <b>non usa il token [CLS]</b>; per classificare propone di <b>sommare</b> tutti i token d'uscita e applicare un solo strato lineare (§ 26.7), cioè un pooling globale come il GAP delle CNN. Il [CLS] è in Prince § 12.10.2 (token &lt;cls&gt;) e nell'articolo originale. Il ViT originale era pre-addestrato su JFT-300M (303 milioni di immagini, Prince § 12.10.2): senza tanti dati non batteva le CNN.</p></div>
""".replace('{C26}', C26), printed=P(25))

s(26, "ViT: Patch Embedding", """
<p><b>Passo per passo</b>: si divide l'immagine in una griglia di N = (H/P) × (W/P) patch P × P → si appiattisce ciascuna in un vettore di P²C numeri → la si <b>proietta linearmente</b> con la <b>stessa matrice E</b> per tutte le patch in un token di dimensione D.</p>
<ul>
<li>Si antepone un token <b>[CLS]</b> apprendibile x<sub>cls</sub> ∈ ℝ<sup>D</sup>; il suo stato finale si usa per la classificazione.</li>
<li>Si somma una <b>codifica posizionale appresa</b> E<sub>pos</sub> a <b>ogni</b> token ([CLS] compreso): altrimenti il transformer non sa da dove viene ciascuna patch.</li>
<li>Risultato: una sequenza di <b>N + 1</b> token di dimensione D.</li>
</ul>
<span class="f">z<sub>0</sub> = [x<sub>cls</sub>; x<sub>p</sub><sup>1</sup>E; …; x<sub>p</sub><sup>N</sup>E] + E<sub>pos</sub>,   E ∈ ℝ<sup>(P²C)×D</sup>,   E<sub>pos</sub> ∈ ℝ<sup>(N+1)×D</sup></span>
<p>Esempio della slide: immagine 224², P = 16: N = 14 · 14 = <b>196</b> patch → <b>197</b> token. Verificato.</p>
<p><b>Figura</b>: la torre di Pisa («input»), alcune patch ritagliate («crop»), e sopra ogni patch il suo token t ∈ ℝ<sup>D</sup> ottenuto con la stessa E (è lo schema della fig. 26.2 del visionbook, con un'altra foto).</p>
<div class="box k"><b>Da saper fare</b>Contare per ViT-B/16 (C = 3, P = 16, D = 768): ogni patch ha 16·16·3 = 768 numeri, quindi E è 768 × 768 = 589.824 pesi (+ 768 bias); E<sub>pos</sub> ha 197 · 768 = 151.296 parametri; x<sub>cls</sub> 768. Con P = 8 invece: N = 28² = 784 patch, 785 token.</div>
<div class="box b"><b>Dal libro · {C26}, § 26.4.1–26.4.2</b><p>Il libro tokenizza nello stesso modo (la patch vettorizzata, canali impilati, poi una proiezione lineare apprendibile W<sub>tokenize</sub>, fig. 26.2) e mette i token come <b>righe</b> di una matrice T ∈ ℝ<sup>N×d</sup>: la stessa convenzione di X ∈ ℝ<sup>(N+1)×D</sup> nella slide 30. La «patch flattening + E» è una convoluzione con kernel P e stride P (§ 26.9.1, slide 37).</p></div>
""".replace('{C26}', C26), printed=P(26))

s(27, "Positional Embeddings", """
<p><b>Perché servono</b>: la self-attention è <b>equivariante alle permutazioni</b>: se si mescolano i token delle patch, le uscite vengono semplicemente mescolate allo stesso modo, quindi il modello non sa dove si trova ogni patch. Sommare E<sub>pos</sub> a ogni token rompe questa simmetria e inietta l'informazione spaziale che l'attenzione da sola non può recuperare.</p>
<table>
<tr><th></th><th>Sinusoidali (fisse, Vaswani et al. 2017)</th><th>Apprese, assolute (default del ViT)</th></tr>
<tr><td>cosa sono</td><td>funzione fissa della posizione i: le dimensioni basse oscillano veloci, le alte lente</td><td>un vettore apprendibile per posizione, nessuna struttura imposta</td></tr>
<tr><td>pro e contro</td><td>nessun parametro; definite per qualunque posizione</td><td>tabella di dimensione fissa: con una nuova risoluzione bisogna <b>interpolare</b></td></tr>
</table>
<p><b>Figura</b>: due mappe di calore (asse orizzontale posizione i, verticale dimensione k): a sinistra un motivo regolare, a destra valori senza struttura apparente.</p>
<p>Formula di Vaswani et al.: PE(i, 2k) = sin(i / 10000<sup>2k/D</sup>), PE(i, 2k+1) = cos(i / 10000<sup>2k/D</sup>): la frequenza scende al crescere di k, come dice la slide.</p>
<div class="box k"><b>Da saper fare</b>Dire con precisione cosa è equivariante. Solo attenzione e MLP per token, <i>senza</i> codifiche posizionali: permutare i token d'ingresso permuta allo stesso modo quelli d'uscita (equivarianza), e il token [CLS], che non viene permutato, dà la stessa uscita (invarianza): un ViT senza posizioni classificherebbe allo stesso modo un'immagine e il suo «puzzle» rimescolato. Con E<sub>pos</sub> sommata la simmetria si rompe.</div>
<div class="box b"><b>Dal libro · {C26}, § 26.8 e 26.11</b><p>Il libro dimostra l'equivarianza: gli strati per token, l'attenzione, i residui e la normalizzazione per token sono tutti equivarianti alle permutazioni, e la composizione di funzioni equivarianti lo è ancora (fig. 26.15). Per le posizioni (§ 26.11) usa un codice periodico con soli seni, p<sub>x</sub> = [sin x, sin(x/B), sin(x/B²), …, sin(x/B<sup>P</sup>)], uno per x e uno per y (eq. 26.12), e lo <b>concatena</b> al token; il ViT invece lo <b>somma</b>. Cita i codici appresi come alternativa (ViT). Nota: nel § 26.8 il libro aggiunge che ogni strato equivariante alle permutazioni è anche equivariante alle traslazioni; vale per la sola attenzione senza posizioni, non per un ViT con E<sub>pos</sub>.</p></div>
""".replace('{C26}', C26), printed=P(27))

s(28, "Positional Embeddings for 2D", """
<p>Il ViT di base <b>appiattisce</b> la griglia di patch in una sequenza 1D e di solito usa codifiche apprese indicizzate dalla posizione appiattita (una E<sub>pos</sub> per «casella»). Alternative:</p>
<ul>
<li><b>2D fattorizzate (riga + colonna)</b>: due tabelle apprese E<sub>row</sub> ed E<sub>col</sub>, sommate per ogni patch: E<sub>pos</sub>(r, c) = E<sub>row</sub>[r] + E<sub>col</sub>[c]. Servono O(H + W) vettori invece di O(HW) (H, W qui in patch).</li>
<li><b>Bias di posizione relativa</b> (Liu et al. 2021, Swin): un bias appreso B(Δi, Δj) sommato ai <b>logit</b> dell'attenzione, indicizzato dallo <b>spostamento relativo</b> fra query e key: invariante alla traslazione.</li>
<li><b>Rotary (RoPE)</b> (Su et al. 2021): ruota q e k di un angolo proporzionale alla posizione, così nel prodotto qᵀk la posizione entra <b>solo tramite lo spostamento relativo</b> (il prodotto dipende ovviamente anche dal contenuto di q e k). Standard negli LLM, esteso al 2D in alcune varianti di ViT.</li>
</ul>
<p><b>Perché conta</b>: la segmentazione lavora a risoluzioni variabili. Le codifiche assolute 1D apprese vanno rimodellate in una griglia 2D e <b>interpolate</b> quando cambia la risoluzione (come fa DPT); gli schemi relativi, come il bias di Swin, si adattano più naturalmente a ingressi di dimensione diversa.</p>
<p><b>Figura</b>: a sinistra una griglia 3×3 di caselle, ognuna con la sua E<sub>pos</sub> («1D flat index»); a destra la versione fattorizzata: una colonna di E<sub>row</sub> e una riga di E<sub>col</sub> le cui somme riempiono la griglia.</p>
<div class="box k"><b>Da saper fare</b>Esempio di conti: griglia 14 × 14. Tabella 1D: 196 vettori; fattorizzata: 14 + 14 = 28 vettori. Passando a 32 × 32 patch (immagine 512² con P = 16) la tabella 1D va interpolata in 2D da 14 × 14 a 32 × 32; con RoPE o un bias relativo non c'è nulla da interpolare per la parte di posizione (il bias relativo ha comunque una tabella di spostamenti massimi, che Swin limita a una finestra).</div>
<div class="box b"><b>Dal libro · Prince § 12.3.1</b><p>Prince distingue le codifiche <b>assolute</b> (una matrice sommata all'ingresso, scelta a mano o appresa; a volte sommata solo a query e key) da quelle <b>relative</b>, che modificano direttamente la matrice di attenzione con un parametro per ogni spostamento fra posizione della key e della query: in una frase conta più la posizione relativa di due parole che quella assoluta. Il visionbook non tratta né il bias relativo né RoPE.</p></div>
""", printed=P(28))

s(29, "ViT: Self-Attention", """
<p>Ogni token (una patch immersa) presta attenzione a <b>tutti</b> i token, compreso sé stesso, e ne combina l'informazione. Proiezioni lineari apprese trasformano ogni token in:</p>
<ul>
<li><b>query</b>: cosa sta cercando questo token;</li>
<li><b>key</b>: le caratteristiche con cui si decide quanto il token è rilevante per una query;</li>
<li><b>value</b>: l'informazione che il token passa agli altri.</li>
</ul>
<ul>
<li><b>Peso di attenzione</b> = somiglianza query-key scalata, normalizzata con la softmax.</li>
<li><b>Uscita</b> = somma pesata di tutti i value.</li>
</ul>
<p>⇒ <b>Campo recettivo globale dal primo strato</b>: ogni coppia di patch interagisce direttamente, mentre una CNN aggrega informazione locale strato dopo strato.</p>
<p><b>Figura</b>: la torre di Pisa con tre patch t<sub>1</sub>, t<sub>2</sub>, t<sub>3</sub> sulla torre; t<sub>2</sub> fa da query (in basso), le frecce tratteggiate «attention» indicano i pesi su t<sub>1</sub>, t<sub>2</sub>, t<sub>3</sub>, e la loro somma («sum») dà il nuovo t<sub>2</sub> (in alto). È lo schema della fig. 26.11 del visionbook (lì con un impala in un safari).</p>
<div class="box b"><b>Dal libro · {C26}, § 26.3, 26.6 e 26.6.1–26.6.2</b><p>Il libro presenta l'attenzione come un <b>pooling dinamico</b>: l'uscita è una combinazione lineare dei token, come in uno strato lineare, ma i pesi dipendono dai dati. L'esempio del safari (fig. 26.7–26.8): la domanda «quanti animali ci sono?» dà peso alle patch con teste di animale, «di che colore è l'impala?» alle patch dell'impala; cambiando la domanda cambia la somma. Il nome query/key/value viene dai database: una cella restituisce il suo value quando la query corrisponde alla sua key. Nella self-attention <b>tutti</b> i token fanno query (§ 26.6.2); nella fig. 26.11 il token del torso dell'impala aggrega le altre patch dell'impala e diventa una rappresentazione più «semantica»: è esattamente quello che serve alla segmentazione. Il § 26.2 spiega il limite delle CNN che motiva tutto: una CNN a 2 strati con kernel 3 non ha nessun neurone collegato sia a x<sub>1</sub> sia a x<sub>7</sub> (fig. 26.1).</p></div>
""".replace('{C26}', C26), printed=P(29))

s(30, "ViT: Self-Attention", """
<span class="f">Attention(Q, K, V) = softmax( QKᵀ / √d<sub>k</sub> ) V,   Q = XW<sup>Q</sup>, K = XW<sup>K</sup>, V = XW<sup>V</sup></span>
<ul>
<li>X ∈ ℝ<sup>(N+1)×D</sup>: i token in ingresso allo strato (N patch + [CLS], con le posizioni), uno per <b>riga</b>.</li>
<li>QKᵀ ∈ ℝ<sup>(N+1)×(N+1)</sup>: tutte le somiglianze query-key; la softmax è <b>per riga</b> (ogni query distribuisce un peso totale 1 sui token); costo O(N²D).</li>
<li><b>Perché √d<sub>k</sub></b>: se le componenti di q e k sono indipendenti, a media zero e varianza 1, allora Var(qᵀk) = d<sub>k</sub>. Dividendo per √d<sub>k</sub> la varianza dei logit torna circa 1, e la softmax non satura quando d<sub>k</sub> cresce.</li>
<li><b>Multi-testa</b>: h teste con d<sub>k</sub> = D/h hanno, al primo ordine, lo stesso costo di attenzione di una testa di dimensione D: O(N²D). Più teste permettono di prestare attenzione in parallelo a sottospazi di rappresentazione diversi.</li>
<li><b>Implementazione</b>: Q, K, V vengono tutte da X, quindi basta un'unica moltiplicazione con W<sup>QKV</sup> ∈ ℝ<sup>D×3D</sup>.</li>
</ul>
<div class="box k"><b>Da saper fare</b>Derivare Var(qᵀk) = d<sub>k</sub>: qᵀk = ∑<sub>j=1</sub><sup>d<sub>k</sub></sup> q<sub>j</sub>k<sub>j</sub>; per q<sub>j</sub>, k<sub>j</sub> indipendenti a media 0 e varianza 1, E[q<sub>j</sub>k<sub>j</sub>] = 0 e Var(q<sub>j</sub>k<sub>j</sub>) = E[q<sub>j</sub>²]E[k<sub>j</sub>²] = 1; i termini sono indipendenti, quindi le varianze si sommano: d<sub>k</sub>. Per ViT-B (D = 768, h = 12, d<sub>k</sub> = 64) senza scala i logit avrebbero deviazione standard 8: la softmax darebbe quasi tutto il peso a un solo token e gradienti quasi nulli. Costo multi-testa: h · N²·(D/h) = N²D, la stessa cosa.</div>
<div class="box b"><b>Dal libro · {C26}, § 26.6.2–26.6.3, e Prince § 12.3.2–12.3.3</b><p>Il visionbook scrive Q = TW<sub>q</sub>ᵀ, K = TW<sub>k</sub>ᵀ, V = TW<sub>v</sub>ᵀ e A = softmax(QKᵀ/√m) con softmax per riga (eq. 26.5–26.6): stessa formula con altri nomi (T per X, m per d<sub>k</sub>). Sulla multi-testa dà l'intuizione migliore: con una testa la somiglianza è t<sub>i</sub>ᵀ W<sub>q</sub>ᵀW<sub>k</sub> t<sub>j</sub>, cioè un solo modo di misurare la somiglianza (per esempio solo il colore); con k teste in parallelo se ne misurano k (colore, texture, forma), poi si concatenano le uscite e si proiettano con una matrice appresa W<sub>MSA</sub> (eq. 26.7). Prince motiva la scala √D<sub>q</sub> con la saturazione della softmax (gradienti piccoli) e indica teste di dimensione D/H per un'implementazione efficiente. Attenzione: nel pseudocodice del § 26.7 il libro scrive softmax(…, dim=0), cioè per colonne, in contraddizione con il «per riga» dell'eq. 26.6: vale per riga.</p></div>
""".replace('{C26}', C26), printed=P(30))

s(31, "ViT: Residual Blocks", """
<ul>
<li>Con i <b>residui</b> ogni blocco impara una <b>correzione</b> invece di una trasformazione completa; il gradiente passa direttamente attraverso il «+», evitando che svanisca in 12 o più blocchi impilati (lo stesso motivo delle skip di ResNet, <a href="#L15">L15</a>).</li>
<li>Due sotto-blocchi residui per strato: la <b>MHSA</b> mescola informazione <b>fra</b> token, l'<b>MLP</b> trasforma <b>ogni</b> token indipendentemente; entrambi «avvolti» allo stesso modo:</li>
</ul>
<span class="f">x ← x + MHSA(LN(x)),   x ← x + MLP(LN(x))</span>
<p>È la variante <b>pre-norm</b>: la LayerNorm sta dentro il ramo, prima di MHSA e MLP, e il cammino residuo resta un'identità pulita. L'MLP è Linear(D → 4D), GELU, Linear(4D → D).</p>
<p><b>Figura</b> (ViT, fig. 1, parte destra): il blocco dell'encoder, ripetuto L volte: Embedded Patches → Norm → Multi-Head Attention → ⊕ → Norm → MLP → ⊕.</p>
<div class="box b"><b>Dal libro · {C26}, § 26.7, e Prince § 12.4</b><p>Il visionbook descrive proprio questa disposizione per il ViT: LayerNorm prima di ogni attenzione e prima di ogni MLP per token, residui attorno a ciascuno (fig. 26.14 e pseudocodice). Chiama la normalizzazione «token norm» (statistiche sul singolo token) e dice che non ha parametri appresi, mentre nel § 12.7.3 la layernorm ha scala e spostamento appresi (e il ViT reale li ha): piccola incoerenza del libro. Prince (eq. 12.13) scrive invece il transformer originale <b>post-norm</b>, X ← LayerNorm[X + MhSa[X]], e nelle note del capitolo osserva che la LayerNorm messa fuori dal ramo residuo fa ridursi i gradienti mentre tornano indietro nella rete (Xiong et al. 2020): è il motivo per cui ViT e transformer moderni usano la variante pre-norm.</p></div>
""".replace('{C26}', C26), printed=P(31))

s(32, "ViT: Residual Blocks – Compute &amp; Memory", """
<ul>
<li><b>Calcolo e memoria</b>: QKᵀ è N × N ⇒ calcolo O(N²D) e memoria O(N²) per la matrice di attenzione (se la si materializza), con N = (H/P)(W/P). <b>Dimezzare P quadruplica N</b>, e siccome quel costo è ∝ N², il calcolo dei punteggi di attenzione cresce di <b>16×</b>. È il motivo per cui esistono encoder gerarchici come il MiT di SegFormer.</li>
<li><b>Parametri per blocco</b> (D = dimensione dei token, MLP con rapporto 4): QKV 3D² + proiezione d'uscita D² + MLP 8D² ≈ <b>12D²</b>, dominati dall'MLP.</li>
</ul>
<p><b>Figura</b>: una barra divisa in QKV 25%, Output 8%, MLP 67%. Esempio: ViT-B/16 (D = 768): ≈ 7,1 M parametri per blocco × 12 ≈ 85 M parametri nei 12 blocchi.</p>
<p><b>Conti verificati</b>: 3/12 = 25%, 1/12 ≈ 8,3%, 8/12 ≈ 66,7%; 12 · 768² = 7.077.888 ≈ 7,08 M; × 12 = 84,9 M. Il ViT-B/16 reale ha circa 86 M parametri: ai blocchi si aggiungono i bias e le LayerNorm (~0,1 M), il patch embedding (0,59 M), le posizioni (0,15 M) e la testa (768 · 1000 ≈ 0,77 M).</p>
<div class="box k"><b>Da saper fare</b>Confrontare i due termini di costo per blocco (moltiplicazioni-addizioni): parte lineare (QKV, uscita, MLP) ≈ 12ND², parte di attenzione (QKᵀ e AV) ≈ 2N²D. Per ViT-B/16 a 224² (N = 197): 12 · 197 · 768² ≈ 1,39 G contro 2 · 197² · 768 ≈ 0,06 G: a questa risoluzione domina la parte <b>lineare</b> (totale ≈ 1,45 G per blocco, ≈ 17,5 G per 12 blocchi, in linea con i ~17,6 GFLOPs dichiarati per ViT-B/16). Il termine N² supera l'altro quando N &gt; 6D, cioè per immagini grandi: a 1024² con P = 16, N = 4096 e 2N²D ≈ 25,8 G contro 12ND² ≈ 29 G. Con P dimezzato la parte d'attenzione cresce 16×, quella lineare 4×: per la predizione densa ad alta risoluzione l'attenzione globale diventa il collo di bottiglia.</div>
""", printed=P(32))

s(33, "Normalization: BatchNorm vs. LayerNorm vs. GroupNorm", """
<p>Tutte <b>normalizzano</b> le attivazioni con media e varianza calcolate su certe dimensioni, poi di solito applicano una trasformazione affine appresa (scala γ e spostamento β, per canale). Cambiano le <b>dimensioni su cui si media</b>:</p>
<ul>
<li><b>BatchNorm</b>: batch e dimensioni spaziali, separatamente per ogni canale (N, H, W per ogni C).</li>
<li><b>LayerNorm</b>: dimensioni delle feature, separatamente per ogni esempio (C, H, W in questo disegno da CNN; in un ViT la dimensione D di ogni <b>singolo token</b>).</li>
<li><b>InstanceNorm</b>: dimensioni spaziali, separatamente per ogni esempio e canale (H, W).</li>
<li><b>GroupNorm</b>: gruppi di canali e dimensioni spaziali, separatamente per ogni esempio (C/G, H, W).</li>
</ul>
<p><b>Figura</b> (Wu e He 2018, Group Normalization, fig. 2): quattro cubi con assi N (batch), C (canali), H,W (spazio); in blu le celle mediate insieme: una fetta «verticale» N × H,W per un canale (BatchNorm), una fetta C × H,W per un esempio (LayerNorm), una colonna H,W per un esempio e un canale (InstanceNorm), un gruppo di canali × H,W per un esempio (GroupNorm).</p>
<div class="box w"><b>Attenzione: «All three» ma sono quattro</b>Titolo e prima riga parlano di tre normalizzazioni («All three normalize…»), ma la slide e la figura ne elencano quattro: BatchNorm, LayerNorm, InstanceNorm, GroupNorm. InstanceNorm e LayerNorm sono i due estremi della GroupNorm: G = C gruppi dà la InstanceNorm, G = 1 la LayerNorm.</div>
<div class="box b"><b>Dal libro · {C12}, § 12.7.3, e Prince cap. 11 (note, fig. 11.14)</b><p>Il visionbook tratta solo BatchNorm e LayerNorm (più la normalizzazione L2): la LayerNorm è la «trasposta» della BatchNorm (in una matrice batch × feature la BatchNorm standardizza le colonne, la LayerNorm le righe, fig. 12.17, già vista in <a href="#L15">L15</a>). GroupNorm e InstanceNorm non ci sono: Prince le descrive nelle note del cap. 11 con la stessa figura di Wu e He (fig. 11.14), precisando che in tutte resta una scala e uno spostamento appresi <b>per canale</b>.</p></div>
""".replace('{C12}', C12), printed=P(33))

s(34, "Why Transformers Use LayerNorm", """
<ul>
<li><b>BatchNorm</b> usa le statistiche del batch in training e le statistiche accumulate (running) in valutazione: il comportamento può dipendere dalla dimensione del batch e le statistiche di training e di test possono differire.</li>
<li><b>LayerNorm</b> normalizza ogni token indipendentemente sulle sue feature: non dipende dal batch, fa lo stesso calcolo in training e in valutazione, niente statistiche accumulate.</li>
<li>La self-attention lavora sui token di <b>una</b> sequenza, e la lunghezza delle sequenze può cambiare da un ingresso all'altro: la LayerNorm evita di dipendere da altri esempi o da statistiche di batch.</li>
<li><b>GroupNorm</b> normalizza gruppi di canali per esempio: utile per le CNN addestrate con <b>batch piccoli</b> (tipico della segmentazione e della detection, dove le immagini sono grandi e in memoria ne entrano poche).</li>
</ul>
<div class="box k"><b>Da saper fare</b>Per un token x ∈ ℝ<sup>D</sup>: μ = (1/D)∑<sub>j</sub> x<sub>j</sub>, σ² = (1/D)∑<sub>j</sub>(x<sub>j</sub> − μ)², LN(x)<sub>j</sub> = γ<sub>j</sub>(x<sub>j</sub> − μ)/√(σ² + ε) + β<sub>j</sub>. Esempio con D = 4, x = (1, 2, 3, 6), γ = 1, β = 0: μ = 3, σ² = (4 + 1 + 0 + 9)/4 = 3,5, uscita ≈ (−1,07; −0,53; 0; 1,60). Lo stesso token dà la stessa uscita qualunque siano gli altri token e gli altri esempi del batch.</div>
<div class="box b"><b>Dal libro · Prince cap. 11 (note) e § 12.4</b><p>Prince elenca i problemi della BatchNorm: batch piccoli danno stime rumorose, è scomoda nelle reti ricorrenti (statistiche diverse per ogni passo, sequenze di test più lunghe di quelle di training) e richiede l'intero batch, difficile con l'addestramento distribuito. Nelle note del cap. 12 ricorda che Vaswani et al. scelsero la LayerNorm perché le statistiche dei dati testuali variano molto fra batch.</p></div>
""", printed=P(34))

s(35, "What ViT Learns", """
<ul>
<li><b>Figura a sinistra</b> («Position embedding similarity»): una griglia 7 × 7 di riquadri, uno per posizione di patch (riga e colonna d'ingresso); ogni riquadro mostra la <b>similarità coseno</b> fra la codifica posizionale di quella patch e quelle di tutte le altre. Ogni riquadro è chiaro sulla propria posizione e, più debolmente, sulla stessa <b>riga</b> e sulla stessa <b>colonna</b>.</li>
<li>Quindi il ViT impara da solo a codificare la struttura <b>2D</b> dell'immagine nelle codifiche posizionali, pur avendole ricevute come una lista 1D.</li>
<li><b>Figura a destra</b> (ViT-L/16): ogni punto è una testa di attenzione in uno strato; l'altezza è la <b>distanza media di attenzione</b> in pixel (distanza fra query e key, pesata con i pesi di attenzione). È l'analogo del campo recettivo di una CNN.</li>
<li>Già nei primi strati alcune teste guardano <b>localmente</b> (pochi pixel) e altre già molto <b>lontano</b> (oltre 100 pixel); salendo di strato tutte le teste diventano globali.</li>
</ul>
<p>Fonte: Dosovitskiy et al. 2021, fig. 7 e 10. La griglia 7 × 7 corrisponde a un modello con patch 32 (224/32 = 7: nel paper è ViT-L/32), il grafico delle distanze a ViT-L/16 con 24 strati.</p>
<div class="box x"><b>Approfondimento</b>La distanza media nei primi strati spiega perché il ViT ha un bias induttivo debole ma non nullo in pratica: le teste locali imparano a fare quello che una conv fa per costruzione. Con pochi dati non ci riesce bene, ed è uno dei motivi per cui il ViT ha bisogno di grandi pre-training (slide 39). Il visionbook (fig. 26.12) mostra mappe di attenzione costruite a mano usando il colore medio delle patch come query e key.</div>
""", printed=P(35))

s(36, "ViT Attention Rollout", """
<ul>
<li><b>Attention rollout</b>: combina <b>ricorsivamente</b> le mappe di attenzione di tutti gli strati per stimare quanto la rappresentazione finale del [CLS] dipende da ciascuna patch d'ingresso.</li>
<li>Produce una visualizzazione simile a una mappa di salienza <b>senza supervisione a livello di pixel</b>, usando solo l'attenzione imparata durante il training di classificazione.</li>
<li>Dà un'idea intuitiva di come fluisce l'informazione spaziale in un ViT, ma è un'<b>approssimazione</b>, non una spiegazione definitiva della predizione.</li>
</ul>
<p><b>Figura</b> (ViT, fig. 6): due coppie di immagini, un cane su un prato e un aereo in cielo; accanto a ciascuna la stessa immagine oscurata dove l'attenzione è bassa: restano illuminati solo il cane e l'aereo.</p>
<div class="box k"><b>Da saper fare</b>Come si calcola (Abnar e Zuidema 2020, usato nel paper del ViT): per ogni strato l si fa la media delle matrici di attenzione sulle teste, A<sub>l</sub>; si tiene conto del residuo con Ã<sub>l</sub> = ½(A<sub>l</sub> + I), rinormalizzando le righe; poi si moltiplicano: R = Ã<sub>L</sub> Ã<sub>L−1</sub> ⋯ Ã<sub>1</sub>. La riga di R del token [CLS], tolta la colonna del [CLS] e rimodellata in una griglia (H/P) × (W/P), è la mappa. È un'approssimazione perché ignora gli MLP, i value e le non linearità: considera solo «chi guarda chi».</div>
""", printed=P(36))

s(37, "ViT: CNNs in Disguise", """
<ul>
<li><b>Tokenizzazione</b>: dividere l'immagine in patch P × P non sovrapposte e proiettarle linearmente equivale a una <b>convoluzione con kernel P, stride P e niente padding</b> (C<sub>in</sub> = 3, C<sub>out</sub> = D).</li>
<li><b>Proiezioni QKV</b>: W<sup>Q</sup>, W<sup>K</sup>, W<sup>V</sup> applicano la stessa trasformazione lineare a ogni token, indipendentemente: sono <b>convoluzioni 1×1</b> sulla mappa di feature.</li>
<li><b>MLP</b>: i due strati lineari del blocco sono anch'essi conv 1×1 (D → 4D, poi 4D → D), con la non linearità puntuale in mezzo.</li>
<li>ViT e CNN usano entrambi trasformazioni lineari, normalizzazioni e connessioni residue; organizzano diversamente l'informazione spaziale.</li>
<li><b>L'unica vera differenza</b>: le CNN mescolano l'informazione spaziale con kernel <b>locali e fissi</b> (uguali per ogni immagine); i ViT con la self-attention, che calcola interazioni <b>dipendenti dall'ingresso</b> fra token, potenzialmente su tutta l'immagine.</li>
</ul>
<p>Tutte e tre le equivalenze sono corrette. In PyTorch il patch embedding del ViT si implementa proprio come <code>Conv2d(3, D, kernel_size=P, stride=P)</code>.</p>
<div class="box b"><b>Dal libro · {C26}, § 26.9</b><p>È il titolo del § 26.9 del visionbook, che percorre gli stessi tre punti: tokenizzazione = conv con kernel e stride K (§ 26.9.1, eq. 26.9: <code>conv(x_in, channels_in=3, channels_out=d, kernel=K, stride=K)</code>), proiezioni QKV = conv 1×1 (§ 26.9.2, fig. 26.16), MLP per token = conv 1×1 (§ 26.9.3). Aggiunge un punto che la slide non dice: i filtri devono essere 1×1, perché un kernel più grande romperebbe l'equivarianza alle permutazioni (l'uscita dipenderebbe da quale token è vicino a quale); quindi la rete <b>non ha alcun modo architetturale</b> di sapere la struttura spaziale, e la posizione deve entrare dagli ingressi (le codifiche posizionali, § 26.9.5.1). L'attenzione invece non è convoluzionale: è un'operazione globale (§ 26.9.5.2). Nell'eq. 26.9 la somma va da −K a K, che darebbe 2K + 1 tap: va letta su K posizioni.</p></div>
""".replace('{C26}', C26), printed=P(37))

s(38, "ViT Patch Tokens as a Feature Grid", """
<ul>
<li>Si scarta il token [CLS]: gli N = h × w token di patch rimanenti corrispondono alla <b>griglia spaziale</b> delle patch (h = H/P, w = W/P).</li>
<li>Ogni token è un vettore di feature di dimensione D: si rimodella la sequenza in una <b>mappa h × w × D</b>, conservando l'ordine originale delle patch.</li>
<li>Si ottiene una rappresentazione spaziale <b>grossolana</b> che può fare da uscita dell'encoder per la predizione densa.</li>
</ul>
<p><b>Figura</b>: una colonna di 9 token («Tokens (N=9)») e, dopo la freccia «reshape», una griglia 3 × 3.</p>
<p><b>Conseguenza</b>: le feature del ViT possono alimentare architetture encoder-decoder per compiti come la segmentazione semantica (SETR, DPT). Modelli gerarchici come SegFormer forniscono feature <b>multi-scala</b>, più simili a quelle delle backbone CNN.</p>
<div class="box k"><b>Da saper fare</b>ViT-B/16 su 224²: 196 token → mappa 14 × 14 × 768, cioè stride 16 rispetto all'immagine (una CNN ResNet arriva a stride 32). Su 512²: 32 × 32 × 768. Per tornare a piena risoluzione serve un decoder che sovracampioni di 16×; DPT prende i token da più strati del transformer, li rimodella in griglie, li porta a risoluzioni diverse e li fonde come in una U-Net.</div>
<div class="box b"><b>Dal libro · {C26}, § 26.7, e Prince § 12.10.3</b><p>Il libro osserva che un transformer produce un <b>insieme di token</b> e che per uscite in un altro formato (un vettore di logit, un'immagine per compiti image-to-image, rimando al § 34.6) serve uno strato d'uscita specifico per il compito. Prince § 12.10.3 descrive i transformer multi-scala (come Swin): come le CNN partono da patch piccole ad alta risoluzione e pochi canali, e via via riducono la risoluzione e aumentano i canali, quindi danno una piramide di feature.</p></div>
""".replace('{C26}', C26), printed=P(38))

s(39, "ViT vs. CNN", """
<table>
<tr><th></th><th>CNN</th><th>ViT</th></tr>
<tr><td>campo recettivo</td><td>da locale a globale</td><td>globale dal primo strato</td></tr>
<tr><td>bias induttivo</td><td>forte bias di località</td><td>bias spaziale più debole</td></tr>
<tr><td>efficienza nei dati</td><td>spesso buona anche con pochi dati</td><td>beneficia di pre-training su larga scala</td></tr>
<tr><td>scalabilità con dati e calcolo</td><td>scala bene</td><td>scala molto bene nei casi studiati</td></tr>
<tr><td>predizione densa</td><td>encoder-decoder</td><td>encoder-decoder</td></tr>
<tr><td>fusione multimodale</td><td>possibile, dipende dall'architettura</td><td>comoda, basata sui token</td></tr>
</table>
<p><b>Figura</b> (ViT, fig. 5, pannello ImageNet): accuratezza di transfer su ImageNet (asse verticale, 75–90%) contro il calcolo di pre-training (asse orizzontale logaritmico). Punti blu: Transformer (ViT); grigi: ResNet (BiT); arancioni: ibridi. A parità di calcolo i ViT stanno sopra le ResNet, e gli ibridi aiutano solo con poco calcolo.</p>
<p><b>Messaggio</b>: le CNN codificano priori spaziali più forti; i ViT permettono interazioni globali flessibili e spesso traggono vantaggio dal pre-training su larga scala.</p>
<div class="box b"><b>Dal libro · Prince § 12.10.2, e {C26}, § 26.2 e 26.9.5</b><p>Prince riporta il dato chiave: il ViT pre-addestrato su 303 milioni di immagini arriva all'11,45% di errore top-1 su ImageNet, ma senza un grande pre-training non batte le CNN: «il forte bias induttivo delle reti convoluzionali può essere superato solo con quantità di dati enormi». Il visionbook riassume la differenza in termini architetturali: le CNN sono «miopi» (ogni filtro vede solo il suo campo recettivo, fig. 26.1), i transformer hanno attenzione globale ma nessuna nozione di vicinato se non tramite le posizioni.</p></div>
""".replace('{C26}', C26), printed=P(39))

# ===================== SINTESI =====================

s(40, "One Architecture, Many Tasks?", """
<ul>
<li><b>In gran parte sì</b>: encoder-decoder + skip connection è una base flessibile; testa e loss si cambiano tenendo la backbone.</li>
<li><b>Ma non è gratis</b>: alcuni compiti chiedono più di una testa nuova.
<ul><li><b>Flusso ottico</b>: servono due frame e un passo di matching esplicito (cost volume, RAFT, slide 21).</li>
<li><b>Profondità</b>: la profondità monoculare ha un'ambiguità di scala; contesto multi-scala e loss adatte aiutano, ma la scala assoluta richiede in genere indizi o ipotesi in più (altezza nota della camera, oggetti di taglia nota, un sensore).</li>
<li><b>Pose</b>: una localizzazione precisa dei keypoint beneficia di feature ad alta risoluzione; alcuni metodi rifiniscono la predizione in modo iterativo (per esempio stacked hourglass), ma non è universale.</li></ul></li>
</ul>
<p><b>Messaggio</b>: FCN e U-Net (CNN) ed encoder basati su ViT sono ottimi punti di partenza per la predizione densa; i metodi allo stato dell'arte aggiungono spesso componenti specifici del compito.</p>
""", sec=("l17-concl", "Sintesi e riferimenti", "slide 40–43"), printed=P(40))

s(41, "Summary", """
<ul>
<li>La <b>predizione densa</b> produce uscite organizzate nello spazio: segmentazione, profondità, flusso ottico, pose.</li>
<li>Le CNN da classificazione sottocampionano progressivamente; la predizione densa recupera la risoluzione con un <b>encoder-decoder</b> e <b>skip connection</b>.</li>
<li><b>U-Net</b>: l'encoder-decoder canonico con skip, molto usato per la segmentazione, soprattutto in ambito medico.</li>
<li><b>ViT</b>: self-attention globale su patch, bias induttivo spaziale più debole delle CNN; i token di patch formano una griglia di feature, spesso seguita da un decoder o da un upsampling per le uscite dense.</li>
<li>Le <b>loss</b> (CE, Dice, focal) guidano il training; le <b>metriche</b> specifiche (mIoU, AbsRel, EPE, PCK) valutano le prestazioni.</li>
<li><b>Prossima lezione</b>: segmentazione avanzata (DeepLab, SegFormer…) e object detection.</li>
</ul>
""", printed=P(41))

s(42, "References", """
<p>Bibliografia della lezione (24 voci), raggruppata per argomento:</p>
<ul>
<li><b>Architetture dense</b>: Long, Shelhamer e Darrell 2015 (FCN); Ronneberger, Fischer e Brox 2015 (U-Net); Badrinarayanan et al. 2015 (SegNet); Zhao et al. 2017 (PSPNet); Milletari et al. 2016 (V-Net, Dice loss); Odena, Dumoulin e Olah 2016 (artefatti a scacchiera, Distill); Shi et al. 2016 (ESPCN, sub-pixel).</li>
<li><b>Transformer</b>: Vaswani et al. 2017; Devlin et al. 2019 (BERT, origine del [CLS]); Dosovitskiy et al. 2021 (ViT); Zheng et al. 2021 (SETR); Xie et al. 2021 (SegFormer); Ranftl et al. 2021 (DPT); Liu et al. 2021 (Swin); Su et al. 2021 (RoPE); Wu e He 2018 (GroupNorm).</li>
<li><b>Compiti e dataset</b>: Cordts et al. 2016 (Cityscapes); Ranftl et al. 2022 (MiDaS); Eigen, Puhrsch e Fergus 2014 (profondità da una immagine); Butler et al. 2012 (MPI-Sintel); Baker et al. 2011 (Middlebury); Teed e Deng 2020 (RAFT); Cao et al. 2017 (OpenPose).</li>
</ul>
<p>Le slide non citano il visionbook come testo di riferimento (solo per la figura del flusso ottico, slide 6): i capitoli corrispondenti sono nella sezione «Studia dal libro» in fondo.</p>
""", printed=P(42))

s(43, "Indice a miniature", """<p>Non è una slide di contenuto: l'ultima pagina del PDF (footer «43 / 43») mostra le miniature numerate delle pagine 1–42, in cinque righe, come indice visivo della lezione. Nessun appunto da aggiungere.</p>""", printed=P(43))
