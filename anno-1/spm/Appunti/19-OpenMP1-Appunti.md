# SPM – Lezione 19: Parallel Programming with OpenMP – Parte 1
## Appunti divisi per slide

---

## SLIDE 1 – Titolo

**Parallel Programming with OpenMP – Part 1**
Anno accademico 2025-2026 – Prof. Massimo Torquati

---

## SLIDE 2 – Outline

Gli argomenti trattati nella lezione sono:

- Introduzione a OpenMP
- Direttive OpenMP per la parallelizzazione dei loop (loop-parallelism)
- Primitive OpenMP e variabili d'ambiente
- Thread Affinity in OpenMP

---

## SLIDE 3 – OpenMP: Open Multi-Processing (1/2)

**OpenMP** e' un'API per la programmazione parallela a memoria condivisa indipendente dalla piattaforma, disponibile per C, C++ e Fortran. Fornisce astrazioni parallele ad alto livello sopra i meccanismi di threading a basso livello.

OpenMP estende i linguaggi C, C++ e Fortran con:
- **Direttive** (pragma): `#pragma omp ...`
- **Routine di libreria**: es. `omp_get_thread_num()`, `omp_get_num_threads()`
- **Variabili d'ambiente**: es. `OMP_SCHEDULE`, `OMP_NUM_THREADS`

E' supportato nativamente da quasi tutti i compilatori (GCC, Intel, Clang, ...) e viene usato per sfruttare il parallelismo a memoria condivisa su CMP (Chip Multi-Processors).

Il compilatore genera automaticamente il codice multi-thread necessario e tutte le sincronizzazioni richieste in base alle direttive specificate nel codice sorgente.

Esempio minimo:
```
#pragma omp parallel for
for (int i = 0; i < N; ++i)
    foo(i);
```

---

## SLIDE 4 – OpenMP: Open Multi-Processing (2/2)

OpenMP permette ai programmatori di organizzare un programma in **regioni seriali e regioni parallele**, fornendo costrutti di sincronizzazione tramite una sintassi "leggera" (direttive del compilatore).

**OpenMP NON e' un compilatore parallelizzante:** non parallelizza automaticamente il codice sequenziale. Il parallelismo deve essere espresso esplicitamente dal programmatore.

**Responsabilita' del programmatore:**
- Evitare le data race
- Ottenere un buon speedup

La decisione di dove e come parallelizzare spetta al programmatore, non al compilatore.

---

## SLIDE 5 – Breve Storia di OpenMP

- Nato alla fine degli anni '90 da un gruppo di vendor, Intel e il Dipartimento dell'Energia degli Stati Uniti.
- Versione 1.0 rilasciata nel 1997, con supporto solo per Fortran. Il binding per C/C++ fu introdotto successivamente.
- Inizialmente l'obiettivo principale era la parallelizzazione dei loop.
- Nel 2008, **OpenMP 3.0** introduce il parallelismo basato su task, migliorato nelle versioni successive.
- Nel 2013, **OpenMP 4.0** introduce il supporto iniziale per acceleratori (GPGPU).

---

## SLIDE 6 – OpenMP: Facilita' d'Uso

OpenMP e' progettato per essere facile da usare:

- **Non richiede la ristrutturazione del codice single-thread** per il threading.
- Preserva l'equivalenza sequenziale: se le direttive OpenMP vengono ignorate, il programma si comporta esattamente come la versione sequenziale originale.
- Abilita la **parallelizzazione incrementale** di programmi sequenziali: e' possibile aggiungere direttive gradualmente.
- Si basa principalmente su direttive del compilatore: se il compilatore non riconosce una direttiva, la ignora senza errori.
- E' possibile parallelizzare usando solo un piccolo numero di direttive, sia per parallelismo a grana grossa che a grana fine.
- Se il compilatore non e' istruito a processare le direttive OpenMP (flag `-fopenmp` assente), il programma viene eseguito sequenzialmente. Le routine di runtime hanno implementazioni sequenziali di default.

---

## SLIDE 7 – Modello di Esecuzione OpenMP: Fork-Join

OpenMP e' ad un livello piu' alto rispetto ai thread C++/POSIX. Fornisce mappatura implicita e bilanciamento del carico dei task.

**Modello Fork-Join:**
1. L'esecuzione inizia con un singolo thread chiamato **Master thread** (ora chiamato Initial/Primary thread).
2. Quando viene incontrata una **parallel region**, quel thread crea un team (o pool) di Worker thread, e la regione parallela viene eseguita concorrentemente dal team.
3. All'interno della regione, il lavoro viene creato tramite **work-sharing constructs** e task; qualsiasi thread del team puo' eseguire i task.
4. Alla fine di una parallel region c'e' una **sincronizzazione implicita a barriera**: dopo la barriera solo il thread Initial continua l'esecuzione.
5. Il thread pool viene **riutilizzato** per le successive parallel region (non viene ricreato ogni volta, riducendo l'overhead).

---

## SLIDE 8 – Memory Model di OpenMP

OpenMP fornisce un **modello di consistenza della memoria rilassato** (relaxed consistency):
- Consente il riordinamento degli accessi all'interno di un thread a variabili diverse.
- Un thread potrebbe non vedere immediatamente le scritture degli altri thread.
- Un thread potrebbe osservare valori non aggiornati (stale values) a meno che non venga usata la sincronizzazione.
- Registri, cache, riordinamento del compilatore e dell'hardware contribuiscono a questo effetto.

Ogni thread ha una propria **threadprivate memory** a cui gli altri thread non possono accedere.

**Happens-Before** viene stabilito tramite sincronizzazioni (barrier, critical, atomics, locks, task wait, ecc.).

**La direttiva flush:**
`#pragma omp flush [variable list]`
Viene usata per forzare la consistenza tra la vista temporanea della memoria di un thread e la memoria primaria (o tra le viste di piu' thread). Va usata con cautela: puo' far evict di valori dalla cache e i successivi accessi potrebbero ricaricare i dati dalla memoria principale.

Le operazioni di flush sono implicite in tutte le operazioni di sincronizzazione OpenMP (barrier, entrata/uscita da parallel region, uscita da workshare region, ecc.). La flush e' principalmente una primitiva di visibilita' di basso livello e raramente e' necessaria nel codice OpenMP ben strutturato.

---

## SLIDE 9 – Direttive OpenMP

In C/C++ le direttive usano il prefisso `#pragma omp`. I pragma sono direttive del compilatore che abilitano comportamenti non parte del linguaggio standard. Sono attivi solo quando OpenMP e' abilitato (`-fopenmp`). I compilatori che non supportano `#pragma omp` lo ignorano.

**Struttura generale di una direttiva:**
```
prefix directive [clause list]
```

Esempi:
- C/C++:  `#pragma omp parallel num_threads(8)`
- Fortran: `!$omp parallel num_threads(8)`

La maggior parte dei costrutti OpenMP si applica al **blocco strutturato** (structured block) che segue la direttiva. Un blocco strutturato e' un blocco di istruzioni con un unico punto di ingresso e un unico punto di uscita (non e' consentito tornare o saltare all'interno di un blocco parallelo dall'esterno). Se il blocco strutturato non e' esplicitamente delimitato con `{}`, viene considerata la singola istruzione successiva.

---

## SLIDE 10 – "Hello World" con OpenMP (1/3)

```cpp
#include <omp.h>   // necessario solo per usare le routine di libreria
int main() {
    #pragma omp parallel
    {   // <- spawning dei thread (Worker)
        int i = omp_get_thread_num();
        int n = omp_get_num_threads();
        std::printf("Hello from thread %d of %d\n", i, n);
    }   // <- joining dei thread
}
```

- `omp_get_thread_num()`: funzione di libreria che restituisce l'ID del Worker thread corrente (da 0 a n-1).
- `omp_get_num_threads()`: funzione di libreria che restituisce il numero di thread nel team corrente.
- Il flag `-fopenmp` abilita le direttive OpenMP in GCC/Clang.
- La variabile d'ambiente `OMP_NUM_THREADS` imposta il numero di default di thread per le parallel region. Se non e' impostata, il numero di thread e' uguale al numero di core disponibili.

---

## SLIDE 11 – "Hello World" (2/3)

Un blocco strutturato puo' essere anche una singola chiamata a funzione (nell'esempio: una lambda C++).

Il flag `-fopenmp` del compilatore definisce la macro del preprocessore `_OPENMP`. Questo puo' essere utile per includere o escludere codice a tempo di compilazione (es. usare versioni diverse del codice a seconda che OpenMP sia abilitato o meno).

La **clausola `num_threads`** viene usata per impostare il numero di thread da creare per una data regione parallela (sovrascrive il valore di `OMP_NUM_THREADS` per quella specifica regione).

---

## SLIDE 12 – "Hello World" (3/3)

La **clausola `if`** viene valutata: se la sua espressione e' vera, il costrutto parallel viene abilitato con `num_threads` thread; altrimenti la direttiva viene ignorata e il codice esegue sequenzialmente sul thread primario.

Per misurare il tempo, OpenMP fornisce la routine di libreria `omp_get_wtime()`, che restituisce il tempo di clock (wall clock time) in secondi con alta risoluzione. E' portatile e indipendente dal sistema operativo.

---

## SLIDE 13 – Direttiva `parallel` di OpenMP

```
#pragma omp parallel [clause list]
```

Quando un thread raggiunge una direttiva `parallel`:
- Crea un team di thread e diventa il thread primario di quel team (thread con ID 0).
- Ogni thread del team esegue il codice della parallel region (il blocco strutturato della regione).
- Alla fine della parallel region c'e' una **barriera implicita**.
- Esistono costrutti di sincronizzazione aggiuntivi che possono sovrascrivere o affinare la barriera implicita.

**Clausole comuni:**
- `if (expr)`: determina se la direttiva crea thread.
- `num_threads (n)`: numero di thread da creare nel team.
- `private (var list)`: specifica variabili locali a ciascun thread (copia privata non inizializzata).
- `firstprivate (var list)`: simile a private, le variabili sono inizializzate con il valore che avevano prima della direttiva.
- `shared (var list)`: specifica che le variabili sono condivise tra tutti i thread del team. In C/C++, la maggior parte delle variabili visibili da uno scope esterno sono condivise per default; gli indici dei loop `for` sono privati per default.
- `default (shared | none)`: specifica il data scoping di default. Si preferisce `default(none)` per richiedere la specifica esplicita di ogni variabile.
- `reduction (op : var list)`: specifica come combinare le copie per-thread di una variabile in un'unica copia all'uscita della regione.

---

## SLIDE 14 – Costrutti Work-Sharing di OpenMP

All'interno di una parallel region, un **worksharing construct** dice ai thread del team come eseguire istruzioni, blocchi e iterazioni di loop cooperativamente (cioe' in parallelo).

**Quattro direttive di worksharing:**
- **`for`:** i thread eseguono cooperativamente le iterazioni del loop.
- **`sections`:** i thread eseguono cooperativamente blocchi di codice distinti.
- **`single`:** un solo thread esegue il blocco, gli altri aspettano. Barriera implicita alla fine, sopprimibile con `nowait`.
- **`workshare`:** divide l'esecuzione in unita' di lavoro separate (solo Fortran).

**Direttiva `for`:**
```
#pragma omp for [clause list]
```
- Partiziona le iterazioni del loop tra i thread del team.
- Clausole comuni: `private`, `firstprivate`, `lastprivate`, `reduction`, `schedule`, `collapse`, `nowait`, `ordered`.
- Alla fine del `for` c'e' una **barriera implicita**.
- Richiede il cosiddetto **Canonical Loop Form** (forma canonica del loop): variabile di controllo con tipo intero o puntatore, condizione di confronto semplice, incremento/decremento semplice).

---

## SLIDE 15 – Esempio: Parallel e For

**Combinare `parallel` e `for` per evitare la creazione ripetuta dei thread:**

```cpp
#pragma omp parallel
{   // <- spawning dei thread una sola volta
    #pragma omp for
    for (uint64_t i = 0; i < num_entries; i++) {
        x[i] = i;
        y[i] = num_entries - i;
    }
    // <- barriera implicita
    #pragma omp for
    for (uint64_t i = 0; i < num_entries; i++)
        z[i] = x[i] + y[i];
    // <- altra barriera implicita
    #pragma omp for
    for (...) { ... }
}   // <- joining dei thread (barriera finale implicita)
```

**Uso della clausola `nowait`:** quando i loop sono indipendenti, si puo' evitare la barriera implicita tra un loop e il successivo:

```cpp
#pragma omp parallel
{
    #pragma omp for nowait
    for (...) { ... }
    // <- qui non c'e' barriera

    #pragma omp for
    for (...) { ... }
}   // <- barriera finale implicita (non puo' essere rimossa)
```

Con `nowait`, qualsiasi thread puo' iniziare il secondo loop immediatamente senza aspettare che gli altri completino il primo. Questo e' sicuro solo se i due loop sono completamente indipendenti.

---

## SLIDE 16 – Condivisione e Privatizzazione delle Variabili

**Tipi di scope per le variabili:**

- **`shared(x)`:** tutti i thread accedono alla stessa locazione di memoria di x. Molte variabili di scope esterno sono condivise per default (ma non tutte).

- **`private(x)`:** ogni thread ha una propria copia privata di x, non inizializzata. Gli aggiornamenti locali a x vengono scartati all'uscita dalla regione parallela; x mantiene il suo valore originale.

- **`firstprivate(x)`:** come private, ma le copie locali di x sono inizializzate con il valore che x aveva prima dell'inizio della regione parallela. Gli aggiornamenti locali vengono scartati all'uscita.

- **`lastprivate(x)`:** usato principalmente con `for` e `sections`. Ha la stessa semantica di `private(x)`, ma alla fine della regione, x assume il valore della copia thread-locale del thread che ha eseguito l'ultima iterazione del loop o l'ultima section. Utile per recuperare il risultato dell'ultima iterazione.

- **`default(shared)` o `default(none)`:** imposta lo scope di default delle variabili non specificate in altre clausole. Si consiglia `default(none)` per richiedere la specifica esplicita di ogni variabile, riducendo il rischio di errori.

**Esempio:**
```cpp
int x=10, last = -1;
#pragma omp parallel for firstprivate(x) lastprivate(last)
for (int i = 0; i < 4; ++i) {
    x += i;     // modifica la copia privata di x
    last = i;   // privato, ma copiato fuori alla fine
}
// qui x=10, last=3
```

---

## SLIDE 17 – Esempio 1: omp_scope.cpp

Esempio pratico (file `omp_scope.cpp`) che mostra il comportamento delle clausole di scope delle variabili in OpenMP. Permette di verificare sperimentalmente come `private`, `firstprivate`, `lastprivate` e `shared` influenzano i valori delle variabili all'interno e all'esterno della regione parallela.

---

## SLIDE 18 – Esempio 2: omp_scope2.cpp

La variabile `i` e' resa `lastprivate` sul `parallel for`: ogni iterazione ha una copia privata di `i`, e il valore dell'ultima iterazione (lexicamente, cioe' quella con il valore piu' alto dell'indice del loop, qui j==15) viene copiato indietro alla fine. La stampa finale deve mostrare `i == 15`, indipendentemente dalla politica di scheduling.

Questo esempio mostra che `lastprivate` garantisce che il valore della variabile dopo il loop corrisponda a quello che avrebbe avuto nella versione sequenziale (ultima iterazione eseguita).

File: `omp_scope2.cpp`

---

## SLIDE 19 – Parallelismo Annidato (Nested Parallelism)

Il parallelismo annidato (nested parallelism) consente di avere regioni parallele all'interno di altre regioni parallele.

**Abilitazione:**
- Tramite la variabile d'ambiente `OMP_NESTED=true`
- Oppure tramite la chiamata `omp_set_nested(1)`
- Non e' abilitato per default.

**Funzioni utili:**
- `omp_get_num_threads()`: restituisce la dimensione del team corrente (se nessun team e' attivo, restituisce 1).
- `omp_get_thread_num()`: restituisce l'ID nel team corrente.
- `omp_get_max_threads()`: restituisce il numero massimo di thread che possono essere creati.

**Variabili d'ambiente rilevanti:**
- `OMP_MAX_ACTIVE_LEVEL=2`: consente al massimo 2 livelli attivi di parallelismo annidato.
- `OMP_NUM_THREADS=4,2`: richiede 4 thread per il loop esterno e 2 per quello interno.
- `OMP_THREAD_LIMIT=8`: limite massimo al numero totale di thread su tutti i livelli.

Il parallelismo annidato e' raramente usato nella pratica: bisogna prestare attenzione all'**oversubscription** (piu' thread di quanti siano i core fisici disponibili), che puo' peggiorare le prestazioni. Controllarlo con `OMP_THREAD_LIMIT`.

File: `omp_nested.cpp`

---

## SLIDE 20 – Clausola `reduction` per la Direttiva `parallel`

```
#pragma omp parallel reduction (op : variable list)
```

La clausola `reduction` specifica l'operatore binario associativo da usare per combinare le copie locali di una variabile in thread diversi in un'unica copia alla fine del costrutto.

**Operatori di riduzione disponibili:** `+`, `*`, `|`, `^`, `&&`, `||`, `min`, `max`

**Valori identita'** (per interi): 0, 1, 0, 0, 1, 0, INT_MAX, INT_MIN

**Semantica:**
- Per ogni variabile nella lista viene creata una copia privata per ciascun thread.
- Ogni copia viene inizializzata con l'elemento neutro dell'operatore di riduzione (es. 0 per `+`, 1 per `*`).
- Ogni thread esegue la regione parallela sui propri dati.
- Alla fine, l'operatore di riduzione viene applicato all'ultimo valore di ciascuna variabile di riduzione locale e al valore iniziale della variabile prima di entrare nella regione parallela.

**Esempio:**
```cpp
int x=5, y=1;
#pragma omp parallel reduction(*:x) reduction(+:y) num_threads(3)
{   // spawning 3 thread; x impostato a 1 (neutro di *), y a 0 (neutro di +)
    x += 3;
    y += 3;
}
// x = (1+3)^3 * 5 = 4^3 * 5 = 64 * 5 = 320
// y = (3 * 3) + 1 = 10
```

File: `omp_reduction.cpp`, `omp_dotprod.cpp`

---

## SLIDE 21 – Esempio: Stima di Pi (1/2)

**Base matematica:**
La seguente integrale vale pi greco:
`integral da 0 a 1 di 4.0 / (1 + x^2) dx = pi`

E' possibile approssimare l'integrale come somma di N rettangoli in [0,1], dove ogni rettangolo ha larghezza delta_x e altezza F(x_i) calcolata al punto medio dell'intervallo i:
`pi ≈ sum_{i=0}^{N} F(x_i) * delta_x`

Un'altra opzione e' calcolare N passi della seguente serie (di Leibniz):
`pi = 4 * sum_{k=0}^{+inf} (-1)^k / (2k+1)`

---

## SLIDE 22 – Esempio: Stima di Pi (2/2)

**Implementazione OpenMP:**
- La variabile `x` deve essere `private` (ogni thread calcola il suo punto medio).
- La variabile `sum` (variabile di riduzione) viene automaticamente privatizzata dalla clausola `reduction(+:sum)`.

**Scalabilita':** il benchmark su 1 miliardo di iterazioni sul frontend del cluster mostra una scalabilita' quasi lineare fino a molti thread.

**Sfida:** come implementare la stima di pi greco **senza usare la clausola `reduction`? (file `omp_pi-noreduction.cpp`)

Approccio alternativo: usare `#pragma omp atomic` o array privati per thread, poi sommare manualmente i risultati parziali.

File: `omp_pi.cpp`

---

## SLIDE 23 – Mappatura delle Iterazioni ai Thread: Clausola `schedule`

```
#pragma omp parallel for schedule(scheduling_class[, chunksize])
```

La clausola `schedule` abilita diverse politiche di distribuzione delle iterazioni del loop. Corrisponde alle politiche di distribuzione discusse nella lezione sul Workload Balancing.

**Quattro classi di scheduling:**

- **`static`:** il lavoro viene assegnato ai thread staticamente in modo ciclico a tempo di compilazione. Se chunksize non e' specificato, ogni thread riceve `#iterazioni / #threads` iterazioni contigue. Se specificato, lo spazio delle iterazioni viene diviso in blocchi di dimensione chunksize assegnati round-robin. Corrisponde alle distribuzioni block e block-cyclic.

- **`dynamic`:** le iterazioni vengono assegnate dinamicamente a runtime con granularita' di chunksize (default chunksize=1). Quando un thread completa un chunk, ne viene assegnato un altro (se disponibile). Buono per workload sbilanciati, ma con maggiore overhead.

- **`guided`:** le iterazioni vengono assegnate dinamicamente a runtime con una granularita' che si riduce esponenzialmente con ogni pezzo di lavoro inviato, fino a chunksize (il minimo chunksize di default e' 1). Heuristic: `chunk = max(#rimanenti / #threads, chunkmin)`. L'implementazione effettiva dipende dal compilatore. In genere meno overhead del dynamic, ma meno deterministico.

- **`runtime`:** la politica di scheduling dipende dalla variabile d'ambiente `OMP_SCHEDULE`. Es. `OMP_SCHEDULE="dynamic,10" ./myprog`.

- **`auto`:** delega la decisione al compilatore e al sistema runtime.

Lo schedule di default e' implementation-dependent. In GCC e' `static`.

---

## SLIDE 24 – Esempi di Schedule Static

Con p=5 thread e 16 iterazioni (i=0..15):

- **`schedule(static)`** – distribuzione block: ogni thread riceve ceil(16/5) = 4 iterazioni contigue. Th0: 0-3, Th1: 4-7, Th2: 8-11, Th3: 12-14, Th4: 15.

- **`schedule(static,1)`** – distribuzione ciclica con c=1: le iterazioni vengono assegnate in round-robin singolo. Th0: 0, 5, 10, 15; Th1: 1, 6, 11; Th2: 2, 7, 12; Th3: 3, 8, 13; Th4: 4, 9, 14.

- **`schedule(static,2)`** – distribuzione block-cyclic con c=2: blocchi di 2 iterazioni consecutive vengono assegnati round-robin. Th0: 0-1, 10-11; Th1: 2-3, 12-13; Th2: 4-5, 14-15; Th3: 6-7; Th4: 8-9.

Le prime due distribuzioni corrispondono rispettivamente alla block e alla cyclic della lezione sul Workload Balancing; la terza corrisponde alla block-cyclic.

---

## SLIDE 25 – Schedule Dynamic e Guided

**Dynamic e guided:** le iterazioni vengono suddivise in chunk di `chunksize` iterazioni consecutive.

**Guided:** il chunksize e' un limite inferiore (chunkmin). Chunk piu' grandi vengono assegnati all'inizio; man mano che i chunk vengono completati, la dimensione dei nuovi chunk si riduce fino a chunkmin.

Euristica guided: `chunk = max(#iterazioni_rimanenti / #threads, chunkmin)`

Quando un thread finisce di eseguire un chunk, il runtime assegna un nuovo chunk.

**`schedule(dynamic,1):`** assegnazione non predicibile, dinamica, con chunk di dimensione 1.

Logicamente e' un paradigma di computazione **master-worker**: il master invia task ai Worker pronti.

Il dynamic schedule richiede piu' lavoro a runtime (maggiore overhead del static), ma garantisce un migliore bilanciamento del workload se c'e' variabilita' non prevedibile nel lavoro per iterazione.

La dimensione del chunk e' un fattore critico: il valore ottimale dipende dal sistema e dall'applicazione.

**Confronto guided vs dynamic:**
- Guided: meno overhead, ma potenzialmente peggiore bilanciamento del carico rispetto al dynamic puro. La localita' e' peggiore del static.
- Dynamic: maggiore overhead, migliore bilanciamento.

File: `omp_schedule.cpp`

---

## SLIDE 26 – Esempio Guided: Schedule Guidato

**Esempio:** `schedule(guided,8)` con 4 thread e 100 iterazioni.

Possibile esecuzione (non deterministica):
- Th0: max(100/4, 8) = 25 → iterazioni 0-24, rimanenti: 75
- Th1: max(75/4, 8) = 19 → iterazioni 25-43, rimanenti: 56
- Th2: max(56/4, 8) = 14 → iterazioni 44-57, rimanenti: 42
- Th3: max(42/4, 8) = 11 → iterazioni 58-68, rimanenti: 31
- Th3: max(31/4, 8) = 8 → iterazioni 69-76, rimanenti: 23
- Th2: max(23/4, 8) = 8 → iterazioni 77-84, rimanenti: 15
- Th3: max(15/4, 8) = 8 → iterazioni 85-92, rimanenti: 7
- Th1: 7 iterazioni rimanenti → iterazioni 93-99

**Osservazioni:**
- Chunk grandi all'inizio, progressivamente piu' piccoli con un minimo di chunksize.
- Overhead minore del dynamic, ma bilanciamento potenzialmente peggiore.
- Localita' peggiore dello scheduling statico (i thread non accedono sempre alle stesse aree di memoria).

---

## SLIDE 27 – Esempio: All-Pairs Distance Matrix con OpenMP

Risultati ottenuti eseguendo `all_pair.cpp` per il dataset MNIST sul nodo front-end del cluster. Tempo sequenziale: 704s. `OMP_NUM_THREADS=40`.

**Tempi con diverse politiche di scheduling (gcc 12.2.0):**

| OMP_SCHEDULE | Tempo (s) |
|---|---|
| static | 102.55 |
| guided,1 | 56.89 |
| static,8 | 44.20 |
| static,1 | 38.90 |
| dynamic,8 | 35.26 |
| dynamic,1 | 33.88 |

**Osservazioni:**
- Il workload e' irregolare (il costo per riga cresce con l'indice), quindi le politiche dinamiche performano meglio.
- `dynamic,1` e' la migliore (massimo bilanciamento, anche se con piu' overhead di scheduling).
- `static` di default e' la peggiore perche' distribuisce le righe a blocchi contigui, assegnando le righe piu' costose (le ultime) a un singolo thread.
- `static,1` e' sorprendentemente buono: la distribuzione ciclica distribuisce le righe costose uniformemente.

---

## SLIDE 28 – Esempio: Mandelbrot Set con OpenMP

Ogni punto del Mandelbrot Set puo' essere calcolato indipendentemente. Per aumentare la granularita' di computazione, si parallelizza il loop esterno (che calcola tutti i pixel in una riga).

Usando la clausola `schedule(runtime)`, e' possibile sperimentare diverse politiche di scheduling impostando la variabile `OMP_SCHEDULE`, senza ricompilare il programma.

**`#pragma omp critical`:** marca una regione come sezione critica. I thread del team accedono alla regione in mutua esclusione (un thread alla volta). Utile per operazioni non atomiche su variabili condivise (es. aggiornare una struttura dati condivisa).

File: directory `mandelbrot-omp`

---

## SLIDE 29 – Clausola `collapse`

La clausola `collapse` specifica quanti loop in un nest di loop annidati devono essere "collassati" in un unico grande spazio di iterazione, poi diviso secondo la clausola `schedule`.

**Obiettivo principale:** aumentare il conteggio delle iterazioni (numero totale di iterazioni disponibili per la distribuzione), utile quando il loop esterno ha poche iterazioni e si vuole dare piu' lavoro ai thread.

Tutti i loop nel nest devono essere in forma canonica.

**Esempio:**
```cpp
#pragma omp parallel for schedule(static) num_threads(5) collapse(2)
for (int i = 0; i < 4; ++i)
    for (int j = 0; j < 5; ++j)
        do_something(i, j);
```

Senza collapse: 4 iterazioni nel loop esterno. Con un thread per iterazione, 4 thread su 5 lavorano (1 thread e' idle). Con `collapse(2)`: lo spazio collassato ha 4*5 = 20 iterazioni, distribuite tra 5 thread (4 iterazioni ciascuno). Bilanciamento perfetto.

File: `omp_collapse.cpp`

---

## SLIDE 30 – Direttiva Worksharing `sections`

```
#pragma omp sections [clause list] {
    [#pragma omp section
     // blocco strutturato
    ]
}
```

La direttiva `sections` abilita il **parallelismo a task** (task parallelism). E' un work-sharing construct.

**Semantica:**
- Specifica che le section(s) incluse nel blocco strutturato devono essere divise tra i thread del team.
- Ogni section viene eseguita una volta da un thread. Section diverse possono essere eseguite da thread diversi.
- C'e' una **barriera implicita** alla fine di una direttiva `sections`, a meno che non si usi la clausola `nowait`.
- Se usata fuori da una parallel region, il codice viene eseguito serialmente sul thread primario.

**Nota:** in seguito verra' discusso il costrutto `task`, che e' piu' flessibile della `sections`.

Clausole tipiche: `private`, `firstprivate`, `reduction`, `nowait`.
**Non esiste** una clausola `schedule` per le sections.

---

## SLIDE 31 – Uso della Direttiva `sections`

```cpp
#pragma omp parallel num_threads(2)
{
    #pragma omp sections
    {
        #pragma omp section
        { task1(); }

        #pragma omp section
        { task1(); task2(); task3(); }

        #pragma omp section
        { task2(); task3(); }
    }   // <- barriera implicita
}   // <- barriera implicita
```

**Punti chiave:**
- L'ordine di esecuzione dei task non e' noto a priori.
- L'assegnazione dei task ai thread e' non-deterministica: non e' garantito quale thread eseguira' quale section.
- Se il numero di section supera il numero di thread, alcuni thread eseguiranno piu' section.
- Se il numero di thread supera il numero di section, alcuni thread rimarranno idle durante questo costrutto.

---

## SLIDE 32 – Esempio: omp_sections.cpp

Esempio pratico che mostra l'uso della direttiva `sections` con la clausola `nowait`.

La clausola `nowait` alla fine del blocco delle sections significa che alla fine del blocco strutturato non c'e' barriera implicita: i thread che hanno completato la propria section possono procedere senza aspettare gli altri.

File: `omp_sections.cpp`

---

## SLIDE 33 – Esempio: Pipeline con sections

**Esempio di pipeline** implementata con `sections`:
- E' garantito che ogni section viene eseguita esattamente una volta da un thread.
- NON e' garantita la mappatura uno-a-uno tra le 4 section e i 4 thread del team.

Per mantenere un team di dimensione fissa, si puo' disabilitare il dynamic team-size: `OMP_DYNAMIC=false` o `omp_set_dynamic(0)`. Tuttavia, questo non garantisce ancora una mappatura 1-to-1 tra section e thread.

Se si ha bisogno di una mappatura stricata "1 stage = 1 thread" (es. per una pipeline in cui ogni stadio deve avere un thread dedicato), si deve usare una parallel region con un controllo esplicito sull'ID del thread (vedi `omp_pipeline_nosections.cpp`), invece della direttiva `sections`.

File: `omp_pipeline_sections.cpp`, `omp_pipeline_nosections.cpp`

---

## SLIDE 34 – Costrutti di Sincronizzazione OpenMP

**Riepilogo dei principali costrutti di sincronizzazione:**

`#pragma omp barrier`
Tutti i thread del team attivo devono raggiungere questo punto prima di poter procedere. Barriera esplicita.

`#pragma omp single [clause list]`
Marca una parallel region da eseguire da un solo thread (il primo che la raggiunge). Gli altri saltano la regione. Barriera implicita alla fine (come gli altri worksharing constructs).

`#pragma omp master`
Marca un blocco strutturato da eseguire solo dal thread Master (quello con ID 0). Non c'e' barriera implicita alla fine del blocco.

`#pragma omp critical [(nome)]`
Marca il blocco come sezione critica. Tutti i thread eseguono la sezione critica uno alla volta (lock-based). Usare `critical(name)` per creare lock separati (sezioni critiche con nome diverso non si escludono a vicenda).

`#pragma omp ordered`
Nei loop con dipendenze, garantisce che le dipendenze portate dal loop non causino data race. Il blocco strutturato (all'interno di un loop) deve essere eseguito nell'ordine sequenziale.

`#pragma omp atomic`
Solo un thread alla volta aggiorna una variabile condivisa. Piu' efficiente di `critical` per operazioni semplici (es. increment, add, ecc.).

---

## SLIDE 35 – Esempio di Uso dei Costrutti di Sincronizzazione

```cpp
#pragma omp parallel
{
    work_par();        // tutti i thread
    // eseguito solo dal master thread (no barriera implicita)
    #pragma omp master
    work_seq();

    // mutua esclusione (con barriera implicita)
    #pragma omp critical
    work_critical();

    // barriera esplicita
    #pragma omp barrier

    work_par();        // tutti i thread
}   // <- barriera implicita finale
```

**Flusso di esecuzione con 3 thread (primary, Th1, Th2):**
- I tre thread eseguono `work_par()` in parallelo.
- Solo il thread primario esegue `work_seq()`, gli altri proseguono.
- I tre thread eseguono `work_critical()` in mutua esclusione, uno alla volta.
- Alla barriera esplicita, tutti i thread si sincronizzano.
- I tre thread eseguono di nuovo `work_par()` in parallelo.
- Barriera implicita finale al termine della parallel region.

---

## SLIDE 36 – Esempio: Scan in OpenMP

**Algoritmo di scan parallelo in OpenMP (4 thread, op=+):**

1. Il vettore di input viene partizionato in blocchi contigui, uno per thread.
2. Ogni thread calcola la scan locale sul proprio blocco.
3. `block_sum[tid]` memorizza il totale del blocco tid.
4. Un thread calcola il prefix sum esclusivo di `block_sum`.
5. Ogni thread aggiunge l'offset dei blocchi precedenti ai propri risultati locali.

**Esempio con vettore x = {-2, 4, 2, -1, -1, 1, -3, 2, 1, 4, 1, 5}:**
- Dopo scan locale: y = {-2, 2, 4, -1, -2, -1, -3, -1, 0, 4, 5, 10}
- block_sum = {4, -1, 0, 10}
- Prefix esclusivo di block_sum: {0, 4, 3, 3}
- Risultato finale: y = {-2, 2, 4, 3, 2, 3, 0, 2, 3, 7, 8, 13}

**Nota:** OpenMP 5.x fornisce supporto diretto per operazioni di scan inclusive ed esclusive tramite la clausola `scan` e le clausole `inclusive`/`exclusive` nella riduzione.

File: `omp_scan.cpp`

---

## SLIDE 37 – Thread Affinity in OpenMP

**Riepilogo dei concetti di Thread Affinity:**
- La thread affinity (o pinning o binding) controlla come i thread vengono mappati alle risorse hardware (core e socket della CPU).
- Mantenere un thread su un core specifico aiuta a mantenere la localita' della cache e a ridurre la latenza di memoria, particolarmente su architetture NUMA, e minimizza l'overhead dei context switch.
- L'affinity e' particolarmente vantaggiosa per workload memory-bound e irregolari.

**First Touch Allocation Policy:**
Prestare attenzione alla politica di first touch: gli elementi di un array vengono allocati nella memoria del nodo NUMA contenente il core che esegue il thread che inizializza quella partizione. Se un thread A inizializza i dati e un thread B li usa (su un nodo NUMA diverso), si generano accessi a memoria remota. La soluzione e' inizializzare i dati con gli stessi thread che li useranno nel calcolo.

**Gestione dell'Affinity in OpenMP:**
- `OMP_PROC_BIND`: controlla se i thread possono migrare tra i core.
  - `false`: il runtime puo' migrare i thread.
  - `true`: lascia la decisione al runtime.
  - `close`: i thread figli vengono mantenuti vicini ai thread padre (buono per localita' della cache).
  - `spread`: i thread si distribuiscono tra i "places" per massimizzare la distanza (buono per banda di memoria su sistemi NUMA).
  - `master`: i thread figli girano sugli stessi core del master.
- `OMP_PLACES`: definisce una lista portatile di "places" (es. threads, cores, sockets) dove i thread possono essere eseguiti.

---

## SLIDE 38 – Esempi di Thread Affinity in OpenMP

**Definizione di OMP_PLACES:**
- `OMP_PLACES="cores"`: definisce un place per ogni core fisico.
- `OMP_PLACES="threads"`: definisce un place per ogni hardware thread (core logico/SMT).
- `OMP_PLACES="sockets"`: definisce un place per ogni socket.

**Combinazioni tipiche:**

- `OMP_PROC_BIND="close" OMP_PLACES="cores"`: impacchetta i thread su core vicini, riempiendo prima un socket poi il successivo. Migliora la localita' della cache (i thread vicini condividono le cache L2/L3).

- `OMP_PROC_BIND="spread" OMP_PLACES="cores"`: distribuisce i thread tra core e socket per massimizzare la distanza. Migliora la banda NUMA e riduce la contention della cache (utile per workload memory-bound su sistemi multi-socket).

**Utility:**
- `OMP_DISPLAY_ENV="true"`: mostra le impostazioni correnti delle variabili d'ambiente OpenMP all'avvio del programma (utile per il debug della configurazione).

**Per-region binding:**
E' possibile impostare il binding per singola parallel region:
`#pragma omp parallel proc_bind(close)`

**Esempi di utilizzo:**
- `OMP_PROC_BIND=close OMP_PLACES="cores" ./omp_affinity`
- `OMP_PLACES="{0:8:1},{8:8:1}" ./omp_affinity` — definisce due place personalizzati: le CPU 0-7 e le CPU 8-15.

File: `omp_affinity.cpp`
