s(1, "Copertina", """
<p><b>Stereo Vision and Depth Prediction</b>. Tredicesima lezione (la data sulla copertina è 12 ottobre 2026).</p>
<p>Finora (L11–L12) si è costruito il modello della camera, che porta un punto 3D in un pixel, e lo si è stimato con la calibrazione. Qui si affronta il problema inverso più importante: <b>da uno o più pixel risalire alla profondità</b>, cioè alla terza coordinata che la proiezione butta via.</p>
<ul>
<li>Prima parte: perché una foto sola è ambigua e quali <b>indizi monoculari</b> usiamo comunque (prospettiva, tessitura, foschia, occlusioni).</li>
<li>Seconda parte: <b>visione stereo</b> classica, cioè triangolazione e disparità, rettificazione, stereo matching denso e sparso, geometria epipolare con le matrici <b>essenziale</b> e <b>fondamentale</b>.</li>
<li>Terza parte: stima della profondità con <b>reti neurali</b>, sia da coppie stereo sia da una sola immagine.</li>
</ul>
<p>Due notebook (in fondo alla pagina): linee epipolari con SIFT e <code>findFundamentalMat</code>, e mappa di disparità con <code>StereoBM</code> sulla coppia Tsukuba.</p>
""")

s(2, "Introduction", "<p>Perché una sola immagine non basta, e cosa aggiunge una seconda camera.</p>", kind="div", sec=("l13-intro", "Introduzione", "slide 2–7"))

s(3, "Objectives", """
<ul>
<li><b>Indizi prospettici</b> in una singola immagine.</li>
<li>Stima della profondità con la <b>visione stereo</b>: rettificazione, matching, triangolazione.</li>
<li>Stima della profondità con le <b>reti neurali profonde</b>.</li>
</ul>
<p>Sono i tre blocchi della lezione, nell'ordine. Nel libro corrispondono ai capitoli 42–43 (una vista) e 40 (stereo).</p>
""")

s(4, "Motivation", """
<ul>
<li>Una foto sola è <b>ambigua in profondità</b>: un pixel può corrispondere a <b>qualunque punto</b> del raggio 3D che passa per il centro della camera e per quel pixel (la proiezione prospettica di L2 divide per Z e perde Z).</li>
<li>Esistono però <b>indizi di profondità</b> (depth cues): linee che convergono, densità della tessitura, occlusioni, foschia.</li>
<li>Una <b>seconda camera</b> aggiunge un vincolo geometrico: i raggi delle due viste si <b>intersecano</b> in un punto 3D. È l'idea della triangolazione (slide 17).</li>
</ul>
<p><b>Figura</b> (Wikimedia Commons): binari ferroviari che si allontanano. Le due rotaie sono parallele in 3D ma nell'immagine convergono verso un unico punto: il <b>punto di fuga</b>, il primo indizio monoculare.</p>
""")

s(5, "Motivation", """
<p><b>Figura</b>: a sinistra un gatto sdraiato su una coperta; a destra la mappa "foreground score" prodotta con le feature di <b>DINOv3</b> (notebook di esempio del repository facebookresearch/dinov3): il gatto è giallo (primo piano), lo sfondo viola.</p>
<ul>
<li>Il messaggio della slide: <b>indizi di profondità e conoscenza a priori</b> permettono di capire cosa sta davanti anche da una sola vista.</li>
<li>Nota: la figura mostra una segmentazione primo piano / sfondo, non una mappa di profondità metrica. È un ordinamento qualitativo (cosa è davanti), che una rete impara dai dati senza alcuna geometria esplicita.</li>
</ul>
""")

s(6, "Perspective Cues", """
<p><b>Figura 3</b> (Wikimedia): pianta della <b>stanza di Ames</b>. La stanza vera è un trapezio: l'angolo sinistro della parete di fondo è molto più lontano dallo spioncino di quello destro. La persona A sta nell'angolo lontano, la persona B in quello vicino; dallo spioncino la stanza appare rettangolare ("apparent shape of room") e A sembra stare alla stessa distanza di B.</p>
<p><b>Figura 4</b> (Wikimedia): una stanza di Ames in uso in un museo. Due persone sulla parete di fondo sembrano di statura molto diversa: in realtà sono a distanze diverse.</p>
""")

s(7, "Perspective Cues", """
<ul>
<li>Gli indizi prospettici sono <b>ipotesi e bias</b> (ad esempio che le superfici siano piane e gli angoli retti) che in genere funzionano nelle immagini naturali, soprattutto negli ambienti costruiti dall'uomo.</li>
<li>La <b>stanza di Ames</b> è una stanza trapezoidale deformata, costruita in modo che pavimento, soffitto e parete di fondo (deformati) proiettino, da <b>uno specifico spioncino</b>, la stessa immagine di una stanza rettangolare normale.</li>
<li>Noi assumiamo la rettangolarità e ricaviamo una geometria 3D <b>sbagliata</b>: le persone sembrano cambiare altezza invece di cambiare distanza.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 42, § 42.2 A Few Notes about Perception of Depth by Humans</b><p>Il libro presenta la stanza di Ames (inventata da Adelbert Ames nel 1946) come prova di quanto siano forti i meccanismi 3D della percezione: la parete di fondo è più grande dove è più lontana, così appare frontale. Il libro propone anche di costruirne una di carta (fig. 42.3): il pavimento si disegna con un'omografia di una pianta quadrata. Un oggetto spostato lungo la parete di fondo sembra cambiare dimensione, e la percezione ignora del tutto il fatto che le persone non cambiano altezza. Lo stesso paragrafo apre con un disegno di sole linee (fig. 42.2, slide 10) in cui vediamo comunque una strada con edifici. <a href="https://visionbook.mit.edu/3d_scene_understanding_single_view.html" target="_blank">Cap. 42</a>.</p></div>
<div class="box k"><b>Da saper spiegare</b><p>Perché l'illusione funziona solo da un punto: la proiezione perde la profondità, quindi infinite scene 3D danno la stessa immagine. La stanza deformata è una di queste scene, scelta apposta; da un altro punto di vista (o con due occhi) le immagini non coincidono più e l'illusione si rompe.</p></div>
""")

s(8, "Monocular Depth Cues", "<p>Gli indizi di profondità disponibili in una sola immagine.</p>", kind="div", sec=("l13-monoculare", "Indizi monoculari", "slide 8–14"))

s(9, "Depth Perception in Humans", """
<ul>
<li>L'occhio <b>non misura</b> la profondità: è una camera pinhole, fa una proiezione 2D.</li>
<li>Il sistema visivo ricostruisce la struttura 3D da:
<ul><li>indizi in una <b>singola immagine</b>;</li>
<li>indizi di <b>movimento</b>;</li>
<li><b>visione binoculare</b> (stereo).</li></ul></li>
</ul>
<p>Nei sistemi di computer vision:</p>
<ul>
<li>bisogna capire <b>quando</b> funzionano gli indizi da una sola immagine (sono ipotesi, slide 7);</li>
<li>bisogna formalizzare i <b>vincoli geometrici</b> fra più viste (seconda parte);</li>
<li>il movimento si tratta spesso come un caso particolare di viste multiple, nel tempo (camera che si muove = più viste della stessa scena).</li>
</ul>
""")

s(10, "Pictorial Depth Cues: Lines", """
<p><b>Figura</b> (visionbook, fig. 42.2): un disegno a sole linee nere, ricostruito da una foto di Mezzanotte e Biederman. Si vedono subito una strada in prospettiva, edifici alti a destra, edifici bassi e un'auto in basso a sinistra.</p>
<ul>
<li>Sono solo segmenti su un foglio piano, eppure la percezione 3D è immediata e non si può "spegnere".</li>
<li>Il libro nota che vediamo anche oggetti e contesto (strada, marciapiede, cielo fra gli edifici) quando il marciapiede è una sola linea: la geometria delle linee e il contesto bastano.</li>
</ul>
""")

s(11, "Pictorial Depth Cues: Lines", """
<p><b>Figura</b> (visionbook, fig. 42.7): l'illusione della <b>torre pendente</b>. Due foto <b>identiche</b> della torre di Pisa, vista dal basso, affiancate: quella di destra sembra più inclinata di quella di sinistra.</p>
<ul>
<li>Spiegazione del libro: le linee verticali di ciascuna torre convergono verso un proprio <b>punto di fuga</b>. Se le due torri fossero parallele in 3D, le loro linee convergerebbero allo <b>stesso</b> punto di fuga; dato che i punti di fuga sono diversi, il cervello conclude che le torri hanno orientazioni 3D diverse.</li>
<li>È automatico: sapere che le foto sono identiche non cambia la percezione.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 42, § 42.3.2 Vanishing Points</b><p>Una retta 3D P<sub>t</sub> = P<sub>0</sub> + tD si proietta in x<sub>t</sub> = f(X<sub>0</sub> + tD<sub>X</sub>)/(Z<sub>0</sub> + tD<sub>Z</sub>), y<sub>t</sub> analoga. Per t → ∞ il punto proiettato tende a</p>
<span class="f">v = ( f D<sub>X</sub>/D<sub>Z</sub> ,  f D<sub>Y</sub>/D<sub>Z</sub> )</span>
<p>che dipende <b>solo dalla direzione D</b>: tutte le rette parallele convergono allo stesso punto di fuga. Se D<sub>Z</sub> = 0 (rette parallele al piano immagine) il punto di fuga è all'infinito e le rette restano parallele nell'immagine. In omogenee il punto all'infinito della retta è [D; 0] e v = K R D (eq. 42.5): il punto di fuga dipende dalla rotazione della camera ma <b>non dalla traslazione</b>. Due camere traslate (una coppia stereo) vedono gli stessi punti di fuga. <a href="https://visionbook.mit.edu/3d_scene_understanding_single_view.html" target="_blank">Cap. 42</a>.</p></div>
""")

s(12, "Pictorial Depth Cues: Perspective", """
<p><b>Figura</b> (visionbook, fig. 42.8): foto di una piazza con edifici porticati e pavimento a piastrelle. Due fasci di rette sul pavimento (verdi e azzurre, lungo i due lati delle piastrelle) convergono in due punti di fuga, uno a sinistra e uno a destra; la retta rossa che li unisce è la <b>linea dell'orizzonte</b> ("horizon line"). Anche le linee orizzontali della facciata convergono a un punto di fuga sulla stessa retta.</p>
<ul>
<li>Tutte le famiglie di rette parallele contenute in un piano hanno punti di fuga <b>allineati</b>: la retta che li contiene è l'orizzonte di quel piano.</li>
<li>Piani paralleli hanno lo stesso orizzonte.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 42, § 42.3.3 Horizon Line</b><p>Il piano del suolo è speciale perché sostiene gli oggetti: la distanza nell'immagine fra il punto di contatto di un oggetto con il suolo e l'orizzonte dice quanto è lontano (più è lontano, più il punto di contatto sale verso l'orizzonte). In coordinate omogenee tutto si fa con prodotti vettoriali: il punto di fuga è l'intersezione l<sub>1</sub> × l<sub>2</sub> di due rette immagine di rette parallele, e l'orizzonte è il prodotto vettoriale di due punti di fuga (fig. 42.9). È la linea dell'orizzonte y = a tanθ già vista in L12. <a href="https://visionbook.mit.edu/3d_scene_understanding_single_view.html" target="_blank">Cap. 42</a>.</p></div>
""")

s(13, "Pictorial Depth Cues: Texture and Haze", """
<p><b>Figura</b> (visionbook, fig. 43.1):</p>
<ul>
<li><b>Sinistra</b>: una superficie metallica a bugne regolari vista di sbieco. Contiene più indizi insieme: <b>ombreggiatura</b> (shading: ogni bugna ha un lato chiaro e uno scuro, quindi appare in rilievo), <b>gradiente di tessitura</b> (le bugne diventano più piccole e fitte verso l'alto, cioè più lontane), <b>prospettiva lineare</b> (le file di bugne convergono).</li>
<li><b>Destra</b>: una valle di montagna. Le montagne lontane hanno contrasto più basso e tinta più azzurrina di quelle vicine: è la <b>prospettiva aerea</b> (o atmosferica), dovuta alla diffusione della luce nell'aria.</li>
</ul>
""")

s(14, "Pictorial Depth Cues", """
<ul>
<li><b>Occlusione</b>: un oggetto che ne copre parzialmente un altro è più vicino. Dà solo l'ordine, non la distanza.</li>
<li><b>Dimensione relativa / familiare</b>: un oggetto più piccolo, o più piccolo della sua dimensione reale nota, è più lontano. Con oggetti di dimensione nota (persone) dà anche distanze <b>assolute</b>.</li>
<li><b>Gradiente di tessitura</b>: una superficie a tessitura uniforme (erba, piastrelle, ghiaia) si proietta in una tessitura sempre più fitta e minuta con la distanza.</li>
<li><b>Ombreggiatura</b> (shading): con direzione della luce nota, l'intensità vincola l'orientazione locale della superficie.</li>
<li><b>Prospettiva aerea</b>: la diffusione atmosferica riduce il contrasto e sposta il colore verso il blu / la foschia con la distanza (conta solo a grandi distanze).</li>
<li><b>Prospettiva lineare</b>: rette parallele nella scena 3D convergono in punti di fuga.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 43, § 43.2 Monocular Depth Cues</b><p>Il libro elenca gli stessi indizi e aggiunge ombre e interriflessioni (l'esempio della pallina e della sua ombra è nel cap. 3, § 3.9 Cues for Support, fig. 3.11: la posizione dell'ombra rispetto all'oggetto dice se tocca il suolo). Per lo shading rimanda allo <b>shape from shading</b>: invertire le equazioni di rendering, dato che la luce riflessa dipende da albedo, intensità della luce e angolo fra luce e normale. Osservazione chiave: quasi tutti questi indizi danno profondità <b>relativa</b>; solo le dimensioni note danno una scala assoluta. Il libro conclude che invece di modellare ogni indizio a mano conviene <b>imparare</b> a combinarli dai dati (§ 43.4, slide 45). <a href="https://visionbook.mit.edu/3d_learning.html" target="_blank">Cap. 43</a>.</p></div>
""")

s(15, "Stereo Vision", "<p>Due viste, triangolazione e disparità.</p>", kind="div", sec=("l13-stereo", "Visione stereo e triangolazione", "slide 15–20"))

s(16, "Stereo Vision", """
<p><b>Figura</b> (visionbook, fig. 40.1): (a) un <b>anaglifo</b> del Titanic: due foto scattate da camere spostate lateralmente e sovrapposte, la vista destra in rosso e la sinistra in ciano; (b) gli occhiali rosso/ciano, uno per occhio.</p>
<ul>
<li>Con gli occhiali ogni occhio vede solo una delle due foto e la nave "esce" in 3D.</li>
<li>Lo spostamento relativo fra le due immagini (ad esempio dei fumaioli) <b>cambia con la profondità</b>: è questa differenza, la <b>disparità</b>, che il cervello trasforma in profondità.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 40, § 40.1–40.2</b><p>Il libro divide il problema in due parti, trattate con tecniche diverse: (1) la <b>geometria</b> delle proiezioni, che permette di triangolare la profondità una volta noti gli spostamenti; (2) il <b>calcolo degli spostamenti</b> fra le parti corrispondenti delle due immagini (matching). Gli <b>stereogrammi a punti casuali</b> di Julesz (fig. 40.3) mostrano che la disparità da sola basta: due immagini di rumore identiche salvo un quadrato spostato di qualche pixel fanno vedere un quadrato che fluttua, senza nessun altro indizio. Nota del libro (§ 40.3.3): nel Titanic la disparità dei fumaioli <b>cresce</b> con la profondità, al contrario della formula della slide 19, perché le due camere non erano parallele. <a href="https://visionbook.mit.edu/3d_scene_understanding_stereo.html" target="_blank">Cap. 40</a>.</p></div>
""")

s(17, "Triangulation", """
<p><b>Idea</b>: con due viste si fa <b>triangolazione</b>, cioè si ricava la posizione di un punto 3D misurando angoli e distanze noti. Esempio della barca vista dalla costa (visionbook, fig. 40.2):</p>
<ul>
<li><b>Sinistra</b>, una sola vista: un osservatore su un rilievo di altezza nota h misura l'angolo α fra l'orizzontale e la direzione della barca. La distanza dalla base del rilievo è
<span class="f">d = h / tan α</span></li>
<li><b>Destra</b>, due viste: due osservatori sulla costa a distanza t misurano gli angoli α e β fra la congiungente e la direzione della barca. La distanza della barca dalla congiungente è
<span class="f">d = t · sin α · sin β / sin(α + β)</span></li>
<li>Formule ricavate da identità trigonometriche; poco precise se h e t non sono grandi.</li>
</ul>
<p>Nota: nel testo estratto dal PDF la prima formula appare come "d = tanh α", ma è un artefatto dell'estrazione: la slide stampata scrive correttamente la frazione h / tan α, come il libro (§ 40.2.1).</p>
<div class="box k"><b>Da saper fare: ricavare la seconda formula</b><p>Nel triangolo osservatore 1, osservatore 2, barca l'angolo alla barca è π − α − β. Per il teorema dei seni la distanza fra osservatore 1 e barca è t · sin β / sin(α + β) (perché sin(π − α − β) = sin(α + β)). La distanza d dalla costa è il cateto opposto ad α: d = t sin β / sin(α + β) · sin α. Verificato numericamente (t = 1, α = 60°, β = 50°: d = 0.706 sia dalla formula sia intersecando le due rette).</p></div>
<div class="box b"><b>Dal libro · cap. 40, § 40.2.1 How Far Away Is a Boat?</b><p>Il libro precisa le due condizioni: il primo metodo richiede un punto di osservazione alto e, per barche lontane, di tenere conto della curvatura della Terra; il secondo richiede una base t abbastanza grande perché gli angoli si discostino in modo apprezzabile da 90°. Se α e β sono entrambi quasi 90°, sin(α + β) è quasi 0 e un piccolo errore di angolo dà un grande errore di distanza: è lo stesso motivo per cui in stereo la profondità dei punti lontani è poco precisa. <a href="https://visionbook.mit.edu/3d_scene_understanding_stereo.html" target="_blank">Cap. 40</a>.</p></div>
""")

s(18, "Triangulation", """
<p><b>Nota</b>: per semplicità si assume che le due camere differiscano solo per una <b>traslazione orizzontale</b> T (camere identiche, assi ottici paralleli).</p>
<ul><li>Z si trova con la similitudine dei triangoli.</li></ul>
<p><b>Figura</b> (visionbook, fig. 40.5): (a) le due camere con i loro assi (X, Y, Z) e i piani immagine; il punto P si proietta in x<sub>L</sub> nella camera sinistra e x<sub>R</sub> nella destra, alla stessa altezza y. (b) La vista dall'alto, cioè la sola riga dell'immagine che contiene il punto: i due centri ottici distanti T sulla base, i piani immagine a distanza f sopra di essi, P in cima a distanza Z.</p>
<ul>
<li>Poiché le camere sono allineate orizzontalmente, <b>y<sub>L</sub> = y<sub>R</sub></b>: il problema si riduce a una riga, cioè a un problema 2D visto dall'alto.</li>
</ul>
""")

s(19, "Triangulation", """
<p>Dalla similitudine dei triangoli (giallo e giallo + arancione nella figura):</p>
<span class="f">(T + x<sub>R</sub> − x<sub>L</sub>) / (Z − f) = T / Z</span>
<p>Risolvendo per Z:</p>
<span class="f">Z = f T / (x<sub>L</sub> − x<sub>R</sub>)</span>
<ul>
<li>x<sub>L</sub> − x<sub>R</sub> è la <b>disparità</b>: la profondità è <b>inversamente proporzionale</b> alla disparità.</li>
<li>f e T sono parametri che dipendono dalle camere (focale e <b>baseline</b>).</li>
<li>La slide aggiunge che la disparità si può stimare anche con camere non calibrate (vedi riquadro).</li>
</ul>
<p><b>Figura</b> (visionbook, fig. 40.5b): il triangolo grande ha base T (fra i due centri ottici) e altezza Z; quello giallo ha il vertice in P e la base sul piano immagine, all'altezza f, fra i due punti x<sub>L</sub> e x<sub>R</sub>.</p>
<div class="box k"><b>Da saper fare: derivazione senza figura</b><p>Camera sinistra nell'origine, destra in (T, 0, 0), assi x verso destra. Un punto (X, Y, Z) si proietta in x<sub>L</sub> = fX/Z e x<sub>R</sub> = f(X − T)/Z. Sottraendo: x<sub>L</sub> − x<sub>R</sub> = fT/Z, quindi Z = fT/(x<sub>L</sub> − x<sub>R</sub>). Con questa convenzione la disparità è positiva. La base del triangolo giallo è T − (x<sub>L</sub> − x<sub>R</sub>) = T + x<sub>R</sub> − x<sub>L</sub>, che è il numeratore della formula della slide.</p></div>
<div class="box x"><b>Approfondimento: attenzione ai versi degli assi nella figura</b><p>La figura del libro disegna X<sub>L</sub> e X<sub>R</sub> con la freccia verso <b>sinistra</b>. Con quel verso le coordinate dei due punti immagine cambiano segno e la stessa costruzione darebbe Z = fT/(x<sub>R</sub> − x<sub>L</sub>). La formula della slide e del libro (eq. 40.1) è giusta con x crescente verso destra e la camera destra in +T: conviene ricordarla così, e ricordare che la disparità di un punto davanti alle camere deve venire positiva.</p></div>
<div class="box k"><b>Da capire bene: «disparità anche con camere non calibrate»</b><p>È vero nel senso che la disparità si misura in pixel, confrontando le due immagini, senza conoscere f e T: per questo le reti stimano la disparità (slide 39). Ma due condizioni restano: (1) il confronto riga per riga richiede immagini <b>rettificate</b>, e rettificare richiede almeno la matrice fondamentale (che si stima dai match, slide 37) o la calibrazione; (2) per passare dalla disparità alla profondità metrica servono comunque f e T. Senza calibrazione la disparità dà solo profondità <b>relative</b> (Z ∝ 1/d).</p></div>
<div class="box k"><b>Da saper fare: sensibilità all'errore</b><p>Derivando Z = fT/d: |∂Z/∂d| = fT/d² = Z²/(fT). Un errore di un pixel nella disparità pesa sulla profondità come Z²: raddoppiando la distanza l'errore quadruplica. Per migliorare la precisione sui punti lontani si aumenta la baseline T o la focale f (stessa conclusione della barca, slide 17).</p></div>
""")

s(20, "Depth estimation", """
<p><b>Depth prediction</b>: dato un punto 2D dell'immagine, stimare la sua profondità 3D.</p>
<p>Per risolverla con la triangolazione servono tre passi:</p>
<ol>
<li><b>Rettificazione</b>: avere due viste allineate correttamente (le coordinate delle due camere differiscono solo per una traslazione nota, orizzontale, come nella slide 18).</li>
<li><b>Stereo matching</b>: per un punto p<sub>L</sub> della camera sinistra trovare il corrispondente p<sub>R</sub> nella camera destra.</li>
<li><b>Calcolo della profondità</b>: calcolare la disparità e risolvere la triangolazione, Z = fT/d.</li>
</ol>
<p>È lo schema di tutta la seconda parte. Il passo difficile è il secondo; il primo serve a renderlo una ricerca 1D.</p>
""")

s(21, "Rectification", "<p>Allineare le due immagini in modo che i punti corrispondenti stiano sulla stessa riga.</p>", kind="div", sec=("l13-rettificazione", "Rettificazione", "slide 21–22"))

s(22, "Why Rectify", """
<ul>
<li>Si vedrà (slide 33–35) che i punti corrispondenti stanno su rette chiamate <b>linee epipolari</b>.</li>
<li>Se le due viste differiscono per una traslazione <b>orizzontale</b>, le linee epipolari sono le <b>righe</b> della griglia dei pixel.
<ul><li>Con una coppia di camere qualunque le linee epipolari sono oblique e orientate in modo diverso nelle due immagini.</li>
<li>Nel caso generale l'algoritmo dovrebbe seguire una retta arbitraria per confrontare i pixel.</li></ul></li>
<li>Il vincolo "corrispondenti sulla stessa riga" è molto comodo, quindi lo si <b>impone</b> come pre-elaborazione.</li>
<li>La <b>rettificazione</b> deforma (warp) le immagini in modo che:
<ul><li>le linee epipolari corrispondenti diventino <b>orizzontali</b>;</li>
<li>le linee epipolari corrispondenti nelle due immagini cadano sulla <b>stessa riga</b>.</li></ul></li>
</ul>
<p><b>Risultato</b>: dopo la rettificazione la ricerca delle corrispondenze è una ricerca <b>1D</b> lungo righe (scanline) corrispondenti.</p>
<div class="box w"><b>Attenzione: non basta una traslazione qualunque</b><p>La slide dice "se le due viste sono legate solo da una traslazione, le linee epipolari sono le righe" (e la slide 20 parla di "una traslazione nota"). Serve una traslazione <b>parallela all'asse x delle immagini</b>, con camere identiche. Controesempio: una camera che avanza lungo il proprio asse ottico (traslazione pura lungo Z) ha l'epipolo al centro dell'immagine e linee epipolari <b>radiali</b>, non orizzontali; con una traslazione verticale le linee epipolari sono le colonne. La slide 18 lo dice correttamente ("traslazione orizzontale"); il libro (§ 40.3.5) chiede piani dei sensori complanari e righe collineari.</p></div>
<div class="box b"><b>Dal libro · cap. 40, § 40.3.5 Image Rectification</b><p>Le immagini rettificate si ottengono con <b>omografie</b> (cap. 41, come i panorami di L9–L10): si sintetizzano le immagini che si sarebbero ottenute con camere allineate. Una procedura: (1) ruotare ciascuna camera in modo che siano parallele fra loro e con l'asse ottico perpendicolare alla congiungente dei centri; (2) ruotare ciascuna attorno al proprio asse ottico per allineare le righe; (3) scalare uniformemente un'immagine perché abbia la stessa dimensione dell'altra. Ruotare una camera attorno al suo centro è un'omografia, per questo basta un warp con interpolazione bilineare (§ 21.4.2). Il libro assume camere calibrate, ma osserva che altri algoritmi richiedono meno: basta conoscere la <b>matrice fondamentale</b>. In OpenCV: <code>stereoRectify</code> (camere calibrate) e <code>stereoRectifyUncalibrated</code> (da F e dai match). <a href="https://visionbook.mit.edu/3d_scene_understanding_stereo.html" target="_blank">Cap. 40</a>.</p></div>
""")

s(23, "Stereo Matching", "<p>Trovare, per ogni pixel della sinistra, il corrispondente nella destra.</p>", kind="div", sec=("l13-matching", "Stereo matching", "slide 23–31"))

s(24, "From Rectified Images to Disparity", """
<ul>
<li>Dopo la rettificazione le due immagini di un punto 3D, p<sub>L</sub> = (x<sub>L</sub>, y) e p<sub>R</sub> = (x<sub>R</sub>, y), hanno la <b>stessa riga</b> y.
<ul><li>Bisogna trovare i match pixel per pixel lungo le righe.</li></ul></li>
<li><b>Disparità</b>: d = x<sub>L</sub> − x<sub>R</sub>, <b>maggiore per i punti vicini</b>, minore per quelli lontani (Z = fT/d).</li>
</ul>
<p><b>Stereo matching</b>: per ogni pixel dell'immagine sinistra (L) trovare il pixel più simile nell'immagine destra (R) sulla stessa riga.</p>
<div class="box k"><b>Da saper dire</b><p>Con la convenzione di slide 19 il punto nell'immagine destra sta <b>a sinistra</b> del corrispondente (x<sub>R</sub> = x<sub>L</sub> − d con d ≥ 0): la ricerca va fatta solo in una direzione e fino a una disparità massima, legata alla distanza minima della scena (d<sub>max</sub> = fT/Z<sub>min</sub>). Un punto all'infinito ha d = 0.</p></div>
""")

s(25, "Stereo Matching", """
<p><b>Figura</b> (visionbook, fig. 40.6): due foto di un ufficio scattate a circa 1 m di distanza l'una dall'altra (libreria, scrivania rotonda, finestra). Rettangoli colorati marcano alcuni elementi riconoscibili nella foto sinistra e la loro posizione nella destra; le frecce gialle mostrano gli spostamenti.</p>
<ul>
<li>A occhio il matching è facile: si localizza un dettaglio in un'immagine e lo si cerca nell'altra in base alla somiglianza della regione attorno.</li>
<li>Gli spostamenti hanno ampiezze diverse: gli oggetti vicini alla camera si spostano di più. Farlo <b>automaticamente</b> e per ogni pixel è il cuore del problema stereo.</li>
</ul>
""")

s(26, "Dense Stereo Matching", """
<ul>
<li>Nel matching <b>denso</b> si cerca un corrispondente per <b>ogni</b> pixel di L fra i pixel di R.
<ul><li>Le immagini sono rettificate, quindi la ricerca si limita alla stessa riga.</li></ul></li>
<li>Per decidere quale pixel corrisponde serve una misura di <b>somiglianza locale</b>, ad esempio la somma delle differenze al quadrato delle intensità fra due patch (finestre) di L e di R.</li>
</ul>
<p>Si confrontano patch e non pixel singoli perché un'intensità sola è uguale in moltissimi punti della riga (slide 29): la finestra rende la "firma" del pixel più distintiva.</p>
""")

s(27, "Cost Volume and Block Matching", """
<ul>
<li>Un <b>cost volume</b> C(x, y, d) misura quanto una piccola patch attorno a (x, y) in L somiglia alla patch attorno a (x − d, y) in R, per ogni disparità candidata d.
<ul><li>La ricerca è limitata a una disparità massima.</li></ul></li>
<li>Il <b>block matching</b> confronta finestre di dimensione fissa con misure semplici e veloci:
<ul><li><b>SAD</b>, somma delle differenze assolute;</li>
<li><b>SSD</b>, somma delle differenze al quadrato;</li>
<li><b>NCC</b>, correlazione incrociata normalizzata, robusta a differenze di luminosità e contrasto fra le due camere.</li></ul></li>
<li>La disparità stimata in ogni pixel è il "vincitore":</li>
</ul>
<span class="f">d̂(x, y) = argmin<sub>d</sub> C(x, y, d)   (argmax per NCC, che è una somiglianza)</span>
<div class="box k"><b>Da saper scrivere</b><p>Con finestra W centrata in (x, y):</p>
<span class="f">C<sub>SSD</sub>(x, y, d) = ∑<sub>(u,v)∈W</sub> ( I<sub>L</sub>(x + u, y + v) − I<sub>R</sub>(x + u − d, y + v) )²</span>
<p>NCC: si sottrae la media di ciascuna finestra e si divide per il prodotto delle deviazioni standard; il valore sta in [−1, 1] e non cambia se una delle due immagini viene moltiplicata per un guadagno positivo o sommata a un offset. Il cost volume è un array di dimensione larghezza × altezza × D (D = numero di disparità): è la stessa struttura che le reti neurali costruiscono con le feature (slide 42). La formula della slide è coerente con d = x<sub>L</sub> − x<sub>R</sub>: il candidato in R è x − d.</p></div>
<div class="box x"><b>Approfondimento: costo e dimensione della finestra</b><p>Calcolato in modo ingenuo il costo è proporzionale a pixel × disparità × area della finestra, ma le somme su finestre si fanno con immagini integrali o filtri box (L5) a costo indipendente dalla finestra. La finestra è un compromesso: piccola dà stime rumorose nelle zone uniformi, grande "allarga" gli oggetti in primo piano ai bordi (foreground fattening), perché la finestra a cavallo di un bordo contiene sia primo piano sia sfondo. Si vede nel notebook (sezione Notebook): con blockSize = 15 gli errori stanno quasi tutti lungo i contorni.</p></div>
""")

s(28, "Failure Modes", """
<p><b>Casi in cui il block matching fallisce</b>:</p>
<ul>
<li><b>Regioni senza tessitura</b>: il costo è piatto al variare di d, non c'è un minimo unico.</li>
<li><b>Pattern ripetitivi</b>: molti match ugualmente buoni (minimi multipli).</li>
<li><b>Occlusioni</b>: il punto è visibile in una sola immagine, quindi un match corretto <b>non esiste</b>.</li>
</ul>
<p><b>Metodi globali / semi-globali</b> (ad esempio Semi-Global Matching, SGM):</p>
<ul>
<li>aggiungono un termine di <b>regolarità</b> (smoothness) fra pixel vicini: disparità vicine devono essere simili, salvo ai bordi degli oggetti;</li>
<li>il problema risultante si risolve in modo approssimato;</li>
<li>più lenti, ma gestiscono meglio regioni senza tessitura e ambigue.</li>
</ul>
<div class="box x"><b>Approfondimento: cosa minimizza SGM</b><p>L'energia è E(D) = ∑<sub>p</sub> C(p, d<sub>p</sub>) + ∑<sub>vicini p,q</sub> [P<sub>1</sub> se |d<sub>p</sub> − d<sub>q</sub>| = 1, P<sub>2</sub> se &gt; 1], con P<sub>1</sub> &lt; P<sub>2</sub>: piccoli salti (superfici inclinate) costano poco, grandi salti (bordi) di più. Ottimizzarla su tutta l'immagine è difficile; lungo una sola direzione è una programmazione dinamica esatta. SGM (Hirschmüller 2008) la risolve lungo 8 o 16 direzioni e somma i costi aggregati. In OpenCV è <code>StereoSGBM</code>, con proprio questi parametri P1 e P2 (sezione Notebook). Il libro (§ 40.3.2.3) lo cita insieme al belief propagation (cap. 29) per interpolare fra i match.</p></div>
""")

s(29, "Dense Stereo Matching", """
<p>Sfocare con un filtro che <b>preserva i bordi</b> migliora l'approccio ingenuo basato sulle intensità.</p>
<p><b>Figura</b> (visionbook, fig. 40.7, da Hosni et al. 2013 su dati Middlebury): è la scena <b>Tsukuba</b>, la stessa del notebook (la lampada arancione davanti agli scaffali).</p>
<ul>
<li><b>(a)</b> una riga dell'immagine (c), con la riga marcata in verde.</li>
<li><b>(b)</b> la <b>disparity space image</b>: per ogni posizione orizzontale (asse x) e ogni disparità (asse verticale) l'errore di matching delle intensità di singoli pixel; in rosso la disparità di costo minimo. I punti rossi saltano in modo caotico, mentre le superfici sono lisce.</li>
<li><b>(d)</b> lo stesso costo dopo un filtraggio che preserva i bordi: i minimi (in rosso) formano segmenti orizzontali puliti; (e) la mappa di profondità risultante.</li>
<li><b>(f)</b> le disparità vere e <b>(g)</b> la profondità vera: (d) ed (e) sono molto vicine.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 40, § 40.3.2 Stereo Matching</b><p>Il libro elenca le cause per cui il confronto pixel a pixel è inaffidabile: <b>mancanza di tessitura</b> (molti pixel quasi identici), <b>rumore</b> di intensità, <b>riflessi speculari</b> che cambiano posizione fra le due viste, <b>occlusioni</b>. La soluzione della figura è sfocare la disparity space image (cioè il cost volume, una fetta per riga) con un filtro che preserva i bordi: si aggregano costi vicini senza mescolare oggetti diversi. Il libro chiama i due passi <b>matching</b> e <b>filtering</b>: trovare e accoppiare feature, poi interpolare o regolarizzare per avere una disparità affidabile ovunque. <a href="https://visionbook.mit.edu/3d_scene_understanding_stereo.html" target="_blank">Cap. 40</a>.</p></div>
<div class="box x"><b>Approfondimento: perché un filtro che preserva i bordi</b><p>Una gaussiana (L5) sul cost volume equivale a usare una finestra più grande: riduce il rumore ma sbava le disparità ai bordi degli oggetti. Un filtro edge-preserving (ad esempio il filtro bilaterale o il guided filter usato da Hosni et al.) pesa i pixel vicini in base alla <b>somiglianza di colore</b> nell'immagine guida: si media solo dentro lo stesso oggetto, e il salto di disparità al bordo resta netto.</p></div>
""")

s(30, "Sparse Stereo Matching", """
<p>Si può riusare l'idea dei <b>keypoint</b> (L8–L9) e stimare la profondità solo nei keypoint:</p>
<ul>
<li>estrarre keypoint in L e in R (ad esempio SIFT);</li>
<li>accoppiarli (ad esempio vicino più vicino + <b>ratio test di Lowe</b>);
<ul><li>in una coppia perfettamente rettificata i match corretti sono <b>orizzontali</b> (stessa riga): si può scartare ogni match che non rispetta questo vincolo geometrico.</li></ul></li>
</ul>
<p>Il vincolo geometrico fa qui la parte che in L9 faceva RANSAC con l'omografia: elimina i match sbagliati. Con camere non rettificate il vincolo diventa "il match sta sulla linea epipolare" (slide 37 e notebook).</p>
<div class="box b"><b>Dal libro · cap. 40, § 40.3.2.1–40.3.2.2</b><p>Il libro usa come rilevatore il <b>criterio di Harris</b>: E(Δx, Δy) ≈ [Δx Δy] M [Δx Δy]<sup>⊤</sup>, con M la somma su una patch dei prodotti delle derivate; un buon punto ha l'autovalore minimo di M sopra una soglia (il λ<sub>min</sub> di L8). Poi i descrittori <b>SIFT</b>: istogrammi delle orientazioni locali dei gradienti, sensibili alla struttura ma poco sensibili a cambi di illuminazione e piccoli spostamenti (fig. 40.9, la mano sotto due illuminazioni). <a href="https://visionbook.mit.edu/3d_scene_understanding_stereo.html" target="_blank">Cap. 40</a>.</p></div>
""")

s(31, "Sparse Stereo Matching", """
<ul>
<li>Notare che i keypoint trovati in L e in R sono <b>diversi</b>.</li>
<li>Dopo il matching, la mappa di profondità (a destra) si ottiene con algoritmi di <b>interpolazione</b>.</li>
</ul>
<p><b>Figura</b> (visionbook, fig. 40.8): le due foto dell'ufficio della slide 25 con i punti di Harris (punti verdi). Le ellissi colorate marcano zone in cui i punti rilevati nelle due immagini non coincidono: non tutti i keypoint hanno un corrispondente. A destra la mappa di profondità in scala di grigi ottenuta interpolando i punti accoppiati: è a blocchi, con i contorni degli oggetti solo abbozzati.</p>
<div class="box b"><b>Dal libro · cap. 40, § 40.3.2.3 Interpolation between Feature Matches</b><p>Per interpolare fra le profondità dei punti accoppiati il libro cita metodi probabilistici come il <b>belief propagation</b> (cap. 29), esatto solo se la struttura su cui si ragiona è una catena o un albero; la <b>programmazione dinamica</b> lungo una riga ha lo stesso limite. Il semi-global matching di Hirschmüller applica l'elaborazione 1D lungo molte direzioni per approssimare una soluzione globale (slide 28). <a href="https://visionbook.mit.edu/3d_scene_understanding_stereo.html" target="_blank">Cap. 40</a>.</p></div>
<div class="box k"><b>Denso o sparso?</b><p>Sparso: pochi punti affidabili e distintivi, matching robusto (descrittori invarianti), ma serve interpolare e i bordi vengono male. Denso: una stima per pixel, ma con i problemi della slide 28 nelle zone senza tessitura e serve regolarizzare. Le reti (slide 39–42) sono metodi densi con feature imparate.</p></div>
""")

s(32, "Epipolar Geometry", "<p>Il vincolo geometrico per due camere qualunque: matrici essenziale e fondamentale.</p>", kind="div", sec=("l13-epipolare", "Geometria epipolare", "slide 32–37"))

s(33, "Two Arbitrary Cameras", """
<p><b>Figura</b> (visionbook, fig. 40.10): due camere calibrate in posizione generica, legate da una rotazione R e una traslazione T (freccia verde "R,T"), con assi ottici non paralleli. Nella camera 1 si osserva il punto p<sub>1</sub>; nella camera 2 ci sono diversi candidati p<sub>2</sub>? (punti rossi).</p>
<ul>
<li>Domanda: dove può stare, nell'immagine 2, il corrispondente di p<sub>1</sub>?</li>
<li>Senza vincoli bisognerebbe cercarlo in tutta l'immagine (ricerca 2D).</li>
</ul>
""")

s(34, "Epipolar Lines", """
<p><b>Figura</b> (visionbook, fig. 40.11): il punto 3D che ha prodotto p<sub>1</sub> sta sul <b>raggio</b> (in rosso) che va dal centro della camera 1 attraverso p<sub>1</sub>. Tre possibili posizioni del punto lungo il raggio (pallini rosso, verde, azzurro) si proiettano nella camera 2 in tre punti diversi, tutti allineati sulla retta rossa nell'immagine 2.</p>
<ul>
<li>Una retta 3D si proietta in una retta 2D: l'immagine del raggio nella camera 2 è una retta, la <b>linea epipolare</b> di p<sub>1</sub>.</li>
<li>Il corrispondente p<sub>2</sub> deve stare su quella retta: la ricerca diventa <b>1D</b>.</li>
<li>Due punti della retta sono facili da calcolare se le camere sono calibrate: la proiezione nella camera 2 del <b>centro della camera 1</b> (il pallino nero in basso, che può anche cadere fuori dall'immagine) e la proiezione di un punto qualunque del raggio.</li>
</ul>
""")

s(35, "Epipolar Geometry", """
<p><b>Figura</b> (visionbook, fig. 40.12): i centri delle camere O<sub>1</sub> e O<sub>2</sub>, il punto P e il triangolo giallo che li unisce.</p>
<ul>
<li><b>Piano epipolare</b>: il piano che contiene i due centri ottici e il punto P (il triangolo giallo).</li>
<li><b>Linee epipolari</b>: le intersezioni del piano epipolare con i due piani immagine (rette rosse). Cambiano se P si muove.</li>
<li><b>Epipoli</b> e<sub>1</sub>, e<sub>2</sub>: le intersezioni della retta O<sub>1</sub>O<sub>2</sub> (la <b>baseline</b>, tratteggiata) con i piani immagine. Non dipendono da P: <b>tutte</b> le linee epipolari di un'immagine passano per il suo epipolo.</li>
</ul>
<p>Nella figura le camere sono ruotate solo attorno all'asse verticale e non c'è spostamento verticale, quindi gli epipoli stanno sugli assi x delle due camere.</p>
<div class="box k"><b>Da saper spiegare</b><p>L'epipolo e<sub>2</sub> è il punto dove la camera 2 "vede" il centro della camera 1. Dopo la rettificazione la baseline è parallela ai piani immagine, quindi gli epipoli vanno all'<b>infinito</b> lungo x e le linee epipolari diventano righe parallele (slide 22). Con camere che convergono gli epipoli sono finiti e le linee formano un fascio.</p></div>
<div class="box b"><b>Dal libro · cap. 40, § 40.3.4.4 Epipolar Lines: The Game</b><p>Il libro propone un gioco (fig. 40.13): sei coppie di camere e sei insiemi di linee epipolari da abbinare. La chiave per risolverlo: immaginare come i raggi uscenti da una camera appaiono dall'altra, e ricordare che l'epipolo è dove una camera vede il centro dell'altra. Il libro sottolinea che saper prevedere l'aspetto delle linee epipolari serve a trovare i bug nel codice. La soluzione è nel libro: provare prima da soli. <a href="https://visionbook.mit.edu/3d_scene_understanding_stereo.html" target="_blank">Cap. 40</a>.</p></div>
""")

s(36, "Epipolar Constraint", """
<p><b>Obiettivo</b>: tradurre in un'equazione il vincolo "p<sub>2</sub> va cercato lungo la linea epipolare giusta".</p>
<ul>
<li>Un punto P ha coordinate 3D <b>P<sub>1</sub></b> nel riferimento della camera 1 e <b>P<sub>2</sub></b> nel riferimento della camera 2.</li>
<li>I due riferimenti sono legati da una rotazione R e una traslazione T:</li>
</ul>
<span class="f">P<sub>2</sub> = R P<sub>1</sub> + T</span>
<ul>
<li>In coordinate immagine il punto è p<sub>1</sub> nella camera 1 e p<sub>2</sub> nella camera 2.</li>
</ul>
<div class="box k"><b>Da saper fare: la derivazione di Longuet-Higgins (§ 40.3.4)</b>
<ol>
<li>Prodotto vettoriale di entrambi i membri con T: T × P<sub>2</sub> = T × R P<sub>1</sub> (perché T × T = 0).</li>
<li>Prodotto scalare con P<sub>2</sub>: a sinistra P<sub>2</sub>·(T × P<sub>2</sub>) = 0, perché T × P<sub>2</sub> è ortogonale a P<sub>2</sub>. Quindi
<span class="f">P<sub>2</sub><sup>⊤</sup> [T]<sub>×</sub> R P<sub>1</sub> = 0,   E = [T]<sub>×</sub> R</span></li>
<li>[T]<sub>×</sub> è la matrice antisimmetrica del prodotto vettoriale: [0 −T<sub>3</sub> T<sub>2</sub>; T<sub>3</sub> 0 −T<sub>1</sub>; −T<sub>2</sub> T<sub>1</sub> 0], con [T]<sub>×</sub>b = T × b.</li>
<li>Con f = 1 l'immagine è p = P/Z (vettore [X/Z, Y/Z, 1]); dividendo per Z<sub>1</sub>Z<sub>2</sub> l'equazione vale anche per i punti immagine: p<sub>2</sub><sup>⊤</sup> E p<sub>1</sub> = 0.</li>
</ol>
<p>Geometricamente: P<sub>2</sub>, T e RP<sub>1</sub> (il raggio 1 espresso nel riferimento 2) sono <b>complanari</b>, e il piano che li contiene è il piano epipolare. Verificato numericamente con R, T e punti casuali: |p<sub>2</sub><sup>⊤</sup>Ep<sub>1</sub>| ≈ 10<sup>−16</sup>.</p></div>
<div class="box x"><b>Approfondimento: che cos'è T qui</b><p>Attenzione al confronto con L11–L12: lì T era la posizione del centro della camera nel mondo e compariva −RT. Qui T è il termine di traslazione della trasformazione rigida dal riferimento 1 al riferimento 2: il centro O<sub>1</sub>, che ha P<sub>1</sub> = 0, ha P<sub>2</sub> = T, cioè T è la posizione del centro della camera 1 vista dalla camera 2. È la stessa convenzione di OpenCV (<code>stereoCalibrate</code>, <code>recoverPose</code>).</p></div>
""")

s(37, "Essential and Fundamental Matrix", """
<ul>
<li>Le coordinate dei due punti sono legate da una matrice <b>E</b>, la <b>matrice essenziale</b> (derivazione completa nel libro, riassunta nella scheda 36), tramite il <b>vincolo epipolare</b>:</li>
</ul>
<span class="f">p<sub>2</sub><sup>⊤</sup> E p<sub>1</sub> = 0</span>
<ul>
<li>Dato p<sub>1</sub>, la sua proiezione p<sub>2</sub> nell'altra camera deve soddisfare il vincolo epipolare.</li>
<li>Le coordinate in <b>pixel</b> c<sub>1</sub> e c<sub>2</sub> sono legate allo stesso modo dalla <b>matrice fondamentale</b> F:</li>
</ul>
<span class="f">c<sub>2</sub><sup>⊤</sup> F c<sub>1</sub> = 0</span>
<ul>
<li>E e F si possono stimare con un metodo "tipo DLT" applicato ai vincoli epipolari.</li>
</ul>
<div class="box k"><b>Da saper spiegare: perché è una retta, e la relazione E–F</b>
<ul>
<li>Fissato p<sub>1</sub>, il vettore l<sub>2</sub> = E p<sub>1</sub> = (a, b, c) e il vincolo diventa a x + b y + c = 0: è l'equazione della <b>linea epipolare</b> nell'immagine 2 (rette in omogenee, L9). Simmetricamente l<sub>1</sub> = E<sup>⊤</sup>p<sub>2</sub>.</li>
<li>p sono coordinate <b>normalizzate</b> (camera con f = 1, centro nell'origine): p = K<sup>−1</sup>c. Sostituendo, c<sub>2</sub><sup>⊤</sup>K<sub>2</sub><sup>−⊤</sup> E K<sub>1</sub><sup>−1</sup>c<sub>1</sub> = 0, quindi
<span class="f">F = K<sub>2</sub><sup>−⊤</sup> E K<sub>1</sub><sup>−1</sup>,   E = K<sub>2</sub><sup>⊤</sup> F K<sub>1</sub></span></li>
<li><b>Epipoli</b>: tutte le linee epipolari passano per l'epipolo, quindi E e<sub>1</sub> = 0 ed e<sub>2</sub><sup>⊤</sup>E = 0: gli epipoli sono gli spazi nulli di E e di E<sup>⊤</sup> (§ 40.3.4.3). Lo stesso vale per F in pixel.</li>
</ul></div>
<div class="box k"><b>Da sapere: gradi di libertà e rango</b>
<ul>
<li><b>E</b>: 3 per R + 3 per T, meno 1 di scala = <b>5</b> gradi di libertà; rango 2, con i due valori singolari non nulli <b>uguali</b> (perché [T]<sub>×</sub> ha valori singolari (|T|, |T|, 0) e R non li cambia; verificato numericamente).</li>
<li><b>F</b>: 9 elementi, meno la scala, meno il vincolo det F = 0: <b>7</b> gradi di libertà; rango 2.</li>
<li>E richiede camere calibrate (si lavora in coordinate normalizzate); F si stima direttamente dai pixel, senza conoscere K.</li>
</ul></div>
<div class="box x"><b>Approfondimento: il metodo "tipo DLT" è l'algoritmo degli 8 punti</b><p>Ogni corrispondenza (c<sub>1</sub>, c<sub>2</sub>) dà <b>una</b> equazione lineare nei 9 elementi di F (c<sub>2</sub><sup>⊤</sup>Fc<sub>1</sub> = 0 è il prodotto scalare fra un vettore di 9 monomi x<sub>2</sub>x<sub>1</sub>, x<sub>2</sub>y<sub>1</sub>, … e il vettore f). Con 8 corrispondenze si risolve A f = 0 con la SVD, come per l'omografia (L9) e la matrice della camera (L12): una equazione per punto invece di due, quindi 8 punti invece di 4. Poi si impone il rango 2 azzerando il valore singolare minimo; per E si pongono anche uguali i primi due (§ 40.3.4.2). Come in L9, normalizzare le coordinate prima (Hartley 1997) è essenziale. Usando il vincolo det F = 0 bastano 7 punti, per E 5 punti (Nistér 2004); dentro RANSAC si usano proprio i solutori minimi. Da E si recuperano R e T con la SVD (quattro soluzioni, una sola mette i punti davanti a entrambe le camere), T solo a meno di scala: da due viste non si ricava la scala assoluta.</p></div>
<div class="box b"><b>Dal libro · cap. 40, § 40.3.4.1 The Fundamental Matrix</b><p>Il libro scrive la relazione come F = K<sup>−⊤</sup>EK<sup>⊤</sup>: è un refuso. Da p = K<sup>−1</sup>c segue F = K<sub>2</sub><sup>−⊤</sup>EK<sub>1</sub><sup>−1</sup> (con camere uguali K<sup>−⊤</sup>EK<sup>−1</sup>), come in Hartley-Zisserman (cap. 9). Verificato numericamente: con K<sup>−1</sup> a destra il vincolo vale sui pixel (residuo ≈ 10<sup>−16</sup>), con K<sup>⊤</sup> no. Per il resto il paragrafo conferma la slide: stessa forma algebrica, F incorpora gli intrinseci (dimensione dei pixel e cambio di origine), rango 2 e 7 gradi di libertà. <a href="https://visionbook.mit.edu/3d_scene_understanding_stereo.html" target="_blank">Cap. 40</a>.</p></div>
""")

s(38, "Learning-Based methods", "<p>Reti neurali per la stima della profondità, da due viste e da una sola.</p>", kind="div", sec=("l13-learning", "Metodi basati sull'apprendimento", "slide 38–46"))

s(39, "Learned Stereo Depth Estimation", """
<ul>
<li>Le reti stereo addestrate predicono la <b>disparità</b>, perché non dipende dai parametri della camera.
<ul><li>La profondità è inversamente proporzionale alla disparità (Z = fT/d).</li></ul></li>
<li>Il block matching classico di solito è <b>più veloce</b>.</li>
<li>I metodi appresi sono in genere <b>più accurati</b>, soprattutto nelle regioni difficili (senza tessitura, riflessi, occlusioni).</li>
</ul>
<div class="box b"><b>Dal libro · cap. 40, § 40.4.1 Output Representation</b><p>Il libro dà tre motivi per stimare la disparità: (1) si misura dalle immagini, senza f e T; (2) è più facile modellare il rumore, che si può assumere indipendente dalla disparità, mentre in profondità l'errore cresce con la distanza (vedi la sensibilità ∝ Z², scheda 19); (3) per una superficie <b>piana</b> la derivata seconda della disparità lungo ogni direzione è nulla, ∂²d/∂x² = 0, cosa che per la profondità non vale: un termine di regolarizzazione semplice favorisce i piani. Il libro scrive poi z = 1/d (sottintendendo il fattore fT) e P = z · K<sup>−1</sup>[n, m, 1]<sup>⊤</sup> per passare da ogni pixel al punto 3D. <a href="https://visionbook.mit.edu/3d_scene_understanding_stereo.html" target="_blank">Cap. 40</a>.</p></div>
<div class="box k"><b>Da saper verificare: disparità lineare sui piani</b><p>Un piano aX + bY + cZ = 1 con X = xZ/f, Y = yZ/f dà 1/Z = a x/f + b y/f + c, lineare in x e y; poiché d = fT/Z, anche d è lineare nei pixel, quindi ha derivate seconde nulle.</p></div>
""")

s(40, "Supervised Stereo Depth Estimation", """
<ul>
<li>Disparità predetta: <b>d̂ = f<sub>θ</sub>(v<sub>1</sub>, v<sub>2</sub>)</b>
<ul><li>f è la rete con parametri θ;</li>
<li>v<sub>1</sub>, v<sub>2</sub> sono le due viste.</li></ul></li>
<li>La loss supervisionata è la distanza fra disparità predetta e disparità vera, ad esempio:
<span class="f">J(θ) = ∑<sub>t</sub> | d − f<sub>θ</sub>(v<sub>1</sub>, v<sub>2</sub>) |²</span>
la somma è sulle coppie t del training set (la slide sottintende l'indice t su d, v<sub>1</sub>, v<sub>2</sub>), e |·|² è la norma al quadrato sull'intera mappa, cioè la somma sui pixel.</li>
<li>Addestramento supervisionato standard: θ ottimizzato con SGD per minimizzare la loss.</li>
<li><b>Architettura a due stadi</b>: f(v<sub>1</sub>, v<sub>2</sub>) = c(g(v<sub>1</sub>), g(v<sub>2</sub>))
<ul><li>g elabora le due viste <b>separatamente</b> (la stessa rete, pesi condivisi: rete siamese);</li>
<li>c confronta le feature e produce la disparità.</li></ul></li>
</ul>
<div class="box b"><b>Dal libro · cap. 40, § 40.4.2 Two-Stage Networks</b><p>Il libro indica i dataset con disparità vera da camere stereo calibrate: <b>KITTI</b> e <b>Scene Flow</b> (sintetico). Le due fasi classiche, matching e filtering, possono essere imparate separatamente (Zbontar e LeCun 2015: una CNN che impara il costo di matching) o insieme, end-to-end (GC-Net, PSMNet, GA-Net). La formula della loss è la stessa della slide. <a href="https://visionbook.mit.edu/3d_scene_understanding_stereo.html" target="_blank">Cap. 40</a>.</p></div>
<div class="box x"><b>Approfondimento: loss usate in pratica</b><p>Le reti stereo reali usano spesso la <b>smooth L1</b> (Huber) invece della L2, più robusta agli errori grandi ai bordi e alle etichette rumorose, e calcolano la loss solo sui pixel con disparità vera disponibile (il LiDAR di KITTI è sparso). Il "SGD" della slide qui è appropriato: a differenza della calibrazione di L12, il training set è grande e si usano mini-batch (in pratica Adam o varianti).</p></div>
""")

s(41, "Stereo Depth Prediction architecture", """
<p><b>Figura</b> (visionbook, fig. 40.14, ricavata dagli schemi di PSMNet, GA-Net e GC-Net): da sinistra a destra</p>
<ol>
<li><b>Rectified Stereo Pair</b>: due immagini stradali rettificate, una sopra l'altra;</li>
<li><b>Feature Extraction</b>: un blocco verde (rete convoluzionale) per le immagini;</li>
<li><b>Cost Volume</b>: un parallelepipedo con assi width, height e disparity;</li>
<li><b>Cost Aggregation</b>: un altro blocco verde (rete convoluzionale 3D);</li>
<li><b>Disparity Estimate</b>: la mappa di disparità a colori.</li>
</ol>
<p>È il block matching delle slide 27–29 con ogni pezzo sostituito da una rete: feature imparate invece delle intensità, aggregazione imparata invece del filtro edge-preserving o di SGM.</p>
""")

s(42, "Pipeline", """
<ol>
<li><b>Rettificare</b> la coppia stereo, in modo che le righe corrispondenti delle due immagini mostrino gli stessi punti del mondo.</li>
<li><b>Estrarre feature</b> da ciascuna immagine con una coppia di reti a <b>pesi condivisi</b>.</li>
<li><b>Costruire un cost volume 3D</b> che indichi l'evidenza visiva locale di un match fra le due immagini per ogni posizione di pixel e ogni disparità possibile.</li>
<li><b>Addestrare e applicare una CNN 3D</b> che aggrega i costi sul cost volume e stima una sola disparità per ogni pixel.
<ul><li>Svolge implicitamente il ruolo della regolarizzazione dei metodi non neurali (ad esempio lo smoothing visto nella slide 29).</li></ul></li>
</ol>
<div class="box k"><b>Da saper spiegare: come si costruisce il cost volume con le feature</b><p>Con feature F<sub>L</sub>, F<sub>R</sub> di C canali, per ogni disparità d si confronta F<sub>L</sub>(x, y) con F<sub>R</sub>(x − d, y): o concatenandole (un volume di feature per ogni d, GC-Net e PSMNet) o con un prodotto scalare (correlazione, un numero per ogni d). Pesi condivisi perché il confronto abbia senso: le due viste devono essere descritte nello stesso spazio di feature. Per avere un'uscita <b>differenziabile</b> e sub-pixel non si usa l'argmin ma il <b>soft argmin</b>: d̂ = ∑<sub>d</sub> d · softmax(−C)<sub>d</sub> (Kendall et al. 2017, GC-Net).</p></div>
<div class="box b"><b>Dal libro · cap. 40, § 40.4.2</b><p>Il libro aggiunge che il cost volume si riferisce alle coordinate di una delle due immagini, che le reti con questo schema hanno superato i metodi a feature progettate a mano, e che il limite è il costo in tempo e memoria della rete 3D: RAFT-Stereo (Lipson et al. 2021) lo evita con un algoritmo iterativo, migliorando velocità e prestazioni. Il problema aperto citato è la <b>generalizzazione</b> fuori dal dominio di addestramento, che è il tema delle due slide successive. <a href="https://visionbook.mit.edu/3d_scene_understanding_stereo.html" target="_blank">Cap. 40</a>.</p></div>
""")

s(43, "DNN Generalization", """
<p><b>Figura</b> (Zhang et al., "Domain-invariant Stereo Matching Networks", ECCV 2020):</p>
<ul>
<li>(a) <b>scene di addestramento</b>: sintetiche, oggetti geometrici con texture casuali;</li>
<li>(b) <b>scene di test</b>: una strada reale con auto parcheggiate;</li>
<li>(c) mappa di feature di GA-Net: rumorosa, piena di dettagli di tessitura; (e) la disparità di GA-Net: zone sbagliate e chiazze;</li>
<li>(d) mappa di feature di DSMNet: più uniforme dentro gli oggetti; (f) la disparità di DSMNet: pulita e coerente.</li>
</ul>
<p>Messaggio della slide: una rete progettata per essere invariante al dominio <b>generalizza</b> a domini nuovi (dal sintetico al reale); una rete standard addestrata sul sintetico molto meno.</p>
<div class="box x"><b>Approfondimento: perché il problema esiste</b><p>La disparità vera è costosa da misurare sul reale, quindi si addestra molto su dati sintetici. Le feature imparate possono dipendere da colore, illuminazione e texture del dominio sintetico; DSMNet introduce una normalizzazione di dominio e un filtro non locale guidato dalla struttura dell'immagine per rendere le feature meno sensibili allo stile. Il libro (§ 40.4.2) cita proprio questo lavoro come risposta alla scarsa generalizzazione.</p></div>
""")

s(44, "Sample", """
<p><b>Figura</b> (Zhang et al., ECCV 2020, fig. 7): confronto di modelli addestrati su dati sintetici e valutati su immagini reali ad alta risoluzione (Middlebury e CityScapes). Due righe: una bicicletta in un ufficio e una strada con auto. Colonne: (a) immagine di ingresso, (b) HD³, (c) PSMNet, (d) DSMNet; disparità in falsi colori (rosso = disparità alta, cioè vicino; blu = lontano).</p>
<ul>
<li>HD³ e PSMNet sbagliano vaste zone: parti dello sfondo dell'ufficio e del cielo diventano rosse (falsamente vicine), e la strada di PSMNet ha un grosso triangolo errato.</li>
<li>DSMNet ricostruisce bene la bicicletta (ruote e telaio) e la strada.</li>
</ul>
""")

s(45, "Depth from a single view", """
<ul>
<li>Gli indizi 3D (slide 9–14) permettono di predire la profondità da una sola immagine.</li>
<li>La stima della profondità diventa un problema di <b>regressione per pixel</b>: predire profondità o disparità di ogni pixel.
<span class="f">ℒ(ẑ, z) = ∑<sub>n,m</sub> ( ẑ[n, m] − z[n, m] )²</span>
con ẑ profondità stimata per pixel e z profondità vera per pixel (la slide scrive "groud-truth" per ground truth).</li>
<li><b>Loss "invariante di scala"</b> secondo la slide:
<span class="f">ℒ(ẑ, z) = ∑<sub>n,m</sub> ( ẑ[n, m] − z[n, m] − α )²,   α = (1/NM) ∑<sub>n,m</sub> ( ẑ[n, m] − z[n, m] )</span>
<ul><li>spesso si aggiungono loss esplicite di regolarità (smoothness) per regolarizzare l'uscita.</li></ul></li>
<li>I dataset si raccolgono di solito con sensori di profondità (Kinect, LiDAR).</li>
</ul>
<div class="box w"><b>Attenzione: così è invariante a uno spostamento, non alla scala</b><p>Sottrarre α, la media della differenza, rende la loss invariante all'aggiunta di una <b>costante</b> alla profondità (ẑ + c dà la stessa loss), non alla moltiplicazione per un fattore. Se ẑ = s·z, la differenza ẑ − z = (s − 1)z varia da pixel a pixel e la loss vale (s − 1)² ∑(z − z̄)² ≠ 0. La loss invariante di scala (Eigen, Puhrsch, Fergus, NIPS 2014) si applica ai <b>logaritmi</b>: con g = log ẑ − log z,</p>
<span class="f">ℒ = ∑<sub>n,m</sub> ( g[n, m] − ḡ )²,   ḡ = (1/NM) ∑<sub>n,m</sub> g[n, m]</span>
<p>Ora ẑ = s·z dà g = log s costante, quindi ℒ = 0: la scala globale non viene penalizzata. Verificato numericamente: con s = 2 la formula della slide dà un valore positivo, quella sui log dà 0. Eigen et al. scrivono l'errore come (1/n)∑g² − (λ/n²)(∑g)²: con λ = 1 è esattamente la formula sopra divisa per n, in addestramento usano λ = 0.5. Il libro (§ 43.4.2) riporta la stessa formula della slide senza logaritmo (e senza parentesi nella definizione di α); subito dopo suggerisce di lavorare su log z o su 1/z per non sovrappesare i punti lontani.</p></div>
<div class="box b"><b>Dal libro · cap. 43, § 43.4 Supervised Methods for Depth from a Single Image</b><p>Formulazione: training set di N immagini ℓ<sup>(i)</sup> con mappe di profondità z<sup>(i)</sup>, stima ẑ = h<sub>θ</sub>(ℓ), θ* = argmin (1/N)∑ℒ(ẑ<sup>(i)</sup>, z<sup>(i)</sup>). <b>§ 43.4.1</b>: i dati vengono da sensori RGB-D (NYUv2, Kinect a mano in interni), LiDAR (KITTI, da un'auto), coppie stereo, o ricostruzioni multi-vista con structure from motion (MegaDepth). <b>§ 43.4.2</b>: la L2 assume di poter stimare la profondità assoluta, ma da una sola immagine la profondità è spesso nota solo a meno di un fattore di scala globale, da cui la loss invariante. Si possono aggiungere termini sulle derivate della profondità per una ricostruzione più coerente. <a href="https://visionbook.mit.edu/3d_learning.html" target="_blank">Cap. 43</a>.</p></div>
<div class="box x"><b>Approfondimento: perché la scala è ambigua</b><p>Una scena ingrandita di un fattore s e allontanata dello stesso fattore dà la stessa immagine (la proiezione dipende da X/Z e Y/Z). Una rete può fissare la scala solo dagli oggetti di dimensione nota (slide 14): per questo molti metodi stimano profondità "relativa" (a meno di scala, o di scala e spostamento sulla disparità) e la calibrano dopo con una misura reale, come fa il libro con la nuvola di punti dell'ufficio (§ 43.4.3).</p></div>
""")

s(46, "Single View Encoder", """
<p><b>Figura</b> (visionbook, fig. 43.4): architettura tipica per la profondità da una sola immagine. A sinistra la foto di un airone; un <b>encoder</b> di blocchi (Convolution, Non-linearity, Downsample) riduce la risoluzione; un <b>decoder</b> di blocchi (Convolution, Non-linearity, Upsample) la riporta alla dimensione dell'ingresso; frecce orizzontali collegano i livelli corrispondenti (<b>skip connection</b>); a destra la mappa di profondità a falsi colori, con l'airone in primo piano.</p>
<ul>
<li>È uno schema tipo U-Net: l'encoder raccoglie il contesto globale (dove sta il suolo, quali oggetti ci sono), il decoder ricostruisce una mappa densa, le skip connection riportano i dettagli fini persi nel sottocampionamento (bordi netti).</li>
<li>Il libro sottolinea che l'architettura è generica, la stessa che si userebbe per altri compiti densi: sono i dati e la loss a farne uno stimatore di profondità.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 43, § 43.3 e § 43.4.3</b><p>Una mappa di profondità con K noto diventa una <b>nuvola di punti</b>: P = z(p) K<sup>−1</sup>p, cioè X = (n − c<sub>x</sub>) z/a, Y = (m − c<sub>y</sub>) z/a, Z = z (eq. 43.1). Il libro consiglia di valutare una stima guardando la nuvola di punti da altri punti di vista (fig. 43.6): la mappa a colori sembra buona anche quando la geometria non lo è, e i punti vicino alle discontinuità sono spesso sbagliati (media fra primo piano e sfondo). Le mappe si visualizzano con la colormap <b>turbo</b>, perché jet ha un profilo di luminosità non monotono. <a href="https://visionbook.mit.edu/3d_learning.html" target="_blank">Cap. 43</a>.</p></div>
<div class="box x"><b>Approfondimento: senza etichette (§ 43.5)</b><p>Il libro descrive anche l'addestramento <b>non supervisionato</b> da video: una rete f<sub>1</sub> stima la profondità di un fotogramma, una rete f<sub>2</sub> il moto R, T fra due fotogrammi; con K noto si proietta ogni pixel in 3D, lo si sposta con R, T e lo si riproietta (ℓ<sub>1→2</sub>(p) = ℓ<sub>1</sub>(K M̂ ẑ(p) K<sup>−1</sup>p), backward warping con interpolazione bilineare); la loss è l'errore fotometrico fra il fotogramma ricostruito e quello vero, mascherato sui pixel validi. Serve un moto con traslazione: una camera che solo ruota dà un'omografia indipendente dalla profondità (L9).</p></div>
""")

s(47, "Conclusions", "<p>I messaggi da portare a casa e i riferimenti.</p>", kind="div", sec=("l13-conclusioni", "Conclusioni", "slide 47–49"))

s(48, "Key Takeaways", """
<ul>
<li>Gli <b>indizi prospettici</b> permettono di stimare la profondità da una sola vista (sono ipotesi sulla scena: possono ingannare, come la stanza di Ames).</li>
<li>Nella visione stereo i <b>vincoli geometrici</b> riducono la ricerca delle corrispondenze fra vista sinistra e destra da <b>2D a 1D</b> (vincolo epipolare, p<sub>2</sub><sup>⊤</sup>Ep<sub>1</sub> = 0).
<ul><li>La <b>rettificazione</b> allinea le linee epipolari con la griglia dei pixel.</li>
<li>Il <b>matching</b> fra le due viste più la <b>triangolazione</b> (Z = fT/d) danno la profondità.</li></ul></li>
<li>La <b>disparità</b> è la quantità chiave sia nei metodi classici sia in quelli basati su reti.</li>
</ul>
""")

s(49, "References", """
<ul>
<li>visionbook, <a href="https://visionbook.mit.edu/3d_scene_understanding_stereo.html" target="_blank">cap. 40 Stereo Vision</a>.</li>
<li>Valutazione dei metodi di stima della profondità allo stato dell'arte: <a href="https://vision.middlebury.edu/stereo/eval3/" target="_blank">Middlebury Stereo Evaluation, versione 3</a> (il libro, § 40.5, la indica per confrontare gli algoritmi su dati comuni; la coppia Tsukuba del notebook viene dal dataset Middlebury del 2001).</li>
</ul>
<p>Per le altre parti della lezione: <a href="https://visionbook.mit.edu/3d_scene_understanding_single_view.html" target="_blank">cap. 42 Single View Metrology</a> (stanza di Ames, punti di fuga, orizzonte) e <a href="https://visionbook.mit.edu/3d_learning.html" target="_blank">cap. 43 Learning to Estimate Depth from a Single Image</a> (indizi monoculari, loss, encoder-decoder). Per approfondire: Hartley e Zisserman, <i>Multiple View Geometry</i>, cap. 9–11 (geometria epipolare, matrice fondamentale e sua stima); Szeliski 2a ed., cap. 12 Depth estimation (sottoparagrafi non verificati); Scharstein e Szeliski 2002 (tassonomia degli algoritmi stereo densi); Hirschmüller 2008 (SGM).</p>
""")
