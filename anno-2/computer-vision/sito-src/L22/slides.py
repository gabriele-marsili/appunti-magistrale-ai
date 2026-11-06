VB = 'https://visionbook.mit.edu/'
def L(slug, txt): return f'<a href="{VB}{slug}" target="_blank">{txt}</a>'
LK = {
 '{C30}': L('representation_learning.html', 'cap. 30'),
 '{C31}': L('perceptual_organization.html', 'cap. 31'),
 '{C33}': L('generative_modeling_and_rep_learning.html', 'cap. 33'),
 '{C37}': L('transfer_learning.html', 'cap. 37'),
 '{C26}': L('transformers.html', 'cap. 26'),
 '{C43}': L('3d_learning.html', 'cap. 43'),
 '{C12}': L('neural_nets.html', 'cap. 12'),
 '{C36}': L('data_augmentation.html', 'cap. 36'),
}
def P(n): return f' <em>· pag. {n}/59</em>'
def R(t):
    for k, v in LK.items(): t = t.replace(k, v)
    return t

# ===================== INTRODUZIONE E VALUTAZIONE =====================

s(1, "Self-Supervised Learning and Vision Foundation Models: copertina", R("""
<p>Lezione del 5 novembre 2026, tenuta da <b>Giacomo Cignoni</b> (dottorando, non dal prof. Carta). È la seconda parte del self-supervised learning (SSL): la <a href="#L21">L21</a> ha introdotto pretraining, pretext task storici, apprendimento contrastivo (InfoNCE, SimCLR) e SimSiam; qui si vedono le altre famiglie di metodi e i modelli che oggi si usano davvero come backbone (DINOv2, DINOv3).</p>
<p>Due parti:</p>
<ol>
<li><b>Self-Supervised Learning</b> (slide 2–40): come si valuta una rappresentazione, metodi a due viste con teacher (BYOL, MoCo), metodi che regolano le statistiche delle feature (Barlow Twins, VICReg), metodi di ricostruzione (autoencoder, SimMIM, MAE, BEiT) e il confronto fra le famiglie.</li>
<li><b>Vision Foundation Models</b> (slide 41–59): DINO, DINOv2 (dati curati, distillazione), Depth Anything, DINOv3 (Gram anchoring), JEPA.</li>
</ol>
<p>Il PDF ha 59 pagine e il footer stampa «n / 59» con n = pagina del PDF, copertina compresa. Le divisorie di parte (pag. 2 e 41) non hanno numero; quelle di sezione (pag. 10 e 28) sì.</p>
<div class="box k"><b>Il filo della lezione in una frase</b><p>Ogni metodo SSL deve risolvere lo stesso problema: <b>far coincidere due cose</b> (due viste, o una vista e il suo pezzo mancante) <b>senza che la rete trovi la soluzione banale</b> (uscita costante, il <i>collasso</i>). I metodi si distinguono per il modo in cui evitano il collasso: negativi (SimCLR, MoCo), asimmetria e teacher lento (BYOL, SimSiam, DINO), vincoli sulle statistiche (Barlow Twins, VICReg), oppure un bersaglio che non può collassare perché è l'immagine stessa (MAE, SimMIM, BEiT).</p></div>
"""), sec=("l22-intro", "Introduzione e valutazione", "slide 1–9"), printed=P(1))

s(2, "Part 1 · Self-Supervised Learning", R("""
<p>Divisoria della prima parte: <i>how to learn without labels</i>, come imparare senza etichette.</p>
"""), kind='div', printed='')

s(3, "Definition", R("""
<p><b>Self-Supervised Learning (SSL)</b>: paradigma di addestramento che insegna a una rete a estrarre <b>rappresentazioni</b> utili da dati <b>non etichettati</b>, ricavando il segnale di apprendimento dalla <b>struttura dei dati stessi</b>.</p>
<ul>
<li>Il prodotto finale non è una predizione ma un <b>encoder</b>: una funzione f che trasforma un'immagine in un vettore (o in una griglia di vettori, uno per patch).</li>
<li>Il «segnale dalla struttura dei dati»: due ritagli della stessa foto devono avere la stessa descrizione; una parte nascosta dell'immagine si deve poter indovinare dal resto.</li>
</ul>
<div class="box b"><b>Dal libro · {C30}, § 30.6 Self-Supervised Learning</b>
<p>Il libro lo scrive come un problema di predizione in cui sia l'ingresso sia il bersaglio sono <b>funzioni dello stesso dato</b> X: si addestra a predire V<sub>2</sub>(X) da V<sub>1</sub>(X). Esempi: V<sub>1</sub> = metà sinistra, V<sub>2</sub> = metà destra; V<sub>1</sub> = fotogrammi passati, V<sub>2</sub> = fotogramma futuro; V<sub>1</sub> = canale di luminanza, V<sub>2</sub> = colore. Il libro insiste sul nome: non è «supervisionato» perché nessuno fornisce coppie ingresso-uscita del compito che interessa davvero; la supervisione è un <b>pretext task</b> che si spera produca buone rappresentazioni (§ 30.5).</p></div>
"""), printed=P(3))

s(4, "Unsupervised vs Self-Supervised learning", R("""
<p>Tabella di confronto fra l'apprendimento <b>non supervisionato classico</b> e il <b>self-supervised</b>:</p>
<table>
<tr><th></th><th>Non supervisionato classico</th><th>Self-supervised</th></tr>
<tr><td>Obiettivo</td><td>scoprire ed esporre la struttura dei dati</td><td>addestrare una rete che impari rappresentazioni <b>trasferibili</b></td></tr>
<tr><td>Segnale</td><td>criteri sulla struttura: distanze, varianza, verosimiglianza</td><td>bersagli di predizione generati dai dati</td></tr>
<tr><td>Uscita tipica</td><td>cluster, componenti, mappe, stime di densità</td><td>un encoder preaddestrato per compiti a valle</td></tr>
<tr><td>Esempi</td><td>k-means, PCA, SOM, DBSCAN</td><td>i metodi di questa lezione</td></tr>
</table>
<p>In sintesi: i metodi classici <b>organizzano</b> i dati; quelli self-supervised usano la struttura dei dati per <b>addestrare una rete riutilizzabile</b>.</p>
<div class="box b"><b>Dal libro · {C30}, § 30.3 e Tab. 30.1</b>
<p>Il libro non separa le due cose così nettamente: mette tutto sotto «representation learning» e classifica i metodi per il <b>principio</b> che seguono. <b>Compressione</b>: autoencoder (togliere la ridondanza), contrastivo (invarianza alle trasformazioni di vista), clustering (quantizzare in categorie). <b>Predizione</b>: futuro, imputazione (dati mancanti), pretext task astratti. Nota che anche PCA e k-means compaiono (§ 30.4, 30.9): un autoencoder lineare con perdita L2 impara lo stesso sottospazio della PCA. Le famiglie di questa lezione si collocano così: BYOL, MoCo, Barlow Twins, VICReg, DINO = compressione per invarianza; SimMIM, MAE, BEiT, JEPA = imputazione.</p></div>
"""), printed=P(4))

s(5, "Why self-supervised learning?", R("""
<p>Schema: <b>preaddestrare</b> una rete su dati non etichettati, poi <b>adattarla</b> ai compiti a valle (downstream).</p>
<p>Il pretraining dà:</p>
<ul>
<li><b>rappresentazioni visive riutilizzabili</b>;</li>
<li>una buona <b>inizializzazione</b>, quindi convergenza più rapida e migliore;</li>
<li>meno bisogno di dati ed etichette per il compito finale.</li>
</ul>
<p>Le rappresentazioni sono utili anche <b>direttamente</b>: nel <b>retrieval</b> di immagini basta confrontare le feature (distanza o similarità coseno) per trovare immagini simili, senza addestrare nulla.</p>
<div class="box b"><b>Dal libro · {C37}, § 37.2 Problem Setting</b>
<p>Il transfer learning ha due fasi: <b>pretraining</b> (acquisire conoscenza) e <b>adaptation</b> (usarla per un compito nuovo). Il libro nota che il pretraining può essere un addestramento normale chiamato così «a posteriori», oppure un algoritmo pensato apposta come riscaldamento: i metodi di representation learning del cap. 30, e quindi tutti quelli di questa lezione, sono del secondo tipo.</p></div>
"""), printed=P(5))

s(6, "Stage 1: self-supervised pretraining", R("""
<p><b>Figura:</b> una griglia di immagini non etichettate entra in una rete (trapezio arancione, con il simbolo di addestramento); la rete produce <i>representations</i> e su queste si calcola la <b>SSL loss</b>.</p>
<ul>
<li>Si addestra un encoder su <b>immagini senza etichette</b> con un obiettivo self-supervised.</li>
<li>La rete impara rappresentazioni <b>generali</b>, non legate a un compito (<i>task-agnostic</i>).</li>
<li>La rete si conserva per riusarla dopo.</li>
</ul>
"""), printed=P(6))

s(7, "Stage 2: downstream tasks", R("""
<p><b>Figura:</b> un'immagine stradale entra nella rete preaddestrata (simboli «frozen» con il fiocco di neve, oppure «trained»); sopra le rappresentazioni c'è una <b>head</b> addestrata che produce una segmentazione, su cui si calcola la loss del compito.</p>
<ul>
<li>Si riusa l'encoder e si addestra una <b>head specifica del compito</b> con dati etichettati.</li>
<li>L'encoder dà le rappresentazioni, la head le converte in predizioni.</li>
<li>L'encoder si può tenere <b>congelato</b> (frozen) oppure <b>riaddestrare</b> (fine-tuning).</li>
<li>Compiti a valle: classificazione, segmentazione, profondità (<a href="#L17">L17</a>, <a href="#L19">L19</a>).</li>
</ul>
<div class="box b"><b>Dal libro · {C37}, § 37.3 Finetuning e § 37.3.1</b>
<ul>
<li><b>Finetuning</b> = inizializzare il nuovo modello con i parametri preaddestrati e continuare ad addestrare. Se l'uscita cambia dimensione (da 2 a 3 classi) si <b>taglia l'ultimo strato</b> e se ne mette uno nuovo inizializzato a caso; lo stesso si può fare con il primo strato se cambia l'ingresso.</li>
<li>§ 37.3.1: non serve riaddestrare tutto. L'esempio del libro è un rilevatore di auto fatto di moduli: un <b>featurizer congelato</b> (proprio DINO, che il libro richiama dal § 31.3.2), un estimatore di profondità e un classificatore denso preaddestrati e poi riaddestrati, un detector addestrato da zero. È esattamente lo schema «backbone congelato + head» delle slide 7 e 42. Si congela per non far <b>dimenticare</b> al modulo ciò che sa.</li>
<li>Anche dentro uno strato si può aggiornare solo un sottospazio dei pesi (aggiornamento a basso rango, l'idea di LoRA) per risparmiare memoria.</li>
</ul></div>
"""), printed=P(7))

s(8, "How to evaluate representation quality?", R("""
<p>Tre protocolli standard, in ordine di quanto si addestra:</p>
<table>
<tr><th>Protocollo</th><th>Cosa si addestra</th><th>Criterio</th></tr>
<tr><td><b>k-NN</b></td><td>niente</td><td>ogni esempio di test prende l'etichetta di maggioranza dei k vicini più prossimi fra le rappresentazioni del training set del compito</td></tr>
<tr><td><b>Linear probe</b></td><td>solo una head lineare</td><td>encoder congelato, si addestra un classificatore lineare sulle feature</td></tr>
<tr><td><b>Fine-tuning</b></td><td>head e backbone</td><td>si riaddestra tutto sui dati del compito</td></tr>
</table>
<ul>
<li>k-NN e linear probe misurano la rappresentazione <b>così com'è</b>: il k-NN chiede che immagini della stessa classe siano <b>vicine</b>, il linear probe che le classi siano <b>separabili linearmente</b> (<a href="#L15">L15</a>: embedding e separabilità lineare).</li>
<li>Il fine-tuning misura quanto la rete è un buon <b>punto di partenza</b>: può dare buoni risultati anche con feature non linearmente separabili. Per questo i ranking fra metodi cambiano a seconda del protocollo (slide 40).</li>
</ul>
<div class="box b"><b>Dal libro · {C37}, § 37.3.2 Heads and Probes, e {C30}, § 30.4.1</b>
<ul>
<li>Un modulo di lettura lineare è un <b>linear probe</b>: pochi parametri, ottimizzazione convessa (spesso con soluzione in forma chiusa). Serve due scopi: riusare la rete per un compito nuovo e <b>sondare</b> cosa sa uno strato: se da quella feature map si classifica linearmente un attributo, lo strato «conosce» quell'attributo.</li>
<li>Nel § 30.4.1 il libro valuta un autoencoder proprio con un <b>1-NN</b> strato per strato, su un dataset giocattolo di cerchi, triangoli e quadrati colorati: il <b>colore</b> si classifica meglio nei pixel grezzi (strato 0) e peggiora andando in profondità; la <b>forma</b> fa il contrario. Morale del libro: non esiste una rappresentazione migliore in assoluto; ognuna rende facili alcune cose e difficili altre.</li>
</ul></div>
<div class="box x"><b>Approfondimento</b><p>Il k-NN di DINO (slide 46) non è un voto semplice: usa k = 20 vicini con similarità coseno e voti pesati con un esponenziale della similarità. Il dettaglio non serve all'esame, ma spiega perché nelle tabelle degli articoli il k-NN è sempre qualche punto sotto il linear probe (per DINO ViT-S/16: 74,5% contro 77,0% su ImageNet).</p></div>
"""), printed=P(8))

s(9, "Designing a useful pretext task", R("""
<p>Un compito con bersagli generati automaticamente deve comunque insegnare <b>rappresentazioni visive utili</b>. Tre criteri:</p>
<ul>
<li><b>Difficoltà giusta</b>: un compito facile insegna poco; un compito ambiguo può essere impossibile.</li>
<li><b>Evitare le scorciatoie</b> (shortcut): la rete può sfruttare bordi, texture o artefatti della fotocamera invece di capire gli oggetti (<a href="#L14">L14</a>; gli esempi storici sono in <a href="#L21">L21</a>: nella posizione relativa delle patch la rete sfruttava l'aberrazione cromatica).</li>
<li><b>Favorire il trasferimento</b>: risolvere il pretext task deve aiutare altri compiti visivi.</li>
</ul>
<p>Messaggio chiave: <b>una loss bassa sul pretext task non garantisce buone rappresentazioni</b> a valle. Il caso estremo è il collasso (slide 12): loss zero, rappresentazione inutile.</p>
<div class="box b"><b>Dal libro · {C30}, § 30.5.1, 30.7 e 30.8</b>
<p>Il libro mostra il lato positivo: con quasi qualunque pretext task ragionevole (classificazione di scene, colorizzazione, inpainting) negli strati nascosti di una CNN <b>emergono rilevatori di oggetti</b> (fig. 30.7 e 30.9: neuroni che si attivano su scale o barche). L'ipotesi del libro è che gli «oggetti» siano una struttura utile del mondo, a cui arriva qualunque sistema che debba capirlo. I pretext task astratti (§ 30.8: predire la rotazione di 90°, la posizione relativa di due patch) funzionano perché per risolverli servono regolarità semantiche e geometriche (le nuvole stanno in alto, il tronco sotto i rami). DINO (slide 46) è la versione moderna dello stesso fenomeno.</p></div>
"""), printed=P(9))

# ===================== INSTANCE DISCRIMINATION E TEACHER-STUDENT =====================

s(10, "Instance Discrimination Methods", R("""
<p>Divisoria di sezione (Part 1): metodi di <b>instance discrimination</b>, cioè metodi che trattano ogni immagine come una «classe» a sé e imparano a riconoscere due viste della stessa immagine. Riprende la <a href="#L21">L21</a> (SimCLR, SimSiam) e aggiunge i metodi con teacher.</p>
"""), kind='div', sec=("l22-istanze", "Instance discrimination e teacher-student", "slide 10–22"), printed=P(10))

s(11, "Instance discrimination", R("""
<p><b>Figura:</b> due ritagli diversi della stessa foto di un gatto (uno con colori alterati) entrano nella <b>stessa</b> rete; le due uscite sono collegate da una freccia «enforce similarity». Dietro ogni ritaglio si intravedono altre immagini del batch.</p>
<ul>
<li>Si generano due <b>viste</b> della stessa immagine con augmentation casuali t<sub>1</sub>, t<sub>2</sub>: <span class="f">v<sub>1</sub> = t<sub>1</sub>(x),  v<sub>2</sub> = t<sub>2</sub>(x)</span></li>
<li>Si codificano con la <b>stessa rete</b> f: <span class="f">z<sub>1</sub> = f(v<sub>1</sub>),  z<sub>2</sub> = f(v<sub>2</sub>)</span></li>
<li>Si spinge la rete a dare rappresentazioni <b>simili</b> alle due viste nonostante il cambio di aspetto.</li>
</ul>
<p>Le augmentation decidono a cosa la rappresentazione diventa <b>invariante</b>: ritaglio, ribaltamento, variazioni di colore, sfocatura (la tabella delle augmentation di SimCLR è in <a href="#L21">L21</a>).</p>
<div class="box b"><b>Dal libro · {C30}, § 30.10 e 30.10.2</b>
<p>Il libro chiama questo termine <b>alignment loss</b>, ‖f(T(x)) − f(x)‖², e lo presenta come un modo di ottenere invarianza <b>attraverso l'obiettivo</b> invece che attraverso l'architettura (come fa la convoluzione con il pooling per le traslazioni). L'esperimento del § 30.10.2 mostra quanto contano le trasformazioni: con soli ritagli l'embedding raggruppa per <b>colore</b> (il colore è l'indizio più facile e il ritaglio lo conserva); aggiungendo variazioni casuali di tinta, luminosità e saturazione diventa invariante al colore e raggruppa per <b>forma</b>.</p></div>
"""), printed=P(11))

s(12, "Agreement alone admits a trivial solution", R("""
<p>Se la loss è solo l'accordo fra le due viste,</p>
<span class="f">L<sub>agree</sub> = ‖f(v<sub>1</sub>) − f(v<sub>2</sub>)‖²</span>
<p>esistono soluzioni banali con loss nulla. Due forme di <b>collasso</b>:</p>
<ul>
<li><b>Collasso completo</b>: f(x) = c per ogni x. Tutte le immagini ricevono lo stesso vettore costante; la loss è 0 ma la rappresentazione non distingue nulla.</li>
<li><b>Collasso dimensionale</b>: rank(Cov(z)) ≪ d. Le feature variano fra le immagini, ma occupano solo un sottospazio di poche dimensioni dello spazio a d dimensioni disponibile: molte coordinate sono costanti o copie (combinazioni lineari) di altre.</li>
</ul>
<div class="box k"><b>Da saper fare: riconoscere i due collassi dalla matrice di covarianza</b>
<p>Prendi un batch di B embedding z<sub>b</sub> ∈ ℝ<sup>d</sup> e la loro covarianza Cov(z) (d × d).</p>
<ul>
<li>Collasso completo: tutti gli z<sub>b</sub> uguali, Cov(z) = 0, rango 0.</li>
<li>Collasso dimensionale, esempio con d = 3: z<sub>b</sub> = (a<sub>b</sub>, 2a<sub>b</sub>, 0) con a<sub>b</sub> variabile. Le immagini sono distinte, ma Cov(z) = Var(a) · [[1, 2, 0], [2, 4, 0], [0, 0, 0]], che ha rango 1: una sola direzione su tre è usata.</li>
</ul>
<p>Diagnosi pratica: calcola gli autovalori di Cov(z) sugli embedding di un set di validazione e guarda quanti sono lontani da zero (lo spettro «crolla» dopo pochi valori). È il criterio usato da Jing et al. (2022), che hanno mostrato che anche i metodi contrastivi soffrono di collasso dimensionale.</p></div>
<div class="box b"><b>Dal libro · {C30}, § 30.10</b>
<p>«Trivial alignment can be achieved when there is representational collapse»: il libro presenta il collasso proprio così, come il difetto dell'alignment loss, e propone come rimedio i <b>negativi</b> (contrastivo). In § 30.3.1 dice la stessa cosa in generale: una penalità di compressione da sola porta a una soluzione degenere (la rappresentazione che non contiene nulla) e va sempre accoppiata a un termine che preservi informazione. Questa lezione mostra gli altri rimedi, senza negativi.</p></div>
"""), printed=P(12))

s(13, "Contrastive and siamese methods: recap", R("""
<p>Ripasso della <a href="#L21">L21</a>:</p>
<table>
<tr><th>Metodo</th><th>Segnale</th><th>Meccanismo chiave</th></tr>
<tr><td>SimCLR</td><td>avvicinare le viste positive, allontanare i negativi</td><td>loss contrastiva (InfoNCE / NT-Xent)</td></tr>
<tr><td>SimSiam</td><td>predire l'altra vista</td><td>predictor + stop-gradient</td></tr>
</table>
<p>Oggi: come <b>teacher</b> e <b>regolarizzatori espliciti</b> rendono utili i bersagli senza etichette.</p>
<p>Il footer della slide dice «SimCLR · MoCo · SimSiam», ma MoCo non è nella tabella: arriva a slide 21.</p>
<div class="box k"><b>Da saper dire</b><p>SimCLR evita il collasso perché la loss <b>penalizza esplicitamente</b> la soluzione costante: se tutte le immagini hanno lo stesso embedding, il positivo non si distingue dai negativi e l'InfoNCE vale log(N) invece di 0. SimSiam non ha negativi: il collasso è una soluzione con loss minima, ma lo stop-gradient e il predictor cambiano la <b>dinamica</b> dell'ottimizzazione in modo che la rete non ci arrivi (Szeliski § 5.4.7). BYOL sta in mezzo: è SimSiam con in più un teacher a media mobile.</p></div>
"""), printed=P(13))

s(14, "BYOL: learning from another network", R("""
<p><b>BYOL</b> = <i>Bootstrap Your Own Latent</i> (Grill et al., NeurIPS 2020).</p>
<p><b>Figura:</b> due viste dello stesso gatto entrano in due reti: a sinistra la rete <b>aggiornata</b> (arancione, lo student), a destra la rete <b>EMA</b> (grigia, il teacher, con una lumaca: si muove lentamente). Una freccia tratteggiata «EMA update» va dallo student al teacher; sopra, «enforce similarity» fra le uscite e uno <b>stop gradient</b> sul ramo del teacher.</p>
<ul>
<li>Si creano due viste della stessa immagine.</li>
<li>Si addestra uno <b>student</b> a predire l'uscita di un <b>teacher</b>.</li>
<li>Il teacher si aggiorna <b>lentamente</b> a partire dallo student.</li>
</ul>
<p>Si impara predicendo le feature di un'altra vista, <b>senza coppie negative</b>.</p>
<div class="box b"><b>Dal libro · Szeliski 2a ed., § 5.4.7 Self-supervised learning</b>
<p>Szeliski lo presenta come una scoperta controintuitiva: senza negativi la rappresentazione potrebbe collassare su una costante, eppure BYOL funziona con tre ingredienti, un <b>momentum encoder</b>, un <b>MLP predictor</b> in più sul ramo online e lo <b>stop-gradient</b> sul ramo target, e così toglie i negativi da MoCo v2. SimSiam mostra poi che basta lo stop-gradient (con il predictor), senza momentum encoder. Szeliski cita anche Tian, Chen e Ganguli (2021), che spiegano perché funziona e mostrano che i pesi del predictor si possono addirittura fissare dalle statistiche delle feature.</p></div>
"""), printed=P(14))

s(15, "Student and teacher: different roles", R("""
<table>
<tr><th>Ruolo</th><th>Student: rete online</th><th>Teacher: rete target</th></tr>
<tr><td>Scopo</td><td>predire le feature dell'altra vista</td><td>fornire le feature bersaglio</td></tr>
<tr><td>Regola di apprendimento</td><td>backpropagation e ottimizzatore</td><td>media mobile dei pesi dello student</td></tr>
<tr><td>Uscita</td><td>una predizione da migliorare</td><td>un bersaglio per il passo corrente</td></tr>
</table>
<ul>
<li>Il teacher parte come <b>copia dello student</b>.</li>
<li>Il teacher fornisce supervisione senza etichette umane, e i suoi bersagli <b>evolvono</b> durante l'addestramento: è un bersaglio mobile che migliora insieme allo student (da qui <i>bootstrap</i>).</li>
</ul>
<div class="box b"><b>Dal libro · {C37}, § 37.4 Learning from a Teacher</b>
<p>Il libro descrive il teacher come un modello già addestrato che lo student imita, sulle uscite o sulle attivazioni intermedie; la supervisione classica è il caso di un teacher «pigro» che dà solo le risposte. In BYOL (e DINO) la novità è che il teacher <b>non è addestrato prima</b>: è una media dello student stesso. Si parla per questo di <b>self-distillation</b>. Nella distillazione di DINOv2 (slide 49) il teacher torna invece fisso, come nel libro.</p></div>
"""), printed=P(15))

s(16, "BYOL loss", R("""
<span class="f">L = ‖s − stop_grad(t)‖²</span>
<p>s = predizione dello student, t = bersaglio del teacher. Le derivate:</p>
<span class="f">∂L/∂s = 2(s − t),   ∂L/∂t = 0</span>
<ul>
<li>Il teacher calcola il bersaglio dall'<b>altra vista</b>.</li>
<li>L'ottimizzatore aggiorna <b>solo lo student</b> con questa loss.</li>
<li>Lo <b>stop-gradient</b> blocca la backpropagation nel teacher: nel grafo di calcolo t è trattato come una costante.</li>
</ul>
<p>La domanda finale della slide ha perso una parola: si legge «How can change over time…», va letto «How can <b>the teacher</b> change over time without receiving gradients from the prediction loss?». Risposta: slide 17, con la media mobile.</p>
<div class="box k"><b>Da saper fare: perché lo stop-gradient impedisce di «barare»</b>
<p>Esempio giocattolo lineare a una dimensione. Ingresso x con E[x²] = 1, seconda vista x' = x + n con rumore indipendente di varianza σ<sub>n</sub>², quindi E[x x'] = 1 e E[x'²] = 1 + σ<sub>n</sub>². Student s = w x, teacher t = ξ x'.</p>
<ul>
<li><b>Senza stop-gradient e pesi condivisi</b> (w = ξ): L(w) = E[(w x − w x')²] = w² σ<sub>n</sub>². Il minimo è w = 0: la discesa del gradiente porta dritta al <b>collasso</b>, perché la rete riduce la loss <b>rimpicciolendo entrambe le uscite</b>.</li>
<li><b>Con stop-gradient</b>: ∂L/∂w = 2E[(w x − ξ x') x] = 2(w − ξ). Il gradiente spinge w verso ξ, cioè lo student verso il bersaglio, ma <b>nessun termine spinge verso 0</b>: con w = ξ il gradiente è nullo per qualunque valore, non solo per 0.</li>
</ul>
<p>Il collasso resta una soluzione possibile, ma non è più ciò verso cui spinge il gradiente. Il caso lineare non dimostra nulla per le reti profonde: serve a vedere che lo stop-gradient toglie la scorciatoia «muovo anche il bersaglio».</p></div>
"""), printed=P(16))

s(17, "The teacher is a moving average", R("""
<p>Aggiornamento del teacher con una <b>media mobile esponenziale</b> (EMA) dei pesi dello student:</p>
<span class="f">ξ ← τ ξ + (1 − τ) θ</span>
<p>θ = pesi dello student, ξ = pesi del teacher, τ = momentum (vicino a 1).</p>
<p><b>Esempio con un peso</b>: teacher 2,00, student aggiornato 3,00, τ = 0,99 → ξ<sub>new</sub> = 0,99 · 2 + 0,01 · 3 = 1,98 + 0,03 = <b>2,01</b>. Il conto della slide è giusto.</p>
<p>Perché la media:</p>
<ul>
<li>leviga gli aggiornamenti rapidi dello student;</li>
<li>fa cambiare i bersagli <b>gradualmente</b>;</li>
<li>conserva informazione dagli student precedenti.</li>
</ul>
<p>Lo student impara con i gradienti; il teacher lo segue attraverso l'EMA.</p>
<div class="box k"><b>Da saper fare: EMA a mano su più passi</b>
<p>Teacher iniziale ξ<sub>0</sub> = 2, student fermo a θ = 3, τ = 0,99. Ogni passo riduce la distanza dal valore dello student di un fattore τ:</p>
<span class="f">ξ<sub>k</sub> = θ − (θ − ξ<sub>0</sub>) τ<sup>k</sup> = 3 − 0,99<sup>k</sup></span>
<ul>
<li>k = 1: 2,01; k = 10: 2,096; k = 69: 2,50 (metà strada); k = 100: 2,634; k = 300: 2,951.</li>
<li><b>Tempo di dimezzamento</b>: k<sub>½</sub> = ln 0,5 / ln τ ≈ 69 passi con τ = 0,99, ≈ 173 con τ = 0,996 (il valore iniziale di BYOL e DINO).</li>
<li>Regola mnemonica: l'EMA «ricorda» circa gli ultimi <b>1/(1 − τ)</b> passi (100 con τ = 0,99, 250 con 0,996). Espandendo la ricorsione, ξ<sub>k</sub> = (1 − τ) ∑<sub>j</sub> τ<sup>j</sup> θ<sub>k−j</sub> + τ<sup>k</sup>ξ<sub>0</sub>: pesi che decadono geometricamente sugli student passati.</li>
</ul>
<p>Con τ = 1 il teacher resta fermo alla copia iniziale (casuale!); con τ = 0 è una copia dello student e si torna a SimSiam senza teacher separato. In BYOL τ parte da 0,996 e sale fino a 1 con un andamento a coseno: alla fine dell'addestramento il teacher quasi si ferma.</p></div>
<div class="box x"><b>Approfondimento</b><p>L'EMA dei pesi è la stessa formula del momentum dell'SGD e della media mobile della BatchNorm (<a href="#L15">L15</a>, <a href="#L16">L16</a>), applicata qui ai parametri. Si usa anche fuori dall'SSL (EMA dei pesi in fase di valutazione) perché la media di modelli vicini nello spazio dei pesi generalizza meglio dell'ultimo iterato; in DINO il teacher è infatti <b>più accurato</b> dello student per tutto l'addestramento.</p></div>
"""), printed=P(17))

s(18, "How BYOL addresses collapse", R("""
<p>L'accordo fra due viste da solo ammette f(x) = c per ogni x. BYOL cambia la <b>dinamica</b> dell'apprendimento con tre ingredienti:</p>
<ul>
<li><b>Predictor head solo nello student</b>: i due rami fanno calcoli diversi (asimmetria).</li>
<li><b>Stop-gradient</b>: il teacher non può adattarsi per ridurre la loss corrente.</li>
<li><b>Teacher aggiornato lentamente</b>: i bersagli seguono la <b>storia</b> dello student, non il suo gradiente attuale.</li>
</ul>
<p>Questa ricetta completa evita il collasso <b>empiricamente</b>.</p>
<div class="box k"><b>Da saper fare: perché BYOL non collassa (ragionamento da orale)</b>
<ol>
<li><b>Il collasso è ancora un minimo</b>: se student e teacher danno lo stesso vettore costante, la loss normalizzata vale 0. Quindi BYOL non lo esclude con la loss, come fa l'InfoNCE: lo rende <b>irraggiungibile</b> per la dinamica.</li>
<li><b>Stop-gradient</b>: lo student non può ridurre la loss spostando il bersaglio (conto della slide 16). Il bersaglio è, per il passo corrente, una costante.</li>
<li><b>Predictor</b>: l'ottimo del predictor è il valore atteso del bersaglio data la vista dello student, q*(z) ≈ E[z' | z]. Lo student viene quindi spinto verso feature da cui si <b>predice</b> bene l'altra vista: un'uscita costante predice bene solo un bersaglio costante, ma il teacher (copia lenta di uno student che ancora varia) non è costante. Gli articoli di BYOL e SimSiam mostrano che togliendo il predictor il metodo collassa.</li>
<li><b>EMA</b>: il bersaglio si muove lentamente, quindi lo student insegue un obiettivo quasi fermo e informativo invece di «trascinarlo» con sé verso il collasso. In SimSiam l'EMA si toglie (τ = 0) e funziona lo stesso, ma BYOL con EMA è più stabile.</li>
</ol>
<p>La parola chiave è <b>«empiricamente»</b>: non c'è una garanzia teorica generale; l'analisi più citata (Tian, Chen e Ganguli 2021) studia il caso lineare e mostra il ruolo di predictor ed EMA.</p></div>
"""), printed=P(18))

s(19, "BYOL: the complete architecture", R("""
<p><b>Figura (dall'articolo):</b> l'immagine x produce due viste v = t(x) e v' = t'(x). Il ramo superiore (<b>online</b>, blu) applica encoder f<sub>θ</sub> → rappresentazione y<sub>θ</sub>, projector g<sub>θ</sub> → proiezione z<sub>θ</sub>, predictor q<sub>θ</sub> → predizione q<sub>θ</sub>(z<sub>θ</sub>). Il ramo inferiore (<b>target</b>, rosa) applica f<sub>ξ</sub> → y'<sub>ξ</sub>, g<sub>ξ</sub> → z'<sub>ξ</sub>, poi uno stop-gradient «sg(z'<sub>ξ</sub>)». La loss confronta predizione e target.</p>
<ul>
<li><b>Encoder f</b>: estrae la rappresentazione y (per esempio l'uscita di una ResNet-50 dopo il pooling, 2048 dimensioni).</li>
<li><b>Projector g</b>: MLP che porta y nello spazio dove si calcola la loss SSL (nell'articolo 256 dimensioni).</li>
<li><b>Predictor q</b>: MLP con la stessa forma del projector; predice la proiezione del teacher; c'è <b>solo nello student</b>.</li>
</ul>
<p><b>Dopo il pretraining</b>: si tiene l'encoder dello student f<sub>θ</sub>; projector e predictor si buttano.</p>
<div class="box x"><b>Approfondimento: perché si butta il projector</b><p>Come in SimCLR (<a href="#L21">L21</a>), lo spazio della loss è costretto a essere invariante alle augmentation e quindi «perde» informazione (colore, orientazione) che a valle può servire. La rappresentazione y prima del projector ne conserva di più e trasferisce meglio. Il projector fa da cuscinetto fra l'obiettivo SSL e la rappresentazione da riusare.</p></div>
"""), printed=P(19))

s(20, "BYOL: do not forget normalization!", R("""
<p>Per due viste v e v' della stessa immagine:</p>
<span class="f">p<sub>θ</sub> = q<sub>θ</sub>(g<sub>θ</sub>(f<sub>θ</sub>(v))),   z'<sub>ξ</sub> = g<sub>ξ</sub>(f<sub>ξ</sub>(v'))</span>
<p>Si confrontano predizione e bersaglio <b>dopo la normalizzazione L2</b>:</p>
<span class="f">L<sub>v,v'</sub> = ‖ p<sub>θ</sub>/‖p<sub>θ</sub>‖ − sg( z'<sub>ξ</sub>/‖z'<sub>ξ</sub>‖ ) ‖²</span>
<p>Si scambiano le viste perché lo student impari in entrambe le direzioni (loss <b>simmetrizzata</b>):</p>
<span class="f">L<sub>BYOL</sub> = L<sub>v,v'</sub> + L<sub>v',v</sub></span>
<div class="box k"><b>Da saper fare: distanza fra vettori unitari = coseno</b>
<p>Per vettori di norma 1, ‖a − b‖² = ‖a‖² + ‖b‖² − 2a·b = <b>2 − 2 cos(p, z')</b>. Quindi la loss di BYOL è, a meno di costanti, l'opposto della similarità coseno (come nell'articolo).</p>
<p>Esempio: p = (3, 4) → p̂ = (0,6; 0,8); z' = (1, 0). Distanza: ‖(−0,4; 0,8)‖² = 0,16 + 0,64 = 0,80. Coseno: 0,6, quindi 2 − 1,2 = 0,80. Stesso numero.</p>
<p>Perché normalizzare: senza normalizzazione la rete potrebbe ridurre la loss semplicemente <b>accorciando i vettori</b> (‖s − t‖² diminuisce se tutto si avvicina a 0: un'altra strada verso il collasso). Con vettori unitari conta solo la <b>direzione</b>. La stessa normalizzazione è il motivo per cui gli embedding contrastivi vivono sull'ipersfera (libro § 30.10.1, <a href="#L21">L21</a>).</p></div>
"""), printed=P(20))

s(21, "MoCo: Momentum Contrast", R("""
<p><b>MoCo</b> (He et al., CVPR 2020). <b>Figura:</b> a sinistra l'<i>encoder</i> (verde) codifica una vista in una query; a destra il <i>momentum encoder</i> (azzurro) codifica l'altra vista in una chiave, che si affianca a una <b>coda</b> (queue) di chiavi passate; il prodotto ⊗ fra query e chiavi dà le <i>affinity</i>, da cui la loss.</p>
<ul>
<li><b>Teacher a momentum</b>: i pesi del momentum encoder sono un'EMA dello student, come in BYOL (MoCo è in realtà precedente a BYOL: l'idea dell'EMA nasce qui).</li>
<li><b>Loss contrastiva</b>, come in SimCLR, <b>con negativi</b>.</li>
<li><b>Coda FIFO</b>: conserva le rappresentazioni dei negativi dei minibatch precedenti; si aggiungono le nuove chiavi e si tolgono le più vecchie.</li>
</ul>
<p>La coda dà <b>molti negativi senza un minibatch grande</b>: SimCLR ha bisogno di batch da migliaia di immagini perché i negativi sono gli altri elementi del batch.</p>
<div class="box k"><b>Da saper dire: perché in MoCo serve l'EMA</b>
<p>Le chiavi nella coda sono state calcolate in passi precedenti. Se l'encoder delle chiavi cambiasse velocemente (fosse lo student stesso), chiavi vecchie e nuove verrebbero da reti diverse e il confronto non sarebbe coerente. Con un momentum alto (nell'articolo m = 0,999, coda di 65 536 chiavi, temperatura 0,07) l'encoder delle chiavi cambia così lentamente che tutta la coda è quasi «della stessa rete». In BYOL l'EMA serve invece a dare un bersaglio stabile senza negativi: stesso strumento, scopo diverso.</p></div>
<div class="box b"><b>Dal libro · Szeliski 2a ed., § 5.4.7</b>
<p>Szeliski ricostruisce la genealogia: Wu et al. (2018) tengono un embedding per ogni immagine del training in una <b>memory bank</b> aggiornata con una media mobile; MoCo sostituisce la memory bank con una <b>coda di lunghezza fissa</b> codificata da un momentum encoder separato dalla rete addestrata; SimCLR usa i negativi del minibatch e augmentation aggressive; MoCo v2 unisce le due cose (aggiunge il projector MLP e le augmentation di SimCLR).</p></div>
"""), printed=P(21))

s(22, "Summary: learning from two views", R("""
<p><b>Figura (riassunto delle tre architetture):</b></p>
<ul>
<li><b>SimCLR</b>: due encoder uguali (pesi condivisi), gradiente su entrambi i rami, loss di «similarity &amp; dissimilarity» (positivi e negativi).</li>
<li><b>BYOL</b>: a sinistra encoder + <b>predictor</b> con gradiente; a destra un <b>momentum encoder</b> (grigio) aggiornato per «moving average», senza gradiente; loss di sola similarità.</li>
<li><b>SimSiam</b>: due encoder con pesi condivisi, predictor da una parte sola, gradiente solo sul ramo con il predictor; loss di sola similarità.</li>
</ul>
<table>
<tr><th></th><th>Negativi</th><th>Predictor</th><th>Teacher EMA</th><th>Stop-grad</th></tr>
<tr><td>SimCLR</td><td>sì (batch)</td><td>no</td><td>no</td><td>no</td></tr>
<tr><td>MoCo</td><td>sì (coda)</td><td>no</td><td>sì</td><td>sì (ramo chiavi)</td></tr>
<tr><td>BYOL</td><td>no</td><td>sì</td><td>sì</td><td>sì</td></tr>
<tr><td>SimSiam</td><td>no</td><td>sì</td><td>no</td><td>sì</td></tr>
</table>
<div class="box k"><b>Da saper fare</b><p>Disegnare a memoria le tre architetture e dire per ognuna dove passa il gradiente e cosa impedisce il collasso. La progressione è: SimCLR (negativi) → MoCo (negativi senza batch enormi, grazie a coda + EMA) → BYOL (via i negativi, restano EMA + predictor + stop-grad) → SimSiam (via anche l'EMA).</p></div>
"""), printed=P(22))

# ===================== RIDUZIONE DELLA RIDONDANZA =====================

s(23, "Preventing collapse with feature statistics", R("""
<p>Un altro approccio: <b>vincolare direttamente le statistiche delle feature</b> nel minibatch. Tre obiettivi:</p>
<ul>
<li><b>Fra le viste: accordo</b>. La rappresentazione non cambia se l'immagine viene aumentata.</li>
<li><b>Fra le immagini: variazione</b>. Non dare la stessa rappresentazione a tutte le immagini (contro il collasso completo).</li>
<li><b>Fra le dimensioni: meno ridondanza</b>. Non copiare lo stesso segnale in tutte le coordinate (contro il collasso dimensionale).</li>
</ul>
<p><b>Barlow Twins</b> e <b>VICReg</b> mettono questi obiettivi nella loss con statistiche del minibatch, <b>senza negativi e senza teacher EMA</b>. I due rami sono simmetrici (stessa rete, gradiente su entrambi).</p>
<div class="box k"><b>Da saper dire: negativi «per dimensione» invece che «per campione»</b><p>Il contrastivo confronta <b>campioni</b>: la matrice B × B delle similarità fra immagini del batch deve avere il positivo alto e il resto basso. Barlow Twins e VICReg confrontano <b>dimensioni</b>: la matrice d × d delle correlazioni fra feature deve essere diagonale. Entrambi impediscono che tutto diventi uguale, guardando la stessa matrice dei dati Z (B × d) per righe o per colonne.</p></div>
"""), sec=("l22-ridondanza", "Riduzione della ridondanza", "slide 23–27"), printed=P(23))

s(24, "Barlow Twins", R("""
<p><b>Figura (dall'articolo):</b> un batch di immagini X viene distorto due volte (Y<sup>A</sup>, Y<sup>B</sup>); encoder f<sub>θ</sub> e projector condivisi producono gli embedding Z<sup>A</sup>, Z<sup>B</sup>; si calcola la cross-correlazione empirica C (immagine a scacchi grigi, d × d) e la si confronta con la matrice identità ℐ (diagonale nera) tramite la loss ℒ<sub>BT</sub>.</p>
<ul>
<li>Per ogni batch di B immagini si codificano due viste con <b>lo stesso encoder e projector</b>.</li>
<li>Gli embedding formano Z<sup>A</sup>, Z<sup>B</sup> ∈ ℝ<sup>B×d</sup>, <b>normalizzati</b>.</li>
<li>Cross-correlazione empirica del minibatch: <span class="f">C = (Z<sup>A</sup>)<sup>⊤</sup> Z<sup>B</sup> / B,   C ∈ ℝ<sup>d×d</sup></span></li>
</ul>
<div class="box k"><b>Da saper fare: quale normalizzazione</b>
<p>«Normalizzati» qui vuol dire <b>standardizzati lungo il batch, feature per feature</b>: per ogni colonna i, si sottrae la media sul batch e si divide per la deviazione standard sul batch (nell'articolo: z_norm = (z − z.mean(0)) / z.std(0), poi C = z_a_norm<sup>⊤</sup> z_b_norm / N). Non è la normalizzazione L2 di ogni vettore come in SimCLR o BYOL.</p>
<p>Così ogni elemento è una vera <b>correlazione</b> fra la feature i della vista A e la feature j della vista B, calcolata sulle B immagini:</p>
<span class="f">C<sub>ij</sub> = ∑<sub>b</sub> z<sup>A</sup><sub>b,i</sub> z<sup>B</sup><sub>b,j</sub> / ( √(∑<sub>b</sub> (z<sup>A</sup><sub>b,i</sub>)²) · √(∑<sub>b</sub> (z<sup>B</sup><sub>b,j</sub>)²) )  ∈ [−1, 1]</span>
<p>Con colonne a media nulla e varianza 1 (calcolata dividendo per B) i denominatori valgono √B · √B = B, e si ritrova la formula della slide.</p></div>
"""), printed=P(24))

s(25, "Barlow Twins: the loss", R("""
<span class="f">L = ∑<sub>i</sub> (1 − C<sub>ii</sub>)² + λ ∑<sub>i</sub> ∑<sub>j≠i</sub> C<sub>ij</sub>²</span>
<p>Primo termine = <b>invarianza</b>, secondo = <b>riduzione della ridondanza</b>. Si spinge C verso la matrice identità I:</p>
<ul>
<li><b>Diagonale C<sub>ii</sub> ≈ 1</b>: la stessa feature deve essere coerente fra le due viste. Si preserva l'informazione attraverso le augmentation.</li>
<li><b>Fuori diagonale C<sub>ij</sub> ≈ 0</b>: feature diverse devono portare segnali scorrelati fra le immagini. Si evita di ripetere informazione nelle dimensioni.</li>
</ul>
<p>Nell'articolo λ = 5 · 10<sup>−3</sup> (i termini fuori diagonale sono d² − d, molti più dei d diagonali) e il projector ha tre strati da 8192 unità: Barlow Twins funziona meglio con embedding <b>molto larghi</b>.</p>
<div class="box k"><b>Da saper fare: Barlow Twins su un esempio 2 × 2</b>
<p>Batch di B = 4 immagini, d = 2 feature, colonne già standardizzate (media 0, varianza 1 dividendo per 4):</p>
<ul>
<li>Vista A: feature 1 = (1, −1, 1, −1), feature 2 = (1, 1, −1, −1).</li>
<li>Vista B: feature 1 = (1, −1, 1, −1), feature 2 = (1, −1, −1, 1).</li>
</ul>
<p>C<sub>ij</sub> = (prodotto scalare fra la colonna i di A e la colonna j di B) / 4:</p>
<ul>
<li>C<sub>11</sub> = (1 + 1 + 1 + 1)/4 = 1: la feature 1 è invariante.</li>
<li>C<sub>22</sub> = (1 − 1 + 1 − 1)/4 = 0: la feature 2 cambia in modo scorrelato fra le viste.</li>
<li>C<sub>12</sub> = (1 + 1 − 1 − 1)/4 = 0, C<sub>21</sub> = (1 − 1 − 1 + 1)/4 = 0.</li>
</ul>
<p>C = [[1, 0], [0, 0]] → L = (1 − 1)² + (1 − 0)² + λ(0 + 0) = <b>1</b>. Tutta la loss viene dalla feature 2 non invariante. Se la vista B avesse feature 2 = (1, 1, −1, −1), uguale ad A, sarebbe C = I e L = 0: due feature invarianti e scorrelate, l'ottimo.</p></div>
"""), printed=P(25))

s(26, "Two ways to lose information", R("""
<p>La loss di Barlow Twins penalizza entrambi i collassi della slide 12:</p>
<ol>
<li><b>Tutte le immagini uguali</b> (collasso completo): le feature sono costanti sul batch, dopo la centratura valgono zero, quindi <span class="f">C = [[0, 0], [0, 0]]</span> La diagonale è 0 invece di 1: il termine di <b>invarianza</b> penalizza la perdita di variazione fra le immagini (L = d).</li>
<li><b>Le feature ripetono lo stesso segnale</b> (collasso dimensionale): le immagini hanno rappresentazioni diverse, ma ogni feature copia un unico segnale variabile, quindi tutte le dimensioni sono perfettamente correlate: <span class="f">C = [[1, 1], [1, 1]]</span> La fuori diagonale è 1 invece di 0: il termine di <b>ridondanza</b> penalizza l'informazione ripetuta (L = 2λ con d = 2).</li>
</ol>
<div class="box k"><b>Da notare</b><p>Il punto 1 è il motivo per cui Barlow Twins <b>non può</b> collassare su una costante come potrebbe BYOL: la loss stessa è alta in quel punto. A rigore, con feature costanti la deviazione standard è zero e la standardizzazione divide per zero; nell'implementazione si usa una BatchNorm senza parametri, che ha un ε al denominatore, quindi le feature costanti diventano davvero 0 come scrive la slide. Il punto 2 è un vincolo che SimCLR non ha in modo esplicito.</p></div>
"""), printed=P(26))

s(27, "VICReg: three explicit constraints", R("""
<p><b>VICReg</b> = <i>Variance-Invariance-Covariance Regularization</i> (Bardes, Ponce, LeCun, ICLR 2022). Tre termini separati:</p>
<span class="f">L = λ s(Z, Z') + μ [v(Z) + v(Z')] + ν [c(Z) + c(Z')]</span>
<table>
<tr><th>Termine</th><th>Vincolo</th><th>Effetto</th></tr>
<tr><td><b>Invarianza s</b></td><td>mean<sub>b</sub> ‖z<sub>b</sub> − z'<sub>b</sub>‖²</td><td>le viste accoppiate devono coincidere</td></tr>
<tr><td><b>Varianza v</b></td><td>mean<sub>j</sub> max(0, γ − σ<sub>j</sub>(Z)), σ<sub>j</sub> = deviazione standard della feature j sulle immagini, γ = soglia minima</td><td>niente feature costanti: ogni coordinata deve variare fra le immagini</td></tr>
<tr><td><b>Covarianza c</b></td><td>(1/d) ∑<sub>i≠j</sub> Cov(Z)<sub>ij</sub>² dentro ogni vista</td><td>meno segnali ridondanti fra le dimensioni, in ciascuna vista separatamente</td></tr>
</table>
<div class="box k"><b>Da saper fare: confronto con Barlow Twins</b>
<ul>
<li>Barlow Twins mette invarianza e varianza nello <b>stesso</b> termine (C<sub>ii</sub> = 1 richiede sia accordo sia varianza non nulla, perché c'è la standardizzazione). VICReg li <b>separa</b>: l'invarianza è una semplice distanza al quadrato, la varianza è una hinge sulla deviazione standard.</li>
<li>La covarianza di VICReg è calcolata <b>dentro</b> ogni vista (Cov(Z), non la cross-correlazione fra Z e Z'), quindi i due rami possono anche essere reti diverse o modalità diverse.</li>
<li>Esempio della varianza con γ = 1: se una feature ha σ = 0,3 sul batch, contribuisce max(0, 1 − 0,3) = 0,7; se ha σ = 1,5 contribuisce 0. È una hinge: spinge solo le feature che variano troppo poco, non costringe a varianza esattamente 1.</li>
</ul>
<p>Valori dell'articolo: λ = μ = 25, ν = 1, γ = 1, expander a tre strati da 8192.</p></div>
<div class="box x"><b>Precisazione sulla formula</b><p>Nell'articolo la deviazione standard è regolarizzata: S(x, ε) = √(Var(x) + ε) con ε = 10<sup>−4</sup>, per evitare gradienti enormi quando la varianza tende a zero (la derivata di √ in 0 è infinita). La covarianza usa 1/(n − 1) e la media del batch. La slide scrive σ<sub>j</sub> senza ε: va bene per capire, non per implementare.</p></div>
"""), printed=P(27))

# ===================== RICOSTRUZIONE E MASKED IMAGE MODELING =====================

s(28, "Reconstruction Models", R("""
<p>Divisoria di sezione (Part 1): <b>modelli di ricostruzione</b>. Cambia il segnale: invece di far coincidere due viste, si nasconde o si comprime l'immagine e si chiede alla rete di <b>ricostruirla</b>. Il bersaglio è l'immagine stessa (o una sua codifica), quindi il collasso su una costante non è una soluzione: una rete costante ricostruisce male.</p>
"""), kind='div', sec=("l22-mim", "Ricostruzione e masked image modeling", "slide 28–40"), printed=P(28))

s(29, "Historical reconstruction: Autoencoders", R("""
<span class="f">x̂ = d<sub>φ</sub>(f<sub>θ</sub>(x)),   L = ‖x̂ − x‖²</span>
<p>f<sub>θ</sub> = encoder, d<sub>φ</sub> = decoder.</p>
<ul>
<li><b>Bersaglio</b>: ricostruire l'immagine originale.</li>
<li><b>Collo di bottiglia</b> (bottleneck): comprimere l'informazione in una rappresentazione compatta; senza il collo di bottiglia la rete imparerebbe l'identità.</li>
</ul>
<p><b>Figura (Masci et al. 2011):</b> autoencoder convoluzionale su una cifra MNIST «2»: conv con stride 2 (28 × 28 → 14 × 14 → 7 × 7 → 3 × 3), flatten, uno strato fully connected stretto al centro, poi reshape e deconvoluzioni simmetriche fino a ricostruire il «2».</p>
<div class="box b"><b>Dal libro · {C30}, § 30.4 Autoencoders</b>
<ul>
<li>Un autoencoder accetta di buttare informazione <b>ridondante</b> ma non di <b>perdere</b> informazione: è compressione nel senso della Tab. 30.1. La loss decide cosa sacrificare quando il collo di bottiglia non basta: la L2 si scompone in una somma sui pixel, quindi guarda ogni pixel separatamente e non penalizza errori di struttura (bordi, texture). Per questo le ricostruzioni L2 sono sfocate.</li>
<li>Il decoder è un'<b>impalcatura</b>: per il representation learning si butta e si tiene f. È lo stesso destino del decoder di MAE (slide 34).</li>
<li>Un autoencoder lineare con perdita L2 impara lo stesso sottospazio della <b>PCA</b> (collegamento con <a href="#L16">L16</a>, PCA delle feature).</li>
<li>§ 30.4.1: le feature dell'autoencoder sul dataset giocattolo sono buone per la forma negli strati profondi e per il colore nei pixel (slide 8).</li>
</ul>
<p>Il libro scrive la loss L2 con una radice quadrata in più (‖·‖<sub>2</sub> invece del quadrato) in un punto del § 30.4: non cambia il minimo, ma la forma standard, come nella slide, è il quadrato.</p></div>
"""), printed=P(29))

s(30, "Masking: learning from missing information", R("""
<p>«The cat sits on the ____.»</p>
<ol>
<li>Si nasconde una parte dell'osservazione.</li>
<li>Si usa il contesto visibile per predire il contenuto mancante.</li>
<li>Si impara usando l'osservazione originale come bersaglio.</li>
</ol>
<p><b>BERT</b> (Devlin et al. 2019) usa questa idea per il <b>masked language modeling</b>: predire le parole mascherate dal testo intorno (circa il 15% dei token).</p>
<p>Per le immagini la domanda di progetto è <b>cosa predire</b>: <b>pixel</b> (SimMIM, MAE), <b>codici discreti</b> (BEiT) o <b>feature apprese</b> (DINOv2 slide 48, JEPA slide 56).</p>
<div class="box b"><b>Dal libro · {C30}, § 30.7 Imputation</b>
<p>Il libro chiama questa famiglia <b>imputation</b>: predire elementi mancanti del tensore dei dati. L'inpainting (pixel mancanti nello spazio), la colorizzazione (canali mancanti) e la predizione del fotogramma futuro (tempo mancante) sono tutti casi dello stesso schema (fig. 30.8). Anche Prince (§ 9.3.7) divide l'SSL in due famiglie: <b>generativa</b> (si maschera parte di ogni esempio e si predice la parte mancante) e <b>contrastiva</b>.</p></div>
"""), printed=P(30))

s(31, "Image patches become transformer tokens", R("""
<p>Il ViT (<a href="#L17">L17</a>, <a href="#L18">L18</a>) divide l'immagine in <b>patch</b> (spesso 16 × 16 pixel) e proietta ogni patch in un <b>token</b>.</p>
<p><b>Figura:</b> un fenicottero diviso in una griglia di patch; a destra la stessa griglia con molte patch sostituite da quadrati grigi (mascherate).</p>
<span class="f">N = HW / P²</span>
<p>Esempio: immagine 224 × 224, patch 16 × 16 → 14 × 14 = <b>196 token</b>.</p>
<p>Il <b>masked image modeling</b> (MIM) nasconde alcune patch e impara a predire informazioni sulle regioni mancanti.</p>
<div class="box k"><b>Da saper fare: contare patch e token</b>
<ul>
<li>224 × 224, P = 16: 224/16 = 14 per lato → 196 patch; ogni patch ha 16 · 16 · 3 = <b>768</b> valori (lo stesso numero della dimensione D di ViT-B, per coincidenza).</li>
<li>224 × 224, P = 14 (DINOv2): 16 × 16 = 256 patch. 518 × 518, P = 14: 37 × 37 = 1369 patch.</li>
<li>MAE con 75% mascherato: 196 · 0,25 = <b>49</b> patch visibili; BEiT con circa il 40%: al massimo 75 patch mascherate (dato dell'articolo).</li>
</ul></div>
<div class="box b"><b>Dal libro · {C26}, § 26.4.1 Tokenizing Data</b>
<p>Tokenizzare un'immagine = rappresentare ogni patch con un vettore: la patch vettorizzata (i tre canali impilati) oppure una sua proiezione lineare appresa a dimensione più bassa. Il libro scrive i token come <b>righe</b> di una matrice T e sottolinea che per un transformer i token sono un <b>insieme</b> (equivarianza alle permutazioni, § 26.8): per questo un encoder può lavorare anche su un sottoinsieme di patch, come fa MAE, purché ogni token porti la sua codifica di posizione. Il § 26.10 cita il masked autoencoding fra gli usi dell'attenzione mascherata.</p></div>
"""), printed=P(31))

s(32, "SimMIM: predicting masked pixels", R("""
<p><b>SimMIM</b> (Xie et al., CVPR 2022). <b>Figura:</b> un'immagine di un castello divisa in patch, alcune sostituite da token di maschera (tratteggiati); tutta la griglia entra nell'encoder (ViT o Swin); una «One-layer Prediction Head» ricostruisce le patch mascherate, confrontate con l'originale con una loss ℓ<sub>1</sub>.</p>
<ul>
<li>Gli embedding delle patch mascherate si sostituiscono con <b>lo stesso token appreso m</b>.</li>
<li>L'encoder vede <b>tutta la griglia</b> (patch visibili + token di maschera).</li>
<li>Si ricostruiscono i pixel RGB con una <b>testa lineare</b>.</li>
</ul>
<span class="f">L = (1 / Ω(x<sub>M</sub>)) ‖y<sub>M</sub> − x<sub>M</sub>‖<sub>1</sub></span>
<p>x<sub>M</sub> = pixel originali mascherati, y<sub>M</sub> = predizioni nelle posizioni mascherate, Ω(x<sub>M</sub>) = numero di pixel mascherati. È un errore assoluto medio calcolato <b>solo sulle parti nascoste</b>.</p>
<div class="box x"><b>Approfondimento</b><p>Il messaggio dell'articolo è nel nome: basta poco. Mascheramento casuale con patch di maschera grandi (32 × 32) e rapporto moderato (circa 60%), testa di un solo strato lineare, regressione diretta dei pixel con L1: niente tokenizer, niente decoder profondo. Le patch di maschera grandi servono a rendere il compito non banale: con patch piccole basterebbe interpolare dai vicini (il «compito troppo facile» della slide 9).</p></div>
"""), printed=P(32))

s(33, "Masked Autoencoder (MAE)", R("""
<p><b>MAE</b> (He et al., CVPR 2022). <b>Figura:</b> l'immagine di ingresso con la maggior parte delle patch grigie; solo le poche patch visibili entrano nell'<b>encoder ViT</b>; alle loro uscite (azzurre) si aggiungono i token di maschera condivisi (grigi) nelle posizioni mancanti; tutta la sequenza entra in un <b>decoder</b> leggero (Transformer piccolo) che produce le patch ricostruite (rosse), confrontate con il <i>target</i>.</p>
<ul>
<li>Come gli autoencoder classici, impara <b>ricostruendo l'ingresso</b>.</li>
<li>Si maschera a caso il <b>75%</b> delle patch.</li>
<li>L'encoder ViT elabora <b>solo le patch visibili</b>.</li>
<li>Il token di maschera condiviso m si inserisce <b>prima del decoder</b>, non prima dell'encoder.</li>
</ul>
<div class="box k"><b>Da saper fare: quanto si risparmia nell'encoder</b>
<p>Immagine 224 × 224, P = 16: N = 196 token; visibili 25% → 49 token. Per un blocco transformer con dimensione D, il costo è circa 12ND² (proiezioni Q, K, V, uscita e MLP con espansione 4) più 2N²D (QK<sup>⊤</sup> e il prodotto con V).</p>
<ul>
<li>Parte lineare: proporzionale a N → 4 volte meno.</li>
<li>Parte di attenzione: proporzionale a N² → 16 volte meno.</li>
<li>Con ViT-L (D = 1024): 12 · 196 · 1024² ≈ 2,47 · 10<sup>9</sup> e 2 · 196² · 1024 ≈ 7,9 · 10<sup>7</sup>, totale ≈ 2,54 · 10<sup>9</sup> moltiplicazioni-somme per blocco; con 49 token ≈ 6,2 · 10<sup>8</sup>. Rapporto ≈ <b>4,1</b>.</li>
</ul>
<p>A 196 token domina la parte lineare, quindi il risparmio vero è circa 4×, non 16×. Il decoder lavora su tutti i 196 token ma è piccolo (nell'articolo 8 blocchi larghi 512, contro i 24 blocchi larghi 1024 di ViT-L): l'articolo riporta un addestramento <b>3 volte o più</b> più veloce. Il costo risparmiato permette modelli più grandi: è il «scalable» del titolo.</p></div>
<div class="box k"><b>Da saper dire: perché il 75% e non il 15% di BERT</b><p>Le immagini sono molto <b>ridondanti</b> nello spazio: una patch mancante si indovina bene interpolando le vicine, senza capire nulla. Le parole invece sono dense di significato. Con il 75% nascosto la rete deve ricostruire parti intere di oggetti, e per farlo serve una comprensione globale della scena.</p></div>
"""), printed=P(33))

s(34, "MAE: reconstruction and feature reuse", R("""
<p><b>Durante il pretraining</b>: un decoder Transformer leggero (meno profondo e più stretto) ricostruisce i pixel delle patch mascherate.</p>
<p><b>Per i compiti a valle</b>: si usano le feature <b>prima del decoder</b>; si tiene l'encoder e si butta il decoder.</p>
<span class="f">L<sub>MAE</sub> = (1/|M|) ∑<sub>i∈M</sub> MSE(x̂<sub>i</sub>, x<sub>i</sub>)</span>
<p>M = posizioni delle patch mascherate; x̂<sub>i</sub>, x<sub>i</sub> = pixel predetti e originali della patch i. La loss è l'errore quadratico medio <b>solo sulle patch mascherate</b>.</p>
<div class="box k"><b>Da saper dire</b>
<ul>
<li><b>Perché solo le mascherate</b>: sulle patch visibili il compito è copiare l'ingresso, che non insegna nulla; l'articolo riporta che includerle peggiora l'accuratezza.</li>
<li><b>Bersaglio normalizzato</b>: nell'articolo la variante migliore predice i pixel di ogni patch <b>normalizzati</b> (sottratta la media e divisa la deviazione standard della patch stessa). Così la rete non spreca capacità sulla luminosità media e si concentra sulla struttura locale (contrasto, bordi).</li>
<li><b>Feature per il linear probe</b>: le feature di MAE sono meno separabili linearmente di quelle contrastive (slide 40): MAE dà il meglio con il fine-tuning.</li>
</ul></div>
"""), printed=P(34))

s(35, "BEiT · Phase 1: learn a visual vocabulary", R("""
<p><b>BEiT</b> = <i>BERT pre-training of Image Transformers</i> (Bao et al., ICLR 2022).</p>
<p><b>Figura:</b> l'immagine di un cane (shiba) entra in un <b>tokenizer</b> che produce una griglia di numeri interi (i <i>visual tokens</i>, per esempio 123, 234, 456…); un <b>decoder</b> (riquadro tratteggiato, «unused during pre-training») ricostruisce l'immagine dai token.</p>
<ul>
<li>Un <b>tokenizer visivo</b> converte ogni patch in un <b>ID discreto</b> (un indice in un vocabolario).</li>
<li>Tokenizer e decoder si addestrano come un <b>autoencoder variazionale discreto</b> (dVAE, con CNN).</li>
<li>Ogni ID identifica un pattern visivo appreso.</li>
<li>Poi il tokenizer si <b>congela</b> e il suo decoder si butta.</li>
</ul>
<div class="box w"><b>Attenzione: chi addestra il tokenizer</b><p>La slide presenta la fase 1 come un passo di BEiT. Nell'articolo gli autori <b>non</b> addestrano il tokenizer: usano direttamente quello <b>pubblico del dVAE di DALL-E</b> (Ramesh et al. 2021), con vocabolario di <b>8192</b> codici; un tokenizer riaddestrato su ImageNet compare solo come confronto in appendice. La fase 1 è quindi un pretraining separato, fatto da altri, su altri dati. La tabella della slide 38 lo dice correttamente («separately pretrained and frozen»).</p></div>
<div class="box b"><b>Dal libro · {C33}, § 33.4 Variational Autoencoders</b>
<p>Il decoder di un autoencoder è un <b>generatore</b> di dati (§ 33.4.1); il VAE rende il codice una variabile aleatoria e si addestra massimizzando un limite inferiore della verosimiglianza (variational inference, § 33.4.3). Il dVAE di DALL-E è la versione con codice <b>discreto</b>: ogni posizione della griglia sceglie uno degli 8192 codici. Per seguire BEiT basta l'idea: il tokenizer trasforma l'immagine in una «frase» di parole visive.</p></div>
"""), printed=P(35))

s(36, "BEiT · Phase 2: predict missing visual tokens", R("""
<p><b>Figura (dall'articolo):</b> in alto il tokenizer congelato trasforma l'immagine originale nella griglia di ID; in basso la stessa immagine è divisa in patch, alcune mascherate a blocchi (<i>blockwise masking</i>); la sequenza ([S], patch e token [M], più embedding di posizione 0–16) entra nel <b>BEiT Encoder</b>; sopra, una <i>Masked Image Modeling Head</i> predice gli ID nelle posizioni mascherate (per esempio 234, 456, 876, 765, 322).</p>
<ol>
<li>Il tokenizer congelato legge l'immagine originale e genera gli ID bersaglio.</li>
<li>Gli embedding delle patch selezionate si sostituiscono con un <b>embedding di maschera appreso</b>.</li>
<li>Si addestrano l'encoder BEiT e la testa di predizione a recuperare gli ID nelle posizioni mascherate.</li>
</ol>
<div class="box x"><b>Approfondimento: i numeri dell'articolo</b><p>Immagine 224 × 224, patch 16 × 16, griglia di 14 × 14 = 196 patch e altrettanti token visivi. Si maschera circa il <b>40%</b> delle patch (al massimo 75) a <b>blocchi</b>: si estraggono rettangoli di almeno 16 patch con rapporto d'aspetto casuale finché si supera il 40%. Il mascheramento a blocchi rende il compito più difficile del casuale, per lo stesso motivo delle patch di maschera grandi di SimMIM.</p></div>
"""), printed=P(36))

s(37, "BEiT predicts code IDs, not pixels", R("""
<p>Bersaglio: gli <b>ID discreti</b> generati dal tokenizer congelato.</p>
<span class="f">ℒ<sub>BEiT</sub> = 𝔼<sub>M</sub> [ ∑<sub>i∈M</sub> log p<sub>MIM</sub>(z<sub>i</sub> | x<sup>ℳ</sup>) ]   (come scritta nella slide)</span>
<p>M = posizioni mascherate, z<sub>i</sub> = ID bersaglio del tokenizer nella posizione i, x<sup>ℳ</sup> = immagine con le patch mascherate. La <b>cross-entropy</b> classifica ogni posizione mascherata sul vocabolario visivo.</p>
<p>La fase 1 impara il vocabolario, la fase 2 impara a predirne i codici dal contesto. A valle si riusa l'<b>encoder BEiT</b>.</p>
<div class="box w"><b>Attenzione: manca il segno (o il max)</b><p>Scritta così, ℒ<sub>BEiT</sub> è una <b>log-verosimiglianza</b>: un numero ≤ 0 che va <b>massimizzato</b>. Nell'articolo infatti l'obiettivo è scritto come <b>max</b> ∑<sub>x</sub> 𝔼<sub>M</sub>[∑<sub>i∈M</sub> log p<sub>MIM</sub>(z<sub>i</sub> | x<sup>M</sup>)]. Se lo si chiama «loss» da minimizzare, come nella slide e come la cross-entropy citata sotto, serve il meno:</p>
<span class="f">ℒ<sub>BEiT</sub> = −𝔼<sub>M</sub> [ ∑<sub>i∈M</sub> log p<sub>MIM</sub>(z<sub>i</sub> | x<sup>M</sup>) ]</span>
<p>Minimizzare la formula della slide senza meno porterebbe a rendere le probabilità corrette più piccole possibile.</p></div>
<div class="box k"><b>Da saper fare</b><p>Esempio con vocabolario di 4 codici: in una posizione mascherata la testa predice p = (0,1; 0,6; 0,2; 0,1) e il codice vero è il 2. Contributo alla cross-entropy: −log 0,6 ≈ 0,51. Se la rete fosse sicura e giusta (p = 1 sul codice 2) il contributo sarebbe 0; con p uniforme sarebbe log 4 ≈ 1,39. Con 8192 codici il valore di partenza (uniforme) è log 8192 ≈ 9,0.</p></div>
"""), printed=P(37))

s(38, "Masked image modeling: recap", R("""
<table>
<tr><th></th><th>SimMIM</th><th>MAE</th><th>BEiT</th></tr>
<tr><td>Ingresso dell'encoder</td><td>griglia completa</td><td>solo token visibili</td><td>griglia completa</td></tr>
<tr><td>Token di maschera aggiunti</td><td>prima dell'encoder</td><td>prima del decoder</td><td>prima dell'encoder</td></tr>
<tr><td>Modulo di predizione</td><td>testa lineare</td><td>decoder Transformer leggero</td><td>testa di classificazione</td></tr>
<tr><td>Bersaglio / loss</td><td>pixel / L1</td><td>pixel / MSE</td><td>ID discreti / cross-entropy</td></tr>
<tr><td>Tokenizer discreto</td><td>non serve</td><td>non serve</td><td>preaddestrato a parte e congelato</td></tr>
</table>
<p>SimMIM e MAE predicono <b>pixel</b>; BEiT predice <b>codici visivi discreti</b>.</p>
<div class="box k"><b>Da saper dire: una conseguenza della riga «ingresso dell'encoder»</b><p>In SimMIM e BEiT l'encoder vede i token di maschera durante il pretraining ma non li vedrà mai a valle (dove le immagini sono intere): c'è una piccola differenza fra pretraining e uso. In MAE l'encoder non vede mai token di maschera, quindi pretraining e uso sono coerenti, e in più il pretraining costa meno (slide 33). Il prezzo è che il decoder deve essere un vero Transformer, perché è lui che deve «riempire» le posizioni mancanti.</p></div>
"""), printed=P(38))

s(39, "Instance Discrimination vs MIM", R("""
<table>
<tr><th>Scelta</th><th>Contrastivo / instance discrimination</th><th>Ricostruzione mascherata</th></tr>
<tr><td>Bersaglio</td><td>far coincidere viste della stessa immagine, contro i negativi</td><td>predire pixel o codici mancanti</td></tr>
<tr><td>Viste per immagine</td><td>di solito due o più viste aumentate</td><td>può bastare una vista mascherata</td></tr>
<tr><td>Bias osservati</td><td>più struttura globale e forma</td><td>più dettaglio locale e texture</td></tr>
</table>
<p><b>Costo della pipeline di ingresso</b>: le augmentation forti girano spesso sulla CPU; generare più viste può fare da collo di bottiglia nel caricamento dei dati e lasciare la GPU ad aspettare. La ricostruzione mascherata non richiede viste multiple.</p>
<div class="box x"><b>Approfondimento: cosa dice Park et al. (ICLR 2023)</b><ul>
<li>Nei ViT contrastivi gli strati finali hanno un'attenzione quasi <b>uguale per tutte le query</b> (tutti i token guardano gli stessi token dell'oggetto): ottimo per una rappresentazione globale dell'immagine, meno per la diversità dei token.</li>
<li>Il contrastivo usa le basse frequenze (forma), il MIM le alte frequenze (texture); il contrastivo sfrutta soprattutto gli strati finali, il MIM i primi.</li>
<li>Conclusione dell'articolo: le due famiglie sono <b>complementari</b>, e combinarle (come fanno iBOT e DINOv2, slide 48) prende il meglio di entrambe.</li>
</ul>
<p>Il collegamento con il libro (§ 30.4.1 e 30.10.2): ciò che la rappresentazione cattura (colore, forma, texture) dipende dall'obiettivo e dalle trasformazioni scelte.</p></div>
"""), printed=P(39))

s(40, "Which representations transfer better?", R("""
<p><b>Figura (da Park et al.):</b> tre grafici. Sinistra: accuratezza di fine-tuning contro linear probing; MoCo e DINO (rossi) hanno linear probing più alto (verso 75–80) ma fine-tuning più basso; SimMIM, BEiT, MAE (blu) l'opposto. Centro: fine-tuning al crescere della taglia del modello (Ti, S, B, L, H): le curve dei metodi mascherati (MAE, BEiT) superano quelle contrastive ai modelli grandi. Destra: ImageNet contro COCO (detection): MAE e BEiT sono più a destra (migliori su COCO), MoCo e il supervisionato più a sinistra.</p>
<ul>
<li><b>Linear probing</b>: l'instance discrimination dà feature più <b>separabili linearmente</b>.</li>
<li><b>Fine-tuning e scala</b>: i modelli mascherati possono superare l'instance discrimination, soprattutto con modelli <b>grandi</b>.</li>
<li><b>Compiti densi</b>: i modelli mascherati vanno bene in object detection, dove conta il dettaglio spaziale.</li>
</ul>
<p>La rappresentazione migliore <b>dipende dal compito a valle</b> (e dal protocollo di valutazione della slide 8).</p>
<div class="box k"><b>Da saper dire</b><p>Perché MAE è peggiore in linear probe ma migliore in fine-tuning: ricostruire pixel richiede di conservare molta informazione di basso livello, quindi le classi non sono già separate da un iperpiano nelle feature finali; ma l'informazione c'è, e il fine-tuning la riorganizza. Le feature contrastive sono già «compresse» verso la semantica dell'immagine intera (separabili), ma hanno buttato parte del dettaglio spaziale.</p></div>
"""), printed=P(40))

# ===================== FOUNDATION MODELS =====================

s(41, "Part 2 · Vision Foundation Models", R("""
<p>Divisoria della seconda parte: <i>scale and generalization matter</i>. Da qui in poi i metodi sono quelli delle parti precedenti (teacher EMA, multi-crop, mascheramento), ma con dati e modelli molto più grandi.</p>
"""), kind='div', sec=("l22-foundation", "Vision foundation model", "slide 41–59"), printed='')

s(42, "Vision foundation models", R("""
<p><b>Foundation model visivo</b>: modello visivo grande, preaddestrato in modo ampio, che supporta <b>molti compiti</b> a valle.</p>
<ul>
<li>Contano <b>scala e diversità</b> dei dati di addestramento.</li>
<li>Le rappresentazioni devono trasferire oltre un singolo benchmark.</li>
<li><b>Backbone congelata + teste per i compiti</b> è uno schema pratico di deployment: un solo passaggio nell'encoder, poi teste leggere per classificazione, segmentazione, profondità.</li>
</ul>
<p>Obiettivo: <b>riuso ampio</b>, una backbone che dà feature forti su molti compiti e domini.</p>
<div class="box b"><b>Dal libro · {C37}, § 37.3.1 e {C30}, § 30.11</b>
<p>L'esempio della fig. 37.3 è proprio questo schema: un featurizer generico <b>congelato</b> («we do not need to update it for each new problem») sotto moduli specifici per profondità, semantica e detection. Il § 30.11 avverte su cosa vuol dire «general-purpose»: non una rappresentazione buona per <b>tutti</b> i compiti possibili, ma per un'ampia varietà dei compiti che interessano agli esseri umani, che sono una piccolissima parte di tutti i compiti possibili.</p></div>
"""), printed=P(42))

s(43, "DINO: self-distillation on Vision Transformers", R("""
<p><b>DINO</b> = <i>self-DIstillation with NO labels</i> (Caron et al., ICCV 2021).</p>
<p><b>Figura (dall'articolo):</b> un'immagine x produce due viste x<sub>1</sub>, x<sub>2</sub>; x<sub>1</sub> entra nello <i>student g<sub>θs</sub></i>, x<sub>2</sub> nel <i>teacher g<sub>θt</sub></i>, collegato allo student da una freccia «ema». Sul ramo teacher: <b>centering</b>, poi softmax, poi stop-gradient (sg) → p<sub>2</sub>. Sul ramo student: softmax → p<sub>1</sub>. Loss: −p<sub>2</sub> log p<sub>1</sub>.</p>
<ul>
<li>DINO fa coincidere le <b>distribuzioni di uscita</b> del teacher e dello student, con una backbone ViT e una testa di proiezione.</li>
<li><b>Student</b>: vede ritagli globali e locali; si aggiorna con i gradienti.</li>
<li><b>Teacher</b>: vede solo ritagli globali; si aggiorna per EMA.</li>
</ul>
<p>Obiettivo di instance discrimination: far coincidere le distribuzioni fra viste diverse della stessa immagine.</p>
<div class="box k"><b>Da saper dire: in cosa DINO è BYOL e in cosa no</b>
<ul>
<li>Come BYOL: student e teacher con la stessa architettura, teacher = EMA dello student (τ da 0,996 a 1), stop-gradient, nessun negativo.</li>
<li>Diverso: invece di una regressione fra vettori normalizzati, la testa produce K <b>logit</b> (nell'articolo K = 65 536), trasformati in distribuzioni con una softmax con temperatura; la loss è la <b>cross-entropy</b> H(P<sub>t</sub>, P<sub>s</sub>) = −∑<sub>k</sub> P<sub>t,k</sub> log P<sub>s,k</sub> (distillazione «alla Hinton» senza etichette). Niente predictor: contro il collasso si usano <b>centering e sharpening</b> (slide 44).</li>
<li><b>Multi-crop</b>: 2 ritagli globali a 224 × 224 (oltre il 50% dell'immagine) e diversi ritagli locali a 96 × 96 (meno del 50%). Il teacher vede solo i globali, lo student tutti: lo student deve indovinare dal particolare la descrizione dell'insieme («local-to-global»).</li>
</ul></div>
<div class="box b"><b>Dal libro · {C37}, § 37.4.1 Knowledge distillation</b>
<p>Nella distillazione lo student imita la <b>pmf</b> del teacher invece di un'etichetta one-hot. Il libro spiega perché aiuta: una pmf dice anche a cosa assomiglia l'immagine («90% gatto, 10% tigre»), quindi è più informativa di un'etichetta. In DINO le «classi» sono le K dimensioni astratte della testa, che nessuno ha definito: la pmf del teacher fa da pseudo-etichetta morbida. La parola <i>self</i>-distillation viene dal fatto che il teacher non è un modello più grande addestrato prima, ma la media dello student.</p></div>
"""), printed=P(43))

s(44, "DINO: centering and sharpening", R("""
<span class="f">p<sub>t</sub> = softmax( (u<sub>t</sub> − c) / τ<sub>t</sub> )</span>
<p>u<sub>t</sub> = logit del teacher, c = media mobile dei logit del teacher, τ<sub>t</sub> = temperatura del teacher.</p>
<table>
<tr><th>Operazione</th><th>Come funziona</th><th>Collasso che contrasta</th></tr>
<tr><td><b>Centering</b></td><td>sottrae la media mobile di ogni logit del teacher</td><td>la stessa coordinata domina per ogni immagine</td></tr>
<tr><td><b>Sharpening</b></td><td>temperatura bassa → bersagli piccati</td><td>ogni immagine riceve una distribuzione piatta, uniforme</td></tr>
</table>
<p>Il centering <b>bilancia l'uso delle uscite</b>; lo sharpening mantiene i bersagli individuali <b>informativi</b>. Lavorano insieme a EMA e stop-gradient: l'articolo mostra che togliendone uno dei due il modello collassa.</p>
<div class="box k"><b>Da saper fare: centering e sharpening su un esempio numerico</b>
<p>K = 3 uscite, due immagini nel batch con logit del teacher u<sup>(1)</sup> = (5, 1, 0) e u<sup>(2)</sup> = (5, 0, 1). La prima coordinata domina per entrambe.</p>
<ul>
<li><b>Senza centering</b>, τ = 1: p = (0,976; 0,018; 0,007) e (0,976; 0,007; 0,018). Con τ = 0,04 diventa (1, 0, 0) per entrambe: tutte le immagini nella stessa «classe» = <b>collasso su una dimensione</b>. Lo student impara a dire sempre «classe 1».</li>
<li><b>Centering</b>: c = media = (5; 0,5; 0,5). Logit centrati: (0; 0,5; −0,5) e (0; −0,5; 0,5).</li>
<li><b>Centering senza sharpening</b> (τ = 1): p = (0,307; 0,507; 0,186) e (0,307; 0,186; 0,507). Le immagini ora si distinguono, ma le distribuzioni sono quasi piatte: il centering da solo spinge verso l'<b>uniforme</b>, l'altro collasso.</li>
<li><b>Centering + sharpening</b> (τ = 0,04, logit divisi per 0,04 → (0; 12,5; −12,5)): p ≈ (0, 1, 0) e (0, 0, 1). Bersagli <b>netti e diversi</b> per le due immagini: è ciò che si vuole.</li>
</ul>
<p>Nell'articolo τ<sub>t</sub> sale da 0,04 a 0,07 nelle prime 30 epoche, τ<sub>s</sub> = 0,1 (lo student è meno piccato del teacher).</p></div>
<div class="box b"><b>Dal libro · {C12}, § 12.7.4 (softmax e temperatura)</b>
<p>Dividere i logit per una temperatura τ &lt; 1 rende la softmax più vicina a un argmax (piccata); τ &gt; 1 la appiattisce verso l'uniforme (<a href="#L15">L15</a>). Attenzione alla notazione del libro: lì la softmax è scritta con e<sup>−τx</sup>, cioè τ è una temperatura <b>inversa</b> con un segno insolito. Nelle slide e nell'articolo τ divide i logit.</p></div>
"""), printed=P(44))

s(45, "One DINO training step", R("""
<p>Pseudocodice di un passo, come nell'implementazione ufficiale:</p>
<pre><code>views = augment(images)            # ritagli globali + locali
s_logits = student(views.all_crops)
with no_grad():
    t_logits = teacher(views.global_crops)
    p_t = softmax((t_logits - center) / tau_t, dim=-1)
log_p_s = log_softmax(s_logits / tau_s, dim=-1)
loss = cross_view_loss(p_t, log_p_s, skip_same_view=True)
optimizer.zero_grad(); loss.backward()
optimizer.step()                   # solo lo student
ema_update(teacher, student, momentum)
center = rho * center + (1 - rho) * t_logits.mean(dim=0)</code></pre>
<ul>
<li><code>no_grad</code> sul teacher = <b>stop-gradient</b>.</li>
<li><code>skip_same_view=True</code>: non si confronta una vista con sé stessa. La loss somma −p<sub>t</sub>(x) · log p<sub>s</sub>(x') su tutte le coppie con x globale e x' ≠ x.</li>
<li>Ordine: prima il passo dell'ottimizzatore sullo student, poi l'EMA del teacher, poi l'aggiornamento del <b>centro</b>, anch'esso una media mobile (con il fattore rho) della media dei logit del teacher sul batch.</li>
</ul>
<div class="box k"><b>Da saper fare: contare le coppie della loss</b><p>Con 2 ritagli globali e 6 locali (8 viste per lo student): ogni globale del teacher si confronta con le altre 7 viste dello student → 2 · 7 = <b>14</b> termini per immagine. Il centro dipende solo dalle statistiche del batch, quindi il centering è economico (nessuna matrice B × B come nel contrastivo). Nell'ablazione dell'articolo un fattore del centro m = 0,9 funziona bene, mentre m = 0,999 (centro troppo lento) porta al collasso.</p></div>
"""), printed=P(45))

s(46, "DINO: emergent visual structure", R("""
<p><b>Figura:</b> otto immagini (uccello su un ramo, coltello, edificio, giraffe, barca a vela, bicicletta, persona sul divano, aereo) affiancate dalle <b>mappe di attenzione</b> del token [CLS] nell'ultimo strato: le zone chiare seguono la sagoma dell'oggetto principale.</p>
<ul>
<li><b>Struttura degli oggetti</b>: alcune teste di attenzione evidenziano le regioni degli oggetti <b>senza mai aver visto maschere di segmentazione</b>.</li>
<li><b>Similarità semantica</b>: le rappresentazioni permettono un ottimo <b>k-NN</b> con immagini di riferimento etichettate (articolo: ViT-S/16 74,5% k-NN e 77,0% linear su ImageNet; ViT-B/8 77,4% e 80,1%).</li>
</ul>
<p>Collegamenti: attention map del [CLS] e rollout in <a href="#L18">L18</a>.</p>
<div class="box b"><b>Dal libro · {C31}, § 31.3.2 Affinity-Based Segmentation</b>
<p>Il libro usa DINO per segmentare: si calcolano le feature <b>densamente</b> (una per patch) ottenendo una mappa H × W × D in cui patch che «stanno insieme» hanno vettori vicini; poi si applica <b>k-means</b> ai vettori della mappa e ogni cluster diventa un segmento (fig. 31.7). L'idea: il metodo SSL ha imparato un'<b>affinità</b> dalle co-occorrenze delle patch nelle immagini naturali, e un algoritmo di clustering qualsiasi la trasforma in segmentazione. Il libro accomuna DINO a SimCLR e MoCo come metodi «contrastivi» che avvicinano patch della stessa immagine e allontanano quelle di immagini diverse: per DINO è vero solo in senso lato, perché <b>non usa negativi</b> espliciti (il ruolo dei negativi lo fa il centering).</p>
<p>Collegamento con § 30.5.1: come i rilevatori di oggetti emergono in una CNN addestrata a classificare scene, le maschere di oggetti emergono nell'attenzione di un ViT addestrato senza etichette.</p></div>
"""), printed=P(46))

s(47, "DINOv2: curated data at scale", R("""
<p><b>LVD-142M</b>: 142 milioni di immagini (Oquab et al. 2023).</p>
<p>Pipeline: <b>grande pool web</b> → <b>rimozione dei duplicati</b> → <b>retrieval visivo</b> → <b>dataset curato</b>.</p>
<p>Il self-supervised elimina il bisogno di etichette, ma <b>quali immagini</b> si usano conta ancora.</p>
<div class="box k"><b>Da saper dire: perché curare dati senza etichette</b><p>Un pool web non curato è dominato da poche categorie (prodotti, persone, testi, meme) e da quasi-duplicati: un metodo SSL ci spenderebbe gran parte della capacità. Nell'articolo il retrieval usa dataset curati (ImageNet e altri) come <b>query</b>: per ogni immagine dei dataset di riferimento si recuperano dal pool le immagini più simili nello spazio delle feature di un modello già addestrato. Così il dataset finale è grande, vario e <b>bilanciato</b> verso concetti utili, senza nessuna etichetta. È la «diversità dei dati» della slide 42 messa in pratica.</p></div>
"""), printed=P(47))

s(48, "DINOv2: global + local objective", R("""
<table>
<tr><th>Loss DINO (teacher)</th><th>Loss di ricostruzione mascherata</th></tr>
<tr><td>far coincidere uscite a livello di immagine di student e teacher su ritagli diversi</td><td>mascherare patch dello student e predire le uscite del teacher in quelle posizioni</td></tr>
<tr><td>favorisce una buona rappresentazione <b>globale</b></td><td>favorisce buone feature <b>locali</b> delle patch</td></tr>
<tr><td>calcolata sul token <b>[CLS]</b></td><td>calcolata sui <b>token delle patch</b></td></tr>
</table>
<span class="f">L<sub>main</sub> = L<sub>DINO</sub> + L<sub>masked</sub></span>
<p>Unisce apprendimento globale e locale. I bersagli mascherati sono <b>uscite del teacher</b>, non pixel.</p>
<div class="box x"><b>Precisazioni sull'articolo</b><ul>
<li>Il termine «masked reconstruction» è la loss di <b>iBOT</b>: non si ricostruiscono pixel ma le <b>distribuzioni del teacher</b> (softmax su prototipi) nelle posizioni mascherate, che il teacher vede invece intere. È il «predire feature» della slide 30, come JEPA.</li>
<li>L'obiettivo completo ha anche un regolarizzatore <b>KoLeo</b>, che spinge le feature del batch a distribuirsi uniformemente (come il termine di uniformity del libro, § 30.10.1), e sostituisce il centering di DINO con una normalizzazione Sinkhorn-Knopp. Patch 14 × 14.</li>
<li>È la risposta alla slide 40: global (stile contrastivo, separabile) + locale (stile MIM, denso) nello stesso modello.</li>
</ul></div>
"""), printed=P(48))

s(49, "DINOv2: distilling a large model", R("""
<p><b>Figura:</b> un <i>large frozen model</i> (verde) produce <i>soft targets</i>; uno <i>smaller model, trainable</i> (arancione) produce <i>predictions</i>; fra le due una <i>distillation loss</i>.</p>
<ol>
<li>Si addestra un grande modello SSL.</li>
<li>Lo si <b>congela</b> come teacher.</li>
<li>Si addestra uno <b>student più piccolo</b> a riprodurne le uscite su immagini non etichettate.</li>
</ol>
<p>Le uscite del teacher sono la supervisione; solo lo student riceve aggiornamenti.</p>
<p>Si trasferisce conoscenza in una backbone più economica. Qui il teacher è <b>fisso</b>, a differenza del teacher EMA.</p>
<div class="box b"><b>Dal libro · {C37}, § 37.4.1 Knowledge distillation</b>
<p>È la distillazione nel senso originale (Hinton et al. 2015): teacher già addestrato e fisso, student che ne imita la pmf. Szeliski (§ 5.4.7) ricorda che nasce come <i>model compression</i> per ottenere modelli più piccoli, proprio l'uso di DINOv2. Differenza da ricordare: in BYOL e DINO il teacher <b>cambia</b> (EMA dello student) e non è più bravo in partenza; qui il teacher è <b>più grande e già migliore</b>.</p></div>
"""), printed=P(49))

s(50, "DINOv2: a family of reusable backbones", R("""
<table>
<tr><th>Backbone</th><th>Parametri</th><th>Come si ottiene</th></tr>
<tr><td>ViT-S/14</td><td>21 milioni</td><td>distillato da ViT-g</td></tr>
<tr><td>ViT-B/14</td><td>86 milioni</td><td>distillato da ViT-g</td></tr>
<tr><td>ViT-L/14</td><td>300 milioni</td><td>distillato da ViT-g</td></tr>
<tr><td><b>ViT-g/14</b></td><td><b>1,1 miliardi</b></td><td>addestramento SSL su larga scala</td></tr>
</table>
<p>Si addestra in grande, poi si distillano modelli più piccoli: si sceglie la backbone che entra nel budget dell'applicazione. Il «/14» è la dimensione della patch.</p>
<div class="box k"><b>Da saper fare</b><p>Rapporto di taglia fra teacher e student più piccolo: 1,1 · 10<sup>9</sup> / 21 · 10<sup>6</sup> ≈ <b>52</b>. Un forward costa circa in proporzione ai parametri (a parità di token): ViT-S è circa 50 volte più economico di ViT-g. A 224 × 224 con patch 14 i token sono 16 × 16 = 256 per tutti i modelli della famiglia.</p></div>
"""), printed=P(50))

s(51, "Application of DINOv2: Depth Anything", R("""
<p>Stimare una <b>mappa di profondità densa da una sola immagine RGB</b> (Yang et al., CVPR 2024).</p>
<p><b>Figura:</b> sei immagini molto diverse (camino in un interno, tavolata, scena notturna, palazzo, città nella nebbia, vista aerea) con le rispettive mappe di profondità sotto (giallo = vicino, viola = lontano).</p>
<p>Pipeline: <b>encoder DINOv2</b> → <b>testa decoder</b> per la profondità → mappa di profondità.</p>
<p>Encoder e decoder si adattano con <b>supervisione di profondità</b> e <b>pseudo-etichette</b>.</p>
<p>DINOv2 fornisce le feature visive; l'addestramento specifico le trasforma in profondità.</p>
<div class="box x"><b>Approfondimento: la ricetta di Depth Anything</b><ul>
<li>Decoder <b>DPT</b> (<a href="#L19">L19</a>) sopra un encoder DINOv2; uscita: profondità <b>relativa</b> (inversa, a meno di scala e traslazione), come MiDaS in <a href="#L17">L17</a>.</li>
<li>Un teacher addestrato su circa 1,5 milioni di immagini etichettate genera <b>pseudo-etichette</b> su circa 62 milioni di immagini non etichettate; lo student si addestra su entrambe, con perturbazioni forti sulle non etichettate (così non si limita a copiare il teacher).</li>
<li>Una loss in più mantiene le feature dello student vicine a quelle del DINOv2 congelato, per conservare la semantica.</li>
</ul></div>
<div class="box b"><b>Dal libro · {C43}, § 43.4 Supervised Methods for Depth from a Single Image</b>
<p>Il libro tratta la profondità monoculare come <b>regressione per pixel</b> con un encoder-decoder; i dati vengono da sensori (Kinect per NYUv2, LiDAR per KITTI) o da stereo e struttura da movimento (MegaDepth). Spiega l'ambiguità di scala (da una sola immagine la profondità si conosce a meno di un fattore globale), quindi le loss invarianti alla scala e la stima nel logaritmo o nell'inverso della profondità. Nota: la loss «scale-invariant» del § 43.4.2 scritta senza logaritmi toglie solo una traslazione; la versione invariante alla scala è sui logaritmi (Eigen et al. 2014). Il libro chiude dicendo che i metodi attuali si basano su enormi quantità di dati: Depth Anything è esattamente questo, e il foundation model fornisce le feature.</p></div>
"""), printed=P(51))

s(52, "DINOv3 scales both data and capacity", R("""
<ul>
<li><b>7B parametri</b> nel grande teacher ViT (Siméoni et al. 2025; l'articolo lo chiama ViT-7B, circa 6,7 miliardi effettivi, patch 16).</li>
<li><b>1,689 miliardi di immagini</b> nel dataset web curato (LVD-1689M).</li>
</ul>
<p>Di nuovo una famiglia di modelli distillati (ViT da S a H+ e anche ConvNeXt) per budget di inferenza più piccoli.</p>
<p>A questa scala, <b>preservare la qualità delle feature dense</b> diventa un problema di addestramento a sé.</p>
<div class="box k"><b>Da saper fare: gli ordini di grandezza</b><p>Da DINOv2 a DINOv3: dati 142 M → 1689 M (circa <b>12×</b>), teacher 1,1 B → 7 B parametri (circa <b>6×</b>). Rispetto a ImageNet-1k (1,28 M immagini) LVD-1689M è oltre 1300 volte più grande.</p></div>
"""), printed=P(52))

s(53, "Dense feature degradation", R("""
<p><b>Figura (fig. 6 dell'articolo, ritagliata):</b> due immagini (pecore su un prato, fiore giallo); per ognuna la mappa di similarità coseno fra la patch di riferimento (rossa) e tutte le altre, a 200k, 400k, 600k, 800k e 1M iterazioni. All'inizio la similarità alta è concentrata sull'oggetto della patch; andando avanti le mappe diventano <b>rumorose</b> e la similarità si spande su patch che non c'entrano.</p>
<p><b>Problema</b>: le feature dense <b>degradano</b> anche se la loss continua a scendere, perché l'obiettivo globale (token [CLS]) e quello locale (token delle patch) <b>competono</b>.</p>
<div class="box k"><b>Da saper dire</b><p>Una loss che scende non garantisce rappresentazioni migliori (slide 9): qui le prestazioni globali (classificazione) migliorano con l'addestramento lungo, mentre quelle dense (segmentazione, profondità) peggiorano. Per accorgersene bisogna <b>misurare</b> i compiti densi durante l'addestramento, non solo la loss.</p></div>
"""), printed=P(53))

s(54, "Gram anchoring for dense features", R("""
<p>Idea: tenere fisso <b>quali patch si somigliano</b>, anche se le feature stesse continuano a cambiare.</p>
<span class="f">G = X X<sup>⊤</sup>   (G<sub>ij</sub> = similarità fra la patch i e la patch j)</span>
<span class="f">L<sub>Gram</sub> = ∑<sub>i,j</sub> (G<sub>ij</sub><sup>student</sup> − G<sub>ij</sub><sup>teacher</sup>)²</span>
<ul>
<li><b>Cosa</b>: far coincidere la mappa di similarità fra patch dello student con una precedente, «buona».</li>
<li><b>Perché</b>: la riga è troncata nella slide («Why: keep.»). Il senso, dall'articolo: <b>conservare la struttura di similarità locale</b> delle feature dense di quando erano buone, lasciando libere le feature di migliorare per l'obiettivo globale.</li>
<li><b>Teacher</b>: un checkpoint <b>precedente</b> con feature dense nette, aggiornato periodicamente (non il teacher EMA di ogni passo).</li>
</ul>
<div class="box k"><b>Da saper fare: cosa vincola e cosa lascia libero la matrice di Gram</b>
<p>X ha una riga per patch (P × D, feature normalizzate L2 nell'articolo, quindi G<sub>ij</sub> è una similarità coseno). Esempio con 3 patch e D = 2: x<sub>1</sub> = (1, 0), x<sub>2</sub> = (1, 0), x<sub>3</sub> = (0, 1). G = [[1, 1, 0], [1, 1, 0], [0, 0, 1]]: le patch 1 e 2 «stanno insieme», la 3 no.</p>
<p>Se le feature ruotano tutte di 90° (x<sub>1</sub> = x<sub>2</sub> = (0, 1), x<sub>3</sub> = (−1, 0)), G non cambia: (XR)(XR)<sup>⊤</sup> = X R R<sup>⊤</sup> X<sup>⊤</sup> = XX<sup>⊤</sup> per R ortogonale. Quindi la loss di Gram vincola solo le <b>relazioni</b> fra patch, non le feature: lo student può cambiare le feature (per esempio per migliorare il [CLS]) purché non rovini chi somiglia a chi. Se invece la patch 3 diventasse simile alle altre (x<sub>3</sub> = (1, 0)), G<sub>13</sub> passerebbe da 0 a 1 e la loss crescerebbe di 2 · 1² (G<sub>13</sub> e G<sub>31</sub>) + 2 (G<sub>23</sub> e G<sub>32</sub>) = 4.</p></div>
<div class="box x"><b>Approfondimento</b><p>Nell'articolo la Gram anchoring entra solo in una fase tardiva (dopo circa 1 milione di iterazioni, cioè quando la degradazione è già cominciata) e ripara anche feature già rovinate. Il nome viene dalla matrice di Gram usata nel trasferimento di stile (Gatys et al.), dove però si confrontano correlazioni fra canali, non fra patch.</p></div>
"""), printed=P(54))

s(55, "DINOv3 in earth observation", R("""
<p>Pipeline: <b>immagini satellitari RGB</b> → <b>backbone SSL satellitare</b> → <b>testa di regressione densa</b> addestrata → <b>mappa dell'altezza della chioma</b> (canopy height).</p>
<ul>
<li>Pretraining di dominio: <b>SAT-493M</b>, 493 milioni di immagini satellitari.</li>
<li>Supervisione della testa: altezze bersaglio da dati <b>LiDAR</b>.</li>
<li>Il trasferimento fra domini dipende da sensori, geografia e compito.</li>
</ul>
<p>L'SSL dà feature spaziali riutilizzabili; la testa supervisionata assegna <b>significato fisico e unità</b> (metri).</p>
<div class="box k"><b>Da saper dire</b><p>È lo schema della slide 7 in un dominio diverso: le immagini satellitari hanno statistiche lontane dalle foto web (vista dall'alto, scala, nessun orizzonte), quindi conviene un pretraining SSL <b>sul dominio</b> stesso, possibile proprio perché non servono etichette. Le etichette (LiDAR) servono solo alla testa, e sono poche e costose. Il LiDAR è lo stesso sensore a tempo di volo del libro (§ 43.4.1).</p></div>
"""), printed=P(55))

s(56, "JEPA: why predict representations?", R("""
<table>
<tr><th>Ricostruzione di pixel</th><th>Predizione di rappresentazioni</th></tr>
<tr><td>predire <b>come appare</b> una regione mancante</td><td>predire le <b>feature</b> di una regione mancante</td></tr>
<tr><td>recuperare colori, texture e dettagli fini</td><td>far coincidere una descrizione appresa del contenuto</td></tr>
</table>
<ul>
<li>I dettagli esatti dei pixel possono essere <b>ambigui o irrilevanti</b> per i compiti a valle (le foglie di un albero dietro una maschera: la forma esatta è imprevedibile, che sia un albero no).</li>
<li>Predire nello spazio delle feature permette di imparare la struttura visiva <b>senza generare un'immagine</b>.</li>
</ul>
<p>Si impara un encoder predicendo nello <b>spazio delle rappresentazioni</b>, poi se ne riusano le feature.</p>
<div class="box k"><b>Da saper dire: JEPA fra le due famiglie</b><p>JEPA (<i>Joint-Embedding Predictive Architecture</i>, proposta da LeCun) prende il <b>mascheramento</b> dal MIM e il <b>bersaglio nello spazio delle feature con teacher EMA</b> da BYOL e DINO. Rispetto a MAE non spreca capacità sui dettagli imprevedibili (con la MSE sui pixel la predizione ottimale di un dettaglio incerto è la media, cioè una macchia sfocata). Rispetto ai metodi a due viste non dipende da augmentation scelte a mano, che codificano le invarianze desiderate (libro § 30.10.2). Il prezzo: il bersaglio è appreso, quindi il collasso torna possibile e serve di nuovo l'asimmetria (predictor, stop-gradient, EMA).</p></div>
"""), printed=P(56))

s(57, "I-JEPA: predict missing image features", R("""
<p><b>I-JEPA</b> (Assran et al., CVPR 2023). <b>Figura (dall'articolo):</b> a sinistra un blocco di <i>contesto</i> dell'immagine (con le zone bersaglio tolte) entra nel <i>context encoder</i> f<sub>θ</sub>; un <i>predictor</i> g<sub>φ</sub>, ricevendo anche le posizioni dei blocchi bersaglio (blu, rosso, giallo), predice le loro feature; in basso l'immagine intera entra nel <i>target encoder</i> f<sub>θ̄</sub>, e le sue feature nelle stesse posizioni sono confrontate con le predizioni con una loss L<sub>2</sub>.</p>
<ol>
<li>Si codifica il <b>contesto visibile</b> con un ViT.</li>
<li>Si predicono le feature dei <b>blocchi bersaglio nascosti</b>, usando le loro posizioni.</li>
<li>Si confrontano con le feature di un <b>target encoder EMA</b> che vede l'immagine intera.</li>
</ol>
<span class="f">L ∝ ∑<sub>i∈M</sub> ‖ẑ<sub>i</sub> − sg(z<sub>i</sub><sup>t</sup>)‖²</span>
<p>M = posizioni bersaglio. Il bersaglio è un <b>vettore di feature</b>, non pixel RGB. A valle si tiene l'encoder e si addestra una testa adatta.</p>
<div class="box x"><b>Approfondimento: la strategia di mascheramento</b><p>Nell'articolo i bersagli sono 4 blocchi abbastanza grandi (ciascuno circa il 15–20% dell'immagine) e il contesto è un blocco grande (85–100%) a cui si tolgono le zone bersaglio. Blocchi grandi costringono a predire contenuto <b>semantico</b> (una parte di un oggetto) invece di dettagli locali. Nessuna augmentation forte: basta una vista.</p></div>
"""), printed=P(57))

s(58, "V-JEPA: learning from video", R("""
<p><b>Figura (V-JEPA 2, fig. 2):</b> a sinistra il pretraining su video: fotogrammi mascherati entrano nell'<i>encoder</i>, un <i>predictor</i> con i token di maschera predice le feature, confrontate con loss L1 con quelle di un <i>ema encoder</i> che vede i fotogrammi interi (con stop-gradient). A destra l'estensione condizionata alle azioni: un <i>frozen encoder</i> codifica i fotogrammi passati e futuri di un braccio robotico; il predictor riceve anche le <b>azioni e pose del robot</b> e predice le feature del fotogramma futuro, sempre con loss L1.</p>
<ul>
<li><b>Pretraining su video</b>: predire le feature di regioni nascoste <b>nello spazio e nel tempo</b> (V-JEPA, Bardes et al. 2024).</li>
<li><b>Estensione condizionata alle azioni</b> (V-JEPA 2, Assran et al. 2025): si congela l'encoder e si addestra una nuova testa a predire feature future da osservazioni passate e <b>azioni del robot</b>. È un modello del mondo appreso nello spazio delle feature, utilizzabile per pianificare.</li>
</ul>
<div class="box b"><b>Dal libro · {C30}, § 30.3.2 Prediction</b>
<p>Il libro mette la <b>predizione del futuro</b> fra le proprietà che definiscono una buona rappresentazione: lo scopo di un sistema visivo è agire per ottenere risultati futuri desiderati, quindi la rappresentazione deve essere un buon substrato per predire e decidere (anche «actionable», utilizzabile per il controllo). V-JEPA 2 con le azioni del robot è esattamente questo.</p></div>
"""), printed=P(58))

s(59, "Further reading", R("""
<ul>
<li><b>DINOv3: Self-supervised learning for vision at unprecedented scale</b> (Meta AI, 2025, post sul blog): panoramica di DINOv3, della scalabilità del SSL e delle applicazioni delle feature preaddestrate.</li>
<li><b>A Cookbook of Self-Supervised Learning</b> (Balestriero et al., 2023, survey e guida pratica): riferimento sulle famiglie di metodi, le ricette di addestramento e la valutazione delle rappresentazioni.</li>
</ul>
<p>Per l'esame il riferimento sono il libro (cap. 30 e 37, più § 31.3.2) e queste schede; il Cookbook è utile se si vuole approfondire una famiglia di metodi in particolare (contiene le tabelle con gli iperparametri tipici). Il prossimo passo pratico è il lab sull'SSL annunciato nella <a href="#L21">L21</a>.</p>
"""), printed=P(59))
