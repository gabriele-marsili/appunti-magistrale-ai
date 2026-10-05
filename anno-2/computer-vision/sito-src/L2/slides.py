
s(1, "Copertina", """
<p><b>Image Formation: Cameras and Color</b>. Seconda lezione.</p>
<p>Si studia il <b>modello diretto</b> (forward model): come la luce che lascia una superficie diventa il valore di un pixel, e quale informazione si perde lungo la strada.</p>
<p>È la base di tutto il corso: la visione cerca di invertire questo processo, e non si può invertire ciò che non si sa modellare.</p>
""")

s(2, "Goals of the Day", """
<ul>
<li>Capire ad alto livello la formazione dell'immagine, <b>dalla luce che lascia una superficie al valore del pixel</b>: superfici, lenti, sensori, colore.</li>
<li>Due modelli matematici della camera:
<ul><li><b>vista di algebra lineare</b>: l<sub>s</sub> = A l<sub>w</sub>, e perché recuperare il mondo dai dati del sensore è un <b>problema inverso</b>;</li>
<li><b>vista geometrica</b>: proiezione prospettica e modello pinhole semplificato (coordinate camera, niente lenti).</li></ul></li>
<li>Tre <b>ambiguità</b> che nascono dalla formazione dell'immagine:
<ul><li>la prospettiva confonde <b>dimensione e profondità</b>;</li>
<li>le camere scartano informazione che va recuperata con inversione (regolarizzata);</li>
<li>il colore confonde <b>illuminante e materiale</b> (e la nostra percezione del colore è a sua volta ambigua).</li></ul></li>
</ul>
<div class="box k"><b>Filo logico della lezione</b><p>Ogni stadio della formazione dell'immagine butta via qualcosa. La lezione chiude (slide 71) mettendo in fila le tre perdite: geometrica, lineare, spettrale. Tienile a mente mentre studi.</p></div>
""")

s(3, "Outline", """
<ol>
<li>Luce e superfici (BRDF, Lambert, Phong).</li>
<li>Proiezione prospettica e modello pinhole (con un intermezzo sulla proiezione ortografica).</li>
<li>Camere come sistemi lineari.</li>
<li>Colore.</li>
</ol>
""")

s(4, "Forward Model vs. Inverse Problem", """
<ul>
<li>La lezione 1 ha presentato la visione come <b>problema inverso</b>: immagine → scena, l'inverso della grafica (scena → immagine).</li>
<li>Prima di risolvere il problema inverso bisogna conoscere con precisione il <b>modello diretto</b>: come una scena 3D diventa un array 2D di numeri.</li>
<li>La CV cerca di invertire la formazione dell'immagine su tre fronti:
<ul><li><b>geometria</b>: recuperare la struttura 3D da immagini 2D;</li>
<li><b>filtering</b>: togliere rumore, sharpening, deblurring (L3, L5);</li>
<li><b>rappresentazioni apprese</b>: separare materiale e illuminazione, trovare feature invarianti.</li></ul></li>
</ul>
""")

s(5, "The Imaging Pipeline", """
<p>Il viaggio di un fotone dal mondo al pixel:</p>
<span class="f">scena →(trasporto della luce)→ ottica (lente) →(messa a fuoco)→ sensore →(ISP)→ immagine digitale</span>
<ul>
<li><b>Scena</b>: sorgenti luminose, superfici, materiali, geometria.</li>
<li><b>Ottica</b>: la lente focalizza la luce sul piano del sensore (modello pinhole/prospettico, lenti).</li>
<li><b>Sensore</b>: converte fotoni in elettroni e poi in numeri; registra <b>una misura lineare per pixel</b>.</li>
<li><b>ISP</b> (image signal processor, non trattato oggi): demosaicing, white balance, gamma… trasforma la lettura grezza nell'immagine RGB che vediamo.</li>
</ul>
<p>Obiettivo della lezione: la geometria e la fisica che decidono quale informazione arriva nei pixel, e soprattutto <b>quale si perde</b>.</p>
<div class="box x"><b>Approfondimento</b><p>La linearità vale per il dato grezzo (raw) del sensore. Dopo l'ISP l'immagine non è più lineare nella luce: la correzione gamma comprime i valori (circa valore<sup>1/2.2</sup>). Se vuoi usare la linearità della luce su un JPEG, prima va linearizzato.</p></div>
""")

s(6, "Light and Surfaces", "<p>Prima parte: come la luce interagisce con le superfici, modelli di riflettanza e ambiguità materiale/luce.</p>", kind="div", sec=("l2-luce", "Luce e superfici", "slide 6–19"))

s(7, "Light Ray", """
<p><b>Figura</b> (tre foto di un lavandino): (a) il bagno illuminato normalmente; (b) e (c) al buio, con un solo raggio laser rosso che colpisce il rubinetto (b) o la ceramica del lavandino (c).</p>
<p>Il punto: anche un <b>singolo raggio</b>, quando colpisce una superficie, viene diffuso in molte direzioni e illumina di rosa tutto l'ambiente. Il punto colpito si vede da ogni direzione perché la superficie rimanda luce ovunque.</p>
<p>Il modello di base della lezione è l'<b>ottica geometrica</b>: la luce viaggia in linea retta come raggi, con direzione e intensità, e interagisce con le superfici nei punti in cui le colpisce.</p>
""")

s(8, "Light Rays and Surfaces", """
<ul>
<li>Un raggio colpisce una superficie dalla direzione <b>p</b> con intensità l<sub>in</sub>.</li>
<li>La superficie genera un raggio uscente in direzione <b>q</b> con intensità l<sub>out</sub>.</li>
<li>Il legame fra l<sub>in</sub> e l<sub>out</sub> dipende da:
<ul><li>il <b>materiale</b> della superficie;</li><li>la <b>normale</b> alla superficie <b>n</b>;</li><li>le <b>direzioni</b> p (entrante) e q (uscente);</li><li>la <b>lunghezza d'onda</b> λ.</li></ul></li>
</ul>
<p><b>Figura:</b> raggio l<sub>in</sub>(λ) che colpisce un piano verde; dal punto di impatto partono raggi in molte direzioni, uno dei quali è l<sub>out</sub> in direzione q.</p>
<p>Questi sono esattamente gli argomenti della BRDF della slide successiva.</p>
""")

s(9, "The BRDF: General Formulation", """
<p>La <b>BRDF</b> (bidirectional reflectance distribution function) F lega la luce uscente a quella entrante:</p>
<span class="f">l<sub>out</sub> = F(l<sub>in</sub>, <b>n</b>, <b>p</b>, <b>q</b>, λ)</span>
<ul>
<li>l<sub>in</sub>, l<sub>out</sub>: intensità del raggio entrante e uscente;</li>
<li><b>n</b>: normale alla superficie;</li>
<li><b>p</b>, <b>q</b>: direzioni del raggio entrante e uscente;</li>
<li>λ: lunghezza d'onda (componente spettrale).</li>
</ul>
<p>La BRDF è il "materiale" visto dalla luce: due oggetti con stessa forma e stessa luce appaiono diversi solo perché hanno BRDF diverse.</p>
<p>Nota: la didascalia parla di shading lambertiano che dipende dall'angolo θ, ma la figura è la stessa della slide 8 (raggio generico, θ non disegnato). Lambert arriva alla slide 10.</p>
<div class="box x"><b>Approfondimento</b><p>Nella definizione radiometrica rigorosa la BRDF è un rapporto (radianza uscente / irradianza entrante) che dipende da due direzioni, cioè 4 angoli, più λ. La scrittura della slide, con l<sub>in</sub> dentro F, è una semplificazione didattica che va benissimo per il corso.</p></div>
""")

s(10, "Linearity of Light", """
<ul>
<li>La luce si comporta in modo <b>lineare</b>: se più sorgenti illuminano una superficie, l'intensità uscente è la <b>somma</b> dei contributi di ciascuna.</li>
<li>Questo giustifica la scomposizione di illuminazioni complesse in componenti semplici (luci puntiformi, luce ambientale…) di cui si sommano gli effetti.</li>
</ul>
<div class="box k"><b>Perché è importante</b><p>È l'ipotesi che regge tutta la lezione e la successiva:</p><ul>
<li>il modello di Phong è una somma di termini (slide 12–13);</li>
<li>la camera è un operatore lineare l<sub>s</sub> = A l<sub>w</sub> (slide 42 in poi);</li>
<li>la risposta dei coni è una mappa lineare (slide 65);</li>
<li>in L3 i sistemi lineari e invarianti per traslazione diventano convoluzioni.</li></ul></div>
""")

s(11, "Lambertian Surfaces", """
<p>Il modello <b>lambertiano</b> è la BRDF più semplice: superficie perfettamente <b>diffusiva</b>, che riflette la luce ugualmente in tutte le direzioni uscenti.</p>
<span class="f">l<sub>out</sub> = F<sub>L</sub>(l<sub>in</sub>(λ), <b>n</b>, <b>p</b>) = a · l<sub>in</sub>(λ) · (<b>n</b> · <b>p</b>)</span>
<ul>
<li><b>a</b>: <b>albedo</b>, coefficiente di riflettanza della superficie (quanta luce rimanda, fra 0 e 1).</li>
<li><b>n · p</b> = cos θ: coseno dell'angolo fra normale e direzione della luce (vettori unitari).</li>
<li>F<sub>L</sub> <b>non dipende da q</b>: la superficie appare ugualmente luminosa da ogni punto di vista; contano solo quanta luce arriva e con che angolo.</li>
</ul>
<p>(Sulla slide gli argomenti di F<sub>L</sub> sono finiti per errore di impaginazione nel pedice; il significato è quello scritto sopra.)</p>
<div class="box k"><b>Da saper fare</b><ul>
<li>Perché il coseno: un fascio che arriva inclinato di θ si distribuisce su un'area 1/cos θ più grande, quindi ogni punto riceve cos θ volte meno luce.</li>
<li>Esempio: luce a θ = 60° → cos θ = 0.5 → l<sub>out</sub> = 0.5 · a · l<sub>in</sub>. A θ = 0 la superficie è al massimo.</li>
<li>Convenzione: per avere n · p = cos θ &gt; 0, p deve puntare dalla superficie verso la luce. Se n · p &lt; 0 la luce sta dietro la superficie e si usa max(0, n · p).</li></ul></div>
<div class="box b"><b>Dal libro · cap. 5, § 5.2.1 Lambertian Surfaces</b><p>Nel libro è l'eq. 5.2, identica alla slide: l<sub>out</sub> = a l<sub>in</sub>(λ)(n · p), con p che punta <b>verso la sorgente</b> e a albedo scalare. Il libro insiste su un solo punto: l'uscita dipende da orientazione della superficie e direzione della luce, <b>non</b> dalla direzione di vista q. Come materiale quasi perfettamente lambertiano cita lo <b>Spectralon</b> (il "bianco di riferimento" usato per tarare gli strumenti).</p>
<p>Il libro non ricava il coseno: la giustificazione con l'area proiettata del riquadro sopra è un'aggiunta nostra, standard in radiometria. Fonte: <a href="https://visionbook.mit.edu/imaging.html">visionbook, cap. 5</a>.</p></div>
""")

s(12, "Lambertian Sphere", """
<p><b>Figura:</b> a sinistra lo schema, una sorgente puntiforme che illumina una sfera osservata da una camera; a destra il rendering di una sfera lambertiana, chiara dal lato della luce e scura dal lato opposto.</p>
<ul>
<li>Il <b>gradiente morbido</b> dal chiaro allo scuro segue esattamente cos θ = n · p, che cambia con continuità sulla sfera.</li>
<li>Poiché l'intensità dipende solo dalla normale, dallo shading si può tentare di risalire alla forma (<i>shape from shading</i>).</li>
</ul>
""")

s(13, "Specular Surfaces and the Phong Model", """
<p>Le superfici reali riflettono luce in modo <b>preferenziale</b> attorno alla direzione speculare (come uno specchio). Il <b>modello di Phong</b> è la somma di tre termini:</p>
<ul>
<li><b>Ambient</b>: termine costante, luce diffusa indirettamente da ogni parte. Approssimazione grossolana dell'illuminazione globale (le interriflessioni fra oggetti).</li>
<li><b>Diffuse</b>: il termine lambertiano di prima.</li>
<li><b>Specular</b>: un riflesso (highlight) concentrato attorno alla direzione di riflessione speculare <b>r</b>.</li>
</ul>
<p>Grazie alla linearità della luce i tre termini si <b>sommano</b> semplicemente.</p>
""")

s(14, "Specular Surfaces and the Phong Model (formula)", """
<span class="f">l<sub>out</sub> = k<sub>a</sub> + a · l<sub>in</sub> (<b>n</b> · <b>p</b>) + k<sub>s</sub> (<b>r</b> · <b>q</b>)<sup>α</sup> l<sub>in</sub></span>
<p>ambiente + diffuso (Lambert) + speculare.</p>
<ul>
<li><b>k<sub>a</sub></b>: coefficiente di luce ambientale; <b>a</b>: albedo del termine lambertiano.</li>
<li><b>k<sub>s</sub></b>: intensità della riflessione speculare.</li>
<li><b>α</b>: "shininess", quanto è concentrato l'highlight.</li>
<li><b>r</b>: direzione di riflessione speculare perfetta di p rispetto a n.</li>
<li>(r · q)<sup>α</sup> è grande solo se la direzione di vista q è vicina a r.</li>
</ul>
<p><b>Figura:</b> p e r simmetrici rispetto alla normale n, che sta nel mezzo.</p>
<p>È il termine speculare a rendere l'aspetto <b>dipendente dal punto di vista</b>, a differenza del lambertiano puro.</p>
<div class="box k"><b>Da saper fare</b><ul>
<li>Riflessione di p rispetto a n (vettori unitari, p verso la luce): <span class="f">r = 2 (n · p) n − p</span></li>
<li>Effetto di α: se q devia da r di 10°, r · q = cos 10° ≈ 0.985. Con α = 10 il termine vale ≈ 0.86, con α = 100 vale ≈ 0.22. Più α è grande, più l'highlight si stringe.</li></ul></div>
<div class="box x"><b>Approfondimento</b><p>Phong è un modello <b>empirico</b>, non fisico: non conserva l'energia e anche qui serve max(0, r · q). In grafica si usano modelli fisicamente basati (microfacet, es. Cook-Torrance).</p></div>
<div class="box b"><b>Dal libro · cap. 5, § 5.2.2 Specular Surfaces</b><p>Formula verificata: il libro scrive il solo termine speculare di Phong come k<sub>s</sub>(r · q)<sup>α</sup> l<sub>in</sub>, con r = 2(p · n)n − p la direzione di massima riflessione speculare (vettore unitario), k<sub>s</sub> costante speculare e α che governa l'<b>ampiezza</b> del lobo speculare. Ambiente (costante sommata a ogni riflessione) e diffuso (eq. 5.2) si sommano per linearità, come sulla slide. La fig. 5.2 del libro è il confronto Lambert / Phong / foto della slide 17. Fonte: <a href="https://visionbook.mit.edu/imaging.html">visionbook, cap. 5</a>.</p></div>
""")

s(15, "Lambertian vs. Phong", """
<p><b>Figura:</b> stessa sfera, stessa luce. A sinistra il rendering lambertiano, solo diffuso; a destra Phong, con in più un <b>highlight speculare</b> bianco dove la direzione di vista è vicina a r.</p>
<p>Conseguenza per la visione: l'highlight <b>si sposta se si muove l'osservatore</b>. Lo stesso punto 3D ha aspetto diverso in viste diverse, e questo disturba il matching fra immagini (stereo, tracking, feature L7).</p>
""")

s(16, "Material Parameters and Appearance", """
<span class="f">l<sub>out</sub> = k<sub>a</sub> + a · l<sub>in</sub> (<b>n</b> · <b>p</b>) + k<sub>s</sub> (<b>r</b> · <b>q</b>)<sup>α</sup> l<sub>in</sub></span>
<ul>
<li>Aumentare <b>α</b> <b>restringe</b> e rende più netto l'highlight (metallo lucidato contro plastica opaca).</li>
<li>Aumentare <b>k<sub>s</sub></b> rende l'highlight più <b>luminoso</b> senza cambiarne la dimensione.</li>
</ul>
<p><b>Figura:</b> griglia 3×3 di sfere, righe = k<sub>s</sub> crescente, colonne = α crescente. Scendendo il riflesso si accende; andando a destra si rimpicciolisce.</p>
""")

s(17, "Example", """
<p><b>Figura:</b> tre sfere a confronto: (a) rendering <b>lambertiano</b>, opaco e uniforme; (b) rendering <b>Phong</b>, con due highlight netti; (c) <b>fotografia</b> di una vera sfera bianca, con riflessi e ombre più complessi.</p>
<p>Il punto: Lambert e Phong catturano l'essenziale (diffuso + speculare), ma l'aspetto di un oggetto reale è più ricco. Phong è un'approssimazione empirica economica, non un modello fisico esatto.</p>
""")

s(18, "Light and Material", """
<ul>
<li>La BRDF determina l'aspetto dell'immagine. <b>Geometria, illuminazione e materiale</b> influenzano insieme il modo in cui la luce interagisce con le superfici: è un'<b>ambiguità ricorrente</b> in visione.</li>
<li><b>Vantaggio</b>: le proprietà del materiale si possono inferire dalle immagini e usare per riconoscimento e comprensione della scena.</li>
<li><b>Sfida</b>: le proprietà del materiale si possono confondere con geometria e illuminazione, e l'inferenza diventa difficile.</li>
</ul>
<p>Esempio: una zona scura può essere un materiale scuro, una parte in ombra o una superficie inclinata rispetto alla luce. Il pixel da solo non lo dice. La stessa struttura "prodotto di incognite" torna nella color constancy (slide 61).</p>
""")

s(19, "Example (luce diversa)", """
<p><b>Figura:</b> lo stesso banco di pane e dolci fotografato sotto tre illuminazioni: luce calda a 3000 K, luce più neutra a 4000 K, e una lampada commerciale per alimenti.</p>
<p>Scena e materiali sono identici, ma i <b>valori dei pixel cambiano</b> molto (più arancioni, più neutri, più rossi). Un sistema di riconoscimento deve essere robusto a questa variazione o saperla compensare.</p>
<p>Curiosità: nei negozi si scelgono apposta luci che rendono il cibo più invitante, cioè si sfrutta l'ambiguità materiale/luce.</p>
""")

s(20, "Pinhole Cameras", "<p>Seconda parte: perché una superficie qualsiasi non forma un'immagine e come un piccolo foro risolve il problema.</p>", kind="div", sec=("l2-pinhole", "Camera pinhole", "slide 20–26"))

s(21, "Why Don't We See Images on a Wall?", """
<ul>
<li>Ogni punto di un muro è illuminato da luce che arriva da <b>molte direzioni</b>.</li>
<li>Per un muro lambertiano la luce uscente da un punto è l'<b>integrale</b> su tutte le direzioni entranti p:</li>
</ul>
<span class="f">l<sub>out</sub> = ∫<sub>p</sub> a · l<sub>in</sub>(p) · (n · p) dp</span>
<ul>
<li>Questo integrale <b>media via</b> tutta la struttura spaziale della scena: il muro sembra solo una superficie illuminata in modo uniforme, senza immagine.</li>
</ul>
<p>Formare un'immagine significa <b>impedire questa integrazione</b>: ogni punto del supporto deve ricevere luce da una sola direzione.</p>
<div class="box w"><b>Attenzione: formula imprecisa sulla slide</b><p>La slide scrive cos(n · p). Ma n · p è già il coseno dell'angolo (slide 11): scrivere il coseno del prodotto scalare è sbagliato. Va scritto (n · p) oppure cos θ, come nella formula sopra. A rigore l'integrale è sulle direzioni della semisfera sopra la superficie (dove n · p &gt; 0).</p><p>Il refuso viene dal libro: nel § 5.3 del visionbook l'integrale è stampato proprio con cos(n · p), mentre la sua eq. 5.2 (Lambert) usa correttamente (n · p). Fidati dell'eq. 5.2.</p></div>
<div class="box b"><b>Dal libro · cap. 5, § 5.3 The Pinhole Camera and Image Formation</b><p>Il ragionamento del libro: il valore del muro in un punto è un <b>unico numero</b> che somma i contributi di tutte le direzioni, quindi dice pochissimo su l<sub>in</sub>(p) per una singola direzione p. Una camera serve a <b>organizzare i raggi</b>: fa arrivare in ogni punto del supporto solo la luce di una direzione nota, così dal valore si risale alla direzione di provenienza. Il libro invita a costruirne una (fig. 5.4 con due fogli, fig. 5.5 con un sacchetto di carta). Fonte: <a href="https://visionbook.mit.edu/imaging.html">visionbook, cap. 5</a>.</p></div>
""")

s(22, "Restricting Incoming Rays", """
<ul>
<li>Per formare un'immagine bisogna impedire a ogni punto della superficie di imaging di <b>vedere tutta la scena</b>.</li>
<li>Soluzione: una barriera opaca con un <b>unico piccolo foro</b> (pinhole) fra scena e superficie di imaging.</li>
<li>Ogni punto della superficie riceve ora luce da (circa) <b>una sola direzione</b>, cioè da un solo punto della scena.</li>
<li>L'integrale della slide precedente diventa una <b>corrispondenza uno a uno</b> fra punti della scena e punti dell'immagine.</li>
</ul>
<p><b>Figura:</b> un foglio bianco e, davanti, un cartone scuro con un forellino. Sul foglio si vede un'immagine debole e sfocata della finestra della stanza.</p>
""")

s(23, "Restricting Incoming Rays (figura)", """
<p><b>Figura:</b></p>
<ul>
<li>(a) Senza barriera: ogni punto dell'albero manda luce a ogni punto del muro → nessuna immagine.</li>
<li>(b) Con il pinhole: ogni punto dell'albero raggiunge un solo punto del muro → sul muro compare l'albero, <b>capovolto</b>.</li>
</ul>
<p>È la traduzione visiva del passaggio da integrale a mappa uno a uno.</p>
""")

s(24, "Natural Pinhole Cameras", """
<p>L'effetto pinhole avviene anche in natura quando la luce passa per una piccola apertura (fra le foglie di un albero, da un forellino in una tenda). L'immagine che si forma è:</p>
<ul>
<li><b>invertita</b> rispetto alla scena (sottosopra e specchiata destra-sinistra);</li>
<li><b>più scura</b> della scena (dal foro passa una frazione minima della luce);</li>
<li><b>più sfocata</b> della scena (il foro non è un punto ideale, e la diffrazione allarga i raggi).</li>
</ul>
<p><b>Figura:</b> la stessa foto del foglio e del cartone forato della slide 22.</p>
<p>Le tre proprietà sono tre limiti reali: l'inversione si risolve per convenzione (piano virtuale, slide 29), luce e sfocatura con le lenti (slide 25).</p>
<div class="box x"><b>Approfondimento</b><p>Le macchie di luce rotonde sotto un albero sono immagini pinhole del sole; durante un'eclissi parziale diventano tante piccole falci.</p></div>
""")

s(25, "Pinhole Camera Model: Setup", """
<ul>
<li>Una camera pinhole è fatta di:
<ul><li>un piano opaco (la barriera) con un unico piccolo foro: il <b>pinhole</b>, detto anche <b>centro della camera</b> o <b>centro ottico</b>;</li>
<li>un <b>piano di imaging</b> dietro la barriera, dove si forma l'immagine.</li></ul></li>
<li>Ogni punto della scena emette o riflette luce in tutte le direzioni, ma ogni punto immagine riceve luce da <b>un solo raggio</b>: quello che passa per il foro.</li>
<li>Con una camera pinhole si ha (circa) <b>un raggio per punto immagine</b>.</li>
<li>Una camera pinhole ideale realizza una <b>proiezione prospettica</b>, la base di tutti i modelli geometrici di camera.</li>
</ul>
""")

s(26, "Pinhole Limitations and Lenses", """
<ul>
<li>Problemi delle camere pinhole reali:
<ul><li><b>Blur</b>: un foro reale ha dimensione finita, quindi raggi dallo stesso punto della scena passano per parti diverse del foro e arrivano in punti diversi del sensore;</li>
<li><b>Raccolta di luce</b>: un foro piccolo lascia passare poca luce e servono esposizioni lunghe.</li></ul></li>
<li>Soluzione: una <b>lente</b> può avere un'apertura grande (più luce) e allo stesso tempo far convergere i raggi di ogni punto della scena in (circa) un solo punto immagine.</li>
</ul>
<p><b>Figura</b> (un cane come scena, tre aperture): foro piccolo → immagine nitida ma <b>scura</b>; foro grande → luminosa ma <b>sfocata</b>; foro grande con lente → luminosa <b>e</b> nitida.</p>
<div class="box k"><b>Compromesso da ricordare</b><p>Col pinhole nitidezza e luminosità sono in conflitto. La lente rompe il compromesso, ma solo per i punti a fuoco: introduce profondità di campo, aberrazioni e distorsioni. Il modello geometrico resta comunque quello pinhole.</p></div>
<div class="box b"><b>Dal libro · cap. 6, Lenses (§ 6.2 Lensmaker's Formula, § 6.3 Imaging with Lenses)</b><p>Le slide non danno nessuna formula sulle lenti; il libro ne ricava tre, in <b>ottica geometrica</b> (niente diffrazione).</p>
<ul>
<li><b>Snell</b>: n<sub>1</sub> sin θ<sub>1</sub> = n<sub>2</sub> sin θ<sub>2</sub> (n indice di rifrazione, 1 nel vuoto, ≈ 1.0003 in aria). Con angoli piccoli (approssimazione <b>parassiale</b>) e lente <b>sottile</b> diventa θ<sub>1</sub> = n θ<sub>2</sub>.</li>
<li>Imponendo che tutti i raggi da un punto a distanza a sull'asse convergano nel punto a distanza b, l'inclinazione della superficie deve crescere <b>linearmente</b> con la distanza dall'asse (eq. 6.1): lo fanno una parabola e, per angoli piccoli, una sfera di raggio R. Ne esce la <b>formula della lente sottile</b>:
<span class="f">1/a + 1/b = 1/f,    f = R / (2(n − 1))</span>
(con raggi diversi R<sub>1</sub>, R<sub>2</sub>: 1/f = (n − 1)(1/R<sub>1</sub> + 1/R<sub>2</sub>)). a e b sono <b>punti coniugati</b>; raggi paralleli (a → ∞) vanno a fuoco a distanza f.</li>
<li>Il raggio che passa per il <b>centro</b> della lente sottile non devia (le due facce lì sono parallele): per questo una lente produce la <b>stessa proiezione prospettica</b> del pinhole, e il modello x = fX/Z resta valido.</li>
<li><b>Profondità di campo</b>: un punto fuori dal piano a fuoco diventa un <b>cerchio di confusione</b> di diametro C. Con f-number N = f/A (A diametro dell'apertura) e distanza U ≫ f, il libro ricava con i triangoli simili D ≈ 2NCU²/f²: la profondità di campo cresce <b>linearmente con N</b> (fig. 6.12: da f/2 a f/4 a f/8 raddoppia ogni volta). Chiudere il diaframma dà più profondità di campo ma meno luce: il compromesso del pinhole torna, attenuato.</li>
<li>Lenti concave: stesse formule con f <b>negativa</b> (fuoco virtuale). Una convessa lunga e una corta formano un telescopio con ingrandimento f<sub>1</sub>/f<sub>2</sub> (§ 6.3.3, facoltativo).</li>
</ul>
<p>Esempio: f = 50 mm, soggetto a a = 2 m. b = 1/(1/50 − 1/2000) mm ≈ 51.3 mm: per mettere a fuoco a 2 m il sensore va allontanato di circa 1.3 mm rispetto al fuoco all'infinito. Fonte: <a href="https://visionbook.mit.edu/lenses.html">visionbook, cap. 6</a>.</p></div>
""")

s(27, "Perspective Projection", "<p>Terza parte: equazioni della proiezione prospettica, sistemi di coordinate e ambiguità dimensione/profondità.</p>", kind="div", sec=("l2-prospettiva", "Proiezione prospettica", "slide 27–36"))

s(28, "Camera", """
<p><b>Figura:</b> una camera pinhole disegnata come una scatola: il foro (centro della camera) sta sull'origine degli assi mondo X, Y, Z; l'asse Z è l'<b>asse ottico</b> (asse principale); il piano di proiezione è la faccia posteriore, a distanza <b>f</b> dal foro.</p>
<p>La domanda: <b>come si passa dalle coordinate 3D di un punto della scena P alle coordinate 2D del punto immagine p?</b> Le slide successive rispondono con i triangoli simili.</p>
""")

s(29, "Perspective Projection: World to Camera Coordinates", """
<ul>
<li><b>Coordinate mondo</b>: un punto 3D della scena P = (X, Y, Z).</li>
<li><b>Coordinate camera</b>: la corrispondente posizione 2D p = (x, y) sul piano immagine.</li>
<li>Il pinhole è l'<b>origine</b> (0, 0, 0); l'asse ottico è l'asse <b>Z</b>, rivolto verso la scena.
<ul><li>Questa semplificazione (mondo e camera coincidono) verrà tolta più avanti nel corso.</li></ul></li>
<li><b>f</b>: distanza fra pinhole e piano immagine, la <b>lunghezza focale</b>.</li>
</ul>
<p><b>Figura:</b> il piano di proiezione reale dietro il pinhole (con p capovolto) e il piano virtuale davanti, entrambi a distanza f; il punto P della scena si proietta lungo la retta che passa per il foro.</p>
""")

s(30, "The Virtual Image Plane Trick", """
<ul>
<li>Il piano immagine reale sta <b>dietro</b> il pinhole a distanza f, e l'immagine è <b>invertita</b>.</li>
<li><b>Trucco</b>: si considera un <b>piano immagine virtuale</b> a distanza f <b>davanti</b> al pinhole, fra foro e scena.</li>
<li>Questa convenzione si usa da qui in poi ed è lo standard nella maggior parte del software.</li>
</ul>
<p>Vantaggio: l'immagine non è capovolta e le equazioni perdono i segni meno; la geometria (triangoli simili) è identica. Fisicamente il piano virtuale non esiste, è solo un modo comodo di fare i conti.</p>
""")

s(31, "Coordinate Mapping: The Perspective Projection Equations", """
<p><b>Proiezione prospettica</b>:</p>
<span class="f">x = f · X / Z,    y = f · Y / Z</span>
<ul>
<li>f è la focale, Z la <b>profondità</b>.</li>
<li>Sul piano virtuale le coordinate non sono invertite.</li>
<li>(x, y) è proporzionale a (X, Y) con fattore di scala <b>f / Z</b>.</li>
<li>Si ricava dai <b>triangoli simili</b> formati da punto della scena, pinhole e punto immagine.</li>
</ul>
<div class="box k"><b>Da saper fare: la derivazione</b><p>Nella figura, il triangolo grande ha cateti Z (lungo l'asse ottico) e Y; quello piccolo, con lo stesso vertice nel pinhole, ha cateti f e y. Sono simili, quindi y : Y = f : Z, cioè y = f Y / Z. Lo stesso per x.</p>
<p>Da ricordare: la mappa è <b>non lineare in Z</b> (c'è una divisione). È questa divisione a generare tutti gli effetti prospettici.</p></div>
<div class="box b"><b>Dal libro · cap. 39, § 39.2 3D Camera Projections in Homogeneous Coordinates</b><p>La divisione per Z si può "nascondere" con le <b>coordinate omogenee</b>: il punto diventa (X, Y, Z, 1) e la proiezione una moltiplicazione per una matrice 3 × 4 (eq. 39.1):</p>
<span class="f">[1 0 0 0; 0 1 0 0; 0 0 1/f 0] · (X, Y, Z, 1)<sup>T</sup> = (X, Y, Z/f)</span>
<p>Dividendo le prime due componenti per la terza si ottiene (fX/Z, fY/Z). La mappa resta non lineare in ℝ³, ma diventa lineare "a meno di scala": è il trucco su cui si costruisce il modello completo M = K[R | −RT] (intrinseci e estrinseci) della parte di geometria del corso. L'ortografica è la stessa matrice con terza riga (0 0 0 1) (eq. 39.2): la terza componente vale sempre 1 e la divisione sparisce. Fonte: <a href="https://visionbook.mit.edu/imaging_geometry.html">visionbook, cap. 39</a>.</p></div>
""")

s(32, "Distant Objects Appear Smaller", """
<ul>
<li>Da x = f X / Z: a dimensione X fissata, aumentando la profondità Z la dimensione proiettata x <b>cala come 1/Z</b>.</li>
<li>Due oggetti della stessa dimensione a profondità diverse hanno dimensioni diverse nell'immagine.</li>
<li>Rette parallele che si allontanano convergono verso un unico punto, il <b>punto di fuga</b> (vanishing point).</li>
<li>È la base geometrica degli indizi di profondità in una singola immagine.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Una persona alta 1.8 m a 10 m, con f = 50 mm: x = 0.05 · 1.8 / 10 = 9 mm sul sensore. A 20 m diventa 4.5 mm.</p></div>
<div class="box w"><b>Attenzione: argomento del punto di fuga incompleto</b><p>La slide dice che le parallele convergono perché x = f X / Z → 0 qualunque sia X. Questo vale solo per rette <b>parallele all'asse ottico</b>, che fuggono verso il centro dell'immagine. In generale, per una retta P(t) = P<sub>0</sub> + t·d con direzione d = (d<sub>X</sub>, d<sub>Y</sub>, d<sub>Z</sub>) e d<sub>Z</sub> ≠ 0:</p>
<span class="f">x(t) = f (X<sub>0</sub> + t d<sub>X</sub>) / (Z<sub>0</sub> + t d<sub>Z</sub>) → f · d<sub>X</sub> / d<sub>Z</sub>   per t → ∞</span>
<p>Il punto di fuga (f d<sub>X</sub>/d<sub>Z</sub>, f d<sub>Y</sub>/d<sub>Z</sub>) dipende solo dalla <b>direzione</b> d, non dal punto di partenza: per questo tutte le rette parallele (stessa d) fuggono nello stesso punto. Le rette parallele al piano immagine (d<sub>Z</sub> = 0) restano parallele anche in immagine.</p></div>
<div class="box b"><b>Dal libro · cap. 39, § 39.6 Concrete Examples (linea dell'orizzonte)</b><p>Il libro ricava la <b>linea dell'orizzonte</b> come caso particolare. Camera ad altezza h dal suolo che guarda in orizzontale: y = a(Y − h)/Z. Un punto del pavimento (Y = 0) a profondità Z finisce a y = −ah/Z, che tende a 0 per Z → ∞: tutte le rette del pavimento fuggono sulla riga del punto principale, cioè l'orizzonte passa per il centro dell'immagine. Inclinando la camera verso il basso di θ, l'orizzonte si sposta a y = a tan θ, indipendente dalla profondità. È il punto di fuga del riquadro sopra applicato a tutte le direzioni orizzontali. Fonte: <a href="https://visionbook.mit.edu/imaging_geometry.html">visionbook, cap. 39</a>.</p></div>
""")

s(33, "Size vs. Depth Ambiguity", """
<ul>
<li>x = f X / Z dipende da X e Z solo attraverso il <b>rapporto X / Z</b>.</li>
<li>Un oggetto di dimensione X a profondità Z si proietta esattamente come un oggetto di dimensione kX a profondità kZ, per qualunque k.
<ul><li>Esempio (con f = 1): A con X = 1, Z = 2 e B con X = 2, Z = 4 danno entrambi x = 0.5.</li></ul></li>
<li>La proiezione prospettica è una mappa <b>molti a uno</b>: un'immagine è compatibile con infinite coppie (dimensione, profondità).</li>
</ul>
<p><b>Conseguenze</b>:</p>
<ul><li>si <b>perde informazione</b> su dimensione e profondità;</li><li>serve <b>invarianza alla scala</b> (ripresa in L6 con le piramidi e in L7 con SIFT).</li></ul>
<div class="box x"><b>Approfondimento</b><p>Tutto il raggio che passa per il pinhole e per p si proietta nello stesso punto: la profondità lungo il raggio è la dimensione persa. Per recuperarla servono altre viste (stereo), conoscenze a priori (dimensioni tipiche degli oggetti) o modelli appresi. È il motivo dei film con i modellini che sembrano veri.</p></div>
""")

s(34, "From Camera Coordinates to Image (Pixel) Coordinates", """
<ul>
<li><b>Coordinate camera</b> (x, y): <b>continue</b>, in unità fisiche, con origine sull'asse ottico.</li>
<li><b>Coordinate immagine</b> (n, m): indici di pixel <b>discreti</b>, con origine convenzionalmente nell'angolo in alto a sinistra.</li>
</ul>
<p><b>Figura:</b> il piano virtuale con gli assi camera (x, y) al centro, dove passa l'asse ottico, e gli assi immagine (n, m) in un angolo. Sono legati dal <b>punto principale</b> (n<sub>0</sub>, m<sub>0</sub>).</p>
<p>È una classica fonte di bug ed errori di segno: le convenzioni cambiano da libreria a libreria (vedi il riquadro della slide 35).</p>
""")

s(35, "Image Coordinates", """
<span class="f">n = −a x + n<sub>0</sub>,    m = −a y + m<sub>0</sub></span>
<ul>
<li><b>a</b>: <b>fattore di scala</b> da unità fisiche a pixel (legato alla dimensione del pixel e alla focale).</li>
<li><b>(n<sub>0</sub>, m<sub>0</sub>)</b>: <b>punto principale</b>, le coordinate in pixel dell'asse ottico.</li>
<li>Il segno meno tiene conto del <b>ribaltamento</b> fra assi camera e assi immagine (es. y cresce verso l'alto, m verso il basso).</li>
</ul>
<div class="box w"><b>Attenzione: testo e figura usano convenzioni diverse</b><p>Nella figura (presa dal libro) l'asse x punta a <b>sinistra</b>, y in alto, e l'origine dei pixel (0,0) è in <b>basso</b> a sinistra con n verso destra e m verso l'<b>alto</b>. Con quella figura:</p>
<ul><li>n = −a x + n<sub>0</sub> è giusto (x e n hanno versi opposti);</li>
<li>ma y e m crescono entrambi verso l'alto, quindi sarebbe m = +a y + m<sub>0</sub>.</li></ul>
<p>La formula della slide con due segni meno torna invece con la convenzione del testo (origine in alto a sinistra, m verso il basso) e x che punta a sinistra. All'esame dichiara sempre i versi degli assi prima di scrivere i segni: il segno di ogni termine è + se i due assi hanno lo stesso verso, − se opposto.</p></div>
<div class="box x"><b>Approfondimento</b><p>In OpenCV e nella maggior parte dei testi la camera ha x a destra e y in basso, come i pixel, quindi non ci sono segni meno: u = f<sub>x</sub> X/Z + c<sub>x</sub>, v = f<sub>y</sub> Y/Z + c<sub>y</sub>. È il pezzo della matrice degli intrinseci K che vedrai nella parte di geometria del corso.</p></div>
<div class="box b"><b>Dal libro · cap. 5, § 5.3.1 e cap. 39, § 39.3 Camera-Intrinsic Parameters</b><p>Il libro conferma il riquadro Attenzione: con la figura della slide (sua fig. 5.8) scrive <b>n = −a x + n<sub>0</sub>, m = a y + m<sub>0</sub></b>, con un solo segno meno. Le coordinate mondo hanno origine nel pinhole e Z perpendicolare al piano del sensore, con assi scelti secondo la <b>regola della mano destra</b> (fig. 5.7).</p>
<p>Sul fattore a le due parti del libro differiscono, ed è la fonte del "legato a pixel e focale" della slide:</p>
<ul><li>nel cap. 5 x contiene già f, quindi a converte solo lunghezze sul sensore in pixel (pixel per metro);</li>
<li>nel cap. 39 a si applica direttamente a X/Z e ingloba la focale: <b>a = fN/w</b>, con N larghezza dell'immagine in pixel e w larghezza del sensore in metri. Il punto principale si chiama (c<sub>x</sub>, c<sub>y</sub>) e con pixel non quadrati le scale sono due (a, b). Il libro nota che con origine in alto a sinistra (convenzione di Python e OpenCV) i segni di a e b risultano negativi nella sua convenzione di assi camera.</li></ul>
<p>Calibrazione "a mano" (§ 39.3.3): un oggetto largo W a distanza Z che occupa L pixel dà a = ZL/W. Esempio del libro: W = 20 cm, Z = 31 cm, L = 2002 pixel, a ≈ 3103 pixel. Fonti: <a href="https://visionbook.mit.edu/imaging.html">visionbook, cap. 5</a>, <a href="https://visionbook.mit.edu/imaging_geometry.html">visionbook, cap. 39</a>.</p></div>
""")

s(36, "Summary (proiezione prospettica)", """
<ul>
<li>La proiezione prospettica guida il ragionamento geometrico su camere e immagini.</li>
<li>È una mappa <b>molti a uno</b>: perde informazione su dimensione assoluta e profondità.</li>
<li>Ci sono diversi sistemi di coordinate: <b>mondo, camera, immagine</b>, con convenzioni diverse e non sempre coerenti.</li>
<li>In molti task (ricostruzione 3D, calibrazione) bisogna saper passare dall'uno all'altro.</li>
</ul>
<p>Catena completa per ora: (X, Y, Z) → prospettiva → (x, y) → scala e traslazione → (n, m).</p>
""")

s(37, "Orthographic Projection", "<p>Intermezzo: una geometria di imaging alternativa, per capire che ogni geometria sceglie quale informazione conservare.</p>", kind="div", sec=("l2-orto", "Proiezione ortografica", "slide 37–41"))

s(38, "Perspective Isn't the Only Choice", """
<ul>
<li>La prospettiva è la conseguenza naturale di un pinhole: i raggi <b>convergono</b> in un punto, quindi la dimensione proiettata dipende dalla profondità (x = f X / Z).</li>
<li>Ma la convergenza è una <b>scelta</b> di geometria, non una legge di natura. E se si accettassero solo i raggi che arrivano <b>perpendicolari</b> al piano immagine?</li>
<li>Allora ogni punto della scena arriva sull'immagine tramite raggi <b>paralleli</b>, e la geometria è diversa.</li>
</ul>
<p><b>Figura:</b> un oggetto a gradini proiettato sul piano immagine con raggi paralleli all'asse Z.</p>
""")

s(39, "Orthographic Projection: Equations", """
<p><b>Proiezione ortografica</b>:</p>
<span class="f">x = k X,    y = k Y</span>
<ul>
<li><b>k</b>: fattore di scala fisso e globale, <b>nessuna dipendenza da Z</b>.</li>
<li>La dimensione nell'immagine è <b>indipendente dalla profondità</b>: oggetti uguali vicini e lontani appaiono uguali.</li>
<li>Toglie l'ambiguità dimensione/profondità, ma a prezzo di <b>eliminare del tutto</b> l'informazione di profondità: niente punti di fuga, niente scorcio prospettico.</li>
</ul>
<div class="box x"><b>Approfondimento</b><p>In pratica è una buona approssimazione quando la variazione di profondità dell'oggetto è piccola rispetto alla sua distanza dalla camera (teleobiettivo, oggetti lontani). La versione "prospettiva debole" usa k = f / Z<sub>medio</sub>: ortografica, ma con la scala della distanza media.</p></div>
""")

s(40, "Soda Straw Camera", """
<p><b>Figura:</b> (a) un fascio di cannucce parallele visto di fronte; (b) una mano come scena; (c) il fascio appoggiato in verticale su una superficie, su cui compare un'immagine chiara e colorata della scena.</p>
<p>È la realizzazione fisica intuitiva della proiezione ortografica: ogni cannuccia lascia passare solo i raggi quasi paralleli al suo asse, quindi seleziona una <b>direzione</b> invece di un punto di convergenza. L'immagine non è capovolta e ha la stessa scala qualunque sia la distanza.</p>
<div class="box b"><b>Dal libro · cap. 5, § 5.3.2–5.3.3 Orthographic Projection, How to Build an Orthographic Camera?</b><ul>
<li>Il libro (fig. 5.10) usa x = X, y = Y, cioè k = 1: la camera a cannucce ha scala <b>unitaria</b>, un oggetto sul piano di proiezione ha la stessa dimensione che ha nel mondo.</li>
<li>Le cannucce vanno <b>dipinte di nero</b> all'interno, altrimenti i riflessi sulle pareti lascerebbero passare raggi obliqui. Nella fig. 5.11 ne servono circa 500; una versione più grande ne usava 32 000.</li>
<li>L'immagine <b>non è capovolta</b>, a differenza del pinhole.</li>
<li>In pratica l'ortografica si ottiene con una <b>lente telecentrica</b> (pinhole + lente) o, approssimativamente, con un teleobiettivo; matematicamente è esatta solo per oggetti infinitamente lontani con zoom infinito.</li>
</ul><p>Fonte: <a href="https://visionbook.mit.edu/imaging.html">visionbook, cap. 5</a>.</p></div>
""")

s(41, "Perspective vs. Orthographic: Two Ways to Lose Information", """
<ul>
<li><b>Prospettica</b>: conserva un indizio di profondità (la dimensione cala con la distanza) ma lo <b>confonde con la scala</b> dell'oggetto; l'ambiguità va risolta in altro modo (stereo, prior, stima di profondità appresa).</li>
<li><b>Ortografica</b>: toglie per costruzione l'ambiguità scala/profondità, ma <b>scarta del tutto</b> la profondità.</li>
<li>Nessuna delle due è "più corretta": sono scelte diverse su quale informazione il sistema conserva. Il tema torna con le camere come sistemi lineari.</li>
</ul>
""")

s(42, "Cameras as Linear Systems", "<p>Quarta parte: la camera come operatore lineare e il recupero della scena con inversione regolarizzata.</p>", kind="div", sec=("l2-lineari", "Camere come sistemi lineari", "slide 42–56"))

s(43, "Motivation", """
<ul>
<li>Finora "camera" ha voluto dire un pinhole ideale o una lente che focalizza raggi su un sensore.</li>
<li>Ma <b>qualunque</b> dispositivo che trasforma una scena in misure si descrive allo stesso modo: la luce è lineare, quindi la mappa scena → sensore è sempre una mappa lineare <b>l<sub>s</sub> = A l<sub>w</sub></b>.
<ul><li>Questa astrazione permette di ragionare su qualunque setup di imaging: pinhole reali sfocati, corner camera…</li></ul></li>
<li><b>Obiettivo</b>: una volta noto A, recuperare la scena l<sub>w</sub> dalle misure l<sub>s</sub> diventa un problema generale (invertire, o regolarizzare, un sistema lineare) che vale per qualunque camera.</li>
</ul>
""")

s(44, "The Camera as a Linear System (setup)", """
<p>Si considera un <b>mondo 1D</b> semplificato:</p>
<ul>
<li>un vettore <b>l<sub>w</sub> ∈ ℝ<sup>N</sup></b> di intensità luminose della scena (una componente per posizione o direzione);</li>
<li>il sensore registra un vettore <b>l<sub>s</sub> ∈ ℝ<sup>M</sup></b> di misure.</li>
</ul>
<p><b>Figura:</b> in alto la scena come fila di celle (indici 0…12), al centro un occlusore con un foro, in basso la fila di pixel del sensore. Una cella della scena manda raggi in molte direzioni, ma solo quello che passa dal foro arriva al sensore. Nota che gli indici del sensore sono in ordine inverso (12…0): l'immagine è capovolta.</p>
""")

s(45, "The Camera as a Linear System (formula)", """
<p>Poiché la luce è lineare, il legame fra scena e sensore è una mappa lineare:</p>
<span class="f">l<sub>s</sub> = A l<sub>w</sub>,    A ∈ ℝ<sup>M×N</sup>  (operatore di imaging)</span>
<ul>
<li>Ogni <b>riga</b> di A dice come una misura del sensore sia una combinazione pesata delle intensità della scena: è il pattern di sensibilità di quel pixel.</li>
</ul>
<div class="box k"><b>Da saper spiegare</b><ul>
<li>Riga i di A = "cosa vede il pixel i" del mondo.</li>
<li>Colonna j di A = dove finisce, sul sensore, la luce del punto j della scena (la risposta all'impulso del punto j).</li></ul></div>
""")

s(46, "The Ideal Pinhole as A = I", """
<span class="f">l<sub>s</sub> = A l<sub>w</sub>,    A ∈ ℝ<sup>M×N</sup></span>
<ul>
<li>In una camera pinhole ideale ogni pixel riceve luce da <b>esattamente una</b> direzione della scena.</li>
<li>Con la convenzione del piano immagine virtuale la mappa è diretta, senza ribaltamento: <b>A = I</b>, la matrice identità.</li>
</ul>
<p>Sul piano reale, con l'immagine capovolta, A sarebbe l'identità "a specchio" (uni sull'antidiagonale): comunque una permutazione, invertibile banalmente. Il libro evita il problema in un altro modo: numera i pixel del sensore al contrario (12…0, fig. 7.1), così anche col piano reale A è esattamente l'identità.</p>
<p>Il pinhole ideale è il caso migliore: l'inversione è immediata (l<sub>w</sub> = l<sub>s</sub>). Ogni camera reale si allontana da qui.</p>
<div class="box b"><b>Dal libro · cap. 7, § 7.2 Flatland e § 7.3 Cameras as Linear Systems</b><p>Il libro lavora in "flatland": la scena è una linea a <b>profondità fissa</b> con albedo diverse punto per punto, discretizzata in 13 valori; la componente n di l<sub>w</sub> è l'intensità della luce che parte dalla posizione n <b>verso la camera</b>. Con un sensore di 13 pixel e foro piccolo, A è l'identità 13 × 13, e nella fig. 7.2 (a, b) anche A<sup>−1</sup> e B sono identità. Il libro osserva che per camere a lente e pinhole normali A è "circa l'identità": è proprio per questo che l'uscita del sensore sembra un'immagine. Per camere mediche o astronomiche non è così, e i dati non assomigliano alla scena. Fonte: <a href="https://visionbook.mit.edu/camera_as_linsys.html">visionbook, cap. 7</a>.</p></div>
""")

s(47, "Real Pinhole", """
<ul>
<li>Un pinhole "meno che ideale" (foro di dimensione finita, diffrazione) rende A <b>vicina a I ma con dispersione</b>: ogni riga ha quasi tutto il peso su una componente e piccoli contributi dai vicini.</li>
<li>Questo è un <b>blur</b>, cioè una <b>convoluzione</b>.</li>
</ul>
<p><b>Figura:</b> (a) foro piccolo: ogni pixel vede un solo punto; (b) A, A<sup>−1</sup> e B sono tutte quasi diagonali e pulite. (c) foro più grande: ogni pixel vede un cono di punti; (d) A è una banda diagonale (il blur), A<sup>−1</sup> ha un pattern a <b>scacchiera</b>, B (l'inversa regolarizzata delle slide 50–53) è una banda liscia.</p>
<div class="box x"><b>Collegamento con L3</b><p>Se il blur è lo stesso ovunque, ogni riga di A è la riga precedente traslata di una posizione: A è una matrice di <b>Toeplitz</b> (circolante con bordi periodici). Moltiplicare per una matrice così è esattamente una convoluzione, ed è il ponte con la lezione su Fourier.</p></div>
<div class="box b"><b>Dal libro · cap. 7, § 7.3 (foro largo)</b><p>Nel libro il foro largo è costruito in modo che ogni pixel copra <b>esattamente due</b> posizioni della scena: ogni riga di A ha <b>due 1 consecutivi</b> con peso uguale, non "quasi tutto il peso su una componente" come dice la slide (quella è una descrizione generica di un blur lieve, ma la figura mostra il caso a pesi uguali). L'uscita (fig. 7.3) è quasi uguale all'ingresso, "più grande e un po' più liscia": più grande perché ogni pixel raccoglie il doppio della luce, più liscia perché è una media mobile di larghezza 2. Il riquadro della slide 54 spiega perché la sua inversa è una scacchiera. Fonte: <a href="https://visionbook.mit.edu/camera_as_linsys.html">visionbook, cap. 7</a>.</p></div>
""")

s(48, "Other Cameras", """
<ul>
<li>Se qualunque A lineare definisce un sistema di imaging valido, si possono progettare camere che <b>non assomigliano a un pinhole</b>, purché l<sub>w</sub> sia ancora recuperabile da l<sub>s</sub>.</li>
<li>Esempi: <b>edge camera</b>, <b>pinspeck camera</b>, <b>corner camera</b>.</li>
<li>In ciascuno la matrice A <b>mescola</b> i valori della scena molto più di un pinhole.</li>
</ul>
<p>Idea di fondo (<i>computational imaging</i>): l'ottica può essere "povera" se l'algoritmo di ricostruzione è buono.</p>
<div class="box b"><b>Dal libro · cap. 7, § 7.4.3 Corner Camera</b><p>La corner camera guarda il <b>pavimento</b> vicino allo spigolo di un muro. Un punto del pavimento all'angolo θ (attorno allo spigolo) riceve luce dalla scena nascosta solo per le direzioni azimutali ξ fra 0 e θ; integrando prima sull'inclinazione verticale φ (con il fattore cos φ di Lambert, eq. 7.7) si ottiene un segnale 1D l<sub>w</sub>(ξ) e</p>
<span class="f">l<sub>ground</sub>(r, θ) ≈ ∫<sub>0</sub><sup>θ</sup> l<sub>w</sub>(ξ) dξ   (eq. 7.8)</span>
<p>cioè esattamente una <b>edge camera</b>: si ricostruisce con una derivata regolarizzata (una maschera spaziale moltiplicata per l'immagine del pavimento, fig. 7.7). La difficoltà è l'ampiezza: la scena dietro l'angolo perturba la luce sul pavimento di circa <b>1/1000</b>. Nella fig. 7.8 il risultato è un "video 1D" (angolo in verticale, tempo in orizzontale) di una o due persone che camminano dietro l'angolo. Fonte: <a href="https://visionbook.mit.edu/camera_as_linsys.html">visionbook, cap. 7</a>.</p></div>
""")

s(49, "Other Cameras (figura)", """
<p><b>Figura:</b> edge camera a sinistra, pinspeck camera a destra, ciascuna con A, A<sup>−1</sup> e B.</p>
<ul>
<li><b>Edge camera</b> (a, b): l'occlusore è un semipiano, uno spigolo. Ogni pixel vede tutta la scena da un lato dello spigolo, e quanta ne vede dipende dalla posizione del pixel. A è <b>triangolare</b> (una metà bianca e una nera); ogni pixel è una somma cumulativa della scena. L'inversa fa le differenze fra pixel vicini.</li>
<li><b>Pinspeck camera</b> (c, d): l'opposto del pinhole, un piccolo <b>oggetto opaco</b> che blocca la luce invece di un foro che la fa passare. Nella figura l'occlusore blocca <b>due</b> valori della scena: ogni pixel vede tutto tranne due punti vicini, quindi A = 1 − A<sub>pinhole largo</sub> (1 = matrice di tutti uni), il "negativo" della camera a foro largo. A<sup>−1</sup> è a scacchiera, molto instabile.</li>
</ul>
<p>Esempio reale di edge camera: lo spigolo di un muro permette di "vedere dietro l'angolo" dalle deboli variazioni di luce sul pavimento (corner camera).</p>
<div class="box b"><b>Dal libro · cap. 7, § 7.4.1 Edge Camera e § 7.4.2 Pinspeck Camera</b><ul>
<li><b>Edge camera</b> (eq. 7.5): A è triangolare superiore di tutti 1, quindi il primo pixel vale la somma di tutta la scena, l<sub>s</sub>[0] = ∑<sub>n=0..12</sub> l<sub>w</sub>[n], e l'uscita è l'<b>integrale</b> (cumulativo) dell'ingresso, letto al contrario. L'inversa è bidiagonale con 1 e −1: una <b>derivata</b> (differenze fra pixel vicini). L'inversa regolarizzata B è una "derivata sfocata", lo stesso oggetto dei filtri derivativi di L5 (visionbook cap. 18).</li>
<li><b>Pinspeck camera</b>: senza occlusore ogni pixel vedrebbe la somma di tutta la scena, una costante (14 nell'esempio del libro). L'occlusore toglie un pezzetto di luce: l'uscita è la costante meno l'<b>ombra</b>, e l'ombra è esattamente l'uscita della camera a foro largo col segno cambiato. Il segnale utile è una piccola variazione sopra un fondo grande (ampia gamma dinamica): per questo è difficile da invertire con rumore.</li>
</ul><p>Fonte: <a href="https://visionbook.mit.edu/camera_as_linsys.html">visionbook, cap. 7</a>.</p></div>
""")

s(50, "Recovering the World from Sensor Measurements", """
<ul>
<li>Data una misura l<sub>s</sub> = A l<sub>w</sub>, si può recuperare l<sub>w</sub>?</li>
<li>Se A è quadrata e invertibile: l<sub>w</sub> = A<sup>−1</sup> l<sub>s</sub>, fatto.</li>
<li>In pratica A spesso <b>non è invertibile</b>:
<ul><li><b>mal condizionata</b>: un piccolo rumore di misura produce errori enormi su l<sub>w</sub>;</li>
<li><b>a rango deficiente</b> o non quadrata.</li></ul></li>
<li>È un problema <b>mal posto</b>: scene l<sub>w</sub> molto diverse danno misure l<sub>s</sub> quasi uguali.
<ul><li>La corner camera è un caso estremo: il segnale utile è una frazione minuscola della misura.</li></ul></li>
</ul>
<div class="box k"><b>Da saper spiegare</b><p>Con rumore, l<sub>s</sub> = A l<sub>w</sub> + η e A<sup>−1</sup> l<sub>s</sub> = l<sub>w</sub> + A<sup>−1</sup> η. Se A ha valori singolari piccoli, A<sup>−1</sup> li inverte in valori enormi e il termine A<sup>−1</sup>η domina. Il numero di condizionamento σ<sub>max</sub>/σ<sub>min</sub> misura quanto l'errore relativo viene amplificato.</p></div>
""")

s(51, "Regularized Least Squares", """
<p>Per ottenere un problema ben posto si aggiunge un termine di <b>regolarizzazione</b> che penalizza soluzioni implausibili (es. l<sub>w</sub> molto grandi o rumorose):</p>
<span class="f">E(l<sub>w</sub>) = ‖l<sub>s</sub> − A l<sub>w</sub>‖² + λ ‖l<sub>w</sub>‖²</span>
<ul>
<li>Primo termine, <b>data fidelity</b>: quanto bene l<sub>w</sub> spiega la misura.</li>
<li>Secondo termine, <b>regolarizzatore</b>: preferisce soluzioni di norma piccola (un prior semplice), pesato da λ &gt; 0.</li>
<li><b>λ regola il compromesso</b>: λ → 0 riporta ai minimi quadrati (possibilmente instabili); λ grande spinge verso l<sub>w</sub> ≈ 0.</li>
</ul>
<div class="box x"><b>Approfondimento</b><p>Interpretazione probabilistica: è la stima MAP con rumore gaussiano sulla misura e prior gaussiano a media zero su l<sub>w</sub>; λ è il rapporto fra varianza del rumore e varianza del prior. Altri regolarizzatori codificano prior diversi, per esempio ‖D l<sub>w</sub>‖² con D = derivata premia scene lisce.</p></div>
""")

s(52, "Deriving the Regularized Inverse", """
<ol>
<li>Si espande l'obiettivo:
<span class="f">E(l<sub>w</sub>) = (l<sub>s</sub> − A l<sub>w</sub>)<sup>T</sup>(l<sub>s</sub> − A l<sub>w</sub>) + λ l<sub>w</sub><sup>T</sup> l<sub>w</sub></span></li>
<li>Si calcola il gradiente rispetto a l<sub>w</sub> e lo si pone a zero:
<span class="f">∇E = −2 A<sup>T</sup>(l<sub>s</sub> − A l<sub>w</sub>) + 2λ l<sub>w</sub> = 0</span></li>
<li>Riordinando:
<span class="f">A<sup>T</sup>A l<sub>w</sub> + λ l<sub>w</sub> = A<sup>T</sup> l<sub>s</sub>  ⇒  (A<sup>T</sup>A + λI) l<sub>w</sub> = A<sup>T</sup> l<sub>s</sub></span></li>
<li>Risolvendo per l<sub>w</sub> si ottiene l'inversa regolarizzata in forma chiusa (slide successiva).</li>
</ol>
<div class="box k"><b>Da saper fare</b><p>Rifai la derivazione a mano. Le due regole che servono: ∇<sub>x</sub>(x<sup>T</sup>x) = 2x e ∇<sub>x</sub>‖b − Ax‖² = −2A<sup>T</sup>(b − Ax). E è convessa (somma di quadrati), quindi il punto a gradiente nullo è il minimo globale.</p></div>
<div class="box b"><b>Dal libro · cap. 7, § 7.3, eq. 7.2–7.4</b><p>Stessa derivazione nel libro, con una differenza di notazione: l'eq. 7.3 è già divisa per 2, cioè scrive 0 = AᵀA l<sub>w</sub> − Aᵀ l<sub>s</sub> + λ l<sub>w</sub>. Il risultato (eq. 7.4) è identico: l<sub>w</sub> = (AᵀA + λI)<sup>−1</sup>Aᵀ l<sub>s</sub>. Il libro chiama B "the regularized inverse of the imaging matrix A" e descrive λ come il peso del compromesso fra spiegare le osservazioni e soddisfare il termine di regolarizzazione; non fissa un valore numerico. Fonte: <a href="https://visionbook.mit.edu/camera_as_linsys.html">visionbook, cap. 7</a>.</p></div>
""")

s(53, "The Regularized Inverse", """
<p>Minimizzando E(l<sub>w</sub>) si ottiene la soluzione in forma chiusa:</p>
<span class="f">l<sub>w</sub> = (A<sup>T</sup>A + λI)<sup>−1</sup> A<sup>T</sup> l<sub>s</sub> = B l<sub>s</sub></span>
<ul>
<li><b>B = (A<sup>T</sup>A + λI)<sup>−1</sup> A<sup>T</sup></b> è la <b>(pseudo)inversa regolarizzata</b> di A.</li>
<li>Aggiungere λI rende A<sup>T</sup>A + λI invertibile anche quando A<sup>T</sup>A è singolare o mal condizionata: <b>sposta tutti gli autovalori in su di λ</b>, lontano da zero.</li>
<li>È la classica <b>regolarizzazione di Tikhonov</b>, cioè la <b>ridge regression</b> del machine learning: qui il "modello" è la camera e i "dati" sono le misure.</li>
</ul>
<div class="box k"><b>Da saper fare</b><ul>
<li>Perché è invertibile: A<sup>T</sup>A è semidefinita positiva (autovalori ≥ 0); sommando λI gli autovalori diventano ≥ λ &gt; 0.</li>
<li>Caso scalare: A = a. Allora B = a / (a² + λ). Con a = 0.01 l'inversa vera è 100 (amplifica il rumore di 100 volte); con λ = 0.01, B = 0.01 / 0.0101 ≈ 0.99. Se a è grande, B ≈ 1/a.</li></ul></div>
<div class="box x"><b>Approfondimento: la vista SVD</b><p>Con A = U Σ V<sup>T</sup>, A<sup>−1</sup> divide ogni componente per σ<sub>i</sub>, mentre B la moltiplica per σ<sub>i</sub> / (σ<sub>i</sub>² + λ). Per σ<sub>i</sub> grandi è quasi 1/σ<sub>i</sub>; per σ<sub>i</sub> piccoli tende a 0 invece di esplodere. La regolarizzazione "spegne" le direzioni che la camera misura male.</p></div>
""")

s(54, "The Regularized Inverse (2)", """
<ul>
<li>Nel pinhole rumoroso (foro grande), <b>A<sup>−1</sup> ha un pattern a scacchiera</b>, mentre l'inversa regolarizzata B è più liscia.</li>
<li>La scacchiera rende A<sup>−1</sup> molto <b>sensibile al rumore</b>: piccoli errori di misura diventano errori grandi e ad alta frequenza su l<sub>w</sub>.</li>
</ul>
<p><b>Figura:</b> la stessa della slide 47, pinhole piccolo e pinhole grande con A, A<sup>−1</sup> e B. (La didascalia "Edge and pinspeck cameras" è sbagliata: è un copia-incolla, qui ci sono due pinhole.)</p>
<div class="box x"><b>Perché proprio una scacchiera</b><p>Una scacchiera, +1 −1 +1 −1, è la frequenza più alta rappresentabile (la Nyquist di L6). Un blur attenua soprattutto le alte frequenze; l'inversa esatta deve riamplificarle di molto, ed è proprio lì che il rumore ha più peso rispetto al segnale. In Fourier (L3) diventa evidente: dividere per la risposta del blur, piccola ad alta frequenza.</p></div>
<div class="box b"><b>Dal libro · cap. 7, § 7.3 (perché A<sup>−1</sup> è una scacchiera)</b><p>Il libro dice solo che A<sup>−1</sup> "contiene molti cambi rapidi" e rende il risultato molto sensibile al rumore, mentre B è "better behaved" e dà ricostruzioni con meno artefatti. Il perché si vede facendo il conto sulla sua A (due 1 consecutivi per riga, slide 47): vedi il riquadro sotto. Fonte: <a href="https://visionbook.mit.edu/camera_as_linsys.html">visionbook, cap. 7</a>.</p></div>
<div class="box k"><b>Da saper fare</b><p>Scrivi A = I + U, con U la matrice che ha 1 sulla prima sopradiagonale (U è nilpotente: U<sup>k</sup> ha 1 sulla k-esima sopradiagonale). Allora</p>
<span class="f">A<sup>−1</sup> = I − U + U² − U³ + …,   (A<sup>−1</sup>)<sub>ij</sub> = (−1)<sup>j−i</sup> per j ≥ i, 0 altrimenti</span>
<p>È una <b>scacchiera</b> di ±1 nel triangolo superiore, esattamente la figura. Ogni valore ricostruito è una somma a segni alterni di <b>tutte</b> le misure successive: il rumore non si smorza con la distanza, si accumula. Per confronto, l'edge camera ha A = I + U + U² + … = (I − U)<sup>−1</sup>, quindi A<sup>−1</sup> = I − U, la derivata della slide 49.</p></div>
""")

s(55, "The Regularized Inverse (3)", """
<p>Si nota come l'inversa regolarizzata B <b>differisca</b> dall'inversa vera A<sup>−1</sup>.</p>
<p><b>Figura:</b> di nuovo edge camera e pinspeck camera (slide 49). Per entrambe A<sup>−1</sup> è una scacchiera o una banda di differenze molto contrastata, mentre B è una versione attenuata e liscia.</p>
<p>B non è A<sup>−1</sup>: introduce un <b>bias</b> (la ricostruzione è leggermente sbagliata ma stabile) in cambio di una grande <b>riduzione della varianza</b> dovuta al rumore. È il compromesso bias/varianza scritto in algebra lineare.</p>
""")

s(56, "The Regularized Inverse (4)", """
<ul>
<li>Modello diretto lineare + inversa regolarizzata è uno <b>schema ricorrente</b> in computer vision.</li>
<li><b>Convoluzione/deconvoluzione</b>: un blur è un operatore lineare A (una matrice di convoluzione); il <b>deblurring</b> si risolve con inversione regolarizzata.
<ul><li>Il pinhole sfocato applica un blur all'immagine (convoluzione). Invertire il pinhole sfocato è una <b>deconvoluzione</b>.</li></ul></li>
</ul>
<div class="box x"><b>Collegamento con L3</b><p>Se A è una convoluzione con kernel h, in Fourier diventa un prodotto punto per punto per H(ω). L'inversa regolarizzata diventa allora una divisione "protetta":</p>
<span class="f">L<sub>w</sub>(ω) = H*(ω) L<sub>s</sub>(ω) / (|H(ω)|² + λ)</span>
<p>È la stessa formula di B, frequenza per frequenza (A<sup>T</sup> diventa il coniugato H*). Con λ scelto dal rapporto rumore/segnale è il filtro di <b>Wiener</b>.</p></div>
""")

s(57, "Color", "<p>Quinta parte: spettri, riflettanza, color constancy, coni e metamerismo.</p>", kind="div", sec=("l2-colore", "Colore", "slide 57–69"))

s(58, "Color Is Ambiguous", """
<ul>
<li>La luce porta con sé un intero <b>spettro</b> di potenza in funzione della lunghezza d'onda.</li>
<li>La nostra visione a colori <b>comprime</b> quello spettro in pochi numeri.</li>
<li>La compressione è <b>con perdita</b> e <b>ambigua</b>:
<ul><li>gli stessi tre numeri possono venire da molti spettri fisici diversi;</li>
<li>la stessa superficie può dare numeri molto diversi sotto luci diverse.</li></ul></li>
<li>I colori delle immagini devono corrispondere alla nostra percezione, anch'essa con perdita.</li>
</ul>
<p><b>Figura:</b> spettro misurato della luce di un cielo azzurro: intensità in funzione della lunghezza d'onda da 350 a 900 nm, con un picco fra 500 e 550 nm e una coda lunga verso il rosso.</p>
""")

s(59, "Light Power Spectra", """
<ul>
<li>La luce visibile va da circa <b>400 a 700 nm</b>, dal blu/violetto al rosso scuro.</li>
<li>Una sorgente o un raggio riflesso è descritto completamente dal suo <b>spettro di potenza</b> l(λ): l'intensità a ogni lunghezza d'onda.</li>
<li>Un prisma separa un fascio per lunghezza d'onda e mostra che la luce "bianca" è una miscela ampia di tutte le lunghezze d'onda visibili.</li>
</ul>
<p><b>Figura:</b> l'arcobaleno dello spettro visibile, diviso in tre bande: 400–500 nm (blu), 500–600 nm (verde), 600–700 nm (rosso).</p>
<p>Da notare: l(λ) è una funzione, un oggetto a infinite dimensioni. I tre numeri RGB sono una sua proiezione su tre dimensioni.</p>
""")

s(60, "RGB and CMY", """
<p><b>Figura:</b> a sinistra i primari <b>additivi</b>: rosso, verde e blu, ciascuno disegnato come uno spettro a gradino che occupa una delle tre bande (600–700, 500–600, 400–500 nm). A destra i primari <b>sottrattivi</b>: bianco − rosso = <b>ciano</b>, bianco − verde = <b>magenta</b>, bianco − blu = <b>giallo</b>, ciascuno con lo spettro a cui manca una banda.</p>
<ul>
<li><b>Additivo</b> (schermi, luci): si <b>somma</b> luce. Rosso + verde + blu = bianco.</li>
<li><b>Sottrattivo</b> (pigmenti, stampa): ogni pigmento <b>toglie</b> una banda dalla luce bianca. Ciano + magenta + giallo tolgono tutto e danno (idealmente) nero.</li>
</ul>
""")

s(61, "Reflectance and the Diffuse Reflection Model", """
<ul>
<li>Si riprende la BRDF lambertiana: l<sub>out</sub> = a l<sub>in</sub> (n · p), con un albedo scalare a.</li>
<li>Rendendo esplicita la dipendenza da λ, la superficie ha uno <b>spettro di riflettanza</b> s(λ) ∈ [0, 1] (quanto riflette di ogni lunghezza d'onda), e lo spettro osservato è:</li>
</ul>
<span class="f">r(λ) = k · l<sub>in</sub>(λ) · s(λ)</span>
<ul>
<li>l<sub>in</sub>(λ): spettro dell'<b>illuminante</b>; s(λ): <b>riflettanza</b> del materiale; k: costante geometrica (il fattore n · p).</li>
<li>s(λ) è la proprietà del materiale che di solito interessa (maturazione di un frutto, tipo di materiale, salute…), ma ciò che si osserva, r(λ), è il suo <b>prodotto</b> con l'illuminante sconosciuto.</li>
</ul>
<p>In pratica l'albedo a di Lambert diventa una funzione di λ: il colore di un oggetto è la forma di s(λ).</p>
""")

s(62, "The Color Constancy Problem", """
<ul>
<li>r(λ) = k l<sub>in</sub>(λ) s(λ) è un <b>prodotto di due incognite</b>: da r(λ) da solo non si ricava s(λ) in modo univoco. Un oggetto rossastro sotto luce bianca e un oggetto grigio sotto luce rossastra possono dare lo stesso spettro osservato.</li>
<li><b>Color constancy</b>: il problema (mal posto) di stimare la riflettanza s(λ) conoscendo solo r(λ), cioè di <b>scontare l'illuminante</b>.</li>
<li>Il sistema visivo umano lo risolve in modo approssimato e automatico; le camere devono farlo con algoritmi espliciti (euristiche, statistiche o modelli appresi).</li>
</ul>
<div class="box x"><b>Approfondimento: il white balance</b><p>Euristica classica, <b>grey world</b>: si assume che la media della scena sia grigia e si scala ciascun canale R, G, B in modo che le medie diventino uguali. È un esempio di prior che rende risolvibile un problema mal posto, come λ nella parte precedente. Il white balance dell'ISP (slide 5) fa questo.</p></div>
<div class="box b"><b>Dal libro · cap. 8, § 8.2.3 Light Reflecting from Surfaces</b><ul>
<li>r(λ) = k l<sub>in</sub>(λ) s(λ) è nel libro il modello per le riflessioni <b>opache</b> (matte), una scala lunghezza d'onda per lunghezza d'onda; vale identico per la luce che attraversa un filtro, con lo spettro di <b>trasmittanza</b> al posto di s(λ).</li>
<li>La riflettanza porta informazione sul materiale: la fig. 8.7 confronta gli spettri di due fiori, uno blu e uno arancione.</li>
<li>Algoritmi citati dal libro per la color constancy: dall'euristica "l'oggetto <b>più luminoso</b> è bianco" a metodi statistici e reti neurali. Il grey world del riquadro sopra è un'euristica sorella, non citata dal libro.</li>
<li>Il libro sottolinea che nemmeno l'uomo risolve il problema in modo perfetto o coerente: è il senso del Dress (slide 64, fig. 8.8), dove luce calda ipotizzata → blu e nero, luce fredda → bianco e oro.</li>
</ul><p>Fonte: <a href="https://visionbook.mit.edu/color.html">visionbook, cap. 8</a>.</p></div>
""")

s(63, "Worked Example: The Same Pixel Value, Two Perceived Colors", """
<p><b>Figura:</b> l'illusione della scacchiera di Adelson. Un cilindro verde proietta un'ombra su una scacchiera; il quadrato A (fuori dall'ombra) sembra scuro, il quadrato B (in ombra) sembra chiaro.</p>
<ul>
<li>A e B hanno <b>valori di pixel identici</b> (verificalo, es. con un contagocce in un editor di immagini), eppure li vediamo diversi perché il sistema visivo <b>sconta l'ombra</b> apparente: è una forma automatica (e parziale) di color constancy.</li>
<li>I valori dei pixel <b>non</b> sono una lettura diretta del colore della superficie: sono il colore della superficie <b>intrecciato con l'illuminazione</b>.</li>
</ul>
""")

s(64, "The Dress", """
<p>La foto "#TheDress" (2015) è un esempio famoso:</p>
<ul>
<li>se si assume <b>luce calda</b>, il vestito appare <b>nero e blu</b>;</li>
<li>se si assume <b>luce fredda</b>, appare <b>bianco e oro</b>;</li>
<li>è un'assunzione implicita sull'illuminante, spesso fatta inconsciamente.</li>
</ul>
<p><b>Figura:</b> (a) la foto originale; (b) lo schema: la stessa immagine è compatibile con un vestito blu/nero sotto luce calda o con un vestito bianco/oro sotto luce fredda.</p>
<p>Il disaccordo fra persone mostra che l'ambiguità è reale: osservatori diversi usano prior diversi sull'illuminante per risolvere lo stesso prodotto di incognite. (Il vestito vero è blu e nero.)</p>
""")

s(65, "The Machinery of the Eye: Cones and Trichromacy", """
<ul>
<li>La retina ha <b>bastoncelli</b> (monocromatici, attivi con poca luce) e <b>coni</b> (visione a colori, attivi con luce normale).</li>
<li>Tre tipi di coni, <b>S, M, L</b> (picco di sensibilità a lunghezza d'onda corta, media, lunga). Ognuno integra la luce entrante su tutto lo spettro, pesata dalla propria curva di sensibilità.</li>
<li><b>Tricromia</b>: la percezione del colore è determinata (con buona approssimazione) da <b>soli tre numeri</b>, qualunque sia lo spettro completo della luce.</li>
<li>Per questo le rappresentazioni <b>RGB bastano</b> quando il destinatario è la visione umana.</li>
</ul>
<p><b>Figura:</b> curve di sensibilità normalizzate dei tre coni: S con picco verso i 440 nm, M verso i 540 nm, L verso i 570 nm. M e L sono molto sovrapposte.</p>
<div class="box b"><b>Dal libro · cap. 8, § 8.3.1 The Machinery of the Eye</b><p>Nel libro l'ordine è L, M, S e la risposta si scrive (L, M, S)<sup>T</sup> = C<sub>eye</sub> t (eq. 8.1), con t lo spettro campionato come vettore colonna. La fig. 8.9 mostra il <b>mosaico</b> dei coni misurato vicino alla fovea: impacchettamento circa esagonale, tipo di cono assegnato in modo casuale, e coni <b>S molto più radi</b> di L e M. Quest'ultimo fatto spiega la slide 69. Dal numero di tipi di coni discende il "tre" della tecnologia: tre primari, tre strati nella pellicola, tre sottopixel negli schermi. Fonte: <a href="https://visionbook.mit.edu/color.html">visionbook, cap. 8</a>.</p></div>
""")

s(66, "Cone Response as a Linear Map", """
<ul>
<li>La risposta di ogni cono è un <b>integrale pesato</b> dello spettro l(λ) con la sua curva di sensibilità.</li>
<li>Discretizzando lo spettro in N campioni e mettendo le tre sensibilità come righe di <b>C<sub>eye</sub> ∈ ℝ<sup>3×N</sup></b>, la risposta è una mappa lineare:</li>
</ul>
<span class="f">(L, M, S)<sup>T</sup> = C<sub>eye</sub> l(λ)</span>
<ul>
<li>Di nuovo un sistema lineare, come per le camere, ma applicato all'occhio: un sensore lineare con <b>3 righe</b> su un ingresso spettrale a <b>N dimensioni</b>.</li>
</ul>
<p>È la stessa struttura l<sub>s</sub> = A l<sub>w</sub> della quarta parte, con A = C<sub>eye</sub> molto "larga" (3 × N, con N grande).</p>
<div class="box b"><b>Dal libro · cap. 8, § 8.3.2–8.3.6 color matching (omesso dalle slide)</b><p>Il libro usa la stessa algebra lineare per spiegare come si <b>riproduce</b> un colore (camera + schermo):</p>
<ul>
<li>Fatti sperimentali: ogni colore si eguaglia con una combinazione lineare di <b>tre primari</b>, e gli eguagliamenti sono transitivi. Discendono dall'avere tre coni.</li>
<li>Un sistema di riproduzione ha sensibilità C (3 × N), una matrice di mescolamento M (3 × 3) e primari P (N × 3, spettri in colonna): lo spettro emesso è P M C t. Per apparire uguale all'originale serve C<sub>eye</sub> P M C = C<sub>eye</sub> (eq. 8.3).</li>
<li>Soluzione: <span class="f">C = R C<sub>eye</sub>  (R 3 × 3 invertibile),    M = (C P)<sup>−1</sup>   (eq. 8.5–8.6)</span>
le sensibilità del sensore devono essere <b>combinazioni lineari</b> di quelle dei coni. Due spazi colore validi differiscono per una matrice 3 × 3 (basi non per forza ortogonali).</li>
<li>Primari fisici richiedono pesi non negativi: i colori fuori dal <b>gamut</b> non si riproducono. Lo spazio <b>CIE XYZ</b> ha funzioni di matching tutte positive, ma nessuna terna di primari fisici positivi lo realizza. Coordinate di cromaticità: x = X/(X+Y+Z), y = Y/(X+Y+Z).</li>
</ul>
<p>Collegamento con la slide 67: una camera le cui curve <b>non</b> sono combinazioni lineari dei coni vede "metameri" diversi da quelli dell'occhio. Fonte: <a href="https://visionbook.mit.edu/color.html">visionbook, cap. 8</a>.</p></div>
""")

s(67, "Metamerism", """
<ul>
<li><b>Metamerismo</b>: due spettri fisicamente diversi che producono le <b>stesse tre risposte</b> dei coni, e quindi appaiono identici a un osservatore umano.</li>
<li>C<sub>eye</sub>: ℝ<sup>N</sup> → ℝ<sup>3</sup> va da uno spazio a molte dimensioni a ℝ<sup>3</sup>, quindi il suo <b>nucleo</b> (null space) è enorme: si può aggiungere a uno spettro un qualunque vettore del nucleo senza cambiare il colore percepito.</li>
<li>Le camere hanno <b>altre</b> tre curve di sensibilità, quindi possono non vedere uguali due spettri che per l'occhio sono uguali (o viceversa): un colore può sembrare giusto a occhio e venire registrato diverso dalla camera.</li>
<li>L'<b>imaging iperspettrale</b> (molte più di 3 bande) distingue metameri che ingannano sia l'occhio sia le camere RGB, al prezzo di sensori più complessi.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Teorema rango-nullità: se C<sub>eye</sub> ha rango 3, dim(nucleo) = N − 3. Con lo spettro campionato ogni 10 nm fra 400 e 700 (N = 31) il nucleo ha dimensione 28. Il metamerismo non è un caso raro, è la regola: quasi tutta l'informazione spettrale è invisibile.</p></div>
<div class="box x"><b>Approfondimento</b><p>Non ogni perturbazione del nucleo dà un metamero fisico: lo spettro risultante deve restare non negativo. Ma lo spazio disponibile resta enorme.</p></div>
<div class="box b"><b>Dal libro · cap. 8, § 8.3.3 Color Metamerism</b><p>Il libro definisce i metameri come spettri diversi con la stessa proiezione sulle funzioni di matching, e aggiunge una sfumatura: per la <b>percezione umana</b> un'immagine iperspettrale aggiunge "qualcosa, ma non molto" a ciò che forma il nostro occhio. Non contraddice la slide: l'iperspettrale distingue metameri per una <b>macchina</b> (materiali, maturazione, diagnosi), non rende più ricca la visione di chi guarda lo schermo. Fonte: <a href="https://visionbook.mit.edu/color.html">visionbook, cap. 8</a>.</p></div>
""")

s(68, "Spatial Resolution and Color", """
<ul>
<li>L'acutezza spaziale umana non è uniforme rispetto al colore: siamo molto più sensibili al dettaglio fine nella <b>luminanza</b> (luminosità) che nella <b>crominanza</b> (colore).</li>
<li>Equivalentemente, sfocare solo i canali di colore si nota molto meno che sfocare la luminanza.</li>
<li>L'asimmetria è sfruttata ovunque nella compressione di immagini e video (<b>chroma subsampling</b>).</li>
</ul>
<div class="box x"><b>Approfondimento</b><p>JPEG e i codec video passano da RGB a YCbCr (Y = luminanza, Cb e Cr = differenze di colore) e nel formato 4:2:0 salvano Cb e Cr a metà risoluzione in entrambe le direzioni: un quarto dei campioni di colore, differenza quasi invisibile.</p></div>
<div class="box b"><b>Dal libro · cap. 8, § 8.4 Spatial Resolution and Color</b><p>Il libro fa la dimostrazione in due spazi. In RGB (fig. 8.14–8.15) sfocare <b>R o G</b> rende sfocata l'immagine, sfocare B no. In <b>Lab</b> (RGB ruotato e stirato in modo non lineare: L luminanza, a e b crominanza; fig. 8.16–8.17) sfocare L si vede subito, sfocare solo a o b lascia l'immagine nitida purché L resti nitida. È la giustificazione del campionare la crominanza più grossolanamente nella compressione. Nelle conclusioni il libro lega l'effetto alla distribuzione rada dei coni S (slide 65). Il passaggio a YCbCr del riquadro sopra è l'analogo usato in JPEG. Fonte: <a href="https://visionbook.mit.edu/color.html">visionbook, cap. 8</a>.</p></div>
""")

s(69, "RGB Blur", """
<p><b>Figura:</b> la stessa foto di due bambine con un solo canale sfocato: (a) solo R, (b) solo G, (c) solo B.</p>
<ul>
<li>Con <b>G sfocato</b> l'intera immagine appare sfocata.</li>
<li>Con <b>R sfocato</b> l'immagine appare anch'essa sfocata (un po' meno che con G, ma si vede bene nei capelli e nella ringhiera).</li>
<li>Con <b>B sfocato</b> quasi non si nota.</li>
</ul>
<p>Il motivo: la luminanza è fatta soprattutto di verde (circa Y ≈ 0.30 R + 0.59 G + 0.11 B), e il verde cade dove le curve M e L dei coni si sovrappongono. Sfocare G (e in parte R) significa sfocare la luminanza; sfocare B tocca soprattutto la crominanza. È la dimostrazione visiva della slide 68.</p>
<div class="box b"><b>Dal libro · cap. 8, § 8.4, fig. 8.15</b><p>Didascalia del libro per questa figura: sfocare la componente <b>R oppure G</b> dà un'immagine a colori che sembra sfocata; solo B si può sfocare impunemente. Il motivo fisiologico indicato dal libro è la scarsità dei coni S, gli unici sensibili alle lunghezze d'onda corte: il sistema visivo campiona il blu a risoluzione spaziale molto più bassa. Fonte: <a href="https://visionbook.mit.edu/color.html">visionbook, cap. 8</a>.</p></div>
""")

s(70, "Conclusions", "<p>Chiusura: le tre ambiguità, i takeaway e le letture.</p>", kind="div")

s(71, "Summary: Three Ambiguities", """
<p>Le tre perdite di informazione della lezione:</p>
<ul>
<li><b>prospettiva</b> → dimensione ↔ profondità;</li>
<li><b>sistema lineare</b> l<sub>s</sub> = A l<sub>w</sub> → inversione mal posta;</li>
<li><b>riflettanza × illuminante</b> → color constancy.</li>
</ul>
<ul>
<li>Ogni stadio della formazione dell'immagine perde informazione:
<ul><li>geometria: da una scena 3D a un array 2D;</li>
<li>colore: da uno spettro continuo a 3 numeri;</li>
<li>camera: da una miscela lineare sconosciuta a un insieme finito di misure.</li></ul></li>
<li>Riconoscere <b>quale</b> informazione viene scartata (e come) è il primo passo per recuperarla: viste aggiuntive, prior, regolarizzazione o modelli appresi.</li>
</ul>
""")

s(72, "Key Takeaways", """
<ul>
<li>Il modello <b>pinhole/prospettico</b> è il modello geometrico di tutta la Parte 2 del corso; si vedranno un modello di camera completo e come stimare profondità e dimensione.</li>
<li><b>Camere come sistemi lineari</b> l<sub>s</sub> = A l<sub>w</sub>: recuperare l<sub>w</sub> è un problema inverso mal posto, stabilizzato con la <b>regolarizzazione</b>.</li>
<li>Il <b>colore</b> è una compressione in 3 numeri di uno spettro completo, e dipende sia dal materiale sia dalla luce.</li>
</ul>
""")

s(73, "Further Reading", """
<p><a href="https://visionbook.mit.edu/">MIT Vision Book</a> (Torralba, Isola, Freeman), capitoli 5, 6, 7, 8. Il libro è più dettagliato delle slide, e quasi tutte le figure della lezione vengono da lì.</p>
<p>Per la proiezione in coordinate omogenee, i parametri intrinseci e la linea dell'orizzonte aggiungi il <a href="https://visionbook.mit.edu/imaging_geometry.html">cap. 39</a> (§ 39.2–39.3), che anticipa la parte di geometria. Percorso di lettura completo nella sezione "Studia dal libro" in fondo alla pagina.</p>
""")

s(74, "Next Lecture", """
<ul>
<li>Oggi le immagini sono state trattate come <b>output di un processo fisico</b> di formazione.</li>
<li>Nella <b>lezione 3</b> diventano <b>segnali</b>: si costruiscono gli strumenti (trasformata di Fourier e convoluzione) per analizzarle e manipolarle.</li>
</ul>
<p>Collegamento: il pinhole sfocato (slide 47) è già una convoluzione, e la deconvoluzione regolarizzata (slide 56) diventa semplice in Fourier.</p>
""")
