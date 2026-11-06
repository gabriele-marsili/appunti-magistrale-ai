VB = 'https://visionbook.mit.edu/'
def L(slug, txt): return f'<a href="{VB}{slug}" target="_blank">{txt}</a>'
LK = {
 '{C30}': L('representation_learning.html', 'cap. 30'),
 '{C37}': L('transfer_learning.html', 'cap. 37'),
 '{C36}': L('data_augmentation.html', 'cap. 36'),
 '{C12}': L('neural_nets.html', 'cap. 12'),
 '{C24}': L('convolutional_neural_nets.html', 'cap. 24'),
}
def R(t):
    for k, v in LK.items(): t = t.replace(k, v)
    return t

# ===================== INTRODUZIONE =====================

s(1, "Self-Supervised Contrastive Learning: copertina", R("""
<p>Lezione del 4 novembre 2026, prof. <b>Antonio Carta</b>. Fin qui le reti (CNN in <a href="#L15">L15</a>, ViT in <a href="#L17">L17</a>) sono state addestrate con <b>etichette</b>. Questa lezione chiede: si può imparare una buona <b>rappresentazione</b> delle immagini <b>senza etichette</b>, e poi riusarla per i compiti veri?</p>
<p>La risposta della lezione è l'<b>apprendimento contrastivo auto-supervisionato</b>: due versioni modificate della stessa foto devono avere embedding vicini, foto diverse embedding lontani. La L22 continua con i metodi senza negativi, mascherati e per distillazione (BYOL, DINO, MAE) e i foundation model.</p>
<p>Il PDF ha 51 pagine: copertina non numerata, footer «x / 50» con x = pagina del PDF − 1; le divisorie (pag. 6, 12, 20, 27, 31, 36, 42, 45) non hanno numero ma contano nella numerazione.</p>
"""), sec=("l21-intro", "Introduzione", "slide 1–5"))

s(2, "Outline", R("""
<p>Tre blocchi:</p>
<ol>
<li><b>Self-supervised learning</b>: imparare rappresentazioni senza etichette (pretraining, finetuning, valutazione, primi pretext task).</li>
<li><b>Apprendimento contrastivo e augmentation</b>: coppie positive e negative, <i>instance discrimination</i>, InfoNCE.</li>
<li><b>SimCLR</b>: il framework contrastivo semplice e forte che riassume tutto (più SimSiam, che toglie i negativi).</li>
</ol>
"""))

s(3, "Pretrain-then-Finetune", R("""
<p>La ricetta standard del deep learning in visione, in tre passi:</p>
<ol>
<li><b>Pretraining</b> di una backbone su un grande dataset etichettato (es. classificazione su ImageNet);</li>
<li>si <b>toglie la testa</b> di classificazione e si tiene la backbone come estrattore di feature;</li>
<li><b>finetuning</b> sul compito a valle (<i>downstream</i>): classificazione, detection, segmentazione…</li>
</ol>
<p>La backbone impara una <b>rappresentazione</b> h = f<sub>θ</sub>(x) riusata fra compiti diversi. Il pretraining è solo un mezzo: conta la prestazione sui <b>compiti a valle mai visti</b>. Obiettivo della lezione: trovare una ricetta di pretraining che dia buone prestazioni sui benchmark a valle dopo il finetuning, <b>senza etichette</b>.</p>
<div class="box w"><b>Attenzione: refusi</b><p>«The <i>eng</i> goal» va letto «the <b>end</b> goal» (lo scopo finale); «Goal: <i>fing</i> a pretraining recipe» va letto «<b>find</b>».</p></div>
<div class="box b"><b>Dal libro · {C37}, § 37.2 Problem Setting</b><p>Il libro divide ogni algoritmo di transfer learning in due fasi: <b>pretraining</b> (come si acquisisce la conoscenza a priori) e <b>adaptation</b> (come la si usa per un compito nuovo). Esempio del libro: un drone che distingue grano da mais deve passare a grano contro soia; invece di ripartire da zero si riusa il classificatore dell'anno prima. Osservazione utile: il pretraining può essere un normale addestramento chiamato così «a posteriori», oppure un compito progettato apposta solo come riscaldamento: gli algoritmi di representation learning del cap. 30 (quelli di questa lezione) sono del secondo tipo.</p></div>
"""))

s(4, "Labels are Expensive", R("""
<ul>
<li>La qualità della rappresentazione cresce con il numero di esempi: servono dataset <b>grandi</b>.</li>
<li>Le annotazioni costano, e il costo cresce con il compito: <b>etichetta d'immagine &lt; scatole &lt; maschere</b> (vedi <a href="#L19">L19</a>); alcuni domini richiedono esperti (immagini mediche, telerilevamento, ispezione industriale).</li>
<li>Le etichette sono rumorose, distorte (bias) e legate a un insieme <b>fisso</b> di classi.</li>
<li>Le immagini senza etichetta sono abbondanti ed economiche (web, telecamere, robot).</li>
</ul>
<p><b>Definizioni</b> (da sapere):</p>
<ul>
<li><b>Self-supervised learning (SSL)</b>: addestrare su un grande dataset non etichettato con un compito le cui etichette sono <b>generate dai dati stessi</b>.</li>
<li><b>Pretext task</b>: il compito auto-supervisionato che definisce una loss «come se» fosse supervisionata.</li>
<li><b>Downstream task</b>: i problemi che si vogliono davvero risolvere dopo il pretraining.</li>
</ul>
<p>Il pretext task in sé non interessa: è solo un modo per addestrare la rappresentazione.</p>
<div class="box b"><b>Dal libro · {C30}, § 30.6 Self-Supervised Learning</b><p>Il libro formalizza l'idea con due funzioni dello stesso dato: si costruiscono un ingresso V<sub>1</sub>(X) e un bersaglio V<sub>2</sub>(X) a partire dall'immagine X (per esempio la metà sinistra e la metà destra) e si addestra la rete a predire V<sub>2</sub> da V<sub>1</sub>. La supervisione è «cucinata» dai dati: predire il fotogramma successivo di un video o il pixel successivo in ordine raster sono casi dello stesso schema. Il libro evita la parola «supervised» perché non esistono coppie ingresso-rappresentazione giuste da imitare: la supervisione è un pretesto che si spera induca buone rappresentazioni.</p></div>
"""))

s(5, "Transferability", R("""
<p>Cosa rende <b>utile</b> una rappresentazione:</p>
<ul>
<li><b>Trasferibile</b>: buone prestazioni su molti compiti a valle, con pochi dati etichettati e poco adattamento (anche <i>few-shot</i>).</li>
<li><b>Semantica</b>: immagini semanticamente simili vicine, diverse lontane; idealmente classi <b>linearmente separabili</b> e fattori <b>disentangled</b> (separati su dimensioni diverse).</li>
<li><b>Invariante</b> ai fattori di disturbo (<i>nuisance</i>: luce, punto di vista, piccoli ritagli, spostamenti di colore) ma conservando il contenuto semantico. Cosa sia disturbo <b>dipende dal compito</b> a valle.</li>
</ul>
<p>I metodi SSL differiscono per come progettano pretext task e architettura per indurre queste proprietà.</p>
<div class="box b"><b>Dal libro · {C30}, § 30.2–30.3</b><p>Il libro riduce le proprietà desiderate a due principi:</p>
<ul>
<li><b>Compressione</b>: una rappresentazione buona tiene solo l'essenziale. Serve a risparmiare memoria, ma soprattutto a ottenere <b>invarianza</b>: se rumore della camera, luce e punto di vista vengono «buttati via», la rappresentazione è più utile per riconoscere oggetti. È anche il rasoio di Occam (minima lunghezza di descrizione). Attenzione: comprimere da solo porta alla soluzione degenere «non rappresentare niente», quindi va sempre accoppiato a un altro obiettivo.</li>
<li><b>Predizione</b>: una buona rappresentazione è un buon substrato per predire il futuro, il passato, le parti mancanti (<i>imputation</i>) o proprietà astratte.</li>
</ul>
<p>La Tab. 30.1 classifica i metodi: autoencoder, <b>contrastivo</b> e clustering sono di tipo compressione (il contrastivo: «ottenere invarianza alle trasformazioni di vista»); predizione del futuro, imputation e pretext task sono di tipo predizione. Il libro chiude il capitolo ricordando che <b>nessuna rappresentazione è buona per tutto</b>: «general-purpose» significa buona per i compiti che interessano agli umani.</p></div>
"""))

# ===================== FINETUNING =====================

s(6, "Finetuning", "<p>Come si usa e come si valuta una rappresentazione preaddestrata: finetuning completo, linear probe, k-NN, prototipi.</p>",
  kind='div', sec=("l21-finetuning", "Finetuning e valutazione", "slide 6–11"))

s(7, "Finetuning", R("""
<p><b>Full finetuning</b>:</p>
<ul>
<li>si sostituisce la testa del pretext task con una <b>testa per il compito</b>;</li>
<li>si addestra tutta la rete sui dati etichettati a valle, di solito con un <b>learning rate più piccolo per la backbone</b>; si possono <b>congelare</b> alcuni strati;</li>
<li>regola pratica: gli strati bassi sono generici, quelli alti specifici del compito; si rifiniscono gli alti, i bassi si possono lasciare congelati.</li>
</ul>
<p><b>Pro e contro</b>: dà la migliore accuratezza a valle (se ci sono abbastanza dati per non andare in overfitting), ma è costoso (un addestramento completo per ogni compito) e ha molti iperparametri (learning rate, schedule, augmentation, epoche).</p>
<div class="box b"><b>Dal libro · {C37}, § 37.3 Finetuning e 37.3.1</b>
<ul>
<li>Finetuning = inizializzare il nuovo modello con i parametri preaddestrati e continuare l'addestramento come al solito (Algorithm 37.1): «piccoli aggiustamenti» dei parametri.</li>
<li>Se cambia la dimensione dell'uscita (da 2 a 3 classi) si <b>taglia l'ultimo strato</b> e se ne mette uno nuovo inizializzato a caso; lo stesso con il primo strato se cambia l'ingresso (fig. 37.2).</li>
<li>§ 37.3.1: si può rifinire solo una parte del grafo e congelare il resto, per esempio per non <b>dimenticare</b> la conoscenza a priori. Esempio del libro: un detector di auto con un featurizer <b>DINO congelato</b> (il metodo SSL della L22), due moduli (profondità e classi per pixel) rifiniti e un detector addestrato da zero. Si può anche aggiornare solo un sottospazio a basso rango dei pesi (LoRA).</li>
</ul></div>
"""))

s(8, "Linear probing", R("""
<ul>
<li>Si <b>congela</b> l'encoder preaddestrato f<sub>θ</sub>.</li>
<li>Si addestra solo un <b>classificatore lineare</b> sopra: <span class="f">ŷ = softmax(W f<sub>θ</sub>(x) + b)</span></li>
<li>Benchmark standard: accuratezza top-1 su ImageNet di un linear probe sulla backbone congelata.</li>
</ul>
<p>Intuizione: la rappresentazione è buona se le classi di ImageNet sono <b>linearmente separabili</b> nello spazio delle feature. È economico (le feature si calcolano una volta sola) e ha pochi iperparametri. È il metodo di valutazione standard dell'SSL per la classificazione.</p>
<div class="box b"><b>Dal libro · {C37}, § 37.3.2 Heads and Probes</b><p>Un modulo di lettura (<i>read-out</i>) che prende feature da un punto della rete e produce una nuova predizione; se è lineare si chiama <b>linear probe</b>. Due usi: riadattare la rete a un compito nuovo con pochi parametri (spesso con soluzioni in forma chiusa), e <b>sondare</b> cosa «sa» uno strato: se le feature di uno strato classificano linearmente un attributo, quello strato codifica l'attributo. È lo strumento con cui si dice che l'accuratezza «ha il picco negli strati intermedi» (slide 18).</p></div>
<div class="box x"><b>Approfondimento</b><p>Il linear probe premia le feature <b>linearmente</b> separabili: un metodo può avere probe basso e finetuning alto (succede ai metodi mascherati come MAE, L22). Per questo la slide 48 consiglia di guardare più metriche.</p></div>
"""))

s(9, "k-NN evaluation", R("""
<ul>
<li>Si calcolano gli embedding di tutte le immagini di training con l'encoder congelato (di solito normalizzati ℓ<sub>2</sub>).</li>
<li>Per un'immagine di test si cercano i <b>k vicini</b> (similarità coseno).</li>
<li>Si predice la classe con un <b>voto pesato</b>:</li>
</ul>
<span class="f">ŷ = argmax<sub>c</sub> ∑<sub>i ∈ 𝒩<sub>k</sub>(x)</sub> exp(sim(z, z<sub>i</sub>)/τ) · 1[y<sub>i</sub> = c]</span>
<ul>
<li><b>Nessun addestramento</b>: gli unici iperparametri sono k e τ.</li>
<li>Misura la <b>struttura locale</b> dello spazio degli embedding.</li>
<li>Economico da far girare <b>durante</b> il pretraining per monitorare i progressi; il linear probe richiederebbe di riaddestrare il classificatore ogni volta.</li>
</ul>
<p>Il peso exp(sim/τ) fa contare di più i vicini più simili; con τ → ∞ diventa il voto di maggioranza semplice.</p>
<div class="box b"><b>Dal libro · {C30}, § 30.4.1</b><p>È lo stesso strumento che il libro usa per valutare le rappresentazioni del capitolo: un classificatore <b>1-nearest-neighbor</b> sugli embedding di ogni strato (fig. 30.5) e la visualizzazione dei vicini di alcune immagini query. Il libro ammette che come valutare una rappresentazione è un problema aperto, e sceglie il test più semplice: «i vicini sono sensati?».</p></div>
<div class="box x"><b>Approfondimento</b><p>Il voto pesato con exp(sim/τ) viene da Wu et al. 2018 (la stessa citazione della slide 24), che usavano τ = 0.07 e k = 200; DINO (L22) usa k = 20.</p></div>
"""))

s(10, "Prototype Learning", R("""
<p><b>Training</b>: un prototipo per classe, l'embedding medio:</p>
<span class="f">μ<sub>c</sub> = (1/|D<sub>c</sub>|) ∑<sub>x ∈ D<sub>c</sub></sub> f<sub>θ</sub>(x)</span>
<p><b>Inferenza</b>: la classe del prototipo più vicino:</p>
<span class="f">ŷ = argmin<sub>c</sub> ‖f<sub>θ</sub>(x) − μ<sub>c</sub>‖<sup>2</sup></span>
<ul>
<li>Si chiama anche classificatore <b>nearest class mean</b> (NCM).</li>
<li>È <b>equivalente a un classificatore lineare</b> (vedi riquadro).</li>
<li>Funziona bene se le classi formano cluster compatti e richiede pochissimi esempi: molto usato nel <b>few-shot learning</b>.</li>
</ul>
<div class="box k"><b>Da saper fare: il NCM è lineare</b><p>Sviluppa il quadrato, con h = f<sub>θ</sub>(x):</p>
<span class="f">‖h − μ<sub>c</sub>‖<sup>2</sup> = ‖h‖<sup>2</sup> − 2 μ<sub>c</sub><sup>⊤</sup>h + ‖μ<sub>c</sub>‖<sup>2</sup></span>
<p>‖h‖<sup>2</sup> è uguale per tutte le classi, quindi non cambia l'argmin. Resta</p>
<span class="f">ŷ = argmax<sub>c</sub> ( w<sub>c</sub><sup>⊤</sup>h + b<sub>c</sub> ),   w<sub>c</sub> = μ<sub>c</sub>,   b<sub>c</sub> = −½ ‖μ<sub>c</sub>‖<sup>2</sup></span>
<p>cioè un classificatore lineare con pesi = prototipi. Il confine fra due classi è l'iperpiano asse del segmento μ<sub>a</sub>μ<sub>b</sub>. Se gli embedding e i prototipi sono normalizzati, i bias sono tutti uguali e il NCM sceglie la classe di similarità coseno massima. Differenza dal linear probe: qui i pesi non si addestrano, si calcolano con una media.</p></div>
"""))

s(11, "Prototype Learning: k-NN contro prototipi", R("""
<p><b>Figura</b>: lo stesso insieme di punti 2D di tre classi (verde, arancione, blu) e lo stesso punto di test (stella nera), classificato in due modi.</p>
<ul>
<li><b>k-NN (k = 5)</b>, a sinistra: la stella è collegata ai suoi 5 vicini; nella figura 3 sono arancioni e 2 verdi, quindi vince l'arancione. Contano solo i punti vicini.</li>
<li><b>Prototipi (medie di classe)</b>, a destra: ogni classe è riassunta da una croce nel suo baricentro; la stella è collegata con linee tratteggiate alle tre croci e prende la classe del prototipo più vicino (nella figura quello arancione, poco più vicino di quello verde).</li>
</ul>
<p>Il punto: il k-NN guarda la <b>struttura locale</b> (e richiede di conservare tutti gli embedding), i prototipi solo la <b>posizione media</b> di ogni classe (un vettore per classe, confini lineari). Si notano anche punti blu sparsi lontano dal loro cluster: il prototipo li ignora, il k-NN ne può essere influenzato.</p>
"""))

# ===================== PRETEXT TASK =====================

s(12, "(Early Historical) Examples of Pretext Tasks", "<p>I primi compiti auto-supervisionati (2014–2018): rotazione, posizione relativa e puzzle, colorizzazione, e i loro limiti.</p>",
  kind='div', sec=("l21-pretext", "Pretext task storici", "slide 12–19"))

s(13, "Pretext Task", R("""
<p><b>Pretext task</b>: si trasforma l'immagine non etichettata e si chiede alla rete di predire una proprietà della trasformazione (o l'informazione mancante).</p>
<ul>
<li>L'etichetta è <b>gratis</b>: la trasformazione l'abbiamo applicata noi.</li>
<li>Si addestra con una loss supervisionata standard (cross-entropy, regressione).</li>
</ul>
<p>Il compito dev'essere <b>risolvibile</b>, <b>non banale</b> (non risolvibile con indizi di basso livello: bordi, colori, artefatti) e <b>semantico</b> (per risolverlo bisogna capire il contenuto). Esempi da altri corsi: il <i>masked language modeling</i> in NLP (BERT), gli obiettivi di autoencoding/ricostruzione.</p>
<div class="box b"><b>Dal libro · {C30}, § 30.5, 30.7, 30.8</b>
<ul>
<li><b>§ 30.5 Predictive encodings</b>: si codifica il dato in z e da z si predice un bersaglio; la predizione è un <b>pretext task</b>, lo scopo è l'encoder. Anche la classificazione per classi semantiche può essere un pretext task se lo scopo è la rappresentazione e non il classificatore.</li>
<li><b>§ 30.7 Imputation</b>: caso speciale in cui il bersaglio è una parte mancante dell'ingresso: pixel mascherati (inpainting), canali mancanti (colorizzazione), fotogrammi futuri (fig. 30.8).</li>
<li><b>§ 30.8 Abstract pretext tasks</b>: predire proprietà astratte, come la rotazione di 90° o la posizione relativa di due patch: per risolverli bisogna conoscere regolarità semantiche e geometriche («le nuvole stanno in alto, il tronco sotto i rami»).</li>
</ul></div>
<div class="box b"><b>Dal libro · Prince § 9.3.7 Self-supervised learning</b><p>Prince divide l'SSL in due famiglie: <b>generativa</b> (si maschera una parte del dato e la si predice: inpainting, parole mascherate) e <b>contrastiva</b> (si confrontano coppie con qualcosa in comune contro coppie scollegate, per esempio «queste due immagini sono trasformazioni l'una dell'altra?»). Nota che per Prince anche la posizione relativa di due patch è un compito contrastivo; nelle slide è un pretext task predittivo.</p></div>
"""))

s(14, "Rotation prediction", R("""
<ul>
<li>Si ruota ogni immagine di r ∈ {0°, 90°, 180°, 270°} e si addestra una CNN a predire r: classificazione a <b>4 classi</b>.</li>
<li>Per predire la rotazione il modello deve riconoscere gli oggetti e il loro <b>orientamento canonico</b> (dov'è la testa, dov'è il cielo).</li>
</ul>
<p><b>Figura</b>: la stessa foto di un cane in quattro versioni, etichettate 0° → classe 0, 90° → classe 1, 180° → classe 2, 270° → classe 3.</p>
<ul>
<li><b>Nessun artefatto</b>: le rotazioni di multipli di 90° non richiedono interpolazione (sono permutazioni dei pixel), quindi la rete non può riconoscerle da tracce di ricampionamento.</li>
<li><b>Fallisce</b> sulle immagini senza orientamento canonico (texture, foto aeree).</li>
</ul>
<p>Riferimento: Gidaris, Singh, Komodakis, ICLR 2018 (RotNet).</p>
<div class="box k"><b>Da saper spiegare</b><p>Perché la rotazione di 45° sarebbe un cattivo pretext task: ruotare di un angolo non multiplo di 90° richiede interpolazione e lascia bordi neri agli angoli; la rete imparerebbe a riconoscere quegli artefatti (una <b>scorciatoia</b>, slide 19) invece del contenuto.</p></div>
"""))

s(15, "Rotation Prediction: Learned Features", R("""
<p><b>Figura</b> (dall'articolo di Gidaris et al., fig. 4): i filtri del <b>primo strato</b> di una AlexNet addestrata (a) in modo supervisionato su ImageNet e (b) a riconoscere la rotazione.</p>
<ul>
<li>In entrambi i casi i filtri sono per lo più <b>filtri di bordo orientati</b> a varie frequenze, più qualche macchia di colore: le stesse strutture dei banchi di filtri (<a href="#L7">L7</a>) e dei filtri appresi delle CNN (<a href="#L15">L15</a>).</li>
<li>Secondo la didascalia, quelli auto-supervisionati sembrano persino <b>più vari</b> di quelli supervisionati.</li>
</ul>
<p>Il punto: un compito senza etichette umane basta a far emergere i filtri di basso livello «giusti».</p>
<div class="box b"><b>Dal libro · {C30}, § 30.5.1 e 30.7: i detector emergono</b><p>Il libro va oltre il primo strato. Una CNN addestrata solo a classificare <b>scene</b> (soggiorno, cucina…) ha negli strati nascosti neuroni che si accendono per oggetti specifici (scale, zattere: fig. 30.7). E la sorpresa raccontata dagli autori: anche una rete addestrata a <b>colorizzare</b> sviluppa detector di oggetti (fig. 30.9). Il libro ne conclude che detector di oggetti emergono per quasi ogni pretext task ragionevole (scene, colorizzazione, inpainting), forse perché gli «oggetti» sono una struttura utile del mondo, non solo una peculiarità umana.</p></div>
"""))

s(16, "Jigsaw puzzles", R("""
<ul>
<li><b>Precursore</b> (Doersch et al. 2015): predire la <b>posizione relativa</b> di due patch, cioè quale degli <b>8 vicini</b> in una griglia 3 × 3 è la seconda patch (classificazione a 8 classi).</li>
<li><b>Jigsaw</b> (Noroozi e Favaro 2016): si mescolano le 9 tessere di una griglia 3 × 3 e si predice la <b>permutazione</b>.</li>
<li>Contro le soluzioni banali: <b>spazi e jitter casuali</b> fra le tessere, color jitter, pixelazione.</li>
</ul>
<p><b>Figura</b>: a sinistra l'esempio di Doersch (un gatto con la griglia: patch centrale e una vicina, «X = (patch, patch); Y = 3», cioè la vicina è nella posizione 3); a destra l'immagine di un cane, le sue tessere con spazi e jitter, e le tessere mescolate di cui predire la permutazione.</p>
<div class="box k"><b>Da saper fare</b><p>Le permutazioni di 9 tessere sono 9! = 362 880: troppe come classi. Noroozi e Favaro ne scelgono un sottoinsieme di <b>1000</b>, prese in modo da essere il più possibile diverse fra loro (distanza di Hamming grande), e la rete classifica fra quelle. Gli spazi fra le tessere servono perché altrimenti la rete accosterebbe i bordi seguendo le linee (continuità dei bordi, slide 19).</p></div>
"""))

s(17, "Colorization", R("""
<ul>
<li>Si converte l'immagine nello spazio colore <b>Lab</b>.</li>
<li>Ingresso: il canale di luminosità <b>L</b>; bersaglio: i canali di colore <b>ab</b>.</li>
<li>Colorare richiede semantica: l'erba è verde, il cielo blu, ma un'auto può essere di qualunque colore.</li>
<li><b>Classificazione</b> su bin quantizzati di ab (non regressione).</li>
<li>Compito naturale con <b>uscita densa</b>: impara feature locali e globali.</li>
<li>Limite: le statistiche dell'ingresso differiscono da quelle a valle (immagini in grigio contro RGB).</li>
</ul>
<p><b>Figura</b>: un cane in bianco e nero («input: L») e la versione a colori («target: ab»).</p>
<div class="box k"><b>Da saper spiegare: perché classificazione e non regressione</b><p>L'auto può essere rossa o blu. Con una loss L2 la predizione ottima è la <b>media</b> dei colori possibili, cioè un grigio-marrone spento. Una distribuzione su bin di colore (nell'articolo Q = 313 bin di ab, con pesi per favorire i colori rari) rappresenta l'ambiguità e permette di scegliere un colore vivace. È lo stesso motivo per cui la cross-entropy gestisce uscite multimodali (<a href="#L15">L15</a>).</p></div>
<div class="box b"><b>Dal libro · {C30}, § 30.7 e 30.10</b><p>Per il libro la colorizzazione è <b>imputation</b> di canali mancanti (fig. 30.8). La stessa coppia grigio/colore ritorna nel § 30.10 come esempio di apprendimento contrastivo per <b>co-occorrenza</b>: invece di predire il colore dal grigio, si chiede che l'embedding dei canali di luminosità coincida con quello dei canali di colore (fig. 30.13, ispirata a Tian et al., Contrastive Multiview Coding).</p></div>
"""))

s(18, "Limitations and Challenges", R("""
<ul>
<li><b>Feature specifiche del compito</b>: gli ultimi strati si specializzano nel pretext task (rotazione, permutazione, colore). L'accuratezza del linear probe ha spesso il <b>picco negli strati intermedi</b>.</li>
<li><b>Scorciatoie</b> (<i>shortcut</i>): la rete sfrutta indizi di basso livello invece della semantica (es. aberrazione cromatica per la posizione delle patch).</li>
<li><b>Fatti a mano</b>: ogni compito richiede ingegneria accurata e codifica un bias induttivo specifico e spesso arbitrario.</li>
<li><b>Divario con il supervisionato</b>: il linear probe restava lontano dal pretraining supervisionato.</li>
</ul>
<p><b>Passo successivo</b>: invece di predire una proprietà della trasformazione, imparare a essere <b>invarianti</b> alle trasformazioni <b>confrontando</b> immagini. Servono trasformazioni sia di colore sia spaziali.</p>
<div class="box b"><b>Dal libro · {C30}, § 30.4.1: nessuno strato è il migliore per tutto</b><p>L'esperimento del libro (autoencoder su forme colorate, 1-NN per strato, fig. 30.5) mostra il fenomeno del primo punto: il <b>colore</b> si classifica meglio direttamente sui pixel (strato 0) e peggiora andando in profondità; la <b>forma</b> fa il contrario. Più in profondità le feature diventano più astratte e più legate all'obiettivo di addestramento. Con un pretext task arbitrario, l'ultimo strato è «troppo» specializzato e quello intermedio è il compromesso migliore.</p></div>
"""))

s(19, "Shortcut learning", R("""
<p><b>Shortcut learning</b>: il modello risolve il pretext task con indizi di basso livello invece della semantica. Esempi:</p>
<ul>
<li><b>Aberrazione cromatica</b>: le lenti spostano i canali di colore verso i bordi dell'immagine, quindi lo spostamento rosso/blu rivela dove si trova una patch (la figura mostra un edificio: in basso, ingrandito, il bordo con frange colorate).</li>
<li><b>Continuità dei bordi</b>: le tessere del puzzle si allineano seguendo le linee.</li>
<li><b>Istogrammi di colore</b>: ritagli della stessa immagine condividono i colori (tornerà in SimCLR, slide 40).</li>
<li><b>Watermark, testo, bordi, artefatti JPEG</b> nelle immagini web.</li>
</ul>
<p>Collegamento: è la stessa famiglia di problemi dei <b>shortcut</b> e degli esempi avversari della <a href="#L14">L14</a>: la rete usa ciò che basta a minimizzare la loss, non ciò che intendiamo noi.</p>
<div class="box x"><b>Approfondimento</b><p>Doersch et al. 2015 si accorsero dell'aberrazione cromatica perché la rete riusciva a dire in che punto dell'immagine si trovava una patch isolata. Il rimedio fu togliere informazione di colore: proiettare i colori verso il grigio o tenere un solo canale per patch. La lezione generale: un'augmentation è anche un modo per <b>cancellare</b> le scorciatoie.</p></div>
"""))

# ===================== CONTRASTIVO =====================

s(20, "Self-Supervised Contrastive Learning", "<p>Confrontare coppie: avvicinare le positive, allontanare le negative.</p>",
  kind='div', sec=("l21-contrastivo", "Apprendimento contrastivo", "slide 20–26"))

s(21, "Contrastive Learning", R("""
<p><b>Obiettivo</b>: uno spazio latente semanticamente significativo per i compiti a valle. <b>Idea</b>: in uno spazio semantico le immagini simili sono vicine, quelle diverse lontane.</p>
<ul>
<li>durante l'addestramento si <b>confrontano coppie</b> di immagini;</li>
<li><b>coppie positive</b> → si avvicinano (<i>pull</i>);</li>
<li><b>coppie negative</b> → si allontanano (<i>push</i>).</li>
</ul>
<p><b>Figura</b> (disegno a mano): tre frecce da un'origine comune; la freccia dell'ancora viene spinta più lontano («push further») da una e tirata più vicino («pull closer») all'altra.</p>
<p>Due scelte di progetto: (1) come si definiscono e campionano coppie positive e negative; (2) quale loss si usa. Il resto della lezione risponde a queste due domande.</p>
<div class="box b"><b>Dal libro · {C30}, § 30.10 Contrastive Learning</b>
<ul>
<li>Il libro parte dall'idea di <b>compressione supervisionata</b>: invece di limitare i bit (autoencoder, clustering), si dice <b>quale</b> informazione buttare. Per essere invarianti a una trasformazione T basta penalizzare la deviazione: <b>alignment loss</b> <span class="f">‖f(T(x)) − f(x)‖<sub>2</sub><sup>2</sup></span></li>
<li>Il difetto: se f restituisce sempre il vettore zero, l'allineamento è perfetto. È il <b>collasso della rappresentazione</b>.</li>
<li>Il contrastivo lo corregge aggiungendo un termine che <b>allontana</b> le coppie che non vogliamo rendere uguali. Positive: (x, T(x)); negative: due campioni presi <b>indipendentemente</b> dalla distribuzione dei dati (fig. 30.12).</li>
<li>Collegamento con il resto del libro: le CNN ottengono l'invarianza alla traslazione <b>con l'architettura</b> (convoluzione equivariante + pooling, {C24}); il contrastivo la ottiene <b>con l'obiettivo</b>, per qualunque trasformazione si scelga.</li>
<li>Il contrastivo è parente del clustering: il clustering è il caso estremo in cui punti simili vanno sullo <b>stesso</b> embedding.</li>
</ul></div>
"""))

s(22, "Positive and negative pairs", R("""
<p>Le loss contrastive funzionano sia in modo supervisionato sia auto-supervisionato.</p>
<ul>
<li><b>Supervisionato</b>: positivi = campioni della <b>stessa classe</b>; negativi = di classi diverse. Esempi: riconoscimento di volti, re-identificazione di persone (dove le classi sono tante e cambiano, quindi serve uno spazio di distanze più che un classificatore).</li>
<li><b>Auto-supervisionato</b>: niente etichette, le coppie vanno <b>definite</b>: positivi = due viste aumentate della <b>stessa immagine</b>; negativi = viste di <b>immagini diverse</b>.</li>
</ul>
<div class="box b"><b>Dal libro · {C30}, § 30.10: due modi di fare coppie</b><p>Il libro distingue il contrastivo per <b>trasformazioni</b> (positivi = x e T(x), come qui) e per <b>co-occorrenza</b> (positivi = due segnali che compaiono insieme: immagine e suono della stessa scena, canali di luminosità e di colore della stessa foto). Poi mostra che sono la stessa cosa: due segnali co-occorrenti sono due «viste» V<sub>1</sub>(X), V<sub>2</sub>(X) di un segnale totale, e una trasformazione è un modo di produrre una vista (nella colorizzazione, la trasformazione è «togli i canali di colore»). CLIP (immagine e testo) è contrastivo per co-occorrenza (Szeliski § 5.4.7).</p></div>
<div class="box x"><b>Approfondimento: Szeliski § 5.3.4</b><p>Nel caso supervisionato si parla di <b>metric learning</b>: imparare un embedding in cui la distanza abbia senso. Le loss che lo fanno si chiamano anche <i>ranking losses</i>. Si addestra con una rete <b>siamese</b>: due copie con pesi condivisi, la loss sulla coppia, il gradiente che passa in entrambe.</p></div>
"""))

s(23, "Triplet Loss", R("""
<p>L'esempio più semplice di loss contrastiva: la <b>triplet loss</b>, con ancora a, positivo p, negativo n e margine α:</p>
<span class="f">ℒ = max(0, ‖z<sub>a</sub> − z<sub>p</sub>‖<sup>2</sup> − ‖z<sub>a</sub> − z<sub>n</sub>‖<sup>2</sup> + α)</span>
<p><b>Figura</b> (FaceNet): prima dell'addestramento il negativo (rosso) è più vicino all'ancora (blu) del positivo (verde); dopo il «LEARNING» il positivo è vicino e il negativo lontano.</p>
<ul>
<li>La loss è zero quando il negativo è più lontano del positivo <b>di almeno α</b>: oltre quel margine non si spinge più.</li>
<li>Le distanze sono al quadrato, come in FaceNet (Schroff et al. 2015, embedding normalizzati, α = 0.2).</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Con α = 0.2: se ‖z<sub>a</sub> − z<sub>p</sub>‖<sup>2</sup> = 0.5 e ‖z<sub>a</sub> − z<sub>n</sub>‖<sup>2</sup> = 0.6, ℒ = max(0, 0.5 − 0.6 + 0.2) = 0.1: il negativo è più lontano ma non abbastanza. Con ‖z<sub>a</sub> − z<sub>n</sub>‖<sup>2</sup> = 1.0, ℒ = 0 e la tripletta non dà più gradiente: per questo serve cercare triplette difficili (<i>hard negative mining</i>). Per vettori unitari ‖u − v‖<sup>2</sup> = 2 − 2 cos(u, v): distanza e similarità coseno sono la stessa informazione.</p></div>
<div class="box b"><b>Dal libro · {C30}, eq. 30.4, e Szeliski § 5.3.4</b><p>Il libro scrive tre loss con una distanza generica D e la stessa struttura ancora/positivo/negativo:</p>
<ul>
<li><b>Hadsell et al. 2006</b> (la «contrastive loss» originale, nome oggi usato per tutta la famiglia), con due margini: <span class="f">ℒ = max(D(f(x), f(x<sup>+</sup>)) − m<sub>pos</sub>, 0) + max(m<sub>neg</sub> − D(f(x), f(x<sup>−</sup>)), 0)</span> I positivi si tirano solo se distano più di m<sub>pos</sub>, i negativi si spingono solo se distano meno di m<sub>neg</sub>.</li>
<li><b>Triplet</b>: <span class="f">ℒ = max(D(f(x), f(x<sup>+</sup>)) − D(f(x), f(x<sup>−</sup>)) + m, 0)</span> Uguale alla slide con D = distanza al quadrato e m = α.</li>
<li><b>InfoNCE</b>: la slide 32.</li>
</ul>
<p><b>Refuso del libro</b>: nella pagina web l'eq. 30.4 di Hadsell ha le parentesi fuori posto (m<sub>pos</sub> finisce dentro D) e un <b>meno</b> davanti al secondo max: va un <b>più</b>, altrimenti la loss premierebbe i negativi vicini. Szeliski (eq. 5.57) cita la stessa loss e precisa la scelta dell'articolo: quadratica sui simili e <i>hinge</i> quadratica [m − d]<sub>+</sub><sup>2</sup> sui dissimili.</p></div>
"""))

s(24, "Instance Discrimination", R("""
<p><b>Pretext task</b>: ogni immagine è la sua <b>classe</b> (classe surrogata).</p>
<ul>
<li>Due augmentation casuali t, t′ di x danno due <b>viste</b> t(x), t′(x): una coppia positiva. Le viste di altre immagini sono negative.</li>
<li>Il modello deve estrarre feature che <b>identificano l'immagine</b> pur essendo <b>invarianti</b> alle augmentation.</li>
<li><b>ExemplarCNN</b> (Dosovitskiy et al. 2014): una classe per immagine con una testa di classificazione vera. I metodi moderni (SimCLR, MoCo) <b>confrontano direttamente gli embedding</b>.</li>
<li>L'instance discrimination è il compito principale dei metodi contrastivi moderni.</li>
</ul>
<p><b>Figura</b> (da ExemplarCNN): una patch di partenza (colonna bordata di rosso, un animale) e, su ogni riga, sue versioni trasformate con intensità crescente verso i due lati: trasformazioni geometriche nelle prime righe (scala, rotazione) e fotometriche nelle ultime (contrasto, saturazione fino al grigio, tinta dal viola al verde). Tutte formano <b>una sola classe</b>.</p>
<div class="box k"><b>Da saper spiegare: perché una testa per immagine non scala</b><p>Con N immagini una testa di classificazione ha N classi: per ImageNet 1.28 milioni di uscite, e ogni classe vede un solo esempio per epoca. Wu et al. 2018 rendono il compito <b>non parametrico</b>: al posto dei pesi della classe i usano l'embedding stesso dell'immagine i (salvato in una <i>memory bank</i>), e la «probabilità di essere l'immagine i» diventa un softmax delle similarità con temperatura. È esattamente la forma di InfoNCE (slide 32).</p></div>
"""))

s(25, "The Role of Negative Pairs", R("""
<p>Perché bisogna allontanare i negativi?</p>
<ul>
<li>Con i soli positivi c'è una <b>soluzione banale</b>: mandare ogni immagine nello stesso punto (<b>collasso della rappresentazione</b>).</li>
<li>I negativi danno <b>contrasto</b>: il modello deve trovare feature che distinguono un'immagine dalle altre.</li>
<li>I <b>negativi difficili</b> (<i>hard negatives</i>: embedding simili ma immagini diverse) danno i gradienti più informativi.</li>
<li>Un negativo alla volta (triplet) converge lentamente → confronto con <b>molti negativi insieme</b> (N-pair loss, InfoNCE).</li>
</ul>
<p><b>Figura</b> (Sohn 2016): a sinistra una DNN produce l'embedding f; la triplet loss confronta f con un solo f<sup>+</sup> e un solo f<sup>−</sup>, e per vedere altri negativi deve ripetere il confronto più volte (frecce circolari). A destra la <b>(N+1)-tuplet loss</b>: f<sub>1</sub> è tirato verso il suo f<sub>1</sub><sup>+</sup> e spinto via da N − 1 negativi in un colpo solo; e la versione <b>multi-class N-pair</b>, in cui N coppie di classi diverse si fanno da negativi a vicenda (i positivi delle altre coppie sono i negativi di ciascuna).</p>
<div class="box x"><b>Approfondimento</b><p>Il trucco di Sohn è lo stesso di SimCLR (slide 38): con N coppie nel batch ogni esempio ha N − 1 negativi «gratis», già calcolati per le altre coppie. Il costo extra è solo la matrice di similarità N × N.</p></div>
"""))

s(26, "Embedding Space Geometry", R("""
<p>Intuizione geometrica per embedding <b>normalizzati ℓ<sub>2</sub></b>: stanno sulla <b>ipersfera unitaria</b> e si confrontano con la similarità coseno. Proprietà ideali:</p>
<ul>
<li><b>Alignment</b>: le coppie positive sono vicine;</li>
<li><b>Uniformity</b>: gli embedding si distribuiscono su tutta la sfera.</li>
</ul>
<p>I positivi danno l'allineamento, i negativi l'uniformità; le classi semantiche diventano <b>cluster</b> sulla sfera.</p>
<p><b>Figura</b>: tre cerchi (la sfera in 2D) con punti di tre colori. <b>Collasso</b>: tutti i punti in un unico punto (allineati ma non uniformi). <b>Casuale</b>: punti sparsi su tutto il cerchio con i colori mescolati (uniformi ma non allineati). <b>Buono</b>: tre gruppi compatti, uno per colore, distanti fra loro (allineati e uniformi).</p>
<div class="box b"><b>Dal libro · {C30}, § 30.10.1 Alignment and Uniformity</b><p>Wang e Isola (2020) mostrano che InfoNCE ottimizza due termini separabili:</p>
<span class="f">ℒ<sub>align</sub>(f; α) = 𝔼<sub>(x, x<sup>+</sup>) ∼ p<sub>pos</sub></sub> ‖f(x) − f(x<sup>+</sup>)‖<sub>2</sub><sup>α</sup></span>
<span class="f">ℒ<sub>unif</sub>(f; t) = log 𝔼<sub>x, x<sup>−</sup> ∼ p<sub>data</sub></sub> e<sup>−t ‖f(x) − f(x<sup>−</sup>)‖<sub>2</sub><sup>2</sup></sup></span>
<span class="f">ℒ = ℒ<sub>align</sub> + λ ℒ<sub>unif</sub></span>
<ul>
<li>ℒ<sub>unif</sub> è piccola quando tutte le coppie a caso sono lontane: è il «potenziale» che spinge i punti a sparpagliarsi.</li>
<li>La normalizzazione è <b>necessaria</b>: senza, il termine sui negativi spingerebbe gli embedding all'infinito. Sulla sfera il minimo di ℒ<sub>unif</sub> tende alla distribuzione uniforme.</li>
<li>Nell'articolo valori tipici α = 2, t = 2.</li>
</ul>
<p><b>Esperimento del libro (§ 30.10.2, fig. 30.14)</b>: embedding a 2 dimensioni (quindi su un cerchio) per le forme colorate. Con positivi = <b>ritagli</b> della stessa immagine, l'embedding raggruppa per <b>colore</b> e ignora la forma (il colore è l'indizio più facile per riconoscere un ritaglio). Aggiungendo un cambio casuale di <b>tinta, luminosità e saturazione</b>, diventa invariante al colore e raggruppa per <b>forma</b>, con le tre forme sparse uniformemente sul cerchio. È la figura «buona» della slide fatta davvero, ed è l'anticipazione della slide 28: le augmentation decidono cosa l'embedding ignora.</p></div>
"""))

# ===================== AUGMENTATION =====================

s(27, "Augmentations and Invariance in SSL", "<p>Le augmentation definiscono le invarianze della rappresentazione.</p>",
  kind='div', sec=("l21-aug", "Augmentation e invarianza", "slide 27–30"))

s(28, "Augmentation and Invariance", R("""
<p>Con l'instance discrimination l'obiettivo contrastivo chiede <span class="f">f(t(x)) ≈ f(t′(x))  per ogni t, t′ ∈ 𝒯</span></p>
<ul>
<li><b>In SSL</b>: l'insieme di augmentation 𝒯 <b>definisce le invarianze</b> della rappresentazione. È il principale <b>bias induttivo</b> dell'SSL contrastivo.</li>
<li><b>Nelle reti supervisionate</b>: sono le etichette a dire cosa è semantico e cosa disturbo.</li>
<li><b>Nella visione classica</b>: le feature fatte a mano (SIFT, <a href="#L8">L8</a>) erano progettate per essere invarianti a scala, rotazione, illuminazione. Qui le invarianze si <b>imparano</b> dalle augmentation.</li>
</ul>
<div class="box b"><b>Dal libro · {C36}, § 36.2 Data Augmentation</b><p>Nel supervisionato il libro giustifica l'augmentation con l'<b>invarianza dell'etichetta</b>: un'immagine capovolta di un uccello è ancora «uccello», quindi si può aggiungere al dataset con la stessa etichetta. Nell'SSL il ragionamento si rovescia: non c'è etichetta da conservare, e sono le augmentation stesse a <b>dichiarare</b> cosa la rappresentazione deve considerare irrilevante. Per questo nell'SSL sono il cuore del metodo e non un regolarizzatore.</p></div>
"""))

s(29, "Examples", R("""
<p>Tabella augmentation → invarianza indotta:</p>
<ul>
<li><b>Crop + resize</b> → scala, traslazione, occlusione, relazione parte → tutto;</li>
<li><b>Flip</b> → orientamento sinistra-destra;</li>
<li><b>Color jitter</b> → cambi di illuminazione e di camera;</li>
<li><b>Grayscale</b> → colore: costringe a usare forma e texture;</li>
<li><b>Blur</b> → dettagli ad alta frequenza, rumore;</li>
<li><b>Solarize</b> → cambi non lineari di intensità (inverte i pixel sopra una soglia).</li>
</ul>
<p><b>Figura</b>: la foto di un cane trasformata in otto modi: originale, crop + resize (un dettaglio ingrandito), flip, color jitter, spostamento di tinta (cane azzurrato), scala di grigi, blur, solarize (colori invertiti e scuri).</p>
<p>I metodi SSL moderni usano <b>lunghe catene</b> di augmentation per codificare implicitamente molte invarianze.</p>
<div class="box k"><b>Da saper spiegare: perché il crop insegna la relazione parte → tutto</b><p>Due ritagli casuali della stessa foto possono essere uno <b>grande</b> (quasi tutto il cane) e uno <b>piccolo</b> (solo la testa), oppure due parti <b>adiacenti</b>. Chiedere che abbiano lo stesso embedding obbliga la rete a predire il tutto dalla parte e a riconoscere che due parti appartengono allo stesso oggetto: è una forma di predizione del contesto, simile a quella della slide 16 ma senza etichette di posizione.</p></div>
"""))

s(30, "Challenges", R("""
<p>Un'invarianza è utile <b>solo se il compito a valle non ha bisogno di quell'informazione</b>:</p>
<ul>
<li>l'invarianza al <b>colore</b> danneggia i compiti fini dove il colore conta (fiori, specie di uccelli);</li>
<li>l'invarianza alla <b>rotazione</b> danneggia quando l'orientamento è semantico (6 contro 9, disposizione della scena);</li>
<li>crop <b>troppo aggressivi</b> possono dare viste senza oggetti in comune: la coppia positiva non è semanticamente legata (<b>falsi positivi</b>);</li>
<li>augmentation <b>troppo deboli</b>: il compito diventa banale e il modello impara scorciatoie.</li>
</ul>
<div class="box k"><b>Da saper spiegare: il compromesso</b><p>Troppo deboli → il compito si risolve con indizi banali (stessi colori, stessi bordi). Troppo forti → si chiede di identificare come uguali cose che non lo sono, o si cancella informazione utile. In mezzo c'è la scelta giusta, che <b>dipende dal compito a valle</b>. Il libro lo dice in generale (§ 30.11): ogni rappresentazione è un compromesso, buona per alcuni compiti e cattiva per altri.</p></div>
<div class="box x"><b>Approfondimento</b><p>Per lo stesso motivo la catena di augmentation pensata per ImageNet non funziona in domini diversi (slide 48): in istologia il colore della colorazione è informazione, in immagini satellitari la rotazione è irrilevante e si può aggiungere, nel testo il flip è dannoso.</p></div>
"""))

# ===================== InfoNCE =====================

s(31, "InfoNCE Loss", "<p>La loss contrastiva moderna: una cross-entropy fra un positivo e molti negativi.</p>",
  kind='div', sec=("l21-infonce", "Loss InfoNCE", "slide 31–35"))

s(32, "InfoNCE loss: definition", R("""
<p>Dati un'ancora z, un positivo z<sup>+</sup> e N − 1 negativi z<sub>1</sub><sup>−</sup>, …, z<sub>N−1</sub><sup>−</sup>:</p>
<span class="f">ℒ<sub>InfoNCE</sub> = − log [ exp(sim(z, z<sup>+</sup>)/τ) / ( exp(sim(z, z<sup>+</sup>)/τ) + ∑<sub>j=1</sub><sup>N−1</sup> exp(sim(z, z<sub>j</sub><sup>−</sup>)/τ) ) ]</span>
<ul>
<li>sim(u, v) = u<sup>⊤</sup>v / (‖u‖ ‖v‖) è di solito la <b>similarità coseno</b>;</li>
<li>τ è la <b>temperatura</b>;</li>
<li>è una <b>cross-entropy su N «classi»</b> (1 positivo + N − 1 negativi), con classe giusta = il positivo;</li>
<li>il gradiente tira z verso z<sup>+</sup> e lo spinge via da ogni z<sub>j</sub><sup>−</sup> con peso pari alla sua <b>probabilità softmax</b>: i negativi difficili pesano di più.</li>
</ul>
<p>Intuizione: è il solito softmax + cross-entropy (<a href="#L15">L15</a>), adattato a un contesto senza classi: le istanze positiva e negative fanno da <b>classi</b>, le similarità fanno da <b>logit</b>.</p>
<div class="box k"><b>Da saper fare: il gradiente di InfoNCE</b><p>Chiama s<sub>k</sub> = sim(z, z<sub>k</sub>) per k ∈ {+, 1, …, N−1} e p<sub>k</sub> = softmax(s/τ)<sub>k</sub>. Allora</p>
<span class="f">ℒ = −s<sub>+</sub>/τ + log ∑<sub>k</sub> exp(s<sub>k</sub>/τ)</span>
<span class="f">∂ℒ/∂s<sub>k</sub> = (1/τ) ( p<sub>k</sub> − 1[k = +] )</span>
<ul>
<li>Per il positivo il gradiente è (p<sub>+</sub> − 1)/τ &lt; 0: la discesa <b>aumenta</b> s<sub>+</sub>, e smette di spingere quando p<sub>+</sub> → 1.</li>
<li>Per ogni negativo è p<sub>j</sub>/τ &gt; 0: la discesa <b>diminuisce</b> s<sub>j</sub>, con forza proporzionale a p<sub>j</sub>, cioè a quanto quel negativo è «scambiabile» con il positivo. Ecco il peso sui negativi difficili.</li>
<li>Con s<sub>k</sub> = z<sup>⊤</sup>z<sub>k</sub> (vettori normalizzati, trascurando la proiezione sulla sfera): <span class="f">∂ℒ/∂z = (1/τ) ( ∑<sub>k</sub> p<sub>k</sub> z<sub>k</sub> − z<sup>+</sup> ) = (1/τ) ( (p<sub>+</sub> − 1) z<sup>+</sup> + ∑<sub>j</sub> p<sub>j</sub> z<sub>j</sub><sup>−</sup> )</span> cioè z si muove verso z<sup>+</sup> e lontano dalla media dei negativi pesata con p<sub>j</sub>.</li>
</ul>
<p>È la stessa forma «p − y» del gradiente di softmax + cross-entropy rispetto ai logit, con y = one-hot sul positivo.</p></div>
<div class="box b"><b>Dal libro · {C30}, eq. 30.4, e Szeliski § 5.3.4, eq. 5.58</b><p>Il libro scrive InfoNCE con il <b>prodotto scalare</b> f(x)<sup>⊤</sup>f(x<sup>+</sup>)/τ (coincide con il coseno se gli embedding sono normalizzati) e la descrive come un <b>log softmax</b> su un vettore di punteggi: un problema di classificazione in cui la classe giusta è il positivo e le altre sono i negativi; spinge i punti finché il positivo non si distingue da tutti i negativi. Szeliski la attribuisce a Sohn (2016), normalizza gli embedding (‖v̂<sub>i</sub>‖ = 1) e dice che τ «controlla quanto saranno stretti i cluster»; la stessa loss si chiama InfoNCE (van den Oord et al. 2018) e NT-Xent (SimCLR).</p></div>
<div class="box x"><b>Approfondimento: perché «Info» NCE</b><p>Il nome viene da CPC (van den Oord, Li, Vinyals 2018): NCE è la <i>noise-contrastive estimation</i>, cioè distinguere il campione vero da campioni di rumore. Gli autori dimostrano che, con N candidati (1 positivo e N − 1 negativi), <span class="f">I(x; c) ≥ log N − ℒ<sub>N</sub></span> cioè minimizzare InfoNCE <b>massimizza un limite inferiore della mutua informazione</b> fra le due viste. Conseguenze: il limite non può superare log N, quindi per stimare molta informazione servono <b>molti negativi</b> (un motivo dei batch grandi, slide 34); e il valore di ℒ al caso: con tutte le similarità uguali p<sub>k</sub> = 1/N e ℒ = log N (con N = 4, log 4 ≈ 1.39).</p></div>
"""))

s(33, "Temperature", R("""
<p>Come nel softmax standard, τ <b>scala i logit</b> prima del softmax.</p>
<p><b>Figura</b>: probabilità softmax del positivo z<sup>+</sup> (blu) e di tre negativi z<sub>1</sub><sup>−</sup>, z<sub>2</sub><sup>−</sup>, z<sub>3</sub><sup>−</sup> (arancione) per tre temperature: τ = 0.1 → 1.00, 0.00, 0.00, 0.00; τ = 0.5 → 0.62, 0.13, 0.07, 0.19; τ = 2.0 → 0.33, 0.22, 0.19, 0.25.</p>
<ul>
<li><b>τ piccola</b>: distribuzione appuntita, si concentra sui negativi <b>più difficili</b>;</li>
<li><b>τ grande</b>: distribuzione piatta, tutti i negativi pesano uguale, gradienti deboli.</li>
</ul>
<p>Riferimento: Wang e Liu, «Understanding the Behaviour of Contrastive Loss», CVPR 2021.</p>
<div class="box k"><b>Da saper fare: la figura calcolata davvero</b><p>I numeri della figura si ottengono con le similarità s = (s<sub>+</sub>, s<sub>1</sub>, s<sub>2</sub>, s<sub>3</sub>) = (0.8, 0, −0.3, 0.2) (o qualunque loro traslazione: il softmax non cambia se si aggiunge una costante). Verifica a τ = 0.5: logit (1.6, 0, −0.6, 0.4), esponenziali (4.95, 1, 0.55, 1.49), somma 7.99, quindi p = (0.62, 0.125, 0.069, 0.187). Conti completi (numpy):</p>
<ul>
<li><b>τ = 0.1</b>: p = (0.997, 0.0003, 0.00002, 0.0025); ℒ = −log p<sub>+</sub> = 0.003; fra i negativi il più difficile (z<sub>3</sub>, s = 0.2) prende l'<b>88%</b> del peso.</li>
<li><b>τ = 0.5</b>: p = (0.620, 0.125, 0.069, 0.187); ℒ = 0.479; z<sub>3</sub> prende il 49% del peso dei negativi.</li>
<li><b>τ = 2</b>: p = (0.335, 0.224, 0.193, 0.248); ℒ = 1.095 (vicino al valore al caso log 4 = 1.386); z<sub>3</sub> prende il 37%: quasi uniforme.</li>
</ul>
<p>Gradienti ∂ℒ/∂s<sub>k</sub> = (p<sub>k</sub> − 1[k=+])/τ: a τ = 2 sono (−0.33, 0.11, 0.10, 0.12), piccoli e quasi uguali sui negativi; a τ = 0.5 (−0.76, 0.25, 0.14, 0.37); a τ = 0.1 (−0.03, 0.003, 0.0002, 0.025): l'esempio è già «risolto» e quel poco di gradiente che resta va quasi tutto sul negativo difficile.</p></div>
<div class="box x"><b>Approfondimento</b><p>Wang e Liu chiamano questo comportamento <i>hardness-aware</i> e parlano di un dilemma uniformità/tolleranza: τ piccola rende l'embedding molto uniforme ma spinge via anche immagini semanticamente simili (che come istanze sono «negativi»), τ grande tollera di più i vicini semantici. In SimCLR (Tab. 5 dell'articolo, embedding normalizzati) il top-1 lineare migliore si ha con τ = 0.1 (64.4%), contro 59.7% a τ = 0.05 e 60.7% a τ = 0.5. MoCo usa τ = 0.07. Ripasso: la temperatura del softmax è in <a href="#L15">L15</a>; il libro la tratta in {C12}, § 12.7.4 (con la convenzione e<sup>−τx</sup>, segno insolito).</p></div>
"""))

s(34, "Negatives Pairs", R("""
<ul>
<li>I metodi allo stato dell'arte usano un numero di negativi molto grande. «SimCLR uses batches &gt; 4096».</li>
<li>Più negativi → più probabilità di includere <b>negativi difficili</b>, gradienti più informativi.</li>
<li>Copertura migliore della distribuzione dei dati → embedding più <b>uniformi</b>.</li>
</ul>
<p><b>Problema</b>: il numero di negativi è legato alla <b>dimensione del batch</b>. La memoria cresce linearmente, la matrice di similarità <b>quadraticamente</b>; le catene di augmentation sono costose e limitate dalla CPU.</p>
<div class="box k"><b>Da saper fare</b><p>Con batch B = 4096 SimCLR ha 2B = 8192 viste: la matrice delle similarità ha 8192<sup>2</sup> ≈ 6.7 · 10<sup>7</sup> elementi (circa 268 MB in float32, solo per i logit), e ogni vista ha 2B − 2 = 8190 negativi.</p></div>
<div class="box w"><b>Attenzione: precisazione sul batch</b><p>Nell'articolo di SimCLR il batch <b>di default è 4096</b>, e gli esperimenti vanno da 256 a 8192 (fino a 32K in appendice); non «più di 4096». Con 100 epoche il batch grande aiuta molto, con addestramenti lunghi la differenza si riduce (slide 41).</p></div>
<div class="box x"><b>Approfondimento: MoCo</b><p>MoCo (He et al. 2020, citato a slide 48 e da Szeliski § 5.4.7) scollega i negativi dal batch. Tiene una <b>coda</b> (nell'articolo 65 536 chiavi) degli embedding dei batch precedenti, calcolati da un <b>encoder momentum</b>, copia lentamente aggiornata della rete: θ<sub>k</sub> ← m θ<sub>k</sub> + (1 − m) θ<sub>q</sub> con m = 0.999. Così le chiavi in coda restano coerenti fra loro anche se la rete cambia, e i negativi sono tanti con un batch normale (256). La loss è sempre InfoNCE (τ = 0.07). Prima di MoCo, Wu et al. 2018 usavano una <i>memory bank</i> di tutti gli embedding del dataset, che però invecchiano. Szeliski: MoCo v2 unisce MoCo e le idee di SimCLR (testa MLP, augmentation forti).</p></div>
"""))

s(35, "Representation collapse", R("""
<p><b>Collasso completo</b>: f(x) = c per ogni x.</p>
<ul>
<li>Le coppie positive sono perfettamente allineate, «la loss è zero»;</li>
<li>la rappresentazione non contiene informazione;</li>
<li>sintomi: <b>deviazione standard</b> degli embedding sul batch → 0, accuratezza k-NN al livello del caso.</li>
</ul>
<p><b>Collasso dimensionale</b>: gli embedding occupano solo un <b>sottospazio di bassa dimensione</b>.</p>
<ul>
<li>non è rilevato dalla loss e spreca capacità;</li>
<li>sintomo: <b>valori singolari</b> della covarianza degli embedding che decadono in fretta.</li>
</ul>
<p>La sfida principale dell'SSL: rappresentazioni di qualità <b>evitando il collasso</b>.</p>
<p><b>Figura</b> (Jing et al. 2022): (b) collasso completo, tutti gli embedding in un unico punto della sfera (un fascio sottile); (c) collasso dimensionale, gli embedding riempiono solo una fascia piatta (un piano) dentro la sfera.</p>
<div class="box w"><b>Attenzione: «la loss è zero» dipende dalla loss</b><p>È vero per una loss di <b>solo allineamento</b> (‖f(x) − f(x<sup>+</sup>)‖<sup>2</sup> = 0) e per la loss di SimSiam (che collassando arriva al suo minimo −1, slide 43). Per <b>InfoNCE</b> il collasso è invece penalizzato: tutte le similarità valgono 1, p<sub>k</sub> = 1/N e ℒ = <b>log N</b>, il valore al caso (con 2B − 1 = 8191 candidati, ≈ 9.0). È proprio per questo che i negativi impediscono il collasso completo.</p></div>
<div class="box k"><b>Da saper fare: misurare il collasso</b><p>Il test di SimSiam: normalizza gli embedding, calcola la deviazione standard di ogni canale sul batch. Se c'è collasso vale 0; se gli embedding sono ben sparsi sulla sfera di dimensione d vale circa <b>1/√d</b> (per d = 2048, circa 0.022). Per il collasso dimensionale: valori singolari della matrice di covarianza in scala log, ordinati; una caduta brusca indica che molte dimensioni sono inutilizzate.</p></div>
"""))

# ===================== SimCLR =====================

s(36, "SimCLR", "<p>Il framework contrastivo semplice: augmentation, encoder, testa di proiezione, NT-Xent.</p>",
  kind='div', sec=("l21-simclr", "SimCLR", "slide 36–41"))

s(37, "SimCLR", R("""
<p><b>Instance discrimination</b>: massimizzare l'<b>accordo</b> fra due viste aumentate in modo diverso della stessa immagine, con una loss contrastiva nello spazio latente.</p>
<p>Tre risultati principali (Chen, Kornblith, Norouzi, Hinton, ICML 2020):</p>
<ol>
<li>la <b>composizione</b> delle augmentation è decisiva per avere un pretext task efficace;</li>
<li>una <b>testa di proiezione non lineare</b> apprendibile fra rappresentazione e loss migliora molto la rappresentazione;</li>
<li>il contrastivo beneficia di <b>batch più grandi</b> e <b>addestramenti più lunghi</b> rispetto al supervisionato.</li>
</ol>
<div class="box b"><b>Dal libro · Szeliski § 5.4.7 e Prince, note del cap. 9</b><p>Szeliski: SimCLR usa mini-batch fissi e applica una loss contrastiva (la NT-Xent, simile alla 5.58) fra ogni campione del batch e tutti gli altri, con augmentation aggressive; prima di confrontare gli embedding applica un MLP. Prince: la rete mappa versioni della stessa immagine trasformate fotometricamente e geometricamente nella stessa rappresentazione, respingendo quelle di immagini diverse, per diventare «indifferente» alle trasformazioni irrilevanti. Il visionbook non nomina SimCLR, ma il § 30.10 ne è la teoria.</p></div>
"""))

s(38, "SimCLR architecture", R("""
<p>Per ogni immagine x di un batch di dimensione B:</p>
<ol>
<li>due augmentation: x̃<sub>i</sub> = t(x), x̃<sub>j</sub> = t′(x), con t, t′ ∼ 𝒯;</li>
<li><b>encoder</b> f (es. ResNet-50): h<sub>i</sub> = f(x̃<sub>i</sub>), usato <b>a valle</b>;</li>
<li><b>testa di proiezione</b> g (MLP): z<sub>i</sub> = g(h<sub>i</sub>), usata <b>solo dalla loss</b>;</li>
<li>loss <b>NT-Xent</b> sulle 2B viste:</li>
</ol>
<span class="f">ℓ<sub>i,j</sub> = − log [ exp(sim(z<sub>i</sub>, z<sub>j</sub>)/τ) / ∑<sub>k=1</sub><sup>2B</sup> 1<sub>[k≠i]</sub> exp(sim(z<sub>i</sub>, z<sub>k</sub>)/τ) ]</span>
<p>Ogni vista ha <b>1 positivo e 2B − 2 negativi</b> (le altre viste del batch). NT-Xent (<i>normalized temperature-scaled cross entropy</i>) è un caso particolare di InfoNCE.</p>
<p><b>Figura</b>: x in basso, due rami con t ∼ 𝒯 e t′ ∼ 𝒯 che danno x̃<sub>i</sub> e x̃<sub>j</sub>; ognuno passa per f(·) (stessi pesi) dando h<sub>i</sub>, h<sub>j</sub> («Representation») e poi per g(·) dando z<sub>i</sub>, z<sub>j</sub>, fra i quali si «massimizza l'accordo».</p>
<div class="box k"><b>Da saper fare: contare i negativi</b><p>Le viste sono 2B. Per la vista i il denominatore somma su tutti i k ≠ i: 2B − 1 termini. Uno è il positivo j (l'altra vista della stessa immagine), gli altri <b>2B − 2</b> sono le due viste di ciascuna delle B − 1 immagini diverse. Quindi NT-Xent è una classificazione a 2B − 1 classi; con B = 4096, 8190 negativi. La loss totale è la media di ℓ<sub>i,j</sub> su <b>tutte le 2B</b> viste, cioè sia ℓ<sub>i,j</sub> sia ℓ<sub>j,i</sub> per ogni coppia: <span class="f">ℒ = (1/2B) ∑<sub>k=1</sub><sup>B</sup> [ ℓ(2k−1, 2k) + ℓ(2k, 2k−1) ]</span></p>
<p>Differenza dalla InfoNCE della slide 32: il denominatore di NT-Xent contiene anche i negativi presi dalla <b>stessa</b> «parte» del batch (le due viste di ogni altra immagine), non un insieme separato di negativi.</p></div>
<div class="box x"><b>Approfondimento</b><p>Due dettagli dell'articolo: l'ottimizzatore è LARS (learning rate 0.3 × B/256) e la BatchNorm è <b>globale</b>, con statistiche aggregate su tutti i dispositivi: con la BN locale le due viste sullo stesso dispositivo condividerebbero statistiche e la rete potrebbe usare questa «fuga di informazione» per riconoscere i positivi (un'altra scorciatoia).</p></div>
"""))

s(39, "Projection Head", R("""
<span class="f">x →<sup>f</sup> h →<sup>g</sup> z,   g(h) = W<sub>2</sub> ReLU(W<sub>1</sub> h)</span>
<ul>
<li>La loss si calcola su z, ma a valle si usa <b>h</b> (la testa di proiezione si butta).</li>
<li>Un linear probe su h funziona <b>meglio</b> che su z. Intuizione:
  <ul>
  <li>la loss contrastiva rende z <b>invariante</b> alle augmentation, togliendo informazione (colore, orientamento…) che a valle può servire;</li>
  <li>è g a farsi carico di questa perdita, mentre h conserva una rappresentazione più ricca.</li>
  </ul></li>
<li>La separazione «encoder + proiettore» si ritrova in quasi tutti i metodi SSL moderni.</li>
</ul>
<div class="box x"><b>Approfondimento: i numeri dell'articolo</b><p>g è un MLP con uno strato nascosto e ReLU, uscita z a 128 dimensioni; h di una ResNet-50 ha 2048 dimensioni. Il linear probe su h è più alto di <b>oltre 10 punti</b> rispetto a quello su z. Gli autori verificano anche che da h si può predire con un MLP quale augmentation è stata applicata (rotazione, cambi di colore) molto meglio che da z: l'informazione buttata da z è proprio quella delle augmentation. È lo stesso fenomeno della slide 18 (gli strati vicini all'obiettivo si specializzano), ora spostato dentro una testa che si scarta.</p></div>
"""))

s(40, "SimCLR data augmentation pipeline", R("""
<p>Catena semplificata, applicata <b>indipendentemente</b> a ogni vista:</p>
<ol>
<li>crop casuale con resize e flip orizzontale;</li>
<li>distorsione del colore: color jitter e grigio casuale;</li>
<li>blur gaussiano.</li>
</ol>
<p><b>Risultati sperimentali</b>:</p>
<ul>
<li>nessuna augmentation da sola basta;</li>
<li><b>crop + distorsione del colore</b> è la coppia più importante;</li>
<li>senza distorsione del colore, i ritagli della stessa immagine si riconoscono dagli <b>istogrammi di colore</b> (scorciatoia, slide 19);</li>
<li>il contrastivo vuole augmentation di colore <b>più forti</b> del supervisionato.</li>
</ul>
<div class="box x"><b>Approfondimento: i parametri dell'articolo</b><ul>
<li>Crop con area fra l'8% e il 100% dell'immagine e rapporto d'aspetto fra 3/4 e 4/3, resize a 224 × 224, flip con probabilità 0.5.</li>
<li>Color jitter di forza s = 1 (luminosità, contrasto, saturazione 0.8 s, tinta 0.2 s) con probabilità 0.8; grigio con probabilità 0.2.</li>
<li>Blur gaussiano con probabilità 0.5, σ fra 0.1 e 2.0.</li>
</ul></div>
<div class="box b"><b>Dal libro · {C30}, § 30.10.2</b><p>L'esperimento del libro sulle forme colorate è questa slide in miniatura: con i soli ritagli l'embedding impara il colore (l'indizio più facile, come gli istogrammi qui); aggiungendo cambi casuali di tinta, luminosità e saturazione impara la forma.</p></div>
"""))

s(41, "SimCLR training requirements", R("""
<ul>
<li>Servono <b>batch grandi</b> per avere molti negativi.</li>
<li>Servono <b>addestramenti lunghi</b> (centinaia di epoche).</li>
</ul>
<p><b>Figura a sinistra</b> (fig. 9 dell'articolo): top-1 del linear probe di una ResNet-50 per batch da 256 a 8192 (barre colorate) e per 100…1000 epoche. A 100 epoche il batch conta molto (da circa 57.5% con 256 a circa 65% con 8192); a 1000 epoche le barre sono tutte fra circa 67% e 69%: con addestramenti lunghi il vantaggio del batch grande si riduce.</p>
<p><b>Figura a destra</b> (fig. 7): top-1 contro numero di parametri per ResNet di varia profondità e larghezza. Punti blu: SimCLR a 100 epoche; stelle rosse: SimCLR a 1000 epoche; croci verdi: ResNet supervisionate (90 epoche). Le reti più larghe guadagnano di più: la R50 (4×) di SimCLR arriva circa al livello della R50 supervisionata (≈ 76%).</p>
<div class="box x"><b>Approfondimento: i numeri</b><p>Dall'articolo: linear probe su ImageNet 69.3% con ResNet-50 e 76.5% con ResNet-50 (4×), circa pari alla ResNet-50 supervisionata. Il divario con il supervisionato si chiude soprattutto <b>aumentando la capacità</b>: il contrastivo beneficia dei modelli grandi più del supervisionato.</p></div>
"""))

# ===================== SimSiam =====================

s(42, "SimSiam", "<p>Un metodo siamese senza negativi: basta lo stop-gradient.</p>",
  kind='div', sec=("l21-simsiam", "SimSiam", "slide 42–44"))

s(43, "SimSiam", R("""
<ul>
<li><b>SimSiam</b> (Chen e He, CVPR 2021): un metodo SSL semplice.</li>
<li><b>Loss</b>: similarità coseno negativa, simmetrizzata:</li>
</ul>
<span class="f">𝒟(p<sub>1</sub>, z<sub>2</sub>) = − (p<sub>1</sub> / ‖p<sub>1</sub>‖<sub>2</sub>) · (z<sub>2</sub> / ‖z<sub>2</sub>‖<sub>2</sub>)</span>
<ul>
<li><b>Stop-grad</b> blocca il gradiente: i due encoder sono lo stesso (pesi condivisi) ma il segnale di apprendimento passa solo in una direzione.</li>
<li>«Projector only in the first augmentation» (vedi riquadro Attenzione).</li>
</ul>
<p><b>Figura</b>: l'immagine x dà due viste x<sub>1</sub>, x<sub>2</sub>; entrambe passano per lo stesso <b>encoder f</b>; a sinistra segue un <b>predictor h</b>, e la sua uscita si confronta («similarity») con l'uscita del ramo destro, sul quale una freccia tratteggiata barrata indica lo <b>stop-grad</b>.</p>
<div class="box w"><b>Attenzione: due imprecisioni</b>
<ul>
<li><b>«Contrastive»</b>: SimSiam <b>non usa negativi</b>. La didascalia della fig. 1 dell'articolo dice che non usa «né coppie negative né un encoder momentum», e gli autori lo presentano come «SimCLR senza negativi». La loss confronta solo le due viste della stessa immagine. È un metodo <b>siamese non contrastivo</b> (Szeliski § 5.4.7: BYOL mostra che si possono togliere i negativi, SimSiam che basta lo stop-gradient). Il suo posto naturale è nella L22, accanto a BYOL.</li>
<li><b>«Projector only in the first augmentation»</b>: il modulo presente in un solo ramo è il <b>predictor h</b>, non il projector. Il projector (MLP a 3 strati) fa parte dell'<b>encoder f</b> e sta in entrambi i rami (pseudocodice: «f: backbone + projection mlp»). Inoltre, poiché la loss è simmetrizzata, il predictor agisce <b>a turno su entrambe le viste</b>: p<sub>1</sub> = h(z<sub>1</sub>) contro z<sub>2</sub>, e p<sub>2</sub> = h(z<sub>2</sub>) contro z<sub>1</sub>.</li>
</ul></div>
<div class="box k"><b>Da saper spiegare: perché non collassa</b><p>Senza negativi la soluzione costante ha loss minima (−1). L'articolo mostra che:</p>
<ul>
<li><b>senza stop-gradient</b> la loss arriva subito a −1 e il modello collassa (linear probe 0.1%, il caso su 1000 classi);</li>
<li><b>senza predictor</b> (h = identità) collassa ugualmente (0.1%);</li>
<li>con entrambi la deviazione standard degli embedding normalizzati resta vicina a 1/√d: niente collasso. Linear probe su ImageNet: circa 68% a 100 epoche (67.7% con la configurazione di default, 68.1% nella tabella di confronto) e 71.3% a 800, con batch 512 (o 256) e SGD normale: niente batch enormi.</li>
</ul>
<p>Interpretazione degli autori: lo stop-gradient trasforma il problema in un'alternanza simile a k-means/EM, in cui il ramo con stop-gradient fa da <b>bersaglio fisso</b> per il passo corrente.</p></div>
"""))

s(44, "SimSiam - Pseudocode", R("""
<p><b>Figura</b>: l'Algorithm 1 dell'articolo, pseudocodice in stile PyTorch.</p>
<ul>
<li>Commenti: <code>f</code> = backbone + projection MLP; <code>h</code> = prediction MLP.</li>
<li>Per ogni minibatch <code>x</code>: <code>x1, x2 = aug(x), aug(x)</code>; <code>z1, z2 = f(x1), f(x2)</code> (proiezioni n × d); <code>p1, p2 = h(z1), h(z2)</code> (predizioni n × d).</li>
<li>Loss <code>L = D(p1, z2)/2 + D(p2, z1)/2</code>, poi <code>L.backward()</code> e aggiornamento SGD di <code>f</code> e <code>h</code>.</li>
<li><code>D(p, z)</code>: <code>z = z.detach()</code> (<b>stop gradient</b>), normalizza p e z lungo dim=1, restituisce <code>-(p*z).sum(dim=1).mean()</code>, cioè il coseno negativo medio sul batch.</li>
</ul>
<div class="box k"><b>Da saper fare: leggere lo pseudocodice</b><p>Lo stop-gradient è il <code>detach()</code> dentro D, applicato sempre al <b>secondo</b> argomento (la z dell'altro ramo). Nel primo termine il gradiente passa per p1 = h(f(x1)) e non per z2; nel secondo per p2 = h(f(x2)) e non per z1. Quindi entrambe le viste ricevono gradiente attraverso il predictor, ed entrambe fanno anche da bersaglio: è la simmetrizzazione che smentisce «projector only in the first augmentation». Rispetto a SimCLR mancano la matrice di similarità B × B, la temperatura e i negativi.</p></div>
"""))

# ===================== CONCLUSIONI =====================

s(45, "Conclusions", "<p>Riepilogo, consigli pratici, letture.</p>",
  kind='div', sec=("l21-concl", "Conclusioni", "slide 45–51"))

s(46, "Pretext Tasks in Contrastive Learning", R("""
<p>Confronto fra pretext task (slide 12–19) e apprendimento contrastivo:</p>
<ul>
<li><b>Obiettivo</b>: predire una proprietà della trasformazione / essere <b>invarianti</b> alla trasformazione.</li>
<li><b>Segnale</b>: etichette progettate a mano (rotazione, permutazione, colore) / <b>confronti fra istanze</b>.</li>
<li><b>Feature</b>: specializzate nel pretext task / generiche, semantiche.</li>
<li><b>Bias induttivo</b>: un compito specifico / l'<b>insieme delle augmentation</b>.</li>
<li><b>Prestazioni</b>: lontane dal supervisionato / vicine al supervisionato (o migliori).</li>
</ul>
<div class="box b"><b>Dal libro · {C30}, Tab. 30.1</b><p>Nella classificazione del libro i pretext task stanno sotto il principio di <b>predizione</b>, il contrastivo sotto quello di <b>compressione</b> («ottenere invarianza alle trasformazioni di vista»). È la stessa contrapposizione della prima riga della tabella: predire la trasformazione contro dimenticarla.</p></div>
"""))

s(47, "Self-Supervised Contrastive Learning: riepilogo", R("""
<p><b>Figura</b>: la catena in cinque blocchi: immagine non etichettata x → due augmentation t(x), t′(x) → encoder f (h) → proiezione g (z) → InfoNCE (positivi contro negativi).</p>
<ul>
<li>Le <b>augmentation</b> definiscono le invarianze (le coppie positive).</li>
<li>I <b>negativi</b> impediscono il collasso.</li>
<li>L'<b>encoder f</b> si tiene per i compiti a valle, la <b>testa g</b> si butta.</li>
<li><b>Valutazione</b>: trasferimento alla classificazione con linear probe.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Questa slide è la risposta di due minuti a «che cos'è l'apprendimento contrastivo auto-supervisionato?». Esercitati a ridirla aggiungendo per ogni blocco il perché: augmentation = bias induttivo; f e g separati perché g assorbe la perdita di informazione; InfoNCE = cross-entropy sulle similarità con temperatura; negativi = uniformità e niente collasso.</p></div>
"""))

s(48, "Practical Tips", R("""
<ul>
<li><b>Batch e negativi</b>: batch piccoli = pochi negativi e contrasto debole. Se non ci si possono permettere batch grandi, si usa una <b>coda</b> (MoCo, riquadro della slide 34) o un metodo <b>senza negativi</b> (SimSiam, BYOL).</li>
<li><b>Augmentation adatte al compito</b>: non togliere informazione che servirà (colore per le specie, orientamento per testo e immagini mediche). Le catene di default di ImageNet non si trasferiscono a ogni dominio.</li>
<li><b>Risultati del linear probe</b>: dipendono dagli iperparametri del probe e favoriscono feature linearmente separabili; k-NN, finetuning completo e low-shot possono dare classifiche diverse.</li>
<li><b>Iperparametri</b>: quelli ottimi per il supervisionato non valgono per l'SSL (learning rate, epoche, weight decay).</li>
<li><b>Caricamento dati</b>: le augmentation pesanti su CPU possono essere il collo di bottiglia; spostarle su GPU o usare pipeline ottimizzate.</li>
</ul>
"""))

s(49, "Further Reading", R("""
<ul>
<li>«A Cookbook of Self-Supervised Learning» (Balestriero et al. 2023): <a href="https://arxiv.org/abs/2304.12210" target="_blank">arXiv 2304.12210</a>. Più dettagli sull'addestramento dei metodi contrastivi e sulle diverse loss.</li>
</ul>
<p>Sui libri: visionbook {C30} (§ 30.6–30.10) e {C37} (§ 37.2–37.3), Szeliski § 5.3.4 e § 5.4.7, Prince § 9.3.7 (vedi la sezione Studia dal libro in fondo).</p>
"""))

s(50, "Key Takeaways", R("""
<ul>
<li>L'SSL impara rappresentazioni da dati non etichettati con etichette auto-generate: il pretext task è solo uno strumento.</li>
<li><b>Contrastivo</b>: avvicinare le coppie positive, allontanare le negative. In SSL i positivi sono viste aumentate della stessa immagine (instance discrimination).</li>
<li>Le <b>augmentation</b> sono il bias induttivo principale: decidono a cosa il modello diventa invariante.</li>
<li><b>InfoNCE</b>: cross-entropy su un positivo e molti negativi, <b>limite inferiore della mutua informazione</b>; la temperatura regola l'attenzione ai negativi difficili.</li>
<li><b>SimCLR</b>: negativi presi dal batch, quindi batch grandi.</li>
<li><b>Valutazione</b>: linear probe, k-NN, prototipi, finetuning, trasferimento a compiti densi.</li>
<li>Attenzione a <b>collasso</b> e <b>scorciatoie</b>.</li>
</ul>
<div class="box k"><b>Da saper spiegare: il limite sulla mutua informazione</b><p>La slide lo afferma senza spiegarlo. Versione da orale: con N candidati, I(v<sub>1</sub>; v<sub>2</sub>) ≥ log N − ℒ<sub>InfoNCE</sub> (van den Oord et al. 2018). Abbassare la loss alza il limite inferiore all'informazione condivisa fra le due viste; il limite non supera log N, quindi più negativi permettono di «misurare» più informazione. Le augmentation decidono quale informazione è condivisa (e quindi conservata), il resto viene buttato: è la «compressione supervisionata» del libro (§ 30.10).</p></div>
"""))

s(51, "Next Lectures", R("""
<ul>
<li>Paradigmi <b>mascherati</b> e di <b>distillazione</b> e i metodi SSL allo stato dell'arte: è la <a href="#L22">L22</a> (BYOL, DINO, MAE, DINOv2/v3).</li>
<li>Un laboratorio sull'SSL (non ancora disponibile).</li>
</ul>
<div class="box b"><b>Dal libro · {C37}, § 37.4 Learning from a Teacher</b><p>Per prepararsi alla L22: nella <b>knowledge distillation</b> lo studente imita la distribuzione di probabilità (pmf) prodotta da un insegnante invece di un'etichetta one-hot. Il bersaglio «morbido» dà più informazione (un gatto «90% gatto, 10% tigre» dice qualcosa su entrambe le classi). DINO usa proprio questo schema, con insegnante e studente che sono due copie della stessa rete.</p></div>
"""))
