# SPM – Lezione 15: Models of Computation
## Appunti divisi per slide

---

## SLIDE 1 – Titolo

**SPM: Models of Computation**
Anno accademico 2025-2026 – Prof. Massimo Torquati

---

## SLIDE 2 – Outline

L'obiettivo della lezione è capire i limiti del parallelismo e il costo della comunicazione. I tre modelli trattati sono:

- **Work-Span model**: limiti del parallelismo, concetti di work e critical path
- **PRAM model**: progettazione di algoritmi paralleli su memoria condivisa idealizzata
- **BSP model**: modello concreto che mostra il costo delle comunicazioni e delle sincronizzazioni

---

## SLIDE 3 – Perché modelli astratti ad alto livello?

I modelli astratti sono utili per diversi motivi:

- Aiutano a capire cosa è possibile fare prima di preoccuparsi di come farlo
- Separano la progettazione dell'algoritmo dai dettagli della macchina reale
- Permettono di ragionare sulla scalabilità e sui limiti fondamentali
- Permettono di concentrarsi sull'algoritmo prima di mapparlo su sistemi reali
- Forniscono **lower bound** sulle prestazioni ottenibili

Un lower bound stabilisce un limite alle migliori prestazioni che qualsiasi algoritmo può raggiungere per un dato problema. Sapere qual è il limite teorico ci permette di valutare quanto un'implementazione reale si avvicini all'ottimo.

---

## SLIDE 4 – Work-Span Model

Il **Work-Span model** (detto anche Work-Depth model) fornisce limiti più precisi rispetto alle leggi di Amdahl e Gustafson.

Un programma parallelo viene rappresentato come un **DAG (Directed Acyclic Graph)**:
- I **nodi** sono task (unita' di lavoro, ovvero codice sequenziale arbitrario)
- Gli **archi** rappresentano le dipendenze di dati tra i task
- Un task è pronto per l'esecuzione (ready) solo se tutti i suoi predecessori nel grafo sono stati completati

**Assunzioni del modello:**
- p processori identici, ciascuno esegue un task pronto alla volta
- **Greedy scheduling**: ogni volta che c'e' un task pronto e un processore disponibile, il task viene eseguito immediatamente
- Il parallelismo è determinato dalla struttura del DAG

---

## SLIDE 5 – Work-Span Model: Terminologia

**T_1 (Work):** il lavoro totale, ovvero la somma dei costi di tutti i task nel DAG. Misura la computazione totale.

**T_inf (Span / Critical Path):** lo span, detto anche percorso critico. E' la catena più lunga di dipendenze con task di costo unitario; formalmente, il percorso dalla radice a una foglia con il costo associato più alto.
- T_1 misura la computazione totale
- T_inf misura la computazione sequenziale inerente (cioe' la parte che non puo' essere parallelizzata)

**Esempio nel DAG della slide:**
- T_1 = 54 (somma di tutti i costi dei nodi)
- T_inf = 27 (costo del percorso critico piu' lungo)

Il rapporto T_1 / T_inf rappresenta il **parallelismo disponibile** nel DAG: nell'esempio vale 54/27 = 2, ovvero al massimo si puo' ottenere uno speedup di 2 indipendentemente dal numero di processori.

---

## SLIDE 6 – Work-Span Model: Lower Bounds

Il tempo di esecuzione T_p (con p processori, sotto greedy scheduling) e' soggetto a due lower bound:

**Work bound (limite del lavoro):**
- T_p >= T_1 / p
- Caso ideale: bilanciamento perfetto del carico e zero overhead. Il migliore tempo possibile e' T_1/p.

**Span bound (limite dello span):**
- T_p >= T_inf
- Il tempo di esecuzione non puo' essere inferiore al percorso critico, indipendentemente dal numero di processori.

Il tempo di esecuzione parallelo e' quindi limitato sia dal lavoro totale sia dal percorso critico. Nessuno dei due puo' essere ignorato nella progettazione di un algoritmo parallelo.

---

## SLIDE 7 – Work-Span Model: Limiti allo Speedup

Dallo stesso framework derivano due limiti superiori allo speedup S(p) = T_1 / T_p:

**Limite dal work bound:**
- S(p) = T_1 / T_p <= T_1 / (T_1/p) = p
- Lo speedup superlineare non e' possibile nel modello.

**Limite dallo span:**
- S(p) = T_1 / T_p <= T_1 / T_inf
- Lo speedup massimo e' limitato dal parallelismo disponibile T_1 / T_inf.

**Esempio (DAG della slide):**
- T_1 = 54, T_inf = 27 → S(p) <= 2
- Anche con infiniti processori, lo speedup massimo ottenibile e' 2.

---

## SLIDE 8 – Teorema di Brent (1974)

**Contesto:** si assume un calcolatore parallelo con processori in grado di eseguire un task in tempo unitario con greedy scheduling. Si assume che il calcolatore abbia abbastanza processori per sfruttare il massimo grado di concorrenza.

**Struttura del DAG:** ad ogni livello i del DAG ci sono m_i task, con la somma totale uguale a T_1.

Con m_i processori al livello i, tutti i task del livello si completano in O(1). Un calcolatore con meno processori p puo' eseguire l'algoritmo entro il seguente limite superiore:

**Teorema di Brent:**
T_p <= (T_1 - T_inf) / p + T_inf

Interpretazione: il tempo parallelo e' limitato dal lavoro distribuito (T_1 - T_inf) / p piu' il percorso critico T_inf.

Il teorema di Brent fornisce un **upper bound** su T_p, mentre i lower bound della slide precedente forniscono lower bound. Insieme delimitano l'intervallo in cui si trova T_p.

---

## SLIDE 9 – Dimostrazione del Teorema di Brent

**Schema della dimostrazione:**

Il DAG ha n livelli; il livello i contiene m_i task unitari. Poiche' ad ogni livello c'e' almeno un task, n = T_inf.

Per ogni livello i, il tempo impiegato da p processori e':
T(i) = ceil(m_i / p) <= (m_i + p - 1) / p

Sommando su tutti gli n livelli:

T_p = sum_{i=1}^{n} T(i) <= sum_{i=1}^{n} (m_i + p - 1) / p
    = T_1/p + (p-1)/p * T_inf
    = (T_1 - T_inf) / p + T_inf

La disuguaglianza utilizza la proprieta' che ceil(x/y) <= (x + y - 1) / y.

---

## SLIDE 10 – Implicazioni del Teorema di Brent

Dallo speedup derivato dal teorema si ricava:

S(p) <= min(p, T_1 / T_inf)

Lo speedup e' limitato sia dal numero di processori sia dal parallelismo disponibile.

**Condizione per buono speedup:**
- T_inf deve essere significativamente piu' piccolo di T_1, cioe' T_inf << T_1
- In quel caso: T_1 - T_inf ≈ T_1, e dal teorema di Brent:
  T_p ≈ T_1/p + T_inf    (quando T_inf << T_1)

**Implicazione per la progettazione degli algoritmi:**
- Occorre puntare a **ridurre lo span T_inf**, poiche' e' il limite asintotico fondamentale alla scalabilita'.
- Si puo' anche aumentare il lavoro T_1, ma solo se questo consente una drastica riduzione dello span.

**Riepilogo dei bound:**
T_1/p <= T_p <= (T_1 - T_inf)/p + T_inf

---

## SLIDE 11 – Implicazioni del Teorema di Brent (cont.)

Partendo dal lower bound di Brent si puo' derivare un lower bound sullo speedup:

S(p) = T_1 / T_p >= T_1 / (T_1/p + T_inf) = p / (1 + p * T_inf / T_1)

S(p) ≈ p   se T_1 / T_inf >> p

Questo dice che lo scheduling greedy raggiunge speedup (quasi) lineare se il problema e' **sovra-decomposto**: se si crea molto piu' parallelismo potenziale rispetto al numero di processori, l'efficienza si avvicina a 1.

**Parallel slack:** il rapporto T_1 / T_inf viene chiamato parallel slack (slack parallelo) e rappresenta l'eccesso di parallelismo disponibile rispetto a quello strettamente necessario. In pratica, si e' osservato che uno slack di almeno 8-10 e' spesso sufficiente per ottenere buone prestazioni.

---

## SLIDE 12 – Limiti del Work-Span Model

I bound del Work-Span model si basano su assunzioni idealizzate che nella pratica non sono soddisfatte:

- **Nessun overhead parallelo**: l'esecuzione parallela esegue esattamente T_1 operazioni totali, senza costi aggiuntivi.
- **Banda di memoria non collo di bottiglia**: si assume una macchina astratta di tipo PRAM in cui l'accesso alla memoria non limita le prestazioni.
- **Greedy scheduling ideale**: i task pronti vengono eseguiti immediatamente, senza ritardi dovuti a lock o sincronizzazioni.

Questi sono **limiti di scalabilita' sotto assunzioni ideali**. Aiutano a ragionare sui limiti teorici, ma non predicono il tempo di esecuzione esatto di un'implementazione reale. In particolare, ignorano la gerarchia di memoria, la banda, il costo delle sincronizzazioni e le limitazioni hardware.

---

## SLIDE 13 – Parallel Random Access Machine (PRAM)

Il modello **PRAM** (Parallel Random Access Machine) e' un modello idealizzato a memoria condivisa per la progettazione di algoritmi paralleli.

**Struttura della macchina ideale:**
- n processori P_0, ..., P_{n-1} connessi a una memoria condivisa globale M
- Nessuna cache, nessuna gerarchia NUMA
- Nessun overhead di sincronizzazione
- Ogni locazione di memoria e' uniformemente accessibile da qualsiasi processore in tempo costante O(1)
- La comunicazione tra processori avviene tramite letture e scritture sulla memoria condivisa globale
- Modello di esecuzione sincrono (lockstep): tutti i processori eseguono le istruzioni in modo sincronizzato

Il modello PRAM semplifica enormemente la progettazione di algoritmi paralleli eliminando tutti i dettagli legati all'hardware reale (latenze, cache, coerenza).

---

## SLIDE 14 – PRAM: Ciclo di Istruzione

n processori identici P_i (i = 0, ..., n-1) operano in lockstep. Ad ogni step, ciascun processore esegue un ciclo di istruzione in tre fasi:

**1. Fase di Read:**
Ogni processore puo' leggere simultaneamente un singolo dato da una cella di memoria condivisa (distinta) e memorizzarlo in un registro locale.

**2. Fase di Compute:**
Ogni processore puo' eseguire un'operazione fondamentale sui suoi dati locali e memorizzare il risultato in un registro.

**3. Fase di Write:**
Ogni processore puo' scrivere simultaneamente un dato su una cella di memoria condivisa.
- Nella variante PRAM a scrittura esclusiva (exclusive write), e' consentita la scrittura solo su celle distinte.
- Nella variante a scrittura concorrente (concurrent write), e' consentita la scrittura sulla stessa cella da piu' processori (possibili race condition).

**Analisi della complessita':** ogni step su PRAM richiede tempo O(1).

---

## SLIDE 15 – Varianti PRAM (1/2): EREW e CREW

Le varianti del modello PRAM differiscono nel modo in cui gestiscono gli accessi concorrenti alla memoria:

**EREW (Exclusive Read Exclusive Write):**
- Nessun processore puo' leggere o scrivere sulla stessa cella di memoria condivisa contemporaneamente a un altro.
- Variante piu' restrittiva: nessun accesso concorrente ne' in lettura ne' in scrittura.

**CREW (Concurrent Read Exclusive Write):**
- Piu' processori possono leggere contemporaneamente dalla stessa cella di memoria.
- La scrittura rimane esclusiva: processori diversi non possono scrivere sulla stessa cella nello stesso ciclo.
- Variante intermedia: lettura concorrente consentita, scrittura concorrente vietata.

---

## SLIDE 16 – Varianti PRAM (2/2): CRCW

**CRCW (Concurrent Read Concurrent Write):**
- Sia la lettura che la scrittura concorrente sulla stessa cella sono consentite.
- In caso di scrittura simultanea, occorre specificare quale valore viene effettivamente memorizzato. Le sotto-varianti sono:

  - **Priority CW:** ogni processore ha una priorita' distinta; vince in scrittura quello con priorita' piu' alta.
  - **Arbitrary CW:** un processore scelto casualmente tra quelli in scrittura vince.
  - **Common CW:** se tutti i valori da scrivere sono uguali, viene scritto quel valore; altrimenti la cella rimane invariata.
  - **Combining CW:** tutti i valori vengono combinati in un unico valore tramite un'operazione binaria associativa (es. somma, prodotto, minimo, OR/AND logico).

La variante piu' potente e' CRCW, ma anche quella piu' difficile da realizzare su hardware reale. EREW e' la piu' vicina alla realta'.

---

## SLIDE 17 – Misure di Complessita' nel Modello PRAM

Il modello PRAM ignora i costi reali dell'hardware per semplificare la progettazione di algoritmi paralleli.

**Le due misure di complessita' per gli algoritmi PRAM:**

- **Complessita' temporale T(n):** numero di step sincroni necessari per completare l'algoritmo.
- **Complessita' in processori P(n):** numero di processori utilizzati per eseguire l'algoritmo.

**Costo dell'algoritmo:**
C(n) = T(n) * P(n)

Un algoritmo PRAM e' **cost-optimal** se il suo costo corrisponde asintoticamente alla complessita' sequenziale ottima. In altri termini, C(n) deve essere O(complessita' del miglior algoritmo sequenziale). Un algoritmo puo' essere veloce (basso T(n)) ma non cost-optimal se usa troppi processori.

---

## SLIDE 18 – Prefix Computation (Scan)

**Definizione:** dato un operatore binario associativo ◦ su un insieme X (es. addizione, moltiplicazione, minimo, massimo, concatenazione di stringhe, AND/OR booleano), e dato un array X = {x_0, ..., x_{n-1}}, si vuole calcolare:

- s_0 = x_0
- s_1 = x_0 ◦ x_1
- ...
- s_{n-1} = x_0 ◦ x_1 ◦ ... ◦ x_{n-1}

In altre parole: s_0 = x_0 e s_i = s_{i-1} ◦ x_i per i = 1, ..., n-1.

Il calcolo di S = {s_0, ..., s_{n-1}} a partire da X = {x_0, ..., x_{n-1}} e' detto **prefix computation** (o scan).

**Lower bound:** Omega(n), cioe' e' necessario leggere almeno tutti gli n input.

L'algoritmo che implementa la prefix computation e' spesso chiamato **scan**.

---

## SLIDE 19 – Esempio di Prefix Computation

**Esempio con operatore min:**

- Input:  {39, 21, 20, 50, 13, 18, 2, 33, 49, 39, 47, 15, 30, 47, 24, 1}
- Output: {39, 21, 20, 20, 13, 13,  2,  2,  2,  2,  2,  2,  2,  2,  2, 1}

Ogni elemento dell'output e' il minimo tra tutti gli elementi dell'input dalla posizione 0 fino alla posizione corrente inclusa.

**Lower bound:** Omega(n) - e' necessario visitare tutti gli n elementi.

---

## SLIDE 20 – Scan Inclusivo ed Esclusivo

Esistono due versioni dell'algoritmo scan:

**Inclusive scan (prefisso inclusivo):**
L'elemento di output in posizione i include anche l'elemento di input in posizione i. Il primo elemento di output corrisponde al primo elemento di input.

**Exclusive scan (prefisso esclusivo):**
L'elemento di output in posizione i include solo gli elementi di input fino alla posizione i-1 (escluso l'elemento i). Il primo elemento di output e' l'elemento neutro dell'operazione.

La libreria standard C++ fornisce entrambe le versioni: std::inclusive_scan e std::exclusive_scan.

La prefix computation si riferisce tipicamente alla versione inclusiva.

---

## SLIDE 21 – Parallel Prefix su PRAM (algoritmo non cost-optimal)

**Obiettivo:** progettare un algoritmo PRAM cost-optimal per il prefix sum, cioe' con C(n) = O(n).

**Algoritmo di recursive doubling con p = n processori:**

```
for (j = 0; j < n; j++) do_in_parallel     // ogni processore j
    reg_j = A[j];                           // copia un valore nel registro locale

for (i = 0; i < ceil(log(n)); i++) do       // ciclo esterno sequenziale
    for (j = pow(2,i); j < n; j++) do_in_parallel   // ogni processore j
        reg_j += A[j - pow(2, i)];          // esegue il calcolo
        A[j] = reg_j;                       // scrive il risultato in memoria condivisa
```

**Analisi:**
- Numero di step: O(log n), poiche' il ciclo esterno esegue ceil(log(n)) iterazioni
- Processori usati: p = n
- Costo: C(n) = T(n) * P(n) = O(log n) * n = O(n log n)

Ogni elemento della sequenza finale rappresenta la somma di tutti gli elementi precedenti nella sequenza originale.

**Questo algoritmo e' veloce ma NON cost-optimal con p = n processori**, poiche' il costo e' O(n log n) anziche' O(n).

---

## SLIDE 22 – Parallel Prefix su PRAM (algoritmo cost-optimal)

Per ridurre il costo C(n) si riduce il numero di processori P(n), usando p = n / log(n) processori.

**Algoritmo in 3 fasi:**

1. Si partizionano gli n valori di input in chunk di dimensione log(n). Ogni processore calcola in parallelo i prefix sum locali del proprio chunk. Tempo: O(log(n)).

2. Si esegue l'algoritmo di prefix sum non cost-optimal (il precedente) sui risultati parziali di ciascun chunk (n/log(n) valori). Tempo: O(log(n / log(n))).

3. Ogni processore somma il valore calcolato al passo 2 dal suo vicino sinistro a tutti i valori del proprio chunk. Tempo: O(log(n)).

**Analisi:**
- Tempo asintotico: O(log n) (uguale a prima)
- Processori: p = n / log(n)
- Costo: C(n) = O(log n) * O(n / log n) = O(n) → cost-optimal

Non si e' battuto il tempo asintotico O(log n), ma si e' ridotto abbastanza il numero di processori da riportare il costo totale a O(n).

---

## SLIDE 23 – Parallel Prefix: Esempio Visivo

**Esempio con n=16, p=4 (chunk di dimensione 4):**

Fase 1 (prefix sum locale per ogni processore):
- P0: {0, 1, 2, 3} → {0, 1, 3, 6}
- P1: {4, 5, 6, 7} → {4, 9, 15, 22}
- P2: {8, 9, 10, 11} → {8, 17, 27, 38}
- P3: {12, 13, 14, 15} → {12, 25, 39, 54}

Fase 2 (prefix sum sui valori finali di ciascun chunk: 6, 22, 38, 54):
- Risultati accumulati: P0 → 6, P1 → 28, P2 → 66, P3 → 120

Fase 3 (ogni processore aggiunge il valore accumulato del vicino sinistro):
- P0: rimane {0, 1, 3, 6}
- P1: aggiunge 6 → {10, 15, 21, 28}
- P2: aggiunge 28 → {36, 45, 55, 66}
- P3: aggiunge 66 → {78, 91, 105, 120}

Costo: C(n) = O(log n) * O(n/log n) = O(n) → cost-optimal.

---

## SLIDE 24 – Compattazione di Array Sparsi (Sparse Array Compaction)

**Problema:** si ha un array monodimensionale A in cui la maggior parte degli elementi e' zero.

**Obiettivo:** compattare tutti gli elementi non-zero preservando il loro ordine.

**Risultato:** si rappresenta l'array in modo piu' efficiente memorizzando solo:
- V: i valori degli elementi non-zero
- C: le coordinate (indici) corrispondenti degli elementi non-zero

Questa operazione e' fondamentale in molti contesti: prodotto matrice-vettore sparso, compressione dati, rappresentazione di grafi sparsi.

---

## SLIDE 25 – Sparse Array Compaction su PRAM

**Algoritmo con p = n/log(n) processori basato su parallel prefix:**

1. Si genera un array temporaneo tmp: tmp[i] = 1 se A[i] != 0, altrimenti tmp[i] = 0.
2. Si esegue un parallel prefix summation (cost-optimal) su tmp. Dopo questa operazione, per ogni elemento non-zero di A, il valore in tmp[i] contiene l'indirizzo di destinazione di quell'elemento in V.
3. Si scrivono gli elementi non-zero di A in V usando gli indirizzi generati dal prefix sum. Le coordinate corrispondenti vengono scritte in C in modo analogo.

**Costo:**
C(n) = T(n) * P(n) = O(log n) * O(n / log n) = O(n)

L'algoritmo e' cost-optimal e sfrutta il parallel prefix come primitive fondamentale. Questo mostra come operazioni composte complesse possano essere costruite componendo primitive parallele efficienti.

---

## SLIDE 26 – Limiti del Modello PRAM

Pur essendo utile per la progettazione, il modello PRAM ha assunzioni non realistiche:

**Accesso alla memoria non realistico:**
Si assume che tutti i processori abbiano accesso uniforme e istantaneo a un'unica memoria condivisa. Nella realta' esistono gerarchie di cache, NUMA, latenze di accesso.

**Sincronizzazione lockstep perfetta:**
Mantenere una sincronizzazione globale ad ogni passo introduce overhead significativo sui sistemi reali.

**Nessun costo di comunicazione e gerarchia di memoria:**
Algoritmi PRAM cost-optimal possono scalare male su macchine reali dove la gerarchia di memoria, i ritardi di comunicazione, gli overhead di sincronizzazione e le risorse limitate giocano un ruolo cruciale.

**Conclusione:** il modello PRAM offre un framework pulito per progettare algoritmi paralleli, ma le sue assunzioni semplificatrici lo rendono poco rappresentativo dei sistemi reali, dove la gerarchia di memoria, i ritardi di comunicazione, gli overhead di sincronizzazione e le risorse limitate giocano un ruolo cruciale.

---

## SLIDE 27 – Bulk Synchronous Parallel (BSP) Model

Il modello **BSP (Bulk-Synchronous Parallel)** fu proposto da Leslie G. Valiant come framework unificato per la progettazione, l'analisi e la programmazione di sistemi paralleli general-purpose.

**Caratteristiche principali:**
- Garantisce sia prestazioni scalabili sia indipendenza dall'architettura
- Non e' solo un modello teorico: puo' servire anche come paradigma di riferimento per la programmazione parallela

**Componenti del modello BSP:**
1. Un insieme di componenti processore-memoria (ogni processore ha la propria memoria locale)
2. Una rete di comunicazione in grado di consegnare messaggi punto a punto tra processori
3. Un meccanismo per la sincronizzazione globale di tutti i processori (barriera)

Riferimento: L. G. Valiant, "A bridging model for parallel computation", Communications of the ACM, Vol. 33, Issue 8, pp. 103-111, August 1990.

---

## SLIDE 28 – BSP Computer

**Architettura di una macchina BSP:**
- n processori P_0, ..., P_{n-1}, ciascuno con la propria memoria locale (multiprocessore a memoria distribuita)
- Il tempo di accesso alla memoria remota e' uniforme: l'accesso a qualsiasi locazione di memoria non locale richiede lo stesso tempo
- La comunicazione tra processori avviene tramite messaggi espliciti (message-passing model)

La rete di comunicazione e' trattata come una **black box**: si conosce il costo del trasferimento di dati, ma non i dettagli interni della rete. Questo rende il modello indipendente dall'architettura sottostante (interconnessione, topologia, ecc.).

---

## SLIDE 29 – BSP Algorithm: Struttura a Superstep

Un algoritmo BSP consiste in una sequenza di **superstep**.

**Struttura di un superstep:**
- Fasi di computazione, comunicazione, o entrambe
- Seguite da una **sincronizzazione globale a barriera** (bulk synchronization) che garantisce che tutta la computazione e comunicazione del superstep siano completate prima di procedere

**Tipologie di superstep:**
- **Computation superstep:** si concentra su elaborazione locale (es. operazioni in virgola mobile)
- **Communication superstep:** si concentra sullo scambio di dati tra processi (es. trasferimento di parole dati)
- **Mixed superstep:** include sia elaborazione locale che scambio di dati nello stesso superstep

La struttura a superstep impone una disciplina alla comunicazione e alla sincronizzazione, rendendo l'algoritmo piu' facile da analizzare e ottimizzare.

---

## SLIDE 30 – h-relation e Costo della Comunicazione

**h-relation:** un communication superstep in cui ogni processore invia e riceve al piu' h parole dati. La h e' il massimo tra le parole inviate e ricevute da un processore nel superstep.

**Costo di una h-relation:**
T(h) = h * g + l

dove:
- **g (gap):** costo per parola comunicata (latenza per unita' di dato). Dipende dal numero di processori p.
- **l (latency):** tempo di sincronizzazione globale. Include i costi della sincronizzazione globale, tutti i costi fissi per assicurarsi che i dati siano arrivati a destinazione, e l'avvio delle comunicazioni. Dipende da p.
- Entrambi sono espressi in FLOPS (il tempo e' moltiplicato per il FLOP rate del processore).

**Full h-relation:** una h-relation in cui ogni processore invia e riceve esattamente h parole dati.

I valori approssimativi di g e l su un dato calcolatore parallelo si ottengono misurando i tempi di esecuzione per una serie di full h-relation, variando h e p.

---

## SLIDE 31 – Costo del Computation Superstep

**Costo di un computation superstep:**
T_comp(w) = w + l

dove:
- **w:** quantita' di lavoro, definita come il numero massimo di operazioni eseguite nel superstep da qualsiasi processore. I processori con meno di w operazioni devono attendere.
- **l:** costo di sincronizzazione (identico a quello della comunicazione).

**Costo di un mixed superstep (computazione + comunicazione):**
T_comp(w) = w + h * g + l

La stessa misura l viene usata per tutti i tipi di superstep. Questo riflette il fatto che ogni superstep termina con una barriera globale, indipendentemente dal tipo di operazioni eseguite.

---

## SLIDE 32 – Costo di un Algoritmo BSP

Il costo totale di un algoritmo BSP si esprime come:

C_BSP = a + b * g + c * l

dove a, b, c sono i coefficienti ottenuti sommando i contributi di computazione, comunicazione e sincronizzazione di tutti i superstep dell'algoritmo.

**Esempio (p=4, g=4 FLOPS, l=20 FLOPS):**
- Superstep di computazione 1: P_1 esegue 60 FLOPS (il massimo)
- Superstep di comunicazione 1: P_1 invia/riceve 10 parole a/da tutti gli altri processori (h = 3*10 = 30 nel totale; ogni processore invia/riceve al piu' 10 parole)
- Superstep di computazione 2: P_0 esegue 80 FLOPS (il massimo)
- Superstep di comunicazione 2: P_0 riceve 10 parole da tutti gli altri processori

Calcolo del costo totale:
C_BSP = (60 + l) + (3*10*g + l) + (80 + l) + (3*10*g + l)
      = 140 + 60*g + 4*l
      = 140 + 60*4 + 4*20
      = 140 + 240 + 80
      = 460 FLOPS

---

## SLIDE 33 – Esempio BSP: Prodotto Scalare (Dot Product) (1/2)

**Problema:** calcolare il prodotto scalare alpha = a^T * b = sum_{i=0}^{n-1} a_i * b_i tra due vettori a e b di lunghezza n.

**Distribuzione dei dati (cyclic):** con p processori, a_i e b_i vengono assegnati al processore p_{i mod p}.

**Esempio: n=10, p=3**
- P_0 riceve gli elementi con indice 0, 3, 6, 9
- P_1 riceve gli elementi con indice 1, 4, 7
- P_2 riceve gli elementi con indice 2, 5, 8

**Struttura in 3 superstep:**
1. **Computation superstep:** ogni processore calcola il dot product parziale locale dei propri elementi.
2. **Communication superstep:** ogni processore invia il proprio risultato parziale a tutti gli altri.
3. **Computation superstep:** ogni processore somma tutti i risultati parziali ricevuti per ottenere alpha.

Al termine, tutti i p processori conoscono il valore finale alpha.

---

## SLIDE 34 – Esempio BSP: Prodotto Scalare (Dot Product) (2/2)

**Analisi del costo:**

- Superstep di computazione 1: ogni processore esegue 2*(n/p) FLOPS → costo: 2*(n/p) + l
- Superstep di comunicazione: ogni processore invia il proprio parziale a p-1 processori → h = p-1 → costo: (p-1)*g + l
- Superstep di computazione 2: ogni processore somma p risultati parziali → costo: p + l

**Costo totale:**
C_dot_product = 2*(n/p) + p + (p-1)*g + 3*l

**Osservazione:** il costo del dot product su BSP dipende dal numero di processori p, dal ratio n/p, dal costo di comunicazione g e dalla latenza di sincronizzazione l. All'aumentare di p, il termine di computazione 2*(n/p) diminuisce, ma il termine di comunicazione (p-1)*g aumenta. Esiste quindi un valore ottimale di p che minimizza il costo.

---

## SLIDE 35 – Esempio BSP: GEMM (Matrix-Matrix Multiplication)

**Assunzione:** le matrici A, B, C sono di dimensione N x N e abbastanza grandi da essere distribuite uniformemente su p processori. Inizialmente, ogni processore contiene N^2/p valori di A e B (un sotto-blocco di dimensione N/sqrt(p) x N/sqrt(p)). Alla fine, ogni processore conterra' N^2/p valori di C. Si assume N mod p = 0.

**Algoritmo BSP in 2 superstep:**

1. **Communication superstep:** scambio di dati tra tutti i processori per trasferire i sotto-blocchi. Il totale di parole comunicate per processore e' circa N^2/p * p = N^2. Costo: h*g + l, con h = N^2/p.

2. **Computation superstep:** ogni processore calcola localmente i valori di C. Il costo e' circa (2*N)/N^2/p = 2*N^3/p FLOPS.

**Costo totale BSP:**
C_BSP(N, p) = 2*N^3/p + g*(N^2/p) + 2*l

**Speedup:**
S(p) = T(1) / T(p) = 2*N^3 / (2*N^3/p + g*N^2/p + 2*l)

**Efficienza asintotica:**
lim_{N -> inf} E(p) = 1

Al crescere di N, il termine di computazione domina e l'efficienza si avvicina a 1.

---

## SLIDE 36 – Riepilogo del Modello BSP

**Parametri della macchina BSP:**
Una macchina BSP astratta e' descritta da BSP(p, r, g, l) dove:
- **p:** numero di processori
- **r:** velocita' di calcolo in FLOPS
- **g:** costo di comunicazione per parola di dato (in unita' di tempo FLOP)
- **l:** costo di sincronizzazione globale (in unita' di tempo FLOP)

La rete di comunicazione e' una black box che fornisce accesso uniforme alla memoria remota.

**Struttura dei programmi BSP:**
I programmi su BSP sono espressi come una serie consecutiva di superstep. Alla fine di ogni superstep c'e' una barriera di sincronizzazione globale tra tutti i processori.

**Il modello BSP promuove:**
- Un approccio strutturato alla parallelizzazione (limita la liberta' del programmatore imponendo un modello specifico)
- Il modello di computazione **SPMD (Single Program, Multiple Data)**: un solo programma deve essere scritto; tutti i processori eseguono lo stesso programma ma su dati diversi
- Il bilanciamento della comunicazione tra i processori (concentrare tutti i dati su un unico processore e' scoraggiato, poiche' aumenta il valore di h e quindi il costo)

---

## SLIDE 37 – Letture Consigliate

- Capitolo 2, Sezione 2.1 del libro "Parallel Programming Concepts and Practice"
- "Parallel Scientific Computation: A Structured Approach Using BSP" di R. H. Bisseling, Oxford University Press, 2020 (seconda edizione)
  - Ulteriori informazioni: https://webspace.science.uu.nl/~bisse101/Book2/psc2.html
- "Structured Parallel Programming – Patterns for Efficient Computation" di M. McCool, A. D. Robison, J. Reinder, Morgan Kaufmann
  - Il Capitolo 2 di questo libro e' fornito come materiale aggiuntivo
