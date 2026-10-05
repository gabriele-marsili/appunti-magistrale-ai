
s(1, "Copertina", """
<p><b>Computer Vision</b>: <i>Introduction, Structure and Organization of the Course</i>. Prima lezione, 1 settembre 2026.</p>
<p>La lezione ha tre parti:</p>
<ul>
<li>che cos'è la visione artificiale e <b>perché è difficile</b>;</li>
<li>cosa ci insegna la <b>percezione umana</b> (prior, contesto) e quali sono i <b>temi</b> che tornano in tutto il corso;</li>
<li>esempi di stato dell'arte e <b>organizzazione del corso</b> (programma, esame, laboratori, libri).</li>
</ul>
""")

s(2, "What is Computer Vision?", "<p>Definizione, livelli dei task, applicazioni e motivi per cui vedere è difficile.</p>", kind="div", sec=("l1-cosa", "Cos'è la computer vision", "slide 2–19"))

s(3, "Computer Vision", """
<p>Citazione di <b>David Marr</b>: vedere significa <b>sapere cosa c'è e dove, guardando</b> (<i>"to know what is where by looking"</i>).</p>
<p><b>Figura:</b> copertina del libro <i>Vision</i> di Marr (1982), con un'illusione a contorni soggettivi in stile Kanizsa: tre sagome "morsicate" fanno vedere un triangolo che non è disegnato.</p>
<ul>
<li>Il "cosa" è il riconoscimento (identità, categoria), il "dove" è la struttura spaziale (posizione, forma 3D).</li>
<li>La definizione è volutamente orientata al <b>significato</b>: non si tratta di misurare la luce, ma di ricavare proprietà del mondo.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 1, § 1.3.6 Marr's Computational Theory of Vision</b>
<p>Marr propone di studiare un sistema visivo su <b>tre livelli</b> quasi indipendenti:</p>
<ul>
<li><b>teoria computazionale</b>: qual è il compito e perché (quale mappa input → output);</li>
<li><b>rappresentazione e algoritmo</b>: come sono codificati input e output e come si passa dall'uno all'altro. La scelta della rappresentazione rende esplicita certa informazione e ne nasconde altra;</li>
<li><b>implementazione (hardware)</b>: il supporto fisico, neuroni o silicio.</li>
</ul>
<p>La visione è vista come una sequenza di rappresentazioni: <b>immagine</b> (intensità) → <b>primal sketch</b> (bordi, giunzioni) → <b>sketch 2.5D</b> (profondità e orientazione delle superfici visibili) → <b>modello 3D</b> degli oggetti. Il libro nota che il limite di Marr è aver sottovalutato l'<b>apprendimento</b>: oggi la sequenza di rappresentazioni la sceglie la rete addestrata.</p>
<p><a href="https://visionbook.mit.edu/taxonomy.html">Cap. 1 The Challenge of Vision</a></p></div>
""")

s(4, "What is Computer Vision? Definition and Scope", """
<ul>
<li><b>Computer vision</b>: studio di come far estrarre alle macchine <b>significato, struttura e decisioni</b> da dati visivi: immagini, video, profondità, più viste.</li>
<li>Copre un insieme enorme di task che ricavano struttura <b>2D e 3D</b> dalle immagini.</li>
<li>Campi vicini, distinti da cosa entra e cosa esce:
<ul>
<li><b>image processing</b>: segnale in ingresso, segnale in uscita (es. denoising);</li>
<li><b>computer graphics</b>: sintesi di immagini da una descrizione della scena;</li>
<li><b>robotica</b>: la percezione serve all'azione;</li>
<li><b>machine learning</b>: la cassetta degli attrezzi moderna.</li>
</ul></li>
</ul>
""")

s(5, "The MIT Summer Vision Project", """
<ul>
<li>Nel 1966 Seymour Papert (MIT) propose la visione artificiale come <b>progetto estivo per studenti</b>: costruire "una parte significativa di un sistema visivo".</li>
<li>Obiettivo finale: <b>identificazione di oggetti</b>, cioè dare un nome agli oggetti confrontandoli con un vocabolario di oggetti noti.</li>
<li>Sessant'anni dopo il problema è ancora aperto: l'aneddoto mostra quanto sia stata sottovalutata la difficoltà.</li>
</ul>
<p><b>Figura:</b> prima pagina del memo originale (<i>Vision Memo No. 100</i>, 7 luglio 1966, "The Summer Vision Project").</p>
<div class="box b"><b>Dal libro · cap. 2, § 2.1 Introduction e § 2.2 A Simple World: The Blocks World</b>
<p>Il capitolo 2 prova a fare davvero il "progetto estivo" in un mondo semplificato, il <b>mondo a blocchi</b> di Larry Roberts (tesi di dottorato del 1963, la prima di computer vision): oggetti con facce solo orizzontali o verticali, appoggiati su un piano bianco. L'obiettivo non è riconoscere ma ricostruire le coordinate 3D X, Y, Z di ogni pixel visibile.</p>
<p>Funziona, ma solo grazie a ipotesi molto forti. È la dimostrazione pratica di cosa le tecniche classiche sanno e non sanno fare (vedi scheda 12 e la sezione "Studia dal libro").</p>
<p><a href="https://visionbook.mit.edu/simplesystem.html">Cap. 2 A Simple Vision System</a></p></div>
""")

s(6, "Low-level Vision", """
<p><b>Visione di basso livello</b>: operazioni vicine ai pixel, spesso immagine in ingresso e immagine (o campo) in uscita.</p>
<ul><li>Esempi: <b>denoising</b>, <b>edge detection</b>, <b>flusso ottico</b>.</li></ul>
<p><b>Figura:</b> a sinistra una foto dall'alto di una scrivania con portatili e oggetti; a destra la sua mappa dei bordi (linee chiare su fondo nero), dove restano solo i contorni di tastiere, schermi e oggetti.</p>
<p>I bordi si ottengono dal gradiente dell'immagine: è il tema di L5.</p>
""")

s(7, "Mid-Level", """
<p><b>Visione di medio livello</b>: raggruppare i pixel e ricavare struttura geometrica.</p>
<ul><li>Esempi: <b>segmentazione</b>, <b>stima della profondità</b>, <b>corrispondenze</b>, <b>ricostruzione 3D</b>.</li></ul>
<p><b>Figura:</b> frame di una scena stradale con segmentazione semantica sovrapposta: auto in blu, pedoni in rosso, strada in viola, vegetazione in verde. Ogni pixel riceve un'etichetta di classe.</p>
""")

s(8, "High-Level", """
<p><b>Visione di alto livello</b>: semantica e ragionamento.</p>
<ul><li>Esempi: <b>riconoscimento</b>, <b>detection</b>, <b>captioning</b>, <b>generazione</b>, <b>ragionamento visione-linguaggio</b>.</li></ul>
<p><b>Figura:</b> un prompt a ChatGPT chiede una rock band su un palco con chitarrista a sinistra, bassista a destra, cantante al centro davanti e batterista sullo sfondo; sotto, l'immagine generata con la disposizione richiesta.</p>
<p>Per generare così bisogna "capire" oggetti, ruoli e relazioni spaziali descritte a parole: la generazione è un task di alto livello quanto il riconoscimento.</p>
""")

s(9, "Cat-Bag", """
<p><b>Figura:</b> prompt "create three images: a cat, a bag, and a cat bag". Il modello produce un gatto, una borsa e una borsa nera a forma di muso di gatto.</p>
<ul>
<li>Il punto è la <b>composizionalità</b>: "cat bag" non è né un gatto né una borsa, ma una combinazione sensata dei due concetti.</li>
<li>I modelli generativi moderni combinano concetti in modi che non hanno visto esplicitamente: un segno di rappresentazioni di alto livello.</li>
</ul>
""")

s(10, "Applications", """
<ul>
<li><b>Telefoni</b>: sblocco col volto, ricerca nelle foto, filtri.</li>
<li><b>Auto</b>: rilevamento delle corsie e dei pedoni, stima della profondità, SLAM per la guida autonoma.</li>
<li><b>Imaging medico</b>: segmentazione di tumori, registrazione fra scansioni diverse, supporto alla diagnosi.</li>
<li><b>AR/VR</b>: tracking a 6 gradi di libertà (posizione + orientazione), ricostruzione della scena, stima della posa di mani e corpo.</li>
</ul>
<p>Schema comune: <b>pixel grezzi in ingresso, informazione strutturata in uscita</b>, spesso con vincoli stretti di latenza e accuratezza.</p>
""")

s(11, "Perception vs. Graphics", """
<ul>
<li><b>Graphics = modello diretto</b> (forward): descrizione della scena → immagine. Date geometria, materiali, luci e camera si calcola (render) l'immagine. Stesso input, stessa uscita.</li>
<li><b>Visione = problema inverso</b>: immagine → descrizione della scena. Dai pixel si vogliono recuperare geometria, materiali, luce, camera e semantica. È <b>mal posto</b>: scene diverse possono produrre la stessa immagine.</li>
</ul>
<p>La visione è "la grafica eseguita al contrario", e la parte difficile è proprio l'inversione.</p>
<div class="box x"><b>Approfondimento</b><p>Il libro chiude il cap. 2 con l'idea di <b>chiudere il cerchio</b>: dopo aver interpretato la scena, la si ri-renderizza (anche da un altro punto di vista) e si controlla che sia coerente con l'immagine. Modello diretto e modello inverso si usano insieme: il diretto serve a verificare l'inverso.</p></div>
""")

s(12, "Why Vision is Hard: Ill-Posedness and Ambiguity", """
<ul>
<li><b>Problema mal posto</b>: i soli dati non determinano una soluzione <b>unica e stabile</b>.</li>
<li>Esempio classico: una singola immagine 2D è compatibile con <b>infinite</b> scene 3D.
<ul>
<li>stessa silhouette → forme diverse (<b>ambiguità di profondità</b>);</li>
<li>stesso ombreggiamento → combinazioni diverse di forma, materiale e luce.</li>
</ul></li>
<li>Gli algoritmi di visione hanno bisogno di <b>prior</b> (ipotesi a priori sul mondo) per scegliere una risposta plausibile fra le tante possibili.</li>
</ul>
<div class="box x"><b>Approfondimento</b><p>La definizione formale è di Hadamard: un problema è ben posto se la soluzione <b>esiste</b>, è <b>unica</b> e <b>dipende con continuità dai dati</b> (piccolo rumore, piccolo cambiamento della soluzione). La proiezione 3D → 2D viola già l'unicità, perché perde una dimensione.</p></div>
<div class="box b"><b>Dal libro · cap. 2, § 2.3 A Simple Image Formation Model e § 2.6 From Edges to Surfaces</b>
<p>Nel mondo a blocchi il libro usa una <b>proiezione ortografica</b> con camera inclinata di un angolo θ:</p>
<span class="f">x = X,   y = cos(θ) Y − sin(θ) Z</span>
<p>Y (altezza) e Z (profondità) finiscono mescolati nella sola coordinata y: un punto che sale e uno che si allontana possono cadere sullo stesso pixel. È l'ambiguità della slide in forma di equazione.</p>
<p>Per risolverla il libro aggiunge <b>prior espliciti</b> come equazioni lineari su Y(x, y):</p>
<ul>
<li>pixel del piano di terra (bianchi, poco saturi): Y = 0; bordi di contatto con il terreno: Y = 0;</li>
<li>bordi verticali nel 3D: ∂Y/∂y = 1/cos(θ); bordi orizzontali: derivata di Y lungo il bordo = 0;</li>
<li>facce piane: derivate seconde di Y nulle, che propagano l'informazione dai bordi alle zone uniformi.</li>
</ul>
<p>Tutti i vincoli insieme formano un sistema sovradeterminato <b>A Y = b</b>, risolto ai minimi quadrati (pseudoinversa, eventualmente pesata). Z si ricava poi dall'equazione di proiezione.</p>
<p><a href="https://visionbook.mit.edu/simplesystem.html">Cap. 2 A Simple Vision System</a></p></div>
""")

s(13, "Why Vision is Hard: Illumination Changes", """
<ul>
<li>Lo stesso oggetto può apparire molto diverso sotto luci diverse:
<ul>
<li>la <b>direzione della luce</b> cambia ombreggiatura e ombre;</li>
<li>la <b>temperatura di colore</b> cambia i colori registrati (bilanciamento del bianco);</li>
<li>i <b>riflessi speculari</b> si spostano con il punto di vista e con la posizione della luce.</li>
</ul></li>
<li>Un sistema robusto deve separare "cosa è cambiato nella scena" da "cosa è cambiato per colpa della luce".</li>
</ul>
<p><b>Figura:</b> la stessa tazzina di caffè in quattro versioni: luce normale, sottoesposta, sovraesposta, luce laterale direzionale. I valori dei pixel cambiano moltissimo, l'oggetto è lo stesso.</p>
<p>Nota: sottoesposizione e sovraesposizione sono cambi di esposizione della camera più che della luce, ma l'effetto sui pixel è lo stesso tipo di disturbo.</p>
<div class="box b"><b>Dal libro · cap. 3, § 3.12 How Do You Know Something Is Wet?</b><p>Esempio del libro dello stesso problema: la sabbia bagnata è più scura di quella asciutta. Come fa il sistema visivo a distinguere "più scuro perché bagnato" (cambia il materiale) da "più scuro perché in ombra" (cambia la luce)? Il libro lascia la domanda aperta: serve a far notare che l'intensità di un pixel da sola non basta. <a href="https://visionbook.mit.edu/visionscience.html">Cap. 3</a></p></div>
""")

s(14, "Why Vision is Hard: Viewpoint/Pose Changes", """
<ul>
<li>Lo stesso oggetto visto da angoli diversi dà proiezioni 2D molto diverse:
<ul>
<li><b>auto-occlusione</b>: parti dell'oggetto nascondono altre parti;</li>
<li><b>scorcio</b> (foreshortening): le forme appaiono compresse;</li>
<li>dimensione apparente e rapporto d'aspetto cambiano con distanza e angolo.</li>
</ul></li>
<li>Riconoscimento e matching devono essere (almeno in parte) <b>invarianti al punto di vista</b>.</li>
</ul>
<p><b>Figura:</b> la foto di un'astronauta vista come "viewpoint A, B (frontale), C": le versioni A e C sono la stessa foto deformata prospetticamente, come se il piano dell'immagine fosse ruotato.</p>
<div class="box w"><b>Attenzione: la figura non mostra un oggetto 3D</b><p>La didascalia parla di "stesso oggetto 3D da punti di vista diversi", ma le tre immagini sono la stessa foto piana deformata con una trasformazione prospettica (omografia: bordi neri e sfondo deformati insieme al volto). Una foto piana ruotata mostra lo scorcio, ma <b>non</b> può mostrare l'auto-occlusione né il cambio di forma di un oggetto 3D vero. Il concetto della slide resta corretto.</p></div>
""")

s(15, "Why Vision is Hard: Occlusion", """
<ul>
<li>Gli oggetti reali si coprono a vicenda e coprono parti di sé stessi.</li>
<li>L'occlusione crea <b>dati mancanti</b>: parti della scena semplicemente non sono osservate in quell'immagine.</li>
<li>Gli algoritmi devono ragionare su ciò che è nascosto usando <b>contesto, prior o più viste</b>.</li>
</ul>
<p><b>Figura:</b> la stessa facciata di case a schiera; a sinistra davanti c'è un'auto scura parcheggiata, a destra un furgone bianco copre gran parte della facciata e della porta.</p>
<div class="box b"><b>Dal libro · cap. 1, § 1.2.1 The Input: The Structure of Ambient Light</b><p>Il libro descrive tutta la luce che riempie lo spazio con la <b>funzione plenottica</b> P(θ, Φ, λ, t, X, Y, Z): intensità per ogni direzione, lunghezza d'onda, istante e punto di osservazione. Un osservatore ne vede solo una fettina. L'occlusione è indicata come la sfida centrale: da qualunque punto di vista le superfici nascoste sono più di quelle visibili, eppure per capire la scena bisogna ragionare anche su di loro. <a href="https://visionbook.mit.edu/taxonomy.html">Cap. 1</a></p></div>
""")

s(16, "Why Vision is Hard: Scale and Intra-Class Variation", """
<ul>
<li><b>Variazione di scala</b>: lo stesso oggetto appare con dimensioni molto diverse a seconda della distanza dalla camera.</li>
<li><b>Variazione intra-classe</b>: oggetti della stessa categoria (es. "uccello") variano enormemente in forma, colore, texture, posa.</li>
<li>Una buona rappresentazione deve generalizzare lungo <b>entrambi gli assi</b> insieme.</li>
<li>Soluzioni: <b>elaborazione multiscala</b> e <b>rappresentazioni apprese invarianti</b>.</li>
</ul>
<p><b>Figura:</b> stormo di uccelli contro il cielo, a distanze diverse: alcuni sono grandi e dettagliati, altri pochi pixel.</p>
<p>Collegamento: la stessa figura torna in L6 per motivare scale-space e piramidi.</p>
""")

s(17, "Humans vs ML Systems", """
<ul>
<li>Gli umani risolvono i task visivi <b>senza sforzo, in millisecondi</b>, grazie a un'enorme quantità di conoscenza a priori implicita e di calcolo (corteccia visiva, anni di "dati di addestramento").</li>
<li>I sistemi di deep learning addestrati su grandi dataset oggi <b>eguagliano o superano</b> gli umani in molti task <b>ristretti</b>.</li>
<li><b>Nota</b>: i modi in cui il ML sbaglia sono diversi da quelli umani: <b>esempi avversari</b> (perturbazioni invisibili che cambiano la predizione) e <b>distribution shift</b> (dati di test diversi da quelli di training).</li>
</ul>
""")

s(18, "The Issue of Robustness and Generalization", """
<ul>
<li>Sia i sistemi appresi sia quelli classici hanno limiti.</li>
<li>I sistemi appresi possono <b>non generalizzare</b> a oggetti e scene nuovi. Due domande tipo: cosa fa un classificatore davanti a un oggetto sconosciuto? E davanti a un oggetto noto in un contesto insolito?</li>
<li>Di solito i sistemi appresi sono più robusti dei classici a grandi cambi di punto di vista o di scena, ma:
<ul>
<li>i limiti di un sistema classico sono <b>più facili da capire</b>; le reti profonde sono più "black box" ed è più difficile prevedere dove falliranno;</li>
<li>è fondamentale capire <b>quando</b> una tecnica funziona e quando no. Funzionerà con una camera a bassa risoluzione? Con cattiva illuminazione?</li>
</ul></li>
</ul>
<div class="box b"><b>Dal libro · cap. 2, § 2.7 Generalization</b><p>Anche il sistema a blocchi viene provato <b>fuori dominio</b>: oggetti che si occludono o impilati, casi che le ipotesi escludevano. I risultati restano ragionevoli, ma nulla lo garantisce: potrebbe fallire in modo imprevedibile. Con l'illusione dei "gradini impossibili" il sistema cerca di soddisfare vincoli incompatibili e produce una ricostruzione simile a quella che percepisce un umano. È lo stesso discorso della slide, applicato a un sistema classico di cui conosciamo esattamente le ipotesi. <a href="https://visionbook.mit.edu/simplesystem.html">Cap. 2</a></p></div>
""")

s(19, "Brief History of Computer Vision: Classical Era to Deep Learning", """
<ul>
<li><b>Anni '60–'80</b>: primi lavori su edge detection, comprensione di scene nel mondo a blocchi, flusso ottico, stereo.</li>
<li><b>Anni '90–2000</b>: feature progettate a mano e geometria: SIFT, corner di Harris, RANSAC, structure-from-motion, geometria multi-vista matura.</li>
<li><b>Anni 2010</b>: rivoluzione del deep learning; le CNN dominano il riconoscimento (ImageNet), poi detection e segmentazione.</li>
<li><b>Dal 2017</b>: transformer e ViT, apprendimento self-supervised, foundation model, modelli visione-linguaggio.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 1, § 1.3.7 Computer Vision e § 1.3.8 Learning-Based Vision</b>
<ul>
<li>1963: primo dottorato in computer vision (Larry Roberts, MIT), il mondo a blocchi.</li>
<li>1958: il <b>perceptron</b> di Rosenblatt; 1969: il libro <i>Perceptrons</i> di Minsky e Papert ne mostra i limiti e raffredda l'interesse; anni '80: reti a più strati, neocognitron di Fukushima, LeCun e le cifre scritte a mano (1989).</li>
<li>2001: Viola e Jones, face detection con boosting, finita dentro le fotocamere.</li>
<li>Anni 2000: benchmark (Caltech 101, PASCAL, ImageNet, COCO) e descrittori a mano (SIFT, HOG) con classificatori "superficiali" (SVM, boosting).</li>
<li>2012: <b>AlexNet</b> vince ImageNet con apprendimento end-to-end dai pixel alla classe ("ImageNet moment").</li>
</ul>
<p>Il libro distingue tre modi di "programmare" la visione: scrivere regole a mano, derivare l'algoritmo da un modello del mondo, oppure <b>impararlo dai dati</b> (coppie input/output). Il corso li attraversa tutti e tre. <a href="https://visionbook.mit.edu/taxonomy.html">Cap. 1</a></p></div>
""")

s(20, "Human Perception", "<p>Cosa ci insegna il nostro sistema visivo: prior, contesto, elaborazione pesante.</p>", kind="div", sec=("l1-percezione", "Percezione umana", "slide 20–29"))

s(21, "Looking at Pixels", """
<p><b>Figura:</b> un'immagine minuscola (32×32 pixel a colori) di una persona che scrive a una scrivania, con un computer, una tazza blu e dei fogli. A sinistra i pixel sono mostrati come quadrati, a destra la stessa immagine interpolata (sfocata).</p>
<ul>
<li>Nonostante la risoluzione bassissima riconosciamo quasi tutto il contenuto.</li>
<li>La versione sfocata è più facile da leggere di quella a quadrati: i bordi netti dei pixel sono "struttura falsa" che disturba (tornerà in L6 con l'interpolazione).</li>
</ul>
<div class="box b"><b>Dal libro · cap. 3, § 3.2 Looking at Individual Pixels</b><p>È la Figura 3.1 del libro (immagine generata e poi ridotta a 32×32). Il libro fa notare che la penna è lunga circa tre pixel: un pixel grigio scuro vicino ad altri simili, circondato da pixel bianchi. Quello che rende il pixel una "penna" non è la sua intensità ma il resto dell'immagine. <a href="https://visionbook.mit.edu/visionscience.html">Cap. 3</a></p></div>
""")

s(22, "Looking at Pixels (patch isolate)", """
<p><b>Figura:</b> tre piccole patch ritagliate dall'immagine precedente e mostrate da sole: un blocco di pixel marroni (la mano), uno blu (la tazza), uno chiaro con qualche pixel scuro (la zona della penna).</p>
<ul>
<li>Fuori dal loro contesto le patch sono <b>quasi impossibili da riconoscere</b>.</li>
<li>Il significato di un pixel non sta nel suo valore: nasce dal <b>contesto</b>.</li>
</ul>
<p>Conseguenza per gli algoritmi: servono rappresentazioni che guardino regioni ampie (campo recettivo grande nelle CNN, attenzione globale nei ViT).</p>
""")

s(23, "Human prior", """
<p><b>Figura:</b> una foto molto sfocata di un ufficio: si "vede" una persona seduta alla scrivania che parla al telefono, con davanti un computer e una tastiera.</p>
<p>Prima di passare alla slide dopo: prova a dire cosa c'è nell'immagine. La risposta che dà quasi chiunque è guidata dal <b>contesto</b> (ufficio, scrivania), non dai dettagli, che non ci sono.</p>
""")

s(24, "Human prior (versione nitida)", """
<p><b>Figura:</b> la stessa scena a piena risoluzione. La persona tiene all'orecchio una <b>scarpa</b>, non un telefono; il "computer" è un <b>cestino rovesciato</b>; sulla scrivania ci sono anche un tostapane e una spillatrice.</p>
<ul>
<li>Nella versione sfocata il cervello ha completato la scena con gli oggetti <b>più probabili</b> in quel contesto.</li>
<li>È la forza dei prior (con poca informazione indovinano quasi sempre) e il loro rischio (quando la scena è insolita, sbagliano con sicurezza).</li>
</ul>
<div class="box b"><b>Dal libro · cap. 1, § 1.3.2 Helmholtz: Perception as Inference</b><p>Helmholtz descrive la percezione come <b>inferenza inconscia</b>: vediamo gli oggetti che, in condizioni normali, produrrebbero le sensazioni che riceviamo, cioè la spiegazione più probabile dei dati. Il libro nota il legame con i metodi <b>bayesiani</b>: prior sul mondo più verosimiglianza dell'immagine. La scena della scarpa è esattamente un caso in cui il prior vince su dati troppo poveri. <a href="https://visionbook.mit.edu/taxonomy.html">Cap. 1</a></p></div>
""")

s(25, "Blind spot test", """
<ul>
<li>La percezione visiva umana è il risultato di una <b>elaborazione pesante</b> da parte del cervello.</li>
<li>Esempio: ogni occhio ha un <b>punto cieco</b> (dove il nervo ottico lascia la retina e non ci sono fotorecettori), che il cervello <b>riempie per interpolazione</b> senza che ce ne accorgiamo.</li>
</ul>
<p><b>Figura:</b> il test di Wikipedia con una R e una L. Chiudi l'occhio destro, fissa la L con il sinistro a una distanza dallo schermo di circa tre volte la distanza fra le lettere, e avvicinati o allontanati: a un certo punto la R sparisce, e al suo posto vedi lo sfondo uniforme.</p>
<p>Il cervello non mostra un "buco": inventa il contenuto più plausibile. È un prior percettivo al livello più basso.</p>
""")

s(26, "Perception vs Measurement", """
<p><b>Figura:</b> l'illusione della scacchiera di <b>Adelson</b> (checker-shadow): un cilindro verde proietta un'ombra su una scacchiera. Il quadrato A (scuro, in luce) e il quadrato B (chiaro, in ombra) hanno <b>lo stesso valore di grigio</b> nell'immagine, ma B sembra molto più chiaro.</p>
<ul>
<li>Il sistema visivo non misura la luce che arriva: stima la <b>riflettanza</b> della superficie, "scontando" l'ombra.</li>
<li>Come misura è un errore, come percezione è corretto: B è davvero una casella chiara.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 1, § 1.2.2 The Output: Measuring Light Versus Measuring Scene Properties</b><p>Il libro usa questa illusione (Figura 1.2c) per dire che la visione <b>non è fotometria</b>: l'uscita desiderata non è l'intensità luminosa ma proprietà della scena (superfici, materiali, oggetti). Il sistema visivo inferisce la scena 3D più probabile che ha prodotto l'immagine. Nella stessa figura ci sono l'occlusione di un quadrato (lo vediamo intero anche se è coperto) e i tavoli di Shepard (due piani identici nel disegno sembrano di forma diversa perché li interpretiamo in 3D). <a href="https://visionbook.mit.edu/taxonomy.html">Cap. 1</a></p></div>
""")

s(27, "3D Perception", """
<p><b>Figura:</b> due disegni fatti solo di segmenti rettilinei. Quello a sinistra si legge come una superficie <b>orizzontale</b> (un pavimento a piastrelle visto in prospettiva), quello a destra come una superficie <b>verticale</b> (un muro).</p>
<ul>
<li>Da poche linee 2D il sistema visivo ricava subito un'interpretazione 3D.</li>
<li>L'indizio è la prospettiva: le linee parallele nel 3D convergono verso <b>punti di fuga</b>.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 3, § 3.6 Horizontal or Vertical</b><p>Nel libro i due disegni sono lo stesso disegno ruotato di 90°. La differenza percepita dipende da dove sta la linea che unisce i due punti di fuga, cioè l'<b>orizzonte</b>: orizzontale a sinistra, verticale a destra. Siccome ci aspettiamo che l'orizzonte sia orizzontale, a sinistra vediamo un pavimento e a destra un muro. Punti di fuga e orizzonte tornano nella parte di geometria del corso. <a href="https://visionbook.mit.edu/visionscience.html">Cap. 3</a></p></div>
""")

s(28, "3D Perception: Motion Blur", """
<p><b>Figura:</b> foto di Parigi di notte scattata da un'auto in movimento: semafori, auto e alberi in primo piano sono molto mossi, la Torre Eiffel sullo sfondo è quasi nitida.</p>
<ul>
<li>Il mosso è <b>più forte per gli oggetti vicini</b> e più debole per quelli lontani.</li>
<li>Quindi anche un "difetto" dell'immagine contiene un'informazione 3D: la <b>profondità relativa</b>.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 3, § 3.7 Motion Blur</b><p>Durante l'esposizione il sensore accumula luce mentre la camera si sposta: l'immagine è la <b>media di tante copie traslate</b> della scena. In una traslazione della camera gli oggetti vicini si spostano nell'immagine più di quelli lontani, quindi vengono mediati su una lunghezza maggiore. Media di copie traslate = convoluzione con un kernel di blur: è lo stesso modello che tornerà in L3 e L5. <a href="https://visionbook.mit.edu/visionscience.html">Cap. 3</a></p></div>
""")

s(29, "Summary", """
<ul>
<li>La percezione umana usa automaticamente il <b>contesto</b> e "sconta" i fattori di disturbo (<i>nuisance</i>), come gli effetti della luce.</li>
<li>Per costruire sistemi robusti servono <b>prior simili</b>.</li>
<li>Oggi il modo principale per ottenere questi prior sono i <b>sistemi appresi</b> dai dati.</li>
</ul>
<div class="box k"><b>Da saper dire all'orale</b><p>Un prior è un'ipotesi su come è fatto il mondo che rende risolvibile un problema mal posto. Esempi dalla lezione: il cervello riempie il punto cieco, sconta l'ombra (Adelson), completa una scena sfocata con gli oggetti più probabili (la scarpa). Nel sistema a blocchi del libro i prior sono scritti a mano come equazioni; nei sistemi moderni sono appresi dai dati.</p></div>
""")

s(30, "Unifying Themes in Computer Vision", "<p>Quattro idee che ritornano in quasi tutti gli argomenti del corso.</p>", kind="div", sec=("l1-temi", "Temi unificanti", "slide 30–37"))

s(31, "Unifying Themes in Computer Vision", """
<ul>
<li><b>Corrispondenza</b>: trovare "lo stesso punto" in immagini diverse.</li>
<li><b>Vincoli geometrici</b>: modelli di camera, geometria multi-vista.</li>
<li><b>Apprendimento di rappresentazioni</b>: feature ed embedding.</li>
<li><b>Coerenza temporale</b>: video e moto.</li>
</ul>
<p>Mappa sul programma: la corrispondenza e la geometria sono la seconda parte del corso (keypoint, omografie, calibrazione, stereo); le rappresentazioni apprese sono la terza (CNN, ViT, self-supervised).</p>
""")

s(32, "Correspondence", """
<ul>
<li><b>Corrispondenza</b>: date due o più immagini della stessa scena, trovare quale pixel o regione di una corrisponde a quale dell'altra.</li>
<li>Si usa per:
<ul>
<li><b>panorami</b> (allineare foto sovrapposte);</li>
<li><b>stereo e profondità</b> (matching fra vista sinistra e destra);</li>
<li><b>tracking</b> (seguire un oggetto nei frame di un video);</li>
<li><b>structure-from-motion / SLAM</b> (matching fra molte viste per ricostruire il 3D).</li>
</ul></li>
<li><b>Approccio classico</b>: rilevare keypoint distintivi, descriverli, fare il matching per similarità dei descrittori.</li>
<li><b>Approccio moderno</b>: matcher appresi, densi (tutti i pixel) o sparsi (solo alcuni punti).</li>
</ul>
""")

s(33, "Correspondence Example: Matching Points Between Two Photos", """
<p><b>Figura:</b> due versioni affiancate della foto di un'astronauta, collegate da linee verdi fra keypoint corrispondenti (occhi, bordi della tuta, stemmi). La seconda versione è la stessa foto vista con una deformazione prospettica.</p>
<ul>
<li>Ogni linea è una corrispondenza trovata confrontando i descrittori locali.</li>
<li>Le linee quasi parallele e ordinate indicano match coerenti con un'unica trasformazione; un match sbagliato si vedrebbe come una linea che "taglia" le altre.</li>
</ul>
<p>Collegamento: keypoint e descrittori sono L7–L8, la stima della trasformazione (omografia) viene subito dopo.</p>
""")

s(34, "Geometric Constraints", """
<ul>
<li>Le camere seguono un <b>modello geometrico</b>: la proiezione prospettica.</li>
<li>La prospettiva impone <b>vincoli rigidi</b> su come i punti possono spostarsi fra viste:
<ul>
<li>le proiezioni di un punto 3D in due immagini sono legate dalla geometria delle camere: <b>vincolo epipolare</b>;</li>
<li>le proiezioni di una scena <b>piana</b> sono legate da una sola matrice 3×3: <b>omografia</b>.</li>
</ul></li>
<li>Questi vincoli permettono di passare da corrispondenze 2D a <b>struttura 3D</b> e di <b>scartare i match sbagliati</b> (verifica geometrica).</li>
</ul>
<p><b>Figura:</b> una camera su treppiede inquadra dei blocchi colorati appoggiati su un piano, con gli assi X, Y, Z del mondo e l'angolo θ di inclinazione; a destra l'immagine vista dalla camera con gli assi sovrapposti. È lo stesso impianto del mondo a blocchi del cap. 2 (§ 2.3, camera inclinata di θ rispetto al piano di terra).</p>
<div class="box k"><b>Da capire</b><p>Il vincolo epipolare riduce la ricerca del corrispondente di un punto da tutta l'immagine (2D) a una retta (1D). L'omografia fa di più: dato un punto, il corrispondente è determinato. Per questo l'omografia vale solo per scene piane (o per camere che ruotano senza traslare).</p></div>
""")

s(35, "Geometry Example: Triangulation and 3D from 2D", """
<ul>
<li>Se lo stesso punto 3D è visto da due camere <b>calibrate</b>, le sue due proiezioni 2D più le posizioni delle camere lo determinano in modo <b>univoco</b> (a meno del rumore).</li>
<li>È la <b>triangolazione</b>: l'inverso geometrico della proiezione, reso ben posto dall'uso di <b>due viste invece di una</b>.</li>
<li>Si generalizza a molte viste: structure-from-motion, stereo.</li>
</ul>
<p><b>Figura:</b> due modi di stimare la distanza d di una barca dalla costa. A sinistra un osservatore su una scogliera di altezza nota h misura l'angolo α sotto l'orizzonte. A destra due osservatori sulla costa, a distanza t fra loro, misurano gli angoli α e β.</p>
<div class="box w"><b>Attenzione: la didascalia descrive solo metà figura</b><p>La didascalia parla di due raggi che si intersecano, ma solo il pannello di destra è triangolazione con due viste. Quello di sinistra usa <b>una sola vista</b> più un'informazione nota a priori (l'altezza h): d = h / tan(α). È un buon esempio di come un <b>prior</b> rende risolvibile il caso a una vista.</p></div>
<div class="box b"><b>Dal libro · cap. 40, § 40.2.1 How Far Away Is a Boat?</b><p>È la Figura 40.2. Con due osservatori a distanza t (la <b>baseline</b>) che misurano gli angoli α e β, i due raggi e la baseline formano un triangolo di cui si conoscono un lato e due angoli, e il libro ricava</p>
<span class="f">d = t · sin(α) sin(β) / sin(α + β)</span>
<p>Più la baseline è piccola rispetto a d, più α + β si avvicina a 180° e la stima diventa sensibile agli errori sugli angoli. Lo stesso principio, con due camere, dà la profondità dallo stereo (cap. 40, § 40.2.2 e § 40.3.1). <a href="https://visionbook.mit.edu/3d_scene_understanding_stereo.html">Cap. 40 Stereo Vision</a></p></div>
<div class="box k"><b>Da saper fare</b><p>Verifica la formula: il terzo angolo del triangolo è 180° − α − β, e sin(180° − α − β) = sin(α + β). Per il teorema dei seni la distanza dall'osservatore con angolo α alla barca è t · sin β / sin(α + β); la distanza della barca dalla costa (altezza del triangolo) è questa per sin α.</p></div>
""")

s(36, "Representation Learning", """
<ul>
<li>Una <b>rappresentazione</b> (feature, embedding) è una trasformazione dei pixel grezzi in un vettore più utile per il task a valle.</li>
<li>Una buona rappresentazione è:
<ul>
<li><b>invariante</b> ai fattori di disturbo che non dovrebbero cambiare la risposta (luce, punto di vista, scala);</li>
<li><b>discriminativa</b> per i fattori che invece contano (identità, categoria).</li>
</ul></li>
<li><b>Classico</b>: la trasformazione si progetta a mano (es. SIFT: istogrammi di gradienti costruiti per essere invarianti a rotazione e scala).</li>
<li><b>Moderno</b>: la trasformazione si impara dai dati (feature di CNN/ViT, embedding contrastivi o self-supervised).</li>
<li>Stesso problema di fondo (una descrizione compatta e invariante dell'aspetto), filosofie di progetto diverse.</li>
</ul>
<div class="box k"><b>Il compromesso da ricordare</b><p>Invarianza e discriminatività tirano in direzioni opposte: una feature invariante a tutto (es. una costante) è inutile, una che distingue tutto (i pixel grezzi) non è invariante a niente. Esempio: l'invarianza alla rotazione è utile per riconoscere un oggetto, ma distruggerebbe la differenza fra "6" e "9".</p></div>
""")

s(37, "Temporal Consistency", """
<ul>
<li>Nei video i frame consecutivi sono <b>molto correlati</b>: oggetti e camera si muovono in modo regolare.</li>
<li><b>Coerenza temporale</b>: le uscite devono essere coerenti nel tempo; identità, posizione ed etichetta di un oggetto non devono "sfarfallare" da un frame all'altro.</li>
<li>Collega la corrispondenza al tempo: si fa il matching di punti e oggetti <b>fra frame</b> invece che fra viste statiche.</li>
</ul>
<p><b>Figura:</b> una strada pedonale ripresa dall'alto con le traiettorie di diversi pedoni disegnate come scie colorate di riquadri: ogni persona mantiene la stessa identità lungo tutto il percorso (tracking).</p>
""")

s(38, "Samples of State-of-the-art Methods", "<p>Una carrellata di sistemi recenti, per avere un'idea di cosa si sa fare oggi.</p>", kind="div", sec=("l1-sota", "Esempi di stato dell'arte", "slide 38–45"))

s(39, "Computational Photography", """
<p>Link: blog di Google Research sulla riduzione di rumore e sfocatura in Google Photos.</p>
<p><b>Figura:</b> schema a due fasi su una foto rumorosa di un edificio con la scritta Google. Fase <b>pull</b>: l'immagine viene ridotta a risoluzioni via via più basse (livelli 1, 2, 3), dove il rumore si attenua. Fase <b>push</b>: si risale livello per livello fino all'output finale ripulito.</p>
<p>È una <b>piramide</b> multiscala come quelle di L6: il rumore è soprattutto ad alta frequenza, quindi ai livelli grossolani la struttura si stima meglio e poi si usa per guidare i livelli fini.</p>
""")

s(40, "BiomedParse", """
<p>Link: repository GitHub di Microsoft BiomedParse, un modello unico per segmentazione (e riconoscimento) in immagini biomediche di modalità diverse.</p>
<p><b>Figura:</b> quattro esempi, predizione del modello (riga sopra) contro ground truth (riga sotto): infezione COVID-19 in TC del torace (Dice 0.93), glioma in risonanza cerebrale (0.97), COVID-19 in radiografia del torace (0.93), strutture ghiandolari in istologia del colon (0.97).</p>
<div class="box x"><b>Il coefficiente di Dice</b><p>Misura la sovrapposizione fra maschera predetta P e vera G:</p>
<span class="f">Dice = 2 |P ∩ G| / (|P| + |G|)</span>
<p>Vale 1 per sovrapposizione perfetta e 0 per maschere disgiunte. È la metrica standard in segmentazione medica.</p></div>
""")

s(41, "Segment Anything V2", """
<p>Link: pagina Meta di <b>SAM 2</b>, modello di segmentazione "promptable" per immagini e video.</p>
<p><b>Figura:</b> tre pannelli: selezione di oggetti che vengono seguiti attraverso i frame di un video (una palla su un campo); segmentazione robusta anche in video mai visti (organismi al microscopio); interattività in tempo reale (una bevanda versata da un bollitore accanto a un fuoco da campo).</p>
<ul>
<li>L'utente indica l'oggetto con un prompt (click, riquadro, maschera) e il modello lo segmenta e lo segue nel tempo.</li>
<li>Funziona <b>zero-shot</b>: oggetti e domini non visti in addestramento. Unisce segmentazione e coerenza temporale (slide 37).</li>
</ul>
""")

s(42, "Depth Anything V2", """
<p>Link: pagina del progetto Depth Anything V2, <b>stima della profondità da una sola immagine</b> (monoculare).</p>
<p><b>Figura:</b> cinque immagini (un ponte in bianco e nero, un interno, una scena affollata, un disegno a matita, una farfalla su fiori) con le mappe di profondità di Marigold, Depth Anything V1 e V2 a confronto. Sotto, un grafico a barre di latenza, parametri e accuratezza sul benchmark proposto dagli autori: Marigold 5.2 s e 948M parametri, DepthFM 2.1 s e 891M, Depth Anything V2 Large 213 ms e 335M, Small 60 ms e 25M, con accuratezza più alta per i due modelli V2.</p>
<ul>
<li>La profondità da una sola vista è mal posta (slide 12): funziona solo perché la rete ha imparato <b>prior</b> sul mondo da moltissimi dati.</li>
</ul>
<div class="box x"><b>Lettura critica</b><p>L'accuratezza è misurata sul benchmark proposto dagli stessi autori: è un confronto utile, ma va preso con cautela. Il libro tratta questo tema nel cap. 43 <a href="https://visionbook.mit.edu/3d_learning.html">Learning to Estimate Depth from a Single Image</a>.</p></div>
""")

s(43, "DINOv3", """
<p>Link: pagina Meta di <b>DINOv3</b>, backbone di visione addestrato in modo <b>self-supervised</b> (senza etichette).</p>
<p><b>Figura:</b> tre pannelli: analisi delle componenti principali delle feature su un'immagine aerea (le feature separano da sole regioni diverse, colorate in modo diverso); object detection su una scena di ciclismo in montagna; la famiglia di modelli ViT di dimensioni diverse.</p>
<ul>
<li>Le feature dense ad alta risoluzione di un solo backbone, <b>senza fine-tuning</b>, servono a detection, segmentazione, stima di profondità.</li>
<li>È l'esempio concreto di "representation learning" della slide 36.</li>
</ul>
""")

s(44, "Robotics Control", """
<p>Link: blog Google su <b>RT-1</b> (Robotics Transformer) e su <b>PaLM-E</b> (modello linguistico multimodale "embodied").</p>
<p><b>Figura:</b> griglia di frame di un braccio robotico in diverse cucine e uffici che afferra e sposta oggetti (lattine, frutta, sacchetti).</p>
<ul>
<li>La visione qui non è il fine ma serve all'<b>azione</b>: immagini (e istruzioni in linguaggio) in ingresso, comandi al robot in uscita.</li>
<li>È il legame con la robotica citato nella slide 4.</li>
</ul>
""")

s(45, "Efficiently Reconstructing Dynamic Scenes One D4RT at a Time", """
<p>Link: pagina del paper <b>D4RT</b>, indicato come best paper a CVPR 2026: ricostruzione 3D di scene <b>dinamiche</b> (che si muovono) da video.</p>
<p><b>Figura (metodo):</b> un encoder con self-attention globale trasforma il video in una <b>rappresentazione latente della scena</b>. Un decoder leggero con cross-attention si interroga con una query: la posizione 3D P del pixel (u, v) del frame sorgente t<sub>src</sub>, all'istante t<sub>tgt</sub>, nel sistema di riferimento della camera t<sub>cam</sub>. La query contiene anche un embedding della patch locale attorno a (u, v). Esempio: una farfalla su un sasso ricostruita nel tempo.</p>
<ul><li>Mette insieme i quattro temi della lezione: corrispondenza, geometria 3D, rappresentazioni apprese e tempo.</li></ul>
<div class="box w"><b>Attenzione: secondo link sbagliato</b><p>Sotto il link di D4RT la slide ripete il link del blog di RT-1 (robotica, slide 44), che con D4RT non c'entra: è un residuo di copia-incolla. Il link giusto è solo il primo.</p></div>
""")

s(46, "Course Organization", "<p>Programma, docenti, prerequisiti, esame, laboratori, libri.</p>", kind="div", sec=("l1-corso", "Organizzazione del corso", "slide 46–57"))

s(47, "Course Outline and Topics", """
<p><b>Parte 1 · Segnali e immagini</b>:</p>
<ul>
<li>formazione dell'immagine, camera, colore (L2);</li>
<li>convoluzione e trasformata di Fourier (L3);</li>
<li>blur e derivate dell'immagine (L5);</li>
<li>aliasing e rappresentazioni multiscala (L6);</li>
<li>laboratori (L4, L7).</li>
</ul>
""")

s(48, "Course Outline and Topics", """
<p><b>Parte 2 · Corrispondenza e geometria</b>:</p>
<ul>
<li>rilevamento di keypoint;</li>
<li>matching e omografie;</li>
<li>modelli di camera e prospettiva;</li>
<li>calibrazione della camera;</li>
<li>principi di visione stereo;</li>
<li>laboratori.</li>
</ul>
""")

s(49, "Course Outline and Topics", """
<p><b>Parte 3 · Rappresentazioni visive apprese</b>:</p>
<ul>
<li>CNN e ViT;</li>
<li>detection e segmentazione;</li>
<li>apprendimento self-supervised;</li>
<li>modelli visione-linguaggio;</li>
<li>modelli di diffusione;</li>
<li>laboratori in PyTorch.</li>
</ul>
""")

s(50, "Course Outline and Topics", """
<p><b>Parte 4 · Applicazioni avanzate e sfide</b>:</p>
<ul>
<li>personalizzazione di modelli preaddestrati;</li>
<li>adattamento continuo (continual learning);</li>
<li>deployment;</li>
<li>robustezza;</li>
<li>incertezza e detection in mondo aperto (open world).</li>
</ul>
""")

s(51, "Lecturers", """
<ul>
<li>Docenti: <b>Antonio Carta</b> e <b>Donald Shenaj</b> (foto nella slide).</li>
<li>Ufficio al Dipartimento di Informatica.</li>
<li>Ricevimento: scrivere una email per prenotare un orario.</li>
</ul>
""")

s(52, "Prerequisites", """
<p>Nessun prerequisito formale, ma si dà per scontata la familiarità con i corsi del primo anno:</p>
<ul>
<li>algebra lineare e ottimizzazione;</li>
<li>probabilità;</li>
<li>machine learning;</li>
<li>concetti base di deep learning;</li>
<li>un minimo di PyTorch: saper addestrare una rete semplice.</li>
</ul>
""")

s(53, "Exam", """
<ul>
<li><b>Solo esame orale</b>.</li>
<li>Forse preceduto da un breve test a risposta multipla (es. 5 domande semplici).</li>
<li>Quest'anno <b>niente prove intermedie</b>.</li>
</ul>
""")

s(54, "Lab Sessions", """
<ul>
<li>Laboratori: <b>notebook</b> da eseguire ed esplorare.</li>
<li>Scopo: sperimentare per capire i <b>limiti dei metodi</b> e vedere applicazioni semplici e ricette di codice.
<ul>
<li>scrivere cosa ci si aspetta <b>prima</b> di ogni esperimento e cosa si è visto <b>dopo</b> (ipotesi e analisi);</li>
<li>cambiare gli iperparametri e osservare cosa cambia.</li>
</ul></li>
<li>Non si tratta di memorizzare API o librerie.</li>
<li><b>Non valutati</b>; si può usare qualunque strumento di AI.</li>
</ul>
""")

s(55, "Software Tools", """
<ul>
<li><b>scipy/numpy</b>: image processing classico in Python (filtri, trasformate, feature).</li>
<li><b>OpenCV</b>: la libreria standard di visione classica e geometria delle camere (C++/Python); nel corso si usano i binding Python.</li>
<li><b>Kornia</b>: visione differenziabile in PyTorch; le operazioni classiche (filtri, geometria, feature) come operazioni tensoriali differenziabili, su GPU.</li>
<li><b>PyTorch/timm</b>: framework di deep learning e libreria di modelli di visione preaddestrati (CNN, ViT).</li>
</ul>
""")

s(56, "Books on Deep Learning", """
<ul>
<li><b>Goodfellow, Bengio, Courville</b>, <i>Deep Learning</i> (<a href="https://www.deeplearningbook.org/">deeplearningbook.org</a>): riferimento per i metodi standard fino alle CNN (2016), senza ViT e diffusione. Le parti 1 e 2 vanno sapute bene, la parte 3 non serve.</li>
<li><b>Prince</b>, <i>Understanding Deep Learning</i> (<a href="https://udlbook.github.io/udlbook/">udlbook</a>): più moderno, PDF gratuito, con notebook sul sito.</li>
</ul>
""")

s(57, "Books on Computer Vision", """
<p>Il <b>riferimento principale sono le slide</b>. Libri:</p>
<ul>
<li><b>Torralba, Isola, Freeman</b>, <i>Foundations of Computer Vision</i> (<a href="https://visionbook.mit.edu/">visionbook.mit.edu</a>): versione web gratuita, riferimento principale per la visione classica (con poche eccezioni). Nelle slide è indicato come "visionbook".</li>
<li><b>Szeliski</b>, <i>Computer Vision: Algorithms and Applications</i>, 2a ed. (<a href="https://szeliski.org/Book/">szeliski.org/Book</a>): PDF gratuito, buono come riferimento ma leggero sui dettagli.</li>
<li>Facoltativo, per chi vuole approfondire la geometria multi-vista (non necessario): <b>Hartley &amp; Zisserman</b>, <i>Multiple View Geometry in Computer Vision</i>.</li>
</ul>
<p>Negli appunti di questo sito il visionbook è usato come base delle spiegazioni: vedi le sezioni "Studia dal libro" di ogni lezione.</p>
""")

s(58, "Conclusion", "<p>Chiusura della lezione.</p>", kind="div")

s(59, "Key Takeaways", """
<ul>
<li>La computer vision è il <b>problema inverso della grafica</b>: ricavare struttura e significato della scena dalle immagini. È intrinsecamente <b>mal posto</b> e richiede <b>prior</b>.</li>
<li>È difficile per <b>illuminazione, punto di vista, occlusione, scala e variazione intra-classe</b>, tutte insieme.</li>
<li>La nostra comprensione intuitiva delle immagini viene da <b>prior forti</b>, uso del <b>contesto</b> ed <b>elaborazione pesante</b>.</li>
<li>I metodi sfruttano <b>corrispondenza, vincoli geometrici, apprendimento di rappresentazioni e coerenza temporale</b>.</li>
</ul>
""")

s(60, "Further Reading", """
<ul>
<li><a href="https://visionbook.mit.edu/taxonomy.html">visionbook cap. 1, The Challenge of Vision</a>.</li>
<li>(facoltativo) <a href="https://visionbook.mit.edu/simplesystem.html">visionbook cap. 2, A Simple Vision System</a>: esempio pratico di cosa le tecniche classiche sanno e non sanno fare in un mondo giocattolo.</li>
</ul>
<p>Consiglio: leggi anche il <a href="https://visionbook.mit.edu/visionscience.html">cap. 3, Looking at Images</a>, da cui vengono molte figure della parte sulla percezione (slide 21–28). Dettagli nella sezione "Studia dal libro".</p>
""")

s(61, "Next Lecture", """
<p><b>Lezione 2 · Formazione dell'immagine</b>:</p>
<ul>
<li>modello diretto e formazione dell'immagine (il "forward model" della slide 11);</li>
<li>modello della camera pinhole;</li>
<li>luce e colore.</li>
</ul>
""")
