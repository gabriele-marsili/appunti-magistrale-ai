
s(1, "Copertina", """
<p><b>Keypoint Detection</b>. Ottava lezione.</p>
<p>Si passa dal trattamento dell'immagine intera (filtri, piramidi) alla ricerca di <b>pochi punti speciali</b> che si possano ritrovare in immagini diverse della stessa scena.</p>
<p>Servono quasi tutti gli strumenti visti finora: gradienti e derivate di gaussiana (L5), laplaciano e LoG (L5), scale-space e piramidi (L6).</p>
""")

s(2, "Motivation", "<p>Perché cercare punti corrispondenti fra immagini.</p>", kind="div", sec=("l8-motivazione", "Motivazione", "slide 2–10"))

s(3, "Goal of the Day", """
<ul>
<li>Obiettivo: ritrovare lo <b>stesso punto fisico</b> in immagini diverse di una scena.</li>
<li>Due sotto-problemi:
<ul><li><b>Detection</b>: dove sono i punti "buoni"?</li>
<li><b>Description</b>: come si distinguono fra loro, così da poterli accoppiare?</li></ul></li>
</ul>
<p>Questa lezione tratta soprattutto la detection (Harris, DoG) e chiude con il descrittore di SIFT. Il matching vero e proprio è nella lezione successiva.</p>
""")

s(4, "Matching and Correspondence", """
<p><b>Figura</b> (da Szeliski): due coppie di foto della stessa scena. Sopra una montagna innevata ripresa da due punti leggermente diversi; sotto una casetta di legno fotografata da due angolazioni molto diverse.</p>
<p>Domande della slide: quali feature permettono di riconoscere le corrispondenze, e perché è difficile?</p>
<ul>
<li>Nella coppia in alto basta una piccola traslazione: molte zone sono quasi identiche.</li>
<li>Nella coppia in basso cambiano prospettiva, scala apparente e illuminazione: confrontare i pixel direttamente non funziona.</li>
</ul>
""")

s(5, "The Correspondence Problem", """
<p><b>Problema della corrispondenza</b>: date due (o più) immagini della stessa scena, trovare coppie di pixel (p<sub>1</sub>, p<sub>2</sub>) che sono proiezioni dello <b>stesso punto 3D</b>.</p>
<p>È difficile per:</p>
<ul>
<li>cambio di punto di vista (distorsione prospettica);</li>
<li>cambio di scala (zoom, distanza);</li>
<li>cambio di illuminazione;</li>
<li>occlusioni e rumore.</li>
</ul>
<p><b>Approccio</b>: invece di accoppiare ogni pixel, si sceglie un insieme <b>sparso</b> di <b>keypoint distintivi</b> e si accoppiano solo quelli.</p>
<div class="box k"><b>Da saper spiegare</b><p>Perché sparso: la maggior parte dei pixel (cielo, muri, bordi rettilinei) è ambigua e non si può accoppiare in modo affidabile; pochi punti buoni bastano per stimare una trasformazione geometrica (un'omografia ha 8 gradi di libertà: servono 4 corrispondenze).</p></div>
""")

s(6, "Correspondence Is the Unifying Problem", """
<p>Molti task diversi si riducono alle corrispondenze:</p>
<ul>
<li><b>Image stitching / panorami</b>: allineare immagini sovrapposte tramite punti corrispondenti.</li>
<li><b>Structure from Motion (SfM)</b>: ricostruire struttura 3D e pose delle camere dalle corrispondenze fra molte viste.</li>
<li><b>Tracking</b>: seguire lo stesso punto nei frame di un video.</li>
<li><b>Stereo / stima della profondità</b>: accoppiare punti fra due camere calibrate.</li>
</ul>
<p>Schema comune: <b>rilevare</b> punti ripetibili, <b>descriverli</b>, <b>accoppiarli</b> in modo affidabile.</p>
""")

s(7, "Recap: Invariance and Equivariance", """
<p>Per keypoint stabili servono invarianza o equivarianza:</p>
<ul>
<li><b>Equivarianza</b>: le posizioni rilevate si trasformano insieme all'immagine (se ruoto l'immagine, i punti ruotano con lei).</li>
<li><b>Invarianza</b>: il valore del descrittore resta stabile dopo una normalizzazione.</li>
</ul>
<p>Strumenti già noti:</p>
<ul>
<li><b>scala</b>: rappresentazioni multiscala (L6);</li>
<li><b>traslazione</b>: sistemi LSI, cioè convoluzioni (L3): convolvere e poi traslare = traslare e poi convolvere;</li>
<li><b>orientazione</b>: nuovo, si vede oggi con SIFT.</li>
</ul>
<p>Nota della slide: il descrittore deve essere invariante/equivariante.</p>
""")

s(8, "Components", """
<p><b>Detector</b></p>
<ul><li>trova le posizioni dei keypoint (e, se serve, scala e orientazione);</li>
<li>esempi: Harris, estremi della DoG;</li>
<li>deve essere <b>equivariante</b> ai cambi di vista.</li></ul>
<p><b>Descriptor</b></p>
<ul><li>codifica in un vettore l'aspetto locale intorno al keypoint;</li>
<li>esempio: l'istogramma a 128 dimensioni di SIFT;</li>
<li>deve essere <b>invariante</b> ai cambi di vista.</li></ul>
<p><b>Classici vs appresi</b></p>
<ul><li>fatti a mano: Harris, SIFT;</li><li>appresi: SuperPoint (detector + descrittore), LightGlue (matcher).</li></ul>
<div class="box k"><b>La distinzione da ricordare</b><p>Detector equivariante (il punto si sposta con l'immagine), descrittore invariante (il vettore non cambia). È la coppia di concetti che torna in tutta la lezione.</p></div>
""")

s(9, "Outline", """
<ol>
<li>Cos'è un keypoint</li>
<li>Corner detection (Harris)</li>
<li>Blob detection (base di SIFT)</li>
<li>Invarianza di scala e scale-space</li>
<li>SIFT: detection e localizzazione</li>
<li>SIFT: orientazione e descrittore</li>
</ol>
""")

s(10, "Example: SIFT", """
<p><b>Figura</b> (opencv.org): foto in bianco e nero di un edificio con torri, con sovrapposti molti cerchi colorati. Ogni cerchio è un keypoint SIFT: il <b>raggio</b> indica la scala, il <b>segmento</b> dal centro l'orientazione.</p>
<ul>
<li>I keypoint si concentrano sulle decorazioni e sugli spigoli dell'edificio, ricchi di struttura.</li>
<li>Il cielo uniforme ne ha pochissimi (qualche uccello, qualche bordo di nuvola).</li>
<li>Ci sono cerchi piccoli e grandi: SIFT rileva strutture a scale diverse.</li>
</ul>
""")

s(11, "What is a Keypoint", "<p>Quali proprietà deve avere un punto per essere utile.</p>", kind="div", sec=("l8-keypoint", "Cos'è un keypoint", "slide 11–18"))

s(12, "What Makes a Good Keypoint: an Overview", """
<ul>
<li><b>Ripetibile</b>: viene rilevato anche con viste e condizioni diverse.</li>
<li><b>Invariante</b>: a scala, rotazione, illuminazione e (idealmente) a un certo cambio di punto di vista.</li>
<li><b>Locale</b>: definito da un piccolo intorno, quindi robusto a occlusioni e disordine altrove.</li>
<li><b>Distintivo</b>: l'aspetto locale basta a distinguerlo dagli altri punti.</li>
<li><b>Efficiente</b>: detection e descrizione abbastanza economiche da farle su molti punti e molte immagini.</li>
</ul>
""")

s(13, "Repeatability: Detecting the Same Point Under Different Views", """
<ul>
<li><b>Ripetibilità</b>: se lo stesso punto fisico è visibile in due immagini, il detector scatta nel pixel corrispondente in entrambe?</li>
<li>È il <b>primo</b> requisito: un punto perfettamente distintivo ma non riproducibile non serve a niente per le corrispondenze.</li>
<li><b>Zone piatte e bordi rettilinei</b> non danno detection ripetibili: molte posizioni vicine sono identiche (ambiguità 2D nelle zone piatte, 1D lungo i bordi), quindi rumore o piccoli cambi di vista spostano il punto "migliore".</li>
</ul>
""")

s(14, "Example", """
<p><b>Figura</b> (Szeliski): la coppia di foto della montagna con tre riquadri rossi nelle stesse posizioni; sotto, gli ingrandimenti delle tre patch in ciascuna immagine.</p>
<ul>
<li>Patch nel <b>cielo</b>: uniforme, si potrebbe accoppiare con qualunque altra patch di cielo.</li>
<li>Patch sul <b>bordo</b> fra neve e cielo: si localizza solo perpendicolarmente al bordo, lungo il bordo scivola.</li>
<li>Patch su una <b>punta di roccia</b> (angolo): ha struttura in due direzioni, si ritrova in un solo posto.</li>
</ul>
<p>È l'intuizione che Harris rende quantitativa (slide 20 e seguenti).</p>
""")

s(15, "Example", """
<p><b>Figura</b> (Szeliski): (a) un'immagine con un albero, una casa e un'aiuola, con tre croci rosse; sotto, per ciascuna croce, la superficie di <b>autocorrelazione</b> come immagine e come grafico 3D.</p>
<ul>
<li>(b) <b>aiuola</b>: un minimo netto e isolato, la patch è ben localizzata.</li>
<li>(c) <b>bordo del tetto</b>: una valle allungata, ambiguità lungo il bordo (aperture problem).</li>
<li>(d) <b>nuvola</b>: superficie piatta e irregolare, nessun minimo chiaro.</li>
</ul>
<p>L'autocorrelazione verrà definita alla slide 25: è l'errore che si fa confrontando la patch con una copia di sé spostata di Δu.</p>
""")

s(16, "Example", """
<p><b>Figura</b>: una staccionata bianca con tante assi uguali.</p>
<p>Punto della slide: un punto può essere <b>localmente stabile</b> (la punta di un'asse è un buon angolo) ma <b>non avere match stabili</b>, perché ci sono tanti punti simili nell'immagine. La distintività è una proprietà globale, non solo locale.</p>
<p>Problema tipico delle <b>texture ripetitive</b> (finestre di un palazzo, piastrelle); nel matching si gestisce con il ratio test di Lowe (lezione successiva).</p>
""")

s(17, "Invariance to Scale, Rotation, Illumination", """
<ul>
<li><b>Scala</b>: lo stesso oggetto a distanze o zoom diversi ha dimensioni diverse; detector e descrittore devono essere stabili ai cambi di scala.</li>
<li><b>Rotazione</b>: una rotazione della camera nel piano ruota le patch; il descrittore deve essere invariante alla rotazione, oppure si calcola un'<b>orientazione di riferimento</b> rispetto a cui normalizzare (è la scelta di SIFT).</li>
<li><b>Illuminazione</b>: la luce sposta (offset) e scala (guadagno) le intensità; i gradienti, opportunamente normalizzati, restano abbastanza stabili.</li>
</ul>
""")

s(18, "Locality vs. Distinctiveness", """
<ul>
<li><b>Località</b>: una regione di supporto piccola è più robusta a occlusioni e sfondo, ma contiene meno informazione.</li>
<li><b>Distintività</b>: un descrittore più grande o dettagliato si accoppia più facilmente in modo univoco fra migliaia di candidati, ma costa di più da calcolare e confrontare.</li>
<li><b>Costo computazionale</b>: migliaia di punti per immagine, poi confronti fra coppie di immagini: tutto deve restare trattabile.</li>
</ul>
<p>Sono compromessi: nessuna scelta massimizza tutto insieme.</p>
""")

s(19, "Harris Corner Detector", "<p>Un criterio matematico ed economico per trovare gli angoli.</p>", kind="div", sec=("l8-harris", "Detector di Harris", "slide 19–42"))

s(20, "Why Corners: Edges vs. Corners vs. Flat Regions", """
<p>Si fa scorrere una piccola finestra (il cerchio rosso) e si guarda come cambia la patch:</p>
<ul>
<li><b>zona piatta</b>: nessun cambiamento in nessuna direzione;</li>
<li><b>bordo</b>: nessun cambiamento lungo il bordo, grande cambiamento attraverso (ambiguità 1D);</li>
<li><b>angolo</b>: grande cambiamento in <b>tutte</b> le direzioni.</li>
</ul>
<p>Gli angoli sono l'unico caso vincolato in 2D, quindi ben localizzati e ripetibili.</p>
<p><b>Figura:</b> tre quadratini con il cerchio rosso: grigio uniforme, un bordo diagonale fra nero e bianco, un angolo bianco su fondo nero.</p>
""")

s(21, "1D Ambiguity: The Aperture Problem", """
<ul>
<li>Guardando attraverso una piccola "apertura" (finestra), un bordo puro vincola il moto solo lungo la direzione del gradiente; il moto <b>lungo</b> il bordo è invisibile.</li>
<li>Nella detection è la stessa ambiguità: un punto di bordo sembra localmente uguale ai vicini lungo il bordo.</li>
<li>Gli <b>angoli</b> risolvono il problema perché vincolano due (o più) direzioni non parallele.</li>
</ul>
<p><b>Figura:</b> l'insegna del barbiere (barber pole). Il cilindro ruota, ma le strisce sembrano salire: attraverso l'apertura si percepisce solo la componente del moto perpendicolare alle strisce.</p>
""")

s(22, "Corner: An Intuitive Definition", """
<p>Un angolo ha:</p>
<ul>
<li>grandi variazioni di intensità, colore o texture;</li>
<li>variazioni in <b>due direzioni diverse</b> (se la variazione è forte in una sola direzione è un bordo, con ambiguità 1D).</li>
</ul>
<p>Serve ora una definizione computazionale economica che usi solo informazione locale.</p>
<p><i>Nota: la slide scrive "cheap computational definition of edge", ma si intende di <b>corner</b>.</i></p>
""")

s(23, "Edges as Gradients", """
<ul>
<li>Vedendo l'immagine come funzione continua: grandi salti di intensità = grandi derivate direzionali.</li>
</ul>
<span class="f">∇I(x) = (∂I/∂x, ∂I/∂y)(x)</span>
<ul>
<li>Il gradiente indica la direzione di <b>massima salita</b> ed è <b>perpendicolare</b> al contorno locale del bordo.</li>
<li>Si calcola con qualunque kernel derivativo visto in L5 (differenze finite, Sobel, derivate di gaussiana); esempio della slide: [−2, −1, 0, 1, 2].</li>
</ul>
<div class="box x"><b>Collegamento con L5</b><p>La derivata direzionale lungo il versore t = (cos θ, sin θ) è ∇I · t: basta calcolare I<sub>x</sub> e I<sub>y</sub> una volta sola per conoscere la variazione in ogni direzione. È esattamente quello che sfrutta la matrice di struttura. La slide chiama il gradiente J(x): in Szeliski J indica lo jacobiano, qui coincide con ∇I.</p></div>
""")

s(24, "The Sum-of-Squared-Differences Surface (SSD)", """
<p>Si vuole: gradiente alto in più direzioni, e un punto distinguibile dai vicini.</p>
<p>La <b>somma dei quadrati delle differenze</b> (SSD) misura la differenza fra un'immagine spostata di Δu e una seconda immagine:</p>
<span class="f">E<sub>SSD</sub>(Δu) = Σ<sub>i</sub> w(x<sub>i</sub>) [I<sub>1</sub>(x<sub>i</sub> + Δu) − I<sub>0</sub>(x<sub>i</sub>)]²</span>
<ul>
<li>x<sub>i</sub> e Δu sono coordinate 2D; Δu è il vettore di spostamento;</li>
<li>la somma corre sui pixel della finestra;</li>
<li>w è la finestra di pesi: un piccolo kernel box o gaussiano.</li>
</ul>
<p>Più E<sub>SSD</sub> è piccolo, più le due patch si somigliano.</p>
""")

s(25, "SSD as Autocorrelation", """
<ul>
<li>Il matching richiede due immagini, ma per <b>scegliere</b> i punti interessanti se ne ha una sola, I<sub>0</sub>.</li>
<li>Si usa allora l'<b>autocorrelazione</b>: la SSD dell'immagine con se stessa spostata.</li>
</ul>
<span class="f">E<sub>AC</sub>(Δu) = Σ<sub>i</sub> w(x<sub>i</sub>) [I<sub>0</sub>(x<sub>i</sub> + Δu) − I<sub>0</sub>(x<sub>i</sub>)]²</span>
<p>Un punto distintivo ha E<sub>AC</sub> <b>alto per ogni direzione</b> di Δu: spostando la patch in qualunque verso, non assomiglia più a se stessa. Serve un criterio efficiente per verificarlo senza provare tutti i Δu.</p>
<div class="box x"><b>Nota sulla notazione</b><p>Rispetto alla slide 24 i ruoli di I<sub>0</sub> e I<sub>1</sub> sono scambiati; non cambia nulla perché la differenza è al quadrato. "Autocorrelazione" è il nome usato da Szeliski, anche se la formula è una SSD, non un prodotto scalare.</p></div>
""")

s(26, "Examples", """
<p><b>Figura:</b> la stessa di slide 15 (Szeliski): immagine con tre croci e le tre superfici di autocorrelazione.</p>
<ul>
<li>Aiuola: minimo stretto in ogni direzione, <b>buon keypoint</b>.</li>
<li>Tetto: valle allungata lungo il bordo, <b>bordo</b>.</li>
<li>Nuvola: superficie bassa e piatta, <b>zona povera di struttura</b>.</li>
</ul>
<p><i>Nella didascalia le lettere sono (a), (b), (c), ma nella figura le superfici sono etichettate (b), (c), (d); (a) è l'immagine.</i></p>
""")

s(27, "Taylor Approximation of E_AC(Δu)", """
<p>Per piccoli spostamenti si approssima al primo ordine:</p>
<span class="f">I<sub>0</sub>(x<sub>i</sub> + Δu) ≈ I<sub>0</sub>(x<sub>i</sub>) + ∇I<sub>0</sub>(x<sub>i</sub>)<sup>⊤</sup> Δu</span>
<p>Sostituendo, I<sub>0</sub>(x<sub>i</sub>) si cancella:</p>
<span class="f">E<sub>AC</sub>(Δu) ≈ Σ<sub>i</sub> w(x<sub>i</sub>) [∇I<sub>0</sub>(x<sub>i</sub>)<sup>⊤</sup> Δu]²</span>
<div class="box k"><b>Da saper fare</b><p>Questa derivazione in tre righe (Taylor, cancellazione, quadrato di un prodotto scalare) è una domanda da orale classica. Ricorda che vale solo per Δu piccoli: è un'approssimazione locale della superficie di autocorrelazione.</p></div>
""")

s(28, "The Structure Tensor A", """
<p>Il quadrato di un prodotto scalare si scrive come forma quadratica: (g<sup>⊤</sup>Δu)² = Δu<sup>⊤</sup>(g g<sup>⊤</sup>)Δu. Quindi:</p>
<span class="f">E<sub>AC</sub>(Δu) ≈ Δu<sup>⊤</sup> A Δu,   A = Σ<sub>i</sub> w(x<sub>i</sub>) ∇I<sub>0</sub>(x<sub>i</sub>) ∇I<sub>0</sub>(x<sub>i</sub>)<sup>⊤</sup></span>
<p>Con ∇I<sub>0</sub> = (I<sub>x</sub>, I<sub>y</sub>):</p>
<span class="f">A = Σ<sub>(x,y)∈W</sub> w(x, y) [ I<sub>x</sub>²   I<sub>x</sub>I<sub>y</sub> ;  I<sub>x</sub>I<sub>y</sub>   I<sub>y</sub>² ]</span>
<ul>
<li>A si chiama <b>matrice dei momenti del secondo ordine</b> (second moment matrix) o <b>tensore di struttura</b>.</li>
<li>Aggrega l'informazione dei gradienti nella finestra w (gaussiana o box).</li>
<li>Riassume come cresce E<sub>AC</sub> in <b>ogni</b> direzione, senza provare esplicitamente ogni Δu.</li>
</ul>
<div class="box b"><b>Dal libro · Szeliski cap. 7, § 7.1.1 Feature detectors</b><p>Szeliski scrive la stessa matrice come convoluzione: A = w ∗ [I<sub>x</sub>² I<sub>x</sub>I<sub>y</sub>; I<sub>x</sub>I<sub>y</sub> I<sub>y</sub>²]. In pratica si calcolano tre immagini (I<sub>x</sub>², I<sub>y</sub>², I<sub>x</sub>I<sub>y</sub>) e le si sfoca con la stessa gaussiana: si ottiene A in <b>ogni</b> pixel con tre convoluzioni. Il libro osserva anche che l'inversa di A fornisce un limite inferiore all'incertezza sulla posizione della patch accoppiata: autovalori grandi = posizione ben determinata in quella direzione. <a href="https://szeliski.org/Book/">szeliski.org/Book</a></p></div>
<div class="box x"><b>Due scale diverse</b><p>Harris ha due σ: quella della derivata di gaussiana usata per I<sub>x</sub>, I<sub>y</sub> (scala di derivazione) e quella della finestra w (scala di integrazione, di solito più grande). Sono le due "manopole" del detector.</p></div>
""")

s(29, "The Structure Tensor A", """
<p>Richiamo dell'obiettivo: un punto distintivo ha E<sub>AC</sub> alto <b>in ogni direzione</b> Δu.</p>
<p>Ora che E<sub>AC</sub> ≈ Δu<sup>⊤</sup>AΔu, la domanda diventa: <b>quali proprietà di A</b> lo garantiscono? Risposta nelle slide 32–34: entrambi gli autovalori grandi.</p>
""")

s(30, "Example: Building A from Ix, Iy on a Patch", """
<ol>
<li>calcola I<sub>x</sub>, I<sub>y</sub> con un filtro derivativo sulla patch;</li>
<li>forma pixel per pixel le tre mappe I<sub>x</sub>², I<sub>y</sub>², I<sub>x</sub>I<sub>y</sub>;</li>
<li>somma (o pesa con una gaussiana) ciascuna mappa sulla finestra: sono le 3 entrate distinte di A (A è simmetrica);</li>
<li>costruisci A e calcola autovalori e autovettori.</li>
</ol>
<p><b>Figura:</b> il campo dei gradienti (frecce rosse) intorno a un angolo bianco su fondo nero, con la finestra (cerchio arancione). Le frecce puntano dal nero verso il bianco: sul lato orizzontale verso il basso, su quello verticale verso destra. Dentro la finestra ci sono gradienti in <b>due direzioni diverse</b>: è questo che rende A "piena".</p>
""")

s(31, "Code", """
<p>Il calcolo di A per un singolo punto in NumPy:</p>
<ul>
<li><code>np.gradient(corner_img)</code> restituisce le derivate lungo righe e colonne.</li>
<li><code>Ix = dI_dcol</code>; <code>Iy = -dI_drow</code>: il segno meno perché nell'array le righe crescono verso il basso, mentre l'asse y cartesiano punta in alto.</li>
<li><code>gauss_w</code>: finestra gaussiana con σ = window_radius/2 (<code>xx</code>, <code>yy</code> sono le coordinate della griglia intorno al punto, definite fuori dalla slide).</li>
<li>A è la matrice 2×2 delle somme pesate di I<sub>x</sub>², I<sub>x</sub>I<sub>y</sub>, I<sub>y</sub>².</li>
</ul>
<div class="box x"><b>Approfondimento</b><p>Per avere A in ogni pixel non si fa un ciclo: si calcolano le mappe <code>Ix**2</code>, <code>Iy**2</code>, <code>Ix*Iy</code> e le si sfoca con <code>scipy.ndimage.gaussian_filter</code>. Il segno di I<sub>y</sub> non cambia det(A) né trace(A) (cambia solo il segno di I<sub>x</sub>I<sub>y</sub>), quindi la risposta di Harris è la stessa.</p></div>
""")

s(32, "Eigenvalues/Eigenvectors of a Symmetric 2x2 Matrix", """
<span class="f">E<sub>AC</sub>(Δu) ≈ Δu<sup>⊤</sup> A Δu</span>
<ul>
<li>A è reale e simmetrica: autovalori λ<sub>1</sub>, λ<sub>2</sub> <b>reali</b>, autovettori e<sub>1</sub>, e<sub>2</sub> <b>ortogonali</b>.</li>
<li>A e<sub>i</sub> = λ<sub>i</sub> e<sub>i</sub>: lungo gli autovettori A agisce come pura scalatura.</li>
<li>Gli autovettori di A danno le direzioni di variazione locale <b>minima</b> e <b>massima</b> dell'intensità.</li>
</ul>
<div class="box k"><b>Da sapere</b><p>A è anche <b>semidefinita positiva</b> (è somma pesata, con pesi ≥ 0, di matrici g g<sup>⊤</sup>), quindi λ<sub>1</sub>, λ<sub>2</sub> ≥ 0: E<sub>AC</sub> non può essere negativa. Per una 2×2 simmetrica gli autovalori si ottengono in forma chiusa: λ = (tr ± √(tr² − 4 det))/2.</p></div>
""")

s(33, "Classifying Corners with Eigenvalues of A", """
<p>Nel sistema di riferimento ruotato lungo gli autovettori (u′<sub>x</sub>, u′<sub>y</sub>):</p>
<span class="f">E<sub>AC</sub>(Δu′) ≈ λ<sub>1</sub> u′<sub>x</sub>² + λ<sub>2</sub> u′<sub>y</sub>²</span>
<ul>
<li><b>λ<sub>1</sub>, λ<sub>2</sub> entrambi grandi</b>: struttura 2D netta e ben localizzata → <b>angolo</b>.</li>
<li><b>Uno grande, uno piccolo</b>: variazione in una sola direzione → <b>bordo</b>.</li>
<li><b>Entrambi piccoli</b>: nessuna struttura → <b>zona piatta</b>.</li>
</ul>
<div class="box k"><b>Interpretazione geometrica</b><p>Le curve di livello E<sub>AC</sub> = costante sono <b>ellissi</b> con assi lungo gli autovettori e semiassi proporzionali a 1/√λ<sub>i</sub>. Angolo: ellisse piccola e rotonda. Bordo: ellisse molto allungata lungo il bordo. Zona piatta: ellisse enorme.</p></div>
""")

s(34, "Classifying Regions: Flat, Edge, Corner via Eigenvalues", """
<ul>
<li>La classificazione richiede solo le <b>grandezze relative</b> di λ<sub>1</sub>, λ<sub>2</sub>, non gli autovettori.</li>
<li>Nel piano (λ<sub>1</sub>, λ<sub>2</sub>):
<ul><li>"piatto" = un piccolo quadrato vicino all'origine (entrambi piccoli);</li>
<li>"bordo" = due cunei sottili lungo gli assi (un autovalore molto più grande dell'altro);</li>
<li>"angolo" = tutto il resto (entrambi comparabilmente grandi).</li></ul></li>
</ul>
<p>La slide descrive il classico diagramma di Harris senza mostrarlo: consiglio di disegnarlo qui su OneNote, con gli assi λ<sub>1</sub> e λ<sub>2</sub> e le tre regioni.</p>
""")

s(35, "Example: Corner vs Edge", """
<p><b>Figura:</b> a sinistra un angolo, a destra un bordo verticale. Sopra il campo dei gradienti con la finestra, sotto gli autovettori di A disegnati sul pixel centrale con i loro autovalori.</p>
<ul>
<li><b>Angolo</b>: λ<sub>1</sub> ≈ 0.72, λ<sub>2</sub> ≈ 0.52. Due autovalori dello stesso ordine: variazione forte in ogni direzione.</li>
<li><b>Bordo</b>: λ<sub>1</sub> ≈ 1.40, λ<sub>2</sub> quasi nullo. L'autovettore di λ<sub>1</sub> è perpendicolare al bordo (direzione del gradiente); lungo il bordo la variazione è praticamente zero.</li>
</ul>
<p>Nota: il bordo ha un λ<sub>1</sub> <b>più grande</b> dell'angolo. Guardare solo l'autovalore massimo, o la traccia, non basta: conta che <b>entrambi</b> siano grandi.</p>
""")

s(36, "The Harris Response Function R", """
<p>Calcolare gli autovalori in ogni pixel è costoso; Harris e Stephens (1988) propongono una quantità più economica:</p>
<span class="f">R = det(A) − α · trace(A)² = λ<sub>1</sub>λ<sub>2</sub> − α (λ<sub>1</sub> + λ<sub>2</sub>)²</span>
<ul>
<li>det e trace si calcolano direttamente dalle entrate I<sub>x</sub>², I<sub>y</sub>², I<sub>x</sub>I<sub>y</sub>: det(A) = λ<sub>1</sub>λ<sub>2</sub>, trace(A) = λ<sub>1</sub> + λ<sub>2</sub>. Niente autodecomposizione.</li>
<li><b>R grande e positivo</b>: entrambi gli autovalori grandi → angolo.</li>
<li><b>R grande e negativo</b>: un autovalore molto più grande dell'altro → bordo.</li>
<li><b>|R| piccolo</b>: entrambi piccoli → zona piatta.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Con A = [a b; b c]: det = ac − b², trace = a + c. Verifica sui casi limite: bordo puro (λ<sub>2</sub> = 0) → R = −αλ<sub>1</sub>² &lt; 0; angolo con λ<sub>1</sub> = λ<sub>2</sub> = λ → R = λ²(1 − 4α) &gt; 0 per α &lt; 1/4. Applicato all'esempio della slide 35 con α = 0.05: angolo R ≈ 0.376 − 0.076 ≈ 0.30; bordo (λ<sub>2</sub> ≈ 0) R ≈ −0.05·1.4² ≈ −0.1.</p></div>
<div class="box b"><b>Dal libro · Szeliski cap. 7, § 7.1.1 Feature detectors</b><p>Il libro presenta R come una delle possibili misure scalari di "angolosità" ricavate da A, con α = 0.06 come valore tipico. Altre scelte: il <b>minimo autovalore</b> λ<sub>min</sub> (Shi e Tomasi), che misura direttamente la direzione peggiore; la <b>media armonica</b> det(A)/trace(A) = λ<sub>1</sub>λ<sub>2</sub>/(λ<sub>1</sub> + λ<sub>2</sub>) (Brown, Szeliski e Winder), più liscia nelle zone in cui λ<sub>1</sub> ≈ λ<sub>2</sub>. Sono tutte funzioni che crescono solo se entrambi gli autovalori sono grandi. <a href="https://szeliski.org/Book/">szeliski.org/Book</a></p></div>
""")

s(37, "Choosing α and Thresholding", """
<ul>
<li><b>α</b> è un parametro empirico di sensibilità: si fissa guardando qualche esempio (valori tipici 0.04–0.06).</li>
<li>α regola quanto R penalizza le strutture allungate (tipo bordo) rispetto a quelle tipo angolo: più α è grande, più un punto deve essere "isotropo" per avere R &gt; 0.</li>
<li>Calcolato R in ogni pixel, si tengono solo i punti con <b>R &gt; τ</b>.</li>
<li>τ bilancia numero e qualità dei keypoint:
<ul><li>τ troppo basso: tanti angoli spuri e rumorosi;</li><li>τ troppo alto: si perdono angoli deboli ma validi.</li></ul></li>
</ul>
<div class="box x"><b>Approfondimento</b><p>R = λ<sub>1</sub>λ<sub>2</sub> − α(λ<sub>1</sub> + λ<sub>2</sub>)² è positivo solo se il rapporto r = λ<sub>1</sub>/λ<sub>2</sub> soddisfa r/(1 + r)² &gt; α. Con α = 0.05 serve r &lt; circa 17.9: oltre, R diventa negativo e il punto è trattato come bordo. È lo stesso tipo di vincolo sul rapporto degli autovalori che SIFT usa per scartare i bordi (slide 62).</p></div>
""")

s(38, "Adaptive Non-Maximal Suppression (ANMS) of Corner Responses", """
<ul>
<li>La sola soglia lascia <b>grappoli</b> di pixel vicini tutti con R alto (lo stesso angolo fisico occupa più pixel).</li>
<li>Inoltre le zone ad alto contrasto hanno molti più keypoint delle altre.</li>
<li><b>ANMS</b>: tenere un punto solo se la sua R è significativamente (10%) migliore di quella degli altri nell'intorno.</li>
<li>Risultato: keypoint isolati, ben localizzati e <b>distribuiti uniformemente</b> nell'immagine.</li>
<li>Idee simili tornano in SIFT (estremi nello scale-space) e nei detector moderni.</li>
</ul>
<div class="box w"><b>Attenzione: la slide descrive l'ANMS in modo impreciso</b><p>Con un intorno fisso quella descritta è la normale <b>non-maximum suppression</b> (NMS). L'ANMS di Brown, Szeliski e Winder (2005), da cui viene la figura della slide 39, è "adattiva" perché il raggio non è fissato: per ogni punto si calcola il <b>raggio di soppressione</b> r<sub>i</sub>, cioè la distanza dal punto più vicino con risposta significativamente maggiore (almeno del 10%: R<sub>i</sub> &lt; 0.9 · R<sub>j</sub>); poi si ordinano i punti per r<sub>i</sub> decrescente e si tengono i primi n. Il raggio finale (r = 24, r = 16 nella figura) è una conseguenza di quanti punti si vogliono, non un parametro.</p></div>
""")

s(39, "ANMS", """
<p><b>Figura</b> (Szeliski, da Brown et al. 2005): la stessa foto (prato, alberi, un oggetto rosso al centro) con i keypoint sovrapposti.</p>
<ul>
<li>(a) i 250 più forti e (b) i 500 più forti: si ammassano nella fascia degli alberi, ad alto contrasto; il prato ne ha pochi.</li>
<li>(c) ANMS con 250 punti, r = 24 e (d) ANMS con 500 punti, r = 16: i punti coprono tutta l'immagine in modo uniforme.</li>
</ul>
<p>Perché conta: per stimare bene una trasformazione (es. per un panorama) servono corrispondenze sparse su tutta l'immagine, non tutte nello stesso angolo.</p>
""")

s(40, "Example: Harris Response", """
<p><b>Figura:</b> la foto "cameraman" (uomo con treppiede e cinepresa su un prato); al centro la mappa della risposta R; a destra i 50 angoli rilevati (cerchi rossi).</p>
<ul>
<li>La mappa R è quasi ovunque neutra, con punti isolati e brevi tratti: valori alti solo in pochi punti.</li>
<li>Gli angoli cadono sui veri angoli geometrici: cinepresa, gambe del treppiede, mani, edifici sullo sfondo, incroci di texture.</li>
<li>Zone piatte (cielo, prato) e bordi rettilinei lunghi sono correttamente soppressi.</li>
</ul>
""")

s(41, "Example: Harris Under Rotation and Illumination Change", """
<p><b>Figura:</b> a sinistra l'immagine originale con gli angoli di Harris; a destra la stessa ruotata di 25° intorno al centro, con luminosità e contrasto cambiati, con gli angoli ri-rilevati da zero (legenda: rilevati / corrispondenti al ground truth).</p>
<ul>
<li>Per misurare la <b>ripetibilità</b> si mappano gli angoli originali con la rotazione nota e si guarda se lì c'è un angolo ri-rilevato (entro 3 pixel).</li>
<li>Risultato: <b>74%</b> degli angoli ritrovati.</li>
</ul>
<p>Punto della slide: Harris regge bene a rotazione e cambi di illuminazione affini. Non è perfetto perché la soglia su R dipende dal contrasto (R scala come il contrasto alla quarta) e per effetti di discretizzazione.</p>
""")

s(42, "Limitations of Harris: Lack of Scale and Rotation Invariance", """
<ul>
<li>Harris usa una finestra di dimensione <b>fissa</b> W, scelta una volta per tutta l'immagine.</li>
<li><b>Scala</b>: se lo stesso angolo appare a una scala diversa (camera più vicina o lontana), la stessa finestra vede una quantità diversa di struttura; la risposta, e perfino il fatto che l'angolo venga rilevato, possono cambiare. Esempio classico: un arco di cerchio che, visto da vicino con finestra piccola, sembra un bordo, e da lontano un angolo.</li>
<li>Soluzione ingenua: rieseguire Harris a più scale fisse. Non dice però <b>quale</b> scala è quella giusta per ciascun punto.</li>
</ul>
<p>Serve un modo principiato per ottenere l'invarianza alla rotazione e per scegliere, per ogni keypoint, una <b>scala caratteristica</b>.</p>
<div class="box w"><b>Attenzione: sulla rotazione il titolo è impreciso</b><p>La <b>risposta</b> di Harris è già invariante alla rotazione: dipende da det(A) e trace(A), cioè dagli autovalori, che non cambiano ruotando l'immagine (con finestra gaussiana isotropa). Il detector è quindi equivariante alla rotazione, come mostra la slide 41 (74% di ripetibilità dopo 25°). Quello che manca è un'<b>orientazione canonica</b> associata al punto, necessaria per costruire un descrittore invariante: è ciò che aggiunge SIFT (slide 65–67). La vera limitazione del detector è la <b>scala</b>.</p></div>
""")

s(43, "Scale Invariance and Scale-Space Detectors", "<p>Scegliere automaticamente la scala giusta per ogni keypoint.</p>", kind="div", sec=("l8-scala", "Invarianza di scala e blob", "slide 43–55"))

s(44, "Blob Detection", """
<ul>
<li>Si passa dalla detection di angoli alla detection di <b>blob</b>.</li>
<li>Un <b>blob</b> è una regione con proprietà uniformi (colore, luminosità, texture), spesso di forma ellittica o circolare.</li>
</ul>
<p><b>Figura</b> (opencv.org): a sinistra una foto di fogli con pallini colorati di varie dimensioni; a destra gli stessi pallini cerchiati in rosso dal blob detector, ognuno con un cerchio della sua dimensione.</p>
<p>Il blob ha una dimensione naturale (il raggio): per questo è l'oggetto ideale per parlare di scala caratteristica.</p>
""")

s(45, "Recap: Scale-Space and Gaussian Pyramids", """
<ul>
<li><b>Scale-space</b> (L6): l'immagine convoluta con gaussiane di σ crescente forma una famiglia continua di versioni sempre più sfocate.</li>
</ul>
<span class="f">L(x, y, σ) = G(x, y, σ) ∗ I(x, y)</span>
<ul>
<li><b>Piramide gaussiana</b>: versione discreta ed efficiente dello scale-space; blur e sottocampionamento di 2, ripetuti.</li>
<li>σ più grande = scala più grossolana = strutture grandi enfatizzate, dettagli piccoli soppressi.</li>
</ul>
<p><b>Obiettivo della sezione</b>: usare lo scale-space per scegliere la scala giusta di ogni keypoint.</p>
""")

s(46, "The Need for a Characteristic Scale per Keypoint", """
<ul>
<li>Un blob o una struttura ad angolo ha una <b>dimensione intrinseca</b> (es. il raggio di una macchia scura circolare).</li>
<li>Se la risposta si misura alla scala sbagliata (finestra molto più piccola o più grande della struttura), è debole o instabile. Succede anche con la R di Harris. Scala ideale: finestra grande quanto la struttura.</li>
<li><b>Scala caratteristica</b>: per ogni keypoint si cerca automaticamente la σ* che <b>massimizza</b> una risposta dipendente dalla scala; σ* diventa parte dell'identità del keypoint.</li>
<li>Punto cruciale: σ* deve essere <b>covariante</b> con la scala dell'immagine. Se ingrandisco l'immagine di un fattore s, la σ* rilevata deve diventare s·σ*.</li>
</ul>
<div class="box k"><b>Perché è la chiave dell'invarianza di scala</b><p>Se σ* segue la scala dell'immagine, una patch di raggio proporzionale a σ* contiene lo stesso contenuto in entrambe le immagini. Normalizzando la patch a una dimensione fissa, il descrittore diventa invariante alla scala.</p></div>
""")

s(47, "Laplacian of Gaussian (LoG)", """
<span class="f">∇²G(x, y, σ) = ∂²G/∂x² + ∂²G/∂y²</span>
<ul>
<li>Il laplaciano ∂²I/∂x² + ∂²I/∂y² misura le derivate spaziali del secondo ordine.</li>
<li>Come ogni operazione basata su derivate, è sensibile al rumore.</li>
<li>Si applica quindi all'immagine sfocata: ∇²(G ∗ I).</li>
<li>Per la proprietà associativa (e commutativa) della convoluzione, equivale ad applicare direttamente il <b>LoG</b>: ∇²(G ∗ I) = (∇²G) ∗ I.</li>
</ul>
<p><b>Figura:</b> il LoG in 3D, un "cappello messicano rovesciato": pozzo negativo al centro, anello leggermente positivo intorno (scala ×10<sup>−3</sup>).</p>
<p>Collegamento: è lo stesso LoG della L5 (slide 52–53 di L5).</p>
""")

s(48, "LoG Response", """
<p><b>Figura:</b> a sinistra un segnale 1D a gradino (0 fino a circa 100, poi 1); a destra la sua risposta al LoG: zero nelle zone costanti, un picco positivo e uno negativo ai due lati del gradino, con uno <b>zero-crossing</b> esattamente sul bordo.</p>
<ul>
<li>Il LoG è circa zero nelle zone costanti (e anche sulle rampe lineari, perché la derivata seconda di una retta è zero).</li>
<li>Risponde forte vicino ai bordi.</li>
</ul>
<p>Per i blob si guarda un'altra cosa: non lo zero-crossing, ma il <b>valore estremo</b> al centro di una macchia (slide 50).</p>
""")

s(49, "Laplacian of Gaussian (LoG) for Scale Selection", """
<p>Forma esplicita (gaussiana normalizzata):</p>
<span class="f">LoG(x, y) = −1/(πσ⁴) · [1 − (x² + y²)/(2σ²)] · e<sup>−(x² + y²)/(2σ²)</sup></span>
<p>Risposta <b>normalizzata in scala</b>:</p>
<span class="f">L<sub>LoG</sub>(x, y, σ) = σ² ∇²(G(·, ·, σ) ∗ I)</span>
<ul><li>Il fattore σ² rende le risposte <b>confrontabili fra scale diverse</b>.</li></ul>
<div class="box k"><b>Da saper spiegare: perché σ²</b><p>Ogni derivata di una gaussiana porta un fattore 1/σ: le derivate seconde scalano come 1/σ². Senza correzione, la risposta del LoG cala al crescere di σ anche sulla stessa struttura, e il massimo lungo la scala cadrebbe sempre a σ piccola. Moltiplicare per σ² (una volta σ per ciascun ordine di derivazione, secondo Lindeberg) rende la risposta invariante: se l'immagine è ingrandita di s, la curva σ²|∇²L| si sposta di s lungo l'asse delle scale senza cambiare altezza.</p>
<p>Verifica della formula: ∇²G = ((x² + y²)/σ⁴ − 2/σ²) · G, e con G = e<sup>−r²/2σ²</sup>/(2πσ²) si ottiene esattamente la forma della slide. Al centro vale −1/(πσ⁴).</p></div>
<div class="box b"><b>Dal libro · visionbook cap. 18, § 18.9 Image Laplacian</b><p>Il capitolo sulle derivate scrive il LoG come ∇²g = (x² + y² − 2σ²)/σ⁴ · g, lo chiama "mexican hat" rovesciato e osserva che è rotazionalmente invariante, nullo sulle variazioni lineari e passa-banda per σ &gt; 1. Non tratta la normalizzazione σ² né la selezione di scala: per quelle serve Szeliski. <a href="https://visionbook.mit.edu/derivatives.html">visionbook.mit.edu/derivatives.html</a></p></div>
""")

s(50, "Laplacian of Gaussian (LoG) for Scale Selection", """
<ul>
<li>Il LoG risponde fortemente alle strutture tipo blob la cui dimensione corrisponde a σ: un <b>disco di raggio ≈ √2·σ</b> dà la risposta massima.</li>
<li><b>Selezione della scala</b>: per un punto candidato si valuta il LoG normalizzato su un intervallo di σ; la σ che <b>massimizza</b> la risposta (in valore assoluto) è la scala caratteristica.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Da dove viene √2σ: il LoG si annulla sul cerchio x² + y² = 2σ² (lo si vede dalla parentesi [1 − r²/2σ²]). La risposta al centro di un disco è massima quando il disco riempie esattamente la parte negativa del kernel, cioè quando il bordo del disco coincide con lo zero-crossing: r = √2·σ. Quindi σ* = r/√2, e raddoppiando il raggio σ* raddoppia (covarianza con la scala).</p></div>
""")

s(51, "Difference of Gaussians (DoG) as an Efficient LoG Approximation", """
<ul><li>Il LoG su molte scale è costoso.</li></ul>
<p><b>Differenza di gaussiane</b>:</p>
<span class="f">D(x, y, σ) = G(x, y, kσ) ∗ I − G(x, y, σ) ∗ I</span>
<span class="f">G(x, y, kσ) − G(x, y, σ) ≈ (k − 1) σ² ∇²G</span>
<ul>
<li>La DoG è proporzionale al LoG <b>già normalizzato</b> σ²∇²G.</li>
<li>È una sottrazione di due immagini sfocate, che si hanno già se si costruisce la piramide gaussiana.</li>
</ul>
<div class="box k"><b>Da saper ricavare</b><p>Dall'equazione del calore (L6): ∂G/∂σ = σ∇²G. Approssimando la derivata con un rapporto incrementale fra σ e kσ:</p>
<span class="f">σ∇²G = ∂G/∂σ ≈ (G(kσ) − G(σ)) / (kσ − σ)</span>
<p>quindi G(kσ) − G(σ) ≈ (k − 1)σ²∇²G. Il fattore (k − 1) è <b>costante</b> su tutte le scale: non altera la posizione degli estremi. La normalizzazione σ² arriva "gratis".</p></div>
<div class="box w"><b>Attenzione: "for a small scale k" è impreciso</b><p>k non è una scala ma il <b>rapporto</b> fra due scale consecutive, e deve essere <b>vicino a 1</b> (k → 1), non piccolo: l'approssimazione è esatta nel limite k → 1. In SIFT k = 2<sup>1/s</sup>, con s = 3 k ≈ 1.26; Lowe osserva che anche con k = √2 la qualità degli estremi quasi non cambia.</p></div>
""")

s(52, "Scale-Space Extrema Detection", """
<ul>
<li>Si costruisce una pila di immagini DoG D(x, y, σ<sub>1</sub>), D(x, y, σ<sub>2</sub>), … a scale ravvicinate, organizzate in <b>ottave</b> (piramide DoG, come la gaussiana).</li>
<li>È una rappresentazione 3D: SCALA × LARGHEZZA × ALTEZZA.</li>
<li><b>Keypoint candidato</b>: un pixel che è un <b>estremo locale</b> (massimo o minimo) nel suo intorno 3 × 3 × 3: 8 vicini nella stessa scala, 9 nella scala sopra, 9 in quella sotto (26 in totale).</li>
</ul>
<p>Con una sola ricerca in un volume 3D si ottengono insieme la <b>localizzazione spaziale</b> (x, y), come la NMS di Harris, e la <b>selezione della scala</b> (σ).</p>
<div class="box k"><b>Da ricordare</b><p>Massimi e minimi corrispondono a blob scuri su sfondo chiaro e blob chiari su sfondo scuro (dipende dal segno della DoG). Vanno cercati entrambi.</p></div>
""")

s(53, "Example: Blob Detector", """
<p><b>Figura</b> (opencv.org): la stessa immagine dei pallini della slide 44, prima e dopo il blob detector.</p>
<ul>
<li>Ogni keypoint ha la sua <b>dimensione caratteristica</b>: cerchi piccoli sui pallini piccoli, grandi su quelli grandi.</li>
<li>Si è ottenuta l'<b>equivarianza di scala</b>: riscalando l'immagine si ritrovano gli stessi keypoint, con scale corrispondentemente diverse.</li>
</ul>
""")

s(54, "Example: DoG Pyramid", """
<p><b>Figura:</b> griglia 3 × 3 di immagini DoG dell'immagine dei pallini: righe = ottave 1, 2, 3; colonne = DoG 1, 2, 3 di ogni ottava. Ogni riquadro riporta quante detection contiene (da 2 a 12), segnate da cerchi rossi.</p>
<ul>
<li>Scendendo di ottava l'immagine è più piccola e sfocata (qui è mostrata ingrandita alla stessa dimensione, quindi appare sgranata).</li>
<li>Le detection nelle ottave basse sono su dettagli piccoli; nelle ottave alte sui pallini grandi, con cerchi più grandi.</li>
<li>In ogni livello le DoG mostrano i pallini come macchie chiare o scure su fondo grigio (grigio = zero).</li>
</ul>
""")

s(55, "Conclusions", """
<ul>
<li>Ora si ha un detector di tipo "blob".</li>
<li>La detection è nello <b>scale-space</b>: ogni keypoint è associato alla sua scala caratteristica.</li>
<li>L'uscita del detector è molto rumorosa e va ripulita (NMS/ANMS, soglie, …).</li>
<li>Serve anche una taratura manuale dei parametri.</li>
</ul>
""")

s(56, "SIFT: Detection and Localization", "<p>La pipeline di Lowe, prima metà: dove e a che scala.</p>", kind="div", sec=("l8-sift-det", "SIFT: detection e localizzazione", "slide 56–63"))

s(57, "SIFT Overview", """
<ul>
<li><b>SIFT</b> (Scale-Invariant Feature Transform, Lowe 1999/2004): la prima pipeline largamente adottata che unisce detection invariante alla scala e un descrittore robusto e distintivo.</li>
<li>Dominante per oltre un decennio in stitching, SfM, riconoscimento di oggetti; ancora oggi è il baseline con cui si confrontano i metodi appresi.</li>
</ul>
<p><b>Pipeline completa</b>:</p>
<ol>
<li>detection con la DoG → invarianza di scala;</li>
<li>localizzazione sub-pixel → precisione;</li>
<li>assegnazione dell'orientazione → invarianza alla rotazione;</li>
<li>descrittore a istogrammi di gradienti, normalizzato → invarianza all'illuminazione.</li>
</ol>
<div class="box k"><b>Da saper fare</b><p>Elencare i quattro stadi e, per ognuno, quale invarianza produce. È la domanda d'esame più probabile sulla lezione (vedi anche la tabella della slide 73).</p></div>
""")

s(58, "SIFT Pipeline Stage 1: DoG Pyramid Construction", """
<ul>
<li>Si costruisce una piramide gaussiana con <b>più scale per ottava</b> (tipicamente s = 3 intervalli).</li>
<li>Si costruisce la piramide DoG sottraendo immagini gaussiane adiacenti.</li>
<li>All'inizio di ogni nuova ottava si sottocampiona di 2 (stessa costruzione delle piramidi di L6).</li>
</ul>
<p>Risultato: un volume scale-space 3D per ottava, pronto per la ricerca degli estremi.</p>
<p><b>Figura</b> (dal paper di Lowe): a sinistra le pile di immagini gaussiane della prima ottava e, sopra, della successiva più piccola; a destra le DoG ottenute sottraendo ogni coppia adiacente.</p>
<div class="box k"><b>Da saper contare</b><p>Con s intervalli per ottava: k = 2<sup>1/s</sup>, servono <b>s + 3</b> immagini gaussiane per ottava, che danno <b>s + 2</b> DoG; la ricerca degli estremi (che richiede una scala sopra e una sotto) si fa sulle s DoG interne, e così le ottave coprono le scale senza buchi. Con s = 3: 6 gaussiane, 5 DoG, 3 livelli utili. Lowe parte da σ = 1.6 (dopo aver raddoppiato l'immagine iniziale).</p></div>
""")

s(59, "SIFT Pipeline Stage 2: Keypoint Localization via Extrema Detection", """
<ul>
<li>In ogni immagine DoG si cercano i pixel che sono estremi locali fra i vicini:
<ul><li>26 vicini (8 nella stessa scala, 9 sopra, 9 sotto);</li><li>la prima e l'ultima scala di ogni ottava sono escluse (manca un vicino).</li></ul></li>
<li>Si ottiene un grande insieme di <b>keypoint candidati</b>:
<ul><li>molti sono instabili (basso contrasto, su bordi);</li><li>vanno filtrati nei passi successivi.</li></ul></li>
</ul>
<p>Risultato: candidati (x, y, σ), con posizione e scala.</p>
<p><b>Figura</b> (paper di Lowe): tre griglie sovrapposte lungo l'asse della scala; il pixel centrale (croce) è confrontato con i suoi 26 vicini (cerchi verdi) nella stessa scala e nelle due adiacenti.</p>
""")

s(60, "Sub-Pixel Refinement of Keypoint Location and Scale", """
<p><b>Problema</b>: la posizione del keypoint è quantizzata sulla griglia dei pixel (e delle scale).</p>
<p><b>Soluzione</b>: si sviluppa D(x, y, σ) in serie di Taylor al secondo ordine intorno al campione e si cerca l'estremo della quadrica, con un passo di tipo Newton.</p>
<span class="f">D(x) ≈ D + ∇D<sup>⊤</sup>x + ½ x<sup>⊤</sup>H<sub>D</sub>x   ⇒   x̂ = −H<sub>D</sub><sup>−1</sup> ∇D</span>
<p>(x = (x, y, σ) è lo scostamento dal campione; ∇D e l'hessiana 3×3 H<sub>D</sub> si stimano con differenze finite fra pixel e scale vicine.)</p>
<ul><li>Se lo scostamento supera 0.5 in una qualunque direzione, l'estremo è più vicino a un altro campione: ci si sposta lì e si ripete.</li></ul>
<p>Risultato: precisione sub-pixel e sub-scala.</p>
<div class="box w"><b>Attenzione: "search for minima" è impreciso</b><p>Si cerca l'<b>estremo</b> (massimo o minimo) della quadrica: gli estremi della DoG sono sia massimi sia minimi (slide 52). Il passo x̂ = −H<sup>−1</sup>∇D trova il punto stazionario in entrambi i casi.</p></div>
""")

s(61, "Rejecting Low-Contrast Keypoints", """
<p><b>Problema</b>: vanno eliminati i keypoint rumorosi.</p>
<ul>
<li>Se |D(p)| &lt; τ (iperparametro), il keypoint si scarta.</li>
<li>Una risposta DoG debole significa basso contrasto locale, sensibilità al rumore e scarsa ripetibilità.</li>
</ul>
<p>Risultato: si elimina una grossa parte dei candidati che sono estremi ma non robusti.</p>
<div class="box x"><b>Dettagli dal paper</b><p>Lowe valuta D nel punto raffinato: D(x̂) = D + ½∇D<sup>⊤</sup>x̂, e scarta se |D(x̂)| &lt; 0.03 con intensità in [0, 1].</p></div>
""")

s(62, "Rejecting Edge Responses (Hessian-Based Test)", """
<p><b>Problema</b>: un estremo della DoG può stare su un bordo, dove è mal localizzato lungo la direzione del bordo (lo stesso aperture problem di Harris). La DoG risponde forte anche ai bordi.</p>
<ul><li>Si riusa l'idea di Harris con l'<b>hessiana</b> 2×2 di D in (x, y) nel keypoint:</li></ul>
<span class="f">H = [ D<sub>xx</sub>  D<sub>xy</sub> ;  D<sub>xy</sub>  D<sub>yy</sub> ]</span>
<ul><li>Il rapporto fra gli autovalori r = λ<sub>max</sub>/λ<sub>min</sub> si controlla senza autodecomposizione:</li></ul>
<span class="f">trace(H)² / det(H) = (λ<sub>max</sub> + λ<sub>min</sub>)² / (λ<sub>max</sub>λ<sub>min</sub>) = (r + 1)²/r</span>
<ul><li>Si <b>tiene</b> il punto se trace²/det &lt; (r + 1)²/r con la soglia r = 10 di Lowe (cioè &lt; 12.1), altrimenti si scarta.</li></ul>
<div class="box k"><b>Da saper spiegare</b><ul>
<li>(r + 1)²/r è minima (vale 4) per r = 1 e cresce con r: controllare trace²/det equivale a controllare il rapporto degli autovalori.</li>
<li>Gli autovalori dell'hessiana sono le <b>curvature principali</b> di D: su un bordo la curvatura attraverso il bordo è grande e quella lungo il bordo è piccola.</li>
<li>Attenzione alla differenza con Harris: là la matrice è il tensore di struttura A (prodotti di derivate <b>prime</b>), qui è l'hessiana (derivate <b>seconde</b>). Stessa logica, stesso trucco det/trace, matrice diversa.</li>
<li>Se det(H) &lt; 0 le curvature hanno segni opposti (punto di sella): non è un estremo, si scarta.</li></ul></div>
""")

s(63, "Recap", """
<ul>
<li>Si ha un insieme di keypoint candidati (x, y, σ), localizzati in spazio e scala.</li>
<li>I keypoint sono filtrati: via quelli a basso contrasto e quelli su bordi.</li>
<li>Sono robusti a piccole trasformazioni (traslazioni, rotazioni, scale, piccoli cambi di illuminazione).</li>
<li><b>Prossimo passo</b>: progettare un descrittore per ogni keypoint.</li>
</ul>
""")

s(64, "SIFT: Orientation and Descriptor", "<p>Seconda metà della pipeline: orientazione e vettore descrittore.</p>", kind="div", sec=("l8-sift-desc", "SIFT: orientazione e descrittore", "slide 64–73"))

s(65, "Orientation Assignment: Gradient Orientation", """
<p><b>Obiettivo</b>: assegnare un'orientazione a ogni keypoint per ottenere l'invarianza alla rotazione.</p>
<ul>
<li>Per ogni keypoint p = (x, y, σ) si usa l'immagine gaussiana L (già calcolata) con scala più vicina a σ: così l'orientazione è calcolata in modo invariante alla scala.</li>
<li>In ogni punto di L si calcolano modulo e orientazione del gradiente con differenze finite:</li>
</ul>
<span class="f">d<sub>x</sub> = L(x+1, y) − L(x−1, y),   d<sub>y</sub> = L(x, y+1) − L(x, y−1)</span>
<span class="f">m(x, y) = √(d<sub>x</sub>² + d<sub>y</sub>²),   θ(x, y) = tan<sup>−1</sup>(d<sub>y</sub>/d<sub>x</sub>)</span>
<div class="box x"><b>Nota pratica</b><p>tan<sup>−1</sup>(d<sub>y</sub>/d<sub>x</sub>) dà angoli solo in (−90°, 90°); per l'istogramma su 360° serve la versione a due argomenti <code>atan2(dy, dx)</code>, che usa i segni di entrambe le componenti. Le differenze centrali non sono divise per 2: non importa, perché tutti i moduli sono scalati allo stesso modo.</p></div>
""")

s(66, "Orientation Assignment: Gradient Orientation Histogram", """
<ul>
<li>Si calcolano m e θ in un intorno di p, pesati con una gaussiana di σ pari a <b>1.5 volte</b> la scala del keypoint, centrata su p.</li>
<li>Si costruisce un istogramma delle orientazioni a <b>36 bin</b> (10° per bin); ogni pixel vota con peso = modulo del gradiente × peso gaussiano.</li>
<li>Il <b>picco</b> dell'istogramma è l'orientazione dominante del keypoint.</li>
</ul>
<p>Risultato: si ottiene l'invarianza alla rotazione ruotando la patch in modo da allinearla all'orientazione del picco.</p>
<div class="box x"><b>Dettaglio dal paper</b><p>Per una precisione migliore di 10°, Lowe interpola il picco con una parabola sui tre bin vicini.</p></div>
""")

s(67, "Handling Multiple Dominant Orientations", """
<ul>
<li>Se l'istogramma ha altri picchi sopra l'<b>80%</b> del massimo, il keypoint si <b>duplica</b>: una copia per ogni orientazione dominante (stessa posizione e scala).</li>
<li>Esempi: angoli dove si incontrano due bordi forti; texture con direzione dominante ambigua.</li>
<li>Ogni copia è trattata in modo indipendente (descrittore e match propri): più robustezza per i punti senza un'orientazione unica.</li>
</ul>
<p>Secondo Lowe capita a circa il 15% dei punti, ma contribuisce molto alla stabilità del matching.</p>
""")

s(68, "Descriptor: Gradient Histograms in a Local Patch", """
<p><b>Obiettivo</b>: un vettore descrittore invariante alle trasformazioni, per un matching robusto fra viste diverse.</p>
<p>Ogni keypoint ha ora un <b>sistema di riferimento</b> proprio:</p>
<ul>
<li>la posizione dà l'invarianza alla traslazione;</li>
<li>la scala dà l'invarianza alla scala;</li>
<li>l'orientazione dà l'invarianza alla rotazione.</li>
</ul>
<p><b>Idea ingenua</b>: correlazione normalizzata fra patch. Non è abbastanza robusta a deformazioni non rigide e a piccoli errori di posizione.</p>
<p><b>Soluzione</b>: riusare gli istogrammi di gradiente come descrittore.</p>
<div class="box k"><b>Perché gli istogrammi funzionano</b><p>Un istogramma su una cella dice "quanti gradienti in ogni direzione", non "esattamente dove": se un gradiente si sposta di un pixel dentro la cella il vettore quasi non cambia. È una tolleranza controllata agli spostamenti, che la correlazione pixel per pixel non ha.</p></div>
""")

s(69, "Descriptor: Gradient Histograms in a Local Patch", """
<p>Sull'immagine gaussiana L(σ) più vicina alla scala del keypoint, ruotata secondo l'orientazione dominante:</p>
<ul>
<li>si estrae una patch intorno al keypoint;</li>
<li>si calcolano modulo e orientazione del gradiente in ogni pixel;</li>
<li>si divide la patch in una griglia regolare di sotto-regioni e in ognuna si accumula un istogramma delle orientazioni (pesato con una gaussiana).</li>
</ul>
<p>Risultato: il descrittore è la concatenazione degli istogrammi.</p>
<p><b>Figura</b> (paper di Lowe): a sinistra i gradienti di una patch 8 × 8 come frecce, con il cerchio della finestra gaussiana; a destra il descrittore 2 × 2: in ogni cella una "stella" di 8 frecce, la cui lunghezza è il totale dei gradienti in quella direzione. Nel SIFT vero la patch è 16 × 16 e la griglia 4 × 4 (slide 70).</p>
""")

s(70, "SIFT 128-D Descriptor", """
<ul>
<li>Patch divisa in una griglia di <b>4 × 4 celle</b> (ogni cella 4 × 4 campioni, patch 16 × 16).</li>
<li>Ogni cella: istogramma delle orientazioni a <b>8 bin</b> (45° per bin).</li>
<li><b>4 × 4 × 8 = 128</b> numeri: il descrittore SIFT.</li>
<li><b>Interpolazione trilineare</b>: ogni voto si distribuisce fra celle vicine (in x e in y) e bin di orientazione vicini, per evitare salti quando un gradiente passa da una cella o da un bin all'altro.</li>
</ul>
<p><b>Figura:</b> la stessa di slide 69.</p>
<div class="box k"><b>Da saper confrontare</b><p>Istogramma di orientazione (slide 66): 36 bin, uno per keypoint, serve a trovare l'orientazione. Istogrammi del descrittore: 8 bin, 16 per keypoint, calcolati dopo aver ruotato la patch. Non confonderli.</p></div>
""")

s(71, "Normalization for Illumination Invariance", """
<ul>
<li>Cambi di luminosità <b>additivi</b> (I + b) non toccano i gradienti: la derivata di una costante è zero.</li>
<li>Cambi di contrasto <b>moltiplicativi</b> (a·I) scalano tutti i moduli dei gradienti allo stesso modo: SIFT <b>normalizza il vettore a norma unitaria</b> e il fattore sparisce.</li>
<li>Effetti non lineari (saturazione della camera in zone chiare, luci non uniformi) possono creare pochi gradienti enormi: si fa <b>clipping</b> a 0.2 dopo la normalizzazione, poi si <b>rinormalizza</b>.</li>
</ul>
<p>Risultato: robustezza ai cambi affini di intensità (a·I + b) e ad artefatti di saturazione localizzati.</p>
<div class="box k"><b>Da saper spiegare</b><p>Il clipping sposta il peso dai moduli (sensibili alla luce) alla <b>distribuzione delle orientazioni</b>, più stabile. Nessun singolo gradiente può dominare il vettore.</p></div>
""")

s(72, "Example: SIFT", """
<p><b>Figura:</b> la stessa di slide 10 (opencv.org), ora leggibile: cerchi = keypoint, raggio = scala σ, segmento = orientazione dominante.</p>
<p>Si notano i cerchi grandi su strutture grandi (finestre, archi) e i piccoli sulle decorazioni fini: è la selezione di scala in azione.</p>
""")

s(73, "Summary of Invariance Properties", """
<p>Tabella della slide, invarianza → meccanismo:</p>
<ul>
<li><b>Scala</b> → estremi della DoG nello scale-space, σ memorizzata per ogni keypoint.</li>
<li><b>Rotazione</b> → orientazione dominante stimata e usata per allineare la patch.</li>
<li><b>Illuminazione (additiva)</b> → i gradienti ignorano gli offset costanti.</li>
<li><b>Illuminazione (contrasto)</b> → normalizzazione a norma unitaria del descrittore.</li>
<li><b>Rumore di localizzazione</b> → raffinamento sub-pixel quadratico.</li>
<li><b>Instabilità sui bordi</b> → scarto basato sull'hessiana.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Ricostruire questa tabella a memoria. Aggiungi mentalmente la traslazione: il descrittore è calcolato in un sistema di riferimento centrato sul keypoint. Cosa SIFT <b>non</b> gestisce: forti cambi di prospettiva (trasformazioni affini/proiettive della patch) e texture ripetitive.</p></div>
""")

s(74, "Toward Matching", "<p>Un confronto sperimentale fra Harris e SIFT su una coppia di immagini.</p>", kind="div", sec=("l8-matching", "Verso il matching", "slide 74–78"))

s(75, "Data", """
<p><b>Figura:</b> "Viewpoint change: camera panned between the two shots". Due foto (image A e image B) di un lungofiume con un veliero a sinistra, edifici bassi e un campanile con guglia dorata, riflessi nell'acqua. Tra le due la camera ha ruotato (panning): il veliero esce quasi dall'inquadratura in B.</p>
""")

s(76, "Harris Corners on the Pair", """
<p><b>Figura:</b> angoli di Harris rilevati indipendentemente in ciascuna immagine: 79 in A, 70 in B (cerchi rossi), concentrati su veliero, edifici della riva e riflessi.</p>
<p>Tutti i cerchi hanno la stessa dimensione: Harris lavora a una sola scala.</p>
<p><i>La didascalia dice "Harris edge detector": si intende corner detector.</i></p>
""")

s(77, "SIFT Keypoints", """
<p><b>Figura:</b> 500 keypoint SIFT per immagine; cerchio = scala, segmento = orientazione.</p>
<ul>
<li>I keypoint SIFT compaiono a <b>molte scale diverse</b>: cerchi piccoli sulle texture fini, cerchi grandi sulla guglia e sul veliero.</li>
<li>Gli angoli di Harris sono tutti alla stessa dimensione di finestra.</li>
</ul>
""")

s(78, "Repeatability", """
<ul>
<li><b>Ripetibilità</b> = frazione di keypoint dell'immagine 1 che hanno un keypoint corrispondente corretto, rilevato vicino alla posizione giusta nell'immagine 2.</li>
<li>SIFT ha ripetibilità più alta di Harris semplice ai cambi di scala, e comparabile o migliore a cambi di vista moderati, grazie alla normalizzazione di scala e orientazione.</li>
<li>Entrambi peggiorano con cambi di vista estremi e texture ripetitive.</li>
</ul>
<div class="box b"><b>Dal libro · Szeliski cap. 7, § 7.1.1 Feature detectors</b><p>Il libro riporta il criterio di valutazione di Schmid, Mohr e Bauckhage (2000): si misura la ripetibilità come frazione di punti ritrovati entro ε pixel dopo aver mappato le posizioni con la trasformazione nota, e l'<b>information content</b> dei descrittori locali. In quel confronto la versione "migliorata" di Harris, con derivate di gaussiana, risultava la più ripetibile. <a href="https://szeliski.org/Book/">szeliski.org/Book</a></p></div>
""")

s(79, "Conclusions", "<p>Chiusura della lezione.</p>", kind="div", sec=("l8-conclusioni", "Conclusioni", "slide 79–84"))

s(80, "SIFT vs Learned Methods", """
<p><b>SIFT</b>:</p>
<ul>
<li>interpretabile e molto facile da usare;</li>
<li>un modello pulito dell'invarianza tramite <b>normalizzazione</b>;</li>
<li>un baseline forte per i task di geometria sparsa.</li>
</ul>
<p>Le pipeline moderne apprese (SuperPoint, LightGlue, …) riusano spesso la stessa astrazione modulare: <b>detect, describe, match, verify</b>.</p>
""")

s(81, "The Matching Pipeline", """
<p>Pipeline completa per trovare corrispondenze fra due immagini:</p>
<ol>
<li>rilevare i keypoint con posizione, scala e orientazione;</li>
<li>calcolare i descrittori;</li>
<li><b>(mancante)</b> matching: nearest neighbor fra descrittori e <b>ratio test di Lowe</b>; dopo il matching vanno eliminati alcuni punti (occlusioni, match scadenti, …);</li>
<li><b>(mancante)</b> stima geometrica e verifica: <b>DLT</b> e <b>RANSAC</b>.</li>
</ol>
<p>I passi "missing" sono il tema della lezione successiva.</p>
<div class="box b"><b>Dal libro · visionbook cap. 41 Homographies, § 41.3</b><p>Il visionbook non ha un capitolo sui keypoint, ma nel capitolo sulle omografie usa proprio questa pipeline per i panorami (§ 41.3 Creating Image Panoramas): le corrispondenze iniziali vengono da un detector/descrittore (SURF, parente veloce di SIFT), l'omografia si stima con la DLT da almeno 4 coppie (§ 41.3.1) e i match sbagliati si eliminano con RANSAC (§ 41.3.2), dove il numero di iterazioni è k = log(1 − p)/log(1 − w<sup>n</sup>). Utile da leggere come anteprima. <a href="https://visionbook.mit.edu/homography.html">visionbook.mit.edu/homography.html</a></p></div>
""")

s(82, "Key Takeaways", """
<ul>
<li><b>Harris</b> rileva gli angoli con i gradienti locali (matrice A), li classifica con gli autovalori, approssimati da det e trace.</li>
<li>L'<b>invarianza di scala</b> viene dalla ricerca di estremi nello scale-space (LoG/DoG).</li>
<li><b>SIFT</b> = detection DoG + raffinamento sub-pixel + scarto di bordi e basso contrasto + descrittore a istogrammi di gradienti normalizzato in orientazione.</li>
<li>Con detection e descrizione stabili, molti problemi si riducono alle corrispondenze: rilevare punti ripetibili, descriverli in modo distintivo, accoppiarli.</li>
</ul>
""")

s(83, "Further Reading", """
<ul>
<li>D. Lowe, "Distinctive Image Features from Scale-Invariant Keypoints", IJCV 2004: il paper di SIFT, molto leggibile; i dettagli numerici (σ = 1.6, soglia 0.03, r = 10, 36 bin, 80%, clipping 0.2) vengono da lì.</li>
<li>Szeliski, <i>Computer Vision: Algorithms and Applications</i> (2a ed.), § 7.1 Points and patches. Vedi la sezione "Studia dal libro" in fondo alla pagina.</li>
</ul>
""")

s(84, "Next Lecture: Matching, RANSAC, Homographies", """
<ul>
<li>Dati keypoint e descrittori di due (o più) immagini, come si trovano le corrispondenze <b>corrette</b>?</li>
<li>Matching del nearest neighbor sui descrittori, e perché una soglia sulla distanza non basta (match ambigui, texture ripetitive).</li>
<li><b>RANSAC</b>: stima robusta di un modello geometrico (es. un'omografia) ignorando i match outlier.</li>
<li>Caso d'uso: stitching di immagini e panorami.</li>
</ul>
""")
