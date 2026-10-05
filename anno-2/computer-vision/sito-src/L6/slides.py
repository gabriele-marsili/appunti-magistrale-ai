
s(1, "Copertina", """
<p><b>Aliasing and Scale-invariance</b>. Sesta lezione.</p>
<p>Si usano gli strumenti di Fourier (L3) e i filtri gaussiani (L5) per rispondere a due domande pratiche:</p>
<ul><li>come si <b>ridimensiona</b> un'immagine senza rovinarla;</li><li>come si <b>analizza</b> un'immagine a più scale.</li></ul>
""")

s(2, "Recap and Roadmap", """
<ul>
<li>In L5 molti filtri (gaussiana, derivate di gaussiana) dipendono da un parametro di scala <b>σ</b>.</li>
<li><b>Scale-space</b>: famiglia continua di rappresentazioni indicizzate dalla scala.</li>
<li><b>Piramidi di immagini</b>: rappresentazioni multiscala discrete e sottocampionate, quindi efficienti.</li>
<li>Applicazioni: ricerca coarse-to-fine, template matching, image blending.</li>
<li>Le rappresentazioni multiscala sono ovunque, da SIFT alle reti profonde.</li>
</ul>
<div class="box k"><b>Filo logico della lezione</b><p>Per costruire le piramidi bisogna sottocampionare. Sottocampionare male produce aliasing. Quindi prima si studia l'aliasing, poi si costruiscono le piramidi nel modo giusto.</p></div>
""")

s(3, "Aliasing", "<p>Cosa si perde, e cosa si inventa, quando si passa da un segnale continuo a campioni discreti.</p>", kind="div", sec=("aliasing","Aliasing","slide 3–18"))

s(4, "From Continuous to Discrete", """
<ul>
<li>Le immagini sono segnali continui, ma lavoriamo con <b>misure discrete</b>.</li>
<li>Le misure discrete hanno una <b>risoluzione in frequenza limitata</b>: bisogna sapere quale informazione si è persa.</li>
<li>Nelle pipeline di CV si sottocampiona di continuo (resize, pooling, stride), quindi i limiti del campionamento vanno capiti.</li>
</ul>
<p><b>Domande guida</b></p>
<ul>
<li>Data una frequenza di campionamento, qual è la frequenza massima rappresentabile senza errori? <i>(Risposta: f<sub>s</sub>/2, slide 11.)</i></li>
<li>Cosa succede quando si fa upsampling o downsampling?</li>
</ul>
<div class="box b"><b>Dal libro · cap. 20, § 20.1 Introduction</b>
<ul>
<li>Il libro modella il campionamento come lettura del segnale continuo a passi regolari: <span class="f">ℓ[n] = ℓ(n T<sub>s</sub>)</span> con <b>T<sub>s</sub> periodo di campionamento</b> (tonde = continuo, quadre = discreto). La frequenza di campionamento è ω<sub>s</sub> = 2π/T<sub>s</sub> (rad) o f<sub>s</sub> = 1/T<sub>s</sub>.</li>
<li>Le due domande del capitolo sono quelle della slide: quanto fitto campionare, e come ricostruire il continuo dai campioni. Scegliere T<sub>s</sub> richiede di capire <b>entrambe</b> le cose: il campionamento da solo non dice cosa "vediamo" fra un campione e l'altro.</li>
</ul>
<p>Capitolo: <a href="https://visionbook.mit.edu/sampling_and_aliasing.html" target="_blank">Sampling and Aliasing</a>.</p></div>
""")

s(5, "Sampling Tradeoff", """
<p>Due obiettivi in conflitto:</p>
<ul>
<li><b>massimizzare l'informazione</b>: servono molti campioni;</li>
<li><b>minimizzare calcolo e memoria</b>: di solito almeno lineari nel numero di pixel.</li>
</ul>
<p>La frequenza di campionamento regola questo compromesso.</p>
<ul>
<li>Il downsampling riduce il costo.</li>
<li>L'upsampling <b>non</b> recupera l'informazione persa.</li>
<li>Punto chiave: la bassa risoluzione non solo perde informazione, può anche <b>aggiungere artefatti</b> (strutture false). È l'aliasing.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 21, § 21.4 Upsampling (21.4.1–21.4.2, 21.4.4)</b>
<p>Perché l'upsampling non recupera nulla: si limita a <b>interpolare</b> fra i campioni esistenti con un kernel fisso.</p>
<ul>
<li><b>Nearest neighbor</b>: ogni punto prende il valore del pixel più vicino, risultato a blocchi. Per k = 2 il kernel è [1, 1].</li>
<li><b>Lineare / bilineare</b>: media pesata dei 2 (1D) o 4 (2D) pixel vicini; in 2D è un'interpolazione lineare orizzontale seguita da una verticale. Kernel triangolare h[n] = (k − |n|)/k su [−k, k]; per k = 2 diventa [1/2, 1, 1/2].</li>
<li>Bicubica e Lanczos danno risultati migliori a costo maggiore.</li>
</ul>
<p>Nessuno di questi kernel crea frequenze sopra la vecchia Nyquist: l'immagine diventa più grande, non più dettagliata. Capitolo: <a href="https://visionbook.mit.edu/upsamplig_downsampling_2.html" target="_blank">Downsampling and Upsampling</a>.</p></div>
""")

s(6, "Moiré Pattern", """
<p><b>Figura:</b> a sinistra righe diagonali sottili ad alta risoluzione; a destra la versione sottocampionata, con bande e scacchiere che nell'originale non esistono.</p>
<p>Le righe hanno frequenza più alta di quella che la griglia sottocampionata può rappresentare, e ricompaiono come pattern a bassa frequenza con orientazione diversa: l'<b>effetto moiré</b>.</p>
""")

s(7, "Aliasing Example", """
<p><b>Figura:</b> sinusoide con f<sub>0</sub> = 0.9 f<sub>s</sub> campionata a f<sub>s</sub> = 1. I campioni (punti rossi) cadono esattamente su una sinusoide lenta con f = 0.1 f<sub>s</sub> (tratteggio arancione).</p>
<div class="box k"><b>Da saper fare</b>
<p>Frequenza apparente = |f<sub>0</sub> − k·f<sub>s</sub>|, con k intero scelto in modo che il risultato cada in [0, f<sub>s</sub>/2]. Qui |0.9 − 1| = 0.1.</p>
<p>Verifica: per n intero, cos(2π·0.9n) = cos(2πn − 2π·0.1n) = cos(2π·0.1n). Sui campioni le due sinusoidi sono identiche.</p></div>
""")

s(8, "Sampling a Sinusoid", """
<p>f(x) = cos(2π f<sub>0</sub> x) campionata a frequenza f<sub>s</sub>:</p>
<ul>
<li>se <b>f<sub>s</sub> &gt; 2f<sub>0</sub></b>, i campioni identificano la sinusoide in modo univoco;</li>
<li>se <b>f<sub>s</sub> &lt; 2f<sub>0</sub></b>, i campioni sono indistinguibili da una sinusoide più lenta a |f<sub>0</sub> − k f<sub>s</sub>|.</li>
</ul>
<p><b>Aliasing</b>: contenuto ad alta frequenza misurato come bassa frequenza perché f<sub>s</sub> è troppo piccola.</p>
<p><b>Prior "slow-and-smooth"</b>: implicitamente si assume che la frequenza giusta sia la più lenta compatibile con i campioni. È così che funzionano gli strumenti matematici ed è coerente con la nostra percezione.</p>
<div class="box x"><b>Approfondimento</b><p>Il caso f<sub>s</sub> = 2f<sub>0</sub> è ambiguo (i campioni possono cadere tutti sugli zeri del coseno): per questo la condizione è una disuguaglianza stretta.</p></div>
<div class="box b"><b>Dal libro · cap. 20, § 20.2 Aliasing</b>
<p>Esempio del libro, da rifare a mano: ℓ(t) = cos(18π t), cioè 9 periodi in [0, 1] (periodo 1/9, frequenza 9). Lo si campiona con T<sub>s</sub> = 1/11 (11 campioni per unità di tempo).</p>
<ul>
<li>11 &lt; 2 · 9 = 18: la condizione di Nyquist è violata.</li>
<li>Con il prior "slow and smooth" la sinusoide più lenta che passa per i campioni ha frequenza |9 − 11| = 2, quindi periodo <b>1/2</b>: è quella che si "vede".</li>
<li>Il libro chiama l'aliasing una "confusione di frequenze": la frequenza non sparisce, viene scambiata per un'altra.</li>
</ul>
<p>Lo stesso capitolo mostra il caso 2D: un'onda diagonale con frequenza che cresce nello spazio, campionata a 52×52 pixel; nell'immagine campionata cambiano sia l'orientazione sia la frequenza delle righe, come nel moiré della slide 6. <a href="https://visionbook.mit.edu/sampling_and_aliasing.html" target="_blank">Cap. 20</a>.</p></div>
""")

s(9, "Aliasing: Definition", """
<ul>
<li><b>Aliasing</b>: contenuto ad alta frequenza che si traveste da bassa frequenza dopo il campionamento, per <b>sovrapposizione delle repliche spettrali</b>.</li>
<li>Succede quando f<sub>s</sub> &lt; 2 × (frequenza massima del segnale).</li>
<li>Dopo l'aliasing l'informazione ad alta frequenza <b>non è recuperabile</b>: non è solo persa, è mescolata alle basse frequenze.</li>
</ul>
<div class="box k"><b>Da saper spiegare</b><p>Perché "repliche spettrali": campionare = moltiplicare per un treno di impulsi di passo T<sub>s</sub>. In Fourier diventa una convoluzione con un treno di impulsi di passo f<sub>s</sub>, quindi lo spettro viene copiato ogni f<sub>s</sub>. Se lo spettro è più largo di f<sub>s</sub>/2 per lato, le copie si sovrappongono e si sommano.</p>
<p>Consiglio: disegna qui su OneNote un triangolo centrato in 0 con le sue copie ogni f<sub>s</sub>, una volta separate e una volta sovrapposte.</p></div>
<div class="box b"><b>Dal libro · cap. 20, § 20.3.1 Modeling the Sampling Process</b>
<p>Il libro rende rigoroso il "campionare = moltiplicare per un treno di impulsi" del riquadro sopra.</p>
<ul>
<li><b>Treno di delta</b> (pettine di Dirac): <span class="f">δ<sub>T<sub>s</sub></sub>(t) = ∑<sub>n</sub> δ(t − n T<sub>s</sub>)</span></li>
<li>Moltiplicandolo per il segnale, per la proprietà di campionamento della delta ogni impulso "prende" il valore di ℓ nel suo punto: <span class="f">ℓ<sub>δ</sub>(t) = ℓ(t) · δ<sub>T<sub>s</sub></sub>(t) = ∑<sub>n</sub> ℓ[n] δ(t − n T<sub>s</sub>)</span></li>
<li>ℓ<sub>δ</sub> è ancora una funzione del <b>continuo</b>, ma contiene solo l'informazione dei campioni. Il trucco serve a usare la trasformata di Fourier continua (e il teorema di convoluzione) su un segnale campionato: la DTFT dei campioni coincide con la trasformata di ℓ<sub>δ</sub> a meno di un cambio di scala dell'asse, L<sub>s</sub>(w) = L<sub>δ</sub>(w/T<sub>s</sub>).</li>
</ul>
<p><a href="https://visionbook.mit.edu/sampling_and_aliasing.html" target="_blank">Cap. 20, Sampling and Aliasing</a>.</p></div>
""")

s(10, "Sampling Theorem", "<p>Il teorema che dice quando campionare è innocuo.</p>", kind="div", sec=("nyquist","Teorema del campionamento","slide 10–18"))

s(11, "The Sampling Theorem (Nyquist–Shannon)", """
<ul>
<li>Sia l(t) un segnale <b>a banda limitata</b> con frequenza massima ω<sub>max</sub>.</li>
<li>Sia ω<sub>s</sub> = 2π / T<sub>s</sub> la frequenza di campionamento.</li>
</ul>
<p>Allora l(t) si ricostruisce perfettamente se <b>ω<sub>s</sub> &gt; 2ω<sub>max</sub></b> (condizione di Nyquist).</p>
<p>In parole: <b>la frequenza di campionamento deve essere più del doppio della frequenza massima del segnale</b>.</p>
<ul><li><b>Frequenza di Nyquist</b> = f<sub>s</sub>/2: la massima frequenza ricostruita correttamente.</li></ul>
<p><b>Figura:</b> spettro L(ω) nullo fuori da [−ω<sub>max</sub>, ω<sub>max</sub>].</p>
<div class="box x"><b>Approfondimento</b><ul>
<li>La slide mescola ω (rad/s) e f (Hz): ω = 2πf, la condizione è la stessa.</li>
<li>La ricostruzione "perfetta" richiede il passa-basso ideale (interpolazione con sinc), che in pratica non si usa (slide 26).</li>
<li>Per le immagini, con un campione per pixel, la Nyquist è 0.5 cicli/pixel: un periodo non può essere più corto di 2 pixel.</li></ul></div>
<div class="box b"><b>Dal libro · cap. 20, § 20.3.2 Sampling in the Fourier Domain</b>
<p>La dimostrazione del teorema in tre passi:</p>
<ol>
<li>La trasformata di un treno di delta di passo T<sub>s</sub> è ancora un treno di delta, di passo <b>2π/T<sub>s</sub></b> in frequenza: più fitti i campioni nel tempo, più distanti gli impulsi in frequenza.</li>
<li>Prodotto nel tempo = convoluzione in frequenza (L3), e convolvere con un treno di delta significa copiare lo spettro su ogni impulso:
<span class="f">L<sub>δ</sub>(w) ∝ ∑<sub>k</sub> L(w − k · 2π/T<sub>s</sub>)</span></li>
<li>Se L è nulla fuori da [−w<sub>max</sub>, w<sub>max</sub>], le copie non si toccano se la distanza fra i centri supera la larghezza: 2π/T<sub>s</sub> &gt; 2w<sub>max</sub>, cioè <b>T<sub>s</sub> &lt; π/w<sub>max</sub></b>. È la condizione della slide scritta sul periodo.</li>
</ol>
<p>Se le copie si sovrappongono, l'alta frequenza di una copia finisce nella banda bassa della copia centrale: è l'aliasing, ed è irreversibile perché le due cose si <b>sommano</b>. Il libro scrive la condizione con la disuguaglianza stretta. <a href="https://visionbook.mit.edu/sampling_and_aliasing.html" target="_blank">Cap. 20</a>.</p></div>
""")

s(12, "Aliasing and sampling theorem", """
<ul>
<li>L'aliasing è una conseguenza del teorema del campionamento.</li>
<li>Se la condizione di Nyquist non è rispettata non si perde solo informazione: si ottiene aliasing.</li>
</ul>
<p><b>Figura:</b> stessa coppia della slide 6 (originale e sottocampionata).</p>
<div class="box b"><b>Dal libro · cap. 20, § 20.4 Reconstruction</b>
<p>La metà "ricostruisci perfettamente" del teorema.</p>
<ul>
<li><b>§ 20.4.1 Ideale</b>: si tiene solo la copia centrale dello spettro con un passa-basso ideale (box in frequenza su [−π/T<sub>s</sub>, π/T<sub>s</sub>]), la cui risposta all'impulso è una sinc, sinc(t) = sin(πt)/(πt). Nel tempo:
<span class="f">ℓ̃(t) = ∑<sub>n</sub> ℓ[n] · sinc((t − n T<sub>s</sub>)/T<sub>s</sub>)</span>
Ogni campione "accende" una sinc centrata su di sé; le sinc valgono 1 nel proprio campione e 0 su tutti gli altri, quindi la somma passa per i campioni e li raccorda in modo liscio.</li>
<li><b>§ 20.4.2 Kernel locali</b>: la sinc ha supporto infinito e decade lentamente (come 1/t), quindi in pratica si usano kernel corti: box di larghezza T<sub>s</sub> (nearest neighbor), triangolo di larghezza 2T<sub>s</sub> (lineare, è la convoluzione di due box), Lanczos-1 (solo il lobo centrale della sinc).</li>
</ul>
<p>Collegamento: sono gli stessi filtri che tornano nel resize (slide 26) e nell'upsampling delle piramidi. <a href="https://visionbook.mit.edu/sampling_and_aliasing.html" target="_blank">Cap. 20</a>.</p></div>
""")

s(13, "Classic Examples", """
<ul>
<li><b>Spaziale, moiré</b>: griglie o texture fini sovrapposte (vestiti a righe in foto, schermo fotografato da un altro schermo).</li>
<li><b>Temporale, effetto wagon-wheel</b>: una ruota o un ventilatore sembra girare più lentamente, o all'indietro, perché il frame rate campiona la rotazione troppo lentamente. <a href="https://en.wikipedia.org/wiki/Wagon-wheel_effect">Esempi su Wikipedia</a></li>
</ul>
<p>Il wagon-wheel è la slide 7 nel tempo: una ruota che fa quasi un giro per frame sembra muoversi di poco.</p>
<div class="box b"><b>Dal libro · cap. 20, § 20.6 Spatiotemporal Sampling</b>
<ul>
<li>Il teorema vale in qualunque dimensione: un video è un segnale 3D (x, y, t) campionato anche nel tempo, e il wagon-wheel è l'aliasing <b>temporale</b>.</li>
<li>Il libro distingue due modi di campionare nel tempo: <b>global shutter</b> (tutti i pixel nello stesso istante, a intervalli regolari) e <b>rolling shutter</b> (ogni riga in un istante diverso): più veloce, ma deforma gli oggetti in movimento o la scena se la camera si muove.</li>
<li>Il moiré è legato all'aliasing: nasce dall'interferenza di due pattern fini sovrapposti (la griglia del sensore è uno dei due).</li>
</ul>
<p><a href="https://visionbook.mit.edu/sampling_and_aliasing.html" target="_blank">Cap. 20</a>.</p></div>
""")

s(14, "Aliasing in Images: Visual Artifacts", """
<ul>
<li><b>Jaggies</b> (bordi a scaletta): i bordi diagonali netti hanno contenuto ad alta frequenza che diventa un pattern a scalini.</li>
<li><b>Texture aliasing</b>: texture fini ripetute (mattoni, tessuti) generano falsi pattern se sottocampionate senza filtrare.</li>
<li>Il <b>resize ingenuo</b> (nearest-neighbor) è il caso da manuale.</li>
</ul>
""")

s(15, "Quantization vs. Sampling", """
<ul>
<li><b>Campionamento</b>: discretizzazione nello spazio/tempo (dove misuro).</li>
<li><b>Quantizzazione</b>: discretizzazione in ampiezza, es. 8 bit per pixel (con che precisione misuro).</li>
<li>Sono indipendenti.</li>
<li><b>L'aliasing nasce dal campionamento</b>, non dalla quantizzazione. La quantizzazione produce altri artefatti (banding).</li>
</ul>
""")

s(16, "Aliasing in CNNs", """
<ul>
<li>Convoluzioni con <b>stride</b> e <b>pooling</b> (max/average) sono downsampling.</li>
<li>Il downsampling può introdurre artefatti nelle rappresentazioni latenti.</li>
<li>Conseguenza: piccoli spostamenti dell'input possono cambiare molto le feature map (<b>perdita di shift-invariance/equivarianza</b>).</li>
</ul>
<div class="box x"><b>Approfondimento</b><p>Per questo una CNN può cambiare predizione spostando l'immagine di un pixel. La soluzione è la stessa della slide 24: sfocare prima di sottocampionare (anti-aliased CNN, BlurPool, Zhang 2019). L'average pooling è già un debole passa-basso, il max pooling no.</p></div>
""")

s(17, "Aliasing Attack in CNNs", """
<p><b>Figura:</b> in alto l'immagine di un uccello l<sub>in</sub>, un rumore z quasi invisibile e la somma l<sub>in</sub> + 0.05·z, identica all'originale a occhio. In basso ciò che si ottiene dopo il sottocampionamento: dalla somma esce un segnale di <b>STOP</b>.</p>
<p>z è costruito ad alta frequenza in modo che, dopo un resize senza prefiltro, faccia alias proprio nell'immagine bersaglio. L'umano vede l'uccello, la rete (che lavora sull'input ridimensionato) vede lo STOP.</p>
<p>È un attacco al <b>sottocampionamento senza prefiltro</b>, non ai pesi della rete: si difende prefiltrando.</p>
<div class="box b"><b>Dal libro · cap. 21, § 21.2 Example: Aliasing-Based Adversarial Attack</b>
<p>L'esempio è di Rodríguez-Muñoz e Torralba (2022). Il "sistema" attaccato è una mini-rete: <b>filtro di bordo [1, −1] → decimazione di 2 → ReLU</b>; ℓ<sub>out</sub> in basso a sinistra è la sua uscita sull'uccello (i bordi).</p>
<ul>
<li>Il rumore si costruisce modulando l'immagine nascosta: <span class="f">z[n, m] = (−1)<sup>n</sup> (−1)<sup>m</sup> ℓ<sub>hidden</sub>[n, m]</span> e l'input attaccato è ℓ<sub>in</sub> + ε z con ε = 0.05.</li>
<li>Moltiplicare per (−1)<sup>n+m</sup> sposta lo spettro di ℓ<sub>hidden</sub> alle frequenze più alte (π, π): a occhio è una trama finissima e debole, quasi invisibile.</li>
<li>La decimazione di 2 ripiega proprio (π, π) sull'origine: è il caso k = 2 della slide 23. Dopo il sottocampionamento l'immagine nascosta torna a bassa frequenza e domina l'uscita.</li>
</ul>
<p>Morale: il punto debole è la decimazione senza prefiltro dentro la rete, non i pesi. <a href="https://visionbook.mit.edu/upsamplig_downsampling_2.html" target="_blank">Cap. 21</a>.</p></div>
""")

s(18, "Summary", """
<ul>
<li>La frequenza di campionamento limita le frequenze rappresentabili.</li>
<li>Se il segnale contiene frequenze più alte, si ha aliasing.</li>
<li>L'aliasing riguarda quasi tutte le pipeline di CV, perché il resize è un'operazione comunissima.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 20, § 20.7 Concluding Remarks</b>
<p>Il libro aggiunge una sfumatura che le slide non dicono: l'aliasing non è sempre solo un danno. Il pattern di aliasing <b>contiene</b> informazione sulle alte frequenze; algoritmi di <b>super-risoluzione</b> possono imparare a sfruttarlo, e se un'immagine è codificata da più canali (o più scatti leggermente spostati) l'aliasing di un canale può essere compensato dagli altri. <a href="https://visionbook.mit.edu/sampling_and_aliasing.html" target="_blank">Cap. 20</a>.</p></div>
""")

s(19, "Downsampling", "<p>Come si sottocampiona perdendo il meno possibile.</p>", kind="div", sec=("downsampling","Downsampling","slide 19–29"))

s(20, "Decimation", """
<p><b>Decimazione</b>: sottocampionare eliminando pixel.</p>
<span class="f">l<sub>↓k</sub>[n, m] = l[k·n, k·m]</span>
<p>Questo approccio ingenuo <b>introduce aliasing</b>.</p>
<div class="box k"><b>Da saper spiegare</b><p>In frequenza (1D): decimare di k allarga lo spettro di un fattore k in frequenza normalizzata. Tutto ciò che stava oltre π/k (la nuova Nyquist) si ripiega dentro la banda.</p></div>
""")

s(21, "Example", """
<p><b>Figura:</b> maglione a 128×128, 64×64, 32×32 ottenuti per decimazione.</p>
<ul>
<li>A 64×64 la trama della maglia diventa una scacchiera regolare e falsa.</li>
<li>A 32×32 compaiono macchie di colore che non corrispondono a niente nell'originale.</li>
</ul>
""")

s(22, "2D Delta Train", """
<p><b>Figura:</b> sopra, treni di impulsi 2D con passo diverso nello spazio; sotto, le loro DFT Δ<sub>k</sub>[u, v].</p>
<ul>
<li>Treno fitto nello spazio (passo 1): un solo impulso nell'origine in frequenza.</li>
<li>Treno più rado nello spazio (passo k): impulsi <b>più fitti</b> in frequenza (passo N/k).</li>
</ul>
<p><b>Perché serve:</b> decimare = moltiplicare per questo treno. Moltiplicazione nello spazio = convoluzione in frequenza, quindi lo spettro viene replicato su ogni impulso. Più sottocampioni, più le repliche sono vicine e si sovrappongono.</p>
<div class="box b"><b>Dal libro · cap. 21, § 21.3.1 Decimation e § 21.3.2 Decimation in the Fourier Domain</b>
<ul>
<li>Decimare di k un'immagine N×M dà un'immagine <b>N/k × M/k</b>; il libro scrive anche ℓ[n, m]↓k.</li>
<li>Per l'analisi si tiene la griglia originale e si azzerano i pixel scartati, moltiplicando per il treno di delta 2D <span class="f">δ<sub>k</sub>[n, m] = ∑<sub>s</sub> ∑<sub>r</sub> δ[n − sk, m − rk]</span></li>
<li>Se N e M sono divisibili per k, la sua DFT è un altro treno con <b>k × k impulsi</b> distanti N/k (e M/k):
<span class="f">Δ<sub>k</sub>[u, v] = (NM/k²) ∑<sub>s=0</sub><sup>k−1</sup> ∑<sub>r=0</sub><sup>k−1</sup> δ[u − sN/k, v − rM/k]</span>
È la riga in basso della figura: con k = 1 un solo impulso, all'aumentare di k impulsi più numerosi e più vicini.</li>
</ul>
<p><a href="https://visionbook.mit.edu/upsamplig_downsampling_2.html" target="_blank">Cap. 21, Downsampling and Upsampling</a>.</p></div>
""")

s(23, "Clothing DFT", """
<p><b>Figura:</b> il maglione l[n,m], poi moltiplicato per il treno di impulsi con k = 2 e k = 4; sotto, le rispettive DFT.</p>
<ul>
<li>Originale: energia vicino all'origine ma anche componenti lontane (la trama fine).</li>
<li>k = 2, k = 4: compaiono le repliche dello spettro. Il <b>quadrato verde</b> è la nuova banda utile [−N/2k, N/2k]. Dentro il quadrato entrano pezzi delle repliche vicine: <b>è l'aliasing visto nello spettro</b>.</li>
</ul>
<div class="box k"><b>Da saper spiegare</b><p>È la slide che collega tutto: treno di impulsi, teorema di convoluzione, repliche, Nyquist. Prova a spiegarla a voce senza guardare.</p></div>
<div class="box b"><b>Dal libro · cap. 21, § 21.3.2 e § 21.3.3 Aliasing in Matrix Form</b>
<p>Formula chiave: la DFT dell'immagine decimata è la media di k × k copie traslate della DFT originale,</p>
<span class="f">L<sub>↓k</sub>[u, v] = (1/k²) ∑<sub>s=0</sub><sup>k−1</sup> ∑<sub>r=0</sub><sup>k−1</sup> L[u − sN/k, v − rM/k]</span>
<ul>
<li>Con k = 2 si sommano 4 copie: ogni frequenza della nuova immagine è la somma di 4 frequenze dell'originale. Se l'originale ha energia fuori dal quadrato verde, quell'energia finisce dentro.</li>
<li>Versione 1D in forma matriciale (§ 21.3.3): con k = 2, L<sub>↓2</sub>[u] = ½ (L[u] + L[u + N/2]), cioè L<sub>↓2</sub> = ½ [I<sub>N/2</sub> | I<sub>N/2</sub>] L. Ogni coefficiente è la somma di due: una frequenza bassa e la sua "gemella" alta, che da quel momento non si possono più separare.</li>
<li>Nel maglione con k = 4 si perde l'orientazione della trama e l'immagine diventa quasi illeggibile (Fig. 21.2 del libro).</li>
</ul>
<p><a href="https://visionbook.mit.edu/upsamplig_downsampling_2.html" target="_blank">Cap. 21</a>.</p></div>
""")

s(24, "Anti-Aliasing Pre-Filtering", """
<ul>
<li>Se l'input non è a banda limitata: <b>passa-basso prima di campionare</b>.</li>
<li>Toglie le frequenze sopra la nuova Nyquist, che così non possono ripiegarsi.</li>
<li>Le fotocamere hanno un <b>filtro ottico anti-aliasing</b> davanti al sensore proprio per questo.</li>
</ul>
<p>Regola pratica: per sottocampionare di k serve un passa-basso con taglio a circa π/k. Con una gaussiana, σ proporzionale a k.</p>
<p>Il prezzo è perdere il dettaglio fine, ma in modo "onesto": immagine sfocata invece di strutture false.</p>
<div class="box b"><b>Dal libro · cap. 20, § 20.5 Anti-Aliasing Filter</b>
<ul>
<li>Il filtro ideale è un box in frequenza che tiene esattamente la banda rappresentabile alla nuova risoluzione: <b>ogni risoluzione richiede il suo filtro</b> (taglio a π/k per un fattore k).</li>
<li>Il prefiltro <b>non salva</b> l'informazione ad alta frequenza: la elimina. Quello che evita è che venga travestita da bassa frequenza.</li>
<li>Esempio del libro: una zebra ridotta più volte di 2 senza prefiltro; le strisce cambiano orientazione, l'animale diventa irriconoscibile e la DFT cambia completamente da un livello all'altro. Con il prefiltro la parte centrale della DFT resta <b>la stessa</b> a tutte le risoluzioni: è il criterio per dire che il downsampling è corretto.</li>
</ul>
<p><a href="https://visionbook.mit.edu/sampling_and_aliasing.html" target="_blank">Cap. 20</a>.</p></div>
""")

s(25, "Anti-Aliasing Pre-Filtering (figura)", """
<p><b>Figura:</b> foto 512×512; downsample ×8 senza prefiltro; blur gaussiano e poi downsample ×8.</p>
<ul>
<li>Senza prefiltro: bordi seghettati, texture della tuta e della bandiera rumorose.</li>
<li>Con prefiltro: più morbida, ma pulita e fedele.</li>
</ul>
""")

s(26, "Anti-Aliasing: Binomial Filter", """
<p><b>Figura:</b> un cubo rosso ricampionato con tre filtri.</p>
<ul>
<li><b>Ideale</b> (box in frequenza = sinc nello spazio): taglio perfetto ma <b>ringing</b> (aloni vicino ai bordi, fenomeno di Gibbs), perché la sinc ha lobi laterali lenti a decadere.</li>
<li><b>Hamming</b>: sinc finestrata, ringing ridotto.</li>
<li><b>Binomiale</b>: approssima una gaussiana, nessun ringing, ma taglio morbido (un po' di aliasing passa, un po' di dettaglio utile si attenua).</li>
</ul>
<div class="box k"><b>Compromesso da ricordare</b><p>Filtro ripido in frequenza = filtro lungo e oscillante nello spazio. Filtro liscio nello spazio = taglio morbido in frequenza. In visione di solito si preferisce evitare il ringing.</p></div>
<div class="box b"><b>Dal libro · cap. 21, § 21.3.4 Anti-Aliasing Filters</b>
<p>I tre filtri della figura, per un downsampling di k su un segnale lungo N:</p>
<ul>
<li><b>Ideale</b>: box in frequenza con taglio a N/(2k), cioè una sinc periodica nello spazio. Taglio netto, ma ringing (Fig. 21.15a).</li>
<li><b>Sinc finestrata con Hamming</b>: si moltiplica la sinc per w[n] = 0.54 + 0.46 cos(πn/L) su [−L, L] (0 fuori), così il kernel ha supporto finito e oscilla meno. Ringing ridotto, ma restano aloni attorno ai bordi.</li>
<li><b>Binomiale</b>: b<sub>2</sub> = [1, 2, 1]/4, b<sub>4</sub> = [1, 4, 6, 4, 1]/16. La risposta in frequenza di b<sub>2</sub> è proporzionale a 1 + cos(2πu/N): decresce in modo monotono, senza ondulazioni; alla nuova Nyquist per k = 2 (u = N/4) il guadagno è 1/2. Non elimina del tutto le frequenze che fanno aliasing, ma le attenua abbastanza, e non produce ringing.</li>
</ul>
<p><a href="https://visionbook.mit.edu/upsamplig_downsampling_2.html" target="_blank">Cap. 21</a>. Le proprietà del binomiale sono in <a href="https://visionbook.mit.edu/blurring_2.html" target="_blank">cap. 17, § 17.4</a>.</p></div>
""")

s(27, "Example: Clothing", """
<ul>
<li><b>Sopra</b> (Fig. 11): 128, 64, 32 per decimazione, con aliasing (come slide 21).</li>
<li><b>Sotto</b> (Fig. 12): stessa sequenza con prefiltro. A 32×32 la trama non si vede più, ma non compaiono pattern falsi: resta un maglione sfocato.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 21, § 21.3.5 Downsampling</b>
<p>Il libro chiama <b>downsampling</b> l'operazione completa (prefiltro + decimazione) e <b>decimazione</b> solo il secondo passo:</p>
<span class="f">z = ℓ<sub>in</sub> ∗ h<sub>k</sub>,   ℓ<sub>out</sub>[n, m] = z[kn, km]</span>
<p>Con k = 2 e il filtro binomiale, ripetuto più volte, a 32×32 si vedono ancora l'orientazione dei punti della maglia e l'ombreggiatura 3D delle pieghe (Fig. 21.17), mentre la decimazione semplice (Fig. 21.2) li distrugge. Osservazione: per arrivare a 32×32 conviene dimezzare più volte con un filtro piccolo, non usare un solo filtro enorme. È l'idea della piramide gaussiana (slide 42). <a href="https://visionbook.mit.edu/upsamplig_downsampling_2.html" target="_blank">Cap. 21</a>.</p></div>
""")

s(28, "Demonstration: Zone Plate", """
<ul>
<li>La <b>zone plate</b> (anelli concentrici con frequenza crescente) è un pattern di test classico per l'aliasing.</li>
<li>Sottocampionata senza filtro, gli anelli fitti producono moiré spurio a bassa frequenza.</li>
</ul>
<p>È utile perché contiene tutte le frequenze e tutte le orientazioni, ognuna in una posizione precisa: dove la frequenza locale supera la Nyquist, lo vedi subito.</p>
""")

s(29, "Demonstration: Zone Plate (figura)", """
<p><b>Figura:</b> zone plate 256×256; downsample ×4 senza prefiltro; blur e poi downsample ×4.</p>
<ul>
<li><b>Senza prefiltro</b>: compaiono cerchi "nuovi" dove l'originale ha solo anelli fittissimi. Sono alias.</li>
<li><b>Con prefiltro</b>: resta solo la parte centrale (basse frequenze), il resto diventa grigio uniforme. È corretto: quelle frequenze non sono rappresentabili alla nuova risoluzione.</li>
</ul>
""")
s(30, "Scale-Space", "<p>Seconda parte: come rappresentare un'immagine a tutte le scale.</p>", kind="div", sec=("scalespace","Scale-space","slide 30–40"))

s(31, "Scale Invariance", """
<p><b>Figura:</b> stormo di uccelli a distanze diverse: lo stesso oggetto appare con dimensioni molto diverse.</p>
<p>Un detector con un filtro di dimensione fissa trova solo oggetti di una certa dimensione. Serve <b>invarianza alla scala</b>.</p>
""")

s(32, "Multi-Scale Representation", """
<p><b>Figura:</b> la stessa immagine a risoluzioni decrescenti (a)–(e). Un detector a finestra fissa (riquadri rossi) trova uccelli diversi a ogni livello: in (a) i piccoli, nei livelli ridotti i grandi, che ora entrano nella finestra.</p>
<p>Idea: invece di cambiare il detector, <b>si cambia l'immagine</b>.</p>
<div class="box b"><b>Dal libro · cap. 23, § 23.1 Introduction e § 23.2 Image Pyramids and Multiscale Image Analysis</b>
<ul>
<li>Il libro presenta l'invarianza alla scala come la "sorella" dell'invarianza per traslazione (cap. 15): la prospettiva fa apparire lo stesso oggetto a dimensioni diverse, quindi per trovare <i>tutti</i> gli uccelli serve un operatore invariante sia per traslazione sia per scala.</li>
<li>Invece di convolvere con template sempre più grandi (costo che cresce con la dimensione del template), si tiene il template piccolo e si rimpicciolisce l'immagine: le convoluzioni restano economiche.</li>
<li>Nell'esempio degli uccelli (immagine 848×643) ogni livello è ridotto <b>del 25%</b> rispetto al precedente, non dimezzato. Il motivo (ragionamento mio, non del libro): per la detection servono scale più fitte di un'ottava, altrimenti un oggetto può cadere fra due livelli. La piramide gaussiana "classica" (slide 41) usa invece il fattore 2.</li>
</ul>
<p><a href="https://visionbook.mit.edu/pyramids_new_notation.html" target="_blank">Cap. 23, Image Pyramids</a>.</p></div>
""")

s(33, "Motivation: Subsampling for Efficiency", """
<p>Molti task vanno risolti a più scale (volti piccoli e grandi). Due modi di cercare fra le scale:</p>
<ol>
<li><b>Immagine fissa, filtro variabile</b> (g<sub>σ</sub> per molti σ): è lo <b>scale-space</b>. Costoso: O(σ) per pixel per scala, tutto a piena risoluzione.</li>
<li><b>Filtro fisso, immagine variabile</b> (blur + downsample ripetuti): è una <b>piramide</b>. Lo stesso filtro piccolo si riusa a ogni livello e ogni livello costa meno del precedente.</li>
</ol>
<p>Le piramidi rinunciano a un po' di flessibilità (scale discrete legate da un fattore fisso, di solito 2) in cambio di grossi guadagni di velocità.</p>
""")

s(34, "From Multiscale Derivatives to Scale-Space", """
<ul><li>Richiamo (L5): scegliere σ per le derivate di gaussiana = scegliere la scala di analisi.</li></ul>
<p><b>Rappresentazione scale-space</b>:</p>
<span class="f">L(x, y; σ) = (g<sub>σ</sub> ∗ l)(x, y),   σ ≥ 0</span>
<ul>
<li>L(·, ·; 0) = l, l'immagine originale. Aumentando σ si toglie progressivamente il dettaglio fine.</li>
<li>Un'immagine diventa un continuo di immagini indicizzate dalla scala: le strutture scompaiono e si fondono al crescere di σ.</li>
</ul>
""")

s(35, "Scale-Space and the Heat Equation", """
<ul>
<li>La gaussiana è la funzione di Green dell'<b>equazione di diffusione</b> (L5).</li>
<li>Aumentare σ = far "diffondere" l'immagine: l'intensità passa dalle zone chiare alle scure, livellando la struttura in modo monotono.</li>
<li>Al crescere di σ <b>non si crea struttura nuova</b> (estremi): è l'assioma che rende la gaussiana il kernel canonico dello scale-space. Altri kernel possono creare estremi spuri.</li>
</ul>
<div class="box w"><b>Attenzione: formula sbagliata sulla slide</b>
<p>La slide scrive ∂L/∂σ = ∇²L con t = σ²/2. Così non torna: la derivata va fatta rispetto a t. Forme corrette, equivalenti:</p>
<span class="f">∂L/∂t = ∇²L   con t = σ²/2</span>
<span class="f">∂L/∂σ = σ · ∇²L</span>
<p>(Si passa dall'una all'altra con dt = σ dσ.) All'esame scrivi una di queste due.</p></div>
<div class="box x"><b>Approfondimento</b><p>"Nessun nuovo estremo" è esatto in 1D. In 2D possono nascere nuovi estremi locali; l'assioma preciso è che gli estremi non vengono "rinforzati" (un massimo non cresce, un minimo non cala). Per il corso basta l'idea: la gaussiana non inventa strutture.</p></div>
""")

s(36, "Scale-Space Axioms", """
<p>La gaussiana è l'<b>unico</b> kernel che soddisfa tutti gli assiomi dello scale-space:</p>
<ul>
<li><b>LSI</b>: lineare e invariante per traslazione;</li>
<li><b>simmetria rotazionale</b>;</li>
<li><b>componibile</b>: sfocare due volte equivale a sfocare una volta con un'altra gaussiana;</li>
<li><b>non aggiunge struttura</b> (es. bordi);</li>
<li>più altri che il corso non chiede.</li>
</ul>
<div class="box w"><b>Attenzione: formula sbagliata sulla slide</b>
<p>La slide scrive g(g(l, σ<sub>1</sub>), σ<sub>2</sub>) = g(l, σ<sub>1</sub> + σ<sub>2</sub>). È sbagliato: si sommano le <b>varianze</b>, non le deviazioni standard.</p>
<span class="f">g<sub>σ2</sub> ∗ (g<sub>σ1</sub> ∗ l) = g<sub>σ</sub> ∗ l   con σ = √(σ<sub>1</sub>² + σ<sub>2</sub>²)</span>
<p>Esempio: due blur con σ = 1 danno σ = √2 ≈ 1.41, non 2. Con t = σ²/2 (slide 35) invece si sommano direttamente: t = t<sub>1</sub> + t<sub>2</sub>.</p></div>
<div class="box b"><b>Dal libro · cap. 17, § 17.3.2 Properties of the Continuous Gaussian</b>
<p>Il libro conferma la correzione: la convoluzione di due gaussiane è una gaussiana con varianza somma, <span class="f">g(·; σ<sub>1</sub>) ∗ g(·; σ<sub>2</sub>) = g(·; σ<sub>3</sub>),   σ<sub>3</sub>² = σ<sub>1</sub>² + σ<sub>2</sub>²</span> e ricorda che la gaussiana è la soluzione dell'equazione del calore. Lo stesso vale per i binomiali (§ 17.4.1): b<sub>n</sub> ∗ b<sub>m</sub> = b<sub>n+m</sub>, con varianza n/4, quindi σ<sub>n</sub>² + σ<sub>m</sub>² = σ<sub>n+m</sub>². Capitolo: <a href="https://visionbook.mit.edu/blurring_2.html" target="_blank">Blur Filters</a> (è quello di L5).</p></div>
""")

s(37, "Visualizing Scale-Space", """
<p><b>Figura:</b> la stessa foto con σ = 0, 1, 2, 4, 8.</p>
<ul>
<li>La texture fine sparisce per prima; le strutture grandi (volto, silhouette) sopravvivono più a lungo.</li>
<li>Strutture diverse hanno scale "naturali" diverse.</li>
</ul>
<p>Collegamento con L7: i detector di keypoint (SIFT) cercano la σ a cui una struttura risponde di più (<i>scale selection</i>).</p>
""")

s(38, "Image Pyramids", """
<ul>
<li>L(x, y; σ) è definita per ogni σ sulla griglia a piena risoluzione.</li>
<li>Calcolarla per molti σ a piena risoluzione è uno spreco: a σ grande l'immagine è liscia e la sua informazione sta già in una risoluzione molto più bassa.</li>
<li><b>Idea</b>: dopo aver sfocato abbastanza da togliere il dettaglio a una certa scala, si può sottocampionare senza perdere informazione.</li>
</ul>
<div class="box k"><b>Il ponte fra le due parti</b><p>Il blur dello scale-space è proprio il prefiltro anti-aliasing della slide 24. Blur + downsample fatti bene = niente aliasing e niente spreco.</p></div>
""")

s(39, "Image Pyramids (definizione)", """
<ul>
<li>Una <b>piramide</b> è una pila {I<sub>0</sub>, I<sub>1</sub>, I<sub>2</sub>, …}: I<sub>0</sub> è l'originale e ogni I<sub>l+1</sub> è una versione sfocata e sottocampionata di I<sub>l</sub>.</li>
<li>Ogni livello è a una scala più grossolana <b>e</b> su una griglia più rada: raddoppiare la σ effettiva corrisponde a dimezzare la risoluzione.</li>
</ul>
<p><b>Figura:</b> un faro a risoluzioni dimezzate successivamente.</p>
""")

s(40, "Octaves and Pyramid Notation", """
<ul>
<li>Dimezzare la risoluzione (e raddoppiare σ) si chiama <b>ottava</b>, come il raddoppio di frequenza in musica.</li>
<li>Il livello l ha risoluzione W/2<sup>l</sup> × H/2<sup>l</sup> e scala effettiva σ<sub>l</sub> = 2<sup>l</sup> σ<sub>0</sub>.</li>
<li>Memoria totale (ogni livello ha 1/4 dei pixel del precedente):</li>
</ul>
<span class="f">Σ<sub>l=0..L−1</sub> WH / 4<sup>l</sup> ≤ (4/3) · WH</span>
<ul>
<li>Una piramide completa costa solo il <b>33% di memoria in più</b>: ecco perché le piramidi sono ovunque.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Serie geometrica di ragione 1/4: 1 + 1/4 + 1/16 + … = 1/(1 − 1/4) = 4/3. In 1D sarebbe ragione 1/2, cioè 2× (100% in più).</p></div>
<div class="box x"><b>Approfondimento</b><p>σ<sub>l</sub> = 2<sup>l</sup>σ<sub>0</sub> vale asintoticamente. Riapplicando sempre lo stesso kernel (σ<sub>b</sub>) le varianze si sommano; in pixel dell'originale: σ<sub>eff</sub>(l)² = σ<sub>b</sub>² (4<sup>l</sup> − 1)/3, quindi σ<sub>eff</sub> ≈ σ<sub>b</sub> · 2<sup>l</sup>/√3, che raddoppia a ogni livello.</p></div>
""")

s(41, "Gaussian Pyramid", "<p>Costruzione concreta della piramide più semplice.</p>", kind="div", sec=("gauss","Piramide gaussiana","slide 41–46"))

s(42, "Construction: Repeated Blur + Downsample", """
<p>A ogni livello: blur con un kernel piccolo e fisso, poi downsample di 2 per dimensione.</p>
<span class="f">I<sub>l+1</sub>[m, n] = (b ∗ I<sub>l</sub>)[2m, 2n]</span>
<ul>
<li>b è fisso (uguale a ogni livello). Applicarlo a immagini sempre più piccole approssima gaussiane sempre più grandi sull'originale (convoluzioni ripetute → circa gaussiana).</li>
<li><b>Promemoria</b>: senza blur il downsampling produce aliasing invece di mettere in evidenza la struttura alle varie scale.</li>
</ul>
""")

s(43, "Kernel: Binomial Filter", """
<ul>
<li>Il <b>filtro binomiale</b> è la scelta standard per b: economico, coefficienti interi, separabile, composizione esatta b<sub>n</sub> ∗ b<sub>n</sub> = b<sub>2n</sub>.</li>
<li>Scelta comune: kernel 5×5 di <b>Burt-Adelson</b>, separabile come <b>(1/16)·[1, 4, 6, 4, 1]</b> su ogni asse.</li>
</ul>
<div class="box k"><b>Da sapere</b><ul>
<li>b<sub>n</sub> = riga n del triangolo di Tartaglia / 2<sup>n</sup>. b<sub>4</sub> = [1 4 6 4 1]/16.</li>
<li>La varianza di b<sub>n</sub> è n/4: b<sub>4</sub> ha σ = 1 pixel. Componendo, le varianze si sommano (coerente con la correzione della slide 36).</li>
<li>In 2D il kernel è il prodotto esterno dei due vettori; lo applichi come due convoluzioni 1D: 10 moltiplicazioni per pixel invece di 25.</li></ul></div>
""")

s(44, "Matrix Form", """
<p>Tutte le operazioni sono lineari. Per un segnale 1D g<sub>0</sub>:</p>
<span class="f">g<sub>k+1</sub> = D<sub>k</sub> B<sub>k</sub> g<sub>k</sub> = G<sub>k</sub> g<sub>k</sub></span>
<ul>
<li><b>D<sub>k</sub></b>: downsampling, una matrice che tiene una riga su due (1 nelle colonne 0, 2, 4, 6).</li>
<li><b>B<sub>k</sub></b>: blur, matrice a bande con [1 4 6 4 1]/16 su ogni riga, troncata ai bordi (zero-padding).</li>
<li>Nell'esempio il segnale ha lunghezza 8, quindi G<sub>0</sub> è 4 × 8.</li>
</ul>
<p>La forma matriciale serve a scrivere la laplaciana e la sua inversa in una riga (slide 49 e 51).</p>
<div class="box b"><b>Dal libro · cap. 23, § 23.4 Gaussian Pyramid</b>
<ul>
<li>Il libro definisce g<sub>0</sub> = ℓ e g<sub>k+1</sub> = D<sub>k</sub>B<sub>k</sub>g<sub>k</sub> con B<sub>k</sub> = convoluzione separabile con b<sub>4</sub> = [1, 4, 6, 4, 1]/16. Per le immagini a colori la piramide si costruisce <b>canale per canale</b>.</li>
<li>Guarda le righe di B<sub>0</sub> ai bordi: [6 4 1 0 …]/16 e [4 6 4 1 0 …]/16 sommano a 11/16 e 15/16, non a 1. È lo zero-padding: i bordi della piramide si scuriscono un po' a ogni livello (è il "bordo scuro" che si vede nel notebook).</li>
<li>Perché funziona: applicare ripetutamente una gaussiana equivale ad applicarne una sola più larga (varianze che si sommano), e dopo il sottocampionamento lo stesso b<sub>4</sub> copre una zona doppia dell'originale. Così un filtro di 5 tap simula filtri sempre più grandi.</li>
<li>Memoria: 1 + 1/4 + 1/16 + … = 4/3 dell'immagine (slide 40).</li>
</ul>
<p><a href="https://visionbook.mit.edu/pyramids_new_notation.html" target="_blank">Cap. 23</a>.</p></div>
""")

s(45, "Example: Gaussian Pyramid", """
<p><b>Figura:</b> piramide gaussiana 256, 128, 64, 32, 16.</p>
<p>I livelli grossolani evidenziano le <b>feature globali</b>, utili per l'object detection, che ha bisogno anche di informazione su scala globale.</p>
""")

s(46, "Properties: Resolution vs. Memory Tradeoff", """
<ul>
<li>Memoria totale ≤ 4/3 dell'originale (slide 40).</li>
<li>Ogni livello dimezza risoluzione e contenuto in frequenza, per ogni dimensione.</li>
<li><b>Livelli grossolani</b>: economici, catturano la struttura globale, perdono il dettaglio.</li>
<li><b>Livelli fini</b>: costosi, catturano dettaglio e texture, ma la struttura grande è difficile da rilevare (un filtro piccolo ne vede solo un pezzo).</li>
</ul>
""")

s(47, "Laplacian Pyramid", "<p>Come non buttare via l'informazione tolta dal blur.</p>", kind="div", sec=("laplace","Piramide laplaciana","slide 47–51"))

s(48, "Loss of Information", """
<ul>
<li>La piramide gaussiana <b>perde informazione</b> a ogni livello: da g<sub>k+1</sub> non si torna a g<sub>k</sub>.</li>
<li>Si affianca un'altra piramide che codifica la differenza fra livelli consecutivi.</li>
</ul>
<p><b>Piramide laplaciana</b>, in tre passi:</p>
<ol><li>prendi g<sub>k</sub> e g<sub>k+1</sub>, due livelli consecutivi della gaussiana;</li><li>riporta g<sub>k+1</sub> alla dimensione di g<sub>k</sub>;</li><li>fai la differenza.</li></ol>
""")

s(49, "Laplacian Pyramid (formula)", """
<span class="f">l<sub>k</sub> = g<sub>k</sub> − F<sub>k</sub> g<sub>k+1</sub> = (I<sub>k</sub> − F<sub>k</sub> G<sub>k</sub>) g<sub>k</sub> = L<sub>k</sub> g<sub>k</sub></span>
<ul>
<li><b>F<sub>k</sub> = B<sub>k</sub> U<sub>k</sub></b>: upsampling seguito da blur.</li>
<li><b>U<sub>k</sub></b>: upsampling ingenuo, inserisce zeri fra i campioni.</li>
<li><b>B<sub>k</sub></b>: lo stesso blur della gaussiana (es. b<sub>4</sub>).</li>
</ul>
<div class="box k"><b>Da capire</b><ul>
<li>l<sub>k</sub> contiene esattamente il dettaglio perso passando da g<sub>k</sub> a g<sub>k+1</sub>: è una <b>banda</b> di frequenze (passa-banda), non un passa-alto puro.</li>
<li>Perché "laplaciana": differenza di due gaussiane (DoG) ≈ laplaciano di gaussiana (L5). I livelli hanno media circa zero e rispondono su bordi e dettagli.</li>
<li>l<sub>k</sub> ha valori positivi e negativi: va tenuto in float (vedi il notebook).</li></ul></div>
<div class="box w"><b>Attenzione: dettaglio omesso nella slide</b><p>Inserendo zeri la media cala di 2 in 1D e di 4 in 2D, quindi il blur dopo l'upsampling va moltiplicato per 2 (1D) o 4 (2D). Il notebook lo fa (<code>4*h</code>).</p></div>
<div class="box b"><b>Dal libro · cap. 23, § 23.5 Laplacian Pyramid e cap. 21, § 21.4.3 Expansion</b>
<ul>
<li>Il libro conferma il fattore mancante: nella matrice F<sub>0</sub> (8×4) il blur dopo l'upsampling ha <b>guadagno 2</b>, perché inserire zeri dimezza il valore medio di g<sub>k+1</sub> (in 2D il fattore è 4, uno per asse).</li>
<li>Perché serve anche il blur: inserire k − 1 zeri fra i campioni (espansione, ℓ<sub>↑k</sub>) <b>replica lo spettro</b> k volte per asse. Il filtro di interpolazione deve togliere le copie in più; con k = 2 il filtro lineare è [1/2, 1, 1/2], cioè 2 · b<sub>2</sub>. Il binomiale non le toglie del tutto, ma il risultato è accettabile.</li>
<li>Ogni livello l<sub>k</sub> contiene "ciò che c'è in g<sub>k</sub> ma non nel livello più grossolano": è un'immagine <b>passa-banda</b>, e le bande sono isotrope (non distinguono orientazioni).</li>
</ul>
<p><a href="https://visionbook.mit.edu/pyramids_new_notation.html" target="_blank">Cap. 23</a>, <a href="https://visionbook.mit.edu/upsamplig_downsampling_2.html" target="_blank">cap. 21</a>.</p></div>
""")

s(50, "Example (piramide laplaciana)", """
<p><b>Figura:</b> piramide laplaciana del faro. Grigio medio = zero; i contorni sono evidenziati. I livelli fini contengono bordi sottili e texture, quelli grossolani le forme grandi.</p>
""")

s(51, "Invertibility", """
<p>Dalla piramide laplaciana più l'ultimo livello della gaussiana (g<sub>N</sub>) si ricostruisce l'originale:</p>
<span class="f">g<sub>k</sub> = l<sub>k</sub> + F<sub>k</sub> g<sub>k+1</sub></span>
<p>Si parte da g<sub>N</sub> e si risale livello per livello fino a g<sub>0</sub>.</p>
<div class="box k"><b>Punti da orale</b><ul>
<li>La ricostruzione è <b>esatta qualunque sia il filtro</b>: l<sub>k</sub> è definito proprio come ciò che manca. Basta usare lo stesso F<sub>k</sub> in costruzione e ricostruzione.</li>
<li>È <b>sovracompleta</b>: circa 4/3 dei campioni dell'originale (stesso conto della slide 40).</li>
<li>Usi: compressione (i livelli sono quasi tutti vicini a zero; è l'uso originale di Burt &amp; Adelson, 1983), blending (slide 58), modifiche per banda.</li></ul></div>
<div class="box b"><b>Dal libro · cap. 23, § 23.5 Laplacian Pyramid, § 23.3 Linear Image Transforms, § 23.7 A Pictorial Summary</b>
<ul>
<li>Il libro sottolinea il punto non ovvio: la ricostruzione <b>non dipende dai filtri usati</b>. Basta conservare il residuo passa-basso (l'ultima gaussiana) e rifare g<sub>k</sub> = l<sub>k</sub> + F<sub>k</sub>g<sub>k+1</sub> dall'alto verso il basso.</li>
<li>Nel linguaggio di § 23.3 una piramide è una trasformazione lineare r = P<sup>T</sup>ℓ con N pixel in ingresso e M coefficienti in uscita: <b>critically sampled</b> se M = N, <b>sovracompleta</b> se M &gt; N. La laplaciana è sovracompleta (circa 4N/3 coefficienti).</li>
<li>§ 23.7 la disegna come matrice: per due livelli più residuo, P impila L<sub>0</sub>, L<sub>1</sub> e G<sub>1</sub>. Le righe sono localizzate (bande diagonali), a differenza della DFT, dove ogni coefficiente dipende da tutti i pixel.</li>
<li>Il confronto con le wavelet/QMF (filtri [1, 1] e [1, −1] con stride 2): sono <b>complete</b> (M = N), ottime per comprimere, ma se modifichi una banda senza le altre compaiono artefatti di aliasing. La laplaciana spende circa il 33% di coefficienti in più ma tollera le modifiche banda per banda: è uno dei motivi per cui si usa nel blending.</li>
</ul>
<p><a href="https://visionbook.mit.edu/pyramids_new_notation.html" target="_blank">Cap. 23</a>.</p></div>
""")

s(52, "Applications", "<p>Dove si usano le piramidi.</p>", kind="div", sec=("app","Applicazioni","slide 52–64"))

s(53, "Coarse-to-Fine Search", """
<ul>
<li>Molti problemi cercano in uno spazio di parametri grande (tutti gli spostamenti, tutte le scale).</li>
<li><b>Coarse-to-fine</b>: risolvi al livello più grossolano (piccolo, economico), usa la soluzione per restringere la ricerca al livello successivo, ripeti.</li>
<li>Invece di una ricerca esaustiva a piena risoluzione, basta una piccola ricerca locale a ogni livello dopo il primo.</li>
</ul>
<div class="box k"><b>Il rischio</b><p>Se al livello grossolano scegli la soluzione sbagliata, i livelli fini non la correggono: cercano solo in un intorno. Oggetti piccoli o sottili possono sparire nei livelli grossolani.</p></div>
""")

s(54, "Coarse-to-Fine Search Example: Optical Flow", """
<ul>
<li>Spostamenti grandi sono difficili da stimare a piena risoluzione (il pixel esce dalla finestra di ricerca).</li>
<li>A un livello grossolano lo stesso spostamento è piccolo (al livello l si divide per 2<sup>l</sup>).</li>
<li>Stimi il flow in cima, lo porti al livello sotto come stima iniziale (upsample e ×2), raffini, ripeti.</li>
<li>È la strategia di Lucas-Kanade piramidale. Il flow ottico tornerà più avanti nel corso.</li>
</ul>
<div class="box w"><b>Attenzione: esempio impreciso sulla slide</b><p>La slide cita RAFT come metodo coarse-to-fine. Non lo è: RAFT aggiorna iterativamente un unico campo di flow e usa una piramide solo sul volume di correlazione; il paper si presenta proprio come alternativa al coarse-to-fine. Esempi deep davvero coarse-to-fine: SPyNet, PWC-Net.</p></div>
""")

s(55, "Pyramid-Based Template Matching", """
<ul>
<li>Template matching ingenuo: O(dimensione immagine × dimensione template).</li>
<li>Coarse-to-fine: match al livello grossolano, tieni le posizioni candidate migliori, raffina solo quelle al livello sotto.</li>
<li>Evita la ricerca esaustiva e trova il match migliore, <i>se</i> il match grossolano è un buon punto di partenza.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Scendere di un livello divide per 4 sia le posizioni sia i pixel del template: il costo esaustivo cala di 16×. L'ottimo globale non è garantito; tenere più candidati (top-k) riduce il rischio.</p></div>
""")

s(56, "Coarse-to-Fine Alignment Example: Matching", """
<ul>
<li>Anche l'allineamento di immagini funziona coarse-to-fine: trasformazione approssimata a bassa risoluzione, poi raffinamento.</li>
<li>Si combina con il matching di feature: si rilevano feature a più livelli della piramide e si stima una trasformazione robusta alla scala a cui sono state trovate (anticipo di SIFT, L7).</li>
</ul>
""")

s(57, "Image Blending", """
<ul>
<li><b>Obiettivo</b>: unire due immagini A e B con una transizione morbida al confine.</li>
<li><b>Soluzione ingenua</b>: una curva di confine, A da un lato e B dall'altro.</li>
<li><b>Problema</b>: differenze di esposizione, colore o dettaglio creano una cucitura visibile.</li>
</ul>
<div class="box k"><b>Perché non basta sfocare la maschera</b><p>Transizione stretta: si vede il gradino di colore. Transizione larga: il dettaglio delle due immagini si sovrappone e compaiono doppi bordi ("fantasmi"). Non esiste una larghezza giusta per tutte le frequenze.</p></div>
""")

s(58, "Multi-Band (Laplacian Pyramid) Blending", """
<p><b>Burt &amp; Adelson, 1983</b>:</p>
<ol>
<li>piramidi laplaciane LP<sup>A</sup> e LP<sup>B</sup> delle due immagini;</li>
<li>piramide <b>gaussiana</b> GP<sup>α</sup> della maschera α (la maschera si sfoca a ogni livello);</li>
<li>blending banda per banda, pixel per pixel:</li>
</ol>
<span class="f">LP<sup>I</sup><sub>l</sub> = GP<sup>α</sup><sub>l</sub> · LP<sup>A</sup><sub>l</sub> + (1 − GP<sup>α</sup><sub>l</sub>) · LP<sup>B</sup><sub>l</sub></span>
<ol start="4"><li>ricostruisci I dalla piramide fusa (slide 51). Lo stesso blending si applica al residuo g<sub>N</sub>.</li></ol>
<p>Ogni banda viene fusa con una transizione di larghezza <b>proporzionale alla sua scala</b>.</p>
<div class="box k"><b>Risposta alla slide 57</b><p>Basse frequenze (colore, luce) fuse su una zona larga: niente gradino. Alte frequenze (texture, bordi) fuse su una zona stretta: niente fantasmi. Esempio classico: la "orapple", che è il notebook di questa lezione.</p></div>
<div class="box b"><b>Dal libro · cap. 23, § 23.5.1 Image Blending</b>
<ul>
<li>Blending ingenuo nel libro: ℓ<sub>out</sub> = ℓ<sup>A</sup> · m + ℓ<sup>B</sup> · (1 − m), con m maschera binaria: bordo netto.</li>
<li>Procedura multi-banda: (1) piramidi laplaciane di A e B (nell'esempio <b>7 livelli</b>); (2) piramide gaussiana della maschera con <b>un livello in più</b>, che serve per fondere anche il residuo passa-basso; (3) a ogni livello <span class="f">l<sub>k</sub> = l<sub>k</sub><sup>A</sup> · m<sub>k</sub> + l<sub>k</sub><sup>B</sup> · (1 − m<sub>k</sub>)</span> (4) ricostruzione della piramide fusa.</li>
<li>Esempio: metà sinistra della mela e metà destra dell'arancia. La maschera, che a piena risoluzione è un gradino, diventa sempre più sfumata salendo nella gaussiana, quindi ogni banda è fusa su una zona proporzionale alla sua scala.</li>
</ul>
<p><a href="https://visionbook.mit.edu/pyramids_new_notation.html" target="_blank">Cap. 23</a>.</p></div>
""")

s(59, "CNN: Pyramids as Multi-Scale Feature Maps", """
<ul>
<li>Una CNN con stride/pooling produce feature map a risoluzione decrescente: una <b>piramide appresa</b>.</li>
<li><b>Primi layer</b> (alta risoluzione): dettaglio fine, campo recettivo piccolo, come i livelli fini.</li>
<li><b>Ultimi layer</b> (bassa risoluzione): campo recettivo grande (σ effettiva grande), come i livelli grossolani.</li>
<li>Valgono gli stessi compromessi scala/efficienza.</li>
</ul>
<div class="box x"><b>Differenza con la piramide gaussiana</b><p>Nella CNN il downsampling di solito non è preceduto da un passa-basso, quindi può fare aliasing (slide 16). E i canali aumentano mentre cala la risoluzione.</p></div>
""")

s(60, "CNN: Feature Pyramid Networks (FPN)", """
<ul>
<li>Detection e segmentazione devono trovare oggetti a molte scale.</li>
<li>L'ultimo layer è troppo grossolano per gli oggetti piccoli; i primi sono ad alta risoluzione ma poveri di semantica.</li>
<li><b>FPN</b> (Lin et al., 2017): alla piramide bottom-up si aggiunge un percorso <b>top-down</b> che fa upsampling delle feature grossolane e le <b>somma</b> a quelle fini tramite <b>connessioni laterali</b>. È l'analogo della ricostruzione laplaciana (upsample e combina).</li>
<li>Ogni livello diventa sia ad alta risoluzione sia ricco di semantica, e si usa per la detection alla scala adatta.</li>
</ul>
<div class="box x"><b>Dettagli utili all'orale</b><p>Connessione laterale = conv 1×1 (allinea i canali); upsampling nearest ×2; dopo la somma una conv 3×3. Analogia: g<sub>k</sub> = l<sub>k</sub> + F<sub>k</sub>g<sub>k+1</sub>, con l<sub>k</sub> il contributo laterale e F<sub>k</sub>g<sub>k+1</sub> quello top-down.</p></div>
""")

s(61, "Conclusions", "<p>Chiusura della lezione.</p>", kind="div")

s(62, "Key Takeaways", """
<ul>
<li>L'<b>aliasing</b> è un problema in quasi tutte le pipeline: le frequenze sopra la Nyquist si ripiegano e creano struttura falsa.</li>
<li>Il <b>downsampling richiede un blur</b> per evitarlo.</li>
<li>L'<b>invarianza alla scala</b> si ottiene con rappresentazioni multiscala: piramide gaussiana, laplaciana, o CNN apprese.</li>
</ul>
""")

s(63, "Further Reading", """
<p><a href="https://visionbook.mit.edu/series.html">MIT Vision Book</a>: capitoli su sampling/aliasing e sulle piramidi. Quasi tutte le figure della lezione vengono da lì.</p>
<ul>
<li><a href="https://visionbook.mit.edu/sampling_and_aliasing.html" target="_blank">Cap. 20, Sampling and Aliasing</a>: slide 3–18.</li>
<li><a href="https://visionbook.mit.edu/upsamplig_downsampling_2.html" target="_blank">Cap. 21, Downsampling and Upsampling</a>: slide 17, 19–29 e l'upsampling delle piramidi.</li>
<li><a href="https://visionbook.mit.edu/pyramids_new_notation.html" target="_blank">Cap. 23, Image Pyramids</a>: slide 31–58.</li>
</ul>
<p>Lo scale-space continuo (slide 34–36) non ha un capitolo dedicato fra questi: la composizione delle gaussiane è nel cap. 17 (L5). Ordine di lettura e cosa saltare nella sezione "Studia dal libro" in fondo alla pagina.</p>
""")

s(64, "Preview", """
<p><b>Lezione 7</b>: feature e descrittori, corner di Harris, SIFT, feature locali apprese.</p>
<p>Collegamento: SIFT costruisce una piramide scale-space e cerca gli estremi della DoG (quasi la piramide laplaciana di oggi) nello spazio e nella scala.</p>
""")
