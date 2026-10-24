# L11 · Embedding word2vec

*Word2vec embeddings* · 09/10/2026 · Claudio Gallicchio · lettura: J&M cap. 5, §5.5-5.10

[Versione interattiva sul sito](https://gabriele-marsili.github.io/appunti-magistrale-ai/anno-2/hlt/sito/#L11) · [Indice della dispensa](README.md)

Seconda lezione sugli embedding (J&M §5.5-5.10): dai vettori sparsi di conteggi a quelli **densi e appresi**. Il centro è **skip-gram con negative sampling** (word2vec): una regressione logistica che, con la **sigmoide del prodotto scalare**, distingue le coppie (target, contesto) vere da coppie con **parole di rumore** estratte con $P_\alpha$ ($\alpha = 0{,}75$); si scrivono la **loss**, i **gradienti** e un passo di **SGD** a mano, e si tengono come embedding i pesi $W$ (o $W + C$). Poi CBOW, fasttext e GloVe, gli effetti della finestra, le **analogie** con il parallelogramma, la semantica storica, i **bias** (danni allocativi e rappresentazionali) e la **valutazione** intrinseca ed estrinseca. Tutti i numeri delle slide sono ricalcolati e tornano; c'è solo un refuso a pagina 50 (*potatoe* per *potato*).

## Indice

- [Apertura](#apertura)
- [Dal contare al predire](#dal-contare-al-predire)
- [Il classificatore skip-gram](#il-classificatore-skip-gram)
- [Imparare gli embedding](#imparare-gli-embedding)
- [Altri embedding statici](#altri-embedding-statici)
- [Proprietà degli embedding](#proprieta-degli-embedding)
- [Bias e valutazione](#bias-e-valutazione)
- [Riepilogo](#riepilogo)
- [Notebook](#notebook)
- [Studio ed esercizi](#studio-ed-esercizi)

## Apertura

<a id="p-1"></a>

### Slide 1 · Embedding word2vec

Undicesima lezione, seconda parte del capitolo 5 di J&M (§5.5-5.10). Nella [L10](L10-semantica-vettoriale.md#p-15) gli embedding erano **vettori sparsi** di conteggi, lunghi $|V|$ e pesati con tf-idf o PPMI. Qui si passa agli embedding **densi** (d = 50-1000) che si **imparano** invece di contarli:

- **skip-gram con negative sampling** (SGNS), l'algoritmo principale di **word2vec**: una regressione logistica ([L6](L06-regressione-logistica.md#p-20)) che distingue coppie (parola, contesto) vere da coppie con parole di rumore;
- la **loss**, i **gradienti** e un passo di **SGD** fatto a mano;
- gli altri embedding statici: **CBOW**, **fasttext**, **GloVe**;
- che cosa catturano: finestra, **analogie** (king − man + woman ≈ queen), cambiamento di significato nel tempo;
- i **bias** che ereditano dal testo e come si **valutano**.

Il sottotitolo riassume i cinque temi: skip-gram, negative sampling, proprietà, bias, valutazione.

<a id="p-2"></a>

### Slide 2 · Indice della lezione

Sei blocchi:

1. **Dal contare al predire**: perché vettori corti e densi, l'idea di word2vec, la self-supervision (§5.5).
2. **Il classificatore skip-gram**: dal prodotto scalare a una probabilità con la sigmoide (§5.5.1).
3. **Imparare gli embedding**: esempi positivi e negativi, la scelta delle parole di rumore, la loss, i gradienti, un passo di SGD (§5.5.2).
4. **Altri embedding statici**: CBOW, fasttext, GloVe (§5.5.3).
5. **Proprietà degli embedding**: visualizzazione, finestra, analogie, semantica storica (§5.6-5.7).
6. **Bias e valutazione** (§5.8-5.9).

La pausa cade fra il blocco 3 e il blocco 4: la prima metà è tutta sull'algoritmo, la seconda su che cosa ne esce.

<a id="p-3"></a>

### Slide 3 · Riferimento: J&M capitolo 5, §5.5-5.10

Lettura: **Jurafsky & Martin**, *Speech and Language Processing*, 3a ed. draft del 19 agosto 2026, capitolo 5 (*Embeddings*), sezioni 5.5-5.10, pagine stampate 136-148:

- 5.5 Word2vec (136-142): il classificatore, l'apprendimento, gli altri embedding statici;
- 5.6 Visualizzare gli embedding (142-143);
- 5.7 Proprietà semantiche, con analogie e semantica storica (143-145);
- 5.8 Bias ed embedding (145-147);
- 5.9 Valutare i modelli vettoriali (147);
- 5.10 Riepilogo (148).

Gli esercizi del capitolo sono a pagina 150: il 5.3 (derivare i gradienti di SGNS) è l'esercizio 6 della scheda di oggi. Le Historical Notes (148-150) raccontano da dove viene la parola *embedding* (LSA, anni '90) e citano CBOW, che il testo del capitolo non descrive.

## Dal contare al predire

<a id="p-4"></a>
**Slide 4 · Dal contare al predire** — Primo blocco: vettori corti e densi, e l'idea di impararli con un classificatore.

<a id="p-5"></a>

### Slide 5 · Vettori corti e densi

Un **embedding** nel senso di oggi è un vettore **corto** ($d$ da 50 a 1000, tipicamente 300) e **denso**, invece dei vettori lunghi $|V|$ della lezione scorsa.

- **Sparso**: *cherry* = [0, 0, 2, 0, 0, 8, 0, ..., 442, 0, 25, 0, ...], una dimensione per parola del vocabolario ($|V|$ = 50.000), quasi tutti zeri. I numeri sono i conteggi di Wikipedia della [scheda 21 della L10](L10-semantica-vettoriale.md#p-21) (442 con *pie*, 25 con *sugar*); ogni dimensione ha un significato (la colonna *pie*).
- **Denso**: *cherry* = [0,13; −0,42; 0,07; 0,91; ...; −0,28], $d$ = 300 numeri reali, quasi mai zero, **senza interpretazione chiara**: la dimensione 17 non vuol dire niente da sola, conta la posizione del vettore rispetto agli altri.

Due differenze da ricordare: i valori sono **reali e possono essere negativi** (i conteggi e la PPMI no), quindi anche il coseno fra due embedding densi può essere negativo, non più solo fra 0 e 1 come nella [L10](L10-semantica-vettoriale.md#p-27). E sono **appresi**, non contati. In memoria: 300 numeri per parola invece di una riga di 50.000 (anche se in formato sparso si salvano solo i non-zero).

<a id="p-6"></a>

### Slide 6 · Perché i vettori densi funzionano meglio

Il libro afferma che i vettori densi **funzionano meglio di quelli sparsi in ogni compito di NLP**, e ammette che le ragioni non sono del tutto capite. Due intuizioni:

- **Numero di parametri**: un classificatore che riceve vettori a 300 dimensioni impara molti meno pesi che su 50.000. Meno parametri, meno rischio di **overfitting** e forse migliore generalizzazione (cfr. [overfitting nella L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-54)).
- **Sinonimia**: nei vettori sparsi le dimensioni *car* e *automobile* sono due colonne distinte e scollegate. Una parola che ha *car* fra i vicini e una che ha *automobile* non hanno nulla in comune su quelle dimensioni. Nei vettori densi *car* e *automobile* finiscono vicini, e l'informazione passa.

Esempio concreto (esercizio 1): un classificatore di sentiment addestrato su recensioni con *car* ma mai con *automobile*. Con il bag of words il peso della colonna *automobile* non è mai stato aggiornato; con la somma degli embedding la recensione *this automobile is great* produce un input vicino a quello di *this car is great*.

> **Da saper fare: Contare i pesi (esercizio 1a)**
>
> Regressione logistica binaria: un peso per ogni dimensione dell'input ([L6](L06-regressione-logistica.md#p-20)). Bag of words: **50.000** pesi; somma degli embedding: **300** pesi. Più il bias in entrambi i casi. Gli embedding però vanno imparati a parte: skip-gram ne ha $2\times50.000\times300 = 30$ milioni di parametri (scheda 17), ma li impara da testo grezzo, senza etichette.

<a id="p-7"></a>

### Slide 7 · Word2vec: skip-gram con negative sampling

L'idea in una frase: **invece di contare** quante volte $c$ compare vicino ad *apricot*, si addestra un **classificatore binario** a rispondere alla domanda *è probabile che $c$ compaia vicino ad apricot?*

- **SGNS**, *skip-gram with negative sampling*: uno dei due algoritmi del pacchetto **word2vec** (Mikolov et al., 2013); per estensione, l'algoritmo stesso si chiama spesso word2vec. Veloce, efficiente, disponibile online con codice ed embedding preaddestrati.
- **Embedding statici**: un vettore fisso per parola del vocabolario, come nella [L10](L10-semantica-vettoriale.md#p-11). *bank* ha lo stesso vettore in ogni frase; gli embedding **contestuali** (BERT) arriveranno al capitolo 9.
- **Gli embedding sono i pesi**: la previsione in sé non interessa. Il compito è un pretesto; quello che si tiene alla fine sono i **pesi appresi** dal classificatore, che sono i vettori delle parole.

È lo stesso schema del representation learning della [scheda 30 della L6](L06-regressione-logistica.md#p-30): invece di progettare le feature, si impara una rappresentazione risolvendo un compito.

<a id="p-8"></a>

### Slide 8 · Contare e predire

|  | i dati | il metodo | il vettore |
| --- | --- | --- | --- |
| **contare** (L10) | testo, finestra di ±k parole attorno a ogni parola | contare le coppie, poi pesarle con PPMI | lungo e sparso, $|V|$ = 50.000, quasi tutti zeri |
| **predire** (word2vec) | lo stesso testo, la stessa finestra: coppie parola-contesto | addestrare un classificatore: *c è un vero contesto di w?* | corto e denso, d = 300 pesi appresi |

Lo schema della slide mette in parallelo le due righe, con frecce da sinistra a destra. Il punto: **stesso testo, stessa finestra**, quindi la stessa ipotesi distribuzionale ([L10](L10-semantica-vettoriale.md#p-9)). Cambia solo che cosa si fa con le coppie: le si conta, oppure si impara a riconoscerle.

In entrambi i casi due parole si confrontano con il **coseno** dei loro vettori. Vedremo alla scheda 40 che le due strade sono più vicine di quanto sembri: SGNS fattorizza implicitamente una matrice PMI.

<a id="p-9"></a>

### Slide 9 · Self-supervision

La trovata decisiva: il **testo stesso** è il training set. Una parola che compare davvero vicino ad *apricot* è la risposta corretta (gold) alla domanda *c compare vicino ad apricot?*.

- **Self-supervision**: nessuna etichetta scritta a mano. La supervisione c'è (il classificatore ha etichette 1/0), ma la fornisce il corpus. Per questo si possono usare miliardi di parole: gli embedding preaddestrati di word2vec vengono da circa 100 miliardi di parole di notizie.
- **Origine**: l'idea viene dai **language model neurali** (Bengio et al., 2003; Collobert et al., 2011): la parola successiva nel testo fa da segnale di supervisione, e durante il training si impara un embedding per ogni parola. È lo stesso principio del language modeling della [L4](L04-modelli-linguistici-n-gram.md#p-5): predire la prossima parola non richiede annotazioni.

È la stessa idea che sta sotto il pretraining dei large language model: un compito ricavato dal testo grezzo, una rappresentazione come sottoprodotto.

<a id="p-10"></a>

### Slide 10 · Due semplificazioni rispetto a un language model neurale

Word2vec è **molto più semplice** di un language model neurale, in due modi:

- **Il compito**: classificazione **binaria** (questa coppia è vera o no?) invece di **predire la parola**. Predire la parola vuol dire scegliere fra $|V|$ classi, con una softmax su 50.000 punteggi ([L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-7)) da calcolare per ogni esempio; la classificazione binaria richiede una sola sigmoide per coppia.
- **L'architettura**: una **regressione logistica** invece di una rete neurale con strati nascosti, che richiede algoritmi di training più sofisticati (le reti neurali sono il capitolo 6).

Il prezzo di questa semplicità: word2vec non è un language model, non sa generare testo né dare la probabilità di una frase. Ma lo scopo è solo ottenere buoni vettori, e per quello basta.

<a id="p-11"></a>

### Slide 11 · L'intuizione di skip-gram

Quattro passi, nella striscia in alto della slide (riquadri colorati con frecce):

1. **Esempi positivi**: la parola target e una parola vicina, presa dalla finestra (*target + neighbor*).
2. **Esempi negativi**: la parola target e una parola presa **a caso** dal lessico (*target + noise word*).
3. **Classificatore**: una **regressione logistica** addestrata a distinguere i due casi.
4. **Embedding**: i pesi appresi.

È la regressione logistica binaria della [L6](L06-regressione-logistica.md#p-20), con una differenza importante: lì l'input $\mathbf x$ era fisso (le feature della recensione) e si imparavano i pesi $\mathbf w$; qui entrambi i vettori del prodotto scalare, quello del target e quello del contesto, sono parametri da imparare. Il nome *skip-gram* viene dal modello originale: dalla parola centrale si predicono le parole del contesto, "saltando" la posizione centrale.

## Il classificatore skip-gram

<a id="p-12"></a>
**Slide 12 · Il classificatore skip-gram** — Secondo blocco, primo passo della tabella di marcia (classificatore → esempi ± → loss → discesa del gradiente → embedding): c è un vero contesto?

<a id="p-13"></a>

### Slide 13 · Target e parole di contesto

Frase del libro, finestra di **±2** parole attorno al target $w$ = *apricot*:

```
... lemon,  a [tablespoon of apricot jam,  a] pinch ...
              c1        c2     w     c3    c4
```

I quattro contesti sono *tablespoon, of, jam, a* (la virgola non conta come parola). Il classificatore riceve una coppia $(w, c)$ e restituisce

$$P(+\mid w,c)$$

la probabilità che $c$ sia un **vero contesto** di $w$: alta per (*apricot, jam*), bassa per (*apricot, aardvark*). La probabilità del caso opposto è il complemento:

$$P(-\mid w,c) = 1 - P(+\mid w,c)$$

Le due etichette + e − sono le classi $y = 1$ e $y = 0$ della regressione logistica. Si noti che $P(+\mid w,c)$ non è la $P(c\mid w)$ di un language model: non è una distribuzione su tutte le parole $c$ (sommata su $c$ non dà 1), ma una probabilità binaria per ciascuna coppia.

<a id="p-14"></a>

### Slide 14 · Dal prodotto scalare alla similarità

$$\text{Similarity}(w,c) \approx \mathbf c\cdot\mathbf w$$

L'intuizione: una parola compare probabilmente vicino al target se il suo embedding è **simile** a quello del target. E due vettori sono simili se hanno un **prodotto scalare alto**: il coseno della [L10](L10-semantica-vettoriale.md#p-26) non è altro che il prodotto scalare normalizzato.

Lo schema in basso: **w** (target) e **c** (contesto) entrano nel **prodotto scalare** $\mathbf c\cdot\mathbf w$, che è un numero reale qualunque; la **sigmoide** lo trasforma in $P(+\mid w,c)$, un numero fra 0 e 1.

Perché il prodotto scalare e non il coseno? È più semplice da derivare e il training sceglie da solo le lunghezze dei vettori. Dopo il training, per confrontare due parole fra loro si usa invece il coseno, come per i vettori sparsi (scheda 8). Attenzione al senso di "simile": qui $\mathbf c$ viene dalla matrice dei contesti e $\mathbf w$ da quella dei target (scheda 17), quindi "simile" vuol dire "compare spesso vicino".

<a id="p-15"></a>

### Slide 15 · Dal prodotto scalare a una probabilità: la sigmoide

$$\sigma(x) = \frac{1}{1+\exp(-x)}\qquad P(+\mid w,c) = \sigma(\mathbf c\cdot\mathbf w) = \frac{1}{1+\exp(-\mathbf c\cdot\mathbf w)}$$

Il prodotto scalare va da $-\infty$ a $+\infty$ (le componenti degli embedding possono essere negative), quindi non è una probabilità. La **sigmoide** della regressione logistica ([L6, scheda 22](L06-regressione-logistica.md#p-22)) lo schiaccia in $(0, 1)$.

Il grafico a destra: curva a S blu, in ascissa il prodotto scalare $\mathbf c\cdot\mathbf w$ da −6 a 6, in ordinata $\sigma$ da 0 a 1; il punto rosso segna $\sigma(0) = 0{,}5$; le annotazioni dicono *prodotto grande → vicino a 1*, *molto negativo → vicino a 0*.

- Due vettori **ortogonali** (prodotto 0) danno 0,5: il classificatore non sa decidere.
- Nessun bias: rispetto alla regressione logistica della L6 manca il termine $b$, la probabilità dipende solo dal prodotto scalare.

<a id="p-16"></a>

### Slide 16 · Un'intera finestra di contesto

$$P(-\mid w,c) = 1-P(+\mid w,c) = \sigma(-\mathbf c\cdot\mathbf w) = \frac{1}{1+\exp(\mathbf c\cdot\mathbf w)}$$

Le due probabilità sommano a 1, e la seconda è la **sigmoide di meno il prodotto scalare**, grazie alla simmetria $1-\sigma(x) = \sigma(-x)$.

Per una finestra di $L$ contesti, skip-gram assume che le parole di contesto siano **indipendenti**: le probabilità si moltiplicano e i logaritmi si sommano.

$$P(+\mid w,c_{1:L}) = \prod_{i=1}^{L}\sigma(\mathbf c_i\cdot\mathbf w)\qquad \log P(+\mid w,c_{1:L}) = \sum_{i=1}^{L}\log\sigma(\mathbf c_i\cdot\mathbf w)$$

La probabilità di una finestra dipende solo dai prodotti scalari del target con ciascun contesto: l'ordine delle parole nella finestra e la loro distanza dal target non contano. È la stessa ipotesi "ingenua" del Naive Bayes ([L6, scheda 15](L06-regressione-logistica.md#p-15)), falsa ma comoda.

> **Da saper fare: Perché 1 − σ(x) = σ(−x)**
>
> $1-\frac{1}{1+e^{-x}} = \frac{e^{-x}}{1+e^{-x}}$; moltiplicando numeratore e denominatore per $e^{x}$: $\frac{1}{e^{x}+1} = \sigma(-x)$. Esempio: $\sigma(1) = 0{,}731$, $\sigma(-1) = 0{,}269$, somma 1. Serve nella loss (scheda 24) e nei gradienti, insieme a $\sigma'(x) = \sigma(x)(1-\sigma(x))$.

<a id="p-17"></a>

### Slide 17 · Due embedding per ogni parola

Per calcolare queste probabilità servono un embedding per ogni parola come **target** e uno per ogni parola come **contesto**. Skip-gram ne tiene quindi **due per parola**:

- la matrice $W$ dei **target embedding** (detti anche *input embedding*), righe 1..$|V|$ della figura, in verde, da *aardvark* a *zebra*;
- la matrice $C$ dei **context embedding** (o *output embedding*), righe $|V|+1$..$2|V|$, in viola: servono sia per i contesti veri sia per le parole di rumore.

I parametri $\theta$ sono la concatenazione delle due: **$2|V|$ vettori di dimensione $d$**. Con $|V| = 50.000$ e $d = 300$: $2\times50.000\times300 = 30$ milioni di numeri. Imparare questi vettori è il vero scopo del training.

Parallelo con la L10: $W$ fa la parte delle **righe** della matrice parola-contesto (le parole), $C$ quella delle **colonne** (i contesti); il prodotto $\mathbf c\cdot\mathbf w$ fa la parte della cella.

> **Approfondimento: Perché non un solo vettore per parola**
>
> Una ragione spesso citata (Goldberg e Levy, 2014; non è nel libro): con un vettore unico, $P(+\mid w,w) = \sigma(\mathbf w\cdot\mathbf w) = \sigma(|\mathbf w|^2)$ sarebbe sempre alta, cioè ogni parola sarebbe considerata un buon contesto di sé stessa, mentre raramente una parola compare accanto a sé. Con due matrici separate il modello è libero di dare a $\mathbf w_i\cdot\mathbf c_i$ il valore che i dati richiedono.

<a id="p-18"></a>

### Slide 18 · Il classificatore: un esempio

Tre embedding giocattolo con $d = 3$, non appresi da un corpus:

|  | parola | embedding |
| --- | --- | --- |
| w | apricot | [0,5; 1,0; −0,5] |
| c | jam | [1,0; 0,5; 0,0] |
| c | matrix | [−0,5; 0,5; 1,0] |

- $\text{dot}(jam, apricot) = 0{,}5 + 0{,}5 + 0{,}0 = 1{,}00$, quindi $P(+\mid apricot, jam) = \sigma(1) = 0{,}73$.
- $\text{dot}(matrix, apricot) = -0{,}25 + 0{,}5 - 0{,}5 = -0{,}25$, quindi $P(+\mid apricot, matrix) = \sigma(-0{,}25) = 0{,}44$ e $P(-\mid apricot, matrix) = 0{,}56$.

Tutti i numeri sono esatti (verificati: $\sigma(1) = 0{,}7311$, $\sigma(-0{,}25) = 0{,}4378$). Nota che jam e matrix sono vettori **di contesto** (matrice $C$), apricot è un vettore **target** (matrice $W$).

> **Da saper fare: Da fare a mano**
>
> Calcolare $\sigma(x)$ senza calcolatrice: $e^{-1}\approx0{,}368$, quindi $\sigma(1) = 1/1{,}368 = 0{,}731$; $e^{0{,}25}\approx1{,}284$, quindi $\sigma(-0{,}25) = 1/2{,}284 = 0{,}438$. Per l'esame conviene ricordare $\sigma(0) = 0{,}5$, $\sigma(1) = 0{,}73$, $\sigma(2) = 0{,}88$, $\sigma(3) = 0{,}95$ e la simmetria $\sigma(-x) = 1-\sigma(x)$.

<a id="p-19"></a>

### Slide 19 · Il classificatore: lettura sulla sigmoide

Stessi tre vettori; il grafico a sinistra mostra la sigmoide ($P(+\mid apricot, c)$ in funzione del prodotto scalare con apricot, da −4 a 4) con i due punti: *matrix* in rosso a $\sigma(-0{,}25) = 0{,}44$, *jam* in verde a $\sigma(1{,}00) = 0{,}73$, con le linee tratteggiate fino agli assi.

- jam: prodotto 1,00, probabilità 0,73;
- matrix: prodotto −0,25, probabilità 0,44;
- la sigmoide è **monotona**: più alto il prodotto scalare, più alta la probabilità.

Già con vettori non addestrati il classificatore "indovina" che *jam* è un contesto più probabile di *matrix* per *apricot*, ma solo perché i numeri sono stati scelti così. Il training (seconda parte) serve a rendere questi prodotti scalari alti per le coppie vere e bassi per le altre.

Con la finestra (jam, matrix) e l'ipotesi di indipendenza: $P(+\mid apricot, jam, matrix) = 0{,}731\times0{,}438 = 0{,}320$ (cella 2 del notebook).

## Imparare gli embedding

<a id="p-20"></a>
**Slide 20 · Imparare gli embedding** — Terzo blocco, i quattro passi restanti della tabella di marcia: esempi positivi e negativi, loss, discesa del gradiente, embedding.

<a id="p-21"></a>

### Slide 21 · Esempi positivi e negativi

Dalla finestra ±2 di *apricot* vengono **4 coppie positive** $(w, c_{pos})$: (apricot, tablespoon), (apricot, of), (apricot, jam), (apricot, a).

Per ognuna si generano **k esempi negativi** $(w, c_{neg})$: il target più una **parola di rumore** (*noise word*), una parola casuale del lessico diversa da $w$. Nella tabella della slide $k = 2$, quindi 8 coppie negative: aardvark, my, where, coaxial, seven, forever, dear, if.

- Ci sono **più negativi che positivi**, nel rapporto fissato da $k$. Nel lavoro originale $k$ va da 5 a 20 per corpora piccoli e da 2 a 5 per corpora grandi (Mikolov et al., 2013b; non è nel libro).
- Le parole di rumore sono scelte **senza guardare il contesto**: *my*, *where* o *if* potrebbero comparire vicino ad apricot in qualche altra frase. È accettato: su un vocabolario grande la probabilità di pescare proprio un contesto tipico è piccola, e su milioni di esempi l'effetto si diluisce (esercizio 2c).

Questo è il **negative sampling**: invece di confrontare il contesto vero con tutte le $|V|$ parole (come farebbe una softmax), lo si confronta con $k$ parole estratte a caso.

> **Da saper fare: Contare le coppie (esercizio 2)**
>
> *the quick brown fox jumps over the lazy dog*, finestra ±2, $k = 3$. Per *fox*: (fox, quick), (fox, brown), (fox, jumps), (fox, over), 4 positive e $4\times3 = 12$ negative. Su tutta la frase (9 parole): le due estremità hanno 2 e 3 contesti, le 5 parole centrali 4 ciascuna: $2+3+4\cdot5+3+2 = 30$ coppie positive, $30\times3 = 90$ negative. Verificato nella cella 25 del notebook.

<a id="p-22"></a>

### Slide 22 · Scegliere le parole di rumore

Le parole di rumore si estraggono secondo la loro **frequenza** (probabilità unigramma), ma **pesata**. La frase della slide va letta così: se si estraesse con la $P(w)$ non pesata, *the* verrebbe scelta tanto spesso quanto compare nel testo e *aardvark* tanto raramente quanto compare. In pratica si usa invece

$$P_\alpha(w) = \frac{\text{count}(w)^\alpha}{\sum_{w'}\text{count}(w')^\alpha}\qquad\alpha = 0{,}75$$

- Elevare i conteggi a una potenza minore di 1 **schiaccia le differenze**: le parole frequenti perdono un po' di probabilità, quelle rare ne guadagnano ($P_\alpha(w) &gt; P(w)$ per le parole rare).
- Con $\alpha = 1$ si torna alla $P(w)$; con $\alpha = 0$ la distribuzione diventa uniforme. 0,75 è un compromesso trovato sperimentalmente: gli embedding vengono migliori.

Perché non uniforme? Con l'uniforme quasi tutte le parole di rumore sarebbero parole rarissime, facili da distinguere e poco informative; con $P(w)$ pura sarebbero quasi sempre *the, of, a*. $P_\alpha$ sta in mezzo.

<a id="p-23"></a>

### Slide 23 · Scegliere le parole di rumore: due eventi

$$P_\alpha(a) = \frac{0{,}99^{0{,}75}}{0{,}99^{0{,}75}+0{,}01^{0{,}75}} = 0{,}97\qquad P_\alpha(b) = \frac{0{,}01^{0{,}75}}{0{,}99^{0{,}75}+0{,}01^{0{,}75}} = 0{,}03$$

Eq. 5.20 del libro. Con $P(a) = 0{,}99$ e $P(b) = 0{,}01$: $0{,}99^{0{,}75} = 0{,}9925$, $0{,}01^{0{,}75} = 0{,}0316$, somma 1,0241; quindi 0,969 e 0,031. Il grafico a barre a sinistra mostra le due coppie di barre (grigio $P$, blu $P_\alpha$): l'evento frequente $a$ scende da 0,99 a 0,97, quello raro $b$ sale da 0,01 a 0,03, cioè **triplica**.

È **la stessa pesatura** usata per la PPMI nella [scheda 57 della L10](L10-semantica-vettoriale.md#p-57), con lo stesso esempio numerico ([scheda 58](L10-semantica-vettoriale.md#p-58)). Non è un caso: Levy et al. (2015) hanno preso $\alpha = 0{,}75$ proprio da word2vec e l'hanno trasferito alla PPMI.

Le parole rare diventano parole di rumore un po' più spesso di quanto direbbe la loro frequenza.

> **Da saper fare: P e P_α su cinque parole (esercizio 4)**
>
> Conteggi the 500, of 300, coffee 150, cup 40, aardvark 10 (totale 1000). $P$ = 0,500; 0,300; 0,150; 0,040; 0,010. Conteggi$^{0{,}75}$: 105,74; 72,08; 42,86; 15,91; 5,62, somma 242,21. $P_\alpha$ = **0,437; 0,298; 0,177; 0,066; 0,023**. Perdono *the* (−13%) e di pochissimo *of*; guadagnano coffee (×1,18), cup (×1,64), aardvark (×2,32). Su 1000 parole di rumore: *the* 500 con $P$ e circa 437 con $P_\alpha$; *aardvark* 10 e circa 23. Verificato nelle celle 4 e 25 del notebook.

<a id="p-24"></a>

### Slide 24 · La loss

Obiettivo: rendere **simili** le coppie positive e **dissimili** le negative. Per una coppia $(w, c_{pos})$ con le sue $k$ parole di rumore:

$$\begin{aligned}L(w,c_{pos},c_{neg*}) &= -\log\Big[P(+\mid w,c_{pos})\prod_{i=1}^{k}P(-\mid w,c_{neg_i})\Big]\\ &= -\Big[\log P(+\mid w,c_{pos}) + \sum_{i=1}^{k}\log P(-\mid w,c_{neg_i})\Big]\\ &= -\Big[\log P(+\mid w,c_{pos}) + \sum_{i=1}^{k}\log\big(1-P(+\mid w,c_{neg_i})\big)\Big]\\ &= -\Big[\log\sigma(\mathbf c_{pos}\cdot\mathbf w) + \sum_{i=1}^{k}\log\sigma(-\mathbf c_{neg_i}\cdot\mathbf w)\Big]\end{aligned}$$

- **Primo termine**: il vero contesto $c_{pos}$ deve avere probabilità alta di essere un vicino.
- **Secondo termine**: ciascuna delle $k$ parole di rumore deve avere probabilità alta di **non** essere un vicino.

Passaggi: il logaritmo trasforma il prodotto in somma (le $k+1$ coppie sono trattate come indipendenti); $P(-) = 1-P(+)$; infine $1-\sigma(x) = \sigma(-x)$ (scheda 16). Il meno davanti rende la quantità da **minimizzare**: è una negative log likelihood.

> **Da saper fare: Calcolare la loss (esercizio 5)**
>
> coffee = [1, 2, 0], cup = [1, 1, 1], tax = [−1, 0, 1], seven = [0, −1, 1]. Prodotti: cup·coffee = 3, tax·coffee = −1, seven·coffee = −2. $L = -[\log\sigma(3) + \log\sigma(1) + \log\sigma(2)] = 0{,}049 + 0{,}313 + 0{,}127 = 0{,}489$. Con tutti i prodotti a 0: $3\ln2 = 2{,}079$; classificatore perfetto (positivo $\to+\infty$, negativi $\to-\infty$): $L\to0$.

<a id="p-25"></a>

### Slide 25 · La loss: due curve

Stessa derivazione; il grafico a destra mostra i due tipi di termine in funzione del prodotto scalare con $\mathbf w$ (da −4 a 4):

- curva verde, **parola di contesto**: $-\log\sigma(\mathbf c_{pos}\cdot\mathbf w)$, scende da circa 4 (a −4) verso 0: la loss è bassa se il prodotto con il contesto vero è **alto**;
- curva rossa, **parola di rumore**: $-\log\sigma(-\mathbf c_{neg}\cdot\mathbf w)$, sale da 0 verso 4: la loss è bassa se il prodotto con il rumore è **basso**.

Le curve si incrociano a prodotto 0 con valore $\ln2 = 0{,}69$; a ±4 valgono $\ln(1+e^{4}) = 4{,}02$. Sono specchiate l'una dell'altra.

È la **cross-entropy loss** della regressione logistica ([L6, scheda 38](L06-regressione-logistica.md#p-38)), $-[y\log\hat y + (1-y)\log(1-\hat y)]$, sommata su un esempio positivo ($y = 1$, resta $-\log\hat y$) e $k$ negativi ($y = 0$, resta $-\log(1-\hat y)$). Le due curve della L6 erano in funzione di $\hat y$; queste in funzione del prodotto scalare, cioè del logit.

<a id="p-26"></a>

### Slide 26 · Un passo di discesa del gradiente

La loss si minimizza con la **stochastic gradient descent**. La figura (Fig. 5.7 del libro) mostra la colonna dei parametri $\theta$: in alto $W$ con la riga di *apricot* ($w$) evidenziata, in basso $C$ con le righe di *jam* ($c_{pos}$), *matrix* e *Tolstoy* ($c_{neg1}$, $c_{neg2}$, $k = 2$). Tre frecce partono da apricot:

- verde tratteggiata verso jam: *avvicina apricot e jam*, il prodotto $\mathbf c_{pos}\cdot\mathbf w$ **aumenta**;
- rosse punteggiate verso matrix e Tolstoy: *allontana*, i prodotti $\mathbf c_{neg}\cdot\mathbf w$ **diminuiscono**.

La frase di partenza è *...apricot jam...*. Un passo modifica **quattro vettori**: il target $\mathbf w$ in $W$ e i tre vettori di contesto in $C$. Tutte le altre righe restano ferme: ogni passo tocca solo $k+2$ righe su $2|V|$, ed è per questo che l'algoritmo è veloce.

<a id="p-27"></a>

### Slide 27 · I gradienti rispetto ai contesti

$$\frac{\partial L}{\partial \mathbf c_{pos}} = [\sigma(\mathbf c_{pos}\cdot\mathbf w)-1]\,\mathbf w\qquad \frac{\partial L}{\partial \mathbf c_{neg_i}} = [\sigma(\mathbf c_{neg_i}\cdot\mathbf w)]\,\mathbf w$$
$$\frac{\partial L}{\partial \mathbf w} = [\sigma(\mathbf c_{pos}\cdot\mathbf w)-1]\,\mathbf c_{pos} + \sum_{i=1}^{k}[\sigma(\mathbf c_{neg_i}\cdot\mathbf w)]\,\mathbf c_{neg_i}$$

- **Parola di contesto**: $\sigma - 1$, cioè la probabilità prevista meno l'etichetta gold 1, per $\mathbf w$. È sempre negativa, quindi il passo $-\eta(\sigma-1)\mathbf w$ **aggiunge** a $\mathbf c_{pos}$ un pezzo di $\mathbf w$: lo avvicina. Tanto più quanto il classificatore sbaglia ($\sigma$ lontana da 1).
- **Parola di rumore**: $\sigma - 0$, la probabilità prevista meno l'etichetta 0, per $\mathbf w$. Positiva: il passo **toglie** un pezzo di $\mathbf w$ a $\mathbf c_{neg}$, lo allontana.

Le tre formule sono le Eq. 5.22-5.24; la derivazione è l'esercizio 6 (libro 5.3).

<a id="p-28"></a>

### Slide 28 · Il gradiente rispetto al target

Stesse formule; la novità è la terza. Il gradiente rispetto al **target** $\mathbf w$ somma gli errori di tutte le **k + 1 coppie**, ciascuno moltiplicato per il suo vettore di contesto: $\mathbf w$ si sposta verso $\mathbf c_{pos}$ e lontano da ogni $\mathbf c_{neg_i}$.

È la forma della regressione logistica ([L6, scheda 45](L06-regressione-logistica.md#p-45)): **(previsto − vero) × input**, $(\hat y - y)x_j$. Qui l'"input" di $\mathbf c$ è $\mathbf w$ e l'"input" di $\mathbf w$ è $\mathbf c$: il prodotto scalare è simmetrico, e ciascuno dei due vettori fa da feature per l'altro.

> **Da saper fare: Derivare i gradienti in tre righe (esercizio 6)**
>
> Fatto chiave: $\frac{d}{dz}\log\sigma(z) = \frac{\sigma(z)(1-\sigma(z))}{\sigma(z)} = 1-\sigma(z)$. Rispetto a $\mathbf c_{pos}$ conta solo il primo termine: $-(1-\sigma(\mathbf c_{pos}\cdot\mathbf w))\mathbf w = [\sigma(\mathbf c_{pos}\cdot\mathbf w)-1]\mathbf w$. Rispetto a $\mathbf c_{neg_i}$ conta solo $-\log\sigma(-\mathbf c_{neg_i}\cdot\mathbf w)$: $-(1-\sigma(-\mathbf c_{neg_i}\cdot\mathbf w))(-\mathbf w) = \sigma(\mathbf c_{neg_i}\cdot\mathbf w)\mathbf w$, usando $1-\sigma(-z) = \sigma(z)$. Rispetto a $\mathbf w$ contano tutti i termini, e si ottiene la somma. Il notebook (cella 6) controlla le tre formule con le differenze finite.

<a id="p-29"></a>

### Slide 29 · Gli aggiornamenti della SGD

$$\mathbf c_{pos}^{t+1} = \mathbf c_{pos}^{t} - \eta[\sigma(\mathbf c_{pos}^{t}\cdot\mathbf w^{t})-1]\,\mathbf w^{t}\qquad \mathbf c_{neg_i}^{t+1} = \mathbf c_{neg_i}^{t} - \eta[\sigma(\mathbf c_{neg_i}^{t}\cdot\mathbf w^{t})]\,\mathbf w^{t}$$
$$\mathbf w^{t+1} = \mathbf w^{t} - \eta\Big[[\sigma(\mathbf c_{pos}^{t}\cdot\mathbf w^{t})-1]\,\mathbf c_{pos}^{t} + \sum_{i=1}^{k}[\sigma(\mathbf c_{neg_i}^{t}\cdot\mathbf w^{t})]\,\mathbf c_{neg_i}^{t}\Big]$$

- **Regola**: ogni vettore meno $\eta$ (learning rate, [L6](L06-regressione-logistica.md#p-47)) per il suo gradiente. Tutti i gradienti si calcolano con i valori al tempo $t$: prima si calcolano tutti, poi si aggiorna (se si aggiornasse $\mathbf w$ prima e poi si usasse il nuovo $\mathbf w$ per i contesti, il risultato sarebbe diverso).
- **Ciclo di training**: $W$ e $C$ inizializzate a caso; si percorre il corpus, una coppia positiva e le sue $k$ parole di rumore alla volta, come la regressione logistica della [L6](L06-regressione-logistica.md#p-46). Molte passate (epoche) sul corpus.

<a id="p-30"></a>

### Slide 30 · Un passo di training: un esempio

I vettori giocattolo di prima, una seconda parola di rumore *Tolstoy* = [0,0; −1,0; 0,5], $k = 2$, $\eta = 0{,}5$.

|  | prima | dopo un passo |
| --- | --- | --- |
| dot(jam, apricot) | 1,00 | 1,52 |
| dot(matrix, apricot) | −0,25 | −1,01 |
| dot(Tolstoy, apricot) | −1,25 | −1,66 |
| loss L | 1,14 | 0,68 |

apricot = [0,5; 1,0; −0,5] − 0,5 × [−0,488; −0,138; 0,549] = [0,744; 1,069; −0,775]  
jam = [1,0; 0,5; 0,0] − 0,5 × [−0,134; −0,269; 0,134] = [1,067; 0,634; −0,067]

Ho ricalcolato tutto con numpy (e coincide con la cella 6 del notebook): i numeri della slide sono esatti. Loss iniziale: $-\ln\sigma(1) - \ln\sigma(0{,}25) - \ln\sigma(1{,}25) = 0{,}313 + 0{,}576 + 0{,}252 = 1{,}141$; dopo il passo 0,681. La slide non mostra i nuovi vettori di rumore: matrix diventa [−0,609; 0,281; 1,109], Tolstoy [−0,056; −1,111; 0,556].

> **Da saper fare: Rifare il passo a mano**
>
> (1) Sigmoidi: $\sigma(1) = 0{,}731$, $\sigma(-0{,}25) = 0{,}438$, $\sigma(-1{,}25) = 0{,}223$. (2) Gradiente di apricot: $(0{,}731-1)\cdot$jam $+ 0{,}438\cdot$matrix $+ 0{,}223\cdot$Tolstoy $= [-0{,}269; -0{,}134; 0] + [-0{,}219; 0{,}219; 0{,}438] + [0; -0{,}223; 0{,}111] = [-0{,}488; -0{,}138; 0{,}549]$. (3) Gradiente di jam: $(0{,}731-1)\cdot$apricot $= [-0{,}134; -0{,}269; 0{,}134]$. (4) Gradienti dei rumori: $0{,}438\cdot$apricot e $0{,}223\cdot$apricot. (5) Ogni vettore meno $0{,}5\times$ il suo gradiente, tutti con i valori vecchi. (6) Nuovi prodotti con il nuovo apricot e i nuovi contesti.

<a id="p-31"></a>

### Slide 31 · Un passo di training: che cosa è successo

Il grafico a barre mostra per jam, matrix e Tolstoy il prodotto scalare con apricot prima (grigio) e dopo il passo (verde per il contesto vero, rosso per i rumori):

- **jam**: da 1,00 a 1,52, più vicino ad apricot;
- **matrix** e **Tolstoy**: da −0,25 a −1,01 e da −1,25 a −1,66, più lontani;
- la **loss** scende da 1,14 a 0,68.

Un passo solo: apricot si avvicina a jam e si allontana dalle due parole di rumore. Notare che il lavoro lo fanno **entrambe** le matrici: se si aggiornasse solo apricot, i prodotti diventerebbero 1,28, −0,61 e −1,46 (calcolato); il resto dello spostamento viene dall'aggiornamento di jam, matrix e Tolstoy.

Moltiplicato per centinaia di milioni di coppie, questo meccanismo fa sì che parole con contesti simili finiscano con vettori simili: *apricot* e *peach* vengono spinti entrambi verso *jam*, *ripe*, *tree*, e quindi l'uno verso l'altro. È l'ipotesi distribuzionale realizzata con la discesa del gradiente.

<a id="p-32"></a>

### Slide 32 · Dopo il training: quale vettore, quale finestra

- **Due insiemi di embedding**: skip-gram impara per ogni parola $i$ un target embedding $\mathbf w_i$ e un context embedding $\mathbf c_i$. È comune **sommarli**, $\mathbf w_i + \mathbf c_i$, oppure buttare via $C$ e tenere solo $\mathbf w_i$. Il notebook usa la somma.
- **Dimensione della finestra**: influenza le prestazioni degli embedding, come per i metodi basati sui conteggi ([L10](L10-semantica-vettoriale.md#p-18)). Negli esperimenti si sceglie spesso su un **devset** ([L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-32)), come un iperparametro qualunque. Che cosa cambia con la finestra è alle schede 45-46.

Gli altri iperparametri da conoscere: la dimensione $d$, il numero di parole di rumore $k$, il learning rate $\eta$, il numero di epoche, la soglia di frequenza minima per entrare nel vocabolario (5 nel notebook).

> **Da saper fare: Esercizio 8a**
>
> Quale vettore rappresenta una parola dopo il training? $\mathbf w_i$ (si butta $C$) oppure $\mathbf w_i + \mathbf c_i$. Entrambe le scelte sono comuni; i $\mathbf c_i$ da soli si usano raramente.

<a id="p-33"></a>

### Slide 33 · Dopo il training: la ricetta

**Ricetta del training**:

1. partire da $2|V|$ vettori casuali di dimensione $d$, le righe di $W$ e $C$;
2. prendere le coppie che co-occorrono come esempi **positivi**, le coppie con parole di rumore come esempi **negativi**;
3. addestrare il classificatore a distinguerle, aggiustando lentamente tutti gli embedding.

**Si butta via il classificatore e si tengono gli embedding.** In realtà il "classificatore" non ha altri parametri oltre agli embedding: buttarlo via vuol dire smettere di usare la sigmoide e il compito binario, e usare i vettori per altro (vicini, coseni, input di altri modelli).

Il prossimo laboratorio (scheda 58) e il notebook di oggi (sezione 5) implementano questa ricetta da zero in numpy.

<a id="p-34"></a>
**Slide 34 · Pausa** — Pausa di 10 minuti; dopo la pausa: altri embedding, che cosa catturano, bias e valutazione.

## Altri embedding statici

<a id="p-35"></a>
**Slide 35 · Altri embedding statici** — Quarto blocco: l'altro algoritmo di word2vec (CBOW), i subword di fasttext, i conteggi globali di GloVe.

<a id="p-36"></a>

### Slide 36 · Skip-gram e CBOW: skip-gram

Word2vec contiene **due algoritmi**: skip-gram e CBOW. La figura li mette uno accanto all'altro sulla finestra di *apricot*:

- a sinistra, **skip-gram: target → contesto**. Da *apricot* partono quattro frecce verso *tablespoon, of, jam, a*: **una previsione per ogni parola di contesto**, cioè quattro coppie positive separate;
- a destra, **CBOW: contesto → target**. Le quattro parole convergono su *apricot*; la didascalia dice che i vettori di contesto vengono mediati.

**Skip-gram** predice le parole del contesto a partire dalla parola target: è tutto quello che si è visto finora. Ogni occorrenza di una parola produce $2L$ esempi di training (uno per contesto), ed è per questo che skip-gram vede molte volte anche le parole rare.

<a id="p-37"></a>

### Slide 37 · Skip-gram e CBOW: CBOW

Stessa figura; la novità è la descrizione di CBOW.

- **CBOW**, *continuous bag of words*: predice la parola **target** a partire dalle parole del **contesto**, i cui vettori vengono **mediati**. Facendo la media **l'ordine non conta**: è un bag of words ([L10](L10-semantica-vettoriale.md#p-33)) del contesto, "continuous" perché fatto di vettori densi invece che di conteggi.
- **Origine**: entrambi semplificano lo strato nascosto dei language model neurali (Mikolov et al., 2013a). Il libro li cita solo nelle Historical Notes (p. 150).

Differenza pratica: per ogni finestra CBOW fa **una** previsione (il target dalla media), skip-gram ne fa $2L$. CBOW è quindi più veloce; skip-gram tratta meglio le parole rare, perché ogni loro occorrenza genera più aggiornamenti.

> **Approfondimento: CBOW con negative sampling, in formule**
>
> Non è nel libro. Con la notazione di oggi: $\mathbf h = \frac{1}{2L}\sum_{j}\mathbf w_{c_j}$ (media dei vettori delle parole di contesto), e il classificatore valuta $\sigma(\mathbf c_{t}\cdot\mathbf h)$ per il vero target $t$ e $\sigma(-\mathbf c_{n}\cdot\mathbf h)$ per $k$ parole di rumore $n$. La loss ha la stessa forma della scheda 24 con $\mathbf h$ al posto di $\mathbf w$; il gradiente rispetto a $\mathbf h$ si divide in parti uguali fra i vettori del contesto.

<a id="p-38"></a>

### Slide 38 · Fasttext: i subword

**Fasttext**: una parola è **sé stessa più un insieme (bag) di n-grammi di caratteri**, con i simboli di confine < e >. La figura, con $n = 3$:

*where* = `<where>` + `<wh` + `whe` + `her` + `ere` + `re>`

e la didascalia: l'embedding di *where* è la somma degli embedding della parola intera e dei suoi n-grammi. Due problemi di word2vec che fasttext affronta:

- **parole sconosciute**: parole del test mai viste nel training (le OOV della [L2](L02-parole-e-token.md#p-13)). Word2vec non ha nessun vettore per loro;
- **sparsità**: nelle lingue a **morfologia ricca** ([L2, scheda 17](L02-parole-e-token.md#p-17)) molte forme di un nome o di un verbo sono rare. In italiano un verbo ha decine di forme (*parlo, parlavamo, parlerebbero*...): ognuna avrebbe un vettore suo, imparato da poche occorrenze.

I confini servono a distinguere: il trigramma `her` dentro *where* è diverso dalla parola `<her>`.

<a id="p-39"></a>

### Slide 39 · Fasttext: embedding dei subword

- **Embedding dei subword** (Bojanowski et al., 2017): si impara con skip-gram un embedding per **ogni n-gramma**; una parola è la **somma** degli embedding di sé stessa e dei suoi n-grammi. Una parola sconosciuta è la somma degli embedding dei soli n-grammi.
- **Lunghezze**: tipicamente tutti gli n-grammi da 3 a 6 caratteri, non solo i trigrammi della figura. Libreria open source con embedding preaddestrati per **157 lingue**: [fasttext.cc](https://fasttext.cc).

L'effetto: parole che condividono pezzi di forma condividono pezzi di vettore. *catlike*, mai vista, riceve un vettore vicino a quello di *cats* e *cat* attraverso `<ca` e `cat`. È la stessa idea della tokenizzazione subword della [L2](L02-parole-e-token.md#p-29) (BPE), ma con n-grammi fissi sovrapposti invece di un vocabolario appreso.

> **Da saper fare: N-grammi a mano (esercizio 9)**
>
> Trigrammi di *cats* (da <cats>): `<ca` `cat` `ats` `ts>`. Di *catlike*: <ca, cat, atl, tli, lik, ike, ke>; in comune con cats: **<ca** e **cat**. 4-grammi di *cats*: <cat, cats, ats>. Una parola di $m$ lettere diventa una stringa di $m+2$ simboli e ha $m+2-n+1$ n-grammi di lunghezza $n$. Verificato nella cella 26 del notebook.

<a id="p-40"></a>

### Slide 40 · GloVe e gli embedding da conteggi

- **GloVe**, *Global Vectors* (Pennington et al., 2014): un altro embedding statico molto usato. Si basa sui **rapporti di probabilità** estratti dalla matrice di co-occorrenza parola-parola: statistiche **globali** del corpus, invece delle singole finestre viste una alla volta.
- **Word2vec e PPMI**: word2vec può essere visto come l'ottimizzazione implicita di una funzione di una matrice di conteggi con pesatura **PPMI** (Levy e Goldberg, 2014), la pesatura della lezione scorsa ([L10](L10-semantica-vettoriale.md#p-50)).

Predire e contare sono più vicini di quanto sembri: la differenza fra la riga "contare" e la riga "predire" della scheda 8 è soprattutto di metodo (fattorizzazione esplicita contro SGD su coppie), non di informazione.

> **Approfondimento: Le due formule dietro la slide**
>
> Facoltativo, da conoscenza solida (non è nel libro). **Levy e Goldberg (2014)**: all'ottimo, SGNS con $k$ parole di rumore soddisfa $\mathbf w\cdot\mathbf c = \text{PMI}(w,c) - \log k$, cioè fattorizza una matrice PMI "spostata" di $\log k$; con le parole di rumore estratte da $P_\alpha$, la PMI è quella con $P_\alpha(c)$ al denominatore, cioè la PPMI-α della [scheda 57 della L10](L10-semantica-vettoriale.md#p-57). **GloVe** minimizza $\sum_{i,j} f(X_{ij})\,(\mathbf w_i\cdot\tilde{\mathbf c}_j + b_i + \tilde b_j - \log X_{ij})^2$, dove $X_{ij}$ è il conteggio di co-occorrenza e $f$ pesa meno le coppie rare: il prodotto scalare deve approssimare il logaritmo del conteggio.

<a id="p-41"></a>

### Slide 41 · Quale embedding, per che cosa

|  | impara da | usarlo per |
| --- | --- | --- |
| **skip-gram** | predire le parole del contesto dalla parola target | la scelta di default; parole rare, corpora più piccoli |
| **CBOW** | predire la parola target dalla media del suo contesto | training più veloce; un po' meglio sulle parole frequenti |
| **fasttext** | predire il contesto, come skip-gram, dalla parola e dai suoi n-grammi di caratteri | parole sconosciute, lingue a morfologia ricca |
| **GloVe** | i conteggi globali di co-occorrenza del corpus | vettori preaddestrati, vicini ai conteggi della L10 |

Tutti e quattro sono **statici**: un vettore per parola, qualunque sia il senso. *mouse* (il roditore e il dispositivo, [L10, scheda 6](L10-semantica-vettoriale.md#p-6)) ha un vettore solo, una media dei due sensi pesata dalla loro frequenza nel corpus. Risolverlo richiede gli embedding contestuali (capitolo 9).

> **Approfondimento: Da dove vengono i consigli d'uso**
>
> Le righe "usarlo per" di skip-gram e CBOW non sono nel libro: riassumono le indicazioni pratiche degli autori di word2vec (Mikolov et al., 2013, e la documentazione del pacchetto). Sono regole empiriche, non teoremi: su un compito concreto la scelta si fa provando, sul devset.

## Proprietà degli embedding

<a id="p-42"></a>
**Slide 42 · Proprietà degli embedding** — Quinto blocco: che cosa catturano i vettori.

<a id="p-43"></a>

### Slide 43 · Visualizzare gli embedding: vicini e clustering

Come si guarda un vettore a 100 o 300 dimensioni? Il libro cita l'economista Martin Shubik: *vedo bene in molte dimensioni, purché siano circa due*.

- **Vicini più prossimi**: ordinare il vocabolario per coseno con $\mathbf w$. I 7 vicini di *frog* con GloVe: *frogs, toad, litoria, leptodactylidae, rana, lizard, eleutherodactylus*. Quattro sono nomi scientifici di generi o famiglie di rane: parole rare che il modello ha comunque collocato bene, perché compaiono negli stessi contesti di *frog*.
- **Clustering gerarchico**: un algoritmo di clustering mostra quali parole sono simili ad altre nello spazio (Rohde et al., 2006). Il libro (p. 142) ha il dendrogramma: parti del corpo (wrist, ankle, hand, foot...), animali (dog, cat, puppy, kitten...) e città (Chicago, Atlanta) in rami separati.

È lo stesso metodo dei vicini nel notebook della L10, ora con vettori densi (sezione 6 del notebook di oggi).

<a id="p-44"></a>

### Slide 44 · Visualizzare gli embedding: proiezione

- **Proiezione**: il metodo più comune è proiettare in 2 dimensioni con **t-SNE** (van der Maaten e Hinton, 2008). La figura a sinistra è quella già vista nella [scheda 14 della L10](L10-semantica-vettoriale.md#p-14): *sweet* in rosso, vicino a *honey, candy, chocolate, cream, juice*; più in là *cider, wine, drink*; in basso i cibi salati *beef, potatoes, fried, soup, rice, corn*; i punti grigi sono parole senza etichetta.
- **Embedding projector**: lo strumento della figura, *projector.tensorflow.org*, permette di esplorare embedding preaddestrati in 2D o 3D.

> **Approfondimento: Come leggere un grafico t-SNE**
>
> t-SNE conserva soprattutto i **vicinati locali**: se due parole sono vicine nella figura, lo sono probabilmente anche nello spazio originale. Le **distanze fra gruppi lontani** e le dimensioni dei gruppi invece non hanno un significato affidabile, e il risultato cambia con i parametri e il seme casuale. Conclusioni quantitative si traggono dai coseni, non dalla figura.

<a id="p-45"></a>

### Slide 45 · La dimensione della finestra

- **Dimensione**: di solito da 1 a 10 parole per lato, cioè un contesto totale da 2 a 20 parole.
- **Finestre corte**: rappresentazioni più **sintattiche**, perché l'informazione viene dalle parole immediatamente vicine. Le parole più simili sono parole **simili** con la **stessa parte del discorso**.
- **Finestre lunghe**: le parole più simili sono **collegate per argomento** (topically related), non simili.

È la distinzione fra **similarità** e **relatedness** della [L10, scheda 6](L10-semantica-vettoriale.md#p-6), che dipende da una scelta tecnica. Con ±1 il contesto di *guitar* è *the, electric, acoustic, plays*, come per *violin* o *piano*; con ±10 entrano *band, stage, song, chords*, gli stessi di *drummer* o *concert*.

> **Approfondimento: Associazioni del primo e del secondo ordine**
>
> Il libro (p. 143) aggiunge una distinzione (Schütze e Pedersen, 1993). **Co-occorrenza del primo ordine** (associazione *sintagmatica*): due parole compaiono tipicamente vicine, come *wrote* e *book*. **Del secondo ordine** (associazione *paradigmatica*): due parole hanno vicini simili, come *wrote* e *said* o *remarked*. Il coseno fra embedding misura il secondo ordine; il prodotto $\mathbf c\cdot\mathbf w$ del classificatore, fra un target e un contesto, è vicino al primo.

<a id="p-46"></a>

### Slide 46 · La finestra: l'esempio di Hogwarts

Vicini di **Hogwarts** (la scuola di Harry Potter) con skip-gram (Levy e Goldberg, 2014):

| finestra ±2 | finestra ±5 |
| --- | --- |
| *Sunnydale, Evernight* | *Dumbledore, Malfoy, half-blood* |
| altre scuole immaginarie (Sunnydale da *Buffy*, Evernight da una serie di vampiri): parole **simili** | parole della serie di Harry Potter: parole **collegate** |

Con ±2 contano i contesti immediati (*at \_\_\_ school*, *students of \_\_\_*), che Hogwarts condivide con le altre scuole; con ±5 entra il vocabolario della saga. La scelta della finestra dipende dallo **scopo** della rappresentazione: per un sistema che cerca sinonimi meglio finestre corte, per raggruppare documenti per argomento meglio finestre lunghe.

> **Da saper fare: Esercizio 8b**
>
> Vicini di *guitar*: (violin, piano, cello, banjo) vengono dalla finestra **±2**: altri strumenti, stessa parte del discorso, parole simili. (chords, strummed, band, solo) vengono da **±10**: parole dello stesso argomento, di parti del discorso diverse (un verbo, *strummed*), collegate ma non simili.

<a id="p-47"></a>

### Slide 47 · Analogia: il modello del parallelogramma

Gli embedding catturano anche significati **relazionali**. Il problema: *apple sta a tree come grape sta a ?* (Rumelhart e Abrahamson, 1973, un modello vettoriale della cognizione degli anni '70).

La figura: un parallelogramma verde con i vertici *apple*, *tree* (in alto) e *grape*, *vine* (in basso). La freccia da apple a tree è parallela e uguale a quella da grape a vine. Si somma il vettore che va da *apple* a *tree* al vettore di *grape*; la parola più vicina a quel punto è la risposta, *vine* (la vite).

L'idea: se la relazione "frutto → pianta che lo produce" è codificata da una direzione costante nello spazio, basta applicare lo stesso spostamento. Già i vettori sparsi riuscivano a risolvere alcune analogie (Turney e Littman, 2005), ma il metodo è diventato famoso con word2vec e GloVe.

<a id="p-48"></a>

### Slide 48 · Il metodo del parallelogramma

$$\hat{\mathbf b}^* = \underset{\mathbf x}{\operatorname{argmin}}\ \text{distance}(\mathbf x,\ \mathbf b - \mathbf a + \mathbf a^*)$$

Per un problema $a : b :: a^* : b^*$, dati $\mathbf a$, $\mathbf b$, $\mathbf a^*$ si cerca $b^*$: la parola più vicina a $\mathbf b - \mathbf a + \mathbf a^*$, con una funzione di distanza come quella **euclidea** (Eq. 5.28). Nella figura i lati sono etichettati: $\mathbf b - \mathbf a$ da apple ($a$) a tree ($b$), $\mathbf b - \mathbf a + \mathbf a^*$ da grape ($a^*$) a vine ($\hat b^*$).

In pratica si usa spesso il **coseno** al posto della distanza (così fa il notebook, sezione 8), e le parole di input vanno escluse dalla ricerca (scheda 50). Il punto $\mathbf b - \mathbf a + \mathbf a^*$ di solito non coincide con nessuna parola: si prende la più vicina.

> **Da saper fare: Parallelogramma a mano (esercizio 10a)**
>
> man = [1, 1], woman = [1, 3], king = [4, 1]. Punto: woman − man + king = [1−1+4; 3−1+1] = [4, 3]. Distanze euclidee: queen [4; 3,2] → 0,2; princess [3; 3,5] → $\sqrt{1+0{,}25} = 1{,}118$; king → 2; woman → 3; man → $\sqrt{9+4} = 3{,}606$. Risposta: **queen**.

<a id="p-49"></a>

### Slide 49 · king − man + woman

Due proiezioni in 2D di vettori GloVe (Fig. 5.9 del libro, da Pennington et al., 2014):

- **(a)** coppie maschile-femminile unite da segmenti tratteggiati quasi paralleli: man-woman, sir-madam, heir-heiress, king-queen, emperor-empress, duke-duchess, earl-countess, brother-sister, nephew-niece, uncle-aunt. $\mathbf{king} - \mathbf{man} + \mathbf{woman}$ è vicino a $\mathbf{queen}$.
- **(b)** le spezzate aggettivo → comparativo → superlativo: slow-slower-slowest, short-shorter-shortest, strong-stronger-strongest, loud-louder-loudest, clear-clearer-clearest, soft-softer-softest, dark-darker-darkest, con offset simili: la morfologia comparativa e superlativa è una direzione.

Anche $\mathbf{Paris} - \mathbf{France} + \mathbf{Italy}$ è vicino a $\mathbf{Rome}$. Il modello sembra estrarre relazioni come **maschile-femminile**, **capitale-di**, **comparativo-superlativo**. Attenzione: la figura è una proiezione scelta per mostrare il parallelismo, che in 300 dimensioni è solo approssimato.

<a id="p-50"></a>

### Slide 50 · Analogie: le cautele

- **Escludere le parole di input**: il vettore più vicino al punto $\mathbf b - \mathbf a + \mathbf a^*$ è di solito una delle 3 parole di input o una loro variante morfologica. *cherry : red :: potato : x* restituisce *potato* o *potatoes* invece di *brown*, quindi vanno escluse esplicitamente.
- **Quali relazioni funzionano**: parole frequenti, distanze piccole e certe relazioni (paesi e capitali, forme flesse); per altre relazioni funziona meno (Linzen, 2016; Gladkova et al., 2016, e altri).
- **Analogia umana**: il metodo è troppo semplice per modellare il processo umano di formare analogie (Peterson et al., 2020).

Il motivo della prima cautela: $\mathbf b - \mathbf a$ è spesso piccolo rispetto ad $\mathbf a^*$, quindi $\mathbf b - \mathbf a + \mathbf a^*$ resta vicino ad $\mathbf a^*$. I successi famosi (king/queen) sono stati ottenuti escludendo gli input.

> **Attenzione (errore nelle slide): potato, non «potatoe»**
>
> La slide scrive che la ricerca restituisce *potatoe* o *potatoes*. Il libro (p. 145) dice *potato or potatoes*: l'esempio serve proprio a mostrare che la risposta è **una delle parole di input** (*potato*) o una sua **variante morfologica** (*potatoes*), come dice la riga sopra. *potatoe* è un refuso. Verificato sul testo del §5.7 e con i vettori dell'esercizio 10b, dove la parola più vicina, senza escludere gli input, è proprio *potato*.

<a id="p-51"></a>

### Slide 51 · Embedding e semantica storica

Gli embedding permettono di studiare come cambia il significato nel tempo: si addestra uno **spazio separato per ogni decennio** su corpora storici come Google n-grams e il Corpus of Historical American English (Hamilton et al., 2016).

La figura (Fig. 5.10 del libro, una visualizzazione t-SNE con vettori word2vec) ha tre pannelli; le frecce blu uniscono le posizioni della stessa parola in decenni diversi, le parole grigie sono i vicini calcolati nello spazio moderno:

- **A, gay**: 1900 vicino a *daft, flaunting, sweet, cheerful, tasteful*; 1950 vicino a *frolicsome, witty, bright*; 1990 vicino a *homosexual, bisexual, lesbian*;
- **B, broadcast**: 1850 vicino a *sow, seed, sows, scatter* (seminare a spaglio); 1900 vicino a *circulated, newspapers*; 1990 vicino a *radio, television, bbc*;
- **C, awful**: 1850 vicino a *solemn, majestic, awe, dread*; 1900 vicino a *horrible, appalling, terrible*; 1990 vicino a *weird, wonderful, awfully*: una **peggiorazione** (da "pieno di timore reverenziale" a "terribile").

Perché si possa confrontare un decennio con l'altro, gli spazi vanno allineati (le coordinate di due training diversi non sono comparabili direttamente; cfr. la sezione 9 del notebook sulla variabilità).

## Bias e valutazione

<a id="p-52"></a>
**Slide 52 · Bias e valutazione** — Sesto blocco: gli stereotipi che gli embedding ereditano dal testo, e come si mettono alla prova gli embedding.

<a id="p-53"></a>

### Slide 53 · Gli embedding riflettono gli stereotipi

Oltre al significato, gli embedding riproducono anche i **bias impliciti** e gli **stereotipi** latenti nel testo.

- **Stereotipi di genere**: word2vec addestrato su notizie dà *man : computer programmer :: woman : homemaker* (Bolukbasi et al., 2016): la professione più vicina a $\mathbf{computer\ programmer} - \mathbf{man} + \mathbf{woman}$ è *homemaker* (casalinga). E anche *father : doctor :: mother : nurse*. È lo stesso metodo del parallelogramma che dava *queen*.
- **Amplificazione del bias**: i termini con genere diventano **più marcati** nello spazio degli embedding di quanto fossero nel testo di partenza, e i bias sono più esagerati delle statistiche reali sull'occupazione (Garg et al., 2018).

Gli embedding non inventano niente: comprimono le co-occorrenze del corpus, e con esse le associazioni presenti nel modo in cui si scrive di uomini e donne. L'amplificazione dice che non si limitano a riflettere.

> **Approfondimento: Debiasing**
>
> Dal libro (p. 146): si è provato a togliere i bias con una trasformazione dello spazio che elimina gli stereotipi di genere ma conserva il genere "definitorio" (*king/queen*) (Bolukbasi et al., 2016; Zhao et al., 2017), o cambiando il training (Zhao et al., 2018). Queste tecniche **riducono** il bias ma **non lo eliminano** (Gonen e Goldberg, 2019): è un problema aperto. Gli embedding storici servono anche a **misurare** i bias del passato (Garg et al., 2018).

<a id="p-54"></a>

### Slide 54 · Associazioni implicite

- **Implicit Association Test** (IAT, Greenwald et al., 1998): misura le associazioni delle persone fra **concetti** (fiori o insetti) e **attributi** (piacevole o spiacevole) dalla **latenza** con cui etichettano le parole. Chi associa fiori a piacevole è più veloce quando lo stesso tasto serve per "fiori" e "parole piacevoli" che nella condizione incongruente.
- **Coseni di GloVe**: Caliskan et al. (2017) hanno replicato questi risultati con i **coseni** di GloVe al posto delle latenze umane: nomi afroamericani come *Leroy* e *Shaniqua* più vicini a parole spiacevoli, nomi euroamericani come *Brad*, *Greg*, *Courtney* a parole piacevoli.

Con gli IAT le persone negli Stati Uniti associano anche i nomi maschili alla matematica e quelli femminili alle arti, i nomi delle persone anziane a parole spiacevoli; Caliskan et al. hanno replicato **tutte** queste associazioni negli embedding. "Piacevole/spiacevole" è la dimensione di **valence** di Osgood ([L10](L10-semantica-vettoriale.md#p-7)).

> **Da saper fare: Un punteggio di bias (esercizio 11a)**
>
> he = [1, 0], she = [0, 1]. nurse [0,2; 0,9]: norma 0,922, cos(she) = 0,976, cos(he) = 0,217, differenza **+0,759**. engineer [0,9; 0,3]: cos(she) = 0,316, cos(he) = 0,949, differenza **−0,632**. teacher [0,6; 0,6]: 0,707 e 0,707, differenza **0**. Il segno dice da che parte pende la parola; è l'idea dei test di Caliskan (WEAT), su vettori giocattolo.

<a id="p-55"></a>

### Slide 55 · Danno allocativo e danno rappresentazionale

| danno allocativo | danno rappresentazionale |
| --- | --- |
| un sistema **assegna risorse**, lavoro o credito in modo ingiusto a gruppi diversi | un sistema **sminuisce** o addirittura **ignora** alcuni gruppi sociali |
| una ricerca di candidati che usa gli embedding potrebbe penalizzare i documenti con nomi femminili (per *programmer* o *doctor*) | un algoritmo che ricava il sentiment delle parole dagli embedding potrebbe aggravare il bias della slide precedente (nomi afroamericani "spiacevoli") |

La distinzione è di Crawford (2017) e Blodgett et al. (2020), ed è la stessa vista per i classificatori nella [scheda 49 della L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-49). Il danno allocativo si vede nelle decisioni (chi viene assunto); quello rappresentazionale nel modo in cui un gruppo è descritto, anche quando nessuna risorsa è in gioco.

> **Da saper fare: Esercizio 11b**
>
> Un sistema di selezione che ordina i documenti dei candidati usando questi embedding (es. coseno fra il curriculum e *engineer*) favorirebbe i documenti con parole vicine a *he*: un **danno allocativo**, perché distribuisce un'opportunità (il colloquio) in modo ingiusto. Se il sistema descrivesse o etichettasse le persone in base a questi stereotipi, il danno sarebbe anche rappresentazionale.

<a id="p-56"></a>

### Slide 56 · Valutare gli embedding: valutazione intrinseca

La valutazione più importante è **estrinseca**: usare i vettori in un compito di NLP (sentiment, NER, question answering) e vedere se le prestazioni migliorano rispetto a un altro modello.

- **Valutazione intrinseca**: la **correlazione** fra i punteggi di similarità del modello (i coseni) e i giudizi di similarità dati da persone. Si usa una correlazione di rango (Spearman): conta che l'ordine delle coppie sia lo stesso, non che il coseno 0,7 corrisponda a 7 su 10.
- **WordSim-353** (Finkelstein et al., 2002): giudizi da 0 a 10 per 353 coppie di nomi; (*plane, car*) ha media 5,77. Misura soprattutto la **relatedness**.

> **Da saper fare: Correlazione di Spearman (esercizio 12a)**
>
> $\rho = 1 - \frac{6\sum d_i^2}{n(n^2-1)}$, con $d_i$ la differenza fra i due ranghi della coppia $i$. Sui cinque giudizi della scheda: ranghi umani (cup/mug 1, plane/car 3, coffee/cup 4, doctor/nurse 2, cat/carpet 5), ranghi del modello (1, 3, 2, 4, 5); $d$ = 0, 0, 2, −2, 0; $\sum d^2 = 8$; $\rho = 1 - 48/120 = 0{,}60$.

<a id="p-57"></a>

### Slide 57 · Valutare gli embedding: SimLex-999 e TOEFL

- **SimLex-999** (Hill et al., 2015): misura la **similarità** (*cup, mug*) e non la relatedness (*cup, coffee*), la distinzione della [lezione scorsa](L10-semantica-vettoriale.md#p-6); contiene coppie di aggettivi, nomi e verbi, concreti e astratti.
- **TOEFL**: 80 domande a scelta multipla: *levied* è più vicino nel significato a *imposed, believed, requested, correlated*? (Landauer e Dumais, 1997). Risposta: *imposed*; il modello sceglie l'opzione con il coseno più alto.

**Tutti questi dataset presentano le parole senza contesto**: un embedding statico deve dare un solo punteggio a *bank*/*money*, qualunque senso si intenda.

> **Approfondimento: Altre valutazioni nel libro (§5.9)**
>
> Più realistici sono i dataset con **contesto**: SCWS (2.003 coppie di parole nella loro frase) e WiC (Word-in-Context: la stessa parola in due frasi, stesso senso o no). C'è poi il **compito di analogia** (morfologia *city:cities::child:children*, relazioni enciclopediche *Beijing:China::Dublin:Ireland*). Infine la **variabilità**: inizializzazione casuale e negative sampling fanno sì che due training sullo stesso corpus diano vicini diversi; quando si studiano le associazioni di un corpus conviene addestrare più embedding su campioni bootstrap dei documenti e mediare (sezione 9 del notebook).

## Riepilogo

<a id="p-58"></a>

### Slide 58 · Riepilogo e prossima lezione

**Riepilogo**:

- embedding densi: $d$ da 50 a 1000, **appresi** invece che contati;
- skip-gram: regressione logistica su coppie (target, contesto), la **sigmoide di un prodotto scalare**;
- negative sampling: $k$ parole di rumore per coppia positiva, estratte con $P_\alpha$, $\alpha = 0{,}75$;
- SGD sulla loss; si tengono $W$, o $W + C$, come embedding;
- CBOW, fasttext, GloVe; dimensione della finestra, analogie, semantica storica;
- bias negli embedding; valutazione intrinseca ed estrinseca.

**Prossima lezione**: **laboratorio su embedding e word2vec**, una sessione con notebook con Andrea Ceni, sul capitolo 5. Conviene arrivarci avendo eseguito il notebook di oggi e rifatto a mano il passo di SGD della scheda 30.

## Notebook

Commento al notebook del corso `HLT-L11-word2vec.ipynb` (il notebook è del docente e non è incluso).

Notebook di accompagnamento: il classificatore skip-gram sugli embedding giocattolo delle slide, $P_\alpha$ con un campionamento di prova, la loss con i gradienti controllati con le differenze finite e il passo di SGD della scheda 30, poi un **training completo di SGNS scritto da zero in numpy** sul corpus delle docstring della libreria standard (lo stesso delle L4 e L10), con vicini più prossimi, confronto fra finestre ±2 e ±8, analogie, variabilità fra due semi, e infine il ricalcolo degli esercizi 1-5, 7 e 9-12 della scheda. Servono solo la libreria standard e `numpy`; nessuna figura.

Ho rieseguito il notebook (Python 3.13): le celle sugli esempi delle slide e della scheda (2, 4, 6, 25, 26) danno esattamente gli output salvati; quelle sul corpus (8-22) danno numeri diversi, come il notebook stesso avverte, perché il corpus è la documentazione della versione di Python installata. I commenti qui sotto si riferiscono agli output salvati e segnalano le differenze rilevanti; le conclusioni qualitative non cambiano, tranne un dettaglio della cella 23 (la variabilità rieseguita arriva a 3 vicini su 8 in comune, non 4). Ho controllato i punti delicati: coppie positive in entrambi i versi, rumore diverso dal target, segni dei gradienti, valori vecchi in tutti gli aggiornamenti, accumulo con `np.add.at`. **Non ho trovato bug.**

### Notebook 1 · Il classificatore sugli embedding giocattolo

```python
def sigmoid(z):
    return 1 / (1 + np.exp(-z))

apricot = np.array([0.5, 1.0, -0.5])     # target embedding w
jam     = np.array([1.0, 0.5,  0.0])     # context embeddings c
matrix  = np.array([-0.5, 0.5, 1.0])
tolstoy = np.array([0.0, -1.0, 0.5])

for name, c in (("jam", jam), ("matrix", matrix), ("Tolstoy", tolstoy)):
    z = c @ apricot
    print(..., sigmoid(z), sigmoid(-z))
print(sigmoid(jam @ apricot) * sigmoid(matrix @ apricot))
```

Output:

```text
dot(jam, apricot) =  1.00   P(+|apricot, jam) = 0.731   P(-|apricot, jam) = 0.269
dot(matrix, apricot) = -0.25   P(+|apricot, matrix) = 0.438   P(-|apricot, matrix) = 0.562
dot(Tolstoy, apricot) = -1.25   P(+|apricot, Tolstoy) = 0.223   P(-|apricot, Tolstoy) = 0.777
P(+|apricot, jam and matrix as the window) = 0.320
```

Eq. 5.15-5.17 sui vettori delle [schede 18-19](L11-embedding-word2vec.md#p-18), più Tolstoy della [scheda 30](L11-embedding-word2vec.md#p-30). $P(-)$ è calcolata come $\sigma(-z)$, e infatti $0{,}731+0{,}269 = 1$. L'ultima riga è la finestra di due contesti con l'ipotesi di indipendenza: il prodotto delle due sigmoidi.

### Notebook 2 · La distribuzione delle parole di rumore

```python
def p_alpha(counts, alpha=0.75):
    c = np.asarray(counts, float) ** alpha
    return c / c.sum()

print("Eq. 5.20:", p_alpha([0.99, 0.01]))
counts = np.array([500, 300, 150, 40, 10])        # the, of, coffee, cup, aardvark
pa = p_alpha(counts)
sample = rng.choice(len(words), size=10_000, p=pa)
```

Output:

```text
Eq. 5.20: [0.969 0.031]
the       P = 0.500   P_alpha = 0.437   sampled 0.437
of        P = 0.300   P_alpha = 0.298   sampled 0.298
coffee    P = 0.150   P_alpha = 0.177   sampled 0.177
cup       P = 0.040   P_alpha = 0.066   sampled 0.064
aardvark  P = 0.010   P_alpha = 0.023   sampled 0.023
```

$P_\alpha$ della [scheda 22](L11-embedding-word2vec.md#p-22): la funzione accetta conteggi o probabilità indifferentemente, perché la normalizzazione elimina il fattore comune ($0{,}99^{0{,}75}$ e $990^{0{,}75}$ differiscono per la stessa costante). Le frequenze campionate su 10.000 estrazioni coincidono con $P_\alpha$ alla seconda cifra: il campionamento fa davvero quello che dice la formula. È anche la soluzione dell'esercizio 4.

### Notebook 3 · Loss, gradienti controllati numericamente e un passo di SGD

```python
def sgns_loss(w, c_pos, c_negs):
    return -(np.log(sigmoid(c_pos @ w)) + sum(np.log(sigmoid(-c @ w)) for c in c_negs))

def sgns_gradients(w, c_pos, c_negs):
    g_pos = (sigmoid(c_pos @ w) - 1) * w                        # Eq. 5.22
    g_negs = [sigmoid(c @ w) * w for c in c_negs]                # Eq. 5.23
    g_w = (sigmoid(c_pos @ w) - 1) * c_pos + sum(sigmoid(c @ w) * c for c in c_negs)   # Eq. 5.24
    return g_pos, g_negs, g_w

def numerical_gradient(f, x, h=1e-6):        # central differences
    ...  g[i] = (f(x + e) - f(x - e)) / (2 * h)

def sgd_step(w, c_pos, c_negs, eta):
    g_pos, g_negs, g_w = sgns_gradients(w, c_pos, c_negs)    # all with the old values
    return w - eta * g_w, c_pos - eta * g_pos, [c - eta * g for c, g in zip(c_negs, g_negs)]
```

Output:

```text
dL/dc_pos  Eq. 5.22 [-0.134 -0.269  0.134]   numerical [-0.134 -0.269  0.134]
dL/dc_neg1 Eq. 5.23 [ 0.219  0.438 -0.219]   numerical [ 0.219  0.438 -0.219]
dL/dw      Eq. 5.24 [-0.488 -0.138  0.549]   numerical [-0.488 -0.138  0.549]

before: dot products [ 1.   -0.25 -1.25]  loss 1.14
after:  dot products [ 1.524 -1.012 -1.66 ]  loss 0.68
new apricot [ 0.744  1.069 -0.775]   new jam [ 1.067  0.634 -0.067]
```

Le tre funzioni centrali del notebook. `sgns_loss` è l'ultima riga della Eq. 5.21 ([scheda 24](L11-embedding-word2vec.md#p-24)), `sgns_gradients` le Eq. 5.22-5.24 ([schede 27-28](L11-embedding-word2vec.md#p-27)). Il **controllo con le differenze finite** è il modo standard di verificare un gradiente scritto a mano: si sposta una coordinata di $\pm h$ e si guarda di quanto cambia la loss; le due colonne coincidono, quindi le formule del libro sono giuste (ed è la verifica numerica dell'esercizio 6). `sgd_step` calcola tutti i gradienti prima di aggiornare, come richiede la [scheda 29](L11-embedding-word2vec.md#p-29), e riproduce esattamente i numeri della [scheda 30](L11-embedding-word2vec.md#p-30).

### Notebook 4 · Il corpus: le docstring della libreria standard

```python
MODULES = """os re json collections itertools random ... zlib bz2 lzma""".split()

def module_text(name):        # docstring of the module and of its public functions and classes
def tokenize(text):           # lower case, sentences without code, punctuation as tokens

docs = {m: tokenize(module_text(m)) for m in MODULES}
docs = {m: t for m, t in docs.items() if len(t) >= 50}

MIN_COUNT = 5
vocab = [w for w, c in freq.most_common() if w.isalpha() and c >= MIN_COUNT]
noise_p = p_alpha(counts)
seqs = [np.array([index[t] for t in docs[m] if t in index]) for m in docs]
```

Output:

```text
123 modules, 60295 tokens, 4443 types
most frequent: . 3788, the 3616, a 1754, , 1747, is 1338, to 1304, of 1169, and 804, ( 755, ) 748, for 742, be 717
vocabulary: 1266 words seen at least 5 times; 45182 tokens kept for training
```

Lo stesso corpus dei notebook della L4 e della L10, così si possono confrontare i vicini con quelli della PPMI. Per skip-gram si tengono solo le parole alfabetiche viste almeno 5 volte (1266 tipi) e si buttano gli altri token, punteggiatura compresa, **prima** di prendere le finestre: due parole separate da una virgola o da una parola rara risultano adiacenti. È anche quello che fa il word2vec originale con la soglia `min_count`. Restano 45.182 token di training.

Rieseguito con un'altra versione di Python (la mia: 3.13) il corpus cambia, come il notebook avverte: 124 moduli, 61.083 token, 1292 parole nel vocabolario, 45.866 token di training. Da qui in poi i numeri del training differiscono dagli output salvati, che sono quelli commentati qui.

### Notebook 5 · Training di SGNS da zero

```python
def positive_pairs(seqs, L):
    for s in seqs:
        for off in range(1, L + 1):
            out.append(np.stack([s[:-off], s[off:]], 1)); out.append(np.stack([s[off:], s[:-off]], 1))

def train_sgns(seqs, L=2, d=50, k=5, epochs=5, eta=0.025, batch=1024, seed=0):
    W = (rng.random((V, d)) - 0.5) / d       # target embeddings
    C = (rng.random((V, d)) - 0.5) / d       # context embeddings
    for ep in range(epochs):
        N = rng.choice(V, size=(len(P), k), p=noise_p)       # k noise words per positive pair
        ...                                                   # redraw noise words equal to the target
        for b in range(0, len(P), batch):
            w, cp, cn = W[wi], C[ci], C[ni]
            sp = sigmoid(np.einsum("bd,bd->b", cp, w))            # P(+|w, c_pos)
            sn = sigmoid(np.einsum("bkd,bd->bk", cn, w))          # P(+|w, c_neg)
            total -= np.log(sp).sum() + np.log(1 - sn).sum()      # Eq. 5.21
            g_cp = (sp - 1)[:, None] * w                          # Eq. 5.22
            g_cn = sn[:, :, None] * w[:, None, :]                 # Eq. 5.23
            g_w = (sp - 1)[:, None] * cp + np.einsum("bk,bkd->bd", sn, cn)   # Eq. 5.24
            np.add.at(C, ci, -eta * g_cp); np.add.at(C, ni.ravel(), -eta * g_cn.reshape(-1, d))
            np.add.at(W, wi, -eta * g_w)
    return W, C, len(P)

W2, C2, n_pairs = train_sgns(seqs, L=2)
E2 = W2 + C2
```

Output:

```text
window ±2, epoch 1: average loss per positive pair 3.121
window ±2, epoch 2: average loss per positive pair 2.607
window ±2, epoch 3: average loss per positive pair 2.547
window ±2, epoch 4: average loss per positive pair 2.513
window ±2, epoch 5: average loss per positive pair 2.472
179990 positive pairs per epoch, each with 5 noise words
```

L'algoritmo del §5.5.2 in una trentina di righe. Le coppie positive: per ogni distanza da 1 a $L$ si accoppia ogni parola con quella $L$ posizioni dopo, nei due versi, quindi tutte le coppie della finestra ±$L$. Le parole di rumore si estraggono da $P_\alpha$ ($k = 5$) e si riestraggono se coincidono con il target. Le formule sono quelle delle schede 24-29, applicate a 1024 coppie per volta: tutti i gradienti di un blocco si calcolano con i valori vecchi e si applicano insieme con `np.add.at`, che somma correttamente quando la stessa parola compare più volte nel blocco (un semplice `C[ci] -= ...` perderebbe gli aggiornamenti ripetuti). Ogni parola è rappresentata da $\mathbf w_i + \mathbf c_i$ ([scheda 32](L11-embedding-word2vec.md#p-32)).

La loss media per coppia positiva (che comprende i 5 termini di rumore) parte da circa 3,1 e scende a 2,47; per confronto, con tutti i prodotti a 0 varrebbe $6\ln2 = 4{,}16$. Rieseguito: 182.720 coppie e loss finale 2,490, stesso andamento.

### Notebook 6 · I vicini più prossimi

```python
def neighbors(E, word, k=8):
    v = E[index[word]]
    norms = np.linalg.norm(E, axis=1); norms[norms == 0] = 1
    cos = E @ v / (norms * np.linalg.norm(v))
    return [(vocab[j], round(float(cos[j]), 2)) for j in np.argsort(-cos) if vocab[j] != word][:k]
```

Output:

```text
file       [('source', 0.73), ('compiled', 0.73), ('opened', 0.67), ('open', 0.65), ('executable', 0.63), ('binary', 0.63), ...]
string     [('containing', 0.79), ('identifying', 0.73), ('ascii', 0.72), ('single', 0.69), ('query', 0.69), ('byte', 0.67), ...]
error      [('handling', 0.8), ('encoding', 0.68), ('occurs', 0.62), ('which', 0.62), ('raised', 0.62), ...]
true       [('false', 0.82), ('legacy', 0.7), ('otherwise', 0.69), ('else', 0.68), ...]
list       [('lines', 0.72), ('tuples', 0.71), ('hexadecimal', 0.71), ('elements', 0.67), ('host', 0.65), ('sequence', 0.65), ...]
directory  [('package', 0.75), ('tree', 0.73), ('pickle', 0.58), ('cache', 0.56), ...]
thread     [('library', 0.79), ('main', 0.65), ('hierarchy', 0.64), ('execution', 0.63), ...]
socket     [('browser', 0.86), ('launcher', 0.75), ('required', 0.71), ('creating', 0.7), ...]
```

Il metodo della [scheda 43](L11-embedding-word2vec.md#p-43): ordinare il vocabolario per coseno. Il commento della cella 14 è coerente con l'output: *file* ha vicini sensati (*source, compiled, opened, open, executable, binary*), *error* ha *handling, occurs, raised*, *list* ha *lines, tuples, elements, sequence*. *true* è vicinissimo a *false* (0,82): gli **antonimi** compaiono negli stessi contesti e la similarità distribuzionale non li separa. *socket* invece è rumore. 45.000 token sono pochissimi: gli embedding preaddestrati di word2vec vengono da circa 100 miliardi di parole.

Rieseguito, le liste cambiano nei dettagli ma restano dello stesso tipo (file: source, compiled, open, binary, executable; true: false 0,82).

### Notebook 7 · La dimensione della finestra

```python
W8, C8, n8 = train_sgns(seqs, L=8, epochs=3)
E8 = W8 + C8
for w in ("file", "error", "directory", "thread", "socket"):
    print(w, "±2", neighbors(E2, w, 6)); print("±8", neighbors(E8, w, 6))
```

Output:

```text
714056 positive pairs per epoch, 4.0 times those of the window ±2
directory  ±2 ['package', 'tree', 'pickle', 'cache', 'node', 'killed']
           ±8 ['top', 'relative', 'working', 'package', 'sys', 'destination']
thread     ±2 ['library', 'main', 'hierarchy', 'execution', 'signature', 'module']
           ±8 ['loop', 'signals', 'event', 'control', 'release', 'threads']
```

L'esperimento delle [schede 45-46](L11-embedding-word2vec.md#p-45) sul nostro corpus. Con ±8 le coppie sono 3,97 volte quelle di ±2 (il notebook arrotonda a 4,0), per questo bastano 3 epoche. I vicini di *directory* (*top, relative, working, destination*) e di *thread* (*loop, signals, event, threads*) con ±8 sono parole dello stesso argomento. Il commento è onesto: su un corpus così piccolo la differenza non è netta e entrambe le liste mescolano parti del discorso. Rieseguito: thread ±8 dà *control, threading, threads, loop, main, event*, stessa conclusione.

### Notebook 8 · Analogie con il parallelogramma

```python
def analogy(E, a, b, a_star, k=3, exclude=True):
    t = E[index[b]] - E[index[a]] + E[index[a_star]]
    cos = E @ t / (norms * np.linalg.norm(t))
    out = [vocab[j] for j in np.argsort(-cos) if not (exclude and vocab[j] in (a, b, a_star))]
    return out[:k]
```

Output:

```text
key : keys :: value : ?    ['values', 'options', 'field']    without excluding the inputs: ['values', 'value', 'options']
file : files :: string : ?    ['imap', 'unicode', 'directories']    ...
line : lines :: file : ?    ['compressed', 'descriptor', 'parse']    without excluding the inputs: ['compressed', 'descriptor', 'file']
read : write :: input : ?    ['constructor', 'string', 'configuration']    ...
byte : bytes :: character : ?    ['aninteger', 'array', 'create']    without excluding the inputs: ['bytes', 'character', 'aninteger']
```

Eq. 5.28 ([scheda 48](L11-embedding-word2vec.md#p-48)) con il coseno al posto della distanza euclidea, come dichiara il testo della cella 18. Solo *key : keys :: value* dà la risposta attesa, *values*; le altre falliscono (*strings, files, output, characters* non escono). E si vede la cautela della [scheda 50](L11-embedding-word2vec.md#p-50): senza escludere gli input, *byte : bytes :: character* restituisce per prima *bytes*, una delle parole date. Rieseguito: stessa situazione (values corretta; senza esclusione il primo risultato è *character*, di nuovo un input).

### Notebook 9 · Variabilità fra due training (extra)

```python
W2b, C2b, _ = train_sgns(seqs, L=2, seed=1, verbose=False)
E2b = W2b + C2b
for w in (...):
    a = {x for x, _ in neighbors(E2, w)}; b = {x for x, _ in neighbors(E2b, w)}
    print(w, len(a & b), "of 8 in common")
```

Output:

```text
file       7 of 8 in common      string     7 of 8 in common
error      7 of 8 in common      true       6 of 8 in common
list       5 of 8 in common      directory  4 of 8 in common
thread     5 of 8 in common      socket     6 of 8 in common
```

Un argomento del §5.9 che le slide non trattano: cambiando solo il seme (inizializzazione e parole di rumore) fra 4 e 7 degli 8 vicini restano gli stessi. Per questo, quando si usano gli embedding per studiare le associazioni di un corpus, il libro consiglia di addestrare più embedding su campioni bootstrap dei documenti e mediare. Rieseguito con l'altro corpus il minimo scende a 3 su 8 (*thread*): la frase «between 4 and 7» della cella 23 vale per gli output salvati, non in generale, e conferma ancora di più la variabilità.

### Notebook 10 · Verifica della scheda: esercizi 1-5

```python
print(2 * 50_000 * 300)                                   # exercise 1
pairs2 = [(s[i], s[j]) for i ... for j in range(max(0, i - 2), min(len(s), i + 3)) if j != i]   # exercise 2
coffee, cup, drink, tax, seven = ...                         # exercise 3
print(p_alpha([500, 300, 150, 40, 10]))                      # exercise 4
print(sgns_loss(coffee, cup, [tax, seven]), 3 * math.log(2)) # exercise 5
```

Output:

```text
exercise 1   weights: 50000 sparse, 300 dense; skip-gram parameters 2 x 50,000 x 300 = 30000000
exercise 2   pairs for fox: [('fox', 'quick'), ('fox', 'brown'), ('fox', 'jumps'), ('fox', 'over')]  all positive pairs: 30  negative pairs with k = 3: 90
exercise 3   dot(coffee, cup) =  3.0   P(+) = 0.953   P(-) = 0.047
exercise 3   dot(coffee, drink) =  2.0   P(+) = 0.881   P(-) = 0.119
exercise 3   dot(coffee, tax) = -1.0   P(+) = 0.269   P(-) = 0.731
exercise 3   dot(coffee, seven) = -2.0   P(+) = 0.119   P(-) = 0.881
             P(+|coffee, cup and drink) = 0.839, log = -0.176
exercise 4   P_alpha = [0.437 0.298 0.177 0.066 0.023]
             expected out of 1,000 noise words: the 500.0 and 436.5 ; aardvark 10.0 and 23.2
exercise 5   L = 0.489   terms: [0.049, 0.313, 0.127]  all dot products 0: 2.079
```

Il ricalcolo degli esercizi numerici 1-5 della scheda: tutti i valori coincidono con le mie soluzioni (sezione Studio). Questa cella e la successiva danno gli stessi output anche rieseguite, perché non dipendono dal corpus. Fare prima gli esercizi a mano.

### Notebook 11 · Verifica della scheda: esercizi 7 e 9-12

```python
g_pos, g_negs, g_w = sgns_gradients(w7, cpos7, [cneg7])      # exercise 7
for eta in (0.5, 1.0): w_, cp_, cn_ = sgd_step(w7, cpos7, [cneg7], eta)
char_ngrams("where", 3); char_ngrams("cats", 4)              # exercise 9
parallelogram("man", "woman", "king", [...])                 # exercise 10, Euclidean distance
cos(v, she) - cos(v, he)                                     # exercise 11
rank = lambda x: np.argsort(np.argsort(-x)) + 1               # exercise 12, Spearman
```

Output:

```text
exercise 7   before: dots 0.0 1.0  loss 2.006
             gradients [-0.5 -0. ] [0.731 0.   ] [0.731 0.231]
             eta = 0.5: w = [ 0.634 -0.116], c_pos = [0.25 1.  ], c_neg = [0.634 1.   ]; dots 0.043, 0.287; loss 1.519
             eta = 1.0: w = [ 0.269 -0.231], c_pos = [0.5 1. ], c_neg = [0.269 1.   ]; dots -0.097, -0.159; loss 1.360
exercise 9   ['<wh', 'whe', 'her', 'ere', 're>'] ['<ca', 'cat', 'ats', 'ts>'] ['<ca', 'cat', 'atl', 'tli', 'lik', 'ike', 'ke>'] ['<cat', 'cats', 'ats>']
exercise 10  (array([4., 3.]), [(0.2, 'queen'), (1.118, 'princess'), (2.0, 'king'), (3.0, 'woman'), (3.606, 'man')])
             (array([5., 0.]), [(1.0, 'potato'), (1.5, 'brown'), (1.581, 'potatoes'), (3.606, 'cherry'), (4.243, 'red')])
exercise 11  nurse +0.759   engineer -0.632   teacher +0.000
exercise 12  human ranks [1 3 4 2 5]  model ranks [1 3 2 4 5]  rho = 0.60
```

Il resto della scheda. Un dettaglio istruttivo nell'esercizio 7: con $\eta = 1$ la loss scende (1,360) ma il prodotto con il contesto positivo passa da 0 a $-0{,}097$, cioè **peggiora**: con un passo troppo lungo lo spostamento di $\mathbf w$ verso $\mathbf c_{pos}$ è sopraffatto da quello lontano da $\mathbf c_{neg}$. Con $\eta = 0{,}5$ entrambi i prodotti si muovono nel verso giusto. La funzione `rank` con il doppio `argsort` dà il rango 1 al valore più alto; funziona perché non ci sono pareggi.

### Notebook 12 · Che cosa fare dopo

```python
# suggestions of the last cell
train_sgns(seqs, L=2, d=100, k=10, epochs=10)   # other settings
E = W2                                          # W alone instead of W + C
```

L'ultima cella propone esperimenti: più epoche, $d = 100$, $k = 10$, soglia di frequenza 3, solo $W$ invece di $W + C$; un corpus più grande (un romanzo di pubblico dominio) per vedere migliorare vicini e analogie; il confronto con i vicini della PPMI del notebook della L10, sullo stesso corpus. Il notebook non produce figure.

## Studio ed esercizi

### Guida allo studio (circa 4 h 05 min)

**Dal contare al predire e il classificatore** (40 min)

Schede 4-19. Saper dire perché i vettori densi funzionano meglio (parametri, sinonimia), che cos'è la self-supervision e quali sono le due semplificazioni rispetto a un language model neurale. Il classificatore: $P(+\mid w,c) = \sigma(\mathbf c\cdot\mathbf w)$, $P(-) = \sigma(-\mathbf c\cdot\mathbf w)$, l'indipendenza dei contesti, le due matrici $W$ e $C$ ($2|V|d$ parametri). Rifare a mano 0,73 e 0,44 della scheda 18. Esercizi 1, 2, 3. Libro pp. 136-139.

**Negative sampling, loss, gradienti, un passo di SGD** (75 min)

Schede 20-33, il cuore della lezione. Costruire esempi positivi e negativi da una frase; $P_\alpha$ con $\alpha = 0{,}75$ e l'esempio 0,99/0,01 → 0,97/0,03 (collegarlo alla PPMI-α della L10); scrivere la loss nei quattro passaggi; derivare i tre gradienti (esercizio 6) e leggerli come "previsto meno vero per l'input"; rifare il passo della scheda 30 (loss da 1,14 a 0,68) e l'esercizio 7 senza guardare. Esercizi 4, 5, 6, 7, 8a e aggiuntivi A e C; celle 2-6 del notebook. Libro pp. 139-142.

**CBOW, fasttext, GloVe** (25 min)

Schede 35-41. Differenza fra skip-gram e CBOW (direzione della previsione, media del contesto); gli n-grammi di fasttext con i simboli di confine e perché aiutano con parole sconosciute e morfologia ricca; GloVe e il legame fra SGNS e PMI (riquadro della scheda 40). Saper riempire a memoria la tabella della scheda 41. Esercizio 9 e aggiuntivo B. Libro p. 142.

**Proprietà: vicini, finestra, analogie, storia** (30 min)

Schede 42-51. Vicini più prossimi e t-SNE; finestre corte (simili, stessa parte del discorso) e lunghe (collegate per argomento), l'esempio di Hogwarts; il parallelogramma con l'Eq. 5.28 e le sue cautele (escludere gli input; il refuso *potatoe* della scheda 50); i tre esempi di semantica storica. Esercizi 8b e 10. Libro pp. 142-145.

**Bias e valutazione** (25 min)

Schede 52-57. Gli esempi di Bolukbasi (homemaker, nurse), l'amplificazione del bias, IAT e Caliskan; danno allocativo e rappresentazionale con un esempio ciascuno; valutazione estrinseca contro intrinseca, WordSim-353, SimLex-999, TOEFL, la correlazione di Spearman. Esercizi 11 e 12. Libro pp. 145-147.

**Notebook e ripasso orale** (50 min)

Eseguire il notebook dall'inizio e leggere `sgns_gradients`, `sgd_step` e `train_sgns` finché ogni riga corrisponde a una formula delle schede 24-29. Provare uno degli esperimenti dell'ultima cella (per esempio solo $W$ invece di $W + C$, o $k = 10$) e confrontare i vicini. Poi rispondere ad alta voce alle domande della sezione orale.

### Esercizi

#### Esercizio 1 (scheda L11): vettori sparsi e densi

(a) Un classificatore di sentiment, una regressione logistica, riceve come input il vettore bag of words della recensione (il conteggio di ciascuna delle $|V| = 50.000$ parole) oppure la somma degli embedding delle sue parole, con $d = 300$. Quanti pesi impara, senza il bias, nei due casi? (b) Le recensioni di training contengono *car* ma mai *automobile*. Una recensione di test dice *this automobile is great*. Perché gli embedding possono aiutare e il bag of words no? (c) Quanti parametri impara skip-gram con un vocabolario di 50.000 parole e $d = 300$? Servono dati etichettati a mano?

<details><summary>Soluzione</summary>

(a) La regressione logistica binaria ha un peso per dimensione dell'input: **50.000** pesi con il bag of words, **300** con la somma degli embedding.

(b) Con il bag of words *automobile* è una colonna mai vista in training: il suo peso è rimasto al valore iniziale (0) e la parola non contribuisce alla decisione. Con gli embedding, *automobile* ha un vettore vicino a quello di *car* (imparato da un grande corpus non etichettato, dove le due parole compaiono in contesti simili), quindi la somma degli embedding della recensione di test è vicina a quella di *this car is great* e il classificatore, che ha imparato i pesi sulle direzioni dello spazio e non sulle singole parole, la tratta in modo simile. È la sinonimia della scheda 6.

(c) Due matrici $W$ e $C$, ciascuna $|V|\times d$: $2\times50.000\times300 = $ **30.000.000** parametri. Non servono etichette manuali: skip-gram è **self-supervised**, le coppie positive vengono dal testo e quelle negative dal campionamento. Verificato nella cella 25 del notebook.

</details>

#### Esercizio 2 (scheda L11): esempi positivi e negativi

La frase *the quick brown fox jumps over the lazy dog*, con una finestra di ±2 parole e $k = 3$ parole di rumore per ogni coppia positiva. (a) Elenca le coppie positive $(w, c_{pos})$ per il target *fox*. Quante coppie negative le accompagnano? (b) Quante coppie positive dà l'intera frase, prendendo a turno ciascuna delle 9 parole come target (con meno contesti alle due estremità)? E quante negative? (c) Una parola di rumore è una parola casuale del lessico diversa dal target. Può essere per caso un vero contesto del target? Perché non è un problema serio?

<details><summary>Soluzione</summary>

(a) *fox* è in posizione 4; i contesti sono le due parole prima e le due dopo: (fox, quick), (fox, brown), (fox, jumps), (fox, over). 4 coppie positive, $4\times3 = $ **12** coppie negative.

(b) Contesti per posizione: *the* (1) ne ha 2, *quick* 3, le parole dalla 3 alla 7 ne hanno 4 ciascuna, *lazy* 3, *dog* 2. Totale $2+3+5\cdot4+3+2 = $ **30** coppie positive e $30\times3 = $ **90** negative. Nota: *the* compare due volte e dà due insiemi di coppie diversi; le coppie (the, quick) e (quick, the) sono entrambe presenti, una per ogni verso.

(c) Sì: la parola di rumore è estratta da $P_\alpha$ senza guardare la finestra, e potrebbe essere proprio *brown*, o una parola che in altre frasi è un contesto tipico di *fox*. Non è grave perché (1) con un vocabolario di decine di migliaia di parole la probabilità di pescare proprio un contesto tipico è piccola; (2) quella stessa coppia compare molte volte come positiva nel corpus, e la spinta occasionale nel verso sbagliato è sommersa dalle molte spinte nel verso giusto; (3) l'obiettivo è solo che i contesti veri abbiano prodotti più alti delle parole tipiche del rumore, non un classificatore perfetto. Verificato (a) e (b) nella cella 25 del notebook.

</details>

#### Esercizio 3 (scheda L11): il classificatore skip-gram a mano

Embedding giocattolo con $d = 3$: target *coffee* = [1, 2, 0]; contesti *cup* = [1, 1, 1], *drink* = [0, 1, −1], *tax* = [−1, 0, 1], *seven* = [0, −1, 1]. (a) Calcola il prodotto scalare di *coffee* con ciascuna delle quattro parole di contesto, e $P(+\mid w,c)$ e $P(-\mid w,c)$ per ciascuna (Eq. 5.15 e 5.16). (b) Calcola $P(+\mid w,c_{1:2})$ per la finestra $c_{1:2}$ = (cup, drink) e il suo logaritmo naturale (Eq. 5.17 e 5.18). (c) Quale ipotesi permette di moltiplicare le probabilità delle due parole di contesto?

<details><summary>Soluzione</summary>

(a)

| c | c · coffee | P(+) = σ | P(−) = σ(−x) |
| --- | --- | --- | --- |
| cup | 1 + 2 + 0 = 3 | 0,953 | 0,047 |
| drink | 0 + 2 + 0 = 2 | 0,881 | 0,119 |
| tax | −1 + 0 + 0 = −1 | 0,269 | 0,731 |
| seven | 0 − 2 + 0 = −2 | 0,119 | 0,881 |

Per esempio $\sigma(3) = 1/(1+e^{-3}) = 1/1{,}0498 = 0{,}953$. Nota la simmetria: $P(+\mid coffee, seven) = \sigma(-2) = 0{,}119 = P(-\mid coffee, drink)$, perché i due prodotti scalari sono opposti.

(b) $P(+\mid coffee, cup, drink) = \sigma(3)\,\sigma(2) = 0{,}953\times0{,}881 = $ **0,839**; $\ln 0{,}839 = \ln\sigma(3) + \ln\sigma(2) = -0{,}049 - 0{,}127 = $ **−0,176**.

(c) L'ipotesi che le parole di contesto siano **indipendenti** l'una dall'altra, dato il target: la probabilità congiunta è il prodotto (e il logaritmo la somma). È falsa (*cup* e *drink* sono correlate fra loro) ma rende il calcolo semplice, come in Naive Bayes. Verificato nella cella 25.

</details>

#### Esercizio 4 (scheda L11): scegliere le parole di rumore

Conteggi unigramma in un piccolo corpus di 1000 token (cinque tipi soltanto): the 500, of 300, coffee 150, cup 40, aardvark 10. (a) Calcola $P(w)$ e $P_\alpha(w)$ con $\alpha = 0{,}75$ (Eq. 5.19). (b) Quali parole guadagnano probabilità e quali la perdono? Su 1000 parole di rumore, quante volte ti aspetti *the* e *aardvark* con $P$ e con $P_\alpha$? (c) Perché skip-gram preferisce $P_\alpha$?

<details><summary>Soluzione</summary>

(a) $P$ = 0,500; 0,300; 0,150; 0,040; 0,010. Conteggi alla 0,75: $500^{0{,}75} = 105{,}74$; $300^{0{,}75} = 72{,}08$; $150^{0{,}75} = 42{,}86$; $40^{0{,}75} = 15{,}91$; $10^{0{,}75} = 5{,}62$; somma 242,21. $P_\alpha$ = **0,437; 0,298; 0,177; 0,066; 0,023**.

(b) Perdono probabilità *the* (da 0,500 a 0,437) e, di pochissimo, *of* (da 0,300 a 0,298); guadagnano *coffee* (×1,18), *cup* (×1,64) e soprattutto *aardvark* (×2,32): più la parola è rara, più guadagna in proporzione. Su 1000 estrazioni: *the* 500 con $P$, circa **437** con $P_\alpha$; *aardvark* 10 con $P$, circa **23** con $P_\alpha$.

(c) Con $P$ quasi tutte le parole di rumore sarebbero parole funzionali frequentissime: il modello imparerebbe soprattutto a distinguere i contesti veri da *the* e *of*, e le parole rare quasi non comparirebbero mai come negativi, quindi i loro vettori di contesto riceverebbero pochi aggiornamenti. $P_\alpha$ appiattisce un po' la distribuzione, dà alle parole rare qualche occasione in più di fare da rumore, e sperimentalmente produce embedding migliori. È lo stesso trucco della PPMI con $\alpha$ della L10. Verificato nelle celle 4 e 25.

</details>

#### Esercizio 5 (scheda L11): la loss

Gli embedding giocattolo dell'esercizio 3, con la coppia positiva (coffee, cup) e le parole di rumore *tax* e *seven* ($k = 2$). (a) Calcola la loss $L(w, c_{pos}, c_{neg})$ della Eq. 5.21 con logaritmi naturali. (b) Quanto vale la loss di un classificatore perfetto, e quanto quando tutti i prodotti scalari sono 0? (c) Quale dei tre termini contribuisce di più alla loss, e quale aggiornamento la ridurrà?

<details><summary>Soluzione</summary>

(a) $L = -[\ln\sigma(\mathbf{cup}\cdot\mathbf{coffee}) + \ln\sigma(-\mathbf{tax}\cdot\mathbf{coffee}) + \ln\sigma(-\mathbf{seven}\cdot\mathbf{coffee})] = -[\ln\sigma(3) + \ln\sigma(1) + \ln\sigma(2)]$. Termini: $-\ln0{,}953 = 0{,}049$; $-\ln0{,}731 = 0{,}313$; $-\ln0{,}881 = 0{,}127$. Somma $L = $ **0,489**.

(b) Classificatore perfetto: $\sigma(\mathbf c_{pos}\cdot\mathbf w)\to1$ e $\sigma(-\mathbf c_{neg}\cdot\mathbf w)\to1$, quindi ogni termine $\to0$ e $L\to$ **0** (lo si raggiunge solo al limite, con prodotti infiniti). Tutti i prodotti a 0: ogni sigmoide vale 0,5, ogni termine $\ln 2$, $L = 3\ln2 = $ **2,079**: è la loss di un classificatore che non sa niente.

(c) Il termine più grande è quello di **tax** (0,313): il prodotto $\mathbf{tax}\cdot\mathbf{coffee} = -1$ è negativo ma non abbastanza, $P(+\mid coffee, tax) = 0{,}269$ è ancora alta per una parola di rumore. Il gradiente rispetto a $\mathbf{tax}$ è $\sigma(-1)\,\mathbf{coffee} = 0{,}269\cdot[1, 2, 0]$, il più grande dei gradienti dei rumori: l'aggiornamento $\mathbf{tax} \leftarrow \mathbf{tax} - \eta\,0{,}269\,\mathbf{coffee}$ allontana *tax* da *coffee*, e nello stesso passo $\mathbf{coffee}$ riceve il termine $+0{,}269\,\mathbf{tax}$ nel gradiente, cioè si sposta lontano da *tax*. Entrambi riducono il prodotto e quindi la loss. Verificato nella cella 25.

</details>

#### Esercizio 6 (scheda L11, libro 5.3): i gradienti della loss di skip-gram

Ricava i gradienti delle Eq. 5.22-5.24 derivando la loss della Eq. 5.21 rispetto a $\mathbf c_{pos}$, $\mathbf c_{neg_i}$ e $\mathbf w$. Puoi usare $\frac{d\sigma(z)}{dz} = \sigma(z)(1-\sigma(z))$ e il fatto che la derivata del prodotto scalare $\mathbf c\cdot\mathbf w$ rispetto a $\mathbf w$ è $\mathbf c$.

<details><summary>Soluzione</summary>

**Passo 1, un lemma.** $\frac{d}{dz}\ln\sigma(z) = \frac{\sigma'(z)}{\sigma(z)} = \frac{\sigma(z)(1-\sigma(z))}{\sigma(z)} = 1-\sigma(z)$. Inoltre $1-\sigma(-z) = \sigma(z)$.

**Passo 2, la loss.** $L = -\ln\sigma(\mathbf c_{pos}\cdot\mathbf w) - \sum_{i=1}^{k}\ln\sigma(-\mathbf c_{neg_i}\cdot\mathbf w)$.

**Passo 3, rispetto a $\mathbf c_{pos}$.** Solo il primo termine dipende da $\mathbf c_{pos}$. Con la regola della catena, $z = \mathbf c_{pos}\cdot\mathbf w$ e $\partial z/\partial\mathbf c_{pos} = \mathbf w$:
$$\frac{\partial L}{\partial\mathbf c_{pos}} = -(1-\sigma(\mathbf c_{pos}\cdot\mathbf w))\,\mathbf w = [\sigma(\mathbf c_{pos}\cdot\mathbf w)-1]\,\mathbf w$$

**Passo 4, rispetto a $\mathbf c_{neg_i}$.** Solo l'$i$-esimo termine della somma. Ora $z = -\mathbf c_{neg_i}\cdot\mathbf w$, $\partial z/\partial\mathbf c_{neg_i} = -\mathbf w$:
$$\frac{\partial L}{\partial\mathbf c_{neg_i}} = -(1-\sigma(-\mathbf c_{neg_i}\cdot\mathbf w))(-\mathbf w) = (1-\sigma(-\mathbf c_{neg_i}\cdot\mathbf w))\,\mathbf w = \sigma(\mathbf c_{neg_i}\cdot\mathbf w)\,\mathbf w$$

**Passo 5, rispetto a $\mathbf w$.** Tutti i termini dipendono da $\mathbf w$; si ripetono i conti con $\partial(\mathbf c\cdot\mathbf w)/\partial\mathbf w = \mathbf c$ e si somma:
$$\frac{\partial L}{\partial\mathbf w} = [\sigma(\mathbf c_{pos}\cdot\mathbf w)-1]\,\mathbf c_{pos} + \sum_{i=1}^{k}\sigma(\mathbf c_{neg_i}\cdot\mathbf w)\,\mathbf c_{neg_i}$$

**Lettura.** Ogni gradiente è (probabilità prevista − etichetta) × l'altro vettore, con etichetta 1 per il contesto vero e 0 per il rumore: la stessa forma $(\hat y - y)x$ della regressione logistica. Verifica numerica: la cella 6 del notebook confronta le tre formule con le differenze finite sui vettori della scheda 30 e trova gli stessi valori alla terza cifra.

</details>

#### Esercizio 7 (scheda L11): un passo di stochastic gradient descent

Embedding con $d = 2$: target $\mathbf w = [1, 0]$, contesto $\mathbf c_{pos} = [0, 1]$, una parola di rumore $\mathbf c_{neg} = [1, 1]$ ($k = 1$), learning rate $\eta = 0{,}5$. (a) Calcola i due prodotti scalari, le due sigmoidi e la loss (logaritmi naturali). (b) Calcola i tre gradienti (Eq. 5.22-5.24) e i vettori aggiornati (Eq. 5.25-5.27), usando i valori vecchi in tutti e tre gli aggiornamenti. (c) Calcola i nuovi prodotti scalari e la nuova loss. Il passo ha fatto quello che doveva?

<details><summary>Soluzione</summary>

(a) $\mathbf c_{pos}\cdot\mathbf w = 0$, $\mathbf c_{neg}\cdot\mathbf w = 1$. $\sigma(0) = 0{,}5$, $\sigma(1) = 0{,}731$. $L = -\ln\sigma(0) - \ln\sigma(-1) = 0{,}693 + 1{,}313 = $ **2,006**.

(b) $\partial L/\partial\mathbf c_{pos} = (0{,}5-1)[1, 0] = [-0{,}5;\ 0]$. $\partial L/\partial\mathbf c_{neg} = 0{,}731\,[1, 0] = [0{,}731;\ 0]$. $\partial L/\partial\mathbf w = -0{,}5\,[0, 1] + 0{,}731\,[1, 1] = [0{,}731;\ 0{,}231]$.  
Aggiornamenti: $\mathbf c_{pos} = [0, 1] - 0{,}5[-0{,}5; 0] = $ **[0,25; 1]**; $\mathbf c_{neg} = [1, 1] - 0{,}5[0{,}731; 0] = $ **[0,634; 1]**; $\mathbf w = [1, 0] - 0{,}5[0{,}731; 0{,}231] = $ **[0,634; −0,116]**.

(c) $\mathbf c_{pos}\cdot\mathbf w = 0{,}25\cdot0{,}634 + 1\cdot(-0{,}116) = 0{,}159 - 0{,}116 = $ **0,043** (era 0); $\mathbf c_{neg}\cdot\mathbf w = 0{,}634^2 - 0{,}116 = 0{,}402 - 0{,}116 = $ **0,287** (era 1). Nuova loss: $-\ln\sigma(0{,}043) - \ln\sigma(-0{,}287) = 0{,}672 + 0{,}847 = $ **1,519**. Sì: il prodotto con il contesto vero è salito, quello con il rumore è sceso molto, la loss è passata da 2,006 a 1,519.

Nota: con $\eta = 1$ la loss scende ancora (1,360) ma il prodotto positivo diventa $-0{,}097$, cioè peggiora: un learning rate troppo grande può spostare un termine nel verso sbagliato pur riducendo la somma. Verificato nella cella 26.

</details>

#### Esercizio 8 (scheda L11): due embedding e la dimensione della finestra

(a) Dopo il training skip-gram ha due embedding per ogni parola. Quale vettore rappresenta una parola? (b) Due liste di vicini di *guitar*, da embedding addestrati con finestra ±2 e ±10 sullo stesso corpus: (violin, piano, cello, banjo) e (chords, strummed, band, solo). Quale lista viene da quale finestra, e perché?

<details><summary>Soluzione</summary>

(a) Il target embedding $\mathbf w_i$ (buttando via la matrice $C$) oppure la somma $\mathbf w_i + \mathbf c_i$; entrambe le scelte sono comuni (libro p. 142). Il notebook usa la somma.

(b) (violin, piano, cello, banjo) viene dalla finestra **±2**: con contesti corti contano le parole immediatamente vicine (*play the \_\_\_*, *acoustic \_\_\_*), condivise da parole **simili** della stessa parte del discorso, altri strumenti. (chords, strummed, band, solo) viene da **±10**: con finestre lunghe contano le parole dello stesso argomento, e i vicini sono **collegati** ma non simili (c'è anche un verbo, *strummed*). È l'esempio di Hogwarts della scheda 46.

</details>

#### Esercizio 9 (scheda L11, dall'esempio fasttext del libro): subword

(a) Scrivi i trigrammi di caratteri di *where*, con i simboli di confine < e >, e quelli di *cats*. (b) La parola *catlike* non è mai comparsa nel training. Quali trigrammi condivide con *cats*, e come le dà un embedding fasttext? (c) Scrivi i 4-grammi di *cats*. Perché fasttext aiuta soprattutto nelle lingue a morfologia ricca?

<details><summary>Soluzione</summary>

(a) *where* → <where> → `<wh` `whe` `her` `ere` `re>` (più la sequenza intera <where>). *cats* → <cats> → `<ca` `cat` `ats` `ts>`.

(b) *catlike* → <ca, cat, atl, tli, lik, ike, ke>. In comune con *cats*: **<ca** e **cat**. Non essendoci un vettore per la parola intera, fasttext rappresenta *catlike* come la **somma degli embedding dei suoi n-grammi** (tutti quelli da 3 a 6 caratteri in pratica), imparati sulle altre parole che li contengono: <ca e cat da *cat, cats, catch*; lik, ike, ke> da *like, alike, lifelike*. Il vettore risultante sta fra la zona dei gatti e quella di *like*, il che per una parola composta è ragionevole.

(c) 4-grammi di *cats*: `<cat` `cats` `ats>`. Nelle lingue a morfologia ricca ogni lemma ha molte forme (in italiano *parlo, parli, parlavamo, parlerebbero*...; in finlandese o turco ancora di più), molte delle quali rare o assenti dal training. Con word2vec ogni forma ha un vettore indipendente, mal stimato o mancante; con fasttext le forme condividono gli n-grammi della radice (`<par`, `parl`) e quelli delle desinenze, quindi anche una forma rara o mai vista riceve un vettore sensato. Verificato nella cella 26.

</details>

#### Esercizio 10 (scheda L11): il modello del parallelogramma a mano

Vettori giocattolo in 2D: man [1, 1], woman [1, 3], king [4, 1], queen [4; 3,2], princess [3; 3,5]; cherry [3, 3], red [2, 3], potato [6, 0], potatoes [6,5; 0,5], brown [5; 1,5]. (a) Risolvi *man : woman :: king : ?* con il metodo del parallelogramma (Eq. 5.28) e la distanza euclidea, fra tutte le parole della prima metà della tabella. (b) Risolvi *cherry : red :: potato : ?* fra tutte le parole della seconda metà, prima includendo e poi escludendo le tre parole di input. (c) Che cosa mostra (b) su come va usato il metodo, e per quali relazioni funziona meglio?

<details><summary>Soluzione</summary>

(a) $\mathbf b - \mathbf a + \mathbf a^* = \mathbf{woman} - \mathbf{man} + \mathbf{king} = [1-1+4;\ 3-1+1] = [4, 3]$. Distanze: queen $\sqrt{0^2+0{,}2^2} = 0{,}2$; princess $\sqrt{1+0{,}25} = 1{,}118$; king $\sqrt{0+4} = 2$; woman $\sqrt{9+0} = 3$; man $\sqrt{9+4} = 3{,}606$. Risposta: **queen**.

(b) $\mathbf{red} - \mathbf{cherry} + \mathbf{potato} = [2-3+6;\ 3-3+0] = [5, 0]$. Distanze: potato $\sqrt{1+0} = 1{,}0$; brown $\sqrt{0+2{,}25} = 1{,}5$; potatoes $\sqrt{2{,}25+0{,}25} = 1{,}581$; cherry $\sqrt{4+9} = 3{,}606$; red $\sqrt{9+9} = 4{,}243$. Includendo gli input la risposta è **potato**, una delle parole date; escludendo cherry, red e potato la risposta è **brown** (1,5), appena davanti a *potatoes* (1,581).

(c) Il vettore differenza (red − cherry = [−1, 0]) è corto rispetto alle distanze fra parole, quindi il punto cercato resta vicino ad $\mathbf a^*$ (potato) e alle sue varianti morfologiche: le parole di input vanno **escluse esplicitamente**, e anche così una variante (*potatoes*) può arrivare quasi prima. Il metodo funziona meglio per **parole frequenti**, **distanze piccole** e relazioni regolari come paese-capitale, maschile-femminile o le forme flesse; meno per le altre (libro p. 145). Verificato nella cella 26.

</details>

#### Esercizio 11 (scheda L11): misurare un bias

Vettori giocattolo in 2D: he [1, 0], she [0, 1], nurse [0,2; 0,9], engineer [0,9; 0,3], teacher [0,6; 0,6]. (a) Per nurse, engineer e teacher calcola il coseno con *she* e con *he*, e la differenza cos(x, she) − cos(x, he). (b) Un sistema di selezione del personale ordina i documenti dei candidati usando questi embedding. Che tipo di danno potrebbe causare?

<details><summary>Soluzione</summary>

(a) Poiché he e she sono vettori unitari sugli assi, cos(x, he) = $x_1/|\mathbf x|$ e cos(x, she) = $x_2/|\mathbf x|$.

| x | |x| | cos(x, she) | cos(x, he) | differenza |
| --- | --- | --- | --- | --- |
| nurse | $\sqrt{0{,}04+0{,}81} = 0{,}922$ | 0,976 | 0,217 | **+0,759** |
| engineer | $\sqrt{0{,}81+0{,}09} = 0{,}949$ | 0,316 | 0,949 | **−0,632** |
| teacher | $\sqrt{0{,}72} = 0{,}849$ | 0,707 | 0,707 | **0** |

*nurse* pende verso *she*, *engineer* verso *he*, *teacher* è neutro. È la logica dei test di associazione di Caliskan et al. (2017) sui coseni.

(b) Un **danno allocativo** (Crawford, 2017; Blodgett et al., 2020): se il sistema misura quanto un curriculum è "vicino" a *engineer*, i documenti con nomi o parole associati a *she* riceverebbero punteggi più bassi a parità di competenze, e le candidate verrebbero penalizzate nell'accesso a un'opportunità (il colloquio, il lavoro). È l'esempio del libro (p. 146) della ricerca di programmatori o medici. Verificato nella cella 26.

</details>

#### Esercizio 12 (scheda L11): valutare gli embedding

Un piccolo insieme inventato di giudizi umani di similarità, nello stile di SimLex-999 (similarità, non relatedness), con i coseni di un modello: cup/mug 9,1 e 0,71; plane/car 5,8 e 0,55; coffee/cup 4,5 e 0,62; doctor/nurse 6,0 e 0,48; cat/carpet 1,2 e 0,10. (a) Ordina le cinque coppie per giudizio umano e per coseno del modello e calcola la correlazione di rango di Spearman $\rho = 1 - 6\sum d^2/(n(n^2-1))$. (b) Quale coppia il modello valuta troppo alta rispetto alle persone? Perché embedding appresi dalle co-occorrenze potrebbero farlo? (c) Perché questo tipo di valutazione intrinseca non basta, e qual è per il libro la valutazione più importante?

<details><summary>Soluzione</summary>

(a)

| coppia | rango umano | rango modello | d | d² |
| --- | --- | --- | --- | --- |
| cup, mug | 1 | 1 | 0 | 0 |
| plane, car | 3 | 3 | 0 | 0 |
| coffee, cup | 4 | 2 | 2 | 4 |
| doctor, nurse | 2 | 4 | −2 | 4 |
| cat, carpet | 5 | 5 | 0 | 0 |

$\sum d^2 = 8$, $n = 5$: $\rho = 1 - \frac{6\cdot8}{5\cdot24} = 1 - \frac{48}{120} = $ **0,60**.

(b) **coffee, cup**: secondo per il modello, quarto per le persone. Le due parole non sono simili (una bevanda e un recipiente) ma sono fortemente **collegate**: compaiono insieme e in contesti dello stesso argomento. Embedding appresi dalle co-occorrenze, soprattutto con finestre ampie, mescolano similarità e relatedness, mentre SimLex-999 chiede solo la similarità.

(c) La valutazione intrinseca misura l'accordo con giudizi su parole **isolate, senza contesto**, su pochi dati e su una nozione di similarità che dipende dal dataset (WordSim-353 premia la relatedness, SimLex-999 la penalizza): un buon punteggio non garantisce vettori utili per un compito. La valutazione più importante per il libro è quella **estrinseca**: usare i vettori in un compito di NLP e vedere se le prestazioni migliorano rispetto a un altro modello. Verificato nella cella 26.

</details>

#### Esercizio aggiuntivo A: completare il passo della scheda 30

Nel passo di SGD della scheda 30 (apricot = [0,5; 1; −0,5], jam = [1; 0,5; 0], matrix = [−0,5; 0,5; 1], Tolstoy = [0; −1; 0,5], $\eta = 0{,}5$) la slide mostra i nuovi apricot e jam. (a) Calcola i nuovi vettori di matrix e Tolstoy. (b) Calcola i prodotti scalari del **nuovo** apricot con i **vecchi** jam, matrix e Tolstoy: quanta parte dello spostamento della scheda 31 è dovuta al solo aggiornamento del target?

<details><summary>Soluzione</summary>

(a) $\sigma(\mathbf{matrix}\cdot\mathbf{apricot}) = \sigma(-0{,}25) = 0{,}438$: gradiente $0{,}438\cdot[0{,}5; 1; -0{,}5] = [0{,}219; 0{,}438; -0{,}219]$; nuovo matrix $= [-0{,}5; 0{,}5; 1] - 0{,}5[0{,}219; 0{,}438; -0{,}219] = $ **[−0,609; 0,281; 1,109]**. $\sigma(-1{,}25) = 0{,}223$: gradiente $[0{,}111; 0{,}223; -0{,}111]$; nuovo Tolstoy $= $ **[−0,056; −1,111; 0,556]**. Entrambi si spostano nella direzione opposta ad apricot.

(b) Nuovo apricot = [0,744; 1,069; −0,775]. Con jam vecchio: $0{,}744 + 0{,}535 + 0 = $ **1,28**; con matrix vecchio: $-0{,}372 + 0{,}535 - 0{,}775 = $ **−0,61**; con Tolstoy vecchio: $0 - 1{,}069 - 0{,}387 = $ **−1,46**. I prodotti finali sono 1,52, −1,01, −1,66: circa metà dello spostamento (da 1,00 a 1,28 su 1,00 a 1,52; da −0,25 a −0,61 su −0,25 a −1,01) viene dall'aggiornamento del target, il resto da quello dei contesti. Verificato con numpy.

</details>

#### Esercizio aggiuntivo B: quanti n-grammi in fasttext

Con le lunghezze di n-gramma usate in pratica, da 3 a 6, quanti n-grammi ha *where*? Scrivili, e di' quanti vettori vengono sommati per ottenerne l'embedding. Quanti ne avrebbe una parola di $m$ lettere?

<details><summary>Soluzione</summary>

<where> ha 7 simboli. Una stringa di 7 simboli ha $7-n+1$ n-grammi di lunghezza $n$: 5 trigrammi (<wh, whe, her, ere, re>), 4 tetragrammi (<whe, wher, here, ere>), 3 di lunghezza 5 (<wher, where, here>), 2 di lunghezza 6 (<where, where>): **14 n-grammi**. Più il vettore della parola intera <where>: **15 vettori** sommati. Nota che il 5-gramma `where` (senza confini) è diverso dalla parola `<where>`, e che `here` compare come 4-gramma: il vettore di *where* condivide un pezzo con quello di *here*. In generale, per $m$ lettere: $\sum_{n=3}^{6}(m+3-n) = 4m - 6$ n-grammi (con $m \ge 4$); per $m = 5$: 14. Verificato con python.

</details>

#### Esercizio aggiuntivo C: l'effetto di α

Due eventi con $P(a) = 0{,}99$ e $P(b) = 0{,}01$. Calcola $P_\alpha(b)$ per $\alpha$ = 1, 0,75, 0,5 e 0. Che cosa succede ai due estremi, e perché word2vec non usa né $\alpha = 1$ né $\alpha = 0$?

<details><summary>Soluzione</summary>

$P_\alpha(b) = \frac{0{,}01^\alpha}{0{,}99^\alpha + 0{,}01^\alpha}$. $\alpha = 1$: **0,01** (la distribuzione originale). $\alpha = 0{,}75$: $0{,}0316/1{,}0241 = $ **0,031**. $\alpha = 0{,}5$: $0{,}1/(0{,}995+0{,}1) = $ **0,091**. $\alpha = 0$: $1/(1+1) = $ **0,5**, la distribuzione uniforme. Con $\alpha = 1$ le parole di rumore sarebbero quasi solo parole funzionali; con $\alpha = 0$ sarebbero quasi solo parole rarissime (che in un vocabolario vero sono la grande maggioranza dei tipi), negativi facili e poco istruttivi. $\alpha = 0{,}75$ è un compromesso trovato sperimentalmente. Verificato con python.

</details>

### Domande tipo orale

<details><summary>Perché si preferiscono embedding corti e densi ai vettori sparsi della lezione precedente?</summary>

Traccia: (1) sparsi: $|V|$ dimensioni (50.000), una per parola, quasi tutti zeri, dimensioni interpretabili; densi: $d$ = 50-1000, valori reali anche negativi, dimensioni senza interpretazione; (2) il libro: i densi funzionano meglio in ogni compito, ragioni non del tutto capite; (3) meno parametri per i classificatori che li usano (300 contro 50.000 pesi), meno overfitting; (4) sinonimia: car e automobile sono colonne scollegate nello sparso, vettori vicini nel denso; (5) i densi si imparano (word2vec), gli sparsi si contano.

</details>

<details><summary>Spiega l'idea di word2vec e il ruolo della self-supervision.</summary>

Traccia: (1) invece di contare le co-occorrenze, si addestra un classificatore binario: c compare vicino a w?; (2) il compito è un pretesto: si tengono i pesi, che sono gli embedding; (3) self-supervision: il testo fornisce le risposte gold (le parole vicine sono positive), nessuna annotazione manuale, quindi si possono usare miliardi di parole; (4) idea nata nei language model neurali (Bengio 2003, Collobert 2011); (5) due semplificazioni: compito binario invece di predire la parola tra |V|, regressione logistica invece di rete con strati nascosti; (6) embedding statici.

</details>

<details><summary>Come calcola skip-gram la probabilità che c sia un contesto di w? E per una finestra intera?</summary>

Traccia: (1) similarità ≈ prodotto scalare $\mathbf c\cdot\mathbf w$; (2) il prodotto va da $-\infty$ a $+\infty$, la sigmoide lo porta in (0, 1): $P(+\mid w,c) = \sigma(\mathbf c\cdot\mathbf w)$; (3) $P(-\mid w,c) = 1-P(+) = \sigma(-\mathbf c\cdot\mathbf w)$; (4) finestra: ipotesi di indipendenza, prodotto delle sigmoidi, somma dei log; (5) esempio: apricot·jam = 1, $\sigma(1) = 0{,}73$; apricot·matrix = −0,25, 0,44; (6) nessun bias, solo il prodotto scalare.

</details>

<details><summary>Perché skip-gram ha due embedding per parola? Quale si usa alla fine?</summary>

Traccia: (1) servono un vettore per la parola come target ($W$, input embedding) e uno come contesto o rumore ($C$, output embedding); (2) parametri $\theta$: $2|V|$ vettori di dimensione $d$ (30 milioni con 50.000 × 300); (3) parallelo con la matrice parola-contesto: $W$ righe, $C$ colonne; (4) un motivo: con un solo vettore $\mathbf w\cdot\mathbf w$ sarebbe sempre alto, ogni parola sarebbe un buon contesto di sé stessa; (5) alla fine si usa $\mathbf w_i$ oppure $\mathbf w_i + \mathbf c_i$.

</details>

<details><summary>Che cos'è il negative sampling? Come si scelgono le parole di rumore e perché con α = 0,75?</summary>

Traccia: (1) per ogni coppia positiva (dalla finestra) si generano $k$ coppie negative con parole casuali del lessico diverse dal target; più negativi che positivi; (2) evita di confrontare con tutte le |V| parole (softmax); (3) estrazione con $P_\alpha(w) = \text{count}(w)^\alpha/\sum\text{count}^\alpha$, $\alpha = 0{,}75$; (4) effetto: le parole rare guadagnano probabilità (0,01 → 0,03 nell'esempio a due eventi), le frequenti ne perdono; (5) con $P$ pura il rumore sarebbe quasi solo the, of; embedding migliori sperimentalmente; (6) stessa pesatura della PPMI-α della L10.

</details>

<details><summary>Scrivi la loss di skip-gram con negative sampling e spiega i due termini.</summary>

Traccia: (1) $L = -[\log P(+\mid w,c_{pos}) + \sum_i\log P(-\mid w,c_{neg_i})]$, negative log likelihood con indipendenza; (2) forma finale $-[\log\sigma(\mathbf c_{pos}\cdot\mathbf w) + \sum_i\log\sigma(-\mathbf c_{neg_i}\cdot\mathbf w)]$; (3) primo termine: prodotto alto col contesto vero; secondo: prodotti bassi con il rumore; (4) è la cross-entropy binaria della regressione logistica su 1 positivo e $k$ negativi; (5) valori di riferimento: $(k+1)\ln2$ con prodotti nulli, 0 per un classificatore perfetto; le due curve si incrociano a 0 in $\ln2$.

</details>

<details><summary>Ricava i gradienti di SGNS e interpretali.</summary>

Traccia: (1) lemma $\frac{d}{dz}\log\sigma(z) = 1-\sigma(z)$; (2) $\partial L/\partial\mathbf c_{pos} = [\sigma(\mathbf c_{pos}\cdot\mathbf w)-1]\mathbf w$; (3) $\partial L/\partial\mathbf c_{neg_i} = \sigma(\mathbf c_{neg_i}\cdot\mathbf w)\mathbf w$ usando $1-\sigma(-z) = \sigma(z)$; (4) $\partial L/\partial\mathbf w$ = somma dei due tipi, ciascuno per il proprio vettore di contesto; (5) forma della regressione logistica: (previsto − vero) × input; (6) il passo avvicina $\mathbf c_{pos}$ e $\mathbf w$, allontana i $\mathbf c_{neg}$; tanto più quanto il classificatore sbaglia.

</details>

<details><summary>Descrivi un passo di SGD per skip-gram, con l'esempio di apricot.</summary>

Traccia: (1) aggiornamenti: ogni vettore meno $\eta$ per il suo gradiente, tutti calcolati con i valori al tempo $t$; (2) un passo tocca solo $k+2$ righe (target, contesto, $k$ rumori); (3) esempio: apricot, jam, matrix, Tolstoy, $\eta = 0{,}5$: prodotti da 1,00/−0,25/−1,25 a 1,52/−1,01/−1,66, loss da 1,14 a 0,68; (4) nuovo apricot [0,744; 1,069; −0,775]; (5) ciclo: inizializzazione casuale di $W$ e $C$, molte passate sul corpus; (6) parole con contesti simili vengono spinte verso gli stessi vettori: l'ipotesi distribuzionale.

</details>

<details><summary>Confronta skip-gram, CBOW, fasttext e GloVe.</summary>

Traccia: (1) skip-gram: target → contesto, una previsione per parola di contesto; default, buono per parole rare; (2) CBOW: contesto (media dei vettori, ordine ignorato) → target; più veloce, un po' meglio per le parole frequenti; (3) fasttext: skip-gram su parola + n-grammi di caratteri (3-6) con confini; parole sconosciute, morfologia ricca; (4) GloVe: rapporti di probabilità dalla matrice di co-occorrenza globale; (5) tutti statici: un vettore per parola, mouse ha un solo vettore; (6) Levy e Goldberg: SGNS fattorizza implicitamente una matrice PMI.

</details>

<details><summary>In che senso word2vec e i metodi basati sui conteggi sono vicini?</summary>

Traccia: (1) stesso testo, stessa finestra, stessa ipotesi distribuzionale; cambia il metodo (contare e pesare contro predire con SGD); (2) Levy e Goldberg (2014): SGNS ottimizza implicitamente una funzione di una matrice di conteggi pesata con PMI (all'ottimo $\mathbf w\cdot\mathbf c = \text{PMI} - \log k$); (3) $\alpha = 0{,}75$ è comune ai due mondi: Levy et al. (2015) l'hanno portato alla PPMI; (4) GloVe usa esplicitamente i conteggi globali; (5) in entrambi i casi si confrontano le parole con il coseno.

</details>

<details><summary>Che effetto ha la dimensione della finestra sugli embedding?</summary>

Traccia: (1) tipicamente da 1 a 10 parole per lato; (2) finestre corte: rappresentazioni più sintattiche, vicini simili con la stessa parte del discorso; (3) finestre lunghe: vicini collegati per argomento, non simili; (4) esempio di Hogwarts: ±2 Sunnydale, Evernight (altre scuole); ±5 Dumbledore, Malfoy, half-blood; (5) è la distinzione similarità/relatedness della L10; (6) la scelta dipende dallo scopo e si fa spesso su un devset.

</details>

<details><summary>Come si risolve un'analogia con gli embedding? Quali sono i limiti?</summary>

Traccia: (1) modello del parallelogramma (Rumelhart e Abrahamson, 1973): apple:tree::grape:vine; (2) $\hat b^* = \text{argmin}_x\,\text{distance}(\mathbf x, \mathbf b - \mathbf a + \mathbf a^*)$; (3) king − man + woman ≈ queen, Paris − France + Italy ≈ Rome, offset comparativo-superlativo; (4) cautele: il più vicino è spesso un input o una sua variante (potato, potatoes invece di brown), vanno esclusi; (5) funziona per parole frequenti, distanze piccole, certe relazioni (capitali, flessione); (6) troppo semplice come modello dell'analogia umana (Peterson et al., 2020).

</details>

<details><summary>Come si usano gli embedding per studiare il cambiamento di significato?</summary>

Traccia: (1) uno spazio di embedding per decennio, da corpora storici (Google n-grams, COHA); (2) si confrontano posizione e vicini della stessa parola nel tempo (Hamilton et al., 2016); (3) gay: da cheerful, frolicsome a homosexual; broadcast: da seminare a trasmettere (radio, television); awful: da full of awe a terrible (peggiorazione); (4) gli spazi vanno allineati, perché due training diversi hanno coordinate non comparabili; (5) gli stessi embedding storici misurano anche i bias del passato (Garg et al., 2018).

</details>

<details><summary>Quali bias riproducono gli embedding? Distingui danno allocativo e rappresentazionale.</summary>

Traccia: (1) gli embedding riproducono gli stereotipi latenti nel testo: man:computer programmer::woman:homemaker, father:doctor::mother:nurse (Bolukbasi et al., 2016); (2) amplificazione: più marcati che nel testo e nelle statistiche sul lavoro; (3) IAT e Caliskan et al. (2017): coseni di GloVe al posto delle latenze, nomi afroamericani più vicini a parole spiacevoli; (4) danno allocativo: risorse distribuite in modo ingiusto (ricerca di candidati che penalizza nomi femminili); danno rappresentazionale: un gruppo sminuito o ignorato (sentiment da embedding); (5) il debiasing riduce ma non elimina.

</details>

<details><summary>Come si valutano gli embedding?</summary>

Traccia: (1) valutazione estrinseca, la più importante: usare i vettori in un compito e misurare il miglioramento; (2) intrinseca: correlazione (di rango, Spearman) fra coseni e giudizi umani; (3) WordSim-353: 353 coppie di nomi, 0-10, plane/car 5,77, più relatedness; SimLex-999: solo similarità (cup/mug sì, cup/coffee no); TOEFL: 80 domande sui sinonimi (levied → imposed); (4) limite: parole senza contesto; esistono SCWS e WiC con contesto, e il compito di analogia; (5) variabilità fra training: più embedding su campioni bootstrap.

</details>
