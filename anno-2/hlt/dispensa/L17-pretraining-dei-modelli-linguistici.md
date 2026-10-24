# L17 · Pretraining dei modelli linguistici

*Pretraining Language Models* · 20/10/2026 · Claudio Gallicchio · lettura: J&M cap. 7, §7.7-7.8

[Versione interattiva sul sito](https://gabriele-marsili.github.io/appunti-magistrale-ai/anno-2/hlt/sito/#L17) · [Indice della dispensa](README.md)

Lezione sul **pretraining** (J&M §7.7-7.8 e cap. 1): come si fissano i pesi del transformer. L'obiettivo è **self-supervised**: predire il token successivo con la **cross-entropy loss** $-\log\hat y_t[w_{t+1}]$, con **teacher forcing**, tutte le posizioni in parallelo grazie alla maschera causale e documenti impacchettati nella finestra. Molti task diventano **generazione condizionata** da un prompt, ma il risultato è un **base model** che non segue istruzioni. Poi i **dati** (Common Crawl, The Pile, deduplicazione e filtri, copyright, privacy, skew), i numeri dei modelli reali con il conto $12Ld^2 + |V|d$ e la **KV cache** (4,7 MB per token in GPT-3), le **scaling law** di Kaplan, $C\approx6ND$ e la regola di **Chinchilla** di circa 20 token per parametro, e la **valutazione**: perplexity = exp(cross-entropy media), benchmark, **contaminazione**, giudici e metriche proxy con la legge di Goodhart. In apertura le scadenze del progetto di gruppo. Tutti i numeri delle slide tornano: nessuna correzione. Con il notebook (un piccolo transformer preaddestrato in numpy, nessun bug) e la scheda di 12 esercizi.

## Indice

- [Progetto di gruppo](#progetto-di-gruppo)
- [Apertura](#apertura)
- [L'obiettivo di training](#l-obiettivo-di-training)
- [Task come generazione](#task-come-generazione)
- [Dati di pretraining](#dati-di-pretraining)
- [Modelli e KV cache](#modelli-e-kv-cache)
- [Scaling law](#scaling-law)
- [Valutazione](#valutazione)
- [Notebook](#notebook)
- [Studio ed esercizi](#studio-ed-esercizi)

## Progetto di gruppo

<a id="p-2"></a>

### Slide 2 · Gruppi del progetto: la bozza

Slide organizzativa. Il file condiviso dei gruppi (`Groups 2026.xlsx`, raggiungibile dal QR code) contiene una **bozza**: 55 studenti frequentanti divisi in **12 gruppi da 4 o 5**.

- **Scambi**: due studenti possono scambiarsi il numero di gruppo se sono d'accordo entrambi; nessun gruppo può superare 5 persone.
- Ogni gruppo scrive `yes` accanto al suo **corresponding author**, la persona che terrà i contatti con i docenti (sarà lei a mandare la proposta del 2 novembre).
- **Scadenza: martedì 27 ottobre**, poi i gruppi sono definitivi.
- Chi frequenta ma non compare nel file deve scrivere al docente.

Cosa fare: controllare di essere nel gruppo giusto (Octech è nel gruppo 5) e concordare entro il 27 chi fa da corresponding author.

<a id="p-3"></a>

### Slide 3 · La strada verso dicembre

La linea del tempo del progetto (date indicative, tutte nel 2026):

| Data | Cosa succede |
| --- | --- |
| 20 ott (mar) | bozza dei gruppi |
| 23 ott (ven) | lista dei temi suggeriti, assegnati in via provvisoria ai gruppi |
| 27 ott (mar) | gruppi definitivi, con corresponding author |
| 29 ott (gio) | scelta definitiva del tema |
| 2 nov (lun) | **proposta iniziale** del progetto (evidenziata in rosso) |
| 11 e 12 nov | presentazioni, primo giro |
| 24-26 nov | presentazioni, secondo giro |
| 3 dic (gio) | poster session, codice e report |

Il consiglio della slide è il punto pratico: **cominciare a lavorare subito dopo la proposta**, perché il secondo giro (fine novembre) chiede già risultati semi-finali. Fra la proposta e il secondo giro ci sono poco più di tre settimane.

<a id="p-4"></a>

### Slide 4 · I temi del progetto

Come funziona l'assegnazione dei temi:

- **23 ottobre**: viene pubblicata una lista di temi suggeriti, ciascuno assegnato in via provvisoria a un gruppo.
- Un tema fissa l'**applicazione o il task**; dataset, modelli e dominio li sceglie il gruppo.
- Il gruppo può scambiare il tema con un altro gruppo, sceglierne un altro dalla lista, oppure **proporne uno suo**, purché nello stesso spirito e motivato.
- **29 ottobre**: ogni gruppo conferma il tema definitivo nel file condiviso.

Alcuni metodi necessari (fine-tuning, LoRA, prompting) arrivano nelle prossime lezioni: per ora basta farsi un'idea. Per il gruppo 5 il tema provvisorio è *Hate Speech and Offensive Language Detection*: conviene già guardare quali dataset esistono e quale encoder preaddestrato usare.

<a id="p-5"></a>

### Slide 5 · La proposta iniziale: lunedì 2 novembre

La proposta iniziale va consegnata **lunedì 2 novembre** (il giorno dei morti, da cui la candela e la battuta: il progetto deve essere *alive and kicking*).

- **Chi**: il corresponding author del gruppo.
- **A chi**: entrambi i docenti, `claudio.gallicchio@unipi.it` e `andrea.ceni@unipi.it`.
- **Oggetto**, nel formato esatto: `[HLT 2026] Initial Project Proposal - <project title> - Group <n>`.

Rispettare il formato dell'oggetto serve ai docenti per ritrovare e smistare le mail di 12 gruppi; per il gruppo 5 sarà `... - Group 5`.

<a id="p-6"></a>

### Slide 6 · Che cosa contiene la proposta

Una mail breve, poche righe per voce, con sei voci:

1. **Selected project**: il titolo del tema;
2. **Our idea**: dominio, obiettivo, vincoli o casi d'uso;
3. **Dataset**: nome, o un'alternativa (anche sintetica);
4. **Models and tools**: modello preaddestrato, libreria, tipo di fine-tuning;
5. **References**: uno o più articoli da cui partire;
6. **Group members**: nomi ed email.

È un punto di partenza, non un impegno: i piani possono cambiare durante il progetto, e i docenti rispondono con commenti o suggerimenti se serve (*a proposal is not a tombstone*). Conviene comunque arrivarci con un dataset concreto e un modello di partenza già individuati, perché sono le voci che determinano il lavoro di novembre.

<a id="p-7"></a>

### Slide 7 · Presentazioni e poster session

Tre momenti di valutazione, tutti con date indicative:

|  | Quando | Durata | Contenuto |
| --- | --- | --- | --- |
| **Round 1** | 11 e 12 nov | 10 min + 5 di domande | stato dell'arte, idee e piani |
| **Round 2** | 24-26 nov | 15 min + 8 di domande | il progetto, risultati semi-finali |
| **Poster session** | gio 3 dic |  | risultati finali, codice e report |

Regole: ogni presentazione è tenuta da **almeno due membri** del gruppo e **ognuno presenta almeno una volta**; il progetto è valutato **collettivamente** (un voto di gruppo). Con 4-5 persone e due round, conviene decidere presto chi presenta quando.

<a id="p-8"></a>

### Slide 8 · Chi presenta quando

Il calendario delle presentazioni per gruppo:

| Round | Giorno | Ora e aula | Gruppi |
| --- | --- | --- | --- |
| 1 | mercoledì 11 novembre | 14-16, FIB C1 | 1-6 |
| 1 | giovedì 12 novembre | 14-16, FIB E | 7-12 |
| 2 | martedì 24 novembre | 11-13, FIB C | 1-4 |
| 2 | mercoledì 25 novembre | 14-16, FIB C1 | 5-8 |
| 2 | giovedì 26 novembre | 14-16, FIB E | 9-12 |

Poi la poster session con tutti i gruppi, giovedì 3 dicembre. Per il **gruppo 5**: round 1 **mercoledì 11 novembre, 14-16, FIB C1**; round 2 **mercoledì 25 novembre, 14-16, FIB C1**. Tutte le date sono indicative (i giorni della settimana corrispondono al calendario 2026).

## Apertura

<a id="p-1"></a>

### Slide 1 · Pretraining dei modelli linguistici

Lezione 17, di Claudio Gallicchio (20 ottobre 2026). Il sottotitolo è il programma: l'**obiettivo di training**, i **dati**, la **scala** e la **valutazione** del pretraining.

Nelle due lezioni precedenti si è costruito il transformer pezzo per pezzo (attenzione, blocchi, embedding di posizione, testa di language modeling, decoding), ma con pesi qualsiasi. Qui si risponde alla domanda che restava aperta: **come si fissano i pesi**. La risposta è una sola idea, predire il token successivo minimizzando la cross-entropy, applicata a trilioni di token; il resto della lezione spiega da dove vengono quei token, quanto deve essere grande il modello e come si misura il risultato. Le prime slide invece riguardano il progetto di gruppo.

<a id="p-9"></a>

### Slide 9 · Indice

Sette parti:

1. **dove siamo**: il pretraining come primo dei quattro stadi di training;
2. **l'obiettivo di training**: predire il token successivo con la cross-entropy, teacher forcing, tutte le posizioni in parallelo;
3. **i task come generazione**: perché un solo obiettivo basta per molti task;
4. **i dati di pretraining**: da dove viene il testo, come si filtra, questioni etiche e legali;
5. **modelli e KV cache**: qualche numero sui modelli reali, il conto dei parametri, la cache di key e value;
6. **scaling law**: come la loss scende con parametri, dati e calcolo;
7. **valutazione**: perplexity, benchmark, giudici umani o LLM, metriche proxy.

<a id="p-10"></a>

### Slide 10 · Riferimento: J&M capitoli 7 e 1

Letture:

- **Capitolo 7**, §**7.7** *Pretraining Transformer LLMs* (con §7.7.1 sulla perplexity) e §**7.8** *Current models and some numbers*: pp. 201-205 nella numerazione stampata del draft di agosto 2026.
- **Capitolo 1**: §1.1 (che cosa vuol dire *large*, scaling law, p. 7), §1.6.1 (pretraining come Shannon game, dati, filtri, questioni etiche, pp. 16-17), §1.9 (valutazione: accuratezza, benchmark, contaminazione, giudici, metriche proxy, pp. 25-29).

Le parti più calcolabili (loss, perplexity, parametri, KV cache) stanno nel cap. 7; le parti discorsive (dati, valutazione) nel cap. 1. Le scaling law di Kaplan et al. (2020) e i numeri di Chinchilla sono un'aggiunta della lezione rispetto al libro, che riporta solo $N_{opt}\propto C^{1/2}$, $D_{opt}\propto C^{1/2}$.

<a id="p-11"></a>

### Slide 11 · Dove siamo: i quattro stadi

La figura (dal cap. 1 del libro) mostra la catena dei **quattro stadi di training** di un LLM moderno, ciascuno con i suoi dati in alto e il modello prodotto in basso:

1. **Pretraining** (rosso), su una pila di libri, *pretraining data*: produce il *Pretrained LLM*;
2. **Instruction tuning** (verde), su coppie istruzione-risposta (sentiment di una frase, riassunto, traduzione): produce l'*Instruction Tuned LLM*;
3. **Preference alignment** (viola), su dati di preferenza: alla domanda su come appropriarsi di denaro, la risposta che rifiuta ha il pollice in su, quella che aiuta il pollice in giù;
4. **RL with verifiable rewards** (giallo), su problemi con risposta controllabile (un problema di pizze con calcolo verificato): produce il *Final Aligned LLM*.

Le frecce oblique dicono che ogni stadio parte dal modello del precedente. È lo schema già visto nella [scheda 56 della L1](L01-introduzione-al-corso.md#p-56).

<a id="p-12"></a>

### Slide 12 · Oggi: lo stadio 1

La stessa figura con un riquadro attorno al solo **stadio 1**: oggi si parla di **pretraining** su corpora di testo enormi. Gli altri stadi (post-training) sono le prossime lezioni.

Il risultato del pretraining è un **base model** (modello base, *pretrained LLM*): un modello che sa predire il token successivo e quindi generare testo, ma che non è stato addestrato a seguire istruzioni né a comportarsi da assistente. Tutto quello che sa (grammatica, fatti, stili, un po' di ragionamento) lo ha imparato come effetto collaterale della predizione del token successivo. La differenza fra base model e modello che segue istruzioni torna nella [scheda 29](L17-pretraining-dei-modelli-linguistici.md#p-29).

<a id="p-13"></a>

### Slide 13 · Il modello che abbiamo costruito

Riepilogo di ciò che c'è già e di ciò che manca.

- **Il modello**: embedding dei token e delle posizioni, una pila di transformer block, la testa di language modeling ([L14](L14-transformer-l-attenzione.md#p-8)). Output: una distribuzione sul token successivo.
- **I pesi**: la matrice di embedding $E$, le matrici di attenzione ($W^Q, W^K, W^V, W^O$) e del feedforward, i parametri delle layer norm. Da milioni a miliardi di numeri, che **prima del training sono casuali**: un modello così genera parole a caso.
- **Oggi**: come fissarli. Si addestra il modello a predire il token successivo, su trilioni di token.

Il meccanismo di apprendimento non è nuovo: è la discesa del gradiente con backpropagation della [L13](L13-reti-neurali.md#p-55), con Adam e uno schedule del learning rate ([schede 61-62 della L13](L13-reti-neurali.md#p-61)). Nuovi sono l'obiettivo applicato a testo grezzo e la scala.

<a id="p-14"></a>

### Slide 14 · Oggi: dal testo a un modello addestrato

La mappa della lezione in sei passi, ciascuno con la sua idea:

1. **obiettivo di training**: predire il token successivo, cross-entropy loss;
2. **task come generazione**: un obiettivo, molti task;
3. **dati di pretraining**: crawl del web e testo curato, filtrati;
4. **modelli e KV cache**: qualche numero, e il riuso di key e value;
5. **scaling law**: la loss in funzione di dimensione, dati e calcolo;
6. **valutazione**: perplexity, benchmark, giudici.

Frase da ricordare: **un obiettivo semplice, applicato a una quantità enorme di testo**. Il risultato dipende dai dati, dalla scala e da come lo si misura: sono i tre temi della seconda parte.

## L'obiettivo di training

<a id="p-15"></a>
**Slide 15 · L'obiettivo di training** — Predire il token successivo: la loss, il teacher forcing, il calcolo in parallelo.

<a id="p-16"></a>

### Slide 16 · Training self-supervised

Frase chiave: **la sequenza naturale dei token è la sua stessa supervisione**.

- **Shannon game**: si dà al modello testo corrente e a ogni token gli si chiede di predire il successivo, come nel gioco in cui una persona indovina un testo lettera per lettera (J&M §1.2.2).
- **La correzione**: gli si dice qual era il token giusto e si aggiornano i pesi per renderlo più probabile.
- **Nessuna etichetta**: non serve annotare niente, il token successivo è già nel testo.

Per questo si parla di apprendimento **self-supervised**: formalmente è apprendimento supervisionato (input = contesto, target = token successivo, come nella [massima verosimiglianza condizionata della L6](L06-regressione-logistica.md#p-37)), ma i target si ricavano gratis dal testo. Conseguenza decisiva: **ogni token del corpus è un esempio di training**, e un corpus di 15 trilioni di token dà 15 trilioni di esempi senza alcun costo di annotazione.

<a id="p-17"></a>

### Slide 17 · La cross-entropy loss

La loss alla posizione $t$ confronta la distribuzione predetta $\hat y_t$ (un vettore di $|V|$ probabilità) con quella corretta $y_t$:

$$L_{CE}(\hat y_t, y_t) = -\sum_{w\in V} y_t[w]\,\log \hat y_t[w]$$

Nel language modeling $y_t$ è **one-hot**: vale 1 sul vero token successivo $w_{t+1}$ e 0 altrove. Tutti i termini della somma tranne uno sono moltiplicati per zero, e resta

$$L_{CE}(\hat y_t, y_t) = -\log \hat y_t[w_{t+1}].$$

Quindi la loss è **meno il logaritmo della probabilità del vero token successivo**. È la stessa loss della regressione logistica ([L6](L06-regressione-logistica.md#p-38)), della multinomiale ([L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-16)) e delle reti feedforward ([L13](L13-reti-neurali.md#p-38)): un classificatore con $|V|$ classi, una per token del vocabolario. Minimizzarla equivale a massimizzare la log-verosimiglianza del testo (MLE condizionata). Il logaritmo è naturale: la loss è in **nat**.

<a id="p-18"></a>

### Slide 18 · La loss a mano

La distribuzione dopo `So long and thanks for` (l'esempio ricorrente del libro, Fig. 1.2), ristretta a quattro candidati: *all* 0,44, *the* 0,33, *your* 0,15, *that* 0,08 (sommano a 1). Ogni riga dice quale sarebbe la loss **se** quel token fosse il vero successivo:

| vero token | $\hat y$ | $-\ln \hat y$ |
| --- | --- | --- |
| all | 0,44 | 0,82 |
| the | 0,33 | 1,11 |
| your | 0,15 | 1,90 |
| that | 0,08 | 2,53 |

Più è bassa la probabilità data al token giusto, più la loss è alta. Agli estremi: probabilità 1, loss 0; probabilità vicina a 0, loss enorme ($-\ln 0{,}001 = 6{,}9$, $-\ln 10^{-6} = 13{,}8$). La loss quindi punisce molto un modello *sicuro e sbagliato*, poco uno incerto.

> **Da saper fare: Verifica dei conti**
>
> $-\ln 0{,}44 = 0{,}821$; $-\ln 0{,}33 = 1{,}109$; $-\ln 0{,}15 = 1{,}897$; $-\ln 0{,}08 = 2{,}526$. Arrotondati a due cifre danno esattamente la tabella. Riferimento utile: un modello che dà probabilità uniforme su $|V|$ token ha loss $\ln|V|$ a ogni posizione ($\ln 50\,000 = 10{,}82$): è la loss tipica all'inizio del training.

<a id="p-19"></a>

### Slide 19 · Teacher forcing

Frase chiave: **il modello riceve sempre la storia corretta**.

Alla posizione $t$ il contesto è `So long and thanks for`; il modello scommette su *the*, ma il vero token è *all*. La loss si calcola confrontando la previsione con *all*, e alla posizione $t+1$ l'input è `So long and thanks for all`: il testo vero, non quello che il modello avrebbe generato.

Questo è il **teacher forcing**: si ignora la scelta del modello e si prosegue con il testo reale. Due motivi:

- gli errori non si accumulano: se il modello sbaglia una parola, le posizioni successive non vengono addestrate su un contesto rovinato;
- i contesti di tutte le posizioni sono noti in anticipo (sono il testo stesso), il che permette di calcolarle tutte insieme ([scheda 22](L17-pretraining-dei-modelli-linguistici.md#p-22)).

Il prezzo è una discrepanza fra training e generazione: in inferenza il modello si nutre delle proprie uscite (generazione autoregressiva), situazione che in training non vede mai (spesso chiamata *exposure bias*).

<a id="p-20"></a>

### Slide 20 · Pretraining di un LLM

La figura (Fig. 7.22 del libro): in basso gli input *So, long, and, thanks, for*; in mezzo il blocco *LLM* con una colonna per posizione; ogni colonna produce $\hat y$, la distribuzione sul token successivo; sopra, la **loss per token** $-\log y_{long}$, $-\log y_{and}$, ..., $-\log y_{all}$ confrontata con il **vero token successivo** (la riga in alto, cioè l'input spostato di una posizione). Le frecce *back prop* scendono da ogni loss dentro il modello.

- A ogni posizione: $\hat y$ e la loss $-\log\hat y$ del vero token successivo.
- Le loss vengono **retropropagate** e addestrano **tutti i pesi**, compresi gli embedding $E$.

Conseguenza: gli embedding non sono più fissati prima (come word2vec) ma imparati per essere utili a **predire le parole successive**. Con il weight tying la stessa $E$ riceve gradiente due volte: dall'input e dalla testa di language modeling.

<a id="p-21"></a>

### Slide 21 · La loss di una sequenza

Su una sequenza di $T$ posizioni la loss è la **media** delle loss per posizione:

$$L_{CE}(\text{batch di lunghezza }T) = \frac{1}{T}\sum_{t=1}^{T} -\log \hat y_t[w_{t+1}]$$

| vero successivo | long | and | thanks | for | all |
| --- | --- | --- | --- | --- | --- |
| $\hat y$ | 0,20 | 0,50 | 0,40 | 0,80 | 0,44 |
| $-\ln\hat y$ | 1,61 | 0,69 | 0,92 | 0,22 | 0,82 |

Somma 4,26, media $4{,}26/5 = 0{,}85$. Le probabilità sono inventate, tranne lo 0,44 della scheda 18. La discesa del gradiente abbassa questa media aggiustando tutti i pesi. Si usa la media e non la somma perché così la scala della loss (e quindi del gradiente e del learning rate) non dipende dalla lunghezza del batch.

> **Da saper fare: Verifica**
>
> $-\ln 0{,}2 = 1{,}609$, $-\ln 0{,}5 = 0{,}693$, $-\ln 0{,}4 = 0{,}916$, $-\ln 0{,}8 = 0{,}223$, $-\ln 0{,}44 = 0{,}821$. Somma $4{,}263$, media $0{,}8526$: la slide arrotonda a 0,85, la [scheda 56](L17-pretraining-dei-modelli-linguistici.md#p-56) scrive 0,853. Torna.

<a id="p-22"></a>

### Slide 22 · Tutte le posizioni in parallelo

Perché il pretraining su trilioni di token è praticabile:

- **I target sono noti**: il vero token successivo di ogni posizione è nel testo (teacher forcing).
- **La maschera causale** ([L14](L14-transformer-l-attenzione.md#p-56)): nessuna posizione può guardare il proprio target, cioè i token alla sua destra, quindi l'output di ogni posizione è calcolato come se le successive non esistessero.
- **Un passaggio, $N$ esempi**: tutte le $N$ posizioni della finestra di contesto vengono valutate in una volta contro i loro veri successivi.

In pratica un solo forward della forma matriciale $\mathrm{softmax}(\mathrm{mask}(QK^\top/\sqrt{d_k}))V$ dà $N$ distribuzioni e $N$ loss. Senza maschera il modello vedrebbe la risposta (la posizione $t$ potrebbe copiare il token $t+1$) e la loss crollerebbe senza che impari nulla di utile per la generazione: è uno degli esperimenti proposti in fondo al notebook. Una rete ricorrente, invece, deve elaborare le posizioni una dopo l'altra anche in training.

<a id="p-23"></a>

### Slide 23 · Riempire la finestra di contesto

La figura: una finestra di $N$ token in cui sono impacchettati il documento 1 (azzurro), un token `eot`, il documento 2 (verde), un altro `eot` e l'inizio del documento 3 (rosso); la freccia indica che il resto del documento 3 va nella finestra successiva. Tutti gli $N$ token sono usati per il training.

- I modelli grandi si addestrano su **finestre piene**: i documenti corti vengono **impacchettati** (packing) con un token di fine testo fra l'uno e l'altro, invece di riempire il resto con padding sprecato.
- I **batch** sono grandi: il GPT-3 più grande usava 3,2 milioni di token per batch.
- Con finestre di 2.048 token: $3{,}2\cdot10^6/2048 = 1562{,}5$, cioè circa 1.560 finestre per batch.

Il token `eot` insegna anche al modello dove finisce un documento, e quindi a smettere di generare. Con 300 miliardi di token di training, un passaggio sui dati richiede $3\cdot10^{11}/3{,}2\cdot10^6 = 93.750$ passi di gradiente (esercizio 3 della scheda).

## Task come generazione

<a id="p-24"></a>
**Slide 24 · I task come generazione** — Un solo obiettivo, molti task: perché predire il token successivo basta a fare classificazione, domande e riassunti.

<a id="p-25"></a>

### Slide 25 · Generazione condizionata

Frase chiave: **molti task pratici di NLP si possono riformulare come predizione di parole**.

- **Generazione condizionata**: generare testo condizionato a un **prompt** di input, scegliendo token probabili dato il contesto precedente.
- **Il prompt**: il task è scritto nel testo stesso, e il modello lo continua.
- **Autoregressiva**: ogni token generato viene aggiunto al contesto per generare il successivo ([L1](L01-introduzione-al-corso.md#p-6)).

L'intuizione (J&M §1.2.1, *prompting = conditional generation = token prediction*): le risposte sono continuazioni ad alta probabilità delle domande, perché nel testo di training le domande sono spesso seguite da risposte. Non serve un modello per task: serve un prompt che renda la risposta voluta la continuazione più probabile. Le tre schede seguenti lo mostrano su sentiment, question answering e riassunto.

<a id="p-26"></a>

### Slide 26 · Sentiment analysis come predizione di parole

Due passi:

1. si dà al modello il prompt `The sentiment of the sentence "I like Jackie Chan" is:`
2. si confrontano le probabilità di due parole come token successivo: $P(\textit{positive}\mid\text{prompt}) = 0{,}42$ e $P(\textit{negative}\mid\text{prompt}) = 0{,}03$ (numeri inventati).

La parola più probabile è l'etichetta: **positive**. Nessun classificatore addestrato per il sentiment, come quelli della [L6](L06-regressione-logistica.md#p-5): solo probabilità di token successivi. Si noti che 0,42 e 0,03 non sommano a 1: sono due voci di una distribuzione su tutto il vocabolario, il resto della massa va ad altre parole. Per decidere basta il confronto; se servisse una probabilità di classe si rinormalizza sulle due parole: $0{,}42/0{,}45 = 0{,}93$.

> **Approfondimento: Per il progetto**
>
> Questo è il **baseline zero-shot** naturale per hate speech detection: un prompt tipo `Is the following tweet offensive? ... Answer:` e il confronto fra $P(\textit{yes})$ e $P(\textit{no})$, senza alcun training. Due cautele, che l'esercizio 4 della scheda anticipa: le parole-etichetta possono avere probabilità piccole rispetto ad altre continuazioni (*bad* più probabile di *negative*), e il modello ha preferenze a priori per certe parole indipendentemente dall'input, quindi conviene calibrare (per esempio confrontare con le probabilità date a un input vuoto) e misurare con macro-F1 sul dev set, non a occhio. È un buon punto di confronto con l'encoder fine-tuned.

<a id="p-27"></a>

### Slide 27 · Question answering come predizione di parole

Il prompt `Q: Who wrote the book "The Origin of Species"? A:`. Si calcola $P(w\mid \text{Q: Who wrote ... A:})$ e il token più probabile è *Charles*; lo si aggiunge al contesto, si ricalcola $P(w\mid \text{... A: Charles})$ e il più probabile è *Darwin*.

Due osservazioni:

- un token come `A:` **suggerisce che segue una risposta**: nel testo di training (FAQ, tabelle di domande) dopo `A:` viene una risposta, quindi il modello alza la probabilità di nomi propri pertinenti;
- la risposta è **generata un token alla volta**, come qualunque testo: *Darwin* diventa probabile perché il contesto ora contiene *Charles* (e lo sarebbe anche senza `A:`).

Il modello deve aver visto Darwin associato al libro: la conoscenza fattuale viene dal pretraining, il formato domanda-risposta dalla struttura del testo.

<a id="p-28"></a>

### Slide 28 · Riassunto come predizione di parole

La figura (da una versione precedente del libro, usata nella lezione 2025): in basso il testo originale (*The only ... idea was born.*), poi il delimitatore `tl;dr`, poi i token del riassunto generato (*Kyle Waring will ...*) in rosso. Sopra i token, il blocco del transformer (viola) e, in verde, la **LM head** che produce ogni token del riassunto; le frecce tratteggiate riportano ogni token generato in input per generare il successivo.

Il trucco: `tl;dr` (*too long; didn't read*) sul web precede spesso un riassunto del post sopra. Quindi dopo un testo lungo e `tl;dr` la continuazione più probabile è un breve riassunto. Il riassunto può attingere a tutto il testo precedente grazie all'attenzione: le linee nere nella figura collegano i token generati a quelli del testo originale.

<a id="p-29"></a>

### Slide 29 · Un obiettivo, molti task

- **Nel testo**: recensioni con il loro voto, domande con risposta, post con il loro `tl;dr`: il web è pieno di task già svolti.
- **Nei pesi**: per predire bene il token successivo il modello deve imparare molto sulla lingua (accordo, sintassi) e sul mondo (chi ha scritto cosa, aritmetica, stili).
- **Il limite**: un **base model** continua il testo, non segue istruzioni in modo affidabile. Al prompt *Translate to French: The small dog* può rispondere *The small dog crossed the road.* (esempio di J&M §1.6.2). Insegnargli a seguire istruzioni è compito dell'**instruction tuning**, il secondo stadio ([L1](L01-introduzione-al-corso.md#p-58)) e la prossima lezione.

Frase da ricordare: **predizione del token successivo su abbastanza testo = un modello per molti task**. Il prompting di un base model funziona, ma richiede di formulare il task come una continuazione naturale del testo.

## Dati di pretraining

<a id="p-30"></a>
**Slide 30 · Dati di pretraining** — Da dove viene il testo, come si filtra e quali problemi pone.

<a id="p-31"></a>

### Slide 31 · Corpora di training

Frase chiave: **soprattutto testo dal web, più dati curati con più attenzione**.

- **Common Crawl**: una serie di istantanee dell'intero web prodotte dall'organizzazione non profit Common Crawl (commoncrawl.org), ciascuna con miliardi di pagine. È la **fonte principale** dei modelli open.
- **Dati curati**: Wikipedia, libri. Pochi in proporzione, ma importanti per la qualità (testo corretto, lungo, informativo).
- **Modelli chiusi**: come sono addestrati i modelli proprietari non è noto nei dettagli.

Il web grezzo è enorme ma rumoroso (menu, spam, duplicati, testo generato automaticamente): per questo i passi di filtraggio delle schede 34-35 sono parte essenziale della costruzione del corpus, non un dettaglio.

<a id="p-32"></a>

### Slide 32 · Quanto testo?

Llama 3.1 405B è stato addestrato su **oltre 15 trilioni di token**. Un conto a spanne:

- $15\cdot10^{12}$ token $\times$ circa 0,75 parole per token $\approx 11{,}25\cdot10^{12}$ parole;
- leggendo 300 parole al minuto, giorno e notte senza pause: $11{,}25\cdot10^{12}/300 = 3{,}75\cdot10^{10}$ minuti, cioè circa **71.000 anni**.

0,75 parole per token è un valore tipico per l'inglese con tokenizzatori BPE (cioè circa 1,33 token per parola; in altre lingue servono più token per parola, [L2](L02-parole-e-token.md#p-43)). Conclusione: molto più testo di quanto una persona potrebbe leggere in molte vite. Un bambino, per confronto, sente nell'ordine di decine di milioni di parole all'anno: i modelli imparano con molti più dati degli umani.

> **Da saper fare: Verifica**
>
> $15\cdot10^{12}\times0{,}75 = 1{,}125\cdot10^{13}$ parole. Minuti in un anno: $60\cdot24\cdot365{,}25 = 525.960$. Anni: $1{,}125\cdot10^{13}/(300\cdot525.960) = 71.298$. La slide dice circa 71.000: torna.

<a id="p-33"></a>

### Slide 33 · The Pile

**The Pile** (Gao et al., 2020, EleutherAI): circa **800 GB** di testo inglese da **22 fonti**, costruito apposta per la varietà. La figura è un **treemap**: ogni rettangolo è una fonte, con area proporzionale alla sua dimensione effettiva nel training, colorata per categoria.

- **Accademico** (blu): PubMed Central (il rettangolo blu più grande), ArXiv, FreeLaw, USPTO (brevetti), PMA (abstract PubMed), Phil (PhilPapers), NIH;
- **Internet** (verde): Pile-CC (da Common Crawl, il rettangolo più grande di tutti), OpenWebText2, StackExchange, Wikipedia;
- **Prosa** (arancio): Bibliotik (libri), PG-19 (Project Gutenberg), BC2 (BookCorpus2);
- **Dialogo** (giallo): Subtitles, IRC, EP (EuroParl), HN (Hacker News), YT (sottotitoli YouTube);
- **Varie** (grigio): Github (codice), DM Math.

Il messaggio: **un mix di fonti scelto per la diversità**, in cui Common Crawl è solo una parte.

> **Approfondimento: Le percentuali del paper**
>
> Dalla tabella 1 di Gao et al. (2020), quota di ciascuna fonte nel training (dimensione effettiva, dopo aver ripetuto più volte le fonti di qualità): Pile-CC 18,1%, PubMed Central 14,4%, Books3 (Bibliotik) 12,1%, OpenWebText2 10,0%, ArXiv 9,0%, Github 7,6%, FreeLaw 6,1%, StackExchange 5,1%, USPTO 3,7%, PubMed Abstracts 3,1%, PG-19 2,2%, OpenSubtitles 1,6%, Wikipedia 1,5%, DM Math 1,2%, poi le fonti sotto l'1%. Per categoria: accademico circa 37%, internet circa 35%, prosa circa 15%, varie circa 9%, dialogo circa 4%. La dimensione grezza è di circa 825 GiB (gli 800 GB della slide); quella effettiva di circa 1,25 TiB, perché fonti come Wikipedia e i libri vengono viste più di una volta per epoca. Per confronto, Llama 3 (Llama Team, 2024) dichiara un mix finale di circa 50% conoscenza generale, 25% matematica e ragionamento, 17% codice, 8% multilingue.

<a id="p-34"></a>

### Slide 34 · Filtri per la qualità

Tre filtri di qualità standard (Longpre et al., 2024; Llama Team, 2024):

- **Deduplicazione**: togliere documenti o pagine duplicate (o quasi duplicate). Il web è pieno di copie: tenerle significa sprecare calcolo, sovrappesare certi testi e favorire la **memorizzazione** letterale.
- **Boilerplate**: togliere menu, banner, testo di navigazione.
- **Contenuti per adulti**: rimossi.

L'esempio della slide: `Home | News | Sports | Login` e `Accept all cookies` sono boilerplate da togliere; `The council approved the new bridge.` è testo da tenere.

I filtri sono spesso **classificatori che danno un punteggio a ogni documento** (qualità, lingua, tossicità), con una soglia sotto cui il documento si scarta: è text classification della [L6](L06-regressione-logistica.md#p-5) usata per costruire i dati di un altro modello.

<a id="p-35"></a>

### Slide 35 · Filtri per la sicurezza

- **Classificatori di tossicità**: rimuovono il materiale tossico.
- **Falsi allarmi**: testi non tossici in dialetti minoritari, come l'African American English, vengono spesso segnalati (Xu et al., 2021).
- **Un compromesso**: i modelli addestrati su dati filtrati sono un po' meno tossici, ma peggiori a riconoscere la tossicità (Longpre et al., 2024): se non vedono mai testo tossico, non imparano a riconoscerlo.

Il primo punto è un problema di **bias** a due livelli: il classificatore sbaglia di più su un gruppo, e il filtro toglie dal corpus proprio i testi di quel gruppo, che quindi il modello finale vedrà meno (esercizio 5: con 10% di falsi positivi sul dialetto contro 2% sugli altri, la quota del dialetto scende dal 5,00% al 4,61%). Conclusione della slide: filtrare meglio è un problema aperto importante.

> **Approfondimento: Per il progetto**
>
> È esattamente il problema noto in letteratura per i dataset di hate speech: Sap et al. (2019) e Davidson et al. (2019) mostrano che i classificatori addestrati su questi dataset segnalano come offensivi i tweet in African American English molto più spesso degli altri, perché nelle annotazioni certi tratti dialettali o parole riappropriate sono associati all'etichetta offensiva. Per il gruppo 5 è una sezione naturale del capitolo sul bias: misurare il tasso di falsi positivi per gruppo (dialetto, o termini identitari come in un test di template) e non solo la F1 complessiva.

<a id="p-36"></a>

### Slide 36 · Questioni etiche e legali

- **Copyright**: buona parte del testo, i libri per esempio, è protetta. Negli USA il *fair use* può consentire o no il training; la questione del compenso agli autori non è risolta (Henderson et al., 2023).
- **Privacy**: numeri di telefono, indirizzi email; i filtri non sempre li tolgono.
- **Consenso**: alcuni siti non vogliono essere raccolti dai crawler (per esempio lo segnalano in `robots.txt`).
- **Skew**: il testo è scritto in proporzione eccessiva da autori degli USA e di altri paesi sviluppati, e le loro prospettive e i loro temi pesano di più nelle generazioni del modello.

Sono problemi del corpus nel suo insieme, che un filtro sul singolo documento non risolve (esercizio 5c): lo skew per esempio è una proprietà della distribuzione, non di un testo.

<a id="p-37"></a>

### Slide 37 · Il copyright in tribunale

Tre casi, per mostrare che la risposta dipende da paese, provenienza dei dati e memorizzazione:

- **Bartz v. Anthropic** (USA): addestrare su libri è *fair use*, un'eccezione della legge statunitense, perché l'uso è *exceedingly transformative* (giugno 2025); ma scaricare libri piratati non lo è: accordo da 1,5 miliardi di dollari, circa 3.000 dollari per libro (quindi circa 500.000 opere).
- **NYT v. OpenAI** (USA): articoli del New York Times nei dati di training, e ChatGPT che ne ripete alcuni quasi alla lettera. Ancora aperto: il giudice deve decidere se questo uso è fair use.
- **GEMA v. OpenAI** (Germania): ChatGPT riproduceva testi di canzoni quasi parola per parola; il tribunale di Monaco (novembre 2025) ha stabilito che i testi **memorizzati nei pesi** sono una copia dell'opera. In appello.

Il filo comune è la **memorizzazione**: un modello che può restituire testo letterale del training pone problemi diversi da uno che ne ha solo estratto statistiche. Anche per questo la deduplicazione (scheda 34) conta: i testi ripetuti molte volte sono quelli che il modello memorizza di più.

<a id="p-38"></a>

### Slide 38 · Data-centric AI

Le domande che chi costruisce un modello dovrebbe farsi sempre sui dati di training (J&M §1.6.1):

- Da dove vengono i dati?
- Chi sono gli autori dei testi?
- Vengono compensati in modo equo?
- È lecito usare questi dati?

L'idea che i dati di training, le loro proprietà e la loro **provenienza** siano essenziali, quanto l'architettura, si chiama **data-centric AI**. Le parti precedenti mostrano perché: la qualità dipende dai filtri, il bias dallo skew del corpus, i rischi legali dalla provenienza. Vale anche per un progetto piccolo: sapere chi ha scritto e chi ha annotato il proprio dataset, che è lo scopo del *datasheet* di un corpus ([scheda 48 della L2](L02-parole-e-token.md#p-48)).

<a id="p-39"></a>
**Slide 39 · Pausa** — Dieci minuti di pausa; dopo: modelli, scaling law, valutazione.

## Modelli e KV cache

<a id="p-40"></a>
**Slide 40 · Modelli e KV cache** — Qualche numero sui modelli reali, il conto dei parametri a mano e la cache di key e value.

<a id="p-41"></a>

### Slide 41 · Modelli attuali

La tabella (Fig. 7.24 del libro), solo modelli open perché chi fa modelli proprietari di frontiera non pubblica questi numeri:

| Modello | Anno | $L$ | $d$ | $A$ | $d_{ff}$ | $|V|$ | Contesto | Param. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GPT-2 XL | 2019 | 48 | 1600 | 25 | 6400 | 50K | 1K | 1,5B |
| GPT-3 | 2020 | 96 | 12288 | 96 | 49152 | 50K | 2K | 175B |
| Qwen3-0.6B | 2025 | 28 | 1024 | 16 | 3072 | 152K | 32K | 0,6B |
| Qwen3-32B | 2025 | 64 | 5120 | 64 | 25600 | 152K | 128K | 32B |
| Llama 3.1 8B | 2024 | 32 | 4096 | 32 | 14336 | 128K | 128K | 8B |
| Llama 3.1 405B | 2024 | 126 | 16384 | 128 | 53248 | 128K | 128K | 405B |

$L$ strati, $d$ dimensione del modello, $A$ teste di attenzione, $d_{ff}$ dimensione del feedforward, $|V|$ vocabolario. Sono numeri indicativi: le architetture moderne usano GQA (meno key e value che query) e SwiGLU, quindi $A$ e $d_{ff}$ non hanno più il significato classico (in Qwen3-0.6B le 16 teste hanno dimensione 128, quindi $A\cdot d_k = 2048 \neq d$).

<a id="p-42"></a>

### Slide 42 · Leggere la tabella

- **Parametri**: 1,5B nel 2019, 175B nel 2020, 405B nel 2024; ma anche modelli piccoli, 0,6B nel 2025.
- **Contesto**: da 1K token a 128K (un fattore 128).
- **Vocabolario**: da 50K token a 152K, per coprire meglio molte lingue e il codice.
- **$d_{ff}$**: $4d$ in GPT-2 e GPT-3 ($6400 = 4\cdot1600$, $49152 = 4\cdot12288$); fra $3d$ e $5d$ nei modelli nuovi.

Verifica dei rapporti $d_{ff}/d$: Qwen3-0.6B $3072/1024 = 3{,}0$; Qwen3-32B $25600/5120 = 5{,}0$; Llama 3.1 8B $14336/4096 = 3{,}5$; Llama 3.1 405B $53248/16384 = 3{,}25$. Con SwiGLU le matrici del feedforward sono tre invece di due ([L14](L14-transformer-l-attenzione.md#p-47)), e si sceglie $d_{ff}$ più piccolo di $4d$ per tenere simile il numero di parametri: $3\cdot d\cdot\tfrac{8}{3}d = 8d^2$ come $2\cdot d\cdot 4d$.

<a id="p-43"></a>

### Slide 43 · Contare i parametri a mano

Il conto della lezione, per un modello classico (GPT-2, GPT-3):

|  |  |  |
| --- | --- | --- |
| attenzione | $W^Q, W^K, W^V, W^O$: 4 matrici $d\times d$ | $4d^2$ |
| feedforward | $d\times4d$ e $4d\times d$ | $8d^2$ |
| **uno strato** |  | $12d^2$ |
| **il modello** | $L$ strati + embedding $E$ | $12Ld^2 + |V|d$ |

**GPT-3**: $12\cdot96\cdot12288^2 = 174{,}0$B, più $50\text{K}\cdot12288 = 0{,}6$B, totale $174{,}6\text{B}\approx175$B. **GPT-2 XL**: $12\cdot48\cdot1600^2 = 1{,}47$B più $50\text{K}\cdot1600 = 0{,}08$B, totale 1,55B, l'1,5B della tabella.

Ipotesi del conto: niente bias, niente layer norm, **weight tying** (una sola $E$ per input e output), niente embedding di posizione. Sono tutti termini lineari in $d$, trascurabili rispetto a $d^2$ quando $d$ è grande. Il $4d^2$ dell'attenzione è quello della [scheda 40 della L14](L14-transformer-l-attenzione.md#p-40), l'$8d^2$ del feedforward della [scheda 46](L14-transformer-l-attenzione.md#p-46).

> **Da saper fare: Verifica e proporzioni**
>
> $12\cdot96\cdot12288^2 = 173{,}95\cdot10^9$; con $|V| = 50.257$ esatto, $E$ ha $0{,}618\cdot10^9$ pesi e il totale è $174{,}56\cdot10^9$. GPT-2 XL: $1{,}4746\cdot10^9 + 0{,}0804\cdot10^9 = 1{,}555\cdot10^9$. In GPT-3 $E$ è solo lo 0,35% dei parametri; in un modello piccolo come GPT-2 small ($d = 768$) è circa il 31% (esercizio 6). In ogni strato l'attenzione è $1/3$ dei pesi e il feedforward $2/3$.

> **Approfondimento: Il conto esatto per un modello moderno**
>
> Con GQA e SwiGLU il conto cambia. Llama 3.1 8B: query e output $d\times d$ ciascuna; key e value $d\times1024$ (8 teste di key/value da 128 invece di 32); feedforward con tre matrici $d\times d_{ff}$. Per strato: $2\cdot4096^2 + 2\cdot4096\cdot1024 + 3\cdot4096\cdot14336 = 218{,}1$M; per 32 strati 6,98B; più due matrici di embedding non legate $2\cdot128.256\cdot4096 = 1{,}05$B. Totale **8,03B**, il valore ufficiale. Lo stesso conto per Qwen3-0.6B (query di dimensione 2048, key e value di 1024, embedding legati) dà 0,44B negli strati più 0,16B di embedding, cioè 0,60B. La formula $12Ld^2 + |V|d$ invece dà 6,97B per Llama 3.1 8B: va bene per l'ordine di grandezza, non per il valore esatto.

<a id="p-44"></a>

### Slide 44 · Impostazioni moderne

- **Modelli migliori** (più accurati): RoPE (embedding di posizione rotary), RMSNorm, feedforward con gate SwiGLU. Visti nelle ultime due lezioni.
- **Modelli più veloci** (efficienza: più velocità o meno memoria): **Mixture-of-Experts** (ogni token attraversa solo alcuni dei feedforward, gli *esperti*), **Grouped-Query Attention** (più teste di query condividono le stesse key e value), **quantizzazione** (pesi in 8 o 4 bit invece di 16).

Il libro non approfondisce queste tecniche di efficienza; ne vede una sola in dettaglio, la **KV cache**, che è usata da praticamente ogni sistema di generazione e rende comprensibile perché esista la GQA.

<a id="p-45"></a>

### Slide 45 · La KV cache

- **Training**: tutti i token insieme, con due moltiplicazioni di matrici ($QK^\top$ e il prodotto per $V$), come nella forma matriciale della L14.
- **Inferenza**: si genera un token nuovo alla volta; per il nuovo token $x_i$ servono la sua query, key e value ($x_iW^Q$, $x_iW^K$, $x_iW^V$).
- **Lo spreco**: le key e i value dei token precedenti $x_{&lt;i}$ sono già stati calcolati ai passi prima. Ricalcolarli a ogni passo è inutile, perché in un modello causale non cambiano: la key del token 3 dipende solo dai token 1-3.
- **La cache**: si salva ogni key e value appena calcolati e si leggono dalla memoria quando servono.

Il motivo per cui funziona è proprio la causalità: aggiungere un token a destra non cambia nulla di ciò che sta a sinistra, in nessuno strato. Generare $n$ token senza cache richiede $1 + 2 + \dots + n = n(n+1)/2$ calcoli di key e value per strato, con la cache solo $n$ (per $n = 1000$: 500.500 contro 1.000, esercizio 7c).

<a id="p-46"></a>

### Slide 46 · La KV cache: il quarto token

La figura (Fig. 7.23 del libro) estrae dalla forma matriciale il calcolo per il **quarto token**: $q_4$ (giallo, $1\times d_k$) per $K^\top$ ($d_k\times N$, colonne $k_1\dots k_4$) dà la riga di punteggi $q_4\cdot k_1, \dots, q_4\cdot k_4$ ($1\times N$, verde); dopo la softmax, per $V$ ($N\times d_v$, righe $v_1\dots v_4$) dà $a_4$ ($1\times d_v$).

- Nuovi (colorati): la query $q_4$, la key $k_4$ (lilla) e il value $v_4$ (rosa).
- In nero: $k_1, k_2, k_3$ e $v_1, v_2, v_3$, letti dalla cache.

I punteggi di $q_4$ con tutte le key si calcolano comunque a ogni passo: si salvano **solo key e value**, non le query (una query serve una volta sola, al suo passo) né i punteggi (cambiano con ogni nuova query). Slogan: **meno calcolo, più memoria**. Il costo per token resta lineare nella lunghezza del contesto (un prodotto scalare per ogni key in cache), ma sparisce il ricalcolo quadratico di key e value.

<a id="p-47"></a>

### Slide 47 · La KV cache a mano (GPT-3)

Quanta memoria occupa la cache:

- per token e per strato: una key e un value, $2d$ numeri (le teste insieme, $d$ numeri ciascuno);
- per token, $L$ strati: $2Ld = 2\cdot96\cdot12288 = 2{,}36$ milioni di numeri;
- a 2 byte per numero (16 bit): **4,7 MB per token**;
- una finestra di 2.048 token: circa **9,7 GB per una sola sequenza**.

La cache cresce **linearmente con il contesto e con il numero di sequenze** servite insieme: con 128K token di contesto e decine di utenti in parallelo diventa il collo di bottiglia della memoria GPU, più dei pesi stessi. Da qui la **GQA**: gruppi di teste condividono key e value, e la cache si riduce dello stesso fattore.

> **Da saper fare: Verifica e confronto con la GQA**
>
> $2\cdot96\cdot12288 = 2.359.296$ numeri; $\times2$ byte $= 4{,}72$ MB; $\times2048 = 9{,}66\cdot10^9$ byte $\approx 9{,}7$ GB (sono 9,0 GiB in potenze di 2). Formula generale: $\text{memoria} = 2\cdot L\cdot d_{kv}\cdot b\cdot T$ con $b$ byte per numero e $T$ token. Llama 3.1 8B con GQA ha $d_{kv} = 8\cdot128 = 1024$: $2\cdot32\cdot1024\cdot2 = 131$ KB per token, 17,2 GB per 128K token; senza GQA ($d_{kv} = 4096$) sarebbero 524 KB e 68,7 GB. Per Llama 3.1 405B a 128K token: 1,08 TB senza GQA, 67,6 GB con (esercizio 7b).

## Scaling law

<a id="p-48"></a>
**Slide 48 · Scaling law** — Dimensione, dati e calcolo: come scende la loss e come spendere un budget.

<a id="p-49"></a>

### Slide 49 · Che cosa vuol dire large?

Frase chiave: **la dimensione si misura in parametri**, cioè i pesi e i bias della rete (ogni numero reale addestrato).

- **Nel nome**: Llama 3.1 405B ha 405 miliardi di parametri, addestrato su oltre 15 trilioni di token.
- **Famiglie**: lo stesso modello in più taglie, da meno di un miliardo a molti trilioni di parametri (Llama 3.1: 8B, 70B, 405B; Qwen3: da 0,6B a 235B), addestrate su trilioni o decine di trilioni di token.

Large ha quindi due sensi (J&M §1.1): molti parametri e molti dati di training. Le scaling law dicono come i due, insieme al calcolo, determinano la qualità. A 2 byte per parametro, i soli pesi di un modello da 405B occupano 810 GB: servono molte GPU anche solo per eseguirlo.

<a id="p-50"></a>

### Slide 50 · Scaling law (Kaplan et al., 2020)

Tre fattori: **dimensione del modello $N$** (parametri), **dati $D$** (token di training), **calcolo $C$** (di training). La figura (Kaplan et al., 2020, Fig. 1) ha tre pannelli, tutti in scala log-log con la **test loss** in ordinata:

- **Compute** (PF-giorni, senza embedding): tante curve azzurre chiare, una per run di training, ognuna scende e si appiattisce; il loro inviluppo inferiore (nero) è ben approssimato dalla retta arancio tratteggiata $L = (C_{min}/2{,}3\cdot10^8)^{-0{,}050}$, dalla loss 6-7 fino a circa 2,5;
- **Dataset size** (token, da circa $2\cdot10^7$ a $2\cdot10^9$): punti quasi su una retta, $L = (D/5{,}4\cdot10^{13})^{-0{,}095}$, da 4,2 a 2,7;
- **Parameters** (senza embedding, da circa $10^3$ a $10^9$): $L = (N/8{,}8\cdot10^{13})^{-0{,}076}$, da 5,6 a circa 2,4.

Una **legge di potenza** $L = (X/X_c)^{-\alpha}$ diventa in log-log una retta: $\log L = -\alpha\log X + \alpha\log X_c$. Messaggio: **più grande è meglio, e in modo prevedibile**, per questo i modelli continuano a crescere; con più spesa, energia e acqua. Ogni legge vale quando gli altri due fattori non sono il collo di bottiglia.

> **Da saper fare: Leggere una legge di potenza**
>
> Con $L(N) = (N/8{,}8\cdot10^{13})^{-0{,}076}$: $L(10^8) = 2{,}83$ nat (perplexity $e^{2{,}83} = 16{,}9$), $L(10^9) = 2{,}38$ (perplexity 10,8): il punto finale del pannello di destra. Moltiplicare $N$ per $k$ moltiplica la loss per $k^{-0{,}076}$: per 10, $\times0{,}839$; per 2, $\times0{,}949$. Per **dimezzare** la loss serve $k = 2^{1/0{,}076}\approx 9.100$. Con i dati: 10 volte più token, loss $\times10^{-0{,}095} = 0{,}804$. Gli esponenti piccoli spiegano perché servono fattori enormi per guadagni modesti, e perché la scala è cresciuta di ordini di grandezza.

<a id="p-51"></a>

### Slide 51 · Come spendere un budget di calcolo

- **Il costo**: il training costa circa $C\approx 6ND$ operazioni in virgola mobile (FLOP). Con un budget fisso, un modello più grande vede meno token.
- **Hoffmann et al. (2022)**: al variare di $C$, la dimensione ottimale e i dati ottimali crescono allo stesso modo, come la radice quadrata del calcolo: $N_{opt}\propto C^{1/2}$, $D_{opt}\propto C^{1/2}$.
- **La prova**: con lo stesso budget di **Gopher** (280B parametri, 300B token), **Chinchilla** (70B parametri, 1,4T token) è andato meglio.

Regola pratica: **circa 20 token di training per parametro**; modello e dati crescono insieme. Molti modelli precedenti, GPT-3 compreso (175B parametri, 300B token, 1,7 token per parametro), erano **troppo grandi per i loro dati**: con lo stesso calcolo un modello più piccolo addestrato più a lungo avrebbe avuto loss più bassa. Quadruplicare il budget significa raddoppiare sia $N$ sia $D$.

> **Da saper fare: Da dove viene 6ND, e il conto di Chinchilla**
>
> **6ND**: nel forward ogni parametro fa circa una moltiplicazione e un'addizione per token, cioè 2 FLOP per parametro per token ($2ND$); il backward costa circa il doppio del forward (gradiente rispetto agli input e rispetto ai pesi), $4ND$. Totale $6ND$ (il costo dell'attenzione, che dipende dal contesto, è trascurato).
>
> **Chinchilla**: $C = 6\cdot70\cdot10^9\cdot1{,}4\cdot10^{12} = 5{,}88\cdot10^{23}$ FLOP; Gopher $6\cdot280\cdot10^9\cdot300\cdot10^9 = 5{,}04\cdot10^{23}$: con $6ND$ il budget di Chinchilla è circa il 17% più alto, lo *stesso budget* della slide è un'approssimazione (il paper usa un conteggio dei FLOP più fine). Ottimo con $D = 20N$: $C = 6N\cdot20N = 120N^2$, quindi $N = \sqrt{C/120}$. Con $C = 5{,}88\cdot10^{23}$: $N = 70$B, $D = 1{,}4$T, cioè Chinchilla. Con il budget di GPT-3 ($6\cdot175\cdot10^9\cdot300\cdot10^9 = 3{,}15\cdot10^{23}$): $N_{opt} = 51$B e $D_{opt} = 1{,}0$T, invece di 175B e 0,3T.

<a id="p-52"></a>

### Slide 52 · Modelli più piccoli, addestrati più a lungo

Il grafico a barre (asse orizzontale logaritmico, da 1 a 10.000) mostra i **token di training per parametro**, con una linea tratteggiata a circa 20:

| Modello | Token | Token/parametro |
| --- | --- | --- |
| GPT-3 175B | 300B | 1,7 |
| Chinchilla 70B | 1,4T | 20 |
| Llama 3.1 405B | 15T | 37 |
| Llama 3.1 8B | 15T | 1.875 |

**Anche l'inferenza costa**: il training si paga una volta, l'inferenza a ogni prompt, e un modello più grande costa di più a ogni prompt (circa $2N$ FLOP per token generato). Per questo spesso si addestra un modello **più piccolo per più tempo**: Llama 3.1 8B, con circa 1.900 token per parametro, è molto oltre i 20 di Chinchilla, **di proposito**. Chinchilla minimizza la loss per un dato calcolo di *training*; se il modello servirà miliardi di richieste, conviene spendere più calcolo in training per avere un modello piccolo, economico da usare. E la loss continua a scendere anche oltre i 20 token per parametro, solo più lentamente.

> **Da saper fare: Verifica**
>
> $300/175 = 1{,}71$; $1400/70 = 20$; $15\,000/405 = 37{,}0$; $15\,000/8 = 1875$. Calcolo di Llama 3.1 8B: $6\cdot8\cdot10^9\cdot15\cdot10^{12} = 7{,}2\cdot10^{23}$, circa 1,22 volte Chinchilla: budget simile, modello 9 volte più piccolo (esercizio 9c). Llama 3.1 405B: $6\cdot405\cdot10^9\cdot15\cdot10^{12} = 3{,}6\cdot10^{25}$ FLOP, circa 60 volte Chinchilla.

## Valutazione

<a id="p-53"></a>
**Slide 53 · Valutazione** — Quanto è buono il modello? Perplexity, accuratezza sui benchmark, giudici, metriche proxy.

<a id="p-54"></a>

### Slide 54 · Perplexity

La **likelihood** di un testo è il prodotto delle probabilità dei suoi token:

$$\text{likelihood}(w_{1:T}) = \prod_{i=1}^{T} P(w_i\mid w_{&lt;i})$$

Ma diventa sempre più piccola al crescere della lunghezza (si moltiplicano numeri minori di 1), quindi non confronta testi di lunghezza diversa. La **perplexity** è l'inverso della probabilità del testo, normalizzato per la lunghezza $T$ con una radice $T$-esima:

$$\text{Perplexity}(w_{1:T}) = P(w_{1:T})^{-1/T} = \left(\prod_{t=1}^{T} P(w_t\mid w_{&lt;t})^{-1}\right)^{1/T}$$

È una misura **per token**, confrontabile fra testi di lunghezze diverse: la media geometrica degli inversi delle probabilità. **Più è bassa la perplexity, migliore il modello.** È la stessa definizione già usata per gli n-gram ([L4](L04-modelli-linguistici-n-gram.md#p-30)), ora con la probabilità data da un transformer e condizionata su tutto il contesto, non sugli ultimi $n-1$ token.

<a id="p-55"></a>

### Slide 55 · Perplexity e loss

La loss di training su un testo di $T$ token è la **cross-entropy media**:

$$L_{CE} = \frac{1}{T}\sum_{t=1}^{T} -\log P(w_t\mid w_{&lt;t})$$

e vale

$$\text{perplexity} = \exp(\text{cross-entropy media}).$$

**Nat**: il log è naturale, quindi la loss è in nat, non in bit; per questo si esponenzia con $e$. Nella [L5](L05-smoothing-ed-entropia.md#p-39) la perplexity era $2^H$ con l'entropia in bit: è la stessa quantità, perché $2^{H/\ln 2} = e^{H}$.

**Lo stesso obiettivo**: loss più bassa = perplexity più bassa = probabilità del testo più alta. Allenare minimizzando la cross-entropy significa quindi minimizzare la perplexity sul training set; la si misura su testo **non visto** per valutare.

> **Da saper fare: La dimostrazione (esercizio lasciato al lettore in J&M §7.7.1)**
>
> Si prende il logaritmo della perplexity: $\ln \mathrm{PP} = \ln\left(\prod_t P(w_t\mid w_{&lt;t})\right)^{-1/T} = -\frac1T\sum_t \ln P(w_t\mid w_{&lt;t}) = L_{CE}$. Quindi $\mathrm{PP} = e^{L_{CE}}$. In bit: $L_{bit} = L_{CE}/\ln2$ e $\mathrm{PP} = 2^{L_{bit}}$, lo stesso numero. Esempio: loss 2,38 nat $= 3{,}43$ bit, perplexity $e^{2{,}38} = 2^{3{,}43} = 10{,}8$.

<a id="p-56"></a>

### Slide 56 · Perplexity a mano

La sequenza della [scheda 21](L17-pretraining-dei-modelli-linguistici.md#p-21), `So long and thanks for all`, con le probabilità dei veri token 0,20; 0,50; 0,40; 0,80; 0,44.

- **Dal prodotto**: $0{,}2\cdot0{,}5\cdot0{,}4\cdot0{,}8\cdot0{,}44 = 0{,}01408$, e $0{,}01408^{-1/5} = 2{,}35$.
- **Dalla loss**: loss media 0,853, e $e^{0{,}853} = 2{,}35$.

**Lo stesso numero**, come deve essere. Lettura: perplexity 2,35 significa che il modello è incerto **come se scegliesse fra circa 2,35 token equiprobabili** a ogni passo (il fattore di ramificazione medio della [L4](L04-modelli-linguistici-n-gram.md#p-33)). Un modello che dà probabilità uniforme su $|V|$ token ha perplexity esattamente $|V|$; un modello perfetto, 1.

> **Da saper fare: Verifica**
>
> Prodotto $0{,}014080$; $0{,}014080^{-0{,}2} = e^{-0{,}2\ln 0{,}01408} = e^{0{,}2\cdot4{,}263} = e^{0{,}8526} = 2{,}3457$. Le due strade danno $2{,}3457$ fino all'ultima cifra.

<a id="p-57"></a>

### Slide 57 · Un'avvertenza: il tokenizzatore

La perplexity **dipende dal numero di token** del testo. Stesso testo, stessa probabilità 0,001, due tokenizzatori (numeri inventati):

- tokenizzatore A, 4 token: $0{,}001^{-1/4} = 5{,}6$;
- tokenizzatore B, 6 token: $0{,}001^{-1/6} = 3{,}2$.

Perplexity diverse, **stessa qualità del modello** su questo testo: la probabilità assegnata al testo intero è identica, cambia solo per quanti token la si divide. Un tokenizzatore che spezza di più fa sembrare il modello migliore. Regola: **confrontare perplexity solo fra modelli con lo stesso tokenizzatore**. Se proprio si devono confrontare tokenizzatori diversi, si normalizza per una unità comune (parole, caratteri o byte): per parola, qui con 2 parole, entrambi danno $0{,}001^{-1/2} = 31{,}6$ (esercizio 11c con altri numeri).

> **Da saper fare: Verifica**
>
> $0{,}001^{-1/4} = 10^{3/4} = 5{,}623$; $0{,}001^{-1/6} = 10^{1/2} = 3{,}162$. Arrotondati: 5,6 e 3,2.

<a id="p-58"></a>

### Slide 58 · Accuratezza e benchmark

- **Accuratezza**: la risposta è corretta? $457 + 3$: *460*; l'autrice di Frankenstein: *Mary Shelley*.
- **Test set**: domande con risposte etichettate da persone, **mai viste in training**; si misura la percentuale di risposte corrette.
- **Benchmark**: grandi test set per LLM, spesso domande da esami umani (scuola, professioni). Sono un **proxy** della conoscenza fattuale o della capacità di ragionare.

La perplexity misura una sola cosa, quanto bene il modello predice il testo; i benchmark misurano se sa fare un compito. Il requisito *non visto* è lo stesso della separazione training/test della [L4](L04-modelli-linguistici-n-gram.md#p-27), ed è quello che la contaminazione (scheda 60) viola. Per confrontare due modelli su un benchmark vale la stessa cautela della [L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-37): verificare che la differenza sia statisticamente significativa.

<a id="p-59"></a>

### Slide 59 · Alcuni benchmark

Quattro benchmark comuni; a sinistra la figura del libro (Fig. 1.18) con un esempio per ciascuno:

- **MMLU** (Hendrycks et al., 2021): 15.908 domande di conoscenza e ragionamento in 57 aree (medicina, matematica, diritto...), a scelta multipla. Esempio: un caso clinico di dolore alla spalla con quattro muscoli fra cui scegliere (risposta: supraspinatus).
- **BigBench Hard**: rompicapi di ragionamento, come seguire istruzioni. Esempio: *Turn left. Turn right. Take 5 steps. Take 4 steps. Turn around. Take 9 steps.* Torni al punto di partenza? (Sì: 9 passi avanti e 9 indietro.)
- **GSM8k**: problemi di matematica a parole con la soluzione passo per passo. Esempio: 4 infornate da 2 dozzine di biscotti divise fra 16 persone, $96/16 = 6$.
- **AIME24**: matematica da competizione. Esempio: sei alberi con mele in progressione aritmetica, il massimo doppio del minimo, totale 990: risposta 220.

> **Da saper fare: Verifica dell'esempio AIME**
>
> Con minimo $a$ e massimo $2a$ in progressione aritmetica di 6 termini, la somma è $6\cdot(a+2a)/2 = 9a = 990$, quindi $a = 110$ e il massimo è 220. Nel GSM8k: $4\cdot2 = 8$ dozzine, $8\cdot12 = 96$ biscotti, $96/16 = 6$.

<a id="p-60"></a>

### Slide 60 · Data contamination

Frase chiave: **il test set finisce nel training set**.

- **Perché**: i modelli si addestrano sul web, e molti test sono sul web.
- **L'effetto**: la metrica **sovrastima** le prestazioni, perché il modello può ricordare le risposte invece di saperle trovare.
- **Un rimedio**: pubblicare i dati di training esatti, o almeno riportare la loro sovrapposizione con i test set: è un vantaggio dei modelli **completamente open**.

L'esempio (numeri inventati): 100 domande, 90 corrette, accuratezza 90%. Ma 30 erano nei dati di training, e sono tutte corrette; sulle altre 70 ne sono corrette 60: $60/70 = 85{,}7\%$, circa 86%. Il valore onesto è quello sul sottoinsieme pulito. Il concetto era già comparso con gli n-gram ([L4](L04-modelli-linguistici-n-gram.md#p-28)): per non sovrastimare la perplexity, nessuna frase del test deve stare nel training.

> **Approfondimento: Per il progetto**
>
> Nella forma piccola la contaminazione riguarda anche il progetto: i dataset di hate speech da Twitter contengono spesso tweet duplicati o quasi duplicati (retweet, stesse frasi con menzioni diverse), che possono finire sia nel training sia nel test e gonfiare la F1. Conviene deduplicare prima di dividere (anche normalizzando menzioni e URL) e, se si usa un modello preaddestrato su dati web recenti, ricordare che può aver visto i tweet del test. Il confronto onesto è sul sottoinsieme pulito, come nell'esempio della slide.

<a id="p-61"></a>

### Slide 61 · Task soggettivi

Frase chiave: **molti task utili hanno molte risposte corrette**.

- **Esempi**: una conversazione, una traduzione, quanto un modello è *sycophantic* (dà ragione all'utente a prescindere). Non esiste una conversazione corretta da confrontare.
- **Persone come giudici**: valutatori con una **rubrica**, per esempio per una traduzione: è fedele all'originale (stesso significato)? è fluente (suona naturale nella lingua di arrivo)?
- **Quali persone**: esperti delle due lingue per la traduzione; persone di provenienze diverse per giudicare utilità o tossicità, perché il giudizio stesso dipende da chi giudica.

Il punto in comune con l'annotazione dei dataset: un giudizio soggettivo va reso il più possibile ripetibile con istruzioni chiare, e conviene misurare quanto i valutatori sono d'accordo fra loro.

<a id="p-62"></a>

### Slide 62 · LLM-as-a-judge

- **Perché**: le persone costano, il lavoro è faticoso e ripetitivo (bisogna valutare molte versioni di un sistema), e valutare abusi o tossicità può essere emotivamente dannoso.
- **Come**: un prompt scritto con cura, la cui affidabilità si controlla confrontando i giudizi dell'LLM con quelli di esperti umani su un piccolo campione.
- **Singolo o a coppie**: un punteggio per un output (*single*), oppure quale di due output è migliore (*pairwise*).

L'esempio è un prompt pairwise: `Which translation is more faithful and more fluent? Translation A: ... Translation B: ... Answer A or B.` Il giudizio a coppie è di solito più facile e stabile di un punteggio assoluto. Un problema noto (oltre le slide): i giudici LLM hanno bias propri, per esempio verso la risposta presentata per prima o verso quelle più lunghe, per cui si scambia l'ordine di A e B e si media.

<a id="p-63"></a>

### Slide 63 · Metriche proxy

Una **metrica proxy** è una metrica formale, facile da calcolare automaticamente. L'esempio della slide, la sovrapposizione di token con una traduzione di riferimento:

|  |  |  |
| --- | --- | --- |
| riferimento | `the cat sat on the mat` |  |
| output 1 | `the cat is on the mat` | 5 token su 6 in comune |
| output 2 | `a feline was sitting on the rug` | 2 su 7 |

In pratica: sovrapposizione di stringhe per traduzione e riassunto (**chrF**, **BLEU**, **ROUGE**), **word error rate** per il riconoscimento del parlato; e sempre verificare che una differenza sia **statisticamente significativa** ([paired bootstrap della L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-44)).

Il limite: l'output 2 è una buona traduzione (un gatto seduto su un tappeto) ma ha punteggio basso, perché usa sinonimi. Le metriche proxy scambiano perfezione con comodità: costano quasi nulla e si possono calcolare a ogni esperimento.

> **Da saper fare: Verifica dei conteggi**
>
> Output 1: *the, cat, on, the, mat* compaiono nel riferimento (che ha due *the*), *is* no: 5 su 6. Output 2: solo *on* e *the*: 2 su 7. Ogni token del riferimento si può usare una volta sola (conteggio *clipped*, come in BLEU), altrimenti un output come *the the the* avrebbe punteggio pieno (esercizio 12b).

<a id="p-64"></a>

### Slide 64 · La legge di Goodhart

**«Quando una misura diventa un obiettivo, smette di essere una buona misura.»**

- **Il rischio**: ottimizzando un sistema per una metrica come chrF o il word error rate, si ottimizzano proprietà casuali (la sovrapposizione di parole) invece dell'obiettivo vero (traduzioni belle).
- **Il risultato**: la metrica diventa un proxy peggiore.

Esempio concreto: senza il limite di un uso per token del riferimento, l'output *the press the press the press* avrebbe 6 token su 6 in comune con *the president met the press on monday* (esercizio 12). Un sistema ottimizzato per quella metrica imparerebbe a ripetere parole frequenti. Vale anche per i benchmark: se tutti tarano i modelli su MMLU, i progressi su MMLU dicono sempre meno sulla capacità generale (e la contaminazione peggiora le cose).

<a id="p-65"></a>

### Slide 65 · Altri fattori

L'accuratezza non è l'unica cosa che conta:

- **Efficienza**: dimensione del modello, tempo di training e di esecuzione, memoria GPU; si valuta la prestazione a parità di budget.
- **Energia**: kWh consumati, kg di CO$_2$ emessi; è la *green AI* (Bolón-Canedo et al., 2024).
- **Sicurezza e bias**: linguaggio tossico, stereotipi. Benchmark dedicati: StereoSet, RealToxicityPrompts, BBQ.
- **Equità**: prestazioni ugualmente buone per gruppi diversi; un criterio è il benessere del **gruppo più svantaggiato** (in senso rawlsiano: si massimizza la prestazione sul gruppo peggiore, non la media).

Il criterio del gruppo peggiore è quello da usare quando si analizza un classificatore per sottogruppi: la media può nascondere un gruppo su cui il modello va molto peggio.

<a id="p-66"></a>

### Slide 66 · Riepilogo e prossima lezione

**Riepilogo**:

- pretraining: predire il token successivo, cross-entropy loss, teacher forcing;
- tutte le posizioni in parallelo, documenti impacchettati nella finestra;
- molti task sono predizione di parole, dato un prompt;
- dati: crawl del web e testo curato, filtrati; copyright, privacy, skew;
- scaling law: più grande è meglio; $N$ e $D$ insieme; modelli più piccoli per l'inferenza;
- perplexity = exp(cross-entropy media); benchmark, giudici, metriche proxy.

**Prossima lezione**: *Post-training I*, instruction tuning e **LoRA**, **venerdì 23 ottobre, 14-16**, Sala Riunioni Ovest del Dipartimento di Informatica; segue *Post-training II* alle 16-18. Lettura: capitolo 8. Niente lezioni il 21 e 22 ottobre.

## Notebook

Commento al notebook del corso `HLT-L17-pretraining.ipynb` (il notebook è del docente e non è incluso).

Notebook di accompagnamento (solo `numpy` e libreria standard, nessuna connessione): rifà i conti delle slide, costruisce un corpus dalle docstring della libreria standard di Python, **preaddestra da zero un piccolo transformer** a un blocco con backward scritto a mano (verificato con il gradiente numerico), genera testo prima e dopo il training, implementa la **KV cache** e controlla che dia gli stessi logit, prova lo scaling in miniatura e ricalcola parametri, FLOP, scaling law e gli esercizi della scheda. Rieseguito da capo: tutto gira senza errori in pochi minuti; i conti deterministici (sezioni 1, 8, 9) coincidono con gli output salvati, mentre corpus, loss e testi generati cambiano un po' con la versione di Python, come avverte il notebook stesso. **Nessun bug**; un solo commento fragile (cella 23, sullo scaling in miniatura). Nessuna figura: tutti gli output sono testuali.

### Notebook 1 · Loss e perplexity a mano

```python
for tok, p in [("all", 0.44), ("the", 0.33), ("your", 0.15), ("that", 0.08)]:
    print(tok, p, -np.log(p))
p = np.array([0.20, 0.50, 0.40, 0.80, 0.44])
losses = -np.log(p)
print(losses.mean(), np.prod(p) ** (-1 / len(p)), np.exp(losses.mean()))
print(0.001 ** (-1 / 4), 0.001 ** (-1 / 6))
```

Output:

```text
true next token all    probability 0.44  loss 0.82
...
true next token that   probability 0.08  loss 2.53

losses [1.61 0.69 0.92 0.22 0.82]  mean 0.8526
perplexity from the product: 2.3457
perplexity from the loss:    2.3457

tokenizer A, 4 tokens: 5.62   tokenizer B, 6 tokens: 3.16
```

I numeri delle [schede 18](L17-pretraining-dei-modelli-linguistici.md#p-18), [21](L17-pretraining-dei-modelli-linguistici.md#p-21), [56](L17-pretraining-dei-modelli-linguistici.md#p-56) e [57](L17-pretraining-dei-modelli-linguistici.md#p-57): le loss per token, la media 0,8526 e la perplexity calcolata nei due modi (prodotto alla $-1/T$ ed esponenziale della loss media), identica alla quarta cifra. In fondo l'avvertenza del tokenizzatore: 5,62 contro 3,16 per lo stesso testo.

### Notebook 2 · Il corpus e le finestre di contesto

```python
docs = [re.findall(r"[a-z]+", t.lower()) for t in texts]   # una docstring = un documento
itos = ["<eot>", "<unk>"] + [w for w, _ in counts.most_common(1498)]
def pack(indices):
    out = []
    for i in indices:
        out += [stoi.get(w, 1) for w in docs[i]] + [0]   # <eot> dopo ogni documento
    return np.array(out)
val_ids, train_ids = pack(order[:n_val]), pack(order[n_val:])
N = 32
print(decode(train_ids[1000:1000 + N]))
print(decode(train_ids[1001:1001 + N]))   # i target: stesso testo spostato di uno
```

Output:

```text
2703 documents, 110618 tokens
training tokens 102045  validation tokens 11276  vocabulary 1500  share of <unk> 0.095

one training window of 32 tokens (documents packed, separated by <eot>):
be determined <eot> returns a string identifying the python implementation ...
its targets, the same tokens shifted by one:
determined <eot> returns a string identifying the python implementation ...
```

Il corpus di pretraining in miniatura: le docstring di circa 130 moduli della libreria standard (funzioni, classi, metodi), una docstring per documento, **deduplicate** con un insieme `seen` (la deduplicazione esatta della [scheda 34](L17-pretraining-dei-modelli-linguistici.md#p-34)). Tokenizzazione a parole minuscole, vocabolario di 1.500 token: le 1.498 parole più frequenti più `<eot>` e `<unk>` (circa il 9,5% dei token è `<unk>`). Un documento su dieci va nel testo di validazione.

`pack` realizza il **packing** della [scheda 23](L17-pretraining-dei-modelli-linguistici.md#p-23): tutti i documenti in un unico flusso con `<eot>` fra l'uno e l'altro. La cella 5 mostra una finestra di 32 token che attraversa un confine di documento e i suoi target, lo stesso testo spostato di una posizione: ogni posizione è un esempio di training. I numeri esatti dipendono dalla versione di Python (nella mia esecuzione 2.755 documenti e 109.246 token, contro 2.703 e 110.618).

### Notebook 3 · Un piccolo transformer in numpy, con backward a mano

```python
d, d_ff = 64, 256
MASK = np.triu(np.full((N, N), -1e9), 1)          # maschera causale
def forward(p, ids, targets=None):
    x0 = p["E"][ids] + p["P"][:T]                     # token + posizione
    n1, c["ln1"] = layer_norm(x0, p["g1"], p["b1"])   # prenorm
    A = softmax(q @ k.transpose(0, 2, 1) / np.sqrt(dd) + MASK[:T, :T])
    x1 = x0 + (A @ v) @ p["Wo"]                        # residual stream
    x2 = x1 + relu(n2 @ W1 + c1) @ W2 + c2            # feedforward
    logits = layer_norm(x2) @ p["E"].T                 # weight tying
    loss = -np.log(prob[target]).mean()                # cross-entropy media
# backward(p, c): dl = (y_hat - y) / (B T), poi ogni operazione all'indietro
```

Output:

```text
parameters: 147,904  (E alone: 96,000; one block, without layer norms: 49,472)
E    backward -0.04655320   numerical -0.04655320
...
b2   backward -0.00101474   numerical -0.00101474

loss before training: 7.333   ln |V| = 7.313
```

Un transformer a **un blocco**, a una testa, come nelle lezioni precedenti: embedding dei token $E$ e delle posizioni appresi, layer norm prenorm, attenzione causale con la maschera $-10^9$ sopra la diagonale, feedforward ReLU con $d_{ff} = 4d$, layer norm finale e testa con **weight tying** (logit $= hE^\top$). La loss è la cross-entropy media su tutte le posizioni di tutte le finestre: teacher forcing e tutte le posizioni in parallelo ([scheda 22](L17-pretraining-dei-modelli-linguistici.md#p-22)).

Il backward è scritto a mano operazione per operazione (la backpropagation della [L13](L13-reti-neurali.md#p-56)), partendo dal gradiente della softmax con cross-entropy, $(\hat y - y)/(BT)$; la $E$ riceve gradiente sia dalla testa sia dall'input. Il **gradient check** confronta il gradiente analitico con $(\ell(w+\varepsilon)-\ell(w-\varepsilon))/2\varepsilon$ su dieci pesi: coincidono fino all'ottava cifra.

Conti: 147.904 parametri, di cui 96.000 nella sola $E$ ($1500\cdot64$) e 49.472 nel blocco ($12d^2 = 49.152$ più i bias del feedforward, 256 + 64). Con $d$ così piccolo, al contrario di GPT-3, gli embedding sono la maggior parte del modello. La loss iniziale è 7,333, vicina a $\ln|V| = \ln 1500 = 7{,}313$: pesi piccoli, distribuzione quasi uniforme (esercizio 1c).

### Notebook 4 · Pretraining, con i baseline n-gram

```python
uni = np.bincount(train_ids, minlength=V) + 1.0; uni /= uni.sum()     # unigram add-one
lp = -np.mean(np.log(0.7 * big_p[xs, ys] + 0.3 * uni[ys]))           # bigram interpolato
def train(p, steps, batch=16, lr=3e-3):
    for step in range(1, steps + 1):
        lr_t = lr * (0.1 + 0.45 * (1 + np.cos(np.pi * step / steps)))  # coseno, da lr a lr/10
        x, y = finestre casuali e le stesse spostate di uno            # teacher forcing
        loss, cache = forward(p, x, y); g = backward(p, cache)
        aggiornamento Adam (b1 = 0.9, b2 = 0.99)
history = train(params, 3000)
```

Output:

```text
unigram   validation loss 5.723  perplexity 305.7
bigram    validation loss 4.824  perplexity 124.5
step     1  batch loss 7.327  validation loss 7.173  perplexity  1303.8
step   300  batch loss 5.442  validation loss 5.450  perplexity   232.8
...
step  3000  batch loss 4.421  validation loss 5.012  perplexity   150.2

140 seconds, 1,536,000 training predictions
final validation perplexity: transformer 150.2, bigram 124.5
```

Il ciclo di pretraining completo: finestre casuali di 32 token, 16 per batch (512 predizioni per passo), cross-entropy media, **Adam** con learning rate che scende a coseno da $3\cdot10^{-3}$ a $3\cdot10^{-4}$ ([schede 61-62 della L13](L13-reti-neurali.md#p-61)). Ogni 300 passi si misura loss e perplexity sul testo di validazione, mai visto.

La perplexity di validazione parte da circa 1.300 (vicina a $|V|$) e scende a circa 150, veloce all'inizio e poi lenta. Il confronto onesto: con soli 100.000 token, un **bigram interpolato** della [L5](L05-smoothing-ed-entropia.md#p-23) (perplexity 124,5) batte il piccolo transformer (150,2). Non è un errore: il transformer guadagna con molti più dati, contesto e calcolo, che è esattamente ciò che dicono le scaling law. La batch loss (4,4) sotto la validation loss (5,0) indica un inizio di overfitting su così poco testo.

Le loss di validazione sono ottenute con `np.exp`, cioè perplexity = exp(loss media), la formula della [scheda 55](L17-pretraining-dei-modelli-linguistici.md#p-55). Nella mia esecuzione (corpus di 2.755 documenti invece di 2.703, per la diversa versione di Python) i numeri sono vicini ma non identici: transformer 143,4, bigram 122,4; la conclusione, bigram migliore del transformer, è la stessa. Su una CPU condivisa il training ha richiesto circa 24 minuti invece dei 140 secondi dell'output salvato.

### Notebook 5 · Generare testo, prima e dopo

```python
def generate(p, prompt, n=20, tau=0.8, top_k=20, seed=0):
    for _ in range(n):
        ctx = np.array(ids[-N:])[None]                  # al massimo N token di contesto
        logits = forward(p, ctx)[0, -1] / tau          # solo l'ultima posizione
        keep = np.argsort(logits)[-top_k:]
        ids.append(int(keep[r.choice(len(keep), p=softmax(logits[keep]))]))
```

Output:

```text
before training: return the endian implementation being continue while see set smtp generators ...
after training : return the current directory for the same <unk> <unk> of the number of the default <unk> <eot> return an optional module for
```

Generazione autoregressiva con temperatura 0,8 e top-k con $k = 20$ (il decoding della lezione precedente), dal prompt *return the*. Prima del training: parole del vocabolario a caso. Dopo: non è inglese corretto, ma lo stile delle docstring (*return the ... of the ...*, *return an optional module*) e il token `<eot>`, seguito da un nuovo inizio di documento: il modello ha imparato che i documenti finiscono, grazie al packing. In generazione si usa solo l'ultima posizione dei logit, mentre in training si usano tutte.

### Notebook 6 · La KV cache

```python
def step_cached(p, token, pos, cache):
    x0 = p["E"][token] + p["P"][pos]
    q, k, v = n1 @ p["Wq"], n1 @ p["Wk"], n1 @ p["Wv"]   # solo il token nuovo
    cache["K"].append(k); cache["V"].append(v)          # salva key e value
    a = softmax(np.array(cache["K"]) @ q / np.sqrt(len(q)))
    x1 = x0 + (a @ np.array(cache["V"])) @ p["Wo"]
    ...
cached = [step_cached(params, t, i, cache) for i, t in enumerate(ids)]
print(np.abs(cached - forward(params, ids[None])[0]).max())
```

Output:

```text
largest difference between the logits with and without the cache: 8.881784197001252e-15

key and value computations to process 32 tokens one at a time: without the cache 528, with the cache 32
time without the cache 9.0 ms, with the cache 4.1 ms (it depends on your computer)
memory of the cache: 2 x 32 x 64 = 4096 numbers, one layer
```

La [KV cache](L17-pretraining-dei-modelli-linguistici.md#p-45) in quindici righe: a ogni passo si calcolano query, key e value del solo token nuovo, si aggiungono key e value alla cache e si fa attenzione su tutte quelle salvate. Nessuna maschera: la cache contiene solo il passato, quindi la causalità è automatica. I logit coincidono con quelli del forward completo a meno di $10^{-14}$ (errori di arrotondamento).

Conteggi: per 32 token, senza cache $1+2+\dots+32 = 528$ calcoli di key e value, con la cache 32. Memoria: $2\cdot32\cdot64 = 4096$ numeri per un solo strato. I tempi dipendono dalla macchina; il vantaggio cresce con la lunghezza (per 1.000 token, 500.500 contro 1.000, esercizio 7c).

### Notebook 7 · Scaling in miniatura

```python
for dd in (16, 32, 64):
    p = init_params(dd, 4 * dd, seed=2)
    h = train(p, 800, log_every=800, quiet=True)
    non_emb = sum(v.size for k, v in p.items() if k not in ("E", "P"))
```

Output:

```text
d =  16   parameters outside the embeddings   3,248   training loss 5.006   validation loss 5.242
d =  32   parameters outside the embeddings  12,640   training loss 5.182   validation loss 5.362
d =  64   parameters outside the embeddings  49,856   training loss 4.609   validation loss 4.988
```

Tre modelli con $d$ = 16, 32, 64, stessi 800 passi e stessi dati; si contano i parametri **fuori dagli embedding**, come fa Kaplan ($12d^2$ più bias e layer norm: per $d = 16$, $3072 + 80 + 96 = 3248$). Nell'output salvato il più grande ha la loss più bassa, ma fra $d = 16$ e $d = 32$ l'ordine si inverte (e nella mia riesecuzione vince $d = 32$, vedi sotto): con modelli minuscoli e pochi passi le differenze sono nel rumore dell'inizializzazione. Le scaling law descrivono una tendenza su molti ordini di grandezza (la [scheda 50](L17-pretraining-dei-modelli-linguistici.md#p-50) copre sei decadi di $N$), non un fattore 4. L'ultimo suggerimento della cella 28 (provare $d = 128$ con gli stessi 800 passi) è il punto di Chinchilla: a calcolo fisso un modello più grande non è sempre meglio.

> **Attenzione (errore nelle slide): Il commento della cella 23 non è robusto**
>
> Il testo dice che il modello più grande, $d = 64$, ha la loss più bassa sia sul training sia sulla validazione. Nella mia riesecuzione (stesso codice, corpus leggermente diverso) non è così: $d = 16$: 5,073 / 5,238; $d = 32$: 4,997 / 5,184; $d = 64$: 5,055 / 5,223 (training / validazione). Vince $d = 32$ su entrambe. Non è un errore del codice, ma la frase va letta come il risultato di una run: con 800 passi e 100.000 token l'ordine fra le tre taglie è nel rumore, come il commento stesso ammette per $d = 16$ e $d = 32$. Per vedere davvero la tendenza servono più passi o più seed.

### Notebook 8 · Parametri, calcolo e scaling law dei modelli reali

```python
count = 12 * L * dm ** 2 + Vm * dm
kv = 2 * L * dm * 2                       # byte per token, 16 bit
print(6 * Np * D, D / Np)                # FLOP e token per parametro
L_N = lambda n: (n / 8.8e13) ** -0.076
```

Output:

```text
model             12 L d^2 + |V| d    table   KV cache per token   full context
GPT-2 XL                    1.55B     1.5B              0.31 MB         0.3 GB
GPT-3                     174.56B   175.0B              4.72 MB         9.7 GB
Llama 3.1 8B                6.97B     8.0B              0.52 MB        68.7 GB
Llama 3.1 405B            407.98B   405.0B              8.26 MB      1082.3 GB

  GPT-3            3.15e+23 FLOPs       1.7 tokens per parameter
  Gopher           5.04e+23 FLOPs       1.1 tokens per parameter
  Chinchilla       5.88e+23 FLOPs      20.0 tokens per parameter
  Llama 3.1 8B     7.20e+23 FLOPs    1875.0 tokens per parameter
  Llama 3.1 405B   3.65e+25 FLOPs      37.0 tokens per parameter

  N = 1e+08   loss 2.830 nats   perplexity 16.9
  N = 1e+09   loss 2.376 nats   perplexity 10.8
  N = 1e+10   loss 1.994 nats   perplexity 7.3
  2 times larger: x 0.949   10 times larger: x 0.839
```

Il conto $12Ld^2 + |V|d$ sui modelli della tabella ([scheda 43](L17-pretraining-dei-modelli-linguistici.md#p-43)), con la KV cache a 16 bit e key e value di dimensione $d$ ([scheda 47](L17-pretraining-dei-modelli-linguistici.md#p-47)), poi $6ND$ e la legge $L(N)$ di Kaplan. Esatto per GPT-2 e GPT-3; per Llama 3.1 8B il conto dà 6,97B contro 8B, perché SwiGLU usa tre matrici con $d_{ff} = 3{,}5d$ e gli embedding non sono legati (il conto esatto, 8,03B, è nell'approfondimento della scheda 43). Anche le colonne della cache valgono senza GQA: con la GQA di Llama 3.1 sono 4 volte (8B) e 16 volte (405B) più piccole. Il 407,98B di Llama 3.1 405B vicino a 405B è una coincidenza di errori che si compensano.

### Notebook 9 · Verifica degli esercizi della scheda

```python
print("1  ", -ln(0.6), -ln(0.1), ln(50000), ln(1500))
print("3  ", 3.2e6 / 2048, 300e9 / 3.2e6, 2048 - (700 + 1 + 900 + 1))
print("9  ", np.sqrt(C / 120), 20 * np.sqrt(C / 120))
def overlap(out, ref, clip=True): ...   # conteggio con o senza clipping
```

Output:

```text
1   0.511 2.303  uniform: 10.82 7.31
2   [2.303 1.204 0.693 0.511 0.916]  sum 5.627  mean 1.125
3   1562.5 windows, 93750.0 steps; 446 tokens fit, 154 go on
5   5000.0 19000.0 removed; share after 0.0461
6   84934656 38597376 786432 total 124318464 ; GPT-3 share of E 0.0035
7   153600 numbers, 307200 bytes, 314.6 MB; 1.08 TB, 67.6 GB; 500500
8   2.83 16.9 2.38 10.8 ; halve: 9139 ; 10x data: 0.804
9   5.88e+23 N 7e+10 D 1.4e+12 4C: N 1.4e+11 D 2.8e+12 Llama 8B 7.2e+23 ratio 1.22
10  3.081 3.081 ; 2.38 nats: 10.8 3.43 bits, 10.8
11  100.0 15.8 1000.0
12  0.7625 5 3 6
```

I numeri delle soluzioni degli esercizi 1-3 e 5-12 (il 4 chiede prompt, non conti). Li ho ricalcolati in modo indipendente: coincidono tutti con le soluzioni della sezione Studio. Nota sul 12a: 0,7625 è $610/800$, l'accuratezza sulle 800 domande non contaminate.

## Studio ed esercizi

### Guida allo studio (circa 4 h 00 min)

**Il progetto: date e cose da fare** (10 min)

Schede 2-8. Entro **martedì 27 ottobre** confermare il gruppo e il corresponding author; **venerdì 23 ottobre** esce la lista dei temi, conferma del tema entro **giovedì 29**; proposta via mail **lunedì 2 novembre** con l'oggetto nel formato esatto e le sei voci della scheda 6. Gruppo 5: round 1 mercoledì 11 novembre e round 2 mercoledì 25 novembre, entrambi 14-16 in FIB C1; poster il 3 dicembre.

**L'obiettivo di training** (45 min)

Schede 11-23. Saper scrivere la cross-entropy con $y$ one-hot e ridurla a $-\log\hat y_t[w_{t+1}]$; la loss media su $T$ posizioni; spiegare self-supervised, teacher forcing (e la differenza con l'inferenza), perché tutte le posizioni si calcolano in parallelo (target noti + maschera causale) e il packing con `eot`. Rifare a mano le tabelle delle schede 18 e 21. Libro §7.7 (pp. 201-202) e §1.6.1 (pp. 16-17). Esercizi 1, 2, 3.

**Task come generazione e dati** (35 min)

Schede 24-38. Saper riformulare sentiment, QA e riassunto come predizione del token successivo e dire il limite di un base model. Per i dati: Common Crawl e dati curati, The Pile, i tre filtri di qualità e quelli di sicurezza con il loro compromesso, copyright, privacy, consenso, skew, data-centric AI. Libro §1.2.1 (pp. 9-10), §1.6.1-1.6.2 (pp. 16-18). Esercizi 4, 5.

**Modelli, parametri e KV cache** (40 min)

Schede 41-47. Leggere la tabella dei modelli; ricavare $12Ld^2 + |V|d$ e applicarlo a GPT-3 e GPT-2 XL; spiegare la KV cache (perché si salvano key e value e non le query), calcolarne la memoria $2Ld\cdot b$ per token e dire perché la GQA la riduce. Libro §7.8 (pp. 204-205). Esercizi 6, 7, 13.

**Scaling law** (35 min)

Schede 49-52. Leggere i tre pannelli di Kaplan come rette in log-log e usare $L(N)$, $L(D)$; ricordare $C\approx6ND$ (e da dove viene), $N_{opt}, D_{opt}\propto C^{1/2}$, circa 20 token per parametro, il confronto Gopher-Chinchilla e perché Llama 3.1 8B va molto oltre. Libro §1.1 (p. 7). Esercizi 8, 9, 14.

**Valutazione** (40 min)

Schede 54-65. Definizione di perplexity, dimostrazione che è $\exp$ della cross-entropy media, calcolo nei due modi, l'avvertenza del tokenizzatore; accuratezza e benchmark (MMLU, BBH, GSM8k, AIME), contaminazione, giudici umani e LLM, metriche proxy e legge di Goodhart, altri fattori. Libro §7.7.1 (pp. 202-203) e §1.9 (pp. 25-29). Esercizi 10, 11, 12, 15.

**Notebook e ripasso orale** (35 min)

Eseguire il notebook (qualche minuto): seguire il training guardando la perplexity di validazione e il confronto con il bigram, la generazione prima e dopo, il test della KV cache. Provare uno degli esperimenti finali (togliere la maschera causale: la loss crolla perché il modello copia il token successivo). Chiudere con le domande d'orale, in particolare la dimostrazione perplexity-loss e il conto Chinchilla.

### Esercizi

#### Esercizio 1 (scheda L17): la cross-entropy loss

Dopo il contesto *the cat sat on the* un modello con vocabolario di quattro token (cat, dog, mat, the) dà $\hat y = [0{,}1;\ 0{,}2;\ 0{,}6;\ 0{,}1]$. Il vero token è *mat*.

1. Scrivi il vettore one-hot $y$ e calcola la loss $-\sum_w y[w]\log\hat y[w]$ termine per termine. Quali termini restano?
2. Quale sarebbe la loss se il vero token fosse *cat*?
3. Prima del training un modello dà circa la stessa probabilità a ogni token. Qual è la sua loss con $|V| = 50.000$? E con i 1.500 token del modello del notebook?

<details><summary>Soluzione</summary>

(a) $y = [0, 0, 1, 0]$. Termini: $0\cdot\ln0{,}1 + 0\cdot\ln0{,}2 + 1\cdot\ln0{,}6 + 0\cdot\ln0{,}1$; resta solo quello di *mat*: loss $= -\ln0{,}6 = 0{,}511$.

(b) $-\ln0{,}1 = 2{,}303$: probabilità più bassa, loss più alta.

(c) Uniforme: $\hat y[w] = 1/|V|$, loss $= \ln|V|$. $\ln50.000 = 10{,}82$; $\ln1.500 = 7{,}31$ (il notebook misura 7,333 prima del training).

</details>

#### Esercizio 2 (scheda L17): loss di una sequenza e teacher forcing

Un modello è addestrato sulla frase *the cat sat on the mat*. Le probabilità date ai veri token successivi sono: cat 0,10; sat 0,30; on 0,50; the 0,60; mat 0,40.

1. Calcola la loss a ogni posizione e la loss media.
2. Alla posizione di *sat* il token più probabile per il modello è *is*. Con il teacher forcing, qual è l'input alla posizione successiva? E in inferenza, quando il modello genera?
3. Quante predizioni del token successivo dà questa frase in un passaggio? Perché si possono calcolare tutte insieme?

<details><summary>Soluzione</summary>

(a) $-\ln$: 2,303; 1,204; 0,693; 0,511; 0,916. Somma 5,627, media **1,125**.

(b) Teacher forcing: l'input successivo è il vero *sat* (il contesto diventa *the cat sat*), la previsione *is* serve solo per la loss. In inferenza il modello usa il token che ha generato: se ha scelto *is*, prosegue da *the cat is*.

(c) 5 predizioni (cat, sat, on, the, mat, ciascuna dal prefisso precedente). Si calcolano insieme perché i target sono nel testo e la maschera causale impedisce a ogni posizione di vedere il proprio target: un forward dà le 5 distribuzioni.

</details>

#### Esercizio 3 (scheda L17): finestre e batch

1. Il GPT-3 più grande usava batch di 3,2 milioni di token e finestre di 2.048 token. Quante finestre ci sono in un batch? Con 300 miliardi di token di training, quanti passi di gradiente servono per un passaggio sui dati?
2. Tre documenti di 700, 900 e 600 token sono impacchettati in una finestra di 2.048, con un token di fine testo fra documenti consecutivi. Quanti token del terzo documento entrano? Che cosa succede al resto?
3. Perché conviene riempire la finestra invece di usare un documento per finestra con padding?

<details><summary>Soluzione</summary>

(a) $3{,}2\cdot10^6/2048 = 1562{,}5$ finestre (circa 1.560); $3\cdot10^{11}/3{,}2\cdot10^6 = 93.750$ passi.

(b) $700 + 1 + 900 + 1 = 1602$ token occupati; restano $2048 - 1602 = 446$ token del terzo documento. Gli altri $600 - 446 = 154$ vanno all'inizio della finestra successiva.

(c) Ogni posizione della finestra è un esempio di training: con il padding le posizioni vuote costano calcolo (e memoria) senza dare loss utile. Con il packing tutto il calcolo va in predizioni vere, e i documenti di lunghezze diverse non sprecano spazio.

</details>

#### Esercizio 4 (scheda L17): scrivere prompt

1. Scrivi un prompt per classificare il sentiment di *The food was cold and the waiter was rude* con un base model. Quali due probabilità confronti?
2. Il modello dà $P(\textit{positive}\mid\text{prompt}) = 0{,}05$, $P(\textit{negative}\mid\text{prompt}) = 0{,}30$, mentre $P(\textit{bad}\mid\text{prompt}) = 0{,}40$. Quale etichetta assegni? Perché è un problema che *bad* sia più probabile di entrambe le parole-etichetta?
3. Scrivi prompt che riformulino come predizione di parole: una domanda sulla capitale dell'Australia, la traduzione di *good morning* in italiano, il riassunto di un testo lungo.

<details><summary>Soluzione</summary>

(a) `The sentiment of the sentence "The food was cold and the waiter was rude" is:` e si confrontano $P(\textit{positive}\mid\text{prompt})$ e $P(\textit{negative}\mid\text{prompt})$.

(b) **negative**: fra le due parole-etichetta è la più probabile ($0{,}30 &gt; 0{,}05$; rinormalizzando, $0{,}30/0{,}35 = 0{,}86$). Il problema: il modello non sa che deve scegliere fra due etichette, continua il testo in modo naturale, e la massa di probabilità si sparpaglia su sinonimi (*bad*, *negative.*, *terrible*). Le probabilità delle etichette diventano piccole e rumorose; un base model non segue il formato richiesto. Rimedi: elencare le opzioni nel prompt, dare esempi (few-shot), sommare le probabilità di più parole per etichetta, o usare un modello instruction-tuned.

(c) `Q: What is the capital of Australia? A:` (continuazione attesa: *Canberra*). `English: good morning\nItalian:` (attesa: *buongiorno*). `[testo lungo] tl;dr:` (attesa: un riassunto breve).

</details>

#### Esercizio 5 (scheda L17): filtri e skew

Un crawl ha 1.000.000 di documenti; 50.000 (5%) sono scritti in un dialetto minoritario. Un classificatore di tossicità segnala per errore il 10% dei documenti nel dialetto e il 2% degli altri, tutti non tossici (numeri inventati).

1. Quanti documenti di ciascun gruppo rimuove il filtro? Qual è la quota del dialetto dopo il filtro?
2. Che cosa vede di meno un modello addestrato sui dati filtrati? Quale problema della lezione mostra l'esempio?
3. Nomina un problema dei dati di training che nessun filtro sul contenuto di un singolo documento può risolvere.

<details><summary>Soluzione</summary>

(a) Dialetto: $0{,}10\cdot50.000 = 5.000$ rimossi, ne restano 45.000. Altri: $0{,}02\cdot950.000 = 19.000$ rimossi, ne restano 931.000. Quota del dialetto: $45.000/976.000 = 4{,}61\%$ (prima 5,00%).

(b) Vede meno testo nel dialetto minoritario, quindi lo modellerà peggio (perplexity più alta, generazioni meno adatte a chi lo parla). È il problema dei **falsi allarmi** dei classificatori di tossicità sui dialetti minoritari (Xu et al., 2021), che si somma allo **skew** del corpus.

(c) Lo **skew** complessivo (chi ha scritto il corpus è una proprietà della distribuzione, non di un testo); il **copyright** o il **consenso** (dipendono dalla provenienza, non dal contenuto); i **duplicati** (si vedono solo confrontando documenti); la **contaminazione** con i test set (si vede solo confrontando con i benchmark).

</details>

#### Esercizio 6 (scheda L17): contare i parametri

Usa il conto della lezione: $12Ld^2$ per i blocchi e $|V|d$ per $E$ (weight tying, niente bias, niente layer norm).

1. GPT-2 small ha $L = 12$, $d = 768$, $|V| = 50.257$ e 1.024 posizioni apprese. Conta i parametri dei blocchi, di $E$ e degli embedding di posizione. Confronta con i 124 milioni di solito indicati.
2. In GPT-3 ($L = 96$, $d = 12.288$, stesso vocabolario), che frazione dei parametri è in $E$?
3. In un blocco, che quota dei $12d^2$ è attenzione e quale feedforward?

<details><summary>Soluzione</summary>

(a) Blocchi: $12\cdot12\cdot768^2 = 84.934.656$. $E$: $50.257\cdot768 = 38.597.376$. Posizioni: $1.024\cdot768 = 786.432$. Totale **124.318.464**, circa 124,3M: i 124M indicati. La differenza minima sono bias e layer norm (circa 0,1M), trascurati. Qui $E$ è il 31% del modello.

(b) $E = 50.257\cdot12.288 = 0{,}618$B; totale $173{,}95 + 0{,}62 = 174{,}56$B; frazione $0{,}0035$, lo **0,35%**. Con $d$ grande il termine $d^2$ domina.

(c) Attenzione $4d^2/12d^2 = 1/3$; feedforward $8d^2/12d^2 = 2/3$.

</details>

#### Esercizio 7 (scheda L17): la KV cache

Key e value in numeri a 16 bit (2 byte), teste insieme: $d$ numeri per una key e $d$ per un value, in ogni strato.

1. GPT-2 XL ha $L = 48$, $d = 1.600$. Quanti byte servono per token? E per un contesto pieno di 1.024 token?
2. Llama 3.1 405B ha $L = 126$, $d = 16.384$ e contesto di 128K token (131.072). Quanto sarebbe grande la cache a contesto pieno? Con la Grouped-Query Attention key e value hanno dimensione 1.024 invece di 16.384: quanto diventa?
3. Senza cache, per generare il token in posizione $i$ ricalcoliamo key e value di tutti gli $i$ token (in ogni strato). Generando 1.000 token, quanti calcoli di key e value per strato servono, contro quanti con la cache?

<details><summary>Soluzione</summary>

(a) $2Ld = 2\cdot48\cdot1600 = 153.600$ numeri $= 307.200$ byte (0,31 MB) per token; per 1.024 token $314{,}6$ MB.

(b) $2\cdot126\cdot16.384\cdot2 = 8{,}26$ MB per token; $\times131.072 = 1{,}08\cdot10^{12}$ byte, circa **1,08 TB** per una sequenza. Con la GQA: $2\cdot126\cdot1.024\cdot2\cdot131.072 = 67{,}6$ GB, 16 volte meno.

(c) Senza cache: $1 + 2 + \dots + 1000 = 1000\cdot1001/2 = 500.500$; con la cache 1.000 (uno per token nuovo).

</details>

#### Esercizio 8 (scheda L17): una legge di potenza

Kaplan et al. (2020): $L(N) = (N/8{,}8\cdot10^{13})^{-0{,}076}$ (nat per token, $N$ parametri fuori dagli embedding) e $L(D) = (D/5{,}4\cdot10^{13})^{-0{,}095}$.

1. Calcola $L(N)$ per $N = 10^8$ e $10^9$, e le perplexity corrispondenti.
2. Di quante volte deve crescere un modello per dimezzare la loss?
3. Di che fattore cambia la loss con 10 volte più dati, secondo $L(D)$?

<details><summary>Soluzione</summary>

(a) $L(10^8) = (10^8/8{,}8\cdot10^{13})^{-0{,}076} = e^{0{,}076\cdot13{,}69} = 2{,}83$ nat, perplexity $e^{2{,}83} = 16{,}9$. $L(10^9) = 2{,}38$, perplexity 10,8.

(b) Moltiplicando $N$ per $k$ la loss si moltiplica per $k^{-0{,}076}$. Dimezzare: $k^{-0{,}076} = 1/2$, $k = 2^{1/0{,}076} = 2^{13{,}16}\approx 9.100$ (9.139). Un modello quasi diecimila volte più grande.

(c) $10^{-0{,}095} = 0{,}804$: la loss scende di circa il 20%.

</details>

#### Esercizio 9 (scheda L17): spendere un budget di calcolo

Usa $C\approx6ND$ FLOP.

1. Calcola $C$ per Chinchilla ($N = 70$B, $D = 1{,}4$T).
2. Con questo $C$ e la regola $D = 20N$, trova $N$ e $D$. Con 4 volte il calcolo, che cosa diventano $N$ e $D$ secondo Hoffmann et al. (2022)?
3. Llama 3.1 8B è stato addestrato su 15T token. Calcola il suo $C$ e confrontalo con Chinchilla. Perché addestrare un modello 9 volte più piccolo di Chinchilla con un budget simile?

<details><summary>Soluzione</summary>

(a) $C = 6\cdot7\cdot10^{10}\cdot1{,}4\cdot10^{12} = 5{,}88\cdot10^{23}$ FLOP.

(b) $C = 6N\cdot20N = 120N^2$, $N = \sqrt{C/120} = \sqrt{4{,}9\cdot10^{21}} = 7\cdot10^{10} = 70$B, $D = 1{,}4$T: proprio Chinchilla. Con $4C$: $N$ e $D$ crescono come $\sqrt{C}$, quindi raddoppiano: 140B e 2,8T.

(c) $C = 6\cdot8\cdot10^9\cdot1{,}5\cdot10^{13} = 7{,}2\cdot10^{23}$, 1,22 volte Chinchilla. Motivo: il costo di **inferenza** è proporzionale a $N$ e si paga a ogni prompt; un modello da 8B è circa 9 volte più economico da usare di uno da 70B. Spendendo il calcolo di training su più token (1.875 per parametro) si ottiene il modello piccolo migliore possibile, anche se non è il punto compute-optimal per il solo training.

</details>

#### Esercizio 10 (scheda L17): perplexity e loss

1. Mostra che la perplexity $P(w_{1:T})^{-1/T}$ (Eq. 7.57) è l'esponenziale della cross-entropy media (Eq. 7.58).
2. Calcola la perplexity della frase dell'esercizio 2 nei due modi.
3. Un modello ha loss media 2,38 nat per token. Qual è la sua perplexity? Quanto vale la loss in bit, e la perplexity cambia se si usa $\log_2$?

<details><summary>Soluzione</summary>

(a) $\ln\mathrm{PP} = -\frac1T\ln P(w_{1:T}) = -\frac1T\ln\prod_t P(w_t\mid w_{&lt;t}) = \frac1T\sum_t -\ln P(w_t\mid w_{&lt;t}) = L_{CE}$, quindi $\mathrm{PP} = e^{L_{CE}}$.

(b) Prodotto: $0{,}1\cdot0{,}3\cdot0{,}5\cdot0{,}6\cdot0{,}4 = 0{,}0036$; $0{,}0036^{-1/5} = 3{,}081$. Dalla loss: $e^{1{,}1254} = 3{,}081$.

(c) $e^{2{,}38} = 10{,}8$. In bit: $2{,}38/\ln2 = 3{,}43$ bit; $2^{3{,}43} = 10{,}8$: la perplexity non cambia, purché si esponenzi con la stessa base del logaritmo.

</details>

#### Esercizio 11 (scheda L17): perplexity e tokenizzatori

Due modelli danno la stessa probabilità, $10^{-6}$, al testo *unbelievably slow*. Il tokenizzatore di A lo divide in 3 token, quello di B in 5 (numeri inventati).

1. Calcola la perplexity di ciascun modello su questo testo.
2. Quale modello è migliore su questo testo?
3. Calcola la perplexity per parola, normalizzando per le 2 parole. Che cosa mostra?

<details><summary>Soluzione</summary>

(a) A: $(10^{-6})^{-1/3} = 10^2 = 100$. B: $(10^{-6})^{-1/5} = 10^{1{,}2} = 15{,}8$.

(b) Nessuno: danno la stessa probabilità al testo. B sembra migliore solo perché divide la stessa probabilità in più token.

(c) $(10^{-6})^{-1/2} = 1000$ per entrambi. Normalizzando per un'unità indipendente dal tokenizzatore (parole, caratteri, byte) le perplexity tornano confrontabili e uguali.

</details>

#### Esercizio 12 (scheda L17): benchmark e metriche proxy

1. Un modello risponde bene a 800 domande su 1.000 di un benchmark. Poi si scopre che 200 domande erano nei suoi dati di training, e a 190 di queste ha risposto bene. Qual è l'accuratezza sulle altre domande?
2. La traduzione di riferimento è *the president met the press on monday*. Conta i token di ogni output che compaiono nel riferimento, usando ogni token del riferimento al massimo una volta: (1) *on monday the president met reporters*; (2) *the press the press the press*. Senza il limite di una volta, quanto prenderebbe l'output 2?
3. Spiega il risultato di (b) con la legge di Goodhart.

<details><summary>Soluzione</summary>

(a) Domande pulite: $1000 - 200 = 800$; corrette fra queste: $800 - 190 = 610$. Accuratezza $610/800 = 76{,}25\%$, contro l'80% dichiarato.

(b) Riferimento: the ×2, president, met, press, on, monday. (1) on, monday, the, president, met: **5 su 6** (reporters no). (2) the, press, the: **3 su 6** (il terzo *press* e il terzo *the* non hanno più corrispondenti). Senza limite: 6 su 6, punteggio pieno.

(c) Senza il clipping la metrica premia la ripetizione di parole frequenti del riferimento: un sistema ottimizzato per massimizzarla imparerebbe a produrre *the press the press*, che non è una traduzione. La misura diventata obiettivo smette di misurare la qualità; il clipping (come in BLEU) chiude questo buco specifico, ma l'ottimizzazione aggressiva ne troverà altri.

</details>

#### Esercizio 13 (nostro): parametri e cache di un modello moderno

Llama 3.1 8B: $L = 32$, $d = 4096$, 32 teste di query da 128, 8 teste di key/value da 128 (GQA), feedforward SwiGLU con tre matrici $d\times d_{ff}$ e $d_{ff} = 14.336$, $|V| = 128.256$, embedding di input e di output separati.

1. Conta i parametri di uno strato (senza layer norm) e del modello. Confronta con $12Ld^2 + |V|d$.
2. Calcola la KV cache per token (16 bit) e per un contesto di 128K token (131.072), con e senza GQA.

<details><summary>Soluzione</summary>

(a) Attenzione: $W^Q$ e $W^O$ sono $4096\times4096$, $W^K$ e $W^V$ sono $4096\times1024$: $2\cdot16{,}78$M $+ 2\cdot4{,}19$M $= 41{,}9$M. Feedforward: $3\cdot4096\cdot14.336 = 176{,}2$M. Strato: 218,1M; per 32 strati 6,98B. Embedding: $2\cdot128.256\cdot4096 = 1{,}05$B. Totale **8,03B**. La formula semplice dà $12\cdot32\cdot4096^2 + 128.256\cdot4096 = 6{,}44 + 0{,}53 = 6{,}97$B: sottostima perché il feedforward ha $3\cdot3{,}5 = 10{,}5\,d^2$ invece di $8d^2$ e l'embedding è contato una volta sola, e sovrastima l'attenzione ($2{,}5d^2$ invece di $4d^2$).

(b) Con GQA: $2\cdot32\cdot1024\cdot2 = 131.072$ byte per token (128 KiB); per 131.072 token $17{,}2$ GB. Senza GQA ($d_{kv} = 4096$): 524.288 byte per token, 68,7 GB. Fattore 4 = 32 teste di query / 8 di key-value.

</details>

#### Esercizio 14 (nostro): il budget di GPT-3 speso alla Chinchilla

GPT-3 aveva 175B parametri ed è stato addestrato su 300B token.

1. Calcola il suo calcolo di training con $C\approx6ND$ e i token per parametro.
2. Con lo stesso $C$ e la regola dei 20 token per parametro, quale $N$ e quale $D$ sarebbero stati ottimali?
3. Con $L(N)$ di Kaplan, quanto peggiora la loss passando da 175B a quel $N$ ottimale, se i dati non fossero un limite? Perché questo non contraddice Chinchilla?

<details><summary>Soluzione</summary>

(a) $C = 6\cdot1{,}75\cdot10^{11}\cdot3\cdot10^{11} = 3{,}15\cdot10^{23}$ FLOP; $300/175 = 1{,}7$ token per parametro.

(b) $N = \sqrt{C/120} = \sqrt{2{,}625\cdot10^{21}} = 5{,}1\cdot10^{10}$, circa **51B**; $D = 20N = 1{,}0$T token.

(c) Rapporto delle loss $(51/175)^{-0{,}076} = 1{,}098$: circa +10% con dati illimitati. Ma $L(N)$ vale solo quando i dati non limitano; GPT-3 era limitato dai dati (1,7 token per parametro, ben lontano dalla convergenza), e a calcolo fisso il guadagno di vedere 3,4 volte più token supera la perdita dovuta a un modello più piccolo. È esattamente la conclusione di Hoffmann et al.: a parità di $C$ conviene bilanciare $N$ e $D$.

</details>

#### Esercizio 15 (nostro): perplexity di un modello uniforme e contaminazione

1. Mostra che un modello che dà probabilità $1/|V|$ a ogni token ha perplexity $|V|$ su qualunque testo. Quanto vale per il modello del notebook prima del training?
2. Un modello ha perplexity 20 su un test set pulito e 8 su un test set che si scopre essere per metà nel training. Assumendo perplexity 20 sulla metà pulita e loss media sulla metà contaminata uguale per tutti i token, quanto vale la perplexity sulla metà contaminata? (le due metà hanno lo stesso numero di token)

<details><summary>Soluzione</summary>

(a) $P(w_{1:T}) = |V|^{-T}$, quindi $P^{-1/T} = |V|$. Equivalente: loss $\ln|V|$ e $e^{\ln|V|} = |V|$. Per il notebook circa 1.500 (misurato 1.304 al primo passo e $e^{7{,}333} = 1.529$ prima del training: i pesi casuali non danno una distribuzione esattamente uniforme).

(b) La loss media è la media delle due metà: $\ln8 = \tfrac12(\ln20 + \ell)$, quindi $\ell = 2\ln8 - \ln20 = 4{,}159 - 2{,}996 = 1{,}163$ e la perplexity sulla metà contaminata è $e^{1{,}163} = 3{,}2$ ($= 64/20$). La perplexity complessiva 8 è la media geometrica di 20 e 3,2: la parte memorizzata abbassa molto il numero totale, e il valore da riportare è 20.

</details>

### Domande tipo orale

<details><summary>Che cos'è il pretraining e perché si dice self-supervised?</summary>

Traccia: (1) primo dei quattro stadi di training, su trilioni di token, produce un base model; (2) obiettivo: predire il token successivo a ogni posizione (Shannon game con correzione); (3) self-supervised: i target sono nel testo, nessuna annotazione; formalmente MLE condizionata, ogni token è un esempio; (4) si aggiornano tutti i pesi con backpropagation e un ottimizzatore come Adam, compresi gli embedding; (5) il modello impara lingua e conoscenza come effetto collaterale; (6) limite: continua testo, non segue istruzioni.

</details>

<details><summary>Scrivi la cross-entropy loss del language modeling e spiega perché si riduce a meno il log di una probabilità.</summary>

Traccia: (1) $L_{CE} = -\sum_w y_t[w]\log\hat y_t[w]$ fra distribuzione predetta e corretta su $V$; (2) $y_t$ one-hot sul vero token $w_{t+1}$, tutti gli altri termini si annullano; (3) resta $-\log\hat y_t[w_{t+1}]$; (4) probabilità 1 dà loss 0, probabilità vicina a 0 loss enorme; esempio 0,44 dà 0,82; (5) sulla sequenza si fa la media sulle $T$ posizioni; (6) stessa loss della regressione logistica con $|V|$ classi; minimizzarla = massimizzare la verosimiglianza; log naturale, nat.

</details>

<details><summary>Che cos'è il teacher forcing? Quali vantaggi ha e che differenza crea con l'inferenza?</summary>

Traccia: (1) in training a ogni posizione il contesto è il testo vero, non la previsione del modello; (2) esempio: il modello scommette *the*, il vero è *all*, si prosegue con *all*; (3) la previsione serve solo per la loss; (4) vantaggi: errori che non si propagano, contesti noti in anticipo quindi tutte le posizioni in parallelo; (5) in inferenza il modello si nutre delle proprie uscite: situazione mai vista in training (exposure bias).

</details>

<details><summary>Perché il pretraining di un transformer si può fare in parallelo su tutte le posizioni, e come si riempie la finestra?</summary>

Traccia: (1) target noti: il token successivo di ogni posizione è nel testo; (2) maschera causale: nessuna posizione vede il proprio target, l'output di ciascuna non dipende dal futuro; (3) un forward con la forma matriciale dà $N$ distribuzioni e $N$ loss; (4) senza maschera il modello copierebbe il successivo; (5) packing: documenti corti concatenati con `eot` per riempire la finestra, niente padding sprecato; (6) batch grandi: GPT-3 3,2M token, circa 1.560 finestre da 2.048.

</details>

<details><summary>Come può un modello addestrato solo a predire il token successivo fare sentiment analysis o rispondere a domande?</summary>

Traccia: (1) generazione condizionata: il task scritto nel prompt, il modello lo continua; (2) sentiment: prompt *The sentiment of ... is:* e confronto di $P(\textit{positive})$ e $P(\textit{negative})$, 0,42 contro 0,03; (3) QA: *Q: ... A:*, poi *Charles*, poi *Darwin*, un token alla volta; (4) riassunto con `tl;dr`; (5) funziona perché il web è pieno di task svolti; (6) limite: un base model non segue istruzioni in modo affidabile, serve instruction tuning.

</details>

<details><summary>Da dove vengono i dati di pretraining e come si filtrano? Quali problemi pongono i filtri?</summary>

Traccia: (1) soprattutto Common Crawl (istantanee del web, miliardi di pagine), più dati curati (Wikipedia, libri); The Pile come esempio di mix di 22 fonti; (2) scala: Llama 3.1 15T token, circa 71.000 anni di lettura; (3) filtri di qualità: deduplicazione, boilerplate, contenuti per adulti, spesso classificatori con punteggio; (4) filtri di sicurezza: classificatori di tossicità; (5) problemi: falsi allarmi su dialetti minoritari come l'AAE, modelli meno tossici ma peggiori a riconoscere la tossicità; filtrare meglio è un problema aperto.

</details>

<details><summary>Quali questioni etiche e legali pongono i dati di pretraining?</summary>

Traccia: (1) copyright: libri e articoli protetti; fair use negli USA incerto, compenso non risolto; (2) casi: Bartz v. Anthropic (training fair use, ma non i libri piratati: 1,5 miliardi), NYT v. OpenAI aperto, GEMA v. OpenAI (testi memorizzati nei pesi = copia); (3) privacy: telefoni, email; (4) consenso dei siti; (5) skew verso autori di USA e paesi sviluppati; (6) data-centric AI: chiedersi provenienza, autori, compenso, liceità.

</details>

<details><summary>Conta i parametri di un transformer come GPT-3 e verifica i 175B.</summary>

Traccia: (1) attenzione $W^Q,W^K,W^V,W^O$: $4d^2$; (2) feedforward $d\times4d$ e $4d\times d$: $8d^2$; (3) strato $12d^2$, modello $12Ld^2 + |V|d$; (4) ipotesi: niente bias e layer norm, weight tying; (5) GPT-3: $12\cdot96\cdot12288^2 = 174{,}0$B più $50\text{K}\cdot12288 = 0{,}6$B, 174,6B; GPT-2 XL 1,55B; (6) i modelli moderni (GQA, SwiGLU, embedding non legati) si discostano: Llama 3.1 8B 6,97B dalla formula contro 8,03B.

</details>

<details><summary>Che cos'è la KV cache, perché funziona e quanto costa in memoria?</summary>

Traccia: (1) in training tutti i token insieme; in inferenza un token nuovo alla volta; (2) key e value dei token precedenti non cambiano (causalità), ricalcolarli è uno spreco; (3) si salvano key e value, si calcola solo $q_i, k_i, v_i$ del nuovo token; le query e i punteggi no; (4) calcoli di key/value: $n(n+1)/2$ senza cache contro $n$; (5) memoria $2Ld$ numeri per token: GPT-3 $2\cdot96\cdot12288 = 2{,}36$M, 4,7 MB a 16 bit, 9,7 GB per 2.048 token; (6) cresce con contesto e sequenze; GQA la riduce condividendo key e value fra teste.

</details>

<details><summary>Che cosa dicono le scaling law di Kaplan et al. (2020)?</summary>

Traccia: (1) tre fattori: parametri $N$, token $D$, calcolo $C$; (2) la test loss scende come legge di potenza di ciascuno, $L = (X/X_c)^{-\alpha}$, retta in log-log; (3) esponenti: 0,076 per $N$, 0,095 per $D$, 0,050 per $C$; (4) ogni legge vale se gli altri fattori non limitano; (5) esempio: $L(10^9) = 2{,}38$ nat, perplexity 10,8; per dimezzare la loss serve un modello circa 9.000 volte più grande; (6) conseguenza: più grande è meglio, in modo prevedibile, quindi modelli sempre più grandi, con costi di energia e acqua.

</details>

<details><summary>Come si spende in modo ottimale un budget di calcolo? Spiega Chinchilla e il 6ND.</summary>

Traccia: (1) $C\approx6ND$: 2 FLOP per parametro per token nel forward, 4 nel backward; (2) a $C$ fisso, più parametri vuol dire meno token; (3) Hoffmann et al.: $N_{opt}\propto C^{1/2}$, $D_{opt}\propto C^{1/2}$; (4) circa 20 token per parametro, quindi $C = 120N^2$; (5) Chinchilla 70B e 1,4T batte Gopher 280B e 300B con budget simile ($5{,}9$ contro $5{,}0\cdot10^{23}$ con 6ND); (6) GPT-3 con 1,7 token per parametro era troppo grande per i suoi dati.

</details>

<details><summary>Perché Llama 3.1 8B è stato addestrato con quasi 1.900 token per parametro, ben oltre Chinchilla?</summary>

Traccia: (1) Chinchilla minimizza la loss a parità di calcolo di training; (2) ma l'inferenza costa a ogni prompt, circa proporzionale a $N$; (3) un modello piccolo addestrato più a lungo è più economico da servire; (4) la loss continua a scendere oltre i 20 token per parametro, solo più lentamente; (5) numeri: 15T/8B = 1.875; calcolo $7{,}2\cdot10^{23}$, simile a Chinchilla con un modello 9 volte più piccolo; (6) Llama 3.1 405B invece 37 token per parametro.

</details>

<details><summary>Definisci la perplexity e dimostra che è l'esponenziale della cross-entropy media.</summary>

Traccia: (1) likelihood = prodotto delle probabilità dei token, decresce con la lunghezza; (2) perplexity $= P(w_{1:T})^{-1/T}$, inverso normalizzato per la lunghezza, misura per token; (3) $\ln\mathrm{PP} = \frac1T\sum -\ln P(w_t\mid w_{&lt;t}) = L_{CE}$; (4) quindi $\mathrm{PP} = e^{L_{CE}}$, con loss in nat; in bit $2^{H}$, stesso numero; (5) esempio: prodotto 0,01408, $0{,}01408^{-1/5} = 2{,}35 = e^{0{,}853}$; (6) interpretazione: scelta fra circa 2,35 token equiprobabili; più bassa è meglio.

</details>

<details><summary>Perché non si possono confrontare le perplexity di modelli con tokenizzatori diversi?</summary>

Traccia: (1) la perplexity normalizza per il numero di token $T$; (2) stesso testo, stessa probabilità 0,001: con 4 token 5,6, con 6 token 3,2; (3) la qualità del modello sul testo è identica, cambia solo la divisione; (4) un tokenizzatore che spezza di più fa sembrare il modello migliore; (5) regola: stessa tokenizzazione, oppure normalizzare per un'unità comune (parole, caratteri, byte).

</details>

<details><summary>Come si valutano gli LLM oltre la perplexity? Che cos'è la data contamination?</summary>

Traccia: (1) accuratezza su test set etichettati e mai visti; (2) benchmark da esami umani: MMLU (15.908 domande in 57 aree), BigBench Hard, GSM8k, AIME24; proxy di conoscenza e ragionamento; (3) contaminazione: il test finisce nel training perché entrambi sono sul web; la metrica sovrastima; (4) esempio: 90% complessivo, ma 86% sulle 70 domande pulite; (5) rimedio: pubblicare i dati o la sovrapposizione con i test, modelli completamente open.

</details>

<details><summary>Come si valutano i task con molte risposte corrette? Che cosa sono le metriche proxy e la legge di Goodhart?</summary>

Traccia: (1) task soggettivi: conversazione, traduzione, sycophancy; (2) giudici umani con rubrica (fedeltà, fluenza), scelti per competenza o varietà di provenienza; (3) LLM-as-a-judge: più economico e meno dannoso per le persone, prompt curato e verificato su un campione umano, singolo o a coppie; (4) metriche proxy: sovrapposizione di token (chrF, BLEU, ROUGE), WER; esempio 5/6 contro 2/7; comode ma imperfette, verificare la significatività; (5) Goodhart: ottimizzando la metrica si ottimizzano proprietà casuali e la metrica peggiora come proxy.

</details>

<details><summary>Oltre all'accuratezza, quali altri fattori conta valutare in un modello?</summary>

Traccia: (1) efficienza: dimensione, tempo di training e inferenza, memoria GPU, prestazione a budget fisso; (2) energia: kWh, kg di CO$_2$, green AI; (3) sicurezza e bias: linguaggio tossico e stereotipi, con StereoSet, RealToxicityPrompts, BBQ; (4) equità: prestazioni buone per tutti i gruppi, criterio del gruppo più svantaggiato invece della media; (5) collegamento con i dati: skew e filtri influenzano bias ed equità.

</details>
