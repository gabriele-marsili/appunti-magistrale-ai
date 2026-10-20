VB = 'https://visionbook.mit.edu/'
def L(slug, txt): return f'<a href="{VB}{slug}" target="_blank">{txt}</a>'
C24 = L('convolutional_neural_nets.html', 'cap. 24')
C12 = L('neural_nets.html', 'cap. 12')
C13 = L('neural_nets_as_distribution_transformers.html', 'cap. 13')
C11 = L('problem_of_generalization.html', 'cap. 11')

# ===================== INTRODUZIONE =====================

s(1, "Convolutional Neural Networks: copertina", """
<p>Lezione del 19 ottobre 2026 sulle <b>reti neurali convoluzionali</b> (CNN). È il punto di svolta del corso: finora i filtri (Gauss, Sobel, Laplaciano, Gabor in <a href="#L5">L5</a> e <a href="#L7">L7</a>, SIFT in <a href="#L8">L8</a>) li sceglievamo noi; da qui in poi li <b>impara la rete dai dati</b>.</p>
<p>Il PDF ha 59 pagine (58 numerate più la copertina) in cinque blocchi: reti profonde in generale, componenti di base, convoluzione nelle reti, pooling e apprendimento gerarchico, architetture classiche. Riferimento del prof: visionbook <b>cap. 24</b> (slide 59).</p>
""", sec=("l15-intro", "Obiettivi e limiti dei filtri fissi", "slide 1–3"))

s(2, "Goal of the Day", """
<ul>
<li>Passare da <b>estrattori di feature statici</b> (filtri progettati a mano) a estrattori <b>appresi</b>, basati su reti neurali profonde (DNN, deep neural networks).</li>
<li>Discutere le <b>scelte di progetto</b> di una CNN: quali strati, in che ordine, con quali parametri, e perché.</li>
</ul>
""")

s(3, "Limitations of Static Feature Extractors", """
<p>I <b>filtri fatti a mano</b> (Sobel, Gabor, SIFT…) sono fissi, scelti da una persona e identici per ogni immagine e ogni dominio. Tre limiti:</p>
<ul>
<li>Si può costruire un <b>banco di filtri</b> grande, per molte orientazioni, scale e pattern (come in <a href="#L7">L7</a>), ma resta una lista piatta.</li>
<li>Non c'è un modo semplice per <b>comporre</b> i filtri in rappresentazioni <b>gerarchiche</b>, cioè feature via via più complesse e semantiche (da bordi a parti di oggetti a oggetti).</li>
<li>Tutti gli strumenti visti finora sono <b>lineari</b>: comporre filtri lineari dà ancora un filtro lineare (convoluzione associativa, <a href="#L3">L3</a>). Per feature complesse servono <b>non linearità</b>.</li>
</ul>
<p>Prezzo da pagare: si perde l'<b>interpretabilità</b>. Di un Sobel sappiamo cosa calcola; dei 512 canali di un layer profondo no.</p>
<div class="box b"><b>Dal libro · {C24}, § 24.2 Convolutional Layers</b><p>Il libro presenta lo strato convoluzionale proprio come continuazione dei capitoli sui filtri: è un banco di filtri lineari, ma i coefficienti sono parametri che si imparano invece di essere progettati (dal cap. 15 in poi i filtri li sceglievamo noi). La differenza con un banco di Gabor non è l'operazione ma da dove vengono i pesi, e il fatto che fra un banco e il successivo c'è una non linearità.</p></div>
""".replace('{C24}', C24))

# ===================== DEEP NEURAL NETWORKS =====================

s(4, "Deep Neural Networks", """<p>Divisoria: si parte dalle reti profonde in generale (slide 5–16), prima di specializzarle alle immagini.</p>""",
  kind='div', sec=("l15-dnn", "Reti neurali profonde", "slide 4–16"))

s(5, "Deep Neural Networks", """
<ul>
<li>Una <b>DNN</b> è una <b>composizione di molti strati</b>:
<span class="f">f<sub>θ</sub>(x) = f<sub>L</sub>(f<sub>L−1</sub>(… f<sub>1</sub>(x)))</span>
<ul><li><b>θ</b>: tutti i parametri (pesi e bias di tutti gli strati);</li>
<li><b>x</b>: l'ingresso, per esempio un'immagine (W, H, C) = larghezza, altezza, canali;</li>
<li>gli strati <b>alternano operazioni lineari e non lineari</b>.</li></ul></li>
<li>Si addestra con la <b>discesa stocastica del gradiente</b> (SGD):
<span class="f">θ<sub>t</sub> = θ<sub>t−1</sub> − α ∇<sub>θ</sub> L(f<sub>θ</sub>(x))</span>
<ul><li><b>L</b> è la loss: cross-entropy per la classificazione, errore quadratico medio (MSE) per la regressione;</li>
<li><b>α</b> è il learning rate (passo).</li></ul></li>
</ul>
<p><b>Figura</b> (visionbook, fig. 12.8): la foto di un airone attraversa una pila di blocchi «Linear + Nonlinearity» e all'uscita compare l'etichetta «heron».</p>
<div class="box b"><b>Dal libro · {C12}, § 12.3 e 12.5</b><p>Il mattone di quasi tutte le reti è «lineare, poi non linearità puntuale, poi lineare…»: z = W x + b, h = g(z) con g applicata elemento per elemento (§ 12.3). Senza g la pila collassa in un'unica mappa lineare. Il libro distingue le <b>attivazioni</b> (i valori x, z, h calcolati per un singolo esempio: «veloci») dai <b>parametri</b> (W, b, imparati sull'intero dataset: «lenti»), § 12.4. Nella formula di SGD si deriva rispetto ai parametri; in un attacco avversario (<a href="#L14">L14</a>) si deriva rispetto all'ingresso.</p></div>
<div class="box k"><b>Da saper fare</b>Scrivere la rete come composizione, dire cosa sono θ, L, α, e spiegare perché servono strati non lineari fra quelli lineari.</div>
""".replace('{C12}', C12))

s(6, "Recap: Simplified DNN training loop", """
<p>Il ciclo di addestramento, per ogni <b>mini-batch</b> (un piccolo gruppo di esempi, per esempio 64 immagini):</p>
<ol>
<li>applica le <b>augmentation</b> all'ingresso (ritagli, ribaltamenti, variazioni di colore: esempi «nuovi» a costo zero);</li>
<li><b>forward pass (1)</b>: calcola le uscite della rete;</li>
<li><b>forward pass (2)</b>: calcola la loss confrontando uscite ed etichette;</li>
<li><b>backward pass</b>: calcola il gradiente della loss rispetto a tutti i parametri (backpropagation, regola della catena);</li>
<li>applica l'<b>aggiornamento</b> con SGD (o una sua variante).</li>
</ol>
<p>Si ripete finché non si converge o si raggiunge una condizione di uscita (numero di epoche, loss di validazione che smette di scendere).</p>
<p>Il gradiente sul mini-batch è una stima rumorosa del gradiente sull'intero dataset: è questo che rende la discesa «stocastica».</p>
""")

s(7, "Optimization in DNN", """
<ul>
<li>Per via delle non linearità la loss è <b>non convessa</b>: non c'è alcuna garanzia formale di convergenza a un minimo globale.
<ul><li>SGD trova un minimo locale (o più in generale un punto in cui il gradiente è circa zero);</li>
<li>in pratica, con buone architetture, i minimi locali trovati sono <b>abbastanza buoni</b>.</li></ul></li>
</ul>
<p><b>Figura</b> (Li et al., NeurIPS 2018): superficie della loss di una ResNet-56 visualizzata lungo due direzioni casuali dello spazio dei pesi. (a) <b>senza skip connection</b>: paesaggio frastagliato, pieno di picchi e valli caotiche; (b) <b>con skip connection</b>: una sola conca liscia, simile a una funzione convessa.</p>
<div class="box w"><b>Attenzione: «SGD will find a local minima»</b>Oltre all'inglese («a local minimum»), l'affermazione va presa con cautela: SGD trova un punto stazionario, non per forza un minimo. Per le reti sovraparametrizzate le evidenze raccolte da Prince (<i>Understanding Deep Learning</i>, § 20.3) indicano pochi minimi locali cattivi e molti punti di sella; con etichette casuali le reti arrivano comunque a errore di training zero (§ 20.2).</div>
""")

s(8, "Optimization in DNN (2)", """
<ul>
<li>La <b>curvatura</b> della loss (la matrice hessiana, cioè le derivate seconde) dice quanto è difficile ottimizzare: un minimo <b>piatto</b> è facile da raggiungere e stabile, uno <b>aguzzo</b> (sharp) è difficile.
<ul><li>Gli ottimizzatori moderni (Adam, oppure SGD con momentum ben regolato) e vari accorgimenti di architettura servono a migliorare la convergenza;</li>
<li>esempio, la figura della slide precedente: le <b>skip connection</b> (connessioni residue, slide 50) rendono il paesaggio più piatto.</li></ul></li>
<li>Alcuni iperparametri, soprattutto il <b>learning rate</b>, vanno regolati con cura.</li>
<li><b>Regola generale</b>: non cambiare architettura o iperparametri di default senza capire e <b>misurare</b> l'effetto della modifica.</li>
</ul>
<div class="box x"><b>Approfondimento</b>Minimi piatti e generalizzazione: un minimo piatto tollera piccoli errori nei pesi e piccoli spostamenti fra la loss di training e quella di test, quindi tende a generalizzare meglio. SGD con batch piccoli e learning rate alti finisce più spesso in minimi piatti (Prince § 20.4.1–20.4.2, fig. 20.11).</div>
""")

s(9, "Design Choices in DNN Architecture", """
<p>Tre criteri per progettare uno strato o un'architettura:</p>
<ul>
<li><b>Forward pass</b>: che rappresentazione induce lo strato, cioè il suo <b>bias induttivo</b> (le ipotesi sul problema già scritte nell'architettura).
<ul><li>Le CNN sono operazioni <b>LSI</b> (lineari e invarianti alla traslazione, <a href="#L3">L3</a>): un'ipotesi forte e adatta alle immagini. Uno strato denso (fully connected) ha un bias induttivo molto debole.</li></ul></li>
<li><b>Backward pass</b>: evitare problemi di ottimizzazione come i gradienti che <b>svaniscono o esplodono</b>.
<ul><li>Esempi: inizializzazioni che mantengono le attivazioni normalizzate (per esempio He), connessioni residue.</li></ul></li>
<li><b>Costo computazionale</b>, pensato per hardware tipo GPU (molto parallelo, stile SIMD):
<ul><li>memoria;</li><li>banda fra GPU e CPU, o fra GPU in sistemi multi-GPU;</li><li>operazioni facili da parallelizzare;</li>
<li>idea: tenere la GPU al 100% durante training e inferenza, senza colli di bottiglia;</li>
<li>nei sistemi di visione embedded ci sono anche vincoli di tempo reale e latenza.</li></ul></li>
</ul>
<div class="box b"><b>Dal libro · {C12}, § 12.8 Why Are Neural Networks a Good Architecture?</b><p>Il libro elenca cinque ragioni: grande capacità (approssimatori universali), differenziabilità (si ottimizzano col gradiente), buoni bias induttivi, efficienza su hardware parallelo (moltiplicazioni di matrici e operazioni puntuali), e costruzione di astrazioni strato dopo strato. Sono gli stessi tre assi della slide: rappresentazione, ottimizzazione, costo.</p></div>
""".replace('{C12}', C12))

s(10, "DNN Input Transformations", """
<p>Per un problema di apprendimento <b>non lineare</b> si cerca una rappresentazione che porti gli ingressi in uno spazio dove le classi sono <b>linearmente separabili</b>.</p>
<p><b>Figura</b> (visionbook, fig. 13.7): a sinistra i dati di ingresso, punti rossi raggruppati al centro e punti blu sparsi intorno (nessuna retta li separa); una «serie di trasformazioni geometriche», cioè una rete neurale, li porta a destra nell'uscita obiettivo, dove ogni classe è schiacciata su un vertice (i codici one-hot (1,0) e (0,1)).</p>
<div class="box b"><b>Dal libro · {C13}, § 13.3–13.4</b><p>Ogni strato trasforma la <b>distribuzione</b> dei dati: p<sub>dati</sub> → p<sub>1</sub> → p<sub>2</sub> → … → p<sub>uscita</sub>. Uno strato lineare sposta, ruota e stira la nuvola di punti; una ReLU proietta sugli assi tutto ciò che ha coordinate negative. Addestrare il classificatore significa trovare la sequenza di trasformazioni che manda i rossi su un codice one-hot e i blu sull'altro.</p></div>
""".replace('{C13}', C13))

s(11, "DNN Input Transformations (2)", """
<ul>
<li>Durante il training la rete impara <b>gradualmente</b> a rendere i dati linearmente separabili.</li>
<li>La separabilità lineare è massima allo <b>strato finale</b>: è lì che c'è il classificatore lineare (softmax).</li>
</ul>
<p><b>Figura</b> (visionbook, fig. 13.8): quattro colonne, quattro momenti del training (da sinistra a destra). In ogni colonna la pila di piani mostra i dati dopo ogni strato (linear, relu, linear, relu, linear, softmax). All'inizio rossi e blu restano mescolati fino in cima; nelle colonne successive le linee si separano e all'ultimo strato le due classi finiscono in punti diversi.</p>
""")

s(12, "Embeddings", """
<ul>
<li><b>Embedding</b>: il vettore ad alta dimensione che rappresenta l'ingresso, preso come uscita di un certo strato della rete.</li>
<li Spesso si <b>congela</b> un modello già addestrato e si usano i suoi embedding per risolvere un problema nuovo (transfer learning: per esempio un classificatore lineare sopra le feature di una ResNet pre-addestrata).</li>
<li><b>Visualizzazione</b>: gli embedding si disegnano in 2D con tecniche di riduzione della dimensionalità (PCA, t-SNE).</li>
</ul>
<p><b>Figura</b> (visionbook, fig. 13.9): embedding di un Vision Transformer addestrato con CLIP, mostrati con t-SNE dopo blocchi successivi (dal basso verso l'alto). Nei piani bassi i colori (classi) sono mescolati; in alto ogni colore occupa una zona sua.</p>
<div class="box b"><b>Dal libro · {C13}, § 13.5</b><p>Gli embedding di quella figura hanno decine di migliaia di dimensioni; t-SNE li proietta in 2D cercando di conservare i <b>vicinati</b> (punti vicini restano vicini). È quindi una vista approssimata: le distanze grandi nel grafico non vanno lette alla lettera. Nota: la rete della figura è un transformer, non una CNN; il fenomeno (classi che si separano salendo di strato) è lo stesso.</p></div>
""".replace('{C13}', C13).replace('<li Spesso', '<li>Spesso'))

s(13, "Embeddings and Generalization", """
<ul>
<li>Lo scopo del training è ottenere una rappresentazione <b>disentangled</b> («districata»): ogni concetto (per esempio ogni classe) ben separato dagli altri.
<ul><li>Una buona rappresentazione districata dovrebbe <b>generalizzare</b> anche a cambiamenti forti: punto di vista, giorno e notte, eccetera.</li></ul></li>
<li>Con il <b>pre-training</b> (addestramento preliminare su dataset enormi) si vuole districare anche concetti <b>nuovi</b>, per esempio classi mai viste in training.</li>
</ul>
<p><b>Figura</b>: la stessa della slide 12 (fig. 13.9 del visionbook).</p>
""")

s(14, "Depth vs Width", """
<p><b>Profondità</b> (numero di strati): permette di rappresentare funzioni più complesse.</p>
<ul><li>Figura (Hanin e Rolnick, ICML 2019): una rete ReLU divide lo spazio degli ingressi in <b>regioni</b> in cui è lineare (ogni regione un colore); salendo di strato le regioni si suddividono ancora. La slide dice che il numero di regioni è esponenziale nella profondità.</li></ul>
<p><b>Larghezza</b> (numero di neuroni per strato): è la dimensione degli embedding.</p>
<ul>
<li>dimensioni più alte danno embedding più <b>sparsi</b>;</li>
<li>in alta dimensione vettori casuali sono quasi <b>ortogonali</b> (vᵀu ≈ 0): c'è spazio per moltissime direzioni «indipendenti»;</li>
<li>la teoria classica (maledizione della dimensionalità) scoraggerebbe gli spazi ad alta dimensione, eppure funzionano.</li>
</ul>
<p>Le architetture allo stato dell'arte sono sia <b>larghe</b> sia <b>profonde</b>.</p>
<div class="box w"><b>Attenzione: regioni «esponenziali nella profondità»</b>Esponenziale è il <b>massimo teorico</b> (Montúfar et al. 2014; Prince § 4.5 e 20.6.1). L'articolo citato in figura dimostra proprio il contrario per le reti reali: con pesi casuali e anche dopo il training, il numero medio di regioni cresce con il <b>numero totale di neuroni</b>, non esponenzialmente con la profondità. Inoltre per vettori casuali il prodotto scalare normalizzato è circa 0 (dell'ordine di 1/√d), non esattamente 0.</div>
<div class="box b"><b>Dal libro · {C12}, § 12.5.2–12.5.3, e {C13}, § 13.3</b><p>Il teorema di approssimazione universale dice che un solo strato nascosto basta, se è abbastanza largo: con le ReLU si costruisce una «gobba» con 4 ReLU, e sommando gobbe si approssima qualunque funzione continua (§ 12.5.2). Ma il numero di neuroni necessario può essere enorme: esistono funzioni che una rete profonda rappresenta con pochi neuroni e una rete poco profonda solo con un numero esponenziale (separazioni di profondità, § 12.5.3). Sulla sparsità: dopo una ReLU in N dimensioni la regione dove tutte le coordinate sono positive è solo 1/2<sup>N</sup> dello spazio, quindi quasi tutti i punti finiscono con molte coordinate a zero (§ 13.3).</p></div>
""".replace('{C12}', C12).replace('{C13}', C13))

s(15, "Regularization in DL", """
<p><b>Nel machine learning classico</b>:</p>
<ul>
<li><b>maledizione della dimensionalità</b>: i problemi ad alta dimensione sono più difficili;</li>
<li><b>compromesso bias-varianza</b>: un buon modello bilancia overfitting (troppo complesso, impara il rumore) e underfitting (troppo semplice).</li>
</ul>
<p><b>Nelle DNN</b>:</p>
<ul>
<li>le DNN (di larghezza infinita) sono <b>approssimatori universali</b>;</li>
<li>la complessità teorica è praticamente infinita per tutte le misure classiche (per esempio la dimensione VC);</li>
<li>in pratica una DNN riesce a imparare a memoria un dataset con <b>etichette casuali</b> (Zhang et al., «Understanding deep learning requires rethinking generalization», ICLR 2017).</li>
</ul>
<p>Eppure, sui dati veri, generalizzano bene: la teoria classica non spiega perché.</p>
<div class="box b"><b>Dal libro · {C11}, § 11.2 e 11.4</b><p>Con la regressione polinomiale l'errore di validazione segue la classica curva a U: grado troppo basso underfitting, troppo alto overfitting (fig. 11.1–11.2). Il libro avverte che le reti moderne non seguono la regola «più parametri, più overfitting»: spesso una rete più grande generalizza meglio, e il numero di parametri è solo un indicatore grossolano della capacità (§ 11.4). L'esperimento di Zhang et al. è descritto da Prince, § 20.2.1: AlexNet su CIFAR-10 arriva a errore di training zero anche con etichette permutate a caso o con immagini di puro rumore, solo più lentamente.</p></div>
""".replace('{C11}', C11))

s(16, "Regularization in DL", """
<p><b>Nelle DNN</b>:</p>
<ul>
<li>l'effetto regolarizzante più forte è <b>implicito</b>: nei parametri di SGD (learning rate, dimensione del batch, numero di epoche) e nell'architettura;</li>
<li>si usa anche la regolarizzazione <b>esplicita</b>: <b>weight decay</b> (penalità sulla norma dei pesi, λ‖θ‖²) e <b>dropout</b> (spegnere a caso neuroni durante il training).</li>
</ul>
<p><b>Regole pratiche sulla dimensione del modello</b>:</p>
<ul>
<li>usa il modello <b>più grande che puoi permetterti</b>: la dimensione si sceglie in base ai limiti di calcolo, non per paura dell'overfitting;</li>
<li><b>scaling laws</b>: per i foundation model si sa che dimensione del modello e dimensione del dataset vanno fatte crescere insieme per un addestramento ottimale a parità di costo.</li>
</ul>
<div class="box x"><b>Approfondimento</b>Regolarizzazione implicita (Prince § 9.2): con passo finito, la discesa del gradiente si comporta come se minimizzasse la loss più una penalità proporzionale al quadrato della norma del gradiente; SGD aggiunge un termine simile legato alla varianza dei gradienti fra batch. Learning rate più alti e batch più piccoli rafforzano l'effetto, e infatti tendono a generalizzare meglio (§ 20.4.1).</div>
""")

# ===================== COMPONENTI DI BASE =====================

s(17, "Basic DNN Components", """<p>Divisoria: i mattoni di una rete (slide 18–24): attivazioni, normalizzazioni, strato di uscita, loss.</p>""",
  kind='div', sec=("l15-componenti", "Componenti di base", "slide 17–24"))

s(18, "Activation Functions", """
<p>Le funzioni di attivazione, applicate elemento per elemento (indice i):</p>
<ul>
<li><b>soglia</b>: x<sub>out</sub>[i] = 1 se x<sub>in</sub>[i] &gt; 0, altrimenti 0 (il perceptron; derivata nulla quasi ovunque: inutilizzabile col gradiente);</li>
<li><b>sigmoide</b>: x<sub>out</sub>[i] = 1 / (1 + e<sup>−x<sub>in</sub>[i]</sup>), valori in (0, 1);</li>
<li><b>tanh</b>: x<sub>out</sub>[i] = 2·sigmoid(2x<sub>in</sub>[i]) − 1, valori in (−1, 1) (è esattamente la tangente iperbolica);</li>
<li><b>ReLU</b>: x<sub>out</sub>[i] = max(x<sub>in</sub>[i], 0);</li>
<li><b>leaky ReLU</b>: x<sub>in</sub>[i] se positivo, α·x<sub>in</sub>[i] altrimenti, con α piccolo.</li>
</ul>
<p><b>ReLU o leaky ReLU</b> sono la scelta standard per le reti grandi:</p>
<ul><li><b>niente gradiente che svanisce</b>: la derivata vale 1 su tutta la parte positiva, mentre quella della sigmoide è al massimo 0,25 e tende a 0 per |x| grande (dieci strati di sigmoide moltiplicano il gradiente per al più 0,25<sup>10</sup> ≈ 10<sup>−6</sup>);</li>
<li><b>implementazione veloce</b> (un confronto).</li></ul>
<p><b>Figura</b> (visionbook, fig. 12.16): i grafici delle cinque funzioni su [−2, 2].</p>
<div class="box w"><b>Attenzione: leaky ReLU «α = 2» nel grafico</b>Il titolo del grafico dice α = 2, ma la curva disegnata passa per (−2, −0,4): la pendenza a sinistra è <b>0,2</b>. Con α = 2 il ramo negativo sarebbe più ripido di quello positivo e la funzione non sarebbe affatto «leaky». Valori tipici: α fra 0,01 e 0,2.</div>
<div class="box k"><b>Da saper fare</b>Disegnare le cinque funzioni con le loro derivate e spiegare perché con la ReLU il gradiente non svanisce lungo la parte positiva (e perché la leaky ReLU evita i neuroni «morti», sempre a zero).</div>
""")

s(19, "Activation Functions (2)", """
<p><b>Figura</b> (visionbook, fig. 13.5): l'effetto di tre strati su una nuvola di punti 2D (piano in basso x<sub>in</sub>, piano in alto x<sub>out</sub>, linee che uniscono ogni punto alla sua immagine):</p>
<ul>
<li><b>linear</b>: la nuvola viene spostata, ruotata e stirata, ma resta una nuvola (trasformazione affine);</li>
<li><b>relu</b>: i punti con una coordinata negativa vengono schiacciati sugli assi; in uscita la densità si accumula lungo i due semiassi positivi e nell'origine;</li>
<li><b>L2-norm</b>: ogni punto viene diviso per la sua norma e finisce sul cerchio unitario (x<sub>out</sub> = x<sub>in</sub> / ‖x<sub>in</sub>‖).</li>
</ul>
<p>Messaggio: ogni strato è una trasformazione geometrica dello spazio; le non linearità piegano lo spazio in modi che una mappa lineare non può fare.</p>
""")

s(20, "Batch Normalization", """
<p>La <b>Batch Normalization</b> standardizza i suoi ingressi:</p>
<span class="f">x<sub>out</sub>[i] = γ · (x<sub>in</sub>[i] − 𝔼[x<sub>in</sub>[i]]) / √Var[x<sub>in</sub>[i]] + β</span>
<ul>
<li><b>γ</b> e <b>β</b> sono parametri appresi: dopo aver portato media 0 e varianza 1, la rete può ridare la scala e la media che le servono.</li>
<li>Media e varianza:
<ul><li>in <b>training</b>: stimate sul <b>mini-batch corrente</b>;</li>
<li>in <b>inferenza</b>: si usano medie mobili calcolate durante il training, così l'uscita per un'immagine non dipende dalle altre immagini del batch.</li></ul></li>
</ul>
<p><b>Nota</b>: la BatchNorm introduce una dipendenza dalla dimensione del batch, che dà problemi in alcuni casi (batch di 1, multi-task learning…). Per questo molte reti moderne usano la <b>LayerNorm</b>.</p>
<div class="box w"><b>Attenzione: γ e β non sono «due scalari»</b>C'è una coppia (γ, β) <b>per ogni canale</b> (o per ogni unità in uno strato denso), e nelle CNN media e varianza di un canale si calcolano su tutti gli esempi del batch <b>e su tutte le posizioni spaziali</b> (Prince § 11.4: con K strati da C canali ci sono KC scale e KC offset). Nell'implementazione c'è anche un piccolo ε: si divide per √(Var + ε) per non dividere per zero (manca sia nella slide sia nel libro).</div>
<div class="box b"><b>Dal libro · {C12}, § 12.7.3, e Prince § 11.4</b><p>Il visionbook dà la stessa formula e osserva che la BatchNorm rompe l'ipotesi che gli esempi siano indipendenti: l'uscita per un'immagine dipende dalle altre del batch. Prince spiega perché funziona: rende stabile la varianza delle attivazioni nel forward pass (essenziale nelle reti residue, dove altrimenti raddoppia a ogni blocco), rende la loss più liscia e quindi permette learning rate più alti, e aggiunge un rumore che regolarizza (§ 11.4.1).</p></div>
""".replace('{C12}', C12))

s(21, "Layer Normalization", """
<ul>
<li>media <b>sul singolo esempio</b>: μ = (1/n) ∑<sub>i=1</sub><sup>n</sup> x<sub>in</sub>[i];</li>
<li>varianza sul singolo esempio: σ² = (1/n) ∑<sub>i=1</sub><sup>n</sup> (x<sub>in</sub>[i] − μ)².</li>
</ul>
<span class="f">x<sub>out</sub>[i] = γ · (x<sub>in</sub>[i] − μ) / σ + β</span>
<ul>
<li>ogni esempio è standardizzato <b>indipendentemente</b> dagli altri: niente dipendenza dal batch, comportamento identico in training e in test;</li>
<li>per rappresentazioni 1D (matrice dei dati N<sub>batch</sub> × N<sub>feature</sub>) la LayerNorm è la «trasposta» della BatchNorm: la BatchNorm normalizza le <b>colonne</b> (una feature su tutto il batch), la LayerNorm le <b>righe</b> (tutte le feature di un esempio).</li>
</ul>
<p><b>Figura</b> (visionbook, fig. 12.17): due griglie N<sub>batch</sub> × C canali; in grigio la zona su cui si calcolano media e varianza: una colonna per la batchnorm, una riga per la layernorm.</p>
<div class="box k"><b>Da saper fare</b>Dato un batch piccolo (per esempio 2 esempi × 3 feature), calcolare a mano l'uscita di BatchNorm e di LayerNorm con γ = 1, β = 0, e dire quale delle due cambia se si cambia un altro esempio del batch.</div>
""")

s(22, "Temperature-Scaled Softmax", """
<p>Lo strato di uscita per la classificazione è la <b>softmax con temperatura</b>:</p>
<span class="f">x<sub>out</sub>[i] = e<sup>x<sub>in</sub>[i]/τ</sup> / ∑<sub>k=1</sub><sup>K</sup> e<sup>x<sub>in</sub>[k]/τ</sup></span>
<ul>
<li>è un'approssimazione <b>morbida dell'argmax</b>: dà più peso all'uscita con la risposta più alta (la classe predetta);</li>
<li>le uscite x<sub>out</sub> sono positive e sommano a 1: sono le <b>probabilità</b> delle classi;
<ul><li>gli ingressi x<sub>in</sub> si chiamano <b>logit</b>;</li>
<li>in inferenza, se interessa solo la classe più probabile, la softmax non serve: l'esponenziale è crescente, quindi il logit massimo corrisponde alla probabilità massima.</li></ul></li>
<li><b>τ</b> è la temperatura:
<ul><li>τ → +∞: i logit divisi per τ tendono tutti a 0, quindi le probabilità diventano <b>uniformi</b> (1/K ciascuna);</li>
<li>τ → 0: distribuzione sempre più <b>appuntita</b>, con probabilità 1 sulla classe migliore (se il massimo è unico).</li></ul></li>
</ul>
<p>Esempio: logit (2, 1, 0). Con τ = 1: e², e¹, e⁰ = 7,39, 2,72, 1 → probabilità 0,67, 0,24, 0,09. Con τ = 0,5 i logit diventano (4, 2, 0) → 0,87, 0,12, 0,02: più appuntita.</p>
<div class="box b"><b>Dal libro · {C12}, § 12.7.4</b><p>Il visionbook scrive la softmax come e<sup>−τ x<sub>in</sub>[i]</sup> / ∑<sub>k</sub> e<sup>−τ x<sub>in</sub>[k]</sup>: lì τ moltiplica, quindi è una temperatura <b>inversa</b> (più τ è grande, più la distribuzione è appuntita), e il segno meno farebbe vincere il logit più <b>piccolo</b>. È una convenzione insolita (lo stesso nel § 24.4). Quella della slide, x/τ, è la convenzione standard: seguite questa.</p></div>
""".replace('{C12}', C12))

s(23, "Output for Regression problems", """
<ul>
<li>Per la <b>regressione</b> l'uscita è semplicemente lineare (attivazione identità): la rete può dare qualunque numero reale.</li>
<li>Se serve un'uscita <b>limitata</b>, si usa la sigmoide (valori in (0, 1)) e la si riscala.</li>
</ul>
<p>Esempio, valori in (0, 255), come i pixel di un'immagine generata:</p>
<span class="f">x<sub>out</sub>[i] = 255 · sigmoid(x<sub>in</sub>[i])</span>
<p>È la stessa formula del visionbook (§ 12.7.4) per un'uscita immagine N × M × 3; per ottenere i pixel si arrotonda all'intero.</p>
""")

s(24, "CrossEntropy loss", """
<p>Nella classificazione si usa la <b>cross-entropy</b>:</p>
<span class="f">l = − ∑<sub>c=1</sub><sup>C</sup> y[c] · log ŷ[c]</span>
<ul>
<li><b>y</b>: probabilità vere (di solito one-hot: 1 sulla classe giusta, 0 altrove, e allora l = −log ŷ[classe giusta]);</li>
<li><b>ŷ</b>: probabilità predette (uscita della softmax).</li>
</ul>
<p>Per <b>stabilità numerica</b> i framework calcolano la cross-entropy direttamente dai <b>logit</b>, fondendo softmax e cross-entropy in un'unica operazione:</p>
<span class="f">l = − ∑<sub>c</sub> y[c] · log( exp(z[c]) / ∑<sub>i=1</sub><sup>C</sup> exp(z[i]) ) = − ∑<sub>c</sub> y[c] · ( z[c] − log ∑<sub>i</sub> exp(z[i]) )</span>
<p>con z i logit. Il termine log ∑ exp si calcola sottraendo prima il logit massimo (trucco «log-sum-exp»), così e<sup>z</sup> non va mai in overflow e non si calcola mai log(0). In PyTorch: <code>nn.CrossEntropyLoss</code> vuole i logit, non le probabilità.</p>
<p>Esempio: logit (2, 1, 0), classe giusta la prima: l = −(2 − log(e² + e + 1)) = −(2 − 2,41) = 0,41 = −log 0,67.</p>
<div class="box w"><b>Attenzione: notazione della seconda formula</b>Nella slide la seconda formula usa x<sub>out</sub>[c]: devono essere i <b>logit</b>, cioè gli <b>ingressi</b> della softmax (x<sub>in</sub> nella notazione della slide 22), non le sue uscite; e y<sub>c</sub> è lo stesso y[c] della prima formula.</div>
""")

# ===================== CONVOLUZIONI =====================

s(25, "Convolutions in DNNs", """<p>Divisoria: lo strato convoluzionale (slide 26–34).</p>""",
  kind='div', sec=("l15-conv", "Convoluzioni nelle reti", "slide 25–34"))

s(26, "Convolution Recap", """
<span class="f">x<sub>out</sub>[n, m] = b + ∑<sub>k<sub>1</sub>, k<sub>2</sub> = −K</sub><sup>K</sup> w[k<sub>1</sub>, k<sub>2</sub>] · x<sub>in</sub>[n + k<sub>1</sub>, m + k<sub>2</sub>]</span>
<ul>
<li><b>w</b> è il <b>kernel</b> (filtro), di dimensione (2K + 1) × (2K + 1): K è la semi-ampiezza (K = 1 per un 3×3);</li>
<li><b>x</b> è un ingresso 2D (larghezza × altezza);</li>
<li>le CNN implementano la <b>correlazione incrociata</b>: indice n + k, nessun ribaltamento del kernel (la convoluzione vera di <a href="#L3">L3</a> userebbe n − k);</li>
<li>in più c'è un <b>bias</b> scalare b, anch'esso appreso.</li>
</ul>
<div class="box b"><b>Dal libro · {C24}, § 24.2 (eq. 24.1–24.2)</b><p>Il libro dice esplicitamente che gli strati «convoluzionali» sono in realtà correlazioni incrociate, e che la differenza non conta: una correlazione con w è una convoluzione con w ribaltato, e poiché w si impara le due famiglie di funzioni sono identiche. Prince (§ 10.2.1, nota) fa lo stesso commento: è una convenzione «sbagliata» ma universale nel machine learning.</p></div>
""".replace('{C24}', C24))

s(27, "Parameter Sharing", """
<ul>
<li>Una convoluzione è solo una <b>operazione lineare speciale</b>: si può scrivere come x<sub>out</sub> = W x<sub>in</sub>.</li>
<li>La matrice W ha <b>molti zeri</b> (ogni uscita dipende solo da pochi ingressi vicini: <b>località</b>) e <b>molti parametri uguali</b> (gli stessi pesi in ogni riga, spostati: <b>condivisione dei pesi</b>).</li>
<li>Rispetto alla moltiplicazione per una matrice piena equivalente si risparmiano calcolo e memoria.</li>
</ul>
<p><b>Figura</b> (visionbook, fig. 24.4): a sinistra la matrice W di una convoluzione 1D con kernel [w[−1], w[0], w[1]]: le tre diagonali centrali (azzurre) ripetono gli stessi tre valori, il resto è zero (matrice di <b>Toeplitz</b>). A destra la stessa operazione vista come rete: ogni uscita è collegata solo a tre ingressi vicini, sempre con i pesi w[1], w[0], w[−1].</p>
<div class="box b"><b>Dal libro · Prince § 10.2.4 e fig. 10.4</b><p>Uno strato fully connected da D ingressi a D uscite ha D² pesi; lo strato convoluzionale con kernel 3 ne ha 3 (più un bias). Lo strato fully connected <b>può</b> riprodurre la convoluzione (basta mettere a zero e rendere uguali i pesi giusti), ma in pratica non la trova: su MNIST-1D una CNN da 2.050 parametri ha circa il 17% di errore di test, la rete fully connected equivalente da 59.065 parametri circa il 40% (§ 10.2.7, fig. 10.8). Il vantaggio non è il numero di parametri ma il <b>bias induttivo</b>: imporre di trattare ogni posizione allo stesso modo.</p></div>
""")

s(28, "Multi-Channel Inputs", """
<p>Finora la convoluzione aveva 1 canale di ingresso e 1 di uscita. Le reti usano <b>più canali</b> sia in ingresso (es. RGB = 3) sia in uscita.</p>
<p><b>Ingresso multicanale</b>: ogni canale si filtra con la sua «fetta» del kernel e i risultati si <b>sommano</b>:</p>
<span class="f">x<sub>out</sub> = ∑<sub>c</sub> w[c, :, :] ⋆ x<sub>in</sub>[c, :, :] + b</span>
<p>dove ⋆ è la convoluzione (correlazione) a un canale della slide 26. Un kernel per un'immagine RGB con 3×3 spaziale ha quindi 3 × 3 × 3 = 27 pesi, più un bias.</p>
<div class="box w"><b>Attenzione: il bias b[c]</b>Nella slide (e nel libro, § 24.2.1) il bias è scritto b[c], con l'indice del canale di <b>ingresso</b> dentro la somma. Un filtro multicanale produce un solo canale di uscita e ha <b>un solo bias</b>: va scritto + b fuori dalla somma (sommare tanti b[c] equivale comunque a un unico bias). Il testo dice «where ∗» ma la formula usa ⋆: è lo stesso simbolo.</div>
""")

s(29, "Multi-Channel Outputs", """
<p><b>Uscita multicanale</b>: si applicano C filtri diversi allo stesso ingresso, ognuno col suo bias:</p>
<span class="f">x<sub>out</sub>[0, :, :] = w[0, :, :] ⋆ x<sub>in</sub> + b[0]<br>⋮<br>x<sub>out</sub>[C−1, :, :] = w[C−1, :, :] ⋆ x<sub>in</sub> + b[C−1]</span>
<ul>
<li>È esattamente un <b>banco di filtri</b> (<a href="#L7">L7</a>): ogni canale di uscita corrisponde a un filtro diverso.</li>
<li>Un canale di uscita si chiama anche <b>feature map</b> (mappa delle feature): per esempio la mappa di «dove ci sono bordi verticali».</li>
</ul>
""")

s(30, "Multi-Input and Multi-Output", """
<p>Il caso generale, C<sub>in</sub> canali in ingresso e C<sub>out</sub> in uscita:</p>
<span class="f">x<sub>out</sub>[c<sub>2</sub>, :, :] = ∑<sub>c<sub>1</sub>=1</sub><sup>C<sub>in</sub></sup> w[c<sub>1</sub>, c<sub>2</sub>, :, :] ⋆ x<sub>in</sub>[c<sub>1</sub>, :, :] + b[c<sub>2</sub>]</span>
<ul><li>tensore totale dei pesi di forma <b>C<sub>out</sub> × C<sub>in</sub> × K × K</b>, più C<sub>out</sub> bias.</li></ul>
<p><b>Figura</b> (visionbook, fig. 24.5): a sinistra C<sub>out</sub> filtri, ognuno un blocco K × K × C<sub>in</sub> (azzurro); al centro l'ingresso x<sub>in</sub>, C<sub>in</sub> piani M × N; a destra l'uscita x<sub>out</sub>, C<sub>out</sub> piani. Ogni filtro attraversa tutta la profondità dell'ingresso e produce un piano dell'uscita.</p>
<div class="box w"><b>Attenzione: ordine degli indici e significato di K</b>La forma «C<sub>out</sub> × C<sub>in</sub> × K × K» è la convenzione di PyTorch, ma nella formula il primo indice di w è c<sub>1</sub>, il canale di ingresso (convenzione del libro: w ∈ ℝ<sup>C<sub>in</sub> × C<sub>out</sub> × K × K</sup>). Il numero di pesi è lo stesso; basta non mescolare le due cose. Inoltre qui K è il <b>lato</b> del kernel, mentre nella slide 26 K era la semi-ampiezza (kernel 2K + 1): stessa lettera, due significati (incoerenza presente anche nel libro).</div>
<div class="box b"><b>Dal libro · {C24}, § 24.2.1 (fig. 24.6)</b><p>Esempio del libro: immagine RGB 128 × 128 filtrata da un banco di filtri 3 × 3 che produce un'uscita 96 × 128 × 128. Ogni filtro ha 3 × 3 × 3 = <b>27</b> parametri (senza bias) e i filtri sono <b>96</b>, uno per canale di uscita: 2.592 pesi in tutto.</p></div>
<div class="box k"><b>Da saper fare</b>Contare i parametri di uno strato: K · K · C<sub>in</sub> · C<sub>out</sub> + C<sub>out</sub>. Esempio: 3×3, da 64 a 128 canali: 9 · 64 · 128 + 128 = 73.856.</div>
""".replace('{C24}', C24))

s(31, "Example: Parameter Efficiency", """
<p>Esempio: ingresso H × W × C<sub>in</sub>, uscita H × W × C<sub>out</sub>.</p>
<p><b>Strato fully connected</b>:</p>
<ul>
<li>ogni unità di uscita è collegata a ogni unità di ingresso;</li>
<li>parametri: (H W C<sub>in</sub>) × (H W C<sub>out</sub>);</li>
<li>per un'immagine 64 × 64 × 3 e C<sub>out</sub> = 64: 12.288 × 262.144 ≈ <b>3,2 miliardi</b> di pesi.</li>
</ul>
<p><b>Convoluzione k × k</b>:</p>
<ul>
<li>parametri: k² C<sub>in</sub> C<sub>out</sub>, <b>indipendenti dalla risoluzione</b> (H, W) dell'immagine;</li>
<li>con k = 3: 9 · 3 · 64 = <b>1.728</b> pesi (più 64 bias).</li>
</ul>
<p>Rapporto: circa due milioni di volte meno parametri. E la stessa conv si può applicare a immagini di qualunque dimensione.</p>
<div class="box k"><b>Da saper fare</b>Rifare i due conti (64·64·3 = 12.288; 64·64·64 = 262.144; prodotto ≈ 3,2·10⁹) e spiegare perché i parametri della conv non dipendono da H e W (pesi condivisi su tutte le posizioni).</div>
""")

s(32, "Stride", """
<span class="f">x<sub>out</sub>[n, m] = b + ∑<sub>k<sub>1</sub>, k<sub>2</sub> = −K</sub><sup>K</sup> w[k<sub>1</sub>, k<sub>2</sub>] · x<sub>in</sub>[s<sub>n</sub> n − k<sub>1</sub>, s<sub>m</sub> m − k<sub>2</sub>]</span>
<ul>
<li><b>stride</b> (passo) s<sub>n</sub>, s<sub>m</sub>: il filtro si calcola solo ogni s pixel. Di solito un unico valore s = s<sub>n</sub> = s<sub>m</sub>.</li>
<li>L'uscita ha dimensione circa N/s × M/s: con s = 2 un quarto delle posizioni, quindi <b>calcolo molto ridotto</b>.</li>
</ul>
<p><b>Figura</b> (visionbook, cap. 24): il filtro w (3 × 3) scorre sull'ingresso saltando di due posizioni alla volta, sia in orizzontale sia in verticale; l'uscita x<sub>out</sub> è più piccola.</p>
<p>Stride = convoluzione seguita da sottocampionamento (prendere un pixel ogni s), ma senza calcolare le posizioni scartate.</p>
<div class="box w"><b>Attenzione: segno degli indici (slide 32 e 34)</b>Qui e nella dilatazione la formula usa x<sub>in</sub>[s n − k] (indice con il meno, come la convoluzione vera), mentre la slide 26 usa x<sub>in</sub>[n + k] (correlazione). È un refuso del libro (eq. 24.5 e 24.6 contro 24.2). Con kernel appresi non cambia nulla (equivale a ribaltare w), ma per coerenza va scritto x<sub>in</sub>[s<sub>n</sub> n + k<sub>1</sub>, s<sub>m</sub> m + k<sub>2</sub>].</div>
""")

s(33, "Stride Aliasing", """
<p><b>Figura</b> (visionbook, fig. 24.8): in alto un parallelepipedo grigio (ingresso) e il risultato del filtro <b>laplaciano</b> [[0, −1, 0], [−1, 4, −1], [0, −1, 0]] con stride 1, 2 e 4; in basso il modulo della DFT di ciascuna immagine.</p>
<ul>
<li><b>stride 1</b>: i bordi del solido sono puliti; lo spettro ha le righe radiali dei bordi;</li>
<li><b>stride 2</b>: i bordi diventano tratteggiati, con artefatti; nello spettro compaiono righe <b>nuove</b> che nell'originale non c'erano;</li>
<li><b>stride 4</b>: artefatti gravi, alcuni bordi spariscono; lo spettro è quasi rumore.</li>
</ul>
<p>È l'<b>aliasing</b> di <a href="#L6">L6</a>: lo stride è un sottocampionamento <b>senza filtro anti-aliasing</b> prima. Il laplaciano esalta proprio le alte frequenze, che sottocampionando si ripiegano su frequenze basse.</p>
<div class="box b"><b>Dal libro · {C24}, § 24.2.2</b><p>Il libro osserva che l'apprendimento può compensare in parte (i kernel appresi minimizzano la loss e i canali possono compensarsi a vicenda), ma lo stride restringe comunque l'insieme dei kernel «utili»: un kernel con molta energia ad alta frequenza, sottocampionato, produce aliasing. Collegamento con <a href="#L14">L14</a>: nel § 21.2 lo stesso fenomeno viene sfruttato per costruire un attacco avversario.</p></div>
""".replace('{C24}', C24))

s(34, "Dilated Convolution", """
<span class="f">x<sub>out</sub>[n, m] = b + ∑<sub>k<sub>1</sub>, k<sub>2</sub> = −K</sub><sup>K</sup> w[k<sub>1</sub>, k<sub>2</sub>] · x<sub>in</sub>[n − d<sub>k</sub> k<sub>1</sub>, m − d<sub>k</sub> k<sub>2</sub>]</span>
<ul>
<li><b>d<sub>k</sub></b>: parametro di <b>dilatazione</b>. Il kernel non tocca pixel adiacenti ma pixel distanti d<sub>k</sub>: è come inserire d<sub>k</sub> − 1 zeri fra i pesi.</li>
<li>Un 3 × 3 con d<sub>k</sub> = 2 copre un'area 5 × 5 con soli 9 pesi; in generale l'estensione è 2K d<sub>k</sub> + 1.</li>
</ul>
<p><b>Figura</b> (visionbook, fig. 24.9): il filtro 5 × 5 con le celle scure a zero e i 9 pesi (azzurri) distanziati di uno; scorre su x<sub>in</sub> e produce x<sub>out</sub> della stessa dimensione.</p>
<div class="box b"><b>Dal libro · {C24}, § 24.2.3</b><p>La dilatazione allarga il campo coperto <b>senza aumentare il calcolo</b>, ma riduce lo spazio dei kernel utili: un filtro di sfocatura binomiale con d<sub>k</sub> = 2 non è più un passa-basso (nella DFT compaiono massimi ad alta frequenza, fig. 24.10–24.11). In cascata, tre 3 × 3 con d = 1, 2, 4 danno un kernel equivalente molto grande definito da soli 27 valori (il libro scrive 9 × 9, ma l'estensione è 3 + 4 + 8 = 15, cioè 15 × 15).</p></div>
""".replace('{C24}', C24))

# ===================== POOLING =====================

s(35, "Pooling", """<p>Divisoria: strati di pooling (slide 36–37).</p>""",
  kind='div', sec=("l15-pooling", "Pooling", "slide 35–37"))

s(36, "Pooling Layers", """
<ul>
<li><b>Max pooling</b>: sostituisce ogni intorno k × k con il suo valore <b>massimo</b>.</li>
<li><b>Average pooling</b>: lo sostituisce con la <b>media</b>.</li>
</ul>
<span class="f">x<sub>out</sub>[i] = max<sub>j ∈ 𝒩(i)</sub> x<sub>in</sub>[j] &nbsp;&nbsp;&nbsp; x<sub>out</sub>[i] = (1/|𝒩|) ∑<sub>j ∈ 𝒩(i)</sub> x<sub>in</sub>[j]</span>
<ul>
<li>riduce la <b>risoluzione spaziale</b> (meno calcolo nei layer successivi); si applica canale per canale, il numero di canali non cambia;</li>
<li>introduce un po' di <b>robustezza a piccole traslazioni</b>: se il pattern si sposta di un pixel restando nella stessa finestra, il massimo non cambia;</li>
<li>il max pooling conserva l'attivazione più forte («questo pattern c'è da qualche parte qui vicino?»); l'average pooling sfuma e mescola le risposte vicine.</li>
</ul>
<p>Esempio: blocco 2 × 2 = [[1, 3], [2, 0]] → max 3, media 1,5.</p>
<div class="box w"><b>Attenzione: indici nella formula</b>Nella slide (e nel libro, eq. 24.8) la stessa lettera i indica sia la posizione di uscita sia la variabile che scorre nell'intorno («max<sub>i ∈ 𝒩(i)</sub> x<sub>in</sub>[i]»). Va usata una seconda lettera: max<sub>j ∈ 𝒩(i)</sub> x<sub>in</sub>[j], come sopra.</div>
<div class="box b"><b>Dal libro · {C24}, § 24.3.1</b><p>Il pooling trasforma l'<b>equivarianza</b> in <b>invarianza</b>: un rilevatore di bordi verticali dà una mappa che si sposta col bordo (equivariante); un max pooling su un intorno abbastanza grande dà una risposta che non dipende da dove sta il bordo (invariante). Facendo il massimo sui canali (per esempio su filtri di orientazioni diverse) si ottiene invece invarianza all'orientazione. Il pooling riduce anche le alte frequenze (la media è un passa-basso).</p></div>
""".replace('{C24}', C24))

s(37, "Global Average Pooling", """
<ul>
<li><b>Global average pooling</b> (GAP): media di ogni feature map su <b>tutte</b> le posizioni spaziali: un numero per canale, qualunque sia la dimensione dell'immagine.</li>
<li>Si usa alla fine della parte convoluzionale di un classificatore, prima degli strati lineari: trasforma una mappa H × W × C in un <b>vettore di C</b> numeri.</li>
<li><b>Invarianza alla traslazione</b>:
<ul><li>le convoluzioni sono <b>equivarianti</b> alla traslazione, non invarianti: se sposto l'ingresso, la mappa di uscita si sposta allo stesso modo, f(T x) = T f(x);</li>
<li>la media su tutte le posizioni introduce un po' di <b>invarianza</b>, f(T x) ≈ f(x): non importa dove compare il pattern.</li></ul></li>
<li>Toglie anche il vincolo di una <b>risoluzione di ingresso fissa</b>: immagini più grandi danno feature map più grandi, ma il numero di canali, quindi la lunghezza del vettore dopo la GAP, non cambia.</li>
</ul>
<div class="box b"><b>Dal libro · Prince § 10.1 e {C24}, § 24.3.2</b><p>Prince definisce: f è <b>invariante</b> a una trasformazione t se f(t[x]) = f(x) (serve alla classificazione: un cane spostato resta un cane); è <b>equivariante</b> se f(t[x]) = t[f(x)] (serve alla segmentazione: la maschera deve spostarsi insieme all'oggetto). Il visionbook nota che il global pooling elimina l'informazione spaziale di ogni canale, ma non tutta: se canali diversi rispondono a cose in posizioni diverse, qualcosa della posizione sopravvive.</p></div>
""".replace('{C24}', C24))

# ===================== GERARCHIA =====================

s(38, "Hierarchical Feature Learning", """<p>Divisoria: campo recettivo e apprendimento gerarchico delle feature (slide 39–43).</p>""",
  kind='div', sec=("l15-gerarchia", "Campo recettivo e gerarchia di feature", "slide 38–43"))

s(39, "Receptive Field", """
<ul>
<li>Il <b>campo recettivo</b> (RF) di un'unità è la regione dell'<b>ingresso originale</b> che può influenzarne il valore.</li>
<li>Un'unità di uno strato iniziale vede solo i pixel «coperti» dal kernel; un'unità profonda può essere influenzata da una regione molto più grande, anche l'intera immagine.</li>
<li>La dimensione del RF dice a che <b>scala</b> di struttura l'unità può rispondere: RF piccolo, texture e bordi locali; RF grande, oggetti interi o contesto globale.</li>
<li>Il RF cresce con la <b>profondità</b> e con la <b>dimensione del kernel</b> (e molto più in fretta con stride e pooling).</li>
</ul>
<p><b>Figura</b> (visionbook, fig. 24.26): rete 1D conv → relu → conv con kernel di 3. A sinistra l'unità x<sub>2</sub>[3] dopo due conv (pallini neri) dipende da <b>5</b> ingressi; a destra l'unità x<sub>1</sub>[5] dopo una sola conv dipende da <b>3</b> ingressi. La relu, puntuale, non allarga il campo.</p>
<p>Regola con kernel k e stride 1: dopo L strati RF = L(k − 1) + 1; per k = 3, RF = 2L + 1 (3, 5, 7, 9…).</p>
<div class="box b"><b>Dal libro · {C24}, § 24.7, e Prince § 10.2.6</b><p>Senza non linearità una pila di convoluzioni è una sola convoluzione con supporto più grande (associatività, <a href="#L3">L3</a>); le non linearità puntuali non cambiano il campo recettivo. Un downsampling di fattore s fa sì che ogni pixel successivo valga s pixel dell'ingresso, quindi da lì in poi il campo cresce s volte più in fretta; una global pooling finale porta il campo all'intera immagine. Prince (fig. 10.6) mostra lo stesso conto: con kernel 3 il campo passa da 3 a 5, e con uno stride 2 al terzo strato a 7.</p></div>
<div class="box k"><b>Da saper fare</b>Calcolare il campo recettivo di una pila di conv: per esempio tre 3 × 3 con stride 1 → 7 × 7; conv 3 × 3, poi max pool 2 × 2 stride 2, poi conv 3 × 3 → 3 + 1 + 2·2 = 8 (la seconda conv aggiunge (3 − 1)·2 perché lavora su pixel che valgono 2).</div>
""".replace('{C24}', C24))

s(40, "The Hierarchy Hypothesis", """
<ul>
<li><b>Ipotesi</b>: una CNN addestrata su un compito visivo complesso impara una <b>gerarchia</b> di rappresentazioni: bordi → texture → parti di oggetti → oggetti interi e concetti semantici, dai primi agli ultimi strati.</li>
<li>Motivazioni:
<ul><li><b>campo recettivo</b>: i primi strati hanno RF piccolo e possono rappresentare solo struttura locale; gli ultimi hanno RF grande e possono rappresentare oggetti interi;</li>
<li><b>visualizzazioni</b> empiriche delle feature map di reti addestrate (slide 41–43).</li></ul></li>
</ul>
<div class="box x"><b>Approfondimento</b>È un'ipotesi, non un teorema. Il visionbook non la enuncia con queste parole: nel § 24.6 si limita a osservare che le mappe dei primi strati rispondono a bordi e linee e quelle profonde diventano semantiche. Le evidenze classiche sono le visualizzazioni di Zeiler e Fergus (2014), che per ogni unità mostrano le parti di immagine che la attivano di più: bordi e colori al primo strato, texture al secondo, parti (occhi, ruote) e poi oggetti interi più in alto. Il riferimento biologico è la corteccia visiva (V1 bordi orientati, poi aree con campi recettivi sempre più grandi e selettività sempre più complessa).</div>
""")

s(41, "Feature Maps", """
<p><b>Figura</b> (visionbook, fig. 24.23): schema di una CNN come pila di feature map.</p>
<ul>
<li><b>Ingresso</b>: l'immagine RGB, cioè 3 canali W × H (tre piani rosa).</li>
<li><b>layer 1 filters</b>: 5 filtri, ciascuno 3 × 3 con 3 canali (R, G, B) → <b>layer 1 feature maps</b>: 5 canali di dimensione W/2 × H/2 (la risoluzione si dimezza).</li>
<li><b>layer 2 filters</b>: ogni filtro ha ora 5 canali, perché l'ingresso del layer 2 ha 5 canali.</li>
<li>In fondo i <b>logit</b>: K canali di dimensione 1 × 1 (una «feature map» di un pixel per classe), poi argmax → «heron».</li>
</ul>
<p>Regola da notare: il numero di canali di un filtro è sempre uguale al numero di canali del suo ingresso; il numero di filtri decide i canali dell'uscita.</p>
""")

s(42, "Example: Feature Maps", """
<p><b>Figura</b> (visionbook, fig. 24.24): le feature map di AlexNet sull'immagine dell'airone.</p>
<ul>
<li>A sinistra l'<b>ingresso</b> RGB [H × W × 3], mostrato come tre canali in scala di grigi.</li>
<li>Al centro i <b>filtri del layer 1</b> (ingranditi 4 volte): piccoli pattern colorati, bordi orientati e macchie di colore; le <b>feature map del layer 1</b> sono [H/4 × W/4 × C<sub>1</sub>]: ogni mappa evidenzia bordi o zone di un certo tipo dell'airone (bordi tratteggiati in arancione: un filtro e la sua mappa).</li>
<li>A destra i <b>filtri del layer 2</b> (ognuno con C<sub>1</sub> canali) e le <b>feature map del layer 2</b> [H/8 × W/8 × C<sub>2</sub>]: risoluzione ancora più bassa, molti più canali (bordo verde: un filtro e la sua mappa).</li>
</ul>
<p>Si vede la tendenza generale: salendo, la <b>risoluzione scende</b> e i <b>canali aumentano</b>; le mappe sono sempre meno «immagini» e sempre più «rilevatori».</p>
""")

s(43, "PCA of Feature Maps visualization", """
<ul>
<li>Negli strati profondi i canali sono centinaia: è difficile guardarli tutti.</li>
<li>Alternativa diffusa: la <b>PCA</b> (analisi delle componenti principali):
<ul><li>si fa la PCA sui vettori di canali di tutte le posizioni dell'immagine e si tengono le prime <b>3 componenti</b>;</li>
<li>così ogni posizione diventa un colore RGB: un'immagine a 3 canali.</li></ul></li>
</ul>
<p><b>Figura</b> (visionbook, fig. 24.25): tre righe, AlexNet, VGG16 e ResNet18; in ogni riga l'immagine di ingresso e la PCA di cinque strati sempre più profondi. Nei primi strati la mappa colorata riproduce i contorni dell'airone; più in alto la risoluzione cala (blocchi sempre più grandi) e i colori raggruppano zone semantiche: l'animale da una parte, lo sfondo dall'altra.</p>
<p>Lettura: colori uguali = vettori di feature simili. Negli strati alti pixel dell'airone lontani fra loro hanno lo stesso colore, perché la rete li rappresenta come «la stessa cosa».</p>
<div class="box k"><b>Da saper fare</b>Spiegare come si costruisce la visualizzazione: feature map H × W × C → matrice (HW) × C → PCA → (HW) × 3 → immagine H × W a colori.</div>
""")

# ===================== ARCHITETTURE =====================

s(44, "Classic Architectures", """<p>Divisoria: architetture classiche, da LeNet a ConvNeXt (slide 45–55).</p>""",
  kind='div', sec=("l15-arch", "Architetture classiche", "slide 44–55"))

s(45, "A Basic CNN Architecture", """
<p>Uno schema base, applicato in sequenza:</p>
<ul>
<li><b>blocchi convoluzionali</b>: conv, non linearità, pooling;
<ul><li>il numero di filtri <b>cresce</b> con la profondità mentre la dimensione dell'immagine <b>diminuisce</b>;</li></ul></li>
<li><b>blocchi densi</b>: strati fully connected e non linearità;</li>
<li><b>uscita</b>: softmax e loss.</li>
</ul>
<p>È il modello classico, già in <b>LeNet</b> (LeCun et al., 1998), addestrata su <b>MNIST</b> (cifre scritte a mano 28 × 28).</p>
<p><b>Figura</b> (visionbook, fig. 24.16): l'airone attraversa blocchi «Convolution + Non-linearity + Subsample» ripetuti, poi gli strati finali e l'etichetta «heron».</p>
<div class="box b"><b>Dal libro · {C24}, § 24.4 A Simple CNN Classifier</b><p>Il libro scrive una CNN minima: z<sub>1</sub>[c] = w[c] ⋆ x + b[c] (conv con C canali), h = max(z<sub>1</sub>, 0) (relu), z<sub>2</sub>[c] = (1/NM) ∑<sub>n,m</sub> h[c, n, m] (global average pooling), z<sub>3</sub> = W z<sub>2</sub> + c (fully connected da C a K classi), y = softmax(z<sub>3</sub>). Nel § 24.5 la addestra con due soli canali a distinguere linee orizzontali e verticali: i due kernel 9 × 9 appresi somigliano a derivate di gaussiana (fig. 24.19), cioè la rete riscopre da sola i filtri di <a href="#L5">L5</a>. (Il testo del § 24.4 parla di «due layer convoluzionali» ma la rete ne ha uno, e chiama «somma» la gap che è una media.)</p></div>
""".replace('{C24}', C24))

s(46, "ImageNet 1k", """
<ul>
<li>I progressi del deep learning dipendono da <b>dati di qualità</b> quanto dalle idee tecniche.</li>
<li><b>ImageNet-1k</b>: classificazione in <b>1000 classi</b>, circa <b>1,2 milioni</b> di immagini di training (1.281.167 secondo Prince § 10.5.1, più 50.000 di validazione).</li>
</ul>
<p><b>Figura</b>: la scritta «IMAGENET» composta da un mosaico di migliaia di piccole immagini del dataset. Link a una galleria di esempi: github.com/EliSchwartz/imagenet-sample-images.</p>
<p>Metriche usate nelle slide successive: <b>top-1</b> (la classe con probabilità massima è quella giusta) e <b>top-5</b> (la classe giusta è fra le cinque più probabili).</p>
""")

s(47, "AlexNet (2012)", """
<ul>
<li>Il primo modello di deep learning allo <b>stato dell'arte</b> nella classificazione di immagini.
<ul><li>Addestrato su ImageNet (1000 classi, 1,2 milioni di immagini);</li>
<li>è l'inizio della rivoluzione del deep learning nella visione.</li></ul></li>
<li>Ingredienti chiave:
<ul><li><b>ReLU</b>: economica e senza gradiente che svanisce;</li>
<li>training su <b>due GPU</b> consumer (la rete è divisa in due metà, una per GPU: le due «strisce» della figura);</li>
<li><b>dropout</b> come regolarizzazione.</li></ul></li>
<li><b>8 strati con pesi</b> (5 conv + 3 fully connected), larghi, con molti canali.</li>
</ul>
<p><b>Figura</b> (dall'articolo di AlexNet): ingresso 224 × 224 × 3; primo strato 11 × 11 con stride 4 e 96 canali (48 + 48 sulle due GPU), poi 5 × 5 con 256 canali, tre conv 3 × 3 (384, 384, 256), max pooling, e tre strati densi 4096, 4096, 1000.</p>
<div class="box b"><b>Dal libro · Prince § 10.5.1</b><p>AlexNet ha circa <b>60 milioni</b> di parametri, quasi tutti negli strati fully connected; usava data augmentation (ritagli e riflessioni, variazioni di intensità), SGD con momentum 0,9, batch 128, dropout e weight decay. Errore top-5 del 16,4% (top-1 38,1%), contro circa il 25% dei metodi non deep dell'anno prima.</p></div>
""")

s(48, "VGG (2014)", """
<ul>
<li>Progetto <b>semplice e uniforme</b>: solo conv <b>3 × 3</b> (stride 1) e max pooling 2 × 2;
<ul><li>fino a <b>19 strati</b> con pesi (VGG-16, VGG-19).</li></ul></li>
<li><b>Argomento del campo recettivo</b>: impilare kernel piccoli raggiunge campi recettivi grandi con <b>meno parametri</b> e <b>più non linearità</b> rispetto a pochi kernel grandi.</li>
<li>Ha mostrato che <b>aumentare la profondità</b> migliora l'accuratezza, mentre la dimensione esatta del kernel conta meno.</li>
</ul>
<p>Simonyan e Zisserman, «Very deep convolutional networks for large-scale image recognition», ICLR 2015.</p>
<div class="box k"><b>Da saper fare</b>Il conto dell'argomento VGG, con C canali in ingresso e in uscita: due 3 × 3 hanno lo stesso campo di un 5 × 5 ma 2 · 9C² = 18C² pesi contro 25C²; tre 3 × 3 equivalgono a un 7 × 7 con 27C² pesi contro 49C², e in più ci sono tre ReLU invece di una.</div>
<div class="box b"><b>Dal libro · Prince § 10.5.1</b><p>VGG-19: 19 strati e circa 144 milioni di parametri, errore top-5 del 6,8% (AlexNet 16,4%). Prince sottolinea che, fra le varie differenze, quella decisiva rispetto ad AlexNet è la profondità.</p></div>
""")

s(49, "GoogLeNet / Inception (2014)", """
<ul>
<li><b>Modulo Inception</b>: applica in <b>parallelo</b> kernel di dimensioni diverse (1 × 1, 3 × 3, 5 × 5, più un max pooling 3 × 3) e concatena le uscite lungo i canali.</li>
<li>Motivazione: la scala «giusta» delle strutture cambia da posizione a posizione e da immagine a immagine; la rete sceglie da sola quale ramo pesare.</li>
<li>La conv <b>1 × 1</b> serve come passo economico di <b>mescolamento dei canali</b> e <b>riduzione della dimensionalità</b> prima delle costose conv 3 × 3 e 5 × 5.</li>
</ul>
<p><b>Figura</b> (dall'articolo di Inception): dal «previous layer» partono quattro rami: 1 × 1; 1 × 1 → 3 × 3; 1 × 1 → 5 × 5; 3 × 3 max pooling → 1 × 1. In cima la «filter concatenation».</p>
<div class="box b"><b>Dal libro · Prince § 10.4.3</b><p>Una conv 1 × 1 calcola, in ogni posizione, una combinazione pesata di tutti i canali: è la stessa rete fully connected applicata ai canali di ogni pixel. Ha 1 × 1 × C<sub>i</sub> × C<sub>o</sub> pesi. Esempio di risparmio: una 5 × 5 da 256 a 32 canali costa 25 · 256 · 32 = 204.800 pesi; passando prima per una 1 × 1 da 256 a 64 canali e poi per la 5 × 5 da 64 a 32 si spendono 256 · 64 + 25 · 64 · 32 = 16.384 + 51.200 = 67.584 pesi, un terzo (è lo stesso esempio della dispensa).</p></div>
""")

s(50, "ResNet: Residual Connections (2015)", """
<ul>
<li><b>Gradienti che svaniscono/esplodono</b>: in reti profonde i gradienti propagati all'indietro attraverso molti strati non lineari tendono a rimpicciolire (o, più raramente, a esplodere) esponenzialmente con la profondità;
<ul><li>questo limita il vantaggio di aumentare la profondità;</li>
<li>è un problema di <b>ottimizzazione</b>, risolvibile con un'architettura migliore che permetta reti più profonde.</li></ul></li>
<li><b>Blocco residuo</b>: <span class="f">y = F(x) + x</span> (la <b>skip connection</b> somma l'ingresso all'uscita).
<ul><li>l'identità è banale da rappresentare (F(x) = 0): uno strato inutile può restare (quasi) un'identità;</li>
<li><b>flusso del gradiente</b>: per la regola della catena ∂y/∂x = ∂F/∂x + I. L'identità garantisce un cammino diretto per il gradiente attorno a ogni blocco, comunque piccolo diventi ∂F/∂x;</li>
<li>in pratica, con le connessioni residue, aggiungere strati inizializzati con pesi piccoli non dovrebbe mai peggiorare l'accuratezza.</li></ul></li>
<li>Ha permesso di addestrare reti con più di <b>100 strati</b> (ResNet-152).</li>
</ul>
<div class="box w"><b>Attenzione: è davvero colpa dei gradienti che svaniscono?</b>La formula ∂y/∂x = ∂F/∂x + I è giusta, ma la motivazione storica è più sottile. He et al. (2016) osservano che una rete «piana» da 56 strati ha errore più alto di una da 20 <b>anche sul training</b> (quindi non è overfitting), e scrivono che questa difficoltà di ottimizzazione difficilmente dipende da gradienti che svaniscono, perché le loro reti usano BatchNorm e i gradienti hanno norme sane. Prince (§ 11.1.1) propone gli <b>shattered gradients</b>: nelle reti profonde il gradiente cambia in modo caotico per spostamenti minimi, e la superficie è «una distesa di piccole montagne» (si veda la figura della slide 7). Le connessioni residue rendono la superficie più liscia.</div>
<div class="box b"><b>Dal libro · {C24}, § 24.11.3, e Prince § 11.2–11.5</b><p>Il visionbook: x<sub>out</sub> = F(x<sub>in</sub>) + x<sub>in</sub>, e se le dimensioni cambiano x<sub>out</sub> = F(x<sub>in</sub>) + W x<sub>in</sub> (proiezione, per esempio con una conv 1 × 1); impilando molti blocchi la rete sceglie da sola la propria profondità effettiva. Prince aggiunge: «srotolando» una rete residua l'uscita è una somma di percorsi di lunghezze diverse (eq. 11.5); anche con l'inizializzazione di He la varianza delle attivazioni raddoppia a ogni blocco, ed è per questo che ogni blocco ResNet contiene BatchNorm (blocco BN-ReLU-conv ripetuto due volte, o il blocco «bottleneck» 1 × 1 → 3 × 3 → 1 × 1 per le reti più profonde).</p></div>
<div class="box k"><b>Da saper fare</b>Derivare ∂y/∂x = ∂F/∂x + I e spiegare perché, moltiplicando questi fattori lungo L blocchi, nel prodotto compare sempre il termine I · I · … · I = I: il gradiente non può annullarsi solo per colpa della profondità.</div>
""".replace('{C24}', C24))

s(51, "DenseNet (2017)", """
<ul>
<li><b>Riuso delle feature</b>: ogni strato riceve come ingresso la <b>concatenazione</b> delle feature map di <b>tutti</b> gli strati precedenti del blocco.</li>
<li><b>Flusso del gradiente</b>: connessione diretta all'uscita di ogni strato precedente, cammini del gradiente più corti.</li>
<li>Compromesso: <b>più memoria</b>, per via della concatenazione.</li>
</ul>
<p>Huang et al., «Densely connected convolutional networks», CVPR 2017.</p>
<p><b>Figure</b> (dall'articolo di DenseNet): a sinistra la rete completa, tre «dense block» separati da strati di transizione (conv + pooling) fino alla predizione «horse»; a destra un dense block a 5 strati con growth rate k = 4: ogni strato aggiunge 4 canali, e frecce colorate portano l'uscita di ogni strato a tutti quelli successivi.</p>
<p>Differenza con ResNet: ResNet <b>somma</b> (x + F(x)), DenseNet <b>concatena</b> ([x, F(x)]), quindi i canali crescono lungo il blocco.</p>
""")

s(52, "EfficientNet (2019)", """
<p><b>EfficientNet</b>:</p>
<ul>
<li>per ingrandire una CNN (più accuratezza, più calcolo) si possono aumentare indipendentemente <b>profondità</b>, <b>larghezza</b> (canali) e <b>risoluzione</b> di ingresso;</li>
<li>risultato: scalare <b>tutte e tre insieme</b>, con un rapporto fisso (compound scaling), dà un'accuratezza per FLOP migliore che scalarne una sola.</li>
</ul>
<p><b>MobileNet</b>, efficienza per l'uso su dispositivi:</p>
<ul>
<li><b>convoluzioni depthwise separable</b>: una conv k × k <b>depthwise</b> (un filtro per canale, nessun mescolamento fra canali) seguita da una conv 1 × 1 <b>pointwise</b> (mescola i canali);</li>
<li>riduce il calcolo (per posizione) da O(k² C<sub>in</sub> C<sub>out</sub>) a O(k² C<sub>in</sub> + C<sub>in</sub> C<sub>out</sub>), permettendo inferenza in tempo reale su telefoni e hardware edge.</li>
</ul>
<p><b>Figura</b> (dall'articolo di EfficientNet): accuratezza top-1 su ImageNet contro numero di parametri (milioni); la curva rossa delle EfficientNet B0–B7 sta sopra a tutte le altre (ResNet, DenseNet, Inception, NASNet, AmoebaNet…): a parità di parametri sono più accurate, fino all'84,3% di B7.</p>
<div class="box k"><b>Da saper fare</b>Il conto della depthwise separable con k = 3 e C<sub>in</sub> = C<sub>out</sub> = 256: standard 9 · 256 · 256 = 589.824 moltiplicazioni per posizione; separabile 9 · 256 + 256 · 256 = 2.304 + 65.536 = 67.840, circa 8,7 volte meno. In generale il rapporto è 1/C<sub>out</sub> + 1/k².</div>
""")

s(53, "ConvNeXt (2022)", """
<ul>
<li><b>ConvNeXt</b> porta nelle CNN le scelte di progetto vincenti dell'era dei Transformer: <b>kernel più grandi</b> (7 × 7 depthwise), meno strati di normalizzazione e attivazione, <b>LayerNorm</b> al posto della BatchNorm, attivazione GELU, e un <b>inverted bottleneck</b> (il blocco prima allarga i canali, 96 → 384, poi li riduce).</li>
<li>Risultato: mantiene il bias induttivo delle CNN e arriva alla pari dei Vision Transformer (ViT) sui grandi benchmark.</li>
</ul>
<p><b>Figura</b> (dall'articolo di ConvNeXt): a sinistra il blocco ResNet (1 × 1 a 64 canali, 3 × 3 a 64, 1 × 1 a 256, con BN e ReLU dopo ogni conv); a destra il blocco ConvNeXt (d7 × 7 depthwise a 96, LN, 1 × 1 a 384, GELU, 1 × 1 a 96): una sola normalizzazione e una sola attivazione per blocco.</p>
""")

s(54, "Recap: Architectural Ideas", """
<ul>
<li><b>Profondità</b>: le architetture profonde sono possibili grazie a connessioni residue, inizializzazioni corrette e ottimizzatori.</li>
<li><b>Kernel</b>: pile di kernel piccoli spesso preferite ai kernel grandi: più non linearità e meno parametri a parità di campo recettivo.</li>
<li><b>Architetture moderne</b> (EfficientNet, MobileNet, ConvNeXt): idee rifinite per migliori compromessi fra calcolo, memoria e accuratezza.</li>
</ul>
<p><b>Note pratiche</b>:</p>
<ul>
<li>parti <b>sempre</b> da architetture esistenti, modelli pre-addestrati e ricette di training note: replicare anni di ottimizzazione su un'architettura tua richiede moltissimo tempo;</li>
<li>il calcolo dipende da kernel, dimensione dell'immagine e canali: anche i layer conv profondi (con immagine piccola) costano molto per via dell'alto numero di canali (il costo di una conv è H · W · k² · C<sub>in</sub> · C<sub>out</sub>).</li>
</ul>
""")

s(55, "Cost vs accuracy", """
<p>Accuratezza top-1 su ImageNet-1K contro costo del forward pass (miliardi di operazioni, G-Ops). La dimensione delle bolle è proporzionale al numero di parametri (legenda in basso: da 5 a 155 milioni).</p>
<p>Cosa si legge nel grafico (Canziani et al. 2016):</p>
<ul>
<li><b>AlexNet</b> in basso a sinistra: poco calcolo, accuratezza intorno al 55–57%;</li>
<li><b>VGG-16 e VGG-19</b>: bolle enormi (circa 140 milioni di parametri) e costo altissimo (circa 30–40 G-Ops) per circa il 71–72%: il modello meno efficiente;</li>
<li><b>ResNet-50/101/152</b> e <b>Inception</b> in alto: circa 76–80% con molto meno calcolo e parametri di VGG (ResNet-18 e 34 stanno intorno al 69–73%);</li>
<li><b>MobileNet, ShuffleNet, SqueezeNet</b> in basso a sinistra: calcolo minimo, accuratezza discreta (circa 60–70%).</li>
</ul>
<p>Lezione: più parametri non vuol dire più accuratezza; contano le idee di architettura (residui, 1 × 1, bottleneck).</p>
""")

# ===================== CONCLUSIONI =====================

s(56, "Conclusions", """<p>Divisoria: punti di forza, limiti e messaggi chiave (slide 57–59).</p>""",
  kind='div', sec=("l15-concl", "Conclusioni", "slide 56–59"))

s(57, "Strengths and Limitations of CNNs", """
<p><b>Punti di forza</b>:</p>
<ul>
<li><b>Località + condivisione dei pesi</b> sono buone ipotesi a priori per le immagini naturali;
<ul><li>le CNN sono la scelta di default su dataset <b>piccoli e medi</b>, dove un'architettura meno vincolata (per esempio un ViT) dovrebbe imparare da zero località e struttura di traslazione.</li></ul></li>
<li><b>Efficienza</b> sia in memoria sia in calcolo.</li>
</ul>
<p><b>Limiti</b>:</p>
<ul>
<li>Anche con un campo recettivo teorico grande (rete profonda, kernel grandi), il <b>campo recettivo effettivo</b> è molto più piccolo e concentrato al centro (Luo et al. 2016: i pixel al bordo del campo pesano pochissimo, la distribuzione dell'influenza è circa gaussiana);
<ul><li>anche CNN profonde possono faticare a mettere in relazione zone lontane dell'immagine.</li></ul></li>
<li><b>Equivarianza alla traslazione rigida</b>: alcuni compiti non vogliono trattare ogni posizione allo stesso modo;
<ul><li>esempio: un sistema di verifica del volto può volere una sensibilità diversa al centro e al bordo dell'immagine.</li></ul></li>
</ul>
<p>Questi limiti sono risolti dai <b>Vision Transformer</b> (prossime lezioni; visionbook cap. 26).</p>
<div class="box b"><b>Dal libro · {C24}, § 24.10 e 24.12</b><p>Il libro giustifica l'elaborazione patch per patch con due proprietà: patch <b>indipendenti</b> (dividi et impera: problemi piccoli, parallelizzabili, indipendenti dalla dimensione dell'immagine; funziona perché le immagini hanno struttura locale) e trattate in modo <b>identico</b> (le statistiche delle immagini sono circa invarianti alla traslazione). Conclusione del capitolo: i transformer potrebbero sostituire le CNN, ma anche loro elaborano ogni patch in modo identico e indipendente, alternando stadi che globalizzano l'informazione fra patch.</p></div>
""".replace('{C24}', C24))

s(58, "Key Takeaways", """
<ul>
<li>Le DNN per la visione permettono di passare da banchi di filtri <b>statici</b> a banchi di filtri <b>appresi</b>, e abilitano l'apprendimento <b>gerarchico</b> delle feature.</li>
<li>Nonostante la loro complessità, le DNN moderne sono molto robuste a overfitting e problemi di ottimizzazione.</li>
<li>La <b>convoluzione</b> è l'operazione naturale delle reti per la visione.</li>
</ul>
""")

s(59, "References", """
<ul>
<li>visionbook, <b>capitolo 24</b> (Convolutional Neural Nets): {link}.</li>
<li><b>conv_arithmetic</b> di Vincent Dumoulin (github.com/vdumoulin/conv_arithmetic): animazioni di convoluzioni con padding, stride, dilatazione e convoluzioni trasposte. Utile per vedere come cambiano le dimensioni dell'uscita: con ingresso N, kernel k, padding p e stride s l'uscita è ⌊(N + 2p − k)/s⌋ + 1.</li>
</ul>
<p>Per il resto della lezione servono anche i capitoli 12 (Neural Networks), 13 (Neural Networks as Distribution Transformers) e 11 (The Problem of Generalization): vedi la sezione Studia dal libro qui sotto.</p>
""".replace('{link}', L('convolutional_neural_nets.html', 'visionbook.mit.edu/convolutional_neural_nets.html')))
