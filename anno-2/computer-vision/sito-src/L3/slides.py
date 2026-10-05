
s(1, "Copertina", """
<p><b>Signal Processing for Images: Fourier and Convolution</b>. Terza lezione.</p>
<p>Si cambia punto di vista sulle immagini: in L2 erano l'output di un processo fisico (luce, ottica, sensore), da qui in poi sono <b>segnali</b> da analizzare e trasformare.</p>
<p>È la base matematica per L5 (filtri e gradienti), L6 (aliasing e piramidi) e per capire cosa fa un layer convoluzionale.</p>
""")

s(2, "Goal of the Day", """
<ul>
<li>Pensare alle immagini come <b>segnali</b> e usare gli strumenti del signal processing 1D/2D.</li>
<li>Costruire gli strumenti, <b>convoluzione</b> e <b>trasformata di Fourier</b>, che stanno sotto a filtraggio, campionamento, compressione e progettazione delle CNN.</li>
</ul>
<p>È la lezione più matematica della prima parte, ma l'idea è semplice: scegliere una rappresentazione in cui un'operazione complicata (la convoluzione) diventa banale (un prodotto punto per punto).</p>
""")

s(3, "Outline", """
<ol>
<li>Immagini come segnali.</li>
<li>Convoluzione.</li>
<li>Trasformata di Fourier (esempi, proprietà, applicazioni e CNN).</li>
</ol>
""")

s(4, "Images as Signals", "<p>Immagine = segnale discreto; due domini (spazio e frequenza); linearità e invarianza per traslazione.</p>", kind="div", sec=("l3-segnali", "Immagini come segnali", "slide 4–12"))

s(5, "Images as Discrete Signals", """
<ul>
<li>Un'immagine è una funzione continua f(x, y) <b>campionata su una griglia</b>: f[m, n], con m = 0, …, M−1 e n = 0, …, N−1.</li>
<li>I pixel sono campioni della scena: scena → ottica → immagine continua → griglia di pixel <b>campionata e quantizzata</b> (L2).</li>
<li>Due viste complementari:
<ul><li><b>dominio spaziale</b>: si ragiona su trasformazioni invarianti per traslazione;</li>
<li><b>dominio frequenziale</b>: l'immagine è una sovrapposizione di onde.</li></ul></li>
<li>Le due viste sono collegate dal <b>teorema di convoluzione</b>: convoluzione nello spazio = prodotto punto per punto in frequenza (slide 63).</li>
</ul>
<p>Convenzione: le parentesi quadre [·] indicano segnali discreti, le tonde (·) segnali continui.</p>
<div class="box b"><b>Dal libro · cap. 15, § 15.2 Signals and Images</b>
<ul>
<li>Il libro scrive l'immagine come ℓ ∈ ℝ<sup>M×N</sup> (M righe = altezza, N colonne = larghezza) e il pixel come <b>ℓ[n, m]</b>, con <b>n orizzontale</b> ∈ [0, N−1] e <b>m verticale</b> ∈ [0, M−1]. La slide 5 scrive f[m, n]; da slide 11 in poi le slide usano la notazione del libro.</li>
<li>Campionamento: ℓ[n] = ℓ(n ΔT), con ΔT passo di campionamento (tonde = continuo, quadre = discreto).</li>
<li>Grandezze di un segnale da conoscere: <b>valore DC</b> (media) μ = (1/N) ∑<sub>n</sub> ℓ[n]; <b>energia</b> E = ∑<sub>n</sub> |ℓ[n]|²; distanza fra segnali D² = (1/N) ∑<sub>n</sub> |ℓ<sub>1</sub>[n] − ℓ<sub>2</sub>[n]|². Un segnale è <b>periodico</b> di periodo N se ℓ[n] = ℓ[n + kN] per ogni n e k.</li>
</ul><p>Il DC tornerà come coefficiente ℒ[0, 0] della DFT (slide 49). <a href="https://visionbook.mit.edu/linear_image_filtering.html">visionbook, cap. 15</a></p></div>
""")

s(6, "Images as Superposition of Waves", """
<p><b>Figura:</b> tre immagini con il loro spettro di ampiezza |F|.</p>
<ul>
<li>Strisce verticali larghe (bassa frequenza): due punti vicini al centro dello spettro.</li>
<li>Strisce verticali fitte (alta frequenza): due punti lontani dal centro, sull'asse orizzontale.</li>
<li>Somma delle due: lo spettro contiene tutti e quattro i punti.</li>
</ul>
<p>Punto: ogni sinusoide pura è una coppia di punti simmetrici nello spettro (slide 57), e lo spettro di una somma è la somma degli spettri (linearità). Un'immagine qualunque è una somma pesata di onde 2D; lo spettro dice quanto pesa ciascuna.</p>
""")

s(7, "Two Views: Spatial vs. Frequency", """
<ul>
<li>Stessa immagine, due rappresentazioni <b>equivalenti</b> (nessuna perdita di informazione) legate dalla trasformata di Fourier: griglia di pixel e oscillazioni.</li>
<li>Le CNN lavorano nel dominio spaziale, ma ogni filtro convoluzionale ha una <b>risposta in frequenza</b>: la rete fa implicitamente un'elaborazione selettiva in frequenza.
<ul><li>i bordi sono contenuto ad alta frequenza;</li><li>il rumore è (spesso) ad alta frequenza.</li></ul></li>
<li>In frequenza certe operazioni (filtraggio) e proprietà (periodicità, scala) sono molto più facili da ragionare:
<ul><li>il blur toglie/attenua le alte frequenze;</li><li>l'aliasing nasce da operazioni come il downsampling ingenuo.</li></ul></li>
</ul>
<div class="box w"><b>Attenzione: definizione imprecisa di aliasing</b><p>La slide chiama l'aliasing "rumore ad alta frequenza". È il contrario: l'aliasing è contenuto ad alta frequenza che, dopo un campionamento troppo rado, <b>ricompare come falsa bassa frequenza</b> (moiré, scalini, pattern che non esistono). Definizione completa in L6.</p></div>
""")

s(8, "Fourier Transform as a Change of Basis", """
<ul>
<li>Spazio e frequenza sembrano molto diversi, ma passare dall'uno all'altro è un'operazione <b>lineare</b>.</li>
<li>È un <b>cambio di base</b>: si rappresenta il segnale in coordinate in cui l'operazione che interessa diventa semplice.</li>
<li>La base di Fourier è comodissima perché la convoluzione diventa un prodotto punto per punto.</li>
</ul>
<div class="box k"><b>Idea guida della lezione</b><p>È come diagonalizzare una matrice: nella base degli autovettori l'operatore agisce moltiplicando ogni coordinata per uno scalare. Gli esponenziali complessi sono proprio gli autovettori di ogni convoluzione (slide 29 e 44).</p></div>
""")

s(9, "Translation Invariance", """
<ul>
<li>Un uccello è un uccello ovunque si trovi nell'immagine.</li>
<li>L'<b>invarianza alla traslazione</b> è una proprietà fondamentale di molti task di visione.</li>
</ul>
<p><b>Figura:</b> stormo di gru in volo; lo stesso oggetto compare in posizioni diverse.</p>
<div class="box k"><b>Distinzione da orale</b><ul>
<li><b>Equivarianza</b>: se trasli l'input, l'output trasla allo stesso modo. È ciò che garantisce la convoluzione.</li>
<li><b>Invarianza</b>: se trasli l'input, l'output non cambia. Si ottiene aggiungendo un'aggregazione (es. global pooling) dopo operazioni equivarianti.</li>
</ul><p>Detection e segmentazione vogliono equivarianza (la maschera si deve spostare con l'oggetto), la classificazione vuole invarianza.</p></div>
""")

s(10, "Linearity", """
<ul>
<li>Molte operazioni interessanti sono anche <b>lineari</b>: l'output è una combinazione lineare degli input.</li>
<li>Domanda della slide: quali operazioni della figura sono lineari? Quali si possono implementare come convoluzioni?</li>
<li>Le immagini sono a colori, ma quasi tutto vale in scala di grigi: ogni canale si tratta separatamente.</li>
</ul>
<p><b>Figura:</b> cubo rosso trasformato con (A) rotazione, (B) scaling, (C) rgb2gray, (D) defocus.</p>
<div class="box k"><b>Risposta</b><ul>
<li>Sono <b>tutte lineari</b> nei valori dei pixel: ogni pixel di output è una combinazione lineare di pixel di input.</li>
<li>Rotazione e scaling <b>non sono invarianti per traslazione</b>: cosa succede a un pixel dipende da dove si trova (lontano dal centro si sposta di più). Non sono convoluzioni.</li>
<li>Defocus: stessa sfocatura ovunque, è una convoluzione (slide 19–20).</li>
<li>rgb2gray: combinazione pesata dei canali pixel per pixel, invariante per traslazione. In gergo CNN è una convoluzione 1×1 sui canali.</li>
</ul></div>
<div class="box b"><b>Dal libro · cap. 15, § 15.3.1 Linear Systems</b>
<p>Il libro parte dal sistema lineare più generale: ogni output è una somma pesata di <b>tutti</b> gli input,</p>
<span class="f">ℓ<sub>out</sub>[n] = ∑<sub>k</sub> h[n, k] ℓ<sub>in</sub>[k],   cioè ℓ<sub>out</sub> = H ℓ<sub>in</sub></span>
<ul>
<li>È esattamente un <b>layer fully connected</b> (fig. 15.4): una matrice piena, un peso per ogni coppia input/output. Rotazione, scaling, rgb2gray e defocus della fig. 15.3 si scrivono tutte così ("all of them!").</li>
<li>Aggiungere l'invarianza per traslazione impone h[n, k] = h[n − k]: il peso dipende solo dalla <b>distanza</b> fra input e output. La matrice diventa a bande e ogni riga usa gli stessi pesi (fig. 15.6): è il passaggio da layer denso a <b>layer convoluzionale</b>, con weight sharing e numero di parametri pari alla dimensione del kernel invece che N×N.</li>
</ul><p><a href="https://visionbook.mit.edu/linear_image_filtering.html">visionbook, cap. 15</a></p></div>
""")

s(11, "Linear, Shift-Invariant (LSI) Systems", """
<ul>
<li>Sistema T <b>lineare</b>:
<span class="f">T[a f<sub>1</sub> + b f<sub>2</sub>] = a T[f<sub>1</sub>] + b T[f<sub>2</sub>]</span></li>
<li>Sistema <b>invariante per traslazione</b> (shift-invariant): traslando l'input, l'output trasla allo stesso modo.
<span class="f">ℓ<sub>out</sub>[n − n<sub>0</sub>, m − m<sub>0</sub>] = f(ℓ<sub>in</sub>[n − n<sub>0</sub>, m − m<sub>0</sub>])</span></li>
<li>Una <b>convoluzione</b> è un sistema LSI.</li>
</ul>
<p><b>Figura:</b> esempi di operatori LSI sulla stessa foto: blur, sharpen, filtro di bordo.</p>
<div class="box k"><b>Come leggere la formula</b><p>Qui f è il sistema, non un segnale. Scritta per esteso: se ℓ<sub>out</sub> = T[ℓ<sub>in</sub>], allora applicando T a ℓ<sub>in</sub>[n − n<sub>0</sub>, m − m<sub>0</sub>] si ottiene ℓ<sub>out</sub>[n − n<sub>0</sub>, m − m<sub>0</sub>]. Per verificare che un'operazione è LSI si controllano separatamente le due proprietà.</p></div>
<div class="box b"><b>Dal libro · cap. 15, § 15.3.2 Linear Translation Invariant Systems</b>
<ul>
<li>Il libro chiama questi sistemi <b>LTI</b> (linear translation invariant); le slide dicono LSI. Sono la stessa cosa. La formula della slide, con f come nome del sistema, è presa dal libro.</li>
<li>Esempio del libro: la media locale su una finestra 5×5,
<span class="f">ℓ<sub>out</sub>[n, m] = (1/25) ∑<sub>k=−2</sub><sup>2</sup> ∑<sub>l=−2</sub><sup>2</sup> ℓ<sub>in</sub>[n + k, m + l]</span>
è lineare e uguale in ogni posizione, quindi LTI.</li>
<li>Il libro afferma che linearità + invarianza "costringono" il sistema a essere una convoluzione, senza dimostrarlo: la dimostrazione è nel riquadro della slide 18.</li>
</ul><p><a href="https://visionbook.mit.edu/linear_image_filtering.html">visionbook, cap. 15</a></p></div>
""")

s(12, "Summary", """
<ul>
<li>Le immagini sono segnali. Conseguenza (L6): i problemi del campionamento discreto.</li>
<li>I sistemi LSI sono una classe semplice di operazioni che si può analizzare a fondo:
<ul><li>molte operazioni comuni di preprocessing sono LSI (L5);</li>
<li>si analizzano sia nel dominio spaziale (kernel di convoluzione) sia in quello frequenziale (Fourier).</li></ul></li>
</ul>
""")

s(13, "Convolution", "<p>Definizione, esempi, proprietà algebriche e conseguenze computazionali.</p>", kind="div", sec=("l3-conv", "Convoluzione", "slide 13–31"))

s(14, "2D Discrete Convolution", """
<span class="f">(f ∗ h)[m, n] = ∑<sub>i</sub> ∑<sub>j</sub> f[i, j] · h[m − i, n − j]</span>
<ul>
<li>∗ indica la convoluzione, non la moltiplicazione.</li>
<li>Con kernel finiti la somma è solo sul supporto del kernel (3×3, 5×5, …).</li>
<li>È l'operazione alla base del filtraggio di immagini e dei layer "convoluzionali" delle CNN.
<ul><li>Nelle reti si usa in realtà la <b>cross-correlazione</b> (niente flip del kernel), ma per kernel appresi le due sono equivalenti (slide 28).</li></ul></li>
</ul>
<p><b>Figura</b> (conv_arithmetic): un kernel 3×3 che scorre su un input 5×5 con padding, producendo una mappa di output.</p>
<div class="box k"><b>Da saper spiegare</b><p>Il segno meno in h[m − i, n − j] è il "flip": per calcolare l'output in (m, n) si ribalta il kernel e lo si centra in (m, n). Ogni output è un prodotto scalare fra il kernel ribaltato e un intorno dell'input.</p></div>
<div class="box b"><b>Dal libro · cap. 15, § 15.4 Convolution</b>
<ul>
<li>Il libro indica la convoluzione con <b>∘</b> (non ∗) e la definisce con il kernel davanti: ℓ<sub>out</sub>[n] = h[n] ∘ ℓ<sub>in</sub>[n] = ∑<sub>k</sub> h[n − k] ℓ<sub>in</sub>[k]. Per la commutatività è la stessa cosa della slide.</li>
<li>Procedura in quattro passi: (1) specchia il kernel, h[k] → h[−k]; (2) spostalo con l'origine in n; (3) moltiplica per i valori dell'input sotto di esso; (4) somma: è ℓ<sub>out</sub>[n].</li>
<li>Esempio del libro, kernel h[−1] = 1, h[0] = 2, h[1] = 3:
<span class="f">ℓ<sub>out</sub>[n] = 3 ℓ<sub>in</sub>[n − 1] + 2 ℓ<sub>in</sub>[n] + 1 ℓ<sub>in</sub>[n + 1]</span>
Nota come i pesi compaiono <b>in ordine inverso</b>: è il flip. In forma matriciale la matrice ha h[0] sulla diagonale, h[1] sotto e h[−1] sopra (matrice a bande, di Toeplitz).</li>
</ul><p><a href="https://visionbook.mit.edu/linear_image_filtering.html">visionbook, cap. 15</a></p></div>
""")

s(15, "Continuous Convolution", """
<p>Convoluzione continua 1D:</p>
<span class="f">(f ∗ h)(x) = ∫<sub>−∞</sub><sup>+∞</sup> f(τ) h(x − τ) dτ</span>
<ul>
<li>h è il <b>kernel</b>.</li>
<li>L'output in x è una somma pesata dei valori dell'input vicini a x.</li>
</ul>
<p>Convoluzione continua 2D:</p>
<span class="f">(f ∗ h)(x, y) = ∬ f(τ, σ) h(x − τ, y − σ) dτ dσ</span>
<p>(Qui σ è solo una variabile di integrazione, non la deviazione standard.)</p>
<div class="box b"><b>Dal libro · cap. 15, § 15.4.5 Convolution in the Continuous Domain</b>
<p>Nel continuo l'elemento neutro è la <b>delta di Dirac</b> δ(t): nulla ovunque tranne che nell'origine, con area 1 (∫ δ(t) dt = 1); si disegna come una freccia di altezza 1. Proprietà che il libro elenca e che servono in L6 (campionamento):</p>
<ul>
<li>scala: δ(at) = δ(t)/|a|; simmetria: δ(−t) = δ(t);</li>
<li>campionamento: ℓ(t) δ(t − a) = ℓ(a) δ(t − a);</li>
<li>setaccio: ∫ ℓ(t) δ(t − a) dt = ℓ(a); identità: ℓ(t) ∘ δ(t) = ℓ(t).</li>
</ul><p>Attenzione a non confonderla con la delta discreta δ[n], che vale semplicemente 1 in n = 0. <a href="https://visionbook.mit.edu/linear_image_filtering.html">visionbook, cap. 15</a></p></div>
""")

s(16, "1D Example", """
<p>Segnale f = [1, 2, 3, 4], kernel h = [1, 0, −1], convoluzione <b>full</b>:</p>
<ul>
<li>si ribalta h → [−1, 0, 1];</li>
<li>lo si fa scorrere e si calcola il prodotto scalare a ogni shift;</li>
<li>risultato (modo full, zero-padding, lunghezza 4 + 3 − 1 = 6):</li>
</ul>
<span class="f">f ∗ h = [1, 2, 2, 2, −3, −4]</span>
<p>Interpretazione: il kernel approssima una <b>derivata discreta</b>. Risposta grande dove il segnale cambia (bordi), vicina a zero dove è piatto.</p>
<div class="box k"><b>Da saper fare</b>
<p>y[n] = ∑<sub>i</sub> f[i] h[n − i]: y[0] = 1·1 = 1; y[1] = 2·1 + 1·0 = 2; y[2] = 3·1 + 2·0 + 1·(−1) = 2; y[3] = 4 − 2 = 2; y[4] = 3·(−1) = −3 (più 4·0); y[5] = 4·(−1) = −4.</p>
<p>All'interno y[n] = f[n] − f[n−2]: è la differenza centrata, moltiplicata per 2. I valori −3 e −4 in fondo sono effetti di bordo (il segnale "cade" a zero per lo zero-padding).</p>
<p>Lunghezze: full = N + k − 1, same = N, valid = N − k + 1.</p></div>
""")

s(17, "2D example", """
<p><b>Figura</b> (visionbook): ℓ<sub>in</sub> è una forma binaria bianca su fondo nero (griglia 9×9). Il kernel h[n, m] è 3×3 con colonne 1, 0, −1; accanto c'è la versione ribaltata h[−n, −m] (colonne −1, 0, 1). A destra ℓ<sub>out</sub>.</p>
<ul>
<li>I riquadri rossi e verdi mostrano due posizioni: la finestra 3×3 nell'input e il pixel di output corrispondente.</li>
<li>L'output è positivo sui bordi sinistri della forma, negativo su quelli destri, zero dove l'input è uniforme: è una <b>derivata orizzontale</b>.</li>
</ul>
<p>Punto: la stessa finestra di pesi si applica identica in ogni posizione. È l'invarianza per traslazione, ed è il motivo del <b>weight sharing</b> nelle CNN.</p>
""")

s(18, "What Operations Are LSI?", """
<ul>
<li>Sono LSI: blurring, sharpening, edge detection, qualunque kernel di convoluzione fisso.</li>
<li>Non sono LSI:
<ul><li>thresholding, correzione gamma: <b>non lineari</b>;</li>
<li>cropping, resizing: <b>non invarianti per traslazione</b>;</li>
<li>la maggior parte delle nonlinearità delle CNN (ReLU, …).</li></ul></li>
<li>Un sistema è LSI <b>se e solo se</b> si scrive come y = h ∗ x per un kernel fisso h.</li>
</ul>
<div class="box k"><b>Da saper dimostrare (idea)</b><p>Scrivi l'input come somma di impulsi traslati: x[n] = ∑<sub>k</sub> x[k] δ[n − k]. Per linearità T[x] = ∑<sub>k</sub> x[k] T[δ[n − k]]; per invarianza T[δ[n − k]] = h[n − k], con h = T[δ]. Quindi T[x] = ∑<sub>k</sub> x[k] h[n − k] = (x ∗ h)[n]. Il kernel è la <b>risposta all'impulso</b> (slide 65).</p></div>
<div class="box b"><b>Dal libro · cap. 15, § 15.6 System Identification</b>
<ul>
<li>Se in ingresso a un filtro LTI metti δ[n], esce h[n]; se metti δ[n − n<sub>0</sub>], esce h[n − n<sub>0</sub>]. Per questo il kernel si chiama <b>risposta all'impulso</b>, e un sistema LTI sconosciuto si "identifica" misurandone la risposta a un impulso.</li>
<li>Esempio del libro: l'acustica di una stanza è un sistema LTI. Un battito di mani approssima un impulso e l'eco registrata è h. Con un percorso diretto e tre riflessioni:
<span class="f">h(t) = a<sub>0</sub> δ(t) + a<sub>1</sub> δ(t − T<sub>1</sub>) + a<sub>2</sub> δ(t − T<sub>2</sub>) + a<sub>3</sub> δ(t − T<sub>3</sub>)</span>
quindi chi ascolta sente ℓ<sub>out</sub>(t) = a<sub>0</sub> ℓ<sub>in</sub>(t) + a<sub>1</sub> ℓ<sub>in</sub>(t − T<sub>1</sub>) + …: copie ritardate e attenuate della voce (fig. 15.14–15.16).</li>
</ul><p>Equivalente in visione: l'immagine di un punto luminoso attraverso un'ottica è la sua risposta all'impulso (PSF, L2). <a href="https://visionbook.mit.edu/linear_image_filtering.html">visionbook, cap. 15</a></p></div>
""")

s(19, "LSI Operations", """
<p><b>Figura</b> (visionbook):</p>
<ul>
<li>(a) <b>Defocusing</b>: due riquadri in punti diversi del cubo vengono trasformati nello stesso modo (stessa sfocatura). È LSI.</li>
<li>(b) <b>Rotazione</b>: le frecce mostrano che punti diversi si spostano di quantità e in direzioni diverse. È lineare ma non invariante per traslazione.</li>
</ul>
<p>Utile all'orale: saper classificare al volo un'operazione, verificando separatamente linearità e invarianza.</p>
""")

s(20, "Blur as an LSI Operation", """
<ul>
<li>Sfocare = sostituire ogni pixel con una <b>media pesata dei vicini</b>.</li>
<li>La stessa regola si applica in ogni posizione (invariante) e il risultato è una somma pesata (lineare), quindi il blur è LSI, cioè una convoluzione.</li>
<li>Lo schema dei pesi (es. una gaussiana) è esattamente il kernel h.</li>
</ul>
<p>Collegamento con L2: il pinhole reale con foro finito produce proprio un blur; la matrice A del modello di formazione dell'immagine era vicina all'identità con dispersione sui vicini.</p>
""")

s(21, "2D Example: Gaussian Blur", """
<span class="f">h(x, y) = 1/(2πσ²) · exp(−(x² + y²) / (2σ²))</span>
<ul>
<li>Esempio: convoluzione con un kernel gaussiano 5×5, σ = 2.</li>
<li>Risultato: i bordi netti diventano una <b>rampa morbida</b> su qualche pixel.</li>
<li>σ più grande = supporto più largo = più smoothing.</li>
</ul>
<p><b>Figura:</b> un bordo verticale netto, lo stesso dopo il blur, e il profilo della riga 32: il gradino (blu) diventa una rampa (arancione).</p>
<div class="box x"><b>Approfondimento: dimensione del kernel</b><p>Una gaussiana va troncata a circa ±3σ (kernel di lato ≈ 6σ + 1). Un 5×5 con σ = 2 copre solo ±1σ: è una gaussiana molto troncata, più vicina a un box. In pratica si sceglie prima σ e poi la dimensione, non il contrario (es. OpenCV usa circa ±3σ). Il fattore 1/(2πσ²) normalizza la gaussiana continua; nel discreto si divide per la somma dei pesi.</p></div>
""")

s(22, "Some Common Kernels", """
<p><b>Blur</b></p>
<ul>
<li><b>Box</b>: media uniforme, h = (1/9)·[[1,1,1],[1,1,1],[1,1,1]].</li>
<li><b>Gaussiana</b>: h(x, y) = 1/(2πσ²) · exp(−(x² + y²)/(2σ²)), liscia e senza ringing.</li>
</ul>
<p><b>Approssimazioni di derivata</b></p>
<ul>
<li><b>Sobel</b>: S<sub>x</sub> = [[−1,0,1],[−2,0,2],[−1,0,1]].</li>
</ul>
<p><b>Figura:</b> originale, box 9×9, gaussiana σ = 3, Sobel. Il box dà un blur più "squadrato", la gaussiana più naturale; il Sobel lascia solo i contorni.</p>
<div class="box x"><b>Approfondimento</b><ul>
<li>Il box in frequenza è una sinc, con lobi laterali: lascia passare parte delle alte frequenze e può invertirne il segno. La gaussiana ha trasformata gaussiana, quindi attenua in modo monotono.</li>
<li>Sobel = derivata centrata [−1, 0, 1] in x per smoothing [1, 2, 1] in y: è separabile (slide 25). Si riprende in L5.</li>
<li>Come scritto, S<sub>x</sub> dà la derivata positiva se usato in cross-correlazione (come nelle librerie); in convoluzione vera il flip cambia il segno.</li></ul></div>
""")

s(23, "Properties of Convolution", """
<ul>
<li><b>Linearità</b>: f ∗ (a h<sub>1</sub> + b h<sub>2</sub>) = a (f ∗ h<sub>1</sub>) + b (f ∗ h<sub>2</sub>).</li>
<li><b>Equivarianza alla traslazione</b>: se l'input trasla di (n<sub>0</sub>, m<sub>0</sub>), l'output trasla della stessa quantità.</li>
<li><b>Commutatività</b>: f ∗ h = h ∗ f.</li>
<li><b>Associatività</b>: (f ∗ h<sub>1</sub>) ∗ h<sub>2</sub> = f ∗ (h<sub>1</sub> ∗ h<sub>2</sub>). Si possono concatenare filtri convolvendo prima i kernel.</li>
<li><b>Identità</b>: l'impulso δ è l'elemento neutro, δ ∗ ℓ = ℓ, con δ[n] = 1 se n = 0, 0 altrimenti.</li>
</ul>
<div class="box k"><b>Da sapere</b><p>Queste proprietà valgono per la convoluzione, non per la cross-correlazione (che non è commutativa). Commutatività e associatività si vedono subito in frequenza: sono commutatività e associatività del prodotto di numeri (slide 63).</p></div>
<div class="box b"><b>Dal libro · cap. 15, § 15.4.1–15.4.2 Properties and Examples</b>
<ul>
<li>Il libro aggiunge la <b>distributività</b>: ℓ<sub>1</sub> ∘ (ℓ<sub>2</sub> + ℓ<sub>3</sub>) = ℓ<sub>1</sub> ∘ ℓ<sub>2</sub> + ℓ<sub>1</sub> ∘ ℓ<sub>3</sub>, e il <b>supporto</b>: convolvendo segnali lunghi N e M il risultato è lungo al più N + M − 1.</li>
<li>Avvertenza del libro: con segnali finiti l'associatività può non valere esattamente, perché dipende da come si gestiscono i bordi (slide 27).</li>
<li>Esempi (fig. 15.9, zero padding): kernel δ[n, m] → immagine invariata; impulso traslato di 2 pixel → immagine traslata di 2 pixel, con una striscia nera di 2 pixel sul lato da cui entra lo zero padding; 0,5 δ[n − 2, m − 2] + 0,5 δ[n + 2, m + 2] → due copie sovrapposte spostate in diagonale; kernel uniforme 5×5 da 1/25 → sfocatura.</li>
</ul><p>Morale: un kernel fatto di impulsi <b>sposta e somma copie</b> dell'immagine; ogni kernel è una combinazione di impulsi, quindi ogni convoluzione è una somma pesata di copie traslate. <a href="https://visionbook.mit.edu/linear_image_filtering.html">visionbook, cap. 15</a></p></div>
""")

s(24, "Computational Consequence of Associativity", """
<ul>
<li>(f ∗ h<sub>1</sub>) ∗ h<sub>2</sub> = f ∗ (h<sub>1</sub> ∗ h<sub>2</sub>): si convolvono prima i kernel, poi si applica il risultato <b>una volta sola</b> all'immagine.</li>
<li>Esempio: due blur 5×5 in sequenza = un solo kernel equivalente 9×9, calcolato una volta.</li>
<li>Serve a fondere catene di filtri in un unico kernel equivalente.</li>
</ul>
<div class="box k"><b>Da sapere</b><ul>
<li>Dimensione: k<sub>1</sub> + k<sub>2</sub> − 1 = 5 + 5 − 1 = 9.</li>
<li>Non è detto che convenga: un 9×9 costa 81 moltiplicazioni per pixel, due 5×5 ne costano 50. La fusione conviene quando i kernel sono tanti e piccoli, o per analizzare il filtro complessivo.</li>
<li>Se fra i due filtri c'è una nonlinearità (CNN) la fusione non è possibile (slide 72).</li></ul></div>
""")

s(25, "Separable Filters", """
<ul>
<li>Un kernel 2D è <b>separabile</b> se h(x, y) = h<sub>x</sub>(x) · h<sub>y</sub>(y), con h<sub>x</sub> vettore riga e h<sub>y</sub> vettore colonna.</li>
<li>La gaussiana è separabile: G<sub>σ</sub>(x, y) = G<sub>σ</sub>(x) · G<sub>σ</sub>(y).</li>
<li>Si convolve prima per righe e poi per colonne (due passate 1D) invece di fare la convoluzione 2D.</li>
<li>Costo con immagine M×N e kernel k×k:
<span class="f">2D: O(MN k²)   separabile: O(MNk + MNk) = O(MNk)</span></li>
</ul>
<p>Esempio: (1/3)[1, 1, 1]<sup>T</sup> · (1/3)[1, 1, 1] = (1/9) · matrice 3×3 di uni (prodotto esterno colonna × riga).</p>
<div class="box k"><b>Da saper fare</b><ul>
<li>Un kernel è separabile se e solo se, come matrice, ha <b>rango 1</b>. Il Sobel è separabile ([1,2,1]<sup>T</sup> · [−1,0,1]); il laplaciano 3×3 [[0,1,0],[1,−4,1],[0,1,0]] no.</li>
<li>Con k = 9: 81 contro 18 moltiplicazioni per pixel.</li>
<li>Perché la gaussiana è separabile: exp(−(x² + y²)/2σ²) = exp(−x²/2σ²) · exp(−y²/2σ²).</li></ul></div>
""")

s(26, "Depthwise Separable Convolutions", """
<p>Trucco comune nelle reti per dispositivi con poche risorse (MobileNet, EfficientNet).</p>
<ul>
<li><b>Convoluzione standard</b>: ogni canale di output mescola tutti i canali di input con un kernel k × k × C<sub>in</sub>.</li>
<li><b>Depthwise separable</b>, in due passi:
<ol><li>convoluzione <b>depthwise</b> k × k, indipendente per ogni canale;</li>
<li>convoluzione <b>pointwise</b> 1 × 1 per mescolare i canali.</li></ol></li>
<li>Parametri/FLOPs (per posizione, C canali in e out): O(k²C + C²) invece di O(k²C²).</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>k = 3, C = 256: standard 9 · 256² ≈ 590k parametri; separabile 9 · 256 + 256² ≈ 68k, circa 8,7 volte meno. In generale il rapporto è 1/C + 1/k².</p>
<p>Idea concettuale: è la stessa separazione della slide 25, ma fra asse spaziale e asse dei canali invece che fra righe e colonne.</p></div>
""")

s(27, "Boundary Handling", """
<p>Ai bordi mancano i vicini. Strategie comuni:</p>
<ul>
<li><b>Zero padding</b>: fuori vale 0. Può scurire i bordi.</li>
<li><b>Replicate (clamp)</b>: si ripetono i pixel di bordo.</li>
<li><b>Reflect (mirror)</b>: si specchia l'immagine oltre il bordo.</li>
<li><b>Circular (wrap)</b>: l'immagine è periodica. È ciò che fa implicitamente la convoluzione via DFT.</li>
</ul>
<p>La scelta cambia gli artefatti. <b>Figura:</b> la stessa patch con le quattro strategie (riquadro rosso = regione originale): nero attorno con zero pad, strisce stirate con replicate, copia speculare con reflect, pezzi del lato opposto con wrap.</p>
<div class="box x"><b>Approfondimento</b><p>Con il wrap il bordo destro "vede" il bordo sinistro: se sono molto diversi, il filtro crea artefatti. È lo stesso problema dei bordi nella DFT, che vede l'immagine come periodica e quindi con un salto netto ai bordi (la croce luminosa sugli assi negli spettri delle slide 38 e 54).</p></div>
<div class="box b"><b>Dal libro · cap. 15, § 15.4.3 Handling Boundaries</b>
<ul>
<li>Il libro confronta le strategie in modo quantitativo (fig. 15.10): filtra un ritaglio con un box 11×11 (pesi 1/121) usando le varie estensioni e misura l'errore rispetto al risultato "vero", calcolato sull'immagine più grande da cui il ritaglio viene. Il <b>mirror</b> dà l'errore più piccolo, lo <b>zero padding</b> il più grande.</li>
<li>Lo zero padding resta il default nelle reti neurali, nonostante scurisca i bordi.</li>
<li>Padding circolare scritto con il modulo: ℓ<sub>in</sub>[n, m] = ℓ<sub>in</sub>[(n)<sub>P</sub>, (m)<sub>Q</sub>], dove (n)<sub>P</sub> = n mod P. Trasforma il segnale finito in un segnale periodico infinito: comodo per l'analisi (è ciò che assume la DFT) ma introduce artefatti.</li>
</ul><p><a href="https://visionbook.mit.edu/linear_image_filtering.html">visionbook, cap. 15</a></p></div>
""")

s(28, "Cross-Correlation vs. Convolution", """
<ul>
<li><b>Convoluzione</b>: (f ∗ h)[m, n] = ∑<sub>i,j</sub> f[i, j] h[m − i, n − j]. Il kernel viene ribaltato.</li>
<li><b>Cross-correlazione</b>: (f ⋆ h)[m, n] = ∑<sub>i,j</sub> f[i, j] h[m + i, n + j]. Nessun ribaltamento.</li>
<li>Per kernel simmetrici (gaussiana, box) coincidono.</li>
<li>Le CNN implementano la cross-correlazione: per kernel appresi non conta (la rete impara direttamente il kernel ribaltato); conta per filtri progettati a mano e per la teoria.</li>
</ul>
<p><b>Figura</b> (Wikimedia): convoluzione, cross-correlazione e autocorrelazione di un rettangolo f e di una rampa g. Nella convoluzione g appare ribaltata; f ∗ g = g ∗ f, mentre f ⋆ g e g ⋆ f sono una lo specchio dell'altra: la cross-correlazione <b>non è commutativa</b>.</p>
<div class="box x"><b>Approfondimento: convenzioni</b><p>La formula della slide è la definizione "da manuale" (tipo Wikipedia) con f al primo posto. Nelle librerie di deep learning l'operazione è scritta con il kernel che scorre sull'immagine: y[m, n] = ∑<sub>i,j</sub> h[i, j] · f[m + i, n + j]. Le due differiscono solo per il verso dello spostamento. Da ricordare: correlazione = convoluzione con il kernel ribaltato.</p></div>
<div class="box b"><b>Dal libro · cap. 15, § 15.5 Cross-Correlation Versus Convolution</b>
<ul>
<li>Il libro scrive la correlazione come la calcolano le librerie, con l'offset k sommato alla posizione:
<span class="f">ℓ<sub>out</sub>[n, m] = ℓ<sub>in</sub> ⋆ h = ∑<sub>k,l</sub> ℓ<sub>in</sub>[n + k, m + l] h[k, l]</span>
mentre la convoluzione usa ℓ<sub>in</sub>[n − k, m − l]. La formula della slide (immagine al primo posto e h[m + i, n + j]) produce la stessa mappa ma <b>specchiata</b> rispetto all'origine: è una convenzione diversa, non la stessa formula.</li>
<li>Fig. 15.11: con un kernel a triangolo che punta in su, la convoluzione di quattro punti luminosi disegna triangoli in su, la correlazione triangoli in giù. Su un'immagine con triangoli in su e in giù, la correlazione ha il massimo sui triangoli <b>uguali al kernel</b>: per cercare un pattern serve la correlazione.</li>
<li><b>Template matching</b> (§ 15.5.1, omesso dalle slide): la correlazione grezza risponde forte in ogni zona chiara. Si usa la <b>correlazione normalizzata</b>: kernel ĥ a media zero e norma unitaria, e divisione per la deviazione standard locale σ[n, m] dell'immagine sulla finestra,
<span class="f">ℓ<sub>out</sub>[n, m] = (1/σ[n, m]) ∑<sub>k,l</sub> ℓ<sub>in</sub>[n + k, m + l] ĥ[k, l]</span>
Nell'esempio della lettera "a" (fig. 15.12) trova le occorrenze indipendentemente dalla luminosità, ma il libro avverte che è fragile: non regge rotazioni, cambi di scala o di font.</li>
</ul><p><a href="https://visionbook.mit.edu/linear_image_filtering.html">visionbook, cap. 15</a></p></div>
""")

s(29, "Convolution as Matrix Multiplication", """
<ul>
<li>La convoluzione con un kernel fisso è un <b>operatore lineare</b> sul vettore dei pixel (immagine appiattita), quindi si scrive come matrice.</li>
<li>Per la convoluzione <b>circolare</b> 1D la matrice è <b>circolante</b> (un caso particolare di Toeplitz):
<span class="f">y = Hx,   H<sub>ij</sub> = h[(i − j) mod N]</span></li>
</ul>
<p><b>Figura:</b> matrice circolante 16×16 di un blur 1D: diagonale principale 0.5, diagonali adiacenti 0.25 (kernel [0.25, 0.5, 0.25]), più due elementi negli angoli opposti: è il wrap-around.</p>
<div class="box k"><b>Collegamenti</b><ul>
<li>È la matrice A di L2 quando la camera applica un blur.</li>
<li>Tutte le matrici circolanti N×N hanno gli stessi autovettori: le onde di Fourier. Quindi la matrice di Fourier le <b>diagonalizza</b> tutte, e gli autovalori sono la DFT di h. È il motivo profondo del teorema di convoluzione (slide 63).</li></ul></div>
<div class="box b"><b>Dal libro · cap. 15, § 15.4.4 Circular Convolution</b>
<p>Per due segnali di uguale lunghezza N:</p>
<span class="f">ℓ<sub>out</sub>[n] = h[n] ∘<sub>N</sub> ℓ<sub>in</sub>[n] = ∑<sub>k=0</sub><sup>N−1</sup> h[(n − k)<sub>N</sub>] ℓ<sub>in</sub>[k]</span>
<ul>
<li>(n − k)<sub>N</sub> è l'indice modulo N: si usa l'estensione periodica di h. Anche l'output è periodico di periodo N.</li>
<li>Valgono le stesse proprietà della convoluzione (commutativa, associativa, …) ed è quella per cui vale esattamente il teorema di convoluzione con la DFT (§ 16.7.4, slide 63).</li>
<li>In forma matriciale è la matrice <b>circolante</b> della figura; la convoluzione lineare su segnale finito con zero padding dà invece la matrice a bande della slide 14 (senza gli elementi negli angoli).</li>
</ul><p><a href="https://visionbook.mit.edu/linear_image_filtering.html">visionbook, cap. 15</a></p></div>
""")

s(30, "Example: Convolution Matrix", """
<ul>
<li>Segnale x = [1, 2, 3, 4]<sup>T</sup>, kernel circolare h = [1, −1, 0, 0].</li>
<li>Matrice circolante:</li>
</ul>
<span class="f">H = [[1, 0, 0, −1], [−1, 1, 0, 0], [0, −1, 1, 0], [0, 0, −1, 1]]</span>
<ul>
<li>Hx = [1 − 4, 2 − 1, 3 − 2, 4 − 3]<sup>T</sup> = [−3, 1, 1, 1]<sup>T</sup>, che coincide con la convoluzione circolare di x con h.</li>
</ul>
<p>Il kernel fa la differenza all'indietro y[n] = x[n] − x[n − 1]. Il −3 iniziale è l'artefatto di <b>wrap-around</b>: x[−1] viene preso come x[3] = 4.</p>
<div class="box w"><b>Attenzione: righe o colonne?</b><p>La slide dice che le righe di H sono shift ciclici di h. Non è così: la prima riga è [1, 0, 0, −1], non h. Con H<sub>ij</sub> = h[(i − j) mod N] sono le <b>colonne</b> a essere shift ciclici di h (la prima colonna è [1, −1, 0, 0]); le righe sono shift ciclici di h <b>ribaltato</b>. La matrice scritta è comunque giusta. Verifica anche con numpy: ifft(fft(x)·fft(h)) dà [−3, 1, 1, 1].</p></div>
""")

s(31, "Summary", """
<ul>
<li>La convoluzione è l'operazione di <b>ogni</b> sistema LSI, parametrizzata da un kernel h.</li>
<li>Le proprietà (linearità, commutatività, associatività, separabilità) permettono di progettare e combinare filtri in modo efficiente.</li>
<li>Viste equivalenti: somma pesata scorrevole; prodotto per una matrice circolante; (prossime slide) prodotto in frequenza.</li>
<li>L'<b>equivarianza alla traslazione</b> è il primo tipo di invarianza ottenuto. Mancano scala, rotazione e altre trasformazioni (L6 per la scala, L7 per le feature invarianti).</li>
</ul>
""")

s(32, "Fourier Transform", "<p>Onde sinusoidali, base di Fourier, DFT.</p>", kind="div", sec=("l3-fourier", "Trasformata di Fourier", "slide 32–51"))

s(33, "Image Transforms", """
<ul>
<li>Un cambio di rappresentazione può rivelare struttura e semplificare certe operazioni.</li>
<li>Esempio: le coordinate polari rendono facili da analizzare i pattern circolari.</li>
<li>La <b>trasformata di Fourier</b> passa dal dominio spaziale a quello frequenziale, dove i segnali sono sovrapposizioni di sinusoidi.</li>
<li>È un <b>cambio di base lineare</b>: x = H ℓ<sub>in</sub>, ℓ<sub>in</sub> = H<sup>−1</sup> x.</li>
</ul>
<p>Nota di notazione: qui H è la matrice del cambio di base (sarà la matrice di Fourier F della slide 51), non la matrice di convoluzione della slide 29.</p>
""")

s(34, "Continuous Sine Wave", """
<span class="f">s(t) = A sin(ωt − θ)</span>
<ul>
<li><b>A</b>: ampiezza;</li>
<li><b>ω</b>: frequenza angolare (rad/s), ω = 2πf;</li>
<li><b>θ</b>: fase (radianti);</li>
<li><b>periodo</b> T = 2π/ω.</li>
</ul>
<p><b>Figura:</b> sinusoide con periodo e ampiezza indicati.</p>
<p>Ampiezza, frequenza e fase descrivono completamente una componente; la trasformata di Fourier restituisce ampiezza e fase per ogni frequenza.</p>
""")

s(35, "Fourier Series: Decomposing Periodic Signals", """
<p><b>Serie di Fourier</b>: un segnale periodico 1D si scrive come somma di sinusoidi. La slide scrive:</p>
<span class="f">ℓ(t) = a<sub>1</sub> sin(t) + a<sub>2</sub> sin(2t) + a<sub>3</sub> sin(3t) + …</span>
<span class="f">a<sub>k</sub> = (1/T) ∫<sub>0</sub><sup>T</sup> ℓ(t) sin(kt) dt</span>
<ul>
<li>Passare in frequenza rende più facile analizzare e manipolare i segnali, soprattutto per filtraggio e compressione.</li>
<li>Riferimento visivo: <a href="https://www.3blue1brown.com/lessons/fourier-transforms/">3Blue1Brown, Fourier transforms</a>.</li>
</ul>
<p>Il coefficiente a<sub>k</sub> è un <b>prodotto scalare</b> fra il segnale e la k-esima funzione di base: è la proiezione su una base ortogonale.</p>
<div class="box w"><b>Attenzione: fattore sbagliato e "qualunque segnale periodico"</b>
<ul>
<li>Il libro (§ 16.3) scrive la serie per una funzione definita su (0, π), con coefficienti <b>a<sub>k</sub> = (2/π) ∫<sub>0</sub><sup>π</sup> ℓ(t) sin(kt) dt</b>. La slide ha 1/T davanti a ∫<sub>0</sub><sup>T</sup>: con T = π manca un fattore 2 (servirebbe 2/T), perché ∫<sub>0</sub><sup>π</sup> sin²(kt) dt = π/2.</li>
<li>Soli seni bastano perché la serie rappresenta l'<b>estensione dispari</b> di ℓ, di periodo 2π (come il dente di sega della slide 36). Per un segnale periodico <b>qualunque</b>, come dice la slide, servono anche i coseni e il termine costante.</li>
</ul>
<p>Forma corretta, con ω<sub>0</sub> = 2π/T:</p>
<span class="f">ℓ(t) = a<sub>0</sub>/2 + ∑<sub>k≥1</sub> [a<sub>k</sub> cos(kω<sub>0</sub>t) + b<sub>k</sub> sin(kω<sub>0</sub>t)]</span>
<span class="f">a<sub>k</sub> = (2/T) ∫<sub>0</sub><sup>T</sup> ℓ(t) cos(kω<sub>0</sub>t) dt,   b<sub>k</sub> = (2/T) ∫<sub>0</sub><sup>T</sup> ℓ(t) sin(kω<sub>0</sub>t) dt</span>
<p>Verifica sul dente di sega ℓ(t) = t/2 su (−π, π): b<sub>k</sub> = (1/π) ∫ (t/2) sin(kt) dt = (−1)<sup>k+1</sup>/k, cioè 1, −1/2, 1/3, −1/4, …, proprio i coefficienti della figura della slide 36. Con 1/T verrebbero la metà.</p></div>
<div class="box b"><b>Dal libro · cap. 16, § 16.3 Fourier Series</b>
<ul>
<li>Il libro (da cui viene la slide) parte da una funzione ℓ(t) definita solo sull'intervallo (0, π) e la sviluppa in soli seni, con
<span class="f">a<sub>n</sub> = (2/π) ∫<sub>0</sub><sup>π</sup> ℓ(t) sin(nt) dt</span></li>
<li>Perché bastano i seni: la serie rappresenta l'<b>estensione dispari</b> di ℓ, periodica di periodo 2π. Dentro (0, π) converge a ℓ, fuori ripete la versione antisimmetrica. Con i coseni si avrebbe un'altra estensione, diversa fuori da (0, π).</li>
<li>Esempio del libro (fig. 16.1–16.2): la rampa ℓ(t) = t/2 dà (1/2) t = sin t − (1/2) sin 2t + (1/3) sin 3t − …, che è la figura della slide 36.</li>
<li>Storia: Fourier propose queste espansioni studiando la propagazione del calore (Théorie analytique de la chaleur, 1822).</li>
</ul><p><a href="https://visionbook.mit.edu/image_processing_fourier.html">visionbook, cap. 16</a></p></div>
""")

s(36, "Fourier Series (figura)", """
<p><b>Figura</b> (visionbook): sopra le singole armoniche sin(t), −1/2 sin(2t), 1/3 sin(3t), −1/4 sin(4t), 1/5 sin(5t); sotto le somme parziali, che si avvicinano sempre più a un <b>dente di sega</b> (fra −π/2 e π/2).</p>
<ul>
<li>Con poche armoniche si cattura la forma generale.</li>
<li>Il salto netto richiede molte armoniche ad alta frequenza, e vicino al salto resta un'oscillazione (fenomeno di Gibbs, slide 48).</li>
</ul>
<p>Le ampiezze decadono come 1/k: è la firma tipica di una discontinuità.</p>
""")

s(37, "Why Frequency Thinking Matters", """
<p>In termini di frequenze:</p>
<ul>
<li>il <b>blur</b> toglie le alte frequenze;</li>
<li>i <b>bordi</b> sono contenuto ad alta frequenza;</li>
<li>il <b>rumore</b> si distribuisce sulle frequenze in modo diverso dal segnale (il rumore bianco è piatto, le immagini naturali concentrano l'energia in basso);</li>
<li>la <b>compressione</b> (JPEG) scarta le alte frequenze impercettibili (slide 70);</li>
<li>l'<b>aliasing</b> è un fenomeno del dominio frequenziale (L6).</li>
</ul>
""")

s(38, "Why Frequency Thinking Matters (figura)", """
<p><b>Figura:</b> foto dell'astronauta e il suo spettro log|F|; la versione sfocata e il suo spettro.</p>
<ul>
<li>Spettro originale: energia concentrata al centro, ma presente fino ai bordi.</li>
<li>Dopo il blur resta solo la parte centrale (più una croce sugli assi): le alte frequenze, all'esterno, sono sparite.</li>
</ul>
<p>Per leggere gli spettri centrati: <b>centro = basse frequenze</b> (DC), <b>periferia = alte frequenze</b>. La croce sugli assi viene dai bordi dell'immagine, che la DFT vede come salti netti perché tratta l'immagine come periodica.</p>
""")

s(39, "Discrete Sine Wave", """
<span class="f">s[n] = A sin(ωn − θ)</span>
<ul>
<li>n: indice discreto.</li>
<li>Il segnale discreto <b>in generale non è periodico</b>.</li>
<li>È periodico solo se ω è un multiplo razionale di 2π; allora ha un periodo intero N (es. ω = 2πk/N).</li>
</ul>
<p><b>Figura</b> (visionbook): coseni e seni discreti su 20 campioni, con k crescente dall'alto in basso.</p>
<div class="box k"><b>Esempio</b><p>sin(n) (ω = 1) non è mai periodico: servirebbe N intero con N = 2πk, impossibile perché π è irrazionale. sin(2π·3n/20) ha periodo 20 e fa 3 cicli.</p></div>
""")

s(40, "Discrete Sine Wave (periodo esplicito)", """
<p>Per rendere esplicito il periodo si usano onde della forma:</p>
<span class="f">s[n] = sin((2π/N) k n − θ)     c[n] = cos((2π/N) k n − θ)</span>
<ul>
<li>N è la lunghezza del segnale;</li>
<li>k ∈ [1, N/2] è la frequenza, intesa come <b>numero di cicli</b> nel segnale.</li>
</ul>
<p>Con questa parametrizzazione la frequenza diventa un indice intero: è esattamente l'indice u (o v) della DFT.</p>
""")

s(41, "Discrete Sine Wave: Properties", """
<p>Data N la lunghezza del segnale:</p>
<ul>
<li>c<sub>N−k</sub> = c<sub>k</sub> e s<sub>N−k</sub> = −s<sub>k</sub>: le frequenze oltre N/2 non sono nuove, sono le speculari di quelle sotto N/2;</li>
<li><b>k = 0</b>: componente <b>DC</b> (segnale costante);</li>
<li><b>k = N/2</b>: frequenza di <b>Nyquist</b>, la più alta rappresentabile; oscilla fra positivo e negativo a ogni campione. Si chiarisce in L6.</li>
</ul>
<div class="box k"><b>Da saper verificare</b><p>cos(2π(N − k)n/N) = cos(2πn − 2πkn/N) = cos(2πkn/N), perché 2πn è un multiplo intero di 2π. A Nyquist: cos(πn) = (−1)<sup>n</sup> alterna +1 e −1; sin(πn) = 0 per ogni n, quindi a Nyquist il seno non si vede proprio.</p></div>
<div class="box w"><b>Attenzione: vale solo con fase nulla</b><p>Le due uguaglianze sono giuste per θ = 0. Con la fase θ della formula accanto si ottiene cos(2π(N−k)n/N − θ) = cos(2πkn/N + θ): la frequenza N − k equivale alla frequenza k <b>con fase opposta</b>, e analogamente s<sub>N−k</sub> con fase θ = −s<sub>k</sub> con fase −θ.</p></div>
<div class="box b"><b>Dal libro · cap. 16, § 16.4 Continuous and Discrete Waves</b>
<ul>
<li>Un'onda discreta è periodica solo se w = 2πK/N con K, N interi; per k = 0 il seno è identicamente 0 e il coseno vale 1 (il DC).</li>
<li>Poiché le frequenze oltre N/2 ripetono quelle sotto, le frequenze indipendenti sono k ∈ [1, N/2].</li>
<li>Fig. 16.3 (N = 20, k = 1, 2, 3): per k = 3 l'onda compie 3 oscillazioni in [0, N − 1], ma i campioni di un'oscillazione non coincidono con quelli della successiva; il pattern di campioni si ripete esattamente solo ogni N = 20 campioni, perché 3/20 è una frazione irriducibile. Il periodo "visivo" (20/3 campioni) non è intero.</li>
</ul><p><a href="https://visionbook.mit.edu/image_processing_fourier.html">visionbook, cap. 16</a></p></div>
""")

s(42, "2D Sine Waves", """
<span class="f">s<sub>u,v</sub>[m, n] = A sin(2π(un/N + vm/M))</span>
<ul>
<li>u e v controllano la frequenza lungo n (orizzontale) e lungo m (verticale).</li>
<li>Un'onda 2D è un pattern di <b>strisce parallele</b>: l'orientazione dipende dal rapporto fra u e v, la spaziatura dalla loro grandezza.</li>
</ul>
<p><b>Figura</b> (visionbook): (a) strisce verticali (v = 0, varia solo lungo n); (b) strisce oblique; (c) pattern fitto a strisce diagonali, frequenza alta in entrambe le direzioni.</p>
<p>Le strisce sono <b>perpendicolari</b> al vettore (u/N, v/M), che nello spettro è la posizione del picco.</p>
""")

s(43, "Rotations in the Complex Plane", """
<ul>
<li><b>Formula di Eulero</b>: e<sup>iθ</sup> = cos θ + i sin θ.</li>
<li>|e<sup>iθ</sup>| = 1: un punto sulla circonferenza unitaria ad angolo θ.</li>
<li>Moltiplicare per e<sup>iθ</sup> = <b>ruotare</b> di θ senza cambiare il modulo.</li>
</ul>
<p><b>Figura:</b> circonferenza unitaria con cos φ e sin φ come proiezioni sugli assi reale e immaginario.</p>
<div class="box k"><b>Da ricordare</b><p>cos θ = (e<sup>iθ</sup> + e<sup>−iθ</sup>)/2 e sin θ = (e<sup>iθ</sup> − e<sup>−iθ</sup>)/(2i). Sono le formule che servono alla slide 57.</p></div>
""")

s(44, "Why Complex Exponentials?", """
<p>Perché complicarsi la vita con gli esponenziali complessi invece di seno e coseno? Comodità:</p>
<ul>
<li>trasformano traslazioni, derivate e convoluzioni in operazioni algebriche semplici (moltiplicazione per una fase o per uno scalare);</li>
<li>ogni numero complesso si scompone in <b>modulo e fase</b>, rappresentazione naturale per le oscillazioni.</li>
</ul>
<div class="box k"><b>Il motivo profondo</b><p>Gli esponenziali complessi sono <b>autofunzioni</b> di ogni sistema LSI: se l'input è e<sup>jωn</sup>, l'output è H(ω) · e<sup>jωn</sup>. Conto: ∑<sub>k</sub> h[k] e<sup>jω(n−k)</sup> = e<sup>jωn</sup> ∑<sub>k</sub> h[k] e<sup>−jωk</sup> = H(ω) e<sup>jωn</sup>. Seno e coseno da soli non lo sono (un filtro ne cambia la fase, trasformando un seno in un mix di seno e coseno).</p>
<p>Traslazione: ℓ[n − n<sub>0</sub>] ↔ L[u] · e<sup>−2πj u n<sub>0</sub>/N</sup>. Il modulo non cambia, cambia solo la fase.</p></div>
<div class="box b"><b>Dal libro · cap. 16, § 16.7.6–16.7.7 Shift e modulazione</b>
<p>Le due proprietà che rendono concreta la frase della slide ("shift = moltiplicazione per una fase"):</p>
<span class="f">ℓ[n − n<sub>0</sub>, m − m<sub>0</sub>] ⟶ ℒ[u, v] · exp(−2πj (un<sub>0</sub>/N + vm<sub>0</sub>/M))</span>
<span class="f">ℓ[n, m] · exp(+2πj (u<sub>0</sub>n/N + v<sub>0</sub>m/M)) ⟶ ℒ[u − u<sub>0</sub>, v − v<sub>0</sub>]</span>
<ul>
<li><b>Traslare nello spazio</b> cambia solo la fase (il modulo resta uguale). Vale esattamente per traslazioni <b>circolari</b>; per una traslazione vera della camera entra contenuto nuovo dai bordi e la proprietà vale solo in modo approssimato (fig. 16.12).</li>
<li><b>Modulare</b> (moltiplicare per un'onda) trasla lo spettro. Con un coseno si ottengono due copie: ℓ · cos(2π(u<sub>0</sub>n/N + v<sub>0</sub>m/M)) ⟶ ½ (ℒ[u − u<sub>0</sub>, v − v<sub>0</sub>] + ℒ[u + u<sub>0</sub>, v + v<sub>0</sub>]) (fig. 16.13). Il segnale modulato con l'esponenziale complesso non è reale, quindi il suo spettro perde la simmetria attorno a 0.</li>
</ul><p><a href="https://visionbook.mit.edu/image_processing_fourier.html">visionbook, cap. 16</a></p></div>
""")

s(45, "Complex 1D Wave", """
<span class="f">e<sub>u</sub>[n] = exp(2πj · un/N)</span>
<ul>
<li>visionbook usa <b>j</b> invece di i per l'unità immaginaria, come in ingegneria.</li>
<li>Legame con seno e coseno (Eulero): exp(ja) = cos a + j sin a.</li>
</ul>
<p><b>Figura</b> (visionbook): e<sub>u</sub>[n] disegnato in 3D (asse n, parte reale, parte immaginaria): è un'<b>elica</b> di campioni che gira attorno all'asse n; (a) frequenza bassa, gira lentamente; (b) frequenza più alta, più giri. Le proiezioni sui due piani sono un coseno e un seno.</p>
""")

s(46, "Complex 2D Wave", """
<span class="f">e<sub>u,v</sub>[m, n] = exp(2πj (un/N + vm/M))</span>
<ul>
<li>u e v controllano la frequenza in orizzontale e in verticale.</li>
<li>È <b>separabile</b>: e<sub>u,v</sub>[m, n] = e<sub>u</sub>[n] · e<sub>v</sub>[m].</li>
</ul>
<p>Conseguenza pratica: la DFT 2D si calcola come DFT 1D su tutte le righe, seguita da DFT 1D su tutte le colonne.</p>
""")

s(47, "Orthogonality of Complex Waves", """
<p>Gli esponenziali complessi formano una <b>base ortogonale</b>:</p>
<span class="f">⟨e<sub>u,v</sub>, e<sub>u′,v′</sub>⟩ = ∑<sub>n=0</sub><sup>N−1</sup> ∑<sub>m=0</sub><sup>M−1</sup> e<sub>u,v</sub>[n, m] · e<sup>∗</sup><sub>u′,v′</sub>[n, m] = MN · δ[u − u′] δ[v − v′]</span>
<p>con δ la delta di Kronecker (1 se l'argomento è 0, 0 altrimenti).</p>
<ul>
<li>Qualunque immagine discreta finita è una combinazione lineare di esponenziali complessi.</li>
<li>La base è ortogonale, quindi i coefficienti sono <b>unici</b> e si trovano con <b>prodotti scalari</b>.</li>
</ul>
<div class="box k"><b>Da saper dimostrare (1D)</b><p>∑<sub>n</sub> e<sup>2πj(u−u′)n/N</sup> è una serie geometrica di ragione r = e<sup>2πj(u−u′)/N</sup>. Se u = u′ ogni termine vale 1 e la somma è N. Altrimenti vale (1 − r<sup>N</sup>)/(1 − r) = 0, perché r<sup>N</sup> = e<sup>2πj(u−u′)</sup> = 1.</p>
<p>La base è ortogonale ma <b>non ortonormale</b>: ogni vettore ha norma² MN. Da qui il fattore 1/(NM) nell'inversa (slide 49).</p></div>
""")

s(48, "Example: Approximating a Square Wave", """
<p><b>Figura:</b> onda quadra approssimata con 1, 2, 4 e 26 armoniche dispari.</p>
<ul>
<li>Più armoniche = approssimazione migliore, ma un salto netto produce sempre un <b>overshoot</b> vicino alla discontinuità: <b>fenomeno di Gibbs</b>.</li>
<li>Le alte frequenze sono responsabili delle transizioni nette.</li>
</ul>
<div class="box x"><b>Approfondimento</b><p>L'overshoot non sparisce aumentando le armoniche: si stringe verso il salto ma resta circa il 9% dell'ampiezza del salto. È la stessa origine del <b>ringing</b> dei filtri con taglio netto in frequenza (L6, slide 26): troncare lo spettro = moltiplicarlo per un box = convolvere il segnale con una sinc.</p></div>
""")

s(49, "The Discrete Fourier Transform (DFT)", """
<p>Data un'immagine ℓ[n, m] di dimensione N×M:</p>
<span class="f">ℒ[u, v] = ℱ{ℓ[n, m]} = ∑<sub>n=0</sub><sup>N−1</sup> ∑<sub>m=0</sub><sup>M−1</sup> ℓ[n, m] · exp(−2πj (un/N + vm/M))</span>
<p>DFT inversa:</p>
<span class="f">ℓ[n, m] = ℱ<sup>−1</sup>{ℒ[u, v]} = (1/NM) ∑<sub>u=0</sub><sup>N−1</sup> ∑<sub>v=0</sub><sup>M−1</sup> ℒ[u, v] · exp(+2πj (un/N + vm/M))</span>
<ul>
<li>L'inversa rappresenta l'immagine come somma di esponenziali complessi a diverse frequenze spaziali, pesati dai coefficienti ℒ[u, v].</li>
<li>La frequenza speciale <b>DC</b> (0, 0) corrisponde all'onda costante.</li>
</ul>
<div class="box k"><b>Da sapere a memoria</b><ul>
<li>Diretta: segno <b>−</b>, nessun fattore. Inversa: segno <b>+</b>, fattore <b>1/NM</b>. È la convenzione di numpy (<code>np.fft.fft2</code> / <code>ifft2</code>).</li>
<li>ℒ[0, 0] = ∑ ℓ[n, m] = NM × media dell'immagine.</li>
<li>Altre convenzioni esistono (1/√(NM) su entrambe, "unitaria"); cambiano i fattori, non la sostanza. Fissata una convenzione, va usata coerentemente: vedi la slide 57.</li>
<li>Costo diretto: N² M² operazioni; con FFT O(NM log(NM)).</li></ul></div>
<div class="box b"><b>Dal libro · cap. 16, § 16.8 A Family of Fourier Transforms</b>
<p>La DFT è una di tre trasformate, a seconda del tipo di segnale (tab. 16.2):</p>
<ul>
<li><b>DFT</b> (discreto, finito): quella della slide; frequenze discrete u = 0, …, N − 1.</li>
<li><b>Trasformata continua</b> (continuo, infinito): ℒ(w) = ∫ ℓ(t) e<sup>−jwt</sup> dt, inversa ℓ(t) = (1/2π) ∫ ℒ(w) e<sup>jwt</sup> dw, con w in radianti. È quella sottintesa quando le slide 63–65 scrivono H(ξ).</li>
<li><b>DTFT</b> (discreto, infinito): ℒ(w) = ∑<sub>n</sub> ℓ[n] e<sup>−jwn</sup>, inversa (1/2π) ∫<sub>2π</sub> ℒ(w) e<sup>jwn</sup> dw. La frequenza è continua ma <b>periodica di periodo 2π</b>: è il motivo profondo dell'aliasing (L6).</li>
</ul><p>In tutte e tre la diretta ha segno − e l'inversa segno + con il fattore di normalizzazione (1/N, 1/2π). <a href="https://visionbook.mit.edu/image_processing_fourier.html">visionbook, cap. 16</a></p></div>
""")

s(50, "Centered DFT", """
<ul>
<li>ℒ[u, v] è <b>periodica</b>: ℒ[u + aN, v + bM] = ℒ[u, v] per ogni a, b interi.</li>
<li>Dato che e<sub>N−u, M−v</sub> = e<sub>−u, −v</sub>, si può scrivere la trasformata con frequenze in [−N/2, N/2] e [−M/2, M/2].</li>
<li>È così che si disegna: DC al centro. In numpy lo fa <code>fftshift</code>.</li>
</ul>
<p><b>Figura:</b> la stessa coppia di foto e spettri della slide 38, ora con lo spettro centrato.</p>
<div class="box k"><b>Da sapere</b><p>Gli intervalli sono di N valori, quindi per N pari sono [−N/2, N/2 − 1]: la frequenza N/2 coincide con −N/2 (anche il libro, eq. 16.4, scrive la somma da −N/2 a N/2, che conterebbe N + 1 termini). Esempio N = 8: <code>fftshift</code> ordina le frequenze come −4, −3, −2, −1, 0, 1, 2, 3. Senza shift, le basse frequenze stanno nei quattro angoli dell'array.</p></div>
""")

s(51, "The Fourier Matrix (1D)", """
<p>La DFT 1D è il prodotto per la matrice di Fourier <b>F</b> (N×N):</p>
<span class="f">F<sub>u,n</sub> = exp(−2πj · un/N)</span>
<p>Prima riga e prima colonna tutte 1; la riga u contiene le potenze di exp(−2πj u/N); l'ultimo elemento è exp(−2πj (N−1)²/N).</p>
<ul>
<li>F è <b>simmetrica</b> (un e nu sono uguali).</li>
<li>La slide scrive F<sup>−1</sup> = F<sup>∗</sup> (coniugata): vedi sotto.</li>
<li>La <b>FFT</b> sfrutta la struttura di F per calcolare la DFT in O(N log N) invece di O(N²).</li>
</ul>
<p>Punto chiave: la DFT è letteralmente un prodotto matrice-vettore, cioè un cambio di base; la FFT è solo un modo furbo di calcolarlo, non un'altra trasformata.</p>
<div class="box w"><b>Attenzione: manca il fattore 1/N</b><p>Per l'ortogonalità della slide 47, F<sup>∗</sup>F = N·I, quindi</p>
<span class="f">F<sup>−1</sup> = (1/N) F<sup>∗</sup></span>
<p>coerente con l'1/N della DFT inversa (slide 49). F<sup>−1</sup> = F<sup>∗</sup> vale solo per la versione normalizzata F/√N, che è unitaria. La slide copia la frase del libro (§ 16.5.2), che però usa la stessa DFT senza fattori della slide 49 (eq. 16.2): anche lì il fattore 1/N è sottinteso. Controllo con N = 2: F = [[1, 1], [1, −1]], F<sup>∗</sup>F = 2I.</p></div>
""")

s(52, "Examples of Signals and their Fourier Transform", "<p>Come si visualizza uno spettro e coppie segnale/trasformata da conoscere.</p>", kind="div", sec=("l3-esempi", "Esempi di trasformate", "slide 52–60"))

s(53, "Visualizing the Fourier Transform", """
<ul>
<li>La DFT restituisce <b>numeri complessi</b>.</li>
<li>Si possono mostrare parte reale e parte immaginaria (la slide scrive "image", è un refuso per "imaginary"):
<span class="f">ℒ[u, v] = Re{ℒ[u, v]} + j Im{ℒ[u, v]}</span></li>
<li>Di solito si usa la forma <b>modulo e fase</b>:
<span class="f">ℒ[u, v] = A[u, v] · exp(j θ[u, v])</span></li>
<li>Spesso si mostra la <b>log-magnitudine</b> log(1 + A): l'ampiezza decade così in fretta con la frequenza che in scala lineare si vedrebbe solo il DC.</li>
</ul>
""")

s(54, "Visualizing the Fourier Transform (figura)", """
<p><b>Figura</b> (visionbook): un parallelepipedo scuro su fondo chiaro (64×64) e la sua DFT centrata, con u, v da −32 a 31.</p>
<ul>
<li>In alto: parte reale e parte immaginaria, poco leggibili.</li>
<li>In basso: ampiezza (una stella di raggi, ognuno perpendicolare a un gruppo di bordi del parallelepipedo) e fase (aspetto rumoroso).</li>
</ul>
<p>Le due coppie contengono la stessa informazione, ma l'ampiezza si interpreta molto meglio. La fase sembra rumore, eppure è lì che sta la struttura (slide 59–60).</p>
""")

s(55, "1D Example", """
<ul>
<li><b>Regione liscia</b>: contenuto a bassa frequenza.</li>
<li><b>Bordo netto</b>: contenuto a <b>banda larga</b>, con molte frequenze, anche molto alte.</li>
<li><b>Texture periodica</b> (es. un muro di mattoni): energia concentrata su frequenze specifiche.</li>
<li>Una texture o una feature complessa ha una <b>firma</b> distintiva in frequenza.</li>
</ul>
<p><b>Figura:</b> a sinistra tre segnali 1D (sinusoide lenta, gradino, onda quadra fitta), a destra |F(k)|: un picco a k basso; un picco a k = 0 con una coda che decade lentamente; un picco isolato attorno a k = 20.</p>
<p>È la base dei descrittori di texture (Gabor, wavelet) della slide 73.</p>
""")

s(56, "Impulse", """
<p>Sia δ un impulso nell'origine: δ[0, 0] = 1, zero altrove.</p>
<span class="f">ℱ{δ[n, m]} = ∑<sub>n</sub> ∑<sub>m</sub> δ[n, m] · exp(−2πj (un/N + vm/M)) = 1</span>
<ul>
<li>Un impulso contiene <b>tutte le frequenze con la stessa ampiezza e fase nulla</b>.</li>
<li>Per questo gli impulsi si usano per sondare la risposta in frequenza di un sistema.</li>
</ul>
<p>Nota del docente: fate il conto da soli per familiarizzare con la trasformata.</p>
<div class="box k"><b>Da saper fare</b><p>Nella somma sopravvive solo il termine n = m = 0, dove l'esponenziale vale exp(0) = 1. Estensione: un impulso in (n<sub>0</sub>, m<sub>0</sub>) ha trasformata exp(−2πj(un<sub>0</sub>/N + vm<sub>0</sub>/M)): ampiezza ancora 1 ovunque, fase lineare. Traslare cambia solo la fase.</p>
<p>Collegamento: dando δ in input a un sistema LSI si ottiene h (δ ∗ h = h), quindi la sua trasformata è H. È il motivo del nome "risposta all'impulso" (slide 65).</p></div>
""")

s(57, "Cosine and Sine Waves", """
<p>Coseni e seni puri danno <b>coppie di frequenze</b> complesse. La slide scrive:</p>
<span class="f">ℱ{cos(2π(u<sub>0</sub>n/N + v<sub>0</sub>m/M))} = ½ (δ[u − u<sub>0</sub>, v − v<sub>0</sub>] + δ[u + u<sub>0</sub>, v + v<sub>0</sub>])</span>
<span class="f">ℱ{sin(2π(u<sub>0</sub>n/N + v<sub>0</sub>m/M))} = 1/(2j) (δ[u − u<sub>0</sub>, v − v<sub>0</sub>] + δ[u + u<sub>0</sub>, v + v<sub>0</sub>])</span>
<p><b>Figura</b> (visionbook): sei onde 2D con diverse frequenze e orientazioni; sotto, l'ampiezza della DFT: sempre due punti simmetrici rispetto al centro (o quattro, per somme di due onde). Più l'onda è fitta, più i punti sono lontani dal centro; la retta che li unisce è perpendicolare alle strisce.</p>
<p>Una sinusoide pura è "un punto" in frequenza (più il suo simmetrico): l'opposto dell'impulso, che è un punto nello spazio e piatto in frequenza.</p>
<div class="box w"><b>Attenzione: due errori nelle formule</b>
<ul>
<li><b>Segno del seno</b>: sin x = (e<sup>jx</sup> − e<sup>−jx</sup>)/(2j), quindi fra le due delta ci vuole un <b>meno</b>, come infatti scrive il libro (§ 16.6.2 e tab. 16.1): è un errore di trascrizione della slide. Controllo rapido: il seno è reale, quindi deve valere la simmetria coniugata ℒ(−u) = ℒ(u)<sup>∗</sup> (slide 62); con il più, i due coefficienti sarebbero entrambi −j/2 e la simmetria non varrebbe.</li>
<li><b>Fattore NM</b>: con la DFT non normalizzata della slide 49, ∑ e<sup>2πj u<sub>0</sub>n/N</sup> e<sup>−2πj un/N</sup> = N·δ[u − u<sub>0</sub>]. Il ½ è giusto solo con la DFT normalizzata (1/NM nella diretta). Il ½ c'è anche nel libro (§ 16.6.2, tab. 16.1), che però definisce la DFT senza fattori (eq. 16.2): la stessa incoerenza, ereditata dalla slide.</li>
</ul>
<p>Versione coerente con la slide 49:</p>
<span class="f">ℱ{cos(…)} = (NM/2) (δ[u − u<sub>0</sub>, v − v<sub>0</sub>] + δ[u + u<sub>0</sub>, v + v<sub>0</sub>])</span>
<span class="f">ℱ{sin(…)} = (NM/2j) (δ[u − u<sub>0</sub>, v − v<sub>0</sub>] − δ[u + u<sub>0</sub>, v + v<sub>0</sub>])</span>
<p>Verificato con numpy: per N = 8, u<sub>0</sub> = 2, <code>fft(cos)</code> vale 4 in u = 2 e u = 6; <code>fft(sin)</code> vale −4j in u = 2 e +4j in u = 6. Gli indici u + u<sub>0</sub> vanno letti modulo N (u = −2 ≡ 6).</p></div>
""")

s(58, "Examples", """
<p><b>Figura</b> (visionbook): sei immagini semplici, con ampiezza e fase della DFT.</p>
<ol>
<li>Una <b>riga orizzontale</b> che attraversa l'immagine → una riga <b>verticale</b> nello spettro. Costante lungo n = solo frequenza u = 0.</li>
<li>Un <b>segmento orizzontale corto</b> → banda verticale con righe laterali (una sinc lungo u).</li>
<li>Un <b>quadrato grande</b> → spettro concentrato in un punto al centro.</li>
<li>Un <b>quadrato piccolo</b> → macchia larga con lobi laterali: la <b>sinc 2D</b>.</li>
<li>Un <b>rettangolo orizzontale</b> → spettro allungato in verticale.</li>
<li>Un <b>rettangolo ruotato</b> → spettro ruotato dello stesso angolo, allungato in direzione perpendicolare.</li>
</ol>
<div class="box k"><b>Regole da ricordare</b><ul>
<li><b>Largo nello spazio = stretto in frequenza</b> e viceversa (proprietà di scala).</li>
<li>Ruotare l'immagine ruota lo spettro dello stesso angolo.</li>
<li>Rettangolo ↔ sinc.</li>
<li>Le fasi hanno solo due valori (0 e π, i due grigi della figura): gli oggetti sono simmetrici e centrati, quindi la DFT è reale e cambia solo di segno.</li></ul></div>
<div class="box b"><b>Dal libro · cap. 16, § 16.6.3 Box Function</b>
<p>La regola "rettangolo ↔ sinc" in forma esatta. Per il box discreto box<sub>L</sub>[n] = 1 se −L ≤ n ≤ L, 0 altrove (larghezza 2L + 1):</p>
<span class="f">box<sub>L</sub>[n] ⟶ sin(πu(2L + 1)/N) / sin(πu/N)</span>
<ul>
<li>È reale (il box è simmetrico attorno all'origine) e vale 2L + 1 in u = 0, cioè la somma dei campioni.</li>
<li>Il primo zero cade in u = N/(2L + 1): <b>più largo il box, più stretto il lobo centrale</b>. Nel grafico del libro (fig. 16.11, L = 5, N = 32) il primo zero è a u ≈ 2,9.</li>
<li>Il libro chiama questa funzione <b>sinc discreta</b>, sincd(x; a) = sin(πx)/(a sin(πx/a)): a differenza della sinc continua è periodica.</li>
</ul><p>In 2D un rettangolo separabile dà il prodotto di due sinc discrete, una lungo u e una lungo v (§ 16.7.2): da qui i lobi laterali allineati agli assi u e v nel quadrato piccolo della figura. <a href="https://visionbook.mit.edu/image_processing_fourier.html">visionbook, cap. 16</a></p></div>
""")

s(59, "Magnitude vs Phase: Which Matters More?", """
<ul>
<li>Esperimento classico: <b>scambiare</b> gli spettri di ampiezza e fase di due immagini.</li>
<li>Risultato: la <b>fase</b> determina in gran parte la struttura percepita; l'ampiezza influenza soprattutto contrasto e "stile" della texture.</li>
<li>Implicazione: bordi, forme e contorni sono codificati soprattutto nelle <b>relazioni di fase</b> fra le frequenze. Conta per capire cosa un filtro conserva o distrugge.</li>
</ul>
<p><b>Figura:</b> immagine A (astronauta), immagine B (cameraman), ampiezza(A) + fase(B), ampiezza(B) + fase(A). In ciascuna combinazione si riconosce l'immagine che ha dato la <b>fase</b>.</p>
<div class="box k"><b>Perché</b><p>Un bordo è un punto in cui molte sinusoidi sono "allineate" (in fase). L'ampiezza dice quanta energia c'è a ogni frequenza, e le immagini naturali hanno ampiezze simili fra loro (circa 1/f); la fase dice dove stanno le cose.</p></div>
<div class="box b"><b>Dal libro · cap. 16, § 16.9 Fourier Analysis as an Image Representation</b>
<ul>
<li>Le ampiezze delle immagini naturali sono molto simili fra loro e seguono una legge di potenza: A[u, v] ≈ a / (u² + v²)<sup>b</sup>, con a e b costanti (lo spettro "1/f"). Per questo l'ampiezza distingue poco un'immagine da un'altra.</li>
<li>La fase stabilisce come le sinusoidi devono allinearsi per formare contorni e bordi. In sintesi del libro: la <b>posizione</b> finisce nella fase, la <b>scala dell'intensità</b> nell'ampiezza.</li>
<li>Lo scambio di ampiezza e fase fra due immagini (fig. 16.14, per ogni canale di colore) dà immagini dominate da quella che ha fornito la fase. Ma il libro precisa che l'importanza relativa <b>dipende dall'immagine</b>: per le texture quasi periodiche conta l'ampiezza (slide 60).</li>
<li>Regole di lettura (fig. 16.16): i contrasti forti diventano linee orientate nello spettro (perpendicolari al bordo), i pattern periodici diventano picchi isolati.</li>
</ul><p><a href="https://visionbook.mit.edu/image_processing_fourier.html">visionbook, cap. 16</a></p></div>
""")

s(60, "Magnitude vs Phase (figura)", """
<p><b>Figura</b> (visionbook): quattro immagini (uccello, spiaggia, bosco, tessuto) con ampiezza e fase della DFT, poi due ricostruzioni:</p>
<ul>
<li><b>Random phase</b>: ampiezza originale con fase casuale. Si perde la struttura; resta una "texture" con l'orientazione dominante (strisce orizzontali per la spiaggia, verticali per il bosco).</li>
<li><b>1/f amplitude</b>: fase originale con un'ampiezza generica 1/f. L'uccello, la spiaggia e il bosco restano riconoscibili.</li>
</ul>
<p>Eccezione istruttiva, l'ultima riga: per la <b>texture</b> del tessuto è il contrario. Con la fase casuale la trama si riconosce ancora, con l'ampiezza 1/f si perde. Per le texture periodiche l'informazione sta nell'ampiezza (picchi a frequenze precise, slide 55).</p>
<div class="box w"><b>Attenzione: didascalia</b><p>La didascalia ripete "scambiare ampiezza e fase fra due immagini", ma la figura fa un esperimento diverso: fase casuale e ampiezza 1/f, senza scambi fra immagini. Nel libro sono due figure distinte: lo scambio è la fig. 16.14, questa è la fig. 16.15. E la conclusione del libro per questa figura non è "la struttura segue sempre la fase", ma che l'importanza relativa di fase e ampiezza <b>dipende dall'immagine</b> (vedi il tessuto).</p></div>
""")

s(61, "Properties of the Fourier Transform", "<p>Linearità, simmetria, teorema di convoluzione, filtraggio in frequenza.</p>", kind="div", sec=("l3-proprieta", "Proprietà della trasformata", "slide 61–67"))

s(62, "Linearity and Conjugate Symmetry of Real Signals", """
<ul>
<li><b>Linearità</b>: ℱ{af + bg} = a ℱ{f} + b ℱ{g}, per segnali reali e complessi.</li>
<li>Per ℓ reale vale la <b>simmetria coniugata</b>:
<span class="f">ℒ(−u) = ℒ(u)<sup>∗</sup>   (equivalentemente ℒ(u) = ℒ(−u)<sup>∗</sup>)</span>
<ul><li>lo spettro di ampiezza è simmetrico rispetto al DC (0, 0), la fase è antisimmetrica;</li>
<li>le frequenze negative non aggiungono informazione: sono lo specchio di quelle positive;</li>
<li>per questo numpy ha <code>rfft</code>, che calcola solo metà delle frequenze (N/2 + 1 valori in 1D).</li></ul></li>
</ul>
<div class="box k"><b>Da saper dimostrare</b><p>ℒ(−u) = ∑ ℓ[n] e<sup>+2πjun/N</sup> = (∑ ℓ[n] e<sup>−2πjun/N</sup>)<sup>∗</sup> = ℒ(u)<sup>∗</sup>, perché ℓ[n] = ℓ[n]<sup>∗</sup> se è reale.</p>
<p>Conteggio: N valori reali → N/2 + 1 coefficienti complessi, di cui DC e Nyquist reali: in tutto di nuovo N numeri reali. Nessuna informazione creata né persa.</p></div>
<div class="box b"><b>Dal libro · cap. 16, § 16.7.1–16.7.3 Linearity, Separability, Parseval</b>
<ul>
<li><b>Separabilità</b>: se ℓ[n, m] = ℓ<sub>1</sub>[n] ℓ<sub>2</sub>[m], allora ℒ[u, v] = ℒ<sub>1</sub>[u] ℒ<sub>2</sub>[v]. Un'immagine separabile ha spettro separabile.</li>
<li><b>Parseval</b> (omesso dalle slide), con la normalizzazione della slide 49:
<span class="f">∑<sub>n,m</sub> ℓ<sub>1</sub>[n, m] ℓ<sub>2</sub><sup>∗</sup>[n, m] = (1/NM) ∑<sub>u,v</sub> ℒ<sub>1</sub>[u, v] ℒ<sub>2</sub><sup>∗</sup>[u, v]</span>
e, per ℓ<sub>1</sub> = ℓ<sub>2</sub> (Plancherel), ∑ |ℓ|² = (1/NM) ∑ |ℒ|²: l'energia si conserva, a meno del fattore NM dovuto alla base non normalizzata (slide 47). Dice che |ℒ[u, v]|² misura quanta energia sta alla frequenza (u, v).</li>
<li>La simmetria coniugata della slide non è enunciata come proprietà nel capitolo, ma è una conseguenza immediata della definizione (riquadro Da saper dimostrare qui sopra).</li>
</ul><p><a href="https://visionbook.mit.edu/image_processing_fourier.html">visionbook, cap. 16</a></p></div>
""")

s(63, "The Convolution Theorem", """
<span class="f">ℱ{f ∗ h} = ℱ{f} · ℱ{h}</span>
<p>La convoluzione nello spazio è un <b>prodotto punto per punto</b> in frequenza. È il risultato centrale della lezione.</p>
<ul>
<li>Convoluzione = <b>filtraggio</b>: un passa-basso è una funzione H(ξ) ≈ 1 per |ξ| piccolo e ≈ 0 per |ξ| grande.</li>
<li>Progettare un filtro diventa progettare una curva di risposta in frequenza.</li>
<li>Filtri in cascata = prodotto delle risposte in frequenza (coerente con l'associatività).</li>
</ul>
<div class="box k"><b>Da saper dimostrare (1D, circolare)</b><p>ℱ{f ∗ h}[u] = ∑<sub>n</sub> ∑<sub>k</sub> f[k] h[n − k] e<sup>−2πjun/N</sup>. Con n = k + r: = ∑<sub>k</sub> f[k] e<sup>−2πjuk/N</sup> · ∑<sub>r</sub> h[r] e<sup>−2πjur/N</sup> = F[u] · H[u].</p>
<p>Con la DFT il teorema vale per la convoluzione <b>circolare</b> (indici modulo N): è il motivo dello zero-padding della slide 64. Vale anche il duale: prodotto nello spazio = convoluzione in frequenza (con fattore 1/N), che è la base del campionamento in L6.</p></div>
<div class="box b"><b>Dal libro · cap. 16, § 16.7.4–16.7.5 Convolution e Dual Convolution</b>
<ul>
<li>Il libro enuncia il teorema per la <b>convoluzione circolare</b> ∘<sub>N,M</sub> (slide 29), perché la dimostrazione richiede di spostare gli indici con condizioni al contorno periodiche:
<span class="f">ℓ<sub>1</sub> ∘<sub>N,M</sub> ℓ<sub>2</sub> ⟶ ℒ<sub>1</sub>[u, v] · ℒ<sub>2</sub>[u, v]</span></li>
<li><b>Duale</b>: il prodotto punto per punto nello spazio diventa una convoluzione (circolare) in frequenza, con un fattore:
<span class="f">ℓ<sub>1</sub>[n, m] · ℓ<sub>2</sub>[n, m] ⟶ (1/NM) ℒ<sub>1</sub> ∘ ℒ<sub>2</sub></span>
È la base della modulazione (slide 44) e del campionamento (L6).</li>
<li>La tabella 16.1 del libro riassume le coppie da sapere: convoluzione ↔ prodotto, prodotto ↔ convoluzione/N, shift ↔ fase lineare, δ ↔ 1, coseno ↔ due delta, box ↔ sinc discreta.</li>
</ul><p><a href="https://visionbook.mit.edu/image_processing_fourier.html">visionbook, cap. 16</a></p></div>
""")

s(64, "Practical: FFT-Based Convolution", """
<ul>
<li>Dal teorema: f ∗ h = ℱ<sup>−1</sup>{ℱ{f} · ℱ{h}}.</li>
<li>Per kernel grandi la convoluzione via FFT, O(N log N), batte quella diretta, O(Nk).</li>
<li>Attenzione: la DFT tratta i segnali come <b>circolari</b>. Per ottenere una convoluzione <b>lineare</b> bisogna fare zero-padding, altrimenti c'è wrap-around (slide 30).</li>
<li>I framework (cuDNN, cuFFT) scelgono fra algoritmi diretti e via FFT a seconda della dimensione del kernel.</li>
</ul>
<div class="box k"><b>Da sapere</b><ul>
<li>Padding: si porta tutto ad almeno N + k − 1 campioni (in 2D per ogni asse); con quella lunghezza la convoluzione circolare coincide con quella lineare full.</li>
<li>In 2D, immagine con P pixel e kernel k×k: diretto O(P k²), FFT O(P log P). Conviene per k grandi.</li>
<li>I kernel 3×3 delle CNN sono piccoli: in pratica si usa la convoluzione diretta o Winograd, non la FFT.</li></ul></div>
""")

s(65, "Impulse Response and Transfer Function", """
<p>Un sistema LSI si descrive completamente in due modi:</p>
<ul>
<li><b>vista spaziale</b>: il kernel h(x), che è la <b>risposta all'impulso</b> (l'output quando l'input è δ(x));</li>
<li><b>vista frequenziale</b>: H(ξ) = ℱ{h}, la <b>funzione di trasferimento</b> o risposta in frequenza: di quanto ogni frequenza viene amplificata o attenuata (|H|) e sfasata (fase di H);</li>
<li>h e H sono una <b>coppia di Fourier</b>.</li>
</ul>
<p>Descrivere il filtro con h o con H è la stessa cosa: si sceglie la rappresentazione più comoda per il ragionamento.</p>
""")

s(66, "Frequency-Domain Filtering", """
<p>Dalla dualità spazio/frequenza: un sistema LSI <b>amplifica o attenua frequenze</b>.</p>
<ul>
<li><b>Passa-basso</b>: lascia passare le basse, attenua le alte. Effetto: sfocatura.</li>
<li><b>Passa-alto</b>: attenua le basse. Esalta bordi e dettagli.</li>
<li><b>Passa-banda</b>: isola un intervallo di frequenze. Usato per analisi di texture e orientazione.</li>
</ul>
<div class="box k"><b>Da sapere</b><p>Passa-alto = identità − passa-basso: h<sub>HP</sub> = δ − h<sub>LP</sub>, cioè H<sub>HP</sub> = 1 − H<sub>LP</sub>. In pratica: originale meno versione sfocata. Lo sharpening di L5 è originale + α · (originale − sfocata). Passa-banda = differenza di due passa-basso (es. DoG, piramide laplaciana in L6).</p></div>
<div class="box b"><b>Dal libro · cap. 16, § 16.10 Fourier Analysis of Linear Filters</b>
<ul>
<li>Per un filtro con kernel h: ℒ<sub>out</sub>[u, v] = H[u, v] · ℒ<sub>in</sub>[u, v], dove la <b>funzione di trasferimento</b> H è la DFT del kernel. In forma polare H = |H| exp(j∠H): |H[u, v]| è il <b>guadagno in ampiezza</b>, ∠H[u, v] lo <b>sfasamento</b>; |H[0, 0]| è il <b>guadagno DC</b> (per un blur normalizzato vale 1: la luminosità media non cambia).</li>
<li>Idea chiave del libro: un filtro lineare <b>ripesa</b> il contenuto spettrale già presente; non crea frequenze nuove, può solo amplificarle o attenuarle (confronta slide 71 sulle nonlinearità).</li>
<li>Esempio (§ 16.10.1, fig. 16.19): in una foto 256×256 di un edificio del MIT le colonne si ripetono ogni 14 pixel, quindi lo spettro ha picchi alla frequenza orizzontale 256/14 ≈ 18 e alle sue armoniche. Azzerando quei coefficienti le colonne spariscono quasi del tutto; tenendo solo quelli resta solo il colonnato. È un filtro progettato direttamente in frequenza.</li>
</ul><p><a href="https://visionbook.mit.edu/image_processing_fourier.html">visionbook, cap. 16</a></p></div>
""")

s(67, "Frequency-Domain Filtering (figure)", """
<p><b>Figura 28:</b> |H(u)| dei tre filtri come trapezi: passa-basso (alto vicino a 0, poi scende), passa-banda (una gobba a frequenze intermedie), passa-alto (zero in basso, sale in alto).</p>
<p><b>Figura 29:</b> una barca a vela filtrata con (a) passa-basso: solo colori e forme sfocate; (b) passa-banda: la barca e gli edifici a scala intermedia, su fondo grigio; (c) passa-alto: solo contorni sottili e dettagli (scritte sulla vela, finestre), su fondo grigio.</p>
<p>Il fondo grigio in (b) e (c) indica valore zero: togliendo il DC l'immagine ha media nulla.</p>
<div class="box x"><b>Approfondimento</b><p>I filtri della figura hanno fianchi inclinati. Un taglio ideale a gradino produrrebbe <b>ringing</b> nell'immagine, perché la sua antitrasformata è una sinc con code lunghe (Gibbs, slide 48). Per questo si preferiscono transizioni morbide come la gaussiana (L6, slide 26).</p></div>
<div class="box b"><b>Dal libro · cap. 16, § 16.10.2 Human Visual System and Contrast Sensitivity Function</b>
<ul>
<li>Se l'input è una sinusoide di frequenza u<sub>0</sub> e ampiezza 1, un sistema lineare restituisce la stessa sinusoide con ampiezza |H[u<sub>0</sub>]|: misurando per quali contrasti vediamo le strisce si stima la |H| del sistema visivo.</li>
<li>La carta di <b>Campbell e Robson</b> (fig. 16.20) fa proprio questo: frequenza che cresce in orizzontale e contrasto che cala in verticale, entrambi in scala logaritmica. Il confine fra strisce visibili e invisibili disegna la <b>contrast sensitivity function</b>.</li>
<li>Risultato: il sistema visivo si comporta come un <b>passa-banda</b>, più sensibile alle frequenze medie (picco attorno a 6 cicli per grado) e meno a quelle molto basse e molto alte. La curva cambia con illuminazione, adattamento ed età.</li>
</ul><p><a href="https://visionbook.mit.edu/image_processing_fourier.html">visionbook, cap. 16</a></p></div>
""")

s(68, "Applications and Connections with DNNs", "<p>Compressione, JPEG e lettura in frequenza delle CNN.</p>", kind="div", sec=("l3-app", "Applicazioni e CNN", "slide 68–77"))

s(69, "Compression", """
<p><b>Figura</b> (visionbook): il parallelepipedo della slide 54 ricostruito tenendo solo gli N coefficienti di Fourier di <b>ampiezza maggiore</b>, con N = 1, 3, 7, 15, 31, 63, 127, 255, 511, 1023, 2047, 4095. Accanto a ogni ricostruzione, la posizione dei coefficienti tenuti.</p>
<ul>
<li>N = 1: solo il DC, un grigio uniforme.</li>
<li>Poche decine di coefficienti: una macchia con l'orientazione giusta.</li>
<li>Qualche centinaio: la forma è riconoscibile; i coefficienti scelti sono vicini al centro e lungo i raggi perpendicolari ai bordi.</li>
</ul>
<p>Secondo il libro (§ 16.5.3, fig. 16.8) con 127 coefficienti l'immagine 64×64 (4096 coefficienti) è già riconoscibile: circa il 3%.</p>
<p>Punto: l'energia delle immagini naturali è concentrata nelle <b>basse frequenze</b>, quindi pochi coefficienti bastano per una ricostruzione riconoscibile. È la base della compressione con perdita.</p>
<p>Perché N è sempre dispari (2<sup>k</sup> − 1)? Si spiega con la simmetria coniugata (slide 62): il DC più coppie di coefficienti coniugati, che hanno la stessa ampiezza e vanno tenuti insieme perché la ricostruzione resti reale.</p>
""")

s(70, "JPEG and Frequency-Domain Compression", """
<ul>
<li>JPEG lavora su <b>blocchi 8×8</b> con la <b>DCT</b> (Discrete Cosine Transform), stretta parente della DFT: a valori reali, corrisponde a un'estensione a simmetria pari del blocco.</li>
<li>Quantizza più aggressivamente i coefficienti ad alta frequenza, percettivamente meno importanti: ragionamento in frequenza applicato direttamente.</li>
<li>Gli <b>artefatti a blocchi</b> a bitrate bassi vengono da questo schema.</li>
</ul>
<div class="box x"><b>Approfondimento</b><ul>
<li>Perché la DCT e non la DFT: la simmetria pari evita il salto ai bordi del blocco che la DFT vedrebbe (slide 27, 38), quindi l'energia è ancora più concentrata nei primi coefficienti.</li>
<li>I blocchi sono quantizzati in modo indipendente: a bitrate basso i bordi fra un blocco e l'altro non combaciano più.</li>
<li>JPEG comprime anche la crominanza più della luminanza (chroma subsampling), perché l'occhio è meno sensibile ai dettagli di colore (L2).</li></ul></div>
""")

s(71, "Frequency View of CNN Operations", """
<ul>
<li><b>Layer convoluzionali</b>: ogni filtro ha una risposta in frequenza H(ξ, η). I filtri appresi somigliano spesso a filtri <b>passa-banda orientati</b> (tipo Gabor nei primi layer).</li>
<li><b>Convoluzioni impilate</b>: per il teorema di convoluzione equivalgono a moltiplicare le risposte in frequenza; il filtro efficace è il prodotto delle risposte dei layer.</li>
<li><b>Nonlinearità</b> (ReLU, …): rompono il quadro LSI/Fourier introducendo <b>nuove frequenze</b> (armoniche). È anche per questo che le reti profonde modellano contenuti in frequenza complessi.</li>
</ul>
<div class="box x"><b>Approfondimento</b><p>Esempio di nuove frequenze: ReLU di un coseno è un coseno "raddrizzato", che contiene la frequenza originale, un DC e armoniche multiple. Un sistema LSI invece non può mai creare frequenze che non c'erano: può solo scalare e sfasare quelle esistenti.</p></div>
""")

s(72, "Receptive Field and Frequency Response", """
<ul>
<li>Un <b>campo recettivo</b> più ampio (stack più profondi, kernel più grandi o dilatati) permette di rappresentare frequenze più basse, cioè informazione più globale.</li>
<li>Kernel piccoli impilati approssimano kernel efficaci più grandi (due 3×3 danno il campo recettivo di un 5×5), ma la risposta in frequenza è diversa per le nonlinearità in mezzo.</li>
<li><b>Convoluzioni dilatate</b>: il kernel campiona l'input in modo rado; se progettate male danno artefatti simili all'aliasing (<b>gridding</b>).</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Campo recettivo di L layer k×k con stride 1: 1 + L(k − 1). Due 3×3 → 5, tre 3×3 → 7. Parametri: due 3×3 = 18 per canale contro 25 del 5×5 (l'argomento di VGG). Un 3×3 con dilatazione d copre 2d + 1 pixel ma ne usa solo 9: è un sottocampionamento dell'input, da cui il possibile aliasing (L6).</p></div>
""")

s(73, "Texture as Frequency Content", """
<ul>
<li>Molte texture si caratterizzano con le loro <b>frequenze spaziali e orientazioni dominanti</b> (descrittori di texture basati su Fourier o Gabor).</li>
<li>I <b>banchi di filtri passa-banda</b> (Gabor, wavelet) scompongono l'immagine in bande di frequenza orientate: sono il fondamento dell'analisi classica delle texture e delle prime architetture simili alle CNN.</li>
</ul>
<div class="box x"><b>Approfondimento</b><p>Un filtro di Gabor è una sinusoide moltiplicata per una gaussiana: in frequenza è una gaussiana centrata sulla frequenza della sinusoide, cioè un passa-banda orientato. Le cellule semplici della corteccia visiva primaria hanno risposte simili, e i filtri del primo layer di una CNN addestrata spesso ci assomigliano.</p></div>
""")

s(74, "Conclusions", "<p>Chiusura della lezione.</p>", kind="div")

s(75, "Takeaways", """
<ul>
<li>Le convoluzioni sono sistemi LSI (e viceversa).</li>
<li>La trasformata di Fourier è un <b>cambio di base</b> verso una base sinusoidale ortogonale, che rivela la struttura in frequenza.</li>
<li>Le convoluzioni sono <b>moltiplicazioni</b> in frequenza: i filtri convoluzionali si analizzano in frequenza per capirne il comportamento.</li>
<li>Gli strumenti di signal processing aiutano a progettare e spiegare le CNN moderne (convoluzioni dilatate, pooling, filtraggio in frequenza).</li>
</ul>
<div class="box b"><b>Dal libro · cap. 16, § 16.11 Concluding Remarks</b>
<p>Il libro chiude con il limite della rappresentazione di Fourier: i pixel dicono <b>dove</b> succede qualcosa ma poco su cosa sia; lo spettro dice <b>quali</b> frequenze ci sono ma niente su dove si trovano, perché ogni coefficiente dipende da tutta l'immagine (è "troppo globale"). Serve una rappresentazione intermedia, localizzata sia nello spazio sia in frequenza: è la motivazione per i filtri passa-banda localizzati, le piramidi (L6) e i banchi di filtri (L7). <a href="https://visionbook.mit.edu/image_processing_fourier.html">visionbook, cap. 16</a></p></div>
""")

s(76, "Next Lectures", """
<ul>
<li><b>Lezione 4</b> (lab): FFT pratica su segnali 1D.</li>
<li><b>Lezione 5</b>: filtri spaziali e temporali come kernel di convoluzione specifici, gradienti (filtri derivativi).</li>
<li><b>Lezione 6</b>: campionamento, aliasing, piramidi di immagini, rappresentazioni multirisoluzione.</li>
</ul>
""")

s(77, "References", """
<ul>
<li><a href="https://visionbook.mit.edu/">visionbook</a> (Torralba, Isola, Freeman, <i>Foundations of Computer Vision</i>), capitoli 15 e 16. Quasi tutte le figure vengono da lì.</li>
<li>Consiglio del docente: rifare da soli alcuni conti del libro. Quelli più utili sono nella guida allo studio qui sotto.</li>
</ul>
""")
