# SPM – Lezione 25: MPI Part II
## Appunti divisi per slide

---

## SLIDE 1 – Titolo

**SPM: Message Passing Interface (MPI) – Part II**
Anno accademico 2025-2026 – Prof. Massimo Torquati

---

## SLIDE 2 – Outline

Gli argomenti trattati in questa seconda parte su MPI sono:

- **Comunicazioni collettive**: operazioni che coinvolgono tutti i processi in un comunicatore (Barrier, Bcast, Reduce, Scatter, Gather, Allgather, Allreduce, Alltoall, Scan, Exscan).
- **Esempi di utilizzo**: somma di vettori, regressione, FFT distribuita, Power Iteration.

---

## SLIDE 3 – Comunicazioni Collettive in MPI

Le **comunicazioni collettive** sono operazioni che coinvolgono simultaneamente tutti i processi di un comunicatore (o un sottoinsieme definito da un communicator). A differenza delle comunicazioni punto-a-punto (MPI_Send/Recv tra due processi), le collettive implementano pattern multi-processo come:

- **one-to-all**: un processo invia dati a tutti gli altri (Broadcast, Scatter).
- **all-to-one**: tutti i processi inviano dati a un singolo processo (Gather, Reduce).
- **all-to-all**: ogni processo comunica con tutti gli altri (Allgather, Allreduce, Alltoall).

**Vantaggi rispetto alle comunicazioni punto-a-punto:**
Le operazioni collettive sono spesso piu' efficienti rispetto a un'implementazione manuale con comunicazioni punto-a-punto, perche' le librerie MPI possono sfruttare algoritmi ottimizzati (ad esempio, implementazioni a butterfly, a doppio albero, pipeline) che tengono conto della topologia della rete.

**Regola fondamentale:** tutti i processi nel comunicatore devono chiamare la stessa operazione collettiva. Non e' possibile che un sottoinsieme di processi chiami una collettiva mentre gli altri eseguono altra logica (a meno di usare comunicatori diversi).

**Nota:** dal punto di vista funzionale, le collettive non sono strettamente necessarie: tutto cio' che fanno puo' essere replicato con comunicazioni punto-a-punto. La loro esistenza serve a semplificare il codice e a migliorare le prestazioni.

---

## SLIDE 4 – Barrier

```c
int MPI_Barrier(MPI_Comm comm)
```

**MPI_Barrier** e' una primitiva di sincronizzazione globale: nessun processo puo' uscire dalla barriera finche' tutti i processi nel comunicatore non l'hanno raggiunta. E' l'equivalente MPI della barriera OpenMP, ma in questo caso coinvolge i processi MPI piuttosto che i thread.

**Versione non bloccante:**
```c
int MPI_Ibarrier(MPI_Comm comm, MPI_Request* req)
```
Come tutte le collettive, esiste una variante non bloccante (prefisso `I`). Il processo chiama `MPI_Ibarrier` e puo' continuare a fare lavoro utile; il completamento della sincronizzazione va verificato con `MPI_Wait` o `MPI_Test` sul request restituito.

**Possibili implementazioni della barriera:**

- **Implementazione centralizzata (master/slave):**
  Il processo master (P0) riceve un messaggio da tutti gli altri (fase di arrivo), poi invia un messaggio a tutti (fase di partenza). Semplice ma crea un collo di bottiglia sul processo 0.
  ```
  // Processo master P0:
  for(i=1; i < p; ++i) recv(P_ANY);
  for(i=1; i < p; ++i) send(P_i);
  // Processi slave P1..P_{p-1}:
  send(P0);
  recv(P0);
  ```
- **Implementazione basata su albero (tree-based):** usa una struttura ad albero binario per ridurre il numero di passi di comunicazione da O(p) a O(log p).
- **Implementazione a butterfly:** piu' sofisticata, ottimale in termini di latenza su reti con topologia adatta (ipercubo).

---

## SLIDE 5 – Broadcast (schema visivo)

```c
int MPI_Bcast(void* buf, int count, MPI_Datatype dt, int root, MPI_Comm comm)
```

**MPI_Bcast** invia lo stesso messaggio dal processo `root` a tutti gli altri processi nel comunicatore (pattern one-to-all). Al termine dell'operazione, il buffer `buf` contiene gli stessi dati su tutti i processi.

**Schema:**
- Il processo root ha il dato A0.
- Dopo il broadcast, tutti i processi (rank 0, 1, 2, ...) hanno A0 nel proprio buffer.

Visivamente:
```
rank 0 (root): A0 --->  A0
rank 1:         [?] --->  A0
rank 2:         [?] --->  A0
...
```

---

## SLIDE 6 – Broadcast (utilizzo API)

```c
int MPI_Bcast(void* buf, int count, MPI_Datatype dt, int root, MPI_Comm comm)
```

**Aspetto importante:** tutti i processi del comunicatore devono chiamare `MPI_Bcast`, inclusi quelli che non sono il root (e che sono quindi ricevitori). E' la chiamata stessa a distinguere chi e' mittente e chi e' ricevitore in base al parametro `root`.

- `buf`: sul processo root e' il buffer da inviare; sugli altri processi e' il buffer dove verra' scritto il dato ricevuto.
- `root`: il rank del processo che origina i dati. Puo' essere qualsiasi rank nel comunicatore, non necessariamente il rank 0 (anche se per convenzione si usa spesso rank 0).

**Schema API:**
```
Processo 0 (root):  buf = A0  --> chiama MPI_Bcast()
Processo 1:         buf = ??? --> chiama MPI_Bcast() --> buf = A0
...
Processo p-1:       buf = ??? --> chiama MPI_Bcast() --> buf = A0
```

---

## SLIDE 7 – Reduce

```c
int MPI_Reduce(const void* sndbuf, void* rcvbuf, int count,
               MPI_Datatype dt, MPI_Op op, int root, MPI_Comm comm)
```

**MPI_Reduce** raccoglie i valori da tutti i processi, applica un operatore di riduzione (op) e deposita il risultato nel processo `root` (pattern all-to-one). Il risultato e' quindi disponibile solo sul processo root dopo l'operazione.

**Parametri:**
- `sndbuf`: buffer di invio (presente su tutti i processi, incluso root).
- `rcvbuf`: buffer di ricezione (significativo solo sul processo root).
- `op`: operatore di riduzione (MPI_SUM, MPI_MAX, MPI_MIN, MPI_PROD, ecc.).
- `root`: il processo che riceve il risultato finale.

**Esempio concettuale:**
```
rank 0: A0 \
rank 1: A1  |
rank 2: A2  |--> reduce --> A = op(A0, A1, A2, A3, A4, A5) su rank root
rank 3: A3  |
rank 4: A4  |
rank 5: A5 /
```

---

## SLIDE 8 – Operatori Predefiniti MPI_Op

MPI fornisce un insieme di operatori di riduzione predefiniti da usare con MPI_Reduce e altre collettive:

| Operatore       | Descrizione                         |
|-----------------|-------------------------------------|
| MPI_SUM         | Somma                               |
| MPI_PROD        | Prodotto                            |
| MPI_MAX         | Massimo                             |
| MPI_MIN         | Minimo                              |
| MPI_LAND        | AND logico                          |
| MPI_LOR         | OR logico                           |
| MPI_LXOR        | XOR logico                          |
| MPI_BAND        | AND bit a bit                       |
| MPI_BOR         | OR bit a bit                        |
| MPI_BXOR        | XOR bit a bit                       |
| MPI_MAXLOC      | Massimo e posizione (indice)        |
| MPI_MINLOC      | Minimo e posizione (indice)         |

**MPI_MINLOC / MPI_MAXLOC:** questi operatori speciali restituiscono non solo il valore minimo/massimo, ma anche la posizione (indice) di quel valore. Per usarli, il tipo di dato deve essere una coppia (valore, indice). MPI fornisce datatypes predefiniti per le coppie, tra cui: `MPI_FLOAT_INT`, `MPI_DOUBLE_INT`, `MPI_INT_INT`, ecc.

E' anche possibile definire operatori di riduzione personalizzati con `MPI_Op_create`.

---

## SLIDE 9 – MPI_MAXLOC / MPI_MINLOC

Gli operatori `MPI_MAXLOC` e `MPI_MINLOC` operano su coppie (valore, indice) e restituiscono la coppia con il valore massimo o minimo insieme all'indice associato.

**Esempio:**

Valori distribuiti sui processi:
```
valori:  19  21  15  28  19  28
indici:   0   1   2   3   4   5
```

- `MAXLOC(valore, indice)` = `(28, 3)` — il valore massimo e' 28, al rank/posizione 3.
- `MINLOC(valore, indice)` = `(15, 2)` — il valore minimo e' 15, al rank/posizione 2.

**Regola di tie-breaking:** se piu' processi hanno lo stesso valore min/max, MPI_MINLOC e MPI_MAXLOC restituiscono l'indice piu' piccolo tra quelli pareggiati.

**Esempi di codice:** `mpi_maxloc.cpp` e `mpi_maxminloc.cpp`

---

## SLIDE 10 – Esempio MPI_Reduce: Integrazione Numerica

Questa slide mostra un esempio concreto di utilizzo di `MPI_Reduce` per il calcolo di un integrale numerico con la **regola del trapezio**.

**Il problema:** calcolare l'integrale definito di una funzione f(x) su [a, b] usando la regola del trapezio con n intervalli.

**Strategia di parallelizzazione:**
1. Il dominio di integrazione [a, b] viene suddiviso in p sottointervalli (uno per processo).
2. Ogni processo calcola la somma trapezoidale locale sul proprio sottointervallo.
3. Si usa `MPI_Reduce` con `MPI_SUM` per sommare tutti i contributi locali sul processo root.

Questo e' lo stesso esempio della lezione precedente (Lezione 24), ma reimplementato usando `MPI_Reduce` al posto delle comunicazioni punto-a-punto MPI_Send/Recv. Il codice risulta piu' semplice e potenzialmente piu' efficiente.

**Esempio di codice:** `mpi_trapezoidreduce.cpp`

---

## SLIDE 11 – Scatter

```c
int MPI_Scatter(const void* sndbuf, int sndcount, MPI_Datatype snddt,
                void* rcvbuf, int rcvcount, MPI_Datatype rcvdt,
                int root, MPI_Comm comm)
```

**MPI_Scatter** distribuisce blocchi di dati dal processo root a tutti i processi nel comunicatore (incluso root stesso). E' il pattern one-to-all con blocchi differenti per ogni processo.

**Differenza con MPI_Bcast:**
- Bcast invia lo stesso dato a tutti.
- Scatter invia una parte diversa del buffer a ogni processo (partizionamento).

**Come funziona:**
- Il buffer di invio sul root contiene p blocchi contigui di `sndcount` elementi ciascuno.
- Il blocco i-esimo viene inviato al processo di rank i.
- Il processo di rank i riceve `rcvcount` elementi nel proprio `rcvbuf`.

**Vincolo:** `MPI_Scatter` richiede che tutti i blocchi abbiano la stessa dimensione. Se i blocchi hanno dimensioni diverse, si usa `MPI_Scatterv`.

**Schema:**
```
root: [A0 | A1 | A2 | A3 | A4 | A5] --> Scatter
rank 0 riceve A0
rank 1 riceve A1
rank 2 riceve A2
...
rank 5 riceve A5
```

---

## SLIDE 12 – Gather

```c
int MPI_Gather(const void* sndbuf, int sndcount, MPI_Datatype snddt,
               void* rcvbuf, int rcvcount, MPI_Datatype rcvdt,
               int root, MPI_Comm comm)
```

**MPI_Gather** e' l'operazione duale di Scatter: raccoglie un blocco da ogni processo del comunicatore e li concatena nel buffer del processo root (pattern all-to-one con blocchi).

**Come funziona:**
- Ogni processo (incluso root) invia `sndcount` elementi dal proprio `sndbuf`.
- Il processo root raccoglie tutti i blocchi nel proprio `rcvbuf`, nell'ordine dei rank.
- Il blocco del processo rank i viene posizionato alla posizione i nel buffer del root.

**Schema:**
```
rank 0: A0 \
rank 1: A1  |
rank 2: A2  |--> Gather --> root: [A0 | A1 | A2 | A3 | A4 | A5]
rank 3: A3  |
rank 4: A4  |
rank 5: A5 /
```

---

## SLIDE 13 – Esempio Map: Somma di Vettori (1/2)

**Problema:** eseguire una computazione Map parallela per la somma elemento per elemento di due vettori A e B di n elementi, producendo il vettore C:
```
A, B, C ∈ R^n
c_i = a_i + b_i  per ogni i ∈ {0, ..., n-1}
```

**Strategia con MPI usando p processi (caso n mod p = 0):**

1. Il processo root partiziona i vettori A e B in p blocchi di n/p elementi ciascuno.
2. **MPI_Scatter** distribuisce i blocchi di A e B a tutti i p processi.
3. Ogni processo calcola la somma locale: `C_locale[i] = A_locale[i] + B_locale[i]`.
4. **MPI_Gather** raccoglie tutti i blocchi locali C nel vettore risultato C sul root.

**Assunzione semplificativa:** nella prima versione si richiede che `n mod p == 0`, cioe' n sia multiplo di p, in modo che ogni processo riceva esattamente n/p elementi.

**Esempio di codice:** `mpi_vectorsum.cpp`

---

## SLIDE 14 – Esempio Map: Somma di Vettori (2/2) – Scatterv/Gatherv

Nella versione piu' generale, n non deve essere multiplo di p. Si usano le varianti con suffisso `v` (variable), che permettono blocchi di dimensioni diverse:

```c
int MPI_Scatterv(const void* sndbuf, const int sndcounts[], const int displs[],
                 MPI_Datatype snddt,
                 void* rcvbuf, int rcvcount, MPI_Datatype rcvdt,
                 int root, MPI_Comm comm)

int MPI_Gatherv(const void* sndbuf, int sndcount, MPI_Datatype snddt,
                void* rcvbuf, const int rcvcounts[], const int displs[],
                MPI_Datatype rcvdt, int root, MPI_Comm comm)
```

**Parametri aggiuntivi:**
- `sndcounts[]`: array di p interi, dove `sndcounts[i]` e' il numero di elementi da inviare al processo i.
- `displs[]` (displacement): array di p interi, dove `displs[i]` e' l'offset (in unita' del datatype) nel buffer sorgente da cui inizia il blocco per il processo i.

Questi parametri permettono di:
- Gestire il caso `n mod p != 0` (gli ultimi processi ricevono un elemento in piu' o in meno).
- Avere gap tra i blocchi nel buffer sorgente.
- Inviare blocchi di dimensioni diverse (distribuzione irregolare).

**Nota importante:** `sndcounts[]`, `displs[]` e `rcvcounts[]` sono significativi solo sul processo root; gli altri processi passano NULL o valori irrilevanti per queste strutture.

**Esempio di codice:** `mpi_vectorsumv.cpp`

---

## SLIDE 15 – Allgather / Allgatherv

```c
int MPI_Allgather(const void* sndbuf, int sndcount, MPI_Datatype snddt,
                  void* rcvbuf, int rcvcount, MPI_Datatype rcvdt,
                  MPI_Comm comm)

int MPI_Allgatherv(const void* sndbuf, int sndcount, MPI_Datatype snddt,
                   void* rcvbuf, const int rcvcounts[], const int displs[],
                   MPI_Datatype rcvdt, MPI_Comm comm)
```

**MPI_Allgather** e' come `MPI_Gather` ma senza un unico root: al termine dell'operazione, **tutti** i processi hanno nel proprio `rcvbuf` la concatenazione dei dati di tutti i processi (pattern all-to-all gather).

**Equivalenza funzionale:** `MPI_Gather` + `MPI_Bcast`, ma solitamente piu' efficiente come singola collettiva.

**Schema:**
```
rank 0: A0        --> dopo Allgather: [A0 B0 C0 D0 E0 F0]
rank 1: B0        --> dopo Allgather: [A0 B0 C0 D0 E0 F0]
rank 2: C0        --> dopo Allgather: [A0 B0 C0 D0 E0 F0]
rank 3: D0        --> dopo Allgather: [A0 B0 C0 D0 E0 F0]
rank 4: E0        --> dopo Allgather: [A0 B0 C0 D0 E0 F0]
rank 5: F0        --> dopo Allgather: [A0 B0 C0 D0 E0 F0]
```

Tutti i processi ottengono l'intera raccolta di dati.

**Esempio di codice:** `mpi_collectreverse.cpp`

---

## SLIDE 16 – Allreduce

```c
int MPI_Allreduce(const void* sndbuf, void* rcvbuf, int count,
                  MPI_Datatype dt, MPI_Op op, MPI_Comm comm)
```

**MPI_Allreduce** combina i valori di tutti i processi con un operatore di riduzione e distribuisce il risultato a **tutti** i processi (non solo al root). E' funzionalmente equivalente a `MPI_Reduce` + `MPI_Bcast`, ma piu' efficiente come singola operazione.

**Differenza con MPI_Reduce:**
- MPI_Reduce deposita il risultato solo sul processo root.
- MPI_Allreduce deposita il risultato su **tutti** i processi.

**Schema:**
```
rank 0: A0 \
rank 1: A1  |
rank 2: A2  |--> Allreduce --> tutti i rank ottengono A = op(A0, A1, A2, A3, A4, A5)
rank 3: A3  |
rank 4: A4  |
rank 5: A5 /
```

**Caso d'uso tipico:** normalizzazione di un vettore distribuito (ogni processo ha bisogno della norma globale per calcolare il proprio contributo normalizzato), convergence check in algoritmi iterativi (tutti i processi devono sapere se il criterio di arresto e' soddisfatto).

---

## SLIDE 17 – Esempio: Power Iteration

**Power Iteration** e' un semplice algoritmo numerico per calcolare la coppia autovalore-autovettore dominante di una matrice, ovvero la coppia (lambda_max, x_max) associata all'autovalore di modulo massimo.

**Algoritmo sequenziale:**
```
dato A ∈ R^(n×n) diagonalizzabile, x_0 ≠ 0 (scelto a caso)
per k = 1, ..., max_iters:
    y_k = A * x_{k-1}                    // prodotto matrice-vettore
    x_k = y_k / ||y_k||_2                // normalizzazione per stabilita'
    lambda_k = (x_k^T * y_k) / (x_k^T * x_k)   // quoziente di Rayleigh
    se ||x_k - x_{k-1}||_2 < epsilon: stop       // test di convergenza
```

**Parallelizzazione con MPI:**

La struttura dell'algoritmo e' iterativa Map-Reduce:

1. **Inizializzazione:** la matrice A viene partizionata tra i processi (ogni processo ne possiede alcune righe). Il vettore x iniziale viene replicato su tutti i processi con `MPI_Bcast`.

2. **Prodotto matrice-vettore distribuito:** ogni processo calcola il contributo locale `y_locale = A_locale * x`, producendo un chunk di y.

3. **MPI_Allgather (o MPI_Allgatherv):** raccoglie i chunk locali di y da tutti i processi, in modo che ogni processo abbia il vettore y completo.

4. **Normalizzazione:** ogni processo normalizza y per ottenere x_{k+1}. (Richiede `MPI_Allreduce` con `MPI_SUM` per calcolare la norma globale ||y||_2.)

5. **Quoziente di Rayleigh e test di convergenza:** richiedono produzioni scalari globali, implementate con `MPI_Allreduce`.

**Esempi di codice:** `mpi_power-iteration_replicated.cpp` e `mpi_power-iteration_partitioned.cpp`

---

## SLIDE 18 – Alltoall / Alltoallv

```c
int MPI_Alltoall(const void* sndbuf, int sndcount, MPI_Datatype snddt,
                 void* rcvbuf, int rcvcount, MPI_Datatype rcvdt,
                 MPI_Comm comm)

int MPI_Alltoallv(const void* sndbuf, const int sndcounts[], const int sdispls[],
                  MPI_Datatype snddt,
                  void* rcvbuf, const int rcvcounts[], const int rdispls[],
                  MPI_Datatype rcvdt, MPI_Comm comm)
```

**MPI_Alltoall** e' il pattern piu' generale di comunicazione collettiva: ogni processo effettua un'operazione di Scatter verso tutti gli altri processi. Il risultato e' che ogni processo i invia il blocco j al processo j, e riceve dal processo j il blocco i.

**Analogia:** e' equivalente a una **trasposizione di matrice** distribuita. Se i dati di tutti i processi vengono visualizzati come una matrice p x p (processo i possiede la riga i), dopo Alltoall ogni processo possiede una colonna.

**Schema:**
```
Prima:
rank 0: [A0 A1 A2 A3 A4 A5]  (A0 per rank 0, A1 per rank 1, ...)
rank 1: [B0 B1 B2 B3 B4 B5]
...

Dopo Alltoall:
rank 0: [A0 B0 C0 D0 E0 F0]  (il blocco con indice 0 da ogni rank)
rank 1: [A1 B1 C1 D1 E1 F1]
...
```

**MPI_Alltoall** assume blocchi di dimensione uguale. Per blocchi di dimensioni diverse si usa **MPI_Alltoallv** (che prende array di sndcounts/sdispls e rcvcounts/rdispls).

---

## SLIDE 19 – Esempio: FFT Distribuita

Questo slide illustra come MPI_Alltoall venga utilizzato per implementare una **FFT monodimensionale distribuita** (Fast Fourier Transform).

**Perche' serve Alltoall nella FFT:**
Gli algoritmi FFT su dati distribuiti richiedono un passo di redistribuzione (o trasposizione) dei dati tra le fasi locali di calcolo. Questo perche' la FFT lavora sia nel dominio del tempo sia in quello delle frequenze, e il modo in cui i dati sono partizionati cambia tra le due fasi.

**Struttura dell'algoritmo distribuito:**
1. Ogni processo possiede un sottoinsieme di coefficienti (distribuzione interleaved: il processo r possiede `x[r], x[r+P], x[r+2P], ...`).
2. Ogni processo esegue una FFT locale (usando la libreria FFTW) sul proprio sottoinsieme.
3. **MPI_Alltoall** implementa la trasposizione distribuita: ogni processo divide i propri coefficienti in P blocchi e invia un blocco a ciascun altro processo.
4. Dopo Alltoall, ogni processo possiede un blocco di frequenze raccolto da tutti.
5. Si esegue un'ulteriore FFT locale su ogni blocco.

**Note implementative:**
- Vincolo semplificativo: `N % (P*P) == 0`.
- Si usa MPI_Alltoall con blocchi di uguale dimensione.
- L'opzione `--check` confronta il risultato con la FFT seriale (calcolata da FFTW) per verificare la correttezza; per P > 1 possono esistere piccole differenze numeriche dovute all'ordine delle operazioni in virgola mobile.
- In codice di produzione si preferisce usare direttamente l'interfaccia MPI di FFTW o una libreria FFT distribuita ottimizzata.

**Esempio di codice:** `mpi_fft1d.cpp`

---

## SLIDE 20 – Parallel Prefix (Scan / Exscan)

MPI fornisce due varianti dell'operazione di prefix (scan), gia' vista nel corso nel contesto PRAM e OpenMP:

**Inclusive Scan:**
```c
int MPI_Scan(const void* sndbuf, void* rcvbuf, int count,
             MPI_Datatype dt, MPI_Op op, MPI_Comm comm)
```
Il processo i calcola `result_i = op(v_0, v_1, ..., v_i)` (include il contributo del processo i stesso).

**Exclusive Scan:**
```c
int MPI_Exscan(const void* sndbuf, void* rcvbuf, int count,
               MPI_Datatype dt, MPI_Op op, MPI_Comm comm)
```
Il processo i calcola `result_i = op(v_0, v_1, ..., v_{i-1})` (esclude il contributo del processo i). Il risultato per il processo 0 e' indefinito (non c'e' alcun prefisso precedente).

**Esempio con count = 1 e op = MPI_SUM:**

```
Input:   -2   4   2  -1   0   1  -3   2   0   4   1   5
         p0  p1  p2  p3  p4  p5  p6  p7  p8  p9 p10 p11

scan:    -2   2   4   3   3   4   1   3   3   7   8  13
exscan: undef -2   2   4   3   3   4   1   3   3   7   8
```

**Nota:** quando `count > 1`, MPI_Scan esegue k riduzioni prefisso indipendenti, una per ogni posizione j = 0, ..., k-1: `rcvbuf[j] = op(sndbuf_rank0[j], ..., sndbuf_rank_i[j])`.

---

## SLIDE 21 – MPI_Scan (Inclusive) – Esempi

Questa slide illustra il comportamento di MPI_Scan con due scenari concreti.

**Caso 1: count = 1, p = 4 processi, op = MPI_SUM**
```
sndbuf dei processi: p0 = -2, p1 = 3, p2 = 8, p3 = -1
rcvbuf dopo Scan:    p0 = -2, p1 = 1, p2 = 9, p3 = 8
```
- p0 riceve: -2 (solo il suo valore)
- p1 riceve: -2 + 3 = 1
- p2 riceve: -2 + 3 + 8 = 9
- p3 riceve: -2 + 3 + 8 + (-1) = 8

**Caso 2: count = 3, p = 2 processi, op = MPI_SUM**
```
sndbuf p0: [1, 2, 3]
sndbuf p1: [4, 5, 6]

rcvbuf p0: [1, 2, 3]          (solo i valori di p0)
rcvbuf p1: [1+4, 2+5, 3+6] = [5, 7, 9]
```
Quando count = k, MPI_Scan esegue k scan indipendenti (uno per elemento del vettore), e `rcvbuf[j] = op(sndbuf_0[j], ..., sndbuf_rank[j])` per j = 0, ..., k-1.

**Esempio di codice:** `mpi_scan.cpp`

---

## SLIDE 22 – Elenco delle Collettive Principali

Riepilogo di tutte le operazioni collettive viste, con il rispettivo pattern di comunicazione:

| Collettiva       | Pattern                          |
|------------------|----------------------------------|
| MPI_Barrier      | Sincronizzazione                 |
| MPI_Bcast        | One-to-all                       |
| MPI_Scatter      | One-to-all (blocchi diversi)     |
| MPI_Gather       | All-to-one (blocchi)             |
| MPI_Reduce       | All-to-one (riduzione)           |
| MPI_Allgather    | All-to-all gather                |
| MPI_Allreduce    | All-to-all riduzione             |
| MPI_Alltoall     | All-to-all scambio personalizzato|
| MPI_Scan         | Prefix reduction inclusivo       |
| MPI_Exscan       | Prefix reduction esclusivo       |

**Varianti non bloccanti:** tutte le collettive hanno una versione non bloccante con prefisso `I` (es. MPI_Ibarrier, MPI_Ibcast, MPI_Iscatter, MPI_Igather, MPI_Ireduce, MPI_Iallgather, MPI_Iallreduce, MPI_Ialltoall, MPI_Iscan, ...). Il completamento va verificato con MPI_Wait o MPI_Test sul request restituito.

**Varianti a dimensione variabile:** quando i blocchi da distribuire o raccogliere hanno dimensioni diverse, si usano le varianti con suffisso `v`: MPI_Scatterv, MPI_Gatherv, MPI_Allgatherv, MPI_Alltoallv.

---

## SLIDE 23 – Letture Consigliate

Riferimenti bibliografici e risorse per approfondire MPI:

- **Libro di testo del corso:** "Parallel Programming Concepts and Practice" – Capitolo 9.
- **Standard MPI ufficiale:** MPI: A Message-Passing Interface Standard Version 4.1.
  URL: https://www.mpi-forum.org/docs/mpi-4.1/mpi41-report.pdf
- **Documentazione Open MPI:** https://docs.open-mpi.org/en/v5.0.x/
- **Tutorial MPI (LLNL):** https://hpc-tutorials.llnl.gov/mpi/ — tutorial pratico del Lawrence Livermore National Laboratory, utile per esempi e spiegazioni progressive.
- **OSU Micro-Benchmarks:** https://mvapich.cse.ohio-state.edu/benchmarks/ — suite di benchmark per misurare le prestazioni delle operazioni MPI (latenza, bandwidth, collettive). Sul cluster `spmcluster`, i benchmark sono installati in `/opt/ohpc/pub/mpi/osu-7.4/`.
