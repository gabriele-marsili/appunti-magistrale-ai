s(1, "Copertina", """
<p><b>Camera Models and Calibration</b>. Dodicesima lezione (8 ottobre 2026).</p>
<p>È la seconda metà del discorso iniziato in L11: lì si è costruito il modello della camera, cioè la matrice <b>3×4</b> che porta un punto 3D del mondo in un pixel; qui si fa il percorso inverso, cioè la <b>calibrazione</b>: stimare quella matrice dalle immagini.</p>
<ul>
<li>Prima parte: quattro esempi concreti di matrici della camera, sempre più complicati, e la <b>linea dell'orizzonte</b>.</li>
<li>Seconda parte: la <b>DLT</b> per stimare la matrice (la stessa idea usata per l'omografia in L9), la scomposizione in K, R, T, l'errore di riproiezione.</li>
<li>Terza parte: il metodo multipiano di <b>Zhang</b> con la scacchiera e la calibrazione in pratica con OpenCV (notebook <code>camera_calibration_opencv</code>, in fondo alla pagina).</li>
</ul>
""")

s(2, "Motivation", "<p>Perché serve conoscere la matrice della camera.</p>", kind="div", sec=("l12-motivazione", "Motivazione", "slide 2–6"))

s(3, "Recap: Perspective Projection and Homogeneous Coordinates", """
<ul>
<li>In L11 le trasformazioni rigide (rotazioni e traslazioni) sono state scritte in <b>coordinate omogenee</b>.</li>
<li>Risultato: <b>ogni trasformazione diventa una matrice</b>, compresa la proiezione prospettica (a meno della divisione finale per la terza coordinata).</li>
<li>Comporre trasformazioni = moltiplicare matrici; invertirle = invertire matrici.</li>
</ul>
<p>È questo che rende possibili sia gli esempi della prima parte (si moltiplicano tre matrici e si legge il risultato) sia la calibrazione (si stima una sola matrice che contiene tutto).</p>
""")

s(4, "Recap: camera matrix P = K[R | −RT]", """
<ul>
<li>La trasformazione da coordinate 3D del mondo alla griglia dei pixel è una matrice <b>3×4</b>, P, da stimare.</li>
<li><b>Intrinseci</b> (K): legano piano immagine e sensore, cioè dipendono dall'hardware (focale, dimensione dei pixel, centro ottico).</li>
<li><b>Estrinseci</b> (R, T): posa della camera rispetto al mondo, cioè rotazione e traslazione.</li>
</ul>
<span class="f">P = K [R | −RT]</span>
<p>Lettura da destra a sinistra: si porta il punto nel riferimento della camera (prima si sottrae la posizione T del centro della camera, poi si ruota con R), quindi si proietta e si converte in pixel con K.</p>
<div class="box k"><b>Da saper fare</b><p>Spiegare perché compare −RT e non T: T è la <b>posizione del centro della camera nel mondo</b>, e il cambio di riferimento è P<sub>C</sub> = R(P<sub>W</sub> − T) = RP<sub>W</sub> − RT. Il titolo della slide scrive Rt minuscolo, il corpo RT: è la stessa cosa. Nel libro la matrice si chiama M; nelle slide si usano sia P sia M.</p></div>
""")

s(5, "Camera Calibration", """
<ul>
<li><b>Setup</b>: si scatta un insieme di foto che soddisfi condizioni sufficienti per una buona stima (quali, lo si vede nella terza parte: pose variate, copertura dell'immagine).</li>
<li><b>Calibrazione</b>: stimare la matrice P.</li>
<li><b>Profitto</b>: quasi tutti i compiti 3D richiedono di conoscere P (stereo e profondità, la prossima lezione; ricostruzione 3D, realtà aumentata, misure metriche da immagini).</li>
</ul>
""")

s(6, "Outline", """
<ol>
<li>Esempi di matrici della camera.</li>
<li>Direct Linear Transform (DLT).</li>
<li>Aspetti pratici della calibrazione.</li>
</ol>
""")

s(7, "Examples of Camera Views", "<p>Quattro pose della camera, dalla più semplice alla più generale, con la matrice scritta per esteso.</p>", kind="div", sec=("l12-esempi", "Esempi di matrici della camera", "slide 7–28"))

s(8, "Extrinsics Parameters", """
<p>Per passare dalle coordinate 3D del mondo alle coordinate 2D dell'immagine (in metri):</p>
<ol>
<li><b>traslare</b> il riferimento in modo che l'origine del mondo coincida con quella della camera;</li>
<li><b>ruotare</b> il riferimento in modo che gli assi coincidano.</li>
</ol>
<span class="f">P = K [R | −RT]</span>
<p>L'ordine conta: prima la traslazione, poi la rotazione. È per questo che nella matrice compare −RT (la traslazione viene ruotata).</p>
<div class="box b"><b>Dal libro · cap. 39, § 39.4 Camera-Extrinsic Parameters</b>
<p>Il libro scrive i due passi come due matrici 4×4 separate: <b>M<sub>1</sub></b> trasla (ultima colonna −T<sub>X</sub>, −T<sub>Y</sub>, −T<sub>Z</sub>), <b>M<sub>2</sub></b> ruota (blocco R 3×3, ultima riga [0 0 0 1]). Il prodotto è</p>
<span class="f">M<sub>2</sub>M<sub>1</sub> = [ R  −RT ; 0<sup>⊤</sup>  1 ],   P<sub>C</sub> = M<sub>2</sub>M<sub>1</sub>P<sub>W</sub></span>
<p>T è la posizione della camera nel mondo e gli assi della camera sono ruotati di R<sup>⊤</sup> rispetto a quelli del mondo; poiché R è ortonormale, R<sup>−1</sup> = R<sup>⊤</sup>. Il modello completo (§ 39.5) è λ[x, y, 1]<sup>⊤</sup> = K M<sub>2</sub> M<sub>1</sub> [X, Y, Z, 1]<sup>⊤</sup>: a destra gli estrinseci, a sinistra intrinseci e proiezione. <a href="https://visionbook.mit.edu/imaging_geometry.html" target="_blank">Cap. 39</a>.</p></div>
""")

s(9, "Examples of Camera Views", """
<p><b>Figura</b> (visionbook, fig. 39.10): le quattro pose degli esempi. In verde il riferimento del mondo (X<sub>w</sub>, Y<sub>w</sub>, Z<sub>w</sub>), in rosso la camera con i suoi assi (X<sub>c</sub>, Y<sub>c</sub>, Z<sub>c</sub>, tratteggiati).</p>
<ul>
<li><b>(a)</b> camera nell'origine del mondo, assi allineati.</li>
<li><b>(b)</b> camera alzata di h sopra l'origine, assi ancora allineati (asse ottico parallelo al suolo).</li>
<li><b>(c)</b> camera alta h e <b>inclinata</b> verso il basso di θ.</li>
<li><b>(d)</b> stessa camera di (c), ma l'origine del mondo è spostata di d sul suolo e il riferimento del mondo è girato (Z<sub>w</sub> punta verso la camera).</li>
</ul>
<p>Lo scopo è vedere come ogni ingrediente (traslazione, rotazione, scelta del riferimento del mondo) entra nella matrice.</p>
""")

s(10, "Example (a)", """
<p>Il caso più semplice: bastano le equazioni di proiezione.</p>
<ul>
<li>Camera nell'<b>origine</b> del mondo.</li>
<li><b>Assi allineati</b>: R = I, T = 0.</li>
<li>Centro dell'immagine (c<sub>x</sub>, c<sub>y</sub>) = (0, 0): le coordinate immagine si misurano dal centro.</li>
</ul>
<p><b>Figura:</b> la camera rossa nell'origine del riferimento verde, con Z<sub>w</sub> lungo l'asse ottico e Y<sub>w</sub> verso l'alto.</p>
""")

s(11, "Example (a)", """
<span class="f">M = K [ R  −RT ; 0<sup>⊤</sup>  1 ] = [a 0 0 0; 0 a 0 0; 0 0 1 0] · I<sub>4</sub> = [a 0 0 0; 0 a 0 0; 0 0 1 0]</span>
<ul>
<li>La matrice degli estrinseci è l'identità 4×4: resta solo K.</li>
<li>In coordinate cartesiane: <b>x = aX/Z</b>, <b>y = aY/Z</b>, la proiezione prospettica di L2 con la focale espressa in pixel.</li>
<li><b>Promemoria</b>: a = f N / w, con f focale.</li>
</ul>
<div class="box w"><b>Attenzione: w è la larghezza del sensore, non del pixel</b><p>La slide scrive "N number of pixels, w pixel width". Nel libro (§ 39.3.1) <b>w è la larghezza del sensore</b> in metri e N il numero di pixel lungo quella larghezza: N/w è il numero di pixel per metro, e a = f·N/w è la focale misurata in pixel. Se w fosse la larghezza di un pixel la formula corretta sarebbe a = f/w (senza N). Esempio del libro: focale 5.7 mm, sensore largo 7.6 mm, 4032 pixel → a = 4032 · 5.7/7.6 ≈ 3024.</p></div>
""")

s(12, "Example (b)", """
<p>Secondo scenario:</p>
<ul>
<li>una persona tiene la camera puntata <b>verso l'orizzonte</b>;</li>
<li>l'asse ottico è ancora <b>parallelo al suolo</b>;</li>
<li>gli assi sono allineati, ma c'è uno <b>spostamento verticale</b> di h (l'origine del mondo è sul suolo, sotto la camera).</li>
</ul>
<p><b>Figura:</b> la camera rossa alla quota h sulla verticale dell'origine verde; i suoi assi sono paralleli a quelli del mondo.</p>
""")

s(13, "Example (b)", """
<p>La slide mette a confronto (a) e (b). In (b) la camera sta in T = (0, h, 0) (la slide scrive T = (0, h), omettendo la componente Z nulla), R = I:</p>
<span class="f">M = [a 0 0 0; 0 a 0 0; 0 0 1 0] · [1 0 0 0; 0 1 0 −h; 0 0 1 0; 0 0 0 1] = [a 0 0 0; 0 a 0 −ah; 0 0 1 0]</span>
<ul>
<li>La matrice di traslazione ha −h nella seconda riga: si <b>sottrae</b> la posizione della camera.</li>
<li>Moltiplicando per K, il −h viene scalato in −ah.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Rifare il prodotto a mano: è un buon esercizio per l'orale. Verificato con sympy, insieme agli esempi (c) e (d).</p></div>
""")

s(14, "Example (b)", """
<p>Dalla matrice di (b), in coordinate cartesiane:</p>
<span class="f">x = a X / Z,   y = a (Y − h) / Z</span>
<ul>
<li>x non cambia rispetto a (a): la camera si è mossa solo in verticale.</li>
<li>y misura l'altezza del punto <b>rispetto alla camera</b> (Y − h), divisa per la profondità.</li>
<li>I punti alla stessa quota della camera (Y = h) finiscono in <b>y = 0</b>, a qualunque distanza.</li>
</ul>
""")

s(15, "Example (b): Horizon Line", """
<p><b>Figura a sinistra</b> (visionbook, fig. 39.11): un lungomare al tramonto, foto scattata con la camera orizzontale all'altezza degli occhi. Una riga rossa attraversa l'immagine a metà altezza: passa per la linea del mare e per le teste delle persone, sia vicine sia lontane.</p>
<p><b>Perché</b>: per Z → ∞ si ha y = a(Y − h)/Z → 0, quindi l'<b>orizzonte</b> è la riga centrale dell'immagine. In più, chi ha gli occhi alla stessa altezza della camera (Y = h) ha y = 0 a qualunque distanza: le teste delle persone di statura simile al fotografo stanno tutte sulla linea dell'orizzonte.</p>
<div class="box b"><b>Dal libro · cap. 39, § 39.6 A Few Concrete Examples</b><p>Il libro usa questo esempio come verifica "a occhio" del modello: con camera parallela al suolo all'altezza degli occhi, gli occhi delle persone di altezza simile si proiettano vicino alla metà dell'asse verticale. È un modo pratico per stimare l'altezza da cui è stata scattata una foto. <a href="https://visionbook.mit.edu/imaging_geometry.html" target="_blank">Cap. 39</a>.</p></div>
""")

s(16, "Example (c)", """
<ul>
<li>Ora la camera è anche <b>inclinata</b> verso il suolo di un angolo θ &gt; 0.</li>
<li>La rotazione è attorno all'asse <b>X<sub>c</sub></b>: X<sub>c</sub> resta fisso, Y<sub>c</sub> e Z<sub>c</sub> ruotano.</li>
</ul>
<p><b>Figura:</b> la camera alla quota h, con Y<sub>c</sub> inclinato in avanti di θ rispetto alla verticale tratteggiata e Z<sub>c</sub> (asse ottico) che punta in basso verso il suolo.</p>
""")

s(17, "Example (c)", """
<p>Matrice degli estrinseci: prima la traslazione di (b), poi la rotazione attorno a X:</p>
<span class="f">[R −RT; 0<sup>⊤</sup> 1] = [1 0 0 0; 0 cosθ sinθ 0; 0 −sinθ cosθ 0; 0 0 0 1] · [1 0 0 0; 0 1 0 −h; 0 0 1 0; 0 0 0 1]</span>
<span class="f">= [1 0 0 0; 0 cosθ sinθ −h cosθ; 0 −sinθ cosθ h sinθ; 0 0 0 1]</span>
<ul>
<li>L'ultima colonna è −RT = −R(0, h, 0)<sup>⊤</sup> = (0, −h cosθ, h sinθ).</li>
<li>La slide chiama "M<sub>2</sub>" il prodotto; nel libro M<sub>2</sub> è solo la rotazione e il prodotto è M<sub>2</sub>M<sub>1</sub>.</li>
</ul>
<div class="box k"><b>Da saper verificare: il segno della rotazione</b><p>Le righe di R sono gli assi della camera scritti nel riferimento del mondo. Terza riga (0, −sinθ, cosθ): Z<sub>c</sub> punta in avanti e <b>verso il basso</b> per θ &gt; 0, come nella figura. Seconda riga (0, cosθ, sinθ): Y<sub>c</sub> è inclinato in avanti. Se si sbaglia il segno dei seni, la camera guarda verso l'alto.</p></div>
""")

s(18, "Example (c)", """
<p>Si moltiplica per K (con c<sub>x</sub> = c<sub>y</sub> = 0):</p>
<span class="f">M = [a 0 0 0; 0 a 0 0; 0 0 1 0] · [R −RT; 0<sup>⊤</sup> 1] = [a 0 0 0; 0 a cosθ a sinθ −ah cosθ; 0 −sinθ cosθ h sinθ]</span>
<p>K moltiplica per a le prime due righe e lascia la terza: la terza riga di M è la terza riga degli estrinseci, cioè la <b>profondità del punto nel riferimento della camera</b>. È questa che finisce al denominatore.</p>
""")

s(19, "Example (c)", """
<p>Applicando M a [X, Y, Z, 1]<sup>⊤</sup> e dividendo per la terza componente:</p>
<span class="f">x = a X / ( sinθ (h − Y) + cosθ Z )</span>
<span class="f">y = a ( cosθ (Y − h) + sinθ Z ) / ( sinθ (h − Y) + cosθ Z )</span>
<ul>
<li>Il denominatore è la profondità lungo l'asse ottico inclinato: mescola la distanza orizzontale Z e il dislivello h − Y.</li>
<li>Formule verificate simbolicamente (sympy), coincidono con l'eq. 39.19 del libro.</li>
</ul>
""")

s(20, "Example (c)", """
<p>Due casi limite per controllare le formule:</p>
<ul>
<li><b>θ = 0</b>: sin = 0, cos = 1, si ritrova (b): x = aX/Z, y = a(Y − h)/Z.</li>
<li><b>θ = 90°</b> (camera che guarda in basso, verso il suolo): x = aX/(h − Y), y = aZ/(h − Y).
<ul><li>Sono le equazioni di proiezione standard x = aX/Z con i ruoli scambiati:</li>
<li><b>h − Y</b> (distanza dalla camera verso il basso) fa da profondità Z;</li>
<li><b>Z</b> fa da coordinata verticale Y.</li></ul></li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Controllare sempre una formula nuova sui casi limite: se θ = 0 non restituisce l'esempio precedente, c'è un errore di segno o di ordine.</p></div>
""")

s(21, "Example (c)", """
<p>Per θ qualunque la <b>linea dell'orizzonte</b> si ottiene mandando Z → +∞ (punti del suolo, o comunque a quota finita, sempre più lontani):</p>
<span class="f">y → a sinθ / cosθ = a tan θ</span>
<ul>
<li>Al numeratore e al denominatore domina il termine in Z; x → 0 per X finito, ma l'orizzonte è tutta la riga y = a tanθ.</li>
<li>Con la camera inclinata verso il basso (θ &gt; 0) l'orizzonte <b>sale</b> sopra il centro dell'immagine; con θ = 0 torna al centro.</li>
</ul>
""")

s(22, "Example (c)", """
<ul>
<li>Orizzonte in <b>y = a tan θ</b>.</li>
<li>Gli occhi delle persone della tua stessa altezza stanno sulla linea dell'orizzonte, <b>indipendentemente dalla distanza</b>.</li>
</ul>
<p><b>Figura</b> (visionbook, fig. 39.12): a sinistra il fotografo con la camera inclinata di θ alla quota h; il piano immagine è disegnato in rosso davanti alla camera, e il punto dove lo attraversa la retta orizzontale tratteggiata a quota h è segnato come "a tg(θ)". A destra due persone a distanze diverse: i loro occhi sono sulla stessa retta orizzontale tratteggiata, quindi nell'immagine finiscono sulla stessa riga; i raggi verdi verso i piedi arrivano invece in punti diversi.</p>
<p>Il motivo: un punto alla quota h della camera ha Y − h = 0, quindi y = a sinθ Z/(cosθ Z) = a tanθ per qualunque Z.</p>
""")

s(23, "Example (c)", """
<ul>
<li>L'orizzonte è in y = a tanθ, quindi:</li>
<li>noti l'orizzonte e a (camera già calibrata) si ricava l'<b>inclinazione</b> θ = arctan(y<sub>h</sub>/a);</li>
<li>noti l'orizzonte e θ si ricava <b>a</b>, cioè si calibra la focale.</li>
</ul>
<p><b>Figura</b> (visionbook, fig. 39.13): due foto di un viale alberato scattate con inclinazioni diverse. Le linee blu seguono i bordi del vialetto e si incontrano nel punto di fuga; la riga rossa orizzontale che passa per quel punto è l'orizzonte stimato. Nelle due foto l'orizzonte cade ad altezze molto diverse.</p>
<div class="box b"><b>Dal libro · cap. 39, § 39.6 e § 39.3.3</b><p>Il libro usa a ≈ 3103 pixel, ottenuto in § 39.3.3 con il metodo "semplice ma inaffidabile": una scacchiera di larghezza nota W a distanza nota Z, larga L pixel nella foto, dà a = Z·L/W. Con l'orizzonte a 1129 pixel dal centro si ottiene θ = arctan(1129/3103) ≈ 20°. È un esempio di <b>calibrazione parziale da un vincolo geometrico</b>, senza scacchiera: le rette parallele del suolo danno il punto di fuga, il punto di fuga dà l'orizzonte. <a href="https://visionbook.mit.edu/imaging_geometry.html" target="_blank">Cap. 39</a>.</p></div>
""")

s(24, "Example (d)", """
<p>Il riferimento della camera in (d) è lo stesso di (c), ma la <b>rotazione da applicare è diversa</b>: bisogna ruotare il riferimento del mondo (verde) su quello della camera (rosso), e in (d) il mondo è orientato diversamente.</p>
<p><b>Figura</b> (visionbook): (c) e (d) affiancati. In (d) l'origine del mondo è sul suolo a distanza d dalla verticale della camera, con <b>Z<sub>w</sub> che punta verso la camera</b> (verso sinistra) e X<sub>w</sub> verso l'osservatore: rispetto a (c) il mondo è girato di 180° attorno all'asse verticale.</p>
""")

s(25, "Example (d)", """
<p>La slide ripete il confronto e dice che servono due rotazioni:</p>
<ul>
<li>attorno a <b>X<sub>w</sub></b> di θ<sub>x</sub> = θ (l'inclinazione, come in (c));</li>
<li>attorno a <b>Y<sub>w</sub></b> di θ<sub>y</sub> = 180° (per girare Z<sub>w</sub> e X<sub>w</sub>).</li>
</ul>
<p>Qui le due rotazioni sono solo elencate; l'<b>ordine</b> giusto (prima Y, poi X) è nella slide successiva.</p>
<div class="box b"><b>Dal libro · cap. 39, § 39.6, esempio (d)</b><p>Nel libro l'origine del mondo è il punto in cui l'asse ottico incontra il suolo: vale tanθ = h/d. Con questa scelta e la proiezione parallela (eq. 39.21) le formule si riducono a x = −aX, y = a cosθ Y − a sinθ Z, che il libro collega al sistema di visione semplice del cap. 2 (con a = 1 e il segno di x opposto per una diversa convenzione degli assi). Verificato: l'asse ottico della camera di (d) tocca il suolo in Z = d − h/tanθ, che è 0 proprio quando tanθ = h/d. <a href="https://visionbook.mit.edu/imaging_geometry.html" target="_blank">Cap. 39</a>.</p></div>
""")

s(26, "Example (d)", """
<ul>
<li><b>Prima</b> si ruota attorno a Y<sub>w</sub> di θ<sub>y</sub> = 180°.</li>
<li><b>Poi</b> attorno a X<sub>w</sub> di θ<sub>x</sub> = θ.</li>
</ul>
<span class="f">R = R<sub>x</sub>(θ) R<sub>y</sub>(180°) = [1 0 0; 0 cosθ sinθ; 0 −sinθ cosθ] · [−1 0 0; 0 1 0; 0 0 −1] = [−1 0 0; 0 cosθ −sinθ; 0 −sinθ −cosθ]</span>
<ul>
<li>La rotazione applicata <b>per prima</b> sta <b>a destra</b> nel prodotto (agisce per prima sul vettore).</li>
<li>R<sub>y</sub>(180°) = diag(−1, 1, −1): cambia segno a X e Z, lascia Y.</li>
</ul>
<div class="box k"><b>Da saper verificare</b><p>Terza riga di R = asse ottico Z<sub>c</sub> nel mondo: (0, −sinθ, −cosθ), cioè verso il basso e verso −Z<sub>w</sub>, cioè verso l'origine del mondo, come nella figura. Verificato con sympy.</p></div>
""")

s(27, "Example (d)", """
<p><b>Le moltiplicazioni di matrici non commutano, e in generale nemmeno le rotazioni.</b></p>
<span class="f">R<sub>x</sub>R<sub>y</sub> = [−1 0 0; 0 cosθ −sinθ; 0 −sinθ −cosθ]     R<sub>y</sub>R<sub>x</sub> = [−1 0 0; 0 cosθ sinθ; 0 sinθ −cosθ]</span>
<ul>
<li>Le due matrici differiscono nel segno dei seni.</li>
<li>Solo R<sub>x</sub>R<sub>y</sub> descrive la camera della figura: con R<sub>y</sub>R<sub>x</sub> l'asse ottico sarebbe (0, sinθ, −cosθ), cioè rivolto <b>verso l'alto</b>.</li>
</ul>
<div class="box x"><b>Approfondimento: perché qui l'ordine conta</b><p>Due rotazioni attorno allo stesso asse commutano; attorno ad assi diversi in generale no. In questo caso particolare R<sub>y</sub>(180°) = diag(−1, 1, −1) commuta con R<sub>x</sub> solo se sinθ = 0. Per i casi generali si fissa una convenzione (angoli di Eulero, assi fissi o mobili) e la si rispetta; OpenCV evita il problema rappresentando R con il <b>vettore di Rodrigues</b> (asse × angolo), quello che restituisce come <code>rvecs</code>.</p></div>
""")

s(28, "Example (d)", """
<span class="f">M = [a 0 0 0; 0 a 0 0; 0 0 1 0] · [R 0; 0<sup>⊤</sup> 1] · [1 0 0 0; 0 1 0 −h; 0 0 1 −d; 0 0 0 1]</span>
<span class="f">= [−a 0 0 0; 0 a cosθ −a sinθ −ah cosθ + ad sinθ; 0 −sinθ −cosθ h sinθ + d cosθ]</span>
<ul>
<li>La camera sta in T = (0, h, d): la traslazione ha −h e −d.</li>
<li>Ultima colonna = K·(−RT): verificata con sympy, coincide con l'eq. 39.20 del libro.</li>
<li>In coordinate cartesiane: x = −aX / (sinθ(h − Y) + cosθ(d − Z)), y = a(cosθ(Y − h) + sinθ(d − Z)) / (sinθ(h − Y) + cosθ(d − Z)).</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Dato un disegno della scena: scrivere T (posizione della camera nel mondo), costruire R riga per riga (assi della camera nel mondo) o come prodotto di rotazioni elementari nell'ordine giusto, moltiplicare K · [R | −RT]. Controllare il risultato su un punto noto (ad esempio il punto dove l'asse ottico tocca il suolo deve andare nel centro dell'immagine).</p></div>
""")

s(29, "Camera Calibration", "<p>Dal modello alla stima: cosa significa calibrare una camera.</p>", kind="div", sec=("l12-calibrazione", "Calibrazione della camera", "slide 29–30"))

s(30, "Camera Calibration", """
<ul>
<li>Una camera è <b>calibrata</b> se si conosce la trasformazione mondo → pixel.</li>
<li><b>Intrinseci</b>:
<ul><li>in teoria si potrebbero calcolare dalle specifiche tecniche (focale, dimensioni del sensore);</li>
<li>in pratica è più rapido e robusto <b>stimarli</b>: usura, autofocus, stabilizzazione e post-elaborazione (ritaglio, correzione della distorsione nel telefono) li cambiano.</li></ul></li>
<li><b>Estrinseci</b>: non si controllano completamente la scena e la posizione della camera.</li>
<li>Quindi i parametri si <b>stimano</b> dalle immagini.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 39, § 39.3.3 A Simple, although Unreliable, Calibration Method</b><p>Il libro mostra perché le specifiche non bastano: per un iPhone dalle specifiche (focale 5.7 mm, sensore 7.6 mm, 4032 pixel) si ottiene a ≈ 3024, mentre con la misura della scacchiera a distanza nota si ottiene a ≈ 3103. La misura diretta è comunque poco precisa (serve conoscere bene la distanza) e va presa solo come controllo di plausibilità; la calibrazione vera è quella di § 39.7. <a href="https://visionbook.mit.edu/imaging_geometry.html" target="_blank">Cap. 39</a>.</p></div>
""")

s(31, "Direct Linear Transform", "<p>Stimare la matrice 3×4 con un sistema lineare omogeneo, come per l'omografia.</p>", kind="div", sec=("l12-dlt", "Direct Linear Transform", "slide 31–39"))

s(32, "DLT: Setup", """
<p>È lo <b>stesso metodo</b> usato per stimare l'omografia H nei panorami (L9), con una matrice 3×4 invece di 3×3.</p>
<ul>
<li>Dati: un insieme di corrispondenze fra punti 3D del mondo <b>P<sub>i</sub></b> e i loro pixel <b>p<sub>i</sub></b>.</li>
<li>M ha <b>12 elementi</b> e <b>11 gradi di libertà</b>: se ne perde uno per l'invarianza di scala (M e λM danno gli stessi pixel).</li>
<li>Ogni corrispondenza vincola M tramite le tre righe m<sub>0</sub><sup>⊤</sup>, m<sub>1</sub><sup>⊤</sup>, m<sub>2</sub><sup>⊤</sup>:</li>
</ul>
<span class="f">p<sub>i</sub> = M P<sub>i</sub> = [m<sub>0</sub><sup>⊤</sup>; m<sub>1</sub><sup>⊤</sup>; m<sub>2</sub><sup>⊤</sup>] P<sub>i</sub>   (uguaglianza a meno di scala, coordinate omogenee)</span>
""")

s(33, "DLT", """
<p>In coordinate cartesiane, per ogni corrispondenza:</p>
<span class="f">x<sub>i</sub> = m<sub>0</sub><sup>⊤</sup>P<sub>i</sub> / m<sub>2</sub><sup>⊤</sup>P<sub>i</sub>,   y<sub>i</sub> = m<sub>1</sub><sup>⊤</sup>P<sub>i</sub> / m<sub>2</sub><sup>⊤</sup>P<sub>i</sub></span>
<p>Moltiplicando per il denominatore si ottengono vincoli <b>lineari</b> in M:</p>
<span class="f">P<sub>i</sub><sup>⊤</sup>m<sub>0</sub> − x<sub>i</sub> P<sub>i</sub><sup>⊤</sup>m<sub>2</sub> = 0,   P<sub>i</sub><sup>⊤</sup>m<sub>1</sub> − y<sub>i</sub> P<sub>i</sub><sup>⊤</sup>m<sub>2</sub> = 0</span>
<p>Il trucco è lo stesso della DLT per l'omografia: la divisione rende il problema non lineare, il prodotto incrociato lo linearizza.</p>
""")

s(34, "DLT", """
<p>In forma matriciale, con m il vettore di 12 elementi ottenuto appiattendo M riga per riga:</p>
<span class="f">A<sub>i</sub> m = [ −P<sub>i</sub><sup>⊤</sup>  0<sup>⊤</sup>  x<sub>i</sub>P<sub>i</sub><sup>⊤</sup> ; 0<sup>⊤</sup>  −P<sub>i</sub><sup>⊤</sup>  y<sub>i</sub>P<sub>i</sub><sup>⊤</sup> ] [m<sub>0</sub>; m<sub>1</sub>; m<sub>2</sub>] = 0</span>
<ul>
<li>Ogni blocco è una riga di 4 elementi (P<sub>i</sub> è omogeneo, [X, Y, Z, 1]): la matrice di <b>una</b> corrispondenza è <b>2 × 12</b>.</li>
<li>Il segno globale delle righe (qui cambiato rispetto alla slide precedente) non conta: si risolve A m = 0.</li>
</ul>
""")

s(35, "DLT", """
<ul>
<li>Ogni corrispondenza dà una matrice 2 × 12, cioè <b>2 equazioni</b>.</li>
<li>M ha 11 gradi di libertà: 11/2 = 5.5, quindi bastano <b>6 corrispondenze</b>.</li>
<li>In pratica, per il rumore, conviene usarne di più (sistema sovradeterminato, A di dimensione 2N × 12).</li>
</ul>
<div class="box x"><b>Approfondimento: i 6 punti non devono essere complanari</b><p>Il conto 6 vale per punti in <b>posizione generale nello spazio</b>. Se tutti i P<sub>i</sub> stanno su un piano, la DLT della 3×4 è degenere: verificato con numpy, con punti su Z = 0 la matrice A ha rango 8 qualunque sia il numero di punti (20 punti: A è 40 × 12, rango 8), quindi lo spazio nullo ha dimensione 4 e M non è determinata. Il motivo: con Z = 0 la terza colonna di M non viene mai "vista". Il libro (§ 39.7.1) lo dice esplicitamente citando Hartley-Zisserman. Per questo con una scacchiera piana si usa il metodo di Zhang (slide 41). Il libro, nel toy example di § 39.7.5, parla invece di "almeno otto corrispondenze": è in contraddizione con il sei di § 39.7.1; il minimo teorico è 6.</p></div>
""")

s(36, "DLT: Solution", """
<p>Si impilano i vincoli di tutte le corrispondenze in A e si risolve:</p>
<span class="f">m* = argmin<sub>m</sub> ‖A m‖   con   ‖m‖ = 1</span>
<ul>
<li>m è definito a meno di scala, quindi il vincolo ‖m‖ = 1 non cambia la soluzione.</li>
<li>Senza il vincolo la soluzione banale è m = 0.</li>
<li>La soluzione è l'<b>autovettore di A<sup>⊤</sup>A con autovalore minimo</b> (la slide scrive "minimum eigenvector").</li>
</ul>
<div class="box k"><b>Da saper fare: perché l'autovettore minimo</b><p>‖Am‖² = m<sup>⊤</sup>A<sup>⊤</sup>Am. Con ‖m‖ = 1 è un quoziente di Rayleigh: il minimo è il più piccolo autovalore di A<sup>⊤</sup>A, raggiunto dal suo autovettore. Equivalente e numericamente migliore: l'<b>ultimo vettore singolare destro</b> della SVD di A (l'ultima riga di V<sup>⊤</sup>). Verificato con numpy: le due soluzioni coincidono a meno del segno. Senza rumore, con almeno 6 punti non complanari, il valore minimo è 0 e si ritrova M esatta a meno di scala.</p></div>
<div class="box x"><b>Approfondimento: normalizzare i punti</b><p>Come per l'omografia (L9), conviene normalizzare i punti (centrarli e scalarli) prima di costruire A: in A compaiono insieme numeri dell'ordine di 1 e prodotti come x<sub>i</sub>X<sub>i</sub> dell'ordine di migliaia, e la soluzione diventa mal condizionata (Hartley-Zisserman, cap. 7).</p></div>
""")

s(37, "Recovering Intrinsic and Extrinsic Camera Parameters", """
<p>Dalla DLT si ha M; ora si separano K, R, T.</p>
<span class="f">M = [KR | −KRT] = [B | b],   B = KR (3 × 3),   b = −KRT (3 × 1)</span>
<ul>
<li>La posizione della camera si ricava dall'ultima colonna.</li>
<li>B = KR è il prodotto di una triangolare superiore (K) per una ortonormale (R): si separano con una scomposizione matriciale.</li>
</ul>
<div class="box w"><b>Attenzione: T = −B<sup>−1</sup>b, e la scomposizione è RQ</b>
<p>La slide scrive T = B<sup>−1</sup>b. Da b = −KRT = −BT segue <b>T = −B<sup>−1</sup>b</b> (eq. 39.23 del libro). Verificato con numpy: con una camera sintetica, −B<sup>−1</sup>b restituisce la posizione vera, B<sup>−1</sup>b il suo opposto.</p>
<p>La slide dice poi "KR recovered by QR decomposition". La QR scrive una matrice come <b>ortogonale × triangolare</b>, cioè nell'ordine opposto a KR. Servono la <b>decomposizione RQ</b> di B (triangolare × ortogonale, <code>scipy.linalg.rq</code>), oppure, come fa il libro, la QR di <b>B<sup>−1</sup></b>: B<sup>−1</sup> = R<sup>⊤</sup>K<sup>−1</sup> = Q·U, quindi R = Q<sup>⊤</sup> e K = U<sup>−1</sup>. In entrambi i casi bisogna poi correggere i segni: la scomposizione è unica solo a meno di segni, e si cambia segno alle colonne di K con diagonale negativa e alle righe corrispondenti di R; infine si divide K per K<sub>33</sub>. Verificato: i due metodi danno lo stesso K e lo stesso R.</p></div>
<div class="box b"><b>Dal libro · cap. 39, § 39.7.2 Recovering Intrinsic and Extrinsic Camera Parameters</b><p>Il libro avverte che questa scomposizione è <b>sensibile al rumore</b>: per questo il risultato si usa solo come inizializzazione della minimizzazione dell'errore di riproiezione (slide 39). Avverte anche di un errore tipico nel codice: rimettere il vettore m nella matrice M nell'ordine sbagliato. Consiglio del libro: simulare punti 3D, proiettarli con una M nota e verificare di ritrovarla. <a href="https://visionbook.mit.edu/imaging_geometry.html" target="_blank">Cap. 39</a>.</p></div>
""")

s(38, "Nonlinearities in the Calibration Objective", """
<ul>
<li>La DLT minimizza un errore nelle <b>coordinate omogenee</b> (errore <b>algebrico</b> ‖Am‖), ma le coordinate omogenee sono invarianti di scala.</li>
<li>Ogni corrispondenza entra nei vincoli con una <b>scala diversa</b> (il fattore m<sub>2</sub><sup>⊤</sup>P<sub>i</sub>, cioè la profondità del punto): i punti non pesano in modo equo.</li>
</ul>
<p>Passaggio da omogenee a cartesiane:</p>
<span class="f">π(u, v, w) = (u/w, v/w)</span>
<p>Si noti la <b>divisione per w</b>: è non lineare. L'obiettivo vero è in coordinate cartesiane, cioè in pixel:</p>
<span class="f">min<sub>M</sub> ∑<sub>i=1..N</sub> ‖p<sub>i</sub> − π(M P<sub>i</sub>)‖²</span>
<div class="box k"><b>Da saper spiegare</b><p>Moltiplicare per il denominatore (DLT) equivale a pesare l'errore del punto i con la sua profondità: un punto lontano ha un residuo algebrico grande anche se in pixel l'errore è piccolo. L'errore che interessa è quello <b>geometrico</b>, misurato in pixel, e non si può scrivere come sistema lineare.</p></div>
""")

s(39, "Nonlinear Optimization by Minimizing Reprojection Error", """
<p><b>Errore di riproiezione</b>: differenza fra la posizione stimata di un punto nell'immagine (proiettando il punto 3D con i parametri correnti) e la sua posizione misurata.</p>
<span class="f">∑<sub>i=1..N</sub> ‖p<sub>i</sub> − p<sub>i</sub>′‖² = ∑<sub>i=1..N</sub> ‖p<sub>i</sub> − π(K [R | −RT] P<sub>i</sub>)‖²</span>
<ul>
<li>π è il passaggio da omogenee a cartesiane.</li>
<li>Si ottimizzano K, R, T; l'ottimizzazione si <b>inizializza con la DLT</b>.</li>
</ul>
<p><b>Figura</b> (visionbook, fig. 39.14): un triangolo arancione con vertici P<sub>1</sub>, P<sub>2</sub>, P<sub>3</sub> nello spazio, la camera con i suoi assi (X<sub>L</sub>, Y<sub>L</sub>, Z<sub>L</sub>) e il piano immagine. Sul piano ci sono i punti osservati p<sub>i</sub> e le riproiezioni stimate p<sub>i</sub>′, collegati da corti segmenti rossi: l'errore di riproiezione è la somma dei quadrati delle loro lunghezze.</p>
<div class="box w"><b>Attenzione: non è SGD</b><p>La slide dice che K, R, T sono minimizzati "by SGD". Non c'è nulla di stocastico: la somma è su tutte le corrispondenze, che sono poche (centinaia o migliaia), e si usa sempre il gradiente completo. Il libro (eq. 39.24) dice semplicemente <b>discesa del gradiente</b>; in pratica si usano metodi ai minimi quadrati non lineari del secondo ordine, tipicamente <b>Levenberg-Marquardt</b>. È quello che fa OpenCV: la documentazione di <code>calibrateCamera</code> (calib3d.hpp) dice che esegue "the global Levenberg-Marquardt optimization algorithm to minimize the reprojection error". Lo stesso vale per la slide 45.</p></div>
<div class="box x"><b>Approfondimento: come si ottimizza R</b><p>R deve restare ortonormale, quindi non si ottimizzano i suoi 9 elementi liberamente: si usa una parametrizzazione minima a 3 numeri, tipicamente il vettore di Rodrigues (direzione = asse, norma = angolo). Nel modello completo π include anche la <b>distorsione</b> della lente (slide 48), che la DLT non può modellare.</p></div>
""")

s(40, "Calibration Targets", "<p>Come procurarsi tante corrispondenze 3D–2D precise: il metodo multipiano e la scacchiera.</p>", kind="div", sec=("l12-target", "Target di calibrazione", "slide 40–45"))

s(41, "Multiplane Calibration Method", """
<ul>
<li>Per la DLT servono un insieme di immagini e corrispondenze fra punti.
<ul><li>Le immagini devono essere facili e veloci da acquisire in qualunque situazione, e i match devono essere robusti.</li></ul></li>
<li>Il <b>metodo di Zhang</b> è uno dei metodi di calibrazione standard.</li>
<li>Si usano <b>pannelli di calibrazione planari</b> standard.</li>
<li>Si scattano più foto del pannello in posizioni e orientazioni diverse rispetto a una camera fissa (o, equivalentemente, si muove la camera).</li>
</ul>
<div class="box w"><b>Attenzione: con un piano la DLT della 3×4 non funziona</b><p>La slide collega il metodo multipiano alla DLT della slide 35, ma tutti i punti di una scacchiera hanno Z = 0: la DLT di M è degenere (rango 8, slide 35). Zhang usa la DLT in un altro modo: per ogni immagine stima l'<b>omografia</b> H fra il piano della scacchiera e l'immagine (la DLT di L9, 4 punti bastano). Con Z = 0 la proiezione diventa H ∝ K[r<sub>1</sub> r<sub>2</sub> t], la stessa omografia del piano vista in L9. Poiché r<sub>1</sub> e r<sub>2</sub> sono ortonormali, ogni H dà <b>2 vincoli lineari</b> sugli intrinseci; con almeno 3 viste (2 se lo skew è fissato a 0) si ricava K in forma chiusa, poi R e t di ogni vista, poi si rifinisce tutto, distorsione compresa, minimizzando l'errore di riproiezione.</p></div>
<div class="box b"><b>Dal libro · cap. 39, § 39.7.3 Multiplane Calibration Method</b><p>Il libro dedica al metodo solo due paragrafi: pannello planare, più foto in posizioni e orientazioni diverse, metodo di Zhang "ancora molto usato". Il libro lo data al 1999 ma la bibliografia cita Zhang 2000 (IEEE TPAMI, "A flexible new technique for camera calibration"): è l'articolo da leggere per le formule. <a href="https://visionbook.mit.edu/imaging_geometry.html" target="_blank">Cap. 39</a>.</p></div>
""")

s(42, "Advantages of Standardized Calibration Targets", """
<ul>
<li>La calibrazione richiede punti 3D <b>noti</b> P<sub>i</sub> accoppiati ai loro pixel osservati p<sub>i</sub>.</li>
<li>In linea di principio va bene qualunque oggetto con punti 3D misurati con precisione, ma:
<ul><li>misurare a mano punti 3D è lento e soggetto a errori (il toy example del libro lo mostra);</li>
<li>servono <b>molte</b> corrispondenze, distribuite su tutta l'immagine, con precisione <b>sub-pixel</b>.</li></ul></li>
</ul>
<p><b>Soluzione</b>: stampare un pattern di geometria nota e regolare.</p>
<ul>
<li>Le coordinate nel mondo sono note <b>per costruzione</b> (il pattern lo abbiamo progettato noi).</li>
<li>Le coordinate immagine si rilevano <b>automaticamente</b> e con precisione.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 39, § 39.7.5 A Toy Example</b><p>Il libro calibra una foto del proprio ufficio con 12 punti misurati a mano (distanze in centimetri sul pavimento, una colonna e una parete vetrata; pixel letti a mano in un editor di immagini). Risultato: errore di riproiezione medio di 12.3 pixel, camera stimata a 171.8 cm di altezza (quella degli occhi del fotografo), inclinazione 20.5° contro i circa 15° stimati a occhio. Funziona, ma con 12 punti rumorosi: è esattamente il motivo per cui si usano pattern stampati con decine di punti rilevati automaticamente. <a href="https://visionbook.mit.edu/imaging_geometry.html" target="_blank">Cap. 39</a>.</p></div>
""")

s(43, "Checkerboard Patterns", """
<ul>
<li>Una scacchiera ha <b>n × m angoli interni</b> (non quadretti: 10 × 7 quadretti danno 9 × 6 angoli interni).</li>
<li>Gli angoli sono i punti di calibrazione: ben localizzati, con forte contrasto in <b>due direzioni</b> (il criterio di Harris di L8).</li>
<li>Si trovano come massimi locali di una risposta "corner" e si ordinano in una griglia usando la topologia nota della scacchiera.</li>
<li>Le coordinate nel mondo dell'angolo (r, c) sono banali: <b>(r·s, c·s, 0)</b> con s lato del quadretto.</li>
</ul>
<p><b>Figura:</b> a sinistra una scacchiera sintetica ("checkerboard target"); a destra la stessa con i massimi della risposta di Harris segnati in rosso sugli angoli interni, con il titolo "54 corners found (expected 54)": una scacchiera 10 × 7 quadretti ha 9 × 6 = 54 angoli interni, gli stessi delle immagini del notebook.</p>
<div class="box k"><b>Da saper spiegare: il lato s</b><p>Se si usa s = 1 (come nel notebook) le traslazioni stimate sono in "quadretti"; con s in millimetri sono in millimetri. Gli intrinseci (in pixel) e le rotazioni non dipendono da s.</p></div>
""")

s(44, "Practical Considerations", """
<ul>
<li><b>Rigidità</b>: l'ipotesi di planarità deve valere; un foglio piegato o ondulato non funziona (incollarlo su un supporto rigido).</li>
<li><b>Dimensione</b>: abbastanza grande da rilevare bene gli angoli, abbastanza piccola da stare tutta nell'immagine.</li>
<li><b>Copertura</b>: servono immagini in cui il pannello copre
<ul><li>il centro e gli angoli e i bordi dell'immagine (la distorsione è più forte ai bordi);</li>
<li>una gamma di distanze e di inclinazioni.</li></ul></li>
</ul>
""")

s(45, "Convergence considerations", """
<p>L'ottimizzatore è <b>locale</b>: converge al punto stazionario più vicino all'inizializzazione.</p>
<ul>
<li>Una buona inizializzazione in forma chiusa (metodo di Zhang) aiuta.</li>
<li>Possono esserci angoli rilevati male (<b>outlier</b>): controllare a vista il rilevamento in ogni immagine usata.</li>
<li><b>Insiemi di viste degeneri</b> (ad esempio tutte quasi frontali) lasciano alcuni parametri (punto principale, distorsione) poco vincolati: l'ottimizzatore può non spostarli in modo significativo dal valore iniziale.</li>
</ul>
<div class="box w"><b>Attenzione: ottimizzatore locale sì, SGD no</b><p>La slide apre con "We use SGD". Il punto (ottimizzatore locale, conta l'inizializzazione) è corretto, ma il metodo non è SGD: è Levenberg-Marquardt sull'intero insieme di corrispondenze (vedi slide 39). Anche LM è locale, quindi il resto della slide vale invariato.</p></div>
<div class="box x"><b>Approfondimento: perché le viste frontali sono degeneri</b><p>Con il pannello parallelo al sensore, un cambio di focale e un cambio di distanza producono quasi la stessa immagine (il pannello diventa solo più grande o più piccolo): i dati non separano f da t<sub>z</sub>. È l'inclinazione del pannello (lo scorcio prospettico) a rendere osservabile la focale; nel metodo di Zhang due viste parallele danno vincoli linearmente dipendenti.</p></div>
""")

s(46, "Camera Calibration with OpenCV", "<p>La pipeline pratica: rilevare gli angoli, calibrare, valutare.</p>", kind="div", sec=("l12-opencv", "Calibrazione con OpenCV", "slide 46–54"))

s(47, "Dataset: a set of checkerboard images from one camera", """
<ul>
<li>Setup tipico: una scacchiera rigida e planare, di cui si conoscono gli angoli interni e il lato del quadretto.</li>
<li>Acquisire <b>15–25 immagini</b>, variando:
<ul><li>la distanza dalla camera (vicino e lontano);</li>
<li>l'inclinazione in <b>entrambe</b> le direzioni (non solo attorno a un asse);</li>
<li>la posizione nell'inquadratura (centro, angoli, bordi).</li></ul></li>
<li>Tenere il pannello rigido e a fuoco; evitare il mosso (cavalletto o tempo di esposizione breve).</li>
</ul>
<p>Il notebook ne usa 13 (le <code>left*.jpg</code> dei sample di OpenCV), e con il pattern sbagliato solo 9 (sezione Notebook).</p>
""")

s(48, "Overview of the OpenCV calibration workflow", """
<pre>per ogni immagine di calibrazione:
    findChessboardCorners   # rileva gli angoli
    cornerSubPix            # li raffina
    (object_points, image_points)  # raccoglie
K, dist, rvecs, tvecs = calibrateCamera(object_points, image_points, image_size)
per ogni nuova immagine:
    undistort(image, K, dist)</pre>
<ul>
<li><b>object_points</b>: le stesse coordinate note della scacchiera (X, Y, 0) per ogni vista (la geometria del pannello è fissa).</li>
<li><b>image_points</b>: le posizioni in pixel degli angoli rilevati, un insieme per immagine.</li>
<li>Tutto ciò che si è visto (stima lineare + raffinamento non lineare + distorsione) avviene dentro <code>calibrateCamera</code>.</li>
</ul>
<div class="box x"><b>Approfondimento: il modello di distorsione di OpenCV</b><p><code>dist</code> contiene (k<sub>1</sub>, k<sub>2</sub>, p<sub>1</sub>, p<sub>2</sub>, k<sub>3</sub>). Sulle coordinate normalizzate (x, y) = (X<sub>c</sub>/Z<sub>c</sub>, Y<sub>c</sub>/Z<sub>c</sub>), con r² = x² + y²:</p>
<span class="f">radiale: x<sub>d</sub> = x(1 + k<sub>1</sub>r² + k<sub>2</sub>r⁴ + k<sub>3</sub>r⁶)  (idem per y)</span>
<span class="f">tangenziale: x<sub>d</sub> += 2p<sub>1</sub>xy + p<sub>2</sub>(r² + 2x²),   y<sub>d</sub> += p<sub>1</sub>(r² + 2y²) + 2p<sub>2</sub>xy</span>
<p>Poi u = f<sub>x</sub>x<sub>d</sub> + c<sub>x</sub>, v = f<sub>y</sub>y<sub>d</sub> + c<sub>y</sub>. k<sub>1</sub> &lt; 0 è la distorsione a barilotto (le rette si curvano verso l'esterno), k<sub>1</sub> &gt; 0 a cuscinetto. È questo che il libro chiama "distorsione geometrica" dentro π (§ 39.7.4) senza scrivere formule (tutorial OpenCV <i>Camera Calibration</i>).</p></div>
""")

s(49, "findChessboardCorners: detecting calibration pattern corners", """
<ul>
<li><code>cv2.findChessboardCorners(image, pattern_size)</code> cerca la griglia n × m di angoli <b>interni</b> e li restituisce in un ordine coerente, riga per riga: serve perché l'i-esimo angolo rilevato corrisponda all'i-esimo object point.</li>
<li>Restituisce un booleano (pattern trovato o no) e, se trovato, le posizioni degli angoli. Non tutte le immagini riescono (occlusioni, poco contrasto, mosso): quelle si scartano.</li>
<li>Simile a un rilevamento alla Harris, più la logica per raggruppare gli angoli nella topologia e nell'ordine giusti.</li>
</ul>
<p>Scartare le immagini in cui il pattern non è stato trovato e controllarne a campione alcune (anche un ordine sbagliato degli angoli è un possibile errore).</p>
<div class="box x"><b>Approfondimento</b><p>L'algoritmo classico di <code>findChessboardCorners</code> in realtà non usa Harris: binarizza l'immagine (soglia adattiva), trova i quadrilateri neri come contorni e li collega in base agli angoli condivisi. Esiste anche <code>findChessboardCornersSB</code>, basato su una risposta "corner" dedicata, più robusto e già sub-pixel. Attenzione al <b>pattern_size</b>: è il numero di angoli interni per riga e per colonna, e se è sbagliato la funzione può restituire una sottogriglia o fallire (è ciò che succede nel notebook).</p></div>
""")

s(50, "Sub-pixel corner refinement", """
<ul>
<li><code>findChessboardCorners</code> dà una stima approssimata; <code>cv2.cornerSubPix(image, corners, win_size, ...)</code> raffina ogni angolo con precisione <b>sub-pixel</b>.</li>
<li>Idea: attorno alla stima iniziale, il vero angolo q è il punto per cui il gradiente dell'immagine in ogni pixel p vicino è <b>ortogonale</b> al vettore p − q. Vale perché sui lati dell'angolo il gradiente è perpendicolare al lato, che passa per q, e nelle zone uniformi è nullo. Si risolve ai minimi quadrati, con poche iterazioni tipo Gauss-Newton.</li>
<li>Senza raffinamento, con angoli a pixel interi, la precisione della calibrazione sarebbe limitata a circa 0.5 px indipendentemente dal numero di immagini.</li>
</ul>
<span class="f">∑<sub>p ∈ finestra</sub> ( ∇I(p)<sup>⊤</sup> (p − q) )² → min su q</span>
<div class="box w"><b>Attenzione: findChessboardCorners non restituisce pixel interi</b><p>La slide dice che <code>findChessboardCorners</code> dà stime a pixel interi. In OpenCV non è così: verificato sul notebook, il 99% delle coordinate restituite ha parte frazionaria (es. 244.454, 94.331), e la documentazione dice che la funzione già chiama <code>cornerSubPix</code> internamente. La chiamata esplicita a <code>cornerSubPix</code> serve comunque a raffinare con la finestra e i criteri scelti. Il ragionamento della slide (pixel interi → errore di quantizzazione fino a 0.5 px) resta valido come motivazione.</p></div>
<div class="box x"><b>Approfondimento: la finestra conta</b><p><code>win_size = (11, 11)</code> è la <b>mezza</b> finestra: la ricerca usa 23 × 23 pixel. Se i quadretti nell'immagine sono più piccoli, nella finestra entrano altri angoli o il bordo del pannello e il punto viene spostato. Nel notebook con il pattern giusto succede proprio questo (sezione Notebook): una finestra 7 × 7 risolve.</p></div>
""")

s(51, "calibrateCamera: running the full calibration", """
<pre>ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(
    object_points,  # lista di array (n_punti, 3), uno per vista
    image_points,   # lista di array (n_punti, 2), uno per vista
    image_size,     # (larghezza, altezza) in pixel
)</pre>
<ul>
<li>Esegue l'inizializzazione in forma chiusa di Zhang, poi il raffinamento non lineare di intrinseci, distorsione e parametri di ogni vista (rvecs, tvecs).</li>
<li><b>ret</b> è l'errore di riproiezione <b>RMS</b> complessivo, in pixel, della soluzione finale.</li>
</ul>
<div class="box k"><b>Da saper leggere</b><ul>
<li><code>K</code>: [f<sub>x</sub> 0 c<sub>x</sub>; 0 f<sub>y</sub> c<sub>y</sub>; 0 0 1], in pixel. Nel notebook f<sub>x</sub> ≈ f<sub>y</sub> ≈ 534, (c<sub>x</sub>, c<sub>y</sub>) ≈ (342, 232) su immagini 640 × 480.</li>
<li><code>rvecs[i]</code>, <code>tvecs[i]</code>: posa della scacchiera i nel riferimento della camera (R in forma di Rodrigues, t nelle unità degli object point). Sono l'R e il −RT della lezione, per ogni vista.</li>
<li><code>ret</code> = √(media dei quadrati delle distanze) su tutti i punti di tutte le viste: verificato, 0.1559 sia da <code>ret</code> sia ricalcolato.</li></ul></div>
<div class="box x"><b>Approfondimento: cosa fa davvero OpenCV</b><p>Dalla documentazione di <code>calibrateCamera</code>: (1) parametri intrinseci iniziali, solo per pattern planari: (c<sub>x</sub>, c<sub>y</sub>) al centro dell'immagine e focali ai minimi quadrati dalle omografie (una versione semplificata di Zhang), distorsione a zero; (2) posa iniziale di ogni vista con <code>solvePnP</code>; (3) Levenberg-Marquardt globale sull'errore di riproiezione. Con un oggetto 3D non planare serve una K iniziale (<code>CALIB_USE_INTRINSIC_GUESS</code>). Lo skew non viene stimato: K ha sempre 0 in posizione (1, 2).</p></div>
""")

s(52, "Some Sanity Checks", """
<p>Controlli di plausibilità sui parametri stimati:</p>
<ul>
<li><b>Centro dell'immagine</b>: u<sub>0</sub>, v<sub>0</sub> vicini al centro (salvo lenti notoriamente decentrate).</li>
<li><b>Pixel non quadrati</b>: α ≈ β, salvo pixel notoriamente non quadrati.</li>
<li>γ ≈ 0 per la maggior parte delle camere consumer.</li>
</ul>
<p>Notazione di Zhang: K = [α γ u<sub>0</sub>; 0 β v<sub>0</sub>; 0 0 1], cioè α = f<sub>x</sub>, β = f<sub>y</sub>, (u<sub>0</sub>, v<sub>0</sub>) = (c<sub>x</sub>, c<sub>y</sub>), γ = skew.</p>
<div class="box w"><b>Attenzione: γ è lo skew, non la distorsione</b><p>La slide etichetta il terzo controllo "lens distortion: γ ≈ 0". Nella notazione di Zhang γ è lo <b>skew</b>, cioè la non ortogonalità fra gli assi del sensore (l'elemento in alto al centro di K), non la distorsione della lente, che sta nei coefficienti k<sub>1</sub>, k<sub>2</sub>, … e non è affatto ≈ 0 (nel notebook k<sub>1</sub> ≈ −0.29). Lo skew è trascurabile nelle camere moderne e OpenCV lo fissa a 0.</p></div>
<div class="box k"><b>Applicato al notebook</b><p>α = 534.16, β = 534.25: rapporto 1.0002, pixel quadrati. (u<sub>0</sub>, v<sub>0</sub>) = (341.7, 232.1) contro il centro (319.5, 239.5): 22 pixel di scarto orizzontale, plausibile per una camera economica.</p></div>
""")

s(53, "Evaluating calibration quality: reprojection errors", """
<ul>
<li>Guardare l'errore di riproiezione RMS <b>per immagine</b>, non solo quello globale di <code>calibrateCamera</code>: una buona calibrazione ha errore basso e <b>uniforme</b> su tutte le immagini.</li>
<li>Un errore alto in un'immagine (pannello destro della figura) indica un problema di rilevamento (mosso, occlusione parziale) o una vista cattiva (angolo estremo).
<ul><li>Rimuovere quelle immagini e ricalibrare.</li></ul></li>
<li>Con viste fatte bene (pannello perfettamente piano, buon rilevamento, nessuna vista cattiva) l'RMS dovrebbe stare sotto 1 px, anche sotto 0.5 px.</li>
</ul>
<p><b>Figura:</b> due grafici a barre dell'errore RMS per immagine (12 immagini). A sinistra "good coverage": barre verdi tutte fra circa 0.15 e 0.3 px, media 0.27 px. A destra "poor coverage": la maggior parte delle barre è bassa, ma tre immagini (in rosso) arrivano a 1.5–1.8 px e tirano la media a 0.60 px. La media globale da sola non dice quali immagini sono il problema.</p>
<div class="box k"><b>Come ottenerlo in OpenCV</b><p><code>cv2.calibrateCameraExtended</code> restituisce anche <code>perViewErrors</code> (RMS per vista) e le deviazioni standard dei parametri. Nel notebook, con il pattern 9 × 6, una sola immagine (left02) ha RMS 1.22 px contro 0.16–0.46 delle altre: è il caso del pannello destro (sezione Notebook).</p></div>
""")

s(54, "Good vs. Bad calibration", """
<div class="two">
<div><p><b>Calibrazione buona</b></p><ul>
<li>RMS per immagine sub-pixel (es. tutti &lt; 0.3–0.5 px).</li>
<li>K e distorsione <b>stabili</b> se si ricalibra su un sottoinsieme casuale delle immagini.</li></ul></div>
<div><p><b>Calibrazione scadente</b></p><ul>
<li>Poche immagini con errore molto più alto (rilevamenti sbagliati o viste estreme).</li>
<li>u<sub>0</sub>, v<sub>0</sub> lontani dal centro senza motivo fisico, o focale implausibile.</li>
<li>Curvatura residua vicino ai bordi dopo l'undistort (distorsione sotto-corretta).</li></ul></div>
</div>
<div class="box k"><b>Stabilità nel notebook</b><p>Con le stesse immagini e configurazioni diverse (pattern 7 × 6 su 9 immagini, 9 × 6 su 13 con finestre diverse) f<sub>x</sub> resta fra 533 e 536 e k<sub>1</sub> fra −0.27 e −0.30, mentre k<sub>3</sub> salta fra −0.08 e 0.25: il segno che k<sub>3</sub> è poco vincolato da questi dati (slide 56).</p></div>
""")

s(55, "Conclusions", "<p>Errori tipici e messaggi da portare a casa.</p>", kind="div", sec=("l12-conclusioni", "Conclusioni", "slide 55–59"))

s(56, "Possible Mistakes in Calibration", """
<ul>
<li><b>Copertura scarsa</b>: se tutte le immagini evitano angoli e bordi dell'inquadratura, la distorsione (più forte ai bordi) è stimata male, anche se l'errore medio sembra buono (lì non ci sono punti che lo misurino).</li>
<li><b>Degenerazione planare</b>: viste tutte (quasi) frontali, o tutte con inclinazioni simili, lasciano K poco vincolata (per questo servono viste multiple e variate).</li>
<li><b>Mosso o rilevamento scadente</b>: immagini sfocate o poco contrastate danno angoli rumorosi o distorti. Ispezionare a vista gli angoli e controllare l'errore per immagine.</li>
<li><b>Overfitting dei coefficienti di distorsione</b>: aggiungere k<sub>3</sub> (o termini più esotici) quando k<sub>1</sub>, k<sub>2</sub> già bastano adatta soprattutto il rumore e può peggiorare il modello su immagini fuori dal set di calibrazione. Aggiungere termini di ordine alto solo se il residuo lo richiede chiaramente (es. fisheye).
<ul><li>In generale la maggior parte delle camere consumer ha distorsioni piccole.</li></ul></li>
</ul>
<div class="box x"><b>Approfondimento: k<sub>3</sub> in OpenCV</b><p>Per default <code>calibrateCamera</code> stima k<sub>3</sub> (5 coefficienti). Per escluderlo: <code>flags=cv2.CALIB_FIX_K3</code>. Nel notebook k<sub>3</sub> passa da 0.01 a 0.25 cambiando solo il pattern o la finestra di raffinamento, mentre k<sub>1</sub>, k<sub>2</sub> e f restano quasi fermi: il caso descritto dalla slide.</p></div>
""")

s(57, "Take-Home Messages", """
<ul>
<li>La calibrazione stima <b>intrinseci</b>, <b>distorsione</b> e, per ogni vista, <b>R</b> e <b>t</b>, da immagini di un pannello planare noto.</li>
<li>La pipeline standard ha due passi:
<ul><li><b>stima lineare (DLT)</b>: errore in coordinate omogenee, distorsione ignorata;</li>
<li><b>raffinamento non lineare</b>: errore in coordinate cartesiane (pixel), distorsione inclusa.</li></ul></li>
<li>Controlli: errore di riproiezione per immagine e ispezione visiva delle immagini corrette.</li>
<li>Dati di calibrazione buoni (inclinazioni, distanze e copertura variate) sono fondamentali.</li>
</ul>
<p>Con la scacchiera, il passo lineare è la DLT delle omografie di Zhang (slide 41), non quella della 3×4.</p>
""")

s(58, "Further Reading", """
<ul>
<li>visionbook, <a href="https://visionbook.mit.edu/imaging_geometry.html" target="_blank">cap. 39 Camera Modeling and Calibration</a>.</li>
<li>Documentazione OpenCV: <i>Camera Calibration and 3D Reconstruction</i> (modulo calib3d, <a href="https://docs.opencv.org/4.13.0/d9/d0c/group__calib3d.html" target="_blank">docs.opencv.org/4.13.0</a>), con il tutorial <a href="https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html" target="_blank">Camera Calibration</a> da cui è preso il notebook.</li>
</ul>
<p>Per approfondire: Zhang, "A flexible new technique for camera calibration", IEEE TPAMI 2000; Hartley e Zisserman, <i>Multiple View Geometry</i>, cap. 6 (modelli di camera) e 7 (stima della matrice della camera, DLT, scomposizione); Szeliski 2a ed., § 2.1.4–2.1.5 (proiezioni e distorsione) e § 11.1 (calibrazione geometrica degli intrinseci).</p>
""")

s(59, "Next Lecture", """
<ul><li><b>Visione stereo e stima della profondità.</b></li></ul>
<p>Due camere calibrate che guardano la stessa scena: dalla differenza fra le due immagini si ricava la profondità. Serve tutto ciò che si è visto qui: K per passare dai pixel ai raggi, R e T fra le due camere.</p>
""")
