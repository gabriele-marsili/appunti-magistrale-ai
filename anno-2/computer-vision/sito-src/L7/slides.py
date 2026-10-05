NB1 = 'NOTEBOOK demo.ipynb · '
NB2 = 'NOTEBOOK filter_bank.ipynb · '
NB3 = 'NOTEBOOK 06-image-blending · '
FOU = '<a href="https://visionbook.mit.edu/image_processing_fourier.html">cap. 16</a>'
FB = '<a href="https://visionbook.mit.edu/spatial_filter_sets.html">cap. 22</a>'
CNN = '<a href="https://visionbook.mit.edu/convolutional_neural_nets.html">cap. 24</a>'

# ---------------------------------------------------------------- demo.ipynb

s(1, "Fourier and Convolution for Images: obiettivi e setup", """
<p>Primo notebook: gli strumenti della L3 e della L4 (DFT, teorema di convoluzione, filtri in frequenza) passano dall'audio 1D alle <b>immagini 2D</b>. Obiettivi dichiarati: saper <b>leggere uno spettro</b> e implementare e verificare semplici filtri.</p>
<pre>image = img_as_float(data.camera())[96:352, 128:384]   # 256×256, valori in [0, 1]
H, W = image.shape
y, x = np.indices(image.shape)          # coordinate di riga e colonna
FX, FY = frequency_grid(image.shape)    # frequenze in cicli/pixel, ordine FFT
radius = np.hypot(FX, FY)               # distanza dall'origine nello spettro</pre>
<ul>
<li>L'immagine è il "cameraman" di scikit-image, ritagliato a <b>256 × 256</b> e convertito in float in [0, 1].</li>
<li>Tre funzioni di supporto: <code>panels</code> (immagini affiancate; con <code>signed=True</code> usa una mappa rosso/blu simmetrica attorno a 0), <code>frequency_grid</code> (le griglie di frequenza, scheda 2) e <code>spectrum</code> (log del modulo, centrato).</li>
<li><code>spectrum</code> mostra <b>log(1 + |F|)</b> dopo <code>fftshift</code>: la dinamica di uno spettro è enorme e in scala lineare si vedrebbe solo la componente continua (come in L4). L'argomento <code>extent</code> mette sugli assi le frequenze vere in cicli/pixel, da −0.5 a 0.5.</li>
<li><code>radius</code> = |f| servirà per tutte le maschere <b>isotrope</b> (che dipendono solo dalla distanza dall'origine, non dalla direzione).</li>
</ul>
""", sec=("l7-demo", "demo.ipynb · Fourier e filtri sulle immagini", 'schede 1–13'), printed=NB1 + 'celle 1–2')

s(2, "La griglia delle frequenze: FX, FY e l'ordine della FFT", """
<pre>def frequency_grid(shape):
    fy = np.fft.fftfreq(shape[0])
    fx = np.fft.fftfreq(shape[1])
    return np.meshgrid(fx, fy)          # FX varia lungo le colonne, FY lungo le righe</pre>
<p><b>Figura</b> (griglia 10 × 10): <code>FX</code> a strisce verticali, <code>FY</code> a strisce orizzontali, e FX² + FY² con il massimo <b>al centro</b> e i minimi agli angoli.</p>
<ul>
<li><code>fftfreq(10)</code> = [0, 0.1, 0.2, 0.3, 0.4, −0.5, −0.4, −0.3, −0.2, −0.1]: prima la DC, poi le positive, poi le <b>negative</b>. È l'ordine in cui <code>fft2</code> restituisce i coefficienti.</li>
<li>Per questo nella terza figura la frequenza più alta (±0.5, Nyquist) è in mezzo e le basse sono ai quattro angoli: gli angoli sono tutti vicini a f = 0 perché lo spettro è <b>periodico</b>.</li>
<li><code>fftshift</code> riordina in modo da avere f = 0 al centro, utile per guardare; <code>ifftshift</code> lo annulla. Una maschera costruita su <code>frequency_grid</code> è già nell'ordine giusto e si moltiplica direttamente per <code>fft2(img)</code>, senza shift.</li>
<li><code>meshgrid(fx, fy)</code> restituisce array con la forma dell'immagine (righe = y), quindi <code>FX[r, c]</code> è la frequenza orizzontale del coefficiente <code>F[r, c]</code>.</li>
</ul>
<div class="box w"><b>Attenzione: una figura vuota</b><p>La cella chiama <code>plt.figure()</code> prima di <code>plt.matshow(FY)</code>, ma <code>matshow</code> apre già una figura sua: nell'output resta un <code>&lt;Figure ... with 0 Axes&gt;</code>. Innocuo; basta togliere <code>plt.figure()</code>.</p></div>
""", img='img/demo_grid.png', printed=NB1 + 'cella 3')

s(3, "Prevedere lo spettro di un'onda", """
<pre>gratings = [(12, 0), (0, 12), (12, 8)]  # (kx, ky)
g = np.cos(2*np.pi*(kx*x/W + ky*y/H))
G = np.fft.fft2(g)
assert np.isclose(abs(G[ky % H, kx % W]), H*W/2)</pre>
<p><b>Figura:</b> sopra tre reticoli: strisce verticali (kx = 12), orizzontali (ky = 12) e oblique (12, 8). Sotto gli spettri: due soli pixel accesi, così piccoli che a questa scala non si vedono; i cerchi ciano ne segnano la posizione, simmetrica rispetto al centro.</p>
<ul>
<li>cos(2π(k<sub>x</sub>x/W + k<sub>y</sub>y/H)) = ½ e<sup>+j…</sup> + ½ e<sup>−j…</sup>: due esponenziali complessi, cioè due <b>picchi coniugati</b> in ±(k<sub>y</sub>, k<sub>x</sub>), ciascuno di modulo <b>HW/2</b> = 32768 (verificato dall'<code>assert</code>).</li>
<li>k<sub>x</sub>, k<sub>y</sub> sono "quanti periodi interi" nell'immagine: in cicli/pixel la frequenza è (k<sub>x</sub>/W, k<sub>y</sub>/H) = (0.047, 0.031) per il reticolo obliquo.</li>
<li>Il vettore (k<sub>x</sub>/W, k<sub>y</sub>/H) è <b>perpendicolare alle strisce</b>: indica la direzione in cui l'intensità cambia. Strisce verticali ⇒ picchi sull'asse orizzontale.</li>
<li>L'indice <code>ky % H</code> converte una frequenza negativa nella posizione dell'array (ordine FFT, scheda 2).</li>
</ul>
<p><b>Esercizi del notebook</b>, con i risultati:</p>
<ul>
<li>Cambiare i valori in <code>gratings</code>: più k è grande, più le strisce sono fitte e più i picchi si allontanano dal centro; ruotando le strisce ruotano i picchi.</li>
<li><b>Frequenza non intera</b> (k<sub>x</sub> = 12.5): l'onda non chiude un numero intero di periodi nella "piastrella" periodica e l'energia si spalma: 256 bin sopra l'1% del massimo invece di 2, picco 21258 invece di 32768. È lo <b>spectral leakage</b> della L4.</li>
<li>Somma di onde: la FFT è lineare, lo spettro è la somma degli spettri (più coppie di picchi).</li>
</ul>
<div class="box b"><b>Dal libro · cap. 16, § 16.4.1 e § 16.6.2</b><p>Il libro scrive le onde 2D discrete come cos(2π(un/N + vm/M)) e mostra (fig. 16.4 e 16.9) che a ogni onda corrisponde una coppia di impulsi simmetrici nel piano (u, v). Il libro scrive la coppia trasformata con fattore ½; con la DFT non normalizzata dell'eq. 16.2, che è quella di <code>np.fft.fft2</code>, ogni picco vale <b>NM/2</b>, come verifica il notebook. Stessa idea, diversa normalizzazione. Vedi anche la fig. 16.16 ("Fourier matching game"): bordi orientati danno linee perpendicolari nello spettro, strutture ripetute danno impulsi. <a href="https://visionbook.mit.edu/image_processing_fourier.html">Link al capitolo</a>.</p></div>
""", img='img/demo_gratings.png', printed=NB1 + 'celle 4–6')

s(4, "DFT inversa, componente continua, Parseval", """
<pre>F = np.fft.fft2(image)
reconstructed = np.fft.ifft2(F).real
assert np.allclose(reconstructed, image, atol=1e-12)
assert np.isclose(F[0, 0].real / image.size, image.mean())
assert np.isclose(np.sum(image**2), np.sum(abs(F)**2)/image.size)</pre>
<p><b>Figura:</b> l'immagine e lo spettro log. Il massimo è al centro (DC e basse frequenze), il valore cala allontanandosi, e c'è una <b>croce</b> luminosa lungo i due assi. Errore massimo di ricostruzione 6.7·10<sup>−16</sup>.</p>
<ul>
<li><b>Invertibilità</b>: <code>ifft2(fft2(img))</code> restituisce l'immagine a meno dell'errore di macchina. La parte immaginaria è rumore numerico, per questo si prende <code>.real</code>.</li>
<li><b>DC</b>: F[0, 0] = ∑ f[y, x], quindi F[0, 0]/(HW) è la <b>media</b> dell'immagine (0.398).</li>
<li><b>Parseval</b>: l'energia si conserva a meno del fattore della convenzione di numpy:
<span class="f">∑ f[y,x]<sup>2</sup> = (1/HW) ∑ |F[v,u]|<sup>2</sup></span>
(16143.14 da entrambe le parti).</li>
<li>La <b>croce sugli assi</b> non è contenuto dell'immagine: la DFT tratta l'immagine come periodica, e il bordo sinistro (scuro) non combacia con il destro, né il superiore con l'inferiore. Il salto al bordo è un "bordo" verticale e orizzontale che dà energia lungo gli assi. Stesso fenomeno del leakage della L4.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 16, § 16.7.3 e § 16.9</b><p>Parseval (§ 16.7.3) vale anche per il prodotto scalare di due immagini, e l'energia totale è la stessa nei due domini a meno di 1/NM. Nel § 16.9 il libro osserva che lo spettro delle immagini naturali è molto simile da un'immagine all'altra: massimo nell'origine e decadimento con la frequenza radiale, approssimabile con A[u, v] ≈ a/(u<sup>2</sup> + v<sup>2</sup>)<sup>b</sup>. È quello che si vede qui, ed è il motivo per cui poche basse frequenze contengono quasi tutta l'energia (scheda 13). <a href="https://visionbook.mit.edu/image_processing_fourier.html">Link al capitolo</a>.</p></div>
""", img='img/demo_spectrum.png', printed=NB1 + 'celle 7–8')

s(5, "Modulo, fase e traslazione", """
<pre>dy, dx = 27, -19
shifted = np.roll(image, (dy, dx), axis=(0, 1))
phase_ramp = np.exp(-2j*np.pi*(FY*dy + FX*dx))
predicted = np.fft.ifft2(F * phase_ramp).real
assert np.allclose(predicted, shifted, atol=1e-12)
assert np.allclose(abs(np.fft.fft2(shifted)), abs(F), atol=1e-10)</pre>
<p><b>Figura:</b> originale, shift circolare di 27 pixel in basso e 19 a sinistra (la parte che esce rientra dal lato opposto: in alto si vede la fascia inferiore dell'immagine, a destra quella sinistra), e la stessa immagine ottenuta moltiplicando lo spettro per una rampa di fase. Le ultime due sono identiche.</p>
<ul>
<li><b>Teorema di traslazione</b>: spostare l'immagine moltiplica ogni coefficiente per un esponenziale complesso di modulo 1:
<span class="f">f[y−d<sub>y</sub>, x−d<sub>x</sub>] ⟷ F[v,u] · e<sup>−2πj(f<sub>y</sub>d<sub>y</sub> + f<sub>x</sub>d<sub>x</sub>)</sup></span></li>
<li>Il <b>modulo</b> non cambia, cambia solo la <b>fase</b>, di una quantità che cresce linearmente con la frequenza (una "rampa"). Quindi la posizione degli oggetti è scritta nella fase.</li>
<li>È lo stesso fatto della L3 in 1D, applicato asse per asse: l'esponenziale 2D è separabile.</li>
</ul>
<div class="box w"><b>Attenzione: vale solo per lo shift circolare</b><p>Il notebook dice "shifting an image only changes its phase". È esatto solo per <code>np.roll</code>, dove i pixel che escono rientrano dall'altro lato. Uno spostamento vero (la camera si muove, entrano pixel nuovi) cambia anche il modulo: ritagliando la stessa finestra 256 × 256 spostata di (27, −19) nell'immagine originale 512 × 512, il modulo dello spettro cambia del <b>22%</b> (norma relativa, verificato). Lo dice anche il libro.</p></div>
<div class="box b"><b>Dal libro · cap. 16, § 16.7.6 e § 16.9</b><p>Il § 16.7.6 dà la stessa proprietà e precisa che, per una traslazione dovuta al moto della camera, è solo un'approssimazione per via dei bordi; la fig. 16.12 stima lo spostamento dal rapporto fra i due spettri. Nel § 16.9 l'esperimento dello <b>scambio di fase</b> (fig. 16.14): ricostruendo con il modulo di un'immagine e la fase di un'altra, il risultato somiglia a quella che ha dato la fase. Per le immagini naturali la struttura sta soprattutto nella fase; per le texture periodiche invece conta molto anche il modulo (fig. 16.15). <a href="https://visionbook.mit.edu/image_processing_fourier.html">Link al capitolo</a>.</p></div>
""", img='img/demo_shift.png', printed=NB1 + 'celle 9–10')

s(6, "Condizioni al bordo: fill, wrap, symm", """
<pre>half_white_square = np.ones((16, 16)); half_white_square[:, 8:] = 0
kernel = gaussian_kernel(3)             # σ = 3, troncata a 3σ: 19×19
signal.convolve2d(half_white_square, kernel, mode="same", boundary=b)
#                                  b in "fill", "wrap", "symm"</pre>
<p><b>Figura:</b> un quadrato 16 × 16 bianco a sinistra e nero a destra, sfocato con tre estensioni diverse. <b>Zero</b>: bordi superiore, inferiore e sinistro scuriti, alone. <b>Periodica</b>: la colonna sinistra diventa grigia, perché "vede" il nero del lato destro. <b>Simmetrica</b>: il bianco resta bianco sul bordo, il nero nero; si sfoca solo la transizione centrale.</p>
<ul>
<li><b>fill</b> (zeri fuori): scurisce i bordi, perché la media include pixel neri inesistenti. Angolo bianco (0, 0): 0.318.</li>
<li><b>wrap</b> (periodica): unisce i lati opposti; qui crea una seconda transizione falsa sul bordo. Angolo: 0.563.</li>
<li><b>symm</b> (specchio, ripetendo il pixel di bordo: [1, 2, 3] → 2, 1, <b>1, 2, 3</b>, 3, 2): la più neutra per immagini naturali. Angolo: 0.993.</li>
<li><code>mode="same"</code> decide solo la <b>dimensione</b> dell'uscita, <code>boundary</code> come si estende l'immagine: sono due scelte diverse.</li>
<li>Il kernel 19 × 19 è più grande dell'immagine 16 × 16: è un esempio estremo, fatto apposta perché ogni pixel risenta del bordo.</li>
</ul>
<div class="box k"><b>Da saper spiegare</b><p>Filtrare moltiplicando nello spettro (<code>ifft2(F * mask)</code>) equivale a <b>boundary="wrap"</b>: il teorema di convoluzione della DFT vale per la convoluzione <b>circolare</b>, perché la DFT tratta l'immagine come periodica (§ 16.7.4 del libro). Per questo nei filtri delle schede successive si vedono effetti ai bordi che "rientrano" dal lato opposto. Per evitarlo si fa padding (simmetrico o con zeri) prima della FFT e si ritaglia dopo.</p></div>
""", img='img/demo_boundary.png', printed=NB1 + 'celle 11–13')

s(7, "Passa-basso ideale e gaussiano in frequenza", """
<pre>cutoff = 0.08   # cicli/pixel
sigma = 2.0     # pixel
ideal_mask  = (radius &lt;= cutoff).astype(float)
smooth_mask = np.exp(-2*np.pi**2*sigma**2*radius**2)
ideal_image  = np.fft.ifft2(F * ideal_mask).real
smooth_image = np.fft.ifft2(F * smooth_mask).real</pre>
<p><b>Figura:</b> originale, passa-basso ideale e passa-basso gaussiano. Entrambi tolgono i dettagli fini, ma l'ideale è pieno di <b>aloni ondulati</b> che seguono i contorni (attorno alla testa, al cappotto, al cavalletto, anche sull'erba); il gaussiano è una sfocatura pulita. Lungo i bordi dell'immagine si vedono sottili fasce di intensità sbagliata: è la convoluzione circolare (scheda 6), che mescola ogni lato con quello opposto.</p>
<ul>
<li><b>Maschera ideale</b>: 1 dentro un disco di raggio 0.08 cicli/pixel, 0 fuori. Tiene il 2.0% dei coefficienti, che però contengono il 97% dell'energia (DC inclusa).</li>
<li><b>Maschera gaussiana</b>: exp(−2π<sup>2</sup>σ<sup>2</sup>|f|<sup>2</sup>) è la trasformata di Fourier di una gaussiana spaziale di deviazione standard σ = 2 pixel. Moltiplicare per questa maschera equivale a sfocare con quella gaussiana (con bordi periodici).</li>
<li>La gaussiana in frequenza ha deviazione standard 1/(2πσ) = 0.080 cicli/pixel: praticamente il cutoff dell'ideale. Il confronto è quindi equo: stessa "larghezza", forma diversa.</li>
<li>Regola da ricordare: <b>larga nello spazio ⇔ stretta in frequenza</b> (σ<sub>f</sub> = 1/(2πσ)).</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Ricavare la maschera gaussiana: la trasformata continua di e<sup>−x²/2σ²</sup> è proporzionale a e<sup>−2π²σ²f²</sup> (f in cicli per unità), e in 2D il prodotto di due gaussiane separabili dà e<sup>−2π²σ²(f<sub>x</sub>²+f<sub>y</sub>²)</sup>. Il guadagno in DC è 1: la media dell'immagine non cambia.</p></div>
""", img='img/demo_lowpass.png', printed=NB1 + 'celle 14–15')

s(8, "Risposta a un bordo: il ringing del passa-basso ideale", """
<pre>step = np.zeros_like(image); step[:, W//4:3*W//4] = 1   # fascia bianca verticale
step_ideal  = np.fft.ifft2(np.fft.fft2(step) * ideal_mask).real
step_smooth = np.fft.ifft2(np.fft.fft2(step) * smooth_mask).real</pre>
<p><b>Figura:</b> a sinistra le due maschere centrate (un disco netto e una macchia gaussiana); a destra una riga dell'immagine attorno al gradino in colonna 64. L'ideale sale oltre 1 e oscilla ai due lati del gradino, con onde che si smorzano lentamente; il gaussiano sale in modo liscio e monotono. Stampa: <code>Ideal step range: [-0.091, 1.091]</code>.</p>
<ul>
<li>Un taglio netto in frequenza corrisponde nello spazio a un kernel con <b>lobi negativi e oscillanti</b> (in 1D la sinc; con un disco in 2D l'analogo radiale, una funzione di Bessel). Convolvere un gradino con quel kernel dà <b>ringing</b>: overshoot del <b>9%</b>, il fenomeno di Gibbs.</li>
<li>La gaussiana ha trasformata gaussiana, sempre positiva nello spazio: fa una media pesata, l'uscita resta fra 0 e 1, niente oscillazioni.</li>
<li>Per le immagini il ringing si vede come <b>aloni</b> paralleli ai contorni (scheda 7). È il motivo per cui in L5–L6 si usano gaussiane e binomiali e non passa-basso ideali.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 16, § 16.6.3 e § 16.10</b><p>Il § 16.6.3 calcola la DFT di un box: la sinc discreta sin(πu(2L+1)/N)/sin(πu/N), con lobi di segno alterno. Per dualità, un box in frequenza (la maschera ideale) è una sinc nello spazio. Il § 16.10 classifica i filtri in passa-basso, passa-banda e passa-alto in base alla risposta in frequenza H[u, v] = trasformata del kernel, con guadagno in DC |H[0, 0]|. <a href="https://visionbook.mit.edu/image_processing_fourier.html">Link al capitolo</a>.</p></div>
""", img='img/demo_edge.png', printed=NB1 + 'cella 15')

s(9, "Il residuo passa-alto", """
<pre>high = np.fft.ifft2(F * (1-smooth_mask)).real
assert np.allclose(high + smooth_image, image)
assert abs(high.mean()) &lt; 1e-12</pre>
<p><b>Figura:</b> il residuo in mappa rosso/blu (bianco = 0): contorni del cameraman, del cavalletto e della camera in rosso e blu accoppiati, erba come rumore fine, cielo quasi bianco. Lungo i bordi dell'immagine c'è una cornice colorata: è di nuovo il bordo periodico.</p>
<ul>
<li>Maschera complementare 1 − M: <b>f<sub>high</sub> = f − f<sub>low</sub></b>. Le due parti sommate ridanno l'immagine esattamente (linearità).</li>
<li>La media del residuo è 0: la maschera gaussiana vale 1 in DC, quindi 1 − M vale 0 in DC e la componente continua va tutta nel passa-basso.</li>
<li>Le alte frequenze contengono <b>bordi, texture fini e rumore</b> insieme: un filtro lineare che toglie il rumore toglie anche i dettagli. Per questo il passa-basso non è un buon denoiser in generale; funziona solo se il disturbo sta in frequenze dove l'immagine non ha nulla (schede 10–11).</li>
<li>È la stessa decomposizione di un livello della piramide laplaciana della L6 (senza sottocampionamento): l<sub>0</sub> = g<sub>0</sub> − blur(g<sub>0</sub>).</li>
</ul>
""", img='img/demo_highpass.png', printed=NB1 + 'celle 16–17')

s(10, "Interferenza periodica: trovare i picchi", """
<pre>kx, ky = 37, 21
noise = .20*np.cos(2*np.pi*(kx*x/W + ky*y/H) + .4)
corrupted = image + noise
Fc = np.fft.fft2(corrupted)</pre>
<p><b>Figura:</b> a sinistra l'immagine con righe oblique fitte sovrapposte; a destra lo spettro, con due punti luminosi isolati (cerchiati) in (f<sub>x</sub>, f<sub>y</sub>) = ±(0.145, 0.082), simmetrici rispetto al centro e lontani dalla croce e dalla macchia centrale dell'immagine.</p>
<ul>
<li>Il disturbo è un'<b>onda reale</b> di ampiezza 0.2 e fase 0.4: nello spettro è una <b>coppia di picchi coniugati</b> in ±(k<sub>y</sub>, k<sub>x</sub>) (scheda 3). La fase cambia solo l'argomento dei due coefficienti, non la posizione.</li>
<li>Nello spazio il disturbo è ovunque; in frequenza è concentrato in <b>due soli coefficienti</b>. È il caso ideale per filtrare in frequenza: disturbo e immagine occupano zone diverse dello spettro.</li>
<li>Per togliere un'onda reale vanno tolti <b>entrambi</b> i picchi: togliendone uno solo la ricostruzione diventa complessa e metà del disturbo resta.</li>
</ul>
""", img='img/demo_interf.png', printed=NB1 + 'celle 18–19')

s(11, "Filtro notch contro passa-basso", """
<pre>def notch_mask(shape, fx0, fy0, width):
    fx, fy = frequency_grid(shape)
    mask = np.ones(shape)
    for sign in [-1, 1]:
        d2 = (fx - sign*fx0)**2 + (fy - sign*fy0)**2
        mask *= 1 - np.exp(-d2/(2*width**2))      # buco gaussiano in ±(fx0, fy0)
    return mask

notch = notch_mask(image.shape, kx/W, ky/H, width=1/W)
cleaned = np.fft.ifft2(Fc * notch).real</pre>
<p><b>Figura:</b> riferimento pulito, risultato del notch (indistinguibile dal riferimento) e passa-basso gaussiano (immagine sfocata e righe ancora visibili, attenuate). Stampa:</p>
<pre>Corrupted  MSE = 0.020000
Notch      MSE = 0.000001
Low-pass   MSE = 0.004886</pre>
<ul>
<li><b>Notch</b>: la maschera vale 1 ovunque tranne due "buchi" gaussiani di larghezza 1 bin (<code>width=1/W</code>) centrati sui picchi, dove vale 0. Tocca pochissimi coefficienti, quindi l'immagine resta intatta.</li>
<li>MSE della corrotta = potenza dell'onda = A<sup>2</sup>/2 = 0.2<sup>2</sup>/2 = <b>0.02</b>, esatto.</li>
<li><b>Passa-basso</b> (σ = 2): alla frequenza del disturbo, |f| = 0.166, la maschera vale e<sup>−2π²·4·0.166²</sup> ≈ <b>0.11</b>: resta l'11% dell'onda, per questo le righe si vedono ancora. E il suo errore viene quasi tutto dalla sfocatura: il blur sull'immagine pulita dà già MSE 0.0046 su 0.0049.</li>
<li>Morale: se si sa <b>dove</b> sta il disturbo nello spettro, si toglie quello e basta. Un filtro generico toglie anche il segnale.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 16, § 16.10.1</b><p>Stesso esempio su una foto vera: le colonne del palazzo del MIT (fig. 16.19) si ripetono ogni 14 pixel e in un'immagine 256 × 256 danno armoniche lungo l'asse orizzontale, attorno a 256/14 ≈ 18.2. Azzerando una banda stretta attorno a quei picchi le colonne spariscono; tenendo solo quei picchi resta l'opposto, solo le colonne. Differenza con il notebook: una struttura periodica ma non sinusoidale dà una serie di armoniche, non una sola coppia. <a href="https://visionbook.mit.edu/image_processing_fourier.html">Link al capitolo</a>.</p></div>
""", img='img/demo_notch.png', printed=NB1 + 'cella 19')

s(12, "Esercizio 1: ripulire corrupted_photo.npy", """
<p>Consegna: ripetere il procedimento su un'immagine nuova, di cui <b>non</b> si conosce la frequenza del disturbo: trovare i picchi nello spettro, costruire la maschera, ricostruire, confrontare con un blur gaussiano.</p>
<pre>observed = np.load("corrupted_photo.npy")          # 256×256
F = np.fft.fft2(observed - observed.mean())
mag = np.abs(F)
mag_search = mag.copy()
mag_search[np.hypot(FX, FY) &lt; 0.03] = 0           # ignora le basse frequenze
r, c = np.unravel_index(np.argmax(mag_search), mag.shape)
ky = int(np.fft.fftfreq(H)[r] * H)                 # indice -&gt; numero di periodi
kx = int(np.fft.fftfreq(W)[c] * W)                 # stampa: kx, ky = 29 -43
notch = notch_mask(observed.shape, kx/W, ky/H, width=1/W)
cleaned = np.fft.ifft2(np.fft.fft2(observed) * notch).real</pre>
<p><b>Figura:</b> tazzina di caffè coperta da righe oblique; con il notch le righe spariscono e i dettagli restano (piattino, cucchiaino, venature del tavolo); con il blur gaussiano le righe spariscono quasi del tutto ma l'immagine è sfocata.</p>
<ul>
<li><b>Perché mascherare il centro</b>: il massimo assoluto dello spettro è sempre nelle basse frequenze dell'immagine (DC e dintorni). Il disturbo è il picco più forte <b>fuori</b> dal centro.</li>
<li>Risultato: una sola coppia in (k<sub>y</sub>, k<sub>x</sub>) = ±(−43, 29), ampiezza 2|F|/(HW) = <b>0.18</b>, circa 400 volte sopra i coefficienti vicini.</li>
<li>Da indice a frequenza: <code>fftfreq(H)[r]</code> è in cicli/pixel, moltiplicato per H dà il numero di periodi, con il segno giusto per le frequenze negative.</li>
<li>Confronto con l'immagine pulita (è <code>data.coffee()</code> di scikit-image in grigio, 256 × 256): MSE osservata 0.0162, notch <b>1.8·10<sup>−6</sup></b>, blur gaussiano 0.0034. A |f| = 0.20 la gaussiana tiene solo il 4% dell'onda, per questo qui le righe spariscono meglio che nella scheda 11, ma al prezzo della sfocatura.</li>
</ul>
<div class="box x"><b>Approfondimento: rendere la ricerca più robusta</b><p>Se ci sono più disturbi, si cercano tutti i picchi fuori dal centro sopra una soglia (per esempio 10 volte la mediana del modulo in un intorno) invece del solo massimo. Se la frequenza non cade esattamente su un bin, il picco si allarga per leakage (scheda 3) e serve un notch più largo di un bin. Nel codice, <code>round</code> è più sicuro di <code>int</code> per convertire frequenze in indici interi.</p></div>
""", img='img/demo_ex_notch.png', printed=NB1 + 'celle 20–23')

s(13, "Esercizio 2: compressione con Fourier", """
<p>Consegna: riprodurre la fig. 16.8 del visionbook. Tenere solo i coefficienti di <b>modulo</b> più grande, azzerare gli altri, ricostruire e confrontare a vari livelli di compressione.</p>
<pre>order = np.sort(np.abs(F).ravel())[::-1]          # moduli in ordine decrescente
for keep in [1.0, 0.20, 0.05, 0.01, 0.002]:
    n = max(1, int(keep * F.size))
    thr = order[n - 1]                             # modulo dell'n-esimo più grande
    F_k = np.where(np.abs(F) &gt;= thr, F, 0)
    rec = np.fft.ifft2(F_k).real
    psnr = 10 * np.log10(1 / mse(rec, image))</pre>
<p><b>Figura e output</b>: 100% (PSNR 317 dB, cioè errore di macchina), 20% <b>31.6 dB</b> (indistinguibile), 5% <b>25.7 dB</b> (leggera grana e perdita di texture nell'erba), 1% <b>21.1 dB</b> (blocchi e aloni, soggetto riconoscibile), 0.2% <b>17.8 dB</b> (131 coefficienti: solo macchie).</p>
<ul>
<li><b>PSNR</b> = 10 log<sub>10</sub>(MAX<sup>2</sup>/MSE), con MAX = 1 per immagini in [0, 1]. Più alto è meglio; ogni 10 dB l'MSE cala di 10 volte.</li>
<li>Funziona perché lo spettro delle immagini naturali decade con la frequenza (scheda 4): con l'1% dei coefficienti si tiene il 97% dell'energia, con il 5% il 99%.</li>
<li>Scegliere i coefficienti più grandi è la <b>migliore approssimazione ai minimi quadrati</b> con quel numero di coefficienti: la base di Fourier è ortogonale, quindi per Parseval l'errore è la somma dei |F|<sup>2</sup> scartati.</li>
<li>Gli artefatti alle compressioni forti sono ringing e "onde" diffuse: ogni coefficiente è un'onda che copre tutta l'immagine. Per questo JPEG usa la DCT su <b>blocchi 8 × 8</b>: l'errore resta locale.</li>
</ul>
<div class="box w"><b>Attenzione: la ricostruzione non è sempre esattamente reale</b><p>L'idea "i due coniugati hanno lo stesso modulo, quindi entrano o escono insieme" è giusta in aritmetica esatta, ma i due moduli possono differire nell'ultima cifra e la soglia può tagliare una coppia. Verificato: al 5% (n = 3276) la parte immaginaria di <code>ifft2</code> arriva a 8·10<sup>−4</sup>, contro 10<sup>−16</sup> agli altri livelli. <code>.real</code> nasconde il problema e l'effetto sull'immagine è trascurabile, ma la versione pulita confronta i moduli arrotondati (<code>np.round(np.abs(F), 8)</code>) o tiene sempre le coppie.</p></div>
<div class="box b"><b>Dal libro · cap. 16, § 16.5.3, fig. 16.8</b><p>Il libro ricostruisce un'immagine 64 × 64 con gli N coefficienti di ampiezza maggiore. Il primo è sempre F[0, 0], quindi con N = 1 si ottiene un'immagine costante (la media); i due successivi sono una coppia coniugata di un'onda lentissima; con i primi <b>127 coefficienti su 4096</b> (circa il 3%) l'immagine è già riconoscibile. Il libro sottolinea che, per l'ortonormalità della base, è la migliore ricostruzione ai minimi quadrati. <a href="https://visionbook.mit.edu/image_processing_fourier.html">Link al capitolo</a>.</p></div>
""", img='img/demo_compression.png', printed=NB1 + 'celle 24–26')

# ---------------------------------------------------------------- filter_bank.ipynb

s(14, "Image Classification with Fixed Filter Banks: l'idea", """
<p>Secondo notebook: i filtri non servono solo a "pulire" un'immagine, ma a <b>descriverla</b>. Si costruisce un classificatore lineare le cui feature sono le risposte a un <b>banco di filtri scelti a mano</b>:</p>
<span class="f">x → x ∗ w<sub>k</sub> → ρ(x ∗ w<sub>k</sub>) → P(ρ(x ∗ w<sub>k</sub>)) → classificatore lineare</span>
<ul>
<li><b>w<sub>k</sub></b>: i filtri del banco (identità, box, Sobel, derivate gaussiane, Gabor, casuali).</li>
<li><b>ρ</b>: non linearità puntuale (|r|, r<sup>2</sup>, max(r, 0)).</li>
<li><b>P</b>: pooling su blocchi non sovrapposti (media o massimo).</li>
<li>Il classificatore è fisso (ridge lineare); si cambiano solo filtri, ρ e pooling, confrontandoli sulla <b>validazione</b>. Obiettivo dichiarato: un banco "piatto" (un solo strato) arriva a circa l'89%.</li>
<li>È la struttura di <b>uno strato di CNN</b> (convoluzione, attivazione, pooling), con due differenze: i filtri non si imparano e c'è un solo strato. Il notebook serve a capire quanto conta ciascun ingrediente prima di passare alle CNN.</li>
</ul>
<div class="box k"><b>Da saper spiegare: perché serve ρ</b><p>Convoluzione e pooling medio sono operatori <b>lineari</b>: le feature sono z = A x per una matrice A fissata. Un classificatore lineare calcola w<sup>T</sup>z = (A<sup>T</sup>w)<sup>T</sup>x, cioè ancora un classificatore lineare sui pixel. Aggiungere filtri lineari non allarga la famiglia di funzioni: senza non linearità non si può fare meglio dei pixel grezzi (scheda 23).</p></div>
<div class="box w"><b>Attenzione: il pooling medio non è una non linearità</b><p>Il testo dice che per questo "we have a nonlinearity and pooling". Il pooling <b>medio</b> è lineare (una convoluzione con un box seguita da sottocampionamento), quindi da solo non risolve il problema: lo risolve ρ. Il max pooling invece è non lineare.</p></div>
<div class="box b"><b>Dal libro · cap. 22, § 22.1 e cap. 24, § 24.1</b><p>Il cap. 22 si apre proprio così: i filtri lineari fanno molto, ma capire un'immagine richiede operatori non lineari, e un banco di filtri seguito da una non linearità semplice (il quadrato) dà rappresentazioni utili, antenate delle reti profonde. Il cap. 24 chiude il cerchio: dopo tanti banchi progettati a mano, "una CNN invece <i>impara</i> un banco di filtri efficace". Link: <a href="https://visionbook.mit.edu/spatial_filter_sets.html">cap. 22</a>, <a href="https://visionbook.mit.edu/convolutional_neural_nets.html">cap. 24</a>.</p></div>
""", sec=("l7-fb", "filter_bank.ipynb · banchi di filtri fissi su Fashion-MNIST", 'schede 14–29'), printed=NB2 + 'cella 1')

s(15, "Dati: Fashion-MNIST", """
<pre>X_all, y_all = load_data("train_x"), load_data("train_y")   # 60000 immagini 28×28
perm = np.random.default_rng(SEED).permutation(len(X_all))
X_train, y_train = X_all[perm[:20000]], y_all[perm[:20000]]
X_val,   y_val   = X_all[perm[50000:]], y_all[perm[50000:]]    # 10000, disgiunte
# test: le 10000 immagini ufficiali t10k</pre>
<p><b>Figura:</b> tre esempi per ciascuna delle 10 classi (T-shirt, pantalone, pullover, vestito, cappotto, sandalo, camicia, sneaker, borsa, stivaletto): sagome chiare su fondo nero, centrate.</p>
<ul>
<li>Immagini in scala di grigi 28 × 28, valori portati in [0, 1]. Il notebook scarica i file in <code>data/</code> se mancano (30 MB).</li>
<li><b>Tre insiemi</b>: training (20000) per allenare, validazione (10000) per scegliere filtri e iperparametri, test (10000) solo alla fine. Train e validazione vengono dallo stesso file ma da indici disgiunti della stessa permutazione.</li>
<li>Rispetto a MNIST (cifre) è più difficile: alcune classi hanno sagome quasi uguali (camicia, T-shirt, pullover, cappotto) e si distinguono per dettagli come maniche, colletto, bottoni.</li>
</ul>
""", img='img/fb_dataset.png', printed=NB2 + 'celle 2–5')

s(16, "Le funzioni della pipeline", """
<pre>NONLINEARITIES = {"none": lambda r: [r], "abs": lambda r: [np.abs(r)],
                  "square": lambda r: [r ** 2], "rectify": lambda r: [np.maximum(r, 0)]}

def convolve(X, kernel):   # (N, H, W) -&gt; (N, H, W), zero padding
    return signal.fftconvolve(X, np.asarray(kernel, np.float32)[None], mode="same", axes=(1, 2))

def pool(R, size, kind="avg"):   # blocchi size×size non sovrapposti
    N, H, W = R.shape
    R = R[:, :H//size*size, :W//size*size].reshape(N, H//size, size, W//size, size)
    R = R.mean(axis=(2, 4)) if kind == "avg" else R.max(axis=(2, 4))
    return R.reshape(N, -1)

def fit_and_score(F_tr, y_tr, F_ev, y_ev, alpha=1.0):
    clf = make_pipeline(StandardScaler(), RidgeClassifier(alpha=alpha))
    return clf.fit(F_tr, y_tr).score(F_ev, y_ev)</pre>
<ul>
<li><code>convolve</code> filtra tutto il batch in una volta con la FFT (<code>fftconvolve</code>, sugli assi 1 e 2). <code>mode="same"</code>: uscita 28 × 28, fuori dall'immagine zeri (qui innocuo: il fondo di Fashion-MNIST è già nero).</li>
<li><code>pool</code> usa un <code>reshape</code> a 5 dimensioni: ogni blocco size × size diventa due assi su cui si fa media o massimo. Con pool 4: 7 × 7 = 49 numeri per filtro.</li>
<li><b>Numero di feature</b> = numero di filtri × (28/p)<sup>2</sup>.</li>
<li><code>extract_features</code> concatena i blocchi di tutti i filtri e, se <code>power ≠ 1</code>, applica z ← sign(z)|z|<sup>power</sup>.</li>
<li>Classificatore: <b>standardizzazione</b> (stimata solo sul training, dentro la pipeline: niente leakage, a differenza della L4) + <b>ridge</b> lineare con α = 1, uno contro tutti.</li>
<li><code>show_bank</code> disegna i kernel (rosso positivo, blu negativo), <code>show_responses</code> le risposte e le feature dopo ρ e pooling, <code>show_conv_responses</code> le risposte su 3 esempi per classe.</li>
</ul>
<div class="box w"><b>Attenzione: "ReLU" non esiste nel dizionario</b><p>Il markdown elenca la non linearità <code>'ReLU'</code>, ma la chiave in <code>NONLINEARITIES</code> è <code>'rectify'</code>: <code>nonlinearity="ReLU"</code> dà <code>KeyError: 'ReLU'</code>. Si usa <code>"rectify"</code> (oppure si aggiunge la chiave).</p></div>
<div class="box w"><b>Attenzione: show_responses usa sempre pool 4</b><p>Disegna <code>pool(rp[None], 4).reshape(7, 7)</code> qualunque sia il pooling che si sta provando: le mappe mostrate non cambiano se si cambia <code>pool_size</code>. Per vederle serve passare la dimensione del pooling e usare <code>reshape(28//p, 28//p)</code>.</p></div>
""", printed=NB2 + 'celle 6–8')

s(17, "Punto di partenza: i pixel grezzi", """
<pre>identity = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]], float)
evaluate([identity], "pixels (identity, none, pool 1)", nonlinearity="none", pool_size=1)
# val acc = 0.8128   #features = 784</pre>
<ul>
<li>Il filtro <b>identità</b> (una delta) restituisce l'immagine; senza non linearità e con pool 1 le feature sono i 784 pixel.</li>
<li>Un classificatore lineare sui pixel fa già <b>81.3%</b>: su immagini centrate e normalizzate un "modello medio" per classe funziona discretamente.</li>
<li>È il riferimento per tutto il resto: ogni banco va confrontato con 0.813 e con il suo numero di feature.</li>
<li>Le figure della cella (kernel, risposte, 30 esempi filtrati) per l'identità mostrano semplicemente le immagini originali.</li>
</ul>
""", printed=NB2 + 'celle 9–10')

s(18, "Baseline: identità, box, Sobel x e y", """
<pre>box     = np.ones((3, 3)) / 9
sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], float)   # derivata in x, media in y
sobel_y = sobel_x.T
baseline_bank = [identity, box, sobel_x, sobel_y]      # abs, pool 4: 4 × 49 = 196 feature</pre>
<p><b>Figura:</b> una T-shirt a righe orizzontali. Risposte: l'identità e il box la ricopiano (il box più sfocata); Sobel x risponde solo ai due fianchi della maglia; Sobel y risponde forte a <b>ogni riga</b>. Sotto, le mappe 7 × 7 dopo |·| e pool 4: è tutto ciò che vede il classificatore.</p>
<ul>
<li>I pezzi <code>box</code>, <code>sobel_x</code>, <code>sobel_y</code> erano da completare (esercizio); sopra la soluzione standard.</li>
<li><b>Sobel</b> = derivata centrale [−1, 0, 1] in una direzione × smoothing [1, 2, 1] nell'altra (L5): separabile, meno sensibile al rumore della differenza semplice.</li>
<li>Risultati (validazione): baseline <b>0.8381</b> con 196 feature, cioè 4 volte meno dei pixel e 2.5 punti meglio.</li>
<li><b>QB.1</b>: senza identità 0.8343 (il pixel grezzo aiuta poco); solo identità con abs e pool 4: 0.7499. Il pooling da solo butta via troppo: servono i filtri di bordo <b>prima</b> del pooling, perché la media di un blocco di pixel perde i contorni, la media di |bordi| no.</li>
<li><b>QB.2</b> (risposta nel notebook): Sobel x vede bordi verticali (pantaloni, vestiti, borse), Sobel y bordi orizzontali (cinghie dei sandali, orli, maniche). Il rapporto fra le due risposte in ogni blocco è un descrittore grezzo dell'<b>orientazione locale</b>.</li>
</ul>
<div class="box x"><b>Approfondimento: il segno di Sobel</b><p><code>fftconvolve</code> fa una vera convoluzione e ribalta il kernel: <code>sobel_x</code> calcola meno la derivata (lo stesso problema del segno della L4). Nella figura il fianco sinistro della maglia (da nero a chiaro) è blu, il destro rosso. Con <code>abs</code> non conta. Con <code>rectify</code> sì: tiene una sola polarità di bordo. Aggiungendo anche −Sobel x e −Sobel y, <code>rectify</code> sulla baseline passa da 0.8361 a 0.8497 (verificato): è il motivo per cui una CNN ha spesso filtri a coppie di segno opposto.</p></div>
""", img='img/fb_responses.png', printed=NB2 + 'celle 11–13')

s(19, "Esercizio: diagonali e laplaciano", """
<pre>sobel_d45  = np.array([[ 0,  1, 2], [-1, 0, 1], [-2, -1, 0]], float)
sobel_d135 = np.array([[-2, -1, 0], [-1, 0, 1], [ 0,  1, 2]], float)
laplacian  = np.array([[ 0,  1, 0], [ 1, -4, 1], [ 0,  1, 0]], float)   # 4-vicini (L5)
ex1_bank = baseline_bank + [sobel_d45, sobel_d135, laplacian]            # 7 filtri, 343 feature</pre>
<p><b>Figura:</b> i 7 kernel del banco. Le diagonali sono Sobel ruotati di 45°: derivata attraverso il bordo diagonale e media lungo di esso (pesi 2 e 1 sulle due diagonali, zeri sull'altra). Il laplaciano è isotropo, con −4 al centro.</p>
<ul>
<li>Risultati: baseline + diagonali <b>0.8597</b>; baseline + laplaciano <b>0.8484</b>; entrambi <b>0.8640</b>.</li>
<li>Le diagonali aiutano di più (+2.2 punti contro +1.0): aggiungono <b>orientazioni</b> che Sobel x/y non coprono (colletti a V, spalle, lacci). Il laplaciano è isotropo: risponde a punti, linee sottili e bordi di ogni orientazione, ma non dice quale orientazione.</li>
<li>Nella figura di risposta della cella (T-shirt a righe) il laplaciano risponde due volte a ogni riga (una per bordo): è una derivata seconda.</li>
</ul>
<div class="box x"><b>Approfondimento: perché dopo |·| le orientazioni vanno messe esplicitamente</b><p>Per una derivata prima, la risposta in qualunque direzione θ è una combinazione lineare delle due derivate x e y: cos θ · ∂<sub>x</sub> + sin θ · ∂<sub>y</sub> (filtri <b>steerable</b>, scheda 20). Prima della non linearità le diagonali sarebbero quindi ridondanti. Ma il classificatore vede |∂<sub>x</sub>| e |∂<sub>y</sub>| già mediati sui blocchi, e da questi non può ricostruire |cos θ ∂<sub>x</sub> + sin θ ∂<sub>y</sub>|: dopo ρ e pooling ogni orientazione aggiunta porta informazione nuova.</p></div>
""", img='img/fb_bank7.png', printed=NB2 + 'celle 14–16')

s(20, "Esercizio: derivate gaussiane a più scale", """
<pre>def gaussian_derivative_kernel(sigma, order):   # order in 'x','y','xx','yy','xy'
    G = gaussian_kernel(sigma); s2 = sigma**2      # supporto (2R+1)², R = ceil(3σ)
    return {"x": -X/s2*G, "y": -Y/s2*G,
            "xx": (X**2/s2**2 - 1/s2)*G, "yy": (Y**2/s2**2 - 1/s2)*G,
            "xy": X*Y/s2**2*G}[order]

def make_gd_bank(sigmas):      # per ogni σ: G, Gx, Gy, Gxx, Gyy, Gxy
    ...
evaluate([identity] + make_gd_bank(sigmas)[0], f"gauss-deriv s={sigmas}")</pre>
<p><b>Figura:</b> i 12 kernel per σ = 1 e σ = 2. Gx e Gy sono coppie rosso/blu affiancate (dispari), Gxx e Gyy una banda centrale blu fra due rosse, Gxy un quadrifoglio a segni alterni. Con σ = 2 sono le stesse forme, più grandi (13 × 13 invece di 7 × 7).</p>
<ul>
<li>Le formule sono le derivate analitiche della gaussiana: ∂G/∂x = −(x/σ<sup>2</sup>)G, ∂<sup>2</sup>G/∂x<sup>2</sup> = (x<sup>2</sup>/σ<sup>4</sup> − 1/σ<sup>2</sup>)G, ∂<sup>2</sup>G/∂x∂y = (xy/σ<sup>4</sup>)G (L5). Il banco era da costruire; soluzione: identità + per ogni σ i 6 filtri.</li>
<li>Risultati: σ = 1 <b>0.8630</b> (343 feature); σ = 2 <b>0.8607</b>; σ = {1, 2} <b>0.8810</b> (637); σ = {0.7, 1, 2, 3} <b>0.8905</b> (1225).</li>
<li>Una scala sola vale quanto i 7 filtri 3 × 3; <b>più scale insieme</b> aiutano: σ piccolo vede i dettagli (cuciture, bottoni), σ grande le strutture larghe (lo spazio fra le gambe dei pantaloni, il colletto, una manica). È l'idea dello scale-space della L6.</li>
<li>Le derivate seconde rispondono a <b>linee e blob</b> di larghezza ~σ, le prime a <b>bordi</b>.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 22, § 22.3.1 (steerable filters)</b><p>Il libro mostra che le derivate gaussiane sono <b>orientabili</b> (steerable): la derivata prima in direzione θ è cos θ · g<sub>x</sub> + sin θ · g<sub>y</sub>, due filtri di base bastano; la derivata seconda in direzione θ è cos<sup>2</sup>θ · g<sub>xx</sub> + sin<sup>2</sup>θ · g<sub>yy</sub> − 2 cos θ sin θ · g<sub>xy</sub>, ne bastano tre (fig. 22.9). Quindi {Gx, Gy, Gxx, Gyy, Gxy} a una scala contiene linearmente tutte le orientazioni delle derivate fino al secondo ordine. Il cap. 24 (fig. 24.19) mostra che una piccola CNN addestrata a distinguere linee orizzontali e verticali impara filtri che somigliano proprio a derivate gaussiane. <a href="https://visionbook.mit.edu/spatial_filter_sets.html">Link al capitolo</a>.</p></div>
""", img='img/fb_gd_bank.png', printed=NB2 + 'celle 17–20')

s(21, "Filtri di Gabor: posizione, orientazione, frequenza", """
<pre>def gabor_kernel(sigma, theta, wavelength, phase=0.0):
    Xr =  X*np.cos(theta) + Y*np.sin(theta)        # coordinate ruotate
    Yr = -X*np.sin(theta) + Y*np.cos(theta)
    g = np.exp(-(Xr**2 + Yr**2)/(2*sigma**2)) * np.cos(2*np.pi*Xr/wavelength + phase)
    g = g - g.mean()                               # media zero: non risponde al costante
    return g / np.abs(g).sum()                     # norma L1 = 1

SCALES = [(1.5, 4), (3, 8)]                        # (σ, λ)
# per ogni scala, orientazione θ = kπ/n e fase in (0, π/2)</pre>
<p><b>Figura</b> (4 orientazioni): 16 kernel. Riga sopra σ = 1.5, λ = 4; sotto σ = 3, λ = 8. Per ogni orientazione (0°, 45°, 90°, 135°) una versione <b>pari</b> "e" (coseno: una barra centrale fra due di segno opposto) e una <b>dispari</b> "o" (seno: una coppia rosso/blu, come un rilevatore di bordo).</p>
<ul>
<li>Un Gabor è una <b>gaussiana moltiplicata per un'onda</b>: la gaussiana dice <b>dove</b> (posizione, estensione σ), l'onda dice <b>quale orientazione</b> θ e <b>quale frequenza</b> 1/λ. In frequenza è una gaussiana centrata su ±(cos θ, sin θ)/λ: un passa-banda orientato.</li>
<li>Le due scale hanno lo stesso rapporto σ/λ = 0.375: stesso numero di oscillazioni sotto l'inviluppo, solo ingrandite. Sono copie scalate dello stesso filtro, come in una piramide.</li>
<li>Pari e dispari (fase 0 e π/2) formano una <b>coppia in quadratura</b>: insieme coprono sia le linee (pari) sia i bordi (dispari).</li>
<li>La sottrazione della media rende il filtro insensibile alle regioni uniformi; la normalizzazione L1 mette i filtri sulla stessa scala.</li>
<li>Biologia: il profilo dei Gabor somiglia ai campi recettivi delle <b>cellule semplici</b> di V1 e ai filtri del primo strato delle CNN.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 22, § 22.2</b><p>Il libro scrive il Gabor complesso ψ(x, y) = 1/(2πσ<sup>2</sup>) · exp(−(x<sup>2</sup>+y<sup>2</sup>)/2σ<sup>2</sup>) · exp(j(u<sub>0</sub>x + v<sub>0</sub>y)) (eq. 22.1): la parte reale è il Gabor coseno, quella immaginaria il Gabor seno. La frequenza centrale (u<sub>0</sub>, v<sub>0</sub>), in radianti per pixel, corrisponde al (2π cos θ/λ, 2π sin θ/λ) del notebook. Con σ grande il Gabor tende a un'onda pura (Fourier, localizzato in frequenza ma non nello spazio); con σ piccolo a un impulso (pixel): il Gabor è il compromesso, ed è il filtro che ottimizza la localizzazione congiunta nei due domini. Figure 22.2–22.4: forme e trasformate al variare di σ, frequenza e orientazione; fig. 22.8: come un banco di Gabor copre il piano delle frequenze (tassellatura polare, σ proporzionale alla distanza dall'origine, come qui). <a href="https://visionbook.mit.edu/spatial_filter_sets.html">Link al capitolo</a>.</p></div>
""", img='img/fb_gabor_bank.png', printed=NB2 + 'celle 21–23')

s(22, "Gabor: quante orientazioni servono", """
<pre>for n in [2, 4, 8]:
    evaluate([identity] + gabor_bank(n)[0], f"gabor {n} orient. x 2 scales x 2 phases")
# gabor 2: 0.8673 (441 feature)   gabor 4: 0.8865 (833)   gabor 8: 0.8949 (1617)</pre>
<p><b>Figura:</b> accuratezza di validazione contro numero di orientazioni: sale da 0.867 a 0.887 a 0.895, con pendenza che cala.</p>
<ul>
<li>Numero di filtri = 1 (identità) + n orientazioni × 2 scale × 2 fasi: 9, 17, 33.</li>
<li>Più orientazioni = più accuratezza, con guadagno decrescente (2 → 4: +1.9 punti, 4 → 8: +0.8). Con 8 orientazioni il passo è 22.5°: a quel punto orientazioni vicine danno risposte molto correlate.</li>
<li>Con 8 orientazioni si raggiunge l'<b>89.5%</b> promesso dal notebook per un banco "piatto".</li>
<li>Questi valori coincidono con gli output salvati dal docente (differenze ≤ 0.0004): le celle Gabor erano già complete, quindi sono il miglior controllo che l'ambiente riproduce i risultati.</li>
</ul>
""", img='img/fb_gabor_acc.png', printed=NB2 + 'cella 23')

s(23, "Esercizio: la non linearità", """
<pre>for nl in ["none", "abs", "square", "rectify"]:
    evaluate(ex1_bank, f"ex1, {nl}, pool 4", nonlinearity=nl)
evaluate(ex1_bank, "ex1, none, pool 1", nonlinearity="none", pool_size=1)</pre>
<p>Risultati con il banco a 7 filtri 3 × 3 della scheda 19, pool 4:</p>
<ul>
<li><b>none</b> 0.8091 · <b>abs</b> 0.8640 · <b>square</b> 0.8468 · <b>rectify</b> 0.8641.</li>
<li>Domanda del notebook: senza non linearità si fa meglio dei pixel? No: <b>none, pool 1</b> (5488 feature, 7 volte i pixel) dà <b>0.8127</b> contro 0.8128 dei pixel. Tutte quelle feature sono combinazioni lineari degli stessi 784 pixel (scheda 14). Con pool 4 si scende a 0.8091: il pooling medio è una proiezione lineare che perde informazione.</li>
<li><b>abs</b> e <b>rectify</b> si equivalgono; abs rende la risposta indipendente dalla <b>polarità</b> del bordo (scuro→chiaro o chiaro→scuro), che per riconoscere un vestito non conta.</li>
<li><b>square</b> è peggiore: eleva al quadrato proprio i valori grandi, così pochi bordi molto contrastati dominano le feature. È l'effetto opposto di <code>power=0.5</code> (scheda 25).</li>
</ul>
<div class="box x"><b>Approfondimento: perché "none" dà quasi esattamente i pixel</b><p>L'argomento lineare dice che la famiglia di classificatori è la stessa. Non garantisce numeri identici: standardizzazione e regolarizzazione ridge agiscono sulle feature, non sui pixel, quindi il classificatore scelto può differire un poco. Qui la differenza è 0.0001: l'argomento regge anche in pratica.</p></div>
""", printed=NB2 + 'celle 24–25')

s(24, "Esercizio: la dimensione del pooling", """
<pre>pool_sizes = [1, 2, 4, 7, 14, 28]
accs = [evaluate(ex1_bank, f"ex1, abs, avg pool {p}", pool_size=p) for p in pool_sizes]</pre>
<p><b>Figura</b> (asse x logaritmico): 0.8645 (pool 1, 5488 feature), <b>0.8810</b> (pool 2, 1372), 0.8640 (pool 4, 343), 0.8184 (pool 7, 112), 0.7026 (pool 14, 28), 0.5239 (pool 28, 7). Un massimo a pool 2, poi un crollo.</p>
<ul>
<li><b>Cosa si guadagna</b>: tolleranza a piccoli spostamenti e deformazioni (un bordo che si sposta di un pixel resta nello stesso blocco), meno feature (classificatore più veloce e meno overfitting), meno rumore.</li>
<li><b>Cosa si perde</b>: la <b>posizione</b>. Con pool 28 resta un numero per filtro, "quanti bordi verticali ci sono nell'immagine", senza sapere dove: 52%.</li>
<li>Il punto ottimo dipende dalla scala degli oggetti e dei dettagli utili: qui, su immagini 28 × 28 centrate, blocchi 2 × 2.</li>
<li>Collegamento con la L6: il pooling medio con passo p è un blur box seguito da sottocampionamento, quindi può fare aliasing. Il box è un pessimo prefiltro (lobi laterali, L4–L5).</li>
</ul>
<div class="box b"><b>Dal libro · cap. 24, § 24.3.1</b><p>Il libro definisce max pooling e mean pooling su un intorno N(i) e spiega il loro ruolo: trasformano l'<b>equivarianza</b> della convoluzione (se l'input si sposta, la mappa si sposta) in <b>invarianza</b> (con un intorno abbastanza grande, l'uscita non dipende da dove sta il bordo). Nota anche il pooling <b>sui canali</b>: il massimo sulle risposte di un banco di rilevatori orientati dà una mappa alta dove c'è un bordo di <i>qualunque</i> orientazione. Il pooling è un sottocampionamento: porta con sé i problemi di aliasing della L6 (§ 24.2.2, fig. 24.8, per lo stride). <a href="https://visionbook.mit.edu/convolutional_neural_nets.html">Link al capitolo</a>.</p></div>
""", img='img/fb_pool.png', printed=NB2 + 'cella 25')

s(25, "Max pooling e power 0.5", """
<pre>evaluate(ex1_bank, "ex1, abs, max pool 4", pool_type="max")    # 0.8533
evaluate(ex1_bank, "ex1, abs, pool 4, power 0.5", power=0.5)   # 0.8717</pre>
<ul>
<li><b>Max pooling</b> 0.8533 contro 0.8640 della media (pool 4). Su queste immagini la media è meglio: tiene conto di <b>quanta</b> struttura c'è nel blocco, il massimo solo della più forte ed è più sensibile al rumore. Nelle CNN profonde il max pooling funziona bene perché i filtri a monte sono appresi per rendere significativo il massimo.</li>
<li><b>power = 0.5</b> (radice quadrata delle feature dopo il pooling): +0.8 punti a costo zero. Domanda del notebook: perché aiuta un classificatore lineare?</li>
</ul>
<div class="box k"><b>Da saper spiegare: la compressione della dinamica</b><p>Le risposte ai bordi hanno una distribuzione con coda lunga: pochi blocchi molto contrastati, molti deboli. Un classificatore lineare pesa le feature in modo proporzionale al loro valore, quindi pochi valori grandi dominano il punteggio. La radice comprime i valori grandi ed espande i piccoli: conta di più <b>se</b> c'è struttura che <b>quanto</b> è contrastata, cioè una forma di invarianza al contrasto. Stessa logica del log dello spettro nella L4. (Spiegazione standard; il notebook misura solo il guadagno.)</p></div>
""", printed=NB2 + 'celle 25–26')

s(26, "Esercizio: filtri casuali", """
<pre>rng = np.random.default_rng(0)
def random_bank(n, size=5):
    return [rng.standard_normal((size, size)) for _ in range(n)]</pre>
<p><b>Figura:</b> 8 kernel 5 × 5 casuali: macchie di rosso e blu senza struttura riconoscibile.</p>
<ul>
<li>Risultati (abs, pool 4), accanto ai banchi a mano con lo stesso numero di feature circa:
<ul>
<li>4 casuali <b>0.8359</b> contro baseline 0.8381;</li>
<li>13 casuali <b>0.8769</b> contro derivate gaussiane σ = {1, 2} 0.8810;</li>
<li>34 casuali <b>0.8924</b> contro Gabor 8 orientazioni 0.8949.</li>
</ul></li>
<li><b>Q6.1</b>: con abbastanza filtri i casuali arrivano quasi ai banchi progettati. Un filtro casuale è una combinazione di tutte le frequenze e orientazioni; dopo |·| e pooling ne misura comunque un pezzo, e molti filtri insieme coprono lo spettro.</li>
<li><b>Q6.2</b>: i casuali non richiedono progettazione, ma non si sa cosa misurano (poco interpretabili), sono ridondanti e servono più filtri per lo stesso risultato. Quelli a mano sono interpretabili ("bordo a 45° a scala 2") e più efficienti a parità di feature.</li>
<li>Il risultato dice che il grosso del lavoro lo fanno <b>ρ + pooling + classificatore</b>; la scelta dei filtri conta, ma meno di quanto sembri. Una CNN va oltre imparando i filtri <b>e</b> impilando più strati.</li>
</ul>
""", img='img/fb_random.png', printed=NB2 + 'celle 27–29')

s(27, "Challenge: migliorare il banco", """
<p>Consegna libera: combinare i banchi, cambiare ρ, pooling e power, oppure scrivere una feature map propria con <code>evaluate_custom</code>, per esempio una <b>piramide spaziale</b> (pooling a più dimensioni concatenato) o un <b>secondo strato</b> (filtrare di nuovo le mappe dopo ρ, prima del pooling). Risultati rieseguiti:</p>
<pre>best_bank = [identity] + gabor_bank(8)[0]
evaluate(best_bank, "gabor 8, power 0.5", power=0.5)       # 0.9056, 1617 feature

def pyramid(X):     # stesse risposte, pooling 2, 4 e 7 concatenati
    return np.concatenate([extract_features(X, ex1_bank, pool_size=p, power=0.5)
                           for p in (2, 4, 7)], axis=1)
evaluate_custom(pyramid, "ex1, pyramid 2+4+7, power 0.5")    # 0.8950, 1827 feature</pre>
<ul>
<li><b>Gabor 8 + power 0.5</b>: <b>90.6%</b>, oltre la soglia dell'89%.</li>
<li><b>Piramide spaziale</b> sui 7 filtri 3 × 3: da 0.8640 (pool 4) a 0.8950. Blocchi piccoli (dettaglio, posizione) e grandi (tolleranza) insieme: è la stessa idea dello <i>spatial pyramid pooling</i> e delle piramidi della L6.</li>
<li><b>Energia di Gabor</b> (verificata a parte): sostituendo le due fasi con √(pari<sup>2</sup> + dispari<sup>2</sup>) si ottiene <b>0.8918</b> con metà delle feature (833). La risposta non dipende più dalla fase: un bordo e una linea con la stessa orientazione e frequenza danno lo stesso valore. Il docente, nei suoi output, riporta 0.8884 con una variante di questa idea e 0.9094 con Gabor a 3 scale più derivate gaussiane (3038 feature).</li>
</ul>
<pre>e = convolve(X, gabor_kernel(s, th, lam, 0))
o = convolve(X, gabor_kernel(s, th, lam, np.pi/2))
feat = pool(np.sqrt(e**2 + o**2), 4)             # "complex cell"</pre>
<div class="box b"><b>Dal libro · cap. 22, § 22.2.2 (local amplitude)</b><p>Con due filtri in quadratura h e q, a<sup>2</sup>(x, y) = ℓ<sub>h</sub><sup>2</sup> + ℓ<sub>q</sub><sup>2</sup> è l'<b>ampiezza locale</b>: la potenza dell'immagine nella banda del filtro, in quell'intorno. Il libro mostra (fig. 22.7) che non dipende dal segno del contrasto e che, anche se i due filtri sono passa-banda, a è un segnale <b>passa-basso</b>, liscio: per questo si può sottocampionare (pooling) senza perdere molto. E osserva che "filtri in quadratura → quadrato → somma" è esattamente una CNN a due strati con due canali nel primo strato e una non linearità quadratica: il modello delle cellule complesse di V1. <a href="https://visionbook.mit.edu/spatial_filter_sets.html">Link al capitolo</a>.</p></div>
""", printed=NB2 + 'celle 30–31')

s(28, "Valutazione finale sul test set", """
<pre>FINAL_BANK = [identity] + gabor_bank(8)[0]    # best validation entry
FINAL_CFG  = dict(nonlinearity="abs", pool_size=4, pool_type="avg", power=0.5)
X_trval = np.concatenate([X_train, X_val])     # si riallena su train + validazione
# pixels     TEST accuracy = 0.8099
# baseline   TEST accuracy = 0.8382
# final      TEST accuracy = 0.8985</pre>
<ul>
<li>Tutte le scelte fatte finora usano la validazione. Solo alla fine si misura il test, <b>una volta</b>, per avere una stima non ottimistica.</li>
<li>Prima del test si riallena su train + validazione (30000 immagini): più dati, stessa configurazione.</li>
<li>Test: pixel <b>81.0%</b>, baseline <b>83.8%</b>, Gabor 8 + power 0.5 <b>89.9%</b> (in validazione era 90.6%: il leggero calo è normale, la configurazione è stata scelta sulla validazione).</li>
</ul>
<div class="box w"><b>Attenzione: nel notebook del docente FINAL_BANK è la baseline</b><p>Nella versione distribuita la riga è <code>FINAL_BANK = baseline_bank  # best validation entry</code>: il commento chiede il banco migliore, il codice mette la baseline, quindi "final" e "baseline" darebbero lo stesso numero. Va sostituito con il proprio banco migliore, come sopra. Inoltre gli output salvati del docente vengono da esecuzioni diverse (questa cella aveva un <code>NameError</code> mentre l'ultima ha il grafico): per confrontare conviene rieseguire tutto dall'alto (Kernel → Restart &amp; Run All). Entrambi i punti vengono dagli appunti di Octech sulla versione originale; nella copia in <code>lab/</code> la riga è già corretta.</p></div>
""", printed=NB2 + 'celle 32–33')

s(29, "Wrap-up: matrice di confusione e cosa manca per una CNN", """
<p><b>Figura:</b> matrice di confusione sul test (righe = classe vera, normalizzate). Diagonale alta per pantalone e borsa (0.98), sandalo e sneaker (0.97), stivaletto (0.95, confuso con sneaker 0.04). La classe peggiore è <b>camicia</b> (0.66): scambiata con T-shirt (0.14), cappotto (0.08), pullover (0.07). Anche T-shirt (0.86), pullover (0.86) e cappotto (0.83) si confondono fra loro.</p>
<ul>
<li>Gli errori sono fra classi con la <b>stessa sagoma</b>: le differenze (colletto, bottoni, lunghezza della manica) sono piccole e in posizioni precise. Filtri di un solo strato più pooling vedono "quanti bordi e di che orientazione in ogni zona", non "un colletto".</li>
<li>Conclusione del notebook: mancano la <b>gerarchia</b> (filtri applicati alle risposte di altri filtri, che combinano bordi in parti e parti in oggetti) e i <b>filtri appresi</b> dai dati per il compito. È quello che aggiunge una CNN.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 24, § 24.2, 24.4, 24.7</b><p>Un <b>layer convoluzionale</b> (§ 24.2) è esattamente <code>convolve</code> con più filtri, ma con i pesi appresi; il libro nota che nelle reti è in realtà una cross-correlazione (con pesi appresi il ribaltamento non conta, L4). Il classificatore più semplice del § 24.4 è: convoluzione → ReLU → pooling globale medio → strato lineare → softmax, cioè la pipeline di questo notebook con i filtri imparati. Il § 24.7 spiega il <b>campo recettivo</b>: impilando strati e sottocampionamenti ogni neurone vede una zona sempre più grande, cosa che un solo strato 3 × 3 non può fare. Il § 24.10 giustifica la convoluzione con la <b>località</b> e l'<b>invarianza alla traslazione</b> del contenuto visivo. <a href="https://visionbook.mit.edu/convolutional_neural_nets.html">Link al capitolo</a>.</p></div>
""", img='img/fb_confusion.png', printed=NB2 + 'celle 34–35')

# ---------------------------------------------------------------- 06-image-blending

s(30, "06-image-blending: già visto nella L6", """
<p>Il terzo notebook della cartella è <b>identico byte per byte</b> a quello della lezione 6 (stesso MD5): la "orapple", metà mela e metà arancia, con il <b>multi-band blending</b> di Burt e Adelson. Le spiegazioni cella per cella, i due bug (laplaciani in uint8 e maschera che non si sfoca) e la correzione in float sono nella L6, sezione finale "Notebook 06-image-blending".</p>
<ul>
<li>Cosa collega questo notebook agli altri due: il blending mescola ogni <b>banda di frequenza</b> separatamente, con una transizione tanto più larga quanto più la banda è bassa. È un filtro passa-banda (i livelli della piramide laplaciana) seguito da una combinazione, la stessa logica "decomponi in frequenza, agisci per banda, ricomponi" di <code>demo.ipynb</code>.</li>
<li>La piramide laplaciana è a sua volta un banco di filtri passa-banda isotropi, a più scale (cap. 23 del libro); i Gabor della scheda 21 sono la versione <b>orientata</b>.</li>
</ul>
""", sec=("l7-blend", "06-image-blending", 'scheda 30, rimanda alla L6'), printed=NB3 + 'vedi L6')
