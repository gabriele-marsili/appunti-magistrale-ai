# SPM – Lezione 23: Distributed Memory Systems – Background
## Appunti divisi per slide

---

## SLIDE 1 – Titolo

**SPM: Distributed Memory Systems – Background**
Anno accademico 2025-2026 – Prof. Massimo Torquati

---

## SLIDE 2 – Outline

Gli argomenti trattati nella lezione sono:

- Reti di interconnessione e alcune topologie
- Un semplice modello di costo della comunicazione
- Sovrapposizione di comunicazione e computazione
- Comunicazioni sincrone e asincrone

---

## SLIDE 3 – Reti di Interconnessione

Le reti di interconnessione per l'HPC (High Performance Computing) differiscono dalle WAN (Wide Area Network):
- Distanze molto piu' brevi (da O(1) a O(10) metri)
- Infrastruttura controllata
- Requisiti molto piu' stringenti di latenza e banda

**Dimensioni tipiche:** da O(10) a O(100.000) nodi connessi alla stessa infrastruttura di rete.

**Obiettivo:** bassa latenza dei messaggi, alta banda, costo accettabile. Il costo e' generalmente elevato in funzione della scala e delle prestazioni richieste.

**Prestazioni dipendenti da:**
- Hardware (cavi, switch, NIC)
- **Routing:** sceglie il percorso seguito dai pacchetti nella rete.
- **Flow control:** regola quante informazioni possono essere iniettate nella rete, evitando congestioni.

Routing e flow control non vengono studiati in dettaglio nel corso.

---

## SLIDE 4 – Metriche di Prestazione della Rete

**Latenza:** il tempo che intercorre da quando un pacchetto inizia a essere trasmesso dal nodo sorgente a quando viene completamente ricevuto al nodo destinazione. Si esprime in unita' di tempo (s, ms, us, ns).

Tre tipi di latenza:
- **No-load latency (latenza a carico zero):** il tempo misurato in assenza di traffico (nessuna congestione). Rappresenta le prestazioni di base della rete.
- **Under-load latency:** il tempo misurato quando la rete e' utilizzata ma il traffico e' sotto il punto di saturazione.
- **Over-load latency:** la latenza misurata quando la rete e' congestionata (sopra il punto di saturazione).

**Throughput offerto:** la quantita' effettiva di dati inviata nella rete per unita' di tempo. Si esprime in bit/s o multipli (Kb/s, Mb/s, Gb/s).

**Saturation Throughput:** la quantita' massima di traffico sostenuta dalla rete. E' il punto in cui la rete e' pienamente utilizzata.

**Banda (Bandwidth):** il tasso massimo teorico di trasferimento dati in condizioni ideali su un dato percorso di rete. Rappresenta la capacita' massima di un canale di comunicazione. Si esprime in Mb/s, Gb/s.

---

## SLIDE 5 – Metriche di Prestazione: Latenza vs. Throughput

La latenza non e' costante: dipende dalla congestione della rete e dalla distanza tra nodo sorgente e nodo destinazione.

Man mano che il throughput offerto si avvicina al saturation throughput, la latenza cresce bruscamente (comportamento a "gomito").

**Spiegazione del fenomeno:** mentre i nodi continuano a iniettare traffico nella rete, si raggiunge un punto di saturazione in cui la latenza cresce rapidamente a causa della contention (i pacchetti si accodano nei buffer degli switch e aspettano di essere inoltrati). E' lo stesso fenomeno che si osserva nelle code dei sistemi di servizio.

---

## SLIDE 6 – Terminologia Base delle Reti

**Endpoint:** sono le sorgenti e le destinazioni dei messaggi. I nodi di calcolo sono gli endpoint. In un sistema distribuito, ogni nodo e' equipaggiato con una **NIC (Network Interface Card)** che invia e riceve dati dalla rete per conto del processore.

**Switch:** un dispositivo connesso a un insieme di link. Trasmette i pacchetti ricevuti su uno o piu' link usando la logica di routing per gestire piu' flussi simultanei.

**Link:** una connessione fisica (un cavo) usata per trasferire dati tra:
- endpoint e endpoint
- endpoint e switch
- switch e switch

I link moderni sono connessioni seriali ad alta velocita' (fibra ottica, rame, ...).

---

## SLIDE 7 – Reti Dirette e Indirette

**Reti dirette (Direct networks):**
- I nodi svolgono sia il ruolo di endpoint che di switch.
- I nodi instradano il traffico.
- Chiamate anche reti statiche.
- Esempi: ring, nD-mesh, hypercube.

**Reti indirette (Indirect networks):**
- Gli endpoint sono connessi indirettamente attraverso switch dedicati.
- Gli switch dedicati instradano il traffico.
- Chiamate anche reti dinamiche o multistage.
- Esempi: Butterfly, Fat Tree, Dragonfly.

La distinzione fondamentale e': nelle reti dirette i nodi partecipano anche al routing; nelle reti indirette il routing e' delegato interamente agli switch.

---

## SLIDE 8 – Diametro, Grado e Bisection-Width

**Grado (Degree):** il grado di una rete e' il numero massimo di vicini di qualsiasi nodo. Indica quante connessioni dirette ha un nodo.

**Diametro (Diameter):** il diametro di una rete e' la lunghezza del piu' lungo tra tutti i cammini minimi tra qualsiasi coppia di nodi. La lunghezza e' misurata in hop (salti) o archi lungo il cammino minimo. Il diametro ha un impatto diretto sulla latenza nel caso peggiore.

**Bisection-width:** la bisection-width di una rete e' il numero minimo di archi (o link) che devono essere rimossi per dividere la rete in due meta' di dimensione (quasi) uguale. In caso di numero dispari di nodi, una delle due meta' puo' includere un nodo in piu'.
- Indica quanto bene una rete puo' gestire il movimento bulk di dati tra due grandi gruppi di nodi.
- Una bisection-width bassa e' un collo di bottiglia per le comunicazioni collettive.

---

## SLIDE 9 – Mesh 2D

Una **Mesh 2D** M(d,d) ha n = d^2 nodi (endpoint) disposti in una griglia quadrata.

**Proprieta':**
- Grado: deg(M(d,d)) = 4 → O(1). Ogni nodo ha al massimo 4 vicini (su, giu', sinistra, destra). Il grado e' costante, indipendente da n.
- Diametro: dia(M(d,d)) = 2(d-1) → O(sqrt(n)). Il percorso piu' lungo e' quello tra gli angoli opposti della griglia.
- Bisection-width: bw(M(d,d)) = d → O(sqrt(n)). Tagliando lungo una riga o una colonna centrale si ottiene la bisection minima.

**Limiti della Mesh 2D:** diametro e bisection-width crescono come sqrt(n), quindi le comunicazioni tra nodi lontani sono costose su reti grandi.

---

## SLIDE 10 – Torus 2D

Un **Torus 2D** T(c,d) e' una Mesh arricchita da **archi di wraparound** ai bordi della griglia (i nodi ai bordi sono collegati ai nodi sul lato opposto, come in un videogioco). Ha n = c*d nodi/endpoint.

**Proprieta':**
- Grado: deg(T(c,d)) = 4 → O(1). Come la Mesh, costante.
- Diametro: dia(T(c,d)) = d/2 + c/2 → O(sqrt(n)). Dimezzato rispetto alla Mesh grazie agli archi di wraparound.
- Bisection-width: bw(T(c,d)) = min(2c, 2d) → O(sqrt(n)). Migliorata rispetto alla Mesh.

Il Torus migliora il diametro e la bisection-width della Mesh a parita' di grado, grazie ai collegamenti wraparound. Topologie toroidali sono usate in molti supercomputer (es. IBM Blue Gene).

---

## SLIDE 11 – Ipercubo (Hypercube): Definizione

L'**ipercubo** Q_d e' il grafo i cui vertici rappresentano le 2^d stringhe di bit di lunghezza d. Due vertici sono adiacenti se e solo se le stringhe di bit che rappresentano differiscono esattamente in una posizione di bit.

**Esempi visivi:**
- Q_1: 2 nodi (0 e 1), un arco.
- Q_2: 4 nodi (00, 01, 10, 11), un quadrato.
- Q_3: 8 nodi (000, ..., 111), un cubo.
- Q_4: 16 nodi, un ipercubo a 4 dimensioni.

Questa struttura permette di numerare univocamente i nodi con codici di Gray, il che e' utile per il routing.

---

## SLIDE 12 – Ipercubo: Proprieta'

Un **Ipercubo** HC(d) di dimensione d ha n = 2^d nodi.

**Proprieta':**
- Grado: deg(HC(d)) = d → O(log(n)). Ogni nodo ha d vicini (uno per ogni dimensione). Il grado cresce logaritmicamente con n.
- Diametro: dia(HC(d)) = d → O(log(n)). Eccellente: il diametro cresce solo logaritmicamente.
- Bisection-width: bw(HC(d)) = n/2 → O(n). Ottima: bisection-width lineare in n.

**Punto critico:** il grado cresce con log(n), quindi aggiungere nodi richiede di aggiungere connessioni a tutti i nodi esistenti. Non e' una topologia facilmente scalabile a livello fisico/economico.

---

## SLIDE 13 – Criteri per Valutare le Topologie di Rete

**I tre criteri principali:**

1. **Basso diametro:** per supportare comunicazioni efficienti tra qualsiasi coppia di processori, riducendo la latenza nel caso peggiore.

2. **Alta bisection-width:** una bassa bisection-width rallenta molte operazioni di comunicazione collettiva. Tuttavia, raggiungere un'alta bisection-width puo' richiedere un grado non costante.

3. **Grado costante:** indipendente dalla dimensione della rete. Permette alla rete di scalare a un gran numero di nodi senza aggiungere un numero eccessivo di connessioni. Mantiene scalabile il costo fisico.

**Tabella comparativa:**

| Topologia | Grado | Diametro | Bisection-Width |
|---|---|---|---|
| Linear Array | O(1) | O(n) | O(1) |
| 2D Mesh/Torus | O(1) | O(sqrt(n)) | O(sqrt(n)) |
| 3D Mesh/Torus | O(1) | O(n^(1/3)) | O(n^(2/3)) |
| Binary Tree | O(1) | O(log(n)) | O(1) |
| Hypercube | O(log(n)) | O(log(n)) | O(n) |

**Conclusione:** nessuna topologia ottimizza contemporaneamente tutte e tre le metriche. La scelta dipende dai compromessi accettabili per l'applicazione e il budget.

---

## SLIDE 14 – Fat Tree (1/2)

Il **Fat Tree** e' una topologia ad albero indiretta in cui gli endpoint sono le foglie e tutti gli altri nodi sono switch.

**Caratteristica fondamentale:** ogni switch ha lo stesso numero di link verso il basso (verso le foglie) e verso l'alto (verso la radice). Il numero di link **aumenta** (la struttura si "ingrassa") avvicinandosi alla radice.

**Idea chiave:** mantenere la banda costante a ogni livello dell'albero, avendo lo stesso numero di link a ogni livello.

**Problema principale:** il costo! Cresce con la profondita' dell'albero. Gli switch al top-level hanno troppi link. Non e' realistica la versione "pura" descritta (ogni switch al livello superiore richiederebbe un numero enorme di porte).

---

## SLIDE 15 – Fat Tree (2/2)

Il Fat Tree viene implementato in modo diverso rispetto alla versione "pura": usando switch con grado limitato (ogni switch ha al piu' k porte), organizzati in una rete multi-stage (k-ary n-fly network e folded Clos network).

**Esempio: Fat Tree a 2 livelli con k=4 porte per switch:**
- Livello superiore: **aggregation switches** (connettono i pod tra loro)
- Livello inferiore: **edge switches** (connettono gli endpoint)
- Con k=4: 2 aggregation switch + 4 edge switch = 6 switch totali; n = k * k/2 = 8 endpoint massimi.

**Formula generale per Fat Tree a 2 livelli:**
- Numero di switch totali: k + k/2
- Endpoint massimi: n = k * k/2
- Bisection-width: bw(n) = n/2
- Grado: deg(n) = k
- Diametro: dia(n) = 4

**Vantaggio:** soluzione a basso costo, limitata dal numero di porte degli switch. Per scalare la rete si aumenta il numero di livelli.

---

## SLIDE 16 – Dragonfly

Il **Dragonfly** e' una rete indiretta multi-livello in cui i router sono organizzati in gruppi.

**Struttura:**
- Ogni router ha connessioni verso p endpoint, a-1 canali locali (verso altri router dello stesso gruppo) e h canali globali (verso router di altri gruppi).
- Un gruppo consiste di a router. Ogni gruppo ha a*p connessioni verso gli endpoint (topologia fully connected all'interno del gruppo) e a*h connessioni globali.

**Proprieta':**
- Grado: deg(DF(p,a,h)) = p + (a-1) + h

**Obiettivi:** basso diametro costante e alta bisection-bandwidth.

**Sfide:** le prestazioni dipendono criticamente da routing non-triviale e bilanciamento del traffico sui link globali. Se il traffico non e' ben bilanciato tra i link globali, le prestazioni possono degradare rapidamente.

**Esempio:** con h=2, p=2, a=4: 8 nodi per gruppo, 72 nodi totali.

---

## SLIDE 17 – Semantica del Message-Passing (1/2)

Il **Message-Passing** e' un paradigma computazionale in cui processi o agenti indipendenti comunicano esclusivamente inviando e ricevendo messaggi.

**Proprieta' fondamentali:**
- Nessuna memoria fisica o logica condivisa tra le entita' comunicanti.
- Ogni processo ha il proprio stato locale; la condivisione avviene solo tramite messaggi.
- Astrae gli aspetti comunicativi dei sistemi concorrenti e distribuiti, imponendo isolamento che rende piu' semplice la gestione dei guasti e la scalabilita'.

**Modelli teorici e formalismi:**
- **Actor Model:** i processi (actor) incapsulano stato e comportamento, interagendo tramite messaggi asincroni. Ogni actor ha una mailbox e processa i messaggi sequenzialmente.
- **Process Calculi:** CSP (Communicating Sequential Processes) e il pi-calcolo, che forniscono framework formali per descrivere e analizzare le interazioni tra entita' concorrenti.

---

## SLIDE 18 – Semantica del Message-Passing (2/2)

**Aspetti chiave del modello Message-Passing:**

- **Asincronia/sincronia:** tra sender e receiver. Sincrono: send/receive accoppiati (entrambi bloccano). Asincrono: send non bloccante, receive potenzialmente bloccante.

- **Input non-determinismo:** l'ordine di arrivo dei messaggi puo' variare.

- **Ordering/Causality:** non esiste un clock globale o un ordinamento globale degli eventi. I processi osservano gli eventi in un ordine parziale.

- **Scalabilita':** il Message-Passing supporta naturalmente i sistemi distribuiti (microservizi, serverless computing, HPC).

- **Sfide:** deadlock (attesa circolare di messaggi) e livelock (nessun progresso reale).

- **Generalita':** puo' essere usato anche in sistemi a memoria condivisa (es. canali Go). L'implementazione del canale puo' essere una coda concorrente.

---

## SLIDE 19 – Comunicazioni Sincrone vs. Asincrone

**Grado di asincronia di un canale:** e' il numero massimo di messaggi (k >= 0) che il sender puo' inviare prima di dover bloccare in attesa che il receiver inizi a ricevere dati. Dipende dalla capacita' di memoria del canale e dalla dimensione del messaggio.

**Comunicazioni sincrone:**
- Un'operazione di send/receive e' sincrona se si completa solo dopo che il messaggio e' stato ricevuto/inviato.
- **Sender-receiver rendezvous:** il sender o il receiver si blocca finche' il peer completa l'operazione.
- Grado di asincronia = 0: il sender non puo' procedere finche' il receiver non ha letto il messaggio.

**Comunicazioni asincrone:**
- L'operazione di comunicazione ritorna immediatamente senza attendere che il messaggio sia stato effettivamente inviato/ricevuto.
- Il completamento/successo della comunicazione viene verificato successivamente (es. callback, futures/promises).
- Anche la comunicazione asincrona puo' portare al blocco se il buffer del canale e' finito e pieno.

---

## SLIDE 20 – Input Non-Determinismo

Quando un canale di input logico multiplex un insieme di canali indipendenti, il **input non-determinismo** si riferisce alla proprieta' per cui l'operazione di receive puo' restituire un messaggio proveniente da qualsiasi canale nell'insieme.

**Comportamento:**
- Non esiste un ordine fisso quando si riceve un messaggio da un canale multi-input.
- Se piu' di un messaggio e' pronto contemporaneamente, uno viene scelto arbitrariamente (ordine non predicibile).

**Considerazioni progettuali:**
- Fissare un ordine di ricezione e' di solito un approccio non ottimale: riduce la flessibilita' e aggiunge overhead.
- Se e' necessario un ordinamento stretto per la correttezza, si implementa un layer aggiuntivo di protocollo di ordinamento sopra il layer di messaggistica non deterministica.

---

## SLIDE 21 – Modello di Costo della Comunicazione (1/2)

**Modello lineare semplificato** per ragionare sul costo della comunicazione nelle applicazioni parallele:

T_comm = t_0 + n * s

Approssimazione:
- Per n piccolo: T_comm ≈ t_0 (la latenza domina)
- Per n grande: T_comm ≈ n * s (il costo di trasmissione domina)

**Parametri del modello:**
- **t_0:** overhead di startup della comunicazione (setup della rete e del runtime di comunicazione). Anche chiamato "latenza".
- **n:** la quantita' di dati da trasferire (numero di byte).
- **s:** il costo di trasmissione per byte.

---

## SLIDE 22 – Modello di Costo della Comunicazione (2/2)

**Approfondimento sui parametri:**

**t_0 (latenza di startup):**
- Contiene tutti i costi per inviare il messaggio piu' breve (es. payload di 1 byte, n=1).
- Il suo valore puo' variare tra diverse implementazioni di message-passing (a causa di copie di dati, operazioni sincrone vs asincrone, ecc.).

**s (costo per byte):**
- Di solito stimato come s = 1/B, dove B e' la banda disponibile lungo il percorso di trasmissione.
- Puo' includere tutti i costi associati alla dimensione del messaggio (es. copie del messaggio).
- Limitato dalla parte piu' lenta del percorso tra sender e receiver.
- Include sia contributi SW (la velocita' a cui l'applicazione puo' alimentare la rete) che HW (la velocita' a cui i dati si muovono sui cavi e switch della rete).

**Valori tipici su sistemi HPC moderni:**
- t_0: circa 1-10 microsec
- B (banda): 100-200 Gb/s

---

## SLIDE 23 – Limiti del Modello di Comunicazione Lineare

Il modello lineare e' semplice e si applica a molti campi dell'architettura dei computer (es. modellare il tempo di accesso alla memoria, transazioni su bus, operazioni di pipeline).

**Limitazioni del modello:**
- Non include l'effetto della distanza di rete (numero di hop tra sorgente e destinazione).
- Non modella la contention (la latenza dipende dall'utilizzo della rete), causata da alta utilizzazione della rete e buffering limitato negli switch.
- Non modella come il trasferimento di dati viene eseguito (sincrono o asincrono).

**Obiettivo pratico:** non e' quello di stimare T_comm con precisione, ma di **nascondere o ridurre il suo costo** (es. sovrapponendo la comunicazione con la computazione).

---

## SLIDE 24 – Sovrapposizione di Computazione e Comunicazione

Un nodo di calcolo e' equipaggiato con una **NIC (Network Interface Card)** che invia e riceve dati dalla rete per conto del processore. La NIC puo' essere un processore specializzato (**SmartNIC**) con capacita' multiple (DMA, compressione, elaborazione, ecc.).

**Meccanismo di overlap:**
1. Il processo sender esegue una **send non-bloccante** verso il processo destinazione.
2. La NIC esegue il trasferimento dati (in background).
3. La NIC notifica il processo sender al completamento della trasmissione.
4. Mentre la NIC trasferisce i dati, il processore esegue altre operazioni utili (es. un altro task).

Questo permette una **sovrapposizione totale o parziale** tra la computazione dei task e la comunicazione con altri processi. Tale sovrapposizione e' fondamentale per mascherare (o mascherare parzialmente) l'overhead di comunicazione.

---

## SLIDE 25 – Overlap: Diagramma Temporale

**Scenario:** un modulo C riceve in input una lista di task (data stream). Per ogni input:
- T_calc: tempo per la computazione
- T_comm: tempo per inviare il task calcolato al modulo successivo

**Service time di C (T_s^C):** l'intervallo di tempo tra l'inizio dell'elaborazione di due task consecutivi.

**Due casi:**
- **Senza overlap:** T_s^C = T_calc + T_comm (sequenziale: prima calcola, poi comunica).
- **Con overlap completo:** T_s^C = max(T_calc, T_comm) (computazione e comunicazione avvengono in parallelo).

**Relazione generale:**
max(T_calc, T_comm) <= T_s^C <= T_calc + T_comm

Il caso senza overlap corrisponde a un collo di bottiglia: il service time e' la somma dei due contributi. Con overlap completo, il service time e' determinato dal termine dominante (il piu' grande tra T_calc e T_comm). Nella realta' si ottiene un overlap parziale, tra i due estremi.

---

## SLIDE 26 – RDMA e Overlap della Latenza

Le SmartNIC possono includere il supporto **RDMA (Remote Direct Memory Access)**: abilita il trasferimento di dati da memoria a memoria tra due nodi senza il coinvolgimento continuo del sistema operativo.

**Tecnologie:**
- **InfiniBand:** fornisce supporto a livello hardware per RDMA con fabric di switch dedicati. Standard de facto nell'HPC ad alte prestazioni.
- **ROCE (RDMA over Converged Ethernet):** implementa RDMA sopra Ethernet, consentendo gli stessi vantaggi di bassa latenza in ambienti datacenter senza richiedere infrastruttura InfiniBand.

**Caratteristiche di RDMA:**
- La CPU offload il trasferimento dati alla NIC e continua l'elaborazione.
- **Zero-copy:** i dati vengono trasferiti direttamente tra i buffer applicativi dei due nodi senza essere copiati in buffer intermedi del kernel.
- **Kernel-bypass:** il trasferimento avviene senza passare attraverso il sistema operativo (riduzione drastica della latenza).
- Comune nelle reti ad alte prestazioni (es. InfiniBand).
- Le API RDMA (es. libibverbs) sono generalmente piu' complesse delle API standard (es. socket).
- Alcune librerie di Message-Passing (es. MPI) sfruttano RDMA internamente per il trasferimento dati punto-a-punto veloce.

---

## SLIDE 27 – Pattern di Comunicazione

Diversi pattern di comunicazione hanno semantiche e implementazioni diverse, utili per diversi scenari:

**One-to-One:** un sender invia a un receiver. Il pattern piu' semplice.

**One-to-Many (broadcast / scatter):** un sender invia a molti receiver. Usato nelle operazioni collettive di broadcast e scatter.

**Many-to-One (gather / reduce):** molti sender inviano a un receiver. Usato nelle operazioni collettive di gather e reduction.

**Many-to-Many (all-to-all):** ogni sender invia a ogni receiver. Il pattern piu' oneroso per la rete.

Il costo della comunicazione dipende anche dal pattern utilizzato, poiche' ciascuno stessa la rete in modo diverso. Ad esempio, l'all-to-all genera un traffico molto piu' pesante sull'infrastruttura di rete rispetto all'one-to-one.

---

## SLIDE 28 – Metodo PCAM di Foster per la Progettazione di Algoritmi Paralleli

Il **metodo PCAM (Partitioning, Communication, Agglomeration, Mapping)**, proposto da Ian Foster, e' un framework concettuale per ragionare sulla parallelizzazione di un problema dato.

**Le quattro fasi:**

1. **Partitioning (Partizionamento):** decomporre il problema in un gran numero di task piccoli (a grana fine) che possono essere eseguiti in parallelo. L'obiettivo e' massimizzare il parallelismo potenziale.

2. **Communication (Comunicazione):** determinare le comunicazioni richieste tra i task (le dipendenze sui dati). Quali task devono scambiarsi informazioni e quando?

3. **Agglomeration (Agglomerazione):** combinare i task identificati in task piu' grandi (a grana grossa) per ridurre la comunicazione migliorando la localita' dei dati. Bilancia overhead e parallelismo. Troppa grana fine = troppo overhead; troppa grana grossa = poco parallelismo.

4. **Mapping (Mappatura):** assegnare i task aggregati ai processi secondo la topologia della rete, per minimizzare la comunicazione, abilitare la concorrenza e bilanciare il workload.

---

## SLIDE 29 – Esempio: Iterazione di Jacobi (Introduzione)

L'**iterazione di Jacobi** e' uno stencil code applicato a un array 2D, usato per risolvere PDE (Partial Differential Equations) a 2D.

**Regola di aggiornamento:** ogni valore nella matrice viene sostituito con la media dei suoi quattro vicini (nord, sud, est, ovest). La regola viene applicata iterativamente fino alla convergenza.

**Condizioni al contorno:** i valori di bordo (boundary, parte gialla nella slide) rimangono costanti a ogni iterazione (fixed boundary conditions).

**Evitare sovrascritture:** alla fine di ogni iterazione, si scambia l'array aggiornato con quello originale per evitare sovrascritture durante l'iterazione successiva (si usano due array alternati: double buffering).

**Matrice iniziale:** bordo superiore = -1, righe successive con valori 3, 2, 1, 0, bordo inferiore = -1.

---

## SLIDE 30 – Esempio: Iterazione di Jacobi (Codice)

```cpp
copy(buff, data, rows, cols);
for (int k = 1; k < MaxIter; k++) {
    for (int i = 1; i < rows-1; i++)
        for (int j = 1; j < cols-1; j++)
            buff[i*cols+j] = 0.25f * (
                data[(i+1)*cols+j] + data[i*cols+j-1] +
                data[i*cols+j+1] + data[(i-1)*cols+j]
            );
    residual = R(buff, data);   // es. norma L2 delle differenze
    if (residual < THRESHOLD) break;
    swap(data, buff, rows, cols);
}
```

**Valori di bordo fissi:** data[0][*], data[n-1][*], data[*][0], data[*][n-1].

**Convergenza:** si controlla il residuo (es. norma L2 della differenza tra l'array corrente e quello precedente). L'iterazione si ferma quando il residuo scende sotto una soglia THRESHOLD.

**Esempio di evoluzione:** dopo 1 iterazione, i valori interni cambiano verso la media dei loro vicini. Dopo 25 e 75 iterazioni la soluzione converge progressivamente verso la soluzione della PDE.

---

## SLIDE 31 – Esempio: Jacobi – Evoluzione dopo 25 e 75 Iterazioni

Le slide mostrano l'evoluzione della matrice dopo 25 e 75 iterazioni. Si osserva come i valori interni convergano progressivamente verso una distribuzione che dipende dalle condizioni al contorno.

Dopo 75 iterazioni la soluzione e' piu' uniforme rispetto a dopo 25 iterazioni: i gradienti interni si smorzano, e la soluzione si avvicina alla soluzione stazionaria della PDE.

Questo conferma che l'iterazione di Jacobi converge verso la soluzione dell'equazione di Poisson (o Laplace) con le condizioni al contorno imposte.

---

## SLIDE 32 – Due Schemi Paralleli per Jacobi: Analisi PCAM

**Applicando il metodo PCAM all'iterazione di Jacobi:**

**Partitioning:** il task piu' piccolo e' il calcolo di un singolo elemento della matrice.

**Communication:** all'interno di un'iterazione, tutti i task a grana fine possono essere calcolati indipendentemente, ma ogni task ha bisogno dei dati dei 4 vicini. Alla fine di ogni iterazione, c'e' una barriera di sincronizzazione tra tutti i p processori e uno scambio di dati.

**Agglomeration:** due opzioni:
- **Metodo 1 (1D partitioning):** partizionamento per righe (o colonne). Ogni processore riceve un blocco contiguo di n/p righe.
- **Metodo 2 (2D partitioning):** partizionamento su una griglia quadrata. Ogni processore riceve un blocco quadrato di dimensione (n/sqrt(p)) x (n/sqrt(p)), con i p processori organizzati in una griglia sqrt(p) x sqrt(p).

**Mapping:** segue la politica usata per l'agglomerazione: gruppi contigui di righe per il metodo 1; rettangoli di griglia quadrata per il metodo 2.

---

## SLIDE 33 – Due Schemi Paralleli per Jacobi: Analisi dei Costi

**Parametri:** griglia di dimensione n x n, p processi su p nodi. Modello lineare di comunicazione: T_comm(n) = t_0 + n * s.

**Metodo 1 (partizionamento 1D per righe):**
- Ogni processo possiede circa n/p righe.
- Deve comunicare le righe di confine ai processori vicini (sopra e sotto): 2 comunicazioni di n elementi ciascuna.
- T_comm(n) ≈ 2 * (t_0 + n * s)

**Metodo 2 (partizionamento 2D a griglia quadrata, p = sqrt(p) x sqrt(p)):**
- Ogni processo possiede un blocco di dimensione (n/sqrt(p)) x (n/sqrt(p)).
- Deve comunicare i 4 bordi del blocco ai 4 processori vicini: 4 comunicazioni di n/sqrt(p) elementi ciascuna.
- T_comm(n) ≈ 4 * (t_0 + (n/sqrt(p)) * s)

**Confronto:**
- Per n grande e p sufficientemente grande: il Metodo 2 e' preferibile perche' ogni processo comunica meno dati complessivamente (n/sqrt(p) per bordo invece di n per bordo), anche se con piu' messaggi (4 invece di 2).
- Il termine dominante di comunicazione del Metodo 2 cala come n/sqrt(p) vs. n del Metodo 1.
- Questo dimostra il vantaggio del partizionamento 2D nella riduzione del volume di comunicazione per sistemi con p grande.

---

## SLIDE 34 – Letture Consigliate

- Capitolo 2, Sezioni 2.2 e 2.4 del libro "Parallel Programming Concept and Practice"
- "Designing and Building Parallel Programs" di Ian Foster (disponibile online): https://www.mcs.anl.gov/~itf/dbpp/

Per approfondire il mondo delle reti di interconnessione e del routing:
- "Principles and Practices of Interconnection Networks" di W. Dally e B. Towles, Morgan Kaufmann, 2004
- "Interconnection Networks – An Engineering Approach" di J. Duato et al., Morgan Kaufmann, 2022
