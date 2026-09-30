# SPM – Lezione 18: Thread-to-Core Affinity
## Appunti divisi per slide

---

## SLIDE 1 – Titolo

**Thread-to-Core Affinity**
Anno accademico 2025-2026 – Prof. Massimo Torquati

---

## SLIDE 2 – Outline

Gli argomenti trattati nella lezione sono:

- Comprensione dei concetti di CPU affinity
- Esempi semplici di utilizzo
- ThreadPool con work-sharing, cooperative help e Worker affinity

---

## SLIDE 3 – Perche' il Posizionamento dei Thread e' Importante?

Le prestazioni di un sistema multicore moderno non dipendono solo dal parallelismo algoritmico e dalle strutture dati utilizzate.

Dipendono anche da:
- **Dove i thread vengono eseguiti** (su quale core fisico/logico)
- **Se i thread migrano tra i core** durante l'esecuzione
- **Quanto bene la computazione segue la gerarchia di memoria**

**Thread migration:** lo spostamento di un thread da un core a un altro da parte dello scheduler del sistema operativo puo' compromettere la localita', specialmente per i thread worker a lunga vita. Quando un thread migra, la sua cache "calda" (ovvero i dati che aveva caricato in cache) diventa potenzialmente inutilizzabile sul nuovo core.

**NUMA (Non-Uniform Memory Access):** su macchine NUMA, ogni processore ha una propria memoria locale. Posizionare la computazione lontano dai dati (es. un thread su un nodo NUMA diverso da quello dove risiedono i suoi dati) aumenta la latenza di accesso alla memoria e riduce la banda disponibile.

**Affinity:** e' un meccanismo per vincolare il posizionamento dei thread al fine di migliorare la localita' e ridurre il rumore run-to-run (variabilita' dei tempi di esecuzione tra una run e l'altra).

---

## SLIDE 4 – CPU Affinity

La **CPU affinity** e' un meccanismo del sistema operativo usato per controllare su quale CPU un thread o processo puo' essere eseguito.

**Terminologia:**
- **Thread mapping (mappatura):** il posizionamento del thread su un determinato core.
- **Thread pinning (pinning):** indica solitamente un vincolo di posizionamento piu' forte: il thread e' legato a una specifica CPU e non puo' migrare.

**Tipi di binding:**
- **Assente:** il thread puo' essere eseguito su qualsiasi CPU consentita (comportamento di default dello scheduler).
- **Preferenziale:** il runtime o lo scheduler cerca di preservare la localita', ma puo' comunque spostare il thread se necessario.
- **Hard (rigido):** il thread e' limitato a un insieme specifico di CPU e non puo' andare altrove.

**Su Linux:** l'affinity e' espressa tramite una **affinity mask**, ovvero l'insieme delle CPU logiche su cui un thread o processo puo' essere eseguito. Lo scheduler puo' spostare il thread solo tra le CPU consentite da quella mask.

---

## SLIDE 5 – Motivazioni per l'Uso dell'Affinity

**Migliore localita':**
- Meno migrazioni mantengono le cache piu' "calde" e riducono il jitter di latenza (variazione nei tempi di risposta).
- Migliore localita' della cache e riutilizzo del TLB (Translation Lookaside Buffer).
- Su sistemi NUMA, mantenere i thread vicino alla loro memoria riduce il traffico verso la memoria remota.

**Minore interferenza:**
- L'affinity puo' ridurre la condivisione indesiderata con thread non correlati.
- Puo' aiutare a evitare posizionamenti scadenti, ad esempio su core occupati o su SMT siblings (due thread logici che condividono lo stesso core fisico).

**Prestazioni piu' stabili:**
- Linux gia' cerca di preservare una certa affinity "naturale" (cerca di tenere un thread sullo stesso core dove stava girando).
- Il pinning esplicito e' spesso utile in esperimenti controllati e in servizi a basso jitter (es. sistemi real-time o ad alta frequenza).

**Conclusione importante:** l'affinity serve principalmente a **ridurre il rumore e preservare la localita'**, non ad aumentare il throughput di picco di per se'.

---

## SLIDE 6 – Ispezione della Topologia della CPU

Prima di scegliere/applicare l'affinity, e' fondamentale conoscere la topologia dei core del sistema. Un pinning fatto male puo' addirittura **peggiorare** le prestazioni:

- Thread sullo stesso core fisico/SMT si contendono le risorse condivise (unita' di esecuzione, cache L1/L2, larghezza di banda della memoria).
- Su sistemi NUMA, un posizionamento sbagliato puo' aumentare gli accessi alla memoria remota.

**Concetti da conoscere:**
- **Socket:** il processore fisico (chip). Un sistema puo' avere piu' socket.
- **NUMA node:** ogni socket (o gruppo di core) ha la propria memoria locale (su sistemi NUMA).
- **Core fisico:** l'unita' di calcolo fisica all'interno di un socket.
- **Core logico (o CPU logica):** un core fisico con SMT (Simultaneous Multi-Threading, es. Hyper-Threading di Intel) espone piu' core logici.

**Strumenti per ispezionare la topologia:**
- `numactl --hardware`: mostra la configurazione dei nodi NUMA, le CPU associate a ciascun nodo e le distanze tra i nodi.
- `lscpu`: mostra informazioni dettagliate sulla CPU (numero di socket, core fisici, thread per core, topologia NUMA).
- `lstopo`: genera una rappresentazione grafica della topologia hardware del sistema (richiede il pacchetto hwloc).

---

## SLIDE 7 – Controllo dell'Affinity

**Da shell: comando `taskset`**
Permette di restringere un processo (o thread) a specifiche CPU.

Esempi:
- `taskset -c 0-2,8-10 ./myprogram`
  Esegue "myprogram" sulle CPU 0, 1, 2, 8, 9 e 10.

- `taskset -p <pid>`
  Mostra l'affinity mask corrente di un PID esistente.

- `taskset -pc 2,4 <pid>`
  Imposta l'affinity CPU di un PID esistente sulle CPU 2 e 4.

- `taskset -apc 2,4 <pid>`
  Applica l'impostazione di affinity a tutti i thread di un processo.

**Programmaticamente su Linux:**
Il C++ standard non ha un'API portabile per la CPU affinity. Le opzioni disponibili su Linux sono:

- **pthread_setaffinity_np:** interfaccia basata su POSIX threads (la piu' usata negli esempi del corso). Permette di impostare l'affinity mask di uno specifico thread.
- **sched_getaffinity / sched_setaffinity:** system call del kernel Linux per leggere e impostare l'affinity a livello di processo/thread.

Negli esempi del corso si utilizzera' l'interfaccia basata su pthread.

---

## SLIDE 8 – Esempio Pratico: affinity.cpp

Il file header **Affinity.hpp** fornisce alcune funzioni helper specifiche per Linux:

- `get_thread_affinity()`: interroga la maschera di affinity corrente del thread chiamante.
- `pin_thread_to_core(cpu)`: vincola il thread corrente a una singola CPU logica specificata.
- `pin_thread_to_cores(cpu_set)`: vincola il thread corrente a un insieme di CPU.
- `get_current_cpu()`: restituisce il numero della CPU su cui il thread e' attualmente in esecuzione.

**File di esempio: affinity.cpp**
Mostra come lavorare con la CPU affinity. Prende in input una CPU mask.

Esempio di utilizzo:
- `./affinity 0xC` — il valore 0xC in binario e' 1100, quindi il thread puo' essere eseguito sulle CPU 2 e 3.

E' possibile anche restringere il processo dall'esterno (potrebbe richiedere privilegi appropriati):
- `systemd-run --scope -p AllowedCPUs=8-15 ./affinity 0xC`
  L'affinity effettiva diventa l'**intersezione** del cpuset esterno e della richiesta del programma (nell'esempio, l'intersezione di {8-15} e {2,3} e' vuota, quindi il thread potrebbe essere vincolato a nessuna CPU o restare sull'affinita' di default).

**Nota importante:** l'affinity richiesta e' solo una parte del quadro. L'insieme effettivo di CPU puo' essere ulteriormente ristretto dal sistema operativo o dall'ambiente di esecuzione (ad esempio, da **SLURM** su cluster HPC, che gestisce l'allocazione delle risorse per i job).

---

## SLIDE 9 – Benchmarking dell'Affinity in un Pattern SPSC

**Setup del benchmark:**
- Un producer e un consumer comunicano attraverso un SPSC ring buffer.
- Ogni thread puo' essere pinnato indipendentemente a una CPU selezionata.
- Dopo un warmup iniziale, si misura il throughput a regime (steady-state).
- L'obiettivo e' confrontare posizionamenti buoni e cattivi.

**Osservazione interessante:**
In questo benchmark semplice, quando prod-work = cons-work = 0 (i thread non fanno lavoro locale, solo comunicano), posizionare producer e consumer su **SMT sibling cores** (i due core logici dello stesso core fisico) puo' essere vantaggioso. Questo perche' la comunicazione domina e i due thread rimangono molto vicini nella gerarchia della cache (condividono la cache L1/L2).

**Nota:** questa non e' una regola generale. All'aumentare della computazione locale, core fisici separati possono diventare preferibili, perche' i due thread non si contendono le unita' di esecuzione del core fisico.

**Esempio di utilizzo:**
```
./spsc_affinity_bench --prod-cpu 0 --cons-cpu 1 --ring 4096
                      --prod-work 0 --cons-work 0
                      --duration 20 --warmup 3
```

File di esempio: `spsc_affinity_bench.cpp`

---

## SLIDE 10 – ThreadPool con Work-Sharing, Cooperative Help e Affinity

**Due miglioramenti al threadPool** rispetto alla versione base:

**1. Cooperative help by caller thread (aiuto cooperativo del thread chiamante):**
- Invece di attendere passivamente il completamento dei task, il thread chiamante (quello che ha sottomesso il lavoro) aiuta ad eseguire i task in attesa nella coda.
- Questo riduce il tempo di inattivita' e migliora il supporto per la generazione ricorsiva di task.
- E' particolarmente utile quando un task genera sottotask e poi attende il loro completamento (pattern fork-join ricorsivo). In questo scenario, senza cooperative help, il thread chiamante rimarrebbe bloccato in attesa mentre i Worker eseguono i sottotask; con cooperative help, il thread chiamante si unisce all'esecuzione dei sottotask, sfruttando meglio le risorse.

**2. Worker affinity (affinita' dei Worker):**
- Ogni Worker puo' essere vincolato a una CPU selezionata al momento dell'avvio.
- Il binding viene eseguito una volta sola, prima di entrare nel ciclo di elaborazione dei task.
- Questo puo' migliorare la localita' della cache e ridurre il rumore di scheduling (variabilita' introdotta dallo scheduler del SO che sposta i thread tra i core).

File di esempio: `include/threadPool.hpp` e `mergesort-pool.cpp`
