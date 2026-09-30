# SPM – Lezione 27: Structured Parallel Programming
## Appunti divisi per slide

---

## SLIDE 1 – Titolo

**SPM: Structured Parallel Programming**
Anno accademico 2025-2026 – Prof. Massimo Torquati

---

## SLIDE 2 – Outline

Gli argomenti trattati nella lezione sono:

- Introduzione e concetti fondamentali della programmazione parallela strutturata
- Pattern di parallelismo su stream: **pipeline** e **farm**
- Pattern di parallelismo sui dati: **map**, **reduce**, **stencil**, **divide & conquer**
- Modello di costo e tempo di esecuzione

---

## SLIDE 3 – Cos'e' e Motivazioni

La **programmazione parallela strutturata** e' una metodologia che mira a semplificare lo sviluppo di applicazioni parallele componendole da un insieme ristretto di pattern ricorrenti e ben definiti. Si contrappone ai metodi tradizionali non strutturati, che mirano all'efficienza assoluta ma spesso producono codice complesso, difficile da mantenere e soggetto a errori.

**Motivazioni principali:**

Esiste un numero limitato di strutture di parallelizzazione ricorrenti che possono essere riconosciute a un adeguato livello di astrazione (es. pipeline, task farm, partitioning). Queste "forme di parallelismo" ricorrenti hanno implementazioni consolidate e riutilizzabili che possono essere "compilate" nel middleware sottostante. E' piu' facile parallelizzare un problema pensando a come ricondurlo a una combinazione di forme note.

**Obiettivo:** chiarezza, manutenibilita' ed efficienza al posto di codice ad hoc di basso livello.

---

## SLIDE 4 – Structured vs. Unstructured Programming

**Programmazione parallela strutturata:**
- Basata su un insieme predefinito di forme parallele composibili e ben valutate.
- Enfatizza la manutenibilita' e una struttura gerarchica chiara dei task.
- Incapsula i dettagli di basso livello nei layer middleware/runtime.
- Rispetta il principio di separazione delle responsabilita' (separation of concerns): la logica applicativa e' separata dalla gestione della concorrenza.

**Programmazione parallela non strutturata:**
- Utilizza meccanismi di concorrenza ad hoc e di basso livello (creazione esplicita di thread, lock, messaggi espliciti).
- Mescola il codice di business logic con il codice di coordinazione e sincronizzazione parallela.
- Offre grande flessibilita' e controllo fine, al costo di maggiore complessita' e soggettivita' agli errori.
- Obbliga il programmatore a gestire manualmente coordinazione, sincronizzazione e consistenza dei dati.

---

## SLIDE 5 – Terminologia

**Pattern paralleli:** astrazioni di alto livello ricorrenti che descrivono modi comuni di organizzare la computazione parallela. Sono template di progettazione riutilizzabili che catturano strutture comuni nei programmi paralleli (es. pipeline, task farm, scan, stencil, map/reduce) e possono essere applicati a classi di problemi paralleli.

**Scheletri algoritmici (Algorithmic Skeletons):** implementazioni concrete o costrutti di libreria che incapsulano pattern paralleli specifici (o combinazioni di pattern) in componenti parallele pronte all'uso. Forniscono un modo strutturato per esprimere il parallelismo e spesso vengono forniti con implementazioni pre-ottimizzate per architetture hardware specifiche. Tipicamente forniti da librerie o framework per semplificare la programmazione parallela.

**Paradigmi paralleli:** framework concettuali ampi per organizzare il pensiero sulla computazione parallela. Forniscono una classificazione generale degli approcci al parallelismo, incorporando sia metodologie strutturate che non strutturate. Spesso legati a specifici modelli di programmazione (shared-memory, distributed-memory, dataflow, BSP, Actor model).

---

## SLIDE 6 – Obiettivi delle Astrazioni di Alto Livello

Le astrazioni di alto livello per il parallelismo servono a:

**Nascondere la complessita' di basso livello:** liberare i programmatori dall'implementare i meccanismi e le politiche necessari al pattern parallelo. Prevenire codice boilerplate ripetitivo, permettendo ai programmatori di concentrarsi sulla logica applicativa.

**Separazione delle responsabilita':** mantenere la funzionalita' domain-specific distinta dalla gestione della concorrenza.

**Maggiore manutenibilita' e riusabilita':** fornire pattern paralleli standard applicabili su varie applicazioni.

**Esempi di pattern paralleli ampiamente usati:**
- **MapReduce:** divide i dati in chunk (map), li processa in parallelo, e fonde i risultati (reduce).
- **Pipeline:** divide la computazione in un insieme di stadi, ciascuno che lavora simultaneamente su passi diversi del flusso di dati.
- **Master-Worker (Task Farm):** un coordinatore centrale (master) distribuisce task tra piu' Worker che li eseguono in parallelo.

---

## SLIDE 7 – Metriche di Prestazioni Base (Recap)

Definizioni fondamentali per valutare le prestazioni di un sistema:

**Latenza (L):** tempo dall'arrivo di un input (richiesta) fino a quando l'output (risposta) e' pronto per essere consegnato. Nel contesto della teoria delle code e del networking, la latenza e' nota come Response Time. Include il tempo di attesa piu' il tempo di servizio. `L = T_c` se c'e' un solo task da computare.

**Completion time (T_c):** tempo totale che un'applicazione impiega per completare tutti i task, dall'inizio alla consegna di tutti i risultati. Spesso detto makespan.

**Service time (T_s):** tempo necessario al sistema per elaborare un task, escludendo il tempo di attesa. A regime e a piena utilizazione, il tempo tra due completamenti consecutivi di task approssima il service time.

**Throughput:** numero di task completati per unita' di tempo. A regime e a piena utilizzazione, e' l'inverso del service time (1/T_s).

**Inter-arrival time (T_a):** tempo medio tra l'arrivo di due task consecutivi al sistema.

---

## SLIDE 8 – Parallelismo su Stream (Recap)

Uno **stream di task** e' una sequenza continua e ordinata di unita' computazionali (chiamate task) dello stesso tipo che vengono elaborate una dopo l'altra:
```
x_1, x_2, ..., x_m, ...   dove x_1 ≺ x_2 ≺ ... ≺ x_m ≺ ...
```

Ogni task nello stream rappresenta tipicamente un'unita' discreta di lavoro (una computazione, trasformazione di dati, operazione di processo) che contribuisce all'obiettivo complessivo del sistema. In streaming, solitamente ma non sempre, la lunghezza dello stream e' infinita o molto grande.

**Terminologia:** stream source e sink sono il primo e l'ultimo stadio del workflow di computazione (di solito una pipeline) che producono e consumano lo stream di task.

**Il principale pattern parallelo per il parallelismo su stream e' la pipeline.**

**Obiettivo del parallelismo su stream:** ridurre il service time (aumentare il throughput).

---

## SLIDE 9 – Pipeline (1/2)

Il **parallelismo a pipeline** e' un pattern di progettazione parallelo che migliora l'efficienza computazionale dividendo una computazione in una sequenza di stadi, dove ogni stadio elabora i dati e passa l'output allo stadio successivo. Gli stadi operano concorrentemente, abilitando la sovrapposizione della computazione e migliorando il throughput.

**Analogia:** una linea di assemblaggio automobilistica, dove ogni stazione esegue un compito specifico su unita' diverse contemporaneamente.

**Obiettivo:** migliorare il throughput sovrapponendo l'esecuzione di task distinti in ingresso.

**Schema:**
```
stream input --> | f_1 | --> | f_2 | --> ... --> | f_k | --> stream output
                   stadio1    stadio2              stadiok
```

Formalmente, la pipeline calcola in parallelo la composizione di k funzioni f_1, ..., f_k su tutti gli elementi dello stream x_1, x_2, ...:
```
F = f_k ∘ f_{k-1} ∘ ... ∘ f_1
F(x_m) = f_k(f_{k-1}(...f_1(x_m)...))
```

---

## SLIDE 10 – Pipeline (2/2)

**Definizione formale della pipeline:**

```
pipe(f_1, ..., f_k)(x_1, x_2, ...) = F(x_1), F(x_2), ...
                                    = f_k(f_{k-1}(...f_1(x_1)...)), f_k(f_{k-1}(...f_1(x_2)...)), ...
```

**Tipizzazione:** se l'input e' uno stream di elementi di tipo X:
- f_1: X → Y_1
- f_2: Y_1 → Y_2
- ...
- f_k: Y_{k-1} → Y_k

Il tipo della pipeline e':
```
pipe(f_1, ..., f_k): X → Y_k
```

**Nota fondamentale:** a differenza della composizione sequenziale delle funzioni, in una pipeline i diversi stadi elaborano *diversi* elementi dello stream *contemporaneamente*, ottenendo l'overlap che genera il guadagno in throughput.

---

## SLIDE 11 – Perche' e' Efficiente? (1/2)

**Perche' la pipeline aumenta l'efficienza?** Perche' le computazioni di f_i su task di input diversi si sovrappongono.

**Esempio concreto (k=3 stadi bilanciati):**

Dati:
- F(x) impiega 75 unita' di tempo sequenzialmente: T_s^seq = 75
- F() puo' essere suddivisa in 3 sottofunzioni: F(x) = f_3(f_2(f_1(x)))
- Ogni stadio impiega circa 25 unita': T_s^stage = 25
- n task in ingresso, costo di comunicazione inter-stadio T_comm ≅ 0

**Domande:**
- Qual e' il throughput della pipeline a 3 stadi?
- Qual e' il service time della pipeline a 3 stadi?

Intuizione: nella fase steady-state, i 3 stadi lavorano in parallelo su 3 task diversi contemporaneamente, quindi ogni 25 unita' di tempo viene completato un task (rispetto a 75 in sequenziale).

---

## SLIDE 12 – Perche' e' Efficiente? (2/2)

**Timing diagram della pipeline a 3 stadi bilanciati (T_s^stage = 25, T_comm ≅ 0):**

```
Stadio1: |f1(x1)| |f1(x2)| |f1(x3)| ... |f1(xn)|
Stadio2:          |f2(x1)| |f2(x2)| |f2(x3)| ... |f2(xn)|
Stadio3:                   |f3(x1)| |f3(x2)| |f3(x3)| ... |f3(xn)|
         <fill>   <---------- steady state ---------->  <drain>
```

- Throughput sequenziale: n / (n * 75) = 1/75 task per unita' di tempo
- Throughput pipeline (n grande): n / ((n+2) * 25) ≅ 1/25

**Guadagno:** throughput triplicato rispetto al sequenziale (speedup = 3).

**Caso stadi non bilanciati** (T_s^stage1 ≠ T_s^stage2 ≠ T_s^stage3):
- Il servizio della pipeline e' determinato dallo **stadio piu' lento (bottleneck)**.
- Con aggiustamenti, bisogna intervenire sul bottleneck per non penalizzare l'intera pipeline.
- `T_s^pipe ≅ max_i(T_s^stage_i)`

---

## SLIDE 13 – Completion Time della Pipeline

**Analisi del completion time con n = 300 task, T_comm trascurabile:**

```
T_c^seq = n * T_s^seq = 300 * 75 = 22500
T_c^pipe,3 = (k-1) + n * T_s^stage = 2 + 300 * 25 = 7550
Speedup S(3) = 22500 / 7550 ≅ 2.98
```

**Con T_comm ≠ 0 (T_comm = 5 < T_s^stage = 25):**
```
T_c^seq = n * T_s^seq = 22500
T_c^pipe,3 = 2*(T_s^stage + T_comm) + (n-1)*(T_s^stage + T_comm) + T_s^stage = 9055
Speedup S(3) ≅ 2.48
```

**Nota fondamentale:** la **latenza peggiora** passando al parallelo. Per un singolo task:
- Latenza sequenziale: L_seq = T_s^seq = 75
- Latenza pipeline a 3 stadi: L_pipe,3 = T_s^seq + 2 * T_comm = 75 + 2*5 = 85

La pipeline aumenta il throughput ma peggiora la latenza per singolo task!

---

## SLIDE 14 – Completion Time con Stadi Bilanciati

**Formula generale per una pipeline di k stadi bilanciati:**

**Caso: lo stadio sink NON invia l'output (il risultato rimane localmente):**
```
T_c^pipe,k(n) = (n + k - 1) * (T_s^stage + T_comm) - T_comm
```

**Caso: lo stadio sink invia l'output:**
```
T_c^pipe,k(n) = (n + k - 1) * (T_s^stage + T_comm)
```

**Nota:** nel timing diagram si assume che non ci sia overlap tra computazione e comunicazione. Se l'overlap e' presente (caso ideale), il service time effettivo diventa `max(T_s^stage, T_comm)`.

---

## SLIDE 15 – Stadi non Bilanciati

**Esempio:** T_s^stage1 = 15, T_s^stage2 = 25, T_s^stage3 = 12; T_comm = 5; n = 300

```
T_c^seq = n * (15 + 25 + 12) = 300 * 52 = 15600
T_c^pipe,3 = T_s^stage1 + T_comm + n * (T_s^stage2 + T_comm) + T_s^stage3
           = 15 + 5 + 300 * (25 + 5) + 12 = 9032
```

Nota: il tempo e' simile a quello di una pipeline dove tutti gli stadi hanno il service time dello stadio piu' lento (stage2 = 25):
```
T_c^pipe,3 ≅ (300 + 2) * (25 + 5) - 5 = 9055
```

**Conclusione fondamentale:** nella steady-state, **lo stadio piu' lento (bottleneck) detta il service time dell'intera pipeline**.

**Formula approssimata (n grande):**
```
T_c^pipe,k(n) ≅ L_pipe,k + (n-1) * T_s^pipe,k
```
dove `T_s^pipe,k = max_i(T_s^stage_i + T_comm)` (senza overlap di computazione e comunicazione).

---

## SLIDE 16 – Modello di Costo della Pipeline

**Dati:** pipeline di k stadi; T_s^seq(F) = somma di tutti i T_s^stage_i.

**Service time della pipeline:**
```
T_s^pipe,k = max_{i=1..k} T_s^stage_i,comm(f_i)
```
dove il service time di ogni stadio, tenendo conto della comunicazione:
- Senza overlap: `T_s^stage_i,comm = T_f_i + T_comm`
- Con overlap: `T_s^stage_i,comm = max(T_f_i, T_comm)`

**Latenza per un singolo task:**
```
L_pipe,k = T_s^seq(F) + (k-1) * T_comm   (senza overlap computazione-comunicazione)
```

**Completion time per n task:**
```
T_c^pipe,k(n) ≅ L_pipe,k + (n-1) * T_s^pipe,k
              ≅ n * T_s^pipe,k   (se n >> k)
```

**Condizione di bottleneck:** lo stadio i e' un bottleneck se il suo service time e' superiore all'inter-arrival time dei task (T_a):
```
T_s^stage_i,comm(f_i) > T_a^stage_i
```
Se gli input buffer non sono limitati, un bottleneck causa la crescita indefinita della coda di input. Rimedi: ridurre il costo, parallelizzare lo stadio (farm), cambiare la decomposizione, applicare backpressure.

---

## SLIDE 17 – Trovare il Numero Minimo di Stadi

**Problema:** data una funzione F con inter-arrival time T_a, quanti stadi k sono necessari per evitare il bottleneck?

**Condizione necessaria** (stadi bilanciati, caso ideale):
```
T_s^seq(F) / k ≤ T_a
```

**Condizione aggiuntiva:** minimizzare la latenza L_pipe,k = T_s^seq(F) + (k-1) * T_comm.

**Formula per il numero minimo di stadi:**
```
k_min = ⌈ T_s^seq(F) / T_a ⌉
```

Minimo k che soddisfa entrambe le equazioni (non il bottleneck + minimizzare la latenza).

**Interpretazione:** se il task arriva ogni T_a unita' di tempo, e il calcolo sequenziale di F richiede T_s^seq, il numero minimo di stadi bilanciati e' il rapporto tra i due. Con meno stadi, la pipeline sarebbe in bottleneck.

---

## SLIDE 18 – Farm (1/2)

Un **task farm** (o semplicemente farm) e' un pattern computazionale che migliora l'efficienza replicando la stessa funzione (stateless) F k volte. Ogni replica e' eseguita da uno stadio chiamato **Worker**.

**Obiettivo:** migliorare il throughput di un singolo stadio (al contrario della pipeline che lo fa suddividendo la computazione in piu' stadi).

**Schema:**
```
                     F_1 (Worker 1)
input stream --> E | F_2 (Worker 2) | C --> output stream
                     ...
                     F_k (Worker k)
```
L'Emitter (E) distribuisce i task ai Worker; il Collector (C) raccoglie i risultati.

---

## SLIDE 19 – Farm (2/2)

**Definizione formale:** una farm applica la stessa funzione stateless F a tutti gli elementi di uno stream di input:
```
farm(F)(x_1, x_2, ...) = F(x_1), F(x_2), ...
```

**Tipizzazione:**
```
F: X → Y
farm(F): X → Y
```

**Nota importante:** il pattern farm nella sua forma standard **non preserva l'ordine input-output**. I Worker possono completare i task in ordine diverso da quello di arrivo. Quindi in generale:
```
farm(F)(x_1, x_2, ...) = ..., F(x_{m+1}), F(x_m), ...
```
Se il preservare l'ordine e' necessario, bisogna usare strategie apposite (vedi slide 26).

---

## SLIDE 20 – Scheletri di Farm

In letteratura e nella pratica esistono diverse varianti dello scheletro farm:

- **Emitter-Worker-Collector (E-W-C):** il piu' comune. L'Emitter riceve i task e li smista ai Worker; il Collector raccoglie i risultati e li invia in output.
- **Solo Emitter (no Collector):** i Worker inviano direttamente l'output, utile quando non e' necessario aggregare i risultati.
- **Pipeline di farm (farm con farm):** piu' Emitter in pipeline che alimentano Worker condivisi.
- **Farm con feedback loop:** i Worker possono reinserire task nell'Emitter (utile per algoritmi branch-and-bound o generazione ricorsiva di task).
- **Versioni distribuite:** Emitter e Collector distribuiti su piu' nodi.

La variante piu' comune nel corso ha un Emitter e un Collector, con k Worker.

---

## SLIDE 21 – Completion Time della Farm

**Assunzioni:**
- Un Emitter e un Collector con service time T_s^E = T_s^C (solo scheduling e raccolta, computazione trascurabile).
- k Worker; T_s^E < T_a (Emitter non e' il bottleneck) e T_s^E < T_s^W.
- n task nello stream.

**Formula del completion time:**
```
T_c^farm,k(n) = (k+1) * T_comm + (n/k) * (T_s^W + T_comm)
```

**Formula generale:**
```
T_c^farm,k(n) = L_farm + (n-1) * T_s^farm,k
```
dove:
- `T_s^farm,k = max(T_s^E, T_s^C, T_s^W,comm / k)` (service time della farm)
- `T_s^W,comm` include sia il tempo di calcolo del Worker che il costo di comunicazione
- `L_farm = T_s^E + T_s^W,comm + T_s^C` (latenza per un singolo task)

**Nota:** T_s^E e' il tempo di servizio dell'Emitter, T_s^C e' quello del Collector, T_s^W e' quello del Worker.

---

## SLIDE 22 – Trovare il Numero di Worker

**Problema:** dato un inter-arrival time T_a per una farm con funzione F e k Worker, qual e' il valore minimo di k?

**Condizione:** Emitter e Collector non devono essere il bottleneck, e la farm non deve essere in bottleneck:
```
max(T_s^E, T_s^C) ≤ T_s^W,comm / k ≤ T_a
```

Quindi:
```
T_s^W,comm / T_a ≤ k ≤ T_s^W,comm / max(T_s^E, T_s^C)
```

**Formula per il numero minimo di Worker:**
```
k_min = ⌈ T_s^W,comm / T_a ⌉
```

**Interpretazione:** se un Worker impiega T_s^W per elaborare un task e arriva un task ogni T_a, servono almeno T_s^W/T_a Worker per stare al passo con l'arrivo dei task (non accumulare coda).

---

## SLIDE 23 – Modello di Costo della Farm

**Schema riassuntivo della farm (E-W1...Wk-C):**

**Service time dei Worker (con/senza overlap di comunicazione):**
```
T_s^W,comm =  T_s^seq + T_comm          (senza overlap)
           o  max(T_s^seq, T_comm)       (con overlap)
```

**Service time della farm:**
```
T_s^farm,k(F) = max(T_s^W,comm(F) / k, T_s^E, T_s^C)
```

**Latenza:**
```
L_farm = T_s^E + T_s^W,comm(F) + T_s^C
```

**Completion time per n task:**
```
T_c^farm,k(n) ≅ L_farm + (n-1) * T_s^farm,k
```

**Condizione di bottleneck della farm:**
```
T_s^farm,k(F) > T_a
```

---

## SLIDE 24 – Task Scheduling (1/2)

L'Emitter deve assegnare i task in ingresso ai Worker garantendo una distribuzione del carico il piu' possibile uniforme.

**Round-Robin (RR):** se tutti i task hanno lo stesso costo computazionale (`F(x_i) ≅ F(x_j)`), la strategia round-robin e' efficace. Il task x_i va al Worker W_j tale che `j = i mod k`. I task vengono distribuiti uniformemente tra i Worker in modo ciclico.

**On-Demand (OD):** quando il costo dei task varia significativamente, bisogna usare la schedulazione on-demand. Ogni task in ingresso viene assegnato dinamicamente al Worker che si rende disponibile per primo. Il Worker invia un messaggio "ready" all'Emitter per notificare la disponibilita' a ricevere un nuovo task.

**Ottimizzazione on-demand:** se lo stream e' abbastanza lungo, il Worker puo' inviare il messaggio "ready" non appena riceve un task (prima di completarlo), in modo che la comunicazione e il calcolo si sovrappongano (il Worker dice "sono pronto per il prossimo" mentre ancora elabora quello corrente).

---

## SLIDE 25 – Task Scheduling (2/2)

**L'Emitter come entita' passiva (implementazione a coda condivisa):**

Invece di un Emitter attivo che smista i task, si puo' usare una struttura a coda:

**Work-Sharing:** tutti i Worker condividono un'unica coda condivisa (concurrent task queue). Ogni Worker preleva un task dalla coda quando si libera. La coda puo' essere protetta da lock o implementata in modo lock-free.

**Work-Stealing:** ogni Worker mantiene la propria coda locale. I task vengono assegnati ai Worker inizialmente (con RR o random). I Worker che hanno esaurito la propria coda ("idle Workers") cercano di rubare (steal) un batch di task dalla coda di altri Worker. Riduce la contesa rispetto al work-sharing (ogni Worker lavora prevalentemente sulla propria coda locale).

Entrambi i meccanismi sono stati visti nel corso nelle lezioni sul ThreadPool.

---

## SLIDE 26 – Preservare l'Ordine Input-Output

In alcuni casi e' necessario preservare l'ordine input-output in una farm (es. elaborazione di frame video: i frame possono essere elaborati indipendentemente, ma l'ordine nel video output deve essere mantenuto).

**Due strategie possibili:**

**1. Schedulazione e raccolta deterministica:** si usa lo stesso ordine nella fase di scheduling e in quella di raccolta. Semplice ma limita il parallelismo (il Collector deve aspettare lo stesso ordine).

**2. Tagging con ID:** l'Emitter aggiunge un tag (un ID numerico) a ogni task schedulato; il Collector rimuove il tag e produce i task in output nell'ordine degli ID.

**Problema del head-of-line blocking:** un task lento con un ID piccolo ritarda l'emissione di task con ID maggiori gia' completati. Il Collector deve bufferizzare i risultati fuori ordine in attesa del task con l'ID atteso. Questo introduce latenza aggiuntiva e consumo di memoria.

---

## SLIDE 27 – Cosa Succede se F e' Stateful? (1/2)

Tradizionalmente, i pattern farm assumono Worker stateless: ogni task e' elaborato indipendentemente e nessun dato interno persiste tra i task. Alcune applicazioni pero' richiedono computazioni stateful.

**Stato read-only:**
- **Memoria distribuita:** ogni Worker mantiene una replica del dato read-only. Non serve sincronizzazione oltre la distribuzione iniziale dei dati.
- **Memoria condivisa:** una singola copia condivisa e' sufficiente.

**Stato read-write** (piu' complesso):
- **Stato monolitico (non partizionabile):** l'intero dato deve essere aggiornato ogni volta che avviene una scrittura. I Worker condividono o replicano un unico stato logico.
- **Stato partizionabile:** si divide lo stato globale in segmenti disgiunti, e ogni Worker gestisce una porzione dello stato.

---

## SLIDE 28 – Cosa Succede se F e' Stateful? (2/2)

**Stato non partizionabile:**
- Le prestazioni dipendono dalla probabilita' di aggiornamenti rispetto alle letture. Il costo scala con la frequenza delle scritture.
- In sistemi shared-memory: si puo' usare uno schema di locking multiple-reader/single-writer (rwlock).
- In sistemi distributed-memory: approccio multicast. I task che aggiornano lo stato vengono inviati a tutti i Worker con un broadcast (oppure lo stato aggiornato viene broadcastato a tutti i Worker).

**Stato partizionabile:**
- Si applica una funzione di hashing al task per identificare la partizione di stato e inviare il task al Worker appropriato.
- I Worker non sono anonimi: l'Emitter deve inviare un task specifico a uno (o un sottoinsieme di) Worker specifici.
- Esempio: deep-packet inspection con stato per-flow (vedi slide 29).

---

## SLIDE 29 – Farm Stateful: Esempio di Stato Partizionabile

**Caso d'uso: deep-packet inspection con stato per-flow**

Ogni pacchetto di rete appartiene a un flusso (identificato dalla 5-tupla: source IP, destination IP, source port, destination port, protocol). L'analisi di ogni pacchetto richiede di accedere allo stato del flusso a cui appartiene.

**Strategia di hashing:**
```
worker_id = hash(flow_key) mod k
```
Il Worker worker_id gestisce tutti i pacchetti del flusso con quella chiave. Questo preserva la localita' per-flow e **evita la sincronizzazione** sullo stato della connessione (ogni Worker ha il proprio stato per i propri flussi).

**Problema di bilanciamento del carico:** il bilanciamento e' solo probabilistico.
- Una buona funzione di hash distribuisce bene molti flussi indipendenti in termini di numero di flussi, ma non necessariamente in termini di volume di traffico.
- Pochi flussi ad alto volume possono concentrarsi sullo stesso Worker, creando sbilanciamento.

---

## SLIDE 30 – Annidamento di Pipeline e Farm

L'**annidamento** permette di costruire applicazioni complesse combinando pipeline e farm su piu' livelli.

**Caso tipico:** l'applicazione e' strutturata come una pipeline di operazioni, mentre all'interno di ogni stadio, una farm viene usata per elaborare piu' task indipendenti in parallelo e aumentare il throughput.

**Schema (pipeline di farm):**
```
S --> | E-W1..Wk-C | --> | E-W1..Wk-C | --> ... --> | E-W1..Wk-C | --> S
       stadio1 (farm)     stadio2 (farm)               stadiom (farm)
```

**Vantaggio:** sfrutta sia il parallelismo temporale (tra i diversi input allo stesso stadio) che il parallelismo spaziale (tra i diversi stadi della pipeline).

**Svantaggio:** i livelli extra prodotti dall'annidamento possono introdurre overhead aggiuntivi di comunicazione e sincronizzazione, aumentando la latenza end-to-end.

---

## SLIDE 31 – E Se Non Abbiamo uno Stream di Task?

I pattern pipeline e farm lavorano su stream di task. Ma cosa succede quando non abbiamo un flusso naturale?

**Stream esogeeni ("exo-stream"):** provengono da una sorgente autentica esterna all'applicazione (sensore, interfaccia di rete, database, ecc.).

**Stream endogeni ("endo-stream"):** generati direttamente dall'applicazione, tipicamente producendo lo stream a partire da iterazioni di ciclo.

**Strategia per dati non-stream (collezioni):** si puo' ottenere uno stream da una collezione monolitica dividendo la collezione in sotto-collezioni e poi ricollezionando i risultati in un'unica collezione. Questo e' il pattern:
```
SplitCollection → Compute → Collect
```
oppure generando uno stream di task dalle iterazioni di un ciclo (es. `taskloop` in OpenMP).

**Attenzione:** produrre uno stream artificialmente non e' sempre l'opzione migliore. L'overhead aggiuntivo di comunicazione potrebbe superare il beneficio del parallelismo.

---

## SLIDE 32 – Esempio Applicativo (1/4)

**Programma sequenziale di riferimento:**
```c
while(EOFcondition(inFile)) {
    X = readFromFile(inFile);   // 100 unita' di tempo
    Y = F(X);                   // 250 unita' di tempo
    Z = G(Y);                   // 600 unita' di tempo
    writeToFile(outFile, Z);    // 80 unita' di tempo
}
```

Dati del problema:
- `readFromFile`: 100 ut; `writeToFile`: 80 ut.
- `F`: 250 ut; `G`: 600 ut.
- F e G possono essere replicate (stateless); le funzioni di I/O sono difficili da parallelizzare.
- T_s^seq = 1030 ut per task.
- T_c^seq = n * 1030 ut.
- Costo di comunicazione per task: T_comm = 20 ut.

**Obiettivo:** ridurre il completion time parallelizzando il codice, assumendo n grande.

---

## SLIDE 33 – Esempio Applicativo (2/4) – Pipeline

**Prima opzione: pipeline a 4 stadi**
```
readFromFile --> F --> G --> writeToFile
T_s^stage1=120  T_s^stage2=270  T_s^stage3=620  T_s^stage4=80
(100+20)        (250+20)        (600+20)        (solo output, no comm)
```

```
T_c^pipe,4(n) ≅ n * max(T_s^stage_i) = n * 620
```

**Analisi:** sia F (270) che G (620) sono bottleneck (il loro service time supera 80, l'inter-arrival time dettato da `readFromFile`). La pipeline semplice non e' sufficiente.

**Soluzione:** usare un pattern farm per F e G per ridurre il loro service time.

---

## SLIDE 34 – Esempio Applicativo (3/4) – Pipeline di Farm

**Seconda opzione: pipeline di farm**
```
readFromFile --> [Farm-F] --> C+E --> [Farm-G] --> writeToFile
T_s^stage1=120
```

Con T_a^stage2 = 120 (dettato dallo stage 1):
- Farm per F: `k_min^stage2 = ⌈270/120⌉ = 3`, nuovo service time di F: 270/3 = 90 ut
- Farm per G: `T_a^stage3 = max(T_s^stage1, T_s^stage2) = 120`, `k_min^stage3 = ⌈620/120⌉ = 6`, nuovo service time di G: 620/6 ≅ 104 ut

I bottleneck sono stati eliminati: ora il bottleneck e' il primo stadio (I/O, non parallelizzabile).

```
T_c^pipe,k(n) ≅ n * 120
```

Risorse usate: 1 (readFile) + 3 (Farm F, k_min=3) + 1 (C+E, trascurabile) + 6 (Farm G) + 1 (writeFile) = 12 risorse.

```
Speedup S(12) = (n * 1030) / (n * 120) ≅ 8.6   (efficienza ≅ 71%)
```

**Nota:** la latenza aumenta da 1030 (sequenziale) a circa 1110, pari a T_s^seq + 4 * T_comm.

---

## SLIDE 35 – Esempio Applicativo (4/4) – Farm Singola ("Forma Normale")

**Terza opzione: farm singola**

Invece di due farm separate per F e G, si usa un'unica farm con una funzione composta F+G:
```
readFromFile --> [Farm (F+G)] --> writeToFile
T_s^stage1=120
```

Con T_a = 120:
- `k_opt = ⌈(250+600+20)/120⌉ = ⌈870/120⌉ = 8`
- Nuovo service time di F+G: 870/8 ≅ 109 ut

```
T_c^pipe,k(n) ≅ n * 120
```

**Confronto con la seconda opzione:**
- Completion time simile: T_c ≅ n * 120.
- **Meno risorse usate:** 8 Worker invece di 3+6=9 (piu' 1 C+E), risparmio di 2 risorse.
- **Latenza inferiore:** meno stadi di pipeline = meno overhead di comunicazione.
- **Efficienza maggiore:** da ~71% a ~86%.

La farm singola e' detta **"forma normale"** perche' rappresenta spesso la soluzione ottimale in termini di efficienza.

---

## SLIDE 36 – Parallelismo sui Dati (Recap)

Il **parallelismo sui dati** considera una collezione di dati in input e produce una collezione di dati in output. In generale, le dimensioni delle collezioni input e output possono differire.

La stessa operazione (o funzione kernel) viene applicata a elementi (o blocchi di elementi) in parallelo su piu' Worker.

**Pattern principali di parallelismo sui dati (cardinalita' input:output):**

| Pattern | Cardinalita' | Esempio |
|---------|-------------|---------|
| Map     | N : N       | Conversione temperatura Celsius → Fahrenheit per ogni elemento |
| Reduce  | N : 1 (o N : M con M<N) | Somma di N numeri; conteggi per classe |
| Stencil | N : N       | Convoluzione 2D |
| Scan    | N : N       | Somme cumulative di N numeri |

**Obiettivo del parallelismo sui dati:** ridurre il completion time (non il service time come nello stream parallelism).

---

## SLIDE 37 – Map (1/2)

Un **map** e' un pattern computazionale in cui una singola funzione F viene applicata indipendentemente a ogni elemento di una collezione di input, producendo una collezione di output della stessa cardinalita'.

**Sfruttamento del parallelismo:** si usa un pool di Worker, ognuno che lavora indipendentemente su una partizione della collezione di input e produce una partizione della collezione di output.

**Schema:**
```
Collezione input (n elementi)
        |
      split/scatter
        |
  F W1  F W2  F W3  ...  F Wk
        |
     collect/gather
        |
Collezione output (n elementi)
```

**Effetti sulle metriche:**
- Il pattern map **riduce la latenza** per computare una singola collezione.
- Se c'e' uno stream di collezioni (senza dipendenze), abbassa il service time e aumenta il throughput.

---

## SLIDE 38 – Map (2/2)

**Definizione formale:** dato un insieme di dati D = {d_1, ..., d_n} e una funzione F, l'operazione map e' definita come:
```
map(F)(D) = {F(d_1), ..., F(d_n)}
```

**Tipizzazione:**
```
d_i ∈ X
F: X → Y
map(F): {X} → {Y}
```

**Differenza fondamentale con la farm:** la farm lavora su stream (flusso continuo di task individuali); il map lavora su una singola collezione che viene elaborata in blocco. Entrambi possono essere implementati con lo stesso scheletro E-W-C, ma il contesto e l'obiettivo differiscono.

---

## SLIDE 39 – Implementazione del Map

Il pattern map puo' essere implementato usando uno scheletro farm (Emitter-Worker-Collector).

**Il problema principale del map e' il bilanciamento del carico:**

**Workload bilanciato:** se ogni elemento della collezione richiede circa lo stesso tempo di elaborazione, l'Emitter puo' distribuire la collezione ai Worker usando una distribuzione a blocchi (block-based distribution). Ogni Worker riceve un blocco contiguo di n/k elementi. Questo caso e' detto **computazione embarrassingly parallel**.

**Workload sbilanciato:** se gli elementi hanno costi diversi (es. rendering di immagini con complessita' variabile), si usa un approccio dinamico:
- **Work-sharing o work-stealing** (approcci passivi): coda condivisa tra tutti i Worker.
- **Distribuzione on-demand coordinata dall'Emitter** (approccio attivo): simile alla farm on-demand.

---

## SLIDE 40 – Modello di Costo del Map

**Setup:** collezione di n elementi; k Worker; un Emitter e un Collector (schema Farm).

**Completion time:**
```
T_c^map(n, k) = T_scatter + T_worker + T_gather
```

dove:
```
T_scatter = T_split(n,k) + k * T_comm(n/k)
T_worker  = (n/k) * T_F + T_comm(n/k)
T_gather  = T_gather(n/k)
```

**Timing diagram:** si noti che il parallelismo a pipeline tra l'Emitter e i Worker, e tra i Worker e il Collector, permette una parziale sovrapposizione dei costi di comunicazione.

**Nota importante:** se la comunicazione (scatter e gather) e' costosa rispetto alla computazione, il beneficio del parallelismo e' ridotto dall'overhead di distribuzione e raccolta dei dati.

---

## SLIDE 41 – Trovare il Numero Ottimale di Worker per il Map

**Modello di comunicazione lineare:** `T_comm(n) = t_0 + n * s` (latenza base + costo proporzionale alla dimensione del messaggio).

Assumendo `T_split(n,k) ≅ 0` e `T_gather(n/k) ≅ 0`:
```
T_c^map(n, k) = k * T_comm(n/k) + (n/k) * T_F + T_comm(n/k)
              = (k+1) * (t_0 + (n/k)*s) + (n/k) * T_F
```

**Minimizzazione rispetto a k:**
```
d T_c^map / dk = 0  -->  k_opt = sqrt(n * (T_F + s) / t_0)
```

**Esempio numerico:** t_0 = 2 µs, BW = 200 MB/s, n = 100M elementi, T_F = 1 µs, s = 8 byte / 200 MB/s = 0.04 µs.

```
k_opt = sqrt(100M * (1 + 0.04) / 2) ≅ 7211
T_c^seq ≅ 100s
T_c^map(1024) ≅ 4.10s
T_c^map(k_opt) ≅ 4.02s
```

**Conclusione:** k_opt e' un numero molto grande perche' n e' grande e t_0 e' piccolo. In pratica k = 1024 (numero di core disponibili) e' quasi ottimale.

---

## SLIDE 42 – Scatter ad Albero Binario

**Problema dello scatter centralizzato:** se l'Emitter invia i dati a tutti i Worker in sequenza, il suo service time scala linearmente con k. Per k grande, l'Emitter diventa il bottleneck.

**Soluzione: scatter ad albero binario**

**Vista logica (k=4):**
```
      E
     / \
   W1   W2
       / \
     W3   W4
```

**Vista implementativa (k=8):** stessa struttura ma con log_2(8)=3 livelli.

**Service time dell'Emitter:**
```
T_s^E = 2 * T_comm(n/2)   (nessun overlap tra i 2 invii)
```

**Latenza dello scatter:**
```
T_scatter = 2 * sum_{i=1}^{log_2(k)} T_comm(n/2^i)
```

Con lo scatter ad albero binario, la latenza di scatter scala come O(log k) invece di O(k).

---

## SLIDE 43 – Gather ad Albero Binario

**Analogamente:** il gather centralizzato scala linearmente con k. Per ridurre il service time del Collector, si usa un **gather ad albero binario**.

**Vista logica (k=4):**
```
W1   W2
     / \
   W3   W4
     \
      C
```

**Service time del Collector:**
```
T_s^C = 2 * T_comm(n/2)   (nessun overlap tra le 2 ricezioni)
```

**Latenza del gather:**
```
T_gather = 2 * sum_{i=1}^{log_2(k)} T_comm(n/2^i)
```

Come lo scatter, la latenza di gather scala come O(log k).

---

## SLIDE 44 – Modello di Costo Map con Filesystem Parallelo (1/2)

**Contesto diverso:** invece di una stream di task, si ha un programma che legge e scrive da file. Si considera la seguente struttura sequenziale:
```c
while(!EOFcondition(inFile)) {
    X = readFromFile(inFile);
    Y = F(X);
    Z = G(Y);
    writeToFile(outFile, Z);
}
```

**Applicazione del pattern Map:** poiche' tutti i task sono disponibili contemporaneamente (nel file) e sono indipendenti, li si puo' vedere come una collezione e applicare il Map.

**Strategia:**
1. Il file di input viene suddiviso in k sotto-collezioni (sub-file).
2. Ogni Worker legge e elabora indipendentemente la propria sotto-collezione.
3. I risultati vengono raccolti (merge) in un'unica collezione di output.

Tipicamente, quando la dimensione totale dell'output e' nota, si usa un **sparse file** come output, in modo che ogni Worker possa scrivere in regioni indipendenti senza conflitti.

---

## SLIDE 45 – Modello di Costo Map con Filesystem Parallelo (2/2)

**Formula del completion time (k Worker, nessun Emitter/Collector esplicito):**
```
T_c^map(n, k) = T_split + (n/k) * T_{F+G} + T_merge
```

**Vantaggi rispetto alla versione con Farm:**
- Si usano solo k risorse (non k+2 come nella farm con Emitter e Collector).
- Potenziale vantaggio di un filesystem parallelo (I/O parallelo): se i dati sono gia' distribuiti, l'overhead di split e' minimo; split e merge sono operazioni logiche che non spostano fisicamente i dati.
- `T_c^map(n,k) ≈ n/k * T_{F+G}`, che puo' essere significativamente piu' basso rispetto all'I/O centralizzato.

**Nota (Hadoop/HDFS):** Hadoop's HDFS mantiene una vista logica dei dati, mentre la sua organizzazione fisica favorisce operazioni efficienti di scatter/gather durante le computazioni map-reduce. Lo split e il merge di HDFS sono appunto operazioni logiche che non richiedono movimento fisico dei dati.

---

## SLIDE 46 – Specializzazioni del Map

Il pattern map standard segue lo schema Scatter → Compute → Gather. Esistono pero' casi dove la distribuzione dell'input e' diversa.

**Caso: Map con broadcast di una collezione**

Si ha:
- Una collezione C partizionata tra tutti i Worker.
- Una seconda collezione di elementi X (una stream di X).
- Una funzione Worker F tale che `y_i = F(x_i, C)` (ogni elemento x_i ha bisogno dell'intera C per essere elaborato).
- Output: stream di collezioni Y = {Y_1, Y_2, ..., Y_#X} dove `Y_i = {y_1, ..., y_#C}`.

**Schema di distribuzione:**
- C viene distribuita ai Worker con scatter.
- Ogni x_i viene inviato (broadcast) a tutti i Worker.
- Ogni Worker elabora F(x_i, C_locale) e produce la propria parte di Y_i.
- I risultati vengono raccolti con gather.

---

## SLIDE 47 – Reduce (1/2)

Un **reduce** e' un pattern computazionale usato per aggregare o combinare risultati da computazioni parallele in un unico output. Opera su una collezione di input e produce un singolo elemento.

**Definizione:**
```
x = reduce(C, ⊕)   dove ⊕ e' l'operatore aggregante (almeno associativo)
```

La commutativity da' maggiore liberta' al runtime di riordinare gli operandi liberamente.

**Schema parallelo ad albero:**
Il parallelismo viene sfruttato organizzando la computazione come un albero bilanciato:
- Le foglie combinano coppie di input (elementi pari e dispari).
- I nodi interni applicano ⊕ ai risultati dei loro sottoalberi sinistro e destro.
- La radice produce il risultato finale.

**Profondita' dell'albero:** O(log n), quindi la latenza parallela scala logaritmicamente.

---

## SLIDE 48 – Reduce (2/2)

**Definizione formale:** dato un insieme D = {d_1, ..., d_n} e un operatore binario associativo ⊕, la funzione reduce e':
```
reduce(⊕)(D) = d_1 ⊕ d_2 ⊕ ... ⊕ d_n
```

**Tipizzazione:**
```
d_i ∈ X
⊕: X × X → X
reduce(⊕): {X} → X
```

**Nota sull'associativita':** l'associativita' garantisce che il risultato sia lo stesso indipendentemente dall'ordine in cui si eseguono le operazioni parziali (purche' l'associativita' sia rispettata). La commutativity permette di riordinare anche gli operandi stessi, dando ancora piu' liberta' all'implementazione parallela.

---

## SLIDE 49 – Implementazioni del Reduce

**Setup:** la collezione di input e' partizionata tra k Worker; ogni Worker calcola il reduce sulla propria partizione locale.

**1. Reduce ad anello (ring-based Reduce):** solo l'associativita' e' necessaria.
- Round 0: il Worker i invia il proprio valore locale al Worker (i+1) mod k, e riceve da (i-1) mod k.
- Round 1, ..., k-1: ogni Worker invia il valore ricevuto al successivo.
- Dopo k-1 round, tutti i Worker hanno il valore ridotto.
- Adatto per messaggi bandwidth-bound (grandi blocchi di dati).

**2. Reduce ad albero (tree-based):**
- Solo un Worker avra' il valore ridotto finale alla radice dell'albero.
- Variante **All-Reduce**: tutti i Worker ottengono il valore ridotto al termine.
- Richiede sia associativita' che commutativity per la massima efficienza.
- Numero di round: O(log k), migliore del ring per latency-bound messages.

---

## SLIDE 50 – All-Reduce

**All-Reduce con algoritmo recursive doubling (log_2(k) round):**

Algoritmo:
```c
void all_reduce(id, k, localdata, ⊕) {
    distance = 1;       // round iniziale
    pr = localdata;     // copia locale del dato parziale
    while (distance < k) {    // log_2(k) round paralleli
        partner = id ^ distance;    // trova il partner (XOR bit a bit)
        send-receive(partner, pr, r); // scambio bidirezionale con il partner
        pr = pr ⊕ r;               // calcola il risultato parziale
        distance <<= 1;            // prossima potenza di 2
    }
    localdata = pr;    // valore finale
}
```

**Esempio con 8 Worker (W0..W7):**
- Distance=1: W0 ↔ W1, W2 ↔ W3, W4 ↔ W5, W6 ↔ W7 (4 coppie in parallelo)
- Distance=2: W0 ↔ W2, W1 ↔ W3, W4 ↔ W6, W5 ↔ W7 (4 coppie)
- Distance=4: W0 ↔ W4, W1 ↔ W5, W2 ↔ W6, W3 ↔ W7 (4 coppie)

Dopo 3 round, tutti gli 8 Worker hanno il valore globale ridotto.

**Nota:** questo algoritmo funziona solo se k e' una potenza di 2. Alcune implementazioni MPI lo usano per messaggi di piccola-media dimensione quando k e' una potenza di 2.

---

## SLIDE 51 – Modello di Costo del Reduce

**Setup:** collezione di n elementi; k Worker; operatore di riduzione ⊕.

**Completion time:**
```
T_c^reduce(n, k) = T_scatter + T_local + T_*-reduce
```

dove:
```
T_scatter = T_split(n,k) + k * T_comm(n/k)

T_local = (n/k) * T_⊕

T_tree-reduce = log_2(k) * (T_⊕ + T_comm(1))
T_all-reduce  = log_2(k) * (T_⊕ + 2 * T_comm(1))
```

**Trovare il k ottimale:** minimizzare `T_c^reduce(n, k)` su k, analogamente a quanto fatto per il map.

**Struttura dell'albero di riduzione:**
- Livello 1: k/2 operazioni ⊕ parallele.
- Livello 2: k/4 operazioni.
- ...
- Livello log_2(k): 1 operazione ⊕ finale.

---

## SLIDE 52 – Map + Reduce (1/2)

**Combinazione dei pattern Map e Reduce:**

L'operazione Reduce e' spesso combinata con il Map (o altri pattern di parallelismo sui dati). Logicamente, e' una pipeline di due stadi: uno che calcola il Map, uno che calcola il Reduce.

**Caso senza dipendenze (stream di collezioni):** se si ha uno stream di collezioni e non ci sono dipendenze tra le iterazioni, le due fasi possono essere eseguite effettivamente in pipeline:
```
pipe(Map(F), Reduce(⊕))
```

Schema equivalente con Worker separati per Map e Reduce:
```
E --> W_M^1..W_M^m --> C --> E --> W_R^1..W_R^r --> C
       (fase Map)                   (fase Reduce)
```

Oppure, con Worker combinati:
```
E --> W_M^1+W_R^1 .. W_M^m+W_R^m --> C
       (ogni Worker fa Map + Reduce locale)
```

---

## SLIDE 53 – Map + Reduce (2/2)

**Implementazione pratica combinata (piu' efficiente):**

Invece di due stadi di pipeline separati, si combina Map e Reduce in tre passi:

1. **Scatter:** ogni Worker riceve una partizione della collezione iniziale.
2. **Map + Reduce locale:** ogni Worker calcola il Map sulla propria partizione e applica l'operatore di riduzione ⊕ localmente (producendo un singolo valore parziale).
3. **Reduce globale:** tutti i Worker scambiano (o raccolgono) i valori delle reduce locali per calcolare il valore finale.

**Schema:**
```
scatter --> W1 [Map+LocalReduce] --> global All-Reduce --> output
scatter --> W2 [Map+LocalReduce] --> global All-Reduce --> output
...
scatter --> Wk [Map+LocalReduce] --> global All-Reduce --> output
```

Questo approccio riduce il volume di dati che transita nel global reduce rispetto a un reduce "puro" su tutti gli elementi.

---

## SLIDE 54 – Esempio: Map+Reduce su Stream (1/2)

**Programma sequenziale con stato:**
```c
state = <valore-iniziale>
for c in {C_1, ..., C_n} {
    mapped = Map(c, f, state);   // mappa f su ogni elemento di c usando state
    state  = Reduce(mapped, ⊕); // aggiorna state con la riduzione di mapped
}
```

dove `Map(c, f, state)` calcola `f(c_i, state)` per i = 1, ..., |c| usando lo stato corrente, e `Reduce(mapped, ⊕)` aggiorna lo stato eseguendo una riduzione su `mapped`.

**Problema:** la computazione e' **stateful**. Per elaborare la collezione C_i si ha bisogno dello stato calcolato al passo i-1. Quindi Map e Reduce **non possono essere messi in pipeline** a causa della dipendenza RAW (Read After Write) sullo stato.

---

## SLIDE 55 – Esempio: Map+Reduce su Stream (2/2)

**Parallelizzazione nonostante lo stato:**

Si parallelizza in un singolo passo: ogni Worker esegue Map e Reduce locale nella stessa iterazione, poi si sincronizza tramite un All-Reduce globale per aggiornare lo stato condiviso.

**Codice di ogni Worker:**
```c
do {
    scatter_receive(partition);
    newstate = state;
    foreach p in partition {
        mapped[p] = f(partition[p], state);
        newstate = newstate ⊕ partition[p];  // riduzione locale
    }
    send(mapped);             // invia la propria parte dell'output
    All-reduce(newstate, ⊕); // sincronizza lo stato tra tutti i Worker
} while(!EOS)
```

**Nota critica:** l'All-Reduce introduce una **barriera implicita**: la prossima iterazione puo' iniziare solo quando la precedente ha terminato (tutti i Worker devono avere il nuovo stato prima di procedere). Questo limita il parallelismo tra iterazioni consecutive a causa della dipendenza sul dato statale.

---

## SLIDE 56 – Letture Consigliate

Riferimenti bibliografici per approfondire la programmazione parallela strutturata:

- **Note del corso di Prof. Danelutto:**
  - `notes2024spm-Danelutto.pdf` — note del corso su structured parallel programming.
  - `Chap10StatePatterns.pdf` — capitolo dedicato ai pattern con stato (stateful patterns).
