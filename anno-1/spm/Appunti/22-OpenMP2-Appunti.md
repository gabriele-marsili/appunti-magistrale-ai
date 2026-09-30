# SPM – Lezione 22: Parallel Programming with OpenMP – Parte 2
## Appunti divisi per slide

---

## SLIDE 1 – Titolo

**Parallel Programming with OpenMP – Part 2**
Anno accademico 2025-2026 – Prof. Massimo Torquati

---

## SLIDE 2 – Outline

Gli obiettivi della lezione sono:

- Comprendere il modello di tasking di OpenMP
- Imparare a creare, sincronizzare e orchestrare i task
- Usare le clausole `depend` e `taskloop` per esprimere parallelismo a pipeline e parallelismo irregolare

---

## SLIDE 3 – OpenMP Tasks: Motivazioni

I loop sono la principale fonte di parallelismo, ma non tutti i programmi hanno loop facilmente parallelizzabili:

- Loop in cui il numero di iterazioni non e' noto in anticipo
- Loop contenenti dipendenze complesse (es. algoritmi LU, Cholesky)
- Algoritmi Divide and Conquer (es. quicksort, merge-sort) e computazioni di data streaming (pattern producer-consumer) sono difficili da parallelizzare con parallel loop o sections

**Perche' i task sono piu' flessibili delle sections:**
- Le `sections` sono definite staticamente nel codice sorgente
- I `task` possono essere creati dinamicamente a runtime

Da OpenMP 4 e' possibile specificare clausole `depend(in/out/inout)` sui task per orchestrare le dipendenze tra task (Task Dependency Graph, TDG).

Il tasking e' stato introdotto come funzionalita' principale in OpenMP 3.0.

---

## SLIDE 4 – OpenMP Tasks: Concetti Base

In OpenMP, un **task** e' un'unita' di lavoro indipendente creata all'interno di una parallel region, che puo' essere eseguita immediatamente oppure in un momento successivo, potenzialmente da un thread diverso.

I task differiti vivono in un **task pool** gestito dal runtime di OpenMP.

**Ciclo di vita di un task:**
- `created` (creato) → `running` (in esecuzione) → `completed` (completato)
- Un task puo' anche essere `deferred` (differito, nel pool) o `suspended` (sospeso a un scheduling point)

**Lo scheduling dei task avviene ai task scheduling points**, ma le decisioni di scheduling del runtime possono essere influenzate da:
- Dipendenze tra task (clausola `depend`)
- Priorita' (clausola `priority`)

**Un task OpenMP e' composto da:**
- Il codice da eseguire
- Il suo data environment (variabili condivise e private)
- Informazioni di controllo relative al task, gestite dal runtime

---

## SLIDE 5 – Task Scheduling Points

I **task scheduling points** sono punti nel programma in cui il runtime OpenMP puo' pianificare l'esecuzione dei task.

A un task scheduling point, un thread del team puo' sospendere l'esecuzione del task corrente e iniziare ad eseguire un altro task.

I thread del team prelevano un task dal task pool quando raggiungono uno scheduling point.

**In sintesi, uno scheduling point puo' verificarsi:**
- Quando si crea un task esplicito (`#pragma omp task`)
- Dopo aver completato il blocco strutturato di un task
- Durante la sincronizzazione (barriere esplicite o implicite)
- Quando si fa offloading a un dispositivo target

---

## SLIDE 6 – Task Impliciti ed Espliciti

**Task impliciti:**
- Creati automaticamente all'inizio di una parallel region, uno per ogni thread del team.
- Il task iniziale esiste sul thread primario prima di qualsiasi parallel region.
- Vengono eseguiti immediatamente sul thread proprietario e agiscono come parent dei task creati al loro interno.
- Alle barriere (esplicite o implicite), ogni task implicito attende il completamento dei propri task figli.

**Task espliciti:**
- Creati esplicitamente con `#pragma omp task` all'interno di un task in esecuzione.
- Se molti thread raggiungono il codice contenente la direttiva, vengono creati molti task.
- Possono essere eseguiti da qualsiasi thread del team, senza un ordine imposto dalla posizione nel sorgente.
- Le clausole `depend(in/out/inout)` possono essere usate per ordinare i task tramite dipendenze sui dati.
- Direttive di sincronizzazione specifiche: `taskwait` (aspetta i figli diretti) e `taskgroup` (aspetta tutti i discendenti).

---

## SLIDE 7 – Direttiva OpenMP `task`

```
#pragma omp task [clause list]
```

**Alcune clausole della `[clause list]`:**

- `if (expr)`: se l'espressione e' false, la regione viene eseguita immediatamente come included task (senza essere deferita).
- `final (expr)`: se true, il task viene marcato come final. I task creati all'interno di un final task diventano included tasks (eseguiti inline nel contesto del final task).
- `untied`: nessuna restrizione di scheduling per il task. Il task puo' essere sospeso e ripreso su un thread diverso. Per default, un task e' **tied** (legato) al primo thread che lo esegue.
- `private (var list)`: ogni task ottiene la propria copia privata non inizializzata.
- `firstprivate (var list)`: ogni task ottiene la propria copia privata inizializzata con il valore nel contesto generante.
- `shared (var list)`: specifica che le variabili sono condivise con il task parent.
- `default (shared | none)`: specifica di default per lo scoping dei dati.
- `depend(kind: var list)`: specifica dipendenze tra task usando locazioni di memoria. Il kind puo' essere `in` (legge), `out` (scrive), o `inout` (legge e scrive).

---

## SLIDE 8 – Esempio "Hello Task" (1/2)

**Esempio base:**
```cpp
#pragma omp parallel num_threads(2)
{
    for (int i = 0; i < 2; i++)
        #pragma omp task
        { printf("Hello from task, thread %d\n", omp_get_thread_num()); }
}
```

In questo esempio:
- La parallel region avvia 2 thread; ogni thread esegue il proprio task implicito.
- All'interno del task implicito, il loop ha 2 iterazioni: ogni iterazione crea un task esplicito.
- In totale vengono creati **4 task** eseguiti dal team (2 thread x 2 iterazioni = 4 task).
- Alla fine della parallel region c'e' una barriera: tutti i 4 task devono finire prima dell'uscita.

**Problema:** forse non vogliamo 4 task, ma esattamente 2.

**Come creare esattamente 2 task, uno per ciascun thread del team?**
→ Soluzione nella slide successiva.

---

## SLIDE 9 – Esempio "Hello Task" Revisitato (2/2)

Per garantire che ogni task venga generato **una sola volta**, la creazione dei task deve essere racchiusa in un costrutto `single`:

```cpp
#pragma omp parallel num_threads(2)
{
    #pragma omp single nowait
    {
        for (int i = 0; i < 2; i++)
            #pragma omp task
            { printf("Hello from task %d\n", i); }
    }
    // Gli altri thread iniziano subito a eseguire i task
}
```

- **Un solo thread** del team esegue il blocco `single` e crea i task.
- Gli **altri thread** iniziano immediatamente a eseguire i task disponibili nel pool.
- Di solito `single` viene usato con `nowait` per evitare una barriera implicita aggiuntiva quando non e' necessaria (altrimenti il thread che ha eseguito il `single` aspetterebbe gli altri prima di procedere a eseguire task).

---

## SLIDE 10 – Modello di Esecuzione dei Task OpenMP

Quando un thread del team incontra una direttiva `task`, puo' scegliere di eseguire il task immediatamente oppure differirne l'esecuzione.

Se l'esecuzione del task viene differita, il task viene inserito in una task queue associata alla parallel region corrente.

Tutti i thread del team preleveranno task dal task pool finche' il pool non e' vuoto.

**Il codice associato al costrutto `task` viene eseguito una sola volta.**

**Task tied (legati) – comportamento di default:**
- Per default, i task sono legati al thread che li avvia.
- Possono essere sospesi solo agli scheduling points.
- Devono riprendere sullo stesso thread (quello a cui sono legati).

**Task untied (non legati):**
```
#pragma omp task untied
```
- Un task untied puo' essere rischedulato: puo' iniziare su un thread, essere sospeso, e riprendere su un thread diverso del team.
- Ha meno restrizioni di scheduling, il che puo' migliorare l'utilizzazione dei thread.

---

## SLIDE 11 – Esempio Completo con Task

```cpp
#pragma omp parallel
{
    #pragma omp task
    taskF();              // un task per ogni thread nel team
    
    #pragma omp barrier   // tutti i task taskF() sincronizzati qui
    
    #pragma omp single nowait
    {
        #pragma omp task
        taskH();          // creato una sola volta
        #pragma omp task
        taskG();          // creato una sola volta
    }   // <- nessuna barriera qui (nowait)
}   // <- barriera implicita finale
```

**Analisi:**
- Il task `taskF()` viene creato da **ogni thread** nella parallel region: con p thread si ottengono p task `taskF()`, uno per thread. Tutti sono tied al rispettivo thread.
- Tutti i task `taskF()` si sincronizzano alla barriera esplicita.
- Un solo thread crea un'istanza di `taskH()` e un'istanza di `taskG()`. Questi task verranno eseguiti da qualche thread del team in ordine non determinato.
- Tutti i task devono essere completati prima che la barriera implicita alla fine della regione possa essere attraversata.

---

## SLIDE 12 – Data Scoping per i Task

Lo scoping dei dati per i task e' delicato se non viene specificato esplicitamente.

**Regola generale:**
- Le variabili del contesto racchiudente sono spesso **firstprivate** nei task, a meno che non siano gia' condivise nella regione racchiudente.
- Questo e' importante perche' l'esecuzione dei task puo' essere differita: le variabili originali potrebbero non essere piu' valide quando il task viene eseguito.

**Esempio problematico:**
```cpp
int x = 1, y = 2;
#pragma omp parallel private(y)
{
    int z = 2;
    #pragma omp task
    {
        int w = 3;
        // x e' shared, y e z diventano firstprivate, w e' private
        // ATTENZIONE: y non e' inizializzata!
        F(x, y, z, w);
    }
}
```

**Variante sicura (preferita):**
```cpp
#pragma omp parallel firstprivate(y) shared(x)
{
    #pragma omp task firstprivate(y) shared(x)
    { ... }
}
```

**Regola pratica:** preferire sempre clausole `shared(...)` e `firstprivate(...)` esplicite per evitare comportamenti inattesi dovuti alle regole di default.

---

## SLIDE 13 – Attesa per il Completamento dei Task

**Comportamento della barriera:**
Una barriera tra thread aspetta che tutti i thread arrivino, e ogni thread aspetta anche il completamento dei propri task figli. Questo vale anche per le barriere implicite alla fine di una parallel region.

Tuttavia, poiche' i task figli vengono eseguiti separatamente dal task generante, e' possibile che un task figlio venga eseguito dopo che il task generante ha terminato.

**`#pragma omp taskwait`**
- Aspetta il completamento dei task figli diretti definiti nel task corrente.
- NON aspetta i discendenti (nipoti, pronipoti, ecc.).
- Sospende il task parent finche' tutti i suoi task figli diretti hanno finito.

**`#pragma omp taskgroup`**
- Definisce una regione in cui qualsiasi task creato diventa parte di quel gruppo.
- Alla fine della taskgroup region c'e' una barriera implicita.
- Aspetta **tutti** i task generati all'interno del blocco strutturato, inclusi i task annidati (discendenti).

---

## SLIDE 14 – taskwait vs taskgroup

**Differenza chiave:**
- `taskwait`: il task corrente aspetta tutti i suoi **figli diretti** creati fino a quel momento. Non aspetta i "nipoti".
- `taskgroup`: aspetta tutti i task creati all'interno del blocco, **inclusi i loro discendenti**. I task creati fuori dal blocco non vengono aspettati.

**Esempio con taskwait:**
```cpp
#pragma omp parallel
#pragma omp single nowait
{
    #pragma omp task
    background_work();

    for (auto x: V) {
        #pragma omp task firstprivate(x)
        compute1(x);
        // taskwait aspetta TUTTI i figli diretti creati finora,
        // incluso il task background_work
        #pragma omp taskwait
        compute2(x);
    }
}
```

**Esempio con taskgroup:**
```cpp
#pragma omp parallel
#pragma omp single nowait
{
    #pragma omp task
    background_work();

    for (auto x: V) {
        #pragma omp taskgroup
        {
            #pragma omp task firstprivate(x)
            compute1(x);
        }   // aspetta TUTTI i task creati nel blocco, inclusi i discendenti
        compute2(x);
    }
}   // solo qui il task background_work deve essere completato
```

---

## SLIDE 15 – Clausole `final` e `if`

E' possibile controllare la generazione dei task con le clausole `final` e `if`. Le due clausole sono simili ma con effetti diversi.

**`if(cond)`:**
- Se `cond` e' false, la regione viene eseguita **immediatamente** dal thread corrente come included task. Nessun task differito viene creato.
- Il task "incluso" viene eseguito inline nel contesto del task chiamante.

**`final(cond)`:**
- Il task viene creato e marcato come final se la condizione e' vera.
- I task discendenti (creati all'interno del final task) diventano **included tasks** e vengono eseguiti inline nel contesto del final task.

```cpp
#pragma omp task if(false)
{
    taskA();    // eseguito immediatamente dal thread corrente
    #pragma omp task
    taskB();    // task normale, puo' essere deferito
}

#pragma omp task final(true)
{
    taskA();    // il nuovo task e' marcato come final
    #pragma omp task
    taskB();    // diventa un included task, eseguito nel contesto del final task
}
```

**Impatto sulle prestazioni:** il numero di task creati e' diverso nei due casi, e questo puo' avere un impatto significativo sulle prestazioni (overhead di creazione e scheduling dei task).

File: `omp_if_vs_final.cpp`, `omp_if_vs_final2.cpp`

---

## SLIDE 16 – Esempio: Fibonacci con Task

**Problema:** calcolare l'n-esimo numero di Fibonacci usando l'algoritmo esponenziale.

Il task e' la funzione `fib(n)`:

```cpp
int fib(int n) {
    if (n < 2) return n;
    int n1, n2;
    #pragma omp task shared(n1)
    n1 = fib(n-1);          // le 8 righe
    #pragma omp task shared(n2)
    n2 = fib(n-2);          // devono avere shared!
    #pragma omp taskwait    // attende entrambi i figli
    return n1 + n2;
}
```

**Punti chiave:**
- `n1` e `n2` devono essere `shared`, altrimenti il default sarebbe `firstprivate` e il task avrebbe una copia locale non modificabile dal thread genitore.
- Il `taskwait` sospende il task parent finche' entrambi i task figli hanno completato. Senza taskwait, `n1` e `n2` andrebbero persi.
- Per limitare la ricorsione e ridurre l'overhead di creazione dei task, si usa un **cutoff**: sotto una certa soglia di n, si passa al calcolo seriale invece di continuare a creare task.

File: `omp_fibo.cpp`, `omp_fibo2.cpp`

---

## SLIDE 17 – Task Scheduling

**Punti di scheduling dei task definiti da OpenMP:**
- Quando viene creato un task (`#pragma omp task`)
- Quando si incontra `taskwait` o `taskyield`
- Alle barriere esplicite o implicite
- Quando un task completa l'esecuzione
- Quando si esce da una regione `taskgroup`

**Task scheduling** si riferisce al meccanismo con cui il runtime OpenMP decide quali task eseguire e quando eseguirli sui thread disponibili.

**Clausole che influenzano il comportamento di scheduling:**
- `if`: decide se un costrutto deve essere eseguito come task o inline
- `final`: marca un task come non-deferrable
- `priority`: influenza l'ordine di scheduling (task con priorita' piu' alta vengono preferiti)
- `untied`: consente ai task di essere ripresi su un thread diverso

**Task tied:**
- Solo il thread a cui il task e' legato puo' eseguirlo.
- Un task puo' essere sospeso solo agli scheduling points specifici.
- Se un task non e' sospeso a una barriera, il thread che lo esegue puo' passare solo a un discendente di qualsiasi task tied al thread.

**Task untied:**
- Hanno meno restrizioni di scheduling.
- Dopo la sospensione agli scheduling points, possono riprendere su un thread diverso.

---

## SLIDE 18 – Generazione di Task da un Loop

Un approccio comune per generare task da un loop e':

```cpp
#pragma omp parallel
{
    #pragma omp single nowait
    {
        for (int i = 0; i < NTASKS; ++i)
            #pragma omp task
            { processTask(...); }
    }
}
```

**Problema:** se `NTASKS` e' molto grande, l'implementazione puo' smettere di generare nuovi task e portare tutti i thread ad eseguire i task gia' generati. Se il thread che genera i task sta eseguendo un task lungo, gli altri thread potrebbero non avere nulla da fare.

**Prima soluzione:** rendere la generazione dei task un untied task, cosi' qualsiasi thread e' eleggibile a riprendere il task generante il loop:
```cpp
#pragma omp single
{
    #pragma omp task untied
    for (int i = 0; i < NTASKS; ++i)
        #pragma omp task
        { ... }
}
```

**Limitazione:** questa soluzione non e' abbastanza flessibile. La soluzione migliore e' usare `taskloop`.

---

## SLIDE 19 – Taskloop

```
#pragma omp taskloop [clause list]
```

Il costrutto `taskloop` e' progettato per parallelizzare loop usando i task.

**Caratteristiche principali:**
- Genera automaticamente task dalle iterazioni del loop, abilitando lo scheduling dinamico.
- Utile quando e' necessario lo scheduling dinamico o il conteggio delle iterazioni non e' predicibile.
- Decompone il loop in chunk e crea un task per ogni chunk.
- L'overhead rispetto a `#pragma omp parallel for` e' generalmente maggiore, a causa della creazione dei task.
- Utile per integrare loop in un DAG di task piu' ampio.

**Clausole principali:**
- `grainsize(n)`: i chunk hanno almeno `n` iterazioni.
- `num_tasks(k)`: crea `k` chunk, ognuno con almeno un'iterazione.
- Le due clausole `grainsize` e `num_tasks` sono mutualmente esclusive.
- Se nessuna delle due e' specificata, il numero di chunk e iterazioni per chunk dipende dall'implementazione.

**Comportamento di default:**
Il `taskloop` crea un task esplicito per ogni chunk di iterazioni. Per default si comporta come se fosse racchiuso in un `taskgroup`, quindi c'e' un'attesa implicita alla fine del loop finche' tutti quei task (e i loro discendenti) completano.

E' possibile usare la clausola `nogroup` per rimuovere l'attesa implicita.

File: `omp_taskloop.cpp`, `omp_taskloop_nogroup.cpp`

---

## SLIDE 20 – Task Reduction

In un `taskgroup` e' possibile dichiarare una variabile di riduzione con la clausola `task_reduction(op: var)`.

**Semantica:**
- Ogni task (o taskloop) che contribuisce alla riduzione deve usare `in_reduction(op: var)` in modo che il suo valore parziale venga combinato nell'oggetto di riduzione.
- La variabile ridotta deve essere `shared` nei task contribuenti.
- Il valore finale e' disponibile quando il taskgroup termina.
- La variabile deve essere inizializzata all'elemento neutro dell'operazione prima del gruppo.

**Da OpenMP 5.0:**
E' possibile scrivere direttamente `reduction(+: var)` sulla direttiva `task` e `taskloop`, con piu' opzioni disponibili.

File: `omp_task_reduction.cpp`, `omp_dotprod_taskloop.cpp`

---

## SLIDE 21 – Pointer-Chasing Loop

**Problema:** parallelizzare una visita di una lista concatenata (linked list), dove il numero di elementi non e' noto in anticipo e il loop non e' in forma canonica.

Non e' possibile usare un `parallel for` worksharing perche' il numero di elementi potrebbe non essere noto in anticipo e il loop non rispetta la forma canonica.

**Soluzione con task:**

```cpp
#pragma omp parallel
#pragma omp single nowait
{
    Node* cur = head;
    while (cur) {
        Node* start = cur;
        // avanza fino a tasksize-1 passi, fermandosi alla fine della lista
        for (int c = 1; c < tasksize && cur->next; ++c)
            cur = cur->next;
        Node* next = cur->next;
        #pragma omp task firstprivate(start, next)
        for (Node* p = start; p != next; p = p->next)
            do_something(p);
        cur = next;
    }
}
```

**Tecnica:** il loop genera task di granularita' `tasksize`, dove ogni task elabora un segmento contiguo della lista. Il puntatore `start` e `next` sono `firstprivate` per evitare race condition.

File: `omp_pchasing.cpp`

---

## SLIDE 22 – Finding Primes con Task

**Due versioni**, entrambe usano task con granularita' `tasksize`:

**Prima versione:**
- Usa un buffer per task (ogni task ha il proprio buffer per i numeri primi trovati).
- Pro: output in ordine deterministico senza sort finale.
- Contro: molti piccoli buffer se il numero di task e' grande.

**Seconda versione:**
- Usa un buffer per thread (un buffer per thread anziche' per task), un `taskloop` e una riduzione.
- Pro: meno buffer (uno solo per thread).
- Contro: richiede un sort finale se i numeri primi devono essere stampati in ordine.

Questo esempio illustra il trade-off tra:
- Overhead di allocazione/gestione della memoria (buffer per task vs per thread)
- Necessita' di riordinamento dei risultati

File: `omp_primes_task1.cpp`, `omp_primes_task2.cpp`

---

## SLIDE 23 – Task Dependencies

Le **dipendenze tra task** (task dependencies) consentono di definire sincronizzazioni a grana fine per l'ordine di esecuzione dei task.

Offrono un controllo piu' preciso rispetto a `taskwait`, che aspetta tutti i figli diretti.

**La clausola `depend`** su un task specifica le dipendenze usando locazioni di memoria (non mutua esclusione):

```
#pragma omp task depend(dependency-type: list)
```

Un task dipendente non puo' essere schedulato finche' tutti i task precedenti (sibling) con dipendenze conflittuali sullo stesso storage non hanno completato.

**Scope delle dipendenze:**
- Le dipendenze ordinano i task sibling creati dallo stesso team.
- Parallel region distinte (anche annidate) creano team diversi e non condividono il task graph, quindi le dipendenze tra team diversi non funzionano.

**Tipi di dipendenze in OpenMP 4.5:**
- `in`: il task legge le locazioni di storage elencate.
- `out`: il task scrive le locazioni di storage elencate.
- `inout`: il task legge e scrive le locazioni di storage elencate.

**Cosa puo' comparire nella depend list:** lvalue di storage o sezioni di array (es. `A[0:8]`).

Versioni piu' recenti di OpenMP hanno aggiunto ulteriori tipi di dipendenza e funzionalita'.

---

## SLIDE 24 – Esempio 1: Dipendenza RAW (Read-After-Write)

**Scenario:** per ogni indice `i`:
- Un task **produce** `x[i]` (depend out su x[i])
- Un task **consuma** `x[i]` (depend in su x[i])
- Un task **indipendente** stampa solo l'indice

**Garanzie:**
- Il task "produce x[i]" appare sempre prima del "consuma x[i]" grazie al matching `depend(out: x[i])` / `depend(in: x[i])`.
- Il task indipendente (stampa indice) puo' stampare prima, dopo, o in mezzo ai task dipendenti, non avendo dipendenze.

Questa e' la classica dipendenza **RAW (Read-After-Write)**: il lettore deve aspettare che lo scrittore abbia completato.

File: `omp_depend1.cpp`

---

## SLIDE 25 – Esempio 2: Dipendenze di Input Multiple

**Scenario:** piu' dipendenze di input da un'unica dipendenza di output.

Un task "produttore" ha `depend(out: x)`. Piu' task "consumatori" hanno `depend(in: x)`.

**Comportamento:**
- I task consumatori non possono partire finche' il produttore non ha completato.
- I task consumatori (tutti con `depend(in: x)`) possono eseguire in qualsiasi ordine tra loro, anche in parallelo (piu' lettori concorrenti sulla stessa locazione sono ammessi).

File: `omp_depend2.cpp`

---

## SLIDE 26 – Esempio 3: Dipendenze Anti e WAW

**Dipendenza anti (WAR – Write-After-Read):**
- Un task successivo vuole scrivere una locazione che un task precedente sta ancora leggendo.
- Lo scrittore deve aspettare che la lettura sia completata.
- OpenMP esprime questo con `depend(in: ...)` sul lettore e `depend(out: ...)` sullo scrittore.

**Dipendenza di output (WAW – Write-After-Write):**
- Due scritture sulla stessa locazione devono essere ordinate.
- Entrambi i task usano `depend(out: ...)` sullo stesso storage.
- Il secondo task aspetta che il primo abbia completato la scrittura.

Questi tre tipi di dipendenze (RAW, WAR, WAW) corrispondono esattamente alle stesse dipendenze analizzate nella teoria del compilatore per l'analisi delle dipendenze tra istruzioni.

File: `omp_depend3.cpp`

---

## SLIDE 27 – Esempio 4: Array Sections

La clausola `depend` supporta le **array sections** per specificare dipendenze su porzioni di array:

```
#pragma omp task depend(in: A[4:11])
```

Questo significa che il task dipende dagli elementi `A[4], A[5], ..., A[14]` (11 elementi a partire da indice 4).

**Sintassi:** `base[lower : length]`
- `base`: nome dell'array
- `lower`: indice del primo elemento
- `length`: numero di elementi (non il limite superiore!)

Le sezioni sono definite per numero di elementi, non per byte. Questo permette di esprimere dipendenze fine-grained su parti di array, utile per algoritmi su matrici a blocchi.

File: `omp_depend4.cpp`

---

## SLIDE 28 – Attesa con `taskyield`

```
#pragma omp taskyield
```

`taskyield` crea uno **scheduling point**. Il runtime puo' sospendere il task corrente e schedulare un task diverso pronto dallo stesso team, per poi riprendere successivamente il task che ha ceduto (yield).

**Comportamento:**
- Il runtime e' autorizzato a ignorare un hint di yield (la maggior parte delle implementazioni non lo ignora).
- Utile in **polling loop** all'interno di task (es. attesa attiva su un flag), e in task a lunga esecuzione per permettere ad altri task pronti di fare progressi.

**Interazione con tied/untied:**
- Con task tied: il task che cede (yield) riprendera' piu' tardi sullo stesso thread.
- Con task untied: il task che cede puo' riprendere su un thread diverso.

`taskyield` e' uno strumento per la cooperazione volontaria: invece di bloccarsi, un task cede volontariamente il processore per permettere ad altri task di avanzare.

---

## SLIDE 29 – Pipeline con I/O Sovrapposto

**Pipeline logica a 3 stadi:** read → compute → write

**Prima versione (pure map su file blocks):**
- Pipeline con task: tutti i blocchi si sovrappongono (read, compute, write eseguiti in parallelo su blocchi diversi).
- La fase write puo' eseguire in parallelo con read e compute su blocchi diversi.
- Possibile estensione: unire read, compute e write in un singolo task (esercizio).

**Seconda versione (dimensione output diversa dall'input):**
- La dimensione del blocco di output non e' uguale a quella del blocco di input, quindi le scritture devono essere eseguite in ordine.
- Pipeline con task per le fasi read e compute.
- Exclusive scan per calcolare l'offset di ciascun blocco di output.
- Parallel for per scrivere i blocchi in parallelo (una volta noti gli offset).

**Nota importante:** le scritture parallele su un singolo file potrebbero non velocizzare le cose. Il filesystem puo' serializzare il lavoro a livello hardware o software. **Bisogna sempre testare e misurare sul sistema target.**

File: `omp_pipe_IO.cpp`, `omp_pipe_IO_varout.cpp`

---

## SLIDE 30 – Algoritmo di Strassen per GEMM

**Problema:** moltiplicare due matrici N x N.

**Algoritmo di Strassen:**
- Divide le matrici in 4 blocchi di dimensione N/2 x N/2.
- Esegue 7 moltiplicazioni di blocchi invece delle 8 dell'algoritmo classico.
- Poi ricombina con addizioni e sottrazioni.
- Costo asintotico ridotto: O(N^2.807) invece di O(N^3).

**Parallelizzazione con task:**
- Ogni macro-istruzione (es. addizione/sottrazione di matrice) puo' essere calcolata usando routine ottimizzate di algebra lineare (es. librerie PLASMA, LAPACK, Armadillo, ...).
- Le dipendenze tra le operazioni formano un DAG di task naturale.
- La clausola `depend` permette di esprimere esattamente queste dipendenze tra i 7 prodotti di blocchi e le operazioni di ricombinazione.

File: `omp_strassen.cpp`

---

## SLIDE 31 – Block-Cholesky Factorization (Left-looking)

**Problema:** fattorizzare una matrice hermitiana definita positiva A di dimensione N x N in L tale che A = L^H * L.

**Struttura a blocchi:**
- A viene partizionata in nb x nb blocchi di dimensione bs x bs, dove N = nb * bs.
- L viene memorizzata in place in A.

**Algoritmo (Left-looking):**
```
for (k = 0; k < nb; k++) {
    // Aggiorna il blocco diagonale corrente A[k][k]
    for (i = 0; i < k; i++)
        F_CHERK(A[k][k], A[k][i], A[k][k]);  // A[k][k] -= A[k][i] * A[k][i]^H
    // Fattorizza il blocco diagonale
    F_CPOTF2(A[k][k], A[k][k]);              // A[k][k] = chol(A[k][k])
    // Aggiorna i blocchi trailing A[j][k] per j = k+1, ..., nb-1
    for (j = k+1; j < nb; j++) {
        for (i = 0; i < k; i++)
            F_CGEMM(A[k][i], A[j][i], A[j][k], A[j][k]);  // A[j][k] -= A[j][i] * A[k][i]^H
        F_CTRSM(A[k][k], A[j][k], A[j][k]);  // A[j][k] = A[j][k] * (A[k][k]^H)^-1
    }
}
```

Ogni operazione (CHERK, CPOTF2, CGEMM, CTRSM) puo' essere espressa come un task con appropriate dipendenze `depend(in/out/inout)` sulle sezioni di array dei blocchi, creando un DAG di task con alto grado di parallelismo.

---

## SLIDE 32 – Block-Cholesky in OpenMP

**Implementazione con task e depend:**
La fattorizzazione di Cholesky a blocchi si presta perfettamente alla parallelizzazione con task OpenMP e clausola `depend`, grazie alla struttura naturale a DAG delle dipendenze tra le operazioni sui blocchi.

**DAG a 5 tile (right-looking):**
Il DAG rappresentato nella slide mostra le dipendenze per una versione right-looking a 5 tile dell'algoritmo di Cholesky. Ogni nodo del DAG corrisponde a un task (POTF2, TRSM, GEMM, o HERK) e ogni arco rappresenta una dipendenza di dati tra task. OpenMP con `depend(in/out/inout)` permette di esprimere esattamente questo grafo di dipendenze, consentendo al runtime di schedulare automaticamente i task rispettando le dipendenze e massimizzando il parallelismo.

File: `omp_chol.cpp`
