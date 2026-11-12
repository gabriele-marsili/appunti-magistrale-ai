VB = 'https://visionbook.mit.edu/'
def L(slug, txt): return f'<a href="{VB}{slug}" target="_blank">{txt}</a>'
LK = {
 '{C51}': L('VLMs.html', 'cap. 51'),
 '{C30}': L('representation_learning.html', 'cap. 30'),
 '{C26}': L('transformers.html', 'cap. 26'),
 '{C32}': L('generative_models.html', 'cap. 32'),
 '{C34}': L('conditional_generative_models.html', 'cap. 34'),
 '{C37}': L('transfer_learning.html', 'cap. 37'),
 '{C13}': L('neural_nets_as_distribution_transformers.html', 'cap. 13'),
 '{C50}': L('object_recognition_v3.html', 'cap. 50'),
}
def P(n): return f' <em>· pag. {n}/61</em>'
def R(t):
    for k, v in LK.items(): t = t.replace(k, v)
    return t

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
