NB = 'NOTEBOOK cnn_image_classification.ipynb · '

# ---------------------------------------------------------------- dataset, augmentation, dataloader

s(1, "CNNs for Image Classification: obiettivi e setup", """
<p>Il notebook mette in pratica la teoria della <a href="#L15">L15</a>: si addestra una <b>rete convoluzionale residua</b> (ResNet-18) a classificare le immagini di <b>CIFAR-10</b> e poi si guarda dentro la rete, alle <b>feature map</b>.</p>
<p>Cosa fa, in ordine:</p>
<ul>
<li>carica CIFAR-10 con <code>torchvision</code>, con <b>augmentation</b> (crop casuale e flip) e <b>normalizzazione</b>;</li>
<li>prepara i <b>batch</b> con un <code>DataLoader</code>;</li>
<li>definisce una <b>ResNet-18</b> adattata a immagini 32×32 (blocchi residui, shortcut, BatchNorm);</li>
<li>la addestra con <b>SGD</b> e cross-entropy, poi misura l'<b>accuratezza</b> sul test;</li>
<li>estrae le attivazioni interne con un <b>forward hook</b> e le visualizza con la <b>PCA</b> a 3 componenti, come nella fig. 24.25 del libro.</li>
</ul>
<pre>torch.cuda.is_available()   # True se c'è una GPU usabile
torch.tensor([1]).cuda()    # prova a spostare un tensore sulla GPU
import torch, torchvision
import matplotlib.pyplot as plt</pre>
<ul>
<li>La cella iniziale serve a controllare di avere una versione di PyTorch <b>con supporto CUDA</b>: la build "CPU only" installa senza errori ma <code>is_available()</code> restituisce False.</li>
<li>Senza GPU il notebook suggerisce <b>Google Colab</b>. Il motivo si vede nelle uscite salvate: sulla CPU del docente un'epoca dura <b>36 minuti</b> (scheda 16), dieci epoche circa sei ore.</li>
</ul>
""", sec=("l16-dati", "Dataset, augmentation e DataLoader", 'schede 1–6'), printed=NB + 'celle 1–3')

s(2, "CIFAR-10 con torchvision", """
<p><b>CIFAR-10</b> (Krizhevsky, 2009): 60 000 immagini a colori <b>32×32</b>, 10 classi bilanciate, <b>50 000 di training</b> e <b>10 000 di test</b>. Le classi, con il loro indice: 0 airplane, 1 automobile, 2 bird, 3 cat, 4 deer, 5 dog, 6 frog, 7 horse, 8 ship, 9 truck. CIFAR-100 ha le stesse dimensioni ma 100 classi (600 immagini per classe).</p>
<pre>train_data = CIFAR10(root=data_dir, train=True,  transform=train_transform, download=True)
test_data  = CIFAR10(root=data_dir, train=False, transform=eval_transform,  download=True)</pre>
<ul>
<li><code>download=True</code> scarica l'archivio (170 MB) solo la prima volta in <code>./data</code>.</li>
<li>I dati grezzi stanno in <code>train_data.data</code>: un array numpy <b>50000×32×32×3 uint8</b> (altezza, larghezza, canali, valori 0–255); le etichette in <code>train_data.targets</code>.</li>
<li>La <b>transform</b> non viene applicata una volta per tutte: <code>train_data[i]</code> la esegue <b>a ogni accesso</b>. Con l'augmentation casuale, due letture della stessa immagine danno tensori diversi (verificato), mentre l'etichetta resta la stessa.</li>
<li>Due pipeline separate: <code>train_transform</code> con augmentation per il training, <code>eval_transform</code> solo con la normalizzazione per il test. Il test va valutato sulle immagini vere, non su versioni perturbate.</li>
<li>Il <code>VisibleDeprecationWarning</code> nell'uscita salvata viene da numpy 2.4 dentro il codice di torchvision che legge l'archivio: innocuo.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Dire cosa restituisce <code>train_data[i]</code>: la coppia (tensore 3×32×32 float già trasformato, etichetta intera fra 0 e 9). Per esempio <code>train_data[0]</code> ha etichetta 6, cioè frog.</p></div>
""", printed=NB + 'celle 4–5')

s(3, "Data augmentation: crop casuale con padding e flip", """
<pre>train_transform = transforms.Compose([
    transforms.RandomCrop(32, padding=4),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(...),
])</pre>
<ul>
<li><b>RandomCrop(32, padding=4)</b>: aggiunge 4 pixel di zeri su ogni lato (40×40) e ritaglia una finestra 32×32 in posizione casuale. Il risultato è una <b>traslazione casuale</b> fino a ±4 pixel in ogni direzione, con una banda nera sul lato da cui l'immagine è "uscita" (si vede nella figura della scheda 5).</li>
<li><b>RandomHorizontalFlip()</b>: specchia l'immagine sinistra-destra con probabilità 0.5.</li>
<li>Le trasformazioni sono estratte <b>di nuovo a ogni epoca</b>: la rete non vede mai due volte esattamente la stessa immagine. Il dataset su disco non cambia, si allarga la distribuzione da cui si campiona.</li>
<li>È una forma di <b>regolarizzazione</b> (<a href="#L15">L15</a>): rende più difficile memorizzare le singole immagini e insegna alla rete che una piccola traslazione o uno specchio non cambiano la classe.</li>
<li>Una CNN è già equivariante alla traslazione negli strati conv, ma con stride, padding ai bordi e aliasing (<a href="#L6">L6</a>, <a href="#L15">L15</a>) il classificatore finale non è esattamente invariante: l'augmentation colma la differenza.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 36, § 36.2 Data Augmentation</b>
<p>Il libro formalizza l'augmentation così: per ogni coppia (x<sub>i</sub>, y<sub>i</sub>) si aggiungono coppie sintetiche (T(x<sub>i</sub>; θ<sub>j</sub>), y<sub>i</sub>), con T una trasformazione e θ<sub>j</sub> parametri casuali (per il crop, la posizione della finestra).</p>
<ul>
<li>L'etichetta <b>non</b> viene trasformata: si sta assumendo che il compito sia <b>invariante</b> alla trasformazione, y(T(x; θ)) = y(x).</li>
<li>Se l'invarianza non vale, l'augmentation fa danni: lo specchio va bene per le scene e gli oggetti, non per il riconoscimento dei caratteri (b e d si scambiano).</li>
<li>Quando l'uscita ha struttura spaziale (segmentazione) la stessa trasformazione va applicata anche all'etichetta: serve <b>equivarianza</b>, non invarianza (torna in <a href="#L17">L17</a>).</li>
<li>Perché funziona: <b>allarga la distribuzione di training</b> e riduce la distanza dal test. La fig. 36.2 lo mostra nelle prime due componenti PCA di feature CLIP: flip, crop e color jitter fanno "coprire" via via i punti di test (CIFAR-100) partendo da Caltech256.</li>
</ul>
<p>Il Prince (§ 9.3.8 Augmentation) dice la stessa cosa in una riga: insegnare al modello a essere indifferente a trasformazioni irrilevanti per l'etichetta.</p>
<p><a href="https://visionbook.mit.edu/data_augmentation.html">visionbook.mit.edu · cap. 36</a></p></div>
""", printed=NB + 'cella 5')

s(4, "ToTensor e Normalize", """
<pre>transforms.ToTensor(),
transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))</pre>
<ul>
<li><b>ToTensor</b>: da immagine H×W×C uint8 in [0, 255] a tensore <b>C×H×W float in [0, 1]</b>. L'ordine dei canali prima delle posizioni è la convenzione di PyTorch (N×C×H×W per un batch, come nel libro § 12.6.1).</li>
<li><b>Normalize(μ, σ)</b>: per ogni canale c calcola (x<sub>c</sub> − μ<sub>c</sub>) / σ<sub>c</sub>. Ingressi centrati e di scala simile rendono l'ottimizzazione meglio condizionata.</li>
<li>Le stesse μ e σ (calcolate sul <b>training</b>) vanno usate anche sul test: infatti <code>eval_transform</code> ripete la stessa Normalize.</li>
<li>Dopo la normalizzazione i valori non stanno più in [0, 1]: la prima immagine va da −2.43 a 2.56 (uscita del notebook, scheda 5).</li>
</ul>
<div class="box w"><b>Attenzione: le σ non sono le deviazioni standard di CIFAR-10</b>
<p>Le medie sono giuste: sul training set misuriamo μ = (0.4914, 0.4822, 0.4465). Le deviazioni standard per canale del training set sono invece</p>
<span class="f">σ = (0.2470, 0.2435, 0.2616)</span>
<p>I valori del notebook (0.2023, 0.1994, 0.2010) sono un'altra cosa: la <b>media delle deviazioni standard calcolate immagine per immagine</b> (misurata: 0.2022, 0.1993, 0.2009). Ignora la variabilità <b>fra</b> immagini (una foto chiara e una scura), quindi è più piccola. Sono numeri che circolano in molti repository per CIFAR.</p>
<p>Effetto: dopo la Normalize gli ingressi hanno deviazione standard ≈ 1.22, 1.22, 1.30 invece di 1. In pratica non cambia quasi nulla (la prima conv è seguita da una BatchNorm che riscala), ma non è una standardizzazione. Versione corretta: <code>Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616))</code>.</p></div>
<div class="box k"><b>Da saper fare</b><p>Calcolare media e deviazione standard per canale: <code>d = train_data.data / 255; d.mean(axis=(0, 1, 2)); d.std(axis=(0, 1, 2))</code>, cioè su tutte le immagini e tutte le posizioni insieme, un numero per canale.</p></div>
""", printed=NB + 'cella 5')

s(5, "Guardare un'immagine: transpose contro permute", """
<pre>x, y = train_data[0]
x.shape, y                    # (torch.Size([3, 32, 32]), 6)
plt.imshow(train_data[0][0].transpose(0,2).numpy())   # cella 7
plt.imshow(train_data.data[200])                       # cella 8</pre>
<ul>
<li>Il tensore è <b>3×32×32</b> (C×H×W), l'etichetta 6 è <b>frog</b>. matplotlib invece vuole <b>H×W×C</b>.</li>
<li>La cella 8 legge <code>train_data.data[200]</code>: i dati <b>grezzi</b>, uint8, già H×W×C, senza transform. Per questo si vede bene (un'altra rana, etichetta 6).</li>
</ul>
<div class="box w"><b>Attenzione: transpose(0,2) ribalta l'immagine sulla diagonale, e la normalizzazione falsa i colori</b>
<p><code>transpose(0,2)</code> scambia solo gli assi 0 e 2: da (C, H, W) si ottiene <b>(W, H, C)</b>. La forma è giusta per imshow, ma righe e colonne sono scambiate: l'immagine è <b>trasposta</b> (specchiata lungo la diagonale). Verificato: <code>x.transpose(0,2)</code> coincide con <code>x.permute(1,2,0).transpose(0,1)</code>. In più il tensore è normalizzato, con valori in [−2.43, 2.56]: matplotlib taglia a [0, 1] (l'avviso "Clipping input data") e i colori diventano saturi.</p>
<p>Versione corretta: riordinare gli assi con <code>permute(1, 2, 0)</code> e annullare la normalizzazione, x·σ + μ:</p>
<pre>mean = torch.tensor((0.4914, 0.4822, 0.4465))[:, None, None]
std  = torch.tensor((0.2023, 0.1994, 0.2010))[:, None, None]
plt.imshow((x * std + mean).clamp(0, 1).permute(1, 2, 0))</pre>
<p>La cella 20 usa invece <code>.numpy().transpose(1,2,0)</code>: lì l'ordine degli assi è giusto (in numpy <code>transpose</code> con tre indici è una permutazione), ma i colori restano falsati per la stessa normalizzazione.</p></div>
<p><b>Figura (nostra esecuzione):</b> la stessa rana di <code>train_data[0]</code> con il codice del notebook (trasposta, colori saturi), con <code>permute</code> (orientata bene, colori ancora saturi) e con <code>permute</code> più denormalizzazione. La banda nera in basso e a destra è il crop casuale con padding della scheda 3; ogni chiamata a <code>train_data[0]</code> ne estrae uno diverso.</p>
""", img='img/nb_imshow_confronto.png', printed=NB + 'celle 6–8')

s(6, "DataLoader: batch e shuffle", """
<pre>dataloader = DataLoader(train_data, batch_size=100, shuffle=True)
for i, (x, y) in enumerate(dataloader):
    ...   # x.shape: [100, 3, 32, 32],  y: tensor di 100 interi
    break</pre>
<ul>
<li>Il <b>DataLoader</b> pesca gli indici, chiama <code>train_data[i]</code> (quindi applica la transform) e <b>impila</b> i risultati in un batch <b>N×C×H×W</b>.</li>
<li><code>y</code> contiene gli <b>indici di classe</b> (int64), non vettori one-hot: è il formato che vuole <code>CrossEntropyLoss</code>.</li>
<li><code>shuffle=True</code>: a ogni nuova iterazione sul DataLoader l'ordine è una nuova permutazione casuale. Ogni immagine compare <b>una volta per epoca</b> (campionamento senza reinserimento). Per il test lo shuffle non serve.</li>
<li><code>num_workers</code> &gt; 0 prepara i batch in processi paralleli: con la GPU evita che la rete aspetti il caricamento e l'augmentation fatti dalla CPU.</li>
<li>Il <code>break</code> fa vedere solo il primo batch.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Numero di batch per epoca = ⌈N / B⌉. Con B = 32: training ⌈50000/32⌉ = <b>1563</b> batch (1562 pieni e l'ultimo di 50000 − 1562·32 = <b>16</b> immagini); test ⌈10000/32⌉ = <b>313</b> batch, l'ultimo ancora di 16. I numeri 1563 e 313 compaiono nelle barre di avanzamento del notebook, e il 16 nella scheda 18.</p></div>
<div class="box b"><b>Dal libro · Prince, § 6.2.1 Batches and epochs</b>
<p>Lo SGD calcola il gradiente su un sottoinsieme casuale (minibatch) dei dati; i batch si estraggono di solito <b>senza reinserimento</b>, finché i dati sono finiti: un passaggio completo è un'<b>epoca</b>. Batch grande = stima del gradiente più precisa ma più cara; batch di tutto il dataset = discesa del gradiente classica. Lo stesso compromesso è nel visionbook, § 10.7.</p></div>
""", printed=NB + 'celle 9–10')

# ---------------------------------------------------------------- modello

s(7, "Una ResNet-18 per immagini 32×32", """
<p>Il notebook copia il codice della ResNet da <code>weiaicunzai/pytorch-cifar100</code>, un repository che addestra molte architetture su CIFAR-100.</p>
<ul>
<li>La ResNet-18 originale (He et al. 2016) è pensata per ImageNet, <b>224×224</b>: il primo strato è una conv <b>7×7 con stride 2</b> seguita da un <b>max pooling con stride 2</b>, quindi riduce subito la risoluzione di 4 volte (224 → 56) e alla fine arriva a 7×7.</li>
<li>Su un'immagine 32×32 la stessa rete passerebbe a 8×8 dopo il primo blocco e a <b>1×1</b> all'ultimo stadio: quasi tutta l'informazione spaziale persa subito (verificato con la ResNet-18 di torchvision).</li>
<li>La versione per CIFAR cambia solo l'ingresso: <b>conv 3×3 con stride 1, senza max pooling</b>, e primo stadio con stride 1. Risoluzioni: 32 → 32 → 16 → 8 → 4.</li>
<li>Larghezze (64, 128, 256, 512 canali) e numero di blocchi (2, 2, 2, 2) sono quelli della ResNet-18 standard.</li>
</ul>
<div class="box w"><b>Attenzione: non è una versione "slim" né "con meno unità"</b>
<p>La cella 11 parla di "slim ResNet18" e gli esercizi dicono che la nostra rete è "slightly different from theirs (slim version, less units)". Confrontando il codice con <code>models/resnet.py</code> del repository: <code>BasicBlock</code>, <code>BottleNeck</code> e <code>ResNet</code> sono <b>identici</b>; l'unica differenza è che il notebook passa <code>num_classes</code> alla funzione <code>resnet18()</code>. Con 100 classi la rete del notebook ha <b>11 220 132</b> parametri, gli stessi "11.2M" indicati nel README del repository per la loro resnet18.</p>
<p>Non è nemmeno più piccola della ResNet-18 per ImageNet: con 10 classi ha 11 173 962 parametri contro 11 181 642 di quella di torchvision, e la differenza è solo la conv d'ingresso (3×3×3×64 = 1 728 pesi invece di 7×7×3×64 = 9 408). Anzi costa di più: lavorando a 32×32 fin dal primo stadio fa circa <b>555 milioni</b> di moltiplicazioni-somme per immagine, contro circa 37 milioni della versione ImageNet applicata a 32×32 (misurato).</p></div>
""", sec=("l16-modello", "Il modello: ResNet-18 per CIFAR", 'schede 7–13'), printed=NB + 'celle 11–12')

s(8, "BasicBlock: il blocco residuo", """
<pre>self.residual_function = nn.Sequential(
    nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False),
    nn.BatchNorm2d(out_channels),
    nn.ReLU(inplace=True),
    nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, bias=False),
    nn.BatchNorm2d(out_channels))
...
def forward(self, x):
    return nn.ReLU(inplace=True)(self.residual_function(x) + self.shortcut(x))</pre>
<ul>
<li>Il ramo residuo F è <b>conv 3×3 → BN → ReLU → conv 3×3 → BN</b>; l'uscita è <b>ReLU(F(x) + shortcut(x))</b>.</li>
<li><code>padding=1</code> con kernel 3×3 conserva la dimensione; con <code>stride=2</code> la prima conv la dimezza (32 → 16).</li>
<li><code>bias=False</code>: un bias prima di una BatchNorm è inutile, perché la BN sottrae la media e poi aggiunge il proprio parametro β, che fa da bias.</li>
<li><code>expansion = 1</code>: il blocco esce con <code>out_channels</code> canali (nel BottleNeck sono 4 volte tanti). È un attributo di classe usato da <code>ResNet</code> per sapere quanti canali arrivano al blocco successivo.</li>
<li><code>nn.ReLU(inplace=True)(...)</code> crea un modulo a ogni forward: funziona perché la ReLU non ha parametri, ma è più pulito <code>torch.relu(...)</code> o un modulo definito nell'<code>__init__</code>.</li>
<li>È l'ordine "post-attivazione" del primo articolo di He et al. (2016): la ReLU finale sta <b>dopo</b> la somma.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 24, § 24.11.3 ResNets</b>
<p>Il libro scrive il blocco residuo come x<sub>out</sub> = F(x<sub>in</sub>) + x<sub>in</sub>: F è un <b>residuo</b> che perturba l'ingresso per migliorarlo. Se le dimensioni non coincidono si aggiunge una mappa lineare, x<sub>out</sub> = F(x<sub>in</sub>) + W x<sub>in</sub>: è esattamente lo shortcut con conv 1×1 della scheda 9.</p>
<ul>
<li>Il punto chiave: per un blocco residuo è <b>facile fare l'identità</b>, basta F = 0. Impilando molti blocchi la rete può "spegnere" quelli che non servono, cioè scegliersi la profondità.</li>
<li>Il gradiente ha sempre un cammino diretto: ∂x<sub>out</sub>/∂x<sub>in</sub> = ∂F/∂x<sub>in</sub> + I (<a href="#L15">L15</a>, slide ResNet).</li>
</ul>
<p>Il Prince (§ 11.2) aggiunge la lettura "srotolata": una rete residua è una somma di cammini di lunghezza diversa. Nel § 11.5.1 descrive il blocco nell'ordine <b>BN → ReLU → conv</b> (pre-attivazione, la variante successiva di He et al.); il notebook usa l'ordine originale <b>conv → BN → ReLU</b>, con la ReLU dopo la somma. Il § 11.2.1 spiega perché l'ordine conta: se F finisse con una ReLU sarebbe sempre ≥ 0 e ogni blocco potrebbe solo aumentare i valori. Qui F finisce con una BN, che è lineare, quindi può anche diminuirli; la ReLU dopo la somma rende però non negativa l'uscita di ogni blocco.</p>
<p><a href="https://visionbook.mit.edu/convolutional_neural_nets.html">visionbook.mit.edu · cap. 24</a></p></div>
""", printed=NB + 'cella 12')

s(9, "Shortcut: identità o proiezione 1×1", """
<pre>self.shortcut = nn.Sequential()          # identità
if stride != 1 or in_channels != BasicBlock.expansion * out_channels:
    self.shortcut = nn.Sequential(
        nn.Conv2d(in_channels, out_channels * BasicBlock.expansion, kernel_size=1, stride=stride, bias=False),
        nn.BatchNorm2d(out_channels * BasicBlock.expansion))</pre>
<ul>
<li>Un <code>nn.Sequential()</code> vuoto restituisce l'ingresso così com'è: è lo shortcut <b>identità</b>.</li>
<li>Se il blocco cambia risoluzione (stride 2) o numero di canali, F(x) e x non si possono sommare: si usa una <b>conv 1×1 con lo stesso stride</b>, più BN, che porta x alla forma giusta (la W x<sub>in</sub> del libro).</li>
<li>Nella ResNet-18 per CIFAR succede <b>tre volte</b>: nel primo blocco di <code>conv3_x</code>, <code>conv4_x</code>, <code>conv5_x</code> (si vedono nella stampa del modello). Gli altri 5 blocchi hanno lo shortcut identità.</li>
<li>Una conv 1×1 con stride 2 prende un pixel su quattro senza filtrare prima: è un sottocampionamento senza passa-basso (<a href="#L6">L6</a>, stride e aliasing in <a href="#L15">L15</a>).</li>
<li>Conteggio: 17 conv nel cammino principale (1 iniziale + 8 blocchi × 2) più l'fc fanno i <b>18 strati</b> del nome; le 3 conv 1×1 degli shortcut non si contano. In tutto la rete ha 20 <code>Conv2d</code> e 20 <code>BatchNorm2d</code>.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Primo blocco di <code>conv3_x</code>, ingresso 64×32×32. Ramo residuo: conv 3×3 stride 2 → 128×16×16, conv 3×3 → 128×16×16. Shortcut: conv 1×1 stride 2, 64 → 128 canali → 128×16×16. La somma è possibile. Parametri dello shortcut: 1·1·64·128 = 8 192 pesi più 2·128 della BN.</p></div>
""", printed=NB + 'cella 12')

s(10, "BatchNorm2d: cosa fa in training e in valutazione", """
<p>Ogni conv del modello è seguita da una <code>BatchNorm2d</code>. Nella stampa compare come <code>BatchNorm2d(64, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)</code>.</p>
<ul>
<li>Per ogni <b>canale</b> c calcola media μ<sub>c</sub> e varianza σ<sub>c</sub><sup>2</sup> su <b>tutto il batch e tutte le posizioni</b> (N·H·W valori), poi</li>
</ul>
<span class="f">y = γ<sub>c</sub> · (x − μ<sub>c</sub>) / √(σ<sub>c</sub><sup>2</sup> + ε) + β<sub>c</sub></span>
<ul>
<li>γ<sub>c</sub> e β<sub>c</sub> sono <b>appresi</b>, uno per canale (<code>affine=True</code>); ε = 10<sup>−5</sup> evita la divisione per zero.</li>
<li><b>In training</b> (<code>model.train()</code>) usa le statistiche del batch corrente e aggiorna le medie mobili: running = 0.9·running + 0.1·batch. Il <code>momentum=0.1</code> della stampa è questo tasso di aggiornamento, <b>non</b> il momentum dell'ottimizzatore.</li>
<li><b>In valutazione</b> (<code>model.eval()</code>) usa le medie mobili, fisse: la predizione di un'immagine non dipende più dalle altre del batch. Per questo il notebook insiste su <code>model.train()</code> e <code>model.eval()</code>.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 12, § 12.7.3 Normalization Layers; Prince, § 11.4</b>
<p>Il visionbook definisce la batchnorm come standardizzazione di ogni attivazione rispetto a media e varianza sul batch, con due parametri appresi che restituiscono espressività; in training le statistiche cambiano da batch a batch, a test si usano statistiche aggregate del training. Fa notare che usare le statistiche del batch di test può servire ad adattarsi a un cambio di distribuzione.</p>
<p>Il Prince (§ 11.4) precisa che nelle reti convoluzionali le statistiche si calcolano su batch <b>e</b> posizioni spaziali, con un γ e un δ per canale, e (§ 11.4.1) ne elenca i benefici: propagazione stabile della varianza nelle reti residue, <b>learning rate più alti</b> (superficie della loss più liscia) e un effetto di <b>regolarizzazione</b> (il rumore delle statistiche di batch).</p>
<p><a href="https://visionbook.mit.edu/neural_nets.html">visionbook.mit.edu · cap. 12</a></p></div>
""", printed=NB + 'celle 12–13')

s(11, "BottleNeck: il blocco delle ResNet profonde", """
<pre>nn.Conv2d(in_channels, out_channels, kernel_size=1, bias=False),               # riduce i canali
nn.BatchNorm2d(out_channels), nn.ReLU(inplace=True),
nn.Conv2d(out_channels, out_channels, stride=stride, kernel_size=3, padding=1, bias=False),
nn.BatchNorm2d(out_channels), nn.ReLU(inplace=True),
nn.Conv2d(out_channels, out_channels * BottleNeck.expansion, kernel_size=1, bias=False),  # riespande ×4
nn.BatchNorm2d(out_channels * BottleNeck.expansion)</pre>
<ul>
<li>Tre conv: <b>1×1</b> che riduce i canali, <b>3×3</b> che lavora nello spazio (con l'eventuale stride), <b>1×1</b> che riespande di <code>expansion = 4</code>.</li>
<li>Serve per le ResNet da 50 strati in su (ResNet-50/101/152): la 3×3, che è la parte cara, lavora su pochi canali.</li>
<li>Nel notebook è <b>definito ma non usato</b>: <code>resnet18</code> usa solo <code>BasicBlock</code>. Per provarlo: <code>ResNet(BottleNeck, [3, 4, 6, 3], num_classes=100)</code> è la ResNet-50, 23.7 milioni di parametri (misurato, come nel README del repository).</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Confronto dei pesi a 256 canali in ingresso e in uscita. Due conv 3×3 256→256: 2·9·256·256 = 1 179 648. Bottleneck 256→64→64→256: 256·64 + 9·64·64 + 64·256 = 16 384 + 36 864 + 16 384 = 69 632, circa 17 volte meno.</p></div>
<div class="box b"><b>Dal libro · Prince, § 11.5.1 ResNet</b><p>Per reti molto profonde il numero di parametri diventerebbe eccessivo: il blocco bottleneck usa una 1×1 per ridurre i canali, una 3×3 normale e un'altra 1×1 per tornare al numero originale, e così integra l'informazione su un'area 3×3 con meno parametri. Il visionbook non tratta il bottleneck.</p></div>
""", printed=NB + 'cella 12')

s(12, "ResNet e _make_layer: come si monta la rete", """
<pre>self.conv1 = nn.Sequential(nn.Conv2d(3, 64, kernel_size=3, padding=1, bias=False),
                           nn.BatchNorm2d(64), nn.ReLU(inplace=True))
self.conv2_x = self._make_layer(block, 64,  num_block[0], 1)
self.conv3_x = self._make_layer(block, 128, num_block[1], 2)
self.conv4_x = self._make_layer(block, 256, num_block[2], 2)
self.conv5_x = self._make_layer(block, 512, num_block[3], 2)
self.avg_pool = nn.AdaptiveAvgPool2d((1, 1))
self.fc = nn.Linear(512 * block.expansion, num_classes)

def _make_layer(self, block, out_channels, num_blocks, stride):
    strides = [stride] + [1] * (num_blocks - 1)
    for stride in strides:
        layers.append(block(self.in_channels, out_channels, stride))
        self.in_channels = out_channels * block.expansion</pre>
<ul>
<li><b>Stem</b> <code>conv1</code>: conv 3×3 da 3 a 64 canali, BN, ReLU.</li>
<li><b>Quattro stadi</b> <code>conv2_x</code>…<code>conv5_x</code>, ciascuno di <code>num_block[i]</code> blocchi. Solo il <b>primo blocco</b> di ogni stadio ha lo stride dello stadio (1 per il primo, 2 per gli altri): <code>strides = [2, 1]</code> per la ResNet-18.</li>
<li><code>self.in_channels</code> è uno <b>stato</b> che si aggiorna mentre si costruisce: ogni blocco riceve i canali prodotti dal precedente. Per questo gli stadi vanno costruiti in ordine.</li>
<li>Schema classico: <b>ogni volta che la risoluzione si dimezza, i canali raddoppiano</b> (64, 128, 256, 512), come in VGG.</li>
<li><b>Testa</b>: <code>AdaptiveAvgPool2d((1, 1))</code> è il <b>global average pooling</b> (512×4×4 → 512), <code>view</code> appiattisce, <code>fc</code> dà i <b>logit</b>. Non c'è softmax: è dentro <code>CrossEntropyLoss</code>.</li>
<li><code>resnet18 = ResNet(BasicBlock, [2, 2, 2, 2])</code>; nel repository ci sono anche resnet34 [3, 4, 6, 3] con BasicBlock e resnet50/101/152 con BottleNeck.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 24, § 24.4 A Simple CNN Classifier e § 24.3.2 Global Pooling</b>
<p>Il classificatore minimo del libro è conv → relu → gap → fc → softmax, addestrato con cross-entropy: la ResNet ha la stessa testa, solo con un corpo molto più profondo. Il global pooling trasforma una mappa C×H×W in un vettore di C numeri, uno per canale, qualunque sia H×W: per questo <code>AdaptiveAvgPool2d</code> funziona anche con immagini più grandi di 32×32. Il libro (§ 24.6) nota anche che logit e immagine si possono vedere come feature map: l'ingresso ha 3 canali RGB, l'uscita è una mappa 1×1 con un canale per classe.</p>
<p><a href="https://visionbook.mit.edu/convolutional_neural_nets.html">visionbook.mit.edu · cap. 24</a></p></div>
""", printed=NB + 'cella 12')

s(13, "Stampa del modello: forme, parametri, campo recettivo", """
<pre>model = resnet18(num_classes=10)
print(model)</pre>
<p>La stampa elenca i moduli annidati (non le forme). Forme e conteggi misurati su un ingresso 3×32×32:</p>
<table>
<tr><th>Stadio</th><th>Uscita</th><th>Parametri</th><th>Campo recettivo</th></tr>
<tr><td>ingresso</td><td>3×32×32</td><td>–</td><td>1</td></tr>
<tr><td>conv1</td><td>64×32×32</td><td>1 856</td><td>3</td></tr>
<tr><td>conv2_x</td><td>64×32×32</td><td>147 968</td><td>11</td></tr>
<tr><td>conv3_x</td><td>128×16×16</td><td>525 568</td><td>25</td></tr>
<tr><td>conv4_x</td><td>256×8×8</td><td>2 099 712</td><td>53</td></tr>
<tr><td>conv5_x</td><td>512×4×4</td><td>8 393 728</td><td>109</td></tr>
<tr><td>avg_pool</td><td>512×1×1</td><td>0</td><td>tutta l'immagine</td></tr>
<tr><td>fc</td><td>10</td><td>5 130</td><td></td></tr>
<tr><td><b>totale</b></td><td></td><td><b>11 173 962</b></td><td></td></tr>
</table>
<ul>
<li><b>Tre quarti dei parametri</b> sono nell'ultimo stadio (8.4 milioni): una conv 3×3 512→512 ha da sola 9·512·512 = 2 359 296 pesi. Il calcolo invece è distribuito su tutti gli stadi, perché i primi lavorano su molte più posizioni.</li>
<li>I campi recettivi sono quelli teorici, verificati misurando quali pixel d'ingresso hanno gradiente non nullo rispetto al pixel centrale di ogni stadio. Già a <code>conv4_x</code> (53) ogni posizione "vede" più dell'intera immagine 32×32; il global pooling poi copre comunque tutto.</li>
<li><code>momentum=0.1</code> nelle righe <code>BatchNorm2d</code> è il tasso delle medie mobili della BN (scheda 10).</li>
</ul>
<div class="box k"><b>Da saper fare</b>
<p><b>Forme</b>: con kernel k, padding p, stride s, l'uscita è ⌊(H + 2p − k)/s⌋ + 1. Conv 3×3, p = 1, s = 2 su 32: ⌊31/2⌋ + 1 = 16.</p>
<p><b>Parametri</b> di una conv: k·k·C<sub>in</sub>·C<sub>out</sub> (+ C<sub>out</sub> se c'è il bias); una BN ne ha 2C. Esempio, stem: 3·3·3·64 + 2·64 = 1 856.</p>
<p><b>Campo recettivo</b>: r ← r + (k − 1)·j, dove j è il prodotto degli stride precedenti, e dopo uno strato con stride s, j ← j·s. Stem: 3. conv2_x, quattro 3×3 con j = 1: 3 + 8 = 11. conv3_x: la prima conv ha ancora j = 1 (+2 → 13), poi j = 2 e tre conv aggiungono 4 ciascuna: 25. conv4_x: 25 + 4 + 3·8 = 53. conv5_x: 53 + 8 + 3·16 = 109.</p></div>
<div class="box b"><b>Dal libro · cap. 24, § 24.7 Receptive Fields</b><p>Il campo recettivo cresce con la profondità perché comporre filtri dà un filtro di supporto più grande (§ 15.4.1); le non linearità puntuali non lo cambiano; ogni sottocampionamento di un fattore s rende s volte più rapida la crescita successiva. Il libro chiede che l'ultimo strato veda tutta l'immagine, e osserva che un global pooling lo garantisce sempre. Nessuna formula chiusa: quella sopra è il conto standard.</p></div>
""", printed=NB + 'cella 13')

# ---------------------------------------------------------------- training e valutazione

s(14, "Preparare il training: modello, ottimizzatore, loss", """
<pre>device = 'cpu'  # set device='cuda' if you have a GPU
model = resnet18(num_classes=100)
model = model.to(device)
optimizer = torch.optim.SGD(model.parameters(), lr=0.04)
criterion = torch.nn.CrossEntropyLoss()
model.train()</pre>
<ul>
<li><code>.to(device)</code> sposta i parametri sulla GPU; nel ciclo anche <code>x</code> e <code>y</code> vanno spostati, perché tutti i tensori di un'operazione devono stare sullo stesso dispositivo.</li>
<li><b>SGD</b> con learning rate 0.04 e i valori di default di PyTorch: <b>momentum 0, weight decay 0</b> (verificato stampando l'ottimizzatore). È la discesa del gradiente "pura" sul minibatch.</li>
<li><b>CrossEntropyLoss</b> = log-softmax + negative log-likelihood, mediata sul batch: riceve i <b>logit</b> e gli indici di classe.</li>
<li><code>model.train()</code> mette BatchNorm (e un eventuale dropout) in modalità training.</li>
</ul>
<div class="box w"><b>Attenzione: num_classes=100 su un problema a 10 classi</b>
<p>La cella 13 crea il modello con <code>num_classes=10</code>, ma quello addestrato ha <code>num_classes=100</code>: l'fc produce 100 logit. Non dà errore perché <code>CrossEntropyLoss</code> richiede solo che le etichette siano minori del numero di classi (0–9 &lt; 100). Però:</p>
<ul>
<li>90 uscite non corrispondono a nessuna classe: il training deve imparare a spingerle in basso. Nella nostra esecuzione, dopo 300 iterazioni, il logit medio è 6.8 per le classi 0–9 e −0.8 per le 10–99, e nessuna predizione cade fra 10 e 99;</li>
<li>la loss iniziale è circa ln 100 ≈ 4.6 invece di ln 10 ≈ 2.3 (primo batch misurato: 4.35);</li>
<li>46 170 parametri in più (11 220 132 contro 11 173 962).</li>
</ul>
<p>Versione corretta: <code>model = resnet18(num_classes=10)</code>. Il valore 100 è un residuo del repository di partenza, che è per CIFAR-100.</p></div>
""", sec=("l16-training", "Training e valutazione", 'schede 14–17'), printed=NB + 'celle 14–15')

s(15, "Il ciclo di training: zero_grad, forward, backward, step", """
<pre>for ep in range(10):
    dataloader = DataLoader(train_data, batch_size=32, shuffle=True, num_workers=0)
    pbar = tqdm(dataloader)
    for x, y in pbar:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()      # azzera i gradienti
        pred = model(x)            # forward
        loss = criterion(pred, y)
        loss.backward()            # backward: riempie p.grad per ogni parametro
        optimizer.step()           # θ ← θ − η·grad
        pbar.set_description(f"Loss: {loss.item():0.4f}")</pre>
<ul>
<li><b>zero_grad</b>: in PyTorch <code>backward()</code> <b>somma</b> nei campi <code>.grad</code>; senza azzerarli, il gradiente di ogni batch si accumulerebbe su quelli precedenti.</li>
<li><b>forward</b>: calcola i logit e la loss, e intanto PyTorch registra il grafo delle operazioni.</li>
<li><b>backward</b>: percorre il grafo all'indietro (backpropagation) e calcola ∂L/∂θ per ogni parametro.</li>
<li><b>step</b>: aggiorna i parametri; con SGD semplice θ ← θ − η∇<sub>θ</sub>L.</li>
<li>Il <code>DataLoader</code> ricreato a ogni epoca è corretto (basterebbe crearlo una volta: anche così ogni epoca avrebbe una nuova permutazione).</li>
<li>Dieci epoche con B = 32 sono 15 630 aggiornamenti. Il commento "10 epoch is a bit on the low end" è giusto: le ricette per CIFAR usano 100–200 epoche (scheda 24).</li>
</ul>
<div class="box b"><b>Dal libro · cap. 14, § 14.4–14.5; cap. 10, § 10.7</b>
<ul>
<li>§ 14.4: l'algoritmo è "<b>prima forward, poi backward</b>". Il forward calcola e conserva le attivazioni di ogni strato; il backward parte dalla loss e propaga all'indietro il gradiente rispetto alle attivazioni, ottenendo lungo la strada il gradiente rispetto ai parametri di ogni strato. Il backward ha bisogno delle attivazioni del forward: è per questo che PyTorch conserva il grafo.</li>
<li>§ 14.5: il gradiente della loss media su un batch è la <b>media dei gradienti</b> dei singoli esempi (il gradiente di una somma è la somma dei gradienti). <code>CrossEntropyLoss</code> media sul batch, quindi la dimensione del passo non dipende da B.</li>
<li>§ 10.7: lo SGD usa la media su un batch casuale come <b>stima</b> del gradiente vero; batch piccolo = stima rumorosa ma economica. Il rumore aiuta a superare piccole irregolarità della loss e ha un effetto di regolarizzazione implicita.</li>
</ul>
<p>Il Prince (eq. 6.10) scrive l'aggiornamento con la <b>somma</b> sul batch invece della media: cambia solo la scala del learning rate.</p>
<p><a href="https://visionbook.mit.edu/backpropagation.html">visionbook.mit.edu · cap. 14</a> · <a href="https://visionbook.mit.edu/gradient_descent.html">cap. 10</a></p></div>
""", printed=NB + 'cella 15')

s(16, "Cosa raccontano le uscite salvate del training", """
<pre>Loss: 1.1877: 100%|██████████| 1563/1563 [36:23&lt;00:00,  1.40s/it]
Loss: 1.1878:  17%|█▋        | 261/1563 [10:03&lt;50:08,  2.31s/it]
KeyboardInterrupt</pre>
<ul>
<li>Il docente ha eseguito su <b>CPU</b>: la prima epoca (1563 batch) ha richiesto <b>36 minuti e 23 secondi</b>, 1.40 s per batch. Dieci epoche avrebbero richiesto circa sei ore.</li>
<li>Nella seconda epoca il training è stato <b>interrotto a mano</b> (KeyboardInterrupt) dopo 261 batch. Il modello in memoria conserva i pesi raggiunti: la valutazione successiva usa una rete addestrata per circa <b>1824 aggiornamenti</b>, poco più di un'epoca.</li>
<li>Il numero nella barra è la loss <b>dell'ultimo batch</b>, non la media dell'epoca: alla fine dell'epoca è un batch di sole 16 immagini. È un valore molto rumoroso; per seguire il training conviene una media mobile, e salvare i valori per disegnare la curva.</li>
<li>Non c'è un insieme di <b>validazione</b>: per scegliere iperparametri (learning rate, epoche) bisognerebbe tenere da parte una parte del training, non guardare il test.</li>
</ul>
<div class="box x"><b>Approfondimento: la nostra esecuzione ridotta</b><p>Stesso codice, 300 batch invece di 10 epoche, CPU a 2 thread: 170 s (0.57 s per batch). Loss del primo batch 4.35 (vicino a ln 100, scheda 14), media dei primi 50 batch 2.74, degli ultimi 50 1.72; gli ultimi cinque valori singoli oscillano fra 1.24 e 2.05, a conferma che il valore della barra da solo dice poco. Accuratezza di test dopo 300 batch: 0.41 (il docente, dopo circa 1824 batch: 0.6323). Dettagli nella sezione <a href="#l16-risultati">Risultati</a>.</p></div>
""", printed=NB + 'cella 15, uscite')

s(17, "Valutazione: accuratezza sul test", """
<pre>with torch.no_grad():
    model = model.eval()
    dataloader = DataLoader(test_data, batch_size=32, num_workers=0)
    correct, tot = 0, 0
    for x, y in pbar:
        pred = model(x)
        _, pred = torch.max(pred.data, 1)
        correct += (pred == y).sum().item()
        tot += x.shape[0]</pre>
<ul>
<li><code>torch.no_grad()</code>: non registra il grafo, quindi niente memoria per le attivazioni e calcolo più veloce. In valutazione non si fa backward.</li>
<li><code>model.eval()</code>: la BatchNorm usa le medie mobili (scheda 10). Restituisce il modello stesso, quindi <code>model = model.eval()</code> è innocuo. La rete <b>resta</b> in modalità eval anche dopo: le feature map delle schede seguenti sono calcolate così, ed è giusto.</li>
<li><code>torch.max(pred, 1)</code> restituisce (valori massimi, indici): l'indice è la classe predetta. <code>.data</code> è un'interfaccia vecchia (stacca il tensore dal grafo), inutile dentro <code>no_grad</code>: oggi si scrive <code>pred.argmax(1)</code>.</li>
<li>Accuratezza = corrette / totali; <code>tot</code> conta le immagini, non i batch, quindi l'ultimo batch da 16 è pesato bene.</li>
</ul>
<p><b>Risultato salvato: ACC 0.6323</b> sulle 10 000 immagini di test (313 batch, 2 minuti e 29 secondi). Il caso casuale darebbe 0.10. Con un training completo le ResNet su CIFAR-10 superano il 90% (He et al. 2016 riportano errori di test fra il 6% e l'8% con le loro ResNet per CIFAR): 0.63 riflette poco più di un'epoca di training, senza momentum né schedule.</p>
<div class="box k"><b>Da saper fare</b><p>Spiegare perché dimenticare <code>model.eval()</code> è un errore: la BN normalizzerebbe con le statistiche del batch di test, quindi la predizione di un'immagine dipenderebbe dalle altre del batch (e dalla sua dimensione), e in più le medie mobili verrebbero aggiornate con i dati di test.</p></div>
""", printed=NB + 'celle 16–17')

# ---------------------------------------------------------------- feature map

s(18, "L'ultimo batch del test", """
<pre>x.shape                # torch.Size([16, 3, 32, 32])
plt.imshow(x[0].detach().cpu().numpy().transpose(1,2,0))</pre>
<ul>
<li>Dopo il ciclo di valutazione <code>x</code> è rimasto l'<b>ultimo batch</b> del test: 10 000 = 312·32 + 16, quindi <b>16 immagini</b>. Le sezioni sulle feature map usano queste.</li>
<li>Il test non è mescolato, quindi sono sempre le stesse 16 immagini (le ultime del test set): horse, dog, ship, airplane, ship, bird, horse, airplane, cat, dog, cat, ship, cat, dog, automobile, horse. La prima è un cavallo con cavaliere.</li>
<li>L'ordine degli assi è giusto (in numpy <code>transpose(1,2,0)</code> è una permutazione), ma l'immagine è normalizzata: matplotlib taglia a [0, 1] (avviso "Clipping input data", range [−2.00, 2.36]) e i colori del notebook sono falsati, come nella scheda 5.</li>
<li><code>.detach().cpu()</code> serve se il tensore richiede gradiente o sta sulla GPU; qui è già su CPU e senza gradiente, ma è l'idioma sicuro.</li>
</ul>
<p><b>Figura (nostra esecuzione):</b> le 16 immagini denormalizzate, con l'etichetta vera.</p>
""", img='img/nb_ultimo_batch.png', sec=("l16-feature", "Feature map: hook e PCA", 'schede 18–23'), printed=NB + 'celle 18–20')

s(19, "visualize_pca: da C canali a un'immagine RGB", """
<pre>def visualize_pca(feature_map):
    x = feature_map.detach().float().cpu().squeeze()   # (C, H, W)
    C, H, W = x.shape
    x = x.reshape(C, -1).T.numpy()                      # (H*W, C)
    x = PCA(n_components=3).fit_transform(x)            # (H*W, 3)
    x = (x - x.min(axis=0)) / (np.ptp(x, axis=0) + 1e-8)   # ogni componente in [0, 1]
    rgb = x.reshape(H, W, 3)</pre>
<ul>
<li>Ogni <b>posizione</b> (i, j) della feature map è un vettore di C numeri, il suo <b>descrittore</b>. Le H·W posizioni sono i campioni della PCA.</li>
<li>La PCA trova le 3 direzioni dello spazio a C dimensioni lungo cui i descrittori variano di più; proiettando ogni posizione su di esse si ottengono 3 numeri, usati come <b>R, G, B</b>.</li>
<li>Ogni componente viene riscalata in [0, 1] (min-max, <code>np.ptp</code> = max − min). Il <code>1e-8</code> evita di dividere per zero se una componente è costante.</li>
<li><b>Come leggerla</b>: posizioni di colore simile hanno descrittori simili, cioè la rete le "vede" in modo simile. Il colore in sé non ha significato.</li>
<li>La PCA è calcolata <b>per ogni immagine</b>: le direzioni (e il loro segno, arbitrario) cambiano da un'immagine all'altra, quindi i colori non sono confrontabili fra immagini diverse.</li>
</ul>
<p>Nella nostra esecuzione le 3 componenti spiegano in media il 69% della varianza a <code>conv1</code> e il 54–61% negli stadi successivi: l'immagine RGB è un riassunto parziale.</p>
<div class="box b"><b>Dal libro · cap. 24, § 24.6 Feature Maps in CNNs</b><p>Il libro chiama feature map sia un canale sia l'intera pila di canali di uno strato: feature disposte in una mappa con la forma dell'ingresso. Oltre a mostrare i canali come immagini in scala di grigi (fig. 24.24, AlexNet), propone proprio questa tecnica: PCA dei canali a 3 dimensioni e resa a colori, prima componente in rosso, seconda in verde, terza in blu. La fig. 24.25 la applica a 5 strati di AlexNet, VGG16 e <b>ResNet18</b>, la stessa rete del notebook.</p>
<p><a href="https://visionbook.mit.edu/convolutional_neural_nets.html">visionbook.mit.edu · cap. 24</a></p></div>
""", printed=NB + 'cella 21')

s(20, "Forward hook: leggere le attivazioni interne", """
<pre>activations = []
def hook(model, input, output):
    activations.append(output.detach())

h = model.conv4_x.register_forward_hook(hook)
model(x)
h.remove()
activations[0].shape     # torch.Size([16, 256, 8, 8])</pre>
<ul>
<li>Un <b>forward hook</b> è una funzione che PyTorch chiama <b>dopo</b> il forward del modulo a cui è agganciato, con (modulo, ingresso, uscita). Permette di leggere un'attivazione intermedia senza modificare il codice del modello.</li>
<li><code>output.detach()</code> la stacca dal grafo; <code>h.remove()</code> toglie l'hook, altrimenti scatterebbe a ogni forward successivo e la lista crescerebbe.</li>
<li>Il primo argomento si chiama <code>model</code> ma è il <b>modulo</b> agganciato (qui <code>conv4_x</code>): il nome può confondere.</li>
<li>L'uscita di <code>conv4_x</code> è quella del suo ultimo blocco, <b>dopo la ReLU</b>: valori ≥ 0, e circa il 38% esattamente zero (nostra esecuzione).</li>
<li>Forma <b>16×256×8×8</b>: 16 immagini, 256 canali, risoluzione 32/4 = 8. Le altre forme sono nella tabella della scheda 13.</li>
<li><code>model(x)</code> fuori da <code>torch.no_grad()</code> costruisce il grafo per niente: meglio <code>with torch.no_grad(): model(x)</code>.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Agganciare l'hook a un altro stadio e prevedere la forma prima di eseguire: <code>conv1</code> e <code>conv2_x</code> 64×32×32, <code>conv3_x</code> 128×16×16, <code>conv5_x</code> 512×4×4, <code>avg_pool</code> 512×1×1.</p></div>
""", printed=NB + 'celle 22–23')

s(21, "Mappe PCA di conv4_x", """
<pre>for iii in range(16):
    visualize_pca(activations[0][iii])</pre>
<p><b>Figura (uscita salvata del notebook):</b> 16 mappe 8×8 a blocchi colorati, una per immagine del batch, nello stesso ordine della scheda 18 (prima riga: horse, dog, ship, airplane, ship, bird, horse, airplane).</p>
<ul>
<li>Ogni cella della griglia 8×8 corrisponde a un blocco 4×4 dell'immagine, ma con campo recettivo teorico 53: <b>ogni posizione vede quasi tutta l'immagine</b>. Non ci si deve aspettare contorni precisi.</li>
<li>Le mappe sono a <b>grandi regioni</b>: in diverse immagini il centro (dove sta l'oggetto) ha un colore diverso dal bordo, e nelle immagini di navi e aerei compaiono <b>fasce orizzontali</b>, compatibili con il fondo di cielo e mare. La rete raggruppa le posizioni per "cosa c'è", più che per colore o bordi.</li>
<li>È la rete del docente dopo poco più di un'epoca: con un training completo le regioni dell'oggetto diventano in genere più nette.</li>
</ul>
<div class="box x"><b>Approfondimento: lettura prudente</b><p>Una PCA a 3 componenti di 256 canali tiene circa metà della varianza e i colori dipendono dall'immagine: queste figure sono un indizio qualitativo, non una prova che la rete "segmenta" l'oggetto. Per un confronto stadio per stadio sulla stessa immagine vedi la figura nella sezione <a href="#l16-risultati">Risultati</a>.</p></div>
""", img='img/nb_pca_conv4.png', printed=NB + 'cella 24')

s(22, "I canali uno per uno: la griglia 8×8", """
<pre>hx = activations[0][0]        # prima immagine: 256×8×8
for iii in range(64):
    plt.subplot(8, 8, iii + 1)
    plt.imshow(hx[iii])</pre>
<p><b>Figura (uscite salvate del notebook):</b> a sinistra i primi 64 canali di <code>conv4_x</code> per il cavallo con cavaliere (mappe 8×8), a destra i primi 64 di <code>conv1</code> per la stessa immagine (mappe 32×32, cella 27).</p>
<ul>
<li><code>conv4_x</code>: mappe a pochi pixel accesi, molte quasi tutte scure (effetto della ReLU: attivazioni <b>sparse</b>). Ogni canale risponde in poche posizioni.</li>
<li><code>conv1</code>: ogni canale è riconoscibile come una versione filtrata dell'immagine, con <b>contorni</b> accesi in direzioni diverse e alcune <b>regioni di colore</b>: sono rilevatori di bordi e colori, come le derivate orientate della <a href="#L5">L5</a>, ma appresi.</li>
<li>Si mostrano solo <b>64 canali su 256</b> per <code>conv4_x</code> (tutti per <code>conv1</code>, che ne ha 64).</li>
<li><code>imshow</code> riscala i colori <b>per ogni riquadro</b> (dal minimo al massimo di quel canale): un canale quasi spento e uno molto attivo possono sembrare ugualmente "accesi". Per confrontare canali servono <code>vmin</code> e <code>vmax</code> comuni.</li>
</ul>
""", img='img/nb_griglie_canali.png', printed=NB + 'celle 25 e 27')

s(23, "conv1: le feature del primo stadio", """
<pre>h = model.conv1.register_forward_hook(hook)
model(x); h.remove()
for iii in range(16):
    visualize_pca(activations[0][iii])     # activations[0]: 16×64×32×32</pre>
<p><b>Figura (uscita salvata del notebook):</b> le 16 mappe PCA di <code>conv1</code>, 32×32. Si riconoscono subito le immagini: il cavallo con cavaliere, la nave, l'aereo, il cane. Gli oggetti sono a colori falsi, con <b>frange colorate lungo i contorni</b>.</p>
<ul>
<li>Lo stem ha campo recettivo <b>3×3</b>: ogni posizione descrive solo un intorno minuscolo (colore locale, presenza e direzione di un bordo). La PCA quindi separa soprattutto <b>colore</b> e <b>bordi</b>, e l'immagine resta quasi una foto.</li>
<li>Confronto con <code>conv4_x</code> (scheda 21): risoluzione 32 → 8, canali 64 → 256, campo recettivo 3 → 53. Le mappe passano da "come appare localmente" a "che parte della scena è".</li>
<li>La cella 26 ridefinisce <code>activations</code> e <code>hook</code> copiando la cella 22: se si dimentica <code>activations = []</code>, <code>activations[0]</code> resta quella vecchia.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 24, § 24.6</b><p>Il libro descrive esattamente questo andamento su AlexNet (fig. 24.24): scendendo nella rete la risoluzione cala e i canali crescono; nei primi strati le mappe rispondono a strutture semplici (bordi, linee), più in profondità diventano più astratte e legate alla semantica, fino a canali che sono quasi una mappa di "dove sta l'uccello". La fig. 24.25 mostra le PCA di 5 strati di ResNet18: stesso passaggio da immagine a falsi colori a regioni grossolane.</p></div>
""", img='img/nb_pca_conv1.png', printed=NB + 'celle 26–27')

# ---------------------------------------------------------------- esercizi

s(24, "Esercizi del notebook", """
<ul>
<li><b>resnet</b>: rileggere il codice della ResNet e verificare le forme delle feature map e come stride, padding e kernel le determinano. Tabella e formule nella scheda 13.</li>
<li><b>augmentations matter</b>: addestrare con e senza augmentation (basta togliere <code>RandomCrop</code> e <code>RandomHorizontalFlip</code> da <code>train_transform</code>) e confrontare accuratezza di training e di test.</li>
<li><b>training stability and lr</b>: aumentare il learning rate di 10× e 100× e guardare la curva della loss; provare uno scheduler.</li>
<li><b>reproduce sota for CIFAR100</b>: riprodurre un risultato del repository <code>weiaicunzai/pytorch-cifar100</code>.</li>
</ul>
<p>Per l'ultimo esercizio la rete è già quella giusta (scheda 7: il codice è identico). Manca la <b>ricetta di training</b>, che nel repository (file <code>train.py</code> e <code>conf/global_settings.py</code>) è:</p>
<ul>
<li>CIFAR-100 con le sue medie e deviazioni standard, augmentation con in più <code>RandomRotation(15)</code>;</li>
<li><b>200 epoche</b>, batch 128;</li>
<li><code>SGD(lr=0.1, momentum=0.9, weight_decay=5e-4)</code>;</li>
<li><code>MultiStepLR(milestones=[60, 120, 160], gamma=0.2)</code>: il learning rate è diviso per 5 alle epoche 60, 120 e 160;</li>
<li>un'epoca di <b>warm-up</b> con learning rate che cresce da zero.</li>
</ul>
<p>Risultato dichiarato per la resnet18: errore top-1 <b>24.39%</b>, top-5 6.95%.</p>
<pre>optimizer = torch.optim.SGD(model.parameters(), lr=0.1, momentum=0.9, weight_decay=5e-4)
scheduler = torch.optim.lr_scheduler.MultiStepLR(optimizer, milestones=[60, 120, 160], gamma=0.2)
for ep in range(200):
    for x, y in dataloader:
        ...                      # zero_grad, forward, backward, step
    scheduler.step()             # una volta per epoca, dopo optimizer.step()</pre>
<p>Soluzioni ragionate, con i mini esperimenti che abbiamo eseguito, nella sezione <a href="#l16-soluzioni">Soluzioni degli esercizi</a>.</p>
""", sec=("l16-esercizi", "Esercizi", 'scheda 24'), printed=NB + 'cella 28')
