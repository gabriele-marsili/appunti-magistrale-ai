# SPM – Lezione 14: Workload Balancing
## Appunti divisi per slide

---

## SLIDE 1 – Titolo

**SPM: Workload Balancing**
Anno accademico 2025-2026 – Prof. Massimo Torquati

---

## SLIDE 2 – Outline

Gli argomenti trattati nella lezione sono tre:

- Data partitioning (partizionamento dei dati)
- Politiche di distribuzione statica dei dati: block, cyclic, block-cyclic
- Workload irregolari e assegnazione dinamica dei task

---

## SLIDE 3 – Data Partitioning

Il **Data Parallelism** è un modello di programmazione in cui la stessa operazione (funzione) viene applicata in parallelo su partizioni indipendenti di un insieme di dati.

Il parallelismo viene sfruttato tramite un insieme di **Worker**, ognuno dei quali calcola gli elementi della propria partizione.

Le partizioni possono essere elaborate in due modi:
- **Indipendentemente** da ciascun Worker (paradigma map)
- Con **interazioni** tra Worker, ovvero scambio di messaggi o sincronizzazioni (paradigma stencil)

Il **data partitioning** è la strategia con cui i dati in input vengono divisi tra i thread o i processi disponibili. Influenza direttamente l'efficienza e le prestazioni del calcolo.

La principale sfida è il **workload imbalance**: se il carico di lavoro non è distribuito uniformemente, alcuni thread/processi termineranno prima e rimarranno in attesa idle degli altri.

Per questo motivo, le tecniche di **workload balancing** sono fondamentali per garantire:
- distribuzione uniforme del carico
- uso ottimale delle risorse
- miglioramento delle prestazioni complessive

---

## SLIDE 4 – Esempio: Insieme di Mandelbrot (1/2)

L'**insieme di Mandelbrot** è l'insieme di tutti i numeri complessi c per cui la sequenza definita dall'iterazione z_n(c) rimane limitata al tendere di n all'infinito.

La regola iterativa è: z_0 = 0, z_{n+1} = z_n^2 + c

In pratica, si verifica se |z_n(c)| <= 2 per un numero elevato di iterazioni (es. 1000). Se la condizione è soddisfatta, si assume che c appartenga all'insieme.

Per ottenere la figura frattale, il **colore di ogni pixel** dipende dal numero di iterazioni necessario prima che |z_n(c)| superi 2.

Il calcolo del colore di ogni pixel è **indipendente** dagli altri (calcolo embarassingly data parallel).

Attenzione al carico computazionale:
- I pixel **neri** (appartenenti all'insieme) richiedono il numero massimo di iterazioni
- I pixel **colorati** fuori dall'insieme escono prima
- I punti vicini al bordo dell'insieme possono anch'essi richiedere molte iterazioni

Il **carico computazionale per pixel è fortemente asimmetrico** (skewed).

---

## SLIDE 5 – Esempio: Insieme di Mandelbrot (2/2)

Se calcolassimo il Mandelbrot set usando 3 thread partizionando i pixel in strisce orizzontali consecutive, otterremmo un risultato sbilanciato:

- Thread 0 riceve la parte superiore dell'immagine (pochi pixel neri, lavoro leggero)
- Thread 1 riceve la parte centrale (la maggior parte dei pixel neri, lavoro pesante)
- Thread 2 riceve la parte inferiore (lavoro leggero)

Il **Thread 1 esegue la maggior parte del lavoro**. Il carico dei thread è sbilanciato, con conseguente bassa efficienza complessiva.

Questo esempio mostra come una partizione statica naive di dati con costo non uniforme per elemento possa causare workload imbalance.

---

## SLIDE 6 – Politiche di Distribuzione dei Dati (1/2)

La domanda chiave è: come aggregare i dati in task e assegnarli ai Worker in modo da garantire un calcolo bilanciato?

L'assegnazione dei task può essere **statica** o **dinamica**.

**Assegnazione statica:**
- La collezione di dati in input viene partizionata una volta sola all'inizio, prima che il calcolo inizi
- Ogni Worker riceve una partizione fissa e la elabora indipendentemente
- L'output è partizionato di conseguenza (le partizioni di output possono essere raccolte o ridotte)
- Tipicamente ogni partizione ha dimensione simile (o meglio ancora, costo computazionale simile)

**Assegnazione dinamica:**
- I dati vengono suddivisi in piccole partizioni (chunk)
- I chunk vengono assegnati ai Worker su richiesta tramite uno scheduler dedicato, oppure i Worker li prelevano da una coda centrale (work sharing) o rubano lavoro da altri Worker (work stealing)
- Chunk piccoli producono un migliore bilanciamento del carico, ma introducono maggiore overhead di scheduling e minore località

---

## SLIDE 7 – Politiche di Distribuzione dei Dati (2/2)

**Politiche statiche:**
- L'obiettivo è trovare una partizione dei dati che distribuisca uniformemente il workload
- Ideali per workload regolari
- Nessun overhead di scheduling dinamico
- Politiche standard: block, cyclic, block-cyclic
- Esempi di applicazione: prodotto matrice-vettore denso, stencil regolari, convoluzione

**Politiche dinamiche:**
- Adattano l'assegnazione dei task ai Worker per gestire workload irregolari
- Migliorano l'efficienza in presenza di carichi computazionali asimmetrici
- Introducono overhead aggiuntivo per lo scheduling (messaggi/sincronizzazioni extra)
- Politiche standard: on-demand, work-sharing, work-stealing
- Esempi di applicazione: Mandelbrot set, algoritmi su grafi, simulazioni N-Body, prodotto matrice-vettore sparso

---

## SLIDE 8 – Esempio: Prodotto Matrice-Vettore

Nel prodotto matrice-vettore b = A * x:
- La granularità minima di un task è il calcolo di un singolo elemento b_i. Per calcolarlo servono la riga i-esima di A (A_{i*}) e il vettore x completo.
- Ogni b_i (ogni task) può essere calcolato indipendentemente dagli altri (dot-product)

Nei casi reali, m e n sono numeri molto grandi (>> numero di core della macchina). Per massimizzare l'utilizzo del singolo processore, ogni processore calcola una partizione di k task.

Questo è un **workload regolare**, quindi la partizione statica è generalmente sufficiente.

---

## SLIDE 9 – Politiche di Distribuzione Statica (1/3) – Block

Esempio: p=5 Worker, m=16 elementi (b_0 ... b_15)

**Distribuzione Block:**
- I task vengono divisi in blocchi contigui di dimensione ceil(m/p)
- La dimensione del blocco è almeno m/p
- Se (m mod p) = k != 0, allora i primi k Worker ricevono un blocco di dimensione ceil(m/p), gli altri di dimensione floor(m/p)

Con p=5 e m=16: ceil(16/5) = 4. I Worker 0,1,2 ricevono 4 elementi, i Worker 3,4 ne ricevono 3.

La versione con ceil (SDIV-based) garantisce la copertura completa ma può lasciare alcuni thread idle se m non è divisibile per p. Una implementazione più bilanciata distribuisce il resto esplicitamente sui primi thread.

La distribuzione block **massimizza la località** dei dati: ogni Worker accede a elementi contigui in memoria.

---

## SLIDE 10 – Politiche di Distribuzione Statica (2/3) – Cyclic

Esempio: p=5 Worker, m=16 elementi

**Distribuzione Cyclic:**
- I task vengono assegnati ai Worker in modo circolare (round-robin)
- Il task t_i viene assegnato al Worker p_{i mod p}

Con p=5 e m=16:
- Worker 0: b_0, b_5, b_10, b_15
- Worker 1: b_1, b_6, b_11
- Worker 2: b_2, b_7, b_12
- Worker 3: b_3, b_8, b_13
- Worker 4: b_4, b_9, b_14

La distribuzione cyclic **distribuisce meglio il carico** in presenza di variazioni regolari del costo, ma ha **minore località** rispetto alla distribuzione block (gli elementi assegnati allo stesso Worker non sono contigui in memoria).

---

## SLIDE 11 – Politiche di Distribuzione Statica (3/3) – Block-Cyclic

Esempio: p=5 Worker, m=16 elementi

**Distribuzione Block-Cyclic:**
- Dato un blocco di dimensione c > 0 (p * c è chiamato stride), il task t_i viene assegnato al processore p_{(i div c) mod p}
- La distribuzione cyclic è un caso speciale con c=1

Con p=5, m=16, c=2:
- Worker 0: b_0, b_1, b_10, b_11
- Worker 1: b_2, b_3, b_12, b_13
- Worker 2: b_4, b_5, b_14, b_15
- Worker 3: b_6, b_7
- Worker 4: b_8, b_9

La distribuzione block-cyclic è un **compromesso** tra block (buona località) e cyclic (buon bilanciamento): ogni Worker riceve più blocchi contigui distribuiti ciclicamente. Il parametro c controlla il trade-off tra località e bilanciamento.

---

## SLIDE 12 – Test delle Politiche Statiche

Risultati su prodotto matrice-vettore con m=2^18, n=2^15 (tempo sequenziale ~9.54s) sul nodo front-end del cluster spmcluster. 10 ripetizioni per punto, rimossi min e max, calcolata la media.

**Osservazioni principali:**
- La distribuzione block-cyclic usa c=8 come dimensione del chunk
- Con 20 thread: Speedup = 8.22, Efficienza = 8.22/20 ≅ 41%

**Perché l'efficienza è bassa?**
- L'intensità aritmetica dell'algoritmo è: I = (2 * m * n) / (8 * (m*n + n + m)) ≅ 0.25 FLOPS/byte
- L'algoritmo è **memory-bound** (limitato dalla banda di memoria, non dalla potenza di calcolo)

**Conclusione importante:** in questo kernel regolare e memory-bound, **una migliore località conta più di un bilanciamento più fine**. La distribuzione block, pur essendo meno bilanciata della cyclic, ottiene speedup simili o migliori perché accede alla memoria in modo più efficiente (elementi contigui).

---

## SLIDE 13 – Strutture Dati Irregolari

Alcune strutture dati sono intrinsecamente irregolari. Esempio: una **Triangulated Irregular Network (TIN)** è una raccolta di triangoli non sovrapposti con dimensioni, forme e densità molto variabili.

- Le regioni con terreno ripido richiedono molti triangoli piccoli
- Le regioni piatte richiedono pochi triangoli grandi

Una partizione statica diretta può portare a gravi squilibri del workload tra i Worker.

Possibili soluzioni:
- Algoritmi di partizionamento basati su grafi o geometria (domain-specific) per distribuire il workload più uniformemente
- Tuttavia, anche con buone politiche statiche, il **workload attivo può cambiare nel tempo** (es. simulazioni adattive)

In molti di questi casi, le **politiche di distribuzione dinamica** sono necessarie per adattarsi ai workload variabili.

---

## SLIDE 14 – Workload Sbilanciati

Nella distribuzione statica dei dati, l'assegnazione è predeterminata all'inizio del programma:
- Nessun overhead a runtime per l'assegnazione dei task ai thread
- Funziona bene se il costo computazionale per elemento non varia troppo e se si conosce in anticipo il numero di task

Il calcolo del Mandelbrot set è un esempio di workload sbilanciato. Una possibile soluzione statica è usare chunk molto piccoli con block-cyclic. Tuttavia:
- Con task fortemente asimmetrici, anche pochi task aggiuntivi per thread possono produrre imbalance
- Nel caso peggiore, tutti i task "pesanti" possono essere assegnati allo stesso thread
- Le assegnazioni statiche non possono essere usate quando il numero di task non è noto staticamente

**Per workload sbilanciati, è meglio usare strategie di assegnazione dinamica.**

---

## SLIDE 15 – Array con Costo Non Uniforme per Elemento

Quando un array ha elementi con costo computazionale molto variabile (alcuni elementi richiedono molto più lavoro degli altri – "compute-intensive array entry"), la distribuzione statica produce inevitabilmente squilibri.

**Work-sharing e work-stealing** possono riassegnare i chunk quando i Worker diventano idle, migliorando il bilanciamento del carico. La chiave è che i Worker che finiscono prima non rimangono in attesa, ma prelevano nuovi task dal pool condiviso o rubano task dagli altri.

---

## SLIDE 16 – Work-Sharing e Work-Stealing

**Work-Sharing:**
- Tutti i Worker thread condividono una singola coda concorrente di task (MPMC – Multiple Producer Multiple Consumer)
- La coda può essere implementata con lock o lock-free (spesso bounded)
- Il threadPool è una possibile implementazione del pattern Work-Sharing
- Semplice ed efficace con pochi produttori e task di dimensioni medie/grandi
- Può soffrire di contention sulla coda quando molti thread accedono contemporaneamente

**Work-Stealing:**
- Ogni Worker thread mantiene una coda locale di task
- I task possono essere assegnati ai Worker con politica round-robin o random, oppure partono su un Worker
- I Worker idle (con coda locale vuota) rubano casualmente (un batch di) task dalla coda di altri Worker
- I Worker eseguono push/pop dalla coda in fondo (tail), i "ladri" rubano dalla testa (head)
- Migliore **località** e minore **contention** rispetto al work-sharing
- Ideale per molti task piccoli e irregolari; meno contention e costo di furto occasionale

---

## SLIDE 17 – Esempio: Matrice delle Distanze All-Pairs (1/3)

**Definizione del problema:**
- Abbiamo una matrice D di dimensione m x n, dove i indica uno degli m vettori (es. i pixel di un'immagine) e j enumera gli n elementi del vettore
- Vogliamo calcolare la distanza (o similarità) d(·,·) tra tutte le coppie di vettori in D
- Delta_{ij} = d(x_i, x_{i'}) per tutti gli i, i' in {0, ..., m-1}
- La funzione d(·,·) può essere la distanza euclidea o qualsiasi funzione binaria simmetrica

**Complessità computazionale:**
- Dobbiamo calcolare m^2 valori di distanza/similarità
- Assumendo che il calcolo di un singolo valore richieda O(n), il totale è O(m^2 * n)

**Sfruttare la simmetria:**
- La matrice Delta è simmetrica: Delta_{ij} = d(x_i, x_{i'}) = d(x_{i'}, x_i)
- Quindi basta calcolare la parte triangolare inferiore di Delta e copiare i valori nella parte superiore corrispondente
- Questo riduce il numero di calcoli di circa la metà

---

## SLIDE 18 – Esempio: Matrice delle Distanze All-Pairs (2/3)

**Dataset MNIST:**
- Consiste di 70.000 cifre scritte a mano, memorizzate come immagini in scala di grigi 28x28
- 60.000 immagini per il training, 10.000 per il test
- Ogni immagine viene trattata come un vettore: m=70.000, n=784

**Considerazioni sulla memoria:**
- Memorizzare la matrice delle distanze 70.000 x 70.000 in singola precisione richiede circa **19.6 GB** – la memoria è già un problema critico

**Formula della distanza euclidea:**
- d(x_i, x_{i'}) = ||x_i - x_{i'}||_2 = sqrt( sum_{j=0}^{n-1} (D_{ij} - D_{i'j})^2 )

**Struttura del calcolo per riga:**
- Per la riga i della matrice Delta, dobbiamo calcolare i+1 elementi (dalla simmetria)
- Il costo computazionale della riga i è quindi proporzionale a (i+1) * n
- Le righe più in basso nella matrice hanno un costo computazionale crescente

---

## SLIDE 19 – Esempio: Matrice delle Distanze All-Pairs (3/3)

**Parallelizzazione naiva con block-cyclic:**
- Una parallelizzazione naive usa la distribuzione block-cyclic statica delle righe di Delta sui thread, con un certo valore di chunk c

**Problema dello sbilanciamento:**
- Considerando una matrice 12x12 e c=2:
  - Thread 0 riceve 2 task
  - Thread 1 riceve 6 task
  - Thread 2 riceve 10 task (il triplo del Thread 0!)
- Con c=1 migliora, ma il workload rimane sbilanciato
- La riga i richiede (i+1) distanze con costo O((i+1)*n), quindi le righe finali sono molto più costose

**Conclusione:** serve una strategia diversa che assegni dinamicamente le righe da calcolare ai thread.

---

## SLIDE 20 – Matrice All-Pairs: Assegnazione Statica vs Dinamica

**Assegnazione statica (block-cyclic):**
- Le righe vengono assegnate staticamente usando offset e stride
- La partizione è fissa e predeterminata prima dell'inizio del calcolo

**Assegnazione dinamica:**
- Il prossimo chunk viene acquisito a runtime da un contatore condiviso (atomico)
- Quando un Worker finisce il suo chunk corrente, preleva il successivo disponibile

**Punto chiave:** cambia solo la politica di assegnazione, il kernel di calcolo (la funzione che calcola le distanze) rimane identico in entrambi i casi.

---

## SLIDE 21 – Risultati: Matrice All-Pairs

Risultati ottenuti eseguendo l'implementazione all_pair.cpp per il dataset MNIST sul nodo front-end del cluster, con 40 thread.

**Distribuzione block-cyclic statica:**
| Chunk size (c) | 1 | 8 | 64 |
|---|---|---|---|
| Speedup(40) | 34.9 | 34.4 | 30.3 |

**Distribuzione dinamica:**
| Chunk size (c) | 1 | 8 | 64 |
|---|---|---|---|
| Speedup(40) | 37.3 | 36.5 | 31.8 |

**Osservazioni:**
- La distribuzione block-cyclic statica riduce lo squilibrio ma non può eliminarlo del tutto, perché il costo delle righe cresce con l'indice di riga
- L'assegnazione dinamica migliora il bilanciamento, al costo di un overhead di sincronizzazione
- Con chunk piccoli (c=1), la differenza tra statico e dinamico è più marcata
- Con chunk grandi (c=64), entrambi peggiorano perché la granularità grossolana reintroduce imbalance

---

## SLIDE 22 – Risultati: Calcolo del Mandelbrot Set

Risultati su macchina a 64 core (2x AMD EPYC 7551, 2-way SMT – 128 logical core @ 2GHz), usando 128 thread. Tempo sequenziale: 146.9 secondi. Codice compilato con -O3 –march=native.

**Speedup con distribuzione block-cyclic statica:**
| Chunk size (c) | 1 | 4 | 8 | 16 |
|---|---|---|---|---|
| Block-Cyclic | 1.96 | 2.38 | 3.6 | 6.94 |

**Speedup con distribuzione dinamica:**
| Chunk size (c) | 1 | 4 | 8 | 16 |
|---|---|---|---|---|
| Dynamic | 1.93 | 2.32 | 3.55 | 6.91 |
| ThreadPool | 2.09 | 2.85 | 4.1 | 7.23 |

**Osservazioni:**
- Per questo workload irregolare, lo scheduling dinamico migliora il bilanciamento
- La soluzione basata su threadPool (work-sharing) introduce un overhead moderato rispetto alla distribuzione dinamica diretta
- All'aumentare di c, lo speedup cresce perché diminuisce l'overhead di scheduling; ma con c troppo grande il bilanciamento peggiora
- Il Mandelbrot set è un caso fortemente irregolare dove le politiche statiche sono insufficienti

---

## SLIDE 23 – Scegliere la Dimensione della Partizione/Task

La scelta della dimensione del task (o della dimensione della partizione nelle distribuzioni statiche) è **critica** per ottenere buone prestazioni parallele.

La dimensione giusta bilancia la distribuzione del carico di lavoro contro l'overhead introdotto dallo scheduling e dalla sincronizzazione.

**Task troppo piccoli:**
- Alto overhead per frequenti sincronizzazioni e scheduling
- Molte comunicazioni e accessi alla struttura di coordinamento

**Task troppo grandi:**
- Basso overhead di scheduling
- Rischio di scarso bilanciamento del carico, con thread in attesa idle

**Dimensione ottimale:**
- E' un trade-off tra minimizzare l'overhead e massimizzare il bilanciamento del workload
- La curva del tempo totale di esecuzione ha un minimo in corrispondenza della dimensione ottimale del task
- Dipende dall'hardware (latenza di sincronizzazione, cache) e dalla natura del workload

---

## SLIDE 24 – Come Scegliere la Strategia di Distribuzione del Workload

Tabella riassuntiva per guidare la scelta della strategia:

| Caratteristiche del workload | Strategia preferita | Motivo |
|---|---|---|
| Costo regolare per task, numero di task noto | Static block | Massima località, minimo overhead di scheduling |
| Lieve irregolarità, costo variabile ma moderato | Cyclic o block-cyclic | Migliore bilanciamento rispetto al block puro, overhead ancora basso |
| Forte irregolarità, costo dipendente dai dati o numero di task sconosciuto | Dynamic assignment | Si adatta a runtime, evita Worker idle |
| Task irregolari molto fine-grain, grande numero di task piccoli | Work-stealing | Migliore scalabilità rispetto al work-sharing, meno contention, migliore località |

**Regole pratiche:**
- Sintonizzare sempre la dimensione del chunk: troppo piccolo aumenta l'overhead, troppo grande aumenta lo squilibrio
- Usare lo scheduling dinamico solo quando lo squilibrio del workload domina il tempo di esecuzione (l'overhead del dynamic scheduling puo' essere non trascurabile)

---

## SLIDE 25 – Letture Consigliate

- Capitolo 4 del libro "Parallel Programming Concept and Practice"
- Lettura aggiuntiva: "Scalable Load Distribution and Load Balancing for Dynamic Parallel Programs" di E. Berger e J.C. Browne
  - Disponibile su: https://people.cs.umass.edu/~emery/pubs/wcbc-99-beb.pdf
