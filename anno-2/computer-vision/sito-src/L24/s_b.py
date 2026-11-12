
# ===================== DALLE IMMAGINI AL TESTO: CAPTIONING =====================

s(35, "Translating Images into Text", R("""
<p>Divisoria della seconda parte: <i>image captioning via cross-attention</i>. Fin qui (CLIP) i due encoder producevano vettori da confrontare; ora il testo va <b>generato</b>, parola per parola, a partire dall'immagine.</p>
"""), kind='div', sec=("l24-caption", "Dalle immagini al testo: captioning", "slide 35–40"), printed='')

s(36, "Encoder-Decoder Translation Between Modalities", R("""
<p><b>Figura</b> (fig. 51.7 del libro, «Text-to-image»): a sinistra lo <b>spazio dei testi</b> (macchia gialla) con un testo <b>t</b>; l'<b>encoder f</b> lo porta in uno <b>spazio latente</b> (cerchio arancione) dove diventa <b>z</b>; il <b>decoder g</b> lo porta nello <b>spazio delle immagini</b> (macchia azzurra), dove l'immagine prodotta ℓ̂ cade vicino a quella vera ℓ: la distanza fra le due è l'<i>errore di predizione</i>. A destra lo stesso schema in verticale: il testo «A yellow bird sitting on a tree branch.» → f → z → g → la foto di un uccellino giallo su un ramo.</p>
<p>Nota: la figura mostra la direzione <b>testo → immagine</b>, mentre la sezione tratta quella <b>immagine → testo</b>; lo schema è lo stesso con i ruoli scambiati.</p>
<ul>
<li><b>Ricetta modulare</b>: un encoder f: 𝒳 → 𝒵 estrae una rappresentazione dell'ingresso, un decoder g: 𝒵 → 𝒴 produce l'uscita in un'altra modalità. Il traduttore è la composizione <b>g ∘ f</b>.</li>
<li>Se encoder e decoder sono <b>preaddestrati separatamente</b>, i loro spazi non coincidono: serve un <b>connettore</b> appreso che li allinei. È il ruolo che avranno il Q-Former di BLIP-2 (slide 39), la proiezione di LLaVA (slide 49) e l'adapter di Qwen-VL (slide 51).</li>
<li>Image-to-text genera la didascalia in modo <b>autoregressivo</b> (slide 37); text-to-image può usare un decoder a <b>diffusione</b>.</li>
</ul>
<div class="box b"><b>Dal libro · {C51}, § 51.4 Translating between Images and Text</b>
<p>Il libro estende la traduzione fra domini di immagini del {C34} (pix2pix, CycleGAN) a modalità diverse: per quasi ogni coppia X, Y esiste ormai un metodo «X2Y». Il punto delicato è che l'uscita di f non è detto sia un ingresso sensato per g: con un encoder di testo e un decoder di immagini, niente garantisce che g(f(t)) rappresenti davvero ciò che t descrive. Due strategie:</p>
<ol>
<li><b>fine-tuning</b> dell'intera catena g ∘ f su coppie {t<sup>(i)</sup>, ℓ<sup>(i)</sup>};</li>
<li>tenere f e g <b>congelati</b> e addestrare solo una funzione <b>h: 𝒵 → 𝒵</b> nello spazio latente, così che g ∘ h ∘ f mappi ogni t<sup>(i)</sup> nel suo ℓ<sup>(i)</sup>.</li>
</ol>
<p>La seconda strategia è esattamente l'idea dei VLM di questa lezione: h è il connettore (Q-Former, proiezione lineare o MLP, adapter a query), e congelare f e g costa poco e conserva ciò che i modelli preaddestrati sanno (cfr. moduli congelati, {C37} § 37.3.1).</p></div>
"""), printed=P(36))

s(37, "Image Captioning: Autoregressive Generation", R("""
<p>Una didascalia y<sub>1</sub>, …, y<sub>T</sub> (sequenza di token) si genera <b>un token alla volta</b>, condizionando sull'immagine x. La regola della catena scompone la probabilità della frase in un prodotto di probabilità condizionate:</p>
<span class="f">p<sub>θ</sub>(y | x) = ∏<sub>t=1</sub><sup>T</sup> p<sub>θ</sub>(y<sub>t</sub> | y<sub>&lt;t</sub>, x),     L<sub>caption</sub> = −∑<sub>t=1</sub><sup>T</sup> log p<sub>θ</sub>(y<sub>t</sub> | y<sub>&lt;t</sub>, x)</span>
<ul>
<li>Ogni fattore è una <b>classificazione</b> sul vocabolario: una softmax su V token (V = dimensione del vocabolario BPE della slide 8). La loss è la somma delle <b>cross-entropy</b> dei singoli passi (<a href="#L15">L15</a>), cioè la log-verosimiglianza negativa della didascalia vera.</li>
<li><b>Addestramento, teacher forcing</b>: al passo t il decoder riceve come prefisso i token <b>veri</b> y<sub>&lt;t</sub> della didascalia di riferimento, non quelli che ha predetto lui. Due vantaggi: (1) un errore iniziale non contamina i passi successivi, quindi l'addestramento è stabile; (2) tutti i T passi sono noti in anticipo, quindi con l'attenzione causale si calcolano le T predizioni <b>in parallelo</b> con un'unica passata.</li>
<li><b>Inferenza</b>: i token veri non ci sono più. Si parte da un token di inizio, si sceglie y<sub>1</sub> (il più probabile, oppure campionando, o con beam search), lo si riappende all'ingresso e si ripete fino al token di fine. Qui le passate sono <b>sequenziali</b>: T token = T passate.</li>
<li>Il condizionamento visivo entra in due modi, a seconda dell'architettura: <b>cross-attention</b> nel decoder (slide 38, BLIP-2, Qwen-VL) oppure <b>token visivi proiettati</b> messi in testa alla sequenza d'ingresso (LLaVA, slide 49).</li>
</ul>
<div class="box b"><b>Dal libro · {C32}, § 32.7 Autoregressive Density Models, e {C26}, § 26.10 Masked Attention</b>
<p>Il libro introduce i modelli autoregressivi sulle immagini (un pixel alla volta, ognuno una classificazione a 256 classi condizionata sui precedenti) e la regola della catena p(X) = ∏<sub>i</sub> p(x<sub>i</sub> | x<sub>1</sub>, …, x<sub>i−1</sub>), eq. 32.5. Per l'addestramento (§ 32.7.1) distingue due modi di fare i batch: coppie [sequenza, prossimo elemento] prese a caso, oppure <b>sequenze sovrapposte</b> (x<sub>1..n−1</sub> → x<sub>n</sub>, x<sub>2..n</sub> → x<sub>n+1</sub>, …). Il secondo è molto più efficiente con un transformer ad <b>attenzione causale</b>: la rappresentazione del token n dipende solo dai precedenti, quindi un'unica passata fornisce tutte le predizioni e le condivide. Nel § 26.10 la maschera causale è triangolare: i pesi di attenzione verso le posizioni future sono forzati a zero, così la predizione in posizione n non «vede» la risposta. Il libro non usa il termine <i>teacher forcing</i>, ma nel § 51.4.2 descrive proprio questo: in addestramento il decoder riceve le parole precedenti della didascalia vera; in campionamento riappende ogni parola generata.</p></div>
<div class="box x"><b>Approfondimento: exposure bias</b><p>Il prezzo del teacher forcing è una discrepanza fra addestramento e uso: in addestramento il modello vede sempre prefissi corretti, in inferenza vede i propri, che possono contenere errori mai incontrati prima, e l'errore si accumula lungo la frase (<i>exposure bias</i>). In pratica, con modelli grandi e decodifica a beam search o campionamento controllato, il problema è contenuto; resta però il motivo per cui le didascalie lunghe tendono a «derivare».</p></div>
<div class="box k"><b>Da saper fare</b><p>Scrivere p(y | x) con la regola della catena, dire cosa riceve il decoder al passo t in addestramento e in inferenza, e spiegare perché l'addestramento è parallelo e l'inferenza sequenziale.</p></div>
"""), printed=P(37))

s(38, "Image-to-Text: Cross-Attention", R("""
<p>Come entra l'immagine nel decoder testuale: le <b>query vengono dal testo</b> (stati nascosti del decoder), le <b>chiavi e i valori dall'immagine</b> (token visivi).</p>
<span class="f">Q = H W<sup>Q</sup>,   K = Z<sub>v</sub> W<sup>K</sup>,   V = Z<sub>v</sub> W<sup>V</sup>,   C = softmax(QK<sup>⊤</sup> / √d<sub>k</sub>) V</span>
<p>Dimensioni, una per una (le righe sono token):</p>
<table>
<tr><th>Matrice</th><th>Dimensioni</th><th>Significato</th></tr>
<tr><td>H</td><td>T × D<sub>t</sub></td><td>stati del decoder, uno per ciascuno dei T token di testo</td></tr>
<tr><td>Z<sub>v</sub></td><td>N × D<sub>v</sub></td><td>N token dell'immagine (per esempio 196 patch di un ViT)</td></tr>
<tr><td>W<sup>Q</sup>; W<sup>K</sup>; W<sup>V</sup></td><td>D<sub>t</sub> × d<sub>k</sub>; D<sub>v</sub> × d<sub>k</sub>; D<sub>v</sub> × d<sub>v</sub></td><td>proiezioni apprese: portano testo e immagine in uno spazio comune di dimensione d<sub>k</sub></td></tr>
<tr><td>Q; K; V</td><td>T × d<sub>k</sub>; N × d<sub>k</sub>; N × d<sub>v</sub></td><td>query testuali; chiavi e valori visivi</td></tr>
<tr><td>QK<sup>⊤</sup></td><td><b>T × N</b></td><td>riga t = quanto il token di testo t «guarda» ciascuno degli N token visivi</td></tr>
<tr><td>C</td><td>T × d<sub>v</sub></td><td>per ogni token di testo, una media pesata dei valori visivi</td></tr>
</table>
<ul>
<li>La matrice di attenzione è <b>rettangolare</b> (T × N), non quadrata: le due sequenze possono avere lunghezze e larghezze diverse (D<sub>t</sub> ≠ D<sub>v</sub>), basta che Q e K finiscano nella stessa dimensione d<sub>k</sub>.</li>
<li>L'uscita ha <b>una riga per token di testo</b>: la cross-attention aggiorna il testo con informazione visiva, l'immagine non viene modificata.</li>
<li><b>Niente maschera causale</b> nella cross-attention: ogni parola può guardare tutta l'immagine, che è nota fin dall'inizio. La causalità serve solo fra token di testo.</li>
<li>Nel decoder ci sono due sottostrati separati: <b>self-attention causale</b> (testo ↔ testo passato, matrice T × T triangolare) e <b>cross-attention</b> (testo → immagine, T × N), poi l'MLP. È lo schema del decoder del transformer originale.</li>
</ul>
<p><b>Figura</b> (fig. 51.11 del libro): in basso un <i>Image Encoder</i> con self-attention (archi incrociati) su tre patch di un uccellino; a destra un <i>Text Decoder</i> che riceve «A yellow bird» e predice, spostato di una posizione, «yellow bird sitting». Gli archi grigi sono la <b>cross-attn</b> dai token visivi ai token di testo; gli archi neri fra token di testo sono la <b>causal self-attn</b>: ogni token riceve solo da sé e dai precedenti.</p>
<div class="box b"><b>Dal libro · {C51}, § 51.4.2 Image-to-Text</b>
<p>Il libro scrive le stesse equazioni con i token come righe e pedici per la modalità: Q<sub>t</sub> = T<sub>t</sub>W<sub>t,q</sub><sup>⊤</sup>, K<sub>ℓ</sub> = T<sub>ℓ</sub>W<sub>ℓ,k</sub><sup>⊤</sup>, V<sub>ℓ</sub> = T<sub>ℓ</sub>W<sub>ℓ,v</sub><sup>⊤</sup>, A<sub>cross</sub> = softmax(Q<sub>t</sub>K<sub>ℓ</sub><sup>⊤</sup>/√m), T<sub>out,cross</sub> = A<sub>cross</sub>V<sub>ℓ</sub> (t = testo, ℓ = immagine; m, mai definito nel capitolo, è la dimensione di query e chiavi, il d<sub>k</sub> della slide). L'immagine «emette» i suoi valori, che vengono mescolati nei token di testo secondo i pesi di attenzione. Due differenze rispetto alla slide:</p>
<ul>
<li>il libro <b>somma</b> le uscite delle due attenzioni, T = w<sub>cross</sub>T<sub>out,cross</sub> + w<sub>self</sub>T<sub>out,self</sub> (pesi eventualmente appresi), cioè le mette in parallelo; la slide le mette in <b>serie</b> come sottostrati distinti. Sono due varianti dello stesso principio; la seconda è quella dei transformer encoder-decoder standard;</li>
<li>il libro nota che sono possibili varianti: cross-attention in ogni strato del decoder, oppure un encoder che <b>comprime</b> l'immagine in un solo token riassuntivo, risparmiando memoria e calcolo. La compressione dei token visivi è proprio ciò che fanno il Q-Former (32 token) e l'adapter di Qwen-VL (256).</li>
</ul>
<p>Rispetto alla self-attention del {C26} (§ 26.6) cambia una sola cosa: le query vengono da un insieme di token e chiavi e valori da un altro.</p></div>
<div class="box k"><b>Da saper fare</b><p>Con T = 12 token di testo, N = 196 patch, D<sub>t</sub> = 512, D<sub>v</sub> = 768, d<sub>k</sub> = d<sub>v</sub> = 64: W<sup>Q</sup> è 512 × 64, W<sup>K</sup> e W<sup>V</sup> 768 × 64; QK<sup>⊤</sup> è 12 × 196; C è 12 × 64. La self-attention causale dello stesso strato ha invece una matrice 12 × 12 triangolare inferiore. Saper dire chi fornisce query e chi chiavi/valori, e perché la cross-attention non ha maschera.</p></div>
"""), printed=P(38))

s(39, "BLIP-2: Bootstrapping Captioning from Frozen Models", R("""
<p><b>Figura</b> (Li et al., 2023): a sinistra un <i>Image Encoder</i> con il fiocco di neve (congelato), al centro il <b>Q-Former</b> (<i>Querying Transformer</i>) che riceve delle <i>Queries</i> apprese e del testo; a destra un <i>Large Language Model</i> congelato che, data una foto di un tramonto e la richiesta «Write a romantic message that goes along this photo», risponde «Love is like a sunset, it's hard to see it coming but when it does it's so beautiful». Sopra, le due fasi: <i>Vision-and-Language Representation Learning</i> e <i>Vision-to-Language Generative Learning</i>.</p>
<ul>
<li><b>Idea</b>: non addestrare né l'encoder visivo né il modello di linguaggio, che sono costosi e già bravi. Si addestra solo un <b>ponte</b> leggero fra i due: il Q-Former (188 M parametri nell'articolo).</li>
<li><b>Componenti preaddestrati</b>: encoder ViT da CLIP (ViT-L/14) o da EVA-CLIP (ViT-g/14); LLM della famiglia <b>OPT</b> (solo decoder) o <b>FlanT5</b> (encoder-decoder).</li>
<li><b>Stage 1, representation learning</b>: encoder visivo congelato, niente LLM. Si addestra il Q-Former con tre obiettivi insieme, <b>L<sub>ITC</sub> + L<sub>ITM</sub> + L<sub>ITG</sub></b> (slide 40): impara a estrarre dalle feature visive ciò che è rilevante per il testo.</li>
<li><b>Stage 2, generative pretraining</b>: encoder e LLM <b>entrambi congelati</b>. Le uscite del Q-Former passano per una <b>proiezione lineare</b> (fully connected) nello spazio degli embedding dell'LLM e vengono messe <b>davanti</b> al testo, come un prompt visivo (<i>soft prompt</i>). Si addestrano Q-Former e proiezione con la loss di linguaggio (per FlanT5 una prefix-LM: una parte del testo va all'encoder dell'LLM, il resto è il bersaglio).</li>
</ul>
<p>Perché funziona: l'LLM congelato non sa nulla di immagini, ma accetta qualunque sequenza di vettori nel suo spazio di embedding. Lo stage 1 fa sì che le 32 uscite del Q-Former contengano già informazione «linguistica», così lo stage 2 deve solo imparare a tradurle nel «dialetto» dell'LLM.</p>
<div class="box x"><b>Approfondimento: i numeri dell'articolo</b><p>Nel riassunto (arXiv 2301.12597) BLIP-2 supera Flamingo-80B di 8,7 punti nel VQAv2 zero-shot con 54 volte meno parametri addestrabili. I dati di pretraining sono gli stessi di BLIP: 129 M immagini (COCO, Visual Genome, CC3M, CC12M, SBU, parte di LAION-400M), con didascalie sintetiche filtrate (il «bootstrapping» del nome). Dell'encoder ViT si toglie l'ultimo strato e si usa il penultimo.</p></div>
"""), printed=P(39))

s(40, "BLIP-2: Inside the Q-Former", R("""
<p><b>Figura</b> (Li et al., 2023). A sinistra il Q-Former: due transformer che <b>condividono gli strati di self-attention</b>. Il ramo delle <i>Learned Queries</i> ha, in più, uno strato di <b>Cross Attention</b> verso le feature dell'immagine congelata (inserito «for every other block», uno strato sì e uno no) e un Feed Forward proprio; il ramo del testo («a cat wearing sunglasses») ha solo self-attention e Feed Forward. In cima i tre obiettivi: Image-Text Matching, Image-Text Contrastive Learning, Image-Grounded Text Generation. A destra tre <b>maschere di self-attention</b> sotto forma di griglie Q/T (grigio = mascherato).</p>
<ul>
<li><b>32 query apprese</b> di dimensione 768: sono parametri, uguali per tutte le immagini. Attraverso la cross-attention ciascuna «interroga» le feature congelate dell'immagine; l'uscita è sempre <b>Z ∈ ℝ<sup>32×768</sup></b>, molto più piccola delle feature del ViT (257 × 1024 per ViT-L/14). È un <b>collo di bottiglia</b>: obbliga a tenere solo l'informazione visiva utile per il testo.</li>
<li>Gli strati sono inizializzati da <b>BERT-base</b> (le cross-attention, che BERT non ha, partono casuali).</li>
<li>Le query interagiscono con il testo <b>solo tramite la self-attention condivisa</b>; la maschera decide chi vede chi, e cambia con l'obiettivo.</li>
</ul>
<table>
<tr><th>Obiettivo</th><th>Cosa fa</th><th>Maschera</th></tr>
<tr><td><b>ITC</b> (contrastivo)</td><td>allinea immagine e testo come CLIP: similarità fra ciascuna delle 32 uscite delle query e l'embedding [CLS] del testo, si prende la <b>massima</b>; InfoNCE con negativi nel batch</td><td><b>unimodale</b>: query vedono solo query, testo solo testo (altrimenti l'informazione passerebbe da una parte all'altra e il compito sarebbe banale)</td></tr>
<tr><td><b>ITM</b> (matching)</td><td>classificazione binaria: la coppia immagine-testo corrisponde? Ogni query passa per un classificatore lineare a 2 classi, i logit si mediano; negativi «difficili» scelti fra quelli con similarità alta</td><td><b>bidirezionale</b>: tutti vedono tutti, serve un confronto fine fra parole e regioni</td></tr>
<tr><td><b>ITG</b> (generazione)</td><td>generare la didascalia condizionata sull'immagine; il primo token di testo è un [DEC]</td><td><b>causale multimodale</b>: le query vedono le query ma non il testo; ogni token di testo vede tutte le query e i token di testo precedenti</td></tr>
</table>
<p>L'ITG è il punto chiave: il testo non ha accesso diretto all'immagine, può leggerla solo attraverso le query. Quindi le query sono costrette a raccogliere <b>tutta l'informazione necessaria per descrivere l'immagine</b>, che è ciò che serve poi all'LLM.</p>
<div class="box k"><b>Da saper fare</b><p>Disegnare le tre griglie di maschera 2 × 2 (blocchi QQ, QT, TQ, TT): ITC = QQ e TT visibili, QT e TQ mascherati; ITM = tutto visibile; ITG = QQ visibile, QT mascherato, TQ visibile, TT triangolare. E spiegare per ciascuna perché è così.</p></div>
<p>(Nella figura originale c'è il refuso «mutlimodal».)</p>
"""), printed=P(40))

# ===================== IL TESTO COME RAPPRESENTAZIONE E VQA =====================

s(41, "Text as a Visual Representation and VQA", R("""
<p>Divisoria: <i>what else can text represent about an image?</i> Il testo generato non è solo un'uscita: è a sua volta una <b>rappresentazione</b> dell'immagine, e diventa uno strumento per rispondere a domande.</p>
"""), kind='div', sec=("l24-vqa", "Il testo come rappresentazione e VQA", "slide 41–47"), printed='')

s(42, "Text as a Visual Representation", R("""
<p><b>Figura</b> (fig. 51.12 del libro): la foto di un gatto grigio su una sedia e quattro rappresentazioni calcolate da essa: il <b>modulo della trasformata di Fourier</b> (<a href="#L3">L3</a>), una <b>mappa di profondità</b> (MiDaS, <a href="#L18">L18</a>), le <b>feature DINO</b> visualizzate a colori (<a href="#L22">L22</a>), e il <b>testo</b> «a grey cat with green eyes standing on a chair» (prodotto da BLIP-2).</p>
<ul>
<li>Un'immagine si può rappresentare con pixel, profondità, feature apprese o <b>linguaggio naturale</b>: un modello image-to-text è solo un altro encoder visivo, con uscita testuale.</li>
<li><b>Vantaggi</b> del testo: è <b>semantico</b> e compatto, leggibile da una persona, e soprattutto è l'ingresso naturale dei <b>modelli di linguaggio</b> e di tutti gli strumenti NLP: dopo la traduzione si può ragionare sul contenuto con un LLM.</li>
<li><b>Svantaggi</b>: <b>perde informazione</b>. La didascalia sceglie cosa dire (il gatto, gli occhi) e tace su posizione esatta, illuminazione, texture, geometria; nessuno potrebbe ricostruire i pixel dalla frase.</li>
</ul>
<div class="box b"><b>Dal libro · {C51}, § 51.5 Text as a Visual Representation</b>
<p>Il libro mette il testo sullo stesso piano delle altre rappresentazioni viste nel corso: frequenze (Fourier), semantica e geometria della scena, embedding di feature (DINO, CLIP). Nella didascalia della figura osserva che i <b>pixel stessi</b> sono una quinta rappresentazione della scena, non «la» scena. Invita a chiedersi pregi e difetti di ciascuna; il pregio specifico del testo è che si <b>interfaccia con i modelli di linguaggio</b>. Nelle conclusioni (§ 51.7) il libro si spinge oltre: il linguaggio è una rappresentazione percettiva compatta e astratta di «cosa c'è dove» (la definizione di visione di Marr), forse il risultato di un lunghissimo representation learning dell'evoluzione umana.</p></div>
"""), printed=P(42))

s(43, "Visual Question Answering: Problem Definition", R("""
<p><b>Figura</b> (fig. 51.13 del libro): due esempi affiancati con la stessa foto di un uccellino giallo. La domanda passa in un encoder di testo f<sub>t</sub>, l'immagine in un encoder f<sub>ℓ</sub>, un decoder g<sub>t</sub> combina le due e produce la risposta: «What animal is this» → «Golden palm weaver» (un tessitore dorato); «What color is the bird» → «yellow». Stessa immagine, domande diverse, risposte diverse.</p>
<ul>
<li><b>VQA</b>: data un'immagine x e una domanda q, predire una risposta a.</li>
<li>Differenza con il captioning: la didascalia descrive ciò che è <b>saliente</b>; nel VQA l'informazione visiva da estrarre <b>dipende dalla domanda</b> (il colore, il conteggio, una relazione), e può richiedere ragionamento o conoscenze esterne.</li>
</ul>
<div class="box b"><b>Dal libro · {C51}, § 51.6 Visual Question Answering</b>
<p>Il libro presenta il VQA come una formulazione dell'obiettivo di un sistema visivo <b>del tutto generale</b>, a cui si può chiedere qualunque cosa su un'immagine: una specie di <b>test di Turing</b> per l'intelligenza visiva. Lo lascia come esercizio: modificare il transformer della fig. 51.11 (slide 38) per il VQA. Bastano un <b>encoder di testo</b> per la domanda, un <b>encoder di immagini</b> e un <b>decoder di testo</b> per la risposta, collegati con gli strumenti del capitolo; il pezzo critico sono i <b>dati</b>, tuple {[domanda, immagine], risposta}. Come implementazione di riferimento rimanda a BLIP-2 (slide 46).</p>
<p>Una soluzione all'esercizio: concatenare i token della domanda prima di quelli della risposta nel decoder (con un separatore), lasciare che tutti facciano cross-attention ai token dell'immagine, e calcolare la loss solo sui token della risposta.</p></div>
"""), printed=P(43))

s(44, "Visual Question Answering: Commonsense Knowledge", R("""
<p><b>Figura</b> (Antol et al., 2015, il dataset VQA): quattro immagini con due domande ciascuna. Un ragazzo con dei «baffi» fatti di banana («What color are her eyes?», «What is the mustache made of?»); una pizza («How many slices of pizza are there?», «Is this a vegetarian pizza?»); una scena a cartone animato con un picnic sotto un albero («Is this person expecting company?», «What is just under the tree?»); un ragazzo con occhiali che mangia («Does it appear to be rainy?», «Does this person have 20/20 vision?»).</p>
<ul>
<li>Le domande sono in linguaggio naturale, scritte da <b>annotatori umani</b> (circa 0,25 M immagini, 0,76 M domande, 10 M risposte nell'articolo): ogni domanda ha 10 risposte di persone diverse.</li>
<li>Possono richiedere <b>riconoscimento</b> (di cosa sono fatti i baffi), <b>conteggio</b> (le fette), <b>relazioni spaziali</b> (cosa c'è sotto l'albero) e <b>senso comune</b>: «aspetta ospiti?» si deduce dal numero di piatti; «ha la vista perfetta?» dal fatto che porta gli occhiali; «vegetariana?» richiede di sapere cosa contiene una pizza vegetariana.</li>
<li>La risposta giusta dipende quindi sia dall'<b>evidenza visiva</b> sia dalla <b>conoscenza del mondo</b>: è il motivo per cui i VLM moderni attaccano l'immagine a un LLM.</li>
</ul>
<div class="box x"><b>Approfondimento: come si valuta</b><p>Con 10 risposte umane per domanda, la metrica del VQA considera una risposta corretta al 100% se almeno 3 annotatori l'hanno data: accuratezza = min(#umani che hanno dato quella risposta / 3, 1). Così si tollerano sinonimi e risposte ambigue. Il dataset ha anche un bias noto: molte domande si «indovinano» senza guardare l'immagine (per «Is there a…?» la risposta più frequente è sì), ragione per cui sono nate versioni bilanciate (VQAv2).</p></div>
"""), printed=P(44))

s(45, "Visual Question Answering: Two Formulations", R("""
<p>Due modi di impostare il problema:</p>
<table>
<tr><th></th><th>Classificazione della risposta</th><th>VQA generativo</th></tr>
<tr><td>Modello</td><td>p<sub>θ</sub>(a | x, q), a ∈ {a<sub>1</sub>, …, a<sub>K</sub>}</td><td>p<sub>θ</sub>(a | x, q) = ∏<sub>t=1</sub><sup>T</sup> p<sub>θ</sub>(a<sub>t</sub> | a<sub>&lt;t</sub>, x, q)</td></tr>
<tr><td>Uscita</td><td>una softmax su K risposte fisse, di solito le più frequenti nel training set (nell'articolo VQA le 1000 più frequenti)</td><td>la risposta come sequenza di token, generata in modo autoregressivo</td></tr>
<tr><td>Loss</td><td>cross-entropy sulla classe</td><td>L<sub>VQA</sub> = −∑<sub>t</sub> log p<sub>θ</sub>(a<sub>t</sub> | a<sub>&lt;t</sub>, x, q)</td></tr>
<tr><td>Limite / pregio</td><td>una risposta fuori dal vocabolario <b>non si può predire</b>; però è semplice e la valutazione è immediata</td><td>risposte aperte, anche lunghe o mai viste; ma la valutazione è più difficile (sinonimi, frasi)</td></tr>
<tr><td>Esempi</td><td>i modelli VQA classici (CNN + LSTM + classificatore)</td><td>BLIP-2 (query del Q-Former), LLaVA (token visivi proiettati)</td></tr>
</table>
<ul>
<li>La formulazione generativa è <b>identica al captioning</b> (slide 37) con un condizionamento in più, la domanda q: il VQA è un captioning guidato da una domanda.</li>
<li>La classificazione è il caso particolare in cui ogni risposta è un solo «token» di un vocabolario di K risposte.</li>
</ul>
"""), printed=P(45))

s(46, "Visual Question Answering: BLIP-2", R("""
<p><b>Figura</b> (Li et al., 2023, figura del fine-tuning VQA): la foto di un gatto con gli occhiali da sole entra nell'<i>Image Encoder</i>; il <b>Q-Former</b> riceve le query apprese <b>e la domanda</b> «What is the cat wearing?»; le sue uscite passano per un <i>Fully Connected</i>; l'<b>LLM</b> riceve i token visivi proiettati <b>e di nuovo la domanda</b>, e genera la risposta «sunglasses».</p>
<ul>
<li><b>Fine-tuning per il VQA</b>: si aggiornano <b>image encoder e Q-Former</b>, l'<b>LLM resta congelato</b>.</li>
<li>La domanda condiziona <b>due volte</b>: nel Q-Former, dove i token della domanda interagiscono con le query tramite la self-attention e quindi <b>orientano la cross-attention</b> verso le regioni dell'immagine utili per quella domanda (estrae «gli occhiali», non «il colore del pelo»); e nell'LLM, che la legge insieme ai token visivi.</li>
<li>L'LLM genera la risposta in modo autoregressivo: formulazione generativa della slide 45.</li>
</ul>
<div class="box w"><b>Attenzione: la figura contraddice il testo</b><p>Nella figura l'<i>Image Encoder</i> ha il fiocco di neve, cioè sembra congelato. Vale il testo della slide: l'articolo (arXiv 2301.12597, § 4.3) dice esplicitamente che nel fine-tuning VQA si aggiornano i parametri del Q-Former <b>e dell'image encoder</b>, tenendo congelato l'LLM. La figura è presa così com'è dall'articolo, che ha la stessa incoerenza. Nel pretraining (slide 39), invece, l'image encoder è davvero congelato.</p></div>
"""), printed=P(46))

s(47, "Language as a Visual Representation", R("""
<p>Riepilogo della sezione, tre idee:</p>
<ul>
<li>Una <b>didascalia</b> codifica una <b>selezione</b> del contenuto visivo in linguaggio naturale (slide 42: rappresentazione semantica ma con perdita).</li>
<li>Il <b>VQA</b> estende il captioning condizionando la generazione su una <b>domanda</b>: invece di dire ciò che è saliente, dice ciò che è stato chiesto (slide 45).</li>
<li>I <b>modelli di linguaggio preaddestrati</b> possono combinare l'informazione visiva con conoscenza linguistica e del mondo (il senso comune della slide 44). È il ponte verso la sezione successiva: invece di addestrare un decoder testuale da zero, si usa un LLM già pronto.</li>
</ul>
"""), printed=P(47))

# ===================== VLM CON INSTRUCTION TUNING =====================

s(48, "Instruction-Tuned VLMs", R("""
<p>Divisoria: <i>from frozen encoders to chat-style assistants</i>. Si passa dai modelli che fanno un compito (didascalia, risposta breve) agli <b>assistenti</b> che seguono istruzioni arbitrarie su un'immagine, in forma di conversazione.</p>
"""), kind='div', sec=("l24-instr", "VLM con instruction tuning", "slide 48–53"), printed='')

s(49, "LLaVA: Visual Instruction Tuning", R("""
<p><b>Figura</b> (Liu et al., 2023): in basso un <i>Vision Encoder</i> che trasforma l'immagine X<sub>v</sub> in feature Z<sub>v</sub>; una <i>Projection W</i> le porta in token H<sub>v</sub>; accanto ci sono i token H<sub>q</sub> dell'istruzione testuale X<sub>q</sub>; tutti entrano nel <i>Language Model f<sub>φ</sub></i>, che produce la risposta X<sub>a</sub> (i pallini verdi in alto).</p>
<span class="f">Z<sub>v</sub> = f<sub>v</sub>(x) ∈ ℝ<sup>N×D<sub>v</sub></sup>,   H<sub>v</sub> = Z<sub>v</sub>W ∈ ℝ<sup>N×D<sub>LLM</sub></sup>,   L<sub>LLaVA</sub> = −∑<sub>t</sub> log p<sub>θ</sub>(y<sub>t</sub> | y<sub>&lt;t</sub>, H<sub>v</sub>, X<sub>q</sub>)</span>
<ul>
<li><b>Componenti preaddestrati</b>: encoder visivo <b>CLIP ViT-L/14</b> e LLM <b>Vicuna</b> (un LLaMA addestrato a conversare).</li>
<li><b>Connettore</b>: una sola matrice W ∈ ℝ<sup>D<sub>v</sub>×D<sub>LLM</sub></sup>, applicata <b>token per token</b>. Ogni patch diventa una «parola» nello spazio degli embedding dell'LLM: con immagini 224 × 224 e patch 14 sono 16 × 16 = <b>256 token visivi</b>, che entrano nella sequenza insieme ai token di testo.</li>
<li>Nell'LLM non c'è cross-attention: token visivi e testuali sono trattati allo stesso modo dalla <b>self-attention causale</b>. Le parole della risposta «vedono» l'immagine perché i token visivi stanno prima di loro nella sequenza.</li>
<li>La loss è quella del captioning (slide 37), calcolata solo sui token della <b>risposta</b> (i token dell'istruzione e quelli visivi sono condizionamento, non bersaglio).</li>
<li>L'encoder visivo resta <b>congelato</b>. <b>LLaVA-1.5</b> sostituisce la proiezione lineare con un <b>MLP a due strati</b> (e usa CLIP ViT-L a 336 px, quindi 24 × 24 = 576 token).</li>
</ul>
<div class="box x"><b>Approfondimento: confronto con BLIP-2</b><p>BLIP-2 <b>comprime</b> l'immagine in 32 query con un modulo addestrato a parte e un LLM congelato; LLaVA <b>non comprime</b> (tutti i 256 token) e usa il connettore più semplice possibile, ma addestra l'LLM. La lezione di LLaVA è che, con dati di istruzioni di buona qualità, un connettore banale basta. Il prezzo è la sequenza più lunga (costo dell'attenzione quadratico nel numero di token).</p></div>
"""), printed=P(49))

s(50, "LLaVA: Training Stages", R("""
<table>
<tr><th>Componente</th><th>Stage 1: feature alignment</th><th>Stage 2: instruction tuning</th></tr>
<tr><td>Encoder visivo CLIP</td><td>congelato</td><td>congelato</td></tr>
<tr><td>Proiezione W</td><td><b>addestrata</b></td><td><b>addestrata</b></td></tr>
<tr><td>LLM Vicuna</td><td>congelato</td><td><b>addestrato</b></td></tr>
</table>
<ul>
<li><b>Stage 1, allineamento delle feature</b>: si addestra <b>solo W</b> su <b>595K coppie</b> immagine-didascalia filtrate da CC3M, riscritte come istruzioni del tipo «descrivi brevemente l'immagine» → didascalia. Con tutto il resto congelato, W impara un «tokenizer visivo» compatibile con l'LLM: è la h: 𝒵 → 𝒵 della slide 36.</li>
<li><b>Stage 2, visual instruction tuning</b>: si addestrano W e Vicuna su <b>158K</b> esempi di istruzioni legate a immagini, di tre tipi: conversazioni (58K), descrizioni dettagliate (23K) e ragionamento complesso (77K).</li>
</ul>
<p>Perché due stadi: se si sbloccasse subito l'LLM con una W casuale, i token visivi sarebbero rumore e il gradiente rischierebbe di rovinare le capacità linguistiche dell'LLM. Prima si allinea il connettore a basso costo, poi si adatta l'LLM al formato conversazionale.</p>
<div class="box x"><b>Approfondimento: come sono state generate le 158K istruzioni</b><p>«GPT-4-generated» va letto con attenzione: il GPT-4 usato era <b>solo testuale</b> e non vedeva l'immagine. Per ogni immagine COCO gli venivano date due rappresentazioni simboliche, le <b>didascalie</b> e i <b>bounding box</b> degli oggetti con le categorie, e da queste scriveva domande e risposte come se vedesse la scena (arXiv 2304.08485, § 3). È un esempio concreto della slide 42: il testo usato come rappresentazione dell'immagine.</p></div>
"""), printed=P(50))

s(51, "Qwen-VL: A Query-Based Cross-Attention Adapter", R("""
<p><b>Figura</b> (Bai et al., 2023): dal basso, un <b>ViT</b> (con la fiammella: addestrabile), un blocco <b>CrossAttn</b> che riceve a sinistra le <i>Learnable Query Embs</i>, e sopra il <b>QwenLM</b>; accanto un'icona di documento per il testo d'ingresso.</p>
<ul>
<li><b>Componenti preaddestrati</b>: encoder <b>OpenCLIP ViT-bigG/14</b> e LLM <b>Qwen-7B</b>.</li>
<li><b>VL Adapter</b>: <b>256 query apprese</b> fanno cross-attention sulle feature del ViT (query = parametri appresi, chiavi e valori = feature dell'immagine: lo schema della slide 38 con le query al posto del testo). L'uscita ha <b>lunghezza fissa</b>, 256 token, qualunque sia la risoluzione: a 448 × 448 il ViT produce 32 × 32 = 1024 patch, compresse 4 volte.</li>
<li>È un <b>singolo strato</b> di cross-attention, con <b>codifiche posizionali 2D</b> aggiunte a query e chiavi per non perdere la posizione delle patch durante la compressione (importante per il grounding, slide 56).</li>
<li>Rispetto a LLaVA: l'adapter <b>riduce</b> il numero di token visivi, mentre il proiettore di LLaVA lavora token per token. Rispetto a BLIP-2: niente Q-Former a molti strati con tre loss; un solo strato di cross-attention addestrato insieme al resto.</li>
</ul>
<div class="box x"><b>Approfondimento: il grounding in Qwen-VL</b><p>Qwen-VL scrive i box <b>come testo</b>: coordinate normalizzate nell'intervallo [0, 1000) racchiuse fra token speciali &lt;box&gt;…&lt;/box&gt;, con la frase di riferimento fra &lt;ref&gt;…&lt;/ref&gt;. Così il grounding diventa generazione di token, senza una testa di regressione dedicata (arXiv 2308.12966).</p></div>
"""), printed=P(51))

s(52, "Qwen-VL: Training Stages", R("""
<table>
<tr><th>Componente</th><th>Stage 1</th><th>Stage 2</th><th>Stage 3</th></tr>
<tr><td>ViT</td><td>addestrato</td><td>addestrato</td><td><b>congelato</b></td></tr>
<tr><td>VL Adapter</td><td>addestrato</td><td>addestrato</td><td>addestrato</td></tr>
<tr><td>Qwen-LM</td><td><b>congelato</b></td><td>addestrato</td><td>addestrato</td></tr>
</table>
<ul>
<li><b>Stage 1, pretraining</b>: <b>1,4 miliardi</b> di coppie immagine-testo ripulite, a risoluzione <b>224²</b>. Si addestrano ViT e adapter, LLM congelato: come lo stage 1 di LLaVA, ma qui si adatta anche l'encoder visivo.</li>
<li><b>Stage 2, pretraining multi-task</b>: tutto sbloccato, risoluzione <b>448²</b>, sette compiti insieme: captioning, VQA, grounding, referring grounding, grounded captioning, OCR e generazione di solo testo (per non perdere le capacità linguistiche).</li>
<li><b>Stage 3, instruction tuning</b>: adapter e LLM su <b>350K</b> dialoghi, ViT congelato. Il risultato è <b>Qwen-VL-Chat</b>.</li>
</ul>
<p>Il passaggio 224² → 448² serve per OCR e grounding, che hanno bisogno di dettagli fini; grazie all'adapter i token per l'LLM restano 256.</p>
<div class="box k"><b>Cosa si congela e cosa si addestra: tabella riassuntiva</b>
<table>
<tr><th>Modello</th><th>Encoder visivo</th><th>Connettore</th><th>LLM</th></tr>
<tr><td>CLIP (slide 10–20)</td><td>addestrato da zero</td><td>proiezioni lineari, addestrate</td><td>(text encoder, addestrato da zero)</td></tr>
<tr><td>LiT (slide 21)</td><td>congelato (preaddestrato)</td><td>addestrato</td><td>(text encoder addestrato)</td></tr>
<tr><td>BLIP-2 stage 1</td><td>congelato</td><td>Q-Former addestrato (ITC + ITM + ITG)</td><td>non usato</td></tr>
<tr><td>BLIP-2 stage 2</td><td>congelato</td><td>Q-Former + FC addestrati</td><td>congelato</td></tr>
<tr><td>BLIP-2 fine-tuning VQA</td><td><b>addestrato</b></td><td>Q-Former addestrato</td><td>congelato</td></tr>
<tr><td>LLaVA stage 1</td><td>congelato</td><td>W addestrata</td><td>congelato</td></tr>
<tr><td>LLaVA stage 2</td><td>congelato</td><td>W addestrata</td><td><b>addestrato</b></td></tr>
<tr><td>Qwen-VL stage 1</td><td><b>addestrato</b></td><td>adapter addestrato</td><td>congelato</td></tr>
<tr><td>Qwen-VL stage 2</td><td>addestrato</td><td>adapter addestrato</td><td>addestrato</td></tr>
<tr><td>Qwen-VL stage 3</td><td>congelato</td><td>adapter addestrato</td><td>addestrato</td></tr>
</table>
<p>Regola generale: il <b>connettore si addestra sempre</b>; il primo stadio tiene congelato l'LLM per non danneggiarlo con token visivi ancora privi di senso; l'LLM si sblocca quando serve insegnare il formato delle istruzioni (LLaVA, Qwen-VL) oppure resta congelato per costo e conservazione (BLIP-2).</p></div>
"""), printed=P(52))

s(53, "Comparing VLM Architectures", R("""
<table>
<tr><th>Modello</th><th>Rappresentazione visiva</th><th>Connettore</th><th>Componente linguistica</th></tr>
<tr><td>CLIP</td><td>un embedding <b>globale</b> per immagine</td><td>proiezioni lineari</td><td>text encoder (non genera)</td></tr>
<tr><td>BLIP-2</td><td>token visivi</td><td>Q-Former + proiezione (32 token)</td><td>LLM preaddestrato <b>congelato</b></td></tr>
<tr><td>LLaVA-1.5</td><td>token visivi di CLIP</td><td>MLP a due strati (tutti i token)</td><td>LLM preaddestrato, <b>riaddestrato</b></td></tr>
<tr><td>Qwen-VL</td><td>feature del ViT</td><td>cross-attention a query (256 token)</td><td>Qwen-7B</td></tr>
</table>
<ul>
<li>Due famiglie: <b>dual encoder</b> (CLIP: due vettori confrontati, utile per classificazione zero-shot e retrieval, non genera testo) e <b>VLM generativi</b> (encoder visivo + connettore + LLM: generano testo condizionato).</li>
<li>Fra i generativi la scelta chiave è il connettore: <b>comprimere con query apprese</b> (BLIP-2, Qwen-VL: sequenze corte, numero di token fisso) o <b>proiettare ogni token</b> (LLaVA: nessuna perdita, sequenze lunghe). Riprende la slide 4: embedding globale contro sequenza di token visivi.</li>
</ul>
"""), printed=P(53))

# ===================== ALTRI COMPITI: RAGIONAMENTO E GROUNDING =====================

s(54, "Other VLM Tasks", R("""
<p>Divisoria: <i>reasoning and grounding</i>. Due compiti che mettono alla prova ciò che CLIP fa male (slide 33–34): ragionare su relazioni e conteggi, e localizzare ciò che una frase descrive.</p>
"""), kind='div', sec=("l24-task", "Altri compiti: ragionamento e grounding", "slide 54–56"), printed='')

s(55, "Visual Reasoning: NLVR2 Benchmark", R("""
<p><b>Figura</b> (Suhr et al., 2019): due foto affiancate, una con molte ghiande e una con una sola ghianda, e la frase «One image shows exactly two brown acorns in back-to-back caps on green foliage.»; la casella <b>False</b> è spuntata.</p>
<ul>
<li><b>NLVR2</b> (<i>Natural Language for Visual Reasoning for Real</i>): data una <b>coppia di foto</b> e un'affermazione in linguaggio naturale, decidere se è <b>vera</b>.</li>
</ul>
<span class="f">p<sub>θ</sub>(y | x<sub>1</sub>, x<sub>2</sub>, s), y ∈ {True, False};   L<sub>NLVR2</sub> = −log p<sub>θ</sub>(y | x<sub>1</sub>, x<sub>2</sub>, s)</span>
<ul>
<li>È una <b>classificazione binaria</b> con cross-entropy, ma per rispondere servono <b>confronto</b> fra due immagini, <b>conteggio</b> («exactly two») e <b>relazioni</b> («back-to-back», «on green foliage»): proprio le capacità che mancano a un embedding globale alla CLIP (slide 33–34).</li>
<li>Le frasi sono state scritte da annotatori a cui si chiedeva di descrivere qualcosa che vale per alcune coppie e non per altre: la risposta non si indovina dagli oggetti presenti.</li>
<li>La coppia di immagini richiede un'architettura che ne riceva due: per esempio i token visivi di entrambe le immagini nella stessa sequenza.</li>
</ul>
"""), printed=P(55))

s(56, "Visual Grounding: Referring Expressions", R("""
<p><b>Figura</b> (Yu et al., 2016): due giraffe, una con un riquadro verde; a destra le espressioni per lo stesso oggetto nei tre dataset. RefCOCO: «giraffe on left», «first giraffe on left». RefCOCO+: «giraffe with lowered head», «giraffe head down». RefCOCOg: «an adult giraffe scratching its back with its horn», «giraffe hugging another giraffe».</p>
<ul>
<li><b>Visual grounding</b> (comprensione di espressioni referenziali): data un'immagine x e un'espressione r che indica <b>un</b> oggetto, predire il suo <b>bounding box</b>.</li>
</ul>
<span class="f">b̂ = f<sub>θ</sub>(x, r)     oppure     k̂ = arg max<sub>k</sub> s<sub>θ</sub>(b<sub>k</sub>, r, x)</span>
<p>Due formulazioni, che ricalcano la detection di <a href="#L19">L19</a>:</p>
<ul>
<li><b>Regressione diretta</b>: la rete produce le 4 coordinate del box (come la testa di regressione di un detector, <a href="#L19">L19</a>, o come testo nei VLM come Qwen-VL). Loss tipiche: L1 sulle coordinate più una loss sull'IoU.</li>
<li><b>Selezione fra regioni candidate</b> {b<sub>k</sub>}: un detector propone dei box (le region proposal di Faster R-CNN, <a href="#L19">L19</a>), un modello assegna a ciascuno un punteggio di compatibilità s<sub>θ</sub>(b<sub>k</sub>, r, x) con la frase e si prende il massimo. È un retrieval testo → regione: il «red circle» della slide 32 fa esattamente questo con CLIP, marcando ogni candidato e confrontandolo con la frase.</li>
<li>Valutazione: una predizione è corretta se l'<b>IoU</b> con il box vero supera 0,5 (<a href="#L19">L19</a>).</li>
</ul>
<p>I tre dataset (immagini di COCO) differiscono per il protocollo di annotazione: <b>RefCOCO</b> e <b>RefCOCO+</b> raccolti con un gioco interattivo a due giocatori, con espressioni brevi; in <b>RefCOCO+</b> erano <b>vietate le parole di posizione</b> («left», «first»), quindi bisogna descrivere l'aspetto (testa abbassata); <b>RefCOCOg</b> è stato raccolto in modo non interattivo e ha espressioni più lunghe e descrittive.</p>
<div class="box k"><b>Da saper fare</b><p>Spiegare la differenza fra grounding e detection (una frase → un oggetto specifico, non tutte le istanze di una classe), scrivere le due formulazioni e dire perché in RefCOCO+ conta l'aspetto e non la posizione.</p></div>
"""), printed=P(56))

# ===================== SINTESI E RIFERIMENTI =====================

s(57, "Recap: VLM Tasks", R("""
<table>
<tr><th>Compito</th><th>Ingresso</th><th>Uscita</th><th>Obiettivo di addestramento</th><th>Esempio</th></tr>
<tr><td>Classificazione zero-shot</td><td>immagine + nomi delle classi</td><td>etichetta</td><td>contrastivo immagine-testo</td><td>CLIP</td></tr>
<tr><td>Captioning</td><td>immagine</td><td>didascalia</td><td>language modeling autoregressivo</td><td>BLIP-2</td></tr>
<tr><td>Visual QA</td><td>immagine + domanda</td><td>risposta</td><td>classificazione o generazione della risposta</td><td>BLIP-2, LLaVA</td></tr>
<tr><td>Ragionamento visivo</td><td>coppia di immagini + affermazione</td><td>vero / falso</td><td>classificazione binaria</td><td>dataset NLVR2</td></tr>
<tr><td>Visual grounding</td><td>immagine + descrizione</td><td>bounding box</td><td>matching di regioni o localizzazione</td><td>dataset RefCOCO</td></tr>
</table>
<p>Da notare: le due ultime righe citano un <b>dataset</b> e non un modello; un VLM generativo come Qwen-VL fa tutti i compiti della tabella con la stessa loss autoregressiva, scrivendo come testo anche «True» o le coordinate del box.</p>
"""), sec=("l24-concl", "Sintesi e riferimenti", "slide 57–61"), printed=P(57))

s(58, "Summary", R("""
<ul>
<li><b>Allineamento visione-linguaggio</b>: CLIP impara uno spazio di embedding comune con apprendimento contrastivo, che abilita classificazione zero-shot e retrieval immagine-testo.</li>
<li><b>Fusione multimodale</b>: BLIP-2 e Qwen-VL usano cross-attention con query apprese; LLaVA proietta i token visivi nello spazio degli embedding dell'LLM.</li>
<li><b>Generazione di testo</b>: i VLM generativi predicono token in modo autoregressivo, condizionati su immagine e testo.</li>
<li><b>Strategie di addestramento</b>: BLIP-2 congela entrambe le backbone preaddestrate nel pretraining; LLaVA e Qwen-VL riaddestrano componenti diverse nei vari stadi (tabella nella scheda della slide 52).</li>
</ul>
"""), printed=P(58))

s(59, "Next Lectures", R("""
<p>Prossime lezioni:</p>
<ul>
<li><b>Parameter-efficient fine-tuning (PEFT)</b>: adattare modelli grandi aggiornando pochi parametri (per esempio adattatori a basso rango come LoRA, già accennati nel {C37} § 37.3.1). È il seguito naturale di questa lezione, dove si è visto quanto conta scegliere cosa congelare.</li>
<li><b>Laboratorio su VLM e PEFT</b>.</li>
</ul>
"""), printed=P(59))

s(60, "References", R("""
<p>Bibliografia della lezione, in due colonne. Gli articoli principali, nell'ordine della lezione:</p>
<ul>
<li><b>CLIP</b>: Radford et al., ICML 2021; InfoNCE: van den Oord et al. 2018; precursori: Mori et al. 1999, Ordonez et al. 2011 (Im2Text), Joulin et al. 2016, Li et al. 2017 (visual n-grams), VirTex (Desai e Johnson), ICMLM (Bulent Sariyildiz et al.), ConVIRT (Zhang et al.).</li>
<li><b>Dati e varianti</b>: LAION-5B (Schuhmann et al., NeurIPS 2022), ALIGN (Jia et al., ICML 2021), OpenCLIP (Cherti et al., CVPR 2023), LiT (Zhai et al., CVPR 2022).</li>
<li><b>Limiti e prompt</b>: Paiss et al. (contare fino a dieci, ICCV 2023), Yuksekgonul et al. (bag-of-words, ICLR 2023), Shtedritski et al. (red circle, ICCV 2023).</li>
<li><b>VLM generativi</b>: BLIP-2 (Li et al., ICML 2023), LLaVA (Liu et al., NeurIPS 2023), LLaVA-1.5 (CVPR 2024), Qwen-VL (Bai et al., 2023).</li>
<li><b>Compiti</b>: VQA (Antol et al., ICCV 2015), NLVR2 (Suhr et al., ACL 2019).</li>
<li><b>Panoramiche</b>: Bordes et al. 2024 (<i>An Introduction to Vision-Language Modeling</i>), le note di Varma (Stanford CS277), il visionbook cap. 51 ({C51}), Marr 1982.</li>
</ul>
<p>Gli identificativi arXiv verificati sono nella sezione «Studia dal libro» in fondo alla pagina.</p>
"""), printed=P(60))

s(61, "Panoramica delle slide (miniature)", R("""
<p>Non è una slide: è la pagina di <b>panoramica</b> che Beamer aggiunge in fondo, con le <b>miniature</b> di tutte le 60 slide in una griglia 10 × 6 numerata (footer «61 / 61»). Serve per orientarsi, non ha contenuto nuovo.</p>
<p>Curiosità pratica: le miniature incorporano di nuovo tutte le immagini <b>ad alta risoluzione</b>, ed è il motivo per cui il PDF pesa circa 77 MB e OneNote non riesce a importarlo. Per OneNote c'è <b>L24_onenote.pdf</b> nella stessa cartella Lessons, la versione compressa (circa 11 MB) preparata per questo sito.</p>
"""), printed=P(61))
