# Ricostruito dal sito pubblicato (lessons/L23.json) l'11/11/2026: i sorgenti originali del 10/11 non erano tornati sul Mac.

s(1, 'Obiettivi e setup', """
<p>Il primo notebook fa tutto il ciclo del <b>self-supervised learning</b> visto in <a href="#L21">L21</a>: si preaddestra una rete <b>senza etichette</b>, poi si congela e si misura quanto sono buone le sue feature usando le etichette solo alla fine, con due classificatori leggerissimi.</p>
<ul>
<li><b>Dati</b>: CIFAR-10, 50 000 immagini di training 32×32 in 10 classi (aereo, auto, uccello, gatto, cervo, cane, rana, cavallo, nave, camion) e 10 000 di test. La cella 2 suggerisce di scaricare l'archivio <code>cifar-10-python.tar.gz</code> da un link OneDrive e di metterlo in <code>./data</code> senza estrarlo: torchvision ne controlla l'MD5 e lo estrae da solo.</li>
<li><b>Metodo</b>: <b>SimSiam</b> (Chen e He 2021), il metodo siamese senza negativi della fine di L21: due viste della stessa immagine, una rete condivisa, un <b>predictor</b> su un solo lato della loss e lo <b>stop-gradient</b>.</li>
<li><b>Valutazione</b>: <b>linear probe</b> e <b>k-NN</b> (k = 20) sulle feature a 512 dimensioni del backbone congelato.</li>
<li><b>Configurazione</b> (cella 6): <code>SSL_EPOCHS = 1</code>, batch 256, lr 0.05; projector a 2048 dimensioni, predictor con strato nascosto a 512; probe per 30 epoche, batch 512, lr 0.01; 5000 immagini di validazione; seed 42.</li>
</ul>
<pre>device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SSL_EPOCHS = 1; SSL_BATCH_SIZE = 256; SSL_LR = 0.05; NUM_WORKERS = 4
PROJECTOR_DIM = 2048; PREDICTOR_HIDDEN_DIM = 512
PROBE_EPOCHS = 30; PROBE_BATCH_SIZE = 512; PROBE_LR = 0.01
VAL_SIZE = 5000; NUM_CLASSES = 10; KNN_K = 20</pre>
<div class="box w"><b>Attenzione: 1 epoca o 10?</b><p>Il codice fissa <code>SSL_EPOCHS = 1</code>, ma il messaggio stampato su CPU («The full 10-epoch run…»), il titolo della sezione 6 («Self-supervised pretraining: 10 epochs») e il commento finale della cella 36 («SSL used 10 image epochs») parlano di <b>10 epoche</b>. Probabilmente il valore è stato abbassato per farlo girare in aula. Per avere le 10 epoche di cui parla il testo basta <code>SSL_EPOCHS = 10</code> (su GPU qualche minuto; su CPU ore). Le nostre cifre (sezione <a href="#l23-risultati">Risultati</a>) sono con 1 epoca, cioè con il notebook così com'è.</p></div>
<div class="box x"><b>Il seme non basta</b><p><code>seed_everything</code> fissa i generatori di Python, NumPy e PyTorch, ma il commento lo dice giusto: su dispositivi diversi (CPU, GPU, versioni diverse di cuDNN) i numeri cambiano lo stesso, perché alcune operazioni non sono deterministiche e l'ordine delle somme in virgola mobile cambia. Il seme rende confrontabili due esperimenti <i>sulla stessa macchina</i>.</p></div>
""", sec=('l23-p1', 'Parte 1 · SimSiam su CIFAR-10', 'schede 1–16'), printed='NOTEBOOK simsiam_cifar10_lab.ipynb · celle 1–6')

s(2, 'Una vista: la pipeline di augmentation', """
<pre>single_view_transform = transforms.Compose([
    transforms.RandomResizedCrop(32, scale=(0.2, 1.0)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomApply([transforms.ColorJitter(0.4, 0.4, 0.2, 0.1)], p=0.8),
    transforms.RandomGrayscale(p=0.2),
    transforms.ToTensor(),
    transforms.Normalize(CIFAR_MEAN, CIFAR_STD)])
eval_transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize(CIFAR_MEAN, CIFAR_STD)])</pre>
<ul>
<li><b>RandomResizedCrop(32, scale=(0.2, 1.0))</b>: sceglie una regione che copre fra il 20% e il 100% dell'<b>area</b> dell'immagine (con un rapporto d'aspetto casuale, di default fra 3/4 e 4/3) e la riporta a 32×32. È la trasformazione più importante: due crop della stessa immagine possono mostrare parti diverse dell'oggetto, e la rete deve dar loro la stessa rappresentazione.</li>
<li><b>Flip orizzontale</b> con probabilità 0,5.</li>
<li><b>ColorJitter</b> applicato con probabilità 0,8: luminosità, contrasto e saturazione moltiplicati per un fattore casuale in [1 − f, 1 + f] (f = 0,4, 0,4, 0,2), tinta spostata di un valore in [−0,1, 0,1] (in frazioni di giro della ruota dei colori). Il commento del notebook dice «in [−factor, +factor]»: per la tinta è letterale, per gli altri tre è il fattore moltiplicativo intorno a 1.</li>
<li><b>Grigio</b> con probabilità 0,2: toglie del tutto il colore.</li>
<li><b>Normalize</b> con media e deviazione standard per canale di CIFAR-10. Le costanti (0.2023, 0.1994, 0.2010) sono quelle storiche dei repository pubblici; le deviazioni standard «vere» dei pixel di CIFAR-10 sono circa 0.247, 0.243, 0.261. Non è un errore: conta usare <b>la stessa normalizzazione</b> in pretraining e valutazione, come dice il commento.</li>
<li><code>eval_transform</code> non ha nulla di casuale: per valutare le feature si usa l'immagine intera, sempre uguale.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 30, § 30.10.2</b><p>Il libro mostra con un esperimento giocattolo (forme colorate, embedding a 2 dimensioni) che sono le <b>trasformazioni</b> a decidere che cosa la rappresentazione impara a ignorare. Con soli crop come viste positive, l'embedding raggruppa le immagini per <b>colore</b>, l'indizio più facile; aggiungendo variazioni casuali di tinta, luminosità e saturazione diventa invariante al colore e raggruppa per <b>forma</b>. È esattamente il ruolo del ColorJitter e del grigio qui: il commento del notebook dice che servono perché le due viste non si possano abbinare «solo con le statistiche di colore». <a href="https://visionbook.mit.edu/representation_learning.html">visionbook § 30.10.2</a>.</p></div>
<div class="box k"><b>Da saper fare</b><p>Per ogni augmentation dire <b>a che cosa rende invariante</b> la rappresentazione (posizione e scala, simmetria sinistra-destra, illuminazione e colore) e perché un'invarianza sbagliata fa danni: con un flip verticale, per esempio, la rete smetterebbe di distinguere sopra da sotto, e con un crop troppo piccolo le due viste non avrebbero più nulla in comune.</p></div>
""", printed='NOTEBOOK simsiam_cifar10_lab.ipynb · celle 7–8')

s(3, 'TwoViews: due viste indipendenti', """
<pre>class TwoViews:
    def __init__(self, transform):
        self.transform = transform
    def __call__(self, image):
        view1 = self.transform(image)   # parametri casuali nuovi
        view2 = self.transform(image)   # di nuovo dall'ORIGINALE
        return view1, view2
ssl_transform = TwoViews(single_view_transform)</pre>
<ul>
<li>Un piccolo <b>wrapper</b>: prende la pipeline di una vista e la chiama due volte sulla <b>stessa immagine originale</b>. Ogni chiamata estrae parametri casuali nuovi (crop, flip, colore), quindi le due viste sono due campioni indipendenti dalla stessa distribuzione di trasformazioni.</li>
<li>Non si trasforma <code>view1</code> per ottenere <code>view2</code>: si accumulerebbero due crop e due cambi di colore, e le viste non sarebbero più simmetriche (una sarebbe sistematicamente più degradata dell'altra).</li>
<li>Le viste nascono <b>nel Dataset</b>, quando un'immagine viene caricata: il ciclo di training riceve tensori già pronti e non contiene codice di augmentation. Lo stesso wrapper funziona invariato per SimCLR, BYOL e Barlow Twins (esercizi della scheda 16).</li>
</ul>
<div class="box w"><b>Attenzione: su Mac (e Windows) il DataLoader si blocca</b><p>Con <code>NUM_WORKERS = 4</code> il DataLoader avvia 4 processi. Su macOS e Windows Python li avvia in modalità <b>spawn</b>: ogni processo riparte da zero e deve ritrovare per nome le classi che riceve. <code>TwoViews</code> è definita dentro il notebook (nel modulo <code>__main__</code> del kernel), che i processi figli non possono reimportare: il primo ciclo su <code>ssl_loader</code> (cella 23; la cella 13 invece funziona, perché lì il dataset si usa senza loader) fallisce con <code>Can't get attribute 'TwoViews' on &lt;module '__main__'&gt;</code> e <i>DataLoader worker exited unexpectedly</i>. Lo abbiamo verificato forzando lo spawn in un kernel Jupyter. Su Colab e su Linux (avvio <b>fork</b>, i figli ereditano la memoria del padre) non succede. Rimedi: <code>NUM_WORKERS = 0</code> (più lento, tutto nel processo principale) oppure spostare <code>TwoViews</code> in un file <code>views.py</code> e importarla.</p></div>
""", printed='NOTEBOOK simsiam_cifar10_lab.ipynb · cella 9')

s(4, 'Dati, split e DataLoader', """
<pre>ssl_dataset     = datasets.CIFAR10(DATA_ROOT, train=True,  download=True, transform=ssl_transform)
feature_dataset = datasets.CIFAR10(DATA_ROOT, train=True,  download=True, transform=eval_transform)
test_dataset    = datasets.CIFAR10(DATA_ROOT, train=False, download=True, transform=eval_transform)
ssl_loader = DataLoader(ssl_dataset, batch_size=256, shuffle=True, drop_last=True, ...)
feature_loader = DataLoader(feature_dataset, batch_size=256, shuffle=False, ...)
# nostra uscita: SSL pretraining images: 50,000 images</pre>
<table>
<tr><th>Fase</th><th>Immagini</th><th>Etichette</th></tr>
<tr><td>Pretraining SSL</td><td>tutte le 50 000 di training</td><td>no</td></tr>
<tr><td>Linear probe e banca del k-NN</td><td>45 000 di training</td><td>sì</td></tr>
<tr><td>Validazione del probe</td><td>le altre 5000 di training</td><td>sì, per scegliere l'epoca</td></tr>
<tr><td>Valutazione finale</td><td>10 000 di test</td><td>sì, una volta sola</td></tr>
</table>
<ul>
<li>Due oggetti dataset sulle <b>stesse immagini di training</b> con trasformazioni diverse: uno dà coppie di viste casuali (per il pretraining), l'altro l'immagine pulita (per le feature). Tenerli separati evita di valutare per sbaglio su viste aumentate.</li>
<li><code>drop_last=True</code> nel loader SSL: 50 000 / 256 = 195,3, quindi si fanno <b>195 passi</b> per epoca e si scartano le ultime 80 immagini (cambiano a ogni epoca, perché il loader mescola). Serve perché le <b>BatchNorm</b> delle teste vogliono più di un esempio per batch e perché ogni passo abbia la stessa dimensione.</li>
<li>I loader di valutazione non mescolano e tengono l'ultimo batch più piccolo: servono tutte le immagini, in ordine.</li>
<li>Il pretraining usa le etichette di CIFAR-10? No: il loader le restituisce comunque (<code>_labels</code>), ma il ciclo le ignora.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Spiegare perché la validazione si ritaglia dal <b>training</b> e non dal test: ogni scelta fatta guardando un insieme (qui la migliore epoca del probe, e il k se lo si cambiasse) «consuma» quell'insieme, che smette di essere una stima onesta. Il test deve restare intatto fino alla fine.</p></div>
""", printed='NOTEBOOK simsiam_cifar10_lab.ipynb · celle 10–12')

s(5, 'Come sono fatte le viste', """
<pre>fig, axes = plt.subplots(3, 4)
for column in range(4):
    original, label = feature_dataset[column]
    (view1, view2), _ = ssl_dataset[column]
    # righe: Original, View 1, View 2; si annulla la normalizzazione solo per disegnare
    axes[row, column].imshow((tensor * std + mean).clamp(0, 1).permute(1, 2, 0))</pre>
<ul>
<li>Per le prime 4 immagini di training la figura mostra l'originale e due viste. Nella nostra esecuzione le classi sono <b>rana, camion, camion e cervo</b>.</li>
<li>Nella nostra figura 5 viste su 8 sono in bianco e nero: con probabilità 0,2 per vista è un caso sfortunato ma possibile (il valore atteso è 1,6 su 8). La rana della vista 1 è ingrandita e più luminosa, il cervo della vista 1 è un crop molto sfocato in cui l'animale quasi non si vede.</li>
<li>Si vede bene che cosa la rete dovrà riconoscere come «la stessa cosa»: crop diversi (a volte solo una parte dell'oggetto, ingrandita), specchiature, colori alterati e qualche vista in bianco e nero.</li>
<li><code>image_for_display</code> annulla la normalizzazione (moltiplica per la deviazione standard, aggiunge la media, taglia in [0, 1]) e porta i canali in fondo (<code>permute(1, 2, 0)</code>), come vuole <code>imshow</code>: la rete invece vede i tensori normalizzati.</li>
<li>Le etichette servono solo per il titolo della figura.</li>
</ul>
<div class="box x"><b>A 32×32 pixel</b><p>I crop piccoli (20% dell'area, cioè circa 14×14 pixel) riportati a 32×32 sono molto sfocati: su CIFAR il RandomResizedCrop usa una scala minima di 0,2 invece dello 0,08 di ImageNet (SimCLR, SimSiam) proprio perché sotto quella soglia di un'immagine 32×32 resterebbe troppo poco.</p></div>
""", img='img/s05.png', printed='NOTEBOOK simsiam_cifar10_lab.ipynb · cella 13')

s(6, 'Il backbone: ResNet-18 per immagini 32×32', """
<pre>backbone = models.resnet18(weights=None, zero_init_residual=True)
backbone.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
backbone.maxpool = nn.Identity()
feature_dim = backbone.fc.in_features      # 512
backbone.fc = nn.Identity()
# nostra uscita: Backbone parameters: 11,168,832</pre>
<ul>
<li><b>Pesi casuali</b> (<code>weights=None</code>): niente ImageNet supervisionato, altrimenti la rete saprebbe già classificare e l'esperimento non direbbe nulla sul self-supervised.</li>
<li>Lo «stem» standard di ResNet (conv 7×7 con stride 2 e max pooling con stride 2) riduce di 4 volte la risoluzione all'inizio: va bene per 224×224, ma un'immagine 32×32 diventerebbe 8×8 prima ancora del primo blocco. Si sostituisce con una <b>conv 3×3 con stride 1</b> e si toglie il max pooling: le mappe restano 32×32, poi 16, 8 e 4 nei quattro stadi. È la stessa modifica del lab CNN della <a href="#L16">L16</a>.</li>
<li><code>fc = nn.Identity()</code>: via il classificatore a 1000 classi; il backbone restituisce il vettore a <b>512 dimensioni</b> dopo il global average pooling. Sono queste le feature che si valuteranno.</li>
<li><code>zero_init_residual=True</code> mette a zero il γ dell'ultima BatchNorm di ogni blocco residuo: all'inizio ogni blocco calcola l'identità e la rete si comporta come una rete meno profonda, il che rende stabili i primi passi (Goyal et al. 2017).</li>
<li>11 168 832 parametri, contro gli 11 689 512 della ResNet-18 originale: −513 000 della fc (512×1000 + 1000), −9 408 + 1 728 per la nuova conv1 (64×3×7×7 contro 64×3×3×3).</li>
</ul>
<div class="box b"><b>Dal libro · cap. 24, § 24.11.3; cap. 12, § 12.7.3</b><p>Il visionbook presenta le ResNet come reti in cui ogni blocco somma all'ingresso una correzione (residuo) e spiega perché questo rende addestrabili reti profonde. Le normalizzazioni (§ 12.7.3) sono il motivo per cui le teste di SimSiam vogliono batch di più esempi: in training la BatchNorm usa media e varianza del batch corrente. <a href="https://visionbook.mit.edu/convolutional_neural_nets.html">visionbook § 24.11.3</a>.</p></div>
""", printed='NOTEBOOK simsiam_cifar10_lab.ipynb · celle 14–15')

s(7, 'SimSiam: projector e predictor', """
<pre>self.projector = nn.Sequential(                 # 512 -> 512 -> 512 -> 2048
    nn.Linear(512, 512, bias=False), nn.BatchNorm1d(512), nn.ReLU(),
    nn.Linear(512, 512, bias=False), nn.BatchNorm1d(512), nn.ReLU(),
    nn.Linear(512, 2048, bias=False), nn.BatchNorm1d(2048, affine=False))
self.predictor = nn.Sequential(                 # 2048 -> 512 -> 2048
    nn.Linear(2048, 512, bias=False), nn.BatchNorm1d(512), nn.ReLU(),
    nn.Linear(512, 2048))</pre>
<ul>
<li>Tre pezzi, tutti condivisi fra le due viste: <b>backbone</b> f (512 dim), <b>projector</b> g (MLP a 3 strati fino a 2048 dim) e <b>predictor</b> h (MLP a 2 strati con un <b>collo di bottiglia</b> a 512).</li>
<li>L'ultima BatchNorm del projector ha <code>affine=False</code>: niente γ e β appresi, l'uscita z ha media 0 e varianza 1 per dimensione sul batch. Niente ReLU dopo, così z può avere componenti negative.</li>
<li>Il predictor finisce con un Linear <b>con bias</b> e senza BatchNorm: deve poter produrre qualunque vettore, perché il suo compito è <b>predire</b> la proiezione dell'altra vista.</li>
<li>I Linear seguiti da BatchNorm non hanno bias (<code>bias=False</code>): la BatchNorm sottrae la media, quindi un bias sarebbe cancellato subito.</li>
<li>Le dimensioni sono quelle dell'articolo per ImageNet (projector a 3 strati a 2048, predictor 2048-512-2048), con lo strato nascosto del projector ridotto a 512 come la feature della ResNet-18.</li>
</ul>
<div class="box w"><b>Attenzione: non è il projector a stare su un solo ramo</b><p>Nella slide di SimSiam della <a href="#L21">L21</a> c'era scritto «Projector only in the first augmentation». Il codice lo smentisce: il projector si applica a <b>entrambe</b> le viste (<code>z1 = projector(h1)</code>, <code>z2 = projector(h2)</code>), ed è il <b>predictor</b> a stare da un solo lato <i>di ciascun termine</i> della loss. Con la loss simmetrizzata il predictor agisce a turno su tutte e due le viste.</p></div>
<div class="box x"><b>Come nell'articolo, con una differenza</b><p>Per CIFAR-10 l'articolo di SimSiam (appendice D) usa un projector a <b>2</b> strati, lr base 0,03, weight decay 5·10⁻⁴, batch 512 e 800 epoche, con un'accuratezza lineare intorno al 91,8%. Il notebook usa invece le scelte dell'articolo per ImageNet (3 strati, lr 0,05, weight decay 10⁻⁴). Con 1 o 10 epoche la differenza non conta.</p></div>
""", printed='NOTEBOOK simsiam_cifar10_lab.ipynb · celle 16–17')

s(8, 'Forward e loss: coseno, simmetria, stop-gradient', """
<pre>def forward(self, view1, view2):
    h1, h2 = self.backbone(view1), self.backbone(view2)       # [B, 512]
    z1, z2 = self.projector(h1), self.projector(h2)           # [B, 2048]
    p1, p2 = self.predictor(z1), self.predictor(z2)           # [B, 2048]
    loss_1_to_2 = -self.criterion(p1, z2.detach()).mean()     # criterion = CosineSimilarity(dim=1)
    loss_2_to_1 = -self.criterion(p2, z1.detach()).mean()
    return 0.5 * (loss_1_to_2 + loss_2_to_1)</pre>
<span class="f">L = −½ [ cos(p<sub>1</sub>, sg(z<sub>2</sub>)) + cos(p<sub>2</sub>, sg(z<sub>1</sub>)) ],  cos(p, z) = pᵀz / (‖p‖ ‖z‖)</span>
<ul>
<li><b>Coseno</b>: <code>CosineSimilarity(dim=1)</code> normalizza i due vettori lungo la dimensione delle feature e ne fa il prodotto scalare, una similarità per immagine del batch; <code>.mean()</code> fa la media sul batch. Il segno meno trasforma «massimizza la similarità» in «minimizza la loss». La loss sta fra −1 (predizione perfettamente allineata) e +1.</li>
<li><b>Simmetria</b>: p<sub>1</sub> predice z<sub>2</sub> e p<sub>2</sub> predice z<sub>1</sub>, e si fa la media dei due termini. Così entrambe le viste passano dal predictor ed entrambe fanno da bersaglio.</li>
<li><b>Stop-gradient</b> (sg, in PyTorch <code>.detach()</code>): nel primo termine z<sub>2</sub> è trattato come una <b>costante</b>, un bersaglio fisso. Il gradiente arriva a backbone e projector solo attraverso il ramo di p<sub>1</sub>. Non è un congelamento: la stessa rete riceve gradiente nel secondo termine, attraverso p<sub>2</sub>.</li>
<li>Non ci sono <b>negativi</b>, né etichette, né un encoder separato aggiornato con la media mobile (quello è BYOL, <a href="#L22">L22</a>).</li>
</ul>
<div class="box k"><b>Da saper fare · coseno e stop-gradient su un esempio</b><p>p = (1, 0), z = (0,6, 0,8): ‖p‖ = ‖z‖ = 1, cos = 0,6, loss del termine −0,6. Il gradiente di cos rispetto a p, a norma unitaria, è z − (cos)·p = (0,6, 0,8) − 0,6·(1, 0) = (0, 0,8): spinge p a ruotare verso z. Senza <code>detach</code> ci sarebbe anche il gradiente rispetto a z, p − (cos)·z = (0,64, −0,48), che spinge z verso p: i due vettori si verrebbero incontro, ed è questa possibilità «di andare incontro» che lascia la porta aperta al collasso.</p></div>
<div class="box b"><b>Dal libro · cap. 30, § 30.10</b><p>Il libro introduce la <b>alignment loss</b> ‖f(T(x)) − f(x)‖² e nota subito il difetto: la si minimizza anche con un f che dà sempre lo stesso vettore (<b>collasso</b>). La sua soluzione sono i negativi (contrastive learning). SimSiam, come BYOL, evita il collasso <b>senza negativi</b>, con l'asimmetria predictor + stop-gradient; il visionbook non tratta questi metodi, che sono in Szeliski § 5.4.7. Con vettori normalizzati, ‖p̂ − ẑ‖² = 2 − 2 cos(p, z): minimizzare l'errore quadratico fra vettori normalizzati o massimizzare il coseno è la stessa cosa. <a href="https://visionbook.mit.edu/representation_learning.html">visionbook § 30.10</a>.</p></div>
""", printed='NOTEBOOK simsiam_cifar10_lab.ipynb · cella 17')

s(9, "L'esperimento sullo stop-gradient", """
<pre>model = SimSiam(backbone, feature_dim, projection_dim=2048, predictor_hidden_dim=512).to(device)
prediction = torch.randn(4, 8, requires_grad=True)
target = torch.randn(4, 8, requires_grad=True)
example_loss = -model.criterion(prediction, target.detach()).mean()
example_loss.backward()
# nostra uscita:
# Prediction receives gradients: True
# Target receives gradients:     False</pre>
<ul>
<li>La cella 18 costruisce il modello e stampa le due teste (le stesse della scheda 7).</li>
<li>La cella 19 è un mini-esperimento con <b>autograd</b> su due tensori casuali 4×8 indipendenti dal modello: dopo <code>backward()</code> il tensore <code>prediction</code> ha un gradiente, <code>target</code> no (<code>target.grad is None</code>), perché è entrato nella loss solo attraverso <code>detach()</code>.</li>
<li><code>detach()</code> restituisce un tensore con gli <b>stessi valori</b> ma staccato dal grafo: per autograd è una costante.</li>
<li>Il commento finale avverte: una loss vicina a −1 da sola <b>non prova</b> che le feature siano buone, perché anche una rete collassata allinea perfettamente le due viste. Per questo il collasso si controlla con altre misure (per esempio la deviazione standard delle uscite normalizzate, che nell'articolo vale circa 1/√d = 1/√2048 ≈ 0,022 quando le cose vanno bene e 0 quando collassa) e alla fine con il probe.</li>
</ul>
<div class="box x"><b>Che cosa succede senza i due ingredienti</b><p>Nell'articolo di SimSiam, togliendo lo stop-gradient la loss arriva subito a −1 e l'accuratezza lineare crolla allo 0,1% (le uscite collassano a un vettore costante); togliendo il predictor (h = identità) succede lo stesso. Gli autori lo interpretano come un algoritmo alla «expectation-maximization»: lo stop-gradient fa sì che il bersaglio sia la stima corrente della rappresentazione «media» dell'immagine sulle augmentation, e il predictor colma la differenza fra una vista e quella media. È un'ipotesi, non un teorema.</p></div>
""", printed='NOTEBOOK simsiam_cifar10_lab.ipynb · celle 18–19')

s(10, 'Ottimizzatore e learning rate', """
<pre>optimizer = torch.optim.SGD([
    {"params": list(model.backbone.parameters()) + list(model.projector.parameters())},
    {"params": model.predictor.parameters()},
], lr=0.05, momentum=0.9, weight_decay=1e-4)
scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=[
    lambda epoch: 0.5 * (1 + math.cos(math.pi * epoch / SSL_EPOCHS)),   # backbone + projector
    lambda epoch: 1.0])                                                   # predictor</pre>
<ul>
<li><b>SGD</b> con momentum 0,9 e weight decay 10⁻⁴, lr 0,05: è la regola dell'articolo lr = 0,05 · B/256 con B = 256.</li>
<li>Due <b>gruppi di parametri</b> con lo stesso lr iniziale ma programmi diversi: backbone e projector seguono un <b>coseno</b> che va da 0,05 a 0 in <code>SSL_EPOCHS</code> epoche; il predictor resta a lr <b>costante</b>. Nell'articolo il predictor a lr fisso funziona leggermente meglio (68,1% contro 67,7% su ImageNet): deve inseguire una rappresentazione che cambia, e un lr che si spegne lo renderebbe pigro.</li>
<li><code>LambdaLR</code> moltiplica il lr iniziale per il valore della funzione; lo <code>scheduler.step()</code> si chiama <b>una volta per epoca</b> (cella 23), quindi il lr è costante dentro un'epoca e cambia a scatti.</li>
<li>La figura (cella 22) disegna i due programmi. Con <code>SSL_EPOCHS = 1</code> ci sono solo due punti: 0,05 all'epoca 0 e 0 all'epoca 1. Ma l'unica epoca di training usa il valore dell'epoca 0: <b>tutto il pretraining avviene a lr 0,05</b>, e il coseno non fa in tempo ad agire.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Calcolare il lr del coseno: η(e) = η<sub>0</sub> · ½ (1 + cos(π e / E)). Con E = 10 ed η<sub>0</sub> = 0,05: η(0) = 0,05, η(5) = 0,025, η(9) ≈ 0,0012. Spiegare perché a metà del programma il lr è esattamente metà: cos(π/2) = 0.</p></div>
<div class="box x"><b>Una piccola svista nel commento</b><p>«Separate parameter groups let's keep…» va letto «let us keep» (o «lets us keep»): è solo un refuso, il codice fa quello che dice.</p></div>
""", img='img/s10.png', printed='NOTEBOOK simsiam_cifar10_lab.ipynb · celle 20–22')

s(11, 'Il ciclo di pretraining', """
<pre>for epoch in range(SSL_EPOCHS):
    model.train()
    for (view1, view2), _labels in tqdm(ssl_loader):
        optimizer.zero_grad(set_to_none=True)
        loss = model(view1.to(device), view2.to(device))
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * view1.size(0); total_images += view1.size(0)
    ssl_losses.append(total_loss / total_images)
    scheduler.step()
# nostra uscita: SSL 01/01 | loss -0.3639 | 1540.5 s</pre>
<ul>
<li>Il ciclo standard di PyTorch: <code>train()</code> (le BatchNorm usano e aggiornano le statistiche del batch), azzera i gradienti, forward con la loss, backward, passo dell'ottimizzatore.</li>
<li>Ogni passo elabora <b>due</b> viste di 256 immagini: il costo è quello di un batch da 512.</li>
<li>La loss di epoca è la media pesata per il numero di immagini (qui tutti i batch sono da 256 grazie a <code>drop_last</code>).</li>
<li>Nella nostra esecuzione su CPU l'unica epoca (195 passi) ha richiesto <b>1540 secondi (circa 26 minuti)</b> e la loss media è <b>−0,364</b>. Su una GPU è questione di decine di secondi.</li>
<li>La figura della cella 24 con una sola epoca è un solo punto. Con più epoche la curva scende verso −1; da sola non dice se la rappresentazione è utile (scheda 9): lo dirà il probe.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Ricordare l'ordine <code>zero_grad → forward → backward → step</code> e spiegare dove si «vede» lo stop-gradient: in <code>loss.backward()</code> il gradiente scorre solo lungo i rami di p<sub>1</sub> e p<sub>2</sub>; i rami di z<sub>1</sub> e z<sub>2</sub> usati come bersaglio sono staccati.</p></div>
""", img='img/s11.png', printed='NOTEBOOK simsiam_cifar10_lab.ipynb · celle 23–24')

s(12, 'Congelare il backbone ed estrarre le feature', """
<pre>@torch.no_grad()
def extract_features(backbone, loader, device):
    backbone.eval()                        # BatchNorm con le statistiche accumulate
    for images, targets in loader:
        h = backbone(images.to(device))    # [B, 512]
        h = F.normalize(h, dim=1)          # ogni vettore a norma 1
        ...
model.backbone.requires_grad_(False)
trainval_features, trainval_labels = extract_features(model.backbone, feature_loader, device)
indices = torch.randperm(50000, generator=torch.Generator().manual_seed(SEED))
val_indices, train_indices = indices[:5000], indices[5000:]
# nostra uscita: Features extracted and cached: (50000, 512)
#                Probe train / kNN bank: 45,000 | Validation: 5,000</pre>
<ul>
<li>Il <b>protocollo congelato</b>: projector e predictor si buttano via, del modello resta solo il backbone, che non verrà più aggiornato. Le etichette entrano in gioco solo adesso.</li>
<li><code>eval()</code> e <code>no_grad()</code> fanno due cose diverse: <code>eval()</code> fa usare alla BatchNorm le <b>medie mobili</b> accumulate in training invece delle statistiche del batch (così la feature di un'immagine non dipende dalle altre immagini del batch); <code>no_grad()</code> spegne solo autograd. Il commento lo dice giusto.</li>
<li><b>Normalizzazione L2</b> per immagine: ogni vettore viene diviso per la sua norma. Non si stima nulla dai dati (nessuna media o varianza calcolata sul training), quindi non c'è rischio di «far filtrare» informazione dalla validazione o dal test. Con vettori unitari il k-NN con distanza euclidea e quello con il coseno danno gli stessi vicini.</li>
<li>Le feature si calcolano <b>una volta</b> e si tengono in memoria (50 000 × 512 float = circa 100 MB): il probe dopo lavora su vettori, non più su immagini.</li>
<li>Lo split 45 000 / 5 000 è casuale ma con seme fisso, e lo stesso per probe e k-NN.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 37, § 37.3.1</b><p>Il visionbook descrive il <b>finetuning di sottoparti</b>: si può congelare un modulo preaddestrato perché non dimentichi ciò che sa e addestrare solo i moduli nuovi. Qui il caso estremo: tutto il backbone congelato, una sola testa lineare nuova. <a href="https://visionbook.mit.edu/transfer_learning.html">visionbook § 37.3.1</a>.</p></div>
""", printed='NOTEBOOK simsiam_cifar10_lab.ipynb · celle 25–27')

s(13, 'Linear probe', """
<pre>linear_probe = nn.Linear(512, 10)                     # logits = W h + b
probe_optimizer = torch.optim.Adam(linear_probe.parameters(), lr=0.01)
probe_scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(probe_optimizer, T_max=30)
for epoch in range(30):
    for features, labels in probe_train_loader:       # vettori in cache, niente ResNet
        loss = F.cross_entropy(linear_probe(features), labels)
        ...
    val_accuracy = linear_accuracy(linear_probe, probe_val_loader, device)
    if val_accuracy > best_val_accuracy:
        best_probe_state = copy.deepcopy(linear_probe.state_dict())
linear_probe.load_state_dict(best_probe_state)
# nostra uscita: Probe 01/30 | val accuracy 30.12% … Probe 30/30 | val accuracy 38.20%
#                Best linear-probe validation accuracy: 38.58%</pre>
<ul>
<li>Il <b>linear probe</b> è un solo strato lineare 512 → 10, senza strati nascosti né non linearità: 5130 parametri, addestrati con la <b>cross-entropy</b> sulle 45 000 feature congelate. Misura quanto le classi sono <b>linearmente separabili</b> nello spazio delle feature.</li>
<li>Adam con lr 0,01 e coseno su 30 epoche; dopo ogni epoca si misura l'accuratezza sulla validazione e si tiene la <b>miglior epoca</b> (una forma di early stopping).</li>
<li><code>copy.deepcopy</code> è necessario: <code>state_dict()</code> restituisce riferimenti ai tensori dei pesi, che continuerebbero a cambiare con l'addestramento.</li>
<li>Nella nostra esecuzione l'accuratezza di validazione migliore è <b>38,58% (all'epoca 24; parte dal 30,1% dopo la prima epoca e si stabilizza intorno al 38%)</b> (curva della cella 32 nella miniatura).</li>
</ul>
<div class="box b"><b>Dal libro · cap. 37, § 37.3.2 Heads and Probes</b><p>Un modulo che legge le feature di una rete e produce una nuova predizione si chiama <b>testa</b> (<i>read-out</i>); se è lineare, <b>linear probe</b>. Il libro gli dà due usi: riadattare una rete a un compito nuovo con pochi parametri (spesso con soluzioni in forma chiusa), e <b>sondare</b> che cosa sa uno strato: se una feature map permette di classificare linearmente un attributo, quella feature map «conosce» l'attributo. Qui è il secondo uso: il probe è uno strumento di misura della rappresentazione. <a href="https://visionbook.mit.edu/transfer_learning.html">visionbook § 37.3.2</a>.</p></div>
<div class="box k"><b>Da saper fare</b><p>Distinguere <b>linear probe</b> (backbone congelato, si addestra solo la testa lineare) da <b>finetuning</b> (si aggiornano anche i pesi del backbone, di solito con lr più basso). Il probe misura la qualità della rappresentazione così com'è; il finetuning misura quanto è un buon punto di partenza.</p></div>
""", img='img/s13.png', printed='NOTEBOOK simsiam_cifar10_lab.ipynb · celle 28–32')

s(14, 'k-NN: nessun classificatore da addestrare', """
<pre>knn_classifier = KNeighborsClassifier(n_neighbors=20, metric="cosine", algorithm="brute", n_jobs=-1)
knn_classifier.fit(train_features.numpy(), train_labels.numpy())      # memorizza 45 000 vettori
knn_val_predictions = knn_classifier.predict(val_features.numpy())
# nostra uscita: kNN (k=20) validation accuracy: 37.02%</pre>
<ul>
<li>Il <b>k-NN</b> non impara nulla: «addestrarlo» vuol dire memorizzare la <b>banca</b> delle 45 000 feature con le loro etichette. Per una query si cercano le 20 feature più simili (similarità coseno, ricerca esaustiva <code>brute</code>) e si sceglie la classe <b>più votata</b>.</li>
<li>Il voto qui è a maggioranza semplice (<code>weights="uniform"</code>, il default di scikit-learn); nella letteratura SSL (Wu et al. 2018, e la slide della L21) si usa spesso un voto <b>pesato</b> con exp(similarità/τ).</li>
<li>Query e banca sono disgiunte (validazione contro i 45 000 di training), quindi un'immagine non può trovare sé stessa come vicino.</li>
<li>k = 20 è fissato in anticipo; se lo si volesse scegliere, si dovrebbe guardare solo la validazione.</li>
<li>Il k-NN premia una rappresentazione in cui le immagini della stessa classe sono <b>vicine</b>; il linear probe una in cui le classi sono <b>separabili da iperpiani</b>, anche se sparse. Di solito il probe dà qualche punto in più.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 30, § 30.4.1</b><p>Il libro valuta le rappresentazioni proprio così: guardando i vicini più prossimi e misurando l'accuratezza di un classificatore <b>1-NN</b> sulle feature di ogni strato di un autoencoder. Il risultato: il colore si classifica meglio sui pixel grezzi e peggiora con la profondità, la forma il contrario. Nessuna rappresentazione è la migliore per tutto: dipende da che cosa si vuole leggere. <a href="https://visionbook.mit.edu/representation_learning.html">visionbook § 30.4.1</a>.</p></div>
<div class="box k"><b>Da saper fare · un voto k-NN</b><p>k = 5, similarità dei 5 vicini: 0,91 cane, 0,88 gatto, 0,85 cane, 0,80 cane, 0,79 gatto. Voto semplice: cane 3, gatto 2 → cane. Voto pesato con exp(s/τ), τ = 0,07: i pesi relativi sono circa 1, 0,65, 0,42, 0,21, 0,18, cioè cane 1,63 contro gatto 0,83 → sempre cane, ma con un margine che tiene conto di quanto i vicini sono simili.</p></div>
""", printed='NOTEBOOK simsiam_cifar10_lab.ipynb · celle 33–34')

s(15, 'Valutazione finale sul test', """
<pre>test_features, test_labels = extract_features(model.backbone, test_loader, device)
linear_test_accuracy = linear_accuracy(linear_probe, probe_test_loader, device)
knn_test_accuracy = (knn_classifier.predict(test_features) == test_labels).mean()
# nostra uscita:
# SimSiam | ResNet-18 | 1 CIFAR-10 pretraining epochs
# Linear probe test accuracy: 37.99%
# kNN (k=20) test accuracy:    37.40%</pre>
<ul>
<li>Tutte le scelte sono fatte (epoca del probe, k): si valuta <b>una sola volta</b> sui 10 000 di test, e questi numeri non si usano per cambiare nulla.</li>
<li>I due metodi usano le <b>stesse</b> feature congelate e le stesse 45 000 etichette: la differenza fra i due numeri dipende solo dal modo di leggere la rappresentazione.</li>
<li>Il confronto più istruttivo è con una ResNet-18 <b>a pesi casuali</b> valutata nello stesso modo (lo abbiamo fatto noi, sezione <a href="#l23-risultati">Risultati</a>): la differenza è ciò che il pretraining ha davvero insegnato. Una rete casuale non dà il 10% del caso, perché anche feature casuali di una CNN conservano informazione su colori e strutture locali.</li>
</ul>
<div class="box w"><b>Attenzione: il commento finale non corrisponde al codice</b><p>Il commento dice «SSL used 10 image epochs», ma con <code>SSL_EPOCHS = 1</code> il pretraining ha fatto una sola epoca. La riga stampata è giusta perché usa la variabile (<code>{SSL_EPOCHS} CIFAR-10 pretraining epochs</code>).</p></div>
<div class="box x"><b>Ordini di grandezza</b><p>Con 800 epoche l'articolo di SimSiam riporta circa il 91,8% di accuratezza lineare su CIFAR-10 con una ResNet-18; una ResNet-18 supervisionata arriva intorno al 93–95%. Con 1 o 10 epoche si è molto lontani: il pretraining self-supervised richiede tempi lunghi, perché il segnale (allineare viste) è molto più debole di un'etichetta.</p></div>
""", printed='NOTEBOOK simsiam_cifar10_lab.ipynb · celle 35–36')

s(16, 'Esercizi: SimCLR, BYOL, Barlow Twins', """
<table>
<tr><th>Metodo</th><th>Cosa cambia rispetto a SimSiam</th></tr>
<tr><td>SimCLR</td><td>niente predictor; loss <b>contrastiva</b> NT-Xent con i negativi del batch</td></tr>
<tr><td>BYOL</td><td>un <b>teacher</b>, copia di backbone e projector aggiornata con <b>EMA</b> dopo <code>optimizer.step()</code>; loss MSE fra vettori normalizzati</td></tr>
<tr><td>Barlow Twins</td><td>niente predictor; loss sulla <b>matrice di cross-correlazione</b> C</td></tr>
</table>
<ul>
<li>Trasformazioni, loader, backbone e valutazione restano gli stessi: cambia solo la classe del modello (e, per BYOL, una riga nel ciclo di training per aggiornare il teacher).</li>
<li><b>SimCLR</b> (<a href="#L21">L21</a>): le 2B viste del batch normalizzate, similarità coseno divise per τ, per ogni vista la positiva è l'altra vista della stessa immagine e le 2B − 2 restanti sono negativi; è una cross-entropy su 2B − 1 «classi».</li>
<li><b>BYOL</b> (<a href="#L22">L22</a>): lo studente ha backbone, projector e predictor; il teacher solo backbone e projector, non riceve gradienti e segue lo studente con ξ ← m ξ + (1 − m) θ. Loss 2 − 2 cos(p, z<sub>teacher</sub>), simmetrizzata.</li>
<li><b>Barlow Twins</b> (L22): le due proiezioni si standardizzano <b>lungo il batch</b>, C = z<sub>1</sub>ᵀ z<sub>2</sub> / N è una matrice D × D; la loss spinge la diagonale a 1 (invarianza) e il resto a 0 (ridondanza), con peso λ = 5·10⁻³ sui termini fuori diagonale.</li>
<li>Il codice di tutti e tre, provato da noi, è nella sezione <a href="#l23-soluzioni">Soluzioni</a> in fondo alla pagina.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Per ognuno dei quattro metodi dire <b>che cosa impedisce il collasso</b>: SimCLR i negativi (termine di uniformità); SimSiam predictor + stop-gradient; BYOL predictor + teacher EMA (+ stop-gradient implicito: il teacher non ha gradienti); Barlow Twins la decorrelazione delle dimensioni (una rete collassata ha C con colonne uguali, lontana dall'identità).</p></div>
""", printed='NOTEBOOK simsiam_cifar10_lab.ipynb · cella 37')

s(17, 'Obiettivi e setup del secondo notebook', """
<p>Il secondo notebook rovescia la prospettiva: niente pretraining, si prende un <b>vision foundation model</b> già addestrato in modo self-supervised, <b>DINOv3</b> (<a href="#L22">L22</a>), lo si <b>congela</b> e lo si usa come estrattore di feature per un compito <b>denso</b>: dire, patch per patch, se appartiene al <b>primo piano</b> (l'oggetto) o allo <b>sfondo</b>.</p>
<ul>
<li><b>Backbone</b>: DINOv3 <b>ViT-S/16</b> preaddestrato su <b>LVD-1689M</b> (1,689 miliardi di immagini curate). È il modello piccolo della famiglia (21 milioni di parametri), distillato dal ViT-7B; le feature hanno 384 dimensioni.</li>
<li><b>Dati</b>: solo <b>9 immagini</b> annotate con una maschera di primo piano, più una foto nuova per la demo.</li>
<li><b>Classificatore</b>: una <b>regressione logistica</b> (scikit-learn) sulle feature delle patch, cioè un linear probe denso.</li>
<li><b>Validazione</b>: <b>leave-one-image-out</b> con l'<b>average precision</b> come metrica.</li>
<li>Requisiti: Python ≥ 3.10, PyTorch ≥ 2.7.1, torchvision ≥ 0.22.1 (controllati nella cella 4). I pesi si scaricano dalla pagina di Meta dopo una richiesta di accesso; il codice dell'architettura dal repository GitHub <code>facebookresearch/dinov3</code>, a una revisione fissata.</li>
</ul>
<pre>MODEL_NAME = "dinov3_vits16"; PATCH_SIZE = 16; LONG_EDGE = 448
WEIGHTS_LOCATION = "./dinov3_vits16_pretrain_lvd1689m-08c60483.pth"
BACKGROUND_MAX = 0.01; FOREGROUND_MIN = 0.99
C_VALUES = np.logspace(-7, 0, 8)      # 1e-7, 1e-6, ..., 1e0
MAX_ITER = 2000; MASK_THRESHOLD = 0.5; MEDIAN_SIZE = 3</pre>
<div class="box w"><b>Attenzione: la variabile DINOV3_WEIGHTS non viene letta</b><p>Il commento della cella 5 dice «Optional: set DINOV3_WEIGHTS to your checkpoint path», ma il codice scrive il percorso fisso <code>WEIGHTS_LOCATION = "./dinov3_vits16_pretrain_lvd1689m-08c60483.pth"</code> e non legge mai la variabile d'ambiente (a differenza di <code>DINOV3_LOCATION</code> per il codice, letta con <code>os.getenv</code>). Se il file non è nella cartella del notebook, la cella 15 si ferma con <i>Checkpoint not found</i>. Rimedio: copiare il file lì, oppure scrivere <code>WEIGHTS_LOCATION = os.getenv("DINOV3_WEIGHTS", "./dinov3_vits16_pretrain_lvd1689m-08c60483.pth")</code>.</p></div>
<div class="box x"><b>La nostra esecuzione</b><p>I pesi di DINOv3 si ottengono solo con l'autorizzazione di Meta, che noi non abbiamo: abbiamo eseguito le celle 1–12 (dati, griglia di patch, bersagli) e verificato tutte le dimensioni, ma non l'estrazione delle feature né il probe. Le figure delle schede 17–21 sono nostre; per le schede 22–25 descriviamo che cosa il codice produce, senza inventare numeri.</p></div>
""", sec=('l23-p2', 'Parte 2 · DINOv3: segmentazione del primo piano', 'schede 17–25'), printed='NOTEBOOK dinov3_foreground_segmentation_lab.ipynb · celle 1–5')

s(18, "I dati: nove immagini con la maschera nell'alfa", """
<pre>BASE_URL = "https://dl.fbaipublicfiles.com/dinov3/notebooks/foreground_segmentation"
image_archive = download_cached(f"{BASE_URL}/foreground_segmentation_images.tar.gz", ...)
label_archive = download_cached(f"{BASE_URL}/foreground_segmentation_labels.tar.gz", ...)
images = [image_records[i] for i in sample_ids]                    # PIL RGB
alpha_masks = [label_records[i].getchannel("A") for i in sample_ids]
# nostra uscita: Loaded 9 correctly paired RGB images and alpha masks.</pre>
<ul>
<li>Sono le stesse 9 immagini del notebook ufficiale di DINOv3: tre gatti su una poltrona viola, un uovo alla coque in un portauovo a forma di gallina con il guscio accanto, un cinghiale in un sottobosco, una crostata di pere, una gallina su un cortile di ghiaia, una pila di pancake, un uccellino di metallo su un tavolo (figura nella miniatura).</li>
<li>Le etichette sono PNG con la maschera nel <b>canale alfa</b>: 0 = sfondo, 255 = primo piano. <code>read_image_archive</code> legge gli archivi <code>tar.gz</code> in memoria, ricava l'ID dal numero finale del nome del file e controlla che immagini e maschere corrispondano (stessi ID, stesse dimensioni).</li>
<li><code>download_cached</code> scrive prima in un file <code>.part</code> e lo rinomina solo a download finito: un download interrotto non viene mai scambiato per completo. In caso d'errore non stampa l'URL, per non salvare nel notebook un eventuale link autorizzato con il token.</li>
<li>La cella 9 mostra l'immagine 1 (gatto tigrato sdraiato sulla schiena su un cuscino a pois), la sua maschera, il solo primo piano su bianco e il solo sfondo. Le foto sono 4032×3024 (due verticali, 3024×4032).</li>
<li>Il backbone è self-supervised, ma questo addestramento è <b>supervisionato</b>: le maschere servono come bersagli del probe, mai come ingresso della rete.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Spiegare perché 9 immagini bastano: non si addestra una rete, ma 385 numeri (384 pesi + un bias), e ogni immagine fornisce centinaia di esempi (una per patch). Il lavoro difficile, cioè avere feature in cui «oggetto» e «sfondo» sono separabili, l'ha già fatto il pretraining.</p></div>
""", img='img/s18.png', printed='NOTEBOOK dinov3_foreground_segmentation_lab.ipynb · celle 6–9')

s(19, 'Dai pixel alla griglia di patch', """
<pre>def patch_aligned_size(image):
    width, height = image.size
    scale = 448 / max(width, height)
    return (max(16, int(height * scale) // 16 * 16), max(16, int(width * scale) // 16 * 16))
def prepare_rgb(image):        # resize bilineare con antialias, to_tensor, Normalize(ImageNet)
def patch_foreground_fraction(mask, size):
    alpha = TF.to_tensor(TF.resize(mask, size, BILINEAR, antialias=True))   # [1, H, W] in [0, 1]
    pooled = F.avg_pool2d(alpha.unsqueeze(0), 16, stride=16)               # [1, 1, H/16, W/16]
    return alpha[0], pooled[0, 0]
# nostra uscita: Number of patch tokens: 588</pre>
<ul>
<li>Un <b>ViT/16</b> taglia l'immagine in patch 16×16 non sovrapposte e ne fa un token ciascuna (<a href="#L17">L17</a>, <a href="#L18">L18</a>). Perché ogni patch sia intera, i lati devono essere multipli di 16: si porta il lato lungo a 448 e si arrotonda <b>per difetto</b> ciascun lato a un multiplo di 16, mantenendo (quasi) il rapporto d'aspetto.</li>
<li>Esempio: 4032×3024 → scala 448/4032 = 1/9 → 448×336 (lati già multipli di 16: 28 e 21 patch) → <b>griglia 21×28 = 588 patch</b>, 588 token per immagine (più il [CLS] e i token di registro, che si scartano).</li>
<li>Normalizzazione ImageNet (media 0,485, 0,456, 0,406; deviazione standard 0,229, 0,224, 0,225): è quella con cui sono stati addestrati i pesi LVD-1689M.</li>
<li>La maschera si ridimensiona alle <b>stesse</b> dimensioni con interpolazione bilineare (l'alfa è una copertura continua; per una maschera di classi discrete si userebbe il nearest neighbor), poi un <b>average pooling 16×16 con stride 16</b> dà la frazione di primo piano di ogni patch. Nessun parametro appreso: è un filtro a scatola seguito da sottocampionamento (<a href="#L6">L6</a>).</li>
<li>Bersagli: frazione &lt; 0,01 → <b>sfondo</b> (0), &gt; 0,99 → <b>primo piano</b> (1), tutto il resto → <b>ignorato</b> (−1). Le patch miste stanno sul <b>bordo</b> dell'oggetto: tenerle fuori semplifica il compito e la validazione.</li>
<li>La figura (cella 12): alfa ridimensionata 336×448, copertura per patch 21×28 (le patch di bordo sono grigie), bersagli (giallo primo piano, verde-azzurro sfondo, viola ignorate: un anello di una patch intorno al gatto).</li>
</ul>
<div class="box k"><b>Da saper fare · conti sulla griglia</b><p>Nelle 9 immagini (misurato da noi): 9 × 588 = <b>5292 patch</b>, di cui 4702 tenute e 590 ignorate (11%); delle tenute, 1086 di primo piano, cioè il <b>23,1%</b>. Per l'immagine 1: 519 tenute su 588, 82 di primo piano. Saper rifare il conto della griglia per un'altra foto: 1600×1200 → 448×336 → 21×28.</p></div>
<div class="box x"><b>Che cosa si perde</b><p>Una patch è 16×16 pixel dell'immagine ridimensionata, cioè 144×144 pixel della foto originale da 4032: la maschera finale non potrà essere più fine di così. I dettagli sottili (zampe, coda, baffi) finiscono nelle patch miste o spariscono.</p></div>
""", img='img/s19.png', printed='NOTEBOOK dinov3_foreground_segmentation_lab.ipynb · celle 10–12')

s(20, 'Caricare e congelare DINOv3', """
<pre>sys.path.insert(0, str(repo))
from dinov3.hub import backbones as dino_backbones
model = getattr(dino_backbones, MODEL_NAME)(weights=str(checkpoint_path.resolve()), pretrained=True)
model = model.to(device).eval()
model.requires_grad_(False)
feature_dim = model.embed_dim       # 384 per ViT-S/16; 768 per B/16; 1024 per L/16
assert model.patch_size == PATCH_SIZE
assert not any(p.requires_grad for p in model.parameters())</pre>
<ul>
<li>La tabella della cella 13 riassume il lab: un foundation model preaddestrato, <b>un vettore di feature per patch</b>, backbone <b>congelato</b>, le maschere binarie supervisionano solo il probe lineare.</li>
<li>Servono due cose distinte: il <b>codice</b> dell'architettura (dal repository GitHub, scaricato come zip a una revisione fissata, così il notebook non si rompe se il repository cambia) e i <b>pesi</b> (file <code>.pth</code>, dalla pagina di Meta). Il percorso dei pesi può essere un file locale o un URL autorizzato; in questo secondo caso il file viene salvato con il nome ufficiale, senza la parte di query dell'URL.</li>
<li>Dopo l'uso <code>WEIGHTS_LOCATION</code> viene svuotata: se si riesegue la cella, il notebook chiede di nuovo il percorso con <code>getpass</code> invece di lasciare un URL con il token nel notebook salvato.</li>
<li><code>eval()</code> e <code>requires_grad_(False)</code>: comportamento di inferenza e nessun gradiente. Gli <code>assert</code> verificano che la patch sia 16 e che non ci sia alcun parametro addestrabile.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 37, § 37.3.1</b><p>L'esempio del visionbook per il finetuning di sottoparti è proprio questo: un sistema in cui il primo modulo, <b>featurize</b>, è DINO preaddestrato e <b>congelato</b>, un estrattore di feature generico che non si aggiorna per ogni nuovo problema; sopra si mettono moduli nuovi o rifiniti (profondità, classificazione per pixel, detector). Il lab è la versione minima: featurizer congelato + un classificatore lineare per patch. <a href="https://visionbook.mit.edu/transfer_learning.html">visionbook § 37.3.1</a>.</p></div>
""", printed='NOTEBOOK dinov3_foreground_segmentation_lab.ipynb · celle 13–15')

s(21, 'Estrarre le feature delle patch', """
<pre>@torch.inference_mode()
def extract_patch_features(image):
    display_tensor, normalized = prepare_rgb(image)
    feature_map = model.get_intermediate_layers(normalized[None].to(device), n=1, reshape=True, norm=True)[0]
    # [1, 384, Gh, Gw] -> [384, Gh*Gw] -> [Gh*Gw, 384]
    features = feature_map[0].flatten(1).transpose(0, 1).float().cpu().numpy()
    return features, (Gh, Gw), display_tensor
keep = (coverage &lt; 0.01) | (coverage &gt; 0.99)
targets = (coverage[keep] &gt; 0.99).astype(np.int64)
X = np.concatenate(feature_parts); y = np.concatenate(target_parts); image_ids = np.concatenate(group_parts)</pre>
<ul>
<li><code>get_intermediate_layers(n=1)</code> restituisce l'uscita dell'<b>ultimo</b> blocco transformer; <code>reshape=True</code> scarta il token [CLS] e i <b>token di registro</b> (in DINOv3 «storage tokens») e rimette i token di patch sulla griglia [1, D, Gh, Gw]; <code>norm=True</code> applica la LayerNorm finale del modello (non è una normalizzazione L2 a norma 1, lo precisa il commento).</li>
<li>La mappa si «srotola» in una matrice <b>[Gh·Gw, 384]</b>, una riga per patch in ordine riga per riga: lo stesso ordine di <code>flatten()</code> sulla griglia dei bersagli, così riga i della matrice e bersaglio i parlano della stessa patch.</li>
<li>Si elabora un'immagine alla volta (immagini con proporzioni diverse non si possono impilare in un batch senza padding), in float32 su CPU o GPU.</li>
<li>Per ogni immagine si tengono solo le patch nette, si controlla che ci siano sia primo piano sia sfondo, e si ricorda l'<b>ID dell'immagine</b> di ogni riga (<code>image_ids</code>): servirà per la validazione.</li>
<li>Risultato atteso con DINOv3: <code>X</code> di forma <b>(4702, 384)</b>, <code>y</code> (4702,) con media 0,231 (le cifre di righe e prevalenza le abbiamo calcolate noi dalle maschere; non dipendono dal backbone).</li>
</ul>
<div class="box b"><b>Dal libro · cap. 31, § 31.3.2 Affinity-Based Segmentation</b><p>Il visionbook spiega perché le feature di questi modelli segmentano: metodi come SimCLR, MoCo e DINO imparano un embedding in cui patch che «stanno insieme» sono vicine; applicati densamente danno una mappa C × N × M in cui ogni posizione ha un vettore, e basta un k-means sui vettori per ottenere una segmentazione (fig. 31.7 con DINO). Il lab fa la versione supervisionata: invece di raggruppare senza etichette, una regressione logistica impara quale direzione dello spazio delle feature separa oggetto da sfondo. <a href="https://visionbook.mit.edu/perceptual_organization.html">visionbook § 31.3.2</a>.</p></div>
""", printed='NOTEBOOK dinov3_foreground_segmentation_lab.ipynb · celle 16–18')

s(22, 'Il probe: regressione logistica e leave-one-image-out', """
<span class="f">p(primo piano | h) = σ(wᵀh + b) = 1 / (1 + e<sup>−(wᵀh + b)</sup>)</span>
<pre>def make_probe(c):
    return LogisticRegression(C=float(c), solver="lbfgs", max_iter=2000, random_state=SEED)
for held_out in range(9):                               # 9 fold
    train_selection = image_ids != held_out; val_selection = image_ids == held_out
    for c_index, c in enumerate(C_VALUES):              # 8 valori di C
        probe = make_probe(c).fit(X[train_selection], y[train_selection])
        probability = probe.predict_proba(X[val_selection])[:, 1]
        scores[held_out, c_index] = average_precision_score(y[val_selection], probability)
# 9 × 8 = 72 addestramenti</pre>
<ul>
<li>La <b>regressione logistica</b> è il linear probe di un problema a due classi: un prodotto scalare fra la feature h (384 numeri) e un vettore di pesi w, più un bias, passato nella sigmoide. Gli <b>stessi</b> w e b valgono per tutte le patch di tutte le immagini: è una convoluzione 1×1 sulla mappa di feature.</li>
<li><b>C</b> è l'<b>inverso</b> della forza della regolarizzazione L2: scikit-learn minimizza ½‖w‖² + C · Σ log-loss, quindi C piccolo = pesi piccoli = modello molto regolarizzato. Si provano 8 valori su scala logaritmica, da 10⁻⁷ a 1.</li>
<li><b>Leave-one-image-out</b>: per ogni C si addestra su 8 immagini e si valuta sulla nona, a turno. Le patch vicine della stessa immagine sono molto <b>correlate</b> (stesso oggetto, stessa luce): con uno split casuale per patch, patch quasi gemelle finirebbero sia in training sia in validazione e la stima sarebbe ottimista. Validare per immagine misura quello che serve davvero: funziona su una foto <b>mai vista</b>?</li>
<li>Ogni patch riceve così, per ogni C, una probabilità «fuori fold» (<code>oof_probabilities</code>), prodotta da un modello che non ha mai visto la sua immagine.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Spiegare perché una regressione logistica sulle feature di un ViT congelato è un <b>linear probe denso</b>, e perché lo split va fatto per <b>gruppi</b> (immagini) quando gli esempi non sono indipendenti. In scikit-learn esiste già: <code>LeaveOneGroupOut</code> o <code>GroupKFold</code> con <code>groups=image_ids</code>.</p></div>
""", printed='NOTEBOOK dinov3_foreground_segmentation_lab.ipynb · celle 19, 21')

s(23, "Average precision invece dell'accuratezza", """
<span class="f">AP = Σ<sub>n</sub> (R<sub>n</sub> − R<sub>n−1</sub>) P<sub>n</sub></span>
<ul>
<li>Le classi sono <b>sbilanciate</b>: il primo piano è il 23% delle patch tenute (in alcune immagini molto meno: 21 su 556 nell'immagine 5, il cinghiale). Un classificatore che dice sempre «sfondo» avrebbe il 77% di accuratezza e sarebbe inutile.</li>
<li><b>Precisione</b>: delle patch dichiarate primo piano, quante lo sono davvero. <b>Recall</b>: delle patch di primo piano vere, quante sono state trovate. Entrambe dipendono dalla soglia sul punteggio.</li>
<li>L'<b>average precision</b> ordina le patch per probabilità decrescente e scorre tutte le soglie: a ogni soglia n prende la precisione P<sub>n</sub>, pesata per quanto è cresciuta la recall (R<sub>n</sub> − R<sub>n−1</sub>). È l'area sotto la curva precisione-recall, calcolata a gradini (è la definizione di <code>average_precision_score</code> di scikit-learn). Vale 1 se tutte le patch di primo piano hanno punteggio più alto di tutte quelle di sfondo.</li>
<li>Non dipende da una soglia scelta, ma solo dall'<b>ordinamento</b>: misura se il probe sa mettere l'oggetto sopra lo sfondo.</li>
<li>Si fa la <b>media sulle 9 immagini</b> (non sulle patch): un'immagine con molte patch non pesa più di una con poche.</li>
</ul>
<div class="box k"><b>Da saper fare · AP su 6 patch</b><p>Punteggi in ordine decrescente con etichette 1, 1, 0, 1, 0, 0 (3 positivi). Scorrendo: dopo la 1ª patch P = 1, R = 1/3; dopo la 2ª P = 1, R = 2/3; la 3ª è negativa (R non cresce, non conta); dopo la 4ª P = 3/4, R = 1. AP = (1/3)·1 + (1/3)·1 + (1/3)·(3/4) = 0,917. L'accuratezza con soglia fra 4ª e 5ª patch sarebbe 5/6.</p></div>
<div class="box b"><b>Dal libro · cap. 50, § 50.4.3</b><p>Il visionbook definisce precisione e recall in funzione di una soglia β sul punteggio: precisione(β) = Σ 1(ŷ<sub>i</sub> &gt; β) y<sub>i</sub> / Σ 1(ŷ<sub>i</sub> &gt; β), recall(β) = Σ 1(ŷ<sub>i</sub> &gt; β) y<sub>i</sub> / Σ y<sub>i</sub>, e l'AP come area sotto la curva precisione-recall, fra 0 e 1. Lì le unità sono box di detection (<a href="#L19">L19</a>, <a href="#L20">L20</a>), qui patch: la logica è la stessa. <a href="https://visionbook.mit.edu/object_recognition_v3.html">visionbook § 50.4.3</a>.</p></div>
""", printed='NOTEBOOK dinov3_foreground_segmentation_lab.ipynb · cella 20')

s(24, 'Scegliere C e leggere le curve precisione-recall', """
<pre>mean_ap = scores.mean(axis=0)                 # media sulle 9 immagini, per ogni C
best_c_index = int(np.argmax(mean_ap))        # a parità vince il primo, cioè il C più piccolo
ax.semilogx(C_VALUES, fold_scores, color="gray")    # una curva grigia per immagine
ax.semilogx(C_VALUES, mean_ap, marker="o")          # la media
# cella 23: per ogni immagine tenuta fuori, la curva precisione-recall al C scelto
ax.step(recall, precision, where="post"); ax.axhline(targets.mean(), linestyle="--")</pre>
<ul>
<li>Il grafico della cella 22 ha C sull'asse x (logaritmico) e l'AP sulla y: 9 curve grigie, una per immagine, e la media. Con C molto piccolo i pesi sono quasi zero, ma l'AP dipende solo dall'ordinamento, che può restare buono anche con pesi minuscoli; con C grande si rischia di adattarsi troppo alle 8 immagini di training.</li>
<li><code>np.argmax</code> restituisce il <b>primo</b> massimo: siccome i C sono in ordine crescente, a parità si sceglie la regolarizzazione <b>più forte</b>, il modello più semplice.</li>
<li>La cella 23 disegna una curva precisione-recall per ogni immagine tenuta fuori, con l'AP nella legenda e una linea tratteggiata alla <b>prevalenza</b> (la frazione di patch di primo piano di quell'immagine): è la precisione di un classificatore a caso, la base da battere.</li>
<li>Il commento finale è onesto: C è stato scelto <b>su questi stessi fold</b>, quindi queste AP sono leggermente ottimiste. Per una stima non distorta servirebbe un insieme di test annotato separato o una <b>cross-validazione annidata</b> (scegliere C dentro ogni fold, sulle 8 immagini di training).</li>
</ul>
<div class="box w"><b>Attenzione: un C piccolo può dare una maschera vuota</b><p>Un'osservazione nostra, da verificare quando si esegue: l'AP ignora la calibrazione, la soglia 0,5 della scheda 25 no. Con regolarizzazione fortissima (C = 10⁻⁶ o 10⁻⁷) le probabilità si schiacciano vicino alla prevalenza, intorno a 0,2–0,3, e possono restare <b>tutte sotto 0,5</b> pur ordinando bene le patch: AP alta, maschera finale vuota. Se succede, conviene scegliere C con una metrica che dipende dalla soglia (per esempio l'IoU della maschera a 0,5) o scegliere la soglia sulla validazione.</p></div>
""", printed='NOTEBOOK dinov3_foreground_segmentation_lab.ipynb · celle 22–23')

s(25, 'Refit e segmentazione di una foto nuova', """
<pre>classifier = make_probe(best_c).fit(X, y)                   # tutte e 9 le immagini
demo_features, grid_shape, _ = extract_patch_features(demo_image)
foreground_score = classifier.predict_proba(demo_features)[:, 1].reshape(grid_shape)
smoothed_score = median_filter(foreground_score, size=3, mode="nearest")   # 3×3 sulla griglia di patch
pixel_score = F.interpolate(grid[None, None], size=(H, W), mode="bilinear")[0, 0]
predicted_mask = pixel_score &gt;= 0.5</pre>
<ul>
<li><b>Refit</b>: scelto C, si addestra un classificatore nuovo su tutte le 4702 patch delle 9 immagini: 384 pesi + 1 bias. Il suo punteggio sul training non si riporta come prestazione.</li>
<li><b>Demo</b>: una foto nuova (un gatto tigrato a pelo lungo sdraiato su una coperta a righe blu e bianche, davanti a un muro chiaro; 1600×1200 → 448×336 → griglia 21×28). Si applica il probe a <b>tutte</b> le patch, anche a quelle di bordo che in training si ignoravano.</li>
<li><b>Filtro mediano</b> 3×3 sulla griglia di patch (non sui pixel): toglie le patch isolate che il probe sbaglia, come il mediano toglie il rumore sale e pepe (<a href="#L5">L5</a>), conservando i bordi meglio di una media.</li>
<li><b>Upsampling bilineare</b> della griglia alla dimensione della foto, poi soglia 0,5 e overlay rosso semitrasparente. L'interpolazione rende i bordi morbidi, ma non recupera i dettagli più piccoli di una patch.</li>
<li>La foto non ha una maschera vera: il risultato è <b>qualitativo</b>, non una misura (né AP né IoU). Con <code>CUSTOM_IMAGE_PATH</code> si può provare una propria foto.</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Elencare i limiti della pipeline: risoluzione di una patch (16 pixel dell'immagine ridimensionata), bordi esclusi dal training, «primo piano» definito dalle 9 immagini (oggetti al centro, a fuoco), soglia 0,5 fissata a priori. E i vantaggi: nessun addestramento della rete, pochi secondi su CPU, 9 immagini annotate.</p></div>
<div class="box x"><b>Verso le tecniche vere</b><p>Il notebook ufficiale di DINOv3 usa lo stesso schema. Per una segmentazione più fine si usano decoder addestrati sopra le feature congelate (per esempio la testa lineare o DPT delle valutazioni di DINOv2/DINOv3), feature a risoluzione più alta (immagine più grande, quindi più patch), oppure l'upsampling guidato dall'immagine.</p></div>
""", img='img/s25.jpg', printed='NOTEBOOK dinov3_foreground_segmentation_lab.ipynb · celle 24–28')
