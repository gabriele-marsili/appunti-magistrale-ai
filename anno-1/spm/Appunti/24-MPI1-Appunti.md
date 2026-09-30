# SPM – Lezione 24: Message Passing Interface (MPI) – Parte 1
## Appunti divisi per slide

---

## SLIDE 1 – Titolo

**SPM: Message Passing Interface (MPI) – Part I**
Anno accademico 2025-2026 – Prof. Massimo Torquati

---

## SLIDE 2 – Outline

Gli argomenti trattati nella lezione sono:

- Introduzione a MPI
- Modello di esecuzione
- Tassonomia delle comunicazioni
- Sincrono/asincrono – Simmetrico/asimmetrico
- Communicator, rank, tag
- Comunicazione simmetrica in MPI: sincrona vs. non-bloccante
- Esempi semplici

---

## SLIDE 3 – Modello Message Passing (Vista Logica)

**Struttura del modello:**
- p processi, ciascuno con il proprio spazio di indirizzamento privato.
- Il posizionamento, il partizionamento e il movimento dei dati sono responsabilita' esplicite del programmatore.
- La maggior parte delle interazioni punto-a-punto sono **two-sided** (a due lati): un processo che ha i dati li invia (es. MPI_Send) e un processo che ha bisogno dei dati li riceve (es. MPI_Recv).

**Punti di forza:**
- Modello di prestazioni relativamente semplice.
- Offre alte prestazioni co-locando i dati con la computazione.
- Modello generale (portabilita') utilizzabile su tutti i sistemi.

**Sfide:**
- Il coordinamento esplicito puo' aumentare la complessita' di programmazione.

Il modello Message Passing corrisponde ai sistemi **Distributed Memory MIMD** (Multiple Instruction, Multiple Data): ogni nodo ha la propria CPU e la propria memoria, senza accesso diretto alla memoria degli altri nodi.

---

## SLIDE 4 – Programmazione Message-Passing a Livello Utente

**Due meccanismi fondamentali sono necessari:**

1. **Un metodo per creare multipli processi**, eventualmente mappati su nodi diversi:
   - **MPMD (Multiple-Program Multiple-Data):** programmi eseguibili diversi nello stesso programma parallelo.
   - **SPMD (Single-Program Multiple-Data):** stesso eseguibile, comportamento diverso a seconda dell'identificativo del processo (rank).

2. **Un metodo per inviare e ricevere messaggi:**
   - Le operazioni di send/receive hanno semantica di completamento precisa: **bloccante** e **non-bloccante**.
   - MPI fornisce anche diverse modalita' di send.

---

## SLIDE 5 – Modello MPMD

Nel modello **MPMD (Multiple-Program Multiple-Data)**:
- Ci sono programmi separati per ciascun eseguibile.
- Diversi eseguibili partecipano alla stessa applicazione parallela.
- I processi cooperano tramite una libreria di comunicazione esplicita (es. MPI).

**Esempio con MPI: un master e due Worker:**
```
mpirun -n 1 Master : -n 2 Worker
```
Il separatore `:` specifica gruppi diversi di processi con eseguibili diversi.

Ogni eseguibile viene compilato separatamente a partire da file sorgente distinti. Il flusso e': file sorgente -> compilazione -> eseguibile -> esecuzione sui nodi allocati.

---

## SLIDE 6 – Modello SPMD

Nel modello **SPMD (Single-Program Multiple-Data)**:
- Lo stesso eseguibile viene lanciato in multipli processi.
- Flussi logici diversi vengono uniti in un unico programma.
- Istruzioni di controllo (if/switch su rank) selezionano parti diverse da eseguire per ciascun processo.
- Ogni processo ha un rank univoco e segue un percorso diverso a seconda del suo rank.

**SPMD e' il modello di esecuzione MPI piu' comune.**

MPI supporta anche le applicazioni MPMD, ma SPMD e' la norma nella pratica.

---

## SLIDE 7 – Message Passing in MPI

**MPI** e' un'interfaccia standard per programmi a message-passing.

**MPI fornisce:**
- Identificazione dei processi (rank)
- Domini di comunicazione (communicator)
- Comunicazione punto-a-punto
- Comunicazione collettiva
- Meccanismi di sincronizzazione e completamento

**MPI non e' un linguaggio:** i programmi sono scritti in C, Fortran o altri linguaggi tramite binding/wrapper. I binding C++ sono deprecati; nel corso si scrivono programmi C++ che usano l'interfaccia C di MPI. Esistono binding non ufficiali per Python, Rust, Go, C#, ecc.

---

## SLIDE 8 – Message Passing in MPI: Funzioni Principali

**Nessuno spazio di indirizzamento condiviso implicito.** Le operazioni di comunicazione e sincronizzazione sono chiamate alla libreria MPI.

**Nota:** MPI-3 ha introdotto le shared-memory windows per processi mappati sullo stesso nodo. Sono oggetti MPI espliciti, non variabili condivise ordinarie.

**Comunicazione:**
- Comunicazione punto-a-punto
- Comunicazione collettiva

**Sincronizzazione:**
- Esplicita: MPI_Barrier
- Implicita: indotta dalla comunicazione
  - Matching send/receive
  - Le operazioni collettive richiedono che tutti i processi nel communicator le chiamino

**Altre funzioni di interrogazione del runtime MPI:**
- `MPI_Comm_size`: quanti processi sono in questo communicator?
- `MPI_Comm_rank`: qual e' il mio rank?
- `MPI_Test` / `MPI_Wait`: questa comunicazione non-bloccante e' completata?

---

## SLIDE 9 – Scope dello Standard MPI

MPI e' uno standard molto ampio. In questa parte ci si concentra su:
- Avvio e finalizzazione dei processi
- Communicator e rank
- Comunicazione punto-a-punto (blocking e non-blocking send/receive)

**Molte altre funzionalita' MPI sono disponibili** (comunicazioni collettive, I/O parallelo, one-sided communication, topologie virtuali, tipi derivati, ecc.).

MPI-4.1 e' stato rilasciato nel 2023.
Documento completo: https://www.mpi-forum.org/docs/mpi-4.1/mpi41-report.pdf

---

## SLIDE 10 – Funzioni MPI Fondamentali

**I programmi semplici usano solo sei routine di libreria:**

1. `MPI_Init`: inizializza MPI.
2. `MPI_Finalize`: termina MPI.
3. `MPI_Comm_size`: determina il numero di processi in un communicator.
4. `MPI_Comm_rank`: determina il rank del processo chiamante nel communicator.
5. `MPI_Send`: invia un messaggio (bloccante).
6. `MPI_Recv`: riceve un messaggio (bloccante).

**Varianti non-bloccanti (introdotte successivamente):**
- `MPI_Isend`
- `MPI_Irecv`

---

## SLIDE 11 – Modello SPMD in MPI

Il codice seguente mostra il pattern SPMD tipico: lo stesso programma e' eseguito da tutti i P processi, ognuno sceglie un percorso di esecuzione diverso in base al proprio rank.

```cpp
MPI_Init(&argc, &argv);    // nessuna chiamata MPI prima di questo punto
int rank;
MPI_Comm_rank(MPI_COMM_WORLD, &rank);
myFunction1();             // eseguita da tutti i processi
switch (rank) {
    case 0:  foo1(); break;    // eseguita solo dal processo 0
    case 1:  foo2(); break;    // eseguita solo dal processo 1
    default: foo3(); break;    // eseguita da tutti gli altri processi
}
myFunction2();             // eseguita da tutti i processi
MPI_Finalize();            // nessuna chiamata MPI dopo questo punto
```

**Il rank e' univoco all'interno di un communicator** e varia da 0 a P-1.

---

## SLIDE 12 – Avvio e Terminazione di Programmi MPI

**`int MPI_Init(int* argc, char*** argv)`**
- Nessuna chiamata MPI prima di questa.
- Analizza la riga di comando, rimuovendo gli argomenti MPI.
- Inizializza l'ambiente MPI.

**`int MPI_Finalize()`**
- Nessuna chiamata MPI dopo questa.
- Esegue la pulizia per terminare l'ambiente MPI.

**Codici di ritorno:**
- `MPI_SUCCESS` in caso di successo.
- Altrimenti viene restituito un codice di errore `MPI_ERR_*`.
- Esempi: `MPI_ERR_COMM`, `MPI_ERR_RANK`, `MPI_ERR_TAG`, `MPI_ERR_COUNT`, ecc.

---

## SLIDE 13 – Communicator

**Communicator (MPI_Comm):**
- Definisce lo scope delle comunicazioni, ovvero il dominio di comunicazione.
- Un communicator e' composto da:
  - Un **gruppo di processi**
  - Un **contesto di comunicazione** (garantisce che messaggi di sottosistemi diversi non interferiscano)
- I processi nel gruppo possono comunicare tra loro.
- **I rank sono locali a un communicator:** lo stesso processo puo' avere rank diversi in communicator diversi.
- Viene passato come argomento a tutte le routine MPI di trasferimento messaggi.
- I processi possono appartenere a piu' domini di comunicazione (i domini possono sovrapporsi).

**`MPI_COMM_WORLD`:**
- Il communicator predefinito: tutti i processi dell'applicazione vi appartengono.
- Il suo gruppo contiene tutti i processi dell'applicazione.

**Creazione di nuovi communicator:**
- `MPI_Comm_split` / `MPI_Comm_create`: creazione dinamica di nuovi communicator per raggruppare sottoinsiemi di processi.

---

## SLIDE 14 – Funzioni di Interrogazione del Communicator

**`int MPI_Comm_size(MPI_Comm comm, int* size)`**
- Memorizza in `size` il numero di processi nel communicator `comm`.

**`int MPI_Comm_rank(MPI_Comm comm, int* rank)`**
- Memorizza in `rank` il rank del processo chiamante nel communicator `comm`.
- Se il communicator ha dimensione P, allora 0 <= rank < P.
- I rank sono locali al communicator.

**Esempio minimo "Hello World" in MPI:**
```cpp
#include <cstdio>
#include <mpi.h>
int main(int argc, char *argv[]) {
    MPI_Init(&argc, &argv);
    int size, rank;
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    std::printf("Hello from rank %d of %d\n", rank, size);
    MPI_Finalize();
}
```

File: `mpi_helloworld.cpp`

---

## SLIDE 15 – MPI sul Cluster spmcluster

Sul cluster spmcluster e' installata la implementazione **Open MPI v5.0.3**.

**Comandi utili:**
- `ompi_info`: mostra informazioni di configurazione di Open MPI.
- Documentazione Open MPI v5: https://docs.open-mpi.org/en/v5.0.x/

**Directory MPI:** `/opt/ohpc/pub/mpi/` (visibile su tutti i nodi del cluster via NFS mount).

**SLURM e MPI – due modalita' di lancio:**
```bash
# Usando il plugin PMIx (Process Management Interface for Exascale)
srun --mpi=pmix -N <nodi> -n <processi> ./myprog

# Allocazione risorse + mpirun
salloc -N <nodi> -n <processi> --time 00:01:00
mpirun -n <processi> ./myprog
```

**Compilazione:** le applicazioni MPI si compilano con `mpicc` (C) o `mpicxx` (C++).

---

## SLIDE 16 – MPI "Hello, world!": Compilazione ed Esecuzione

**Compilazione:**
```bash
# Sul nodo master
mpicxx -Wall -O3 mpi_helloworld.cpp -o mpi_helloworld

# Su un nodo del cluster usando SLURM
srun -n 1 make mpi_helloworld
```

**Esecuzione:**
```bash
salloc -N 4         # supponiamo che SLURM assegni node[01-04]

# Usando direttamente mpirun
mpirun -n 4 ./mpi_helloworld

# Usando SLURM
srun --mpi=pmix -n 4 ./mpi_helloworld
```

---

## SLIDE 17 – Invio e Ricezione di Messaggi

**`int MPI_Send(const void* buf, int count, MPI_Datatype dt, int dest, int tag, MPI_Comm comm)`**

**`int MPI_Recv(void* buf, int count, MPI_Datatype dt, int source, int tag, MPI_Comm comm, MPI_Status* status)`**

**Parametri principali:**
- `source` e `dest`: i rank dei processi nel communicator `comm`.
- `count`: il numero di **elementi** del datatype MPI `dt`, NON il numero di byte. Il numero di byte e' `count * type_size`, dove `type_size` si ottiene con `MPI_Type_size`.
- `tag`: valore intero che identifica il tipo logico del messaggio. Deve soddisfare: 0 <= tag < MPI_TAG_UB.

**Matching:** una receive fa il match con un messaggio usando communicator, source e tag.

---

## SLIDE 18 – Invio e Ricezione di Messaggi (cont.)

**Wildcards (solo lato receiver):**
- `MPI_ANY_SOURCE`: fa il match con un messaggio da qualsiasi processo nel communicator.
- `MPI_ANY_TAG`: fa il match con un messaggio con qualsiasi tag.

Quando si usano wildcards, source e tag effettivi possono essere ispezionati tramite `MPI_Status`:
- `status.MPI_SOURCE`
- `status.MPI_TAG`

**Vincoli lato receiver:**
- **No letture parziali:** una `MPI_Recv` fa il match con un messaggio completo.
- Ricevere meno di `count` elementi e' consentito (il messaggio puo' essere piu' corto del buffer).
- Se il messaggio in arrivo non rientra nel buffer di ricezione, viene generato `MPI_ERR_TRUNCATE`.

---

## SLIDE 19 – Status del Receiver

**`MPI_Status`** e' un oggetto di output riempito dalle operazioni di receive e completamento.

Per una receive completata contiene: la sorgente (`MPI_SOURCE`), il tag (`MPI_TAG`) e l'errore (`MPI_ERROR`) della comunicazione. E' utile quando si usano `MPI_ANY_SOURCE` o `MPI_ANY_TAG`.

Se non serve nessuna informazione, si puo' usare `MPI_STATUS_IGNORE` al posto dello status.

**`int MPI_Get_count(const MPI_Status* status, MPI_Datatype dt, int* count)`**
- Memorizza in `count` quanti elementi del datatype MPI `dt` sono stati ricevuti.
- Utile quando il buffer di receive e' piu' grande del messaggio in arrivo: `MPI_Recv` puo' completare anche se sono stati ricevuti meno elementi di quanti richiesti.

---

## SLIDE 20 – Alcuni Datatype MPI Primitivi

In MPI un messaggio e' descritto dalla tripla `<buffer, count, datatype>`.

Il datatype indica al runtime come interpretare la memoria puntata dal buffer. Il parametro `count` dice quanti elementi di quel datatype vengono inviati o ricevuti.

**Tabella dei principali datatype MPI primitivi:**

| MPI Datatype | Tipo C/C++ |
|---|---|
| MPI_CHAR | char |
| MPI_INT | int |
| MPI_LONG | long |
| MPI_LONG_LONG_INT | long long int |
| MPI_UNSIGNED | unsigned int |
| MPI_FLOAT | float |
| MPI_DOUBLE | double |
| MPI_LONG_DOUBLE | long double |
| MPI_BYTE | raw byte |

**Per array contigui** di valori C/C++ primitivi, i datatype MPI predefiniti sono sufficienti. Per struct, matrici memorizzate per colonne, halo, sottoarray o regioni di memoria non contigue, MPI fornisce i **derived datatypes** (tipi derivati) costruibili tramite specifiche funzioni MPI.

`MPI_BYTE` e' per byte grezzi non interpretati, non per dati strutturati portabili.

---

## SLIDE 21 – Un Programma Semplice

La slide mostra un programma MPI semplice con send e receive: il processo 0 invia un messaggio al processo 1, che lo riceve e lo stampa.

Il pattern fondamentale e' sempre lo stesso: un processo chiama `MPI_Send` con il rank del destinatario, l'altro chiama `MPI_Recv` con il rank del mittente (o `MPI_ANY_SOURCE`). Il matching avviene per communicator, source e tag.

File: `mpi_sendrecv.cpp`

---

## SLIDE 22 – Tag MPI

Un **tag** e' un'etichetta intera allegata a un messaggio.

**Scopo dei tag:** distinguere diversi tipi logici di messaggi (es. dati, messaggi di controllo, segnali di terminazione).

Una receive fa il match con i messaggi usando communicator, source e tag. Se un messaggio ricevuto non fa il match con il tag richiesto, rimane in attesa (pending) e potra' essere abbinato da una successiva `MPI_Recv`.

**Esempio di utilizzo con tag distinti:**
```cpp
const int DATA_TAG = 0;
const int EOS_TAG  = 1;   // End-Of-Stream

MPI_Send(buffer, count, MPI_INT, dest, DATA_TAG, MPI_COMM_WORLD);
MPI_Send(nullptr, 0, MPI_BYTE, dest, EOS_TAG, MPI_COMM_WORLD);
```

Il receiver puo' selezionare il tipo di messaggio atteso specificando il tag, oppure usare `MPI_ANY_TAG` per ricevere qualsiasi messaggio.

---

## SLIDE 23 – Tassonomia delle Comunicazioni

**Pattern di comunicazione:**
- **Comunicazione punto-a-punto:** un sender, un receiver.
- **Comunicazione collettiva:** tutti i processi in un communicator partecipano. Alcune collettive eseguono anche elaborazione dei dati (es. `MPI_Reduce`).

**Sincronia con il peer di comunicazione:**
- **Comunicazione sincrona (rendezvous):** il sender e il receiver si incontrano; il sender si blocca finche' il receiver e' pronto.
- **Comunicazione asincrona:** il sender puo' completare senza aspettare che il receiver inizi la receive corrispondente.

**Semantica di completamento:**
- **Bloccante:** la chiamata ritorna solo dopo che l'operazione locale e' completata. Il buffer del messaggio puo' essere immediatamente riutilizzato.
- **Non-bloccante:** la chiamata avvia l'operazione e ritorna subito. Il completamento deve essere verificato prima di accedere al buffer del messaggio.

**Attenzione:** Sincrono != Bloccante, Asincrono != Non-bloccante.

**Esempi MPI:**
- `MPI_Ssend`: bloccante + sincrono
- `MPI_Issend`: non-bloccante + sincrono
- `MPI_Send`: bloccante standard send
- `MPI_Isend`: non-bloccante standard send

---

## SLIDE 24 – Send Sincrona: Semantica Rendezvous

**Primitiva sincrona `ssend`:**
- Ritorna quando il trasferimento del messaggio e' completato.
- `ssend` ha semantica di **rendezvous**: il send non puo' completare finche' la receive corrispondente non e' stata avviata.
- Il buffer puo' essere riutilizzato in sicurezza solo quando la chiamata ritorna.
- In MPI, `ssend` e' implementata da `MPI_Ssend`.

**Diagramma temporale:**
- Il Processo 1 chiama `ssend(&x, 2)` e si blocca.
- Il Processo 2 chiama `recv(&y, 1)`.
- Solo quando la receive e' avviata, il trasferimento dei dati procede e il send puo' completare.

**`ssend` esegue due azioni:** trasferisce dati e sincronizza i processi.

---

## SLIDE 25 – Possibile Protocollo Rendezvous per ssend

**Una possibile implementazione del rendezvous:**
1. Il sender annuncia che vuole inviare (Request to send).
2. Il receiver ha gia' postato o posta la receive corrispondente.
3. Il trasferimento dei dati puo' procedere.
4. Il sender completa solo dopo che il receiver ha partecipato.

**Due scenari possibili:**
- **Scenario A:** il sender arriva primo, invia la richiesta, si sospende, aspetta l'ACK del receiver, poi avviene il trasferimento.
- **Scenario B:** il receiver arriva primo (ha gia' postato la receive), il sender trova il receiver gia' pronto e il trasferimento puo' avvenire immediatamente.

In entrambi i casi, il sender completa solo dopo che il receiver ha partecipato alla comunicazione.

---

## SLIDE 26 – Send Asincrona: Comportamento Bufferizzato

**Nella send asincrona:**
- Il sender puo' completare senza aspettare che il receiver inizi la receive corrispondente.
- Questo richiede tipicamente **buffering**: i dati vengono copiati in un buffer interno di MPI.
- Non c'e' sincronizzazione rendezvous con il receiver.
- Il sender puo' continuare, ma il buffering interno e' finito.

**Comportamento di `MPI_Send`:**
- `MPI_Send` **puo'** comportarsi in questo modo per messaggi piccoli (copia nel buffer di sistema MPI), ma non e' garantito.
- Per messaggi grandi, `MPI_Send` **puo'** bloccare finche' la `MPI_Recv` corrispondente non e' postata (cioe' usa il protocollo rendezvous).
- Questo e' ancora conforme alla semantica di blocking send: quando ritorna, il buffer di send puo' essere riutilizzato in sicurezza.

**Regola pratica:** non fare assunzioni su quale protocollo usa `MPI_Send` internamente. La soglia tra bufferizzazione e rendezvous dipende dall'implementazione MPI e puo' variare.

---

## SLIDE 27 – Definizioni MPI di Bloccante e Non-Bloccante

**Bloccante (Blocking):**
- Una chiamata bloccante ritorna dopo che la parte locale dell'operazione e' completata.
- Per una blocking send: il buffer di send puo' essere riutilizzato in sicurezza quando la chiamata ritorna.
- Questo NON implica che la receive corrispondente sia completata.
- Con capacita' di buffer limitata, una blocking send puo' comportarsi come una synchronous send.

**Non-bloccante (Non-blocking):**
- Una chiamata non-bloccante ritorna immediatamente dopo che l'operazione e' stata avviata.
- L'operazione rimane pending e puo' procedere mentre il programma continua.
- Il buffer utente coinvolto in un'operazione non-bloccante NON deve essere acceduto in modo non sicuro prima del completamento.
- **Non modificare (o liberare) il buffer utente finche' non si sa che l'operazione e' completata!**
- Spetta al programmatore garantire questo (es. usando `MPI_Wait`/`MPI_Test` o le loro varianti).
- Le chiamate non-bloccanti permettono di sovrapporre comunicazione e computazione.

---

## SLIDE 28 – Comunicazione Bloccante e Deadlock

**Esempio di deadlock con blocking send:**
```cpp
if (myrank == 0) {
    MPI_Send(buf, count, MPI_INT, 1, 100, MPI_COMM_WORLD);
    MPI_Recv(buf, count, MPI_INT, 1, 100, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
} else if (myrank == 1) {
    MPI_Send(buf, count, MPI_INT, 0, 100, MPI_COMM_WORLD);
    MPI_Recv(buf, count, MPI_INT, 0, 100, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
}
```

Se `MPI_Send` si blocca finche' la receive corrispondente non e' postata (o finche' non c'e' abbastanza buffering), si ha deadlock: entrambi i processi sono bloccati sulla send, aspettando che l'altro esegua la receive.

**Altro caso classico:** invio di dati al vicino di destra su un ring (lo stesso problema dei "Filosofi a cena" di Dijkstra).

**Soluzione – rompere l'attesa circolare:**
```cpp
if (myrank % 2 == 1) {
    MPI_Send(...);
    MPI_Recv(...);
} else {
    MPI_Recv(...);
    MPI_Send(...);
}
```
I processi con rank dispari inviano prima e poi ricevono; quelli con rank pari ricevono prima e poi inviano. In questo modo non c'e' attesa circolare.

---

## SLIDE 29 – Perche' MPI_Send puo' Bloccare?

`MPI_Send` ritorna quando e' sicuro riutilizzare il buffer dell'applicazione. Questo puo' avvenire perche':
- Il messaggio e' stato copiato in un buffer MPI/di sistema, oppure
- La receive corrispondente e' stata postata e il trasferimento dati puo' procedere.

Lo standard MPI permette l'uso di un buffer di sistema ma non lo richiede necessariamente.

**Per messaggi grandi:** `MPI_Send` puo' usare un protocollo rendezvous.

**Scenario di deadlock con due send simultanee:**
- P0 esegue `MPI_Send` verso P1.
- P1 esegue `MPI_Send` verso P0.
- Entrambe le send aspettano che l'altra parte esegua la receive.
- Nessuna delle due receive viene mai eseguita: deadlock.

I buffer dell'applicazione di entrambi i processi sono "bloccati" in attesa che avvenga il matching.

---

## SLIDE 30 – Send/Receive Non-Bloccanti

**`int MPI_Isend(const void* buf, int count, MPI_Datatype dt, int dest, int tag, MPI_Comm comm, MPI_Request* req)`**

**`int MPI_Irecv(void* buf, int count, MPI_Datatype dt, int source, int tag, MPI_Comm comm, MPI_Request* req)`**

**Semantica:**
- L'elaborazione continua immediatamente senza attendere il completamento dell'operazione.
- Viene restituito un **request handle** (`req`) che deve essere usato per testare o attendere il completamento.
- Chiamando `MPI_Wait()` o `MPI_Test()` (o le loro varianti `*all`), si puo' determinare quando l'operazione e' completata. Solo allora e' sicuro riutilizzare (o liberare) il buffer del messaggio.
- E' possibile mescolare chiamate non-bloccanti e bloccanti.
- Esempi: `MPI_Isend()` + `MPI_Recv()`, oppure `MPI_Send()` + `MPI_Irecv()`.

**Oltre ad evitare deadlock**, la comunicazione non-bloccante viene tipicamente usata per sovrapporre computazione e comunicazione.

---

## SLIDE 31 – Attesa e Verifica di Chiamate Non-Bloccanti

**`int MPI_Wait(MPI_Request* req, MPI_Status* status)`**
- Blocca finche' un'operazione di send o receive non-bloccante e' completata.
- Dopo che `MPI_Wait` ritorna, il request diventa `MPI_REQUEST_NULL`.
- Usare `MPI_STATUS_IGNORE` se le informazioni di status non sono necessarie.
- Per attendere piu' operazioni non-bloccanti: `MPI_Waitany()`, `MPI_Waitall()`, `MPI_Waitsome()`.

**`int MPI_Test(MPI_Request* req, int* flag, MPI_Status* status)`**
- Testa se una send o receive non-bloccante e' completata (non bloccante).
- `flag` viene impostato a 1 se l'operazione e' completata, 0 altrimenti.
- Se `flag == 1`, l'operazione e' completata e il request diventa `MPI_REQUEST_NULL`.
- Per controllare piu' operazioni non-bloccanti: `MPI_Testany()`, `MPI_Testall()`, `MPI_Testsome()`.

**Differenza chiave:** `MPI_Wait` blocca il processo fino al completamento; `MPI_Test` fa un controllo non-bloccante (polling) e ritorna immediatamente con il risultato.

---

## SLIDE 32 – Proprieta' MPI di Non-Overtaking: Ordine di Matching

**Regola di non-overtaking:** se un sender single-threaded invia due messaggi usando la stessa destinazione, tag e communicator, e il receiver posta due `MPI_Irecv` con la stessa sorgente, communicator e tag:
- msg1 fa il match con req1
- msg2 fa il match con req2
- msg2 **non puo' superare** msg1 nel matching dei messaggi.

**Tuttavia, l'ordine di completamento NON e' garantito:**
- Con `MPI_Waitany`, req2 puo' completare prima di req1.

**Riassunto:**
- **L'ordine di matching dei messaggi e' garantito** (FIFO per stesso source/dest/tag).
- **L'ordine di completamento dei request NON e' garantito.**

Questa distinzione e' importante: il fatto che msg1 sia "in volo" prima di msg2 non significa che la sua receive locale completi prima.

---

## SLIDE 33 – Scambio di Messaggi: MPI_Sendrecv

```cpp
int MPI_Sendrecv(const void* sndbuf, int sndcount, MPI_Datatype snddt, int dest,   int sndtag,
                       void* rcvbuf, int rcvcount, MPI_Datatype rcvdt, int source, int rcvtag,
                 MPI_Comm comm, MPI_Status* status)
```

- **`MPI_Sendrecv` e' bloccante:** ritorna quando sia la parte di send che la parte di receive sono completate localmente.

**Perche' usare Sendrecv?** Per evitare il deadlock. MPI internamente schedula le parti di send e receive in modo che i pattern comuni di scambio a coppie evitino il deadlock senza che il programmatore debba gestirlo manualmente.

**Caso d'uso tipico:** scambio di dati con un vicino in ring, stencil, e **halo exchange** (scambio dei bordi delle partizioni nelle computazioni su griglia distribuita).

**`MPI_Sendrecv_replace`:** usa lo stesso buffer sia per send che per receive (utile quando si vuole inviare e poi sovrascrivere con i dati ricevuti).

---

## SLIDE 34 – Esempio: Ping-Pong su un Ring Ordinato

**Pattern:** ogni processo invia PING in senso orario e PONG in senso antiorario usando comunicazione punto-a-punto non-bloccante.

- Ogni processo ha un vicino a destra (`right = (rank+1) % size`) e uno a sinistra (`left = (rank-1+size) % size`).
- Usa `MPI_Isend` e `MPI_Irecv` per avviare le comunicazioni, poi `MPI_Wait` per aspettare il completamento.
- L'uso delle operazioni non-bloccanti permette di avviare le comunicazioni nelle due direzioni in parallelo senza rischio di deadlock.

File: `mpi_pingpong_nb.cpp`

---

## SLIDE 35 – Esempio: Integrazione Numerica

**Problema:** calcolare pi greco tramite integrazione numerica con la regola dei trapezi.

**Parallelizzazione MPI:**
- L'intervallo [0,1] viene suddiviso in P sotto-intervalli, dove P e' il numero di processi.
- Ogni processo calcola l'area del sotto-intervallo locale.
- Ogni processo invia il risultato parziale al master (processo con rank 0).
- Il master somma tutti i risultati parziali per ottenere il risultato finale.

**Pattern:** Map-Reduce semplice: computazione locale + riduzione manuale sul rank 0.

Questo e' uno dei pattern fondamentali nella programmazione MPI: ogni processo lavora su una partizione dei dati e i risultati parziali vengono aggregati su un processo master.

File: `mpi_trapezoid.cpp`

---

## SLIDE 36 – Esempio: Master-Workers

**Scenario:**
- I client (Worker, rank 1..P-1) inviano un numero casuale di richieste con tag `msg_tag` al Server, poi un messaggio finale con tag `eos_tag` e payload zero per segnalare l'End-Of-Stream (EOS).
- Il Server (rank 0) accetta richieste da `MPI_ANY_SOURCE` e con `MPI_ANY_TAG` finche' tutti i Worker hanno inviato il messaggio EOS.
- Il Server usa `status.MPI_SOURCE` e `status.MPI_TAG` per identificare il mittente e il tipo di messaggio.
- Il Server termina dopo aver ricevuto un EOS da ciascun Worker.

**Punti chiave del pattern:**
- L'uso di `MPI_ANY_SOURCE` e `MPI_ANY_TAG` rende il server flessibile: risponde al primo Worker disponibile, indipendentemente dall'ordine.
- Il tag EOS e' un segnale di terminazione esplicito: il server non puo' sapere quante richieste arriveranno, ma sa che ogni Worker mandera' esattamente un EOS.

File: `mpi_masterWorkers.cpp`

---

## SLIDE 37 – Double Buffering

Il **double buffering** e' una tecnica per nascondere la latenza di comunicazione e aumentare il throughput. E' utile principalmente per dati di dimensione piccola/media poiche' richiede piu' memoria.

**Idea:** usare due buffer di comunicazione per ogni peer vicino (bufA, bufB).
- Mentre bufA e' "in volo" (in fase di trasmissione/ricezione), bufB puo' essere usato per la computazione.
- Al completamento, i buffer vengono scambiati (swap), cosi' la comunicazione del round successivo si sovrappone alla computazione del round corrente.

**Pseudocodice:**
```
MPI_Irecv(rbufA, rA);        // avvia receive su buffer A
MPI_Irecv(rbufB, rB);        // avvia receive su buffer B
while (true) {
    MPI_Wait(rA, ...);         // aspetta completamento receive
    pw = rbufA;                // buffer corrente di lavoro
    swap(rbufA, rbufB);        // scambia buffer
    MPI_Irecv(rbufA, rA);     // riposta la receive
    do_work(pw);               // lavora sui dati ricevuti
    MPI_Wait(sA, ...);         // aspetta send precedente
    copy(pw, sbufA);
    MPI_Isend(sbufA, sA);     // invia
    swap(sbufA, sbufB);        // scambia send buffer
}
```

Il risultato e' che la computazione (`do_work`) e la comunicazione (`MPI_Isend`/`MPI_Irecv`) si sovrappongono, riducendo il tempo di attesa.

---

## SLIDE 38 – Farm Skeleton in MPI

**Pattern:** implementazione di uno skeleton Farm classico (Emitter-Workers-Collector) usando comunicazioni asincrone e **double buffering** in tutti gli stadi per massimizzare la sovrapposizione di computazione e comunicazione.

**Struttura:**
- **Emitter (rank 0):** distribuisce i task ai Worker su richiesta (politica on-demand).
- **Workers (rank 1..k-2):** ricevono task, li elaborano, inviano il risultato al Collector.
- **Collector (rank k-1):** raccoglie i risultati dai Worker.

**Possible extension:** all'interno di un Worker, si puo' usare OpenMP o CUDA per ridurre il service time del Worker (ibridazione MPI + OpenMP o MPI + CUDA).

**Nota importante:** se piu' thread chiamano routine MPI, usare `MPI_Init_thread` al posto di `MPI_Init` per inizializzare MPI con il livello di thread support appropriato.

File: `mpi_farm-doublebuffering.cpp`

---

## SLIDE 39 – Letture Consigliate

- Capitolo 9 del libro "Parallel Programming Concepts and Practice"
- MPI: A Message-Passing Interface Standard Version 4.1: https://www.mpi-forum.org/docs/mpi-4.1/mpi41-report.pdf
- Documentazione Open MPI: https://docs.open-mpi.org/en/v5.0.x/
- Tutorial MPI: https://hpc-tutorials.llnl.gov/mpi/
- OSU micro-benchmarks (benchmark per misurare prestazioni MPI): https://mvapich.cse.ohio-state.edu/benchmarks/
  - I benchmark C sono installati in `/opt/ohpc/pub/mpi/osu-7.4/` sul cluster spmcluster.
