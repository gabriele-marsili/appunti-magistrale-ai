# SPM – Lezione 16: C++ Lock-Free Programming (Concetti Base)
## Appunti divisi per slide

---

## SLIDE 1 – Titolo

**SPM: Lock-Free Programming in C++ – Basic Concepts**
Anno accademico 2025-2026 – Prof. Massimo Torquati

---

## SLIDE 2 – Outline

Gli argomenti trattati nella lezione sono:

- Concetto di operazioni atomiche e semplice esempio
- Memory Consistency Models (modelli di consistenza della memoria)
- Memory Model del C++
- Esempi di implementazione: ring buffer e bounded MPMC queue

---

## SLIDE 3 – C++ Atomics

Il C++11 introduce i tipi atomici (std::atomic<T>), che possono essere manipolati in un contesto concorrente in modo sicuro senza acquisire lock (ovvero senza usare std::mutex).

Le operazioni su tipi atomici sono **indivisibili** rispetto agli altri thread: nessun altro thread puo' osservare uno stato intermedio durante l'esecuzione dell'operazione.

In molti scenari, le operazioni atomiche sono piu' veloci dei mutex, specialmente in presenza di alta concorrenza quando la sezione critica e' molto piccola.

I C++ atomics possono essere usati per costruire **algoritmi non-blocking**, che evitano:
- Overhead di sospensione/ripresa dei thread
- Deadlock
- Problemi di priority inversion: un thread ad alta priorita' e' in attesa di acquisire un lock attualmente detenuto da un thread a bassa priorita'

---

## SLIDE 4 – Atomic Counting (Benchmark)

Per illustrare i vantaggi degli atomics si considera un esempio semplice: l'incremento concorrente di una variabile usando sia mutex che atomics.

Test eseguito sul nodo front-end di spmcluster.

Risultato: l'uso degli atomics e' circa **6 volte piu' efficiente** rispetto all'approccio tradizionale con lock.

Questo benchmark mostra come, per operazioni molto semplici (come un contatore), l'overhead del mutex (acquisizione del lock, potenziale context switch, rilascio) sia preponderante rispetto al lavoro utile. L'atomico opera direttamente sull'istruzione hardware senza richiedere strutture di sincronizzazione del kernel.

---

## SLIDE 5 – Sfide della Programmazione Lock-Free

La programmazione lock-free evita alcuni problemi di sincronizzazione (deadlock, priority inversion) ma ne introduce di nuovi.

In generale, e' piu' complessa e introduce problemi legati a **starvation** e **livelock**:

- **Starvation (fame):** un thread viene continuamente privato della possibilita' di fare progressi mentre gli altri thread continuano a progredire. Il thread e' sempre "scavalcato" dagli altri e non riesce mai a completare la propria operazione.

- **Livelock:** i thread interferiscono continuamente tra loro in modo tale che non c'e' reale progresso del sistema. A differenza del deadlock (in cui i thread sono bloccati), nel livelock i thread sono attivi ma non avanzano. E' come due persone che si spostano in un corridoio cercando di lasciarsi passare ma si muovono sempre nella stessa direzione.

E' necessaria una progettazione attenta per evitare race condition sottili e per garantire sia la correttezza che il progresso. Comprendere le **garanzie di progresso** e' essenziale quando si progettano strutture dati lock-free.

---

## SLIDE 6 – Garanzie di Progresso Non-Blocking

Esistono tre classi principali di garanzie di progresso (dalla piu' forte alla piu' debole):

**Wait-freedom (WF) – liberta' dall'attesa:**
- Ogni thread completa la propria operazione in un numero limitato di passi, indipendentemente dagli altri thread.
- La starvation e' impossibile per qualsiasi thread.
- E' la garanzia piu' forte.

**Lock-freedom (LF) – liberta' dai lock:**
- Il sistema nel suo complesso fa progressi: almeno un thread progredisce.
- La starvation e' possibile per alcuni thread (un thread specifico potrebbe non progredire mai).
- E' piu' debole della wait-freedom: garantisce il progresso globale ma non l'equita'.

**Obstruction-freedom (OF) – liberta' dall'ostruzione:**
- Un thread e' garantito di completare solo se alla fine viene eseguito in isolamento per un tempo sufficiente.
- Sotto contention, il livelock e' possibile.
- E' la garanzia piu' debole: ha senso solo quando la contention e' bassa o i conflitti possono essere risolti.

Lo strumento fondamentale per costruire algoritmi non-blocking in C++ e' std::atomic<T> e le sue operazioni atomiche.

---

## SLIDE 7 – std::atomic<T>

Gli oggetti std::atomic<T> non sono ne' copiabili ne' spostabili (not copyable, not movable).

**Principali operazioni offerte da std::atomic<T>:**
- **load / store:** leggere e scrivere il valore atomico
- **exchange:** sostituisce atomicamente il valore atomico e restituisce il vecchio valore
- **compare_exchange:** sostituisce atomicamente il valore atomico solo se corrisponde a un valore atteso (CAS)
- **fetch operations:** eseguono una lettura-modifica-scrittura (read-modify-write) in un singolo passo atomico (es. fetch_add, fetch_sub, fetch_or, ecc.)
- **wait / notify (da C++20):** forniscono un'attesa bloccante su valori atomici, simile nella filosofia alle condition variable

**Esempio pratico:** nel codice all_pair.cpp, la politica di scheduling dinamico puo' essere implementata usando un contatore atomico (fetch_add) al posto di una variabile protetta da mutex.

Riferimento: https://en.cppreference.com/w/cpp/atomic/atomic

---

## SLIDE 8 – Tipi di Dati Atomici in C++

Il C++ fornisce tipi atomici standard per flag, booleani, puntatori, tipi interi e altri tipi banalmente copiabili tramite std::atomic<T>.

Le operazioni disponibili dipendono dal tipo T sottostante (ad esempio, le operazioni aritmetiche sono disponibili solo per i tipi integrali e i puntatori).

**Nota importante:** se std::atomic<myT> e' definito per un tipo personalizzato myT e il metodo is_lock_free() restituisce false, tutte le operazioni (load, store, exchange, ecc.) sono comunque garantite essere atomiche, ma l'implementazione puo' ricorrere internamente a un lock.

Questo significa che il codice rimane corretto anche se l'hardware sottostante non supporta nativamente il tipo di dato corrispondente. Il programmatore non deve gestire manualmente questo fallback.

---

## SLIDE 9 – Compare-And-Swap (CAS)

Il **CAS (Compare-And-Swap)** e' una primitiva fondamentale per implementare assegnamenti atomici.

Esistono due metodi: compare_exchange_strong e compare_exchange_weak.
- compare_exchange_weak e' piu' efficiente ma puo' subire **spurious failures** (puo' restituire false anche se il confronto da' esito positivo).

**Semantica del CAS:**
1. Confronta il valore expected con il valore memorizzato nell'atomico.
2. Se sono uguali, imposta l'atomico al valore desired; altrimenti sovrascrive expected con il valore attuale dell'atomico.
3. Restituisce true se lo swap al passo 2 e' avvenuto con successo, false altrimenti.

**Regola importante:** le operazioni CAS devono essere sempre eseguite in un ciclo (loop), perche':
- Il CAS puo' fallire a causa di race condition con altri thread
- compare_exchange_weak puo' fallire spuriamente anche senza contention

---

## SLIDE 10 – Parallel Max-Reduction con CAS

**Problema:** calcolare il massimo di una sequenza di interi a 64 bit in parallelo.

**Versione errata (false_max):**
La versione che testa la condizione in un if separato dall'assegnamento e' scorretta: il controllo e l'assegnazione sono due operazioni distinte e non atomiche. Due o piu' thread potrebbero leggere lo stesso valore prima di eseguire l'assegnamento in ordine casuale, causando risultati incorretti.

**Versione corretta (correct_max):**
Usa un CAS in cui la lettura e la scrittura vengono eseguite atomicamente. Il ciclo CAS garantisce che solo il thread che effettivamente aggiorna il massimo con un valore maggiore di quello corrente riesca a farlo senza interferenze.

**Nota interessante sulle prestazioni:** la versione errata puo' essere piu' lenta perche' molti thread eseguono store atomici ridondanti sulla stessa cache line, causando maggiore contention e traffico di coerenza della cache rispetto alla versione basata su CAS. Questo non e' pero' una regola generale.

---

## SLIDE 11 – Concetti di Base sulla Memoria

L'intuizione dice che una lettura dalla memoria dovrebbe restituire l'ultimo valore scritto in quella locazione. In un sistema mono-thread questo e' ovvio, ma in un sistema multiprocessore il concetto di "ultimo valore scritto" e' ambiguo.

Dipende dall'**ordinamento e dalla visibilita' delle operazioni di memoria**: l'ordine in cui le operazioni eseguite da un thread diventano visibili agli altri thread.

I moderni processori e i compilatori possono **riordinare** le operazioni di memoria in vari modi per ragioni di prestazioni. Questo influenza quando le scritture di un thread diventano visibili agli altri.

Un **Memory Consistency Model** definisce il comportamento consentito per le letture e le scritture su indirizzi diversi in un sistema parallelo. Risponde alla domanda: quali valori puo' restituire una load dato un certo ordine di store da thread diversi?

---

## SLIDE 12 – Memory Consistency Models

**Ordinamento e visibilita' delle operazioni:**
- Le regole di ordinamento definiscono quando e come i cambiamenti in un thread diventano visibili agli altri.
- Garantiscono interazioni prevedibili tra i thread, anche in presenza di ottimizzazioni del compilatore e/o dell'hardware.

Un **Memory Consistency Model** e' un insieme di regole che definisce come le operazioni di memoria (letture e scritture) si comportano e vengono osservate attraverso thread o processori diversi. Stabilisce l'ordine in cui le operazioni sembrano eseguirsi e definisce quando il risultato di una scrittura di un thread diventa visibile agli altri.

Serve a:
- **Garantire la correttezza dei programmi:** previene i bug nei programmi concorrenti definendo chiaramente l'ordine delle operazioni.
- **Abilitare o disabilitare ottimizzazioni per le prestazioni:** modelli diversi offrono diverse possibilita' di ottimizzazione.

**Punto chiave:** gli atomics non garantiscono solo aggiornamenti atomici; impongono anche specifiche regole di ordinamento e visibilita' della memoria.

---

## SLIDE 13 – Perche' l'Ordinamento della Memoria e' Importante?

**Esempio illustrativo (inizialmente A = B = flag = 0):**

Thread 1:
- Store A = 1
- Store B = 1
- Store flag = 1

Thread 2:
- while (Load flag == 0); // attesa attiva
- valA = Load A
- valB = Load B
- print(valA, valB)

Ci si aspetta che Thread 2 stampi A=1, B=1. Senza sincronizzazione questo non e' garantito.

Per alcuni modelli di consistenza, i risultati (0,0), (1,0) e (0,1) sono output validi.

**Perche'?** Perche' le scritture su indirizzi diversi (A, B, flag) possono diventare visibili in momenti diversi su core diversi. Se il sistema include cache, la coerenza della cache ordina ogni locazione individualmente. Quale risultato viene stampato dipende dal memory consistency model.

**Conclusione: l'ordinamento della memoria non e' automaticamente sequenziale.**

---

## SLIDE 14 – Cache Coherence vs. Memory Consistency

Sono due concetti distinti che spesso vengono confusi:

**Memory Consistency (Consistenza della memoria):**
- Definisce il comportamento corretto del programma.
- Stabilisce le regole per l'ordinamento e la visibilita' di tutte le operazioni di memoria.
- Specifica come le operazioni di memoria sono ordinate e osservate tra processori/core diversi, su locazioni diverse.
- E' visibile al software di sistema ed e' parte della specifica dell'architettura.

**Cache Coherence (Coerenza della cache):**
- Riguarda una singola locazione di memoria replicata in piu' cache.
- Garantisce che tutti i processori vedano lo stesso valore per una data locazione di memoria, mantenendo il valore consistente tra le cache.
- NON e' visibile a livello software. Possiamo vederne effetti collaterali (es. false sharing, speedup superlineare, ecc.).

I moderni processori usano protocolli di coerenza per mantenere sincronizzate le cache. Sopra di essi, i memory consistency model definiscono come compilatori e hardware possono riordinare le operazioni.

---

## SLIDE 15 – Relazione Happens-Before (HB)

La relazione **Happens-Before (HB)** e' il concetto fondamentale per ragionare sulla correttezza dei programmi concorrenti.

**Definizione:** se A happens-before B, allora B deve essere in grado di osservare gli effetti di A.
- Ogni scrittura/effetto eseguito da A e' visibile a B.
- B non puo' osservare uno stato che ignora gli effetti di A (B non puo' essere riordinato prima di A).
- HB e' un ordine parziale transitivo: se A HB B e B HB C, allora A HB C.

**Come viene stabilita la relazione HB:**
- **Sequenced-before (intra-thread):** all'interno di un singolo thread, le azioni sono ordinate secondo le regole di esecuzione del C++.
- **Synchronizes-with (inter-thread):**
  - unlock(m) synchronizes-with lock(m) sullo stesso mutex m
  - notify_one/all() synchronizes-with il ritorno con successo di wait()
  - Il completamento di un thread synchronizes-with il ritorno con successo da join()
  - Un'operazione store-release su un atomico synchronizes-with un'operazione load-acquire che legge quel valore

**Data race e Undefined Behavior:** due accessi non-atomici in conflitto alla stessa variabile (almeno uno dei quali e' una scrittura) e senza relazione HB causano una data race, che in C++ e' Undefined Behavior.

---

## SLIDE 16 – Ordinamento delle Operazioni di Memoria

**Program order (ordine del programma):**
Un programma definisce una sequenza di letture e scritture. All'interno di un singolo thread, le operazioni appaiono nell'ordine del programma.

**Quattro tipi di vincoli di ordinamento (A -> B indica un vincolo di ordinamento):**

- **W_X -> R_Y:** una scrittura su X deve essere ordinata prima della successiva lettura di Y. Quando una scrittura precede una lettura nell'ordine del programma, il modello di memoria puo' richiedere che tale ordinamento venga preservato.

- **R_X -> R_Y:** una lettura da X deve essere ordinata prima della successiva lettura da Y.

- **R_X -> W_Y:** una lettura da X deve essere ordinata prima della successiva scrittura su Y.

- **W_X -> W_Y:** una scrittura su X deve essere ordinata prima della successiva scrittura su Y.

Modelli di memoria diversi possono rilassare alcuni o tutti questi vincoli di ordinamento, consentendo al compilatore e all'hardware di eseguire riordinamenti per migliorare le prestazioni.

---

## SLIDE 17 – Sequential Consistency (SC)

**Definizione di Leslie Lamport (1979):**
"Un multiprocessore e' sequenzialmente consistente se il risultato di qualsiasi esecuzione e' lo stesso di quello che si otterrebbe se le operazioni di tutti i processori fossero eseguite in un qualche ordine sequenziale, e le operazioni di ciascun processore appaiono in questa sequenza nell'ordine specificato dal suo programma."

E' la prima definizione formale ampiamente adottata di memory consistency. SC e' il modello piu' restrittivo.

**Definizione equivalente:**
Esiste un unico ordine totale di tutti i load e store su tutti i thread tale che il valore restituito da ogni load e' uguale al valore del piu' recente store in quella locazione in questo ordine totale.

**Proprieta' di SC:**
- SC preserva tutti e quattro i vincoli di ordinamento delle operazioni di memoria: W->R, R->R, R->W, W->W.
- E' il modello piu' intuitivo dal punto di vista del programmatore.

**Costo:** l'hardware e i compilatori reali possono riordinare le operazioni per efficienza, quindi sono spesso necessarie istruzioni aggiuntive (fence) o sincronizzazioni piu' forti per garantire SC nella pratica.

---

## SLIDE 18 – Sequential Consistency: Esempio

**Metafora dello "switching":** tutti i processori emettono load/store nell'ordine del programma, e la memoria sceglie un processore alla volta, ne esegue la prossima operazione e poi sceglie un altro processore.

**Esempio con P0 e P1 (A=0, B=0 inizialmente):**
- P0: Store A=1; Load B in r1
- P1: Store B=2; Load A in r2

**Con SC, il risultato r1=0 e r2=0 NON e' consentito.** SC consente solo:
- r1=0, r2=1 (P0 esegue tutto prima di P1, ma P0 legge B prima che P1 scriva)
- r1=2, r2=0 (P1 esegue tutto prima, P0 legge B=2 ma P1 legge A prima dello store di P0)
- r1=2, r2=1 (P1 esegue prima tutto, poi P0)

Il risultato (0,0) sarebbe possibile solo se le store venissero ritardate rispetto alle load, il che viola SC.

---

## SLIDE 19 – Motivazione per la Consistenza Rilassata

I modelli di consistenza rilassata (Relaxed Memory Consistency) consentono di rilassare alcuni vincoli sull'ordine del programma.

**Perche'?** Per migliorare le prestazioni nascondendo la latenza della memoria: si sovrappongono le operazioni di accesso alla memoria con altre operazioni indipendenti.

I moderni processori usano **write buffer** per migliorare le prestazioni: un processore puo' consentire che una lettura a una locazione di memoria diversa bypasyi store piu' vecchi in attesa nel buffer locale (W_X -> R_Y rilassato), per nascondere la latenza delle scritture.

Un **Write Buffer** e' una piccola coda nella CPU che contiene i dati da operazioni di scrittura recenti non ancora trasmesse alla memoria principale (o al livello successivo nella gerarchia di memoria). Il processore puo' continuare a eseguire istruzioni senza attendere che ogni store sia completato. Se la CPU deve leggere una locazione nel write buffer, puo' ottenere quel dato direttamente dal buffer (store-to-load forwarding).

Questo e' perfettamente corretto dal punto di vista di un singolo thread, ma per applicazioni multi-thread e' necessaria sincronizzazione aggiuntiva. Poiche' una lettura puo' bloccare il processore finche' non e' soddisfatta, i load possono bypassare store in attesa su indirizzi diversi nel write buffer.

---

## SLIDE 20 – Total Store Order e Processor Consistency

**TSO (Total Store Order)** e **PC (Processor Consistency)** rilassano entrambi il vincolo W->R in modi diversi.

**TSO:**
- Tutti i processori osservano le scritture di ciascun processore nello stesso ordine.
- Un load puo' bypassare store piu' vecchi nel write buffer locale (ma un load NON puo' bypassare uno store piu' vecchio sulla stessa locazione!).
- Tutti i processori osservano il medesimo ordine per le scritture di qualsiasi processore.
- Un load puo' bypassare uno store precedente su un indirizzo diverso, quindi un thread puo' temporaneamente osservare un valore piu' vecchio.
- **x86 usa un modello di memory consistency simile a TSO.** NOTA: TSO consente r1=0 e r2=0 nell'esempio precedente!

**PC (Processor Consistency):**
- Tutti i processori osservano le scritture emesse da ciascun processore nell'ordine del programma, ma le scritture provenienti da processori diversi non devono formare un unico ordine globale.
- Richiede sincronizzazione esplicita (es. memory fence) quando sono necessari aggiornamenti coordinati su piu' locazioni.
- Nessuna architettura moderna implementa strettamente PC. Molti sistemi adottano modelli piu' forti o piu' rilassati.

---

## SLIDE 21 – Consentire il Riordinamento delle Scritture (PSO e Weak Ordering)

**PSO (Partial Store Ordering)** rilassa anche il vincolo W->W.

**Perche'?** Il processore puo' riordinare le operazioni di scrittura nel Write Buffer per ragioni di prestazioni (es. una scrittura potrebbe essere un cache miss, mentre l'altra e' un cache hit con costi di gestione inferiori). Questa e' un'ottimizzazione valida per un singolo thread.

Per le applicazioni multi-thread, e' necessaria sincronizzazione aggiuntiva.

**Esempio del problema con PSO:**

Thread 1 (su P0):
- A = 1
- flag = 1

Thread 2 (su P1):
- while (flag == 0); // attesa
- print A

Sotto PSO, P1 potrebbe osservare il cambiamento a flag prima del cambiamento ad A, stampando quindi 0 (il valore iniziale di A). Questo non e' consentito da SC e TSO.

**Perche' le architetture consentono riordinamenti piu' aggressivi?**
- Sovrapporre letture e scritture multiple indipendenti nel sistema di memoria
- Eseguire le letture in anticipo e ritardare le scritture, nascondendo ulteriormente la latenza della memoria
- L'esecuzione out-of-order e speculativa consente alla CPU di mantenere la pipeline piena

Un esempio di modello completamente rilassato e' il **Weak Ordering** (tutti gli ordinamenti possono essere rilassati). Le microarchitetture ARM e POWER adottano un modello di memoria molto rilassato per prestazioni migliori, a costo di maggiore complessita' di programmazione.

---

## SLIDE 22 – Ripristinare l'Ordine: Fence (Barriere di Memoria)

Le architetture forniscono primitive per imporre un ordinamento piu' stretto delle operazioni di memoria.

**Memory barrier instructions (fence):** restringono il riordinamento delle operazioni, ma sono costose.

Una fence impone vincoli di ordinamento tra le operazioni di memoria prima e dopo la fence nel programma.

**Tipologie di fence:**
- **Load fence (RMB - Read Memory Barrier):** impedisce il riordinamento dei load (letture) tra loro
- **Store fence (WMB - Write Memory Barrier):** impedisce il riordinamento degli store (scritture) tra loro
- **Full fence (MB - Memory Barrier):** impedisce il riordinamento sia dei load che degli store

Altre primitive di sincronizzazione possono imporre ordinamento, spesso su locazioni di memoria specifiche: test_and_set, compare-and-swap e tutte le operazioni Read-Modify-Write (RMW).

I programmatori (e in alcuni casi il compilatore/runtime) devono inserire correttamente le sincronizzazioni per garantire un ordinamento corretto. Lock e altre operazioni di sincronizzazione possono fornire implicitamente garanzie di ordinamento simili alle fence.

---

## SLIDE 23 – Garanzia Data-Race-Free (DRF)

**Teorema fondamentale:** se un programma e' DRF (Data-Race-Free), allora il suo comportamento osservabile e' consistente con una qualche esecuzione Sequenzialmente Consistente.

Conseguenze:
- Tutte le operazioni si comportano come se si verificassero in un unico ordine globale che rispetta l'ordine del programma di ciascun thread.
- Il riordinamento delle istruzioni non compromette la correttezza se il programma e' DRF.
- I programmi correttamente sincronizzati (tramite mutex, barriere, atomics, ecc.) sono DRF.

**Importante:** la Sequential Consistency non elimina di per se' le data race. I programmatori devono garantire esplicitamente la data-race freedom tramite sincronizzazione.

**Definizione di Data Race:** due o piu' thread accedono concorrentemente alla stessa locazione di memoria, almeno uno esegue una scrittura, e non c'e' sincronizzazione tra gli accessi.

**Razionale del riordinamento:** il principio e' "ottimizzare per il caso comune". Poiche' la maggior parte degli accessi alla memoria non crea conflitti, le architetture evitano di incorrere nell'overhead di un ordinamento stretto per ogni operazione.

---

## SLIDE 24 – I Linguaggi di Programmazione Hanno Bisogno di un Memory Model

Il compilatore puo' riordinare le istruzioni per ragioni di prestazioni, indipendentemente dalle microarchitetture di basso livello. E' generalmente accettato che un compilatore possa riordinare letture e scritture ordinarie quasi arbitrariamente, purche' il riordinamento non possa cambiare l'esecuzione osservabile del codice per un singolo thread.

Il **C++ moderno (da C++11)** e anche il linguaggio Java definiscono un memory model che garantisce SC per i programmi DRF. Il compilatore mappa gli atomics e le fence a livello di linguaggio sul modello di memoria HW sottostante.

**Nessuna garanzia** se il programma contiene data race: i programmi non sincronizzati contengono data race, ovvero l'output dipende dalla velocita' relativa dei processori che eseguono i thread (risultati non deterministici).

**C++11 introduce, a livello del linguaggio:**
- Operazioni atomiche e fence per specificare come funziona l'ordinamento della memoria sia per le operazioni atomiche che per quelle non-atomiche.
- Questo aiuta i programmatori a controllare la visibilita' e l'ordinamento degli accessi alla memoria tra i thread, rendendo il programma portabile tra diverse microarchitetture.

---

## SLIDE 25 – Basi del Memory Model C++

Il C++ fornisce all'utente **sei opzioni di memory ordering** per i tipi atomici:

1. **std::memory_order_relaxed:** nessun vincolo di ordinamento aggiuntivo
2. **std::memory_order_consume:** (deprecato di fatto, non usare)
3. **std::memory_order_acquire:** per le operazioni di load
4. **std::memory_order_release:** per le operazioni di store
5. **std::memory_order_acq_rel:** combinazione di acquire e release, per RMW
6. **std::memory_order_seq_cst:** sequentially consistent (il default)

**Regole di compatibilita':**
- Le operazioni di **Store** possono essere: relaxed, release, o seq_cst
- Le operazioni di **Load** possono essere: relaxed, acquire, o seq_cst
- Le operazioni **RMW** (Read-Modify-Write) possono essere: relaxed, acquire, release, acq_rel o seq_cst

Il memory ordering di default e' il piu' restrittivo: **std::memory_order_seq_cst**.

Ogni ordering impone vincoli diversi su come le operazioni possono essere riordinate attorno all'operazione atomica.

Nota: std::memory_order_consume non e' implementato dalla maggior parte dei compilatori e lo standard C++ sconsiglia di usarlo.

---

## SLIDE 26 – C++ Memory Ordering: Tipi e Semantica

Riferimento: https://en.cppreference.com/w/cpp/atomic/memory_order

**Sequential Consistency (seq_cst):**
Tutte le operazioni atomiche seq_cst su tutti i thread appaiono in un unico ordine globale coerente con l'ordine del programma di ciascun thread. E' la garanzia piu' forte.

**Acquire (per load e RMW):**
Impedisce a tutti i load/store successivi nel thread corrente di essere spostati prima dell'operazione atomica di load corrente. Se l'acquire legge un valore prodotto da un matching release sullo stesso atomico, si stabilisce una relazione synchronizes-with (e quindi happens-before).

**Release (per store e RMW):**
Impedisce a tutti i load/store precedenti nel thread corrente di essere spostati dopo l'operazione atomica di store corrente. Si accoppia con un successivo load in acquire.

**Relaxed:**
Nessuna restrizione sul riordinamento delle operazioni di load/store circostanti. E' garantita solo l'atomicita' dell'operazione (nessuna relazione HB).

**Acquire-Release (per RMW):**
Combinazione di acquire e release: carica il valore corrente in modalita' acquire e memorizza un nuovo valore in modalita' release. Nessuna operazione successiva puo' essere spostata prima, e nessuna operazione precedente puo' essere spostata dopo.

Operazioni RMW: exchange, compare-exchange, test_and_set su atomic_flag, e fetch_*.

---

## SLIDE 27 – SC Implica un Ordine Totale

La semantica SC richiede un unico ordine totale su tutte le operazioni atomiche con ordering std::memory_order_seq_cst.

**Esempio di codice con due thread che scrivono su x e y e poi leggono y e x rispettivamente:**

L'assert finale (che controlla che almeno uno dei due flag letti sia true) non puo' mai scattare con seq_cst, perche' o lo store su x oppure lo store su y deve avvenire prima di almeno uno dei load su x o y.

Ragionamento: se il load a linea 16 restituisce false, significa che lo store su x deve essere avvenuto prima dello store su y e quindi il load a linea 21 deve restituire true. Vale anche il viceversa.

**SC e' il memory ordering piu' costoso:** richiede la sincronizzazione globale tra tutti i thread (imposta dal compilatore C++). Usarla solo quando effettivamente necessaria.

---

## SLIDE 28 – Relaxed Ordering

Con **std::memory_order_relaxed**, ogni operazione atomica e' garantita essere atomica, ma non vengono imposti vincoli di ordinamento aggiuntivi.

Con il relaxed ordering non esiste una relazione happens-before tra le operazioni atomiche. Le operazioni su atomici diversi possono essere osservate in qualsiasi ordine.

**Esempio:** con relaxed, l'assert (equivalente al precedente esempio) puo' scattare. Un load puo' restituire false anche se un altro load sullo stesso thread ha restituito true poco prima. Questo significa che un thread potrebbe vedere lo store su y avvenire prima dello store su x, mentre l'altro thread vede lo store su x ma non y.

**Nota pratica:** su alcune CPU (es. x86) potrebbe non essere possibile osservare l'assert che scatta a causa dell'ordinamento degli store nell'HW (x86 usa TSO, che e' piu' forte di relaxed). Su architetture piu' rilassate (ARM, POWER) il comportamento errato e' osservabile.

---

## SLIDE 29 – Acquire e Release Ordering

Con l'**acquire-release ordering**, la sincronizzazione e' a coppie tra il thread che esegue la release e il thread che esegue l'acquire. Thread diversi possono vedere ordinamenti diversi.

Un'operazione release **synchronizes-with** un'operazione acquire che legge il valore scritto.

**Differenza rispetto a SC:** con SC c'e' un ordine totale globale su tutte le operazioni atomiche seq_cst. Con acquire-release, la sincronizzazione e' solo tra le coppie release-acquire specifiche; non c'e' un ordine globale tra operazioni su variabili diverse.

**Conseguenza:** in un codice con due coppie release-acquire indipendenti su variabili diverse, l'assert finale potrebbe scattare perche' le due coppie non si influenzano. Il fatto che un thread veda il valore di x non impone alcun vincolo su cosa l'altro thread vede per y.

Nota: il fallimento e' possibile su modelli deboli (ARM/RISC-V/POWER). Su x86 non fallisce a causa del modello TSO piu' forte dell'hardware.

---

## SLIDE 30 – Rilassare SC con Acquire e Release

E' possibile ottenere lo stesso effetto della SC usando acquire-release con sincronizzazioni meno costose, purche' le coppie siano strutturate correttamente.

**Esempio di HB chain corretto:**
- x.store(relaxed) e' sequenced-before y.store(release) → il primo non puo' essere spostato dopo il secondo
- y.store(release) synchronizes-with y.load(acquire) → se l'acquire legge il valore scritto dalla release, si stabilisce HB
- y.load(acquire) e' sequenced-before x.load(relaxed) → il secondo non puo' essere spostato prima del primo

Per transitivity: x.store happens-before x.load → x.load deve vedere true.

**Regola fondamentale:** acquire e release devono essere "accoppiati" per fornire qualsiasi sincronizzazione. Nel codice, e' fondamentale che il load dell'atomico venga fatto in un ciclo (loop): se non e' in loop, le operazioni potrebbero non essere accoppiate correttamente e la sincronizzazione non viene stabilita.

---

## SLIDE 31 – Fence (Barriere di Memoria in C++)

Le **fence** sono operazioni che impongono vincoli di ordinamento senza modificare una locazione di memoria.

Le fence sono spesso usate per aggiungere vincoli di ordinamento attorno a operazioni atomiche relaxed.

Il C++11 fornisce: **std::atomic_thread_fence(memory_order)**

**Tipi di fence:**
- **Release fence:** impedisce a load/store precedenti di spostarsi dopo la fence
- **Acquire fence:** impedisce a load/store successivi di spostarsi prima della fence
- **Acq_rel fence:** combina le due precedenti, agisce come full barrier
- **Seq_cst fence:** agisce come full barrier e partecipa all'ordine SC globale per le operazioni seq_cst

**Utilizzo con operazioni non-atomiche:**
Le fence con operazioni atomiche possono essere usate per ordinare anche operazioni non-atomiche. Nell'esempio della slide: lo store a linea 10 happens-before il load a linea 17 grazie alle fence. Lo store non puo' bypassare la release fence, la release fence synchronizes-with l'acquire fence a linea 16, e il load a linea 15 non puo' bypassare l'acquire fence.

---

## SLIDE 32 – All-Pairs Distance Matrix: Lock vs Atomic

Risultati ottenuti eseguendo l'implementazione all_pair.cpp per il dataset MNIST sul nodo front-end del cluster.

**Distribuzione dinamica con c=1: confronto tra lock-based e atomic-based.**

| #threads | std::mutex | std::atomic |
|---|---|---|
| 20 | 59.32 s | 59.36 s |
| 40 | 34.22 s | 34.10 s |
| 60 | 65.21 s | 61.07 s |

**Osservazione:** con alta concorrenza (60 thread), la versione atomica si comporta meglio.

Con pochi thread (20-40), le prestazioni sono simili: il costo di sincronizzazione non e' il collo di bottiglia. Con alta concorrenza (60 thread) e alta contention, gli atomics si rivelano piu' scalabili del mutex, perche' evitano il costo di context switch e il syscall overhead del mutex.

---

## SLIDE 33 – Spin-Lock

**Implementazione semplice di spin lock usando le funzionalita' C++20:**

Il lock usa un **atomic_flag** (un flag booleano per cui le operazioni sono garantite lock-free a livello HW su tutte le architetture conformi).

Operazioni disponibili su atomic_flag: test_and_set, clear (da sempre), e da C++20: test, wait, notify_one/all.

**Logica del lock:**
- Il metodo lock tenta di acquisire il lock a linea 11 con test_and_set. Se fallisce (il lock era gia' acquisito), lo spin-lock esegue uno spin usando test() a linea 12 finche' non vede un cambiamento, poi ritenta di acquisire il lock.
- Il metodo clear a linea 16 imposta l'atomic_flag a false (rilascia il lock).

**Differenza tra test e test_and_set:**
- test_and_set e' un RMW e genera traffico di coerenza della cache ogni volta.
- test e' una semplice lettura: lo spinning su test riduce il traffico perche' si legge dalla cache locale. Solo quando il flag cambia si ritenta il test_and_set (strategia test-and-test-and-set, TTAS).

Riferimento: https://en.cppreference.com/w/cpp/atomic/atomic_flag

---

## SLIDE 34 – Max-Reduction Revised: Benchmark

Codice atomic_max_v2.cpp. Il calcolo del massimo di una sequenza implementato con: std::mutex, spinLock, e atomic CAS.

**Tempo di esecuzione su 5 run (secondi, min-max):**

| std::mutex | spinLock | std::atomic |
|---|---|---|
| 11.0 – 11.9 | 5.6 – 20.7 | 0.8 – 1.3 |

**Osservazioni:**
- La versione atomic-based e' consistentemente piu' veloce e ragionevolmente stabile.
- L'implementazione con spinLock e' quasi sempre peggiore del mutex: ha alta varianza (da 5.6 a 20.7 s) perche' sotto alta contention lo spin degrada rapidamente.
- **Implementare uno spin lock efficiente e' difficile.** I dettagli contano molto: backoff esponenziale, strategia TTAS, numero di spin prima di cedere il controllo, ecc.

---

## SLIDE 35 – Barrier e Spin-Barrier

**std::barrier (C++20):** primitiva di sincronizzazione che consente a un numero fisso di thread di attendere che tutti abbiano raggiunto un certo punto nel codice.

- La barriera e' riutilizzabile, quindi puo' essere usata in algoritmi iterativi o a fasi in cui sono necessari piu' punti di barriera tra le iterazioni.

**Trade-off tra spin-barrier e blocking barrier:**

- **Spin-barrier (busy-waiting):** quando si prevede che il tempo di attesa alla barriera sia molto breve, l'implementazione con busy-wait puo' avere meno overhead rispetto a una barriera bloccante, perche' evita il costo dei context switch.

- **Blocking barrier (std::barrier):** se i tempi di attesa possono essere piu' lunghi o sono imprevedibili, e' generalmente preferibile usare una barriera bloccante, perche' permette all'OS di sospendere i thread in attesa, liberando risorse CPU per altri lavori. Le barriere bloccanti mettono i thread in sleep usando la sincronizzazione a livello OS.

L'esempio di come usare std::barrier e una possibile implementazione della spin-barrier si trovano nel file spinbarrier-wait.cpp.

---

## SLIDE 36 – SPSC Ring Buffer

**SPSC bounded ring buffer:** coda circolare di dimensione fissa per Single Producer / Single Consumer.

E' possibile implementare un SPSC lock-free: nessun mutex; solo due indici (head, tail) aggiornati da thread diversi. Vantaggi: bassa latenza, alto throughput, jitter prevedibile.

**Caratteristiche dell'implementazione proposta:**
- **Cache-friendly:** senza allocazioni dinamiche; array pre-allocato; head e tail sono su cache line diverse (usando alignas(std::hardware_destructive_interference_size) o 64 byte) per evitare il **false sharing**. Il false sharing si verifica quando due thread accedono frequentemente a variabili diverse ma sullo stesso cache line, causando traffico di invalidazione inutile.
- Supporta **back-pressure esplicita:** quando la coda e' piena/vuota, push/pop possono fallire rapidamente (non-blocking) o bloccarsi con C++20 wait/notify.
- Caso d'uso tipico: **pipeline producer-consumer**.

---

## SLIDE 37 – SPSC Ring Buffer (cont.)

head e tail sono std::atomic<std::size_t> (spesso racchiusi in una struct con padding per evitare il false-sharing tra i due indici stessi).

**Regola publish/consume con release/acquire:**
- **Producer:** scrive il payload, poi esegue tail.store(next, std::memory_order_release)
- **Consumer:** esegue tail.load(std::memory_order_acquire) prima di leggere il payload
- Simmetricamente per head: il consumer avanza head in release, il producer osserva head in acquire.

**Dove usare relaxed:** i load/store dell'indice "posseduto" da un thread (es. il producer legge la propria tail locale) possono usare relaxed; si usa acquire quando si osserva l'indice dell'altra parte; si usa release quando si avanza il proprio indice dopo l'accesso al payload.

**Perche' funziona:** la release del producer su tail synchronizes-with l'acquire del consumer sullo stesso atomico, quindi tutte le scritture del payload happens-before le letture del consumer. Non sono necessarie fence esplicite aggiuntive.

**Garanzia di progresso:**
- **Wait-free** quando si usa l'API non-bloccante (push/pop che restituiscono false se la coda e' piena/vuota)
- **Blocking** con sleep efficiente usando C++20 atomic::wait/notify_one

---

## SLIDE 38 – Il Problema ABA

Le strutture dati basate sugli atomics possono essere piu' veloci di quelle basate su lock, ma presentano il cosiddetto **problema ABA**.

**Definizione:** il problema ABA si verifica quando il valore di una locazione cambia da A a B e poi di nuovo ad A. Un thread che ha letto A in precedenza non puo' rilevare che e' avvenuta una modifica intermedia.

E' un problema tipico delle strutture dati lock-free basate su puntatori.

**Perche' e' pericoloso:** un CAS confronta solo il valore corrente con quello atteso. Se il valore e' tornato al valore originale (A -> B -> A), il CAS ha successo credendo che nulla sia cambiato, ma in realta' la struttura dati e' stata modificata nel frattempo.

---

## SLIDE 39 – Esempio ABA (Stack Lock-Free)

**Pseudocodice tipico di una operazione pop su uno stack lock-free basato su puntatori:**

```
Node* pop() {
    Node* current = head;
    while (current) {
        if (head == current &&
            CAS(&head, current, current->next)) break;
        current = head;
    }
    return current;
}
```

**Scenario del problema ABA (lista iniziale: 1 -> 2 -> 3):**

1. Thread 1 tenta di fare pop del nodo head (1), ma viene sospeso appena prima di eseguire il CAS (dopo aver letto current->next = nodo 2).
2. Thread 2 si avvia e fa pop del nodo head (1).
3. Thread 2 fa pop del nuovo head (nodo 2).
4. Thread 2 fa push di un nuovo nodo (4), riutilizzando il nodo che conteneva il valore iniziale 1 (stesso indirizzo!).
5. Thread 1 riprende, il suo CAS ha successo perche' il puntatore corrente coincide (i puntatori raw sembrano uguali anche se il contenuto e' cambiato), rimuovendo l'attuale head (4) e impostando head a un nodo che non e' piu' nella lista (il nodo 2, gia' eliminato). Risultato: corruzione della struttura dati.

---

## SLIDE 40 – Soluzioni al Problema ABA

**Approccio 1: Tag (version number)**
- Aggiungere un tag extra (numero di versione) al dato.
- Il tag viene incrementato ogni volta che il puntatore viene aggiornato.
- Il CAS opera sia sul puntatore che sul tag come singola operazione atomica.
- Anche se l'indirizzo e' lo stesso, il tag sara' cambiato (A->B->A avra' incrementato il tag due volte).
- Richiede **CAS2** (double-word CAS, non disponibile su tutte le architetture).
- Il numero di tag potrebbe dover essere molto grande per evitare overflow (wraparound).

**Approccio 2: Hazard Pointers (puntatori di pericolo)**
- Affrontano il problema di liberare o riutilizzare nodi che potrebbero ancora essere acceduti da altri thread.
- Prima di leggere o modificare un nodo condiviso, ogni thread "annuncia pubblicamente" che sta usando quel nodo tramite una lista di hazard pointer per thread.
- Se un puntatore appare in qualsiasi lista di hazard pointer, non puo' essere reclamato.
- Una volta che il thread ha finito con il nodo, rimuove il puntatore dalla lista. Se nessun altro thread ha quel puntatore nella sua lista, il nodo puo' essere liberato in sicurezza.

**Approccio 3: Reclamazione differita della memoria**
- Impedisce il riutilizzo di nodi mentre esistono richieste in sospeso.
- Gli hazard pointer sono spesso usati per la reclamazione sicura della memoria.

---

## SLIDE 41 – Bounded MPMC Queue

**Use case:** implementare una coda FIFO lock-free bounded MPMC (Multiple Producer Multiple Consumer) usando un CAS-loop per le operazioni di enqueue (push) e dequeue (pop). File: bounded-mpmc.cpp.

**Struttura:**
- Il buffer e' un ring-buffer con due indici (pread e pwrite) che puntano alla testa e alla coda della coda.
- Il buffer memorizza puntatori incapsulati in un nodo contenente il puntatore al dato e un indice atomico long (seq), che e' la sequenza degli elementi memorizzati nella coda. seq consente ai thread di "prenotare" un nodo. La sequenza aumenta monotonicamente.

**Operazione push (enqueue):**
- Se la sequenza e' uguale alla coda (pwrite), si tenta di prenotare il nodo con un'operazione CAS che aggiorna atomicamente il puntatore tail.
- Se l'operazione riesce, la sequenza viene aggiornata dopo aver memorizzato il dato.

**Operazione pop (dequeue):**
- Se il puntatore head (pread) e' uguale al prossimo elemento della sequenza, si tenta di prenotare il nodo con un'operazione CAS che aggiorna atomicamente il puntatore head.
- Se l'operazione riesce, la sequenza viene aggiornata al prossimo valore di sequenza dopo aver letto il dato.

Il campo seq monotonicamente crescente serve a distinguere istanze diverse dello stesso slot nel ring buffer, risolvendo implicitamente il problema ABA per questo caso d'uso.

---

## SLIDE 42 – Lock-Free vs. Lock-Based Concurrency

**Vantaggi della programmazione lock-free:**
- Gli algoritmi lock-free garantiscono il progresso a livello di sistema anche se uno o piu' thread falliscono o vengono ritardati indefinitamente (proprieta' di progresso lock-free).
- Gli algoritmi bloccanti tradizionali possono portare a deadlock o blocking indefinito.

**Svantaggi e complessita':**
- A parte casi semplici (es. la variante di all_pairs.cpp dove il lock e' stato sostituito con fetch_add), la concorrenza lock-free e' significativamente piu' complessa di quella bloccante lock-based.
- Il problema ABA e la tecnica associata di reclamazione sicura della memoria sono aspetti importanti da considerare nelle strutture dati basate su puntatori.

**Prestazioni:**
- Le prestazioni relative degli algoritmi bloccanti vs. non-bloccanti dipendono significativamente dalla quantita' di concorrenza (e dal numero di core) e dall'algoritmo specifico usato.
- In ambienti dedicati con alta concorrenza e quindi alta contention su variabili condivise, gli algoritmi lock-free attentamente progettati sono generalmente piu' scalabili.

**Regola pratica:** usare la programmazione lock-free solo quando il profiling mostra che il lock e' il collo di bottiglia. Preferire implementazioni esistenti ben testate (es. da librerie) alle proprie implementazioni custom.

---

## SLIDE 43 – Letture Consigliate

- Capitolo 5 del libro "Parallel Programming Concept and Practice"
- "C++ Concurrency in Action" seconda edizione di Anthony Williams
  - https://www.manning.com/books/c-plus-plus-concurrency-in-action-second-edition
  - Il Capitolo 5 e' fornito come materiale aggiuntivo
- "A Primer on Memory Consistency and Cache Coherence" di Daniel J. Sorin, Mark D. Hill, e David A. Wood (documento molto dettagliato su tutti gli aspetti dei Memory Consistency Model)

**Link utili:**
- std::memory_order: https://en.cppreference.com/w/cpp/atomic/memory_order
- std::atomic_thread_fence: https://en.cppreference.com/w/cpp/atomic/atomic_thread_fence

**Paper di ricerca:**
- "Lock-free locks revised": https://dl.acm.org/doi/10.1145/3503221.3508433
- "The State-of-the-Art LCRQ Concurrent Queue Algorithm Does NOT Require CAS2": https://dl.acm.org/doi/10.1145/3572848.3577485
