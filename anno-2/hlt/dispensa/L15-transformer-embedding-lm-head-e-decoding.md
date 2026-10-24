# L15 · Transformer: embedding, LM head e decoding

*Transformers: Decoding* · 16/10/2026 · Claudio Gallicchio · lettura: J&M cap. 7, §7.4-7.6

[Versione interattiva sul sito](https://gabriele-marsili.github.io/appunti-magistrale-ai/anno-2/hlt/sito/#L15) · [Indice della dispensa](README.md)

Seconda lezione sul **transformer** (J&M §7.4-7.6): le due estremità del modello e il modo di usarlo per generare. In basso, gli **embedding dei token** (righe della matrice $E$ $[|V|\times d]$, selezionate da one-hot) e delle **posizioni**: apprese, **sinusoidali** (seni e coseni di frequenze diverse, prodotto scalare che dipende solo dalla distanza) e relative con **RoPE** (rotazioni di query e key). In alto, la **language modeling head**: logit $u = hE^\top$ con **weight tying**, softmax, il modello decoder-only completo. Poi il **decoding**: greedy (e beam search), random sampling, **temperatura**, **top-k** e **top-p**, tutti sull'esempio *all/the/your/that*. Tutti i numeri delle slide tornano: nessuna correzione. Con il notebook (nessun bug) e la scheda di 11 esercizi.

## Indice

- [Apertura](#apertura)
- [Embedding dei token](#embedding-dei-token)
- [Posizioni](#posizioni)
- [La language modeling head](#la-language-modeling-head)
- [Greedy e random sampling](#greedy-e-random-sampling)
- [Temperatura, top-k, top-p](#temperatura-top-k-top-p)
- [Notebook](#notebook)
- [Studio ed esercizi](#studio-ed-esercizi)

## Apertura

<a id="p-1"></a>

### Slide 1 · Transformer: embedding, LM head e decoding

Lezione 15, di Claudio Gallicchio (16 ottobre 2026): chiude il giro del transformer iniziato nella [L14](L14-transformer-l-attenzione.md#p-1). Il sottotitolo elenca le tre cose che mancavano: **embedding dei token e delle posizioni** (come si entra nel modello), la **language modeling head** (come se ne esce con una distribuzione sul token successivo) e il **decoding** (come da quella distribuzione si sceglie il token da generare).

Dopo questa lezione si sa descrivere un language model decoder-only dall'id del token in ingresso fino al testo generato: è la base della lezione di laboratorio successiva su nanoGPT.

<a id="p-2"></a>

### Slide 2 · Indice

Sei parti:

1. **dove siamo**: ripasso del blocco della L14 e mappa della lezione;
2. **embedding dei token**: la matrice $E$ e i vettori one-hot;
3. **posizioni**: perché servono, embedding appresi, sinusoidali, RoPE;
4. **language modeling head**: unembedding, softmax, weight tying, il modello completo;
5. **greedy e random sampling**: il decoding nei due casi estremi (con un cenno alla beam search);
6. **temperature, top-k, top-p**: i tre modi per stare fra i due estremi.

<a id="p-3"></a>

### Slide 3 · Riferimento: J&M §7.4-7.6

Lettura: capitolo 7 di Jurafsky e Martin (draft del 19 agosto 2026), paragrafi **7.4** (The input: embeddings for token and position), **7.5** (The Language Modeling Head) e **7.6** (Decoding), pagine stampate 191-201. Quasi tutte le figure e gli esempi numerici delle slide (*Thanks for all the*, Janet will back the bill, i logit 1,2 / 0,9 / 0,1 / -0,5) vengono da lì.

Due aggiunte della lezione rispetto al libro: la formula delle **posizioni sinusoidali** (il libro le nomina soltanto) e l'idea geometrica di **RoPE**; il libro si limita a citare RoPE. L'esempio di greedy e beam search (schede 40-41) viene dal capitolo 13 del libro (traduzione automatica).

<a id="p-4"></a>

### Slide 4 · Dove siamo: il blocco della lezione scorsa

La figura è quella del transformer per un token ([schede 6-8 della L14](L14-transformer-l-attenzione.md#p-6)): dal basso *input token*, Embedding, il nodo $\oplus$ con Positional, la pila di $L$ blocchi (layer norm, multi-head attention, layer norm, feedforward) con la colonna della **residual stream**, in cima Unembedding e Softmax. Il riquadro evidenzia i **blocchi**: è ciò che si è visto nella L14 (attenzione, feedforward, layer norm, residual stream).

Oggi si completano le due estremità che la L14 aveva lasciato in sospeso.

<a id="p-5"></a>

### Slide 5 · Oggi, in basso: l'input

Stessa figura, riquadro in basso su **Embedding** e **Positional**: come si passa dagli **id dei token** (interi prodotti dal tokenizer BPE, [L2](L02-parole-e-token.md#p-40)) ai vettori di dimensione $d$ che entrano nel primo blocco.

Due ingredienti: l'**embedding del token** (che cosa è) e l'**embedding della posizione** (dove si trova), sommati. Senza il secondo, come si vedrà, l'attenzione non distingue l'ordine delle parole.

<a id="p-6"></a>

### Slide 6 · Oggi, in alto: la testa e il decoding

Riquadro in alto, su **Unembedding** e **Softmax** ("output probabilities over tokens"): la **language modeling head**, che dall'ultimo vettore della residual stream produce una distribuzione sul vocabolario per il token successivo.

Poi una domanda che non riguarda l'architettura ma l'uso: data la distribuzione, **quale token generare**? È il **decoding**. La stessa rete può dare testi molto diversi (ripetitivi, creativi, sconclusionati) a seconda di come si sceglie il token.

<a id="p-7"></a>

### Slide 7 · Il transformer block in una slide

Ripasso compatto della [L14](L14-transformer-l-attenzione.md#p-62), da sapere a memoria:

- **attenzione**: ogni token è una somma pesata dei *value* dei token fino a lui; pesi = softmax dei prodotti scalari della sua query con le loro key, divisi per $\sqrt{d_k}$;
- **multi-head**: $A$ teste in parallelo, concatenate e proiettate con $W^O$;
- **il blocco** (prenorm): layer norm, attenzione, somma alla corrente; layer norm, feedforward, somma alla corrente;
- **tutti i token insieme**: input $X$ e output $H$ di forma $[N\times d]$, con la maschera causale sul futuro.

Il punto che serve oggi: $X$ e $H$ hanno la stessa forma $[N\times d]$. Oggi si vede da dove viene $X$ (embedding + posizioni) e che cosa si fa della riga $N$ di $H$ dell'ultimo blocco (la testa).

<a id="p-8"></a>

### Slide 8 · Dagli id al token successivo: i passi di oggi

Cinque riquadri in fila, uno per sezione: **token embeddings** (la matrice $E$, un vettore per id), **positions** (appresi, sinusoidali, RoPE), **language modeling head** (dall'ultimo vettore a una distribuzione sul vocabolario), **greedy e random sampling** (il token più probabile o uno a caso), **temperature, top-k, top-p** (vie di mezzo).

Il messaggio: *in basso* dagli id ai vettori, *in alto* da un vettore al token successivo. Ripetendo il passo in alto un token dopo l'altro (il token scelto viene aggiunto all'input) il modello **genera testo**: è la generazione autoregressiva della [L1](L01-introduzione-al-corso.md#p-6).

## Embedding dei token

<a id="p-9"></a>
**Slide 9 · Embedding dei token** — Dall'id intero al vettore: la matrice di embedding e la sua lettura come prodotto con un one-hot.

<a id="p-10"></a>

### Slide 10 · La matrice di embedding E

$E$ ha **una riga di $d$ numeri per ogni token del vocabolario**: forma $[|V|\times d]$.

- **dal testo agli id**: `thanks` `for` `all` `the` viene tokenizzato con BPE in $[5, 4000, 10532, 2224]$ (l'esempio del libro; gli id sono le posizioni dei token nel vocabolario del tokenizer, [encoder BPE della L2](L02-parole-e-token.md#p-40));
- **dagli id ai vettori**: si prendono le righe 5, 4000, 10532 e 2224 di $E$. Sono gli embedding **appresi** del capitolo 6 del libro (la matrice $E$ dell'LM feedforward, [L13](L13-reti-neurali.md#p-42)), uno per token, aggiornati con il resto della rete durante il pretraining.

**Attenzione alla notazione**: qui $V$ è il *vocabolario*, $|V|$ la sua dimensione; non ha niente a che fare con i vettori *value* $V$ dell'attenzione della L14. Il libro fa la stessa precisazione.

<a id="p-11"></a>

### Slide 11 · Vettori one-hot

La figura: un vettore riga $[1\times|V|]$ di zeri con un 1 in posizione 5, moltiplicato per $E$ (rettangolo azzurro $|V|\times d$ con la riga 5 in verde), dà il vettore verde $[1\times d]$.

Un **one-hot** ha tutte le componenti a 0 tranne un 1 all'indice del token (lo stesso oggetto dei target one-hot della [L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-6)). Nel prodotto $x E$ ogni componente $j$ del risultato è $\sum_k x_k E_{kj} = E_{5j}$: sopravvive solo la riga 5.

**Selezionare una riga di $E$ = moltiplicare $E$ per un one-hot.** Nel codice si fa con l'indicizzazione (`E[ids]`), molto più economica; la forma matriciale serve a vedere l'embedding come **primo strato lineare** della rete, senza bias né attivazione, e a capire il weight tying della scheda 28.

<a id="p-12"></a>

### Slide 12 · Tutta la sequenza insieme

Con $N$ token si impilano $N$ one-hot, uno per posizione della finestra di contesto: una matrice $[N\times|V|]$. Il prodotto con $E$ $[|V|\times d]$ dà $[N\times d]$: **una riga di embedding per token**, la matrice degli embedding dei token dell'input.

Nella figura le righe della matrice one-hot hanno l'1 in posti diversi (token diversi); l'ultima ha l'1 nello stesso posto della prima: lo stesso token in due posizioni dà **due righe identiche**. È esattamente il problema che le posizioni risolveranno (scheda 15).

La forma $[N\times d]$ è quella di $X$ nella forma matriciale del blocco ([L14](L14-transformer-l-attenzione.md#p-54)).

<a id="p-13"></a>

### Slide 13 · Embedding dei token a mano

Vocabolario giocattolo di $|V| = 6$ token con $d = 3$ (numeri inventati, non appresi), che servirà anche per la testa (scheda 30):

| id | token | riga di $E$ |
| --- | --- | --- |
| 1 | So | [1, 0, 0] |
| 2 | long | [0, 1, 0] |
| 3 | and | [0, 0, 1] |
| 4 | thanks | [1, 1, 0] |
| 5 | for | [0, 1, 1] |
| 6 | all | [1, 0, 1] |

- one-hot di *thanks* = $[0,0,0,1,0,0]$, per $E$ = riga 4 = $[1,1,0]$;
- *So long and thanks for* = id $[1,2,3,4,5]$: le righe da 1 a 5.

**$E$ è grande**: con $|V| = 50.000$ e $d = 512$ ha $50.000\cdot512 = 25{,}6$ milioni di pesi (verificato). Con $d = 768$ (esercizio 1) sono 38,4 milioni: in un modello piccolo come GPT-2 small (124 milioni) l'embedding è circa un terzo dei parametri.

> **Da saper fare: Conto da saper fare**
>
> Numero di pesi della matrice di embedding: $|V|\cdot d$. Esempi: $50.000\cdot512 = 25.600.000$; $50.000\cdot768 = 38.400.000$; GPT-2 ($|V| = 50.257$, $d = 768$): 38.597.376. Senza weight tying la testa ne aggiunge altrettanti (scheda 28).

## Posizioni

<a id="p-14"></a>
**Slide 14 · Posizioni** — Come dire al modello dove si trova ogni token: embedding appresi, sinusoidali, relativi (RoPE).

<a id="p-15"></a>

### Slide 15 · Perché servono le posizioni

**Gli embedding dei token non dipendono dalla posizione.** Le frasi *dog bites man .* e *man bites dog .* hanno significati opposti ma usano gli stessi quattro vettori:

- **stessi vettori**: *dog* ha lo stesso embedding in posizione 1 e in posizione 3;
- **attenzione cieca all'ordine**: l'attenzione è una somma pesata, e i pesi dipendono solo dai prodotti scalari fra vettori. Nel primo strato l'output per il punto finale (che vede tutti e quattro i token) è **identico** nelle due frasi: stessi quattro vettori, solo in ordine diverso, e una somma non dipende dall'ordine degli addendi.

Esercizio 2 della scheda, verificato: con embedding giocattolo e attenzione semplificata l'output del punto è $[0{,}677;\ 0{,}677]$ in entrambe le frasi; aggiungendo le posizioni diventa $[1{,}000;\ 0{,}679]$ e $[0{,}963;\ 0{,}627]$.

Quindi **bisogna aggiungere l'informazione sulla posizione di ogni token**. (La maschera causale dà in realtà un debole segnale d'ordine, perché il token $i$ vede $i$ token; ma non basta a distinguere l'ordine dentro il contesto.)

> **Approfondimento: Permutation equivariance**
>
> Facoltativo. Senza posizioni e senza maschera, self-attention, layer norm e feedforward sono **equivarianti per permutazione**: permutando le righe di $X$ si ottengono le stesse righe di $H$ permutate allo stesso modo. Per un modello di linguaggio, in cui l'ordine delle parole cambia il significato, questo è inaccettabile: le posizioni rompono la simmetria.

<a id="p-16"></a>

### Slide 16 · Embedding di posizione assoluti

La figura (Fig. 7.14 del libro): per ogni parola di *Janet will back the bill* un vettore rosa (word embedding) e uno viola numerato da 1 a 5 (position embedding), sommati nei nodi $\oplus$ verdi; i vettori composti salgono nel transformer block.

- **Posizioni apprese**: un embedding per ogni posizione fino a una lunghezza massima, raccolti in $E_{pos}$ di forma $[N\times d]$. Come c'è un embedding per la parola *fish*, c'è un embedding per la *posizione 3*, appreso in training.
- La riga $i$ dell'input è $X_i = E[\mathrm{id}(i)] + E_{pos}[i]$: una **somma** (non una concatenazione), perciò stessa dimensione $[1\times d]$.

**L'input $X$ = embedding dei token + embedding delle posizioni, entrambi $[N\times d]$.** È l'unico punto in cui la posizione entra nel modello: da lì sale lungo la residual stream.

<a id="p-17"></a>

### Slide 17 · Posizioni a mano

Il token *thanks* ($E[\text{thanks}] = [1,1,0]$) in due posizioni, con embedding di posizione inventati:

- posizione 4: $[1,1,0] + [0{,}0;\ 0{,}2;\ -0{,}1] = [1{,}0;\ 1{,}2;\ -0{,}1]$;
- posizione 1: $[1,1,0] + [0{,}1;\ 0{,}0;\ 0{,}0] = [1{,}1;\ 1{,}0;\ 0{,}0]$.

Somme verificate. **Lo stesso token ha ora un vettore d'ingresso diverso in ogni posizione**, e l'attenzione può distinguere *dog* soggetto da *dog* oggetto. I valori di posizione sono piccoli rispetto all'embedding del token: in un modello vero le scale le decide il training.

<a id="p-18"></a>

### Slide 18 · Un problema delle posizioni apprese

- **Pochi esempi alla fine**: le prime posizioni compaiono in ogni testo di training, quelle vicine al limite massimo solo nei testi lunghi. Gli embedding di quelle posizioni ricevono pochi aggiornamenti, possono essere addestrati male e generalizzare male al test. Inoltre oltre la lunghezza massima **non esistono** (esercizio 3).
- **Una funzione statica**: in alternativa, una funzione fissa che manda la posizione intera in un vettore reale; è definita per sequenze di lunghezza arbitraria.

Il transformer originale (Vaswani et al., 2017) usa **seni e coseni di frequenze diverse**: scheda successiva.

> **Approfondimento: Per il progetto**
>
> Gli encoder preaddestrati della famiglia BERT/RoBERTa usano posizioni **apprese** con lunghezza massima 512 token: un testo più lungo va troncato o spezzato. Per i messaggi d'odio (tweet, commenti) di solito basta, ma conviene controllare la distribuzione delle lunghezze in token del dataset e fissare `max_length` di conseguenza: un valore inutilmente alto costa memoria (l'attenzione è quadratica in $N$, [L14](L14-transformer-l-attenzione.md#p-60)).

<a id="p-19"></a>

### Slide 19 · Embedding di posizione sinusoidali

$$PE(p,2i) = \sin\!\left(\frac{p}{10000^{2i/d}}\right)\qquad PE(p,2i+1) = \cos\!\left(\frac{p}{10000^{2i/d}}\right)$$

con $p$ la posizione, $d$ la dimensione del modello, $i = 0,1,\dots,d/2-1$ (Vaswani et al., 2017).

- **Coppie di dimensioni**: le dimensioni $2i$ e $2i+1$ sono un seno e un coseno della **stessa frequenza** $\omega_i = 1/10000^{2i/d}$: un punto che gira su una circonferenza.
- **Frequenze**: veloci nelle prime coppie ($i = 0$: $\omega_0 = 1$, **un radiante per posizione**), sempre più lente nelle ultime (per $i = d/2-1$, $\omega \approx 1/10000$).
- **Nessun parametro**: calcolate, non apprese; definite per qualsiasi posizione.

Come per gli embedding appresi, il vettore $PE(p)$ di dimensione $d$ si **somma** all'embedding del token.

> **Da saper fare: Da saper scrivere**
>
> La formula, il significato dei simboli e i due casi estremi: la prima coppia ha periodo $2\pi\approx6{,}28$ posizioni; l'ultima ha periodo circa $2\pi\cdot10000\approx63.000$ posizioni. Con $d = 4$ le frequenze sono $1$ e $1/10000^{2/4} = 1/100$ (scheda 20).

<a id="p-20"></a>

### Slide 20 · Posizioni sinusoidali: un esempio

Con $d = 4$: due coppie, frequenze $1$ e $1/100$, cioè $PE(p) = [\sin p,\ \cos p,\ \sin(p/100),\ \cos(p/100)]$ (angoli in radianti).

| $p$ | vettore |
| --- | --- |
| 0 | [0,00; 1,00; 0,00; 1,00] |
| 1 | [0,84; 0,54; 0,01; 1,00] |
| 2 | [0,91; -0,42; 0,02; 1,00] |

Valori verificati ($\sin 2 = 0{,}909$, $\cos 2 = -0{,}416$, $\cos 0{,}02 = 0{,}9998$).

- **coppia veloce**: cambia molto da una posizione all'altra, distingue le posizioni vicine;
- **coppia lenta**: cambia pochissimo, distingue le posizioni lontane. Come le **lancette di un orologio**: i secondi distinguono istanti vicini, le ore istanti lontani; insieme identificano l'istante.

Con due sole coppie però la coppia veloce si ripete ogni 6,28 posizioni: è per questo che servono molte frequenze (esercizio 4).

<a id="p-21"></a>

### Slide 21 · Posizioni sinusoidali: posizioni vicine

**Sinistra**: heatmap di $\sin(p/10000^{2i/d})$ con $d = 64$, posizioni $p$ da 0 a 50 sull'asse orizzontale, dimensione seno $2i$ da 0 a 62 su quello verticale, colori da blu (-1) a rosso (+1). In basso (frequenze veloci) le strisce alternano rapidamente; salendo diventano bande larghe e lente; in alto è tutto quasi bianco (seno vicino a 0 per tutte le posizioni mostrate).

**Destra**: prodotto scalare di $PE(4)$ con $PE(p)$ al variare di $p$. Picco 32 in $p = 4$ (il prodotto con se stesso vale $d/2 = 32$, perché $\sin^2+\cos^2 = 1$ per ognuna delle 32 coppie), 30,9 in $p = 5$, 21,0 in $p = 17$, poi una discesa oscillante fino a circa 16 in $p = 50$. Tutti valori verificati.

**Il prodotto scalare dipende solo dalla distanza**: $PE(p)\cdot PE(q) = \sum_i \cos(\omega_i(p-q))$. Posizioni vicine hanno vettori più simili, come diceva il libro: 4 è più simile a 5 che a 17.

> **Da saper fare: Perché dipende solo dalla distanza**
>
> Per ogni coppia: $\sin(\omega p)\sin(\omega q) + \cos(\omega p)\cos(\omega q) = \cos(\omega(p-q))$ (formula di sottrazione del coseno). Sommando sulle $d/2$ coppie: $PE(p)\cdot PE(q) = \sum_{i=0}^{d/2-1}\cos(\omega_i(p-q))$. Con $p = q$ ogni termine vale 1: totale $d/2$. Il notebook (cella 7) verifica che $PE(4)\cdot PE(17) = PE(30)\cdot PE(43) = 21{,}0067$: distanza 13 in entrambi i casi.

> **Approfondimento: Non è monotòno**
>
> La curva non scende in modo monotòno: ci sono risalite (circa 19,6 intorno a $p = 36$) perché i coseni veloci oscillano. Con $d = 4$ l'effetto è estremo: $PE(4)\cdot PE(17) = \cos 13+\cos0{,}13 = 1{,}899$ è *maggiore* di $PE(4)\cdot PE(5) = \cos1+\cos0{,}01 = 1{,}540$, perché 13 radianti sono poco più di due giri ($13/2\pi\approx2{,}07$). Più frequenze, con periodi diversi, rendono la somma una misura di vicinanza affidabile (esercizio 4).

<a id="p-22"></a>

### Slide 22 · Posizioni relative e RoPE

- **Posizione relativa**: rappresentare la *distanza* fra due token invece della posizione assoluta di ciascuno.
- **Dentro l'attenzione**: questi metodi sono di solito implementati nel meccanismo di attenzione **a ogni strato**, non sommati una volta sola all'input come gli embedding assoluti.
- **RoPE**: Rotary Position Embedding (Su et al., 2024), il metodo più diffuso; lo usano molti LLM recenti (per esempio la famiglia Llama).

Motivazione: **per una parola conta spesso quanto è lontana un'altra parola, non dove si trovano entrambe**. Che il verbo sia 3 token dopo il soggetto conta allo stesso modo all'inizio di un documento e alla posizione 5000.

<a id="p-23"></a>

### Slide 23 · RoPE: l'idea

La figura mostra due piani: a sinistra una query in posizione 2 e una key in posizione 1, a destra una query in posizione 5 e una key in posizione 4. Le frecce sono ruotate di angoli diversi nei due casi (a destra tutte e due molto più ruotate), ma l'**angolo fra query e key**, in rosso, è lo stesso.

- si **ruota** ogni coppia di dimensioni di ogni query e di ogni key di un angolo **proporzionale alla sua posizione**: query in posizione $m$ di $m\theta$, key in posizione $n$ di $n\theta$;
- il prodotto scalare di due vettori ruotati dipende dalle loro lunghezze e dall'angolo fra loro: qui dal **contenuto** e da $(m-n)\theta$, cioè **solo da $m-n$**.

**Posizioni 2 e 1, o 5 e 4: stessa posizione relativa, stesso punteggio.** Come per le sinusoidali, ogni coppia ruota con una sua velocità $\theta_i$.

> **Approfondimento: La formula di RoPE**
>
> Oltre le slide (Su et al.). Per la coppia $i$, con $\theta_i = 10000^{-2i/d}$, la rotazione è $R(\alpha) = \begin{pmatrix}\cos\alpha & -\sin\alpha\\ \sin\alpha & \cos\alpha\end{pmatrix}$ applicata a $(x_{2i},x_{2i+1})$ con $\alpha = m\theta_i$. Poiché $R(\alpha)^\top R(\beta) = R(\beta-\alpha)$, il punteggio è $(R(m\theta)q)\cdot(R(n\theta)k) = q^\top R((n-m)\theta)\,k$: dipende solo da $n-m$. Differenze con le sinusoidali: si applica a **query e key** (non ai value) **in ogni strato**, e **moltiplica** invece di sommare. Il notebook (cella 10) lo verifica con $d = 8$: punteggio $-1{,}6954$ per le coppie di posizioni (2,1), (5,4), (105,104).

> **Da saper fare: RoPE in due dimensioni a mano**
>
> Esercizio 5 della scheda: $q = k = [1,0]$, 30° per posizione. $(m,n) = (2,1)$: $q$ ruotato di 60° = $[0{,}5;\ 0{,}866]$, $k$ di 30° = $[0{,}866;\ 0{,}5]$, prodotto $0{,}866 = \cos30°$. $(5,4)$: stesso risultato. $(4,1)$: angolo fra i due 90°, prodotto 0.

## La language modeling head

<a id="p-24"></a>
**Slide 24 · La language modeling head** — Dall'ultimo vettore della residual stream a una distribuzione sul token successivo.

<a id="p-25"></a>

### Slide 25 · Un language model predice il token successivo

$$P(\text{fish}\mid\text{Thanks for all the})$$

- **una distribuzione**: una probabilità per *ogni* possibile token successivo del vocabolario, che sommano a 1;
- **il contesto**: un modello n-gram condiziona sulle $n-1$ parole precedenti ([L4](L04-modelli-linguistici-n-gram.md#p-7)), l'LM feedforward su una finestra fissa ([L13](L13-reti-neurali.md#p-47)); un transformer su tutta la sua **finestra di contesto**, che nei modelli attuali va da centinaia di migliaia a milioni di token;
- **la testa** (*head*): il "circuito" aggiuntivo sopra i transformer block che fa language modeling. Il termine *head* indica in generale lo strato finale specifico del compito: per la classificazione si mette una testa diversa sopra gli stessi blocchi.

<a id="p-26"></a>

### Slide 26 · La testa: unembedding

La figura (Fig. 7.15 del libro): in basso i token $w_1,\dots,w_N$ entrano nel blocco $L$, che dà $h^L_1, h^L_2,\dots,h^L_N$ di forma $[1\times d]$; solo $h^L_N$ sale nella testa. Il riquadro evidenzia l'**Unembedding layer $U = E^\top$** $[d\times|V|]$ e i **logit** $u_1,\dots,u_{|V|}$ $[1\times|V|]$.

**Unembedding**: uno strato lineare da $h^L_N$, l'output dell'ultimo blocco all'ultimo token, $[1\times d]$, ai **logit** $u$, $[1\times|V|]$: un punteggio per ogni token del vocabolario. Ogni logit è il prodotto scalare di $h^L_N$ con una colonna di $U$.

È lo stesso schema "strato lineare + softmax" della regressione multinomiale ([L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-8)) e dell'uscita dell'LM feedforward ([L13](L13-reti-neurali.md#p-36)), con $|V|$ classi: decine di migliaia.

<a id="p-27"></a>

### Slide 27 · La testa: softmax

Stessa figura, ora il riquadro è sulla **Softmax** e sulle **word probabilities** $y_1,\dots,y_{|V|}$, forma $[1\times|V|]$.

- la softmax trasforma i logit $u$ nelle probabilità $y$ sul vocabolario: $y_k = e^{u_k}/\sum_j e^{u_j}$ ([L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-7));
- da $y$ si sceglie il token da generare: è il decoding, seconda parte della lezione.

Proprietà da ricordare: la softmax conserva l'ordine dei logit (il logit più alto ha la probabilità più alta) e dipende solo dalle **differenze** fra logit (aggiungere una costante a tutti non cambia niente). Sono le due proprietà che rendono la temperatura e il greedy decoding così semplici.

<a id="p-28"></a>

### Slide 28 · Weight tying

$$u = h^L_N\,E^\top\qquad y = \mathrm{softmax}(u)$$

- **La stessa matrice**: all'input $E$ $[|V|\times d]$ porta un one-hot in un embedding; nella testa la sua trasposta $E^\top$ $[d\times|V|]$ riporta un embedding al vocabolario.
- **Unembedding**: $E^\top$ fa il cammino inverso dell'embedding; in training $E$ impara a essere buona in **entrambe le mappe** (riceve gradiente da tutte e due le estremità). La testa può anche avere una sua matrice appresa, ma il **weight tying** è molto comune.

Lettura geometrica: il logit del token $k$ è $h\cdot E_k$, il prodotto scalare fra l'ultimo vettore e l'embedding di $k$. La testa favorisce i token il cui embedding è **più allineato** con $h$ (scheda 30).

> **Da saper fare: Quanti parametri risparmia**
>
> Senza tying la testa ha una matrice $U$ di $d\cdot|V|$ pesi, tanti quanti $E$. Con $|V| = 50.000$ e $d = 768$: 38,4 milioni risparmiati (esercizio 1c). Per GPT-2 small ($|V| = 50.257$, $d = 768$, 12 strati, 1024 posizioni): 124,4 milioni di parametri con tying, 163 milioni senza (esercizio 12).

> **Approfondimento: Per il progetto**
>
> Nel fine-tuning di un encoder per la classificazione (hate/offensive/neither) la testa di language modeling si **butta via** e si mette al suo posto una testa di classificazione: uno strato lineare $[d\times K]$ con $K$ classi (più una softmax), applicato al vettore del token [CLS] o a un pooling dei vettori. È piccola ($768\cdot3$ pesi) e parte da zero, mentre $E$ e i blocchi partono dal pretraining: per questo si usa un learning rate basso e poche epoche.

<a id="p-29"></a>

### Slide 29 · Esercizio in aula: la testa

Tre minuti, carta e penna. Vocabolario ed $E$ della scheda 13; all'ultimo token, *for*, l'ultimo blocco dà $h = [2, 0, 1]$.

1. i logit $u = hE^\top$: il prodotto scalare di $h$ con ogni riga di $E$;
2. le probabilità: la softmax dei sei logit (aiuti: $e^0 = 1$, $e^1\approx2{,}72$, $e^2\approx7{,}39$, $e^3\approx20{,}09$);
3. il token successivo più probabile.

Domanda finale: quale token ha l'embedding più simile ad $h$? Soluzione nella scheda successiva.

<a id="p-30"></a>

### Slide 30 · La testa a mano

Logit $u = hE^\top$ con $h = [2,0,1]$: So $2$, long $0$, and $1$, thanks $2$, for $1$, all $3$.

Esponenziali $7{,}39;\ 1;\ 2{,}72;\ 7{,}39;\ 2{,}72;\ 20{,}09$, somma $41{,}30$. Probabilità: **all 0,49**, So 0,18, thanks 0,18, and 0,07, for 0,07, long 0,02 (verificato: 0,486; 0,179; 0,179; 0,066; 0,066; 0,024).

**Ogni logit è il prodotto scalare di $h$ con l'embedding di un token**: *all* $= [1,0,1]$ è il più simile ad $h$ (anche con il coseno: 0,95 contro 0,89 di *So*). Il modello completa *So long and thanks for* **all**.

> **Da saper fare: Procedura**
>
> (1) un prodotto scalare per riga di $E$; (2) esponenziali; (3) somma; (4) divisione. Controllo: le probabilità sommano a 1 (0,49+0,18+0,18+0,07+0,07+0,02 = 1,01 per arrotondamento). Token con logit uguali (So e thanks; and e for) hanno probabilità uguali.

<a id="p-31"></a>

### Slide 31 · Un token o tutti i token

- **Inferenza**: la testa si calcola solo sull'**ultimo token** $N$, per predire il token in posizione $N+1$. Le altre posizioni servono comunque, come key e value dell'attenzione.
- **Training**: la testa predice il token successivo **a ogni posizione**, non solo all'ultima. Grazie alla maschera causale ([L14](L14-transformer-l-attenzione.md#p-56)) la posizione $i$ non vede i token dopo di lei: una finestra di $N$ token dà $N$ esempi di training in un solo passaggio (esercizio 7).
- **In cima alla corrente**: nei blocchi più alti la residual stream rappresenta soprattutto il **token successivo** ([L14](L14-transformer-l-attenzione.md#p-52)); la testa lo "legge".

> **Approfondimento: Logit lens**
>
> Oltre le slide. Se la testa "legge" la corrente in cima, si può provare a leggerla anche a metà: applicare layer norm finale e unembedding $E^\top$ al vettore $h^\ell_i$ di uno strato intermedio $\ell$ e guardare quale token verrebbe predetto. È il **logit lens** (nostalgebraist, 2020). Nei modelli tipo GPT-2 le predizioni degli strati bassi sono rumorose o ripetono il token corrente, e negli strati alti convergono gradualmente verso quella finale: conferma empirica dell'idea della corrente che passa dal token corrente al token successivo. Varianti più affidabili (tuned lens) imparano una piccola trasformazione per strato prima dell'unembedding.

<a id="p-32"></a>

### Slide 32 · Il modello intero

La figura (Fig. 7.16 del libro), un token $w_i$ dal basso verso l'alto:

- **codifica dell'input**: embedding del token ($E$) più quello della sua posizione, il nodo $\oplus$; ne esce $x^1_i$;
- **$L$ blocchi** (layer norm, attenzione, layer norm, feedforward): l'output di uno strato è l'input del successivo, $h^1_i = x^2_i$, $h^2_i = x^3_i$, ..., $h^{L-1}_i = x^L_i$;
- una **layer norm in più** (*extra layer norm*) sopra l'ultimo blocco, poi la testa: unembedding $U$ e softmax ("Language Modeling Head" in cima);
- si campiona il token da generare in posizione $i+1$ (la freccia verde verso $w_{i+1}$).

È il disegno da saper fare all'orale: tutto ciò che c'è fra $w_i$ e $w_{i+1}$, con le forme $[1\times d]$ nella corrente e $[1\times|V|]$ in cima. L'extra layer norm è tipica dell'architettura prenorm: l'ultimo blocco somma alla corrente senza normalizzare.

<a id="p-33"></a>

### Slide 33 · Decoder-only e transformer originale

La figura: a sinistra un **encoder** (pile di blocchi sopra *The green witch arrived*), a destra un **decoder** che genera *llegó la bruja verde </s>* partendo da *<s>*, ogni token generato rientra come input al passo dopo (frecce tratteggiate); linee di **cross-attention** portano l'output dell'encoder in ogni strato del decoder.

- il transformer originale (Vaswani et al., 2017) è un **encoder-decoder** per la traduzione automatica;
- **encoder**: legge tutta la frase sorgente (attenzione bidirezionale, senza maschera); **decoder**: genera la traduzione da sinistra a destra (attenzione causale) e guarda l'encoder con la cross-attention;
- un language model causale come quello di oggi è, grosso modo, la **metà decoder** senza cross-attention: un modello **decoder-only** (GPT e quasi tutti gli LLM attuali).

Il nome confonde perché storicamente il transformer è nato encoder-decoder e solo dopo il paradigma causale ha usato la sola parte decoder. Gli encoder-only (BERT) sono il capitolo 9 del libro.

<a id="p-34"></a>
**Slide 34 · Pausa** — Dieci minuti; dopo: il decoding, dal greedy al top-p.

## Greedy e random sampling

<a id="p-35"></a>
**Slide 35 · Greedy e random sampling** — I due estremi del decoding: sempre il token più probabile, o un token estratto dalla distribuzione.

<a id="p-36"></a>

### Slide 36 · Decoding

**Decoding**: scegliere il token da generare a partire dalle probabilità del modello.

- **autoregressivo**: da sinistra a destra, ogni token condizionato sulle scelte precedenti; si chiama generazione **causale** o **autoregressiva**;
- **il ciclo**: calcola $y$, scegli un token, aggiungilo all'input, ripeti.

Esempio: *So long and thanks for* $\to$ *all*; *So long and thanks for all* $\to$ *the*; *So long and thanks for all the* $\to$ *fish*.

Due osservazioni: il modello è sempre lo stesso, cambia solo la **regola di scelta**; e ogni scelta diventa contesto per le successive, quindi un errore all'inizio si propaga. Il libro nota che "autoregressivo" è usato in senso lato: un modello autoregressivo in statistica è lineare, un transformer no.

<a id="p-37"></a>

### Slide 37 · L'esempio di riferimento

La figura (Fig. 7.17 del libro): dopo *So long and thanks for* il transformer dà quattro logit, $u$ = all 1,2; the 0,9; your 0,1; that -0,5; la softmax li trasforma in $y$ = **all 0,44; the 0,33; your 0,15; that 0,08**. Vocabolario di soli 4 token, per illustrazione.

Verificato: softmax esatta $0{,}443;\ 0{,}328;\ 0{,}148;\ 0{,}081$. **Queste quattro probabilità servono per tutti i metodi di oggi**: conviene ricordarle, con le cumulate $0{,}44;\ 0{,}77;\ 0{,}92;\ 1{,}00$.

<a id="p-38"></a>

### Slide 38 · Greedy decoding

$$\hat w_t = \operatorname{argmax}_{w\in V} P(w\mid w_{\lt t})$$

**Greedy decoding**: sempre il token più probabile, l'argmax. Nella figura la probabilità 0,44 di *all* è cerchiata: nel nostro esempio si genera **all**.

"Greedy" (goloso) perché fa la scelta **localmente ottima** a ogni passo, senza chiedersi se a posteriori era la migliore per l'intera sequenza (scheda 40). Poiché la softmax conserva l'ordine, l'argmax delle probabilità è l'argmax dei logit: per il greedy la softmax non serve nemmeno.

<a id="p-39"></a>

### Slide 39 · Greedy decoding: i difetti

- **Deterministico**: stesso contesto e stesso modello danno sempre esattamente la stessa stringa.
- **Generico e ripetitivo**: i token scelti sono, per definizione, i più prevedibili. Spesso il testo entra in un **ciclo**: nel notebook (cella 16) un modello bigram con greedy produce *the default is a string to the default is a string to ...* all'infinito.

**In pratica i large language model non usano il greedy decoding** per generare testo libero. Resta utile quando serve riproducibilità o una sola risposta "più probabile" (per esempio estrazione di un'etichetta).

<a id="p-40"></a>

### Slide 40 · Il problema del greedy decoding

Un esempio inventato del libro (capitolo 13): un albero con tre passi $t_1, t_2, t_3$; a ogni passo la probabilità del token successivo dato il prefisso. Da *start*: yes 0,5, ok 0,4, EOS 0,1. Dopo *yes*: ok 0,3, yes 0,4, EOS 0,3. Dopo *ok*: ok 0,7, yes 0,2, EOS 0,1. Poi EOS con probabilità 1.

- **greedy** (in rosso): yes (0,5), poi yes (0,4), poi EOS: $P = 0{,}5\cdot0{,}4\cdot1 = 0{,}20$;
- **ok ok EOS** (in blu): $0{,}4\cdot0{,}7\cdot1 = 0{,}28$, la sequenza più probabile.

**Il primo token più probabile non è sempre l'inizio della sequenza più probabile.** La probabilità di una sequenza è il prodotto delle probabilità condizionate (regola della catena, [L4](L04-modelli-linguistici-n-gram.md#p-11)): un primo passo un po' meno probabile può aprire continuazioni molto più probabili.

<a id="p-41"></a>

### Slide 41 · Beam search

Stesso albero, con le probabilità delle sequenze a destra: ok ok EOS 0,28; ok yes EOS 0,08; ok EOS 0,04; yes ok EOS 0,15; yes yes EOS 0,20; yes EOS 0,15 (tutti verificati).

**Beam search**: a ogni passo si tengono le $k$ migliori sequenze parziali (*ipotesi*); $k$ è la **beam width**, qui $k = 2$.

1. passo 1: si tengono yes (0,5) e ok (0,4);
2. passo 2: si estendono entrambe con ogni token (6 candidati, probabilità = prodotto lungo il cammino) e si tengono le 2 migliori: ok ok (0,28) e yes yes (0,20);
3. passo 3: entrambe finiscono con EOS. La migliore è **ok ok EOS**, la sequenza che il greedy aveva perso.

Il greedy è la beam search con $k = 1$. Si usa nella traduzione automatica (capitolo 13 del libro), compito molto vincolato in cui serve la traduzione più probabile; per la generazione libera produce testi piatti come il greedy.

> **Da saper fare: Beam search a mano**
>
> A ogni passo: (1) estendi ogni ipotesi con ogni token; (2) probabilità = probabilità dell'ipotesi per quella del token; (3) ordina e tieni le prime $k$; (4) un'ipotesi che termina con EOS è completa. Alla fine scegli la completa con probabilità più alta. In pratica si sommano log-probabilità e si normalizza per la lunghezza, altrimenti le sequenze corte sono favorite (ogni fattore è minore di 1).

<a id="p-42"></a>

### Slide 42 · Random sampling

**Random sampling** (o random multinomial sampling): si sceglie il token successivo **secondo la sua probabilità**. I token più probabili escono più spesso, ma qualunque token può uscire. Si ripete fino al token di fine sequenza (EOS). L'idea risale a Shannon (1948).

A destra l'algoritmo del libro: $i\leftarrow1$; $w_i\sim p(w)$; finché $w_i \ne$ EOS: $i\leftarrow i+1$, $w_i\sim p(w_i\mid w_{\lt i})$. Nella figura il token estratto è *the* (0,33), non il più probabile.

È esattamente il campionamento da modelli n-gram della [L4](L04-modelli-linguistici-n-gram.md#p-37), con il transformer al posto delle conte. **È il modo più comune di fare decoding dai LLM**, con le modifiche delle prossime schede.

<a id="p-43"></a>

### Slide 43 · Campionare come lanciare un dado

La figura: il segmento $[0,1)$ diviso in quattro intervalli lunghi quanto le probabilità: all $[0;\ 0{,}44)$, the $[0{,}44;\ 0{,}77)$, your $[0{,}77;\ 0{,}92)$, that $[0{,}92;\ 1)$. Un numero casuale $r = 0{,}81$ cade nell'intervallo di **your**.

- gli estremi degli intervalli sono le **probabilità cumulate**;
- il token estratto è il primo la cui cumulata supera $r$;
- su molte estrazioni *all* esce il 44% delle volte, *that* l'8% (nel notebook, 10.000 estrazioni: 0,438 e 0,085).

> **Da saper fare: Campionare a mano**
>
> Ordine fissato dei token, cumulate, primo indice con cumulata $\gt r$. Esercizio 8: logit 2; 1; 0,5; -1 danno probabilità 0,609; 0,224; 0,136; 0,030, cumulate 0,609; 0,834; 0,970; 1: $r = 0{,}65$ dà *floor*, $r = 0{,}98$ dà *moon*.

<a id="p-44"></a>

### Slide 44 · Il problema del random sampling

**La coda**: la distribuzione ha molti token strani e poco probabili; ciascuno è raro, ma insieme sono una parte non trascurabile della massa.

Esempio della slide: 3 token probabili con 0,70 in totale e 10.000 token improbabili con 0,00003 ciascuno, cioè $10.000\cdot0{,}00003 = 0{,}30$ in totale. Quindi **3 token su 10 vengono dalla coda**: in una frase di 20 token ci si aspettano circa 6 token strani, e ognuno diventa contesto per i successivi, facendo deragliare il testo.

**Il greedy decoding è troppo noioso, il random sampling troppo casuale.** Serve qualcosa in mezzo: non sempre il primo, ma senza scendere nella coda.

## Temperatura, top-k, top-p

<a id="p-45"></a>
**Slide 45 · Temperature, top-k, top-p** — Tre modi per modificare la distribuzione prima di campionare.

<a id="p-46"></a>

### Slide 46 · Qualità e diversità

Temperatura, top-k e top-p servono a bilanciare due obiettivi in conflitto, **qualità** e **diversità**:

- **le parole più probabili**: giudicate dalle persone più accurate, più coerenti, più fattuali; ma anche più noiose e ripetitive;
- **le parole di probabilità media**: più creative e varie; ma meno fattuali e più a rischio di incoerenza.

Tutti e tre i metodi tagliano o riducono la coda (contro l'eccesso di casualità) senza ridursi all'argmax (contro la noia).

<a id="p-47"></a>

### Slide 47 · Temperature sampling

$$y = \mathrm{softmax}(u)\qquad\longrightarrow\qquad y = \mathrm{softmax}(u/\tau)$$

Si dividono i logit per la **temperatura** $\tau$ prima della softmax.

- $\tau\lt1$: logit più grandi in valore assoluto e differenze amplificate; la softmax spinge i valori alti verso 1 e quelli bassi verso 0. Per $\tau\to0$: **greedy decoding**.
- $\tau\gt1$: logit più piccoli, distribuzione più piatta, verso l'**uniforme**.
- $\tau = 1$: la softmax normale.

Il nome viene dalla termodinamica (distribuzione di Boltzmann): un sistema caldo esplora molti stati, uno freddo resta in quelli a bassa energia. Il libro chiama *low-temperature sampling* il caso $\tau\in(0,1]$.

> **Da saper fare: Perché $\tau\to0$ dà il greedy**
>
> $y_k = \dfrac{e^{u_k/\tau}}{\sum_j e^{u_j/\tau}} = \dfrac{1}{\sum_j e^{(u_j-u_k)/\tau}}$. Se $k$ è il logit massimo (unico), per $j\ne k$ si ha $u_j-u_k\lt0$ e $e^{(u_j-u_k)/\tau}\to0$: $y_k\to1$, gli altri $\to0$. Per $\tau\to\infty$ tutti gli esponenti $\to0$ e $y_k\to1/|V|$.

<a id="p-48"></a>

### Slide 48 · Esercizio in aula: temperatura

Tre minuti. Logit all 1,2; the 0,9; your 0,1; that -0,5; $\tau = 0{,}5$.

1. dividi i logit per $\tau$;
2. calcola la softmax (aiuti: $e^{2{,}4}\approx11{,}02$, $e^{1{,}8}\approx6{,}05$, $e^{0{,}2}\approx1{,}22$, $e^{-1}\approx0{,}37$);
3. confronta con $\tau = 1$: 0,44; 0,33; 0,15; 0,08.

Domanda: con $\tau = 0{,}5$ la distribuzione è più appuntita o più piatta? Soluzione nella scheda successiva.

<a id="p-49"></a>

### Slide 49 · Temperatura a mano ($\tau = 0{,}5$)

|  | all | the | your | that |
| --- | --- | --- | --- | --- |
| logit | 1,2 | 0,9 | 0,1 | -0,5 |
| $\div0{,}5$ | 2,4 | 1,8 | 0,2 | -1,0 |
| exp | 11,02 | 6,05 | 1,22 | 0,37 |
| prob. $\tau = 0{,}5$ | **0,59** | **0,32** | **0,07** | **0,02** |
| prob. $\tau = 1$ | 0,44 | 0,33 | 0,15 | 0,08 |

Somma degli esponenziali 18,66. Verificato: $0{,}591;\ 0{,}324;\ 0{,}065;\ 0{,}020$.

Con $\tau = 0{,}5$ il primo token sale da 0,44 a 0,59, *that* scende da 0,08 a 0,02: **più appuntita**. Notare che *the* resta quasi uguale (0,33 $\to$ 0,32): il secondo token perde poco, la massa si sposta dalla coda verso il primo. **L'ordine dei token non cambia mai**, solo quanto la distribuzione è concentrata (dividere per $\tau\gt0$ conserva l'ordine dei logit).

<a id="p-50"></a>

### Slide 50 · Temperatura: il quadro completo

Cinque istogrammi degli stessi logit con temperature diverse (tutti i valori verificati):

| $\tau$ | all | the | your | that |
| --- | --- | --- | --- | --- |
| 0,1 (quasi greedy) | 0,95 | 0,05 | 0,00 | 0,00 |
| 0,5 | 0,59 | 0,32 | 0,07 | 0,02 |
| 1 (softmax normale) | 0,44 | 0,33 | 0,15 | 0,08 |
| 2 | 0,35 | 0,30 | 0,20 | 0,15 |
| 10 (quasi uniforme) | 0,27 | 0,26 | 0,24 | 0,23 |

$\tau\lt1$: il token più probabile cresce e gli altri si riducono, verso il greedy. $\tau\gt1$: le probabilità si livellano, verso l'uniforme (0,25 ciascuna). **$\tau$ più bassa: più qualità, meno diversità; più alta: il contrario.**

La figura 7.21 del libro usa $\tau$ = 0,1; 0,5; 1; 10; 100; la slide sostituisce 100 (tutto 0,25) con $\tau = 2$, più utile come esempio intermedio.

<a id="p-51"></a>

### Slide 51 · Top-k sampling

L'algoritmo del libro:

1. si sceglie in anticipo un numero $k$;
2. per ogni token del vocabolario si calcola $p(w_t\mid w_{\lt t})$;
3. si ordinano i token per probabilità e si scartano tutti tranne i primi $k$;
4. si **rinormalizzano** le $k$ probabilità perché sommino a 1;
5. si campiona fra i $k$ rimasti secondo le probabilità rinormalizzate.

**$k = 1$: top-k è il greedy decoding.** $k = |V|$: è il random sampling. Con $k\gt1$ a volte esce un token che non è il più probabile ma è comunque abbastanza probabile: testo più vario ma ancora di buona qualità, e la coda è tagliata via del tutto.

<a id="p-52"></a>

### Slide 52 · Top-k a mano ($k = 2$)

- probabilità: all 0,44; the 0,33; your 0,15; that 0,08;
- si tengono i primi 2: all 0,44; the 0,33 (somma 0,77);
- si rinormalizza dividendo per 0,77: **all 0,57; the 0,43** (verificato: $0{,}44/0{,}77 = 0{,}571$, $0{,}33/0{,}77 = 0{,}429$).

*your* e *that* non possono più essere generati; *the* ora esce il 43% delle volte invece del 33%. La rinormalizzazione conserva i **rapporti** fra i token rimasti (0,57/0,43 = 0,44/0,33).

<a id="p-53"></a>

### Slide 53 · Il problema di un k fisso

Due istogrammi dei primi 20 token ordinati per probabilità, con i primi 5 in blu.

- **contesto sicuro** (sinistra): probabilità che si dimezzano a ogni token, 0,50; 0,25; 0,125; ...; i primi 5 tengono il **97%** della massa ($0{,}5+0{,}25+0{,}125+0{,}0625+0{,}03125 = 0{,}969$);
- **contesto aperto** (destra): barre basse e quasi uguali (circa 0,08 che scende lentamente a 0,03); i primi 5 tengono solo il **35%**.

$k$ è fisso ma la forma della distribuzione cambia da contesto a contesto: lo stesso $k = 5$ nel primo caso lascia entrare token marginali, nel secondo esclude continuazioni perfettamente plausibili che insieme valgono il 65% della massa.

<a id="p-54"></a>

### Slide 54 · Top-p (nucleus) sampling

$$\sum_{w\in V^{(p)}} P(w\mid w_{\lt t}) \ge p$$

$V^{(p)}$ è il **più piccolo insieme di parole** (prese in ordine di probabilità decrescente) la cui probabilità totale è almeno $p$. Si rinormalizza dentro $V^{(p)}$ e si campiona.

- **l'idea**: tenere la parte $p$ della **massa di probabilità**, non le prime $k$ parole (Holtzman et al., 2020; detto anche *nucleus sampling*);
- **adattivo**: l'insieme dei candidati si allarga quando il modello è incerto e si restringe quando è sicuro.

**Comune in pratica: prima top-k come filtro rigido** (elimina comunque la spazzatura), **poi top-p** per adattarsi alla confidenza del modello. Valori tipici nelle API: $p$ fra 0,9 e 0,95.

<a id="p-55"></a>

### Slide 55 · Esercizio in aula: top-p

Tre minuti. Probabilità all 0,44; the 0,33; your 0,15; that 0,08.

1. le probabilità cumulate, dal token più probabile;
2. $p = 0{,}9$: quali token restano? Con quali probabilità rinormalizzate?
3. $p = 0{,}75$: quali token restano?

Domanda: con $p = 0{,}75$, quale altro metodo dà lo stesso risultato? Soluzione nella scheda successiva.

<a id="p-56"></a>

### Slide 56 · Top-p a mano

Ordinate: all 0,44; the 0,33; your 0,15; that 0,08. Cumulate: **0,44; 0,77; 0,92; 1,00**.

- $p = 0{,}9$: la prima cumulata $\ge0{,}9$ è 0,92, quindi si tengono **all, the, your**. Rinormalizzate (divise per 0,92): **all 0,48; the 0,36; your 0,16** (verificato: 0,478; 0,359; 0,163).
- $p = 0{,}75$: già 0,77 $\ge$ 0,75, si tengono **all, the**: lo stesso risultato di **top-2** (scheda 52).

In una distribuzione più piatta lo stesso $p$ terrebbe più token; in una molto appuntita (per esempio $\tau$ basso) potrebbe tenerne uno solo e diventare greedy.

> **Da saper fare: Errore tipico**
>
> Il criterio è "il più piccolo insieme con massa **almeno** $p$": si include il token che fa superare la soglia. Con $p = 0{,}9$ non ci si ferma a all+the (0,77 $\lt$ 0,9), si aggiunge your. Se una cumulata è esattamente uguale a $p$, ci si ferma lì.

<a id="p-57"></a>

### Slide 57 · I metodi di decoding a confronto

| metodo | sceglie | nota |
| --- | --- | --- |
| greedy | il token più probabile | deterministico, ripetitivo |
| random | un token campionato dall'intera distribuzione | token strani dalla coda |
| temperatura | logit divisi per $\tau$, poi campionamento | $\tau\lt1$ verso il greedy, $\tau\gt1$ verso l'uniforme |
| top-k | campionamento fra i $k$ più probabili, rinormalizzati | $k$ uguale in ogni contesto |
| top-p | campionamento nel più piccolo insieme con massa $\ge p$ | si adatta alla confidenza del modello |

**Tutti partono dalla stessa distribuzione $y$: cambiano solo il modo di scegliere.** Nessuno richiede di riaddestrare il modello; si possono combinare (tipicamente temperatura, poi top-k, poi top-p).

<a id="p-58"></a>

### Slide 58 · Riepilogo e prossima lezione

Riepilogo:

- **embedding dei token**: righe di $E$ $[|V|\times d]$, selezionate da vettori one-hot;
- **posizioni**: apprese, sinusoidali, o relative (RoPE);
- **la testa**: logit $u = hE^\top$ (weight tying), poi softmax;
- **decoder-only**: la metà decoder dell'encoder-decoder originale;
- **greedy** è noioso, **random sampling** troppo casuale;
- **temperatura, top-k, top-p**: qualità contro diversità.

**Prossima lezione**: laboratorio *n-grams and nanoGPT* su Shakespeare, sessione con notebook con Andrea Ceni.

## Notebook

Commento al notebook del corso `HLT-L15-transformer-decoding.ipynb` (il notebook è del docente e non è incluso).

Notebook di accompagnamento (solo `numpy` e libreria standard, pochi secondi): rifà gli esempi delle slide (embedding e testa con il vocabolario giocattolo, *dog bites man*, posizioni sinusoidali, RoPE, i cinque metodi di decoding sui logit del libro), applica i metodi di decoding a un modello bigram vero e ricalcola gli esercizi 1, 2, 4, 5, 6 e 8-10 della scheda. Rieseguito da capo: tutti gli output coincidono con quelli salvati tranne la sezione 6, che come dichiarato dipende dalla versione di Python (il corpus sono i docstring della libreria standard); nessun errore e **nessun bug**. Non produce figure.

### Notebook 1 · Embedding e testa sul vocabolario giocattolo

```python
vocab = ["So", "long", "and", "thanks", "for", "all"]
E = np.array([[1,0,0],[0,1,0],[0,0,1],[1,1,0],[0,1,1],[1,0,1]], float)
onehot = np.zeros(len(vocab)); onehot[vocab.index("thanks")] = 1
print(onehot @ E)
ids = [vocab.index(w) for w in "So long and thanks for".split()]
print(E[ids])
h = np.array([2, 0, 1], float)
u = h @ E.T            # logits, weight tying
y = softmax(u)
```

Output:

```text
one-hot of thanks: [0. 0. 0. 1. 0. 0.]   one-hot x E = [1. 1. 0.]
ids (from 0): [0, 1, 2, 3, 4]
all     logit  3.0  probability 0.486
So      logit  2.0  probability 0.179
thanks  logit  2.0  probability 0.179
and     logit  1.0  probability 0.066
for     logit  1.0  probability 0.066
long    logit  0.0  probability 0.024
```

Le schede [13](L15-transformer-embedding-lm-head-e-decoding.md#p-13) e [30](L15-transformer-embedding-lm-head-e-decoding.md#p-30) in codice. Due modi di prendere gli embedding: il prodotto `onehot @ E` (la forma matematica) e l'indicizzazione `E[ids]` (quella usata davvero). Attenzione agli **indici**: in Python partono da 0, quindi *thanks* ha indice 3 qui e id 4 nella slide.

La testa è una riga: `h @ E.T` è il weight tying. La `softmax` sottrae il massimo prima di esponenziare (stabilità numerica, risultato invariato). Output identico alla slide: *all* 0,486.

### Notebook 2 · Perché servono le posizioni

```python
emb = {"dog": [1, 0], "bites": [0, 1], "man": [1, 1], ".": [0.5, 0.5]}
pos = np.array([[0.1, 0], [0.2, 0], [0.3, 0], [0.4, 0]])

def simplified_attention_last(X):
    weights = softmax(X @ X[-1])
    return weights, weights @ X
```

Output:

```text
dog bites man .  without positions: output [0.677 0.677]   with positions: output [1.    0.679]
man bites dog .  without positions: output [0.677 0.677]   with positions: output [0.963 0.627]
```

La [scheda 15](L15-transformer-embedding-lm-head-e-decoding.md#p-15) con numeri: attenzione semplificata della L14 (punteggi = prodotti scalari con l'ultimo token, il punto) sulle due frasi. Senza posizioni l'output è identico, $[0{,}677;\ 0{,}677]$: stessi vettori, stessi punteggi, solo permutati. Con le posizioni (sommate, `X + pos`) gli output diventano diversi. È l'esercizio 2 della scheda.

### Notebook 3 · Posizioni sinusoidali

```python
def sinusoidal(p, d):
    i = np.arange(d // 2)
    w = 1 / 10000 ** (2 * i / d)
    v = np.zeros(d)
    v[0::2], v[1::2] = np.sin(p * w), np.cos(p * w)
    return v
```

Output:

```text
d = 4, position 0: [0. 1. 0. 1.]
d = 4, position 1: [0.841 0.54  0.01  1.   ]
d = 4, position 2: [ 0.909 -0.416  0.02   1.   ]
d =  4: dot(PE(4), PE(5)) =   1.54   dot(PE(4), PE(17)) =   1.90
d = 64: dot(PE(4), PE(5)) =  30.92   dot(PE(4), PE(17)) =  21.01
only the distance matters: 21.00672 21.00672
```

La formula della [scheda 19](L15-transformer-embedding-lm-head-e-decoding.md#p-19): `v[0::2]` sono le dimensioni pari (seni), `v[1::2]` le dispari (coseni), con la stessa frequenza per ogni coppia. I vettori per $p = 0,1,2$ sono quelli della [scheda 20](L15-transformer-embedding-lm-head-e-decoding.md#p-20); con $d = 64$ i prodotti 30,92 e 21,01 sono quelli della [scheda 21](L15-transformer-embedding-lm-head-e-decoding.md#p-21).

Due risultati da notare: con $d = 4$ la posizione 4 risulta più "vicina" a 17 che a 5 (1,90 contro 1,54), perché la coppia veloce ha periodo $2\pi$ (esercizio 4); e $PE(4)\cdot PE(17) = PE(30)\cdot PE(43)$, la dipendenza dalla sola distanza.

### Notebook 4 · RoPE

```python
def rope(x, position, base=10000):
    d = len(x); i = np.arange(d // 2)
    theta = position / base ** (2 * i / d)
    x1, x2 = x[0::2], x[1::2]
    out = np.empty(d)
    out[0::2] = x1 * np.cos(theta) - x2 * np.sin(theta)
    out[1::2] = x1 * np.sin(theta) + x2 * np.cos(theta)
    return out
```

Output:

```text
query at   2, key at   1 (distance 1): score -1.6954
query at   5, key at   4 (distance 1): score -1.6954
query at 105, key at 104 (distance 1): score -1.6954
query at   5, key at   1 (distance 4): score -1.3021
```

La rotazione della [scheda 23](L15-transformer-embedding-lm-head-e-decoding.md#p-23) per esteso: ogni coppia $(x_{2i}, x_{2i+1})$ viene ruotata di un angolo $\text{posizione}\cdot\theta_i$, con le stesse frequenze delle sinusoidali; le due righe `out[...]` sono il prodotto per la matrice di rotazione $2\times2$. Con query e key casuali di dimensione 8 il punteggio a distanza 1 è lo stesso ($-1{,}6954$) ovunque si trovino i due token, a distanza 4 è diverso.

Nota: nel modello vero RoPE si applica alle query e alle key *dopo* le proiezioni $W^Q$, $W^K$, in ogni testa e in ogni strato; qui è mostrata solo la rotazione.

### Notebook 5 · I cinque metodi di decoding sull'esempio del libro

```python
def sample(probs, rng):
    r = rng.random()
    return int(np.searchsorted(np.cumsum(probs), r, side="right"))

def with_temperature(logits, tau):
    return softmax(np.asarray(logits) / tau)

def top_k(probs, k):
    keep = np.argsort(-probs)[:k]
    out = np.zeros_like(probs); out[keep] = probs[keep]
    return out / out.sum()

def top_p(probs, p):
    order = np.argsort(-probs)
    n = int(np.searchsorted(np.cumsum(probs[order]), p) + 1)
    out = np.zeros_like(probs); out[order[:n]] = probs[order[:n]]
    return out / out.sum()
```

Output:

```text
probabilities {'all': 0.443, 'the': 0.328, 'your': 0.148, 'that': 0.081}
greedy: all
random sampling  distribution [0.443 0.328 0.148 0.081]   frequencies in 10,000 draws [0.438 0.33  0.147 0.085]
temperature 0.5  distribution [0.591 0.324 0.065 0.02 ]   frequencies in 10,000 draws [0.588 0.323 0.07  0.019]
temperature 2    distribution [0.349 0.3   0.201 0.149]   frequencies in 10,000 draws [0.346 0.3   0.201 0.152]
top-k, k = 2     distribution [0.574 0.426 0.    0.   ]   frequencies in 10,000 draws [0.571 0.429 0.    0.   ]
top-p, p = 0.9   distribution [0.482 0.357 0.161 0.   ]   frequencies in 10,000 draws [0.479 0.36  0.161 0.   ]
```

Ogni metodo è una funzione di poche righe, e conviene leggerle come definizioni:

- `sample` è il dado della [scheda 43](L15-transformer-embedding-lm-head-e-decoding.md#p-43): `searchsorted(..., side="right")` trova il primo token con cumulata $\gt r$;
- `top_k` azzera tutto tranne i $k$ più probabili e rinormalizza;
- `top_p`: `searchsorted` (lato sinistro) dà il primo indice con cumulata $\ge p$; il `+ 1` include quel token, cioè "il più piccolo insieme con massa almeno $p$".

Le distribuzioni coincidono con le schede 49, 50, 52 e 56 (con le probabilità esatte invece di quelle arrotondate: top-k dà 0,574 invece di 0,57); le frequenze su 10.000 estrazioni le approssimano bene.

### Notebook 6 · Decoding da un modello bigram vero

```python
def next_logits(word):
    cands = bigrams[word]
    words_ = list(cands)
    counts = np.array([cands[w] for w in words_], float)
    return words_, np.log(counts / counts.sum())

for method in ("greedy", ("sample", None), ("temperature", 0.5), ("temperature", 1.5), ("top-k", 5), ("top-p", 0.7)):
    print(method, generate('the', method))
```

Output:

```text
42938 tokens, 3609 types
greedy                 the default is a string to the default is a string to the default is a string to the default is a string to the default
('sample', None)       the parser add argument list after g typing import subprocess getstatusoutput bin at runtime arguments setup a reference its sort keys and its return x noise
('temperature', 0.5)   the argument is not str id readonly int tuple of a negative integer l and return the name of the caller can be used to the
('top-k', 5)           the file descriptor referring to be passed in the current line number of an error message formatter instances are used to create a b return a
```

I metodi di decoding funzionano con **qualunque** language model che dia una distribuzione sul token successivo: qui un bigram sui docstring della libreria standard di Python (lo stesso corpus del notebook della [L4](L04-modelli-linguistici-n-gram.md#p-37)), con le log-probabilità come logit (la softmax delle log-probabilità restituisce le probabilità).

Il risultato illustra la [scheda 39](L15-transformer-embedding-lm-head-e-decoding.md#p-39): il **greedy** entra subito in un ciclo (*the default is a string to ...*), il campionamento puro e la temperatura alta pescano parole rare, temperatura bassa, top-k e top-p restano sulle continuazioni frequenti ma variano. Nessun testo ha senso perché il bigram vede una sola parola.

> **Approfondimento: Output diverso sul proprio computer**
>
> Rieseguito con Python 3.11 il corpus ha 40.629 token e 3.444 tipi (contro 42.938 e 3.609 salvati) e i testi campionati cambiano; il greedy dà la stessa frase ripetuta. Non è un bug: il notebook avvisa che la sezione 6 dipende dalla versione di Python installata.

### Notebook 7 · Controlli della scheda esercizi

```python
# esercizio 4: sinusoidali, d = 4
for p in (4, 5, 17): print(sinusoidal(p, 4))
# esercizio 5: RoPE in 2D, 30 gradi per posizione
for m, n in ((2, 1), (5, 4), (4, 1)):
    qm, kn = rot([1, 0], 30 * m), rot([1, 0], 30 * n)
# esercizi 8-10: logit 2.0, 1.0, 0.5, -1.0 (mat, floor, roof, moon)
# ... esercizi 1, 2, 6
```

Output:

```text
exercise 1  for x E = [0. 1. 1.]  weights of E with |V| = 50,000, d = 768: 38400000
exercise 4  PE(4) = [-0.757 -0.654  0.04   0.999]
exercise 4  PE(5) = [-0.959  0.284  0.05   0.999]
exercise 4  PE(17) = [-0.961 -0.275  0.169  0.986]
            dot(4, 5) = 1.540, dot(4, 17) = 1.899
exercise 5  (m, n) = (2, 1): dot product 0.866
exercise 5  (m, n) = (5, 4): dot product 0.866
exercise 5  (m, n) = (4, 1): dot product 0.000
exercise 6  logits [0. 2. 1. 2. 3. 1.]  for 0.486
exercise 8  probabilities [0.609 0.224 0.136 0.03 ]  r = 0.65 -> floor  r = 0.98 -> moon
exercise 9  tau 0.5 [0.842 0.114 0.042 0.002]  tau 2 [0.434 0.263 0.205 0.097]
exercise 10 k = 2 [0.731 0.269 0.    0.   ]  k = 3 [0.629 0.231 0.14  0.   ]
            p = 0.8 [0.731 0.269 0.    0.   ]  p = 0.95 [0.629 0.231 0.14  0.   ]
```

Ricalcola gli esercizi numerici della scheda con le funzioni definite sopra: le soluzioni nella sezione Studio sono state verificate anche con un calcolo indipendente e coincidono. Da usare *dopo* aver fatto i conti a mano. Gli esercizi 3, 7 e 11 sono concettuali o di conteggio e non compaiono.

## Studio ed esercizi

### Guida allo studio (circa 3 h 40 min)

**Dall'id al vettore** (25 min)

Schede 1-13. Saper dire che cosa è $E$ (forma, una riga per token, appresa), perché selezionare una riga = moltiplicare per un one-hot, la forma $[N\times d]$ della sequenza, e contare i pesi ($|V|\cdot d$). Ricordare che $V$ qui è il vocabolario. Libro §7.4, pp. 191-192. Esercizio 1.

**Posizioni** (50 min)

Schede 14-23. Perché l'attenzione è cieca all'ordine (*dog bites man*), posizioni apprese e loro limiti, formula sinusoidale con frequenze e calcolo a mano con $d = 4$, la dimostrazione che il prodotto scalare dipende solo da $p-q$, l'idea di RoPE con le rotazioni. Libro pp. 192-193 (la formula sinusoidale e RoPE sono aggiunte della lezione). Esercizi 2, 3, 4, 5.

**La language modeling head** (35 min)

Schede 24-33. Le due equazioni $u = hE^\top$, $y = \mathrm{softmax}(u)$ con le forme, weight tying e il risparmio di parametri, la testa a mano (scheda 30), inferenza vs training, il disegno del modello completo con l'extra layer norm, decoder-only vs encoder-decoder. Libro §7.5, pp. 193-196. Esercizi 6, 7, 12.

**Greedy, beam search, random sampling** (30 min)

Schede 35-44. Il ciclo autoregressivo, l'argmax, perché il greedy è deterministico e ripetitivo, l'albero yes/ok (0,20 contro 0,28) e la beam search con $k = 2$, il campionamento con le cumulate, il problema della coda (0,30 della massa). Libro §7.6.1-7.6.2, pp. 196-198. Esercizi 8, 13.

**Temperatura, top-k, top-p** (40 min)

Schede 45-57. Saper rifare senza guardare i conti delle schede 49, 52 e 56 sull'esempio all/the/your/that; spiegare i limiti $\tau\to0$ e $\tau\to\infty$, perché l'ordine non cambia, il problema del $k$ fisso e perché top-p è adattivo; tabella riassuntiva della scheda 57. Libro §7.6.3-7.6.4, pp. 198-201. Esercizi 9, 10, 11, 14.

**Notebook e ripasso orale** (40 min)

Eseguire il notebook accanto alle schede: celle 2, 5, 7, 10 e 13 riproducono gli esempi; nella cella 16 provare altre temperature e altri $k$, $p$ e semi. Controllare gli esercizi con la cella 19. Chiudere con le domande d'orale, in particolare il disegno del modello completo e il confronto fra i metodi di decoding.

### Esercizi

#### Esercizio 1 (scheda L15): la matrice di embedding

Vocabolario della lezione con $d = 3$: So $[1,0,0]$, long $[0,1,0]$, and $[0,0,1]$, thanks $[1,1,0]$, for $[0,1,1]$, all $[1,0,1]$ (id da 1 a 6).

1. Scrivi il one-hot di *for* e calcola il suo prodotto con $E$.
2. Scrivi la matrice dei one-hot dell'input *long thanks all* e la matrice dei suoi embedding. Quali forme hanno?
3. Un modello vero ha $|V| = 50.000$ e $d = 768$. Quanti pesi ha $E$? Quanti pesi risparmia il modello con il weight tying?

<details><summary>Soluzione</summary>

(a) $[0,0,0,0,1,0]$; il prodotto seleziona la riga 5: $[0,1,1]$.

(b) One-hot: righe $[0,1,0,0,0,0]$, $[0,0,0,1,0,0]$, $[0,0,0,0,0,1]$, forma $[3\times6]$ ($N\times|V|$). Embedding: righe $[0,1,0]$, $[1,1,0]$, $[1,0,1]$, forma $[3\times3]$ ($N\times d$).

(c) $50.000\cdot768 = 38.400.000$ pesi. Senza tying la testa avrebbe una matrice $[768\times50.000]$ con altrettanti pesi: il tying ne risparmia **38,4 milioni**.

</details>

#### Esercizio 2 (scheda L15): perché le posizioni

Embedding giocattolo con $d = 2$: dog $[1,0]$, bites $[0,1]$, man $[1,1]$, punto $[0{,}5;\ 0{,}5]$.

1. Con l'attenzione semplificata della L14 (punteggi = prodotti scalari con il token corrente, pesi = softmax, output = somma pesata degli input) calcola l'output per il punto in *dog bites man .* e in *man bites dog .*, senza posizioni.
2. Aggiungi gli embedding di posizione $[0{,}1;0]$, $[0{,}2;0]$, $[0{,}3;0]$, $[0{,}4;0]$ per le posizioni 1-4 e ricalcola l'output del punto nelle due frasi.
3. Che cosa mostrano (a) e (b)?

<details><summary>Soluzione</summary>

(a) Prima frase: punteggi con $[0{,}5;0{,}5]$: dog 0,5; bites 0,5; man 1; punto 0,5. Esponenziali 1,649; 1,649; 2,718; 1,649 (somma 7,665), pesi 0,215; 0,215; 0,355; 0,215. Output $0{,}215[1,0]+0{,}215[0,1]+0{,}355[1,1]+0{,}215[0{,}5;0{,}5] = [0{,}677;\ 0{,}677]$. Seconda frase: gli stessi punteggi in un altro ordine (man 1, bites 0,5, dog 0,5, punto 0,5), quindi gli stessi addendi: **stesso output** $[0{,}677;\ 0{,}677]$.

(b) Prima frase: input dog $[1{,}1;0]$, bites $[0{,}2;1]$, man $[1{,}3;1]$, punto $[0{,}9;0{,}5]$. Punteggi 0,99; 0,68; 1,67; 1,06; pesi 0,209; 0,153; 0,413; 0,224; output $[1{,}000;\ 0{,}679]$. Seconda frase: man $[1{,}1;1]$, bites $[0{,}2;1]$, dog $[1{,}3;0]$, punto $[0{,}9;0{,}5]$. Punteggi 1,49; 0,68; 1,17; 1,06; pesi 0,354; 0,158; 0,257; 0,231; output $[0{,}963;\ 0{,}627]$.

(c) Senza posizioni l'attenzione è una somma che non dipende dall'ordine: due frasi di significato opposto danno lo stesso vettore. Sommando un vettore diverso per ogni posizione lo stesso token ha input diversi in posizioni diverse, e l'output distingue le due frasi.

</details>

#### Esercizio 3 (scheda L15): posizioni apprese

1. Un modello con posizioni assolute apprese ha lunghezza massima $N = 2048$ e $d = 768$. Forma di $E_{pos}$ e numero di pesi?
2. Quali righe di $E_{pos}$ vengono aggiornate da un testo di training di 300 token? Che cosa suggerisce per le posizioni vicine a 2048?
3. Che cosa succede se al test vogliamo elaborare un testo di 3.000 token?

<details><summary>Soluzione</summary>

(a) $[2048\times768]$: $2048\cdot768 = 1.572.864$ pesi (poco rispetto ai 38,4 milioni di $E$).

(b) Solo le righe 1-300: le altre non entrano nel calcolo e non ricevono gradiente. Le posizioni vicine a 2048 sono aggiornate solo dai testi (o finestre) lunghi quasi 2048, quindi molto meno spesso: rischiano di essere addestrate male (scheda 18).

(c) Le posizioni da 2049 a 3000 **non hanno un embedding**: il modello non può elaborare il testo tutto insieme. Bisogna troncarlo o spezzarlo in finestre (eventualmente sovrapposte). Una funzione fissa (sinusoidale) o una codifica relativa come RoPE è invece definita per ogni posizione, anche se la qualità oltre la lunghezza vista in training non è garantita.

</details>

#### Esercizio 4 (scheda L15): posizioni sinusoidali a mano

Con $d = 4$: $PE(p) = [\sin p,\ \cos p,\ \sin(p/100),\ \cos(p/100)]$ (radianti).

1. Calcola $PE(4)$, $PE(5)$, $PE(17)$.
2. Calcola i prodotti scalari di $PE(4)$ con $PE(5)$ e con $PE(17)$. Quale è maggiore?
3. Mostra che $PE(p)\cdot PE(q) = \cos(p-q) + \cos((p-q)/100)$ e usalo per spiegare (b). Perché i modelli veri usano molte più frequenze ($d = 64$ nella lezione)?

<details><summary>Soluzione</summary>

(a) $PE(4) = [-0{,}757;\ -0{,}654;\ 0{,}040;\ 0{,}999]$; $PE(5) = [-0{,}959;\ 0{,}284;\ 0{,}050;\ 0{,}999]$; $PE(17) = [-0{,}961;\ -0{,}275;\ 0{,}169;\ 0{,}986]$.

(b) $PE(4)\cdot PE(5) = 0{,}726 - 0{,}186 + 0{,}002 + 0{,}998 = 1{,}540$; $PE(4)\cdot PE(17) = 0{,}728 + 0{,}180 + 0{,}007 + 0{,}985 = 1{,}899$. È **maggiore quello con 17**, contro l'intuizione.

(c) Per ogni coppia $\sin a\sin b + \cos a\cos b = \cos(a-b)$: la prima coppia dà $\cos(p-q)$, la seconda $\cos((p-q)/100)$. Con distanza 1: $\cos1 + \cos0{,}01 = 0{,}540 + 1{,}000 = 1{,}540$; con distanza 13: $\cos13 + \cos0{,}13 = 0{,}907 + 0{,}992 = 1{,}899$. Il termine veloce ha periodo $2\pi\approx6{,}28$: 13 radianti sono poco più di due giri ($13/2\pi\approx2{,}07$), quindi $\cos13$ è vicino a 1 e la posizione 17 "sembra" vicina alla 4. Con molte frequenze di periodi diversi le coincidenze di una frequenza sono compensate dalle altre e la somma decresce (quasi) con la distanza: con $d = 64$ si ottiene 30,9 per la distanza 1 e 21,0 per la distanza 13.

</details>

#### Esercizio 5 (scheda L15): RoPE in due dimensioni

Query e key con lo stesso contenuto, $q = k = [1,0]$, ruotate di 30° per posizione (una sola coppia di dimensioni): la query in posizione $m$ di $30m$ gradi, la key in posizione $n$ di $30n$ gradi.

1. Calcola i vettori ruotati e il loro prodotto scalare per $(m,n) = (2,1)$ e $(5,4)$.
2. Calcolalo per $(m,n) = (4,1)$. Perché è più piccolo?
3. Da che cosa dipende il punteggio, oltre al contenuto di $q$ e $k$?

<details><summary>Soluzione</summary>

Ruotare $[1,0]$ di $\alpha$ dà $[\cos\alpha,\ \sin\alpha]$.

(a) $(2,1)$: $q = [\cos60°, \sin60°] = [0{,}5;\ 0{,}866]$, $k = [\cos30°,\sin30°] = [0{,}866;\ 0{,}5]$; prodotto $0{,}433+0{,}433 = 0{,}866$. $(5,4)$: $q = [\cos150°,\sin150°] = [-0{,}866;\ 0{,}5]$, $k = [\cos120°,\sin120°] = [-0{,}5;\ 0{,}866]$; prodotto $0{,}433+0{,}433 = 0{,}866$. Uguali.

(b) $(4,1)$: $q = [\cos120°,\sin120°] = [-0{,}5;\ 0{,}866]$, $k = [0{,}866;\ 0{,}5]$; prodotto $-0{,}433+0{,}433 = 0$. L'angolo fra i due vettori è $30°\cdot(4-1) = 90°$: vettori ortogonali. In generale il prodotto vale $\cos(30°(m-n))$, che scende con la distanza (finché la distanza non supera 6, cioè 180°).

(c) Solo dalla **distanza** $m-n$ (dall'angolo $(m-n)\theta$), non dalle posizioni assolute. Con una sola frequenza il punteggio è periodico (distanza 12 = distanza 0): per questo RoPE usa molte coppie con velocità diverse.

</details>

#### Esercizio 6 (scheda L15): la testa a mano

Vocabolario ed $E$ dell'esercizio 1, con weight tying. All'ultimo token l'ultimo blocco dà $h = [0,2,1]$.

1. Calcola i logit $u = hE^\top$ e le probabilità $y = \mathrm{softmax}(u)$.
2. Quale token sceglie il greedy decoding? Perché il suo logit è il più alto?
3. Dai le forme di $h$, $E^\top$, $u$, $y$ per un modello vero con $d = 768$ e $|V| = 50.000$.

<details><summary>Soluzione</summary>

(a) Logit (prodotto di $h$ con ogni riga): So 0, long 2, and 1, thanks 2, for 3, all 1. Esponenziali 1; 7,389; 2,718; 7,389; 20,086; 2,718; somma 41,300. Probabilità: So 0,024; long 0,179; and 0,066; thanks 0,179; **for 0,486**; all 0,066.

(b) ***for***: il suo embedding $[0,1,1]$ è il più allineato con $h = [0,2,1]$ (prodotto 3). Il logit di un token è il prodotto scalare di $h$ con il suo embedding. (Nota: qui il modello ripeterebbe un token che compare nel contesto; con questi numeri giocattolo è solo un esercizio sulla geometria.)

(c) $h$: $[1\times768]$; $E^\top$: $[768\times50.000]$; $u$: $[1\times50.000]$; $y$: $[1\times50.000]$.

</details>

#### Esercizio 7 (scheda L15): un token o tutti i token

1. In inferenza il modello ha letto un prompt di 1.000 token. Su quali posizioni si applica la testa di language modeling per generare il token successivo?
2. In training, su una finestra di 1.000 token, quante predizioni del token successivo fa la testa? Perché è possibile senza vedere le risposte?
3. Nel transformer originale per la traduzione, quale parte legge tutta la frase sorgente e quale genera? Perché un language model tipo GPT si chiama decoder-only?

<details><summary>Soluzione</summary>

(a) Solo sull'**ultima** posizione, la 1.000, per predire il token 1.001. Le posizioni precedenti attraversano comunque i blocchi, perché forniscono key e value all'attenzione dell'ultima.

(b) **1.000** predizioni, una per posizione: la posizione $i$ predice il token $i+1$ (input i token 1-1000, target i token 2-1001 del testo). È possibile perché la **maschera causale** impedisce alla posizione $i$ di vedere i token successivi, compreso quello che deve predire: tutte le predizioni si calcolano in un solo passaggio in parallelo, senza "barare".

(c) L'**encoder** legge tutta la frase sorgente (attenzione senza maschera); il **decoder** genera la traduzione da sinistra a destra, con attenzione causale e cross-attention sull'output dell'encoder. Un LM tipo GPT corrisponde grosso modo alla sola metà decoder, senza encoder e quindi senza cross-attention: decoder-only.

</details>

#### Esercizio 8 (scheda L15): greedy e random sampling

Dopo *The cat sat on the* un modello dà i logit mat 2,0; floor 1,0; roof 0,5; moon -1,0.

1. Calcola le probabilità con la softmax.
2. Quale token sceglie il greedy decoding? Che cosa genera se lo rieseguiamo con lo stesso contesto?
3. Per il random sampling dividi $[0,1)$ in intervalli, nell'ordine della tabella. Quale token generano $r = 0{,}65$ e $r = 0{,}98$?

<details><summary>Soluzione</summary>

(a) Esponenziali 7,389; 2,718; 1,649; 0,368, somma 12,124. Probabilità: mat 0,609; floor 0,224; roof 0,136; moon 0,030.

(b) *mat* (logit massimo). Rieseguito con lo stesso contesto e lo stesso modello genera **sempre** *mat*: il greedy è deterministico.

(c) Cumulate 0,609; 0,834; 0,970; 1. Intervalli: mat $[0;\ 0{,}609)$, floor $[0{,}609;\ 0{,}834)$, roof $[0{,}834;\ 0{,}970)$, moon $[0{,}970;\ 1)$. $r = 0{,}65$: **floor**; $r = 0{,}98$: **moon** (il token più improbabile esce comunque circa 3 volte su 100).

</details>

#### Esercizio 9 (scheda L15): temperatura

I logit dell'esercizio 8.

1. Calcola le probabilità con $\tau = 0{,}5$ e $\tau = 2$.
2. Come cambiano le probabilità di *mat* e *moon*? Cambia l'ordine dei token?
3. Che cosa diventano le probabilità per $\tau\to0$ e per $\tau$ molto grande?

<details><summary>Soluzione</summary>

(a) $\tau = 0{,}5$: logit divisi 4; 2; 1; -2, esponenziali 54,598; 7,389; 2,718; 0,135, somma 64,841: probabilità **0,842; 0,114; 0,042; 0,002**. $\tau = 2$: logit 1; 0,5; 0,25; -0,5, esponenziali 2,718; 1,649; 1,284; 0,607, somma 6,258: probabilità **0,434; 0,263; 0,205; 0,097**.

(b) *mat*: 0,609 ($\tau = 1$) $\to$ 0,842 con $\tau = 0{,}5$, $\to$ 0,434 con $\tau = 2$. *moon*: 0,030 $\to$ 0,002 con $\tau = 0{,}5$, $\to$ 0,097 con $\tau = 2$. L'ordine non cambia mai: dividere per $\tau\gt0$ conserva l'ordine dei logit e la softmax è crescente.

(c) $\tau\to0$: mat $\to1$, gli altri $\to0$ (greedy). $\tau\to\infty$: tutti i logit divisi tendono a 0 e le probabilità a $1/4 = 0{,}25$ (uniforme).

</details>

#### Esercizio 10 (scheda L15): top-k e top-p

Le probabilità dell'esercizio 8 ($\tau = 1$).

1. Top-k con $k = 2$ e $k = 3$: quali token restano e con quali probabilità rinormalizzate?
2. Top-p con $p = 0{,}8$ e $p = 0{,}95$: quali token restano e con quali probabilità?
3. Quale valore di $k$ dà il greedy decoding, e quale il random sampling?

<details><summary>Soluzione</summary>

(a) $k = 2$: mat, floor; somma 0,834; rinormalizzate **0,731; 0,269**. $k = 3$: mat, floor, roof; somma 0,970; **0,629; 0,231; 0,140**.

(b) Cumulate 0,609; 0,834; 0,970; 1. $p = 0{,}8$: la prima cumulata $\ge0{,}8$ è 0,834: restano mat e floor, **0,731; 0,269** (come top-2). $p = 0{,}95$: serve 0,970: restano mat, floor, roof, **0,629; 0,231; 0,140** (come top-3).

(c) $k = 1$: greedy. $k = |V|$ (qui 4): random sampling, nessun token scartato.

</details>

#### Esercizio 11 (scheda L15): scegliere un metodo di decoding

1. In un contesto sicuro un modello dà 0,90 al primo token e distribuisce il resto su molti token; in un contesto aperto i suoi primi 10 token tengono solo 0,30 della massa. Quanti token tiene top-p con $p = 0{,}9$ nel primo contesto? Perché un $k = 10$ fisso si comporta così diversamente nei due contesti?
2. Il libro dice che è comune combinare top-k e top-p. In che ordine e a quale scopo?
3. Quali metodi della lezione sono deterministici? Quale useresti per controllare che lo stesso prompt dia sempre la stessa risposta, e quali per scrivere storie varie?

<details><summary>Soluzione</summary>

(a) **Un solo token**: la cumulata del primo è già 0,90 $\ge$ 0,9 (top-p diventa greedy). Con $k = 10$ nel contesto sicuro si lasciano entrare 9 token marginali che insieme valgono meno di 0,10; nel contesto aperto si tengono solo 0,30 della massa e si scartano continuazioni plausibili che valgono il 70%. Il numero giusto di candidati dipende dalla forma della distribuzione, che un $k$ fisso ignora.

(b) Prima **top-k** come filtro rigido, per eliminare comunque la spazzatura della coda; poi **top-p** fra i rimasti, per adattarsi alla confidenza del modello.

(c) Deterministici: il **greedy** (e la beam search; equivalenti: top-k con $k = 1$, temperatura $\tau\to0$). Per la riproducibilità il greedy. Per storie varie metodi di campionamento: temperatura intorno a 1 o un po' sopra, combinata con top-p (o top-k). (Anche il campionamento diventa riproducibile se si fissa il seme del generatore casuale, come nel notebook.)

</details>

#### Esercizio 12 (proprio): i parametri di GPT-2 small

GPT-2 small ha $|V| = 50.257$, $d = 768$, $L = 12$ blocchi, posizioni apprese fino a $N = 1024$, feedforward con $d_{ff} = 4d$ e weight tying.

1. Conta i pesi di $E$ e di $E_{pos}$.
2. Conta i pesi dei blocchi trascurando bias e layer norm (attenzione $4d^2$, feedforward $8d^2$, L14).
3. Totale con e senza weight tying. Che frazione è l'embedding?

<details><summary>Soluzione</summary>

(a) $E$: $50.257\cdot768 = 38.597.376$. $E_{pos}$: $1024\cdot768 = 786.432$.

(b) $12\cdot(4+8)\cdot768^2 = 12\cdot12\cdot589.824 = 84.934.656$.

(c) Con tying: $38.597.376 + 786.432 + 84.934.656 = 124.318.464$, circa 124 milioni (aggiungendo bias e layer norm si arriva a 124.439.808, il numero ufficiale). Senza tying si aggiunge una seconda matrice da 38.597.376: 162,9 milioni, il 31% in più. L'embedding da solo è il 31% dei parametri del modello con tying: nei modelli piccoli pesa molto, nei modelli grandi (dove $d^2L$ domina) molto meno.

</details>

#### Esercizio 13 (proprio): greedy contro beam search

Un modello con tre token (A, B, EOS). Dall'inizio: A 0,6; B 0,4. Dopo A: A 0,3; B 0,3; EOS 0,4. Dopo B: EOS 0,9; A 0,1. (Consideriamo solo sequenze di al massimo due token più EOS.)

1. Quale sequenza produce il greedy decoding e con quale probabilità?
2. Esegui la beam search con $k = 2$ fino al secondo passo. Quale sequenza vince?
3. Perché il greedy sbaglia?

<details><summary>Soluzione</summary>

(a) Greedy: A (0,6), poi EOS (0,4, il massimo dopo A): **A EOS**, $0{,}6\cdot0{,}4 = 0{,}24$.

(b) Passo 1: si tengono A (0,6) e B (0,4). Passo 2: candidati A A $0{,}18$, A B $0{,}18$, A EOS $0{,}24$, B EOS $0{,}36$, B A $0{,}04$. I 2 migliori: B EOS (0,36) e A EOS (0,24), entrambi completi. Vince **B EOS** con 0,36.

(c) Il greedy sceglie A perché è il primo token più probabile, ma dopo A la massa è sparsa su tre continuazioni, mentre dopo B quasi tutta la massa (0,9) va su una sola. La probabilità di una sequenza è un prodotto: un primo passo meno probabile può dare la sequenza più probabile (schede 40-41).

</details>

#### Esercizio 14 (proprio): temperatura e top-p insieme

Logit $u = [3, 2, 1, 0]$ per quattro token.

1. Calcola le probabilità con $\tau = 1$ e con $\tau = 2$.
2. Applica top-p con $p = 0{,}9$ in entrambi i casi: quanti token restano?
3. Che cosa insegna sull'ordine in cui si applicano temperatura e top-p?

<details><summary>Soluzione</summary>

(a) $\tau = 1$: esponenziali 20,09; 7,39; 2,72; 1, somma 31,19: probabilità 0,644; 0,237; 0,087; 0,032. $\tau = 2$: logit 1,5; 1; 0,5; 0, esponenziali 4,48; 2,72; 1,65; 1, somma 9,85: probabilità 0,455; 0,276; 0,167; 0,102.

(b) $\tau = 1$: cumulate 0,644; 0,881; 0,968: restano **3 token** (0,665; 0,245; 0,090 rinormalizzati). $\tau = 2$: cumulate 0,455; 0,731; 0,899; 1: 0,899 è appena sotto 0,9, quindi restano **tutti e 4**.

(c) Temperatura e top-p non commutano in generale: se la temperatura si applica prima, appiattendo la distribuzione allarga il nucleo di top-p; se si applica dopo il taglio, cambia solo le proporzioni fra i token rimasti. Le librerie fissano un ordine (di solito prima la temperatura sui logit, poi i filtri top-k e top-p): con $\tau$ alto conviene ricordare che anche top-p lascerà entrare più token.

</details>

### Domande tipo orale

<details><summary>Come diventa un vettore un token in ingresso a un transformer?</summary>

Traccia: (1) il testo è tokenizzato (BPE) in id interi, posizioni nel vocabolario; (2) la matrice di embedding $E$ $[|V|\times d]$ ha una riga appresa per token; (3) l'embedding è la riga $E[\mathrm{id}]$, che equivale al prodotto del one-hot $[1\times|V|]$ per $E$ (primo strato lineare senza bias); (4) per la sequenza: matrice one-hot $[N\times|V|]$ per $E$ = $[N\times d]$; (5) si somma l'embedding di posizione; (6) numero di pesi $|V|d$, per esempio 25,6 milioni con $|V| = 50.000$, $d = 512$; $V$ qui è il vocabolario, non i value.

</details>

<details><summary>Perché un transformer ha bisogno di informazione sulla posizione?</summary>

Traccia: (1) gli embedding dei token non dipendono dalla posizione: *dog* ha lo stesso vettore in posizione 1 e 3; (2) l'attenzione è una somma pesata con pesi da prodotti scalari: permutando gli input si permutano solo gli addendi; (3) quindi nel primo strato l'output del punto in *dog bites man .* e *man bites dog .* è identico (esercizio 2: $[0{,}677;\ 0{,}677]$); (4) feedforward e layer norm lavorano per posizione e non aiutano; (5) soluzione: sommare un vettore che dipende dalla posizione, così lo stesso token ha input diversi in posizioni diverse.

</details>

<details><summary>Descrivi gli embedding di posizione appresi e i loro limiti.</summary>

Traccia: (1) una matrice $E_{pos}$ $[N\times d]$ con una riga per posizione fino alla lunghezza massima, appresa come $E$; (2) $X_i = E[\mathrm{id}(i)] + E_{pos}[i]$, somma della stessa dimensione; (3) limiti: le posizioni finali compaiono di rado nei dati e sono addestrate male; (4) oltre la lunghezza massima non esistono, il testo va troncato o spezzato; (5) alternativa: una funzione fissa della posizione (sinusoidale) o codifiche relative (RoPE).

</details>

<details><summary>Scrivi gli embedding sinusoidali e spiega le loro proprietà.</summary>

Traccia: (1) $PE(p,2i) = \sin(p/10000^{2i/d})$, $PE(p,2i+1) = \cos(p/10000^{2i/d})$; (2) coppie seno/coseno con frequenze $\omega_i$ da 1 (un radiante per posizione) a circa $1/10000$; (3) coppie veloci distinguono posizioni vicine, lente posizioni lontane (orologio); (4) nessun parametro, definite per ogni posizione; (5) $PE(p)\cdot PE(q) = \sum_i\cos(\omega_i(p-q))$: dipende solo dalla distanza, vale $d/2$ per $p = q$; con $d = 64$: 32, 30,9 per distanza 1, 21,0 per distanza 13; (6) con poche frequenze la somma non è monotòna (esercizio 4).

</details>

<details><summary>Che cos'è RoPE e in che cosa differisce dalle posizioni sinusoidali?</summary>

Traccia: (1) codifica di posizione relativa: conta la distanza fra due token, non la posizione assoluta; (2) ogni coppia di dimensioni di query e key viene ruotata di un angolo proporzionale alla posizione, $m\theta_i$ e $n\theta_i$; (3) il prodotto scalare di due vettori ruotati dipende dal contenuto e dall'angolo relativo, cioè solo da $m-n$; (4) esempio: posizioni (2,1) e (5,4) danno lo stesso punteggio; (5) differenze: applicata dentro l'attenzione, in ogni strato, solo a query e key, moltiplicativa invece che additiva all'input; (6) è il metodo più diffuso negli LLM recenti (Su et al.).

</details>

<details><summary>Descrivi la language modeling head con le forme degli oggetti.</summary>

Traccia: (1) prende $h^L_N$, output dell'ultimo blocco all'ultimo token (dopo l'extra layer norm), $[1\times d]$; (2) unembedding: strato lineare $U$ $[d\times|V|]$ che dà i logit $u$ $[1\times|V|]$, un punteggio per token; (3) softmax: probabilità $y$ $[1\times|V|]$; (4) da $y$ si sceglie il token (decoding); (5) esempio: $h = [2,0,1]$, logit 2,0,1,2,1,3, *all* 0,49; (6) è lo stesso schema della regressione multinomiale con $|V|$ classi.

</details>

<details><summary>Che cos'è il weight tying e perché funziona?</summary>

Traccia: (1) la testa usa $U = E^\top$, la trasposta della matrice di embedding: $u = hE^\top$; (2) $E$ manda one-hot in embedding, $E^\top$ riporta un embedding sul vocabolario (unembedding); (3) il logit di un token è il prodotto scalare fra $h$ e il suo embedding: si favoriscono i token il cui embedding è allineato con lo stato finale; (4) in training $E$ riceve gradiente da entrambe le estremità e impara entrambe le mappe; (5) risparmia $|V|d$ parametri, 38,4 milioni con $|V| = 50.000$, $d = 768$; (6) è comune ma non obbligatorio: la testa può avere una sua matrice.

</details>

<details><summary>Dove si applica la testa in inferenza e in training?</summary>

Traccia: (1) in inferenza solo sull'ultimo token $N$ per predire il token $N+1$; le altre posizioni servono come key e value; (2) in training a ogni posizione: la posizione $i$ predice il token $i+1$, $N$ predizioni per finestra; (3) è possibile grazie alla maschera causale: nessuna posizione vede il proprio target; (4) nei blocchi alti la residual stream rappresenta il token successivo e la testa lo legge (logit lens: la stessa lettura sugli strati intermedi).

</details>

<details><summary>Disegna e descrivi un transformer decoder-only completo per un token.</summary>

Traccia: (1) input $w_i$: embedding $E$ più embedding di posizione = $x^1_i$; (2) $L$ blocchi prenorm (layer norm, attenzione, somma; layer norm, feedforward, somma), $h^\ell_i = x^{\ell+1}_i$; (3) extra layer norm finale; (4) unembedding $E^\top$ e softmax: distribuzione $[1\times|V|]$; (5) si sceglie $w_{i+1}$, lo si aggiunge all'input e si ripete; (6) decoder-only perché corrisponde alla metà decoder dell'encoder-decoder originale, senza cross-attention.

</details>

<details><summary>Che differenza c'è fra il transformer originale e un modello decoder-only?</summary>

Traccia: (1) Vaswani et al. 2017: encoder-decoder per la traduzione; (2) encoder: legge tutta la frase sorgente, attenzione senza maschera; (3) decoder: genera la traduzione da sinistra a destra con attenzione causale e cross-attention sull'encoder; (4) un LM causale (GPT) è la sola metà decoder senza cross-attention; (5) gli encoder-only (BERT) sono l'altra metà, per la comprensione e la classificazione.

</details>

<details><summary>Che cos'è il greedy decoding e quali sono i suoi difetti?</summary>

Traccia: (1) $\hat w_t = \operatorname{argmax}_w P(w\mid w_{\lt t})$, sempre il token più probabile (nell'esempio *all*); (2) scelta localmente ottima; (3) deterministico: stesso contesto, stessa stringa; (4) testo generico e ripetitivo, spesso in ciclo; (5) non trova necessariamente la sequenza più probabile: albero yes/ok, greedy 0,20 contro ok ok EOS 0,28; (6) la beam search con $k$ ipotesi rimedia in parte e si usa nella traduzione; (7) i LLM in pratica non usano il greedy per la generazione libera.

</details>

<details><summary>Spiega il random sampling e il suo problema.</summary>

Traccia: (1) si estrae il token secondo la sua probabilità, fino a EOS (Shannon 1948; come il campionamento dagli n-gram della L4); (2) in pratica: cumulate, numero casuale $r$, primo token con cumulata $\gt r$ (esempio $r = 0{,}81$: *your*); (3) i token probabili escono più spesso ma ogni token può uscire; (4) problema: la coda di molti token improbabili ha massa totale non trascurabile (10.000 token da 0,00003 = 0,30: 3 token su 10); (5) i token strani diventano contesto e il testo deraglia; (6) greedy troppo noioso, random troppo casuale.

</details>

<details><summary>Che cos'è la temperatura e che effetto ha sulla distribuzione?</summary>

Traccia: (1) $y = \mathrm{softmax}(u/\tau)$; (2) $\tau\lt1$ amplifica le differenze fra logit: distribuzione più appuntita; $\tau\to0$ greedy; (3) $\tau\gt1$ le riduce: più piatta; $\tau\to\infty$ uniforme; (4) esempio: $\tau = 0{,}5$ porta *all* da 0,44 a 0,59 e *that* da 0,08 a 0,02; $\tau = 0{,}1$: 0,95; $\tau = 10$: da 0,27 a 0,23; (5) l'ordine dei token non cambia mai; (6) $\tau$ bassa più qualità, alta più diversità.

</details>

<details><summary>Confronta top-k e top-p sampling.</summary>

Traccia: (1) top-k: tieni i $k$ token più probabili, rinormalizza, campiona; $k = 1$ greedy, $k = |V|$ random; esempio $k = 2$: all 0,57, the 0,43; (2) problema: $k$ fisso mentre la forma della distribuzione cambia (top 5 = 97% in un contesto sicuro, 35% in uno aperto); (3) top-p (nucleus, Holtzman et al. 2020): il più piccolo insieme con massa $\ge p$; esempio $p = 0{,}9$: all, the, your (0,48; 0,36; 0,16); $p = 0{,}75$: come top-2; (4) adattivo: più candidati quando il modello è incerto, meno quando è sicuro; (5) in pratica si combinano: prima top-k come filtro, poi top-p.

</details>

<details><summary>Che cosa si intende per compromesso fra qualità e diversità nel decoding?</summary>

Traccia: (1) le parole più probabili danno testi giudicati più accurati, coerenti, fattuali, ma noiosi e ripetitivi; (2) le parole di probabilità media danno testi più creativi e vari ma meno fattuali e a rischio di incoerenza; (3) greedy e random sono i due estremi; (4) temperatura, top-k, top-p regolano il compromesso partendo dalla stessa distribuzione $y$; (5) scelta pratica: greedy o $\tau$ bassa per compiti con una risposta giusta, campionamento con $\tau$ intorno a 1 e top-p per testi creativi.

</details>
