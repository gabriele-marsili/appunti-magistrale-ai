# L6 · Regressione logistica

*Logistic Regression* · 02/10/2026 · Claudio Gallicchio · lettura: J&M cap. 4, §4.1-4.6 (Naive Bayes: Appendice B)

[Versione interattiva sul sito](https://gabriele-marsili.github.io/appunti-magistrale-ai/anno-2/hlt/sito/#L6) · [Indice della dispensa](README.md)

Prima lezione sulla classificazione (J&M §4.1-4.6, Naive Bayes dall'Appendice B). Che cos'è la **text classification** (sentiment, spam, language id, attribuzione d'autore; anche il language modeling è una classificazione), i quattro componenti di un classificatore probabilistico e la differenza tra **generativo** (Naive Bayes, addestrato contando con add-one) e **discriminativo**. Poi la **regressione logistica**: somma pesata delle feature, **sigmoide**, logit, soglia 0,5 e confine lineare, con l'esempio della recensione a sei feature ($P(+) = 0{,}70$). La **cross-entropy loss** come negative log likelihood, e la **discesa del gradiente**: gradiente $(\hat y - y)x_j$, SGD, learning rate, un passo a mano, mini-batch in forma matriciale. È lo schema (feature, funzione, loss, ottimizzatore) che resterà identico per reti neurali e LLM.

## Indice

- [Apertura](#apertura)
- [Classificazione del testo](#classificazione-del-testo)
- [Dalle feature alla probabilità](#dalle-feature-alla-probabilita)
- [La loss cross-entropy](#la-loss-cross-entropy)
- [Discesa del gradiente](#discesa-del-gradiente)
- [Notebook](#notebook)
- [Studio ed esercizi](#studio-ed-esercizi)

## Apertura

<a id="p-1"></a>
**Slide 1 · Regressione logistica** — Lezione 6 (Gallicchio, 2 ottobre 2026): classificazione del testo, Naive Bayes, regressione logistica con la sigmoide, la loss cross-entropy e la discesa del gradiente.

<a id="p-2"></a>

### Slide 2 · Indice della lezione

Quattro parti, che coprono la prima metà del capitolo 4 del libro:

- **Text classification** (§4.1 e Appendice B): che cos'è classificare un testo, le tre strade (regole, prompting, apprendimento supervisionato), i quattro componenti di un classificatore probabilistico e il **Naive Bayes** come esempio di classificatore *generativo*.
- **Dalle feature alla probabilità** (§4.2-4.3): somma pesata $z = \mathbf{w}\cdot\mathbf{x}+b$, **sigmoide**, logit, soglia 0,5; l'esempio della recensione con sei feature; scaling delle feature e forma matriciale.
- **La loss cross-entropy** (§4.4-4.5): da dove viene (massima verosimiglianza condizionata) e come si comporta.
- **Discesa del gradiente** (§4.6): gradiente $(\hat y - y)x_j$, SGD, learning rate, un passo fatto a mano, mini-batch.

Il filo: la L4 e la L5 stimavano probabilità *contando*; da qui in poi le probabilità escono da una funzione con **pesi appresi minimizzando una loss**, lo stesso schema che userà ogni rete neurale e ogni LLM.

<a id="p-3"></a>

### Slide 3 · Riferimento: J&M capitolo 4, §4.1-4.6

Lettura principale: Jurafsky e Martin, *Speech and Language Processing*, 3a ed. (draft del 19 agosto 2026), **capitolo 4, Logistic Regression and Text Classification**, sezioni:

- **4.1** Machine learning and classification;
- **4.2** The sigmoid function;
- **4.3** Classification with logistic regression (esempio della recensione, period disambiguation, scaling, forma matriciale);
- **4.4** Learning in logistic regression;
- **4.5** The cross-entropy loss function;
- **4.6** Gradient descent (gradiente, SGD, esempio a mano, mini-batch).

**Naive Bayes** non è nel PDF del capitolo: sta nell'**Appendice B**, sul sito del libro (il QR code porta a web.stanford.edu/~jurafsky/slp3/). Il resto del capitolo (softmax e regressione multinomiale, valutazione, cross-validation, significatività, §4.7-4.16) è la prossima lezione. La derivazione completa del gradiente è nella §4.15 (*Advanced*), riassunta qui nella [scheda 45](L06-regressione-logistica.md#p-45).

## Classificazione del testo

<a id="p-4"></a>
**Slide 4 · Text classification** — Prima parte: assegnare un'etichetta a un testo, e un primo classificatore che si addestra contando, il Naive Bayes.

<a id="p-5"></a>

### Slide 5 · Classificazione del testo: sentiment e spam

**Text categorization** (o text classification): assegnare a un testo intero un'etichetta presa da un insieme fisso di categorie. Due esempi canonici:

- **Sentiment analysis**: l'orientamento positivo o negativo di chi scrive verso un oggetto. Le recensioni (film, libri, prodotti) esprimono un giudizio sul prodotto; un editoriale o un testo politico verso un'azione o un candidato. Serve dal marketing alla politica.
- **Spam detection**: assegnare una email a una di due classi, *spam* o *not-spam*.

Sono entrambi problemi **binari** (due classi), il caso trattato in tutta questa lezione; il caso a molte classi (softmax) è la prossima. Per il sentiment esistono anche versioni a più valori (positivo, negativo, neutro; oppure da 1 a 5 stelle).

<a id="p-6"></a>

### Slide 6 · Altri compiti: language id, autore, language modeling

- **Language id**: in che lingua è scritto un testo; spesso il primo passo di una pipeline (per esempio per scegliere il tokenizzatore o filtrare un corpus di pretraining).
- **Authorship attribution**: chi ha scritto il testo; serve all'analisi umanistica (testi di autore incerto) e forense.
- **Language modeling**: ogni parola del vocabolario è una classe, e predire la parola successiva significa **classificare il contesto visto finora** in una classe per parola.

L'ultimo punto (evidenziato nella slide) è il motivo per cui la classificazione è centrale nel corso: un LLM è, a ogni passo, un classificatore con $|V|$ classi che restituisce una **distribuzione** sul prossimo token ([scheda 5 della L1](L01-introduzione-al-corso.md#p-5), [scheda 41 della L5](L05-smoothing-ed-entropia.md#p-41)). Con BPE da 50.000 token le classi sono 50.000. La versione a molte classi della regressione logistica (softmax) è esattamente lo strato di uscita di un LLM.

<a id="p-7"></a>

### Slide 7 · Le parole come indizi

Per il sentiment alcune parole sono indizi fortissimi: *awesome*, *love* per il positivo, *awful*, *ridiculously* per il negativo (in verde e rosso nelle due righe di recensione della slide: *...awesome caramel sauce and sweet toasty almonds. I love this place!* contro *...awful pizza and ridiculously overpriced...*).

- **Features**: le proprietà utili dell'input che il classificatore estrae e usa per decidere. Possono essere conteggi di parole, indicatori binari (c'è un punto esclamativo?), lunghezze, qualunque cosa calcolabile dal testo.
- **Lexicons**: liste scritte a mano di parole positive e negative; una fonte comune di feature per il sentiment (per esempio "numero di parole del lessico positivo nel documento", che sarà la feature $x_1$ della [scheda 26](L06-regressione-logistica.md#p-26)).

Il classificatore non sa nulla del significato di *awesome*: impara dai dati **quanto pesa** ciascuna feature a favore di una classe.

<a id="p-8"></a>

### Slide 8 · Classificazione: input, feature, classi

Definizione generale: prendere un input $x$, **estrarre delle feature** utili e assegnare $x$ a una classe di un insieme **discreto** $Y$.

- Sentiment: $Y = \{\text{positive}, \text{negative}\}$, codificato come $\{1, 0\}$.
- Language id: $Y = \{\text{Abkhaz}, \text{Ainu}, \text{Albanian}, \text{Amharic}, \dots, \text{Zulu}, \text{Zuñi}\}$: tante classi quante le lingue.

**Input**: una singola **osservazione** $x$; per la text classification una recensione o un altro testo. **Output**: una classe predetta da $Y = \{y_1, y_2, \dots, y_M\}$ (il libro avverte che a volte l'insieme delle classi si chiama $C$, come nel Naive Bayes delle schede 14-18).

Le classi sono *discrete* e senza ordine: è questo che distingue la classificazione dalla regressione (output reale). Il nome "regressione logistica" inganna: è un classificatore, che però *calcola* un numero reale, la probabilità della classe positiva.

<a id="p-9"></a>

### Slide 9 · Tre modi di classificare

- **Regole scritte a mano**: "se *love* compare in $x$ e non è preceduto da *don't*, classifica come positivo". Sono **fragili**: le situazioni e i dati cambiano nel tempo, e le feature interagiscono in modi complessi (la negazione qui ne è un esempio: *not bad*, *I don't think I've ever loved a film more*), quindi è difficile scrivere regole che funzionino in molti casi.
- **Prompting di un LLM**: chiedere l'etichetta a un modello linguistico; ne parleremo più avanti nel corso. Il libro ne indica i limiti: i modelli possono allucinare e non sanno spiegare perché hanno scelto la classe.
- **Apprendimento supervisionato**: un training set etichettato e un algoritmo di apprendimento. È il modo più comune.

Le liste di parole scritte a mano non spariscono: restano utili **come feature** di un classificatore appreso, che decide da solo quanto fidarsi di ciascuna.

<a id="p-10"></a>

### Slide 10 · Apprendimento supervisionato

Il **training set etichettato** è un insieme di $m$ coppie input-output:

$$\{(x^{(1)}, y^{(1)}), (x^{(2)}, y^{(2)}), \dots, (x^{(m)}, y^{(m)})\}$$

Ogni $x^{(i)}$ ha la sua etichetta corretta $y^{(i)}$, il **segnale di supervisione**. Convenzione di notazione da fissare subito: l'**apice tra parentesi** $(i)$ indica l'esempio, il **pedice** $j$ la feature; $x^{(i)}_j$ è la feature $j$ dell'esempio $i$.

- **Obiettivo**: imparare un classificatore che mappa un input *nuovo* nella sua classe corretta, trovando le feature utili (come *awesome* o *awful*). Conta la generalizzazione, misurata su dati mai visti ([training, dev e test della L4](L04-modelli-linguistici-n-gram.md#p-27)).
- **Classificatori probabilistici**, come la regressione logistica: oltre alla classe danno la sua **probabilità**. Utile a valle: si può cambiare soglia, combinare sistemi, non prendere decisioni discrete troppo presto.

Differenza con gli n-gram: anche lì c'era un training set, ma senza etichette (il "segnale" era la parola successiva, già nel testo).

<a id="p-11"></a>

### Slide 11 · I quattro componenti (1-2)

Ogni classificatore probabilistico appreso ha quattro pezzi; la lezione li costruisce nell'ordine.

1. **Rappresentazione a feature**: ogni osservazione $x^{(i)}$ diventa un vettore $[x_1, x_2, \dots, x_n]$ (per la text classification: conteggi di parole, indicatori, lunghezza...). Il libro usa anche le notazioni $f_i$, $f_i(x)$.
2. **Funzione di classificazione**: calcola $P(y = y_i \mid x)$ per ogni classe. Per due classi la **sigmoide** (oggi), per molte la **softmax** (prossima lezione).

Questi due pezzi definiscono il *modello*: dato un vettore di feature e dei pesi, producono una probabilità. Gli altri due (scheda seguente) servono a trovare i pesi.

<a id="p-12"></a>

### Slide 12 · I quattro componenti (3-4)

3. **Funzione obiettivo**: ciò che l'apprendimento ottimizza, di solito una **loss** sugli esempi di training; qui la **cross-entropy loss** ([schede 37-39](L06-regressione-logistica.md#p-37)).
4. **Algoritmo di ottimizzazione**: un metodo per ottimizzare l'obiettivo; qui la **stochastic gradient descent** ([scheda 46](L06-regressione-logistica.md#p-46)).

Le due fasi:

- **Training**: si imparano i pesi $\mathbf{w}$ e il bias $b$ con SGD e cross-entropy.
- **Test**: dato un esempio nuovo si calcola $P(y\mid x)$ e si restituisce l'etichetta più probabile.

Lo schema "modello + loss + ottimizzatore" è identico per una rete neurale o un transformer: cambiano solo la funzione di classificazione (più strati) e il numero di parametri.

<a id="p-13"></a>

### Slide 13 · Classificatori generativi e discriminativi

Due modi di trovare la classe più probabile $c$ per un documento $d$:

- **Generativo (Naive Bayes)**: impara un modello di ciascuna classe: il **prior** $P(c)$, quanto è frequente la classe, e la **likelihood** $P(d\mid c)$, come la classe *genera* i suoi documenti. Poi inverte con Bayes per ottenere $P(c\mid d)$. In principio potrebbe generare documenti finti di ogni classe.
- **Discriminativo (regressione logistica)**: nessun modello di come nascono i documenti. Impara direttamente $P(c\mid d)$: un peso per ogni feature di $d$, per quanto aiuta a **distinguere** le classi.

Un'immagine utile: per distinguere cani da gatti, il generativo impara com'è fatto un cane e com'è fatto un gatto; il discriminativo impara solo che cosa li separa (il collare? le orecchie?). I sistemi discriminativi sono spesso più accurati e più usati, soprattutto con molti dati e feature correlate, che il Naive Bayes conta due volte.

<a id="p-14"></a>

### Slide 14 · Naive Bayes: il classificatore

La classe scelta è quella con probabilità massima dato il documento:

$$\hat c = \operatorname*{argmax}_{c\in C} P(c\mid d)$$

Con la **regola di Bayes** $P(c\mid d) = P(d\mid c)\,P(c)/P(d)$, e poiché $P(d)$ è **uguale per tutte le classi** (non dipende da $c$), si può togliere senza cambiare l'argmax:

$$\hat c = \operatorname*{argmax}_{c\in C} \underbrace{P(d\mid c)}_{\text{likelihood}}\;\underbrace{P(c)}_{\text{prior}}$$

Nella slide le due parti sono indicate da graffe: *likelihood* sopra $P(d\mid c)$, *prior* sopra $P(c)$. Attenzione: senza $P(d)$ i due numeri non sono più probabilità che sommano a 1 sulle classi, ma il loro **rapporto** è lo stesso; per avere $P(c\mid d)$ basta normalizzare (dividere ciascuno per la somma).

<a id="p-15"></a>

### Slide 15 · Naive Bayes: ipotesi e spazio log

$P(d\mid c)$ per un documento intero è impossibile da stimare direttamente. Due ipotesi semplificatrici:

- **Bag of words**: la posizione delle parole non conta, il documento è un multinsieme di parole.
- **Ipotesi naive di Bayes**: le parole sono **indipendenti data la classe**, quindi la likelihood è un prodotto.

$$c_{NB} = \operatorname*{argmax}_{c\in C} P(c)\prod_{i\in \text{positions}} P(w_i\mid c)$$

dove *positions* sono tutte le posizioni del documento di test. In **spazio log**, come per i modelli linguistici ([scheda 22 della L4](L04-modelli-linguistici-n-gram.md#p-22)), il prodotto diventa una somma e si evita l'underflow:

$$c_{NB} = \operatorname*{argmax}_{c\in C} \log P(c) + \sum_{i\in\text{positions}} \log P(w_i\mid c)$$

È una **funzione lineare delle feature**: raggruppando le occorrenze, il punteggio è $\log P(c) + \sum_{w} \text{count}(w,d)\log P(w\mid c)$, cioè una somma pesata dei conteggi. Per questo il Naive Bayes, come la regressione logistica, è un **classificatore lineare**.

> **Da saper fare: Naive Bayes come somma pesata**
>
> Con due classi si decide "+" se $\log P(+\mid d) - \log P(-\mid d) &gt; 0$, cioè
>
> $$\underbrace{\log\frac{P(+)}{P(-)}}_{b} + \sum_w \text{count}(w,d)\,\underbrace{\log\frac{P(w\mid +)}{P(w\mid -)}}_{w_w} &gt; 0$$
>
> È esattamente la forma $\mathbf{w}\cdot\mathbf{x}+b &gt; 0$ della regressione logistica ([scheda 25](L06-regressione-logistica.md#p-25)) con $x_w$ = conteggio della parola. La differenza sta in **come** si ottengono i pesi: il Naive Bayes li calcola contando, classe per classe; la regressione logistica li ottimizza tutti insieme per separare le classi. L'esempio numerico è nell'esercizio aggiuntivo B.

<a id="p-16"></a>

### Slide 16 · Naive Bayes: il training è contare

Le stime sono frequenze relative, cioè **massima verosimiglianza** come per gli n-gram ([scheda 13 della L4](L04-modelli-linguistici-n-gram.md#p-13)):

- **Prior**: $\hat P(c) = N_c / N_{doc}$, la frazione dei documenti di training nella classe $c$.
- **Likelihood**: si concatenano tutti i documenti della classe $c$ in un unico testo e si prende la frequenza di $w_i$ in quel testo:

$$\hat P(w_i\mid c) = \frac{\text{count}(w_i, c)}{\sum_{w\in V}\text{count}(w, c)}$$

Il denominatore è il **numero totale di token** della classe $c$. $V$ è il vocabolario: i tipi di parola di **tutte** le classi insieme (non solo di $c$), perché a test una parola vista solo nell'altra classe deve avere una probabilità anche in questa. Non c'è ottimizzazione: un solo passaggio sui dati.

<a id="p-17"></a>

### Slide 17 · Zeri e add-one smoothing

Stesso problema della [L5](L05-smoothing-ed-entropia.md#p-5): se *fantastic* non compare mai nelle recensioni positive di training,

$$\hat P(\text{"fantastic"}\mid\text{positive}) = \frac{\text{count}(\text{"fantastic"},\text{positive})}{\sum_{w\in V}\text{count}(w,\text{positive})} = 0$$

e l'intero prodotto diventa 0, **qualunque siano le altre parole**: una recensione piena di elogi più *fantastic* avrebbe probabilità nulla di essere positiva.

Rimedio: **add-one (Laplace)**, come nella [scheda 10 della L5](L05-smoothing-ed-entropia.md#p-10):

$$\hat P(w_i\mid c) = \frac{\text{count}(w_i,c)+1}{\sum_{w\in V}(\text{count}(w,c)+1)} = \frac{\text{count}(w_i,c)+1}{\left(\sum_{w\in V}\text{count}(w,c)\right)+|V|}$$

Le parole di test **mai viste in training in nessuna classe** si eliminano semplicemente dal documento (la slide stessa lo chiama un approccio brutale: si butta via un pezzo del documento, ma una parola mai vista non porta alcun indizio su quale classe preferire, e tenerla con l'add-one darebbe solo un fattore $1/(N_c+|V|)$ che dipende dal numero di token $N_c$ della classe, non dalla parola).

Conclusione della slide: con tutte le parole come feature, il Naive Bayes è **un modello linguistico unigram per classe**, smussato con Laplace.

<a id="p-18"></a>

### Slide 18 · Naive Bayes: un esempio svolto

Training (tabella della slide): tre recensioni negative (*just plain boring*; *entirely predictable and lacks energy*; *no surprises and very few laughs*) e due positive (*very powerful*; *the most fun film of the summer*). Test: *predictable with no fun*.

- Prior: $P(-) = 3/5$, $P(+) = 2/5$.
- *with* non compare mai nel training: si elimina.
- $|V| = 20$ tipi; 14 token nelle negative, 9 nelle positive: denominatori $14+20 = 34$ e $9+20 = 29$.
- Likelihood add-one: *predictable* $(1+1)/34$ e $(0+1)/29$; *no* $(1+1)/34$ e $(0+1)/29$; *fun* $(0+1)/34$ e $(1+1)/29$.

$$P(-)P(S\mid -) = \frac35\cdot\frac{2\cdot 2\cdot 1}{34^3} = 6{,}1\times 10^{-5}\qquad P(+)P(S\mid +) = \frac25\cdot\frac{1\cdot 1\cdot 2}{29^3} = 3{,}2\times 10^{-5}$$

La recensione è classificata **negativa**. Verificato in Python: $6{,}106\times10^{-5}$ e $3{,}280\times10^{-5}$ (il secondo valore, come nel libro, è troncato: arrotondato sarebbe $3{,}3\times10^{-5}$; la decisione non cambia). Normalizzando, $P(-\mid S) = 6{,}106/(6{,}106+3{,}280) = 0{,}65$.

> **Da saper fare: Rifare il conto a mano**
>
> Passi da saper eseguire all'esame: (1) prior come frazione di *documenti*; (2) contare i *token* per classe e i *tipi* del vocabolario comune ($|V|$); (3) eliminare le parole di test fuori vocabolario; (4) per ogni parola rimasta $(\text{count}+1)/(N_c+|V|)$; (5) moltiplicare per il prior (o sommare i log). Qui: $34^3 = 39.304$ e $29^3 = 24.389$, quindi $0{,}6\cdot 4/39.304$ contro $0{,}4\cdot 2/24.389$. Errore tipico: usare $|V|$ della sola classe, o dimenticare che *no* e *predictable* compaiono una volta sola tra le negative.

## Dalle feature alla probabilità

<a id="p-19"></a>
**Slide 19 · Regressione logistica** — Seconda parte: dalla somma pesata delle feature a una probabilità, con la sigmoide.

<a id="p-20"></a>

### Slide 20 · Pesi, bias e somma pesata

La regressione logistica moltiplica ogni feature $x_i$ per il suo **peso** $w_i$, somma e aggiunge il **bias** $b$:

$$z = \left(\sum_{i=1}^{n} w_i x_i\right) + b$$

$z$ è la **somma pesata degli indizi** a favore della classe positiva. In notazione vettoriale (vettori in grassetto) è un **prodotto scalare**:

$$z = \mathbf{w}\cdot\mathbf{x} + b$$

Esempio minimo: due feature, $\mathbf{w} = [2, -1]$, $b = 0{,}5$, $\mathbf{x} = [3, 2]$: $z = 6 - 2 + 0{,}5 = 4{,}5$. È tutto il "modello" in senso stretto: un vettore di $n$ pesi più un numero.

<a id="p-21"></a>

### Slide 21 · Che cosa significano pesi e bias

- **Pesi**: numeri reali appresi dal training set, uno per feature. Un peso **positivo** è un indizio per la classe positiva, uno **negativo** per quella negativa; il modulo dice quanto conta. Ci aspettiamo per *awesome* un peso alto e positivo, per *abysmal* uno molto negativo.
- **Bias** (o **intercept**): un altro numero reale sommato agli input pesati. È il valore di $z$ quando tutte le feature sono 0: sposta la decisione a favore di una classe a priori, un po' come il prior del Naive Bayes.
- **Intervallo di $z$**: niente costringe $z$ tra 0 e 1. I pesi sono reali, quindi $z$ va da $-\infty$ a $+\infty$ e può essere negativo: non è una probabilità.

Serve quindi una funzione che schiacci $\mathbb{R}$ in $(0, 1)$: la sigmoide, scheda seguente.

<a id="p-22"></a>

### Slide 22 · La funzione sigmoide

$$\sigma(z) = \frac{1}{1+e^{-z}} = \frac{1}{1+\exp(-z)}$$

Il grafico della slide (curva blu, $z$ da $-8$ a $8$, $\sigma$ da 0 a 1) mostra la forma a S: piatta vicino a 0 per $z &lt; -4$, ripida intorno all'origine, piatta vicino a 1 per $z &gt; 4$, passa per $(0;\ 0{,}5)$.

- Si chiama **sigmoide** per la forma a S, o **funzione logistica**, che dà il nome alla regressione logistica.
- Manda qualunque reale in $(0, 1)$, estremi esclusi: proprio ciò che serve per una probabilità.
- È quasi **lineare intorno a 0** (pendenza $1/4$) e **schiaccia** i valori estremi verso 0 o 1.
- È **derivabile**, il che servirà per l'apprendimento.

Valori da ricordare (verificati): $\sigma(0) = 0{,}5$; $\sigma(\ln 3) = 0{,}75$; $\sigma(2) = 0{,}881$; $\sigma(4) = 0{,}982$; $\sigma(-2) = 0{,}119$.

> **Da saper fare: La derivata della sigmoide**
>
> $\sigma'(z) = \sigma(z)\,(1-\sigma(z))$. Dimostrazione: $\sigma(z) = (1+e^{-z})^{-1}$, quindi $\sigma'(z) = e^{-z}/(1+e^{-z})^2 = \dfrac{1}{1+e^{-z}}\cdot\dfrac{e^{-z}}{1+e^{-z}} = \sigma(z)\,(1-\sigma(z))$, perché $\dfrac{e^{-z}}{1+e^{-z}} = 1-\sigma(z)$. Il massimo è $1/4$ in $z = 0$; in $z = 0{,}83$ vale $0{,}697\cdot 0{,}303 = 0{,}211$. È il pezzo chiave per derivare il gradiente della [scheda 45](L06-regressione-logistica.md#p-45).

<a id="p-23"></a>

### Slide 23 · Due classi, due probabilità

Applicata alla somma pesata, la sigmoide dà un numero tra 0 e 1; perché sia una distribuzione, le due classi devono sommare a 1:

$$P(y=1) = \sigma(\mathbf{w}\cdot\mathbf{x}+b) = \frac{1}{1+\exp(-(\mathbf{w}\cdot\mathbf{x}+b))}$$$$P(y=0) = 1-\sigma(\mathbf{w}\cdot\mathbf{x}+b) = \frac{\exp(-(\mathbf{w}\cdot\mathbf{x}+b))}{1+\exp(-(\mathbf{w}\cdot\mathbf{x}+b))}$$

La sigmoide ha la proprietà di **simmetria**

$$1-\sigma(x) = \sigma(-x)$$

quindi $P(y=0) = \sigma(-z)$: la classe negativa usa lo stesso meccanismo con il segno di $z$ cambiato. Prova: $1-\dfrac{1}{1+e^{-x}} = \dfrac{e^{-x}}{1+e^{-x}}$; moltiplicando sopra e sotto per $e^{x}$ si ottiene $\dfrac{1}{e^{x}+1} = \sigma(-x)$. Numericamente: $\sigma(2)+\sigma(-2) = 0{,}881+0{,}119 = 1$.

<a id="p-24"></a>

### Slide 24 · Il logit

Il punteggio $z$ si chiama **logit**, perché la **funzione logit** è l'inversa della sigmoide:

$$\text{logit}(p) = \sigma^{-1}(p) = \ln\frac{p}{1-p}$$

$p/(1-p)$ sono gli **odds** (quote): con $p = 0{,}8$ gli odds sono 4 a 1 e il logit è $\ln 4 = 1{,}39$. Leggere $z$ come **log odds** dà un significato ai pesi: aumentare la feature $x_j$ di 1 somma $w_j$ ai log odds, cioè moltiplica gli odds per $e^{w_j}$.

I due grafici della slide sono la stessa curva vista nei due versi: a sinistra la sigmoide (blu), da $z$ a $p$, per $z\in[-6, 6]$; a destra il logit (rosso), da $p$ a $z$, che esplode verso $-\infty$ per $p\to 0$ e verso $+\infty$ per $p\to 1$. Entrambi passano per il punto marcato $z = 0$, $p = 0{,}5$: logit zero significa odds 1 a 1. Il logit della slide è troncato a $\pm 5$ circa sull'asse verticale.

<a id="p-25"></a>

### Slide 25 · ŷ e la soglia di decisione

Notazione: $\hat y = \sigma(z) = P(y=1\mid x)$, letto "y hat": la probabilità della classe **positiva** stimata dal modello; quella negativa è $1-\hat y$. Il vero $y$ vale 0 o 1, $\hat y$ è un numero in $(0,1)$.

Regola di decisione, con **decision boundary** 0,5:

$$\text{decision}(x) = \begin{cases}1 &amp; \text{se } P(y=1\mid x) &gt; 0{,}5\\ 0 &amp; \text{altrimenti}\end{cases}$$

Poiché $\sigma$ è crescente e $\sigma(0) = 0{,}5$, la condizione $\hat y &gt; 0{,}5$ equivale a $z &gt; 0$, cioè $\mathbf{w}\cdot\mathbf{x}+b &gt; 0$. Il confine tra le classi nello spazio delle feature è quindi l'**iperpiano** $\mathbf{w}\cdot\mathbf{x}+b = 0$: la regressione logistica è un **classificatore lineare**. La sigmoide non cambia la decisione, serve a dare una probabilità (e a rendere la loss derivabile).

> **Da saper fare: Domanda tipica: perché è lineare?**
>
> Risposta in tre passi: (1) $\sigma$ è monotona crescente con $\sigma(0) = 1/2$; (2) quindi $\sigma(z) &gt; 1/2 \iff z &gt; 0$; (3) $z = \mathbf{w}\cdot\mathbf{x}+b$ è lineare in $\mathbf{x}$, quindi il confine è un iperpiano (una retta con due feature). Con due feature, $\mathbf{w} = [2, -1]$, $b = 0{,}5$, il confine è $2x_1 - x_2 + 0{,}5 = 0$, cioè $x_2 = 2x_1+0{,}5$. Una soglia diversa da 0,5 (per esempio 0,9) sposta l'iperpiano in parallelo ($z &gt; \text{logit}(0{,}9) = 2{,}2$), non lo piega.

<a id="p-26"></a>

### Slide 26 · Sentiment: sei feature

Il classificatore di sentiment del libro (§4.3.1) usa sei feature, conteggi e indicatori binari (tabella della slide, con i valori sul documento della scheda seguente):

| Var | Definizione | Valore |
| --- | --- | --- |
| $x_1$ | count(parole del lessico positivo $\in$ doc) | 3 |
| $x_2$ | count(parole del lessico negativo $\in$ doc) | 2 |
| $x_3$ | 1 se "no" $\in$ doc, 0 altrimenti | 1 |
| $x_4$ | count(pronomi di 1a e 2a persona $\in$ doc) | 3 |
| $x_5$ | 1 se "!" $\in$ doc, 0 altrimenti | 0 |
| $x_6$ | ln(numero di parole e punteggiatura del doc) | $\ln(66) = 4{,}19$ |

La lunghezza entra come **logaritmo**: un conteggio grezzo (66, ma anche 600) avrebbe una scala molto diversa dalle altre feature; il log la comprime ([scheda 32](L06-regressione-logistica.md#p-32)). Le feature sono scelte per intuizione: i lessici catturano il sentiment, *no* e "!" segnalano negazione ed enfasi, i pronomi un tono personale.

<a id="p-27"></a>

### Slide 27 · Un piccolo documento di test

La figura (Fig. 4.2 del libro) è una recensione con le parole che attivano le feature cerchiate e collegate da linee tratteggiate al valore della feature:

*It's hokey. There are virtually no surprises, and the writing is second-rate. So why was it so enjoyable? For one thing, the cast is great. Another nice touch is the music. I was overcome with the urge to get off the couch and start dancing. It sucked me in, and it'll do the same to you.*

- $x_1 = 3$: *enjoyable*, *great*, *nice* (in giallo);
- $x_2 = 2$: *hokey*, *second-rate* (in arancione);
- $x_3 = 1$: *no* (in grigio);
- $x_4 = 3$: *I*, *me*, *you* (in viola);
- $x_5 = 0$: nessun punto esclamativo;
- $x_6 = \ln 66 = 4{,}19$: 66 parole e segni di punteggiatura.

Quindi $\mathbf{x} = [3, 2, 1, 3, 0, 4{,}19]$. Verifica del 66: contando parole e punteggiatura con *It's* e *it'll* come un token ciascuno si ottengono esattamente 66 token (68 separando i clitici *'s* e *'ll*): il valore dipende dalla tokenizzazione, come visto nella [L2](L02-parole-e-token.md#p-1).

<a id="p-28"></a>

### Slide 28 · La probabilità di una recensione positiva

Pesi (dati, non ancora appresi) $\mathbf{w} = [2{,}5;\ -5{,}0;\ -1{,}2;\ 0{,}5;\ 2{,}0;\ 0{,}7]$ e $b = 0{,}1$. Il conto della slide:

|  |  |
| --- | --- |
| $2{,}5\times 3$ | $7{,}50$ |
| $-5{,}0\times 2$ | $-10{,}00$ |
| $-1{,}2\times 1$ | $-1{,}20$ |
| $0{,}5\times 3$ | $1{,}50$ |
| $2{,}0\times 0$ | $0{,}00$ |
| $0{,}7\times 4{,}19$ | $2{,}93$ |
| $+\,b$ | $0{,}10$ |
| $z$ | $0{,}83$ |

$\sigma(0{,}83) = 0{,}70 = P(+\mid x)$, quindi $P(-\mid x) = 0{,}30$ e, poiché $0{,}70 &gt; 0{,}5$, la recensione è classificata **positiva**. Verificato: $z = 0{,}8328$ (con $\ln 66 = 4{,}1897$), $\sigma(z) = 0{,}6969$.

Lettura dei pesi: $w_1 = 2{,}5$, le parole positive sono indizio per la classe positiva; $w_2 = -5{,}0$, le negative pesano contro, il doppio delle positive. Infatti due parole negative ($-10$) battono tre positive ($+7{,}5$), e a salvare la recensione sono pronomi, lunghezza e bias.

> **Da saper fare: Varianti da fare a mano**
>
> Ogni modifica di una feature sposta $z$ di (variazione)$\times$(peso): con un "!" ($x_5 = 1$) $z = 2{,}83$, $P = 0{,}944$; senza *no* ($x_3 = 0$) $z = 2{,}03$, $P = 0{,}884$; con una parola negativa in più $z = -4{,}17$, $P = 0{,}015$ e la decisione si ribalta. È l'esercizio 4 della scheda.

<a id="p-29"></a>

### Slide 29 · Altri compiti, altre feature

**Period disambiguation**: un punto chiude la frase (EOS) o fa parte di una parola (abbreviazione)? È il problema della segmentazione in frasi della [scheda 32 della L3](L03-elaborazione-del-testo.md#p-32), ora come classificazione binaria. Feature della parola $w_i$ che porta il punto:

$$x_1 = \begin{cases}1 &amp; \text{se } \textit{Case}(w_i) = \text{Lower}\\0&amp;\text{altrimenti}\end{cases}\quad x_2 = \begin{cases}1 &amp; \text{se } w_i \in \text{AcronymDict}\\0&amp;\text{altrimenti}\end{cases}$$$$x_3 = \begin{cases}1 &amp; \text{se } w_i = \text{St.}\ \&amp;\ \textit{Case}(w_{i-1}) = \text{Upper}\\0&amp;\text{altrimenti}\end{cases}$$

- $x_1$ (minuscola) probabilmente con peso positivo verso EOS, $x_2$ (abbreviazione nota, *Prof.*) con peso negativo.
- **Feature interactions**: combinazioni di feature più primitive. $x_3$ dice: *St.* dopo una parola maiuscola è probabilmente *Street* in un nome di via (*Main St.*), non fine frase.
- **Feature templates**: specifiche astratte che generano feature in automatico, per esempio "ogni bigram che precede un punto nel training". Lo spazio è enorme ma *sparso*; il libro dice che ogni feature si identifica con un hash della sua descrizione (*bigram(American breakfast)* → numero $i$).

<a id="p-30"></a>

### Slide 30 · Representation learning

Stesse feature della scheda precedente; la novità è il riquadro in basso. Progettare feature a mano richiede **molto lavoro umano**: guardare il training set con intuizioni linguistiche, provare, fare analisi degli errori, aggiungere interazioni. Per questo i sistemi NLP recenti **imparano le feature automaticamente dall'input**: è il **representation learning**.

Il passaggio è il cuore del corso: negli embedding e nelle reti neurali (capitoli 5 e 6 del libro) la rappresentazione $\mathbf{x}$ non è più una lista di conteggi scelti da noi, ma un vettore appreso; e uno strato finale fa ancora esattamente quello che fa la regressione logistica, una somma pesata seguita da sigmoide o softmax.

<a id="p-31"></a>

### Slide 31 · Scaling delle feature: z-score

Quando le feature hanno scale molto diverse conviene riportarle a intervalli confrontabili. La **standardizzazione** (**z-score**) centra ogni feature a media 0 e deviazione standard 1:

$$\mu_i = \frac1m\sum_{j=1}^{m}x_i^{(j)}\qquad \sigma_i = \sqrt{\frac1m\sum_{j=1}^{m}\left(x_i^{(j)}-\mu_i\right)^2}\qquad x_i' = \frac{x_i-\mu_i}{\sigma_i}$$

Qui $\sigma_i$ è la deviazione standard della feature $i$ sugli $m$ esempi, **non la sigmoide** (il libro lo avverte esplicitamente). Si divide per $m$, non per $m-1$: deviazione standard "di popolazione".

Esempio (esercizio 7): valori 2, 4, 4, 6, 9 → $\mu = 5$, $\sigma = \sqrt{28/5} = 2{,}37$, z-score $-1{,}27;\ -0{,}42;\ -0{,}42;\ 0{,}42;\ 1{,}69$. Media e deviazione si calcolano **sul solo training set** e si riusano tali e quali su dev e test, altrimenti informazioni del test entrano nel modello.

<a id="p-32"></a>

### Slide 32 · Normalizzazione e scala logaritmica

- **Normalizzazione** min-max: porta ogni feature in $[0, 1]$, $x_i' = \dfrac{x_i-\min(x_i)}{\max(x_i)-\min(x_i)}$. Con 2, 4, 4, 6, 9: $0;\ 0{,}29;\ 0{,}29;\ 0{,}57;\ 1$.
- **Scala log**: per conteggi di parole, di bigram o qualunque cosa segua una distribuzione **Zipfiana** (pochi valori enormi, moltissimi piccoli). È la scelta fatta per $x_6$, il log della lunghezza: 66 e 132 parole diventano 4,19 e 4,88, una differenza moderata.

Perché scalare: (1) feature con intervalli confrontabili sono più facili da **confrontare** (i pesi diventano paragonabili); (2) la **discesa del gradiente converge più in fretta**, perché con scale molto diverse lo stesso learning rate è troppo grande per una feature e troppo piccolo per un'altra. Il notebook lo mostra: con $\eta = 3$ le feature grezze non convergono (costo 2,14), quelle standardizzate sì (0,468).

<a id="p-33"></a>

### Slide 33 · Molti esempi insieme: forma matriciale

Invece di un ciclo su $m$ esempi di test ($\hat y^{(i)} = \sigma(\mathbf{w}\cdot\mathbf{x}^{(i)}+b)$ uno alla volta), si impilano i vettori di feature come **righe** di una matrice $\mathbf{X}$ di forma $m\times f$:

$$\mathbf{X} = \begin{bmatrix}x^{(1)}_1 &amp; x^{(1)}_2 &amp; \dots &amp; x^{(1)}_f\\ x^{(2)}_1 &amp; x^{(2)}_2 &amp; \dots &amp; x^{(2)}_f\\ x^{(3)}_1 &amp; x^{(3)}_2 &amp; \dots &amp; x^{(3)}_f\\ \dots\end{bmatrix}\qquad \underset{(m\times 1)}{\hat{\mathbf{y}}} = \sigma(\underset{(m\times f)}{\mathbf{X}}\ \underset{(f\times 1)}{\mathbf{w}} + \underset{(m\times 1)}{\mathbf{b}})$$

$\mathbf{b}$ è il bias ripetuto $m$ volte (in numpy basta lo scalare, per broadcasting); $\sigma$ si applica **elemento per elemento**. La riga $i$ di $\mathbf{X}\mathbf{w}$ è proprio $\mathbf{x}^{(i)}\cdot\mathbf{w}$.

Esempio (esercizio 8): $\mathbf{X} = [[3,2],[1,4],[0,0]]$, $\mathbf{w} = [1,-1]$, $b = 0{,}5$: $\mathbf{X}\mathbf{w}+b = [1{,}5;\ -2{,}5;\ 0{,}5]$, $\hat{\mathbf{y}} = [0{,}82;\ 0{,}08;\ 0{,}62]$, decisioni $[1, 0, 1]$. Su hardware moderno (GPU) una moltiplicazione matriciale è molto più veloce del ciclo: conta sui dataset grandi.

<a id="p-34"></a>
**Slide 34 · Pausa** — Pausa di 10 minuti; dopo la pausa: come si imparano i pesi.

## La loss cross-entropy

<a id="p-35"></a>
**Slide 35 · La loss cross-entropy** — Terza parte: quanto è lontana la previsione dall'etichetta vera.

<a id="p-36"></a>

### Slide 36 · Imparare i pesi

Obiettivo: trovare $\mathbf{w}$ e $b$ tali che, per ogni esempio di training, $\hat y$ sia il più vicino possibile all'etichetta vera $y$: se $y = 1$ vogliamo $\hat y$ vicino a 1, se $y = 0$ vicino a 0. Servono due cose (i componenti 3 e 4 della [scheda 12](L06-regressione-logistica.md#p-12)):

- **Loss function** (o **cost function**): una *distanza* tra l'output del sistema $\hat y$ e l'output corretto (gold) $y$. Qui la **cross-entropy loss**.
- **Algoritmo di ottimizzazione**: aggiorna iterativamente i pesi per minimizzare la loss. Qui la **stochastic gradient descent**.

Si parla di distanza (da minimizzare) e non di somiglianza (da massimizzare) per convenzione: ottimizzare è sempre "scendere".

<a id="p-37"></a>

### Slide 37 · Massima verosimiglianza condizionata

Principio: scegliere $\mathbf{w}, b$ che **massimizzano la log probabilità delle etichette vere dati gli input** (**conditional maximum likelihood estimation**). È la MLE della [L4](L04-modelli-linguistici-n-gram.md#p-13), ma *condizionata* su $x$: non si modella $x$, solo $y$ dato $x$ (discriminativo).

- **Bernoulli**: due soli esiti, quindi $p(y\mid x) = \hat y^{\,y}(1-\hat y)^{1-y}$. Il trucco degli esponenti: se $y = 1$ resta $\hat y$, se $y = 0$ resta $1-\hat y$.
- **Log likelihood**: il log è monotono, quindi massimizzare il log massimizza la probabilità; e trasforma il prodotto in somma: $\log p(y\mid x) = y\log\hat y + (1-y)\log(1-\hat y)$.
- **Negative log likelihood**: per avere qualcosa da *minimizzare* si cambia segno:

$$L_{CE}(\hat y, y) = -\log p(y\mid x) = -\left[y\log\hat y + (1-y)\log(1-\hat y)\right]$$

Questa è la **negative log likelihood loss**, generalmente chiamata **cross-entropy loss**. Il log è naturale (convenzione del libro quando la base non è indicata).

<a id="p-38"></a>

### Slide 38 · La cross-entropy loss

Sostituendo $\hat y = \sigma(\mathbf{w}\cdot\mathbf{x}+b)$:

$$L_{CE}(\hat y, y) = -\left[y\log\sigma(\mathbf{w}\cdot\mathbf{x}+b) + (1-y)\log\left(1-\sigma(\mathbf{w}\cdot\mathbf{x}+b)\right)\right]$$

Il grafico mostra la loss in funzione di $\hat y = P(y=1\mid x)$: la curva blu continua $-\log\hat y$ (caso $y = 1$) scende da $+\infty$ a 0 andando verso $\hat y = 1$; la curva rossa tratteggiata $-\log(1-\hat y)$ (caso $y = 0$) sale da 0 a $+\infty$. Si incrociano a $\hat y = 0{,}5$ con loss $\ln 2 = 0{,}69$. I due punti marcati a $\hat y = 0{,}70$ valgono 0,36 (blu) e 1,2 (rosso): la recensione della scheda seguente.

- La loss va da **0** ($-\log 1$, nessuna perdita) a **infinito** ($-\log 0$): una previsione sicura e sbagliata costa moltissimo.
- Le probabilità della risposta giusta e di quella sbagliata sommano a 1: alzare una abbassa l'altra.
- È la **cross-entropy** della [L5](L05-smoothing-ed-entropia.md#p-38) tra la distribuzione vera $(y, 1-y)$, tutta concentrata sull'etichetta corretta, e quella stimata $(\hat y, 1-\hat y)$: $H(p,q) = -\sum_k p_k\log q_k$ con $p$ "one-hot".

> **Approfondimento: Lo stesso numero degli LLM**
>
> Nella L5 la cross-entropy era in bit ($\log_2$) e la perplexity era $2^H$. Qui si usa il log naturale (nat); la sostanza non cambia, cambia l'unità ($1$ nat $= 1/\ln 2 \approx 1{,}44$ bit). La loss di un LLM è la stessa cosa con la softmax al posto della sigmoide: $-\log$ della probabilità data al token corretto, mediata sui token; e $e^{\text{loss media}}$ è la perplexity ([scheda 41 della L5](L05-smoothing-ed-entropia.md#p-41)).

<a id="p-39"></a>

### Slide 39 · La loss sulla recensione di esempio

La recensione della [scheda 28](L06-regressione-logistica.md#p-28) ha $\hat y = 0{,}70$.

- **Se è positiva** ($y = 1$): resta solo il primo termine, $-\log\hat y = -\log(0{,}70) = 0{,}36$. Il modello ha dato 0,70 alla classe giusta: loss piccola.
- **Se è negativa** ($y = 0$): resta solo il secondo, $-\log(1-\hat y) = -\log(0{,}30) = 1{,}2$. Magari il recensore proseguiva: *But bottom line, the movie is terrible! I beg you not to see it!* Il modello è confuso: loss grande.

La loss per l'etichetta corretta è più piccola di quella per l'etichetta sbagliata, come deve essere. Verificato: $-\ln 0{,}70 = 0{,}357$ e $-\ln 0{,}30 = 1{,}204$; con il $\hat y$ esatto $0{,}6969$ il secondo valore è $1{,}19$ (il notebook stampa entrambi).

Nota: il caso "negativa" non sarebbe più la stessa recensione, perché la frase aggiunta cambierebbe le feature (un "!" in più, *terrible* nel lessico negativo): il libro tiene $\hat y$ fisso solo per illustrare la loss.

## Discesa del gradiente

<a id="p-40"></a>
**Slide 40 · Discesa del gradiente** — Quarta parte: trovare i pesi che minimizzano la loss.

<a id="p-41"></a>

### Slide 41 · L'obiettivo: minimizzare la loss media

$$\hat\theta = \operatorname*{argmin}_{\theta}\ \frac1m\sum_{i=1}^{m} L_{CE}\!\left(f(x^{(i)};\theta),\ y^{(i)}\right)$$

- **Parametri**: $\theta = \{\mathbf{w}, b\}$ (in machine learning $\theta$ indica sempre i parametri appresi). Si scrive $\hat y^{(i)} = f(x^{(i)};\theta)$ per rendere esplicito che la previsione dipende da $\theta$, e si **media** la loss sugli $m$ esempi di training.
- **Gradient descent**: trovare la direzione in cui la loss **sale più ripida** e muoversi nel verso opposto. L'immagine del libro: scendere in fretta a fondo valle guardandosi intorno e camminando dove il terreno scende di più.

Minimizzare la loss media equivale a massimizzare la log-verosimiglianza del training set (somma dei log $p(y^{(i)}\mid x^{(i)})$, se gli esempi sono indipendenti): è la massima verosimiglianza condizionata della [scheda 37](L06-regressione-logistica.md#p-37) su tutti gli esempi.

<a id="p-42"></a>

### Slide 42 · Convessità

La loss della regressione logistica è **convessa**: ha al più un minimo, senza minimi locali in cui restare bloccati, quindi la discesa del gradiente da qualunque punto di partenza lo trova (con un learning rate adeguato). Le reti neurali a più strati hanno invece una loss **non convessa**, con **minimi locali**.

I due grafici: a sinistra (blu) una parabola, "convex: one minimum", con un solo punto di minimo; a destra (rosso) una curva con due valli, "non-convex: local minima", con il *global minimum* a sinistra (più basso) e un *local minimum* a destra separato da una collina: partendo da destra la discesa si fermerebbe nella valle sbagliata.

> **Approfondimento: "Al più" un minimo: dati separabili**
>
> Il libro scrive "at most one minimum" a ragion veduta: se i dati di training sono **linearmente separabili** il minimo non esiste. Moltiplicando $\mathbf{w}$ e $b$ per una costante sempre più grande, ogni $\hat y$ si avvicina all'etichetta giusta e la loss tende a 0 senza mai raggiungerlo: i pesi crescono all'infinito. Con il bag of words, molte feature e pochi documenti la separabilità è frequente. Il rimedio è la **regolarizzazione** (un termine che penalizza pesi grandi), trattata nel resto del capitolo 4.

<a id="p-43"></a>

### Slide 43 · Discesa del gradiente in una dimensione

$$w^{t+1} = w^{t} - \eta\,\frac{d}{dw}L(f(x;w), y)$$

La figura (Fig. 4.3 del libro): curva blu della loss in funzione di un unico peso $w$, con minimo in $w^{\min}$ (*goal*). Si parte da $w^1 = 0$ (qui l'apice è il numero del passo); la retta tangente verde tratteggiata ha **pendenza negativa**; la freccia rossa "one step of gradient descent" porta il punto più a destra e più in basso sulla curva.

- Pendenza negativa → si muove $w$ nel verso **positivo**, a destra; pendenza positiva → a sinistra. Il segno meno nella formula fa esattamente questo.
- Il passo è la pendenza moltiplicata per il **learning rate** $\eta$: un $\eta$ più alto sposta $w$ di più a ogni passo.

Vicino al minimo la pendenza si riduce, quindi anche il passo diventa più piccolo da solo: con $\eta$ fisso si rallenta in prossimità della meta.

<a id="p-44"></a>

### Slide 44 · Il gradiente

Con molti parametri la "pendenza" è un vettore, il **gradiente**: una **derivata parziale** per ogni peso più una per il bias, ciascuna dice quanto cambierebbe la loss con un piccolo cambiamento di quel parametro.

$$\nabla L(f(x;\theta),y) = \begin{bmatrix}\frac{\partial}{\partial w_1}L(f(x;\theta),y)\\ \vdots\\ \frac{\partial}{\partial w_n}L(f(x;\theta),y)\\ \frac{\partial}{\partial b}L(f(x;\theta),y)\end{bmatrix}\qquad \theta^{t+1} = \theta^{t} - \eta\,\nabla L(f(x;\theta), y)$$

Il gradiente punta dove la loss **cresce di più**; ci si muove nel verso opposto, di $\eta$ volte il gradiente. La figura (Fig. 4.4 del libro) è una superficie a scodella blu, $\text{Cost}(w,b)$, su due assi $w$ e $b$; un punto rosso sulla superficie, la sua proiezione tratteggiata sul piano e una freccia rossa nel piano $(w,b)$ che indica la direzione in cui ci si muove: opposta al gradiente, verso il fondo della scodella.

<a id="p-45"></a>

### Slide 45 · Il gradiente per la regressione logistica

La derivata della loss per **una** osservazione:

$$\frac{\partial L_{CE}(\hat y,y)}{\partial w_j} = \left[\sigma(\mathbf{w}\cdot\mathbf{x}+b)-y\right]x_j = (\hat y - y)\,x_j\qquad \frac{\partial L_{CE}(\hat y,y)}{\partial b} = \sigma(\mathbf{w}\cdot\mathbf{x}+b)-y = \hat y - y$$

Un valore molto intuitivo: **l'errore della previsione per l'input**. Conseguenze:

- se la previsione è giusta ($\hat y\approx y$) il gradiente è quasi nullo: niente da correggere;
- se $y = 1$ e $\hat y$ è basso, $\hat y - y &lt; 0$: il passo $-\eta(\hat y-y)x_j$ **aumenta** i pesi delle feature presenti ($x_j &gt; 0$);
- una feature assente ($x_j = 0$) non riceve aggiornamento; il bias si comporta come una feature sempre uguale a 1.

Il libro scrive anche la forma equivalente $-(y-\hat y)x_j$.

> **Da saper fare: Derivazione (libro §4.15)**
>
> Con $z = \mathbf{w}\cdot\mathbf{x}+b$ e $\hat y = \sigma(z)$, per la regola della catena $\dfrac{\partial L}{\partial w_j} = \dfrac{\partial L}{\partial\hat y}\cdot\dfrac{\partial\hat y}{\partial z}\cdot\dfrac{\partial z}{\partial w_j}$.
>
> 1. $\dfrac{\partial L}{\partial\hat y} = -\dfrac{y}{\hat y} + \dfrac{1-y}{1-\hat y} = \dfrac{\hat y - y}{\hat y(1-\hat y)}$;
> 2. $\dfrac{\partial\hat y}{\partial z} = \sigma(z)(1-\sigma(z)) = \hat y(1-\hat y)$ ([scheda 22](L06-regressione-logistica.md#p-22));
> 3. $\dfrac{\partial z}{\partial w_j} = x_j$ e $\dfrac{\partial z}{\partial b} = 1$.
>
> Il fattore $\hat y(1-\hat y)$ si semplifica e resta $(\hat y - y)x_j$. È la combinazione sigmoide + cross-entropy a dare un gradiente così pulito, che non si annulla quando la sigmoide è saturata su una risposta sbagliata. Il notebook (cella 21) lo controlla con le differenze finite: formula e gradiente numerico coincidono alla sesta cifra.

<a id="p-46"></a>

### Slide 46 · Stochastic gradient descent

L'algoritmo della slide (Fig. 4.5 del libro), in breve:

```
theta = 0                      # (o piccoli valori casuali)
ripeti finché non hai finito:
  per ogni (x(i), y(i)) in ordine casuale:
    1. (facoltativo) y_hat = f(x(i); theta), loss L(y_hat, y(i))
    2. g = gradiente di L rispetto a theta    # dove la loss sale
    3. theta = theta - eta * g                # vai dall'altra parte
restituisci theta
```

- **Online**: aggiorna dopo ogni esempio, senza aspettare di aver visto tutto il dataset. **Stocastica** perché sceglie un esempio a caso alla volta.
- Il calcolo della loss (passo 1) serve solo per monitorare: il gradiente $(\hat y-y)x_j$ non ne ha bisogno.
- **Inizializzazione**: pesi a 0 per la regressione logistica (la loss è convessa, il punto di partenza non conta); piccoli valori casuali per le reti neurali, dove pesi tutti uguali resterebbero uguali.
- **Stop**: alla convergenza (norma del gradiente sotto $\epsilon$) oppure quando la loss comincia a **salire su un held-out set**, segno di overfitting ([dev set della L4](L04-modelli-linguistici-n-gram.md#p-27)).

<a id="p-47"></a>

### Slide 47 · Il learning rate

Il **learning rate** $\eta$ è un **iperparametro**: lo sceglie il progettista (di solito provando sul dev set), non si impara dal training come $\mathbf{w}$ e $b$.

- **Troppo alto**: passi troppo lunghi, si scavalca il minimo.
- **Troppo basso**: passi troppo corti, ci vuole troppo.
- Comune partire alto e diminuire lentamente: $\eta_k$ all'iterazione $k$ (*learning rate schedule*).

I tre pannelli: stessa loss a parabola con minimo in $w = 2$ (pallino scuro), sei passi da $w = -0{,}5$. Con $\eta = 0{,}05$ (*too low*) i punti avanzano di poco e restano lontani dal minimo; con $\eta = 0{,}3$ (*about right*) arrivano quasi subito; con $\eta = 1{,}05$ (*too high*) rimbalzano da una parete all'altra salendo sempre più in alto.

Ho ricostruito i punti: corrispondono a $L(w) = (w-2)^2+0{,}5$, per cui $w^{t+1}-2 = (1-2\eta)(w^t-2)$. La distanza dal minimo si moltiplica per $0{,}9$ con $\eta = 0{,}05$ (−0,5; −0,25; 0,03; 0,27; 0,50; 0,70), per $0{,}4$ con $\eta = 0{,}3$ (−0,5; 1; 1,6; 1,84...), per $-1{,}1$ con $\eta = 1{,}05$ (−0,5; 4,75; −1,03; 5,33): oscilla e diverge. Qui si diverge appena $\eta &gt; 1$.

<a id="p-48"></a>

### Slide 48 · Un passo a mano: il setup

L'esempio del libro (§4.6.3), versione ridotta della recensione: una sola osservazione **positiva** ($y = 1$) con due feature, $\mathbf{x} = [x_1, x_2] = [3, 2]$:

- $x_1 = 3$: parole del lessico positivo;
- $x_2 = 2$: parole del lessico negativo.

Parametri iniziali $w_1 = w_2 = b = 0$, learning rate $\eta = 0{,}1$. Con tutti i pesi a zero $z = 0$ e $\hat y = \sigma(0) = 0{,}5$: il modello non sa nulla e dà 50 e 50. La loss iniziale è $-\ln 0{,}5 = 0{,}69$.

<a id="p-49"></a>

### Slide 49 · Un passo a mano: il gradiente

Tre parametri, quindi tre componenti:

$$\nabla_{w,b}L = \begin{bmatrix}(\sigma(\mathbf{w}\cdot\mathbf{x}+b)-y)x_1\\(\sigma(\mathbf{w}\cdot\mathbf{x}+b)-y)x_2\\ \sigma(\mathbf{w}\cdot\mathbf{x}+b)-y\end{bmatrix} = \begin{bmatrix}(\sigma(0)-1)x_1\\(\sigma(0)-1)x_2\\ \sigma(0)-1\end{bmatrix} = \begin{bmatrix}-0{,}5\,x_1\\-0{,}5\,x_2\\-0{,}5\end{bmatrix} = \begin{bmatrix}-1{,}5\\-1{,}0\\-0{,}5\end{bmatrix}$$

L'errore è $\hat y - y = 0{,}5 - 1 = -0{,}5$, moltiplicato per ciascun input. Tutte le componenti sono negative: **aumentare** $w_1$, $w_2$ e $b$ abbassa la loss. Notare che anche $w_2$, il peso delle parole *negative*, viene spinto in su: da un solo esempio positivo il modello non può sapere che le parole negative sono un indizio contrario, sa solo che erano presenti in un esempio positivo.

<a id="p-50"></a>

### Slide 50 · Un passo a mano: l'aggiornamento

$$\theta^1 = \begin{bmatrix}w_1\\w_2\\b\end{bmatrix} - \eta\begin{bmatrix}-1{,}5\\-1{,}0\\-0{,}5\end{bmatrix} = \begin{bmatrix}0{,}15\\0{,}1\\0{,}05\end{bmatrix}$$

Dopo un passo: $w_1 = 0{,}15$, $w_2 = 0{,}1$, $b = 0{,}05$. Ora $z = 0{,}15\cdot3 + 0{,}1\cdot2 + 0{,}05 = 0{,}70$ e $\hat y = \sigma(0{,}70) = 0{,}67$: la loss su questa recensione scende da 0,69 a 0,40 (verificato: $0{,}6931\to 0{,}4032$). Dopo altri esempi negativi con molte parole negative $w_2$ diventerebbe negativo: lo si vede nell'esercizio 10 ($w_2 = -0{,}25$ dopo un esempio negativo con $x_2 = 5$).

> **Da saper fare: Lo schema da applicare all'esame**
>
> (1) $z = \mathbf{w}\cdot\mathbf{x}+b$; (2) $\hat y = \sigma(z)$; (3) errore $e = \hat y - y$; (4) gradiente $[e\,x_1, \dots, e\,x_n, e]$; (5) $\theta \leftarrow \theta - \eta\cdot$ gradiente; (6) controllo: ricalcolare $\hat y$ e la loss, che sull'esempio usato deve scendere (per $\eta$ non troppo grande). Errore classico: sommare il gradiente invece di sottrarlo, o dimenticare il bias.

<a id="p-51"></a>

### Slide 51 · Stochastic, batch e mini-batch

- **Stochastic**: un esempio a caso alla volta. Ogni passo migliora quel singolo esempio, magari peggiorando gli altri: movimenti **molto irregolari** (*choppy*).
- **Batch**: il gradiente sull'intero dataset. Una stima **ottima della direzione**, ma ogni singolo passo costa un passaggio su tutti gli esempi.
- **Mini-batch**: un gruppo di $m$ esempi, per esempio 512 o 1024. Si vettorizza e si elabora in **parallelo**: efficiente su hardware moderno, e meno rumoroso della versione stocastica.

Sono la stessa cosa con $m$ diverso: **$m = 1$ è la SGD, $m$ = dimensione del dataset è il batch training**. Un'**epoca** è un passaggio su tutto il training: con $N$ esempi e mini-batch di $m$ si fanno $\lceil N/m\rceil$ aggiornamenti per epoca (1500 esempi: 1500 con $m=1$, 94 con $m=16$, 1 con $m=1500$, come nel notebook).

<a id="p-52"></a>

### Slide 52 · Costo e gradiente del mini-batch

Assumendo gli esempi **indipendenti**, la log probabilità delle etichette è la somma dei log, e il **costo** del mini-batch è la **loss media** dei suoi $m$ esempi:

$$\text{Cost}(\hat y, y) = \frac1m\sum_{i=1}^m L_{CE}(\hat y^{(i)}, y^{(i)}) = -\frac1m\sum_{i=1}^m\left[y^{(i)}\log\sigma(\mathbf{w}\cdot\mathbf{x}^{(i)}+b) + (1-y^{(i)})\log\left(1-\sigma(\mathbf{w}\cdot\mathbf{x}^{(i)}+b)\right)\right]$$

(la slide, come l'equazione 4.30 del libro, omette le parentesi quadre: la somma va intesa su entrambi i termini). Il gradiente è la **media dei gradienti individuali**:

$$\frac{\partial\,\text{Cost}}{\partial w_j} = \frac1m\sum_{i=1}^m\left[\sigma(\mathbf{w}\cdot\mathbf{x}^{(i)}+b) - y^{(i)}\right]x^{(i)}_j$$

In **forma matriciale**, con $\mathbf{X}$ di forma $m\times f$ e $\mathbf{y}$ di forma $m\times 1$ come nella [scheda 33](L06-regressione-logistica.md#p-33):

$$\frac{\partial\,\text{Cost}}{\partial\mathbf{w}} = \frac1m(\hat{\mathbf{y}}-\mathbf{y})^{\top}\mathbf{X} = \frac1m\left(\sigma(\mathbf{X}\mathbf{w}+\mathbf{b})-\mathbf{y}\right)^{\top}\mathbf{X}$$

Il risultato è un vettore di $f$ componenti (come riga; $\frac1m\mathbf{X}^\top(\hat{\mathbf{y}}-\mathbf{y})$ è la stessa cosa in colonna). Per il bias, non scritto nella slide: $\frac1m\sum_i(\hat y^{(i)}-y^{(i)})$, la media degli errori. Usare la media e non la somma rende il passo indipendente dalla dimensione del batch.

<a id="p-53"></a>

### Slide 53 · Riepilogo e prossima lezione

**Riepilogo**:

- text classification: sentiment, spam, language id, autore; anche il language modeling;
- apprendimento supervisionato: un training set etichettato e quattro componenti (feature, funzione di classificazione, loss, ottimizzatore);
- Naive Bayes è generativo, la regressione logistica discriminativa;
- regressione logistica: feature pesate, sigmoide, soglia di decisione 0,5;
- cross-entropy loss: la negative log likelihood dell'etichetta vera;
- discesa del gradiente: muoversi contro il gradiente, $(\hat y - y)x_j$; SGD e mini-batch.

**Prossima lezione**: **regressione logistica multinomiale** (softmax, più di due classi), valutazione, cross-validation, significatività statistica; capitolo 4, §4.7-4.16.

## Notebook

Commento al notebook del corso `HLT-L06-logistic-regression.ipynb` (il notebook è del docente e non è incluso).

Notebook di accompagnamento: rifà il Naive Bayes dell'Appendice B, la sigmoide, il classificatore di sentiment a sei feature, la cross-entropy, il passo di discesa del gradiente con un controllo numerico del gradiente; poi genera 2000 recensioni artificiali (con negazioni ed etichette rumorose), addestra la regressione logistica con mini-batch in `numpy` su sei feature e su tutte le parole, la confronta con il Naive Bayes, mostra il trucco `NOT_` per la negazione e studia learning rate, scaling e dimensione del mini-batch. Servono solo libreria standard, `numpy` e `matplotlib`. Ricalcola gli esercizi 2-5 e 7-12 della scheda.

L'ho eseguito con Python 3.11 (nbconvert): tutti gli output coincidono con quelli salvati, cifra per cifra (cambia solo il modo in cui le stampe sono spezzate). Ho controllato in particolare segno del gradiente, aggiornamento del bias, media contro somma, standardizzazione con statistiche del solo training, vocabolario del solo training (niente leakage), dtype e overflow: **non ho trovato bug**. Due note di robustezza (non errori nell'uso che ne fa il notebook) sono nei riquadri azzurri: la sigmoide con `math.exp` va in overflow per $z &lt; -709$, e la SGD con $\eta = 0{,}1$ su conteggi grezzi è inutilmente rumorosa.

### Notebook 1 · Naive Bayes sull'esempio dell'Appendice B

```python
NB_TRAIN = [("-", "just plain boring"),
            ("-", "entirely predictable and lacks energy"),
            ("-", "no surprises and very few laughs"),
            ("+", "very powerful"),
            ("+", "the most fun film of the summer")]

def train_nb(docs):
    classes = sorted(set(c for c, _ in docs))
    prior = {c: sum(1 for cc, _ in docs if cc == c) / len(docs) for c in classes}
    counts = {c: Counter(w for cc, d in docs if cc == c for w in d.split()) for c in classes}
    vocab = set(w for _, d in docs for w in d.split())
    return prior, counts, vocab

def nb_scores(model, doc):
    prior, counts, vocab = model
    scores = {}
    for c in prior:
        total = sum(counts[c].values())
        p = prior[c]
        for w in doc.split():
            if w in vocab:                       # unknown words are dropped
                p *= (counts[c][w] + 1) / (total + len(vocab))
        scores[c] = p
    return scores
```

Output:

```text
|V| = 20  words in the negative reviews: 14  in the positive ones: 9
predictable with no fun     P(-) P(S|-) = 6.11e-05   P(+) P(S|+) = 3.28e-05   ->  -
very boring and no fun      P(-) P(S|-) = 3.17e-07   P(+) P(S|+) = 7.8e-08   ->  -
unsmoothed, very boring and no fun: {'+': 0.0, '-': 0.0}
```

Implementazione diretta delle [schede 16-17](L06-regressione-logistica.md#p-16): prior come frazione di documenti, un `Counter` per classe (il testo concatenato della classe), vocabolario comune alle due classi, add-one con denominatore $N_c + |V|$, parole fuori vocabolario saltate. Riproduce l'esempio della [scheda 18](L06-regressione-logistica.md#p-18) ($6{,}11\cdot10^{-5}$ contro $3{,}28\cdot10^{-5}$; il markdown del notebook nota correttamente che il libro arrotonda per difetto a 3,2) e risolve l'esercizio 2 (*very boring and no fun*: negativa, $3{,}17\cdot10^{-7}$ contro $7{,}8\cdot10^{-8}$).

La cella 4 mostra perché serve lo smoothing: senza, *boring* non compare mai tra le positive e *fun* mai tra le negative, quindi **entrambi** i punteggi sono 0 e non si può decidere. Il calcolo usa prodotti di probabilità, non somme di log: va bene per frasi corte (anche sulle recensioni generate della sezione 6, fino a 45 token, il punteggio più piccolo è circa $10^{-79}$, lontano dal limite dei float intorno a $10^{-308}$), ma su documenti lunghi si sommano i log ([scheda 15](L06-regressione-logistica.md#p-15)).

### Notebook 2 · Sigmoide e logit

```python
def sigmoid(z):
    return 1 / (1 + math.exp(-z))

def logit(p):
    return math.log(p / (1 - p))
```

Output:

```text
sigma(0) = 0.5   sigma(ln 3) = 0.7500   sigma(-ln 3) = 0.2500
sigma(2) = 0.881   sigma(-2) = 0.119   sum = 0.9999999999999999
logit(0.8) = 1.39
logit(0.9) = 2.20
logit(0.99) = 4.60
```

Le due funzioni delle [schede 22-24](L06-regressione-logistica.md#p-22), con i valori dell'esercizio 3. La somma $\sigma(2)+\sigma(-2)$ stampata come 0,9999999999999999 è la proprietà $1-\sigma(z) = \sigma(-z)$ a meno dell'arrotondamento in virgola mobile. I logit mostrano la forma della sigmoide: per passare da $p = 0{,}5$ a $0{,}9$ basta $z = 2{,}2$, da $0{,}9$ a $0{,}99$ serve altri $2{,}4$.

> **Approfondimento: Una sigmoide che non va in overflow**
>
> Non è un errore nell'uso che ne fa il notebook (qui $|z|$ resta piccolo), ma va saputo: con `math.exp`, `sigmoid(-800)` solleva `OverflowError: math range error`, perché $e^{800}$ supera il massimo dei float. La versione numpy della sezione 7 (`1 / (1 + np.exp(-z))`) invece dà `inf`, un `RuntimeWarning` e il risultato corretto 0. Versione stabile per scalari, verificata:
>
> ```
> def sigmoid(z):
>     if z >= 0:
>         return 1 / (1 + math.exp(-z))
>     e = math.exp(z)          # z < 0: exp(z) non va in overflow
>     return e / (1 + e)
> ```
>
> Nelle librerie si usa `scipy.special.expit`, e la loss si calcola direttamente dai logit (*log-sum-exp*, come `BCEWithLogitsLoss` di PyTorch) senza passare per $\log\sigma$.

### Notebook 3 · La recensione del libro e le sue varianti

```python
BOOK_W = [2.5, -5.0, -1.2, 0.5, 2.0, 0.7]
BOOK_B = 0.1

def weighted_sum(w, x, b):
    return sum(wi * xi for wi, xi in zip(w, x)) + b

x = [3, 2, 1, 3, 0, math.log(66)]
z = weighted_sum(BOOK_W, x, BOOK_B)
# variants: x5 = 1, x3 = 0, x2 + 1
```

Output:

```text
x1 =  3.00   w1 =   2.5   w1 x1 =   7.50   positive lexicon words
x2 =  2.00   w2 =  -5.0   w2 x2 = -10.00   negative lexicon words
x3 =  1.00   w3 =  -1.2   w3 x3 =  -1.20   'no' in the review
x4 =  3.00   w4 =   0.5   w4 x4 =   1.50   1st and 2nd person pronouns
x5 =  0.00   w5 =   2.0   w5 x5 =   0.00   '!' in the review
x6 =  4.19   w6 =   0.7   w6 x6 =   2.93   ln(length)
z = 0.83   P(+ | x) = 0.70   P(- | x) = 0.30
with an exclamation mark   z =  2.83   P(+ | x) = 0.944
without the word no        z =  2.03   P(+ | x) = 0.884
one more negative word     z = -4.17   P(+ | x) = 0.015
```

Il conto della [scheda 28](L06-regressione-logistica.md#p-28), riga per riga, e le tre varianti dell'esercizio 4. Ogni variante sposta $z$ esattamente del peso della feature cambiata ($+2{,}0$, $+1{,}2$, $-5{,}0$): la linearità di $z$ rende l'effetto di una feature indipendente dalle altre, mentre l'effetto sulla probabilità non lo è (la sigmoide è più ripida vicino a 0). Il grafico mostra la sigmoide da $-8$ a $8$, la linea tratteggiata della soglia 0,5 e la recensione come punto rosso in $(0{,}83;\ 0{,}70)$, appena sopra la soglia, nella zona quasi lineare della curva.

### Notebook 4 · Un estrattore di feature

```python
PRONOUNS = {"i", "me", "my", "mine", "we", "us", "our", "you", "your"}

def six_features(tokens, pos_lex, neg_lex):
    t = [w.lower() for w in tokens]
    return [sum(w in pos_lex for w in t), sum(w in neg_lex for w in t), int("no" in t),
            sum(w in PRONOUNS for w in t), int("!" in t), math.log(len(t))]

EX_POS = {"loved", "great", "nice", "enjoyable"}
EX_NEG = {"boring", "awful", "hokey", "second-rate"}
review = "I loved this film ! The acting is great , the plot is not boring , and the music is nice ."
```

Output:

```text
x = [3, 1, 0, 1, 1, 3.09]   (22 tokens)
z = 7.26   P(+ | x) = 0.999
```

Le sei feature della [scheda 26](L06-regressione-logistica.md#p-26) come funzione: tokenizzazione per spazi (la recensione è già separata), confronto in minuscolo, lessici come insiemi. Sulla recensione dell'esercizio 5: tre parole positive (*loved, great, nice*), una negativa (*boring*), nessun *no*, un pronome (*I*), un "!", 22 token, $\ln 22 = 3{,}09$. Verificato a mano: $z = 7{,}5 - 5 + 0 + 0{,}5 + 2 + 0{,}7\cdot 3{,}091 + 0{,}1 = 7{,}26$.

Il punto della cella 13: *not boring* è un giudizio positivo, ma fa crescere $x_2$, il conteggio delle parole negative con peso $-5$. La recensione è classificata bene nonostante questo errore di feature, grazie al resto. Il notebook riprende la negazione nella sezione 9.

### Notebook 5 · La cross-entropy loss

```python
def ce_loss(y_hat, y):
    return -(y * math.log(y_hat) + (1 - y) * math.log(1 - y_hat))
```

Output:

```text
if the review is positive (y = 1): loss = 0.36
if the review is negative (y = 0): loss = 1.19   (with y_hat rounded to 0.70, as in the book: 1.20)
y_hat = 0.9:  loss with y = 1: 0.105   loss with y = 0: 2.303
y_hat = 0.5:  loss with y = 1: 0.693   loss with y = 0: 0.693
y_hat = 0.1:  loss with y = 1: 2.303   loss with y = 0: 0.105
cost of the mini-batch: 0.301
y = 1 and y_hat going to 0: [4.6, 9.2, 18.4]
```

La formula della [scheda 37](L06-regressione-logistica.md#p-37) con il log naturale. Sulla recensione: 0,36 e 1,19 (1,20 nel libro, che usa $\hat y$ arrotondato a 0,70: [scheda 39](L06-regressione-logistica.md#p-39)). I valori dell'esercizio 9 mostrano la simmetria ($\hat y = 0{,}9$ con $y = 1$ costa quanto $\hat y = 0{,}1$ con $y = 0$) e il caso neutro $\ln 2 = 0{,}693$. Il costo del mini-batch $(1,1,0)$ con $\hat y = (0{,}9;\ 0{,}5;\ 0{,}1)$ è la media $(0{,}105+0{,}693+0{,}105)/3 = 0{,}301$. L'ultima riga: con $y = 1$, ogni volta che $\hat y$ si divide per 100 la loss cresce di $\ln 100 = 4{,}6$, senza limite.

Nota pratica: `ce_loss` con $\hat y$ esattamente 0 o 1 darebbe `math domain error` (log di 0); la versione numpy della sezione 7 ritaglia $\hat y$ in $[10^{-12}, 1-10^{-12}]$ con `np.clip` proprio per questo.

### Notebook 6 · Un passo di discesa del gradiente e il controllo numerico

```python
def gradient(w, b, x, y):
    err = sigmoid(weighted_sum(w, x, b)) - y
    return [err * xi for xi in x], err

def sgd_step(w, b, x, y, eta):
    gw, gb = gradient(w, b, x, y)
    return [wi - eta * gi for wi, gi in zip(w, gw)], b - eta * gb

def numerical_gradient(w, b, x, y, h=1e-6):
    # (L(theta + h) - L(theta - h)) / 2h, one parameter at a time
```

Output:

```text
gradient: ([-1.5, -1.0], -0.5)
new parameters: [0.15, 0.1] 0.05
loss before 0.69, after 0.40, y_hat after 0.67
y = 0: formula [0.322218, 0.161109, -0.241663, 0.161109]   numerical [0.322218, 0.161109, -0.241663, 0.161109]
y = 1: formula [-1.677782, -0.838891, 1.258337, -0.838891]   numerical [-1.677782, -0.838891, 1.258337, -0.838891]
```

`gradient` è la formula $(\hat y - y)x_j$ e $\hat y - y$ per il bias ([scheda 45](L06-regressione-logistica.md#p-45)); `sgd_step` sottrae $\eta$ volte il gradiente, **bias compreso**. Riproduce il passo delle [schede 48-50](L06-regressione-logistica.md#p-48): gradiente $[-1{,}5;\ -1{,}0;\ -0{,}5]$, nuovi parametri $[0{,}15;\ 0{,}1;\ 0{,}05]$, loss da 0,69 a 0,40.

La cella 21 è un'abitudine da prendere: confrontare il gradiente analitico con le **differenze finite centrate** $(L(\theta+h)-L(\theta-h))/2h$ in un punto qualunque (qui con tre feature, una negativa). Le due liste coincidono alla sesta cifra per $y = 0$ e $y = 1$: segni e fattori della formula sono giusti. Si nota anche che le componenti per $y = 1$ sono quelle per $y = 0$ meno $x_j$ (l'errore cambia di esattamente 1).

### Notebook 7 · Esercizi 10, 11 e 12: passi stocastici e mini-batch

```python
POS_EX, NEG_EX = ([3, 2], 1), ([2, 5], 0)
w, b = sgd_step([0.0, 0.0], 0.0, *NEG_EX, eta=0.1)          # exercise 10
w, b = sgd_step([0.0, 0.0], 0.0, *POS_EX, eta=0.1)          # exercise 11
w, b = sgd_step(w, b, *NEG_EX, eta=0.1)
grads = [gradient([0.0, 0.0], 0.0, *ex) for ex in (POS_EX, NEG_EX)]   # exercise 12
gw = [sum(g[0][j] for g in grads) / 2 for j in range(2)]
```

Output:

```text
exercise 10, one step on the negative example: [-0.1, -0.25] -0.05
exercise 11, after the positive example:      [0.15, 0.1] 0.05
             after the negative example:      [0.01, -0.25] -0.02
             loss on the negative example 1.21 -> 0.25; loss on the positive example 0.69 -> 0.97
exercise 12, mini-batch gradient: [-0.25, 0.75] 0.0  new parameters: [0.025, -0.075] 0.0
```

Le soluzioni degli esercizi 10-12, che coincidono con i miei conti (sezione Studio). Due osservazioni:

- Esercizio 11: il secondo passo (sull'esempio negativo) fa crollare la loss su quell'esempio (1,21 → 0,25) ma fa **salire** quella sull'esempio positivo fino a 0,97, sopra il valore iniziale 0,69. È il comportamento "choppy" della SGD ([scheda 51](L06-regressione-logistica.md#p-51)): ogni passo pensa solo all'esempio corrente.
- Esercizio 12: con il mini-batch dei due esempi il gradiente medio di $b$ è 0 (gli errori $-0{,}5$ e $+0{,}5$ si annullano) e $w_2$ va subito in negativo ($-0{,}075$), perché l'esempio negativo ha più parole negative (5 contro 2).

### Notebook 8 · Un piccolo dataset di recensioni generate

```python
def clause(rng, polarity):
    aspect = rng.choice(ASPECTS)
    if rng.random() < 0.2:      # one in five with a negation
        return f"{aspect} is not {rng.choice(NEG_WORDS if polarity else POS_WORDS)}"
    return f"{aspect} is {'very ' if rng.random() < 0.3 else ''}{rng.choice(POS_WORDS if polarity else NEG_WORDS)}"

# make_review: 2-4 aspects, the majority agrees with the label,
# optional "no" sentence and closer, 5% of the labels flipped
rng = random.Random(2026)
data = [make_review(rng) for _ in range(2000)]
train_data, test_data = data[:1500], data[1500:]
```

Output:

```text
1500 training reviews, 500 test reviews, 49% positive in training
+ the photography is wonderful but the acting is very awful but the photography is not terrible and the script is moving .
- the photography is not brilliant , the ending is weak . you will hate it .
- i saw this film last week . the plot is predictable , the script is terrible . no one laughed .
```

Le recensioni sono generate da modelli fissi: da 2 a 4 aspetti del film (*the acting, the plot, ...*), ognuno con un giudizio, la maggioranza concorde con l'etichetta; un giudizio su cinque è espresso con una **negazione** (*the plot is not boring* è positivo); frasi finali tipiche di ciascuna classe (*you will hate it*, *go and see it !*), frasi con *no* più frequenti nelle negative, e il 5% di etichette invertite come rumore di annotazione. Seme fisso: i dati sono identici a ogni esecuzione.

Il dataset è diviso in 1500 recensioni di training e 500 di test, e il test non viene mai usato per stimare nulla (vocabolario, medie e deviazioni standard si calcolano sul training): niente *leakage*. Il primo esempio stampato mostra già una difficoltà: è positivo, ma contiene *awful* e *terrible*.

### Notebook 9 · Molti esempi insieme e la funzione di training

```python
def predict(X, w, b):
    return 1 / (1 + np.exp(-(X @ w + b)))

def cost(X, y, w, b):
    p = np.clip(predict(X, w, b), 1e-12, 1 - 1e-12)
    return -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))

def batch_gradient(X, y, w, b):
    err = predict(X, w, b) - y
    return X.T @ err / len(y), err.mean()

def train_lr(X, y, eta=0.1, epochs=30, batch_size=16, seed=0):
    rng = np.random.default_rng(seed)
    w, b = np.zeros(X.shape[1]), 0.0
    history = [cost(X, y, w, b)]
    for _ in range(epochs):
        order = rng.permutation(len(y))
        for start in range(0, len(y), batch_size):
            idx = order[start:start + batch_size]
            gw, gb = batch_gradient(X[idx], y[idx], w, b)
            w, b = w - eta * gw, b - eta * gb
        history.append(cost(X, y, w, b))
    return w, b, history
```

Output:

```text
Xw + b = [ 1.5 -2.5  0.5]   y_hat = [0.82 0.08 0.62]   decisions = [1 0 1]
exercise 12: (array([-0.25,  0.75]), np.float64(0.0))
```

`predict` è $\hat{\mathbf{y}} = \sigma(\mathbf{X}\mathbf{w}+b)$ della [scheda 33](L06-regressione-logistica.md#p-33) (il bias scalare si estende a tutte le righe per broadcasting); risolve l'esercizio 8. `batch_gradient` è la forma matriciale della [scheda 52](L06-regressione-logistica.md#p-52): $\frac1m\mathbf{X}^\top(\hat{\mathbf{y}}-\mathbf{y})$ per i pesi e la **media** degli errori per il bias; ritrova il gradiente dell'esercizio 12.

`train_lr` fa la discesa a mini-batch: a ogni epoca rimescola gli esempi, li divide in blocchi di `batch_size` e fa un aggiornamento per blocco, bias compreso; con `batch_size=1` è SGD, con `batch_size=len(y)` batch training. Pesi iniziali a zero ([scheda 46](L06-regressione-logistica.md#p-46)). Il costo registrato a fine epoca è quello su tutto il training. Ho controllato i punti in cui un'implementazione sbaglia di solito (segno dell'aggiornamento, bias non aggiornato, somma invece di media, ultimo mini-batch più corto, dtype intero di `y`): sono tutti corretti.

### Notebook 10 · Le sei feature: pesi del libro e pesi appresi

```python
X6_train, y_train = six_matrix(train_data)
X6_test, y_test = six_matrix(test_data)
print(accuracy(X6_test, y_test, np.array(BOOK_W), BOOK_B))
mean6, std6 = X6_train.mean(axis=0), X6_train.std(axis=0)      # training statistics only
S6_train, S6_test = (X6_train - mean6) / std6, (X6_test - mean6) / std6
w6, b6, hist6 = train_lr(S6_train, y_train, eta=0.1, epochs=30, batch_size=16)
w6_raw = w6 / std6         # the same weights, for the features before standardization
```

Output:

```text
exercise 7: mean 5, standard deviation 2.37, z-scores [-1.27, -0.42, -0.42, 0.42, 1.69], normalized [0.0, 0.29, 0.29, 0.57, 1.0]
accuracy of the hand-set weights of the book: 0.764
accuracy of the learned weights: 0.778   (training cost 0.693 -> 0.469)

                                weights           average value
feature                         book  learned    negative  positive
positive lexicon words           2.5    0.45       0.91      2.11
negative lexicon words          -5.0   -1.09       2.07      0.91
'no' in the review              -1.2   -1.44       0.25      0.08
1st and 2nd person pronouns      0.5   -0.30       1.26      1.16
'!' in the review                2.0    0.33       0.23      0.40
ln(length)                       0.7    1.49       3.15      3.17
```

Prima l'esercizio 7 (z-score e min-max con la deviazione standard "di popolazione", divisione per $m$, come nella [scheda 31](L06-regressione-logistica.md#p-31)). Poi le sei feature sulle recensioni generate. I pesi del libro, mai visti questi dati, danno già il 76,4% di accuratezza sul test; i pesi appresi il 77,8%, con il costo di training che scende da $\ln 2 = 0{,}693$ (pesi a zero) a 0,469.

La standardizzazione usa media e deviazione standard del **solo training**, applicate anche al test: corretto. `w6 / std6` riporta i pesi alla scala delle feature grezze (se $x' = (x-\mu)/\sigma$, allora $w'x' = (w'/\sigma)x - w'\mu/\sigma$: il peso per $x$ è $w'/\sigma$, il resto finisce nel bias, che il notebook non stampa).

Lettura della tabella: lessici, *no* e "!" hanno i segni del libro, e le medie per classe spiegano perché (le recensioni positive hanno in media 2,11 parole positive contro 0,91). I pesi appresi sono più piccoli in modulo di quelli scritti a mano (tranne *no*): con negazioni ed etichette rumorose i dati non giustificano tanta fiducia. Pronomi e lunghezza hanno la stessa media nelle due classi ma pesi non nulli: le feature sono correlate (recensioni più lunghe hanno più parole di entrambi i lessici) e i pesi si compensano; un peso non si legge da solo. L'accuratezza resta sotto l'80% perché i lessici sono ingannati dalla negazione.

### Notebook 11 · Le parole come feature

```python
def bow_matrix(dataset, vocab):
    index = {w: j for j, w in enumerate(vocab)}
    X = np.zeros((len(dataset), len(vocab)))
    for i, (tokens, _) in enumerate(dataset):
        for t in tokens:
            if t in index:
                X[i, index[t]] += 1
    return X

vocab = sorted(set(t for tokens, _ in train_set for t in tokens))   # training vocabulary only
```

Output:

```text
75 word features.  Test accuracy: logistic regression 0.896, Naive Bayes 0.892
most negative weights: hate -1.48, money -1.24, save -1.24, your -1.24, . -0.97, terrible -0.82
most positive weights: go 1.03, it 0.99, enjoyable 0.98, recommend 0.89, superb 0.84, better 0.83
weight of not: 0.12
```

Invece di due lessici, **ogni parola del vocabolario è una feature** (bag of words: $x_j$ = conteggio della parola $j$). Il vocabolario si costruisce sul training; le parole di test fuori vocabolario sono ignorate, come nel Naive Bayes. Accuratezza 89,6% per la regressione logistica, 89,2% per il Naive Bayes multinomiale della sezione 1 sugli stessi dati: qui i due classificatori lineari si equivalgono.

I pesi estremi mostrano che cosa ha imparato il modello: oltre alle parole di sentiment usa le **frasi finali** dei modelli (*hate*, *save your money*, *go*, *recommend*) e perfino il punto. Qualunque indizio correlato all'etichetta nel training riceve un peso: con dati reali è così che un classificatore impara scorciatoie indesiderate. *not* ha peso quasi nullo (0,12): da solo non dice nulla, conta che cosa nega.

### Notebook 12 · La negazione: il trucco NOT_

```python
def mark_negation(tokens, negations=("not", "no", "never", "n't"), stops=(".", ",", "!", "?", "and", "but")):
    out, negated = [], False
    for t in tokens:
        if t in stops:
            negated = False
            out.append(t)
        elif negated:
            out.append("NOT_" + t)
        else:
            out.append(t)
            negated = t in negations
    return out
```

Output:

```text
the plot is not NOT_boring and the music is nice .
with NOT_: logistic regression 0.946, Naive Bayes 0.950   (before: 0.896)
  weight of boring       -1.14
  weight of NOT_boring    0.75
  weight of great         0.98
  weight of NOT_great    -0.87
hand-set weights of the book: 0.950   (without negation marking: 0.764)
learned weights:              0.950   (without negation marking: 0.778)
learned weights, for the raw features: [ 1.12 -1.46 -0.49 -0.09 -0.04  0.91]
```

Il rimedio dell'Appendice B: dopo una negazione, ogni parola fino al successivo segno di punteggiatura riceve il prefisso `NOT_`, così *not boring* diventa *not NOT\_boring* e `NOT_boring` è una feature a sé con il suo peso. Qui anche *and* e *but* chiudono l'ambito, perché nei modelli separano le clausole. Risultato: `NOT_boring` ha peso $+0{,}75$, opposto a *boring* ($-1{,}14$); `NOT_great` $-0{,}87$, opposto a *great*. Le accuratezze salgono al 94,6% (regressione logistica) e 95,0% (Naive Bayes).

La cella 39 applica lo stesso trucco alle sei feature: una parola negativa negata conta nel lessico positivo e viceversa (il confronto è in minuscolo, quindi `not_boring`). Anche i pesi scritti a mano del libro salgono dal 76,4% al 95,0%: il problema non erano i pesi ma le feature, un esempio concreto di quanto conti la rappresentazione ([scheda 30](L06-regressione-logistica.md#p-30)). Sui dati reali la negazione è più difficile: può stare lontano dalla parola che nega, e sarcasmo o contrasto (*it could have been great*) richiedono più di un prefisso.

### Notebook 13 · Il learning rate e lo scaling

```python
for eta in (0.03, 0.3, 3, 30):
    _, _, hist = train_lr(S6_train, y_train, eta=eta, epochs=60, batch_size=len(y_train))
for eta in (0.3, 3):
    _, _, h_raw = train_lr(X6_train, y_train, eta=eta, epochs=60, batch_size=len(y_train))
    _, _, h_std = train_lr(S6_train, y_train, eta=eta, epochs=60, batch_size=len(y_train))
```

Output:

```text
eta =  0.03: training cost after 5 epochs 0.669, after 60 epochs 0.539
eta =   0.3: training cost after 5 epochs 0.548, after 60 epochs 0.471
eta =     3: training cost after 5 epochs 0.471, after 60 epochs 0.468
eta =    30: training cost after 5 epochs 2.254, after 60 epochs 2.892
eta = 0.3: cost after 60 epochs, raw features 0.480, standardized 0.471
eta = 3: cost after 60 epochs, raw features 2.136, standardized 0.468
```

Batch training (un aggiornamento per epoca) sulle sei feature standardizzate, con quattro learning rate. Nel grafico: $\eta = 0{,}03$ (verde) scende lentissimo e dopo 60 epoche è ancora a 0,539; $\eta = 0{,}3$ (blu) arriva a 0,471; $\eta = 3$ (blu scuro) scende quasi in verticale e in poche epoche si stabilizza a 0,468, il minimo; $\eta = 30$ (rosso) oscilla con picchi fino a circa 3 senza mai convergere: è il pannello *too high* della [scheda 47](L06-regressione-logistica.md#p-47) su un problema vero. Poiché la loss è convessa, tutti i learning rate che convergono arrivano allo stesso minimo (0,468); cambia solo il tempo.

La seconda cella mostra perché si scala ([scheda 32](L06-regressione-logistica.md#p-32)): con $\eta = 3$ le feature standardizzate convergono, quelle grezze (conteggi fino a 4 e più, log della lunghezza intorno a 3, indicatori 0/1) no (costo 2,136). Il learning rate "giusto" dipende dalla scala delle feature, e con scale diverse non ne esiste uno buono per tutte.

### Notebook 14 · Stochastic, mini-batch e batch

```python
Xw_train = bow_matrix(train_data, vocab)
for bs in (1, 16, 128, len(y_train)):
    _, _, hist = train_lr(Xw_train, y_train, eta=0.1, epochs=20, batch_size=bs)
```

Output:

```text
batch size    1: training cost after 20 epochs 0.482, increases from one epoch to the next: 9
batch size   16: training cost after 20 epochs 0.314, increases from one epoch to the next: 5
batch size  128: training cost after 20 epochs 0.350, increases from one epoch to the next: 1
batch size 1500: training cost after 20 epochs 0.574, increases from one epoch to the next: 0
```

Stesse feature (bag of words), stesso $\eta = 0{,}1$, quattro dimensioni del mini-batch: 1500, 94, 12 e 1 aggiornamenti per epoca. Nel grafico: il batch training (blu scuro) scende in linea quasi retta e lentissima (0,574 dopo 20 epoche: solo 20 aggiornamenti in tutto); il mini-batch da 128 (verde) scende liscio; quello da 16 (blu) scende più in fretta di tutti, con piccole oscillazioni, fino a 0,314; la SGD pura (rosso) cala subito a 0,34 ma poi **salta su e giù** fino quasi a 1,0 all'epoca 17, chiudendo a 0,482. Sono i movimenti *choppy* della [scheda 51](L06-regressione-logistica.md#p-51): ogni aggiornamento rincorre un singolo esempio.

> **Approfondimento: La SGD rumorosa vuole un learning rate più piccolo**
>
> Il rumore della curva rossa non è un difetto della SGD in sé ma della combinazione SGD + $\eta = 0{,}1$ su conteggi non scalati: un singolo esempio con un gradiente grande sposta tutti i pesi. Rieseguendo lo stesso training con $\eta = 0{,}01$ (verificato), dopo 20 epoche il costo è 0,317 invece di 0,482 e il massimo dopo la prima epoca scende da 0,99 a 0,40. È la ragione del consiglio della [scheda 47](L06-regressione-logistica.md#p-47): learning rate che decresce nel tempo ($\eta_k$), oppure mini-batch, che media il rumore.

## Studio ed esercizi

### Guida allo studio (circa 3 h 55 min)

**Classificazione e Naive Bayes** (45 min)

Schede 4-18. Saper definire text classification con esempi e spiegare perché il language modeling è una classificazione (scheda 6); tre modi di classificare e perché le regole sono fragili (scheda 9); notazione $x^{(i)}_j$ e i quattro componenti (schede 10-12); generativo contro discriminativo (scheda 13). Naive Bayes: argmax con Bayes, ipotesi bag of words e naive, spazio log, training per conteggio, add-one; rifare a mano l'esempio della scheda 18. Esercizi 1, 2 e aggiuntivo B; celle 1-5 del notebook. Appendice B del libro.

**Sigmoide e regressione logistica** (55 min)

Schede 19-33. Somma pesata e significato di pesi e bias; sigmoide, valori notevoli, simmetria $1-\sigma(z) = \sigma(-z)$, derivata; logit e log odds; soglia 0,5 ed equivalenza con $z &gt; 0$ (classificatore lineare). Rifare il conto della recensione (scheda 28) e le varianti. Period disambiguation, interazioni, template, representation learning; scaling (z-score, min-max, log) e forma matriciale con le dimensioni. Esercizi 3-8; celle 6-13 e 26-32 del notebook. Libro §4.1-4.3.

**Cross-entropy loss** (35 min)

Schede 35-39. Derivare la loss da Bernoulli + log + cambio di segno (scheda 37), saperne disegnare le due curve e leggerle (scheda 38), calcolare 0,36 e 1,2 sulla recensione; legame con la cross-entropy della L5. Esercizio 9; celle 14-17. Libro §4.4-4.5.

**Discesa del gradiente** (60 min)

Schede 40-52. Obiettivo come argmin della loss media, convessità (e perché "al più" un minimo); discesa in una dimensione e segno del passo; gradiente come vettore di derivate parziali; formula $(\hat y - y)x_j$ con la derivazione della scheda 45; algoritmo SGD, inizializzazione e criteri di arresto; learning rate e i tre pannelli della scheda 47; rifare il passo delle schede 48-50; stochastic, batch, mini-batch e la forma matriciale del gradiente. Esercizi 10-12 e aggiuntivo A; celle 18-23 e 41-46. Libro §4.6.

**Ripasso orale e notebook** (40 min)

Rispondere ad alta voce alle domande d'orale qui sotto senza guardare gli appunti; poi eseguire il notebook (sezioni 6-10) e saper spiegare: perché i pesi appresi delle sei feature sono più piccoli di quelli del libro, perché le parole come feature battono i lessici, come funziona il trucco `NOT_`, che cosa mostrano i grafici del learning rate e della dimensione del mini-batch.

### Esercizi

#### Esercizio 1 (scheda L06): compiti di classificazione

Per ciascun compito indica l'input $x$, l'insieme delle classi $Y$ e una feature utile. (a) Decidere se una email è spam. (b) Decidere in che lingua è scritto un tweet. (c) Decidere se un punto chiude una frase. (d) Predire il token successivo di un testo con un vocabolario di 50.000 token BPE. Per uno dei compiti scrivi una regola a mano e spiega perché sarebbe fragile.

<details><summary>Soluzione</summary>

- (a) $x$: l'email (testo, oggetto, mittente); $Y = \{\text{spam}, \text{not-spam}\}$; feature: conteggio di parole come *free*, *winner*; presenza di link; mittente fuori rubrica.
- (b) $x$: il tweet; $Y$ = l'insieme delle lingue considerate (tante classi); feature: conteggi di n-gram di caratteri (*th*, *ch*, *ñ*), presenza di parole funzionali (*the*, *der*, *il*), script Unicode.
- (c) $x$: il punto con la parola che lo porta e il contesto; $Y = \{\text{EOS}, \text{not-EOS}\}$; feature: parola minuscola, parola in un dizionario di abbreviazioni, parola successiva maiuscola.
- (d) $x$: il contesto (i token precedenti); $Y$ = i 50.000 token, una classe per token; feature: gli ultimi token (come negli n-gram) o, in un LLM, una rappresentazione appresa del contesto. È il language modeling visto come classificazione ([scheda 6](L06-regressione-logistica.md#p-6)).

Regola a mano, per (a): "se l'email contiene *free* e un link, è spam". Fragile: gli spammer cambiano parole (*fr33*), molte email legittime (newsletter, offerte richieste) contengono entrambi, e le feature interagiscono (un link da un mittente noto è innocuo); ogni eccezione richiede una nuova regola. Lo stesso per (c): "un punto dopo minuscola chiude la frase" sbaglia su *etc.* o *e.g.* a metà frase.

</details>

#### Esercizio 2 (scheda L06, dall'Appendice B): Naive Bayes a mano

Training set di cinque recensioni: negative *just plain boring*; *entirely predictable and lacks energy*; *no surprises and very few laughs*; positive *very powerful*; *the most fun film of the summer*. $|V| = 20$; le negative contengono 14 parole, le positive 9. (a) Con add-one, classifica la recensione di test *very boring and no fun*: calcola $P(-)P(S\mid -)$ e $P(+)P(S\mid +)$. (b) Quanto varrebbe $P(+)P(S\mid +)$ senza smoothing? Perché è un problema? (c) In una frase ciascuno: che cosa modellano il Naive Bayes (generativo) e la regressione logistica (discriminativa)?

<details><summary>Soluzione</summary>

(a) Prior $P(-) = 3/5$, $P(+) = 2/5$. Tutte e cinque le parole sono nel vocabolario. Conteggi tra le negative: *very* 1, *boring* 1, *and* 2, *no* 1, *fun* 0; tra le positive: *very* 1, *boring* 0, *and* 0, *no* 0, *fun* 1. Denominatori $14+20 = 34$ e $9+20 = 29$.

$$P(-)P(S\mid -) = \frac35\cdot\frac{2\cdot2\cdot3\cdot2\cdot1}{34^5} = \frac35\cdot\frac{24}{45.435.424} = 3{,}17\times10^{-7}$$$$P(+)P(S\mid +) = \frac25\cdot\frac{2\cdot1\cdot1\cdot1\cdot2}{29^5} = \frac25\cdot\frac{4}{20.511.149} = 7{,}80\times10^{-8}$$

Negativa, con un rapporto di circa 4 a 1 ($P(-\mid S) = 0{,}80$ normalizzando).

(b) Senza smoothing $P(\text{boring}\mid +) = 0/9 = 0$ (e anche *and*, *no*), quindi $P(+)P(S\mid +) = 0$. Ma anche $P(\text{fun}\mid -) = 0/14$, quindi pure $P(-)P(S\mid -) = 0$: entrambi i punteggi sono nulli e il classificatore non può decidere. Una sola parola mai vista con una classe azzera quella classe qualunque siano le altre parole (lo conferma la cella 4 del notebook).

(c) Il Naive Bayes modella come ciascuna classe genera i documenti, $P(c)$ e $P(d\mid c)$, e ricava $P(c\mid d)$ con Bayes; la regressione logistica modella direttamente $P(c\mid d)$, con un peso per feature scelto per separare le classi.

</details>

#### Esercizio 3 (scheda L06): sigmoide e logit

(a) Calcola $\sigma(0)$, $\sigma(\ln 3)$ e $\sigma(-\ln 3)$; verifica $1-\sigma(z) = \sigma(-z)$ su $z = \ln 3$. (b) Con la calcolatrice, $\sigma(2)$ e $\sigma(-2)$. (c) Qual è il logit di $p = 0{,}8$? Quale $z$ dà $P(y=1\mid x) = 0{,}9$, e quale $0{,}99$? (d) Di quanto deve spostarsi $z$ da 0 perché la probabilità passi da 0,5 a 0,9, e da 0,9 a 0,99? Che cosa dice della forma della sigmoide?

<details><summary>Soluzione</summary>

(a) $\sigma(0) = 1/(1+1) = 0{,}5$. $\sigma(\ln 3) = 1/(1+e^{-\ln 3}) = 1/(1+1/3) = 3/4 = 0{,}75$. $\sigma(-\ln 3) = 1/(1+3) = 1/4 = 0{,}25$. Verifica: $1-\sigma(\ln 3) = 1-3/4 = 1/4 = \sigma(-\ln 3)$.

(b) $\sigma(2) = 1/(1+e^{-2}) = 1/1{,}1353 = 0{,}881$; $\sigma(-2) = 0{,}119$; somma 1.

(c) $\text{logit}(0{,}8) = \ln(0{,}8/0{,}2) = \ln 4 = 1{,}386$. Per $p = 0{,}9$: $z = \ln 9 = 2{,}197$. Per $p = 0{,}99$: $z = \ln 99 = 4{,}595$.

(d) Da 0,5 a 0,9: $z$ da 0 a 2,20. Da 0,9 a 0,99: da 2,20 a 4,60, cioè altri 2,40, più del primo tratto per un guadagno di probabilità dieci volte più piccolo (0,09 contro 0,4). La sigmoide è ripida al centro e sempre più piatta verso gli estremi: avvicinarsi a 1 costa sempre di più in termini di $z$ (passare da odds 9 a odds 99 costa $\ln 11 = 2{,}4$ in $z$).

</details>

#### Esercizio 4 (scheda L06): la recensione di esempio

Classificatore di sentiment della lezione: pesi $\mathbf{w} = [2{,}5;\ -5{,}0;\ -1{,}2;\ 0{,}5;\ 2{,}0;\ 0{,}7]$ per le feature (lessico positivo, lessico negativo, *no*, pronomi di 1a e 2a persona, "!", ln della lunghezza), bias $b = 0{,}1$. La recensione di esempio ha $\mathbf{x} = [3, 2, 1, 3, 0, \ln 66 = 4{,}19]$. (a) Calcola $z$ e $P(+\mid x)$. (b) $P(+\mid x)$ se contenesse anche un punto esclamativo ($x_5 = 1$). (c) $P(+\mid x)$ senza la parola *no* ($x_3 = 0$). (d) Che cosa succede alla decisione con una parola negativa in più?

<details><summary>Soluzione</summary>

(a) $z = 7{,}5 - 10 - 1{,}2 + 1{,}5 + 0 + 2{,}933 + 0{,}1 = 0{,}833$; $P(+\mid x) = \sigma(0{,}833) = 1/(1+e^{-0{,}833}) = 1/(1+0{,}435) = 0{,}697 \approx 0{,}70$. Positiva.

(b) $z$ cresce di $w_5\cdot 1 = 2{,}0$: $z = 2{,}833$, $P = 0{,}944$.

(c) $z$ cresce di $1{,}2$ (si toglie $w_3 = -1{,}2$): $z = 2{,}033$, $P = 0{,}884$.

(d) $x_2 = 3$: $z$ cala di 5, $z = -4{,}167$, $P(+\mid x) = 0{,}015$. La decisione si ribalta: negativa, e con grande sicurezza. Una parola negativa pesa il doppio di una positiva.

</details>

#### Esercizio 5 (scheda L06): feature a mano

Con il classificatore dell'esercizio 4, il lessico positivo {loved, great, nice, enjoyable} e quello negativo {boring, awful, hokey, second-rate}, considera la recensione

```
I loved this film ! The acting is great , the plot is not boring , and the music is nice .
```

(a) Calcola le sei feature (conta ogni parola e segno di punteggiatura per $x_6$). (b) Calcola $z$ e $P(+\mid x)$. (c) *not boring* è positivo, ma quale feature fa crescere? Proponi una modifica delle feature che lo gestisca.

<details><summary>Soluzione</summary>

(a) $x_1 = 3$ (*loved, great, nice*); $x_2 = 1$ (*boring*); $x_3 = 0$ (niente *no*: *not* è un'altra parola); $x_4 = 1$ (*I*); $x_5 = 1$; token: 22 (18 parole e 4 segni: "!", due virgole, il punto), $x_6 = \ln 22 = 3{,}091$.

(b) $z = 7{,}5 - 5{,}0 + 0 + 0{,}5 + 2{,}0 + 0{,}7\cdot 3{,}091 + 0{,}1 = 7{,}264$; $P(+\mid x) = \sigma(7{,}264) = 0{,}9993$.

(c) *not boring* fa crescere $x_2$, il conteggio delle parole **negative**, che ha peso $-5$: senza quell'errore $z$ sarebbe ancora più alto. Rimedi: (1) marcare la negazione come nell'Appendice B, prefissando `NOT_` alle parole dopo *not* fino alla punteggiatura, e contare una parola negativa negata nel lessico positivo (e viceversa): qui $x_1 = 4$, $x_2 = 0$, $z = 14{,}76$; (2) una feature di interazione "parola negativa preceduta da *not*" o un template di bigram (*not boring* come feature a sé). Il notebook (celle 37-39) mostra che il rimedio (1) porta i pesi del libro dal 76,4% al 95,0% di accuratezza sulle recensioni generate.

</details>

#### Esercizio 6 (scheda L06): disambiguazione del punto

Feature della parola che porta il punto: $x_1 = 1$ se è minuscola; $x_2 = 1$ se è in un dizionario di abbreviazioni {Prof., Dr., St., Inc.}; $x_3 = 1$ se è *St.* e la parola precedente è maiuscola.

```
Prof. Smith lives on Main St. He goes to St. Mary church every sunday.
```

(a) Calcola $x_1, x_2, x_3$ per ciascuno dei quattro punti. (b) Quali punti chiudono una frase? Quale è difficile, e perché nessuna feature da sola può deciderlo?

<details><summary>Soluzione</summary>

| Punto | $x_1$ | $x_2$ | $x_3$ | EOS? |
| --- | --- | --- | --- | --- |
| Prof. | 0 | 1 | 0 | no |
| St. (dopo Main) | 0 | 1 | 1 | sì |
| St. (prima di Mary) | 0 | 1 | 0 | no |
| sunday. | 1 | 0 | 0 | sì |

(b) Chiudono una frase il punto di *Main St.* e quello di *sunday.*. Il caso difficile è *Main St.*: il punto è **insieme** parte dell'abbreviazione e fine frase. Le sue feature ($x_2 = 1$, $x_3 = 1$, cioè "abbreviazione, nome di via") spingono verso not-EOS, proprio come per *Prof.*; il secondo *St.* ha quasi le stesse feature e non è fine frase. Nessuna feature della parola stessa li distingue: serve il contesto **a destra**, per esempio "la parola successiva è maiuscola e non è un nome proprio" (*He* è un pronome) e la combinazione di più feature con i loro pesi. Anche così è ambiguo: *St. Mary* ha anch'esso una maiuscola dopo il punto.

</details>

#### Esercizio 7 (scheda L06): scaling delle feature

Una feature assume i valori 2, 4, 4, 6, 9 su cinque documenti. (a) Standardizzala: media, deviazione standard e z-score. (b) Normalizzala in $[0, 1]$. (c) Perché si prende il log di un conteggio di parole prima di usarlo come feature?

<details><summary>Soluzione</summary>

(a) $\mu = 25/5 = 5$. Scarti al quadrato: 9, 1, 1, 1, 16, somma 28. $\sigma = \sqrt{28/5} = \sqrt{5{,}6} = 2{,}366$ (formula della scheda 31, divisione per $m$; con $m-1$ si avrebbe 2,646). z-score $(x-5)/2{,}366$: $-1{,}27;\ -0{,}42;\ -0{,}42;\ 0{,}42;\ 1{,}69$ (media 0, deviazione 1).

(b) $\min = 2$, $\max = 9$, intervallo 7: $0;\ 2/7 = 0{,}29;\ 0{,}29;\ 4/7 = 0{,}57;\ 1$.

(c) I conteggi seguono una distribuzione Zipfiana: pochi valori molto grandi e molti piccoli. Il log comprime la coda (100 e 1000 diventano 4,6 e 6,9), così i documenti lunghi o le parole frequentissime non dominano la somma pesata, e la differenza tra 1 e 2 occorrenze conta più di quella tra 100 e 101, che è il comportamento desiderato. Inoltre feature con scale confrontabili fanno convergere meglio la discesa del gradiente.

</details>

#### Esercizio 8 (scheda L06): molti esempi insieme

Tre esempi con due feature come righe di $\mathbf{X}$, e un modello con $\mathbf{w} = [1, -1]$ e $b = 0{,}5$: $\mathbf{X} = [[3, 2], [1, 4], [0, 0]]$. (a) Quali sono le dimensioni di $\mathbf{X}$, $\mathbf{w}$, $\mathbf{b}$ e $\hat{\mathbf{y}}$ in $\hat{\mathbf{y}} = \sigma(\mathbf{X}\mathbf{w}+\mathbf{b})$? (b) Calcola $\mathbf{X}\mathbf{w}+\mathbf{b}$, $\hat{\mathbf{y}}$ e la decisione per ciascun esempio.

<details><summary>Soluzione</summary>

(a) $\mathbf{X}$: $3\times 2$ ($m\times f$); $\mathbf{w}$: $2\times 1$; $\mathbf{b}$: $3\times 1$ (lo scalare 0,5 ripetuto tre volte); $\hat{\mathbf{y}}$: $3\times 1$.

(b) $\mathbf{X}\mathbf{w} = [3-2,\ 1-4,\ 0] = [1, -3, 0]$; più $b$: $[1{,}5;\ -2{,}5;\ 0{,}5]$. $\hat{\mathbf{y}} = [\sigma(1{,}5), \sigma(-2{,}5), \sigma(0{,}5)] = [0{,}818;\ 0{,}076;\ 0{,}622]$. Decisioni ($\hat y &gt; 0{,}5$, cioè $z &gt; 0$): $[1, 0, 1]$. Il terzo esempio ha tutte le feature a zero: decide solo il bias.

</details>

#### Esercizio 9 (scheda L06): cross-entropy loss

(a) Calcola la cross-entropy loss (log naturale) per $\hat y = 0{,}9;\ 0{,}5;\ 0{,}1$, prima con $y = 1$ e poi con $y = 0$. (b) Un mini-batch ha tre esempi con etichette $(1, 1, 0)$ e previsioni $\hat y = (0{,}9;\ 0{,}5;\ 0{,}1)$. Qual è il costo del mini-batch? (c) Che cosa succede alla loss quando $y = 1$ e $\hat y \to 0$? Perché è una proprietà desiderabile?

<details><summary>Soluzione</summary>

(a) Con $y = 1$, $L = -\ln\hat y$: $0{,}105;\ 0{,}693;\ 2{,}303$. Con $y = 0$, $L = -\ln(1-\hat y)$: $2{,}303;\ 0{,}693;\ 0{,}105$. Simmetria: sbagliare con sicurezza 0,9 costa 2,30 in entrambe le direzioni; $\hat y = 0{,}5$ costa sempre $\ln 2$.

(b) Loss individuali: $-\ln 0{,}9 = 0{,}105$; $-\ln 0{,}5 = 0{,}693$; $-\ln(1-0{,}1) = 0{,}105$. Costo = media $= 0{,}903/3 = 0{,}301$.

(c) $L = -\ln\hat y \to +\infty$: con $\hat y = 10^{-2}, 10^{-4}, 10^{-8}$ la loss è 4,6; 9,2; 18,4. È desiderabile perché penalizza in modo illimitato una previsione **sicura e sbagliata**, spingendo il modello a non dare mai probabilità quasi nulla alla classe vera; e il gradiente $(\hat y - y)x_j$ resta grande (vicino a $-x_j$) proprio in quel caso, quindi l'errore viene corretto in fretta. Un'etichetta sbagliata nel training, però, pesa molto: è il rovescio della medaglia.

</details>

#### Esercizio 10 (scheda L06, libro 4.3): un passo con un esempio negativo

Rifai il passo di discesa del gradiente della lezione con un esempio di training negativo: $y = 0$, $\mathbf{x} = [2, 5]$, pesi iniziali $w_1 = w_2 = b = 0$, $\eta = 0{,}1$. (a) Calcola il gradiente e i nuovi $w_1$, $w_2$, $b$. (b) Verifica che $w_2$ si è mosso nella direzione prevista a lezione: dopo esempi negativi con molte parole negative, $w_2$ diventa negativo.

<details><summary>Soluzione</summary>

(a) $z = 0$, $\hat y = \sigma(0) = 0{,}5$, errore $\hat y - y = 0{,}5 - 0 = 0{,}5$. Gradiente: $[0{,}5\cdot 2;\ 0{,}5\cdot 5;\ 0{,}5] = [1{,}0;\ 2{,}5;\ 0{,}5]$. Aggiornamento $\theta^1 = \theta^0 - 0{,}1\cdot[1{,}0;\ 2{,}5;\ 0{,}5] = [-0{,}1;\ -0{,}25;\ -0{,}05]$.

(b) $w_2 = -0{,}25$: negativo, e il più negativo dei tre, perché l'esempio ha più parole negative (5) che positive (2) e l'aggiornamento di ogni peso è proporzionale alla sua feature. Anche $w_1$ scende ($-0{,}1$): da un singolo esempio negativo il modello impara che "le parole del lessico positivo erano presenti in un esempio negativo"; servono esempi di entrambe le classi perché $w_1$ diventi positivo e $w_2$ negativo. Controllo: la loss sull'esempio scende da $\ln 2 = 0{,}693$ a $-\ln(1-\sigma(-0{,}2-1{,}25-0{,}05)) = -\ln(1-\sigma(-1{,}5)) = 0{,}201$.

</details>

#### Esercizio 11 (scheda L06): due passi di SGD

Si parte da $w_1 = w_2 = b = 0$ con $\eta = 0{,}1$. Primo passo sull'esempio positivo della lezione, $\mathbf{x} = [3, 2]$, $y = 1$, che dà $\theta^1 = [0{,}15;\ 0{,}1;\ 0{,}05]$. Secondo passo sull'esempio negativo dell'esercizio 10, $\mathbf{x} = [2, 5]$, $y = 0$. (a) Calcola $\hat y$ sull'esempio negativo prima del secondo passo, il gradiente e $\theta^2$. (b) Calcola la loss sull'esempio negativo prima e dopo il secondo passo. (c) Calcola la loss sull'esempio positivo con $\theta^2$ e confrontala con quella iniziale ($-\ln 0{,}5 \approx 0{,}69$): che cosa mostra sulla SGD?

<details><summary>Soluzione</summary>

(a) $z = 0{,}15\cdot 2 + 0{,}1\cdot 5 + 0{,}05 = 0{,}85$; $\hat y = \sigma(0{,}85) = 0{,}7006$. Errore $0{,}7006$. Gradiente $[1{,}401;\ 3{,}503;\ 0{,}701]$. $\theta^2 = [0{,}15 - 0{,}140;\ 0{,}1 - 0{,}350;\ 0{,}05 - 0{,}070] = [0{,}010;\ -0{,}250;\ -0{,}020]$.

(b) Prima: $-\ln(1-0{,}7006) = 1{,}206$ (il modello, dopo aver visto solo un positivo, dà 0,70 di positivo a un negativo). Dopo: $z = 0{,}0198 - 1{,}2514 - 0{,}0201 = -1{,}252$, $\hat y = 0{,}222$, loss $-\ln 0{,}778 = 0{,}252$.

(c) Sull'esempio positivo con $\theta^2$: $z = 0{,}0297 - 0{,}5006 - 0{,}0201 = -0{,}491$, $\hat y = 0{,}380$, loss $-\ln 0{,}380 = 0{,}968$. Dopo il primo passo era 0,403, all'inizio 0,693: ora è **peggio che all'inizio**. Ogni passo di SGD migliora l'esempio corrente e può peggiorare gli altri: i movimenti irregolari (*choppy*) della [scheda 51](L06-regressione-logistica.md#p-51). Sulla media dei due esempi il progresso c'è comunque: costo medio da 0,693 a $(0{,}968+0{,}252)/2 = 0{,}610$.

</details>

#### Esercizio 12 (scheda L06): gradiente di un mini-batch

Usa gli stessi due esempi, $\mathbf{x} = [3, 2]$ con $y = 1$ e $\mathbf{x} = [2, 5]$ con $y = 0$, come un unico mini-batch di dimensione $m = 2$, ripartendo da $w_1 = w_2 = b = 0$ con $\eta = 0{,}1$. (a) Calcola il gradiente del mini-batch, media dei due gradienti individuali, e i nuovi parametri. (b) Confronta con i due passi stocastici dell'esercizio 11: quanti aggiornamenti, e in che direzione si muove $w_2$? (c) La loss della regressione logistica è convessa: perché questo rende poco importante il punto di partenza?

<details><summary>Soluzione</summary>

(a) Con i pesi a zero $\hat y = 0{,}5$ per entrambi. Gradiente del positivo: errore $-0{,}5$, $[-1{,}5;\ -1{,}0;\ -0{,}5]$. Del negativo: errore $+0{,}5$, $[1{,}0;\ 2{,}5;\ 0{,}5]$. Media: $[-0{,}25;\ 0{,}75;\ 0]$. Nuovi parametri: $[0{,}025;\ -0{,}075;\ 0]$.

(b) Un solo aggiornamento invece di due. $w_2$ va **subito** in negativo ($-0{,}075$), mentre nella SGD saliva prima a $+0{,}1$ (passo sul positivo) e poi scendeva a $-0{,}25$; il bias resta 0 perché i due errori si annullano; $w_1$ sale di poco ($0{,}025$) perché le parole positive compaiono in entrambi gli esempi. La direzione del mini-batch tiene conto di entrambi gli esempi insieme, con passi più piccoli e meno rumorosi; il costo medio scende da 0,693 a 0,638 (due passi stocastici: 0,610, ma con due aggiornamenti).

(c) Una funzione convessa ha al più un minimo e nessun minimo locale: da qualunque punto si parta, scendendo lungo il gradiente (con un learning rate adeguato) si arriva allo stesso minimo, quindi l'inizializzazione cambia solo il tempo di convergenza, non il risultato. Per questo i pesi della regressione logistica partono da 0, mentre nelle reti neurali (non convesse) l'inizializzazione conta.

</details>

#### Esercizio aggiuntivo A: la derivata della sigmoide e il gradiente

(a) Dimostra che $\sigma'(z) = \sigma(z)(1-\sigma(z))$ e calcolala in $z = 0$ e $z = 0{,}83$. (b) Usando (a) e la regola della catena, ricava $\partial L_{CE}/\partial w_j = (\hat y - y)x_j$ e $\partial L_{CE}/\partial b = \hat y - y$. (c) Sulla recensione della lezione ($\hat y = 0{,}697$, $\mathbf{x} = [3, 2, 1, 3, 0, 4{,}19]$, $y = 1$) calcola il gradiente rispetto a $w_1$, $w_5$ e $b$.

<details><summary>Soluzione</summary>

(a) $\sigma(z) = (1+e^{-z})^{-1}$, quindi $\sigma'(z) = -(1+e^{-z})^{-2}\cdot(-e^{-z}) = \dfrac{e^{-z}}{(1+e^{-z})^2} = \dfrac{1}{1+e^{-z}}\cdot\dfrac{e^{-z}}{1+e^{-z}} = \sigma(z)(1-\sigma(z))$. In $z = 0$: $0{,}5\cdot 0{,}5 = 0{,}25$ (il massimo). In $z = 0{,}83$: $0{,}697\cdot 0{,}303 = 0{,}211$.

(b) $L = -[y\ln\hat y + (1-y)\ln(1-\hat y)]$ con $\hat y = \sigma(z)$, $z = \mathbf{w}\cdot\mathbf{x}+b$. $\dfrac{\partial L}{\partial\hat y} = -\dfrac{y}{\hat y}+\dfrac{1-y}{1-\hat y} = \dfrac{\hat y-y}{\hat y(1-\hat y)}$. $\dfrac{\partial\hat y}{\partial z} = \hat y(1-\hat y)$. $\dfrac{\partial z}{\partial w_j} = x_j$, $\dfrac{\partial z}{\partial b} = 1$. Moltiplicando, $\hat y(1-\hat y)$ si semplifica: $\dfrac{\partial L}{\partial w_j} = (\hat y-y)x_j$, $\dfrac{\partial L}{\partial b} = \hat y - y$.

(c) Errore $0{,}697 - 1 = -0{,}303$. $\partial L/\partial w_1 = -0{,}303\cdot 3 = -0{,}909$; $\partial L/\partial w_5 = -0{,}303\cdot 0 = 0$ (la feature assente non riceve aggiornamento); $\partial L/\partial b = -0{,}303$. Con $\eta = 0{,}1$, $w_1$ salirebbe da 2,5 a 2,591.

</details>

#### Esercizio aggiuntivo B: il Naive Bayes come classificatore lineare

Riprendi l'esempio della scheda 18 (test *predictable with no fun*). (a) Calcola i due punteggi in spazio log, $\ln P(c) + \sum_i \ln P(w_i\mid c)$. (b) Scrivi la decisione come $z = b + \sum_w \text{count}(w)\,w_w &gt; 0$ per la classe +, con $b = \ln\frac{P(+)}{P(-)}$ e $w_w = \ln\frac{P(w\mid +)}{P(w\mid -)}$; calcola $b$, i pesi delle tre parole e $z$. (c) Verifica che $\sigma(z)$ è proprio $P(+\mid S)$ normalizzata.

<details><summary>Soluzione</summary>

(a) $\ln(6{,}106\cdot10^{-5}) = -9{,}704$ per la classe negativa, $\ln(3{,}280\cdot10^{-5}) = -10{,}325$ per la positiva: vince la negativa. In dettaglio: $\ln\frac35 + 2\ln\frac{2}{34} + \ln\frac{1}{34}$ contro $\ln\frac25 + 2\ln\frac{1}{29} + \ln\frac{2}{29}$.

(b) $b = \ln\frac{2/5}{3/5} = \ln\frac23 = -0{,}405$. $w_{\text{predictable}} = w_{\text{no}} = \ln\frac{1/29}{2/34} = \ln\frac{34}{58} = -0{,}534$; $w_{\text{fun}} = \ln\frac{2/29}{1/34} = \ln\frac{68}{29} = 0{,}852$. $z = -0{,}405 - 0{,}534 - 0{,}534 + 0{,}852 = -0{,}621 &lt; 0$: negativa. È la differenza dei due punteggi di (a): $-10{,}325 - (-9{,}704) = -0{,}621$.

(c) $\sigma(-0{,}621) = 0{,}349$, e $3{,}280/(3{,}280 + 6{,}106) = 0{,}349$. Con due classi il Naive Bayes è una regressione logistica con pesi fissati dai conteggi, $\sigma$ della differenza dei log-punteggi; la regressione logistica li sceglie invece minimizzando la cross-entropy.

</details>

### Domande tipo orale

<details><summary>Che cos'è la text classification? Dai esempi e spiega perché anche il language modeling lo è.</summary>

Traccia: (1) assegnare a un testo un'etichetta da un insieme discreto e fisso di classi; (2) esempi: sentiment analysis (recensioni, editoriali), spam detection, language id, authorship attribution (umanistica e forense); (3) input un'osservazione $x$, output una classe di $Y = \{y_1,\dots,y_M\}$, a partire da feature estratte; (4) language modeling: ogni parola del vocabolario è una classe, predire la parola successiva è classificare il contesto; un LLM è un classificatore con $|V|$ classi che restituisce una distribuzione; (5) per questo la regressione logistica (e la softmax) è alla base dei modelli neurali.

</details>

<details><summary>Quali sono i tre modi di classificare un testo e perché si preferisce l'apprendimento supervisionato?</summary>

Traccia: (1) regole scritte a mano (*love* non preceduto da *don't* → positivo): fragili, i dati cambiano e le feature interagiscono (negazione); (2) prompting di un LLM: può allucinare e non spiega la scelta; (3) apprendimento supervisionato: training set etichettato $\{(x^{(i)}, y^{(i)})\}$ e un algoritmo che impara quali feature contano; il più comune; (4) le liste di parole scritte a mano restano utili come feature, il modello ne stabilisce il peso; (5) classificatori probabilistici: danno anche la probabilità, utile a valle.

</details>

<details><summary>Quali sono i quattro componenti di un classificatore probabilistico? Descrivili per la regressione logistica.</summary>

Traccia: (1) rappresentazione a feature: ogni $x^{(i)}$ diventa $[x_1,\dots,x_n]$ (conteggi di lessici, indicatori, log della lunghezza); (2) funzione di classificazione: $\hat y = \sigma(\mathbf{w}\cdot\mathbf{x}+b)$, sigmoide per due classi, softmax per molte; (3) funzione obiettivo: cross-entropy loss media sugli esempi; (4) ottimizzazione: stochastic gradient descent; (5) training impara $\mathbf{w}, b$; test calcola $P(y\mid x)$ e sceglie l'etichetta più probabile (soglia 0,5); (6) lo stesso schema vale per reti neurali e LLM.

</details>

<details><summary>Differenza tra classificatore generativo e discriminativo, con un esempio di ciascuno.</summary>

Traccia: (1) generativo (Naive Bayes): modella come ogni classe genera i documenti, prior $P(c)$ e likelihood $P(d\mid c)$, poi Bayes per $P(c\mid d)$; (2) discriminativo (regressione logistica): modella direttamente $P(c\mid d)$, un peso per feature scelto per separare le classi; (3) immagine: cani e gatti, imparare com'è fatto ciascuno contro imparare che cosa li distingue; (4) i discriminativi sono spesso più accurati, gestiscono meglio feature correlate (che il NB conta due volte); (5) entrambi qui sono classificatori lineari; il NB si addestra contando, la LR ottimizzando.

</details>

<details><summary>Descrivi il Naive Bayes: ipotesi, training, smoothing, classificazione.</summary>

Traccia: (1) $\hat c = \operatorname{argmax}_c P(d\mid c)P(c)$, $P(d)$ eliminato perché uguale per tutte le classi; (2) bag of words e ipotesi naive (parole indipendenti data la classe): $P(c)\prod_i P(w_i\mid c)$; (3) in spazio log una somma, funzione lineare dei conteggi; (4) training = contare: $P(c) = N_c/N_{doc}$, $P(w\mid c)$ = frequenza di $w$ nel testo concatenato della classe; (5) zeri: una parola mai vista in una classe azzera il prodotto; add-one con $|V|$ di tutte le classi al denominatore; parole di test mai viste in training eliminate; (6) è un modello unigram per classe; (7) esempio: *predictable with no fun* → negativa, $6{,}1\cdot10^{-5}$ contro $3{,}3\cdot10^{-5}$.

</details>

<details><summary>Come calcola la regressione logistica la probabilità di una classe? Che ruolo hanno pesi, bias e sigmoide?</summary>

Traccia: (1) somma pesata $z = \sum_i w_ix_i + b = \mathbf{w}\cdot\mathbf{x}+b$; (2) pesi reali, uno per feature, segno e modulo dicono direzione e importanza dell'indizio (*awesome* positivo, *abysmal* negativo); bias = intercept; (3) $z\in(-\infty,+\infty)$, non è una probabilità; (4) sigmoide $\sigma(z) = 1/(1+e^{-z})$ in $(0,1)$, quasi lineare vicino a 0, schiaccia gli estremi, derivabile; (5) $P(y=1) = \sigma(z)$, $P(y=0) = 1-\sigma(z) = \sigma(-z)$; (6) esempio: recensione con $z = 0{,}83$, $P(+) = 0{,}70$.

</details>

<details><summary>Che cos'è il logit e come si interpreta z?</summary>

Traccia: (1) $\text{logit}(p) = \ln\frac{p}{1-p}$, inversa della sigmoide; (2) $p/(1-p)$ sono gli odds: $p = 0{,}8$ → odds 4 → logit 1,39; (3) chiamare $z$ "logit" ricorda che lo si interpreta come log odds della classe positiva; (4) quindi un peso $w_j$ è la variazione dei log odds per un'unità in più di $x_j$, e gli odds si moltiplicano per $e^{w_j}$; (5) $z = 0$ ↔ $p = 0{,}5$ ↔ odds 1 a 1; il logit va a $\pm\infty$ per $p\to 0, 1$; (6) il termine "logits" si usa anche per i punteggi prima della softmax negli LLM.

</details>

<details><summary>Che cos'è la decision boundary e perché la regressione logistica è un classificatore lineare?</summary>

Traccia: (1) $\hat y = P(y=1\mid x)$; si decide 1 se $\hat y &gt; 0{,}5$, altrimenti 0; (2) $\sigma$ è crescente con $\sigma(0) = 0{,}5$, quindi $\hat y &gt; 0{,}5 \iff z &gt; 0$; (3) il confine $\mathbf{w}\cdot\mathbf{x}+b = 0$ è un iperpiano nello spazio delle feature (una retta con due feature); (4) la sigmoide non cambia la decisione, serve per avere probabilità e una loss derivabile; (5) cambiare la soglia sposta l'iperpiano in parallelo; (6) anche il Naive Bayes è lineare in spazio log; problemi non linearmente separabili richiedono feature di interazione o reti a più strati.

</details>

<details><summary>Descrivi le sei feature del classificatore di sentiment del libro e fai il conto sulla recensione di esempio.</summary>

Traccia: (1) $x_1$ parole del lessico positivo (3: enjoyable, great, nice), $x_2$ negativo (2: hokey, second-rate), $x_3$ = 1 se c'è *no*, $x_4$ pronomi di 1a e 2a persona (3: I, me, you), $x_5$ = 1 se c'è "!" (0), $x_6 = \ln(66) = 4{,}19$; (2) pesi $[2{,}5;\ -5;\ -1{,}2;\ 0{,}5;\ 2;\ 0{,}7]$, $b = 0{,}1$; (3) $z = 7{,}5 - 10 - 1{,}2 + 1{,}5 + 0 + 2{,}93 + 0{,}1 = 0{,}83$; (4) $\sigma(0{,}83) = 0{,}70$: positiva; $P(-) = 0{,}30$; (5) lettura: una parola negativa pesa il doppio di una positiva; (6) limite: *not boring* conta come negativo, serve gestire la negazione.

</details>

<details><summary>Perché e come si scalano le feature? Che cosa sono feature interactions, feature templates e representation learning?</summary>

Traccia: (1) z-score $x' = (x-\mu)/\sigma$ con media e deviazione sul training (σ non è la sigmoide; divisione per $m$); min-max in $[0,1]$; log per conteggi Zipfiani (come $x_6$); (2) motivi: feature confrontabili e discesa del gradiente più rapida (stesso $\eta$ adatto a tutte); (3) statistiche dal solo training, applicate al test; (4) interazioni: combinazioni di feature primitive (*St.* dopo parola maiuscola = Street); (5) template: specifiche che generano molte feature (ogni bigram prima di un punto), spazio sparso, hash; (6) progettare feature costa: il representation learning le impara dai dati (embedding, reti neurali).

</details>

<details><summary>Deriva la cross-entropy loss per la regressione logistica.</summary>

Traccia: (1) obiettivo: massima verosimiglianza condizionata, massimizzare la probabilità delle etichette vere dati gli input; (2) due esiti, Bernoulli: $p(y\mid x) = \hat y^{y}(1-\hat y)^{1-y}$; (3) log: $y\log\hat y + (1-y)\log(1-\hat y)$ (monotono, stesso massimo, somma invece di prodotto); (4) cambio di segno per avere una loss da minimizzare: $L_{CE} = -[y\log\hat y + (1-y)\log(1-\hat y)]$; (5) con $\hat y = \sigma(\mathbf{w}\cdot\mathbf{x}+b)$; (6) esempio: $-\ln 0{,}70 = 0{,}36$ se positiva, $-\ln 0{,}30 = 1{,}2$ se negativa; (7) è la cross-entropy tra la distribuzione vera one-hot e quella stimata.

</details>

<details><summary>Quali proprietà ha la cross-entropy loss e che legame ha con la cross-entropy e la perplexity della L5?</summary>

Traccia: (1) va da 0 ($\hat y$ = 1 sulla classe giusta) a $+\infty$ ($\hat y\to 0$): penalizza molto gli errori sicuri; (2) le due curve $-\log\hat y$ e $-\log(1-\hat y)$ si incrociano a 0,5 con valore $\ln 2$; (3) alzare la probabilità della risposta giusta abbassa quella sbagliata (sommano a 1); (4) $H(p,q) = -\sum_k p_k\log q_k$ con $p$ concentrata sull'etichetta vera: resta $-\log q_{\text{vera}}$; (5) la L5 usava bit, qui nat; (6) negli LLM la loss di training è la stessa con la softmax, mediata sui token; il suo esponenziale è la perplexity.

</details>

<details><summary>Come funziona la discesa del gradiente? Spiega segno del passo, gradiente e learning rate.</summary>

Traccia: (1) obiettivo $\hat\theta = \operatorname{argmin}_\theta\frac1m\sum_i L_{CE}(f(x^{(i)};\theta), y^{(i)})$, $\theta = \{\mathbf{w}, b\}$; (2) in una dimensione $w^{t+1} = w^t - \eta\frac{dL}{dw}$: pendenza negativa → $w$ aumenta; (3) in più dimensioni il gradiente è il vettore delle derivate parziali (pesi e bias), punta dove la loss cresce di più; si va nel verso opposto: $\theta^{t+1} = \theta^t - \eta\nabla L$; (4) $\eta$ iperparametro: troppo alto scavalca e diverge, troppo basso è lento; si fa decrescere ($\eta_k$); (5) la loss della LR è convessa: niente minimi locali; le reti neurali no.

</details>

<details><summary>Qual è il gradiente della cross-entropy per la regressione logistica? Derivalo e interpretalo.</summary>

Traccia: (1) $\partial L/\partial w_j = (\hat y - y)x_j$, $\partial L/\partial b = \hat y - y$; (2) derivazione: catena $\partial L/\partial\hat y\cdot\partial\hat y/\partial z\cdot\partial z/\partial w_j$, con $\partial L/\partial\hat y = (\hat y-y)/(\hat y(1-\hat y))$, $\sigma' = \sigma(1-\sigma)$, $\partial z/\partial w_j = x_j$: il fattore $\hat y(1-\hat y)$ si semplifica; (3) interpretazione: errore della previsione per l'input; previsione giusta → nessun aggiornamento; feature assente → peso invariato; (4) segno: se $y = 1$ e $\hat y$ basso, i pesi delle feature presenti aumentano; (5) controllabile con differenze finite (il notebook lo fa).

</details>

<details><summary>Fai a mano un passo di discesa del gradiente sull'esempio della lezione.</summary>

Traccia: (1) $\mathbf{x} = [3, 2]$, $y = 1$, $w_1 = w_2 = b = 0$, $\eta = 0{,}1$; (2) $z = 0$, $\hat y = 0{,}5$, errore $-0{,}5$; (3) gradiente $[-1{,}5;\ -1{,}0;\ -0{,}5]$, tutto negativo: aumentare i parametri abbassa la loss; (4) $\theta^1 = \theta^0 - 0{,}1\cdot$ gradiente $= [0{,}15;\ 0{,}1;\ 0{,}05]$; (5) ora $z = 0{,}70$, $\hat y = 0{,}67$, loss da 0,69 a 0,40; (6) anche $w_2$ è salito: un solo esempio positivo non basta; con esempi negativi (esercizio 10: $\mathbf{x} = [2,5]$, $y = 0$) $w_2$ diventa negativo.

</details>

<details><summary>Descrivi l'algoritmo SGD e confrontalo con batch e mini-batch training.</summary>

Traccia: (1) SGD: $\theta\leftarrow 0$; ripetere: per ogni esempio in ordine casuale calcolare il gradiente della sua loss e fare $\theta\leftarrow\theta-\eta g$; online, un esempio alla volta; (2) loss calcolata solo per monitorare; init a 0 per la LR (convessa), piccoli valori casuali per reti neurali; stop a convergenza (norma del gradiente < $\epsilon$) o quando sale la loss su un held-out set; (3) SGD: passi rumorosi (choppy), ogni passo può peggiorare altri esempi; (4) batch: gradiente su tutto il dataset, direzione ottima ma costosa per passo; (5) mini-batch ($m$ = 512, 1024): media dei gradienti, vettorizzata e parallela, compromesso; $m = 1$ SGD, $m = N$ batch; (6) forma matriciale $\frac1m(\hat{\mathbf{y}}-\mathbf{y})^\top\mathbf{X}$.

</details>
