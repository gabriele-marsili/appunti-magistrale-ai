# GDL: banca domande per l'orale (1 settembre 2026)

Formato dell'orale. Le slide GDL35 dicono "~3 domande di complessità crescente".
I resoconti di 25 orali reali di giugno-luglio 2026 (Appendice C della dispensa)
mostrano una cosa diversa e più severa:

- gli **argomenti** sono in pratica **due**, con tre livelli di scavo dentro ciascuno;
- la **prima domanda è eliminatoria**: "o lo sai alla prima o esci". Chi non parte,
  esce in pochi secondi, senza che si passi alla seconda.

Questo ribalta in parte la strategia che avevo scritto qui prima. Fino a superare la
prima domanda conta la **copertura**: non puoi permetterti un argomento su cui non sai
nemmeno partire. Superata quella, conta la **profondità**: è lì che si fa il voto.

⚠ Correzione: la versione precedente di questo file diceva "non serve sapere 35 lezioni
in modo piatto". Con la policy eliminatoria è sbagliato — serve eccome, almeno al primo
livello su tutto.

Questo file NON duplica l'Appendice A di `Dispensa_GDL.pdf` (p.174-180), che contiene
già le domande di primo livello per parte. Qui c'è quello che a quella appendice manca:

1. le domande **L2 e L3** (il meccanismo e lo scavo), cioè quelle che fanno il voto;
2. la copertura **lezione per lezione** invece che per parte, per la ripetizione a voce;
3. le **trappole**, cioè i punti dove una risposta plausibile è sbagliata.

**Aggiornamento (agosto 2026)** — la dispensa è stata rivista e ora copre due cose che prima
stavano solo qui:

- **GrIDDD ha un capitolo suo** (Parte VII, cap. 31, p.164-173) con la trattazione del paper
  più le stesse domande L1/L2/L3 che trovi nella PARTE 0 qui sotto. Le due versioni sono
  allineate: usa la dispensa per studiare il contenuto, questo file per interrogarti a voce.
- **Nove delle trappole** sono diventate box «Trappola» dentro i capitoli pertinenti, quindi
  le incontri mentre studi invece di scoprirle solo in fase di ripasso.

Restano esclusive di questo file la copertura lezione per lezione e la gran parte delle
domande L2/L3 sul programma.

- **Appendice C della dispensa** (nuova): 25 orali reali di giugno e luglio 2026, con le
  domande verbatim di una giornata intera, le regole del gioco e la distribuzione degli
  argomenti effettivamente usciti.
- **`Simulazioni_orale_GDL.pdf`** (nuovo): 14 simulazioni ricostruite sugli orali reali,
  con la scala di scavo e le risposte in fondo. È lo strumento da usare nell'ultima
  settimana, quando serve *produrre* invece che rileggere.

Versione web dello stesso materiale, per il drilling a voce dal telefono (una domanda
alla volta, traccia nascosta, segna cosa è crollato):
<https://claude.ai/code/artifact/cac54c2b-fcd6-4497-ba7b-b347d00902e0>

## Come si usa

Ripetizione a voce, un blocco al giorno. Per ogni lezione:

1. rispondi **L1 a voce e senza guardare**, cronometrandoti (max 2 minuti);
2. se L1 è uscita fluida, passa a **L2**: qui puoi usare carta, molte sono derivazioni;
3. **L3 solo dopo**: sono le domande in cui il prof ti porta se stai andando bene.
   Se su una L3 ti blocchi non è un problema, è il segnale che lì c'è il tuo margine.

Regola pratica: se non riesci a spiegare una cosa **senza scrivere formule**, non la sai
abbastanza per l'orale. Le formule sono il secondo passaggio, non il primo.

Legenda: ⭐ = alta probabilità (derivazione iconica o punto ripetuto a lezione).
⚠ = trappola, punto dove la risposta intuitiva è sbagliata.

---

# PARTE 0: il paper GrIDDD (4° assignment)

*Ninniri, Podda, Bacciu, "Graph Diffusion that can Insert and Delete", NeurIPS 2025.*

Fonti: `midterms/fourth/GrIDDD_paper.pdf`, il tuo poster `GrIDDD_poster.pdf`,
`utils and paper/GrIDDD_riassunto.md` e `GrIDDD_approfondimento.md`.

Questa è la sezione da cui parte quasi sicuramente l'orale, per due motivi: è il lavoro
che hai consegnato tu, ed è un paper del gruppo del prof (Bacciu è coautore). Aspettati
che la prima domanda sia larga ("raccontami il paper") e che le successive scavino sui
punti in cui il paper tocca il programma.

## L1: sai raccontarlo

- Racconta GrIDDD in tre minuti: problema, idea, risultato principale.
- Qual è il problema concreto che risolve? (i DDPM su grafi hanno **taglia fissa**:
  decidi quanti atomi prima di iniziare la diffusione e quel numero non cambia più)
- Perché la taglia fissa è un problema serio proprio per le molecole e non, per esempio,
  per le immagini? (molte proprietà chimiche correlano direttamente col numero di atomi;
  per le immagini la risoluzione è una scelta a monte, non una proprietà da ottimizzare)
- Come lo risolvevano prima? (DiGress e MiDi campionano la taglia dalla distribuzione
  empirica del training set; FreeGress la predice con un classificatore ausiliario dal
  condizionamento)
- Perché quelle soluzioni bastano per il *property targeting* ma non per la *property
  optimization*? (nell'ottimizzazione la taglia è legata alla struttura che stai
  modificando, non è un parametro che puoi fissare da fuori)
- Qual è il claim in una frase? (inserimenti e cancellazioni **monotone** di nodi durante
  sia il forward sia il reverse process, incorporate **durante il training**)
- Su quali dataset, e qual è il numero più forte? (QM9 e ZINC-250k; success rate 45.1%
  su QED in property optimization contro 9.4% di GCPN, quasi 5x)

## L2: sai come funziona

- Cosa vuol dire che gli edit sono **monotoni**? (una volta che un nodo è inserito o
  cancellato non cambia direzione)
- Quanti edit servono e come si distribuiscono nel tempo? (|Δ^T| = n^T − n^0; i timestep
  degli edit sono campionati da una distribuzione logistica ζ'(t) che integra a uno,
  con D che controlla *quando* avvengono e w la ripidità della curva)
- ⭐ Spiega il trucco `DEL` / `DEL*`. Perché servono **due** stati e non uno?
  (la cancellazione è modellata come un tipo di atomo aggiuntivo `DEL`, che deve essere
  **assorbente** per garantire la monotonicità; ma uno stato assorbente non si può
  ri-attraversare nel reverse, quindi non potresti mai re-inserire un nodo in fase di
  denoising. `DEL*` è lo stato **transiente** da cui, nel reverse, un nodo può uscire e
  tornare a un tipo proprio)
- Come garantiscono che esattamente |Δ^T| nodi siano in `DEL` al tempo T? (schema ibrido:
  solo |Δ^T| nodi seguono la matrice di transizione speciale Q*^t, gli altri seguono il
  forward standard)
- Com'è il forward standard ereditato da DiGress/FreeGress? (matrici di transizione
  Q_X^t = α^t A_X + (1−α^t) B_X, che interpolano fra identità e distribuzione marginale
  dei tipi di atomo del training set)
- Come funzionano gli inserimenti, e perché sono più semplici delle cancellazioni?
  (un nodo è attivato al timestep s+1 se il modello ha campionato s come tempo di
  inserimento; categoria iniziale campionata dalla marginale m_X, archi da m_E)
- ⭐ Qual è il problema del reverse process, e come lo risolvono? (in G^0 un nodo inserito
  durante il forward **non esiste**, quindi il posterior classico p_θ(x^{t−1}|x^t, x^0)
  non è definito. Introducono un **posterior generalizzato**, Eq. 9, che marginalizza sul
  tempo di attivazione ŝ di ciascun nodo, predetto dal modello)
- A cosa serve la rete ausiliaria g_φ(G^t)? (predice quanti `DEL*` aggiungere al passo t
  prima di passare il grafo al denoiser principale; addestrata in parallelo e solo nei
  timestep in cui ζ'(t) > 0)
- Da cosa è composta la loss? (somma di quattro cross-entropy: nodi X*^0, archi E*^0,
  tempi di attivazione S*, e numero di `DEL*` predetti dalla rete ausiliaria, pesate da
  λ_X, λ_E, λ_S, λ_DEL)
- Come fanno generazione condizionata? (classifier-free guidance di Ho e Salimans 2022,
  con conditional dropout: durante il training con probabilità ρ il vettore y è
  sostituito da un placeholder parametrizzato ȳ; a inferenza si combinano predizione
  condizionata e non condizionata pesando per λ. Stesso meccanismo di FreeGress)

## L3: sai criticarlo e collocarlo

- ⭐ Colloca GrIDDD nella tassonomia generativa del corso (GDL29 slide 5).
  (Explicit → Latent → Variational, stesso ramo dei VAE: entrambi massimizzano un ELBO
  della log-likelihood. Differenza chiave dei diffusion: lo spazio latente ha **la stessa
  dimensionalità dei dati**. GrIDDD eredita la proprietà, con la torsione che quella
  cardinalità ora può cambiare durante il processo)
- Se un diffusion model è un VAE gerarchico con encoder fisso, cosa cambia in GrIDDD?
  (l'encoder non è più del tutto fisso: la parte di edit di taglia è appresa, e la
  dimensione dello spazio latente non è più un invariante del processo)
- ⭐ Perché il caso **MW** (peso molecolare) è quello che racconta meglio il paper?
  (MW correla pesantemente con la taglia del grafo: è esattamente lì che la flessibilità
  di taglia conta. FreeGress dimezza il proprio MAE su MW *grazie* a una rete ausiliaria
  che predice la taglia ottimale dal target; GrIDDD ottiene MAE 4.89 contro 8.96 **senza
  conoscere a priori la distribuzione delle taglie**)
- Discuti il trade-off MAE/validità su QM9. (su μ: MAE 0.66 contro 0.74 di FreeGress ma
  validità 79% contro 83.7%. Su HOMO: MAE peggiore, 0.37 contro 0.32, ma validità 94%
  contro 90.1%. Non è un miglioramento uniforme e va detto)
- Cosa dimostra l'esperimento out-of-distribution? (training su QM9, max 9 atomi, ma
  generazione fino a 15: GrIDDD tiene il 35% di validità a 15 atomi mentre DiGress crolla
  quasi a zero. Dimostra che impara la flessibilità di taglia, non a stare nel range)
- Cosa dice l'ablation? (disabilitando insert/delete il success rate su QED crolla dal
  45.1% al 33.8%: la novità del paper è responsabile del risultato, non un artefatto)
- Perché il baseline naive con classe `PAD` non basta? (genera il 3% di molecole valide
  in più ma è molto peggio su tutto il resto: componenti connesse, cross-entropy)
- ⚠ **Quali sono i limiti dichiarati?** Non improvvisare, sono due e precisi:
  (1) le due reti possono **entrare in conflitto**, il modello principale predice
  un'attivazione e l'ausiliaria una cancellazione nello stesso timestep, il che è
  formalmente illegale nel framework; (2) tende a produrre più molecole **spezzate**, cioè
  con più componenti connesse, perché i nodi inseriti tardi faticano a connettersi prima
  della fine del denoising. Gli autori suggeriscono di usare il numero di componenti
  connesse come feature di input.
- Quanto costa? (30% più lento di FreeGress in training per l'overhead delle due reti;
  in sampling spesso più veloce perché adatta il numero di step al task)
- Come cambieresti il paper? (domanda aperta tipica: il conflitto fra le due reti si
  potrebbe risolvere con un'unica testa che predice l'edit come variabile categoriale a
  tre valori, invece che due reti indipendenti che possono contraddirsi)
- Se dovessi fare la stessa cosa con un **flow matching** su grafi invece che con un DDPM,
  cosa cambierebbe? (il path è deterministico e la cardinalità variabile diventa più
  scomoda: non hai una catena di stati discreti su cui appoggiare uno stato assorbente)
- Ponte con la Parte V: che architettura fa il denoising? È message passing, quindi valgono
  oversmoothing e oversquashing anche qui? Cosa succede a un nodo appena inserito, che ha
  pochi archi, rispetto all'aggregazione dai vicini?

---

# PARTE I: PGM e Causalità (GDL1-6, dispensa cap. 1-6, p.13-35)

## GDL1-2: intro e modelli grafici

- L1: perché serve un modello generativo invece di uno discriminativo? Cosa modella
  p(x, y) che p(y|x) non modella?
- L2: la tassonomia dei modelli generativi (explicit/implicit, latent/visible,
  tractable/intractable). Dove cade ogni modello del corso? ⭐ Questa tassonomia torna
  in GDL29 e serve per collocare il paper.
- L3: se ti do un task, come scegli la famiglia? (criterio: ti serve la likelihood esatta?
  ti serve campionare veloce? ti serve un latente interpretabile?)

## GDL3-4: Bayesian Networks, d-separation

- L1: definisci una BN, disegna un esempio, scrivi la fattorizzazione p(x) = Π p(x_i|Pa(x_i)).
- L1: cos'è la d-separation? Enuncia il criterio sui tre pattern (chain, fork, collider).
- L2: ⚠ il **collider**: perché osservare il collider *crea* dipendenza invece di romperla?
  (explaining away. È la trappola classica: la regola è opposta a chain e fork)
- L2: Markov blanket, MB(X) = Pa(X) ∪ Ch(X) ∪ Pa(Ch(X)). Perché servono anche i **genitori
  dei figli**? (perché il figlio è un collider: condizionarci apre il cammino verso l'altro
  genitore, che quindi va incluso per chiudere)
- L2: ancestral sampling: come campioni da una BN e perché l'ordine topologico è necessario.
- L3: due BN diverse possono codificare le stesse indipendenze? (sì, Markov equivalence
  class: stesso scheletro e stesse v-structure) Che conseguenza ha per lo structure learning?
  (dai soli dati osservazionali non puoi distinguere dentro la classe, quindi non puoi
  identificare la direzione causale di tutti gli archi)

## GDL5: causalità

- L1: differenza fra rete Bayesiana e rete causale.
- L1: gerarchia di Pearl, i tre livelli con un esempio per ciascuno.
- L2: cos'è il do-operator, e cosa fa al grafo? (fissa X rimuovendo gli **archi entranti**)
- L2: ⭐ quando p(y|x) = p(y|do(x))? (nessun backdoor path da X a Y)
- L2: backdoor criterion e formula di aggiustamento p(y|do(x)) = Σ_z p(y|x,z) p(z).
  Le due condizioni su Z: nessun nodo di Z è discendente di X, e Z blocca tutti i backdoor.
- L3: ⚠ perché non basta "condizionare su tutto"? (condizionare su un discendente di X, o
  su un collider, **introduce** bias invece di rimuoverlo. È il punto in cui l'intuizione
  statistica standard sbaglia)
- L3: dammi un esempio di controfattuale che non è esprimibile come intervento.

## GDL6: structure learning

- L1: score-based contro constraint-based, in una frase ciascuno.
- L2: come funziona PC? (parti dal grafo completo, elimina archi con test di indipendenza
  condizionale a cardinalità crescente, poi orienta le v-structure)
- L2: cos'è GES e in cosa differisce (ricerca greedy nello spazio delle equivalence class,
  forward e backward phase).
- L3: cosa puoi identificare **senza** interventi e cosa no? Come rompono l'impasse gli
  ANM (additive noise model)? (asimmetria nella distribuzione dei residui: sotto ipotesi di
  additività e non-gaussianità la direzione diventa identificabile)
- L3: ponte con GDL30: questa domanda ("cosa è identificabile e sotto quali ipotesi") è
  **la stessa** che si pone il Causal Representation Learning, ma su variabili latenti.

---

# PARTE II: learning probabilistico (GDL7-14, cap. 7-13, p.36-67)

## GDL7: variabili osservate

- L1: MLE, MAP, Bayesiano: le tre formule e cosa cambia concettualmente.
- L2: cos'è un prior coniugato e perché è comodo (la posterior resta nella stessa famiglia).
  Beta-Binomiale come esempio.
- L2: posterior predictive: perché è diversa dal plug-in della stima puntuale?
- L3: quando MAP tende a MLE, e perché? (dati che crescono, il prior si diluisce)
  ⚠ MAP non è invariante per riparametrizzazione, MLE sì. Punto sottile e chiedibile.
- L3: Naive Bayes: qual è esattamente l'assunzione e perché funziona in pratica anche
  quando è chiaramente falsa?

## GDL8: EM e GMM

- L1: perché serve EM? Cosa rende intrattabile la MLE con variabili nascoste?
  (la log-verosimiglianza contiene un log di una somma, che non si fattorizza)
- L2: ⭐⭐ **Deriva EM per GMM alla lavagna.** È *la* domanda iconica.
  E-step: γ_ik = π_k N(x_i|μ_k, Σ_k) / Σ_j π_j N(x_i|μ_j, Σ_j).
  M-step: μ_k = Σ_i γ_ik x_i / Σ_i γ_ik, Σ_k analogo pesato, π_k = Σ_i γ_ik / N.
- L2: perché EM **non decresce mai** la likelihood? (l'E-step rende l'ELBO tight, il
  M-step lo aumenta: quindi la likelihood, che è sopra l'ELBO, non può scendere)
- L3: EM converge all'ottimo globale? (no, solo a un punto stazionario; dipende
  dall'inizializzazione. Il GMM ha singolarità: una componente che collassa su un punto
  manda la likelihood a infinito)
- L3: ⭐ riscrivi EM come massimizzazione alternata dell'ELBO in (q, θ). È il ponte diretto
  verso VI e VAE, ed è la risposta che fa la differenza sulla lente #2.

## GDL9-10: HMM

- L1: definisci un HMM: stati, transizioni A, emissioni B, prior π. Quali sono i tre
  problemi classici (valutazione, decodifica, learning)?
- L2: forward-backward. α_t(i) = p(x_{1:t}, S_t=i), ricorrenza
  α_t(i) = b_i(x_t) Σ_j α_{t−1}(j) a_{ji}; β_t(i) = p(x_{t+1:T}|S_t=i).
  Smoothing γ_t(i) = α_t(i) β_t(i) / Z.
- L2: Viterbi. δ_t(j) = b_j(x_t) max_i δ_{t−1}(i) a_{ij}, più backpointer.
- L2: ⚠ **differenza fra Viterbi e la sequenza dei γ argmax**: la sequenza degli stati
  singolarmente più probabili può essere una sequenza **impossibile** (transizione a
  probabilità zero). Viterbi massimizza la sequenza congiunta. Trappola classica.
- L3: Baum-Welch è EM: chi è q, chi è θ, cosa sono γ e ξ nell'E-step?
- L3: complessità di forward-backward, O(T K^2), e perché diventa proibitivo con K grande.

## GDL11: Variational Inference

- L1: perché serve VI? Cosa c'è di intrattabile in p(z|x)? (l'evidenza p(x) al denominatore)
- L2: ⭐ **deriva l'ELBO** e mostra log p(x) = L(q) + KL(q || p(z|x)).
  Corollario: massimizzare l'ELBO equivale a minimizzare la KL, senza mai calcolare p(x).
- L2: assunzione mean-field q(z) = Π_i q_i(z_i); update CAVI
  q_i*(z_i) ∝ exp(E_{q_{−i}}[log p(z, x)]).
- L3: ⚠ perché VI usa KL(q||p) e non KL(p||q)? (reverse KL è **mode-seeking**, tende a
  sottostimare la varianza e a coprire un solo modo; forward KL sarebbe mass-covering ma
  richiede aspettative sotto p, che è proprio quello che non sai calcolare)
- L3: VI contro MCMC: bias e varianza, garanzie asintotiche, costo. Quando scegli quale?

## GDL12: LDA

- L1: descrivi il processo generativo di LDA (per ogni documento θ_d ~ Dir(α), per ogni
  parola z_dn ~ Cat(θ_d), w_dn ~ Cat(β_{z_dn})).
- L2: perché Dirichlet? Cosa controlla α? (α < 1 dà distribuzioni sparse: un documento
  parla di pochi topic, che è l'assunzione realistica)
- L2: collapsed Gibbs contro variational inference per LDA: cosa si integra fuori.
- L3: ⚠ LDA è **bag of words**: cosa perde? E come si collega ai topic model neurali
  (ProdLDA e affini) via amortized inference, cioè lo stesso salto che porta da VI al VAE?

## GDL13: sampling

- L1: rejection sampling e importance sampling: idea e limite principale
  (in alta dimensione l'efficienza crolla).
- L2: MCMC: cos'è una catena di Markov con distribuzione stazionaria target?
  Detailed balance come condizione sufficiente.
- L2: Metropolis-Hastings, criterio di accettazione
  min(1, p(z') q(z|z') / (p(z) q(z'|z))).
- L2: ⭐ **Gibbs è un caso particolare di MH con acceptance 1**: dimostralo sostituendo
  q = full conditional nel rapporto di accettazione.
- L3: cos'è il burn-in, perché i campioni sono correlati, come diagnostichi la convergenza.
- L3: dove ricompare il sampling nel resto del corso? (contrastive divergence in GDL14, il
  reverse process dei diffusion in GDL29, che è campionamento ancestrale su una catena)

## GDL14: modelli non diretti

- L1: MRF contro BN: cosa cambia nella fattorizzazione (potenziali sulle clique, e una
  costante di normalizzazione globale Z).
- L2: perché Z è il problema? (somma su tutte le configurazioni, esponenziale)
- L2: CRF: perché condizionare su x rende il problema più trattabile della modellazione
  congiunta?
- L2: RBM: p(v,h) ∝ exp(v^T W h + a^T v + b^T h). Perché la struttura bipartita è cruciale?
  (le condizionali p(h|v) e p(v|h) fattorizzano, quindi il Gibbs sampling è a blocchi)
- L2: ⭐ contrastive divergence CD-1:
  ΔW ∝ <v h^T>_data − <v h^T>_1-step-Gibbs. Cosa approssima e perché è biased?
- L3: ⚠ perché la fase negativa è il pezzo difficile? (è un'aspettativa sotto il modello,
  cioè richiede campioni dal modello stesso. Questo è **lo stesso problema** che i GAN
  aggirano completamente rinunciando alla densità esplicita: ponte forte da fare)

---

# PARTE III: deep learning fondamentale (GDL15-20, cap. 14-18, p.68-95)

## GDL15-16: CNN

- L1: convoluzione: parameter sharing, sparsità delle connessioni, equivarianza alla
  traslazione. ⚠ equivarianza, non invarianza: l'invarianza la dà semmai il pooling.
- L2: calcola la dimensione dell'output dato input, kernel, stride, padding, dilation.
  Domanda da esercizio, tipica del midterm 2.
- L2: campo recettivo: come cresce con la profondità, e perché dilated conv lo fa crescere
  esponenzialmente (WaveNet).
- L2: LeNet → AlexNet → VGG → ResNet: cosa ha aggiunto ciascuno.
- L2: ⭐ perché funziona la residual connection? (h^{l+1} = h^l + F(h^l): in backprop il
  gradiente ha un cammino diretto con Jacobiano identità, che non si attenua)
- L3: BatchNorm: cosa fa esattamente al forward e al backward, perché si comporta
  diversamente in train e in inference, e perché regolarizza.
- L3: ⚠ perché la conv 1x1 non è inutile? (mixing sui canali e riduzione dimensionale a
  costo basso: è il bottleneck di ResNet e Inception)

## GDL17: propagazione dell'informazione, RNN

- L1: cos'è BPTT e perché serve il troncamento.
- L2: ⭐ **deriva il vanishing/exploding gradient**: il gradiente contiene Π_l J_l, il
  prodotto dei Jacobiani. Se il raggio spettrale è < 1 svanisce, se > 1 esplode.
- L2: rimedi: init (Xavier, He), gradient clipping (per l'exploding), gate, residual, ReLU.
- L3: perché il clipping cura l'exploding ma non il vanishing? (il clipping riscala la
  norma, non ricrea informazione persa: un gradiente numericamente nullo resta nullo)

## GDL18: modelli ricorrenti gated

- L1: LSTM, i tre gate e il cell state:
  f_t = σ(W_f[h_{t−1}, x_t]), c_t = f_t ⊙ c_{t−1} + i_t ⊙ c̃_t, h_t = o_t ⊙ tanh(c_t).
- L2: ⭐ **perché il cell state risolve il vanishing?** (il cammino c_{t−1} → c_t è
  additivo e modulato dal forget gate: se f ≈ 1 il gradiente passa quasi inalterato.
  È lo stesso meccanismo della residual connection, in versione temporale e appresa)
- L2: GRU: due gate (reset e update), niente cell state separato. Trade-off con LSTM.
- L2: Echo State Network: reservoir random fisso con ρ(W) < 1, si allena solo il readout
  lineare. Cos'è la echo state property? (lo stato dipende asintoticamente dall'input e non
  dalle condizioni iniziali) ⚠ Bacciu è l'autore di riferimento su questo: aspettati che
  ci scavi più della media.
- L3: se ESN funziona con pesi random, cosa ci dice sul contributo reale del training
  ricorrente? Quando ha senso preferirlo?

## GDL19: cross-attention

- L1: qual è il bottleneck del seq2seq classico? (tutta la frase compressa in un vettore
  a lunghezza fissa)
- L2: attention additiva di Bahdanau,
  α_t = softmax(v^T tanh(W_h h_t + W_s s)). Chi è query e chi è key qui?
- L3: differenza fra attention additiva e moltiplicativa, e perché quella moltiplicativa
  ha vinto (si implementa come prodotto matriciale, quindi è parallelizzabile su GPU).

## GDL20: transformers

- L1: scrivi self-attention: softmax(Q K^T / sqrt(d_k)) V.
- L2: ⭐ perché si divide per sqrt(d_k)? (con d_k grande i prodotti scalari hanno varianza
  che cresce con d_k, la softmax satura e il gradiente muore)
- L2: complessità O(n^2 d) in lunghezza di sequenza. Da dove viene esattamente?
- L2: multi-head: perché h teste invece di una più grande? (sottospazi di rappresentazione
  diversi, e attention pattern diversi appresi in parallelo)
- L2: positional encoding: perché è **necessario**? (self-attention è permutation
  equivariant: senza posizione, "cane morde uomo" e "uomo morde cane" sono identici)
- L2: BERT contro GPT contro T5: encoder-only, decoder-only, encoder-decoder, e a cosa
  serve ciascuno.
- L3: ⚠ la self-attention è un **grafo completo**: dillo esplicitamente, è il ponte con la
  lente #3. Un Transformer è una GNN su grafo completo con aggregazione per attention.
- L3: cosa cambia con il masking causale, e perché GPT lo usa in training ma non "vede"
  il futuro nemmeno a inferenza.

---

# PARTE IV: generative deep learning (GDL23-31, cap. 19-25, p.96-137)

## GDL23: autoencoder

- L1: autoencoder e bottleneck: cosa impara e cosa NON è (non è un modello generativo:
  non hai un prior da cui campionare).
- L2: undercomplete contro overcomplete, e perché serve regolarizzare.
- L2: denoising AE, sparse AE, contractive AE: quale regolarizzazione impone ciascuno.
- L3: ⭐ **DAE come stimatore della score**: ∇ log p ≈ (g(f(x)) − x) / σ². Vincent 2011.
  È il ponte diretto con GDL31 e con i diffusion: un denoiser *è* uno score estimator.
  Domanda di collegamento ad alto valore.
- L3: manifold hypothesis: cosa dice e perché giustifica il bottleneck.

## GDL24: VAE

- L1: perché un VAE è generativo e un AE no?
- L2: ⭐⭐ **deriva l'ELBO del VAE**:
  log p(x) ≥ E_q[log p(x|z)] − KL(q_φ(z|x) || p(z)), termine di ricostruzione più
  regolarizzazione verso il prior.
- L2: ⭐ **reparametrization trick**: z = μ + σ ⊙ ε con ε ~ N(0, I). Perché senza non
  puoi backpropagare? (il sampling è un'operazione stocastica non differenziabile rispetto
  ai parametri: il trick sposta la stocasticità in ε, che non dipende da φ)
- L2: cos'è l'amortized inference e cosa cambia rispetto a CAVI? (una rete predice q per
  ogni x, invece di ottimizzare parametri variazionali separati per ogni dato)
- L2: posterior collapse: cos'è, perché succede, come si mitiga (KL annealing, β-VAE,
  decoder meno potente).
- L3: ⚠ perché i campioni dei VAE sono **sfocati**? (la likelihood gaussiana equivale a
  una MSE, che è mode-averaging: la media di due modi plausibili è essa stessa il target)
- L3: β-VAE: cosa fa β > 1 e che rapporto ha col disentanglement (ponte con GDL30).

## GDL25: GAN

- L1: scrivi l'obiettivo minimax e spiega chi ottimizza cosa.
- L2: ⭐⭐ **deriva il discriminatore ottimale** D* = p_d / (p_d + p_g), e sostituiscilo
  nell'obiettivo per mostrare che si ottiene 2·JS(p_d || p_g) − log 4.
- L2: perché il non-saturating loss? (all'inizio D vince facile e il gradiente del
  generatore satura: si massimizza log D(G(z)) invece di minimizzare log(1 − D(G(z))))
- L2: mode collapse: cos'è e perché il minimax lo favorisce.
- L2: ⭐ perché WGAN? (se i supporti sono disgiunti, JS è costante a log 2 e il gradiente è
  nullo ovunque; la Wasserstein resta informativa. Vincolo 1-Lipschitz via weight clipping
  o gradient penalty)
- L2: CycleGAN: cycle consistency ||F(G(x)) − x|| + ||G(F(y)) − y||, per training non
  appaiato.
- L3: ⚠ perché non puoi valutare un GAN con la likelihood? (non ne ha una tractabile: è un
  modello **implicito**. Da qui FID e Inception Score, con tutti i loro difetti)
- L3: metti in fila VAE e GAN sull'asse mode-covering / mode-seeking e spiega perché
  ciascuno sbaglia dalla parte opposta.

## GDL27-28: normalizing flows

- L1: idea del cambio di variabile e vincolo fondamentale (trasformazione invertibile e
  che preserva la dimensione).
- L2: ⭐ **deriva la change of variables**:
  log p_X(x) = log p_Z(f(x)) + log|det J_f(x)|, e la composizione come somma dei log-det.
- L2: perché il determinante del Jacobiano è il collo di bottiglia? (O(d³) in generale)
  Come lo aggirano i coupling layer di RealNVP? (Jacobiano triangolare, determinante =
  prodotto della diagonale, inversione O(d))
- L2: MAF contro IAF: chi è veloce in density evaluation e chi in sampling, e perché sono
  speculari.
- L3: ⚠ i flow hanno likelihood **esatta**: allora perché non hanno vinto? (il vincolo di
  invertibilità e di dimensione preservata costa capacità espressiva a parità di parametri,
  e i modelli sono pesanti)
- L3: CNF e ODE neurale: la traccia al posto del determinante. Ponte diretto con GDL31.

## GDL29: diffusion

- L1: forward process e reverse process, a parole, e perché il forward non ha parametri.
- L2: ⭐ scrivi il forward q(x_t|x_{t−1}) = N(sqrt(1−β_t) x_{t−1}, β_t I) e la proprietà
  chiave: q(x_t|x_0) in forma chiusa con ᾱ_t, che permette di campionare un t qualsiasi
  senza simulare la catena.
- L2: ⭐ il training objective semplificato: E||ε − ε_θ(x_t, t)||², cioè predire il rumore.
  Da dove viene, partendo dall'ELBO?
- L2: perché DDPM si può leggere come **VAE gerarchico con encoder fisso**?
- L2: classifier guidance contro classifier-free guidance: cosa cambia e perché la seconda
  ha vinto (non serve un classificatore separato addestrato su dati rumorosi).
- L2: latent diffusion: perché nello spazio latente (costo quadratico nella risoluzione).
- L3: ⚠ trade-off centrale: qualità e stabilità di training ottime, **sampling lento**
  (T step). Tutte le ricerche successive (DDIM, distillation, flow matching) attaccano
  quel punto.
- L3: ponte col paper: nei diffusion **discreti su grafi** cosa cambia rispetto al caso
  continuo? (le matrici di transizione Q^t sostituiscono il rumore gaussiano)

## GDL30: CRL e disentanglement

- L1: cos'è il disentanglement, e perché è desiderabile.
- L2: ⭐ **impossibilità di Locatello 2019**: enunciala con precisione. Senza supervisione
  o bias induttivo, il disentanglement non è identificabile, perché esistono infinite
  trasformazioni del latente che preservano la distribuzione marginale.
- L2: come lo aggirano iVAE (variabile ausiliaria u che rompe l'invarianza) e CITRIS
  (identifiability sotto interventi temporali noti, triplette (x_t, x_{t+1}, I_{t+1})).
- L3: causalità classica contro CRL: nella prima le variabili sono **osservate** e con
  semantica nota, nella seconda sono **latenti** e vanno prima ricavate da x = h*(s).
  È la lente #5 e va saputa raccontare in tre frasi.

## GDL31: score matching e flow matching

- L1: cos'è la score function ∇_x log p(x) e perché è comoda (non richiede la costante di
  normalizzazione Z, che è il problema di GDL14).
- L2: ESM, ISM, DSM: perché quella esplicita è intrattabile e perché la denoising è
  equivalente e praticabile.
- L2: probability flow ODE: la versione deterministica della reverse SDE, stesse marginali,
  permette likelihood esatta. Ponte con i CNF.
- L2: ⭐ flow matching: si regredisce un campo di velocità lungo un path condizionale;
  rectified flow dà traiettorie quasi rettilinee, quindi pochi step di sampling.
- L3: perché flow matching e diffusion coincidono sotto path gaussiani? Cosa guadagni
  davvero scegliendo il path?

---

# PARTE V: GNN (GDL32, cap. 26-28, p.138-152)

⚠ **Risolto, e nel senso opposto**: GDL33 *Deep Learning for Graphs II — Advanced Models*
**non è materiale d'esame**. Verificato sulle slide GDL35 (p.34): «Deep learning for graph II:
Advanced models lecture is not part of exam materials». La nota Todoist del 10/08 che diceva
il contrario era sbagliata ed è stata corretta. Non c'è niente da chiedere al prof.

Oversmoothing, oversquashing e underreaching restano però in programma perché sono trattati
anche dentro GDL32 e nella dispensa (cap. 28): studiali, ma dal deck GDL32, non dal 33.

- L1: perché non puoi applicare una CNN a un grafo? (nessun ordine canonico dei vicini,
  grado variabile, serve invarianza alle permutazioni)
- L2: ⭐ framework message passing:
  h_v^{l+1} = UPDATE(h_v^l, AGG({h_u^l : u ∈ N(v)})), con AGG permutation invariant.
- L2: deriva la GCN come approssimazione spettrale di ordine 1 (Chebyshev sul Laplaciano
  normalizzato) e spiega da dove viene D^{-1/2} A D^{-1/2}.
- L2: GraphSAGE (sampling dei vicini per scalare), GIN (sum + MLP iniettivo, raggiunge il
  limite 1-WL), GAT (attention ristretta ai vicini).
- L2: ⭐ **over-smoothing**: con molti layer le rappresentazioni convergono a un punto fisso
  costante. Mitigazioni: residual, jumping knowledge.
- L2: **over-squashing**: un vicinato che cresce esponenzialmente viene schiacciato in un
  vettore di dimensione fissa. Mitigazioni: global attention, rewiring. ⚠ Non confonderli:
  over-smoothing è omogeneizzazione, over-squashing è perdita di banda.
- L3: espressività e test 1-WL: perché GIN è il massimo ottenibile con message passing
  standard, e che tipo di grafi non sa distinguere?
- L3: confronta GCN, GraphSAGE, GAT, GIN su espressività, scalabilità, costo.
- L3: ponte col paper: il denoiser di GrIDDD opera su grafi, quindi eredita questi limiti.
  Un nodo inserito tardi ha pochi archi: come si lega all'osservazione degli autori sulle
  molecole spezzate?

---

# PARTE VI: RL (GDL34, cap. 29-30, p.153-163)

- L1: definisci un MDP (S, A, P, R, γ). Cosa fa γ e perché serve.
- L2: ⭐ **deriva Bellman expectation** partendo da G_t = R_{t+1} + γ G_{t+1}, e poi la
  Bellman optimality v*(s) = max_a [R + γ Σ P v*].
- L2: policy iteration contro value iteration: cosa itera ciascuno e quale converge in meno
  iterazioni ma con passi più costosi.
- L2: Q-learning: Q(s,a) ← Q(s,a) + α[r + γ max_a' Q(s',a') − Q(s,a)]. Perché è off-policy?
  (il target usa max, non l'azione effettivamente scelta dalla policy di comportamento)
- L2: ⚠ SARSA contro Q-learning: SARSA usa a' effettivamente scelta, quindi è on-policy ed
  è più conservativa (l'esempio del cliff walking è il modo più veloce per raccontarlo).
- L2: DQN, i tre trucchi: experience replay (rompe la correlazione temporale), target
  network (stabilizza il bersaglio), reward clipping.
- L2: ⭐ policy gradient theorem e log-derivative trick: ∇J = E[∇ log π · Q].
- L2: REINFORCE: non biased ma ad alta varianza; il baseline riduce la varianza senza
  introdurre bias. Perché?
- L2: Actor-Critic, e PPO con l'obiettivo clipped min(r Â, clip(r, 1±ε) Â): che problema
  risolve il clipping? (impedire aggiornamenti troppo grandi della policy)
- L3: quando policy-based e quando value-based? (azioni continue o policy stocastica
  necessaria → policy; azioni discrete e Q rappresentabile → value)
- L3: dov'è il legame con il resto del corso? (il policy gradient è lo stesso trucco di
  stima del gradiente attraverso il campionamento che il reparametrization trick risolve
  in modo diverso nei VAE: score function estimator contro pathwise estimator)

---

# Le 5 lenti unificanti

Sono le domande di terzo livello per eccellenza: se le sai raccontare, hai già dimostrato
che il corso lo possiedi tutto. Dettaglio completo in `Dispensa_GDL.pdf` Appendice A e in
`~/.claude/skills/gdl-knowledge/exam-prep.md`.

1. **La famiglia generativa**: VAE (2013) → GAN (2014) → Flows (2014-15) → Diffusion (2020)
   → Flow Matching (2023). Per ciascuno: cosa rilassa del precedente, e a quale prezzo.
2. **L'ELBO** come filo unico: EM (q = posterior esatta, ELBO tight) → VI (q mean-field) →
   VAE (q amortizzato) → Diffusion (ELBO gerarchico). Stessa quantità, vincoli su q
   progressivamente rilassati.
3. **Message passing**: belief propagation (PGM) → GNN → self-attention (grafo completo)
   → GAT (ponte). Stessa formula UPDATE/AGG, cambia il grafo e l'aggregazione.
4. **Attention**: Bahdanau → self-attention → multi-head → GAT. Filo conduttore:
   indicizzare per **contenuto** invece che per posizione.
5. **Causalità classica contro CRL**: variabili osservate contro variabili latenti da
   ricavare; identifiability e cosa la ripristina (interventi, variabili ausiliarie).

Bonus, la domanda che unisce tutto: **dove si colloca GrIDDD in ciascuna delle 5 lenti?**
(lente 1: ramo diffusion, esteso a taglia variabile; lente 2: ELBO gerarchico con posterior
generalizzato; lente 3: il denoiser è message passing su grafo; lente 4: eredita la
classifier-free guidance, non l'attention; lente 5: nessun legame diretto, e saperlo dire
è meglio che forzare un collegamento che non c'è)

---

# Esercizi di codice

Verificato il 12/08 lanciando `./run_tests.sh`: **tutti e 15 gli esercizi sono ancora
rossi**, nessuno iniziato. `numpy` e `pytest` sono già disponibili, il runner parte.

Quindici esercizi non ci stanno nel tempo che resta, e non devono starci: l'orale si
gioca sulla teoria. Questi cinque però pagano più di un'ora di rilettura, perché
scrivere il codice ti dice in dieci minuti se sai davvero una cosa o se la stai solo
riconoscendo quando la rileggi:

| Esercizio | Perché proprio questo | Giorno |
|---|---|---|
| `02_em_gmm_bic` | è la derivazione iconica dell'orale | 17/8 |
| `03_hmm` | ti fa toccare la differenza Viterbi contro argmax dei γ | 17/8 |
| `07_conv_forward` | stesso terreno del midterm 2, ti costringe a decidere assi e stride | 19/8 |
| `11_vae_elbo` | l'ELBO, la seconda derivazione più probabile | 21/8 |
| `12_gan_optimal_d` | D\*, la terza | 21/8 |

Gli altri dieci (`01`, `04`, `05`, `06`, `08`, `09`, `10`, `13`, `14`, `15`) restano
agganciati al giorno del loro argomento nei task Todoist, da fare solo se avanza tempo.

Per AGT ce ne sono quattro (`01_minimax_alfabeta`, `02_shapley_indici`,
`03_core_nucleolo`, `04_gale_shapley`), anch'essi tutti rossi, già distribuiti sui
giorni di ripasso 2-6 settembre. Lì hanno un valore in più rispetto a GDL: fanno da
**oracolo** per correggerti quando rifai il practicetest a mano.

---

# Autovalutazione

Dopo ogni simulazione segna qui cosa è crollato, con la data. Il ripasso mirato dei giorni
26-30/8 si costruisce **solo** su questa lista, non su un ripasso uniforme.

| Data | Domanda | Livello | Cosa è mancato |
|---|---|---|---|
|  |  |  |  |
