# L14 · Transformer: l'attenzione

*Transformers: Attention* · 14/10/2026 · Claudio Gallicchio · lettura: J&M cap. 7, apertura e §7.1-7.3 (pp. 177-191)

[Versione interattiva sul sito](https://gabriele-marsili.github.io/appunti-magistrale-ai/anno-2/hlt/sito/#L14) · [Indice della dispensa](README.md)

Prima lezione sul **transformer** (J&M cap. 7): invece di un vettore fisso per parola, ogni token riceve un **embedding contestuale** costruito strato per strato dalla **self-attention causale**. Si parte dall'attenzione semplificata (softmax di prodotti scalari), poi la **testa di attenzione** con **query, key, value**, lo **scaled dot product** e $W^O$, calcolata a mano sull'esempio *chicken, road, it*; la **multi-head attention** e il conto dei parametri ($4d^2$); il **transformer block** prenorm con **residual stream**, feedforward (e SwiGLU), **layer norm** e RMSNorm; infine la forma matriciale $\mathrm{softmax}(\mathrm{mask}(QK^\top/\sqrt{d_k}))V$ con la **maschera causale** e il costo quadratico. Tutti i numeri delle slide tornano: nessuna correzione. Con il notebook (nessun bug) e la scheda di 12 esercizi.

## Indice

- [Apertura](#apertura)
- [Il transformer in breve](#il-transformer-in-breve)
- [Attenzione](#attenzione)
- [La testa di attenzione](#la-testa-di-attenzione)
- [Multi-head attention](#multi-head-attention)
- [Il transformer block](#il-transformer-block)
- [Tutti i token insieme](#tutti-i-token-insieme)
- [Notebook](#notebook)
- [Studio ed esercizi](#studio-ed-esercizi)

## Apertura

<a id="p-1"></a>

### Slide 1 · Transformer: l'attenzione

Lezione 14, di Claudio Gallicchio (14 ottobre 2026): si entra nel **transformer**, l'architettura di tutti i grandi language model. Il sottotitolo dice il programma: **self-attention**, **multi-head attention** e il **transformer block**.

È il seguito diretto della L13: là il language model feedforward guardava una **finestra fissa** di parole precedenti, con un embedding statico per parola ([il limite della scheda 49 della L13](L13-reti-neurali.md#p-49)). Qui ogni token riceve un vettore costruito **dal suo contesto**, e il meccanismo che lo costruisce è l'attenzione. Posizioni, testa di language modeling e decoding sono rimandati alla prossima lezione.

<a id="p-2"></a>

### Slide 2 · Indice

Sei parti, nell'ordine in cui si costruisce un blocco:

1. **il transformer in breve**: un token che attraversa embedding, blocchi e testa di language modeling;
2. **attenzione**: perché servono gli embedding contestuali, e la versione semplificata (somma pesata con pesi da prodotti scalari);
3. **la testa di attenzione**: query, key, value, il fattore $1/\sqrt{d_k}$, $W^O$, con un esempio fatto a mano;
4. **multi-head attention**: più teste in parallelo, concatenate;
5. **il transformer block**: layer norm, feedforward, residual stream;
6. **tutti i token insieme**: la forma matriciale $QK^\top$, la maschera causale e il costo quadratico.

<a id="p-3"></a>

### Slide 3 · Riferimento: J&M capitolo 7

Lettura principale: **capitolo 7** di Jurafsky e Martin (Transformers and Pretraining), l'apertura del capitolo e i paragrafi **7.1** (Attention), **7.2** (Transformer Blocks) e **7.3** (Parallelizing computation using a single matrix X). Nella numerazione stampata del draft di agosto 2026 sono le pagine 177-191.

Le figure delle slide (il transformer con la residual stream, il calcolo di $a_3$ in otto passi, la multi-head con $A = 4$, il blocco, le matrici $Q$, $K$, $V$) sono quelle del libro: rileggerle lì con le didascalie aiuta. Il resto del capitolo (embedding di posizione, testa di language modeling, decoding, pretraining) è la lezione successiva.

## Il transformer in breve

<a id="p-4"></a>
**Slide 4 · Il transformer in breve** — Vista dall'alto: dall'input alla distribuzione sul token successivo.

<a id="p-5"></a>

### Slide 5 · Da embedding statici a embedding contestuali

Il messaggio della slide in due righe: **word2vec dà un vettore per parola**, un **transformer dà un vettore per token nel suo contesto**.

- **Embedding statici** ([L11](L11-embedding-word2vec.md#p-7)): `chicken` ha sempre lo stesso vettore, qualunque sia la frase. Tutti i sensi e gli usi di una parola sono schiacciati in un punto solo.
- **Reti feedforward** ([L13](L13-reti-neurali.md#p-42)): la matrice di embedding $E$ come primo strato; il contesto entra solo concatenando una finestra fissa.
- **Transformer** (Vaswani et al., 2017): l'architettura standard dei large language model. Qui la si usa per il **language modeling da sinistra a destra** (causale): predire i token uno alla volta dal contesto precedente, come in [generazione autoregressiva della L1](L01-introduzione-al-corso.md#p-6).

Il punto chiave: il vettore di un token non è più letto da una tabella, ma **calcolato** strato dopo strato combinando le rappresentazioni degli altri token.

<a id="p-6"></a>

### Slide 6 · Un token attraverso il transformer: l'input

La figura (del libro) mostra il transformer per **un solo token**, dal basso verso l'alto: embedding, $L$ blocchi, unembedding e softmax. Il riquadro evidenzia l'**input encoding**.

- il token viene convertito in un vettore: la sua riga della **matrice di embedding $E$**, come nella L13;
- a questo si **somma** (il nodo $\oplus$ della figura) un vettore che codifica la sua **posizione** nella sequenza (box Positional).

La posizione serve perché l'attenzione, come vedremo, è una somma pesata e di per sé non sa in che ordine stanno i token. Come si costruiscono gli embedding di posizione è argomento della prossima lezione (§7.4); oggi basta sapere che l'input del primo blocco è *embedding + posizione*, un vettore di dimensione $d$.

<a id="p-7"></a>

### Slide 7 · Un token attraverso il transformer: i blocchi

Il riquadro ora è sulla pila di **transformer block**, ripetuta $L$ volte (L times nella figura). Ogni blocco contiene **layer norm**, **multi-head attention**, un'altra layer norm e uno strato **feedforward**.

La colonna azzurra verticale è la **residual stream**: il vettore del token sale lungo la colonna e ogni componente del blocco *legge* dalla colonna, calcola qualcosa e *aggiunge* il risultato (i due nodi $\oplus$). Il vettore viene così passato in alto e arricchito a ogni blocco, invece di essere sostituito. È l'idea delle connessioni residue viste nella [scheda 67 della L13](L13-reti-neurali.md#p-67), portata all'estremo.

Le frecce tratteggiate che entrano in MultiHead Attention da sinistra sono le informazioni che arrivano **dagli altri token**: è l'unico punto del blocco dove questo succede (scheda 51).

<a id="p-8"></a>

### Slide 8 · Un token attraverso il transformer: la testa di language modeling

In cima, la **language modeling head**: il vettore finale del token viene moltiplicato per la **matrice di unembedding $U$**, che dà un punteggio (logit) per ogni token del vocabolario; una **softmax** sul vocabolario trasforma i logit in una **distribuzione di probabilità sul token successivo**.

È lo stesso schema logit + softmax della regressione multinomiale ([L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-8)) e dell'LM feedforward della L13: cambia solo come si arriva al vettore da cui partono i logit. Nella prossima lezione si vedrà che spesso $U$ è la trasposta di $E$ (weight tying) e come si sceglie il token da generare (decoding).

<a id="p-9"></a>

### Slide 9 · Tutta la finestra di contesto

La figura mostra il modello su tutto l'input `So long and thanks for`: in basso la codifica di input (embedding $E$ più la posizione 1-5), in mezzo i blocchi impilati, in alto una testa $U$ per posizione con il **token successivo più probabile**: *long, and, thanks, for, all*.

- $n$ vettori di input $x_1,\dots,x_n$ diventano $n$ vettori di output $h_1,\dots,h_n$: stessa lunghezza;
- da $L = 12$ a $L = 96$ blocchi o più;
- le frecce fra colonne portano informazione **dai token precedenti**: la colonna di *thanks* riceve da *So, long, and*, mai da *for*.

In training si predice a ogni posizione contemporaneamente (ogni posizione ha il suo target, il token dopo); in generazione serve solo l'ultima colonna. Questo funziona perché l'attenzione è **causale**: nessuna posizione vede il futuro.

<a id="p-10"></a>

### Slide 10 · Oggi: dentro i transformer block

Mappa della lezione. Il transformer ha tre pezzi: **input encoding** (embedding + posizione), **transformer block** $\times L$, **language modeling head** (unembedding + softmax). Oggi solo nozioni di base sul primo e sul terzo; il cuore è il secondo.

I cinque passi di oggi, ognuno costruito sul precedente:

1. **attention**: una somma pesata del contesto;
2. **la testa di attenzione**: query, key, value, una testa a mano;
3. **multi-head attention**: più teste in parallelo;
4. **il transformer block**: attenzione, feedforward, layer norm, residual stream;
5. **tutti i token insieme**: matrici e maschera.

Frase da ricordare: **l'attenzione è il nucleo del transformer, costruisce il vettore di un token a partire dal suo contesto**.

## Attenzione

<a id="p-11"></a>
**Slide 11 · Attenzione: embedding contestuali** — Perché il vettore di una parola deve dipendere dalla frase, e la prima versione dell'attenzione.

<a id="p-12"></a>

### Slide 12 · Il significato di it

Due frasi che differiscono per una sola parola: `The chicken didn't cross the road because it was too tired.` e `... because it was too wide.`

- Con un **vettore statico** c'è un solo vettore per *it*: un pronome che può riferirsi ad animali e a cose inanimate, uguale nelle due frasi.
- **Nel contesto** invece *it* è il pollo nella prima frase (a essere stanco è il pollo) e la strada nella seconda (a essere larga è la strada).

Il riferimento del pronome (**coreferenza**) si decide con informazione che sta *altrove* nella frase, in questo caso dopo il pronome: *tired* o *wide*. Coppie di frasi così (Winograd schema) sono un test classico di comprensione. Conclusione della slide: **il significato di it dipende dal contesto**, quindi la sua rappresentazione deve dipenderne.

<a id="p-13"></a>

### Slide 13 · Il significato di it, da sinistra a destra

Un language model **causale** legge da sinistra a destra. Quando arriva a *it* ha visto solo `The chicken didn't cross the road because it`: *tired* e *wide* non sono ancora arrivati, quindi **non può ancora sapere** a cosa si riferisce *it*.

La conseguenza è sottile ma importante: in quel punto il vettore di *it* dovrebbe avere **aspetti sia di chicken sia di road**, i due candidati plausibili. Sarà il vettore di un token successivo (per esempio quello di *wide*) a risolvere l'ambiguità, attingendo a sua volta dal contesto.

Il vincolo causale non è un dettaglio implementativo: deriva dal compito, predire il prossimo token sapendo solo il passato (la fattorizzazione della [regola della catena, L4](L04-modelli-linguistici-n-gram.md#p-11)).

<a id="p-14"></a>

### Slide 14 · Le parole di contesto possono essere lontane

Altri due fenomeni dove serve contesto, e non necessariamente vicino:

- **Accordo**: `The keys to the cabinet are on the table.` Il soggetto è *The keys*, plurale, quindi il verbo è *are* e non *is*. La parola immediatamente prima del verbo è *cabinet*, singolare: un modello che guarda solo la parola precedente (un bigramma) sarebbe tentato da *is*.
- **Senso**: `I walked along the pond, and noticed one of the trees along the bank.` Qui *bank* è la riva e non la banca, per via di *pond*, una decina di parole prima ([sensi delle parole, L10](L10-semantica-vettoriale.md#p-6)).

Le parole che aiutano a calcolare il significato di una parola possono essere **molto lontane** nella frase o nel paragrafo. Gli n-gram (finestra di $n-1$ parole) e l'LM feedforward (finestra fissa) non ci arrivano; l'attenzione può guardare qualunque token precedente, a qualunque distanza.

<a id="p-15"></a>

### Slide 15 · Embedding contestuali

Definizione: gli **embedding contestuali** sono vettori per il significato di una parola **nel suo contesto**, costruiti integrando il significato delle parole di contesto utili.

- **Strato dopo strato**: a ogni strato la rappresentazione del token $i$ combina l'informazione su $i$ dello strato precedente con l'informazione sui token vicini. Ne escono rappresentazioni sempre più contestualizzate salendo nella pila.
- **Attenzione**: è il meccanismo che **pesa e combina** le rappresentazioni degli altri token del contesto allo strato $k$ per costruire la rappresentazione di un token allo strato $k+1$.

Da notare la doppia componente: il token conserva la propria informazione (lo farà la residual stream) e ne aggiunge altra presa dai vicini (lo farà l'attenzione). Pesare vuol dire che non tutti i token del contesto contano allo stesso modo: i pesi sono calcolati, diversi per ogni token e ogni frase.

<a id="p-16"></a>

### Slide 16 · Self-attention su it

La figura mostra i token della frase su due righe: in alto lo strato $k+1$, in basso lo strato $k$. Dal token *it* dello strato $k+1$ partono linee verso i token dello strato $k$; **sfumature più scure** indicano **pesi di attenzione più alti**.

- i pesi più alti (evidenziati con un riquadro) vanno a *chicken* e *road*: a questo punto *it* potrebbe riferirsi all'uno o all'altro, come detto nella scheda 13;
- pesi bassi sugli altri token precedenti (*The*, *it* stesso);
- *was too tired* sono in grigio: stanno dopo *it* e un modello causale non li usa.

Si chiama **self**-attention perché i token guardano altri token **della stessa sequenza** (non di un'altra frase, come nell'attenzione encoder-decoder della traduzione).

<a id="p-17"></a>

### Slide 17 · Self-attention causale

La figura: cinque input $x_1,\dots,x_5$ in basso, un blocco di attenzione per posizione, cinque output $a_1,\dots,a_5$ in alto. Ogni $a_i$ riceve frecce da $x_i$ e da tutti gli $x$ a sinistra: $a_1$ solo da $x_1$, $a_5$ da tutti e cinque.

- **Input e output**: uno strato di self-attention mappa $x_1,\dots,x_n$ in $a_1,\dots,a_n$ della **stessa lunghezza**.
- **Causale**: alla posizione $i$ l'attenzione usa $x_i$ e tutti gli input precedenti $x_1,\dots,x_{i-1}$, **nessun token dopo** $i$.
- **In parallelo**: lo stesso calcolo (stessi parametri) avviene a ogni posizione $i$, indipendentemente dalle altre posizioni dello stesso strato.

Il terzo punto è ciò che distingue il transformer dalle reti ricorrenti: $a_5$ non deve aspettare $a_4$, quindi tutte le posizioni si calcolano insieme (ultima parte della lezione).

<a id="p-18"></a>

### Slide 18 · Una versione semplificata dell'attenzione

Tre formule, prima senza parametri:

$$a_i = \sum_{j\le i} \alpha_{ij}\, x_j \qquad \mathrm{score}(x_i,x_j) = x_i\cdot x_j \qquad \alpha_{ij} = \mathrm{softmax}(\mathrm{score}(x_i,x_j))\ \ \forall j\le i$$

- **Somma pesata**: l'output $a_i$ è una combinazione degli input $x_j$ con $j\le i$; $\alpha_{ij}$ dice quanto $x_j$ contribuisce ad $a_i$.
- **Score**: la similarità fra $x_i$ e $x_j$ è il loro **prodotto scalare** ([L10](L10-semantica-vettoriale.md#p-24)): più è grande, più i vettori sono simili.
- **Pesi**: la **softmax** ([L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-7)), calcolata sui punteggi di $x_i$ con tutti gli $x_j$, $j\le i$, li trasforma in pesi fra 0 e 1 che sommano a 1.

In una frase: **confronta $x_i$ con i vettori precedenti, normalizza i punteggi, somma i vettori con questi pesi**. Poiché i pesi sommano a 1, $a_i$ è una media pesata: sta "in mezzo" ai vettori del contesto, spostato verso quelli più simili a $x_i$.

> **Da saper fare: La softmax di un vettore di punteggi**
>
> $\alpha_{ij} = \dfrac{\exp(\mathrm{score}(x_i,x_j))}{\sum_{k\le i}\exp(\mathrm{score}(x_i,x_k))}$: esponenziale di ogni punteggio diviso la somma degli esponenziali, solo sulle posizioni $k\le i$. Il denominatore è la stessa somma per tutti i $j$ della riga $i$.

<a id="p-19"></a>

### Slide 19 · Esercizio: attenzione semplificata

Esercizio in aula (3 minuti, carta e penna). Tre token con vettori giocattolo di dimensione 3: $x_1 = $ *chicken* $= [1,0,1]$, $x_2 = $ *road* $= [0,1,0]$, $x_3 = $ *it* $= [1,1,1]$. Aiuti: $e^1\approx2{,}72$, $e^2\approx7{,}39$, $e^3\approx20{,}09$.

1. i punteggi di *it*: $x_3\cdot x_1$, $x_3\cdot x_2$, $x_3\cdot x_3$;
2. i pesi $\alpha_{31},\alpha_{32},\alpha_{33}$: ogni $e^{\text{score}}$ diviso la somma dei tre;
3. l'output $a_3 = \alpha_{31}x_1+\alpha_{32}x_2+\alpha_{33}x_3$.

Domanda finale: quale token prende il peso maggiore? Provare prima di guardare la scheda successiva.

<a id="p-20"></a>

### Slide 20 · Attenzione semplificata: l'esempio svolto

Punteggi: $x_3\cdot x_1 = 1+0+1 = 2$, $x_3\cdot x_2 = 1$, $x_3\cdot x_3 = 3$. Softmax: $e^2+e^1+e^3 = 7{,}39+2{,}72+20{,}09 = 30{,}19$, quindi pesi $7{,}39/30{,}19 = 0{,}24$, $2{,}72/30{,}19 = 0{,}09$, $20{,}09/30{,}19 = 0{,}67$ (il grafico a barre a destra li mostra).

Output: $a_3 = 0{,}24\,[1,0,1] + 0{,}09\,[0,1,0] + 0{,}67\,[1,1,1] = [0{,}91;\ 0{,}76;\ 0{,}91]$.

Il peso maggiore va a *it* stesso: **un vettore è molto simile a se stesso**. È il difetto della versione semplificata: con lo score $x_i\cdot x_j$ il token tende a guardare sé stesso, e non c'è nulla da imparare (nessun parametro). La testa di attenzione risolve entrambe le cose con le proiezioni query, key, value.

> **Da saper fare: Verifica dei conti**
>
> Calcolati in Python (cella 1 del notebook): pesi esatti $0{,}2447;\ 0{,}0900;\ 0{,}6652$, $a_3 = [0{,}910;\ 0{,}755;\ 0{,}910]$. Con i pesi arrotondati a due cifre: $0{,}24+0{,}67 = 0{,}91$ e $0{,}09+0{,}67 = 0{,}76$, i numeri della slide.

> **Approfondimento: Si guarda sempre se stessi?**
>
> Non necessariamente: $x_i\cdot x_i = \|x_i\|^2$, ma un altro vettore più lungo e orientato in modo simile può avere prodotto scalare maggiore. Esempio dell'esercizio 2 della scheda: $x_1 = [1,2]$, $x_2 = [0,1]$; per $x_2$ i punteggi sono $x_2\cdot x_1 = 2 > x_2\cdot x_2 = 1$, quindi $a_2$ dà più peso a $x_1$.

## La testa di attenzione

<a id="p-21"></a>
**Slide 21 · La testa di attenzione: query, key, value** — Si aggiungono i parametri: tre proiezioni per tre ruoli diversi.

<a id="p-22"></a>

### Slide 22 · Tre ruoli per ogni vettore di input

Nella testa di attenzione ogni vettore di input gioca **tre ruoli diversi**:

- **Query**: l'elemento *corrente*, che viene confrontato con gli input precedenti;
- **Key**: un input precedente, nel ruolo di ciò che *viene confrontato* con l'elemento corrente per ottenere un peso di similarità;
- **Value**: un elemento precedente, nel ruolo di ciò che viene *pesato e sommato* per calcolare l'output.

L'analogia è la ricerca in un archivio: la query si confronta con ogni chiave, e si restituiscono i valori delle chiavi che corrispondono meglio, pesati. Nella versione semplificata lo stesso $x_j$ faceva da chiave e da valore, e $x_i$ da query: separare i ruoli permette di cercare una cosa (es. "un nome che possa essere il referente") e restituirne un'altra (l'informazione utile di quel nome).

Nota lessicale: **head** (testa) nei transformer è uno strato strutturato specifico, non la parte finale della rete; non va confusa con la *language modeling head*.

<a id="p-23"></a>

### Slide 23 · Vettori query, key e value

Tre **matrici di pesi** imparate nel training proiettano $x_i$ (riga $[1\times d]$) nei suoi tre ruoli:

$$q_i = x_i W^Q \qquad k_i = x_i W^K \qquad v_i = x_i W^V$$

La figura mostra un solo $x_i$ che si divide in tre frecce verso $W^Q$, $W^K$, $W^V$ e produce $q_i$, $k_i$, $v_i$. Ogni token calcola tutti e tre, ma li userà in momenti diversi: la query solo quando è lui il token corrente, key e value quando è guardato dai token successivi (e da se stesso).

Le matrici sono **le stesse per tutte le posizioni** di quello strato: è come lo strato di embedding o una feedforward applicata a ogni token. Come sempre nel libro i vettori sono righe e si moltiplica a destra: $xW$, non $Wx$.

<a id="p-24"></a>

### Slide 24 · La testa di attenzione: punteggi scalati

Le equazioni complete della testa, con evidenziate le prime due:

$$q_i = x_iW^Q;\ k_j = x_jW^K;\ v_j = x_jW^V \qquad \mathrm{score}(x_i,x_j) = \frac{q_i\cdot k_j}{\sqrt{d_k}}$$

- tre proiezioni di ogni input;
- il confronto ora è fra la **query di $x_i$** e la **key di $x_j$**, con un prodotto scalare: non è più simmetrico ($q_i\cdot k_j \ne q_j\cdot k_i$ in generale) e non premia automaticamente il token stesso;
- il prodotto si divide per $\sqrt{d_k}$, dove $d_k$ è la dimensione di $q$ e $k$: è lo **scaled dot product**.

Perché dividere: un prodotto scalare è una somma di $d_k$ termini, quindi cresce con $d_k$. Con componenti indipendenti di media 0 e varianza 1 la sua varianza è $d_k$ e la deviazione standard $\sqrt{d_k}$ (8 per $d_k = 64$). Punteggi così grandi rendono la softmax quasi one-hot, e i gradienti quasi nulli: problemi numerici nel training. Dividendo per $\sqrt{d_k}$ la scala torna circa 1.

> **Approfondimento: Il conto della varianza**
>
> Se $q_m, k_m$ sono indipendenti con media 0 e varianza 1, ogni prodotto $q_m k_m$ ha media 0 e varianza 1, e la somma di $d_k$ termini indipendenti ha varianza $d_k$. Il notebook (cella 3) lo verifica: deviazione standard 2,00; 4,02; 8,03; 15,97 per $d_k = 4, 16, 64, 256$, tutte 1,00 dopo la divisione. Softmax di $[1,0]$: $[0{,}73;\ 0{,}27]$; di $[8,0]$: $[0{,}9997;\ 0{,}0003]$.

<a id="p-25"></a>

### Slide 25 · La testa di attenzione: pesi, somma e W^O

Le tre equazioni restanti (evidenziate in questa slide):

$$\alpha_{ij} = \mathrm{softmax}(\mathrm{score}(x_i,x_j))\ \forall j\le i \qquad \mathrm{head}_i = \sum_{j\le i}\alpha_{ij} v_j \qquad a_i = \mathrm{head}_i\, W^O$$

- la **softmax**, come prima: pesi che sommano a 1 sulle posizioni $j\le i$;
- una somma pesata dei **value** (non più degli $x_j$);
- $W^O$ riporta l'output della testa alla forma $[1\times d]$, quella dell'input.

Frase della slide: **ogni value è pesato dalla similarità della sua key con la query dell'elemento corrente**. Da ricordare la divisione dei compiti: query e key decidono *quanto* guardare ogni token, i value decidono *che cosa* se ne prende.

<a id="p-26"></a>

### Slide 26 · Calcolare a3 passo per passo: passo 1

La figura del libro mostra in otto passi il calcolo di $a_3$, l'output della posizione 3, con tre input $x_1, x_2, x_3$ di forma $[1\times d]$ in basso. Il riquadro evidenzia il **passo 1**: ogni input passa per $W^K$, $W^Q$, $W^V$ e genera i suoi vettori **key, query, value**.

Sono calcolati per tutti e tre i token, ma della query serve solo quella di $x_3$ (il token corrente); di $x_1$ e $x_2$ servono key e value. In un modello causale le key e i value dei token passati non cambiano quando arriva un token nuovo: per questo in generazione si possono tenere in memoria (KV cache, cenno utile per l'orale).

<a id="p-27"></a>

### Slide 27 · Calcolare a3 passo per passo: passi 2-4

Il riquadro ora copre i passi centrali:

- **passo 2**: la **query di $x_3$** si confronta con le **key di $x_1, x_2, x_3$** (tre prodotti scalari, i rombi verdi);
- **passo 3**: ogni punteggio scalare si divide per $\sqrt{d_k}$;
- **passo 4**: la softmax trasforma i tre punteggi nei pesi $\alpha_{3,1}, \alpha_{3,2}, \alpha_{3,3}$ (la barra orizzontale che collega i tre nodi: la softmax ha bisogno di tutti i punteggi insieme per normalizzare).

Fin qui sono tutte quantità scalari, una per coppia (token corrente, token del contesto): la forma $[1\times d_k]$ indicata vicino alle frecce è quella delle key e query in ingresso ai prodotti.

<a id="p-28"></a>

### Slide 28 · Calcolare a3 passo per passo: passi 5-8

La parte alta della figura:

- **passo 5**: ogni **value** $v_j$ ($[1\times d_v]$) viene moltiplicato per il suo peso $\alpha_{3,j}$;
- **passo 6**: i tre value pesati si **sommano** ($\Sigma$): è $\mathrm{head}_3$, di forma $[1\times d_v]$;
- **passo 7**: $W^O$, di forma $[d_v\times d]$, riporta il risultato a $[1\times d]$;
- **passo 8**: l'output della self-attention, $a_3$.

Per l'orale saper ripetere gli otto passi nell'ordine, con le forme: genera $q,k,v$; confronta query e key; scala; softmax; pesa i value; somma; proietta con $W^O$; output.

<a id="p-29"></a>

### Slide 29 · Le forme in una testa di attenzione

Input e output hanno la stessa dimensione $[1\times d]$: per questo il transformer è **molto modulare**, i pezzi si impilano senza adattatori.

| oggetto | forma |
| --- | --- |
| $x_i$ | $[1\times d]$, l'input |
| $W^Q, W^K$ | $[d\times d_k]$ |
| $W^V$ | $[d\times d_v]$ |
| $q_i, k_j$ | $[1\times d_k]$: il loro prodotto scalare è uno scalare |
| $\mathrm{head}_i$ | $[1\times d_v]$: somma pesata dei value |
| $W^O$ | $[d_v\times d]$ |
| $a_i$ | $[1\times d]$, l'output |

Nel transformer originale: $d = 512$ (la **dimensione del modello**), $d_k = d_v = 64$. Query e key devono avere la stessa dimensione $d_k$ (si fa il prodotto scalare); $d_v$ può essere diversa, perché i value si sommano e basta.

<a id="p-30"></a>

### Slide 30 · Una testa a mano: l'input

Numeri giocattolo, non imparati: $d = 3$, $d_k = d_v = 2$. Gli stessi tre token di prima, $x_1 = [1,0,1]$, $x_2 = [0,1,0]$, $x_3 = [1,1,1]$, e tre matrici $[3\times 2]$:

$$W^Q = \begin{bmatrix}1&0\\0&-1\\1&0\end{bmatrix}\quad W^K = \begin{bmatrix}1&0\\0&1\\0&0\end{bmatrix}\quad W^V = \begin{bmatrix}1&0\\0&1\\0&1\end{bmatrix}$$

Si calcola l'output per *it*, il terzo token. Ogni matrice trasforma un vettore di 3 numeri in uno di 2. Regola pratica per $xW$: **ogni componente di $x$ moltiplica una riga di $W$, e le righe si sommano**. Con input fatti di 0 e 1 basta sommare le righe corrispondenti agli 1.

Esercizio in aula (3 minuti): calcolare $q_3 = x_3W^Q$, le key $k_1, k_2, k_3$ e i value $v_1, v_2, v_3$.

<a id="p-31"></a>

### Slide 31 · Una testa a mano: query, key, value

Con la regola delle righe:

- $q_3 = x_3W^Q = [1,0]+[0,-1]+[1,0] = [2,-1]$ (tutte e tre le righe, perché $x_3 = [1,1,1]$);
- key: $k_1 = x_1W^K = [1,0]+[0,0] = [1,0]$, $k_2 = [0,1]$, $k_3 = [1,0]+[0,1]+[0,0] = [1,1]$;
- value: $v_1 = x_1W^V = [1,0]+[0,1] = [1,1]$, $v_2 = [0,1]$, $v_3 = [1,2]$.

Messaggio della slide: **la query solo per il token corrente; key e value per tutti i token fino a lui**. Si noti che $W^K$ ignora la terza componente (ultima riga nulla): due vettori che differiscono solo lì hanno la stessa key.

<a id="p-32"></a>

### Slide 32 · Una testa a mano: punteggi e pesi

Punteggi $q_3\cdot k_j$ con $q_3 = [2,-1]$: $q_3\cdot k_1 = 2$, $q_3\cdot k_2 = -1$, $q_3\cdot k_3 = 2-1 = 1$.

- diviso $\sqrt{d_k} = \sqrt2$: $1{,}41;\ -0{,}71;\ 0{,}71$;
- esponenziali: $4{,}11;\ 0{,}49;\ 2{,}03$, somma $6{,}63$;
- pesi: $0{,}62;\ 0{,}07;\ 0{,}31$ (grafico a barre a destra).

Ora ***it* guarda soprattutto *chicken*, non se stesso**: le proiezioni hanno cambiato chi è simile a chi. Con la versione semplificata il peso maggiore andava a *it* (0,67), qui a *chicken* (0,62). Le matrici sono inventate, ma il punto è generale: $W^Q$ e $W^K$ imparano *quale* similarità conta per il compito.

> **Da saper fare: Verifica**
>
> Ricalcolato (cella 2 del notebook): punteggi scalati $1{,}414;\ -0{,}707;\ 0{,}707$, esponenziali $4{,}113;\ 0{,}493;\ 2{,}028$ (somma 6,634), pesi $0{,}620;\ 0{,}074;\ 0{,}306$. Tutti i numeri della slide tornano.

<a id="p-33"></a>

### Slide 33 · Una testa a mano: l'output

Somma pesata dei value:

$$\mathrm{head}_3 = 0{,}62\,[1,1] + 0{,}07\,[0,1] + 0{,}31\,[1,2] = [0{,}93;\ 1{,}31]$$

Poi $W^O = \begin{bmatrix}1&0&0\\0&1&1\end{bmatrix}$, di forma $[d_v\times d] = [2\times3]$: copia la prima componente e duplica la seconda, quindi $a_3 = \mathrm{head}_3W^O = [0{,}93;\ 1{,}31;\ 1{,}31]$, con $d = 3$ numeri come l'input.

I due casi estremi aiutano a leggere il risultato: con tutto il peso su *it*, $a_3 = v_3W^O = [1,2,2]$; con tutto il peso su *chicken*, $a_3 = v_1W^O = [1,1,1]$. L'output vero sta in mezzo, più vicino al secondo: il **62% dell'output di *it* viene dal value di *chicken***.

> **Da saper fare: Verifica**
>
> Esatto: $\mathrm{head}_3 = [0{,}926;\ 1{,}306]$ e $a_3 = [0{,}926;\ 1{,}306;\ 1{,}306]$ (cella 2 del notebook), arrotondati come nella slide. Con i pesi arrotondati: $0{,}62+0{,}31 = 0{,}93$ e $0{,}62+0{,}07+0{,}62 = 1{,}31$.

<a id="p-34"></a>
**Slide 34 · Pausa** — Dieci minuti; dopo: multi-head attention, il transformer block, tutti i token insieme.

## Multi-head attention

<a id="p-35"></a>
**Slide 35 · Multi-head attention** — Più teste in parallelo, ognuna con le sue matrici.

<a id="p-36"></a>

### Slide 36 · Perché più teste

I transformer usano **più teste di attenzione**: ogni testa può guardare il contesto **per uno scopo diverso**.

- **Teste specializzate**: una testa può rappresentare una particolare relazione linguistica fra il contesto e il token corrente (es. soggetto-verbo, pronome-referente), oppure cercare un certo tipo di pattern nel contesto (es. il token precedente, una ripetizione).
- **Parametri propri**: $A$ teste in parallelo, alla stessa profondità del modello; la testa $c$ ha le sue matrici $W^{Qc}, W^{Kc}, W^{Vc}$.

Il motivo di fondo: una testa produce **una sola distribuzione di pesi** per token. Se *it* deve contemporaneamente trovare il suo referente e controllare l'accordo col verbo, una sola softmax deve fare un compromesso; con più teste ogni relazione ha la sua distribuzione.

<a id="p-37"></a>

### Slide 37 · Multi-head attention con A = 4: le teste

La figura del libro: in basso l'input $x_i$ $[1\times d]$ e i token precedenti $x_{i-1}, x_{i-2}, x_{i-3},\dots$ collegati con linee tratteggiate a quattro triangoli, **Head 1-4**, ognuno con le sue $W^{Kc}, W^{Vc}, W^{Qc}$. Il riquadro evidenzia le teste: "each head attends differently to context".

Ogni testa fa esattamente il calcolo della scheda 25 con le sue matrici e produce un output di forma $[1\times d_v]$, la barretta sopra ogni triangolo. Le quattro teste lavorano in parallelo sugli stessi input e non si scambiano informazione fra loro.

<a id="p-38"></a>

### Slide 38 · Multi-head attention con A = 4: concatenazione e proiezione

La parte alta della figura: i quattro output $[1\times d_v]$ si **concatenano** (frecce rosa) in un vettore $[1\times Ad_v]$ ("here A=4"); poi $W^O$, di forma $[Ad_v\times d]$, li **proietta** alla rappresentazione finale $a_i$ di forma $[1\times d]$.

Annotazione della figura: di solito $d_v = d/A$, quindi $W^O$ è $[d\times d]$. $W^O$ non serve solo a sistemare la forma: ogni componente di $a_i$ è una combinazione lineare di **tutte** le teste, quindi è qui che i risultati delle teste si mescolano. Senza $W^O$ (con $Ad_v = d$) le teste resterebbero in blocchi separati di componenti.

<a id="p-39"></a>

### Slide 39 · Multi-head attention: le equazioni

Per ogni testa $c$ da 1 ad $A$ le equazioni di una testa, con l'indice $c$:

$$q_i^c = x_iW^{Qc};\ k_j^c = x_jW^{Kc};\ v_j^c = x_jW^{Vc} \qquad \mathrm{score}^c(x_i,x_j) = \frac{q_i^c\cdot k_j^c}{\sqrt{d_k}}$$$$\alpha_{ij}^c = \mathrm{softmax}(\mathrm{score}^c(x_i,x_j))\ \forall j\le i \qquad \mathrm{head}_i^c = \sum_{j\le i}\alpha_{ij}^c v_j^c$$$$a_i = (\mathrm{head}^1\oplus\mathrm{head}^2\oplus\dots\oplus\mathrm{head}^A)\,W^O \qquad \mathrm{MultiHeadAttention}(x_i,[x_1,\dots,x_{i-1}]) = a_i$$

$\oplus$ è la **concatenazione** degli $A$ output, poi $W^O$. La notazione dell'ultima riga ricorda che il risultato dipende da $x_i$ e dagli input alla sua sinistra. Messaggio: **$A$ teste, stesse equazioni, matrici diverse**. $W^O$ è una sola, condivisa, dopo la concatenazione.

<a id="p-40"></a>

### Slide 40 · Quanti parametri

- **Dimensione di una testa**: di solito $d_v = d/A$ (e $d_k = d_v$), così $W^O$ è quadrata, $[Ad_v\times d] = [d\times d]$. Allora la multi-head costa in parametri **circa quanto una testa sola** di dimensione piena.
- **Transformer originale**: $d = 512$, $A = 8$, $d_k = d_v = 64$. Le $W^Q, W^K, W^V$ delle 8 teste: $3\times8\times(512\times64) = 3\times512\times512$; $W^O$: $512\times512$. Totale $4\times512^2 = 1.048.576$ pesi.

Circa **un milione di pesi per l'attenzione di uno strato** (senza bias). In generale con $d_k = d_v = d/A$: $3\cdot A\cdot d\cdot\frac dA + d^2 = 4d^2$, indipendentemente da $A$. Una testa sola con $d_k = d_v = d$ avrebbe $3d^2 + d^2 = 4d^2$: lo stesso numero. Dividere in teste cambia *come* si usano i parametri, non quanti sono.

> **Da saper fare: Contare i pesi dell'attenzione**
>
> Formula da saper scrivere: $3Ad\,d_k + Ad_v\,d$; con $d_k = d_v = d/A$ diventa $4d^2$. Esempi: $d = 512$: 1.048.576; $d = 768$ (12 teste da 64, esercizio 4): $4\cdot768^2 = 2.359.296$.

## Il transformer block

<a id="p-41"></a>
**Slide 41 · Il transformer block** — Attenzione, feedforward, layer norm e residual stream.

<a id="p-42"></a>

### Slide 42 · Il transformer block: quattro componenti

La figura: tre colonne verticali (le residual stream dei token $i-2$, $i-1$, $i$), dal basso $x$ all'alto $h$. Sulla colonna di $x_i$ si innesta il blocco: Layer Norm, MultiHead Attention (che riceve con frecce tratteggiate anche dalle colonne a sinistra), un $\oplus$, poi Layer Norm, Feedforward e un altro $\oplus$; in cima esce $h_i$.

Quattro componenti:

- **self-attention**: la multi-head attention;
- **strato feedforward**;
- **connessioni residue**;
- **layer norm**: strati di normalizzazione.

Tre dei quattro sono già noti dalla L13 (feedforward, residue, normalizzazione: [scheda 66](L13-reti-neurali.md#p-66) e [67](L13-reti-neurali.md#p-67)); il nuovo è l'attenzione. Le prossime schede seguono il percorso di un vettore lungo la colonna.

<a id="p-43"></a>

### Slide 43 · La residual stream

Il riquadro evidenzia la colonna del token $i$: la **residual stream**.

- una sola corrente di vettori $d$-dimensionali per la posizione $i$;
- parte dal vettore di input $x_i$;
- i componenti **leggono** dalla corrente e **aggiungono** il loro output.

Il modo di pensare proposto (Elhage et al., 2021, citato dal libro): non una catena di trasformazioni dove ogni strato sostituisce il vettore, ma un "canale" condiviso dove ogni componente scrive un contributo additivo. Conseguenze: il vettore conserva l'informazione originale del token, e il gradiente ha una strada diretta dall'output all'input (la ragione per cui le connessioni residue rendono addestrabili reti profonde, L13).

<a id="p-44"></a>

### Slide 44 · Il transformer block: prima metà

Il riquadro è sulla parte bassa del blocco: **layer norm, poi multi-head attention**; il risultato viene **aggiunto nella corrente**, cioè sommato a $x_i$.

$$t_i^3 = x_i + \mathrm{MultiHeadAttention}(\mathrm{LayerNorm}(x_i), \dots)$$

La layer norm agisce sulla copia letta dalla corrente, non sulla corrente stessa: nella colonna resta $x_i$ non normalizzato, a cui si somma l'output dell'attenzione. Le frecce tratteggiate ricordano che l'attenzione prende anche le rappresentazioni (normalizzate) dei token a sinistra.

<a id="p-45"></a>

### Slide 45 · Il transformer block: seconda metà

Il riquadro è sulla parte alta: **layer norm, poi lo strato feedforward**; il risultato si somma alla corrente e dà $h_i$, l'**output del blocco**.

$$h_i = t_i^3 + \mathrm{FFN}(\mathrm{LayerNorm}(t_i^3))$$

Nota in fondo alla slide: **prenorm**, le layer norm vengono *prima* di attenzione e feedforward. Il transformer originale (Vaswani et al., 2017) era **postnorm**: normalizzava dopo la somma residua. La variante prenorm è quella usata oggi perché si addestra in modo più stabile: la corrente residua resta una somma "pulita" e il gradiente la attraversa senza passare per le normalizzazioni.

<a id="p-46"></a>

### Slide 46 · Lo strato feedforward

- **Due strati**: una rete completamente connessa con uno strato nascosto e due matrici di pesi, $\mathrm{FFN}(x) = \mathrm{ReLU}(xW_1+b_1)W_2+b_2$ (la rete della L13).
- **Position-wise**: lavora su ogni posizione **indipendentemente**, non mescola le posizioni. Stessi pesi in ogni posizione, pesi diversi da uno strato all'altro.
- $d_{ff} = 4d$: lo strato nascosto è 4 volte più largo di $d$; nel transformer originale $512\to2048$.
- Contiene la **maggior parte dei parametri** del transformer, e sembra codificare gran parte della sua **conoscenza fattuale** (Geva et al., 2021; Meng et al., 2022).

Conto: $2\times512\times2048 = 2.097.152$ pesi, **il doppio dell'attenzione** dello stesso strato (1.048.576). In generale $2d\,d_{ff} = 8d^2$ contro $4d^2$: due terzi dei pesi di un blocco stanno nella feedforward.

> **Da saper fare: Verifica**
>
> $2\cdot512\cdot2048 = 2.097.152 = 2\times1.048.576$. Con i bias si aggiungono $2048+512$ parametri: 2.099.712 (esercizio 9).

<a id="p-47"></a>

### Slide 47 · Feedforward con gate: SwiGLU

La maggior parte degli LLM oggi usa strati feedforward **con gate**, con l'attivazione **SwiGLU** (Shazeer, 2020).

- **Swish**: $\mathrm{Swish}_\beta(x) = x\,\sigma(\beta x)$, un'attivazione liscia, $x$ per la sigmoide di $\beta x$. Il piccolo grafico mostra la forma: quasi zero per $x$ negativi (con un leggero avvallamento sotto lo zero), circa lineare per $x$ positivi, come una ReLU smussata.
- **SwiGLU**: $\mathrm{FFN}_{\mathrm{SwiGLU}} = \big(\mathrm{Swish}_\beta(xW_1+b_1)\otimes(xW_2+b_2)\big)W_3+b_3$.

Due trasformazioni lineari dello stesso input, la prima passata per Swish, moltiplicate **componente per componente** ($\otimes$): una è un **valore**, l'altra un **gate** che dice quanto di quel valore passa. Le matrici ora sono tre, quindi $d_{ff}$ si sceglie di solito un po' meno di $4d$ per non aumentare i parametri (con $d_{ff} = \frac23\cdot4d$ i pesi tornano $8d^2$).

<a id="p-48"></a>

### Slide 48 · Layer norm

La **layer norm** è una variante dello **z-score** applicata al vettore di **un token**.

Esempio: $x = [2,4,6,8]$. Media $\mu = 5$; deviazione standard $\sigma = \sqrt{(9+1+1+9)/4} = \sqrt5\approx2{,}24$. Si sottrae la media e si divide per $\sigma$: $[-3,-1,1,3]/2{,}24 = [-1{,}34;\ -0{,}45;\ 0{,}45;\ 1{,}34]$. I due grafici a barre mostrano il vettore prima (con la linea $\mu = 5$) e dopo (media 0, deviazione standard 1).

Non si applica a un intero strato ma solo al vettore di embedding di un token: $d$ numeri in ingresso, $d$ in uscita. Il nome è fuorviante: "layer" si riferisce alle componenti di un vettore nascosto, non a un batch di esempi (quella è la batch norm).

> **Da saper fare: Attenzione al denominatore**
>
> Nel libro e nel notebook la varianza usa $\frac1d$ (deviazione standard di popolazione): per $[2,4,6,8]$, $\sigma = \sqrt5 = 2{,}236$. Con $\frac1{d-1}$ verrebbe 2,58 e i valori normalizzati cambierebbero: allo scritto usare $\frac1d$.

<a id="p-49"></a>

### Slide 49 · Layer norm: le equazioni

$$\mu = \frac1d\sum_{j=1}^d x[j] \qquad \sigma = \sqrt{\frac1d\sum_{j=1}^d (x[j]-\mu)^2} \qquad \hat x = \frac{x-\mu}{\sigma}$$$$\mathrm{LayerNorm}(x) = \gamma\,\frac{x-\mu}{\sigma} + \beta$$

- media e deviazione standard sulle $d$ componenti del vettore $x$;
- $\hat x$ ha media zero e deviazione standard uno;
- $\gamma$ (**gain**) e $\beta$ (**offset**) sono due parametri **imparabili** che ridanno al modello la libertà di scegliere scala e centro.

Molte reti moderne usano **RMSNorm**: divide per la radice della media dei quadrati, $\sqrt{\frac1d\sum_j x[j]^2}$, senza sottrarre la media (meno conti, risultati simili). Per $[2,4,6,8]$: $\mathrm{RMS} = \sqrt{30} = 5{,}48$, output $[0{,}37;\ 0{,}73;\ 1{,}10;\ 1{,}46]$.

> **Approfondimento: Che cosa toglie la layer norm**
>
> $\hat x$ non cambia se si moltiplica $x$ per una costante positiva o si somma una costante: $\mathrm{LN}(ax+b) = \mathrm{LN}(x)$ per $a > 0$. Il notebook lo mostra con $10x+5$ (cella 6). La layer norm tiene la "forma" del vettore e toglie scala e spostamento, che sono quelli che crescono in modo incontrollato nelle reti profonde.

> **Da saper fare: Gain e offset per componente**
>
> Nel libro $\gamma$ e $\beta$ sono vettori di dimensione $d$ (uno per componente), quindi ogni layer norm ha $2d$ parametri: con $d = 512$ due layer norm per blocco fanno $2\cdot2\cdot512 = 2048$ parametri (esercizio 9).

<a id="p-50"></a>

### Slide 50 · Tutto insieme

Le equazioni di un blocco per il token $i$, con variabili intermedie $t$:

$$\begin{aligned} t_i^1 &= \mathrm{LayerNorm}(x_i)\\ t_i^2 &= \mathrm{MultiHeadAttention}(t_i^1, [t_1^1,\dots,t_{i-1}^1])\\ t_i^3 &= t_i^2 + x_i\\ t_i^4 &= \mathrm{LayerNorm}(t_i^3)\\ t_i^5 &= \mathrm{FFN}(t_i^4)\\ h_i &= t_i^5 + t_i^3 \end{aligned}$$

Layer norm dell'input; attenzione sul token $i$ e su quelli precedenti (anch'essi normalizzati); somma nella corrente; layer norm; feedforward; somma: l'output $h_i$. **Attenzione e feedforward aggiungono ciascuno il proprio output alla corrente**.

> **Da saper fare: h come somma di tre termini**
>
> Sostituendo: $h_i = x_i + t_i^2 + t_i^5$, cioè l'input più il contributo dell'attenzione più quello della feedforward. È la lettura "residual stream" in formula (esercizio 10).

<a id="p-51"></a>

### Slide 51 · L'attenzione mescola i token

La figura: cinque colonne grigie (le residual stream di cinque token) e una freccia rossa che parte dalla corrente del token A, attraversa le colonne e sale nella corrente del token B.

- l'attenzione è **l'unico componente** che prende in input informazione da **altri token**; layer norm e feedforward lavorano su una posizione alla volta;
- il suo output viene aggiunto nella corrente del token **corrente**;
- una testa di attenzione può quindi **spostare informazione** dalla corrente del token A a quella del token B (Elhage et al., 2021).

Conclusione: **ogni corrente contiene informazione sul suo token e sui token vicini**. Il notebook (cella 7) ne fa una verifica: cambiando l'ultimo token, gli output dei token precedenti non cambiano, perché la sola via fra posizioni è l'attenzione ed è causale.

<a id="p-52"></a>

### Slide 52 · Impilare i blocchi

- **Stessa forma**: input $x_i$ e output $h_i$ hanno dimensione $d$, quindi i blocchi si possono impilare (l'output di uno è l'input del successivo).
- **Quanti**: da 12 blocchi (T5, GPT-3 small) a 96 (GPT-3 175B), di più nei modelli recenti.
- **Che cosa contiene la corrente**: nei blocchi bassi soprattutto il token **corrente**; nei blocchi più alti di solito il token **successivo**, perché alla fine il modello è addestrato a predirlo.
- **Un'ultima layer norm** alla fine dell'ultimo blocco, prima della testa di language modeling (nel prenorm l'output dell'ultimo blocco non è normalizzato).

Il terzo punto è un modo utile di pensare: la stessa corrente parte come "embedding del token $i$" e arriva come "rappresentazione di ciò che viene dopo $i$", pronta per l'unembedding.

> **Approfondimento: T5 a 12 strati**
>
> T5 è un modello encoder-decoder: nella versione base ha 12 blocchi nell'encoder e 12 nel decoder. Il "12" della slide (e del libro) si riferisce alla profondità di ciascuna pila.

## Tutti i token insieme

<a id="p-53"></a>
**Slide 53 · Tutti i token insieme** — Una matrice $X$ per l'intera sequenza.

<a id="p-54"></a>

### Slide 54 · La matrice di input X

Si impilano gli $N$ embedding di input in una matrice $X$ di forma $[N\times d]$, **una riga per token**. Allora

$$Q = XW^Q \qquad K = XW^K \qquad V = XW^V$$

con $Q, K$ di forma $[N\times d_k]$ e $V$ di forma $[N\times d_v]$: la riga $i$ di $Q$ è $q_i$, e così via. La figura mostra i tre prodotti con le righe colorate (Input Token 1-4, Query Token 1-4, ...).

Il calcolo per ogni token è indipendente da quello degli altri (a parità di strato): si possono fare tutti insieme, con moltiplicazioni di matrici efficienti su GPU. $N$, la lunghezza del contesto, può arrivare a centinaia di migliaia di token nei modelli recenti.

<a id="p-55"></a>

### Slide 55 · Tutti i confronti insieme: QKᵀ

$Q$ ha una query per riga, $K^\top$ una key per colonna: il prodotto $QK^\top$, di forma $[N\times d_k]\cdot[d_k\times N] = [N\times N]$, contiene **tutti i prodotti scalari** fra una query e una key.

- elemento $(i,j) = q_ik_j^\top$: la query del token $i$ contro la key del token $j$;
- riga $i$: la query del token $i$ contro le key di tutti i token. In tutto $N\times N$ punteggi.

La figura evidenzia la riga di $q_3$ e la colonna di $k_2$, che si incontrano nella cella $q_3k_2^\top$. Una sola moltiplicazione di matrici sostituisce $N^2$ prodotti scalari separati.

<a id="p-56"></a>

### Slide 56 · Mascherare il futuro

$QK^\top$ confronta ogni query anche con le key dei token **successivi**: indovinare la parola dopo è facile se la si conosce già. In training sarebbe un imbroglio, e in generazione quei token non esistono ancora.

Soluzione: una **matrice maschera** $M$ $[N\times N]$ con $-\infty$ **sopra la diagonale** ($j > i$, i token successivi) e 0 altrove:

$$\mathrm{mask}(QK^\top) = QK^\top + M, \qquad M_{ij} = \begin{cases}0 & j\le i\\ -\infty & j > i\end{cases}$$

I punteggi contro i token successivi diventano $-\infty$, e la softmax li trasforma in 0 ($e^{-\infty} = 0$): **nessuna informazione dai token successivi**. La matrice risultante (a destra nella figura) è triangolare inferiore. Si maschera *prima* della softmax, così i pesi rimasti sommano ancora a 1.

> **Approfondimento: Perché non azzerare dopo la softmax**
>
> Azzerando i pesi dopo la softmax le righe non sommerebbero più a 1 (bisognerebbe rinormalizzare). Sommare $-\infty$ prima equivale esattamente a fare la softmax solo sulle posizioni $j\le i$, come nelle formule per un token. In pratica si usa un numero molto negativo o $-\infty$ con una softmax stabile (sottrazione del massimo, come nel notebook).

<a id="p-57"></a>

### Slide 57 · Il nostro esempio in forma matriciale: QKᵀ

Gli stessi tre token *chicken, road, it*, con query e key calcolate a mano. Le query di tutti e tre: $q_1 = x_1W^Q = [1,0]+[1,0] = [2,0]$, $q_2 = [0,-1]$, $q_3 = [2,-1]$. Le key come prima.

$$Q = \begin{bmatrix}2&0\\0&-1\\2&-1\end{bmatrix}\quad K^\top = \begin{bmatrix}1&0&1\\0&1&1\end{bmatrix}\quad QK^\top = \begin{bmatrix}2&0&2\\0&-1&-1\\2&-1&1\end{bmatrix}$$

Ogni elemento di $QK^\top$ è una riga di $Q$ per una colonna di $K^\top$. Riga 3, colonna 1: $q_3k_1^\top = 2\cdot1+(-1)\cdot0 = 2$, il punteggio di *it* contro *chicken*. La riga 3, $(2,-1,1)$, contiene i punteggi di *it* calcolati nella scheda 32.

<a id="p-58"></a>

### Slide 58 · Il nostro esempio in forma matriciale: maschera e softmax

Quattro passi sulla matrice:

- **dividere** per $\sqrt{d_k} = \sqrt2$: righe $(1{,}41;\ 0;\ 1{,}41)$, $(0;\ -0{,}71;\ -0{,}71)$, $(1{,}41;\ -0{,}71;\ 0{,}71)$;
- **sommare $M$**: i punteggi contro i token successivi diventano $-\infty$ (due nella riga 1, uno nella riga 2);
- **softmax per riga**: $-\infty$ diventa 0. Riga 1: $(1, 0, 0)$, *chicken* può guardare solo se stesso; riga 2: $e^0/(e^0+e^{-0{,}71}) = 1/1{,}49 = 0{,}67$ e $0{,}33$; riga 3: $(0{,}62;\ 0{,}07;\ 0{,}31)$, i pesi di *it* già trovati.

**Un prodotto di matrici, una maschera e una softmax danno i pesi di tutti i token** in un colpo solo. Si noti che senza la maschera la riga 1 avrebbe dato peso anche a *road* e *it*, che vengono dopo.

> **Da saper fare: Verifica**
>
> Ricalcolato (cella 4 del notebook): pesi per riga $(1;0;0)$, $(0{,}670;\ 0{,}330;\ 0)$, $(0{,}620;\ 0{,}074;\ 0{,}306)$; e ogni riga dell'output coincide con il calcolo posizione per posizione. Righe dell'output $A$: $[1,1,1]$, $[0{,}67;\ 1;\ 1]$, $[0{,}93;\ 1{,}31;\ 1{,}31]$.

<a id="p-59"></a>

### Slide 59 · Una testa in forma matriciale

$$\mathrm{head} = \mathrm{softmax}\Big(\mathrm{mask}\Big(\frac{QK^\top}{\sqrt{d_k}}\Big)\Big)V \qquad A = \mathrm{head}\,W^O$$

- $\mathrm{head}$: $[N\times N]\cdot[N\times d_v] = [N\times d_v]$, una riga per token;
- $A$: $[N\times d]$, l'output per ogni token.

La figura (del libro) mostra la catena per $N = 4$: $Q$ per $K^\top$ dà la matrice $N\times N$ dei $q_i\cdot k_j$; la maschera mette $-\infty$ sopra la diagonale; il risultato moltiplica $V$ e dà le righe $a_1,\dots,a_4$. Scala e softmax non sono disegnate, come dice la didascalia.

È l'equazione più importante della lezione: va saputa scrivere con le forme di ogni fattore.

> **Approfondimento: La A della figura e la A del testo**
>
> Nella figura la matrice finale si chiama $A$ ma ha forma $N\times d_v$: è l'output della testa *prima* di $W^O$ (che la figura non disegna), cioè $\mathrm{head}$. La $A$ dell'equazione è $\mathrm{head}\,W^O$, di forma $[N\times d]$. Le due coincidono solo se $W^O$ è l'identità ($d_v = d$). La figura è quella del libro, con la stessa etichetta.

<a id="p-60"></a>

### Slide 60 · Il costo dell'attenzione

- **Quadratico**: a ogni strato servono $N\times N$ prodotti scalari, uno per ogni coppia di token dell'input;
- costoso per documenti molto lunghi, come romanzi interi.

Esempi: $N = 1.000$ token, $1.000\times1.000 = 10^6$ punteggi (un milione); $N = 100.000$ token, $10^{10}$ punteggi (dieci miliardi). Raddoppiare il contesto quadruplica i punteggi.

E questo è il prezzo **per ogni testa di ogni strato**: il prezzo di guardare tutto il contesto. Con la maschera causale circa metà dei punteggi ($N(N+1)/2$) sono davvero usati, ma l'ordine resta $N^2$. Al contrario, il costo della feedforward cresce linearmente con $N$.

> **Approfondimento: Lineare in d, quadratico in N**
>
> Il numero di punteggi non dipende da $d$; ogni punteggio costa $d_k$ moltiplicazioni, quindi $QK^\top$ costa circa $N^2d_k$ per testa e $N^2d$ per strato (sommando sulle teste). Raddoppiare $d$ raddoppia questo costo e quadruplica i parametri ($4d^2+8d^2$); raddoppiare $N$ quadruplica i punteggi e lascia invariati i parametri (esercizio 12).

<a id="p-61"></a>

### Slide 61 · Multi-head attention in forma matriciale

$$Q^i = XW^{Qi};\ K^i = XW^{Ki};\ V^i = XW^{Vi}$$$$\mathrm{head}_i = \mathrm{SelfAttention}(Q^i,K^i,V^i) = \mathrm{softmax}\Big(\mathrm{mask}\Big(\frac{Q^iK^{i\top}}{\sqrt{d_k}}\Big)\Big)V^i$$$$\mathrm{MultiHeadAttention}(X) = (\mathrm{head}_1\oplus\mathrm{head}_2\oplus\dots\oplus\mathrm{head}_A)\,W^O$$

- ogni testa $i$ ha le sue $Q^i, K^i, V^i$ (qui $i$ indica la testa, non il token);
- ogni testa dà $[N\times d_v]$;
- concatenando: $[N\times Ad_v]$; $W^O$ riporta a $[N\times d]$.

**Input $X$ e output hanno entrambi forma $[N\times d]$**, come per un token solo: la versione matriciale è la stessa cosa della scheda 39, fatta per tutte le righe insieme.

<a id="p-62"></a>

### Slide 62 · Il transformer block in forma matriciale

$$O = X + \mathrm{MultiHeadAttention}(\mathrm{LayerNorm}(X)) \qquad H = O + \mathrm{FFN}(\mathrm{LayerNorm}(O))$$

- **L'input $X$**: per il primo strato, gli embedding iniziali dei token (più la posizione); per gli strati successivi, l'output $H$ dello strato precedente.
- **In parallelo**: la stessa feedforward e la stessa layer norm su ciascuno degli $N$ vettori (riga per riga).
- **Stessa forma**: $X$ e $H$ sono entrambi $[N\times d]$, quindi i blocchi si impilano.

Sono le equazioni 7.39-7.40 del libro, versione matriciale delle sei equazioni della scheda 50 ($O$ corrisponde a $t^3$). Un modello intero è: embedding + posizione, poi $L$ volte questo blocco, poi layer norm finale e testa di language modeling.

<a id="p-63"></a>

### Slide 63 · Riepilogo e prossima lezione

Riepilogo:

- **embedding contestuali**: un vettore per ogni token nel suo contesto;
- **attenzione**: una somma pesata del contesto, con pesi dalla softmax di prodotti scalari;
- **testa di attenzione**: query, key, value, scala $\sqrt{d_k}$, e $W^O$;
- **multi-head**: $A$ teste in parallelo, concatenate;
- **transformer block**: layer norm, attenzione, feedforward, residual stream;
- **forma matriciale**: $X$, $QK^\top$, la maschera sul futuro; costo quadratico.

Prossima lezione, **Transformers II** (ancora capitolo 7): embedding di posizione, la testa di language modeling e il decoding.

## Notebook

Commento al notebook del corso `HLT-L14-transformer-attention.ipynb` (il notebook è del docente e non è incluso).

Notebook di accompagnamento della lezione (solo `numpy`, nessuna rete, pochi secondi): rifà gli esempi delle slide (attenzione semplificata, la testa a mano, la forma matriciale con la maschera), mostra perché si divide per $\sqrt{d_k}$, costruisce multi-head attention, layer norm, feedforward e un blocco intero con un **test di causalità**, conta i parametri e ricalcola gli esercizi 2-9, 11 e 12 della scheda. Rieseguito da capo: tutti gli output coincidono con quelli salvati, nessun errore e **nessun bug**. Tutti i pesi sono numeri giocattolo o casuali: lo scopo è vedere i conti, non avere un modello che funziona.

### Notebook 1 · Attenzione semplificata sull'esempio della lezione

```python
def softmax(z):
    z = np.asarray(z, dtype=float)
    e = np.exp(z - z.max())          # stabile: sottrae il massimo
    return e / e.sum()

X = np.array([[1, 0, 1],   # chicken
              [0, 1, 0],   # road
              [1, 1, 1]], float)   # it
i = 2
scores = X[: i + 1] @ X[i]
alpha = softmax(scores)
print(alpha @ X[: i + 1])
```

Output:

```text
scores  [2. 1. 3.]
weights [0.2447, 0.0900, 0.6652]
a3      [0.91  0.755 0.91 ]
```

La versione semplificata della [scheda 18](L14-transformer-l-attenzione.md#p-18): punteggi $x_3\cdot x_j$ per $j\le3$, softmax, somma pesata degli $x_j$. Gli stessi numeri della [scheda 20](L14-transformer-l-attenzione.md#p-20): *it* guarda soprattutto se stesso.

Due dettagli di codice da notare: `X[: i + 1]` prende solo le righe fino alla posizione corrente (è la causalità, scritta come slicing); la softmax sottrae il massimo prima di esponenziare, il che non cambia il risultato ma evita l'overflow, e funziona anche con $-\infty$ (servirà per la maschera).

### Notebook 2 · Una testa di attenzione per una posizione

```python
def attention_head_at(X, i, WQ, WK, WV, WO, verbose=True):
    q = X[i] @ WQ              # query del token corrente
    K = X[: i + 1] @ WK        # key dei token fino a i
    V = X[: i + 1] @ WV        # loro value
    dk = WQ.shape[1]
    scores = K @ q / np.sqrt(dk)
    alpha = softmax(scores)
    head = alpha @ V
    a = head @ WO
    return a, alpha
```

Output:

```text
q = [ 2. -1.]
scores / sqrt(dk) = [ 1.414 -0.707  0.707]
weights = [0.62  0.074 0.306]
head = [0.926 1.306]
a = [0.926 1.306 1.306]
```

Le equazioni della [scheda 24](L14-transformer-l-attenzione.md#p-24) e [25](L14-transformer-l-attenzione.md#p-25) in otto righe, con le matrici della testa fatta a mano ([schede 30-33](L14-transformer-l-attenzione.md#p-30)). Il codice ricalca gli otto passi: query solo del token corrente, key e value di tutti i token fino a lui, punteggi scalati, softmax, somma pesata dei value, $W^O$.

Notare `K @ q`: con le key come righe, il prodotto matrice-vettore dà in un colpo tutti i $k_j\cdot q$. La cella propone di cambiare $W^Q$ o $W^K$ perché *it* guardi soprattutto *road*: per esempio una query $q_3 = [-1, 1]$, che dà punteggi $-1$, $1$, $0$ con $k_1, k_2, k_3$ (verificato: il massimo va a $k_2$).

### Notebook 3 · Perché dividere per la radice di d_k

```python
for dk in (4, 16, 64, 256):
    q = rng.standard_normal((10000, dk)); k = rng.standard_normal((10000, dk))
    dots = (q * k).sum(axis=1)
    print(dk, dots.std(), (dots / np.sqrt(dk)).std())
print(softmax([1, 0]), softmax([8, 0]))
```

Output:

```text
d_k =   4: std of the dot products   2.00 (sqrt(d_k) =  2.00), after dividing by sqrt(d_k) 1.00
d_k =  16: std ...   4.02 (sqrt(d_k) =  4.00), ... 1.00
d_k =  64: std ...   8.03 (sqrt(d_k) =  8.00), ... 1.00
d_k = 256: std ...  15.97 (sqrt(d_k) = 16.00), ... 1.00

softmax of [1, 0]: [0.7311, 0.2689]
softmax of [8, 0]: [0.9997, 0.0003]  (almost one-hot: tiny gradients)
```

Esperimento numerico per la motivazione della [scheda 24](L14-transformer-l-attenzione.md#p-24): con componenti indipendenti di media 0 e varianza 1, la deviazione standard di $q\cdot k$ cresce come $\sqrt{d_k}$ (2, 4, 8, 16), e dividendo per $\sqrt{d_k}$ torna a 1 per ogni $d_k$.

Il secondo pezzo mostra il perché del problema: punteggi dell'ordine di 8 (tipici con $d_k = 64$ senza scala) danno una softmax quasi one-hot, $[0{,}9997;\ 0{,}0003]$, e lì il gradiente della softmax è quasi nullo, quindi la testa smette di imparare. Sono le risposte dell'esercizio 6.

### Notebook 4 · Tutti i token insieme: forma matriciale e maschera causale

```python
def causal_self_attention(X, WQ, WK, WV, WO):
    Q, K, V = X @ WQ, X @ WK, X @ WV
    N, dk = X.shape[0], WQ.shape[1]
    scores = Q @ K.T / np.sqrt(dk)
    mask = np.triu(np.full((N, N), -np.inf), k=1)   # -inf sopra la diagonale
    weights = np.vstack([softmax(row) for row in scores + mask])
    return weights @ V @ WO, weights
```

Output:

```text
Q K^T =
 [[ 2.  0.  2.]
 [ 0. -1. -1.]
 [ 2. -1.  1.]]
weights (softmax by row) =
 [[1.    0.    0.   ]
 [0.67  0.33  0.   ]
 [0.62  0.074 0.306]]
output A =
 [[1.    1.    1.   ]
 [0.67  1.    1.   ]
 [0.926 1.306 1.306]]
each row equals the computation for one position: True
```

La formula della [scheda 59](L14-transformer-l-attenzione.md#p-59): $\mathrm{softmax}(\mathrm{mask}(QK^\top/\sqrt{d_k}))VW^O$. La maschera è costruita con `np.triu(..., k=1)`: la parte triangolare superiore *esclusa* la diagonale, piena di $-\infty$. I numeri sono quelli delle [schede 57-58](L14-transformer-l-attenzione.md#p-57).

L'ultima riga di output è il controllo importante: ogni riga del calcolo matriciale coincide con il calcolo posizione per posizione della funzione precedente. La forma matriciale non è un'approssimazione, è lo stesso conto riorganizzato.

### Notebook 5 · Multi-head attention

```python
def multi_head_attention(X, heads, WO):
    outs = [causal_self_attention(X, WQ, WK, WV, np.eye(WV.shape[1]))[0]
            for WQ, WK, WV in heads]
    concat = np.concatenate(outs, axis=1)
    return concat @ WO, concat

d, A, N = 8, 2, 5
dk = dv = d // A
```

Output:

```text
input (5, 8)  concatenation (5, 8)  output (5, 8)
weights: 256 = 4 d^2 = 256
```

Ogni testa riusa `causal_self_attention` con $W^O$ uguale all'identità (la proiezione si fa una volta sola, dopo); le uscite $[N\times d_v]$ si concatenano lungo le colonne in $[N\times Ad_v]$ e si moltiplicano per $W^O$. Con $d = 8$, $A = 2$, $d_k = d_v = 4$: concatenazione $[5\times8]$, output $[5\times8]$ come l'input.

Il conteggio dei pesi verifica la [scheda 40](L14-transformer-l-attenzione.md#p-40): $3\cdot2\cdot8\cdot4 + 8\cdot8 = 256 = 4d^2$.

### Notebook 6 · Layer norm, RMSNorm e feedforward

```python
def layer_norm(x, gamma=1.0, beta=0.0):
    mu = x.mean(axis=-1, keepdims=True)
    sigma = x.std(axis=-1, keepdims=True)   # 1/d, come nel libro
    return gamma * (x - mu) / sigma + beta

def rms_norm(x):
    return x / np.sqrt((x ** 2).mean(axis=-1, keepdims=True))

def ffn(x, W1, b1, W2, b2):
    return np.maximum(0, x @ W1 + b1) @ W2 + b2
```

Output:

```text
x = [2. 4. 6. 8.]  mean 5.0  std 2.236
layer norm: [-1.342 -0.447  0.447  1.342]
layer norm of 10 x + 5: [-1.342 -0.447  0.447  1.342]  (the same: scale and offset are removed)
RMSNorm:    [0.365 0.73  1.095 1.461]
```

Le definizioni delle [schede 48-49](L14-transformer-l-attenzione.md#p-48). `axis=-1` fa sì che la normalizzazione sia sulle componenti di ogni riga (ogni token), non sulla colonna: è proprio la differenza fra layer norm e batch norm. `np.std` usa $\frac1d$ di default, come il libro.

Il test con $10x+5$ mostra l'invarianza a scala e spostamento; RMSNorm non sottrae la media, quindi l'output non è centrato. La feedforward usa ReLU (la versione del libro); i modelli attuali usano SwiGLU ([scheda 47](L14-transformer-l-attenzione.md#p-47)).

### Notebook 7 · Un blocco intero e il test di causalità

```python
def transformer_block(X):
    O = X + multi_head_attention(layer_norm(X), heads, WO_mh)[0]
    H = O + ffn(layer_norm(O), W1, b1, W2, b2)
    return H

X_changed = Xr.copy(); X_changed[-1] = rng.standard_normal(d)
H_changed = transformer_block(X_changed)
print(np.allclose(H[:-1], H_changed[:-1]))
```

Output:

```text
X (5, 8) -> H (5, 8)
outputs of tokens 1 to 4 unchanged: True
output of token 5 changed:          True
after 4 blocks: (5, 8)
```

Il blocco prenorm della [scheda 62](L14-transformer-l-attenzione.md#p-62) in due righe. Il test: si cambia solo l'ultimo token dell'input; gli output dei primi quattro token restano identici, quello del quinto cambia. È la dimostrazione pratica della [scheda 51](L14-transformer-l-attenzione.md#p-51): layer norm e feedforward lavorano riga per riga, e l'unico canale fra posizioni è l'attenzione, che è causale.

Il ciclo finale impila quattro volte lo stesso blocco (stessi pesi, solo per mostrare che le forme combaciano: in un modello vero ogni strato ha pesi suoi).

> **Approfondimento: Che cosa succede togliendo la maschera**
>
> Il notebook suggerisce di provarlo (sezione 10): senza maschera la riga 1 dell'attenzione guarda anche i token 2-5, quindi cambiando il token 5 cambiano gli output di *tutti* i token e il test di causalità fallisce. È il comportamento di un encoder bidirezionale (tipo BERT), che si vedrà più avanti nel corso.

### Notebook 8 · Dove stanno i parametri

```python
def block_weights(d, dff):
    return 4 * d * d, 2 * d * dff

att, ff = block_weights(512, 2048)
att, ff = block_weights(12288, 4 * 12288)
print(96 * (att + ff))
```

Output:

```text
original transformer, one block: attention 1,048,576, feedforward 2,097,152, feedforward share 67%
GPT-3 175B, 96 blocks: 173,946,175,488 weights
```

Il conto delle [schede 40](L14-transformer-l-attenzione.md#p-40) e [46](L14-transformer-l-attenzione.md#p-46): per blocco $4d^2$ nell'attenzione e $2d\,d_{ff} = 8d^2$ nella feedforward, quindi due terzi dei pesi sono nella feedforward. Per GPT-3: $96\cdot12\cdot12288^2\approx1{,}74\cdot10^{11}$, cioè circa 174 miliardi, molto vicino ai 175 miliardi dichiarati; il resto sono soprattutto gli embedding ($50.257\times12.288\approx0{,}6$ miliardi) e i bias.

### Notebook 9 · Controlli della scheda esercizi

```python
# esercizio 5: una testa a mano
X5 = np.array([[1, 0], [0, 1], [1, 1]], float)
WQ5 = np.array([[1, 0], [0, 2]], float)
WK5 = np.array([[1, 1], [0, 1]], float)
WV5 = np.array([[2, 0], [0, 1]], float)
a, w = attention_head_at(X5, 2, WQ5, WK5, WV5, np.eye(2), verbose=False)
# ... esercizi 2, 3, 4, 6, 7, 8, 9, 11, 12
```

Output:

```text
exercise 2  a3: scores [2. 0. 4.], weights [0.117 0.016 0.867], output [1.8509, 0.2505]
exercise 2  a2: scores [2. 1.], weights [0.731 0.269], output [0.7311, 1.7311]
exercise 3/12  N = 5: causal 15, all pairs 25
exercise 4  d_k = 64  weights 4d^2 = 2,359,296
exercise 5  weights [0.178 0.088 0.734]  a3 [1.824 0.822]
exercise 7  concatenation [1 2 0 3]  a_i [4. 2. 0. 1.]
exercise 8  mean 1.0  std 1.581  normalized [ 1.265 -1.265  0.632 -0.632]
exercise 9  attention 1,048,576, feedforward 2,099,712 (with biases), layer norms 2,048
exercise 12 one head and layer 4,194,304, whole model 603,979,776, causal 2,098,176
```

Ricalcola gli esercizi numerici della scheda: le soluzioni nella sezione Studio qui sotto sono state verificate anche con un calcolo indipendente e coincidono con questo output. Va usato *dopo* aver fatto i conti a mano.

Gli esercizi 1 e 10 sono concettuali e non compaiono; il 4c (una testa sola di dimensione piena) non è ricalcolato ma si fa a mente: $4d^2$ anche lì.

## Studio ed esercizi

### Guida allo studio (circa 3 h 50 min)

**Il quadro e la motivazione** (25 min)

Schede 4-17. Saper disegnare a memoria il transformer per un token (embedding + posizione, $L$ blocchi con la residual stream, unembedding + softmax) e dire la differenza fra embedding statici e contestuali con gli esempi di *it*, *keys ... are*, *bank*. Definizione di self-attention causale. Libro pp. 177-180. Esercizio 1.

**Attenzione semplificata e testa di attenzione** (60 min)

Schede 18-33: il cuore della lezione. Scrivere le cinque equazioni della testa (proiezioni, score scalato, softmax, somma dei value, $W^O$) con le forme di ogni oggetto (tabella della scheda 29); spiegare i tre ruoli query/key/value e perché si divide per $\sqrt{d_k}$. Rifare a mano senza guardare l'esempio *chicken, road, it* nelle due versioni (pesi 0,24/0,09/0,67 e 0,62/0,07/0,31). Libro §7.1 (pp. 179-184). Esercizi 2, 5, 6.

**Multi-head attention e parametri** (25 min)

Schede 36-40. Perché più teste, concatenazione e $W^O$, la regola $d_v = d/A$ e il conto $4d^2$ (uguale a una testa piena). Esercizi 4 e 7.

**Il transformer block** (45 min)

Schede 42-52. Le sei equazioni $t^1,\dots,t^5,h$ e la lettura $h_i = x_i + t_i^2 + t_i^5$; residual stream, prenorm, feedforward position-wise con $d_{ff} = 4d$ e i suoi $8d^2$ pesi, SwiGLU, layer norm con $\gamma,\beta$ e RMSNorm; perché solo l'attenzione mescola i token. Libro §7.2 (pp. 184-188). Esercizi 8, 9, 10.

**Forma matriciale e costo** (35 min)

Schede 54-62. Saper scrivere $\mathrm{softmax}(\mathrm{mask}(QK^\top/\sqrt{d_k}))VW^O$ con le forme, costruire la maschera $M$, rifare l'esempio in forma matriciale (schede 57-58) e spiegare il costo quadratico in $N$. Equazioni del blocco 7.39-7.40. Libro §7.3 (pp. 188-191). Esercizi 11, 12.

**Notebook e ripasso orale** (40 min)

Eseguire il notebook: celle 1-4 accanto alle schede corrispondenti, poi il test di causalità della cella 7 e la prova senza maschera suggerita in fondo. Controllare con la cella 9 gli esercizi fatti a mano. Chiudere rispondendo ad alta voce alle domande d'orale, in particolare la derivazione dello scaled dot product e il conteggio dei parametri.

### Esercizi

#### Esercizio 1 (scheda L14): significato contestuale

1. In *The chicken didn't cross the road because it was too wide*, su quale token precedente dovrebbe basarsi di più la rappresentazione di *it*, e quale parola lo dice? Perché un embedding statico di *it*, come word2vec, non può catturarlo?
2. Un language model causale ha letto *The chicken didn't cross the road because it*. Quali token può usare l'attenzione per costruire la rappresentazione di *it*? Può usare *wide*?
3. Completa *The keys to the cabinet \_\_\_ on the table* con *is* o *are*. Quale token lo decide, e quale token più vicino potrebbe ingannare un modello che guarda solo la parola precedente, come un bigramma?

<details><summary>Soluzione</summary>

(a) Su *road*: è la strada a poter essere troppo larga; lo dice *wide*. Un embedding statico assegna a *it* lo stesso vettore in ogni frase (anche in *... it was too tired*, dove il referente è *chicken*), quindi non può rappresentare un riferimento che cambia con il contesto.

(b) Tutti i token fino a *it* compreso: *The, chicken, didn't, cross, the, road, because, it*. Non può usare *wide*, che viene dopo (attenzione causale): a quel punto *it* dovrebbe avere aspetti sia di *chicken* sia di *road* (scheda 13).

(c) *are*: lo decide *keys*, plurale, testa del soggetto. Il token più vicino, *cabinet*, è singolare e spingerebbe un bigramma verso *is*. L'attenzione può collegare il verbo a *keys* a qualunque distanza.

</details>

#### Esercizio 2 (scheda L14): attenzione semplificata a mano

Tre input con $d = 2$: $x_1 = [1,2]$, $x_2 = [0,1]$, $x_3 = [2,0]$.

1. Con l'attenzione semplificata (score = prodotto scalare, pesi = softmax, output = somma pesata degli $x_j$, $j\le i$) calcola punteggi, pesi e output $a_3$.
2. Fai lo stesso per $a_2$. Quale vettore prende il peso maggiore?
3. Si dice spesso che nell'attenzione semplificata un token guarda soprattutto se stesso. È sempre vero? Che cosa mostra (b)?

<details><summary>Soluzione</summary>

(a) Punteggi: $x_3\cdot x_1 = 2$, $x_3\cdot x_2 = 0$, $x_3\cdot x_3 = 4$. Esponenziali $7{,}389;\ 1;\ 54{,}598$, somma $62{,}987$: pesi $0{,}117;\ 0{,}016;\ 0{,}867$. Output $a_3 = 0{,}117\,[1,2] + 0{,}016\,[0,1] + 0{,}867\,[2,0] = [1{,}851;\ 0{,}250]$.

(b) Punteggi $x_2\cdot x_1 = 2$, $x_2\cdot x_2 = 1$; pesi $e^2/(e^2+e) = 0{,}731$ e $0{,}269$; $a_2 = 0{,}731\,[1,2] + 0{,}269\,[0,1] = [0{,}731;\ 1{,}731]$. Il peso maggiore va a $x_1$, non a $x_2$.

(c) Non è sempre vero: $x_i\cdot x_i = \|x_i\|^2$, ma un vettore più lungo e abbastanza allineato può avere prodotto scalare più grande. Qui $x_1$ è più lungo di $x_2$ e ha componente 2 nella stessa direzione: $x_2\cdot x_1 = 2 > x_2\cdot x_2 = 1$. È vero spesso (come nell'esempio della lezione), non per necessità.

</details>

#### Esercizio 3 (scheda L14): contare i punteggi dell'attenzione causale

1. Una sequenza di $N = 5$ token. Quanti punteggi calcola l'attenzione causale in una testa (tutte le posizioni), e quanti ne calcolerebbe se ogni token potesse guardare ogni token?
2. Scrivi la tabella $5\times5$ dei pesi $\alpha_{ij}$ segnando con 0 quelli che l'attenzione causale mette a zero. Quanto vale $\alpha_{11}$, e perché?
3. Dai i due conteggi di (a) per $N$ generico.

<details><summary>Soluzione</summary>

(a) La posizione $i$ guarda $i$ token: $1+2+3+4+5 = 15$ punteggi. Senza vincolo causale $5\times5 = 25$.

(b) Tabella triangolare inferiore: nella riga $i$ sono non nulli $\alpha_{i1},\dots,\alpha_{ii}$, e $\alpha_{ij} = 0$ per $j > i$ (10 zeri sopra la diagonale). $\alpha_{11} = 1$: il primo token può guardare solo se stesso e i pesi di una riga sommano a 1 (softmax di un solo punteggio).

(c) Causale: $N(N+1)/2$; tutte le coppie: $N^2$. Per $N$ grande il causale è circa la metà, ma resta quadratico.

</details>

#### Esercizio 4 (scheda L14): forme

Un transformer con $d = 768$ e $A = 12$ teste, $d_k = d_v = d/A$.

1. Dai $d_k$ e le forme di $x_i$, $W^Q, W^K, W^V$ di una testa, $q_i$, dell'output $\mathrm{head}_i$ di una testa, della concatenazione delle 12 teste, di $W^O$ e di $a_i$.
2. Quanti pesi (senza bias) ha lo strato di multi-head attention? Scrivilo come multiplo di $d^2$.
3. Quanti ne avrebbe una sola testa con $d_k = d_v = d$? Confronta.

<details><summary>Soluzione</summary>

(a) $d_k = d_v = 768/12 = 64$. $x_i$: $[1\times768]$; $W^Q, W^K, W^V$: $[768\times64]$; $q_i$: $[1\times64]$; $\mathrm{head}_i$: $[1\times64]$; concatenazione: $[1\times768]$ ($12\cdot64$); $W^O$: $[768\times768]$; $a_i$: $[1\times768]$.

(b) $3\cdot12\cdot768\cdot64 + 768\cdot768 = 3d^2 + d^2 = 4d^2 = 2.359.296$.

(c) Una testa piena: $W^Q, W^K, W^V$ di $[768\times768]$ e $W^O$ di $[768\times768]$, ancora $4d^2 = 2.359.296$. Stesso numero di parametri: le 12 teste dividono lo spazio in 12 sottospazi da 64 dimensioni, con 12 distribuzioni di attenzione diverse invece di una sola.

</details>

#### Esercizio 5 (scheda L14): una testa di attenzione a mano

Tre input con $d = 2$ e una testa con $d_k = d_v = 2$; $W^O$ è l'identità, quindi $a_3 = \mathrm{head}_3$. $x_1 = [1,0]$, $x_2 = [0,1]$, $x_3 = [1,1]$; $W^Q = \begin{bmatrix}1&0\\0&2\end{bmatrix}$, $W^K = \begin{bmatrix}1&1\\0&1\end{bmatrix}$, $W^V = \begin{bmatrix}2&0\\0&1\end{bmatrix}$.

1. Calcola $q_3$, le key $k_1,k_2,k_3$ e i value $v_1,v_2,v_3$.
2. Calcola i punteggi di $x_3$ con $x_1,x_2,x_3$ divisi per $\sqrt{d_k}$ e i pesi $\alpha_{3j}$.
3. Calcola l'output $a_3$.

<details><summary>Soluzione</summary>

(a) Regola delle righe: $q_3 = [1,0]+[0,2] = [1,2]$. Key: $k_1 = [1,1]$, $k_2 = [0,1]$, $k_3 = [1,1]+[0,1] = [1,2]$. Value: $v_1 = [2,0]$, $v_2 = [0,1]$, $v_3 = [2,1]$.

(b) Punteggi: $q_3\cdot k_1 = 1+2 = 3$, $q_3\cdot k_2 = 2$, $q_3\cdot k_3 = 1+4 = 5$. Divisi per $\sqrt2$: $2{,}121;\ 1{,}414;\ 3{,}536$. Esponenziali $8{,}342;\ 4{,}113;\ 34{,}313$, somma $46{,}769$: pesi $0{,}178;\ 0{,}088;\ 0{,}734$.

(c) $a_3 = 0{,}178\,[2,0] + 0{,}088\,[0,1] + 0{,}734\,[2,1] = [1{,}824;\ 0{,}822]$. Qui *il token guarda soprattutto se stesso*, perché la sua key è la più allineata con la sua query.

</details>

#### Esercizio 6 (scheda L14): perché dividere per la radice di d_k

1. Calcola la softmax dei due punteggi $[1,0]$ e dei due punteggi $[8,0]$.
2. Query e key con componenti casuali indipendenti, $\pm1$ con uguale probabilità. Il prodotto scalare è una somma di $d_k$ termini $\pm1$: media 0, varianza $d_k$. Qual è la sua dimensione tipica (deviazione standard) per $d_k = 64$? E dopo aver diviso per $\sqrt{d_k}$?
3. Perché punteggi della grandezza del secondo caso di (a) sono un problema per il training?

<details><summary>Soluzione</summary>

(a) $[1,0]$: $e/(e+1) = 0{,}731$ e $0{,}269$. $[8,0]$: $e^8/(e^8+1) = 2981/2982 = 0{,}9997$ e $0{,}0003$.

(b) Deviazione standard $\sqrt{64} = 8$; dopo la divisione per $\sqrt{64} = 8$ la deviazione standard è 1.

(c) Punteggi grandi (come 8, tipici con $d_k = 64$ senza scala) rendono la softmax quasi one-hot: quasi tutto il peso su un token. In quella zona la softmax è satura e le sue derivate ($\alpha_j(1-\alpha_j)$ e $-\alpha_j\alpha_k$) sono quasi nulle, quindi i gradienti verso query e key spariscono e la testa impara male o non impara (lo stesso problema della sigmoide saturata, L13). Dividendo per $\sqrt{d_k}$ i punteggi restano dell'ordine di 1 qualunque sia $d_k$.

</details>

#### Esercizio 7 (scheda L14): concatenazione e proiezione

Uno strato con $A = 2$ teste, $d = 4$, $d_v = 2$. Per il token $i$ le due teste danno $\mathrm{head}^1 = [1,2]$ e $\mathrm{head}^2 = [0,3]$, e $W^O$ ha righe $[1,0,0,1]$, $[0,1,0,0]$, $[0,0,1,1]$, $[1,0,0,0]$.

1. Scrivi la concatenazione $\mathrm{head}^1\oplus\mathrm{head}^2$ e la sua forma.
2. Calcola $a_i = (\mathrm{head}^1\oplus\mathrm{head}^2)W^O$ e dai la forma di $W^O$.
3. Perché serve $W^O$, invece di usare la concatenazione come output?

<details><summary>Soluzione</summary>

(a) $[1,2,0,3]$, forma $[1\times Ad_v] = [1\times4]$.

(b) Regola delle righe: $1\cdot[1,0,0,1] + 2\cdot[0,1,0,0] + 0\cdot[0,0,1,1] + 3\cdot[1,0,0,0] = [4,2,0,1]$. $W^O$ è $[Ad_v\times d] = [4\times4]$.

(c) Due ragioni: (1) in generale $Ad_v$ può essere diverso da $d$, e $W^O$ riporta alla dimensione della residual stream; (2) anche quando $Ad_v = d$, senza $W^O$ ogni testa scriverebbe in un blocco fisso di componenti; $W^O$ mescola le teste, perché ogni componente di $a_i$ può combinare le uscite di tutte (qui la prima componente, 4, somma il primo valore della testa 1 e il secondo della testa 2).

</details>

#### Esercizio 8 (scheda L14): layer norm a mano

1. Calcola media $\mu$, deviazione standard $\sigma$ e vettore normalizzato $\hat x$ di $x = [3,-1,2,0]$.
2. Calcola $\mathrm{LayerNorm}(x)$ con gain $\gamma = 2$ e offset $\beta = 1$ (uguali per tutte le componenti).
3. Qual è il vettore normalizzato di $10x+5 = [35,-5,25,5]$? Perché?
4. RMSNorm divide $x$ per la radice della media dei quadrati $\sqrt{\frac1d\sum_j x[j]^2}$ senza sottrarre la media. Calcolala per $x$.

<details><summary>Soluzione</summary>

(a) $\mu = (3-1+2+0)/4 = 1$. Scarti $[2,-2,1,-1]$, quadrati $4,4,1,1$, varianza $10/4 = 2{,}5$, $\sigma = \sqrt{2{,}5} = 1{,}581$. $\hat x = [1{,}265;\ -1{,}265;\ 0{,}632;\ -0{,}632]$.

(b) $2\hat x + 1 = [3{,}530;\ -1{,}530;\ 2{,}265;\ -0{,}265]$.

(c) Lo stesso $\hat x$: la media diventa $10\mu+5$ e la deviazione standard $10\sigma$, quindi $(10x+5-(10\mu+5))/(10\sigma) = (x-\mu)/\sigma$. La normalizzazione toglie scala e spostamento.

(d) $\mathrm{RMS} = \sqrt{(9+1+4+0)/4} = \sqrt{3{,}5} = 1{,}871$; $x/\mathrm{RMS} = [1{,}604;\ -0{,}535;\ 1{,}069;\ 0]$. Non è centrato: la media resta positiva.

</details>

#### Esercizio 9 (scheda L14): dove stanno i parametri

Un blocco del transformer originale: $d = 512$, $A = 8$, $d_{ff} = 2048$.

1. Quanti pesi nella multi-head attention (senza bias)?
2. Quanti parametri nella feedforward, con due matrici e due vettori di bias?
3. Quanti nelle due layer norm ($\gamma$ e $\beta$ per ogni componente)? Quale parte del blocco ha più parametri?
4. GPT-3 175B ha 96 blocchi con $d = 12.288$. Usando $4d^2$ per l'attenzione e $8d^2$ per la feedforward ($d_{ff} = 4d$), stima il numero di parametri.

<details><summary>Soluzione</summary>

(a) $4\cdot512^2 = 1.048.576$.

(b) $W_1$: $512\cdot2048$, $W_2$: $2048\cdot512$, totale $2.097.152$ pesi; bias $2048+512 = 2560$; totale $2.099.712$.

(c) Ogni layer norm ha $2d = 1024$ parametri, due fanno $2048$: trascurabili. La feedforward ha circa due terzi dei parametri del blocco ($2{,}10$ milioni contro $1{,}05$).

(d) $12d^2$ per blocco: $12\cdot12288^2 = 1{,}812\cdot10^9$; per 96 blocchi $173.946.175.488\approx1{,}74\cdot10^{11}$, cioè circa 174 miliardi: quasi tutti i 175 miliardi del nome. Il resto è soprattutto la matrice di embedding (circa $50\,000\times12\,288\approx0{,}6$ miliardi) più bias e layer norm.

</details>

#### Esercizio 10 (scheda L14): la residual stream

1. Usando le sei equazioni del blocco ($t^1,\dots,t^5$ e $h$), scrivi $h_i$ come $x_i$ più due termini.
2. Per un token, $x_i = [1,0,0,1]$, l'attenzione dà $t_i^2 = [0,1,0,0]$ e la feedforward $t_i^5 = [0,0,2,0]$. Calcola $t_i^3$ e $h_i$.
3. Quale componente può portare in $h_i$ informazione da altri token? Quale lavora su ogni posizione indipendentemente?

<details><summary>Soluzione</summary>

(a) $h_i = t_i^5 + t_i^3 = t_i^5 + t_i^2 + x_i$: l'input più il contributo dell'attenzione più quello della feedforward.

(b) $t_i^3 = t_i^2 + x_i = [1,1,0,1]$; $h_i = t_i^5 + t_i^3 = [1,1,2,1]$.

(c) Solo la multi-head attention ($t^2$ dipende anche da $t_1^1,\dots,t_{i-1}^1$). Feedforward e layer norm lavorano su ogni posizione indipendentemente (stessi pesi a ogni posizione).

</details>

#### Esercizio 11 (scheda L14): una testa in forma matriciale

Gli input e le matrici dell'esercizio 5, impacchettati in $X = \begin{bmatrix}1&0\\0&1\\1&1\end{bmatrix}$.

1. Calcola $Q = XW^Q$, $K = XW^K$ e $QK^\top$.
2. Dividi per $\sqrt2$, applica la maschera causale e la softmax riga per riga. Controlla che la riga 3 dia i pesi dell'esercizio 5.
3. Calcola gli output dei tre token, $\mathrm{softmax}(\dots)V$. Perché l'output del primo token è esattamente $v_1$?

<details><summary>Soluzione</summary>

(a) $Q = \begin{bmatrix}1&0\\0&2\\1&2\end{bmatrix}$, $K = \begin{bmatrix}1&1\\0&1\\1&2\end{bmatrix}$, $QK^\top = \begin{bmatrix}1&0&1\\2&2&4\\3&2&5\end{bmatrix}$.

(b) Diviso $\sqrt2$: righe $(0{,}707;\ 0;\ 0{,}707)$, $(1{,}414;\ 1{,}414;\ 2{,}828)$, $(2{,}121;\ 1{,}414;\ 3{,}536)$. Maschera: $-\infty$ in $(1,2)$, $(1,3)$, $(2,3)$. Softmax: riga 1 $(1,0,0)$; riga 2 $(0{,}5;\ 0{,}5;\ 0)$ (due punteggi uguali); riga 3 $(0{,}178;\ 0{,}088;\ 0{,}734)$, come nell'esercizio 5.

(c) Con $V = \begin{bmatrix}2&0\\0&1\\2&1\end{bmatrix}$: output $[2,0]$, $[1;\ 0{,}5]$, $[1{,}824;\ 0{,}822]$. Il primo token ha nella sua riga un solo punteggio non mascherato: la softmax gli dà peso 1, quindi l'output è $1\cdot v_1 = [2,0]$ qualunque siano query e key.

</details>

#### Esercizio 12 (scheda L14): il costo dell'attenzione

Un modello con contesto $N = 2048$ token, 12 strati e 12 teste per strato.

1. Quanti elementi ha la matrice $QK^\top$ di una testa in uno strato? Quanti punteggi in tutto il modello, per una sequenza?
2. Quanti elementi di una $QK^\top$ sopravvivono alla maschera causale?
3. Che cosa succede a questi conti se il contesto raddoppia a 4096 token? E se invece raddoppia la dimensione $d$?

<details><summary>Soluzione</summary>

(a) $2048^2 = 4.194.304$ per testa e strato; in tutto il modello $4.194.304\cdot12\cdot12 = 603.979.776$ (circa 600 milioni).

(b) $N(N+1)/2 = 2048\cdot2049/2 = 2.098.176$, poco più della metà.

(c) Con $N = 4096$ i conti si **quadruplicano**: $4096^2 = 16.777.216$ per testa, $2.415.919.104$ in tutto il modello. Raddoppiando $d$ il numero di punteggi **non cambia** (dipende solo da $N$, strati e teste); cambia il costo di ciascun punteggio ($d_k = d/A$ raddoppia) e quadruplicano i parametri ($12d^2$ per blocco).

</details>

#### Esercizio 13 (proprio): il nostro esempio senza scala e senza maschera

Con le matrici della lezione (schede 30-33), $q_3 = [2,-1]$, key $k_1 = [1,0]$, $k_2 = [0,1]$, $k_3 = [1,1]$.

1. Calcola i pesi di *it* **senza** dividere per $\sqrt{d_k}$. Sono più o meno concentrati di quelli della lezione (0,62; 0,07; 0,31)?
2. Calcola i pesi del token *chicken* (riga 1) **senza** maschera causale, con $q_1 = [2,0]$ e scala $\sqrt2$. Che cosa ci sarebbe di sbagliato in un language model?

<details><summary>Soluzione</summary>

(a) Punteggi $2, -1, 1$; esponenziali $7{,}389;\ 0{,}368;\ 2{,}718$, somma $10{,}475$: pesi $0{,}705;\ 0{,}035;\ 0{,}259$. Più concentrati su *chicken* (0,705 contro 0,62): senza scala la softmax è più "appuntita", ed è l'effetto che con $d_k$ grande diventa quasi one-hot.

(b) Riga 1 di $QK^\top$: $(2,0,2)$, divisa per $\sqrt2$: $(1{,}414;\ 0;\ 1{,}414)$; esponenziali $4{,}113;\ 1;\ 4{,}113$, somma $9{,}226$: pesi $0{,}446;\ 0{,}108;\ 0{,}446$. *chicken* prenderebbe il 55% dell'informazione da *road* e *it*, che vengono dopo: in training il modello vedrebbe i token che deve predire (a ogni posizione il target è il token successivo) e imparerebbe a copiarli, inutile in generazione dove il futuro non c'è.

</details>

#### Esercizio 14 (proprio): forme in forma matriciale

Una sequenza di $N = 10$ token, $d = 64$, $A = 4$ teste con $d_k = d_v = d/A$. Dai le forme di $X$, $W^{Qc}$, $Q^c$, $Q^cK^{c\top}$, $M$, $\mathrm{head}_c$, della concatenazione, di $W^O$ e dell'output dello strato. Quanti pesi ha lo strato di attenzione, e quanti la feedforward con $d_{ff} = 4d$ (senza bias)?

<details><summary>Soluzione</summary>

$d_k = d_v = 16$. $X$: $[10\times64]$; $W^{Qc}$: $[64\times16]$; $Q^c$: $[10\times16]$; $Q^cK^{c\top}$: $[10\times10]$; $M$: $[10\times10]$; $\mathrm{head}_c$: $[10\times16]$; concatenazione: $[10\times64]$; $W^O$: $[64\times64]$; output: $[10\times64]$, come $X$.

Attenzione: $4d^2 = 4\cdot4096 = 16.384$ pesi. Feedforward: $2\cdot64\cdot256 = 32.768 = 8d^2$. Nessuno dei due conteggi dipende da $N$: i parametri non crescono con la lunghezza della sequenza, i punteggi sì ($N^2 = 100$ per testa).

</details>

#### Esercizio 15 (proprio): sei equazioni a mano

Un blocco giocattolo con $d = 2$. Per il token $i$: $x_i = [3,1]$; l'attenzione, applicata all'input normalizzato, restituisce $t_i^2 = [0{,}5;\ -0{,}5]$; la feedforward è $\mathrm{FFN}(z) = \mathrm{ReLU}(z)$ (componente per componente); layer norm senza gain e offset ($\gamma = 1$, $\beta = 0$).

1. Calcola $t_i^1 = \mathrm{LayerNorm}(x_i)$.
2. Calcola $t_i^3$, $t_i^4$, $t_i^5$ e $h_i$.
3. Che cosa si nota sulla layer norm di un vettore di dimensione 2?

<details><summary>Soluzione</summary>

(a) $\mu = 2$, scarti $[1,-1]$, $\sigma = 1$: $t_i^1 = [1,-1]$.

(b) $t_i^3 = t_i^2 + x_i = [3{,}5;\ 0{,}5]$. $t_i^4 = \mathrm{LN}(t_i^3)$: $\mu = 2$, scarti $[1{,}5;\ -1{,}5]$, $\sigma = 1{,}5$, quindi $[1,-1]$. $t_i^5 = \mathrm{ReLU}([1,-1]) = [1,0]$. $h_i = t_i^5 + t_i^3 = [4{,}5;\ 0{,}5]$.

(c) Con $d = 2$ la layer norm (senza $\gamma,\beta$) dà sempre $[1,-1]$ o $[-1,1]$ (o è indefinita se le componenti sono uguali): conserva solo quale componente è maggiore. Mostra bene che cosa toglie (scala e media) e perché servono $\gamma$ e $\beta$; con $d$ realistico (centinaia) l'informazione persa è una piccola frazione.

</details>

### Domande tipo orale

<details><summary>Che cos'è un embedding contestuale e perché serve?</summary>

Traccia: (1) word2vec dà un vettore per parola, uguale in ogni frase; un transformer dà un vettore per token nel suo contesto; (2) esempi: *it* che è il pollo o la strada a seconda di *tired*/*wide*; accordo *keys ... are* con *cabinet* in mezzo; *bank* come riva per via di *pond*; (3) le parole utili possono essere lontane, oltre la finestra di n-gram e LM feedforward; (4) costruzione strato per strato: a ogni strato la rappresentazione di $i$ combina sé stessa e i vicini, tramite l'attenzione; (5) in un modello causale a ogni punto il vettore riflette solo il contesto a sinistra (it con aspetti di chicken e road).

</details>

<details><summary>Descrivi l'attenzione semplificata e il suo limite.</summary>

Traccia: (1) $a_i = \sum_{j\le i}\alpha_{ij}x_j$, somma pesata degli input fino a $i$; (2) score = prodotto scalare $x_i\cdot x_j$ come similarità; (3) $\alpha_{ij}$ = softmax degli score sulla riga, pesi in $[0,1]$ che sommano a 1; (4) esempio chicken/road/it: pesi 0,24, 0,09, 0,67, $a_3 = [0{,}91;\ 0{,}76;\ 0{,}91]$; (5) limiti: nessun parametro da imparare, un solo tipo di similarità, lo stesso vettore fa da elemento confrontato e da contenuto restituito, e il token tende a guardare se stesso (spesso, non sempre). Da qui query, key, value.

</details>

<details><summary>Che cosa sono query, key e value?</summary>

Traccia: (1) tre ruoli di ogni input: query = elemento corrente che si confronta con i precedenti; key = elemento precedente confrontato con la query per avere un peso; value = elemento precedente che viene pesato e sommato; (2) tre proiezioni imparate $q_i = x_iW^Q$, $k_j = x_jW^K$, $v_j = x_jW^V$, stesse matrici a ogni posizione; (3) analogia con una ricerca: la query contro tutte le chiavi, si restituiscono i valori pesati; (4) vantaggio: separare "che cosa cerco", "come mi presento" e "che cosa offro"; il confronto non è più simmetrico e non premia per forza se stessi (esempio: con le proiezioni *it* guarda chicken, 0,62).

</details>

<details><summary>Scrivi le equazioni di una testa di attenzione con le forme di ogni oggetto.</summary>

Traccia: (1) $q_i = x_iW^Q$, $k_j = x_jW^K$, $v_j = x_jW^V$; (2) $\mathrm{score}(x_i,x_j) = q_i\cdot k_j/\sqrt{d_k}$; (3) $\alpha_{ij} = \mathrm{softmax}_j(\mathrm{score})$ per $j\le i$; (4) $\mathrm{head}_i = \sum_{j\le i}\alpha_{ij}v_j$; (5) $a_i = \mathrm{head}_iW^O$. Forme: $x_i$, $a_i$: $[1\times d]$; $W^Q, W^K$: $[d\times d_k]$; $W^V$: $[d\times d_v]$; $q, k$: $[1\times d_k]$; $\mathrm{head}_i$: $[1\times d_v]$; $W^O$: $[d_v\times d]$. Originale: $d = 512$, $d_k = d_v = 64$. Input e output della stessa forma: modularità.

</details>

<details><summary>Perché si divide il prodotto scalare per la radice di d_k?</summary>

Traccia: (1) $q\cdot k$ è una somma di $d_k$ termini; con componenti indipendenti a media 0 e varianza 1 ha media 0 e varianza $d_k$, deviazione standard $\sqrt{d_k}$ (8 per $d_k = 64$); (2) punteggi grandi rendono la softmax quasi one-hot (softmax di $[8,0]$ = $[0{,}9997;\ 0{,}0003]$); (3) lì la softmax è satura, le derivate sono quasi nulle: gradienti minuscoli verso $W^Q$ e $W^K$, training instabile o lento; (4) dividendo per $\sqrt{d_k}$ la deviazione standard torna circa 1 per ogni $d_k$ (verificato nel notebook); (5) nome: scaled dot-product attention.

</details>

<details><summary>Calcola a mano l'output di una testa sull'esempio chicken, road, it.</summary>

Traccia: (1) $q_3 = x_3W^Q = [2,-1]$; key $[1,0], [0,1], [1,1]$; value $[1,1], [0,1], [1,2]$ (regola: ogni componente di $x$ moltiplica una riga di $W$); (2) punteggi $2, -1, 1$, divisi per $\sqrt2$: $1{,}41;\ -0{,}71;\ 0{,}71$; (3) esponenziali $4{,}11;\ 0{,}49;\ 2{,}03$, somma 6,63: pesi $0{,}62;\ 0{,}07;\ 0{,}31$; (4) $\mathrm{head}_3 = [0{,}93;\ 1{,}31]$, $a_3 = \mathrm{head}_3W^O = [0{,}93;\ 1{,}31;\ 1{,}31]$; (5) lettura: il 62% viene dal value di chicken; casi estremi $[1,2,2]$ e $[1,1,1]$.

</details>

<details><summary>Che cos'è la multi-head attention e quanti parametri ha?</summary>

Traccia: (1) $A$ teste in parallelo alla stessa profondità, ognuna con le sue $W^{Qc}, W^{Kc}, W^{Vc}$; (2) motivazione: ogni testa una distribuzione di pesi diversa, relazioni linguistiche o pattern diversi; (3) output $[1\times d_v]$ per testa, concatenati in $[1\times Ad_v]$, proiettati da $W^O$ $[Ad_v\times d]$ a $[1\times d]$; (4) di solito $d_v = d/A$: $W^O$ quadrata e totale $4d^2$ pesi, uguale a una testa piena; (5) originale $d = 512$, $A = 8$: $4\cdot512^2 = 1.048.576$; (6) $W^O$ mescola le teste.

</details>

<details><summary>Descrivi il transformer block e le sue equazioni.</summary>

Traccia: (1) quattro componenti: multi-head attention, feedforward, connessioni residue, layer norm; (2) equazioni: $t^1 = \mathrm{LN}(x_i)$, $t^2 = \mathrm{MHA}(t_i^1, [t_1^1..t_{i-1}^1])$, $t^3 = t^2+x_i$, $t^4 = \mathrm{LN}(t^3)$, $t^5 = \mathrm{FFN}(t^4)$, $h_i = t^5+t^3$; (3) quindi $h_i = x_i + t^2 + t^5$; (4) prenorm: normalizzazione prima di attenzione e FFN (l'originale era postnorm); (5) input e output $[1\times d]$: i blocchi si impilano; versione matriciale $O = X + \mathrm{MHA}(\mathrm{LN}(X))$, $H = O + \mathrm{FFN}(\mathrm{LN}(O))$.

</details>

<details><summary>Che cos'è la residual stream e perché è un modo utile di pensare al transformer?</summary>

Traccia: (1) una corrente di vettori $d$-dimensionali per ogni posizione, che parte da $x_i$; (2) ogni componente legge dalla corrente e aggiunge il suo output, invece di sostituirla; (3) l'attenzione è l'unico componente che legge da altre correnti: può spostare informazione dalla corrente del token A a quella del token B (Elhage et al.); (4) nei blocchi bassi la corrente rappresenta il token corrente, in quelli alti di solito il token successivo; (5) vantaggi: l'informazione originale si conserva, il gradiente ha un percorso diretto (connessioni residue, L13); ultima layer norm prima della testa.

</details>

<details><summary>Lo strato feedforward del transformer: struttura, parametri, varianti.</summary>

Traccia: (1) rete a uno strato nascosto, due matrici, $\mathrm{FFN}(x) = \mathrm{ReLU}(xW_1+b_1)W_2+b_2$; (2) position-wise: stessi pesi a ogni posizione, non mescola le posizioni; pesi diversi fra strati; (3) $d_{ff} = 4d$ (512 → 2048): $2d\,d_{ff} = 8d^2$ pesi, il doppio dell'attenzione, due terzi del blocco; (4) sembra contenere gran parte della conoscenza fattuale (Geva 2021, Meng 2022); (5) oggi SwiGLU: $(\mathrm{Swish}_\beta(xW_1+b_1)\otimes(xW_2+b_2))W_3+b_3$, un valore e un gate, $\mathrm{Swish}_\beta(x) = x\sigma(\beta x)$; con tre matrici $d_{ff}$ un po' meno di $4d$.

</details>

<details><summary>Layer norm: definizione, esempio, differenza con RMSNorm.</summary>

Traccia: (1) z-score sul vettore di un token: $\mu$ e $\sigma$ sulle $d$ componenti (con $\frac1d$); (2) $\mathrm{LN}(x) = \gamma\frac{x-\mu}{\sigma}+\beta$, $\gamma$ gain e $\beta$ offset imparabili; (3) esempio $[2,4,6,8]$: $\mu = 5$, $\sigma = \sqrt5$, $[-1{,}34;\ -0{,}45;\ 0{,}45;\ 1{,}34]$; (4) non su tutto uno strato o un batch, ma su un vettore: $d$ in, $d$ out; invariante a scala e spostamento; (5) RMSNorm divide per $\sqrt{\frac1d\sum x_j^2}$ senza sottrarre la media, più semplice e usata nei modelli moderni; (6) serve a tenere i valori in un intervallo stabile nella rete profonda.

</details>

<details><summary>Come si calcola l'attenzione per tutti i token insieme? Scrivi la formula e le forme.</summary>

Traccia: (1) $X$ $[N\times d]$, una riga per token; $Q = XW^Q$, $K = XW^K$ $[N\times d_k]$, $V = XW^V$ $[N\times d_v]$; (2) $QK^\top$ $[N\times N]$: elemento $(i,j) = q_i\cdot k_j$, tutti i punteggi con una moltiplicazione; (3) divisione per $\sqrt{d_k}$, maschera, softmax per riga; (4) $\mathrm{head} = \mathrm{softmax}(\mathrm{mask}(QK^\top/\sqrt{d_k}))V$ $[N\times d_v]$, $A = \mathrm{head}\,W^O$ $[N\times d]$; (5) multi-head: $(\mathrm{head}_1\oplus\dots\oplus\mathrm{head}_A)W^O$; (6) è lo stesso calcolo del token singolo per tutte le righe insieme (il notebook lo verifica), eseguito in parallelo su GPU.

</details>

<details><summary>A che cosa serve la maschera causale e come è fatta?</summary>

Traccia: (1) $QK^\top$ contiene anche i confronti con i token successivi ($j > i$); in un LM causale sarebbe barare: il target di ogni posizione è il token dopo, che sarebbe visibile; (2) $M$: $-\infty$ sopra la diagonale, 0 altrove; si somma ai punteggi prima della softmax; (3) $e^{-\infty} = 0$: pesi nulli sul futuro, e la riga somma ancora a 1 sulle posizioni $j\le i$; (4) esempio: riga 1 $(1,0,0)$, il primo token guarda solo sé stesso; riga 2 $(0{,}67;\ 0{,}33;\ 0)$; (5) senza maschera si ottiene un encoder bidirezionale; il test del notebook (cambiare l'ultimo token non cambia gli altri output) fallirebbe.

</details>

<details><summary>Perché l'attenzione ha costo quadratico, e che cosa implica?</summary>

Traccia: (1) $QK^\top$ ha $N\times N$ elementi: un punteggio per ogni coppia di token, per ogni testa di ogni strato; (2) esempi: $N = 1000$ → $10^6$; $N = 100.000$ → $10^{10}$; raddoppiare $N$ quadruplica; (3) la maschera ne lascia $N(N+1)/2$, ma l'ordine resta $N^2$; (4) il numero di parametri non dipende da $N$; raddoppiare $d$ non cambia il numero di punteggi ma il costo di ciascuno; (5) conseguenza: contesti molto lunghi (romanzi interi) sono costosi; esempio dell'esercizio 12: 2048 token, 12 strati, 12 teste → circa 600 milioni di punteggi per sequenza.

</details>

<details><summary>Dove stanno i parametri di un transformer? Stima quelli di GPT-3.</summary>

Traccia: (1) attenzione: $4d^2$ per strato (con $d_v = d/A$); (2) feedforward: $2d\,d_{ff} = 8d^2$ con $d_{ff} = 4d$; (3) layer norm: $2d$ ciascuna, trascurabili; bias trascurabili; (4) quindi circa $12d^2$ per blocco, due terzi nella feedforward; originale: 1,05 e 2,10 milioni; (5) GPT-3: $96\cdot12\cdot12288^2\approx1{,}74\cdot10^{11}$, quasi tutti i 175 miliardi; il resto è soprattutto l'embedding; (6) i parametri crescono con $d^2$ e con il numero di strati, non con la lunghezza del contesto.

</details>
