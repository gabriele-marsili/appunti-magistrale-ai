NB1 = 'NOTEBOOK demo.ipynb · '
NB2 = 'NOTEBOOK classification.ipynb · '
NB3 = 'NOTEBOOK 15lif.ipynb · '

# ---------------------------------------------------------------- demo.ipynb

s(1, "Signal Processing with Audio: obiettivi e setup", """
<p>Primo notebook: gli strumenti della L3 (DFT, convoluzione, teorema di convoluzione) applicati a un <b>segnale 1D</b>, l'audio. In 1D si vede e si <b>ascolta</b> tutto, poi in L5–L6 le stesse idee passano alle immagini.</p>
<p>Cosa fa, in ordine:</p>
<ul>
<li>sintetizza un accordo e ne calcola lo <b>spettro</b> con la FFT;</li>
<li>applica filtri <b>passa-basso, passa-alto, passa-banda</b> moltiplicando lo spettro per una maschera;</li>
<li>separa due "strumenti" mescolati;</li>
<li>confronta tre kernel di convoluzione (box, gaussiana, derivata) nel <b>tempo</b> e in <b>frequenza</b>.</li>
</ul>
<pre>import numpy as np
from scipy import signal
from IPython.display import Audio, display
rng = np.random.default_rng(0)
SR = 22050  # sample rate</pre>
<ul>
<li><b>SR = 22050 Hz</b>: campioni al secondo. Fissa la frequenza di campionamento f<sub>s</sub> e quindi il limite di Nyquist f<sub>s</sub>/2 = 11025 Hz.</li>
<li><code>rng</code> con seme fisso: il rumore è sempre lo stesso, i risultati sono riproducibili.</li>
<li><code>Audio</code> serve solo per ascoltare; per eseguire fuori da Jupyter serve comunque il pacchetto <code>ipython</code>.</li>
</ul>
""", sec=("l4-demo", "demo.ipynb · FFT e filtri sull'audio", 'schede 1–12'), printed=NB1 + 'celle 1–2')

s(2, "Sintesi di un accordo", """
<p>Si costruisce un <b>La minore</b> (A3, C4, E4 a 220, 261.63, 329.63 Hz) come somma di tre sinusoidi pure, più un po' di rumore bianco.</p>
<pre>t = np.arange(int(SR * duration)) / SR
chord = sum(np.sin(2 * np.pi * f * t) for f in note_freqs.values())
chord += 0.15 * rng.standard_normal(chord.shape)
chord /= np.abs(chord).max()</pre>
<ul>
<li><code>t = n / SR</code>: l'asse dei tempi campionato. 2 s a 22050 Hz = <b>44100 campioni</b>.</li>
<li>sin(2πf t) con t = n/f<sub>s</sub> è la sinusoide discreta sin(2π(f/f<sub>s</sub>)n): conta solo il rapporto <b>f/f<sub>s</sub></b> (cicli per campione).</li>
<li>Il rumore gaussiano ha spettro piatto: servirà a vedere il "pavimento" nello spettro in scala log.</li>
<li>La normalizzazione per il massimo porta il segnale in [−1, 1], il range che si aspetta la riproduzione audio. È un semplice fattore di scala: non cambia la forma dello spettro, solo l'ampiezza.</li>
</ul>
""", printed=NB1 + 'celle 3–5')

s(3, "Forma d'onda: il tempo nasconde le frequenze", """
<p>La funzione <code>plot_waveform</code> mostra l'intero segnale (2 s) e i primi 500 campioni (circa 23 ms).</p>
<p><b>Figura:</b> a sinistra una fascia uniforme da cui non si capisce nulla; a destra un'oscillazione irregolare, con un inviluppo che cresce e cala e un po' di rumore sovrapposto.</p>
<ul>
<li>La somma di sinusoidi a frequenze vicine produce <b>battimenti</b>: l'ampiezza complessiva oscilla alla frequenza differenza (es. 261.63 − 220 ≈ 42 Hz).</li>
<li>Dal grafico nel tempo è impossibile dire <b>quali</b> e <b>quante</b> frequenze ci sono. È la motivazione della FFT: cambiare base (L3) e guardare il segnale come somma di sinusoidi.</li>
</ul>
""", img='img/demo_waveform.png', printed=NB1 + 'celle 6–7')

s(4, "FFT di un segnale reale: rfft e rfftfreq", """
<pre>X = np.fft.rfft(chord)                        # spettro complesso
freqs = np.fft.rfftfreq(len(chord), d=1/SR)   # asse in Hz
magnitude = np.abs(X)</pre>
<p>Output: 44100 campioni in ingresso, <b>22051</b> in uscita, risoluzione <b>0.5 Hz/bin</b>, frequenza massima <b>11025 Hz</b>.</p>
<ul>
<li><b>rfft</b>: per un segnale reale la DFT ha <b>simmetria hermitiana</b>, X[N−k] = X[k]<sup>*</sup> (L3). La metà negativa è ridondante, quindi <code>rfft</code> restituisce solo i bin da 0 (DC) a N/2 (Nyquist): <b>N/2 + 1</b> valori.</li>
<li><b>rfftfreq</b>: il bin k corrisponde a f<sub>k</sub> = k · f<sub>s</sub> / N. Senza <code>d=1/SR</code> l'asse sarebbe in cicli per campione (0…0.5).</li>
<li><b>Risoluzione</b> Δf = f<sub>s</sub>/N = 1/durata = 1/2 s = 0.5 Hz. Per risolvere frequenze più vicine serve un segnale <b>più lungo</b>, non una f<sub>s</sub> più alta.</li>
<li><b>Nyquist</b>: l'ultimo bin è f<sub>s</sub>/2. Frequenze sopra non sono rappresentabili (si ripiegano: aliasing, L6).</li>
<li><code>np.abs</code> è la magnitudine, <code>np.angle</code> la fase.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Dato N e f<sub>s</sub>: numero di bin di rfft (N/2 + 1 se N è pari), Δf = f<sub>s</sub>/N, frequenza del bin k = k·Δf, frequenza massima f<sub>s</sub>/2. Qui: 44100 → 22051 bin, Δf = 0.5 Hz, A3 = 220 Hz cade nel bin 440.</p></div>
<div class="box b"><b>Dal libro · cap. 16, § 16.5 The Discrete Fourier Transform</b>
<p>Il libro definisce la DFT senza fattori davanti e mette 1/N nell'<b>inversa</b>, la stessa convenzione di numpy:</p>
<span class="f">L[u] = ∑<sub>n=0</sub><sup>N−1</sup> ℓ[n] e<sup>−2πj un/N</sup>  ·  ℓ[n] = (1/N) ∑<sub>u=0</sub><sup>N−1</sup> L[u] e<sup>+2πj un/N</sup></span>
<ul>
<li>L'indice u conta i <b>cicli contenuti nella finestra</b> di N campioni: la frequenza in cicli per campione è u/N, in Hz u·f<sub>s</sub>/N. È esattamente ciò che fa <code>rfftfreq</code>.</li>
<li>Le esponenziali complesse sono ortogonali, con ⟨e<sub>u</sub>, e<sub>u'</sub>⟩ = N·δ[u − u']: la DFT è solo un <b>cambio di base</b> invertibile (§ 16.2), la FFT (Cooley–Tukey) lo calcola in O(N log N) invece di O(N<sup>2</sup>).</li>
<li>Conseguenza della convenzione: un coseno di ampiezza A che fa u<sub>0</sub> cicli nella finestra dà due righe, in u<sub>0</sub> e in N − u<sub>0</sub>, alte A·N/2 ciascuna (metà dell'energia per parte). <code>rfft</code> tiene solo la prima: da qui il picco ≈ A·N/2 della scheda 5.</li>
<li>Plancherel (§ 16.7.3): ∑|ℓ[n]|<sup>2</sup> = (1/N) ∑|L[u]|<sup>2</sup>. L'energia si conserva a meno del fattore 1/N.</li>
</ul>
<p><a href="https://visionbook.mit.edu/image_processing_fourier.html">visionbook.mit.edu · cap. 16</a></p></div>
""", printed=NB1 + 'celle 8–9')

s(5, "Spettro in scala lineare e logaritmica", """
<p><b>Figura:</b> tre picchi netti alle frequenze delle note (linee rosse). In scala lineare il rumore è invisibile; in scala log compare un pavimento di rumore piatto intorno a 10, circa tre ordini di grandezza sotto i picchi.</p>
<ul>
<li>La scala log è quella standard anche per gli spettri delle immagini: la dinamica è enorme e in lineare si vedrebbe solo la DC.</li>
<li><b>Ampiezza dei picchi</b>: numpy non normalizza la FFT diretta, quindi una sinusoide di ampiezza A dà un picco di circa <b>A · N/2</b>. Qui A = 1/3.24 (dopo la normalizzazione) e N/2 = 22050: picco ≈ 6800, come nel grafico. Per leggere l'ampiezza vera si divide per N/2.</li>
</ul>
<div class="box x"><b>Approfondimento: spectral leakage</b><p>Il picco di A3 vale circa 6810, quelli di C4 ed E4 circa 6070, anche se le tre sinusoidi hanno la stessa ampiezza, e in scala log C4 ed E4 hanno "gonne" larghe. Motivo: 220 Hz cade esattamente sul bin 440, mentre 261.63 Hz cade a 523.26 bin, fra due bin. La DFT tratta il segnale come periodico (L3); se la finestra non contiene un numero intero di periodi c'è un salto al bordo e l'energia si <b>spalma</b> sui bin vicini. È lo stesso motivo per cui nello spettro di un'immagine compaiono le croci lungo gli assi.</p></div>
<div class="box b"><b>Dal libro · cap. 16, § 16.6.3 Box Function e § 16.7.5 Dual Convolution</b>
<p>Il libro dà gli strumenti per fare il conto del leakage, anche se non lo chiama così:</p>
<ul>
<li>Un segnale di 2 s è una sinusoide infinita <b>moltiplicata per un box</b> (la finestra di osservazione).</li>
<li>Prodotto nel tempo = <b>convoluzione in frequenza</b> (dual convolution, § 16.7.5): ogni riga della sinusoide viene sostituita da una copia della trasformata del box.</li>
<li>La trasformata del box è la <b>sinc discreta</b> (§ 16.6.3), che vale 1 al centro e ha zeri a distanza di un bin.</li>
</ul>
<span class="f">|picco| / (A·N/2) ≈ |sin(πδ) / (πδ)|, δ = distanza della frequenza vera dal bin più vicino</span>
<p>Per A3, δ = 0: i bin campionano la sinc proprio sugli zeri, niente leakage. Per C4, 261.63 Hz = bin 523.26, δ = 0.26: il picco scende a 0.89 (verificato, 6070/6810 = 0.89) e gli altri bin campionano i lobi laterali, che sono le "gonne" in scala log. Moltiplicare prima per una finestra liscia (Hann) sostituisce la sinc con una trasformata dai lobi molto più bassi.</p>
<p><a href="https://visionbook.mit.edu/image_processing_fourier.html">visionbook.mit.edu · cap. 16</a></p></div>
""", img='img/demo_spectrum.png', printed=NB1 + 'celle 10–11')

s(6, "Filtrare in frequenza: rfft, maschera, irfft", """
<pre>def freq_filter(x, sr, mask_fn):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), d=1/sr)
    return np.fft.irfft(X * mask_fn(f), n=len(x))</pre>
<ul>
<li>Tre passi: <b>trasformata</b>, <b>moltiplicazione</b> per una maschera reale H(f), <b>antitrasformata</b>.</li>
<li>Per il <b>teorema di convoluzione</b> (L3) moltiplicare gli spettri equivale a convolvere nel tempo con h = IDFT(H). Qui si progetta il filtro direttamente in frequenza.</li>
<li><code>n=len(x)</code> in <code>irfft</code> serve: da N/2 + 1 bin non si sa se N era pari o dispari. Senza, per N dispari si ottiene un campione in meno.</li>
<li>La maschera è reale e simmetrica, quindi non introduce sfasamenti (filtro a fase zero) e l'uscita è reale.</li>
</ul>
<div class="box x"><b>Approfondimento: la convoluzione è circolare</b><p>Moltiplicare DFT corrisponde a una convoluzione <b>circolare</b> (L3, matrice circolante): l'inizio e la fine del segnale si "toccano". Con 2 s di sinusoidi stazionarie non si vede, ma su segnali con transitori il filtro può trascinare energia dalla fine all'inizio. Come dice il notebook, i sistemi audio reali filtrano a blocchi o nel tempo.</p></div>
<div class="box b"><b>Dal libro · cap. 15, § 15.4.4 Circular Convolution; cap. 16, § 16.7.4 Convolution</b>
<p>Il teorema di convoluzione del libro è enunciato per la convoluzione <b>circolare</b> ∘<sub>N</sub>, in cui gli indici si prendono modulo N:</p>
<span class="f">(h ∘<sub>N</sub> ℓ)[n] = ∑<sub>k=0</sub><sup>N−1</sup> h[(n − k)<sub>N</sub>] ℓ[k]  ⟶  DFT: H[u] · L[u]</span>
<ul>
<li>È una scelta di <b>condizione al bordo</b>: il segnale finito viene esteso come periodico (circular padding, § 15.4.3).</li>
<li>Per ottenere con la FFT la convoluzione lineare (quella di <code>np.convolve</code>, modo full) basta allungare entrambi i segnali con zeri fino a N ≥ len(x) + len(h) − 1: così il "giro" cade negli zeri (esercizio 5 della guida).</li>
<li>Il libro nota anche il costo: con la FFT la convoluzione diventa O(N log N), conveniente per kernel lunghi.</li>
</ul>
<p><a href="https://visionbook.mit.edu/linear_image_filtering.html">cap. 15</a> · <a href="https://visionbook.mit.edu/image_processing_fourier.html">cap. 16</a></p></div>
""", printed=NB1 + 'celle 12–13')

s(7, "Passa-basso, passa-alto, passa-banda", """
<pre>chord_lp = freq_filter(chord, SR, lambda f: (f &lt;= 240).astype(float))
chord_hp = freq_filter(chord, SR, lambda f: (f &gt;= 300).astype(float))
chord_bp = freq_filter(chord, SR, lambda f: ((f &gt;= 245) &amp; (f &lt;= 280)).astype(float))</pre>
<ul>
<li><b>Passa-basso</b> (≤ 240 Hz): resta solo A3. Suono "ovattato", come attraverso un muro. <b>Figura:</b> spettro in log dopo il passa-basso: sotto 240 Hz il rumore resta, sopra lo spettro crolla a ~10<sup>−13</sup>, cioè zero numerico.</li>
<li><b>Passa-alto</b> (≥ 300 Hz): restano E4 e il rumore. Il notebook dice "upper harmonics", ma le note sono sinusoidi pure senza armoniche: restano la <b>nota più alta</b> e il rumore.</li>
<li><b>Passa-banda</b> (245–280 Hz): isola C4. Funziona perché le note distano circa 42 Hz e la banda contiene C4 e nessun'altra nota; con risoluzione 0.5 Hz/bin la banda comprende 70 bin.</li>
<li>Le maschere sono <b>ideali</b> (0/1, bordo netto). Nel tempo corrispondono a una sinc, che ha code lunghe e produce <b>ringing</b> sulle transizioni brusche (fenomeno di Gibbs). Qui non si nota perché le sinusoidi sono stazionarie; su un impulso rettangolare sì (vedi scheda 11).</li>
</ul>
""", img='img/demo_lowpass.png', printed=NB1 + 'celle 14–19')

s(8, "Separare due sorgenti mescolate", """
<p>Si aggiunge una "melodia" (D5 = 587 Hz, E5 = 659 Hz) all'accordo e si prova a separarle con un taglio in frequenza.</p>
<pre>mix = 0.5 * chord + 0.5 * melody
recovered_chord  = freq_filter(mix, SR, lambda f: (f &lt;= 400).astype(float))
recovered_melody = freq_filter(mix, SR, lambda f: (f &gt;= 500).astype(float))</pre>
<p><b>Figura:</b> lo spettro del mix ha cinque picchi; il passa-basso tiene i tre sotto 400 Hz, il passa-alto i due sopra 500 Hz.</p>
<ul>
<li>Funziona perché le due sorgenti occupano <b>bande disgiunte</b>: è l'idea dell'equalizzazione in un mix musicale.</li>
<li>Non è perfetta: il rumore dell'accordo sopra 500 Hz finisce nella "melodia". Se due sorgenti si sovrappongono in frequenza, un filtro lineare non le separa.</li>
<li>Il commento del notebook parla di "band-pass", ma in codice sono un passa-basso e un passa-alto.</li>
</ul>
""", img='img/demo_separation.png', printed=NB1 + 'celle 20–22')

s(9, "np.convolve e le modalità full, same, valid", """
<p>Segnale di prova: un <b>impulso rettangolare</b> (campioni 20–39 a 1) con rumore, 60 campioni.</p>
<pre>np.convolve(x, h, mode='full')   # len(x)+len(h)-1 = 66
np.convolve(x, h, mode='same')   # len(x) = 60, centrata
np.convolve(x, h, mode='valid')  # len(x)-len(h)+1 = 54</pre>
<ul>
<li><b>full</b>: tutte le posizioni in cui kernel e segnale si sovrappongono almeno in parte (zero-padding implicito). È la definizione della L3.</li>
<li><b>same</b>: la parte centrale di full, lunga quanto l'ingresso. Con kernel di lunghezza dispari è centrata esattamente; con lunghezza pari c'è uno sfasamento di mezzo campione.</li>
<li><b>valid</b>: solo le posizioni con sovrapposizione completa, niente effetti di bordo.</li>
<li>Sono le stesse scelte di <code>padding</code> di una CNN: cambiano la dimensione dell'uscita e, se non centrate, spostano il risultato.</li>
<li><code>np.convolve</code> fa una vera <b>convoluzione</b>: ribalta il kernel. Conta per i kernel non simmetrici (scheda 10).</li>
</ul>
<div class="box b"><b>Dal libro · cap. 15, § 15.4.1 Properties e § 15.4.3 Handling Boundaries</b>
<ul>
<li><b>Supporto</b>: un segnale di lunghezza N convoluto con un kernel di lunghezza M dà al più N + M − 1 campioni non nulli: è la lunghezza di <code>full</code>.</li>
<li><b>Identità</b>: δ ∘ ℓ = ℓ, e un impulso spostato δ[n − n<sub>0</sub>] trasla il segnale (fig. 15.9).</li>
<li>Per <code>same</code> bisogna inventare i valori oltre il bordo. Il libro elenca quattro scelte: <b>zero padding</b> (il default delle reti neurali, scurisce i bordi), <b>circolare</b> (il segnale diventa periodico), <b>mirror</b> (riflessione) e <b>repeat</b> (si ripete il campione di bordo). Confrontandole con un box 11×11 (fig. 15.10) il mirror dà l'errore più piccolo e lo zero padding il più grande.</li>
<li><code>np.convolve</code> offre solo lo zero padding; per le altre si usa <code>np.pad(x, k, mode='reflect'|'edge'|'wrap')</code> e poi <code>mode='valid'</code>.</li>
</ul>
<p><a href="https://visionbook.mit.edu/linear_image_filtering.html">visionbook.mit.edu · cap. 15</a></p></div>
""", img='img/demo_pulse.png', printed=NB1 + 'celle 23–26')

s(10, "Tre kernel nel tempo: box, gaussiana, derivata", """
<pre>box   = np.ones(7) / 7
gauss = signal.windows.gaussian(15, std=2.5); gauss /= gauss.sum()
deriv = np.array([-1, 0, 1]) / 2.0
x_deriv = np.convolve(x, deriv, mode='same')</pre>
<ul>
<li><b>Box</b> e <b>gaussiana</b> sono normalizzati a somma 1: guadagno in DC = 1, la media del segnale non cambia (L5).</li>
<li>La finestra gaussiana a 15 campioni con σ = 2.5 copre ±2.8σ: il troncamento è trascurabile.</li>
<li><b>Figura:</b> il box dà fronti a rampa lineare lunga 7 campioni e riduce il rumore; la gaussiana dà fronti morbidi a S; la derivata vale circa zero sui tratti piatti e ha due picchi sui fronti, più il rumore amplificato.</li>
</ul>
<div class="box w"><b>Attenzione: la "derivata" ha il segno sbagliato</b>
<p>Nella figura il fronte di <b>salita</b> (campione 20) dà un picco <b>negativo</b> (−0.5) e quello di discesa un picco positivo. Motivo: <code>np.convolve</code> ribalta il kernel, quindi con h = [−1, 0, 1]/2 calcola</p>
<span class="f">y[n] = (x[n−1] − x[n+1]) / 2 = −(derivata centrale)</span>
<p>Verificato eseguendo: <code>x_deriv[19:21] = [−0.5, −0.5]</code>. Correzione: <code>deriv = np.array([1, 0, -1]) / 2</code> con <code>np.convolve</code>, oppure tenere [−1, 0, 1] e usare <code>np.correlate</code>. È esattamente la differenza convoluzione/cross-correlazione del notebook 15lif e dell'esempio "flip h" della L3.</p></div>
<div class="box b"><b>Dal libro · cap. 19, § 19.4 Temporal filters</b>
<p>Quando la variabile è il <b>tempo</b> (audio, video) conta una proprietà che nelle immagini non esiste: la <b>causalità</b>.</p>
<ul>
<li>Filtro <b>causale</b>: h[t] = 0 per t &lt; 0, l'uscita usa solo presente e passato. Solo questi si possono applicare in tempo reale.</li>
<li>I kernel del notebook, usati con <code>mode='same'</code>, sono <b>centrati</b>, quindi non causali: usano anche campioni futuri. Per renderli causali il libro dice di troncarli e spostarli in avanti, pagando un <b>ritardo</b> (qui 3 campioni per il box, 7 per la gaussiana).</li>
<li>La derivata temporale del libro è la differenza all'indietro ℓ[t] − ℓ[t − 1], causale, invece della differenza centrale.</li>
<li>Filtri <b>ricorsivi</b> (IIR): ℓ<sub>out</sub>[t] = ℓ<sub>in</sub>[t] + α ℓ<sub>out</sub>[t − 1] ha risposta all'impulso α<sup>t</sup> u[t], infinita; è stabile solo se |α| &lt; 1. È lo smoothing esponenziale, il modo economico di fare un passa-basso in tempo reale.</li>
</ul>
<p>Questo spiega la frase del notebook sui sistemi audio reali che non fanno fft, maschera, ifft: serve un filtro causale a bassa latenza.</p>
<p><a href="https://visionbook.mit.edu/temporal_filters_v2.html">visionbook.mit.edu · cap. 19</a></p></div>
""", img='img/demo_kernels_time.png', printed=NB1 + 'celle 27–31')

s(11, "Kernel in frequenza: la risposta in frequenza", """
<pre>N = 256
bins = np.fft.rfftfreq(N)               # 0 ... 0.5 cicli/campione
kpad = np.zeros(N); kpad[:len(k)] = k   # zero-padding
H = np.abs(np.fft.rfft(kpad))</pre>
<ul>
<li>Per il teorema di convoluzione y = x ∗ h ⇒ Y = X · H: la DFT del kernel è la sua <b>risposta in frequenza</b>, dice quanto viene tenuta ogni frequenza.</li>
<li><b>Zero-padding</b> a 256: non aggiunge informazione, campiona più fitto la stessa DTFT, quindi la curva è liscia.</li>
<li>Il kernel è messo all'inizio e non centrato: cambia solo la fase (teorema di traslazione), la magnitudine è la stessa.</li>
<li><b>Figura:</b> box con lobi laterali fino al 23% (e zeri); gaussiana liscia e monotona, praticamente zero oltre 0.2; derivata a campana nulla in 0 <b>e</b> in 0.5, con picco a 0.25.</li>
</ul>
<div class="box w"><b>Attenzione: la derivata centrale non è un passa-alto</b>
<p>Il notebook dice che la risposta di [−1, 0, 1]/2 "cresce verso Nyquist". Non è vero, e lo mostra la sua stessa figura:</p>
<span class="f">|H(f)| = |sin(2πf)|, f in cicli/campione</span>
<p>è zero in DC e zero a Nyquist (f = 0.5, dove [1, −1, 1, −1…] dà x[n+1] − x[n−1] = 0), massima a f = 0.25: è un <b>passa-banda</b>. La derivata ideale ha |H| = 2πf; la differenza centrale la approssima solo alle basse frequenze e in più smussa, per questo è meno sensibile al rumore più fine. La differenza in avanti [1, −1] ha invece |H| = 2|sin(πf)|, crescente fino a Nyquist: quella sì è un passa-alto. Collegamento con L5 (d<sub>0</sub> e d<sub>1</sub>).</p></div>
<div class="box b"><b>Dal libro · cap. 16, § 16.6.3 Box Function e § 16.10 Fourier Analysis of Linear Filters</b>
<p>La risposta in frequenza H[u] del kernel è la sua <b>funzione di trasferimento</b>: |H| è il guadagno a ogni frequenza, ∠H lo sfasamento, |H[0]| il guadagno in DC. Il libro classifica i filtri in <b>passa-basso, passa-banda, passa-alto</b> guardando |H| (fig. 16.17): è il criterio con cui la differenza centrale risulta un passa-banda.</p>
<p>Per un box di 2L + 1 campioni il libro dà la forma chiusa (sinc discreta):</p>
<span class="f">Box<sub>L</sub>[u] = sin(πu(2L + 1)/N) / sin(πu/N)</span>
<p>Con L = 3 (7 campioni) e normalizzato a somma 1, in cicli per campione f = u/N: |H(f)| = |sin(7πf) / (7 sin(πf))|. Primo zero a f = 1/7 ≈ 0.143, lobo laterale più alto 0.233 (il 23% della figura) intorno a f ≈ 0.21, e a Nyquist |H(0.5)| = 1/7 ≈ 0.143 (la gaussiana arriva a 0.0015, la differenza centrale a 0). Più il box è largo nel tempo, più la sinc è stretta in frequenza (fig. 16.10: supporto largo in un dominio, stretto nell'altro).</p>
<p><a href="https://visionbook.mit.edu/image_processing_fourier.html">visionbook.mit.edu · cap. 16</a></p></div>
<div class="box w"><b>Attenzione: il box non produce ringing nel tempo</b>
<p>Il notebook dice che i lobi laterali del box "nel tempo appaiono come ringing sui bordi". Un kernel a valori tutti ≥ 0 e somma 1 fa una media pesata: l'uscita non può superare il massimo né scendere sotto il minimo dell'ingresso, quindi sul gradino dà una rampa monotona, senza oscillazioni (lo si vede nella figura della scheda 10). I lobi laterali significano altro: le alte frequenze <b>non sono tolte bene</b> e, dove il lobo è negativo, sono tenute con <b>segno invertito</b> (una trama fine può uscire con contrasto invertito, L5). Il ringing vero viene da un taglio netto in frequenza, cioè dalle maschere ideali delle schede 7–8: su questo impulso sovraelonga dell'11% (figura nella guida allo studio). Anche la L5 usa "ringing" in senso lato per il box.</p></div>
""", img='img/demo_kernels_freq.png', printed=NB1 + 'celle 32–34')

s(12, "Riepilogo API ed esercizi", """
<ul>
<li>FFT di un segnale reale: <code>np.fft.rfft(x)</code>, inversa <code>np.fft.irfft(X, n=len(x))</code>.</li>
<li>Asse delle frequenze: <code>np.fft.rfftfreq(n, d=1/SR)</code>.</li>
<li>Convoluzione: <code>np.convolve(x, h, mode='same')</code>. Ricorda che ribalta h.</li>
<li>Finestra gaussiana: <code>scipy.signal.windows.gaussian(M, std=s)</code> (va normalizzata a mano).</li>
<li>Ascolto: <code>IPython.display.Audio(array, rate=SR)</code>.</li>
</ul>
<p><b>Esercizi proposti:</b> costruire altri segnali e trovarne le frequenze dominanti; separare più sorgenti; progettare a mano un filtro per ripulire una registrazione vocale rumorosa (campioni su samplefocus.com).</p>
<div class="box k"><b>Da saper fare</b><p>Leggere uno spettro: dove sono i picchi (in Hz), perché in log compare il pavimento di rumore, che cosa tiene ciascuna maschera. Dire per ogni kernel se è passa-basso, passa-banda o passa-alto guardando la sua risposta in frequenza.</p></div>
""", printed=NB1 + 'celle 35–37')

# ---------------------------------------------------------------- classification.ipynb

s(13, "Free Spoken Digit Dataset: caricamento", """
<p>Secondo notebook: lo spettro non serve solo a filtrare ma anche a <b>descrivere</b> un segnale, cioè come feature per classificare. Compito: riconoscere la cifra (0–9) pronunciata.</p>
<ul>
<li><b>FSDD</b>: 3000 file WAV a 8 kHz, 6 speaker × 10 cifre × 50 ripetizioni. Non è nella cartella del corso: va scaricato (<code>git clone https://github.com/Jakobovski/free-spoken-digit-dataset</code>). Il notebook lo cerca in <code>../data/free-spoken-digit-dataset-master/recordings</code>, cioè <code>Lessons/L4/data/…</code> accanto a <code>lab/</code>; altrimenti si adatta <code>FSDD_PATH</code>.</li>
<li>Nome file <code>{cifra}_{speaker}_{indice}.wav</code>: etichetta e speaker si leggono dal nome.</li>
</ul>
<pre>sr, data = wavfile.read(path)
data = data.astype(np.float32) / np.iinfo(data.dtype).max   # int16 -&gt; [-1, 1]
if len(data) &lt; target_len:
    data = np.pad(data, (0, target_len - len(data)))
else:
    data = data[:target_len]</pre>
<ul>
<li>I WAV sono <b>int16</b>: dividere per 32767 porta in [−1, 1]. Funziona solo per file interi (<code>np.iinfo</code> su float darebbe errore); per FSDD va bene, verificato su tutti i 3000 file.</li>
<li>Ogni clip è portata a <b>8000 campioni = 1 s</b> con zeri in coda: così tutte le FFT hanno la stessa lunghezza e lo stesso asse (4001 bin da 0 a 4000 Hz, Δf = 1 Hz).</li>
<li>Le clip durano da 0.14 s a 2.3 s (mediana 0.42 s): 20 clip su 3000 vengono <b>troncate</b> a 1 s, la maggior parte è per più di metà silenzio aggiunto. Conta per la ZCR (scheda 15).</li>
<li><code>sr</code> viene letto ma ignorato: si assume 8 kHz, vero per FSDD.</li>
</ul>
<p>Notebook rieseguito per intero con il dataset scaricato: tutti i numeri stampati coincidono con gli output salvati (3000 clip, 300 per cifra, stesse accuratezze).</p>
""", sec=("l4-classif", "classification.ipynb · feature spettrali e k-NN", 'schede 13–20'), printed=NB2 + 'celle 1–5')

s(14, "Forme d'onda e spettri per cifra", """
<p>Si ascolta un esempio per cifra e se ne disegnano forma d'onda e spettro (lineare e log).</p>
<pre>freqs = np.fft.rfftfreq(TARGET_LEN, d=1/TARGET_SR)   # 0 ... 4000 Hz
mag = np.abs(np.fft.rfft(clips[idx]))
ax.semilogy(freqs, mag + 1e-6)</pre>
<ul>
<li>Nel tempo: cifre più corte e più lunghe, alcune con transitori netti (sibilanti: "six", "seven"), altre più morbide.</li>
<li><b>Figura (spettri in log):</b> tutti hanno energia concentrata sotto ~1000 Hz (fondamentale della voce e prime armoniche, i picchi regolari) e una coda fino a 4000 Hz che cala al bordo. Le differenze fra cifre sono nella <b>distribuzione</b> dell'energia fra bande (per esempio 6 e 7 hanno relativamente più energia fra 2000 e 3500 Hz).</li>
<li><code>+ 1e-6</code> evita log(0) nei punti in cui lo spettro è nullo.</li>
<li>4000 Hz è la frequenza di Nyquist per f<sub>s</sub> = 8 kHz: la banda telefonica, sufficiente per capire le parole.</li>
</ul>
""", img='img/cls_logspectra.png', printed=NB2 + 'celle 6–11')

s(15, "Tre feature spettrali: centroide, rolloff, ZCR", """
<p>Invece di 4001 numeri per clip, tre misure della "brillantezza" (contenuto ad alta frequenza).</p>
<pre>def spectral_centroid(x, sr):
    mag = np.abs(np.fft.rfft(x)); f = np.fft.rfftfreq(len(x), d=1/sr)
    return np.sum(f * mag) / (np.sum(mag) + 1e-8)

def spectral_rolloff(x, sr, threshold=0.85):
    cumulative = np.cumsum(mag)
    idx = np.searchsorted(cumulative, threshold * cumulative[-1])
    return f[min(idx, len(f) - 1)]

def zero_crossing_rate(x):
    return np.mean(np.abs(np.diff(np.sign(x))) / 2)</pre>
<ul>
<li><b>Centroide</b>: baricentro dello spettro, ∑ f<sub>k</sub>|X<sub>k</sub>| / ∑ |X<sub>k</sub>|. In Hz.</li>
<li><b>Rolloff</b>: la frequenza sotto cui sta l'85% dello spettro cumulato. <code>searchsorted</code> trova il primo indice in cui la somma cumulata supera la soglia.</li>
<li><b>ZCR</b>: frazione di coppie di campioni consecutivi con cambio di segno. Per una sinusoide a frequenza f vale circa 2f/f<sub>s</sub>: è una stima della frequenza <b>nel tempo</b>, senza FFT.</li>
<li>Range ottenuti: centroide 572–2218 Hz, rolloff 717–3669 Hz, ZCR 0.014–0.425.</li>
</ul>
<div class="box w"><b>Attenzione: la ZCR misura soprattutto la durata</b>
<p>La ZCR è calcolata sulla clip riempita di zeri fino a 1 s: nel silenzio aggiunto non ci sono attraversamenti, ma la media li conta. Una clip di 0.3 s ha la ZCR divisa per circa 3. Verificato: correlazione fra ZCR e durata della clip = 0.69 (0.25 calcolandola solo sulla clip originale), e in media la ZCR è il 44% di quella vera, esattamente la durata media. Correzione: calcolarla sul segnale originale, prima del padding (<code>zero_crossing_rate(data[:8000])</code> dentro il loop di caricamento).</p></div>
<div class="box w"><b>Attenzione: il rolloff non usa l'energia</b>
<p>Il testo dice "85% dell'energia", ma il codice somma la <b>magnitudine</b> |X|, non l'energia |X|<sup>2</sup>. Non è un dettaglio: con |X|<sup>2</sup> il rolloff mediano scende da 2128 Hz a 668 Hz, perché l'energia è molto concentrata sulle basse frequenze. Correzione: <code>cumulative = np.cumsum(mag**2)</code>. Una prova su un solo segnale sintetico (dove la differenza è di pochi Hz) non basta a dire che l'effetto è trascurabile: sulle clip vere lo è tutt'altro. Con le due correzioni il k-NN a 3 feature sale da 49.7% a 57.5% (split casuale) e da 28.7% a 37.5% (speaker escluso).</p></div>
""", printed=NB2 + 'celle 12–13')

s(16, "Scatter plot e pair plot delle feature", """
<p><b>Figura:</b> centroide contro rolloff, un punto per clip, colore = cifra. I punti formano una banda curva unica: le due feature sono <b>fortemente correlate</b> (entrambe misurano la stessa cosa). Le cifre sono in parte separate lungo la banda (il 4 in basso a sinistra, il 2 e il 6 in alto) ma molto sovrapposte.</p>
<ul>
<li>Il <b>pair plot</b> (celle 16–17) fa lo stesso per tutte le coppie; sulla diagonale gli istogrammi per cifra. La ZCR separa bene soprattutto il 6 ("six", sibilanti: ZCR alta).</li>
<li>Messaggio: tre numeri che misurano la "brillantezza" non bastano per 10 classi. Ci si aspetta un classificatore sopra il caso (10%) ma lontano dal 100%.</li>
</ul>
""", img='img/cls_scatter.png', printed=NB2 + 'celle 14–17')

s(17, "k-NN: 3 feature contro spettro completo", """
<pre>X_norm = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)
X_train, X_test, y_train, y_test = train_test_split(
    X_norm, labels, test_size=0.2, random_state=0, stratify=labels)
knn = KNeighborsClassifier(n_neighbors=5).fit(X_train, y_train)</pre>
<ul>
<li><b>Standardizzazione</b> a media 0 e varianza 1: il k-NN usa la distanza euclidea, e senza scalare le feature in Hz (migliaia) schiaccerebbero la ZCR (decimi).</li>
<li><b>k-NN, k = 5</b>: la classe è il voto dei 5 esempi di training più vicini. Nessun addestramento vero.</li>
<li>3 feature: train 63.8%, <b>test 49.8%</b>.</li>
<li>Aggiungendo lo <b>spettro log</b> intero (log(|X| + 1), 4001 valori): train 92.9%, <b>test 88.0%</b>.</li>
<li>Il log comprime la dinamica, come nei grafici: senza, le distanze sarebbero dominate dai pochi picchi più alti. Il +1 evita log(0).</li>
<li>Con 4004 dimensioni standardizzate le tre feature iniziali pesano pochissimo nella distanza: il risultato è praticamente quello del solo spettro.</li>
</ul>
<div class="box w"><b>Attenzione: scaler stimato anche sul test</b>
<p>Media e deviazione standard sono calcolate su tutte le 3000 clip prima dello split: il test set influenza la normalizzazione (data leakage). Qui l'effetto è trascurabile (con lo scaler stimato solo sul training, dentro una <code>make_pipeline</code>, si ottengono 49.7% e 88.2%), ma la procedura corretta è quella della cella 24: <code>make_pipeline(StandardScaler(), KNeighborsClassifier(5))</code>.</p></div>
""", printed=NB2 + 'celle 18–20')

s(18, "Matrice di confusione", """
<p><b>Figura:</b> matrice 10×10 sul test set (600 clip, 60 per cifra) del k-NN con spettro, accuratezza 88.0%. Diagonale forte; gli errori principali sono 0 scambiato con 3, 2 e 6, e 3 con 2, 0 e 6; il 4 è quasi perfetto (59/60).</p>
<ul>
<li>Riga = classe vera, colonna = predetta. Somma di riga = 60 grazie a <code>stratify=labels</code>.</li>
<li>Le confusioni hanno senso fonetico: "zero" e "three" condividono vocali e parte della struttura spettrale.</li>
</ul>
""", img='img/cls_confusion.png', printed=NB2 + 'celle 21–22')

s(19, "Generalizza a un nuovo speaker?", """
<p>Lo split casuale mette nel test clip di speaker che hanno registrato <b>la stessa cifra altre 40 volte</b> nel training: il vicino più prossimo è quasi sempre la stessa persona che dice la stessa cosa. Un sistema reale deve funzionare con voci mai sentite.</p>
<pre>model = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=5))
per_speaker = cross_val_score(model, features, labels,
                              groups=speakers, cv=LeaveOneGroupOut())</pre>
<ul>
<li><b>Leave-one-speaker-out</b>: 6 fold, ognuno allena su 5 speaker e testa sul sesto. La pipeline stima lo scaler solo sul training.</li>
<li>Risultati: 3 feature <b>28.7%</b>, 3 feature + spettro <b>32.2%</b> in media, contro 49.7% e 88.2% dello split casuale.</li>
<li><b>Figura:</b> barre per speaker molto diverse (george quasi al caso; con lo spettro lucas e yweweler arrivano vicino al 50%, nicolas e theo scendono sotto le 3 feature); le linee tratteggiate dello split casuale sono molto più in alto.</li>
</ul>
<div class="box k"><b>Da saper spiegare</b><p>Lo spettro dell'intera clip codifica anche la <b>voce</b> (altezza, timbro), il volume, il microfono e la stanza. Nello split casuale il k-NN sfrutta questi indizi, perché i vicini sono dello stesso speaker; con lo speaker escluso non servono più e resta solo la parte legata alla parola. È un esempio di <b>shortcut</b> e di valutazione ottimistica: stesso rischio con le immagini (stesso fotografo, stessa camera, stesso sfondo fra training e test).</p></div>
""", img='img/cls_loso.png', printed=NB2 + 'celle 23–25')

s(20, "Esercizio: feature invarianti allo speaker", """
<p>Obiettivo: progettare feature che alzino l'accuratezza <b>leave-one-speaker-out</b> (base 32%). Il notebook dice che con sola numpy si arriva intorno al 60%. Gli hint, spiegati:</p>
<ul>
<li><b>Guadagno</b>: moltiplicare il segnale per g moltiplica |X| per g; dopo il log diventa un <b>offset additivo</b> log g. Sottraendo la media del vettore log si toglie.</li>
<li><b>Bande</b>: migliaia di bin rendono i vicini sensibili a piccole differenze di altezza della voce. Mediare la potenza su qualche decina di bande larghe, più fitte alle basse frequenze (scala log, come l'orecchio), è più robusto.</li>
<li><b>Tempo</b>: togliere il silenzio, dividere il parlato in pochi pezzi consecutivi e calcolare le bande per ciascuno. Lo spettro dell'intera clip perde l'<b>ordine</b> dei suoni; i pezzi lo conservano in parte. È l'idea dello spettrogramma e delle MFCC.</li>
</ul>
<p>Verificato: 30 bande log-spaziate fra 60 e 4000 Hz, 4 pezzi con finestra di Hann, log e sottrazione della media danno <b>61.3%</b> leave-one-speaker-out (90.3% casuale). Il codice è nella guida allo studio.</p>
""", printed=NB2 + 'celle 26–28')

# ---------------------------------------------------------------- 15lif.ipynb

s(21, "Convoluzione 1D scritta a mano", """
<p>Terzo notebook ("15" = capitolo 15 del visionbook, <i>linear image filtering</i>): convoluzione e cross-correlazione implementate con i cicli, senza librerie, per vedere gli indici.</p>
<pre>out = np.zeros(l.shape[0] + h.shape[0] - 1)       # modalità full
for n in range(out.shape[0]):
    for k in range(l.shape[0]):
        hidx = n - k
        if hidx &gt;= 0 and hidx &lt; h.shape[0]:
            out[n] += h[hidx] * l[k]</pre>
<ul>
<li>È la definizione della L3: <b>(l ∗ h)[n] = ∑<sub>k</sub> l[k] h[n − k]</b>. L'indice n − k è il ribaltamento del kernel.</li>
<li>L'<code>if</code> equivale a uno <b>zero-padding</b>: fuori dal kernel si somma zero.</li>
<li>Lunghezza di uscita len(l) + len(h) − 1: la modalità <code>full</code> di <code>np.convolve</code>.</li>
<li>Esempio: [1, 2, 3, 4] ∗ [−1, −2, −3] = <b>[−1, −4, −10, −16, −17, −12]</b>, identico a <code>np.convolve</code> (verificato).</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Il conto a mano: ribalta h in [−3, −2, −1], fallo scorrere su l e somma i prodotti. Per esempio out[2] = 1·(−3) + 2·(−2) + 3·(−1) = −10.</p></div>
<div class="box b"><b>Dal libro · cap. 15, § 15.3 Systems e § 15.4 Convolution</b>
<p>Il libro arriva alla convoluzione da due richieste su un sistema:</p>
<ul>
<li><b>Linearità</b> (sovrapposizione e omogeneità): ogni uscita è una combinazione lineare degli ingressi, ℓ<sub>out</sub> = H ℓ<sub>in</sub> con una matrice qualunque, come uno strato fully connected (fig. 15.4).</li>
<li><b>Invarianza alla traslazione</b>: se l'ingresso si sposta, l'uscita si sposta uguale. Motivazione: un oggetto (gli uccelli di fig. 15.5) può stare ovunque, quindi va elaborato allo stesso modo in ogni posizione.</li>
<li>Insieme obbligano i pesi a dipendere solo dalla differenza n − k: h[n, k] = h[n − k]. Questa è la convoluzione, e la matrice H diventa di Toeplitz (circolante nel caso periodico).</li>
</ul>
<p>Notazione: il libro scrive la convoluzione con ∘ (qui e nelle slide ∗) e la correlazione con ⋆. Proprietà: commutativa, associativa, distributiva sulla somma, con δ come elemento neutro. Il ciclo del notebook scorre su l[k] e ribalta h; per la commutatività si potrebbe scorrere su h e ribaltare l con lo stesso risultato.</p>
<p><a href="https://visionbook.mit.edu/linear_image_filtering.html">visionbook.mit.edu · cap. 15</a></p></div>
""", sec=("l4-lif", "15lif.ipynb · convoluzione, correlazione, template matching", 'schede 21–27'), printed=NB3 + 'celle 1–3')

s(22, "Cross-correlazione 1D", """
<pre>out = np.zeros(l.shape[0])        # TODO: boundary
for n in range(out.shape[0]):
    for k in range(h.shape[0]):
        lidx = n + k
        if lidx &gt;= 0 and lidx &lt; l.shape[0]:
            out[n] += h[k] * l[lidx]</pre>
<ul>
<li><b>(h ⋆ l)[n] = ∑<sub>k</sub> h[k] l[n + k]</b>: il kernel scorre <b>senza ribaltamento</b>. È il prodotto scalare fra h e la finestra di l che parte in n.</li>
<li>Stesso esempio: <b>[−14, −20, −11, −4]</b>.</li>
<li>Relazione: cross-correlare con h = convolvere con h ribaltato. Per kernel simmetrici (box, gaussiana) le due coincidono; per quelli antisimmetrici (derivata) cambia il segno, come nella scheda 10.</li>
<li>Le "convoluzioni" delle CNN sono in realtà cross-correlazioni: con pesi appresi il ribaltamento è irrilevante. Il libro (§ 15.5) lo dice esplicitamente.</li>
<li>A differenza della convoluzione, la cross-correlazione <b>non è commutativa né associativa</b> (§ 15.5): h ⋆ l ≠ l ⋆ h in generale. Per questo le catene di filtri si ragionano con la convoluzione.</li>
</ul>
<div class="box x"><b>Approfondimento: dove cade l'uscita</b><p>L'uscita ha la lunghezza del segnale ma <b>non è centrata</b>: out[n] è riferito al primo campione della finestra, non al centro, e lo zero-padding c'è solo a destra. Rispetto a <code>np.correlate(l, h, 'full')</code> = [−3, −8, −14, −20, −11, −4] mancano i primi len(h) − 1 valori. Il "TODO: boundary" del notebook è questo. Conseguenza nel template matching: il picco cade sull'angolo in alto a sinistra del pattern trovato, non sul suo centro.</p></div>
""", printed=NB3 + 'cella 4')

s(23, "Convoluzione e cross-correlazione 2D", """
<p>Le stesse due funzioni in 2D: due indici di uscita (n, m) e due di somma (k, j).</p>
<pre>hidx_n, hidx_m = n - k, m - j                  # convoluzione: ribalta
out[n, m] += h[hidx_n, hidx_m] * l[k, j]

lidx_n, lidx_m = n + k, m + j                  # cross-correlazione
out[n, m] += h[k, j] * l[lidx_n, lidx_m]</pre>
<ul>
<li>Convoluzione in modalità <b>full</b>: uscita (H<sub>l</sub> + H<sub>h</sub> − 1) × (W<sub>l</sub> + W<sub>h</sub> − 1). Cross-correlazione della stessa dimensione dell'immagine.</li>
<li>In 2D il ribaltamento è su <b>entrambi</b> gli assi (rotazione di 180°).</li>
<li>Quattro cicli annidati: costo O(H W k<sup>2</sup>). Va bene per immagini 30×30; per immagini vere si usa <code>scipy.signal.convolve2d</code>, un kernel separabile (L3, L5) o la FFT.</li>
<li>Verificato: coincidono con <code>convolve2d(…, 'full')</code> e con una porzione di <code>correlate2d(…, 'full')</code>.</li>
</ul>
""", printed=NB3 + 'celle 5–6')

s(24, "Kernel triangolo e risposta all'impulso", """
<p>Pattern: un triangolo binario 3×5. Immagine 30×30 nera con due impulsi, in (10, 10) e (15, 20).</p>
<p><b>Figura:</b> a sinistra la convoluzione, con due copie del triangolo <b>dritto</b>; a destra la cross-correlazione, con due triangoli <b>capovolti</b> e spostati in alto a sinistra.</p>
<ul>
<li>Convolvere un impulso restituisce il kernel: è la <b>risposta all'impulso</b> (L3). Un'immagine è una somma di impulsi pesati, quindi la convoluzione "stampa" una copia del kernel in ogni pixel.</li>
<li>Cross-correlare un impulso restituisce il kernel <b>ribaltato</b>. È il modo più semplice per vedere la differenza fra le due operazioni.</li>
<li>Gli spostamenti diversi dipendono dalle convenzioni di bordo delle due funzioni (full contro non centrata, scheda 22). Verificato con un solo impulso in (10, 10): la convoluzione mette il triangolo dritto nelle righe 10–12, colonne 10–14 (angolo in alto a sinistra sull'impulso); la cross-correlazione lo mette capovolto nelle righe 8–10, colonne 6–10 (angolo in basso a destra sull'impulso).</li>
</ul>
<div class="box b"><b>Dal libro · cap. 15, § 15.5 Cross-Correlation Versus Convolution e § 15.6 System Identification</b>
<p>L'esperimento del notebook è quello della fig. 15.11 del libro: un kernel triangolare applicato a pochi pixel accesi dà triangoli dritti con la convoluzione e capovolti con la correlazione.</p>
<p>Il § 15.6 dà il nome al fenomeno: la risposta di un sistema LTI a δ è h stesso, per questo h si chiama <b>risposta all'impulso</b>, e misurarla basta a identificare il sistema. L'esempio del libro è acustico e si lega al notebook audio: la risposta all'impulso di una stanza (un battito di mani registrato in un ristorante, fig. 15.15) contiene il suono diretto più gli echi, h(t) = a<sub>0</sub>δ(t) + a<sub>1</sub>δ(t − T<sub>1</sub>) + …; convolvere qualsiasi suono con h riproduce come lo si sentirebbe in quella stanza.</p>
<p><a href="https://visionbook.mit.edu/linear_image_filtering.html">visionbook.mit.edu · cap. 15</a></p></div>
""", img='img/lif_impulses.png', printed=NB3 + 'celle 7–10')

s(25, "Trovare il pattern con la cross-correlazione", """
<p>Ora l'immagine contiene il triangolo due volte e una volta capovolto (in alto a destra).</p>
<p><b>Figura:</b> immagine; convoluzione; cross-correlazione. Nella cross-correlazione i due triangoli dritti danno un picco netto (valore 9), quello capovolto arriva al massimo a 6. Nella convoluzione i ruoli si invertono: 9 sul capovolto, 6 sui dritti.</p>
<ul>
<li>Il template matching è una <b>cross-correlazione</b>: in ogni posizione calcola il prodotto scalare fra il pattern e la finestra, che è massimo quando la finestra <b>assomiglia</b> al pattern. La convoluzione cerca invece il pattern ribaltato.</li>
<li>Valore del picco: ∑ h<sup>2</sup> = 9 (pattern binario con 9 pixel a 1), esattamente in (10, 10) e (15, 20), cioè sull'<b>angolo in alto a sinistra</b> di ciascun triangolo (ancoraggio della scheda 22). Nel punto (5, 20) del triangolo capovolto vale 5; il 6 è il massimo nei dintorni, in riga 4.</li>
<li>La convoluzione ha il suo 9 in (7, 24): è il triangolo capovolto, con l'indice spostato di (2, 4) = dimensioni del kernel meno 1, perché l'uscita full parte da −(M − 1).</li>
<li>Il libro (fig. 15.11 e–g) fa lo stesso confronto: massimi della convoluzione sui triangoli rovesciati, della correlazione su quelli dritti.</li>
<li>È <b>invariante alla traslazione</b> (è un operatore LSI) ma non alla scala, alla rotazione o all'illuminazione.</li>
</ul>
""", img='img/lif_pattern.png', printed=NB3 + 'celle 11–12')

s(26, "Template matching normalizzato", """
<p>Problema: la cross-correlazione non è normalizzata. Una regione uniformemente chiara dà valori alti anche se non assomiglia al pattern. Si aggiunge un rettangolo bianco 6×10 per mostrarlo.</p>
<pre>h = (h - h.mean()) / (h.std() + eps)           # template a media 0, varianza 1
out[n, m] += h[k, j] * l[n + k, m + j]
out[n, m] /= l[n:n+3, m:m+5].std() + eps       # diviso per la std locale</pre>
<p><b>Figura:</b> immagine con il rettangolo; cross-correlazione semplice; versione normalizzata. Nella semplice il rettangolo raggiunge 9, come i triangoli: <b>26 posizioni</b> a pari merito, il detector non distingue. Nella normalizzata i due triangoli valgono <b>15</b>; dentro il rettangolo la risposta è <b>0</b> (zona uniforme), ma sul suo <b>bordo</b> arriva a 9; nel punto del triangolo capovolto vale −1.67, poco sopra arriva a 8.7. Il distacco c'è ma non è enorme: con una soglia mal scelta si avrebbero falsi positivi.</p>
<ul>
<li>Template a <b>media zero</b>: una regione costante dà prodotto scalare 0, qualunque sia la sua luminosità. Per questo non serve sottrarre la media locale dell'immagine.</li>
<li>Divisione per la <b>std locale</b>: toglie la dipendenza dal contrasto.</li>
<li>Il risultato è la <b>correlazione normalizzata (NCC)</b> moltiplicata per il numero di pixel del pattern: il massimo è 15 = 3 × 5 invece di 1. Dividendo anche per 15 si ottiene un valore in [−1, 1].</li>
<li>Restano risposte sui bordi del rettangolo: lì la finestra contiene un gradino che assomiglia in parte al pattern.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 15, § 15.5.1 Template Matching and Normalized Correlation</b>
<p>Il libro scrive la correlazione normalizzata con la finestra <b>centrata</b> sul pixel (k, l da −N a N) invece che agganciata all'angolo:</p>
<span class="f">ℓ<sub>out</sub>[n, m] = (1/σ[n, m]) ∑<sub>k,l=−N</sub><sup>N</sup> ℓ<sub>in</sub>[n + k, m + l] ĥ[k, l]</span>
<ul>
<li>ĥ è il template a media zero e norma unitaria; σ[n, m] è la deviazione standard locale, calcolata dalla media locale μ[n, m] sulla stessa finestra.</li>
<li>Il notebook normalizza ĥ a deviazione standard 1 invece che a norma 1: cambia solo una costante (il 15 del massimo), non dove stanno i picchi.</li>
<li>Esempio del libro (fig. 15.12): template della lettera "a" su una pagina di testo. La correlazione semplice si accende sulle zone bianche, quella normalizzata solo sulle "a", e una soglia dà i riquadri delle detection.</li>
<li>Giudizio del libro: il metodo è molto fragile, gestisce solo la posizione e cade con rotazione, scala o un font diverso.</li>
</ul>
<p><a href="https://visionbook.mit.edu/linear_image_filtering.html">visionbook.mit.edu · cap. 15</a></p></div>
<div class="box k"><b>Da saper spiegare</b><p>Perché la cross-correlazione pura privilegia le zone chiare, cosa risolvono la media zero del template e la divisione per la deviazione standard locale, e perché il metodo non gestisce scala e rotazione (servono piramidi, L6, e descrittori, L7).</p></div>
""", img='img/lif_template.png', printed=NB3 + 'celle 13–14')

s(27, "Esercizi del notebook", """
<ul>
<li><b>Bordi</b>: implementare altre condizioni al contorno, per esempio il padding <b>circolare</b> (indici modulo N, oppure <code>np.pad(image, …, mode='wrap')</code> prima dei cicli), o il mirror che il libro indica come il migliore (§ 15.4.3). Con il circolare la convoluzione coincide con quella calcolata via FFT (L3).</li>
<li><b>Caratteri</b>: fare lo screenshot di un testo, ritagliare un carattere come template e cercarlo. Provare font diversi, grassetto contro normale, caratteri ambigui (l, I, 1): si vede quanto il metodo sia fragile.</li>
<li><b>Uccelli</b> (visionbook, fig. 15.5, la figura con cui il libro motiva l'invarianza alla traslazione): ritagliare un uccello come template e cercare gli altri. Alla risoluzione originale il detector è rumoroso; conviene ridurre l'immagine (<code>scipy.ndimage.zoom</code>), così i dettagli fini spariscono e il pattern diventa più semplice. Ridurre senza sfocare prima produce aliasing (L6).</li>
</ul>
""", printed=NB3 + 'celle 15–16')
