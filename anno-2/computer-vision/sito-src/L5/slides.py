
s(1, "Copertina", """
<p><b>Signal Processing for Images</b> · <b>Linear Filters: Blur and Gradients</b>. Quinta lezione.</p>
<p>Si prendono convoluzione e trasformata di Fourier (L3, L4) e si usano per progettare filtri concreti: prima quelli che <b>sfocano</b>, poi quelli che <b>derivano</b>.</p>
""")

s(2, "Goals of Today", """
<p>Obiettivo: usare convoluzione e Fourier per progettare <b>filtri applicati</b> alle immagini.</p>
<ol>
<li><b>Blur</b>: box, gaussiano, binomiale.</li>
<li><b>Derivate dell'immagine</b>: gradienti e laplaciano.</li>
</ol>
<p>Ogni filtro della lezione è un sistema <b>lineare e invariante per traslazione (LSI)</b>, quindi si studia da due punti di vista:</p>
<ul>
<li><b>risposta all'impulso</b> = kernel di convoluzione (vista spaziale);</li>
<li><b>risposta in frequenza</b> = trasformata di Fourier del kernel (vista in frequenza).</li>
</ul>
<div class="box k"><b>Filo logico della lezione</b><p>Per ogni filtro chiediti sempre due cose: che forma ha il kernel e che forma ha la sua risposta in frequenza. Quasi tutti i pregi e i difetti (ringing, rumore, shift di mezzo pixel) si leggono lì.</p></div>
""")

s(3, "Blur Filters", "<p>Filtri che sfocano: box, gaussiano, binomiale.</p>", kind="div", sec=("l5-blur", "Filtri di blur", "slide 3–24"))

s(4, "Blur Filters as Low-Pass Filters", """
<p>Un <b>filtro di blur</b> ha due letture equivalenti:</p>
<ul>
<li><b>spazio</b>: fa la media dei pixel vicini;</li>
<li><b>frequenza</b>: attenua le alte frequenze spaziali, cioè è un <b>passa-basso</b>.</li>
</ul>
<p>Tre scelte classiche:</p>
<ul>
<li><b>Box</b>: il più semplice ed economico.</li>
<li><b>Gaussiano</b>: liscio, separabile, con molte proprietà comode.</li>
<li><b>Binomiale</b>: approssimazione discreta ed efficiente della gaussiana.</li>
</ul>
<p>Si confrontano su tre assi: <b>forma del kernel</b>, <b>risposta in frequenza</b>, <b>comportamento se applicati più volte</b>.</p>
<p>Nota: il blur si può fare anche con operatori non lineari (es. filtro mediano); oggi solo sistemi LSI.</p>
<div class="box b"><b>Dal libro · cap. 17, § 17.1 Introduction</b><p>Il libro dà tre usi del blur, utili come risposta a "a cosa serve sfocare?":</p>
<ul><li><b>ridurre il rumore</b> (figura del cartello di STOP, slide 5);</li>
<li><b>far emergere strutture a una certa scala</b>, eliminando il dettaglio più fine (zebra, slide 13);</li>
<li><b>ricampionare</b> l'immagine: prima di ridurla va tolto il contenuto ad alta frequenza (L6).</li></ul>
<p>Cita anche alternative <b>non lineari</b> che sfocano preservando i bordi: la <b>diffusione anisotropa</b> e il <b>filtro bilaterale</b>. Nel corso restano fuori, ma è bene sapere che esistono quando all'orale si parla dei limiti del blur lineare (perde i bordi insieme al rumore).</p><p><a href="https://visionbook.mit.edu/blurring_2.html" target="_blank">Leggi nel libro</a></p></div>
""")

s(5, "Blur Example", """
<p><b>Figura:</b> (a) un segnale di STOP con forte rumore a grana fine; (b) la stessa immagine sfocata.</p>
<p>Il rumore sparisce quasi del tutto, ma si perdono anche i bordi netti delle lettere. È il compromesso di ogni passa-basso: il rumore sta alle alte frequenze, ma lì stanno anche i dettagli.</p>
""")

s(6, "Blurring Removes Sampling Artifacts", """
<p><b>Figura:</b> (a) ritratto a bassissima risoluzione (blocchi visibili, "pixelato"); (b) lo stesso sfocato, in cui il volto (Lincoln) diventa più riconoscibile.</p>
<p>I bordi netti fra i blocchi sono alte frequenze <b>introdotte dal campionamento</b>, non appartengono alla scena. Sfocandoli il sistema visivo torna a vedere la struttura a bassa frequenza, che è quella vera.</p>
<p>Collegamento con L6: blur e campionamento vanno sempre insieme (prefiltro anti-aliasing, piramidi).</p>
""")

s(7, "Box Filter", """
<span class="f">box<sub>N,M</sub>[n, m] = 1 se −N ≤ n ≤ N e −M ≤ m ≤ M, altrimenti 0</span>
<ul>
<li><b>Intuizione</b>: somma dei pixel in un rettangolo di (2N+1) × (2M+1) attorno al pixel.</li>
<li>Così è <b>non normalizzato</b>: per preservare la luminosità media si divide per il numero di tap, in modo che il <b>guadagno DC</b> sia ∑<sub>n</sub> h[n] = 1.</li>
<li><b>Separabile</b>: box 2D = box 1D sulle righe ∗ box 1D sulle colonne.</li>
</ul>
<p><b>Figura:</b> il kernel box<sub>1,1</sub>, 3×3 tutti a 1, disegnato come stem 3D.</p>
<div class="box w"><b>Attenzione: formulazione imprecisa</b><p>La slide dice "DC gain is just the mean value". Il guadagno DC è la <b>somma</b> dei coefficienti, H(0) = ∑<sub>n</sub> h[n]: è la risposta a un'immagine costante. È il box <i>normalizzato</i> (guadagno DC = 1) a restituire la <b>media</b> dei pixel della finestra.</p></div>
<div class="box b"><b>Dal libro · cap. 17, § 17.2 Box Filter</b><ul><li>Il libro ricava il guadagno DC mettendo in ingresso un'immagine costante ℓ[n, m] = a: ogni uscita somma (2N+1)(2M+1) pixel uguali, quindi ℓ<sub>out</sub> = a(2N+1)(2M+1). In generale <b>guadagno DC = ∑<sub>n,m</sub> h[n, m] = H[0, 0]</b>, il valore della DFT del kernel a frequenza zero. Per box<sub>1</sub> = [1, 1, 1] vale 3.</li>
<li>Per non cambiare il contrasto si normalizza il kernel in modo che sommi a 1: è questo box normalizzato che calcola la media.</li>
<li>Box grandi si calcolano in tempo costante per pixel con l'<b>immagine integrale</b> (somme cumulative su righe e colonne: la somma di un rettangolo si ottiene con 4 accessi).</li>
<li>Box non quadrati sfocano in modo direzionale: un box<sub>N,0</sub> orizzontale sfoca solo lungo le righe, uno verticale solo lungo le colonne (figura 17.2 del libro).</li></ul><p><a href="https://visionbook.mit.edu/blurring_2.html" target="_blank">Leggi nel libro</a></p></div>
""")

s(8, "Fourier of Box Filter", """
<ul>
<li>La risposta in frequenza del box è una <b>sinc</b> (periodica, perché il segnale è discreto):</li>
</ul>
<span class="f">H(ω) ∝ sin((2k+1)ω/2) / sin(ω/2)</span>
<ul>
<li>L'attenuazione delle alte frequenze <b>non è monotona</b>: dopo il primo zero la risposta risale (lobi laterali).</li>
</ul>
<p><b>Figura:</b> (a) box<sub>1</sub>[n], tre campioni a 1; (b) |Box<sub>1</sub>[u]|: massimo 3 in u = 0 (la somma dei tap), poi scende, si annulla e risale.</p>
<div class="box x"><b>Approfondimento</b><p>Qui k è la semiampiezza (il box ha 2k+1 tap, la N della slide precedente). La funzione sin((2k+1)ω/2)/sin(ω/2) si chiama <b>nucleo di Dirichlet</b>: vale 2k+1 in ω = 0 e si annulla in ω = 2πj/(2k+1). Si ottiene sommando la serie geometrica ∑<sub>n=−k..k</sub> e<sup>−jωn</sup>.</p></div>
""")

s(9, "Even vs Odd Size", """
<ul>
<li>Un kernel di dimensione <b>pari</b> non ha un campione centrale: l'uscita è spostata di <b>mezzo pixel</b>.</li>
<li>Per questo si usano quasi sempre kernel di dimensione <b>dispari</b>.</li>
</ul>
<p>Lo stesso problema tornerà con la derivata d<sub>0</sub> = [1, −1] (slide 27 e 30).</p>
""")

s(10, "Box Filter: Limitations", """
<ul>
<li><b>Non monotono</b>: i lobi laterali lasciano passare alcune alte frequenze e possono introdurre <b>ringing</b>.</li>
<li>Convolvere due box <b>non</b> dà un box più grande: [1, 1] ∗ [1, 1] = [1, 2, 1], che è un triangolo.
<ul><li>Avere blur <b>componibili</b> (blur ∘ blur = blur più grande della stessa famiglia) è importante per le rappresentazioni multiscala (L6).</li></ul></li>
<li><b>Artefatto visibile</b>: aspetto a blocchi o con aloni, soprattutto sui bordi netti.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 17, § 17.2.2 Limitations</b><p>Il libro rende concreta la non monotonia con due segnali passati in box<sub>1</sub> = [1, 1, 1] (non normalizzato):</p>
<ul><li>l'onda alla frequenza più alta [1, −1, 1, −1, …] esce <b>identica</b> (1 − 1 + 1 = 1): guadagno 1, cioè 1/3 del guadagno DC, quindi viene attenuata poco;</li>
<li>l'onda di periodo 3 [0.5, 0.5, −1, 0.5, 0.5, −1, …], più lenta, esce <b>tutta zero</b> (0.5 + 0.5 − 1 = 0).</li></ul>
<p>Una frequenza più bassa viene cancellata del tutto e una più alta no: è proprio la risposta "a sinc" della slide 8, con lo zero in ω = 2π/3.</p>
<p>Esempio del libro per la composizione: [1, 1, 1] ∗ [1, 1, 1] = [1, 2, 3, 2, 1], un triangolo. Sfocare due volte con un box non equivale a sfocare una volta con un box più grande.</p>
<p>Sul pari/dispari (slide 9) il libro nota che un box <b>pari</b> come [1, 1] annullerebbe la frequenza più alta, ma non è centrato e sposta l'uscita di mezzo pixel: per questo si preferiscono kernel dispari. Il binomiale [1, 2, 1] = [1, 1] ∗ [1, 1] prende il meglio dei due: dispari e con zero alla frequenza più alta.</p><p><a href="https://visionbook.mit.edu/blurring_2.html" target="_blank">Leggi nel libro</a></p></div>
""")

s(11, "Gaussian Filter", """
<p>Gaussiana 1D:</p>
<span class="f">g(x; σ) = 1/√(2πσ²) · exp(−x² / 2σ²)</span>
<p>Gaussiana 2D:</p>
<span class="f">g(x, y; σ) = 1/(2πσ²) · exp(−(x² + y²) / 2σ²)</span>
<ul>
<li><b>Simmetria radiale</b> in 2D: dipende solo da x² + y².</li>
<li><b>σ controlla la scala</b> spaziale del blur.</li>
<li>Le costanti sono scelte per avere <b>guadagno DC = 1</b> (integrale 1).</li>
</ul>
<div class="box w"><b>Attenzione: normalizzazione 2D sbagliata sulla slide</b><p>La slide scrive per la 2D lo stesso fattore della 1D, 1/√(2πσ²). Con quel fattore l'integrale non fa 1. La 2D è il prodotto di due gaussiane 1D, quindi il fattore è il prodotto dei due:</p>
<span class="f">1/√(2πσ²) · 1/√(2πσ²) = 1/(2πσ²)</span>
<p>(Lo stesso errore è ripetuto nella slide 12.)</p></div>
""")

s(12, "Gaussian Filter: Discretization", """
<ul>
<li><b>Discretizzazione</b>: si campiona la gaussiana su una griglia di circa <b>±3σ</b>; oltre, i valori sono trascurabili (entro 3σ sta il 99.7% della massa in 1D).</li>
<li>Kernel discreto, <b>non normalizzato</b>:</li>
</ul>
<span class="f">g[n, m; σ] = exp(−(n² + m²) / 2σ²)</span>
<p>In pratica si divide poi per la somma dei campioni, così il guadagno DC è esattamente 1.</p>
<div class="box k"><b>Da saper fare</b><p>Dimensione del kernel: 2⌈3σ⌉ + 1. Per σ = 1 → 7×7; per σ = 2 → 13×13. Il costo cresce con σ: per questo servono separabilità (slide 14) e piramidi (L6).</p></div>
<p>La formula continua in cima alla slide ha lo stesso errore di normalizzazione segnalato nella slide 11.</p>
<div class="box b"><b>Dal libro · cap. 17, § 17.3.1 Discretization</b><ul><li>Perché togliere la costante? Il libro osserva che la somma dei campioni della gaussiana discreta <b>non coincide</b> con l'integrale della continua, quindi 1/(2πσ²) non garantirebbe comunque guadagno DC 1. Si preferisce la forma con valore 1 nell'origine e si normalizza dopo, dividendo per la somma.</li>
<li>Troncatura: bastano i campioni in (−3σ, 3σ). Al bordo l'ampiezza è exp(−9/2) ≈ 0.011, circa l'<b>1% del valore centrale</b> (è il dato che il libro usa per giustificare la regola, più del 99.7% di massa).</li></ul><p><a href="https://visionbook.mit.edu/blurring_2.html" target="_blank">Leggi nel libro</a></p></div>
""")

s(13, "Example", """
<p><b>Figura:</b> una zebra filtrata con gaussiane di σ = 2, 4, 8.</p>
<ul>
<li>σ = 2: le strisce si vedono ancora.</li>
<li>σ = 4: le strisce si confondono, la sagoma resta.</li>
<li>σ = 8: resta solo una macchia scura con la forma dell'animale.</li>
</ul>
<p>σ decide quale <b>scala</b> di dettaglio sopravvive: le strisce hanno periodo di pochi pixel e spariscono per prime.</p>
""")

s(14, "Separability", """
<p>Dimostrazione della separabilità della gaussiana (kernel non normalizzato):</p>
<span class="f">g ∗ ℓ [n, m] = ∑<sub>k,l</sub> g[n−k, m−l] ℓ[k, l]</span>
<span class="f">= ∑<sub>k,l</sub> exp(−((n−k)² + (m−l)²) / 2σ²) ℓ[k, l]</span>
<span class="f">= ∑<sub>k</sub> exp(−(n−k)² / 2σ²) · ( ∑<sub>l</sub> exp(−(m−l)² / 2σ²) ℓ[k, l] )</span>
<span class="f">= g<sup>x</sup> ∗ (g<sup>y</sup> ∗ ℓ)</span>
<ul>
<li>Il passaggio chiave: exp(a + b) = exp(a) · exp(b), e il primo fattore non dipende da l, quindi esce dalla somma interna.</li>
<li>Si filtra prima lungo un asse con una gaussiana 1D, poi lungo l'altro.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Costo per pixel con un kernel K×K: <b>K² moltiplicazioni</b> in 2D, <b>2K</b> con due passate 1D. Per σ = 2 (K = 13): 169 contro 26.</p></div>
""")

s(15, "Gaussian Filter: Other Properties", """
<ul>
<li><b>Simmetria circolare + separabilità</b>: la gaussiana è l'<b>unico</b> filtro che ha entrambe.</li>
<li><b>Autosimile sotto Fourier</b>: la trasformata di una gaussiana è una gaussiana.</li>
</ul>
<span class="f">G(ω; σ) = exp(−ω²σ² / 2)</span>
<ul>
<li>Quindi il passa-basso gaussiano ha una risposta in frequenza <b>liscia, monotona, senza lobi laterali</b>: risolve il difetto principale del box.</li>
<li>Nota l'inversione: σ grande nello spazio = gaussiana stretta in frequenza (larghezza 1/σ), cioè blur più forte.</li>
<li><b>Composizione</b>: la convoluzione di due gaussiane è una gaussiana, e <b>si sommano le varianze</b>:</li>
</ul>
<span class="f">g<sub>σ1</sub> ∗ g<sub>σ2</sub> = g<sub>σ3</sub>,   σ<sub>3</sub>² = σ<sub>1</sub>² + σ<sub>2</sub>²</span>
<p>È la base delle piramidi gaussiane (L6).</p>
<div class="box k"><b>Da saper dimostrare</b><p>Con il teorema di convoluzione: G<sub>σ1</sub>(ω)·G<sub>σ2</sub>(ω) = exp(−ω²(σ<sub>1</sub>² + σ<sub>2</sub>²)/2) = G<sub>σ3</sub>(ω). Esempio: due blur con σ = 1 danno σ = √2 ≈ 1.41, non 2.</p></div>
<div class="box b"><b>Dal libro · cap. 17, § 17.3.2 Properties of the Continuous Gaussian</b><ul><li>Il libro formula la prima proprietà così: la gaussiana è "the only completely circularly symmetric operator that is separable". In 2D anche la trasformata è radiale: G(w<sub>x</sub>, w<sub>y</sub>; σ) = exp(−(w<sub>x</sub>² + w<sub>y</sub>²)σ²/2), monotona decrescente con la frequenza.</li>
<li>Costo: convolvere direttamente un kernel N×N costa in proporzione a N², la cascata di due kernel 1D in proporzione a 2N (g<sup>x</sup>[n] = g[n, 0], g<sup>y</sup>[m] = g[0, m]).</li>
<li>Una proprietà in più rispetto alla slide: per <b>σ → 0 la gaussiana tende all'impulso</b>, cioè al filtro identità. È il motivo per cui σ si può leggere come una "manopola" continua che va dall'immagine originale a blur sempre più forti.</li></ul><p><a href="https://visionbook.mit.edu/blurring_2.html" target="_blank">Leggi nel libro</a></p></div>
""")

s(16, "Gaussian Filter: Two More Connections", """
<ul>
<li><b>Equazione del calore</b>: g<sub>σ</sub> è la soluzione di</li>
</ul>
<span class="f">∂u/∂t = ∇²u</span>
<ul>
<li style="list-style:none">al tempo <b>t = σ²/2</b>, partendo da una sorgente puntiforme (un impulso). Sfocare con σ più grande è letteralmente "lasciar diffondere il calore più a lungo". Tornerà nello scale-space (L6).</li>
<li><b>Teorema del limite centrale</b>: convolvere con se stesso molte volte un kernel "ragionevole" (positivo, a varianza finita) converge a una gaussiana. Per questo box e binomiali ripetuti approssimano un blur gaussiano.</li>
</ul>
<div class="box k"><b>Da saper verificare</b><p>La soluzione con sorgente puntiforme in 2D è u(x, t) = 1/(4πt) · exp(−|x|²/4t). Confronta con g<sub>σ</sub>: 2σ² = 4t, cioè t = σ²/2. La formula della slide è corretta. Da qui anche la composizione: tempi che si sommano = varianze che si sommano.</p></div>
""")

s(17, "Gaussian Filter: Limitations", """
<ul>
<li>La gaussiana continua ha supporto su tutto ℝ: <b>troncarla e campionarla rompe le proprietà esatte</b>.
<ul>
<li>il kernel troncato non somma esattamente a 1 (piccolo errore sul DC);</li>
<li>la somma delle varianze σ<sub>3</sub>² = σ<sub>1</sub>² + σ<sub>2</sub>² vale solo approssimativamente.</li>
</ul></li>
<li>Con convoluzioni ripetute gli errori si <b>accumulano</b> e il risultato si allontana dalla gaussiana ideale.</li>
</ul>
<p>Il <b>filtro binomiale</b> risolve questi problemi con un'aritmetica discreta ben educata.</p>
<div class="box x"><b>Approfondimento</b><p>Anche la separabilità e la simmetria circolare diventano approssimate su griglia: per σ piccoli (sotto circa 1 pixel) la gaussiana campionata è molto poco "gaussiana". È un caso in cui il binomiale è preferibile.</p></div>
<div class="box b"><b>Dal libro · cap. 17, § 17.3.3 Limitations</b><p>Il libro mostra la rottura delle proprietà con un esempio numerico. Con σ² = 1/2 e 5 campioni:</p>
<span class="f">g<sub>5</sub>[n] = [0.0183, 0.3679, 1.0000, 0.3679, 0.0183]</span>
<ul><li>In teoria g<sub>5</sub> ∗ g<sub>5</sub> dovrebbe essere la gaussiana con σ² = 1. Rifacendo il conto e riportando il centro a 1 si ottiene circa [0.135, 0.589, 1, 0.589, 0.135], mentre campionando direttamente la gaussiana con σ² = 1 si ottiene [0.135, 0.607, 1, 0.607, 0.135]: vicini, ma <b>non uguali</b>. Ripetendo, l'errore si accumula.</li>
<li>Anche il comportamento alle alte frequenze si rompe: g<sub>5</sub> ∗ [1, −1, 1, −1, …] <b>non è zero</b> (normalizzando g<sub>5</sub> resta un'oscillazione di ampiezza circa 0.17), mentre la gaussiana continua attenua le alte frequenze quasi del tutto.</li></ul>
<p>(I due vettori ricavati sono conti nostri, fatti con numpy, sull'esempio del libro.)</p><p><a href="https://visionbook.mit.edu/blurring_2.html" target="_blank">Leggi nel libro</a></p></div>
""")

s(18, "Binomial Filters", """
<ul>
<li>Si costruiscono convolvendo ripetutamente il kernel più semplice possibile, [1, 1], con se stesso (<b>triangolo di Tartaglia</b>):</li>
</ul>
<span class="f">[1, 1] ∗ [1, 1] = [1, 2, 1],   [1, 2, 1] ∗ [1, 1] = [1, 3, 3, 1], …</span>
<ul>
<li>La convoluzione di n copie di [1, 1] dà i <b>coefficienti binomiali</b> C(n, k), k = 0, …, n: è il filtro b<sub>n</sub>, con n+1 tap.</li>
<li>Coefficienti <b>interi</b>: aritmetica esatta, nessun errore di arrotondamento.</li>
</ul>
<p><b>Figura:</b> tabella di b<sub>0</sub> … b<sub>8</sub> con le rispettive varianze σ<sup>2</sup><sub>n</sub> = 0, 1/4, 1/2, …, 2.</p>
""")

s(19, "Binomial Filters: Properties", """
<ul>
<li><b>Guadagno DC = 2<sup>n</sup></b> (somma dei binomiali): si normalizza dividendo per 2<sup>n</sup>.</li>
<li><b>Varianza σ² = n/4</b>: cresce linearmente con il numero di convoluzioni con [1, 1].</li>
<li><b>Composizione esatta</b>: b<sub>n</sub> ∗ b<sub>m</sub> = b<sub>n+m</sub>, senza approssimazioni (a differenza delle gaussiane troncate).</li>
<li>n = 2 dà il kernel a 3 tap onnipresente <b>[1, 2, 1]/4</b>.</li>
<li>Risposta in frequenza <b>monotona decrescente</b>, senza lobi laterali, come la gaussiana.</li>
<li>Kernel simmetrico.</li>
<li>La frequenza più alta possibile, [1, −1, 1, −1, …], viene <b>annullata</b> da [1, 2, 1]: 1 − 2 + 1 = 0. Con il box dispari [1, 1, 1] no: 1 − 1 + 1 = 1.</li>
</ul>
<div class="box k"><b>Da saper ricavare</b><ul>
<li>Varianza: [1, 1]/2 ha varianza 1/4 (due tap a distanza 1, ognuno con peso 1/2); b<sub>n</sub> è n di questi in convoluzione e le varianze si sommano: n/4. Quindi b<sub>4</sub> = [1 4 6 4 1]/16 ha σ = 1.</li>
<li>Risposta in frequenza: [1, 1]/2 ha |H| = |cos(ω/2)|, quindi b<sub>n</sub> ha <b>|H(ω)| = cos<sup>n</sup>(ω/2)</b>, monotona in [0, π] e nulla in ω = π.</li></ul></div>
<div class="box b"><b>Dal libro · cap. 17, § 17.4.1 Properties</b><p>Il libro scrive la risposta in frequenza con la DFT su N campioni:</p>
<span class="f">B<sub>2</sub>[u] = 2 + 2 cos(2πu/N),   B<sub>2n</sub>[u] = (2 + 2 cos(2πu/N))<sup>n</sup></span>
<ul><li>È la stessa cosa della formula cos<sup>n</sup>(ω/2) del riquadro sopra: con ω = 2πu/N si ha 2 + 2 cos ω = 4 cos²(ω/2).</li>
<li>B<sub>2</sub> decresce in modo monotono e senza ondulazioni, e vale <b>zero</b> alla frequenza più alta (figura 17.7, DFT con N = 20).</li>
<li>Proprietà enunciata per <b>tutti</b> i b<sub>n</sub> con n ≥ 1: convoluti con [1, −1, 1, −1, …] danno il segnale nullo. È una conseguenza del fattore [1, 1] contenuto in ogni b<sub>n</sub>.</li>
<li>Il libro presenta b<sub>2</sub> = [1, 2, 1] come "the simplest approximation to the Gaussian filter".</li></ul><p><a href="https://visionbook.mit.edu/blurring_2.html" target="_blank">Leggi nel libro</a></p></div>
""")

s(20, "2D Binomial Filters", """
<ul>
<li><b>Costruzione separabile</b>: B<sub>n</sub>(x, y) = b<sub>n</sub>(x) · b<sub>n</sub>(y).</li>
<li>Il kernel binomiale 3×3 standard (n = 2) è il prodotto esterno di [1, 2, 1]/4 con se stesso:</li>
</ul>
<span class="f">(1/16) · [[1, 2, 1], [2, 4, 2], [1, 2, 1]]</span>
<ul>
<li>Smoothing <b>veloce, esatto, separabile</b>: utilissimo per le piramidi (L6 usa b<sub>4</sub>, 5×5) e per il filtraggio su hardware e dispositivi embedded (solo somme e shift).</li>
</ul>
""")

s(21, "Box vs. Gaussian vs. Binomial", """
<p><b>Figura:</b> la foto dell'astronauta filtrata con un box 5×5, una gaussiana σ = 2 e un binomiale (16 applicazioni di [1, 2, 1]/4).</p>
<ul>
<li>Il box lascia strutture un po' a blocchi sui bordi netti.</li>
<li>Gaussiana e binomiale danno un blur morbido e uniforme; il binomiale qui è il più sfocato.</li>
</ul>
<div class="box w"><b>Attenzione: "n = 16" non è il b<sub>n</sub> della slide 18</b><p>Qui e nella legenda della slide 22 "n = 16" conta le applicazioni di [1, 2, 1]/4 = b<sub>2</sub>. Sedici applicazioni danno <b>b<sub>32</sub></b>, con σ² = 32/4 = 8, cioè σ ≈ 2.83: più largo della gaussiana σ = 2 del confronto. Per questo il binomiale sembra più sfocato. Il binomiale equivalente alla gaussiana σ = 2 (σ² = 4) è b<sub>16</sub>, cioè 8 applicazioni di [1, 2, 1]/4.</p></div>
""")

s(22, "Frequency Responses", """
<p><b>Figura:</b> |H(ω)| normalizzato dei tre filtri, frequenza da 0 a π.</p>
<ul>
<li><b>Box a 5 tap</b> (blu): si annulla in 0.4π e 0.8π e risale fra i due zeri (lobo laterale di circa 0.25): sono le frequenze che "passano" e causano artefatti.</li>
<li><b>Gaussiana</b> (arancione) e <b>binomiale</b> (verde): discesa liscia e monotona fino a zero.</li>
</ul>
<div class="box k"><b>Da saper verificare</b><p>Box a 5 tap: zeri in ω = 2πj/5, cioè 0.4π e 0.8π, come in figura. A ω = 0.2π: gaussiana σ = 2, exp(−2ω²) ≈ 0.45; binomiale cos<sup>32</sup>(ω/2) ≈ 0.20, coerente con la curva verde (è b<sub>32</sub>, vedi slide 21).</p></div>
""")

s(23, "Noisy Box vs Binomial", """
<p><b>Figura:</b> (a) una barca a vela con un rumore a scacchiera ad alta frequenza; (b) filtrata con un box; (c) filtrata con un binomiale.</p>
<ul>
<li>Il <b>box</b> lascia ancora una trama residua: la frequenza della scacchiera cade su un suo lobo laterale.</li>
<li>Il <b>binomiale</b> la elimina: annulla esattamente la frequenza più alta (slide 19).</li>
</ul>
<div class="box b"><b>Dal libro · cap. 17, § 17.4.2 2D Binomial Filters</b><p>Nella figura del libro il confronto è fra un <b>box 3×3</b> e il <b>binomiale b<sub>2,2</sub></b> 3×3, cioè due kernel della stessa dimensione: il box non riesce a togliere del tutto la scacchiera, il binomiale la cancella perfettamente. La scacchiera (−1)<sup>n+m</sup> è la frequenza più alta in entrambe le direzioni: il box 3×3 ha lì guadagno 1/9 relativo al DC (non zero), il binomiale ha guadagno 0.</p><p><a href="https://visionbook.mit.edu/blurring_2.html" target="_blank">Leggi nel libro</a></p></div>
""")

s(24, "Conclusions", """
<p><b>Raccomandazioni pratiche</b></p>
<ul>
<li><b>Box</b>: veloce, ma introduce artefatti.</li>
<li><b>Gaussiana</b>: comportamento in frequenza ottimale nel continuo; nel discreto le proprietà si "rompono".</li>
<li><b>Binomiale</b>: veloce e conserva nel discreto le proprietà del blur gaussiano.</li>
</ul>
<p><b>Intuizione</b></p>
<ul>
<li>nello <b>spazio</b> il blur fa la media dei pixel e toglie il rumore;</li>
<li>in <b>frequenza</b> il blur attenua le componenti ad alta frequenza.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 17, § 17.5 Concluding Remarks</b><p>Il messaggio pratico del libro: il kernel <b>[1, 2, 1]/4</b> (e la sua versione 2D) è da tenere sempre a portata di mano, sia per togliere rumore sia per il <b>sottocampionamento di un fattore 2</b>. Lo si ritrova nelle piramidi di immagini (L6) e anche nelle operazioni di pooling delle reti neurali.</p><p><a href="https://visionbook.mit.edu/blurring_2.html" target="_blank">Leggi nel libro</a></p></div>
""")

s(25, "Image Derivatives", "<p>Seconda parte: misurare le variazioni.</p>", kind="div", sec=("l5-derivate", "Derivate discrete", "slide 25–31"))

s(26, "Why Derivatives?", """
<ul>
<li>Le derivate misurano i <b>cambiamenti</b>: bordi, contorni, gradienti di tessitura.</li>
<li>L'operatore che calcola ∂I/∂x e ∂I/∂y è <b>lineare e invariante per traslazione</b>, quindi si implementa con una <b>convoluzione</b>.</li>
<li>Applicazioni: rilevamento di bordi e contorni, shape-from-shading e altri indizi 3D, editing di immagini, sharpening, separazione illuminazione/riflettanza.</li>
</ul>
<p><b>Figura:</b> (a) edificio con cupola (MIT); (b) e (c) le due derivate, su fondo grigio (= 0). In una risaltano le colonne verticali, nell'altra le strutture orizzontali (cornicione, gradini): ogni derivata vede i bordi perpendicolari alla sua direzione.</p>
<div class="box b"><b>Dal libro · cap. 18, § 18.2 Discretizing Image Derivatives</b><p>Il libro parte dalla definizione continua, ∂ℓ/∂x = lim<sub>ε→0</sub> (ℓ(x+ε, y) − ℓ(x, y))/ε, ed elenca <b>tre ostacoli</b> nel calcolarla su un'immagine vera:</p>
<ol><li>l'immagine è <b>campionata</b>: il limite non si può fare, si hanno solo i pixel;</li>
<li>ci sono punti <b>non derivabili</b> (i bordi degli oggetti sono quasi discontinuità);</li>
<li>il <b>rumore</b>: la differenza fra pixel vicini può essere dominata dal rumore più che dal segnale.</li></ol>
<p>Le slide 27–31 rispondono al punto 1, le slide 38–45 al punto 3. Nell'introduzione (§ 18.1) il libro motiva le derivate anche come indizio dell'informazione 3D persa nella proiezione (forme, ombreggiature).</p><p><a href="https://visionbook.mit.edu/derivatives.html" target="_blank">Leggi nel libro</a></p></div>
""")

s(27, "Discretizing the Derivative", """
<p>Derivata continua: f′(x) = lim<sub>h→0</sub> (f(x+h) − f(x)) / h. Due approssimazioni discrete standard:</p>
<span class="f">d<sub>0</sub> = [1, −1]     d<sub>1</sub> = ½ [1, 0, −1]</span>
<ul>
<li><b>d<sub>0</sub></b>: differenza in avanti, 2 tap, <b>shift di mezzo campione</b> (il risultato sta fra due campioni).</li>
<li><b>d<sub>1</sub></b>: differenza centrale, 3 tap, <b>nessuno shift</b>, ma salta il campione centrale.</li>
</ul>
<div class="box k"><b>Da capire</b><p>Sono kernel di convoluzione: (ℓ ∗ d<sub>0</sub>)[n] = ℓ[n] − ℓ[n−1] e (ℓ ∗ d<sub>1</sub>)[n] = (ℓ[n+1] − ℓ[n−1])/2. Il segno "al contrario" di [1, −1] viene dal ribaltamento del kernel nella convoluzione. d<sub>0</sub> ha dimensione pari: è il caso della slide 9.</p></div>
""")

s(28, "Example", """
<p><b>Figura:</b> (a) un segnale ℓ[n] a gradino: sale da 0 a 2 intorno a n = 5 e riscende intorno a n = 15; (b) il kernel d<sub>0</sub>; (c) ℓ ∘ d<sub>0</sub>; (d) il kernel d<sub>1</sub>; (e) ℓ ∘ d<sub>1</sub>.</p>
<ul>
<li>Dove il segnale è costante la derivata è 0; picchi <b>positivi</b> sulla salita, <b>negativi</b> sulla discesa.</li>
<li>d<sub>1</sub> dà picchi più bassi e più larghi (media su due passi).</li>
</ul>
<p>(Nelle figure del Vision Book il simbolo ∘ indica la convoluzione.)</p>
""")

s(29, "Frequency Response", """
<p><b>Figura:</b> |D<sub>0</sub>[u]| e |D<sub>1</sub>[u]| a confronto con la risposta ideale della derivata (linea nera, |ω|).</p>
<ul>
<li>Entrambe sono buone approssimazioni solo alle <b>basse frequenze</b>.</li>
<li><b>d<sub>0</sub></b> approssima meglio il modulo (cresce fino al bordo della banda), ma introduce uno <b>sfasamento</b> (il mezzo pixel).</li>
<li><b>d<sub>1</sub></b> non ha sfasamento, ma torna a 0 alla frequenza massima: ignora le oscillazioni più rapide.</li>
</ul>
<div class="box k"><b>Da saper ricavare</b><ul>
<li>D<sub>0</sub>(ω) = 1 − e<sup>−jω</sup> = 2j sin(ω/2) e<sup>−jω/2</sup>: modulo 2|sin(ω/2)|, fase lineare = ritardo di mezzo campione.</li>
<li>D<sub>1</sub>(ω) = (e<sup>jω</sup> − e<sup>−jω</sup>)/2 = j sin ω: modulo |sin ω|, nullo in ω = π, nessun ritardo.</li>
<li>Ideale: jω. Per ω piccolo sin ω ≈ ω e 2 sin(ω/2) ≈ ω.</li></ul></div>
<div class="box b"><b>Dal libro · cap. 18, § 18.2 Discretizing Image Derivatives</b><p>Il libro scrive le risposte con la DFT su N campioni (frequenza discreta u, ω = 2πu/N):</p>
<span class="f">D<sub>0</sub>[u] = 1 − exp(−2πju/N) = exp(−πju/N) · 2j sin(πu/N)</span>
<span class="f">D<sub>1</sub>[u] = j sin(2πu/N)</span>
<ul><li>Il fattore exp(−πju/N) è una fase lineare: è lo <b>spostamento di mezzo campione</b> (verso destra, dice il libro).</li>
<li>D<sub>1</sub> non ha fase aggiunta, ma approssima la derivata su un intervallo di frequenze più piccolo: il segnale alternato [1, −1, 1, −1, …] dà uscita zero.</li>
<li>Il riferimento ideale nel grafico è |2πu/N|, cioè |ω|.</li></ul><p><a href="https://visionbook.mit.edu/derivatives.html" target="_blank">Leggi nel libro</a></p></div>
""")

s(30, "2D derivatives", """
<p>In 2D si calcolano separatamente le derivate lungo x e lungo y. Con d<sub>0</sub> la slide scrive d<sub>0</sub><sup>x</sup> come vettore colonna (1, −1)<sup>T</sup> e d<sub>0</sub><sup>y</sup> come vettore riga (1 −1).</p>
<p>Le uscite sono <b>disallineate</b>:</p>
<ul>
<li>la derivata lungo x è spostata di mezzo pixel in x;</li>
<li>quella lungo y di mezzo pixel in y.</li>
</ul>
<p>Quindi non si possono combinare pixel per pixel (per esempio nel modulo del gradiente) senza un errore di posizione. d<sub>1</sub> o Sobel (slide 46) non hanno questo problema.</p>
<div class="box w"><b>Attenzione: convenzione x/y incoerente con Sobel</b><p>Qui d<sub>0</sub><sup>x</sup> è un vettore colonna, quindi deriva lungo la direzione verticale. Nella slide 46 invece S<sub>x</sub> deriva lungo le righe (il [1, 0, −1] è orizzontale). Con la convenzione usuale (x orizzontale, y verticale) la derivata lungo x è il kernel <b>riga</b> (1 −1) e quella lungo y il kernel <b>colonna</b>. All'esame dichiara la convenzione che usi.</p></div>
<div class="box b"><b>Dal libro · cap. 18, § 18.2 Discretizing Image Derivatives</b><p>Il libro propone anche l'<b>operatore di Roberts</b> (1963), con due kernel 2×2 in diagonale:</p>
<span class="f">[[1, 0], [0, −1]]   e   [[0, 1], [−1, 0]]</span>
<p>Le due uscite misurano le derivate lungo le diagonali e sono entrambe centrate nello <b>stesso punto</b> (il centro del quadrato 2×2), quindi non sono disallineate fra loro come le due d<sub>0</sub> in x e y. Resta lo spostamento di mezzo pixel rispetto alla griglia, ma è uguale per le due componenti, e il gradiente si può combinare punto per punto. È l'operatore (c) della figura alla slide 49.</p><p><a href="https://visionbook.mit.edu/derivatives.html" target="_blank">Leggi nel libro</a></p></div>
""")

s(31, "Summary", """
<ul>
<li>Abbiamo un'approssimazione discreta della derivata.</li>
<li>È <b>veloce</b> (2 o 3 tap).</li>
<li>È <b>imperfetta</b>: spostata (d<sub>0</sub>) e scalata in frequenza (entrambe) rispetto alla derivata vera.</li>
</ul>
""")

s(32, "Gradient-Based Image Representation", "<p>Il gradiente come rappresentazione dell'immagine, e come tornare indietro.</p>", kind="div", sec=("l5-rappr", "Rappresentazioni col gradiente", "slide 32–37"))

s(33, "Gradient-Based Image Representation", """
<p>Tre motivi per rappresentare un'immagine con i suoi gradienti:</p>
<ul>
<li>i gradienti <b>evidenziano la struttura</b>, come i bordi;</li>
<li>sono <b>"quasi" invertibili</b>: dai gradienti si ricostruisce l'immagine, a meno della media (slide 34–36);</li>
<li>esempio motivante: l'<b>editing di immagini</b> (slide 37).</li>
</ul>
""")

s(34, "Inverting Gradient-Based Image Representations", """
<p>In 1D, la convoluzione con d<sub>0</sub> = (1 −1) su 5 campioni con <b>zero padding</b> è la matrice bidiagonale D<sub>0</sub>: 1 sulla diagonale, −1 sotto.</p>
<ul>
<li>Riga i: r[i] = ℓ[i] − ℓ[i−1], con ℓ[−1] = 0.</li>
<li>L'inversa D<sub>0</sub><sup>−1</sup> è la matrice triangolare inferiore di tutti 1: la <b>somma cumulativa</b>.</li>
</ul>
<p>L'inversione è <b>esatta</b>, ma solo perché lo zero padding fissa il primo valore: r[0] = ℓ[0].</p>
<div class="box k"><b>Da capire</b><p>È la versione discreta di "integrare la derivata": ℓ[n] = ∑<sub>i≤n</sub> r[i]. Nel continuo serve una costante di integrazione; qui la fornisce lo zero padding.</p></div>
""")

s(35, "Inversion: valid-conv case", """
<p>Con padding <b>valid</b> (si tengono solo le uscite con tutti gli ingressi dentro l'immagine) si perde la prima riga: D<sub>0</sub> è 4 × 5, righe (−1, 1) che scorrono.</p>
<ul>
<li><b>Non è invertibile</b>: N ingressi, N − 1 uscite. Il nucleo contiene i vettori costanti (la derivata di una costante è 0).</li>
<li>Si usa la <b>pseudo-inversa</b> D<sub>0</sub><sup>+</sup> (5 × 4, riportata sulla slide con fattore 1/5).</li>
<li>Si perde la <b>componente DC</b>, cioè la media dell'immagine.</li>
</ul>
<div class="box x"><b>Approfondimento</b><p>D<sub>0</sub><sup>+</sup> r è la soluzione di minima norma: fra tutti i segnali con quelle differenze, quello a <b>media zero</b>. Verificato numericamente: la matrice della slide coincide con <code>np.linalg.pinv</code> di D<sub>0</sub>.</p></div>
<div class="box b"><b>Dal libro · cap. 18, § 18.3 Gradient-Based Image Representation</b><ul><li>Perché rappresentare un'immagine con le derivate? Secondo il libro perché permette di <b>manipolare aspetti dell'immagine difficili da controllare</b> agendo direttamente sui pixel (es. togliere un oggetto, slide 37).</li>
<li>Con le differenze "valid" la matrice ha una riga in meno delle colonne e si usa la <b>pseudo-inversa</b>. Il prezzo, dice il libro, è che il segnale ricostruito ha <b>media zero</b>: si perde un grado di libertà che dalle derivate non si può stimare.</li>
<li>In 2D il libro accenna che la pseudo-inversa si calcola in modo efficiente nel <b>dominio di Fourier</b> (con bordi circolari le derivate sono convoluzioni, diagonali nella base DFT, e invertirle significa dividere per la loro risposta in frequenza dove non è nulla).</li></ul><p><a href="https://visionbook.mit.edu/derivatives.html" target="_blank">Leggi nel libro</a></p></div>
""")

s(36, "Example", """
<span class="f">ℓ = [1, 1, 2, 2, 0]</span>
<span class="f">ℓ̂ = D<sub>0</sub><sup>+</sup> r = [−0.2, −0.2, 0.8, 0.8, −1.2]</span>
<p>La media di ℓ è (1+1+2+2+0)/5 = 1.2, e infatti ℓ̂ = ℓ − 1.2: la ricostruzione è esatta <b>a meno della media</b>.</p>
<div class="box w"><b>Attenzione: segno di r sbagliato sulla slide</b><p>Con la D<sub>0</sub> della slide 35 (righe −1, 1) si ha r[i] = ℓ[i+1] − ℓ[i], quindi:</p>
<span class="f">r = D<sub>0</sub> ℓ = [0, 1, 0, −2]</span>
<p>La slide scrive [0, −1, 0, 2], cioè il segno opposto. Il risultato ℓ̂ della slide invece è giusto, ma si ottiene da r = [0, 1, 0, −2]: con il r della slide verrebbe [0.2, 0.2, −0.8, −0.8, 1.2].</p><p>L'errore viene dal libro: in § 18.3 l'esempio è identico, con la stessa D<sub>0</sub>, lo stesso r = [0, −1, 0, 2] e lo stesso ℓ̂. Verificato con numpy: D<sub>0</sub>ℓ = [0, 1, 0, −2] e D<sub>0</sub><sup>+</sup>D<sub>0</sub>ℓ = [−0.2, −0.2, 0.8, 0.8, −1.2].</p></div>
""")

s(37, "Image Editing in the Gradient Domain", """
<p><b>Figura:</b> pipeline encoding → edit → decoding.</p>
<ol>
<li><b>Encoding</b>: il segnale di STOP è convertito nelle due derivate dx e dy.</li>
<li><b>Edit</b>: entrambe sono moltiplicate per una maschera nera che azzera i gradienti nella zona della scritta.</li>
<li><b>Decoding</b>: si ricostruisce l'immagine dai gradienti modificati.</li>
</ol>
<p>Risultato: un cartello rosso <b>senza la scritta</b>, riempito con il colore giusto.</p>
<p>Punto chiave: <b>non si è specificato nulla su colori o orientazioni</b>. Togliendo i bordi della scritta, la ricostruzione (integrazione) riempie la zona in modo liscio, raccordandola ai bordi rimasti.</p>
<div class="box x"><b>Approfondimento</b><p>In 2D un campo di gradienti modificato in genere non è più il gradiente di nessuna immagine. Si cerca allora l'immagine il cui gradiente è il più vicino possibile ai minimi quadrati: si risolve un'<b>equazione di Poisson</b> ∇²ℓ = div(g). È il <i>Poisson image editing</i> (Pérez et al., 2003), usato per inpainting e clonazione senza cuciture.</p></div>
<div class="box b"><b>Dal libro · cap. 18, § 18.4 Image Editing in the Gradient Domain</b><ul><li><b>Codifica</b>: r = [D<sub>x</sub>; D<sub>y</sub>] ℓ, le due derivate impilate in un solo vettore. r ha valori grandi solo dove l'intensità cambia.</li>
<li><b>Modifica</b>: si mettono a zero le derivate nella zona della scritta "STOP".</li>
<li><b>Decodifica</b>: pseudo-inversa di [D<sub>x</sub>; D<sub>y</sub>], calcolata nel dominio di Fourier. Poiché lì i gradienti sono nulli, l'integrazione propaga il colore dei dintorni dentro la zona cancellata.</li></ul>
<p>Il libro non parla di equazione di Poisson: la soluzione ai minimi quadrati della pseudo-inversa è la stessa cosa detta in un altro modo (vedi riquadro sopra).</p><p><a href="https://visionbook.mit.edu/derivatives.html" target="_blank">Leggi nel libro</a></p></div>
""")

s(38, "Blurred Derivatives", "<p>Derivate e rumore: sfocare prima di derivare.</p>", kind="div", sec=("l5-gauss-der", "Derivate sfocate e laplaciano", "slide 38–58"))

s(39, "Blurred Derivatives", """
<ul>
<li>Le derivate <b>amplificano il rumore</b>.</li>
<li>Esempio: rumore gaussiano i.i.d. di varianza σ² su ogni pixel. Dopo la convoluzione con d<sub>0</sub> = (1 −1) la varianza diventa <b>2σ²</b> (differenza di due variabili indipendenti: le varianze si sommano).</li>
<li>C'è anche un problema di <b>scala</b>: progettando un detector bisogna scegliere a quale scala/risoluzione misurare le variazioni.</li>
</ul>
<p><b>Figura:</b> (a) STOP con rumore; (b) la sua derivata, dominata dal rumore, con il cartello appena visibile; (c) la derivata sfocata, dove i bordi del cartello e delle lettere emergono netti.</p>
<div class="box k"><b>Da saper spiegare</b><p>In frequenza il motivo è chiaro: la derivata ideale ha guadagno |ω|, cresce con la frequenza, e il rumore bianco ha energia uguale a tutte le frequenze. Moltiplicare per |ω| esalta proprio la parte dove il rumore domina il segnale.</p></div>
<div class="box x"><b>Approfondimento</b><p>Con d<sub>1</sub> = ½[1, 0, −1] la varianza del rumore diventa (¼ + ¼)σ² = σ²/2: il fattore ½ e il salto di un campione aiutano.</p></div>
""")

s(40, "Efficient Blurred Derivatives", """
<p><b>Derivata sfocata</b>: si calcola la derivata, poi si sfoca per togliere il rumore (le alte frequenze).</p>
<p>Derivata e convoluzione <b>commutano</b>:</p>
<span class="f">(∂ℓ/∂x) ∗ g = ℓ ∗ (∂g/∂x)</span>
<ul>
<li>Quindi basta <b>un solo kernel</b>: la derivata del kernel di blur. Si fa una sola convoluzione invece di due.</li>
</ul>
<div class="box k"><b>Da saper dimostrare</b><p>Sono entrambe operazioni LSI, e i sistemi LSI commutano. In frequenza: la derivata moltiplica per jω, il blur per G(ω); il prodotto jω·G(ω) non dipende dall'ordine, ed è la trasformata di ∂g/∂x.</p></div>
""")

s(41, "Gaussian Derivatives", """
<p>Le <b>derivate di gaussiana</b> sfocano e derivano in un colpo solo:</p>
<span class="f">g′<sub>σ</sub>(x) = −(x / σ²) · g<sub>σ</sub>(x)</span>
<p><b>Figura:</b> (a) la gaussiana 2D; (b) la sua derivata lungo x: un lobo positivo e uno negativo affiancati.</p>
<div class="box k"><b>Da saper fare</b><p>Derivando g = c·exp(−x²/2σ²) si ottiene c·exp(−x²/2σ²)·(−2x/2σ²) = −(x/σ²)g. La formula della slide è corretta. Il kernel è dispari: somma zero, quindi risposta nulla sulle zone costanti.</p></div>
""")

s(42, "Gaussian Derivatives at Multiple Scales", """
<p><b>Figura:</b> derivate prima e seconda della gaussiana per σ = 1, 2, 4.</p>
<p><b>Le derivate non sono invarianti alla scala.</b></p>
<ul>
<li><b>σ grande</b>: kernel più largo, risponde a variazioni più grossolane, meno sensibile al rumore.</li>
<li><b>σ piccolo</b>: risponde al dettaglio fine, più sensibile al rumore.</li>
<li><b>Scegliere σ = scegliere la scala</b> a cui si misura la variazione.</li>
</ul>
<p>Nel grafico le ampiezze scalano con σ: la derivata prima con 1/σ², la seconda con 1/σ³ (per la gaussiana normalizzata). È il punto di partenza della normalizzazione di scala che servirà in L6–L7.</p>
""")

s(43, "Example", """
<p><b>Figura:</b> in alto la zebra filtrata con derivate di gaussiana a σ = 1, 2, 4; in basso i kernel corrispondenti visti in 3D.</p>
<ul>
<li>σ = 1: rispondono i bordi delle singole strisce.</li>
<li>σ = 4: le strisce spariscono, rimangono i contorni della sagoma.</li>
</ul>
<p>Stessa immagine, stessa operazione, "bordi" diversi a seconda della scala.</p>
""")

s(44, "Higher-Order Gaussian Derivatives", """
<ul>
<li>Derivata n-esima 1D della gaussiana:</li>
</ul>
<span class="f">g<sub>σ</sub><sup>(n)</sup>(x) = H<sub>n</sub>(x/σ) · g<sub>σ</sub>(x)</span>
<ul>
<li style="list-style:none">con H<sub>n</sub> un <b>polinomio di Hermite</b> (a meno di un fattore di scala).</li>
<li>Derivata seconda:</li>
</ul>
<span class="f">g″<sub>σ</sub>(x) = (x²/σ⁴ − 1/σ²) · g<sub>σ</sub>(x)</span>
<ul>
<li>Derivate 2D <b>separabili</b>: prodotti di kernel 1D di derivata e di smoothing, per esempio</li>
</ul>
<span class="f">∂<sub>xx</sub>g<sub>σ</sub>(x, y) = g″<sub>σ</sub>(x) g<sub>σ</sub>(y),   ∂<sub>xy</sub>g<sub>σ</sub>(x, y) = g′<sub>σ</sub>(x) g′<sub>σ</sub>(y)</span>
<p>Formano un <b>banco di filtri</b> sistematico ("Gaussian derivative filter bank"): l'insieme completo delle misure di struttura locale a una data scala (come una serie di Taylor locale dell'immagine sfocata).</p>
<div class="box k"><b>Da saper fare</b><p>Derivando −(x/σ²)g: −(1/σ²)g + (x²/σ⁴)g. La formula della slide è corretta. Il fattore esatto è g<sub>σ</sub><sup>(n)</sup> = (−1/σ)<sup>n</sup> He<sub>n</sub>(x/σ) g<sub>σ</sub>, con He<sub>2</sub>(u) = u² − 1.</p></div>
<div class="box b"><b>Dal libro · cap. 18, § 18.6 High-Order Gaussian Derivatives</b><p>Il libro dà la formula esatta con i polinomi di Hermite "dei fisici" H<sub>n</sub>:</p>
<span class="f">g<sub>x<sup>n</sup></sub>(x; σ) = (−1/(σ√2))<sup>n</sup> H<sub>n</sub>(x/(σ√2)) g(x; σ)</span>
<p>con H<sub>0</sub> = 1, H<sub>1</sub>(x) = 2x, H<sub>2</sub>(x) = 4x² − 2 e la ricorsione H<sub>n</sub>(x) = 2x H<sub>n−1</sub>(x) − 2(n−1) H<sub>n−2</sub>(x). In 2D il kernel di ordine (n, m) è il prodotto delle due versioni 1D per g(x, y; σ): tutte separabili.</p>
<p>Verifica per n = 2: (1/(2σ²)) · (4x²/(2σ²) − 2) = x²/σ⁴ − 1/σ², la formula della slide. La slide scrive H<sub>n</sub>(x/σ) senza fattore: corrisponde agli Hermite "dei probabilisti" He<sub>n</sub> (vedi riquadro sopra), stessa famiglia con normalizzazione diversa.</p><p><a href="https://visionbook.mit.edu/derivatives.html" target="_blank">Leggi nel libro</a></p></div>
""")

s(45, "Higher-Order Gaussian Derivatives", """
<p><b>Figura:</b> "triangolo" dei kernel gaussiani 2D fino all'ordine 6: in cima g, poi g<sub>x</sub> e g<sub>y</sub>, poi g<sub>x²</sub>, g<sub>xy</sub>, g<sub>y²</sub>, e così via.</p>
<ul>
<li>Ogni riga è un ordine di derivazione; la riga n ha n + 1 kernel.</li>
<li>Più alto è l'ordine, più lobi alternati bianchi e neri: il kernel risponde a oscillazioni più rapide nella sua direzione.</li>
</ul>
""")

s(46, "Derivatives Using Binomial Filters: Sobel", """
<ul>
<li>Come i binomiali approssimano la gaussiana, <b>differenze di binomiali</b> approssimano le derivate di gaussiana.</li>
<li>L'<b>operatore di Sobel–Feldman</b> compone in modo separabile uno smoothing binomiale [1, 2, 1] in una direzione e la derivata [1, 0, −1] nell'altra:</li>
</ul>
<span class="f">S<sub>x</sub> = [1, 2, 1]<sup>T</sup> ∗ [1, 0, −1]</span>
<p>La slide lo scrive come la matrice 3×3 con righe (−1 0 1), (−2 0 2), (−1 0 1).</p>
<div class="box w"><b>Attenzione: segno della matrice</b><p>Il prodotto [1, 2, 1]<sup>T</sup> ∗ [1, 0, −1] dà righe (1 0 −1), (2 0 −2), (1 0 −1): l'<b>opposto</b> della matrice sulla slide. La matrice della slide è la stessa scritta come <i>maschera di correlazione</i> (kernel ribaltato), che è la forma in cui Sobel si trova di solito in OpenCV e in molti testi. Il visionbook (§ 18.7) invece scrive Sobel<sub>x</sub> = [1, 0, −1] ∘ [1, 2, 1]<sup>T</sup> con prima riga (1 0 −1), cioè il prodotto: conferma che la matrice della slide ha il segno opposto. Le due forme calcolano la stessa derivata (positiva quando l'intensità cresce verso destra) solo se si usa la convoluzione con la prima e la correlazione con la seconda.</p></div>
<div class="box k"><b>Da capire</b><p>[1, 0, −1] = [1, 1] ∗ [1, −1]: una differenza d<sub>0</sub> seguita da uno smoothing binomiale b<sub>1</sub>. Quindi Sobel = "binomiale in entrambe le direzioni + d<sub>0</sub> in una", l'analogo discreto di una derivata di gaussiana piccola. Sobel è d<sub>1</sub> (a meno del fattore ½) sulle righe, b<sub>2</sub> (a meno di ¼) sulle colonne.</p></div>
""")

s(47, "Image Gradient and Directional Derivatives", """
<ul>
<li><b>Vettore gradiente</b>: due immagini di derivate.</li>
</ul>
<span class="f">∇ℓ(x, y) = (∂ℓ/∂x, ∂ℓ/∂y)</span>
<ul>
<li>Con le derivate di gaussiana: ∇ℓ ∗ g = ∇g ∗ ℓ = (g<sub>x</sub>, g<sub>y</sub>) ∗ ℓ.</li>
<li><b>Derivata direzionale</b> lungo il versore t = (cos θ, sin θ): è una <b>combinazione lineare</b> delle due derivate:</li>
</ul>
<span class="f">(∂ℓ/∂t) ∗ g = cos θ · (g<sub>x</sub> ∗ ℓ) + sin θ · (g<sub>y</sub> ∗ ℓ)</span>
<div class="box k"><b>Da capire</b><p>Bastano <b>due</b> convoluzioni per avere la derivata in <b>qualunque</b> direzione: è il prodotto scalare ∇ℓ · t. Questa proprietà (filtri orientabili, <i>steerable filters</i>) è ciò che rende economico costruire detector di orientazione. Il massimo su θ si ha nella direzione del gradiente e vale |∇ℓ|.</p></div>
<div class="box b"><b>Dal libro · cap. 18, § 18.8 Image Gradient and Directional Derivatives</b><p>Il libro sottolinea che la combinazione lineare vale anche per i <b>kernel discreti</b>: dati due kernel di derivata lungo n e lungo m,</p>
<span class="f">d<sub>θ</sub>[n, m] = cos θ · d<sub>n</sub>[n, m] + sin θ · d<sub>m</sub>[n, m]</span>
<p>è il kernel della derivata a angolo θ (è così che si ottiene la colonna "45°" della figura alla slide 48). Il libro non scrive modulo e angolo: sono le formule standard |∇ℓ| = √(ℓ<sub>x</sub>² + ℓ<sub>y</sub>²) e θ = atan2(ℓ<sub>y</sub>, ℓ<sub>x</sub>), usate nelle ultime due colonne della figura.</p><p><a href="https://visionbook.mit.edu/derivatives.html" target="_blank">Leggi nel libro</a></p></div>
""")

s(48, "Example: Sobel", """
<p><b>Figura:</b> un disco bianco su fondo nero, I[n, m]. Tre righe (Sobel, d<sub>0</sub>, d<sub>1</sub>) e cinque colonne: derivata lungo n, lungo m, a 45°, modulo quadro del gradiente |∇I|², angolo del gradiente (in colore).</p>
<ul>
<li>Con Sobel il modulo è quasi uniforme lungo tutto il bordo del cerchio: è il più <b>invariante alla rotazione</b>.</li>
<li>Con d<sub>0</sub> e d<sub>1</sub> il modulo varia con l'orientazione del bordo (più debole o frastagliato su alcune diagonali).</li>
<li>Prezzo di Sobel: il risultato è <b>più sfocato</b>.</li>
</ul>
<p>(La didascalia cita anche una "vera" derivata di gaussiana, che nella figura non compare.)</p>
""")

s(49, "Frequency Response: Sobel", """
<p><b>Figura:</b> modulo della risposta in frequenza 2D di (a) d<sub>0</sub>, (b) d<sub>1</sub>, (c) operatore di Roberts (differenze in diagonale), (d) Sobel–Feldman.</p>
<ul>
<li>d<sub>0</sub>: una "V" lungo u, che cresce fino al bordo della banda.</li>
<li>d<sub>1</sub>: sale e ridiscende a zero alla frequenza massima.</li>
<li><b>Sobel</b>: come d<sub>1</sub> lungo u, ma <b>smorzato lungo v</b> dal binomiale: due gobbe localizzate alle frequenze medio-basse. Risponde a variazioni orizzontali e ignora il rumore ad alta frequenza.</li>
</ul>
<div class="box x"><b>Approfondimento</b><p>La trasformata di Sobel è il prodotto delle due 1D: |S<sub>x</sub>(u, v)| ∝ |sin u| · cos²(v/2). Il fattore cos²(v/2) è lo smoothing binomiale in direzione ortogonale.</p></div>
<div class="box b"><b>Dal libro · cap. 18, § 18.7 Derivatives using Binomial Filters</b><p>Il libro scrive la DFT di Sobel come prodotto delle due 1D:</p>
<span class="f">Sobel<sub>x</sub>[u, v] = D<sub>1</sub>[u] B<sub>2</sub>[v] = j sin(2πu/N) (2 + 2 cos(2πv/N))</span>
<p>(a meno del fattore 2 dovuto al fatto che [1, 0, −1] è 2d<sub>1</sub>). Lungo u si comporta come d<sub>1</sub>, lungo v il binomiale B<sub>2</sub> si annulla alla frequenza più alta: è l'origine delle due "gobbe" della figura (d). Conclusione del libro sulla figura del disco: Sobel dà il modulo del gradiente più invariante alla rotazione, ma è più sfocato.</p><p><a href="https://visionbook.mit.edu/derivatives.html" target="_blank">Leggi nel libro</a></p></div>
""")

s(50, "Gradient Field: Example", """
<p><b>Figura:</b> l'astronauta, il modulo del gradiente |∇I| (bianco sui contorni) e l'orientazione del gradiente (frecce rosse).</p>
<ul>
<li><b>Modulo alto</b>: bordi e contorni.</li>
<li>L'<b>orientazione è perpendicolare al bordo</b> (punta verso il lato più chiaro): è l'indizio usato da alcuni descrittori (istogrammi di orientazione di SIFT e HOG, L7).</li>
<li>Conseguenza: con le derivate direzionali si costruiscono <b>detector di orientazione</b>.</li>
</ul>
""")

s(51, "The Image Laplacian", """
<ul>
<li>Le derivate dipendono dalla direzione: per estrarre feature può servirne più d'una, a orientazioni diverse.</li>
<li>Il <b>laplaciano</b> è un operatore del <b>secondo ordine</b> e <b>invariante alla rotazione</b>:</li>
</ul>
<span class="f">∇²ℓ = ∂²ℓ/∂x² + ∂²ℓ/∂y²</span>
<ul>
<li>Come la derivata, è <b>sensibile al rumore</b> (anche di più: guadagno |ω|² in frequenza), quindi va sfocato.</li>
</ul>
<div class="box x"><b>Approfondimento</b><p>Invarianza alla rotazione: ∇²ℓ è la traccia della matrice hessiana, e la traccia non cambia ruotando gli assi. In frequenza il laplaciano moltiplica per −(u² + v²), che dipende solo dal raggio.</p></div>
""")

s(52, "Laplacian of Gaussian (LoG)", """
<ul>
<li>Combina smoothing gaussiano e laplaciano, sempre grazie alla commutatività:</li>
</ul>
<span class="f">(∇²ℓ) ∗ g<sub>σ</sub> = (∇²g<sub>σ</sub>) ∗ ℓ</span>
<ul>
<li><b>LoG<sub>σ</sub> = ∇²g<sub>σ</sub></b>: kernel a forma di "cappello messicano" (rovesciato).</li>
<li>Dipende dalla scala tramite σ.</li>
</ul>
<p><b>Figura:</b> il LoG in 3D e la sua sezione ∇²g(x, 0) per σ = 1: minimo di circa −0.32 al centro, un anello leggermente positivo intorno, somma zero.</p>
<div class="box k"><b>Da saper ricavare</b><p>Per la gaussiana 2D normalizzata:</p>
<span class="f">∇²g<sub>σ</sub> = ((x² + y²)/σ⁴ − 2/σ²) · g<sub>σ</sub></span>
<p>Al centro vale −2/σ² · 1/(2πσ²); per σ = 1: −1/π ≈ −0.318, come nella figura. Si annulla sul cerchio x² + y² = 2σ².</p></div>
<div class="box x"><b>Approfondimento</b><p>Il "cappello messicano" propriamente è −∇²g (picco positivo al centro). Il LoG della figura è rovesciato: negativo al centro.</p></div>
<div class="box b"><b>Dal libro · cap. 18, § 18.9 Image Laplacian</b><p>Il libro scrive il LoG come</p>
<span class="f">∇²g = ((x² + y² − 2σ²)/σ⁴) · g(x, y; σ)</span>
<p>(uguale alla formula del riquadro sopra, con 2σ² portato nel numeratore). Usi indicati dal libro: le <b>piramidi laplaciane</b> (rappresentazioni multiscala, L6) e la <b>rilevazione di keypoint</b> in SIFT (L7–L8), dove il LoG è approssimato da differenze di gaussiane.</p><p><a href="https://visionbook.mit.edu/derivatives.html" target="_blank">Leggi nel libro</a></p></div>
""")

s(53, "LoG - Frequency Response", """
<p>Per σ &gt; 1 il LoG è un <b>passa-banda</b>.</p>
<p><b>Figura:</b> modulo della DFT del LoG per (a) σ = ½, (b) σ = 1, (c) σ = 2, e (d) della approssimazione discreta a 5 punti:</p>
<span class="f">∇²<sub>5</sub> = [[0, 1, 0], [1, −4, 1], [0, 1, 0]]</span>
<ul>
<li>(a) e (d) crescono fino al bordo della banda: di fatto sono <b>passa-alto</b>.</li>
<li>(b) e (c): un anello, zero in DC e zero alle alte frequenze: <b>passa-banda</b>, sempre più stretto e più basso in frequenza al crescere di σ.</li>
</ul>
<div class="box x"><b>Approfondimento</b><p>Nel continuo la trasformata è −(u² + v²)·exp(−σ²(u² + v²)/2): è un passa-banda per <b>ogni</b> σ &gt; 0. La soglia σ &gt; 1 della slide è una regola pratica del caso discreto: con σ piccolo il picco cadrebbe oltre la frequenza di Nyquist (circa √2/σ), quindi sulla griglia si vede solo la parte crescente.</p></div>
""")

s(54, "Discrete Laplacian Approximation: 1D", """
<ul>
<li>In 1D il laplaciano (derivata seconda) si approssima con <b>[1, −2, 1]</b>.</li>
<li>Si ottiene come d<sub>0</sub> ∗ d<sub>0</sub> = [1, −1] ∗ [1, −1].</li>
</ul>
<div class="box k"><b>Da capire</b><p>Due shift di mezzo campione, uno per ciascun d<sub>0</sub>, si sommano in uno shift di un campione intero: basta centrare il kernel e diventa simmetrico, senza shift. La sua risposta in frequenza è −4 sin²(ω/2), che vicino a 0 vale circa −ω², come la derivata seconda ideale.</p></div>
<div class="box b"><b>Dal libro · cap. 18, § 18.9 Image Laplacian</b><p>Il libro costruisce il laplaciano discreto esattamente così: in 1D [1, −2, 1] = [1, −1] ∗ [1, −1], e in 2D la formula a 5 punti somma le due derivate seconde,</p>
<span class="f">∇²<sub>5</sub>ℓ[n, m] = −4ℓ[n, m] + ℓ[n+1, m] + ℓ[n−1, m] + ℓ[n, m+1] + ℓ[n, m−1]</span>
<p>L'invarianza alla rotazione del laplaciano continuo, nel discreto, vale solo in modo <b>approssimato</b>: ∇²<sub>5</sub> guarda solo i 4 vicini lungo gli assi.</p><p><a href="https://visionbook.mit.edu/derivatives.html" target="_blank">Leggi nel libro</a></p></div>
""")

s(55, "Discrete Laplacian Approximation: 2D", """
<ul>
<li>Approssimazione discreta a <b>5 punti</b>:</li>
</ul>
<span class="f">∇²ℓ[m, n] ≈ ℓ[m+1, n] + ℓ[m−1, n] + ℓ[m, n+1] + ℓ[m, n−1] − 4ℓ[m, n]</span>
<span class="f">∇²<sub>5</sub> = [[0, 1, 0], [1, −4, 1], [0, 1, 0]]</span>
<ul>
<li>Misura la <b>curvatura</b> locale: <b>positivo</b> in una zona scura circondata da zone chiare, <b>negativo</b> in una chiara circondata da scure, circa <b>0</b> nelle zone piatte o a rampa lineare.</li>
<li>È <b>separabile per somma</b>: si applica [1, −2, 1] lungo x, lo si applica lungo y e si sommano i due risultati.</li>
</ul>
<div class="box k"><b>Da saper verificare</b><p>Pixel scuro (0) con quattro vicini chiari (1): 1+1+1+1 − 0 = 4 &gt; 0. Rampa ℓ = a·m: (a(m+1) + a(m−1) − 2am) = 0. Attenzione: "separabile per somma" non è la separabilità a prodotto della gaussiana (kernel 2D = prodotto esterno di due 1D).</p></div>
""")

s(56, "Example", """
<p><b>Figura:</b> (a) una ruota con cerchione a raggi; (b) derivata seconda lungo x; (c) derivata seconda lungo y; (d) laplaciano, cioè la somma di (b) e (c).</p>
<p>Rispetto alle derivate prime, il laplaciano:</p>
<ul>
<li>è <b>invariante alla rotazione</b>: in (d) i raggi rispondono allo stesso modo qualunque sia la loro direzione, in (b) e (c) no;</li>
<li><b>misura la curvatura</b>: su una rampa lineare la derivata prima è diversa da zero anche senza bordi, il laplaciano è zero;</li>
<li>i bordi si possono localizzare come <b>zero-crossing</b> del laplaciano (non molto affidabili, anche per il rumore);</li>
<li>gli zero-crossing formano <b>contorni chiusi</b>.</li>
</ul>
""")

s(57, "LoG vs Derivative", """
<p><b>Figura:</b> (a) lo stesso segnale a gradino della slide 28; (b) d<sub>1</sub>; (c) ℓ ∘ d<sub>1</sub>, picchi sui bordi; (d) d<sub>0</sub> ∘ d<sub>0</sub> = [1, −2, 1]; (e) ℓ ∘ d<sub>0</sub>², una coppia +/− su ogni bordo.</p>
<p>Gli <b>zero-crossing della derivata seconda</b> cadono dove la derivata prima ha il <b>massimo</b> (in modulo). Sono due modi di trovare lo stesso bordo.</p>
<p>(Nella didascalia "LoR" è un refuso per LoG.)</p>
""")

s(58, "Summary", """
<ul>
<li>Le derivate evidenziano <b>bordi e struttura</b>.</li>
<li>Le derivate sono detector <b>orientati</b>.</li>
<li>Il rumore richiede un blur, e il blur introduce un <b>parametro di scala</b>.</li>
<li>Il <b>LoG</b> è una rappresentazione invariante alla rotazione.
<ul>
<li>Non è necessariamente migliore: è un'altra rappresentazione, con i suoi compromessi.</li>
<li>Tornerà nelle rappresentazioni multiscala (L6) e in SIFT (L7), dove la DoG ne è l'approssimazione.</li>
</ul></li>
</ul>
""")

s(59, "Early Visual System", "<p>Perché questi filtri assomigliano a ciò che fa il nostro occhio.</p>", kind="div", sec=("l5-visivo", "Sistema visivo", "slide 59–63"))

s(60, "Early Visual System", """
<ul>
<li>Il <b>sistema visivo precoce</b> (<i>early visual system</i>) è la parte "percettiva" del cervello, dall'occhio alla corteccia visiva primaria (V1): fa l'elaborazione di base dell'immagine.</li>
<li>Per motivare i filtri visti se ne mostra il legame con il <b>LoG</b>.</li>
</ul>
""")

s(61, "Early Visual System Model", """
<ul>
<li>La sensibilità al contrasto umana si modella bene combinando un <b>laplaciano</b> (esalta i bordi) e una <b>gaussiana</b> (smoothing):</li>
</ul>
<span class="f">h = −∇²g<sub>σ</sub> + λ g<sub>σ</sub></span>
<p><b>Figura:</b> il kernel h, un picco positivo al centro circondato da un anello negativo poco profondo (struttura centro-periferia).</p>
<ul>
<li>La sua risposta in frequenza ha un <b>picco a frequenze spaziali intermedie</b> e ricalca la <b>funzione di sensibilità al contrasto</b> (CSF) misurata sperimentalmente.</li>
</ul>
<div class="box x"><b>Approfondimento</b><p>In frequenza: H(ω) = (|ω|² + λ)·exp(−σ²|ω|²/2). Il termine λ dà un guadagno DC diverso da zero (vediamo anche le zone uniformi), il termine |ω|² fa salire la curva, l'esponenziale la fa scendere. Il profilo centro-periferia ricorda i campi recettivi delle cellule gangliari della retina.</p></div>
<div class="box b"><b>Dal libro · cap. 18, § 18.10 A Simple Model of the Early Visual System</b><ul><li>Nel libro λ è una piccola costante che dà al filtro un <b>guadagno DC non nullo</b>; nelle figure i parametri sono <b>λ = 2 e σ = 5</b>.</li>
<li>Il libro non sostiene che il cervello calcoli un LoG: dice che la trasformata di h ha una forma <b>qualitativamente simile</b> alla funzione di sensibilità al contrasto umana. È un modello minimo, non un modello fisiologico.</li>
<li>Con lo stesso h il libro spiega le illusioni di Vasarely (slide 63): l'uscita del filtro mostra le diagonali che percepiamo.</li></ul><p><a href="https://visionbook.mit.edu/derivatives.html" target="_blank">Leggi nel libro</a></p></div>
""")

s(62, "Contrast Sensitivity Function (Campbell and Robson)", """
<ul>
<li>Nell'immagine di Campbell e Robson la <b>frequenza</b> delle onde cresce da sinistra a destra, il <b>contrasto</b> (ampiezza) cambia in verticale ma è costante lungo ogni riga orizzontale.</li>
<li>Eppure vediamo le onde fino a un'altezza maggiore al centro che agli estremi: il confine percepito è una curva a campana. È un'illusione dovuta alla sensibilità al contrasto del sistema visivo.</li>
<li>La FFT di h = −∇²g<sub>σ</sub> + λg<sub>σ</sub> riproduce bene questa percezione.</li>
</ul>
<p><b>Figura:</b> a sinistra la carta di Campbell-Robson; a destra il guadagno di h in funzione della frequenza: parte da un "DC gain" non nullo, sale a un picco a frequenza media, poi scende a zero.</p>
""")

s(63, "Vasarely Illusion", """
<ul>
<li>Le <b>illusioni di Vasarely</b> sono fatte di quadrati concentrici a tinta uniforme. Le diagonali chiare (o scure) che si vedono sono un'illusione: aloni di luminosità ai bordi fra tinte piatte, effetto collaterale del <b>filtraggio passa-banda</b> del sistema visivo.</li>
<li>Filtrando l'immagine con h = −∇²g<sub>σ</sub> + λg<sub>σ</sub>, il risultato ℓ ∗ h mostra proprio le diagonali che percepiamo.</li>
</ul>
<p><b>Figura:</b> in alto quadrati concentrici con centro chiaro, il risultato del filtro con una X chiara e un profilo in cui compaiono i picchi (overshoot) ai bordi; in basso lo stesso con centro scuro e X scura.</p>
<div class="box w"><b>Attenzione: lettere delle sottofigure</b><p>Il testo indica le illusioni come (a), (c) e i risultati filtrati come (b), (d). Nella figura le etichette sono per righe: illusioni (a) e (d), risultati filtrati (b) ed (e), profili (c) e (f). È anche la numerazione della figura 18.22 del libro (§ 18.10).</p></div>
""")

s(64, "Sharpening", "<p>Usare il blur al contrario: esaltare le alte frequenze.</p>", kind="div", sec=("l5-sharp", "Sharpening", "slide 64–68"))

s(65, "Sharpening Filter", """
<ul>
<li>Idea: esaltare le alte frequenze <b>sottraendo una copia sfocata</b>:</li>
</ul>
<span class="f">ℓ<sub>sharp</sub> = 2ℓ − (g<sub>σ</sub> ∗ ℓ) = ℓ + (ℓ − g<sub>σ</sub> ∗ ℓ)</span>
<ul>
<li>(ℓ − g<sub>σ</sub> ∗ ℓ) è una versione <b>passa-alto</b> di ℓ; sommarla all'originale amplifica bordi e texture.</li>
<li>Equivale a convolvere con <b>h = 2δ − g<sub>σ</sub></b>, con risposta in frequenza <b>2 − ĝ<sub>σ</sub>(ω)</b>: vale 1 in DC (luminosità media invariata) e tende a 2 alle alte frequenze.</li>
<li>Applicato più volte aumenta la nitidezza, ma alla fine amplifica anche <b>rumore e ringing</b>.</li>
</ul>
<div class="box x"><b>Approfondimento</b><p>È l'<b>unsharp masking</b> della fotografia. La forma generale è ℓ + α(ℓ − g<sub>σ</sub> ∗ ℓ), con α che regola l'intensità. Poiché ℓ − g<sub>σ</sub> ∗ ℓ ≈ −(σ²/2)∇²ℓ per σ piccolo, fare sharpening equivale circa a sottrarre un laplaciano.</p></div>
<div class="box b"><b>Dal libro · cap. 18, § 18.11 Sharpening Filter</b><p>Il libro presenta lo sharpening come il modo più semplice per <b>attenuare le componenti sfocate</b> dell'immagine: si toglie una copia sfocata (con il binomiale 3×3) da due volte l'originale, e il kernel risultante ha guadagno DC 1, quindi non cambia la luminosità media. Nella figura con la barca (slide 68) lo stesso filtro è applicato da 1 a 5 volte di seguito. Il libro non usa il termine "unsharp masking" e non discute la risposta in frequenza: la formula 2 − ĝ<sub>σ</sub> qui sopra è un conto nostro (vale per la versione con la gaussiana).</p><p><a href="https://visionbook.mit.edu/derivatives.html" target="_blank">Leggi nel libro</a></p></div>
""")

s(66, "Sharpening kernel", """
<p>Versione discreta con il binomiale 3×3 come blur:</p>
<span class="f">h = [[0, 0, 0], [0, 2, 0], [0, 0, 0]] − (1/16) · [[1, 2, 1], [2, 4, 2], [1, 2, 1]]</span>
<div class="box k"><b>Da saper fare</b><p>Il risultato ha 2 − 4/16 = 1.75 al centro, −2/16 sui quattro vicini laterali, −1/16 sui diagonali. Somma: 2 − 1 = 1, quindi la luminosità media resta invariata.</p></div>
""")

s(67, "Example 1", """
<p><b>Figura:</b> l'astronauta originale, sfocato con gaussiana σ = 2, e il risultato 2ℓ − ℓ<sub>blur</sub>.</p>
<p>L'immagine sharpened ha contorni e texture più marcati; attorno ai bordi forti (bandiera, casco) compaiono leggeri aloni: l'overshoot tipico di questo filtro.</p>
""")

s(68, "Example 2", """
<p><b>Figura:</b> una barca a vela con sharpening applicato ripetutamente, da (a) a (f). <a href="https://visionbook.mit.edu/derivatives.html#sharpening-filter">Vision Book, sharpening filter</a></p>
<p>A ogni iterazione i dettagli (numero sulla vela, bordi) diventano più incisi, ma crescono anche il rumore e gli aloni: il guadagno alle alte frequenze si moltiplica a ogni applicazione.</p>
""")

s(69, "Conclusions", "<p>Chiusura della lezione.</p>", kind="div")

s(70, "Key Takeaways", """
<ul>
<li>I filtri di <b>blur</b> (box, gaussiano, binomiale) sono tutti <b>passa-basso</b>.
<ul>
<li>Tolgono il rumore e permettono di evidenziare feature a scale diverse.</li>
<li>Gaussiano e binomiale hanno risposte in frequenza lisce e monotone (niente ringing), il box no.</li>
<li>La gaussiana ha proprietà comode: separabile, trasformata di Fourier gaussiana, varianze che si sommano sotto convoluzione.</li>
</ul></li>
<li><b>Gradienti</b>: quasi tutta la struttura dell'immagine (tranne la media) sta nei gradienti; lo si sfrutta per editing e inpainting.
<ul>
<li>Per ridurre il rumore, le <b>derivate di gaussiana</b> uniscono smoothing e derivazione a una scala σ scelta.</li>
<li>Il <b>LoG</b> dà detector di bordi invarianti alla rotazione.</li>
</ul></li>
</ul>
""")

s(71, "References", """
<p><a href="https://visionbook.mit.edu/series.html">MIT Vision Book</a>, cap. 17 (Blur Filters) e cap. 18 (Image Derivatives). Quasi tutte le figure della lezione vengono da lì.</p>
""")

s(72, "Preview", """
<ul>
<li>Ora abbiamo filtri con una scala e possiamo estrarre diverse feature utili.</li>
<li>Abbiamo invarianza alla rotazione, ma solo per alcuni filtri (laplaciano, LoG).</li>
</ul>
<p><b>Lezione 6</b> aggiungerà:</p>
<ul>
<li><b>invarianza alla rotazione</b>: banchi di filtri a più orientazioni;</li>
<li><b>scale-space</b>: piramidi di immagini per rappresentazioni multiscala;</li>
<li>i problemi di <b>campionamento e aliasing</b>.</li>
</ul>
<div class="box w"><b>Attenzione: "scale-invariant filters"</b><p>La slide dice "we now have scale-invariant filters". È in contraddizione con la slide 42 ("Derivatives are not scale-invariant!"): i filtri visti hanno un <b>parametro di scala</b> σ, cioè si possono regolare su una scala, ma non sono invarianti. L'invarianza alla scala si ottiene solo con le rappresentazioni multiscala di L6.</p></div>
""")
