# L7 · Regressione logistica multinomiale e valutazione

*Multinomial Logistic Regression* · 02/10/2026 · Claudio Gallicchio · lettura: J&M cap. 4, §4.7-4.16

[Versione interattiva sul sito](https://gabriele-marsili.github.io/appunti-magistrale-ai/anno-2/hlt/sito/#L7) · [Indice della dispensa](README.md)

Seconda lezione sulla regressione logistica (J&M §4.7-4.16). Da due a $K$ classi: la **softmax** trasforma $K$ punteggi (logit) in una distribuzione, una riga della matrice dei pesi $W$ per classe (un **prototipo**), la **cross-entropy** diventa $-\log \hat y_c$ e il gradiente resta $(\hat y_k - y_k)\,x_i$. Poi la **valutazione**: matrice di confusione, perché l'accuracy inganna con classi sbilanciate, **precision, recall, F-measure**, macro e micro average, devset e **cross-validation**. Poi la **significatività statistica**: effect size, ipotesi nulla, p-value e **paired bootstrap test**. Chiude con danni dei classificatori e model card, interpretazione dei pesi e **regolarizzazione L2 e L1** (come prior gaussiano e laplaciano). Tutti i numeri delle slide sono ricalcolati; un piccolo errore di arrotondamento a pagina 9.

## Indice

- [Apertura](#apertura)
- [Regressione logistica multinomiale](#regressione-logistica-multinomiale)
- [Valutazione: precision, recall, F, cross-validation](#valutazione-precision-recall-f-cross-validation)
- [Significatività statistica](#significativita-statistica)
- [Danni, interpretazione e regolarizzazione](#danni-interpretazione-e-regolarizzazione)
- [Notebook](#notebook)
- [Studio ed esercizi](#studio-ed-esercizi)

## Apertura

<a id="p-1"></a>

### Slide 1 · Regressione logistica multinomiale

Settima lezione, seconda parte del capitolo 4 di J&M. La lezione precedente ha costruito la **regressione logistica binaria**: feature, somma pesata, **sigmoide**, **cross-entropy loss**, discesa del gradiente. Qui si fanno quattro passi:

- da 2 a $K$ classi con la **softmax** (regressione logistica multinomiale);
- come si **valuta** un classificatore: precision, recall, F-measure, cross-validation;
- come si decide se un classificatore è **davvero** migliore di un altro: test di significatività e **paired bootstrap**;
- danni sociali, interpretazione dei pesi e **regolarizzazione**.

Le idee di valutazione valgono per qualunque classificatore (Naive Bayes, regressione logistica, reti neurali, LLM usati come classificatori), non solo per questa lezione.

<a id="p-2"></a>

### Slide 2 · Indice della lezione

Quattro blocchi, nell'ordine del libro:

1. **Softmax**: generalizzazione della sigmoide a $K$ classi, matrice dei pesi, loss e gradiente (§4.7-4.8).
2. **Valutazione**: matrice di confusione, precision, recall, F-measure, macro/micro average, devset e cross-validation (§4.9-4.10).
3. **Significatività statistica**: effect size, p-value, paired bootstrap (§4.11).
4. **Danni, interpretazione, regolarizzazione**: tre sezioni brevi (§4.12-4.14).

A metà c'è la pausa, subito prima del confronto fra due classificatori.

<a id="p-3"></a>

### Slide 3 · Riferimento: J&M capitolo 4, §4.7-4.16

Lettura principale: **Jurafsky & Martin**, *Speech and Language Processing*, 3a ed. draft del 19 agosto 2026, capitolo 4 (*Logistic Regression and Text Classification*), sezioni 4.7-4.16:

- 4.7-4.8: regressione logistica multinomiale e il suo apprendimento;
- 4.9-4.10: valutazione; test set e cross-validation;
- 4.11: test di significatività statistica;
- 4.12-4.13: evitare danni; interpretare i modelli;
- 4.14-4.15 (*Advanced*): regolarizzazione; derivazione del gradiente (del caso binario);
- 4.16: riassunto e note storiche (la regressione logistica in NLP nasce negli anni '90 anche come *maximum entropy*, maxent).

Le sezioni 4.1-4.6 sono state l'oggetto della lezione 6. Il QR code porta al sito del libro.

## Regressione logistica multinomiale

<a id="p-4"></a>
**Slide 4 · Regressione logistica multinomiale** — Prima parte: più di due classi, con la softmax.

<a id="p-5"></a>

### Slide 5 · Più di due classi

Molti compiti di NLP hanno più di due classi:

- **sentiment a 3 vie**: positivo, negativo, neutro;
- **part of speech** di una parola: 10, 30 o anche 50 tag (tema della prossima lezione, cap. 18);
- **named entity**: tipo di un'espressione (persona, luogo, organizzazione);
- **predizione della parola successiva**: un LLM sceglie fra le $|V|$ parole del vocabolario, quindi è una classificazione a $|V|$ vie.

Il modello si chiama **regressione logistica multinomiale** o **softmax regression** (nella letteratura NLP più vecchia anche *maxent classifier*). L'ultimo esempio è il motivo per cui la softmax è così importante: lo strato finale di ogni language model neurale, compresi i transformer, è esattamente una softmax sui $|V|$ token, con loss cross-entropy (vedi la *next-token prediction* della L1).

<a id="p-6"></a>

### Slide 6 · Una sola classe corretta: vettori one-hot

Ogni osservazione appartiene a **una sola** delle $K$ classi (**hard classification**: un documento non può essere sia spam sia urgente).

- L'etichetta vera è un **vettore one-hot** di lunghezza $K$: $y_c = 1$ per la classe corretta $c$, $y_j = 0$ per tutte le altre. Esempio della slide: $K = 3$, classe corretta la seconda, $\mathbf y = [0, 1, 0]$.
- Il classificatore produce un vettore di stime $\hat{\mathbf y}$, con $\hat y_k$ = stima di $P(y_k = 1\mid x)$. Esempio: $\hat{\mathbf y} = [0{,}2,\ 0{,}7,\ 0{,}1]$: somma 1, e la classe più probabile (l'argmax) è proprio la seconda.

Questi due vettori, $\mathbf y$ e $\hat{\mathbf y}$, sono quelli che entrano nella loss ([scheda 17](L07-regressione-logistica-multinomiale-e-valutazione.md#p-17)) e nel gradiente ([scheda 21](L07-regressione-logistica-multinomiale-e-valutazione.md#p-21)): stesso esempio.

> **Approfondimento: E se un documento ha più etichette?**
>
> Il caso *multi-label* (un articolo che parla sia di sport sia di economia) non è hard classification: le classi non si escludono e la softmax, che obbliga le probabilità a sommare 1, non è il modello giusto. Si usano invece $K$ classificatori binari indipendenti, ognuno con la sua sigmoide (conoscenza standard, non nelle slide).

<a id="p-7"></a>

### Slide 7 · La funzione softmax

La **softmax** generalizza la sigmoide: prende $K$ punteggi reali qualsiasi e restituisce $K$ probabilità.

$$\text{softmax}(z_i) = \frac{\exp(z_i)}{\sum_{j=1}^{K}\exp(z_j)}\qquad 1 \le i \le K$$

- l'esponenziale rende tutto positivo (anche punteggi negativi);
- il denominatore normalizza: i $K$ valori sono in $[0, 1]$ e sommano a 1;
- conserva l'ordine: punteggio più alto, probabilità più alta.

La figura mette a confronto i due casi. **Binario**: un solo punteggio $z = 1{,}5$, la sigmoide dà $P(y=1\mid x) = \sigma(1{,}5) = 0{,}82$. **$K$ classi**: $z = [2{,}0;\ 0{,}5;\ -1{,}0]$ diventa $[0{,}79;\ 0{,}18;\ 0{,}04]$ (valori esatti 0,786, 0,175, 0,039: la somma degli arrotondati fa 1,01 solo per l'arrotondamento). Calcolo: $e^{2} = 7{,}389$, $e^{0{,}5} = 1{,}649$, $e^{-1} = 0{,}368$, somma 9,406.

> **Da saper fare: Softmax a mano**
>
> Tre passi: (1) esponenziale di ogni punteggio; (2) somma; (3) dividere ciascuno per la somma. Trucco per i conti a mano: sottrarre prima il massimo (non cambia nulla, [scheda 8](L07-regressione-logistica-multinomiale-e-valutazione.md#p-8)), così il più grande diventa $e^0 = 1$. Per $z = [2;\ 0{,}5;\ -1]$: $[1;\ e^{-1{,}5};\ e^{-3}] = [1;\ 0{,}223;\ 0{,}050]$, somma 1,273, risultato $[0{,}786;\ 0{,}175;\ 0{,}039]$.

<a id="p-8"></a>

### Slide 8 · Softmax di un vettore e logit

Applicata a tutto il vettore $\mathbf z = [z_1,\dots,z_K]$ la softmax restituisce un vettore:

$$\text{softmax}(\mathbf z) = \left[\frac{\exp(z_1)}{\sum_{i=1}^K \exp(z_i)},\ \dots,\ \frac{\exp(z_K)}{\sum_{i=1}^K \exp(z_i)}\right]$$

- il **denominatore è lo stesso** per tutte le componenti: è ciò che normalizza;
- i punteggi in ingresso si chiamano **logit**, come nel caso della sigmoide;
- come la sigmoide, la softmax **schiaccia**: il punteggio più grande viene spinto verso 1, gli altri soppressi. Il nome viene da qui: è una versione "morbida" dell'argmax.

Due proprietà da saper dimostrare (esercizio 1): **aggiungere la stessa costante** a tutti i logit non cambia nulla, perché $e^{z_i + c} = e^c e^{z_i}$ e $e^c$ si semplifica tra numeratore e denominatore; **moltiplicarli** per una costante maggiore di 1 rende la distribuzione più appuntita (per $[2,1,0]$ la probabilità massima passa da 0,665 a 0,867 raddoppiando i logit).

> **Approfondimento: Stabilità numerica**
>
> La prima proprietà è quella che si usa in pratica: si calcola $\text{softmax}(\mathbf z - \max_j z_j)$. Con logit grandi l'esponenziale va in overflow: in numpy `np.exp([1000, 1001, 999])` dà infinito e la divisione restituisce `nan`, mentre la versione con il massimo sottratto dà $[0{,}245;\ 0{,}665;\ 0{,}090]$ (verificato). Il notebook usa la versione stabile. Dividere i logit per una costante $T$ prima della softmax è la *temperatura* del campionamento negli LLM.

<a id="p-9"></a>

### Slide 9 · Softmax di un vettore: un esempio

L'esempio del libro (§4.7.1), con sei classi:

| $z$ | $\exp(z)$ | softmax |
| --- | --- | --- |
| 0,6 | 1,82 | 0,05 |
| 1,1 | 3,00 | 0,09 |
| −1,5 | 0,22 | 0,01 |
| 1,2 | 3,32 | 0,10 |
| 3,2 | 24,53 | 0,74 |
| −1,1 | 0,33 | 0,01 |

Il grafico a barre a destra mostra le sei probabilità: una barra lunga per $\hat y_5$, tutte le altre corte. Il punteggio più alto, $z_5 = 3{,}2$, prende il 74% della massa pur essendo "solo" 2 unità sopra il secondo ($z_4 = 1{,}2$): $e^{2} \approx 7{,}4$ volte più massa. I due logit negativi ($z_3$, $z_6$) restano all'1%. Valori esatti: $[0{,}0548;\ 0{,}0904;\ 0{,}0067;\ 0{,}0999;\ 0{,}7382;\ 0{,}0100]$ (verificati con numpy e nella cella 2 del notebook).

> **Attenzione (errore nelle slide): La somma degli esponenziali è 33,23, non 33,24**
>
> La riga *sum* della tabella riporta 33,24. La somma esatta è $e^{0{,}6}+e^{1{,}1}+e^{-1{,}5}+e^{1{,}2}+e^{3{,}2}+e^{-1{,}1} = 33{,}2349 \approx 33{,}23$; la somma dei valori arrotondati della colonna fa 33,22. Nessuna delle due dà 33,24. Errore di arrotondamento innocuo: le probabilità della tabella sono giuste. Verifica: `np.exp([0.6,1.1,-1.5,1.2,3.2,-1.1]).sum()` = 33,2349; anche la cella 2 del notebook stampa `sum 33.23`.

<a id="p-10"></a>

### Slide 10 · Softmax nella regressione logistica

Ogni classe $k$ ha il suo **vettore di pesi** $\mathbf w_k$ e il suo **bias** $b_k$. Il punteggio della classe è la somma pesata delle feature, $z_k = \mathbf w_k\cdot\mathbf x + b_k$, e la softmax trasforma i $K$ punteggi in probabilità:

$$P(y_k = 1\mid\mathbf x) = \frac{\exp(\mathbf w_k\cdot\mathbf x + b_k)}{\sum_{j=1}^{K}\exp(\mathbf w_j\cdot\mathbf x + b_j)}$$

La figura: tre feature ($x_1$ = numero di parole = 3, $x_2$ = parole del lessico positivo = 1, $x_3$ = occorrenze di *no* = 0) collegate con frecce a **tutti** e tre i punteggi (ogni freccia è un peso: $3\times 3 = 9$ pesi); punteggi $z = [2{,}0;\ 0{,}5;\ -1{,}0]$; dopo la softmax positivo 0,79, negativo 0,18, neutro 0,04. I valori dei pesi non sono mostrati: i punteggi sono quelli della [scheda 7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-7). Rispetto al binario cambia solo che i pesi sono $K$ vettori invece di uno.

<a id="p-11"></a>

### Slide 11 · Forma matriciale

I $K$ vettori di pesi diventano le **righe** di una matrice $W$ di forma $K\times f$ ($f$ = numero di feature), i $K$ bias un vettore $\mathbf b$:

$$\hat{\mathbf y} = \text{softmax}(W\mathbf x + \mathbf b)$$

La figura mostra le dimensioni: $W$ ($3\times 3$, una riga per classe: positivo in blu, negativo in rosso, neutro in verde) per $\mathbf x$ ($f\times 1$), più $\mathbf b$ ($K\times 1$), dà $\mathbf z$ ($K\times 1$), e la softmax dà $\hat{\mathbf y}$ ($K\times 1$). La riga $k$ di $W$ moltiplicata per $\mathbf x$ è proprio $\mathbf w_k\cdot\mathbf x$: un solo prodotto matrice-vettore calcola tutti i punteggi, ed è così che si implementa (GPU, numpy).

> **Approfondimento: Un mini-batch intero**
>
> Con $m$ esempi come righe di $X$ ($m\times f$) i punteggi di tutti gli esempi e tutte le classi sono $Z = XW^{\top} + \mathbf b$ ($m\times K$, il bias sommato a ogni riga) e la softmax si applica **riga per riga**, cioè lungo l'asse delle classi (`axis=1` in numpy, con `keepdims=True`). Normalizzare lungo l'asse sbagliato farebbe sommare a 1 le colonne, cioè gli esempi: è un errore classico. Il notebook lo fa correttamente (`softmax_rows`).

<a id="p-12"></a>

### Slide 12 · Le righe di W come prototipi

Interpretazione utile: ogni riga $\mathbf w_k$ è un **prototipo** (un *template*) della classe $k$. Il prodotto scalare $\mathbf w_k\cdot\mathbf x$ è grande quando $\mathbf x$ "assomiglia" al template, quindi funziona da **misura di similarità**; l'input va alla classe il cui prototipo gli somiglia di più (Doumbouya et al., 2025, citato dal libro). La figura è la stessa della scheda precedente: si guardano le righe colorate di $W$.

Conseguenza importante: la softmax dipende solo dalle **differenze** tra punteggi ([scheda 8](L07-regressione-logistica-multinomiale-e-valutazione.md#p-8)), quindi aggiungere lo stesso vettore a tutte le righe di $W$ non cambia le probabilità. Un singolo peso non si legge da solo: conta come si confronta con i pesi della stessa feature nelle altre righe. Per $K = 2$ questo porta esattamente alla regressione logistica binaria con $\mathbf w = \mathbf w_1 - \mathbf w_2$ (esercizio 2).

<a id="p-13"></a>

### Slide 13 · Regressione logistica binaria: un vettore di pesi

La figura del libro (Fig. 4.6, metà sinistra) per il caso binario: la frase *dessert was great* diventa un vettore di $f$ feature ($x_1$ = word count = 3, $x_2$ = parole del lessico positivo = 1, $x_3$ = conteggio di *no* = 0, ... $x_f$); le frecce blu sono i pesi di un **unico vettore** $\mathbf w$ di forma $1\times f$ che convergono su un solo nodo di uscita $\hat y$, uno scalare prodotto dalla sigmoide.

L'uscita è $\hat y = P(+)$ e la probabilità dell'altra classe è il complemento, $P(-) = 1 - P(+)$ (in figura scritto come $p(+) = 1 - p(-)$, che è la stessa cosa). Una sola probabilità basta perché con due classi la seconda è determinata dalla prima.

<a id="p-14"></a>

### Slide 14 · Regressione logistica multinomiale: una matrice di pesi

Metà destra della Fig. 4.6: le stesse $f$ feature, ma **tre nodi di uscita** $\hat y_1, \hat y_2, \hat y_3$ = $P(+)$, $P(-)$, $P(\text{neutro})$, prodotti dalla softmax. Ogni feature è collegata a ogni uscita: frecce blu verso $\hat y_1$, grigie tratteggiate verso $\hat y_2$, rosse verso $\hat y_3$. Le $f$ frecce rosse sono una riga di $W$, il vettore $\mathbf w_3$: i pesi della classe 3, cioè il suo **prototipo** (nota in figura).

- uscita: un vettore $\hat{\mathbf y}$ di forma $K\times 1$;
- pesi: $K$ vettori separati, impacchettati in $W$ di forma $K\times f$;
- i bias sono omessi dalla figura per chiarezza.

Numero di parametri: $Kf + K$ contro $f + 1$ del binario.

<a id="p-15"></a>

### Slide 15 · Feature nella regressione logistica multinomiale

La feature del punto esclamativo, $x_5 = 1$ se "!" compare nel documento, 0 altrimenti.

- **Binario**: un solo peso $w_5$; positivo spinge verso $y = 1$, negativo verso $y = 0$, il valore assoluto dice quanto conta.
- **Multinomiale**: un peso **per classe**, e la feature può essere evidenza a favore o contro *ciascuna* classe. Tabella del libro: $w_{5,+} = 3{,}5$, $w_{5,-} = 3{,}1$, $w_{5,0} = -5{,}3$: il punto esclamativo è indizio di un'opinione forte, positiva o negativa, e indizio *contro* il neutro.

Esempio (esercizio 5): punteggi uguali $[1, 1, 1]$, distribuzione uniforme; aggiungendo "!" diventano $[4{,}5;\ 4{,}1;\ -4{,}3]$ e $\hat{\mathbf y} = [0{,}599;\ 0{,}401;\ 0{,}0001]$. Il neutro sparisce, e tra positivo e negativo resta incertezza: conta solo la differenza $3{,}5 - 3{,}1 = 0{,}4$.

Il testo della slide contiene anche una riga sulla notazione $f(x, y)$, nascosta nella pagina renderizzata: siccome i pesi dipendono da input e classe, si scrivono tre feature $f_5(x,+)$, $f_5(x,-)$, $f_5(x,0)$, ciascuna con un solo peso (libro §4.7.3; servirà per i CRF del cap. 18).

<a id="p-16"></a>

### Slide 16 · La loss per K classi

La **cross-entropy binaria** della lezione precedente ha due termini, uno attivo quando $y = 1$ e uno quando $y = 0$:

$$L_{CE}(\hat y, y) = -\log p(y\mid x) = -[\,y\log\hat y + (1-y)\log(1-\hat y)\,]$$

Per $K$ classi diventa **un termine per classe**, con $\mathbf y$ e $\hat{\mathbf y}$ vettori:

$$L_{CE}(\hat{\mathbf y}, \mathbf y) = -\sum_{k=1}^{K} y_k\log\hat y_k$$

Il caso binario è il caso $K = 2$ con $\mathbf y = [y,\ 1-y]$ e $\hat{\mathbf y} = [\hat y,\ 1-\hat y]$. Il nome non è casuale: è la **cross-entropy** della L5 ([scheda 38 della L5](L05-smoothing-ed-entropia.md#p-38)) tra la distribuzione "vera" $\mathbf y$ (tutta la massa sulla classe corretta) e quella del modello $\hat{\mathbf y}$, con logaritmo naturale invece che in base 2.

<a id="p-17"></a>

### Slide 17 · Target one-hot: la negative log likelihood

Siccome $\mathbf y$ è one-hot, nella somma tutti i termini delle classi sbagliate sono moltiplicati per 0 e resta solo quello della classe corretta $c$:

$$L_{CE} = -\log\hat y_c$$

Per questo la loss si chiama anche **negative log likelihood loss**: è meno il log della probabilità assegnata alla risposta giusta.

Esempio della [scheda 6](L07-regressione-logistica-multinomiale-e-valutazione.md#p-6): $\mathbf y = [0, 1, 0]$, $\hat{\mathbf y} = [0{,}2;\ 0{,}7;\ 0{,}1]$. I termini sono $0\cdot\log 0{,}2 + 1\cdot\log 0{,}7 + 0\cdot\log 0{,}1$ e la loss è $-\ln 0{,}7 = 0{,}357 \approx 0{,}36$. Il logaritmo è **naturale** (in base 10 verrebbe 0,155): con il log naturale la derivata è più pulita.

<a id="p-18"></a>

### Slide 18 · La loss in funzione dei punteggi

Sostituendo la softmax, la loss diventa una funzione dei pesi:

$$L_{CE} = -\log\frac{\exp(\mathbf w_c\cdot\mathbf x + b_c)}{\sum_{j=1}^{K}\exp(\mathbf w_j\cdot\mathbf x + b_j)}$$

Il grafico a destra è la curva $-\log\hat y_c$ al variare di $\hat y_c$ fra 0 e 1: vale 0 per $\hat y_c = 1$ (predizione perfetta), cresce lentamente fino a circa 0,5 e poi esplode verso infinito quando $\hat y_c\to 0$. Il punto evidenziato è l'esempio: $\hat y_c = 0{,}7$, loss 0,36. Per abbassare la loss il modello deve alzare il punteggio della classe corretta **rispetto a tutti gli altri**: non basta che sia alto in assoluto.

> **Approfondimento: La forma log-sum-exp**
>
> Scrivendo $z_j = \mathbf w_j\cdot\mathbf x + b_j$: $L_{CE} = -z_c + \log\sum_j e^{z_j}$. Il secondo termine (*log-sum-exp*) è circa $\max_j z_j$: se la classe corretta ha già il punteggio massimo con largo margine, la loss è vicina a 0; se un'altra classe la supera di $d$, la loss è almeno circa $d$. È anche la forma da cui si deriva il gradiente in due righe ([scheda 20](L07-regressione-logistica-multinomiale-e-valutazione.md#p-20)) e quella che le librerie calcolano direttamente dai logit per stabilità numerica.

<a id="p-19"></a>

### Slide 19 · La loss sull'esempio della softmax

Con $\hat{\mathbf y} = [0{,}05;\ 0{,}09;\ 0{,}01;\ 0{,}10;\ 0{,}74;\ 0{,}01]$ della [scheda 9](L07-regressione-logistica-multinomiale-e-valutazione.md#p-9):

- **classe corretta 5**: $\mathbf y = [0,0,0,0,1,0]$, sopravvive solo il quinto termine, loss $-\ln 0{,}74 = 0{,}30$: il modello ha dato il 74% alla risposta giusta, loss piccola;
- **classe corretta 2**: sopravvive solo il secondo termine, loss $-\ln 0{,}09 = 2{,}41$ (2,40 con il valore non arrotondato 0,0904); con l'1% sarebbe stata $-\ln 0{,}01 = 4{,}6$.

La frase finale ("conta solo la classe corretta; abbassare le altre probabilità la alza") va letta così: nella *formula* compare solo $\hat y_c$, ma le altre probabilità entrano tramite il denominatore comune, perché la somma è 1: togliere massa alle classi sbagliate è l'unico modo per darne a quella giusta. Verificato in Python (cella 4 del notebook: 0,30 e 2,40).

<a id="p-20"></a>

### Slide 20 · Il gradiente per K classi

Derivata della loss rispetto al peso $w_{k,i}$ (feature $x_i$, classe $k$):

$$\frac{\partial L_{CE}}{\partial w_{k,i}} = -(y_k - \hat y_k)\,x_i = (\hat y_k - y_k)\,x_i$$

La slide scrive anche le due forme equivalenti, con $\hat y_k = p(y_k = 1\mid x)$ e con la softmax esplicita. Lettura: **errore sulla classe $k$** ($\hat y_k - y_k$, la probabilità data meno quella che si sarebbe dovuta dare) **per la feature** $x_i$. È la stessa forma del caso binario $(\hat y - y)\,x$, applicata classe per classe. Per il bias: $\partial L/\partial b_k = \hat y_k - y_k$. In forma matriciale il gradiente rispetto a $W$ è il prodotto esterno $(\hat{\mathbf y} - \mathbf y)\,\mathbf x^{\top}$, una matrice $K\times f$ come $W$.

> **Da saper fare: Derivare il gradiente (due righe)**
>
> Da $L = -z_c + \log\sum_j e^{z_j}$: $\dfrac{\partial L}{\partial z_k} = -[k = c] + \dfrac{e^{z_k}}{\sum_j e^{z_j}} = \hat y_k - y_k$. Poi la regola della catena con $z_k = \mathbf w_k\cdot\mathbf x + b_k$: $\partial z_k/\partial w_{k,i} = x_i$ e $\partial z_k/\partial b_k = 1$, mentre $z_k$ non dipende dai pesi delle altre righe. Verificato con il gradiente numerico nella cella 6 del notebook (differenza $10^{-10}$). Il libro (§4.15) deriva solo il caso binario, con la derivata della sigmoide $\sigma(1-\sigma)$.

<a id="p-21"></a>

### Slide 21 · Effetto di un aggiornamento

Esempio one-hot della [scheda 6](L07-regressione-logistica-multinomiale-e-valutazione.md#p-6), classe corretta la 2:

|  | $y$ | $\hat y$ | $\hat y - y$ | i suoi pesi |
| --- | --- | --- | --- | --- |
| classe 1 | 0 | 0,2 | +0,2 | scendono |
| classe 2 | 1 | 0,7 | −0,3 | salgono |
| classe 3 | 0 | 0,1 | +0,1 | scendono |

La discesa del gradiente fa $\mathbf w_k \leftarrow \mathbf w_k - \eta\,(\hat y_k - y_k)\,\mathbf x$: si muovono solo i pesi delle feature presenti ($x_i \ne 0$). La riga della classe corretta si sposta **verso** $\mathbf x$ (il prototipo assomiglia di più all'esempio), quelle sbagliate se ne **allontanano**, tanto più quanto più probabilità avevano preso. Le tre correzioni sommano a zero ($0{,}2 - 0{,}3 + 0{,}1 = 0$): vale sempre, perché $\sum_k\hat y_k = \sum_k y_k = 1$.

> **Da saper fare: Un passo completo (esercizio 4)**
>
> Con $W = [[2; -1{,}5], [-1; 2{,}5], [0{,}2; 0{,}3]]$, $\mathbf b = [0{,}5; 0; 1]$, $\mathbf x = [3, 2]$, classe corretta neutro: $\hat{\mathbf y} = [0{,}669;\ 0{,}149;\ 0{,}182]$, errore $[0{,}669;\ 0{,}149;\ -0{,}818]$, gradiente = errore per $\mathbf x$. Con $\eta = 0{,}1$ la riga neutra diventa $[0{,}445;\ 0{,}464]$ e la probabilità del neutro sale da 0,18 a 0,60 in un solo passo (loss da 1,70 a 0,51). Conti completi nell'esercizio 4 della sezione Studio.

## Valutazione: precision, recall, F, cross-validation

<a id="p-22"></a>
**Slide 22 · Valutazione** — Seconda parte: come si misura quanto funziona un classificatore.

<a id="p-23"></a>

### Slide 23 · La matrice di confusione

Per un compito binario di **rilevamento** (spam sì/no; tweet che parla della nostra azienda di torte sì/no) si confrontano le uscite del sistema con le **gold label**, le etichette umane che vogliamo riprodurre. La **matrice di confusione** ha le gold label sulle **colonne** e l'uscita del sistema sulle **righe**; quattro esiti:

|  | gold positivo | gold negativo |
| --- | --- | --- |
| sistema positivo | true positive (tp) | false positive (fp) |
| sistema negativo | false negative (fn) | true negative (tn) |

In figura le celle corrette (diagonale) sono blu, gli errori rossi; ai margini le tre formule: $\text{precision} = \frac{tp}{tp+fp}$ accanto alla riga "sistema positivo", $\text{recall} = \frac{tp}{tp+fn}$ sotto la colonna "gold positivo", $\text{accuracy} = \frac{tp+tn}{tp+fp+tn+fn}$ in basso a destra. Regola mnemonica: la precision legge la **riga** (ciò che il sistema ha detto positivo), la recall la **colonna** (ciò che è davvero positivo). Le stesse misure le abbiamo già usate per la regex di *the* ([scheda 12 della L3](L03-elaborazione-del-testo.md#p-12)).

<a id="p-24"></a>

### Slide 24 · Accuracy e classi sbilanciate

L'**accuracy** è la percentuale di osservazioni etichettate correttamente (riquadro evidenziato in figura). Sembra la misura naturale, ma **non funziona con classi sbilanciate**.

Esempio del libro: un milione di tweet, solo 100 parlano della torta. Un classificatore che risponde sempre "non parla della torta" ha 999.900 true negative e 100 false negative: accuracy $999.900/1.000.000 = 99{,}99\%$. E non trova **niente** di ciò che cercavamo.

In generale un classificatore che predice sempre la classe maggioritaria ha accuracy pari alla frequenza di quella classe: con classi sbilanciate (spam, tweet rilevanti, entità rare) è un numero alto che non dice nulla. Per questo in text classification si usano precision e recall.

<a id="p-25"></a>

### Slide 25 · Precision e recall

- **Precision**: fra gli elementi che il sistema ha etichettato positivi, la percentuale che è davvero positiva secondo le gold label. $P = tp/(tp+fp)$. Risponde a: *quando il sistema dice sì, quanto posso fidarmi?*
- **Recall**: fra gli elementi davvero presenti nell'input, la percentuale che il sistema ha trovato. $R = tp/(tp+fn)$. Risponde a: *quanto di ciò che c'era ho trovato?*

In figura sono evidenziate le due formule. Entrambe hanno i **true positive al numeratore** e ignorano i true negative: misurano la capacità di trovare ciò che cerchiamo, che è quello che conta quando la classe positiva è rara.

> **Approfondimento: Il compromesso precision/recall**
>
> Con un classificatore probabilistico si sceglie una soglia di decisione (0,5 nella L6). Alzandola il sistema dice "sì" solo quando è molto sicuro: meno false positive, precision più alta, ma più false negative, recall più bassa; abbassandola il contrario. Una sola coppia (P, R) descrive quindi un solo punto di questo compromesso; l'F-measure ([scheda 27](L07-regressione-logistica-multinomiale-e-valutazione.md#p-27)) lo riassume in un numero.

<a id="p-26"></a>

### Slide 26 · Il classificatore senza torte

Precision e recall smascherano il classificatore che dice sempre "no":

- nessun true positive e 100 false negative: **recall** $= 0/100 = 0$;
- niente etichettato positivo, quindi $tp + fp = 0$: **precision** $= 0/0$, **indefinita**.

Dove l'accuracy diceva 99,99%, la recall dice 0: esattamente il fallimento che ci interessa. Nella pratica la precision indefinita si conviene di solito pari a 0 (lo fa anche la funzione `report` del notebook), così l'F1 di questo classificatore è 0.

<a id="p-27"></a>

### Slide 27 · La F-measure

Un solo numero che combina precision e recall (van Rijsbergen, 1975):

$$F_\beta = \frac{(\beta^2+1)\,PR}{\beta^2 P + R}\qquad F_1 = \frac{2PR}{P+R}$$

- $\beta$ pesa l'importanza relativa: $\beta > 1$ favorisce la **recall**, $\beta &lt; 1$ la **precision** (per $\beta\to\infty$ $F_\beta\to R$, per $\beta\to 0$ $F_\beta\to P$);
- $\beta = 1$: stesso peso, $F_1$, la misura più usata.

Esempio (esercizio 8): $P = 0{,}5$, $R = 0{,}9$ danno $F_1 = 0{,}643$, $F_{0,5} = 0{,}549$, $F_2 = 0{,}776$: con la recall alta, $F_2$ (che la favorisce) è il più alto. Quando conviene la recall: screening, ricerca di documenti legali (meglio un falso allarme che perdere qualcosa); la precision: filtri antispam (meglio uno spam in più che perdere una mail vera).

> **Da saper fare: Da dove viene la formula**
>
> L'F-measure è una media armonica *pesata*: $F = 1/(\alpha\frac1P + (1-\alpha)\frac1R)$. Ponendo $\beta^2 = (1-\alpha)/\alpha$ e moltiplicando numeratore e denominatore per $PR$ si ottiene $F_\beta = (\beta^2+1)PR/(\beta^2P + R)$. Con $\alpha = 1/2$: $\beta = 1$ e $F_1 = 2PR/(P+R)$, la media armonica semplice.

<a id="p-28"></a>

### Slide 28 · La media armonica

$$\text{HarmonicMean}(a_1,\dots,a_n) = \frac{n}{\frac1{a_1}+\dots+\frac1{a_n}}$$ cioè il reciproco della media dei reciproci. L'F-measure è una media armonica pesata di $P$ e $R$, e la media armonica **resta vicina al più piccolo** dei due: è più conservativa della media aritmetica. Un $F_1$ alto richiede **sia** buona precision **sia** buona recall.

Il grafico fissa $P = 0{,}9$ e fa variare $R$ sull'asse x: la retta tratteggiata è la media aritmetica (da 0,45 a 0,95), la curva continua è $F_1$, la punteggiata è il minimo tra $P$ e $R$ (sale con $R$ fino a 0,9 e poi resta piatta). $F_1$ sta sempre fra il minimo e la media aritmetica, e per $R$ piccola si incolla al minimo. Punto evidenziato: $P = 0{,}9$, $R = 0{,}1$, media aritmetica 0,50 ma $F_1 = 2\cdot 0{,}09/1{,}0 = 0{,}18$. Un sistema che trova un decimo di ciò che c'è non merita "50%".

<a id="p-29"></a>

### Slide 29 · Più di due classi: matrice di confusione 3×3

Classificazione di email in una fra tre classi: urgent, normal, spam. Righe: uscita del sistema; colonne: gold label. Ogni cella conta i documenti della classe gold della colonna a cui il sistema ha dato la classe della riga.

| sistema \ gold | urgent | normal | spam |
| --- | --- | --- | --- |
| urgent | 8 | 10 | 1 |
| normal | 5 | 60 | 50 |
| spam | 3 | 30 | 200 |

Esempi di lettura: 1 email spam è stata etichettata urgent (riga urgent, colonna spam); 50 spam sono finite in normal. Totale 367 documenti, 268 sulla diagonale (corretti). Per ogni classe la figura scrive le due frazioni: precision = cella diagonale / somma della **riga** (es. $8/(8+10+1)$), recall = cella diagonale / somma della **colonna** (es. $8/(8+5+3)$).

<a id="p-30"></a>

### Slide 30 · Precision e recall per classe

Evidenziata la riga urgent:

- precision di urgent: dei 19 documenti che il sistema ha chiamato urgent, 8 lo sono davvero: $8/19 = 0{,}42$;
- recall di urgent: dei 16 urgent veri ne ha trovati 8: $8/16 = 0{,}50$;
- allo stesso modo precision di normal $60/115 = 0{,}52$, di spam $200/233 = 0{,}86$.

Le recall delle altre due classi, non scritte sulla slide: normal $60/100 = 0{,}60$, spam $200/251 = 0{,}80$. Il sistema va bene sulla classe frequente (spam) e male su quella rara e importante (urgent): una sola accuracy (268/367 = 0,73) lo nasconderebbe.

<a id="p-31"></a>

### Slide 31 · Macroaverage e microaverage

Per avere un solo numero si scompone il problema in tre matrici binarie "classe contro resto" (figura):

| classe | tp | fp | fn | tn | precision |
| --- | --- | --- | --- | --- | --- |
| urgent | 8 | 11 | 8 | 340 | 8/19 = 0,42 |
| normal | 60 | 55 | 40 | 212 | 60/115 = 0,52 |
| spam | 200 | 33 | 51 | 83 | 200/233 = 0,86 |
| pooled | 268 | 99 | 99 | 635 | 268/367 = 0,73 |

- **Macroaverage**: si calcola la misura per ogni classe e si fa la media: $(0{,}42+0{,}52+0{,}86)/3 = 0{,}60$. Ogni classe pesa uguale: riflette meglio le classi piccole; da usare quando tutte contano allo stesso modo.
- **Microaverage**: si sommano le tre matrici in una sola (*pooled*) e si calcola la misura lì: $268/(268+99) = 0{,}73$. Ogni *documento* pesa uguale: dominata dalla classe frequente, qui spam.

Tutti i numeri verificati (cella 15 del notebook: macro P 0,600, macro R 0,632, macro F1 0,614, micro 0,730).

> **Da saper fare: Perché micro precision = micro recall**
>
> Nel pooled $fp = fn = 99$. Non è un caso: ogni documento sbagliato è un false positive per la classe che il sistema ha scelto e un false negative per la sua classe gold, quindi $\sum_k fp_k = \sum_k fn_k$ = numero di errori. Allora micro P = micro R = micro F1 = $\sum tp/N$ = accuracy (con una sola etichetta per documento). Esercizio 4.1 del libro, esercizio 9 della scheda.

<a id="p-32"></a>

### Slide 32 · Training, development e test set

La figura è una barra divisa in tre: un grande **training set** ("learn the weights"), un piccolo **devset** ("tune, choose") e un piccolo **test set** ("report, once").

- **training set**: addestra il modello, come per i modelli n-gram;
- **development test set** (devset): serve a scegliere iperparametri (learning rate, forza della regolarizzazione, insieme di feature) e in generale a decidere quale modello è il migliore; così non si fa overfitting sul test set;
- **test set**: mai visto; quando si ha quello che si crede il modello migliore, lo si valuta lì **una volta** per riportarne le prestazioni.

È lo stesso protocollo della L4 ([scheda 27 della L4](L04-modelli-linguistici-n-gram.md#p-27)) e dei dati held-out per i pesi dell'interpolazione nella L5 ([scheda 25 della L5](L05-smoothing-ed-entropia.md#p-25)).

<a id="p-33"></a>

### Slide 33 · I limiti di una divisione fissa

Con una divisione fissa c'è un conflitto: per lasciare tanti dati al training, il test set o il devset rischiano di essere **troppo piccoli per essere rappresentativi**. Una stima fatta su pochi documenti è rumorosa: con 100 documenti di test e accuracy vera 0,8, l'accuracy misurata ha deviazione standard $\sqrt{0{,}8\cdot 0{,}2/100} = 0{,}04$, e due sistemi che differiscono di 2 punti non si distinguono (si torna su questo con la significatività, [scheda 39](L07-regressione-logistica-multinomiale-e-valutazione.md#p-39)).

La soluzione: la **cross-validation**, che usa tutti i dati per il training e tutti per il test (non contemporaneamente).

<a id="p-34"></a>

### Slide 34 · Cross-validation

La figura: dieci righe (modelli 1-10), ognuna con i dati divisi in 10 riquadri (fold); in ogni riga un fold diverso è rosso (test), gli altri nove azzurri (training); il fold rosso scorre lungo la diagonale; accanto a ogni riga l'errore $e_1, \dots, e_{10}$, in fondo la media.

1. dividere i dati in $k$ **fold** disgiunti;
2. addestrare su $k-1$ fold, testare su quello rimasto;
3. ripetere $k$ volte, in modo che ogni fold sia il test una volta;
4. fare la **media** dei $k$ tassi d'errore.

Con $k = 10$ (**10-fold cross-validation**): dieci modelli, ciascuno addestrato sul 90% dei dati. Ogni documento è usato esattamente una volta come test. Costo: $k$ addestramenti invece di uno.

> **Approfondimento: Varianti**
>
> Con $k = n$ (un documento per fold) si ha la *leave-one-out*, costosa ma utile con pochissimi dati. Con classi sbilanciate si usano fold *stratificati*, con la stessa proporzione di classi in ogni fold. Il risultato della cross-validation stima la bontà della *procedura* di addestramento; il modello finale si riaddestra poi su tutti i dati di training (come fa la cella 20 del notebook).

<a id="p-35"></a>

### Slide 35 · Cross-validation dentro il training set

Il problema della cross-validation pura: siccome tutti i dati finiscono prima o poi nel test, **tutto il corpus deve restare "cieco"**: non si potrebbe guardarlo per progettare feature o capire gli errori, altrimenti si sbircia il test e si sovrastimano le prestazioni. Ma guardare i dati è importante per progettare un sistema di NLP.

Soluzione comune (Fig. 4.10): un **training set** e un **test set** fissi; la 10-fold cross-validation si fa **dentro il training set** (in figura dieci iterazioni, ciascuna con un blocco "Dev" azzurro che scorre e il resto "Training" giallo); il test set, a parte sulla destra, si usa nel modo normale, una volta, per l'errore finale. È lo schema del notebook (5 fold dentro i 1800 esempi di training per scegliere il learning rate).

> **Approfondimento: Leakage**
>
> Tutto ciò che si "impara" dai dati va calcolato solo sui fold di training: vocabolario selezionato per frequenza, media e deviazione standard per standardizzare le feature, selezione delle feature, scelta di soglie. Se lo si calcola su tutti i dati, informazione del fold di test entra nel modello (*leakage*, parente della contaminazione della L4) e la stima è ottimista. Nel notebook non succede: la standardizzazione usa solo il training e il vocabolario costruito sui 1800 esempi non trasmette informazione nella cross-validation, perché una parola presente solo nel fold di dev riceve gradiente zero e il suo peso resta 0.

<a id="p-36"></a>
**Slide 36 · Pausa** — Pausa di 10 minuti; dopo la pausa: confrontare due classificatori.

## Significatività statistica

<a id="p-37"></a>
**Slide 37 · Test di significatività statistica** — Terza parte: A è davvero migliore di B, o è stato solo fortunato su questo test set?

<a id="p-38"></a>

### Slide 38 · Confrontare due classificatori

Classificatori $A$ (nuovo) e $B$ (vecchio), una metrica $M$ (F1, accuracy, ...), un test set $x$. $M(A, x)$ è il punteggio di $A$ su $x$, e la differenza

$$\delta(x) = M(A, x) - M(B, x)$$

si chiama **effect size**: quanto $A$ fa meglio di $B$ su $x$.

**Limite di un solo test set**: $A$ batte $B$ di 0,04 in F1. È davvero migliore? Non necessariamente: potrebbe essere stato fortunato *su questo* test set. L'**obiettivo** è sapere se $A$ vincerebbe ancora su un altro test set $x'$, cioè se la superiorità è una proprietà dei classificatori e non del campione di documenti.

<a id="p-39"></a>

### Slide 39 · δ dipende dal test set

Gli stessi classificatori $A$ e $B$, metrica accuracy, tre test set di 10 documenti:

|  | A | B | δ |
| --- | --- | --- | --- |
| test set 1 | 0,70 | 0,50 | 0,20 |
| test set 2 | 0,60 | 0,60 | 0,00 |
| test set 3 | 0,60 | 0,70 | −0,10 |

$A$ e $B$ non cambiano mai: cambiano solo i documenti. $\delta$ è positivo, nullo, perfino negativo: su un test set piccolo si muove molto, solo per caso. Quindi un singolo $\delta(x) &gt; 0$ non basta. Ordine di grandezza: su 10 documenti con accuracy vera 0,6 l'accuracy misurata ha deviazione standard $\sqrt{0{,}6\cdot 0{,}4/10}\approx 0{,}15$, quindi oscillazioni di 0,1-0,2 sono normali. (Le prime due righe sono il test set $x$ e il primo campione bootstrap $x^{(1)}$ del libro, Fig. 4.11: si ritrovano alle schede 44-45.)

<a id="p-40"></a>

### Slide 40 · Un'analogia: la moneta è equa?

Lanciamo una moneta 10 volte e otteniamo 9 teste. È truccata?

1. Si assume la spiegazione noiosa: la moneta è equa. È l'**ipotesi nulla**.
2. Anche una moneta equa dà 4, 6, 7 teste per caso: il grafico mostra quanto spesso. È la distribuzione binomiale $\binom{10}{k}/1024$: barre simmetriche attorno a 5 (0,246), 0,205 per 4 e 6, 0,117 per 3 e 7, 0,044 per 2 e 8, quasi invisibili agli estremi. Le barre di 9 e 10 sono in rosso.
3. Con la moneta equa, 9 o più teste escono $\binom{10}{9}+\binom{10}{10} = 10 + 1 = 11$ volte su 1024: circa l'1% (0,0107). Questo è il **p-value**.
4. Molto sorprendente per una moneta equa: si **rifiuta l'ipotesi nulla**; la moneta probabilmente è truccata.

**p-value**: probabilità di un risultato *almeno altrettanto estremo* del nostro, se vale l'ipotesi nulla.

> **Approfondimento: Una coda o due**
>
> Qui si contano solo i risultati estremi in una direzione (molte teste): è un test a **una coda**. Se la domanda fosse "la moneta è sbilanciata in un verso qualsiasi?" si conterebbero anche 0 e 1 teste e il p-value raddoppierebbe a 22/1024 = 0,021. Il confronto fra classificatori del libro è a una coda: ci interessa solo se $A$ è *migliore* di $B$ ($H_1: \delta &gt; 0$).

<a id="p-41"></a>

### Slide 41 · Il p-value per due classificatori

Stesso ragionamento: la moneta equa diventa "$A$ non è migliore di $B$". Nel libro $H_0: \delta(x)\le 0$ contro $H_1: \delta(x) &gt; 0$.

Le due curve sono la distribuzione di $\delta$ su un altro test set **se $H_0$ è vera**: campane centrate in 0 (asse da −0,4 a 0,4). Il nostro $\delta(x)$ (linea tratteggiata) fa la parte delle 9 teste; l'area colorata a destra, cioè un $\delta$ almeno grande quanto il nostro, è il p-value.

- sinistra: $\delta(x) = 0{,}04$, gran parte della coda è colorata, $p = 0{,}34$: facile da ottenere per caso;
- destra: $\delta(x) = 0{,}30$, la linea è all'estremo della campana e l'area è invisibile, $p = 0{,}001$: molto difficile per caso.

Un p-value piccolo: si rifiuta $H_0$ e si conclude che $A$ è migliore. Le curve sono illustrative, ma coerenti: entrambi i p-value corrispondono a una normale con deviazione standard circa 0,097 (verificato).

<a id="p-42"></a>

### Slide 42 · La logica di un test di significatività

1. Si assume la spiegazione noiosa, l'**ipotesi nulla** $H_0$: $A$ non è migliore di $B$.
2. Se $H_0$ fosse vera, quanto spesso il solo caso darebbe un $\delta$ almeno grande quanto $\delta(x)$? È il **p-value**: $P(\delta(X)\ge\delta(x)\mid H_0)$, dove $X$ varia su tutti i possibili test set.
3. Si fissa **prima** una soglia, di solito 0,05 o 0,01.
4. Se $p$ è sotto la soglia si rifiuta $H_0$: $A$ è migliore di $B$ e il risultato è **statisticamente significativo**.

La soglia va fissata in anticipo: sceglierla dopo aver visto $p$ (o provare tante metriche finché una è significativa) rende il test privo di senso. Stessa logica della moneta: assumere che non ci sia niente di speciale, poi controllare se il risultato sarebbe sorprendente.

<a id="p-43"></a>

### Slide 43 · Come leggere il p-value

- **$p$ sotto la soglia**: $A$ è migliore di $B$, risultato significativo. Esempio $p = 0{,}0047 &lt; 0{,}01$ (dal libro: 47 campioni bootstrap su 10.000).
- **$p$ sopra la soglia**: non si può dire che $A$ sia migliore, la differenza può essere fortuna. Ma questo **non dimostra** che $A$ e $B$ siano ugualmente buoni: assenza di prova non è prova di assenza.
- **p-value e $H_0$**: è calcolato *assumendo* $H_0$ vera; è la probabilità di un risultato come il nostro, non la probabilità dell'ipotesi. $p = 0{,}03$ non significa "c'è il 3% di probabilità che $A$ non sia migliore".
- **p-value ed effect size**: quanto $A$ è migliore lo dice $\delta$, non $p$. Con un test set enorme anche un $\delta$ minuscolo diventa significativo; con un test set minuscolo anche un $\delta$ grande può non esserlo. Vanno riportati entrambi.

<a id="p-44"></a>

### Slide 44 · Il paired bootstrap test

Il test set $x$ del libro, 10 documenti, giusto (1) o sbagliato (0) per ciascun classificatore:

| doc | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | acc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | 1 | 1 | 1 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 0,70 |
| B | 1 | 0 | 1 | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 0,50 |

$\delta(x) = 0{,}70 - 0{,}50 = 0{,}20$. Per vedere quanto $\delta$ varia per caso servirebbero tanti test set; ne abbiamo uno. Idea del **bootstrap** (Efron e Tibshirani, 1993): costruire tanti **test set virtuali** da $x$, estraendo 10 documenti a caso **con reinserimento**. **Paired**: per ogni documento estratto si tengono i risultati di *entrambi* $A$ e $B$, così i due sistemi sono confrontati sugli stessi documenti. L'unica assunzione è che $x$ sia rappresentativo della popolazione.

> **Approfondimento: Perché paired e perché con reinserimento**
>
> **Paired**: un documento difficile è difficile per entrambi; estraendo la coppia di risultati la difficoltà comune si cancella nella differenza e il test è molto più sensibile che campionare $A$ e $B$ separatamente. **Con reinserimento**: è ciò che crea variabilità. Estraendo 10 documenti su 10 *senza* reinserimento si ottiene sempre una permutazione di $x$, quindi $\delta = 0{,}20$ in ogni campione e il test con soglia $2\delta(x)$ darebbe $p = 0$, sempre "significativo" (verificato in Python).

<a id="p-45"></a>

### Slide 45 · Un test set virtuale

La seconda tabella è il primo campione $x^{(1)}$: documenti estratti 3, 6, 2, 7, 8, 9, 1, 1, 9, 4. I documenti 1 e 9 escono due volte, 5 e 10 mai: è un test set che avremmo potuto avere. Ricopiando le colonne di $x$:

- $A$: 1 0 1 1 1 0 1 1 0 0, accuracy 0,60;
- $B$: 1 1 0 0 1 0 1 1 0 1, accuracy 0,60;
- $\delta(x^{(1)}) = 0{,}00$.

"A and B are both right on 6 documents" va letto come "ciascuno è giusto su 6": i documenti su cui sono giusti *insieme* sono 4 (3, 8, 1, 1). Ripetendo moltissime volte, per esempio $b = 100.000$, si ottengono 100.000 valori di $\delta$, che insieme mostrano quanto $\delta$ varia per caso. (Verificato riga per riga.)

<a id="p-46"></a>

### Slide 46 · Dal bootstrap al p-value

Due istogrammi della frazione dei campioni per valore di $\delta$ (passi di 0,1, perché su 10 documenti $\delta$ è un multiplo di 0,1):

- **sinistra**: i $\delta$ dei test set virtuali, centrati su $\delta(x) = 0{,}20$ (linea blu), con la linea rossa a $2\delta(x) = 0{,}40$; le barre da 0,40 in su sono rosse: il 27% dei campioni;
- **destra**: lo stesso istogramma spostato di −0,20, centrato in 0 "come se $A$ non fosse migliore"; ora le barre rosse sono quelle da $\delta(x) = 0{,}20$ in su. Stesse barre, stesso 27%.

Lo spostamento è il cuore del metodo: i campioni bootstrap vengono da $x$, che è sbilanciato di 0,20 a favore di $A$, quindi oscillano attorno a 0,20 e non attorno a 0. La forma della dispersione è quella del caso; sotto $H_0$ la stessa dispersione starebbe attorno a 0. Il p-value è quanto spesso il caso da solo arriva al nostro $\delta(x)$: $p = 0{,}27 &gt; 0{,}05$, con 10 documenti una differenza di 0,20 può essere tranquillamente fortuna.

> **Da saper fare: Il 27% calcolato esattamente**
>
> Differenze per documento $A - B$: +1 sui documenti 2, 5, 7, 10 (probabilità 0,4), −1 su 4 e 6 (0,2), 0 sugli altri quattro (0,4). In un campione di 10 estrazioni $\delta = (n_+ - n_-)/10$, e si conta $P(n_+ - n_- \ge 4)$ con la distribuzione multinomiale: risultato esatto 0,2684. Il notebook, con $b = 100.000$, dà 0,267. Anche le altezze delle barre corrispondono (0,166 a 0,2; 0,156 a 0,3; 0,123 a 0,4; 0,080 a 0,5).

<a id="p-47"></a>

### Slide 47 · Il paired bootstrap in quattro passi

1. Calcolare $\delta(x)$ sul test set $x$.
2. Costruire $b$ test set virtuali estraendo documenti da $x$ con reinserimento.
3. Calcolare $\delta$ su ciascuno e spostare l'istogramma in 0.
4. p-value: la frazione di test set virtuali che raggiungono $\delta(x)$.

In formula (Eq. 4.48, versione di Berg-Kirkpatrick et al., 2012), con lo spostamento incorporato:

$$p\text{-value}(x) = \frac1b\sum_{i=1}^{b}\mathbb 1\big(\delta(x^{(i)}) - \delta(x)\ge\delta(x)\big) = \frac1b\sum_{i=1}^{b}\mathbb 1\big(\delta(x^{(i)})\ge 2\delta(x)\big)$$

Il piccolo grafico ripete l'istogramma sinistro della scheda precedente (p-value = 0,27). Sui 10 documenti, $b = 100.000$: $p = 0{,}27$, non significativo. I test set veri hanno molti più documenti: $\delta$ oscilla meno e lo stesso $\delta$ può essere significativo (nel notebook, su 600 recensioni, 0,082 di differenza dà $p\approx 0$).

> **Approfondimento: ≥ o >?**
>
> Il libro usa $\ge 2\delta(x)$ nell'Eq. 4.48 e nello pseudocodice (Fig. 4.12), ma nel testo che lo accompagna scrive "$\delta(x^{(i)}) &gt; 2\delta(x)$". Con pochi documenti la differenza è grande, perché $\delta$ assume pochi valori: sull'esempio $P(\delta\ge 0{,}4) = 0{,}268$ ma $P(\delta &gt; 0{,}4) = 0{,}146$ (verificato). La versione corretta, coerente con la definizione di p-value ("almeno altrettanto estremo"), è $\ge$: è quella delle slide e del notebook.

## Danni, interpretazione e regolarizzazione

<a id="p-48"></a>
**Slide 48 · Danni, interpretazione e regolarizzazione** — Ultima parte: tre sezioni brevi su danni dei classificatori, interpretazione dei pesi e regolarizzazione.

<a id="p-49"></a>

### Slide 49 · Evitare danni: danni rappresentazionali

Un classificatore può fare danni. Una prima classe sono i **danni rappresentazionali** (*representational harms*): un sistema che sminuisce un gruppo sociale, per esempio perpetuando stereotipi negativi.

Esempio (Kiritchenko e Mohammad, 2018): 200 sistemi di sentiment analysis valutati su coppie di frasi **identiche** salvo un nome proprio, tipico afroamericano (es. *Shaniqua*) o tipico euroamericano (es. *Stephanie*). La maggior parte dei sistemi assegnava sentiment più basso ed emozioni più negative alle frasi con nomi afroamericani. Il metodo è istruttivo: coppie minime che differiscono solo per l'attributo sensibile, così ogni differenza nell'uscita è attribuibile a quello. Per un classificatore lineare il meccanismo è semplice: se nei dati di training un nome compare più spesso in contesti negativi, il suo peso verso la classe negativa cresce.

<a id="p-50"></a>

### Slide 50 · Toxicity detection e fonti del bias

**Toxicity detection**: riconoscere hate speech, abusi, molestie. Lo scopo è ridurre i danni, ma classificatori molto usati etichettano come tossiche frasi **non tossiche** che semplicemente menzionano identità (donne, persone cieche, persone gay) o usano tratti dell'*African American Vernacular English*. Sono **false positive** che possono **silenziare** il discorso di o su questi gruppi: un danno diverso da quello rappresentazionale.

**Fonti del bias**:

- i dati di training: il machine learning replica e perfino **amplifica** i loro bias;
- le etichette (bias degli annotatori);
- le risorse usate, come i lessici di sentiment (o gli embedding preaddestrati);
- perfino ciò che il modello è addestrato a ottimizzare.

Non esistono ancora soluzioni generali: per questo bisogna almeno misurare e documentare (scheda successiva). Legame con la valutazione: le prestazioni vanno guardate *per gruppo*, come le misure per classe della [scheda 30](L07-regressione-logistica-multinomiale-e-valutazione.md#p-30), perché una media le nasconde.

<a id="p-51"></a>

### Slide 51 · Model card

Quando si pubblica un modello di NLP, rilasciare una **model card** per ogni versione (Mitchell et al., 2019). Contenuto:

- **training**: algoritmi e parametri di addestramento;
- **dati di training**: fonti, motivazione, preprocessing;
- **dati di valutazione**: fonti, motivazione, preprocessing;
- **uso previsto** e utenti previsti;
- **prestazioni** su diversi gruppi demografici o di altro tipo e in diverse situazioni d'uso.

È il corrispettivo, per i modelli, del *datasheet* dei corpora visto nella L2. L'ultimo punto è il più legato a questa lezione: chiede proprio di disaggregare precision, recall e F1 per gruppo invece di dare un solo numero.

<a id="p-52"></a>

### Slide 52 · Interpretare i modelli

**Interpretabilità**: vogliamo sapere *perché* il classificatore ha preso una decisione; come esseri umani dovremmo capire i nostri algoritmi.

La regressione logistica è adatta perché le feature sono spesso progettate a mano e ognuna ha un peso:

- il **segno** dice verso quale classe spinge;
- la **grandezza** quanto forte;
- si può anche verificare se l'effetto di una feature è **statisticamente significativo** (il libro cita il likelihood ratio test e il Wald test).

Due cautele: i pesi sono confrontabili solo se le feature hanno scale comparabili (una feature che vale fino a 1000 avrà un peso piccolo anche se conta molto: per questo si standardizza); nel caso multinomiale, come detto alla [scheda 12](L07-regressione-logistica-multinomiale-e-valutazione.md#p-12), contano le differenze fra le righe di $W$. Nel notebook i pesi delle parole riproducono lo schema del punto esclamativo: *hate* 1,49 per il negativo e −1,40 per il positivo.

<a id="p-53"></a>

### Slide 53 · Testare ipotesi e confondenti

Oltre che come classificatore, la regressione logistica è uno strumento di **analisi** per testare ipotesi sui dati:

- le parole logicamente negative (*no, not, never*) sono associate al sentiment negativo?
- le recensioni negative parlano di più della fotografia del film?

**Confondenti** (*confounds*): altri fattori che possono influire, come il genere del film, l'anno, la lunghezza della recensione. Si mettono nel modello **come feature**: allora ogni peso misura l'effetto della sua feature **a parità delle altre**. Esempio: se le recensioni negative sono più lunghe e quelle lunghe contengono più spesso *not*, senza la feature "lunghezza" il peso di *not* assorbirebbe in parte l'effetto della lunghezza. Lo stesso vale fuori dal linguaggio: feature linguistiche estratte con NLP messe in relazione con riammissioni ospedaliere, esiti elettorali, vendite di prodotti, controllando età del paziente, contea, marca.

<a id="p-54"></a>

### Slide 54 · Overfitting e generalizzazione

**Overfitting**: una parola vista in una sola recensione di training, positiva (per esempio un nome raro), sembra **perfettamente predittiva** del positivo e riceve un peso enorme. Il modello impara il training set troppo bene, rumore compreso: correlazioni accidentali trattate come regole.

**Generalizzazione**: un buon modello funziona su dati nuovi, il test set mai visto. Un modello in overfitting va bene sui dati di training e male su quelli nuovi. È lo stesso fenomeno dei 4-gram che ricopiano Shakespeare nella L4 ([scheda 43 della L4](L04-modelli-linguistici-n-gram.md#p-43)).

Nel notebook: con 150 recensioni di training e 345 pesi, dopo 200 epoche l'accuracy di training è 1,000 e quella di test 0,778.

> **Approfondimento: Pesi che vanno all'infinito**
>
> Se una feature separa perfettamente le classi nel training, la cross-entropy senza regolarizzazione non ha minimo finito: aumentare quel peso abbassa sempre la loss (la probabilità della classe corretta si avvicina a 1 senza raggiungerla), e la discesa del gradiente lo fa crescere indefinitamente. La regolarizzazione rende il minimo finito (conoscenza standard, coerente con §4.14).

<a id="p-55"></a>

### Slide 55 · Regolarizzazione

Si aggiunge all'obiettivo un termine che penalizza i pesi grandi:

$$\hat\theta = \arg\max_\theta \sum_{i=1}^{m}\log P(y^{(i)}\mid x^{(i)}) - \alpha R(\theta)$$

Il primo termine è l'adattamento ai dati (*fit*): la log probabilità delle etichette di training, cioè meno la cross-entropy della lezione precedente (la slide dice "first lecture": è la prima lezione sulla regressione logistica, la L6). Il libro qui scrive l'obiettivo come massimizzazione e senza il fattore $1/m$, che non cambia l'argmax.

- $R(\theta)$ cresce con i pesi: i pesi grandi costano;
- un peso grande sopravvive solo se migliora davvero l'adattamento;
- $\alpha$ fissa il prezzo: più è alto, più i pesi sono piccoli (con $\alpha$ troppo alto il modello è troppo semplice: underfitting);
- il **bias non è penalizzato**: fa da soglia, assorbe la frequenza a priori delle classi e il fatto che i dati non sono centrati; spingerlo verso 0 non riduce l'overfitting e peggiora il modello.

$\alpha$ è un iperparametro: si sceglie sul devset o con la cross-validation, mai sul test.

<a id="p-56"></a>

### Slide 56 · Regolarizzazione L2 e L1

- **L2** (*ridge regression*): $R(\theta) = \lVert\theta\rVert_2^2 = \sum_j\theta_j^2$, la somma dei quadrati ($\lVert\theta\rVert_2$ è la lunghezza euclidea del vettore). I pesi grandi costano molto, quelli piccoli quasi niente: preferisce **tanti pesi piccoli**.
- **L1** (*lasso regression*): $R(\theta) = \lVert\theta\rVert_1 = \sum_i|\theta_i|$, la somma dei valori assoluti (distanza di Manhattan). Ogni peso costa, anche piccolo: molti pesi diventano **esattamente 0**, cioè meno feature (soluzioni *sparse*).

Il grafico confronta le due penalità per un solo peso fra −2 e 2: la parabola $\theta^2$ (blu) e la V $|\theta|$ (rossa tratteggiata), che si incrociano a $\pm 1$. Vicino a 0 la parabola è piatta (derivata $2\theta\to 0$: un peso già piccolo non viene più spinto), mentre la V ha pendenza costante $\pm 1$: anche un peso minuscolo viene spinto verso 0 con la stessa forza, finché ci arriva. Per questo L1 azzera i pesi. Nessuna delle due penalizza il bias. L2 è più facile da ottimizzare (derivata semplice), L1 ha derivata discontinua in 0.

> **Da saper fare: L'aggiornamento con L2: weight decay (esercizio 12)**
>
> Minimizzando $L + \alpha\sum_j\theta_j^2$ la derivata della penalità è $2\alpha\theta_j$, e il passo di discesa diventa
>
> $$\theta_j \leftarrow \theta_j - \eta\left(\frac{\partial L}{\partial\theta_j} + 2\alpha\theta_j\right) = (1 - 2\eta\alpha)\,\theta_j - \eta\frac{\partial L}{\partial\theta_j}$$
>
> A ogni passo il peso è moltiplicato per una costante $&lt; 1$ (con $\eta = 0{,}1$, $\alpha = 0{,}5$: 0,9) prima del passo normale: si chiama *weight decay*. Con L1 invece si sottrae una quantità fissa $\eta\alpha$ verso 0 (nel notebook con *soft thresholding*, che si ferma a 0).

<a id="p-57"></a>

### Slide 57 · La regolarizzazione come prior

Un'altra lettura: prima di vedere i dati ci aspettiamo che i pesi siano piccoli. Il **prior** $P(\theta)$ esprime questa credenza; l'addestramento diventa "adattati ai dati ma resta vicino al prior" (stima MAP).

Il grafico mostra i due prior di un peso su $[-3, 3]$: la **gaussiana** (blu), larga e arrotondata in 0, corrisponde a L2; la **laplaciana** (rossa), con una punta acuta in 0 e code più pesanti, corrisponde a L1: mette molta più probabilità esattamente vicino a 0, quindi più pesi nulli.

Perché: massimizzare $\prod_i P(y^{(i)}\mid x^{(i)})\cdot\prod_j P(\theta_j)$ in log è $\sum_i\log P(y^{(i)}\mid x^{(i)}) + \sum_j\log P(\theta_j)$. Con un prior gaussiano a media 0, $\log P(\theta_j) = -\theta_j^2/(2\sigma^2) + $ costante, cioè la penalità L2 con $\alpha = 1/(2\sigma^2)$ (il libro pone $2\sigma^2 = 1$); con un prior di Laplace $\log P(\theta_j) = -|\theta_j|/s + $ costante, la penalità L1. Prior più stretto = regolarizzazione più forte.

<a id="p-58"></a>

### Slide 58 · Riepilogo e prossima lezione

- **softmax**: $K$ punteggi in $K$ probabilità; un vettore di pesi per classe, le righe di $W$;
- **loss**: meno il log della probabilità della classe corretta; gradiente $(\hat y_k - y_k)\,x_i$;
- **matrice di confusione**; precision, recall, F1; macro e micro average;
- **devset e cross-validation**;
- **significatività**: ipotesi nulla, p-value, paired bootstrap;
- **danni e model card**; interpretabilità; regolarizzazione L2 e L1.

**Prossima lezione**: *Parts of speech and named entities*, sequence labeling, con Andrea Ceni (J&M capitolo 18). Lì la classificazione non è più di un documento ma di ogni parola di una sequenza, e tornerà la notazione $f(x, y)$ delle feature (CRF).

## Notebook

Commento al notebook del corso `HLT-L07-multinomial-logistic-regression.ipynb` (il notebook è del docente e non è incluso).

Notebook di accompagnamento: softmax e loss sull'esempio del libro, un classificatore a tre classi fatto a mano con gradiente verificato numericamente, un dataset sintetico di 2400 recensioni (negativo, neutro, positivo) generate da template, regressione logistica multinomiale da zero in numpy (mini-batch SGD, L2 e L1 opzionali), valutazione con matrice di confusione e macro/micro average, cross-validation a 5 fold dentro il training set per scegliere il learning rate, paired bootstrap test, regolarizzazione su un training piccolo, lettura dei pesi. Servono solo `numpy` e `matplotlib`, niente rete. Controlla gli esercizi 1-5, 9 e 11 della scheda.

Ho eseguito il notebook (Python 3.11, nbconvert): tutti gli output coincidono con quelli salvati. Ho controllato i punti dove di solito si sbaglia: softmax stabile (massimo sottratto, anche per righe con `axis=1, keepdims=True`), argmax per riga, one-hot, gradiente (confrontato con quello numerico), confusione con righe = sistema e colonne = gold, precision per riga e recall per colonna, macro e micro non scambiati, cross-validation senza leakage, bootstrap con reinserimento e appaiato, soglia $2\delta(x)$ con $\ge$, bias non regolarizzato, conversione dei pesi standardizzati. **Non ho trovato bug**; segnalo solo una convenzione di scala per $\alpha$ e un artefatto di binning nella figura del bootstrap.

### Notebook 1 · La softmax e la loss sull'esempio del libro

```python
def softmax(z):
    z = np.asarray(z, dtype=float)
    e = np.exp(z - z.max())          # subtracting the maximum does not change the result and avoids overflow
    return e / e.sum()

z = np.array([0.6, 1.1, -1.5, 1.2, 3.2, -1.1])
z1 = np.array([2.0, 1.0, 0.0])
print(softmax(z1), softmax(z1 + 3), softmax(2 * z1))

def ce_loss(y_hat, c):
    return -math.log(y_hat[c])
```

Output:

```text
exp(z)      [ 1.8221  3.0042  0.2231  3.3201 24.5325  0.3329]  sum 33.23
softmax(z)  [0.0548 0.0904 0.0067 0.0999 0.7382 0.01  ]  sum 0.9999999999999999

exercise 1: [0.6652 0.2447 0.09  ]  z + 3: [0.6652 0.2447 0.09  ]  2z: [0.8668 0.1173 0.0159]
exercise 2: softmax([1.5, 0.3])[0] = 0.7685  sigmoid(1.5 - 0.3) = 0.7685
correct class 5: probability 0.74, loss 0.30
correct class 2: probability 0.09, loss 2.40
```

La softmax sottrae il massimo prima dell'esponenziale: risultato identico ([scheda 8](L07-regressione-logistica-multinomiale-e-valutazione.md#p-8)) e niente overflow. L'output riproduce la [scheda 9](L07-regressione-logistica-multinomiale-e-valutazione.md#p-9) (e conferma la somma 33,23, non 33,24), le proprietà dell'esercizio 1 (traslare i logit non cambia nulla, raddoppiarli porta il massimo da 0,665 a 0,867) e l'esercizio 2 ($\text{softmax}([1{,}5;\ 0{,}3])_1 = \sigma(1{,}2) = 0{,}7685$). `ce_loss` è la negative log likelihood $-\ln\hat y_c$ con indice 0-based: 0,30 e 2,40 come nella [scheda 19](L07-regressione-logistica-multinomiale-e-valutazione.md#p-19) (2,40 invece di 2,4 perché usa 0,0904 non arrotondato).

### Notebook 2 · Un classificatore a tre classi fatto a mano (esercizi 3 e 4)

```python
W = np.array([[2.0, -1.5], [-1.0, 2.5], [0.2, 0.3]])
b = np.array([0.5, 0.0, 1.0])
x = np.array([3.0, 2.0])
z = W @ x + b
y_hat = softmax(z)

def gradient(W, b, x, c):
    y = np.zeros(len(b)); y[c] = 1
    err = softmax(W @ x + b) - y
    return np.outer(err, x), err

gW, gb = gradient(W, b, x, 2)
W1, b1 = W - 0.1 * gW, b - 0.1 * gb
```

Output:

```text
z = [3.5 2.  2.2]  y_hat = [0.6686 0.1492 0.1822]  class: positive
loss if positive: 0.403  loss if neutral: 1.703

gradient of W (correct class neutral):
 [[ 2.006  1.337]
 [ 0.448  0.298]
 [-2.453 -1.636]] 
gradient of b: [ 0.669  0.149 -0.818]
largest difference from the numerical gradient: 1.3803957976676884e-10

after one step with eta = 0.1: W =
 [[ 1.799 -1.634]
 [-1.045  2.47 ]
 [ 0.445  0.464]] 
b = [ 0.433 -0.015  1.082] 
y_hat = [0.2743 0.1267 0.599 ]  loss if neutral: 0.512
```

Il gradiente rispetto a $W$ è il prodotto esterno $(\hat{\mathbf y} - \mathbf y)\,\mathbf x^{\top}$ ([scheda 20](L07-regressione-logistica-multinomiale-e-valutazione.md#p-20)), con il one-hot costruito correttamente e l'errore di forma $K$. Il controllo numerico (differenze centrate, $\epsilon = 10^{-6}$) coincide fino a $10^{-10}$: la formula $(\hat y_k - y_k)x_i$ è giusta. Dopo un passo con $\eta = 0{,}1$ la riga del neutro si è spostata verso $\mathbf x$ (da $[0{,}2;\ 0{,}3]$ a $[0{,}445;\ 0{,}464]$), le altre due se ne sono allontanate, e la recensione passa da positivo a neutro. Tutti i numeri coincidono con le soluzioni degli esercizi 3 e 4.

### Notebook 3 · Un dataset di recensioni a tre classi

```python
def make_review(rng):
    label = rng.choices([0, 1, 2], weights=[0.4, 0.2, 0.4])[0]     # negative, neutral, positive
    ...                                                              # aspects with opinions, facts, openers, closers
    if rng.random() < 0.05:                                          # label noise
        label = rng.choice([l for l in (0, 1, 2) if l != label])
    return " ".join(p for p in parts if p).split(), label

rng = random.Random(2026)
data = [make_review(rng) for _ in range(2400)]
train_data, test_data = data[:1800], data[1800:]
```

Output:

```text
1800 training reviews, 600 test reviews
classes in training: {'negative': 710, 'neutral': 383, 'positive': 707}
negative  i saw this film last week . the photography is second-rate but the acting is very nice but ...
neutral   the cast is not hokey , the music is brilliant , the dialogue is very wonderful and the dialogue is not nice . you will love it !
```

Recensioni sintetiche generate da template, come nel notebook della lezione precedente: le positive e negative combinano 2-4 giudizi su aspetti del film (la maggioranza concorde con l'etichetta, uno su cinque espresso con una negazione, *is not superb*), le neutre elencano fatti con al più un giudizio. Il 5% delle etichette è invertito di proposito (rumore di annotazione): l'ultima recensione mostrata è chiaramente positiva ma etichettata neutra. Classi sbilanciate: il neutro è circa il 20%. Divisione fissa 1800/600, fatta prima di tutto il resto.

### Notebook 4 · Due rappresentazioni: sei feature a mano e bag of words

```python
def six_features(tokens):
    low = [t.lower() for t in tokens]
    return [sum(t in POS_WORDS for t in low), sum(t in NEG_WORDS for t in low), int("no" in low),
            sum(t in PRONOUNS for t in low), int("!" in tokens), math.log(len(tokens))]

vocab = sorted(set(t for tokens, _ in train_data for t in tokens))
H_train, H_test = hand_matrix(train_data), hand_matrix(test_data)
mean_h, std_h = H_train.mean(axis=0), H_train.std(axis=0)
H_train, H_test = (H_train - mean_h) / std_h, (H_test - mean_h) / std_h
B_train, B_test = bow_matrix(train_data, vocab), bow_matrix(test_data, vocab)
```

Output:

```text
six hand features: (1800, 6)   words as features: (1800, 115) (115 words)
```

Le sei feature del libro (lessico positivo, lessico negativo, presenza di *no*, pronomi di prima e seconda persona, punto esclamativo, log della lunghezza) e il bag of words sui 115 tipi del training. Le feature a mano sono **standardizzate** con media e deviazione standard del **solo training**, applicate poi anche al test: corretto, nessuna informazione del test entra nel preprocessing. Il vocabolario è costruito sul training; le parole del test fuori vocabolario sono ignorate.

### Notebook 5 · Regressione logistica multinomiale da zero

```python
def softmax_rows(Z):
    E = np.exp(Z - Z.max(axis=1, keepdims=True))
    return E / E.sum(axis=1, keepdims=True)

def predict_proba(X, W, b):
    return softmax_rows(X @ W.T + b)

def predict(X, W, b):
    return predict_proba(X, W, b).argmax(axis=1)

def one_hot(y, K):
    Y = np.zeros((len(y), K)); Y[np.arange(len(y)), y] = 1
    return Y

def batch_gradient(X, y, W, b):
    err = predict_proba(X, W, b) - one_hot(y, W.shape[0])           # m x K
    return err.T @ X / len(y), err.mean(axis=0)

def train_softmax(X, y, K=3, eta=0.1, epochs=30, batch_size=16, l2=0.0, l1=0.0, seed=0):
    ...
            W = W - eta * (gW + 2 * l2 * W)          # the L2 penalty is not applied to the bias
            b = b - eta * gb
            if l1 > 0:                               # L1: soft thresholding after the step
                W = np.sign(W) * np.maximum(np.abs(W) - eta * l1, 0)
```

Output:

```text
six hand features: training cost 1.099 -> 0.499, test accuracy 0.813
words as features: training cost 1.099 -> 0.321, test accuracy 0.895
```

Forma matriciale per un mini-batch: $Z = XW^{\top} + \mathbf b$ ($m\times K$), softmax **riga per riga** (`axis=1`, `keepdims=True`, massimo sottratto per riga), predizione con argmax per riga, gradiente $(1/m)(\hat Y - Y)^{\top}X$ di forma $K\times f$ come $W$ e gradiente del bias come media delle righe di $\hat Y - Y$. Il costo iniziale con pesi nulli è $\ln 3 = 1{,}099$ (distribuzione uniforme su tre classi): un buon controllo. La penalità L2 entra con la sua derivata $2\alpha W$ e **non tocca il bias**, come prescrive il libro; L1 è applicata con soft thresholding, anch'essa solo a $W$. Risultato: bag of words 0,895 di accuracy di test, feature a mano 0,813.

> **Approfondimento: La scala di α**
>
> Il notebook minimizza la loss *media* sul batch più $\alpha\sum\theta^2$; il libro (Eq. 4.51) sottrae $\alpha\sum\theta^2$ dalla log likelihood *sommata* su tutti gli $m$ esempi. Le due formulazioni sono equivalenti con $\alpha_{\text{libro}} = m\cdot\alpha_{\text{notebook}}$: i valori di $\alpha$ del notebook (0,001-0,1) non vanno confrontati direttamente con quelli del libro. Non è un errore, è una convenzione (la stessa di molte librerie).

### Notebook 6 · Valutazione: confusione, precision, recall, F1

```python
def confusion(y_true, y_pred, K=3):
    M = np.zeros((K, K), dtype=int)
    for t, p in zip(y_true, y_pred):
        M[p, t] += 1                                   # rows: system output, columns: gold
    return M

def report(M, names):
    tp = np.diag(M); fp = M.sum(axis=1) - tp; fn = M.sum(axis=0) - tp
    P = tp / np.maximum(tp + fp, 1); R = tp / np.maximum(tp + fn, 1); F = 2 * P * R / np.maximum(P + R, 1e-12)
    micro = tp.sum() / (tp.sum() + fp.sum())
    ...
```

Output:

```text
the three-class example of the book (urgent, normal, spam):
                precision  recall     F1    support
urgent              0.421    0.500    0.457       16
normal              0.522    0.600    0.558      100
spam                0.858    0.797    0.826      251
macroaverage        0.600    0.632    0.614
microaverage        0.730    0.730    0.730   (= accuracy 0.730)

words as features: confusion matrix (rows: system, columns: gold; ['negative', 'neutral', 'positive'])
[[226   3  23]
 [  4 107   5]
 [ 20   8 204]]
                precision  recall     F1    support
negative            0.897    0.904    0.900      250
neutral             0.922    0.907    0.915      118
positive            0.879    0.879    0.879      232
macroaverage        0.900    0.897    0.898
microaverage        0.895    0.895    0.895   (= accuracy 0.895)
```

Convenzione del libro: righe = sistema, colonne = gold (`M[p, t]`). Quindi i false positive di una classe sono il resto della **riga** (`M.sum(axis=1) - tp`) e i false negative il resto della **colonna** (`M.sum(axis=0) - tp`): assi corretti. Macro = media delle misure per classe; micro = misure sulle somme di tp, fp, fn; non sono scambiati, e la riga micro mostra P = R = F1 = accuracy ([scheda 31](L07-regressione-logistica-multinomiale-e-valutazione.md#p-31)). Sull'esempio del libro escono 0,600 (macro P) e 0,730 (micro). Sulle recensioni: le sei feature confondono soprattutto negativo e positivo (65 negative chiamate positive), perché i conteggi di lessico non vedono la negazione; il bag of words riduce quegli errori a 20 e 23. Il neutro è facile per entrambi, quindi macro e micro sono vicini.

### Notebook 7 · Cross-validation dentro il training set

```python
def cross_validate(X, y, k=5, seed=0, **kw):
    rng = np.random.default_rng(seed)
    folds = np.array_split(rng.permutation(len(y)), k)
    scores = []
    for i in range(k):
        dev = folds[i]; tr = np.concatenate([f for j, f in enumerate(folds) if j != i])
        W, b, _ = train_softmax(X[tr], y[tr], **kw)
        scores.append(accuracy(X[dev], y[dev], W, b))
    return np.mean(scores), np.std(scores)

for eta in (0.003, 0.01, 0.03, 0.1, 0.3):
    m, s = cross_validate(B_train, y_train, eta=eta, epochs=10)
```

Output:

```text
eta = 0.003: dev accuracy 0.843 (std over the folds 0.015)
eta =  0.01: dev accuracy 0.876 (std over the folds 0.011)
eta =  0.03: dev accuracy 0.890 (std over the folds 0.012)
eta =   0.1: dev accuracy 0.887 (std over the folds 0.005)
eta =   0.3: dev accuracy 0.858 (std over the folds 0.030)
chosen on the dev folds: eta = 0.03
final model with eta = 0.03, trained on all 1800 training reviews: test accuracy 0.892
```

Lo schema della [scheda 35](L07-regressione-logistica-multinomiale-e-valutazione.md#p-35): 5 fold dentro i 1800 esempi di training (360 per fold), cinque modelli per valore del learning rate, media dell'accuracy sui fold di dev; il test non viene toccato. Poi un solo modello con il valore scelto, addestrato su tutto il training, valutato **una volta** sul test: 0,892. I fold sono gli stessi per tutti i valori di $\eta$ (stesso seed): il confronto è appaiato. I fold sono disgiunti e coprono tutto (`array_split` di una permutazione). 0,03 e 0,1 differiscono di 0,003, meno della deviazione standard tra fold: una differenza da non prendere sul serio, che introduce la sezione successiva.

### Notebook 8 · Il paired bootstrap test

```python
def paired_bootstrap(correct_A, correct_B, b=10000, seed=0):
    rng = np.random.default_rng(seed)
    n = len(correct_A)
    delta = correct_A.mean() - correct_B.mean()
    idx = rng.integers(0, n, size=(b, n))              # b samples of n documents, with replacement
    deltas = correct_A[idx].mean(axis=1) - correct_B[idx].mean(axis=1)
    return delta, np.mean(deltas >= 2 * delta - 1e-12), deltas

A10 = np.array([1, 1, 1, 0, 1, 0, 1, 1, 0, 1]); B10 = np.array([1, 0, 1, 1, 0, 1, 0, 1, 0, 0])
d, p, deltas10 = paired_bootstrap(A10, B10, b=100000)
```

Output:

```text
the example of the book: acc(A) = 0.70, acc(B) = 0.50, delta = 0.20, p-value = 0.267
exercise 11: delta = 0.40, p-value = 0.205
words (A) against hand features (B): delta = 0.082, p-value = 0.0000
words, seed 0 (A) against words, seed 1 (B): delta = 0.007, p-value = 0.151
```

Implementazione fedele alla Fig. 4.12: `rng.integers(0, n, size=(b, n))` estrae gli indici **con reinserimento**, e lo **stesso** indice si usa per $A$ e per $B$ (paired); p-value = frazione dei campioni con $\delta(x^{(i)})\ge 2\delta(x)$, con una tolleranza $10^{-12}$ per gli errori di virgola mobile ($0{,}4$ calcolato come media può valere $0{,}39999\dots$). Esempio del libro: $p = 0{,}267$ (esatto 0,268, [scheda 46](L07-regressione-logistica-multinomiale-e-valutazione.md#p-46)); esercizio 11: 0,205 (esatto 0,207). Sulle 600 recensioni il bag of words batte le feature a mano di 0,082 con $p\approx 0$; due addestramenti dello stesso modello con un ordine diverso degli esempi differiscono di 0,007 con $p = 0{,}15$: rumore.

La figura: a sinistra i $\delta$ bootstrap del confronto parole contro feature a mano, centrati su $\delta(x) = 0{,}082$ (linea blu) e lontanissimi dalla linea rossa $2\delta(x) = 0{,}164$: nessun campione la raggiunge. A destra i due seed: la linea rossa $2\delta(x)\approx 0{,}013$ taglia la coda destra dell'istogramma, e la parte a destra è circa il 15% dei campioni.

> **Approfondimento: Perché gli istogrammi sono a pettine**
>
> Su 600 documenti $\delta$ è un multiplo di $1/600\approx 0{,}0017$, ma `hist` usa 40 intervalli di larghezza fissa che non si allineano a questi valori: alcuni intervalli contengono due valori possibili e altri uno (o nessuno, a destra), da cui le barre alternate alte e basse e i buchi. È un artefatto di disegno, non del test: il p-value si calcola sui valori, non sulle barre.

### Notebook 9 · Overfitting e regolarizzazione L2 e L1

```python
small = np.arange(150)
X_small, y_small = B_train[small], y_train[small]
for l2 in (0, 0.0003, 0.001, 0.003, 0.01, 0.03, 0.1):
    W, b, _ = train_softmax(X_small, y_small, eta=0.1, epochs=200, l2=l2)
    ...
for l1 in (0, 0.001, 0.003, 0.01, 0.03, 0.1):
    W, b, _ = train_softmax(X_small, y_small, eta=0.1, epochs=200, l1=l1)
```

Output:

```text
L2 regularization, 150 training reviews, 200 epochs:
   alpha   train acc  test acc   largest |w|   sum of w^2
       0      1.000     0.778         1.66         73.8
  0.0003      1.000     0.783         1.58         66.4
   0.001      0.987     0.788         1.42         53.0
   0.003      0.960     0.793         1.11         31.9
    0.01      0.940     0.798         0.68         12.5
    0.03      0.873     0.757         0.41          4.7
     0.1      0.647     0.570         0.31          1.4
L1 regularization, same data:
   alpha   train acc  test acc   non-zero weights (of 345)
       0      1.000     0.778        345
   0.001      0.987     0.782        320
   0.003      0.947     0.782        289
    0.01      0.907     0.770        212
    0.03      0.607     0.575        143
     0.1      0.493     0.417         43
```

Con 150 recensioni e 345 pesi, senza regolarizzazione il modello memorizza il training (accuracy 1,000) e fa 0,778 sul test. **L2**: al crescere di $\alpha$ la somma dei quadrati dei pesi scende da 73,8 a 1,4 e il peso massimo da 1,66 a 0,31; l'accuracy di training scende, quella di test sale fino a 0,798 ($\alpha = 0{,}01$) e poi crolla (underfitting). **L1**: i pesi diventano **esattamente** zero, 133 su 345 con $\alpha = 0{,}01$ (più di un terzo) con accuracy di test quasi invariata (0,770), 302 su 345 con $\alpha = 0{,}1$, ma a quel punto il modello è inutile. Il testo del notebook avverte giustamente che qui il test serve solo a mostrare l'effetto: $\alpha$ si sceglie con la cross-validation (primo suggerimento della sezione finale).

### Notebook 10 · Leggere i pesi

```python
for k, name in enumerate(LABELS):
    order = np.argsort(W_b[k])
    top = ", ".join(f"{vocab[j]} ({W_b[k, j]:.2f})" for j in order[-6:][::-1])
    ...
W_raw = W_h / std_h                # the learned weights, for the features before standardization
```

Output:

```text
negative  for: hate (1.49), my (0.80), predictable (0.73), evening (0.66), back (0.66), want (0.66)
          against: love (-1.25), go (-0.79), see (-0.65), wonderful (-0.55)
positive  for: love (1.08), go (0.75), see (0.67), fun (0.66), enjoyable (0.57), recommend (0.56)
          against: hate (-1.40), my (-0.62), boring (-0.58), back (-0.55)

feature                         negative   neutral  positive
positive lexicon words              0.29     -1.39      1.10
negative lexicon words              1.34     -1.50      0.16
'no' in the review                  0.79     -0.50     -0.30
1st and 2nd person pronouns         0.35     -0.46      0.11
exclamation mark                    0.25     -0.59      0.34
log(length)                        -1.62      2.35     -0.74
```

Ogni riga di $W$ è il prototipo di una classe ([scheda 12](L07-regressione-logistica-multinomiale-e-valutazione.md#p-12)): le parole più pesanti per il negativo vengono dalle chiusure dei template (*you will hate it*, *i want my evening back*), quelle del positivo da *you will love it*, *go and see it*, *i recommend it*. Il modello ha scoperto i template: in dati veri le parole forti sarebbero meno ovvie. Per le sei feature il notebook riporta i pesi sulla scala originale dividendo per la deviazione standard (corretto: $w\,(h-\mu)/s = (w/s)\,h - w\mu/s$, il termine costante va nel bias). Il punto esclamativo riproduce lo schema del libro: positivo per positivo e negativo, negativo per il neutro (0,25; −0,59; 0,34 contro 3,1; −5,3; 3,5). Il peso alto della lunghezza per il neutro mostra perché un peso non si legge isolato: lunghezza e conteggi di lessico sono correlati (confondenti, [scheda 53](L07-regressione-logistica-multinomiale-e-valutazione.md#p-53)).

## Studio ed esercizi

### Guida allo studio (circa 4 h 50 min)

**Softmax, matrice dei pesi, loss** (50 min)

Schede 5-19. Saper scrivere la softmax e dire perché le uscite sono probabilità; rifare a mano la tabella della scheda 9 e i conti della scheda 7 (sottraendo il massimo); invarianza alla traslazione e effetto della scala; forma matriciale $\hat{\mathbf y} = \text{softmax}(W\mathbf x + \mathbf b)$ con le dimensioni; righe di $W$ come prototipi; feature con un peso per classe (punto esclamativo). Loss: dalla somma $-\sum_k y_k\log\hat y_k$ a $-\log\hat y_c$, esempi 0,36, 0,30, 2,4. Esercizi 1, 2, 3, 5. Libro §4.7-4.8.

**Gradiente e aggiornamento** (30 min)

Schede 20-21. Derivare $\partial L/\partial w_{k,i} = (\hat y_k - y_k)x_i$ dalla forma log-sum-exp; leggere il segno (la riga corretta va verso $\mathbf x$, le altre se ne allontanano); fare un passo completo a mano. Esercizio 4; controllare con la cella 6 del notebook (gradiente numerico). Libro §4.8 e, per il caso binario, §4.15.

**Metriche di valutazione** (55 min)

Schede 23-31. Matrice di confusione (righe sistema, colonne gold), perché l'accuracy inganna (99,99% del classificatore senza torte), precision e recall con le loro domande, $F_\beta$ e $F_1$, media armonica (0,9 e 0,1 danno 0,18). Con tre classi: precision per riga e recall per colonna, le tre matrici classe-contro-resto, macro 0,60 e micro 0,73, perché micro P = micro R = accuracy. Esercizi 6, 7, 8, 9; cella 15 del notebook. Libro §4.9.

**Devset e cross-validation** (20 min)

Schede 32-35. Ruoli di training, devset e test; perché una divisione fissa è fragile; $k$-fold cross-validation passo per passo; perché in pratica si fa dentro il training set con un test fisso; leakage. Esercizio 10; celle 19-20 del notebook. Libro §4.10.

**Significatività e paired bootstrap** (55 min)

Schede 38-47. Effect size; perché $\delta$ varia con il test set; moneta e p-value (11/1024); ipotesi nulla, soglia fissata prima, cosa il p-value *non* dice; bootstrap appaiato con reinserimento; rifare a mano il campione $x^{(1)}$; perché la soglia è $2\delta(x)$; p = 0,27 sull'esempio. Esercizio 11; celle 23-24 del notebook. Libro §4.11.

**Danni, interpretazione, regolarizzazione** (35 min)

Schede 49-57. Danni rappresentazionali e silencing, fonti del bias, model card; lettura dei pesi e confondenti; overfitting, obiettivo regolarizzato, perché il bias non si penalizza; L2 contro L1 (grafico delle penalità, sparsità), weight decay, interpretazione bayesiana come prior. Esercizio 12; celle 28-29 e 32-33 del notebook. Libro §4.12-4.14.

**Notebook e ripasso orale** (45 min)

Eseguire il notebook dall'inizio; leggere `softmax_rows`, `batch_gradient`, `report`, `cross_validate` e `paired_bootstrap` finché si sa spiegare ogni riga (asse della softmax, righe/colonne della confusione, indici con reinserimento). Provare il bootstrap senza reinserimento e vedere che $p$ diventa 0. Poi rispondere ad alta voce alle domande della sezione orale senza guardare la traccia.

### Esercizi

#### Esercizio 1 (scheda L07): la softmax a mano

Sia $\mathbf z = [2, 1, 0]$. (a) Calcola $\text{softmax}(\mathbf z)$: i tre esponenziali, la loro somma, le tre probabilità; verifica che sommano a 1. (b) Calcola $\text{softmax}(\mathbf z + 3) = \text{softmax}([5, 4, 3])$ senza calcolatrice. Che cosa mostra? (c) Calcola $\text{softmax}(2\mathbf z) = \text{softmax}([4, 2, 0])$. Che cosa succede alla probabilità più grande quando i punteggi sono moltiplicati per una costante maggiore di 1?

<details><summary>Soluzione</summary>

(a) $e^2 = 7{,}389$, $e^1 = 2{,}718$, $e^0 = 1$; somma 11,107. Probabilità $[0{,}665;\ 0{,}245;\ 0{,}090]$, somma 1 (a meno di arrotondamenti).

(b) $\dfrac{e^{5}}{e^5+e^4+e^3} = \dfrac{e^3e^2}{e^3(e^2+e^1+e^0)} = \dfrac{e^2}{e^2+e+1}$: il fattore $e^3$ si semplifica, e così per ogni componente. Risultato identico, $[0{,}665;\ 0{,}245;\ 0{,}090]$. Mostra che la softmax dipende solo dalle **differenze** fra i punteggi: aggiungere una costante a tutti non cambia nulla (ed è il trucco di stabilità: sottrarre il massimo).

(c) $e^4 = 54{,}598$, $e^2 = 7{,}389$, $e^0 = 1$; somma 62,987; probabilità $[0{,}867;\ 0{,}117;\ 0{,}016]$. La probabilità più grande sale da 0,665 a 0,867: moltiplicare per una costante $&gt;1$ allarga le differenze e rende la distribuzione più appuntita (al limite, un argmax); dividere la rende più piatta (temperatura). Verificato con numpy e con la cella 2 del notebook.

</details>

#### Esercizio 2 (scheda L07): due classi, softmax e sigmoide

(a) Per $K = 2$ con punteggi $\mathbf z = [z_1, z_2]$, mostra che la prima componente della softmax è $\sigma(z_1 - z_2)$. (b) Una regressione logistica multinomiale a due classi ha vettori di pesi $\mathbf w_1, \mathbf w_2$ e bias $b_1, b_2$. Mostra che calcola la stessa probabilità di un classificatore binario e di' quali sono il suo vettore di pesi $\mathbf w$ e il suo bias $b$.

<details><summary>Soluzione</summary>

(a) Dividendo numeratore e denominatore per $e^{z_1}$:

$$\frac{e^{z_1}}{e^{z_1}+e^{z_2}} = \frac{1}{1+e^{z_2-z_1}} = \frac{1}{1+e^{-(z_1-z_2)}} = \sigma(z_1 - z_2)$$

e la seconda componente è $1 - \sigma(z_1-z_2) = \sigma(z_2 - z_1)$. Esempio della cella 2 del notebook: $\text{softmax}([1{,}5;\ 0{,}3])_1 = \sigma(1{,}2) = 0{,}7685$.

(b) Con $z_k = \mathbf w_k\cdot\mathbf x + b_k$: $P(y_1 = 1\mid\mathbf x) = \sigma\big((\mathbf w_1 - \mathbf w_2)\cdot\mathbf x + (b_1 - b_2)\big)$. È un classificatore logistico binario con $\mathbf w = \mathbf w_1 - \mathbf w_2$ e $b = b_1 - b_2$. Conseguenze: i due vettori non sono identificabili separatamente (aggiungendo lo stesso vettore a entrambi non cambia nulla), conta solo la differenza; e il caso binario della L6 è esattamente il caso $K = 2$ della softmax, con $2f+2$ parametri di cui solo $f+1$ efficaci.

</details>

#### Esercizio 3 (scheda L07): un classificatore di sentiment a tre vie

Classi positivo, negativo, neutro; due feature, $x_1$ = numero di parole del lessico positivo, $x_2$ = numero di parole del lessico negativo. Pesi e bias (una riga per classe, ordine +, −, 0):

$$W = \begin{bmatrix}2{,}0 & -1{,}5\\ -1{,}0 & 2{,}5\\ 0{,}2 & 0{,}3\end{bmatrix}\qquad \mathbf b = [0{,}5;\ 0{,}0;\ 1{,}0]$$

Una recensione ha $\mathbf x = [3, 2]$. (a) Calcola $\mathbf z = W\mathbf x + \mathbf b$ e $\hat{\mathbf y} = \text{softmax}(\mathbf z)$. Quale classe viene assegnata? (b) Calcola la cross-entropy loss se la classe corretta è positivo, e se è neutro. (c) Quale riga di $W$ è il prototipo del neutro? Per quale tipo di recensione il neutro vince sulle altre due?

<details><summary>Soluzione</summary>

(a) $z_+ = 2\cdot 3 - 1{,}5\cdot 2 + 0{,}5 = 3{,}5$; $z_- = -3 + 5 + 0 = 2{,}0$; $z_0 = 0{,}6 + 0{,}6 + 1 = 2{,}2$. Esponenziali $33{,}115;\ 7{,}389;\ 9{,}025$, somma 49,530. $\hat{\mathbf y} = [0{,}669;\ 0{,}149;\ 0{,}182]$: classe **positivo**.

(b) Positivo: $-\ln 0{,}669 = 0{,}403$. Neutro: $-\ln 0{,}182 = 1{,}703$ (per completezza, negativo: 1,903). Nota: le tre loss differiscono esattamente delle differenze fra i logit ($1{,}703 - 0{,}403 = 3{,}5 - 2{,}2$), perché $L = -z_c + \log\sum_j e^{z_j}$ e il secondo termine è comune.

(c) La terza riga, $[0{,}2;\ 0{,}3]$: pesi piccoli per entrambe le feature, il neutro vive del **bias** alto (1,0). Vince quando c'è poca evidenza di sentiment. Condizioni: $z_0 &gt; z_+ \iff 1{,}8(x_1 - x_2) &lt; 0{,}5$ e $z_0 &gt; z_- \iff 2{,}2x_2 - 1{,}2x_1 &lt; 1$. Per conteggi interi non negativi la prima richiede $x_1\le x_2$, e allora la seconda dà $x_2 &lt; 1$: il neutro vince solo per $\mathbf x = [0, 0]$, nessuna parola di lessico ($\mathbf z = [0{,}5;\ 0;\ 1]$, $\hat y_0 = 0{,}51$). Con $[1, 1]$ neutro e negativo pareggiano (1,5 e 1,5). Verificato numericamente.

</details>

#### Esercizio 4 (scheda L07): un passo di discesa del gradiente con K classi

Classificatore e recensione dell'esercizio 3, $\mathbf x = [3, 2]$, classe corretta neutro: $\mathbf y = [0, 0, 1]$. (a) Calcola il gradiente della loss rispetto a ogni peso $w_{k,i}$ e a ogni bias $b_k$, con $\partial L/\partial w_{k,i} = (\hat y_k - y_k)x_i$ e $\partial L/\partial b_k = \hat y_k - y_k$. (b) Aggiorna $W$ e $\mathbf b$ con learning rate $\eta = 0{,}1$ e ricalcola $\hat{\mathbf y}$ sulla stessa recensione. Quali righe si sono avvicinate a $\mathbf x$ e quali allontanate?

<details><summary>Soluzione</summary>

(a) Errore $\hat{\mathbf y} - \mathbf y = [0{,}669;\ 0{,}149;\ -0{,}818]$. Gradiente di $W$ = errore per $\mathbf x^{\top}$:

$$\nabla_W = \begin{bmatrix}2{,}006 & 1{,}337\\ 0{,}448 & 0{,}298\\ -2{,}453 & -1{,}636\end{bmatrix}\qquad \nabla_{\mathbf b} = [0{,}669;\ 0{,}149;\ -0{,}818]$$

(b) $W' = W - 0{,}1\,\nabla_W$, $\mathbf b' = \mathbf b - 0{,}1\,\nabla_{\mathbf b}$:

$$W' = \begin{bmatrix}1{,}799 & -1{,}634\\ -1{,}045 & 2{,}470\\ 0{,}445 & 0{,}464\end{bmatrix}\qquad\mathbf b' = [0{,}433;\ -0{,}015;\ 1{,}082]$$

Nuovi punteggi $\mathbf z' = [2{,}564;\ 1{,}791;\ 3{,}345]$, $\hat{\mathbf y}' = [0{,}274;\ 0{,}127;\ 0{,}599]$: la recensione ora è classificata neutra e la loss scende da 1,703 a 0,512. La riga del neutro (gradiente negativo) si è spostata **verso** $\mathbf x$: le aggiunge $0{,}0818\cdot[3, 2]$; le righe positivo e negativo (gradiente positivo) se ne sono **allontanate**, la positiva molto di più perché aveva preso più probabilità (0,669 contro 0,149). Verificato con la cella 6 del notebook, che controlla anche il gradiente numericamente.

</details>

#### Esercizio 5 (scheda L07): una feature con un peso per classe

Nel libro la feature del punto esclamativo di un classificatore di sentiment a tre vie ha pesi $w_{5,+} = 3{,}5$, $w_{5,-} = 3{,}1$, $w_{5,0} = -5{,}3$. (a) Senza questa feature un documento ha punteggi uguali $\mathbf z = [1{,}0;\ 1{,}0;\ 1{,}0]$. Calcola $\hat{\mathbf y}$ prima e dopo aver aggiunto il contributo di un punto esclamativo ($x_5 = 1$). (b) Spiega a parole che cosa dicono i tre pesi. (c) Nella notazione $f(x, y)$, quante feature con un solo peso ha un classificatore con 6 feature di input e 3 classi? E quanti bias?

<details><summary>Soluzione</summary>

(a) Prima: punteggi uguali, $\hat{\mathbf y} = [1/3;\ 1/3;\ 1/3]$. Dopo: $\mathbf z = [4{,}5;\ 4{,}1;\ -4{,}3]$; sottraendo il massimo $[0;\ -0{,}4;\ -8{,}8]$, esponenziali $[1;\ 0{,}670;\ 0{,}00015]$, somma 1,670: $\hat{\mathbf y} = [0{,}599;\ 0{,}401;\ 0{,}0001]$.

(b) Il punto esclamativo è evidenza **a favore** di un'opinione forte, positiva o negativa, quasi allo stesso modo (3,5 e 3,1) ed evidenza fortemente **contro** il neutro (−5,3). Da solo distingue poco tra positivo e negativo: conta la differenza 0,4, che sposta il rapporto fra le due da 1 a $e^{0{,}4} = 1{,}49$. Elimina invece quasi del tutto il neutro.

(c) Ogni coppia (feature, classe) diventa una feature $f_i(x, y)$ con un solo peso: $6\times 3 = 18$ feature e 18 pesi, cioè le celle di $W$ ($3\times 6$); più **3 bias**, uno per classe. Totale 21 parametri.

</details>

#### Esercizio 6 (scheda L07, libro 4.2): un classificatore di spam

Un classificatore di spam è eseguito su 1000 email, di cui 40 sono spam. Ne etichetta 30 come spam, e 24 di queste lo sono davvero. (a) Riempi la matrice di confusione: tp, fp, fn, tn. (b) Calcola accuracy, precision, recall e F1. (c) Calcola l'accuracy di un classificatore che etichetta tutto come non spam. Quale metrica è più utile qui, e perché?

<details><summary>Soluzione</summary>

(a) $tp = 24$; $fp = 30 - 24 = 6$; $fn = 40 - 24 = 16$; $tn = 1000 - 24 - 6 - 16 = 954$.

(b) Accuracy $= (24 + 954)/1000 = 0{,}978$. Precision $= 24/30 = 0{,}80$. Recall $= 24/40 = 0{,}60$. $F_1 = 2\cdot 0{,}8\cdot 0{,}6/(0{,}8+0{,}6) = 0{,}96/1{,}4 = 0{,}686$.

(c) Tutto non spam: $tn = 960$, $fn = 40$, accuracy $= 960/1000 = 0{,}96$, appena 1,8 punti sotto il classificatore vero, ma recall 0 e precision indefinita (0/0). Le metriche utili sono **precision, recall e F1**, che guardano la classe rara: distinguono un classificatore che trova il 60% dello spam con l'80% di precisione da uno che non trova nulla, mentre l'accuracy, dominata dai 960 non spam, quasi non li separa.

</details>

#### Esercizio 7 (scheda L07): la Delicious Pie Company

Su un milione di tweet, 100 parlano di Delicious Pie. (a) Il classificatore che etichetta ogni tweet come non pertinente: accuracy, recall, e che cosa succede alla precision. (b) Un secondo classificatore segnala 200 tweet come pertinenti, 80 dei quali lo sono davvero. Calcola precision, recall, F1 e accuracy, e confrontalo con il primo.

<details><summary>Soluzione</summary>

(a) $tn = 999.900$, $fn = 100$, $tp = fp = 0$. Accuracy $= 999.900/1.000.000 = 0{,}9999$; recall $= 0/100 = 0$; precision $= 0/0$, **indefinita** (nessun tweet etichettato positivo; per convenzione spesso 0, e allora $F_1 = 0$).

(b) $tp = 80$, $fp = 120$, $fn = 20$, $tn = 1.000.000 - 80 - 120 - 20 = 999.780$. Precision $= 80/200 = 0{,}40$; recall $= 80/100 = 0{,}80$; $F_1 = 2\cdot 0{,}4\cdot 0{,}8/1{,}2 = 0{,}533$; accuracy $= (80 + 999.780)/10^6 = 0{,}99986$.

Confronto: il secondo classificatore ha accuracy **più bassa** del primo (0,99986 contro 0,9999, perché fa 140 errori invece di 100) eppure è l'unico utile: trova l'80% dei tweet cercati. L'accuracy premia il classificatore inutile; recall e F1 (0 contro 0,533) danno l'ordine giusto.

</details>

#### Esercizio 8 (scheda L07): la F-measure

(a) Un sistema ha precision 0,5 e recall 0,9. Calcola $F_1$, $F_{0,5}$, $F_2$ e la media aritmetica di P e R. Quale F favorisce la recall? (b) Un altro sistema restituisce pochissimi risultati, tutti corretti: $P = 1{,}0$, $R = 0{,}05$. Calcola $F_1$ e la media aritmetica. Quale delle due riflette l'utilità del sistema? (c) Perché l'F-measure usa la media armonica invece di quella aritmetica?

<details><summary>Soluzione</summary>

(a) Con $F_\beta = (\beta^2+1)PR/(\beta^2P + R)$ e $PR = 0{,}45$:

- $F_1 = 2\cdot 0{,}45/1{,}4 = 0{,}643$;
- $F_{0,5} = 1{,}25\cdot 0{,}45/(0{,}25\cdot 0{,}5 + 0{,}9) = 0{,}5625/1{,}025 = 0{,}549$;
- $F_2 = 5\cdot 0{,}45/(4\cdot 0{,}5 + 0{,}9) = 2{,}25/2{,}9 = 0{,}776$;
- media aritmetica 0,70.

$F_2$ ($\beta &gt; 1$) favorisce la recall: qui la recall è alta e infatti $F_2$ è il valore più alto; $F_{0,5}$ favorisce la precision ed è il più basso.

(b) $F_1 = 2\cdot 1\cdot 0{,}05/1{,}05 = 0{,}095$; media aritmetica 0,525. Il sistema trova il 5% di ciò che c'è: è quasi inutile, e lo dice $F_1$; la media aritmetica, sopra 0,5, lo fa sembrare discreto.

(c) La media armonica resta vicina al **minimo** dei due valori (è sempre compresa fra il minimo e la media aritmetica, e $F_1\le 2\min(P,R)$): un $F_1$ alto richiede che *entrambe* siano buone, e non si può "comprare" con una precision perfetta e una recall nulla (o il contrario, un sistema che dice sempre sì ha recall 1). Inoltre la media armonica è la media giusta per rapporti con lo stesso numeratore ($tp$): $1/F_1 = \frac12\left(\frac{tp+fp}{tp} + \frac{tp+fn}{tp}\right)$, cioè $F_1 = 2tp/(2tp + fp + fn)$.

</details>

#### Esercizio 9 (scheda L07, con libro 4.1): tre classi, macro e micro

La matrice di confusione del libro (righe: uscita del sistema; colonne: gold):

|  | gold urgent | gold normal | gold spam |
| --- | --- | --- | --- |
| sistema urgent | 8 | 10 | 1 |
| sistema normal | 5 | 60 | 50 |
| sistema spam | 3 | 30 | 200 |

(a) Calcola la recall di ogni classe, la recall macroaverage e la recall microaverage. (b) Il libro calcola la precision microaverage, $268/367\approx 0{,}73$. Perché la precision microaverage è sempre uguale alla recall microaverage? (c) Quale delle due medie riporteresti se la classe che conta di più è urgent?

<details><summary>Soluzione</summary>

(a) Recall = diagonale / somma della colonna: urgent $8/16 = 0{,}500$; normal $60/100 = 0{,}600$; spam $200/251 = 0{,}797$. Macro $= (0{,}5 + 0{,}6 + 0{,}797)/3 = 0{,}632$. Micro: $\sum tp/(\sum tp + \sum fn) = 268/(268 + 99) = 268/367 = 0{,}730$ (i false negative sono 8 + 40 + 51 = 99).

(b) Con una sola etichetta per documento, ogni errore sta in una cella fuori diagonale (riga $r$, colonna $g$, $r\ne g$) ed è contemporaneamente un false positive per la classe $r$ e un false negative per la classe $g$. Quindi $\sum_k fp_k = \sum_k fn_k$ = numero di celle fuori diagonale (99) e micro P $= \sum tp/(\sum tp + \sum fp)$ = micro R; entrambe valgono $\sum tp/N$, cioè l'**accuracy**, e anche il micro F1.

(c) La **macroaverage**, o meglio ancora le misure per classe di urgent riportate esplicitamente (P 0,42, R 0,50, F1 0,46). La micro è dominata da spam (251 documenti su 367) e qui coincide con l'accuracy: urgent, 16 documenti, quasi non la sposta. Nella macro urgent pesa un terzo. Verificato con `report` nella cella 15 del notebook.

</details>

#### Esercizio 10 (scheda L07): development set e cross-validation

Hai 1000 documenti etichettati. (a) Con una 5-fold cross-validation su tutti i documenti, quanti modelli addestri, su quanti documenti ciascuno, e su quanti testi ciascuno? Come si calcola il punteggio finale? (b) Seguendo il libro, metti da parte 200 documenti come test set e fai una 5-fold cross-validation dentro gli 800 rimanenti per scegliere il learning rate. Quanti modelli, con quanti documenti di training e di dev ciascuno, e quante volte si usa il test set? (c) Perché è un problema progettare le feature guardando tutto il corpus quando si valuta con la cross-validation, e che cosa risolve lo schema di (b)?

<details><summary>Soluzione</summary>

(a) 5 modelli; ciascuno addestrato su 4 fold = 800 documenti e testato sul fold restante di 200. Ogni documento è testato una volta. Punteggio finale: la **media** dei 5 punteggi (o tassi d'errore) sui fold di test.

(b) Per ogni valore candidato del learning rate, 5 modelli, ciascuno con $800\cdot 4/5 = 640$ documenti di training e 160 di dev; si sceglie il valore con la miglior media sui fold di dev. Con $L$ valori candidati sono $5L$ modelli (es. 5 valori, 25 modelli), più **un** modello finale addestrato su tutti gli 800 con il valore scelto. Il test set si usa **una sola volta**, alla fine, su quel modello.

(c) Nella cross-validation su tutto il corpus ogni documento prima o poi è nel test: guardare il corpus per inventare feature significa guardare il test, e le feature risultano tagliate su quei documenti; la stima delle prestazioni è ottimista (è una forma di contaminazione). Nello schema (b) si può guardare liberamente il training (gli 800) per progettare feature e analizzare errori, mentre i 200 di test restano ciechi fino alla valutazione finale.

</details>

#### Esercizio 11 (scheda L07): il paired bootstrap a mano

Due classificatori A e B confrontati su un test set di cinque documenti, metrica accuracy:

| documento | 1 | 2 | 3 | 4 | 5 |
| --- | --- | --- | --- | --- | --- |
| A | giusto | giusto | sbagliato | giusto | giusto |
| B | giusto | sbagliato | giusto | sbagliato | sbagliato |

(a) Calcola l'accuracy di A e B e l'effect size $\delta(x)$. (b) Tre test set virtuali estratti con reinserimento: (1, 2, 2, 4, 5), (3, 3, 1, 5, 2), (2, 4, 5, 5, 4). Calcola $\delta$ su ciascuno e di' se conta per il p-value del paired bootstrap, cioè se $\delta(x^{(i)})\ge 2\delta(x)$. (c) *[difficile]* Perché il test conta i campioni con $\delta(x^{(i)})\ge 2\delta(x)$ invece che $\delta(x^{(i)})\ge\delta(x)$? (d) Su un test set più grande, con $b = 10.000$ test set virtuali, 320 hanno $\delta(x^{(i)})\ge 2\delta(x)$. Qual è il p-value? La differenza è significativa alla soglia 0,05? E a 0,01?

<details><summary>Soluzione</summary>

(a) A: 4/5 = 0,8; B: 2/5 = 0,4; $\delta(x) = 0{,}4$, quindi $2\delta(x) = 0{,}8$.

(b) Si ricopiano le colonne:

- (1, 2, 2, 4, 5): A giusto su tutti, 1,0; B giusto solo sull'1, 0,2; $\delta = 0{,}8\ge 0{,}8$: **conta**;
- (3, 3, 1, 5, 2): A giusto su 1, 5, 2: 0,6; B giusto su 3, 3, 1: 0,6; $\delta = 0$: non conta;
- (2, 4, 5, 5, 4): A 1,0; B 0,0; $\delta = 1{,}0\ge 0{,}8$: **conta**.

(Attenzione al primo: $\delta = 0{,}8$ esattamente, conta perché la disuguaglianza è $\ge$; in virgola mobile serve una tolleranza, come nel notebook.)

(c) *[difficile]* Il p-value si calcola **sotto $H_0$**, dove $\delta$ dovrebbe oscillare attorno a 0. Ma i campioni bootstrap sono estratti da $x$, che è sbilanciato di $\delta(x)$ a favore di A: la loro distribuzione è centrata su $\delta(x)$, non su 0. Si sposta allora tutta la distribuzione di $-\delta(x)$ per centrarla in 0 e si chiede quanto spesso raggiunge $\delta(x)$: $\delta(x^{(i)}) - \delta(x)\ge\delta(x)$, cioè $\delta(x^{(i)})\ge 2\delta(x)$ (Eq. 4.48). Con la soglia $\delta(x)$ si conterebbe circa metà dei campioni qualunque sia la differenza (sull'esempio del libro 0,59 invece di 0,27): il test non direbbe nulla.

(d) $p = 320/10.000 = 0{,}032$. Significativo a 0,05 ($0{,}032 &lt; 0{,}05$), **non** a 0,01. Per il test set di cinque documenti, il p-value esatto è 0,207 (notebook, $b = 100.000$: 0,205): non significativo.

</details>

#### Esercizio 12 (scheda L07): regolarizzazione L2 e L1

Due vettori di pesi si adattano ugualmente bene ai dati: $\theta_A = [3, 0, 0, 0]$ e $\theta_B = [1{,}5;\ 1{,}5;\ 1{,}5;\ 1{,}5]$. (a) Calcola la penalità L2 $\lVert\theta\rVert_2^2$ e la penalità L1 $\lVert\theta\rVert_1$ di ciascuno. Quale vettore preferisce ciascun tipo di regolarizzazione? (b) *[difficile]* L'obiettivo con L2 sottrae $\alpha\sum_j\theta_j^2$. Scrivi l'aggiornamento della discesa del gradiente per un peso $\theta_j$ con learning rate $\eta$ e mostra che la penalità riduce il peso di un fattore costante a ogni passo. Calcola il fattore per $\eta = 0{,}1$ e $\alpha = 0{,}5$. (c) Quale regolarizzazione sceglieresti per un classificatore con un milione di feature di parole che deve girare su un dispositivo piccolo, e perché? *[difficile]* Quale è più facile da ottimizzare?

<details><summary>Soluzione</summary>

(a) L2: $\theta_A$: $9$; $\theta_B$: $4\cdot 2{,}25 = 9$. L1: $\theta_A$: 3; $\theta_B$: 6. Con questi numeri **L2 è indifferente** (stessa penalità 9: i due vettori hanno la stessa lunghezza euclidea, 3), mentre **L1 preferisce $\theta_A$**, il vettore sparso (3 contro 6). Il risultato mostra la differenza di geometria: L1 premia la sparsità a parità di norma L2; L2 invece, a parità di norma L1, preferisce i pesi distribuiti (es. $[1{,}5;\ 1{,}5]$ ha L2 4,5 contro 9 di $[3, 0]$).

(b) *[difficile]* Massimizzare $\sum\log P - \alpha\sum_j\theta_j^2$ equivale a minimizzare $L + \alpha\sum_j\theta_j^2$, con $L = -\sum\log P$ la cross-entropy; la derivata della penalità è $2\alpha\theta_j$, quindi

$$\theta_j\leftarrow\theta_j - \eta\left(\frac{\partial L}{\partial\theta_j} + 2\alpha\theta_j\right) = (1 - 2\eta\alpha)\,\theta_j - \eta\frac{\partial L}{\partial\theta_j}$$

A ogni passo, prima della correzione dovuta ai dati, il peso è moltiplicato per $1 - 2\eta\alpha$ (*weight decay*): con $\eta = 0{,}1$, $\alpha = 0{,}5$ il fattore è $1 - 0{,}1 = 0{,}9$, un 10% di riduzione per passo. Se i dati non spingono il peso (gradiente della loss nullo, per esempio una parola mai presente nel batch), il peso decade geometricamente verso 0 senza mai arrivarci.

(c) **L1**: produce un vettore sparso, con la maggior parte dei pesi esattamente 0; le feature con peso nullo si possono eliminare, quindi il modello occupa poca memoria ed è veloce (con un milione di parole la maggior parte non porta informazione sulla classe; nel notebook già con 345 pesi L1 ne azzera più di un terzo a costo quasi nullo). *[difficile]* **L2** è più facile da ottimizzare: la penalità è differenziabile ovunque con derivata semplice $2\theta$, mentre $|\theta|$ non è differenziabile in 0 (servono subgradienti o il soft thresholding del notebook).

</details>

#### Esercizio aggiuntivo A: il gradiente della softmax con la log-sum-exp

(a) Mostra che $L_{CE} = -\log\hat y_c = -z_c + \log\sum_{j=1}^{K}e^{z_j}$. (b) Deriva $\partial L/\partial z_k$ per $k = c$ e per $k\ne c$, e scrivi il risultato in un'unica formula. (c) Usa la regola della catena per ottenere $\partial L/\partial w_{k,i}$ e $\partial L/\partial b_k$. (d) Verifica che $\sum_k\partial L/\partial z_k = 0$ e spiega che cosa significa.

<details><summary>Soluzione</summary>

(a) $\hat y_c = e^{z_c}/\sum_j e^{z_j}$, quindi $-\log\hat y_c = -z_c + \log\sum_j e^{z_j}$.

(b) $\dfrac{\partial}{\partial z_k}\log\sum_j e^{z_j} = \dfrac{e^{z_k}}{\sum_j e^{z_j}} = \hat y_k$. Il termine $-z_c$ contribuisce $-1$ solo se $k = c$. Quindi $\partial L/\partial z_c = \hat y_c - 1$ e $\partial L/\partial z_k = \hat y_k$ per $k\ne c$; in una formula, $\partial L/\partial z_k = \hat y_k - y_k$ con $\mathbf y$ one-hot.

(c) $z_k = \sum_i w_{k,i}x_i + b_k$ dipende solo dalla riga $k$: $\partial z_k/\partial w_{k,i} = x_i$, $\partial z_k/\partial b_k = 1$. Quindi $\partial L/\partial w_{k,i} = (\hat y_k - y_k)x_i$ e $\partial L/\partial b_k = \hat y_k - y_k$ (Eq. 4.41).

(d) $\sum_k(\hat y_k - y_k) = 1 - 1 = 0$. Il gradiente rispetto ai logit non ha componente nella direzione $[1, 1, \dots, 1]$: aggiungere la stessa quantità a tutti i logit non cambia la loss (invarianza della softmax), e gli aggiornamenti "tolgono" alle classi sbagliate esattamente quanto "danno" alla corretta. Verifica numerica sull'esercizio 4: $0{,}669 + 0{,}149 - 0{,}818 = 0$.

</details>

### Domande tipo orale

<details><summary>Che cos'è la softmax e in che senso generalizza la sigmoide?</summary>

Traccia: (1) definizione $\text{softmax}(z_i) = e^{z_i}/\sum_j e^{z_j}$, da $K$ logit a $K$ probabilità in $[0,1]$ che sommano a 1; (2) esponenziale per la positività, denominatore comune per normalizzare; conserva l'ordine e schiaccia verso il massimo (esempio: $z_5 = 3{,}2$ prende il 74%); (3) dipende solo dalle differenze: invariante alla traslazione, da cui il trucco di sottrarre il massimo; (4) per $K = 2$ la prima componente è $\sigma(z_1 - z_2)$: la regressione logistica binaria è il caso $K = 2$ con $\mathbf w = \mathbf w_1 - \mathbf w_2$; (5) è lo strato di uscita degli LLM ($|V|$ classi).

</details>

<details><summary>Come è fatta la regressione logistica multinomiale? Che forma hanno i parametri e come si interpretano?</summary>

Traccia: (1) un vettore di pesi e un bias per classe, $z_k = \mathbf w_k\cdot\mathbf x + b_k$, poi softmax; (2) in forma matriciale $\hat{\mathbf y} = \text{softmax}(W\mathbf x + \mathbf b)$, $W$ di forma $K\times f$, $\mathbf b$ di $K$ elementi, $Kf + K$ parametri; (3) ogni riga di $W$ è un prototipo della classe, il prodotto scalare una similarità; (4) un peso per (feature, classe): la stessa feature può essere a favore di alcune classi e contro altre (punto esclamativo 3,5, 3,1, −5,3); notazione $f(x, y)$; (5) contano le differenze fra righe.

</details>

<details><summary>Qual è la loss della regressione logistica multinomiale e perché si chiama negative log likelihood?</summary>

Traccia: (1) cross-entropy $-\sum_k y_k\log\hat y_k$, un termine per classe, generalizza i due termini del caso binario; (2) con $\mathbf y$ one-hot resta solo $-\log\hat y_c$: meno il log della probabilità della classe corretta, cioè della verosimiglianza dell'etichetta osservata; (3) esempi: $-\ln 0{,}7 = 0{,}36$; 0,30 e 2,4 sull'esempio a sei classi; (4) curva: 0 per $\hat y_c = 1$, infinito per $\hat y_c\to 0$; (5) le altre classi contano tramite la normalizzazione: per alzare $\hat y_c$ bisogna abbassare le altre; (6) è la cross-entropy della L5 fra distribuzione vera (one-hot) e modello.

</details>

<details><summary>Derivi il gradiente della cross-entropy rispetto a un peso $w_{k,i}$ e spieghi l'effetto di un aggiornamento.</summary>

Traccia: (1) $L = -z_c + \log\sum_j e^{z_j}$; (2) $\partial L/\partial z_k = \hat y_k - y_k$; (3) catena: $\partial z_k/\partial w_{k,i} = x_i$, quindi $(\hat y_k - y_k)x_i$; bias $\hat y_k - y_k$; matrice $(\hat{\mathbf y} - \mathbf y)\mathbf x^{\top}$; (4) stessa forma del binario $(\hat y - y)x$; (5) aggiornamento $\mathbf w_k\leftarrow\mathbf w_k - \eta(\hat y_k - y_k)\mathbf x$: la riga corretta va verso $\mathbf x$, le sbagliate si allontanano in proporzione alla probabilità presa; si muovono solo le feature presenti; (6) esempio con errori +0,2, −0,3, +0,1, che sommano a 0.

</details>

<details><summary>Perché l'accuracy non basta per valutare un classificatore di testi? Che cosa misurano precision e recall?</summary>

Traccia: (1) matrice di confusione, righe sistema e colonne gold, tp/fp/fn/tn; (2) accuracy = corretti/totale; con classi sbilanciate il classificatore della classe maggioritaria ha accuracy altissima (no-pie: 99,99%) e non trova nulla; (3) precision $tp/(tp+fp)$: quando dice sì, quanto è affidabile; recall $tp/(tp+fn)$: quanto di ciò che c'è trova; entrambe mettono al centro i true positive; (4) no-pie: recall 0, precision 0/0 indefinita; (5) compromesso tramite la soglia di decisione.

</details>

<details><summary>Che cos'è la F-measure e perché usa la media armonica?</summary>

Traccia: (1) $F_\beta = (\beta^2+1)PR/(\beta^2P + R)$, van Rijsbergen 1975; (2) $\beta &gt; 1$ favorisce la recall, $\beta &lt; 1$ la precision; $F_1 = 2PR/(P+R)$ la più usata; (3) è una media armonica pesata ($\beta^2 = (1-\alpha)/\alpha$); (4) la media armonica sta vicino al minimo: $P = 0{,}9$, $R = 0{,}1$ dà 0,18 contro 0,50 della media aritmetica; un $F_1$ alto richiede entrambe; (5) forma con i conteggi $F_1 = 2tp/(2tp+fp+fn)$.

</details>

<details><summary>Come si valuta un classificatore con più di due classi? Differenza fra macro e micro average.</summary>

Traccia: (1) matrice $K\times K$, precision per classe = diagonale/riga, recall = diagonale/colonna (urgent 8/19 = 0,42 e 8/16 = 0,50); (2) per un solo numero, matrici classe-contro-resto; (3) macro: media delle misure per classe, ogni classe pesa uguale (0,60), adatta quando tutte le classi contano, riflette le classi piccole; (4) micro: somma delle matrici, poi la misura (268/367 = 0,73), ogni documento pesa uguale, dominata dalla classe frequente; (5) micro P = micro R = accuracy, perché ogni errore è un fp per una classe e un fn per un'altra.

</details>

<details><summary>A che cosa servono training, development e test set? Che cos'è la cross-validation e come la si usa in pratica?</summary>

Traccia: (1) training per i pesi, devset per iperparametri e scelta del modello (evita overfitting del test), test una volta per il risultato; (2) divisione fissa: test o dev troppo piccoli e poco rappresentativi; (3) $k$-fold: $k$ fold disgiunti, $k$ modelli addestrati su $k-1$, media degli errori; con $k = 10$ ognuno sul 90%; (4) problema: tutto il corpus finisce nel test, non si può guardarlo per progettare feature; (5) soluzione: test fisso e cross-validation dentro il training (Fig. 4.10); (6) leakage: ogni statistica (vocabolario, standardizzazione) solo sui fold di training.

</details>

<details><summary>Il classificatore A batte B di 0,04 in F1. Che cosa si può concludere? Spieghi la logica di un test di significatività.</summary>

Traccia: (1) $\delta(x) = M(A,x) - M(B,x)$, effect size; (2) $\delta$ dipende dal test set (0,20, 0,00, −0,10 su tre test set di 10 documenti): A potrebbe essere stato fortunato; (3) ipotesi nulla $H_0$: A non è migliore ($\delta\le 0$); (4) p-value $= P(\delta(X)\ge\delta(x)\mid H_0)$, probabilità di un risultato almeno altrettanto estremo se $H_0$ è vera (moneta: 9 teste su 10, 11/1024); (5) soglia fissata prima (0,05, 0,01); sotto la soglia si rifiuta $H_0$: significativo; (6) con 0,04 il p-value può essere alto (0,34 nella figura).

</details>

<details><summary>Che cosa il p-value non dice? Che rapporto c'è con l'effect size?</summary>

Traccia: (1) non è la probabilità che $H_0$ sia vera: è calcolato assumendola vera, probabilità dei dati non dell'ipotesi; (2) $p$ sopra la soglia non dimostra che A e B siano uguali: solo che non lo possiamo escludere; (3) $p$ non dice quanto A è migliore: quello è $\delta$; (4) con un test set enorme anche un $\delta$ minuscolo è significativo, con uno piccolo anche un $\delta$ grande può non esserlo (0,20 su 10 documenti: $p = 0{,}27$); riportare entrambi; (5) la soglia va scelta prima.

</details>

<details><summary>Descriva il paired bootstrap test. Perché paired, perché con reinserimento, perché la soglia 2δ(x)?</summary>

Traccia: (1) un solo test set: si creano $b$ test set virtuali estraendo $n$ documenti da $x$ con reinserimento; (2) paired: per ogni documento si tengono i risultati di entrambi, la difficoltà comune si cancella; (3) senza reinserimento ogni campione sarebbe una permutazione di $x$, sempre lo stesso $\delta$; (4) si calcola $\delta(x^{(i)})$ su ciascuno; la distribuzione è centrata su $\delta(x)$ perché $x$ è sbilanciato verso A; sotto $H_0$ sarebbe centrata in 0: si sposta e si conta $\delta(x^{(i)}) - \delta(x)\ge\delta(x)$, cioè $\ge 2\delta(x)$; (5) esempio: 10 documenti, $\delta = 0{,}20$, $p = 0{,}27$, non significativo; (6) vale per qualunque metrica, anche F1 o BLEU.

</details>

<details><summary>Quali danni possono causare i classificatori e da dove vengono i bias? Che cos'è una model card?</summary>

Traccia: (1) danni rappresentazionali: sminuire un gruppo, stereotipi; 200 sistemi di sentiment con frasi identiche salvo il nome (Kiritchenko e Mohammad 2018); (2) toxicity detection: falsi positivi su frasi che menzionano identità o usano l'AAVE, silencing; (3) fonti: dati (replicati e amplificati), etichette, risorse come lessici o embedding, obiettivo di ottimizzazione; nessuna soluzione generale; (4) model card (Mitchell et al. 2019): algoritmo e parametri, dati di training e di valutazione (fonti, motivazione, preprocessing), uso e utenti previsti, prestazioni per gruppo e situazione.

</details>

<details><summary>Come si interpreta un modello di regressione logistica? Che cosa sono i confondenti?</summary>

Traccia: (1) interpretabilità: capire perché il modello decide; (2) feature progettate a mano, ogni peso ha segno (direzione) e grandezza (forza); test di significatività sulla singola feature (likelihood ratio, Wald); (3) cautele: scale delle feature, differenze fra righe nel multinomiale; (4) uso come strumento di analisi: *no, not, never* e sentiment negativo; (5) confondenti: genere, anno, lunghezza; inserirli come feature così ogni peso misura l'effetto a parità delle altre; anche per esiti non linguistici (riammissioni, elezioni, vendite).

</details>

<details><summary>Che cos'è l'overfitting nella regressione logistica e come lo combatte la regolarizzazione? Differenza fra L2 e L1.</summary>

Traccia: (1) una parola presente in una sola recensione positiva sembra perfettamente predittiva e riceve un peso enorme; modello perfetto sul training, scarso sul test; (2) obiettivo $\sum\log P(y\mid x) - \alpha R(\theta)$, $\alpha$ prezzo dei pesi grandi, scelto con devset o cross-validation; bias non penalizzato; (3) L2 (ridge) $\sum\theta^2$: tanti pesi piccoli, derivata $2\theta$, weight decay $(1-2\eta\alpha)$; (4) L1 (lasso) $\sum|\theta|$: pendenza costante, pesi esattamente 0, modelli sparsi, derivata discontinua in 0; (5) esempio del notebook: L2 porta il test da 0,778 a 0,798, L1 con $\alpha = 0{,}01$ azzera 133 pesi su 345.

</details>

<details><summary>In che senso la regolarizzazione è un prior?</summary>

Traccia: (1) prior $P(\theta)$: credenza sui pesi prima dei dati, piccoli e vicini a 0; (2) stima MAP: massimizzare $\prod P(y\mid x)\prod_j P(\theta_j)$, in log $\sum\log P(y\mid x) + \sum\log P(\theta_j)$; (3) prior gaussiano a media 0: $\log P(\theta_j) = -\theta_j^2/(2\sigma^2) + c$, cioè L2 con $\alpha = 1/(2\sigma^2)$ (il libro pone $2\sigma^2 = 1$); (4) prior di Laplace: $-|\theta_j|/s + c$, cioè L1; più appuntito in 0, quindi più pesi nulli; (5) prior più stretto = regolarizzazione più forte.

</details>
