
# ===================== INTRODUZIONE =====================

s(1, "Vision-Language Models (VLMs): copertina", R("""
<p>Lezione dell'11 novembre 2026, tenuta da <b>Donald Shenaj</b> (donald.shenaj@di.unipi.it), non dal prof. Carta. Tema: i modelli che mettono insieme <b>immagini e linguaggio</b>, dall'allineamento contrastivo di CLIP fino agli assistenti multimodali che rispondono a istruzioni (LLaVA, Qwen-VL).</p>
<p>È il seguito naturale del self-supervised learning: in <a href="#L21">L21</a> la «seconda vista» di un'immagine era un'altra augmentation della stessa immagine; qui la seconda vista è la sua <b>didascalia</b>. La loss resta una InfoNCE.</p>
<p>Il PDF ha 61 pagine e il footer stampa «n / 61» con n = pagina del PDF, copertina compresa. Le divisorie di sezione (pag. 7, 35, 41, 48, 54) non hanno footer. La pag. 61 non è una slide ma la panoramica con le miniature generata da Beamer.</p>
<div class="box k"><b>Il filo della lezione in una frase</b><p>Si costruisce uno <b>spazio comune</b> in cui un'immagine e la frase che la descrive finiscono vicine (CLIP); poi si impara a <b>tradurre</b> da immagine a testo (captioning, BLIP-2); infine si collega un encoder visivo a un <b>modello di linguaggio</b> grande, che così può rispondere a domande e seguire istruzioni sulle immagini (VQA, LLaVA, Qwen-VL). Riferimento principale: il {C51} del libro, «Vision and Language».</p></div>
"""), sec=("l24-intro", "Introduzione", "slide 1–6"), printed=P(1))

s(2, "Lecture Outline", R("""
<p>Indice delle cinque parti della lezione:</p>
<ol>
<li><b>Aligning Vision and Language</b>: CLIP, cioè allineamento, dati, valutazione e limiti (slide 7–34).</li>
<li><b>Translating Images into Text</b>: captioning con decoder autoregressivo e cross-attention, BLIP-2 (slide 35–40).</li>
<li><b>Text as a Visual Representation and VQA</b>: il testo come rappresentazione di un'immagine e il visual question answering (slide 41–47).</li>
<li><b>Instruction-Tuned VLMs</b>: LLaVA e Qwen-VL (slide 48–53).</li>
<li><b>Other VLM Tasks: Reasoning and Grounding</b>: NLVR2, RefCOCO (slide 54–56).</li>
</ol>
<p>Le slide 57–60 chiudono con sintesi, prossime lezioni (PEFT e un laboratorio su VLM e PEFT) e riferimenti.</p>
"""), printed=P(2))

s(3, "Recap", R("""
<p>Ripasso di cosa serve da prima:</p>
<ul>
<li>Le lezioni precedenti: <b>classificazione</b>, <b>detection</b> e predizione densa con CNN, ViT e attention (<a href="#L16">L16</a>, <a href="#L17">L17</a>, <a href="#L18">L18</a>, <a href="#L19">L19</a>).</li>
<li><b>Self-supervised learning</b>: SimCLR impara rappresentazioni con una loss contrastiva (<b>InfoNCE / NT-Xent</b>), usando come negativi le altre immagini del batch (<i>in-batch negatives</i>) e una <b>temperatura</b> τ che regola quanto la softmax è «appuntita» (<a href="#L21">L21</a>).</li>
<li>In SimCLR le <b>coppie positive</b> sono due viste aumentate della stessa immagine.</li>
</ul>
<p>Il punto di aggancio: CLIP userà la stessa macchina (similarità coseno, temperatura, negativi nel batch, cross-entropy), ma la coppia positiva sarà <b>immagine + didascalia</b>.</p>
"""), printed=P(3))

s(4, "From Patch Tokens to Vision-Language Representations", R("""
<p>Un encoder visivo (per esempio un ViT, <a href="#L17">L17</a>–<a href="#L18">L18</a>) produce una <b>sequenza di feature</b>, una per patch:</p>
<span class="f">Z<sub>v</sub> = f<sub>v</sub>(x) ∈ ℝ<sup>N×D<sub>v</sub></sup></span>
<p>Qui N è il numero di token visivi (patch, più eventualmente il [CLS]) e D<sub>v</sub> la loro dimensione. Più avanti, nelle slide su CLIP, N indicherà invece il numero di coppie nel batch: sono due N diversi.</p>
<p>Le architetture vision-language usano questa sequenza in due modi:</p>
<ul>
<li><b>Embedding globale</b>: un solo vettore per immagine, ottenuto con un pooling o prendendo un token globale (come il [CLS]) e proiettandolo in uno spazio condiviso con il testo. È la scelta di <b>CLIP</b>: comoda per confrontare immagini e frasi con un prodotto scalare.</li>
<li><b>Sequenza di token visivi</b>: si tengono le feature delle singole patch, perché un modello di linguaggio possa «guardare» i dettagli. BLIP-2 le interroga con query apprese via cross-attention; LLaVA le proietta e le inserisce direttamente nella sequenza d'ingresso del LLM.</li>
</ul>
<p>La differenza conta: un vettore unico basta per dire «è un cane», ma perde dove sono le cose e quante sono (i limiti delle slide 33–34 nascono anche da qui).</p>
"""), printed=P(4))

s(5, "Vision-Language Supervision", R("""
<ul>
<li>Il self-supervised solo visivo definisce le coppie positive con <b>augmentation</b>: la rete impara ciò che resta invariante a ritagli e colori, ma nessuno le dice <b>cosa</b> c'è nell'immagine.</li>
<li>Le coppie immagine-testo raccolte dal web (didascalie, <b>alt-text</b> delle pagine HTML) danno una <b>supervisione semantica</b>: il testo nomina oggetti, attributi, azioni, stili. È supervisione «gratuita» e rumorosa, ma enorme.</li>
<li>Allineare visione e linguaggio permette di trasferire il modello a <b>categorie nuove definite a parole</b>, senza addestrare un classificatore per ogni insieme di etichette (zero-shot, slide 27).</li>
</ul>
<div class="box b"><b>Dal libro · {C51}, § 51.3 Learning Visual Representations from Language Supervision</b>
<p>Il libro parte da un'osservazione: la classificazione con K classi è già una <b>forma povera di supervisione linguistica</b>, perché ogni etichetta è un sostantivo scelto fra K. Prima di CLIP si era provato ad arricchirla con aggettivi e verbi, con relazioni fra oggetti, con coppie domanda-risposta. La conclusione del libro è che, con abbastanza dati e calcolo, conviene usare <b>tutto il linguaggio libero</b> come pretext task (nel senso del {C30}): una frase intera contiene molte più informazioni di un'etichetta.</p></div>
"""), printed=P(5))

s(6, "Vision-Language Tasks", R("""
<p>Quattro compiti, uno per quadrante, che la lezione affronterà in ordine:</p>
<ul>
<li><b>Zero-shot classification</b> (in alto a sinistra): l'immagine di un cane passa nell'image encoder, il vettore I<sub>1</sub> si confronta con i vettori dei testi T<sub>1</sub>…T<sub>N</sub> e vince «A photo of a dog». Didascalia: «no classifier head ever trained for “dog”», nessuna testa di classificazione è mai stata addestrata per la classe cane.</li>
<li><b>Captioning</b> (in alto a destra): un tramonto sul mare, l'utente chiede un messaggio romantico che accompagni la foto e il modello risponde con una frase («Love is like a sunset…»). Descrivere un'immagine con <b>testo libero</b>.</li>
<li><b>Visual question answering</b> (in basso a sinistra): una pizza con le domande «How many slices of pizza are there? Is this a vegetarian pizza?». Risposte <b>aperte</b>, che richiedono di contare e di riconoscere ingredienti.</li>
<li><b>Instruction-following chat</b> (in basso a destra): un uomo che stira i vestiti sul retro di un taxi giallo in movimento, con la domanda «What's unusual about this image?». Serve capire la scena e ragionare su cosa è strano: è l'esempio classico di LLaVA.</li>
</ul>
<p>Andando dal primo all'ultimo cresce quanto il modello deve <b>generare</b> e <b>ragionare</b>: si passa dallo scegliere fra frasi date (CLIP) allo scrivere risposte libere (VLM con LLM).</p>
"""), printed=P(6))

# ===================== CLIP =====================

s(7, "Aligning Vision and Language", R("""
<p>Divisoria della prima parte: <b>CLIP</b>, cioè allineamento di immagini e testo, dati di addestramento, valutazione (zero-shot, retrieval, prompt) e limiti.</p>
"""), kind='div', sec=("l24-clip", "Allineare visione e linguaggio: CLIP", "slide 7–34"), printed='')

s(8, "Representing Text for a Neural Network", R("""
<p>Prima di confrontare testo e immagini bisogna trasformare il testo in vettori.</p>
<ul>
<li><b>Tokenizzazione</b>: il testo si spezza in unità discrete, i <b>token</b>, e ciascuno riceve un indice intero.</li>
<li><b>Byte-Pair Encoding (BPE)</b>: si parte dai singoli caratteri (o byte) e si <b>fondono ripetutamente le coppie adiacenti più frequenti</b> in un simbolo nuovo, finché il vocabolario raggiunge la dimensione voluta. Bilancia dimensione del vocabolario e lunghezza delle sequenze. È il tokenizzatore del text encoder di CLIP.</li>
<li><b>Token embedding</b>: ogni indice si mappa in un vettore appreso a d dimensioni tramite una matrice <span class="f">E ∈ ℝ<sup>V×d</sup></span> con V = dimensione del vocabolario: il token i è la riga i di E.</li>
</ul>
<p><b>Figura (visionbook, fig. 51.1):</b> le parole «A», «yellow», «bird» diventano vettori one-hot (K-dimensionali), che la matrice W<sub>tokenize</sub> trasforma in token d-dimensionali.</p>
<div class="box b"><b>Dal libro · {C51}, § 51.2 Background: Representing Text as Tokens</b>
<p>Il libro usa la stessa ricetta della visione moderna: <b>tokenizzare</b> e poi passare i token a un transformer ({C26}), che funziona per qualunque modalità purché sia ridotta a una sequenza di vettori. Confronta tre scelte:</p>
<ul>
<li><b>una parola = un codice one-hot</b>: il vocabolario K esplode (oltre 100.000 parole in inglese) e non copre parole nuove, come i nomi di variabile inventati dai programmatori;</li>
<li><b>un carattere = un codice</b>: bastano poche decine di codici, ma ogni parola diventa una sequenza lunga da modellare;</li>
<li><b>BPE</b>: la via di mezzo, con codici per sottostringhe frequenti come «th» o «ing»; la usano GPT e CLIP.</li>
</ul>
<p>Il token è il prodotto <span class="f">W<sub>tokenize</sub> x</span> con x one-hot in ℝ<sup>K</sup> e W<sub>tokenize</sub> di dimensione d × K: moltiplicare per un one-hot vuol dire <b>prendere una colonna</b>, quindi in pratica è una tabella di lookup. La E della slide è la stessa matrice trasposta (V = K). In uscita, per generare testo, si fa il percorso inverso: una softmax sui K elementi del vocabolario predice il token successivo (slide 37).</p></div>
<div class="box k"><b>Da saper fare: BPE a mano</b>
<p>Corpus giocattolo: «low» ×5, «lower» ×2, «newest» ×6, «widest» ×3. Si parte dai caratteri.</p>
<ol>
<li>Coppia adiacente più frequente: «e s» (6 in newest + 3 in widest = 9) → nuovo simbolo «es».</li>
<li>Ora «es t» compare 9 volte → «est».</li>
<li>Poi «l o» (5 + 2 = 7) → «lo», poi «lo w» (7) → «low».</li>
</ol>
<p>Dopo poche fusioni «newest» = n e w est, «lower» = low e r. Le parole frequenti finiscono in pochi token, quelle rare si spezzano in pezzi ma restano rappresentabili: nessuna parola è «fuori vocabolario». Nel tokenizzatore di CLIP (testo in minuscolo) il vocabolario ha 49.152 simboli e la sequenza è tagliata a 76 token.</p></div>
"""), printed=P(8))

s(9, "Precursors to CLIP", R("""
<ul>
<li>L'idea di imparare la visione dal testo associato alle immagini è vecchia: Mori et al. 1999, Ordonez et al. 2011 (Im2Text), Joulin et al. 2016, Li et al. 2017. Quest'ultimo (<b>visual n-grams</b>) arrivava all'<b>11,5%</b> di accuratezza zero-shot su ImageNet: l'idea c'era, i numeri no.</li>
<li>Approcci più recenti con obiettivi diversi: <b>VirTex</b> (captioning autoregressivo: predire la didascalia parola per parola), <b>ICMLM</b> (masked language modeling: indovinare parole mascherate della didascalia guardando l'immagine), <b>ConVIRT</b> (apprendimento contrastivo).</li>
<li><b>ConVIRT</b> (Zhang et al. 2020): contrastivo <b>bidirezionale</b> immagine-testo su radiografie del torace e referti medici.</li>
</ul>
<p><b>Figura (ConVIRT):</b> in alto il ramo immagine (radiografie x<sub>v</sub> → augmentation t<sub>v</sub> → image encoder f<sub>v</sub> → h<sub>v</sub> → proiezione g<sub>v</sub> → v), in basso il ramo testo (frasi del referto come «Heart size is enlarged…», «No abnormality seen…» → t<sub>u</sub> → text encoder f<sub>u</sub> → h<sub>u</sub> → g<sub>u</sub> → u). A destra le due loss incrociate ℓ<sup>(v→u)</sup> e ℓ<sup>(u→v)</sup>.</p>
<span class="f">L<sub>ConVIRT</sub> = λ L<sub>v→u</sub> + (1 − λ) L<sub>u→v</sub>,   L<sub>v→u</sub> = −log [ exp(sim(v, u)/τ) / ∑<sub>u′</sub> exp(sim(v, u′)/τ) ]</span>
<ul>
<li>sim è la similarità coseno, u′ scorre sui testi del batch: per ogni immagine si classifica quale referto è il suo. L<sub>u→v</sub> è lo specchio (per ogni referto, quale immagine). λ pesa le due direzioni; nell'articolo λ = 0,75 e τ = 0,1, e le loss si mediano sulle coppie del minibatch.</li>
<li>CLIP adotta un obiettivo simmetrico simile (λ = ½ implicito), ma addestrato <b>da zero</b> su <b>400 milioni</b> di coppie invece di circa 200 mila (ConVIRT: circa 217 mila coppie radiografia-referto più 48 mila per le ossa).</li>
</ul>
<p>Due differenze di progetto che torneranno: ConVIRT inizializzava gli encoder da modelli preaddestrati e usava proiezioni non lineari (MLP a uno strato nascosto, come SimCLR); CLIP addestra da zero e usa proiezioni <b>lineari</b> (slide 12).</p>
"""), printed=P(9))

s(10, "CLIP: Contrastive Language-Image Pre-training", R("""
<p><b>CLIP</b> (Radford et al., OpenAI 2021) addestra <b>insieme</b> un encoder di immagini e uno di testo con un obiettivo contrastivo: le coppie immagine-testo corrette si avvicinano, quelle sbagliate si allontanano.</p>
<p><b>Figura (dall'articolo), in tre pannelli:</b></p>
<ol>
<li><b>Contrastive pre-training</b>: un batch di didascalie («Pepper the aussie pup», …) passa nel text encoder e dà T<sub>1</sub>…T<sub>N</sub>; le immagini passano nell'image encoder e danno I<sub>1</sub>…I<sub>N</sub>. Si forma la matrice N × N dei prodotti I<sub>i</sub>·T<sub>j</sub>; la <b>diagonale</b> (evidenziata in blu) sono le coppie vere.</li>
<li><b>Create dataset classifier from label text</b>: i nomi delle classi (plane, car, dog, …, bird) si inseriscono nel template «A photo of a {object}.» e si codificano con il text encoder: i vettori risultanti sono i <b>pesi</b> del classificatore.</li>
<li><b>Use for zero-shot prediction</b>: l'immagine di un cane dà I<sub>1</sub>, si calcolano I<sub>1</sub>·T<sub>1</sub>…I<sub>1</sub>·T<sub>N</sub> e vince «A photo of a dog.».</li>
</ol>
<ul>
<li><b>Zero-shot</b>: nessun esempio etichettato del dataset di arrivo, nessun classificatore addestrato; basta scrivere i nomi delle classi.</li>
<li>Dati: <b>400 milioni</b> di coppie raccolte dal web (il dataset WIT, non pubblico), batch enorme di <b>32.768</b> coppie, 32 epoche.</li>
</ul>
<div class="box k"><b>Da saper dire: perché contrastivo e non captioning</b><p>Gli autori di CLIP provarono prima a predire la didascalia esatta parola per parola (come VirTex): è un compito molto più difficile del necessario, perché la stessa immagine ammette infinite descrizioni. Riformulato come «quale di queste N didascalie va con questa immagine?», il problema diventa una classificazione N-aria; nell'articolo l'obiettivo contrastivo raggiunge la stessa accuratezza zero-shot su ImageNet con circa <b>4 volte meno calcolo</b> di una predizione bag-of-words, e molto meno di un modello di linguaggio trasformer.</p></div>
"""), printed=P(10))

s(11, "CLIP: A Single Image-Text Pair", R("""
<p><b>Idea chiave</b>: massimizzare la similarità fra gli embedding delle coppie immagine-testo vere, minimizzarla per le coppie sbagliate.</p>
<p><b>Figura (Varma, Stanford CS277/BIODS271):</b> una sola coppia. La foto di un cucciolo seduto nell'erba entra nell'<b>image encoder</b> e diventa un <i>image embedding</i>; la frase «A dog sitting in a field» entra nel <b>text encoder</b> e diventa un <i>text embedding</i>. Una freccia a due punte fra i due embedding indica che devono essere vicini.</p>
<ul>
<li>Le due reti sono <b>diverse</b> (a differenza di SimCLR, dove una sola rete codifica entrambe le viste), ma scrivono nello <b>stesso spazio</b>.</li>
<li>Una coppia da sola non basta: con il solo termine «avvicina» entrambi gli encoder potrebbero restituire un vettore costante (il <b>collasso</b> di <a href="#L22">L22</a>). Servono i negativi, cioè le altre coppie del batch: le slide 14–17 costruiscono la matrice passo per passo.</li>
</ul>
"""), printed=P(11))

s(12, "CLIP: Choosing an Encoder Architecture", R("""
<ul>
<li><b>Image encoder f<sub>v</sub></b>: due famiglie. Una <b>ResNet modificata</b> (<a href="#L16">L16</a>) in cui il global average pooling finale è sostituito da un <b>attention pooling</b> (un singolo strato di attention con la media delle feature come query); oppure un <b>Vision Transformer</b> (<a href="#L17">L17</a>), di cui si usa il token [CLS].</li>
<li><b>Text encoder f<sub>t</sub></b>: un transformer «stile decoder», cioè con <b>self-attention causale</b> (ogni token vede solo i precedenti, {C26}, § 26.10) sui token BPE. Il modello base ha <b>12 strati, larghezza 512, 8 teste, 63M parametri</b>. Come feature del testo si prende la rappresentazione del token finale <b>[EOS]</b>: per via della maschera causale è l'unico che ha visto tutta la frase.</li>
<li><b>Proiezione</b>: entrambe le uscite si mappano con una matrice <b>lineare</b> in uno spazio comune a d<sub>z</sub> dimensioni, <b>senza</b> la projection head non lineare (MLP) di SimCLR (<a href="#L21">L21</a>). Gli autori non hanno visto differenze e hanno scelto la soluzione più semplice.</li>
</ul>
<p>Nota di notazione: la slide chiama d<sub>z</sub> la dimensione dello spazio comune (come il libro), il pseudocodice di slide 20 la chiama d<sub>e</sub>. È la stessa grandezza: 512 per il modello base, 768 per ViT-L/14.</p>
"""), printed=P(12))

s(13, "CLIP: Normalizing Into a Shared Space", R("""
<p>Le uscite degli encoder si proiettano linearmente e si <b>normalizzano in norma L2</b>:</p>
<span class="f">v<sub>i</sub> = W<sub>v</sub>h<sub>i</sub><sup>v</sup> / ‖W<sub>v</sub>h<sub>i</sub><sup>v</sup>‖<sub>2</sub>,    t<sub>i</sub> = W<sub>t</sub>h<sub>i</sub><sup>t</sup> / ‖W<sub>t</sub>h<sub>i</sub><sup>t</sup>‖<sub>2</sub></span>
<ul>
<li>h<sub>i</sub><sup>v</sup> ∈ ℝ<sup>D<sub>v</sub></sup> e h<sub>i</sub><sup>t</sup> ∈ ℝ<sup>D<sub>t</sub></sup> sono le feature degli encoder (dimensioni diverse); W<sub>v</sub> (d<sub>z</sub> × D<sub>v</sub>) e W<sub>t</sub> (d<sub>z</sub> × D<sub>t</sub>) le portano nello spazio comune a d<sub>z</sub> dimensioni.</li>
<li>Dopo la normalizzazione ‖v<sub>i</sub>‖ = ‖t<sub>i</sub>‖ = 1, quindi il prodotto scalare <b>è</b> la similarità coseno: <span class="f">v<sub>i</sub><sup>⊤</sup>t<sub>j</sub> = cos θ<sub>ij</sub> ∈ [−1, 1]</span></li>
<li>Tutti gli embedding vivono sulla <b>sfera unitaria</b> di ℝ<sup>d<sub>z</sub></sup> (che i matematici scrivono S<sup>d<sub>z</sub>−1</sup>, perché è una superficie a d<sub>z</sub> − 1 dimensioni).</li>
</ul>
<div class="box b"><b>Dal libro · {C51}, § 51.3, e {C30}, § 30.10.1</b>
<p>Perché normalizzare? Il libro dà la ragione in una riga: senza normalizzazione la loss si potrebbe abbassare <b>spingendo i negativi infinitamente lontano</b>, cioè facendo crescere le norme invece di imparare direzioni utili. Con vettori unitari il punteggio è limitato fra −1 e 1 e conta solo l'<b>angolo</b>. Nel § 30.10.1 (Wang e Isola) la stessa idea in positivo: la InfoNCE ha un termine di <b>allineamento</b> (positivi vicini) e uno di <b>uniformità</b> (i negativi distribuiscono i punti su tutta l'ipersfera), e l'uniformità ha senso solo se i punti sono vincolati alla sfera. Il libro scrive che per vettori unitari il prodotto scalare è «proporzionale all'angolo»: più precisamente è il <b>coseno</b> dell'angolo, una funzione decrescente dell'angolo, non proporzionale.</p></div>
"""), printed=P(13))

s(14, "CLIP: A Batch of N Pairs", R("""
<p>CLIP si addestra su batch di <b>N coppie</b> immagine-didascalia. Ogni immagine si confronta con <b>tutte le N didascalie</b>, ogni didascalia con <b>tutte le N immagini</b>.</p>
<p><b>Figura (primo passo di un'animazione che continua fino a slide 19):</b> per ora c'è solo il batch, una pila di didascalie («A dog sitting in a field» in cima) e la pila corrispondente di immagini (il cucciolo in cima). Ancora nessun encoder.</p>
<ul>
<li>In ogni batch c'è <b>un</b> positivo per immagine (la sua didascalia) e <b>N − 1 negativi</b> (le didascalie delle altre immagini), senza costo aggiuntivo: i negativi sono «gratis».</li>
<li>Per questo CLIP usa batch enormi (32.768): più negativi rendono il compito più difficile e la rappresentazione più fine, come in SimCLR.</li>
</ul>
"""), printed=P(14))

s(15, "CLIP: Image Embeddings for the Batch", R("""
<p>Ogni immagine del batch passa <b>indipendentemente</b> nello <b>stesso</b> image encoder e produce I<sub>1</sub>, …, I<sub>N</sub>. Il batch cambia solo quanti vettori escono, non come si calcola ciascuno.</p>
<p><b>Cosa aggiunge la figura rispetto a slide 14:</b> compare l'image encoder (trapezio verde) e, alla sua uscita, la colonna verde dei vettori I<sub>1</sub>, I<sub>2</sub>, I<sub>3</sub>, …, I<sub>N</sub> con l'etichetta «Image Embedding».</p>
<ul>
<li>L'indipendenza è importante: a inferenza l'embedding di un'immagine non dipende dalle altre del batch, quindi a inferenza si può calcolare una volta per tutte e salvare (retrieval, slide 30).</li>
<li>Notazione: qui l'encoder si chiama f<sub>ℓ</sub> (con ℓ = immagine, la notazione del libro), mentre altrove nelle slide è f<sub>v</sub>. È la stessa rete.</li>
</ul>
"""), printed=P(15))

s(16, "CLIP: Text Embeddings for the Batch", R("""
<p>Le N didascalie passano nel text encoder f<sub>t</sub> e vengono proiettate nello spazio comune: T<sub>1</sub>, …, T<sub>N</sub>.</p>
<p><b>Cosa aggiunge la figura:</b> sopra compare il text encoder (trapezio viola) e la riga viola orizzontale T<sub>1</sub>, T<sub>2</sub>, T<sub>3</sub>, …, T<sub>N</sub> con l'etichetta «Text Embedding». Le immagini formano una <b>colonna</b>, i testi una <b>riga</b>: è già la cornice della matrice di slide 17.</p>
<ul>
<li>Anche i testi si codificano indipendentemente l'uno dall'altro.</li>
<li>Dopo questo passo si hanno due matrici N × d<sub>z</sub> di vettori unitari: I (immagini) e T (testi).</li>
</ul>
"""), printed=P(16))

s(17, "CLIP: All Pairwise Similarities", R("""
<p>Si calcolano tutte le similarità a coppie</p>
<span class="f">S<sub>ij</sub> = I<sub>i</sub><sup>⊤</sup>T<sub>j</sub>,   S = I T<sup>⊤</sup> ∈ ℝ<sup>N×N</sup></span>
<p>Le coppie vere stanno sulla <b>diagonale</b>.</p>
<p><b>Cosa aggiunge la figura:</b> fra la colonna delle immagini e la riga dei testi compare la griglia N × N con le celle I<sub>i</sub>·T<sub>j</sub>; le celle della diagonale (I<sub>1</sub>·T<sub>1</sub>, I<sub>2</sub>·T<sub>2</sub>, …, I<sub>N</sub>·T<sub>N</sub>) sono colorate in azzurro: sono i <b>positivi</b>. Tutte le altre, N² − N, sono i negativi.</p>
<ul>
<li>Basta <b>un prodotto di matrici</b> per tutto il batch: è il motivo per cui l'obiettivo contrastivo è così efficiente.</li>
<li>Obiettivo dell'addestramento: valori alti sulla diagonale, bassi fuori. Il libro (fig. 51.2) disegna la stessa matrice con N = 6: 6 caselle verdi da aumentare, 30 rosse da diminuire.</li>
<li>S non è simmetrica: S<sub>ij</sub> confronta l'immagine i con il testo j, S<sub>ji</sub> l'immagine j con il testo i. Per questo righe e colonne danno due loss diverse (slide 18–19).</li>
</ul>
"""), printed=P(17))

s(18, "CLIP: Image-to-Text Objective", R("""
<p>Si applica una <b>softmax lungo la riga k</b>: l'immagine I<sub>k</sub> si confronta con tutte le N didascalie.</p>
<span class="f">L<sub>I→T</sub> = ∑<sub>k=1</sub><sup>N</sup> −log [ exp(I<sub>k</sub>·T<sub>k</sub>/τ) / ∑<sub>j=1</sub><sup>N</sup> exp(I<sub>k</sub>·T<sub>j</sub>/τ) ]</span>
<ul>
<li>(I<sub>k</sub>, T<sub>k</sub>) è la coppia positiva (numeratore, in verde nella slide); le altre N − 1 didascalie sono i <b>negativi del batch</b> (nel denominatore, in rosso). È una <b>InfoNCE con temperatura τ</b>.</li>
<li><b>Figura:</b> nella matrice è riquadrata la prima riga (I<sub>1</sub>·T<sub>1</sub> … I<sub>1</sub>·T<sub>N</sub>): l'immagine 1 deve «scegliere» la propria didascalia fra tutte.</li>
<li>Letta come classificazione: per l'immagine k i logit sono la riga k di S/τ, la classe giusta è k, e il termine è la <b>cross-entropy</b> della softmax (<a href="#L15">L15</a>). Con etichette 0, 1, …, N−1 sulla diagonale, è esattamente <code>cross_entropy(logits, arange(N))</code>.</li>
<li><b>Temperatura</b>: dividere per τ piccolo (CLIP arriva a 0,01) allarga le differenze fra coseni che stanno tutti in [−1, 1]; senza, la softmax su valori così compressi sarebbe quasi uniforme e il gradiente debole.</li>
</ul>
<p>La slide scrive la loss come <b>somma</b> sulle k; il pseudocodice (slide 20) fa la <b>media</b>. Cambia solo un fattore N, che equivale a riscalare il learning rate.</p>
<div class="box b"><b>Dal libro · {C30}, § 30.10, eq. 30.4, e {C51}, § 51.3</b>
<p>La InfoNCE del libro è scritta per un'ancora x, un positivo x<sup>+</sup> e dei negativi x<sub>i</sub><sup>−</sup>: <span class="f">−log [ e<sup>f(x)·f(x⁺)/τ</sup> / ( e<sup>f(x)·f(x⁺)/τ</sup> + ∑<sub>i</sub> e<sup>f(x)·f(x<sub>i</sub>⁻)/τ</sup> ) ]</span> Il libro sottolinea che è un <b>log-softmax</b>, quindi un problema di classificazione in cui la classe giusta è il positivo. Nel § 51.3 CLIP è presentato come lo stesso metodo in cui le due «viste» sono <b>due modalità</b>: ancora = immagine, positivo = la sua didascalia, negativi = le altre didascalie del batch, con due encoder diversi f<sub>ℓ</sub> e f<sub>t</sub>. La formula del libro per CLIP non mette la temperatura (equivale a τ = 1); CLIP la usa e la impara (slide 20).</p></div>
"""), printed=P(18))

s(19, "CLIP: The Symmetric Objective", R("""
<p>CLIP applica la softmax anche <b>lungo ogni colonna</b>: la didascalia T<sub>k</sub> si confronta con tutte le N immagini.</p>
<span class="f">L<sub>T→I</sub> = ∑<sub>k=1</sub><sup>N</sup> −log [ exp(I<sub>k</sub>·T<sub>k</sub>/τ) / ∑<sub>j=1</sub><sup>N</sup> exp(I<sub>j</sub>·T<sub>k</sub>/τ) ]</span>
<span class="f">L = L<sub>I→T</sub> + L<sub>T→I</sub></span>
<ul>
<li><b>Figura:</b> ora è riquadrata la prima <b>colonna</b> (I<sub>1</sub>·T<sub>1</sub> … I<sub>N</sub>·T<sub>1</sub>): la didascalia 1 deve scegliere la propria immagine.</li>
<li>Il numeratore è lo stesso delle due direzioni (il positivo I<sub>k</sub>·T<sub>k</sub>); cambia il denominatore: nella riga si sommano i testi, nella colonna le immagini.</li>
<li>Perché due direzioni: con la sola L<sub>I→T</sub> un testo potrebbe essere «vicino a tutte le immagini» senza penalità (ogni immagine lo confronta con altri testi, ma nessuno lo confronta con altre immagini). La simmetria rende entrambi gli spazi discriminativi e serve per il retrieval in entrambi i sensi (slide 30).</li>
<li>La slide somma le due direzioni; l'implementazione fa la <b>media</b> sui campioni e sulle due direzioni: (L<sub>I→T</sub> + L<sub>T→I</sub>)/2. Solo un fattore di scala.</li>
</ul>
<div class="box k"><b>Da saper fare: la loss di CLIP su un batch di 3 coppie</b>
<p>Coseni (riga i = immagine i, colonna j = testo j):</p>
<table>
<tr><th></th><th>T<sub>1</sub></th><th>T<sub>2</sub></th><th>T<sub>3</sub></th></tr>
<tr><td>I<sub>1</sub></td><td><b>0,8</b></td><td>0,2</td><td>0,1</td></tr>
<tr><td>I<sub>2</sub></td><td>0,3</td><td><b>0,7</b></td><td>0,0</td></tr>
<tr><td>I<sub>3</sub></td><td>0,1</td><td>0,4</td><td><b>0,6</b></td></tr>
</table>
<p>Con τ = 0,1 i logit sono i coseni × 10.</p>
<ul>
<li><b>Riga 3</b> (immagine 3): logit 1, 4, 6. Loss = −log[e<sup>6</sup>/(e<sup>1</sup> + e<sup>4</sup> + e<sup>6</sup>)] = log(1 + e<sup>−2</sup> + e<sup>−5</sup>) = log(1 + 0,135 + 0,007) ≈ <b>0,133</b>. Il negativo «pericoloso» è T<sub>2</sub> (0,4): il termine e<sup>−2</sup> viene da lui.</li>
<li><b>Riga 1</b>: logit 8, 2, 1 → log(1 + e<sup>−6</sup> + e<sup>−7</sup>) ≈ 0,0034. Righe: 0,0034; 0,019; 0,133, media <b>0,052</b>.</li>
<li><b>Colonna 2</b> (testo 2 contro le immagini): logit 2, 7, 4 → log(1 + e<sup>−5</sup> + e<sup>−3</sup>) ≈ 0,055. Colonne: 0,0076; 0,055; 0,0092, media <b>0,024</b>.</li>
<li>Loss di CLIP = (0,052 + 0,024)/2 ≈ <b>0,038</b>.</li>
</ul>
<p><b>Effetto di τ</b>: con τ = 1 la riga 3 ha logit 0,1, 0,4, 0,6, probabilità del positivo appena 0,41 e loss 0,886; la loss totale sale a 0,79. Stessi coseni, ma con τ grande la softmax non distingue 0,6 da 0,4. Riferimento utile: se tutti i coseni fossero uguali (collasso) ogni termine varrebbe log N = log 3 ≈ 1,10.</p></div>
<div class="box k"><b>Da saper dire: CLIP contro la NT-Xent di SimCLR</b>
<p>La cross-entropy è la stessa della NT-Xent di <a href="#L21">L21</a> (similarità coseno, temperatura, positivo al numeratore, negativi del batch al denominatore). Le differenze:</p>
<ul>
<li>in SimCLR un batch di N immagini dà 2N viste e ogni ancora ha <b>2N − 2 negativi</b>, presi dalla <b>stessa modalità</b> (anche viste dell'«altro lato»); in CLIP ogni immagine ha <b>N − 1 negativi</b>, tutti <b>dell'altra modalità</b>: non c'è nessun termine immagine-immagine né testo-testo (niente negativi intra-modalità);</li>
<li>due encoder diversi invece di una rete condivisa, e proiezione lineare invece di MLP;</li>
<li>la simmetria c'è in entrambi (in SimCLR ogni vista fa da ancora a turno), ma in CLIP è fra due modalità e dà due loss distinte, righe e colonne.</li>
</ul></div>
"""), printed=P(19))

s(20, "CLIP: Training Pseudocode", R("""
<p><b>Figura:</b> il pseudocodice in stile NumPy dell'articolo di CLIP. Riga per riga:</p>
<ul>
<li><b>Ingressi</b>: I[n, h, w, c] minibatch di immagini, T[n, l] minibatch di testi (l token); image_encoder è una ResNet o un ViT, text_encoder un CBOW o un transformer; W_i[d_i, d_e] e W_t[d_t, d_e] le proiezioni apprese; t la <b>temperatura appresa</b>.</li>
<li><code>I_f = image_encoder(I)</code> → [n, d_i]; <code>T_f = text_encoder(T)</code> → [n, d_t]: feature di ciascuna modalità.</li>
<li><code>I_e = l2_normalize(np.dot(I_f, W_i), axis=1)</code> e lo stesso per T_e → [n, d_e]: proiezione lineare e normalizzazione di ogni riga (slide 13, scritta con vettori riga, quindi h·W invece di W·h).</li>
<li><code>logits = np.dot(I_e, T_e.T) * np.exp(t)</code> → [n, n]: la matrice S di slide 17 moltiplicata per e<sup>t</sup>. Confrontando con S/τ si legge <span class="f">e<sup>t</sup> = 1/τ,   t = log(1/τ)</span></li>
<li><code>labels = np.arange(n)</code>: la classe giusta della riga (o colonna) k è k, la diagonale.</li>
<li><code>loss_i = cross_entropy_loss(logits, labels, axis=0)</code> e <code>loss_t = …axis=1</code>: cross-entropy normalizzata lungo i due assi, cioè colonne e righe (slide 18–19); <code>loss = (loss_i + loss_t)/2</code>.</li>
</ul>
<div class="box k"><b>Da saper dire: perché la temperatura si impara come log(1/τ)</b>
<ul>
<li>Si ottimizza t senza vincoli e si usa e<sup>t</sup>: τ = e<sup>−t</sup> resta <b>sempre positiva</b>, qualunque valore prenda t.</li>
<li>Il parametro lavora in scala logaritmica: passare da τ = 0,1 a 0,01 è uno spostamento di t di log 10 ≈ 2,3, lo stesso che da 1 a 0,1. Un gradiente su t produce variazioni <b>relative</b> di τ, più stabili.</li>
<li>In CLIP τ parte da <b>0,07</b> (t = log(1/0,07) ≈ 2,66, lo stesso valore usato in letteratura contrastiva) e il fattore e<sup>t</sup> è <b>limitato a 100</b>, cioè τ ≥ 0,01, per evitare instabilità.</li>
<li>Perché impararla: in SimCLR τ è un iperparametro da tarare a mano (<a href="#L21">L21</a>); qui la rete sceglie da sola quanto rendere appuntita la softmax.</li>
</ul></div>
<p>Il nome delle due variabili dipende da come <code>cross_entropy_loss</code> interpreta l'asse: con axis=0 la normalizzazione corre lungo le righe di una colonna (le immagini, per un testo fisso). Non conta: la loss finale è la media delle due e non cambia scambiandole.</p>
"""), printed=P(20))

s(21, "LiT: Locked-image Text Tuning", R("""
<p>CLIP addestra entrambi gli encoder <b>da zero</b>. <b>LiT</b> (Zhai et al., CVPR 2022) <b>congela</b> un image encoder già preaddestrato e addestra solo il text encoder con la stessa loss contrastiva:</p>
<span class="f">v = f<sub>v</sub>(x),   t<sub>θ</sub> = f<sub>t,θ</sub>(c),   min<sub>θ</sub> L<sub>contrastive</sub>(v, t<sub>θ</sub>)</span>
<p>Solo θ (il testo) si ottimizza: il testo impara a «leggere» uno spazio visivo che resta fermo.</p>
<p><b>Figura:</b> tre configurazioni, ognuna con una torre immagine e una torre testo. Lettera maiuscola = preaddestrato, minuscola = da zero; L = locked (lucchetto chiuso), U/u = unlocked. <b>Lu</b>: immagine preaddestrata e bloccata, testo da zero (LiT). <b>Uu</b>: immagine preaddestrata ma aggiornata, testo da zero. <b>uu</b>: entrambe da zero (CLIP). La tabella riporta l'accuratezza zero-shot:</p>
<table>
<tr><th></th><th>ImageNet</th><th>IN-v2</th><th>CIFAR-100</th><th>Pets</th></tr>
<tr><td>Lu</td><td><b>70,1</b></td><td><b>61,7</b></td><td><b>70,9</b></td><td><b>88,1</b></td></tr>
<tr><td>Uu</td><td>57,2</td><td>50,2</td><td>62,1</td><td>74,8</td></tr>
<tr><td>uu</td><td>50,6</td><td>43,3</td><td>47,9</td><td>70,3</td></tr>
</table>
<p><b>Risultato</b>: bloccare l'image encoder (Lu) batte sia l'aggiornamento congiunto (Uu, +13 punti su ImageNet) sia l'addestramento da zero (uu, +20), negli esperimenti zero-shot riportati.</p>
<ul>
<li>Perché aiuta: l'encoder visivo preaddestrato su molti dati (etichettati o self-supervised) ha già buone feature; con dati immagine-testo rumorosi, aggiornarlo le <b>rovina</b> invece di migliorarle. È lo stesso principio del backbone congelato del linear probe (<a href="#L22">L22</a>, <a href="#L23">L23</a>).</li>
<li>Vantaggio pratico: le feature delle immagini si possono calcolare una volta sola, e l'addestramento costa molto meno.</li>
</ul>
<div class="box b"><b>Dal libro · {C37}, § 37.3.1</b>
<p>Il libro descrive il transfer learning modulare: alcuni moduli preaddestrati si tengono <b>congelati</b> per non far loro dimenticare ciò che sanno, altri si addestrano o riaddestrano. LiT ne è un caso netto: un modulo visivo congelato e un modulo testuale addestrato da zero perché impari a parlare con lui.</p></div>
"""), printed=P(21))

s(22, "CLIP: Representations at Different Depths", R("""
<p><b>Figura (visionbook, fig. 51.3):</b> a sinistra la colonna dell'<b>image encoder</b> (blocchi «ViT block ×3»), a destra quella del <b>text encoder</b> («transformer block ×3»); fra un gruppo di blocchi e l'altro un piano (rombo) mostra una mappa <b>t-SNE</b> delle rappresentazioni a quella profondità. In cima le due colonne confluiscono nel «joint embedding space» (il cerchio arancione). Il dataset è giocattolo: icone di forme colorate (cerchi, triangoli, quadrati in vari colori) e le frasi corrispondenti («red circle», «blue triangle», …); linee sottili collegano lo stesso elemento fra un piano e il successivo.</p>
<ul>
<li>Nell'encoder di <b>immagini</b> i primi strati raggruppano per <b>colore</b>, gli ultimi per <b>forma</b>; nell'encoder di <b>testo</b> succede il <b>contrario</b>.</li>
<li>La loss contrastiva agisce solo sugli embedding finali proiettati; gli strati intermedi si addestrano per backpropagation, senza un obiettivo proprio.</li>
</ul>
<div class="box b"><b>Dal libro · {C51}, § 51.3 (fig. 51.3), e {C13} per t-SNE</b>
<p>La spiegazione del libro: per una rete che parte dai <b>pixel</b> il colore è un'informazione <b>superficiale</b>, letta quasi direttamente dai valori RGB, mentre la forma richiede diversi strati di elaborazione (bordi, contorni, configurazioni). Per una rete che parte dalle <b>parole</b>, «red» e «triangle» sono invece due token ugualmente semplici: nessuno dei due è più «profondo», e l'ordine in cui emergono può anche invertirsi. Il libro la presenta come un'osservazione <b>qualitativa</b> su un esempio, non come una legge. La stessa progressione colore → forma nelle immagini compare nel § 30.4.1 per gli autoencoder (vista in <a href="#L22">L22</a>). Il t-SNE (cap. 13, fig. 13.9) è una proiezione 2D che conserva i vicini, non le distanze globali: si leggono i raggruppamenti, non le posizioni assolute.</p></div>
"""), printed=P(22))

s(23, "CLIP: The Joint Embedding Space", R("""
<p><b>Figura (visionbook, fig. 51.4):</b> lo spazio comune proiettato in 2D. Gli embedding stanno su un arco di circonferenza; le icone (triangoli, quadrati, cerchi colorati) e le etichette di testo («teal triangle», «pink square», «red circle», «orange square», …) si dispongono in gruppi: triangoli a sinistra, quadrati in alto e in basso, cerchi a destra, e ogni frase cade vicino alle icone che descrive. A sinistra il cerchio arancione ricorda che è lo spazio congiunto della slide precedente.</p>
<ul>
<li>Gli embedding normalizzati di immagini e testi stanno su un'<b>ipersfera unitaria</b>, qui visualizzata con <b>kernel PCA</b>.</li>
<li>Le coppie immagine-testo corrispondenti hanno embedding simili.</li>
<li>L'addestramento contrastivo aumenta cos θ<sub>ii</sub> <b>rispetto</b> a cos θ<sub>ij</sub> (i ≠ j), <b>senza</b> imporre un valore assoluto di similarità: la loss dipende solo dalle differenze fra logit di una stessa riga o colonna.</li>
</ul>
<div class="box b"><b>Dal libro · {C51}, § 51.3 (fig. 51.4)</b>
<p>Il libro fa notare che le descrizioni cadono vicino alle immagini giuste ma <b>non perfettamente</b>, anche per i limiti della proiezione. Dettagli della figura: embedding di CLIP a <b>768 dimensioni</b>, proiettati in 2D con kernel PCA con <b>kernel coseno</b> (coerente con la similarità usata dalla loss), dopo aver <b>tolto la prima componente principale</b>, che codifica uno <b>scostamento globale</b> fra embedding di immagini e di testi. Questo scostamento è il cosiddetto <b>modality gap</b>: in CLIP le immagini occupano una regione della sfera e i testi un'altra, separate da una direzione costante. Senza toglierlo, il disegno mostrerebbe due nuvole separate (immagini da una parte, testi dall'altra) invece dei gruppi per contenuto.</p></div>
<div class="box k"><b>Da saper dire: perché il modality gap non disturba la loss</b><p>Se a tutti i testi si somma (prima di normalizzare) uno stesso spostamento, ogni similarità I<sub>i</sub>·T<sub>j</sub> cambia di una quantità che per un'immagine fissata è quasi la stessa per tutti i j: nella softmax di una riga uno spostamento comune dei logit si semplifica. È proprio il terzo punto della slide: la loss chiede solo che il positivo superi i negativi, non che immagine e testo coincidano. Per questo i coseni fra coppie vere in CLIP sono tipicamente bassi in assoluto (circa 0,3), eppure il ranking è corretto.</p></div>
"""), printed=P(23))

s(24, "Training Data for Vision-Language Models", R("""
<p>CLIP è stato addestrato su <b>400 milioni</b> di coppie raccolte dal web. Qualità, filtraggio e diversità dei dati sono fattori decisivi nell'addestramento vision-language su larga scala.</p>
<p><b>Figura (Bordes et al. 2024, «An Introduction to Vision-Language Modeling»):</b> una panoramica di come si migliorano i dati, in tre gruppi.</p>
<ul>
<li><b>Data</b>: <i>remove duplicate</i> (togliere i duplicati: la stessa foto di cane ripetuta), <i>balancing</i> (bilanciare i concetti: tanti gatti, pochi fenicotteri), <i>pruning</i> (scartare le coppie in cui il testo non corrisponde: «A photo of a dog» ✓, «A drawing of a bird» ✗ sotto la foto di un cane), <i>improving</i> (riscrivere le didascalie in modo più ricco: «A beagle dog is smiling and looking at the camera»).</li>
<li><b>Grounding</b>: usare i <i>bounding box</i> (ogni frase legata a una regione: «A golden retriever swimming», «Tennis balls in a swimming pool») e le <i>negative captions</i> (didascalie sbagliate apposta, per insegnare le differenze fini).</li>
<li><b>Alignment</b>: <i>instruction tuning</i> (coppie istruzione-risposta: «Provide a description of what is presented in the image» → «This is a photo of a smiling dog») e <i>RLHF</i> (feedback umano che premia la risposta corretta «This image is a photo of a smiling dog» e penalizza quella sbagliata).</li>
</ul>
<p>Gli ultimi due gruppi anticipano la seconda metà della lezione (grounding, slide 56; instruction tuning, slide 48–53).</p>
"""), printed=P(24))

s(25, "Data at Scale: LAION-5B", R("""
<p><b>LAION-5B</b> (Schuhmann et al., NeurIPS 2022): <b>5,85 miliardi</b> di coppie immagine-testo estratte da Common Crawl, di cui 2,32 miliardi in inglese, 2,26 miliardi in altre lingue e 1,27 miliardi in lingua non determinata. Pubblica metadati e URL delle immagini (non le immagini), e permette di addestrare modelli stile CLIP in modo aperto con <b>OpenCLIP</b> (slide 26).</p>
<p><b>Figura:</b> quattro esempi del sottoinsieme inglese con il loro testo: un quaderno a spirale con una spiaggia («Blue Beach Umbrellas, Point Of Rocks, Crescent Beach, Siesta Key - Spiral Notebook»), un'auto blu con un testo che è un nome di file («BMW-M2-M-Performance-Dekor-Long-Beach-Blue-05»), la copertina di un libro con il titolo intero, una smerigliatrice con un titolo di prodotto pieno di codici e misure («Dynabrade 52632 4-1/2" Dia. Right Angle…»).</p>
<ul>
<li>L'alt-text del web contiene <b>titoli di prodotti, nomi di file, descrizioni incomplete</b>: non sono didascalie scritte per descrivere l'immagine.</li>
<li>LAION filtra le coppie tenendo quelle con similarità CLIP sopra una soglia: migliora l'allineamento immagine-testo ma <b>non elimina il rumore</b>, ed eredita i bias del CLIP usato per filtrare.</li>
</ul>
<p>Il messaggio: CLIP funziona <b>nonostante</b> il rumore, perché la scala compensa. Con 400 milioni o 5 miliardi di coppie i segnali coerenti (la parola «beach» con foto di spiagge) si sommano e il rumore si media.</p>
"""), printed=P(25))

s(26, "OpenCLIP: Reproducing and Scaling CLIP", R("""
<ul>
<li><b>OpenCLIP</b>: implementazione open source di dual encoder stile CLIP e del loro addestramento contrastivo.</li>
<li>Usa dataset pubblici (<b>LAION-80M, LAION-400M, LAION-2B</b>) e rilascia modelli preaddestrati di architetture e taglie diverse (ViT-B/32 fino a ViT-g/14). Il ViT-bigG di OpenCLIP tornerà come encoder visivo di Qwen-VL (slide 51).</li>
<li>Gli esperimenti di scaling mostrano <b>andamenti diversi</b> per CLIP di OpenAI e OpenCLIP, nonostante architetture e procedure simili.</li>
</ul>
<p><b>Figura (Cherti et al., CVPR 2023, «Reproducible Scaling Laws for Contrastive Language-Image Learning»):</b> errore zero-shot su ImageNet (asse y, scala logaritmica) in funzione del calcolo totale (GMAC per campione × campioni visti, asse x logaritmico). I punti sono modelli OpenCLIP (arancioni, forma = dataset, dimensione = campioni visti 3B/13B/34B, tonalità = architettura) e CLIP di OpenAI (blu, CLIP-WIT). Le due rette sono leggi di potenza <span class="f">E = a · C<sup>b</sup></span> con esponenti circa −0,11 (OpenCLIP) e −0,16 (CLIP).</p>
<ul>
<li>Una retta in un grafico log-log è una <b>legge di potenza</b>: raddoppiare il calcolo riduce l'errore di un fattore costante.</li>
<li>Su ImageNet zero-shot la retta di OpenAI è più ripida (dati WIT); nello stesso articolo, sul retrieval, è OpenCLIP a scalare meglio. Gli autori attribuiscono la differenza alla <b>distribuzione dei dati</b> di addestramento, non al modello: è l'argomento della slide 24.</li>
</ul>
"""), printed=P(26))

s(27, "CLIP: Zero-Shot Classification", R("""
<p>I nomi delle classi candidate c<sub>1</sub>, …, c<sub>K</sub> si codificano come embedding di testo e definiscono un classificatore <b>senza addestramento specifico</b>:</p>
<span class="f">p(y = k | x, C) = exp(z<sub>v</sub><sup>x</sup>·z<sub>t</sub><sup>c<sub>k</sub></sup>/τ) / ∑<sub>j=1</sub><sup>K</sup> exp(z<sub>v</sub><sup>x</sup>·z<sub>t</sub><sup>c<sub>j</sub></sup>/τ)</span>
<span class="f">ĉ = argmax<sub>c∈C</sub> z<sub>v</sub><sup>x</sup>·z<sub>t</sub><sup>c</sup></span>
<p><b>Figura:</b> i pannelli (2) e (3) di CLIP (slide 10): il text encoder trasforma «A photo of a {object}.» per ogni classe in T<sub>1</sub>…T<sub>N</sub>, l'immagine di un cane dà I<sub>1</sub>, vince la cella I<sub>1</sub>·T<sub>3</sub>, «A photo of a dog.».</p>
<ul>
<li>È una <b>regressione logistica multinomiale</b> (<a href="#L15">L15</a>) in cui la matrice dei pesi non si impara: le sue righe sono gli embedding dei testi delle classi, e τ fa da scala dei logit.</li>
<li>L'insieme C si può <b>cambiare a inferenza</b>: aggiungere una classe vuol dire codificare una frase in più.</li>
<li>τ non cambia la classe scelta (l'argmax non dipende da una scala positiva); cambia solo quanto sono «sicure» le probabilità.</li>
<li>Le probabilità <b>dipendono da C</b> e <b>non sono calibrate</b>: se nessuna delle classi è giusta, la softmax ne sceglie comunque una con probabilità alta. «90% gatto» vuol dire «più gatto delle altre opzioni date», non «90% di probabilità che sia un gatto».</li>
</ul>
<div class="box k"><b>Da saper fare: zero-shot a mano</b>
<p>Immagine con embedding z<sub>v</sub>, coseni con i testi «a photo of a dog» 0,31, «… cat» 0,25, «… car» 0,12, τ = 0,01 (logit 31, 25, 12). p(dog) = 1/(1 + e<sup>−6</sup> + e<sup>−19</sup>) ≈ 0,998. Togliendo «dog» da C: p(cat) = 1/(1 + e<sup>−13</sup>) ≈ 1,000. Il modello è «sicurissimo» che sia un gatto: è la non-calibrazione della slide.</p></div>
"""), printed=P(27))

s(28, "Building Custom Zero-Shot Classifiers", R("""
<p><b>Figura (visionbook, fig. 51.6):</b> tre volte gli stessi embedding di immagini (le icone del dataset giocattolo, disposti su una circonferenza) con due vettori di testo disegnati dal centro: (a) «triangle» (rosso) contro «circle» (verde), classificazione per <b>forma</b>; (b) «purple» contro «teal», per <b>colore</b>; (c) «arrowhead» contro «ball», per <b>tipo di oggetto</b>. In ogni pannello i punti sono colorati in rosso o verde a seconda del vettore più vicino.</p>
<ul>
<li>Gli stessi embedding si classificano per forma, colore o oggetto <b>cambiando solo le frasi</b>.</li>
<li>Cambiare gli embedding testuali candidati sposta il <b>confine di decisione</b>, senza aggiornare alcun parametro di CLIP.</li>
<li>Con K embedding di testo si sceglie quello con il <b>coseno più alto</b>.</li>
</ul>
<div class="box b"><b>Dal libro · {C51}, § 51.3 (fig. 51.5 e 51.6)</b>
<p>Il libro costruisce il classificatore con due descrizioni libere, per esempio «striped red circles» (classe a) e «polka dotted green square» (classe b): si calcolano z<sub>t</sub><sup>a</sup> = f<sub>t</sub>(t<sup>a</sup>) e z<sub>t</sub><sup>b</sup> = f<sub>t</sub>(t<sup>b</sup>) (nel testo del libro c'è un refuso, f<sub>t</sub>(t<sup>a</sup>) anche per b), l'embedding della query z<sub>ℓ</sub><sup>q</sup> = f<sub>ℓ</sub>(ℓ<sup>q</sup>), e si sceglie <span class="f">ŷ = argmax<sub>c</sub> z<sub>ℓ</sub><sup>q</sup> · z<sub>t</sub><sup>c</sup></span> CLIP resta congelato. Geometricamente ogni vettore di testo è una direzione sulla sfera e il classificatore guarda a quale direzione l'immagine è più vicina in <b>angolo</b>: con due classi il confine è un iperpiano (il bisettore delle due direzioni), con più classi la sfera si divide in regioni, una per frase. Il libro paragona il sistema a un <b>astrolabio</b> moderno: si «girano le manopole» (le frasi) e si legge la previsione che serve.</p></div>
"""), printed=P(28))

s(29, "CLIP: Zero-Shot Results", R("""
<p><b>Figura (dall'articolo di CLIP):</b> barre orizzontali con la differenza di accuratezza fra <b>CLIP zero-shot</b> e un <b>linear probe su feature di ResNet-50</b> (un classificatore lineare <b>addestrato</b> sui dati etichettati di ogni dataset), su 27 dataset. Barre verdi a destra: vince CLIP; blu a sinistra: vince il linear probe.</p>
<ul>
<li>CLIP vince su <b>16 dataset su 27</b>, compreso ImageNet (+1,9). I guadagni maggiori: StanfordCars +28,9, Country211 +23,2, Food101 +22,5, Kinetics700 +14,5, SST2 +12,4 (classificazione del sentimento di frasi renderizzate come immagini).</li>
<li>Perde nei <b>domini specializzati o astratti</b>: EuroSAT −37,1 e RESISC45 −11,9 (immagini satellitari), PatchCamelyon −19,5 (istologia), KITTI Distance −34,0 (stimare la distanza di un'auto), CLEVRCounts −18,2 (contare oggetti, slide 33), GTSRB −18,4 (cartelli stradali), MNIST −10,0, FGVCAircraft −11,3, DTD −16,6 (texture).</li>
</ul>
<p>Lettura: CLIP è forte dove il web contiene tanto testo che <b>nomina</b> le cose (modelli di auto, piatti, luoghi); è debole dove le classi sono rare sul web o non si descrivono bene a parole (una distanza, un numero, una texture, un tipo di tessuto al microscopio). Il confronto è impressionante comunque: lo zero-shot batte su metà dei dataset un classificatore che ha visto i dati etichettati.</p>
"""), printed=P(29))

s(30, "Text-to-Image Retrieval", R("""
<p>Data una query testuale q, si ordinano le immagini candidate {x<sub>1</sub>, …, x<sub>M</sub>} per similarità coseno:</p>
<span class="f">î = argmax<sub>i∈{1,…,M}</sub> z<sub>t</sub><sup>q</sup> · z<sub>v</sub><sup>x<sub>i</sub></sup></span>
<ul>
<li>Gli embedding delle immagini si <b>precalcolano</b> una volta; a inferenza basta un <b>prodotto matrice-vettore</b> (M × d<sub>z</sub> per d<sub>z</sub>), più un ordinamento. Per collezioni enormi si usano indici di ricerca approssimata dei vicini.</li>
<li>Il retrieval immagine → testo è lo stesso con le modalità scambiate.</li>
<li><b>Recall@K</b>: frazione delle query per cui almeno un risultato rilevante è fra i primi K. Esempio: su 100 query, se in 72 casi l'immagine giusta è fra le prime 5, Recall@5 = 72%.</li>
</ul>
<p><b>Figura (ALIGN, Jia et al. 2021, l'analogo di CLIP di Google, addestrato su 1,8 miliardi di coppie immagine-alt-text quasi senza filtri):</b> (A) text → image: «Roppongi Hills Spider at night» restituisce foto della grande scultura di ragno; (B) image → text: un dipinto dei covoni di Monet recupera testi come «original picture of monet haystack», «haystack series monet art institute of chicago» (benchmark Flickr30k, MSCOCO); (C) immagine + testo → immagine: la Torre Eiffel più la parola «snow» restituisce la torre sotto la neve, sommando gli embedding delle due modalità.</p>
<p>Il pannello (C) mostra che lo spazio comune ha una certa <b>aritmetica</b>: sommare vettori di immagine e di testo combina i concetti.</p>
"""), printed=P(30))

s(31, "Prompting VLMs: Textual Prompts", R("""
<ul>
<li>Sostituire il nome della classe («dog») con un template («a photo of a dog») migliora l'accuratezza zero-shot su ImageNet di <b>1,3 punti</b>.</li>
<li><b>Prompt ensembling</b>: per ogni classe si fa la media degli embedding normalizzati di più template («a photo of a big {}», «a drawing of a {}», …; CLIP ne usa 80 per ImageNet), ottenendo altri <b>3,5 punti</b>. In tutto quasi 5 punti.</li>
<li>Gli embedding dei testi si precalcolano: l'ensemble costa solo all'inizio, non per ogni immagine.</li>
</ul>
<p><b>Figura (dall'articolo):</b> punteggio medio zero-shot su molti dataset in funzione dei GFLOP del modello (RN50, RN101, RN50x4, RN50x16, RN50x64; da 6,1 a 265,9 GFLOP). La curva verde (prompt engineering ed ensembling) sta sopra quella blu (nomi di classe nudi, come Li et al. 2017) di circa <b>5 punti</b> per il modello più grande; l'annotazione «4X efficiency gain» indica che con i prompt un modello circa 4 volte più piccolo raggiunge il punteggio del più grande senza prompt.</p>
<div class="box k"><b>Da saper dire: perché il template aiuta</b>
<ul>
<li><b>Distribuzione</b>: nei dati di addestramento una parola isolata come testo associato a un'immagine è rara; frasi intere sono la norma. Il template avvicina la query a ciò che il text encoder ha visto.</li>
<li><b>Ambiguità</b>: «crane» può essere una gru da cantiere o un uccello, «boxer» una razza di cane o un pugile. «a photo of a boxer, a type of pet» risolve il senso (CLIP usa template di questo tipo per Oxford Pets).</li>
<li><b>Ensemble</b>: ogni template introduce un piccolo errore diverso; mediare gli embedding (e rinormalizzare) li riduce, come un ensemble di classificatori, ma al costo di un solo vettore per classe.</li>
</ul></div>
"""), printed=P(31))

s(32, "Prompting VLMs: Visual Prompts", R("""
<ul>
<li>I <b>prompt visivi</b> modificano l'immagine d'ingresso per indicare una <b>regione di interesse</b>, senza aggiornare i parametri del modello.</li>
<li>Un <b>cerchio rosso</b> disegnato attorno a un oggetto dirige l'attenzione di CLIP su quell'oggetto, conservando il contesto intorno (a differenza del ritaglio, che lo butta).</li>
<li>Per il <b>visual grounding</b> si marcano le regioni candidate una alla volta e si ordinano per similarità immagine-testo con la frase.</li>
</ul>
<p><b>Figure (Shtedritski et al., ICCV 2023, «What Does CLIP Know About a Red Circle?»):</b> in alto, <i>referring expressions comprehension</i>: la foto di un gruppo di elefanti viene copiata più volte con un cerchio rosso attorno a un elefante diverso; ciascuna copia e la frase «The calf on the right» entrano nel VLM, che dà un punteggio per copia (le barre azzurre) e vince la regione giusta. In basso, due esempi con un cerchio rosso disegnato su un animale: «The cow that is the smallest» e «The white little lamb».</p>
<ul>
<li>Perché funziona: nei dati web ci sono molte immagini con cerchi rossi attorno a qualcosa di cui il testo parla, e CLIP ha imparato l'associazione. Gli autori notano che l'effetto compare solo nei modelli più grandi e addestrati su più dati.</li>
<li>Questo trasforma un modello che dà un vettore globale (slide 4) in uno che può «puntare», senza addestramento: un'anticipazione del grounding di slide 56.</li>
</ul>
"""), printed=P(32))

s(33, "Limitations: Counting", R("""
<ul>
<li>L'apprendimento contrastivo immagine-testo standard <b>non supervisiona esplicitamente il numero</b> di oggetti: nelle didascalie web i numeri sono rari, e per distinguere la coppia giusta nel batch quasi mai serve contare.</li>
<li>CLIP confonde spesso numeri diversi di oggetti nella valutazione di Paiss et al. (ICCV 2023, «Teaching CLIP to Count to Ten»).</li>
<li>Le visualizzazioni dell'attenzione suggeriscono una copertura <b>incompleta</b> delle istanze ripetute: il modello guarda alcune copie dell'oggetto, non tutte.</li>
</ul>
<p><b>Figura:</b> risultati di retrieval del CLIP originale in una griglia: righe «Three», «Five», «Six», «Nine», colonne «Animals», «Lamps», «Dogs», «Hearts». In ogni casella l'immagine recuperata per, per esempio, «six dogs», con una spunta verde se il numero è giusto e una croce rossa se no. Le croci sono la maggioranza (la riga «Nine» è tutta sbagliata, e anche le carte da gioco con i cuori, dove contare è l'unica cosa che conta, sono tutte sbagliate).</p>
<p>Coerente con slide 29: CLEVRCounts, un dataset di conteggio, è fra quelli dove CLIP zero-shot perde di più (−18,2). Il rimedio proposto da Paiss et al. è una loss aggiuntiva con <b>negativi controfattuali</b>: la stessa didascalia con il numero cambiato, che il modello deve rifiutare.</p>
"""), printed=P(33))

s(34, "Limitations: Relational Understanding", R("""
<ul>
<li>L'allineamento immagine-testo può basarsi soprattutto sull'<b>identità degli oggetti</b>, con poca sensibilità all'<b>ordine delle parole</b> e alle <b>relazioni</b>.</li>
<li>Scambiare soggetto e oggetto cambia il significato della frase ma lascia le stesse parole.</li>
<li>Nell'esempio, BLIP dà punteggi simili a «the horse is eating the grass» e «the grass is eating the horse».</li>
</ul>
<p><b>Figura (Yuksekgonul et al., ICLR 2023, «When and Why Vision-Language Models Behave like Bags-of-Words»):</b> la foto di un cavallo che bruca l'erba entra in BLIP con le due frasi. In realtà la frase assurda «the grass is eating the horse» ottiene il punteggio più alto, <b>81%</b>, contro il <b>78%</b> della frase giusta: non solo punteggi simili, ma la scelta sbagliata.</p>
<div class="box k"><b>Da saper dire: perché nasce il comportamento «bag of words»</b>
<p>Durante l'addestramento contrastivo i negativi sono le didascalie di <b>altre immagini</b> del batch: quasi sempre parlano di oggetti diversi. Per vincere basta riconoscere quali oggetti ci sono, non come sono legati: l'ordine delle parole non serve mai, e il modello non lo impara (una <b>scorciatoia</b>, come quelle viste in <a href="#L21">L21</a>). Gli autori lo misurano con il benchmark ARO (relazioni, attributi, ordine) e propongono di aggiungere <b>negativi difficili</b> costruiti scambiando le parole della didascalia vera (NegCLIP): così la scorciatoia smette di funzionare. È lo stesso rimedio del conteggio: negativi che differiscono solo nella cosa che si vuole insegnare.</p></div>
"""), printed=P(34))
