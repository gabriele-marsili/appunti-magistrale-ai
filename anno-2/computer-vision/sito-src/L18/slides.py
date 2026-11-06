NB = 'NOTEBOOK vit_trained.ipynb · '
V26 = '<a href="https://visionbook.mit.edu/transformers.html">visionbook.mit.edu · cap. 26</a>'

# ---------------------------------------------------------------- dati, patch e token

s(1, "Vision Transformers (ViT): obiettivi e setup", """
<p>Il notebook mette in pratica la parte sul ViT della <a href="#L17">L17</a> (slide 24–39): nel lab sulle CNN (<a href="#L16">L16</a>) i filtri convoluzionali guardavano intorni locali; qui l'immagine viene tagliata in <b>patch</b>, ogni patch diventa un <b>token</b> e la <b>self-attention</b> scambia informazione fra tutte le patch.</p>
<p>Cosa fa, in ordine:</p>
<ul>
<li>carica <b>Imagenette</b> (10 classi di ImageNet, foto vere a 224×224) e la divide in training, validazione e test;</li>
<li>costruisce i pezzi del ViT <b>a mano</b>: patch embedding, attenzione scalata, separazione in teste, attenzione multi-testa, verificandoli contro le funzioni di PyTorch;</li>
<li>monta un ViT piccolo (D = 96, 4 teste, 2 blocchi, 317 674 parametri) e lo addestra da zero per 40 epoche con <b>AdamW</b>;</li>
<li>guarda dentro la rete: feature dei token come mappe 14×14, <b>attention rollout</b>, similarità degli <b>embedding posizionali</b>, confrontando con un <b>ViT-B/16 preaddestrato</b> di torchvision (86,6 milioni di parametri);</li>
<li>chiude con domande, esperimenti facoltativi e tre esercizi "da colloquio" (attenzione con maschera, proiezione fusa e teste, softmax stabile).</li>
</ul>
<pre>torch.manual_seed(4444)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# uscita salvata: Using device: cuda | PyTorch: 2.9.1+cu128</pre>
<ul>
<li>A differenza della L16 il dispositivo si sceglie da solo: lo stesso codice gira su GPU o su CPU.</li>
<li>Il <b>seme</b> fissato rende riproducibili inizializzazione, shuffle e augmentation. Lo abbiamo verificato: rieseguendo su CPU (PyTorch 2.14) le prime epoche danno <b>esattamente</b> gli stessi numeri del docente (sezione <a href="#l18-risultati">Risultati</a>).</li>
<li>Tempi: il docente ha usato una GPU, 43–61 s per epoca; sulla nostra CPU a 2 core un'epoca richiede circa 96 s. Il ViT di questo lab è piccolo: le 40 epoche si possono fare anche senza GPU, in poco più di un'ora.</li>
</ul>
""", sec=("l18-token", "Dati, patch e token", 'schede 1–6'), printed=NB + 'celle 1–3')

s(2, "Imagenette: classi, trasformazioni, split", """
<p><b>Imagenette</b> (Jeremy Howard, fast.ai) è un sottoinsieme "facile" di ImageNet: 10 classi ben distinte, foto reali a risoluzione piena (non miniature 32×32 come CIFAR). Si usa la versione <b>320px</b> (lato corto ridotto a 320 pixel).</p>
<table>
<tr><th>indice</th><th>classe</th><th>indice ImageNet</th></tr>
<tr><td>0</td><td>tench (tinca)</td><td>0</td></tr>
<tr><td>1</td><td>English springer (cane)</td><td>217</td></tr>
<tr><td>2</td><td>cassette player</td><td>482</td></tr>
<tr><td>3</td><td>chain saw (motosega)</td><td>491</td></tr>
<tr><td>4</td><td>church</td><td>497</td></tr>
<tr><td>5</td><td>French horn</td><td>566</td></tr>
<tr><td>6</td><td>garbage truck</td><td>569</td></tr>
<tr><td>7</td><td>gas pump</td><td>571</td></tr>
<tr><td>8</td><td>golf ball</td><td>574</td></tr>
<tr><td>9</td><td>parachute</td><td>701</td></tr>
</table>
<pre>IMG_SIZE, PATCH_SIZE, NUM_CLASSES = 224, 16, 10
EMBED_DIM, NUM_HEADS, DEPTH = 96, 4, 2
BATCH_SIZE = 32
EPOCHS = 40
train_tf = Compose([RandomResizedCrop(224, scale=(0.65, 1.0)), RandomHorizontalFlip(),
                    ToTensor(), Normalize(mean, std)])
eval_tf  = Compose([Resize(256), CenterCrop(224), ToTensor(), Normalize(mean, std)])</pre>
<ul>
<li>Le cartelle di Imagenette hanno i nomi WordNet di ImageNet (n01440764…): la lista <code>imagenette_to_imagenet</code> serve solo a prendere i <b>nomi leggibili</b> dalle 1000 categorie dei pesi di ViT-B/16. Gli stessi indici serviranno a confrontare le predizioni del modello preaddestrato (scheda 22).</li>
<li><b>Training</b>: <code>RandomResizedCrop</code> ritaglia una regione casuale che copre fra il 65% e il 100% dell'area (con rapporto d'aspetto casuale) e la riporta a 224×224, poi flip orizzontale. È il "crop poi riscala" del libro (§ 36.2), diverso dal pad + crop di CIFAR nella <a href="#L16">L16</a>.</li>
<li><b>Valutazione</b>: ridimensiona il lato corto a 256 e prende il quadrato centrale 224×224 (rapporto 224/256 = 0,875, la convenzione standard di ImageNet).</li>
<li><b>Normalizzazione</b> con media e deviazione standard di ImageNet: sono quelle con cui è stato addestrato ViT-B/16, così le stesse immagini vanno bene per entrambi i modelli.</li>
<li><b>Split</b>: Imagenette ha solo train (9469 immagini) e val (3925). Il notebook mescola la val ufficiale con un generatore a seme 42 e la divide a metà: <b>1962 di validazione</b> (per seguire il training) e <b>1963 di test</b> (guardato una volta sola, alla fine). Le due metà vengono dalla stessa distribuzione.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Batch per epoca con B = 32: training ⌈9469/32⌉ = <b>296</b> (l'ultimo da 9469 − 295·32 = 29 immagini), validazione ⌈1962/32⌉ = 62 (l'ultimo da 10), test 62 (l'ultimo da 11). In 40 epoche l'ottimizzatore fa 296 · 40 = <b>11 840</b> aggiornamenti.</p></div>
<p>Il commento accanto a <code>EPOCHS = 40</code> dice che "un'epoca è solo una dimostrazione": è un residuo di una versione a 1 epoca, vedi la scheda 15.</p>
""", printed=NB + 'celle 4–5')

s(3, "Un'immagine e un batch: (B, C, H, W)", """
<pre>x, y = train_set[55]                 # image: (3, 224, 224) label: tench
img = (x * std[:, None, None] + mean[:, None, None]).clamp(0, 1)
plt.imshow(img.permute(1, 2, 0))
images, labels = next(iter(train_loader))
# images: torch.Size([32, 3, 224, 224]) labels: torch.Size([32])</pre>
<ul>
<li>Ogni immagine è un tensore <b>C×H×W = 3×224×224</b>, il batch è <b>B×C×H×W</b> come nella <a href="#L16">L16</a>.</li>
<li>Qui la visualizzazione è <b>giusta</b>: prima si annulla la normalizzazione (x·σ + μ), poi <code>permute(1, 2, 0)</code> porta gli assi in H×W×C per matplotlib. È proprio la correzione che nella L16 avevamo dovuto fare a mano.</li>
<li><code>train_set[55]</code> applica la transform di training, quindi un ritaglio e un flip casuali: chiamandolo due volte si ottengono due immagini diverse. Con il seme fissato la prima chiamata è riproducibile (nella nostra esecuzione: la stessa tinca).</li>
<li>Un transformer però non lavora su (B, C, H, W) ma su <b>sequenze</b> (B, N, D): N token di dimensione D. Le schede 4–5 fanno il passaggio.</li>
</ul>
<p><b>Figura (uscita salvata del notebook):</b> l'immagine 55 del training, una tinca su un fondo di ghiaia, dopo il ritaglio casuale.</p>
""", img='img/nb_tench.png', printed=NB + 'celle 6–8')

s(4, "Dai pixel ai token: N = HW/P²", """
<p>Un'immagine H×W con C canali e patch di lato P si divide in</p>
<span class="f">N = (H/P) · (W/P)</span>
<p>patch non sovrapposte. Ogni patch si appiattisce in un vettore x<sub>p</sub> ∈ ℝ<sup>P²C</sup> e si proietta con la stessa matrice E ∈ ℝ<sup>(P²C)×D</sup>: z<sub>p</sub> = x<sub>p</sub>E ∈ ℝ<sup>D</sup> (vettori riga, come nella slide 26 della <a href="#L17">L17</a>).</p>
<p>Con H = W = 224, C = 3, P = 16, D = 96:</p>
<span class="f">(B, 3, 224, 224) → (B, 196, 768) → (B, 196, 96) → (B, 197, 96)</span>
<ul>
<li><b>196 patch</b> (griglia 14×14), ognuna con 16·16·3 = <b>768</b> valori;</li>
<li>proiettate in token di <b>96</b> dimensioni;</li>
<li>più il token <b>[CLS]</b>: <b>197 token</b>.</li>
</ul>
<p><b>Domanda del notebook</b>: con P = 8? La griglia diventa 28×28: <b>N = 784</b> patch, <b>785 token</b>, ognuna con 8·8·3 = 192 valori. La matrice di attenzione di ogni testa passa da 197×197 = 38 809 a 785×785 = 616 225 elementi, circa <b>16 volte</b> di più (15,9).</p>
<div class="box k"><b>Da saper fare</b>
<p>Dato (H, W, C, P, D) scrivere tutte le forme: N = HW/P², valori per patch P²C, sequenza (N + 1)×D, matrice di attenzione (N + 1)² per testa. Notare che N · P²C = HWC: le patch contengono esattamente tutti i pixel, né più né meno, qualunque sia P. P deve dividere H e W (il codice lo controlla con un <code>assert</code>).</p>
<p>Esempi: 224, P = 32 → 7×7 = 49 patch, 50 token (il ViT-L/32 della figura delle posizioni in L17, slide 35); 384, P = 16 → 24×24 = 576 patch, 577 token (scheda 21).</p></div>
""", printed=NB + 'cella 9')

s(5, "PatchEmbed: una convoluzione con kernel P e stride P", """
<pre>class PatchEmbed(nn.Module):
    def __init__(self, image_size=224, patch_size=16, in_channels=3, dim=96):
        self.grid_size = image_size // patch_size          # 14
        self.num_patches = self.grid_size ** 2             # 196
        self.proj = nn.Conv2d(in_channels, dim, kernel_size=patch_size, stride=patch_size)
    def forward(self, x):
        return self.proj(x).flatten(2).transpose(1, 2)    # (B, N, D)</pre>
<ul>
<li>Ogni patch riceve la <b>stessa</b> proiezione lineare: è esattamente una convoluzione con kernel 16×16 e stride 16, che non si sovrappone mai (L17, slide 37 "CNNs in disguise"). Ogni filtro della conv è una riga di E: 96 filtri di forma 3×16×16.</li>
<li>Forme: la conv dà (B, 96, 14, 14), cioè ⌊(224 − 16)/16⌋ + 1 = 14 per lato; <code>flatten(2)</code> unisce le due dimensioni spaziali → (B, 96, 196); <code>transpose(1, 2)</code> mette i token sulle righe → <b>(B, 196, 96)</b>. Uscita salvata: <code>[2, 196, 96]</code>.</li>
<li>L'ordine dei token è quello di lettura (raster): il token n corrisponde alla patch di riga ⌊n/14⌋ e colonna n mod 14. Servirà per tornare alla griglia (schede 18 e 19).</li>
<li>Parametri: 768·96 pesi + 96 bias = <b>73 824</b>.</li>
</ul>
<pre>patches = F.unfold(images[:2], kernel_size=16, stride=16).transpose(1, 2)   # (2, 196, 768)
linear_tokens = F.linear(patches, conv.weight.flatten(1), conv.bias)
torch.testing.assert_close(patch_tokens, linear_tokens, atol=1e-5, rtol=1e-5)</pre>
<ul>
<li>La cella 13 lo verifica: <code>unfold</code> estrae esplicitamente le patch appiattite (la "patch matrix" <b>[2, 196, 768]</b>), poi un prodotto per la matrice dei pesi della conv appiattita (96×768) dà gli stessi token.</li>
<li>Funziona perché <code>unfold</code> e <code>weight.flatten(1)</code> ordinano i 768 valori nello stesso modo: prima il canale, poi riga e colonna dentro la patch.</li>
</ul>
<p><b>Figura (uscita salvata del notebook):</b> la prima immagine del batch (una pallina da golf su un tee, con testo stampato sotto) e la stessa con la griglia 14×14 delle patch 16×16.</p>
<div class="box b"><b>Dal libro · cap. 26, § 26.4.1 Tokenizing Data e § 26.9.1 Tokenization</b>
<p>Il libro tokenizza nello stesso modo: si taglia l'immagine in patch non sovrapposte, ogni patch diventa un vettore e una proiezione lineare apprendibile la porta alla dimensione del token (fig. 26.2). Nel § 26.9.1 osserva che è una convoluzione con kernel e stride uguali al lato della patch, e la scrive proprio come <code>conv(x_in, channels_in=3, channels_out=d, kernel=K, stride=K)</code>: il <code>nn.Conv2d</code> della cella 11. Se H e W non sono multipli di K si ridimensiona o si fa padding. Nel libro i token sono le <b>righe</b> di una matrice T ∈ ℝ<sup>N×d</sup>, la stessa convenzione del notebook.</p>
<p>{V26}</p></div>
""".replace('{V26}', V26), img='img/nb_griglia_patch.png', printed=NB + 'celle 10–13')

s(6, "Com'è fatto un token", """
<pre>raw = F.unfold(images[:1], kernel_size=16, stride=16).transpose(1, 2)   # (1, 196, 768)
embedded = patch_embed(images[:1])                                       # (1, 196, 96)
# Token 0: [-1.81  -0.947  0.163 ...]
# Token 1: [ 0.411  0.43  -0.234 ...]
# Token 2: [ 0.457  0.383 -0.282 ...]</pre>
<ul>
<li>Un token è un <b>vettore</b>, non una piccola immagine: 96 coordinate apprese. La proiezione qui è ancora <b>casuale</b> (il <code>patch_embed</code> della cella 11 non viene mai addestrato, è separato dal modello): le figure mostrano la struttura dei dati, non feature semantiche.</li>
<li><b>Figura in alto</b>: le prime sei patch, cioè le prime sei caselle della riga in alto della griglia (bordo bianco e prato, poi l'erba e il bordo della pallina).</li>
<li><b>Figura in basso a sinistra</b>: la matrice 196×768 delle patch appiattite. Si vedono <b>tre bande verticali</b> da 256 colonne, i canali R, G, B (l'ordine di <code>unfold</code>: prima il canale), e una periodicità di 14 righe, una riga della griglia di patch. Le ultime 14 righe, la riga di patch in fondo all'immagine, sono diverse da tutte le altre.</li>
<li><b>In basso a destra</b>: gli stessi 196 patch proiettati, 196×96. Le strisce verticali sono dimensioni che rispondono in modo simile a quasi tutte le patch (il bias e la media dell'immagine), le strisce orizzontali le righe della griglia.</li>
</ul>
<p><b>Domande del notebook</b> (cella 16), con le risposte della cella 17 ragionate:</p>
<ul>
<li><b>Perché 768 valori e solo 96 dimensioni?</b> 768 = P²C è fissato da patch e canali; D = 96 è una <b>scelta di progetto</b>: è la larghezza di tutti i blocchi dell'encoder e determina capacità e costo (D = 768 in ViT-B/16). È indipendente da P: con P = 8 le patch hanno 192 valori, ma D può restare 96.</li>
<li><b>Due patch identiche hanno lo stesso embedding?</b> Sì: la stessa funzione lineare (stessi pesi, stesso bias) applicata allo stesso vettore. Si vede nelle uscite: i token 1 e 2 (due quadrati di prato quasi uguali) hanno coordinate molto vicine, il token 0 (con il bordo bianco) è diverso. Diventano distinguibili solo dopo la somma dell'embedding posizionale (scheda 13).</li>
</ul>
""", img='img/nb_token_patch.png', printed=NB + 'celle 14–17')

# ---------------------------------------------------------------- self-attention

s(7, "Self-attention: query, key, value", """
<p>Ingresso di un blocco, senza la dimensione del batch: X ∈ ℝ<sup>(N+1)×D</sup>, un token per <b>riga</b> (N patch + [CLS]). Tre proiezioni apprese:</p>
<span class="f">Q = XW<sup>Q</sup>,   K = XW<sup>K</sup>,   V = XW<sup>V</sup>,   Q, K, V ∈ ℝ<sup>(N+1)×d<sub>k</sub></sup></span>
<span class="f">Attention(Q, K, V) = softmax( QKᵀ / √d<sub>k</sub> ) V,   A ∈ ℝ<sup>(N+1)×(N+1)</sup></span>
<p>Tre passi:</p>
<ol>
<li><b>Confronta</b>: S = QKᵀ/√d<sub>k</sub>; S<sub>ij</sub> dice quanto la query del token i corrisponde alla key del token j.</li>
<li><b>Normalizza ogni riga</b>: A<sub>ij</sub> = exp(S<sub>ij</sub>) / ∑<sub>m</sub> exp(S<sub>im</sub>). La softmax è lungo l'asse delle <b>key</b> (<code>dim=-1</code>): ogni riga somma a 1, è la distribuzione di una query su tutti i token.</li>
<li><b>Mescola i value</b>: Y<sub>i</sub> = ∑<sub>j</sub> A<sub>ij</sub>V<sub>j</sub>. Ogni token d'uscita è una media pesata dei value.</li>
</ol>
<table>
<tr><th>tensore</th><th>forma (una testa)</th><th>in PyTorch (batch B, h teste)</th></tr>
<tr><td>Q, K, V</td><td>(N+1, d<sub>k</sub>)</td><td>(B, h, N+1, d<sub>k</sub>)</td></tr>
<tr><td>S, A</td><td>(N+1, N+1)</td><td>(B, h, N+1, N+1)</td></tr>
<tr><td>Y = AV</td><td>(N+1, d<sub>k</sub>)</td><td>(B, h, N+1, d<sub>k</sub>)</td></tr>
</table>
<ul>
<li><b>Perché √d<sub>k</sub></b>: se le componenti di q e k sono indipendenti, a media 0 e varianza 1, Var(qᵀk) = d<sub>k</sub>. Senza scala, teste più larghe darebbero logit più grandi e una softmax più satura. Derivazione completa nella <a href="#L17">L17</a>, slide 30.</li>
<li>Il notebook usa la stessa larghezza d<sub>k</sub> per query, key e value; non è obbligatorio per i value (vedi il riquadro).</li>
</ul>
<div class="box b"><b>Dal libro · cap. 26, § 26.6.2 Self-Attention; Prince § 12.2.4 e 12.3.2</b>
<p>Il visionbook scrive la stessa cosa con altri nomi: token T ∈ ℝ<sup>N×d</sup> come righe, Q e K di larghezza m, V di larghezza d (eq. 26.5), A = softmax(QKᵀ/√m) con softmax <b>dentro ogni riga</b> e uscita AV (eq. 26.6). Precisa che query e key devono avere la stessa dimensione perché se ne fa il prodotto scalare, mentre i value hanno la dimensione dei token perché vengono sommati per produrre i nuovi token. Lo presenta come un <b>pooling dinamico</b>: una combinazione lineare dei token con pesi che dipendono dai dati.</p>
<p>Il Prince usa la convenzione <b>trasposta</b>: i token sono le <b>colonne</b> di X ∈ ℝ<sup>D×N</sup>, le proiezioni si scrivono Ω X con bias β, e l'attenzione è Sa[X] = V · Softmax[KᵀQ / √D<sub>q</sub>] con la softmax applicata a ogni <b>colonna</b> (eq. 12.7 e 12.9). È la stessa operazione: la sua matrice di attenzione è la trasposta di A. Sulla scala (§ 12.3.2): prodotti scalari grandi spingono la softmax nella zona in cui il valore più grande domina del tutto, piccoli cambiamenti dell'ingresso non cambiano più l'uscita, i gradienti diventano minuscoli e il modello è difficile da addestrare.</p>
<p>{V26}</p></div>
""".replace('{V26}', V26), sec=("l18-attn", "Self-attention da zero", 'schede 7–11'), printed=NB + 'cella 18')

s(8, "Esempio giocattolo: tre token, una testa", """
<pre>toy_q = torch.tensor([[2., 0.], [0., 2.], [1., 1.]])     # cella 19
toy_k = toy_q.clone()
toy_v = torch.tensor([[1., 0.], [0., 1.], [1., 1.]])
toy_scores = toy_q @ toy_k.T / math.sqrt(2)
toy_weights = toy_scores.softmax(dim=-1)
toy_output = toy_weights @ toy_v</pre>
<p>Con d<sub>k</sub> = 2 si divide per √2 ≈ 1,41. I conti si fanno a mano:</p>
<ul>
<li><b>Punteggi</b>: q<sub>1</sub>·k<sub>1</sub> = 4 → 2,83; q<sub>1</sub>·k<sub>2</sub> = 0; q<sub>1</sub>·k<sub>3</sub> = 2 → 1,41. Riga 3: tutti 2 → 1,41.</li>
<li><b>Softmax della riga 1</b>: e<sup>2,83</sup> ≈ 16,9, e<sup>0</sup> = 1, e<sup>1,41</sup> ≈ 4,1; somma 22,0 → pesi <b>0,77; 0,05; 0,19</b>.</li>
<li><b>Uscita 1</b> = 0,77·(1, 0) + 0,05·(0, 1) + 0,19·(1, 1) = <b>(0,9546; 0,2321)</b>, come nell'uscita salvata. Il token 2 è simmetrico: (0,2321; 0,9546).</li>
<li><b>Token 3</b>: q<sub>3</sub> = (1, 1) somiglia ugualmente a tutte le key, pesi 1/3 ciascuno, uscita = media dei value = <b>(0,6667; 0,6667)</b>.</li>
</ul>
<p><b>Seconda variante</b> (cella 20): q<sub>1</sub> = q<sub>2</sub> = (2, 0), quindi anche k<sub>1</sub> = k<sub>2</sub>. Le righe 1 e 2 dei punteggi sono uguali (2,83; 2,83; 1,41), i pesi pure (0,45; 0,45; 0,11) e quindi anche le uscite: <b>(0,5542; 0,5542)</b> per entrambi. Poiché k<sub>1</sub> = k<sub>2</sub>, nessuna query può distinguere i token 1 e 2: il peso si divide a metà fra loro.</p>
<p><b>Figura (uscite salvate del notebook):</b> per ciascuna variante, a sinistra la matrice 3×3 dei punteggi scalati, a destra i pesi dopo la softmax per riga, con i valori scritti nelle caselle.</p>
<div class="box k"><b>Da saper fare</b><p>Rifare la riga 1 <b>senza</b> la scala: punteggi 4, 0, 2 → e<sup>4</sup> ≈ 54,6, 1, e<sup>2</sup> ≈ 7,4 → pesi 0,87; 0,02; 0,12 invece di 0,77; 0,05; 0,19. La distribuzione è più concentrata sul massimo: è l'effetto della saturazione della scheda 9, già visibile con d<sub>k</sub> = 2. Controllo veloce: ogni riga dei pesi somma a 1 (<code>Row sums: tensor([1., 1., 1.])</code>).</p></div>
""", img='img/nb_attenzione_giocattolo.png', printed=NB + 'celle 19–20')

s(9, "Domande su √d<sub>k</sub> e attenzione scritta a mano", """
<p><b>Domande del notebook</b> (cella 21) e risposte (cella 22):</p>
<ul>
<li><b>Cosa succede togliendo 1/√d<sub>k</sub>?</b> I punteggi hanno varianza ≈ d<sub>k</sub> invece di ≈ 1. Punteggi grandi <b>saturano</b> la softmax: quasi tutto il peso va alla key con il punteggio più alto, e i gradienti attraverso la softmax diventano molto piccoli (in una softmax quasi one-hot le derivate p<sub>i</sub>(δ<sub>ij</sub> − p<sub>j</sub>) sono quasi tutte nulle).</li>
<li><b>Due righe di query uguali?</b> Danno righe di punteggi q<sub>i</sub>Kᵀ uguali, quindi distribuzioni di attenzione e uscite ∑<sub>j</sub>A<sub>ij</sub>V<sub>j</sub> identiche (la cella 20 lo mostra).</li>
</ul>
<pre>def attention_from_scratch(q, k, v):
    # q, k, v: (B, h, T, d_k)
    scores = (q @ k.transpose(-2, -1)) / math.sqrt(q.shape[-1])   # (B, h, T, T)
    weights = scores.softmax(dim=-1)
    return weights @ v, weights

actual, weights = attention_from_scratch(q, k, v)                  # q, k, v: (2, 4, 5, 8)
expected = F.scaled_dot_product_attention(q, k, v, dropout_p=0.0)
# PASS: output torch.Size([2, 4, 5, 8]), weights torch.Size([2, 4, 5, 5])</pre>
<ul>
<li><code>k.transpose(-2, -1)</code> scambia solo le ultime due dimensioni: (B, h, T, d<sub>k</sub>) → (B, h, d<sub>k</sub>, T). Il prodotto <code>@</code> fra tensori a 4 dimensioni è un prodotto di matrici <b>per ogni coppia (batch, testa)</b>.</li>
<li><code>math.sqrt(q.shape[-1])</code>: la scala usa la larghezza della <b>singola testa</b> (qui 8), non D.</li>
<li>Il test confronta con <code>F.scaled_dot_product_attention</code> di PyTorch e controlla che ogni riga dei pesi sommi a 1. La funzione di PyTorch restituisce solo l'uscita: su GPU usa kernel fusi (FlashAttention e simili) che non scrivono mai la matrice A in memoria. Per questo, quando servono i pesi (rollout, schede 19–23), il notebook li chiede esplicitamente a <code>nn.MultiheadAttention</code>.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Ordini di grandezza senza scala: con d<sub>k</sub> = 24 (le teste di questo lab) i logit avrebbero deviazione standard √24 ≈ 4,9; con d<sub>k</sub> = 64 (ViT-B) √64 = 8. Una differenza di 8 fra due logit dà un rapporto di pesi e<sup>8</sup> ≈ 3000: la softmax è praticamente un argmax. Derivazione di Var(qᵀk) = d<sub>k</sub> nella <a href="#L17">L17</a>, slide 30.</p></div>
""", printed=NB + 'celle 21–24')

s(10, "Perché QKV ha dimensione 3D: split_qkv", """
<span class="f">[Q | K | V] = XW<sup>QKV</sup>,   W<sup>QKV</sup> ∈ ℝ<sup>D×3D</sup></span>
<ul>
<li>Ogni token produce <b>tre</b> vettori (query, key, value), ciascuno di larghezza D. Concatenati fanno 3D, e una sola moltiplicazione di matrici li calcola tutti insieme (L17, slide 30).</li>
<li>Con h teste, d<sub>k</sub> = D/h: (B, N+1, D) → (B, N+1, 3D) → 3 tensori (B, h, N+1, d<sub>k</sub>). Qui D = 96, h = 4: teste da <b>24</b> dimensioni, 3D = <b>288</b>.</li>
<li><b>3D significa Q, K e V, non tre teste.</b></li>
</ul>
<p><b>Domande del notebook</b> (cella 25), con le risposte della cella 26:</p>
<ul>
<li><b>Perché 3D e non hD?</b> Le h teste <b>dividono</b> ciascuno dei tre vettori in h pezzi da d<sub>k</sub>, quindi la larghezza totale resta 3D per ogni h. Un'uscita da hD per ciascuno di Q, K, V darebbe a ogni testa la larghezza piena D: un altro modello, h volte più grande.</li>
<li><b>Quanti pesi?</b> W<sup>QKV</sup> ha 3D² pesi: 3·96² = <b>27 648</b> (più 288 bias).</li>
<li><b>Cambiando h a D fisso cambia il numero di parametri?</b> No: cambia solo come le 3D uscite vengono suddivise.</li>
</ul>
<pre>def split_qkv(qkv, num_heads):
    B, T, three_D = qkv.shape                       # (B, T, 3D)
    d_k = three_D // (3 * num_heads)
    qkv = qkv.reshape(B, T, 3, num_heads, d_k).permute(2, 0, 3, 1, 4)
    return qkv[0], qkv[1], qkv[2]                   # ciascuno (B, h, T, d_k)</pre>
<ul>
<li>Il <code>reshape(B, T, 3, h, d_k)</code> legge le 288 uscite di un token come [Q (96) | K (96) | V (96)], e ogni blocco da 96 come 4 teste da 24. È la stessa disposizione dei pesi <code>in_proj_weight</code> di <code>nn.MultiheadAttention</code>: per questo nell'esercizio B (scheda 27) si possono copiare i pesi e ottenere lo stesso risultato.</li>
<li><code>permute(2, 0, 3, 1, 4)</code> porta gli assi nell'ordine (3, B, h, T, d<sub>k</sub>): prima si sceglie Q, K o V, poi per ogni batch e testa si ha la matrice T×d<sub>k</sub>.</li>
<li><code>split_heads</code>, definita nella stessa cella, fa la stessa cosa per un solo tensore (B, T, D) → (B, h, T, d<sub>k</sub>), ma il notebook non la usa.</li>
</ul>
""", printed=NB + 'celle 25–27')

s(11, "Multi-head self-attention a mano", """
<span class="f">head<sub>i</sub> = Attention(Q<sub>i</sub>, K<sub>i</sub>, V<sub>i</sub>),   MHSA(X) = Concat(head<sub>1</sub>, …, head<sub>h</sub>) W<sup>O</sup>,   W<sup>O</sup> ∈ ℝ<sup>D×D</sup></span>
<pre>X             [T, 96]
Linear(QKV)   [T, 288]
Q, K, V       [4, T, 24] ciascuno
A             [4, T, T]
head outputs  [4, T, 24]
concat        [T, 96]
output linear [T, 96]</pre>
<pre>class MyMultiHeadAttention(nn.Module):
    def __init__(self, dim, num_heads):
        self.qkv = nn.Linear(dim, 3 * dim)
        self.out_proj = nn.Linear(dim, dim)
    def forward(self, x):
        B, T, D = x.shape
        q, k, v = split_qkv(self.qkv(x), self.num_heads)
        attended, weights = attention_from_scratch(q, k, v)
        merged = attended.transpose(1, 2).reshape(B, T, D)
        return self.out_proj(merged)</pre>
<ul>
<li><code>attended.transpose(1, 2)</code> riporta (B, h, T, d<sub>k</sub>) a (B, T, h, d<sub>k</sub>), poi <code>reshape</code> affianca le uscite delle teste di ciascun token: è la concatenazione. Senza la trasposizione il codice non darebbe errore ma mescolerebbe i token (scheda 27).</li>
<li>La cella 31 controlla forma d'uscita (2, 7, 96) e che il gradiente arrivi all'ingresso, finito.</li>
</ul>
<p><b>Domande del notebook</b> (cella 28):</p>
<ul>
<li><b>Una testa elabora solo 1/h delle patch?</b> No: ogni testa guarda <b>tutti</b> i token, ma in un sottospazio di d<sub>k</sub> = D/h dimensioni. Si dividono le <b>dimensioni</b>, non i token.</li>
<li><b>Raddoppiando h a D fisso?</b> d<sub>k</sub> si dimezza (24 → 12), i parametri non cambiano, le moltiplicazioni di QKᵀ e AV restano h·T²·d<sub>k</sub> = T²D, ma le matrici di attenzione da salvare raddoppiano (2h matrici T×T) e ogni testa misura la somiglianza in uno spazio più piccolo.</li>
<li><b>Perché 4D² parametri?</b> W<sup>QKV</sup> ha 3D² pesi, W<sup>O</sup> ne ha D²: in tutto 4D² (più 4D di bias). Con D = 96: 36 864 + 384 = 37 248 per blocco.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 26, § 26.6.3 Multihead Self-Attention; Prince § 12.3.3</b>
<p>Il visionbook motiva le teste così: con una sola testa la somiglianza fra due token è un'unica forma bilineare t<sub>i</sub>ᵀW<sub>q</sub>ᵀW<sub>k</sub>t<sub>j</sub>, cioè un solo criterio (per esempio il colore); con k teste in parallelo si misurano k criteri diversi, poi si concatenano le uscite e una matrice appresa W<sub>MSA</sub> le ricombina (eq. 26.7, è la W<sup>O</sup> del notebook). Il Prince (eq. 12.10–12.12) aggiunge che di solito le teste hanno dimensione D/H per un'implementazione efficiente, che le uscite si concatenano in verticale (colonne come token) e si ricombinano con Ω<sub>c</sub>, e che più teste sembrano necessarie perché l'attenzione funzioni bene, forse perché rendono il training più robusto a inizializzazioni sfortunate.</p>
<p>{V26}</p></div>
""".replace('{V26}', V26), printed=NB + 'celle 28–31')

# ---------------------------------------------------------------- modello

s(12, "Il blocco encoder pre-LayerNorm", """
<span class="f">X′ = X + MHSA(LN(X)),   X″ = X′ + MLP(LN(X′))</span>
<pre>class EncoderBlock(nn.Module):
    def __init__(self, dim=96, heads=4, mlp_ratio=4):
        self.norm1 = nn.LayerNorm(dim)
        self.attn = nn.MultiheadAttention(dim, heads, batch_first=True)
        self.norm2 = nn.LayerNorm(dim)
        self.mlp = nn.Sequential(nn.Linear(dim, mlp_ratio * dim), nn.GELU(),
                                 nn.Linear(mlp_ratio * dim, dim))
    def forward(self, x):
        h = self.norm1(x)
        attended, _ = self.attn(h, h, h, need_weights=False)
        x = x + attended
        return x + self.mlp(self.norm2(x))</pre>
<ul>
<li>L'<b>attenzione</b> mescola informazione <b>fra</b> token; l'<b>MLP</b> trasforma <b>ogni</b> token per conto suo (96 → 384 → 96 con GELU).</li>
<li><b>Pre-norm</b> (L17, slide 31): la LayerNorm sta dentro il ramo, prima di attenzione e MLP; il cammino residuo <code>x + …</code> resta un'identità pulita, e ogni blocco impara una correzione.</li>
<li>Il modello usa <code>nn.MultiheadAttention</code> di PyTorch, che fa esattamente quello della scheda 11 (verificato nell'esercizio B). <code>self.attn(h, h, h)</code>: query, key e value vengono dallo stesso ingresso, cioè <b>self</b>-attention.</li>
<li><code>batch_first=True</code> è essenziale: per default <code>nn.MultiheadAttention</code> si aspetta (T, B, D). Senza, con un batch (32, 197, 96) l'attenzione verrebbe calcolata fra le 32 immagini invece che fra i 197 token, senza alcun errore.</li>
<li><code>need_weights=False</code> evita di restituire (e mediare) i pesi e permette il percorso veloce; per il rollout si userà <code>True</code>.</li>
<li>LayerNorm normalizza ogni token sulle sue 96 coordinate, non dipende dal batch e fa lo stesso calcolo in training e in valutazione (L17, slide 34).</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Parametri di un blocco con D = 96: attenzione 4D² + 4D = 37 248; MLP D·4D + 4D + 4D·D + D = 8D² + 5D = 74 208; due LayerNorm 2·2D = 384. Totale <b>111 840</b>, circa 12D² (L17, slide 32), con l'MLP che ne pesa due terzi.</p></div>
<div class="box b"><b>Dal libro · cap. 26, § 26.7; Prince § 12.4</b>
<p>Il visionbook descrive il ViT con la stessa disposizione: normalizzazione prima di ogni attenzione e di ogni MLP per token, residui attorno a ciascuno (fig. 26.14). La chiama "token norm" e la descrive senza parametri appresi; <code>nn.LayerNorm</code> ha invece scala γ e spostamento β appresi (2D parametri), come la layernorm del § 12.7.3 dello stesso libro. Il Prince (fig. 12.7, eq. 12.13) descrive il transformer originale <b>post-norm</b>, con la LayerNorm dopo la somma; nelle note del cap. 12 spiega che quella posizione fa ridursi i gradienti nella propagazione all'indietro e rende necessario il warm-up del learning rate: è uno dei motivi per cui il ViT usa la pre-norm.</p>
<p>{V26}</p></div>
""".replace('{V26}', V26), sec=("l18-vit", "Il modello ViT", 'schede 12–14'), printed=NB + 'celle 32–33')

s(13, "[CLS], embedding posizionali e la classe ViT", """
<span class="f">Z<sub>0</sub> = [x<sub>cls</sub>; z<sub>1</sub>; …; z<sub>N</sub>] + E<sub>pos</sub>,   E<sub>pos</sub> ∈ ℝ<sup>(N+1)×D</sup></span>
<pre>self.cls_token = nn.Parameter(torch.zeros(1, 1, dim))
self.pos_embed = nn.Parameter(torch.zeros(1, n + 1, dim))
nn.init.normal_(self.cls_token, std=0.02); nn.init.normal_(self.pos_embed, std=0.02)
...
def forward_features(self, images):
    tokens = self.patch_embed(images)                       # (B, 196, 96)
    cls = self.cls_token.expand(images.size(0), -1, -1)     # (B, 1, 96)
    tokens = torch.cat([cls, tokens], dim=1) + self.pos_embed
    for block in self.blocks:
        tokens = block(tokens)
    return self.norm(tokens)                                # (B, 197, 96)
def forward(self, images):
    return self.head(self.forward_features(images)[:, 0])  # (B, 10)</pre>
<ul>
<li>L'attenzione da sola non sa da dove viene una patch: rimescolando i token d'ingresso le uscite si rimescolano allo stesso modo (L17, slide 27). Il ViT aggiunge un vettore <b>appreso</b> per ogni posizione, <b>una sola volta</b>, prima del primo blocco.</li>
<li><b>[CLS]</b> è un token appreso in posizione 0, uguale per tutte le immagini; <code>expand</code> lo ripete sul batch senza copiarlo in memoria. Non corrisponde a nessuna patch: raccoglie informazione da tutte attraverso l'attenzione, e la sua uscita finale, dopo l'ultima LayerNorm, va alla testa lineare.</li>
<li>Entrambi partono da rumore piccolo (deviazione standard 0,02). Nulla dice al modello che la patch 15 sta sotto la patch 1: deve impararlo (scheda 21).</li>
<li>Uscite salvate: <b>317 674 parametri</b>, feature <code>[2, 197, 96]</code>, logit <code>[2, 10]</code>. Rispetto a ViT-B/16: 2 blocchi invece di 12, D = 96 invece di 768, 4 teste invece di 12, stesse patch 16×16 e immagini 224×224.</li>
</ul>
<div class="box k"><b>Da saper fare</b><table>
<tr><th>parte</th><th>conto</th><th>parametri</th></tr>
<tr><td>patch embedding</td><td>768·96 + 96</td><td>73 824</td></tr>
<tr><td>[CLS] + posizioni</td><td>96 + 197·96</td><td>19 008</td></tr>
<tr><td>attenzione (2 blocchi)</td><td>2·(4D² + 4D)</td><td>74 496</td></tr>
<tr><td>MLP (2 blocchi)</td><td>2·(8D² + 5D)</td><td>148 416</td></tr>
<tr><td>LayerNorm (5)</td><td>5·2D</td><td>960</td></tr>
<tr><td>testa</td><td>96·10 + 10</td><td>970</td></tr>
<tr><td><b>totale</b></td><td></td><td><b>317 674</b></td></tr>
</table><p>Le LayerNorm sono cinque: due per blocco più quella finale.</p></div>
<div class="box b"><b>Dal libro · cap. 26, § 26.7 e 26.11; Prince § 12.10.2</b>
<p>Il visionbook <b>non usa il token [CLS]</b>: per classificare somma tutti i token d'uscita e applica uno strato lineare, un pooling globale come il gap delle CNN (è la "mean pooling" della scheda 25). Anche le posizioni sono diverse: il libro usa un codice periodico fisso, fatto di soli seni a frequenze diverse (eq. 26.12), e lo <b>concatena</b> al token; il ViT <b>somma</b> un embedding <b>appreso</b>. Il Prince descrive il ViT come nel notebook: patch 16×16, proiezione lineare appresa, codifiche posizionali 1D apprese, token &lt;cls&gt; mappato dall'ultimo strato nelle probabilità di classe, pre-training supervisionato su 303 milioni di immagini.</p>
<p>{V26}</p></div>
<div class="box x"><b>Approfondimento: le scelte dell'articolo originale</b><p>Dosovitskiy et al. (2021) prendono il [CLS] da BERT. Nelle appendici riportano che classificare con la media dei token (gap) funziona altrettanto bene, purché si cambi il learning rate, e che embedding posizionali "consapevoli del 2D" (riga e colonna separate, o relativi) non danno guadagni significativi rispetto a quelli 1D appresi: il modello impara da solo la struttura 2D (scheda 21). ViT-B/16 ha D = 768, 12 teste, 12 blocchi, MLP da 3072: la stessa ricetta del notebook in grande.</p></div>
""".replace('{V26}', V26), printed=NB + 'celle 34–35')

s(14, "La sequenza d'ingresso: 197 × 96", """
<pre>input_patches = model.patch_embed(images[:1])
input_cls = model.cls_token.expand(1, -1, -1)
input_tokens = torch.cat([input_cls, input_patches], dim=1) + model.pos_embed
# Sequence shape: (1, 197, 96)
# [CLS] token, first 12 values: [ 0.03  0.04 -0.039 -0.008 ...]
# Patch token 1, first 12 values: [ 0.099 -0.055 -0.778  0.292 ...]</pre>
<ul>
<li>È Z<sub>0</sub>, la sequenza che entra nel primo blocco, per il modello <b>prima del training</b> (la cella viene prima della 39).</li>
<li><b>Riga 0</b> ([CLS]): valori piccolissimi, perché è la somma di due vettori casuali con deviazione standard 0,02 (circa 0,03 in totale). Nella figura è la riga sottile sopra la linea nera.</li>
<li><b>Righe 1–196</b>: dominate dal patch embedding, con valori fino a ±3; l'embedding posizionale (0,02) all'inizio non si vede quasi. Durante il training dovrà crescere per far contare la posizione.</li>
<li>Si riconosce la stessa struttura della scheda 6: periodicità di 14 righe (le righe della griglia) e le ultime 14 righe diverse dalle altre.</li>
</ul>
<p><b>Figura (uscita salvata del notebook):</b> la matrice 197×96, una riga per token (0 = [CLS]) e una colonna per coordinata.</p>
<div class="box k"><b>Da saper fare</b><p>Forme dall'immagine alla classe, per un'immagine: 3×224×224 → conv 16/16 → 96×14×14 → flatten e transpose → 196×96 → [CLS] → 197×96 → + E<sub>pos</sub> (197×96) → 2 blocchi (197×96 → 197×96) → LayerNorm → riga 0 (96) → testa → 10 logit. Ogni blocco conserva la forma: per questo se ne possono impilare quanti si vuole.</p></div>
""", img='img/nb_sequenza_ingresso.png', printed=NB + 'celle 36–37')

# ---------------------------------------------------------------- training e valutazione

s(15, "Il ciclo di training con AdamW", """
<pre>def run_epoch(model, loader, criterion, optimizer=None):
    training = optimizer is not None
    model.train(training)
    for xb, yb in loader:
        with torch.set_grad_enabled(training):
            logits = model(xb); loss = criterion(logits, yb)
            if training:
                optimizer.zero_grad(set_to_none=True)
                loss.backward()
                optimizer.step()
        total_loss += loss.item() * len(xb)
        total_correct += (logits.argmax(1) == yb).sum().item()
    return total_loss / total_count, total_correct / total_count

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.05)</pre>
<ul>
<li>Lo stesso ciclo della <a href="#L16">L16</a> (forward, loss, backward, step), ma in una sola funzione usata sia per il training sia per la valutazione: senza ottimizzatore mette il modello in <code>eval</code> e disattiva il gradiente con <code>set_grad_enabled(False)</code>.</li>
<li><code>zero_grad(set_to_none=True)</code> mette i gradienti a <code>None</code> invece che a zero: stesso effetto, meno memoria e meno operazioni.</li>
<li><code>loss.item() * len(xb)</code>: la loss è la media sul batch, moltiplicandola per la dimensione si ottiene la somma, così l'ultimo batch più piccolo (29 immagini) pesa il giusto.</li>
<li>L'accuratezza di training è calcolata <b>durante</b> l'epoca, su immagini con augmentation e con pesi che cambiano batch per batch: è una stima pessimista rispetto al modello di fine epoca.</li>
<li><b>AdamW</b>: Adam (learning rate adattivo per ogni parametro, con momento) con <b>weight decay disaccoppiato</b>: i pesi vengono ridotti di un fattore (1 − η·λ) a ogni passo, separatamente dal gradiente. lr = 3·10<sup>−4</sup> e λ = 0,05 sono valori tipici per i transformer.</li>
</ul>
<p><b>Uscite salvate</b>: epoca 1 train acc 0,340, val 0,418 (loss 1,886 e 1,707); epoca 40 train 0,766, val 0,675 (loss 0,684 e 1,031); migliore validazione <b>0,708 all'epoca 39</b>. Curve nella scheda 16.</p>
<div class="box w"><b>Attenzione: il testo parla di una sola epoca, il codice ne fa 40</b>
<p>La cella 38 dice "We train for one epoch by default (<code>EPOCHS = 1</code> near the dataset setup)" e "A small ViT trained from scratch for one epoch is not expected to achieve strong accuracy"; il commento della cella 5 dice che un'epoca "è solo una dimostrazione"; la cella 58 chiede di confrontare le mappe "with the one-epoch model above"; la domanda 2 della cella 53 chiede perché la mappa delle posizioni del nostro modello sia "mostly noise". Ma il codice ha <code>EPOCHS = 40</code> e <b>tutte</b> le uscite salvate sono a 40 epoche: il log fino a "epoch 40/40", le curve, il test 0,668, il rollout, il titolo "Our ViT after 40 epoch(s)" nella figura delle posizioni, e la cella 48 che comincia con "After 40 epochs". Il testo è rimasto da una versione precedente del notebook.</p>
<p>Versione corretta: leggere tutto il notebook come "40 epoche". Che cosa cambierebbe con una sola epoca lo abbiamo misurato (sezione <a href="#l18-risultati">Risultati</a>): test <b>0,419</b> invece di 0,668, rollout e similarità delle posizioni quasi di solo rumore. È a un modello da 1 epoca che si riferiscono la domanda sul "rumore" e il confronto della cella 58.</p></div>
<div class="box b"><b>Dal libro · Prince § 6.4 e note dei cap. 9 e 12</b>
<p>Il § 6.4 spiega Adam: normalizza ogni passo con una stima del momento secondo del gradiente, quindi ogni parametro ha in pratica il suo learning rate, e aggiunge il momento. Nelle note del cap. 9 il Prince spiega perché esiste AdamW: con lo SGD il weight decay equivale alla regolarizzazione L2, con Adam no, perché il learning rate è diverso per ogni parametro; AdamW (Loshchilov e Hutter 2019) applica il decadimento direttamente ai pesi e funziona meglio. Nelle note del cap. 12: addestrare i transformer richiede di solito sia Adam sia un <b>warm-up</b> del learning rate, per un intreccio di cause (normalizzazione, residui, gradienti di query e key più piccoli di quelli dei value).</p></div>
<div class="box x"><b>Approfondimento: le scelte di training del notebook</b>
<ul>
<li><b>Weight decay su tutti i parametri</b>: <code>AdamW(model.parameters(), …)</code> applica λ = 0,05 anche a bias, γ e β delle LayerNorm, <code>pos_embed</code> e <code>cls_token</code>. Le ricette dei ViT di solito escludono bias e parametri di normalizzazione (e spesso le posizioni) con due gruppi di parametri. Spingere a zero gli embedding posizionali, che partono già piccoli, rema contro il loro apprendimento.</li>
<li><b>Niente warm-up né scheduler</b>: lr costante per 40 epoche. Le ricette standard (articolo del ViT, DeiT) usano warm-up lineare e poi decadimento a coseno; la validazione oscillante della scheda 16 è coerente con un lr che non scende mai.</li>
<li>Su un modello da 2 blocchi i problemi di ottimizzazione che motivano il warm-up sono molto più lievi: il training funziona lo stesso, e per un lab la semplicità vale più di qualche punto di accuratezza.</li>
</ul></div>
""", sec=("l18-train", "Training e valutazione", 'schede 15–17'), printed=NB + 'celle 38–39')

s(16, "Le curve di training", """
<pre>ax[0].plot(history["train_loss"]); ax[0].plot(history["val_loss"])
ax[1].plot(history["train_acc"]);  ax[1].plot(history["val_acc"])</pre>
<p><b>Figura (uscita salvata del notebook):</b> a sinistra la cross-entropy, a destra l'accuratezza, per epoca (asse da 0 a 39), training in blu e validazione in arancio.</p>
<ul>
<li><b>Prime epoche</b>: la validazione è <b>sopra</b> il training (epoca 1: 0,418 contro 0,340). Non è un errore: l'accuratezza di training è misurata con augmentation (ritagli fino al 65% dell'area) e mentre i pesi cambiano, quella di validazione su ritagli centrali e con il modello di fine epoca.</li>
<li><b>Dall'epoca 15 circa</b> le curve si separano: la loss di training continua a scendere (fino a 0,684) e l'accuratezza a salire (0,766), mentre la validazione si ferma intorno a 0,67–0,70, con loss attorno a 1,0. È l'inizio dell'<b>overfitting</b>: il modello migliora sui dati visti più che su quelli nuovi.</li>
<li>La validazione <b>oscilla</b> molto da un'epoca all'altra (0,643 all'epoca 25, 0,708 all'epoca 39, 0,675 all'epoca 40): learning rate costante e 1962 immagini di validazione, dove un punto percentuale sono circa 20 immagini.</li>
<li>Per un modello da 0,3 milioni di parametri addestrato da zero su 9469 immagini, 67% su 10 classi è un risultato ragionevole; un ViT-B/16 preaddestrato riconosce le 4 immagini di prova senza errori (scheda 22).</li>
</ul>
<div class="box x"><b>Approfondimento: quale modello tenere</b><p>Il notebook valuta il modello dell'<b>ultima</b> epoca (validazione 0,675), non il migliore (0,708 all'epoca 39). Di solito si salva un checkpoint ogni volta che la validazione migliora e alla fine si ricarica il migliore (o si ferma il training quando smette di migliorare, early stopping). È proprio a questo che serve la validazione: scegliere epoca e iperparametri, e solo dopo misurare una volta il test. Con oscillazioni così ampie la differenza fra le due scelte è in buona parte rumore.</p></div>
<div class="box b"><b>Dal libro · cap. 11 The Problem of Generalization, § 11.2</b><p>Il libro distingue underfitting (errore alto anche sul training) e overfitting (errore basso sul training e alto sui dati nuovi): il divario fra le curve blu e arancio dopo l'epoca 15 è il secondo caso, lieve. La cura è la regolarizzazione (qui augmentation e weight decay) o più dati. <a href="https://visionbook.mit.edu/problem_of_generalization.html">visionbook.mit.edu · cap. 11</a></p></div>
""", img='img/nb_curve.png', printed=NB + 'cella 40')

s(17, "Valutazione sul test e predizioni", """
<pre>test_loss, test_acc = run_epoch(model, test_loader, criterion)
# held-out test accuracy: 0.668, test loss: 1.016
with torch.no_grad():
    model.eval()
    examples, targets = next(iter(test_loader))
    predictions = model(examples[:8].to(device)).argmax(-1).cpu()</pre>
<ul>
<li>Il test (1963 immagini) si guarda <b>una volta</b>, alla fine: <b>0,668</b>, in linea con la validazione delle ultime epoche (0,675). Il caso darebbe 0,10.</li>
<li><code>test_loader</code> non mescola, quindi <code>examples</code> sono sempre le prime 32 immagini del test: le stesse che il notebook userà per feature, rollout e confronto con ViT-B/16.</li>
<li>Nella figura <b>5 predizioni giuste su 8</b>: motosega, le tre chiese, la tinca. Errori: il lettore di cassette predetto "golf ball", i due camion della spazzatura predetti "chain saw" e "cassette player". Dopo 1 epoca (nostra esecuzione) le giuste erano solo 1 su 8.</li>
</ul>
<p><b>Figura (uscita salvata del notebook):</b> le prime 8 immagini del test, con etichetta vera e predetta.</p>
<div class="box w"><b>Attenzione: qui model.eval() non disattiva nessun dropout</b>
<p>La cella 41 dice che <code>model.eval()</code> "disables training-time behavior such as dropout". In generale è vero, ma questo modello non ha né dropout né BatchNorm: <code>nn.MultiheadAttention</code> ha <code>dropout=0.0</code> per default (verificato), l'MLP non contiene <code>nn.Dropout</code>, e la LayerNorm fa lo stesso calcolo in training e in valutazione. Per questo modello <code>train()</code> ed <code>eval()</code> danno esattamente le stesse uscite.</p>
<p>Versione corretta: <code>model.eval()</code> va comunque chiamato (è l'abitudine giusta e serve appena si aggiunge un dropout), ma qui l'unica cosa che conta è <code>torch.no_grad()</code>, che evita di costruire il grafo per il backward. Lo stesso vale per il ViT-B/16 di torchvision: ha moduli di dropout, ma con probabilità 0 (verificato).</p></div>
""", img='img/nb_predizioni.png', printed=NB + 'celle 41–42')

# ---------------------------------------------------------------- dentro il ViT

s(18, "I canali delle feature come mappe 14×14", """
<pre>tokens = model.forward_features(examples[:1]).cpu()      # (1, 197, 96)
patch_features = tokens[:, 1:]                           # togli [CLS]: (1, 196, 96)
grid = patch_features.reshape(1, 14, 14, 96)
axes[i + 1].imshow(grid[0, :, :, i])                     # canali 0, 1, 2, 3</pre>
<ul>
<li>È l'idea della <a href="#L17">L17</a>, slide 38: tolto il [CLS], i 196 token di patch tornano nella <b>griglia</b> 14×14 da cui venivano, e ogni coordinata j dell'embedding diventa una mappa F<sub>j</sub> ∈ ℝ<sup>14×14</sup>, come un canale di una feature map di una CNN.</li>
<li>Il <code>reshape(1, 14, 14, 96)</code> è corretto perché i token sono in ordine raster (scheda 5): il token 1 + 14r + c è la patch (r, c).</li>
<li>Sono <b>canali di feature</b>, non probabilità di classe né pesi di attenzione. Le feature sono quelle d'uscita, dopo la LayerNorm finale.</li>
</ul>
<p><b>Figura (uscita salvata del notebook):</b> la prima immagine del test (un uomo con le cuffie rosse che scolpisce un orso di legno con la motosega, su un prato) e i canali 0–3 dopo 40 epoche. Le mappe sono a blocchi 14×14 e piuttosto <b>rumorose</b>; si intravede la scena (nel canale 0 la zona del prato, a sinistra, è più chiara e uniforme), ma nessun canale isola un oggetto.</p>
<div class="box k"><b>Da saper fare</b><p>Collegare alla <a href="#L16">L16</a>: lì la feature map di <code>conv4_x</code> era 256×8×8 e ogni posizione aveva campo recettivo 53; qui la "feature map" è 96×14×14 e ogni token, dopo il primo blocco, ha già visto <b>tutta</b> l'immagine (campo recettivo globale). Per vedere tutti i 96 canali insieme si può usare la stessa PCA a 3 componenti della L16, con i 196 token come campioni.</p></div>
""", sec=("l18-dentro", "Dentro il ViT: feature, posizioni, attenzione", 'schede 18–23'), img='img/nb_canali.png', printed=NB + 'celle 43–44')

s(19, "Attention rollout: la teoria e gli stadi", """
<p>Una matrice di attenzione descrive le interazioni in <b>un</b> blocco. Dopo più blocchi un token può ricevere informazione passando per token intermedi. Il rollout (L17, slide 36; Abnar e Zuidema 2020) compone i blocchi:</p>
<span class="f">Ā<sup>(l)</sup> = (1/h) ∑<sub>i</sub> A<sub>i</sub><sup>(l)</sup>,   Ã<sup>(l)</sup> = row_normalize(Ā<sup>(l)</sup> + I),   R<sup>(0)</sup> = I,   R<sup>(l)</sup> = Ã<sup>(l)</sup> R<sup>(l−1)</sup></span>
<ul>
<li><b>Media sulle teste</b>, poi <b>+ I</b> per il cammino residuo: il token passa anche "così com'è" attraverso il <code>x + …</code>. Siccome ogni riga di Ā somma a 1, la normalizzazione dà semplicemente Ã = (Ā + I)/2: metà peso al residuo, metà all'attenzione.</li>
<li>Si moltiplica in <b>ordine di forward</b>: R<sup>(L)</sup> = Ã<sup>(L)</sup>⋯Ã<sup>(1)</sup>. La riga 0 di R stima quanto il [CLS] d'uscita "viene" da ciascun token d'ingresso; tolta la colonna del [CLS], i 196 valori si rimodellano in 14×14 e si interpolano a 224×224 per sovrapporli all'immagine.</li>
<li>È una <b>visualizzazione approssimata</b> del flusso di informazione, non una spiegazione causale della predizione: ignora value, MLP e non linearità.</li>
</ul>
<pre>for block in model.blocks:
    normed = block.norm1(tokens)
    attended, weights = block.attn(normed, normed, normed,
                                   need_weights=True, average_attn_weights=False)   # (B, h, T, T)
    tokens = tokens + attended
    tokens = tokens + block.mlp(block.norm2(tokens))
    mean_attn = weights.mean(dim=1)
    adjusted = (mean_attn + ident) / (mean_attn + ident).sum(dim=-1, keepdim=True)
    composed = adjusted @ composed</pre>
<ul>
<li>La funzione ripete a mano il forward di <code>EncoderBlock</code> (stessi passi, stesso ordine) per poter chiedere i pesi per testa con <code>average_attn_weights=False</code>.</li>
</ul>
<p><b>Figura:</b> a sinistra le uscite salvate del docente (40 epoche), a destra la nostra esecuzione a 1 epoca, per la prima immagine del test (la motosega). In alto l'attenzione del [CLS] in ciascun blocco, in basso il rollout cumulato. A 40 epoche il blocco 1 concentra quasi tutto su <b>una</b> patch in alto al centro (le cuffie rosse, scheda 20), il blocco 2 è più diffuso con qualche picco nella parte bassa; il rollout dopo il blocco 2 è ancora dominato dal picco del blocco 1, perché la composizione conserva quello che il blocco 1 ha già raccolto. Dopo 1 epoca il blocco 2 guarda una grande zona centrale indistinta.</p>
<div class="box k"><b>Da saper fare</b><p>Dimostrare che ogni riga di R somma a 1: Ã ha righe non negative che sommano a 1 (matrice stocastica per righe); il prodotto di due matrici stocastiche per righe lo è ancora, perché (ÃB)<b>1</b> = Ã(B<b>1</b>) = Ã<b>1</b> = <b>1</b>. Quindi la riga del [CLS] è una distribuzione sui 197 token d'ingresso. Saper spiegare perché senza + I il rollout sarebbe sbagliato: ignorerebbe che il residuo porta avanti ogni token, e dopo molti blocchi il prodotto delle sole attenzioni tende a righe tutte uguali.</p></div>
<div class="box x"><b>Approfondimento: Abnar e Zuidema (2020)</b><p>"Quantifying Attention Flow in Transformers" propone due metodi: <b>attention rollout</b> (il prodotto delle matrici con l'identità, quello del notebook) e <b>attention flow</b>, che tratta il grafo dei blocchi come una rete di flusso e calcola il flusso massimo da ogni token d'ingresso all'uscita (più costoso). Entrambi correlano con l'importanza misurata togliendo i token o con i gradienti molto meglio dell'attenzione grezza dell'ultimo strato. L'articolo del ViT (Dosovitskiy et al. 2021, fig. 6) usa il rollout per le immagini del cane e dell'aereo della slide 36.</p></div>
""", img='img/nb_rollout_stadi.png', printed=NB + 'celle 45–46')

s(20, "Il rollout del nostro modello", """
<pre>heat = attention_rollout(model, examples[:4])          # (4, 14, 14)
upsampled = F.interpolate(heat[i][None, None], size=(224, 224),
                          mode="bilinear", align_corners=False)[0, 0]
axes[1, i].imshow(pic); axes[1, i].imshow(upsampled, cmap="jet", alpha=0.55)</pre>
<ul>
<li>Stessa funzione della scheda 19, su 4 immagini del test; restituisce la riga del [CLS] senza la sua colonna, 14×14.</li>
<li>L'interpolazione bilineare serve solo alla visualizzazione: l'informazione vera è a risoluzione 14×14, una casella per patch.</li>
</ul>
<p><b>Figura (uscita salvata del notebook, 40 epoche):</b> in alto le immagini, in basso il rollout sovrapposto. Cosa si vede, come descritto nella cella 48 e verificato sulla figura:</p>
<ul>
<li><b>Motosega</b>: il picco è sulle <b>cuffie rosse</b>, non sulla motosega. Le protezioni per le orecchie compaiono in molte foto di motoseghe: il modello può usarle come indizio di <b>contesto</b>.</li>
<li><b>Lettore di cassette</b>: picchi su dettagli piccoli e contrastati (il comando laterale a destra, i pulsanti colorati).</li>
<li><b>Chiesa (interno)</b>: piccole macchie ai bordi, poco sull'altare, mappa quasi diffusa.</li>
<li><b>Chiesa (esterno)</b>: la torre illuminata e il suo <b>riflesso</b> sul selciato bagnato: il modello non separa l'oggetto dalla sua immagine riflessa.</li>
</ul>
<p>Il commento del notebook: un modello piccolo addestrato da zero tende a guardare regioni luminose, colorate e contrastate, e il contesto correlato con l'etichetta. Confronto con 1 epoca nella sezione <a href="#l18-risultati">Risultati</a>.</p>
<div class="box x"><b>Approfondimento: il test di occlusione</b><p>La cella 48 propone di verificare se le cuffie guidano davvero la predizione "chain saw": coprirle (per esempio con un quadrato grigio, o con zeri dopo la normalizzazione) e confrontare la probabilità della classe. È un test <b>causale</b>, a differenza del rollout: misura l'effetto di un intervento sull'ingresso. Fatto in modo sistematico (un quadrato che scorre su tutta l'immagine e la mappa del calo di probabilità) è l'occlusion sensitivity di Zeiler e Fergus (2014). Risultati del test nella sezione <a href="#l18-soluzioni">Soluzioni</a>.</p></div>
""", img='img/nb_rollout_nostro.png', printed=NB + 'celle 47–48')

s(21, "ViT-B/16 preaddestrato e la similarità delle posizioni", """
<pre>pretrained_vit = vit_b_16(weights=ViT_B_16_Weights.IMAGENET1K_V1).to(device).eval()
# Pretrained ViT-B/16: 12 blocks; 768 embedding dimensions
def pos_similarity_grid(pos):                         # pos: (1+N, D)
    p = F.normalize(pos[1:].float(), dim=-1)           # togli [CLS], vettori unitari (196, D)
    sim = (p @ p.T).reshape(14, 14, 14, 14)            # [riga q, colonna q, riga k, colonna k]
    return sim.permute(0, 2, 1, 3).reshape(196, 196)</pre>
<ul>
<li>Per ogni posizione si calcola la <b>similarità coseno</b> fra il suo embedding posizionale e quelli di tutte le 196 posizioni: una mappa 14×14. Le 196 mappe vengono affiancate nella disposizione della griglia: il quadratino in riga r e colonna c è la mappa della posizione (r, c). È la fig. 7 di Dosovitskiy et al. (2021), la stessa della slide 35 della <a href="#L17">L17</a>.</li>
<li><code>permute(0, 2, 1, 3)</code> porta gli assi in (riga q, riga k, colonna q, colonna k): così il <code>reshape</code> a 196×196 mette le mappe una accanto all'altra invece di intrecciarle. Codice corretto.</li>
</ul>
<p><b>Figura (uscite salvate del notebook):</b> in alto, a sinistra il nostro modello dopo 40 epoche, a destra ViT-B/16; in basso tre mappe ingrandite di ViT-B/16, per le posizioni (0, 0), (7, 7) e (3, 11).</p>
<ul>
<li><b>Il nostro modello</b>: ogni quadratino è chiaro sul bordo o al centro. Le posizioni del bordo somigliano alle altre del bordo, quelle interne alle interne: ha imparato solo "<b>centro contro bordo</b>".</li>
<li><b>ViT-B/16</b>, ingrandimenti: ogni posizione è simile soprattutto alla propria <b>riga</b> e alla propria <b>colonna</b> (la croce attorno al segno rosso), con bande più deboli e periodiche altrove.</li>
</ul>
<p><b>Domande del notebook</b> (cella 53) e risposte (cella 54), ragionate:</p>
<ol>
<li><b>Come ha imparato righe e colonne, se niente in <code>pos_embed</code> dice "griglia 2D"?</b> Gli embedding sono parametri addestrati. Nelle immagini naturali patch vicine sono correlate, e patch sulla stessa riga o colonna condividono strutture (orizzonte, bordi verticali): sugli 1,3 milioni di immagini di ImageNet è utile che il modello sappia quali posizioni sono allineate, e il gradiente lo scrive negli embedding.</li>
<li><b>Perché la mappa del nostro modello è "quasi rumore"?</b> Dopo 1 epoca lo è davvero (figura nella sezione <a href="#l18-risultati">Risultati</a>): resta solo il punto chiaro della posizione con sé stessa. Dopo 40 epoche, quella salvata, non è rumore ma la struttura centro/bordo: gli oggetti di Imagenette sono quasi sempre centrati, e 9469 immagini sono poche per imparare righe e colonne esatte (domanda scritta per la versione a 1 epoca, scheda 15).</li>
<li><b>Fine-tuning a 384×384 (24×24 patch)?</b> Si rimodellano i 196 embedding in una griglia 14×14, la si interpola (bilineare o bicubica) a 24×24, si riappiattisce e si rimette davanti l'embedding del [CLS]: <b>577</b> posizioni. È ciò che fa l'articolo del ViT per il fine-tuning ad alta risoluzione.</li>
</ol>
<div class="box k"><b>Da saper fare: leggere il pannello di ViT-B/16 (non è aliasing)</b><p>Il pannello grande di ViT-B/16 sembra una trama a righe e colonne regolari invece di 196 mappe separate. Non è un problema di campionamento della figura: i 196 valori per lato sono disegnati su circa 365 pixel, cioè ingranditi, non sottocampionati, e ridisegnandoli a piena risoluzione o con uno spazio bianco fra una mappa e l'altra si ottiene la stessa trama (figura nella sezione <a href="#l18-risultati">Risultati</a>). È il contenuto vero: ogni mappa è a sua volta una trama di righe e colonne, e affiancate senza spazi le righe chiare di mappe vicine si allineano in linee continue. Per leggere le croci servono gli ingrandimenti della seconda figura.</p></div>
<div class="box b"><b>Dal libro · cap. 26, § 26.11 Positional Encodings; Prince § 12.3.1</b><p>Il visionbook usa un codice posizionale <b>fisso</b>: per ogni coordinata x (e separatamente y) un vettore di seni a frequenze decrescenti, [sin x, sin(x/B), …, sin(x/B<sup>P</sup>)], <b>concatenato</b> al token (eq. 26.12); cita i codici appresi del ViT come alternativa. Il codice fisso ha la struttura 2D "per costruzione", quello appreso deve scoprirla, ed è proprio ciò che mostra la figura. Il Prince (§ 12.3.1, fig. 12.5) distingue codifiche assolute (una matrice sommata all'ingresso, fissa o appresa) e relative, e nota che quelle sinusoidali si estendono a sequenze più lunghe, mentre una tabella appresa va interpolata. {V26}</p></div>
<div class="box x"><b>Approfondimento: quali pesi sono</b><p>I pesi <code>IMAGENET1K_V1</code> di torchvision non vengono dal pre-training su JFT dell'articolo originale: secondo la documentazione sono addestrati da zero su ImageNet-1K con una variante della ricetta di DeiT (augmentation e regolarizzazione pesanti), con 81,07% di accuratezza top-1, 86 567 656 parametri e circa 17,6 GFLOP per immagine. Per questo la risposta 1 parla di 1,3 milioni di immagini.</p></div>
""".replace('{V26}', V26), img='img/nb_posizioni.png', printed=NB + 'celle 49–54')

s(22, "Rollout del ViT-B/16: standard e filtrato", """
<pre>tokens = vit._process_input(batch)                                  # (B, 196, 768)
tokens = torch.cat([vit.class_token.expand(B, -1, -1), tokens], dim=1)
tokens = vit.encoder.dropout(tokens + vit.encoder.pos_embedding)
for block in vit.encoder.layers:
    h = block.ln_1(tokens)
    attended, head_weights = block.self_attention(h, h, h, need_weights=True,
                                                  average_attn_weights=False)
    tokens = tokens + block.dropout(attended)
    tokens = tokens + block.mlp(block.ln_2(tokens))
    attn = head_weights.mean(dim=1)                                 # (B, 197, 197)
    ...                                                             # rollout standard come prima
    off_diag = attn.masked_fill(diagonal, float('inf'))
    threshold = torch.quantile(off_diag, discard_ratio, dim=-1, keepdim=True)   # 0.65
    sparse = attn.masked_fill((attn &lt; threshold) &amp; ~diagonal, 0)
    sparse = (sparse + identity) / (sparse + identity).sum(dim=-1, keepdim=True)
    filtered = sparse @ filtered</pre>
<ul>
<li>Il <code>forward</code> di torchvision non restituisce le attenzioni: la funzione <b>riscrive il forward d'inferenza</b> di ogni <code>EncoderBlock</code> (ln_1, attenzione, dropout, residuo, ln_2, MLP, residuo) chiedendo i pesi, senza toccare i parametri. Abbiamo confrontato riga per riga con il codice di torchvision ed è identico: sulle 4 immagini i logit coincidono esattamente con quelli di <code>vit(batch)</code> (differenza massima 0, verificato).</li>
<li>ViT-B/16: 12 blocchi, 12 teste, D = 768, N = 196, 1000 classi (che includono le 10 di Imagenette).</li>
<li><b>Rollout standard</b>: come nella scheda 19, su 12 blocchi.</li>
<li><b>Rollout filtrato</b> (euristica, lo dice il notebook): in ogni riga si azzerano i collegamenti più deboli, il 65% dei valori fuori diagonale, <b>prima</b> di aggiungere l'identità. Restano solo le connessioni forti, e le mappe sono più nette.</li>
</ul>
<p><b>Predizioni</b> (cella 56): motosega → chain saw, lettore → cassette player, chiesa interna → <b>altar</b>, chiesa esterna → church. La terza è giusta nel contenuto (l'immagine è un altare), anche se l'etichetta di Imagenette è church.</p>
<p><b>Figura (uscita della cella 57, colonne 1, 4 e 5):</b> immagine, rollout standard, rollout filtrato, per le 4 immagini. Nel rollout standard il picco cade nello <b>sfondo</b> in tre immagini su quattro: il tronco e il prato per la motosega, l'angolo in basso a sinistra per il lettore, gli alberi scuri per la chiesa esterna. Il filtrato fa emergere l'oggetto nelle due chiese (i pannelli della pala d'altare, la torre), ma i picchi di sfondo restano.</p>
<div class="box x"><b>Approfondimento: il filtro per riga</b><p>Il quantile si calcola su ogni riga dopo aver messo la diagonale a +∞: la diagonale finisce in cima e il quantile 0,65 è calcolato su 197 valori invece che sui 196 fuori diagonale, uno spostamento minimo. La versione più diffusa (il codice <code>vit-explain</code> di Jacob Gildenblat, da cui viene il nome <code>discard_ratio</code>) scarta invece i valori più deboli sull'<b>intera</b> matrice, non riga per riga. Sono due euristiche diverse, nessuna delle due "giusta": il filtraggio cambia la mappa, ed è un motivo in più per non leggere il rollout come una spiegazione.</p></div>
""", img='img/nb_rollout_vitb.png', printed=NB + 'celle 55–56')

s(23, "Attenzione del [CLS] per blocco e token \"register\"", """
<pre>for j, layer_idx in enumerate([5, 11], start=1):
    axes[i, j].imshow(pre_layers[layer_idx][i], cmap='magma')    # blocchi 6 e 12</pre>
<p><b>Figura (uscita della cella 57, colonne 1–3):</b> immagine, attenzione del [CLS] nel blocco 6 e nel blocco 12 di ViT-B/16 (media sulle teste, 14×14).</p>
<ul>
<li><b>Blocco 6</b>: l'attenzione sta in gran parte sull'oggetto (la torre della chiesa, testa e braccia dell'uomo, zone del lettore).</li>
<li><b>Blocco 12</b>: pochi token isolati, quasi tutti nello <b>sfondo</b> (cielo e acqua per la chiesa esterna, i bordi del lettore e della chiesa interna, il prato per la motosega).</li>
<li>Il rollout standard (scheda 22) eredita questi token: per questo i suoi picchi sono nello sfondo, anche se le 4 predizioni sono corrette.</li>
<li>Rispetto al nostro modello, ViT-B/16 è molto più accurato ma le sue mappe sono meno centrate sugli oggetti: <b>più accuratezza non significa attenzione più interpretabile</b>.</li>
</ul>
<div class="box w"><b>Attenzione: "token register" è un'ipotesi, vera solo in parte su queste immagini</b>
<p>La cella 59 afferma che i token isolati del blocco 12 "sono" i token ad alta norma "register-like", cioè patch di sfondo usate per immagazzinare informazione globale. La figura non lo dimostra (mostra l'attenzione, non le norme), e l'abbiamo verificato misurando la norma dei token di ViT-B/16 sulle stesse 4 immagini:</p>
<ul>
<li>token ad alta norma <b>esistono</b>: all'uscita del blocco 12 la norma massima di un token di patch è circa 100 contro una mediana di circa 20 (rapporto massimo/mediana 4,7; 4,3; 2,0; 4,0 nelle quattro immagini);</li>
<li>nelle immagini 1, 2 e 4 (motosega, lettore, chiesa esterna) i token di norma più alta all'ingresso del blocco 12 sono fra i 5 più guardati dal [CLS] nel blocco 12; nella <b>chiesa interna no</b>: il rapporto è solo 2,0 e i picchi d'attenzione cadono su token di norma ordinaria;</li>
<li>su 32 immagini del test i token con norma oltre 3 volte la mediana sono in media 1,7 per immagine e ricevono in media solo l'<b>8%</b> dell'attenzione del [CLS] nel blocco 12.</li>
</ul>
<p>Versione corretta: i picchi del blocco 12 sono <b>compatibili</b> con i token ad alta norma descritti da Darcet et al. (2024) e in 3 immagini su 4 coincidono con essi; non sono però tutti token ad alta norma, e per affermarlo bisogna guardare le norme, non solo l'attenzione.</p></div>
<p><b>Domande del notebook</b> (cella 58), senza risposta nel notebook:</p>
<ul>
<li><b>Perché il rollout finale differisce dall'attenzione del [CLS] nell'ultimo blocco?</b> Quella del blocco 12 dice da quali token <i>di quello strato</i> il [CLS] prende informazione; ma quei token, dopo 11 blocchi, sono già miscele di molte patch. Il rollout risale fino ai token d'ingresso componendo tutti i blocchi e il residuo.</li>
<li><b>Cosa conserva l'identità?</b> Il cammino residuo: ogni token porta avanti anche sé stesso. Senza I il rollout trascurerebbe che metà del segnale passa per il "+ x".</li>
<li><b>Predizione giusta ma mappa sullo sfondo: il rollout basta come prova del ragionamento del classificatore?</b> No. È un'approssimazione (media sulle teste, value e MLP ignorati) e non è causale; inoltre i token di sfondo possono contenere informazione globale sull'oggetto. Servono interventi: occlusione, attribuzioni basate sul gradiente.</li>
<li><b>Confronto con il modello "a una epoca"</b>: in realtà quello sopra è a 40 epoche (scheda 15). Il nostro modello concentra la mappa su pochi dettagli contrastati e di contesto; ViT-B/16 la distribuisce sull'oggetto nei blocchi intermedi e sullo sfondo nell'ultimo.</li>
</ul>
<div class="box x"><b>Approfondimento: Darcet et al. (2024), Vision Transformers Need Registers</b><p>Nei ViT grandi e addestrati a lungo (supervisionati, CLIP, DINOv2) alcune patch di sfondo poco informative vengono "riciclate": la loro norma diventa molto più grande delle altre, contengono informazione globale sull'immagine e poca sulla propria posizione, e producono macchie nelle mappe di attenzione. La cura proposta è aggiungere alla sequenza alcuni token appresi in più, i <b>register</b>, che non corrispondono a nessuna patch e vengono scartati all'uscita: il modello usa quelli come memoria e le mappe tornano pulite. Il [CLS] è già un token di questo tipo (scheda 25).</p></div>
""", img='img/nb_cls_blocchi_vitb.png', printed=NB + 'celle 57–59')

# ---------------------------------------------------------------- domande ed esercizi

s(24, "Domande finali e conteggio dei parametri", """
<p><b>Domande del notebook</b> (cella 60) con le risposte (cella 61), completate:</p>
<ol>
<li><b>Numero di patch</b>: 224×224, P = 16 → N = 196, N + 1 = 197. Con P = 8 → 784 e 785.</li>
<li><b>Scala</b>: senza 1/√d<sub>k</sub> varianza dei punteggi ≈ d<sub>k</sub>, softmax satura, gradienti piccoli (scheda 9). La softmax è <b>per riga</b> perché ogni riga è la distribuzione di <b>una query</b> su tutte le key: i pesi di ogni query devono sommare a 1.</li>
<li><b>Posizioni tutte zero</b>: l'encoder è <b>equivariante</b> alle permutazioni e il [CLS] (che non viene permutato) <b>invariante</b>: rimescolando le patch la predizione non cambia. Dall'ordine dei token l'attenzione non può ricavare la disposizione: per lei la sequenza è un insieme. Verificato: con <code>pos_embed</code> a zero, permutando le 196 patch i logit cambiano al massimo di 8·10<sup>−7</sup> (errore di arrotondamento).</li>
<li><b>Costo</b>: dimezzare P moltiplica N per 4; la matrice di attenzione ha (N + 1)² elementi, quindi memoria e calcolo di QKᵀ e AV crescono di circa <b>16</b> volte, gli strati lineari solo di 4.</li>
<li><b>Rollout</b>: in ogni blocco un token arriva all'uscita per due vie, attenzione e residuo; l'identità modella il residuo, e le matrici di tutti i blocchi si moltiplicano per risalire dall'uscita alle patch d'ingresso.</li>
<li><b>Parametri</b>: la risposta è nel codice della cella 62 (tabella sotto).</li>
</ol>
<table>
<tr><th></th><th>nostro ViT</th><th>quota</th><th>ViT-B/16</th><th>quota</th></tr>
<tr><td>patch embedding</td><td>73 824</td><td>23,2%</td><td>590 592</td><td>0,7%</td></tr>
<tr><td>[CLS] + posizioni</td><td>19 008</td><td>6,0%</td><td>152 064</td><td>0,2%</td></tr>
<tr><td>attenzione</td><td>74 496</td><td>23,5%</td><td>28 348 416</td><td>32,7%</td></tr>
<tr><td>MLP</td><td>148 416</td><td>46,7%</td><td>56 669 184</td><td>65,5%</td></tr>
<tr><td>LayerNorm</td><td>960</td><td>0,3%</td><td>38 400</td><td>0,0%</td></tr>
<tr><td>testa</td><td>970</td><td>0,3%</td><td>769 000</td><td>0,9%</td></tr>
<tr><td><b>totale</b></td><td><b>317 674</b></td><td></td><td><b>86 567 656</b></td><td></td></tr>
</table>
<ul>
<li>In entrambi l'<b>MLP</b> ha la quota maggiore. Ma nel nostro modello il patch embedding pesa quasi un quarto, in ViT-B/16 meno dell'1%: il patch embedding cresce come 768·D, i blocchi come 12D² ciascuno, moltiplicati per la profondità. Con D piccolo e 2 soli blocchi la proiezione d'ingresso conta molto; con D = 768 e 12 blocchi diventa trascurabile.</li>
<li>La funzione <code>param_groups</code> assegna ogni parametro a un gruppo dal nome (<code>attn</code>/<code>self_attention</code>, <code>mlp</code>, <code>norm</code>/<code>.ln</code>…) e controlla con due <code>assert</code> che i totali tornino.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Rifare la colonna di ViT-B/16 a mano (D = 768, 12 blocchi, 1000 classi): patch 768·768 + 768 = 590 592; posizioni 197·768 + 768 = 152 064; attenzione 12·(4D² + 4D) = 28 348 416; MLP 12·(8D² + 5D) = 56 669 184; LayerNorm 25·2D = 38 400; testa 768·1000 + 1000 = 769 000. E il costo di un blocco del nostro modello in moltiplicazioni-somme: parte lineare 12·T·D² ≈ 21,8 M, attenzione 2·T²·D ≈ 7,5 M con T = 197.</p></div>
<div class="box b"><b>Dal libro · cap. 26, § 26.8 Permutation Equivariance</b><p>Il libro dimostra la risposta 3: gli strati applicati token per token (MLP, normalizzazione), l'attenzione e le connessioni residue sono tutti equivarianti alle permutazioni, e una composizione di funzioni equivarianti è equivariante (eq. 26.8, fig. 26.15). Quindi un transformer senza codici posizionali tratta i token come un insieme non ordinato; il § 26.9.5 aggiunge che, avendo solo "filtri" 1×1, la rete non ha modo di conoscere la disposizione spaziale se non dagli ingressi. {V26}</p></div>
""".replace('{V26}', V26), sec=("l18-eser", "Domande, esperimenti, esercizi", 'schede 24–28'), printed=NB + 'celle 60–62')

s(25, "Esperimenti facoltativi", """
<p>Regola del notebook: <b>cambiare una cosa alla volta e scrivere la previsione prima di eseguire</b>. Le risposte della cella 64, ragionate:</p>
<p><b>1. PATCH_SIZE = 8</b></p>
<table>
<tr><th></th><th>P = 16</th><th>P = 8</th></tr>
<tr><td>griglia</td><td>14×14</td><td>28×28</td></tr>
<tr><td>patch N / token N + 1</td><td>196 / 197</td><td>784 / 785</td></tr>
<tr><td>valori per patch P²C</td><td>768</td><td>192</td></tr>
<tr><td>tensore di attenzione (B, h, T, T)</td><td>(32, 4, 197, 197)</td><td>(32, 4, 785, 785)</td></tr>
<tr><td>parametri del patch embedding</td><td>73 824</td><td>18 528</td></tr>
<tr><td>parametri delle posizioni</td><td>18 912</td><td>75 360</td></tr>
</table>
<ul>
<li>Il tensore di attenzione cresce di 785²/197² ≈ 15,9 volte: in float32 passa da circa 20 MB a 315 MB <b>per blocco</b>, e il training li conserva tutti per il backward. Se la memoria non basta si riduce <code>BATCH_SIZE</code>.</li>
<li>I parametri restano quasi gli stessi (≈ 319 000): il patch embedding si restringe, le posizioni crescono.</li>
<li>Calcolo per immagine (nostro conto): circa 73 milioni di moltiplicazioni-somme con P = 16, circa 425 milioni con P = 8, quasi 6 volte di più. Con P = 8 la parte di attenzione di un blocco (118 M) supera quella lineare (87 M): succede quando T &gt; 6D, qui 785 &gt; 576.</li>
<li>Le mappe di rollout diventano più fini (28×28); patch piccole di solito aiutano l'accuratezza dopo un training lungo.</li>
</ul>
<p><b>2. Niente embedding posizionali</b> (azzerati e congelati): il modello vede l'immagine come un "sacco di patch"; rimescolando le patch i logit non cambiano (risposta 3 della scheda 24). Il calo di accuratezza c'è, ma su Imagenette è spesso più piccolo di quanto ci si aspetti: molte classi si riconoscono da texture e colori locali.</p>
<p><b>3. Mean pooling</b> invece di [CLS]:</p>
<pre>def forward(self, images):
    return self.head(self.forward_features(images)[:, 1:].mean(dim=1))</pre>
<p>Il [CLS] non serve più e si può togliere; le due scelte arrivano ad accuratezze simili. Se lo si tiene senza collegarlo alla testa, fa da <b>register</b>: un token in più dove le patch scrivono e leggono informazione globale (Darcet et al. 2024). Il rollout va cambiato: non si legge più la riga del [CLS] ma la <b>media delle righe</b> dei token di patch, perché l'uscita è la loro media.</p>
<p><b>4. CIFAR-10</b>: a 32×32 con P = 16 si hanno 2×2 = <b>4 patch</b>, 5 token: ogni patch è un quarto dell'immagine e l'attenzione ha quasi nulla da mettere in relazione. Meglio P = 4 (8×8 = 64 patch, 65 token) o P = 2 (256 patch). Da cambiare: <code>IMG_SIZE = 32</code>, statistiche di CIFAR, <code>RandomCrop(32, padding=4)</code> e flip, <code>class_names = train_set.classes</code>, una validazione presa dal training, niente sezione su ViT-B/16 (vuole immagini 224×224). Confronto atteso con la ResNet della <a href="#L16">L16</a>: con pochi dati e nessun pre-training la CNN, che ha la località "per costruzione", parte avvantaggiata (L17, slide 39).</p>
<div class="box x"><b>Approfondimento: Beyer et al. (2022), Better plain ViT baselines for ImageNet-1k</b><p>Un ViT "semplice" addestrato solo su ImageNet-1K può essere un buon modello con pochi accorgimenti: classificazione con la <b>media dei token</b> invece del [CLS], embedding posizionali <b>fissi</b> sinusoidali 2D invece che appresi, batch più piccolo, augmentation moderata (RandAugment, Mixup). Con queste modifiche un ViT-S/16 supera il 76% di top-1 in 90 epoche. Per il notebook il messaggio è che [CLS] e posizioni apprese non sono obbligatori: mean pooling e codici fissi (come nel visionbook) funzionano altrettanto bene.</p></div>
""", printed=NB + 'celle 63–64')

s(26, "Esercizio A: attenzione con maschera", """
<span class="f">Attention(Q, K, V) = softmax( QKᵀ/√d<sub>k</sub> + M ) V,   M<sub>ij</sub> = 0 (permesso) oppure −∞ (vietato)</span>
<pre>def masked_attention(q, k, v, mask=None):
    scores = q @ k.transpose(-2, -1) / math.sqrt(q.shape[-1])
    if mask is not None:
        scores = scores.masked_fill(~mask, float("-inf"))   # mask booleana: True = permesso
    weights = scores.softmax(dim=-1)
    return weights @ v, weights

causal = torch.tril(torch.ones(T, T, dtype=torch.bool))     # il token i vede solo 0..i</pre>
<ul>
<li>La maschera booleana usa la stessa convenzione di <code>F.scaled_dot_product_attention</code>: <code>True</code> = la key partecipa. <code>masked_fill(~mask, -inf)</code> realizza la M additiva.</li>
<li>Test (cella 69): senza maschera coincide con l'attenzione normale; con una maschera casuale (diagonale sempre permessa) coincide con PyTorch, i pesi vietati sono <b>esattamente</b> 0 e le righe sommano a 1; con la maschera causale coincide con <code>is_causal=True</code>. Uscita: PASS.</li>
</ul>
<p><b>Follow-up</b> (risposte della cella 67):</p>
<ul>
<li><b>Prima o dopo la softmax?</b> Prima: e<sup>−∞</sup> = 0, quindi le key vietate ricevono peso zero e la softmax <b>rinormalizza</b> sulle permesse. Azzerare dopo la softmax lascerebbe righe che non sommano più a 1.</li>
<li><b>Serve una maschera al ViT per classificare?</b> No: l'immagine è disponibile tutta insieme, ogni patch può guardare ogni altra, e tutte le immagini hanno lo stesso numero di token (197). Serve per la generazione autoregressiva di immagini o video, per il video in streaming (il futuro non è ancora arrivato) e per batch di immagini a risoluzioni diverse (padding da ignorare).</li>
<li><b>Perché la maschera causale nel training di un modello autoregressivo</b>: in training tutti i fotogrammi di un video sono disponibili e si predicono in parallelo in un solo forward. Senza maschera i token che devono predire il fotogramma 3 potrebbero guardare il fotogramma 3 e copiarlo: loss quasi zero, e un modello inutile in generazione, quando il futuro non esiste. La maschera rende il training uguale alla generazione.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 26, § 26.10 Masked Attention</b><p>Il libro introduce la maschera causale per i modelli che generano una sequenza un elemento alla volta: l'uscita in posizione i deve dipendere solo dagli ingressi fino a i, e lo si ottiene mettendo a zero i pesi dell'attenzione verso le posizioni successive (fig. 26.17–26.19), così che tutte le predizioni si possano addestrare in parallelo. {V26}</p></div>
""".replace('{V26}', V26), printed=NB + 'celle 65–69')

s(27, "Esercizio B: proiezione fusa e teste", """
<p>T = N + 1 = 197, B = 2, D = 96, h = 4, d<sub>k</sub> = 24. La tabella da riempire prima di eseguire:</p>
<table>
<tr><th>passo</th><th>operazione</th><th>forma</th></tr>
<tr><td>1</td><td>ingresso X</td><td>(2, 197, 96)</td></tr>
<tr><td>2</td><td>proiezione fusa XW<sup>QKV</sup></td><td>(2, 197, 288)</td></tr>
<tr><td>3</td><td>Q, K, V con le teste separate</td><td>(2, 4, 197, 24) ciascuno</td></tr>
<tr><td>4</td><td>punteggi e pesi A</td><td>(2, 4, 197, 197)</td></tr>
<tr><td>5</td><td>uscita per testa AV</td><td>(2, 4, 197, 24)</td></tr>
<tr><td>6</td><td>concatenazione delle teste</td><td>(2, 197, 96)</td></tr>
<tr><td>7</td><td>proiezione d'uscita ·W<sup>O</sup></td><td>(2, 197, 96)</td></tr>
</table>
<pre>q, k, v = qkv.reshape(B, T, 3, h, d_k).permute(2, 0, 3, 1, 4)
scores = q @ k.transpose(-2, -1) / math.sqrt(d_k)
attn = scores.softmax(dim=-1)
values = attn @ v
merged = values.transpose(1, 2).reshape(B, T, D)
out = out_proj(merged)</pre>
<p>La cella 73 copia i pesi di un <code>nn.MultiheadAttention</code> in due <code>nn.Linear</code> e controlla forme (tutte OK) e risultato: "PASS: matches nn.MultiheadAttention".</p>
<p><b>Domande</b> (risposte della cella 71, ragionate):</p>
<ol>
<li><b>Perché 3D? Il 3 dipende da h?</b> Query, key e value larghi D ciascuno; il 3 non dipende da h, i parametri sono 3D² per ogni h.</li>
<li><b>Su quale asse la softmax?</b> Quello delle key (<code>dim=-1</code>): la riga i di A è una distribuzione sui 197 token e dà il peso di ciascun value nell'uscita del token i.</li>
<li><b>Si dividono i token o le dimensioni?</b> Le dimensioni: ogni testa vede tutti i 197 token, ristretti a 24 coordinate.</li>
<li><b>Perché <code>transpose(1, 2)</code> prima di <code>reshape</code>?</b> <code>values</code> è (B, h, T, d<sub>k</sub>) e in memoria contiene prima tutti i token della testa 0, poi quelli della testa 1… Un <code>reshape(B, T, D)</code> diretto taglierebbe questa sequenza in righe da 96 numeri: ogni riga conterrebbe 4 token consecutivi di una stessa testa. <b>Il codice non si blocca</b>: il numero di elementi è lo stesso (2·4·197·24 = 2·197·96), quindi il reshape riesce e l'errore è silenzioso; se ne accorge solo un test come quello della cella 73. Con <code>transpose(1, 2)</code> si passa a (B, T, h, d<sub>k</sub>) e ogni riga contiene le h uscite di un solo token.</li>
<li><b>Perché W<sup>O</sup>?</b> Dopo la concatenazione ogni blocco di 24 coordinate viene ancora da una sola testa; W<sup>O</sup> le mescola e riporta il risultato nello spazio del flusso residuo. Con W<sup>QKV</sup> fa 4D² pesi per blocco.</li>
</ol>
<div class="box k"><b>Da saper fare: <code>.T</code> su tensori a più dimensioni</b>
<pre>values.shape                  # (2, 4, 197, 24)
values.T.shape                # (24, 197, 4, 2)   inverte TUTTI gli assi
values.transpose(1, 2).shape  # (2, 197, 4, 24)   scambia solo teste e token
k.transpose(-2, -1).shape     # (2, 4, 24, 197)   giusto per QKᵀ (oppure k.mT)</pre>
<p>Su una matrice <code>.T</code> scambia i due assi, su un tensore a 4 dimensioni li inverte tutti, portando batch e teste in fondo. PyTorch 2.14 stampa un avviso: questo uso è deprecato e in futuro darà errore. Regola: nominare sempre gli assi da scambiare.</p></div>
""", printed=NB + 'celle 70–73')

s(28, "Esercizio C: softmax numericamente stabile", """
<span class="f">softmax(x)<sub>i</sub> = e<sup>x<sub>i</sub></sup> / ∑<sub>j</sub> e<sup>x<sub>j</sub></sup> = e<sup>x<sub>i</sub>−c</sup> / ∑<sub>j</sub> e<sup>x<sub>j</sub>−c</sup></span>
<pre>def softmax_stable(x, dim=-1):
    x_max = x.amax(dim=dim, keepdim=True)    # c = massimo della riga
    e = torch.exp(x - x_max)                 # esponenti tutti &lt;= 0: niente overflow
    return e / e.sum(dim=dim, keepdim=True)  # denominatore &gt;= 1

big = torch.tensor([1000., 1001., 1002.])
# naive : tensor([nan, nan, nan])
# stable: tensor([0.0900, 0.2447, 0.6652])</pre>
<ul>
<li>In float32 e<sup>x</sup> va a <code>inf</code> per x ≳ 88 (e<sup>88,7</sup> ≈ 3,4·10<sup>38</sup>, il massimo float32), e inf/inf = nan: è ciò che succede alla versione ingenua con 1000, 1001, 1002.</li>
<li>Sottrarre la stessa costante a tutti gli elementi non cambia la softmax (si semplifica e<sup>−c</sup>). Con <b>c = max</b> nessun esponente è positivo. Il risultato coincide con softmax(0, 1, 2) = (0,0900; 0,2447; 0,6652).</li>
<li>I test confrontano con <code>torch.softmax</code> anche su punteggi di forma (2, 4, 197, 197) moltiplicati per 50 e su un asse diverso (<code>dim=1</code>), e controllano una riga mascherata in parte.</li>
</ul>
<p><b>Follow-up</b> (risposte della cella 75):</p>
<ol>
<li><b>Denominatore ≥ 1</b>: per l'indice del massimo e<sup>0</sup> = 1 e gli altri termini sono ≥ 0. Non può essere zero nemmeno se tutti gli altri termini vanno in underflow, e nessun termine può andare in overflow.</li>
<li><b>Righe mascherate</b>: in parte mascherata, e<sup>−∞</sup> = 0 e le altre sommano a 1. Del tutto mascherata, c = −∞ e −∞ − (−∞) non è definito: l'uscita è <code>nan</code> (anche <code>torch.softmax</code> fa così, verificato). Una query senza key permesse non ha una distribuzione valida e il nan si propaga ad AV e ai gradienti: per questo l'esercizio A chiede almeno una key permessa per riga.</li>
<li><b>log_softmax</b>: log softmax(x)<sub>i</sub> = x<sub>i</sub> − c − log ∑<sub>j</sub> e<sup>x<sub>j</sub>−c</sup> (il trucco <b>log-sum-exp</b>). <code>torch.log(softmax(x))</code> è una cattiva idea: per un logit molto negativo la probabilità va a 0 in float32 e log 0 = −∞, quindi loss infinita e gradienti nan (con logit 0 e −200: log softmax ingenuo dà −∞, <code>log_softmax</code> dà −200). Per questo <code>nn.CrossEntropyLoss</code> prende i <b>logit</b> e applica <code>log_softmax</code> al suo interno.</li>
</ol>
<div class="box w"><b>Attenzione: refuso nel commento della cella 76</b><p>Il commento dell'ultima riga di <code>softmax_stable</code> finisce con un "er?" rimasto per errore: <code># denominator &gt;= 1 (the max term is e^0 = 1)er?</code>. È solo un commento e il codice è corretto. Versione corretta: <code># denominator &gt;= 1 (the max term is e^0 = 1)</code>.</p></div>
""", printed=NB + 'celle 74–76')
