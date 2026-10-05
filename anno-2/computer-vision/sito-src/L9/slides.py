
s(1, "Copertina", """
<p><b>Homographies and Image Panoramas</b>, sottotitolo <i>Matching, RANSAC, Homographies</i>. Nona lezione (1 ottobre 2026).</p>
<p>È la continuazione diretta di L8: lì si sono trovati keypoint e descrittori (Harris, SIFT); qui li si <b>accoppia</b> fra due immagini e si usano le coppie per stimare la trasformazione geometrica che le allinea, fino a costruire un <b>panorama</b>.</p>
<p>Strumenti nuovi: coordinate omogenee, omografia, stima robusta con RANSAC. Strumenti ripresi: descrittore SIFT (L8), interpolazione (L6), blending multi-banda (L6).</p>
""")

s(2, "Roadmap", "<p>Il problema dei panorami e la pipeline completa.</p>", kind="div", sec=("l9-intro", "Panorami e pipeline", "slide 2–8"))

s(3, "Image Panoramas", """
<p><b>Figura:</b> in alto tre foto scattate in sequenza dallo stesso punto, ruotando la camera: un fiume con lastre di ghiaccio, un veliero a sinistra, un campanile a guglia al centro, palazzi sulla riva. In basso il <b>panorama</b> ottenuto cucendo le tre foto in un'unica immagine molto larga.</p>
<ul>
<li>Il bordo del panorama è curvo e con zone nere: le immagini, una volta deformate nel sistema di riferimento comune, non sono più rettangoli allineati.</li>
<li>Le giunzioni non si vedono: oltre all'allineamento geometrico serve un <b>blending</b> delle zone sovrapposte.</li>
</ul>
<p>È l'obiettivo concreto della lezione: capire ogni passo che porta dalle tre foto all'immagine in basso.</p>
""")

s(4, "Recap: Detectors and Descriptors", """
<ul>
<li><b>Keypoint detector</b>: trova punti ripetibili (L8).</li>
<li><b>SIFT</b>: keypoint invarianti alla scala + descrittore a <b>128 dimensioni</b> (istogrammi di gradienti su 4×4 celle × 8 orientazioni).</li>
<li>Ogni keypoint porta con sé <b>posizione</b>, <b>scala</b>, <b>orientazione</b> e il <b>vettore descrittore</b>.</li>
</ul>
<p><b>Figura:</b> la prima foto del panorama con i keypoint SIFT disegnati in verde: si addensano sul veliero, sulla guglia e lungo la riva, quasi nessuno nel cielo e sull'acqua liscia.</p>
""")

s(5, "Today: From Descriptors to Correspondences", """
<ul>
<li>Due insiemi: {(p<sub>i</sub>, d<sub>i</sub>)} dall'immagine A e {(q<sub>j</sub>, e<sub>j</sub>)} dall'immagine B (p, q posizioni; d, e descrittori).</li>
<li><b>Matching</b>: trovare coppie (i, j) tali che d<sub>i</sub> ed e<sub>j</sub> descrivano lo <b>stesso punto della scena</b>.</li>
<li>Match corretti = <b>inlier</b>; match sbagliati = <b>outlier</b>.</li>
<li>I match buoni servono poi a stimare la trasformazione geometrica fra le due immagini.</li>
</ul>
<p><b>Figura:</b> due foto affiancate con linee colorate che collegano i keypoint accoppiati; le linee sono quasi orizzontali e parallele, come ci si aspetta per una camera che ruota.</p>
<p>Nota: la slide scrive "rigid transformation", ma l'omografia non è rigida (vedi l'Attenzione alla slide 32).</p>
""")

s(6, "Roadmap", """
<p>La <b>pipeline completa</b> dei panorami, che fa da indice alla lezione:</p>
<ol>
<li><b>Detection e descrizione</b> dei keypoint: SIFT (L8).</li>
<li><b>Matching dei descrittori</b>: nearest neighbor e ratio test di Lowe.</li>
<li><b>Stima robusta</b>: RANSAC.</li>
<li><b>Omografie</b>: definizione e stima con la DLT.</li>
<li><b>Warp</b>: deformare un'immagine nel riferimento dell'altra (e fonderle).</li>
</ol>
<p>Nella pratica RANSAC e DLT lavorano insieme: RANSAC chiama la DLT su campioni minimi di 4 coppie.</p>
""")

s(7, "Missing Match: Occlusions", """
<p><b>Figura:</b> la stessa facciata di una casa con un'auto scura parcheggiata; nella seconda foto un furgone bianco in movimento copre gran parte dell'auto e della facciata.</p>
<ul>
<li>I keypoint dell'auto e del portone visibili nella prima foto <b>non hanno un corrispondente</b> nella seconda: sono coperti.</li>
<li>Un matcher "ingenuo" assegna comunque a ognuno il descrittore più vicino, producendo un <b>match sbagliato</b>.</li>
</ul>
<p>Punto della slide: non ogni keypoint deve essere accoppiato; serve un criterio per <b>rifiutare</b> i match (ratio test, slide 14).</p>
""")

s(8, "Bad Match: Repeated Structures", """
<p><b>Figura:</b> una staccionata bianca di assi tutte uguali davanti all'erba.</p>
<ul>
<li>Ogni punta di asse è un ottimo angolo (Harris lo rileva, L8), ma i descrittori delle punte sono <b>quasi identici</b>.</li>
<li>Il descrittore più vicino può essere quello di un'asse vicina: match <b>ambiguo</b>, spesso sbagliato di un "periodo".</li>
</ul>
<p>È lo stesso esempio della staccionata visto in L8 (distintività): qui si vede la conseguenza sul matching.</p>
""")

s(9, "Descriptor Matching", "<p>Dai descrittori alle coppie candidate.</p>", kind="div", sec=("l9-matching", "Matching dei descrittori", "slide 9–18"))

s(10, "Matching", """
<ul>
<li>Abbiamo due immagini A e B, con keypoint e descrittori già estratti:
<ul><li>A: {(p<sub>i</sub>, d<sub>i</sub>)}, p<sub>i</sub> posizione, d<sub>i</sub> descrittore;</li>
<li>B: {(q<sub>j</sub>, e<sub>j</sub>)}.</li></ul></li>
<li><b>Matching</b>: trovare le coppie (i, j) che descrivono lo stesso punto della scena.</li>
<li>Bisogna separare i match buoni (<b>inlier</b>) da quelli sbagliati (<b>outlier</b>).</li>
</ul>
<p>Il matching lavora <b>solo sui descrittori</b>, senza guardare la geometria; la geometria entra dopo, con RANSAC.</p>
""")

s(11, "Nearest-Neighbor Matching", """
<p><b>Idea base</b>: il descrittore più vicino è il match corretto. Per ogni d<sub>i</sub> di A si cerca il <b>nearest neighbor</b> in B:</p>
<span class="f">j* = argmin<sub>j</sub> ‖d<sub>i</sub> − e<sub>j</sub>‖<sub>2</sub></span>
<ul>
<li>Si ottiene un insieme di coppie candidate (i, j*), <b>una per ogni keypoint di A</b>.</li>
<li><b>Problema</b>: ogni descrittore viene accoppiato, anche quando il vero corrispondente non esiste (occlusione, slide 7) o il match è scadente.</li>
</ul>
<div class="box x"><b>Approfondimento: costo della ricerca</b><p>La ricerca esaustiva costa O(N<sub>A</sub>·N<sub>B</sub>·D) con D = 128: con migliaia di keypoint per immagine è già pesante. Si usano strutture per la ricerca approssimata dei vicini (k-d tree con best-bin-first in Lowe 2004, FLANN in OpenCV) che trovano il vicino giusto quasi sempre a una frazione del costo.</p></div>
""")

s(12, "Distance Metrics", """
<ul>
<li><b>Distanza euclidea</b> ‖d<sub>i</sub> − e<sub>j</sub>‖<sub>2</sub>: standard per descrittori a valori reali (SIFT, descrittori appresi).</li>
<li><b>Distanza di Hamming</b> ‖d<sub>i</sub> ⊕ e<sub>j</sub>‖<sub>0</sub>: numero di bit diversi, per <b>descrittori binari</b> (ORB, BRIEF, BRISK).
<ul><li>Si calcola con uno XOR e un popcount: velocissima.</li></ul></li>
<li>La metrica deve essere quella adatta al tipo di descrittore.</li>
</ul>
<p>⊕ è lo XOR bit a bit; la "norma 0" conta le componenti non nulle, cioè i bit in cui i due descrittori differiscono.</p>
""")

s(13, "Ambiguity in Matching", """
<ul>
<li>Molte regioni si somigliano (finestre, erba, muri di mattoni): anche il nearest neighbor nello spazio dei descrittori può essere sbagliato.</li>
<li><b>Idea</b>: un buon match è <b>vicino</b> a d<sub>i</sub> e <b>non troppo vicino a nessun altro</b> descrittore.</li>
<li>Un match cattivo ha un primo vicino quasi alla stessa distanza del secondo.</li>
</ul>
<div class="box k"><b>Perché la distanza assoluta non basta</b><p>Una soglia fissa su ‖d<sub>i</sub> − e<sub>j*</sub>‖ funziona male: alcuni descrittori sono molto distintivi e hanno match corretti anche a distanza relativamente grande, altri sono in zone ripetitive e hanno match sbagliati a distanza piccola. Conta il <b>contrasto</b> fra il primo e il secondo vicino, non la distanza in sé.</p></div>
""")

s(14, "Lowe's Ratio Test", """
<p><b>Intuizione</b>: se il primo vicino è nettamente più vicino di tutti gli altri, probabilmente è il match vero.</p>
<ul>
<li>Per ogni d<sub>i</sub> si cercano i <b>due</b> vicini più prossimi: e<sub>j1</sub> (migliore) ed e<sub>j2</sub> (secondo).</li>
<li>Si accetta il match solo se:</li>
</ul>
<span class="f">‖d<sub>i</sub> − e<sub>j1</sub>‖ / ‖d<sub>i</sub> − e<sub>j2</sub>‖ &lt; τ</span>
<ul><li>Nel notebook τ = 0.75, scelta comune.</li></ul>
<div class="box b"><b>Dalla fonte · Lowe 2004, § 7.1 Keypoint matching</b><p>Lowe motiva il test così: il secondo vicino fornisce una stima della densità di match sbagliati in quella zona dello spazio dei descrittori. Per un match corretto il primo vicino è molto più vicino di qualunque falso; per un match sbagliato molti descrittori falsi sono a distanze simili. Nel suo esperimento con soglia <b>0.8</b> si elimina circa il 90% dei match falsi scartando meno del 5% di quelli corretti. In Szeliski il criterio si chiama <b>NNDR</b> (nearest neighbor distance ratio), cap. 7, § 7.1.3 Feature matching.</p></div>
<div class="box x"><b>Approfondimento: occlusioni e repliche</b><p>Il test risolve i due casi delle slide 7–8. Occlusione: il vero match non c'è, primo e secondo vicino sono entrambi casuali e a distanze simili, rapporto vicino a 1, scartato. Staccionata: ci sono più descrittori quasi uguali, rapporto vicino a 1, scartato (si perde il punto, ma si evita un errore).</p></div>
""")

s(15, "Choosing the Ratio Threshold", """
<ul>
<li><b>Precision</b>: frazione di match corretti fra quelli trovati.</li>
<li><b>Recall</b>: frazione dei match corretti esistenti che vengono trovati.</li>
<li><b>τ piccola</b> (es. 0.6): precision più alta, match più pochi ma affidabili; si usa quando si tollerano pochi outlier.</li>
<li><b>τ grande</b> (es. 0.9): recall più alto, più match ma anche più outlier; utile quando la scena ha pochi keypoint e non si vuole perderne.</li>
</ul>
<p><b>In pratica</b>:</p>
<ul>
<li>τ si tara per il compromesso precision/recall voluto; partire da 0.75 va bene in molte applicazioni (panorami).</li>
<li>Dipende dalla scena (quanti keypoint, quanto affidabili) e dall'applicazione: nei video i frame consecutivi sono molto simili; in altre applicazioni A e B possono essere molto diverse.</li>
</ul>
<div class="box k"><b>Collegamento con RANSAC</b><p>Il ratio test e RANSAC si spartiscono il lavoro: un τ più largo lascia passare più outlier, che RANSAC dovrà eliminare con più iterazioni (slide 41: le iterazioni crescono rapidamente al calare della frazione di inlier w). Un τ troppo stretto può lasciare troppo poche coppie per stimare bene H.</p></div>
""")

s(16, "Mutual Nearest Neighbors", """
<ul>
<li><b>Mutual NN</b> (MNN): si accetta (i, j) solo se j è il NN di d<sub>i</sub> in B <b>e</b> i è il NN di e<sub>j</sub> in A (controllo nei due sensi, detto anche cross-check).</li>
<li>Elimina i match <b>molti-a-uno</b> (un punto di B scelto da molti punti di A).</li>
<li>Si combina con il ratio test per aumentare ancora la precision.</li>
<li>Abbassa un po' il recall ma riduce molto i falsi positivi.</li>
</ul>
<p>In OpenCV corrisponde all'opzione <code>crossCheck=True</code> del BFMatcher.</p>
""")

s(17, "Visual Inspection", """
<ul>
<li>Disegnando tutti i match NN su una coppia tipica si vedono molti errori evidenti:
<ul><li>linee che attraversano l'immagine in diagonale;</li>
<li>gruppi di linee parallele (corrette) mescolati a linee sparse che si incrociano (sbagliate).</li></ul></li>
<li>Dopo il ratio test restano soprattutto linee parallele: insieme di corrispondenze molto più pulito.</li>
<li>Gli outlier residui li gestisce <b>RANSAC</b>.</li>
</ul>
<p><b>Figura:</b> la coppia di foto del panorama con i match dopo il ratio test: linee quasi tutte orizzontali e parallele, concentrate sulla riva e sulla guglia.</p>
<p>Perché parallele: con una camera che ruota poco attorno all'asse verticale, ogni punto si sposta di circa la stessa quantità in orizzontale.</p>
""")

s(18, "Recap", """
<ul>
<li>Abbiamo un insieme di match <b>robusto</b>: per (quasi) ogni keypoint di A sappiamo qual è il corrispondente in B.</li>
<li>Non è perfetto: i passi successivi devono essere robusti a rumore ed errori.</li>
<li>La quantità di rumore dipende dall'applicazione.</li>
</ul>
<p>Prossimo passo: quale <b>modello geometrico</b> lega le coordinate di A a quelle di B.</p>
""")

s(19, "Homographies", "<p>Il modello geometrico che lega due viste: l'omografia.</p>", kind="div", sec=("l9-omografie", "Omografie", "slide 19–27"))

s(20, "Viewpoint as a Change in Coordinates", """
<ul>
<li><b>Panorama</b>: cucire due immagini prese da un fotografo <b>fermo</b>.</li>
<li><b>Problema</b>: le immagini mostrano la stessa scena ma in <b>coordinate diverse</b>; per cucirle bisogna convertire le coordinate da A a B.</li>
<li>Scattando B il fotografo resta nello stesso punto e <b>ruota</b> la camera rispetto ad A.</li>
</ul>
<p>Riformulazione chiave: un cambio di punto di vista (senza traslazione) è solo un <b>cambio di coordinate</b> sul piano immagine, che si può scrivere come una funzione (x, y) → (x′, y′).</p>
""")

s(21, "Viewpoint as a Change in Coordinates", """
<p><b>Figura</b> (visionbook, cap. 41, fig. 41.4): a sinistra due piani immagine (verde, camera 1; rosso, camera 2) con lo <b>stesso centro ottico</b> nell'origine, il secondo ottenuto ruotando il primo di R. A destra la vista dall'alto: il raggio che parte dal centro e va al punto 3D (X, Y, Z) taglia il piano verde in (x, y) e il piano rosso in (x′, y′).</p>
<ul>
<li>Tutti i punti 3D sullo stesso raggio finiscono negli stessi (x, y) e (x′, y′): la corrispondenza <b>non dipende dalla profondità</b>.</li>
<li>Quindi esiste una mappa fra i due piani immagine valida per <b>qualunque</b> scena: è l'omografia.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 41, § 41.2.1 Camera Rotation</b><p>Il libro ricava la mappa in tre righe. Si mette il riferimento del mondo sulla camera 1: λ<sub>1</sub>[x, y, 1]<sup>⊤</sup> = K[X, Y, Z]<sup>⊤</sup>. La camera 2 è solo ruotata: λ<sub>2</sub>[x′, y′, 1]<sup>⊤</sup> = KR[X, Y, Z]<sup>⊤</sup>. Si ricava [X, Y, Z]<sup>⊤</sup> = λ<sub>1</sub>K<sup>−1</sup>[x, y, 1]<sup>⊤</sup> dalla prima e lo si sostituisce nella seconda:</p>
<span class="f">(λ<sub>2</sub>/λ<sub>1</sub>)[x′, y′, 1]<sup>⊤</sup> = K R K<sup>−1</sup> [x, y, 1]<sup>⊤</sup>,   cioè H = K R K<sup>−1</sup></span>
<p>La profondità sparisce (resta solo nel fattore di scala λ<sub>2</sub>/λ<sub>1</sub>, irrilevante in coordinate omogenee). Vale anche con intrinseci diversi: H = K<sub>2</sub>RK<sub>1</sub><sup>−1</sup>. K è la matrice degli intrinseci del cap. 39 (focale, punto principale). Verificato numericamente con punti 3D casuali. <a href="https://visionbook.mit.edu/homography.html" target="_blank">visionbook.mit.edu/homography.html</a></p></div>
<div class="box x"><b>Approfondimento: ruotare attorno a quale punto</b><p>La condizione esatta è che il <b>centro ottico</b> resti fermo. Se si ruota la fotocamera tenendola in mano, il centro ottico trasla un po': per oggetti lontani l'errore è trascurabile, per oggetti vicini compare la <b>parallasse</b> (ghosting nel panorama). Per questo nei panorami professionali si usa una testa panoramica che ruota attorno al centro di proiezione dell'obiettivo.</p></div>
""")

s(22, "Homography", """
<p><b>Notazione</b>: coordinate omogenee, il punto (x, y) si rappresenta come la terna [x, y, 1]<sup>⊤</sup>.</p>
<p><b>Definizione</b>: un'<b>omografia</b> (trasformazione proiettiva) è una trasformazione geometrica che <b>preserva le rette</b>.</p>
<ul>
<li>Nei panorami si cuciono immagini legate da un'omografia.</li>
<li>Data p′ = h(p): se i punti p<sub>1</sub>, p<sub>2</sub>, p<sub>3</sub> sono allineati, anche h(p<sub>1</sub>), h(p<sub>2</sub>), h(p<sub>3</sub>) lo sono.</li>
<li>Qui un'omografia è sempre una mappa <b>da piano 2D a piano 2D</b>: non servono ancora le coordinate 3D.</li>
</ul>
<p><b>Figura</b> (visionbook, fig. 41.2): una griglia regolare e la sua immagine tramite un'omografia: le righe restano rette, ma le parallele convergono e i quadrati diventano trapezi.</p>
<div class="box w"><b>Attenzione: la collinearità va detta su tre punti</b><p>La slide scrive "se p<sub>1</sub>, p<sub>2</sub> sono collineari, h(p<sub>1</sub>), h(p<sub>2</sub>) sono collineari": due punti sono sempre allineati, quindi la frase non dice nulla. La proprietà corretta (come nel libro) riguarda <b>tre</b> punti: p<sub>1</sub>, p<sub>2</sub>, p<sub>3</sub> allineati ⇒ Hp<sub>1</sub>, Hp<sub>2</sub>, Hp<sub>3</sub> allineati. Equivalente: l'immagine di una retta è una retta.</p></div>
<div class="box b"><b>Dal libro · cap. 41, § 41.2 e cap. 38, § 38.4</b><p>Dimostrazione in una riga con le rette omogenee. Una retta ax + by + c = 0 si scrive l<sup>⊤</sup>p = 0 con l = [a, b, c]<sup>⊤</sup>. Se p′ = Hp, allora l<sup>⊤</sup>p = l<sup>⊤</sup>H<sup>−1</sup>p′ = (H<sup>−⊤</sup>l)<sup>⊤</sup>p′ = 0: tutti i punti trasformati stanno sulla retta l′ = H<sup>−⊤</sup>l. Il cap. 38 aggiunge il test di collinearità: tre punti sono allineati se e solo se det[p<sub>1</sub> p<sub>2</sub> p<sub>3</sub>] = 0; poiché det[Hp<sub>1</sub> Hp<sub>2</sub> Hp<sub>3</sub>] = det H · det[p<sub>1</sub> p<sub>2</sub> p<sub>3</sub>], lo zero si conserva. Le omografie <b>non</b> conservano angoli, lunghezze, parallelismo. <a href="https://visionbook.mit.edu/homogeneous_coordinates.html" target="_blank">visionbook.mit.edu/homogeneous_coordinates.html</a></p></div>
""")

s(23, "Example", """
<p>Anche quando la <b>scena è planare</b> si ottiene un'omografia.</p>
<p><b>Figura</b> (visionbook): due foto di uno scaffale di libri di visione (fra cui <i>The Retina</i>) prese da punti di vista diversi, la seconda molto di sbieco. I dorsi sono deformati in trapezi, ma i bordi dei libri e le righe dei titoli restano <b>rette</b>.</p>
<ul>
<li>Le coste dei libri stanno circa su un piano: due foto qualsiasi di quel piano sono legate da un'omografia, anche se la camera si è <b>spostata</b>.</li>
<li>È il secondo caso in cui vale il modello, oltre alla rotazione pura (riassunto alla slide 27).</li>
</ul>
<div class="box b"><b>Dal libro · cap. 41, § 41.2.2 Planar Surface</b><p>Si mette il riferimento del mondo sul piano, con Z = 0. La proiezione diventa λ[x, y, 1]<sup>⊤</sup> = K[R | t][X, Y, 0, 1]<sup>⊤</sup> = K[c<sub>1</sub> c<sub>2</sub> t][X, Y, 1]<sup>⊤</sup>, dove c<sub>1</sub>, c<sub>2</sub> sono le prime due colonne di R: la terza colonna viene moltiplicata per Z = 0 e sparisce. K[c<sub>1</sub> c<sub>2</sub> t] è una 3×3: il piano del mondo e il piano immagine sono legati da un'omografia. Fra due camere che guardano lo stesso piano la mappa è H<sub>2</sub>H<sub>1</sub><sup>−1</sup>, ancora un'omografia. Il libro nota che è un vincolo più forte del vincolo epipolare, ma vale solo in questi due casi. <a href="https://visionbook.mit.edu/homography.html" target="_blank">visionbook.mit.edu/homography.html</a></p></div>
""")

s(24, "Mapping Points with an Homography H", """
<p>Dati H e un punto p = (x, y):</p>
<ol>
<li><b>Omogeneizzare</b>: p̃ = (x, y, 1)<sup>⊤</sup>.</li>
<li><b>Applicare</b> l'omografia: q̃ = H p̃.</li>
<li><b>De-omogeneizzare</b> (dividere per la terza componente): q = (q̃<sub>1</sub>/q̃<sub>3</sub>, q̃<sub>2</sub>/q̃<sub>3</sub>).</li>
</ol>
<div class="box k"><b>Da saper fare: un conto a mano</b><p>H = [[1, 0, 2], [0, 1, 0], [0.01, 0, 1]], p = (10, 5). p̃ = (10, 5, 1); Hp̃ = (12, 5, 1.1); q = (12/1.1, 5/1.1) ≈ (10.91, 4.55). Senza la divisione si otterrebbe (12, 5): sbagliato. È la divisione per q̃<sub>3</sub> a rendere la mappa <b>non lineare</b> in coordinate cartesiane (e a far convergere le parallele).</p></div>
<div class="box b"><b>Dal libro · cap. 38, § 38.2 Homogeneous and Heterogeneous Coordinates</b><p>Un punto 2D (x, y) diventa [x, y, 1]<sup>⊤</sup>, e ogni multiplo non nullo [λx, λy, λ]<sup>⊤</sup> rappresenta lo <b>stesso</b> punto: geometricamente, tutti i punti di una retta per l'origine nello spazio omogeneo. Si torna alle coordinate cartesiane dividendo per l'ultima componente. Il libro avverte che in coordinate omogenee la somma di vettori non ha senso, conta solo la proporzionalità. <a href="https://visionbook.mit.edu/homogeneous_coordinates.html" target="_blank">visionbook.mit.edu/homogeneous_coordinates.html</a></p></div>
""")

s(25, "The Homography Matrix H", """
<ul>
<li>Un'omografia è una matrice <b>3 × 3</b>: q̃ = H p̃, H ∈ ℝ<sup>3×3</sup>.</li>
<li>Per via delle coordinate omogenee, H è definita <b>a meno di un fattore di scala</b>: H ≡ λH (λ ≠ 0).</li>
<li>In coordinate cartesiane:</li>
</ul>
<span class="f">x′ = (h<sub>11</sub>x + h<sub>12</sub>y + h<sub>13</sub>) / (h<sub>31</sub>x + h<sub>32</sub>y + h<sub>33</sub>),   y′ = (h<sub>21</sub>x + h<sub>22</sub>y + h<sub>23</sub>) / (h<sub>31</sub>x + h<sub>32</sub>y + h<sub>33</sub>)</span>
<ul>
<li>Poiché H è definita a meno di scala ha <b>8 gradi di libertà</b> (9 entrate meno 1 per la scala).</li>
<li>La slide rimanda alla lezione successiva per i dettagli su scala e conversione omogenee/cartesiane.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 38, § 38.3 2D Image Transformations</b><p>L'omografia è il gradino più generale di una gerarchia di trasformazioni, tutte scritte come matrici 3×3 in coordinate omogenee:</p>
<ul>
<li><b>traslazione</b> (2 gdl): conserva tutto tranne la posizione;</li>
<li><b>euclidea / rigida</b> (rotazione + traslazione, 3 gdl): conserva lunghezze e angoli;</li>
<li><b>similitudine</b> (+ scala uniforme, 4 gdl): conserva gli angoli;</li>
<li><b>affine</b> (ultima riga [0, 0, 1], 6 gdl): conserva il parallelismo;</li>
<li><b>proiettiva / omografia</b> (3×3 generica, 8 gdl): conserva solo le rette (collinearità).</li>
</ul>
<p>La differenza fra affine e omografia sta tutta nell'<b>ultima riga</b> (h<sub>31</sub>, h<sub>32</sub>): se sono zero il denominatore è costante e la mappa torna lineare. <a href="https://visionbook.mit.edu/homogeneous_coordinates.html" target="_blank">visionbook.mit.edu/homogeneous_coordinates.html</a></p></div>
""")

s(26, "Degrees of Freedom", """
<ul>
<li>H ha <b>8 gradi di libertà</b> → servono almeno <b>4 corrispondenze</b> (ognuna dà <b>2 equazioni</b>, una per x′ e una per y′).</li>
<li>Con esattamente 4 coppie in <b>posizione generale</b> (nessuna terna allineata) la soluzione è <b>unica</b>.</li>
<li>Con n &gt; 4 il sistema è sovradeterminato e si risolve ai <b>minimi quadrati</b> (DLT).</li>
</ul>
<div class="box k"><b>Da saper fare: contare i gradi di libertà</b><p>Incognite: 9 entrate − 1 scala = 8. Equazioni: 2 per coppia. Coppie minime: 8/2 = <b>4</b>. Stesso ragionamento per gli altri modelli: affine 6 gdl → 3 coppie; similitudine 4 gdl → 2 coppie; traslazione 2 gdl → 1 coppia. È anche la n che entra nella formula delle iterazioni di RANSAC (slide 41). Verificato con numpy: con 4 coppie generiche la matrice della DLT (8×9) ha rango 8 e la H vera si ritrova esattamente.</p></div>
""")

s(27, "Summary", """
<p><b>Quando due immagini sono legate da un'omografia</b>:</p>
<ul>
<li><b>Scena planare</b>: due viste qualsiasi di una superficie piana, comunque si muova la camera.</li>
<li><b>Rotazione pura</b> della camera (nessuna traslazione del centro ottico): qualunque scena.</li>
<li>Un'omografia è una matrice 3×3; il passo successivo è stimarla dai dati.</li>
</ul>
<p><b>Non tutto è un'omografia</b>: scena non planare (quasi tutte le scene 3D) <b>e</b> camera che trasla rompono il modello, perché punti a profondità diverse si spostano in modo diverso (parallasse).</p>
<div class="box k"><b>Da saper spiegare: perché la traslazione rompe il modello</b><p>Con la rotazione pura la corrispondenza dipende solo dal raggio, non dalla profondità (slide 21). Con una traslazione t, un punto a profondità Z si sposta nell'immagine di una quantità proporzionale a t/Z: punti vicini si spostano molto, punti lontani poco. Nessuna singola H può riprodurre spostamenti che dipendono da Z, a meno che tutti i punti abbiano una relazione fissa con la profondità, cioè stiano su un piano. Per oggetti molto lontani (t/Z ≈ 0) l'omografia resta una buona approssimazione anche con piccole traslazioni.</p></div>
""")

s(28, "Estimating a Homography: DLT", "<p>Stimare H dalle corrispondenze con la Direct Linear Transform.</p>", kind="div", sec=("l9-dlt", "Stima dell'omografia: DLT", "slide 28–29"))

s(29, "Recap", """
<ul>
<li>Abbiamo un insieme di corrispondenze fra keypoint di A e di B.</li>
<li>Abbiamo un modello che converte le coordinate di A in quelle di B (l'omografia).</li>
</ul>
<p><b>Prossimo passo</b>: stimare i parametri di H dalle corrispondenze con la <b>Direct Linear Transform (DLT)</b>, che da almeno 4 coppie restituisce una stima di H.</p>
<p>La slide rimanda i dettagli della DLT alle prossime lezioni e per oggi la tratta come una scatola nera. Il libro la spiega già qui: sotto la derivazione.</p>
<div class="box b"><b>Dal libro · cap. 41, § 41.3.1 Direct Linear Transform Algorithm</b><p>Da x′ = (h<sub>1</sub><sup>⊤</sup>p̃)/(h<sub>3</sub><sup>⊤</sup>p̃) e y′ = (h<sub>2</sub><sup>⊤</sup>p̃)/(h<sub>3</sub><sup>⊤</sup>p̃) (h<sub>k</sub><sup>⊤</sup> = riga k di H) si moltiplica per il denominatore e si porta tutto a sinistra: le equazioni diventano <b>lineari</b> nelle 9 entrate di H. Per una coppia (x, y) → (x′, y′):</p>
<span class="f">[ x  y  1  0  0  0  −x′x  −x′y  −x′ ] · h = 0<br>[ 0  0  0  x  y  1  −y′x  −y′y  −y′ ] · h = 0</span>
<p>Impilando N coppie si ottiene <b>A h = 0</b> con A di dimensione <b>2N × 9</b> e h = H scritta come vettore. Poiché la scala di h è arbitraria, si cerca il vettore di norma 1 che minimizza ‖Ah‖²: è l'<b>autovettore di A<sup>⊤</sup>A con autovalore minimo</b>, cioè l'ultimo vettore singolare destro della SVD di A. Il libro precisa che ‖Ah‖² è un errore <b>algebrico</b> senza significato geometrico: in pratica la DLT fornisce l'inizializzazione e poi si minimizza l'errore di riproiezione in pixel. <a href="https://visionbook.mit.edu/homography.html" target="_blank">visionbook.mit.edu/homography.html</a></p></div>
<div class="box k"><b>Da saper fare: la DLT passo per passo</b><p>1) Per ogni coppia scrivi le due righe di A. 2) Impila: A è 2N × 9. 3) SVD A = UΣV<sup>⊤</sup>; h = ultima colonna di V. 4) Rimodella h in 3×3. Con N = 4 in posizione generale A ha rango 8, il nucleo ha dimensione 1 e la soluzione è esatta (verificato con numpy). Con N &gt; 4 e rumore, il valore singolare minimo non è zero e h è la soluzione ai minimi quadrati (algebrici).</p></div>
<div class="box x"><b>Approfondimento: normalizzazione dei punti (Hartley)</b><p>Le righe di A mescolano termini come 1 e x′x ≈ 10<sup>5</sup>–10<sup>6</sup> (coordinate in pixel): il problema è numericamente mal condizionato. La DLT <b>normalizzata</b> trasla i punti di ogni immagine in modo che il baricentro sia nell'origine e li scala in modo che la distanza media dall'origine sia √2 (trasformazioni T e T′), stima H̃ sui punti normalizzati e poi torna indietro con H = T′<sup>−1</sup>H̃T. Prova numerica con 50 punti in un'immagine 2000×2000: il rapporto fra il primo e il penultimo valore singolare di A passa da circa 2·10<sup>7</sup> a circa 3. Riferimento: Hartley e Zisserman, <i>Multiple View Geometry</i>, cap. 4 (Estimation – 2D projective transformations), che il libro cita. Non è nelle slide ma è la versione da usare in pratica (OpenCV la applica internamente).</p></div>
""")

s(30, "Outliers and Robust Estimation", "<p>Perché i match sbagliati rovinano la stima e come difendersi.</p>", kind="div", sec=("l9-outlier", "Outlier e stima robusta", "slide 30–35"))

s(31, "Why Matching Produces Outliers", """
<ul>
<li><b>Pattern ripetitivi</b>: molte regioni identiche (finestre, piastrelle); il NN è ambiguo (slide 8).</li>
<li><b>Occlusioni</b>: un punto visibile in A non ha corrispondente in B, e il NN è per forza sbagliato (slide 7).</li>
<li><b>Cambi di illuminazione o di punto di vista</b>: il descrittore cambia abbastanza che il vero match non è più il NN.</li>
<li><b>Sfondo disordinato</b> (clutter): distrattori con descrittori simili per caso.</li>
</ul>
""")

s(32, "Inliers vs. Outliers", """
<p>Data una trasformazione geometrica dalle coordinate di A a quelle di B (es. un'omografia):</p>
<ul>
<li><b>Inlier</b>: un match (p<sub>i</sub>, q<sub>j</sub>) coerente con la trasformazione.</li>
<li><b>Outlier</b>: un match che la viola.</li>
</ul>
<ul>
<li>Non si sa a priori quali sono gli outlier: manca la ground truth.</li>
<li>Nelle pipeline reali gli outlier restano <b>anche dopo il ratio test</b>.</li>
</ul>
<p>Circolarità da notare: per sapere chi è inlier serve H, per stimare bene H servono solo gli inlier. RANSAC rompe il circolo.</p>
<div class="box w"><b>Attenzione: l'omografia non è una trasformazione rigida</b><p>La slide (e la slide 5) scrive "rigid geometric transformation (e.g. a homography)". <b>Rigida</b> (euclidea) significa solo rotazione + traslazione: conserva distanze e angoli, 3 gradi di libertà in 2D. L'omografia è la trasformazione più generale della gerarchia (8 gdl) e non conserva né distanze né angoli né parallelismo (cap. 38, § 38.3; cap. 41, § 41.2). La frase corretta è "data una trasformazione <b>geometrica parametrica</b> (es. un'omografia)".</p></div>
""")

s(33, "Outliers and Least Squares", """
<p><b>Problema</b>: la stima ottimizza un obiettivo ai <b>minimi quadrati</b>.</p>
<ul>
<li>Si minimizza ∑<sub>i</sub> r<sub>i</sub><sup>2</sup>, dove r<sub>i</sub> è il residuo del match i (distanza fra il punto predetto dall'omografia stimata e il punto vero).</li>
<li>Un solo residuo grande (outlier) può <b>dominare</b> la somma.</li>
<li>Anche con un solo outlier si può spostare la stima di quanto si vuole rendendolo abbastanza lontano.</li>
</ul>
<p><b>Conclusione</b>: i minimi quadrati <b>non sono robusti</b> agli outlier.</p>
<div class="box k"><b>Da saper spiegare: perché il quadrato</b><p>Il gradiente di r² rispetto ai parametri è 2r·∂r/∂θ: l'influenza di un punto cresce <b>linearmente</b> con il suo residuo, senza limite. Un punto a residuo 100 pesa come 100 punti a residuo 1. In termini statistici, i minimi quadrati sono la massima verosimiglianza per rumore gaussiano, che ha code sottilissime: un outlier è "impossibile" per il modello, e il modello si piega per spiegarlo. Il <b>breakdown point</b> dei minimi quadrati è 0: basta un punto per rovinare la stima.</p></div>
""")

s(34, "Example with 1D Regression", """
<p><b>Figura</b>: regressione lineare su circa 20 punti blu ben allineati (x da 0 a 10, y da 0 a 20), più un <b>unico outlier</b> arancione in (14, −10), lontano e fuori dall'intervallo delle x.</p>
<ul>
<li>Retta senza outlier (linea continua): y = 2.00x + 0.98, segue bene i dati.</li>
<li>Retta con l'outlier (tratteggiata): y = 0.72x + 6.06, pendenza ridotta a un terzo, sbagliata su tutti i punti buoni.</li>
</ul>
<p>Il titolo parla di outlier ad alta <b>leva</b> (high-leverage): un punto con x lontana dalla media delle x ha un braccio di leva grande sulla pendenza, e tira la retta verso di sé.</p>
""")

s(35, "Robust Estimation", """
<ul>
<li>Gli outlier sono pochi ma hanno un impatto sproporzionato.</li>
<li>Gli <b>stimatori robusti</b> limitano l'influenza dei singoli punti.</li>
<li><b>RANSAC</b> (RANdom SAmple Consensus): trova il più grande insieme di dati coerente con un modello. Componente molto diffuso nelle pipeline di visione.</li>
</ul>
<div class="box x"><b>Approfondimento: le alternative</b><p>Gli <b>M-stimatori</b> sostituiscono r² con una funzione ρ(r) che cresce meno (Huber, Cauchy, Tukey) e si risolvono con minimi quadrati ripesati iterativi (IRLS); servono una buona inizializzazione e funzionano con pochi outlier. La <b>mediana dei minimi quadrati</b> (LMedS) minimizza la mediana di r² e regge fino al 50% di outlier senza soglia. RANSAC è preferito in visione perché regge anche frazioni di outlier oltre il 50%, purché il modello minimo sia piccolo. Szeliski ne parla nel cap. 8, § 8.1 Pairwise alignment (parte sui minimi quadrati robusti e RANSAC).</p></div>
""")

s(36, "RANSAC", "<p>Random Sample Consensus: stima robusta per campionamento.</p>", kind="div", sec=("l9-ransac", "RANSAC", "slide 36–42"))

s(37, "RANSAC Motivation", """
<ul>
<li>Vogliamo stimare H da corrispondenze rumorose.</li>
<li>La DLT (minimi quadrati) è corrotta anche da pochi outlier.</li>
<li><b>RANSAC</b>: stimare <b>molte</b> omografie candidate e tenere quella sostenuta dal più grande <b>insieme di consenso</b> (inlier), ignorando completamente gli outlier.</li>
</ul>
<p>Idea rovesciata rispetto ai minimi quadrati: invece di usare tutti i dati e sperare che gli errori si compensino, si usano <b>meno dati possibili</b> per ogni ipotesi, così che almeno qualche ipotesi sia costruita solo da inlier.</p>
""")

s(38, "RANSAC Algorithm", """
<p>Ripeti N volte:</p>
<ol>
<li><b>Campiona</b>: estrai a caso il numero minimo di corrispondenze (4 per H).</li>
<li><b>Stima</b>: calcola H dal campione con la DLT.</li>
<li><b>Valuta</b>: conta gli inlier, cioè le coppie (p<sub>i</sub>, q<sub>i</sub>) con errore &lt; t (soglia).</li>
<li><b>Aggiorna</b>: tieni H se ha più inlier del migliore finora.</li>
</ol>
<p>Alla fine restituisci H* con più inlier e <b>ristimala con la DLT su tutti i suoi inlier</b>.</p>
<div class="box b"><b>Dal libro · cap. 41, § 41.3.2 Robust Model Fitting</b><p>Il libro presenta lo stesso schema in forma generale (Fischler e Bolles, 1981): scegli a caso il minimo numero di punti che determina il modello, calcola il modello, conta i punti entro la tolleranza ε, ripeti, tieni il modello con l'insieme di consenso più grande. Per le omografie: 4 coppie danno le 8 equazioni della DLT. <a href="https://visionbook.mit.edu/homography.html" target="_blank">visionbook.mit.edu/homography.html</a></p></div>
<div class="box k"><b>Da saper spiegare: perché il campione minimo</b><p>La probabilità che un campione di n coppie sia tutto di inlier è w<sup>n</sup>: decresce in fretta con n. Usare il minimo (4 per H) massimizza la probabilità di pescare un campione pulito. La precisione si recupera dopo, con la ristima su tutti gli inlier. Un dettaglio pratico: i campioni degeneri (tre punti allineati) si scartano subito, perché la DLT non dà una H unica (slide 51).</p></div>
""")

s(39, "Inlier/Outlier Model", """
<ul>
<li><b>Errore di trasferimento simmetrico</b>: d(q, Hp)² + d(p, H<sup>−1</sup>q)².</li>
<li>Oppure <b>errore di trasferimento in un verso</b>: d(q, Hp)² (proietta p con H e confronta con q).</li>
<li>Un match è <b>inlier</b> se l'errore di trasferimento è sotto la soglia t.</li>
<li>Soglia in pixel (es. t = 3–5 px) scelta in base al rumore atteso; nel notebook 4.0.</li>
</ul>
<p>d è la distanza euclidea in pixel fra punti già de-omogeneizzati. Quello simmetrico misura l'errore in entrambe le immagini, utile se le due immagini hanno scale diverse.</p>
<div class="box x"><b>Approfondimento: soglia sul quadrato o sulla distanza</b><p>Attenzione alle unità: se si confronta d² con t, t è in pixel², se si confronta d con t è in pixel. In OpenCV (<code>findHomography</code> con <code>RANSAC</code>) il parametro <code>ransacReprojThreshold</code> è una distanza in pixel sull'errore in un verso. Hartley e Zisserman suggeriscono di legare la soglia al rumore: con rumore gaussiano σ per coordinata, una soglia su d<sup>2</sup> di circa 5.99σ² (quantile 95% di una χ² a 2 gradi di libertà).</p></div>
""")

s(40, "Example", """
<p><b>Figura</b> (visionbook, fig. 41.8): RANSAC per adattare una <b>retta</b> (modello minimo: 2 punti) a 11 punti, di cui 2 outlier.</p>
<ul>
<li>(a) I dati: 9 punti quasi allineati in salita e 2 punti fuori.</li>
<li>(b) Due punti estratti a caso (rossi): la retta che li unisce scende ed ha solo <b>3 inlier</b>.</li>
<li>(c) Un'altra coppia: retta orizzontale, <b>4 inlier</b>.</li>
<li>(d) Coppia buona: retta in salita con <b>9 inlier</b> (azzurri).</li>
<li>(e) Altra coppia buona: <b>8 inlier</b>.</li>
<li>(f) Risultato: la retta ristimata con i minimi quadrati sui 9 inlier del modello migliore; i 2 outlier sono ignorati.</li>
</ul>
<p>Mostra il punto chiave: basta che <b>una</b> estrazione cada su due inlier perché il consenso la premi.</p>
""")

s(41, "Number of Iterations", """
<p>Sia w la frazione di inlier nei dati e n la dimensione del campione minimo (4 per H):</p>
<ul>
<li>w<sup>n</sup>: probabilità che un campione sia tutto di inlier;</li>
<li>1 − w<sup>n</sup>: probabilità che contenga almeno un outlier;</li>
<li>con k estrazioni, (1 − w<sup>n</sup>)<sup>k</sup>: probabilità che <b>tutte</b> contengano almeno un outlier.</li>
</ul>
<p>Se p è la probabilità desiderata di successo, 1 − p = (1 − w<sup>n</sup>)<sup>k</sup>, e prendendo il logaritmo:</p>
<span class="f">k = log(1 − p) / log(1 − w<sup>n</sup>)</span>
<p>Conclusione della slide: data una stima della frazione di outlier si sa quante iterazioni servono per avere probabilità p di trovare il modello giusto (stimato da soli inlier).</p>
<div class="box w"><b>Attenzione: p non è "la probabilità che tutti i punti siano inlier"</b><p>La slide definisce p come "the probability that all points are inliers", che è w<sup>n</sup> (riga sopra) e renderebbe la formula senza senso. Dall'equazione 1 − p = (1 − w<sup>n</sup>)<sup>k</sup>, p è la <b>probabilità che almeno uno dei k campioni sia composto solo da inlier</b>, cioè la confidenza desiderata di successo (tipicamente 0.99), come scrive anche la conclusione della slide stessa e il libro ("probability of selecting the correct model"). Inoltre k va arrotondato <b>per eccesso</b>.</p></div>
<div class="box k"><b>Da saper fare: i numeri (p = 0.99, calcolati con numpy)</b>
<ul>
<li>n = 4 (omografia): w = 0.9 → <b>5</b>; w = 0.8 → <b>9</b>; w = 0.7 → <b>17</b>; w = 0.5 → <b>72</b>; w = 0.3 → <b>567</b>.</li>
<li>n = 2 (retta): w = 0.5 → 17; n = 8 (matrice fondamentale): w = 0.5 → 1177.</li>
</ul>
<p>Due lezioni: k <b>non dipende dal numero di punti</b>, solo da w e n; e cresce in modo esplosivo con n quando w è basso, per questo si usa il campione minimo.</p></div>
<div class="box b"><b>Dal libro · cap. 41, § 41.3.2, e un refuso del libro</b><p>Il libro ricava la stessa formula (eq. 41.8) con w definita come "probabilità che un punto sia entro la tolleranza", cioè frazione di <b>inlier</b>, e p come probabilità di scegliere il modello corretto. Nell'esempio numerico sulla figura della slide 40 (2 outlier su 11) però scrive w = 0.18 e ottiene k = 91 con p = 0.95: 0.18 ≈ 2/11 è la frazione di <b>outlier</b>. Con la sua stessa definizione w = 9/11 ≈ 0.82 e k = log(0.05)/log(1 − 0.82²) ≈ 2.7, cioè <b>3</b> iterazioni. Ricontrollato con numpy: con w = 0.18 esce davvero 91, con w = 0.82 esce 2.7. Occhio a non copiare l'esempio del libro. <a href="https://visionbook.mit.edu/homography.html" target="_blank">visionbook.mit.edu/homography.html</a></p></div>
""")

s(42, "Trade-offs in RANSAC", """
<ul>
<li><b>Soglia t</b>: troppo piccola, si scartano inlier veri; troppo grande, si accettano outlier.</li>
<li><b>Numero di iterazioni N</b>: più iterazioni, più confidenza, ma più lento.</li>
<li><b>Frazione di outlier 1 − w</b>: secondo la slide RANSAC funziona bene sotto il 50%; con frazioni molto alte servono molte iterazioni o varianti più sofisticate.</li>
<li><b>Rifinitura finale</b>: ristimare sempre H da tutti gli inlier alla fine.</li>
</ul>
<div class="box x"><b>Approfondimento: il 50% non è un limite di RANSAC</b><p>Il 50% è il breakdown point di stimatori come LMedS, non di RANSAC. Per le omografie (n = 4) con 70% di outlier (w = 0.3) bastano circa 567 iterazioni per p = 0.99 (slide 41), un costo trascurabile; il problema vero nasce quando w è molto basso o n è grande. Le varianti citate dalla slide sono per esempio <b>PROSAC</b> (campiona prima i match con ratio migliore), <b>LO-RANSAC</b> (ottimizzazione locale del modello migliore), <b>MLESAC/MAGSAC</b> (punteggio basato sulla verosimiglianza invece del conteggio). In pratica si aggiorna anche k in modo <b>adattivo</b>: ogni volta che si trova un modello con più inlier si ristima w e si ricalcola k.</p></div>
""")

s(43, "Learned Matching", "<p>Matcher appresi con reti ad attenzione.</p>", kind="div", sec=("l9-learned", "Matching appreso", "slide 43–46"))

s(44, "Limitations of Classical Matching", """
<p>Ratio test + RANSAC funziona bene ma fallisce con:</p>
<ul>
<li><b>Cambi di vista estremi</b> (oltre circa 60°): i descrittori non si riconoscono più.</li>
<li><b>Zone poco testurizzate</b>: troppo pochi keypoint.</li>
<li><b>Pattern ripetitivi</b>: il ratio test non riesce a distinguere molti descrittori simili.</li>
<li><b>Immagini scure o rumorose</b>: il basso SNR degrada sia la detection sia la descrizione.</li>
</ul>
<p>Limite di fondo: ogni descrittore è calcolato e confrontato <b>da solo</b>, senza sapere dove sono gli altri keypoint.</p>
""")

s(45, "SuperGlue: Attention-Based Matching", """
<ul>
<li><b>SuperGlue</b> (Sarlin et al., 2020): il matching come problema di <b>assegnamento su grafo</b>.</li>
<li>Keypoint e descrittori delle due immagini sono i nodi di un grafo fra le due immagini.</li>
<li><b>Self-attention</b>: ogni descrittore viene raffinato con il contesto della propria immagine.</li>
<li><b>Cross-attention</b>: l'informazione passa fra le due immagini.</li>
<li>Molto migliore del matching classico nelle scene difficili (interni, poca luce).</li>
</ul>
<p><b>Vantaggi</b>: è addestrato su moltissime coppie di immagini e usa il <b>contesto</b> (i descrittori degli altri keypoint, tramite l'attenzione).</p>
<p><b>Figura</b> (dal paper): due immagini con le loro feature locali (da una CNN o da un detector classico) entrano in una rete a grafo con attenzione, il "middle-end" fra detector e stima della geometria; in uscita un assegnamento <b>parziale</b>: i punti senza corrispondente (occlusi) possono restare non accoppiati.</p>
<div class="box x"><b>Approfondimento: come si ottiene l'assegnamento</b><p>Dalla rete esce una matrice di punteggi fra tutti i keypoint di A e di B, con una riga e una colonna extra di "dustbin" per i punti senza corrispondente. L'algoritmo di Sinkhorn la normalizza in una matrice quasi doppiamente stocastica (trasporto ottimo): è la versione appresa e "morbida" del mutual NN (slide 16), che impone match uno-a-uno.</p></div>
""")

s(46, "LightGlue: Efficient Attention Matching", """
<ul>
<li><b>LightGlue</b> (Lindenberger et al., 2023): riprogetta SuperGlue per l'<b>efficienza</b>.</li>
<li><b>Profondità adattiva</b>: per le coppie facili esce prima, usando meno strati transformer.</li>
<li><b>Pruning</b> per confidenza: elimina durante l'inferenza i keypoint con bassa confidenza.</li>
<li>2–10× più veloce di SuperGlue con accuratezza simile o migliore.</li>
<li>Sta diventando il matcher appreso di riferimento per il tempo reale (github.com/cvg/lightglue).</li>
</ul>
<p><b>Figura</b> (repository LightGlue): una coppia "difficile", la porta con la quadriga vista da lontano al tramonto e la quadriga da vicino: linee verdi collegano molti punti corrispondenti; la rete si è fermata dopo 8 strati, 32.3 ms.</p>
<p>Collegamento con L8: SuperPoint fornisce detector e descrittore appresi, LightGlue il matcher.</p>
""")

s(47, "Full Pipeline", "<p>Mettere tutto insieme: dal match al panorama.</p>", kind="div", sec=("l9-pipeline", "Pipeline completa", "slide 47–49"))

s(48, "Pipeline Overview", """
<span class="f">detect → describe → match → RANSAC → DLT → warp</span>
<ul>
<li><b>Input</b>: due immagini I<sub>A</sub>, I<sub>B</sub> della stessa scena (planare o con sola rotazione).</li>
<li><b>Output</b>: un'immagine deformata I<sub>B′</sub> allineata al sistema di riferimento di I<sub>A</sub>.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 41, § 41.3.3 Image Stitching</b><p>Per più di due immagini il libro procede così: stima H fra ogni coppia di immagini adiacenti (DLT + RANSAC), sceglie come riferimento l'immagine <b>centrale</b>, compone le omografie per portare tutte le immagini nel suo riferimento (es. H<sub>1→3</sub> = H<sub>2→3</sub>H<sub>1→2</sub>), deforma tutte le immagini e fonde le zone sovrapposte. Scegliere il centro riduce la deformazione delle immagini ai bordi. Il libro non entra nei dettagli del blending. <a href="https://visionbook.mit.edu/homography.html" target="_blank">visionbook.mit.edu/homography.html</a></p></div>
""")

s(49, "Final Step: Warp and Compose", """
<ul>
<li><b>Warping inverso</b>: per ogni pixel (x′, y′) dell'output si calcola la posizione corrispondente in I<sub>B</sub> e si campiona lì.
<ul><li>Evita i <b>buchi</b> (il warping diretto può lasciare pixel dell'output non raggiunti).</li>
<li>Si usa l'<b>interpolazione bilineare</b> per la precisione sub-pixel.</li>
<li>Warping diretto e inverso saranno ripresi nelle prossime lezioni.</li></ul></li>
<li>Si compongono I<sub>A</sub> e I<sub>B′</sub> con un <b>blending</b>, ad esempio il blending multi-scala della lezione sulle piramidi (L6).</li>
</ul>
<div class="box w"><b>Attenzione: H o H<sup>−1</sup> dipende dal verso di H</b><p>La slide scrive (x, y) = H<sup>−1</sup>(x′, y′), con (x′, y′) nel riferimento di I<sub>A</sub> e (x, y) in I<sub>B</sub>. Ma nella lezione H va da A a B: slide 20 ("convert coordinates from A to B") e slide 39 (errore d(q, Hp) con p in A, q in B). Con quella convenzione H porta già un punto del riferimento di A in B, quindi il warping inverso campiona I<sub>B</sub> in <b>H(x′, y′)</b>, non in H<sup>−1</sup>(x′, y′). La regola generale: il warping inverso usa la mappa <b>dall'output all'input</b>; è H<sup>−1</sup> solo se H è stata stimata da B ad A (come fa OpenCV quando si passa <code>findHomography(pts_B, pts_A)</code> e poi <code>warpPerspective</code>, che inverte internamente).</p></div>
<div class="box b"><b>Dal libro · cap. 38, § 38.5 Image Warping</b><p>Il libro confronta le due strategie. <b>Forward mapping</b>: ogni pixel di input viene spostato e arrotondato alla griglia di output: restano buchi e compare aliasing. <b>Backward mapping</b>: per ogni pixel di output si applica la trasformazione inversa M<sup>−1</sup> e si interpola l'input (bilineare, bicubica, Lanczos del cap. 21): nessun valore mancante. Per deformazioni che rimpiccioliscono molto si usa il MIP-mapping, cioè si campiona dal livello giusto di una piramide (L6). <a href="https://visionbook.mit.edu/homogeneous_coordinates.html" target="_blank">visionbook.mit.edu/homogeneous_coordinates.html</a></p></div>
<div class="box x"><b>Approfondimento: il compositing (Szeliski cap. 8, § 8.4 Compositing)</b><p>Dopo l'allineamento restano giunzioni visibili per differenze di esposizione, vignettatura, piccoli errori di registrazione e oggetti in movimento. Le soluzioni standard, in ordine di complessità: <b>feathering</b> (media pesata con peso che cresce verso il centro di ogni immagine, ottenuto dalla distance transform), scelta di una <b>cucitura</b> ottima che passi dove le immagini concordano (contro il ghosting), <b>blending multi-banda</b> di Burt e Adelson (L6: le basse frequenze si fondono su una zona larga, le alte su una zona stretta), blending nel dominio del gradiente (Poisson). Per panorami molto larghi si proietta su una superficie <b>cilindrica o sferica</b> invece che sul piano di un'immagine, perché l'omografia verso un piano esplode avvicinandosi a 90° dal riferimento.</p></div>
""")

s(50, "Conclusions", "<p>Configurazioni degeneri, riepilogo, letture.</p>", kind="div", sec=("l9-conclusioni", "Conclusioni", "slide 50–53"))

s(51, "Degenerate Configurations and Violated Assumptions", """
<ul>
<li>La <b>DLT fallisce con punti collineari</b>: H non è determinata univocamente.</li>
<li>L'omografia vale <b>solo</b> per scene planari o rotazione pura della camera.</li>
<li>La stessa pipeline si può usare con un <b>altro modello</b> di trasformazione: ad esempio OpenCV Stitcher supporta omografie (panorami) e trasformazioni affini (es. scansioni di documenti).</li>
</ul>
<div class="box k"><b>Da saper spiegare: quando è degenere</b><p>Per il campione minimo basta che <b>tre</b> dei quattro punti siano allineati: con numpy, tre punti su una retta danno una matrice A 8×9 di rango 7, cioè un nucleo di dimensione 2 e infinite H compatibili. Intuizione: tre punti allineati danno informazioni su una sola retta; il quarto non basta a fissare come si deforma il resto del piano. Con tante coppie il problema nasce se quasi tutti i punti stanno su una retta o se sono tutti ammassati in una zona piccola (H mal condizionata lontano da lì). Per questo è utile che i keypoint siano ben distribuiti (ANMS, L8).</p></div>
<div class="box x"><b>Approfondimento: scegliere il modello</b><p>Scansioni e foto prese da molto lontano: affine (6 gdl, 3 coppie). Scena planare o rotazione pura: omografia (8 gdl, 4 coppie). Scena 3D con camera che trasla: nessuna mappa punto-punto globale; si usa la geometria epipolare (matrice fondamentale, 7–8 coppie) e un punto corrisponde a una retta, non a un punto. Un modello più semplice del necessario lascia residui grandi; uno più complesso del necessario richiede più iterazioni di RANSAC e si adatta al rumore.</p></div>
""")

s(52, "Recap", """
<ul>
<li><b>Ratio test</b>: elimina i match ambigui confrontando il miglior vicino con il secondo.</li>
<li><b>Omografia H</b>: trasformazione proiettiva fra piani, 3×3 a meno di scala, stimata con la DLT.</li>
<li><b>RANSAC</b>: stima robusta tramite campionamento casuale e consenso.</li>
<li><b>Pipeline completa</b>: detect → describe → match → RANSAC/DLT → warp.
<ul><li>Una pipeline simile si usa in molte altre applicazioni (SfM, localizzazione, realtà aumentata, rettifica di documenti).</li></ul></li>
</ul>
""")

s(53, "Further Reading", """
<ul>
<li><b>Lowe</b>, <i>Distinctive Image Features from Scale-Invariant Keypoints</i>, IJCV 2004: ratio test e matching di SIFT (§ 7.1).</li>
<li><b>Visionbook, cap. 41</b> Homographies: <a href="https://visionbook.mit.edu/homography.html" target="_blank">visionbook.mit.edu/homography.html</a>.</li>
</ul>
<p>Per le basi (coordinate omogenee, gerarchia delle trasformazioni, warping) il cap. 38; per RANSAC, stitching e compositing più in dettaglio Szeliski cap. 8. Vedi la sezione Studia dal libro.</p>
""")
