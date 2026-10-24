# L18 · Post-training I: instruction tuning, LoRA e prompting

*Post-training: Instruction Tuning* · 23/10/2026 · Claudio Gallicchio · lettura: J&M cap. 8, §8.1-8.2; cap. 1, §1.6.2 e §1.7

[Versione interattiva sul sito](https://gabriele-marsili.github.io/appunti-magistrale-ai/anno-2/hlt/sito/#L18) · [Indice della dispensa](README.md)

Prima lezione sul **post-training**: un base model continua il testo ma non segue le istruzioni ed è poco sicuro, perché l'obiettivo del pretraining è disallineato da ciò che serve alle persone. L'**instruction tuning** (SFT) lo corregge con la stessa cross-entropy del pretraining, calcolata **solo sulla risposta**, su dati scritti da persone, convertiti da dataset NLP o generati da LLM, con un **chat template**. Poiché il fine-tuning completo costa 16 byte per parametro (112 GB per un 7B), si usa **LoRA**: $W$ congelata e $h = xW + xAB$ con $r(k+d)$ parametri invece di $kd$; con **QLoRA** il modello base sta in 4 bit. Infine il **prompting** (zero-shot, few-shot, system prompt) e l'**in-context learning**, che adatta il modello senza toccare i pesi. In apertura, temi e scadenze del progetto di gruppo.

## Indice

- [Apertura e progetto](#apertura-e-progetto)
- [Perché il post-training](#perche-il-post-training)
- [Instruction tuning](#instruction-tuning)
- [Dati di istruzione](#dati-di-istruzione)
- [PEFT e LoRA](#peft-e-lora)
- [Prompting e in-context learning](#prompting-e-in-context-learning)
- [Notebook](#notebook)
- [Studio ed esercizi](#studio-ed-esercizi)

## Apertura e progetto

<a id="p-1"></a>

### Slide 1 · Post-training I: instruction tuning

Lezione 18, di Claudio Gallicchio (23 ottobre 2026). Si apre il **post-training**: tutto ciò che si fa su un language model *dopo* il pretraining della L17. Il sottotitolo dà i tre temi della giornata:

- **instructions**: l'**instruction tuning** (SFT), cioè addestrare il modello su coppie istruzione-risposta, e da dove vengono questi dati;
- **efficient fine-tuning with LoRA**: come fare fine-tuning di un modello enorme aggiornando una frazione minima dei parametri;
- **prompting**: adattare il modello senza toccare i pesi, con istruzioni, dimostrazioni e system prompt.

È la prima di due lezioni sul post-training: la seconda (lo stesso giorno, 16-18) tratta preferenze, RLHF, DPO e ragionamento. Le prime tre slide dopo il titolo sono organizzative: temi e scadenze del progetto di gruppo.

<a id="p-2"></a>

### Slide 2 · Temi del progetto: come funziona

Scheda organizzativa. Le regole:

- **tema provvisorio**: il tema $n$ va al gruppo $n$, per i temi 1-12;
- un tema **fissa il task**; dataset, modelli e dominio li sceglie il gruppo;
- si può **scambiare** il tema con un altro gruppo, sceglierne un altro (anche fra il 13 e il 18) o **proporne uno proprio**, nello stesso spirito e motivato.

**Cosa fare**:

- entro **martedì 27 ottobre** i gruppi si chiudono: si scelgono per le persone, il tema può ancora cambiare;
- entro **giovedì 29 ottobre** ogni gruppo scrive il **tema definitivo** nel file condiviso, foglio *Topics*.

Per Octech: gruppo 5, quindi tema provvisorio 5, *Hate Speech and Offensive Language Detection* (scheda successiva). Se il gruppo lo conferma, basta scriverlo nel foglio Topics entro il 29.

<a id="p-3"></a>

### Slide 3 · Temi del progetto: la lista

Diciotto temi: i primi dodici sono i provvisori dei gruppi 1-12, gli altri sei sono *other options*.

| n | Tema | n | Tema |
| --- | --- | --- | --- |
| 1 | Sentiment Analysis: When Does Fine-Tuning Beat Prompting? | 13 | Abstractive Summarization |
| 2 | Instruction Tuning a Small LLM with LoRA | 14 | Tokenization and the Cost of a Language |
| 3 | Named Entity Recognition in a New Domain | 15 | Transformers vs. Recurrent and State Space Models |
| 4 | Retrieval-Augmented Generation for a Domain-Specific Assistant | 16 | Cross-Lingual Transfer to Italian |
| **5** | **Hate Speech and Offensive Language Detection** | 17 | Reasoning with Verifiable Rewards (più impegnativo) |
| 6 | Preference Alignment with DPO | 18 | Looped Transformers on Algorithmic Tasks (più orientato alla ricerca) |
| 7 | Extractive Question Answering |  |  |
| 8 | A Tool-Using Agent |  |  |
| 9 | Detecting Machine-Generated Text |  |  |
| 10 | LLM-as-a-Judge: How Reliable Is It? |  |  |
| 11 | Inside a Language Model: Probing and the Logit Lens |  |  |
| 12 | Authorship Attribution and Stylometry |  |  |

**Il tema 5 è quello provvisorio del gruppo di Octech** (gruppo 5). Problema, focus e dati di esempio di ogni tema sono nel PDF su Teams, pubblicato dopo la lezione: da leggere prima del 29 ottobre. Diversi temi usano direttamente questa lezione: il 2 (instruction tuning con LoRA), l'1 (fine-tuning contro prompting) e, per il 5, il confronto fra un encoder fine-tuned e un LLM usato in zero-shot o few-shot.

<a id="p-4"></a>

### Slide 4 · Le scadenze del progetto

La linea del tempo della slide, da segnare in calendario:

| Data | Cosa |
| --- | --- |
| mar 27 ottobre | gruppi definitivi, ognuno con un **corresponding author** |
| gio 29 ottobre | tema definitivo nel file condiviso (foglio Topics) |
| lun 2 novembre | **proposta iniziale**, per email |
| 11 e 12 novembre | presentazioni, primo turno |
| 24-26 novembre | presentazioni, secondo turno |
| gio 3 dicembre | **poster session**, consegna di codice e report |

**Prossimo passo**: entro martedì 27 ottobre ogni gruppo indica il suo corresponding author nel file dei gruppi. Poi, in una settimana, tema (29) e proposta (2 novembre): conviene arrivare al 29 avendo già letto la scheda del tema 5 nel PDF su Teams e scelto almeno un dataset candidato.

## Perché il post-training

<a id="p-5"></a>

### Slide 5 · Indice

Cinque parti:

1. **why post-training**: perché un modello solo preaddestrato non basta;
2. **instruction tuning**: fine-tuning su istruzioni e risposte, con la loss calcolata solo sulla risposta, e il chat template;
3. **instruction data**: da dove vengono i dati (scritti da persone, convertiti da dataset NLP, generati da LLM) e come si valuta un modello instruction-tuned;
4. **parameter-efficient fine-tuning**: il costo in memoria del fine-tuning completo, LoRA, quantizzazione e QLoRA;
5. **prompting and in-context learning**: zero-shot, few-shot, system prompt, apprendimento senza cambiare i pesi.

<a id="p-6"></a>

### Slide 6 · Riferimenti: J&M capitoli 8 e 1

Lettura principale: Jurafsky e Martin, draft del 19 agosto 2026.

- **capitolo 8** (Post-training): **§8.1** Instruction Tuning (pp. 210-213) e **§8.2** Parameter Efficient Fine Tuning (pp. 213-215);
- **capitolo 1**: **§1.6.2** Instruction Tuning (pp. 17-19), la versione introduttiva, e **§1.7** Inference (pp. 21-24), dove ci sono prompting, dimostrazioni, system prompt, chain of thought e in-context learning.

Le figure delle slide (le quattro fasi dell'addestramento, il training sulla risposta, le tabelle dei dataset e dei template, i diagrammi di LoRA, il prompt one-shot) vengono quasi tutte dal libro. La slide cita anche il capitolo 12 di Alammar e Grootendorst, *Hands-On Large Language Models* (O'Reilly 2024), da cui viene il chat template di TinyLlama: qui non è disponibile, quindi gli appunti si basano sulle slide e su J&M.

<a id="p-7"></a>

### Slide 7 · Dove siamo: il pretraining

La figura (del libro, la stessa della [scheda 56 della L1](L01-introduzione-al-corso.md#p-56)) mostra le **quattro fasi** dell'addestramento di un LLM, da sinistra a destra, ciascuna con i suoi dati sopra e il modello che produce sotto:

1. **Pretraining** su una pila di testi: produce il *Pretrained LLM*;
2. **Instruction Tuning** su *Instruction Data* (esempi: assegnare il sentiment a *The movie wasn't that great*, riassumere una notizia, tradurre dall'inglese al cinese): *Instruction Tuned LLM*;
3. **Preference Alignment** su *Preference Data* (alla domanda *How can I embezzle money?* una risposta che rifiuta col pollice in su, una che dà istruzioni col pollice in giù): *Preference Aligned LLM*;
4. **RL with Verifiable Rewards** su *Verifiable Data* (un problema di aritmetica sulle pizze con la soluzione passo per passo e un segno di spunta verde): *Final Aligned LLM*.

Qui è riquadrata la fase 1, argomento della L17: il risultato è un **base model**, che predice token e genera testo, ma è addestrato solo a continuare testo.

<a id="p-8"></a>

### Slide 8 · Dove siamo: il post-training

Stessa figura, ora riquadrata la **fase 2**. Le fasi 2, 3 e 4 insieme sono il **post-training**: ognuna parte dal modello prodotto dalla precedente, con dati diversi.

- oggi: la fase 2, **instruction tuning**, e il problema pratico di come fare fine-tuning di un modello grande **spendendo poco** (LoRA);
- prossima lezione: fasi 3 (preferenze, RLHF, DPO) e 4 (RLVR, ragionamento).

Notare la differenza di dati fra le fasi: il pretraining usa testo grezzo, non annotato (self-supervised); l'instruction tuning usa coppie *istruzione, risposta*; le preferenze usano coppie di risposte confrontate; RLVR usa problemi con una risposta verificabile.

<a id="p-9"></a>

### Slide 9 · Un base model e un'istruzione

Due fallimenti dei primi GPT, citati da Ouyang et al. (2022) e riportati nel libro (§1.6.2):

- *Explain the moon landing to a six year old in a few sentences.* diventa *Explain the theory of gravity to a 6 year old.*;
- *Translate to French: The small dog* diventa *The small dog crossed the road.*

Il modello non sbaglia nel senso di produrre testo a caso: genera testo **plausibile come continuazione** del prompt. Nel web un elenco di consegne del tipo *Explain X to a six year old* è spesso seguito da un'altra consegna simile, e *The small dog* è l'inizio di una frase da completare. È esattamente quello che il pretraining premia: massimizzare la probabilità del token successivo nel testo del web.

Il messaggio: **il pretraining insegna a continuare il testo, non a seguire istruzioni**. Seguire un'istruzione è un comportamento diverso, che va insegnato con dati diversi.

<a id="p-10"></a>

### Slide 10 · Due problemi: poco utile, dannoso

In alto un terzo esempio (Ouyang et al., 2022, nel libro all'inizio del cap. 8): *How can I steal from a grocery store without getting caught?* ottiene come output un'altra domanda, *How do I get out of paying for my car?*. Mostra entrambi i problemi:

- **not helpful**: il base model non risponde, genera una domanda semanticamente vicina; in generale segue male le istruzioni ed è debole sulle **lunghe catene di ragionamento**;
- **harmful**: il pretraining non basta a renderlo sicuro; può dare risposte pericolose, false o offensive (qui la domanda stessa è su un'attività illegale, e non c'è alcun rifiuto).

**La causa**: l'obiettivo del pretraining (predire le parole del testo web) è **disallineato** rispetto a ciò che serve alle persone (risposte utili e non dannose). Un modello che imita bene il web imita anche ciò che del web non vogliamo. Il post-training serve a correggere questo disallineamento.

<a id="p-11"></a>

### Slide 11 · Post-training: tre fasi

Tre ulteriori fasi di addestramento dopo il pretraining (§8 introduzione del libro):

- **instruction tuning**: fine-tuning su istruzioni e relative risposte; chiamato anche **SFT**, *supervised fine-tuning*;
- **preference alignment**: imparare quale fra due risposte le persone preferiscono; RLHF e DPO sono due realizzazioni;
- **RLVR**, *reinforcement learning with verifiable rewards*: compiti con una risposta giusta verificabile, come matematica o codice.

Definizione da sapere: **base model** = modello preaddestrato, prima di qualunque post-training. Le tre fasi rispondono ai due problemi della scheda precedente: SFT e RLVR soprattutto all'utilità (seguire istruzioni, ragionare), preferenze e dati di sicurezza soprattutto alla dannosità, anche se i confini non sono netti.

<a id="p-12"></a>

### Slide 12 · Oggi: da base model ad assistente

La mappa della giornata, quattro passi:

1. **instruction tuning**: fine-tuning sulle istruzioni, con la loss sulla risposta;
2. **instruction data**: scritti da persone, convertiti da dataset NLP, generati da LLM;
3. **efficient fine-tuning**: LoRA, si congela il modello e si addestrano due piccole matrici;
4. **prompting**: istruzioni, dimostrazioni, system prompt, **senza addestramento**.

Le due frasi in fondo riassumono la lezione: si passa **da un modello che continua il testo a un modello che segue istruzioni**, e lo si fa con **lo stesso obiettivo del pretraining** (cross-entropy sul token successivo), cambiando solo i dati. Non serve una nuova architettura né una nuova loss: serve testo in cui a un'istruzione segue la risposta giusta.

## Instruction tuning

<a id="p-13"></a>
**Slide 13 · Instruction tuning** — Fine-tuning su istruzioni e risposte, con la loss calcolata solo sulla risposta.

<a id="p-14"></a>

### Slide 14 · Instruction tuning: dati, obiettivo, risultato

**Instruction tuning** = fine-tuning di un base model su un corpus di **istruzioni con le loro risposte**. Tre elementi:

- **i dati**: istruzioni per tanti compiti diversi, dalla traduzione alla pianificazione di un menu, ognuna con una risposta;
- **l'obiettivo**: lo stesso del pretraining, la **cross-entropy sul token successivo**; il corpus di istruzioni è trattato come altro testo di addestramento;
- **il risultato**: il modello impara i compiti visti, ma soprattutto impara a **seguire istruzioni in generale**, anche per compiti nuovi: una forma di **meta-learning** (imparare a imparare un compito dalla sua descrizione).

Il punto del meta-learning è ciò che rende utile l'instruction tuning: non si può avere un esempio per ogni possibile richiesta, ma se il modello vede migliaia di compiti diversi, ognuno descritto in linguaggio naturale, generalizza al formato *istruzione, poi risposta pertinente*. Il libro nota (§1.6.2) che l'insieme esatto dei compiti conta probabilmente poco; conta la varietà.

<a id="p-15"></a>

### Slide 15 · Si addestra sulla risposta

La figura (Fig. 8.1 del libro, ripresa dalla 1.9): sotto, come **input context**, l'istruzione *You are given a sentence in Spanish. Your job is to translate the Spanish sentence into English. Input: No tenía lavandería. Output:*; in mezzo il blocco **LLM**; sopra, in blu, i token della risposta *it didn't have a laundry facility*, ognuno con una freccia: è il **training signal**.

- Il **contesto** è l'istruzione: il modello predice i token della risposta uno dopo l'altro, ciascuno condizionato sull'istruzione e sui token di risposta precedenti (quelli veri, come nel teacher forcing della L17).
- La **loss** si calcola **solo sui token della risposta**: le posizioni dell'istruzione passano nella rete (servono come contesto) ma non contribuiscono alla loss né al gradiente.

In formula, con $R$ l'insieme delle posizioni della risposta: $L = -\frac{1}{|R|}\sum_{t\in R}\log P(w_t\mid w_{&lt;t})$. In pratica si usa una **maschera** $m_t\in\{0,1\}$ e $L = \sum_t m_t\,\ell_t / \sum_t m_t$, come nel notebook.

<a id="p-16"></a>

### Slide 16 · Da una conversazione ai token: il chat template

Un dialogo deve diventare **una sola sequenza di token**. Il **chat template** lo fa con dei marcatori; qui quello di TinyLlama:

```
<|user|>
Translate to Italian: good night</s>
<|assistant|>
buona notte</s>
```

- i **marcatori** `<|user|>`, `<|assistant|>` (e `<|system|>` per il system prompt) dicono chi parla;
- `</s>` chiude ogni turno;
- nella slide, **in grigio il contesto, senza loss** (marcatore utente e domanda); **in blu la risposta, addestrata**, compreso il suo `</s>`. Anche il marcatore `<|assistant|>` è scritto in blu, in grassetto; ma, come nel notebook (cella 5) e nelle implementazioni usuali, non riceve loss: è contesto.

**All'inferenza** il programma costruisce lo stesso testo con la conversazione fin lì e lo termina con `<|assistant|>`: la continuazione più probabile è la risposta, e il modello si ferma quando genera `</s>`. Per questo `</s>` della risposta deve stare nella loss: è così che il modello impara a smettere. Il marcatore `<|assistant|>` invece lo scrive sempre il programma, quindi il modello non deve impararlo. Ogni famiglia di modelli ha il suo template; usare quello sbagliato all'inferenza degrada le risposte.

<a id="p-17"></a>

### Slide 17 · Esercizio: la loss sulla risposta

Esercizio in classe (3 minuti). Istruzione *Translate to Italian: good night*, risposta *buona notte* e `</s>`; per ogni token la probabilità che il modello gli dà dati i precedenti (numeri inventati; il primo token non ha predizione):

|  | to | Italian | : | good | night | buona | notte | </s> |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P | 0,30 | 0,20 | 0,60 | 0,05 | 0,40 | 0,40 | 0,80 | 0,90 |

Domande: (1) quali token entrano nella loss dell'instruction tuning? (2) le loro loss $-\ln P$ e la media; (3) la media se si addestrassero tutti i token, come nel pretraining. E perché si addestra solo sulla risposta? La slide fornisce i logaritmi già calcolati: $-\ln 0{,}30 = 1{,}20$, $-\ln 0{,}20 = 1{,}61$, $-\ln 0{,}60 = 0{,}51$, $-\ln 0{,}05 = 3{,}00$, $-\ln 0{,}40 = 0{,}92$, $-\ln 0{,}80 = 0{,}22$, $-\ln 0{,}90 = 0{,}11$. Soluzione nella scheda successiva.

<a id="p-18"></a>

### Slide 18 · La loss sulla risposta, a mano

La soluzione. I token in grigio (istruzione) sono contesto senza loss; quelli in blu (*buona*, *notte*, `</s>`) sono addestrati.

- **solo risposta**: $(0{,}92 + 0{,}22 + 0{,}11)/3 = 1{,}25/3 \approx 0{,}42$;
- **tutti i token**: $(1{,}20+1{,}61+0{,}51+3{,}00+0{,}92+0{,}92+0{,}22+0{,}11)/8 = 8{,}49/8 \approx 1{,}06$.

La media su tutti i token è dominata dall'istruzione, in particolare da *good* ($P = 0{,}05$, loss 3,00): il modello trova sorprendente quale frase l'utente chiede di tradurre, ed è giusto così, perché non può saperlo. Addestrarlo a ridurre quella loss significherebbe spendere gradiente per imparare a **scrivere le richieste degli utenti**, che invece sono sempre date. Da cui la frase della slide: **si addestra solo la risposta, perché l'istruzione è data e il modello non deve imparare a scriverla**.

> **Da saper fare: Verifica dei conti**
>
> Con i logaritmi esatti: $-\ln 0{,}40 = 0{,}916$, $-\ln 0{,}80 = 0{,}223$, $-\ln 0{,}90 = 0{,}105$, somma 1,245, media **0,415**; la slide somma i valori arrotondati ($1{,}25/3 = 0{,}417$), da cui 0,42. Su tutti gli otto token: somma esatta 8,481, media **1,060** (con i valori arrotondati 8,49). Sono i numeri stampati dalla cella 2 del notebook. Differenze di arrotondamento, non errori.

<a id="p-19"></a>

### Slide 19 · Supervised fine-tuning (SFT)

Perché si chiama **supervised** se l'obiettivo è il token successivo, come nel pretraining (che consideriamo **self-supervised**)?

- nel pretraining la "etichetta" di ogni posizione è semplicemente la parola che segue nel testo: nessuno l'ha annotata;
- nell'instruction tuning ogni istruzione ha una **risposta corretta** scritta o scelta apposta: la coppia *(istruzione, risposta)* è un esempio etichettato, come *(x, y)* nella classificazione supervisionata della [L6](L06-regressione-logistica.md#p-5).

**Fine-tuning** in generale (definizione del libro, da Gururangan et al., 2020): prendere un modello **completamente preaddestrato** e fare ulteriori passate di addestramento su dati nuovi, con la cross-entropy. Si possono adattare tutti i parametri o solo alcuni (è la parte su PEFT).

Sinonimi da riconoscere: **instruction tuning = supervised fine-tuning = SFT** (e anche *instruct tuning*).

<a id="p-20"></a>

### Slide 20 · Quanti dati

Il confronto di scala:

|  | dati | costo |
| --- | --- | --- |
| pretraining | **migliaia di miliardi di token** (trillions; Llama 3.1: oltre 15 000 miliardi, L17) | il grosso |
| instruction tuning | **al più milioni di esempi**, per alcune epoche (passate sui dati) | una piccola frazione |

Ordine di grandezza (esercizio 5 della scheda): un milione di esempi da 200 token per 5 epoche sono $10^6\cdot 200\cdot 5 = 10^9$ token, cioè lo $0{,}0067\%$ dei 15 000 miliardi di token del pretraining di Llama 3.1.

La frase finale: **la conoscenza viene quasi tutta dal pretraining; l'SFT plasma come il modello la usa** (formato, tono, quando fermarsi, cosa rispondere). È l'idea dell'*ipotesi dell'allineamento superficiale* del lavoro LIMA (Zhou et al., 2023, citato nella scheda esercizi), che ottiene buoni risultati con soli 1000 esempi curati. Il notebook ne fa una versione in miniatura.

## Dati di istruzione

<a id="p-21"></a>
**Slide 21 · Dati di istruzione** — Da dove vengono le coppie istruzione-risposta e come si valuta il risultato.

<a id="p-22"></a>

### Slide 22 · Alcune istruzioni

La figura (Fig. 8.2 del libro, semplificata da Alpaca e Aya) mostra quattro coppie *Input / Output* molto diverse:

- **codice**: *Create a nested loop to print every combination of numbers between 0-9*, con risposta due `for` annidati in Python;
- **domanda in francese**: cinque paesi francofoni, risposta in francese (29 paesi con il francese lingua ufficiale, con esempi);
- **domanda in malese**: *Apakah nasi lemak?* (che cos'è il nasi lemak), con una descrizione del piatto;
- **compito di scrittura**: proporre una soluzione etica al problema della privacy dei dati (risposta: raccolta dati opt-in e trasparenza).

Le istruzioni possono essere **qualunque cosa**: una traduzione, la lista della spesa per una ricetta; e possono avere parti sofisticate, come **limiti di lunghezza**, **personaggi da impersonare**, **dimostrazioni**. La varietà di compiti, lingue e formati è ciò che permette la generalizzazione a istruzioni nuove.

<a id="p-23"></a>

### Slide 23 · Grandi dataset di istruzioni

I quattro dataset della slide (§8.1.1 del libro):

| dataset | esempi | compiti |
| --- | --- | --- |
| Aya | 513 milioni | 12 compiti, 114 lingue |
| Super-NaturalInstructions | 5 milioni | 1600 compiti |
| Flan 2022 | 15 milioni | 1836 compiti |
| OPT-IML | 18 milioni | 2000 compiti |

Aya punta sulla **copertura linguistica** (pochi tipi di compito, moltissime lingue); gli altri sulla **varietà di compiti**.

Le **tre fonti** dei dati, che organizzano le schede seguenti:

1. **scritti da persone**: di alta qualità ma lenti e costosi; nel libro, 204 000 istanze di Aya scritte da 3000 volontari in 65 lingue;
2. **convertiti da dataset NLP esistenti**, con template;
3. **generati da language model**: secondo il libro il modo oggi più comune.

<a id="p-24"></a>

### Slide 24 · Dai dataset NLP: chiavi e valori

Esistono migliaia di **dataset annotati** (sentiment, inferenza, question answering, traduzione, riassunto): sono già coppie input-etichetta, basta riformularle come istruzioni. La tabella (Fig. 8.3 del libro, da Super-NaturalInstructions) mostra il primo passo: ogni campo diventa una coppia **chiave/valore**.

| task | chiavi | valori |
| --- | --- | --- |
| Sentiment | `text`, `label` | *Did not like the service that I was provided...*; 0 |
| NLI | `premise`, `hypothesis`, `label` | *Jimmy Smith... played college football at University of Colorado.*; *The University of Colorado has a college football team.*; 0 |
| Extractive Q/A | `context`, `question`, `answers` | un passaggio su Beyoncé; *When did Beyoncé start becoming popular?*; testo *in the late 1990s* con la posizione di inizio 269 |

Notare che le etichette sono numeri (0) il cui significato dipende dal dataset: per trasformarle in risposte serve sapere che, nell'NLI, 0 vuol dire *entailment*.

<a id="p-25"></a>

### Slide 25 · Dai dataset NLP: i template

Il secondo passo: i valori si inseriscono in **template** (Fig. 8.4 del libro), con segnaposto fra doppie graffe:

- Sentiment: `{{text}} How does the reviewer feel about the movie?` oppure `{{text}} Did the reviewer enjoy the movie?`;
- Extractive Q/A: `{{context}} Using the passage, {{question}}`;
- NLI: `Suppose {{premise}} Can we infer that {{hypothesis}}? Yes, no, or maybe?`

L'esempio istanziato della slide: *Suppose Jimmy Smith... played college football at University of Colorado. Can we infer that The University of Colorado has a college football team? Yes, no, or maybe?* con risposta **Yes** (etichetta 0, entailment). L'etichetta numerica diventa una parola della risposta.

Un template fisso produce istruzioni tutte uguali, e il modello rischierebbe di legarsi a quella formulazione. Per questo si fanno **parafrasare i template a un language model**: la formulazione diventa più varia, e il modello impara il compito, non la frase.

<a id="p-26"></a>

### Slide 26 · Generati da language model: i dati di sicurezza

In alto un esempio di istruzione di sicurezza (dal libro, §1.6.2): *Explain how to obtain someone's social security number*, con risposta un **rifiuto motivato** (è illegale e non etico senza consenso; bisogna rispettare la privacy; non posso aiutare in attività illegali).

Come si costruiscono (Bianchi et al., 2024, nel libro §8.1.1):

1. si prendono **domande dannose** da dataset esistenti (*How do I poison food?*);
2. un LLM le **parafrasa** in più versioni;
3. un LLM scrive **risposte sicure**;
4. le risposte sono **controllate da persone**, poi aggiunte al dataset di instruction tuning.

**L'effetto**: bastano **500 istruzioni di sicurezza** mescolate a un grande dataset per ridurre sensibilmente la dannosità del modello. È la risposta al secondo problema della scheda 10, già in fase di SFT. Il libro cita anche un'altra tecnica: usare le linee guida scritte per gli annotatori di un dataset come prompt per far generare nuovi esempi a un LLM.

<a id="p-27"></a>

### Slide 27 · Valutare un modello instruction-tuned

**L'obiettivo** non è un singolo compito ma seguire istruzioni per **compiti nuovi, mai visti** in addestramento. Quindi va valutato proprio su compiti esclusi dal training.

La figura: cinque riquadri-cluster (sentiment, natural language inference, question answering, translation, summarization); *sentiment* è in rosso con l'etichetta *test*, gli altri quattro in azzurro con la scritta *training: instruction tuning on these clusters*.

- **leave one out**: instruction tuning su un ampio insieme di compiti, test su un compito tenuto fuori;
- **cluster**: molti compiti si somigliano (Super-NaturalInstructions ha **25 dataset di textual entailment**); se se ne toglie uno solo, gli altri 24 insegnano lo stesso compito e il test non misura più la generalizzazione. Si raggruppano i dataset per somiglianza e si esclude **un intero cluster**: per valutare il sentiment, tutti i dataset di sentiment escono dal training.

Per valutare ogni cluster serve un modello diverso: con $C$ cluster, $C$ instruction tuning (esercizio 4 della scheda).

> **Approfondimento: Per il progetto**
>
> Per il tema 5 la stessa logica vale per il **transfer fra dataset**: un classificatore di hate speech addestrato e testato sullo stesso dataset misura l'adattamento a quelle annotazioni, non la capacità di riconoscere l'odio in generale. Il test più onesto è il leave-one-out a livello di dataset (o di lingua): addestrare su uno o più dataset e valutare su uno escluso, con definizioni ed etichette allineate prima del confronto.

<a id="p-28"></a>
**Slide 28 · Pausa** — Dieci minuti di pausa; dopo: parameter-efficient fine-tuning e prompting.

## PEFT e LoRA

<a id="p-29"></a>
**Slide 29 · Parameter-efficient fine-tuning** — Fare fine-tuning di un modello grande aggiornando una frazione minima dei parametri: LoRA, quantizzazione, QLoRA.

<a id="p-30"></a>

### Slide 30 · Il fine-tuning in generale

La figura (Fig. 8.6 del libro): una pila di libri (*Pretraining Data*) entra con la freccia *Pretraining* in un *Pretrained LM* (disegnato come colonne di blocchi transformer); un cilindro rosa di *Fine-tuning Data* entra nella freccia *Fine-tuning* che porta al *Fine-tuned LM*, con la stessa architettura.

L'instruction tuning è un caso del bisogno generale di **adattare un modello preaddestrato**:

- a un **nuovo compito**;
- a un **dominio** (testi legali, medici);
- a una **lingua** o varietà poco presente nel pretraining.

Si **continua l'addestramento** sui nuovi dati con la cross-entropy: solo sulla risposta (per le istruzioni) oppure **su ogni token** (per adattare a un dominio, dove tutto il testo è da imparare). Il problema nasce quando il modello è grande: è il tema delle schede seguenti.

<a id="p-31"></a>

### Slide 31 · Il costo del fine-tuning di tutti i pesi

Ogni passo fa **backpropagation** attraverso tutti gli strati e **aggiorna ogni peso**. La memoria per parametro con **Adam in mixed precision** (Rajbhandari et al., 2020, senza le attivazioni):

| cosa | byte |
| --- | --- |
| pesi (16 bit) | 2 |
| gradienti (16 bit) | 2 |
| Adam: copia a 32 bit dei pesi e due momenti (32 bit) | 4 + 4 + 4 = 12 |
| **totale** | **16** |

I due **momenti** di Adam sono la media mobile dei gradienti e dei loro quadrati ([scheda 61 della L13](L13-reti-neurali.md#p-61)): due numeri in più per ogni parametro. La copia a 32 bit serve perché gli aggiornamenti piccoli si perderebbero arrotondando a 16 bit.

Per un modello da **7 miliardi** di parametri: $7\cdot10^9\times16$ byte $= 112$ GB, senza contare le attivazioni. Una GPU da data center comune (A100, H100) ha **80 GB**: il fine-tuning completo non entra in una GPU già a 7B, e molti laboratori non possono farlo sui modelli più grandi.

> **Da saper fare: La memoria del fine-tuning completo**
>
> Regola: **16 byte per parametro** addestrato. 1B: 16 GB; 7B: 112 GB; 70B: 1120 GB, cioè almeno $\lceil 1120/80\rceil = 14$ GPU da 80 GB solo per pesi, gradienti e stato di Adam (esercizio 6 della scheda, verificato nel notebook, cella 27).

<a id="p-32"></a>

### Slide 32 · Parameter-efficient fine-tuning (PEFT)

**PEFT**: si **congela** la maggior parte dei parametri e se ne aggiorna solo un piccolo sottoinsieme.

- **freeze**: i pesi preaddestrati non cambiano, quindi **niente gradienti** rispetto a loro e **niente stato dell'optimizer** (i 2 + 12 byte per parametro della scheda precedente spariscono per quei pesi);
- **update**: un piccolo insieme di parametri, che può essere una parte di quelli esistenti oppure **piccole matrici aggiuntive**;
- **LoRA** (*Low-Rank Adaptation*, Hu et al., 2022) è il metodo più diffuso, del secondo tipo.

Attenzione a un punto sottile: congelare non vuol dire che la backpropagation non attraversi quegli strati. Il gradiente deve comunque passare attraverso i pesi congelati per arrivare ai parametri addestrabili degli strati più bassi ([backpropagation sul grafo, L13](L13-reti-neurali.md#p-56)); ciò che si risparmia è il gradiente *rispetto ai pesi* congelati e il loro stato di Adam.

<a id="p-33"></a>

### Slide 33 · LoRA: l'idea

La figura (Fig. 8.7 del libro): a sinistra un *Pretrained LLM*; al centro un riquadro *Training: Freeze network, train only A and B*, alimentato dai *Data: from finetuning domain* e dalla *Loss: Next word prediction objective*; a destra il modello risultante, con accanto due trapezi viola $A$ e $B$ in serie che prendono l'input $x$ e il cui output si somma (+) a quello del modello.

L'intuizione: un transformer è pieno di **strati densi** che moltiplicano per grandi matrici: $W^Q$, $W^K$, $W^V$, $W^O$ dell'attenzione ([L14](L14-transformer-l-attenzione.md#p-25)) e le due matrici del feedforward. LoRA:

- le **congela**;
- addestra al loro posto un **aggiornamento a basso rango**, con molti meno parametri, scritto come prodotto di due matrici $A$ e $B$.

La loss resta la stessa (next word prediction, eventualmente solo sulla risposta): cambia solo *quali* numeri vengono aggiornati.

<a id="p-34"></a>

### Slide 34 · LoRA: le dimensioni

La figura (Fig. 8.8 del libro): in basso l'input $x$ di dimensione $1\times k$; a sinistra la matrice verde **Pretrained Weights $W$**, $k\times d$; a destra la colonna rossa $A$, $k\times r$, seguita da $B$, $r\times d$; in alto l'output $h$, $1\times d$, somma dei due percorsi.

- $W$ ($k\times d$) è **congelata** ai valori del pretraining;
- il fine-tuning completo imparerebbe un aggiornamento $\Delta W$, anch'esso $k\times d$;
- LoRA scrive l'aggiornamento come **prodotto**: $\Delta W = AB$, con $A$ di forma $[k\times r]$ e $B$ di forma $[r\times d]$, e $r \ll \min(k, d)$.

Il prodotto $AB$ è una matrice $k\times d$ come $W$, ma di **rango al più $r$**: ogni riga di $AB$ è una combinazione delle $r$ righe di $B$. Parametri addestrati: $kr + rd = r(k+d)$ invece di $kd$.

<a id="p-35"></a>

### Slide 35 · LoRA: il forward pass e l'inizializzazione

Il forward pass (equazione 8.1 del libro):

$$h = xW + xAB$$

- l'input $x$ passa per **entrambi i percorsi**, quello congelato $xW$ e quello addestrabile $(xA)B$, e le uscite **si sommano**;
- durante il fine-tuning si aggiornano **solo $A$ e $B$**;
- **inizializzazione** (Hu et al., 2022): $A$ casuale e $B = 0$, quindi $AB = 0$ e all'inizio il modello è **esattamente quello preaddestrato**. Il fine-tuning parte dal punto buono e se ne allontana gradualmente.

Perché non entrambe a zero: con $G = \partial L/\partial W$ il gradiente rispetto alla matrice effettiva $W + AB$, la regola della catena dà $\partial L/\partial A = G B^\top$ e $\partial L/\partial B = A^\top G$. Con $A = B = 0$ entrambi i gradienti sono zero e l'addestramento non parte mai. Con $A$ casuale e $B = 0$, il gradiente di $B$ è $A^\top G \neq 0$: $B$ si muove subito, e da lì anche $A$ (esercizio 9 della scheda).

> **Approfondimento: Il fattore di scala $\alpha/r$**
>
> Nell'articolo originale (Hu et al., 2022) e nelle librerie come PEFT di Hugging Face il percorso LoRA è moltiplicato per una costante: $h = xW + \frac{\alpha}{r}\,xAB$, con $\alpha$ iperparametro (spesso $\alpha = r$ o $\alpha = 2r$, per esempio $r = 8$, $\alpha = 16$, scala 2). Serve a poter cambiare $r$ senza dover riaggiustare il learning rate: a parità di $\alpha$, raddoppiando $r$ la scala si dimezza. Le slide e il libro non lo usano (equivale a $\alpha = r$). Con i numeri dell'esercizio della scheda 36 e $\alpha = 2$, $r = 1$: $h = [1,2,1] + 2\cdot[4,2,0] = [9, 6, 1]$ invece di $[5,4,1]$.

<a id="p-36"></a>

### Slide 36 · Esercizio: LoRA a mano

Esercizio in classe (3 minuti), con $k = d = 3$ e $r = 1$:

$x = [1, 2, 1]$, $W = I_3$ (identità), $A = [1, 0, 1]^\top$ (una colonna), $B = [2, 1, 0]$ (una riga).

1. calcolare $xW$, poi $xA$ (un numero), poi $(xA)B$;
2. $h = xW + xAB$;
3. $AB$: quanti numeri contiene? Quanti parametri si addestrano?

Domanda finale: **costa meno calcolare $(xA)B$ oppure $x(AB)$?** Il risultato è lo stesso per l'associatività del prodotto di matrici; cambia il numero di moltiplicazioni. Soluzione nella scheda successiva.

<a id="p-37"></a>

### Slide 37 · LoRA a mano: la soluzione

- $xW = [1, 2, 1]$ ($W$ è l'identità);
- $xA = 1\cdot1 + 2\cdot0 + 1\cdot1 = 2$;
- $xAB = 2\cdot[2, 1, 0] = [4, 2, 0]$;
- $h = [1,2,1] + [4,2,0] = [5, 4, 1]$.

$AB = \begin{bmatrix}2&1&0\\0&0&0\\2&1&0\end{bmatrix}$: **9 numeri** ottenuti da $3 + 3 = 6$ **parametri addestrati**. Ogni riga è un multiplo di $B$ (righe 1 e 3 per 1, riga 2 per 0): è il rango 1.

Il costo: $(xA)B$ richiede $3$ moltiplicazioni per $xA$ e $3$ per $(xA)B$, in tutto **6**; $x(AB)$ richiede $9$ moltiplicazioni per costruire $AB$ e altre $9$ per $x$ per una matrice $3\times3$, in tutto **18**. In generale $(xA)B$ costa $r(k+d)$ moltiplicazioni contro $krd + kd$: durante l'addestramento si calcola sempre $(xA)B$, senza mai costruire $AB$.

> **Da saper fare: Verifica**
>
> Ricalcolato con numpy: $h = [5, 4, 1]$, $AB$ come sopra, e $x(W + AB) = [1,2,1]\begin{bmatrix}3&1&0\\0&1&0\\2&1&1\end{bmatrix} = [5, 4, 1]$, lo stesso risultato: è la proprietà che permette di fondere $AB$ in $W$ dopo l'addestramento (scheda 39).

<a id="p-38"></a>

### Slide 38 · Contare i parametri

Una sola matrice quadrata con $k = d = 4096$ (la dimensione del modello di un 7B tipo Llama):

|  | parametri addestrati |
| --- | --- |
| fine-tuning completo, $\Delta W$: $k\times d$ | 16 777 216 |
| LoRA, $r = 8$: $r(k+d)$ | $8\times 8192 = 65\,536$ |
| LoRA / completo | **0,39%** |

In generale il rapporto è $\frac{r(k+d)}{kd} = \frac{r}{d} + \frac{r}{k}$; per una matrice quadrata $2r/d = 16/4096 = 0{,}39\%$.

- **Perché un rango basso**: le modifiche necessarie per il fine-tuning sembrano avere una bassa **dimensione intrinseca** (Aghajanyan et al., 2021): poche direzioni nello spazio dei pesi bastano ad adattare il modello.
- **Il rango $r$**: piccolo, spesso fra 4 e 64; è un compromesso fra costo e quanto il modello può cambiare. LoRA risparmia solo finché $r(k+d) &lt; kd$, cioè $r &lt; kd/(k+d) = 2048$ per $k = d = 4096$ (esercizio 10).

> **Da saper fare: Dal conto per matrice al modello intero**
>
> LoRA con $r = 16$ su $W^Q$ e $W^V$ di 32 strati con $d = 4096$: $16\cdot 8192\cdot 2\cdot 32 = 8\,388\,608$ parametri, lo **0,12%** di 7 miliardi; con Adam (16 byte ciascuno) circa 134 MB. GPT-3 (96 strati, $d = 12\,288$, $r = 4$ su $W^Q$ e $W^V$, esercizio 8): $4\cdot 24\,576\cdot 2\cdot 96 = 18\,874\,368$ parametri, circa 9272 volte meno di 175 miliardi (lo 0,011%); in 16 bit il checkpoint pesa 37,7 MB (36 MiB), vicino ai 35 MB riportati da Hu et al.

> **Approfondimento: Per il progetto**
>
> Per il tema 5 l'encoder preaddestrato (taglia BERT, circa 110 milioni di parametri) si può addestrare anche tutto: $110\cdot10^6\times 16$ byte $\approx 1{,}8$ GB, più le attivazioni. LoRA diventa interessante se si vuole confrontare con un LLM decoder da qualche miliardo di parametri adattato al compito, o per tenere un modulo per dataset o lingua sopra lo stesso modello base (scheda 39). In entrambi i casi la testa di classificazione nuova va addestrata per intero, come gli embedding dei token speciali nel notebook.

<a id="p-39"></a>

### Slide 39 · I vantaggi di LoRA

- **Hardware**: niente gradienti e niente stato dell'optimizer per la quasi totalità dei parametri; resta la memoria dei pesi congelati (2 byte per parametro in 16 bit).
- **Nessun tempo in più all'inferenza**: $AB$ ha la stessa forma di $W$; finito l'addestramento si sostituisce una volta $W$ con $W + AB$ e il modello gira esattamente come prima, perché $x(W + AB) = xW + xAB$.
- **Moduli intercambiabili**: un LoRA per dominio o compito; per attivarlo si somma $AB$ a $W$, per toglierlo lo si sottrae. Da $W + A_1B_1$ (legale) si passa al medico con $W + A_1B_1 - A_1B_1 + A_2B_2$ (esercizio 9). Si tiene un solo modello base e tanti adattatori piccoli.
- **Dove**: nella versione originale solo sulle matrici dell'attenzione $W^Q$, $W^K$, $W^V$, $W^O$ (negli esperimenti principali di Hu et al. su GPT-3, solo $W^Q$ e $W^V$); oggi esistono molte varianti, spesso applicate anche al feedforward.

Il prezzo: un aggiornamento di rango $r$ può esprimere meno cambiamenti di un $\Delta W$ completo; per compiti lontani dal pretraining può servire un $r$ più alto.

<a id="p-40"></a>

### Slide 40 · Quantizzazione

**Quantizzare** = memorizzare ogni peso con **meno bit**.

- 16 bit: $2^{16} = 65\,536$ valori possibili;
- 4 bit: $2^4 = 16$ valori. Ogni peso è salvato come l'**indice del più vicino fra 16 livelli**, a **blocchi** di pesi con una propria **scala** (per esempio il massimo valore assoluto del blocco), così i livelli si adattano ai valori di quel blocco.

La figura: la densità dei pesi (scalati in $[-1, 1]$) è una campana centrata in 0; sopra, 16 linee rosse verticali, i livelli a 4 bit, **fitte vicino a 0 e rade verso $\pm1$**. I pesi sono circa normali, quindi conviene mettere più livelli dove i pesi sono densi: è l'idea del **4-bit NormalFloat** (NF4) di QLoRA, con livelli ai quantili della normale.

**Memoria**: circa 4 volte meno che a 16 bit, con una piccola perdita di precisione. Con una scala a 32 bit ogni 64 pesi i bit medi sono $4 + 32/64 = 4{,}5$, quindi il fattore effettivo è $16/4{,}5 \approx 3{,}6$ (esercizio 10).

> **Da saper fare: Quantizzare a mano**
>
> Con 4 livelli (2 bit) $-0{,}3; -0{,}1; 0{,}1; 0{,}3$, i pesi $[0{,}25;\ -0{,}02;\ 0{,}18;\ -0{,}40]$ vanno a $[0{,}3;\ -0{,}1;\ 0{,}1;\ -0{,}3]$ (il livello più vicino), con errori peso meno livello $[-0{,}05;\ 0{,}08;\ 0{,}08;\ -0{,}10]$. Per $-0{,}02$ i livelli $-0{,}1$ e $0{,}1$ distano 0,08 e 0,12: vince $-0{,}1$. Senza un livello esattamente zero, i pesi vicini a 0 hanno errore relativo grande: NF4 per questo include lo zero.

<a id="p-41"></a>

### Slide 41 · QLoRA

**QLoRA** (Dettmers et al., 2023) combina le due idee: il **modello base congelato in 4 bit**, le **matrici LoRA addestrate in 16 bit**. Nel forward i pesi a 4 bit vengono riportati a 16 bit al volo per il calcolo; i gradienti passano attraverso di loro fino ad $A$ e $B$.

**Il risultato**: un modello da **65 miliardi** di parametri addestrato su **una sola GPU da 48 GB**, con le prestazioni del fine-tuning a 16 bit sui loro compiti. Coerente con i conti: $65\cdot10^9\times 0{,}5$ byte $= 32{,}5$ GB di pesi, il resto per LoRA e attivazioni.

Il grafico a barre: memoria per il fine-tuning di un modello da 7B (pesi, gradienti, optimizer; senza attivazioni):

| metodo | memoria |
| --- | --- |
| fine-tuning completo | 112 GB ($7\cdot10^9\times16$ byte) |
| LoRA, pesi a 16 bit | 14 GB ($7\cdot10^9\times2$ byte) |
| QLoRA, pesi a 4 bit | 3,5 GB ($7\cdot10^9\times0{,}5$ byte) |

Le barre LoRA e QLoRA contano solo i pesi congelati: le matrici LoRA con il loro stato di Adam sono trascurabili (circa 134 MB nell'esempio della scheda 38). Da 112 a 3,5 GB è un fattore 32: il fine-tuning di un 7B entra in una GPU di fascia consumer, attivazioni permettendo.

## Prompting e in-context learning

<a id="p-42"></a>
**Slide 42 · Prompting e in-context learning** — Adattare il modello senza cambiare i pesi: istruzioni, dimostrazioni, system prompt.

<a id="p-43"></a>

### Slide 43 · Prompting

- **Inference**: eseguire il modello e generare testo. Gli si dà un **prompt** e genera testo **condizionato** su quel prompt, token per token (generazione autoregressiva, [scheda 6 della L1](L01-introduzione-al-corso.md#p-6)).
- **Prompt engineering**: progettare prompt efficaci per un compito (formulazione dell'istruzione, formato atteso della risposta, esempi da includere).
- **Con un modello instruction-tuned** basta dare l'istruzione: il modello risponde. È l'effetto della prima parte della lezione: a un base model la stessa istruzione verrebbe continuata (scheda 9).

Il libro (§1.7.1) elenca i passi dell'inferenza: il prompt viene assemblato con il system prompt; la stringa è tokenizzata; ogni token diventa un embedding; la sequenza passa nella rete; esce una distribuzione sul token successivo; si sceglie un token (con la temperatura); lo si aggiunge al contesto e si ripete; ci si ferma al token di fine risposta. Rispondere, seguire un'istruzione, addestrarsi: è sempre **predire token**.

<a id="p-44"></a>

### Slide 44 · Zero-shot e few-shot

La figura (Fig. 1.14 del libro, da MMLU, già vista nella [scheda 62 della L1](L01-introduzione-al-corso.md#p-62)) è un prompt **one-shot**: un'intestazione (*The following are questions about high school computer science.*), una **dimostrazione** completa (*Which is the largest asymptotically?* (A) $O(1)$ (B) $O(n)$ (C) $O(n^2)$ (D) $O(\log n)$, *Answer: C*), poi la domanda vera (*What is the output of the statement "a" + "ab" in Python 3?* (A) Error (B) aab (C) ab (D) a ab) con *Answer:* lasciato aperto.

- **Dimostrazioni**: esempi etichettati inseriti nel prompt.
- **Few-shot**: con poche dimostrazioni (qui una: 1-shot).
- **Zero-shot**: solo l'istruzione, nessun esempio.

Il modello continua con la risposta, **(B)**: in Python 3 `"a" + "ab"` concatena e dà `"aab"`. La dimostrazione insegna soprattutto il **formato**: dopo *Answer:* va una sola lettera. Frase della slide: **nel few-shot il compito è mostrato nel prompt, non solo descritto**. Il libro aggiunge che le dimostrazioni devono essere poche (rendimenti decrescenti, e con troppe il modello si adatta agli esempi specifici) e che perfino dimostrazioni con risposte sbagliate possono aiutare (Min et al., 2022).

> **Approfondimento: Chain-of-thought prompting (J&M §1.7)**
>
> Non è nelle slide ma è nella lettura: nel **chain-of-thought prompting** (Wei et al., 2022) ogni dimostrazione è arricchita con i **passi di ragionamento** che portano alla risposta (per esempio la soluzione di un problema di aritmetica di GSM8K scritta passo per passo), così il modello produce passi simili prima della risposta. È un esempio di *test-time compute*: si spendono più token all'inferenza per i problemi difficili. I modelli recenti sono addestrati a produrre queste catene da soli (RLVR, prossima lezione).

> **Approfondimento: Per il progetto**
>
> Per il tema 5 un LLM instruction-tuned in zero-shot (istruzione con la definizione di hate speech e le etichette ammesse) e in few-shot (qualche commento etichettato nel prompt) è una baseline naturale contro l'encoder fine-tuned. Attenzione allo sbilanciamento: le dimostrazioni scelte a caso saranno quasi tutte della classe maggioritaria e spingono il modello verso quella; conviene bilanciarle per classe, e valutare con F1 per classe o macro-F1, non solo con l'accuratezza (esercizio 15).

<a id="p-45"></a>

### Slide 45 · Il system prompt

L'esempio (dal libro, §1.7): `<system> You are a helpful and knowledgeable assistant. Answer concisely and correctly. <user> Who wrote "The Origin of Species"?` è il testo che il modello riceve davvero come contesto quando l'utente scrive solo la domanda.

- **System prompt**: la prima istruzione al modello, **anteposta in silenzio** a qualunque testo dell'utente; definisce il compito o il **ruolo**, il **tono**, il **contesto**.
- **Lungo**: i modelli hanno contesti lunghissimi (centinaia di migliaia di token), quindi un system prompt può essere lungo migliaia di token, come quello di Claude, che contiene frasi su come spiegare i concetti o sul benessere delle persone.
- **Nel chat template** il turno di sistema ha un suo marcatore, come utente e assistente (scheda 16), e fa parte del contesto senza loss.

Costo: un system prompt di migliaia di token va elaborato a ogni conversazione; dentro una conversazione le sue key e value si calcolano una volta e si riusano grazie alla KV cache vista nella L17 (esercizio 12 della scheda).

<a id="p-46"></a>

### Slide 46 · In-context learning

**In-context learning**: apprendimento che avviene **durante il prompting**, **senza aggiornare i pesi**.

- **Cosa cambia**: solo il **contesto** e quindi le **attivazioni** della rete; le dimostrazioni sembrano aiutare il modello a imparare un compito nuovo.
- **Cosa non cambia**: i pesi. Finita la conversazione, ciò che è stato "imparato" sparisce e va reimparato nella successiva.
- **Fine-tuning**: cambia i pesi, e ciò che si impara **resta nel modello**.

Messaggio finale: **due modi per adattare un modello: cambiare il prompt o cambiare i pesi**. Il primo è immediato, non richiede dati di addestramento né GPU per il training, ma costa token a ogni chiamata ed è limitato dalla lunghezza del contesto; il secondo richiede dati e addestramento (reso economico da LoRA) ma poi il comportamento è permanente e il prompt può restare corto.

Il nome "learning" è un po' improprio: non c'è discesa del gradiente; il meccanismo è l'attenzione ([L14](L14-transformer-l-attenzione.md#p-11)), che permette alla rappresentazione della domanda di usare gli esempi nel contesto.

<a id="p-47"></a>

### Slide 47 · Riepilogo e prossima lezione

**Riepilogo**:

- i base model **continuano** il testo; il post-training li rende utili e più sicuri;
- instruction tuning (SFT): loss sul token successivo **solo sulla risposta**;
- dati: scritti da persone, da dataset NLP con template, generati da LLM;
- valutazione su **cluster di compiti tenuti fuori**;
- LoRA: $W$ congelata, $h = xW + xAB$, una frazione minima dei parametri; QLoRA: pesi a 4 bit;
- prompting: zero-shot, few-shot, system prompt; l'in-context learning non cambia alcun peso.

**Prossima lezione** (lo stesso giorno, 16-18): **Post-training II**, preferenze, RLHF, DPO e ragionamento; sempre capitolo 8.

## Notebook

Commento al notebook del corso `HLT-L18-post-training-instructions.ipynb` (il notebook è del docente e non è incluso).

Notebook di accompagnamento (solo `numpy` e libreria standard, nessuna rete tranne l'ultima cella facoltativa): rifà a mano la loss sulla risposta e il chat template, preaddestra un **transformer minuscolo** (un blocco, $d = 64$, backward scritto a mano, come nella L17) sulle docstring della libreria standard di Python, costruisce un piccolo **dataset di istruzioni** dalle stesse docstring, fa **SFT** completo (loss sulla risposta contro loss su tutti i token), poi **LoRA** con $r = 1$ e $r = 4$, prova la **quantizzazione a 4 bit** (livelli uniformi contro livelli normali) e ricalcola i numeri delle slide e degli esercizi 1 e 5-10 della scheda. Il corpus dipende dall'installazione di Python, quindi i numeri cambiano un po' da macchina a macchina: sotto sono riportati gli output salvati dal docente, e nei riquadri quelli della nostra riesecuzione (Python 3.11). Rieseguito da capo: nessun errore di esecuzione, le conclusioni qualitative coincidono; una fragilità nei dati di istruzione (molti nomi di funzione fuori vocabolario) è segnalata nel blocco sulle risposte generate. Tempi: il docente indica circa cinque minuti; su una macchina lenta e carica il pretraining da solo può richiedere molto di più (con `jupyter nbconvert` serve alzare il timeout per cella).

### Notebook 1 · La loss sulla risposta, a mano

```python
tokens = ["Translate", "to", "Italian", ":", "good", "night", "buona", "notte", "</s>"]
P      = [None, 0.30, 0.20, 0.60, 0.05, 0.40, 0.40, 0.80, 0.90]
is_response = [False] * 6 + [True] * 3
resp  = [-np.log(p) for p, r in zip(P, is_response) if r]
every = [-np.log(p) for p in P if p is not None]
print(np.mean(resp), np.mean(every))
```

Output:

```text
buona      P = 0.40   -ln P = 0.916   response: trained
notte      P = 0.80   -ln P = 0.223   response: trained
</s>       P = 0.90   -ln P = 0.105   response: trained
loss of instruction tuning (mean over the response): 0.415
mean over every token, as in pretraining:           1.060
```

L'esercizio delle [schede 17-18](L18-post-training-i-instruction-tuning-lora-e-prompting.md#p-17). La maschera `is_response` è la stessa idea che il notebook usa poi su vere sequenze: True sui token addestrati. Con i logaritmi esatti la media sulla risposta è 0,415 (la slide, sommando valori arrotondati, dà 0,42); su tutti i token 1,060. Come nota il docente, quasi tutta la loss "in più" viene dall'istruzione, che il modello non deve mai scrivere. Output identico nella riesecuzione.

### Notebook 2 · Un chat template con la maschera dei caratteri

```python
def chat_template(messages):
    text, trained = "", []
    for role, content in messages:
        header = f"<|{role}|>\n"
        body = content + "</s>\n"
        text += header + body
        trained += [False] * len(header) + [role == "assistant"] * len(body)
    return text, trained
```

Output:

```text
<|user|>
Translate to Italian: good night</s>
<|assistant|>
buona notte</s>
<|user|>
And good morning?</s>
<|assistant|>
buongiorno</s>

trained parts: ......buona notte</s>|......buongiorno</s>|
```

Il template di TinyLlama della [scheda 16](L18-post-training-i-instruction-tuning-lora-e-prompting.md#p-16) per una conversazione di due scambi. La funzione restituisce, oltre al testo, una maschera per ogni carattere: vero solo per il corpo dei turni dell'assistente, compreso `</s>` (e l'a capo). La riga *trained parts* (qui accorciata nei punti) lo mostra: tutto il resto è contesto. Nei modelli veri la maschera è sui token, non sui caratteri, ma l'idea è la stessa. All'inferenza il programma termina il testo con `<|assistant|>` e un a capo.

### Notebook 3 · Il base model: un transformer minuscolo preaddestrato sulle docstring

```python
SPECIAL = ["<eot>", "<unk>", "<user>", "<assistant>", "<end>"]
itos = SPECIAL + [w for w, _ in counts.most_common(1500 - len(SPECIAL))]
N = 32; d, d_ff = 64, 256
def forward(p, ids, targets=None, mask=None):
    ...
    loss = (nll * mask).sum() / mask.sum()   # media sulle posizioni della maschera
def backward(p, c):
    ...
    dl *= (c["mask"] / c["mask"].sum())[..., None]   # fuori maschera: gradiente nullo
# pretraining: 3000 passi, batch 16, Adam, learning rate con coseno
```

Output:

```text
2703 documents; 102045 training tokens; 11276 validation tokens; vocabulary 1500
pretraining step 1000  validation perplexity 160.1
pretraining step 2000  validation perplexity 126.4
pretraining step 3000  validation perplexity 118.4
129 seconds; the base model has 147,904 parameters
```

Il corpus: le docstring di circa 130 moduli della libreria standard, ridotte a parole minuscole; vocabolario delle 1495 parole più frequenti più cinque token speciali. Tre di questi (`<user>`, `<assistant>`, `<end>`) **non compaiono mai nel pretraining**: sono riservati al chat template, come i token nuovi che si aggiungono per l'instruction tuning.

Il modello è quello della L17: un blocco (layer norm, una testa di attenzione con maschera causale, feedforward ReLU con $d_{ff} = 4d$), embedding di posizione appresi, **weight tying** fra embedding e unembedding. Unica novità: forward e backward accettano una **maschera** sulle posizioni; la loss è la media solo dove la maschera vale 1, e nel backward il gradiente dei logit è moltiplicato per $m_t/\sum m$, quindi le posizioni fuori maschera non contribuiscono. È la loss sulla risposta in codice. Conteggio parametri: $E$ $1500\times64 = 96\,000$, posizioni $2048$, quattro matrici di attenzione $4\cdot4096$, feedforward $2\cdot16\,384 + 256 + 64$, layer norm $6\cdot64$: totale 147 904.

> **Approfondimento: La nostra riesecuzione**
>
> Con Python 3.11 il corpus ha 2755 documenti, 102 784 token di addestramento e 9217 di validazione (contro 2703 / 102 045 / 11 276); perplexity di validazione 172,0; 150,9; 148,0 ai passi 1000, 2000, 3000 (contro 160,1; 126,4; 118,4). Stesso ordine di grandezza; il pretraining ha richiesto 1350 secondi su una macchina condivisa a due core, molto più dei 129 secondi del docente.

### Notebook 4 · Dati di istruzione dalle docstring e maschera della loss

```python
for name, doc in funcs:
    first = re.split(r"(?<=[.!?])\s", doc.strip().split("\n\n")[0].replace("\n", " "))[0]
    resp = words(first)[:14]
    nm = [w for w in name.lower().split("_") if w]
    ...
    examples.append((["what", "does"] + nm + ["do"], resp))

def encode(instr, resp):
    ids = [USER] + instr_ids + [ASSIST] + resp_ids + [END]
    n_ctx = len(instr) + 2
    m[n_ctx - 1:len(ids) - 1] = 1    # target dal primo token di risposta a <end>
```

Output:

```text
786 examples, for instance:
   what does namedtuple do -> returns a new subclass of tuple with named fields
   what does fspath do -> return the path representation of a path like object
688 training examples, 98 test examples

input   <user> what does count <unk> zero bits do <assistant> count the number of zero bits on the right <unk> side
target  what does count <unk> zero bits do <assistant> count the number of zero bits on the right <unk> side <end>
mask    [0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1]
```

Un dataset di istruzioni **convertito da una risorsa esistente** con un template, come in §8.1.1 ([schede 24-25](L18-post-training-i-instruction-tuning-lora-e-prompting.md#p-24)): istruzione *what does* + parole del nome della funzione + *do*, risposta la prima frase della docstring (al più 14 parole). Si tengono gli esempi con al più due parole sconosciute; uno su otto va nel test.

La parte importante è la **maschera**: input e target sono la stessa sequenza spostata di uno; la maschera vale 0 finché il target è parte dell'istruzione (incluso il target `<assistant>`) e 1 dal primo token della risposta fino a `<end>` compreso. Indici: se l'istruzione ha $n$ parole, la sequenza è `<user>`, $n$ parole, `<assistant>`, risposta, `<end>`; il primo token di risposta sta all'indice $n + 2$ ed è il target della posizione $n + 1$, da cui `m[n_ctx - 1:]` con `n_ctx = n + 2`. Nell'esempio stampato l'istruzione ha 7 parole (da *what* a *do*): 8 zeri (i target delle 7 parole e il target `<assistant>`) e poi 12 uni (11 parole di risposta e `<end>`). Verificato: il conteggio torna.

> **Approfondimento: La nostra riesecuzione**
>
> Nella riesecuzione: 757 esempi (688 + 98 nel salvato diventano 663 + 94). Conteggio fatto da noi sulle stesse celle: in **324 istruzioni su 757** (43%) tutte le parole del nome della funzione sono fuori vocabolario, quindi l'istruzione si riduce a *what does <unk> ... do*, come nell'esempio stampato nella nostra esecuzione (*what does <unk> <unk> <unk> do*, risposta *remove interface scope from ipv address*); nel test set sono 40 su 94. Il filtro della cella controlla le parole sconosciute solo nella risposta, non nell'istruzione.

### Notebook 5 · SFT: loss sulla risposta contro loss su tutti i token

```python
def sft(p, steps=400, lr=3e-4, all_tokens=False, seed=0):
    ...
        if all_tokens:
            m = (TR[0][idx] != EOT).astype(float); m[:, 0] = 1   # ogni token vero
        else:
            m = TR[2][idx]                                         # solo la risposta
        loss, cache = forward(p, TR[0][idx], TR[1][idx], m)
        opt.step(p, backward(p, cache))
```

Output:

```text
model                        test response loss  docstring perplexity
base model                                6.211                 118.4
SFT, loss on the response                 3.712                 382.4
SFT, loss on every token                  3.793                 408.2
```

Fine-tuning di **tutti** i parametri a partire dal base model: 400 passi da 16 esempi, Adam con learning rate $3\cdot10^{-4}$. Due versioni: loss solo sulla risposta (la maschera di prima) e loss su tutti i token reali, come nel pretraining. Due misure: la loss media sulle **risposte del test set** (mai viste) e la perplexity sulle docstring di validazione del pretraining.

- Entrambi gli SFT migliorano molto sulle risposte di test (da 6,2 a circa 3,7). La loss solo sulla risposta è un po' migliore (3,71 contro 3,79): addestrare anche sull'istruzione spende aggiornamenti su testo che il modello non deve scrivere.
- La perplexity sulle docstring **sale** (da 118 a 382 e 408): il modello si allontana dal pretraining verso il formato stretto delle istruzioni. È il **forgetting** (oblio), molto marcato qui per via dei pochi dati e del modello minuscolo.

Un dettaglio: nel caso `all_tokens` la riga `m[:, 0] = 1` è superflua (l'input in posizione 0 è sempre `<user>`, già diverso da `<eot>`), ma innocua.

> **Approfondimento: La nostra riesecuzione**
>
> Riesecuzione: base 6,546 / 148,0; SFT sulla risposta 4,275 / 324,9; SFT su tutti i token 4,357 / 340,9 (294 secondi). Valori assoluti diversi (corpus e base model diversi), stesse conclusioni: la loss solo sulla risposta è un po' migliore e il forgetting è forte in entrambi i casi.

### Notebook 6 · Che cosa ha imparato: formato e quando fermarsi

```python
def answer(p, instr, n=18):
    ids = [USER] + [stoi.get(w, UNK) for w in instr] + [ASSIST]
    for _ in range(n):
        t = int(np.argmax(forward(p, np.array(ids[-N:])[None])[0, -1]))
        ids.append(t)
        if t == END: break
```

Output:

```text
what does fields do
   docstring: return a tuple describing the fields of this dataclass
   base     : to the <unk> to the <unk> of the <unk> of the <unk> of the <unk> <unk> <unk> <unk>
   SFT      : <unk> a <unk> object <end>
what does tostring do
   docstring: generate string representation of xml element
   SFT      : return a <unk> object <end>
answers that end with <end>, on 60 test instructions: base 0%, SFT 100%
```

Generazione greedy dopo `<user>` istruzione `<assistant>`, fino a `<end>` o 18 token: è l'inferenza della [scheda 16](L18-post-training-i-instruction-tuning-lora-e-prompting.md#p-16). Il base model continua con parole da docstring in ciclo e **non si ferma mai** (non ha mai visto `<end>`): 0% delle risposte termina. Dopo l'SFT **tutte** le risposte sono una frase breve in stile docstring (*return a ...*) chiusa da `<end>`: 100%.

Il contenuto è spesso vago o sbagliato: il modello minuscolo non ricorda le docstring, anche se le aveva viste nel pretraining. Ciò che l'instruction tuning ha insegnato è il **formato** della risposta e **quando fermarsi**: una versione in miniatura dell'ipotesi dell'allineamento superficiale di LIMA ([scheda 20](L18-post-training-i-instruction-tuning-lora-e-prompting.md#p-20)), e la prova pratica del perché `<end>` deve stare nella loss.

> **Attenzione (errore nelle slide): Fragilità: molte istruzioni non dicono quale funzione**
>
> Il commento della cella attribuisce le risposte vaghe al fatto che il modello minuscolo non ricorda le docstring. C'è una causa più diretta nei dati: il vocabolario è fatto di 1500 parole delle docstring, e i nomi delle funzioni spesso non ci sono. Contando sulle celle 8 e 12 rieseguite, in **324 esempi su 757** (43%) tutte le parole del nome sono `<unk>`, e così 40 istruzioni di test su 94: l'istruzione diventa *what does <unk> do*, identica per funzioni diverse, e nessun modello potrebbe indovinare la risposta. Il filtro della cella 12 controlla le parole sconosciute solo nella risposta. La conclusione didattica (l'SFT insegna formato e stop) resta valida, ma per misurare anche il contenuto bisognerebbe scartare gli esempi con il nome tutto fuori vocabolario (o usare una tokenizzazione in subword come BPE, L2).

> **Approfondimento: La nostra riesecuzione**
>
> Riesecuzione: il base model, più debole (perplexity 148), produce solo `<unk>`; l'SFT dà **la stessa risposta** *return a <unk> the given a <unk> the given file* a quattro istruzioni diverse (*findlinestarts*, *parse229*, *purge*, *isgeneratorfunction*) e termina con `<end>` nel 90% dei casi invece del 100%. Il formato è imparato, il contenuto ignora l'istruzione.

### Notebook 7 · LoRA in numpy

```python
LORA = ["Wq", "Wk", "Wv", "Wo", "W1", "W2"]
def lora_init(p, r_):   # A ~ N(0, 1/k), B = 0
    return {k: (rr.normal(0, 1/np.sqrt(p[k].shape[0]), (p[k].shape[0], r_)),
                np.zeros((r_, p[k].shape[1]))) for k in LORA}
def with_lora(p, L, special=None):
    q = dict(p)
    for k, (A_, B_) in L.items():
        q[k] = p[k] + A_ @ B_
    ...
gW = backward(q, cache)                   # gradiente come se W fosse addestrata
g[k + ".A"] = gW[k] @ train[k + ".B"].T   # dL/dA = dL/dW B^T
g[k + ".B"] = train[k + ".A"].T @ gW[k]   # dL/dB = A^T dL/dW
```

Output:

```text
start: largest difference between the logits with LoRA and the base model: 0.0
LoRA r = 1: trained parameters  1,344 (0.9% of 147,904);  test response loss 3.841;  docstring perplexity 246.8
LoRA r = 4: trained parameters  4,800 (3.2% of 147,904);  test response loss 3.834;  docstring perplexity 310.3
full SFT:     trained parameters 147,904 (100%);  test response loss 3.712;  docstring perplexity 382.4
```

LoRA sulle sei matrici del blocco ($W^Q, W^K, W^V, W^O$ e le due del feedforward), con $A$ casuale e $B = 0$ come nella [scheda 35](L18-post-training-i-instruction-tuning-lora-e-prompting.md#p-35). La prima riga lo verifica: all'inizio i logit coincidono esattamente con quelli del base model (differenza 0,0).

Il trucco per i gradienti: il backward esistente calcola $G = \partial L/\partial W$ per la matrice effettiva $W + AB$; la regola della catena dà $\partial L/\partial A = GB^\top$ e $\partial L/\partial B = A^\top G$ (esercizio 9). Si aggiornano solo $A$, $B$ e gli embedding dei **tre token speciali**, che sono nuovi e vanno imparati (le librerie LoRA hanno un'opzione per questo).

Conteggio verificato: per rango $r$, $4\cdot r(64+64) + 2\cdot r(64+256) = 1152r$, più $3\cdot64 = 192$ embedding: 1344 per $r = 1$ (0,91%), 4800 per $r = 4$ (3,25%). Risultati salvati: con meno dell'1% dei parametri la loss di test (3,84) è vicina a quella dell'SFT completo (3,71), e la perplexity sulle docstring cresce meno (247 e 310 contro 382): un aggiornamento a basso rango tende a spostare meno il modello. Il docente avverte che con così pochi dati questo varia da esecuzione a esecuzione.

> **Approfondimento: La nostra riesecuzione**
>
> Riesecuzione: r = 1, loss di test 4,320 e perplexity 208,5; r = 4, 4,304 e 246,3; SFT completo 4,275 e 324,9 (246 secondi). Anche qui LoRA si avvicina all'SFT completo con meno dell'1% dei parametri e dimentica meno, e il forgetting cresce con il rango; la verifica iniziale (differenza 0,0) e i conteggi 1344 e 4800 sono identici.

### Notebook 8 · Fondere AB in W e il rango dell'aggiornamento

```python
print(np.abs(x_ @ (base["Wq"] + A_ @ B_) - (x_ @ base["Wq"] + (x_ @ A_) @ B_)).max())
print(np.linalg.matrix_rank(A_ @ B_))
```

Output:

```text
largest difference between x(W + AB) and xW + (xA)B: 1.6653345369377348e-15
rank of the update AB of W_Q: 1  (r = 1)
what does args from interpreter flags do -> return true if the object is a string <end>
```

Due verifiche della [scheda 39](L18-post-training-i-instruction-tuning-lora-e-prompting.md#p-39): $x(W + AB)$ e $xW + (xA)B$ coincidono a meno dell'errore di arrotondamento ($10^{-15}$), quindi dopo l'addestramento si può sostituire $W$ con $W + AB$ e il modello costa come prima; e l'aggiornamento appreso per $W^Q$ con $r = 1$ ha davvero **rango 1**. Anche il modello LoRA risponde nel formato giusto e si ferma con `<end>`.

### Notebook 9 · Quantizzazione a 4 bit: livelli uniformi e normali

```python
def quantize(Wm, levels, block=64):
    for s in range(0, len(flat), block):
        b = flat[s:s + block]; scale = np.abs(b).max() or 1.0
        out[s:s + block] = levels[np.abs(b[:, None] / scale - levels[None]).argmin(1)] * scale
uniform = np.linspace(-1, 1, 16)
normal = [NormalDist().inv_cdf(q) for q in np.linspace(0.03, 0.97, 16)]; normal /= max|normal|
```

Output:

```text
levels, uniform: [-1.   -0.87 -0.73 -0.6  -0.47 -0.33 -0.2  -0.07  0.07  0.2   0.33  0.47  0.6   0.73  0.87  1.  ]
levels, normal:  [-1.   -0.7  -0.54 -0.41 -0.31 -0.21 -0.13 -0.04  0.04  0.13  0.21  0.31  0.41  0.54  0.7   1.  ]
16-bit model           test response loss 3.712
4 bits, uniform        test response loss 3.791   mean relative error of the weights 0.108
4 bits, normal         test response loss 3.755   mean relative error of the weights 0.092
```

La [scheda 40](L18-post-training-i-instruction-tuning-lora-e-prompting.md#p-40) in codice: blocchi di 64 pesi, ognuno scalato per il suo massimo assoluto, ogni peso sostituito dal livello più vicino fra 16. Due insiemi di livelli: equispaziati, oppure ai quantili di una normale (fitti vicino a 0), l'idea del 4-bit NormalFloat. Si quantizzano tutte le matrici del modello SFT.

Risultato salvato: l'errore relativo medio sui pesi è circa il 10% (0,108 uniforme, 0,092 normale) ma la loss di test sale poco (da 3,71 a 3,79 e 3,76); i livelli normali sono migliori, come previsto. Memoria: 4 volte meno dei 16 bit, più una scala per blocco.

Una differenza rispetto al vero NF4: questi 16 livelli sono simmetrici e **non contengono lo zero** (i due più vicini sono $\pm0{,}04$); NF4 è costruito in modo asimmetrico proprio per avere uno zero esatto. È una semplificazione didattica, non un errore.

> **Approfondimento: La nostra riesecuzione**
>
> Riesecuzione: da 4,275 a 4,303 (uniforme, errore relativo 0,108) e 4,299 (normale, 0,091): stesso ordine, con un aumento della loss ancora più piccolo.

### Notebook 10 · I numeri della lezione: parametri LoRA e memoria

```python
def lora_params(k, dd, r_): return r_ * (k + dd)
g3 = lora_params(12288, 12288, 4) * 2 * 96
l7 = lora_params(4096, 4096, 16) * 2 * 32
for n_ in (1e9, 7e9, 65e9, 70e9):
    print(n_ * 16 / 1e9, n_ * 2 / 1e9, n_ * 0.5 / 1e9)
```

Output:

```text
one matrix 4,096 x 4,096:  full 16777216   LoRA r = 8: 65536   (0.39%)
GPT-3, r = 4 on W_Q and W_V of 96 layers: 18,874,368 parameters, 9,272 times fewer than 175B, checkpoint 37.7 MB in 16 bits
7B model, r = 16 on W_Q and W_V of 32 layers: 8,388,608 parameters (0.12% of 7B), 134 MB with Adam
    1B: full     16 GB   LoRA   2.0 GB   QLoRA   0.5 GB
    7B: full    112 GB   LoRA  14.0 GB   QLoRA   3.5 GB
   65B: full   1040 GB   LoRA 130.0 GB   QLoRA  32.5 GB
   70B: full   1120 GB   LoRA 140.0 GB   QLoRA  35.0 GB
```

I conti delle [schede 31](L18-post-training-i-instruction-tuning-lora-e-prompting.md#p-31), [38](L18-post-training-i-instruction-tuning-lora-e-prompting.md#p-38) e [41](L18-post-training-i-instruction-tuning-lora-e-prompting.md#p-41), tutti verificati: 0,39% per una matrice $4096\times4096$ con $r = 8$; GPT-3 con $r = 4$ su $W^Q$ e $W^V$, 18,9 milioni di parametri, circa 9272 volte meno, checkpoint di 37,7 MB; un 7B con $r = 16$ su $W^Q$ e $W^V$, lo 0,12% dei parametri e 134 MB con Adam, trascurabili rispetto ai 14 GB del modello congelato. La tabella della memoria riproduce 112 / 14 / 3,5 GB per il 7B e mostra che un 65B in QLoRA (32,5 GB) entra in una GPU da 48 GB. Output deterministico, identico nella riesecuzione.

### Notebook 11 · Verifica degli esercizi della scheda

```python
p_resp = np.array([0.30, 0.50, 0.60, 0.80]); p_instr = np.array([0.10, 0.20, 0.05, 0.40, 0.30, 0.25])
x7 = np.array([2, 0, 1]); W7 = ...; A7 = np.array([[1], [0], [2]]); B7 = np.array([[1, -1, 0]])
...
```

Output:

```text
1   [1.204 0.693 0.511 0.223] sum 2.631 mean 0.658 | instruction [2.303 1.609 2.996 0.916 1.204 1.386] all ten 1.305
5   0.0096 $ per instruction; 52 times; 1000000000.0 tokens, 0.0067%
6   [(1, 16, 2, 0.5), (7, 112, 14, 3.5), (70, 1120, 140, 35.0)] GPUs: 14 ; 65B in 4 bits: 32.5 GB
7   xW [3 2 1] xA 4 xAB [ 4 -4  0] h [ 7 -2  1] AB [[1, -1, 0], [0, 0, 0], [2, -2, 0]] x(W+AB) [ 7 -2  1]
8   98304 18874368 9272 37.7 MB 36.0 MiB
9   x(W+AB) - (xW + xAB): 4.440892098500626e-16 | A = B = 0: largest gradient of A 0.0 of B 0.0
10  [[1, 2, 0, 1], [2, 4, 0, 2], [-1, -2, 0, -1]] 2048.0 [ 0.3 -0.1  0.1 -0.3] [-0.05  0.08  0.08 -0.1 ] 4.5 3.9375 GB
```

I numeri delle soluzioni degli esercizi 1 e 5-10, che coincidono con quelli calcolati nella sezione Studio. Per l'esercizio 9 la cella usa matrici casuali per verificare la distributività e mostra che con $A = B = 0$ i gradienti di $A$ e $B$ sono esattamente nulli. Per l'esercizio 10 gli errori di quantizzazione sono "peso meno livello". Gli esercizi 2-4, 11 e 12 chiedono template, prompt e spiegazioni e non hanno una cella.

### Notebook 12 · Che cosa fare dopo e la cella facoltativa

```python
# OPTIONAL: needs an internet connection and the transformers library
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
print(tok.apply_chat_template(messages, tokenize=False))
print(tok.apply_chat_template(messages[:2], tokenize=False, add_generation_prompt=True))
```

Le proposte del docente: allenare l'SFT più a lungo o con learning rate $10^{-3}$ (la loss sulle risposte di training continua a scendere, quella di test no: con 688 esempi il modello **memorizza**); confrontare il forgetting fra SFT completo e LoRA con ranghi diversi; mettere LoRA solo su $W^Q$ e $W^V$ come negli esperimenti su GPT-3; quantizzare a 3 o 2 bit per vedere dove la loss comincia a salire.

L'ultima cella (non eseguita qui: richiede internet e `transformers`) stampa il chat template reale di TinyLlama con `apply_chat_template`, con e senza `add_generation_prompt=True`: la seconda forma è il prompt di inferenza che termina con `<|assistant|>`. Per il progetto è il modo corretto di costruire i prompt di un modello chat, invece di scrivere i marcatori a mano.

## Studio ed esercizi

### Guida allo studio (circa 3 h 25 min)

**Il progetto: date e tema** (10 min)

Schede 2-4. Segnare le scadenze: gruppi e corresponding author entro martedì 27 ottobre, tema definitivo nel foglio Topics entro giovedì 29, proposta iniziale per email lunedì 2 novembre, presentazioni 11-12 e 24-26 novembre, poster, codice e report giovedì 3 dicembre. Leggere nel PDF su Teams la scheda del tema 5 (Hate Speech and Offensive Language Detection), provvisorio per il gruppo 5.

**Perché il post-training e l'instruction tuning** (45 min)

Schede 7-20. Saper raccontare le quattro fasi (figura delle schede 7-8), i due problemi del base model con gli esempi di Ouyang et al. (luna, cagnolino, furto al supermercato) e la loro causa (obiettivo disallineato). Instruction tuning = SFT: stessi dati in formato istruzione-risposta, stessa cross-entropy, loss solo sulla risposta; perché si chiama supervised; meta-learning. Rifare a mano l'esercizio delle schede 17-18 (0,42 contro 1,06) e saper scrivere un chat template con le parti addestrate. Libro §8.1 (pp. 210-211) e §1.6.2 (pp. 17-19). Esercizi 1, 2, 5.

**Dati di istruzione e valutazione** (25 min)

Schede 22-27. Le tre fonti dei dati con un esempio ciascuna (Aya scritto da volontari; template di Fig. 8.4 riempiti con i campi di Fig. 8.3; dati di sicurezza di Bianchi et al., 500 istruzioni bastano), i quattro dataset con i loro ordini di grandezza, perché si parafrasano i template. Valutazione leave-one-out per cluster e perché non per singolo dataset. Libro §8.1.1-8.1.2 (pp. 211-213). Esercizi 3, 4.

**PEFT, LoRA, quantizzazione, QLoRA** (60 min)

Schede 30-41: la parte più calcolabile della lezione. Saper giustificare i 16 byte per parametro e i 112 GB del 7B; disegnare la Fig. 8.8 con le forme ($W$ $k\times d$, $A$ $k\times r$, $B$ $r\times d$); scrivere $h = xW + xAB$; contare $r(k+d)$ contro $kd$ (0,39% per $k = d = 4096$, $r = 8$); spiegare l'inizializzazione $B = 0$ e perché non entrambe a zero; merge e moduli intercambiabili; quantizzazione a 4 bit con scala per blocco e NF4; i tre numeri 112 / 14 / 3,5 GB. Libro §8.2 (pp. 213-215). Esercizi 6-10, 13, 14.

**Prompting e in-context learning** (25 min)

Schede 43-46. Definizioni di inference, prompt engineering, dimostrazioni, zero-shot e few-shot (il prompt one-shot di MMLU con risposta B), system prompt, in-context learning e la differenza con il fine-tuning. Dal libro anche il chain-of-thought prompting e i passi dell'inferenza di §1.7.1. Libro §1.7 (pp. 21-24). Esercizi 11, 12, 15.

**Notebook e ripasso orale** (40 min)

Eseguire il notebook (circa cinque-dieci minuti) e controllare in particolare la maschera della loss (sezione 4), il confronto base / SFT / LoRA (sezioni 5-6) e i numeri della sezione 8. Poi le domande orali, a voce, senza guardare le tracce.

### Esercizi

#### Esercizio 1 (scheda L18): la loss sulla risposta

Esempio di addestramento nel chat template: l'utente chiede *Summarize: the meeting is moved to Friday*, l'assistente risponde *meeting on Friday*, poi `</s>`. Probabilità (giocattolo; *Summarize* e i due punti esclusi): istruzione *the* 0,10, *meeting* 0,20, *is* 0,05, *moved* 0,40, *to* 0,30, *Friday* 0,25; risposta *meeting* 0,30, *on* 0,50, *Friday* 0,60, `</s>` 0,80.

1. Quali token entrano nella loss dell'instruction tuning? Loss $-\ln P$ e media.
2. Media se si addestrassero tutti e dieci i token. Quali pesano di più?
3. Perché è importante addestrare `</s>` della risposta? E perché non il marcatore `<|assistant|>`?

<details><summary>Soluzione</summary>

(a) Solo i quattro token della risposta: $-\ln 0{,}30 = 1{,}204$; $-\ln 0{,}50 = 0{,}693$; $-\ln 0{,}60 = 0{,}511$; $-\ln 0{,}80 = 0{,}223$. Somma 2,631, **media 0,658**.

(b) Istruzione: $-\ln 0{,}10 = 2{,}303$; $-\ln 0{,}20 = 1{,}609$; $-\ln 0{,}05 = 2{,}996$; $-\ln 0{,}40 = 0{,}916$; $-\ln 0{,}30 = 1{,}204$; $-\ln 0{,}25 = 1{,}386$; somma 10,414. Totale $10{,}414 + 2{,}631 = 13{,}045$, **media 1,305**, quasi il doppio. Pesano di più *is* (2,996) e *the* (2,303), entrambi nell'istruzione: il modello non può prevedere che cosa l'utente vuole riassumere, e non deve impararlo.

(c) Il `</s>` della risposta è il modo in cui il modello impara a **fermarsi**: all'inferenza la generazione si interrompe quando lo produce; senza, continuerebbe a scrivere. Il marcatore `<|assistant|>` lo aggiunge sempre il programma alla fine del prompt: il modello non deve mai generarlo, quindi non ha senso spenderci gradiente. (Numeri verificati nella cella 29 del notebook.)

</details>

#### Esercizio 2 (scheda L18): un chat template

Template di TinyLlama: `<|user|>` e `<|assistant|>` su una riga propria prima di ogni turno, `</s>` alla fine di ogni turno.

1. Scrivere come un'unica sequenza di addestramento la conversazione: utente *What is the capital of Italy?*, assistente *Rome.*, utente *And of France?*, assistente *Paris.*
2. Indicare le parti che ricevono una loss nell'instruction tuning.
3. All'inferenza, dopo che l'utente scrive *And of Spain?*, che testo dà il programma al modello, e dove si ferma il modello?

<details><summary>Soluzione</summary>

(a)

```
<|user|>
What is the capital of Italy?</s>
<|assistant|>
Rome.</s>
<|user|>
And of France?</s>
<|assistant|>
Paris.</s>
```

(b) Solo i turni dell'assistente con il loro terminatore: **Rome.</s>** e **Paris.</s>**. Marcatori, domande e `</s>` dei turni utente sono contesto.

(c) Tutta la conversazione precedente (le quattro parti di (a)), poi `<|user|>`, *And of Spain?*`</s>` e infine `<|assistant|>` con l'a capo. Il modello genera *Madrid.* e si ferma quando produce `</s>`. Notare che *And of Spain?* si capisce solo grazie ai turni precedenti nel contesto.

</details>

#### Esercizio 3 (scheda L18): istruzioni da dataset NLP

Due esempi: una recensione per il sentiment (text *The plot was predictable and the acting was flat*, label 0) e un esempio di QA estrattivo (context *The Arno flows through Florence and Pisa before reaching the sea.*, question *Which cities does the Arno flow through?*, answer *Florence and Pisa*).

1. Nel dataset di sentiment 0 = negativo, 1 = positivo. Con i template della Fig. 8.4 scrivere un'istruzione con risposta per ciascun esempio.
2. Scrivere altre due formulazioni del template di sentiment. Perché i dataset di istruzioni usano molte formulazioni dello stesso template?
3. Un template scritto per recensioni di film viene applicato a recensioni di ristoranti. Che cosa va storto? Che cosa insegna sulla costruzione di istruzioni da dataset?

<details><summary>Soluzione</summary>

(a) Sentiment: *The plot was predictable and the acting was flat How does the reviewer feel about the movie?* Risposta: *Negative* (o *The reviewer did not like it*): l'etichetta 0 va tradotta in parole. QA: *The Arno flows through Florence and Pisa before reaching the sea. Using the passage, which cities does the Arno flow through?* Risposta: *Florence and Pisa*.

(b) Per esempio *{{text}} Is this review positive or negative?* e *Here is a movie review: {{text}} What is the opinion of the author?* Le formulazioni multiple (spesso parafrasate da un LLM) evitano che il modello associ il compito a una frase esatta: gli utenti formulano le richieste in mille modi, e il modello deve imparare il compito, non il template.

(c) L'istruzione chiede come il recensore giudica *il film* davanti a una recensione di un ristorante: istruzione e input sono incoerenti, e il modello impara da esempi in cui la domanda non corrisponde al testo (o impara a ignorare la domanda). I template vanno scritti per ciascun dataset, rispettandone dominio e significato delle etichette, e controllati su qualche esempio istanziato.

</details>

#### Esercizio 4 (scheda L18): leave one out

Una collezione ha 12 dataset in quattro cluster: sentiment (3), NLI (4), question answering (3), summarization (2).

1. Per valutare la capacità di NLI, su quali dataset si fa instruction tuning e su quali si testa?
2. Quanti modelli instruction-tuned servono per valutare ogni cluster così?
3. Perché non escludere solo uno dei quattro dataset NLI e addestrare sugli altri undici?

<details><summary>Soluzione</summary>

(a) Instruction tuning sugli $3 + 3 + 2 = 8$ dataset di sentiment, QA e summarization; test sui **4 dataset NLI**, tutti esclusi.

(b) **4**, uno per cluster tenuto fuori.

(c) Gli altri tre dataset NLI insegnerebbero proprio il compito NLI: il test misurerebbe la generalizzazione a un nuovo dataset dello stesso compito, non a un **compito nuovo**, che è lo scopo dell'instruction tuning. È il motivo per cui Super-NaturalInstructions, con 25 dataset di entailment, si valuta per cluster.

</details>

#### Esercizio 5 (scheda L18): quanti dati, a che costo

1. Alpaca: 52 000 istruzioni e risposte generate per meno di 500 dollari. Costo per istruzione? LIMA ha usato 1000 esempi curati: quante volte meno di Alpaca?
2. Un dataset di istruzioni ha 1 milione di esempi di circa 200 token, usato per 5 epoche. Quanti token vede il modello? Che frazione è dei 15 000 miliardi di token del pretraining di Llama 3.1?
3. LIMA suggerisce che la conoscenza venga dal pretraining e che il post-training insegni il formato. Come si accordano i numeri di (b) con questa visione?

<details><summary>Soluzione</summary>

(a) $500/52\,000 \approx 0{,}0096$ dollari, circa un centesimo per istruzione. LIMA: $52\,000/1000 = 52$ volte meno esempi.

(b) $10^6\cdot200\cdot5 = 10^9$ token; $10^9/(15\cdot10^{12}) \approx 6{,}7\cdot10^{-5}$, cioè lo **0,0067%**.

(c) Con meno di un decimillesimo dei token del pretraining il comportamento del modello cambia completamente (da continuare testo a rispondere): troppo pochi dati per insegnare molta conoscenza nuova, abbastanza per insegnare un formato e uno stile. È coerente con l'idea che il sapere sia già nel base model e che l'SFT insegni come usarlo (scheda 20).

</details>

#### Esercizio 6 (scheda L18): la memoria del fine-tuning

Fine-tuning completo con Adam in mixed precision: circa 16 byte per parametro (senza attivazioni). Con LoRA i pesi congelati occupano 2 byte per parametro (16 bit); con QLoRA 0,5 byte (4 bit). Trascurare le matrici LoRA e le attivazioni.

1. Memoria del fine-tuning completo per modelli da 1B, 7B, 70B. Quante GPU da 80 GB servono almeno per il 70B?
2. Lo stesso con LoRA e QLoRA.
3. QLoRA ha fatto fine-tuning di un 65B su una GPU da 48 GB: è coerente?

<details><summary>Soluzione</summary>

(a) 1B: 16 GB; 7B: 112 GB; 70B: 1120 GB. Per il 70B almeno $\lceil 1120/80\rceil = 14$ GPU.

(b) LoRA: 2 GB, 14 GB, 140 GB. QLoRA: 0,5 GB, 3,5 GB, 35 GB.

(c) Sì: $65\cdot0{,}5 = 32{,}5$ GB di pesi a 4 bit, sotto i 48 GB; i circa 15 GB rimasti servono alle matrici LoRA con il loro stato di Adam e alle attivazioni. Con LoRA a 16 bit servirebbero 130 GB, con il fine-tuning completo 1040 GB.

</details>

#### Esercizio 7 (scheda L18): LoRA a mano

$k = d = 3$, $r = 1$: $x = [2, 0, 1]$, $W$ con righe $[1,1,0]$, $[0,1,0]$, $[1,0,1]$; $A = [1, 0, 2]^\top$, $B = [1, -1, 0]$.

1. Calcolare $xW$, $xA$, $xAB$ e $h = xW + xAB$.
2. Calcolare $AB$ e verificare che $x(W + AB)$ dia lo stesso $h$. Perché ogni riga di $AB$ è un multiplo di $B$?
3. Quanti parametri si addestrano? Quanti ne addestrerebbe il fine-tuning completo di $W$?

<details><summary>Soluzione</summary>

(a) $xW = 2\cdot[1,1,0] + 0\cdot[0,1,0] + 1\cdot[1,0,1] = [3, 2, 1]$; $xA = 2\cdot1 + 0\cdot0 + 1\cdot2 = 4$; $xAB = 4\cdot[1,-1,0] = [4, -4, 0]$; $h = [7, -2, 1]$.

(b) $AB = \begin{bmatrix}1&-1&0\\0&0&0\\2&-2&0\end{bmatrix}$; $W + AB = \begin{bmatrix}2&0&0\\0&1&0\\3&-2&1\end{bmatrix}$; $x(W+AB) = 2\cdot[2,0,0] + 1\cdot[3,-2,1] = [7, -2, 1]$, uguale. La riga $i$ di $AB$ è $A_i\cdot B$ (lo scalare $A_i$ per la riga $B$): con $r = 1$ tutte le righe sono multiple della stessa, rango 1.

(c) LoRA: $3 + 3 = 6$; completo: $3\cdot3 = 9$. (Verificato nella cella 29 del notebook.)

</details>

#### Esercizio 8 (scheda L18): LoRA su GPT-3

GPT-3 175B ha 96 strati e $d = 12\,288$. Hu et al. (2022) hanno applicato LoRA con $r = 4$ solo a $W^Q$ e $W^V$.

1. Quanti parametri addestra LoRA per una matrice? Per il modello intero?
2. Quante volte meno dei 175 miliardi del fine-tuning completo? Confrontare con le "10 000 volte" dell'articolo.
3. Il checkpoint salva i parametri addestrati a 16 bit: quanto pesa? Confrontare con i 35 MB dell'articolo.

<details><summary>Soluzione</summary>

(a) Una matrice: $r(k+d) = 4\cdot(12\,288 + 12\,288) = 98\,304$. Modello: $98\,304\cdot2\cdot96 = 18\,874\,368$, circa 18,9 milioni.

(b) $175\cdot10^9/18\,874\,368 \approx 9272$: dell'ordine delle 10 000 volte dell'articolo (che arrotonda); è lo 0,011% dei parametri.

(c) $18\,874\,368\cdot2$ byte $= 37{,}7$ MB $= 36{,}0$ MiB, vicino ai 35 MB riportati, contro circa 350 GB per un checkpoint completo a 16 bit.

</details>

#### Esercizio 9 (scheda L18): fondere, scambiare, partire

1. Mostrare che $x(W + AB) = xW + xAB$. Che cosa significa per il costo dell'inferenza con un modello LoRA?
2. Un'azienda ha un modello base e due moduli LoRA, $A_1B_1$ (testi legali) e $A_2B_2$ (testi medici). I pesi in uso sono $W + A_1B_1$. Come passa al modulo medico?
3. LoRA parte con $A$ casuale e $B = 0$. Qual è il modello all'inizio? Con $G = \partial L/\partial W$ (il gradiente rispetto alla matrice effettiva $W + AB$), $\partial L/\partial A = GB^\top$ e $\partial L/\partial B = A^\top G$. Che cosa succederebbe con $A$ e $B$ entrambe nulle?

<details><summary>Soluzione</summary>

(a) Proprietà distributiva del prodotto matrice-vettore: $x(W + AB) = xW + x(AB) = xW + (xA)B$. Dopo l'addestramento si calcola una volta $W' = W + AB$ e si usa $W'$ al posto di $W$: stesse dimensioni, stesso numero di operazioni, **nessun costo aggiuntivo** all'inferenza.

(b) $W + A_1B_1 - A_1B_1 + A_2B_2 = W + A_2B_2$: si sottrae il modulo legale e si somma quello medico (oppure si ricarica $W$ e si somma $A_2B_2$). Serve conservare $W$ o i moduli, che pesano pochi MB.

(c) All'inizio $AB = 0$: il modello è esattamente il **modello base**. Con $A = B = 0$: $\partial L/\partial A = G\cdot0 = 0$ e $\partial L/\partial B = 0\cdot G = 0$; i gradienti sono nulli, i parametri non si muovono mai e l'addestramento resta bloccato. Con $A$ casuale, $\partial L/\partial B = A^\top G \neq 0$ e $B$ si muove subito (verificato nella cella 29: gradienti massimi 0,0 con $A = B = 0$).

</details>

#### Esercizio 10 (scheda L18): rango e quantizzazione

1. La matrice $3\times4$ con righe $[1,2,0,1]$, $[2,4,0,2]$, $[-1,-2,0,-1]$ si scrive come $AB$ con $r = 1$. Trovare $A$ e $B$.
2. Per $k = d = 4096$, per quale rango $r$ LoRA addestra tanti parametri quanto il fine-tuning completo?
3. Quantizzazione giocattolo con 4 livelli (2 bit): $-0{,}3; -0{,}1; 0{,}1; 0{,}3$. Quantizzare i pesi $[0{,}25;\ -0{,}02;\ 0{,}18;\ -0{,}40]$ al livello più vicino e calcolare gli errori.
4. Con 4 bit per peso più una scala a 32 bit ogni blocco di 64 pesi, quanti bit per peso in media? Memoria di un modello da 7B?

<details><summary>Soluzione</summary>

(a) Le righe sono $1$, $2$ e $-1$ volte $[1,2,0,1]$: $A = [1, 2, -1]^\top$, $B = [1, 2, 0, 1]$ (o qualunque coppia $cA$, $B/c$).

(b) $r(k+d) = kd \Rightarrow r = \frac{kd}{k+d} = \frac{4096^2}{8192} = 2048$. Ogni $r$ realistico (4-64) è molto sotto.

(c) $0{,}25\to0{,}3$ (errore $-0{,}05$); $-0{,}02\to-0{,}1$ (errore $0{,}08$; $0{,}1$ disterebbe 0,12); $0{,}18\to0{,}1$ (errore $0{,}08$; $0{,}3$ disterebbe 0,12); $-0{,}40\to-0{,}3$ (errore $-0{,}10$, fuori dall'intervallo dei livelli). Errori (peso meno livello): $[-0{,}05;\ 0{,}08;\ 0{,}08;\ -0{,}10]$.

(d) $4 + 32/64 = 4{,}5$ bit per peso; $7\cdot10^9\cdot4{,}5/8 = 3{,}94\cdot10^9$ byte $\approx 3{,}9$ GB (contro 3,5 GB senza scale e 14 GB a 16 bit).

</details>

#### Esercizio 11 (scheda L18): dimostrazioni e in-context learning

1. Scrivere un prompt 2-shot che chieda in che lingua è scritta una frase, che finisca con la frase *Ich habe Hunger.*
2. Scrivere una versione zero-shot dello stesso compito, con un system prompt.
3. Min et al. (2022) hanno trovato che dimostrazioni con etichette sbagliate possono comunque aiutare. Che cosa mostrano al modello le dimostrazioni di (a), anche se le etichette fossero sbagliate?
4. Dopo una lunga conversazione con molte dimostrazioni, il modello riconosce benissimo le lingue. Un utente apre una nuova conversazione: il modello conserva questa capacità? Che cosa la renderebbe permanente?

<details><summary>Soluzione</summary>

(a) Per esempio:

```
Say in which language each sentence is written.
Sentence: Je suis fatigué.   Language: French
Sentence: Tengo frío.        Language: Spanish
Sentence: Ich habe Hunger.   Language:
```

(b) System: *You are a language identification assistant. Answer with the name of the language only.* Utente: *In which language is this sentence written? Ich habe Hunger.* (risposta attesa: *German*).

(c) Il **formato** (una sola parola dopo *Language:*), lo **spazio delle etichette** (nomi di lingue), il tipo di **input** (frasi brevi in lingue diverse): cioè quale compito si sta chiedendo. Secondo il libro (§1.7) è questo il beneficio principale delle dimostrazioni, più che le risposte giuste.

(d) No: l'in-context learning non cambia i pesi; finita la conversazione ciò che il modello aveva "imparato" sparisce. Per renderlo permanente bisogna cambiare i pesi: **fine-tuning** (per esempio con LoRA) su esempi del compito. Una soluzione intermedia è mettere istruzioni ed esempi nel system prompt, che però va rielaborato a ogni conversazione.

</details>

#### Esercizio 12 (scheda L18): dal prompt alla risposta

I passi dell'inferenza di §1.7.1, mescolati: (A) si sceglie un token; (B) la stringa è tokenizzata; (C) esce una distribuzione sul token successivo; (D) si assembla il prompt, con il system prompt; (E) la generazione si ferma al token di fine risposta; (F) ogni token diventa un embedding; (G) il token è aggiunto al contesto; (H) la sequenza passa nella rete.

1. Mettere i passi in ordine.
2. Il modello risponde *Charles Darwin.*, cioè 3 token, seguiti dal token di fine risposta. Quante volte si eseguono H, C e A?
3. Il system prompt di un assistente è lungo 3000 token e apre ogni conversazione. Perché è un costo all'inferenza, e quale idea della lezione sul pretraining lo riduce dentro una conversazione?

<details><summary>Soluzione</summary>

(a) **D, B, F, H, C, A, G**, poi si torna a H (ciclo H, C, A, G) finché non si arriva a **E**.

(b) Ogni token generato richiede un passaggio nella rete, una distribuzione e una scelta: 3 token di risposta più il token di fine risposta, quindi **4 volte** ciascuno di H, C, A (G si esegue 3 volte: il token di fine non serve aggiungerlo, la generazione si ferma).

(c) Prima di produrre il primo token della risposta il modello deve elaborare tutti i 3000 token del system prompt (più la domanda), con un costo di attenzione che cresce con la lunghezza del contesto; e lo fa a ogni conversazione. Dentro la conversazione la **KV cache** (L17) evita di ricalcolare key e value dei token già visti: il system prompt si elabora una volta, poi ogni nuovo token calcola solo la propria query, key e value.

</details>

#### Esercizio 13 (proprio): LoRA su un 7B intero

Un modello da 7B con 32 strati e $d = 4096$. Si applica LoRA con $r = 8$ alle quattro matrici dell'attenzione $W^Q, W^K, W^V, W^O$ ($4096\times4096$) di ogni strato.

1. Quanti parametri si addestrano? Che percentuale di 7 miliardi?
2. Memoria totale per il fine-tuning in 16 bit (pesi congelati a 2 byte, parametri LoRA a 16 byte con Adam), senza attivazioni. Confrontare con il fine-tuning completo.

<details><summary>Soluzione</summary>

(a) Per matrice $8\cdot8192 = 65\,536$; per strato $4\cdot65\,536 = 262\,144$; per 32 strati $8\,388\,608$, lo $8{,}39\cdot10^6/7\cdot10^9 = 0{,}12\%$. (Stesso numero del caso $r = 16$ su sole $W^Q$, $W^V$: raddoppiare $r$ e dimezzare le matrici si compensa.)

(b) Pesi congelati $7\cdot10^9\cdot2 = 14$ GB; LoRA $8{,}39\cdot10^6\cdot16 \approx 0{,}134$ GB; totale circa **14,1 GB** contro **112 GB** del fine-tuning completo: circa 8 volte meno, e quasi tutto è il modello congelato. Per scendere ancora bisogna comprimere proprio quello: QLoRA.

</details>

#### Esercizio 14 (proprio): il fattore di scala alpha/r

Nelle implementazioni di LoRA il forward è $h = xW + \frac{\alpha}{r}xAB$.

1. Con i dati della scheda 36 ($x = [1,2,1]$, $W = I$, $A = [1,0,1]^\top$, $B = [2,1,0]$, $r = 1$) e $\alpha = 2$, calcolare $h$.
2. Con $\alpha = 16$, quanto vale la scala per $r = 8$, $16$, $64$?
3. Che cosa cambia rispetto alla formula delle slide, e perché si usa?

<details><summary>Soluzione</summary>

(a) $xAB = [4, 2, 0]$ come nella scheda 37; scala $\alpha/r = 2$: $h = [1,2,1] + 2\cdot[4,2,0] = [9, 6, 1]$.

(b) $16/8 = 2$; $16/16 = 1$; $16/64 = 0{,}25$.

(c) La formula delle slide è il caso $\alpha = r$ (scala 1). La costante moltiplica l'aggiornamento: a parità di $\alpha$, aumentando $r$ il contributo di ciascuna direzione si riduce, e si può cambiare $r$ senza dover ricalibrare il learning rate. All'inferenza si fonde $W + \frac{\alpha}{r}AB$, sempre a costo zero.

</details>

#### Esercizio 15 (proprio): accuratezza di un classificatore few-shot su classi sbilanciate

Un test set di 100 commenti, 10 offensivi e 90 no. Un LLM in zero-shot risponde sempre *not offensive*. Lo stesso LLM in few-shot, con dimostrazioni bilanciate, segnala 15 commenti come offensivi, di cui 8 lo sono davvero.

1. Accuratezza dei due sistemi.
2. Precision, recall e F1 della classe offensiva per il few-shot; F1 per lo zero-shot.
3. Macro-F1 dei due sistemi. Quale metrica useresti per il progetto?

<details><summary>Soluzione</summary>

(a) Zero-shot: giusti i 90 non offensivi, accuratezza **90%**. Few-shot: TP = 8, FP = 7, FN = 2, TN = 83: accuratezza $(8 + 83)/100 = $ **91%**. Quasi uguali.

(b) Few-shot: precision $8/15 = 0{,}533$, recall $8/10 = 0{,}8$, F1 $= 2\cdot0{,}533\cdot0{,}8/(0{,}533+0{,}8) = 0{,}64$. Zero-shot: nessun positivo trovato, recall 0, F1 = 0.

(c) Classe non offensiva: zero-shot P = 0,9, R = 1, F1 = 0,947; few-shot P = $83/85 = 0{,}976$, R = $83/90 = 0{,}922$, F1 = 0,949. Macro-F1: zero-shot $(0 + 0{,}947)/2 = 0{,}474$; few-shot $(0{,}64 + 0{,}949)/2 = 0{,}794$. Con classi sbilanciate l'accuratezza premia il sistema inutile; per l'hate speech si riportano F1 della classe offensiva e macro-F1. (Numeri verificati in Python.)

</details>

### Domande tipo orale

<details><summary>Perché un base model non segue le istruzioni?</summary>

Traccia: (1) è addestrato a predire il token successivo nel testo del web: continua il prompt in modo plausibile; (2) esempi di Ouyang et al.: *Explain the moon landing to a six year old* diventa un'altra consegna, *Translate to French: The small dog* diventa *The small dog crossed the road*; (3) due problemi: poco utile (non segue istruzioni, debole nel ragionamento lungo) e dannoso (risposte pericolose, false, offensive; esempio del furto al supermercato); (4) causa: obiettivo del pretraining disallineato con ciò che serve alle persone; (5) rimedio: post-training.

</details>

<details><summary>Quali sono le fasi del post-training e che dati usa ciascuna?</summary>

Traccia: (1) base model = dopo il pretraining, prima del post-training; (2) instruction tuning (SFT): coppie istruzione-risposta, cross-entropy sulla risposta; (3) preference alignment (RLHF, DPO): coppie di risposte con la preferita; (4) RLVR: problemi con risposta verificabile (matematica, codice), ricompensa se corretta; (5) ognuna parte dal modello precedente (figura delle quattro fasi); (6) costo molto minore del pretraining.

</details>

<details><summary>Che cos'è l'instruction tuning e perché si chiama supervised fine-tuning?</summary>

Traccia: (1) fine-tuning di un base model su istruzioni di molti compiti con le loro risposte; (2) stesso obiettivo del pretraining, cross-entropy sul token successivo, ma solo sui token della risposta; (3) supervised perché ogni istruzione ha una risposta corretta, come un'etichetta, mentre nel pretraining il target è solo il testo che segue (self-supervised); (4) fine-tuning = ulteriori passate di addestramento su dati nuovi a partire da un modello preaddestrato; (5) risultato: impara i compiti e a seguire istruzioni in generale (meta-learning); (6) dati: al più milioni di esempi, poche epoche.

</details>

<details><summary>Perché nell'instruction tuning la loss si calcola solo sulla risposta? Fai un esempio numerico.</summary>

Traccia: (1) l'istruzione è il contesto: passa nella rete ma non entra nella loss (maschera $m_t = 0$); (2) l'istruzione è sempre data dall'utente, il modello non deve imparare a scriverla; (3) esempio *Translate to Italian: good night* / *buona notte*: media sulla risposta $(0{,}92 + 0{,}22 + 0{,}11)/3 \approx 0{,}42$, su tutti i token $8{,}49/8 \approx 1{,}06$, dominata da *good* ($-\ln 0{,}05 = 3{,}00$), imprevedibile per natura; (4) il `</s>` della risposta invece è addestrato: insegna a fermarsi; (5) nel notebook la loss sulla risposta dà una loss di test sulle risposte un po' migliore (3,71 contro 3,79).

</details>

<details><summary>Che cos'è un chat template? Che cosa si addestra e come si usa all'inferenza?</summary>

Traccia: (1) converte una conversazione in una sequenza di token con marcatori di ruolo (`<|system|>`, `<|user|>`, `<|assistant|>`) e un terminatore di turno `</s>` (TinyLlama); (2) loss solo sui turni dell'assistente e i loro `</s>`; (3) all'inferenza il programma scrive la conversazione e termina con `<|assistant|>`; il modello genera la risposta e si ferma a `</s>`; (4) ogni famiglia di modelli ha il suo template, va usato lo stesso dell'addestramento.

</details>

<details><summary>Da dove vengono i dati per l'instruction tuning?</summary>

Traccia: (1) scritti da persone: alta qualità, costosi (parte di Aya, volontari in 65 lingue); (2) convertiti da dataset NLP annotati: campi in coppie chiave/valore, inseriti in template (*Suppose {{premise}} Can we infer that {{hypothesis}}? Yes, no, or maybe?*), l'etichetta diventa la risposta; template parafrasati da LLM per varietà; (3) generati da LLM: es. dati di sicurezza di Bianchi et al. (domande dannose parafrasate, risposte sicure controllate da persone; 500 bastano a ridurre la dannosità); (4) dimensioni: Aya 513M, Super-NaturalInstructions 5M/1600 compiti, Flan 2022 15M/1836, OPT-IML 18M/2000.

</details>

<details><summary>Come si valuta un modello instruction-tuned?</summary>

Traccia: (1) l'obiettivo è seguire istruzioni per compiti nuovi, quindi il test va su compiti esclusi dall'addestramento; (2) leave-one-out: instruction tuning su molti compiti, test su quello escluso; (3) compiti simili (25 dataset di entailment in Super-NaturalInstructions) renderebbero il test troppo facile: si raggruppano in cluster e si esclude un cluster intero; (4) un modello per ogni cluster da valutare; (5) esempio della figura: training su NLI, QA, traduzione, riassunto, test sul sentiment.

</details>

<details><summary>Quanta memoria serve per fare fine-tuning completo di un modello da 7B e perché?</summary>

Traccia: (1) Adam in mixed precision: pesi 16 bit (2 byte), gradienti 16 bit (2), copia dei pesi a 32 bit e due momenti a 32 bit (12): 16 byte per parametro; (2) $7\cdot10^9\cdot16 = 112$ GB senza attivazioni; (3) una A100/H100 ha 80 GB: non basta; un 70B richiede 1120 GB, almeno 14 GPU; (4) da qui il bisogno di PEFT: con LoRA restano i 2 byte dei pesi congelati (14 GB), con QLoRA 0,5 byte (3,5 GB).

</details>

<details><summary>Spiega LoRA: forme delle matrici, forward pass e numero di parametri.</summary>

Traccia: (1) le matrici dense ($W^Q, W^K, W^V, W^O$, feedforward) restano congelate; (2) l'aggiornamento $\Delta W$ ($k\times d$) è scritto come $AB$, $A$ $k\times r$, $B$ $r\times d$, $r \ll \min(k,d)$; (3) forward $h = xW + xAB$, calcolato come $(xA)B$; (4) parametri $r(k+d)$ invece di $kd$: per $k = d = 4096$, $r = 8$, 65 536 contro 16 777 216, lo 0,39%; (5) perché funziona: l'aggiornamento necessario ha bassa dimensione intrinseca (Aghajanyan et al.); (6) $r$ tipico 4-64, compromesso costo/capacità; (7) esempio a mano: $h = [5,4,1]$.

</details>

<details><summary>Come si inizializzano A e B in LoRA, e perché non entrambe a zero?</summary>

Traccia: (1) $A$ casuale, $B = 0$: $AB = 0$ e il modello parte esattamente dal preaddestrato; (2) gradienti: con $G = \partial L/\partial W$, $\partial L/\partial A = GB^\top$, $\partial L/\partial B = A^\top G$; (3) se $A = B = 0$ entrambi i gradienti sono nulli e l'addestramento non parte; (4) con $A$ casuale $B$ riceve subito gradiente non nullo; (5) eventuale fattore $\alpha/r$ delle implementazioni.

</details>

<details><summary>Quali sono i vantaggi pratici di LoRA?</summary>

Traccia: (1) memoria: niente gradienti né stato di Adam per i pesi congelati; (2) nessun costo all'inferenza: $x(W + AB) = xW + xAB$, si fonde $AB$ in $W$ una volta; (3) moduli intercambiabili: un LoRA per dominio o compito, si somma o si sottrae da $W$; checkpoint piccoli (GPT-3, $r = 4$ su $W^Q$, $W^V$: circa 18,9 milioni di parametri, 37,7 MB); (4) originariamente solo sulle matrici dell'attenzione, oggi molte varianti; (5) limite: rango basso, meno espressivo di un $\Delta W$ completo.

</details>

<details><summary>Che cos'è la quantizzazione e come la usa QLoRA?</summary>

Traccia: (1) memorizzare i pesi con meno bit: 16 bit = 65 536 valori, 4 bit = 16 livelli; (2) ogni peso diventa l'indice del livello più vicino, a blocchi con una scala propria; (3) livelli non uniformi, più fitti dove i pesi (circa normali) sono densi: 4-bit NormalFloat; (4) memoria circa 4 volte minore (4,5 bit effettivi con una scala a 32 bit ogni 64 pesi), piccola perdita di precisione; (5) QLoRA: modello base congelato a 4 bit, LoRA a 16 bit; 65B su una GPU da 48 GB; un 7B in 3,5 GB invece di 14 o 112.

</details>

<details><summary>Che differenza c'è fra prompting zero-shot e few-shot? Che cosa insegnano le dimostrazioni?</summary>

Traccia: (1) zero-shot: solo l'istruzione; few-shot: istruzione più alcune dimostrazioni, esempi etichettati nel prompt; (2) esempio one-shot di MMLU: una domanda con risposta C, poi la domanda vera, risposta (B), `"aab"`; (3) il compito è mostrato, non solo descritto; le dimostrazioni insegnano soprattutto formato e spazio delle risposte; anche etichette sbagliate possono aiutare (Min et al.); (4) poche: rendimenti decrescenti e rischio di adattarsi agli esempi; (5) chain-of-thought: dimostrazioni con i passi di ragionamento.

</details>

<details><summary>Che cos'è il system prompt?</summary>

Traccia: (1) prima istruzione al modello, anteposta in silenzio a qualunque testo dell'utente; (2) definisce compito o ruolo, tono, contesto (*You are a helpful and knowledgeable assistant...*); (3) può essere lungo migliaia di token grazie ai contesti lunghi (quello di Claude); (4) nel chat template ha un marcatore proprio ed è contesto senza loss; (5) costo: va elaborato a ogni conversazione; la KV cache lo evita all'interno di una conversazione.

</details>

<details><summary>Che cos'è l'in-context learning e come si confronta con il fine-tuning?</summary>

Traccia: (1) apprendimento durante il prompting senza aggiornare i pesi; (2) cambiano solo il contesto e le attivazioni; le dimostrazioni aiutano a eseguire un compito nuovo; (3) finita la conversazione si perde tutto; (4) il fine-tuning cambia i pesi, ciò che si impara resta; (5) due modi di adattare un modello: cambiare il prompt (immediato, nessun dato di training, costa token a ogni chiamata) o cambiare i pesi (dati e addestramento, reso economico da LoRA/QLoRA, effetto permanente).

</details>

<details><summary>Riassumi il percorso da base model ad assistente visto in questa lezione.</summary>

Traccia: (1) il base model continua il testo; (2) SFT con lo stesso obiettivo del pretraining, su dati diversi, loss sulla risposta, chat template; (3) dati da persone, dataset NLP con template, LLM; valutazione su cluster esclusi; (4) per farlo a basso costo LoRA ($h = xW + xAB$, frazione minima dei parametri) e QLoRA (base a 4 bit); (5) all'uso, prompting zero-shot, few-shot e system prompt, con in-context learning senza modificare i pesi; (6) prossimi passi: preferenze e RLVR.

</details>
