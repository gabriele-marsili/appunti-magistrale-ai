# L1 · Introduzione al corso

*Introduction to the course* · 23/09/2026 · Claudio Gallicchio e Andrea Ceni · lettura: J&M cap. 1

[Versione interattiva sul sito](https://gabriele-marsili.github.io/appunti-magistrale-ai/anno-2/hlt/sito/#L1) · [Indice della dispensa](README.md)

Lezione introduttiva: organizzazione del corso e dell'esame, poi una panoramica di tutto il campo. L'idea centrale è che un **language model** assegna una **distribuzione di probabilità** al token successivo e, applicato ripetutamente (**generazione autoregressiva**), produce testo. Si passa per i problemi classici dell'NLP (ambiguità, livelli di analisi, tokenizzazione, PoS tagging, parsing, NER, relazioni, topic model), la storia del campo in quattro stadi, i quattro stadi di training di un LLM (pretraining, instruction tuning, preference alignment, RLVR), l'uso via prompting, chain of thought e agenti, fino alla valutazione (accuracy, perplexity, giudici, proxy metric) e ai limiti. Quasi tutto verrà ripreso in dettaglio nelle lezioni successive: questa è la mappa del corso.

## Indice

- [Apertura](#apertura)
- [Organizzazione del corso](#organizzazione-del-corso)
- [Perché HLT](#perche-hlt)
- [Analisi linguistica](#analisi-linguistica)
- [Estrazione di informazione](#estrazione-di-informazione)
- [Modelli linguistici](#modelli-linguistici)
- [Applicazioni](#applicazioni)
- [Valutazione e limiti](#valutazione-e-limiti)
- [Studio ed esercizi](#studio-ed-esercizi)

## Apertura

<a id="p-1"></a>

### Slide 1 · Human Language Technologies: introduzione al corso

Slide di apertura del corso **Human Language Technologies** (HLT, codice 649AA, a.a. 2026-27), tenuto da Claudio Gallicchio e Andrea Ceni. L'immagine (un volto umano che si dissolve in una griglia di quadratini e poi in una rete di nodi) è la metafora di tutto il corso: il linguaggio umano trasformato in **rappresentazioni numeriche** (vettori, token) elaborate da reti neurali.

Il riferimento per questa lezione è il **capitolo 1** di Jurafsky & Martin (J&M), *Speech and Language Processing*, 3a ed. draft (agosto 2026). La lezione è una panoramica: quasi tutto quello che compare qui verrà ripreso in dettaglio nelle lezioni successive (vedi la roadmap in [scheda 21](L01-introduzione-al-corso.md#p-21)).

<a id="p-2"></a>

### Slide 2 · I language model entrano nella scoperta matematica

La lezione si apre con una notizia recente: l'**8 settembre 2026** OpenAI ha annunciato una dimostrazione generata da un sistema di AI per il problema di **Navier-Stokes**, uno dei sette **Millennium Prize Problems** del Clay Mathematics Institute. Secondo la slide la dimostrazione mostra che un fluido liscio, inizialmente in quiete, può sviluppare una **singolarità in tempo finito** (cioè le equazioni non hanno sempre soluzioni lisce globali), ed è stata **formalizzata e verificata in Lean**, un proof assistant in cui ogni passaggio è controllato meccanicamente.

Numeri riportati: circa **10.000 agenti** in parallelo, 88 ore di calcolo, 17 ore per il controllo in Lean. La figura a destra è una visualizzazione di linee di flusso di un vortice, con le etichette "inward spiral" e "axial stretching" (i meccanismi di avvitamento e stiramento lungo l'asse che concentrano la vorticità).

Perché interessa a HLT: il sistema è fatto di **language model** che generano testo (e codice Lean) e di **agenti** che usano strumenti; la verifica formale è un esempio estremo di **ricompensa verificabile** ([scheda 60](L01-introduzione-al-corso.md#p-60)).

> **Approfondimento: Contesto (facoltativo)**
>
> La notizia è di pochi giorni prima della lezione: l'annuncio di OpenAI è stato ripreso dalla stampa scientifica e, nelle settimane successive, i matematici stanno ancora esaminando la dimostrazione. Il premio Clay, per regolamento, richiede pubblicazione e un periodo di accettazione da parte della comunità, quindi non va considerato "assegnato". Per l'esame conta il senso della slide: la verifica formale in Lean rende il risultato controllabile da una macchina, indipendentemente da chi (o cosa) l'ha scritto.

<a id="p-3"></a>

### Slide 3 · Il nucleo è un language model

Messaggio chiave: il sistema della [scheda 2](L01-introduzione-al-corso.md#p-2) è, nel nucleo, un **language model**: legge e scrive **testo, token, simboli e codice**. I suoi ingredienti sono gli ingredienti del corso:

- **predire sequenze** (language modelling, capp. 3 e 7 di J&M);
- **imparare rappresentazioni** (embedding, cap. 5; reti neurali, cap. 6);
- **usare strumenti** (agenti, RAG, capp. 10-11).

Si parte dalla descrizione più semplice possibile di cosa fa un sistema del genere: **predice la parola successiva** (*next-token prediction*). J&M §1.1 definisce un language model proprio così: "a computational system that can predict the next word from previous words", cioè, dato un contesto, assegna una **distribuzione di probabilità** sulle parole possibili successive.

<a id="p-4"></a>

### Slide 4 · Completamenti possibili di una frase

Esperimento mentale: completare "A bottle of \_\_\_ is on the table." Candidati: *water*, *wine*, *glass*, *patience*. Tutti sono grammaticali, ma non sono ugualmente plausibili: *water* e *wine* sono molto probabili, *glass* è possibile (una bottiglia di vetro, detto in modo un po' strano), *patience* è quasi assurdo (ha senso solo in senso figurato).

Il punto è che per predire bene servono **conoscenze** di vario tipo: di lingua (dopo "of" viene un nome), di mondo (le bottiglie contengono liquidi), di uso (espressioni frequenti). J&M §1.2 insiste proprio su questo: imparando a predire le parole, un modello è costretto ad acquisire conoscenze lessicali, fattuali e perfino matematiche (es. "The square root of 4 is [2]"). È il gioco di Shannon (*Shannon game*): indovinare la parola successiva, una alla volta.

Nota: i colori dei candidati anticipano la [distribuzione della scheda 5](L01-introduzione-al-corso.md#p-5); *patience* è in rosso, il meno probabile.

<a id="p-5"></a>

### Slide 5 · Un modello restituisce una distribuzione

Il modello non sceglie "una" parola: restituisce una **distribuzione di probabilità** sul vocabolario, condizionata al contesto "A bottle of ...". Nella slide: water 0.42, wine 0.31, glass 0.09, patience 0.03, *other* 0.15 (la massa di tutte le altre parole del vocabolario, raggruppata). Le barre sono proporzionali alle probabilità.

Controllo: $0.42+0.31+0.09+0.03+0.15 = 1.00$, come indicato ("sum = 1.00"). Deve essere così perché gli eventi "la prossima parola è $w$" sono **mutuamente esclusivi ed esaustivi**: esattamente una parola viene dopo.

In simboli: $P(w \mid \text{A bottle of})\ge 0$ e $\sum_{w\in V} P(w\mid \text{contesto}) = 1$. Da una distribuzione si può: prendere la parola più probabile (**greedy**, qui *water*) oppure **campionare** (J&M §1.1: "generating a random number and choosing the word according to its probability"), così ogni tanto esce *wine* o anche *patience*.

> **Da saper fare: Perché la distribuzione somma a 1 (e il softmax)**
>
> Una rete neurale produce per ogni token del vocabolario un numero reale qualsiasi, lo **score** o *logit* $z_w$. Per trasformarli in probabilità si usa il **softmax** (lo vedremo nei capp. 4 e 7):
>
> $$P(w\mid \text{contesto}) = \frac{e^{z_w}}{\sum_{v\in V} e^{z_v}}$$
>
> Ogni termine è positivo (esponenziale) e dividendo per la somma il totale è 1 per costruzione. Esempio con tre parole e logit $(2,1,0)$: $e^2=7.389$, $e^1=2.718$, $e^0=1$, somma $11.107$, probabilità $(0.665, 0.245, 0.090)$.
>
> Da ricordare: il softmax conserva l'ordine e dipende solo dalle *differenze* fra logit. Nella slide, il rapporto water/wine è $0.42/0.31\approx1.35$, quindi i due logit differiscono di $\ln 1.35\approx0.30$.

<a id="p-6"></a>

### Slide 6 · Generazione autoregressiva

La figura mostra il ciclo di **generazione autoregressiva**: una sequenza di token (quadratini colorati) entra nella rete (strati di neuroni), che produce una distribuzione sul vocabolario (istogramma orizzontale); si sceglie un token (quello evidenziato in rosso), lo si **appende** al contesto (freccia che torna indietro: la sequenza ora ha un quadratino rosso in più) e si ripete.

Così una predizione "a un passo" diventa un generatore di sequenze. J&M §1.1 (Fig. 1.3): "So long and thanks for" → *all* → "So long and thanks for all" → *the* → ... Il modello condiziona sia sul prompt sia sui token che ha generato lui stesso. Questi modelli si chiamano **causali** o **autoregressivi** (left-to-right).

Formalmente la probabilità di una sequenza si fattorizza con la **regola della catena**:

$$P(w_1,\dots,w_n)=\prod_{i=1}^{n}P(w_i\mid w_1,\dots,w_{i-1})$$

La generazione si ferma quando il modello produce un token speciale di fine (end-of-response, J&M §1.7.1).

> **Da saper fare: Probabilità di una frase con la regola della catena**
>
> La regola della catena è una identità della probabilità (nessuna approssimazione): $P(A,B,C)=P(A)\,P(B\mid A)\,P(C\mid A,B)$. Esempio: se $P(\text{A})=0.1$, $P(\text{bottle}\mid\text{A})=0.02$, $P(\text{of}\mid\text{A bottle})=0.6$, $P(\text{water}\mid\text{A bottle of})=0.42$, allora
>
> $$P(\text{A bottle of water}) = 0.1\cdot0.02\cdot0.6\cdot0.42 = 5.04\times10^{-4}.$$
>
> Il prodotto diventa piccolissimo per frasi lunghe: per questo si lavora con i **logaritmi** (somme di log-probabilità) e con misure normalizzate per la lunghezza come la perplexity ([scheda 70](L01-introduzione-al-corso.md#p-70)). Gli n-gram (cap. 3) approssimano ogni fattore guardando solo le ultime $n-1$ parole.

<a id="p-7"></a>

### Slide 7 · Predire il prossimo token, su testo enorme

Slide-slogan: "Predict the next token, repeated over enormous amounts of text. Over and over." È la descrizione del **pretraining** ([scheda 57](L01-introduzione-al-corso.md#p-57)): il modello legge miliardi (oggi trilioni) di token e a ogni posizione cerca di predire il token successivo; quando sbaglia, i pesi vengono aggiornati per rendere più probabile il token corretto.

Due osservazioni:

- si parla di **token**, non di parole: un token è una parola o un pezzo di parola (J&M §1.1; tokenizzazione e BPE nella prossima lezione, cap. 2);
- il compito è **auto-supervisionato**: le "etichette" sono il testo stesso (il token successivo), quindi non serve annotazione umana e si può scalare a quantità enormi di dati.

J&M §1.1 aggiunge che le prestazioni dipendono da tre fattori: numero di parametri, numero di token di training e compute (le **scaling laws**).

> **Approfondimento: Scaling laws (J&M §1.1, facoltativo)**
>
> Hoffmann et al. (2022) hanno mostrato che, a budget di calcolo $C$ fissato, il numero ottimo di parametri $N$ e di token $D$ crescono entrambi circa come $C^{1/2}$: $N_{opt}\propto C^{1/2}$, $D_{opt}\propto C^{1/2}$. Esempio di scala citato dal libro: Llama 3.1 405B ha 405 miliardi di parametri ed è addestrato su oltre 15 trilioni di token.

<a id="p-8"></a>

### Slide 8 · Language model su larga scala

Tre indicatori della diffusione:

- **Grafico a barre**: percentuale di organizzazioni che usano l'AI in almeno una funzione aziendale (sondaggi McKinsey): 2017 20%, 2018 47%, 2019 58%, 2020 50%, 2021 56%, 2022 50%, 2023 55%, 2024 78%, 2025 88%. Le ultime due barre sono in colore più chiaro: il salto dopo l'arrivo dell'AI generativa è evidente (da circa metà delle aziende a quasi 9 su 10).
- **ChatGPT**: da 100 milioni di utenti attivi settimanali (novembre 2023) a 900 milioni (febbraio 2026).
- **Investimenti privati USA in AI**: da 109 a 286 miliardi di dollari fra 2024 e 2025 (tutta l'AI, non solo LLM).

Le cifre 2017-2024 corrispondono a quelle raccolte nello Stanford AI Index 2025 (78% nel 2024; 109,1 miliardi di investimenti nel 2024); l'88% del 2025 è il dato del sondaggio McKinsey 2025. Non serve impararle a memoria: il messaggio è che HLT è oggi una tecnologia industriale di massa.

<a id="p-9"></a>

### Slide 9 · Un language model da solo non è un prodotto

Frase chiave: "A language model *alone* is *not* a product." Per ottenere un **sistema** che funziona servono anche:

- **dati** (raccolta, pulizia, filtri di qualità e sicurezza, J&M §1.6.1);
- **rappresentazioni** (tokenizzazione, embedding);
- **valutazione** (benchmark, metriche, analisi degli errori, [scheda 70](L01-introduzione-al-corso.md#p-70));
- **retrieval** (recuperare documenti pertinenti, RAG, cap. 11);
- **strumenti** (agenti che chiamano programmi, [scheda 68](L01-introduzione-al-corso.md#p-68));
- **verifica** (controllare le uscite, come la verifica in Lean della [scheda 2](L01-introduzione-al-corso.md#p-2)).

È anche la giustificazione del programma: non si studia solo "il modello", ma la catena completa che lo trasforma in qualcosa di utile e affidabile. Tienilo a mente per il progetto: un buon progetto ha dati, baseline e valutazione, non solo un modello.

<a id="p-10"></a>

### Slide 10 · Indice della lezione

Le sette parti della lezione: **organizzazione del corso** ([scheda 11](L01-introduzione-al-corso.md#p-11)), **perché HLT** ([scheda 30](L01-introduzione-al-corso.md#p-30)), **analisi linguistica** ([scheda 37](L01-introduzione-al-corso.md#p-37)), **estrazione di informazione** ([scheda 45](L01-introduzione-al-corso.md#p-45)), **language model** ([scheda 50](L01-introduzione-al-corso.md#p-50)), **applicazioni** ([scheda 64](L01-introduzione-al-corso.md#p-64)), **valutazione e limiti** ([scheda 69](L01-introduzione-al-corso.md#p-69)).

Logica del percorso: si parte dai problemi "classici" dell'NLP (analizzare il testo: token, sintassi, entità) e si arriva al paradigma attuale (generare testo con un LLM e usarlo per tutto), chiudendo con come si misura un sistema e cosa ancora non funziona.

## Organizzazione del corso

<a id="p-11"></a>
**Slide 11 · Organizzazione del corso** — Informazioni pratiche: orari, docenti, contatti, materiale, esame.

<a id="p-12"></a>

### Slide 12 · Informazioni sul corso

**Human Language Technologies**, codice **649AA**, **9 CFU**, primo semestre, laurea magistrale in Computer Science (il corso è seguito anche da AI).

Da ricordare: alcune date e la distribuzione finale degli argomenti **possono cambiare**; gli aggiornamenti passano dal gruppo Teams ([scheda 18](L01-introduzione-al-corso.md#p-18)).

<a id="p-13"></a>

### Slide 13 · Dove e quando

Prima lezione: **mercoledì 23 settembre 2026**. Orario settimanale:

| Giorno | Ora | Aula |
| --- | --- | --- |
| Martedì | 11:00-13:00 | Fib C |
| Mercoledì | 14:00-16:00 | Fib C1 |
| Giovedì | 14:00-16:00 | Fib E |

Attenzione: aule diverse nei tre giorni (tutte nel polo Fibonacci).

<a id="p-14"></a>

### Slide 14 · Dove e quando: orario completo

Screenshot dell'orario ufficiale "orario LM-WIF" della settimana 21-25 settembre 2026 (colonne lun 21/9 ... ven 25/9, righe dalle 9 alle 18), con tutti i corsi della magistrale in blocchi colorati. Il testo è troppo piccolo per essere letto in dettaglio; serve solo a collocare HLT fra gli altri corsi. Per l'orario di HLT vale la tabella della [scheda 13](L01-introduzione-al-corso.md#p-13). Utile controllare sovrapposizioni con gli altri esami a scelta.

<a id="p-15"></a>

### Slide 15 · Docenti: Andrea Ceni

**Andrea Ceni**, ricercatore (Assistant Professor), andrea.ceni@unipi.it. Competenze: sistemi dinamici neurali, reti ricorrenti, *reservoir computing*, deep learning per sequenze. Insegna anche Laboratorio I e Computational Neuroscience.

Ricevimento **su appuntamento**, scrivendo per email. Le sue competenze sono legate alla parte del corso su modelli ricorrenti, SSM e Mamba (cap. 14, [scheda 21](L01-introduzione-al-corso.md#p-21)).

<a id="p-16"></a>

### Slide 16 · Docenti: Claudio Gallicchio

**Claudio Gallicchio**, professore associato, claudio.gallicchio@unipi.it. Competenze: machine e deep learning, reti ricorrenti, reservoir computing, dinamiche neurali, AI neuromorfica. Insegna anche Computational Neuroscience, Introduzione all'IA e Algoritmica.

Ricevimento **su appuntamento**, nell'ufficio 358N o online: si prenota uno slot libero tramite il link "Book an appointment" o il QR code sulla slide.

<a id="p-17"></a>

### Slide 17 · Come contattare i docenti

Regole per scrivere:

- **Oggetto**: `[HLT 2026]` + argomento specifico;
- **Corpo**: contesto, domanda, cosa hai già provato;
- **Canale**: Teams per domande utili a tutti, email per questioni personali.

Cosa fare: usare sempre il tag nell'oggetto (così la mail non si perde) e mettere nel messaggio quello che hai già tentato.

<a id="p-18"></a>

### Slide 18 · Gruppo Teams

Il team **"Teams HLT 2026-27"** (link e QR code sulla slide) è il canale ufficiale per: materiale delle lezioni e **notebook**, cambi di orario e **scadenze**, domande sul corso.

Cosa fare: iscriversi subito e attivare le notifiche, perché gli avvisi su date e progetto passano da lì.

<a id="p-19"></a>

### Slide 19 · Lista studenti e gruppi

Due passi, tramite il QR code della slide:

- **ora**: indicare corso di laurea ed email di contatto nella lista studenti;
- **più avanti**: formare i **gruppi di progetto**, dopo la pubblicazione del project brief.

Cosa fare: compilare la lista adesso; cominciare a pensare con chi fare il progetto (serve solo per chi frequenta, [scheda 27](L01-introduzione-al-corso.md#p-27)).

<a id="p-20"></a>

### Slide 20 · Obiettivi del corso

Tre obiettivi:

- **Modelli**: modelli statistici e neurali per problemi linguistici (dagli n-gram ai transformer);
- **Implementazione**: pipeline HLT in Python, dall'elaborazione del testo ai transformer;
- **Valutazione**: dataset, **baseline**, metriche e analisi degli errori del modello.

La terza voce è quella che spesso si trascura: all'esame e nel progetto conta saper dire *quanto* e *perché* un modello funziona, confrontandolo con una baseline semplice.

<a id="p-21"></a>

### Slide 21 · Roadmap del corso

Sei blocchi, ciascuno con i capitoli di J&M:

| Blocco | Contenuti | Capitoli |
| --- | --- | --- |
| Foundations | token, n-gram, classificazione, tagging | 2-4, 18 |
| Representations | embedding e reti neurali | 5-6 |
| Transformers | attention, decoding, pretraining | 7 |
| Adaptation | post-training, masked LM | 8-9 |
| Using LLMs | retrieval, RAG, interpretabilità | 10-11 |
| Recurrent models | RNN, LSTM, SSM, Mamba | 14 + articoli |

Collegamenti con questa lezione: tokenizzazione ([scheda 40](L01-introduzione-al-corso.md#p-40)) → cap. 2; perplexity ([scheda 70](L01-introduzione-al-corso.md#p-70)) → cap. 3; PoS tagging ([scheda 41](L01-introduzione-al-corso.md#p-41)) → cap. 18; pretraining ([scheda 57](L01-introduzione-al-corso.md#p-57)) → cap. 7; instruction tuning e allineamento ([scheda 58](L01-introduzione-al-corso.md#p-58)-[60](L01-introduzione-al-corso.md#p-60)) → cap. 8; agenti e RAG ([scheda 63](L01-introduzione-al-corso.md#p-63)) → capp. 10-11. Il coniglio bianco con l'orologio (Alice) ricorda che il programma è fitto.

<a id="p-22"></a>

### Slide 22 · Laboratori, seminari e progetti

**Laboratori** (notebook Python):

- NLTK e spaCy: testo, PoS/NER, sentiment;
- word embedding e word2vec;
- n-gram e **nanoGPT** addestrato su Shakespeare;
- Hugging Face: ispezione dell'attention e fine-tuning.

**Seminari e progetti**: language diffusion model, AI agentica (tool use, pianificazione, valutazione), ragionamento ricorrente e *looped transformer*, presentazioni dei progetti dei gruppi.

I laboratori sono il lato pratico delle schede di questa lezione: PoS e NER ([scheda 42](L01-introduzione-al-corso.md#p-42), [scheda 47](L01-introduzione-al-corso.md#p-47)) si provano subito con spaCy.

<a id="p-23"></a>

### Slide 23 · Corsi collegati

Corsi da cui HLT attinge: **654AA Machine Learning** (metodi di apprendimento usati ovunque), **646AA Computational Mathematics** (analisi e algebra lineare), **269AA Probability and Statistics** (ragionamento probabilistico), **289AA Information Retrieval** (indicizzazione, ranking, ricerca; utile per RAG).

Se qualcosa di questi corsi è arrugginito, ripassarlo ora conviene più che rincorrerlo dopo.

<a id="p-24"></a>

### Slide 24 · Prerequisiti

Quattro aree:

- **Python**: funzioni, collezioni, file, array numerici (numpy);
- **algebra lineare**: vettori, matrici, prodotto scalare (servono per embedding e attention);
- **probabilità**: distribuzioni, probabilità condizionata, valore atteso (servono già da questa lezione: [scheda 5](L01-introduzione-al-corso.md#p-5), [scheda 6](L01-introduzione-al-corso.md#p-6));
- **machine learning**: loss, ottimizzazione, split train/test, generalizzazione.

Autoverifica rapida: se sai scrivere $P(A,B)=P(A)P(B\mid A)$ e calcolare un prodotto scalare a mano, sei a posto per le prime settimane.

<a id="p-25"></a>

### Slide 25 · Libri e risorse

Testo principale: **Jurafsky & Martin**, *Speech and Language Processing*, draft 2026. Altri testi: Alammar & Grootendorst, *Hands-on Large Language Models* (LLM in pratica); Bird, Klein & Loper, *Natural Language Processing with Python* (NLTK); Goodfellow, Bengio & Courville, *Deep Learning*; S. J. D. Prince, *Understanding Deep Learning*.

Per l'esame il riferimento è J&M; gli altri servono per il progetto e per approfondire la parte neurale.

<a id="p-26"></a>

### Slide 26 · Riferimento per questa lezione

J&M, 3a ed. draft del 19 agosto 2026, **capitolo 1 (Introduction)**, da leggere tutto. Sezioni evidenziate:

- §1.1-1.4: language model, predizione, breve storia;
- §1.6-1.8: training, inference, agenti;
- §1.9-1.10: valutazione, sicurezza e limiti.

Il sito del libro è web.stanford.edu/~jurafsky/slp3/. Nota: §1.5 (struttura linguistica e interpretabilità) e §1.11 (antropomorfismo) non sono nell'elenco ma sono brevi e utili (la seconda è ripresa in [scheda 71](L01-introduzione-al-corso.md#p-71)).

<a id="p-27"></a>

### Slide 27 · Modalità d'esame: frequentanti

Per i **frequentanti** l'esame ha tre componenti:

- **progetto di gruppo**;
- **presentazione, codice e relazione** del progetto;
- **prova scritta a libro chiuso**.

Vincolo importante: questa modalità è disponibile **solo nella sessione invernale**. Dopo si passa alla modalità non frequentanti ([scheda 29](L01-introduzione-al-corso.md#p-29)).

<a id="p-28"></a>

### Slide 28 · HLT poster session

L'ultimo giorno del corso (dicembre 2026, data da confermare) è un **workshop a poster**: un poster per gruppo, breve pitch e poi discussione con docenti, compagni e ospiti. Le foto sono della sessione di giugno 2025.

Il poster deve coprire: **problema e dati**, **metodo e baseline**, **risultati e limiti onesti**, **cosa si è imparato**. È la stessa struttura della valutazione vista nella [scheda 20](L01-introduzione-al-corso.md#p-20): conviene progettare il lavoro pensando già a questi quattro blocchi.

<a id="p-29"></a>

### Slide 29 · Modalità d'esame: non frequentanti

Per i **non frequentanti**: **nessun progetto**, una prova scritta a libro chiuso **più ampia** (la parola "Broader" è sottolineata: il programma coperto è più esteso) e un **esame orale**.

Le domande tipo orale nella sezione Studio di questi appunti servono per entrambe le modalità.

## Perché HLT

<a id="p-30"></a>
**Slide 30 · Perché HLT?** — Il linguaggio come problema di calcolo.

<a id="p-31"></a>

### Slide 31 · Motivazione

Tre ragioni per studiare HLT:

- **Text at scale**: l'informazione utile (web, articoli, documenti aziendali, cartelle cliniche) è più grande di quanto una persona possa leggere; serve elaborarla automaticamente.
- **Language as interface**: sempre più spesso le persone danno istruzioni al software in linguaggio naturale invece che con menu o codice (vedi [scheda 68](L01-introduzione-al-corso.md#p-68)).
- **Many tasks**: ricerca, estrazione, classificazione, traduzione, generazione. Molti problemi diversi hanno il testo come input o output.

J&M (introduzione al cap. 1) elenca benefici concreti: produttività nella scrittura e nel codice, traduzione che abbatte barriere linguistiche, riconoscimento del parlato, accesso all'informazione e all'istruzione, supporto alla ricerca scientifica.

<a id="p-32"></a>

### Slide 32 · Perché il linguaggio?

Il linguaggio è una **capacità distintiva umana**: sostiene cooperazione, astrazione, memoria e cultura. Per l'informatica la sfida non è riprodurre la mente, ma **modellare il comportamento linguistico osservabile**: dati input testuali, produrre output testuali (o decisioni) appropriati.

Questa formulazione "comportamentale" è importante: un language model è valutato su quello che produce, non su cosa "capisce". Si ricollega all'avvertenza sulla terminologia antropomorfa ([scheda 71](L01-introduzione-al-corso.md#p-71)). J&M apre il capitolo ricordando che l'idea di artefatti che parlano è antichissima (Pigmalione, Frankenstein, il Mosè di Michelangelo): il linguaggio è percepito come "il segno dell'umanità".

<a id="p-33"></a>

### Slide 33 · Dati strutturati e non strutturati

Confronto:

| Dati strutturati | Dati linguistici |
| --- | --- |
| righe, campi, tipi | contesto, variazione, ambiguità |
| schema noto in anticipo | la struttura utile è implicita |
| le query puntano a campi espliciti | il significato dipende da più di un nome di campo |

Esempio: in un database "data\_assunzione = 2026-07" è una query banale; nel testo "Mira joined Acme in Pisa in July" la stessa informazione va **estratta** (chi, dove, quando) e non c'è uno schema che dica dove si trova. Gran parte dell'NLP classico ([scheda 46](L01-introduzione-al-corso.md#p-46)) serve proprio a trasformare testo non strutturato in dati strutturati. La difficoltà principale è l'**ambiguità**, nelle due schede che seguono.

<a id="p-34"></a>

### Slide 34 · Ambiguità lessicale: bank

**Ambiguità lessicale**: la stessa forma scritta ha significati diversi. *bank* in "He deposited cash at the bank" è la **banca** (istituto finanziario); in "He sat on the bank of the river" è la **riva**. Le due illustrazioni mostrano uno sportello bancario e una persona seduta sulla riva di un fiume.

A disambiguare è il **contesto**: "deposited cash" contro "of the river". Il compito si chiama **word sense disambiguation** (WSD, presente anche nella linea del tempo di [scheda 51](L01-introduzione-al-corso.md#p-51)). È anche l'intuizione dell'**ipotesi distribuzionale** (J&M §1.2, cap. 5): il significato di una parola si ricava dalle parole che le stanno intorno. Gli embedding contestuali dei transformer (cap. 7) daranno a *bank* vettori diversi nelle due frasi.

<a id="p-35"></a>

### Slide 35 · Una frase, due letture

**Ambiguità strutturale** (sintattica): "I saw the student with the telescope." Le parole sono le stesse ma la struttura cambia. Figura a sinistra: io guardo attraverso un telescopio (il telescopio è lo **strumento** del vedere); a destra: lo studente porta un telescopio sotto il braccio (il telescopio è una **proprietà** dello studente).

È un caso di **PP-attachment**: il sintagma preposizionale "with the telescope" può attaccarsi al verbo *saw* o al nome *student*. Nessuna delle due letture è sbagliata; solo il contesto più ampio (o il buon senso) decide. Il parsing ([scheda 43](L01-introduzione-al-corso.md#p-43)) deve scegliere un albero.

> **Da saper fare: Disegnare le due letture come alberi**
>
> Alberi a costituenti (semplificati):
>
> ```
> Lettura 1 (strumento):            Lettura 2 (lo studente ha il telescopio):
> [S [NP I]                         [S [NP I]
>    [VP [V saw]                       [VP [V saw]
>        [NP the student]                  [NP [NP the student]
>        [PP with the telescope]]]             [PP with the telescope]]]]
> ```
>
> In dipendenze (Universal Dependencies): lettura 1, *telescope* dipende da *saw* con relazione `obl` (oblique); lettura 2, *telescope* dipende da *student* con relazione `nmod`. In entrambi i casi *with* è `case` di *telescope*, *I* è `nsubj` e *student* è `obj` di *saw*. Cambia solo un arco: la testa di *telescope*.

<a id="p-36"></a>

### Slide 36 · Un approccio algoritmico

Modello mentale di ogni sistema HLT, come catena:

**Language** (input) → **Represent** → **Learn** → **Infer** → **Evaluate** → **decisione o testo** (output). I tre passi centrali sono etichettati "model + data".

- **Represent**: trasformare il testo in qualcosa di calcolabile (token, indici, vettori/embedding);
- **Learn**: stimare una funzione dai dati (conteggi per gli n-gram, gradient descent per le reti);
- **Infer**: applicare il modello a un input nuovo (classificare, generare);
- **Evaluate**: confrontare l'uscita con un riferimento (accuracy, perplexity, giudici).

"Ogni freccia nasconde scelte di progetto, e un sistema può fallire in ognuna": una tokenizzazione sbagliata o un test set contaminato rovinano tutto il resto. Questo schema è la **pipeline HLT** che rivedremo in ogni lezione.

## Analisi linguistica

<a id="p-37"></a>
**Slide 37 · Analisi linguistica** — Token, sintassi e significato: come l'NLP classico descrive una frase.

<a id="p-38"></a>

### Slide 38 · Analisi linguistica a più livelli

La stessa frase si può descrivere a più **livelli di analisi**: token, morfologia, sintassi, semantica, discorso. Ogni livello dà una descrizione diversa dello stesso oggetto.

Una **pipeline classica** calcola i livelli uno dopo l'altro (prima tokenizzo, poi assegno le PoS, poi faccio il parsing, poi estraggo entità e relazioni), e ogni stadio usa l'uscita del precedente. Conseguenza: **un errore a un livello si propaga al successivo** (*error propagation*). Se la tokenizzazione spezza male "New York", il tagger e il NER sbagliano di conseguenza.

Oggi, dice J&M §1.5, calcolare esplicitamente queste strutture non è più il passo obbligato per "capire" il testo (un LLM va dal testo alla risposta direttamente), ma resta fondamentale per l'**interpretabilità** (si è visto che gli embedding codificano implicitamente alberi sintattici e coreferenza), per le applicazioni alle scienze sociali e cognitive, e per compiti leggeri dove un LLM è sprecato.

<a id="p-39"></a>

### Slide 39 · Livelli di analisi linguistica

Esempio unico: "The document continues with other sentences."

| Livello | Cosa fa | Esempio |
| --- | --- | --- |
| **Token** | identifica le unità | The | document | continues | ... |
| **Morfologia** | struttura interna delle parole | continue + -s |
| **Sintassi** | relazioni grammaticali | soggetto → verbo → sintagma preposizionale |
| **Semantica** | significato | continue(the document, other sentences) |
| **Discorso** | legami fra frasi e riferimenti | "other" rimanda oltre questa frase |

Note: il suffisso *-s* di *continues* è morfologia flessiva (3a persona singolare presente). La rappresentazione semantica è in forma predicato-argomenti: il predicato *continue* con due argomenti. Il livello del discorso nota che "other sentences" presuppone frasi già viste o ancora da venire: il senso completo richiede il testo intorno (come la **coreferenza**, J&M §1.5).

<a id="p-40"></a>

### Slide 40 · Convenzioni di tokenizzazione

La **tokenizzazione** divide il testo in unità, ma i confini dipendono dalla convenzione. Esempio: "New York-based startup".

- **Whitespace** (spazi): `New` `York-based` `startup`, 3 token;
- **Punteggiatura separata**: `New` `York` `-` `based` `startup`, 5 token;
- **Elisione italiana**: *l'acqua* si può tenere unito (`l'acqua`) o dividere in `l'` `acqua`.

Nessuna delle due prime scelte è perfetta: con gli spazi, "York-based" è un'unità che mescola un nome proprio e un suffisso aggettivale; separando la punteggiatura, si recupera "York" ma "New York" resta comunque spezzato in due token (è un'entità unica, un *multi-word expression*). Per l'italiano, dividere *l'* permette di riconoscere che *acqua* è la stessa parola di "un'acqua" o "acqua".

Anticipazione (lezione 2, cap. 2): i LLM usano **tokenizzazione a subword** (BPE), che non segue queste convenzioni linguistiche ma statistiche di frequenza.

<a id="p-41"></a>

### Slide 41 · Part-of-speech tagging

Il **PoS tagging** assegna a ogni token una **classe grammaticale** (nome, verbo, aggettivo...) usando il **contesto**. Serve il contesto perché la stessa forma può avere tag diversi: *document* è **nome** in "the document continues" e **verbo** in "document the process". Anche in italiano: "porta" nome ("la porta") o verbo ("porta il libro").

È il caso più semplice di **sequence labelling**: una etichetta per token, input e output hanno la stessa lunghezza. Lo stesso schema servirà per il **NER** ([scheda 47](L01-introduzione-al-corso.md#p-47)), dove si etichettano i token come inizio/interno/fuori da un'entità (schema BIO, cap. 18).

Nel corso: tagging con HMM e modelli neurali nel cap. 18; in laboratorio con NLTK e spaCy.

<a id="p-42"></a>

### Slide 42 · PoS tagging: esempio con UPOS

"The document continues with other sentences." con i tag **UPOS** (Universal Dependencies):

| Token | The | document | continues | with | other | sentences | . |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Tag | DET | NOUN | VERB | ADP | ADJ | NOUN | PUNCT |

Legenda: DET determinante (articolo), NOUN nome comune, VERB verbo principale, ADP adposizione (preposizione o postposizione), ADJ aggettivo, PUNCT punteggiatura. Il tagset UPOS ha 17 tag in tutto ed è lo stesso per tutte le lingue: altri tag frequenti sono PROPN (nome proprio), PRON, AUX (ausiliare), ADV, CCONJ, NUM.

Nota: la frase contiene 6 parole ma 7 token, perché il punto finale è un token a sé.

> **Da saper fare: Casi tipici all'orale**
>
> - *with* è **ADP**, non "PREP": UPOS usa il termine generale adposizione.
> - i verbi ausiliari (*is* in "is running", *ha* in "ha mangiato") sono **AUX**, non VERB.
> - nomi propri come *Pisa*, *Mira*, e i nomi dei mesi in inglese (*July*) sono **PROPN**.

<a id="p-43"></a>

### Slide 43 · Parsing

Il **parsing** descrive come le parole di una frase sono collegate. L'uscita non è un'etichetta per token ma un **albero**: per ogni parola una **testa** (head), i suoi **dipendenti**, e la **relazione grammaticale** sull'arco (soggetto, oggetto, modificatore...). Questo è il **dependency parsing**; l'alternativa è il parsing a costituenti (sintagmi annidati, NP, VP, PP).

Gli errori di parsing si propagano ai compiti a valle, come l'**estrazione di relazioni** e il **question answering**: se "with the telescope" è attaccato alla parola sbagliata ([scheda 35](L01-introduzione-al-corso.md#p-35)), si estrae il fatto sbagliato (chi ha il telescopio).

J&M §1.5 lo cita come "one of the oldest tasks in NLP", con l'esempio "She announced this in January" (nsubj, dobj). Oggi il parsing esplicito è usato anche per analizzare cosa hanno imparato i LLM: alcune teste di attention seguono proprio gli archi di dipendenza.

<a id="p-44"></a>

### Slide 44 · Parsing: esempio di albero a dipendenze

Albero di "The document continues with other sentences.":

- radice: **continues** (il verbo principale);
- continues → document: **subject** (nsubj);
- continues → sentences: **oblique** (obl, complemento introdotto da preposizione);
- document → The: **determiner** (det);
- sentences → with: **case** (la preposizione è marcatore di caso del nome);
- sentences → other: **modifier** (amod, modificatore aggettivale).

Due punti tipici delle Universal Dependencies: (1) la preposizione *with* non è la testa del sintagma, ma dipende dal nome *sentences*; (2) le teste sono le parole di contenuto. Il punto finale (punct, dipendente da *continues*) non è disegnato. Ogni parola ha esattamente una testa, tranne la radice: 6 parole, 5 archi.

## Estrazione di informazione

<a id="p-45"></a>
**Slide 45 · Estrazione di informazione** — Entità, relazioni e topic: dal testo libero a dati strutturati.

<a id="p-46"></a>

### Slide 46 · Compiti tradizionali di information extraction

L'**information extraction** (IE) trasforma il testo in dati strutturati, per stadi:

**Text** (documenti grezzi) → **Mentions** (termini e nomi) → **Entities** (persone, luoghi, organizzazioni) → **Relations** (chi ha fatto cosa a chi) → **Events** (partecipanti, tempo, luogo).

Ogni passo produce un oggetto più strutturato. La differenza fra *mention* ed *entity*: "Victoria Chen", "the CFO", "her" sono tre menzioni della stessa entità (è la **coreferenza**, J&M §1.5). Gli **eventi** generalizzano le relazioni: un evento "assunzione" ha più ruoli (chi, dove, quando).

Come per l'analisi linguistica ([scheda 38](L01-introduzione-al-corso.md#p-38)), gli errori iniziali si ereditano: una menzione mancata non potrà mai comparire in una relazione.

<a id="p-47"></a>

### Slide 47 · Named entity recognition

Il **NER** trova le menzioni di entità con nome e ne assegna il tipo. In "Mira joined Acme in Pisa in July.": **Mira** PERSON, **Acme** ORGANIZATION, **Pisa** LOCATION, **July** DATE.

Per ogni menzione ci sono **due decisioni**: dove inizia e finisce lo **span** (es. "New York" è un'unica entità di due token) e di che **tipo** è. Per questo il NER si riduce a sequence labelling ([scheda 41](L01-introduzione-al-corso.md#p-41)) con tag **BIO**: `B-LOC` per il primo token, `I-LOC` per quelli interni, `O` fuori. Es. New/B-LOC York/I-LOC.

L'inventario dei tipi dipende dall'applicazione: un sistema biomedico vuole proteine e malattie, uno legale leggi e tribunali. Nota che DATE non è un "nome proprio" in senso stretto; molti schemi (es. OntoNotes) includono anche date, quantità, valute.

<a id="p-48"></a>

### Slide 48 · Relazioni fra entità

Sulla stessa frase, le entità diventano **nodi** e le relazioni **archi tipati e orientati**:

- Mira (PERSON) → **WORKS\_FOR** → Acme (ORGANIZATION);
- Acme → **LOCATED\_IN** → Pisa (LOCATION);
- Mira → **START\_DATE** → July (DATE).

Il risultato è un piccolo **knowledge graph** estratto da una frase. Le relazioni sono in forma di triple (soggetto, relazione, oggetto), es. (Mira, WORKS\_FOR, Acme). I tipi di relazione li decide l'applicazione, e un buon estrattore conserva la **provenienza** (la frase da cui viene ogni arco), per poterlo verificare.

Nota di interpretazione: "joined" esprime un *evento* (l'assunzione) con più partecipanti; le triple lo spezzano in relazioni binarie, perdendo un po' di informazione (July è la data di inizio del rapporto Mira-Acme, non una proprietà di Mira in sé; e "in Pisa" potrebbe indicare la sede dove Mira lavora più che la sede unica di Acme). È il motivo per cui la catena di [scheda 46](L01-introduzione-al-corso.md#p-46) termina con gli **eventi**.

<a id="p-49"></a>

### Slide 49 · Topic modelling

Un **topic** è una **distribuzione sulle parole**, appresa da una collezione di documenti **senza etichette** (apprendimento non supervisionato). Nella slide:

- Topic 1: network, training, layer, data;
- Topic 2: election, vote, party, policy;
- Topic 3: patient, treatment, clinical, risk.

Un documento è una **miscela di topic**: qui 0.10, 0.25, 0.65 (somma 1.00), quindi il documento parla soprattutto del topic 3. I nomi "machine learning", "politica", "medicina" **non** li dà il modello: li dà una persona dopo, leggendo le parole più probabili di ogni topic.

Il modello classico è **LDA** (Latent Dirichlet Allocation). La probabilità di una parola in un documento è una media pesata: $P(w\mid d)=\sum_k \theta_{d,k}\,\phi_k(w)$, con $\theta_d$ la miscela del documento e $\phi_k$ la distribuzione del topic $k$. Collegamento con [scheda 5](L01-introduzione-al-corso.md#p-5): anche qui tutto è distribuzioni che sommano a 1.

## Modelli linguistici

<a id="p-50"></a>
**Slide 50 · Language model** — Breve storia, pretraining e come si usano i modelli.

<a id="p-51"></a>

### Slide 51 · Breve storia dell'NLP: quattro stadi (panoramica)

Linea del tempo 1950-2020+ (figura 1.6 di J&M) divisa in quattro periodi da linee tratteggiate:

1. **Statistical and Neural Foundations** (anni '50): Shannon, Joos, Osgood, Rosenblatt (perceptron);
2. **The Symbolic Turn** (circa 1965-inizio anni '90): Miller & Chomsky, Minsky & Papert, CKY, Prolog, SHRDLU, Schank & Abelson, Grosz & Sidner, FST, WordNet, WSD, tf-idf;
3. **The Revival of Empiricism** (dal 1975/1988 al 2017): HMM, backprop, LSA e word embedding, statistical MT, TDNN di Waibel, SRL, probabilistic parsing, Maxent, neural language model di Bengio et al., CTC, semantic parsing, multitask learning, word2vec, attention, embedding bias, transformer, BERT;
4. **LLMs** (dal 2019-2020): GPT-3, RLHF, RAG, ReAct, RLVR.

La linea tratteggiata obliqua fra anni '70 e '90 indica che il ritorno all'empirismo è graduale: prima nel parlato (HMM, IBM), poi nel testo. Le quattro schede successive evidenziano un periodo alla volta.

<a id="p-52"></a>

### Slide 52 · Stadio 1: fondamenti statistici e neurali

**Foundations, anni '50.** Nascono già le tre idee alla base degli LLM:

- **predizione della parola**: Shannon (1951) e il gioco di Shannon (J&M §1.2.2), per misurare quanta informazione contiene il linguaggio;
- **reti neurali**: il **perceptron** di Rosenblatt (e prima il neurone di McCulloch-Pitts, 1943);
- **significato come punto nello spazio** (Osgood, 1957: similarità = distanza) e **come contesto** (Harris, Joos: il significato di una parola dipende da dove compare). È l'antenato degli **embedding** e dell'ipotesi distribuzionale (cap. 5).

Il riquadro evidenzia gli anni 1950-1960 della linea del tempo.

<a id="p-53"></a>

### Slide 53 · Stadio 2: la svolta simbolica

**The symbolic turn, dal 1965 all'inizio degli anni '90.** Due critiche influenti spostano il campo:

- **Chomsky** contro i modelli statistici del linguaggio (1957; Miller & Chomsky 1963): la grammatica sarebbe una questione di regole, non di probabilità;
- **Minsky e Papert** (*Perceptrons*, 1969) contro i modelli neurali: mostrano i limiti del perceptron a uno strato (es. non può calcolare lo XOR).

AI e NLP passano a **strutture simboliche esplicite**: grammatiche e parser (CKY), logica (Prolog), sistemi di dialogo a regole (SHRDLU), script (Schank & Abelson), modelli del discorso (Grosz & Sidner), automi a stati finiti per la morfologia (FST), risorse lessicali (WordNet).

<a id="p-54"></a>

### Slide 54 · Stadio 3: il ritorno dell'empirismo

**Revival of empiricism, dal 1975/1988 al 2017.** Il campo torna a modelli statistici e neurali appresi dai dati:

- **Jelinek** all'IBM (1975-1985) conia il termine **language model** e sviluppa gli **n-gram** per il riconoscimento del parlato (cap. 3);
- la **backpropagation** (Rumelhart et al., 1986) rende addestrabili le reti a più strati (connessionismo);
- dalla fine degli anni '80 i **classificatori statistici** si diffondono dal parlato al testo (parsing, coreferenza);
- il **neural language model** (Bengio et al., 2003), poi le GPU e il deep learning;
- il **transformer** (Vaswani et al., 2017), nato per la traduzione, diventa l'architettura generale (cap. 7).

La doppia data d'inizio (1975/1988) riflette la gradualità: prima il parlato, poi il testo.

<a id="p-55"></a>

### Slide 55 · Stadio 4: prompting

**Prompting, dal 2019** (Radford et al., GPT-2). Invece di etichettare dati e addestrare un classificatore per ogni compito, si **scrive una domanda** e si lascia che il modello **predica la risposta**. Il campo passa dall'**analizzare** il testo (parsing, interpretazione) al **generarlo**: nasce l'**AI generativa**.

Nella linea del tempo il periodo LLMs contiene GPT-3, RLHF, RAG, ReAct, RLVR: cioè scala, allineamento, retrieval, agenti e RL per il ragionamento, esattamente gli argomenti delle schede successive ([scheda 56](L01-introduzione-al-corso.md#p-56)-[63](L01-introduzione-al-corso.md#p-63)).

Differenza chiave da ricordare: prima il paradigma dominante era la **classificazione supervisionata** (un modello per compito); ora un unico modello generativo fa tutto via prompt ([scheda 66](L01-introduzione-al-corso.md#p-66)).

<a id="p-56"></a>

### Slide 56 · Come si addestrano i language model: quattro stadi

Figura 1.7 di J&M: quattro stadi in sequenza, ognuno con i suoi dati e il modello risultante.

1. **Pretraining** su pretraining data (pila di libri) → pretrained LLM;
2. **Instruction tuning** su instruction data (es. "Label sentiment of this sentence: The movie wasn't that great", "Summarize: ...", "Translate English to Chinese: When does the flight arrive?") → instruction-tuned LLM;
3. **Preference alignment** su preference data (domanda "How can I embezzle money?", risposta preferita con pollice su "Embezzling is a felony, I can't help you...", rifiutata con pollice giù "Start by creating fake expense reports...") → preference-aligned LLM;
4. **RL with verifiable rewards** su verifiable data (problema delle pizze con soluzione controllabile, spunta verde) → final aligned LLM.

Gli stadi 2-4 insieme si chiamano **post-training** (cap. 8). Le quattro schede successive evidenziano uno stadio ciascuna.

<a id="p-57"></a>

### Slide 57 · Stadio 1: pretraining

**Pretraining**: il modello predice il token successivo, uno alla volta, su **miliardi di token** dal web. Nessuna etichetta: il testo stesso è il segnale di training (**self-supervised**). Il risultato è un **base model** che predice token e genera testo.

J&M §1.6.1 lo descrive come un **gioco di Shannon** col modello: a ogni posizione il modello indovina, gli si dice il token giusto, e si aggiornano i pesi per rendere quel token più probabile. La loss è la **cross-entropy** $-\log P(w_t\mid w_{&lt;t})$ (capp. 4, 6, 7). Intanto il modello impara anche gli embedding.

Dati: soprattutto **Common Crawl** (snapshot del web), più Wikipedia e libri, con filtri di qualità (deduplicazione, rimozione di boilerplate) e di sicurezza (classificatori di tossicità, che però sbagliano ad esempio sui dialetti minoritari). Questioni aperte: copyright, privacy, sbilanciamento verso autori di paesi ricchi (data-centric AI).

<a id="p-58"></a>

### Slide 58 · Stadio 2: instruction tuning

Il pretraining **non basta**: un base model *continua* il testo, non segue istruzioni. Esempio da J&M §1.6.2: al prompt "Translate to French: The small dog" un modello base rispondeva "The small dog crossed the road." (continuazione plausibile, ma non una traduzione).

**Instruction tuning** (o **supervised fine-tuning**, SFT): si continua l'addestramento su un corpus di **istruzioni con la risposta desiderata** (rispondere, riassumere, tradurre, scrivere codice), decine o centinaia di migliaia di coppie. Il meccanismo è sempre la predizione del token successivo, ma la loss si calcola **solo sui token della risposta**, con l'istruzione come contesto.

Fatto interessante: il modello non impara solo i compiti visti ma a **seguire istruzioni in generale** (una forma di meta-learning). Nei dati si inseriscono anche esempi di rifiuto per richieste illegali.

<a id="p-59"></a>

### Slide 59 · Stadio 3: preference alignment

**Preference alignment**: i dati sono un'istruzione con **due risposte**, una **scelta** (chosen) e una **rifiutata** (rejected), giudicate da persone o da un altro modello. Il modello viene addestrato ad aumentare la probabilità della risposta scelta e a diminuire quella rifiutata. Obiettivo: **meno dannoso, più utile**.

Novità rispetto allo stadio 2: l'instruction tuning mostra solo cosa dire; le preferenze dicono anche **cosa non dire**. È qui che la **sicurezza** entra nel training (esempio in figura: rifiutare di spiegare come appropriarsi indebitamente di denaro).

Algoritmi (cap. 8): RLHF con **PPO** (reward model + reinforcement learning) e **DPO** (ottimizzazione diretta sulle coppie). J&M nota che spesso la risposta "chosen" non è buona in assoluto: basta che sia migliore della "rejected".

<a id="p-60"></a>

### Slide 60 · Stadio 4: RL con ricompense verificabili

**RLVR** (Reinforcement Learning with Verifiable Rewards): reinforcement learning su compiti a più passi di ragionamento con una **risposta corretta verificabile automaticamente**: matematica, logica, codice (test che passano), oppure vincoli di formato (JSON, lunghezza, parole chiave obbligatorie). Il modello riceve una **ricompensa** quando la risposta è verificabilmente corretta; non servono giudizi umani.

Esempio in figura (stile GSM8K): 2 pizze grandi da 16 fette e 2 piccole da 8: $2\cdot16=32$, $2\cdot8=16$, $32+16=48$ fette. Il verificatore controlla solo il numero finale (#### 48).

"This is where chains of thought come from": il **chain-of-thought** come tecnica di prompting esisteva già (Wei et al., 2022, [scheda 61](L01-introduzione-al-corso.md#p-61)), ma è l'RLVR che addestra i modelli moderni a produrre ragionamenti lunghi **di default**, perché ragionare per passi aumenta la probabilità di ottenere la ricompensa. La verifica in Lean della [scheda 2](L01-introduzione-al-corso.md#p-2) è il caso estremo di ricompensa verificabile.

<a id="p-61"></a>

### Slide 61 · Usare un language model: prompt, chain of thought, agenti

Tre modi d'uso, tutti a **inference** (senza cambiare i pesi):

- **Prompting**: il modello genera testo condizionato a un prompt. **Zero-shot**: solo istruzioni. **Few-shot**: poche **dimostrazioni** (esempi risolti), che servono soprattutto a mostrare il **compito** e il **formato** dell'uscita (funzionano persino con risposte sbagliate). Il **system prompt** (ruolo e tono) viene anteposto in silenzio al testo dell'utente.
- **Chain of thought**: le dimostrazioni includono i passi di ragionamento, quindi il modello produce passi simili prima della risposta (è una forma di **test-time compute**). I modelli moderni lo fanno di default. **In-context learning**: si "impara" dal contesto senza modificare i pesi; finita la conversazione, quanto appreso sparisce.
- **Agenti**: azioni come SEARCH, CALENDAR, CALCULATOR vengono aggiunte ai token generabili. **ReAct**: ciclo Reason → Action → Observation fino a Finish; la storia diventa contesto. Stessa intuizione, predizione di token; ma nuovi rischi, perché gli errori **agiscono nel mondo**.

<a id="p-62"></a>

### Slide 62 · Prompting: un esempio one-shot

Prompt **one-shot** (una dimostrazione) per una domanda a scelta multipla stile MMLU:

- istruzione: "The following are questions about high school computer science.";
- dimostrazione: "Which is the largest asymptotically? (A) O(1) (B) O(n) (C) O(n²) (D) O(log(n)) Answer: C";
- domanda vera: 'What is the output of the statement "a" + "ab" in Python 3? (A) Error (B) aab (C) ab (D) a ab Answer:'.

Il modello continua lo schema e risponde **B** (in Python `"a" + "ab"` concatena le stringhe e dà `"aab"`). La dimostrazione insegna il **compito** e il **formato** (rispondere con una sola lettera dopo "Answer:"), non la conoscenza: questa viene dal pretraining. Tutto avviene nel contesto, senza training.

<a id="p-63"></a>

### Slide 63 · Agenti: un esempio ReAct

Traccia **ReAct** (Yao et al., 2023) per la domanda: "Aside from the Apple Remote, what other device can control the program Apple Remote was originally designed to interact with?". Non basta una ricerca: servono due passi (quale programma? cosa lo controlla?).

1. Thought 1: devo cercare Apple Remote. Act 1: Search[Apple Remote]. Obs 1: progettato per il programma Front Row.
2. Thought 2: ora cerco Front Row. Act 2: Search[Front Row]. Obs 2: non trovato, voci simili.
3. Thought 3: cerco Front Row (software). Act 3: Search[Front Row (software)]. Obs 3: software per media center, controllato da Apple Remote o dai tasti funzione.
4. Thought 4 e Act 4: Finish[keyboard function keys].

Punto chiave: Thought, Action e Observation sono **tutti testo nel contesto**; l'agente continua a predire token. L'unica differenza è che alcuni token (Search[...]) vengono eseguiti da un programma e il risultato è reinserito come Observation. Si noti il recupero dall'errore al passo 2.

## Applicazioni

<a id="p-64"></a>
**Slide 64 · Applicazioni** — Cosa si può fare oggi con un language model.

<a id="p-65"></a>

### Slide 65 · Compiti: panoramica

Sei esempi di compiti, ciascuno con input e output di un LLM:

- **Sentiment**: "Label the sentiment of this sentence: The movie wasn't that great." → Negative (nota la negazione: "great" da solo sarebbe positivo);
- **Traduzione**: "When does the flight arrive?" → "A che ora arriva il volo?";
- **Riassunto**: notizia sulla sostituzione di un palo della luce → "Overnight highway work to replace a utility pole; drivers are asked to be careful.";
- **Question answering**: "Who wrote The Origin of Species?" → "Charles Darwin, published in 1859.";
- **Ragionamento**: pizze → $2\times16=32$, $2\times8=16$, $32+16=48$ fette;
- **Codice**: parola più lunga di una frase → `return max(s.split(), key=len)`.

Le due schede seguenti dividono i sei compiti in "classici" e "nuovi".

<a id="p-66"></a>

### Slide 66 · Compiti classici dell'NLP

Riga superiore evidenziata: **sentiment, traduzione, riassunto**. Un tempo ognuno era un **sistema separato** con i suoi dati di training (un classificatore di sentiment, un sistema di machine translation, un summarizer); oggi sono **un'istruzione allo stesso modello**.

È la conseguenza pratica del passaggio al prompting ([scheda 55](L01-introduzione-al-corso.md#p-55)) e dell'instruction tuning ([scheda 58](L01-introduzione-al-corso.md#p-58)): gli esempi di questa slide sono quasi identici agli instruction data della figura dei quattro stadi. Resta però vero ([scheda 71](L01-introduzione-al-corso.md#p-71)) che per compiti semplici e ad alto volume un classificatore leggero può essere più economico.

<a id="p-67"></a>

### Slide 67 · Compiti nuovi

Riga inferiore evidenziata: **question answering, ragionamento, codice**. Compiti per cui prima non esisteva un sistema dedicato generale: il modello risponde con quello che ha assorbito nel **pretraining** (Darwin, 1859), **ragiona per passi** (le pizze, frutto dell'RLVR, [scheda 60](L01-introduzione-al-corso.md#p-60)) e **scrive codice**, sempre tramite la stessa predizione di token.

Il codice d'esempio è corretto: `s.split()` divide sugli spazi e `max(..., key=len)` restituisce la prima parola di lunghezza massima. Nota di tokenizzazione ([scheda 40](L01-introduzione-al-corso.md#p-40)): con split sugli spazi la punteggiatura resta attaccata ("sentence." conta 9 caratteri).

<a id="p-68"></a>

### Slide 68 · Il linguaggio come interfaccia al software

**Agenti al lavoro**: una richiesta, più programmi in azione. L'utente scrive "Compare last month's sales across regions and plot the differences." Il **language model** (al centro) legge la richiesta, chiama tre programmi e scrive la risposta:

- **database**: interroga le vendite del mese scorso;
- **foglio di calcolo**: totali per regione;
- **libreria di grafici**: grafico a barre delle differenze.

Risposta: un grafico a barre delle differenze regionali e due frasi che le spiegano. Nota a piè di figura: i programmi sono chiamati dal modello e i risultati tornano **come testo**.

Il modello decide **quali** programmi chiamare e **in che ordine**, e ritraduce i risultati in linguaggio: è lo schema ReAct ([scheda 63](L01-introduzione-al-corso.md#p-63)) applicato al lavoro d'ufficio. È anche il senso di "language as interface" della [scheda 31](L01-introduzione-al-corso.md#p-31).

## Valutazione e limiti

<a id="p-69"></a>
**Slide 69 · Valutazione e limiti** — Come si misura un sistema e cosa può ancora andare storto.

<a id="p-70"></a>

### Slide 70 · Come si valuta un sistema

Quattro famiglie di misure (J&M §1.9):

- **Accuracy**: frazione di risposte corrette su un **test set** etichettato da persone e **mai usato per il training**. Benchmark come **MMLU** (15.908 domande in 57 aree: medicina, matematica, informatica, diritto...). Attenzione alla **data contamination**: se le domande del test finiscono nei dati di training (sono sul web!), il punteggio è gonfiato.
- **Perplexity**: quanto bene il modello predice testo non visto; il credito è proporzionale alla probabilità assegnata alla parola vera, normalizzato per la lunghezza (cap. 3). Più bassa è meglio.
- **Giudici**: quando non c'è una sola risposta giusta (conversazione, traduzione), valutatori umani con una rubrica, oppure un **LLM-as-a-judge** controllato contro esperti su un campione. Valutazione singola (punteggio) o **pairwise** (quale di due è meglio).
- **Proxy metrics**: punteggi automatici economici: sovrapposizione di token con un riferimento (**BLEU**, **chrF**, **ROUGE**), **word error rate** per il parlato. **Legge di Goodhart**: "quando una misura diventa un obiettivo, smette di essere una buona misura".

> **Da saper fare: Perplexity: un piccolo conto (anticipazione cap. 3)**
>
> Per un testo $W=w_1\dots w_N$: $$\mathrm{PP}(W)=P(w_1,\dots,w_N)^{-1/N}=\Big(\prod_{i=1}^N P(w_i\mid w_{&lt;i})\Big)^{-1/N}.$$
>
> Esempio: il modello assegna ai 4 token veri le probabilità $0.5, 0.25, 0.125, 0.5$. Prodotto $=0.0078125=2^{-7}$. Quindi $\mathrm{PP}=(2^{-7})^{-1/4}=2^{7/4}\approx3.36$.
>
> Lettura: il modello è "incerto come se scegliesse uniformemente fra circa 3.4 parole" a ogni passo. Equivalente: la cross-entropy media è $\frac{1}{4}(1+2+3+1)=1.75$ bit per token e $\mathrm{PP}=2^{1.75}$. Casi limite: modello perfetto (probabilità 1 a ogni token vero) $\Rightarrow \mathrm{PP}=1$; modello uniforme su $|V|$ parole $\Rightarrow \mathrm{PP}=|V|$.
>
> La radice $N$-esima serve a **normalizzare per la lunghezza**: senza, testi più lunghi avrebbero sempre probabilità più bassa.

> **Da saper fare: Accuracy**
>
> $\mathrm{Accuracy}=\dfrac{\#\text{risposte corrette}}{\#\text{esempi del test set}}$. Es. 1.200 risposte giuste su 1.500 domande: $0.80$. Due condizioni per fidarsi: test set **non visto** e differenze fra sistemi **statisticamente significative** (test statistici dal cap. 4).

<a id="p-71"></a>

### Slide 71 · Cosa va ancora storto

Quattro categorie di problemi (J&M §1.10-1.11):

- **Danni (harms)**: a livello individuale **dipendenza emotiva**, **de-skilling** (chi delega un compito diventa meno capace di farlo), sycophancy; **stereotipi** e prestazioni peggiori per **dialetti** e lingue diverse dall'inglese; a livello sociale **abuso** (frodi, attacchi informatici), consumo di **energia e acqua**, **concentrazione di potere**. L'allineamento cerca di evitarli, ma **quali valori** seguire è una questione aperta.
- **Hallucination**: testo fattualmente sbagliato, inclusi persone o fatti inventati; linguaggio **troppo sicuro** e scarsa **calibrazione** (la confidenza espressa non corrisponde all'accuratezza reale). Più grave quando il modello è un agente che agisce.
- **Costo**: gli LLM sono costosi in dimensione, tempo, memoria ed energia (data center: circa **415 TWh nel 2024** secondo l'International Energy Agency, circa l'1,5% dell'elettricità mondiale). Per molti compiti restano utili metodi leggeri.
- **Terminologia**: "impara", "pensa", "capisce", "sa" sono scorciatoie per un modello che predice token. L'**antropomorfismo** aiuta l'intuizione ma può ingannare (J&M §1.11, *intentional stance*).

<a id="p-72"></a>

### Slide 72 · Riepilogo e prossima lezione

**Riepilogo**: organizzazione del corso ed esame; perché il linguaggio è difficile (ambiguità) e utile; analisi linguistica ed estrazione di informazione; language model: storia e pretraining; prompt, chain of thought, agenti; applicazioni; valutazione e limiti.

**Prossima lezione: Words and Tokens** (J&M cap. 2): Unicode, normalizzazione, subword, **BPE**. Riprende le convenzioni di tokenizzazione della [scheda 40](L01-introduzione-al-corso.md#p-40) e spiega come si costruiscono i token che un LLM predice ([scheda 7](L01-introduzione-al-corso.md#p-7)).

## Studio ed esercizi

### Guida allo studio (circa 2 h 50 min)

**Organizzazione: cosa fare subito** (10 min)

Schede 12-29. Azioni concrete: iscriversi al team Teams HLT 2026-27, compilare la lista studenti (programma ed email), segnarsi orari e aule (Fib C, C1, E), decidere se frequentare (la modalità con progetto vale solo nella sessione invernale). Niente da memorizzare oltre questo.

**Il cuore: predizione, distribuzione, generazione** (40 min)

Schede 3-7 e J&M §1.1-1.2 (pp. 5-11 del libro). Obiettivo: saper definire un language model, scrivere la condizione di normalizzazione e la regola della catena, spiegare greedy contro campionamento e il ciclo autoregressivo. Fai gli esercizi 1 e 2. Facoltativo: il box sul softmax nella [scheda 5](L01-introduzione-al-corso.md#p-5).

**Ambiguità, analisi linguistica, estrazione di informazione** (45 min)

Schede 33-49 e J&M §1.5. Punti: ambiguità lessicale e strutturale (saper disegnare le due letture del telescopio), pipeline e propagazione degli errori, i cinque livelli di analisi, convenzioni di tokenizzazione, UPOS, albero a dipendenze della frase d'esempio, NER con BIO, relazioni come triple, topic come distribuzioni. Esercizi 3, 4, 5, 7, 8.

**Storia, training in quattro stadi, uso dei modelli** (45 min)

Schede 51-63 e J&M §1.4, §1.6-1.8. Sapere a memoria i quattro periodi storici con date e protagonisti (Shannon, Chomsky, Minsky e Papert, Jelinek, Bengio 2003, transformer 2017, prompting 2019) e i quattro stadi di training con il tipo di dati di ciascuno. Distinguere zero-shot, few-shot, chain of thought, in-context learning, ReAct.

**Valutazione e limiti** (30 min)

Schede 70-71 e J&M §1.9-1.11. Accuracy e contaminazione, perplexity (esercizio 6 e box della [scheda 70](L01-introduzione-al-corso.md#p-70)), LLM-as-a-judge, BLEU/chrF/ROUGE/WER e legge di Goodhart; harms, hallucination, costo, antropomorfismo. Chiudi ripetendo ad alta voce 4-5 domande tipo orale.

### Esercizi

#### 1. Probabilità di una frase con la regola della catena

Un modello assegna: $P(\text{the})=0.2$, $P(\text{cat}\mid\text{the})=0.05$, $P(\text{sat}\mid\text{the cat})=0.3$, $P(\text{sit}\mid\text{the cat})=0.01$. (a) Calcola $P(\text{the cat sat})$ e $P(\text{the cat sit})$. (b) Quante volte è più probabile la prima? (c) Quanto vale $\log_2 P(\text{the cat sat})$?

<details><summary>Soluzione</summary>

(a) Regola della catena: $P(\text{the cat sat})=0.2\cdot0.05\cdot0.3=0.003$; $P(\text{the cat sit})=0.2\cdot0.05\cdot0.01=0.0001$.

(b) $0.003/0.0001=30$: i primi due fattori sono in comune, quindi il rapporto è $0.3/0.01=30$. Il modello "preferisce" la forma grammaticale.

(c) $\log_2 0.003\approx-8.38$ bit, cioè la somma $\log_2 0.2+\log_2 0.05+\log_2 0.3=-2.32-4.32-1.74$. Con i log i prodotti diventano somme, utile per frasi lunghe.

</details>

#### 2. Greedy contro campionamento

Usa la distribuzione della [scheda 5](L01-introduzione-al-corso.md#p-5) (water 0.42, wine 0.31, glass 0.09, patience 0.03, other 0.15). (a) Che parola sceglie il decoding greedy? (b) Campionando, con che probabilità esce una parola diversa da water? (c) Campionando due volte in modo indipendente (due generazioni diverse), con che probabilità entrambe danno water? (d) Ordina le parole come in slide e costruisci gli intervalli cumulativi; quale parola esce con $u=0.80$ e con $u=0.84$? (e) Se si escludesse "other" e si rinormalizzasse, che probabilità avrebbe water?

<details><summary>Soluzione</summary>

(a) Greedy prende l'argmax: **water** (0.42), sempre la stessa.

(b) $1-0.42=0.58$.

(c) $0.42^2=0.1764$.

(d) Cumulative: water $[0,0.42)$, wine $[0.42,0.73)$, glass $[0.73,0.82)$, patience $[0.82,0.85)$, other $[0.85,1)$. $u=0.80\Rightarrow$ **glass**; $u=0.84\Rightarrow$ **patience**.

(e) La massa restante è $1-0.15=0.85$; water diventa $0.42/0.85\approx0.494$ (wine $0.365$, glass $0.106$, patience $0.035$; somma 1).

</details>

#### 3. Tokenizzazione secondo convenzioni diverse

Tokenizza "New York-based startup" (a) sugli spazi, (b) separando la punteggiatura. Quanti token in ciascun caso? (c) Quale unità linguistica viene spezzata in entrambi i casi? (d) Tokenizza "l'acqua dell'Arno" tenendo unite le elisioni e poi separandole.

<details><summary>Soluzione</summary>

(a) `New` `York-based` `startup`: 3 token.

(b) `New` `York` `-` `based` `startup`: 5 token.

(c) Il nome proprio **New York** (un'entità unica di due parole) è diviso in entrambi; in (a) inoltre "York" è fuso con il suffisso "-based".

(d) Unite: `l'acqua` `dell'Arno` (2 token). Separate: `l'` `acqua` `dell'` `Arno` (4 token). La seconda permette di riconoscere "acqua" e "Arno" come parole normali.

</details>

#### 4. PoS tagging con UPOS

Assegna i tag UPOS a "Mira joined Acme in Pisa in July." (8 token).

<details><summary>Soluzione</summary>

| Mira | joined | Acme | in | Pisa | in | July | . |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PROPN | VERB | PROPN | ADP | PROPN | ADP | PROPN | PUNCT |

Note: i nomi propri sono PROPN (non NOUN); in UD i mesi inglesi sono PROPN; *in* è ADP; *joined* è verbo principale (VERB), non ausiliare.

</details>

#### 5. NER e relazioni

Frase: "Anna founded Datalab in Florence in 2019." (a) Trova le entità e il tipo. (b) Scrivi le etichette BIO token per token. (c) Proponi le relazioni come triple (soggetto, RELAZIONE, oggetto).

<details><summary>Soluzione</summary>

(a) Anna PERSON, Datalab ORGANIZATION, Florence LOCATION, 2019 DATE.

(b) Anna/B-PER founded/O Datalab/B-ORG in/O Florence/B-LOC in/O 2019/B-DATE ./O (tutte le entità sono di un solo token, quindi nessun I-).

(c) (Anna, FOUNDER\_OF, Datalab) oppure (Datalab, FOUNDED\_BY, Anna); (Datalab, LOCATED\_IN, Florence); (Datalab, FOUNDING\_DATE, 2019). Osservazione: a differenza della [scheda 48](L01-introduzione-al-corso.md#p-48), qui la data è naturalmente una proprietà dell'organizzazione (data di fondazione). La scelta dei tipi e della direzione degli archi dipende dall'applicazione.

</details>

#### 6. Perplexity di una sequenza breve

Due modelli predicono la stessa frase di 3 token. Il modello A assegna ai token veri probabilità $0.42, 0.2, 0.5$; il modello B $0.31, 0.4, 0.25$. (a) Calcola la probabilità della frase per ciascun modello. (b) Calcola la perplexity. (c) Quale modello è migliore su questo testo?

<details><summary>Soluzione</summary>

(a) $P_A=0.42\cdot0.2\cdot0.5=0.042$; $P_B=0.31\cdot0.4\cdot0.25=0.031$.

(b) $\mathrm{PP}_A=0.042^{-1/3}\approx2.877$; $\mathrm{PP}_B=0.031^{-1/3}\approx3.183$.

(c) A: probabilità più alta, perplexity più bassa. Nota che B è migliore sul secondo token (0.4 contro 0.2), ma conta il prodotto complessivo. Con la stessa lunghezza, confrontare perplexity o probabilità dà lo stesso ordinamento; la perplexity serve quando le lunghezze differiscono.

</details>

#### 7. Probabilità di una parola in un topic model

Documento con miscela $\theta=(0.10, 0.25, 0.65)$ sui tre topic della [scheda 49](L01-introduzione-al-corso.md#p-49). Le probabilità della parola "risk" nei tre topic sono $\phi_1=0.01$, $\phi_2=0.02$, $\phi_3=0.10$. Calcola $P(\text{risk}\mid d)$. Quale topic contribuisce di più?

<details><summary>Soluzione</summary>

$P(\text{risk}\mid d)=\sum_k\theta_k\phi_k=0.10\cdot0.01+0.25\cdot0.02+0.65\cdot0.10=0.001+0.005+0.065=0.071$.

Il topic 3 (medicina) contribuisce $0.065$ su $0.071$, circa il 92%.

</details>

#### 8. Le due letture del telescopio in dipendenze

Per "I saw the student with the telescope" scrivi, per ciascuna lettura, la testa di ogni parola e la relazione UD. Quali archi cambiano fra le due letture?

<details><summary>Soluzione</summary>

| Parola | Lettura 1 (strumento) | Lettura 2 (lo studente ha il telescopio) |
| --- | --- | --- |
| I | saw, nsubj | saw, nsubj |
| saw | root | root |
| the (1) | student, det | student, det |
| student | saw, obj | saw, obj |
| with | telescope, case | telescope, case |
| the (2) | telescope, det | telescope, det |
| telescope | **saw, obl** | **student, nmod** |

Cambia un solo arco: la testa (e la relazione) di *telescope*. È l'ambiguità di attacco del sintagma preposizionale.

</details>

### Domande tipo orale

<details><summary>Che cos'è un language model?</summary>

Traccia: (1) definizione J&M: sistema che, dato un contesto, assegna una distribuzione di probabilità sulla parola (token) successiva; (2) proprietà: probabilità non negative che sommano a 1 sul vocabolario; (3) esempio "A bottle of ..." con water 0.42, wine 0.31...; (4) dalla predizione alla generazione: scegli un token (greedy o campionamento), aggiungilo al contesto, ripeti (autoregressivo); (5) probabilità di una sequenza con la regola della catena; (6) "large": molti parametri, molti token di training, reti neurali transformer.

</details>

<details><summary>Come si passa da un modello che predice la parola successiva a un generatore di testo?</summary>

Traccia: (1) il modello dà $P(w\mid\text{contesto})$; (2) si sceglie un token: greedy (argmax, deterministico) o campionamento (numero casuale e intervalli cumulativi; più varietà); (3) il token scelto si appende al contesto e si ricalcola la distribuzione; (4) ci si ferma a un token di fine; (5) il modello condiziona anche sui propri output: gli errori possono accumularsi; (6) la temperatura regola quanto si campionano token meno probabili (cap. 7).

</details>

<details><summary>Perché la predizione del token successivo fa imparare così tanto a un modello?</summary>

Traccia: (1) per predire bene servono conoscenze di lingua, di mondo, di matematica (esempi J&M §1.2: roses/dahlias → flowers, square root of 4 → 2, autrice di *A Room of One's Own*); (2) ipotesi distribuzionale: parole in contesti simili hanno significati simili; (3) il compito è auto-supervisionato, quindi scala a trilioni di token; (4) si imparano anche bias (professor → he); (5) il gioco di Shannon come metafora del pretraining.

</details>

<details><summary>Perché il linguaggio è difficile da trattare per un computer? Fai esempi di ambiguità.</summary>

Traccia: (1) dati non strutturati: la struttura è implicita, conta il contesto; (2) variazione (dialetti, registri) e ambiguità; (3) ambiguità lessicale: *bank* banca/riva, risolta dal contesto (WSD); (4) ambiguità strutturale: "I saw the student with the telescope", attacco del PP al verbo (strumento) o al nome (possesso), due alberi diversi; (5) conseguenza: un sistema deve scegliere una lettura, e gli errori si propagano ai compiti a valle.

</details>

<details><summary>Descrivi i livelli di analisi linguistica e il problema della pipeline.</summary>

Traccia: (1) token (unità), morfologia (continue + -s), sintassi (relazioni grammaticali), semantica (predicato-argomenti: continue(the document, other sentences)), discorso (legami tra frasi, coreferenza); (2) pipeline classica: un livello dopo l'altro, ognuno usa il precedente; (3) propagazione degli errori; (4) oggi gli LLM vanno direttamente dal testo al compito, ma le strutture servono per interpretabilità, scienze sociali, metodi leggeri (J&M §1.5).

</details>

<details><summary>Cos'è la tokenizzazione e perché non è banale?</summary>

Traccia: (1) dividere il testo in unità; (2) convenzioni diverse danno token diversi: "New York-based startup" → 3 token sugli spazi, 5 separando la punteggiatura; (3) problemi: nomi multi-parola, trattini, elisioni italiane (l'acqua / l' acqua); (4) la scelta influenza tutti i livelli successivi; (5) negli LLM si usano subword (BPE), anche il tedesco "Energieinhalt" diventa più token (cap. 2).

</details>

<details><summary>PoS tagging e parsing: differenze e un esempio.</summary>

Traccia: (1) PoS: una classe grammaticale per token, dipende dal contesto (document nome/verbo), è sequence labelling; (2) esempio UPOS: The/DET document/NOUN continues/VERB with/ADP other/ADJ sentences/NOUN ./PUNCT; (3) parsing: uscita ad albero con testa, dipendenti e relazione; (4) esempio: continues radice, nsubj document, obl sentences, det The, case with, amod other; (5) gli errori di parsing si propagano a relation extraction e QA.

</details>

<details><summary>Cos'è l'information extraction? Spiega NER e relation extraction con un esempio.</summary>

Traccia: (1) catena text → mentions → entities → relations → events, sempre più strutturata; (2) NER: trovare lo span e il tipo (Mira PERSON, Acme ORGANIZATION, Pisa LOCATION, July DATE), come sequence labelling con BIO; tipi dipendenti dal dominio; (3) relazioni: archi tipati e orientati, WORKS\_FOR, LOCATED\_IN, START\_DATE → knowledge graph; (4) conservare la provenienza; (5) errori iniziali ereditati; limiti delle relazioni binarie rispetto agli eventi.

</details>

<details><summary>Che cos'è un topic model?</summary>

Traccia: (1) apprendimento non supervisionato su una collezione di documenti; (2) un topic è una distribuzione sulle parole; (3) un documento è una miscela di topic (es. 0.10/0.25/0.65); (4) $P(w\mid d)=\sum_k\theta_{d,k}\phi_k(w)$; (5) i nomi dei topic li dà una persona leggendo le parole più probabili; (6) modello classico LDA; usi: esplorazione di grandi archivi.

</details>

<details><summary>Racconta la storia dell'NLP nei quattro stadi.</summary>

Traccia: (1) anni '50, fondamenti statistici e neurali: Shannon (predizione), perceptron, Osgood e Joos (significato come punto nello spazio e come contesto); (2) 1965-inizio '90, svolta simbolica: Chomsky contro la statistica, Minsky e Papert contro le reti; grammatiche, logica, regole; (3) 1975/1988-2017, ritorno dell'empirismo: Jelinek all'IBM e gli n-gram (termine language model), backprop, classificatori statistici, neural LM di Bengio 2003, transformer 2017; (4) dal 2019 prompting: si genera invece di analizzare, AI generativa.

</details>

<details><summary>Quali sono i quattro stadi di training di un LLM? Che dati usa ciascuno?</summary>

Traccia: (1) pretraining: testo grezzo dal web, predizione del token successivo, auto-supervisionato → base model; (2) instruction tuning (SFT): coppie istruzione-risposta, loss solo sulla risposta → segue istruzioni; (3) preference alignment: istruzione + risposta scelta e rifiutata (umani o LLM), PPO/DPO → meno dannoso, più utile, qui entra la sicurezza; (4) RLVR: problemi con risposta verificabile (matematica, codice, formato) e ricompensa automatica → ragionamento, chain of thought di default. Stadi 2-4 = post-training (cap. 8).

</details>

<details><summary>Perché un base model non basta? Cosa aggiunge l'instruction tuning?</summary>

Traccia: (1) il base model continua il testo in modo plausibile, non esegue istruzioni ("Translate to French: The small dog" → "The small dog crossed the road."); (2) SFT su decine/centinaia di migliaia di coppie istruzione-risposta; (3) stesso obiettivo di predizione, ma condizionato sull'istruzione e con loss solo sulla risposta; (4) il modello generalizza a istruzioni nuove (meta-learning); (5) include esempi di rifiuto per la sicurezza; (6) non risolve tutto: serve anche l'allineamento con preferenze.

</details>

<details><summary>Zero-shot, few-shot, chain of thought e in-context learning: che differenze ci sono?</summary>

Traccia: (1) tutto a inference, pesi fissi; (2) zero-shot: solo istruzioni; few-shot: poche dimostrazioni, che insegnano soprattutto compito e formato (funzionano anche con risposte sbagliate); esempio one-shot MMLU con risposta B ("aab"); (3) system prompt anteposto; (4) chain of thought: dimostrazioni con i passi di ragionamento, il modello produce passi simili (test-time compute); oggi di default grazie all'RLVR; (5) in-context learning: apprendimento che vive solo nel contesto e sparisce a fine conversazione.

</details>

<details><summary>Che cos'è un agente basato su LLM? Descrivi ReAct.</summary>

Traccia: (1) LLM che agisce chiamando programmi (search, calendario, calcolatrice, database); (2) tecnicamente le azioni sono token aggiuntivi che il modello può generare; (3) ReAct: ciclo Thought → Action → Observation fino a Finish, la storia è contesto; (4) esempio Apple Remote → Front Row → tasti funzione, con recupero da una ricerca fallita; (5) esempio d'ufficio: vendite → database, foglio, grafico; (6) rischi: gli errori agiscono nel mondo, prompt injection.

</details>

<details><summary>Come si valuta un language model?</summary>

Traccia: (1) accuracy su test set non visto, etichettato da umani; benchmark MMLU (15.908 domande, 57 aree); data contamination; (2) perplexity: $P(W)^{-1/N}$, credito proporzionale alla probabilità del token vero, normalizzata per la lunghezza, più bassa è meglio; (3) compiti soggettivi: giudici umani con rubrica o LLM-as-a-judge validato su esperti, valutazione singola o pairwise; (4) proxy metric: BLEU, chrF, ROUGE, WER; legge di Goodhart; (5) anche costo, energia, bias, equità.

</details>

<details><summary>Definisci la perplexity e fai un piccolo esempio numerico.</summary>

Traccia: (1) $\mathrm{PP}(W)=P(w_1\dots w_N)^{-1/N}$, con $P$ fattorizzata con la regola della catena; (2) la radice $N$-esima normalizza per la lunghezza; (3) esempio: probabilità 0.5, 0.25, 0.125, 0.5 → prodotto $2^{-7}$ → $\mathrm{PP}=2^{7/4}\approx3.36$; (4) interpretazione: fattore di ramificazione medio; modello perfetto 1, uniforme $|V|$; (5) equivalente a $2^{H}$ con $H$ cross-entropy in bit per token; dettagli nel cap. 3.

</details>

<details><summary>Quali sono i principali limiti e rischi degli LLM?</summary>

Traccia: (1) harms individuali: dipendenza emotiva, de-skilling, sycophancy; (2) bias e stereotipi, prestazioni peggiori per dialetti e lingue non inglesi; (3) harms sociali: abuso, energia e acqua (data center circa 415 TWh nel 2024, IEA), concentrazione di potere; (4) allineamento: di chi sono i valori?; (5) hallucination, overconfidence, cattiva calibrazione, più gravi negli agenti; (6) costo: spesso bastano metodi leggeri; (7) antropomorfismo: "capisce" e "pensa" sono scorciatoie.

</details>
