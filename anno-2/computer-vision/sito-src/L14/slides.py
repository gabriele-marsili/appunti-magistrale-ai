def C(k): return f' <em>· CoEvolution {k}/16</em>'
def B(k): return f' <em>· Brau pag. {k}</em>' if k else ' <em>· Brau, copertina</em>'
def P(k): return f' <em>· Pilot 2 {k}/15</em>'
VB = 'https://visionbook.mit.edu/'
def L(slug, txt): return f'<a href="{VB}{slug}" target="_blank">{txt}</a>'

# ===================== PARTE 1: CoEvolution (pagine 1-16) =====================

s(1, "CoEvolution: copertina", """
<p><b>A Comprehensive Trustworthy Framework for Connected Machine Learning and Secure Interconnected AI Solutions</b>: il nome esteso del progetto europeo <b>CoEvolution</b>. Relatore Nikolaos Koroniotis (NTUA, Atene); progetto finanziato da Horizon Europe (grant agreement n. 101168560).</p>
<p>La lezione è un <b>seminario ospite</b> fatto di tre presentazioni, unite in questo PDF:</p>
<ul>
<li><b>Pagine 1–16</b>: panoramica del progetto CoEvolution (sicurezza, fiducia e robustezza dei sistemi di AI).</li>
<li><b>Pagine 17–51</b>: <b>Adversarial Examples</b>, di Fabio Brau (Università di Cagliari): è la parte tecnica e quella da studiare davvero.</li>
<li><b>Pagine 52–66</b>: il <b>Pilot 2</b> del progetto (veicoli autonomi), con un caso concreto di attacco avversario alla segmentazione LiDAR e una difesa per purificazione.</li>
</ul>
<p>Legame con il corso: finora le reti (L7 in poi, e poi stereo e profondità in L13) sono state viste come strumenti che funzionano. Qui si guarda il rovescio: quanto è facile <b>ingannarle</b> con modifiche dell'input invisibili all'occhio, e come difendersi.</p>
""", sec=("l14-coevo", "Il progetto CoEvolution", "slide 1–12"), printed=C(1))

s(2, "CoEvolution Key Facts", """
<ul>
<li>Durata <b>36 mesi</b>: dal 1 novembre 2024 al 31 ottobre 2027.</li>
<li>Bando HORIZON-CL3-2023-CS-01-03 (cluster 3, cybersecurity); tipo di azione <b>RIA</b> (Research and Innovation Action).</li>
<li>Budget circa <b>6 milioni di euro</b> (5.999.688,75 €); coordinatore <b>ICCS</b> (Institute of Communication and Computer Systems, Atene).</li>
</ul>
<p>Sono dati di contesto: non servono per l'esame.</p>
""", printed=C(2))

s(3, "Consortium", """
<ul>
<li><b>15 partner da 8 paesi</b>: Grecia, Italia, Germania, Spagna, Irlanda, Austria, Cipro, Svizzera.</li>
<li><b>5 partner di ricerca</b>: ICCS, ISI, UNICA (Cagliari, da cui viene il seminario di Brau), Upatras, <b>UNIPI</b> (Pisa).</li>
<li><b>7 PMI</b> (AEGIS, SLC, AVI, DIE, CBRL, STS, BEVD) e <b>3 grandi aziende</b> (Siemens, Telefónica Innovación Digital, AVL).</li>
</ul>
<p><b>Figura</b>: i loghi dei partner (fra cui Siemens, AEGIS, Telefónica, AVL, AVISENSE, Sphynx, Beevadoo, Università di Patrasso). AVL e AVISENSE sono i partner del Pilot 2 (pagina 52).</p>
""", printed=C(3))

s(4, "Motivation", """
<ul>
<li>Il mercato dell'AI cresce rapidamente (la slide stima oltre ~2000 miliardi di dollari entro il 2032).</li>
<li>Sistemi di AI <b>interconnessi</b> (modelli che si passano dati e decisioni) amplificano il rischio di attacchi <b>a cascata</b> di due tipi:
<ul><li><b>evasione</b> (evasion): si modifica l'input al momento dell'uso per far sbagliare il modello già addestrato; gli esempi avversari della seconda parte sono attacchi di evasione;</li>
<li><b>avvelenamento</b> (poisoning): si manipolano i dati di addestramento perché il modello impari qualcosa di sbagliato.</li></ul></li>
<li>Modelli senza <b>consapevolezza del contesto</b> sono più vulnerabili ad attacchi avversari sottili.</li>
<li>Le librerie esistenti per la sicurezza dei modelli (<b>Foolbox, CleverHans, IBM ART, SecML</b>) implementano attacchi e difese, ma secondo la slide manca un <b>flusso unificato</b> di valutazione della sicurezza.</li>
</ul>
""", printed=C(4))

s(5, "Vision", """
<p>Obiettivo del progetto: una soluzione <b>end-to-end</b> per valutare <b>Security, Trust and Robustness (STR)</b> dei modelli di AI.</p>
<ul>
<li>Produrre modelli <b>context-aware</b> (slide 12).</li>
<li>Descrivere ogni modello con un <b>AI Model Bill of Materials</b> (AI MBOM, slide 11).</li>
<li>Integrarsi con le pratiche <b>MLDevOps</b> (sviluppo e messa in produzione continui dei modelli) e con il quadro normativo europeo sull'AI.</li>
</ul>
""", printed=C(5))

s(6, "Ambition", """
<p>Tre filoni di ricerca, sviluppati nelle tre slide successive:</p>
<ol type="A">
<li><b>Rilevazione, prevenzione e mitigazione</b> degli attacchi avversari ai modelli.</li>
<li>Attacchi avversari all'apprendimento collaborativo <b>peer-to-peer</b> (P2P) e <b>federato</b> (FL).</li>
<li><b>Supporto alle decisioni</b> per mitigare le minacce, tenendo conto del contesto e di più obiettivi in conflitto.</li>
</ol>
""", printed=C(6))

s(7, "A. Detection, Prevention and Mitigation of Adversarial Attacks on AI models", """
<ul>
<li>I modelli di ML funzionano bene in visione, riconoscimento vocale, rilevamento di malware, ma sono <b>vulnerabili</b> ad attacchi costruiti ad arte:
<ul><li><b>poisoning</b>: dati di training manipolati;</li>
<li><b>backdoor</b>: un trigger nascosto (ad esempio un piccolo adesivo) inserito in training, che fa dare al modello un'uscita scelta dall'attaccante solo quando il trigger è presente;</li>
<li><b>information retrieval</b>: estrarre informazioni sul modello o sui dati di training (ad esempio model extraction, slide 54);</li>
<li><b>DoS</b>: degradare il servizio.</li></ul></li>
<li>Limiti delle difese esistenti: richiedono <b>competenze di sicurezza</b> approfondite e sono <b>costose</b> da calcolare (l'adversarial training della slide 47 moltiplica il costo dell'addestramento).</li>
<li>CoEvolution vuole integrare <b>test e difese</b> nei flussi di sviluppo industriali e automotive.</li>
</ul>
""", printed=C(7))

s(8, "B. Adversarial attacks on P2P and FL collaborative learning", """
<ul>
<li>L'ML tradizionale è <b>centralizzato</b>: tutti i dati vanno su un server. Costi di memoria e banda, problemi di <b>privacy</b>, latenza.</li>
<li>Il <b>federated learning</b> (FL) tiene i dati sui client: ognuno addestra localmente e manda al server solo gli aggiornamenti dei pesi, che il server media (FedAvg). Limiti secondo la slide:
<ul><li>il server centrale è un <b>single point of failure</b>;</li>
<li>i client devono <b>fidarsi</b> ciecamente dell'autorità centrale a cui mandano informazioni.</li></ul></li>
<li>Proposta del progetto: <b>P4L</b>, un sistema di apprendimento <b>peer-to-peer</b> che preserva la privacy, completamente distribuito e senza infrastruttura: i partecipanti collaborano in modo asincrono e decentralizzato.</li>
</ul>
<p>Il titolo parla di attacchi: in FL e P2P un partecipante malevolo può mandare aggiornamenti avvelenati (model poisoning) o inserire backdoor nel modello comune.</p>
""", printed=C(8))

s(9, "C. Context-aware decision support for threat mitigation using multi-objective criteria", """
<ul>
<li>Il <b>reinforcement learning</b> ha avuto successo in robotica, sistemi intelligenti, progettazione di chip.</li>
<li>Molti problemi reali però hanno <b>più obiettivi in conflitto</b> (sicurezza, costo, prestazioni), che l'RL standard con una sola ricompensa scalare non gestisce in modo naturale.</li>
<li>CoEvolution formula il supporto alle decisioni come un <b>problema di raccomandazione</b>:
<ul><li>un framework di decisione multi-obiettivo;</li>
<li>scegliere l'azione di mitigazione migliore fra quelle candidate;</li>
<li>etichettare le azioni come positive o negative per addestrare un agente decisionale.</li></ul></li>
</ul>
""", printed=C(9))

s(10, "CoEvolution: A Multilayer Hub for Secure & Trusted AI", """
<ul>
<li>Strumenti e servizi per: <b>robustificazione</b> dei modelli, valutazione e garanzia di sicurezza, raccolte (pool) di modelli e dataset <b>fidati</b>, meccanismi per costruire AI sicura.</li>
<li>La sicurezza è affrontata da tre punti di vista:
<ul><li><b>ciclo di vita</b> del modello, dalla progettazione alla messa in produzione;</li>
<li><b>supply chain</b> dell'AI: singoli modelli, apprendimento federato o decentralizzato, catene di fornitura (modelli pre-addestrati e dataset presi da terzi);</li>
<li>garanzia di sicurezza e fiducia per tutti i tipi di modello.</li></ul></li>
</ul>
""", printed=C(10))

s(11, "AI Model Bill of Materials (AI MBOM)", """
<ul>
<li>Ispirato al <b>Software Bill of Materials</b> (SBOM: l'elenco dei componenti e delle dipendenze di un software), arricchito con: <b>provenienza dei dati</b>, <b>comportamento del modello</b>, conformità etica.</li>
<li>Descrive dataset, dipendenze, proprietari, utenti e informazioni di sicurezza del modello.</li>
<li>Fa da <b>portatore di credenziali</b> lungo tutto il ciclo di vita del modello.</li>
<li>Rende trasparenti robustezza, fiducia, spiegabilità ed equità.</li>
</ul>
<p>Perché serve: chi usa un modello pre-addestrato preso da terzi non sa su quali dati è stato addestrato né se è stato manomesso (backdoor, slide 7). L'MBOM è la «carta d'identità» verificabile del modello.</p>
""", printed=C(11))

s(12, "Context Awareness", """
<ul>
<li>I modelli acquisiscono <b>consapevolezza dell'ambiente</b> tramite embedding <b>cross-modali</b> (rappresentazioni comuni a più modalità, ad esempio immagini e testo, o sensori diversi).</li>
<li>Consentono comportamenti <b>adattivi</b> in base al contesto in cui il modello è messo in uso.</li>
<li>I meccanismi di contesto sono «infusi» nei modelli nella fase di deployment, tramite gli strumenti e i servizi del progetto.</li>
</ul>
""", printed=C(12))

s(13, "Pilots", "<p>I due casi d'uso del progetto: Pilot 1 (manifattura) e Pilot 2 (veicoli autonomi).</p>", kind="div", sec=("l14-coevo-pilot", "CoEvolution: i pilot", "slide 13–16"), printed=C(13))

s(14, "Pilot 1: Securing the AI Supply Chain of Manufacturing Infrastructure", """
<p><b>Obiettivo</b>: sicurezza e affidabilità dei componenti di AI usati nell'<b>edge computing</b> per l'automazione industriale.</p>
<ul>
<li>Verificare l'<b>integrità</b> dei componenti di AI forniti da terzi nelle applicazioni di fabbrica.</li>
<li>Misure di fiducia perché i modelli si comportino come previsto nei flussi produttivi.</li>
<li>Proteggere i modelli installati su dispositivi edge e l'infrastruttura edge dagli attacchi avversari.</li>
</ul>
<p><b>Figura</b>: un monitor con interfacce di controllo in un ambiente industriale.</p>
""", printed=C(14))

s(15, "Pilot 2: Securing the AI Supply Chain in the Autonomous Vehicles Domain", """
<p><b>Obiettivo</b>: resilienza e sicurezza dei sistemi di AI dei <b>CAV</b> (Connected and Autonomous Vehicles) per una navigazione autonoma sicura.</p>
<ul>
<li>Test di cyber-resilienza in scenari di <b>valet parking</b> (parcheggio autonomo).</li>
<li>Infrastruttura di test con LiDAR precisi, altri sensori e mappe ad alta qualità.</li>
<li><b>Percezione cooperativa</b> fra veicoli e pianificazione dei percorsi multi-agente.</li>
<li>Tecniche di sicurezza contro il <b>data poisoning</b> e la manipolazione dei sensori.</li>
</ul>
<p><b>Figura</b>: vista dall'alto di una strada con auto evidenziate da cerchi luminosi (veicoli connessi). Il pilot è ripreso in dettaglio nella terza parte (pagine 52–66).</p>
""", printed=C(15))

s(16, "Contatti del progetto", """
<p>Sito del progetto (coevolution-project.eu) e account social (X, Facebook, Bluesky, LinkedIn, YouTube). Fine della prima presentazione.</p>
""", printed=C(16))

# ===================== PARTE 2: Adversarial Examples, F. Brau (pagine 17-51) =====================

s(17, "Adversarial Examples – Machine Learning Security", "<p>Seminario di Fabio Brau (Dipartimento di Ingegneria Elettrica ed Elettronica, Università di Cagliari), nell'ambito di CoEvolution.</p>", kind="div", sec=("l14-brau", "Esempi avversari: introduzione", "slide 17–25"), printed=B(0))

s(18, "Indice", """
<p>Tre parti:</p>
<ol>
<li><b>Introduzione, definizioni e tassonomia</b> (slide 19–35): cosa sono gli esempi avversari, come si misura la perturbazione (norme l<sub>p</sub>), come si classificano gli attacchi.</li>
<li><b>Generazione degli esempi avversari</b> (slide 36–47): gli attacchi come problemi di ottimizzazione, FGSM, L-BFGS, Carlini-Wagner, PGD, e la difesa con adversarial training.</li>
<li><b>Conclusioni</b> (slide 48–50).</li>
</ol>
<p>Nota: il deck è un <b>estratto</b> di una lezione più lunga, quindi i numeri di pagina stampati saltano (28 → 30 → 35 → 36 → 47). Nelle schede è indicato il numero stampato vero.</p>
""", printed=B(2))

s(19, "Neural Networks achieve Human Performances…", """
<p><b>Figura</b>: tre tappe storiche.</p>
<ul>
<li><b>LeNet-5</b> su MNIST (1998): riconoscimento di cifre scritte a mano (l'interfaccia mostra la cifra 0 riconosciuta).</li>
<li><b>AlexNet</b> su ImageNet: una griglia di immagini di ImageNet. La slide scrive 2013; AlexNet è del 2012 (vittoria di ILSVRC 2012).</li>
<li><b>YOLO</b> (2016): rilevamento di oggetti, con riquadri attorno a un cane, una bicicletta e un'auto.</li>
</ul>
<p>Messaggio: le reti raggiungono prestazioni paragonabili a quelle umane in classificazione e detection. La slide successiva mostra il rovescio della medaglia.</p>
""", printed=B(3))

s(20, "… but they make weird mistakes.", """
<ul>
<li><b>Sinistra, evasione di un filtro antispam (2010)</b>: due email di spam («FIRECRACKER STOCK ALERT!!!»), una bloccata (X rossa) e una che passa (spunta verde). Il filtro usa l'<b>OCR</b>; l'attaccante modifica l'immagine del testo quanto basta per sfuggire. Gli attacchi ai classificatori sono studiati in sicurezza da prima del deep learning: Dalvi et al. 2004 (<i>Adversarial Classification</i>; la slide scrive «Delvi») e Biggio et al. 2010.</li>
<li><b>Destra, attacchi alle immagini (2014)</b>: tre righe (scuolabus, cane, tempio) con immagine originale, perturbazione amplificata e immagine perturbata. Le immagini perturbate, identiche a occhio, non sono più riconosciute dalla rete (Szegedy et al. 2013, <i>Intriguing properties of neural networks</i>).</li>
</ul>
<div class="box b"><b>Dal libro · cap. 24, § 24.5.4 Identifying Vulnerabilities</b><p>Il libro costruisce un esempio avversario <b>a mano</b> su una CNN piccolissima addestrata a distinguere righe orizzontali e verticali. Guardando i filtri appresi scopre che la rete non cerca «linee» ma guarda dove sta l'<b>energia nel dominio di Fourier</b>. Allora moltiplica un'immagine di righe orizzontali per una sinusoide: la <b>modulazione</b> (L3, cap. 16) sposta lo spettro nella zona che la rete associa alle linee verticali. Per noi le righe restano orizzontali, la rete sbaglia su tutte le immagini. Morale del libro: per reti grandi l'esempio avversario non si progetta a mano ma si trova risolvendo un problema di <b>ottimizzazione</b> (la perturbazione minima che cambia l'uscita), che è esattamente il contenuto delle slide 37–46. ${L24}.</p></div>
""".replace('${L24}', L('convolutional_neural_nets.html', 'Cap. 24')), printed=B(4))

s(21, "Adversarial Examples", """
<p><b>Figura</b> (Goodfellow et al. 2014): l'esempio più famoso. Un panda classificato «panda» con confidenza 57.7%, più 0.007 volte un'immagine di rumore colorato, dà un'immagine identica a occhio classificata «gibbon» con confidenza <b>99.3%</b>.</p>
<ul>
<li><b>Esempi avversari</b>: input progettati <b>intenzionalmente</b> per far sbagliare un modello di ML.</li>
<li>Si possono costruire in modo che appaiano <b>quasi identici</b> agli input normali.</li>
<li>Il rumore non è casuale: è il segno del gradiente della loss (FGSM, slide 39–40), con ε = 0.007 sui pixel normalizzati.</li>
<li>Il modello non solo sbaglia, ma sbaglia con <b>alta confidenza</b>: la confidenza non è una garanzia.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 35, § 35.6.1 Adversarial Attacks</b><p>Il libro tratta gli attacchi come il caso peggiore di <b>spostamento della distribuzione</b> (data shift): dopo i bias dei dataset (§ 35.1–35.5, spostamenti non voluti) arriva lo spostamento <b>malevolo</b>, scelto da un avversario che controlla l'input al momento del test (§ 35.6 Adversarial Shifts). L'attaccante ottimizza un rumore piccolo, vincolato in una palla di raggio r attorno all'immagine, per far uscire la classe che vuole. Nell'esempio del libro (fig. 35.12) una foto di gatto diventa «struzzo» per la rete; il rumore è mostrato amplificato 20 volte. Il libro nota che l'attacco richiede accesso alla rete, e che rendere un sistema pubblico significa darlo in mano anche agli attaccanti. Nota: nella versione online la formula dell'attacco «struzzo» è scritta come argmax della cross-entropy H(y<sub>ostrich</sub>, f(x + ε)); per far uscire la classe obiettivo quella cross-entropy va <b>minimizzata</b> (argmin), come nella colonna targeted della slide 37. ${L35}.</p></div>
""".replace('${L35}', L('bias_and_shift.html', 'Cap. 35')), printed=B(5))

s(22, "Adversarial Examples in Audio Systems", """
<ul>
<li>Anche i modelli <b>speech-to-text</b> si ingannano aggiungendo all'audio un rumore impercettibile.</li>
<li><b>Figura</b> (Carlini e Wagner 2018): la forma d'onda di una frase («without the dataset the article is useless») più un rumore avversario a <b>−30 dB</b> rispetto al segnale dà un audio che a orecchio è uguale, ma che il modello trascrive come «okay google browse to evil dot com».</li>
<li>È un attacco <b>targeted</b> (slide 33): l'attaccante sceglie la trascrizione esatta.</li>
</ul>
<p>Il fenomeno non è legato alle immagini: riguarda qualunque modello differenziabile con input ad alta dimensione.</p>
""", printed=B(6))

s(23, "Adversarial Examples become popular", """
<p><b>Figura</b>: la pagina web di Nicholas Carlini «A Complete List of All (arXiv) Adversarial Example Papers» con un grafico del numero cumulativo di articoli dal 2014 al 2022: cresce in modo esplosivo, fino a circa 6000; accanto un QR code al sito.</p>
<p>Messaggio: dal 2014 gli esempi avversari sono diventati uno dei temi più studiati del machine learning.</p>
""", printed=B(7))

s(24, "Why are adversarial Examples worth studying?", """
<p>Due motivi.</p>
<ul>
<li><b>Minaccia alla sicurezza</b> («know your enemy»): le reti sono usate in compiti sempre più critici. <b>Figura</b> (DeepXplore): due foto di una strada di montagna; nella seconda, solo più scura, il modello di guida DAVE-2 sterza a destra invece di seguire la curva (frecce rosse). Una piccola variazione di luce basta a far sbagliare il volante.</li>
<li><b>Prospettiva fondamentale</b>: <b>Figura</b>: un'immagine di squalo più rumore gaussiano con σ = 0.5 (rumore molto visibile) viene classificata «airplane»; la stessa immagine più una perturbazione avversaria δ quasi nera (impercettibile) viene classificata «ship». La slide non dice l'etichetta dell'immagine pulita; il senso è che il rumore casuale grande non cambia la decisione, quella piccola ma scelta sì.</li>
</ul>
<p>Domanda della slide: perché perturbazioni <b>piccole e malevole</b> bastano a ingannare il modello mentre il <b>rumore gaussiano</b>, molto più grande, no?</p>
<div class="box k"><b>Da capire bene: perché il rumore casuale non basta</b><p>Al primo ordine la loss cambia di ∇L<sup>⊤</sup>δ. Per δ casuale gaussiano con deviazione σ su n pixel, ∇L<sup>⊤</sup>δ ha deviazione standard σ‖∇L‖<sub>2</sub>: i contributi dei pixel hanno segni casuali e in gran parte si cancellano. Per δ = ε·sign(∇L) tutti i contributi hanno lo stesso segno e la variazione è ε‖∇L‖<sub>1</sub>, che a parità di energia per pixel può essere fino a √n volte più grande (quando i |g<sub>i</sub>| sono simili) (con n = 224·224·3 ≈ 150 000, √n ≈ 390). È l'argomento «lineare» di Goodfellow: in alta dimensione tanti cambiamenti minuscoli, tutti nella direzione giusta, si sommano.</p></div>
<div class="box b"><b>Dal libro · cap. 21, § 21.2 Example: Aliasing-Based Adversarial Attack</b><p>Un attacco avversario costruito <b>analiticamente</b>, che lega questa lezione all'aliasing di L6. Il sistema giocattolo è: convoluzione con il filtro derivata [−1, 1], <b>decimazione</b> (si tiene un pixel ogni due, cioè una convoluzione con stride 2), ReLU. L'attaccante prende un'immagine nascosta (un segnale di stop), la moltiplica per (−1)<sup>n</sup>(−1)<sup>m</sup>, cioè la sposta alla frequenza più alta, e la somma all'immagine originale con forza ε = 0.05. A occhio l'immagine attaccata è identica all'originale, ma dopo la decimazione la componente ad alta frequenza si <b>ripiega</b> in banda base (aliasing) e l'uscita mostra lo stop. Il colpevole è il campionamento senza filtro anti-aliasing: le CNN con stride sono esposte allo stesso meccanismo. ${L21}.</p></div>
<div class="box b"><b>Prince · § 20.4.6 Leaving the data manifold</b><p>Prince osserva che gli esempi avversari sono punti <b>vicini ma fuori</b> dalla varietà (manifold) dei dati naturali, dove la rete classifica male. Aggiunge però la spiegazione oggi più accreditata (Ilyas et al. 2019): non sono un difetto di robustezza «fuori dal training», ma sfruttano <b>informazione presente nella distribuzione di training</b> con norma piccola e invisibile agli umani (feature «non robuste» ma predittive). Szeliski (§ 5.4.6) riporta lo stesso risultato: la rete usa correlazioni reali del dataset che a noi sembrano rumore.</p></div>
""".replace('${L21}', L('upsamplig_downsampling_2.html', 'Cap. 21')), printed=B(8))

s(25, "Sensitivity to Input Perturbation", """
<p>Come misurare quanto è «piccola» una perturbazione: il <b>PSNR</b> (Peak Signal to Noise Ratio):</p>
<span class="f">PSNR(x, x<sub>adv</sub>) = 10 · log<sub>10</sub> ( MAX² / ( (1/n) ‖x − x<sub>adv</sub>‖<sub>2</sub>² ) )</span>
<ul>
<li>MAX è il valore massimo di un pixel (1 con pixel in [0, 1], 255 con interi a 8 bit); il denominatore è l'errore quadratico medio (MSE) sugli n pixel.</li>
<li><b>Più dB = perturbazione più piccola</b>: nessuna perturbazione dà ∞ dB.</li>
</ul>
<p><b>Figura</b>: un cartello di limite 30 classificato «30». Senza perturbazione (∞ dB) resta 30; con <b>rumore gaussiano σ = 0.5</b> (6 dB, immagine molto rumorosa) diventa «80»; con una <b>perturbazione avversaria a 40 dB</b> (invisibile) diventa «STOP».</p>
<p><b>Perturbazione avversaria minima</b> (mediana della perturbazione sufficiente a ingannare una rete, ricavata da Rony et al., attacco DDN in norma l<sub>2</sub>): MNIST 25.9 dB, CIFAR-10 52.4 dB, ImageNet 61.9 dB. Le reti su immagini più grandi e dataset più complessi si ingannano con perturbazioni <b>più piccole</b> (più dB).</p>
<div class="box k"><b>Da saper fare: PSNR e norma l<sub>2</sub></b><p>Con pixel in [0, 1]: MSE = ‖δ‖<sub>2</sub>²/n, quindi PSNR = −10 log<sub>10</sub> MSE.</p>
<ul>
<li>Rumore gaussiano σ = 0.5: MSE ≈ σ² = 0.25, PSNR = 10 log<sub>10</sub> 4 ≈ <b>6 dB</b>, come nella figura (trascurando il taglio dei valori in [0, 1]).</li>
<li>40 dB ⇔ MSE = 10<sup>−4</sup> ⇔ scarto quadratico medio 0.01 per pixel, circa 2.5 livelli su 255.</li>
<li>A parità di ‖δ‖<sub>2</sub> il PSNR cresce con n: la stessa energia spalmata su più pixel dà MSE più basso. Per questo i numeri di ImageNet (n ≈ 150 000) sono alti: ad esempio ‖δ‖<sub>2</sub> = 0.3 su 224 × 224 × 3 pixel dà circa 62 dB, mentre ‖δ‖<sub>2</sub> = 1.4 su MNIST (784 pixel) dà circa 26 dB. I due valori di ‖δ‖<sub>2</sub> sono esempi plausibili, scelti per mostrare l'ordine di grandezza.</li>
</ul></div>
""", printed=B(9))

s(26, "Definition and Taxonomy", "<p>Definizione formale di esempio avversario e classificazione degli attacchi.</p>", kind="div", sec=("l14-tassonomia", "Definizioni e tassonomia", "slide 26–35"), printed=B(10))

s(27, "Neural Networks for Image Classification", """
<p><b>Figura</b> in alto (Arcos-García et al. 2018): una CNN per il riconoscimento di cartelli stradali. Input 3 × 48 × 48, poi blocchi conv, ReLU, max-pooling e moduli di trasformazione spaziale (st1, st2, st3), fino a due layer fully connected e la softmax su <b>43 classi</b> (il dataset tedesco GTSRB). Parte «feature extraction» e parte «classification».</p>
<p><b>Figura</b> in basso, lo schema astratto che si usa nel resto della lezione:</p>
<ul>
<li>l'input <b>x</b> (un cartello di precedenza) entra in una rete <b>y = f(x)</b>;</li>
<li>l'uscita y è un vettore di punteggi per classe (0.1, 0.7, 0.0, 0.2 nell'esempio);</li>
<li>la classe predetta è quella con punteggio massimo, letta in una <b>tabella di codifica</b> (0 = rombo giallo, 1 = precedenza, 2 = freccia blu, 4 = stop): qui 1.</li>
</ul>
<p>Notazione delle slide: f: ℝ<sup>n</sup> → ℝ<sup>C</sup> dà i punteggi (logit o probabilità) delle C classi, e 𝒦(x) = argmax<sub>j</sub> f(x)<sub>j</sub> è l'etichetta predetta.</p>
""", printed=B(11))

s(28, "Geometrical Intuition", """
<p>Un classificatore <b>divide lo spazio degli input in regioni</b>, una per classe, separate da <b>frontiere di decisione</b>.</p>
<p><b>Figura</b>: un piano con cartelli sparsi (frecce blu, rombi gialli, stop rossi), ciascuno un punto dello spazio delle immagini. Due curve nere sono le frontiere; la regione a destra è la «stop region». Alcuni punti stanno vicinissimi a una frontiera (uno stop e un rombo sbiaditi sulla curva).</p>
<ul>
<li>Ogni immagine è un punto di uno spazio di dimensione enorme (n = 48 · 48 · 3 ≈ 6900 per i cartelli).</li>
<li>Le frontiere sono definite ovunque, anche dove non ci sono dati di training: lì il comportamento è <b>«undefined behaviour»</b>, non controllato da nessun esempio.</li>
<li>Un esempio avversario è un punto <b>vicino</b> a un'immagine pulita ma dall'altra parte di una frontiera. In alta dimensione quasi ogni punto ha una frontiera a distanza piccola in qualche direzione.</li>
</ul>
""", printed=B(12))

s(29, "Adversarial Examples", """
<p><b>Figura</b>: in alto un cartello di stop x entra nella rete y = f(x): i punteggi sono 0.1 (rombo), 0.2 (precedenza), 0.01 (freccia), <b>0.7 (stop)</b>, classificazione corretta. In basso allo stesso stop si somma una perturbazione colorata δ: l'immagine x + δ sembra identica, ma i punteggi diventano <b>0.6 (rombo)</b>, 0.2, 0.01, 0.2 (stop). La rete ora vede un rombo giallo (diritto di precedenza).</p>
<p>È la definizione visiva: una perturbazione piccola cambia la classe predetta. Su un'auto autonoma significherebbe non fermarsi allo stop.</p>
""", printed=B(13))

s(30, "Definition of Adversarial Examples", """
<p><b>Definizione</b>: un esempio avversario è il risultato di una perturbazione con <b>norma l<sub>p</sub> piccola</b> che inganna un modello di classificazione:</p>
<span class="f">𝒦(x + δ) ≠ 𝒦(x)   e   ‖δ‖ ≈ 0   (in qualche norma l<sub>p</sub>)</span>
<p><b>Figura</b>: cartello «obbligo di svolta a destra» più una perturbazione grigia appena visibile = un'immagine identica classificata «limite 20 km/h».</p>
<p><b>Norme l<sub>p</sub></b> (distanze di Minkowski) su δ ∈ ℝ<sup>n</sup>:</p>
<span class="f">‖δ‖<sub>0</sub> = #{ i : δ<sub>i</sub> ≠ 0 }   (numero di pixel modificati)</span>
<span class="f">‖δ‖<sub>p</sub> = ( ∑<sub>i=1</sub><sup>n</sup> |δ<sub>i</sub>|<sup>p</sup> )<sup>1/p</sup></span>
<span class="f">‖δ‖<sub>∞</sub> = max<sub>i</sub> |δ<sub>i</sub>|   (la modifica più grande su un singolo pixel)</span>
<p><b>Figura</b> a destra: le «palle unitarie» {‖δ‖<sub>p</sub> = 1} in 2D per p = 0.25, 0.5, 1, 2, 4, …, ∞: una stella concava, una stella meno concava, un rombo, un cerchio, un quadrato arrotondato, un quadrato. Le prime due (p &lt; 1) sono cerchiate in rosso come «No Convex (pseudo-norm)».</p>
<div class="box k"><b>Da saper fare: calcolare le norme</b><p>δ = (0.5, 0, −0.2, 0, 0.1):</p>
<ul>
<li>‖δ‖<sub>0</sub> = 3 (tre componenti non nulle);</li>
<li>‖δ‖<sub>1</sub> = 0.5 + 0.2 + 0.1 = 0.8;</li>
<li>‖δ‖<sub>2</sub> = √(0.25 + 0.04 + 0.01) = √0.30 ≈ 0.548;</li>
<li>‖δ‖<sub>∞</sub> = 0.5.</li>
</ul>
<p>Vale sempre ‖δ‖<sub>∞</sub> ≤ ‖δ‖<sub>2</sub> ≤ ‖δ‖<sub>1</sub> ≤ ‖δ‖<sub>0</sub> · ‖δ‖<sub>∞</sub>. Per questo la palla l<sub>1</sub> sta dentro la palla l<sub>2</sub>, che sta dentro la palla l<sub>∞</sub> (stesso raggio).</p></div>
<div class="box k"><b>Da capire bene: cosa vuol dire «pseudo-norma»</b><p>Una norma deve essere positiva, <b>omogenea</b> (‖aδ‖ = |a|·‖δ‖) e soddisfare la <b>disuguaglianza triangolare</b>; quest'ultima equivale alla convessità della palla unitaria.</p>
<ul>
<li>Per <b>p &lt; 1</b> la formula è omogenea ma la triangolare fallisce: con a = (1, 0), b = (0, 1) e p = 0.5, ‖a‖ = ‖b‖ = 1 ma ‖a + b‖ = (1 + 1)<sup>2</sup> = 4 &gt; 2. La palla è una stella concava (figura). In matematica si chiama più precisamente <b>quasi-norma</b>.</li>
<li><b>l<sub>0</sub></b> non è nemmeno omogenea: ‖2δ‖<sub>0</sub> = ‖δ‖<sub>0</sub>. Soddisfa la triangolare ma non è una norma; il nome viene dal limite ∑|δ<sub>i</sub>|<sup>p</sup> → ‖δ‖<sub>0</sub> per p → 0 (senza la radice 1/p, che con almeno due componenti non nulle farebbe esplodere il valore).</li>
</ul>
<p>«Pseudo-norma» nella slide va letto in senso largo («non è una vera norma»). Conseguenza pratica: con l<sub>0</sub> e p &lt; 1 i problemi di ottimizzazione non sono convessi nemmeno nel vincolo, e la proiezione sulla palla è più difficile.</p></div>
""", printed=B(14))

s(31, "Different visualization of l<sup>p</sup> bounded attacks", """
<p>La definizione con le norme di Minkowski copre perturbazioni <b>visivamente molto diverse</b>. <b>Figura</b> (Pintor et al. 2021, attacco FMN su MNIST): un «1» e un «7» originali, attaccati minimizzando norme diverse:</p>
<ul>
<li><b>l<sub>0</sub></b> (‖δ‖<sub>0</sub> = 7 e 8, classificati 8 e 2): <b>pochi pixel, valori illimitati</b>: alcuni punti neri isolati, ciascuno cambiato al massimo.</li>
<li><b>l<sub>1</sub></b> (‖δ‖<sub>1</sub> = 3.53 e 2.68, classificati 8 e 2): pochi pixel, valori limitati: qualche punto sparso.</li>
<li><b>l<sub>2</sub></b> (‖δ‖<sub>2</sub> = 4.87 e 4.20, classificati 3 e 2): modifiche concentrate lungo il tratto, che appare spezzato e rimodellato; l'etichetta della slide dice «few pixels, bounded values».</li>
<li><b>l<sub>∞</sub></b> (‖δ‖<sub>∞</sub> = 0.341 e 0.348, classificati 8 e 3): <b>molti pixel, valori limitati</b>: tutto lo sfondo diventa grigio a chiazze, ogni pixel cambiato al massimo di circa un terzo.</li>
</ul>
<p>Regola pratica: l<sub>0</sub> e l<sub>1</sub> favoriscono perturbazioni <b>sparse</b>, l<sub>∞</sub> perturbazioni <b>dense</b> e uniformi, l<sub>2</sub> sta in mezzo. La scelta della norma è parte del modello di minaccia.</p>
""", printed=B(15))

s(32, "Taxonomy: Digital or Real World", """
<ul>
<li><b>Perturbazione digitale</b>: una δ non rilevabile dall'occhio, sommata direttamente ai pixel. <b>Figura</b>: cartello 30 + δ grigia = immagine identica classificata 80. È il <b>focus della lezione</b>.</li>
<li><b>Attacchi fisici</b>: perturbazioni che sopravvivono all'acquisizione con camere, microfoni ecc. <b>Figura</b>: un cartello di stop con adesivi neri e bianchi (<b>patch</b>) classificato come rombo di precedenza; uno stop coperto da un <b>poster</b> che ne altera i colori, classificato come freccia blu (attacchi di Eykholt et al. 2018).</li>
</ul>
<p>Gli attacchi fisici devono essere robusti a punto di vista, distanza, illuminazione e stampa, quindi sono in genere <b>visibili</b> (ma sembrano graffiti o adesivi innocui). Si ottengono ottimizzando la perturbazione in media su molte trasformazioni.</p>
""", printed=B(16))

s(33, "Taxonomy: Targeted or Untargeted", """
<ul>
<li><b>Targeted</b>: l'attaccante vuole che il modello risponda una <b>classe precisa</b> &lt;target&gt;. <b>Figura</b>: tre cartelli blu diversi (freccia, rotatoria, fine divieto), tutti fatti classificare come STOP.</li>
<li><b>Untargeted</b>: l'attaccante vuole solo che il modello <b>sbagli</b>, senza scegliere l'uscita. <b>Figura</b>: tre immagini CIFAR-10 a bassa risoluzione classificate bird, truck, frog (classi sbagliate qualunque).</li>
</ul>
<p>Il targeted è più difficile (bisogna raggiungere una regione specifica, non una qualunque) e più pericoloso. Nella formulazione cambia il segno dell'ottimizzazione: l'untargeted <b>aumenta</b> la loss della classe vera, il targeted <b>diminuisce</b> la loss della classe obiettivo (slide 37).</p>
""", printed=B(17))

s(34, "Taxonomy: Black or White Box", """
<ul>
<li><b>White box</b>: l'attaccante conosce <b>architettura</b>, <b>pesi</b> e <b>dati</b>. Può calcolare i gradienti ∇<sub>x</sub>L con la backpropagation. <b>Figura</b>: un'immagine «5» più una perturbazione entra nella rete (pesi congelati, «completely known and frozen»); si calcola la loss rispetto a un target avversario e si <b>ottimizza la perturbazione</b>, non i pesi.</li>
<li><b>Black box</b>: il modello è un <b>oracolo</b>: si possono fare solo interrogazioni (input → uscita). Varianti: si conosce l'architettura ma non i dati, i dati ma non l'architettura, oppure nessuno dei due. <b>Figura</b>: immagini di query passano dalla CNN bersaglio; le risposte servono ad addestrare un <b>modello sostituto</b> (substitute model), da cui si generano attacchi da trasferire alla rete vera.</li>
</ul>
<p>Due strategie black box: (1) attacchi <b>basati su query</b> che stimano il gradiente o cercano a caso (Square attack, slide 58); (2) <b>trasferibilità</b>: esempi avversari costruiti su un modello sostituto spesso ingannano anche un modello diverso.</p>
<div class="box b"><b>Szeliski · § 5.4.6 Adversarial examples</b><p>Szeliski descrive la costruzione originale di Szegedy: si fa backpropagation di un gradiente verso la classe «falsa» fino all'<b>input</b>, aggiornando l'immagine finché quella classe domina; è un attacco white box perché serve accesso ai pesi. Riporta la scoperta che gli esempi avversari sono relativamente robusti e <b>condivisi</b> da reti con numero di layer, attivazioni o dati di training diversi: è la base della trasferibilità. Cita anche gli adesivi sugli stop (Eykholt 2018, slide 32), la libreria CleverHans (slide 4) e l'addestramento robusto di Madry (slide 47).</p></div>
""", printed=B(18))

s(35, "Minimal Taxonomy of Adversarial Examples", """
<p>Tre assi per classificare un attacco (il <b>modello di minaccia</b>):</p>
<ul>
<li><b>Conoscenza dell'avversario</b>: white box (architettura e parametri noti) ↔ black box (niente di noto). Sono possibili situazioni intermedie (gray box).</li>
<li><b>Obiettivo</b>: untargeted (una classe sbagliata qualunque) ↔ targeted (una classe specifica).</li>
<li><b>Norma della perturbazione</b>: 1-norma, 2-norma, ∞-norma: misura la grandezza della perturbazione.</li>
</ul>
<p>Le slide seguenti non fissano una norma: le formulazioni valgono per qualunque l<sub>p</sub>, con effetti diversi (slide 31). L'eccezione è FGSM, che è naturale per l<sub>∞</sub>.</p>
""", printed=B(19))

s(36, "Generation of Adversarial Examples", "<p>Gli attacchi come problemi di ottimizzazione: FGSM, L-BFGS, Carlini-Wagner, PGD, adversarial training.</p>", kind="div", sec=("l14-generazione", "Generazione degli esempi avversari", "slide 36–47"), printed=B(20))

s(37, "Generation of Adversarial Examples: loss-based attacks", """
<p><b>Attacchi basati sulla loss</b>: si fissa il budget ε e si cerca la perturbazione che fa più danno.</p>
<p><b>Untargeted</b>: <b>aumentare</b> la loss della classe vera vicino a x:</p>
<span class="f">max<sub>δ ∈ ℝ<sup>n</sup></sub> ℒ(f(x + δ), l<sub>true</sub>)   s.t.  ‖δ‖<sub>p</sub> ≤ ε,  0 ≤ x + δ ≤ 1,  Q·(x + δ) ∈ {0, …, Q}</span>
<p><b>Targeted</b>: <b>diminuire</b> la loss della classe obiettivo vicino a x:</p>
<span class="f">min<sub>δ ∈ ℝ<sup>n</sup></sub> ℒ(f(x + δ), l<sub>target</sub>)   s.t.  stessi vincoli</span>
<ul>
<li><b>Vincolo di box</b> 0 ≤ x + δ ≤ 1: l'immagine resta nel range valido dei pixel.</li>
<li><b>Vincolo intero</b> con Q = 255: x + δ deve essere rappresentabile a 8 bit (un'immagine salvata su file).</li>
<li>Insieme garantiscono che l'esempio avversario sia un'<b>immagine vera</b>. In pratica il vincolo intero si ignora durante l'ottimizzazione e si arrotonda alla fine (rischiando di perdere l'effetto se la perturbazione è molto piccola).</li>
</ul>
<p>Ingredienti: ℒ è la loss di training (cross-entropy), ma usata al contrario: i pesi sono fissi e la variabile è l'input.</p>
""", printed=B(21))

s(38, "Generation of Adversarial Examples: distance-based attacks", """
<p><b>Attacchi basati sulla distanza</b>: si cerca la perturbazione <b>più piccola</b> che inganna il modello (il budget non è fissato, è il risultato).</p>
<p><b>Untargeted</b>: il campione più vicino a x classificato in una classe <b>diversa</b>:</p>
<span class="f">min<sub>δ</sub> ‖δ‖<sub>p</sub>   s.t.  𝒦(x + δ) ≠ l<sub>true</sub>,  0 ≤ x + δ ≤ 1,  Q·(x + δ) ∈ {0, …, Q}</span>
<p><b>Targeted</b>: il campione più vicino a x classificato nella classe <b>obiettivo</b>:</p>
<span class="f">min<sub>δ</sub> ‖δ‖<sub>p</sub>   s.t.  𝒦(x + δ) = l<sub>target</sub>,  stessi vincoli</span>
<div class="box k"><b>Da capire bene: i due tipi di attacco a confronto</b>
<ul>
<li><b>Loss-based</b> (FGSM, PGD): vincolo sulla norma, si massimizza il danno. Rispondono a: «con budget ε, il modello resiste?». Danno l'<b>accuratezza robusta</b> a un ε fissato.</li>
<li><b>Distance-based</b> (L-BFGS, CW, DDN, FMN): si minimizza la norma con il vincolo di sbagliare. Rispondono a: «quanto è lontana la frontiera di decisione?». Danno la <b>perturbazione minima</b>, cioè i dB della slide 25.</li>
<li>Il vincolo 𝒦(x + δ) ≠ l<sub>true</sub> usa l'argmax: non è differenziabile, quindi non si può ottimizzare direttamente con il gradiente. Le slide 41–44 lo trasformano in una <b>penalità</b> differenziabile.</li>
</ul></div>
""", printed=B(22))

s(39, "Fast Gradient Sign Method", """
<p>La loss serve a trovare la direzione <b>peggiore</b> che inganna il modello, non ad addestrarlo. Con f: ℝ<sup>n</sup> → ℝ<sup>C</sup>:</p>
<span class="f">δ* = ε · sign( ∇<sub>x</sub> ℒ(f(x), l<sub>true</sub>) )</span>
<ul>
<li><b>ε</b>: l'ampiezza voluta, in norma l<sub>∞</sub>.</li>
<li><b>∇<sub>x</sub>ℒ</b>: il gradiente rispetto all'<b>input</b> (non ai pesi) dà la direzione di massima crescita della loss. Si calcola con una backpropagation, fermandosi ai pixel.</li>
<li><b>Osservazione</b>: la perturbazione ha norma uniforme limitata: x* = x + δ*, ‖δ*‖<sub>∞</sub> = ε (ogni pixel si sposta esattamente di ±ε, salvo le componenti con gradiente nullo).</li>
</ul>
<div class="box k"><b>Da saper fare: perché il segno del gradiente</b><p>Si linearizza la loss: ℒ(x + δ) ≈ ℒ(x) + g<sup>⊤</sup>δ, con g = ∇<sub>x</sub>ℒ. Si massimizza g<sup>⊤</sup>δ con ‖δ‖<sub>∞</sub> ≤ ε: ogni termine g<sub>i</sub>δ<sub>i</sub> è massimo con δ<sub>i</sub> = ε·sign(g<sub>i</sub>), quindi</p>
<span class="f">max<sub>‖δ‖∞ ≤ ε</sub> g<sup>⊤</sup>δ = ε ∑<sub>i</sub> |g<sub>i</sub>| = ε‖g‖<sub>1</sub>,   ottenuto con δ* = ε·sign(g)</span>
<p>Esempio: g = (0.3, −2, 0, 0.5), ε = 0.1 ⇒ δ* = (0.1, −0.1, 0, 0.1), aumento previsto g<sup>⊤</sup>δ* = 0.03 + 0.2 + 0 + 0.05 = 0.28 = ε‖g‖<sub>1</sub> = 0.1 · 2.8.</p>
<p>Con il vincolo l<sub>2</sub> invece il massimo è δ* = ε·g/‖g‖<sub>2</sub> (gradiente normalizzato), con aumento ε‖g‖<sub>2</sub>. FGSM è quindi il passo di massima salita per la norma l<sub>∞</sub>.</p>
<p><b>Versione targeted</b>: si vuole <b>diminuire</b> la loss della classe obiettivo, quindi si scende: δ* = −ε·sign(∇<sub>x</sub>ℒ(f(x), l<sub>target</sub>)). Infine si taglia x + δ* in [0, 1].</p></div>
<div class="box b"><b>Dal libro · cap. 12, § 12.4 Activations Versus Parameters</b><p>Il libro osserva che ogni layer prende come input sia le attivazioni sia i parametri, e che quindi tutto ciò che si fa sui parametri si può fare sulle attivazioni. Di norma si tengono fissi gli input e si imparano i pesi; si può invece tenere fissi i pesi e <b>ottimizzare l'input</b> rispetto a un obiettivo. È ciò che fanno gli attacchi avversari, la visualizzazione delle reti e il prompting. Il gradiente ∇<sub>x</sub>ℒ si ottiene con la stessa backpropagation del training, proseguita di un passo fino all'input. ${L12}.</p></div>
""".replace('${L12}', L('neural_nets.html', 'Cap. 12')), printed=B(23))

s(40, "Fast Gradient Sign Method: pro, contro e adversarial training", """
<span class="f">δ* = ε · sign(∇<sub>x</sub>ℒ(f(x), l<sub>true</sub>)),   x* = x + δ*</span>
<p><b>Figura</b>: il panda della slide 21, «l'attacco avversario più famoso», su GoogLeNet (ε = 0.007).</p>
<ul>
<li><b>Pro</b>: facile da implementare; <b>veloce</b> (un solo gradiente, quindi utile nell'adversarial training); limitato in norma uniforme.</li>
<li><b>Contro</b>: richiede ε grande (a volte visibile); <b>non sempre</b> produce un esempio avversario (un solo passo lineare può non attraversare la frontiera se la loss è curva).</li>
</ul>
<p><b>Adversarial training</b> (Goodfellow et al.): si addestra con una loss che mescola esempi puliti e avversari:</p>
<span class="f">ℒ̃(f(x), l) = α · ℒ(f(x), l) + (1 − α) · ℒ(f(x + δ*), l)</span>
<p>Il secondo termine è la <b>loss avversaria</b>; δ* va ricalcolato a ogni passo con il modello corrente (Goodfellow usa α = 0.5).</p>
<div class="box b"><b>Dal libro · cap. 36, § 36.2 Data Augmentation e § 36.3 Adversarial Training</b><p>Nel libro l'adversarial training è un caso estremo di <b>data augmentation</b>. La data augmentation minimizza la loss <b>in media</b> su trasformazioni casuali T(x; θ) dei dati (flip, crop, colore), allargando la distribuzione di training perché i dati di test sembrino «più dati di training». L'adversarial training sostituisce la media con il <b>caso peggiore</b>: per ogni esempio si applica la trasformazione che produce la loss più alta. Con T(x) = x + ε e ‖ε‖ &lt; r si ottiene la difesa contro gli attacchi in palla (slide 47). Il libro nota che lo stesso schema min-max si usa anche nelle GAN, nel reinforcement learning e si chiama in generale <b>robust optimization</b>. Prince (§ 9.3.4 Applying noise) presenta l'adversarial training come la forma estrema dell'aggiunta di rumore all'input: invece di rumore casuale si cerca il rumore peggiore. ${L36}.</p></div>
""".replace('${L36}', L('data_augmentation.html', 'Cap. 36')), printed=B(24))

s(41, "Minimal Adversarial Perturbation with Penalty", """
<p>Il problema distance-based targeted (slide 38) ha un vincolo non differenziabile 𝒦(x + δ) = l<sub>target</sub> (barrato in rosso). Szegedy et al. lo sostituiscono con una <b>penalità</b>:</p>
<span class="f">min<sub>δ</sub>  c‖δ‖<sub>p</sub> + ℒ(f(x + δ), l<sub>target</sub>)   s.t.  0 ≤ x + δ ≤ 1</span>
<ul>
<li><b>c</b> è la costante di penalità che bilancia «perturbazione piccola» e «classe obiettivo».</li>
<li>Con <b>c = 0</b> conta solo la loss: la soluzione non ha limiti sulla grandezza (resta solo il box).</li>
<li>Con <b>c grande</b> conta solo la norma: δ(c) ≈ 0, che non inganna nessuno.</li>
</ul>
<p><b>«Teorema»</b> della slide: se ℒ(f(x + δ), l<sub>target</sub>) è <b>convessa</b>, allora (1) per ogni c L-BFGS con vincoli di box trova una soluzione δ(c); (2) si può scegliere c con una ricerca lineare (line search) in modo che 𝒦(x + δ(c)) = l<sub>target</sub>.</p>
<div class="box k"><b>Da capire bene: l'ipotesi di convessità e la ricerca su c</b>
<ul>
<li>Per le reti profonde l'ipotesi è <b>falsa</b>: la loss in funzione dell'input non è convessa. Lo dicono Szegedy et al. stessi: per perdite convesse il metodo darebbe la soluzione esatta del problema di perturbazione minima, per le reti ne dà solo un'<b>approssimazione</b> (un minimo locale). La slide lo enuncia come teorema, ma per le reti vale come euristica.</li>
<li>Come si muove c: aumentando c la perturbazione si riduce finché a un certo punto smette di ingannare. Si cerca quindi il <b>c più grande</b> per cui x + δ(c) è ancora classificato l<sub>target</sub>: è la perturbazione più piccola che funziona. Con la convenzione di Carlini-Wagner (slide 44), dove c moltiplica la loss invece della norma, si cerca il <b>c più piccolo</b> che funziona. È la stessa cosa con c ↔ 1/c.</li>
</ul></div>
""", printed=B(25))

s(42, "Minimal Adversarial Perturbation with Penalty: BL-BFGS", """
<p><b>BL-BFGS</b> (Box-constrained Limited-memory Broyden-Fletcher-Goldfarb-Shanno): un metodo <b>quasi-Newton</b> per minimizzare con vincoli di box. Approssima l'Hessiana con gli ultimi gradienti (memoria limitata) e gestisce direttamente i vincoli 0 ≤ x + δ ≤ 1.</p>
<span class="f">min<sub>δ</sub>  c‖δ‖<sub>p</sub> + ℒ(f(x + δ), l<sub>target</sub>)   s.t.  0 ≤ x + δ ≤ 1</span>
<p><b>Figura</b> (Szegedy et al. 2013): i <b>primi esempi avversari</b> presentati alla comunità, su AlexNet: uno scuolabus giallo e un uccello nell'erba, con la perturbazione amplificata al centro e l'immagine avversaria a destra, identica all'originale. Nell'articolo tutte le immagini attaccate vengono classificate «struzzo».</p>
<ul>
<li><b>Pro</b>: perturbazioni particolarmente piccole (approssima la perturbazione minima); affidabile, converge quasi sempre.</li>
<li><b>Contro</b>: <b>lento</b>: la slide stima circa 20 000 passaggi in avanti della rete per ogni ricerca su c.</li>
</ul>
""", printed=B(26))

s(43, "Including the Box Constraint in the Objective (CW)", """
<p>Carlini e Wagner (CW) eliminano <b>entrambi</b> i vincoli del problema di perturbazione minima (barrati in rosso e in blu) con due semplificazioni.</p>
<p><b>1 · Cambio di variabile</b> (elimina il box): si ottimizza w invece di δ, con</p>
<span class="f">δ = ½ (tanh(w) + 1) − x</span>
<p>Poiché tanh(w) ∈ (−1, 1), x + δ = ½(tanh(w) + 1) ∈ (0, 1) per ogni w ∈ ℝ<sup>n</sup>: il vincolo di box è soddisfatto <b>automaticamente</b> e si può usare un ottimizzatore senza vincoli (Adam).</p>
<p><b>2 · Loss migliore</b> (sostituisce il vincolo sulla classe): una funzione dei <b>logit</b> y = f(x + δ), la parte positiva di un «margine»:</p>
<span class="f">ℒ(y, l) = [ y<sub>l</sub> − max<sub>j≠l</sub> y<sub>j</sub> ]<sup>+</sup>   (come scritta nella slide)</span>
<div class="box w"><b>Attenzione: il margine della slide ha il segno giusto per l'untargeted, non per il targeted</b><p>Nella slide 44 questa loss si usa con l = l<sub>target</sub> e si <b>minimizza</b>. Ma [y<sub>t</sub> − max<sub>j≠t</sub> y<sub>j</sub>]<sup>+</sup> è positiva quando la classe obiettivo è <b>già</b> la più votata, e minimizzarla spinge y<sub>t</sub> verso il basso: il contrario di ciò che si vuole. La funzione di Carlini e Wagner (la loro f<sub>6</sub>) per l'attacco targeted è</p>
<span class="f">ℒ(y, t) = [ max<sub>j≠t</sub> y<sub>j</sub> − y<sub>t</sub> ]<sup>+</sup>   (in generale max(max<sub>j≠t</sub> y<sub>j</sub> − y<sub>t</sub>, −κ))</span>
<p>che vale 0 appena il logit della classe obiettivo supera tutti gli altri, cioè appena l'attacco riesce, e da lì in poi lascia lavorare solo il termine di norma. La forma della slide, con l = l<sub>true</sub>, è invece quella dell'attacco <b>untargeted</b>: [y<sub>true</sub> − max<sub>j≠true</sub> y<sub>j</sub>]<sup>+</sup> si annulla quando un'altra classe supera quella vera. La costante κ ≥ 0 chiede un margine di confidenza (κ = 0 dà la parte positiva della slide).</p></div>
<div class="box k"><b>Da capire bene: perché i logit e non la cross-entropy</b><p>La cross-entropy continua a spingere anche quando l'attacco è già riuscito (vuole probabilità 1) e attraverso la softmax ha gradienti che si saturano. Il margine sui logit misura direttamente «quanto manca a cambiare classe», si azzera appena basta e non spreca perturbazione: per questo CW trova perturbazioni più piccole di L-BFGS.</p></div>
""", printed=B(27))

s(44, "CW Minimum Problem (Unconstrained)", """
<p>Dal problema con vincoli si passa a quello con penalità (come Szegedy, slide 41), e poi con il cambio di variabile a un problema <b>senza vincoli</b>:</p>
<span class="f">min<sub>w ∈ ℝ<sup>n</sup></sub>  ‖ ½(tanh(w) + 1) − x ‖<sub>p</sub> + c · ℒ( f( ½(tanh(w) + 1) ), l<sub>target</sub> )</span>
<ul>
<li>Il primo argomento è δ, il secondo è x + δ (le graffe rosse della slide).</li>
<li>Qui c moltiplica la <b>loss</b>, non la norma come nella slide 41 (si passa dall'una all'altra dividendo per c).</li>
<li><b>Osservazione</b>: c si sceglie con una ricerca in modo che 𝒦(x + δ(c)) = l<sub>target</sub>. Carlini e Wagner usano una ricerca binaria: il c più piccolo con cui l'attacco riesce dà la perturbazione più piccola.</li>
</ul>
<div class="box k"><b>Da saper fare: scrivere CW da zero</b>
<ol>
<li>Variabile: w ∈ ℝ<sup>n</sup>, inizializzata con w = artanh(2x − 1) (così δ = 0 all'inizio).</li>
<li>Immagine: x' = ½(tanh(w) + 1), sempre in (0, 1).</li>
<li>Obiettivo: ‖x' − x‖<sub>2</sub><sup>2</sup> + c · max(max<sub>j≠t</sub> Z(x')<sub>j</sub> − Z(x')<sub>t</sub>, −κ), con Z i logit (segno corretto, vedi riquadro della slide 43).</li>
<li>Minimizzare con Adam per qualche centinaio o migliaio di passi; tenere il x' più vicino a x fra quelli classificati t.</li>
<li>Ricerca binaria su c: se l'attacco riesce, si diminuisce c; se fallisce, si aumenta.</li>
</ol>
<p>Nell'articolo originale la variante principale usa ‖δ‖<sub>2</sub><sup>2</sup>; per l<sub>0</sub> e l<sub>∞</sub> ci sono procedure iterative apposite.</p></div>
""", printed=B(28))

s(45, "Examples of attack with CW", """
<p><b>Figura</b> (Carlini e Wagner): due griglie 6 × 6 di cifre MNIST. La riga è la cifra originale (0–5), la colonna la classe obiettivo (0–5): ogni immagine fuori diagonale è classificata come la colonna.</p>
<ul>
<li><b>Sinistra, l<sub>2</sub></b>: le cifre sembrano <b>identiche</b> agli originali; la perturbazione è distribuita e appena visibile come una leggera sfocatura del tratto.</li>
<li><b>Destra, l<sub>0</sub></b>: pochi pixel cambiati, visibili come puntini bianchi sparsi attorno e dentro il tratto.</li>
</ul>
<p>Ogni cifra si può trasformare in <b>qualunque</b> altra classe con perturbazioni minime: è un attacco targeted completo, che all'epoca ha battuto anche la difesa per «distillazione» proposta come robusta.</p>
""", printed=B(30))

s(46, "Projected Gradient Descent (PGD)", """
<p><b>Problema di massimo</b> (untargeted, loss-based, slide 37):</p>
<span class="f">max<sub>δ</sub> ℒ(f(x + δ), l<sub>true</sub>)   s.t.  ‖δ‖<sub>p</sub> ≤ ε,  0 ≤ x + δ ≤ 1,  Q·(x + δ) ∈ {0, …, Q}</span>
<p><b>FGSM iterato</b> con proiezione (Madry et al. 2018):</p>
<span class="f">x̃<sup>(t)</sup> = x<sup>(t−1)</sup> + α · sgn( ∇<sub>x</sub>ℒ(f(x<sup>(t−1)</sup>), l<sub>true</sub>) )</span>
<span class="f">x<sup>(t)</sup> = Π<sub>B<sub>p</sub>(x, ε)</sub>( x̃<sup>(t)</sup> )</span>
<ul>
<li><b>α</b> è il learning rate della salita del gradiente (più piccolo di ε).</li>
<li><b>Π</b> è la proiezione sulla palla l<sub>p</sub> di raggio ε <b>centrata nell'immagine originale x</b>: dopo ogni passo si riporta il punto dentro il budget.</li>
<li>Procedura: (1) punto di partenza casuale nella palla; (2) qualche passo di salita del gradiente; (3) proiezione nella palla l<sub>p</sub>; (4) si ripetono 1–3 (riavvii casuali) e si tiene il risultato con loss più alta.</li>
</ul>
<p><b>Figura</b>: mappa della loss attorno a un campione (X al centro, zona viola a loss bassa) dentro una palla L<sup>2</sup> (cerchio nero). Due traiettorie rosse da due punti di partenza diversi salgono verso zone gialle o verdi a loss alta, restando dentro il cerchio: partenze diverse portano a massimi locali diversi.</p>
<div class="box k"><b>Da saper fare: PGD passo per passo</b>
<p>Caso l<sub>∞</sub> (il più usato), pixel in [0, 1], ad esempio ε = 8/255, α = 2/255, K passi:</p>
<ol>
<li>x<sup>(0)</sup> = x + u, con u uniforme in [−ε, ε]<sup>n</sup>.</li>
<li>Per t = 1…K: g = ∇<sub>x</sub>ℒ(f(x<sup>(t−1)</sup>), l<sub>true</sub>); x̃ = x<sup>(t−1)</sup> + α·sign(g).</li>
<li>Proiezione l<sub>∞</sub>: x<sup>(t)</sup> = clip(x̃, x − ε, x + ε), componente per componente; poi clip in [0, 1] per il box.</li>
</ol>
<p>Caso l<sub>2</sub>: passo x̃ = x<sup>(t−1)</sup> + α·g/‖g‖<sub>2</sub>; proiezione: se ‖x̃ − x‖<sub>2</sub> &gt; ε si riporta x̃ − x sulla sfera, x + ε(x̃ − x)/‖x̃ − x‖<sub>2</sub>.</p>
<p>La proiezione si fa <b>dopo</b> il passo, rispetto a x e non rispetto all'iterata precedente, altrimenti la perturbazione totale potrebbe crescere fino a Kα.</p>
<p>Nota sulla slide: il passo con sgn è quello di massima salita per l<sub>∞</sub> (scheda 39); se si lavora in una palla l<sub>2</sub>, come nella figura, il passo naturale è il gradiente normalizzato. Con il segno l'algoritmo funziona comunque, ma non è più la salita più ripida per quella norma. Il nome «descent» viene dalla formulazione come minimo di −ℒ.</p></div>
""", printed=B(35))

s(47, "Adversarial Training by PGD", """
<p><b>Minimizzazione del caso peggiore empirico</b> (Madry et al.):</p>
<span class="f">min<sub>θ</sub> ρ(θ),   ρ(θ) = 𝔼<sub>(x, l) ∈ 𝒳</sub> [ max<sub>‖δ‖<sub>p</sub> &lt; ε</sub> ℒ(f<sub>θ</sub>(x + δ), l; θ) ]</span>
<ul>
<li>Problema <b>min-max</b> (punto di sella): il massimo interno è l'attacco (trovato con PGD), il minimo esterno è l'addestramento dei pesi θ.</li>
<li>Invece della loss media sui dati puliti si minimizza la loss <b>nel caso peggiore</b> in una palla attorno a ogni esempio.</li>
</ul>
<p><b>Figura</b> (tre pannelli): (1) punti verdi e blu separati da una retta: frontiera giusta sui dati puliti; (2) attorno a ogni punto un quadrato (la palla l<sub>∞</sub> di raggio ε); alcuni quadrati attraversano la retta e due stelle rosse indicano esempi avversari, punti del quadrato classificati male; (3) la frontiera robusta (curva rossa) <b>si piega</b> per lasciare ogni quadrato interamente dalla parte giusta.</p>
<p>Messaggio della figura: la robustezza richiede una frontiera <b>più complessa</b> (più capacità del modello) e lontana da ogni esempio almeno ε.</p>
<div class="box k"><b>Da saper fare: l'algoritmo di adversarial training</b>
<ol>
<li>Si prende un mini-batch {(x<sub>i</sub>, l<sub>i</sub>)}.</li>
<li><b>Massimo interno</b>: per ogni x<sub>i</sub> si calcola x<sub>i</sub><sup>adv</sup> con K passi di PGD sul modello corrente f<sub>θ</sub> (pesi fermi).</li>
<li><b>Minimo esterno</b>: un passo di SGD su θ con il gradiente ∇<sub>θ</sub> ∑<sub>i</sub> ℒ(f<sub>θ</sub>(x<sub>i</sub><sup>adv</sup>), l<sub>i</sub>).</li>
</ol>
<p>Perché basta il gradiente nel punto peggiore: per il teorema di Danskin il gradiente di max<sub>δ</sub> ℒ(θ, δ) rispetto a θ è il gradiente di ℒ calcolato nel massimizzatore δ*. Costo: ogni passo richiede K + 1 forward e backward, cioè circa K + 1 volte l'addestramento normale. Rispetto alla slide 40 qui si usano solo esempi avversari (α = 0) e un attacco più forte (PGD invece di FGSM).</p>
<p>Effetti noti: l'accuratezza sui dati puliti di solito <b>scende</b> un po', quella sotto attacco sale molto; la robustezza vale per la norma e l'ε usati in training.</p></div>
<div class="box b"><b>Dal libro · cap. 36, § 36.3 Adversarial Training, e cap. 35, § 35.6.2 Defenses</b><p>Il libro scrive l'adversarial training come</p>
<span class="f">argmin<sub>f</sub> 𝔼<sub>x, y</sub> [ max<sub>ε : ‖ε‖ &lt; r</sub> ℒ(f(x + ε), y) ]</span>
<p>(eq. 36.2): è la formula della slide con il libro che chiama ε la perturbazione e r il raggio (le slide usano δ ed ε). In § 35.6.2 spiega il perché: l'analisi avversaria è un'analisi del <b>caso peggiore</b>, mentre il training normale minimizza il <b>rischio empirico</b>, cioè l'errore medio. Ottimizzando solo la media, il caso peggiore può essere arbitrariamente cattivo; minimizzare l'errore nel caso peggiore dà sistemi più robusti. ${L36}, ${L35}.</p></div>
""".replace('${L36}', L('data_augmentation.html', 'Cap. 36')).replace('${L35}', L('bias_and_shift.html', 'Cap. 35')), printed=B(36))

s(48, "Conclusion", "<p>Conclusioni del seminario: esempi avversari anche per la visione biologica e riepilogo.</p>", kind="div", sec=("l14-conclusioni", "Conclusioni del seminario", "slide 48–51"), printed=B(47))

s(49, "Adversarial Examples for Biological Vision Systems", """
<ul>
<li><b>Figura</b> a sinistra: la falena <b>Polyphemus</b>, con grandi macchie a forma di occhio sulle ali posteriori. È un meccanismo di difesa: le macchie imitano gli occhi di un animale più grande e spaventano i predatori. È un «esempio avversario» prodotto dall'evoluzione contro il sistema visivo degli uccelli.</li>
<li><b>Figura</b> a destra: «<b>chihuahua o muffin</b>», una griglia di foto in cui musi di chihuahua e muffin ai mirtilli si somigliano: anche noi esitiamo.</li>
</ul>
<p>Riferimento della slide: l'articolo del 2018 il cui primo autore è Elsayed (con Shankar, Papernot, Goodfellow e altri), pubblicato poi come <i>Adversarial Examples that Fool both Computer Vision and Time-Limited Humans</i>: esempi avversari costruiti su reti, mostrati a persone per un tempo molto breve, influenzano anche la loro scelta.</p>
<p>Il libro (§ 35.6) nomina proprio l'evoluzione fra i contesti in cui lo spostamento dei dati è avversario: un altro animale che cerca di mangiarci.</p>
""", printed=B(48))

s(50, "Conclusion", """
<p>Ripresa dell'indice, come riepilogo:</p>
<ol>
<li><b>Introduzione, definizioni e tassonomia</b>: esempio avversario = perturbazione piccola in norma l<sub>p</sub> che cambia la classe; tre assi: conoscenza (white/black box), obiettivo (targeted/untargeted), norma.</li>
<li><b>Generazione</b>: loss-based (FGSM, PGD) e distance-based (L-BFGS, CW); la difesa più solida è l'<b>adversarial training</b> min-max.</li>
</ol>
""", printed=B(49))

s(51, "sAIfer Lab", """
<p><b>sAIfer Lab</b>: laboratorio congiunto sulla sicurezza e affidabilità dell'AI (Joint lab on Safety and Security of AI), fra il <b>PRA Lab</b> del Dipartimento di Ingegneria Elettrica ed Elettronica dell'Università di Cagliari e lo <b>SmartLab</b> del DIBRIS dell'Università di Genova.</p>
<p><b>Figura</b>: foto di gruppo del laboratorio e i numeri: oltre 70 ricercatori, oltre 800 pubblicazioni, oltre 100 progetti, 30 anni di esperienza. Fine della seconda presentazione.</p>
""", printed=B(50))

# ===================== PARTE 3: Pilot 2 AVISENSE (pagine 52-66) =====================

s(52, "Pilot 2: Securing the AI Supply Chain in the Autonomous Vehicles Domain", "<p>Terza presentazione: il Pilot 2 di CoEvolution (AVISENSE e AVL), sicurezza della percezione nei veicoli autonomi.</p>", kind="div", sec=("l14-pilot2", "Pilot 2: veicoli autonomi", "slide 52–56"), printed=P(1))

s(53, "Problem Statement", """
<p><b>Figura</b> a sinistra: «a complex system … in a complex environment». Un'auto con i coni dei suoi sensori e i moduli software, e accanto l'ambiente: traffico, condizioni della strada, meteo, comportamento dei guidatori.</p>
<ul>
<li><b>Sensori di bordo</b>: i CAV usano camere, radar, <b>LiDAR</b>, ultrasuoni, GPS.</li>
<li><b>Modelli di percezione</b>: le funzioni del veicolo dipendono da modelli di AI che interpretano l'ambiente e guidano il percorso.</li>
<li><b>Percezione cooperativa</b>: i veicoli condividono ciò che vedono per migliorare il modello dell'ambiente, estendere il raggio dei sensori e resistere a guasti e attacchi.</li>
<li><b>Sicurezza critica</b>: le comunicazioni <b>V2V</b> (veicolo-veicolo) e <b>V2X</b> (veicolo-infrastruttura) aprono nuovi canali di attacco.</li>
</ul>
""", printed=P(2))

s(54, "Potential attacks", """
<p><b>Figura</b>: la pipeline del veicolo e i punti in cui si può attaccare (ovali rossi).</p>
<ul>
<li>Pipeline: ambiente → sensori (LiDAR, radar, camera, GPS) → <b>sensor fusion</b> → <b>modello di percezione</b> → <b>modello di moto</b> (pianificazione) → controllo del veicolo. A monte: training del modello e aggiornamenti <b>OtA</b> (over the air).</li>
<li><b>Attacchi avversari ai sensori</b>: sull'ingresso dei sensori (ad esempio punti LiDAR falsi o perturbati, spoofing del GPS). Sono gli esempi avversari della seconda parte, nel mondo fisico.</li>
<li><b>Data poisoning</b>: sul training del modello.</li>
<li><b>Manomissione del modello</b>, accesso non autorizzato, supply chain compromessa: sugli aggiornamenti OtA (un modello con backdoor installato da remoto).</li>
<li><b>Estrazione del modello</b>: fra percezione e moto; interrogando il modello si ricostruisce una copia (che poi serve anche per attacchi black box per trasferimento, scheda 34).</li>
</ul>
""", printed=P(3))

s(55, "Trust score system", """
<p><b>Figura</b>: la stessa pipeline, racchiusa in un riquadro verde «Trust score system»; ai punti di attacco della slide precedente corrispondono ora dei <b>controlli</b> (ovali verdi):</p>
<ul>
<li>sui sensori: i dati dei sensori sono <b>affidabili</b>?</li>
<li>sugli aggiornamenti OtA: il modello aggiornato è fidato (dati di training non compromessi) e adatto all'hardware del veicolo?</li>
<li>sulla percezione: ci sono attività di <b>estrazione</b> in corso?</li>
<li>sul controllo: <b>validazione a runtime</b>: il comportamento resta entro i limiti previsti del ciclo di vita?</li>
</ul>
<p>L'idea è assegnare a ogni componente un punteggio di fiducia, e usarlo per decidere se fidarsi delle sue uscite. La validazione a runtime corrisponde in bibliografia al rilevamento di input fuori distribuzione (Hendrycks e Gimpel, rif. [41]).</p>
""", printed=P(4))

s(56, "Perception", """
<ul>
<li><b>La sfida</b>: i veicoli autonomi usano <b>LiDAR</b> e <b>GNSS</b> (sistemi satellitari di posizionamento, come GPS e Galileo) per capire la scena.</li>
<li>Questi sensori sono <b>vulnerabili ad attacchi avversari</b> che compromettono quattro capacità critiche (riquadri a destra): <b>rilevamento e tracciamento 3D</b> di oggetti, <b>segmentazione semantica</b>, <b>SLAM e localizzazione</b>, <b>percezione cooperativa V2X</b>.</li>
<li><b>Key insight</b>: senza difese robuste, una percezione compromessa può portare a guasti di sicurezza catastrofici nella guida reale.</li>
</ul>
""", printed=P(5))

s(57, "3D Segmentation", """
<ul>
<li>La <b>segmentazione semantica</b> LiDAR e RGB è uno strato di percezione importante: assegna a ogni punto (o pixel) una classe (strada, auto, pedone, vegetazione…).</li>
<li>Le nuvole di punti 3D e le immagini RGB sono elaborate da <b>reti di segmentazione separate</b>.</li>
<li>Le <b>perturbazioni avversarie</b> su una delle due modalità corrompono l'uscita e compromettono la sicurezza a valle.</li>
</ul>
<p><b>Figura</b> (Kapsali, Gkillas, Lalos, <i>UniPure</i>, IEEE Trans. on AI): due rami. <b>Ramo 1 LiDAR</b>: sensore LiDAR sul veicolo → nuvola di punti grezza → rete di segmentazione LiDAR → uscita pulita colorata per classe; con un attacco avversario (icona del diavoletto rosso) l'uscita diventa «corrupted». <b>Ramo 2 RGB</b>: camera → immagine → rete di segmentazione → maschera pulita, oppure maschera corrotta sotto attacco.</p>
""", sec=("l14-lidar", "Attacchi alla segmentazione LiDAR e purificazione", "slide 57–61"), printed=P(6))

s(58, "Adversarial attacks on LiDAR semantic segmentation", """
<p><b>Pipeline</b> (riga in alto): nuvola di punti LiDAR, N × (x, y, z, intensità) → <b>range image</b> (proiezione sferica, 64 × 1024) → <b>perturbazione δ</b> con ‖δ‖<sub>∞</sub> ≤ ε → rete di segmentazione <b>LENet</b> (il modello bersaglio) → etichette semantiche per punto.</p>
<ul>
<li><b>Range image</b>: ogni punto si proietta su una griglia con riga = angolo di elevazione (uno dei 64 fasci laser) e colonna = azimut (1024 direzioni sul giro completo); il pixel contiene distanza, coordinate e intensità. Così la nuvola diventa un'«immagine» e si possono usare CNN 2D (RangeNet++, rif. [10]).</li>
<li><b>Attacco di evasione</b> al momento dell'inferenza: una δ limitata, costruita per <b>massimizzare la loss</b> del modello, si somma all'input; i pesi non si toccano.</li>
<li><b>White box, PGD</b>: accesso al modello e ai gradienti ∇<sub>x</sub>L; aggiornamento iterato x ← Π<sub>ε</sub>(x + α · sign(∇<sub>x</sub>L)); è l'attaccante più forte, il caso peggiore (slide 46).</li>
<li><b>Black box, Square attack</b> (Andriushchenko et al. 2020): solo le uscite del modello; modifiche casuali a forma di <b>quadrato</b> entro ε, tenute se la loss aumenta. È un attaccante realistico senza accesso al modello: niente gradienti, solo query.</li>
</ul>
<p><b>Figura</b>: dati AVL (LiDAR OT128) con ε = 0.3 m. Nella predizione pulita la strada è magenta; nella predizione sotto PGD gli stessi punti diventano <b>vegetazione</b> (verde).</p>
<p><b>Impatto</b>: PGD con ε = 0.3 m porta la mIoU, misurata rispetto alla predizione pulita, a <b>0.056</b>; la pixel accuracy scende a <b>0.26</b>.</p>
<div class="box k"><b>Da capire bene: le metriche e l'ε in metri</b>
<ul>
<li><b>IoU</b> di una classe = |predetti ∩ veri| / |predetti ∪ veri|; <b>mIoU</b> = media sulle classi. È più severa della pixel accuracy perché pesa allo stesso modo le classi piccole.</li>
<li>Qui il «vero» è la <b>predizione sul dato pulito</b>, non l'annotazione manuale: la mIoU misura quanto l'attacco <b>cambia</b> l'uscita del modello. Il pulito, per definizione, ha mIoU 1.</li>
<li>ε = 0.3 m: la perturbazione agisce sui valori della range image misurati in metri; ogni valore cambia al massimo di 30 cm, una quantità confrontabile con il rumore e la risoluzione di un LiDAR a decine di metri.</li>
</ul></div>
""", printed=P(7))

s(59, "Adversarial purification as a pre-processing defence", """
<p><b>Pipeline</b>: input avversario x<sub>adv</sub> = x + δ → <b>purificatore P(·)</b> che rimuove δ → input purificato x̂ = P(x<sub>adv</sub>) ≈ x → modello bersaglio <b>congelato</b>, non riaddestrato → predizioni ripristinate.</p>
<p><b>Figura</b>: tre nuvole segmentate: pulita (strada magenta), attaccata con PGD ε = 0.3 m (strada diventata verde), dopo la purificazione (strada di nuovo magenta, quasi come la pulita).</p>
<p>Tre famiglie di purificatori:</p>
<ul>
<li><b>Basati su denoising</b>: reti addestrate su coppie pulito/avversario; veloci ma legati agli attacchi visti in training.</li>
<li><b>Generativi</b> (GAN, diffusione): proiettano l'input sulla varietà dei dati puliti; indipendenti dall'attacco ma costosi.</li>
<li><b>Model-based</b> (la proposta degli autori): ottimizzazione con un <b>prior</b> (sparsità nel dominio wavelet) risolta con <b>deep unrolling</b>; interpretabile, leggera, in tempo reale.</li>
</ul>
<p><b>Model-agnostic e plug-in</b>: nessun riaddestramento del modello di percezione. Sui dati AVL la purificazione <b>recupera il 40%</b> della mIoU persa per l'attacco (0.056 → 0.435).</p>
<div class="box k"><b>Da saper fare: il conto del 40%</b><p>La mIoU è misurata rispetto alla predizione pulita, quindi il pulito vale 1.</p>
<span class="f">persa = 1 − 0.056 = 0.944,   recuperata = 0.435 − 0.056 = 0.379,   0.379 / 0.944 ≈ 0.40</span>
<p>Il 40% è giusto con questa definizione. Non va letto come «la mIoU sale del 40%» (in termini relativi sale di quasi 8 volte, 0.435/0.056 ≈ 7.8) né come «si arriva al 40% del pulito» (si arriva al 43.5%). Con un riferimento diverso, ad esempio la mIoU rispetto alle annotazioni vere, il pulito non vale 1 e il conto cambia.</p></div>
<div class="box k"><b>Da capire bene: purificazione e adversarial training</b><p>L'adversarial training (slide 47) cambia i <b>pesi</b> del modello; la purificazione cambia l'<b>input</b> e lascia il modello com'è. Vantaggio: si applica a modelli già certificati o forniti da terzi (la supply chain del progetto). Limite noto: se l'attaccante conosce anche il purificatore può attaccare la catena P seguito da f nel suo complesso (attacco adattivo); per questo le difese vanno valutate anche contro attacchi che ne tengono conto.</p></div>
""", printed=P(8))

s(60, "Model-based Purification: UniPure", """
<p><b>Figura</b>: lo schema di <b>UniPure</b> (Unified Model-Based Purification), un unico purificatore per RGB e LiDAR.</p>
<ul>
<li><b>Ingressi</b>: in alto un'immagine RGB pulita e la sua versione avversaria; in basso una nuvola LiDAR pulita e la range image avversaria (una striscia verticale in grigio).</li>
<li><b>Blocco centrale</b>: trasformata wavelet discreta (<b>DWT</b>) → <b>soft-thresholding</b> (azzera i coefficienti piccoli, dove sta gran parte della perturbazione) → DWT inversa; con un modulo di consistenza con i dati, un prior di sparsità nel dominio wavelet e un denoiser.</li>
<li><b>Problema di ottimizzazione</b> (per ogni modalità m):
<span class="f">min<sub>x<sub>r</sub></sub>  ½ ‖x<sub>adv</sub> − x<sub>r</sub>‖<sub>2</sub><sup>2</sup> + λ R(x<sub>r</sub>) + γ Q(x<sub>r</sub>)</span>
un termine di fedeltà ai dati (non allontanarsi troppo dall'input osservato), un prior di sparsità wavelet R e un prior appreso Q.</li>
<li>Si risolve con <b>Half-Quadratic Splitting</b> (HQS: si spezza il problema in sottoproblemi più semplici con variabili ausiliarie) e lo si «srotola» in <b>K stadi</b> (deep unrolling): ogni stadio ha un aggiornamento di x (consistenza con i dati), di u (soft-thresholding wavelet) e di z (restauro con una piccola CNN).</li>
<li><b>Uscite</b>: input RGB e LiDAR purificati, passati alle reti di segmentazione (backbone RGB e LiDAR, non modificate); a destra le segmentazioni ottenute.</li>
</ul>
<p>Collegamento con il corso: il soft-thresholding in un dominio di trasformata è l'idea classica di denoising per sparsità; le wavelet sono parenti dei banchi di filtri e delle piramidi di L6–L7. Un attacco l<sub>∞</sub> sparge piccole modifiche su tutti i pixel, che finiscono soprattutto nei coefficienti di dettaglio piccoli.</p>
""", printed=P(9))

s(61, "UniPure restores cleaner segmentation", """
<p><b>Figura</b>: un fotogramma (frame 000400) di una <b>sequenza LiDAR</b> (nel file originale è un video), con la legenda delle classi di SemanticKITTI (car, road, sidewalk, building, vegetation, terrain…). Tre nuvole segmentate: <b>pulita</b>, <b>attaccata</b> (la strada e il marciapiede diventano in gran parte vegetazione e terreno), <b>UniPure</b> (simile alla pulita).</p>
<p>Sotto, il grafico dell'IoU per fotogramma lungo la sequenza (401 fotogrammi): le curve pulita e purificata sono vicine (circa 0.5), quella attaccata resta molto più in basso (circa 0.15–0.2). Le etichette del fotogramma corrente, piccole e lette dall'immagine, sono circa 0.55 (pulito), 0.18 (attaccato), 0.52 (purificato).</p>
<p>Nota: qui il pulito non vale 1, quindi l'IoU è misurata rispetto a un riferimento diverso da quello della slide 58 (probabilmente le annotazioni); i numeri non si confrontano con 0.056 e 0.435.</p>
""", printed=P(10))

s(62, "Perception, Path Planning, Vehicle Control", """
<p><b>Figura</b>: tre blocchi in fila: <b>Perception</b> → <b>Path Planning</b> → <b>Vehicle Control</b>.</p>
<ul>
<li>La percezione è il punto in cui il veicolo costruisce la sua <b>comprensione del mondo</b>.</li>
<li>Se la percezione è compromessa, <b>ogni decisione a valle fallisce</b>: percorsi sbagliati, manovre pericolose, esiti catastrofici.</li>
<li><b>Obiettivo</b> del pilot: rendere sicuri gli strati di percezione e pianificazione, per un'autonomia affidabile.</li>
</ul>
""", sec=("l14-pilot2-fine", "Pilot 2: obiettivo e bibliografia", "slide 62–66"), printed=P(11))

s(63, "References – Autonomous driving foundations", """
<p>Bibliografia, prima parte.</p>
<ul>
<li><b>Survey, standard e regolamenti</b>: survey sulla guida autonoma (Yurtsever et al. 2020); SAE J3016 (i livelli di automazione); ISO/SAE 21434 (cybersecurity dei veicoli); regolamenti UNECE 155 e 156 (gestione della cybersecurity e degli aggiornamenti software, quindi OtA); ISO 21448 SOTIF (sicurezza della funzione prevista); rapporto ENISA-JRC sulla cybersecurity dell'AI nella guida autonoma.</li>
<li><b>Dataset e modelli di percezione</b>: <b>KITTI</b> (Geiger et al. 2012, già incontrato in L13 per lo stereo), <b>SemanticKITTI</b> (segmentazione LiDAR), nuScenes, <b>RangeNet++</b> (la proiezione in range image), <b>LENet</b> (il modello bersaglio della slide 58), OPV2V e DAIR-V2X (percezione cooperativa).</li>
</ul>
""", printed=P(12))

s(64, "References – Attacks & AI supply-chain threats", """
<ul>
<li><b>Attacchi ai sensori e nel mondo fisico</b>: attacchi remoti a camera e LiDAR, accecamento ottico dei LiDAR, attacchi avversari alla percezione LiDAR (Cao et al. 2019), esempi avversari fisicamente realizzabili per il rilevamento LiDAR, attacchi alla fusione camera-LiDAR, spoofing del GPS, adesivi sui cartelli (Eykholt et al. 2018, slide 32).</li>
<li><b>ML avversario, V2X e supply chain</b>: <b>Madry et al. 2018</b> (PGD), <b>Andriushchenko et al. 2020</b> (Square attack), attacchi alla comunicazione multi-agente e alla percezione cooperativa, <b>Poison Frogs</b> (avvelenamento «clean-label»), <b>BadNets</b> (backdoor nella supply chain dei modelli), Tramèr et al. 2016 (<b>furto del modello</b> tramite API di predizione).</li>
</ul>
<p>Ogni voce è etichettata con la minaccia della slide 54 a cui corrisponde.</p>
""", printed=P(13))

s(65, "References – Defences and trust", """
<ul>
<li><b>Purificazione avversaria e robustezza</b>: Defense-GAN (purificazione generativa), denoiser guidato da rappresentazioni di alto livello, <b>purificazione con modelli di diffusione</b> (Nie et al. 2022), DUP-Net per nuvole di punti, <b>algorithm unrolling</b> (Monga, Li, Eldar 2021), UniPure (gli autori), <b>randomized smoothing</b> per la robustezza certificata (Cohen et al. 2019).</li>
<li><b>Difese per sensori, V2X e supply chain</b>: robustezza della percezione LiDAR, percezione collaborativa robusta per consenso, <b>Neural Cleanse</b> (rilevare backdoor), difese certificate dal poisoning, PRADA (rilevare il furto del modello), Uptane (aggiornamenti software sicuri per auto), Hendrycks e Gimpel 2017 (rilevare esempi fuori distribuzione, base della validazione a runtime).</li>
</ul>
""", printed=P(14))

s(66, "Thank you!", """
<p>Slide di chiusura, con la nota di finanziamento: il lavoro è stato svolto nel progetto CoEvolution, finanziato da Horizon Europe (grant agreement n. 101168560); il contenuto non rappresenta l'opinione dell'Unione Europea.</p>
""", printed=P(15))
