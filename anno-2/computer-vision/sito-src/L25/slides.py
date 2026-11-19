VB = 'https://visionbook.mit.edu/'
def L(slug, txt): return f'<a href="{VB}{slug}" target="_blank">{txt}</a>'
LK = {
 '{C37}': L('transfer_learning.html', 'cap. 37'),
 '{C24}': L('convolutional_neural_nets.html', 'cap. 24'),
 '{C26}': L('transformers.html', 'cap. 26'),
 '{C51}': L('VLMs.html', 'cap. 51'),
 '{C12}': L('neural_nets.html', 'cap. 12'),
 '{C14}': L('backpropagation.html', 'cap. 14'),
}
def P(n): return f' <em>· pag. {n}/48</em>'
def R(t):
    for k, v in LK.items(): t = t.replace(k, v)
    return t

# ===================== INTRODUZIONE E PEFT =====================

s(1, "Parameter-Efficient Fine-Tuning: copertina", R("""
<p>Lezione del 12 novembre 2026, tenuta da <b>Donald Shenaj</b> come la <a href="#L24">L24</a>. Tema: come <b>adattare</b> un modello preaddestrato grande (un ViT, CLIP, SAM, un LLM) a un compito nuovo addestrando solo una <b>piccolissima frazione</b> dei parametri.</p>
<p>Il PDF ha 48 pagine e il footer stampa «n / 48» con n = pagina del PDF, copertina compresa. Le divisorie (pag. 4, 16, 36) non hanno footer. La pag. 48 non è una slide ma la panoramica con le miniature generata da Beamer.</p>
<div class="box k"><b>Il filo della lezione in una frase</b><p>Invece di riaddestrare tutti i pesi W<sub>0</sub>, si <b>congela</b> il modello e si impara solo un pezzetto: i bias (BitFit), piccoli moduli inseriti (adapter), vettori aggiunti all'ingresso (prompt), oppure un <b>aggiornamento a basso rango</b> ΔW = BA dei pesi esistenti (LoRA), che dopo l'addestramento si somma a W<sub>0</sub> e non costa nulla in inferenza.</p></div>
"""), sec=("l25-intro", "Introduzione: dal fine-tuning al PEFT", "slide 1–3"), printed=P(1))

s(2, "Lecture Outline", R("""
<p>Tre parti:</p>
<ol>
<li><b>Parameter-Efficient Fine-Tuning</b>: perché serve e i metodi «classici» (BitFit, adapter, CLIP-Adapter, prompt e prefix tuning, VPT), slide 4–15.</li>
<li><b>Low-Rank Adaptation (LoRA)</b>: il metodo, la sua matematica e le varianti (QLoRA, DoRA, AdaLoRA, VeRA), slide 16–35.</li>
<li><b>LoRA for Computer Vision</b>: ViT, segmentazione medica, Conv-LoRA, SemLA, VoRA; confronto finale, slide 36–47.</li>
</ol>
"""), printed=P(2))

s(3, "Recap: probing, fine-tuning parziale e completo", R("""
<p>Dato un modello preaddestrato f<sub>θ<sub>0</sub></sub> (θ<sub>0</sub> = i suoi parametri) e un compito nuovo con una testa ϕ (per esempio un classificatore lineare):</p>
<ul>
<li><b>Linear probing</b>: θ<sub>0</sub> congelato, si addestra solo la testa ϕ. È quello che hai fatto nella <a href="#L23">L23</a> su SimSiam e DINOv3.</li>
<li><b>Fine-tuning parziale</b>: si addestrano ϕ e un sottoinsieme θ<sub>train</sub> ⊊ θ<sub>0</sub> (per esempio gli ultimi blocchi).</li>
<li><b>Fine-tuning completo</b>: si addestrano ϕ e tutti i θ<sub>0</sub>.</li>
</ul>
<p><b>PEFT</b>: i parametri preaddestrati restano <b>congelati</b> e si addestra un insieme piccolo di parametri specifici del compito, sempre chiamato ϕ, con</p>
<span class="f">|ϕ| ≪ |θ<sub>0</sub>|</span>
<p>dove |·| conta i parametri scalari. Attenzione alla notazione: nella prima parte della slide ϕ è la testa, nella seconda è tutto ciò che si addestra (testa più eventuali moduli aggiunti).</p>
<div class="box b"><b>Dal libro · {C37}, § 37.3 Finetuning e § 37.3.1–37.3.2</b><p>Il libro presenta il fine-tuning come «continuare ad addestrare» partendo da θ<sub>0</sub>, sostituendo la testa (e se serve il primo strato) quando cambia la dimensione di uscita. Nel § 37.3.1 mostra che si può congelare una parte del grafo e aggiornarne un'altra, per risparmiare memoria o per <b>non dimenticare</b> ciò che il modello sapeva, e accenna proprio all'aggiornamento a basso rango di una matrice di pesi come modo diffuso di aggiornare «solo un sottospazio». Il § 37.3.2 chiama i classificatori lineari sulle feature congelate <i>linear probe</i>.</p></div>
"""), printed=P(3))

s(4, "Parameter-Efficient Fine-Tuning", R("""<p>Divisoria della prima parte: perché il PEFT e i metodi che addestrano bias, moduli aggiunti o vettori di prompt.</p>"""),
  kind='div', sec=("l25-peft", "Parte 1 · Metodi PEFT", "slide 4–15"), printed='')

s(5, "The Model Ecosystem", R("""
<p>La figura (Horwitz et al., 2025) è una mappa dei modelli pubblicati su Hugging Face: ogni nodo è un modello, gli archi collegano un modello alla sua «radice» da cui è derivato. I colori indicano il tipo di derivazione: <b>adapter</b> (azzurro), <b>fine-tune</b> (verde), <b>quantizzazione</b> (viola), <b>merge</b> (blu). Si vedono alberi enormi attorno a pochi modelli base, per esempio stable-diffusion-xl-base-1.0 e Llama-3.2-3B.</p>
<p>Il messaggio: oggi quasi nessuno addestra da zero. Si parte da un modello base e se ne fanno migliaia di <b>varianti</b>, e la maggior parte sono adapter (soprattutto LoRA) e fine-tuning. Per questo conta che adattare costi poco in memoria, in tempo e in spazio su disco.</p>
"""), printed=P(5))

s(6, "Why Parameter-Efficient Fine-Tuning?", R("""
<p>Quanto costa il fine-tuning completo di un modello con |θ<sub>0</sub>| parametri, addestrato con <b>Adam</b> in FP32 (32 bit = 4 byte)?</p>
<span class="f">4|θ<sub>0</sub>| + 4|θ<sub>0</sub>| + 8|θ<sub>0</sub>| = 16|θ<sub>0</sub>| byte</span>
<ul>
<li><b>Pesi</b>: 4 byte per parametro.</li>
<li><b>Gradienti</b>: 4 byte per parametro.</li>
<li><b>Stati di Adam</b>: due numeri FP32 per parametro, il momento primo m (media mobile dei gradienti) e il secondo v (media mobile dei quadrati), quindi 8 byte.</li>
<li>Con <b>più compiti</b> bisogna salvare una copia intera del modello per ciascuno.</li>
<li>Il PEFT addestra pochi parametri: si risparmiano gradienti, stati dell'ottimizzatore e checkpoint (i pesi del modello invece restano in memoria).</li>
</ul>
<p>La stima <b>esclude le attivazioni</b> salvate per la backpropagation e gli altri buffer.</p>
<div class="box k"><b>Da saper fare: il conto</b><p>ViT-B/16 con circa 86 milioni di parametri: 16 × 86·10<sup>6</sup> ≈ 1,4 GB solo per pesi, gradienti e Adam. Un LLM da 7 miliardi: 16 × 7·10<sup>9</sup> = 112 GB, più di una GPU da 80 GB, prima ancora delle attivazioni. Con LoRA il termine «gradienti + Adam» (12 byte per parametro) si paga solo sui parametri di LoRA, magari lo 0,1–1% del totale: restano circa 4|θ<sub>0</sub>| byte per i pesi congelati, cioè 28 GB per il modello da 7 miliardi.</p></div>
<div class="box x"><b>Approfondimento: in pratica è spesso di più</b><p>Con il <i>mixed precision</i> classico si tengono pesi e gradienti in 16 bit più una copia «master» dei pesi in FP32 e i due stati di Adam: 2 + 2 + 4 + 8 = 16 byte, lo stesso totale per strade diverse. Le attivazioni, che la slide esclude, crescono con batch e lunghezza della sequenza e spesso dominano.</p></div>
"""), printed=P(6))

s(7, "Bias-Term Fine-Tuning (BitFit)", R("""
<p><b>BitFit</b> (Ben Zaken et al., 2022) addestra <b>solo i bias</b> e lascia congelate tutte le matrici dei pesi:</p>
<span class="f">h = σ(Wx + b),  W congelata, b addestrato</span>
<ul>
<li><b>Nessun modulo né parametro aggiunto</b>: si sceglie solo quali parametri esistenti sbloccare.</li>
<li>Su BERT si addestra circa lo <b>0,08–0,09%</b> dei parametri.</li>
<li>Su diversi compiti del benchmark di linguaggio <b>GLUE</b> le prestazioni sono paragonabili al fine-tuning completo.</li>
</ul>
<p>Perché può funzionare: un bias sposta l'uscita di uno strato prima della non linearità, quindi cambia <b>quali unità si attivano</b> e quanto. Ma può solo traslare, non ruotare né scalare le feature: è il metodo più vincolato della lezione.</p>
<div class="box k"><b>Da saper fare</b><p>In un blocco transformer di dimensione d con MLP di dimensione 4d i bias sono: Q, K, V, O (4d), i due strati dell'MLP (4d + d), le due LayerNorm (2d), cioè 11d. Per un ViT-B (d = 768, 12 blocchi) sono 12 × 11 × 768 ≈ 101 mila, contro 86 milioni di parametri: circa lo 0,12%. Lo rifarai nel <a href="#L26">lab</a>.</p></div>
"""), printed=P(7))

s(8, "Residual Adapters for Visual Domains", R("""
<p>Uno dei primi adapter in visione (Rebuffi et al., 2017). Si vuole <b>un solo backbone convoluzionale</b> per tanti domini visivi diversi (immagini di aerei, testi, cifre, fiori, texture…). Per ogni dominio d si inserisce un <b>adapter residuo</b>:</p>
<span class="f">h′ = h + α<sub>d</sub> ∗ h</span>
<ul>
<li>α<sub>d</sub>: filtro convoluzionale <b>1×1</b> appreso, specifico del dominio d. Una conv 1×1 è una piccola matrice C×C applicata in ogni posizione: mescola i canali senza guardare i vicini.</li>
<li>Il backbone (le conv grandi, w<sub>1</sub>, w<sub>2</sub> nella figura) è <b>condiviso</b> fra i domini.</li>
<li>Ogni dominio ha il <b>suo</b> adapter e i suoi parametri di normalizzazione (le BatchNorm, BN nella figura).</li>
<li>Valutato sui dieci dataset del <b>Visual Decathlon</b>.</li>
</ul>
<p>La struttura «h + qualcosa(h)» è la stessa idea delle ResNet (<a href="#L15">L15</a>): se α<sub>d</sub> = 0 l'adapter non cambia nulla, quindi si parte dal modello preaddestrato e si impara solo la correzione.</p>
"""), printed=P(8))

s(9, "Bottleneck Adapters for Transformers", R("""
<p>L'adapter di <b>Houlsby et al. (2019)</b>, il più usato nei transformer. Per ogni compito t si inserisce in ogni blocco un modulo residuo a <b>collo di bottiglia</b>:</p>
<span class="f">h′ = h + W<sub>up</sub><sup>(t)</sup> σ(W<sub>down</sub><sup>(t)</sup> h),   W<sub>down</sub><sup>(t)</sup> ∈ ℝ<sup>r×d</sup>,  W<sub>up</sub><sup>(t)</sup> ∈ ℝ<sup>d×r</sup></span>
<ul>
<li><b>Collo di bottiglia</b>: la dimensione passa da d a r e torna a d, con r ≪ d.</li>
<li><b>2dr</b> pesi addestrabili per adapter, bias esclusi.</li>
<li>I pesi del transformer preaddestrato restano congelati.</li>
<li>La figura mostra dove vanno: <b>due adapter per blocco</b>, uno dopo l'attenzione e uno dopo il feed-forward, prima della somma residua e della LayerNorm (i blocchi verdi «Adapter»; nell'articolo si addestrano anche le LayerNorm).</li>
<li><b>Limite</b>: sono operazioni <b>in più, in sequenza</b>, che aumentano la latenza in inferenza (slide 18).</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>d = 768, r = 64: 2 × 768 × 64 ≈ 98 mila pesi per adapter, due per blocco, 12 blocchi: circa 2,4 milioni, meno del 3% di un ViT-B. Con r = 8 si scende a circa 300 mila.</p></div>
"""), printed=P(9))

s(10, "Adapters for 3D Medical Segmentation", R("""
<p>Esempio di adapter usati per cambiare <b>tipo di dato</b>, non solo dominio (Gong et al., 2023, 3DSAM-adapter). <b>SAM</b> (Segment Anything) è un modello di segmentazione 2D promptabile, addestrato su foto naturali; qui lo si vuole usare su <b>volumi 3D</b> medici (TAC, risonanza).</p>
<ul>
<li><b>SAM 2D</b> elabora l'informazione spaziale dentro una singola fetta.</li>
<li><b>3DSAM-adapter</b> inserisce, dopo ogni blocco di attenzione congelato, uno <b>spatial adapter</b> con convoluzioni 3D <i>depth-wise</i> (una per canale).</li>
<li>Le feature sono organizzate come un volume X ∈ ℝ<sup>D×H×W×C</sup> (profondità, altezza, larghezza, canali): la conv 3D le mescola anche <b>fra fette vicine</b>.</li>
</ul>
<p>Così si riusano i pesi di SAM e si aggiunge solo ciò che manca: il contesto lungo la profondità. Nella figura sono marcati come addestrati (fiamma) gli adapter, il prompt encoder, il mask decoder e alcuni embedding; il resto è congelato.</p>
"""), printed=P(10))

s(11, "CLIP-Adapter: motivazione", R("""
<p>Il problema è il <b>few-shot</b>: adattare un modello avendo pochissimi esempi etichettati per classe (esempio della slide: malattie rare con solo 5 immagini per classe). Due modi di adattare CLIP (<a href="#L24">L24</a>) restando congelato:</p>
<ul>
<li><b>CoOp</b>: al posto delle parole del prompt («a photo of a») impara dei <b>vettori di contesto</b> [V<sub>1</sub>][V<sub>2</sub>]…[V<sub>M</sub>] davanti al nome della classe, che passano nel text encoder congelato. Il gradiente deve <b>attraversare tutto il text encoder</b>.</li>
<li><b>CLIP-Adapter</b>: un piccolo <b>MLP</b> dopo l'image encoder congelato (e volendo uno dopo il text encoder). Il gradiente si ferma all'adapter.</li>
</ul>
<p>La figura confronta i costi riportati dall'articolo (Gao et al., 2021): CoOp 7193 MiB di memoria GPU e 14 h 40 min di training, CLIP-Adapter 2227 MiB e 50 min. La differenza viene dal fatto che CLIP-Adapter non fa backpropagation dentro gli encoder.</p>
<div class="box b"><b>Dal libro · {C37}, § 37.5 Prompting</b><p>Il libro chiama <i>prompting</i> il modificare l'ingresso invece dei pesi: in NLP si antepone del testo, per i VLM si possono usare gli stessi prompt testuali (§ 51.3), per le immagini si può aggiungere un «prompt» di pixel ottimizzato (come un rumore avversario, ma che aiuta invece di danneggiare, fig. 37.6) o un token aggiuntivo a un ViT (fig. 37.7). CoOp è la versione «appresa» del prompt testuale.</p></div>
"""), printed=P(11))

s(12, "CLIP-Adapter: architettura", R("""
<p>Con poche immagini etichettate per classe si adatta l'embedding dell'immagine prodotto da CLIP:</p>
<ul>
<li>f: embedding dell'immagine dall'encoder CLIP <b>congelato</b>.</li>
<li>A<sub>v</sub>(f): nuovo embedding prodotto dall'<b>adapter visivo</b> addestrabile (un MLP a due strati).</li>
</ul>
<p>Si combinano originale e adattato con un <b>coefficiente residuo</b> α:</p>
<span class="f">f<sup>⋆</sup> = (1 − α) f + α A<sub>v</sub>(f)</span>
<ul>
<li>f<sup>⋆</sup> è l'embedding finale usato per classificare.</li>
<li>Si confronta f<sup>⋆</sup> con gli embedding di testo delle classi con la <b>similarità coseno</b>, esattamente come nello zero-shot di CLIP.</li>
</ul>
<p>α decide quanto fidarsi dell'adapter: α = 0 è CLIP zero-shot, α = 1 butta via la feature originale. Con pochi esempi conviene un α piccolo, perché un MLP addestrato su 5 immagini per classe va facilmente in <b>overfitting</b>; mescolando con f si conserva la conoscenza generale di CLIP. Nella figura c'è anche un adapter per il testo, A<sub>t</sub>(W), applicato alla matrice W delle classi.</p>
"""), printed=P(12))

s(13, "Prompt tuning e prefix tuning", R("""
<p><b>Prompt tuning</b>: si antepongono alla sequenza d'ingresso X (i token) p embedding addestrabili:</p>
<span class="f">X′ = [P; X],  P ∈ ℝ<sup>p×d</sup></span>
<p>P sono «parole virtuali»: vettori nello stesso spazio dei token, ma non corrispondono a nessuna parola del vocabolario.</p>
<p><b>Prefix tuning</b> (Li e Liang, 2021): invece di aggiungere token all'ingresso, si aggiungono p <b>chiavi e valori</b> addestrabili all'attenzione di <b>ogni</b> strato ℓ:</p>
<span class="f">K<sub>ℓ</sub>′ = [P<sub>K</sub><sup>ℓ</sup>; K<sub>ℓ</sub>],  V<sub>ℓ</sub>′ = [P<sub>V</sub><sup>ℓ</sup>; V<sub>ℓ</sub>]</span>
<ul>
<li>K<sub>ℓ</sub>, V<sub>ℓ</sub>: chiavi e valori dello strato ℓ; P<sub>K</sub><sup>ℓ</sup>, P<sub>V</sub><sup>ℓ</sup>: i prefissi appresi per quello strato.</li>
<li>Ogni token può «guardare» anche questi p elementi in più: è un contesto aggiuntivo che orienta l'attenzione verso il compito.</li>
<li>I pesi del transformer restano congelati. La figura: con il fine-tuning serve una copia del transformer per compito (traduzione, riassunto, tabella → testo); con il prefix tuning un solo transformer e un piccolo prefisso per compito.</li>
</ul>
<p>Collegamento con la <a href="#L17">L17</a>–<a href="#L18">L18</a>: nella self-attention ogni query fa una softmax sulle chiavi; aggiungere chiavi e valori significa aggiungere voci a quella somma pesata, senza cambiare le proiezioni W<sub>Q</sub>, W<sub>K</sub>, W<sub>V</sub>.</p>
<div class="box x"><b>Approfondimento</b><p>La formula del prompt tuning X′ = [P; X] è quella di Lester et al. (2021), «The Power of Scale for Parameter-Efficient Prompt Tuning»; la slide cita solo Li e Liang per il prefix tuning. Differenza pratica: il prompt agisce solo all'ingresso, il prefisso in ogni strato, quindi è più espressivo ma ha più parametri.</p></div>
"""), printed=P(13))

s(14, "Visual Prompt Tuning (VPT)", R("""
<p>Il prompt tuning portato al <b>ViT</b> (Jia et al., 2022). Si imparano p embedding di prompt P ∈ ℝ<sup>p×d</sup>, con la stessa dimensione dei token delle patch.</p>
<ul>
<li>I prompt sono <b>vettori addestrabili</b>, non patch estratte dall'immagine.</li>
<li><b>VPT-Shallow</b>: prompt inseriti solo nello strato d'ingresso.</li>
<li><b>VPT-Deep</b>: prompt <b>diversi</b> e addestrabili inseriti a ogni strato del transformer.</li>
<li>Si addestrano solo i prompt e la testa di classificazione; il backbone ViT resta congelato.</li>
</ul>
<p>Nella figura: in rosso (fiamma) i prompt P<sub>0</sub>, P<sub>1</sub>, … e la testa, in blu (fiocco) gli strati congelati; x<sub>0</sub> è il [CLS], E<sub>0</sub> i token delle patch. VPT-Deep è l'analogo visivo del prefix tuning, con una differenza: in VPT-Deep i prompt di uno strato vengono sostituiti da quelli nuovi dello strato dopo, mentre il prefix tuning aggiunge chiavi e valori.</p>
<div class="box b"><b>Dal libro · {C37}, § 37.5 e fig. 37.7</b><p>Il libro descrive proprio VPT: un token-prompt di dimensione d concatenato ai token delle patch, ottimizzato per migliorare le prestazioni sul compito nuovo; tutti i token gli fanno attenzione, così modula la trasformazione già dal primo strato. Nota sulla didascalia della fig. 37.7: dice che i parametri della rete originale «devono essere aggiornati», mentre il testo e l'articolo di VPT tengono il backbone congelato; leggila come una svista.</p></div>
"""), printed=P(14))

s(15, "Visual Prompt Tuning: risultati", R("""
<p>Benchmark <b>VTAB-1k</b>: 19 compiti visivi, con <b>1000 esempi etichettati</b> per compito, divisi in tre gruppi: <b>Natural</b> (7, foto comuni), <b>Specialized</b> (4, immagini mediche e satellitari), <b>Structured</b> (8, conteggio, distanza, orientamento: richiedono geometria più che semantica).</p>
<p>I grafici: accuratezza di test in funzione della dimensione del backbone (ViT-B/16, ViT-L/16, ViT-H/14). Linee: VPT-deep (rosso), VPT-shallow, Full (fine-tuning completo, blu), Linear (probe), Bias (BitFit), Adapter.</p>
<ul>
<li><b>VPT-Deep supera il fine-tuning completo</b> su Natural e Structured per diverse configurazioni di ViT.</li>
<li>Su Specialized VPT-deep e Full sono quasi appaiati.</li>
<li>Le prestazioni dipendono dal gruppo di compiti e dal backbone.</li>
</ul>
<p>Perché un metodo con meno parametri può battere il fine-tuning completo? Con solo 1000 esempi, aggiornare 300–600 milioni di parametri porta a <b>overfitting</b> e a dimenticare ciò che il modello sapeva; tenere il backbone fermo è una forma di <b>regolarizzazione</b>.</p>
"""), printed=P(15))

# ===================== LoRA =====================

s(16, "Low-Rank Adaptation (LoRA)", R("""<p>Divisoria della seconda parte: LoRA, il metodo PEFT oggi più usato, e le sue varianti.</p>"""),
  kind='div', sec=("l25-lora", "Parte 2 · LoRA e varianti", "slide 16–35"), printed='')

s(17, "Motivazione di LoRA", R("""
<p>Il fine-tuning completo aggiorna le matrici dei pesi preaddestrate:</p>
<span class="f">W′ = W<sub>0</sub> + ΔW</span>
<p>I limiti dei metodi visti finora:</p>
<ul>
<li>Il <b>fine-tuning completo</b> richiede di salvare dei pesi interi per ogni compito.</li>
<li>Gli <b>adapter a collo di bottiglia</b> aggiungono operazioni durante l'inferenza.</li>
<li><b>Prompt e prefix tuning</b> modificano l'ingresso o il contesto dell'attenzione (e occupano posti nella sequenza).</li>
</ul>
<p><b>LoRA</b>: imparare un aggiornamento ΔW <b>a basso rango</b>, che dopo l'addestramento si può <b>sommare</b> (merge) alle matrici preaddestrate.</p>
<p>L'ipotesi di fondo (Hu et al., 2022): il cambiamento che serve per adattare un modello preaddestrato a un compito ha un <b>rango intrinseco basso</b>, cioè vive in poche direzioni. Non serve una matrice d×d piena per descriverlo.</p>
"""), printed=P(17))

s(18, "Adapter a collo di bottiglia: latenza in inferenza", R("""
<p>Tabella 1 dell'articolo di LoRA: tempo di un passo in avanti di <b>GPT-2 medium</b>, in millisecondi.</p>
<table>
<tr><th>batch</th><th>32</th><th>16</th><th>1</th></tr>
<tr><td>Fine-tuning / LoRA</td><td>1449,4</td><td>338,0</td><td>19,8</td></tr>
<tr><td>Adapter<sup>L</sup></td><td>1482,0</td><td>354,8</td><td>23,9</td></tr>
<tr><td>Adapter<sup>H</sup></td><td>1492,2</td><td>366,3</td><td>25,8</td></tr>
</table>
<ul>
<li>Il costo degli adapter, in proporzione, è <b>più grande con batch piccoli</b>: con batch 1 Adapter<sup>H</sup> è più lento del 30%, con batch 32 del 3%. Con poco lavoro parallelo la GPU è sottoutilizzata e gli strati in più, che vanno eseguiti in sequenza, pesano di più.</li>
<li>LoRA, dopo il merge, ha la stessa latenza del modello originale: zero operazioni in più.</li>
</ul>
<p>Adapter<sup>H</sup> è quello di Houlsby (due per blocco), Adapter<sup>L</sup> una variante più leggera (un adapter per blocco, di Lin et al.).</p>
<div class="box w"><b>Attenzione: manca la lunghezza della sequenza</b><p>Nell'articolo le tre colonne non differiscono solo per il batch: hanno anche <b>sequenze lunghe 512, 256 e 128</b> token. La slide la omette, quindi «batch 1» qui vuol dire anche sequenze più corte. La conclusione resta vera, ma i due fattori sono mescolati.</p></div>
"""), printed=P(18))

s(19, "Prefix tuning: il budget di parametri", R("""
<p>Figura 2 dell'articolo di LoRA: accuratezza di validazione su <b>WikiSQL</b> (domanda in linguaggio naturale → query SQL) e <b>MultiNLI</b> (implicazione fra frasi) in funzione del log<sub>10</sub> del numero di parametri addestrabili, con GPT-3 da 175 miliardi.</p>
<ul>
<li>Il punto blu isolato a destra (circa 10<sup>11</sup>) è il fine-tuning completo.</li>
<li>Le curve del prefix tuning (PrefixEmbed arancione, PrefixLayer verde) salgono e poi <b>scendono</b>: allungare il prefisso oltre un certo punto peggiora l'accuratezza.</li>
<li>LoRA (triangoli viola) sta in alto e resta stabile su un ampio intervallo di budget, a livello del fine-tuning completo.</li>
</ul>
<p>Un motivo per cui il prefisso lungo peggiora: occupa posizioni della sequenza (meno spazio per il testo vero) e cambia la distribuzione dell'attenzione in modi che l'ottimizzazione gestisce male.</p>
"""), printed=P(19))

s(20, "LoRA: l'aggiornamento a basso rango", R("""
<p>Uno strato lineare preaddestrato calcola h = W<sub>0</sub>x. LoRA aggiunge un ramo in parallelo:</p>
<span class="f">ΔW = (α/r) BA,   h = W<sub>0</sub>x + (α/r) BAx = (W<sub>0</sub> + (α/r) BA) x</span>
<span class="f">B ∈ ℝ<sup>d<sub>out</sub>×r</sup>,   A ∈ ℝ<sup>r×d<sub>in</sub></sup></span>
<ul>
<li>W<sub>0</sub> è <b>congelata</b>; A e B sono <b>addestrabili</b>.</li>
<li>r è il <b>rango</b>: A comprime x da d<sub>in</sub> a r numeri, B li riporta a d<sub>out</sub>. Il prodotto BA è una matrice d<sub>out</sub>×d<sub>in</sub> di rango al massimo r.</li>
<li>α è un fattore di scala fisso: α/r regola quanto pesa l'aggiornamento.</li>
</ul>
<p>La figura (dall'articolo): a sinistra il blocco blu dei pesi preaddestrati (disegnato quadrato, d×d), a destra i due trapezi arancioni A (inizializzata gaussiana) e B (inizializzata a zero), con la strettoia di larghezza r. I due rami si sommano in h.</p>
<div class="box k"><b>Da saper fare: perché «basso rango»</b><p>Ogni colonna di BA è una combinazione lineare delle r colonne di B: l'immagine di ΔW è un sottospazio di dimensione ≤ r. Quindi ΔW può cambiare <b>tutte</b> le d<sub>out</sub>·d<sub>in</sub> entrate di W<sub>0</sub>, ma solo «lungo r direzioni». Esempio: d = 4, r = 1: B = (1, 2, 0, −1)<sup>T</sup>, A = (1, 0, 1, 0) danno una ΔW 4×4 con 8 entrate non nulle ma descritta da 8 numeri invece di 16, e tutte le righe proporzionali.</p></div>
<div class="box b"><b>Dal libro · {C37} § 37.3.1 e {C24} § 24.2.4</b><p>Il § 37.3.1 cita l'aggiornamento a basso rango come modo per aggiornare solo un sottospazio della matrice dei pesi: meno gradienti da tenere in memoria e una forma di regolarizzazione su «quanto» si adatta. L'idea di fattorizzare una matrice grande in due piccole è la stessa dei filtri <b>separabili</b> del § 24.2.4: un filtro k×k di rango 1 è il prodotto di un filtro verticale e uno orizzontale, 2k numeri invece di k².</p></div>
"""), printed=P(20))

s(21, "LoRA: quanti parametri si addestrano", R("""
<p>Con W<sub>0</sub> ∈ ℝ<sup>d<sub>out</sub>×d<sub>in</sub></sup>, B ∈ ℝ<sup>d<sub>out</sub>×r</sup>, A ∈ ℝ<sup>r×d<sub>in</sub></sup> (|W| = numero di elementi):</p>
<ul>
<li><b>Fine-tuning completo</b>: |W<sub>0</sub>| = d<sub>out</sub>d<sub>in</sub> pesi addestrabili.</li>
<li><b>LoRA</b>: |A| + |B| = r d<sub>in</sub> + d<sub>out</sub> r.</li>
</ul>
<span class="f">(|A| + |B|) / |W<sub>0</sub>| = r(d<sub>in</sub> + d<sub>out</sub>) / (d<sub>out</sub>d<sub>in</sub>) = r (1/d<sub>out</sub> + 1/d<sub>in</sub>)</span>
<p>La frazione cresce <b>linearmente in r</b> e cala con la dimensione della matrice: più il modello è grande, più LoRA è conveniente.</p>
<div class="box k"><b>Da saper fare: esempi</b><p>d<sub>in</sub> = d<sub>out</sub> = 768 (ViT-B), r = 4: 4 × (768 + 768) = 6144 parametri contro 589 824, cioè 4 × 2/768 ≈ 1,04%. Su W<sub>Q</sub> e W<sub>V</sub> dei 12 blocchi: 24 × 6144 = 147 456 parametri, lo 0,17% di un ViT-B/32 da 88 milioni. Con d = 12 288 (GPT-3) e r = 4: 4 × 2/12 288 ≈ 0,065% per matrice.</p></div>
"""), printed=P(21))

s(22, "LoRA: inizializzazione", R("""
<p>Le matrici si inizializzano così:</p>
<span class="f">A ∼ 𝒩(0, σ²),   B = 0   ⇒   ΔW(0) = (α/r) BA = 0</span>
<ul>
<li>All'inizio l'aggiornamento è nullo: il primo passo in avanti è <b>identico al modello preaddestrato</b>. Si parte esattamente da dove il pretraining ha lasciato, senza rumore.</li>
<li>B riceve gradienti già al primo passo di ottimizzazione.</li>
<li>Ad A i gradienti arrivano solo <b>dopo che B è cambiata</b> (la slide 23 spiega perché).</li>
</ul>
<p>Perché non entrambe a zero? Allora anche il gradiente di B sarebbe nullo (dipende da Ax = 0) e nulla si muoverebbe mai: è una simmetria da rompere. Perché non entrambe casuali? Allora ΔW ≠ 0 subito e si partirebbe da un modello «rovinato» da una perturbazione casuale.</p>
<div class="box x"><b>Approfondimento: α/r</b><p>Nell'articolo α è una costante e non viene ottimizzata: gli autori la fissano al primo valore di r che provano. Dividere per r serve a non dover ritoccare il learning rate quando si cambia rango. La libreria <code>peft</code> inizializza A con la distribuzione uniforme di Kaiming invece che gaussiana: cambia poco, l'importante è B = 0.</p></div>
"""), printed=P(22))

s(23, "LoRA: i gradienti", R("""
<p>In notazione per componenti (i = indice di uscita, j = indice di rango, k = indice di ingresso):</p>
<span class="f">h = W<sub>0</sub>x + (α/r) BAx,   h<sub>i</sub> = (W<sub>0</sub>x)<sub>i</sub> + (α/r) ∑<sub>j</sub> B<sub>ij</sub> ∑<sub>k</sub> A<sub>jk</sub>x<sub>k</sub></span>
<p><b>Gradiente rispetto a B</b>: B<sub>ij</sub> influenza solo h<sub>i</sub>, moltiplicato per (Ax)<sub>j</sub>:</p>
<span class="f">∂ℒ/∂B<sub>ij</sub> = (α/r) (∂ℒ/∂h<sub>i</sub>) (Ax)<sub>j</sub>   ⇒   ∂ℒ/∂B = (α/r) (∂ℒ/∂h) (Ax)<sup>T</sup></span>
<p><b>Gradiente rispetto ad A</b>: A<sub>jk</sub> influenza tutte le uscite passando per B:</p>
<span class="f">∂ℒ/∂A<sub>jk</sub> = (α/r) ∑<sub>i</sub> (∂ℒ/∂h<sub>i</sub>) B<sub>ij</sub> x<sub>k</sub>   ⇒   ∂ℒ/∂A = (α/r) B<sup>T</sup> (∂ℒ/∂h) x<sup>T</sup></span>
<p>All'inizializzazione B = 0, quindi:</p>
<span class="f">∂ℒ/∂A = 0,   ∂ℒ/∂B ≠ 0 in generale</span>
<p>Le formule sono corrette. ∂ℒ/∂B non è nullo perché A è casuale, quindi Ax ≠ 0. Al primo passo si muove solo B; dal secondo B ≠ 0 e anche A riceve gradiente.</p>
<div class="box k"><b>Da saper fare: verificare con le dimensioni</b><p>∂ℒ/∂h è d<sub>out</sub>×1 e (Ax)<sup>T</sup> è 1×r: il prodotto è d<sub>out</sub>×r, come B. B<sup>T</sup> è r×d<sub>out</sub>, ∂ℒ/∂h è d<sub>out</sub>×1, x<sup>T</sup> è 1×d<sub>in</sub>: il prodotto è r×d<sub>in</sub>, come A. Con un batch si sommano i contributi dei singoli esempi. È la regola dello strato lineare della backpropagation (∂ℒ/∂W = (∂ℒ/∂h) x<sup>T</sup>) applicata due volte.</p></div>
<div class="box b"><b>Dal libro · {C14}</b><p>Il capitolo sulla backpropagation ricava la stessa regola per uno strato lineare: il gradiente dei pesi è il prodotto esterno fra il gradiente che arriva dall'uscita e l'ingresso dello strato. LoRA è una catena di due strati lineari senza non linearità in mezzo (prima A, poi B).</p></div>
"""), printed=P(23))

s(24, "LoRA negli strati transformer", R("""
<p>Per una matrice di token X ∈ ℝ<sup>N×d</sup> (N token, ognuno una riga di dimensione d) l'attenzione calcola</p>
<span class="f">Q = XW<sub>Q</sub><sup>T</sup>,  K = XW<sub>K</sub><sup>T</sup>,  V = XW<sub>V</sub><sup>T</sup></span>
<p>LoRA può adattare tutte e quattro le proiezioni dell'attenzione:</p>
<span class="f">W<sub>Q</sub>′ = W<sub>Q</sub> + (α/r) B<sub>Q</sub>A<sub>Q</sub>, … , W<sub>O</sub>′ = W<sub>O</sub> + (α/r) B<sub>O</sub>A<sub>O</sub></span>
<ul>
<li>Ogni matrice adattata ha la <b>sua coppia</b> A, B.</li>
<li>Si possono adattare anche solo alcune proiezioni, o le matrici dell'MLP.</li>
</ul>
<p>Qui i token sono righe, quindi si scrive XW<sup>T</sup>: è lo stesso strato lineare h = Wx applicato a ogni token. W<sub>O</sub> è la proiezione d'uscita che rimescola le teste dopo l'attenzione (<a href="#L17">L17</a>). In Hugging Face queste matrici si chiamano <code>q_proj</code>, <code>k_proj</code>, <code>v_proj</code>, <code>out_proj</code>: sono i nomi che userai nel <a href="#L26">lab</a>.</p>
<div class="box b"><b>Dal libro · {C26}, § 26.6</b><p>Query, chiavi e valori sono proiezioni lineari dei token con matrici apprese condivise fra i token. Adattare W<sub>Q</sub> e W<sub>K</sub> cambia <b>chi guarda chi</b> (le mappe di attenzione), adattare W<sub>V</sub> e W<sub>O</sub> cambia <b>cosa viene trasportato</b> da un token all'altro.</p></div>
"""), printed=P(24))

s(25, "LoRA: quali proiezioni adattare?", R("""
<p>GPT-3 175B con un <b>budget fisso</b> di parametri LoRA (18 milioni): più matrici si adattano, più basso dev'essere il rango di ciascuna.</p>
<table>
<tr><th>matrici adattate</th><th>r</th><th>WikiSQL</th><th>MultiNLI-m</th></tr>
<tr><td>W<sub>Q</sub></td><td>8</td><td>70,4</td><td>91,0</td></tr>
<tr><td>W<sub>K</sub></td><td>8</td><td>70,0</td><td>90,8</td></tr>
<tr><td>W<sub>V</sub></td><td>8</td><td>73,0</td><td>91,0 (la slide dice 91,5)</td></tr>
<tr><td>W<sub>O</sub></td><td>8</td><td>73,2</td><td>91,3</td></tr>
<tr><td>W<sub>Q</sub>, W<sub>K</sub></td><td>4</td><td>71,4</td><td>91,3</td></tr>
<tr><td>W<sub>Q</sub>, W<sub>V</sub></td><td>4</td><td>73,7</td><td>91,3</td></tr>
<tr><td>W<sub>Q</sub>, W<sub>K</sub>, W<sub>V</sub>, W<sub>O</sub></td><td>2</td><td>73,7</td><td>91,7</td></tr>
</table>
<ul>
<li>A parità di budget, <b>adattare più proiezioni</b> con rango più basso va meglio che una sola con rango alto.</li>
<li>Il sottoinsieme migliore dipende dal compito. W<sub>Q</sub> o W<sub>K</sub> da sole sono le scelte peggiori.</li>
</ul>
<div class="box w"><b>Attenzione: un numero sbagliato</b><p>Nella tabella 5 dell'articolo di LoRA (Hu et al., 2022) la riga W<sub>V</sub> ha MultiNLI <b>91,0</b>, non 91,5. Con 91,5 sembrerebbe che W<sub>V</sub> da sola batta W<sub>O</sub> e le coppie su MultiNLI, il che non è vero. Le altre cifre coincidono con l'articolo.</p></div>
"""), printed=P(25))

s(26, "LoRA: la scelta del rango", R("""
<p>Stesse matrici, rango diverso (tabella 6 dell'articolo, GPT-3 175B). I numeri della slide coincidono con l'articolo.</p>
<table>
<tr><th></th><th>matrici</th><th>r=1</th><th>r=2</th><th>r=4</th><th>r=8</th><th>r=64</th></tr>
<tr><td>WikiSQL</td><td>W<sub>Q</sub></td><td>68,8</td><td>69,6</td><td>70,5</td><td>70,4</td><td>70,0</td></tr>
<tr><td></td><td>W<sub>Q</sub>, W<sub>V</sub></td><td>73,4</td><td>73,3</td><td>73,7</td><td>73,8</td><td>73,5</td></tr>
<tr><td></td><td>tutte e 4</td><td>74,1</td><td>73,7</td><td>74,0</td><td>74,0</td><td>73,9</td></tr>
<tr><td>MultiNLI</td><td>W<sub>Q</sub></td><td>90,7</td><td>90,9</td><td>91,1</td><td>90,7</td><td>90,7</td></tr>
<tr><td></td><td>W<sub>Q</sub>, W<sub>V</sub></td><td>91,3</td><td>91,4</td><td>91,3</td><td>91,6</td><td>91,4</td></tr>
<tr><td></td><td>tutte e 4</td><td>91,2</td><td>91,7</td><td>91,7</td><td>91,5</td><td>91,4</td></tr>
</table>
<ul>
<li>Ranghi piccoli (perfino <b>r = 1</b>) eguagliano ranghi grandi in questi esperimenti: r = 64 non aiuta.</li>
<li>Conta <b>quali matrici</b> si adattano tanto quanto il rango: le righe differiscono più delle colonne.</li>
</ul>
<p>È l'evidenza sperimentale dell'ipotesi della slide 17: l'aggiornamento utile ha rango intrinseco basso. L'articolo lo verifica anche confrontando i sottospazi appresi con r = 8 e r = 64: le prime direzioni coincidono, le altre sono quasi rumore.</p>
"""), printed=P(26))

s(27, "LoRA: merge per l'inferenza", R("""
<p>Finito l'addestramento si somma l'aggiornamento alla matrice preaddestrata:</p>
<span class="f">W<sub>merged</sub> = W<sub>0</sub> + (α/r) BA,   h = W<sub>merged</sub> x</span>
<ul>
<li><b>Merged</b>: nessuna moltiplicazione in più in inferenza; il modello ha esattamente la forma e la velocità dell'originale.</li>
<li><b>Unmerged</b>: si tengono gli adapter separati, uno per compito.</li>
<li>Adapter diversi condividono lo <b>stesso backbone</b>: per cambiare compito si sottrae un BA e se ne somma un altro, oppure si tiene W<sub>0</sub> in memoria e si caricano solo i piccoli A, B.</li>
</ul>
<p>Questo è il vantaggio decisivo rispetto agli adapter di Houlsby (slide 18): la non linearità σ dentro l'adapter impedisce di fonderlo in W<sub>0</sub>, mentre BA è lineare e si somma.</p>
<div class="box k"><b>Da saper fare</b><p>Perché un adapter Houlsby non si può fondere? h + W<sub>up</sub>σ(W<sub>down</sub>h) non è della forma Mh per nessuna matrice M, a causa di σ. Con LoRA invece W<sub>0</sub>x + (α/r)BAx = (W<sub>0</sub> + (α/r)BA)x per ogni x.</p></div>
"""), printed=P(27))

s(28, "LoRA: i requisiti di memoria", R("""
<table>
<tr><th>componente di memoria</th><th>con LoRA</th></tr>
<tr><td>pesi preaddestrati</td><td>ancora salvati</td></tr>
<tr><td>gradienti dei pesi preaddestrati</td><td>non salvati</td></tr>
<tr><td>stati dell'ottimizzatore per i pesi preaddestrati</td><td>non salvati</td></tr>
<tr><td>gradienti e stati dell'ottimizzatore di LoRA</td><td>salvati</td></tr>
<tr><td>checkpoint per compito</td><td>solo i piccoli pesi dell'adapter</td></tr>
<tr><td>memoria delle attivazioni</td><td>ancora necessaria per la backpropagation</td></tr>
</table>
<p>Riprendendo il conto della slide 6: dei 16 byte per parametro, con LoRA restano i 4 dei pesi congelati; i 12 di gradienti e Adam si pagano solo sui parametri di LoRA.</p>
<p>L'ultima riga è importante: per calcolare il gradiente di A e B serve propagare il gradiente <b>attraverso</b> tutti gli strati congelati che stanno sopra, quindi le attivazioni intermedie vanno salvate come nel fine-tuning normale. LoRA riduce la memoria dei parametri, non quella delle attivazioni.</p>
"""), printed=P(28))

s(29, "LoRA: risultati sperimentali", R("""
<p>Tabella 4 dell'articolo, GPT-3 175B. WikiSQL e MNLI-m: accuratezza; <b>SAMSum</b> (riassunto di dialoghi): ROUGE-1/2 e ROUGE-L (sovrapposizione di parole con il riassunto di riferimento).</p>
<table>
<tr><th>metodo</th><th>parametri addestrabili</th><th>WikiSQL</th><th>MNLI-m</th><th>SAMSum R1/R2</th><th>RL</th></tr>
<tr><td>Fine-tuning completo</td><td>175 255,8M</td><td>73,8</td><td>89,5</td><td>52,0/28,0</td><td>44,5</td></tr>
<tr><td>BitFit</td><td>14,2M</td><td>71,3</td><td>91,0</td><td>51,3/27,4</td><td>43,5</td></tr>
<tr><td>PreEmbed</td><td>3,2M</td><td>63,1</td><td>88,6</td><td>48,3/24,2</td><td>40,5</td></tr>
<tr><td>PreLayer</td><td>20,2M</td><td>70,1</td><td>89,5</td><td>50,8/27,3</td><td>43,5</td></tr>
<tr><td>Adapter<sup>H</sup></td><td>7,1M</td><td>71,9</td><td>89,8</td><td>53,0/28,9</td><td>44,8</td></tr>
<tr><td>Adapter<sup>H</sup></td><td>40,1M</td><td>73,2</td><td>91,5</td><td>53,2/29,0</td><td>45,1</td></tr>
<tr><td><b>LoRA</b></td><td><b>4,7M</b></td><td>73,4</td><td><b>91,7</b></td><td><b>53,8/29,8</b></td><td><b>45,9</b></td></tr>
<tr><td><b>LoRA</b></td><td>37,7M</td><td><b>74,0</b></td><td>91,6</td><td>53,4/29,2</td><td>45,1</td></tr>
</table>
<ul>
<li>LoRA con <b>4,7 milioni</b> di parametri addestrabili (0,003% di 175 miliardi) è paragonabile al fine-tuning completo: un po' sotto su WikiSQL, sopra su MNLI e SAMSum.</li>
<li>Salendo a 37,7M migliora WikiSQL in questo esperimento.</li>
</ul>
<p>I numeri coincidono con l'articolo. Il checkpoint per compito passa da circa 350 GB (175 miliardi di parametri in 16 bit) a pochi MB.</p>
"""), printed=P(29))

s(30, "QLoRA: Quantized Low-Rank Adaptation", R("""
<p><b>QLoRA</b> (Dettmers et al., 2023) riduce anche i 4 byte per parametro dei pesi congelati, che LoRA lasciava intatti:</p>
<span class="f">h = dequant(W<sub>NF4</sub>) x + (α/r) BAx</span>
<ul>
<li>I pesi preaddestrati congelati sono salvati <b>quantizzati a 4 bit</b> nel formato NF4.</li>
<li>Al momento del calcolo vengono <b>dequantizzati</b> a una precisione più alta (per esempio BF16) per la moltiplicazione.</li>
<li>Si addestrano solo i parametri LoRA (in 16 bit), senza aggiornare il backbone quantizzato. Il gradiente attraversa i pesi dequantizzati per arrivare ad A e B.</li>
</ul>
<p>La figura confronta tre colonne: fine-tuning completo (modello a 16 bit, stati dell'ottimizzatore a 32 bit per tutti i pesi), LoRA (modello a 16 bit, adapter e stati solo per gli adapter), QLoRA (modello a 4 bit, adapter a 16 bit, e frecce verso la CPU per il <i>paging</i> degli stati dell'ottimizzatore). Il risultato reso famoso dall'articolo: il fine-tuning di un modello da 65 miliardi di parametri su una sola GPU da 48 GB.</p>
"""), printed=P(30))

s(31, "QLoRA: ottimizzazioni di memoria", R("""
<ul>
<li><b>NF4</b> (NormalFloat a 4 bit): 16 livelli di quantizzazione scelti per pesi distribuiti circa come una <b>gaussiana</b>. Invece di livelli equispaziati, si usano i quantili della normale: più livelli vicino a zero, dove cadono quasi tutti i pesi.</li>
<li><b>Double quantization</b>: anche le costanti di scala usate per quantizzare (una per blocco di pesi) vengono quantizzate, risparmiando ancora qualche decimo di bit per parametro.</li>
<li><b>Paged optimizers</b>: si usa la memoria unificata CPU/GPU per gestire i picchi di memoria degli stati dell'ottimizzatore, spostandoli sulla CPU quando la GPU è piena.</li>
</ul>
<span class="f">W<sub>NF4</sub> (salvati in 4 bit) → dequantizza → W<sub>compute</sub> (operazioni in precisione più alta)</span>
<div class="box k"><b>Da saper fare: perché i quantili</b><p>Con 4 bit hai 16 valori possibili. Se i pesi sono ~𝒩(0, σ²) e scegli 16 livelli equispaziati fra −max e +max, la maggior parte dei livelli estremi resta quasi inutilizzata. Scegliendo i livelli in modo che ogni intervallo contenga la stessa probabilità, ogni codice è usato con la stessa frequenza: è l'idea di NF4 (ogni blocco di pesi viene prima normalizzato dividendo per il suo massimo assoluto, la «costante di scala»).</p></div>
"""), printed=P(31))

s(32, "DoRA: Weight-Decomposed Low-Rank Adaptation", R("""
<p><b>DoRA</b> (Liu et al., 2024) separa ogni matrice in <b>modulo</b> e <b>direzione</b> delle sue colonne:</p>
<span class="f">W = V diag(m / ‖V‖<sub>col</sub>),   m<sub>j</sub> = ‖W<sub>:,j</sub>‖<sub>2</sub></span>
<ul>
<li>m ∈ ℝ<sup>d<sub>in</sub></sup> controlla la <b>lunghezza</b> di ciascuna colonna.</li>
<li>V determina la <b>direzione</b> delle colonne.</li>
<li>La normalizzazione è per colonna: ‖V‖<sub>col</sub> è il vettore delle norme delle colonne di V, e diag(m/‖V‖<sub>col</sub>) riscala ogni colonna j di V in modo che abbia norma m<sub>j</sub>.</li>
</ul>
<p>Nella figura: a sinistra la decomposizione del peso preaddestrato in modulo m = ‖W<sub>0</sub>‖<sub>c</sub> e direzione V = W<sub>0</sub>; durante l'adattamento la direzione riceve un aggiornamento LoRA (ΔV = BA) e il modulo m è addestrato direttamente; a destra il merge in un'unica W′.</p>
<p>La motivazione dell'articolo: analizzando come cambiano modulo e direzione dei pesi, il fine-tuning completo e LoRA si comportano in modo diverso (LoRA tende a cambiarli insieme, in proporzione); separarli rende LoRA più simile al fine-tuning completo.</p>
"""), printed=P(32))

s(33, "DoRA: aggiornamenti a basso rango della direzione", R("""
<p>LoRA si applica alla <b>direzione</b>:</p>
<span class="f">V = W<sub>0</sub> + (α/r) BA,   W′ = V diag(m / ‖V‖<sub>col</sub>)</span>
<ul>
<li>W<sub>0</sub> congelata.</li>
<li>Si addestrano A, B e il vettore dei moduli m (d<sub>in</sub> numeri in più per matrice).</li>
<li>A differenza di LoRA, i moduli delle colonne sono adattati <b>esplicitamente</b>.</li>
</ul>
<p>All'inizio B = 0 e m = ‖W<sub>0</sub>‖<sub>col</sub>, quindi W′ = W<sub>0</sub>: come LoRA, si parte dal modello preaddestrato. Anche DoRA si può fondere in una sola matrice dopo l'addestramento; durante il training però costa di più, perché a ogni passo bisogna calcolare le norme delle colonne di V.</p>
<div class="box k"><b>Da saper fare</b><p>W<sub>0</sub> = [[3, 0], [4, 1]] (colonne (3, 4) e (0, 1)): m = (5, 1). Se il training porta m a (10, 1) senza toccare la direzione, la prima colonna diventa (6, 8): stessa direzione, lunghezza doppia. LoRA da solo, per ottenere questo, dovrebbe imparare ΔW = [[3, 0], [4, 0]].</p></div>
"""), printed=P(33))

s(34, "AdaLoRA: allocazione adattiva del rango", R("""
<p><b>AdaLoRA</b> (Zhang et al., 2023) usa una parametrizzazione simile alla SVD:</p>
<span class="f">ΔW = PΛQ,   Λ = diag(λ<sub>1</sub>, …, λ<sub>r</sub>)</span>
<ul>
<li>P e Q fanno da vettori singolari (con una penalità che li spinge a restare ortogonali), λ<sub>i</sub> da valori singolari.</li>
<li>Durante il training si stima l'<b>importanza</b> di ogni componente a basso rango.</li>
<li>Si <b>potano</b> le componenti meno importanti (si azzera il loro λ), così il rango finale è <b>diverso</b> da strato a strato.</li>
</ul>
<p>La mappa di calore mostra i ranghi finali (da 0 a 12) per ogni matrice (W<sub>q</sub>, W<sub>k</sub>, W<sub>v</sub>, W<sub>o</sub> dell'attenzione e W<sub>f1</sub>, W<sub>f2</sub> dell'MLP) in ognuno dei 12 strati: gli strati alti e le matrici dell'MLP W<sub>f1</sub> ricevono rango alto, i primi strati e W<sub>q</sub> rango basso. Con LoRA standard tutte le celle avrebbero lo stesso r.</p>
<p>Perché la forma PΛQ e non BA? Per potare un rango in BA bisognerebbe togliere una colonna di B e una riga di A, ma le direzioni di BA non sono separate per importanza; con Λ diagonale ogni componente ha il suo «interruttore» λ<sub>i</sub>.</p>
"""), printed=P(34))

s(35, "VeRA: Vector-based Random Matrix Adaptation", R("""
<p><b>VeRA</b> (Kopiczko et al., 2024) riduce ancora i parametri: le matrici a basso rango sono <b>casuali, congelate e condivise fra tutti gli strati</b>; si imparano solo due vettori di scala per strato:</p>
<span class="f">ΔW = diag(b) B diag(d) A,   b ∈ ℝ<sup>d<sub>out</sub></sup>,  d ∈ ℝ<sup>r</sup></span>
<ul>
<li>A e B: generate una volta da un seme casuale e mai addestrate (in blu, «shared across layers»).</li>
<li>d riscala ciascuna delle r direzioni casuali, b riscala ciascuna uscita. Sono gli unici parametri addestrabili (in arancione).</li>
<li>Inizializzazione: b = 0 (così ΔW = 0 all'inizio), d = costante.</li>
</ul>
<p>Confronto con LoRA per una matrice d×d: LoRA addestra 2rd numeri, VeRA d + r. Per questo VeRA può permettersi un <b>rango molto più alto</b> (per esempio 256) a parità o sotto di parametri: le direzioni non si imparano, si scelgono fra tante direzioni casuali dando loro un peso.</p>
<p>Per salvare un adapter VeRA basta salvare b, d e il seme: le matrici casuali si rigenerano.</p>
"""), printed=P(35))

# ===================== LoRA PER LA VISIONE =====================

s(36, "LoRA for Computer Vision", R("""<p>Divisoria della terza parte: LoRA applicato a ViT, segmentazione, convoluzioni, adattamento di dominio e VLM.</p>"""),
  kind='div', sec=("l25-cv", "Parte 3 · LoRA in visione e sintesi", "slide 36–47"), printed='')

s(37, "LoRA per i Vision Transformer", R("""
<p>Le proiezioni dell'attenzione in un ViT, con X ∈ ℝ<sup>N×D</sup> (N token delle patch più il [CLS], <a href="#L17">L17</a>):</p>
<span class="f">Q = XW<sub>Q</sub><sup>T</sup>,  K = XW<sub>K</sub><sup>T</sup>,  V = XW<sub>V</sub><sup>T</sup></span>
<p>LoRA modifica alcune di queste matrici:</p>
<span class="f">W<sub>i</sub>′ = W<sub>i</sub> + (α/r) B<sub>i</sub>A<sub>i</sub>,   i ∈ {Q, K, V, O}</span>
<ul>
<li>I pesi del ViT preaddestrato restano congelati.</li>
<li>Si addestrano solo le matrici a basso rango A<sub>i</sub>, B<sub>i</sub> (più la testa del compito).</li>
<li>LoRA si può applicare anche alle proiezioni dell'MLP.</li>
</ul>
<p>È esattamente la ricetta della slide 24: un ViT è un transformer su token di patch, quindi LoRA si applica senza cambiare nulla. Nel <a href="#L26">lab</a> lo fai sull'encoder visivo di CLIP (ViT-B/32) con <code>target_modules=['q_proj', 'v_proj']</code>.</p>
"""), printed=P(37))

s(38, "LoRA per i ViT: confronto con altri metodi PEFT", R("""
<p>Grafico dall'articolo di NOAH (Zhang et al., 2022): punteggio medio su VTAB-1k (ViT-B/16 preaddestrato su ImageNet-21k) per i tre gruppi.</p>
<table>
<tr><th></th><th>VPT</th><th>Adapter</th><th>LoRA</th><th>NOAH</th></tr>
<tr><td>Natural</td><td>78,5</td><td>79,0</td><td>79,5</td><td>80,2</td></tr>
<tr><td>Specialized</td><td>82,4</td><td>84,1</td><td>84,6</td><td>84,9</td></tr>
<tr><td>Structured</td><td>55,0</td><td>58,5</td><td>60,5</td><td>61,3</td></tr>
</table>
<ul>
<li>LoRA supera VPT e gli adapter standard in tutti e tre i gruppi.</li>
<li><b>NOAH</b> (Neural prOmpt seArcH) combina più meccanismi (adapter, LoRA, VPT) scegliendo con una ricerca automatica dell'architettura quanto usarne in ogni strato, e ottiene i valori più alti.</li>
</ul>
<p>Attenzione alla scala: le barre partono da 77, 80 e 50, quindi le differenze sembrano più grandi di quanto sono (1–2 punti su Natural e Specialized, di più su Structured).</p>
"""), printed=P(38))

s(39, "LoRA per la segmentazione medica: SAMed", R("""
<p><b>SAMed</b> (Zhang e Liu, 2023): adattare l'image encoder di <b>SAM</b> alla segmentazione di immagini mediche (nella figura una TAC addominale con gli organi colorati).</p>
<ul>
<li><b>Ingresso</b>: immagini mediche 2D invece di foto naturali.</li>
<li><b>Adattamento</b>: LoRA sulle proiezioni <b>query e value</b> di ogni blocco dell'encoder.</li>
<li><b>Uscita</b>: le maschere di segmentazione dal mask decoder.</li>
<li>I pesi dell'image encoder preaddestrato restano congelati.</li>
</ul>
<p>Nella figura, oltre ai «LoRA layers» sotto i blocchi congelati, sono marcati come addestrati (fiamma) anche il <b>prompt encoder</b> e il <b>mask decoder</b>, che sono piccoli. Il prompt usato è un embedding di default appreso: SAMed segmenta tutti gli organi senza che un medico clicchi dei punti. La scelta di Q e V è quella raccomandata dall'articolo di LoRA (slide 25).</p>
"""), printed=P(39))

s(40, "Conv-LoRA: adattamento spaziale", R("""
<p>Problema: LoRA lavora token per token (è uno strato lineare applicato a ogni token separatamente), quindi l'aggiornamento non ha alcuna nozione di <b>vicinato spaziale</b>. Per segmentare servono invece dettagli locali, che i ViT preaddestrati (come SAM) catturano poco.</p>
<p><b>Conv-LoRA</b> (Zhong et al., 2024) inserisce un modulo convoluzionale fra A e B:</p>
<span class="f">h = W<sub>0</sub>x + (α/r) B · MoEConv(Ax)</span>
<ul>
<li>A riduce i canali al rango r; B li riporta alla dimensione di uscita.</li>
<li>Nello spazio piccolo di dimensione r i token vengono rimessi a griglia e passano per <b>MoEConv</b>: una <i>mixture of experts</i> convoluzionale, in cui un piccolo selettore (gating) sceglie quale «esperto» usare.</li>
<li>Ogni esperto lavora a una <b>scala spaziale</b> diversa: ridimensiona la mappa (interpolazione), applica una convoluzione 3×3, e torna alla risoluzione originale.</li>
</ul>
<p>La figura confronta (a) LoRA, encoder A e decoder B addestrabili accanto ai pesi congelati, e (b) Conv-LoRA con il blocco MoE-Conv in mezzo. Il costo resta piccolo perché le convoluzioni lavorano su r canali, non su d.</p>
"""), printed=P(40))

s(41, "SemLA: una libreria di LoRA per dominio", R("""
<p><b>Compito</b>: segmentazione semantica <i>open-vocabulary</i> (classi date a parole, come in CLIP) sotto <b>domain shift</b>, cioè quando le immagini di test hanno un aspetto diverso da quelle di training. Esempio: scene stradali con pioggia, nebbia o di notte.</p>
<ul>
<li>Si parte dallo stesso modello di segmentazione preaddestrato per ogni dominio.</li>
<li>Si addestra un <b>adapter LoRA separato</b> su ogni dominio sorgente: ΔW<sub>i</sub> = B<sub>i</sub>A<sub>i</sub>, i = 1, …, M, con M il numero di domini.</li>
<li>Per ogni dominio si calcola il <b>centroide</b> degli embedding CLIP delle sue immagini e lo si salva insieme al suo LoRA.</li>
</ul>
<p>Il risultato è una «biblioteca» di adapter indicizzata nello spazio di CLIP: ogni libro (adapter) ha come etichetta il punto medio delle immagini su cui è stato addestrato.</p>
"""), printed=P(41))

s(42, "SemLA: recupero e fusione dei LoRA", R("""
<p>Per un'immagine di test x:</p>
<ol>
<li>si estrae il suo <b>embedding CLIP</b>;</li>
<li>si recuperano i <b>k adapter</b> di dominio più simili (centroide più vicino);</li>
<li>si combinano i loro aggiornamenti:</li>
</ol>
<span class="f">ΔW(x) = ∑<sub>i=1</sub><sup>k</sup> w<sub>i</sub>(x) B<sub>i</sub>A<sub>i</sub></span>
<ul>
<li>w<sub>i</sub>(x): peso basato sulla similarità per l'adapter i (per esempio una softmax delle similarità coseno).</li>
<li>L'aggiornamento è <b>specifico dell'immagine</b>: una foto con pioggia e un po' di buio pesca dagli adapter «pioggia» e «notte».</li>
<li><b>Nessun aggiornamento dei gradienti</b> in inferenza: si fanno solo somme pesate di matrici già addestrate.</li>
</ul>
<p>Nella figura: la bussola di CLIP posiziona la foto nello spazio, la «LoRA fusion weighted on proximity» combina i libri vicini in un LoRA su misura per quell'immagine, che si applica al modello. Nel <a href="#L26">lab</a> ne fai una versione semplificata su classificazione con nebbia, pioggia e notte sintetiche.</p>
"""), printed=P(42))

s(43, "Vision as LoRA (VoRA)", R("""
<p><b>VoRA</b> (Wang et al., 2025) affronta i VLM della <a href="#L24">L24</a> da un'altra parte. Un MLLM classico (figura a) è «encoder-based»: patch → embedding → <b>ViT</b> → <b>connettore</b> → LLM, come LLaVA. VoRA (figura b) <b>toglie il ViT</b>:</p>
<ul>
<li>Integra l'elaborazione visiva <b>dentro</b> un modello di linguaggio preaddestrato.</li>
<li>Introduce un embedding delle patch e moduli <b>LoRA specifici per la visione</b> negli strati dell'LLM.</li>
<li>Riusa i pesi dell'LLM congelati.</li>
<li>Distilla le feature visive da un <b>ViT insegnante</b> preaddestrato (slide 44).</li>
<li>In inferenza <b>non serve un encoder ViT separato</b>: le patch vanno direttamente nell'LLM.</li>
</ul>
<p>Il vantaggio: un'unica rete, che accetta immagini a risoluzione qualsiasi senza i vincoli del ViT, e i LoRA visivi si possono fondere nell'LLM.</p>
"""), printed=P(43))

s(44, "VoRA: distillazione blocco per blocco", R("""
<p>Per insegnare all'LLM a «vedere», si allineano le sue rappresentazioni visive intermedie a quelle di un ViT insegnante:</p>
<span class="f">ℒ<sub>distill</sub><sup>i</sup> = (1/S) ∑<sub>s=1</sub><sup>S</sup> [1 − cos(g<sub>i</sub>(h<sub>llm</sub><sup>i,s</sup>), h<sub>vit</sub><sup>i,s</sup>)]</span>
<ul>
<li>i: blocco transformer scelto; s: indice del token visivo.</li>
<li>S: numero di token visivi allineati; g<sub>i</sub>: una testa di proiezione ausiliaria (porta la dimensione dell'LLM a quella del ViT).</li>
<li>1 − cos vale 0 se i vettori puntano nella stessa direzione e 2 se opposti: la loss spinge ogni token dell'LLM ad avere la stessa direzione del token corrispondente del ViT.</li>
<li>Si addestrano i moduli di adattamento visivo (LoRA, embedding) e le teste ausiliarie.</li>
<li>La distillazione si combina con l'obiettivo di <b>language modeling</b> (prevedere il token successivo del testo).</li>
</ul>
<p>Nella figura, durante il pretraining il ViT congelato produce i bersagli e la «cosine loss»; in inferenza (b) restano solo l'LLM con i LoRA e il tokenizer.</p>
<div class="box b"><b>Dal libro · {C37}, § 37.4 Learning from a Teacher</b><p>Il libro distingue due modi di imparare da un insegnante: imitarne le <b>uscite</b> (la knowledge distillation classica, § 37.4.1, dove lo studente copia la distribuzione di probabilità del maestro) oppure imitarne le <b>attivazioni intermedie</b>, cioè come elabora l'ingresso. VoRA fa la seconda cosa, strato per strato.</p></div>
"""), printed=P(44))

s(45, "Confronto fra i metodi PEFT", R("""
<table>
<tr><th>metodo</th><th>componenti addestrabili</th><th>cosa modifica</th></tr>
<tr><td>BitFit</td><td>vettori di bias</td><td>parametri esistenti</td></tr>
<tr><td>Adapter a collo di bottiglia</td><td>proiezioni down/up</td><td>modulo residuo sulle feature</td></tr>
<tr><td>Prompt / VPT</td><td>embedding di prompt</td><td>token d'ingresso aggiuntivi</td></tr>
<tr><td>Prefix tuning</td><td>chiavi e valori</td><td>contesto aggiuntivo dell'attenzione</td></tr>
<tr><td>LoRA</td><td>matrici a basso rango A, B</td><td>aggiornamento dei pesi BA</td></tr>
<tr><td>QLoRA</td><td>matrici LoRA</td><td>backbone congelato quantizzato</td></tr>
<tr><td>DoRA</td><td>A, B, moduli delle colonne</td><td>direzione e modulo</td></tr>
<tr><td>AdaLoRA</td><td>fattori a basso rango tipo SVD</td><td>rango variabile per strato</td></tr>
<tr><td>VeRA</td><td>vettori di scala</td><td>proiezioni casuali condivise</td></tr>
</table>
<div class="box k"><b>Da saper fare: tre domande per classificare un metodo</b><p>(1) <b>Dove</b> interviene: sui pesi (BitFit, LoRA e varianti), sulle feature (adapter), sull'ingresso o sul contesto (prompt, prefix)? (2) Si può <b>fondere</b> nel modello dopo il training senza costo in inferenza? Sì per BitFit, LoRA, DoRA, AdaLoRA, VeRA; no per adapter (non linearità) e prompt/prefix (allungano la sequenza). (3) Cosa costa in <b>memoria</b>: solo QLoRA riduce anche i pesi congelati.</p></div>
"""), printed=P(45))

s(46, "Summary", R("""
<ul>
<li>Il PEFT riduce il numero di parametri addestrabili mantenendo i pesi preaddestrati.</li>
<li>LoRA rappresenta l'aggiornamento dei pesi come <b>prodotto di matrici a basso rango</b>.</li>
<li>QLoRA riduce la memoria del backbone; DoRA e AdaLoRA cambiano la parametrizzazione dell'aggiornamento.</li>
<li>In visione LoRA si usa per adattare ViT, per la segmentazione e per i vision-language model.</li>
</ul>
"""), printed=P(46))

s(47, "Next Lectures", R("""
<ul>
<li><b>Lab</b>: Vision-Language Models e PEFT (la <a href="#L26">L26</a> di questo sito: CLIP, zero-shot, linear probe, LoRA e varianti con la libreria <code>peft</code>, fusione alla SemLA).</li>
<li>Modelli di <b>diffusione</b> per generare immagini e video.</li>
<li>Modelli di diffusione <b>personalizzati</b>: Textual Inversion, DreamBooth e ancora LoRA.</li>
</ul>
"""), printed=P(47))

s(48, "Pagina panoramica (non è una slide)", R("""
<p>Pagina generata automaticamente da Beamer con le miniature delle slide 1–47: non contiene niente di nuovo.</p>
"""), printed=P(48))
