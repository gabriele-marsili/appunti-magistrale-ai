# L4 · Modelli linguistici n-gram

*N-gram Language Models* · 30/09/2026 · Claudio Gallicchio · lettura: J&M cap. 3, §3.1-3.5

[Versione interattiva sul sito](https://gabriele-marsili.github.io/appunti-magistrale-ai/anno-2/hlt/sito/#L4) · [Indice della dispensa](README.md)

Il primo modello linguistico vero e proprio del corso: l'**n-gram**. La probabilità di una frase si scompone con la **regola della catena**; l'**assunzione di Markov** accorcia la storia alle ultime $n-1$ parole; le probabilità si stimano contando (**MLE**, frequenze relative), con i simboli <s> e </s> ai confini di frase e i conti in **log probabilità**. Poi la valutazione: training, development e test set, contaminazione, **perplexity** (probabilità inversa normalizzata per la lunghezza, fattore di ramificazione medio pesato). Infine il **campionamento** mostra cosa ha imparato il modello: più contesto dà frasi più coerenti ma anche **overfitting** (Shakespeare), il genere del corpus conta (WSJ) e gli n-gram mai visti (**zeri**) rompono il modello, da cui lo smoothing della prossima lezione. Tutti i concetti (training/test, perplexity, sampling) valgono identici per i grandi modelli neurali.

## Indice

- [Apertura](#apertura)
- [Modelli linguistici](#modelli-linguistici)
- [N-gram: Markov e MLE](#n-gram-markov-e-mle)
- [Valutazione: training/test, perplexity](#valutazione-training-test-perplexity)
- [Campionamento e generalizzazione](#campionamento-e-generalizzazione)
- [Notebook](#notebook)
- [Studio ed esercizi](#studio-ed-esercizi)

## Apertura

<a id="p-1"></a>
**Slide 1 · Modelli linguistici n-gram** — Lezione 4 (Gallicchio, 30 settembre 2026): probabilità di sequenze di parole contando n-gram, come si valuta un modello linguistico (perplexity) e che cosa rivela il campionamento.

<a id="p-2"></a>

### Slide 2 · Indice della lezione

Quattro parti, che coprono le sezioni 3.1-3.5 del libro:

- **Modelli linguistici**: che cosa sono e perché predire la parola successiva (ripresa della [L1](L01-introduzione-al-corso.md#p-5)).
- **N-gram**: regola della catena, **assunzione di Markov** e stima a **massima verosimiglianza** (MLE) contando; esempi *I am Sam* e Berkeley Restaurant Project; log probabilità e modelli su larga scala.
- **Valutazione**: training, development e test set; la **perplexity**.
- **Campionamento e generalizzazione**: generare frasi dal modello, overfitting, dipendenza dal corpus, il problema degli zeri.

Lo smoothing e l'interpolazione (§3.6-3.7) sono la lezione successiva. Gli n-gram sono il modello più semplice, ma i concetti introdotti qui (training/test, perplexity, campionamento) sono esattamente quelli usati per gli LLM.

<a id="p-3"></a>

### Slide 3 · Riferimento: J&M capitolo 3, §3.1-3.5

Lettura principale: Jurafsky e Martin, *Speech and Language Processing*, 3a ed. (draft del 19 agosto 2026), **capitolo 3, N-gram Language Models, sezioni 3.1-3.5**: n-gram (3.1), training e test set (3.2), perplexity (3.3), campionamento (3.4), generalizzazione e overfitting (3.5). Il QR code porta al sito del libro, web.stanford.edu/~jurafsky/slp3/.

Le slide seguono il libro molto da vicino, spesso con le stesse frasi ed esempi: il capitolo è un ottimo ripasso. Tre esercizi della scheda (3, 4, 8) sono gli esercizi 3.1, 3.2 e 3.12 del libro. La slide 46 (zeri) anticipa l'inizio del §3.6.

## Modelli linguistici

<a id="p-4"></a>
**Slide 4 · Modelli linguistici** — Si riparte dalla definizione: un modello linguistico predice le parole che seguono.

<a id="p-5"></a>

### Slide 5 · Che cos'è un modello linguistico

Un **language model** (LM) è un modello di machine learning che **predice le parole successive**. Dopo *The water of Walden Pond is so beautifully ...* le parole plausibili (in verde nella slide) sono *blue, green, clear*; quelle improbabili (in rosso) *refrigerator, this*.

Due modi equivalenti di vederlo:

- **parola successiva**: una probabilità per ogni parola possibile, cioè una **distribuzione di probabilità sul vocabolario** ($\sum_{w\in V} P(w\mid h)=1$, come nella [scheda 5 della L1](L01-introduzione-al-corso.md#p-5));
- **sequenza intera**: una probabilità per ogni frase; *all of a sudden I notice three guys standing on the sidewalk* è molto più probabile della stessa frase con le parole rimescolate. Stesse parole, quindi un modello che guarda solo alle frequenze delle singole parole non distinguerebbe le due frasi: serve l'ordine.

Le due viste coincidono grazie alla regola della catena ([scheda 11](L04-modelli-linguistici-n-gram.md#p-11)). Per semplicità si parla di **parole**, ma in pratica i modelli lavorano su **token** come quelli di BPE ([L2](L02-parole-e-token.md#p-28)).

<a id="p-6"></a>

### Slide 6 · Perché predire le parole successive

- **Large language model**: si costruiscono *solo* addestrandoli a predire parole ([L1, scheda 7](L01-introduzione-al-corso.md#p-7)); da questo unico compito imparano moltissimo sulla lingua.
- **Grammatica e ortografia**: in *Their are two midterms*, *There are* è più probabile di *Their are*, quindi un LM suggerisce la correzione.
- **Riconoscimento del parlato**: *I will be back soonish* e *I will be bassoon dish* suonano quasi uguali; l'acustica non decide, la probabilità della sequenza sì.
- **Comunicazione aumentativa** (AAC, *augmentative and alternative communication*): chi non può parlare né usare i segni sceglie parole da un menu con lo sguardo o altri movimenti; la predizione mette nel menu le parole probabili e riduce la fatica.

In tutti i casi il LM fa da **giudice di plausibilità** tra alternative prodotte da un altro componente. Il modello più semplice è l'**n-gram**.

<a id="p-7"></a>

### Slide 7 · N-gram

Un **n-gram** è una sequenza di $n$ parole. Nella frase *The water of Walden Pond is so beautifully blue* (9 parole):

- **bigram** (2-gram): *The water, water of, of Walden, ..., beautifully blue*, in tutto 8;
- **trigram** (3-gram): *The water of, ..., so beautifully blue*, in tutto 7.

In generale una sequenza di $L$ parole contiene $L-n+1$ n-gram (sovrapposti). Con i simboli di confine <s> e </s> il conto cambia ([scheda 14](L04-modelli-linguistici-n-gram.md#p-14)).

**Ambiguità di terminologia**: «n-gram» indica anche il **modello probabilistico** che stima la probabilità di una parola date le $n-1$ precedenti, e quindi di intere sequenze. «Un modello bigram» = un modello che condiziona sulla sola parola precedente.

**Perché partire da qui**: la formalizzazione è semplicissima (contare e dividere) e permette di introdurre training/test set, perplexity, campionamento e interpolazione, che si ritrovano identici nei modelli neurali.

## N-gram: Markov e MLE

<a id="p-8"></a>
**Slide 8 · N-gram: probabilità dai conteggi** — Come si stimano le probabilità contando in un corpus, e perché serve un'approssimazione.

<a id="p-9"></a>

### Slide 9 · Probabilità di una parola data una storia

$P(w\mid h)$: probabilità della parola $w$ data la **storia** (contesto) $h$. Il modo più diretto di stimarla è la **frequenza relativa**:

$$P(w\mid h) = \frac{C(h\,w)}{C(h)}$$

«Tra tutte le volte che ho visto $h$, quante volte era seguita da $w$?» Per l'esempio della slide: $C(\text{The water of Walden Pond is so beautifully blue})$ diviso $C(\text{The water of Walden Pond is so beautifully})$, contati in un corpus molto grande.

**Perché non funziona**: nemmeno l'intero web basta. La lingua è **creativa**, frasi nuove si inventano continuamente, e una storia lunga compare pochissime volte o mai: il denominatore è 0 o molto piccolo, e la stima è indefinita o inaffidabile. Serve un modo più furbo, che si costruisce nelle prossime tre schede: regola della catena (esatta) più assunzione di Markov (approssimazione).

> **Approfondimento: Collegamento con la legge di Heaps**
>
> (Facoltativo.) Il motivo è lo stesso delle parole sconosciute della [L2, scheda 12](L02-parole-e-token.md#p-12): il numero di sequenze possibili cresce esponenzialmente con la lunghezza ($|V|^n$), mentre il corpus cresce solo linearmente. Già per le singole parole il vocabolario non si esaurisce mai; per le frasi intere quasi ogni frase lunga è nuova.

<a id="p-10"></a>

### Slide 10 · Notazione

- $P(\text{the})$ abbrevia $P(X_i = \text{the})$, dove $X_i$ è la **variabile aleatoria** della parola in posizione $i$.
- $w_{1:n}$: la sequenza di $n$ parole $w_1 \dots w_n$.
- $w_{1:n-1} = w_{&lt;n}$: tutte le parole prima di $w_n$, cioè la sua **storia**.
- $P(w_1, \dots, w_n)$: la **probabilità congiunta** dell'intera sequenza, cioè $P(X_1=w_1, \dots, X_n=w_n)$.

Attenzione alla doppia $n$: nel capitolo $n$ è spesso la lunghezza della sequenza, mentre l'ordine dell'n-gram si scrive con la $N$ maiuscola ([scheda 12](L04-modelli-linguistici-n-gram.md#p-12): $N=2$ bigram, $N=3$ trigram). Nella perplexity $N$ torna a essere il numero di token del test set ([scheda 30](L04-modelli-linguistici-n-gram.md#p-30)). La notazione $w_{&lt;t}$ è la stessa della [L1](L01-introduzione-al-corso.md#p-6).

<a id="p-11"></a>

### Slide 11 · La regola della catena

$$P(w_{1:n}) = P(w_1)P(w_2\mid w_1)P(w_3\mid w_{1:2})\cdots P(w_n\mid w_{1:n-1}) = \prod_{k=1}^{n} P(w_k\mid w_{1:k-1})$$

- **Scomposizione**: la probabilità congiunta è un **prodotto di probabilità condizionate**, ogni parola data tutte le precedenti. È un'identità esatta, conseguenza della definizione $P(A,B)=P(A)P(B\mid A)$ applicata ripetutamente; nessuna approssimazione.
- **Legame con l'autoregressione**: calcolare la probabilità di una sequenza e predire la parola successiva sono **lo stesso problema**. Chi sa fare l'uno sa fare l'altro: è la fattorizzazione dei modelli autoregressivi ([L1, scheda 6](L01-introduzione-al-corso.md#p-6)).
- **Ancora bloccati**: il fattore $P(w_n\mid w_{1:n-1})$ ha una storia lunga, che probabilmente non è mai stata vista: non si può contare ([scheda 9](L04-modelli-linguistici-n-gram.md#p-9)).

Esempio: $P(\text{the cat sat}) = P(\text{the})\,P(\text{cat}\mid\text{the})\,P(\text{sat}\mid\text{the cat})$.

<a id="p-12"></a>

### Slide 12 · L'assunzione di Markov

Idea: **approssimare la storia con le ultime poche parole**.

- **Bigram**: $P(w_n\mid w_{1:n-1}) \approx P(w_n\mid w_{n-1})$. $P(\text{blue}\mid\text{The water of Walden Pond is so beautifully})$ diventa $P(\text{blue}\mid\text{beautifully})$: la probabilità di una parola **dipende solo dalla precedente**.
- **N-gram**: $P(w_n\mid w_{1:n-1}) \approx P(w_n\mid w_{n-N+1:n-1})$, cioè si guardano $N-1$ parole indietro ($N=2$ bigram, $N=3$ trigram). I **modelli di Markov** predicono un'unità futura senza guardare troppo lontano nel passato.
- **Sequenza intera**: sostituendo nella regola della catena, $P(w_{1:n}) \approx \prod_{k=1}^{n} P(w_k\mid w_{k-1})$, un prodotto di probabilità bigram.

Il prezzo: il modello ignora tutto ciò che sta prima della finestra. Un bigram, predicendo *sat* in *the cat sat*, non sa che c'era *the*. Con $N$ più grande la finestra cresce, ma i conteggi diventano più scarsi ([scheda 43](L04-modelli-linguistici-n-gram.md#p-43)): è il compromesso centrale degli n-gram.

> **Da saper fare: Scrivere la probabilità di una frase con catena, bigram e trigram**
>
> Per <s> the cat sat </s>:
>
> - catena (esatta): $P(\text{the}\mid\text{&lt;s&gt;})\,P(\text{cat}\mid\text{&lt;s&gt; the})\,P(\text{sat}\mid\text{&lt;s&gt; the cat})\,P(\text{&lt;/s&gt;}\mid\text{&lt;s&gt; the cat sat})$;
> - bigram: $P(\text{the}\mid\text{&lt;s&gt;})\,P(\text{cat}\mid\text{the})\,P(\text{sat}\mid\text{cat})\,P(\text{&lt;/s&gt;}\mid\text{sat})$;
> - trigram (due <s>): $P(\text{the}\mid\text{&lt;s&gt; &lt;s&gt;})\,P(\text{cat}\mid\text{&lt;s&gt; the})\,P(\text{sat}\mid\text{the cat})\,P(\text{&lt;/s&gt;}\mid\text{cat sat})$.
>
> Sempre 4 fattori: uno per ogni parola più uno per </s>, mai uno per <s>. Esercizio 1 della scheda.

<a id="p-13"></a>

### Slide 13 · Stima a massima verosimiglianza (MLE)

Si prendono i conteggi da un corpus e si **normalizzano**, in modo che stiano tra 0 e 1 e sommino a 1:

$$P(w_n\mid w_{n-1}) = \frac{C(w_{n-1}w_n)}{C(w_{n-1})}\qquad P(w_n\mid w_{n-N+1:n-1}) = \frac{C(w_{n-N+1:n-1}\,w_n)}{C(w_{n-N+1:n-1})}$$

- **Frequenza relativa**: conteggio del bigram diviso conteggio della prima parola. Il denominatore «giusto» sarebbe $\sum_w C(w_{n-1}w)$, ma tutti i bigram che iniziano con $w_{n-1}$ sommano al conteggio unigram di $w_{n-1}$ (ogni occorrenza di una parola è seguita da esattamente una parola, grazie a </s> anche l'ultima della frase). Quindi le probabilità di ogni riga sommano a 1.
- **Massima verosimiglianza**: è la stima che rende **più probabile il corpus di training**, cioè massimizza $P(T\mid M)$. Esempio: *Chinese* compare 400 volte in un milione di parole, $P(\text{Chinese}) = 400/1.000.000 = 0{,}0004$: tra tutti i valori possibili è quello che rende più verosimili 400 occorrenze su un milione.
- **Non è la stima migliore**: in un altro corpus o contesto *Chinese* può essere rarissima. La MLE si adatta al training set, e dà probabilità 0 a tutto ciò che non ha visto ([scheda 46](L04-modelli-linguistici-n-gram.md#p-46)).

> **Approfondimento: Perché la frequenza relativa massimizza la verosimiglianza**
>
> (Facoltativo, derivazione standard.) Con $k$ occorrenze di una parola su $M$ parole, la verosimiglianza è $L(p) = p^k(1-p)^{M-k}$. Derivando il logaritmo: $\frac{k}{p} - \frac{M-k}{1-p} = 0 \Rightarrow p = k/M$. Con più parole (distribuzione categoriale) si massimizza $\sum_w C(w)\log p_w$ con il vincolo $\sum_w p_w = 1$; il moltiplicatore di Lagrange dà $p_w = C(w)/\sum_v C(v)$. Per i bigram vale lo stesso riga per riga, con il contesto fissato.

<a id="p-14"></a>

### Slide 14 · Un mini-corpus: I am Sam

Tre frasi, ciascuna con un **simbolo di inizio** <s> e un **simbolo di fine** </s>:

```
<s> I am Sam </s>
<s> Sam I am </s>
<s> I do not like green eggs and ham </s>
```

- **<s>** dà alla prima parola il suo contesto bigram: $P(\text{I}\mid\text{&lt;s&gt;}) = 2/3$, perché tre frasi iniziano e due con *I*. Senza <s> la prima parola richiederebbe una probabilità unigram a parte.
- **</s>** rende il modello una **vera distribuzione di probabilità sulle frasi**. Senza di esso, le probabilità sommerebbero a 1 **separatamente per ogni lunghezza**: tutte le frasi di una parola sommano a 1, tutte quelle di due parole a 1, e così via, con somma totale infinita. Con </s> il modello decide anche *quando fermarsi*, e la massa si divide tra lunghezze diverse.

Verificato con il codice: con </s> la somma delle probabilità di tutte le frasi generabili (fino a 200 parole) vale 1,000; togliendo </s> e rinormalizzando le righe, le frasi di lunghezza 1, 2, 3 sommano ciascuna a 1. La lente nella slide rimanda alla nota a piè di pagina del libro (esercizio 3.5).

> **Approfondimento: Perché la somma vale 1 con </s>**
>
> (Facoltativo.) Ogni frase corrisponde a un cammino che parte da <s> e termina quando esce </s>; la sua probabilità è il prodotto delle probabilità di transizione. Poiché ogni riga della tabella somma a 1, la massa totale dei cammini che terminano entro $L$ passi più quella di quelli ancora «in corsa» vale sempre 1; se da ogni parola si può raggiungere </s>, la massa in corsa tende a 0 e la somma sulle frasi finite tende a 1. Senza </s> non c'è terminazione: si può solo fissare la lunghezza a priori, e si ottiene una distribuzione diversa per ogni lunghezza.

<a id="p-15"></a>

### Slide 15 · Probabilità bigram di I am Sam

Le sei probabilità della slide, **contare e dividere**:

| bigram | conteggio | contesto | P |
| --- | --- | --- | --- |
| $P(\text{I}\mid\text{&lt;s&gt;})$ | 2 | C(<s>) = 3 | 2/3 = 0,67 |
| $P(\text{Sam}\mid\text{&lt;s&gt;})$ | 1 | 3 | 1/3 = 0,33 |
| $P(\text{am}\mid\text{I})$ | 2 | C(I) = 3 | 2/3 = 0,67 |
| $P(\text{do}\mid\text{I})$ | 1 | 3 | 1/3 = 0,33 |
| $P(\text{Sam}\mid\text{am})$ | 1 | C(am) = 2 | 1/2 = 0,5 |
| $P(\text{&lt;/s&gt;}\mid\text{Sam})$ | 1 | C(Sam) = 2 | 1/2 = 0,5 |

*I* compare tre volte, seguita due volte da *am* e una da *do*; *am* due volte, seguita una volta da *Sam* e una da </s>. Tutti i valori sono corretti (ricalcolati con `fractions`). Il modello completo ha anche $P(\text{&lt;/s&gt;}\mid\text{am}) = 1/2$, $P(\text{I}\mid\text{Sam}) = 1/2$ e probabilità 1 per la catena deterministica *do → not → like → green → eggs → and → ham → </s>*. Ogni riga somma a 1.

Conseguenza: $P(\text{&lt;s&gt; I am Sam &lt;/s&gt;}) = \frac23\cdot\frac23\cdot\frac12\cdot\frac12 = \frac19$, ma $P(\text{&lt;s&gt; I am &lt;/s&gt;}) = \frac23\cdot\frac23\cdot\frac12 = \frac29$, più probabile pur non essendo nel corpus: il modello ricombina i bigram visti.

> **Da saper fare: Costruire la tabella bigram di un mini-corpus**
>
> 1. Aggiungi <s> e </s> a ogni frase.
> 2. Per ogni parola $u$ (e per <s>), elenca le parole che la seguono e quante volte.
> 3. Dividi per il numero di occorrenze di $u$ come contesto (= numero di bigram che iniziano con $u$).
> 4. Controllo: ogni riga somma a 1; <s> non compare mai come parola predetta, </s> mai come contesto.
>
> Errore tipico: dividere per il numero totale di parole del corpus (quella è la probabilità unigram). Esercizio 2 della scheda.

<a id="p-16"></a>

### Slide 16 · Il Berkeley Restaurant Project

Un corpus reale ma piccolo: il **Berkeley Restaurant Project** (Jurafsky et al. 1994), un sistema di dialogo «del secolo scorso» che rispondeva a domande su un database di ristoranti di Berkeley, California. Esempi di richieste degli utenti:

- *can you tell me about any good cantonese restaurants close by*
- *tell me about chez panisse*
- *i'm looking for a good place to eat breakfast*
- *when is caffe venezia open during the day*

**Il corpus**: 9332 richieste (frasi), **normalizzate** in minuscolo e senza punteggiatura (case folding, [L3](L03-elaborazione-del-testo.md#p-25)); vocabolario $V = 1446$ tipi.

**Cosa si calcola**: conteggi e probabilità bigram per otto parole scelte perché «stanno bene insieme»: *i, want, to, eat, chinese, food, lunch, spend*. Sono solo 8 righe e 8 colonne di una tabella che in realtà è $1446\times1446$ (più <s> e </s>).

<a id="p-17"></a>

### Slide 17 · Conteggi bigram

La tabella dei conteggi (Fig. 3.1 del libro): **righe** = prima parola del bigram, **colonne** = parola che segue. La cella (i, want) è il numero di volte in cui *want* ha seguito *i*. Gli zeri sono in grigio nella slide.

|  | i | want | to | eat | chinese | food | lunch | spend |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| i | 5 | 827 | 0 | 9 | 0 | 0 | 0 | 2 |
| want | 2 | 0 | 608 | 1 | 6 | 6 | 5 | 1 |
| to | 2 | 0 | 4 | 686 | 2 | 0 | 6 | 211 |
| eat | 0 | 0 | 2 | 0 | 16 | 2 | 42 | 0 |
| chinese | 1 | 0 | 0 | 0 | 0 | 82 | 1 | 0 |
| food | 15 | 0 | 15 | 0 | 1 | 4 | 0 | 0 |
| lunch | 2 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| spend | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |

Si legge per righe: dopo *want* viene quasi sempre *to* (608); dopo *to* soprattutto *eat* (686) e *spend* (211); dopo *chinese* quasi solo *food* (82). La tabella non è simmetrica: C(i want) = 827 ma C(want i) = 2, perché l'ordine conta.

<a id="p-18"></a>

### Slide 18 · Conteggi bigram: sparsità

Stessa tabella, evidenziata la cella **C(i want) = 827**: *want* ha seguito *i* 827 volte.

La slide dice che **la maggior parte delle celle è zero** (in realtà sono esattamente la metà, riquadro sotto), anche se le otto parole sono state scelte per essere coerenti tra loro. Un insieme casuale di otto parole sarebbe ancora più sparso. Molti zeri sono «giusti» (*want want* non si dice), altri sono solo sfortuna del corpus (*eat food*? *spend lunch*?).

È la prima comparsa della **sparsità**: la tabella completa ha $1446^2 \approx 2{,}1$ milioni di celle, e un corpus di 9332 frasi brevi ne può riempire solo una piccola frazione. Il problema peggiora con $N$ ([scheda 43](L04-modelli-linguistici-n-gram.md#p-43)) ed è la ragione dello smoothing ([scheda 46](L04-modelli-linguistici-n-gram.md#p-46)).

> **Attenzione (errore nelle slide): Gli zeri sono la metà delle celle, non la maggioranza**
>
> La slide (come il libro, «the majority of the values are zero») afferma che la maggior parte delle celle è zero. Contando sulla tabella: zeri per riga i 4, want 1, to 2, eat 4, chinese 5, food 4, lunch 6, spend 6, totale **32 su 64, esattamente la metà**; le celle non nulle sono anch'esse 32. Versione corretta: «metà delle celle è zero, anche se le otto parole sono state scelte per essere coerenti». Il messaggio sulla sparsità resta valido: nella tabella completa $1446\times1446$ la frazione di zeri è enormemente più alta. Verificato contando in Python.

<a id="p-19"></a>

### Slide 19 · Probabilità bigram

Ogni cella dei conteggi si divide per il **conteggio unigram della parola di riga**. Conteggi unigram delle otto parole:

| i | want | to | eat | chinese | food | lunch | spend |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2533 | 927 | 2417 | 746 | 158 | 1093 | 341 | 278 |

Probabilità risultanti (come nella slide, due cifre significative):

|  | i | want | to | eat | chinese | food | lunch | spend |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| i | 0.002 | 0.33 | 0 | 0.0036 | 0 | 0 | 0 | 0.00079 |
| want | 0.0022 | 0 | 0.66 | 0.0011 | 0.0065 | 0.0065 | 0.0054 | 0.0011 |
| to | 0.00083 | 0 | 0.0017 | 0.28 | 0.00083 | 0 | 0.0025 | 0.087 |
| eat | 0 | 0 | 0.0027 | 0 | 0.021 | 0.0027 | 0.056 | 0 |
| chinese | 0.0063 | 0 | 0 | 0 | 0 | 0.52 | 0.0063 | 0 |
| food | 0.014 | 0 | 0.014 | 0 | 0.00092 | 0.0037 | 0 | 0 |
| lunch | 0.0059 | 0 | 0 | 0 | 0 | 0.0029 | 0 | 0 |
| spend | 0.0036 | 0 | 0.0036 | 0 | 0 | 0 | 0 | 0 |

Evidenziato: $P(\text{want}\mid\text{i}) = 827/2533 = 0{,}3265 \approx 0{,}33$. **La riga di *i* somma a 1 su tutto il vocabolario di 1446 parole** (più </s>): le otto colonne mostrate ne sono solo una parte. Sulle otto colonne la riga *i* somma 843/2533 = 0,33, la riga *want* 629/927 = 0,68, la riga *spend* appena 2/278 = 0,007: il resto della massa va a parole non mostrate (*spend money*, *spend the*...).

Ho ricalcolato tutte le 64 celle dai conteggi: 63 coincidono con l'arrotondamento a due cifre significative; una no (riquadro sotto). La tabella della scheda esercizi (esercizio 4) è identica a quella della slide.

> **Attenzione (errore nelle slide): Cella food → chinese: 0,00091, non 0,00092**
>
> La slide (come la Fig. 3.2 del libro) riporta $P(\text{chinese}\mid\text{food}) = 0{,}00092$. Dai dati della slide stessa: $C(\text{food chinese}) = 1$ e $C(\text{food}) = 1093$, quindi $1/1093 = 0{,}000915$, che arrotondato a due cifre significative è **0,00091**. Differenza trascurabile (probabilmente un arrotondamento fatto in due passi, 0,000915 → 0,00092), ma è l'unica cella su 64 non coerente con i conteggi; tutte le altre coincidono. Verificato ricalcolando la tabella cella per cella in Python.

> **Da saper fare: Dalla tabella dei conteggi a quella delle probabilità**
>
> $P(w\mid u) = C(u\,w)/C(u)$, dove $C(u)$ è il conteggio unigram della riga, **non** la somma della riga mostrata (che copre solo 8 colonne su 1446). Esempi: $P(\text{to}\mid\text{want}) = 608/927 = 0{,}656 \approx 0{,}66$; $P(\text{eat}\mid\text{to}) = 686/2417 = 0{,}284 \approx 0{,}28$; $P(\text{food}\mid\text{chinese}) = 82/158 = 0{,}519 \approx 0{,}52$; $P(\text{lunch}\mid\text{eat}) = 42/746 = 0{,}056$.

<a id="p-20"></a>

### Slide 20 · La probabilità di una frase

**I want English food**: con <s> e </s> la frase ha cinque bigram, e la probabilità è il prodotto delle cinque probabilità bigram:

$$\begin{aligned}P(\text{&lt;s&gt; i want english food &lt;/s&gt;}) &= P(\text{i}\mid\text{&lt;s&gt;})\,P(\text{want}\mid\text{i})\,P(\text{english}\mid\text{want})\,P(\text{food}\mid\text{english})\,P(\text{&lt;/s&gt;}\mid\text{food})\\ &= 0{,}25\times0{,}33\times0{,}0011\times0{,}5\times0{,}68 = 0{,}000031\end{aligned}$$

Verificato: il prodotto vale $3{,}0855\cdot10^{-5}$, cioè 0,000031. Usando il valore non arrotondato $827/2533$ al posto di 0,33 si ottiene $3{,}05\cdot10^{-5}$: stesso ordine, l'arrotondamento non cambia nulla.

Quattro dei cinque fattori vengono da «altre probabilità utili» dello stesso corpus: la slide nomina solo *english* e *food|english*, ma nemmeno $P(\text{i}\mid\text{&lt;s&gt;}) = 0{,}25$ e $P(\text{&lt;/s&gt;}\mid\text{food}) = 0{,}68$ sono nella tabella (che non ha né la riga <s> né la colonna </s>); solo $P(\text{want}\mid\text{i}) = 0{,}33$ viene dalla tabella.

**Esercizio della slide**, *i want chinese food*: $0{,}25\times0{,}33\times0{,}0065\times0{,}52\times0{,}68 = 0{,}00019$ (esattamente $1{,}896\cdot10^{-4}$), circa **6,1 volte** più probabile della frase con *english*: il rapporto è $\frac{0{,}0065\times0{,}52}{0{,}0011\times0{,}5} = 6{,}15$, perché i fattori comuni si semplificano.

> **Da saper fare: Calcolare la probabilità di una frase con un modello bigram**
>
> 1. Aggiungi <s> e </s>.
> 2. Elenca i bigram consecutivi: una frase di $k$ parole ne ha $k+1$.
> 3. Moltiplica le probabilità (o somma i logaritmi, [scheda 22](L04-modelli-linguistici-n-gram.md#p-22)).
> 4. Se anche un solo bigram ha probabilità 0, la frase ha probabilità 0.
>
> Per confrontare due frasi che differiscono in una parola basta il rapporto dei fattori che cambiano. Esercizio 4 della scheda.

<a id="p-21"></a>

### Slide 21 · Che cosa catturano le statistiche bigram

Tre riquadri colorati, tre tipi di conoscenza codificata nelle probabilità:

- **Sintassi** (blu): dopo *eat* viene di solito un nome o un aggettivo; dopo *to* di solito un verbo. $P(\text{eat}\mid\text{to}) = 0{,}28$, mentre $P(\text{food}\mid\text{to}) = 0$: un nome subito dopo *to* infinitivo non capita.
- **Il compito** (verde): le frasi rivolte a un assistente personale iniziano spesso con *I*, $P(\text{i}\mid\text{&lt;s&gt;}) = 0{,}25$: un quarto delle richieste. In un romanzo sarebbe molto meno.
- **Cultura** (rosso): chi usa il sistema cerca più spesso cibo cinese che inglese, $P(\text{chinese}\mid\text{want}) = 0{,}0065$ contro $P(\text{english}\mid\text{want}) = 0{,}0011$ (circa 6 volte).

Conclusione della slide: le probabilità codificano fatti sulla **lingua**, sul **compito** e sul **corpus di training**. Nessuna di queste conoscenze è stata inserita a mano: emerge dal contare. È, in piccolo, quello che fanno gli LLM ([L1](L01-introduzione-al-corso.md#p-7)), ed è anche il motivo per cui il modello eredita i bias del corpus.

<a id="p-22"></a>

### Slide 22 · Log probabilità

$$p_1\times p_2\times p_3\times p_4 = \exp(\log p_1+\log p_2+\log p_3+\log p_4)$$

- **Underflow**: le probabilità sono al massimo 1; più se ne moltiplicano, più il prodotto è piccolo, finché non è più rappresentabile in virgola mobile e diventa 0.
- **Sommare, non moltiplicare**: sommare nello spazio dei log equivale a moltiplicare nello spazio lineare. Le probabilità dei LM si **memorizzano e si calcolano sempre come log probabilità** e si riconvertono con $\exp$ solo quando serve riportare una probabilità.
- **Quale logaritmo**: $\log$ senza base indica il **logaritmo naturale** $\ln$. La base non cambia il confronto tra modelli, purché $\log$ ed $\exp$ (o $2^x$) siano coerenti.

Esempio: per *i want english food*, $\ln 0{,}25 + \ln 0{,}33 + \ln 0{,}0011 + \ln 0{,}5 + \ln 0{,}68 = -1{,}386 - 1{,}109 - 6{,}812 - 0{,}693 - 0{,}386 = -10{,}386$, ed $e^{-10{,}386} = 3{,}09\cdot10^{-5}$. Una probabilità 0 ha log $-\infty$: basta un bigram mai visto per affondare tutta la somma.

> **Da saper fare: Quando arriva l'underflow**
>
> Con probabilità tutte circa 0,01, una frase di 10 parole ha probabilità $10^{-20}$, log naturale $10\times(-4{,}605) = -46{,}05$. Il più piccolo double normale è circa $2{,}2\cdot10^{-308}$: $0{,}01^n &lt; 10^{-308}$ da $n = 155$ parole; grazie ai numeri subnormali il prodotto diventa esattamente 0 in Python a $n = 162$ (verificato). La somma dei log invece vale $-4{,}605\,n$: per 1000 parole $-4605$, nessun problema. Esercizio 5 della scheda.

<a id="p-23"></a>

### Slide 23 · Contesto più lungo e scala

- **Trigram, 4-gram, 5-gram**: con abbastanza dati si condiziona su due, tre o quattro parole precedenti. All'inizio della frase servono **pseudo-parole** in più: per un trigram $P(\text{I}\mid\text{&lt;s&gt;&lt;s&gt;})$, cioè $N-1$ simboli <s>. Di </s> ne basta uno: la frase finisce la prima volta che esce.
- **Grandi dataset di n-gram**: COCA (Corpus of Contemporary American English), il milione di n-gram più frequenti di un corpus curato di 1 miliardo di parole di inglese americano; **Google Web 5-grams**, da 1 trilione (*trillion*, $10^{12}$) di parole di testo web; **Google Books Ngrams**, 800 miliardi di token in otto lingue (cinese, inglese, francese, tedesco, ebraico, italiano, russo, spagnolo, secondo il libro).
- **Infini-gram** (Liu et al. 2024): n-gram di **lunghezza qualsiasi**, calcolati al momento dell'inferenza su corpora di 5 trilioni di token, usando **suffix array** invece di enormi tabelle di conteggi precalcolate. Per ogni contesto si cerca il suffisso più lungo che compare nel corpus.
- **Efficienza**: probabilità quantizzate a 4-8 bit (invece di float da 8 byte); parole in memoria come hash da 64 bit (le stringhe restano su disco); *reverse trie*; **pruning** degli n-gram rari (soglia sui conteggi o criteri di entropia); toolkit come **KenLM** costruiscono le tabelle in pochi passaggi sul corpus (array ordinati e merge sort).

<a id="p-24"></a>
**Slide 24 · Pausa** — Pausa di 10 minuti; dopo la pausa: valutazione dei modelli linguistici e campionamento.

## Valutazione: training/test, perplexity

<a id="p-25"></a>
**Slide 25 · Valutare i modelli linguistici** — Come si decide se un modello linguistico è migliore di un altro: dati di training e test, poi la perplexity.

<a id="p-26"></a>

### Slide 26 · Valutazione estrinseca e intrinseca

- **Estrinseca** (riquadro blu): si inserisce il modello in un'applicazione e si misura quanto migliora l'applicazione (valutazione *end-to-end*). Esempio: si fa girare il riconoscitore vocale o il traduttore due volte, una con ciascun language model, e si vede quale dà la trascrizione più accurata (per esempio con il WER, [L3](L03-elaborazione-del-testo.md#p-52)). È l'**unico modo** per sapere se un miglioramento aiuta davvero il compito, ma è spesso **molto costosa**.
- **Intrinseca** (riquadro verde): misura la qualità del modello **indipendentemente da qualsiasi applicazione**. È veloce, e serve a valutare rapidamente possibili miglioramenti. La metrica intrinseca standard è la **perplexity**, sia per gli n-gram sia per i grandi modelli neurali.

Messaggio finale: quando possibile, un miglioramento intrinseco va **confermato** da una valutazione end-to-end su un compito reale. Il libro (§3.3) precisa che un calo di perplexity non garantisce un miglioramento nel compito, anche se di solito sono correlati.

<a id="p-27"></a>

### Slide 27 · Training, development e test set

Per valutare qualunque modello di machine learning servono almeno tre insiemi distinti:

- **Training set**: i dati con cui si imparano i parametri. Per un n-gram è il corpus da cui si prendono i conteggi.
- **Development set** (devset, *held-out*): dati tenuti da parte per tutti i test fatti *durante* lo sviluppo: confrontare modifiche, scegliere iperparametri (per esempio l'ordine $N$). Deve venire dallo stesso tipo di testo del test set, perché il suo scopo è prevedere come andrà sul test.
- **Test set**: dati tenuti da parte, **senza sovrapposizione** con il training set, usati **una volta sola, alla fine**. Dà una stima non distorta (*unbiased*) di quanto il modello generalizza a dati nuovi.

Frase finale: un modello che cattura perfettamente i dati di training ma va malissimo su qualunque altro dato non serve a nulla. È la definizione di **overfitting**, che il campionamento farà vedere ([scheda 43](L04-modelli-linguistici-n-gram.md#p-43)).

<a id="p-28"></a>

### Slide 28 · Come scegliere training e test set

- **Rispecchiare il compito**: per il riconoscimento vocale di lezioni di chimica, il test set è fatto di lezioni di chimica.
- **Uso generale**: test set estratto da una grande varietà di testi, non da un solo documento o un solo autore; dividere i testi raccolti in training e test **con cura**.
- **Mai allenare sul test set** (*never ever*): se una frase del test è anche nel training, la sua probabilità è artificialmente alta. Si chiama **data contamination** e distorce ogni metrica basata sulla probabilità, perplexity in testa. Per gli LLM è un problema serio, perché i benchmark finiscono sul web ([L1, scheda 70](L01-introduzione-al-corso.md#p-70)).
- **Testare una volta**: provare il test set molte volte dopo modifiche diverse **adatta implicitamente** il modello al test (si tengono le modifiche che sembrano funzionare). Si sviluppa sul devset e si usa il test set una volta, quando il modello è pronto.
- **Quanto grande**: il più grande possibile, perché un test piccolo può essere per caso non rappresentativo; almeno abbastanza grande da misurare una differenza **statisticamente significativa** tra due modelli. Il compromesso: ogni frase messa nel test è tolta al training.

> **Da saper fare: Riconoscere gli errori di protocollo**
>
> Tre errori tipici (esercizio 6 della scheda): (a) scegliere tra bigram, trigram e 4-gram guardando la perplexity sul **test** set: è tuning sul test, va fatto sul devset; (b) test set estratto a caso dalle stesse frasi o dagli stessi articoli del training: contaminazione o stima troppo ottimistica, meglio separare per documento; (c) test su testo di un altro genere (giornali) per un compito sulle lezioni di chimica: il test non rispecchia il compito.

<a id="p-29"></a>

### Slide 29 · Quale modello è migliore

Il criterio: **è migliore il modello che assegna probabilità più alta al test set**.

- **Meno sorpreso**: un modello migliore predice il test set più accuratamente, cioè assegna probabilità più alta a ogni parola quando compare. Un modello perfetto indovinerebbe ogni parola successiva con probabilità 1 (e 0 a tutte le altre).
- **Non la probabilità grezza**: la probabilità di un test set dipende dalla lunghezza, e diminuisce per testi più lunghi (ogni parola aggiunge un fattore $\le 1$). Per confrontare testi di lunghezze diverse serve una metrica **per parola**, normalizzata per la lunghezza.

Quella metrica è la **perplexity**, funzione della probabilità del test set. Esempio: con il modello *I am Sam*, $P(\text{I am Sam}) = 1/9$ e $P(\text{I am Sam, Sam I am}) = 1/162$: la seconda è più piccola solo perché il testo è più lungo; per token le due sono quasi uguali (perplexity 1,73 e 1,89, [scheda 31](L04-modelli-linguistici-n-gram.md#p-31)).

<a id="p-30"></a>

### Slide 30 · Perplexity

$$\text{perplexity}(W) = P(w_1w_2\dots w_N)^{-\frac{1}{N}} = \sqrt[N]{\frac{1}{P(w_1w_2\dots w_N)}}$$

- **Probabilità inversa**: uno diviso la probabilità del test set $W = w_1\dots w_N$.
- **Normalizzata per la lunghezza**: radice $N$-esima, con $N$ il numero di parole (token) del test set; per questo si parla di perplexity **per parola** o **per token**. Abbreviata PP o PPL.
- **Più bassa è meglio**: più alta la probabilità del test set, più bassa la perplexity. Minimizzare la perplexity equivale a massimizzare la probabilità del test set (la funzione $x\mapsto x^{-1/N}$ è decrescente).
- **Perché l'inversa**: viene dalla definizione originale di perplexity in teoria dell'informazione (entropia incrociata, §3.7 del libro, prossima lezione).

Frase finale: la perplexity è funzione **sia del testo sia del modello**; su un testo fissato confronta modelli. Non ha senso confrontare perplexity calcolate su test set diversi.

In pratica si calcola in log: $\text{PP}(W) = \exp\!\left(-\frac1N\sum_{i=1}^N \ln P(w_i\mid w_{&lt;i})\right)$, cioè l'esponenziale della log-verosimiglianza media negativa per token (la stessa quantità della loss di pretraining, [L1](L01-introduzione-al-corso.md#p-57)).

> **Da saper fare: Calcolare una perplexity a mano**
>
> 1. Calcola la probabilità del test set (prodotto dei fattori, oppure somma dei log).
> 2. Conta $N$: tutti i token predetti, cioè le parole più un </s> per frase; <s> non si conta ([scheda 31](L04-modelli-linguistici-n-gram.md#p-31)).
> 3. $\text{PP} = P^{-1/N}$, oppure $\exp(-\frac1N\sum\ln p_i)$.
>
> Controllo di buon senso: $\text{PP}\ge 1$ sempre, e $\text{PP}=1$ solo se ogni token ha probabilità 1. Un modello uniforme su $|V|$ parole ha $\text{PP} = |V|$.

<a id="p-31"></a>

### Slide 31 · Perplexity di un modello unigram e bigram

Con la regola della catena la probabilità del test set si espande in fattori condizionati:

$$\text{PP}(W) = \sqrt[N]{\prod_{i=1}^{N}\frac{1}{P(w_i\mid w_1\dots w_{i-1})}}$$

- **Unigram**: $\text{PP}(W) = \sqrt[N]{\prod_{i=1}^{N}\frac{1}{P(w_i)}}$, la **media geometrica** (radice $N$-esima di un prodotto di $N$ numeri) delle probabilità unigram inverse.
- **Bigram**: $\text{PP}(W) = \sqrt[N]{\prod_{i=1}^{N}\frac{1}{P(w_i\mid w_{i-1})}}$, media geometrica delle probabilità bigram inverse.

**Dettagli di conteggio**: $W$ è **l'intero test set**, attraverso i confini di frase (non una media delle perplexity delle singole frasi). Se il vocabolario ha <s> e </s>, li si include nelle probabilità e si conta **un token per frase** in $N$: il simbolo di fine, **non** quello di inizio. Motivo (nota del libro): </s> è un evento vero che il modello deve predire, mentre <s> segue </s> con probabilità quasi 1 e non viene predetto; contarlo gonfierebbe $N$ con una transizione finta.

Esempio con il modello *I am Sam*: test <s> I am Sam </s>, $P = 1/9$, $N = 4$ (I, am, Sam, </s>), $\text{PP} = 9^{1/4} = \sqrt3 = 1{,}732$. Test di due frasi <s> I am Sam </s> <s> Sam I am </s>: $P = \frac19\cdot\frac1{18} = \frac1{162}$, $N = 8$, $\text{PP} = 162^{1/8} = 1{,}889$. Contando anche <s> ($N=10$) verrebbe $162^{1/10} = 1{,}663$: numero diverso e non confrontabile.

<a id="p-32"></a>

### Slide 32 · Perplexity più bassa, predittore migliore

|  | Unigram | Bigram | Trigram |
| --- | --- | --- | --- |
| Perplexity | 962 | 170 | 109 |

- **L'esperimento** (libro §3.3): modelli unigram, bigram e trigram addestrati su **38 milioni di parole** del Wall Street Journal; perplexity su un test set WSJ di **1,5 milioni di parole**. I numeri coincidono con quelli del libro.
- **Più contesto**: il trigram ha un'idea migliore di quali parole vengono dopo e assegna loro probabilità più alta; è **meno sorpreso**, 109 contro 962 dell'unigram. Il guadagno maggiore è il primo passo (da 962 a 170, fattore 5,7); da bigram a trigram il fattore è 1,56: rendimenti decrescenti.
- **Due condizioni**: il modello non deve sapere nulla del test set, altrimenti la perplexity è artificialmente bassa (contaminazione); due modelli sono confrontabili **solo con vocabolari identici**.

Perché il vocabolario: un modello con vocabolario più piccolo (per esempio con tutte le parole rare mappate su un unico token UNK) predice più facilmente e ha perplexity più bassa senza essere migliore. Per lo stesso motivo non si confrontano perplexity di LLM con tokenizer diversi.

> **Da saper fare: Leggere una perplexity come «numero di scelte»**
>
> Perplexity 109 significa che, in media geometrica, il trigram è incerto come se dovesse scegliere uniformemente tra 109 parole a ogni passo; l'unigram come tra 962. Equivalente: probabilità media geometrica per parola $1/109 \approx 0{,}0092$ contro $1/962 \approx 0{,}0010$. È l'interpretazione del fattore di ramificazione pesato ([scheda 35](L04-modelli-linguistici-n-gram.md#p-35)).

<a id="p-33"></a>

### Slide 33 · Perplexity come fattore di ramificazione medio pesato: il linguaggio

Un linguaggio in miniatura: $L = \{\text{red}, \text{blue}, \text{green}\}$, non probabilistico: qualunque colore può seguire qualunque parola.

Il **fattore di ramificazione** (*branching factor*) è il numero di possibili parole successive che possono seguire una qualunque parola: qui **3**.

Test set usato nelle schede seguenti: $T = $ *red red red red blue* (5 token; in questo esempio non ci sono <s> e </s>, quindi $N = 5$). L'idea da mostrare: la perplexity è un fattore di ramificazione «pesato» dalle probabilità, uguale a quello vero quando le scelte sono equiprobabili e più piccolo quando alcune sono prevedibili.

<a id="p-34"></a>

### Slide 34 · Modello A: probabilità uguali

Il modello **A** è addestrato su conteggi uguali dei tre colori: ognuno ha probabilità 1/3.

$$\text{PP}_A(T) = P_A(\text{red red red red blue})^{-\frac15} = \left(\left(\tfrac13\right)^5\right)^{-\frac15} = \left(\tfrac13\right)^{-1} = 3$$

La perplexity di A su $T$ è **esattamente il fattore di ramificazione**, 3. Non dipende dal test set: qualunque sequenza di colori ha perplexity 3 sotto A, perché ogni token ha probabilità 1/3. In generale un modello uniforme su $k$ scelte ha perplexity $k$.

<a id="p-35"></a>

### Slide 35 · Modello B: il rosso è probabile

Il modello **B** ha visto soprattutto rosso: $P(\text{red}) = 0{,}8$, $P(\text{green}) = 0{,}1$, $P(\text{blue}) = 0{,}1$.

$$\text{PP}_B(T) = P_B(\text{red red red red blue})^{-1/5} = 0{,}04096^{-\frac15} = 0{,}527^{-1} = 1{,}89$$

Verifica: $0{,}8^4\times0{,}1 = 0{,}04096$; $0{,}04096^{1/5} = 0{,}5278$; $1/0{,}5278 = 1{,}8946 \approx 1{,}89$. (Il passaggio intermedio della slide tronca 0,5278 a 0,527; con 0,527 si otterrebbe 1,898, ma il risultato 1,89 è quello corretto.)

La maggior parte delle volte il colore successivo è rosso, quindi prevedibile: il test set è più probabile e la perplexity più bassa. Il **fattore di ramificazione** è sempre 3 (tre colori possibili), ma il **fattore di ramificazione medio pesato** è più piccolo: in media è come scegliere tra 1,89 alternative.

La perplexity misura l'accordo tra modello e test. Il modello D con $P(\text{blue}) = 0{,}8$ e $P(\text{red}) = 0{,}1$ darebbe su $T$ perplexity $(0{,}1^4\times0{,}8)^{-1/5} = 6{,}60$, più del fattore di ramificazione: un modello sbilanciato nella direzione sbagliata è peggio di quello uniforme (esercizio 9).

> **Da saper fare: Perplexity di un modello unigram su una sequenza**
>
> $\text{PP} = \left(\prod_i p_i\right)^{-1/N}$. Con $c_w$ occorrenze di ogni parola: $\text{PP} = \prod_w p_w^{-c_w/N}$. Per B su $T$: $0{,}8^{-4/5}\cdot0{,}1^{-1/5} = 1{,}195\times1{,}585 = 1{,}895$. Per il modello C ($0{,}5; 0{,}25; 0{,}25$): $(0{,}5^4\cdot0{,}25)^{-1/5} = 64^{1/5} = 2{,}30$. Tutti verificati in Python.

## Campionamento e generalizzazione

<a id="p-36"></a>
**Slide 36 · Campionamento e generalizzazione** — Che cosa ha imparato un modello linguistico: lo si vede generando frasi.

<a id="p-37"></a>

### Slide 37 · Campionare da un modello linguistico

**Campionare** da una distribuzione significa scegliere punti casuali **secondo la loro probabilità**: le frasi probabili escono più spesso di quelle improbabili. L'idea di visualizzare un LM generando frasi risale a Shannon (1948) e Miller e Selfridge (1950).

**La figura** (Fig. 3.3 del libro, unigram calcolati sul testo del libro): una barra divisa in intervalli, uno per parola, di ampiezza pari alla probabilità: *the* 0,06, *of* 0,03, *a* 0,02, *to* 0,02, *in* 0,02, poi puntini. Sotto, la retta da 0 a 1 con le probabilità **cumulate**: ,06 ,09 ,11 ,13 ,15 (fine di the, of, a, to, in), poi, molto più avanti, *however* (p = 0,0003) intorno a ,66 e *polyphonic* (p = 0,0000018) intorno a ,99. Le parole sono ordinate dalla più frequente, ma l'ordine è arbitrario.

- **Unigram**: le parole coprono la retta da 0 a 1, ciascuna con un intervallo proporzionale alla frequenza; si estrae un numero casuale, si stampa la parola il cui intervallo lo contiene, e si ripete finché esce </s>.
- **Bigram**: si estrae un bigram che inizia con <s> secondo la sua probabilità; se la sua seconda parola è $w$, si estrae un bigram che inizia con $w$, e così via fino a </s>. È la generazione autoregressiva della [L1](L01-introduzione-al-corso.md#p-6) con un contesto di una parola.

> **Da saper fare: Campionare a mano con numeri casuali dati**
>
> Unigram con the 0,5, a 0,3, cat 0,15, </s> 0,05: intervalli [0; 0,5), [0,5; 0,8), [0,8; 0,95), [0,95; 1). I numeri 0,62, 0,13, 0,91, 0,47, 0,97 danno *a the cat the* e poi </s>: frase finita, ma senza alcuna coerenza. Per il bigram si ricostruisce la retta a ogni passo, con le probabilità della riga del contesto corrente. Esercizio 10 della scheda.

<a id="p-38"></a>

### Slide 38 · Shakespeare, dagli unigram ai 4-gram

Otto frasi casuali, due per ciascuno di quattro modelli n-gram addestrati sulle opere di Shakespeare (Fig. 3.4 del libro). Tutto in minuscolo, punteggiatura trattata come parole; maiuscole corrette a mano per leggibilità.

- **1-gram**: *To him swallowed confess hear both. Which. Of save on trail for are ay device and rote life have*; *Hill he late speaks; or! a more to leg less first you enter*
- **2-gram**: *Why dost stand forth thy canopy, forsooth; he is this palpable hit the King Henry. Live king. Follow.*; *What means, sir. I confess she? then all sorts, he is trim, captain.*
- **3-gram**: *Fly, and will rid me these news of price. Therefore the sadness of parting, as they say, 'tis done.*; *This shall forbid it should be branded, if renown made it empty.*
- **4-gram**: *King Henry. What! I will go seek the traitor Gloucester. Exeunt some of the watch. A great banquet serv'd in;*; *It cannot be but so.*

Messaggio: **più lungo il contesto, più coerenti le frasi**. Le quattro schede seguenti evidenziano una riga per volta.

<a id="p-39"></a>

### Slide 39 · Shakespeare: unigram

Evidenziate le frasi unigram. Le parole sono estratte **indipendentemente**, ciascuna con la sua frequenza: nessuna relazione coerente tra loro, e **nessuna punteggiatura di fine frase** al posto giusto. I segni di punteggiatura compaiono (sono parole frequenti) ma in posizioni casuali, e la frase finisce solo quando per caso esce </s>. Il vocabolario è shakespeariano (*ay*), l'ordine no.

<a id="p-40"></a>

### Slide 40 · Shakespeare: bigram

Evidenziate le frasi bigram: c'è **coerenza locale da parola a parola**, soprattutto considerando la punteggiatura come parole. *Live king. Follow.*: ogni coppia adiacente (*live king*, *king .*, *. follow*, *follow .*) è plausibile, ma la frase nel suo insieme non ha senso (*he is this palpable hit the King Henry*). Il modello vede una parola alla volta: ogni transizione è sensata, il percorso no.

<a id="p-41"></a>

### Slide 41 · Shakespeare: trigram

Evidenziate le frasi trigram: **cominciano a somigliare molto a Shakespeare**. *Therefore the sadness of parting, as they say, 'tis done.* è quasi una frase vera: con due parole di contesto il modello ricostruisce sintagmi interi e perfino formule idiomatiche (*as they say*). La coerenza globale manca ancora (la prima frase salta da *news of price* a un altro discorso).

<a id="p-42"></a>

### Slide 42 · Shakespeare: 4-gram

Evidenziate le frasi 4-gram: **un po' troppo simili a Shakespeare**. *It cannot be but so.* è presa **direttamente dal King John**. Con un contesto lungo il modello **riproduce i suoi dati di training** invece di generare frasi nuove: non sta generalizzando, sta copiando. La scheda successiva spiega perché con i numeri.

<a id="p-43"></a>

### Slide 43 · Perché i 4-gram sono troppo bravi

- $N = 884.647$ token nelle opere complete di Shakespeare: **poco**, per gli standard dei corpora.
- $V = 29.066$ tipi di parola.
- $V^2 \approx 844$ milioni di bigram possibili (esattamente $29.066^2 = 844.832.356$): le matrici di probabilità n-gram sono **ridicolmente sparse**. Il corpus contiene al più $N-1 = 884.646$ bigram distinti, cioè lo 0,105% delle celle: almeno il 99,9% sono zero.
- $V^4 \approx 7\times10^{17}$ 4-gram possibili (esattamente $7{,}14\cdot10^{17}$), contro meno di un milione di 4-gram osservati.
- **6**: le possibili parole successive, una volta che il generatore ha scelto *It cannot be*: *but, I, that, thus, this* e il punto. Quasi nessuna scelta: il modello riproduce il corpus.

Conclusione: gli n-gram di ordine più alto modellano il corpus di training sempre meglio, fino a **riprodurlo**: è **overfitting**. Con contesti lunghi quasi ogni contesto è stato visto una o poche volte, quindi la distribuzione successiva è concentrata su pochissime parole (spesso una sola). Sul training la perplexity crolla, su testo nuovo i contesti lunghi non si trovano affatto (zeri, [scheda 46](L04-modelli-linguistici-n-gram.md#p-46)). Il notebook lo mostra sulle docstring di Python: perplexity sul training da 386 (unigram) a 1,59 (5-gram), e 76 frasi su 200 generate dal 4-gram copiate alla lettera.

> **Da saper fare: Conti di sparsità**
>
> $V^2 = 29.066^2 = 8{,}45\cdot10^{8}$; $V^3 = 2{,}46\cdot10^{13}$; $V^4 = 7{,}14\cdot10^{17}$. Bigram distinti al massimo $N-1$ (un testo di $N$ token ha $N-1$ bigram, con i confini di frase uno in più per frase): frazione $\le 884.646/844.832.356 = 0{,}105\%$. Con $V = 1446$ (BeRP) le celle sono $2{,}09\cdot10^6$. Esercizio 11 della scheda.

<a id="p-44"></a>

### Slide 44 · Il Wall Street Journal non è Shakespeare

Frasi generate da modelli unigram, bigram e trigram addestrati su **40 milioni di parole del WSJ** (Fig. 3.5 del libro; da non confondere con i 38 milioni dell'esperimento di perplexity della [scheda 32](L04-modelli-linguistici-n-gram.md#p-32), che è un altro esperimento):

- **1-gram**: *Months the my and issue of year foreign new exchange's september were recession exchange new endorsed a acquire to six executives*
- **2-gram**: *Last December through the way to preserve the Hudson corporation N. B. E. C. Taylor would seem to complete the major central planners one point five percent of U. S. E. has already old M. X. corporation of living on information such as more frequently fishing to keep her*
- **3-gram**: *They also point to ninety nine point six billion dollars from two hundred four oh six three percent of the rates of interest stores as Mexico and Brazil on market conditions*

Entrambi i corpora sono inglese, eppure **nessuna sovrapposizione** tra le frasi generate e poca anche tra piccoli sintagmi: il lessico è finanziario (*recession, percent, billion dollars, market conditions*), i numeri sono scritti in lettere. I modelli statistici sono **quasi inutili come predittori** se training e test sono diversi quanto Shakespeare e il WSJ.

<a id="p-45"></a>

### Slide 45 · Il corpus di training conta

- **Genere**: un LM per tradurre documenti legali ha bisogno di un corpus di documenti legali (il libro aggiunge: per un sistema di question answering, un corpus di domande).
- **Dialetto e varietà**: conta soprattutto per post sui social e trascrizioni del parlato. L'**African American English** (AAE) ha parole come *finna*, un ausiliare che marca il futuro immediato, e grafie come *den* per *then*: *Bored af den my phone finna die!!!* (Blodgett e O'Connor 2017).
- **Altri inglesi**: i tweet in **Nigerian Pidgin** hanno lessico e n-gram molto diversi dall'inglese americano: *R u a wizard or wat gan sef: in d mornin - u tweet, afternoon - u tweet* (Jurgens et al. 2017).
- **Parole mai viste**: e se *Jurafsky* non compare mai nel training ma spunta nel test? Si lavora su **token subword**: con BPE ogni parola è una sequenza di subword noti, al limite singole lettere (o byte), quindi il test set non contiene mai token sconosciuti ([L2, scheda 13](L02-parole-e-token.md#p-13)).

Regola: **addestrare sul genere e sulla varietà di lingua del compito**. È lo stesso tema della lingua situata e dei datasheet ([L2, schede 47-48](L02-parole-e-token.md#p-47)): un modello addestrato su inglese «standard» funziona peggio proprio sulle varietà sottorappresentate.

Nota: niente token sconosciuti non vuol dire niente zeri. Una **sequenza** di token noti può non essere mai comparsa (scheda successiva): BPE risolve il problema delle parole, non quello degli n-gram.

<a id="p-46"></a>

### Slide 46 · Zeri

**Qualunque corpus di training finito mancherà di alcune sequenze di parole perfettamente accettabili.**

- **Zeri**: n-gram che non compaiono mai nel training ma compaiono nel test. Il corpus contiene *ruby* e *slippers*, ma mai *ruby slippers*: per la MLE $P(\text{slippers}\mid\text{ruby}) = 0/C(\text{ruby}) = 0$.
- **Sottostima**: si sottostima la probabilità di sequenze che invece capitano, e questo danneggia qualunque applicazione (un riconoscitore vocale non potrà mai trascrivere *ruby slippers*).
- **Niente perplexity**: una sola parola con probabilità 0 nel suo contesto rende 0 la probabilità dell'intero test set; la perplexity non si può calcolare, perché non si divide per zero (in log: $\ln 0 = -\infty$, perplexity infinita).
- **Il rimedio**: **smoothing** (o *discounting*): togliere un po' di massa di probabilità ad alcuni eventi più frequenti e darla a quelli mai visti. Laplace, add-k, interpolazione e backoff sono la prossima lezione (§3.6).

Già nel mini-corpus: $P(\text{&lt;s&gt; I do not like Sam &lt;/s&gt;}) = 0$ per il solo bigram *like Sam*. Nel notebook, su moduli Python tenuti da parte, il 46% dei bigram e il 76% dei trigram del test non compaiono nel training: perplexity infinita per tutti i modelli, perfino l'unigram (8% di parole mai viste, perché lì si lavora su parole e non su subword).

<a id="p-47"></a>

### Slide 47 · Riepilogo e prossima lezione

**Riepilogo**:

- un language model predice la parola successiva e assegna probabilità alle sequenze;
- n-gram: regola della catena, assunzione di Markov, conteggi normalizzati in probabilità (MLE);
- training, development e test set; mai allenare sul test set;
- perplexity: probabilità inversa normalizzata per la lunghezza, più bassa è meglio;
- il campionamento mostra che cosa ha imparato il modello: la coerenza cresce con $n$, e così l'overfitting;
- zeri: gli n-gram mai visti rompono il modello.

**Prossima lezione**: **smoothing e interpolazione**, cioè stimare ciò che non è mai comparso nel training; perplexity ed entropia (capitolo 3, §3.6-3.7). Lì si vedrà da dove viene l'inversa nella perplexity.

## Notebook

Commento al notebook del corso `HLT-L04-n-gram-language-models.ipynb` (il notebook è del docente e non è incluso).

Notebook di accompagnamento della lezione: conta n-gram sul corpus *I am Sam*, calcola probabilità di frasi in log, costruisce un corpus dalle docstring della libreria standard di Python, campiona frasi da modelli 1-4 gram, calcola perplexity su training e test e riproduce l'esempio dei colori e l'esercizio 3.12. Serve solo la libreria standard più `matplotlib`, niente rete. Permette di controllare gli esercizi 2, 3, 4, 7, 8, 9, 10, 11 della scheda. Gli output mostrati sono quelli salvati dallo studente; la mia esecuzione (Python 3.11, nbconvert) li riproduce identici. Trovato un bug reale: `inspect.getdoc` eredita le docstring delle classi madri e porta 21 frasi del training nel test set (contaminazione), segnalato con la correzione verificata. Il resto (conteggio di N con </s> sì e <s> no, simboli di confine nei trigrammi, gestione degli zeri, log naturale, seed) è corretto.

### Notebook 1 · Contare n-gram: il corpus I am Sam

```python
SAM = ["I am Sam", "Sam I am", "I do not like green eggs and ham"]

def sentences_to_tokens(sentences, n):
    """Each sentence becomes a list of tokens with n-1 start symbols and one end symbol."""
    return [["<s>"] * (n - 1) + s.split() + ["</s>"] for s in sentences]

def train(sentences, n):
    """counts[context][word]: how many times word followed the (n-1)-word context."""
    counts = defaultdict(Counter)
    for toks in sentences_to_tokens(sentences, n):
        for i in range(n - 1, len(toks)):
            counts[tuple(toks[i - n + 1:i])][toks[i]] += 1
    return counts

def prob(counts, context, word):
    """Maximum likelihood estimate P(word | context); 0 for unseen n-grams."""
    c = counts.get(tuple(context))
    if not c or word not in c:
        return Fraction(0)
    return Fraction(c[word], sum(c.values()))
```

Output:

```text
P(I    | <s> ) = 2/3
P(Sam  | <s> ) = 1/3
P(am   | I   ) = 2/3
P(do   | I   ) = 1/3
P(Sam  | am  ) = 1/2
P(</s> | Sam ) = 1/2
P(I    | Sam ) = 1/2
P(Sam  | like) = 0
```

Il modello n-gram è solo una tabella: `counts[contesto][parola]`, un `Counter` per ogni contesto di $n-1$ parole. `sentences_to_tokens` aggiunge $n-1$ simboli <s> e un solo </s>, come prescrive il libro ([scheda 23](L04-modelli-linguistici-n-gram.md#p-23)); il ciclo parte da $i = n-1$, quindi <s> non viene mai predetto, solo usato come contesto. `prob` è la MLE $C(\text{contesto}\,w)/\sum_v C(\text{contesto}\,v)$, con il denominatore calcolato come somma della riga: coincide con il conteggio del contesto ([scheda 13](L04-modelli-linguistici-n-gram.md#p-13)). Le frazioni esatte (`Fraction`) evitano arrotondamenti.

L'output riproduce le sei probabilità della [scheda 15](L04-modelli-linguistici-n-gram.md#p-15) più $P(\text{I}\mid\text{Sam}) = 1/2$ e $P(\text{Sam}\mid\text{like}) = 0$ (bigram mai visto). Ho eseguito il notebook (Python 3.11): questo e tutti gli output seguenti coincidono con quelli salvati.

### Notebook 2 · Trigrammi con due simboli di inizio

```python
trigrams = train(SAM, 3)
rows = [(ctx, w, Fraction(c, sum(ws.values()))) for ctx, ws in trigrams.items() for w, c in ws.items()]
print(len(rows), "non-zero trigram probabilities")
```

Output:

```text
16 non-zero trigram probabilities
P(I | <s> Sam) = 1
P(not | I do) = 1
P(am | Sam I) = 1
P(</s> | am Sam) = 1
...
P(I | <s> <s>) = 2/3
P(am | <s> I) = 1/2
P(do | <s> I) = 1/2
P(Sam | I am) = 1/2
P(</s> | I am) = 1/2
P(Sam | <s> <s>) = 1/3
```

Stessa funzione con $n = 3$: due <s> all'inizio, un </s> alla fine. Le frasi hanno 4, 4 e 9 token predetti, quindi 17 occorrenze di trigram; i trigrammi distinti sono **16** (solo *<s> <s> I* compare due volte), e ognuno ha probabilità non nulla. Dieci hanno probabilità 1 (contesto visto una sola volta, o sempre seguito dalla stessa parola); le incertezze sono solo all'inizio ($P(\text{I}\mid\text{&lt;s&gt; &lt;s&gt;}) = 2/3$) e dove i contesti si ripetono (*<s> I*, *I am*). È la soluzione dell'esercizio 3 della scheda (verificata anche con un'implementazione indipendente).

### Notebook 3 · La probabilità di una frase, in log

```python
def sentence_logprob(counts, n, sentence):
    """Natural log probability of a sentence under an n-gram model; -inf if any n-gram is unseen."""
    toks = sentences_to_tokens([sentence], n)[0]
    total = 0.0
    for i in range(n - 1, len(toks)):
        p = prob(counts, toks[i - n + 1:i], toks[i])
        if p == 0:
            return float("-inf")
        total += math.log(p)
    return total
```

Output:

```text
I am Sam             log P =   -2.197   P = 0.1111
Sam I am             log P =   -2.890   P = 0.0556
I am                 log P =   -1.504   P = 0.2222
Sam I am Sam         log P =   -3.584   P = 0.0278
I do not like Sam    log P =     -inf   P = 0.0000
```

Somma di log naturali invece di prodotto ([scheda 22](L04-modelli-linguistici-n-gram.md#p-22)); un n-gram mai visto dà subito $-\infty$ (il codice lo gestisce esplicitamente, perché `math.log(0)` solleverebbe un errore). Controllo: $\ln(1/9) = -2{,}197$, $\ln(1/18) = -2{,}890$, $\ln(2/9) = -1{,}504$, $\ln(1/36) = -3{,}584$.

*I am* non è nel corpus ed è la più probabile delle cinque: il bigram ricombina pezzi visti, e le frasi corte hanno meno fattori. *Sam I am Sam* (anch'essa nuova) ha probabilità 1/36. *I do not like Sam* ha probabilità 0 per il solo bigram *like Sam*: è il problema degli zeri in miniatura (esercizio 2 della scheda).

### Notebook 4 · La frase del Berkeley Restaurant Project

```python
brp = {("<s>", "i"): 0.25, ("i", "want"): 0.33, ("want", "english"): 0.0011, ("want", "chinese"): 0.0065,
       ("english", "food"): 0.5, ("chinese", "food"): 0.52, ("food", "</s>"): 0.68}

def brp_prob(sentence):
    toks = ["<s>"] + sentence.split() + ["</s>"]
    logp = sum(math.log(brp[(a, b)]) for a, b in zip(toks, toks[1:]))
    return math.exp(logp)
```

Output:

```text
P(i want english food) = 0.000031
P(i want chinese food) = 0.000190
ratio = 6.1
```

Le probabilità della slide in un dizionario, con i bigram presi a coppie consecutive (`zip(toks, toks[1:])`). Riproduce 0,000031 della [scheda 20](L04-modelli-linguistici-n-gram.md#p-20) e risolve l'esercizio della slide: *i want chinese food* ha probabilità 0,000190, circa 6,1 volte di più (rapporto esatto 6,145). Nota: il dizionario contiene solo i bigram di queste due frasi; con un bigram assente (per esempio *i want to eat*) la funzione solleverebbe `KeyError` invece di restituire 0, ma per l'uso fatto qui non è un problema.

### Notebook 5 · Un corpus più grande: le docstring della libreria standard

```python
def module_text(name):
    """The docstring of a module and of its public functions and classes."""
    try:
        mod = importlib.import_module(name)
    except Exception:
        return ""
    parts = [inspect.getdoc(mod) or ""]
    for member, obj in inspect.getmembers(mod):
        if member.startswith("_") or not (inspect.isfunction(obj) or inspect.isclass(obj) or inspect.isbuiltin(obj)):
            continue
        d = inspect.getdoc(obj)
        if d and (getattr(obj, "__module__", None) or name).split(".")[0] == name.split(".")[0]:
            parts.append(d)
    return "\n".join(parts)

texts = {m: to_sentences(module_text(m)) for m in MODULES}
texts = {m: s for m, s in texts.items() if s}
# held-out modules for testing: every tenth module; the rest is the training corpus
test_modules = sorted(texts)[::10]
train_sents = [s for m, ss in texts.items() if m not in test_modules for s in ss]
test_sents = [s for m in test_modules for s in texts[m]]
```

Output:

```text
133 modules, 2904 training sentences, N = 49759 tokens, V = 4006 types
609 test sentences from 14 held-out modules: abc, calendar, configparser, doctest, gc, http.client, logging, optparse, py_compile, select, statistics, textwrap, unittest, zipfile

- this can be used to efficiently compute the digests of datas that share a common initial substring .
- this can be overridden in sitecustomize , usercustomize or pythonstartup .
- this returns true when obj is a future instance or is advertising itself as duck-type compatible by setting _ asyncio_future_blocking .
- removes the pack format from the registry .
```

Un corpus senza scaricare nulla: le **docstring** di 138 moduli della libreria standard (133 producono almeno una frase; *bisect, keyword, token, trace* non danno frasi valide dopo i filtri e *turtle* non si importa senza tkinter). `to_sentences` mette in minuscolo, divide in frasi a `. ! ?` seguiti da spazio (una segmentazione a regole come in [L3, scheda 32](L03-elaborazione-del-testo.md#p-32)), scarta gli esempi doctest (`>>>`) e i pezzi che sembrano codice, e tratta la punteggiatura come parole, come il libro fa per Shakespeare. Risultato salvato: **2904 frasi di training, N = 49.759 token, V = 4006 tipi**; 609 frasi di test da 14 moduli.

Lo split è per **documento** (modulo), non per frase: un modulo su dieci in ordine alfabetico va nel test. È la scelta giusta secondo la [scheda 28](L04-modelli-linguistici-n-gram.md#p-28): il test contiene testi interi mai visti, non frasi sparse degli stessi documenti. Il genere è molto particolare (documentazione tecnica): il modello imparerà quel genere ([scheda 45](L04-modelli-linguistici-n-gram.md#p-45)).

I numeri dipendono dalla versione di Python, come avverte il notebook, e anche dall'ambiente: eseguendo le stesse celle con `python` fuori da Jupyter ottengo 2917 frasi e N = 49.933, perché `inspect.getmembers` vede membri diversi a seconda dei moduli già caricati dal kernel. Eseguito con Jupyter (nbconvert) ottengo gli stessi numeri salvati.

> **Attenzione (errore nelle slide): Bug: getdoc eredita le docstring, e il test set contiene frasi del training**
>
> `inspect.getdoc(obj)`, se una classe non ha una docstring propria, restituisce quella della **classe madre**. Il filtro su `__module__` serve proprio a non prendere testo di altri moduli, ma l'ereditarietà lo aggira: tutte le eccezioni senza docstring (per esempio `http.client.BadStatusLine`, `calendar.IllegalMonthError`) portano la docstring di `Exception` o `ValueError`. Risultato, verificato eseguendo il notebook:
>
> - **21 delle 609 frasi di test (3,4%) sono anche nel training**, 17 delle quali sono la stessa frase *common base class for all non-exit exceptions .*: è contaminazione train/test, proprio ciò che la [scheda 28](L04-modelli-linguistici-n-gram.md#p-28) vieta;
> - il training contiene 246 frasi duplicate (la stessa frase 27 volte), che gonfiano i conteggi di pochi n-gram.
>
> Nei moduli di test ci sono 30 classi con docstring ereditata. Correzione: usare solo la docstring propria dell'oggetto.
>
> ```
> def module_text(name):
>     try:
>         mod = importlib.import_module(name)
>     except Exception:
>         return ""
>     parts = [inspect.cleandoc(mod.__doc__ or "")]
>     for member, obj in inspect.getmembers(mod):
>         if member.startswith("_") or not (inspect.isfunction(obj) or inspect.isclass(obj) or inspect.isbuiltin(obj)):
>             continue
>         d = obj.__doc__ if isinstance(getattr(obj, "__doc__", None), str) else None   # own docstring only
>         if d and (getattr(obj, "__module__", None) or name).split(".")[0] == name.split(".")[0]:
>             parts.append(inspect.cleandoc(d))
>     return "\n".join(parts)
> ```
>
> Verifica (stesso kernel): con la correzione i moduli di test sono gli stessi 14, le frasi diventano 2806 di training e 532 di test, N = 48.390, V = 3989, e **nessuna frase di test compare nel training**. Le conclusioni del notebook non cambiano: sul test gli n-gram a probabilità zero diventano 840 su 9907 per l'unigram (8,5%), 4607 per il bigram (46,5%), 7699 per il trigram (77,7%), contro 8,0%, 45,7%, 76,1% dell'originale. La contaminazione qui ha un effetto piccolo, ma nel verso atteso: rende il test leggermente più «facile».

### Notebook 6 · Frequenze e sparsità del corpus

```python
uni = train(train_sents, 1)[()]
print("most frequent words:", ", ".join(f"{w} ({c})" for w, c in uni.most_common(15)))
bi = train(train_sents, 2)
distinct_bigrams = sum(len(c) for c in bi.values())
print(f"distinct bigrams: {distinct_bigrams:,} out of V^2 = {V**2:,} possible: ...")
```

Output:

```text
most frequent words: . (3162), the (3014), </s> (2904), a (1449), , (1438), is (1125), to (1071), of (935), and (701), ( (654), ) (648), for (612), in (571), be (542), if (540)
distinct bigrams: 22,224 out of V^2 = 16,048,036 possible: 0.14 % of the table is non-zero
```

Un modello unigram è `train(..., 1)` con contesto vuoto `()`. Le parole più frequenti sono punteggiatura e parole funzionali (*. the a , is to of*); </s> compare 2904 volte, una per frase, ed è a tutti gli effetti un «token» del modello unigram. Solo **22.224 bigram distinti su 16 milioni** di celle possibili: lo 0,14% della tabella è diverso da zero, la stessa sparsità della [scheda 43](L04-modelli-linguistici-n-gram.md#p-43) in piccolo.

Precisazione sul testo della cella 11 («con N token ci sono al più N - 1 bigram distinti»): vale per un testo continuo. Con i confini di frase il codice conta un bigram per ogni token più uno per frase (<s> w₁ ... </s>): qui 49.759 + 2904 = 52.663 occorrenze di bigram, non 49.758. Inoltre $V$ non include <s> e </s>, che invece sono righe e colonne della tabella. Il 0,14% cambia di pochissimo; è un'imprecisione del testo, non un errore del codice.

### Notebook 7 · Campionare frasi dai modelli 1-4 gram

```python
def sample_sentence(counts, n, rng, max_len=40):
    context = ["<s>"] * (n - 1)
    words = []
    while len(words) < max_len:
        c = counts[tuple(context)]
        word = rng.choices(list(c.keys()), weights=list(c.values()))[0]
        if word == "</s>":
            break
        words.append(word)
        context = (context + [word])[1:] if n > 1 else []
    return " ".join(words) if words else "(empty sentence: </s> was drawn first)"

models = {n: train(train_sents, n) for n in (1, 2, 3, 4)}
rng = random.Random(2026)
```

Output:

```text
--- 1-gram
(empty sentence: </s> was drawn first)
no this indicate
( been in member signal mapping classes random all , instance
--- 2-gram
file is created by python object . 9 .
zdict the result is to be added to set by the encoding , then , relative to the case no tty is rfc_ 4122 variant is no command line of the current stack traces .
return a single instance , this object creation to ` code object , unless ' b' to instantiate a slice assignment ) ) on platforms where file .
--- 3-gram
an ftp client class .
see help ( thing ) on a variable .
return a temporary file .
--- 4-gram
you can concatenate ordinary characters , so last matches the string ' last' .
see individual fields' descriptions for details .
- : attr : ` line ` the text from the linecache module for the list of subdirectories is retrieved before the tuples for the directory and everything contained in it are processed .
```

Il campionamento della [scheda 37](L04-modelli-linguistici-n-gram.md#p-37): si parte da $n-1$ simboli <s>, si estrae la parola successiva con `rng.choices` pesando per i conteggi (equivale a pesare per le probabilità MLE, perché i pesi vengono normalizzati), si fa scorrere il contesto e ci si ferma a </s> o a 40 parole. Il seed fisso (2026) rende l'output riproducibile a parità di corpus.

Il risultato ripete la lezione di Shakespeare: gli **unigram** sono insalata di parole (e la prima frase è vuota: </s> ha probabilità 2904/52.663 = 5,5% di uscire subito); i **bigram** hanno coerenza locale ma derivano (*zdict the result is to be added to set by the encoding*); i **trigram** producono frasi brevi plausibili; i **4-gram** copiano: l'ultima frase incolla due docstring diverse nel punto in cui condividono un contesto di tre token.

Scelta, non bug: il limite di 40 parole tronca le frasi lunghe senza segnalarlo (con il seed 7 capita a 10 frasi bigram su 200).

### Notebook 8 · Quante frasi campionate sono copiate dal training

```python
train_set = set(train_sents)
rng = random.Random(7)
for n in (2, 3, 4):
    copied = sum(sample_sentence(models[n], n, rng) in train_set for _ in range(200))
```

Output:

```text
2-gram: 0 of 200 sampled sentences are training sentences, copied verbatim
3-gram: 11 of 200 sampled sentences are training sentences, copied verbatim
4-gram: 76 of 200 sampled sentences are training sentences, copied verbatim
```

Misura quantitativa dell'overfitting ([scheda 42](L04-modelli-linguistici-n-gram.md#p-42)): su 200 frasi campionate, quelle identiche a una frase di training sono 0 per il bigram, 11 per il trigram e **76 (38%) per il 4-gram**. Con contesti di tre token quasi ogni contesto ha una sola continuazione vista, e il generatore ripercorre il corpus. Le frasi troncate a 40 parole non possono mai coincidere con una frase di training, ma sono poche e quasi solo nel bigram.

### Notebook 9 · Perplexity sul training set

```python
def perplexity(counts, n, sentences):
    """Perplexity of an n-gram model on a list of sentences; also returns the number of unseen n-grams."""
    logp, N, zeros = 0.0, 0, 0
    for toks in sentences_to_tokens(sentences, n):
        for i in range(n - 1, len(toks)):
            p = prob(counts, toks[i - n + 1:i], toks[i])
            N += 1
            if p == 0:
                zeros += 1
            else:
                logp += math.log(p)
    return (math.exp(-logp / N) if zeros == 0 else float("inf")), zeros, N
```

Output:

```text
1-gram model, perplexity on the TRAINING sentences:   385.56   (N = 52663, unseen n-grams: 0)
2-gram model, perplexity on the TRAINING sentences:    20.24   (N = 52663, unseen n-grams: 0)
3-gram model, perplexity on the TRAINING sentences:     3.21   (N = 52663, unseen n-grams: 0)
4-gram model, perplexity on the TRAINING sentences:     1.78   (N = 52663, unseen n-grams: 0)
5-gram model, perplexity on the TRAINING sentences:     1.59   (N = 52663, unseen n-grams: 0)
```

$\text{PP} = \exp(-\frac1N\sum\ln p_i)$ ([scheda 30](L04-modelli-linguistici-n-gram.md#p-30)), con log ed exp naturali, coerenti tra loro. **Conteggio di $N$**: il ciclo parte da $n-1$, quindi conta ogni parola più un </s> per frase e mai <s>, esattamente come prescrive la [scheda 31](L04-modelli-linguistici-n-gram.md#p-31): $N = 52.663 = 49.759$ parole $+ 2904$ </s>, uguale per tutti gli ordini (i <s> aggiuntivi dei modelli di ordine alto non entrano in $N$). Verificato sul corpus giocattolo: `perplexity(bigrams, 2, ["I am Sam"])` dà $N = 4$ e $\sqrt3 = 1{,}732$; con le due frasi *I am Sam*, *Sam I am* dà $N = 8$ e $162^{1/8} = 1{,}889$, come a mano. Se c'è anche un solo zero restituisce infinito, coerente con la [scheda 46](L04-modelli-linguistici-n-gram.md#p-46); con una lista vuota di frasi darebbe una divisione per zero, caso che il notebook non tocca.

Il testo lo dice chiaramente: **questa non è valutazione**, è perplexity sui dati di training (training on the test set). Scende da 386 a 1,59 perché i contesti lunghi diventano quasi deterministici. La figura: asse x $n$ da 1 a 7, asse y la perplexity sul training in scala logaritmica (da $10^0$ a oltre $10^2$), una curva blu con marcatori circolari che scende ripida da circa 386 ($n=1$) a 20 ($n=2$) e 3,2 ($n=3$), poi si appiattisce: 1,78 a $n=4$, 1,59 a $n=5$, 1,56 a $n=6$ e 1,55 a $n=7$ (valori ricalcolati). Titolo: «Longer context, better fit to the training corpus». Non scende a 1 perché alcuni contesti, anche lunghi, sono seguiti da parole diverse in frasi diverse (e alcune frasi sono duplicate).

### Notebook 10 · Perplexity sui moduli tenuti da parte: gli zeri

```python
for n in (1, 2, 3):
    pp, zeros, N = perplexity(train(train_sents, n), n, test_sents)
```

Output:

```text
1-gram model on the HELD-OUT sentences: perplexity = inf, 913 of 11364 test n-grams have probability zero (8.0 %)
2-gram model on the HELD-OUT sentences: perplexity = inf, 5192 of 11364 test n-grams have probability zero (45.7 %)
3-gram model on the HELD-OUT sentences: perplexity = inf, 8648 of 11364 test n-grams have probability zero (76.1 %)
```

Sul test vero la perplexity è **infinita per tutti i modelli**: l'8% delle parole di test non compare mai nel training (qui si lavora su parole, non su subword, quindi le parole sconosciute ci sono: [scheda 45](L04-modelli-linguistici-n-gram.md#p-45)), e i bigram e trigram mai visti sono il 45,7% e il 76,1%. Più alto $n$, più zeri: l'opposto di quanto succede sul training. È il messaggio della [scheda 46](L04-modelli-linguistici-n-gram.md#p-46), e la motivazione dello smoothing.

Due precisazioni sul testo della cella 20: la [scheda 46](L04-modelli-linguistici-n-gram.md#p-46) e il libro introducono gli zeri all'inizio del §3.6, non nel §3.5 come scrive il notebook; e i numeri risentono leggermente della contaminazione descritta sopra (con la correzione 8,5%, 46,5%, 77,7%).

> **Approfondimento: Contare gli zeri invece di restituire solo infinito**
>
> (Facoltativo.) Restituire il numero di zeri insieme a infinito è una buona scelta didattica: la perplexity da sola direbbe solo «inf». Per avere un numero finito servono lo smoothing (prossima lezione) oppure, come prova, calcolare la perplexity solo sui token con probabilità non nulla: ma quel numero non è confrontabile tra modelli, perché ciascuno scarta token diversi.

### Notebook 11 · Colori e cifre: fattore di ramificazione pesato

```python
def unigram_perplexity(probs, test):
    return math.exp(-sum(math.log(probs[w]) for w in test) / len(test))

T = "red red red red blue".split()
A = {"red": 1/3, "blue": 1/3, "green": 1/3}
B = {"red": 0.8, "blue": 0.1, "green": 0.1}
digits = {str(d): (91 if d == 0 else 1) / 100 for d in range(10)}
```

Output:

```text
perplexity of A on T: 3.000   perplexity of B on T: 1.895
textbook exercise 3.12: 1.725
```

Riproduce le schede [34](L04-modelli-linguistici-n-gram.md#p-34) e [35](L04-modelli-linguistici-n-gram.md#p-35): A = 3,000, B = 1,895 (la slide arrotonda a 1,89). Qui non ci sono <s> e </s>, quindi $N = 5$ (lunghezza della lista). L'esercizio 3.12 del libro (esercizio 8 della scheda): 91 zeri e una volta ciascuna le cifre 1-9, test *0 0 0 0 0 3 0 0 0 0*: $(0{,}91^9\times0{,}01)^{-1/10} = 1{,}725$. L'ultima cella (6) suggerisce di provare il notebook su un altro testo e di verificare l'esercizio 3.5 del libro (senza </s> le frasi di ogni lunghezza sommano a 1).

## Studio ed esercizi

### Guida allo studio (circa 4 h 00 min)

**Modelli linguistici, regola della catena, Markov** (25 min)

Schede 5-12. Saper dire che cos'è un LM nelle due viste (distribuzione sulla parola successiva, probabilità di sequenze) e perché coincidono (regola della catena). Perché la frequenza relativa su storie intere fallisce; assunzione di Markov per bigram e n-gram con la notazione $w_{n-N+1:n-1}$. Esercizio 1. Libro §3.1 fino a 3.1.1.

**MLE, I am Sam, Berkeley Restaurant Project** (50 min)

Schede 13-21. Rifare a mano la tabella bigram di *I am Sam* con <s> e </s> e il ruolo di ciascuno; ricalcolare qualche cella BeRP dai conteggi e dagli unigrammi (attenzione: si divide per il conteggio unigram della riga, non per la somma della riga mostrata); probabilità di *i want english food* e *i want chinese food*. Esercizi 2, 3, 4; controllare con le celle 2-8 del notebook. Libro §3.1.2.

**Log probabilità e scala** (15 min)

Schede 22-23. Underflow, somma di log, logaritmo naturale; padding con $N-1$ simboli <s>; grandi dataset (COCA, Google Web 5-grams, Google Books, infini-gram) e trucchi di efficienza. Esercizio 5. Libro §3.1.3.

**Valutazione e perplexity** (55 min)

Schede 26-35. Estrinseca vs intrinseca; training, dev e test set e i quattro errori di protocollo (contaminazione, tuning sul test, test non rappresentativo, test troppo piccolo). Perplexity: definizione, forma in log, conteggio di $N$ (</s> sì, <s> no), unigram e bigram, tabella WSJ 962/170/109, colori (A = 3, B = 1,89). Esercizi 6, 7, 8, 9. Libro §3.2-3.3.

**Campionamento, overfitting, genere, zeri** (35 min)

Schede 37-46. Campionare con la retta cumulata (unigram) e riga per riga (bigram); leggere le frasi di Shakespeare per ordine e spiegare con $N$, $V$, $V^2$, $V^4$ perché i 4-gram copiano; WSJ vs Shakespeare; genere e varietà (AAE, Nigerian Pidgin); perché BPE elimina le parole sconosciute ma non gli zeri. Esercizi 10, 11, 12. Libro §3.4-3.5 e inizio §3.6.

**Notebook** (30 min)

Eseguire il notebook dall'inizio; leggere `train`, `prob`, `perplexity` e `sample_sentence` finché si sa spiegare ogni riga; verificare il conteggio di $N$ sul corpus giocattolo; provare la correzione di `module_text` e vedere che la contaminazione sparisce. Provare un altro seed e un altro testo.

**Ripasso orale** (30 min)

Rispondere ad alta voce alle domande della sezione orale senza guardare la traccia. Punti che cadono spesso: perché serve </s>, perché <s> non si conta in $N$, perplexity come fattore di ramificazione pesato, perché la perplexity sul training non è una valutazione, perché più $n$ significa più overfitting e più zeri.

### Esercizi

#### Esercizio 1 (scheda L04): regola della catena e assunzione di Markov

Frase <s> the cat sat </s>. (a) Scrivi la sua probabilità con la regola della catena, senza approssimazioni. (b) Scrivi la stessa probabilità con un modello bigram e con un modello trigram (due simboli di inizio). (c) Quale assunzione trasforma (a) in (b)? Che cosa ignora un bigram quando predice *sat*?

<details><summary>Soluzione</summary>

(a) Catena, condizionando sempre su tutto il prefisso (che inizia con <s>):

$$P = P(\text{the}\mid\text{&lt;s&gt;})\,P(\text{cat}\mid\text{&lt;s&gt; the})\,P(\text{sat}\mid\text{&lt;s&gt; the cat})\,P(\text{&lt;/s&gt;}\mid\text{&lt;s&gt; the cat sat})$$

(b) Bigram: $P(\text{the}\mid\text{&lt;s&gt;})\,P(\text{cat}\mid\text{the})\,P(\text{sat}\mid\text{cat})\,P(\text{&lt;/s&gt;}\mid\text{sat})$. Trigram: $P(\text{the}\mid\text{&lt;s&gt; &lt;s&gt;})\,P(\text{cat}\mid\text{&lt;s&gt; the})\,P(\text{sat}\mid\text{the cat})\,P(\text{&lt;/s&gt;}\mid\text{cat sat})$. In tutti i casi 4 fattori: tre parole più </s>; <s> non è mai predetto.

(c) L'**assunzione di Markov**: $P(w_n\mid w_{1:n-1}) \approx P(w_n\mid w_{n-N+1:n-1})$, la parola dipende solo dalle ultime $N-1$. Predicendo *sat*, il bigram guarda solo *cat* e ignora *the* e il fatto che la frase sia appena iniziata (<s>). Nel trigram il secondo fattore è uguale a quello della catena, perché lì la storia è lunga solo due token.

</details>

#### Esercizio 2 (scheda L04): probabilità bigram da un mini-corpus

Modello bigram non smussato sul corpus della lezione: <s> I am Sam </s>, <s> Sam I am </s>, <s> I do not like green eggs and ham </s>. (a) Calcola $P(\text{am}\mid\text{I})$, $P(\text{Sam}\mid\text{am})$, $P(\text{&lt;/s&gt;}\mid\text{am})$, $P(\text{I}\mid\text{Sam})$, $P(\text{like}\mid\text{not})$. (b) Calcola la probabilità di <s> I am Sam </s>, <s> Sam I am </s> e <s> I am </s>. Quale è la più probabile, ed è nel corpus? (c) Qual è la probabilità di <s> I do not like Sam </s>? Perché?

<details><summary>Soluzione</summary>

(a) Conteggi: I 3 volte (seguita da am, am, do); am 2 (Sam, </s>); Sam 2 (</s>, I); not 1 (like).

- $P(\text{am}\mid\text{I}) = 2/3 \approx 0{,}667$
- $P(\text{Sam}\mid\text{am}) = 1/2$
- $P(\text{&lt;/s&gt;}\mid\text{am}) = 1/2$
- $P(\text{I}\mid\text{Sam}) = 1/2$
- $P(\text{like}\mid\text{not}) = 1/1 = 1$

(b) Con $P(\text{I}\mid\text{&lt;s&gt;}) = 2/3$, $P(\text{Sam}\mid\text{&lt;s&gt;}) = 1/3$, $P(\text{&lt;/s&gt;}\mid\text{Sam}) = 1/2$:

- $P(\text{&lt;s&gt; I am Sam &lt;/s&gt;}) = \frac23\cdot\frac23\cdot\frac12\cdot\frac12 = \frac19 \approx 0{,}111$
- $P(\text{&lt;s&gt; Sam I am &lt;/s&gt;}) = \frac13\cdot\frac12\cdot\frac23\cdot\frac12 = \frac1{18} \approx 0{,}056$
- $P(\text{&lt;s&gt; I am &lt;/s&gt;}) = \frac23\cdot\frac23\cdot\frac12 = \frac29 \approx 0{,}222$

La più probabile è *I am*, che **non è nel corpus**: il modello ricombina bigram visti (<s> I, I am, am </s>), e una frase più corta ha un fattore in meno.

(c) **0**: il bigram *like Sam* non compare mai, quindi $P(\text{Sam}\mid\text{like}) = 0/1 = 0$ e il prodotto si annulla, anche se la frase è grammaticale. È il problema degli zeri. Verificato con `fractions` e con `sentence_logprob` del notebook.

</details>

#### Esercizio 3 (scheda L04, libro 3.1): probabilità trigram

Scrivi l'equazione MLE di una probabilità trigram, modificando quella bigram $P(w_n\mid w_{n-1}) = C(w_{n-1}w_n)/C(w_{n-1})$. Poi scrivi tutte le probabilità trigram non nulle del corpus dell'esercizio 2, con due simboli <s> <s> all'inizio di ogni frase. Quante sono?

<details><summary>Soluzione</summary>

$$P(w_n\mid w_{n-2}w_{n-1}) = \frac{C(w_{n-2}\,w_{n-1}\,w_n)}{C(w_{n-2}\,w_{n-1})}$$

dove il denominatore conta il bigram come **contesto** (cioè seguito da qualcosa).

Frasi: <s> <s> I am Sam </s>; <s> <s> Sam I am </s>; <s> <s> I do not like green eggs and ham </s>. Occorrenze di trigram: 4 + 4 + 9 = 17, di cui 16 distinte (*<s> <s> I* compare due volte).

- contesto <s> <s> (3): $P(\text{I}) = 2/3$, $P(\text{Sam}) = 1/3$
- contesto <s> I (2): $P(\text{am}) = 1/2$, $P(\text{do}) = 1/2$
- contesto I am (2): $P(\text{Sam}) = 1/2$, $P(\text{&lt;/s&gt;}) = 1/2$
- probabilità 1 (contesto visto una volta): $P(\text{&lt;/s&gt;}\mid\text{am Sam})$, $P(\text{I}\mid\text{&lt;s&gt; Sam})$, $P(\text{am}\mid\text{Sam I})$, $P(\text{not}\mid\text{I do})$, $P(\text{like}\mid\text{do not})$, $P(\text{green}\mid\text{not like})$, $P(\text{eggs}\mid\text{like green})$, $P(\text{and}\mid\text{green eggs})$, $P(\text{ham}\mid\text{eggs and})$, $P(\text{&lt;/s&gt;}\mid\text{and ham})$

Totale: **16** probabilità trigram non nulle (6 minori di 1, 10 uguali a 1). Ogni contesto ha le sue probabilità che sommano a 1. Verificato con `train(SAM, 3)` del notebook (cella 4) e con un'implementazione indipendente.

</details>

#### Esercizio 4 (scheda L04, libro 3.2): il Berkeley Restaurant Project

Con la tabella bigram BeRP della lezione (identica nella scheda) e $P(\text{i}\mid\text{&lt;s&gt;}) = 0{,}25$, $P(\text{english}\mid\text{want}) = 0{,}0011$, $P(\text{food}\mid\text{english}) = 0{,}5$, $P(\text{&lt;/s&gt;}\mid\text{food}) = 0{,}68$: (a) calcola $P(\text{&lt;s&gt; i want chinese food &lt;/s&gt;})$; quante volte è più probabile della frase con *english* (0,000031)? (b) Calcola $P(\text{&lt;s&gt; i want to eat chinese food &lt;/s&gt;})$. (c) Quanto vale $P(\text{&lt;s&gt; i want to spend lunch &lt;/s&gt;})$? Quale fattore è responsabile?

<details><summary>Soluzione</summary>

(a) $0{,}25\times P(\text{want}\mid\text{i})\,0{,}33\times P(\text{chinese}\mid\text{want})\,0{,}0065\times P(\text{food}\mid\text{chinese})\,0{,}52\times0{,}68 = 1{,}896\cdot10^{-4} \approx \mathbf{0{,}00019}$. Rapporto con la frase *english*: i fattori comuni ($0{,}25$, $0{,}33$, $0{,}68$) si semplificano, $\frac{0{,}0065\times0{,}52}{0{,}0011\times0{,}5} = \frac{0{,}00338}{0{,}00055} = \mathbf{6{,}15}$ (circa 6 volte; con i valori arrotondati $0{,}00019/0{,}000031 = 6{,}1$).

(b) Sette fattori: $0{,}25\times0{,}33\times P(\text{to}\mid\text{want})\,0{,}66\times P(\text{eat}\mid\text{to})\,0{,}28\times P(\text{chinese}\mid\text{eat})\,0{,}021\times0{,}52\times0{,}68 = 1{,}13\cdot10^{-4} \approx \mathbf{0{,}00011}$. Due parole in più ma solo 1,7 volte meno probabile della (a): *want to* (0,66) e *to eat* (0,28) sono transizioni molto probabili.

(c) **0**. I fattori sono $0{,}25\times0{,}33\times0{,}66\times P(\text{spend}\mid\text{to})\,0{,}087\times P(\text{lunch}\mid\text{spend})\times P(\text{&lt;/s&gt;}\mid\text{lunch})$, e $P(\text{lunch}\mid\text{spend}) = 0$ ($C(\text{spend lunch}) = 0$ nella tabella dei conteggi): basta quel fattore ad annullare tutto, qualunque sia $P(\text{&lt;/s&gt;}\mid\text{lunch})$ (che non è dato). Tutti i prodotti verificati in Python.

</details>

#### Esercizio 5 (scheda L04): log probabilità

Supponi che ogni probabilità bigram di un testo valga circa 0,01. (a) Qual è la probabilità di una frase di 10 parole? Scrivila come potenza di dieci, poi come log probabilità naturale ($\ln 0{,}01 \approx -4{,}605$). (b) Il più piccolo numero positivo rappresentabile in un double a 64 bit è circa $10^{-308}$. Dopo quante parole il prodotto va in underflow? Che cosa succede invece alla somma dei log?

<details><summary>Soluzione</summary>

(a) Dieci fattori: $0{,}01^{10} = (10^{-2})^{10} = \mathbf{10^{-20}}$. Log naturale: $10\times\ln 0{,}01 = 10\times(-4{,}605) = \mathbf{-46{,}05}$ (esatto $-46{,}0517$). (Contando anche </s> sarebbero 11 fattori: $10^{-22}$, $-50{,}66$.)

(b) $0{,}01^n = 10^{-2n} &lt; 10^{-308}$ quando $2n &gt; 308$, cioè da **$n = 155$ parole** (a 154 si è esattamente al limite). Precisazione: $10^{-308}$ è circa il più piccolo double *normale* ($2{,}2\cdot10^{-308}$); sotto ci sono i numeri subnormali, e in Python il prodotto diventa esattamente 0 a $n = 162$ (verificato moltiplicando in un ciclo). In ogni caso qualche centinaio di parole basta. La somma dei log invece cresce linearmente: $-4{,}605\,n$, per 155 parole $-713{,}8$, per un milione di parole $-4{,}6\cdot10^{6}$: numeri perfettamente rappresentabili. Per questo i LM lavorano sempre in log.

</details>

#### Esercizio 6 (scheda L04): training, development e test set

Che cosa c'è di sbagliato, se c'è qualcosa, e che cosa faresti invece? (a) Per scegliere tra bigram e trigram un collega calcola la perplexity di entrambi sul test set, sceglie il migliore, poi prova anche un 4-gram sul test set e tiene il migliore dei tre. (b) Un LM è addestrato su una raccolta di articoli di giornale; il test set è un campione casuale di frasi dagli stessi articoli. (c) Un LM per il riconoscimento vocale di lezioni di chimica è testato su frasi di giornale, dove la perplexity è più facile da confrontare con risultati pubblicati.

<details><summary>Soluzione</summary>

(a) **Sbagliato**: usare il test set per scegliere il modello (qui l'ordine $N$, un iperparametro) è **tuning sul test set**; dopo tre confronti la perplexity del vincitore è una stima ottimistica, non più «unbiased». Fare tutti i confronti sul **development set** e usare il test set una volta sola, alla fine, sul modello scelto.

(b) **Sbagliato**: se le frasi di test sono anche nel training è **data contamination** (probabilità artificialmente alte, perplexity troppo bassa). Anche togliendole dal training, frasi degli stessi articoli condividono nomi, argomenti e formulazioni: la stima resta ottimistica. Dividere per **documento** (articoli interi nel test, mai visti in training), meglio se anche di periodi o fonti diversi, se l'uso previsto lo richiede.

(c) **Sbagliato**: il test set deve **rispecchiare il compito** (scheda 28): per lezioni di chimica servono trascrizioni di lezioni di chimica. Il confronto con la letteratura si può fare in aggiunta, su un test standard, ma non decide quale modello usare per questo compito. E alla fine conviene una valutazione estrinseca (WER del riconoscitore).

</details>

#### Esercizio 7 (scheda L04): perplexity di un modello bigram

Usa il modello bigram dell'esercizio 2; conta </s> in $N$ ma non <s>. (a) Calcola la perplexity sul test set <s> I am Sam </s> e sul test set di due frasi <s> I am Sam </s> <s> Sam I am </s>. (b) Calcola la perplexity su <s> I am </s>. Perché è più bassa? (c) Qual è la perplexity su <s> I do not like Sam </s>? (d) Perché le perplexity in (a) sono ottimistiche?

<details><summary>Soluzione</summary>

(a) <s> I am Sam </s>: $P = 1/9$, $N = 4$ (I, am, Sam, </s>), $\text{PP} = 9^{1/4} = \sqrt3 = \mathbf{1{,}732}$. Due frasi: $P = \frac19\cdot\frac1{18} = \frac1{162}$, $N = 8$, $\text{PP} = 162^{1/8} = \mathbf{1{,}889}$. (La seconda frase da sola avrebbe $18^{1/4} = 2{,}06$; la perplexity del test di due frasi è la media geometrica per token su tutto il test, non la media delle due perplexity.)

(b) $P = 2/9$, $N = 3$, $\text{PP} = (9/2)^{1/3} = 4{,}5^{1/3} = \mathbf{1{,}651}$. È più bassa perché la probabilità media **per token** è più alta: i tre fattori sono 2/3, 2/3, 1/2 (media geometrica $0{,}606$), mentre *I am Sam* aggiunge due fattori da 1/2 al posto di uno ($P(\text{Sam}\mid\text{am})$ e $P(\text{&lt;/s&gt;}\mid\text{Sam})$ invece di $P(\text{&lt;/s&gt;}\mid\text{am})$), media geometrica $0{,}577$. Non conta la lunghezza in sé, grazie alla normalizzazione.

(c) $P = 0$ (bigram *like Sam* mai visto), quindi $\text{PP} = 0^{-1/6}$: **infinita / non definita**. Il modello non smussato non è valutabile su questo test.

(d) Le frasi di test **sono nel corpus di training**: è training on the test set, i bigram sono stati stimati proprio su quelle frasi. Su testo nuovo la perplexity sarebbe più alta (o infinita, come in (c)). Valori verificati con `perplexity` del notebook e con `fractions`.

</details>

#### Esercizio 8 (scheda L04, libro 3.12): perplexity unigram

Un training set di 100 numeri contiene 91 zeri e una volta ciascuna le cifre da 1 a 9. Si addestra un modello unigram e si vede il test set *0 0 0 0 0 3 0 0 0 0*. (a) Qual è la perplexity unigram del test set? (b) Quanto sarebbe se il test fossero dieci zeri? E se fosse *1 2 3 4 5 6 7 8 9*?

<details><summary>Soluzione</summary>

MLE: $P(0) = 91/100 = 0{,}91$, $P(d) = 1/100 = 0{,}01$ per $d = 1,\dots,9$.

(a) Nove zeri e un 3, $N = 10$: $P = 0{,}91^9\times0{,}01 = 0{,}3894\times0{,}01 = 0{,}003894$. $\text{PP} = 0{,}003894^{-1/10} = \mathbf{1{,}725}$. In log: $-\frac1{10}(9\ln0{,}91 + \ln0{,}01) = -\frac1{10}(-0{,}8488 - 4{,}6052) = 0{,}5454$, $e^{0{,}5454} = 1{,}725$.

(b) Dieci zeri: $\text{PP} = (0{,}91^{10})^{-1/10} = 1/0{,}91 = \mathbf{1{,}099}$. Le cifre 1-9: $\text{PP} = (0{,}01^9)^{-1/9} = 1/0{,}01 = \mathbf{100}$.

Lettura: le dieci cifre danno un fattore di ramificazione 10, ma la perplexity pesata dipende dall'accordo tra modello e test: 1,1 se il test è tutto ciò che il modello si aspetta, 100 (più di 10!) se il test è fatto solo di ciò che il modello considera raro. Verificato con `unigram_perplexity` del notebook (1,725).

</details>

#### Esercizio 9 (scheda L04): fattore di ramificazione medio pesato

Linguaggio {red, blue, green}, fattore di ramificazione 3, test $T$ = *red red red red blue*. A dà 1/3 a ogni colore (perplexity 3), B dà $P(\text{red}) = 0{,}8$, $P(\text{green}) = P(\text{blue}) = 0{,}1$ (perplexity 1,89). (a) Calcola la perplexity su $T$ del modello C con $P(\text{red}) = 0{,}5$, $P(\text{blue}) = 0{,}25$, $P(\text{green}) = 0{,}25$. (b) Il modello D dà $P(\text{blue}) = 0{,}8$, $P(\text{red}) = 0{,}1$, $P(\text{green}) = 0{,}1$. Senza calcolare, la sua perplexity su $T$ è più alta o più bassa di quella di A? Poi calcolala. (c) Un modello può avere perplexity minore di 1 su qualche test? Può averla più alta del fattore di ramificazione?

<details><summary>Soluzione</summary>

(a) $P_C(T) = 0{,}5^4\times0{,}25 = 0{,}0625\times0{,}25 = 0{,}015625 = 1/64$. $\text{PP} = 64^{1/5} = 2^{6/5} = \mathbf{2{,}297}$: tra B (1,89) e A (3), perché C favorisce il rosso ma meno di B.

(b) **Più alta**: D concentra la probabilità sul blu, ma il test è quasi tutto rosso, a cui D dà solo 0,1 (meno di 1/3). Calcolo: $P_D(T) = 0{,}1^4\times0{,}8 = 8\cdot10^{-5}$, $\text{PP} = (8\cdot10^{-5})^{-1/5} = 12500^{1/5} = \mathbf{6{,}60}$.

(c) **Minore di 1, no**: ogni probabilità è $\le 1$, quindi $P(W) \le 1$ e $P(W)^{-1/N} \ge 1$; vale 1 solo se ogni token ha probabilità 1 (modello perfetto). **Più alta del fattore di ramificazione, sì**: D ha 6,60 > 3. L'interpretazione come «fattore di ramificazione medio pesato» vale quando il modello descrive bene il test (e un modello uniforme ha esattamente $k$); un modello che sbaglia sistematicamente è più «perplesso» di uno che tira a caso. Tutti i valori verificati in Python.

</details>

#### Esercizio 10 (scheda L04): campionare a mano

(a) Unigram con the 0,5, a 0,3, cat 0,15, </s> 0,05. Dividi [0, 1] in un intervallo per parola, in quest'ordine, e genera parole dai numeri casuali 0,62, 0,13, 0,91, 0,47, 0,97. Che frase ottieni? (b) Campiona dal modello bigram dell'esercizio 2 con i numeri 0,4, 0,5, 0,2, 0,9, in quest'ordine, uno per parola generata. A ogni passo ordina le possibili parole successive come compaiono per la prima volta nel corpus e dai a ciascuna un intervallo proporzionale alla sua probabilità bigram. Quali parole ottieni, e la frase è finita dopo il quarto numero? (c) Dai due frasi che il modello bigram dell'esercizio 2 può generare e che non sono nel corpus. Quante frasi diverse può generare?

<details><summary>Soluzione</summary>

(a) Intervalli: the [0; 0,5), a [0,5; 0,8), cat [0,8; 0,95), </s> [0,95; 1]. 0,62 → *a*; 0,13 → *the*; 0,91 → *cat*; 0,47 → *the*; 0,97 → </s>. Frase: ***a the cat the***, poi fine. Nessuna coerenza: le parole sono indipendenti.

(b)

- Contesto <s>: I [0; 2/3), Sam [2/3; 1). 0,4 → **I**.
- Contesto I: am [0; 2/3), do [2/3; 1). 0,5 → **am**.
- Contesto am: Sam [0; 1/2) (primo in *I am Sam*), </s> [1/2; 1). 0,2 → **Sam**.
- Contesto Sam: </s> [0; 1/2) (primo in *I am Sam </s>*), I [1/2; 1). 0,9 → **I**.

Parole: **I am Sam I**; la frase **non è finita**: </s> non è uscito, e il prossimo numero sceglierebbe tra am e do. Verificato con una simulazione in Python con lo stesso ordinamento.

(c) Per esempio *I am*, *Sam I am Sam*, *I am Sam I do not like green eggs and ham*, *Sam I do not like green eggs and ham*: tutte fatte di bigram visti ma assenti dal corpus. Il modello può generare **infinite** frasi diverse: il ciclo Sam → I → am → Sam può ripetersi quante volte si vuole (*I am Sam I am Sam I am*...), con probabilità che decresce geometricamente ma non si annulla. La somma delle probabilità di tutte le frasi vale comunque 1 (verificato numericamente).

</details>

#### Esercizio 11 (scheda L04): sparsità in Shakespeare

Le opere complete di Shakespeare contengono $N = 884.647$ token e $V = 29.066$ tipi. (a) Quanti bigram e trigram possibili ci sono su questo vocabolario? (b) Al massimo quanti bigram distinti possono comparire nel corpus? Che frazione dei bigram possibili è, e che cosa dice della tabella dei conteggi bigram? (c) Usa questi numeri per spiegare perché le frasi 4-gram campionate nella lezione erano prese quasi alla lettera da Shakespeare, mentre quelle unigram no.

<details><summary>Soluzione</summary>

(a) Bigram: $V^2 = 29.066^2 = 844.832.356 \approx 8{,}45\cdot10^8$ (gli «844 milioni» della slide). Trigram: $V^3 = 24.555.897.259.496 \approx 2{,}46\cdot10^{13}$. (Per completezza $V^4 \approx 7{,}14\cdot10^{17}$.)

(b) Un testo di $N$ token contiene $N-1$ bigram (occorrenze), quindi al massimo **884.646** bigram distinti (con i simboli di frase qualcuno in più, uno per frase; l'ordine di grandezza non cambia). Frazione: $884.646 / 844.832.356 = 0{,}00105$, cioè **al più lo 0,105%**. Almeno il 99,9% della tabella dei conteggi bigram è zero: la tabella è **ridicolmente sparsa**, e nella realtà i bigram distinti sono molti meno di $N-1$ perché molti si ripetono.

(c) Il numero di 4-gram osservati è al più circa $8{,}8\cdot10^5$ su $7\cdot10^{17}$ possibili: quasi ogni contesto di tre parole compare una sola volta o poche volte, e ha quindi una o pochissime continuazioni (6 per *It cannot be*). Campionando, il generatore non ha scelta e ripercorre il testo originale: overfitting. L'unigram invece ha un'unica distribuzione su 29.066 parole, estratte indipendentemente: nessun contesto da copiare, quindi nessuna frase del corpus riprodotta (ma nemmeno coerenza). Il notebook mostra lo stesso fenomeno: 76 frasi 4-gram su 200 copiate, 0 bigram.

</details>

#### Esercizio 12 (scheda L04): corpus di training e zeri

(a) Un modello trigram addestrato sul Wall Street Journal serve a calcolare la perplexity di una raccolta di tweet. Ti aspetti una perplexity più alta o più bassa che su un test WSJ? Perché? (b) Un corpus di training contiene le parole *ruby* e *slippers* ma mai la sequenza *ruby slippers*. Quanto vale $P(\text{slippers}\mid\text{ruby})$ con la MLE, e che cosa succede alla probabilità e alla perplexity di un test set che contiene la sequenza? (c) Vero o falso, e perché: con un tokenizer BPE il test set non può mai contenere un token mai visto, quindi un modello bigram su token BPE non assegna mai probabilità zero a un test set.

<details><summary>Soluzione</summary>

(a) **Più alta** (molto): genere e varietà diversi ([scheda 45](L04-modelli-linguistici-n-gram.md#p-45)). I tweet hanno lessico, grafie (*u, den, finna*), hashtag, menzioni, frasi brevi e sintassi colloquiale che nel WSJ non ci sono: molti trigram (e anche parole) del test hanno probabilità bassa o nulla. Senza smoothing la perplexity è quasi certamente **infinita**, per gli zeri.

(b) $P_{\text{MLE}}(\text{slippers}\mid\text{ruby}) = C(\text{ruby slippers})/C(\text{ruby}) = 0/C(\text{ruby}) = \mathbf{0}$. La probabilità di qualunque frase (e dell'intero test set) che contiene la sequenza è 0; la perplexity è $0^{-1/N}$, **non calcolabile** (infinita): non si divide per zero. Serve lo smoothing.

(c) **Falso**. La prima parte è vera: con BPE (soprattutto byte-level) ogni parola si scompone in token del vocabolario, quindi non ci sono token sconosciuti. Ma un modello bigram assegna probabilità a **coppie** di token: una coppia di token noti può non essere mai comparsa nel training (ogni parola nuova, come *Jurafsky*, si spezza in pezzi la cui sequenza non è mai stata vista), e la sua MLE è 0. BPE elimina le parole sconosciute, non gli n-gram sconosciuti. Solo un modello unigram, e solo se ogni token del vocabolario compare almeno una volta nel training, eviterebbe gli zeri.

</details>

#### Esercizio aggiuntivo A: perché serve </s>

Vocabolario {a, b}. Un modello bigram senza simbolo di fine ha $P(\text{a}\mid\text{&lt;s&gt;}) = P(\text{b}\mid\text{&lt;s&gt;}) = 1/2$ e $P(\text{a}\mid x) = P(\text{b}\mid x) = 1/2$ per ogni $x$. (a) Quanto sommano le probabilità di tutte le frasi di lunghezza 1? E di lunghezza 2? E di tutte le frasi di lunghezza 1, 2 o 3 insieme? (b) Ora aggiungi </s>: $P(\text{a}\mid x) = P(\text{b}\mid x) = 0{,}4$, $P(\text{&lt;/s&gt;}\mid x) = 0{,}2$ per $x \in \{\text{a},\text{b}\}$, e da <s> ancora 1/2 e 1/2. Quanto vale la probabilità totale delle frasi di lunghezza $k$? Quanto sommano su tutte le lunghezze?

<details><summary>Soluzione</summary>

(a) Lunghezza 1: *a*, *b*, $1/2 + 1/2 = 1$. Lunghezza 2: quattro frasi da $1/4$, somma 1. Lunghezza 3: otto frasi da $1/8$, somma 1. Tutte insieme: $1+1+1 = 3$. Senza </s> il modello definisce **una distribuzione per ogni lunghezza**, e sommando su tutte le lunghezze si ottiene infinito: non è una distribuzione sulle frasi (nota a piè di pagina del libro, [scheda 14](L04-modelli-linguistici-n-gram.md#p-14)).

(b) Una frase di lunghezza $k$ è: prima parola (probabilità 1/2 per ciascuna delle 2), $k-1$ parole successive (0,4 ciascuna), poi </s> (0,2). Massa di tutte le frasi di lunghezza $k$: $2^k\cdot\frac12\cdot0{,}4^{k-1}\cdot0{,}2 = 0{,}8^{k-1}\cdot0{,}2$. Somma su $k \ge 1$: $0{,}2\sum_{j\ge0}0{,}8^j = 0{,}2\cdot\frac1{1-0{,}8} = \mathbf{1}$. Con </s> la massa si divide tra le lunghezze (geometricamente decrescente) e il totale è 1. Verificato numericamente (somma troncata a $k = 200$: 1,0000).

</details>

#### Esercizio aggiuntivo B: dalla tabella dei conteggi alle probabilità

Con i conteggi BeRP della [scheda 17](L04-modelli-linguistici-n-gram.md#p-17) e gli unigrammi della [scheda 19](L04-modelli-linguistici-n-gram.md#p-19): (a) calcola $P(\text{want}\mid\text{i})$, $P(\text{spend}\mid\text{to})$, $P(\text{food}\mid\text{chinese})$, $P(\text{chinese}\mid\text{food})$ con quattro cifre significative. (b) La riga *want* della tabella delle probabilità somma a 0,68 sulle otto colonne. È un errore? (c) Perché $C(\text{i want}) = 827$ ma $C(\text{want i}) = 2$?

<details><summary>Soluzione</summary>

(a) $827/2533 = 0{,}3265$; $211/2417 = 0{,}08730$; $82/158 = 0{,}5190$; $1/1093 = 0{,}0009149$. Arrotondati a due cifre: 0,33; 0,087; 0,52; 0,00091 (la slide scrive 0,00092, [scheda 19](L04-modelli-linguistici-n-gram.md#p-19)).

(b) No: la somma sulle otto colonne mostrate è $629/927 = 0{,}679$; il resto (0,32) va alle altre 1438 parole del vocabolario e a </s> (*want a*, *want some*...). La riga somma a 1 solo sull'intero vocabolario. Allo stesso modo la riga *i* somma 0,33 e *spend* 0,007 sulle colonne mostrate.

(c) Il bigram è ordinato: $C(\text{i want})$ conta *want* dopo *i* (frequentissimo: *i want to...*), $C(\text{want i})$ conta *i* dopo *want*, raro in inglese. Le matrici di conteggi e probabilità **non sono simmetriche**. Tutti i valori ricalcolati in Python.

</details>

### Domande tipo orale

<details><summary>Che cos'è un modello linguistico? Perché le due definizioni (parola successiva, probabilità di una frase) sono equivalenti?</summary>

Traccia: (1) modello che predice le parole successive: una distribuzione sul vocabolario data la storia, $\sum_w P(w\mid h) = 1$; (2) oppure una probabilità per ogni sequenza (frase ordinata vs rimescolata); (3) equivalenza: regola della catena, $P(w_{1:n}) = \prod_k P(w_k\mid w_{1:k-1})$; chi sa predire la parola successiva sa calcolare la probabilità di una frase e viceversa; (4) con </s> la distribuzione è sulle frasi di qualunque lunghezza; (5) usi: LLM, correzione, parlato, AAC; (6) in pratica su token BPE.

</details>

<details><summary>Perché non si può stimare P(w | h) contando storie intere? Che cosa fa l'assunzione di Markov?</summary>

Traccia: (1) frequenza relativa $C(hw)/C(h)$; (2) la lingua è creativa: storie lunghe quasi mai viste, denominatore 0 o piccolo, stime inaffidabili, nemmeno il web basta; (3) Markov: $P(w_n\mid w_{1:n-1}) \approx P(w_n\mid w_{n-N+1:n-1})$, bigram guarda una parola, trigram due; (4) sostituita nella catena: prodotto di probabilità bigram; (5) prezzo: si perde il contesto lontano (dipendenze a lunga distanza); compromesso tra contesto e sparsità.

</details>

<details><summary>Come si stimano le probabilità di un modello n-gram? Perché si chiama massima verosimiglianza?</summary>

Traccia: (1) MLE: $P(w_n\mid w_{n-1}) = C(w_{n-1}w_n)/C(w_{n-1})$, generalizzata a $N$; (2) il denominatore è la somma della riga, che coincide con il conteggio unigram; righe normalizzate; (3) massima verosimiglianza: i parametri che massimizzano $P(\text{training}\mid\text{modello})$; esempio Chinese 400/1.000.000; (4) limiti: si adatta al training, probabilità 0 agli eventi mai visti, stime rumorose per conteggi piccoli; (5) esempio I am Sam: $P(\text{I}\mid\text{&lt;s&gt;}) = 2/3$.

</details>

<details><summary>A che cosa servono i simboli <s> e </s>?</summary>

Traccia: (1) <s> dà alla prima parola un contesto bigram ($P(\text{I}\mid\text{&lt;s&gt;}) = 2/3$); per un n-gram servono $N-1$ simboli <s>; (2) </s> fa sì che il modello sia una vera distribuzione sulle frasi: senza, le probabilità sommano a 1 per ogni lunghezza separatamente (totale infinito); con </s> il modello decide quando fermarsi; (3) nel conteggio di $N$ per la perplexity </s> si conta, <s> no (è predetto con probabilità quasi 1 dopo </s>, transizione finta); (4) nel campionamento si parte da <s> e ci si ferma a </s>.

</details>

<details><summary>Descrivi l'esempio del Berkeley Restaurant Project: come si passa dai conteggi alle probabilità e alla probabilità di una frase?</summary>

Traccia: (1) 9332 richieste, minuscolo, niente punteggiatura, V = 1446; (2) tabella dei conteggi 8×8 (righe = prima parola), molti zeri (metà delle celle), C(i want) = 827; (3) ogni cella diviso l'unigram della riga: $P(\text{want}\mid\text{i}) = 827/2533 = 0{,}33$; le righe sommano a 1 sull'intero vocabolario, non sulle 8 colonne; (4) *i want english food*: cinque bigram con <s> e </s>, $0{,}25\times0{,}33\times0{,}0011\times0{,}5\times0{,}68 = 0{,}000031$; chinese circa 6 volte più probabile; (5) le probabilità codificano sintassi, compito e cultura.

</details>

<details><summary>Perché si usano le log probabilità?</summary>

Traccia: (1) probabilità $\le 1$, il prodotto di molte decresce esponenzialmente; (2) underflow: sotto circa $10^{-308}$ il double diventa 0 (con 0,01 per parola dopo circa 155 parole); (3) $\prod p_i = \exp(\sum\log p_i)$: si sommano i log, numeri moderati; (4) si memorizza e si calcola tutto in log, si torna con exp solo per riportare una probabilità; (5) log naturale per convenzione; (6) probabilità 0 → $-\infty$.

</details>

<details><summary>Valutazione estrinseca e intrinseca: differenze, pro e contro.</summary>

Traccia: (1) estrinseca: modello dentro un'applicazione (riconoscitore vocale, traduttore), si misura il compito (per esempio WER), due esecuzioni per due modelli; unico modo di sapere se aiuta davvero; costosa; (2) intrinseca: qualità indipendente dall'applicazione, veloce, per iterare; la metrica standard è la perplexity, per n-gram e LLM; (3) un miglioramento di perplexity non garantisce un miglioramento nel compito, anche se di solito sono correlati: va confermato end-to-end.

</details>

<details><summary>Training, development e test set: a che cosa servono e quali errori evitare?</summary>

Traccia: (1) training: si imparano i parametri (i conteggi); dev: tutti i confronti e il tuning durante lo sviluppo; test: una volta sola alla fine, stima non distorta della generalizzazione; (2) il test deve rispecchiare il compito (chimica) o, per uso generale, molti testi e autori; dev dallo stesso tipo di testo del test; (3) mai allenare sul test (data contamination, probabilità gonfiate, perplexity troppo bassa); (4) non testare molte volte (tuning implicito); (5) dimensione: grande abbastanza per differenze statisticamente significative; (6) overfitting: perfetto sul training, inutile altrove.

</details>

<details><summary>Definisci la perplexity. Perché l'inversa e perché la radice N-esima?</summary>

Traccia: (1) $\text{PP}(W) = P(w_1\dots w_N)^{-1/N}$; (2) il criterio base è «migliore chi dà più probabilità al test», ma la probabilità dipende dalla lunghezza: la radice $N$-esima normalizza, per token; (3) l'inversa rende la misura «più bassa è meglio» e viene dalla teoria dell'informazione (entropia incrociata, §3.7): $\text{PP} = \exp(-\frac1N\sum\ln P(w_i\mid w_{&lt;i}))$; (4) minimizzare PP = massimizzare la probabilità del test; (5) dipende da testo e modello: confronta modelli sullo stesso test, con lo stesso vocabolario.

</details>

<details><summary>Come si calcola la perplexity di un modello bigram su un test set con più frasi? Che cosa si conta in N?</summary>

Traccia: (1) $\text{PP} = \sqrt[N]{\prod_{i=1}^N 1/P(w_i\mid w_{i-1})}$, media geometrica delle probabilità bigram inverse; (2) $W$ è l'intero test set, attraverso i confini di frase, non la media delle perplexity per frase; (3) si includono <s> e </s> nelle probabilità; in $N$ si conta un </s> per frase, non <s>; (4) esempio: <s> I am Sam </s> ha $P = 1/9$, $N = 4$, $\text{PP} = \sqrt3 = 1{,}73$; con due frasi $162^{1/8} = 1{,}89$; (5) per l'unigram la stessa formula con $P(w_i)$.

</details>

<details><summary>Perché la perplexity si può leggere come fattore di ramificazione medio pesato? Discuti l'esempio dei colori.</summary>

Traccia: (1) fattore di ramificazione: numero di parole che possono seguire; {red, blue, green} → 3; (2) modello A uniforme: $\text{PP} = ((1/3)^5)^{-1/5} = 3$, uguale al fattore di ramificazione; un modello uniforme su $k$ scelte ha PP $k$; (3) modello B con red 0,8: su red red red red blue $P = 0{,}04096$, PP 1,89: il branching factor è sempre 3, quello pesato scende perché il prossimo colore è prevedibile; (4) un modello sbilanciato nel verso sbagliato (blu 0,8) dà 6,6 > 3; (5) WSJ: trigram 109 = «come scegliere fra 109 parole».

</details>

<details><summary>Commenta la tabella di perplexity sul WSJ (962, 170, 109). Quali condizioni rendono confrontabili due perplexity?</summary>

Traccia: (1) unigram, bigram, trigram addestrati su 38 milioni di parole del WSJ, test di 1,5 milioni; (2) più contesto, più probabilità alle parole giuste, meno sorpresa; guadagno grande da uni a bi (5,7 volte), minore da bi a tri (1,56): rendimenti decrescenti; (3) condizioni: il modello non deve conoscere il test (altrimenti PP artificialmente bassa); stesso test set; vocabolari identici (un vocabolario ridotto con UNK abbassa la perplexity senza migliorare il modello); (4) perché è intrinseca, va confermata sul compito.

</details>

<details><summary>Come si campiona da un modello unigram e da un modello bigram?</summary>

Traccia: (1) campionare = scegliere secondo la probabilità, le frasi probabili più spesso (Shannon 1948, Miller e Selfridge 1950); (2) unigram: intervalli su [0, 1] proporzionali alle probabilità (retta cumulata: the 0,06, of fino a 0,09...), numero casuale, parola del suo intervallo, ripetere fino a </s>; (3) bigram: si parte da <s>, si estrae dalla riga del contesto corrente, la parola estratta diventa il contesto, fino a </s>; è generazione autoregressiva; (4) serve a vedere che cosa ha imparato il modello.

</details>

<details><summary>Che cosa mostrano le frasi generate da Shakespeare con unigram, bigram, trigram e 4-gram? Perché i 4-gram copiano?</summary>

Traccia: (1) unigram: parole indipendenti, nessuna coerenza né punteggiatura finale sensata; bigram: coerenza locale (*Live king. Follow.*); trigram: quasi Shakespeare; 4-gram: troppo (*It cannot be but so* è dal King John); (2) numeri: $N = 884.647$, $V = 29.066$, $V^2 \approx 8{,}4\cdot10^8$, $V^4 \approx 7\cdot10^{17}$; bigram osservati al più lo 0,1% dei possibili; (3) quasi ogni contesto lungo è visto una volta, dopo *It cannot be* solo 6 continuazioni: il generatore ripercorre il corpus; (4) è overfitting: ordini alti modellano sempre meglio il training fino a riprodurlo.

</details>

<details><summary>Perché il corpus di training conta? Discuti WSJ contro Shakespeare, genere e varietà di lingua.</summary>

Traccia: (1) WSJ (40 milioni di parole) e Shakespeare: entrambi inglese, ma nessuna sovrapposizione tra frasi generate e poca anche nei sintagmi; modelli quasi inutili se training e test sono così diversi; (2) genere: documenti legali per tradurre documenti legali; (3) dialetto e varietà: AAE (*finna*, *den*), Nigerian Pidgin; conta per social e parlato; (4) parole mai viste: con BPE ogni parola è una sequenza di subword noti, niente token sconosciuti; (5) ma gli n-gram mai visti restano; (6) collegamento con la lingua situata e i datasheet (L2).

</details>

<details><summary>Che cosa sono gli zeri e perché sono un problema? Qual è il rimedio?</summary>

Traccia: (1) n-gram assenti dal training ma presenti nel test; esempio *ruby slippers*, $P_{\text{MLE}} = 0$; (2) due problemi: sottostima di sequenze possibili (danneggia le applicazioni); probabilità 0 dell'intero test set, quindi perplexity non calcolabile (divisione per zero, log $-\infty$); (3) peggiorano con $n$: nel notebook 8% di zeri unigram, 46% bigram, 76% trigram sul test; (4) rimedio: smoothing/discounting, togliere massa agli eventi frequenti e darla a quelli mai visti (Laplace, add-k, interpolazione, backoff: prossima lezione).

</details>

<details><summary>Perché la perplexity di un n-gram sul proprio training set non è una valutazione? Che cosa succede al crescere di n?</summary>

Traccia: (1) è training on the test set: le probabilità sono stimate proprio su quei dati, nessuno zero, perplexity artificialmente bassa; (2) al crescere di $n$ sul training scende verso 1 (nel notebook 386, 20, 3,2, 1,78, 1,59 per n = 1-5): il modello memorizza; (3) sul test succede il contrario: più zeri, perplexity infinita senza smoothing; (4) è la definizione di overfitting: la scelta di $n$ va fatta sul devset; (5) stesso fenomeno del campionamento: 4-gram che copiano (76 frasi su 200).

</details>
