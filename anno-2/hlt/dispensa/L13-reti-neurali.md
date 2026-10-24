# L13 · Reti neurali

*Neural Networks: From language to a prediction, and back again* · 13/10/2026 · Andrea Ceni · lettura: J&M cap. 6, §6.1-6.6 (pp. 151-176); approssimazione universale e tecniche di training (Adam, schedule, weight decay, LayerNorm, residual) dalle slide

[Versione interattiva sul sito](https://gabriele-marsili.github.io/appunti-magistrale-ai/anno-2/hlt/sito/#L13) · [Indice della dispensa](README.md)

Prima lezione di Andrea Ceni, sul capitolo 6 di J&M: le **reti neurali feedforward**. Un'**unità** è una somma pesata più una **non linearità** (sigmoide, tanh, **ReLU**); un'unità sola è un classificatore lineare e non calcola **XOR**, mentre uno **strato nascosto** impara una rappresentazione in cui il problema diventa lineare. Senza non linearità gli strati collassano in uno; con essa vale l'**approssimazione universale**, che però garantisce solo l'esistenza. Poi la forward pass con le **forme** dei tensori, **logit**, **softmax** e **cross-entropy**; il testo che entra come **embedding** (matrice $E$, pooling, masking), il classificatore di sentiment e il **language model feedforward** di Bengio. Nella seconda parte la **backpropagation** come regola della catena su un **grafo computazionale**, e la ricetta moderna di training: Adam/AdamW, schedule, weight decay, dropout, inizializzazione, LayerNorm, connessioni residue, tutto ancora dentro un LLM. Tutti i numeri delle slide sono ricalcolati e tornano; non ci sono errori da correggere.

## Indice

- [Apertura](#apertura)
- [L'unità neurale](#l-unita-neurale)
- [Strati nascosti e XOR](#strati-nascosti-e-xor)
- [Reti feedforward](#reti-feedforward)
- [Reti neurali per il linguaggio](#reti-neurali-per-il-linguaggio)
- [Come impara la rete](#come-impara-la-rete)
- [Training in pratica](#training-in-pratica)
- [Che cosa resta in un LLM](#che-cosa-resta-in-un-llm)
- [Studio ed esercizi](#studio-ed-esercizi)

## Apertura

<a id="p-1"></a>

### Slide 1 · Reti neurali

Tredicesima lezione, la prima di Andrea Ceni: il capitolo 6 di J&M (*Neural Networks*). Il sottotitolo, *from language to a prediction, and back again*, riassume il percorso: si parte da un testo, lo si trasforma in numeri (embedding), una rete lo trasforma in una **distribuzione di probabilità** sulle risposte possibili, e poi l'errore torna indietro (*back again*) per correggere i parametri con la **backpropagation**.

Quasi tutto è già noto in forma più semplice:

- la **regressione logistica** binaria e multinomiale ([L6](L06-regressione-logistica.md#p-20), [L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-10)) è una rete a un solo strato;
- la **softmax** e la **cross-entropy** sono quelle della [L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-16);
- gli **embedding** sono quelli della [L11](L11-embedding-word2vec.md#p-5);
- il **modello linguistico neurale** era stato annunciato alla fine della [L5](L05-smoothing-ed-entropia.md#p-42).

Il pezzo davvero nuovo è lo **strato nascosto**, con la non linearità che lo rende utile, e il modo di calcolare i gradienti attraverso molti strati.

<a id="p-2"></a>

### Slide 2 · Riferimento: J&M capitolo 6, §6.1-6.6

Lettura: **Jurafsky & Martin**, *Speech and Language Processing*, 3a ed. draft del 19 agosto 2026, capitolo 6, pagine stampate 151-176:

- 6.1 Units (152-154): somma pesata, bias, sigmoide, tanh, ReLU;
- 6.2 The XOR problem (154-157): perceptron, separabilità lineare, la rete XOR di Goodfellow;
- 6.3 Feedforward neural networks (157-161): strati, matrici, softmax, notazione con gli apici [ℓ], perché serve la non linearità;
- 6.4 Feedforward networks for NLP: classification (161-163): feature costruite a mano e vettorizzazione su un batch;
- 6.5 Embeddings as the input (163-168): matrice $E$, pooling, language model feedforward;
- 6.6 Training neural nets (168-175): cross-entropy, grafi computazionali, backward differentiation, consigli pratici.

Il capitolo non ha esercizi di fine capitolo: la scheda ufficiale della lezione (13 esercizi) li sostituisce, e il suo esercizio 10 completa la backward pass che il libro lascia al lettore (§6.6.4). Il teorema di approssimazione universale e gran parte delle tecniche di training dell'ultima parte (Adam, schedule, weight decay, LayerNorm, residual) sono **oltre il libro**: per quelli fanno fede le slide.

<a id="p-3"></a>

### Slide 3 · Un problema di previsione linguistica

Due compiti che sembrano diversi:

- **Task A, language modelling**: *The film was unexpectedly \_\_\_*. La risposta non è una parola ma una **probabilità su tutto il vocabolario** ([L4](L04-modelli-linguistici-n-gram.md#p-5)).
- **Task B, sentiment**: *"This movie was painfully slow."* positivo, negativo o neutro? Di nuovo una **probabilità su un piccolo insieme di classi** ([L6](L06-regressione-logistica.md#p-5)).

La domanda guida (*che cosa deve produrre esattamente la macchina?*) porta a vederli come **lo stesso problema computazionale**: mappare un testo in una **distribuzione su un insieme fisso di risposte**. Cambia solo la dimensione dell'insieme: 3 classi oppure $|V|$ parole. Il language modelling è quindi una classificazione con tantissime classi, e la stessa macchina (embedding, strato nascosto, softmax) serve per entrambi (scheda 40).

<a id="p-4"></a>

### Slide 4 · L'output è una distribuzione, non una parola

Il grafico a barre mostra $P(w\mid\text{context})$ per il contesto *The film was unexpectedly \_\_\_*: *good* 0,28, *moving* 0,21, *funny* 0,14, *dull* 0,11, *boring* 0,10, *terrible* 0,09, *the* circa 0.

- Le sei barre sommano a 0,93: il restante 0,07 è distribuito sulle altre parole del vocabolario. La slide lo dice esplicitamente: ogni probabilità è $\ge 0$ e la somma vale 1 **su tutte le 50.000 voci**, non solo sulle sei mostrate.
- *the* ha probabilità quasi nulla: un articolo dopo un avverbio è sintatticamente improbabile.
- Il contesto non decide il sentiment: *unexpectedly* è compatibile sia con *good* sia con *dull*, e la distribuzione lo riflette.

La stessa forma di risposta (un vettore di probabilità) vale per la parola successiva, la classe di sentiment, la parte del discorso ([L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-5)). Per produrla servirà la **softmax** (scheda 36).

<a id="p-5"></a>

### Slide 5 · Dal testo alla previsione: la pipeline

La lezione segue una pipeline in sei caselle, ciascuna con la sua sezione del libro:

1. **language**: il testo grezzo, *"The film was unexpectedly \_\_\_"*;
2. **rappresentazione numerica, embedding** (cap. 5 e §6.5): ogni token diventa un vettore denso ([L11](L11-embedding-word2vec.md#p-5));
3. **rete neurale** $\mathbf h = g(W\mathbf x + \mathbf b)$ (§6.1-6.3): uno strato nascosto con attivazione non lineare $g$;
4. **logit** $\mathbf z$ (§6.3): punteggi non normalizzati, uno per risposta;
5. **probabilità** $\mathbf p = \mathrm{softmax}(\mathbf z)$ (§6.3);
6. **previsione**, e una **loss** se conosciamo la risposta giusta (§6.6).

Le caselle 4-6 erano già tutte nella regressione logistica multinomiale ([L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-10)); la novità è la casella 3, e la casella 2 diventa parte del modello invece di un insieme di feature scelte a mano. La promessa della slide: alla fine nessuna casella sarà una scatola nera.

<a id="p-6"></a>

### Slide 6 · Obiettivi della lezione

Che cosa si deve saper fare alla fine (utile come checklist per l'orale):

- dire esattamente che cosa calcola un'**unità neurale** (schede 10-13);
- distinguere una mappa **lineare** da una **non lineare** e dire perché servono entrambe (scheda 26);
- spiegare che cosa porta uno **strato nascosto** (XOR, schede 18-25);
- enunciare che cosa garantisce l'**approssimazione universale** e che cosa no (schede 27-28);
- dare la **forma** di ogni tensore in una forward pass (schede 32-33);
- scegliere default sensati per il training: **optimizer, schedule, regolarizzazione** (schede 61-68);
- definire **logit, softmax, cross-entropy** e come si collegano (schede 36-38);
- descrivere gli **embedding** come rappresentazioni apprese (schede 42-43);
- spiegare la **backpropagation** come regola della catena su un grafo (schede 54-57);
- indicare quali pezzi di oggi sono ancora dentro un **LLM** moderno (scheda 70).

<a id="p-7"></a>

### Slide 7 · Il neurone biologico, per curiosità

Slide di contesto (*Historical Notes*), non da esame nei dettagli. A sinistra il **modello di Hodgkin-Huxley** (studi del 1952 sull'assone gigante del calamaro, Nobel 1963): quattro **equazioni differenziali accoppiate**. La prima è il bilancio delle correnti sulla membrana, $C\,du/dt = I - g_K n^4(u-E_K) - g_{Na}m^3h(u-E_{Na}) - g_L(u-E_L)$, con $u$ potenziale di membrana e tre canali (potassio, sodio, perdita); le altre tre descrivono le variabili di apertura $n, m, h$, ciascuna che tende con costante di tempo $\tau(u)$ al suo valore di regime (la slide scrive $n_0(u)$ nella seconda riga e, più sbrigativamente, $m(u)$ e $h(u)$ nelle ultime due: sono anch'essi valori di regime).

Il messaggio:

- questo descrive **una sola cellula**, ed è ancora una semplificazione;
- l'unità artificiale ha solo una **somma pesata** e una **non linearità scalare**: il divario è enorme e voluto;
- ciò che si eredita davvero dalle neuroscienze è l'idea di **rappresentazione distribuita** (un concetto codificato da molte unità, ogni unità che partecipa a molti concetti), non il realismo dei circuiti.

<a id="p-8"></a>

### Slide 8 · Ispirazione biologica, non simulazione

Due colonne:

- **Da dove viene il nome**: **McCulloch e Pitts (1943)**, un modello volutamente semplificato del neurone come elemento logico (il libro: descrivibile in logica proposizionale). Sono astrazioni, non repliche.
- **Che cosa si studia davvero**: una **funzione parametrizzata** $f(\mathbf x;\theta)$ che si può **derivare** e **adattare ai dati**. Si giudica da ciò che predice, non da quanto somiglia a un cervello.

Dalla biologia viene solo il **vocabolario**: *unit*, *activation*, *network*. Il punto di vista della lezione (e la prima delle "cinque idee" della scheda 71): una rete neurale è una funzione parametrizzata e differenziabile, niente di più e niente di meno. È lo stesso punto di vista della regressione logistica ([L6](L06-regressione-logistica.md#p-36)): scegli una famiglia di funzioni, una loss, e cerchi i parametri con la discesa del gradiente. Differenziabile è la parola chiave: è ciò che permette di usare il gradiente per l'apprendimento.

## L'unità neurale

<a id="p-9"></a>
**Slide 9 · L'unità neurale** — Prima sezione (§6.1): un'unità è una somma pesata seguita da una non linearità.

<a id="p-10"></a>

### Slide 10 · Un'unità calcola una somma pesata degli input

Il diagramma: tre input $x_1, x_2, x_3$ entrano con pesi $w_1, w_2, w_3$ in un nodo $\Sigma$; un quarto input costante **+1** entra con peso $b$. L'uscita del nodo è

$$z = b + \sum_i w_i x_i = \mathbf w\cdot\mathbf x + b$$

- $\mathbf x$: il vettore di input, i **dati**;
- $\mathbf w, b$: **pesi** e **bias**, i **parametri** da imparare;
- $z$: la **pre-attivazione**, un solo numero reale.

È esattamente il punteggio della regressione logistica ([scheda 20 della L6](L06-regressione-logistica.md#p-20)). Il disegno del bias come peso di un input fissato a +1 è un trucco di notazione che il libro usa spesso (Fig. 6.9): aggiungendo $x_0 = 1$ al vettore, il bias diventa un peso come gli altri e si può scrivere $z = \mathbf w\cdot\mathbf x$. Geometricamente $z = 0$ è un **iperpiano**; $z$ misura (a meno di un fattore $\|\mathbf w\|$) la distanza con segno dell'input da quell'iperpiano.

<a id="p-11"></a>

### Slide 11 · Poi una non linearità

Dopo la somma, l'unità applica una funzione **non lineare** $f$: l'output è l'**attivazione** $a = f(z)$. Con la sigmoide:

$$y = \sigma(\mathbf w\cdot\mathbf x + b) = \frac{1}{1+e^{-(\mathbf w\cdot\mathbf x + b)}}$$

- $f$ si applica **elemento per elemento**: su un vettore $\mathbf z$ di pre-attivazioni (uno strato di unità) $f(\mathbf z) = [f(z_1), f(z_2), \dots]$;
- con la sigmoide l'output sta in $(0,1)$ e si legge come una **probabilità** ([sigmoide nella L6](L06-regressione-logistica.md#p-22));
- per un'unità isolata $a$ e $y$ coincidono; in una rete più profonda il libro riserva $y$ all'output finale e $a$ all'attivazione di ogni nodo.

Una singola unità sigmoide **è** una regressione logistica binaria. La frase in fondo anticipa il punto centrale della lezione: è l'attivazione $f$ che impedisce a una rete profonda di **collassare in una sola mappa lineare** (scheda 26).

<a id="p-12"></a>

### Slide 12 · Leggere i parametri

La tabella dà un'interpretazione di ogni parametro in un'unità che rileva il sentiment positivo:

| parametro | effetto | esempio |
| --- | --- | --- |
| $w_i$ grande e positivo | la feature $i$ spinge forte l'output in su | *superb* |
| $w_i$ negativo | la feature spinge in giù | *painfully* |
| $w_i \approx 0$ | la feature è ignorata | *the* |
| $b$ grande e positivo | l'unità si attiva salvo prove contrarie | un prior di classe |

La domanda: **che cosa calcola l'unità se tutti i pesi sono zero?** Allora $z = b$ per ogni input e l'unità produce la **costante $f(b)$**. Cambiando solo $b$ si sposta questa costante ma l'unità resta sorda all'input. Il bias fissa il **default**, i pesi la fanno **ascoltare**. È la stessa lettura di pesi e bias della [scheda 21 della L6](L06-regressione-logistica.md#p-21).

Attenzione all'interpretazione: vale bene per un'unità che legge feature con un significato; per le unità nascoste di una rete (che leggono altre unità o dimensioni di embedding) i pesi raramente sono leggibili uno per uno.

<a id="p-13"></a>

### Slide 13 · Un'unità a mano

L'esempio del libro (§6.1, p. 153): $\mathbf w = [0{,}2;\ 0{,}3;\ 0{,}9]$, $b = 0{,}5$, $\mathbf x = [0{,}5;\ 0{,}6;\ 0{,}1]$.

$$z = 0{,}5\cdot0{,}2 + 0{,}6\cdot0{,}3 + 0{,}1\cdot0{,}9 + 0{,}5 = 0{,}10 + 0{,}18 + 0{,}09 + 0{,}5 = 0{,}87$$
$$y = \sigma(0{,}87) = \frac{1}{1+e^{-0{,}87}} = \frac{1}{1+0{,}419} = 0{,}70$$

Verificato: $\sigma(0{,}87) = 0{,}7047$. Il grafico a destra è la sigmoide con la soglia di decisione a $z = 0$ ($\sigma = 0{,}5$). La domanda "*sopra o sotto 0,5?*" ha una risposta immediata senza calcolare l'esponenziale: basta il **segno di $z$**. $z > 0$ significa $\sigma(z) > 0{,}5$ ([soglia nella L6](L06-regressione-logistica.md#p-25)).

> **Da saper fare: Saper calcolare un'unità**
>
> Prodotto scalare, più bias, poi l'attivazione. Con gli stessi numeri: tanh$(0{,}87) = 0{,}70$, ReLU$(0{,}87) = 0{,}87$. Per $\mathbf x = [-1, -2, -1]$: $z = -0{,}2-0{,}6-0{,}9+0{,}5 = -1{,}2$, $\sigma = 0{,}23$, tanh $= -0{,}83$, ReLU $= 0$ (esercizio 1). Valori da ricordare: $\sigma(0) = 0{,}5$, $\sigma(1) = 0{,}73$, $\sigma(2) = 0{,}88$.

<a id="p-14"></a>

### Slide 14 · Funzioni di attivazione: due mestieri diversi

La tabella separa le attivazioni **di output** da quelle **nascoste**:

| funzione | codominio | ruolo |
| --- | --- | --- |
| sigmoide $\sigma(z)$ | $(0,1)$ | output: probabilità di una classe binaria |
| softmax | simplesso: valori $\ge 0$ che sommano a 1 | output: distribuzione su $K$ classi |
| ReLU $\max(z,0)$ | $[0,\infty)$ | nascosta: il default standard |
| tanh | $(-1,1)$ | nascosta: storicamente importante, ancora nelle RNN |
| GELU | liscia, simile a ReLU | nascosta: comune negli MLP dei transformer |

La sigmoide **non** è più l'attivazione nascosta di default: sopravvive all'output, dove $(0,1)$ significa probabilità, e come **gate** dentro alcuni strati. Regola pratica: l'attivazione di **output** si sceglie dal **compito** (binario, $K$ classi, regressione), quella **nascosta** da **ciò che si addestra bene**. La nota in fondo: nei transformer softmax e sigmoide compaiono anche dentro gli strati, come pesi (attention) e gate (MLP gated), non come attivazioni nascoste (cap. 7).

<a id="p-15"></a>

### Slide 15 · Un catalogo di funzioni di attivazione

Una tabella presa da Wikipedia (*Activation function*), da non imparare a memoria: per ogni funzione il grafico, la formula, la derivata, il codominio e l'ordine di continuità. Si riconoscono quelle della lezione: identità, gradino (*binary step*, quella del perceptron), sigmoide con derivata $g(x)(1-g(x))$, tanh con derivata $1-g(x)^2$, ReLU con derivata 0 o 1, GELU $x\,\Phi(x)$ con codominio $(-0{,}17\dots, \infty)$. Poi le varianti nate per correggere difetti della ReLU: **leaky ReLU** e **PReLU** (pendenza piccola invece di zero per $x<0$, così il gradiente non si annulla), **ELU**, **SELU**, **SiLU/Swish** $x\,\sigma(x)$, softplus $\ln(1+e^x)$ (una ReLU liscia), e funzioni più esotiche (gaussiana, sinusoide).

Il messaggio: c'è un'enorme varietà, ma i requisiti sono pochi: **non linearità**, una **derivata** utilizzabile quasi ovunque, **costo** basso. La colonna della derivata non è un dettaglio: è ciò che entra nella backpropagation (scheda 57).

<a id="p-16"></a>

### Slide 16 · Le tre che si incontrano più spesso

Tre grafici sullo stesso asse $z\in[-6,6]$:

- **sigmoide**: le zone rosa ai lati ($|z|$ oltre circa 3) sono marcate *saturated, gradient ≈ 0*. Lì la curva è piatta: $\sigma'(z) = \sigma(z)(1-\sigma(z))$ vale al massimo $1/4$ (in $z=0$) e già $\sigma'(3{,}2) \approx 0{,}04$, $\sigma'(6) \approx 0{,}0025$;
- **tanh**: stessa forma a S, centrata in 0, codominio $(-1,1)$; satura anch'essa;
- **ReLU** (blu) e **GELU** (tratteggio arancio): ReLU è 0 per $z<0$ e l'identità per $z>0$; GELU è quasi uguale ma liscia, con un piccolo avvallamento negativo (minimo $\approx -0{,}17$ intorno a $z \approx -0{,}75$).

Perché ReLU: è **economica**, **non satura** per $z>0$ (derivata 1) e lascia passare i gradienti più facilmente. Il libro chiama il problema **vanishing gradient**: la backpropagation moltiplica le derivate strato per strato, e fattori quasi nulli fanno svanire il segnale. ReLU non lo elimina del tutto (per $z<0$ la derivata è 0: un'unità sempre spenta smette di imparare, la cosiddetta *dying ReLU*, esercizio 10d).

> **Da saper fare: Il limite 1/4 della sigmoide (esercizio 1d)**
>
> $\sigma'(z) = \sigma(1-\sigma) \le 1/4$ perché $p(1-p)$ è massimo in $p = 1/2$. Dieci unità sigmoide in catena: il prodotto delle derivate è al più $(1/4)^{10} \approx 9{,}5\cdot10^{-7}$. Con unità saturate ($z = 6$, $\sigma' = 0{,}0025$) il segnale svanisce ancora più in fretta. Con ReLU attive il fattore è 1.

## Strati nascosti e XOR

<a id="p-17"></a>
**Slide 17 · Perché servono gli strati nascosti** — Seconda sezione (§6.2-6.3): representation learning raccontato attraverso lo XOR.

<a id="p-18"></a>

### Slide 18 · Un'unità sola è un classificatore lineare

La frontiera di decisione di un'unità con due input è l'insieme dei punti con $z = 0$:

$$w_1x_1 + w_2x_2 + b = 0 \quad\Longleftrightarrow\quad x_2 = -\frac{w_1}{w_2}x_1 - \frac{b}{w_2}$$

- in due dimensioni è una **retta** (pendenza $-w_1/w_2$, intercetta $-b/w_2$); in $d$ dimensioni un **iperpiano**;
- da un lato la classe 0, dall'altro la classe 1;
- cambiando i parametri la retta si sposta e ruota, ma **resta una retta**.

A destra la tabella di verità di XOR (1 solo se gli input sono diversi) e i quattro punti nel piano: pieni (output 1) in $(0,1)$ e $(1,0)$, vuoti in $(0,0)$ e $(1,1)$, cioè sulle due diagonali opposte. Il titolo del grafico, *try one straight line*, è una sfida che non si può vincere (scheda 19).

Con attivazione a **gradino** (1 se $z>0$, 0 altrimenti, Eq. 6.7) l'unità è il **perceptron** di Rosenblatt (1958); con la sigmoide è la **regressione logistica**. In entrambi i casi la frontiera è lineare: la sigmoide cambia solo quanto è "morbida" la decisione vicino alla retta ([L6](L06-regressione-logistica.md#p-25)).

<a id="p-19"></a>

### Slide 19 · AND e OR sono separabili, XOR no

Tre pannelli (la Fig. 6.5 del libro), con pieni = output 1 e vuoti = 0:

- **AND**: solo $(1,1)$ è pieno; una retta tratteggiata con pendenza negativa lo separa dagli altri tre (etichettata con l'equazione $x_2 = (-w_1/w_2)x_1 + (-b/w_2)$). Pesi possibili: $w_1 = w_2 = 1$, $b = -1{,}5$.
- **OR**: solo $(0,0)$ è vuoto; una retta vicina all'origine lo isola. Pesi: $w_1 = w_2 = 1$, $b = -0{,}5$.
- **XOR**: i pieni sono su una diagonale, i vuoti sull'altra; un punto interrogativo rosso al centro. **Nessuna retta** li separa: XOR non è **linearmente separabile**.

> **Da saper fare: Dimostrare che XOR non è separabile (esercizio 2c)**
>
> Con output 1 se $z > 0$, le quattro condizioni sono: $(0,0)\to0$: $b \le 0$; $(1,1)\to0$: $w_1+w_2+b \le 0$; $(0,1)\to1$: $w_2+b > 0$; $(1,0)\to1$: $w_1+b > 0$. Sommando le ultime due: $w_1+w_2+2b > 0$. Sommando le prime due: $w_1+w_2+2b \le 0$. Contraddizione: nessuna terna $(w_1,w_2,b)$ funziona. Il libro usa per AND $b=-1$ e per OR $b=0$ con la convenzione "0 se $z\le0$": coerente con questa.

<a id="p-20"></a>

### Slide 20 · Nota storica: da uno strato a molti

Tre date in sequenza:

- **1958, Rosenblatt**: il **perceptron**, uno strato di pesi e una regola per impararli dagli esempi;
- **1969, Minsky e Papert** (*Perceptrons*): la dimostrazione che uno **strato singolo** calcola solo funzioni **linearmente separabili**, quindi non XOR. Il libro ricorda che dopo questo risultato il campo declinò per una ventina d'anni;
- **1974 e 1986, Werbos; Rumelhart, Hinton e Williams**: la **backpropagation**, i gradienti per ogni strato, così anche gli strati nascosti si possono imparare.

La frase chiave: **uno strato nascosto basta** per calcolare XOR (lo si sapeva già); ciò che mancava era un modo **pratico di addestrarlo**. Per una rete a uno strato il gradiente si scrive direttamente ([L6](L06-regressione-logistica.md#p-45)); per i pesi degli strati nascosti, che non toccano direttamente la loss, serve la regola della catena applicata sistematicamente (schede 54-57).

<a id="p-21"></a>

### Slide 21 · XOR con uno strato nascosto

La rete della Fig. 6.6 (da Goodfellow et al. 2016), tutta con ReLU:

$$\mathbf h = \mathrm{ReLU}(W\mathbf x + \mathbf b),\quad W = \begin{bmatrix}1&1\\1&1\end{bmatrix},\ \mathbf b = \begin{bmatrix}0\\-1\end{bmatrix}$$
$$y = \mathrm{ReLU}(\mathbf u\cdot\mathbf h + c),\quad \mathbf u = [1, -2],\ c = 0$$

Nel disegno: due input $x_1, x_2$ in basso, due unità nascoste $h_1, h_2$ al centro, l'output $y$ in alto. Ogni input è collegato a entrambe le unità nascoste con peso 1; i bias (grigi, come pesi di un nodo costante +1) sono 0 per $h_1$ e $-1$ per $h_2$; i pesi verso $y$ sono $+1$ da $h_1$ e $-2$ da $h_2$, con bias 0.

Le due unità nascoste hanno gli stessi pesi e differiscono solo per il bias: $h_1 = \mathrm{ReLU}(x_1+x_2)$ conta quanti input sono accesi, $h_2 = \mathrm{ReLU}(x_1+x_2-1)$ si accende solo se lo sono **entrambi** (è un AND). L'output fa "quanti sono accesi, meno due volte se lo sono entrambi": esattamente XOR. Qui i pesi sono dati; in pratica li si impara.

<a id="p-22"></a>

### Slide 22 · Forward pass dello XOR: x = [1, 1]

Dal basso verso l'alto, con i valori scritti nei nodi del disegno:

- $h_1 = \mathrm{ReLU}(1\cdot1 + 1\cdot1 + 0) = \mathrm{ReLU}(2) = 2$;
- $h_2 = \mathrm{ReLU}(1\cdot1 + 1\cdot1 - 1) = \mathrm{ReLU}(1) = 1$;
- $y = \mathrm{ReLU}(1\cdot2 - 2\cdot1 + 0) = \mathrm{ReLU}(0) = 0$.

$y = 0 = \mathrm{XOR}(1,1)$, corretto (la riga evidenziata della tabella di verità). Lo strato nascosto manda $[1,1]$ in $\mathbf h = [2,1]$, e l'unità di output, con il peso $-2$ su $h_2$, lo cancella esattamente a zero. Per $[0,0]$ (non in slide, ma nel libro): $W\mathbf x + \mathbf b = [0,-1]$, $\mathbf h = [0,0]$, $y = 0$.

<a id="p-23"></a>

### Slide 23 · Forward pass dello XOR: x = [0, 1]

- $h_1 = \mathrm{ReLU}(1\cdot0 + 1\cdot1 + 0) = 1$;
- $h_2 = \mathrm{ReLU}(1\cdot0 + 1\cdot1 - 1) = \mathrm{ReLU}(0) = 0$;
- $y = \mathrm{ReLU}(1\cdot1 - 2\cdot0 + 0) = 1$.

$y = 1 = \mathrm{XOR}(0,1)$, corretto. Per simmetria $[1,0]$ dà gli stessi $\mathbf h = [1,0]$ e $y = 1$: **i due input diversi finiscono nello stesso punto nascosto**. Lo strato nascosto li ha fusi.

> **Da saper fare: Tabella completa (esercizio 3a)**
>
> | $\mathbf x$ | $W\mathbf x+\mathbf b$ | $\mathbf h$ | $\mathbf u\cdot\mathbf h$ | $y$ |
> | --- | --- | --- | --- | --- |
> | [0,0] | [0,−1] | [0,0] | 0 | 0 |
> | [0,1] | [1,0] | [1,0] | 1 | 1 |
> | [1,0] | [1,0] | [1,0] | 1 | 1 |
> | [1,1] | [2,1] | [2,1] | 0 | 0 |
>
> Verificato in numpy. Saperla rifare in due minuti è un classico.

<a id="p-24"></a>

### Slide 24 · Lo strato nascosto cambia la domanda

Due pannelli affiancati (la Fig. 6.7 del libro):

- **a) spazio di input $\mathbf x$**: i quattro punti dello XOR, pieni sulle diagonali opposte, non separabili;
- **b) spazio appreso $\mathbf h$**: $(0,0)\to(0,0)$ vuoto, $(0,1)$ e $(1,0)\to(1,0)$ pieno (la freccia verde: *collapse to h = [1,0]*), $(1,1)\to(2,1)$ vuoto. Una retta tratteggiata rossa ora separa il punto pieno dai due vuoti.

Due input che chiedevano risposte diverse alla stessa retta vengono **fusi in un punto**, e il problema che resta è **lineare**. In questo spazio l'unità di output è un classificatore lineare qualunque: con i pesi dati, $\mathbf u\cdot\mathbf h = h_1 - 2h_2$ vale 0, 1, 0 sui tre punti, e una frontiera come $h_1 - 2h_2 = 0{,}5$ li separa.

È la stessa idea del **representation learning** già nominato nella [scheda 30 della L6](L06-regressione-logistica.md#p-30): invece di cercare una frontiera curva nello spazio originale, la rete impara una **trasformazione dello spazio** in cui basta una frontiera lineare.

> **Da saper fare: Esercizio 3b-c**
>
> (b) Retta separatrice nello spazio $\mathbf h$: $h_1 - 2h_2 = 0{,}5$ (positivi sotto, negativi sopra). (c) Togliendo la ReLU nascosta, $\mathbf h = W\mathbf x + \mathbf b$ e $\mathbf u\cdot\mathbf h = (x_1+x_2) - 2(x_1+x_2-1) = 2 - x_1 - x_2$: gli output sono 2, 1, 1, 0. La rete calcola una funzione **lineare** della somma degli input, non XOR: per $[0,0]$ dà 2 invece di 0. Senza non linearità lo strato nascosto non può fondere i due punti.

<a id="p-25"></a>

### Slide 25 · Gli strati nascosti imparano rappresentazioni

Slide-slogan, da sapere a memoria: **gli strati nascosti sono utili perché imparano rappresentazioni che rendono il compito facile**. Nello XOR "facile" vuol dire linearmente separabile; in generale vuol dire che l'ultimo strato (una regressione logistica) può fare bene il suo lavoro sulle feature che gli strati precedenti hanno costruito.

La riga sotto annuncia che è l'idea che ritornerà in tutto il resto del corso: negli **embedding** (già visti: word2vec impara vettori in cui la similarità diventa un prodotto scalare, [L11](L11-embedding-word2vec.md#p-14)), nelle **RNN**, nell'**attention**, in ogni strato di un **transformer**. Il libro (§6.2.1) lo dice così: possiamo vedere lo strato nascosto come la formazione di una rappresentazione dell'input, e questa capacità di imparare automaticamente rappresentazioni utili è uno dei vantaggi chiave delle reti neurali.

<a id="p-26"></a>

### Slide 26 · Perché la non linearità non è opzionale

Due strati **lineari** (senza attivazione) uno sopra l'altro (Eq. 6.14):

$$\mathbf z^{[2]} = W^{[2]}(W^{[1]}\mathbf x + \mathbf b^{[1]}) + \mathbf b^{[2]} = \underbrace{(W^{[2]}W^{[1]})}_{W'}\mathbf x + \underbrace{(W^{[2]}\mathbf b^{[1]} + \mathbf b^{[2]})}_{\mathbf b'} = W'\mathbf x + \mathbf b'$$

- una mappa lineare (affine) composta con un'altra è ancora una mappa lineare;
- quindi una rete di 10 strati **puramente lineari** ha esattamente il potere rappresentativo di **uno** strato, solo con più parametri;
- è l'attivazione $f$ che rende la composizione davvero più ricca;
- è anche ciò che rende la loss **non convessa**, ed è il prezzo da pagare ([convessità nella L6](L06-regressione-logistica.md#p-42)).

Il riquadro: *senza una non linearità fra gli strati, la profondità non compra niente*. L'esercizio 3c lo mostra sullo XOR: togliendo la ReLU nascosta la rete diventa la funzione lineare $2 - x_1 - x_2$.

> **Da saper fare: Esercizio 4: tre strati lineari**
>
> $W' = W^{[3]}W^{[2]}W^{[1]}$, $\mathbf b' = W^{[3]}W^{[2]}\mathbf b^{[1]} + W^{[3]}\mathbf b^{[2]} + \mathbf b^{[3]}$. Con 4 input, due strati di 100 e 3 output: $4\cdot100+100 + 100\cdot100+100 + 100\cdot3+3 = 10.903$ parametri contro $4\cdot3+3 = 15$ dello strato unico equivalente. Mai più espressiva; può essere **meno** espressiva: con uno strato nascosto di 1 unità $W'$ ha rango al più 1 e non può rappresentare una mappa $\mathbb R^4\to\mathbb R^3$ qualsiasi.

<a id="p-27"></a>

### Slide 27 · Quanto è espressivo uno strato nascosto?

**Teorema di approssimazione universale** (Hornik et al., 1989): per ogni funzione continua $f$ su un compatto $K\subset\mathbb R^d$ e ogni $\varepsilon > 0$ esiste una rete con **un solo strato nascosto** di $N$ unità tale che

$$\sup_{\mathbf x\in K}\Big|f(\mathbf x) - \sum_{j=1}^N u_j\,\sigma(\mathbf w_j\cdot\mathbf x + b_j)\Big| < \varepsilon$$

In parole: una combinazione lineare di $N$ unità nascoste approssima $f$ uniformemente (errore massimo, non medio) quanto si vuole. I tre grafici mostrano una curva grigia ondulata in una dimensione approssimata (in verde) da reti con **4, 10 e 40 ReLU** nascoste: la curva verde è una spezzata con un nodo per unità, e l'errore massimo indicato scende da 0,37 a 0,16 a 0,01. Con 40 unità la spezzata è indistinguibile dalla curva.

Perché funziona con le ReLU: ogni unità $u_j\,\mathrm{ReLU}(x - k_j)$ aggiunge un "gomito" in $k_j$ e cambia la pendenza di $u_j$; con abbastanza gomiti si insegue qualunque curva continua. La domanda vera non è *se* ma **quante unità** servono.

> **Da saper fare: Esercizio 5: x² con le ReLU**
>
> $g(x) = \mathrm{ReLU}(x) + 2\,\mathrm{ReLU}(x-1)$ vale 0, 1, 4 in 0, 1, 2 come $x^2$; in 0,5 e 1,5 vale 0,5 e 2,5 contro 0,25 e 2,25: errore 0,25. Con nodi in 0; 0,5; 1; 1,5 e pesi 0,5; 1; 1; 1 (le pendenze dei tratti sono 0,5; 1,5; 2,5; 3,5) l'errore massimo è $h^2/4 = 0{,}0625$. Per errore $\le 0{,}01$ serve $h \le 0{,}2$: **10 unità** (verificato numericamente: errore massimo 0,0100).

<a id="p-28"></a>

### Slide 28 · Che cosa l'approssimazione universale non dice

Due colonne:

- **Garantisce l'esistenza**: esistono pesi che approssimano $f$ bene quanto si vuole; bastano uno strato nascosto e una non linearità; senza non linearità nessuna approssimazione (si resta lineari, scheda 26).
- **Non dice quante, come trovarle, quanto bene**:
  - $N$ può crescere **esponenzialmente** con la dimensione dell'input;
  - niente su come **trovare** i pesi (l'ottimizzazione non convessa può non arrivarci);
  - niente sulla **generalizzazione** da dati finiti (approssimare $f$ non è impararla da 1400 esempi);
  - universale non vuol dire facile da imparare: **l'architettura è un prior**.

**Perché la profondità?** Comporre strati costruisce feature fatte di feature: certe funzioni richiedono esponenzialmente molte unità in uno strato solo ma poche se distribuite su più strati. Conclusione: l'espressività è **necessaria, non sufficiente**; profondità, dati e ottimizzazione fanno il resto.

> **Da saper fare: L'esponenziale in concreto (esercizio 5d)**
>
> L'interpolazione a griglia dell'esercizio 5 in $[0,2]^d$ con passo $h = 0{,}2$ ha 10 celle per dimensione, quindi $10^d$ celle: per $d = 10$ sono $10^{10}$ pezzi. Il teorema garantisce che una rete esista, ma una costruzione così ingenua è inutilizzabile già con 10 input (e un embedding ne ha 300).

> **Approfondimento: Quali attivazioni vanno bene**
>
> Facoltativo. Hornik et al. (1989) dimostrano il teorema per funzioni "a schiacciamento" come la sigmoide, quella nella formula della slide; Leshno et al. (1993) lo estendono a ogni attivazione continua **non polinomiale**, ReLU compresa (quella dei grafici). Un'attivazione polinomiale di grado fisso non basta: la rete resterebbe un polinomio di quel grado.

## Reti feedforward

<a id="p-29"></a>
**Slide 29 · Reti feedforward** — Terza sezione (§6.3): strati, matrici, forme dei tensori, logit, softmax e cross-entropy.

<a id="p-30"></a>

### Slide 30 · La rete feedforward

Il disegno (Fig. 6.8): 4 unità di **input** $\mathbf x$ (blu), 5 unità **nascoste** $\mathbf h$ (verde), 3 unità di **output** $\mathbf y$ (arancio). Ogni unità è collegata a tutte quelle dello strato precedente: i pesi fra input e nascosto formano la matrice $W$, quelli fra nascosto e output la matrice $U$.

- lo strato nascosto $\mathbf h$ è la **rappresentazione** che la rete si costruisce dell'input;
- lo strato di output trasforma quella rappresentazione in una risposta;
- **convenzione di conteggio**: questa è una rete a **2 strati**, perché l'input non si conta (si contano gli strati con pesi). Con la stessa convenzione la regressione logistica è una rete a 1 strato;
- **nessun ciclo**: l'informazione va solo in avanti (*feedforward*). Le reti con cicli, le **reti ricorrenti**, arrivano nel cap. 14.

Due termini dal libro: **fully connected** (ogni coppia di unità di strati adiacenti ha un peso) e **MLP** (*multi-layer perceptron*), nome storico improprio perché le unità moderne non hanno l'attivazione a gradino del perceptron.

<a id="p-31"></a>

### Slide 31 · La forward pass in tre righe

Tutta l'inferenza di un classificatore a 2 strati (Eq. 6.12):

$$\mathbf h = g(W\mathbf x + \mathbf b)\qquad \mathbf z = U\mathbf h\qquad \mathbf y = \mathrm{softmax}(\mathbf z)$$

- $g$ è l'attivazione nascosta: da leggere come **ReLU** salvo diverso avviso (il libro scrive spesso $\sigma$ per indicare un'attivazione qualsiasi);
- $\mathbf z$ sono i **logit**: punteggi non normalizzati, uno per classe ([logit nella L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-8));
- la softmax li trasforma in una distribuzione;
- alcuni modelli tolgono il bias di output, come qui ($\mathbf z = U\mathbf h$ senza $+\mathbf c$): concettualmente non cambia nulla.

Lettura utile dal libro: le ultime due righe sono una **regressione logistica multinomiale** ([L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-11)) applicata non alle feature $\mathbf x$ ma a $\mathbf h$, feature che la rete costruisce da sola. Notazione: qui $\mathbf x$ è un **vettore colonna** (un esempio), come nel libro; in codice si elabora un batch intero, con le righe come esempi, e lo stesso $W$ compare come $XW^\top$ (scheda 33).

<a id="p-32"></a>

### Slide 32 · Chiedersi sempre: che forma ha?

| oggetto | forma | che cos'è |
| --- | --- | --- |
| $\mathbf x$ | $d$ | un input: feature o un embedding aggregato (pooled) |
| $W$ | $d_h\times d$ | pesi nascosti: la riga $j$ sono i $d$ pesi dell'unità $j$ |
| $\mathbf b$ | $d_h$ | bias nascosti, uno per unità |
| $\mathbf h$ | $d_h$ | rappresentazione nascosta |
| $U$ | $K\times d_h$ | pesi di output: la riga $k$ sono i pesi della classe $k$ |
| $\mathbf z, \mathbf y$ | $K$ | logit e probabilità |

Regola per ricostruire le forme: una matrice dei pesi è sempre **(uscite × entrate)** in questa notazione, perché moltiplica un vettore colonna a destra. Così $W\mathbf x$ ha forma $(d_h\times d)(d) = d_h$, $U\mathbf h$ ha forma $(K\times d_h)(d_h) = K$. Il numero di parametri segue subito: $d_h d + d_h + K d_h$ (più $K$ se c'è un bias di output). La riga $k$ di $U$ fa da "prototipo" della classe $k$, come le righe di $W$ nella [scheda 12 della L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-12). Abitudine che, dice la slide, farà risparmiare ore: in attention, nei transformer, in ogni stack trace di PyTorch.

<a id="p-33"></a>

### Slide 33 · In pratica: un batch intero

Sulla carta un esempio alla volta, $\mathbf h = g(W\mathbf x + \mathbf b)$. In codice un batch di $m$ esempi, **uno per riga** di $X$ (Eq. 6.20):

$$H = g(XW^\top + \mathbf b)\qquad Z = HU^\top\qquad \hat Y = \mathrm{softmax}(Z)$$

|  | un esempio | batch di $m$ |
| --- | --- | --- |
| $\mathbf x\to X$ | $d$ | $m\times d$ |
| $\mathbf h\to H$ | $d_h$ | $m\times d_h$ |
| $\mathbf z\to Z$ | $K$ | $m\times K$ |
| $W$ | $d_h\times d$ | $d_h\times d$ (invariata) |
| $\mathbf b$ | $d_h$ | $d_h$, sommato a ogni riga (broadcast) |

Cambia solo l'ordine del prodotto: i parametri sono gli stessi. È esattamente `torch.nn.Linear`, che memorizza $W$ come (out × in) e restituisce $XW^\top + \mathbf b$. La softmax si applica **riga per riga**. La domanda: batch di 64 recensioni, $d = 300$, $d_h = 128$, $K = 3$, forma di $Z$? **64 × 3**, una riga di logit per recensione.

Nota in fondo alla slide: l'Eq. 6.22 del libro scrive invece $\mathbf xW + \mathbf b$ con $W$ di forma $d\times d_h$ (Fig. 6.13). Stessa rete, matrice trasposta: per questo bisogna sempre controllare le forme.

> **Da saper fare: Esercizio 6a**
>
> $X$: 64×300; $W^{[1]}$: 128×300; $\mathbf b^{[1]}$: 128; $H$: 64×128; $W^{[2]}$: 3×128; $Z$: 64×3. Parametri: $128\cdot300 + 128 + 3\cdot128 + 3 = 38.915$ (38.912 senza bias di output). Il batch non cambia il numero di parametri.

<a id="p-34"></a>

### Slide 34 · Notazione per reti più profonde

Con più strati si numera con l'apice fra parentesi quadre, con $\mathbf x = \mathbf a^{[0]}$ (Eq. 6.13):

$$\mathbf z^{[\ell]} = W^{[\ell]}\mathbf a^{[\ell-1]} + \mathbf b^{[\ell]}\qquad \mathbf a^{[\ell]} = g^{[\ell]}(\mathbf z^{[\ell]})$$

e la forward pass è un ciclo: per $\ell = 1,\dots,n$ si applicano le due righe, e $\hat{\mathbf y} = \mathbf a^{[n]}$.

- una regola applicata $n$ volte: è tutto ciò che significa "**profondità**";
- $g^{[\ell]}$ è di solito ReLU dentro e softmax alla fine;
- simboli fissi: $\mathbf z$ è sempre una **pre-attivazione**, $\mathbf a$ o $\mathbf h$ sempre un'**attivazione**, $\mathbf p$ sempre **probabilità**. Il libro chiama **logit** la $\mathbf z^{[n]}$ dell'ultimo strato.

Questa notazione serve soprattutto nella backpropagation, dove bisogna distinguere $\partial L/\partial\mathbf z^{[\ell]}$ da $\partial L/\partial\mathbf a^{[\ell]}$ (esercizio 10).

<a id="p-35"></a>

### Slide 35 · La regressione logistica è una rete a uno strato

Due colonne:

- **binaria**: $y = \sigma(\mathbf w\cdot\mathbf x + b)$. Un'unità di output con sigmoide, output la probabilità della classe positiva, **zero** strati nascosti ([L6](L06-regressione-logistica.md#p-23));
- **multiclasse**: $\mathbf p = \mathrm{softmax}(W\mathbf x + \mathbf b)$. $K$ unità di output con softmax, una distribuzione su $K$ classi, ancora zero strati nascosti ([L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-14)).

Il riquadro: aggiungere uno strato nascosto alla regressione logistica permette al modello di usare **interazioni non lineari fra le feature**, che possono aiutare in certi compiti. Esempio linguistico: nella regressione logistica la feature "contiene *not*" e la feature "contiene *good*" contribuiscono ognuna con il proprio peso, sommandosi; non c'è modo di dire "*good* vale positivo, ma negativo se c'è anche *not*" (è uno XOR in miniatura). Un'unità nascosta che si accende solo quando entrambe sono presenti (come $h_2$ della scheda 21) lo permette. Le reti neurali sono una **generalizzazione** di un modello già noto, non una specie diversa.

<a id="p-36"></a>

### Slide 36 · La softmax trasforma punteggi in una distribuzione

$$p_i = \mathrm{softmax}(\mathbf z)_i = \frac{e^{z_i}}{\sum_{j=1}^K e^{z_j}}$$

Due grafici: a sinistra i **logit** (barre arancio, qualunque numero reale) per *good, moving, funny, boring, terrible*, all'incirca 2,6; 1,9; 0,8; −0,4; −1,3; a destra le **probabilità** (barre verdi, somma 1): 0,58; 0,29; 0,10; 0,03; 0,01. Ricalcolando con i logit letti dal grafico si ottiene 0,577; 0,287; 0,095; 0,029; 0,012: tornano.

- l'esponenziale rende tutto **positivo**, la divisione per il totale fa **sommare a 1**;
- l'ordine dei logit si conserva, ma le differenze si amplificano: la softmax è **peaky**. Uno scarto di 2 nei logit diventa un rapporto di $e^2 \approx 7{,}4$ nelle probabilità ($p_i/p_j = e^{z_i - z_j}$). Qui *good* e *funny* distano 1,8 e il rapporto è $0{,}58/0{,}10 \approx 6$.

È la softmax della [scheda 7 della L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-7). Esempio del libro (Eq. 6.10-6.11): $\mathbf z = [0{,}6;\ 1{,}1;\ -1{,}5;\ 1{,}2;\ 3{,}2;\ -1{,}1]$ dà $[0{,}055;\ 0{,}090;\ 0{,}0067;\ 0{,}10;\ 0{,}74;\ 0{,}010]$ (verificato). Nei titoli dei grafici i logit sono scritti $\mathbf z = W\mathbf h + \mathbf b$: è la matrice di output che nella scheda 31 si chiamava $U$.

<a id="p-37"></a>

### Slide 37 · Dalla rappresentazione nascosta alla loss

Quattro caselle in colonna: rappresentazione nascosta $\mathbf h$ → logit $\mathbf z = W\mathbf h + \mathbf b$ (qualunque reale) → probabilità $\mathbf p = \mathrm{softmax}(\mathbf z)$ ($\ge 0$, somma 1) → loss $L = -\log p_y$ (un numero).

- un logit può essere **negativo** o **maggiore di 1**: non è una probabilità;
- contano solo le **differenze** fra i logit: $\mathrm{softmax}(\mathbf z) = \mathrm{softmax}(\mathbf z - c)$ per ogni costante $c$, perché $e^{z_i - c}/\sum_j e^{z_j - c}$ ha $e^{-c}$ sopra e sotto;
- la stessa identità è il modo di calcolare la softmax in modo **stabile**, con $c = \max(\mathbf z)$: l'esponente più grande diventa $e^0 = 1$ e non si va in overflow;
- la loss legge **una sola componente** di $\mathbf p$: quella della classe corretta.

Consiglio della slide: dire "**logit**" quando si intendono punteggi non normalizzati; le prossime quattro lezioni lo danno per scontato. (Il nome viene dal caso binario: il logit della [scheda 24 della L6](L06-regressione-logistica.md#p-24) è l'inversa della sigmoide.)

> **Da saper fare: Softmax stabile (esercizio aggiuntivo B)**
>
> $\mathbf z = [1000, 1001, 1002]$: $e^{1000}$ va in overflow (numpy restituisce nan). Sottraendo il massimo: $[-2,-1,0]$, $\mathbf p = [0{,}090;\ 0{,}245;\ 0{,}665]$. Aggiungere 5 a tutti i logit non cambia nulla; raddoppiarli rende la distribuzione più piccata (esercizio 7b).

<a id="p-38"></a>

### Slide 38 · Cross-entropy: quanto abbiamo sbagliato?

$$L_{CE}(\mathbf p,\mathbf y) = -\sum_{k=1}^K y_k\log p_k = -\log p_c$$

- $\mathbf y$ è **one-hot**, quindi tutti i termini tranne quello della classe corretta $c$ si annullano;
- da qui l'altro nome: **negative log likelihood** ([L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-17));
- $p_c\to1$ dà $L\to0$; $p_c\to0$ dà $L\to\infty$: la loss cresce più in fretta proprio quando la classe corretta riceve quasi zero probabilità;
- con un output sigmoide binario si riduce alla solita **binary cross-entropy** $-[y\log\hat y + (1-y)\log(1-\hat y)]$ (Eq. 6.25, [L6](L06-regressione-logistica.md#p-38)).

Il grafico è la curva $-\log p_c$ con tre punti segnati: $p_c = 0{,}1\to L = 2{,}30$; $p_c = 0{,}5\to L = 0{,}69$; $p_c = 0{,}9\to L = 0{,}11$ (verificati: $\ln 10$, $\ln 2$, $-\ln 0{,}9$). Per la classificazione "dura" la loss guarda solo la probabilità assegnata alla classe giusta; il resto della distribuzione conta indirettamente, perché la massa data alle classi sbagliate è tolta a quella giusta.

> **Da saper fare: Esercizio 7: logit [2, 1, −1]**
>
> $\mathrm{softmax}([2,1,-1]) = [0{,}705;\ 0{,}259;\ 0{,}035]$. Se la classe vera è *negative*: $L = -\ln 0{,}259 = 1{,}35$. Gradiente rispetto ai logit $\mathbf p - \mathbf y = [0{,}705;\ -0{,}741;\ 0{,}035]$: un passo di discesa alza il logit di *negative* e abbassa gli altri due. Un classificatore che dà sempre la distribuzione uniforme su 3 classi ha loss $\ln 3 = 1{,}099$: è il riferimento da battere.

## Reti neurali per il linguaggio

<a id="p-39"></a>
**Slide 39 · Reti neurali per il linguaggio** — Quarta sezione (§6.4-6.5): embedding, classificazione del testo e language modelling.

<a id="p-40"></a>

### Slide 40 · Due compiti linguistici, una sola macchina

Due colonne con la stessa pila di cinque caselle:

- **classificazione del testo**: testo → embedding → nascosto $\mathbf h$ → logit su **3 classi** → softmax → sentiment;
- **language modelling**: parole di contesto → embedding → nascosto $\mathbf h$ → logit su **$|V|$ parole** → softmax → $P(\text{parola successiva})$.

Che cosa cambia: la **rappresentazione di input** (aggregata per la classificazione, concatenata per il LM: scheda 44), lo **spazio di output** (3 contro 50.000) e l'**obiettivo** di training (etichette di sentiment annotate contro la parola successiva, che il testo fornisce da sé: è la **self-supervision** della [L11](L11-embedding-word2vec.md#p-9)). La rete in mezzo è la stessa. È la risposta alla domanda della scheda 3: entrambi i compiti mappano testo in una distribuzione su un insieme fisso di risposte.

<a id="p-41"></a>

### Slide 41 · Dalle feature costruite a mano a quelle apprese

Due approcci (§6.4.1 → §6.5):

- **tradizionale, feature a mano** ("*you design x*"): conteggio delle parole del lessico positivo, conteggio di "no", log della lunghezza del documento... (sono le feature della [scheda 26 della L6](L06-regressione-logistica.md#p-26)). Interpretabili, economiche, limitate dall'**immaginazione** di chi le progetta. Una rete neurale messa sopra queste feature aggiunge soltanto le **interazioni** fra di esse (Fig. 6.10);
- **neurale, rappresentazioni apprese** ("*the network designs h*"): l'input è una sequenza di **embedding**; gli strati nascosti costruiscono qualunque feature riduca la loss; servono più dati, e li ripagano.

La frase in fondo: il vero potere del deep learning è che le feature sono **apprese, non progettate**. Il libro aggiunge che proprio per questo le reti profonde sono lo strumento giusto quando ci sono abbastanza dati per imparare le feature; con pochi dati le feature a mano e un modello semplice restano competitive (lo si vede nell'esercizio 13, dove la regressione logistica su bag of words è difficile da battere).

<a id="p-42"></a>

### Slide 42 · Embedding: da un simbolo a un vettore

La figura: *dessert* → *id = 3* → vettore **one-hot** $1\times|V|$ con un 1 in terza posizione → moltiplicato per la matrice $E$ ($|V|\times d$, con la riga 3 evidenziata) → $\mathbf e(\textit{dessert})$, un vettore $1\times d$.

- $E$ è la **matrice di embedding**: una riga appresa per ogni voce del vocabolario, forma $|V|\times d$;
- è **condivisa** fra tutte le posizioni dell'input: la stessa riga per *dessert* ovunque compaia;
- $E$ può essere **preaddestrata** (word2vec, GloVe, cap. 5: [L11](L11-embedding-word2vec.md#p-7)) oppure imparata **da zero** insieme al resto della rete, o preaddestrata e poi aggiornata (*fine-tuned*, esercizio 13).

Moltiplicare un one-hot per $E$ **seleziona una riga**: $\mathbf x E = E_{3,:}$ se $x_3 = 1$. In pratica si implementa come **lookup** (indicizzazione), non come prodotto: moltiplicare per un vettore di 50.000 zeri sarebbe uno spreco. La vista "one-hot per matrice" però è utile concettualmente: mostra che $E$ è uno strato lineare come gli altri, e che si impara con lo stesso gradiente. Gli id vengono dalla tokenizzazione (BPE, [scheda 28 della L2](L02-parole-e-token.md#p-28)).

<a id="p-43"></a>

### Slide 43 · Perché gli embedding aiutano: forza statistica condivisa

A sinistra uno spazio di embedding in 2 dimensioni con tre gruppi: animali (*cat, dog, rabbit*) in alto, parole negative (*bad, awful, terrible*) in basso a sinistra, parole positive (*good, great, superb*) a destra. Una freccia fra *cat* e *dog*: *small distance → shared statistical strength*. A destra una citazione di Zhuangzi (cap. 26): *le reti servono per i pesci; preso il pesce, si dimentica la rete. Le parole servono per il significato; colto il significato, si dimenticano le parole.*

- con i **simboli**, *cat* e *dog* sono diversi quanto *cat* e *the*: due indici distinti, niente in comune (sono vettori one-hot ortogonali);
- con gli **embedding**, ciò che il modello impara su una parola **si trasferisce** alle parole con vettori vicini (in una rete, input vicini producono attivazioni vicine);
- quel trasferimento è tutto il vantaggio, ed è il motivo per cui l'idea scala fino ai language model moderni.

Nessuno dice alla rete che *cat* e *dog* sono legati: la relazione **emerge** perché previsioni simili richiedono rappresentazioni simili. È l'ipotesi distribuzionale ([L10](L10-semantica-vettoriale.md#p-9)) vista dal lato della rete, e la ragione della sinonimia *car*/*automobile* della [scheda 6 della L11](L11-embedding-word2vec.md#p-6).

<a id="p-44"></a>

### Slide 44 · I testi hanno lunghezze diverse

Una rete feedforward vuole un input di dimensione fissa, ma un testo ha $n$ parole. Due modi di **aggregare** (*pooling*, Eq. 6.21):

$$\text{mean: }\ \mathbf x = \frac1n\sum_{i=1}^n\mathbf e(w_i)\qquad \text{max: }\ x_j = \max_i\ \mathbf e(w_i)_j$$

- semplice, economico, e una **baseline** davvero forte;
- **invariante all'ordine**: *dog bites man* e *man bites dog* danno lo stesso vettore;
- va bene quando il compito riguarda **quali parole compaiono**, male quando riguarda **come si combinano** (negazione, esercizio 8).

Riquadro a destra: **classificazione → pooling** (la presenza conta più della posizione); **language modelling → concatenazione** (bisogna sapere quale parola era dove). I modelli di sequenza (RNN, attention) mantengono l'ordine invece di scartarlo: è il prossimo passo del corso, ed è il motivo per cui il pooling è solo una baseline. Il mean pooling è l'analogo denso del **bag of words** ([L10](L10-semantica-vettoriale.md#p-33)): anche lì l'ordine si perde.

> **Da saper fare: Esercizio 8: la negazione**
>
> Con *good* = [1,0], *bad* = [−1,0], *not* = [0,1], *film* = [0,0], $\mathbf w = [3,-1]$: *good film* $\to[0{,}5;0]$, $s = 1{,}5$; *bad film* $s = -1{,}5$; *not good film* $\to[1/3;1/3]$, $s = 2/3 > 0$: positivo, **sbagliato**; *not bad film* $\to[-1/3;1/3]$, $s = -4/3$: negativo, **sbagliato**. *good, not bad* e *bad, not good* danno lo stesso $[0;1/3]$: il pooling non sa a che cosa si riferisce *not*.

<a id="p-45"></a>

### Slide 45 · Padding e masking

Un problema pratico che compare in ogni implementazione:

- **il problema**: gli esempi di un mini-batch hanno lunghezze diverse, ma un batch è **un solo tensore** (un rettangolo $m\times n\times d$): ogni sequenza deve avere la stessa lunghezza;
- **la soluzione**: si fa **padding** di ogni batch fino alla sequenza **più lunga di quel batch** (con un token speciale di pad), e si passa una **maschera** che esclude le posizioni di padding da pooling, attention e loss.

Due errori da evitare (riquadro rosso):

- **non** fare padding dell'intero dataset alla lunghezza del documento più lungo: si sprecherebbe la maggior parte del calcolo sul padding;
- un token di pad **non mascherato** corrompe silenziosamente la media. Esempio: una recensione di 3 parole con embedding $\mathbf e_1,\mathbf e_2,\mathbf e_3$ in un batch di lunghezza 10, pad = vettore nullo: la media non mascherata è $(\mathbf e_1+\mathbf e_2+\mathbf e_3)/10$ invece di $/3$, cioè il vettore giusto ridotto di un fattore 3,3. La rete vede input diversi per la stessa frase a seconda di con chi è finita nel batch.

Con la maschera $m_i\in\{0,1\}$ il mean pooling corretto è $\sum_i m_i\mathbf e_i / \sum_i m_i$.

<a id="p-46"></a>

### Slide 46 · Un classificatore neurale di testo, completo

Il diagramma (Fig. 6.13), dal basso: le parole *dessert was great* → tre embedding ($N\times d$) → **mean-pool** → un vettore $1\times d$ → $\mathbf h = g(W\mathbf x + \mathbf b)$ → $\mathbf z = U\mathbf h$ → softmax. A destra la tabella delle probabilità: **positive 0,83**, negative 0,11, neutral 0,06 (sommano a 1).

- forme: $N\times d \to d \to d_h \to 3$; un batch di $m$ recensioni aggiunge una dimensione $m$ davanti (e richiede padding e maschera, scheda 45);
- $E$, $W$, $U$ e i bias sono tutti imparati **insieme**, dallo stesso algoritmo (backpropagation + discesa del gradiente). Se si parte da embedding preaddestrati si può anche tenerli **congelati** e imparare solo $W$, $U$, $\mathbf b$.

Ogni freccia è già stata definita: lookup in $E$ (scheda 42), pooling (44), strato nascosto (31), logit e softmax (36-37). È l'architettura dell'esercizio 13, applicata alle 2000 recensioni di Pang e Lee. Conto dei parametri: $|V|d$ per $E$, $d_hd + d_h$ per lo strato nascosto, $Kd_h$ (+$K$) per l'output; con $|V|$ di decine di migliaia, quasi tutti i parametri stanno in $E$.

<a id="p-47"></a>

### Slide 47 · Un language model neurale feedforward

Il modello di Bengio et al. (2003), con finestra di $N = 3$ parole (Fig. 6.14, Eq. 6.23-6.24). Si approssima $P(w_t\mid w_{1:t-1})\approx P(w_t\mid w_{t-3},w_{t-2},w_{t-1})$, la stessa ipotesi di Markov di un 4-gram ([L4](L04-modelli-linguistici-n-gram.md#p-12)):

$$\mathbf e = [E\mathbf x_{t-3};\ E\mathbf x_{t-2};\ E\mathbf x_{t-1}]\quad \mathbf h = g(W\mathbf e + \mathbf b)\quad \mathbf z = U\mathbf h\quad \hat{\mathbf y} = \mathrm{softmax}(\mathbf z)$$

Il disegno: *for all the ?*; le tre parole di contesto passano per $E$, i tre embedding sono **concatenati** in $\mathbf e$ di dimensione $1\times Nd$, poi strato nascosto, $|V|$ logit, softmax su $P(w_t\mid\text{context})$.

- **concatenazione, non pooling**: per predire, l'ordine delle parole è il segnale;
- l'output ha **$|V|$ unità**, decine di migliaia: è lì che va la maggior parte del calcolo (la matrice $U$ è $|V|\times d_h$ e la softmax richiede di sommare $|V|$ esponenziali);
- $E$ è **condivisa** fra le tre posizioni; $W$ invece no: ha colonne diverse per ogni posizione, ed è così che il modello sa chi era dove.

Storicamente importante e didatticamente perfetto: introduce ogni idea che il transformer riuserà (embedding condivisi, strati, logit su $|V|$, softmax, cross-entropy sulla parola successiva).

> **Da saper fare: Esercizio 6b-c: dove stanno i parametri**
>
> $N = 3$, $d = 100$, $d_h = 200$, $|V| = 10.000$. $E$: $10.000\cdot100 = 1.000.000$; strato nascosto: $300\cdot200 + 200 = 60.200$; output: $200\cdot10.000 + 10.000 = 2.010.000$. Domina lo strato di output, poi $E$. Con finestra di 10 parole solo lo strato nascosto cresce: $1000\cdot200 + 200 = 200.200$ (lineare in $N$). Il classificatore con pooling invece non cambia con la lunghezza delle recensioni.

<a id="p-48"></a>

### Slide 48 · LM neurale contro LM n-gram

- **Modello n-gram: parole come simboli scollegati.** Stima conteggi su contesti discreti. Smoothing e backoff assegnano sì probabilità non nulla agli n-gram mai visti ([L5](L05-smoothing-ed-entropia.md#p-7)), ma niente lega *cat* a *dog*: l'evidenza su uno non aiuta mai l'altro.
- **Modello neurale: le parole condividono una rappresentazione.** Il contesto entra come embedding; parole simili hanno vettori vicini, quindi i parametri sono di fatto **condivisi**; l'evidenza su una parola si generalizza alle vicine.

L'esempio del libro: visto in training *I have to make sure that the **cat** gets fed.*; in test *I forgot to make sure that the **dog** gets \_\_\_*. Un n-gram predice *fed* dopo *that the cat gets* ma non dopo *that the dog gets* (al massimo ci arriva con il backoff a contesti più corti, [L5](L05-smoothing-ed-entropia.md#p-23)); un LM neurale porta *fed* anche al secondo caso, perché *cat* e *dog* stanno vicini. Il punto preciso della slide: **gli n-gram non visti li gestisce già lo smoothing; ciò che i LM neurali aggiungono è la condivisione fra parole simili**. Il libro elenca anche i costi: più lenti, più complessi, energivori, meno interpretabili.

> **Da saper fare: Esercizio aggiuntivo C in breve**
>
> Un LM neurale "bigram" giocattolo con $E(\textit{cat}) = [1;0]$, $E(\textit{dog}) = [0{,}9;0{,}1]$ dà $P(\textit{gets}\mid\textit{cat}) = 0{,}71$ e $P(\textit{gets}\mid\textit{dog}) = 0{,}65$ anche se *dog gets* non è mai stato visto: la probabilità passa dal vicino. Un bigram MLE darebbe 0.

<a id="p-49"></a>

### Slide 49 · Il limite che guida il resto del corso

La frase: *She picked up the **violin** and, after listening patiently while everyone else finished discussing the changes to tomorrow's schedule, began to \_\_\_* (risposta: *play*). Una finestra di 3 parole vede solo *began to \_\_\_*.

- la parola che decide la risposta è lontana: *violin* sta 17 parole prima della lacuna, 20 posizioni contando le due virgole e *'s* come token separati (la slide dice "più di 20 token": con un tokenizer a subword il numero dipende dalla segmentazione, ma l'ordine di grandezza è quello);
- allargando la finestra lo strato di input cresce **linearmente** ($Nd$ ingressi, quindi $Nd\cdot d_h$ pesi in $W$): i parametri esplodono e la maggior parte delle posizioni sono sprecate;
- peggio: il modello **non ha modo di dire quale** parola precedente contava; ogni posizione ha i suoi pesi fissi.

A destra la strada del corso: **reti ricorrenti** (cap. 14) → **attention** (cap. 7) → **transformer** (cap. 7). Una finestra fissa è un'ipotesi di modellazione, e spesso quella sbagliata. È la stessa critica rivolta all'ipotesi di Markov degli n-gram ([L5](L05-smoothing-ed-entropia.md#p-42)): il LM feedforward ha risolto il problema della condivisione fra parole simili, non quello del contesto lungo.

## Come impara la rete

<a id="p-50"></a>
**Slide 50 · Pausa** — Dieci minuti di pausa; dopo, come impara la rete.

<a id="p-51"></a>
**Slide 51 · Come impara la rete** — Quinta sezione (§6.6): forward pass, loss, backward pass, aggiornamento.

<a id="p-52"></a>

### Slide 52 · Il training in tre passi

Il diagramma: cinque caselle $\mathbf x\to\mathbf h\to\mathbf z\to\mathbf p\to L$ percorse in avanti (**forward pass**, calcola la previsione) e, sotto, frecce viola all'indietro (**backward pass**: quanto ha contribuito ogni parametro a $L$?).

1. **Forward**: si fa passare $\mathbf x$ nella rete e si ottiene $\mathbf p$;
2. **Loss**: si confronta $\mathbf p$ con la risposta vera $y$: $L = -\log p_y$;
3. **Backward e update**: si calcola $\partial L/\partial\theta$ per ogni parametro $\theta$, poi si fa un passo nella direzione opposta.

Sono gli stessi ingredienti della regressione logistica ([i quattro componenti della L6](L06-regressione-logistica.md#p-11): rappresentazione, funzione di classificazione, loss, ottimizzazione). Il libro: è apprendimento supervisionato, e la sola difficoltà nuova è il passo 3, perché la loss è attaccata all'ultimo strato mentre i pesi del primo strato la influenzano solo attraverso tutti gli strati intermedi. La soluzione è la **error backpropagation**, che è un caso particolare della **backward differentiation** su un grafo computazionale.

<a id="p-53"></a>

### Slide 53 · Discesa del gradiente

$$\theta^{t+1} = \theta^t - \eta\,\frac{\partial L}{\partial\theta}$$

- $\partial L/\partial\theta$ risponde a: **se sposto di poco questo parametro, come reagisce la loss?**
- $\eta$ troppo grande: la loss **oscilla o diverge**; troppo piccolo: il training **striscia** ([learning rate nella L6](L06-regressione-logistica.md#p-47));
- per la regressione logistica la loss è **convessa**; per una rete neurale **no**, e ci si accontenta di un buon minimo invece del migliore;
- in pratica si usa **Adam** o **SGD con momentum**, non la discesa del gradiente semplice (scheda 61).

Il grafico: una loss a forma di parabola in funzione di un parametro $w$, con una serie di punti rossi che scendono lungo la curva verso la stella verde del minimo; i passi si accorciano avvicinandosi, perché la pendenza diminuisce (con $\eta$ fisso il passo è proporzionale al gradiente). Il gradiente punta in salita, quindi si va dall'altra parte; $\eta$ decide di quanto. Stesso algoritmo della [scheda 43 della L6](L06-regressione-logistica.md#p-43).

<a id="p-54"></a>

### Slide 54 · Grafi computazionali

Un **grafo computazionale** scompone un'espressione in operazioni elementari, un nodo per operazione. Esempio del libro (Fig. 6.15): $L(a,b,c) = c(a+2b)$ diventa

$$d = 2b\qquad e = a + d\qquad L = c\cdot e$$

Nel disegno: i nodi di input $a, b, c$ a sinistra; $b$ entra in $d = 2b$; $a$ e $d$ entrano in $e = a + d$; $e$ e $c$ entrano in $L = c\cdot e$.

La **forward pass** riempie i valori da sinistra a destra: con $a = 3$, $b = 1$, $c = -2$: $d = 2$, $e = 5$, $L = -10$. I valori intermedi ($d$, $e$) vanno conservati: serviranno nella backward pass come derivate locali (per esempio $\partial L/\partial c = e$). È anche ciò che fanno i framework: registrano il grafo durante la forward pass (scheda 58).

<a id="p-55"></a>

### Slide 55 · La regola della catena, un nodo alla volta

Il disegno isola tre nodi: $d \to e = a + d \to L = c\cdot e$. I valori scorrono da sinistra a destra (frecce blu), i gradienti da destra a sinistra (frecce viola). Per il nodo $e$:

- $\partial L/\partial e$, il **gradiente all'uscita** di $e$ (*upstream gradient*): come cambia $L$ se cambia $e$; è già stato calcolato e arriva da destra;
- $\partial e/\partial d$, la **derivata locale** del nodo: richiede solo la formula $e = a + d$, quindi qui vale 1;
- $\partial L/\partial d = \partial L/\partial e\cdot\partial e/\partial d$, il **gradiente all'ingresso** (*downstream gradient*): il prodotto, mandato ancora a sinistra al nodo $d$.

La regola, nel riquadro: **gradiente rispetto all'input di un nodo = gradiente rispetto alla sua uscita × la sua derivata locale**. Con $c = -2$: $\partial L/\partial e = c = -2$, $\partial e/\partial d = 1$, quindi $\partial L/\partial d = -2$. Nessun nodo ha bisogno di conoscere tutto il grafo: solo ciò che arriva da destra e la propria derivata. È la regola della catena $\frac{df}{dx} = \frac{du}{dv}\frac{dv}{dx}$ (Eq. 6.31) applicata localmente.

<a id="p-56"></a>

### Slide 56 · Backward differentiation sul grafo

Il grafo della scheda 54 con tutti i gradienti scritti sugli archi (Fig. 6.17). Le derivate locali (riquadro a destra):

- $L = c\cdot e$: $\partial L/\partial e = c$, $\partial L/\partial c = e$;
- $e = a + d$: $\partial e/\partial a = 1$, $\partial e/\partial d = 1$;
- $d = 2b$: $\partial d/\partial b = 2$.

Da destra a sinistra, con $a = 3$, $b = 1$, $c = -2$ ($d = 2$, $e = 5$):

$$\frac{\partial L}{\partial e} = c = -2,\quad \frac{\partial L}{\partial c} = e = 5,\quad \frac{\partial L}{\partial d} = -2\cdot1 = -2,\quad \frac{\partial L}{\partial a} = -2\cdot1 = -2,\quad \frac{\partial L}{\partial b} = -2\cdot2 = -4$$

Verifica diretta: $L = ca + 2cb$, quindi $\partial L/\partial a = c = -2$, $\partial L/\partial b = 2c = -4$, $\partial L/\partial c = a + 2b = 5$. Ogni gradiente è quello alla sua destra per una derivata locale. Nota: per un nodo che manda la sua uscita a più nodi, i gradienti che tornano da ciascun ramo si **sommano** (qui non succede, ma succede per esempio per $\mathbf h$ in una rete con più uscite, o per la matrice $E$ condivisa fra le posizioni).

> **Da saper fare: Esercizio 9: controllo numerico e un passo**
>
> (c) $b = 1{,}01$: $L = -2(3 + 2{,}02) = -10{,}04$, quindi $\Delta L/\Delta b = -0{,}04/0{,}01 = -4$: coincide (esatto, perché $L$ è lineare in $b$). (d) Con $\eta = 0{,}1$: $a = 3 - 0{,}1(-2) = 3{,}2$; $b = 1 - 0{,}1(-4) = 1{,}4$; $c = -2 - 0{,}1\cdot5 = -2{,}5$; nuovo $L = -2{,}5\cdot(3{,}2 + 2{,}8) = -15$. La loss scende da −10 a −15.

<a id="p-57"></a>

### Slide 57 · Un gradiente, derivato una volta

Il caso di un'unità sigmoide con binary cross-entropy (il nodo finale della rete della Fig. 6.18, Eq. 6.42-6.43):

$$z = \mathbf w\cdot\mathbf x + b,\quad a = \sigma(z),\quad L = -[y\log a + (1-y)\log(1-a)]$$
$$\frac{\partial L}{\partial a} = -\Big(\frac{y}{a} - \frac{1-y}{1-a}\Big),\qquad \frac{\partial a}{\partial z} = a(1-a)$$
$$\frac{\partial L}{\partial z} = \frac{\partial L}{\partial a}\frac{\partial a}{\partial z} = -y(1-a) + (1-y)a = a - y,\qquad \frac{\partial L}{\partial w_j} = (a-y)\,x_j$$

- due termini disordinati collassano in $a - y$: l'**errore di previsione**;
- l'aggiornamento di $w_j$ è quell'errore scalato dall'input che l'ha prodotto: input grandi si prendono più colpa;
- la stessa forma vale per softmax + cross-entropy: $\partial L/\partial\mathbf z = \mathbf p - \mathbf y$ ([L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-20));
- per questo l'accoppiata softmax/cross-entropy è lo standard: il gradiente è banale (e numericamente stabile, perché non si divide mai per $a$).

È la formula della regressione logistica ([L6](L06-regressione-logistica.md#p-45), Eq. 6.29). In una rete è solo il primo anello: da $\partial L/\partial z^{[2]}$ si prosegue all'indietro verso gli strati nascosti (esercizio 10).

> **Da saper fare: Esercizio 10: backprop completa a mano**
>
> $W^{[1]} = [[0{,}5;-0{,}5];[1;0{,}5]]$, $\mathbf b^{[1]} = [1;-1]$, $\mathbf w^{[2]} = [1;-2]$, $b^{[2]} = 0{,}5$, $\mathbf x = [1;2]$, $y = 1$. Forward: $\mathbf z^{[1]} = [0{,}5;1]$, $\mathbf a^{[1]} = [0{,}5;1]$, $z^{[2]} = 0{,}5 - 2 + 0{,}5 = -1$, $a^{[2]} = 0{,}269$, $L = 1{,}313$. Backward: $\delta^{[2]} = a^{[2]} - y = -0{,}731$; $\partial L/\partial\mathbf w^{[2]} = \delta^{[2]}\mathbf a^{[1]} = [-0{,}366;-0{,}731]$; $\partial L/\partial b^{[2]} = -0{,}731$; $\partial L/\partial\mathbf a^{[1]} = \delta^{[2]}\mathbf w^{[2]} = [-0{,}731;1{,}462]$; ReLU attive, quindi $\boldsymbol\delta^{[1]}$ uguale; $\partial L/\partial W^{[1]} = \boldsymbol\delta^{[1]}\mathbf x^\top = [[-0{,}731;-1{,}462];[1{,}462;2{,}924]]$. Dopo un passo con $\eta = 0{,}1$ la loss scende a 0,239. Soluzione completa nella sezione esercizi.

<a id="p-58"></a>

### Slide 58 · In pratica non si deriva niente a mano

Il ciclo di training in PyTorch, cinque righe:

```
optimizer.zero_grad()
y_hat = model(x)
loss  = criterion(y_hat, y)
loss.backward()
optimizer.step()
```

- `zero_grad`: azzera i gradienti rimasti dal batch precedente. Se lo si dimentica, si **accumulano** (PyTorch somma i gradienti nei campi `.grad`);
- `model(x)`: la forward pass $\mathbf x\to\mathbf h\to\mathbf z\to\mathbf p$, e intanto il **grafo viene registrato**;
- `criterion`: la loss $L$, un numero per batch (di solito la media sugli esempi). In PyTorch `CrossEntropyLoss` riceve i **logit** e applica al suo interno log-softmax e NLL, in forma stabile;
- `backward()`: backward differentiation sul grafo registrato; riempie $\partial L/\partial\theta$ per ogni parametro;
- `step()`: l'optimizer applica $\theta\leftarrow\theta - \eta\,\partial L/\partial\theta$ (o la versione di Adam).

I framework costruiscono il grafo computazionale mentre si esegue la forward pass e poi lo percorrono all'indietro per noi: è la **differenziazione automatica** in modalità inversa. Saper fare la backprop a mano (schede 54-57) serve a capire che cosa calcolano e perché certe scelte (ReLU, residual, inizializzazione) aiutano.

<a id="p-59"></a>

### Slide 59 · Il vocabolario che si incontra nel codice

| termine | significato |
| --- | --- |
| example | una coppia $(\mathbf x, y)$ |
| mini-batch | un gruppo di esempi elaborati insieme |
| batch size | quanti: tipicamente da 16 a 512 |
| epoch | un passaggio completo sul training set |
| learning rate $\eta$ | quanto è lungo ogni passo |
| optimizer | la regola di aggiornamento: SGD, SGD+momentum, Adam |

A destra il ciclo: training data → mini-batch → forward pass → loss → backward pass → optimizer step, ripetuto per molte epoche. Conti utili: con 1400 recensioni e batch da 64 un'epoca sono $\lceil1400/64\rceil = 22$ passi di aggiornamento. La differenza fra stochastic, batch e mini-batch gradient descent è quella della [scheda 51 della L6](L06-regressione-logistica.md#p-51): il mini-batch dà un gradiente meno rumoroso di un singolo esempio e sfrutta il parallelismo delle GPU.

## Training in pratica

<a id="p-60"></a>
**Slide 60 · Addestrare reti profonde in pratica** — Sesta sezione (§6.6.5 e oltre il libro): optimizer, schedule, regolarizzazione, normalizzazione, connessioni residue.

<a id="p-61"></a>

### Slide 61 · Optimizer: SGD, momentum, Adam

Tre regole di aggiornamento, con $\mathbf g = \nabla_\theta L$ calcolato su un mini-batch:

- **SGD**: $\theta\leftarrow\theta - \eta\,\mathbf g$. Un solo passo per tutti i parametri.
- **SGD + momentum**: $\mathbf v\leftarrow\beta\mathbf v + \mathbf g$, $\theta\leftarrow\theta - \eta\mathbf v$. Una media mobile dei gradienti: gli zig-zag si cancellano, le direzioni costanti si sommano.
- **Adam**: $\mathbf m\leftarrow\beta_1\mathbf m + (1-\beta_1)\mathbf g$, $\mathbf s\leftarrow\beta_2\mathbf s + (1-\beta_2)\mathbf g^2$, $\theta\leftarrow\theta - \eta\,\hat{\mathbf m}/(\sqrt{\hat{\mathbf s}} + \epsilon)$. Momentum più un passo scalato **per parametro** dalla grandezza recente del gradiente. I cappelli indicano la correzione del bias, $\hat{\mathbf m} = \mathbf m/(1-\beta_1^t)$, $\hat{\mathbf s} = \mathbf s/(1-\beta_2^t)$, necessaria perché $\mathbf m$ e $\mathbf s$ partono da 0.

Il grafico: curve di livello ellittiche di una loss, ripida in $\theta_2$ e dolce in $\theta_1$. Da *start*, SGD (rosso) **rimbalza** fra le pareti della valle con grandi zig-zag; con momentum (blu) le oscillazioni si smorzano; Adam (verde) scende con una traiettoria liscia verso il minimo (stella). Default di oggi: **AdamW** (Adam con weight decay disaccoppiato, scheda 64), $\beta_1 = 0{,}9$, $\beta_2\approx0{,}999$.

> **Da saper fare: Esercizio 11b-c**
>
> Momentum con $\beta = 0{,}9$: gradiente alternato $+1,-1,\dots$: $v = 1;\ -0{,}1;\ 0{,}91;\ -0{,}181;\ 0{,}837;\ -0{,}247$ (le oscillazioni si smorzano); gradiente sempre $+1$: $v = 1;\ 1{,}9;\ 2{,}71;\ 3{,}44;\ 4{,}10;\ 4{,}69$, verso $1/(1-\beta) = 10$ (accelera). Adam al primo passo: $\hat m = g$, $\hat s = g^2$, passo $\eta\,g/|g| = \eta\,\mathrm{sign}(g)$, uguale per un gradiente di 0,001 e uno di 1000 (SGD li tratterebbe con un rapporto di $10^6$).

> **Approfondimento: β₂ nei language model**
>
> Facoltativo. 0,999 è il default di Adam; nel pretraining dei grandi language model si usa spesso $\beta_2 = 0{,}95$ (per esempio GPT-3 e LLaMA), che fa adattare più in fretta la stima di $\mathbf s$ e rende il training più stabile con batch enormi.

<a id="p-62"></a>

### Slide 62 · Schedule del learning rate

- All'inizio un $\eta$ **grande** per fare progressi; alla fine un $\eta$ **piccolo** per assestarsi in un minimo invece di rimbalzarci attorno.
- **Step decay**: si divide $\eta$ per una costante ogni tot epoche.
- **Cosine annealing**: un decadimento liscio fino a zero, $\eta_t = \frac{\eta_{\max}}{2}\big(1 + \cos\frac{\pi t}{T}\big)$, che vale $\eta_{\max}$ in $t=0$, $\eta_{\max}/2$ a metà, 0 in $t = T$.
- **Warm-up**: si fa crescere $\eta$ linearmente nei primi passi, poi lo si fa decadere. Standard per i transformer: le statistiche dei gradienti di Adam sono inaffidabili all'inizio.

Il grafico: $\eta_t$ in funzione del passo per quattro schedule: costante (tratteggio grigio a $\eta_{\max}$), step decay (blu, a gradini), coseno (verde, una mezza onda da $\eta_{\max}$ a 0), warm-up + coseno (arancio: rampa lineare da 0 a $\eta_{\max}$, poi la mezza onda). Lo schedule è un **iperparametro** come $\eta$, scelto sul development set.

> **Da saper fare: Esercizio 11a**
>
> $\eta_{\max} = 0{,}001$, $T = 1000$: $\eta_0 = 0{,}001$; $\eta_{250} = 0{,}0005(1 + \cos\frac\pi4) = 0{,}000854$; $\eta_{500} = 0{,}0005$; $\eta_{750} = 0{,}000146$; $\eta_{1000} = 0$. Con warm-up lineare sui primi 100 passi, in $t = 50$: $\eta = 0{,}001\cdot50/100 = 0{,}0005$.

<a id="p-63"></a>

### Slide 63 · Overfitting, e che cosa fare

Il grafico: loss in funzione dell'epoca (0-30). La **training loss** (blu) scende sempre, da circa 2 fin sotto 0,2; la **validation loss** (rossa) scende insieme fino a circa l'epoca 15 (minimo intorno a 0,5), poi **risale** fino a circa 0,7. Il punto verde all'epoca 15 dice *stop here*: è l'**early stopping**.

- Dividere i dati: **train** per adattare, **dev/validation** per scegliere, **test** una volta sola alla fine ([L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-32));
- ogni iperparametro scelto sul test set rende il numero riportato "una bugia" (il test non è più indipendente);
- **dropout**: azzerare unità a caso durante il training, così la rete non può contare su nessuna in particolare (scheda 65);
- inoltre: piccola **inizializzazione** casuale, **normalizzazione** dell'input, **early stopping**.

La training loss scende sempre; solo la validation loss dice se il modello sta imparando qualcosa di generale. Da quando le due curve si separano la rete sta memorizzando gli esempi di training: è l'**overfitting** della [scheda 54 della L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-54), molto più facile con una rete che con una regressione logistica, perché i parametri sono molti di più (nell'esercizio 13 migliaia per ogni recensione di training).

<a id="p-64"></a>

### Slide 64 · Regolarizzazione L2 e weight decay

$$L_{\text{reg}}(\theta) = L(\theta) + \frac\lambda2\|\theta\|^2\qquad \nabla_\theta L_{\text{reg}} = \nabla_\theta L + \lambda\theta$$
$$\theta\leftarrow\theta - \eta(\nabla_\theta L + \lambda\theta) = (1 - \eta\lambda)\,\theta - \eta\,\nabla_\theta L$$

Ogni passo prima **restringe** ogni peso di un fattore $(1-\eta\lambda)$, poi segue il gradiente: da qui il nome **weight decay**.

- preferisce **pesi piccoli**: nessuna feature singola domina la previsione, la funzione è più liscia;
- scambia una training loss un po' più alta per una validation loss più bassa;
- con Adam si tiene lo stesso restringimento $(1-\eta\lambda)$ e si applica il passo di Adam a $\nabla_\theta L$ invece che a $\nabla_\theta L_{\text{reg}}$: è **AdamW**, lo standard per i language model. Il motivo: se la penalità passasse dentro Adam, verrebbe divisa per $\sqrt{\hat s}$ e i pesi con gradienti grandi verrebbero regolarizzati meno degli altri.

$\lambda$ è un iperparametro scelto sul development set. È la regolarizzazione L2 della [scheda 56 della L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-56) (lì con $\alpha$ e senza il fattore 1/2, che serve solo a rendere il gradiente $\lambda\theta$ invece di $2\lambda\theta$).

> **Da saper fare: Esercizio 12a**
>
> $\eta = 0{,}01$, $\lambda = 0{,}1$: fattore $1 - 0{,}001 = 0{,}999$ per passo. Dopo 1000 passi senza gradiente: $0{,}999^{1000} = 0{,}368\approx e^{-1}$. Un peso che la loss non sostiene si riduce a circa un terzo.

<a id="p-65"></a>

### Slide 65 · Regolarizzazione: dropout

Due reti con 4 input, due strati nascosti da 5 e 2 output. A sinistra (*training*) alcune unità sono barrate con una × rossa, insieme alle loro connessioni: un sottoinsieme casuale viene rimosso. A destra (*test*) tutte le unità sono presenti, nessun dropout.

$$\tilde{\mathbf h} = \frac{\mathbf m\odot\mathbf h}{1-p},\qquad m_j\sim\mathrm{Bernoulli}(1-p)$$

- una nuova **maschera casuale a ogni mini-batch**: ogni unità è spenta con probabilità $p$;
- nessuna unità può contare su un particolare "partner": le feature diventano **robuste** (è come addestrare insieme moltissime sottoreti che condividono i pesi);
- dividere per $1-p$ (**inverted dropout**) mantiene uguale il valore atteso delle attivazioni: $E[\tilde h_j] = (1-p)\,\frac{h_j}{1-p} + p\cdot0 = h_j$. Così al test non cambia niente: si usa la rete intera senza riscalare.

Valori tipici: $p\approx0{,}1$ nei transformer, fino a 0,5 nei vecchi MLP. Il libro (§6.6.5) descrive la stessa idea: si sostituisce l'output di ogni unità con zero con probabilità $p$ e si rinormalizzano le altre.

> **Da saper fare: Esercizio 12b**
>
> $p = 0{,}5$, $\mathbf m = [1,0,1,0]$, $\mathbf h = [2,4,6,8]$: $\tilde{\mathbf h} = [2,0,6,0]/0{,}5 = [4,0,12,0]$. Al test si usa $\mathbf h$ così com'è.

<a id="p-66"></a>

### Slide 66 · Inizializzazione e normalizzazione

**Inizializzazione: piccola, casuale, scalata.**

$$\mathrm{Var}(W_{ij}) = \frac{1}{n_{\text{in}}}\ \text{(Xavier)},\qquad \frac{2}{n_{\text{in}}}\ \text{(He, per ReLU)}$$

- pesi tutti a zero: ogni unità nascosta calcola la stessa funzione e riceve lo stesso gradiente, **per sempre** (simmetria; esercizio 12c). Nella regressione logistica partire da zero va bene (libro §6.6.5), in una rete no;
- si estrae $W$ a caso con la varianza sopra, scalata sul **fan-in** $n_{\text{in}}$: così la varianza delle pre-attivazioni non cresce né svanisce strato dopo strato (He raddoppia perché la ReLU azzera metà delle attivazioni);
- si normalizzano anche gli input: media zero, varianza unitaria (lo z-score della [L6](L06-regressione-logistica.md#p-31)).

**Strati di normalizzazione: ricentrare e riscalare dentro la rete.** $\hat{\mathbf h} = \boldsymbol\gamma\odot\frac{\mathbf h - \mu}{\sigma} + \boldsymbol\beta$.

- **LayerNorm**: $\mu$ e $\sigma$ calcolati sulle feature di **un esempio**; $\boldsymbol\gamma$ e $\boldsymbol\beta$ appresi;
- **BatchNorm**: normalizza ogni feature sul mini-batch; comune in visione, scomoda per testi di lunghezza variabile;
- LayerNorm sta dentro **ogni blocco transformer**.

Entrambe tengono attivazioni e gradienti in un intervallo sensato al crescere della profondità.

> **Da saper fare: Esercizio 12d**
>
> $n_{\text{in}} = 300$: Xavier $\sqrt{1/300} = 0{,}058$; He $\sqrt{2/300} = 0{,}082$.

> **Approfondimento: Xavier nella forma originale**
>
> Facoltativo. Glorot e Bengio (2010) ricavano $\mathrm{Var} = 1/n_{\text{in}}$ dalla condizione sulla forward pass e $1/n_{\text{out}}$ da quella sulla backward pass, e propongono il compromesso $2/(n_{\text{in}} + n_{\text{out}})$, che è la forma implementata come `xavier_normal_` in PyTorch. La slide usa la versione con il solo fan-in (detta anche LeCun).

<a id="p-67"></a>

### Slide 67 · Connessioni residue

Il diagramma: dall'input $\mathbf h^{[\ell]}$ partono due strade, una attraverso il blocco $F$ (Linear → ReLU → Linear), l'altra un collegamento diretto viola (*identity, skip*); le due si sommano nel nodo $+$ e danno $\mathbf h^{[\ell+1]}$.

$$\mathbf h^{[\ell+1]} = \mathbf h^{[\ell]} + F(\mathbf h^{[\ell]})\qquad \frac{\partial\mathbf h^{[\ell+1]}}{\partial\mathbf h^{[\ell]}} = I + \frac{\partial F}{\partial\mathbf h^{[\ell]}}$$

- il termine identità dà ai gradienti un **percorso diretto** all'indietro attraverso molti strati: anche se $\partial F/\partial\mathbf h$ è piccolo, il prodotto delle jacobiane non svanisce, perché contiene sempre il termine $I$ (rimedio al **vanishing gradient** della scheda 16);
- hanno reso addestrabili reti con **più di 100 strati** (He et al., ResNet, 2016);
- ogni sotto-strato di un blocco transformer sta dentro una connessione residua: prossima lezione.

Il blocco deve imparare solo una **correzione** al suo input: se lo strato non serve, basta $F\approx0$, cosa più facile da imparare dell'identità. È materiale oltre il cap. 6, usato in ogni blocco del cap. 7.

<a id="p-68"></a>

### Slide 68 · La ricetta moderna di training

| problema | rimedio standard | in un transformer LM |
| --- | --- | --- |
| gradienti a zig-zag, scalati male | momentum, Adam | AdamW |
| passo sbagliato all'inizio o alla fine | schedule del learning rate | warm-up lineare, poi decadimento a coseno |
| overfitting | weight decay, dropout, early stopping | weight decay, dropout leggero |
| attivazioni che esplodono o svaniscono | inizializzazione scalata, normalizzazione | LayerNorm in ogni blocco |
| pile molto profonde che si addestrano male | connessioni residue | un residual attorno a ogni sotto-strato |

La tabella riassume le schede 61-67 ed è un'ottima traccia per una domanda d'orale ("come si addestra una rete profonda?"): problema, rimedio, che cosa si usa nei LLM. Il messaggio in fondo: la maggior parte di queste tecniche cambia poco **ciò che la rete può rappresentare** (l'approssimazione universale era già garantita, scheda 27); decide se il training **trova** una buona soluzione. È la parte "come trovarla" che il teorema lasciava aperta (scheda 28).

## Che cosa resta in un LLM

<a id="p-69"></a>
**Slide 69 · Che cosa resta in un LLM moderno** — Settima sezione (riepilogo, §6.7 del libro): tutto quello che si è visto oggi, più qualche idea nuova.

<a id="p-70"></a>

### Slide 70 · Che cosa di oggi è ancora dentro un LLM

Una griglia di dodici voci spuntate: **embedding**, **strati lineari** $W\mathbf x + \mathbf b$, **bias**, **attivazioni non lineari** (GELU), **blocchi feedforward / MLP**, **logit**, **softmax**, **cross-entropy**, **backpropagation**, **ottimizzazione basata sul gradiente**, **rappresentazioni apprese**, **residual, LayerNorm, AdamW**.

- Che cosa **aggiunge** un transformer: l'**attention**, cioè quali posizioni precedenti contano, **calcolato** invece che fissato (la risposta al limite della finestra fissa, scheda 49), e la **scala** in dati, parametri e calcolo.
- Che cosa **conserva**: tutte le voci sopra, compresi gli strumenti di training dell'ultima sezione.

Un transformer non è un oggetto di tipo diverso: sono questi pezzi, disposti in modo più intelligente e scalati. In particolare un LLM si addestra esattamente con l'obiettivo del LM feedforward della scheda 47: cross-entropy sulla parola (token) successiva, su un vocabolario di decine di migliaia di voci.

<a id="p-71"></a>

### Slide 71 · Cinque idee da ricordare

1. Una rete neurale è una **funzione parametrizzata e differenziabile**, non un cervello (schede 7-8).
2. Gli **strati nascosti imparano rappresentazioni** che rendono il compito più facile (XOR, schede 21-25).
3. Il linguaggio entra attraverso gli **embedding**, che permettono a parole simili di condividere evidenza (schede 42-43, 48).
4. Le previsioni diventano probabilità con la **softmax** e sono valutate con la **cross-entropy** (schede 36-38).
5. La **backpropagation più un optimizer** aggiusta i parametri finché emergono rappresentazioni utili (schede 52-58, 61).

Prossima lezione: **attention e transformer**, capitolo 7. Per prepararsi conviene avere sicuri tre pezzi di oggi che il transformer usa a ogni strato: le forme delle matrici con i batch (scheda 33), la softmax (scheda 36) e le connessioni residue con LayerNorm (schede 66-67).

<a id="p-72"></a>
**Slide 72 · Slide di riserva** — Materiale facoltativo, se c'è tempo o una domanda.

<a id="p-73"></a>

### Slide 73 · Una breve storia

Una linea del tempo (dalle note storiche del libro):

- **1943** McCulloch e Pitts: un neurone come elemento logico;
- **1958** Rosenblatt: il perceptron, con una regola di apprendimento;
- **1960** Widrow e Hoff: la soglia diventa un **bias** (la notazione che usiamo ancora);
- **1969** Minsky e Papert: uno strato solo calcola soltanto funzioni linearmente separabili;
- **1974** Werbos: la backpropagation, in una tesi di dottorato che nessuno lesse;
- **1986** Rumelhart, Hinton e Williams: la backpropagation, questa volta notata;
- **2003** Bengio et al.: il language model neurale disegnato oggi (scheda 47);
- **2006-** Hinton; Bengio et al.: il deep learning, con dati, GPU e ottimizzazione migliore.

Il filo: le idee di base (unità, strati, gradiente) sono vecchie di decenni; ciò che è cambiato è la possibilità pratica di addestrare reti grandi e profonde. Il libro ricorda anche gli anni '80 del connessionismo (*parallel distributed processing*), da cui vengono le rappresentazioni distribuite e le reti ricorrenti (Elman, 1990).

## Studio ed esercizi

### Guida allo studio (circa 5 h 40 min)

**L'unità e le attivazioni** (35 min)

Schede 7-16. Saper scrivere $z = \mathbf w\cdot\mathbf x + b$, $a = f(z)$ e rifare a mano l'esempio del libro ($z = 0{,}87$, $\sigma = 0{,}70$). Conoscere codominio, derivata e ruolo di sigmoide, tanh, ReLU, GELU, softmax (tabella della scheda 14); spiegare saturazione e vanishing gradient con il limite $\sigma'\le1/4$. Esercizio 1. Libro pp. 152-154.

**XOR, non linearità, approssimazione universale** (50 min)

Schede 17-28. Dimostrare che XOR non è separabile (esercizio 2c, quattro disuguaglianze); rifare la tabella della rete XOR e disegnare lo spazio $\mathbf h$ (esercizio 3); spiegare perché due strati lineari collassano in uno (Eq. 6.14, esercizio 4) e che cosa fa la ReLU nello XOR. Enunciare il teorema di approssimazione universale e le sue quattro cose che *non* dice; esercizio 5 per sentire l'esponenziale. Libro pp. 154-158 e 160.

**Feedforward, forme, softmax, cross-entropy** (45 min)

Schede 29-38. Le tre righe della forward pass; la tabella delle forme (pesi come uscite × entrate) e la versione batch $XW^\top$ (esercizio 6a); la notazione con gli apici $[\ell]$; la regressione logistica come rete a uno strato. Softmax: invarianza per traslazione, calcolo stabile, peakiness ($e^2\approx7{,}4$); cross-entropy come $-\log p_c$, valori 2,30 / 0,69 / 0,11; gradiente $\mathbf p - \mathbf y$. Esercizio 7 ed esercizio aggiuntivo B. Libro pp. 157-161, 168-169; ripassare [softmax](L07-regressione-logistica-multinomiale-e-valutazione.md#p-7) e [NLL](L07-regressione-logistica-multinomiale-e-valutazione.md#p-17) della L7.

**Reti neurali per il linguaggio** (45 min)

Schede 39-49. Matrice di embedding e lookup; perché gli embedding condividono forza statistica; mean e max pooling, invarianza all'ordine e il problema della negazione (esercizio 8); padding e masking; il classificatore completo e il LM feedforward di Bengio con concatenazione; dove stanno i parametri (esercizio 6b-c); confronto con gli n-gram (cat/dog) e il limite della finestra fissa. Esercizio aggiuntivo C. Libro pp. 161-168.

**Backpropagation** (70 min)

Schede 51-59, il cuore della seconda metà. Rifare il grafo $c(a+2b)$ avanti e indietro senza guardare (esercizio 9, compreso il passo di discesa: $L$ da −10 a −15); derivare $\partial L/\partial z = a - y$ per sigmoide + binary cross-entropy; poi l'esercizio 10 completo (forward, backward fino a $W^{[1]}$, aggiornamento, loss da 1,313 a 0,239) e l'esercizio aggiuntivo A con la softmax. Sapere che cosa fanno le cinque righe del ciclo PyTorch. Libro pp. 169-174.

**Training in pratica** (45 min)

Schede 60-68. Le formule di SGD, momentum e Adam (con la correzione del bias) e il loro comportamento sul grafico a zig-zag; schedule a coseno e warm-up; overfitting ed early stopping; L2 come weight decay e la differenza con AdamW; dropout invertito; inizializzazione Xavier/He e il problema della simmetria; LayerNorm contro BatchNorm; connessioni residue e la jacobiana $I + \partial F/\partial\mathbf h$. Saper ricostruire la tabella della scheda 68. Esercizi 11 e 12. Libro p. 174-175 (il resto è oltre il libro).

**Esercizio 13 e ripasso per l'orale** (50 min)

Leggere la soluzione dell'esercizio 13 (o, se si ha il notebook della lezione, eseguirne la sezione 11) per collegare tutto a dati veri: frozen contro fine-tuned, il conto dei parametri, la copertura di GloVe e word2vec. Poi le domande d'orale, ad alta voce, in particolare 1, 3, 6, 9, 11, 14. Schede 69-71 come riepilogo finale.

### Esercizi

#### Esercizio 1 (scheda L13): un'unità a mano

L'unità del §6.1 ha pesi $\mathbf w = [0{,}2;\ 0{,}3;\ 0{,}9]$ e bias $b = 0{,}5$.

1. Per l'input $\mathbf x = [0{,}5;\ 0{,}6;\ 0{,}1]$ calcola $z = \mathbf w\cdot\mathbf x + b$ e l'output con attivazione sigmoide, tanh e ReLU.
2. Ripeti per $\mathbf x = [-1, -2, -1]$. Quale dei tre output non porta informazione su quanto è negativo $z$?
3. Calcola la derivata della sigmoide e della tanh nello $z$ di (a), usando $\sigma'(z) = \sigma(z)(1-\sigma(z))$ e $\tanh'(z) = 1-\tanh^2(z)$.
4. *(più difficile)* La derivata della sigmoide è al più 1/4. Un segnale viene propagato all'indietro attraverso dieci unità sigmoide in catena, ognuna delle quali contribuisce con la sua derivata come fattore. Limita il prodotto e calcola $\sigma'(6)$. Che cosa dice questo delle reti profonde di unità sigmoide, e perché ReLU aiuta?

<details><summary>Soluzione</summary>

(a) $z = 0{,}1 + 0{,}18 + 0{,}09 + 0{,}5 = 0{,}87$. $\sigma(0{,}87) = 1/(1+e^{-0{,}87}) = 1/1{,}419 = 0{,}705$; $\tanh(0{,}87) = 0{,}701$; $\mathrm{ReLU}(0{,}87) = 0{,}87$.

(b) $z = -0{,}2 - 0{,}6 - 0{,}9 + 0{,}5 = -1{,}2$. $\sigma(-1{,}2) = 0{,}231$; $\tanh(-1{,}2) = -0{,}834$; $\mathrm{ReLU}(-1{,}2) = 0$. La **ReLU** dà 0 per ogni $z\le0$: da 0 non si capisce se $z$ era −0,1 o −100. Sigmoide e tanh invece restano funzioni strettamente crescenti di $z$.

(c) $\sigma'(0{,}87) = 0{,}705\cdot0{,}295 = 0{,}208$; $\tanh'(0{,}87) = 1 - 0{,}701^2 = 0{,}508$.

(d) $\sigma'(z) = \sigma(1-\sigma)$ è il prodotto $p(1-p)$, massimo per $p = 1/2$ (cioè $z = 0$), dove vale $1/4$. Dieci fattori: $(1/4)^{10} = 9{,}5\cdot10^{-7}$, nel caso migliore. Lontano da 0 è molto peggio: $\sigma(6) = 0{,}99753$, $\sigma'(6) = 0{,}0025$. In una rete profonda di sigmoidi il gradiente che arriva ai primi strati è minuscolo (**vanishing gradient**): i primi strati quasi non imparano. La ReLU ha derivata 1 per $z>0$: un'unità attiva lascia passare il gradiente invariato, senza ridurlo a ogni strato (resta il problema delle unità con $z<0$, che hanno derivata 0). Verificato in numpy.

</details>

#### Esercizio 2 (scheda L13): un'unità sola è un classificatore lineare

Un'unità con attivazione a gradino dà 1 se $z = \mathbf w\cdot\mathbf x + b > 0$ e 0 altrimenti. Gli input sono binari, $\mathbf x = [x_1, x_2]$.

1. Per $\mathbf w = [1,-1]$ e $b = 0$ disegna la frontiera di decisione nel piano e scrivi la tabella di verità. Che funzione logica è?
2. Dai pesi e bias per AND, OR e NAND.
3. *(più difficile)* Dimostra che nessuna scelta di $w_1, w_2, b$ calcola XOR (scrivi le quattro disuguaglianze e sommane due).

<details><summary>Soluzione</summary>

(a) $z = x_1 - x_2$. Frontiera: la retta $x_2 = x_1$ (la diagonale per l'origine); output 1 nel semipiano sotto la diagonale ($x_1 > x_2$). Tabella: $(0,0)\to0$ ($z = 0$, non $>0$), $(0,1)\to0$, $(1,0)\to1$, $(1,1)\to0$. È **$x_1$ AND NOT $x_2$** (l'implicazione negata).

(b) Una scelta possibile (ce ne sono infinite): **AND** $w = [1,1]$, $b = -1{,}5$ (solo $(1,1)$ dà $z = 0{,}5 > 0$); **OR** $w = [1,1]$, $b = -0{,}5$; **NAND** $w = [-1,-1]$, $b = 1{,}5$ (solo $(1,1)$ dà $z = -0{,}5$). Anche quelle del libro funzionano con questa convenzione: AND con $b = -1$ e OR con $b = 0$. Verificate su tutte e quattro le combinazioni.

(c) XOR richiederebbe: $(0,0)\to0$: $b\le0$; $(1,1)\to0$: $w_1+w_2+b\le0$; $(0,1)\to1$: $w_2+b>0$; $(1,0)\to1$: $w_1+b>0$. Sommando le ultime due: $w_1+w_2+2b>0$. Sommando le prime due: $w_1+w_2+2b\le0$. Le due conclusioni si contraddicono, quindi non esistono $w_1, w_2, b$. Geometricamente: il punto medio $(0{,}5;0{,}5)$ è medio sia dei due positivi sia dei due negativi, e $z$ è affine, quindi $z(0{,}5;0{,}5)$ dovrebbe essere insieme $>0$ e $\le0$.

</details>

#### Esercizio 3 (scheda L13): la rete XOR

La rete della Fig. 6.6: $\mathbf h = \mathrm{ReLU}(W\mathbf x + \mathbf b)$ con $W = [[1,1],[1,1]]$, $\mathbf b = [0,-1]$, e $y = \mathrm{ReLU}(\mathbf u\cdot\mathbf h + c)$ con $\mathbf u = [1,-2]$, $c = 0$.

1. Calcola $\mathbf h$ e $y$ per i quattro input. La rete calcola XOR?
2. Disegna i quattro vettori nascosti $\mathbf h$ nel piano $(h_1, h_2)$. Quali input finiscono nello stesso punto, e quale retta separa le due classi in questo spazio?
3. Sostituisci la ReLU dello strato nascosto con l'identità, $\mathbf h = W\mathbf x + \mathbf b$, e ricalcola $y$ per i quattro input. Che cosa calcola ora la rete, e perché?

<details><summary>Soluzione</summary>

(a) $W\mathbf x + \mathbf b = [x_1+x_2,\ x_1+x_2-1]$.

| $\mathbf x$ | $\mathbf h$ | $\mathbf u\cdot\mathbf h$ | $y$ |
| --- | --- | --- | --- |
| [0,0] | [0,0] | 0 | 0 |
| [0,1] | [1,0] | 1 | 1 |
| [1,0] | [1,0] | 1 | 1 |
| [1,1] | [2,1] | 0 | 0 |

Sì, è XOR.

(b) I punti sono $(0,0)$, $(1,0)$ (contato due volte: $[0,1]$ e $[1,0]$ finiscono qui) e $(2,1)$. La classe 1 è il solo punto $(1,0)$; l'output della rete è $\mathrm{ReLU}(h_1 - 2h_2)$, che vale 0, 1, 0. Una retta separatrice è $h_1 - 2h_2 = 0{,}5$, cioè $h_2 = (h_1 - 0{,}5)/2$: $(1,0)$ sta sotto, $(0,0)$ e $(2,1)$ sopra.

(c) Senza ReLU: $\mathbf u\cdot\mathbf h = (x_1+x_2) - 2(x_1+x_2-1) = 2 - x_1 - x_2$. Output: $[0,0]\to2$, $[0,1]\to1$, $[1,0]\to1$, $[1,1]\to0$ (la ReLU finale non interviene perché i valori sono $\ge0$). La rete calcola una **funzione lineare** di $x_1+x_2$, non XOR. Il motivo: la composizione di due mappe affini è affine (Eq. 6.14), e XOR non è realizzabile da una soglia su una funzione affine (esercizio 2c). Era la ReLU, azzerando il $-1$ di $h_2$ per $[0,1]$ e $[1,0]$, a piegare lo spazio e a fondere i due punti. Verificato in numpy.

</details>

#### Esercizio 4 (scheda L13): profondità senza non linearità

Una rete ha tre strati con l'identità come attivazione: $\mathbf h^{[1]} = W^{[1]}\mathbf x + \mathbf b^{[1]}$, $\mathbf h^{[2]} = W^{[2]}\mathbf h^{[1]} + \mathbf b^{[2]}$, $\mathbf y = W^{[3]}\mathbf h^{[2]} + \mathbf b^{[3]}$.

1. Mostra che $\mathbf y = W'\mathbf x + \mathbf b'$ e dai $W'$ e $\mathbf b'$.
2. Con 4 input, due strati nascosti da 100 unità e 3 output, quanti parametri ha la rete a tre strati, e quanti lo strato singolo equivalente?
3. La rete lineare a tre strati è mai più espressiva di un singolo strato lineare? Può essere meno espressiva? (Pensa a uno strato nascosto di 1 unità.)

<details><summary>Soluzione</summary>

(a) Sostituendo: $\mathbf y = W^{[3]}(W^{[2]}(W^{[1]}\mathbf x + \mathbf b^{[1]}) + \mathbf b^{[2]}) + \mathbf b^{[3]}$, quindi $W' = W^{[3]}W^{[2]}W^{[1]}$ (forma 3×4) e $\mathbf b' = W^{[3]}W^{[2]}\mathbf b^{[1]} + W^{[3]}\mathbf b^{[2]} + \mathbf b^{[3]}$.

(b) Strato 1: $100\cdot4 + 100 = 500$; strato 2: $100\cdot100 + 100 = 10.100$; strato 3: $3\cdot100 + 3 = 303$. Totale **10.903**. Lo strato singolo equivalente: $3\cdot4 + 3 = $ **15**.

(c) **Mai più espressiva**: per (a) ogni rete a tre strati lineari calcola una funzione affine, che uno strato singolo può già rappresentare. **Può essere meno espressiva**: se uno strato nascosto ha 1 sola unità, $W' = W^{[3]}W^{[2]}W^{[1]}$ passa per una matrice $1\times\cdot$ e ha **rango al più 1**; uno strato singolo 3×4 può avere rango fino a 3. In generale il rango di $W'$ è limitato dalla larghezza minima (il "collo di bottiglia"). Più parametri, nessun guadagno: la profondità serve solo con una non linearità.

</details>

#### Esercizio 5 (scheda L13): approssimazione universale a mano

Una rete con uno strato nascosto di ReLU e output lineare calcola una funzione lineare a tratti. Approssimiamo $f(x) = x^2$ su $[0,2]$.

1. Mostra che $g(x) = \mathrm{ReLU}(x) + 2\,\mathrm{ReLU}(x-1)$ coincide con $f$ in $x = 0, 1, 2$. Calcola $g(0{,}5)$ e $g(1{,}5)$ e gli errori. (L'errore massimo su ogni tratto è nel suo punto medio.)
2. Scrivi una rete con quattro unità nascoste che coincide con $f$ in 0; 0,5; 1; 1,5 e 2 (il peso di output di ogni unità è il cambio di pendenza nel suo gomito). Qual è l'errore massimo?
3. L'errore massimo di un interpolante di questo tipo di $x^2$ con gomiti equispaziati a distanza $h$ è $h^2/4$. Quante unità nascoste garantiscono un errore al più 0,01 su $[0,2]$?
4. *(più difficile)* Estendi l'idea a $[0,2]^d$ con una griglia di passo $h$ in ogni direzione. Quanti pezzi servono, all'incirca, con $h = 0{,}2$ e $d = 10$? Che cosa dice questo di ciò che promette il teorema di approssimazione universale?

<details><summary>Soluzione</summary>

(a) $g(0) = 0$; $g(1) = 1 + 0 = 1$; $g(2) = 2 + 2 = 4$: coincide con $0, 1, 4$. $g(0{,}5) = 0{,}5$ contro $0{,}25$: errore $0{,}25$. $g(1{,}5) = 1{,}5 + 1 = 2{,}5$ contro $2{,}25$: errore $0{,}25$. (Pendenze: 1 su $[0,1]$, 3 su $[1,2]$; il secondo gomito aggiunge 2.)

(b) Valori da interpolare: 0; 0,25; 1; 2,25; 4. Pendenze dei quattro tratti: $0{,}25/0{,}5 = 0{,}5$; $0{,}75/0{,}5 = 1{,}5$; $1{,}25/0{,}5 = 2{,}5$; $1{,}75/0{,}5 = 3{,}5$. Cambi di pendenza: 0,5 (in 0, partendo da pendenza 0), poi 1, 1, 1. Rete:
$$g(x) = 0{,}5\,\mathrm{ReLU}(x) + \mathrm{ReLU}(x-0{,}5) + \mathrm{ReLU}(x-1) + \mathrm{ReLU}(x-1{,}5)$$
cioè pesi nascosti tutti 1, bias $0; -0{,}5; -1; -1{,}5$, pesi di output $0{,}5; 1; 1; 1$. Errore massimo $h^2/4 = 0{,}25/4 = $ **0,0625**, nei punti medi (per esempio $g(0{,}25) = 0{,}125$ contro $0{,}0625$). Verificato su una griglia fine.

(c) $h^2/4\le0{,}01\Rightarrow h\le0{,}2$. Su $[0,2]$ servono $2/0{,}2 = 10$ tratti, quindi **10 unità** (gomiti in 0; 0,2; ...; 1,8; pesi di output 0,2 poi 0,4 nove volte). Verificato: errore massimo 0,0100.

(d) La griglia ha $2/h = 10$ celle per direzione, quindi $10^d$ celle: per $d = 10$ circa $10^{10}$ pezzi lineari. Il numero cresce **esponenzialmente con la dimensione** (maledizione della dimensionalità). Il teorema promette solo l'**esistenza** di una rete con un solo strato nascosto abbastanza largo; non dice che sia piccola, né che la si trovi con l'ottimizzazione, né che generalizzi da pochi dati. Con input di 300 dimensioni (un embedding) una costruzione così è impensabile: è uno dei motivi per cui si usano reti profonde, che compongono feature invece di piastrellare lo spazio (scheda 28).

</details>

#### Esercizio 6 (scheda L13): forme e parametri

Un classificatore con uno strato nascosto legge un embedding aggregato $\mathbf x$ di dimensione $d = 300$, ha $d_h = 128$ unità nascoste e $K = 3$ classi. Un mini-batch ha $m = 64$ recensioni, le righe di $X$.

1. Dai le forme di $X$, $W^{[1]}$, $\mathbf b^{[1]}$, della matrice nascosta $H = g(XW^{[1]\top} + \mathbf b^{[1]})$, di $W^{[2]}$ e della matrice dei logit $Z$. Quanti parametri ha il classificatore, embedding esclusi?
2. Un language model a finestra fissa legge gli embedding delle $N = 3$ parole precedenti ($d = 100$), concatenati, ha $d_h = 200$ unità nascoste e un vocabolario di $|V| = 10.000$ parole. Conta i parametri di $E$, dello strato nascosto e dello strato di output. Quale parte domina?
3. Come cresce il numero di parametri del language model se la finestra passa da 3 a 10 parole? E quello del classificatore con pooling se le recensioni si allungano?

<details><summary>Soluzione</summary>

(a) $X$: $64\times300$; $W^{[1]}$: $128\times300$; $\mathbf b^{[1]}$: $128$; $H$: $64\times128$; $W^{[2]}$: $3\times128$; $Z = HW^{[2]\top} (+\mathbf b^{[2]})$: $64\times3$. Parametri: $128\cdot300 + 128 + 3\cdot128 + 3 = 38.400 + 128 + 384 + 3 = $ **38.915** (38.912 se lo strato di output non ha bias).

(b) $E$: $|V|\times d = 10.000\cdot100 = $ **1.000.000**. Strato nascosto: input $Nd = 300$, quindi $200\cdot300 + 200 = $ **60.200**. Output: $10.000\cdot200 + 10.000 = $ **2.010.000** (2.000.000 senza bias). Domina lo **strato di output**, circa due terzi del totale (3.070.200), seguito da $E$; lo strato nascosto è meno del 2%. È anche dove va il calcolo: $|V|$ logit e una softmax su 10.000 voci per ogni previsione.

(c) Con $N = 10$ solo lo strato nascosto cambia: input $1000$, quindi $200\cdot1000 + 200 = 200.200$; cresce **linearmente in $N$** ($N d\, d_h + d_h$). $E$ e lo strato di output non cambiano. Il classificatore con pooling **non cambia affatto**: il pooling produce sempre un vettore di dimensione $d$, qualunque sia la lunghezza della recensione (cambia solo il calcolo, non i parametri).

</details>

#### Esercizio 7 (scheda L13): logit, softmax e cross-entropy

Un classificatore produce i logit $\mathbf z = [2, 1, -1]$ per le classi (positive, negative, neutral).

1. Calcola $\mathrm{softmax}(\mathbf z)$. Se la classe vera è *negative*, quanto vale la cross-entropy?
2. Che cosa succede alle probabilità se si aggiunge 5 a ogni logit? E se si raddoppia ogni logit?
3. Il gradiente della loss rispetto ai logit è $\mathbf p - \mathbf y$. Calcolalo. Quale logit viene spinto in su da un passo di discesa, e quali in giù?
4. Che loss ottiene un classificatore che dà sempre la distribuzione uniforme sulle tre classi?

<details><summary>Soluzione</summary>

(a) $e^2 = 7{,}389$, $e^1 = 2{,}718$, $e^{-1} = 0{,}368$, somma $10{,}475$. $\mathbf p = [0{,}705;\ 0{,}259;\ 0{,}035]$. $L = -\ln 0{,}259 = $ **1,349**.

(b) $+5$ a tutti: **nessun cambiamento**, perché $e^{z_i+5}/\sum_j e^{z_j+5}$ ha $e^5$ sopra e sotto (contano solo le differenze). Raddoppio: $\mathrm{softmax}([4,2,-2]) = [0{,}879;\ 0{,}119;\ 0{,}002]$, la distribuzione diventa **più piccata** (le differenze raddoppiano, i rapporti si elevano al quadrato). È l'effetto di una temperatura $T = 1/2$.

(c) $\mathbf y = [0,1,0]$: $\mathbf p - \mathbf y = [0{,}705;\ -0{,}741;\ 0{,}035]$. Il passo $\mathbf z\leftarrow\mathbf z - \eta(\mathbf p - \mathbf y)$ **alza** il logit di *negative* (gradiente negativo) e **abbassa** quelli di *positive* (molto, perché ha preso molta probabilità) e di *neutral* (poco). Le componenti sommano a 0: si sposta massa, non la si crea.

(d) $p_c = 1/3$ qualunque sia la classe vera: $L = \ln 3 = $ **1,099**. È la loss di riferimento di un modello che non ha imparato niente; qui il classificatore (1,349) fa peggio dell'uniforme su questo esempio, perché è sicuro della classe sbagliata. Verificato in numpy.

</details>

#### Esercizio 8 (scheda L13): mean pooling e ordine delle parole

Embedding giocattolo in due dimensioni: *good* = [1,0], *bad* = [−1,0], *not* = [0,1], *film* = [0,0]. Uno scorer lineare di sentiment legge la media degli embedding di una recensione, $s = \mathbf w\cdot\mathbf x$ con $\mathbf w = [3,-1]$; $s>0$ significa positivo.

1. Calcola $\mathbf x$ e $s$ per *good film*, *bad film*, *not good film* e *not bad film*. Quali recensioni sono classificate male?
2. Calcola $\mathbf x$ per *good, not bad* e per *bad, not good* (ignora la virgola). Che cosa noti?
3. Il mean pooling è comunque una baseline forte per il sentiment. Perché funziona sulla maggior parte delle recensioni reali, e su quali input ti aspetti che fallisca? Che cosa potrebbe risolverli?

<details><summary>Soluzione</summary>

(a)

| recensione | $\mathbf x$ | $s$ | esito |
| --- | --- | --- | --- |
| good film | [0,5; 0] | 1,5 | positivo, giusto |
| bad film | [−0,5; 0] | −1,5 | negativo, giusto |
| not good film | [1/3; 1/3] | $1 - 1/3 = 0{,}67$ | positivo, **sbagliato** |
| not bad film | [−1/3; 1/3] | $-1 - 1/3 = -1{,}33$ | negativo, **sbagliato** |

Il contributo di *not* è lo stesso ($-1/3$) qualunque parola neghi: la media somma gli effetti, non li compone.

(b) *good, not bad*: $([1,0] + [0,1] + [-1,0])/3 = [0;\ 1/3]$; *bad, not good*: $([-1,0]+[0,1]+[1,0])/3 = [0;\ 1/3]$. **Identici** ($s = -1/3$ per entrambi), pur avendo sentimenti opposti: il mean pooling è invariante all'ordine e non sa a quale parola si applica la negazione (*dog bites man* / *man bites dog* della scheda 44).

(c) Funziona perché nella maggior parte delle recensioni il sentiment è portato da **quali parole compaiono** (*great, boring, masterpiece, waste*), spesso molte e ridondanti, e la media ne cattura la prevalenza; le costruzioni composizionali sono una minoranza. Fallisce su **negazione** (*not good*), **contrasto** (*the first half is great, but the ending ruins it*), **ironia**, recensioni lunghe con poche parole decisive diluite nella media, frasi in cui l'ordine cambia il significato. Rimedi: feature di n-gram o bigram (*not\_good* come token, o il trucco della negazione che prefissa NOT\_ alle parole fino alla punteggiatura); una rete con una finestra concatenata; e soprattutto i **modelli di sequenza** (RNN, attention, transformer) che mantengono l'ordine. Verificato in numpy.

</details>

#### Esercizio 9 (scheda L13): un grafo computazionale

Il grafo della Fig. 6.15 calcola $L(a,b,c) = c(a+2b)$ attraverso $d = 2b$ ed $e = a + d$, con $a = 3$, $b = 1$, $c = -2$.

1. Fai la forward pass: calcola $d$, $e$ e $L$.
2. Fai la backward pass: calcola $\partial L/\partial e$, $\partial L/\partial c$, $\partial L/\partial d$, $\partial L/\partial a$ e $\partial L/\partial b$, moltiplicando a ogni nodo il gradiente che arriva dalla sua uscita per la derivata locale.
3. Controlla numericamente $\partial L/\partial b$: aumenta $b$ di 0,01 e ricalcola $L$.
4. Fai un passo di discesa del gradiente su $a$, $b$ e $c$ con $\eta = 0{,}1$. Quanto vale il nuovo $L$?

<details><summary>Soluzione</summary>

(a) $d = 2\cdot1 = 2$; $e = 3 + 2 = 5$; $L = -2\cdot5 = -10$.

(b) Nodo $L = c\cdot e$: $\partial L/\partial e = c = -2$, $\partial L/\partial c = e = 5$. Nodo $e = a + d$ (derivate locali 1 e 1): $\partial L/\partial d = -2\cdot1 = -2$, $\partial L/\partial a = -2\cdot1 = -2$. Nodo $d = 2b$ (derivata locale 2): $\partial L/\partial b = -2\cdot2 = -4$. Controllo analitico: $L = ac + 2bc$, quindi $\partial_a L = c = -2$, $\partial_b L = 2c = -4$, $\partial_c L = a + 2b = 5$.

(c) $L(3;\ 1{,}01;\ -2) = -2\cdot(3 + 2{,}02) = -10{,}04$. $\Delta L/\Delta b = (-10{,}04 + 10)/0{,}01 = -4$, uguale al gradiente (esattamente, perché $L$ è lineare in $b$ a $a, c$ fissati).

(d) $a\leftarrow 3 - 0{,}1\cdot(-2) = 3{,}2$; $b\leftarrow 1 - 0{,}1\cdot(-4) = 1{,}4$; $c\leftarrow -2 - 0{,}1\cdot5 = -2{,}5$. Nuovo $L = -2{,}5\cdot(3{,}2 + 2{,}8) = -2{,}5\cdot6 = $ **−15**: è sceso da −10 a −15, come deve dopo un passo contro il gradiente (qui $L$ non ha minimo, quindi continuerebbe a scendere). Verificato in numpy.

</details>

#### Esercizio 10 (scheda L13): backpropagation in una rete a due strati

La rete della Fig. 6.18 (due input, due unità nascoste ReLU, un output sigmoide, binary cross-entropy), con $W^{[1]} = [[0{,}5;\ -0{,}5],[1{,}0;\ 0{,}5]]$, $\mathbf b^{[1]} = [1, -1]$, $\mathbf w^{[2]} = [1, -2]$, $b^{[2]} = 0{,}5$. L'esempio di training è $\mathbf x = [1, 2]$ con etichetta $y = 1$. Il libro si ferma a $\partial L/\partial z^{[2]} = a^{[2]} - y$ (Eq. 6.43); qui si finisce il lavoro.

1. Forward pass: calcola $\mathbf z^{[1]}$, $\mathbf a^{[1]}$, $z^{[2]}$, $a^{[2]}$ e la loss.
2. Backward pass: calcola $\partial L/\partial z^{[2]}$, i gradienti di $\mathbf w^{[2]}$ e $b^{[2]}$, poi $\partial L/\partial\mathbf a^{[1]}$, $\partial L/\partial\mathbf z^{[1]}$ (Eq. 6.40 per la ReLU) e i gradienti di $W^{[1]}$ e $\mathbf b^{[1]}$.
3. Aggiorna tutti i parametri con $\eta = 0{,}1$ e ricalcola la loss sullo stesso esempio.
4. *(più difficile)* Con $\mathbf b^{[1]} = [-2, -1]$ invece, la prima unità nascosta ha $z^{[1]}_1 < 0$. Quali gradienti diventano zero, e che cosa succede a questa unità se resta inattiva su tutti gli esempi di training?

<details><summary>Soluzione</summary>

(a) $\mathbf z^{[1]} = W^{[1]}\mathbf x + \mathbf b^{[1]} = [0{,}5 - 1 + 1;\ 1 + 1 - 1] = [0{,}5;\ 1]$. $\mathbf a^{[1]} = [0{,}5;\ 1]$ (entrambe attive). $z^{[2]} = 1\cdot0{,}5 - 2\cdot1 + 0{,}5 = -1$. $a^{[2]} = \sigma(-1) = 0{,}2689$. $L = -\ln 0{,}2689 = $ **1,3133**.

(b) $\delta^{[2]} = \partial L/\partial z^{[2]} = a^{[2]} - y = -0{,}7311$.  
$\partial L/\partial\mathbf w^{[2]} = \delta^{[2]}\,\mathbf a^{[1]} = [-0{,}3655;\ -0{,}7311]$; $\partial L/\partial b^{[2]} = -0{,}7311$.  
$\partial L/\partial\mathbf a^{[1]} = \delta^{[2]}\,\mathbf w^{[2]} = [-0{,}7311;\ 1{,}4621]$.  
ReLU: derivata 1 dove $z^{[1]}\ge0$ (qui entrambe), quindi $\boldsymbol\delta^{[1]} = \partial L/\partial\mathbf z^{[1]} = [-0{,}7311;\ 1{,}4621]$.  
$\partial L/\partial W^{[1]} = \boldsymbol\delta^{[1]}\mathbf x^\top = [[-0{,}7311;\ -1{,}4621],[1{,}4621;\ 2{,}9242]]$; $\partial L/\partial\mathbf b^{[1]} = [-0{,}7311;\ 1{,}4621]$.  
Controllo numerico su $W^{[1]}_{21}$ (differenza finita con $\epsilon = 10^{-6}$): 1,4621.

(c) $\theta\leftarrow\theta - 0{,}1\,\nabla$: $W^{[1]} = [[0{,}5731;\ -0{,}3538],[0{,}8538;\ 0{,}2076]]$, $\mathbf b^{[1]} = [1{,}0731;\ -1{,}1462]$, $\mathbf w^{[2]} = [1{,}0366;\ -1{,}9269]$, $b^{[2]} = 0{,}5731$. Nuova forward: $\mathbf z^{[1]} = [0{,}9386;\ 0{,}1227]$, $z^{[2]} = 1{,}3096$, $a^{[2]} = 0{,}7874$, $L = $ **0,2390** (da 1,313). Lettura: la prima unità nascosta, con peso di output positivo, è stata rafforzata; la seconda, con peso negativo, è stata indebolita (il suo $z$ è sceso da 1 a 0,12).

(d) Con $\mathbf b^{[1]} = [-2,-1]$: $\mathbf z^{[1]} = [-2{,}5;\ 1]$, $\mathbf a^{[1]} = [0;\ 1]$, $z^{[2]} = -1{,}5$, $a^{[2]} = 0{,}182$, $L = 1{,}701$. Poiché la ReLU ha derivata 0 per $z_1^{[1]}<0$: $\delta^{[1]}_1 = 0$, quindi sono nulli i gradienti di **$b^{[1]}_1$** e della **prima riga di $W^{[1]}$**; è nullo anche il gradiente di **$w^{[2]}_1$**, perché vale $\delta^{[2]}a^{[1]}_1 = \delta^{[2]}\cdot0$. Se l'unità resta inattiva su tutti gli esempi di training, i suoi parametri non ricevono mai gradiente e non cambiano più: è un'**unità morta** (*dying ReLU*), capacità sprecata. Rimedi: inizializzazione scalata (He), learning rate non troppo alto, varianti come leaky ReLU o GELU che hanno derivata non nulla per $z<0$. Tutti i numeri verificati in numpy.

</details>

#### Esercizio 11 (scheda L13): optimizer e schedule

1. Uno schedule a coseno con $\eta_{\max} = 0{,}001$ su $T = 1000$ passi pone $\eta_t = (\eta_{\max}/2)(1 + \cos(\pi t/T))$. Calcola $\eta$ per $t$ = 0, 250, 500, 750 e 1000. Con un warm-up lineare sui primi 100 passi, quanto vale $\eta$ in $t = 50$?
2. Il momentum tiene $\mathbf v\leftarrow\beta\mathbf v + \mathbf g$ e fa il passo $\theta\leftarrow\theta - \eta\mathbf v$, con $\beta = 0{,}9$ e $\mathbf v = 0$ all'inizio. Calcola $v$ per sei passi quando il gradiente alterna +1, −1, +1, ... e quando vale sempre +1. Che cosa fa il momentum nei due casi?
3. *(più difficile)* Al primo passo Adam con la correzione del bias sposta ogni parametro di $\eta\,\hat m/(\sqrt{\hat s} + \epsilon)$. Mostra che per un singolo gradiente $g$ questo è $\eta\,\mathrm{sign}(g)$ (ignorando $\epsilon$). Confronta con la SGD semplice per un parametro con gradiente 0,001 e uno con gradiente 1000. Perché serve la correzione del bias?

<details><summary>Soluzione</summary>

(a) $t = 0$: $0{,}0005\cdot2 = 0{,}001$. $t = 250$: $0{,}0005(1 + \cos45°) = 0{,}0005\cdot1{,}7071 = 0{,}000854$. $t = 500$: $0{,}0005(1+0) = 0{,}0005$. $t = 750$: $0{,}0005(1 - 0{,}7071) = 0{,}000146$. $t = 1000$: $0{,}0005(1-1) = 0$. Con warm-up lineare da 0 a $\eta_{\max}$ nei primi 100 passi: $\eta_{50} = 0{,}001\cdot50/100 = $ **0,0005** (dopo il warm-up parte il coseno).

(b) Alternato: $v_1 = 1$; $v_2 = 0{,}9 - 1 = -0{,}1$; $v_3 = -0{,}09 + 1 = 0{,}91$; $v_4 = 0{,}819 - 1 = -0{,}181$; $v_5 = -0{,}163 + 1 = 0{,}837$; $v_6 = 0{,}753 - 1 = -0{,}247$. Costante: $1;\ 1{,}9;\ 2{,}71;\ 3{,}439;\ 4{,}095;\ 4{,}686$, che tende a $1/(1-\beta) = 10$. Nel primo caso i contributi di segno opposto si compensano: $v$ oscilla con ampiezza che tende a $1/(1+\beta) = 0{,}53$ invece di $\pm1$, e lo spostamento netto su due passi è quasi nullo ($v_1 + v_2 = 0{,}9$, poi $0{,}73$, $0{,}59$...): il momentum **smorza gli zig-zag**. Nel secondo caso i contributi si sommano e il passo effettivo arriva fino a 10 volte quello della SGD: il momentum **accelera** lungo le direzioni costanti (il grafico della scheda 61).

(c) Al passo 1, con $m_0 = s_0 = 0$: $m_1 = (1-\beta_1)g$, $s_1 = (1-\beta_2)g^2$. Correzione: $\hat m = m_1/(1-\beta_1) = g$, $\hat s = s_1/(1-\beta_2) = g^2$. Passo: $\eta\,g/\sqrt{g^2} = \eta\,g/|g| = \eta\,\mathrm{sign}(g)$. Per $g = 0{,}001$ e $g = 1000$ Adam fa lo stesso passo $\eta$; la SGD farebbe $0{,}001\eta$ e $1000\eta$, un rapporto di $10^6$: Adam è **invariante alla scala** del gradiente per parametro. Senza correzione $m$ e $s$ sono stime distorte verso 0 nei primi passi (partono da 0 e la media mobile ci mette circa $1/(1-\beta)$ passi a riempirsi: 10 passi per $m$, 1000 per $s$). Al primo passo senza correzione si avrebbe $0{,}1g/\sqrt{0{,}001g^2} = 3{,}16\,\mathrm{sign}(g)$: passi più di tre volte troppo grandi, proprio quando le statistiche sono meno affidabili. Verificato in numpy.

</details>

#### Esercizio 12 (scheda L13): regolarizzazione e inizializzazione

1. Il weight decay moltiplica ogni peso per $(1-\eta\lambda)$ a ogni passo. Con $\eta = 0{,}01$ e $\lambda = 0{,}1$, qual è il fattore, e quanto resta di un peso dopo 1000 passi in cui il suo gradiente è zero?
2. Il dropout invertito con $p = 0{,}5$ estrae la maschera $\mathbf m = [1, 0, 1, 0]$ per il vettore nascosto $\mathbf h = [2, 4, 6, 8]$. Calcola $\tilde{\mathbf h} = \mathbf m\odot\mathbf h/(1-p)$. Mostra che $E[\tilde h_j] = h_j$. Che cosa si usa al test?
3. Nella rete dell'esercizio 10 tutti i pesi di $W^{[1]}$ e $\mathbf b^{[1]}$ sono posti allo stesso valore, e i due pesi di $\mathbf w^{[2]}$ sono uguali. Mostra che le due unità nascoste ricevono lo stesso gradiente. Che cosa succede durante il training, e qual è il rimedio?
4. Per uno strato con $n_{\text{in}} = 300$ input, calcola la deviazione standard dei pesi iniziali con l'inizializzazione Xavier (varianza $1/n_{\text{in}}$) e con quella di He per ReLU (varianza $2/n_{\text{in}}$).

<details><summary>Soluzione</summary>

(a) $1 - \eta\lambda = 1 - 0{,}001 = $ **0,999**. Dopo 1000 passi: $0{,}999^{1000} = 0{,}368\approx e^{-1}$ (perché $(1 - 1/n)^n\to e^{-1}$). Resta circa il 37% del peso: i pesi che la loss non "difende" decadono esponenzialmente verso 0.

(b) $\mathbf m\odot\mathbf h = [2, 0, 6, 0]$; diviso per $0{,}5$: $\tilde{\mathbf h} = $ **[4, 0, 12, 0]**. Valore atteso: $m_j = 1$ con probabilità $1-p$, quindi $E[\tilde h_j] = (1-p)\cdot\frac{h_j}{1-p} + p\cdot0 = h_j$. Al test si usa la rete intera, $\mathbf h$ senza maschera e senza riscalare: il riscalamento è già stato fatto in training (per questo si chiama *invertito*).

(c) Se le due righe di $W^{[1]}$ sono uguali e $b^{[1]}_1 = b^{[1]}_2$, allora $z^{[1]}_1 = z^{[1]}_2$ per ogni input, quindi $a^{[1]}_1 = a^{[1]}_2$. Con $w^{[2]}_1 = w^{[2]}_2$: $\partial L/\partial a^{[1]}_j = \delta^{[2]}w^{[2]}_j$ è uguale per le due unità, e così $\delta^{[1]}_j$ (stessa derivata della ReLU) e i gradienti $\delta^{[1]}_j\mathbf x$ delle due righe di $W^{[1]}$ e di $b^{[1]}_j$; anche i gradienti di $w^{[2]}_j = \delta^{[2]}a^{[1]}_j$ sono uguali. (Verificato in numpy: con tutti i pesi 0,3 le due righe del gradiente sono identiche.) Dopo l'aggiornamento i parametri sono di nuovo uguali, e così per sempre: le due unità restano **copie** l'una dell'altra e la rete si comporta come se avesse una sola unità nascosta. Rimedio: **inizializzazione casuale** dei pesi (*symmetry breaking*), piccola e scalata; i bias possono partire da 0.

(d) Xavier: $\sqrt{1/300} = $ **0,0577**. He: $\sqrt{2/300} = $ **0,0816**.

</details>

#### Esercizio 13 (scheda L13): sentiment su recensioni reali (notebook)

La sezione 11 del notebook della lezione addestra il classificatore del §6.5 (embedding aggregati con la media, uno strato nascosto di 64 ReLU, softmax) sulle 2000 recensioni di film del dataset polarity di Pang e Lee (NLTK `movie_reviews`), divise in 1400 di training, 200 di development e 400 di test. La variabile `EMBEDDINGS` sceglie gli embedding iniziali: GloVe 100d (default), word2vec Google News 300d, oppure casuali imparati da zero.

1. Con gli embedding GloVe di default, confronta l'accuracy di test della rete con embedding congelati, della rete con embedding fine-tuned, e della regressione logistica su bag of words e su tf-idf. Quale modello è il migliore? Con 400 recensioni di test, di quali differenze ti fideresti?
2. Conta i parametri della rete fine-tuned (il notebook stampa la dimensione del vocabolario). Quale matrice ne contiene quasi tutti, e quanti parametri ci sono per recensione di training? Che cosa mostrano le curve di training e development, e quale tecnica della lezione è quindi essenziale?
3. Poni `EMBEDDINGS = "word2vec300"` e poi `"scratch"`, e riesegui la sezione. word2vec congelato fa molto meglio di GloVe congelato. Guarda la copertura stampata dal notebook e le parole più frequenti senza vettore, e spiega perché la media degli embedding di una recensione è così diversa nei due casi.
4. Confronta i vicini più prossimi di *bad*, *great* e *boring* prima e dopo il fine-tuning. Perché *good* e *bad* sono vicini in GloVe, e che cosa fa loro l'addestramento sul sentiment?
5. *(più difficile)* Il mean pooling su una recensione di 800 token diluisce le poche parole che portano l'opinione. Proponi due rimedi che usino solo materiale di questa lezione e delle precedenti, e implementane uno nel notebook.

<details><summary>Soluzione</summary>

**Nota**: il notebook non è fra i materiali di questa lezione, quindi i numeri delle esecuzioni ufficiali non sono riportati qui. La soluzione dà il ragionamento e i conti verificabili; i numeri di controllo indicati sono stati ottenuti a parte su `movie_reviews` di NLTK (1.583.820 token, 39.768 tipi, lunghezza media 792 token per recensione) e dipendono dalla divisione casuale.

(a) Che cosa aspettarsi: la regressione logistica su **bag of words** è una baseline molto forte su questo dataset (in una nostra prova con una divisione casuale 1400/200/400 e parametri di default di scikit-learn: 84,8% su bag of words, 79,0% su tf-idf, che con questa regolarizzazione di default rende peggio); la rete con GloVe **congelati** e mean pooling di solito resta sotto, il **fine-tuning** la avvicina. Quanto fidarsi: con $n = 400$ e accuracy intorno a 0,8 l'errore standard è $\sqrt{0{,}8\cdot0{,}2/400}\approx0{,}02$, cioè 2 punti: differenze di 1-3 punti sono nel rumore (lo dice anche la scheda: i numeri possono variare di un punto o due fra esecuzioni). Ci si fida solo di differenze ampie (5 punti o più) o confermate da un test di significatività come il **paired bootstrap** della [L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-44), e la scelta fra modelli va fatta sul dev set, non sul test.

(b) Parametri: $E$ ha $|V|\times100$, lo strato nascosto $100\cdot64 + 64 = 6464$, l'output $64\cdot2 + 2 = 130$ (2 classi, positivo/negativo). Con un vocabolario dell'ordine dell'intero corpus (39.768 tipi) $E$ ha circa 3,98 milioni di parametri, oltre il **99,8%** del totale; con 1400 recensioni di training sono circa **2800 parametri per recensione** (il numero esatto dipende dal vocabolario stampato dal notebook). Le curve mostrano la firma dell'**overfitting** (scheda 63): la loss di training scende verso 0 mentre quella di development smette di scendere e risale dopo poche epoche. Tecnica essenziale: **early stopping** sul dev set (insieme a weight decay e dropout); è anche il motivo per cui congelare $E$ è una forma di regolarizzazione.

(c) La media è dominata dai token più frequenti. In `movie_reviews` i più frequenti sono la punteggiatura e le parole funzionali (*, the . a and of to ' is in*...). GloVe 6B (minuscolo, con punteggiatura e stopword nel vocabolario) ha un vettore per tutti, quindi la media di ogni recensione è dominata da questi stessi vettori, quasi identici da una recensione all'altra: le medie si somigliano tutte e il segnale di sentiment è un piccolo scarto su un grande vettore comune. word2vec Google News non ha vettori per la punteggiatura e per diverse stopword molto frequenti (per esempio *a, and, of, to*): le parole senza vettore vengono saltate, e la media si fa soprattutto sulle **parole di contenuto**, dove sta l'opinione. La copertura più bassa, paradossalmente, funziona da rimozione delle stopword (la rimozione delle stopword vista nel laboratorio della L9). Con "scratch" gli embedding partono casuali e devono essere imparati da 1400 recensioni: tanti parametri, pochi dati, overfitting forte.

(d) *good* e *bad* sono vicini in GloVe perché compaiono negli **stessi contesti** (*a \_\_\_ movie*, *really \_\_\_*): l'ipotesi distribuzionale mette vicini gli antonimi, che condividono quasi tutto tranne la polarità ([scheda 5 della L10](L10-semantica-vettoriale.md#p-5)). Il fine-tuning sul sentiment sposta gli embedding nella direzione del gradiente del classificatore: le parole positive vengono spinte da una parte e le negative dall'altra lungo la direzione che il classificatore legge, quindi dopo il training i vicini di *bad* diventano parole negative (*worst, awful, boring*...) e *good* si allontana. Le rappresentazioni diventano specifiche del compito (scheda 25).

(e) Due rimedi con il materiale del corso: (1) **media pesata con tf-idf** ([L10](L10-semantica-vettoriale.md#p-43)): $\mathbf x = \sum_i \text{tfidf}(w_i)\,\mathbf e(w_i)/\sum_i\text{tfidf}(w_i)$, che abbassa il peso delle parole presenti ovunque; in alternativa, eliminare stopword e punteggiatura prima della media; (2) **max pooling** o la concatenazione di media e massimo (scheda 44): il massimo per dimensione non viene diluito dalla lunghezza, quindi una parola molto marcata lascia traccia anche in una recensione di 800 token. Implementazione minima del (2) nel modello: sostituire `x = (E[ids] * mask).sum(1) / mask.sum(1)` con `x = E[ids].masked_fill(~mask, -1e9).max(1).values` (con la maschera del padding, scheda 45), oppure `torch.cat([media, massimo], -1)` raddoppiando la dimensione di input dello strato nascosto. Il risultato va confrontato sul dev set, con le cautele di (a).

</details>

#### Esercizio aggiuntivo A: backprop con la softmax

Una rete con 2 input, 2 unità nascoste ReLU e 3 classi: $W = [[1;-1],[0{,}5;1]]$, $\mathbf b = [0;0]$, $U = [[1;0],[0;1],[-1;1]]$ (forma 3×2), niente bias di output. Input $\mathbf x = [1;0]$, classe vera la prima ($\mathbf y = [1,0,0]$).

1. Forward pass: $\mathbf z^{[1]}$, $\mathbf h$, i logit $\mathbf z$, $\mathbf p$ e la loss.
2. Backward pass: $\partial L/\partial\mathbf z$, $\partial L/\partial U$, $\partial L/\partial\mathbf h$, $\partial L/\partial W$, $\partial L/\partial\mathbf b$.
3. Un passo con $\eta = 0{,}5$: nuova loss.

<details><summary>Soluzione</summary>

(a) $\mathbf z^{[1]} = W\mathbf x = [1;\ 0{,}5]$, $\mathbf h = [1;\ 0{,}5]$. $\mathbf z = U\mathbf h = [1;\ 0{,}5;\ -0{,}5]$. $e^{1} = 2{,}718$, $e^{0{,}5} = 1{,}649$, $e^{-0{,}5} = 0{,}607$, somma $4{,}974$: $\mathbf p = [0{,}547;\ 0{,}332;\ 0{,}122]$. $L = -\ln0{,}547 = $ **0,604**.

(b) $\partial L/\partial\mathbf z = \mathbf p - \mathbf y = [-0{,}453;\ 0{,}332;\ 0{,}122]$.  
$\partial L/\partial U = (\mathbf p - \mathbf y)\mathbf h^\top = [[-0{,}453;\ -0{,}227],[0{,}332;\ 0{,}166],[0{,}122;\ 0{,}061]]$.  
$\partial L/\partial\mathbf h = U^\top(\mathbf p - \mathbf y) = [1\cdot(-0{,}453) + 0 - 1\cdot0{,}122;\ 0 + 0{,}332 + 0{,}122] = [-0{,}575;\ 0{,}453]$.  
Entrambe le ReLU attive: $\boldsymbol\delta^{[1]} = [-0{,}575;\ 0{,}453]$; $\partial L/\partial W = \boldsymbol\delta^{[1]}\mathbf x^\top = [[-0{,}575;\ 0],[0{,}453;\ 0]]$ (seconda colonna nulla perché $x_2 = 0$); $\partial L/\partial\mathbf b = [-0{,}575;\ 0{,}453]$.

(c) Dopo il passo: $\mathbf z^{[1]} = [1{,}575;\ 0{,}047]$, logit $[1{,}938;\ -0{,}218;\ -1{,}626]$, $p_1 = 0{,}874$, $L = $ **0,135**. Lo schema è identico all'esercizio 10: l'unica differenza è che $\delta$ all'output è un vettore $\mathbf p - \mathbf y$ e torna indietro con $U^\top$. Verificato in numpy, con controllo per differenze finite su $W_{21}$ (0,4535).

</details>

#### Esercizio aggiuntivo B: softmax stabile e invarianza

(a) Calcola $\mathrm{softmax}([1000, 1001, 1002])$. Che cosa succede se lo calcoli direttamente in virgola mobile? Come si evita il problema? (b) Quanto vale la cross-entropy se la classe vera è la prima? Scrivila nella forma $-z_c + \log\sum_j e^{z_j}$ e calcolala senza overflow.

<details><summary>Soluzione</summary>

(a) $e^{1000}$ supera il massimo rappresentabile in doppia precisione (circa $1{,}8\cdot10^{308}$, cioè $e^{709{,}8}$): numeratore e denominatore diventano infinito e il rapporto è `nan` (verificato in numpy). Poiché $\mathrm{softmax}(\mathbf z) = \mathrm{softmax}(\mathbf z - c)$, si sottrae $c = \max(\mathbf z) = 1002$: $\mathrm{softmax}([-2,-1,0]) = [0{,}135;\ 0{,}368;\ 1]/1{,}503 = $ **[0,090; 0,245; 0,665]**.

(b) $L = -z_1 + \log\sum_j e^{z_j} = -z_1 + c + \log\sum_j e^{z_j - c} = -1000 + 1002 + \ln1{,}503 = 2 + 0{,}408 = $ **2,408** ($= -\ln0{,}090$). È il trucco *log-sum-exp*; per questo le librerie prendono i **logit** e non le probabilità (scheda 58): calcolano log-softmax e NLL insieme in forma stabile.

</details>

#### Esercizio aggiuntivo C: un language model neurale giocattolo

Vocabolario $V = \{\textit{cat}, \textit{dog}, \textit{gets}, \textit{fed}\}$, embedding di dimensione 2: $E(\textit{cat}) = [1;0]$, $E(\textit{dog}) = [0{,}9;0{,}1]$, $E(\textit{gets}) = [0;1]$, $E(\textit{fed}) = [0{,}5;0{,}5]$. Un LM feedforward con finestra di una parola: $\mathbf h = \mathrm{ReLU}(W\mathbf e)$ con $W = I$, $\mathbf z = U\mathbf h$ con le righe di $U$ (una per parola del vocabolario, nell'ordine) $[0,0], [0,0], [2,0], [0,2]$.

1. Calcola $P(\cdot\mid\textit{cat})$ e $P(\cdot\mid\textit{dog})$.
2. In training si è visto *cat gets* ma mai *dog gets*. Che probabilità dà a *gets* dopo *dog* un bigram MLE? E il modello neurale? Perché?
3. Quanti parametri ha il modello? Come crescerebbe con una finestra di 3 parole?

<details><summary>Soluzione</summary>

(a) *cat*: $\mathbf h = [1;0]$, $\mathbf z = [0;0;2;0]$, $\mathbf p = [0{,}096;\ 0{,}096;\ 0{,}711;\ 0{,}096]$ ($e^2/(e^2+3) = 7{,}389/10{,}389$). *dog*: $\mathbf h = [0{,}9;0{,}1]$, $\mathbf z = [0;0;1{,}8;0{,}2]$, $e^{1{,}8} = 6{,}05$, $e^{0{,}2} = 1{,}22$, somma $9{,}27$: $\mathbf p = [0{,}108;\ 0{,}108;\ 0{,}653;\ 0{,}132]$.

(b) Bigram MLE: $P(\textit{gets}\mid\textit{dog}) = C(\textit{dog gets})/C(\textit{dog}) = 0$ (servirebbe lo smoothing, che però darebbe a *gets* la stessa piccola massa di qualunque altra parola). Il modello neurale dà **0,653**: *dog* ha un embedding vicino a *cat*, quindi produce uno $\mathbf h$ e dei logit vicini, e la probabilità imparata per *cat gets* si trasferisce. È l'esempio *the dog gets fed* della scheda 48 in miniatura.

(c) $E$: $4\times2 = 8$; $W$: $2\times2 = 4$ (senza bias); $U$: $4\times2 = 8$. Totale 20. Con una finestra di 3 parole concatenate $W$ diventa $2\times6$ (12 pesi): cresce solo lo strato nascosto, linearmente nella finestra, mentre $E$ resta condivisa. Verificato in numpy.

</details>

### Domande tipo orale

<details><summary>Che cosa calcola un'unità neurale, e che rapporto c'è con la regressione logistica?</summary>

Traccia: (1) somma pesata più bias $z = \mathbf w\cdot\mathbf x + b$, poi attivazione non lineare $a = f(z)$ applicata elemento per elemento; (2) $\mathbf x$ dati, $\mathbf w, b$ parametri, $z$ pre-attivazione; (3) con la sigmoide l'unità è esattamente una regressione logistica binaria, l'output in $(0,1)$ si legge come probabilità; la multinomiale è uno strato di $K$ unità con softmax: una rete a uno strato, zero strati nascosti; (4) lettura dei parametri: pesi positivi/negativi/nulli, bias come default (tutti i pesi a zero: costante $f(b)$); (5) esempio del libro: $z = 0{,}87$, $\sigma = 0{,}70$; il segno di $z$ basta a dire sopra o sotto 0,5.

</details>

<details><summary>Confronta sigmoide, tanh, ReLU e GELU. Perché ReLU è il default per gli strati nascosti?</summary>

Traccia: (1) codomini: $(0,1)$, $(-1,1)$, $[0,\infty)$, GELU liscia simile a ReLU con minimo circa −0,17; (2) ruoli: sigmoide e softmax all'output (scelta dal compito), ReLU/GELU/tanh nascoste (scelta da ciò che si addestra bene); (3) saturazione: sigmoide e tanh hanno derivata quasi nulla per $|z|$ grande; $\sigma'\le1/4$, quindi in catena il gradiente svanisce: $(1/4)^{10}\approx10^{-6}$ (vanishing gradient); (4) ReLU: economica, derivata 1 per $z>0$, non satura; limite: derivata 0 per $z<0$ (unità morte); (5) GELU nei transformer, tanh nelle RNN.

</details>

<details><summary>Perché un'unità sola non può calcolare XOR, e come lo risolve uno strato nascosto?</summary>

Traccia: (1) la frontiera di un'unità è $w_1x_1 + w_2x_2 + b = 0$, una retta (iperplano): classificatore lineare (perceptron con gradino, regressione logistica con sigmoide); (2) XOR ha i positivi su una diagonale e i negativi sull'altra: dimostrazione con le quattro disuguaglianze (sommando a coppie: $w_1+w_2+2b$ sia $>0$ sia $\le0$); (3) Minsky e Papert 1969; (4) la rete di Goodfellow: $W$ tutta di 1, $\mathbf b = [0,-1]$, $\mathbf u = [1,-2]$, ReLU; tabella: $\mathbf h$ = [0,0], [1,0], [1,0], [2,1], $y$ = 0, 1, 1, 0; (5) lo strato nascosto fonde [0,1] e [1,0] in $\mathbf h = [1,0]$ e nello spazio $\mathbf h$ il problema è lineare: representation learning.

</details>

<details><summary>Perché le attivazioni non lineari sono indispensabili in una rete profonda?</summary>

Traccia: (1) due strati lineari: $W^{[2]}(W^{[1]}\mathbf x + \mathbf b^{[1]}) + \mathbf b^{[2]} = W'\mathbf x + \mathbf b'$ con $W' = W^{[2]}W^{[1]}$; (2) vale per qualunque numero di strati: una rete lineare di 10 strati ha lo stesso potere di uno strato, con più parametri (e può essere anche meno espressiva se ha un collo di bottiglia: rango); (3) esempio: senza ReLU la rete XOR calcola $2 - x_1 - x_2$; (4) la non linearità permette di piegare lo spazio e fondere punti; è anche ciò che rende la loss non convessa, prezzo da pagare; (5) senza non linearità nessuna approssimazione universale.

</details>

<details><summary>Enuncia il teorema di approssimazione universale. Che cosa garantisce e che cosa no?</summary>

Traccia: (1) Hornik et al. 1989: per ogni $f$ continua su un compatto $K\subset\mathbb R^d$ e ogni $\varepsilon>0$ esiste una rete con un solo strato nascosto di $N$ unità con $\sup_K|f - \sum_j u_j\sigma(\mathbf w_j\cdot\mathbf x + b_j)|<\varepsilon$; (2) intuizione con ReLU: somme di gomiti, spezzate che inseguono la curva (4, 10, 40 unità: errore 0,37, 0,16, 0,01); (3) garantisce solo l'esistenza; (4) non dice: quante unità ($N$ può crescere esponenzialmente con $d$: $10^d$ celle con passo 0,2), come trovare i pesi, se si generalizza da dati finiti; l'architettura è un prior; (5) perché la profondità: feature composte, alcune funzioni richiedono esponenzialmente meno unità con più strati.

</details>

<details><summary>Descrivi la forward pass di una rete feedforward a due strati, con le forme di tutti i tensori, anche per un batch.</summary>

Traccia: (1) $\mathbf h = g(W\mathbf x + \mathbf b)$, $\mathbf z = U\mathbf h$, $\mathbf y = \mathrm{softmax}(\mathbf z)$; rete "a 2 strati" perché l'input non si conta; (2) forme: $\mathbf x$: $d$; $W$: $d_h\times d$ (riga $j$ = pesi dell'unità $j$); $\mathbf b, \mathbf h$: $d_h$; $U$: $K\times d_h$; $\mathbf z, \mathbf y$: $K$; (3) batch: righe come esempi, $H = g(XW^\top + \mathbf b)$, $Z = HU^\top$, $X$: $m\times d$, $Z$: $m\times K$; i parametri non cambiano; è `nn.Linear`; il libro in Eq. 6.22 usa $\mathbf xW$ con $W$ trasposta; (4) esempio: 64 recensioni, $d = 300$, $d_h = 128$, $K = 3$: $Z$ è 64×3, 38.915 parametri; (5) notazione $\mathbf z^{[\ell]}, \mathbf a^{[\ell]}$ per reti profonde.

</details>

<details><summary>Che cosa sono i logit, e come si passa dai logit alla loss? Perché softmax e cross-entropy vanno in coppia?</summary>

Traccia: (1) logit = punteggi non normalizzati dell'ultimo strato, qualunque reale; (2) softmax $p_i = e^{z_i}/\sum_j e^{z_j}$: positivi e somma 1; conserva l'ordine, amplifica le differenze (scarto 2 → rapporto 7,4); (3) invarianza $\mathrm{softmax}(\mathbf z) = \mathrm{softmax}(\mathbf z - c)$, usata con $c = \max\mathbf z$ per la stabilità; (4) cross-entropy con target one-hot $= -\log p_c$ (negative log likelihood): 2,30 / 0,69 / 0,11 per $p_c$ = 0,1 / 0,5 / 0,9; uniforme su 3 classi: $\ln3$; (5) il gradiente rispetto ai logit è $\mathbf p - \mathbf y$: semplice, stabile, e i framework prendono i logit e calcolano log-softmax + NLL insieme.

</details>

<details><summary>Come entra il testo in una rete neurale? Spiega la matrice di embedding e il pooling.</summary>

Traccia: (1) tokenizzazione → id; $E$ è $|V|\times d$, one-hot $\times E$ seleziona una riga, in pratica un lookup; $E$ condivisa fra le posizioni; preaddestrata (word2vec, GloVe), da zero o fine-tuned; (2) vantaggio: parole simili hanno vettori vicini, ciò che si impara su una si trasferisce (cat/dog), relazione emergente; (3) i testi hanno lunghezze diverse: mean pooling $\frac1n\sum\mathbf e(w_i)$ o max pooling per dimensione; vettore di dimensione fissa; (4) limiti: invariante all'ordine (dog bites man), negazione (esercizio 8); baseline forte perché il sentiment dipende soprattutto da quali parole compaiono; (5) padding al più lungo del batch e maschera, altrimenti la media è corrotta.

</details>

<details><summary>Descrivi il language model neurale feedforward di Bengio. In che cosa è migliore di un n-gram, e quale limite ha?</summary>

Traccia: (1) ipotesi di Markov come un 4-gram: $P(w_t\mid w_{t-3},w_{t-2},w_{t-1})$; (2) $\mathbf e = [E\mathbf x_{t-3}; E\mathbf x_{t-2}; E\mathbf x_{t-1}]$ (concatenazione, perché l'ordine conta), $\mathbf h = g(W\mathbf e + \mathbf b)$, $\mathbf z = U\mathbf h$ con $|V|$ logit, softmax; addestramento con cross-entropy sulla parola successiva (self-supervised); (3) parametri: lo strato di output $d_h\times|V|$ domina parametri e calcolo; (4) vantaggio: condivisione fra parole simili (cat gets fed / dog gets \_\_\_); gli n-gram mai visti li gestiva già lo smoothing; (5) limite: finestra fissa; violin… began to \_\_\_; allargarla fa crescere $W$ linearmente e non dice quale parola conta → RNN, attention, transformer.

</details>

<details><summary>Che cos'è un grafo computazionale e come funziona la backward differentiation? Fai l'esempio del libro.</summary>

Traccia: (1) scomporre una funzione in operazioni elementari, un nodo per operazione; $L = c(a+2b)$: $d = 2b$, $e = a+d$, $L = ce$; (2) forward: con $a = 3$, $b = 1$, $c = -2$: $d = 2$, $e = 5$, $L = -10$, conservando i valori intermedi; (3) backward: ogni nodo riceve il gradiente upstream, lo moltiplica per la derivata locale e lo manda indietro (regola della catena locale); (4) numeri: $\partial L/\partial e = c = -2$, $\partial L/\partial c = e = 5$, $\partial L/\partial d = -2$, $\partial L/\partial a = -2$, $\partial L/\partial b = -4$; controllo con differenza finita; (5) i gradienti di rami diversi che convergono in un nodo si sommano; è ciò che fa `loss.backward()`.

</details>

<details><summary>Deriva il gradiente della binary cross-entropy rispetto alla pre-attivazione di un'unità sigmoide, e spiega come si prosegue verso gli strati nascosti.</summary>

Traccia: (1) $L = -[y\log a + (1-y)\log(1-a)]$, $a = \sigma(z)$; (2) $\partial L/\partial a = -(y/a - (1-y)/(1-a))$, $\partial a/\partial z = a(1-a)$; il prodotto dà $a - y$; (3) $\partial L/\partial w_j = (a-y)x_j$: errore per input; stessa forma $\mathbf p - \mathbf y$ per la softmax; (4) verso lo strato nascosto: $\partial L/\partial\mathbf a^{[1]} = \delta^{[2]}\mathbf w^{[2]}$, poi per la ReLU si moltiplica per 1 o 0, $\partial L/\partial W^{[1]} = \boldsymbol\delta^{[1]}\mathbf x^\top$; (5) esempio dell'esercizio 10: $L$ da 1,313 a 0,239 dopo un passo; unità con $z<0$ non ricevono gradiente.

</details>

<details><summary>Confronta SGD, momentum e Adam. Che cosa sono AdamW e uno schedule con warm-up e coseno?</summary>

Traccia: (1) SGD $\theta\leftarrow\theta - \eta\mathbf g$ con $\mathbf g$ dal mini-batch, un passo uguale per tutti; $\eta$ troppo grande diverge, troppo piccolo striscia; (2) momentum $\mathbf v\leftarrow\beta\mathbf v + \mathbf g$: media dei gradienti, gli zig-zag si cancellano (gradiente alternato) e le direzioni costanti accelerano fino a $1/(1-\beta)$; (3) Adam: momenti $\mathbf m, \mathbf s$ con correzione del bias, passo $\eta\hat{\mathbf m}/(\sqrt{\hat{\mathbf s}}+\epsilon)$ scalato per parametro (primo passo $\eta\,\mathrm{sign}(g)$); (4) AdamW: weight decay $(1-\eta\lambda)$ applicato a parte, non dentro Adam; $\beta_1 = 0{,}9$, $\beta_2\approx0{,}999$; (5) schedule: warm-up lineare (statistiche di Adam inaffidabili all'inizio) poi coseno $\frac{\eta_{\max}}2(1+\cos\frac{\pi t}T)$; scelto sul dev set.

</details>

<details><summary>Come si combatte l'overfitting in una rete neurale? Spiega weight decay e dropout.</summary>

Traccia: (1) diagnosi: training loss sempre in discesa, validation loss che risale; early stopping al minimo della validation; train/dev/test, mai scegliere sul test; (2) L2: $L + \frac\lambda2\|\theta\|^2$, gradiente $+\lambda\theta$, aggiornamento $(1-\eta\lambda)\theta - \eta\nabla L$: weight decay; pesi piccoli, funzione più liscia; esempio $0{,}999^{1000}\approx0{,}37$; (3) dropout: maschera Bernoulli nuova a ogni mini-batch, unità spente con probabilità $p$, divisione per $1-p$ (invertito) per conservare il valore atteso; al test nessun dropout; $p\approx0{,}1$ nei transformer, fino a 0,5 negli MLP; (4) altro: inizializzazione piccola, normalizzazione dell'input, meno parametri (embedding congelati).

</details>

<details><summary>Perché l'inizializzazione conta, e a che cosa servono LayerNorm e le connessioni residue?</summary>

Traccia: (1) pesi tutti uguali (o a zero): simmetria, ogni unità nascosta calcola la stessa funzione e riceve lo stesso gradiente per sempre (esercizio 12c); serve un'inizializzazione casuale; (2) scalata sul fan-in: Xavier $1/n_{\text{in}}$, He $2/n_{\text{in}}$ per ReLU, per tenere stabile la varianza delle attivazioni; per $n_{\text{in}} = 300$: 0,058 e 0,082; (3) LayerNorm: media e varianza sulle feature di un esempio, $\gamma$ e $\beta$ appresi; BatchNorm sul batch, scomoda per testi; (4) residual: $\mathbf h^{[\ell+1]} = \mathbf h^{[\ell]} + F(\mathbf h^{[\ell]})$, jacobiana $I + \partial F/\partial\mathbf h$: percorso diretto per il gradiente contro il vanishing gradient; reti con più di 100 strati; il blocco impara una correzione; (5) tutti presenti in ogni blocco transformer.

</details>

<details><summary>Che cosa della lezione di oggi si ritrova in un LLM moderno, e che cosa aggiunge il transformer?</summary>

Traccia: (1) restano: embedding, strati lineari con bias, attivazioni non lineari (GELU), blocchi MLP, logit, softmax, cross-entropy, backpropagation, ottimizzazione a gradiente, rappresentazioni apprese, residual, LayerNorm, AdamW; (2) l'obiettivo è lo stesso del LM feedforward: cross-entropy sul token successivo, softmax su tutto il vocabolario; (3) il transformer aggiunge l'attention: quali posizioni precedenti contano, calcolato e non fissato, che risolve il limite della finestra fissa; (4) e la scala: dati, parametri, calcolo; (5) slogan: un transformer non è un oggetto di tipo diverso, sono questi pezzi disposti meglio e scalati.

</details>

<details><summary>Che cosa significa che gli strati nascosti imparano rappresentazioni? Collega XOR, embedding e feature costruite a mano.</summary>

Traccia: (1) lo strato nascosto trasforma lo spazio dell'input in uno in cui il compito è facile (lineare per l'ultimo strato); XOR: [0,1] e [1,0] fusi in [1,0]; (2) le ultime due righe di una rete sono una regressione logistica multinomiale sulle feature $\mathbf h$ che la rete costruisce; (3) approccio tradizionale: feature a mano (lessico positivo, conteggio di "no"), interpretabili ma limitate dall'immaginazione; una rete su queste aggiunge solo interazioni; (4) approccio neurale: input = embedding, gli strati costruiscono qualunque feature riduca la loss; servono più dati; (5) gli embedding stessi sono rappresentazioni apprese: cat e dog vicini, e il fine-tuning sul sentiment li rende specifici del compito (good e bad si allontanano).

</details>
