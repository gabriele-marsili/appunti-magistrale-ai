# SPM – Lezione 26: MPI Part III
## Appunti divisi per slide

---

## SLIDE 1 – Titolo

**SPM: Message Passing Interface (MPI) – Part III**
Anno accademico 2025-2026 – Prof. Massimo Torquati

---

## SLIDE 2 – Outline

Questa terza parte su MPI tratta le funzionalita' avanzate:

- **Gruppi e Comunicatori:** definire chi comunica con chi, tramite gruppi, comunicatori e topologie virtuali.
- **Tipi di dato derivati MPI:** definire quale layout di memoria viene comunicato, tramite datatypes personalizzati.
- **MPI e thread:** programmazione ibrida MPI + thread (OpenMP, C++ threads, FastFlow, CUDA, ecc.).

Due problemi fondamentali risolti dalle funzionalita' avanzate:
1. Definire *chi comunica con chi* (via gruppi, comunicatori, topologie).
2. Definire *quale layout di memoria* viene comunicato (via tipi di dato derivati).

---

## SLIDE 3 – Gruppi (Groups)

Un **gruppo MPI** e' un insieme ordinato di processi. Ogni processo nel gruppo e' associato a un rank univoco (da 0 a groupsize-1). Un gruppo e' solitamente associato a un oggetto comunicatore, che definisce il contesto di comunicazione.

**Ottenere il gruppo di un comunicatore:**
```c
int MPI_Comm_group(MPI_Comm comm, MPI_Group *group);
```

**Costruire nuovi gruppi da gruppi esistenti:**
MPI fornisce operazioni insiemistiche sui gruppi:
- `MPI_Group_union()` — unione di due gruppi
- `MPI_Group_intersection()` — intersezione
- `MPI_Group_difference()` — differenza
- `MPI_Group_incl()` — include un sottoinsieme di rank
- `MPI_Group_excl()` — esclude un sottoinsieme di rank

**Esempio: suddivisione in gruppi pari e dispari**
```c
int even = (p+1)/2;
for(i=0; i < even; ++i) members[i] = 2 * i;

MPI_Group world_group, even_group, odd_group;
MPI_Comm_group(MPI_COMM_WORLD, &world_group);
MPI_Group_incl(world_group, even, members, &even_group);
MPI_Group_excl(world_group, even, members, &odd_group);
```
Il codice crea un gruppo `even_group` con i rank pari (0, 2, 4, ...) e un gruppo `odd_group` con i rank dispari (1, 3, 5, ...).

**Esempio di codice:** `mpi_group.cpp`

---

## SLIDE 4 – Comunicatori (Communicators)

Un **comunicatore MPI** racchiude un gruppo di processi che possono comunicare tra loro. Lega un gruppo di processi a un contesto di comunicazione. Il contesto impedisce che messaggi di comunicatori diversi si sovrappongano (non-interference): i messaggi inviati su un comunicatore non possono essere ricevuti su un altro.

**Tipi di comunicatori:**
- **Intracommunicator:** usato per comunicazioni all'interno di un gruppo (il caso piu' comune).
- **Intercommunicator:** usato per comunicazioni tra gruppi distinti.

**Scopi principali:** comunicazioni collettive su sottogruppi di processi, topologie virtuali definite dall'utente.

**Principali funzioni di gestione dei comunicatori:**
```c
// Crea un nuovo comunicatore dal gruppo specificato
int MPI_Comm_create(MPI_Comm old_comm, MPI_Group group, MPI_Comm* new_comm)

// Confronta due comunicatori
int MPI_Comm_compare(MPI_Comm comm1, MPI_Comm comm2, int* res)

// Duplica un comunicatore (stesso gruppo, contesto diverso)
int MPI_Comm_dup(MPI_Comm comm, MPI_Comm* new_comm)

// Suddivide un comunicatore in sottocomunicatori (vedi slide successiva)
int MPI_Comm_split(MPI_Comm comm, int color, int key, MPI_Comm* new_comm)
```

MPI fornisce oltre 40 funzioni per gruppi, comunicatori e topologie virtuali.

---

## SLIDE 5 – Splitting dei Comunicatori

```c
int MPI_Comm_split(MPI_Comm comm, int color, int key, MPI_Comm* new_comm)
```

**MPI_Comm_split** e' l'operazione piu' usata per suddividere un comunicatore in sottocomunicatori disgiunti. E' un'operazione collettiva: tutti i processi nel comunicatore originale devono chiamarla.

**Come funziona:**
- Tutti i processi con lo stesso valore di `color` formano un nuovo sottocomunicatore.
- All'interno di ogni sottocomunicatore, i rank sono ordinati secondo il valore di `key` (in caso di parita', secondo il rank originale nel comunicatore padre).

**Esempio: griglia 4x4 – comunicatori di riga**
```c
int rank;
MPI_Comm_rank(MPI_COMM_WORLD, &rank);
int color = rank / 4;   // un color per ogni riga logica
int key   = rank % 4;   // ordine all'interno del comunicatore di riga

MPI_Comm row_comm;
MPI_Comm_split(MPI_COMM_WORLD, color, rank, &row_comm);
```

In una griglia 4x4 con 16 processi (rank 0..15):
- I processi 0,1,2,3 (riga 0) hanno color=0 --> formano `row_comm` con rank 0,1,2,3
- I processi 4,5,6,7 (riga 1) hanno color=1 --> formano `row_comm` con rank 0,1,2,3
- Ecc.

**Nota:** il parametro `key` definisce l'ordine dei rank nel nuovo comunicatore, non il rank stesso.

**Esempio di codice:** `mpi_split.cpp`

---

## SLIDE 6 – Topologie Virtuali (breve menzione)

Una **topologia virtuale** rappresenta il modo in cui i processi MPI sono logicamente organizzati e comunicano.

**Tipologie:**
- **Topologia cartesiana:** organizzazione regolare in griglia 2D o 3D. Utile per problemi strutturati come Jacobi, moltiplicazione di matrici, stencil computations.
  ```c
  int MPI_Cart_create(MPI_Comm comm_old, int ndims, int* dims, int* periods,
                      int reorder, MPI_Comm* comm_cart)
  ```
  - `ndims`: numero di dimensioni.
  - `dims`: dimensione di ogni asse.
  - `periods`: indica se la griglia e' periodica (toroidale) su ogni asse.
  - `reorder`: se 1, MPI puo' riordinare i rank per ottimizzare il mapping sui nodi fisici.

- **Topologia a grafo:** per comunicazioni irregolari non strutturate come griglie.
  ```c
  int MPI_Graph_create(MPI_Comm comm_old, int nnodes, int* index, int* edges,
                       int reorder, MPI_Comm* cgraph)
  ```

Le topologie virtuali non cambiano le prestazioni di per se', ma forniscono funzioni di utilita' come `MPI_Cart_shift` (per trovare i vicini in una griglia) e consentono a MPI di ottimizzare il mapping sui processori fisici se `reorder=1`.

Riferimento: Sezione 8 della specifica MPI 4.1.

**Esempio di codice:** `mpi_cartesiantopo.cpp`

---

## SLIDE 7 – Tipi di Dato Derivati MPI

MPI permette agli utenti di costruire nuovi tipi di dato personalizzati basandosi sui tipi primitivi MPI (MPI_INT, MPI_FLOAT, MPI_DOUBLE, ecc.).

**Cosa descrive un tipo derivato:** il layout in memoria dei dati da comunicare. Non copia i dati di per se'; il movimento effettivo avviene quando il tipo viene usato in una chiamata di comunicazione.

**Perche' sono utili:**
- **Dati non contigui in memoria:** ad esempio, le colonne di una matrice memorizzata in row-major order non sono contigue. Senza tipi derivati, bisognerebbe copiare i dati in un buffer temporaneo contiguo prima di inviarli (packing manuale).
- **Dati eterogenei:** strutture C/C++ che contengono tipi diversi (es. una struct con un intero e un array di float).

**Vantaggi pratici:**
- Migliorano la leggibilita' del codice evitando codice di packing/unpacking ripetitivo.
- Possono migliorare le prestazioni riducendo il numero di copie in memoria e il numero di messaggi.

**Struttura di un tipo derivato MPI:** e' un oggetto opaco che specifica:
- Una sequenza di tipi di base.
- Una sequenza di displacement (offset) che indicano dove si trova ogni blocco in memoria.
- L'ordine degli elementi non deve necessariamente corrispondere al loro ordine in memoria; un elemento puo' comparire piu' volte.

---

## SLIDE 8 – Costruzione di un Tipo Derivato

I passi fondamentali per creare e usare un tipo derivato MPI sono:

1. **Costruire il tipo** usando un costruttore (es. `MPI_Type_vector()`). Il nuovo tipo ha tipo C `MPI_Datatype`.
2. **Committare il tipo** con `MPI_Type_commit()`, rendendolo utilizzabile nelle chiamate di comunicazione.
3. **Liberare il tipo** con `MPI_Type_free()` quando non e' piu' necessario (facoltativo ma raccomandato per evitare memory leak).

```c
MPI_Datatype new_type;    // dichiara il nuovo tipo
...
MPI_Type_vector(..., &new_type);   // costruisce new_type
MPI_Type_commit(&new_type);        // commit new_type (obbligatorio prima dell'uso)
...
// uso in chiamate MPI_Send, MPI_Recv, collettive, ecc.
...
MPI_Type_free(&new_type);          // libera new_type (raccomandato)
```

---

## SLIDE 9 – Costruttori di Tipi Derivati

I costruttori di tipi derivati piu' comunemente usati sono:

**1. MPI_Type_contiguous** — blocco contiguo:
```c
int MPI_Type_contiguous(int count, MPI_Datatype oldtype, MPI_Datatype* newtype)
```
Crea un nuovo tipo come concatenazione di `count` copie di `oldtype`.

**2. MPI_Type_vector** — blocchi con stride:
```c
int MPI_Type_vector(int count, int blocklen, int stride,
                    MPI_Datatype oldtype, MPI_Datatype* newtype)
```
Crea un tipo formato da `count` blocchi di `blocklen` elementi, separati da un gap di `stride` elementi (misurato in estensioni di `oldtype`, non in byte).

**3. MPI_Type_create_struct** — struttura eterogenea:
```c
int MPI_Type_create_struct(int count, int blocklen[], MPI_Aint displacements[],
                           MPI_Datatype oldtype[], MPI_Datatype* newtype)
```
Crea un tipo da un insieme di blocchi di tipi diversi. I displacements sono espressi in **byte** (usare `MPI_Get_address()` per calcolarli in modo portabile). `MPI_Aint` e' un tipo MPI abbastanza grande da contenere indirizzi di memoria.

**4. MPI_Type_indexed** — blocchi con displacement variabili:
```c
int MPI_Type_indexed(int count, int blocklen[], int displacements[],
                     MPI_Datatype oldtype, MPI_Datatype* newtype)
```
Come vector ma con displacement diversi per ogni blocco. I displacement sono espressi in estensioni di `oldtype`. Per displacement in byte, usare `MPI_Type_create_hindexed`.

---

## SLIDE 10 – Tipo Contiguo (Contiguous)

```c
int MPI_Type_contiguous(int count, MPI_Datatype oldtype, MPI_Datatype* newtype)
```

Il tipo risultante (`newtype`) e' la concatenazione di `count` copie di `oldtype`, senza gap tra loro. E' il tipo piu' semplice: equivalente a inviare un array contiguo di `count` elementi.

**Esempio visivo (count=4, oldtype=double):**
```
newtype:
| double | double | double | double |
```
(4 double contigui in memoria)

**Uso tipico:** quando si vuole incapsulare un array di tipo noto in un singolo datatype per comodita' o per uniformita' dell'interfaccia.

---

## SLIDE 11 – Tipo Vettore (Vector)

```c
int MPI_Type_vector(int count, int blocklen, int stride,
                    MPI_Datatype oldtype, MPI_Datatype* newtype)
```

**Parametri:**
- `count`: numero di blocchi.
- `blocklen`: numero di elementi in ogni blocco.
- `stride`: distanza (in numero di elementi di `oldtype`) tra l'inizio di due blocchi consecutivi.

**Esempio visivo (count=3, blocklen=2, stride=4, oldtype=double):**
```
Memoria:
| d0 | d1 | d2 | d3 | d4 | d5 | d6 | d7 | d8 | d9 | d10 | d11 |
  [blocco 1: d0,d1]       [blocco 2: d4,d5]       [blocco 3: d8,d9]
                 ^stride=4^              ^stride=4^
```

**Caso d'uso classico:** estrarre le colonne di una matrice stored in row-major order. Se la matrice ha n colonne, per inviare la colonna j si usa `MPI_Type_vector(n_rows, 1, n_cols, MPI_DOUBLE, &col_type)`.

Per stride in byte (invece che in elementi), usare `MPI_Type_create_hvector()`.

**Esempio di codice:** `mpi_rowcol.cpp`

---

## SLIDE 12 – Tipo Struttura (Struct)

```c
int MPI_Type_create_struct(int count, int blocklen[],
                           MPI_Aint displacements[], MPI_Datatype oldtypes[],
                           MPI_Datatype* newtype)
```

**Parametri:**
- `count`: numero di blocchi.
- `blocklen[]`: numero di elementi in ogni blocco.
- `displacements[]`: offset in **byte** di ogni blocco rispetto all'inizio della struttura.
- `oldtypes[]`: tipo MPI di ogni blocco.

**Esempio: struttura Particle con 2 float e 1 int:**
```c
struct Particle {
    float x;
    float y;
    int type;
} p;

int blocklen[] = {2, 1};                        // 2 float, 1 int
MPI_Datatype oldtypes[] = {MPI_FLOAT, MPI_INT};
MPI_Aint xaddr, typeaddr, displs[2];
MPI_Get_address(&p.x,    &xaddr);
MPI_Get_address(&p.type, &typeaddr);
displs[0] = 0;
displs[1] = typeaddr - xaddr;

MPI_Type_create_struct(2, blocklen, displs, oldtypes, &new_type);
MPI_Type_commit(&new_type);
```

**Nota importante:** impostare i displacement manualmente e' non portabile (dipende dall'allineamento del compilatore). Usare sempre `MPI_Get_address()` per calcolare i displacement in modo portabile.

**Nota avanzata:** se il tipo viene usato con `count > 1` per inviare un array di strutture, verificare l'extent del tipo. Spesso e' necessario `MPI_Type_create_resized` per rendere l'extent uguale a `sizeof(struct)` (evitare padding issues tra elementi consecutivi dell'array).

**Esempio di codice:** `mpi_struct.cpp`

---

## SLIDE 13 – Esempi Applicativi

Questa slide elenca gli esempi di codice del corso in cui comunicatori e tipi derivati diventano utili in codice reale:

- **`mpi_jacobi_1d_blk.cpp`** — Algoritmo di iterazione di Jacobi con comunicazioni bloccanti (MPI_Send/Recv). Mostra come i processi adiacenti si scambiano le "halo rows" (righe fantasma) per calcolare lo stencil sui bordi della loro partizione.

- **`mpi_jacobi_1d_nblk.cpp`** — Stessa iterazione di Jacobi ma con comunicazioni non bloccanti (MPI_Isend/Irecv), per sovrapporre la comunicazione delle halo rows con il calcolo sugli elementi interni.

- **`mpi_mm2d.cpp`** — Moltiplicazione di matrici con partizionamento 2D semplice. Esempio base di come usare comunicatori per le operazioni sulle righe e colonne della griglia di processi.

- **`mpi_summa.cpp`** — Scalable Universal Matrix Multiplication Algorithm (SUMMA): un algoritmo sofisticato per moltiplicazione di matrici distribuite che usa comunicatori di riga e colonna per broadcast di pannelli. (vedi slide 16-18)

---

## SLIDE 14 – Esempio: Iterazioni di Jacobi

**Stencil a 5 punti** su griglia 2D, parallelizzazione con decomposizione 1D (ogni processo possiede un blocco contiguo di righe della matrice):

**Il problema delle halo rows (righe fantasma):**
- Per calcolare lo stencil sui punti di bordo di ogni partizione, ogni processo ha bisogno di una riga del processo vicino (superiore e inferiore).
- **Halo row** = una copia locale dell'ultima/prima riga del processo vicino.

**Schema di comunicazione:**
- Il processo P1 ha bisogno dell'ultima riga di P0 e della prima riga di P2 per aggiornare i punti di bordo della propria partizione.
- P0 ha bisogno della prima riga di P1.
- P2 ha bisogno dell'ultima riga di P1.

In ogni iterazione, i processi si scambiano queste righe di halo prima di procedere al calcolo dello stencil. Lo schema con bloccanti richiede attenzione per evitare deadlock (usare send-receive alternato o `MPI_Sendrecv`).

**Esempi di codice:** `jacobi_seq.cpp` e `mpi_jacobi_1d_blk.cpp`

---

## SLIDE 15 – Sovrapposizione Computazione e Comunicazione (Jacobi non-bloccante)

**Il problema con le comunicazioni bloccanti:**
- Il processo deve prima inviare/ricevere le halo rows, poi eseguire tutto il calcolo.
- Tempo totale per iterazione: `T_iterazione = T_comm + T_calc`.

**Ottimizzazione con comunicazioni non bloccanti:**
- I punti interni della partizione (non a bordo) non dipendono dalle halo rows.
- Si puo' avviare la comunicazione non bloccante delle halo rows (`MPI_Isend`/`MPI_Irecv`), poi calcolare lo stencil sui punti interni (che non richiedono le halo rows), e infine attendere (`MPI_Wait`) il completamento della comunicazione prima di calcolare i punti di bordo.
- Questo permette di sovrapporre comunicazione e computazione.

**Formule di tempo:**
```
Senza overlap (bloccante):   T_C = T_calc + T_comm
Con overlap (non-bloccante): T_C = max(T_calc, T_comm)   (caso ideale)
```

**Nota importante:** le comunicazioni non bloccanti MPI consentono il potenziale overlap, ma non lo garantiscono. L'overlap effettivo dipende dal progresso MPI, dalla dimensione dei messaggi e dalla disponibilita' di computazione indipendente.

**Esempio di codice:** `mpi_jacobi_1d_nblk.cpp`

---

## SLIDE 16 – Comunicatori Complessi: SUMMA (1/3)

**SUMMA (Scalable Universal Matrix Multiplication Algorithm):** algoritmo di moltiplicazione di matrici distribuite progettato per scalare efficientemente su griglie di processi di grandi dimensioni.

**Setup:** le matrici A (m x k), B (k x n) e C (m x n) sono inizialmente distribuite tra i processi organizzati in una griglia p_rows x p_cols. Non tutti i dati necessari a calcolare un prodotto parziale si trovano nella memoria locale di ogni processo.

**Esempio:** per calcolare il blocco C01 del processo (0,1):
```
C01 = A00 * B01 + A01 * B11 + A02 * B21
```
Il processo (0,1) deve avere accesso ai blocchi A0j e Bi1 che appartengono ad altri processi.

**Soluzione SUMMA:** si usano comunicatori di riga e di colonna per distribuire i dati necessari tramite operazioni di broadcast. Durante l'algoritmo, pannelli di A e B vengono temporaneamente replicati lungo le righe/colonne dei processi attraverso broadcast.

---

## SLIDE 17 – Comunicatori Complessi: SUMMA (2/3) – Le Fasi

**Algoritmo SUMMA con griglia 3x3 (k=3 fasi in generale):**

Per ogni fase l (l = 0, 1, ..., k-1):
- Il processo (i, l) broadcast la propria colonna di A lungo la riga i (broadcast orizzontale).
- Il processo (l, j) broadcast la propria riga di B lungo la colonna j (broadcast verticale).
- Ogni processo (i, j) aggiorna C_ij += A_il * B_lj.

**Schema delle 3 fasi:**
- Fase 1: broadcast della colonna 0 di A lungo ogni riga + broadcast della riga 0 di B lungo ogni colonna.
- Fase 2: broadcast della colonna 1 di A e riga 1 di B.
- Fase 3: broadcast della colonna 2 di A e riga 2 di B.

Ogni processo accumula il prodotto parziale ad ogni fase. Alla fine delle k fasi, ogni processo ha il proprio blocco di C completo.

---

## SLIDE 18 – Comunicatori Complessi: SUMMA (3/3) – Implementazione

**Creazione dei comunicatori di riga e colonna con MPI_Comm_split:**

```c
MPI_Comm rowComm;
MPI_Comm colComm;

// color = myId/gridDim --> tutti i processi della stessa riga hanno lo stesso color
// key   = myId%gridDim --> rank all'interno del nuovo comunicatore (posizione nella riga)
MPI_Comm_split(MPI_COMM_WORLD, myId/gridDim, myId%gridDim, &rowComm);

// color = myId%gridDim --> tutti i processi della stessa colonna hanno lo stesso color
// key   = myId/gridDim --> rank all'interno del nuovo comunicatore (posizione nella colonna)
MPI_Comm_split(MPI_COMM_WORLD, myId%gridDim, myId/gridDim, &colComm);
```

Con questi due comunicatori, il broadcast orizzontale si fa su `rowComm` e il broadcast verticale su `colComm`.

**Nota:** gli stessi comunicatori di riga/colonna potrebbero essere derivati da un comunicatore cartesiano (creato con `MPI_Cart_create`), che e' un'alternativa equivalente.

**Esempio di codice:** `mpi_summa.cpp`

---

## SLIDE 19 – Thread e MPI

MPI descrive il parallelismo tra processi con spazi di indirizzo separati. Di per se', MPI non e' thread-aware: `MPI_Init` fornisce solo l'inizializzazione per un singolo thread.

**Limitazioni di default:** senza supporto ai thread, solo un thread alla volta puo' eseguire routine MPI.

**I thread in MPI non sono indirizzabili:** non e' possibile inviare un messaggio a uno specifico thread di un processo (solo al processo nel suo insieme, identificato dal rank).

**Inizializzazione con supporto ai thread:**
Per usare MPI con thread si deve chiamare `MPI_Init_thread` invece di `MPI_Init`.

**Paradigma "hybrid programming" (MPI + X):**
Il processo MPI puo' usare thread per computazione e/o comunicazione. Le combinazioni piu' comuni sono:
- MPI + OpenMP
- MPI + C++ threads
- MPI + FastFlow
- MPI + CUDA
- MPI + MPI Shared Memory (introdotto in MPI-3, per regioni di memoria condivisa reale tra processi sullo stesso nodo)

**Requisito di compilazione OpenMPI:** OpenMPI deve essere compilato con il flag `--enable-mpi-threads` per avere il supporto ai thread.

---

## SLIDE 20 – Inizializzare MPI per i Thread

```c
int MPI_Init_thread(int* argc, char*** argv, int required, int* provided)
```

**Livelli di supporto ai thread** (argomento `required`):

| Livello                  | Descrizione |
|--------------------------|-------------|
| `MPI_THREAD_SINGLE`      | Il processo e' single-threaded. Equivalente a chiamare `MPI_Init`. |
| `MPI_THREAD_FUNNELED`    | Solo il thread che ha chiamato `MPI_Init_thread` puo' fare chiamate MPI. Con OpenMP, solo il thread master chiama MPI. |
| `MPI_THREAD_SERIALIZED`  | Piu' thread possono chiamare MPI, ma mai concorrentemente. L'applicazione deve serializzare le chiamate. |
| `MPI_THREAD_MULTIPLE`    | Piu' thread possono chiamare funzioni MPI senza restrizioni (livello massimo). |

**Il runtime MPI riempie `provided`** con il livello effettivamente supportato dall'implementazione, che potrebbe essere inferiore a `required`.

**Esempio di utilizzo:**
```c
int provided = 0;
MPI_Init_thread(&argc, &argv, MPI_THREAD_FUNNELED, &provided);
if (provided < MPI_THREAD_FUNNELED)
    MPI_Abort(MPI_COMM_WORLD, 1);   // il livello richiesto non e' disponibile
```

---

## SLIDE 21 – MPI con Thread (Semantica)

**Sezione 11.6 della specifica MPI 4.1.**

**Semantica delle chiamate concorrenti:** quando piu' thread fanno chiamate MPI concorrentemente, il risultato sara' come se le chiamate fossero eseguite sequenzialmente in qualche ordine (linearizzabilita').

**Responsabilita' del programmatore:**
- Assicurarsi che le operazioni collettive siano ordinate correttamente tra i thread: non lasciare che thread diversi emettano collettive sullo stesso comunicatore a meno di poter garantire lo stesso ordine su tutti i processi.
- Assicurarsi che i programmi MPI siano privi di data race.

**Esempio di problema di ordinamento con collettive:**
Se Thread 0 su P0 chiama `MPI_Bcast` e Thread 1 su P1 chiama `MPI_Reduce` sullo stesso comunicatore contemporaneamente, il comportamento e' indefinito perche' l'ordine delle collettive potrebbe differire tra i processi.

---

## SLIDE 22 – MPI con Thread (Concorrenza e Costo)

**Esempio con MPI_THREAD_MULTIPLE:**

```
Processo P0:                    Processo P1:
Thread 0: MPI_Recv(... rank 1...)    MPI_Recv(... rank 0...)
Thread 1: MPI_Send(... rank 1...)    MPI_Send(... rank 0...)
```

Con `MPI_THREAD_MULTIPLE`, la libreria MPI deve permettere chiamate concorrenti da piu' thread e garantire che la chiamata bloccante di un thread non blocchi il progresso di un altro thread. Nell'esempio, qualunque thread venga eseguito per primo, le due send e le due receive si completeranno sempre correttamente.

**Costo di MPI_THREAD_MULTIPLE:**
- L'implementazione deve proteggere certe strutture dati e sezioni di codice con mutex, introducendo overhead.
- `MPI_THREAD_MULTIPLE` rende legali le chiamate MPI concorrenti, ma non necessariamente veloci.
- In applicazioni ad alte prestazioni, e' spesso preferibile usare `MPI_THREAD_FUNNELED` (solo il thread master comunica) per evitare questo overhead.

---

## SLIDE 23 – Esempio: MPI + OpenMP

**Programmazione ibrida MPI + OpenMP** in pratica:

**Attenzione al binding dei processi e all'affinita' dei thread OpenMP:** con piu' nodi e piu' thread per processo, la configurazione di binding e' critica per le prestazioni (evitare che i thread migrino tra nodi NUMA).

**Esempio di lancio su cluster SLURM (round-robin distribution):**
```bash
salloc -N 8
mpirun -x OMP_NUM_THREADS=16 -x OMP_DISPLAY_AFFINITY=true \
       --map-by node --bind-to=none --report-bindings \
       -n 8 ./mpi_trapezoid+omp 200000000
```
- `--map-by node`: distribuisce i processi MPI round-robin sui nodi.
- `--bind-to=none`: non lega i processi a specifici core (lascia che OpenMP gestisca i thread).
- `-x OMP_NUM_THREADS=16`: passa la variabile d'ambiente a tutti i processi MPI.

**Con SLURM (srun):**
```bash
srun --mpi=pmix --export=ALL,OMP_NUM_THREADS=16 --cpu-bind=none \
     ./mpi_trapezoid+omp 2000000000
```

**Esempi di codice:** `mpi_trapezoid+omp.cpp` e `mpi_summa+omp.cpp`

---

## SLIDE 24 – Letture Consigliate

Riferimenti bibliografici e risorse per approfondire MPI avanzato:

- **Libro di testo del corso:** "Parallel Programming Concepts and Practice" – Capitolo 9.
- **Standard MPI ufficiale:** MPI: A Message-Passing Interface Standard Version 4.1.
  URL: https://www.mpi-forum.org/docs/mpi-4.1/mpi41-report.pdf
- **Documentazione Open MPI:** https://docs.open-mpi.org/en/v5.0.x/
- **Tutorial MPI (LLNL):** https://hpc-tutorials.llnl.gov/mpi/
- **OSU Micro-Benchmarks:** https://mvapich.cse.ohio-state.edu/benchmarks/
  Sul cluster spmcluster: `/opt/ohpc/pub/mpi/osu-7.4/`
