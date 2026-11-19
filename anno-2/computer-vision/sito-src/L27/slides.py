VB = 'https://visionbook.mit.edu/'
def L(slug, txt): return f'<a href="{VB}{slug}" target="_blank">{txt}</a>'
LK = {
 '{C32}': L('generative_models.html', 'cap. 32'),
 '{C33}': L('generative_modeling_and_rep_learning.html', 'cap. 33'),
 '{C34}': L('conditional_generative_models.html', 'cap. 34'),
 '{C51}': L('VLMs.html', 'cap. 51'),
 '{C26}': L('transformers.html', 'cap. 26'),
 '{C24}': L('convolutional_neural_nets.html', 'cap. 24'),
}
def P(n): return f' <em>· pag. {n}/59</em>'
def R(t):
    for k, v in LK.items(): t = t.replace(k, v)
    return t

# ===================== INTRODUZIONE =====================

s(1, "Diffusion Models: copertina", R("""
<p>Lezione del 18 novembre 2026, tenuta da <b>Donald Shenaj</b> come la <a href="#L24">L24</a> e la <a href="#L25">L25</a>. Tema: i <b>modelli di diffusione</b>, cioè i modelli che generano immagini (e video) partendo da rumore gaussiano e togliendolo un poco alla volta. Sono la tecnologia dietro Stable Diffusion, FLUX, Sora, Veo.</p>
<p>Il PDF ha 59 pagine e il footer stampa «n / 59» con n = pagina del PDF, copertina compresa. Non hanno footer le due pagine di sole immagini (5 e 6) e le divisorie (7, 29, 45). La pag. 59 non è una slide ma la panoramica delle miniature generata da Beamer.</p>
<div class="box k"><b>Il filo della lezione in una frase</b><p>Distruggere un'immagine aggiungendo rumore è facile e non richiede di imparare nulla; si addestra una rete a <b>prevedere il rumore</b> aggiunto a un passo a caso, e poi la si usa al contrario, partendo da rumore puro, per costruire un'immagine nuova passo dopo passo.</p></div>
"""), sec=("l27-intro", "Introduzione", "slide 1–6"), printed=P(1))

s(2, "The Diffusion Process", R("""
<p>La citazione è la prima frase dell'articolo di <b>Song et al. (2021)</b> sulle equazioni differenziali stocastiche: creare rumore dai dati è facile, creare dati dal rumore è modellazione generativa.</p>
<p>La figura mostra due equazioni differenziali stocastiche (SDE):</p>
<ul>
<li><b>SDE in avanti</b> (dati → rumore): dx = f(x, t) dt + g(t) dw. Il termine f(x, t) dt è uno spostamento deterministico (nei modelli che vediamo restringe un poco l'immagine verso zero), g(t) dw aggiunge rumore browniano. Le facce si sciolgono in rumore da sinistra a destra.</li>
<li><b>SDE inversa</b> (rumore → dati): dx = [f(x, t) − g(t)<sup>2</sup> ∇<sub>x</sub> log p<sub>t</sub>(x)] dt + g(t) dw̄. È lo stesso processo percorso all'indietro nel tempo; l'unica cosa che non conosciamo è il termine in verde, lo <b>score</b> ∇<sub>x</sub> log p<sub>t</sub>(x), il gradiente del logaritmo della densità dei dati rumorosi.</li>
</ul>
<p>Il messaggio: se impariamo lo score a ogni livello di rumore, possiamo far girare il film al contrario. Nella slide 15 vedrai che <b>prevedere il rumore e prevedere lo score sono la stessa cosa</b> a meno di un fattore.</p>
<p>Per l'esame non serve saper risolvere le SDE: basta capire che DDPM (slide 10–14) è la versione a passi discreti di questo quadro.</p>
"""), printed=P(2))

s(3, "Lecture Outline", R("""
<p>Tre parti:</p>
<ol>
<li><b>Fundamentals of Diffusion Models</b>: GAN contro diffusione, DDPM (processo in avanti, schedule, processo inverso, loss, addestramento e campionamento), score, U-Net con passo e testo, classifier-free guidance, DDIM, target ε/x<sub>0</sub>/v, flow matching, distillazione, metriche. Slide 7–28.</li>
<li><b>Diffusion Model Architectures</b>: latent diffusion e Stable Diffusion, SDXL, KOALA, DiT, SANA, SD3, FLUX, encoder di testo. Slide 29–44.</li>
<li><b>Extending Diffusion to Video</b>: strati temporali, attenzione spaziale e temporale, Stable Video Diffusion, video DiT, Wan, CogVideoX, Movie Gen, modelli proprietari. Slide 45–55.</li>
</ol>
"""), printed=P(3))

s(4, "Building Blocks of Diffusion Models", R("""
<p>La slide mette in fila i pezzi che conosci già e che ritornano oggi:</p>
<ul>
<li><b>CLIP</b> (<a href="#L24">L24</a>): l'allineamento testo-immagine. Qui serve il suo <b>encoder di testo</b>, che trasforma il prompt in vettori.</li>
<li><b>U-Net</b> (<a href="#L17">L17</a>): encoder-decoder con skip connection, nata per la segmentazione. Qui diventa la <b>rete che toglie il rumore</b> (denoiser): immagine rumorosa in ingresso, rumore previsto in uscita, stessa risoluzione.</li>
<li><b>ViT</b> (<a href="#L17">L17</a>–<a href="#L18">L18</a>): l'immagine in patch e un transformer. Qui diventa il <b>Diffusion Transformer (DiT)</b>, che sostituisce la U-Net nei modelli recenti.</li>
<li><b>PEFT</b> (<a href="#L25">L25</a>): LoRA e simili servono ad adattare un modello di diffusione preaddestrato; sarà il tema della prossima lezione (generazione personalizzata).</li>
</ul>
"""), printed=P(4))

s(5, "FLUX.2: esempi ufficiali", R("""
<p>Pagina di sole immagini: campioni ufficiali di <b>FLUX.2</b> (Black Forest Labs, 2025). Fotorealismo (l'ape, la coccinella), stili diversi (illustrazione vintage, poster in bianco e nero), e <b>testo leggibile</b> dentro l'immagine («Hello FLUX.2» sul monitor, la scritta del poster).</p>
<p>Il testo scritto bene è un indizio di cui si parla alla slide 43: i modelli con un vero modello linguistico come encoder (FLUX.2 usa Mistral Small 3) disegnano le scritte molto meglio di quelli che usano solo CLIP.</p>
"""), printed='')

s(6, "Sora: esempio di video", R("""
<p>Un fotogramma di un video generato da <b>Sora</b> (OpenAI, 2024): una donna cammina in una strada di Tokyo di notte, con riflessi sul bagnato e insegne. Nel PDF c'è il link «Watch video».</p>
<p>Il punto: lo stesso principio (togliere rumore passo per passo) funziona anche per i video, dove bisogna generare insieme l'aspetto di ogni fotogramma e il <b>movimento coerente</b> nel tempo. È la terza parte della lezione (slide 45–55).</p>
"""), printed='')

# ===================== FONDAMENTI =====================

s(7, "Fundamentals of Diffusion Models", R("""<p>Divisoria della prima parte: imparare a generare imparando a togliere il rumore.</p>"""),
  kind='div', sec=("l27-fond", "Parte 1 · Fondamenti: DDPM, guida, campionatori, flow matching", "slide 7–28"), printed='')

s(8, "Why Diffusion Instead of GANs?", R("""
<p>Una <b>GAN</b> (Goodfellow et al., 2014) addestra insieme due reti: un <b>generatore</b> G che trasforma rumore z in immagini, e un <b>discriminatore</b> D che cerca di distinguere immagini vere da generate. È un gioco min-max: G vuole ingannare D.</p>
<p>La figura è quella dell'articolo originale. Le linee in basso mostrano come G mappa i punti z sull'asse x. Puntini neri = p<sub>data</sub>, curva verde = p<sub>g</sub> (distribuzione generata), tratteggio blu = uscita di D.</p>
<ul>
<li><b>Sinistra</b>: p<sub>g</sub> è diversa da p<sub>data</sub> e D le separa.</li>
<li><b>Destra</b>, all'equilibrio: p<sub>g</sub> = p<sub>data</sub> e D(x) = 0,5 ovunque: non sa più distinguere.</li>
</ul>
<p>Problemi delle GAN: addestramento <b>instabile</b> e <b>mode collapse</b> (il generatore produce sempre le stesse poche immagini e ignora parti della distribuzione). La diffusione usa una semplice loss di regressione sul rumore, senza avversario: si addestra in modo stabile e copre tutta la distribuzione.</p>
<p>Il prezzo: una GAN genera con <b>un solo passaggio</b> nella rete, la diffusione con <b>molti passi</b> di denoising (decine o centinaia).</p>
<div class="box b"><b>Dal libro · {C32}, § 32.9 Generative Adversarial Networks</b><p>Il libro scrive l'obiettivo min-max (eq. 32.6) e lo legge da due lati: per G fissato, D fa una regressione logistica fra dati veri e sintetici; per D ottimo, G minimizza la probabilità di essere scoperto. Si alternano un passo su G e K passi su D (spesso K = 1 basta). L'analogia del libro: D è un insegnante di pittura che indica gli errori dello studente. Prince, cap. 15, § 15.1.4, chiama il collasso a pochi punti <i>mode collapse</i>.</p></div>
"""), printed=P(8))

s(9, "The Generative Modeling Problem", R("""
<p>Il problema generativo: dati dei campioni da una distribuzione sconosciuta p<sub>data</sub>(x), imparare un modello p<sub>θ</sub>(x) da cui estrarre <b>immagini nuove</b> che sembrano vere.</p>
<ul>
<li>Le <b>GAN</b> imparano con il gioco avversario.</li>
<li>I <b>VAE</b> massimizzano un limite inferiore variazionale (ELBO) della log-verosimiglianza.</li>
<li>I <b>modelli di diffusione</b> si ispirano alla termodinamica (Sohl-Dickstein et al., 2015): aggiungono gradualmente rumore ai dati e imparano a invertire questo processo.</li>
</ul>
<p>La generazione parte da rumore gaussiano e applica una catena di passi di denoising imparati:</p>
<span class="f">x<sub>T</sub> ∼ 𝒩(0, I),   x<sub>T</sub> → x<sub>T−1</sub> → … → x<sub>0</sub></span>
<p>x<sub>T</sub> è rumore puro della stessa forma dell'immagine (per esempio 3 × 256 × 256 numeri indipendenti), x<sub>0</sub> è l'immagine finale.</p>
<div class="box b"><b>Dal libro · {C32}, § 32.3 e § 32.8</b><p>Il libro distingue l'approccio <b>diretto</b> (imparare una funzione rumore → immagine, come GAN e diffusione) da quello indiretto (imparare una densità o un'energia e poi cercare campioni che la massimizzano). Ricorda anche un requisito spesso dimenticato: un buon generatore non deve <b>memorizzare</b> il training set, deve generalizzare. Nel § 32.8 presenta la diffusione come parente degli autoregressivi: anche lì un problema difficile viene spezzato in tanti passi facili.</p></div>
"""), printed=P(9))

s(10, "DDPM: Forward Diffusion", R("""
<p><b>DDPM</b> (Denoising Diffusion Probabilistic Models, Ho et al., 2020) definisce un <b>processo in avanti</b> fisso: una catena di Markov che aggiunge un po' di rumore gaussiano a ogni passo. Partendo da un'immagine pulita x<sub>0</sub> ∼ q(x<sub>0</sub>), x<sub>t</sub> è l'immagine rumorosa al passo t:</p>
<span class="f">q(x<sub>t</sub> | x<sub>t−1</sub>) = 𝒩(x<sub>t</sub>; √(1 − β<sub>t</sub>) x<sub>t−1</sub>, β<sub>t</sub> I)</span>
<p>In parole: x<sub>t</sub> = √(1 − β<sub>t</sub>) x<sub>t−1</sub> + √β<sub>t</sub> ε<sub>t</sub>. Si <b>rimpicciolisce</b> un po' l'immagine (fattore √(1 − β<sub>t</sub>) &lt; 1) e si aggiunge rumore di varianza β<sub>t</sub> ∈ (0, 1). Il restringimento serve a tenere la varianza totale vicina a 1, così il processo non esplode.</p>
<p>Con α<sub>t</sub> = 1 − β<sub>t</sub> e ᾱ<sub>t</sub> = ∏<sub>s=1</sub><sup>t</sup> α<sub>s</sub> si può saltare direttamente da x<sub>0</sub> a qualunque x<sub>t</sub>:</p>
<span class="f">x<sub>t</sub> = √ᾱ<sub>t</sub> x<sub>0</sub> + √(1 − ᾱ<sub>t</sub>) ε,   ε ∼ 𝒩(0, I)</span>
<ul>
<li>Il processo in avanti <b>non ha parametri da addestrare</b>.</li>
<li>Se ᾱ<sub>T</sub> ≈ 0, x<sub>T</sub> è praticamente rumore gaussiano puro.</li>
<li>Per addestrare <b>non serve calcolare gli stati intermedi</b> x<sub>1</sub>, …, x<sub>t−1</sub>: si genera x<sub>t</sub> in un colpo solo.</li>
</ul>
<div class="box k"><b>Da saper fare: la formula chiusa con due passi</b><p>x<sub>1</sub> = √α<sub>1</sub> x<sub>0</sub> + √(1 − α<sub>1</sub>) ε<sub>1</sub>, x<sub>2</sub> = √α<sub>2</sub> x<sub>1</sub> + √(1 − α<sub>2</sub>) ε<sub>2</sub>. Sostituendo: x<sub>2</sub> = √(α<sub>2</sub>α<sub>1</sub>) x<sub>0</sub> + √(α<sub>2</sub>(1 − α<sub>1</sub>)) ε<sub>1</sub> + √(1 − α<sub>2</sub>) ε<sub>2</sub>. Due gaussiane indipendenti a media zero si sommano in una gaussiana con varianza somma: α<sub>2</sub> − α<sub>2</sub>α<sub>1</sub> + 1 − α<sub>2</sub> = 1 − α<sub>1</sub>α<sub>2</sub>. Quindi x<sub>2</sub> = √ᾱ<sub>2</sub> x<sub>0</sub> + √(1 − ᾱ<sub>2</sub>) ε. Per induzione vale per ogni t.</p></div>
<div class="box b"><b>Dal libro · Prince, cap. 18, § 18.2 e 18.2.1 Diffusion kernel</b><p>Prince fa esattamente questa derivazione (eq. 18.4–18.7) e chiama q(x<sub>t</sub> | x<sub>0</sub>) il <b>diffusion kernel</b>. Attenzione alla notazione: Prince chiama z<sub>t</sub> le immagini rumorose, x l'immagine pulita, e scrive <b>α<sub>t</sub> per il prodotto cumulato</b> (le slide lo chiamano ᾱ<sub>t</sub>). Il visionbook (§ 32.8) scrive lo stesso passo x<sub>t</sub> = √(1 − β<sub>t</sub>) x<sub>t−1</sub> + √β<sub>t</sub> ε<sub>t</sub> e dice che per T grande x<sub>T</sub> tende a 𝒩(0, I).</p></div>
"""), printed=P(10))

s(11, "Noise Schedules: How Fast Is Information Destroyed?", R("""
<p>La successione β<sub>1</sub>, …, β<sub>T</sub> si chiama <b>noise schedule</b> e decide quanto in fretta l'informazione viene distrutta. Il grafico mostra ᾱ<sub>t</sub> (quanto segnale resta) per T = 1000:</p>
<ul>
<li><b>Schedule lineare</b> (DDPM: β cresce linearmente da 10<sup>−4</sup> a 0,02, curva blu): ᾱ vale 0,52 a t = 250, 0,08 a t = 500, 0,003 a t = 750. Il gatto è già irriconoscibile a metà: gli ultimi centinaia di passi sono quasi tutti rumore, quindi <b>passi sprecati</b>.</li>
<li><b>Schedule a coseno</b> (Nichol e Dhariwal, 2021, curva arancione): ᾱ cala più lentamente, 0,85, 0,49, 0,14 agli stessi passi. Il segnale si distrugge in modo più uniforme.</li>
</ul>
<p>Il rapporto segnale-rumore è</p>
<span class="f">SNR(t) = ᾱ<sub>t</sub> / (1 − ᾱ<sub>t</sub>)</span>
<p>cioè varianza del segnale diviso varianza del rumore in x<sub>t</sub>. Con lo schedule lineare l'SNR scende sotto 1 intorno a t ≈ 260, con il coseno intorno a t ≈ 500 (conti nostri, figura della dispensa).</p>
<p>Ultimo punto: Stable Diffusion 3 applica la stessa idea al training, <b>campionando più spesso i passi a rumore intermedio</b>, dove la previsione è più difficile e utile.</p>
<div class="box k"><b>Da saper fare</b><p>Leggere i valori di ᾱ sotto le immagini e dire a che SNR corrispondono: ᾱ = 0,52 → SNR ≈ 1,08 (segnale e rumore pari); ᾱ = 0,08 → SNR ≈ 0,087.</p></div>
"""), printed=P(11))

s(12, "DDPM: Reverse Diffusion (Learning to Denoise)", R("""
<p>La catena in alto: da x<sub>T</sub> (rumore) a x<sub>0</sub> (la faccia). La freccia tratteggiata all'indietro è q(x<sub>t</sub> | x<sub>t−1</sub>), il passo in avanti <b>fisso</b>; la freccia piena in avanti è p<sub>θ</sub>(x<sub>t−1</sub> | x<sub>t</sub>), il passo inverso <b>imparato</b>.</p>
<span class="f">p<sub>θ</sub>(x<sub>t−1</sub> | x<sub>t</sub>) = 𝒩(x<sub>t−1</sub>; μ<sub>θ</sub>(x<sub>t</sub>, t), Σ<sub>θ</sub>(x<sub>t</sub>, t))</span>
<ul>
<li>La <b>media</b> μ<sub>θ</sub> è data da una rete neurale; la varianza Σ<sub>θ</sub> può essere fissa (DDPM) o imparata (Improved DDPM).</li>
<li>Perché una gaussiana basta? Se β<sub>t</sub> è piccolo, anche il vero passo inverso è <b>quasi gaussiano</b>. Per questo servono tanti passi piccoli.</li>
<li>Si campiona partendo da x<sub>T</sub> ∼ 𝒩(0, I) e generando x<sub>t−1</sub> da x<sub>t</sub> un passo alla volta.</li>
<li>La stessa rete serve per tutti i passi, condizionata su t.</li>
</ul>
<p>L'ultima riga è il punto chiave: il <b>posteriore</b> q(x<sub>t−1</sub> | x<sub>t</sub>, x<sub>0</sub>) è calcolabile in forma chiusa durante il training, perché lì x<sub>0</sub> lo conosciamo. Durante la generazione invece x<sub>0</sub> è proprio ciò che non abbiamo: la rete deve stimarlo.</p>
<div class="box b"><b>Dal libro · Prince, cap. 18, § 18.2.3–18.3</b><p>Prince mostra su un esempio in 1D (fig. 18.5) che il vero passo inverso q(x<sub>t−1</sub> | x<sub>t</sub>) senza conoscere x<sub>0</sub> è in generale una distribuzione complicata, anche multimodale, ma spesso ben approssimata da una gaussiana; condizionando anche su x<sub>0</sub> (fig. 18.6) diventa esattamente gaussiano, con media data dall'eq. 18.15. Il decoder (§ 18.3) usa gaussiane con varianze σ<sub>t</sub><sup>2</sup> fissate e si campiona per <i>ancestral sampling</i>.</p></div>
"""), printed=P(12))

s(13, "DDPM: Training Objective", R("""
<p>Due distribuzioni a confronto:</p>
<ul>
<li>q(x<sub>t−1</sub> | x<sub>t</sub>, x<sub>0</sub>): il <b>posteriore del processo in avanti</b>, una gaussiana nota in forma chiusa;</li>
<li>p<sub>θ</sub>(x<sub>t−1</sub> | x<sub>t</sub>): il processo inverso <b>imparato</b>.</li>
</ul>
<p>DDPM si ricava massimizzando un <b>limite inferiore variazionale</b> (ELBO, come nei VAE) di log p<sub>θ</sub>(x<sub>0</sub>). Il limite si scompone in termini KL fra queste due gaussiane, uno per passo; fra gaussiane con la stessa varianza il KL è una distanza quadratica fra le medie.</p>
<p>La rete non prevede direttamente la media: prevede il <b>rumore aggiunto</b> ε<sub>θ</sub>(x<sub>t</sub>, t), da cui la media si ricava così:</p>
<span class="f">μ<sub>θ</sub>(x<sub>t</sub>, t) = (1/√α<sub>t</sub>) (x<sub>t</sub> − β<sub>t</sub>/√(1 − ᾱ<sub>t</sub>) · ε<sub>θ</sub>(x<sub>t</sub>, t))</span>
<p>Ho et al. buttano via i pesi che dipendono da t e usano la loss semplice</p>
<span class="f">ℒ<sub>simple</sub> = 𝔼<sub>x<sub>0</sub>, t, ε</sub> ‖ε − ε<sub>θ</sub>(x<sub>t</sub>, t)‖<sub>2</sub><sup>2</sup></span>
<p>È una regressione: «indovina il rumore che ho aggiunto». Nessun avversario, nessun campionamento durante il training.</p>
<div class="box b"><b>Dal libro · Prince, cap. 18, § 18.4–18.5</b><p>Prince fa tutta la derivazione: ELBO (§ 18.4.1–18.4.3), loss come somma di errori quadratici fra la media prevista e la media del posteriore (eq. 18.29), poi due riparametrizzazioni (§ 18.5.1–18.5.2): si scrive x<sub>0</sub> in funzione di x<sub>t</sub> e del rumore, e si fa prevedere alla rete il rumore. Ne esce l'eq. 18.39 con un peso per passo, e ignorando i pesi l'eq. 18.40, che è ℒ<sub>simple</sub>.</p></div>
<div class="box k"><b>Da saper fare: da dove viene μ<sub>θ</sub></b><p>Dalla formula chiusa x<sub>0</sub> = (x<sub>t</sub> − √(1 − ᾱ<sub>t</sub>) ε)/√ᾱ<sub>t</sub>. Sostituendo questa x<sub>0</sub> nella media del posteriore e semplificando, i termini in x<sub>0</sub> spariscono e resta la formula della slide con ε al posto di ε<sub>θ</sub>. Il messaggio: <b>sapere il rumore equivale a sapere la media del passo inverso</b>.</p></div>
"""), printed=P(13))

s(14, "DDPM: Training and Sampling", R("""
<p>I due algoritmi affiancati.</p>
<p><b>Addestramento</b> (si ripete finché converge):</p>
<ol>
<li>prendi un'immagine x<sub>0</sub> dal dataset;</li>
<li>scegli un passo a caso t ∼ 𝒰{1, …, T} (quanto rumore);</li>
<li>estrai rumore ε ∼ 𝒩(0, I) della stessa forma dell'immagine;</li>
<li>costruisci in un colpo x<sub>t</sub> = √ᾱ<sub>t</sub> x<sub>0</sub> + √(1 − ᾱ<sub>t</sub>) ε;</li>
<li>passo di gradiente su ‖ε − ε<sub>θ</sub>(x<sub>t</sub>, t)‖<sup>2</sup>.</li>
</ol>
<p><b>Campionamento</b>:</p>
<ol>
<li>parti da rumore puro x<sub>T</sub> ∼ 𝒩(0, I);</li>
<li>per t = T, …, 1: prevedi il rumore ε<sub>θ</sub>(x<sub>t</sub>, t), toglilo per ottenere la media μ<sub>θ</sub>(x<sub>t</sub>, t), poi aggiungi un po' di rumore fresco: x<sub>t−1</sub> = μ<sub>θ</sub>(x<sub>t</sub>, t) + σ<sub>t</sub> z, con z ∼ 𝒩(0, I) se t &gt; 1 e z = 0 all'ultimo passo; σ<sub>t</sub><sup>2</sup> = β<sub>t</sub>;</li>
<li>restituisci x<sub>0</sub>.</li>
</ol>
<p>Asimmetria importante: il training usa <b>un passo a caso</b> per immagine (costa una sola valutazione della rete), il campionamento ne richiede <b>T in sequenza</b>.</p>
<div class="box x"><b>Approfondimento: perché si riaggiunge rumore</b><p>Sembra assurdo togliere rumore e poi rimetterne. Ma la media μ<sub>θ</sub> è una media: se si seguissero solo le medie si otterrebbero immagini sfocate, una specie di «media di tutte le immagini possibili». Il rumore fresco mantiene il campionamento stocastico e fa arrivare su campioni nitidi e diversi. Per σ<sub>t</sub> Ho et al. provano due scelte equivalenti in pratica: σ<sub>t</sub><sup>2</sup> = β<sub>t</sub> (quella della slide) e la varianza del posteriore β̃<sub>t</sub> = β<sub>t</sub>(1 − ᾱ<sub>t−1</sub>)/(1 − ᾱ<sub>t</sub>).</p></div>
<div class="box b"><b>Dal libro · Prince, § 18.6, algoritmi 18.1 e 18.2</b><p>Sono gli stessi due algoritmi, con la notazione z<sub>t</sub>. Prince sottolinea due vantaggi del training (semplice, e ogni immagine viene riusata con rumori diversi, quindi è una forma di data augmentation) e il difetto del campionamento: richiede di eseguire la rete in serie tante volte.</p></div>
"""), printed=P(14))

s(15, "Denoising = Estimating the Score", R("""
<p>Lo <b>score</b> della distribuzione dei dati rumorosi è il gradiente ∇<sub>x<sub>t</sub></sub> log q(x<sub>t</sub>): un vettore che, in ogni punto, punta verso le zone dove la densità è più alta. Vale</p>
<span class="f">∇<sub>x<sub>t</sub></sub> log q(x<sub>t</sub>) ≈ − ε<sub>θ</sub>(x<sub>t</sub>, t) / √(1 − ᾱ<sub>t</sub>)</span>
<ul>
<li>Prevedere il rumore ⇔ prevedere la direzione che lo toglie: lo score è il rumore cambiato di segno e riscalato.</li>
<li>È proprio il termine verde della SDE inversa della slide 2.</li>
<li>Con un condizionamento c (il prompt) la regola di Bayes dà ∇ log q(x<sub>t</sub> | c) = ∇ log q(x<sub>t</sub>) + ∇ log q(c | x<sub>t</sub>): score incondizionato più un termine «classificatore».</li>
</ul>
<div class="box k"><b>Da saper fare: da dove viene la formula</b><p>Per una sola immagine nota, q(x<sub>t</sub> | x<sub>0</sub>) = 𝒩(√ᾱ<sub>t</sub> x<sub>0</sub>, (1 − ᾱ<sub>t</sub>) I). Il gradiente del logaritmo di una gaussiana è −(x<sub>t</sub> − media)/varianza = −√(1 − ᾱ<sub>t</sub>) ε/(1 − ᾱ<sub>t</sub>) = −ε/√(1 − ᾱ<sub>t</sub>). La rete addestrata con ℒ<sub>simple</sub> stima la media di ε dato x<sub>t</sub>, e da qui lo score della distribuzione marginale (risultato del <i>denoising score matching</i>).</p></div>
<div class="box w"><b>Precisazione: Bayes e la classifier-free guidance</b><p>La scomposizione di Bayes è letteralmente la base della <b>classifier guidance</b> (Dhariwal e Nichol, 2021), che usa un classificatore vero addestrato sulle immagini rumorose per stimare ∇ log q(c | x<sub>t</sub>). La classifier-free guidance (slide 21) parte dalla stessa formula ma non ha classificatore: ricava il termine come differenza fra la previsione condizionata e quella incondizionata dello stesso modello. È questo il senso di «spiega la CFG».</p></div>
<div class="box b"><b>Dal libro · Prince, § 18.6.3 Conditional generation</b><p>Prince presenta prima la classifier guidance: si aggiunge al passo di campionamento σ<sub>t</sub><sup>2</sup> ∂ log Pr(c | z<sub>t</sub>)/∂z<sub>t</sub> (eq. 18.41), il gradiente di un classificatore che lavora sulle immagini rumorose; poi la classifier-free guidance, che evita il classificatore separato.</p></div>
"""), printed=P(15))

s(16, "Denoising U-Net", R("""
<p>DDPM specifica il processo, la loss e il campionamento; il <b>denoiser</b> può essere una U-Net o un transformer. Confronto con la U-Net per segmentazione della <a href="#L17">L17</a>:</p>
<table>
<tr><th></th><th>U-Net per segmentazione</th><th>U-Net per diffusione</th></tr>
<tr><td>Ingresso</td><td>immagine x</td><td>immagine rumorosa x<sub>t</sub></td></tr>
<tr><td>Condizionamento</td><td>di solito nessuno</td><td>passo t, eventuale testo c</td></tr>
<tr><td>Uscita</td><td>punteggi di classe per pixel</td><td>rumore previsto ε<sub>θ</sub>(x<sub>t</sub>, t, c)</td></tr>
<tr><td>Architettura</td><td>encoder, decoder, skip</td><td>blocchi multi-risoluzione, skip, blocchi residui e attenzione</td></tr>
</table>
<ul>
<li>Gli embedding del passo condizionano i blocchi di denoising (slide 17).</li>
<li>Il testo entra con la cross-attention (slide 19–20).</li>
<li>La rete è <b>condivisa fra tutti i passi</b>: una sola U-Net, non T reti.</li>
</ul>
<div class="box b"><b>Dal libro · Prince, § 18.6.1 e fig. 18.9</b><p>Prince descrive la U-Net per la diffusione: l'encoder riduce la risoluzione e aumenta i canali, il decoder fa il contrario, le rappresentazioni dell'encoder sono concatenate a quelle del decoder; fra un livello e l'altro blocchi residui e periodicamente una self-attention globale. Addestrare T U-Net diverse sarebbe inefficiente, quindi se ne usa una sola che riceve il passo come ingresso.</p></div>
"""), printed=P(16))

s(17, "Timestep Conditioning in the Denoising U-Net", R("""
<p>La U-Net riceve x<sub>t</sub> e deve prevedere il rumore. Siccome è la <b>stessa rete per tutti i t</b>, deve sapere <b>quanto rumore c'è</b>: a t piccolo deve togliere un velo sottile, a t grande deve quasi inventare l'immagine.</p>
<p>Il passo si codifica con una codifica posizionale sinusoidale (come i token del transformer, <a href="#L17">L17</a>) seguita da un piccolo MLP:</p>
<span class="f">e<sub>t</sub> = MLP(PE(t))</span>
<p>L'embedding entra nei blocchi residui. Per una feature map h ∈ ℝ<sup>B×C×H×W</sup> (batch, canali, altezza, larghezza):</p>
<span class="f">h̃ = h + P(e<sub>t</sub>)</span>
<p>dove P è una proiezione lineare a C numeri, uno per canale, sommati a <b>ogni posizione spaziale</b> (broadcast su H e W). In alternativa e<sub>t</sub> può predire una scala e uno spostamento per la normalizzazione delle feature (h̃ = γ(e<sub>t</sub>) · norm(h) + β(e<sub>t</sub>)), che è l'idea dell'adaLN dei DiT (slide 37).</p>
<div class="box b"><b>Dal libro · {C32}, § 32.8</b><p>Il libro spiega bene <b>perché</b> serve t: guardando un'immagine molto granulosa la rete non sa se è una scena normale coperta di rumore (probabile per t grande) o una scena davvero piena di texture caotiche (probabile per t piccolo). Dare t alla rete toglie l'ambiguità.</p></div>
"""), printed=P(17))

s(18, "CLIP in Text-to-Image Generation", R("""
<p>CLIP (<a href="#L24">L24</a>) impara rappresentazioni di immagini e testi con il pretraining contrastivo su coppie immagine-didascalia. Per generare serve soprattutto l'<b>encoder di testo</b>:</p>
<ul>
<li>trasforma il prompt in una <b>sequenza</b> di feature, una per token (non un vettore solo);</li>
<li>Stable Diffusion v1 usa l'encoder di testo di CLIP ViT-L/14: M = 77 token, d = 768 numeri ciascuno;</li>
<li>SDXL usa due encoder di testo: CLIP ViT-L e OpenCLIP ViT-bigG;</li>
<li>la <b>cross-attention</b> permette alla rete di denoising di guardare i singoli token del testo.</li>
</ul>
<p>Perché la sequenza e non il solo embedding globale? Perché pixel diversi devono guardare parole diverse: la zona del gatto guarda «gatto», lo sfondo guarda «spiaggia».</p>
<div class="box b"><b>Dal libro · {C51}, § 51.4 e fig. 51.10</b><p>Il libro descrive un modello testo-immagine a diffusione come quello di Rombach et al.: gli embedding del testo vengono inseriti in ogni U-Net di denoising, anche in più strati, così ogni decisione della rete può dipendere dal testo. Nota poi che un modello di diffusione condizionato assomiglia a un VAE condizionato: entrambi prendono testo e rumore gaussiano, ma il VAE produce l'immagine con un passaggio solo, la diffusione con una catena di passi.</p></div>
"""), printed=P(18))

s(19, "Text Conditioning in the Denoising U-Net", R("""
<p>La figura (da Rombach et al., adattata) mostra il prompt «orange cat» trasformato da un encoder di testo τ<sub>θ</sub> (qui disegnato come LLM) in una sequenza di embedding; frecce azzurre portano questi embedding a <b>tutti i livelli</b> della U-Net, in discesa e in salita.</p>
<ul>
<li>L'encoder mappa il prompt y nei token C = τ(y).</li>
<li>Blocchi di cross-attention sono inseriti a <b>risoluzioni diverse</b> della U-Net.</li>
<li>Le <b>query</b> vengono dalle feature della U-Net, <b>chiavi e valori</b> dagli embedding del testo.</li>
<li>Le stesse feature di testo condizionano più blocchi e tutti i passi: il testo si codifica <b>una volta sola</b> per immagine.</li>
</ul>
"""), printed=P(19))

s(20, "Text Conditioning Through Cross-Attention", R("""
<p>Z ∈ ℝ<sup>N×d</sup> sono i token dell'immagine latente (N posizioni spaziali, per esempio 64 × 64 = 4096), C ∈ ℝ<sup>M×d<sub>c</sub></sup> le feature del testo (M = 77):</p>
<span class="f">Q = ZW<sub>Q</sub>,  K = CW<sub>K</sub>,  V = CW<sub>V</sub></span>
<span class="f">CrossAttn(Z, C) = softmax(QK<sup>⊤</sup> / √d<sub>k</sub>) V</span>
<ul>
<li>Q dalle feature spaziali dell'immagine, K e V dall'encoder di testo.</li>
<li>La matrice di attenzione è <b>N × M</b>: posizioni dell'immagine × token del testo. La riga i dice quanto il pixel i guarda ciascuna parola.</li>
<li>Lo stesso condizionamento si usa a tutte le risoluzioni della U-Net.</li>
</ul>
<p>È la stessa attenzione della <a href="#L17">L17</a>, con una differenza sola rispetto alla self-attention: query e chiavi vengono da due insiemi diversi. L'uscita ha N righe, una per posizione dell'immagine: il testo «entra» nelle feature dell'immagine.</p>
<div class="box b"><b>Dal libro · {C26}, § 26.6 e {C51}, § 51.4.2</b><p>Il cap. 26 introduce query, chiavi e valori come proiezioni lineari dei token. Il § 51.4.2 usa la cross-attention per il captioning (testo che guarda l'immagine); qui la direzione è opposta: l'immagine guarda il testo.</p></div>
"""), printed=P(20))

s(21, "Classifier-Free Guidance", R("""
<p>Problema: un modello condizionato sul testo tende a seguirlo «poco», generando immagini plausibili ma solo vagamente legate al prompt. La <b>classifier-free guidance</b> (CFG, Ho e Salimans, 2022) amplifica l'effetto del testo.</p>
<p><b>Training</b>: il prompt viene <b>tolto a caso</b> (sostituito dal prompt vuoto ∅, tipicamente nel 10–20% dei casi). La stessa rete impara a prevedere il rumore sia con il testo sia senza.</p>
<p><b>Campionamento</b>: a ogni passo si esegue la rete due volte, ε<sub>θ</sub>(x<sub>t</sub>, t, c) con il prompt e ε<sub>θ</sub>(x<sub>t</sub>, t, ∅) senza, e si estrapola:</p>
<span class="f">ε̂<sub>θ</sub>(x<sub>t</sub>, t, c) = ε<sub>θ</sub>(x<sub>t</sub>, t, ∅) + w [ε<sub>θ</sub>(x<sub>t</sub>, t, c) − ε<sub>θ</sub>(x<sub>t</sub>, t, ∅)]</span>
<ul>
<li>w = 0: si ignora il prompt; w = 1: previsione condizionata normale.</li>
<li>w &gt; 1: si va oltre, nella direzione «che cosa cambia aggiungendo il testo». Valori tipici per Stable Diffusion 7–8.</li>
<li>w grande migliora l'aderenza al prompt ma può ridurre la diversità e introdurre artefatti (colori saturi, immagini «bruciate»).</li>
<li>Costo: <b>due valutazioni della rete per passo</b> (si possono mettere nello stesso batch).</li>
</ul>
<div class="box k"><b>Da saper fare: perché funziona</b><p>Moltiplica per −1/√(1 − ᾱ<sub>t</sub>) e passa agli score: la differenza ε(c) − ε(∅) è proporzionale a ∇ log q(x<sub>t</sub> | c) − ∇ log q(x<sub>t</sub>) = ∇ log q(c | x<sub>t</sub>) (slide 15). La CFG campiona quindi con score ∇ log q(x<sub>t</sub>) + w ∇ log q(c | x<sub>t</sub>), cioè da una distribuzione proporzionale a q(x<sub>t</sub>) q(c | x<sub>t</sub>)<sup>w</sup>: per w &gt; 1 un «classificatore implicito» elevato a potenza spinge verso le immagini in cui il prompt è molto probabile.</p></div>
<div class="box x"><b>Approfondimento: attenzione alla convenzione su w</b><p>Nell'articolo di Ho e Salimans la formula è scritta (1 + w) ε(c) − w ε(∅), quindi lì w = 0 vuol dire «solo condizionato» e la «scala di guida» della slide corrisponde al loro 1 + w. La convenzione della slide è quella di Stable Diffusion e delle librerie (guidance_scale). Non è un errore, ma se leggi l'articolo i numeri sono spostati di 1.</p></div>
<div class="box b"><b>Dal libro · Prince, § 18.6.3</b><p>Prince descrive la CFG come addestramento congiunto condizionato e non condizionato, togliendo l'informazione di classe a caso, e nota il «vantaggio sorprendente»: sovrappesando il condizionamento si ottengono esempi di qualità molto alta ma un po' stereotipati, come il trucco della troncatura nelle GAN.</p></div>
"""), printed=P(21))

s(22, "DDIM: Fewer Sampling Steps", R("""
<p><b>DDIM</b> (Denoising Diffusion Implicit Models, Song, Meng ed Ermon, 2021) usa <b>lo stesso predittore di rumore già addestrato</b> di DDPM, ma un campionamento diverso. Prima si stima l'immagine pulita:</p>
<span class="f">x̂<sub>0</sub>(x<sub>t</sub>) = (x<sub>t</sub> − √(1 − ᾱ<sub>t</sub>) ε<sub>θ</sub>(x<sub>t</sub>, t)) / √ᾱ<sub>t</sub></span>
<p>(è la formula chiusa invertita). Poi si salta da t a un passo precedente qualunque s &lt; t:</p>
<span class="f">x<sub>s</sub> = √ᾱ<sub>s</sub> x̂<sub>0</sub>(x<sub>t</sub>) + √(1 − ᾱ<sub>s</sub> − σ<sub>t→s</sub><sup>2</sup>) ε<sub>θ</sub>(x<sub>t</sub>, t) + σ<sub>t→s</sub> z</span>
<p>In parole: si ricostruisce x<sub>s</sub> come se il rumore da rimettere fosse quello appena stimato. Con σ<sub>t→s</sub> = 0 (<b>DDIM deterministico</b>) non si aggiunge rumore nuovo: ogni rumore iniziale x<sub>T</sub> porta sempre alla stessa immagine.</p>
<ul>
<li>Si usa una <b>sottosequenza</b> dei passi (per esempio 50 su 1000): molte meno valutazioni della rete.</li>
<li>Stesso modello, procedura di campionamento diversa: nessun riaddestramento.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Verificare che con un solo passo da t = T a s = 0 (ᾱ<sub>0</sub> = 1) DDIM restituisce direttamente x̂<sub>0</sub>: il termine con ε ha coefficiente √(1 − 1) = 0. Per questo con pochissimi passi l'immagine è sfocata: x̂<sub>0</sub> a rumore massimo è la «media» delle immagini compatibili.</p></div>
<div class="box b"><b>Dal libro · Prince, § 18.6.2 e fig. 18.10</b><p>La loss di DDPM dipende solo dal diffusion kernel q(z<sub>t</sub> | x), quindi è valida per un'intera <b>famiglia</b> di processi in avanti, compatibili con lo stesso modello addestrato ma con regole diverse per andare all'indietro. Fra questi DDIM, non più stocastico, e i modelli accelerati che saltano passi; Prince cita 50 passi come sufficienti nel caso deterministico. Nelle note aggiunge che DDIM equivale a un'equazione differenziale ordinaria con traiettorie poco curve, risolvibile con metodi numerici efficienti.</p></div>
"""), printed=P(22))

s(23, "Predicting Noise, Images, or Velocity", R("""
<p>Scriviamo x<sub>t</sub> = a<sub>t</sub> x<sub>0</sub> + b<sub>t</sub> ε con a<sub>t</sub> = √ᾱ<sub>t</sub>, b<sub>t</sub> = √(1 − ᾱ<sub>t</sub>). La rete può prevedere tre cose diverse:</p>
<ul>
<li><b>rumore</b>: ε<sub>θ</sub>(x<sub>t</sub>, t) ≈ ε (DDPM);</li>
<li><b>immagine</b>: x<sub>0,θ</sub>(x<sub>t</sub>, t) ≈ x<sub>0</sub>;</li>
<li><b>velocità</b>: v<sub>θ</sub>(x<sub>t</sub>, t) ≈ a<sub>t</sub> ε − b<sub>t</sub> x<sub>0</sub> (Salimans e Ho, 2022).</li>
</ul>
<p>La parametrizzazione in v è <b>invertibile</b>:</p>
<span class="f">x<sub>0</sub> = a<sub>t</sub> x<sub>t</sub> − b<sub>t</sub> v,   ε = b<sub>t</sub> x<sub>t</sub> + a<sub>t</sub> v</span>
<p>e l'inversione usa a<sub>t</sub><sup>2</sup> + b<sub>t</sub><sup>2</sup> = 1 (schedule <i>variance preserving</i>: la varianza di x<sub>t</sub> resta 1 se i dati hanno varianza 1).</p>
<ul>
<li>Sono <b>target alternativi</b> per lo stesso denoiser, non processi in avanti diversi.</li>
<li>La formula del campionatore deve usare la parametrizzazione scelta in modo coerente.</li>
</ul>
<div class="box k"><b>Da saper fare: verificare l'inversione</b><p>a x<sub>t</sub> − b v = a(a x<sub>0</sub> + b ε) − b(a ε − b x<sub>0</sub>) = (a<sup>2</sup> + b<sup>2</sup>) x<sub>0</sub> = x<sub>0</sub>. Allo stesso modo b x<sub>t</sub> + a v = (b<sup>2</sup> + a<sup>2</sup>) ε = ε. Geometricamente: con a = cos φ e b = sin φ, x<sub>t</sub> ruota da x<sub>0</sub> a ε, e v = dx<sub>t</sub>/dφ è la sua velocità lungo l'arco.</p></div>
<div class="box x"><b>Approfondimento: perché cambiare target</b><p>Con target ε, a rumore altissimo (ᾱ → 0) l'immagine stimata x̂<sub>0</sub> = (x<sub>t</sub> − b ε<sub>θ</sub>)/a si ottiene dividendo per a ≈ 0, quindi un errore piccolo su ε diventa enorme su x̂<sub>0</sub>; con target x<sub>0</sub> il problema si sposta sulla stima del rumore a rumore basso. v è un compromesso che si comporta bene a tutti i livelli di rumore ed è stabile anche quando SNR → 0, il caso estremo della distillazione progressiva (pochissimi passi, si parte da rumore puro).</p></div>
"""), printed=P(23))

s(24, "x_t = a_t x_0 + b_t ε", R("""
<p>La stessa forma x<sub>t</sub> = a<sub>t</sub> x<sub>0</sub> + b<sub>t</sub> ε descrive due famiglie di modelli:</p>
<table>
<tr><th></th><th>a<sub>t</sub></th><th>b<sub>t</sub></th><th>target tipico</th></tr>
<tr><td>DDPM / LDM / SDXL</td><td>√ᾱ<sub>t</sub></td><td>√(1 − ᾱ<sub>t</sub>)</td><td>ε (oppure v = a<sub>t</sub> ε − b<sub>t</sub> x<sub>0</sub>)</td></tr>
<tr><td>Rectified flow / SD3 / FLUX</td><td>1 − t</td><td>t</td><td>dx<sub>t</sub>/dt = ε − x<sub>0</sub></td></tr>
</table>
<ul>
<li>Entrambe mescolano dati e rumore gaussiano; differiscono per lo <b>schedule</b> (come variano a e b) e per il <b>target</b> della previsione.</li>
<li>Dati x<sub>t</sub> e uno qualunque fra ε, x<sub>0</sub>, v, gli altri si ricavano (a<sub>t</sub> e b<sub>t</sub> sono noti).</li>
<li>Prossimo passo: il cammino in <b>linea retta</b>, facile da integrare in pochi passi.</li>
</ul>
<p>Nota: per il rectified flow a<sup>2</sup> + b<sup>2</sup> = (1 − t)<sup>2</sup> + t<sup>2</sup> non vale 1 (a t = 0,5 vale 0,5): non è variance preserving. Le formule di inversione della slide 23 valgono solo per il caso DDPM; per il flusso lineare si ricavano direttamente da x<sub>t</sub> = (1 − t) x<sub>0</sub> + t ε.</p>
"""), printed=P(24))

s(25, "Flow Matching: Training a Velocity Field", R("""
<p>Sia x<sub>0</sub> un dato e x<sub>1</sub> ∼ 𝒩(0, I) un rumore. Si definisce il cammino <b>lineare</b></p>
<span class="f">x<sub>t</sub> = (1 − t) x<sub>0</sub> + t x<sub>1</sub>,   t ∈ [0, 1]</span>
<p>e la sua velocità condizionata, costante lungo il segmento:</p>
<span class="f">u<sub>t</sub> = dx<sub>t</sub>/dt = x<sub>1</sub> − x<sub>0</sub></span>
<p>Un modello v<sub>θ</sub>(x<sub>t</sub>, t) si addestra con il <b>conditional flow matching</b>:</p>
<span class="f">ℒ<sub>CFM</sub> = 𝔼<sub>x<sub>0</sub>, x<sub>1</sub>, t</sub> ‖v<sub>θ</sub>(x<sub>t</sub>, t) − (x<sub>1</sub> − x<sub>0</sub>)‖<sub>2</sub><sup>2</sup></span>
<p>È lo stesso schema di DDPM: un dato, un rumore, un tempo a caso, una regressione. La generazione parte dal rumore a t = 1 e <b>integra il campo vettoriale</b> imparato fino a t = 0: per esempio con Eulero, x ← x − h · v<sub>θ</sub>(x, t), t ← t − h.</p>
<p>Convenzione: qui t = 0 sono i dati, come in SD3 e nel rectified flow; Lipman et al. usano il contrario (t = 0 rumore). Lo segnala la slide stessa.</p>
<div class="box x"><b>Approfondimento: perché la rete impara un campo sensato</b><p>Lo stesso punto x<sub>t</sub> sta su tanti segmenti diversi, con target x<sub>1</sub> − x<sub>0</sub> diversi. La regressione quadratica impara allora la loro <b>media</b>, 𝔼[x<sub>1</sub> − x<sub>0</sub> | x<sub>t</sub>]: il campo marginale. È questo campo, non i singoli segmenti, a trasportare la distribuzione del rumore in quella dei dati; le sue traiettorie non sono più dritte ma restano poco curve, quindi bastano pochi passi di integrazione (figura nella dispensa).</p></div>
"""), printed=P(25))

s(26, "DDPM and Flow Matching", R("""
<table>
<tr><th></th><th>DDPM</th><th>Flow matching</th></tr>
<tr><td>Target del training</td><td>rumore aggiunto ε</td><td>velocità condizionata x<sub>1</sub> − x<sub>0</sub></td></tr>
<tr><td>Cammino del training</td><td>schedule gaussiano di rumore</td><td>cammino di probabilità scelto (qui lineare)</td></tr>
<tr><td>Campionamento</td><td>passi inversi di denoising</td><td>integrazione del campo vettoriale</td></tr>
<tr><td>Esempi</td><td>LDM, SDXL</td><td>SD3, FLUX</td></tr>
</table>
<p>Nota della slide: la v-prediction di DDPM (slide 23, v = a<sub>t</sub> ε − b<sub>t</sub> x<sub>0</sub>) e la velocità del flow matching (x<sub>1</sub> − x<sub>0</sub>, cioè ε − x<sub>0</sub>) <b>non sono la stessa cosa</b>: hanno lo stesso nome ma coefficienti diversi, perché i cammini sono diversi (un arco di cerchio contro un segmento).</p>
"""), printed=P(26))

s(27, "Few-Step Generation: Distillation", R("""
<p>Il costo del campionamento si misura in <b>NFE</b> (number of function evaluations), il numero di passaggi nella rete. Campionatori migliori (DDIM, risolutori di ODE) arrivano a circa 20–50 passi; la <b>distillazione</b> scende a 1–8.</p>
<table>
<tr><th>Metodo</th><th>Idea</th></tr>
<tr><td>Progressive distillation</td><td>lo studente imita con 1 passo 2 passi dell'insegnante; si ripete, dimezzando ogni volta</td></tr>
<tr><td>Consistency models / LCM</td><td>mappare qualunque x<sub>t</sub> di una traiettoria direttamente su x<sub>0</sub></td></tr>
<tr><td>Adversarial distillation (SDXL-Turbo, FLUX [schnell])</td><td>aggiungere una loss in stile GAN per generare in 1–4 passi</td></tr>
<tr><td>Guidance distillation (FLUX [dev])</td><td>incorporare la CFG in un solo passaggio</td></tr>
</table>
<p>Lettura: la progressive distillation passa da 1024 a 512, 256, … passi; i consistency model imparano la «scorciatoia» lungo la traiettoria deterministica di DDIM; la versione avversaria recupera la nitidezza che la sola regressione perde in pochi passi (si ritorna alle GAN, ma come aiuto); la guidance distillation dimezza il costo eliminando la seconda valutazione della CFG.</p>
<div class="box b"><b>Dal libro · Prince, note del cap. 18</b><p>Prince cita Salimans e Ho (2022), che distillano passi adiacenti in un passo solo, e spiega perché il campionamento è lento: servono tanti passi piccoli perché il vero passo inverso sia vicino a una gaussiana. Con modelli più espressivi per il singolo passo (GAN condizionate, Xiao et al.) i passi possono essere meno.</p></div>
"""), printed=P(27))

s(28, "How Do We Evaluate Generated Images?", R("""
<ul>
<li><b>FID</b> (Fréchet Inception Distance): si estraggono le feature di Inception da immagini vere e generate, si adatta una gaussiana a ciascun insieme e si misura la distanza fra le due gaussiane. Più basso è meglio. Misura <b>qualità e diversità</b> insieme: se il modello genera sempre la stessa bella immagine, la gaussiana delle generate è stretta e la FID peggiora.</li>
<li><b>CLIP score</b>: similarità coseno fra l'embedding CLIP del prompt e quello dell'immagine generata. Più alto è meglio. Misura l'<b>aderenza al prompt</b>.</li>
<li>Alzare w della CFG di solito alza il CLIP score ma prima o poi peggiora la FID: è il <b>compromesso qualità-diversità</b>.</li>
<li>I sistemi moderni usano anche studi di <b>preferenza umana</b> e benchmark composizionali (GenEval, T2I-CompBench: contare oggetti, colori, posizioni relative).</li>
</ul>
<div class="box x"><b>Approfondimento: la formula della FID</b><p>Con medie μ<sub>r</sub>, μ<sub>g</sub> e covarianze Σ<sub>r</sub>, Σ<sub>g</sub> delle feature: FID = ‖μ<sub>r</sub> − μ<sub>g</sub>‖<sup>2</sup> + Tr(Σ<sub>r</sub> + Σ<sub>g</sub> − 2(Σ<sub>r</sub>Σ<sub>g</sub>)<sup>1/2</sup>). Il primo termine guarda la posizione media, il secondo la forma della nuvola: è qui che si vede la mancanza di diversità (Heusel et al., 2017).</p></div>
"""), printed=P(28))

# ===================== ARCHITETTURE =====================

s(29, "Diffusion Model Architectures", R("""<p>Divisoria della seconda parte: architetture U-Net e transformer.</p>"""),
  kind='div', sec=("l27-arch", "Parte 2 · Architetture: dalla U-Net latente ai diffusion transformer", "slide 29–44"), printed='')

s(30, "Architecture Evolution", R("""
<p>Linea del tempo dei denoiser: in blu le U-Net e varianti, in verde i DiT e varianti.</p>
<ul>
<li>2015: la <b>U-Net originale</b> (segmentazione medica).</li>
<li>2020: <b>DDPM</b>, U-Net nello spazio dei pixel.</li>
<li>2022: <b>LDM</b>, U-Net nello spazio latente (Stable Diffusion).</li>
<li>2023: <b>Diffusion Transformer</b> e <b>SDXL</b> (U-Net più grande).</li>
<li>2024: <b>Stable Diffusion 3</b> e <b>FLUX.1</b> (transformer multimodali).</li>
<li>2025: <b>Qwen-Image</b> e <b>Z-Image</b>.</li>
</ul>
<p>Il messaggio: dal 2023 il denoiser passa dalla U-Net al transformer, come era successo nel riconoscimento con il ViT (<a href="#L17">L17</a>).</p>
"""), printed=P(30))

s(31, "Diffusion Model Architectures", R("""
<table>
<tr><th>Modello</th><th>Backbone di denoising</th><th>Riferimento</th></tr>
<tr><td>DDPM</td><td>U-Net nello spazio dei pixel</td><td>Ho et al., 2020</td></tr>
<tr><td>LDM</td><td>U-Net nello spazio latente</td><td>Rombach et al., 2022</td></tr>
<tr><td>SDXL</td><td>U-Net latente più grande</td><td>Podell et al., 2023</td></tr>
<tr><td>KOALA</td><td>U-Net di SDXL compressa</td><td>Lee et al., 2024</td></tr>
<tr><td>DiT</td><td>transformer su patch latenti</td><td>Peebles e Xie, 2023</td></tr>
<tr><td>SD3</td><td>Multimodal Diffusion Transformer (MM-DiT)</td><td>Esser et al., 2024</td></tr>
<tr><td>FLUX.1</td><td>transformer multimodale</td><td>Black Forest Labs, 2024</td></tr>
<tr><td>SANA</td><td>DiT con attenzione lineare</td><td>Xie et al., 2025</td></tr>
</table>
<p>È l'indice della seconda parte: le slide 32–44 prendono questi modelli uno per uno.</p>
"""), printed=P(31))

s(32, "Latent Diffusion Models", R("""
<p>Fare diffusione su 512 × 512 × 3 pixel costa moltissimo: la U-Net gira su tensori enormi per decine di passi. L'idea di <b>Latent Diffusion</b> (Rombach et al., 2022, la base di Stable Diffusion): comprimere prima l'immagine con un autoencoder preaddestrato e fare la diffusione nello spazio compresso.</p>
<span class="f">z<sub>0</sub> = ℰ(x<sub>0</sub>),   x̂<sub>0</sub> = 𝒟(z<sub>0</sub>),   x<sub>0</sub> ∈ ℝ<sup>H×W×3</sup>,  z<sub>0</sub> ∈ ℝ<sup>H/f × W/f × c</sup></span>
<ul>
<li>La diffusione opera nel latente: la rete è ε<sub>θ</sub>(z<sub>t</sub>, t, c).</li>
<li>Con fattore f = 8 il numero di posizioni spaziali scende di 8<sup>2</sup> = <b>64 volte</b>.</li>
<li>Il testo entra con la cross-attention (i riquadri QKV nella figura).</li>
<li>Alla fine il latente z<sub>0</sub> viene decodificato in immagine da 𝒟.</li>
</ul>
<p>Figura (Rombach et al.): a sinistra in rosso lo spazio dei pixel con encoder ℰ e decoder 𝒟; al centro in verde lo spazio latente con il processo di diffusione e la U-Net di denoising con blocchi QKV; a destra il condizionamento (mappe semantiche, testo, rappresentazioni, immagini) che passa per un encoder τ<sub>θ</sub>.</p>
<div class="box x"><b>Approfondimento: perché funziona</b><p>Gran parte dei bit di un'immagine descrive dettagli impercettibili. L'autoencoder (addestrato con loss percettiva e avversaria) se ne occupa una volta per tutte, e la diffusione lavora solo sulla struttura «semantica». Il denoiser non vede mai pixel: per questo i difetti fini (mani, testo piccolo) dipendono anche dalla qualità del decoder.</p></div>
<div class="box b"><b>Dal libro · Prince, note del cap. 18 («Improving speed»)</b><p>Prince presenta Stable Diffusion proprio come rimedio alla lentezza: si proietta il dato in uno spazio latente più piccolo con un autoencoder convenzionale e si fa la diffusione lì, con il vantaggio di ridurre la dimensione e di poter descrivere con la diffusione anche altri tipi di dati.</p></div>
"""), printed=P(32))

s(33, "Following One Tensor Through Stable Diffusion", R("""
<table>
<tr><th>Passo</th><th>Operazione</th><th>Forma</th></tr>
<tr><td>1</td><td>prompt → encoder di testo CLIP</td><td>77 × 768</td></tr>
<tr><td>2</td><td>rumore latente iniziale z<sub>T</sub></td><td>4 × 64 × 64</td></tr>
<tr><td>3</td><td>la U-Net prevede ε<sub>θ</sub>(z<sub>t</sub>, t, c) (e ε<sub>θ</sub>(z<sub>t</sub>, t, ∅) per la CFG)</td><td>4 × 64 × 64</td></tr>
<tr><td>4</td><td>50 passi con CFG: 50 × 2 = 100 valutazioni</td><td></td></tr>
<tr><td>5</td><td>decoder VAE 𝒟(z<sub>0</sub>)</td><td>3 × 512 × 512</td></tr>
</table>
<ul>
<li>Il latente ha 4 · 64<sup>2</sup> = 16 384 valori contro 3 · 512<sup>2</sup> = 786 432 dell'immagine: <b>48 volte meno valori</b>, ma non necessariamente 48 volte meno calcolo (la U-Net ha molti canali interni e attenzione).</li>
<li>Quasi tutto il calcolo è nel passo 3, ripetuto 100 volte: è ciò che architetture e campionatori cercano di ridurre.</li>
</ul>
<p>La nota a piè di pagina: le valutazioni condizionate e incondizionate si contano separatamente, anche se in pratica si mettono nello stesso batch.</p>
<div class="box k"><b>Da saper fare</b><p>Rifare il conto: 786 432 / 16 384 = 48 (il 64 delle posizioni, diviso il rapporto dei canali 4/3). E capire che l'encoder di testo gira una volta, il decoder una volta, la U-Net cento volte.</p></div>
"""), printed=P(33))

s(34, "Stable Diffusion XL (SDXL)", R("""
<ul>
<li>U-Net latente più grande, circa <b>2,6 miliardi</b> di parametri.</li>
<li><b>Due encoder di testo</b>: OpenCLIP ViT-bigG e CLIP ViT-L (le loro feature vengono concatenate).</li>
<li><b>Micro-condizionamento</b> sulle dimensioni originali dell'immagine, sulle coordinate del ritaglio e sulla risoluzione di arrivo: nel training molte immagini sono piccole o ritagliate, e dirlo al modello evita che impari a generare immagini sfocate o tagliate.</li>
<li><b>Refiner</b> facoltativo, addestrato per la fase finale a basso rumore.</li>
</ul>
<p>La figura (Podell et al.): rumore 128 × 128 e prompt entrano nel modello base, che produce un latente «non raffinato»; il refiner lo rifinisce; il decoder VAE produce l'immagine 1024 × 1024.</p>
"""), printed=P(34))

s(35, "KOALA: Efficient Latent Diffusion", R("""
<p>KOALA (Lee et al., 2024) parte da SDXL e sostituisce la sua U-Net da 2,56 miliardi di parametri con <b>studenti più piccoli</b>: KOALA-1B (1,16 miliardi) e KOALA-700M (0,78 miliardi), togliendo blocchi interi e anche strati dentro i blocchi (nella figura l'insegnante in alto, gli studenti sotto, con meno blocchi transformer per livello).</p>
<ul>
<li><b>Distillazione della conoscenza</b> da un SDXL congelato (l'insegnante): le frecce rosse collegano le feature corrispondenti di insegnante e studente.</li>
<li>Imitare le feature intermedie di <b>self-attention</b> risulta particolarmente efficace.</li>
<li>La loss combina l'obiettivo di diffusione con una distillazione a livello di feature:</li>
</ul>
<span class="f">ℒ = ℒ<sub>diffusion</sub> + λ ℒ<sub>KD</sub></span>
<p>Dati: coppie immagine-testo pubbliche derivate da LAION; LAION-POP fornisce immagini ad alta risoluzione con didascalie dettagliate (una delle lezioni dell'articolo: meglio meno immagini ma grandi e ben descritte).</p>
<div class="box b"><b>Dal libro · {C37} § 37.4.1 Knowledge distillation</b><p>Il visionbook spiega la distillazione come imitare le uscite o le attivazioni di un insegnante (già visto nella <a href="#L22">L22</a> per DINO). KOALA la applica alle feature interne del denoiser.</p></div>
""".replace('{C37}', L('transfer_learning.html', 'cap. 37'))), printed=P(35))

s(36, "KOALA: Model Size and Inference Cost", R("""
<p>Il grafico confronta latenza (barre) e memoria (punti) di vari modelli su tre GPU consumer: 8 GB (3060 Ti), 11 GB (2080 Ti), 24 GB (4090). Le scritte «OOM» (out of memory) segnano i modelli che non entrano: <b>SDXL non gira su 8 GB</b>, KOALA sì.</p>
<ul>
<li>Parametri dell'U-Net: SDXL-Base 2,56 miliardi; KOALA-1B 1,16; KOALA-700M 0,78.</li>
<li>KOALA-Lightning-700M: immagine 1024 × 1024 in 0,66 s con 10 passi su una RTX 4090.</li>
<li>Generazione a 1024 px anche su GPU con 8 GB di VRAM.</li>
</ul>
<div class="box w"><b>Attenzione: il punto «Up to 69» è troncato</b><p>Nella slide c'è un punto che dice solo «Up to 69». Dall'articolo (abstract di Lee et al., NeurIPS 2024) la frase completa è: le due U-Net compatte riducono la dimensione dell'U-Net di SDXL <b>fino al 54% e al 69%</b> (KOALA-1B e KOALA-700M). Lo confermano i conti: 1 − 1,16/2,56 ≈ 55%, 1 − 0,78/2,56 ≈ 70%.</p></div>
"""), printed=P(36))

s(37, "DiT: Diffusion Transformers", R("""
<p>Il <b>Diffusion Transformer</b> (Peebles e Xie, 2023) sostituisce la U-Net della latent diffusion con un transformer che lavora su <b>patch del latente</b>, esattamente come un ViT lavora su patch dell'immagine.</p>
<p>Per un latente H × W e patch p × p:</p>
<span class="f">N = HW / p<sup>2</sup>,   Z = PatchEmbed(z<sub>t</sub>) ∈ ℝ<sup>N×D</sup></span>
<p>Esempio: latente 32 × 32 × 4 (immagine 256 × 256 con f = 8), p = 2 → N = 1024/4 = 256 token.</p>
<ul>
<li>Il passo t e la classe y condizionano il transformer con <b>adaLN-Zero</b>: un MLP su (t, y) predice scala γ, spostamento β e una porta α per ogni LayerNorm; α parte da zero, così ogni blocco all'inizio è l'identità (stessa idea della B = 0 di LoRA, <a href="#L25">L25</a>).</li>
<li>La figura confronta tre modi di condizionare: adaLN-Zero (il migliore nell'articolo), cross-attention, token di condizionamento concatenati alla sequenza (in-context).</li>
<li>DiT-XL/2: 675 milioni di parametri, circa 119 GFLOP a 256 × 256.</li>
<li>Training su ImageNet condizionato alla classe, con l'obiettivo di denoising di DDPM.</li>
</ul>
<p>In uscita (in alto nella figura) il transformer produce per ogni patch il rumore previsto e una covarianza Σ, che vengono rimesse in forma 32 × 32 × 4.</p>
"""), printed=P(37))

s(38, "DiT: Scaling Behavior", R("""
<p>A sinistra: FID-50K (più bassa è meglio) dei modelli DiT; il diametro dei cerchi è proporzionale ai GFLOP. A destra: confronto con lo stato dell'arte con guida (ADM-U-G, LDM-4-G, LDM-8-G); DiT-XL/2-G ha la FID più bassa.</p>
<ul>
<li>Generazione ImageNet condizionata alla classe, a 256 × 256 e 512 × 512.</li>
<li>Modelli da 33 a 675 milioni di parametri; patch p ∈ {2, 4, 8}.</li>
<li>Aumentare profondità, larghezza o numero di token migliora in generale la FID.</li>
<li>DiT-XL/2: FID-50K di 2,27 a 256 × 256 con classifier-free guidance.</li>
</ul>
<p>Il messaggio dell'articolo: conta il <b>calcolo</b> (GFLOP), non solo i parametri. Patch più piccole non aggiungono parametri ma moltiplicano i token (p = 8 → 16 token, p = 2 → 256) e quindi il calcolo, e la qualità migliora.</p>
"""), printed=P(38))

s(39, "SANA: Efficient High-Resolution Image Synthesis", R("""
<p>SANA (Xie et al., 2025) punta all'efficienza ad alta risoluzione:</p>
<ul>
<li><b>Transformer con attenzione lineare</b>: sostituisce la self-attention quadratica (costo ∝ N<sup>2</sup>) con una variante a complessità lineare, e arriva a 4096 × 4096.</li>
<li><b>Autoencoder a compressione profonda</b>: compressione spaziale 32× (contro 8× di Stable Diffusion), quindi 16 volte meno token a parità di patch.</li>
<li>Diffusione pura nel latente compresso, senza decodifica autoregressiva.</li>
<li>Varianti da 0,6 e 1,6 miliardi di parametri competitive con modelli molto più grandi.</li>
</ul>
<p>Il grafico: latenza a 1024 × 1024 e a 4096 × 4096 rispetto a Flux-Dev, SD3, PixArt; SANA-0.6B è 25 volte più veloce di Flux-Dev a 1024 e 106 volte a 4096. Gli autori riportano SANA-0.6B competitivo con Flux-12B, circa 20 volte più piccolo e più di 100 volte più veloce. Velocità e memoria contano anche per il fine-tuning di personalizzazione (prossima lezione).</p>
"""), printed=P(39))

s(40, "Stable Diffusion 3 / 3.5: MM-DiT", R("""
<p>Stable Diffusion 3 (Esser et al., 2024) usa un <b>Multimodal Diffusion Transformer</b>.</p>
<ul>
<li>Condizionamento testuale da tre encoder: CLIP-L, OpenCLIP-bigG (le «CLIP-G/14» della figura, 77 + 77 token) e <b>T5-XXL</b>, un modello linguistico.</li>
<li>Token di immagine e di testo interagiscono con <b>attenzione congiunta</b>, ma ciascuna modalità ha i propri pesi (slide 41).</li>
<li>SD3-8B: 8 miliardi di parametri; a 1024 × 1024, 50 passi, 34 s su una RTX 4090 (24 GB).</li>
<li>Training con <b>rectified flow</b> nel latente di un autoencoder preaddestrato:</li>
</ul>
<span class="f">ℒ = 𝔼<sub>t, x<sub>0</sub>, x<sub>1</sub></sub> [w(t) ‖v<sub>θ</sub>(x<sub>t</sub>, t, c) − u<sub>t</sub>‖<sup>2</sup>]</span>
<p>u<sub>t</sub> = x<sub>1</sub> − x<sub>0</sub> come nella slide 25; w(t) pesa i tempi, ed è qui che SD3 dà più importanza ai rumori intermedi (slide 11).</p>
<p>Figura: a sinistra la didascalia passa nei tre encoder; i vettori «pooled» di CLIP si sommano all'embedding del passo (y, che modula i blocchi), i token di testo (c) e le patch del latente rumoroso (x) entrano insieme nei blocchi MM-DiT; alla fine modulazione, linear, unpatching.</p>
"""), printed=P(40))

s(41, "Cross-Attention vs. Joint Attention", R("""
<p><b>Cross-attention</b> (SD 1.x, SDXL): Q = ZW<sub>Q</sub>, K = CW<sub>K</sub>, V = CW<sub>V</sub>.</p>
<ul>
<li>I token dell'immagine Z leggono i token del testo C.</li>
<li>C è fisso: <b>il testo non viene mai aggiornato</b>.</li>
<li>Strati separati di self-attention (immagine ↔ immagine) e cross-attention (immagine → testo).</li>
<li>Mappa di attenzione: N × M.</li>
</ul>
<p><b>Attenzione congiunta</b> (MM-DiT di SD3, FLUX): si impilano le due sequenze,</p>
<span class="f">Q = [ZW<sub>Q</sub><sup>img</sup>; CW<sub>Q</sub><sup>txt</sup>],  K = [ZW<sub>K</sub><sup>img</sup>; CW<sub>K</sub><sup>txt</sup>],  V = [ZW<sub>V</sub><sup>img</sup>; CW<sub>V</sub><sup>txt</sup>]</span>
<ul>
<li>Una sola attenzione sugli N + M token concatenati.</li>
<li>Pesi separati per modalità, attenzione condivisa.</li>
<li>I token di testo vengono <b>aggiornati in ogni blocco</b>.</li>
<li>Mappa: (N + M) × (N + M); la cross-attention ne è un blocco (le righe immagine, le colonne testo).</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Disegnare la matrice (N + M) × (N + M) e indicarne i quattro blocchi: immagine-immagine (la self-attention), immagine-testo (la vecchia cross-attention), testo-immagine e testo-testo (nuovi: il testo «guarda» l'immagine che si sta formando). Con N = 4096 e M = 154 il costo cresce di poco, perché M ≪ N.</p></div>
"""), printed=P(41))

s(42, "FLUX.1: Rectified-Flow Transformer", R("""
<ul>
<li>Modello testo-immagine da <b>12 miliardi</b> di parametri, Black Forest Labs, 2024.</li>
<li>Blocchi transformer multimodali seguiti da blocchi a flusso singolo: <b>19 blocchi double-stream</b> (pesi separati per testo e immagine, come MM-DiT) e <b>38 single-stream</b> (testo e immagine trattati come un'unica sequenza con gli stessi pesi).</li>
<li>Testo e immagine interagiscono con attenzione congiunta; le posizioni sono codificate con <b>rotary embedding</b> (RoPE).</li>
<li>Addestrato con il rectified flow; il campionamento integra il campo di velocità.</li>
<li>Encoder di testo: T5-XXL e CLIP-L.</li>
<li>Varianti [pro], [dev] e [schnell]: [dev] è <b>guidance-distilled</b> (nessun passaggio separato per la CFG), [schnell] è distillato per pochi passi (slide 27).</li>
</ul>
<p>Dimensione e composizione del dataset non sono state rese pubbliche in modo sufficientemente dettagliato; l'architettura è descritta nel report di FLUX.1 Kontext (2025).</p>
"""), printed=P(42))

s(43, "From CLIP to Language Models as Text Encoders", R("""
<table>
<tr><th>Modello</th><th>Encoder di testo</th><th>Denoiser</th></tr>
<tr><td>SD 1.x</td><td>CLIP ViT-L</td><td>U-Net</td></tr>
<tr><td>SDXL</td><td>CLIP ViT-L + OpenCLIP bigG</td><td>U-Net</td></tr>
<tr><td>SD3 / FLUX.1</td><td>CLIP + T5-XXL</td><td>MM-DiT</td></tr>
<tr><td>SANA</td><td>Gemma-2 (LLM solo decoder)</td><td>DiT lineare</td></tr>
<tr><td>Qwen-Image</td><td>Qwen2.5-VL</td><td>MM-DiT</td></tr>
<tr><td>FLUX.2 [dev]</td><td>Mistral Small 3 (VLM da 24B)</td><td>DiT da 32B</td></tr>
<tr><td>Z-Image</td><td>Qwen3-4B</td><td>DiT single-stream da 6B</td></tr>
</table>
<ul>
<li>Le feature contrastive di CLIP sono buone per <b>che cosa</b> c'è nell'immagine, più deboli su <b>conteggio, relazioni spaziali e scrittura di testo</b> (gli stessi limiti di CLIP visti nella <a href="#L24">L24</a>).</li>
<li>Tendenza: modelli linguistici sempre più grandi come encoder, e un'<b>unica sequenza di token</b> per testo e immagine (Z-Image).</li>
</ul>
<div class="box b"><b>Dal libro · {C51}, § 51.3</b><p>Il libro spiega che CLIP è addestrato solo a far combaciare immagine e didascalia nello spazio congiunto: tutto ciò che la didascalia non distingue (quanti oggetti, chi è a sinistra di chi) l'embedding tende a perderlo. Un modello linguistico addestrato a prevedere testo conserva invece la struttura della frase.</p></div>
"""), printed=P(43))

s(44, "Diffusion Architectures: Comparison", R("""
<table>
<tr><th>Modello</th><th>Backbone</th><th>Parametri</th><th>Training</th><th>Contributo principale</th></tr>
<tr><td>SDXL</td><td>U-Net</td><td>2,6B*</td><td>previsione del rumore</td><td>backbone più grande, due encoder di testo</td></tr>
<tr><td>KOALA</td><td>U-Net</td><td>0,78–1,16B*</td><td>previsione del rumore + KD</td><td>compressione e meno passi</td></tr>
<tr><td>DiT</td><td>transformer</td><td>fino a 675M</td><td>previsione del rumore</td><td>scaling con il calcolo del transformer</td></tr>
<tr><td>SD3.5</td><td>MM-DiT</td><td>2,5–8,1B</td><td>rectified flow</td><td>attenzione congiunta testo-immagine</td></tr>
<tr><td>FLUX.1</td><td>transformer ibrido</td><td>12B</td><td>rectified flow</td><td>blocchi multimodali e single-stream</td></tr>
<tr><td>SANA</td><td>DiT lineare</td><td>0,6–1,6B</td><td>basato su flusso</td><td>compressione profonda, attenzione lineare</td></tr>
</table>
<p>Numero di parametri, numero di passi e latenza misurano aspetti diversi dell'efficienza. L'asterisco: parametri della sola U-Net. Negli altri casi i numeri sono delle varianti riportate, e encoder di testo e autoencoder non sono contati in modo uniforme fra le famiglie: <b>non confrontare i numeri alla lettera</b>.</p>
"""), printed=P(44))

# ===================== VIDEO =====================

s(45, "Extending Diffusion to Video", R("""<p>Divisoria della terza parte: aggiungere un asse temporale alla diffusione di immagini.</p>"""),
  kind='div', sec=("l27-video", "Parte 3 · Diffusione per i video", "slide 45–55"), printed='')

s(46, "Video Diffusion Models", R("""
<ul>
<li>Un video è una sequenza di fotogrammi (frame): il modello deve imparare sia l'<b>aspetto</b> sia il <b>movimento</b>.</li>
<li>Si estende la diffusione di immagini con <b>strati temporali</b> che collegano i frame.</li>
<li>Gli strati <b>spaziali</b> modellano ogni frame; quelli <b>temporali</b> i cambiamenti fra frame.</li>
<li>Durante il training si possono mescolare immagini e video (un'immagine è un video di un frame: basta spegnere gli strati temporali).</li>
</ul>
<p>La figura (Ho et al., 2022, Video Diffusion Models) è una U-Net 3D: le etichette indicano risoluzione spaziale (N<sup>2</sup>, (N/K)<sup>2</sup>, …) e canali (M<sub>1</sub>, M<sub>2</sub>, …) a ogni livello; il condizionamento (z<sub>t</sub>, c, λ<sub>t</sub>) entra in ingresso, con λ<sub>t</sub> il livello di rumore.</p>
<div class="box b"><b>Dal libro · Prince, note del cap. 18</b><p>Prince elenca i video fra le applicazioni della diffusione: generazione, previsione di frame passati e futuri, interpolazione (Ho et al., 2022 e altri).</p></div>
"""), printed=P(46))

s(47, "Diffusion Timestep vs. Video Frame Index", R("""
<p>Un video pulito X<sub>0</sub> ∈ ℝ<sup>F×C×H×W</sup> (F frame, C canali) viene corrotto al passo di diffusione t con la solita formula:</p>
<span class="f">X<sub>t</sub> = √ᾱ<sub>t</sub> X<sub>0</sub> + √(1 − ᾱ<sub>t</sub>) ε,   ε ∼ 𝒩(0, I)</span>
<p>Due «tempi» diversi da non confondere:</p>
<ul>
<li><b>t</b>: passo di diffusione, <b>quanto è rumoroso</b> il video;</li>
<li><b>f</b>: indice del frame, <b>dove siamo</b> nel video.</li>
</ul>
<p>A un dato t il denoiser elabora <b>tutti i frame insieme</b>, tutti con lo stesso livello di rumore (la figura: tre frame f = 1, 2, 3, stessa t).</p>
"""), printed=P(47))

s(48, "Video Diffusion: Spatial and Temporal Attention", R("""
<p>Z<sub>t</sub> ∈ ℝ<sup>B×F×H×W×C</sup> è un batch di feature video rumorose. Per non pagare l'attenzione su tutti gli F·H·W token insieme la si scompone:</p>
<table>
<tr><th></th><th>Attenzione spaziale</th><th>Attenzione temporale</th></tr>
<tr><td>Dove</td><td>dentro ogni frame</td><td>attraverso i frame</td></tr>
<tr><td>Forma del tensore</td><td>(BF, HW, C)</td><td>(BHW, F, C)</td></tr>
</table>
<ul>
<li>L'attenzione spaziale collega le posizioni <b>dentro</b> un frame (ogni frame è un elemento del batch); quella temporale collega <b>la stessa posizione</b> nei diversi frame (ogni pixel è un elemento del batch e la sequenza è lunga F).</li>
<li>L'attenzione congiunta su tutti gli FHW token è possibile ma più costosa.</li>
</ul>
<div class="box k"><b>Da saper fare: il costo</b><p>Coppie di attenzione: congiunta (FHW)<sup>2</sup>; spaziale F(HW)<sup>2</sup>; temporale HW·F<sup>2</sup>. Con F = 16 e HW = 1024: congiunta 2,7·10<sup>8</sup>, spaziale 1,7·10<sup>7</sup>, temporale 2,6·10<sup>5</sup>. La versione scomposta costa circa 16 volte meno. Il prezzo: due pixel diversi in due frame diversi non si «vedono» direttamente, ma solo in due passaggi.</p></div>
"""), printed=P(48))

s(49, "Stable Video Diffusion: Image-to-Video at Scale", R("""
<ul>
<li>Si parte da un modello di <b>diffusione di immagini</b> con pesi spaziali preaddestrati.</li>
<li>Si aggiungono strati temporali e si addestra su video.</li>
<li>Pretraining su video su larga scala, poi fine-tuning su video di alta qualità.</li>
<li>Obiettivo: frame realistici <b>e</b> movimento coerente.</li>
</ul>
<p>La figura (Blattmann et al., 2023) mostra sequenze generate (un robot DJ, una casa di formaggio che esplode, un coniglio in un paesaggio fantasy) e, nell'ultima riga, una vista che ruota attorno a un oggetto: generare viste diverse dello stesso oggetto è un sottoprodotto del modello video.</p>
"""), printed=P(49))

s(50, "Video Diffusion Transformers", R("""
<ul>
<li>I video DiT estendono i DiT di immagini a <b>token spazio-temporali</b> invece che patch di immagine.</li>
<li>Un <b>VAE video</b> comprime il video sia nello spazio sia nel tempo.</li>
<li>Il latente viene diviso in <b>patch 3D</b>, proiettato in token e passato al transformer.</li>
</ul>
<span class="f">N<sub>token</sub> = (F′/p<sub>f</sub>) · (H′/p<sub>h</sub>) · (W′/p<sub>w</sub>)</span>
<p>F′, H′, W′ sono le dimensioni del latente, p<sub>f</sub>, p<sub>h</sub>, p<sub>w</sub> quelle della patch.</p>
<div class="box k"><b>Da saper fare: l'esempio di Wan 2.1</b><p>81 frame a 480 × 832. Il VAE comprime di 4 nel tempo tenendo a parte il primo frame: 1 + 80/4 = 21; di 8 nello spazio: 480/8 = 60, 832/8 = 104. Latente 21 × 60 × 104. Patch 1 × 2 × 2: 21 × 30 × 52 = <b>32 760 token</b>. Un'immagine 1024 × 1024 in SD3 fa 4096 token: il video ne ha 8 volte tanti, e l'attenzione costa 64 volte tanto.</p></div>
"""), printed=P(50))

s(51, "Video Generation Models", R("""
<table>
<tr><th>Modello</th><th>Accesso</th><th>Idea principale</th></tr>
<tr><td>CogVideoX</td><td>pesi aperti</td><td>video DiT, VAE 3D</td></tr>
<tr><td>Wan 2.1/2.2</td><td>pesi aperti</td><td>video DiT, flow matching; mixture of experts nella 2.2</td></tr>
<tr><td>HunyuanVideo</td><td>pesi aperti</td><td>grande transformer video</td></tr>
<tr><td>Sora / Sora 2</td><td>proprietario</td><td>patch latenti spazio-temporali</td></tr>
<tr><td>Veo 3.1</td><td>proprietario</td><td>generazione di video e audio</td></tr>
<tr><td>Runway Gen-4.5</td><td>proprietario</td><td>generazione video e controllo creativo</td></tr>
</table>
<p>Nota della slide: <b>pesi aperti non vuol dire</b> dati di training o codice di training aperti.</p>
"""), printed=P(51))

s(52, "CogVideoX: Video Diffusion Transformer", R("""
<ul>
<li>Usa un <b>VAE 3D causale</b> per comprimere nello spazio e nel tempo («causale»: ogni frame latente dipende solo dai frame precedenti, così il primo frame si codifica da solo come un'immagine).</li>
<li>Un transformer di diffusione elabora token di video e di testo con <b>attenzione congiunta</b> («3D Full Attention» nella figura).</li>
<li><b>Modulazione separata</b> per token di testo e video («Text Expert AdaLN» e «Vision Expert AdaLN»: scala, spostamento e porta diversi per le due modalità, come i pesi separati di MM-DiT).</li>
<li>Rilasciato in varianti da 2 e 5 miliardi di parametri.</li>
</ul>
"""), printed=P(52))

s(53, "Wan: Video Diffusion Models", R("""
<ul>
<li>Famiglia di modelli video a pesi aperti.</li>
<li>Un VAE video comprime nello spazio e nel tempo.</li>
<li>Un transformer di diffusione lavora sui latenti video, addestrato con <b>flow matching</b>.</li>
<li>Wan 2.2 introduce <b>due transformer separati</b>: uno per i livelli di rumore alti, uno per quelli bassi.</li>
<li>A ogni passo di denoising si usa <b>un solo esperto</b>, scelto in base al livello di rumore.</li>
</ul>
<p>Così i due esperti si specializzano: quello ad alto rumore decide composizione e movimento globale, quello a basso rumore i dettagli. Il costo per passo resta quello di un modello solo, anche se i parametri totali raddoppiano. È la stessa intuizione del refiner di SDXL (slide 34).</p>
"""), printed=P(53))

s(54, "Meta Movie Gen: Large-Scale Video Generation", R("""
<ul>
<li>Transformer video da <b>30 miliardi</b> di parametri addestrato con flow matching.</li>
<li>Autoencoder temporale per comprimere i video («TAE» nella figura).</li>
<li>Pretraining su immagini e video, poi fine-tuning su video di alta qualità.</li>
<li>Pesi non rilasciati.</li>
</ul>
<p>Figura (Polyak et al., 2024): il video passa dall'encoder TAE, viene diviso in patch (patchify) e affiancato agli embedding di posizione; i blocchi transformer ricevono il passo t (scala e spostamento) e il testo via cross-attention, da tre encoder (UL2, ByT5, MetaCLIP); il decoder TAE ricostruisce il video. L'esempio è uno struzzo che regge un cartello con una scritta.</p>
"""), printed=P(54))

s(55, "Proprietary Video Generation Models", R("""
<p><b>Sora</b> (OpenAI):</p>
<ul>
<li>compressione del video in uno spazio latente;</li>
<li>transformer di diffusione su <b>patch spazio-temporali</b>;</li>
<li>supporta risoluzioni, durate e proporzioni diverse (le patch permettono sequenze di lunghezza variabile).</li>
</ul>
<p><b>Veo 3.1</b> (Google DeepMind):</p>
<ul>
<li>testo → video e immagine → video;</li>
<li>genera video con <b>audio sincronizzato</b>;</li>
<li>dettagli di architettura e training non del tutto pubblici.</li>
</ul>
"""), printed=P(55))

# ===================== CHIUSURA =====================

s(56, "Summary", R("""
<ul>
<li>I modelli di diffusione imparano a <b>invertire</b> un processo che aggiunge rumore gradualmente.</li>
<li>Il training consiste nel <b>prevedere il rumore</b> aggiunto a un passo scelto a caso.</li>
<li>Condizionamento sul testo e classifier-free guidance permettono di <b>controllare</b> la generazione.</li>
<li>La latent diffusion <b>riduce il costo</b> lavorando in uno spazio compresso.</li>
<li>U-Net e diffusion transformer sono le architetture principali.</li>
<li>La diffusione video estende quella di immagini modellando la <b>dimensione temporale</b>.</li>
</ul>
<p>Mancano nel riassunto due cose che all'orale contano: il <b>flow matching</b> (SD3, FLUX, Wan, Movie Gen lo usano tutti) e i metodi per fare <b>meno passi</b> (DDIM, distillazione).</p>
"""), sec=("l27-fine", "Chiusura", "slide 56–59"), printed=P(56))

s(57, "References", R("""
<p>Bibliografia della lezione. Quelle da conoscere per nome: Ho et al. 2020 (DDPM), Song et al. 2021 (SDE e score), Song, Meng ed Ermon 2021 (DDIM), Nichol e Dhariwal 2021 (Improved DDPM, schedule a coseno), Dhariwal e Nichol 2021 (classifier guidance, «Diffusion Models Beat GANs»), Ho e Salimans 2022 (CFG), Salimans e Ho 2022 (distillazione progressiva, v-prediction), Lipman et al. 2023 (flow matching), Liu et al. 2023 (rectified flow), Rombach et al. 2022 (latent diffusion), Peebles e Xie 2023 (DiT), Esser et al. 2024 (SD3), Heusel et al. 2017 (FID).</p>
"""), printed=P(57))

s(58, "Next Lecture", R("""
<p>Prossima lezione: <b>personalizzazione</b> dei modelli di diffusione, cioè insegnare a un modello preaddestrato un soggetto o uno stile nuovo da poche immagini (Textual Inversion, DreamBooth, LoRA). Riprende la <a href="#L25">L25</a> sul PEFT.</p>
"""), printed=P(58))

s(59, "Panoramica delle slide", R("""
<p>Non è una slide: è la pagina di panoramica con le miniature di tutte le 58 pagine, generata automaticamente da Beamer. Utile solo per orientarsi.</p>
"""), printed=P(59))
