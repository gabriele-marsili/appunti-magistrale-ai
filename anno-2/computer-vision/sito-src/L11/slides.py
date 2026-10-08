
s(1, "Copertina", """
<p><b>Camera Model and Perspective Geometry</b>, sottotitolo <i>Homogeneous Coordinates, Intrinsics and Extrinsic Parameters</i>. Undicesima lezione (7 ottobre 2026).</p>
<p>Si riprende la camera pinhole di L2 e la si scrive come <b>prodotto di matrici</b>. Gli strumenti:</p>
<ul>
<li><b>coordinate omogenee</b> (già viste di corsa in L9 per le omografie): tutte le trasformazioni, proiezione compresa, diventano prodotti matrice-vettore;</li>
<li><b>parametri intrinseci K</b>: da coordinate della camera (metri) a pixel;</li>
<li><b>parametri estrinseci R, T</b>: dal riferimento del mondo a quello della camera;</li>
<li>la <b>matrice completa</b> p = K[R | −RT]P<sub>W</sub>.</li>
</ul>
<p>Fonte principale: visionbook cap. 38 (rappresentare immagini e geometria) e cap. 39, § 39.1–39.5 (modello della camera). La L12 userà questo modello per la calibrazione.</p>
""")

s(2, "Motivation and Roadmap", "<p>Perché serve un modello proiettivo della camera e cosa si costruisce oggi.</p>", kind="div", sec=("l11-intro", "Motivazione e roadmap", "slide 2–6"))

s(3, "Recap: the Pinhole Camera Model", """
<ul>
<li><b>Camera pinhole</b>: la luce di un punto 3D passa per un solo piccolo foro e forma sul sensore un'immagine <b>capovolta</b>.</li>
<li><b>Equazioni di proiezione</b> (caso semplice: origine nel foro, asse Z lungo l'asse ottico):</li>
</ul>
<span class="f">x = f X / Z,   y = f Y / Z</span>
<p><b>Figura</b> (visionbook, cap. 5): (a) un albero davanti a un muro senza schermo: ogni punto del muro riceve luce da tutti i punti dell'albero, quindi nessuna immagine; (b) con una barriera nera e un foro, ogni punto del muro riceve luce da un solo punto dell'albero: compare l'albero capovolto.</p>
<p><b>Oggi</b>: si generalizza il modello a un sistema di coordinate qualsiasi (camera spostata e ruotata), e ogni cambio di coordinate diventa una moltiplicazione di matrici.</p>
<p>Collegamento: è la proiezione prospettica di L2 (formazione dell'immagine).</p>
""")

s(4, "Why We Need a Projective Model", """
<ul>
<li><b>Dai pixel alla nuvola di punti</b>: ogni compito 3D (stima della profondità, tracking, ricostruzione) richiede di <b>invertire</b> la proiezione, cioè risalire dai pixel 2D alla struttura 3D.</li>
<li>Le coordinate cartesiane sono scomode: la proiezione richiede una <b>divisione per Z</b>, è <b>non lineare</b>, difficile da comporre e invertire.</li>
<li>Le <b>coordinate omogenee</b> rendono proiezione, rotazione, traslazione e scala tutte <b>moltiplicazioni di matrici</b>.</li>
<li>Risultato: un modello di camera anche complesso è <b>una sola matrice</b>.</li>
</ul>
""")

s(5, "From Pixels to Point Cloud", """
<p>Tre modi di rappresentare un'immagine:</p>
<ul>
<li><b>Griglia di pixel</b>: matrice ℓ[n, m], n = 1…N, m = 1…M. È la rappresentazione di convoluzioni e Fourier (L3–L6); la geometria è implicita nella posizione nell'array.</li>
<li><b>Nuvola di punti</b>: insieme {(ℓ<sub>i</sub>, x<sub>i</sub>, y<sub>i</sub>)}: intensità più posizione esplicita.
<ul><li>Spostare, ruotare, scalare diventa facile: si cambiano le coordinate dei punti.</li>
<li>Problema: tornando alla griglia i punti trasformati <b>non cadono sui centri dei pixel</b> (serve interpolare, vedi warping).</li></ul></li>
<li><b>Rappresentazione implicita</b>: ℓ(x, y) = f<sub>θ</sub>(x, y), l'immagine come funzione continua di (x, y). f<sub>θ</sub> può essere un'interpolazione dei pixel o una rete neurale.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 38, § 38.1 Introduction e § 38.6 Implicit Image Representations</b><p>Il libro presenta le tre rappresentazioni come complementari, non alternative: si usa quella che rende semplice l'operazione da fare. Esempio: traslare di un pixel a destra nella forma "insieme di pixel" è solo x<sub>i</sub> → x<sub>i</sub> + 1. Nel § 38.6 la forma implicita viene sviluppata: con l'interpolazione nearest neighbor o bilineare θ è l'immagine stessa; con una rete (una SIREN addestrata sulle coppie posizione → intensità) θ sono i pesi, e la rete deve rispondere anche a coordinate non intere. Il warping diventa ℓ̂(x, y) = f<sub>θ</sub>(M<sup>−1</sup>[x, y, 1]<sup>⊤</sup>). Il libro non usa il termine "point cloud": parla di insieme di pixel. <a href="https://visionbook.mit.edu/homogeneous_coordinates.html" target="_blank">visionbook.mit.edu/homogeneous_coordinates.html</a></p></div>
""")

s(6, "Roadmap", """
<ul>
<li><b>Coordinate omogenee</b>: geometria proiettiva, come rappresentare punti e trasformazioni.</li>
<li><b>Modello della camera</b>:
<ul><li><b>Intrinseci K</b>: da coordinate camera a pixel (focale, punto principale, skew, aspect ratio);</li>
<li><b>Estrinseci R, T</b>: trasformazione rigida dal mondo alla camera;</li>
<li><b>Matrice della camera</b> P = K[R | −RT]: proiezione completa dal mondo ai pixel.</li></ul></li>
</ul>
<p>Nota sulla notazione: la slide chiama P la matrice 3×4; il libro la chiama <b>M</b> (§ 39.5) e usa P per i punti 3D. Qui P<sub>W</sub> è il punto nel mondo.</p>
""")

s(7, "Homogeneous Coordinates", "<p>Aggiungere una coordinata per rendere lineari traslazioni e proiezioni.</p>", kind="div", sec=("l11-omogenee", "Coordinate omogenee", "slide 7–11"))

s(8, "Why Euclidean Coordinates Are Awkward for Projection", """
<p><b>Coordinate cartesiane</b> (eterogenee). Notazione del visionbook: <b>maiuscole</b> per il mondo 3D (X, Y, Z), <b>minuscole</b> per l'immagine (x, y).</p>
<p>In cartesiane ogni trasformazione ha una "forma" diversa:</p>
<ul>
<li><b>Proiezione</b> x = fX/Z: un <b>rapporto</b>, non è una mappa lineare di (X, Y, Z).</li>
<li><b>Traslazione</b> x = X + T<sub>x</sub>: una <b>somma</b> (trasformazione affine, non lineare: l'origine non resta ferma).</li>
<li><b>Rotazione e scala</b>: prodotti matrice-vettore.</li>
</ul>
<p>Tre "linguaggi" diversi per tre operazioni: comporle richiede di tenere traccia di ciascuna. Le coordinate omogenee le unificano.</p>
""")

s(9, "Heterogeneous vs Homogeneous in Code", """
<ul>
<li><b>Cartesiane</b>: <code>point2d = scale(translate(rotate(point3d, 30), 10), 2)</code>
<ul><li>bisogna conoscere e applicare ogni trasformazione separatamente, nell'ordine giusto;</li>
<li>comporre e invertire trasformazioni arbitrarie è scomodo.</li></ul></li>
<li><b>Omogenee</b>: <code>point2d = map_homogeneous(point3d, Amat)</code>
<ul><li>basta la matrice della composizione, non serve ricordare i singoli passi;</li>
<li><b>composizione = prodotto di matrici</b>, <b>inversione = inversa della matrice</b>.</li></ul></li>
</ul>
<p>Vantaggio pratico: una catena di 10 trasformazioni applicata a un milione di punti costa un solo prodotto 3×3 (o 4×4) per punto.</p>
""")

s(10, "Homogeneous Coordinates: Scale Invariance", """
<ul>
<li>Le coordinate omogenee aggiungono <b>una dimensione</b>: [x, y, 1] per un punto 2D, [X, Y, Z, 1] per un punto 3D.</li>
<li>Notazione del visionbook: <b>parentesi quadre</b> per le omogenee, <b>tonde</b> per le cartesiane.</li>
<li>In cartesiane si possono <b>sommare</b> i punti, in omogenee no: [x<sub>1</sub>, y<sub>1</sub>, 1] + [x<sub>2</sub>, y<sub>2</sub>, 1] ha terza componente 2 e rappresenta il punto medio, non la somma.</li>
</ul>
<p><b>Figura</b> (visionbook, fig. 38.1): spazio (x, y, w). Il piano grigio a sinistra è il piano cartesiano con il punto (x, y); il piano w = 1 contiene (x, y, 1); la retta tratteggiata per l'origine passa per (x, y, 1) e per (λx, λy, λ). Tutti i punti di quella retta rappresentano lo stesso punto cartesiano.</p>
<div class="box b"><b>Dal libro · cap. 38, § 38.2 Homogeneous and Heterogeneous Coordinates</b><p>Il libro attribuisce l'idea a Möbius (1827). Conversioni: (x, y) → [x, y, 1]<sup>⊤</sup>, (x, y, z) → [x, y, z, 1]<sup>⊤</sup>; all'indietro [x, y, w]<sup>⊤</sup> → (x/w, y/w). Ogni multiplo non nullo [λx, λy, λ]<sup>⊤</sup> è lo stesso punto. L'avvertenza sulla somma è nel libro: in omogenee contano solo le direzioni (rette per l'origine), non i vettori. <a href="https://visionbook.mit.edu/homogeneous_coordinates.html" target="_blank">visionbook.mit.edu/homogeneous_coordinates.html</a></p></div>
""")

s(11, "Homogeneous Coordinates", """
<p><b>Invarianza di scala</b>:</p>
<span class="f">[x, y, w]<sup>⊤</sup> ≡ [λx, λy, λw]<sup>⊤</sup>   per ogni λ ≠ 0</span>
<ul>
<li>Un punto cartesiano diventa un'intera <b>retta per l'origine</b> nello spazio omogeneo.</li>
<li>Conversione a cartesiane: [x, y, w] → (x/w, y/w).</li>
<li>Questo grado di libertà in più è ciò che rende <b>lineare la proiezione</b>: la divisione per Z si rimanda alla conversione finale.</li>
</ul>
<p><b>Figura</b>: la stessa di fig. 38.1 (scheda 10).</p>
<div class="box k"><b>Da saper fare</b><p>[6, 4, 2] e [3, 2, 1] sono lo stesso punto (3, 2). [1, 2, 0] non ha corrispondente cartesiano: è un <b>punto all'infinito</b> nella direzione (1, 2). È qui che i punti di fuga entrano in modo naturale: la proiezione di rette parallele converge a un punto all'infinito del piano 3D che diventa finito nell'immagine.</p></div>
""")

s(12, "2D Image Transformations", "<p>Traslazione, scala, rotazione, shear come matrici 3×3 e loro composizione.</p>", kind="div", sec=("l11-trasf2d", "Trasformazioni 2D", "slide 12–27"))

s(13, "2D Image Transformations", """
<ul>
<li>Obiettivo: scrivere le trasformazioni dell'immagine come <b>prodotti di matrici</b> in coordinate omogenee.</li>
<li>Trasformazioni più complesse si ottengono per <b>composizione</b>, e restano un solo prodotto di matrici.</li>
<li>Non tutto è una matrice: deformazioni libere (warping arbitrario), distorsione di una lente fisheye. Per questo corso le matrici bastano.</li>
</ul>
<p><b>Figura</b> (visionbook, fig. 38.2): la foto di un orologio da parete e cinque versioni trasformate: traslata, ruotata, scalata (più grande), con shear (inclinata come un parallelogramma) e con un warping arbitrario in cui l'orologio si piega come in un quadro di Dalí. Solo l'ultima non è esprimibile con una matrice 3×3.</p>
<p>Nota: la slide dice "rigid image transformations", ma scala e shear non sono rigide (non conservano le distanze): qui "rigido" va inteso come "parametrico, globale".</p>
""")

s(14, "Translation: Matrix in Euclidean and Homogeneous Coordinates", """
<p><b>Cartesiane</b>: (x, y) → (x + t<sub>x</sub>, y + t<sub>y</sub>): una somma, <b>non</b> una mappa lineare.</p>
<p><b>Omogenee</b>: matrice di traslazione di (t<sub>x</sub>, t<sub>y</sub>):</p>
<span class="f">T = [[1, 0, t<sub>x</sub>], [0, 1, t<sub>y</sub>], [0, 0, 1]],   p′ = T p</span>
<p>Il trucco: la terza componente vale 1, quindi l'ultima colonna viene moltiplicata per 1 e <b>sommata</b>. La traslazione diventa un prodotto come tutte le altre trasformazioni.</p>
<div class="box b"><b>Dal libro · cap. 38, § 38.3.1 Translation</b><p>Il libro sottolinea che le omogenee hanno "trasformato una somma in un prodotto". Mostra anche la composizione di due traslazioni (prossima scheda) e che il prodotto di due matrici di traslazione commuta. Attenzione alla notazione del libro: nel § 38.3.1 chiama <b>S</b> la seconda traslazione, la stessa lettera che nel § 38.3.2 indica la scala. <a href="https://visionbook.mit.edu/homogeneous_coordinates.html" target="_blank">visionbook.mit.edu/homogeneous_coordinates.html</a></p></div>
""")

s(15, "Composition of Translations", """
<ul>
<li>Traslare prima di (t<sub>x1</sub>, t<sub>y1</sub>) poi di (t<sub>x2</sub>, t<sub>y2</sub>): <b>T<sub>2</sub>T<sub>1</sub></b> (la prima applicata è quella a destra).</li>
<li>Il prodotto di due traslazioni è una traslazione di (t<sub>x1</sub> + t<sub>x2</sub>, t<sub>y1</sub> + t<sub>y2</sub>).</li>
<li>Principio generale: <b>comporre trasformazioni = moltiplicare le matrici</b>.</li>
<li>In cartesiane si sommano i due vettori di traslazione: stesso risultato.</li>
</ul>
<p><b>Figura</b> (visionbook, fig. 38.3): a sinistra un quadrato arancione nell'origine spostato dal vettore t; a destra due spostamenti successivi t e s, equivalenti a un solo spostamento t + s.</p>
<div class="box k"><b>Da saper fare</b><p>T(3, 4)·T(1, −2) = [[1, 0, 4], [0, 1, 2], [0, 0, 1]]: traslazione di (4, 2) (verificato con numpy). Le traslazioni commutano fra loro; in generale le trasformazioni no (scheda 24).</p></div>
""")

s(16, "Scaling", """
<ul>
<li><b>Scala</b> di (s<sub>x</sub>, s<sub>y</sub>) rispetto all'origine:</li>
</ul>
<span class="f">S = [[s<sub>x</sub>, 0, 0], [0, s<sub>y</sub>, 0], [0, 0, 1]]</span>
<ul>
<li>Allunga o comprime le coordinate <b>rispetto all'origine</b>: un oggetto lontano dall'origine si sposta anche, oltre a cambiare dimensione.</li>
<li>Il blocco 2×2 in alto a sinistra è la matrice di scala in cartesiane: per le trasformazioni lineari le omogenee aggiungono solo una riga e una colonna banali.</li>
</ul>
""")

s(17, "Scaling: Isotropic vs Anisotropic", """
<ul>
<li><b>Scala uniforme</b> (isotropa, s<sub>x</sub> = s<sub>y</sub>): conserva gli <b>angoli</b> (similitudine).</li>
<li><b>Scala non uniforme</b> (anisotropa): gli angoli cambiano, un quadrato diventa un rettangolo, un cerchio un'ellisse.</li>
</ul>
<p><b>Figura</b> (visionbook, fig. 38.4): un quadrato di lato 2 centrato nell'origine e lo stesso dopo x′ = 2x, y′ = 0.5y: un rettangolo largo e basso.</p>
<div class="box b"><b>Dal libro · cap. 38, § 38.3.2 Scaling</b><p>Il libro aggiunge due proprietà: con qualunque scala le rette parallele restano parallele, e le <b>aree</b> vengono moltiplicate per il determinante s<sub>x</sub>s<sub>y</sub> (nella figura 2 × 0.5 = 1: l'area del quadrato resta 4). <a href="https://visionbook.mit.edu/homogeneous_coordinates.html" target="_blank">visionbook.mit.edu/homogeneous_coordinates.html</a></p></div>
""")

s(18, "Rotation", """
<ul>
<li><b>Rotazione antioraria</b> di θ attorno all'origine:</li>
</ul>
<span class="f">R = [[cos θ, −sin θ, 0], [sin θ, cos θ, 0], [0, 0, 1]]</span>
<p><b>Figura</b> (visionbook, fig. 38.5): un quadrato centrato nell'origine e lo stesso ruotato di un angolo θ, con le frecce tratteggiate che indicano il verso.</p>
<p>Controllo rapido: con θ = 90° il punto (1, 0) va in (0, 1), cioè in senso antiorario se l'asse y punta in alto.</p>
""")

s(19, "Rotation: Euclidean vs Image Coordinates", """
<p>Nota del docente sul libro:</p>
<ul>
<li>La matrice di rotazione scritta nel cap. 38 (tranne la fig. 38.7) è in realtà una rotazione <b>oraria</b> in coordinate euclidee; nelle slide si usa la vera rotazione <b>antioraria</b>.</li>
<li>Nelle coordinate pixel l'asse <b>y punta in basso</b>: una rotazione antioraria in coordinate euclidee appare <b>oraria</b> sullo schermo.</li>
</ul>
<p><b>Figura</b>: a sinistra assi euclidei (y in alto) con una freccia che gira in senso antiorario; a destra assi immagine (y in basso) con la stessa trasformazione, che appare ribaltata e quindi oraria.</p>
<div class="box b"><b>Dal libro · cap. 38, § 38.3.3 Rotation (verifica)</b><p>Verificato sul libro: il § 38.3.3 scrive R = [[cos θ, sin θ, 0], [−sin θ, cos θ, 0], [0, 0, 1]] e la chiama "counterclockwise". Con p′ = Rp e asse y in alto, questa matrice manda (1, 0) in (cos θ, −sin θ): è oraria. Quindi la nota della slide è <b>corretta</b>; la matrice del libro diventa antioraria solo pensando all'asse y verso il basso (coordinate immagine). La figura riassuntiva 38.7 (scheda 23) usa invece la forma con −sin in alto a destra. Il libro aggiunge: det R = 1, R<sup>⊤</sup> = R<sup>−1</sup>, due rotazioni si sommano negli angoli, per θ piccolo R ≈ [[1, θ], [−θ, 1]] (una rotazione piccola è uno shear), e una rotazione si può scrivere come due shear e una scala. <a href="https://visionbook.mit.edu/homogeneous_coordinates.html" target="_blank">visionbook.mit.edu/homogeneous_coordinates.html</a></p></div>
""")

s(20, "Rotation", """
<span class="f">R = [[cos θ, −sin θ, 0], [sin θ, cos θ, 0], [0, 0, 1]]</span>
<ul>
<li>Il blocco 2×2 in alto a sinistra è la rotazione in cartesiane.</li>
<li>R è <b>ortogonale</b> sia in cartesiane sia in omogenee:
<ul><li>si inverte gratis: <b>R<sup>⊤</sup> = R<sup>−1</sup></b> (la rotazione di −θ);</li>
<li>conserva le <b>distanze dall'origine</b> (e anche angoli e distanze fra punti).</li></ul></li>
</ul>
<p>Nota: nella slide "R<sup>T</sup>" indica la trasposta, non va confuso con il vettore di traslazione T degli estrinseci (schede 62–68).</p>
""")

s(21, "Derivation of Rotation", """
<p>Come ricavare R: guardare dove vanno i <b>vettori della base</b>.</p>
<ul>
<li>(1, 0) = (cos 0, sin 0) → (cos θ, sin θ).</li>
<li>(0, 1) = (cos π/2, sin π/2) → (cos(π/2 + θ), sin(π/2 + θ)) = (−sin θ, cos θ).</li>
<li>Le immagini dei vettori di base sono le <b>colonne</b> della matrice: R = [[cos θ, −sin θ], [sin θ, cos θ]].</li>
</ul>
<p><b>Figura</b> (Wikimedia Commons): circonferenza unitaria con il punto (cos t, sin t) all'angolo t dall'asse x.</p>
<div class="box k"><b>Da saper fare: il metodo vale per ogni matrice</b><p>Per una trasformazione lineare qualsiasi, la colonna j della matrice è l'immagine del j-esimo vettore di base. Con lo stesso ragionamento si scrivono al volo shear (e<sub>2</sub> → (q<sub>x</sub>, 1)) e scala (e<sub>1</sub> → (s<sub>x</sub>, 0)). Nelle omogenee la terza colonna è l'immagine dell'origine [0, 0, 1]: ecco perché lì sta la traslazione.</p></div>
""")

s(22, "Shearing", """
<ul>
<li><b>Shear orizzontale</b> di q<sub>x</sub>: x′ = x + q<sub>x</sub>y (ogni riga scivola in proporzione alla sua altezza).</li>
<li>Matrice omogenea che combina shear orizzontale (q<sub>x</sub>) e verticale (q<sub>y</sub>):</li>
</ul>
<span class="f">Q = [[1, q<sub>x</sub>, 0], [q<sub>y</sub>, 1, 0], [0, 0, 1]]</span>
<p><b>Figura</b> (visionbook, fig. 38.6): il quadrato originale; shear orizzontale (q<sub>x</sub> = 1, q<sub>y</sub> = 0: x′ = x + y, parallelogramma inclinato a destra); verticale (q<sub>x</sub> = 0, q<sub>y</sub> = 1: y′ = x + y); uno shear arbitrario con entrambi i parametri.</p>
<div class="box w"><b>Attenzione: lo shear con entrambi i parametri non conserva l'area</b><p>La slide dice che Q "preserves area". Vale solo per lo shear in una sola direzione: det Q = 1 − q<sub>x</sub>q<sub>y</sub>, che è 1 solo se q<sub>x</sub>q<sub>y</sub> = 0. Con q<sub>x</sub> = q<sub>y</sub> = 0.5 l'area si riduce a 0.75; con q<sub>x</sub> = q<sub>y</sub> = 1 il determinante è 0 e il piano collassa su una retta (verificato con numpy). Il libro (§ 38.3.4) dice solo che le rette restano rette, le parallele restano parallele e gli angoli cambiano.</p></div>
<div class="box b"><b>Dal libro · cap. 38, § 38.3.4 Shearing</b><p>Stessa matrice Q della slide. Nel testo del libro lo spostamento orizzontale è scritto x′ = x + q<sub>y</sub>y, che contraddice la matrice e l'esempio (con q<sub>y</sub> = 0 non ci sarebbe shear): è un refuso del libro, la forma giusta è quella della slide, x′ = x + q<sub>x</sub>y. <a href="https://visionbook.mit.edu/homogeneous_coordinates.html" target="_blank">visionbook.mit.edu/homogeneous_coordinates.html</a></p></div>
""")

s(23, "Summary", """
<p><b>Figura</b> (visionbook, fig. 38.7): riassunto delle trasformazioni 2D, ognuna con il disegno di un quadrato verde trasformato e la sua equazione omogenea [x′, y′, 1]<sup>⊤</sup> = M[x, y, 1]<sup>⊤</sup>:</p>
<ul>
<li><b>Traslazione</b>: [[1, 0, t<sub>x</sub>], [0, 1, t<sub>y</sub>], [0, 0, 1]];</li>
<li><b>Scala</b>: [[s<sub>x</sub>, 0, 0], [0, s<sub>y</sub>, 0], [0, 0, 1]];</li>
<li><b>Rotazione</b>: [[cos θ, −sin θ, 0], [sin θ, cos θ, 0], [0, 0, 1]] (qui nella forma antioraria);</li>
<li><b>Shear</b>: [[1, q<sub>x</sub>, 0], [q<sub>y</sub>, 1, 0], [0, 0, 1]].</li>
</ul>
<p>Da ricordare: lineari (scala, rotazione, shear) nel blocco 2×2, traslazione nella terza colonna, ultima riga [0, 0, 1].</p>
""")

s(24, "Chaining Transformations", """
<ul>
<li>Qualunque sequenza di traslazioni, scale, rotazioni e shear si riduce a <b>una sola matrice 3×3</b>: M = T<sub>n</sub> … T<sub>2</sub>T<sub>1</sub>.</li>
<li><b>L'ordine conta</b>: il prodotto di matrici non è commutativo.</li>
<li>Un solo prodotto per punto, comunque lunga sia la catena.</li>
<li>Ogni famiglia di trasformazioni è un <b>gruppo</b> (chiusa rispetto al prodotto): es. R<sub>θ1</sub>R<sub>θ2</sub> = R<sub>θ1+θ2</sub>.</li>
</ul>
<span class="f">p′ = Q · S · R · T · p   (prima la traslazione, poi rotazione, scala, shear)</span>
<div class="box k"><b>Da saper fare: l'ordine conta</b><p>Origine [0, 0, 1], R = rotazione di 90°, T = traslazione di (1, 0). R·T·p = (0, 1): prima trasli in (1, 0) poi ruoti attorno all'origine. T·R·p = (1, 0): la rotazione lascia ferma l'origine, poi trasli. Altro caso: scala anisotropa e rotazione non commutano, scala uniforme e rotazione sì (verificato con numpy).</p></div>
<div class="box w"><b>Attenzione: "same for every transform" non vale per lo shear generico</b><p>Traslazioni, rotazioni, scale (diagonali) sono gruppi. Le matrici di shear Q(q<sub>x</sub>, q<sub>y</sub>) con entrambi i parametri <b>non</b> lo sono: Q(1, 0)·Q(0, 1) = [[2, 1], [1, 1]], che ha 2 sulla diagonale e non è della forma Q. Sono gruppi gli shear in una sola direzione (Q(a, 0)Q(b, 0) = Q(a + b, 0)) e la famiglia affine nel suo insieme, come dice il libro (§ 38.3.5). Verificato con numpy.</p></div>
""")

s(25, "Chaining: Example", """
<p><b>Rotazione attorno a un punto t diverso dall'origine</b>: R ruota solo attorno all'origine, ma la si ottiene per composizione.</p>
<ol>
<li>traslare di −t (il centro va nell'origine);</li>
<li>ruotare attorno all'origine;</li>
<li>traslare di +t (il centro torna al suo posto).</li>
</ol>
<span class="f">p′ = T<sub>t</sub> R<sub>θ</sub> T<sub>−t</sub> p   (le trasformazioni si applicano da destra a sinistra)</span>
<div class="box k"><b>Da saper fare: un conto completo</b><p>Rotazione di 90° attorno a t = (2, 1). T<sub>t</sub>R<sub>90°</sub>T<sub>−t</sub> = [[0, −1, 3], [1, 0, −1], [0, 0, 1]]. Il centro (2, 1) resta fermo; il punto (3, 1), a distanza 1 a destra del centro, va in (2, 2), a distanza 1 sopra: corretto per una rotazione antioraria (verificato con numpy). In forma chiusa: M = [[R, (I − R)t], [0, 1]].</p></div>
<div class="box b"><b>Dal libro · cap. 38, § 38.3.5 Chaining Transformations</b><p>Il libro scrive la stessa composizione come p′ = T R T<sup>−1</sup> p (con T<sup>−1</sup> la traslazione di −t) e usa il concatenamento per introdurre la gerarchia: <b>euclidee</b> (rotazioni e traslazioni: conservano lunghezze e angoli), <b>similitudini</b> (più scala uniforme: conservano gli angoli), <b>affini</b> (tutto il resto della catena). Ognuna è un gruppo. <a href="https://visionbook.mit.edu/homogeneous_coordinates.html" target="_blank">visionbook.mit.edu/homogeneous_coordinates.html</a></p></div>
""")

s(26, "Generic 2D Transformations", """
<ul>
<li>Tutte le trasformazioni viste formano una <b>trasformazione affine</b> (6 gdl): parte lineare + traslazione, ultima riga fissa [0, 0, 1]:</li>
</ul>
<span class="f">A = [[a, b, c], [d, e, f], [0, 0, 1]]</span>
<ul><li>Conserva il <b>parallelismo</b>.</li></ul>
<ul>
<li><b>Trasformazione proiettiva</b> (omografia, 8 gdl perché definita a meno di scala): matrice 3×3 invertibile qualsiasi:</li>
</ul>
<span class="f">H = [[a, b, c], [d, e, f], [g, h, i]]</span>
<ul><li>Conserva solo la <b>collinearità</b> (le rette restano rette).</li></ul>
<div class="box b"><b>Dal libro · cap. 38, § 38.3.6 Generic 2D Transformations</b><p>Due osservazioni del libro. (1) Con un'affine si può eliminare l'ultima riga e passare direttamente alle cartesiane, ma solo se il punto di ingresso ha 1 come terza componente. (2) La proiettiva generica non cambia se si moltiplica per uno scalare: 9 − 1 = 8 gdl; rispetto all'affine aggiunge le trasformazioni in cui g, h ≠ 0, cioè quelle in cui il denominatore gx + hy + i varia con il punto e le parallele convergono. È l'omografia di L9 (cap. 41). <a href="https://visionbook.mit.edu/homogeneous_coordinates.html" target="_blank">visionbook.mit.edu/homogeneous_coordinates.html</a></p></div>
<div class="box x"><b>Approfondimento: la gerarchia completa</b><p>Traslazione 2 gdl, euclidea 3, similitudine 4, affine 6, proiettiva 8. Più gdl, meno invarianti: lunghezze → angoli → parallelismo → solo rette (e il birapporto). Il numero di corrispondenze minime per stimarle è gdl/2: traslazione 1, euclidea 2 (3 gdl, 1.5 arrotondato per eccesso), similitudine 2, affine 3, proiettiva 4 (L9, scheda 26).</p></div>
""")

s(27, "2D Transformations as Convolutions", """
<ul>
<li>Se l'immagine è una <b>nuvola di punti</b> {[ℓ<sub>i</sub>, x<sub>i</sub>, y<sub>i</sub>]}, una trasformazione geometrica si può vedere come una <b>convoluzione 1D</b> sulla lista delle coordinate.</li>
<li>Per la rotazione i kernel sono w<sub>x</sub> = [cos θ, sin θ] e w<sub>y</sub> = [−sin θ, cos θ]: ogni uscita x′<sub>i</sub>, y′<sub>i</sub> è un prodotto scalare fra (x<sub>i</sub>, y<sub>i</sub>) e un kernel.</li>
<li>I pesi sono gli stessi per tutti i punti, come in ogni convoluzione 1D (condivisione dei pesi).</li>
</ul>
<p><b>Figura</b> (visionbook, fig. 38.8): a sinistra tre colonne di nodi (x, y, ℓ) per ogni punto; i blocchi w<sub>x</sub> e w<sub>y</sub> prendono (x<sub>i</sub>, y<sub>i</sub>) e producono (x′<sub>i</sub>, y′<sub>i</sub>); l'intensità ℓ passa invariata (ℓ′<sub>i</sub> = ℓ<sub>i</sub>).</p>
<div class="box w"><b>Attenzione: i kernel seguono la convenzione oraria del libro</b><p>Con w<sub>x</sub> = [cos θ, sin θ] si ottiene x′ = x cos θ + y sin θ, cioè la prima riga della matrice del libro, che è una rotazione <b>oraria</b> (scheda 19). Con la rotazione antioraria delle slide i kernel sono w<sub>x</sub> = [cos θ, −sin θ], w<sub>y</sub> = [sin θ, cos θ]. Il concetto (kernel 1×2 condiviso da tutti i punti) non cambia.</p></div>
<div class="box b"><b>Dal libro · cap. 38, § 38.3.7 Geometric Transformations as Convolutions</b><p>Il punto del libro: sull'array di pixel solo la traslazione è una convoluzione; rotazione, scala e shear no. Rendendo esplicita la geometria (lista di punti) tutte diventano convoluzioni 1D con kernel di dimensione 1 lungo la lista. Il limite: le uscite non cadono più su una griglia, quindi per convolvere poi le intensità bisogna tornare a un'immagine. È il legame con le reti che lavorano su nuvole di punti. <a href="https://visionbook.mit.edu/homogeneous_coordinates.html" target="_blank">visionbook.mit.edu/homogeneous_coordinates.html</a></p></div>
""")

s(28, "Image Warping", "<p>Applicare una trasformazione a un'immagine vera: dove prendere i valori dei pixel.</p>", kind="div", sec=("l11-warping", "Image warping", "slide 28–34"))

s(29, "Image Warping and Geometric Transforms", """
<ul>
<li><b>Warping</b>: ricampionare un'immagine sotto una trasformazione geometrica M (una delle matrici 3×3 o una mappa non lineare).
<ul><li>Per riavere la solita griglia rettangolare di pixel bisogna calcolare l'intensità nei "buchi".</li></ul></li>
<li>Due strategie:
<ul><li><b>forward mapping</b>: si spingono i pixel della sorgente verso il bersaglio;</li>
<li><b>backward mapping</b>: per ogni pixel del bersaglio si va a prendere il valore nella sorgente.</li></ul></li>
</ul>
<p>Collegamento: è la stessa operazione del passo "warp" dei panorami (L9, L10: <code>cv2.warpPerspective</code> fa backward mapping).</p>
""")

s(30, "Forward Mapping", """
<ul>
<li>Per ogni pixel sorgente (x, y): calcola (x′, y′) = M(x, y) e scrivi il suo valore nel bersaglio in (x′, y′).</li>
<li>Semplice, ma (x′, y′) in generale <b>non è intero</b>: bisogna arrotondare.</li>
</ul>
<p><b>Figura</b> (visionbook, fig. 38.10), metà sinistra: due griglie, sorgente e bersaglio; le frecce colorate partono dai pixel della sorgente e arrivano in punti del bersaglio; un pixel del bersaglio resta senza freccia ed è marcato con "?". A destra il backward mapping: le frecce partono da <b>ogni</b> pixel del bersaglio e tornano nella sorgente.</p>
""")

s(31, "Why Forward Mapping Doesn't Work Well", """
<ul>
<li>Coordinate non intere: arrotondando restano <b>buchi</b> (pixel del bersaglio mai scritti).</li>
<li>Più pixel sorgente possono finire nello stesso pixel bersaglio (<b>sovrapposizione</b>), altri in nessuno (<b>lacune</b>).</li>
<li>Peggio con trasformazioni non rigide, dove la mappa stira alcune zone più di altre (es. scala &gt; 1 o omografie).</li>
</ul>
<p><b>Figura</b>: la stessa fig. 38.10 (scheda 30).</p>
""")

s(32, "Backward Mapping", """
<ul>
<li>Per ogni pixel <b>bersaglio</b> (x′, y′): calcola la posizione sorgente M<sup>−1</sup>(x′, y′) e <b>interpola</b> la sorgente in quel punto.</li>
<li>Ogni pixel bersaglio riceve esattamente un valore: <b>niente buchi</b>.</li>
<li>Serve l'inversa M<sup>−1</sup>, che per le matrici 3×3 si ottiene invertendo la matrice.</li>
</ul>
<p><b>Figura</b>: la stessa fig. 38.10.</p>
<div class="box b"><b>Dal libro · cap. 38, § 38.5 Image Warping</b><p>Il libro chiama il forward mapping "intuitivo ma non una buona idea": produce valori mancanti e aliasing. Il backward mapping evita i buchi, e l'aliasing si evita con un'interpolazione corretta: se l'immagine di arrivo ha densità di pixel minore della sorgente (riduzione), prima si <b>sfoca</b> la sorgente (filtro anti-aliasing, L6), poi si campiona. Interpolazioni consigliate: bilineare, bicubica, Lanczos (rimando al § 21.4.1). <a href="https://visionbook.mit.edu/homogeneous_coordinates.html" target="_blank">visionbook.mit.edu/homogeneous_coordinates.html</a></p></div>
""")

s(33, "Example", """
<p><b>Figura</b> (visionbook, fig. 38.11): la foto dell'orologio (sinistra) ruotata e scalata con le due strategie, entrambe con interpolazione nearest neighbor.</p>
<ul>
<li><b>Forward mapping</b> (centro): l'immagine è punteggiata da una griglia regolare di <b>pixel neri</b>, i buchi mai scritti; i numeri dell'orologio sono frastagliati.</li>
<li><b>Backward mapping</b> (destra): nessun buco, immagine continua; restano solo i bordi a scaletta dovuti al nearest neighbor.</li>
</ul>
<p>Le zone nere agli angoli, in entrambi i casi, sono pixel del bersaglio che cadono fuori dalla sorgente: non sono buchi ma "fuori immagine".</p>
""")

s(34, "High-Quality Warping", """
<ul>
<li>Il nearest neighbor non è l'unica scelta, né la migliore: nearest neighbor (a blocchi), <b>bilineare</b>, kernel di ordine superiore (bicubico, Lanczos).</li>
<li><b>MIP-mapping</b>: usa una <b>piramide multiscala</b> per scegliere il livello giusto da cui interpolare.</li>
</ul>
<div class="box x"><b>Approfondimento: perché la piramide</b><p>Se la trasformazione rimpicciolisce una zona (es. un piano molto inclinato visto in prospettiva), un pixel del bersaglio copre molti pixel della sorgente: interpolare solo dai 4 vicini produce aliasing. Il MIP-mapping (Williams 1983, citato nel § 38.5) precalcola una piramide gaussiana (L6) e per ogni pixel legge dal livello la cui risoluzione corrisponde al fattore di riduzione locale. È il metodo standard delle GPU per le texture.</p></div>
""")

s(35, "Camera Model in Homogeneous Coordinates", "<p>Mondo, camera, pixel: il modello completo in una riga.</p>", kind="div", sec=("l11-modello", "Il modello della camera", "slide 35–38"))

s(36, "Camera Model", """
<p>Non sempre si possono allineare mondo e immagine in modo da avere le equazioni prospettiche semplici:</p>
<ul>
<li>con <b>più camere</b> in posizioni e orientazioni diverse, l'origine può coincidere al massimo con una di esse;</li>
<li>la camera può <b>muoversi</b> nel tempo.</li>
</ul>
<p><b>Figura</b> (visionbook, fig. 39.1): una persona in piedi fotografa una persona seduta a un tavolo. A sinistra il riferimento <b>centrato sulla camera</b> (assi rossi X<sub>c</sub>, Y<sub>c</sub>, Z<sub>c</sub> sulla macchina fotografica, Z<sub>c</sub> verso la scena); a destra un riferimento <b>centrato sul mondo</b> (assi verdi X<sub>w</sub>, Y<sub>w</sub>, Z<sub>w</sub> attaccati al tavolo).</p>
<div class="box b"><b>Dal libro · cap. 39, § 39.1 Introduction</b><p>Nel cap. 5 l'origine era nel foro stenopeico; per interpretare una scena servono altri riferimenti (il pavimento, un oggetto, un'altra camera). Il capitolo si pone tre obiettivi: passare fra coordinate del mondo e della camera, passare fra camere diverse, legare i punti 2D dell'immagine ai punti 3D (calibrazione). Lo strumento per tutti e tre sono le coordinate omogenee. <a href="https://visionbook.mit.edu/imaging_geometry.html" target="_blank">visionbook.mit.edu/imaging_geometry.html</a></p></div>
""")

s(37, "The Pinhole Projection Equations: from World to Camera to Image", """
<ul>
<li>Punto del mondo <b>P</b> = [X, Y, Z]<sup>⊤</sup> (cartesiane) o [X, Y, Z, 1]<sup>⊤</sup> (omogenee).</li>
<li>Pixel <b>p</b> = [x, y]<sup>⊤</sup> (cartesiane) o [x, y, 1]<sup>⊤</sup> (omogenee).</li>
<li>Pipeline completa:
<ol><li>coordinate del <b>mondo</b> (3D, metri);</li>
<li>coordinate della <b>camera</b>, tramite gli estrinseci R, T;</li>
<li>coordinate <b>pixel</b>, tramite gli intrinseci K.</li></ol></li>
</ul>
<p>Il risultato finale è una sola matrice che contiene tutti i parametri:</p>
<span class="f">p = K [R | −RT] P<sub>W</sub></span>
<div class="box w"><b>Attenzione: dimensioni scambiate nella pipeline</b><p>La slide scrive "camera (2D, meters) coordinates in 2D" e "pixel (3D, pixels)". È il contrario: le coordinate della <b>camera</b> sono <b>3D</b> (X<sub>c</sub>, Y<sub>c</sub>, Z<sub>c</sub> in metri: gli estrinseci sono un moto rigido 3D → 3D); le coordinate <b>pixel</b> sono <b>2D</b> (n, m), con 3 componenti solo in omogenee. Il passaggio 3D → 2D avviene con K, che contiene la proiezione prospettica (§ 39.4–39.5, fig. 39.9).</p></div>
""")

s(38, "Intrinsic and Extrinsic Parameters", """
<ul>
<li><b>Intrinseci K</b>: come le coordinate della camera diventano pixel. Dipendono <b>solo dalla camera</b> (ottica e sensore), non dalla sua posizione.</li>
<li><b>Estrinseci R, T</b>: come le coordinate del mondo diventano coordinate della camera. Dipendono <b>solo dalla posa</b> (posizione e orientazione).</li>
<li>Proiezione completa: p = K[R | −RT]P<sub>W</sub>, <b>prima gli estrinseci, poi gli intrinseci</b> (da destra a sinistra).</li>
</ul>
<p>Conseguenza pratica: K si calibra una volta per camera (L12); R, T cambiano a ogni scatto se la camera si muove.</p>
""")

s(39, "3D Camera Projections with Homogeneous Coordinates", "<p>La proiezione prospettica come matrice 3×4, con camera allineata al mondo.</p>", kind="div", sec=("l11-proiezione", "Proiezione in coordinate omogenee", "slide 39–45"))

s(40, "Camera Coordinate Frame: Setup and Conventions", """
<ul>
<li><b>Riferimento della camera</b>:
<ul><li>origine nel <b>centro della camera</b> (il foro);</li>
<li>asse <b>Z lungo l'asse ottico</b>, perpendicolare all'immagine;</li>
<li>la camera guarda verso le <b>Z positive</b>.</li></ul></li>
<li>Il piano immagine (di proiezione) sta a distanza <b>f</b> (focale) lungo Z.</li>
</ul>
<p><b>Figura</b> (visionbook, fig. 39.3 nella versione con persona seduta): a destra la persona seduta con il punto <b>P</b> sulla testa; al centro il centro della camera con gli assi rossi X<sub>c</sub>, Y<sub>c</sub>, Z<sub>c</sub>; a sinistra, dietro il centro, il piano di proiezione con l'immagine <b>capovolta</b> della persona e il punto <b>p</b>. La retta sottile collega P, centro e p.</p>
""")

s(41, "Camera Center and Projection Plane, f", """
<ul>
<li><b>Centro della camera</b>: il foro, dove convergono tutti i raggi di proiezione.</li>
<li>Piano immagine a <b>Z = f</b>.
<ul><li>Nella figura il piano è a Z = −f (dietro il foro, come nella camera fisica) e l'immagine è <b>capovolta</b>.</li>
<li>Calcolando la proiezione sul piano a Z = +f (piano immagine "virtuale", davanti al foro) si ottiene la stessa immagine ma <b>senza ribaltamento</b>.</li></ul></li>
<li>Un punto 3D P = (X, Y, Z) si proietta nell'intersezione fra il piano e il raggio che va dal centro a P.</li>
</ul>
<p><b>Figura</b>: la stessa della scheda 40.</p>
<p>Il piano virtuale è una comodità matematica: geometricamente è il piano fisico ribaltato di 180° attorno all'asse ottico, quindi le formule hanno segni positivi.</p>
""")

s(42, "Simple Case with “Aligned Camera”: Perspective and Similar Triangles", """
<ul>
<li><b>Proiezione prospettica</b>: per un punto (X, Y, Z) i triangoli simili danno</li>
</ul>
<span class="f">x = f X / Z,   y = f Y / Z</span>
<ul>
<li>Sono coordinate sul piano immagine in <b>metri</b>, non in pixel.</li>
<li>La divisione per Z è l'unica parte non lineare.</li>
<li>Sono ancora coordinate cartesiane: ora vanno scritte in omogenee.</li>
</ul>
<p><b>Figura</b>: triangolo con vertice nel foro; il cateto lungo è Z con altezza Y (punto della scena), quello corto è f con altezza y (immagine). La proporzione y : Y = f : Z dà la formula.</p>
<p>Conseguenza: un oggetto due volte più lontano appare grande la metà; X e Z non si possono separare da una sola immagine (ambiguità di scala).</p>
""")

s(43, "Perspective with Homogeneous Coordinates", """
<ul>
<li>Dato un punto P = [X, Y, Z, 1] in omogenee e la focale f;</li>
<li>in cartesiane: x = fX/Z, y = fY/Z;</li>
<li>in omogenee si usa una <b>matrice di proiezione 3×4</b>:</li>
</ul>
<span class="f">K P = [[f, 0, 0, 0], [0, f, 0, 0], [0, 0, 1, 0]] · [X, Y, Z, 1]<sup>⊤</sup> = [fX, fY, Z]<sup>⊤</sup> = λ [x, y, 1]<sup>⊤</sup></span>
<p>Con λ = Z: la profondità diventa il fattore di scala omogeneo, e la divisione si fa solo alla fine.</p>
<div class="box b"><b>Dal libro · cap. 39, § 39.2 3D Camera Projections in Homogeneous Coordinates</b><p>Stessa matrice e stesso passaggio: la proiezione prospettica, non lineare in cartesiane, è un <b>operatore lineare</b> in omogenee. Il libro nota che la quarta colonna (tutta zero) si potrebbe togliere lavorando con [X, Y, Z] cartesiane, ma tenerla permette di comporre con le trasformazioni 4×4 degli estrinseci e di cambiare modello di camera cambiando solo questa matrice. <a href="https://visionbook.mit.edu/imaging_geometry.html" target="_blank">visionbook.mit.edu/imaging_geometry.html</a></p></div>
""")

s(44, "Perspective with Homogeneous Coordinates", """
<p>Verifica che K è la matrice di proiezione: si riporta KP in cartesiane dividendo per la terza componente.</p>
<span class="f">KP = [fX, fY, Z]<sup>⊤</sup> → (fX/Z, fY/Z) = p</span>
<p>p rispetta le equazioni prospettiche x = fX/Z, y = fY/Z.</p>
<div class="box w"><b>Attenzione: refuso nella formula</b><p>Nella slide il vettore cartesiano è scritto (x F/Z, f Y/Z): la prima componente deve essere <b>f X / Z</b> (f minuscola, X maiuscola). È un refuso di battitura; la riga sotto riporta la formula giusta.</p></div>
""")

s(45, "Perspective with Homogeneous Coordinates", """
<p>Poiché le omogenee sono definite a meno di un fattore di scala, la matrice si può <b>riscalare</b> dividendo tutto per f:</p>
<span class="f">K = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1/f, 0]]</span>
<p>KP = [X, Y, Z/f]<sup>⊤</sup> → (fX/Z, fY/Z): stesso punto (verificato con numpy). La quarta colonna resta zero in entrambe le forme.</p>
<div class="box b"><b>Dal libro · cap. 39, § 39.2 e § 39.2.1 Parallel Projection</b><p>Il libro riporta la stessa forma con 1/f. Nel § 39.2.1 mostra che anche la <b>proiezione parallela</b> (ortografica, cap. 5) è una matrice 3×4: K = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]]. Moltiplicando: [X, Y, 1] → (X, Y), cioè si butta via Z. È un esempio di come, cambiando K, si cambia modello di camera senza toccare il resto. <a href="https://visionbook.mit.edu/imaging_geometry.html" target="_blank">visionbook.mit.edu/imaging_geometry.html</a></p></div>
""")

s(46, "Intrinsic Parameters", "<p>Dai metri ai pixel: focale in pixel, punto principale, pixel non quadrati.</p>", kind="div", sec=("l11-intrinseci", "Parametri intrinseci", "slide 46–53"))

s(47, "Image to Sensor", """
<p><b>Figura</b> (visionbook, fig. 39.4): l'asse ottico Z<sub>c</sub> attraversa il centro della camera. Davanti, a destra, una casetta (pareti verdi, tetto rosso) con il punto <b>P</b>; fra la casa e il centro il <b>piano immagine virtuale</b> con gli assi verdi x, y. Dietro il centro, a distanza <b>f</b>, il <b>sensore</b>: una griglia di N × M pixel di larghezza fisica w, su cui la casa appare capovolta.</p>
<p>Il punto della figura: la proiezione dà coordinate in metri sul piano immagine; il sensore le misura in <b>pixel</b>, contati da un angolo della griglia. Servono un cambio di unità (metri → pixel) e una traslazione dell'origine: sono gli <b>intrinseci</b>.</p>
""")

s(48, "Focal Length in Pixels vs. Physical Units", """
<ul>
<li>In unità fisiche: focale <b>f</b> (metri), larghezza del sensore <b>w</b> (metri), larghezza dell'immagine <b>N</b> pixel.</li>
<li><b>N/w</b> = pixel per metro sul sensore.</li>
<li>Focale in pixel:</li>
</ul>
<span class="f">a = f · N / w</span>
<span class="f">K = [[a, 0, 0, 0], [0, a, 0, 0], [0, 0, 1, 0]]</span>
<p>Ora K dà le coordinate 2D in <b>pixel</b> invece che in metri.</p>
<div class="box k"><b>Da saper fare</b><p>iPhone 13 Pro (esempio del libro): f = 5.7 mm, sensore largo 7.6 mm, 4032 pixel: a = 5.7 × 4032 / 7.6 ≈ <b>3024 pixel</b> (verificato). Il valore di a dice quanti pixel occupa un oggetto alto quanto la sua distanza: a = (pixel) × Z / (dimensione).</p></div>
<div class="box b"><b>Dal libro · cap. 39, § 39.3.1 From Meters to Pixels</b><p>Stessa definizione a = fN/w. Il libro introduce subito anche il punto principale (c<sub>x</sub>, c<sub>y</sub>) = (N/2, M/2) per un sensore centrato e la scala b per l'asse verticale, arrivando a K = [[a, 0, c<sub>x</sub>, 0], [0, b, c<sub>y</sub>, 0], [0, 0, 1, 0]] e alle equazioni n = aX/Z + c<sub>x</sub>, m = bY/Z + c<sub>y</sub>. <a href="https://visionbook.mit.edu/imaging_geometry.html" target="_blank">visionbook.mit.edu/imaging_geometry.html</a></p></div>
""")

s(49, "Principal Point", """
<ul>
<li><b>(c<sub>x</sub>, c<sub>y</sub>)</b>: posizione in pixel dove l'asse ottico interseca il sensore (<b>punto principale</b>).
<ul><li>di solito è (circa) al centro dell'immagine;</li>
<li>l'origine dei pixel è invece di solito l'angolo in alto a sinistra;</li>
<li>quindi bisogna <b>traslare</b> le coordinate.</li></ul></li>
<li>Sensore centrato sull'asse ottico: c<sub>x</sub> = N/2, c<sub>y</sub> = M/2 (N larghezza, M altezza in pixel).</li>
</ul>
<span class="f">K = [[a, 0, c<sub>x</sub>, 0], [0, a, c<sub>y</sub>, 0], [0, 0, 1, 0]]</span>
<p><b>Figura</b>: la stessa fig. 39.4 della scheda 47.</p>
<p>Perché la traslazione sta nella terza colonna e non nella quarta: va sommata <b>dopo</b> la divisione per Z, quindi deve essere moltiplicata per Z (la terza componente del punto) prima della divisione: (aX + c<sub>x</sub>Z)/Z = aX/Z + c<sub>x</sub>.</p>
""")

s(50, "Pixel Aspect Ratio: Non-Square Pixels", """
<ul>
<li>Se i pixel non sono quadrati (larghezza e altezza fisica diverse) servono due scale: <b>a ≠ b</b>.</li>
<li>a = fN/w e b = fM/h: differiscono se N/w ≠ M/h (pixel per metro diversi in orizzontale e verticale).</li>
</ul>
<span class="f">K = [[a, 0, c<sub>x</sub>, 0], [0, b, c<sub>y</sub>, 0], [0, 0, 1, 0]]</span>
<p>Nelle camere moderne i pixel sono quasi sempre quadrati e a ≈ b; la calibrazione (L12) li stima comunque separatamente (f<sub>x</sub>, f<sub>y</sub> in OpenCV).</p>
""")

s(51, "Putting It Together: Full Form of K", """
<p>Mappa completa dalla camera ai pixel:</p>
<span class="f">[[a, 0, c<sub>x</sub>, 0], [0, b, c<sub>y</sub>, 0], [0, 0, 1, 0]] · [X, Y, Z, 1]<sup>⊤</sup> → (a X/Z + c<sub>x</sub>,  b Y/Z + c<sub>y</sub>) = (n, m)</span>
<ul><li><b>4 parametri intrinseci</b>: a, b, c<sub>x</sub>, c<sub>y</sub>.</li></ul>
<p><b>Figura</b> (visionbook, fig. 39.5): (a) vista 3D del piano immagine con il punto p e gli assi della camera; (b) "convenzione 1": il riquadro del sensore con origine dei pixel (0, 0) in <b>basso a sinistra</b>, n verso destra, m verso l'alto, e gli assi della camera (verdi) con x che punta a <b>sinistra</b>; (c) "convenzione 2": origine in <b>alto a sinistra</b>, n verso destra, m verso il basso.</p>
<div class="box k"><b>Da saper fare: proiettare un punto</b><p>a = 800, b = 820, c<sub>x</sub> = 320, c<sub>y</sub> = 240, punto in camera (0.2, −0.1, 2): n = 800 · 0.1 + 320 = 400, m = 820 · (−0.05) + 240 = 199 (verificato con numpy). Ordine: prima dividere X e Y per Z, poi scalare, poi sommare il punto principale.</p></div>
<div class="box b"><b>Dal libro · cap. 39, § 39.3.2 From Pixels to Rays</b><p>Il libro fa anche il passo inverso: un punto immagine (x, y) è un punto 3D (x, y, f) sul piano immagine, e tutti i punti λ(x, y, f), λ &gt; 0, si proiettano lì: <b>un pixel corrisponde a un raggio</b>, non a un punto. Se si conosce la profondità Z, P = (Z/f)(x, y, f). In pixel si usa a al posto di f (in forma matriciale è K<sup>−1</sup> applicato a [n, m, 1]). È il motivo per cui da una sola immagine non si ricostruisce il 3D. <a href="https://visionbook.mit.edu/imaging_geometry.html" target="_blank">visionbook.mit.edu/imaging_geometry.html</a></p></div>
""")

s(52, "Sign of a and b", """
<ul>
<li>a e b possono essere <b>negativi</b> se il verso degli assi pixel è opposto a quello degli assi della camera.</li>
<li>Nella convenzione standard (origine in alto a sinistra, convenzione 2) <b>a e b sono entrambi negativi</b>.</li>
<li>Il libro usa la convenzione 1, dove solo <b>a</b> è negativo.</li>
<li>L'asse x del piano immagine virtuale (freccia verde) risulta invertito sul sensore per effetto della proiezione.</li>
</ul>
<p><b>Figura</b>: la stessa fig. 39.5. Nella (b) n cresce verso destra mentre x della camera punta a sinistra (a &lt; 0), m e y crescono entrambi verso l'alto (b &gt; 0); nella (c) anche m cresce verso il basso, opposto a y (b &lt; 0).</p>
<div class="box b"><b>Dal libro · cap. 39, § 39.3.1 (convenzioni di segno)</b><p>Verificato: il libro dice che con l'asse ottico lungo Z e la camera che guarda verso Z positive il segno di a deve essere negativo, e che con indici di array con origine in alto a sinistra (Python, OpenCV) sono negativi sia a sia b. La slide riporta correttamente il libro. <a href="https://visionbook.mit.edu/imaging_geometry.html" target="_blank">visionbook.mit.edu/imaging_geometry.html</a></p></div>
<div class="box x"><b>Approfondimento: perché in OpenCV f<sub>x</sub>, f<sub>y</sub> sono positivi</b><p>Il segno dipende da come si orientano gli assi della <b>camera</b>. OpenCV (e Hartley-Zisserman) sceglie X<sub>c</sub> verso destra e Y<sub>c</sub> verso il <b>basso</b> nell'immagine, con Z<sub>c</sub> in avanti: gli assi della camera hanno lo stesso verso degli indici pixel e f<sub>x</sub>, f<sub>y</sub> sono positivi. Il libro tiene Y<sub>c</sub> verso l'alto e quindi trova segni negativi. Stessa fisica, convenzioni diverse: è la trappola segnalata nella scheda 73.</p></div>
""")

s(53, "Other Camera Parameters", """
<p>Complicazioni ignorate finora:</p>
<ul>
<li>i pixel possono essere disposti lungo assi <b>non perpendicolari</b>: serve un parametro di <b>skew</b> (in K compare un termine s in posizione (1, 2));</li>
<li>la <b>distorsione radiale</b> delle lenti fa apparire curve le rette (a barile o a cuscinetto): non è lineare, non entra in K;</li>
<li>gli strumenti standard di calibrazione modellano tutti questi effetti insieme (documentazione OpenCV, modulo calib).</li>
</ul>
<div class="box b"><b>Dal libro · cap. 39, § 39.3.4 Other Camera Parameters</b><p>Il libro cita gli stessi due effetti (skew per pixel non quadrati o assi non ortogonali, distorsione radiale come fonte frequente di errore da correggere) e rimanda a Zhang (2000) per il metodo di calibrazione che li stima: è il metodo multipiano con la scacchiera della L12. <a href="https://visionbook.mit.edu/imaging_geometry.html" target="_blank">visionbook.mit.edu/imaging_geometry.html</a></p></div>
""")

s(54, "Simple, Unreliable Calibration", "<p>Stimare la focale in pixel con un righello e una scacchiera.</p>", kind="div", sec=("l11-calibrazione", "Una calibrazione semplice", "slide 54–58"))

s(55, "Simple, Unreliable Calibration", """
<p><b>Figure</b> (visionbook, fig. 39.7):</p>
<ul>
<li>(a) un iPhone tenuto in mano, appoggiato a un <b>righello</b> che arriva fino a una scacchiera stampata e incollata su un cartone, fissata a una parete: la distanza camera-scacchiera si legge sul righello;</li>
<li>(b) la foto scattata, in formato <b>verticale</b>: la scacchiera vista frontalmente (piano della camera parallelo alla scacchiera), con l'etichetta "7x9 checkerboard for camera calibration. Squares are: 20x20 mm"; la scacchiera ha 10 colonne di quadretti da 2 cm, quindi è larga 20 cm.</li>
</ul>
<p>L'idea: se si conoscono dimensione reale, distanza e dimensione in pixel di un oggetto, la proiezione prospettica dà la focale in pixel.</p>
""")

s(56, "Calibration: Setup", """
<ul>
<li>Oggetto di dimensione nota: la scacchiera, larghezza <b>W = 20 cm</b>.</li>
<li>Distanza nota camera-oggetto: <b>Z = 31 cm</b>.</li>
<li>Foto dell'oggetto: la scacchiera è larga <b>L = 2002 pixel</b>.</li>
</ul>
<p><b>Figura</b>: la foto del setup (righello, telefono, scacchiera), come nella scheda 55.</p>
<p>Ipotesi implicite: scacchiera parallela al sensore (tutti i suoi punti alla stessa Z), distanza misurata dal centro ottico, nessuna distorsione.</p>
""")

s(57, "Calibration: Estimation", """
<ul>
<li>Dalla proiezione prospettica in pixel, L = a W / Z, quindi</li>
</ul>
<span class="f">a = Z · L / W = 31 × 2002 / 20 = 3103.1 pixel</span>
<ul>
<li>Foto di 4032 × 3024 pixel; la slide (come il libro) pone c<sub>x</sub> = 3024/2 = 1512 e c<sub>y</sub> = 4032/2 = 2016:</li>
</ul>
<span class="f">K = [[3103.1, 0, 1512, 0], [0, 3103.1, 2016, 0], [0, 0, 1, 0]]</span>
<p><b>Figura</b>: la foto del setup.</p>
<div class="box w"><b>Attenzione: refuso nella K della slide</b><p>Nella slide l'elemento (2, 2) di K è scritto <b>30103.1</b>: deve essere <b>3103.1</b> (pixel quadrati, a = b; nel libro, eq. 39.7, è 3103.1). Anche "bold (K)" in testa è un residuo di formattazione: si legge semplicemente <b>K</b>.</p></div>
<div class="box k"><b>Da saper fare: c<sub>x</sub>, c<sub>y</sub> e l'orientamento della foto</b><p>c<sub>x</sub> = metà della <b>larghezza</b>, c<sub>y</sub> = metà dell'<b>altezza</b>. Con una foto orizzontale 4032 × 3024 sarebbe c<sub>x</sub> = 2016, c<sub>y</sub> = 1512. La foto della scacchiera (fig. 39.7b) però è <b>verticale</b>: larga 3024 e alta 4032, quindi c<sub>x</sub> = 1512 e c<sub>y</sub> = 2016 sono corretti. Controprova: la scacchiera occupa circa due terzi della larghezza della foto, e 2002/3024 ≈ 0.66 (con 4032 sarebbe 0.50). La dicitura "4032 × 3024" va letta come risoluzione nominale del sensore, non come larghezza × altezza della foto.</p></div>
<div class="box b"><b>Dal libro · cap. 39, § 39.3.3 A Simple, although Unreliable, Calibration Method</b><p>Stessi numeri del libro: scacchiera stampata con quadretti di 2 cm, larghezza 20 cm, distanza misurata col righello ≈ 31 cm, 2002 pixel, a = 3103.1, foto 4032 × 3024 dell'obiettivo grandangolare di un iPhone 13 Pro. Il libro presenta il metodo come un <b>controllo di plausibilità</b>, non come una calibrazione vera: dipende da una misura col righello, dal parallelismo esatto e ignora distorsioni. <a href="https://visionbook.mit.edu/imaging_geometry.html" target="_blank">visionbook.mit.edu/imaging_geometry.html</a></p></div>
""")

s(58, "Calibration: Accuracy", """
<p>Quanto è accurato il metodo?</p>
<ul>
<li>a stimato = <b>3103.1</b>;</li>
<li>a corretto = <b>3024</b> (dalle specifiche hardware: 5.7 mm × 4032 / 7.6 mm).</li>
</ul>
<p>Errore relativo ≈ <b>2.6%</b> (verificato). Con a = 3024, a 31 cm la scacchiera dovrebbe misurare 3024 × 20/31 ≈ 1951 pixel invece di 2002: basta un errore di circa 8 mm sulla distanza (ad esempio misurarla dal bordo del telefono invece che dal centro ottico) per spiegare la differenza.</p>
<p><b>Nota</b>: calibrando così non serve conoscere i parametri hardware, che sono spesso difficili da trovare, alterati dall'elaborazione interna della camera (ritaglio, stabilizzazione, correzione delle distorsioni) e vanno comunque verificati.</p>
<div class="box x"><b>Approfondimento: perché "unreliable"</b><p>Il metodo stima un solo parametro (a) con una sola misura, assume c<sub>x</sub>, c<sub>y</sub> al centro, nessuno skew, nessuna distorsione e scacchiera perfettamente frontale. La calibrazione vera (L12) usa molte immagini della scacchiera in pose diverse, stima insieme K, distorsione e posa di ogni immagine, e minimizza l'errore di riproiezione su centinaia di angoli.</p></div>
""")

s(59, "Extrinsic Parameters", "<p>Dove si trova la camera e come è orientata rispetto al mondo.</p>", kind="div", sec=("l11-estrinseci", "Parametri estrinseci", "slide 59–68"))

s(60, "World Coordinate Frame vs. Camera Coordinate Frame", """
<p>Finora due grandi semplificazioni:</p>
<ul>
<li>origine della camera = origine del mondo;</li>
<li>asse ottico allineato a un asse del mondo.</li>
</ul>
<p>Ora le si rimuove. (Prima di una serie di build della stessa slide.)</p>
""", printed=' <em>· pag. 59/72</em>')

s(61, "World Coordinate Frame vs. Camera Coordinate Frame", """
<p>Rispetto alla precedente aggiunge i due riferimenti separati:</p>
<ul>
<li><b>Riferimento del mondo</b>: fisso, legato alla scena, <b>condiviso</b> da tutte le camere e le viste.</li>
<li><b>Riferimento della camera</b>: origine nel centro della camera, assi allineati all'asse ottico.</li>
<li>I <b>parametri estrinseci</b> descrivono la trasformazione <b>rigida</b> che porta le coordinate del mondo in quelle della camera.</li>
</ul>
<p><b>Figura</b> (visionbook, fig. 39.8): la persona con la camera (assi rossi X<sub>c</sub>, Y<sub>c</sub>, Z<sub>c</sub>, con la freccia curva <b>R</b>) e il tavolo con la persona seduta; gli assi verdi del mondo X<sub>w</sub>, Y<sub>w</sub>, Z<sub>w</sub> in basso a destra. Il punto P sulla testa della persona seduta è raggiunto da due vettori: <b>P<sub>w</sub></b> dall'origine del mondo e <b>P<sub>c</sub></b> dalla camera; il vettore <b>T</b> va dall'origine del mondo alla camera.</p>
""", printed=' <em>· pag. 59/72</em>')

s(62, "Transformation Parameters", """
<p>Mondo (verde) e camera (rosso) sono legati da:</p>
<ul>
<li>una <b>traslazione T</b>: il vettore che va dall'origine del mondo al centro della camera, cioè la <b>posizione della camera</b> in coordinate del mondo;</li>
<li>una <b>rotazione</b>: gli assi della camera sono ruotati di <b>R<sup>⊤</sup></b> rispetto a quelli del mondo, quindi R è la rotazione che porta le coordinate dal mondo alla camera;</li>
<li>prima di applicare gli intrinseci bisogna esprimere i punti del mondo nel riferimento della camera.</li>
</ul>
<p><b>Figura</b>: la stessa fig. 39.8.</p>
<div class="box k"><b>Da saper spiegare: perché R<sup>⊤</sup> e non R</b><p>Se gli <b>assi</b> della camera sono quelli del mondo ruotati di R<sub>c</sub>, le <b>coordinate</b> di un punto fisso cambiano con la rotazione inversa R<sub>c</sub><sup>−1</sup> = R<sub>c</sub><sup>⊤</sup>. Il libro chiama R direttamente la matrice che agisce sulle coordinate (mondo → camera), così gli assi della camera risultano ruotati di R<sup>⊤</sup>: scelta fatta "per semplificare le derivazioni" (§ 39.4). Le righe di R sono gli assi della camera espressi nel mondo.</p></div>
""", printed=' <em>· pag. 60/72</em>')

s(63, "World Coordinate Frame vs. Camera Coordinate Frame", """
<p><b>Come si porta un punto P<sub>W</sub> dal mondo alla camera?</b></p>
<ul>
<li>P<sub>W</sub> è espresso negli assi verdi (mondo);</li>
<li>si <b>trasla di −T</b>, così le due origini coincidono;</li>
<li>si <b>ruota di R</b>.</li>
</ul>
<p><b>Figura</b>: la stessa fig. 39.8. (Prima build di questa slide.)</p>
""", printed=' <em>· pag. 61/72</em>')

s(64, "World Coordinate Frame vs. Camera Coordinate Frame", """
<p>Aggiunge la formula in cartesiane:</p>
<span class="f">P<sub>c</sub> = R (P<sub>W</sub> − T) = R P<sub>W</sub> − R T</span>
<p>Controllo: il centro della camera P<sub>W</sub> = T va in P<sub>c</sub> = 0, l'origine del riferimento camera (verificato con numpy).</p>
""", printed=' <em>· pag. 61/72</em>')

s(65, "World Coordinate Frame vs. Camera Coordinate Frame", """
<p>Aggiunge cosa si ottiene dopo i due passi:</p>
<ul>
<li>stessa <b>origine</b> (centro della camera);</li>
<li><b>asse Z allineato</b> all'asse ottico (e anche X, Y allineati agli assi del sensore);</li>
<li>ora si possono applicare gli intrinseci e ottenere i pixel: siamo tornati al caso "camera allineata" delle schede 42–51.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 39, § 39.4 Camera-Extrinsic Parameters</b><p>Il libro costruisce la camera così: la si mette nell'origine del mondo, si ruotano i suoi assi di R<sup>⊤</sup>, poi la si sposta di T; l'ordine conta. Per portare un punto dal mondo alla camera si fa il percorso inverso in ordine inverso: prima −T, poi R, da cui P<sub>C</sub> = R(P<sub>W</sub> − T). T è esplicitamente "la posizione della camera in coordinate del mondo". R e T si chiamano estrinseci perché sono "esterni" alla camera: cambiano spostandola, non cambiando ottica. <a href="https://visionbook.mit.edu/imaging_geometry.html" target="_blank">visionbook.mit.edu/imaging_geometry.html</a></p></div>
""", printed=' <em>· pag. 61/72</em>')

s(66, "Homogeneous Coordinates", """
<p>Gli stessi due passi come matrici 4×4 in omogenee 3D:</p>
<span class="f">M<sub>1</sub> = [[1, 0, 0, −T<sub>X</sub>], [0, 1, 0, −T<sub>Y</sub>], [0, 0, 1, −T<sub>Z</sub>], [0, 0, 0, 1]]   (traslazione di −T)</span>
<span class="f">M<sub>2</sub> = [[R<sub>1</sub>, R<sub>2</sub>, R<sub>3</sub>, 0], [R<sub>4</sub>, R<sub>5</sub>, R<sub>6</sub>, 0], [R<sub>7</sub>, R<sub>8</sub>, R<sub>9</sub>, 0], [0, 0, 0, 1]]   (rotazione R)</span>
<p>Trasformazione completa, <b>prima trasla poi ruota</b>:</p>
<span class="f">P<sub>C</sub> = M<sub>2</sub> M<sub>1</sub> P<sub>W</sub></span>
<p>È la versione 3D delle matrici 3×3 delle schede 14 e 18: una riga e una colonna in più.</p>
""", printed=' <em>· pag. 62/72</em>')

s(67, "Homogeneous Coordinates", """
<p>Aggiunge il prodotto esplicito:</p>
<span class="f">M<sub>2</sub>M<sub>1</sub> = [[R<sub>1</sub>, R<sub>2</sub>, R<sub>3</sub>, −r<sub>1</sub>T], [R<sub>4</sub>, R<sub>5</sub>, R<sub>6</sub>, −r<sub>2</sub>T], [R<sub>7</sub>, R<sub>8</sub>, R<sub>9</sub>, −r<sub>3</sub>T], [0, 0, 0, 1]] = [[R, −RT], [0<sup>⊤</sup>, 1]]</span>
<p>r<sub>i</sub> è la riga i di R, quindi −r<sub>i</sub>T è la componente i di −RT.</p>
<div class="box k"><b>Da saper fare: il prodotto a blocchi</b><p>[[R, 0], [0<sup>⊤</sup>, 1]] · [[I, −T], [0<sup>⊤</sup>, 1]] = [[R·I + 0·0<sup>⊤</sup>, R(−T) + 0·1], [0<sup>⊤</sup>, 1]] = [[R, −RT], [0<sup>⊤</sup>, 1]]. Verificato con numpy su una R casuale e T = (1, 2, 3): l'ultima colonna coincide con −RT. Nell'ordine opposto (prima ruotare, poi traslare) si otterrebbe [[R, −T], [0<sup>⊤</sup>, 1]], un'altra trasformazione.</p></div>
<div class="box x"><b>Approfondimento: quanti gradi di libertà ha R</b><p>R ha 9 entrate ma è ortogonale con det = 1: R<sup>⊤</sup>R = I impone 6 vincoli (3 norme unitarie, 3 ortogonalità), restano <b>3 gdl</b> (ad esempio tre angoli, o un asse e un angolo). Per questo nella scheda 71 la rotazione conta 3 e non 9. In OpenCV si rappresenta con il vettore di Rodrigues a 3 componenti (<code>rvec</code>).</p></div>
""", printed=' <em>· pag. 63/72</em>')

s(68, "Summary", """
<p><b>Parametri estrinseci</b>: rotazione R e traslazione T.</p>
<span class="f">P<sub>C</sub> = [[R, −RT], [0<sup>⊤</sup>, 1]] P<sub>W</sub></span>
<p>Notazione alternativa diffusa (OpenCV, Hartley-Zisserman): <b>t = −RT</b>, così P<sub>C</sub> = RP<sub>W</sub> + t e la matrice si scrive [R | t]. Attenzione: t non è la posizione della camera; la posizione è T = −R<sup>⊤</sup>t. Il libro e le slide usano sempre T e −RT.</p>
""", printed=' <em>· pag. 64/72</em>')

s(69, "The Full Camera Matrix", "<p>Intrinseci ed estrinseci in una sola matrice 3×4.</p>", kind="div", sec=("l11-matrice", "La matrice completa", "slide 69–71"))

s(70, "Combining Intrinsic and Extrinsic Parameters", """
<span class="f">(x, y) → λ [x, y, 1]<sup>⊤</sup> = [x′, y′, w]<sup>⊤</sup> = K M<sub>2</sub> M<sub>1</sub> [X, Y, Z, 1]<sup>⊤</sup></span>
<ul>
<li>Applicazione da destra a sinistra: <b>prima gli estrinseci, poi gli intrinseci</b>.</li>
<li>Per tornare in cartesiane si divide per w: (x, y) = (x′/w, y′/w).</li>
</ul>
<p>Forma abituale:</p>
<span class="f">p = K [R | −RT] P<sub>W</sub></span>
<p>Dimensioni: K (3×3, dopo aver tolto la colonna di zeri) × [R | −RT] (3×4) × P<sub>W</sub> (4×1) = p (3×1, omogeneo). La matrice M = K[R | −RT] è 3×4 e ha rango 3.</p>
<div class="box b"><b>Dal libro · cap. 39, § 39.5 Full Camera Model</b><p>Il libro scrive prima la forma con K 3×4 (colonna di zeri) per due matrici 4×4, poi nota che, proprio per quella colonna di zeri, si può eliminare la coordinata omogenea del punto camera: K diventa 3×3 e la catena diventa K · R · [I | −T], cioè K[R | −RT]. Chiama la matrice completa <b>M</b> (eq. 39.14). Osserva infine che cambiando K si ottengono altri modelli (ortografico, prospettiva debole, camera affine). <a href="https://visionbook.mit.edu/imaging_geometry.html" target="_blank">visionbook.mit.edu/imaging_geometry.html</a></p></div>
<div class="box k"><b>Da saper fare: proiettare un punto del mondo</b><p>1) P<sub>c</sub> = R(P<sub>W</sub> − T); 2) se Z<sub>c</sub> ≤ 0 il punto è dietro la camera; 3) (n, m) = (a X<sub>c</sub>/Z<sub>c</sub> + c<sub>x</sub>, b Y<sub>c</sub>/Z<sub>c</sub> + c<sub>y</sub>). Oppure in un colpo solo: p̃ = K[R | −RT][X, Y, Z, 1]<sup>⊤</sup> e divisione per la terza componente. Le due strade danno lo stesso risultato (verificato con numpy).</p></div>
""", printed=' <em>· pag. 66/72</em>')

s(71, "Degrees of Freedom of P", """
<ul>
<li><b>Intrinseci</b>: a, b, c<sub>x</sub>, c<sub>y</sub> → 4 (spesso c'è anche lo skew: 5).</li>
<li><b>Estrinseci</b>: 3 (rotazione) + 3 (traslazione) = 6.</li>
<li><b>Totale</b>: la matrice 3×4 è definita a meno di scala, quindi ha 12 − 1 = <b>11 gradi di libertà</b>.</li>
</ul>
<div class="box k"><b>Da saper fare: far tornare i conti</b><p>5 intrinseci (con skew) + 6 estrinseci = <b>11</b>, esattamente i gdl di una 3×4 generica a meno di scala: ogni matrice 3×4 con il blocco 3×3 sinistro invertibile si scompone in K[R | −RT] (decomposizione RQ, L12). Senza skew i parametri fisici sono 10: la 3×4 generica è un po' più generale del modello a 4 intrinseci. Per la stima: ogni corrispondenza 3D–2D dà 2 equazioni, quindi servono almeno 6 punti (11/2 = 5.5) non complanari (L12).</p></div>
""", printed=' <em>· pag. 67/72</em>')

s(72, "Conclusions", "<p>Trappole, idee chiave, riferimenti, prossima lezione.</p>", kind="div", sec=("l11-conclusioni", "Conclusioni", "slide 72–76"))

s(73, "Common Pitfalls", """
<ul>
<li>Pensare sempre <b>esplicitamente</b> ai sistemi di coordinate: mondo, camera, immagine (metri), pixel.</li>
<li>Attenzione all'<b>ordine</b> delle operazioni: le matrici si applicano da destra a sinistra e non commutano.</li>
<li>Attenzione agli <b>assi invertiti</b> e ai cambi di segno (es. dalla camera all'immagine, y verso l'alto o verso il basso).</li>
</ul>
<p>Esempi visti in questa lezione: la rotazione "antioraria" del libro che è oraria (scheda 19), i segni di a e b (scheda 52), R contro R<sup>⊤</sup> negli estrinseci (scheda 62), T contro t = −RT (scheda 68).</p>
""", printed=' <em>· pag. 69/72</em>')

s(74, "Key Takeaways", """
<ul>
<li>Le <b>coordinate omogenee</b> trasformano proiezione, traslazione e le altre trasformazioni in un'unica moltiplicazione di matrici.</li>
<li>Modello della camera <b>p = K[R | −RT]P<sub>W</sub></b>, separato in parametri <b>intrinseci</b> (K: la camera) ed <b>estrinseci</b> (R, T: la posa).</li>
</ul>
""", printed=' <em>· pag. 70/72</em>')

s(75, "References", """
<ul>
<li>MIT Vision Book, cap. 38: <i>Representing Images and Geometry</i> (<a href="https://visionbook.mit.edu/homogeneous_coordinates.html" target="_blank">link</a>).</li>
<li>MIT Vision Book, cap. 39: <i>Camera Modeling and Calibration</i> (<a href="https://visionbook.mit.edu/imaging_geometry.html" target="_blank">link</a>), per questa lezione § 39.1–39.5.</li>
</ul>
<p>Per approfondire: Hartley e Zisserman, <i>Multiple View Geometry</i>, cap. 6 (modelli di camera); Szeliski 2a ed., § 2.1 (primitive e trasformazioni geometriche, proiezioni 3D → 2D).</p>
""", printed=' <em>· pag. 71/72</em>')

s(76, "Next Lecture", """
<ul>
<li>Stimare K, R, T (e i coefficienti di distorsione) da immagini reali.</li>
<li>Calibrazione con la <b>DLT</b> (Direct Linear Transform) da corrispondenze 3D–2D.</li>
<li>Calibrazione <b>multipiano</b> con una scacchiera (metodo di Zhang).</li>
<li>Minimizzazione dell'<b>errore di riproiezione</b>:</li>
</ul>
<span class="f">∑<sub>i</sub> ‖p<sub>i</sub> − π(K[R | −RT]P<sub>i</sub>)‖²</span>
<p>π è la divisione prospettica (da omogenee a cartesiane). Capitolo del libro: 39, § 39.6–39.8.</p>
""", printed=' <em>· pag. 72/72</em>')
