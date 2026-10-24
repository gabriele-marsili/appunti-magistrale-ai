# L10 · Semantica vettoriale

*Vector Semantics* · 08/10/2026 · Claudio Gallicchio · lettura: J&M cap. 5, §5.1-5.4; cap. 11, §11.1.1-11.1.3 (tf-idf); Appendice J (PPMI)

[Versione interattiva sul sito](https://gabriele-marsili.github.io/appunti-magistrale-ai/anno-2/hlt/sito/#L10) · [Indice della dispensa](README.md)

Prima lezione sugli embedding (J&M §5.1-5.4, §11.1.1-11.1.3, Appendice J). Che cosa deve catturare un modello del significato (**sensi, sinonimia, similarità, relatedness, connotazione**), l'**ipotesi distribuzionale** (parole in contesti simili hanno significati simili) e la parola come **punto in uno spazio**. Poi la ricetta **contare, pesare, confrontare**: la **matrice parola-contesto** e la **matrice termine-documento**, il **coseno** al posto del prodotto scalare (che favorisce le parole frequenti), **tf-idf** per i documenti e la ricerca, **PMI/PPMI** (con α = 0,75 contro il bias degli eventi rari) per le parole. Sono gli embedding sparsi; la prossima lezione passa a word2vec. Tutti i numeri delle slide sono ricalcolati: un arrotondamento sbagliato a pagina 54 (−6,47 invece di −6,70), uno minimo a pagina 42, e i coseni della figura a pagina 46, calcolati sui conteggi grezzi e non con tf-idf.

## Indice

- [Apertura](#apertura)
- [Semantica lessicale](#semantica-lessicale)
- [Ipotesi distribuzionale ed embedding](#ipotesi-distribuzionale-ed-embedding)
- [Matrice parola-contesto e coseno](#matrice-parola-contesto-e-coseno)
- [Documenti come vettori: tf-idf](#documenti-come-vettori-tf-idf)
- [PMI e PPMI](#pmi-e-ppmi)
- [Riepilogo: quale conteggio, quale peso](#riepilogo-quale-conteggio-quale-peso)
- [Notebook](#notebook)
- [Studio ed esercizi](#studio-ed-esercizi)

## Apertura

<a id="p-1"></a>

### Slide 1 · Semantica vettoriale

Decima lezione, inizio del capitolo 5 di J&M (*Embeddings*). Finora una parola è stata una **stringa** o un **indice nel vocabolario**: negli n-gram ([L4](L04-modelli-linguistici-n-gram.md#p-8)) *cat* e *dog* sono due simboli diversi quanto *cat* e *carburetor*, e nei classificatori della [L6](L06-regressione-logistica.md#p-7) una parola mai vista in training non dà nessun indizio. Qui si costruisce una rappresentazione del **significato** come **vettore**:

- che cosa dovrebbe fare un modello del significato delle parole (**semantica lessicale**);
- l'idea di fondo: il significato si ricava dal **contesto** (ipotesi distribuzionale);
- vettori di **conteggi** e il **coseno** per confrontarli;
- due modi di pesare i conteggi: **tf-idf** per i documenti e **PPMI** per le parole.

Sono gli embedding **sparsi**; la prossima lezione passa a quelli densi (word2vec).

<a id="p-2"></a>

### Slide 2 · Indice della lezione

Cinque blocchi:

1. **Semantica lessicale**: sensi, sinonimia, similarità, relatedness, connotazione (§5.1).
2. **Semantica vettoriale, l'intuizione**: ipotesi distribuzionale, la parola come punto in uno spazio (§5.2).
3. **Embedding da conteggi e coseno**: matrice parola-contesto, prodotto scalare, lunghezza, coseno (§5.3-5.4).
4. **Documenti come vettori: tf-idf**: matrice termine-documento, tf, idf, ricerca (cap. 11, §11.1.1-11.1.3).
5. **Pesare le co-occorrenze: PPMI**: PMI, PPMI, il problema degli eventi rari (Appendice J).

La pausa cade fra il blocco 3 e il blocco 4.

<a id="p-3"></a>

### Slide 3 · Riferimento: J&M capitolo 5, §5.1-5.4

Lettura principale: **Jurafsky & Martin**, *Speech and Language Processing*, 3a ed. draft del 19 agosto 2026, capitolo 5 (*Embeddings*), sezioni 5.1-5.4 (pagine 127-136 del libro):

- 5.1 semantica lessicale; 5.2 l'intuizione della semantica vettoriale;
- 5.3 embedding semplici basati su conteggi; 5.4 il coseno.

Poi due letture fuori dal capitolo 5:

- **capitolo 11** (*Retrieval-based Models*), §11.1.1-11.1.2: documenti come vettori e tf-idf (pagine 255-257). La slide cita solo queste due, ma le slide 45-46 (punteggio di un documento con il coseno) corrispondono al §11.1.3, pagine 258-259, con l'esempio delle quattro nano-frasi usato nell'esercizio 9 della scheda;
- **Appendice J**, sul sito del libro (non è nel PDF del libro): PMI e PPMI.

Le sezioni 5.5-5.10 (word2vec, proprietà ed errori degli embedding) sono la prossima lezione.

## Semantica lessicale

<a id="p-4"></a>
**Slide 4 · Semantica lessicale** — Primo blocco: che cosa dovrebbe saper fare un modello del significato delle parole.

<a id="p-5"></a>

### Slide 5 · Che cosa deve fare un modello del significato

Rappresentare il significato di *dog* con la stringa DOG (o con un indice) non dice niente. Il libro cita la battuta di Barbara Partee: *Qual è il significato della vita? LIFE'*. Un buon modello dovrebbe invece catturare:

- **parole simili e opposte**: *cat* è simile a *dog*; *cold* è l'**antonimo** di *hot*;
- **connotazioni**: *happy* è positiva, *sad* negativa (è ciò che serve al sentiment della [L6](L06-regressione-logistica.md#p-5));
- **prospettive** sullo stesso evento: *buy*, *sell* e *pay* descrivono lo stesso acquisto da punti di vista diversi (se io compro da te, tu mi hai venduto e io ti ho pagato);
- **inferenze**, per question answering e dialogo.

Lo studio linguistico del significato delle parole è la **semantica lessicale** (*lexical semantics*). Oggi se ne vedono solo le nozioni di base, quelle che i vettori proveranno a catturare; antonimia, iponimia e meronimia sono nell'Appendice I del libro.

<a id="p-6"></a>

### Slide 6 · Sensi, sinonimia, similarità, relatedness

- **Sensi**: un **lemma** (*mouse*, forma di citazione anche di *mice*; cfr. lemmatizzazione nella [L3](L03-elaborazione-del-testo.md#p-33)) può avere più **word sense**: il roditore o il dispositivo che muove il cursore. Una parola con più sensi è **polisemica**: è l'ambiguità lessicale di *bank* vista nella [scheda 34 della L1](L01-introduzione-al-corso.md#p-34).
- **Sinonimia**: *couch/sofa*, *car/automobile* hanno (quasi) lo stesso significato: sostituibili senza cambiare le condizioni di verità della frase. Mai esattamente identici (**principio di contrasto**: forma diversa, qualche differenza di significato): *H2O* appartiene al registro scientifico, in una guida escursionistica si scrive *water*. Il registro fa parte del significato.
- **Similarità**: *cat* non è sinonimo di *dog* ma i due sono simili (animali domestici, quadrupedi). Pochi sinonimi, moltissime parole simili; ci sono dataset di giudizi umani, ad esempio SimLex-999 su scala 0-10 (*vanish/disappear* 9,8; *hole/agreement* 0,3).
- **Relatedness** (associazione): *coffee* e *cup* non si somigliano affatto, ma sono collegate perché partecipano allo stesso evento (bere il caffè dalla tazza); così *surgeon/scalpel*. Parole dello stesso **campo semantico** (ospedale: *surgeon, nurse, scalpel*) sono collegate; i [topic model](L01-introduzione-al-corso.md#p-49) ne sono la versione appresa.

Similarità e relatedness sono ciò che vogliamo far catturare ai vettori. Come si vedrà, il conteggio dei contesti tende a mescolarle: dipende dalla finestra.

<a id="p-7"></a>

### Slide 7 · Connotazione: una parola come punto nello spazio

La **connotazione** è il significato **affettivo** di una parola: *wonderful* è positiva, *dreary* negativa; parole quasi sinonime possono differire solo in questo (*copy* contro *knockoff*, *innocent* contro *naive*).

**Osgood et al. (1957)** misurarono tre dimensioni, con giudizi umani:

- **valence**: piacevolezza;
- **arousal**: intensità dell'emozione suscitata;
- **dominance**: grado di controllo.

|  | valence | arousal | dominance |
| --- | --- | --- | --- |
| courageous | 8,0 | 5,5 | 7,4 |
| music | 7,7 | 5,6 | 6,5 |
| heartbreak | 2,5 | 5,7 | 3,6 |
| cub | 6,7 | 4,0 | 4,2 |

Il grafico 3D a sinistra mette le quattro parole nello spazio (valence, arousal, dominance): *courageous* e *music* quasi sovrapposti in alto, *cub* più in basso, *heartbreak* (in rosso) lontano, a valence bassa. Tre numeri = le coordinate di un punto; parole vicine hanno connotazioni simili. È la **prima semantica vettoriale**: il significato (una parte di esso) è un punto in uno spazio. La differenza con quanto segue: qui le dimensioni sono scelte e misurate a mano, poi verranno ricavate dal testo.

> **Da saper fare: Distanza o coseno? (esercizio 2 della scheda)**
>
> Distanza euclidea: courageous-music $\sqrt{0{,}3^2+0{,}1^2+0{,}9^2} = 0{,}95$; courageous-heartbreak $\sqrt{5{,}5^2+0{,}2^2+3{,}8^2} = 6{,}69$. Coseni: 0,998 e 0,889. Il coseno quasi non distingue le due coppie, perché le scale vanno da 1 a 9 e tutti i vettori stanno nello stesso ottante, con direzioni vicine. Se si centrano le scale sul punto neutro 5, il coseno courageous-heartbreak diventa $-0{,}92$: con dimensioni che hanno un punto neutro conta la posizione, e la distanza è la misura giusta. Il coseno serve quando la **lunghezza** del vettore è un disturbo (frequenza), come nei conteggi.

## Ipotesi distribuzionale ed embedding

<a id="p-8"></a>
**Slide 8 · Semantica vettoriale: l'intuizione** — Secondo blocco: il significato di una parola si ricava dai contesti in cui compare.

<a id="p-9"></a>

### Slide 9 · L'ipotesi distribuzionale

**Ipotesi distribuzionale**: *parole che compaiono in contesti simili tendono ad avere significati simili*.

- Nasce dai linguisti degli anni '50: **Joos (1950), Harris (1954), Firth (1957)** (la formula famosa di Firth: *you shall know a word by the company it keeps*).
- Esempio di Harris: *oculist* ed *eye-doctor* sono sinonimi e compaiono negli stessi ambienti, vicino a *eye* o *examined*.
- Versione quantitativa: la **quantità di differenza di significato** corrisponde grosso modo alla **quantità di differenza negli ambienti** (Harris, 1954, p. 157).

Il libro apre il capitolo con un'analogia biologica: Smilodon e Thylacosmilus, due specie lontane, hanno sviluppato gli stessi denti a sciabola perché vivevano in ambienti simili (evoluzione convergente). Per le parole vale lo stesso: ambiente simile, "forma" di significato simile.

<a id="p-10"></a>

### Slide 10 · Due idee degli anni '50 che convergono

Stessa ipotesi, nuovo riquadro: la **semantica vettoriale** nasce dall'incontro di due idee degli anni '50:

- il **punto nello spazio** di Osgood (la scheda 7): il significato come coordinate;
- la definizione **distribuzionale** dei linguisti: il significato di una parola è la sua distribuzione nell'uso, cioè le **parole vicine** o gli **ambienti grammaticali**.

Messe insieme: le coordinate di una parola si ricavano dalla sua distribuzione. Le dimensioni non sono più valence o arousal decise da uno psicologo, ma (per ora) le parole del vocabolario che le stanno vicino. Il libro aggiunge una terza fonte, l'information retrieval degli anni '60 (il vector space model di Salton), che è da dove vengono tf-idf e la matrice termine-documento della seconda parte.

<a id="p-11"></a>

### Slide 11 · Embedding

Gli **embedding** sono **rappresentazioni vettoriali del significato delle parole apprese direttamente dalla loro distribuzione nei testi**. Sono il primo esempio, nel libro, di **representation learning**: invece di progettare feature a mano (le sei feature del sentiment nella [scheda 30 della L6](L06-regressione-logistica.md#p-30)) le rappresentazioni si imparano dal testo in modo **self-supervised**, senza etichette umane.

- **Statici**: un vettore per parola (per tipo), lo stesso in ogni frase. Sono quelli di questa lezione e di word2vec.
- **Contestuali** (dinamici): un vettore per **occorrenza** (per istanza, nel senso della [L2](L02-parole-e-token.md#p-8)), diverso a seconda della frase, come in BERT. *bank* della banca e *bank* del fiume hanno vettori diversi.

Gli embedding sono al cuore dei large language model: il primo strato di un LLM trasforma ogni token in un vettore.

<a id="p-12"></a>

### Slide 12 · Che cosa vuol dire ongchoi?

Esperimento mentale del libro. Non conosci la parola *ongchoi* (un prestito recente dal cantonese), ma la vedi in tre contesti:

- (5.1) *Ongchoi is delicious sauteed with garlic.*
- (5.2) *Ongchoi is superb over rice.*
- (5.3) *...ongchoi leaves with salty sauces...*

Già da qui si capisce qualcosa: è commestibile (*delicious*, *sauteed*), si mangia con il riso, ha foglie. Nessuno ti ha dato una definizione: sono bastati i vicini. La slide successiva aggiunge il passo decisivo.

<a id="p-13"></a>

### Slide 13 · Ongchoi: il confronto con altri contesti

Si aggiungono contesti di **altre** parole, già noti:

- (5.4) *...spinach sauteed with garlic over rice...*
- (5.5) *...chard stems and leaves are delicious...*
- (5.6) *...collard greens and other salty leafy greens*

*Ongchoi* condivide i vicini *rice, garlic, delicious, salty* con *spinach*, *chard* e *collard greens*: quindi è probabilmente una **verdura a foglia**. Infatti è *Ipomoea aquatica*, lo spinacio d'acqua. Il ragionamento è indiretto: non si confronta *ongchoi* con *spinach* direttamente, si confrontano i loro **contesti**.

Messaggio della slide: la stessa intuizione si implementa **contando le parole nel contesto** di ongchoi. Se le righe dei conteggi di due parole si somigliano, le parole si somigliano. Tutto il resto della lezione è come contare e come confrontare.

<a id="p-14"></a>

### Slide 14 · Le parole come punti in uno spazio semantico

L'idea della semantica vettoriale: una parola è un **punto in uno spazio multidimensionale**, ricavato dalla distribuzione dei suoi vicini.

La figura (Fig. 5.1 del libro) mostra embedding word2vec a **200 dimensioni** proiettati in 2 dimensioni con t-SNE: attorno a *sweet* (in rosso) stanno *honey, candy, juice, chocolate, cream*; più lontano *cider, wine, drink* (bevande) in un gruppo, *beef, potatoes, fried, soup, rice, corn* (cibi salati) in basso. I punti grigi sono parole non etichettate. Parole di significato simile sono vicine.

- Perché serve: un classificatore di sentiment basato su parole ([L6](L06-regressione-logistica.md#p-7)) non sa niente di una parola assente dal training. Con gli embedding può assegnare un sentiment a una parola mai vista **se ha visto parole di significato simile** (vettori vicini).
- I vettori si imparano dal testo **senza supervisione**.

Nota: la proiezione in 2D distorce le distanze; è un aiuto visivo, non una misura.

<a id="p-15"></a>

### Slide 15 · Due tipi di embedding: sparsi e densi

|  | sparsi | densi |
| --- | --- | --- |
| dimensione | $|V|$, 10.000-50.000 (una per parola del vocabolario) | $d$ = 50-1000 (es. 300) |
| valori | conteggi (o loro funzioni), quasi tutti 0 | numeri reali, anche negativi |
| dimensioni | interpretabili: la dimensione 'pie' conta *pie* | senza interpretazione chiara |
| esempi | conteggi, tf-idf, PPMI (oggi) | word2vec (prossima lezione) |

Esempio della slide: *cherry* sparso è $[0, 0, 2, 0, 0, 8, 0, \dots, 442, 0, 25, 0, \dots]$ (442 è il conteggio con *pie*, 25 con *sugar*, scheda 21), denso è $[0{,}13;\ -0{,}42;\ 0{,}07;\ 0{,}91;\ \dots;\ -0{,}28]$.

Per entrambi lo strumento di confronto è lo stesso: il **coseno**, la misura standard di similarità fra due parole, frasi o documenti. I densi funzionano meglio in praticamente tutti i compiti (meno pesi da imparare, e sinonimi come *car* e *automobile* non restano due dimensioni separate), ma i conteggi sono il modo più chiaro per capire che cosa vuol dire che un vettore rappresenta un significato.

## Matrice parola-contesto e coseno

<a id="p-16"></a>
**Slide 16 · Embedding da conteggi e coseno** — Terzo blocco: contare i vicini, misurare gli angoli.

<a id="p-17"></a>

### Slide 17 · Il piano: contare, pesare, confrontare

Lo schema che regge tutta la lezione, a tre passi, per due oggetti diversi:

| che cosa | 1. contare | 2. pesare | 3. confrontare |
| --- | --- | --- | --- |
| **parole** (testo corrente, finestra di ±4 parole) | **matrice parola-contesto**: una parola è una riga | **PPMI**: associazione, non frequenza | **coseno**: l'angolo, non la lunghezza |
| **documenti** (es. le 37 opere di Shakespeare) | **matrice termine-documento**: un documento è una colonna | **tf-idf**: le parole presenti in ogni documento pesano 0 |

- Prima della pausa: la matrice parola-contesto e il coseno (contare e confrontare).
- Dopo la pausa: le due pesature, tf-idf per i documenti e poi PPMI per le parole.

Il passo 2 esiste perché i conteggi grezzi sono dominati dalle parole frequenti (*the*, *good*): è lo stesso problema in due vesti.

<a id="p-18"></a>

### Slide 18 · La matrice parola-contesto

Una **matrice di co-occorrenza** parola-contesto (*word-context*, o *term-term*): righe = parole target, colonne = parole di contesto, entrambe dal vocabolario, quindi $|V|\times|V|$. La cella $(w, c)$ conta quante volte la parola $c$ compare **vicino** a $w$ nel corpus.

- **Finestra di contesto**: "vicino" vuol dire, per esempio, entro **4 parole a sinistra e 4 a destra** (±4).
- La slide mostra una sola occorrenza per ciascuna di quattro parole, con la sua finestra:
    
  *is traditionally followed by* **cherry** *pie, a traditional dessert*
    
  *often mixed, such as* **strawberry** *rhubarb pie. Apple pie*
    
  *computer peripherals and personal* **digital** *assistants. These devices usually*
    
  *a computer. This includes* **information** *available on the internet*

Contare i vicini è esattamente ciò che si faceva per i bigram ([L4](L04-modelli-linguistici-n-gram.md#p-17)), con due differenze: si guarda a sinistra e a destra, e non solo alla parola adiacente. La dimensione della finestra cambia il tipo di similarità catturata: finestre corte (±1-3) danno vicini simili anche sintatticamente (stessa parte del discorso), finestre lunghe danno parole dello stesso argomento (relatedness), §5.7 del libro.

<a id="p-19"></a>

### Slide 19 · I conteggi delle quattro finestre

|  | a | computer | pie |
| --- | --- | --- | --- |
| cherry | 1 | 0 | 1 |
| strawberry | 0 | 0 | 2 |
| digital | 0 | 1 | 0 |
| information | 1 | 1 | 0 |

Solo tre parole di contesto (*a, computer, pie*), contate solo nelle quattro finestre. Verifica: *cherry* ha a destra *pie, a*; *strawberry* ha *pie* due volte (*rhubarb pie. Apple pie*); *digital* ha *computer* a sinistra; *information* ha *a computer* a sinistra. La riga di *cherry* è evidenziata in rosso: **cherry = [1, 0, 1]**, **information = [1, 1, 0]**.

- Un **vettore** è solo una lista di numeri.
- Uno **spazio vettoriale** è un insieme di vettori, caratterizzato dalla sua **dimensione**: 3 qui, $|V|$ in una matrice vera.

> **Da saper fare: Contare a mano (esercizio 3 della scheda)**
>
> Procedura: per ogni occorrenza della parola target, prendi le $k$ parole a sinistra e a destra (senza uscire dalla frase, se il testo è diviso in frasi) e incrementa la cella di ciascuna. Una parola di contesto che compare due volte nella stessa finestra conta due volte (*strawberry*-*pie* = 2). È il calcolo che fa `word_context_matrix` nella cella 8 del notebook.

<a id="p-20"></a>

### Slide 20 · Le dimensioni hanno un significato

Stessa tabella; la novità è il ruolo dell'**ordine**. Ogni posizione del vettore corrisponde a una parola di contesto fissata una volta per tutte: la terza dimensione di *ogni* vettore conta *pie*, la seconda conta *computer*. Solo così due vettori si possono confrontare componente per componente.

Esempio: *information* e *digital* hanno lo stesso valore, 1, sulla dimensione *computer*: è il primo indizio che le due parole si somigliano. *cherry* e *strawberry* condividono invece la dimensione *pie*. Negli embedding densi questa interpretazione delle singole dimensioni si perde (scheda 15).

<a id="p-21"></a>

### Slide 21 · Conteggi veri da Wikipedia

|  | aardvark | ... | computer | data | result | pie | sugar |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cherry | 0 | ... | 2 | 8 | 9 | 442 | 25 |
| strawberry | 0 | ... | 0 | 0 | 1 | 60 | 19 |
| digital | 0 | ... | 1670 | 1683 | 85 | 5 | 4 |
| information | 0 | ... | 3325 | 3982 | 378 | 5 | 13 |

Ora i conteggi sono su **tutto Wikipedia** (Davies, 2015), e si mostrano sei delle $|V|$ dimensioni, scelte a mano per la pagina (la riga di *digital* è evidenziata). Si vede a occhio che:

- *cherry* e *strawberry* si somigliano fra loro più che a *digital*: entrambe hanno quasi tutta la massa su *pie* e *sugar*;
- *digital* e *information* si somigliano fra loro più che a *strawberry*: massa su *computer* e *data*.

Coseni sulle sei dimensioni (cella 4 del notebook): cherry-strawberry 0,969, digital-information 0,996, cherry-digital 0,019, strawberry-digital 0,003. Questa tabella è il materiale di quasi tutti i conti della lezione: coseno (scheda 28) e PPMI (scheda 52).

<a id="p-22"></a>

### Slide 22 · Vettori sparsi

Stessa tabella; sotto, la riga di *cherry* disegnata come vettore: tante caselle a 0 (*aardvark* e le altre), poi 2, 8, 9, 442, 25 sulle cinque colonne mostrate, poi ancora zeri.

- Una parola è un punto in $|V|$ dimensioni, dove $|V|$ sono di solito le **10.000-50.000 parole più frequenti** del corpus (oltre le 50.000 non conviene: le parole rare danno colonne quasi vuote).
- Quasi tutti i numeri sono zero: sono **vettori sparsi**. Per memorizzarli e calcolare con loro si usano strutture sparse, che salvano solo le celle non nulle.

È la sparsità già vista per i bigram ([scheda 18 della L4](L04-modelli-linguistici-n-gram.md#p-18)), per lo stesso motivo (legge di Zipf): la maggior parte delle coppie di parole non compare mai insieme. Sul corpus di docstring del notebook la matrice 2000 × 2000 ha solo il 2,7% di celle non nulle.

<a id="p-23"></a>

### Slide 23 · Una visualizzazione nello spazio

Due sole dimensioni, *data* (asse orizzontale) e *computer* (asse verticale): *digital* è il punto **[1683, 1670]** (freccia verde), *information* il punto **[3982, 3325]** (freccia blu).

- Le due frecce puntano quasi nella **stessa direzione**: angolo di circa 4,9° (verificato: $\cos = 0{,}9963$). È questo che misurerà il coseno.
- *information* è più frequente, quindi la sua freccia è più **lunga**: circa 5188 contro 2370. La lunghezza riflette la **frequenza**, non il significato.

Da qui la scelta della misura: due parole con lo stesso uso ma frequenze diverse devono risultare simili, quindi si deve guardare la direzione e ignorare la lunghezza.

<a id="p-24"></a>

### Slide 24 · Il prodotto scalare

$$\text{dot}(\mathbf v,\mathbf w) = \mathbf v\cdot\mathbf w = \sum_{i=1}^{N} v_i w_i = v_1w_1 + v_2w_2 + \dots + v_Nw_N$$

- Detto anche **prodotto interno** (*inner product*): somma dei prodotti delle componenti corrispondenti.
- È **alto** quando i due vettori hanno valori grandi **nelle stesse dimensioni**: per i conteggi, quando le due parole hanno molti contesti in comune.
- È **0** per vettori **ortogonali**, che hanno gli zeri in dimensioni diverse (nessun contesto in comune): forte dissimilarità.

Esempio: $\mathbf v = [1, 3]$, $\mathbf w = [3;\ 1{,}6]$: $1\cdot 3 + 3\cdot 1{,}6 = 7{,}8$. Sulle quattro finestre (scheda 19): dot(cherry, strawberry) = 2, dot(digital, information) = 1, dot(cherry, digital) = 0.

È la stessa operazione della somma pesata $\mathbf w\cdot\mathbf x$ della regressione logistica ([L6](L06-regressione-logistica.md#p-20)).

<a id="p-25"></a>

### Slide 25 · Lunghezza di un vettore e bias della frequenza

$$|\mathbf v| = \sqrt{\sum_{i=1}^{N} v_i^2}$$

La **lunghezza** (norma euclidea): radice della somma dei quadrati.

**Bias della frequenza**: le parole frequenti hanno vettori più lunghi, perché co-occorrono con più parole e con conteggi più alti. Il prodotto scalare cresce con la lunghezza, quindi **favorisce le parole frequenti**. Il grafico a destra lo mostra: $\mathbf v = [1, 3]$, $\mathbf w = [3;\ 1{,}6]$ e $2\mathbf w$ (freccia rossa, stessa direzione, doppia lunghezza). dot($\mathbf v$, $\mathbf w$) = 7,8, dot($\mathbf v$, $2\mathbf w$) = 15,6, ma l'angolo $\theta$ è lo stesso: $\cos\theta = 0{,}73$ per entrambi (verificato: $7{,}8/(\sqrt{10}\cdot\sqrt{11{,}56}) = 0{,}725$, angolo di 43,5°).

Vogliamo una similarità che non dipenda dalla frequenza. In generale $\text{dot}(c\mathbf v, \mathbf w) = c\,\text{dot}(\mathbf v, \mathbf w)$ (esercizio 5c): una parola che compare 10 volte più spesso negli stessi contesti avrebbe un prodotto scalare 10 volte più grande. Nel notebook (cella 10) la correlazione fra log-frequenza e log-lunghezza delle righe è 0,98.

<a id="p-26"></a>

### Slide 26 · Il coseno come prodotto scalare normalizzato

$$\mathbf a\cdot\mathbf b = |\mathbf a||\mathbf b|\cos\theta \qquad\Longrightarrow\qquad \frac{\mathbf a\cdot\mathbf b}{|\mathbf a||\mathbf b|} = \cos\theta$$

- Si divide il prodotto scalare per le **lunghezze** dei due vettori.
- Il risultato è il **coseno dell'angolo** $\theta$ fra i due vettori: dipende solo dalla direzione.
- Per **vettori unitari** (lunghezza 1) il prodotto scalare *è* il coseno. Il grafico a destra mostra $\mathbf v/|\mathbf v|$ e $\mathbf w/|\mathbf w|$ sulla circonferenza unitaria, con l'angolo $\theta$ fra loro.

Conseguenza pratica: si possono normalizzare tutti i vettori **una volta** (dividendo per la lunghezza) e poi confrontarli con semplici prodotti scalari, cioè un prodotto matrice-vettore. È ciò che fa un motore di ricerca (esercizio 7 della scheda) e il calcolo dei vicini nel notebook.

<a id="p-27"></a>

### Slide 27 · La similarità coseno

$$\text{cosine}(\mathbf v,\mathbf w) = \frac{\mathbf v\cdot\mathbf w}{|\mathbf v||\mathbf w|} = \frac{\sum_{i=1}^{N} v_iw_i}{\sqrt{\sum_{i=1}^{N} v_i^2}\,\sqrt{\sum_{i=1}^{N} w_i^2}}$$

**Intervallo**:

- 1 per vettori con la **stessa direzione** (anche di lunghezze diverse);
- 0 per vettori **ortogonali**;
- $-1$ per direzioni **opposte**.

I conteggi grezzi sono **non negativi**: tutti i vettori stanno nello stesso "quadrante" generalizzato, l'angolo fra due di loro è al massimo 90° e il coseno va da 0 a 1. Coseni negativi compaiono solo con vettori a valori di segno qualsiasi, come gli embedding densi.

Invarianza alla scala (esercizio 5 della scheda): per $c&gt;0$, $\cos(c\mathbf v,\mathbf w) = \dfrac{c\,\mathbf v\cdot\mathbf w}{c|\mathbf v||\mathbf w|} = \cos(\mathbf v,\mathbf w)$. È proprio la proprietà che mancava al prodotto scalare.

> **Da saper fare: Calcolare un coseno a mano**
>
> Tre passi: (1) prodotto scalare, (2) le due lunghezze, (3) il rapporto. Con le quattro finestre: cos(cherry, strawberry) $= \dfrac{1\cdot0+0\cdot0+1\cdot2}{\sqrt2\cdot2} = \dfrac{2}{2{,}828} = 0{,}707$; cos(cherry, information) $= \dfrac{1}{\sqrt2\sqrt2} = 0{,}5$; cos(digital, information) $= \dfrac{1}{1\cdot\sqrt2} = 0{,}707$. Il prodotto scalare metteva cherry-strawberry (2) davanti a digital-information (1); il coseno li mette alla pari, perché *strawberry* ha il vettore più lungo (esercizio 6).

<a id="p-28"></a>

### Slide 28 · Il coseno: un esempio

|  | pie | data | computer |
| --- | --- | --- | --- |
| cherry | 442 | 8 | 2 |
| digital | 5 | 1683 | 1670 |
| information | 5 | 3982 | 3325 |

$$\cos(\text{cherry},\text{information}) = \frac{442\cdot5+8\cdot3982+2\cdot3325}{\sqrt{442^2+8^2+2^2}\,\sqrt{5^2+3982^2+3325^2}} = \frac{40{.}716}{442{,}08\cdot 5187{,}7} = 0{,}018$$
$$\cos(\text{digital},\text{information}) = \frac{5\cdot5+1683\cdot3982+1670\cdot3325}{\sqrt{5^2+1683^2+1670^2}\,\sqrt{5^2+3982^2+3325^2}} = \frac{12{.}254{.}481}{2371{,}0\cdot5187{,}7} = 0{,}996$$

Tre dimensioni della tabella di Wikipedia. *cherry* e *information* sono quasi **ortogonali** (0,018), *digital* e *information* quasi nella **stessa direzione** (0,996): il modello decide che *information* è molto più vicina a *digital* che a *cherry*, un risultato sensato. Tutti i numeri verificati con numpy (e nella cella 4 del notebook).

Si noti che il prodotto scalare grezzo cherry-information (40.716) non è piccolo in assoluto: sono le lunghezze a mostrare che è minuscolo rispetto a ciò che i due vettori potrebbero dare.

<a id="p-29"></a>

### Slide 29 · Coseno e angoli

Figura 5.5 del libro, che il libro stesso chiama "approssimativa" (*rough*, non in scala): i tre vettori nello spazio di due conteggi, *pie* (asse verticale, dimensione 1) e *computer* (asse orizzontale, dimensione 2). *cherry* punta quasi in verticale (molto *pie*, quasi niente *computer*); *digital* e *information* quasi in orizzontale, con *information* più lunga. Gli archi verdi marcano gli angoli.

- L'angolo fra *digital* e *information* è **molto più piccolo** di quello fra *cherry* e *information* (su queste due dimensioni: circa 0° contro quasi 90°).
- Il coseno è **massimo, 1, quando l'angolo è minimo, 0°**, e decresce quando l'angolo cresce: più simili = coseno più grande = angolo più piccolo.
- La **lunghezza** dei vettori, cioè la frequenza delle parole, non conta.

<a id="p-30"></a>

### Slide 30 · A che cosa serve il coseno

Stessa figura; la novità sono gli usi.

- **Vicini più prossimi**: le 10 parole più simili a una parola target $w$ si trovano calcolando il coseno fra $w$ e le altre $|V|-1$ parole, ordinando e prendendo le prime 10. È la funzione `neighbors` del notebook (cella 8).
- **Parafrasi**: trovare parole o espressioni intercambiabili.
- **Cambiamento di significato** nel tempo: confrontare il vettore della stessa parola in corpora di epoche diverse (§5.7.1, prossima lezione).
- **Significati in corpora diversi**: la stessa parola in domini diversi (*mouse* in un corpus di biologia o di informatica).

Sui conteggi grezzi i vicini sono spesso deludenti: nel notebook i vicini di *file* sono *with, and, in, from*, cioè le parole che co-occorrono con tutto. È il motivo per cui dopo la pausa si pesano i conteggi.

<a id="p-31"></a>
**Slide 31 · Pausa** — Pausa di 10 minuti; dopo la pausa: documenti come vettori e due modi di pesare i conteggi.

## Documenti come vettori: tf-idf

<a id="p-32"></a>
**Slide 32 · Documenti come vettori: tf-idf** — Quarto blocco: contare le parole di un documento; nello schema è evidenziata la riga dei documenti, matrice termine-documento e tf-idf ("you are here").

<a id="p-33"></a>

### Slide 33 · Un documento come bag of words

Il **vector space model** dell'information retrieval (**Salton, 1971**): un documento è un **vettore dei conteggi delle parole** che contiene. La figura: una recensione (*I love this movie! It's sweet, but with satirical humor...*) finisce in un sacchetto in cui le parole sono mescolate, e ne esce una tabella parola-conteggio.

- È il **bag of words**: la **posizione** delle parole si butta, resta solo la **frequenza**. *it* compare 6 volte, *I* 5, *the* 4, *and* e *to* 3, *seen* 2, *love, recommend, movie* una volta.
- Sulle 18 dimensioni della tabella (*adventure, and, fairy, genre, great, have, humor, I, it, satirical, seen, sweet, the, times, to, whimsical, would, yet*, in ordine alfabetico) il documento è $[1\ 3\ 1\ 1\ 1\ 1\ 1\ 5\ 6\ 1\ 2\ 1\ 4\ 1\ 3\ 1\ 1\ 1]$; in realtà ha una componente per ogni parola dell'inglese, quasi tutte 0.

Ho ricontato sul testo della recensione: *it* 6 (contando *It's*), *I* 5 (con *I've* e *I'm*), *the* 4: la slide è giusta. Il testo del libro (§11.1.1) scrive invece "*it* occurred 5 times", in contraddizione con la sua stessa figura che dice 6: refuso del libro, non della slide.

È la stessa rappresentazione usata da Naive Bayes e dalla regressione logistica con le parole come feature ([L6](L06-regressione-logistica.md#p-15)): lì serviva per classificare, qui per confrontare documenti.

<a id="p-34"></a>

### Slide 34 · La matrice termine-documento

|  | As You Like It | Twelfth Night | Julius Caesar | Henry V |
| --- | --- | --- | --- | --- |
| battle | 1 | 0 | 7 | 13 |
| good | 114 | 80 | 62 | 89 |
| fool | 36 | 58 | 1 | 4 |
| wit | 20 | 15 | 2 | 3 |

La **matrice termine-documento** (*term-document matrix*): **righe = parole del vocabolario**, **colonne = documenti** della collezione. Ogni cella è il numero di volte che la parola della riga compare nel documento della colonna: *fool* compare **58 volte** in *Twelfth Night*.

In generale ha $|V|$ righe e una colonna per documento ($|D|$ colonne). Qui quattro parole e quattro opere di Shakespeare: due commedie (*As You Like It*, *Twelfth Night*) e due drammi storici/tragedie (*Julius Caesar*, *Henry V*). Rispetto alla matrice parola-contesto cambia solo il "contesto": non le parole vicine, ma il **documento intero**.

<a id="p-35"></a>

### Slide 35 · Documenti come vettori colonna

Stessa tabella, con le colonne riquadrate in rosso: ogni documento è un **vettore colonna** di lunghezza 4 (di lunghezza $|V|$ in realtà).

- *As You Like It* = [1, 114, 36, 20], *Twelfth Night* = [0, 80, 58, 15], *Julius Caesar* = [7, 62, 1, 2], *Henry V* = [13, 89, 4, 3] (ordine: battle, good, fool, wit).
- Le due commedie hanno valori simili, 1 e 0, sulla prima dimensione (quante volte compare *battle*).

Il principio: **documenti simili contengono parole simili**, e documenti con parole simili hanno vettori colonna simili. Simmetricamente, le **righe** della stessa matrice sono vettori di parole: due parole sono simili se compaiono negli stessi documenti (lo riprende la scheda 46).

<a id="p-36"></a>

### Slide 36 · Le quattro opere nello spazio

La figura (Fig. 11.5 del libro) usa due delle quattro dimensioni: *fool* sull'asse orizzontale e *battle* su quello verticale; le coordinate sono scritte come [fool, battle]. *Twelfth Night* [58, 0] e *As You Like It* [36, 1] sono frecce quasi orizzontali e lunghe; *Henry V* [4, 13] e *Julius Caesar* [1, 7] frecce corte quasi verticali. (L'etichetta 40 in cima all'asse verticale, dopo 5, 10, 15 a passo costante, è un refuso della figura del libro: la scala prosegue con 20.)

- Le commedie hanno valori alti di *fool* e bassi di *battle*; *Julius Caesar* ed *Henry V* il contrario.
- *As You Like It* e *Twelfth Night* si somigliano fra loro (più buffoni e spirito che battaglie) molto più di quanto somiglino a *Julius Caesar* o *Henry V*. Su queste due dimensioni i coseni lo confermano: 0,9996 fra le due commedie, 0,17 fra *As You Like It* e *Julius Caesar*.

Sotto, i vettori completi a quattro dimensioni, in blu le commedie e in rosso le altre due: la slide seguente mostra che cosa succede quando si usano tutte e quattro le dimensioni.

<a id="p-37"></a>

### Slide 37 · Sui conteggi grezzi i coseni dicono altro

Stessa figura; ma sui **quattro conteggi grezzi** i coseni sono:

- cos(As You Like It, Twelfth Night) = **0,950**;
- cos(As You Like It, Julius Caesar) = **0,945** (la slide arrotonda a 0,94).

Le due commedie risultano appena più simili fra loro che a una tragedia. Il motivo è *good*: 114, 80, 62 e 89 occorrenze, cioè **una parola frequente che compare in ogni opera domina ogni vettore**. Nel prodotto scalare As You Like It · Twelfth Night = 11.508, il termine di *good* vale $114\cdot80 = 9120$ (79%); in As You Like It · Julius Caesar = 7151 vale $114\cdot62 = 7068$ (99%). Tutti i vettori puntano più o meno nella direzione di *good*, quindi tutti i coseni sono alti.

Verifica: togliendo la riga *good* i coseni diventano 0,968 (commedie) e 0,274 (commedia-tragedia). Serve un modo sistematico per abbassare il peso di parole come *good*: è il term weighting.

<a id="p-38"></a>

### Slide 38 · Term weighting

In information retrieval i conteggi grezzi diventano **pesi dei termini** (*term weights*): **tf-idf** o la sua variante **BM25**. Due ingredienti:

- **Term frequency** (tf): quanto è frequente una parola **nel documento**. Le parole che compaiono più spesso in un documento probabilmente ne dicono il contenuto. Ma non in modo lineare: da qui il **logaritmo**.
- **Document frequency** (df): in **quanti documenti** compare la parola. I termini presenti in pochi documenti aiutano a distinguere quei documenti dal resto della collezione; quelli presenti dappertutto, come *good*, servono poco.

**tf-idf** = *term frequency – inverse document frequency*, il prodotto dei due (il trattino è un trattino, non un meno). La prima componente guarda dentro il documento, la seconda guarda la collezione.

> **Approfondimento: BM25 (facoltativo, §11.1.3 del libro)**
>
> $$\text{score}(q,d) = \sum_{t\in q}\log\frac{N}{\text{df}_t}\cdot\frac{\text{tf}_{t,d}}{k\left(1-b+b\frac{|d|}{|d_{avg}|}\right)+\text{tf}_{t,d}}$$ Due parametri: $k$ regola quanto conta la frequenza del termine (con $k = 0$ conta solo la presenza; con $k$ grande torna la frequenza grezza) e fa saturare il contributo di un termine ripetuto; $b$ regola la normalizzazione per la lunghezza del documento ($b = 1$ piena, $b = 0$ nessuna). Valori tipici $k\in[1{,}2;\ 2]$, $b = 0{,}75$. Il libro nota anche che le **stop list** (elenchi di parole funzionali da eliminare, come *the, a, to*) sono oggi poco usate in IR perché l'idf già abbassa il peso delle parole funzionali.

<a id="p-39"></a>

### Slide 39 · Term frequency

$$\text{tf}_{t,d} = \begin{cases}1+\log_{10}\text{count}(t,d) & \text{se count}(t,d)&gt;0\\ 0 & \text{altrimenti}\end{cases}$$

- $\text{count}(t,d)$ è il **conteggio grezzo**: quante volte il termine $t$ compare nel documento $d$.
- Si usa il suo $\log_{10}$ più uno: una parola che compare 100 volte non rende il documento 100 volte più rilevante.
- **Conteggi nulli**: il logaritmo di 0 non esiste, quindi un termine assente ha tf = 0 per definizione (il caso separato della formula).

Il "+1" serve a distinguere la presenza singola dall'assenza: con $\log_{10}$ soltanto, un conteggio 1 darebbe 0 come un conteggio 0. Il libro cita in nota una variante usata nelle edizioni precedenti, $\text{tf} = \log_{10}(\text{count}+1)$, che risolve lo stesso problema in un altro modo. È la stessa idea della [scala logaritmica per i conteggi](L06-regressione-logistica.md#p-32) vista come scaling delle feature nella L6.

<a id="p-40"></a>

### Slide 40 · Term frequency: la crescita logaritmica

| count | 0 | 1 | 10 | 100 | 1000 |
| --- | --- | --- | --- | --- | --- |
| tf | 0 | 1 | 2 | 3 | 4 |

Ogni **fattore 10** nel conteggio aggiunge **1** al peso. Il grafico a destra mostra la curva $1+\log_{10}x$ per conteggi da 1 a 1000, con i quattro punti 1→1, 10→2, 100→3, 1000→4: sale ripida all'inizio e poi si appiattisce.

Valori della tabella delle opere (verificati): *battle* 7 volte → $1+\log_{10}7 = 1{,}845$; 13 volte → 2,114; *good* 114 volte → 3,057. La frequenza grezza di *good* in *As You Like It* è 114 volte quella di *battle*, la tf solo 3 volte. Il logaritmo da solo, però, non elimina il problema di *good*: la scheda 60 lo chiama esplicitamente il problema che resta dopo la tf.

<a id="p-41"></a>

### Slide 41 · Document frequency e idf

$$\text{idf}_t = \log_{10}\frac{N}{\text{df}_t}$$

- $\text{df}_t$, **document frequency**: il numero di documenti in cui il termine $t$ compare (non quante volte: un documento conta una volta sola).
- $N$: il numero di documenti della collezione. L'idf è di **Sparck Jones (1972)**.
- Meno documenti contengono il termine, **più alto** il peso: massimo $\log_{10}N$ per un termine in un solo documento.
- **0** per un termine che compare in **tutti** i documenti ($N/N = 1$).

Attenzione alla differenza fra df e frequenza totale: *good* potrebbe comparire 100 volte in un solo documento e avere df = 1; quel che conta per l'idf è quanto la parola è **sparsa nella collezione**. Il logaritmo, anche qui, smorza: con $N = 37$, df = 1 contro df = 2 vale 1,57 contro 1,27, non il doppio.

<a id="p-42"></a>

### Slide 42 · L'idf in Shakespeare

| parola | df | idf |
| --- | --- | --- |
| Romeo | 1 | 1,57 |
| salad | 2 | 1,27 |
| Falstaff | 4 | 0,967 (esatto 0,966) |
| forest | 12 | 0,489 |
| battle | 21 | 0,246 |
| wit | 34 | 0,037 |
| fool | 36 | 0,012 |
| good | 37 | 0 |
| sweet | 37 | 0 |

Collezione delle **37 opere** di Shakespeare; il grafico a barre mostra $\log_{10}(37/\text{df})$ per nove parole. *Romeo* compare in una sola opera: $\log_{10}(37/1) = 1{,}57$, la parola più informativa. *battle* in 21 opere: 0,246; *fool* in 36: 0,012. *good* e *sweet* compaiono in tutte e 37: idf 0, **completamente non discriminanti** (il libro nota che *sweet* era uno degli aggettivi preferiti di Shakespeare).

Osservazione che tornerà nell'esercizio 8: *fool* e *wit*, che a occhio distinguono le commedie, hanno idf quasi nullo perché compaiono in quasi tutte le opere. L'idf misura la rarità nella collezione, non la capacità di separare due gruppi scelti da noi.

> **Attenzione (errore nelle slide): idf di Falstaff: 0,966, non 0,967**
>
> $\log_{10}(37/4) = \log_{10}9{,}25 = 0{,}96614$, che arrotondato a tre decimali è **0,966**. La slide (barra e tabella) riporta 0,967, copiando la tabella del libro (§11.1.2), che ha lo stesso arrotondamento sbagliato. Differenza irrilevante per i concetti; gli altri otto valori sono esatti. Verifica: `math.log10(37/4)` = 0,966142.

<a id="p-43"></a>

### Slide 43 · tf-idf

$$\text{tf-idf}(t,d) = \text{tf}_{t,d}\cdot\text{idf}_t$$

|  | As You Like It | Twelfth Night | Julius Caesar | Henry V |
| --- | --- | --- | --- | --- |
| battle | 0,246 | 0 | 0,454 | 0,520 |
| good | 0 | 0 | 0 | 0 |
| fool | 0,031 | 0,033 | 0,012 | 0,019 |
| wit | 0,085 | 0,081 | 0,048 | 0,055 |

Il peso tf-idf della parola $t$ nel documento $d$ è il prodotto della term frequency (locale al documento) per l'inverse document frequency (globale sulla collezione). Alto quando la parola è **frequente in questo documento e rara negli altri**. La tabella è la matrice termine-documento delle quattro opere, pesata.

> **Da saper fare: Ricalcolare la tabella**
>
> Con df = 21, 37, 36, 34 per battle, good, fool, wit e $N = 37$: tf di *fool* in *As You Like It* = $1+\log_{10}36 = 2{,}556$, per idf 0,012 dà 0,031. Tutti i valori della tabella tornano usando gli idf **arrotondati** del libro (0,246; 0,012; 0,037). Con gli idf esatti (0,0119 e 0,0367) tre celle cambiano alla terza cifra: fool/As You Like It 0,030, wit/Twelfth Night 0,080, wit/Henry V 0,054. Non è un errore, è la convenzione della tabella: all'esame dichiarare quale idf si usa.

<a id="p-44"></a>

### Slide 44 · La matrice pesata

Stessa tabella; la novità sono i commenti.

- *battle* in *Julius Caesar*: $(1+\log_{10}7)\times0{,}246 = 1{,}845\times0{,}246 = 0{,}454$. In *Henry V*: $(1+\log_{10}13)\times0{,}246 = 2{,}114\times0{,}246 = 0{,}520$.
- *good*, presente in ogni opera, pesa **0 ovunque** e non distingue più le opere: il problema della scheda 37 è sparito.
- *fool* e *wit* mantengono pesi piccoli: compaiono in quasi tutte le opere (df 36 e 34).

Effetto sui coseni (calcolato, esercizio 8d): con tf-idf su queste quattro parole cos(As You Like It, Julius Caesar) = 0,970 e cos(As You Like It, Twelfth Night) = 0,345. Le due commedie risultano **meno** simili di prima: rimosso *good*, l'unica dimensione con un peso sostanziale è *battle*, che *As You Like It* contiene (una volta) e *Twelfth Night* no. Su quattro dimensioni tf-idf non può funzionare; su un vocabolario vero (migliaia di parole, nomi di personaggi, luoghi) le parole rare e caratteristiche fanno il lavoro.

<a id="p-45"></a>

### Slide 45 · tf-idf in information retrieval

- **Documenti**: un'opera, un articolo di Wikipedia, una pagina web. Per tf-idf un documento può essere qualunque unità di testo: spesso **ogni paragrafo** è un documento (il libro, cap. 11, parla di *passage*).
- **Query**: la richiesta dell'utente è trattata come un **documento corto**, un vettore nello stesso spazio $|V|$-dimensionale, pesato nello stesso modo (tf della query per idf della collezione).

Il compito si chiama **ad hoc retrieval**: data una query, restituire i documenti della collezione ordinati per rilevanza. L'architettura del libro (Fig. 11.1): i documenti sono indicizzati una volta (vettori tf-idf, più un **indice invertito** che per ogni termine elenca i documenti che lo contengono), la query è trasformata in vettore al momento, e si calcola un punteggio per ogni documento candidato.

<a id="p-46"></a>

### Slide 46 · Il punteggio: il coseno fra query e documento

$$\text{score}(q,d) = \cos(\mathbf q,\mathbf d) = \frac{\mathbf q\cdot\mathbf d}{|\mathbf q||\mathbf d|}$$

- La **rilevanza** di un documento per la query è il coseno dei due vettori.
- Ipotesi semplificatrice: documenti con parole simili a quelle della query sono più rilevanti.
- Una query con *battle* mette al primo posto *Julius Caesar* ed *Henry V*. Il grafico a destra mostra la query lungo l'asse *battle* e i quattro documenti come vettori unitari nel piano (battle, fool), con i coseni scritti accanto.

Le stesse matrici servono a due scopi: il **significato di una parola** è una riga, il **contenuto di un documento** è una colonna.

Esempio del libro (§11.1.3, esercizio 9): query *sweet love* e quattro nano-documenti; Doc 1 (*sweet sweet nurse love*) ha coseno 0,747, Doc 2 (*sweet sorrow*) 0,078.

> **Approfondimento: I coseni della figura sono calcolati sui conteggi grezzi**
>
> I numeri del grafico (Twelfth Night 0,00, As You Like It 0,03, Henry V 0,96, Julius Caesar 0,99) sono i coseni fra la query *battle* e i **conteggi grezzi** ridotti alle due dimensioni (battle, fool): $1/\sqrt{1^2+36^2} = 0{,}028$, $0/58 = 0$, $13/\sqrt{13^2+4^2} = 0{,}956$, $7/\sqrt{7^2+1^2} = 0{,}990$. Anche le direzioni delle frecce sono quelle dei conteggi grezzi (As You Like It quasi verticale, lungo *fool*). Con i vettori **tf-idf** della scheda 43, su tutte e quattro le parole, i coseni con la query sono: Julius Caesar 0,994, Henry V 0,994, **As You Like It 0,939**, Twelfth Night 0. La figura è un'illustrazione in due dimensioni, non un errore: l'ordinamento della slide (prima Julius Caesar ed Henry V) resta vero anche con tf-idf, ma con tf-idf *As You Like It* è quasi alla pari, perché con *good* azzerato e *fool* quasi azzerato il suo vettore è dominato dall'unica occorrenza di *battle*. Verificato con numpy (idf esatti; con quelli arrotondati del libro i valori sono gli stessi alla terza cifra).

## PMI e PPMI

<a id="p-47"></a>
**Slide 47 · Pesare le co-occorrenze: PPMI** — Quinto blocco: associazione invece di frequenza; nello schema è evidenziata la riga delle parole, la pesatura PPMI della matrice parola-contesto.

<a id="p-48"></a>

### Slide 48 · Pointwise mutual information

**La frequenza grezza è una cattiva misura di associazione**: *the* co-occorre con tutto. Nella matrice parola-contesto le colonne *the*, *of*, *and* hanno i conteggi più alti per quasi ogni parola, e il coseno sui conteggi ne è dominato (i vicini *with, and, in* di *file* nel notebook).

$$\text{PMI}(w,c) = \log_2\frac{P(w,c)}{P(w)P(c)}$$

- **Numeratore**: quanto spesso abbiamo **osservato** la parola target $w$ con la parola di contesto $c$.
- **Denominatore**: quanto spesso le due co-occorrerebbero **per caso**, se fossero indipendenti ($P(w,c) = P(w)P(c)$ sotto indipendenza).
- Il rapporto dice **quante volte più del caso** compaiono insieme; il $\log_2$ lo esprime in **bit**, come l'entropia della [L5](L05-smoothing-ed-entropia.md#p-31).

La formula generale fra due eventi $x$ e $y$ è attribuita a Fano (1961); Church e Hanks (1989) la applicarono alle associazioni fra parole.

> **Approfondimento: PMI e mutual information**
>
> La slide intitola *mutual information* la formula $I(x,y) = \log_2\frac{P(x,y)}{P(x)P(y)}$ fra due **eventi** $x$ e $y$: è la versione **puntuale** (pointwise), ed è così che la chiama il libro. La **mutual information** vera e propria è fra due **variabili aleatorie** ed è la media della PMI su tutte le coppie: $I(X;Y) = \sum_{x,y}P(x,y)\log_2\frac{P(x,y)}{P(x)P(y)}$. La MI è sempre $\ge 0$ (è zero solo se $X$ e $Y$ sono indipendenti); la PMI di una singola coppia può essere negativa. All'orale: PMI = una cella, MI = tutta la tabella.

<a id="p-49"></a>

### Slide 49 · PMI: positiva, nulla, negativa

La retta della slide colloca tre coppie della tabella di Wikipedia:

- **cherry, computer: $-6{,}7$**, molto meno del caso (zona rossa);
- **information, data: 0,09**, praticamente il caso (vicino allo 0);
- **cherry, pie: 4,38**, molto più del caso (zona blu): $2^{4{,}38}\approx 21$ volte più spesso di quanto previsto dall'indipendenza.

Regola di lettura: **0** se le due parole co-occorrono quanto previsto dal caso; **positiva** se più spesso, **negativa** se meno spesso. La PMI è uno strumento per trovare parole **fortemente associate** (collocazioni come *New York*, *strong tea*). Valori verificati sulla tabella della scheda 52: $-6{,}695$; 0,0944; 4,379.

<a id="p-50"></a>

### Slide 50 · Positive PMI: perché scartare i valori negativi

$$\text{PPMI}(w,c) = \max\left(\log_2\frac{P(w,c)}{P(w)P(c)},\ 0\right)$$

- **Intervallo**: la PMI va da $-\infty$ (coppia mai osservata: $\log 0$) a $+\infty$.
- **Valori negativi**: dire che due parole co-occorrono **meno** del caso è inaffidabile, a meno di avere un corpus enorme. Esempio: se $P(w) = P(c) = 10^{-6}$, sotto indipendenza $P(w,c) = 10^{-12}$; per stabilire che la frequenza osservata è **significativamente** più bassa di un caso su mille miliardi servirebbero ben più di $10^{12}$ coppie.

Inoltre non è chiaro che le associazioni "negative" siano giudizi che gli esseri umani sanno dare ("*quanto è poco associata* questa parola a quest'altra?"). Quindi si tiene solo la parte positiva.

<a id="p-51"></a>

### Slide 51 · PPMI: i valori negativi diventano 0

Stessa formula; la retta ora mostra l'effetto: *cherry, computer* ($-6{,}7$, cerchio vuoto) viene spostato a **0** (freccia rossa); *information, data* (0,09) e *cherry, pie* (4,38) restano dove sono.

- Sostituire i valori negativi con 0 è la **positive pointwise mutual information**, PPMI (**Niwa e Nitta, 1994**).
- Anche i **conteggi nulli**, il cui log sarebbe $-\infty$, diventano 0: la matrice PPMI ha zeri almeno dove li aveva la matrice dei conteggi, quindi resta **sparsa**.

Da notare: dopo la PPMI la stessa cella 0 significa due cose diverse ("mai visti insieme" e "visti insieme meno del caso"). Per il coseno va bene: in entrambi i casi la coppia non contribuisce alla somiglianza.

<a id="p-52"></a>

### Slide 52 · PPMI da una matrice parola-contesto: le probabilità

|  | computer | data | result | pie | sugar | count(w) |
| --- | --- | --- | --- | --- | --- | --- |
| cherry | 2 | 8 | 9 | 442 | 25 | 486 |
| strawberry | 0 | 0 | 1 | 60 | 19 | 80 |
| digital | 1670 | 1683 | 85 | 5 | 4 | 3447 |
| information | 3325 | 3982 | 378 | 5 | 13 | 7703 |
| count(context) | 4997 | 5673 | 473 | 512 | 61 | 11716 |

$f_{ij}$ è il numero di volte che la parola $w_i$ compare con il contesto $c_j$: i conteggi di Wikipedia di prima della pausa (senza *aardvark*), con i totali di riga e di colonna. La somma di tutte le celle è **11.716** (somme verificate).

$$p_{ij} = \frac{f_{ij}}{\sum_{i'=1}^{W}\sum_{j'=1}^{C}f_{i'j'}},\qquad p_{i*} = \frac{\sum_{j=1}^{C}f_{ij}}{\sum_{i'}\sum_{j'}f_{i'j'}},\qquad p_{*j} = \frac{\sum_{i=1}^{W}f_{ij}}{\sum_{i'}\sum_{j'}f_{i'j'}}$$

Probabilità congiunta = cella / totale; marginale della parola = totale di riga / totale; marginale del contesto = totale di colonna / totale. Sono stime a **massima verosimiglianza**, frequenze relative come per gli n-gram ([L4](L04-modelli-linguistici-n-gram.md#p-13)). $W$ è il numero di parole (righe), $C$ di contesti (colonne). Qui le marginali sono calcolate sulla sola sotto-tabella 4 × 5: in una matrice vera i totali includerebbero tutte le $|V|$ colonne, e i valori di PPMI sarebbero diversi. È un esempio didattico.

<a id="p-53"></a>

### Slide 53 · La PPMI di una cella

$$\text{PPMI}_{ij} = \max\left(\log_2\frac{p_{ij}}{p_{i*}\,p_{*j}},\ 0\right)$$

Stessa tabella dei conteggi; la PPMI di una cella è il logaritmo del rapporto fra la probabilità congiunta della cella e il prodotto delle probabilità della sua riga e della sua colonna, e 0 se il logaritmo è negativo.

Forma comoda per i conti a mano: i tre denominatori $N$ in parte si semplificano,

$$\frac{p_{ij}}{p_{i*}p_{*j}} = \frac{f_{ij}/N}{(f_{i*}/N)(f_{*j}/N)} = \frac{f_{ij}\cdot N}{f_{i*}\cdot f_{*j}}$$

cioè **conteggio osservato** diviso **conteggio atteso** sotto indipendenza, $f_{i*}f_{*j}/N$. Esempio: cherry-pie atteso $486\cdot512/11716 = 21{,}2$, osservato 442, rapporto 20,8, $\log_2 20{,}8 = 4{,}38$. Lavorare con i conteggi interi evita gli errori di arrotondamento delle probabilità a quattro decimali (vedi scheda 54).

<a id="p-54"></a>

### Slide 54 · PPMI: un esempio svolto

$$P(w{=}\text{information}, c{=}\text{data}) = \frac{3982}{11716} = 0{,}3399\qquad P(w{=}\text{information}) = \frac{7703}{11716} = 0{,}6575\qquad P(c{=}\text{data}) = \frac{5673}{11716} = 0{,}4842$$
$$\text{PPMI}(\text{information},\text{data}) = \log_2\frac{0{,}3399}{0{,}6575\cdot0{,}4842} = \log_2 1{,}068 = 0{,}0944$$

*information* e *data* co-occorrono solo un po' più di quanto preveda il caso, perché **entrambe sono frequenti**: attese per caso $7703\cdot5673/11716 = 3730$ co-occorrenze, osservate 3982. Una PMI positiva ma piccola, **0,0944 bit**, nonostante sia il conteggio più alto della tabella.

Secondo esempio: *cherry* e *computer* co-occorrono molto meno del caso, solo 2 volte nella tabella, contro $486\cdot4997/11716 = 207$ attese: PMI negativa, sostituita da 0.

> **Attenzione (errore nelle slide): pmi(cherry, computer) = −6,70, non −6,47**
>
> La riga in rosso calcola $\log_2(0{,}0002/(0{,}0415\times0{,}4265)) = -6{,}47$. Il valore $0{,}0002$ è la probabilità congiunta $2/11716 = 0{,}000171$ arrotondata a quattro decimali: l'arrotondamento la gonfia del 17%, abbastanza da spostare il logaritmo di 0,23. Con i valori esatti: $\log_2\frac{2\cdot11716}{486\cdot4997} = \log_2 0{,}00965 = -6{,}70$, che è anche il valore delle schede 49 e 51 ($-6{,}7$) e dell'Appendice J. La conclusione non cambia (PPMI = 0). Verificato con numpy; la cella 18 del notebook stampa `pmi(cherry, computer) = -6.7` e il suo testo segnala lo stesso arrotondamento.

<a id="p-55"></a>

### Slide 55 · Dalle probabilità alla PPMI

| p(w, context) | computer | data | result | pie | sugar | p(w) |
| --- | --- | --- | --- | --- | --- | --- |
| cherry | 0,0002 | 0,0007 | 0,0008 | 0,0377 | 0,0021 | 0,0415 |
| strawberry | 0,0000 | 0,0000 | 0,0001 | 0,0051 | 0,0016 | 0,0068 |
| digital | 0,1425 | 0,1436 | 0,0073 | 0,0004 | 0,0003 | 0,2942 |
| information | 0,2838 | 0,3399 | 0,0323 | 0,0004 | 0,0011 | 0,6575 |
| p(context) | 0,4265 | 0,4842 | 0,0404 | 0,0437 | 0,0052 |  |

Ogni conteggio diviso per 11.716 dà le **probabilità congiunte**; le **marginali** sono $p(w)$ nella colonna di destra e $p(\text{context})$ nella riga in basso (ogni marginale è la somma della sua riga o colonna, e tutte le congiunte sommano a 1). Sotto, già visibile, la matrice PPMI (scheda seguente). Valori verificati con numpy.

Gli "0,0000" di *strawberry* sono veri zeri (conteggio 0), non arrotondamenti; lo 0,0002 di cherry-computer invece è 0,000171 arrotondato, ed è l'origine dell'errore della scheda 54.

<a id="p-56"></a>

### Slide 56 · La matrice PPMI

| PPMI | computer | data | result | pie | sugar |
| --- | --- | --- | --- | --- | --- |
| cherry | 0 | 0 | 0 | 4,38 | 3,30 |
| strawberry | 0 | 0 | 0 | 4,10 | 5,51 |
| digital | 0,18 | 0,01 | 0 | 0 | 0 |
| information | 0,02 | 0,09 | 0,28 | 0 | 0 |

- *cherry* e *strawberry* sono **fortemente associate** a *pie* e *sugar* (fino a 5,51 bit: strawberry-sugar 45 volte più del caso).
- *digital* e *information* solo **debolmente** a *computer*, *data* e *result*: sono contesti frequenti, che compaiono con tutto, quindi il caso ne prevede già moltissime co-occorrenze.
- Tutte le altre celle sono 0: la matrice è sparsa come i conteggi.

Messaggio: **i coseni sui vettori PPMI confrontano ciò che è distintivo di due parole, non quanto sono frequenti**. Numeri (esercizio 12): cos(cherry, strawberry) passa da 0,969 (conteggi) a 0,960 (PPMI); cos(digital, information) crolla da 0,996 a 0,079 (0,085 con i valori arrotondati della tabella), perché le loro associazioni positive cadono su colonne diverse (digital su *computer*, information su *result* e *data*). Su sole cinque colonne, con contesti tutti frequenti, è un effetto estremo: in una matrice vera avrebbero molti contesti distintivi in comune.

<a id="p-57"></a>

### Slide 57 · PMI ed eventi rari: la PPMI con α

**Eventi rari**: la PMI è distorta verso gli eventi poco frequenti. Una parola vista una volta sola, in un solo contesto anch'esso raro, riceve un'associazione altissima da una sola co-occorrenza. Esempio (esercizio 11): con $N = 10^6$ coppie, parola e contesto visti una volta ciascuno, insieme: $\text{PMI} = \log_2\frac{10^{-6}}{10^{-6}\cdot10^{-6}} = \log_2 10^6 = 19{,}9$ bit, contro il massimo di 5,51 della tabella. Nel notebook (cella 21) le celle con PPMI più alta sono coppie viste 2 volte, come *nonzero/maxsplit* (12,6 bit).

$$\text{PPMI}_\alpha(w,c) = \max\left(\log_2\frac{P(w,c)}{P(w)P_\alpha(c)},\ 0\right)\qquad P_\alpha(c) = \frac{\text{count}(c)^\alpha}{\sum_{c'}\text{count}(c')^\alpha}$$

Rimedio di **Levy et al. (2015)**: usare al denominatore una probabilità diversa per il contesto, ottenuta elevando i conteggi dei contesti alla potenza **α = 0,75** e rinormalizzando. Elevare a una potenza minore di 1 "schiaccia" i conteggi grandi più di quelli piccoli, quindi la distribuzione dei contesti diventa più piatta.

<a id="p-58"></a>

### Slide 58 · L'effetto di α: un esempio

$$P_\alpha(a) = \frac{0{,}99^{0{,}75}}{0{,}99^{0{,}75}+0{,}01^{0{,}75}} = \frac{0{,}9925}{0{,}9925+0{,}0316} = 0{,}97\qquad P_\alpha(b) = \frac{0{,}0316}{1{,}0241} = 0{,}03$$

Con $P(a) = 0{,}99$ e $P(b) = 0{,}01$, il grafico a barre mostra le due coppie di barre: il frequente $a$ scende da 0,99 a 0,97, il raro $b$ sale da 0,01 a 0,03 (esattamente 0,969 e 0,031). Un contesto raro riceve una probabilità più alta, quindi il denominatore della PMI cresce e la sua **PMI scende** (per $b$ di $\log_2(0{,}031/0{,}01) = 1{,}6$ bit); quella dei contesti frequenti sale di poco.

Sulla tabella di Wikipedia (verificato, notebook cella 18): $P_\alpha$ dei contesti diventa 0,402, 0,442, 0,069, 0,073, 0,015; PPMI(cherry, pie) scende da 4,38 a 3,64, PPMI(strawberry, sugar) da 5,51 a 4,01, mentre PPMI(information, data) sale da 0,09 a 0,23.

**Altro rimedio**: **add-k smoothing** dei conteggi prima di calcolare la PMI, con $k$ fra 0,1 e 3: lo stesso add-k degli n-gram ([L5](L05-smoothing-ed-entropia.md#p-21)), che toglie un po' di peso alle coppie viste una o due volte. Il notebook mostra che va usato con cautela: su una matrice 2000 × 2000 con $k = 0{,}5$ si aggiungono 2 milioni di pseudo-conteggi, quasi 7 volte le co-occorrenze reali, e le parole funzionali tornano fra i vicini.

## Riepilogo: quale conteggio, quale peso

<a id="p-59"></a>

### Slide 59 · Quale conteggio, quale pesatura, per che cosa

La mappa decisionale della lezione parte da una domanda: **che cosa voglio confrontare?**

- **Documenti** (ricerca, similarità fra documenti): il contesto è il **documento intero**; matrice **termine-documento**, un documento è una colonna; pesatura **tf-idf**: frequente qui, raro altrove.
- **Parole** (parole simili, vicini): il contesto sono le **parole vicine**; matrice **parola-contesto**, una parola è una riga; pesatura **PPMI**: più del caso.

Poi, in entrambi i casi, si confrontano i vettori con il **coseno**. **Stessa ricetta, contesto diverso**: il documento intero o le parole vicine.

Le due pesature non sono vincolate alle due matrici: il libro usa tf-idf anche sulla matrice parola-contesto (§5.3 lo cita come la pesatura più popolare) e si può usare PMI fra parole e documenti. La mappa indica gli abbinamenti tipici.

<a id="p-60"></a>

### Slide 60 · Le pesature dei documenti: che problema risolve ciascuna

Matrice termine-documento, quattro passi:

1. **Conteggio grezzo** $\text{count}(t,d)$. Problema: 100 occorrenze non rendono una parola 100 volte più rilevante.
2. **Term frequency** $\text{tf}_{t,d} = 1+\log_{10}\text{count}(t,d)$. Soluzione: cresce lentamente (10 → 2, 100 → 3; 0 se la parola è assente). Problema: *good*, presente in ogni opera, pesa ancora molto.
3. **Inverse document frequency** $\text{idf}_t = \log_{10}(N/\text{df}_t)$. Soluzione: 0 per una parola presente in ogni documento, alta per una rara.
4. **tf-idf** $w_{t,d} = \text{tf}_{t,d}\times\text{idf}_t$. Risultato: alto per le parole **frequenti in questo documento e rare negli altri**, quelle che lo caratterizzano.

Ogni passo risolve il problema del precedente: tf-idf è il risultato. È uno schema utile all'orale: per ogni formula, saper dire quale difetto corregge.

<a id="p-61"></a>

### Slide 61 · Le pesature delle parole: che problema risolve ciascuna

Matrice parola-contesto, quattro passi:

1. **Conteggio grezzo** $\text{count}(w,c)$. Problema: *the*, *of* co-occorrono con tutto: la frequenza non è associazione.
2. **PMI** $\log_2\frac{P(w,c)}{P(w)P(c)}$. Soluzione: co-occorrenza osservata contro quella attesa per caso. Problema: i valori negativi sono inaffidabili e $\log 0 = -\infty$.
3. **PPMI** $\max(\text{PMI}, 0)$. Soluzione: si tiene solo l'associazione positiva. Problema: un contesto raro visto una volta con $w$ riceve una PMI altissima.
4. **α = 0,75 o add-k**, $P_\alpha(c) = \text{count}(c)^\alpha/\sum_{c'}\text{count}(c')^\alpha$. Soluzione: i contesti rari ricevono una $P(c)$ più alta e quindi una PMI più bassa; add-k smussa tutti i conteggi.

Il risultato: **PPMI con α = 0,75**, associazione senza il bias verso le parole rare. Parallelo con la scheda precedente: idf e PMI fanno lo stesso lavoro (togliere peso a ciò che compare dappertutto), uno contando documenti, l'altro confrontando con il caso.

<a id="p-62"></a>

### Slide 62 · Riepilogo e prossima lezione

**Riepilogo**:

- semantica lessicale: sensi, sinonimia, similarità, relatedness, connotazione;
- ipotesi distribuzionale: contesti simili, significati simili;
- matrice parola-contesto: una parola come i conteggi dei suoi vicini;
- il coseno: angoli, non lunghezze; mai il prodotto scalare grezzo;
- documenti (ricerca, similarità): matrice termine-documento e tf-idf;
- parole (parole simili): matrice parola-contesto e PPMI, α = 0,75.

**Prossima lezione**: **word2vec**. Skip-gram con negative sampling: invece di contare, si addestra un classificatore (una regressione logistica, [sigmoide](L06-regressione-logistica.md#p-22) del prodotto scalare fra due vettori) a distinguere i veri vicini da parole estratte a caso, e i pesi appresi sono gli embedding densi. Poi proprietà, bias e valutazione degli embedding. Capitolo 5, §5.5-5.10. Legame con oggi: word2vec ottimizza implicitamente una matrice di PMI spostata (Levy e Goldberg, 2014), e usa lo stesso esponente 0,75 per campionare i negativi.

## Notebook

Commento al notebook del corso `HLT-L10-vector-semantics.ipynb` (il notebook è del docente e non è incluso).

Notebook di accompagnamento della lezione: le tre dimensioni di Osgood, i conteggi del libro con prodotto scalare e coseno, un corpus costruito senza scaricare nulla (le docstring di circa 120 moduli della libreria standard di Python, come nel notebook della L4), la matrice parola-contesto 2000 × 2000 con i vicini più prossimi, la matrice termine-documento con tf-idf e un piccolo motore di ricerca, le quattro nano-frasi del libro, la PPMI (anche con α = 0,75 e add-k) sulla tabella dell'Appendice J e sul corpus, e infine il ricalcolo degli esercizi 2-4 e 6-12 della scheda. Servono solo la libreria standard e `numpy`, niente rete e niente grafici (il notebook non produce figure).

Ho eseguito il notebook (Python 3.13, nbconvert): le celle con numeri del libro e della scheda (2, 4, 16, 18, 23, 24) danno esattamente gli output salvati; le celle sul corpus di docstring (6-21) danno numeri leggermente diversi, come il notebook stesso avverte, perché il corpus è la documentazione della versione di Python installata (con 3.13: 124 moduli e circa 61.000 token invece di 123 e 60.295). I commenti qui sotto si riferiscono agli output salvati; le conclusioni qualitative non cambiano. Ho controllato i punti dove di solito si sbaglia: finestra ±k senza la parola stessa, coseno con divisione per entrambe le norme (e norme nulle gestite), tf con il caso count = 0, idf con df contato per documenti e non per occorrenze, query pesata con l'idf della collezione, marginali PPMI dalla stessa matrice, α applicato solo ai contesti, valori $-\infty$ portati a 0. **Non ho trovato bug.**

### Notebook 1 · Osgood: distanza e coseno (esercizio 2)

```python
VAD = {"courageous": [8.0, 5.5, 7.4], "music": [7.7, 5.6, 6.5],
       "heartbreak": [2.5, 5.7, 3.6], "cub": [6.7, 4.0, 4.2]}

def cosine(v, w):
    v, w = np.asarray(v, float), np.asarray(w, float)
    return float(v @ w / (np.linalg.norm(v) * np.linalg.norm(w)))

def distance(v, w):
    return float(np.linalg.norm(np.asarray(v, float) - np.asarray(w, float)))
```

Output:

```text
                        courageous                 music            heartbreak                   cub
courageous     dist 0.00 cos 1.000   dist 0.95 cos 0.998   dist 6.69 cos 0.889   dist 3.77 cos 0.986
music          dist 0.95 cos 0.998   dist 0.00 cos 1.000   dist 5.95 cos 0.900   dist 2.97 cos 0.991
heartbreak     dist 6.69 cos 0.889   dist 5.95 cos 0.900   dist 0.00 cos 1.000   dist 4.57 cos 0.858
cub            dist 3.77 cos 0.986   dist 2.97 cos 0.991   dist 4.57 cos 0.858   dist 0.00 cos 1.000
```

Le due funzioni di base del notebook. Sulla tabella di Osgood ([scheda 7](L10-semantica-vettoriale.md#p-7)) le distanze vanno da 0,95 a 6,69, mentre i coseni stanno tutti fra 0,858 e 0,998: con tre scale positive da 1 a 9 tutti i vettori puntano più o meno nella stessa direzione, e il coseno non discrimina. Il testo della cella trae la conclusione giusta: il coseno è lo strumento per i vettori di conteggi, dove la lunghezza riflette la frequenza e va ignorata; per punti su scale con un punto neutro serve la distanza. Risponde all'esercizio 2.

### Notebook 2 · I conteggi del libro: prodotto scalare e coseno (esercizi 4 e 6)

```python
FIG52 = {"cherry": [1, 0, 1], "strawberry": [0, 0, 2], "digital": [0, 1, 0], "information": [1, 1, 0]}   # a, computer, pie
FIG53 = {"cherry": [0, 2, 8, 9, 442, 25], ...}     # aardvark, computer, data, result, pie, sugar

table(FIG52, dot, ...); table(FIG52, cosine, ...)
table(FIG53, cosine, ...)
pie_result = {w: [v[4], v[3]] for w, v in FIG53.items()}         # exercise 5.1
short = {w: [v[4], v[2], v[1]] for w, v in FIG53.items()}        # pie, data, computer
```

Output:

```text
Fig. 5.2, dot products:
                   cherry   strawberry      digital  information
cherry              2.000        2.000        0.000        1.000
strawberry          2.000        4.000        0.000        0.000
digital             0.000        0.000        1.000        1.000
information         1.000        0.000        1.000        2.000

Fig. 5.2, cosines:
cherry              1.000        0.707        0.000        0.500
strawberry          0.707        1.000        0.000        0.000
digital             0.000        0.000        1.000        0.707
information         0.500        0.000        0.707        1.000

Fig. 5.3, cosines on the six dimensions:
cherry              1.000        0.969        0.019        0.019
strawberry          0.969        1.000        0.003        0.003
digital             0.019        0.003        1.000        0.996
information         0.019        0.003        0.996        1.000

exercise 5.1: cos(cherry, strawberry) = 0.99999   cos(cherry, digital) = 0.079
the book: cos(cherry, information) = 0.018   cos(digital, information) = 0.996
```

Le tabelle delle [schede 19](L10-semantica-vettoriale.md#p-19) e [21](L10-semantica-vettoriale.md#p-21). Sulla prima: il prodotto scalare mette cherry-strawberry (2) sopra digital-information (1), il coseno le mette alla pari (0,707): *strawberry* ha un vettore più lungo ([0, 0, 2]) e il coseno lo compensa (esercizio 6). Sulla seconda i coseni separano nettamente i due gruppi (0,969 e 0,996 dentro i gruppi, 0,003-0,019 fra i gruppi). Gli indici delle colonne sono corretti (pie = 4, result = 3, data = 2, computer = 1 dopo *aardvark*), e l'ultima riga riproduce .018 e .996 della [scheda 28](L10-semantica-vettoriale.md#p-28).

### Notebook 3 · Un corpus senza download: le docstring della libreria standard

```python
def module_text(name):
    mod = importlib.import_module(name)
    parts = [inspect.getdoc(mod) or ""]
    ...   # docstrings of the public functions and classes defined in the module

def tokenize(text):
    text = re.sub(r"\s+", " ", text.lower())
    ...   # sentences with >>> or backslashes are skipped
    toks = re.findall(r"[a-z][a-z'_-]*|[0-9]+|[^\sa-z0-9]", s)

docs = {m: tokenize(module_text(m)) for m in MODULES}
docs = {m: t for m, t in docs.items() if len(t) >= 50}
```

Output:

```text
123 modules, 60295 tokens, 4443 types
most frequent: . 3788, the 3616, a 1754, , 1747, is 1338, to 1304, of 1169, and 804, ( 755, ) 748, for 742, be 717
```

Il corpus è la documentazione di circa 140 moduli, di cui 123 con almeno 50 token. Tokenizzazione a regex in minuscolo, con la punteggiatura come token (le idee della [L3](L03-elaborazione-del-testo.md#p-27)); le frasi con esempi di codice (`>>>`) sono scartate. Ogni modulo servirà anche come **documento** nella sezione tf-idf. Le parole più frequenti sono punteggiatura e parole funzionali, come in ogni corpus inglese: è proprio ciò che inquinerà i conteggi grezzi. Con Python 3.13 l'esecuzione dà 124 moduli, 61.083 token, 4494 tipi.

### Notebook 4 · La matrice parola-contesto e i vicini più prossimi

```python
V = [w for w, _ in freq.most_common() if w.isalpha()][:2000]
WINDOW = 4

def word_context_matrix(docs, index, window):
    F = np.zeros((len(index), len(index)))
    for toks in docs.values():
        ids = [index.get(t, -1) for t in toks]
        for i, wi in enumerate(ids):
            if wi < 0: continue
            for j in range(max(0, i - window), min(len(ids), i + window + 1)):
                if j != i and ids[j] >= 0:
                    F[wi, ids[j]] += 1
    return F

def neighbors(M, word, k=8):
    v = M[index[word]]
    norms = np.linalg.norm(M, axis=1); norms[norms == 0] = 1
    cos = M @ v / (norms * np.linalg.norm(v))
    ...
```

Output:

```text
word-context matrix (2000, 2000), 2.7% of the cells are non-zero, 299196 co-occurrences
row of 'file' on a few contexts: {'the': 204, 'open': 19, 'name': 31, 'read': 21, 'directory': 6, 'string': 5}
file       [('with', 0.925), ('and', 0.924), ('in', 0.922), ('directory', 0.917), ('from', 0.916), ('of', 0.914), ...]
string     [('object', 0.941), ('file', 0.913), ('with', 0.907), ('or', 0.892), ('returns', 0.892), ...]
error      [('argument', 0.839), ('file', 0.838), ('which', 0.834), ('given', 0.827), ('to', 0.825), ...]
directory  [('file', 0.917), ('given', 0.917), ('to', 0.897), ('argument', 0.895), ('and', 0.89), ...]
socket     [('function', 0.724), ('and', 0.715), ('with', 0.715), ('path', 0.714), ('interface', 0.713), ...]
```

La matrice della [scheda 18](L10-semantica-vettoriale.md#p-18), $|V| = 2000$, finestra ±4: per ogni occorrenza si contano le parole entro 4 posizioni, esclusa la parola stessa (`j != i`); i limiti `max(0, ...)` e `min(len, ...)` evitano di uscire dal documento. Solo il 2,7% delle celle è non nullo ([scheda 22](L10-semantica-vettoriale.md#p-22)). `neighbors` normalizza le righe e fa un unico prodotto matrice-vettore: il coseno con tutte le parole in un colpo ([scheda 30](L10-semantica-vettoriale.md#p-30)); le norme nulle sono messe a 1 per non dividere per zero.

Risultato: qualche vicino sensato (*directory* per *file*, *object* per *string*), ma le liste sono piene di *with, and, in, of, to*, con coseni tutti sopra 0,8. Sui conteggi grezzi le parole più simili a qualunque cosa sono quelle che co-occorrono con tutto: è il problema che la PPMI risolverà (blocco 10).

### Notebook 5 · La lunghezza delle righe è la frequenza

```python
lengths = np.linalg.norm(F, axis=1)
order = np.argsort(-lengths)
print("longest vectors:", ...)
np.corrcoef(np.log1p([freq[w] for w in V]), np.log1p(lengths))[0, 1]
```

Output:

```text
longest vectors: the 2273, of 1125, is 1057, a 1035, to 921, be 603, in 548, if 539
log frequency and log vector length: correlation 0.980
```

Verifica numerica del **bias della frequenza** della [scheda 25](L10-semantica-vettoriale.md#p-25): i vettori più lunghi sono quelli delle parole più frequenti, e la correlazione fra log-frequenza e log-lunghezza è 0,98. Un prodotto scalare non normalizzato premierebbe sempre *the*; il coseno divide per questa lunghezza.

### Notebook 6 · Documenti come vettori: tf-idf sui moduli

```python
T = np.zeros((len(VT), len(D)))           # term-document matrix
...
def tf_idf(T):
    tf = np.where(T > 0, 1 + np.log10(np.where(T > 0, T, 1)), 0.0)
    df = (T > 0).sum(axis=1)
    idf = np.log10(T.shape[1] / np.maximum(df, 1))
    return tf * idf[:, None], idf
```

Output:

```text
term-document matrix (2447, 123)
raw counts, most similar modules to json:   [('weakref', 0.54), ('py_compile', 0.518), ('doctest', 0.511), ('typing', 0.506), ('sys', 0.498)]
idf(the) = 0.011  (in 120 of 123 modules)
idf(file) = 0.326  (in 58 of 123 modules)
idf(socket) = 1.187  (in 8 of 123 modules)
idf(json) = 2.090  (in 1 of 123 modules)

tf-idf, most similar modules to gzip    [('bz2', 0.434), ('lzma', 0.348), ('io', 0.165), ('fileinput', 0.131), ('codecs', 0.108)]
tf-idf, most similar modules to socket  [('ipaddress', 0.262), ('ftplib', 0.222), ('smtplib', 0.197), ('asyncio', 0.173), ('io', 0.156)]
tf-idf, most similar modules to pickle  [('struct', 0.079), ('warnings', 0.068), ('re', 0.066), ('secrets', 0.059), ('platform', 0.057)]
```

La matrice termine-documento della [scheda 34](L10-semantica-vettoriale.md#p-34), con i 123 moduli come documenti. `tf_idf` applica le formule delle [schede 39](L10-semantica-vettoriale.md#p-39)-[43](L10-semantica-vettoriale.md#p-43): il doppio `np.where` evita $\log 0$ (prima sostituisce gli zeri con 1, poi rimette tf = 0), il df conta i documenti con conteggio positivo (non le occorrenze), $N$ è il numero di colonne. Sui conteggi grezzi i moduli più simili a `json` non c'entrano niente (`weakref`, `py_compile`): domina il lessico comune, come *good* nelle opere di Shakespeare ([scheda 37](L10-semantica-vettoriale.md#p-37)). Con tf-idf `gzip` trova `bz2` e `lzma`, `socket` i moduli di rete. *the* compare in 120 moduli su 123: idf 0,011, praticamente zero. `pickle` resta con coseni piccoli con tutto: la sua documentazione condivide poche parole distintive con gli altri moduli.

### Notebook 7 · Un piccolo motore di ricerca

```python
def search(query, k=5):
    q = np.zeros(len(VT))
    for t, c in Counter(re.findall(r"[a-z]+", query.lower())).items():
        if t in tindex: q[tindex[t]] = (1 + math.log10(c)) * idf[tindex[t]]
    norms = np.linalg.norm(W, axis=0); norms[norms == 0] = 1
    cos = W.T @ q / (norms * (np.linalg.norm(q) or 1))
    return [(D[j], round(float(cos[j]), 3)) for j in np.argsort(-cos)[:k]]
```

Output:

```text
read the lines of a text file    [('linecache', 0.146), ('bz2', 0.129), ('gzip', 0.125), ('fileinput', 0.121), ('textwrap', 0.108)]
compress data                    [('bz2', 0.197), ('gzip', 0.173), ('lzma', 0.149), ('binascii', 0.031), ('struct', 0.029)]
parse a date and time            [('linecache', 0.141), ('email', 0.124), ('imaplib', 0.073), ('platform', 0.07), ('logging', 0.058)]
send an email message            [('email', 0.238), ('smtplib', 0.196), ('http.client', 0.112), ('py_compile', 0.044), ('gettext', 0.044)]
```

La query è un documento corto, pesata con la sua tf e l'idf **della collezione** ([scheda 45](L10-semantica-vettoriale.md#p-45)); il punteggio è il coseno ([scheda 46](L10-semantica-vettoriale.md#p-46)). Le parole della query assenti dal vocabolario vengono ignorate. *compress data* e *send an email message* funzionano bene. *parse a date and time* no: `datetime` non compare, perché nelle sue docstring, così come vengono raccolte, la parola *date* non c'è mai (verificato: conteggio 0). Tf-idf confronta le **parole** della query, non il loro significato: è il limite che gli embedding densi e il dense retrieval (cap. 11) vogliono superare.

### Notebook 8 · Le quattro nano-frasi del libro (esercizio 9)

```python
nano = {"Doc 1": "sweet sweet nurse love", "Doc 2": "sweet sorrow",
        "Doc 3": "how sweet is love", "Doc 4": "nurse"}
Tn = np.array([[Counter(d.split())[w] for d in nano.values()] for w in vocab_n], float)
Wn, idf_n = tf_idf(Tn)
q = np.array([(1 + math.log10(c)) * idf_n[vocab_n.index(w)] if (c := Counter("sweet love".split())[w]) else 0
              for w in vocab_n])
```

Output:

```text
idf: {'how': 0.602, 'is': 0.602, 'love': 0.301, 'nurse': 0.301, 'sorrow': 0.602, 'sweet': 0.125}
Doc 1: tf-idf {... 'love': 0.301, 'nurse': 0.301, 'sorrow': 0.0, 'sweet': 0.163}   cos(query, doc) = 0.747
Doc 2: tf-idf {... 'sorrow': 0.602, 'sweet': 0.125}   cos(query, doc) = 0.078
Doc 3: tf-idf {'how': 0.602, 'is': 0.602, 'love': 0.301, ... 'sweet': 0.125}   cos(query, doc) = 0.357
Doc 4: tf-idf {... 'nurse': 0.301 ...}   cos(query, doc) = 0.000
```

Riproduce la Fig. 11.6 del libro: 0,747 e 0,078 (il libro scrive 0,0779). Calcola anche i due documenti che il libro lascia come esercizio: Doc 3 ha coseno 0,357 (contiene entrambe le parole della query, ma anche *how* e *is*, rare e quindi pesanti, che allungano il vettore), Doc 4 ha 0. Classifica finale: Doc 1, Doc 3, Doc 2, Doc 4. Il `:=` (walrus) richiede Python 3.8 o successivo.

### Notebook 9 · PPMI sulla tabella dell'Appendice J (esercizi 10 e 11)

```python
def ppmi(F, alpha=None, k=0.0):
    Fk = F + k
    N = Fk.sum()
    pw = Fk.sum(axis=1) / N
    counts_c = Fk.sum(axis=0)
    pc = counts_c ** alpha / (counts_c ** alpha).sum() if alpha else counts_c / N
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log2((Fk / N) / np.outer(pw, pc))
    return np.where(np.isfinite(pmi), np.maximum(pmi, 0), 0.0)
```

Output:

```text
PPMI matrix of Appendix J:
              computer      data    result       pie     sugar
cherry            0.00      0.00      0.00      4.38      3.30
strawberry        0.00      0.00      0.00      4.10      5.51
digital           0.18      0.01      0.00      0.00      0.00
information       0.02      0.09      0.28      0.00      0.00

pmi(information, data) = 0.0944   pmi(cherry, computer) = -6.7
with alpha = 0.75:
[[0.   0.   0.   3.64 1.8 ]
 [0.   0.   0.   3.37 4.01]
 [0.27 0.14 0.   0.   0.  ]
 [0.1  0.23 0.   0.   0.  ]]
with add-1 smoothing:
[[0.   0.   0.   4.36 3.26]
 [0.   0.   0.   4.03 5.41]
 [0.18 0.01 0.   0.   0.  ]
 [0.02 0.1  0.27 0.   0.  ]]
```

Una funzione per le tre varianti della [scheda 61](L10-semantica-vettoriale.md#p-61). `np.outer(pw, pc)` è la matrice dei prodotti $P(w)P(c)$, il denominatore del caso; i $\log 0 = -\infty$ delle celle vuote diventano 0 con `np.isfinite`. L'esponente α si applica solo ai **contesti** (le colonne), come nella formula di Levy et al.; $P(w)$ resta la marginale normale. La matrice coincide con quella della [scheda 56](L10-semantica-vettoriale.md#p-56), e la riga sotto stampa $-6{,}7$ per cherry-computer: conferma la correzione della [scheda 54](L10-semantica-vettoriale.md#p-54) (il testo della cella la spiega allo stesso modo).

Con α = 0,75 le associazioni con i contesti rari (*pie*, *sugar*) scendono (4,38 → 3,64; 5,51 → 4,01) e quelle con i contesti frequenti salgono (0,09 → 0,23): [scheda 58](L10-semantica-vettoriale.md#p-58). Add-1 qui cambia poco, perché i conteggi sono grandi.

### Notebook 10 · PPMI sul corpus: vicini migliori

```python
Pf = ppmi(F)
for w in ("file", "string", "error", "integer", "directory", "socket"):
    print(f"{w:10s}", neighbors(Pf, w))
```

Output:

```text
PPMI on the docstring matrix: 2.3% of the cells are non-zero (raw counts: 2.7%)
file       [('files', 0.262), ('directory', 0.246), ('or', 0.206), ('a', 0.191), ('the', 0.187), ...]
string     [('a', 0.291), ('containing', 0.281), ('ascii', 0.254), ('as', 0.207), ('xml', 0.204), ...]
error      [('occurs', 0.228), ('message', 0.22), ('errors', 0.206), ('handling', 0.183), ('encoding', 0.18), ...]
integer    [('float', 0.224), ('representation', 0.214), ('x', 0.182), ('flags', 0.178), ('integers', 0.176), ...]
directory  [('file', 0.246), ('link', 0.234), ('tree', 0.231), ('exists', 0.211), ('dst', 0.204), ...]
socket     [('ftp', 0.248), ('smtp', 0.23), ('timeout', 0.223), ('connection', 0.21), ('client', 0.205), ...]
```

Stessa funzione `neighbors`, sulla matrice pesata. I vicini di *error*, *directory* e *socket* sono ora parole dello stesso campo (*message, errors, handling*; *link, tree, exists*; *ftp, smtp, connection*), senza parole funzionali; *integer* trova *float* e *integers*. Restano *a, the* fra i vicini di *file* e *string*: con 60.000 token la PPMI è lontana dall'essere perfetta. I coseni sono molto più bassi (0,2-0,3 invece di 0,9): non c'è più la componente comune dovuta alle parole frequenti. La matrice è un po' più sparsa (2,3% contro 2,7%) perché le PMI negative diventano 0 ([scheda 51](L10-semantica-vettoriale.md#p-51)).

### Notebook 11 · Eventi rari: α e add-k sul corpus

```python
print("largest PPMI cells (target, context, PPMI, raw count):")
for row in top_cells(Pf): print("  ", row)
Pa = ppmi(F, alpha=0.75); Pk = ppmi(F, k=0.5)
neighbors(Pa, "file", 6); neighbors(Pk, "file", 6)
```

Output:

```text
largest PPMI cells (target, context, PPMI, raw count):
   ('nonzero', 'maxsplit', 12.56, 2)
   ('maxsplit', 'nonzero', 12.56, 2)
   ('fnmatch', 'fnmatch', 12.02, 2)
   ('aninteger', 'abytes', 11.8, 2)
   ('abytes', 'aninteger', 11.8, 2)
   ('statisticserror', 'statisticserror', 11.79, 2)

the same cells with alpha = 0.75: [11.21, 11.14, 10.7, 10.48, 10.53, 10.5]
the same cells with add-0.5:      [2.49, 2.49, 2.49, 2.49, 2.49, 2.49]

neighbors of 'file' with alpha = 0.75: [('files', 0.281), ('directory', 0.263), ('or', 0.209), ('the', 0.208), ('binary', 0.207), ('write', 0.203)]
neighbors of 'file' with add-0.5:      [('the', 0.619), ('and', 0.558), ('a', 0.555), ('or', 0.54), ('is', 0.536), ('in', 0.515)]
```

Il bias verso gli eventi rari ([scheda 57](L10-semantica-vettoriale.md#p-57)) in un corpus vero: le sei celle con PPMI più alta sono coppie viste **2 volte**, parole rare (*aninteger*, *abytes* sono refusi delle docstring), 12 bit di associazione da due co-occorrenze. α = 0,75 le abbassa di circa 1,3 bit (e i vicini di *file* migliorano: entrano *binary* e *write*). Add-0,5 le schiaccia tutte a 2,49, ma i vicini di *file* tornano a essere *the, and, a*: su una matrice 2000 × 2000, aggiungere 0,5 a quattro milioni di celle aggiunge due milioni di pseudo-conteggi, quasi 7 volte le 299.196 co-occorrenze reali, e appiattisce tutto. Il valore di $k$ va scelto in rapporto alla dimensione della matrice (sul devset, come per gli n-gram della [L5](L05-smoothing-ed-entropia.md#p-21)). Con Python 3.13 cambiano le coppie (compare *uid/gid*, vista 5 volte) ma non il quadro.

### Notebook 12 · Verifica degli esercizi 2-7 della scheda

```python
mini = ["the cat sat on the mat", "the dog sat on the rug", "the cat chased the dog",
        "a dog ate the food", "the cat ate the fish"]
mini_docs = {k: s.split() for k, s in enumerate(mini)}            # one document per sentence
F3 = word_context_matrix(mini_docs, mini_index, 2)
...
v7, w7, u7 = np.array([1.0, 1.0]), np.array([3.0, 3.0]), np.array([1.0, 0.0])
```

Output:

```text
exercise 2   courageous, music: distance 0.95, cosine 0.998
exercise 2   courageous, heartbreak: distance 6.69, cosine 0.889
exercise 3   {'cat': [5, 1, 1, 1], 'dog': [3, 1, 1, 1]}  cosine 0.982
exercise 4   cos(cherry, strawberry) = 0.99999, cos(cherry, digital) = 0.079
exercise 6   cherry, strawberry: dot 2, cosine 0.707
exercise 6   cherry, information: dot 1, cosine 0.500
exercise 6   digital, information: dot 1, cosine 0.707
exercise 6   cherry, digital: dot 0, cosine 0.000
exercise 7   dot(v, u) = 1, dot(w, u) = 3, cos(v, u) = 0.707, cos(w, u) = 0.707, unit vectors [0.707 0.707] [0.707 0.707]
```

Tutti i valori coincidono con le soluzioni della sezione Studio, ricontrollate a mano. Nell'esercizio 3 ogni frase è un documento separato, quindi le finestre non attraversano i confini di frase: è la lettura corretta della consegna. Le colonne sono nell'ordine *the, sat, ate, chased*.

### Notebook 13 · Verifica degli esercizi 8-12 della scheda

```python
idf_book = {"battle": 0.246, "good": 0.0, "fool": 0.012, "wit": 0.037}   # the idf values of the textbook's table
weighted = np.array([[tf(c) * idf_book[w] for w, c in zip(PLAYS, play)] for play in plays])
...
pmi = lambda i, j: math.log2(APP_J[i, j] * N / (APP_J[i].sum() * APP_J[:, j].sum()))
...
FIGJ4 = np.array([[0, 0, 0, 4.38, 3.30], [0, 0, 0, 4.10, 5.51], [0.18, 0.01, 0, 0, 0], [0.02, 0.09, 0.28, 0, 0]])
```

Output:

```text
exercise 8   tf(battle) = [1.0, 0.0, 1.845, 2.114]  idf(battle) = 0.246, idf(good) = 0
             tf-idf(battle) = [0.246, 0.0, 0.454, 0.52]  tf-idf(good) = [0.0, 0.0, 0.0, 0.0]
             raw counts: cos(As You Like It, Twelfth Night) = 0.950, cos(As You Like It, Julius Caesar) = 0.945
             tf-idf vectors (battle, good, fool, wit): [[0.246, 0.0, 0.031, 0.085], [0.0, 0.0, 0.033, 0.081], [0.454, 0.0, 0.012, 0.048]]
             tf-idf: cos(As You Like It, Twelfth Night) = 0.345, cos(As You Like It, Julius Caesar) = 0.970
exercise 9   df = {'sweet': 3, 'love': 2, 'nurse': 2, 'sorrow': 1, 'how': 1, 'is': 1}  idf = {'sweet': 0.125, 'love': 0.301, ...}
             query {'love': 0.301, 'sweet': 0.125}  length 0.326
             Doc 1 {'love': 0.301, 'nurse': 0.301, 'sweet': 0.163}  length 0.456, cosine with the query 0.747
             Doc 2 {'sorrow': 0.602, 'sweet': 0.125}  length 0.615, cosine with the query 0.078
exercise 10  PPMI(cherry, pie) = 4.38, PPMI(strawberry, sugar) = 5.51, PMI(digital, pie) = -4.91
             information, data: observed 3982, expected by chance 3730, ratio 1.07, PMI 0.09
             information, result: observed 378, expected by chance 311, ratio 1.22, PMI 0.28
exercise 11  PMI of a single co-occurrence with N = 10^6: 19.9
             P(c) = [0.9  0.09 0.01]  P_alpha(c) = [0.825 0.147 0.028]
             P_alpha(a), P_alpha(b) = [0.969 0.031]
exercise 12  Fig. J.4:        cos(cherry, strawberry) = 0.960, cos(digital, information) = 0.085
             unrounded PPMI:  cos(cherry, strawberry) = 0.960, cos(digital, information) = 0.079
             raw counts:      cos(cherry, strawberry) = 0.969, cos(digital, information) = 0.996
```

Esercizio 8: con gli idf arrotondati del libro, come chiede la consegna (con gli idf esatti i coseni tf-idf sono 0,343 e 0,971). Esercizio 10: la forma osservato/atteso della [scheda 53](L10-semantica-vettoriale.md#p-53), con i conteggi interi. Esercizio 12: il notebook mostra entrambe le versioni, con i valori arrotondati della tabella (0,085) e con la PPMI non arrotondata (0,079); la differenza viene dai piccoli valori (0,01; 0,02) arrotondati a due decimali. Tutto coincide con le soluzioni della sezione Studio.

## Studio ed esercizi

### Guida allo studio (circa 4 h 00 min)

**Semantica lessicale e ipotesi distribuzionale** (30 min)

Schede 4-15. Saper distinguere sensi, sinonimia, similarità e relatedness con un esempio ciascuno (*mouse*, *couch/sofa*, *cat/dog*, *coffee/cup*), il principio di contrasto (*H2O*/*water*), le tre dimensioni di Osgood. Enunciare l'ipotesi distribuzionale (Joos, Harris, Firth) e raccontare l'esempio di *ongchoi*. Embedding statici e contestuali, sparsi e densi. Esercizi 1 e 2. Libro §5.1-5.2 (pagine 128-132).

**Matrice parola-contesto e coseno** (50 min)

Schede 16-30. Costruire a mano una matrice parola-contesto con finestra ±k (scheda 19, esercizio 3). Prodotto scalare, lunghezza, perché il prodotto scalare favorisce le parole frequenti, coseno come prodotto scalare normalizzato, intervallo 0-1 per i conteggi. Rifare i due coseni della scheda 28 (0,018 e 0,996). Esercizi 4, 5, 6, 7; celle 2-4 e 8-10 del notebook. Libro §5.3-5.4 (pagine 132-136).

**Documenti come vettori e tf-idf** (55 min)

Schede 32-46. Bag of words e matrice termine-documento; perché *good* rende tutte le opere simili sui conteggi grezzi (0,950 contro 0,945); tf con il logaritmo e il caso 0; df e idf (Romeo 1,57, good 0); tf-idf; la query come documento e il coseno come punteggio. Rifare la tabella della scheda 43 e la Fig. 11.6 del libro (0,747 e 0,078). Leggere i riquadri delle schede 42 e 46. Esercizi 8 e 9; celle 12, 13 e 16 del notebook. Libro §11.1.1-11.1.3 (pagine 255-259).

**PMI, PPMI ed eventi rari** (55 min)

Schede 47-58. Definizione di PMI e lettura (0, positiva, negativa; in bit); perché si scartano i negativi; PPMI di una cella come osservato/atteso con i conteggi interi; rifare 4,38 (cherry, pie), 0,0944 (information, data) e $-6{,}70$ (cherry, computer, riquadro della scheda 54). Il bias verso gli eventi rari, $P_\alpha$ con α = 0,75 e add-k. Esercizi 10, 11, 12 e aggiuntivo A; celle 18-21 del notebook. Appendice J sul sito del libro.

**Riepilogo, notebook e ripasso orale** (50 min)

Schede 59-62: saper ridisegnare lo schema contare-pesare-confrontare e le due catene "problema → correzione" (conteggio → tf → idf → tf-idf; conteggio → PMI → PPMI → α). Eseguire il notebook dall'inizio e leggere `word_context_matrix`, `tf_idf`, `search` e `ppmi` finché si sa spiegare ogni riga. Provare a cambiare `WINDOW` (1 e 10) e guardare come cambiano i vicini. Poi rispondere ad alta voce alle domande della sezione orale.

### Esercizi

#### Esercizio 1 (scheda L10): sensi e relazioni fra parole

(a) La parola *bank* ha almeno due sensi. Indicali e, per ciascuno, scrivi una frase breve in cui va bene solo quel senso. (b) Classifica ogni coppia come sinonimi, parole simili, parole collegate (related) o antonimi: (car, automobile), (cat, dog), (coffee, cup), (hot, cold), (surgeon, scalpel), (couch, sofa). (c) Perché due parole non hanno quasi mai esattamente lo stesso significato? Usa *H2O* e *water*.

<details><summary>Soluzione</summary>

(a) Senso 1, istituto finanziario: *I deposited my salary at the bank.* Senso 2, riva di un fiume: *We had a picnic on the bank of the river.* In ciascuna frase il contesto (*deposited, salary*; *river, picnic*) seleziona un senso: è l'ipotesi distribuzionale applicata alle occorrenze, ed è ciò che un embedding statico non sa fare (un solo vettore per *bank*, che mescola i due sensi), mentre uno contestuale sì ([L1, scheda 34](L01-introduzione-al-corso.md#p-34)).

(b) (car, automobile) sinonimi; (cat, dog) simili; (coffee, cup) collegate: partecipano allo stesso evento, bere il caffè dalla tazza; (hot, cold) antonimi; (surgeon, scalpel) collegate: il chirurgo usa il bisturi, stesso campo semantico (ospedale); (couch, sofa) sinonimi. Nota: gli antonimi sono molto *simili* in quasi tutto tranne una dimensione, e compaiono negli stessi contesti (*the water is hot/cold*): per questo i vettori distribuzionali tendono a metterli vicini.

(c) Per il **principio di contrasto**: una differenza di forma comporta sempre qualche differenza di significato. *H2O* e *water* si riferiscono alla stessa sostanza e sono sostituibili salvando la verità, ma *H2O* appartiene al registro scientifico e sarebbe fuori luogo in una guida escursionistica. Il registro (genere, contesto d'uso) fa parte del significato; per questo "sinonimo" indica in pratica una sinonimia approssimata.

</details>

#### Esercizio 2 (scheda L10): la connotazione come punto nello spazio

Le tre dimensioni affettive di Osgood et al. (1957): courageous [8,0; 5,5; 7,4], music [7,7; 5,6; 6,5], heartbreak [2,5; 5,7; 3,6], cub [6,7; 4,0; 4,2] (valence, arousal, dominance). (a) Calcola distanza euclidea e coseno fra *courageous* e *music* e fra *courageous* e *heartbreak*. Quale coppia è più vicina? (b) I due coseni sono entrambi alti, sopra 0,88, mentre le due distanze sono molto diverse. Perché il coseno è una cattiva scelta per questi vettori tridimensionali, e che cosa dice su quando usarlo?

<details><summary>Soluzione</summary>

(a) courageous - music = [0,3; −0,1; 0,9]: distanza $\sqrt{0{,}09+0{,}01+0{,}81} = \sqrt{0{,}91} = 0{,}95$. Coseno: prodotto scalare $8\cdot7{,}7+5{,}5\cdot5{,}6+7{,}4\cdot6{,}5 = 61{,}6+30{,}8+48{,}1 = 140{,}5$; lunghezze $|c| = \sqrt{64+30{,}25+54{,}76} = \sqrt{149{,}01} = 12{,}207$, $|m| = \sqrt{59{,}29+31{,}36+42{,}25} = \sqrt{132{,}9} = 11{,}528$; $\cos = 140{,}5/140{,}72 = 0{,}998$.

courageous - heartbreak = [5,5; −0,2; 3,8]: distanza $\sqrt{30{,}25+0{,}04+14{,}44} = \sqrt{44{,}73} = 6{,}69$. Prodotto scalare $20+31{,}35+26{,}64 = 77{,}99$; $|h| = \sqrt{6{,}25+32{,}49+12{,}96} = \sqrt{51{,}7} = 7{,}190$; $\cos = 77{,}99/(12{,}207\cdot7{,}190) = 77{,}99/87{,}77 = 0{,}889$. La coppia più vicina è courageous-music, per entrambe le misure.

(b) Le tre scale vanno da 1 a 9 e tutti i valori sono positivi e intorno al centro: tutti i vettori puntano nella stessa regione dello spazio, con angoli piccoli (al massimo 31° fra queste quattro parole), quindi i coseni sono compressi fra 0,86 e 1. Ciò che distingue *heartbreak* è la **posizione** lungo la scala di valence (2,5 contro 8,0), che il coseno ignora in gran parte perché guarda solo la direzione. Se si centrano le scale sul punto neutro 5, cos(courageous, heartbreak) diventa $-0{,}92$: con dimensioni dotate di un punto neutro serve la distanza, o almeno la centratura. Il coseno è la scelta giusta quando la **lunghezza** del vettore è un disturbo da eliminare, come nei vettori di conteggi, dove riflette la frequenza. Verificato con numpy e con la cella 2 del notebook.

</details>

#### Esercizio 3 (scheda L10): una matrice parola-contesto a mano

Mini-corpus di cinque frasi: *the cat sat on the mat*; *the dog sat on the rug*; *the cat chased the dog*; *a dog ate the food*; *the cat ate the fish*. (a) Con finestra ±2 parole, riempi le righe di *cat* e *dog* della matrice parola-contesto, limitata ai contesti *the, sat, ate, chased*. (b) Calcola il coseno fra le due righe. (c) Che cosa predice l'ipotesi distribuzionale su *cat* e *dog*, e che cosa cambierebbe nelle due righe con un corpus di un milione di frasi?

<details><summary>Soluzione</summary>

(a) Finestre (dentro ciascuna frase): *cat* in frase 1: [the] cat [sat on] → the 1, sat 1. Frase 3: [the] cat [chased the] → the 2, chased 1. Frase 5: [the] cat [ate the] → the 2, ate 1. Totale **cat = [5, 1, 1, 1]** (the, sat, ate, chased).

*dog* in frase 2: [the] dog [sat on] → the 1, sat 1. Frase 3: [chased the] dog → chased 1, the 1. Frase 4: [a] dog [ate the] → ate 1, the 1 (*a* non è fra le colonne). Totale **dog = [3, 1, 1, 1]**.

(b) $\text{dot} = 5\cdot3+1+1+1 = 18$; $|cat| = \sqrt{25+3} = \sqrt{28} = 5{,}292$; $|dog| = \sqrt{9+3} = \sqrt{12} = 3{,}464$; $\cos = 18/18{,}33 = 0{,}982$.

(c) L'ipotesi distribuzionale predice che *cat* e *dog*, che compaiono negli stessi contesti (soggetto di *sat*, *ate*, oggetto di *chased*), abbiano significati simili: il coseno alto lo conferma. Però gran parte del coseno viene da *the* (15 dei 18 del prodotto scalare): con un milione di frasi la colonna *the* (e le altre parole funzionali) crescerebbe per tutte le parole e il coseno grezzo sarebbe alto per quasi ogni coppia di nomi. Le righe diventerebbero anche molto più lunghe e sparse (migliaia di contesti, quasi tutti a 0), e comparirebbero contesti distintivi (*meow, purr* contro *bark, leash*). Per far emergere quelli serve una pesatura come la PPMI, che azzera *the*. Verificato con la cella 23 del notebook.

</details>

#### Esercizio 4 (scheda L10, libro 5.1): coseni sui conteggi di Wikipedia

Con i conteggi di Wikipedia della scheda 21 (cherry: pie 442, result 9; strawberry: pie 60, result 1; digital: pie 5, result 85): (a) usando solo le dimensioni *pie* e *result*, calcola cos(cherry, strawberry) e cos(cherry, digital). (b) Quale coppia è più simile, e il risultato corrisponde all'intuizione sul significato delle parole?

<details><summary>Soluzione</summary>

(a) Vettori [pie, result]: cherry [442, 9], strawberry [60, 1], digital [5, 85].

cos(cherry, strawberry) $= \dfrac{442\cdot60+9\cdot1}{\sqrt{442^2+9^2}\sqrt{60^2+1^2}} = \dfrac{26.529}{442{,}09\cdot60{,}008} = \dfrac{26.529}{26.529{,}2} = 0{,}99999$.

cos(cherry, digital) $= \dfrac{442\cdot5+9\cdot85}{442{,}09\cdot\sqrt{5^2+85^2}} = \dfrac{2210+765}{442{,}09\cdot85{,}147} = \dfrac{2975}{37.642} = 0{,}079$.

(b) cherry e strawberry sono molto più simili (quasi la stessa direzione: entrambe hanno quasi tutta la massa su *pie*), cherry e digital quasi ortogonali. Corrisponde all'intuizione: due frutti usati nei dolci contro una parola del lessico informatico. Nota: le dimensioni pie e result sono nella Fig. 5.3 del libro (la tabella di Wikipedia); il testo dell'esercizio 5.1 del libro rimanda per errore alla Fig. 5.2, che ha solo *a, computer, pie*; la scheda usa correttamente i conteggi giusti. Verificato con la cella 4 del notebook.

</details>

#### Esercizio 5 (scheda L10, libro 5.2): il coseno è invariante alla scala

(a) Mostra che per ogni costante positiva $c$ vale $\cos(c\mathbf v,\mathbf w) = \cos(\mathbf v,\mathbf w)$. (b) Perché è una proprietà desiderabile per una misura di similarità fra parole, data la discussione su frequenza e lunghezza dei vettori? (c) Il prodotto scalare è invariante alla scala? Quanto vale $\text{dot}(c\mathbf v,\mathbf w)$?

<details><summary>Soluzione</summary>

(a) $(c\mathbf v)\cdot\mathbf w = \sum_i cv_iw_i = c\,(\mathbf v\cdot\mathbf w)$ e $|c\mathbf v| = \sqrt{\sum_i c^2v_i^2} = |c|\,|\mathbf v| = c|\mathbf v|$ perché $c&gt;0$. Quindi

$$\cos(c\mathbf v,\mathbf w) = \frac{c\,(\mathbf v\cdot\mathbf w)}{c|\mathbf v||\mathbf w|} = \frac{\mathbf v\cdot\mathbf w}{|\mathbf v||\mathbf w|} = \cos(\mathbf v,\mathbf w).$$

(Con $c&lt;0$ il coseno cambia segno: $|c| = -c$.)

(b) Una parola che compare $c$ volte più spesso negli stessi contesti ha, in prima approssimazione, un vettore di conteggi $c$ volte più lungo con la stessa direzione. Il suo **uso**, cioè la distribuzione relativa dei contesti, è lo stesso, quindi il significato è lo stesso. Una misura invariante alla scala dà la stessa similarità indipendentemente dalla frequenza: è proprio ciò che si chiedeva nella scheda 25.

(c) No: $\text{dot}(c\mathbf v,\mathbf w) = c\,\text{dot}(\mathbf v,\mathbf w)$, cresce linearmente con $c$. Esempio della scheda 25: $\text{dot}(\mathbf v,\mathbf w) = 7{,}8$, $\text{dot}(\mathbf v, 2\mathbf w) = 15{,}6$, coseno 0,73 in entrambi i casi. Per questo il prodotto scalare grezzo favorisce le parole frequenti.

</details>

#### Esercizio 6 (scheda L10): prodotto scalare contro coseno sulle quattro finestre

Con i conteggi delle quattro finestre (cherry [1, 0, 1], strawberry [0, 0, 2], digital [0, 1, 0], information [1, 1, 0] sulle colonne a, computer, pie): (a) calcola dot(cherry, strawberry), dot(cherry, information), dot(digital, information) e i coseni corrispondenti. (b) Ordina le tre coppie per prodotto scalare e per coseno. Dove non coincidono gli ordinamenti, e perché? (c) Quanto vale cos(cherry, digital)? Che cosa significa un coseno 0 qui?

<details><summary>Soluzione</summary>

Lunghezze: $|cherry| = \sqrt2 = 1{,}414$, $|strawberry| = 2$, $|digital| = 1$, $|information| = \sqrt2$.

(a) dot(cherry, strawberry) $= 0+0+1\cdot2 = 2$, cos $= 2/(\sqrt2\cdot2) = 0{,}707$. dot(cherry, information) $= 1\cdot1+0+0 = 1$, cos $= 1/(\sqrt2\sqrt2) = 0{,}5$. dot(digital, information) $= 0+1\cdot1+0 = 1$, cos $= 1/(1\cdot\sqrt2) = 0{,}707$.

(b) Per prodotto scalare: cherry-strawberry (2) > cherry-information = digital-information (1). Per coseno: cherry-strawberry = digital-information (0,707) > cherry-information (0,5). Disaccordo su digital-information, che il prodotto scalare mette alla pari con cherry-information e sotto cherry-strawberry: il prodotto scalare premia *strawberry* perché il suo vettore è più lungo (conteggio 2 su *pie*), il coseno toglie questo effetto e premia *digital*, il cui unico contesto (*computer*) è condiviso con *information*. Il coseno separa anche cherry-information (che condividono solo *a*, un contesto poco significativo) da digital-information.

(c) cos(cherry, digital) $= 0/(\sqrt2\cdot1) = 0$: vettori **ortogonali**, nessun contesto in comune nelle finestre. Con conteggi non negativi 0 è il minimo possibile: massima dissimilarità misurabile, che qui vuol dire solo "nessuna evidenza di somiglianza" in un corpus di quattro finestre. Verificato con la cella 4 del notebook.

</details>

#### Esercizio 7 (scheda L10): vettori unitari

Siano $\mathbf v = [1, 1]$, $\mathbf w = [3, 3]$, $\mathbf u = [1, 0]$. (a) Calcola dot($\mathbf v$, $\mathbf u$), dot($\mathbf w$, $\mathbf u$), cos($\mathbf v$, $\mathbf u$), cos($\mathbf w$, $\mathbf u$). (b) Calcola i vettori unitari di $\mathbf v$ e $\mathbf w$. Quanto vale il prodotto scalare di ciascuno con $\mathbf u$? (c) In un motore di ricerca che confronta una query con milioni di documenti tramite il coseno, perché conviene memorizzare i documenti come vettori unitari?

<details><summary>Soluzione</summary>

(a) dot($\mathbf v$, $\mathbf u$) = 1, dot($\mathbf w$, $\mathbf u$) = 3. $|\mathbf v| = \sqrt2$, $|\mathbf w| = 3\sqrt2$, $|\mathbf u| = 1$: cos($\mathbf v$, $\mathbf u$) $= 1/\sqrt2 = 0{,}707$, cos($\mathbf w$, $\mathbf u$) $= 3/(3\sqrt2) = 0{,}707$. Stessa direzione ($\mathbf w = 3\mathbf v$), stesso coseno, prodotti scalari diversi.

(b) $\mathbf v/|\mathbf v| = [1/\sqrt2,\ 1/\sqrt2] = [0{,}707;\ 0{,}707]$ e $\mathbf w/|\mathbf w| = [3/(3\sqrt2),\ 3/(3\sqrt2)]$ = lo stesso vettore. Prodotto scalare con $\mathbf u$ (già unitario): 0,707 per entrambi, cioè il coseno.

(c) Il coseno è $\frac{\mathbf q}{|\mathbf q|}\cdot\frac{\mathbf d}{|\mathbf d|}$ (Eq. 11.8 del libro). Se ogni documento è salvato già normalizzato, le milioni di norme si calcolano una volta sola all'indicizzazione; a ogni query si normalizza solo la query (e per l'ordinamento non serve nemmeno: $|\mathbf q|$ è uguale per tutti i documenti), e il punteggio è un semplice prodotto scalare, sparso e veloce, eventualmente un unico prodotto matrice-vettore. È ciò che fanno `neighbors` e `search` nel notebook. Verificato con la cella 23.

</details>

#### Esercizio 8 (scheda L10): le quattro opere

Matrice termine-documento delle schede 34-35 (37 opere nella collezione). (a) Calcola la tf $= 1+\log_{10}\text{count}$ (0 per conteggio 0) di *battle* nelle quattro opere. (b) *battle* compare in 21 opere su 37, *good* in tutte e 37. Calcola i loro idf e il tf-idf di *battle* e di *good* nelle quattro opere. (c) Sui conteggi grezzi cos(As You Like It, Twelfth Night) = 0,950 e cos(As You Like It, Julius Caesar) = 0,945: le due commedie sono appena più vicine fra loro che una commedia e una tragedia. Spiega perché. (d) Con gli idf del libro per *fool* (0,012) e *wit* (0,037), calcola i vettori tf-idf di As You Like It, Twelfth Night e Julius Caesar sulle quattro parole, e i coseni di As You Like It con le altre due. Tf-idf aiuta su queste quattro parole? Perché?

<details><summary>Soluzione</summary>

(a) Conteggi di battle: 1, 0, 7, 13. tf: $1+\log_{10}1 = 1$; 0 (conteggio 0); $1+\log_{10}7 = 1+0{,}845 = 1{,}845$; $1+\log_{10}13 = 1+1{,}114 = 2{,}114$.

(b) idf(battle) $= \log_{10}(37/21) = \log_{10}1{,}762 = 0{,}246$; idf(good) $= \log_{10}(37/37) = 0$. tf-idf(battle) = [0,246; 0; 0,454; 0,520]; tf-idf(good) = [0; 0; 0; 0], qualunque sia la tf (3,057; 2,903; 2,792; 2,949).

(c) *good* ha conteggi enormi (114, 80, 62, 89) in tutte le opere e domina tutti i vettori, che puntano quasi tutti nella direzione di *good*. Nel prodotto scalare AYLI·TN = 11.508, il termine di good vale $114\cdot80 = 9120$; in AYLI·JC = 7151 vale $114\cdot62 = 7068$. Le dimensioni che distinguono davvero (fool, wit, battle) pesano poco. Senza la riga di good i coseni diventano 0,968 e 0,274.

(d) tf di fool: 2,556; 2,763; 1; di wit: 2,301; 2,176; 1,301. Vettori (battle, good, fool, wit):

- AYLI = [0,246; 0; 2,556·0,012; 2,301·0,037] = [0,246; 0; 0,031; 0,085], lunghezza 0,262;
- TN = [0; 0; 0,033; 0,081], lunghezza 0,087;
- JC = [0,454; 0; 0,012; 0,048], lunghezza 0,457.

cos(AYLI, TN) $= \dfrac{0{,}031\cdot0{,}033+0{,}085\cdot0{,}081}{0{,}262\cdot0{,}087} = \dfrac{0{,}0079}{0{,}0228} = 0{,}345$. cos(AYLI, JC) $= \dfrac{0{,}246\cdot0{,}454+0{,}031\cdot0{,}012+0{,}085\cdot0{,}048}{0{,}262\cdot0{,}457} = \dfrac{0{,}1161}{0{,}1197} = 0{,}970$.

Su queste quattro parole tf-idf **peggiora** le cose: ora la commedia è molto più vicina alla tragedia. Motivo: l'idf azzera *good* (bene) ma quasi azzera anche *fool* e *wit*, che compaiono in 36 e 34 opere su 37; resta una sola dimensione con peso sostanziale, *battle*, che As You Like It contiene (una volta) e Twelfth Night no. L'idf misura la rarità nella collezione, non la capacità di separare commedie e tragedie. Con il vocabolario completo (migliaia di parole: nomi di personaggi, luoghi, lessico specifico) le parole rare e caratteristiche fanno il lavoro; con quattro parole scelte a mano no. Verificato con la cella 24 del notebook (con gli idf esatti: 0,343 e 0,971).

</details>

#### Esercizio 9 (scheda L10, libro §11.1.3): quattro nano-documenti e una query

Documenti: Doc 1 *sweet sweet nurse love*; Doc 2 *sweet sorrow*; Doc 3 *how sweet is love*; Doc 4 *nurse*. Query: *sweet love*. (a) Calcola document frequency e idf ($N = 4$) delle sei parole sweet, love, nurse, sorrow, how, is. (b) Calcola il vettore tf-idf della query, di Doc 1 e di Doc 2 (tf = $1+\log_{10}$count). (c) Calcola il coseno della query con Doc 1 e con Doc 2. Quale documento viene messo al primo posto?

<details><summary>Soluzione</summary>

(a) df: sweet 3 (Doc 1, 2, 3), love 2 (Doc 1, 3), nurse 2 (Doc 1, 4), sorrow 1, how 1, is 1. idf: sweet $\log_{10}(4/3) = 0{,}125$; love e nurse $\log_{10}2 = 0{,}301$; sorrow, how, is $\log_{10}4 = 0{,}602$.

(b) Query: sweet tf 1 → 0,125; love tf 1 → 0,301; $|\mathbf q| = \sqrt{0{,}125^2+0{,}301^2} = \sqrt{0{,}0156+0{,}0906} = 0{,}326$.  
Doc 1: sweet count 2, tf $1+\log_{10}2 = 1{,}301$ → 0,163; nurse 0,301; love 0,301; $|\mathbf d_1| = \sqrt{0{,}163^2+0{,}301^2+0{,}301^2} = \sqrt{0{,}0264+0{,}0906+0{,}0906} = 0{,}456$.  
Doc 2: sweet 0,125; sorrow 0,602; $|\mathbf d_2| = \sqrt{0{,}0156+0{,}3625} = 0{,}615$.

(c) Solo le parole della query contribuiscono al prodotto scalare. $\mathbf q\cdot\mathbf d_1 = 0{,}125\cdot0{,}163+0{,}301\cdot0{,}301 = 0{,}0204+0{,}0906 = 0{,}1109$; $\cos = 0{,}1109/(0{,}326\cdot0{,}456) = 0{,}747$. $\mathbf q\cdot\mathbf d_2 = 0{,}125\cdot0{,}125 = 0{,}0156$; $\cos = 0{,}0156/(0{,}326\cdot0{,}615) = 0{,}078$. Primo Doc 1, che contiene entrambe le parole della query (e due volte *sweet*); Doc 2 contiene solo *sweet*, la parola meno informativa, e *sorrow*, rara, gli allunga il vettore. Per completezza: Doc 3 0,357, Doc 4 0. Valori del libro (Fig. 11.6: 0,747 e 0,0779) e della cella 16 del notebook.

</details>

#### Esercizio 10 (scheda L10): PPMI a mano

Conteggi dell'Appendice J (scheda 52), con totali di riga 486, 80, 3447, 7703, totali di colonna 4997, 5673, 473, 512, 61 e $N = 11.716$. (a) Calcola PPMI(cherry, pie) e PPMI(strawberry, sugar). (b) Calcola PMI(digital, pie). Quanto vale la sua PPMI, e perché il valore negativo si scarta? (c) PPMI(information, result) = 0,28 e PPMI(information, data) = 0,09, benché *information* compaia 3982 volte con *data* e solo 378 con *result*. Spiega.

<details><summary>Soluzione</summary>

Formula comoda: $\text{PMI} = \log_2\dfrac{f_{ij}\cdot N}{f_{i*}\cdot f_{*j}}$ (osservato / atteso).

(a) PPMI(cherry, pie): atteso $486\cdot512/11716 = 21{,}24$, osservato 442, rapporto 20,81, $\log_2 20{,}81 = 4{,}38$. PPMI(strawberry, sugar): atteso $80\cdot61/11716 = 0{,}417$, osservato 19, rapporto 45,6, $\log_2 45{,}6 = 5{,}51$. (Per il $\log_2$ con la calcolatrice: $\log_2 x = \ln x/\ln 2$.)

(b) PMI(digital, pie): atteso $3447\cdot512/11716 = 150{,}6$, osservato 5, rapporto 0,0332, $\log_2 0{,}0332 = -4{,}91$. PPMI = $\max(-4{,}91, 0) = 0$. Si scarta perché stimare che due parole co-occorrono **meno** del caso richiede molti dati (con probabilità piccole l'atteso stesso è piccolo e la stima è rumorosa), e perché non è chiaro che le associazioni negative siano utili o giudicabili; qui inoltre un osservato di 5 occorrenze è poca evidenza.

(c) La PMI confronta l'osservato con l'**atteso**, non guarda il conteggio assoluto. *information* e *data* sono entrambe frequentissime: per caso ci si aspetterebbero $7703\cdot5673/11716 = 3730$ co-occorrenze; le 3982 osservate sono solo 1,07 volte l'atteso, $\log_2 1{,}07 = 0{,}09$. Con *result*, contesto molto meno frequente, l'atteso è $7703\cdot473/11716 = 311$; 378 osservate sono 1,22 volte, $\log_2 1{,}22 = 0{,}28$. È esattamente il motivo per cui si usa la PMI: la frequenza grezza non è associazione. Verificato con la cella 24 del notebook.

</details>

#### Esercizio 11 (scheda L10): eventi rari e la pesatura α

(a) In un corpus con $N = 10^6$ coppie parola-contesto, una parola vista una volta co-occorre una volta con un contesto visto una volta. Calcola la sua PMI e confrontala con il valore massimo della matrice PPMI del libro, 5,51. (b) Tre contesti compaiono 900, 90 e 10 volte. Calcola $P(c)$ e $P_\alpha(c)$ con α = 0,75. Quali contesti guadagnano probabilità, e che cosa succede alla loro PMI? (c) L'esempio del libro: $P(a) = 0{,}99$ e $P(b) = 0{,}01$ danno $P_\alpha(a) = 0{,}97$ e $P_\alpha(b) = 0{,}03$. Verifica i due valori.

<details><summary>Soluzione</summary>

(a) $P(w,c) = 10^{-6}$, $P(w) = 10^{-6}$, $P(c) = 10^{-6}$: $\text{PMI} = \log_2\dfrac{10^{-6}}{10^{-6}\cdot10^{-6}} = \log_2 10^6 = 6\log_2 10 = 6\cdot3{,}32 = 19{,}9$ bit, quasi quattro volte il massimo della tabella (5,51, strawberry-sugar, che si basa su 19 co-occorrenze). Una sola co-occorrenza fra due eventi unici produce la massima associazione possibile: è il bias della PMI verso gli eventi rari.

(b) $P(c) = 900/1000, 90/1000, 10/1000 = 0{,}9;\ 0{,}09;\ 0{,}01$. Potenze: $900^{0{,}75} = 164{,}3$, $90^{0{,}75} = 29{,}2$, $10^{0{,}75} = 5{,}62$; somma 199,2. $P_\alpha = 0{,}825;\ 0{,}147;\ 0{,}028$. Guadagnano i due contesti meno frequenti (0,09 → 0,147; 0,01 → 0,028), perde quello frequente (0,9 → 0,825). Poiché $P_\alpha(c)$ sta al denominatore, la PMI di una coppia con il contesto da 10 occorrenze scende di $\log_2(0{,}028/0{,}01) = 1{,}50$ bit, con quello da 90 di 0,71 bit; con il contesto da 900 sale di 0,13 bit.

(c) $0{,}99^{0{,}75} = e^{0{,}75\ln0{,}99} = 0{,}9925$; $0{,}01^{0{,}75} = 10^{-1{,}5} = 0{,}0316$; somma 1,0241. $P_\alpha(a) = 0{,}9925/1{,}0241 = 0{,}969 \approx 0{,}97$; $P_\alpha(b) = 0{,}0316/1{,}0241 = 0{,}031\approx0{,}03$. Corretto. Verificato con la cella 24 del notebook.

</details>

#### Esercizio 12 (scheda L10): coseni sui vettori PPMI

Con la matrice PPMI del libro (scheda 56): (a) calcola cos(cherry, strawberry) e cos(digital, information) sulle righe PPMI. Sui conteggi grezzi delle stesse cinque colonne i due coseni sono 0,969 e 0,996. (b) *cherry* e *strawberry* restano molto simili; *digital* e *information* diventano molto meno simili. Spiega, guardando su quali colonne cade la loro PPMI. (c) Riassumi la ricetta della lezione, contare, pesare, confrontare: per le parole e per i documenti, quale matrice, quale pesatura e quale misura di similarità?

<details><summary>Soluzione</summary>

(a) cherry = [0, 0, 0, 4,38, 3,30], strawberry = [0, 0, 0, 4,10, 5,51]: dot $= 4{,}38\cdot4{,}10+3{,}30\cdot5{,}51 = 17{,}96+18{,}18 = 36{,}14$; lunghezze $\sqrt{19{,}18+10{,}89} = 5{,}484$ e $\sqrt{16{,}81+30{,}36} = 6{,}868$; cos $= 36{,}14/37{,}66 = 0{,}960$.

digital = [0,18; 0,01; 0; 0; 0], information = [0,02; 0,09; 0,28; 0; 0]: dot $= 0{,}18\cdot0{,}02+0{,}01\cdot0{,}09 = 0{,}0036+0{,}0009 = 0{,}0045$; lunghezze $\sqrt{0{,}0325} = 0{,}180$ e $\sqrt{0{,}0869} = 0{,}295$; cos $= 0{,}0045/0{,}0532 = 0{,}085$ (0,079 con i valori PPMI non arrotondati).

(b) *cherry* e *strawberry* hanno la PPMI sulle **stesse** colonne (*pie*, *sugar*), contesti distintivi: il coseno resta alto. *digital* e *information* avevano coseno 0,996 perché entrambe hanno conteggi enormi su *computer* e *data*; ma sono contesti frequentissimi, quindi la PPMI vi è quasi nulla. Ciò che resta di distintivo cade su colonne diverse: *digital* su *computer* (0,18), *information* su *result* (0,28) e *data* (0,09). Il coseno PPMI confronta ciò che è distintivo, non la frequenza. Su sole cinque colonne, tutte frequenti per le due parole, l'effetto è estremo: in una matrice vera avrebbero molti contesti distintivi in comune (*storage, retrieval, network*...).

(c) Parole (parole simili, vicini): matrice **parola-contesto** con finestra di ±k parole (una parola è una riga), pesatura **PPMI** (meglio con α = 0,75), similarità **coseno**. Documenti (ricerca, similarità fra documenti): matrice **termine-documento** (un documento è una colonna, una query è un documento corto), pesatura **tf-idf** (o BM25), similarità **coseno**. Stessa ricetta, contesto diverso: le parole vicine o il documento intero. Verificato con la cella 24 del notebook.

</details>

#### Esercizio aggiuntivo A: PPMI con α = 0,75 sulla tabella dell'Appendice J

Con i totali di colonna 4997, 5673, 473, 512, 61 (computer, data, result, pie, sugar): (a) calcola $P_\alpha(c)$ con α = 0,75 per i cinque contesti e confrontalo con $P(c)$. (b) Calcola PPMI$_\alpha$(cherry, pie) e PPMI$_\alpha$(information, data), sapendo che $P(\text{cherry}) = 0{,}0415$, $P(\text{information}) = 0{,}6575$, $P(\text{cherry, pie}) = 0{,}0377$, $P(\text{information, data}) = 0{,}3399$. (c) Commenta i due cambiamenti rispetto a 4,38 e 0,09.

<details><summary>Soluzione</summary>

(a) Potenze 0,75: $4997^{0{,}75} = 594{,}3$; $5673^{0{,}75} = 653{,}7$; $473^{0{,}75} = 101{,}4$; $512^{0{,}75} = 107{,}6$; $61^{0{,}75} = 21{,}8$; somma 1478,9. $P_\alpha$ = 0,402; 0,442; 0,069; 0,073; 0,015, contro $P$ = 0,427; 0,484; 0,040; 0,044; 0,005. I due contesti frequenti perdono, i tre rari guadagnano (sugar triplica).

(b) PPMI$_\alpha$(cherry, pie) $= \log_2\dfrac{0{,}0377}{0{,}0415\cdot0{,}0728} = \log_2 12{,}5 = 3{,}64$. PPMI$_\alpha$(information, data) $= \log_2\dfrac{0{,}3399}{0{,}6575\cdot0{,}4420} = \log_2 1{,}170 = 0{,}23$.

(c) cherry-pie scende da 4,38 a 3,64: *pie* è un contesto relativamente raro e ora ha probabilità più alta al denominatore. information-data sale da 0,09 a 0,23: *data* è frequentissimo e ora pesa meno al denominatore. α riduce la distanza fra le associazioni con contesti rari e frequenti; strawberry-sugar, la cella più alta, scende da 5,51 a 4,01. Verificato con numpy e con la cella 18 del notebook (matrice `with alpha = 0.75`).

</details>

#### Esercizio aggiuntivo B: la query battle con tf-idf (riquadro della scheda 46)

La query è la sola parola *battle*. (a) Mostra che, qualunque sia il peso tf-idf della query, il coseno con un documento $\mathbf d$ è $d_{battle}/|\mathbf d|$. (b) Calcola i coseni con le quattro opere usando i conteggi grezzi ridotti alle due dimensioni (battle, fool), e poi usando i vettori tf-idf completi della scheda 43. (c) Che cosa cambia nell'ordinamento?

<details><summary>Soluzione</summary>

(a) La query è $\mathbf q = [w, 0, 0, 0]$ con $w&gt;0$ (tf 1 per idf 0,246): $\mathbf q\cdot\mathbf d = w\,d_{battle}$, $|\mathbf q| = w$, quindi $\cos = d_{battle}/|\mathbf d|$: il peso della query si semplifica.

(b) Conteggi grezzi (battle, fool): AYLI $1/\sqrt{1+1296} = 0{,}028$; TN $0/58 = 0$; JC $7/\sqrt{50} = 0{,}990$; HV $13/\sqrt{185} = 0{,}956$. Sono i numeri della figura della slide. tf-idf (battle, good, fool, wit): AYLI $0{,}246/0{,}262 = 0{,}939$; TN 0; JC $0{,}454/0{,}457 = 0{,}994$; HV $0{,}520/0{,}523 = 0{,}994$.

(c) In entrambi i casi Julius Caesar ed Henry V vengono prima e Twelfth Night ultima, ma con tf-idf As You Like It passa da 0,03 a 0,94, quasi alla pari: il suo unico *battle* pesa molto perché *good* è azzerato e *fool*, *wit* quasi. Lezione: con un coseno la presenza di un termine raro della query conta molto, anche con tf bassa, se il resto del documento ha pesi piccoli. Verificato con numpy.

</details>

### Domande tipo orale

<details><summary>Che cosa dovrebbe saper rappresentare un modello del significato delle parole? Distingui similarità e relatedness.</summary>

Traccia: (1) rappresentare il significato con una stringa o un indice (DOG, LIFE') non dice niente; (2) desiderata: parole simili (cat/dog) e antonimi (hot/cold), connotazioni (happy/sad), prospettive sullo stesso evento (buy/sell/pay), inferenze per QA e dialogo; (3) sensi e polisemia (mouse), sinonimia approssimata e principio di contrasto (H2O/water); (4) similarità: le parole condividono proprietà (cat/dog, SimLex-999); relatedness o associazione: partecipano allo stesso evento o campo semantico (coffee/cup, surgeon/scalpel); (5) i vettori distribuzionali catturano entrambe, in misura che dipende dalla finestra.

</details>

<details><summary>Che cos'è l'ipotesi distribuzionale? Raccontala con l'esempio di ongchoi.</summary>

Traccia: (1) parole che compaiono in contesti simili tendono ad avere significati simili (Joos 1950, Harris 1954, Firth 1957; oculist/eye-doctor vicino a eye, examined); (2) la differenza di significato corrisponde grosso modo alla differenza di ambienti; (3) ongchoi compare con garlic, rice, delicious, salty, leaves; gli stessi contesti di spinach, chard, collard greens: quindi è una verdura a foglia (è lo spinacio d'acqua); (4) il confronto è indiretto, fra i contesti; (5) computazionalmente: contare le parole nel contesto e confrontare i vettori di conteggi.

</details>

<details><summary>Che cosa sono gli embedding? Sparsi contro densi, statici contro contestuali.</summary>

Traccia: (1) rappresentazioni vettoriali del significato delle parole apprese dalla loro distribuzione nei testi; esempio di representation learning self-supervised, al posto delle feature a mano; (2) l'idea parte da Osgood (valence, arousal, dominance: una parola è un punto); (3) sparsi: $|V|$ dimensioni (10-50 mila), conteggi o loro pesature (tf-idf, PPMI), quasi tutti zeri, dimensioni interpretabili; densi: 50-1000 numeri reali senza interpretazione, appresi (word2vec), migliori nei compiti; (4) statici: un vettore per parola; contestuali (BERT): un vettore per occorrenza, risolvono la polisemia; (5) utilità: un classificatore generalizza a parole mai viste se ha visto parole con vettori vicini.

</details>

<details><summary>Come si costruisce una matrice parola-contesto? Che effetto ha la dimensione della finestra?</summary>

Traccia: (1) righe = parole target, colonne = parole di contesto, $|V|\times|V|$; (2) cella $(w,c)$ = numero di volte che $c$ compare entro ±k parole da un'occorrenza di $w$ (k = 4 nell'esempio); (3) esempio delle quattro finestre: cherry = [1, 0, 1] su a, computer, pie; (4) su Wikipedia: cherry e strawberry hanno la massa su pie e sugar, digital e information su computer e data; (5) la matrice è sparsa (Zipf), si memorizza in forma sparsa; (6) finestre corte (1-3) danno vicini sintatticamente simili, lunghe danno vicini dello stesso argomento.

</details>

<details><summary>Perché non si usa il prodotto scalare grezzo come misura di similarità? Definisci il coseno e il suo intervallo.</summary>

Traccia: (1) $\mathbf v\cdot\mathbf w = \sum_i v_iw_i$: alto se i vettori hanno valori grandi nelle stesse dimensioni, 0 se ortogonali; (2) cresce con la lunghezza $|\mathbf v| = \sqrt{\sum v_i^2}$, e le parole frequenti hanno vettori più lunghi: bias della frequenza ($\text{dot}(c\mathbf v,\mathbf w) = c\,\text{dot}$); (3) coseno = prodotto scalare diviso le due lunghezze = $\cos\theta$, dipende solo dalla direzione, invariante alla scala; (4) intervallo $[-1, 1]$; per conteggi non negativi $[0, 1]$; (5) per vettori unitari prodotto scalare = coseno: si normalizza una volta e poi si fanno prodotti scalari; (6) esempio: cos(digital, information) = 0,996, cos(cherry, information) = 0,018.

</details>

<details><summary>Calcola a mano un coseno fra due vettori di conteggi e interpreta il risultato.</summary>

Traccia: (1) scrivere i vettori sulle stesse dimensioni, nello stesso ordine; (2) prodotto scalare; (3) le due lunghezze; (4) rapporto. Esempio: cherry [442, 8, 2] e information [5, 3982, 3325] su pie, data, computer: dot = 2210+31.856+6650 = 40.716; lunghezze 442,08 e 5187,7; coseno 0,018, quasi ortogonali. digital [5, 1683, 1670] con information: dot 12.254.481, lunghezze 2371,0 e 5187,7, coseno 0,996. (5) Interpretazione: information è molto più vicina a digital; le lunghezze diverse (frequenza) non contano.

</details>

<details><summary>Che cos'è la matrice termine-documento e perché sui conteggi grezzi As You Like It sembra simile a Julius Caesar?</summary>

Traccia: (1) righe = parole, colonne = documenti; cella = occorrenze della parola nel documento (fool 58 volte in Twelfth Night); vector space model di Salton, bag of words; (2) un documento è un vettore colonna, una parola è un vettore riga; (3) sulle dimensioni fool e battle le commedie si separano bene dalle tragedie; (4) ma sui quattro conteggi cos(AYLI, TN) = 0,950 e cos(AYLI, JC) = 0,945: good (114, 80, 62, 89) compare in tutte le opere e domina tutti i vettori (79% e 99% dei prodotti scalari); (5) serve pesare: togliere peso alle parole presenti dappertutto.

</details>

<details><summary>Definisci tf, idf e tf-idf. Quale problema risolve ciascun ingrediente?</summary>

Traccia: (1) tf $= 1+\log_{10}\text{count}(t,d)$ se count > 0, altrimenti 0: 100 occorrenze non valgono 100 volte una; ogni fattore 10 aggiunge 1; il +1 distingue 1 da 0; (2) df = numero di documenti che contengono il termine; idf $= \log_{10}(N/\text{df})$ (Sparck Jones 1972): 0 per un termine in tutti i documenti, alto per uno raro (Romeo 1,57, battle 0,246, good 0); (3) tf-idf = tf × idf: alto per parole frequenti nel documento e rare nella collezione; (4) esempio: battle in Julius Caesar $(1+\log_{10}7)\cdot0{,}246 = 0{,}454$; (5) catena: conteggio → tf (crescita lenta) → idf (good a 0) → tf-idf.

</details>

<details><summary>Come funziona il recupero di documenti con tf-idf? Fai l'esempio della query sweet love.</summary>

Traccia: (1) ad hoc retrieval: una query, una collezione, documenti ordinati per rilevanza; (2) la query è un documento corto pesato con tf e con l'idf della collezione; (3) punteggio = coseno fra vettore della query e del documento; equivalentemente prodotto scalare dei vettori normalizzati; contribuiscono solo i termini della query; (4) esempio: idf sweet 0,125, love 0,301; Doc 1 (sweet sweet nurse love) coseno 0,747, Doc 2 (sweet sorrow) 0,078; (5) in pratica indice invertito per trovare i documenti candidati, varianti come BM25 (parametri $k$ e $b$); (6) limite: confronta le parole, non il significato (datetime non trovato da "date" nel notebook).

</details>

<details><summary>Che cos'è la PMI? Come si legge il suo valore? Che differenza c'è con la mutual information?</summary>

Traccia: (1) la frequenza grezza non è associazione: the co-occorre con tutto; (2) $\text{PMI}(w,c) = \log_2\frac{P(w,c)}{P(w)P(c)}$: co-occorrenza osservata contro quella attesa sotto indipendenza, in bit (Fano 1961; Church e Hanks 1989); (3) 0 = come il caso, positiva = più del caso (cherry-pie 4,38, circa 21 volte), negativa = meno (cherry-computer −6,70); (4) forma con i conteggi: $\log_2(f_{wc}N/(f_wf_c))$; (5) la mutual information fra due variabili è la media della PMI su tutte le coppie, sempre $\ge 0$; la PMI è di una cella e può essere negativa.

</details>

<details><summary>Perché si usa la PPMI invece della PMI? Calcolane un valore dalla tabella.</summary>

Traccia: (1) PMI va da $-\infty$ a $+\infty$; i negativi sono inaffidabili: con $P(w) = P(c) = 10^{-6}$ servirebbe un corpus enorme per dire che $P(w,c)$ è significativamente sotto $10^{-12}$; e $\log 0 = -\infty$ per le coppie mai viste; (2) PPMI = max(PMI, 0) (Niwa e Nitta 1994), la matrice resta sparsa; (3) dalla tabella: $p_{ij} = f_{ij}/N$, marginali da righe e colonne, $N = 11.716$; (4) information-data: $\log_2(0{,}3399/(0{,}6575\cdot0{,}4842)) = 0{,}094$, piccola perché entrambe frequenti (atteso 3730, osservato 3982); cherry-pie 4,38; (5) attenzione agli arrotondamenti: con 0,0002 al posto di 0,000171 si ottiene −6,47 invece di −6,70.

</details>

<details><summary>Qual è il problema della PMI con gli eventi rari e come si corregge?</summary>

Traccia: (1) una parola vista una volta in un contesto visto una volta riceve PMI altissima: con $N = 10^6$, $\log_2 10^6 = 19{,}9$ bit da una sola co-occorrenza; nel notebook le celle più alte sono coppie viste 2 volte; (2) correzione di Levy et al. (2015): $P_\alpha(c) = \text{count}(c)^\alpha/\sum\text{count}(c')^\alpha$ con α = 0,75 al denominatore; (3) la potenza < 1 appiattisce la distribuzione: i contesti rari guadagnano probabilità (0,01 → 0,03), quindi PMI più bassa; (4) sulla tabella: cherry-pie 4,38 → 3,64, information-data 0,09 → 0,23; (5) alternativa: add-k sui conteggi (k da 0,1 a 3), come per gli n-gram; troppo smoothing su una matrice grande appiattisce tutto.

</details>

<details><summary>Che cosa cambia nei coseni passando dai conteggi alla PPMI? Usa cherry/strawberry e digital/information.</summary>

Traccia: (1) sui conteggi i coseni sono dominati dalle colonne frequenti: cherry-strawberry 0,969, digital-information 0,996; (2) PPMI: cherry e strawberry hanno associazioni forti sulle stesse colonne (pie, sugar), coseno 0,960; (3) digital e information hanno PPMI quasi nulla su computer e data (contesti che compaiono con tutto) e il resto cade su colonne diverse: coseno 0,079 (0,085 con i valori arrotondati); (4) il coseno PPMI confronta ciò che è distintivo, non la frequenza; (5) nel notebook: i vicini di error, directory, socket passano da parole funzionali a parole dello stesso campo.

</details>

<details><summary>Riassumi la ricetta contare-pesare-confrontare per parole e per documenti.</summary>

Traccia: (1) domanda di partenza: che cosa voglio confrontare; (2) documenti: contesto = documento intero, matrice termine-documento (colonne), tf-idf (frequente qui, raro altrove), coseno; usi: ricerca, similarità fra documenti; (3) parole: contesto = parole vicine (finestra ±k), matrice parola-contesto (righe), PPMI con α = 0,75 (più del caso), coseno; usi: vicini, parafrasi, cambiamenti di significato; (4) le due pesature fanno lo stesso lavoro (tolgono peso a ciò che compare dappertutto): idf contando documenti, PMI confrontando con il caso; (5) prossimo passo: vettori densi appresi, word2vec, che ottimizza implicitamente una PMI spostata.

</details>
