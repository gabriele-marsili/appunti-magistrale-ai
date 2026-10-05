# L5 · Smoothing ed entropia

*Smoothing and Entropy* · 01/10/2026 · Claudio Gallicchio · lettura: J&M cap. 3, §3.6-3.8

[Versione interattiva sul sito](https://gabriele-marsili.github.io/appunti-magistrale-ai/anno-2/hlt/sito/#L5) · [Indice della dispensa](README.md)

Seconda lezione sugli n-gram (J&M §3.6-3.8). Come dare probabilità agli n-gram mai visti nel training: **Laplace (add-one)** e **add-k**, con le tabelle BeRP di probabilità, conteggi ricostruiti $C^*$ e sconti; **interpolazione lineare** con $\lambda$ stimati su dati held-out e **stupid backoff**, tutto verificato anche sul mini-corpus *I am Sam*. Poi la teoria dell'informazione che sta sotto la perplexity: **entropia** (corsa di cavalli e codici ottimali), entropy rate, teorema di Shannon-McMillan-Breiman, **cross-entropy** e **perplexity $= 2^H$**. Chiude con ciò che passa agli LLM (cross-entropy come loss, perplexity, campionamento) e con i due limiti degli n-gram che motivano i modelli neurali.

## Indice

- [Apertura](#apertura)
- [Laplace e add-k](#laplace-e-add-k)
- [Interpolazione e backoff](#interpolazione-e-backoff)
- [Entropia, cross-entropy e perplexity](#entropia-cross-entropy-e-perplexity)
- [Verso i modelli neurali](#verso-i-modelli-neurali)
- [Notebook](#notebook)
- [Studio ed esercizi](#studio-ed-esercizi)

## Apertura

<a id="p-1"></a>
**Slide 1 · Smoothing ed entropia** — Lezione 5 (Gallicchio, 1 ottobre 2026): come dare probabilità agli n-gram mai visti nel training (Laplace, add-k, interpolazione, stupid backoff) e da dove viene la perplexity (entropia e cross-entropy).

<a id="p-2"></a>

### Slide 2 · Indice della lezione

Quattro parti, che completano il capitolo 3 del libro:

- **Smoothing: Laplace e add-k** (§3.6.1-3.6.2): aggiungere un conteggio fittizio a ogni n-gram, così nessuno ha probabilità 0.
- **Interpolazione e backoff** (§3.6.3-3.6.4): quando il contesto lungo non ha conteggi, usare anche (o invece) gli ordini più bassi.
- **Perplexity ed entropia** (§3.7): entropia, cross-entropy e la perplexity come $2^{H}$; si scopre perché la perplexity è una probabilità *inversa*.
- **Che cosa passa ai large language model**: next-token prediction, disciplina training/test, cross-entropy come loss, campionamento; e i due limiti degli n-gram che motivano i modelli neurali.

È la seconda metà del discorso iniziato nella [L4](L04-modelli-linguistici-n-gram.md#p-1): là si contava e si valutava, qui si risolve il problema degli **zeri** ([L4, scheda 46](L04-modelli-linguistici-n-gram.md#p-46)) e si dà fondamento teorico alla perplexity.

<a id="p-3"></a>

### Slide 3 · Riferimento: J&M capitolo 3, §3.6-3.8

Lettura principale: Jurafsky e Martin, *Speech and Language Processing*, 3a ed. (draft del 19 agosto 2026), **capitolo 3, sezioni 3.6-3.8 e note storiche**:

- **3.6** Smoothing, interpolation, and backoff (Laplace, add-k, interpolazione, stupid backoff);
- **3.7** Advanced: perplexity's relation to entropy (la sezione è marcata *Advanced* nel libro, ma il docente la fa in aula);
- **3.8** Summary;
- **Historical notes**: Markov (1913), Shannon (1948), Jelinek all'IBM, l'origine dell'add-one nella legge di successione di Laplace (1812), Good-Turing, Kneser-Ney, i toolkit SRILM e KenLM, e il passaggio ai modelli neurali.

Il QR code porta al sito del libro, web.stanford.edu/~jurafsky/slp3/. Le tabelle BeRP delle slide 11-19 sono le Fig. 3.1, 3.6, 3.7 e 3.8 del libro; gli esercizi 3.2, 3.4 e 3.7 del libro usano proprio questi metodi.

> **Approfondimento: Che cosa c'è oltre: Kneser-Ney**
>
> (Facoltativo, dalle note storiche del libro.) Laplace, add-k e stupid backoff sono i metodi più semplici. Lo standard storico per gli n-gram è stato il **Modified Interpolated Kneser-Ney** (Chen e Goodman 1999): sconta ogni conteggio di una quantità fissa (come nel grafico della [scheda 8](L05-smoothing-ed-entropia.md#p-8)) e, per l'ordine più basso, usa non la frequenza di una parola ma *in quanti contesti diversi* compare. Non è nel programma delle slide.

<a id="p-4"></a>

### Slide 4 · Dove eravamo rimasti

Tre richiami dalla [L4](L04-modelli-linguistici-n-gram.md#p-1):

- **Massima verosimiglianza**: $P(w_n\mid w_{n-1}) = \dfrac{C(w_{n-1}w_n)}{C(w_{n-1})}$, frequenze relative contate nel corpus di training ([L4, scheda 13](L04-modelli-linguistici-n-gram.md#p-13)).
- **Perplexity**: $\text{PP}(W) = P(w_1\dots w_N)^{-1/N} = \sqrt[N]{1/P(w_1\dots w_N)}$, la probabilità inversa del test set normalizzata per la lunghezza; più bassa è meglio ([L4, scheda 30](L04-modelli-linguistici-n-gram.md#p-30)).
- **Zeri**: $C(\text{ruby slippers}) = 0$. Un n-gram mai visto nel training ha **probabilità 0**, e così l'intero test set che lo contiene: la perplexity non si può calcolare ([L4, scheda 46](L04-modelli-linguistici-n-gram.md#p-46)).

Obiettivo di oggi: **dare probabilità a ciò che non è mai comparso nel training**, senza rompere il vincolo che le probabilità di ogni contesto sommino a 1.

<a id="p-5"></a>

### Slide 5 · Una frase di test con uno zero

Il corpus *I am Sam* della [L4, scheda 14](L04-modelli-linguistici-n-gram.md#p-14):

```
<s> I am Sam </s>
<s> Sam I am </s>
<s> I do not like green eggs and ham </s>
```

- **$N = 17$ token**: le 14 parole più i tre </s>; <s> non si conta, perché non viene mai predetto.
- **$V = 11$ tipi possono seguire una parola**: le dieci parole distinte (I, am, Sam, do, not, like, green, eggs, and, ham) più </s>. Anche qui <s> è escluso: non compare mai come parola successiva. Questo $V$ è quello che servirà per l'add-one.
- Conteggi utili: $C(\text{I}) = 3$, $C(\text{I am}) = 2$, $C(\text{I do}) = 1$, **$C(\text{I like}) = 0$**; $C(\text{am}) = 2$, $C(\text{am Sam}) = 1$, $C(\text{am &lt;/s&gt;}) = 1$, **$C(\text{am I}) = 0$** (in rosso nella slide).

**Frase di test**: <s> I like green eggs and ham </s>. Per la MLE $P(\text{like}\mid\text{I}) = 0/3 = 0$, quindi tutta la frase ha probabilità 0 e la perplexity è indefinita (divisione per zero, o $\log 0 = -\infty$).

Il punto della slide: **tutti gli altri bigram della frase compaiono nel corpus** (<s> I, like green, green eggs, eggs and, and ham, ham </s>). Una frase perfettamente sensata è dichiarata impossibile per un solo bigram mancante. Questo esempio torna nelle schede [20](L05-smoothing-ed-entropia.md#p-20) (add-one), [26](L05-smoothing-ed-entropia.md#p-26) (interpolazione) e [28](L05-smoothing-ed-entropia.md#p-28) (stupid backoff).

> **Da saper fare: Contare N e V in un mini-corpus**
>
> - $N$ (per perplexity e unigram): tutte le parole più un </s> per frase, niente <s>: $3+3+8+3 = 17$.
> - $V$ (per l'add-one sui bigram): i tipi che possono comparire come parola successiva, cioè parole distinte più </s>: $10+1 = 11$.
> - Controllo: le righe dei conteggi bigram sommano al conteggio del contesto, es. $C(\text{I am}) + C(\text{I do}) = 3 = C(\text{I})$.
>
> Attenzione alle convenzioni: l'esercizio 3.4 del libro dice di contare anche <s> «come ogni altro token», e allora $V$ cambia. Leggi sempre cosa dichiara il testo.

## Laplace e add-k

<a id="p-6"></a>
**Slide 6 · Smoothing: Laplace e add-k** — Prima parte: lo smoothing più semplice, aggiungere un conteggio fisso (1 o k) a ogni n-gram.

<a id="p-7"></a>

### Slide 7 · Smoothing

**Smoothing** (o **discounting**): togliere un po' di massa di probabilità agli eventi frequenti e darla agli eventi mai visti. Il nome «discounting» dice l'operazione sui visti (si scontano), «smoothing» l'effetto sulla distribuzione (meno picchi, niente zeri).

- **Zeri**: sequenze che non compaiono mai nel training ma compaiono nel test. Il corpus ha *ruby* e *slippers*, ma non *ruby slippers*. Con BPE i **token** non sono mai sconosciuti (ogni parola si spezza in token noti); le **sequenze** di token invece sì: lo smoothing serve anche con la tokenizzazione subword.
- **Due problemi**: (1) si **sottostima** la probabilità di sequenze che capitano davvero, e questo danneggia qualunque applicazione; (2) un solo zero rende 0 la probabilità del test set, quindi **niente perplexity**.
- **Esempio**: dopo *denied the* il corpus ha *allegations* 3 volte, *reports* 2, *claims* 1, *request* 1, in tutto 7. Lo smoothing tiene da parte una quota di questi 7 conteggi per parole mai viste lì, come *attack* o *outcome* (grafico nella scheda successiva).
- **Algoritmi della lezione**: Laplace (add-one), add-k, interpolazione tra ordini di n-gram, stupid backoff.

Vincolo da non perdere: dopo lo smoothing le probabilità di ogni contesto devono ancora sommare a 1 (tranne stupid backoff, che rinuncia apposta, [scheda 27](L05-smoothing-ed-entropia.md#p-27)). La massa data agli zeri deve essere tolta a qualcun altro.

<a id="p-8"></a>

### Slide 8 · Rubare massa di probabilità

Due grafici a barre orizzontali sui conteggi dopo *denied the*:

- **Sinistra, massima verosimiglianza (7 conteggi)**, barre blu: allegations 3, reports 2, claims 1, request 1; attack, man, outcome 0 (nessuna barra).
- **Destra, smoothed (gli stessi 7 conteggi)**: allegations 2,5, reports 1,5, claims 0,5, request 0,5 (blu), più una barra rossa **other words 2**.

**Il totale resta 7**: ogni parola vista perde mezzo conteggio ($4\times0{,}5 = 2$) e questi 2 conteggi vanno a **tutte le parole mai viste** dopo *denied the*, insieme. In probabilità: $P(\text{allegations}\mid\text{denied the})$ passa da $3/7 = 0{,}43$ a $2{,}5/7 = 0{,}36$, e le parole mai viste ricevono in tutto $2/7 = 0{,}29$, da dividere tra loro.

Perché «per generalizzare meglio»: su 7 osservazioni, il fatto di non aver visto *attack* è poca evidenza che sia impossibile. Togliere un po' ai visti è una scommessa sul fatto che il test conterrà parole nuove in quel contesto.

> **Approfondimento: Sconto fisso: absolute discounting**
>
> (Facoltativo.) Il grafico toglie la **stessa quantità** (0,5) a ogni conteggio visto: è l'idea dell'**absolute discounting**, alla base di Kneser-Ney. Togliere un valore fisso pesa poco sui conteggi grandi (3 → 2,5, −17%) e molto su quelli piccoli (1 → 0,5, −50%), che sono proprio i meno affidabili. L'add-one della [scheda 12](L05-smoothing-ed-entropia.md#p-12) fa il contrario: aggiunge a tutti e, quando $V$ è grande, toglie moltissimo anche ai conteggi grandi.

<a id="p-9"></a>

### Slide 9 · Parole sconosciute: vocabolario aperto e chiuso

- **Vocabolario chiuso**: si conoscono in anticipo tutte le parole; $V$ è fisso (es. un sistema a comandi con un lessico dato).
- **Vocabolario aperto**: di solito non è così, e nel test compaiono parole **out of vocabulary (OOV)**, mai viste nel training (legge di Heaps, [L2, scheda 12](L02-parole-e-token.md#p-12)).
- **<UNK> nel training**: si fissa $V$ in anticipo, per esempio le parole viste almeno due volte; ogni altra parola del training diventa il token **<UNK>** (*unknown word*), e le sue probabilità si stimano come quelle di qualunque altra parola.
- **<UNK> al test**: ogni parola fuori da $V$ diventa <UNK> e usa le sue probabilità: *I like green tomatoes* diventa *I like green <UNK>*.
- **Con i token subword**: il vocabolario è l'insieme dei token BPE; ogni parola è una sequenza di token noti, al limite singole lettere (o byte), quindi **nessun token del test è sconosciuto** ([L2, scheda 13](L02-parole-e-token.md#p-13)).

Distinzione da tenere: <UNK> e subword risolvono le **parole** sconosciute; lo smoothing risolve le **combinazioni** sconosciute di parole note. Sono due problemi diversi, e un modello reale li ha entrambi.

> **Approfondimento: <UNK> e confronto di perplexity**
>
> (Facoltativo.) Con <UNK> si può «barare»: scegliendo un vocabolario piccolo, molte parole diventano <UNK>, che è un token frequente e quindi facile da predire, e la perplexity scende senza che il modello sia migliore. Per questo le perplexity di modelli a <UNK> si confrontano solo a parità di vocabolario; con i subword vale lo stesso a parità di tokenizer ([scheda 41](L05-smoothing-ed-entropia.md#p-41)).

<a id="p-10"></a>

### Slide 10 · Laplace smoothing

Il caso più semplice, sugli unigram:

- **Senza smoothing (MLE)**: $P(w_i) = \dfrac{c_i}{N}$, il conteggio $c_i$ della parola diviso il numero totale $N$ di token.
- **Add-one (Laplace)**: $P_{\text{Laplace}}(w_i) = \dfrac{c_i + 1}{N + V}$. Si aggiunge 1 a ogni conteggio; le parole del vocabolario sono $V$ e ognuna è incrementata, quindi ci sono **$V$ osservazioni in più** e il denominatore cresce di $V$.
- **Senza $+V$** le probabilità sommerebbero a $\sum_i (c_i+1)/N = (N+V)/N &gt; 1$: non sarebbe più una distribuzione (è la domanda che il libro pone tra parentesi).

Esempio su *I am Sam* ($N=17$, $V=11$): $P(\text{I})$ passa da $3/17 = 0{,}18$ a $4/28 = 0{,}14$, mentre una parola mai vista nel corpus di unigram avrebbe $1/28 = 0{,}036$ invece di 0.

**Dove si usa**: non è abbastanza buono per i modelli n-gram moderni, ma introduce i concetti degli altri algoritmi di smoothing, è una **baseline** utile ed è pratico per la **classificazione di testi** (Naive Bayes, Appendice B del libro).

> **Approfondimento: La legge di successione di Laplace**
>
> (Facoltativo, dalle note storiche.) Il nome viene dalla **legge di successione** di Laplace (1812): se un evento si è verificato $s$ volte su $n$ prove, la probabilità che si verifichi la prossima volta è $(s+1)/(n+2)$. È l'add-one con due esiti possibili ($V=2$). In termini bayesiani è la media a posteriori con prior uniforme (Dirichlet con tutti i parametri a 1); l'add-k corrisponde a una Dirichlet con parametri $k$. Jeffreys (1948) lo applicò al problema delle frequenze zero.

<a id="p-11"></a>

### Slide 11 · Conteggi bigram (Berkeley Restaurant Project)

La tabella dei conteggi bigram del BeRP già vista nella [L4, scheda 17](L04-modelli-linguistici-n-gram.md#p-17) (Fig. 3.1 del libro): **otto parole su $V = 1446$**, corpus di **9332 frasi**. Gli zeri sono in grigio chiaro.

- **Righe**: la prima parola del bigram (il contesto). **Colonne**: la parola che segue.
- La cella in riga *i* e colonna *want* (827) è il numero di volte in cui *want* ha seguito *i*.

I conteggi unigram che servono come denominatori (libro, p. 72):

| i | want | to | eat | chinese | food | lunch | spend |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2533 | 927 | 2417 | 746 | 158 | 1093 | 341 | 278 |

Numeri da ricordare per gli esempi seguenti: $C(\text{want to}) = 608$, $C(\text{want}) = 927$, $C(\text{chinese food}) = 82$, $C(\text{chinese}) = 158$. Le righe mostrate non sommano al conteggio unigram, perché mancano le altre 1438 colonne del vocabolario.

<a id="p-12"></a>

### Slide 12 · Conteggi bigram con add-one

Si aggiunge 1 a **ogni** conteggio (Fig. 3.6 del libro). Le **32 celle su 64** che erano zero ora valgono 1 (in grigio); tutte le altre crescono di uno: $C(\text{i want}) = 827 + 1 = 828$, $C(\text{want to}) = 609$, $C(\text{chinese food}) = 83$.

Verificato: nella tabella della slide 11 gli zeri sono esattamente 32 (metà delle celle, come già notato nella [L4, scheda 18](L04-modelli-linguistici-n-gram.md#p-18)).

Il problema si vede già pensando alla tabella intera: le celle sono $1446^2 \approx 2{,}09$ milioni, quasi tutte zero, e ognuna riceve un conteggio. Nella riga di *want* si aggiungono 1446 conteggi fittizi a 927 osservazioni vere: dopo lo smoothing il **61%** della massa della riga ($1446/2373$) è inventato. È la radice del difetto che si vedrà nelle schede 16-19.

<a id="p-13"></a>

### Slide 13 · La riga di lunch

Stessa tabella, con un riquadro sulla **riga di *lunch***: dei suoi otto conteggi, **sei erano zero**. Fra queste otto parole, dopo *lunch* erano comparse solo *i* (2 volte) e *food* (1 volta); ora valgono 3 e 2, e i sei bigram mai visti valgono 1, come se fossero stati visti una volta.

È una riga tipica di una parola poco frequente ($C(\text{lunch}) = 341$): le osservazioni vere sono poche e quasi tutto il vocabolario è zero. L'add-one tratta allo stesso modo *lunch want* (implausibile) e *lunch food* (plausibile ma mai visto): il conteggio aggiunto è **uguale per tutti**, non dipende da quanto la parola sia plausibile. L'interpolazione ([scheda 26](L05-smoothing-ed-entropia.md#p-26)) correggerà proprio questo, dando agli zeri una quota proporzionale alla frequenza della parola.

<a id="p-14"></a>

### Slide 14 · Probabilità bigram con add-one

$$P_{\text{MLE}}(w_n\mid w_{n-1}) = \frac{C(w_{n-1}w_n)}{C(w_{n-1})}\qquad P_{\text{Laplace}}(w_n\mid w_{n-1}) = \frac{C(w_{n-1}w_n)+1}{\sum_w \big(C(w_{n-1}w)+1\big)} = \frac{C(w_{n-1}w_n)+1}{C(w_{n-1})+V}$$

- **MLE**: ogni riga di conteggi si normalizza con il conteggio unigram della sua prima parola.
- **Perché $+V$**: il denominatore della MLE è in realtà la somma di tutti i bigram che iniziano con $w_{n-1}$, cioè $\sum_w C(w_{n-1}w) = C(w_{n-1})$ ([L4, scheda 13](L04-modelli-linguistici-n-gram.md#p-13)). Questi bigram sono $V$, uno per ogni parola successiva possibile, e a ognuno si aggiunge 1: in tutto si aggiunge $V$.
- **Berkeley**: a ogni conteggio unigram si somma $V = 1446$. $P(\text{to}\mid\text{want}) = (608+1)/(927+1446) = 609/2373 = 0{,}26$, mentre la stima senza smoothing era $608/927 = 0{,}66$.

> **Da saper fare: Calcolare una probabilità add-one**
>
> Ricetta: (conteggio del bigram + 1) / (conteggio del contesto + $V$). Esempio: $P(\text{food}\mid\text{chinese}) = (82+1)/(158+1446) = 83/1604 = 0{,}052$ (MLE: $82/158 = 0{,}52$, dieci volte di più). Un bigram mai visto dopo *chinese*: $1/1604 = 0{,}00062$. Errore tipico: dimenticare il $+V$ al denominatore, o usare come $V$ il numero di righe della tabella (8) invece del vocabolario intero (1446).

<a id="p-15"></a>

### Slide 15 · La tabella delle probabilità add-one

La Fig. 3.7 del libro: i conteggi smoothed divisi per $C(w_{n-1}) + V$. Le probabilità che prima erano zero sono in grigio. **Nessuno zero**: ogni bigram del vocabolario ha una probabilità.

Come si legge:

- In ogni riga i valori grigi sono **tutti uguali**, $1/(C(w_{n-1})+V)$: riga *i* $1/3979 = 0{,}00025$, riga *lunch* $1/1787 = 0{,}00056$. Il contesto raro (*lunch*) dà agli zeri una probabilità più alta del contesto frequente (*i*), perché ha meno evidenza contro di loro.
- I valori più alti restano quelli dei bigram frequenti: $P(\text{want}\mid\text{i}) = 0{,}21$, $P(\text{to}\mid\text{want}) = 0{,}26$, $P(\text{eat}\mid\text{to}) = 0{,}18$, ma molto più bassi della MLE (0,33, 0,66, 0,28).
- Le righe non sommano a 1 sulle otto colonne mostrate: il resto della massa sta nelle altre 1438 colonne, e con l'add-one è **molta**.

Tutti i 64 valori ricalcolati in Python dai conteggi e dagli unigram: coincidono con la slide.

<a id="p-16"></a>

### Slide 16 · P(to | want): più di metà persa

Stessa tabella, evidenziata la cella **$P(\text{to}\mid\text{want}) = 0{,}26$**, cioè $609/(927+1446)$; senza smoothing era 0,66.

Il bigram **più frequente dopo *want*** perde più di metà della sua probabilità (−61%). Eppure *want to* è stato visto 608 volte su 927: è l'evidenza più solida della tabella. L'add-one non distingue tra conteggi affidabili e conteggi scarsi; sposta massa in proporzione a $V$, e con $V = 1446$ contro $C(\text{want}) = 927$ la sposta in gran parte.

Il rapporto tra le due stime, $0{,}26/0{,}66 \approx 0{,}39$, anticipa lo **sconto** $d$ della [scheda 18](L05-smoothing-ed-entropia.md#p-18): per i conteggi grandi è quasi $C(w_{n-1})/(C(w_{n-1})+V)$.

<a id="p-17"></a>

### Slide 17 · Conteggi ricostruiti C*

$$P_{\text{Laplace}}(w_n\mid w_{n-1}) = \frac{C(w_{n-1}w_n)+1}{C(w_{n-1})+V} = \frac{C^*(w_{n-1}w_n)}{C(w_{n-1})}\quad\Rightarrow\quad C^*(w_{n-1}w_n) = \frac{[C(w_{n-1}w_n)+1]\times C(w_{n-1})}{C(w_{n-1})+V}$$

Il **conteggio ricostruito** (*adjusted count*) $C^*$ è il conteggio che, diviso il denominatore **non** smoothed $C(w_{n-1})$, dà la probabilità smoothed. Serve a vedere quanto lo smoothing ha cambiato i conteggi, confrontandoli direttamente con quelli originali (Fig. 3.8 del libro; zeri originali in grigio).

In pratica ogni riga è moltiplicata per un fattore fisso $C(w_{n-1})/(C(w_{n-1})+V)$, e **i valori grigi di ogni riga sono proprio questo fattore** (perché $C^*=1\times$ fattore):

| riga | i | want | to | eat | chinese | food | lunch | spend |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fattore | 0,64 | 0,39 | 0,63 | 0,34 | 0,098 | 0,43 | 0,19 | 0,16 |

Esempi: $C^*(\text{i want}) = 828\times0{,}637 = 527$; $C^*(\text{to eat}) = 687\times0{,}626 = 430$. Le righe delle parole rare (*chinese*, *lunch*, *spend*) sono schiacciate di più. Valori verificati in Python (la slide arrotonda a due cifre significative).

<a id="p-18"></a>

### Slide 18 · C*(want to) = 238: lo sconto d

Evidenziata la cella **$C^*(\text{want to}) = 238$**: era 608.

Lo **sconto** (*discount*) $d$ è il rapporto tra il conteggio nuovo e quello vecchio:

$$d = \frac{C^*}{C} = \frac{238}{608} = 0{,}39$$

Calcolo esatto: $C^* = 609\times927/2373 = 237{,}9$, $d = 0{,}391$. Attenzione al verso: $d$ vicino a 1 vuol dire che il conteggio è quasi intatto, $d$ piccolo che è stato tagliato molto; $d = 0{,}39$ significa che *want to* ha perso il 61% del suo conteggio (lo stesso 61% di probabilità della [scheda 16](L05-smoothing-ed-entropia.md#p-16)).

> **Da saper fare: Da conteggio a C* e d**
>
> $C^* = (C+1)\cdot\dfrac{C(w_{n-1})}{C(w_{n-1})+V}$, poi $d = C^*/C$. Per *want to*: $(608+1)\times 927/2373 = 237{,}9$; $d = 237{,}9/608 = 0{,}39$. Per un conteggio grande $d \approx C(w_{n-1})/(C(w_{n-1})+V)$; per un conteggio piccolo il $+1$ pesa e $d$ è un po' più alto (per $C(\text{want chinese}) = 6$: $C^* = 2{,}7$, $d = 0{,}46$).

<a id="p-19"></a>

### Slide 19 · C*(chinese food) = 8,2: troppa massa agli zeri

Evidenziata la cella **$C^*(\text{chinese food}) = 8{,}2$**: era 82, sconto $d = 0{,}10$. Calcolo: $83\times158/1604 = 8{,}18$; $d = 8{,}18/82 = 0{,}0997$.

Il conteggio di *chinese food* è stato **diviso per 10**, contro una divisione per circa 2,6 di *want to*. Il motivo: *chinese* è rara ($C = 158$) e il vocabolario è grande ($V = 1446$): nel denominatore $158 + 1446$, il 90% è massa inventata. Dopo *chinese* il corpus ha visto *food* 82 volte su 158 (52%), ma l'add-one lascia a *food* il 5% e distribuisce il resto su 1445 parole quasi tutte mai viste.

Conclusione della slide: il cambiamento è così forte perché **si sposta troppa massa di probabilità verso tutti gli zeri**. È il difetto di fondo dell'add-one per i modelli linguistici: quando $V$ è grande rispetto ai conteggi del contesto, i conteggi veri contano poco.

Come leggere «A factor of 10 more than want to»: $d = 0{,}10$ vuol dire che il conteggio di *chinese food* è ridotto di **un fattore 10** (da 82 a 8,2, come dice il libro), una riduzione più forte di quella di *want to* (fattore $1/0{,}39 \approx 2{,}6$, da 608 a 238). Non vuol dire che uno sconto sia 10 volte l'altro: il rapporto tra i due sconti è $0{,}391/0{,}0997 \approx 3{,}9$.

<a id="p-20"></a>

### Slide 20 · Add-one su I am Sam

$V = 11$ token possibili come successivi: le dieci parole e </s>. Ogni riga riceve $+11$ al denominatore e somma ancora a 1.

| dopo *am* | MLE | add-one |
| --- | --- | --- |
| am Sam | 1/2 | 2/13 = 0,15 |
| am </s> | 1/2 | 2/13 = 0,15 |
| am I | 0 | 1/13 = 0,08 |
| 8 altri | 0 | 1/13 ciascuno |
| totale | 1 | 13/13 = 1 |

| dopo *I* | MLE | add-one |
| --- | --- | --- |
| I am | 2/3 | 3/14 = 0,21 |
| I like | 0 | 1/14 = 0,07 |

- *am* è rara: $C(\text{am}) = 2$ contro $V = 11$. La maggior parte della sua massa, $9/13 = 69\%$, va ai **nove token mai visti** dopo di lei (I e gli altri 8).
- La frase di test <s> I like green eggs and ham </s> ora ha probabilità $2{,}0\times10^{-6}$ e **perplexity 6,5** sui suoi 7 token (riquadro).

Messaggio della slide: **niente zeri, ma i bigram visti perdono la maggior parte della probabilità** (am Sam da 0,5 a 0,15, I am da 0,67 a 0,21). Su un corpus minuscolo lo stesso difetto delle schede 16-19 è ancora più evidente.

> **Da saper fare: L'esercizio della slide: probabilità e perplexity con add-one**
>
> Denominatori: $C(\text{&lt;s&gt;}) + 11 = 14$, $C(\text{I}) + 11 = 14$, e per like, green, eggs, and, ham (conteggio 1 ciascuna) $1 + 11 = 12$.
>
> - $P(\text{I}\mid\text{&lt;s&gt;}) = (2+1)/14 = 3/14$
> - $P(\text{like}\mid\text{I}) = (0+1)/14 = 1/14$
> - $P(\text{green}\mid\text{like}) = P(\text{eggs}\mid\text{green}) = P(\text{and}\mid\text{eggs}) = P(\text{ham}\mid\text{and}) = P(\text{&lt;/s&gt;}\mid\text{ham}) = (1+1)/12 = 1/6$
>
> $P = \frac{3}{14}\cdot\frac{1}{14}\cdot\left(\frac16\right)^5 = \frac{3}{196\cdot7776} = 1{,}97\times10^{-6}$.
>
> $N = 7$ (sei parole più </s>): $\text{PP} = P^{-1/7} = 6{,}53$; in bit, $-\frac17\log_2 P = 2{,}71$ bit per token e $2^{2{,}71} = 6{,}53$ ([scheda 39](L05-smoothing-ed-entropia.md#p-39)). Verificato in Python. Nota: anche i bigram visti una sola volta (like green, …) scendono da probabilità 1 a 1/6.

<a id="p-21"></a>

### Slide 21 · Add-k smoothing

$$P^*_{\text{Add-}k}(w_n\mid w_{n-1}) = \frac{C(w_{n-1}w_n)+k}{C(w_{n-1})+kV}$$

$k = 1$ è Laplace; $k = 0$ è la MLE. Invece di 1 si aggiunge un **conteggio frazionario** $k$, come 0,5 o 0,01: **meno massa** passa dai visti ai non visti.

| $k$ | am Sam | am I |
| --- | --- | --- |
| 1 | 0,15 | 0,08 |
| 0,5 | 0,20 | 0,07 |
| 0,1 | 0,35 | 0,03 |
| 0,01 | 0,48 | 0,005 |
| 0 | 0,50 | 0 |

(*I am Sam*, $V = 11$; formule $(1+k)/(2+11k)$ e $k/(2+11k)$, verificate in Python.) Al diminuire di $k$ si passa con continuità dall'add-one alla MLE.

- **Scegliere $k$**: è un iperparametro, si ottimizza per esempio su un **devset** ([L4, scheda 27](L04-modelli-linguistici-n-gram.md#p-27)).
- **Limiti**: utile per alcuni compiti, classificazione di testi compresa; per il language modeling funziona ancora male, perché i suoi conteggi smoothed sono lontani dai conteggi osservati in testo nuovo (Gale e Church 1994; il libro parla di varianze scarse e sconti spesso inappropriati).

> **Da saper fare: Add-k a mano**
>
> Con $k = 0{,}5$: $P(\text{Sam}\mid\text{am}) = (1+0{,}5)/(2+0{,}5\cdot11) = 1{,}5/7{,}5 = 0{,}20$; $P(\text{I}\mid\text{am}) = 0{,}5/7{,}5 = 0{,}067$. Controllo: $2\times1{,}5/7{,}5 + 9\times0{,}5/7{,}5 = (3+4{,}5)/7{,}5 = 1$. Il denominatore cresce di $kV$, non di $V$.

## Interpolazione e backoff

<a id="p-22"></a>
**Slide 22 · Interpolazione e backoff** — Seconda parte: quando il contesto lungo non ha conteggi, usare meno contesto.

<a id="p-23"></a>

### Slide 23 · Usare meno contesto

Un'altra fonte di conoscenza contro gli zeri: la **gerarchia degli n-gram**. Se un trigram non ha conteggi, si usa il bigram $P(w_n\mid w_{n-1})$; se non ne ha il bigram, l'unigram $P(w_n)$.

Due modi di usarla, nei due riquadri della slide:

- **Interpolazione** (riquadro verde): si **mescolano** le probabilità trigram, bigram e unigram, ciascuna pesata con un $\lambda$. Usa **sempre tutti gli ordini**, anche quando il trigram ha conteggi.
- **Backoff** (riquadro rosso): si usa il trigram se ha conteggi; altrimenti si **ripiega** (*back off*) sul bigram, e poi sull'unigram. Usa **l'ordine più alto che ha qualche conteggio**, uno solo alla volta.

L'idea comune: a volte **meno contesto aiuta a generalizzare**, per i contesti su cui il modello ha imparato poco. È il compromesso della [L4, scheda 43](L04-modelli-linguistici-n-gram.md#p-43): gli ordini alti sono precisi ma sparsi, quelli bassi grossolani ma sempre stimabili; invece di sceglierne uno, li si combina.

<a id="p-24"></a>

### Slide 24 · Interpolazione lineare

$$\hat P(w_n\mid w_{n-2}w_{n-1}) = \lambda_1 P(w_n) + \lambda_2 P(w_n\mid w_{n-1}) + \lambda_3 P(w_n\mid w_{n-2}w_{n-1})$$

- **Una miscela** (*mixture*): la probabilità trigram si stima mescolando le stime unigram, bigram e trigram (tutte MLE), ciascuna pesata con un $\lambda$.
- **I pesi sommano a 1** ($\lambda_i \ge 0$, $\sum_i\lambda_i = 1$): la miscela è una **media pesata** delle tre stime, e quindi è ancora una distribuzione di probabilità. Prova: $\sum_w \hat P(w\mid\cdot) = \lambda_1\sum_w P(w) + \lambda_2\sum_w P(w\mid\cdot) + \lambda_3\sum_w P(w\mid\cdot\,\cdot) = \lambda_1+\lambda_2+\lambda_3 = 1$.
- **Trigram mai visti**: un conteggio trigram nullo non dà più probabilità zero, perché i termini bigram e unigram «riempiono». Basta che la parola esista nel vocabolario e $\lambda_1 &gt; 0$ perché $\hat P &gt; 0$.

Rispetto all'add-one, la massa data a un evento mai visto non è uguale per tutti: dipende da quanto la parola è frequente (unigram) e da quanto è plausibile dopo la parola precedente (bigram).

> **Da saper fare: Interpolazione: le domande tipiche**
>
> - Perché i $\lambda$ devono sommare a 1? Perché altrimenti $\sum_w \hat P \ne 1$.
> - Che cosa succede con $\lambda_3 = 1$? Si torna al trigram MLE, con tutti i suoi zeri. Con $\lambda_1 = 1$ si ignora il contesto.
> - Quando $\hat P(w\mid\cdot) = 0$? Solo se tutti i termini con peso positivo sono zero, cioè (con $\lambda_1&gt;0$) solo se $w$ non è nel vocabolario.

<a id="p-25"></a>

### Slide 25 · Pesi condizionati dal contesto e dati held-out

$$\hat P(w_n\mid w_{n-2}w_{n-1}) = \lambda_1(w_{n-2:n-1})P(w_n) + \lambda_2(w_{n-2:n-1})P(w_n\mid w_{n-1}) + \lambda_3(w_{n-2:n-1})P(w_n\mid w_{n-2}w_{n-1})$$

- **Condizionati sul contesto**: ogni $\lambda$ è una funzione delle due parole precedenti. Se i conteggi di un bigram sono accurati (bigram frequente), i trigram costruiti su di esso sono più affidabili e ricevono più peso ($\lambda_3$ più alto); per un contesto raro conviene fidarsi di più degli ordini bassi. Per ogni contesto i tre pesi devono ancora sommare a 1.
- **Corpus held-out**: un corpus di training aggiuntivo, *tenuto da parte* rispetto ai dati di training. Si **fissano le probabilità n-gram** (stimate sul training) e si scelgono i $\lambda$ che danno al set held-out la **probabilità più alta** (massima verosimiglianza sul held-out).
- **EM**: l'algoritmo *expectation-maximization* è un modo per trovare i $\lambda$ ottimali; è iterativo e converge a valori **localmente** ottimali (Jelinek e Mercer 1980; per questo l'interpolazione lineare si chiama anche *Jelinek-Mercer smoothing*).
- **Iperparametri**: in generale i corpora held-out servono a fissare gli **iperparametri**, parametri che non si imparano dai conteggi di training ($\lambda$, $k$ dell'add-k). Lo stesso ruolo del devset della [L4, scheda 27](L04-modelli-linguistici-n-gram.md#p-27).

Perché non scegliere i $\lambda$ sul training: lì il trigram MLE è sempre il migliore (ha visto tutti i suoi trigram), e si otterrebbe $\lambda_3 = 1$, cioè di nuovo gli zeri.

> **Approfondimento: Un passo di EM per i λ**
>
> (Facoltativo, procedura standard.) Dati i token $w_1\dots w_M$ del held-out e le componenti $P_j$ fissate: **E**: per ogni token calcola la responsabilità di ogni componente, $r_{ij} = \lambda_j P_j(w_i\mid\cdot) / \sum_k \lambda_k P_k(w_i\mid\cdot)$; **M**: $\lambda_j \leftarrow \frac1M\sum_i r_{ij}$. Si ripete fino a convergenza: la log-verosimiglianza del held-out non diminuisce mai.

<a id="p-26"></a>

### Slide 26 · Interpolazione su I am Sam

Bigram e unigram mescolati con $\lambda_1 = \lambda_2 = 1/2$; conteggi unigram su $N = 17$ token.

- **am Sam**: $\frac12\cdot\frac{2}{17} + \frac12\cdot\frac12 = \frac{21}{68} = 0{,}31$. La MLE era 0,5, l'add-one dava 0,15.
- **am I**: $\frac12\cdot\frac{3}{17} + \frac12\cdot0 = \frac{3}{34} = 0{,}09$. Mai visto dopo *am*, ma *I* è un token frequente (3 su 17).
- **I like**: $\frac12\cdot\frac{1}{17} + \frac12\cdot0 = \frac{1}{34} = 0{,}03$. La frase di test non è più impossibile.
- **Totale**: sommando sugli 11 token successivi, $\frac12\cdot1 + \frac12\cdot1 = 1$: una distribuzione di probabilità (l'unigram somma a 1 sugli 11 token, il bigram dopo *am* pure).

Rispetto all'add-one: **i bigram visti conservano più probabilità** (0,31 contro 0,15), e **quelli mai visti ricevono una quota che dipende dalla frequenza della parola** (am I 0,09, am like $\frac12\cdot\frac1{17} = 0{,}03$), invece di 1/13 per tutti. Tutti i valori verificati in Python.

> **Da saper fare: La frase di test con l'interpolazione**
>
> <s> I like green eggs and ham </s>, con $\hat P = \frac12 P_{\text{uni}} + \frac12 P_{\text{bi}}$:
>
> - $P(\text{I}\mid\text{&lt;s&gt;}) = \frac12\cdot\frac3{17} + \frac12\cdot\frac23 = 0{,}422$
> - $P(\text{like}\mid\text{I}) = \frac1{34} = 0{,}029$
> - like→green, green→eggs, eggs→and, and→ham: $\frac12\cdot\frac1{17} + \frac12\cdot1 = 0{,}529$ ciascuno
> - $P(\text{&lt;/s&gt;}\mid\text{ham}) = \frac12\cdot\frac3{17} + \frac12\cdot1 = 0{,}588$
>
> Prodotto $5{,}7\times10^{-4}$, perplexity su 7 token $= 2{,}90$, contro 6,53 dell'add-one ([scheda 20](L05-smoothing-ed-entropia.md#p-20)): a parità di frase, l'interpolazione la trova molto meno sorprendente. Calcolo verificato in Python.

<a id="p-27"></a>

### Slide 27 · Stupid backoff

$$S(w_i\mid w_{i-N+1:i-1}) = \begin{cases}\dfrac{\text{count}(w_{i-N+1:i})}{\text{count}(w_{i-N+1:i-1})} & \text{se count}(w_{i-N+1:i}) &gt; 0\\[2mm] \lambda\, S(w_i\mid w_{i-N+2:i-1}) & \text{altrimenti}\end{cases}$$

- **Backoff**: se l'n-gram che serve ha conteggio zero, si ripiega sull'(n-1)-gram, e si continua finché si trova una storia con qualche conteggio.
- **Discounting**: perché un modello a backoff dia una **vera distribuzione**, gli n-gram di ordine alto vanno **scontati**, per lasciare massa agli ordini bassi. Se no si sommano la massa piena dell'ordine alto (che già fa 1 sui visti) e quella aggiunta dagli ordini bassi.
- **Stupid backoff** (Brants et al. 2007): **niente discounting**. Un conteggio zero ripiega sull'ordine più basso, moltiplicato per un peso $\lambda$ **fisso** e indipendente dal contesto; Brants et al. trovarono che **$\lambda = 0{,}4$** funziona bene.
- **Uno score**: per questo si scrive $S$ e non $P$, perché **non è una distribuzione di probabilità** (gli score di un contesto non sommano a 1). Il backoff termina nell'unigram, $S(w) = \text{count}(w)/N$.

Perché si usa lo stesso: è semplicissimo e veloce su corpora enormi (Brants et al. lo usavano per la traduzione automatica con n-gram stimati su testo web), e se lo score serve solo a **confrontare** ipotesi, la normalizzazione non conta. Non si può però calcolarne la perplexity in modo sensato.

<a id="p-28"></a>

### Slide 28 · Stupid backoff su I am Sam

Un modello trigram, $\lambda = 0{,}4$, dopo il contesto **Sam I**; il corpus contiene *Sam I am* una volta (e $C(\text{Sam I}) = 1$).

- **$S(\text{am}\mid\text{Sam I})$** $= C(\text{Sam I am})/C(\text{Sam I}) = 1/1 = 1$: il trigram c'è, si usa la MLE trigram.
- **$S(\text{do}\mid\text{Sam I})$**: nessun trigram, si ripiega sul bigram: $0{,}4\times C(\text{I do})/C(\text{I}) = 0{,}4\times1/3 = 0{,}13$.
- **$S(\text{Sam}\mid\text{Sam I})$**: né trigram né bigram (*I Sam* non c'è): $0{,}4\times0{,}4\times C(\text{Sam})/N = 0{,}16\times2/17 = 0{,}019$. Ogni livello di backoff moltiplica per un altro $\lambda$.
- **Totale**: sommando sugli 11 token successivi gli score fanno **1,27**.

Messaggio: **niente discounting, niente normalizzazione**: uno score, non una probabilità. Il trigram visto si prende già tutto il valore 1, e tutto ciò che arriva dal backoff è in più.

> **Da saper fare: Da dove viene 1,27**
>
> I 9 token che non seguono mai *I* (tutti tranne am e do) ripiegano sull'unigram, con conteggi I 3, Sam 2, </s> 3, not, like, green, eggs, and, ham 1 ciascuno: somma 14.
>
> $$1 + 0{,}4\cdot\tfrac13 + 0{,}16\cdot\tfrac{14}{17} = 1 + 0{,}133 + 0{,}132 = 1{,}265 \approx 1{,}27$$
>
> Verificato in Python token per token (I 0,028; </s> 0,028; Sam 0,019; gli altri sei 0,0094). Un backoff «corretto» (es. Katz) sconterebbe il trigram sotto 1 e normalizzerebbe la massa lasciata agli ordini bassi in modo che il totale sia esattamente 1.

<a id="p-29"></a>
**Slide 29 · Pausa** — Pausa di 10 minuti; dopo la pausa: entropia e cross-entropy.

## Entropia, cross-entropy e perplexity

<a id="p-30"></a>
**Slide 30 · Perplexity ed entropia** — Terza parte: da dove viene la perplexity. Entropia, cross-entropy e perplexity come 2 elevato alla cross-entropy (§3.7 del libro).

<a id="p-31"></a>

### Slide 31 · Entropia

$$H(X) = -\sum_{x\in\chi} p(x)\log_2 p(x)$$

L'**entropia** è una misura di informazione (o di incertezza).

- **La variabile aleatoria** $X$ varia su ciò che si sta predicendo: parole, lettere, parti del discorso; l'insieme dei valori si chiama $\chi$, con una funzione di probabilità $p(x)$.
- **Bit**: il logaritmo si può calcolare in qualunque base; con base 2 l'entropia si misura in **bit** (con $\ln$ in *nat*; $1$ nat $= 1/\ln 2 \approx 1{,}44$ bit).
- **Un limite inferiore** al numero di bit necessari per codificare una certa decisione o informazione, nello **schema di codifica ottimale**: le schede 32-35 lo mostrano con le corse di cavalli.

Casi da saper dire: una moneta equa ha $H = 1$ bit; un evento certo ha $H = 0$ (convenzione $0\log 0 = 0$); una distribuzione uniforme su $k$ valori ha il massimo, $H = \log_2 k$. Ogni termine $-\log_2 p(x)$ è la **sorpresa** di $x$: l'entropia è la sorpresa media.

<a id="p-32"></a>

### Slide 32 · La corsa di cavalli: 3 bit per corsa

L'esempio classico di Cover e Thomas (1991). Si vuole mandare un messaggio breve all'allibratore: **su quale degli otto cavalli** puntare.

Codice più semplice: il **numero del cavallo in binario**, tre bit: 1 → 001, 2 → 010, …, 7 → 111, e 8 → 000. Ogni corsa costa **3 bit**, qualunque cavallo si scelga.

Domanda che apre le schede successive: si può fare di meglio? Dipende da **quanto sono probabili** le scelte. Se alcuni cavalli si scelgono molto più spesso di altri, conviene dare loro codici più corti.

<a id="p-33"></a>

### Slide 33 · Cavalli non equiprobabili: H = 2 bit

Ora le puntate hanno una distribuzione (lo *spread* delle scommesse, usato come probabilità a priori): cavallo 1: 1/2, 2: 1/4, 3: 1/8, 4: 1/16, cavalli 5-8: 1/64 ciascuno. Il codice in tabella è ancora quello a 3 bit della scheda precedente.

$$H(X) = -\tfrac12\log_2\tfrac12 - \tfrac14\log_2\tfrac14 - \tfrac18\log_2\tfrac18 - \tfrac1{16}\log_2\tfrac1{16} - 4\left(\tfrac1{64}\log_2\tfrac1{64}\right) = \tfrac12 + \tfrac12 + \tfrac38 + \tfrac14 + \tfrac38 = 2 \text{ bit}$$

L'entropia è un **limite inferiore** al numero medio di bit per corsa: nessun codice può fare in media meno di 2 bit. Il codice a 3 bit spreca quindi 1 bit per corsa: tratta come ugualmente probabili scelte che non lo sono.

> **Da saper fare: Calcolare un'entropia a mano**
>
> Per ogni valore: $p\cdot(-\log_2 p)$. Con probabilità potenze di 2 i log sono interi: $-\log_2\frac12 = 1$, $-\log_2\frac14 = 2$, $-\log_2\frac18 = 3$, $-\log_2\frac1{16} = 4$, $-\log_2\frac1{64} = 6$. Quindi $\frac12\cdot1 + \frac14\cdot2 + \frac18\cdot3 + \frac1{16}\cdot4 + 4\cdot\frac1{64}\cdot6 = 2$. Controllo: le probabilità sommano a $\frac12+\frac14+\frac18+\frac1{16}+\frac4{64} = 1$.

<a id="p-34"></a>

### Slide 34 · Un codice da 2 bit in media

Codici corti per i cavalli più probabili (in grassetto blu nella tabella): 1 → `0`, 2 → `10`, 3 → `110`, 4 → `1110`, 5-8 → `111100`, `111101`, `111110`, `111111`.

Lunghezza media:

$$\tfrac12\times1 + \tfrac14\times2 + \tfrac18\times3 + \tfrac1{16}\times4 + 4\times\tfrac1{64}\times6 = 2 \text{ bit per corsa}$$

- La lunghezza di ogni codice è esattamente $-\log_2 p$ (1, 2, 3, 4, 6 bit): per questo la media coincide con l'entropia e il codice è **ottimale**.
- Il codice è **a prefisso**: nessuna parola di codice è l'inizio di un'altra, quindi una sequenza di bit si decodifica senza separatori (`0110` = cavallo 1, poi cavallo 3).

> **Approfondimento: Teorema della codifica di sorgente**
>
> (Facoltativo, teoria dell'informazione standard.) Per ogni codice a prefisso la lunghezza media $L$ soddisfa $L \ge H(X)$, e il codice di Huffman raggiunge $H(X) \le L &lt; H(X)+1$. L'uguaglianza $L = H$ si ha solo quando tutte le probabilità sono potenze di $1/2$, come qui. Codificando blocchi di simboli insieme ci si avvicina a $H$ quanto si vuole.

<a id="p-35"></a>

### Slide 35 · Cavalli equiprobabili: 3 bit

Se ogni cavallo ha probabilità $p = 1/8$:

$$H(X) = -\sum_{i=1}^{8}\tfrac18\log_2\tfrac18 = -\log_2\tfrac18 = 3 \text{ bit}$$

Il codice a lunghezza fissa di 3 bit della [scheda 32](L05-smoothing-ed-entropia.md#p-32) è **già ottimale**: la sua lunghezza media è l'entropia. Con scelte equiprobabili non c'è struttura da sfruttare.

Il confronto tra le schede 33 e 35 è la stessa idea della perplexity come **fattore di ramificazione pesato** ([L4, schede 33-35](L04-modelli-linguistici-n-gram.md#p-33)): otto alternative equiprobabili valgono $2^3 = 8$ scelte; la distribuzione sbilanciata vale $2^2 = 4$ scelte «effettive», anche se i cavalli sono sempre otto.

<a id="p-36"></a>

### Slide 36 · Entropia di una sequenza

Finora una sola variabile; per il linguaggio servono **sequenze**.

- **Sequenze di $n$ parole**: l'entropia di una variabile aleatoria che varia su tutte le sequenze di $n$ parole di un linguaggio $L$: $$H(w_1,\dots,w_n) = -\sum_{w_{1:n}\in L} p(w_{1:n})\log p(w_{1:n})$$
- **Entropy rate** (entropia per parola): l'entropia della sequenza divisa per il **numero di parole**: $$\tfrac1n H(w_{1:n}) = -\tfrac1n\sum_{w_{1:n}\in L} p(w_{1:n})\log p(w_{1:n})$$
- **Entropia di un linguaggio**: si vede il linguaggio come un **processo stocastico** $L$ che produce una sequenza di parole; la sua vera entropia richiede sequenze di lunghezza infinita: $$H(L) = \lim_{n\to\infty}\tfrac1n H(w_{1:n}) = -\lim_{n\to\infty}\tfrac1n\sum_{W\in L} p(w_{1:n})\log p(w_{1:n})$$

Il problema pratico: la somma è su **tutte** le sequenze possibili, e per di più nel limite; nessuno la può calcolare. La scheda successiva mostra come aggirarla. (Nell'ultima formula $W$ indica la sequenza $w_{1:n}$: è la notazione del libro.)

<a id="p-37"></a>

### Slide 37 · Il teorema di Shannon-McMillan-Breiman

$$H(L) = \lim_{n\to\infty} -\frac1n\log p(w_{1:n})$$

- **Una sola sequenza lunga**: se il linguaggio è «regolare» in certi modi, cioè **stazionario ed ergodico**, invece di sommare su tutte le sequenze possibili basta prendere **una singola sequenza abbastanza lunga**.
- **L'intuizione**: una sequenza abbastanza lunga contiene moltissime sequenze più corte, e ognuna ricompare al suo interno con una frequenza pari alla sua probabilità; la media sul tempo sostituisce la media sulle sequenze.
- **Stazionario**: le probabilità assegnate a una sequenza sono invarianti per traslazioni dell'indice temporale; la distribuzione al tempo $t$ è la stessa che al tempo $t+1$. I **modelli di Markov, e quindi gli n-gram, sono stazionari**: in un bigram $P_i$ dipende solo da $P_{i-1}$, in qualunque punto della sequenza.
- **Il linguaggio naturale non è stazionario**: la probabilità delle prossime parole può dipendere da eventi arbitrariamente lontani e dal tempo (argomento del discorso, cose dette pagine prima, attualità). I modelli statistici danno quindi solo un'approssimazione delle distribuzioni e delle entropie vere.

Conclusione pratica: con assunzioni scorrette ma comode, **l'entropia si stima dalla log probabilità media di un campione molto lungo**. È esattamente quello che si fa calcolando la perplexity su un test set grande.

<a id="p-38"></a>

### Slide 38 · Cross-entropy

- **Definizione**: non si conosce la vera distribuzione $p$ che ha generato i dati; si ha un **modello** $m$ di $p$. La cross-entropy di $m$ su $p$ è $$H(p,m) = \lim_{n\to\infty} -\frac1n\sum_{W\in L} p(w_1,\dots,w_n)\log m(w_1,\dots,w_n)$$ Si estraggono le sequenze secondo $p$, ma si sommano i log delle loro probabilità secondo $m$.
- **Una sola sequenza lunga**: per un processo stazionario ed ergodico, come per l'entropia: $$H(p,m) = \lim_{n\to\infty} -\frac1n\log m(w_1w_2\dots w_n)$$ Il testo vero (il test set) è un campione da $p$; basta valutarlo con $m$. Non serve conoscere $p$.
- **Un limite superiore**: per ogni modello $m$, $$H(p) \le H(p,m)$$ Più $m$ è accurato, più $H(p,m)$ è vicina a $H(p)$; tra due modelli, il più accurato ha la **cross-entropy più bassa**.

Frase finale della slide (dal libro): poiché la cross-entropy non può mai essere più bassa della vera entropia, un modello non può sbagliare **sottostimando** l'entropia vera. Cioè: qualunque modello si costruisca, la sua cross-entropy è una stima per eccesso; abbassarla avvicina sempre alla verità, non c'è rischio di «scendere troppo».

> **Approfondimento: Cross-entropy = entropia + divergenza KL**
>
> (Facoltativo, risultato standard.) Per distribuzioni su un singolo simbolo: $H(p,m) = -\sum_x p(x)\log m(x) = H(p) + D_{\text{KL}}(p\,\|\,m)$, con $D_{\text{KL}}(p\|m) = \sum_x p(x)\log\frac{p(x)}{m(x)} \ge 0$ (disuguaglianza di Gibbs), nulla solo se $m = p$. Da qui $H(p) \le H(p,m)$: il «costo in più» di usare $m$ al posto di $p$ è la divergenza KL. Esempio: dati i cavalli della [scheda 33](L05-smoothing-ed-entropia.md#p-33) e il codice uniforme a 3 bit (cioè $m$ uniforme), $H(p,m) = 3$ bit $= 2 + 1$: un bit di KL.

<a id="p-39"></a>

### Slide 39 · La perplexity è 2 elevato alla cross-entropy

$$H(W) = -\frac1N\log_2 P(w_1w_2\dots w_N)\qquad \text{Perplexity}(W) = 2^{H(W)} = P(w_1w_2\dots w_N)^{-\frac1N} = \sqrt[N]{\frac{1}{P(w_1w_2\dots w_N)}}$$

- **Lunghezza fissa**: la cross-entropy è definita nel limite; la si approssima su una sequenza abbastanza lunga di lunghezza fissa $N$, per un modello $M = P(w_i\mid w_{i-N+1:i-1})$. (Qui la $N$ del modello è l'ordine dell'n-gram, quella di $H(W)$ è la lunghezza del test set: il libro usa la stessa lettera per due cose, come già nella [L4, scheda 10](L04-modelli-linguistici-n-gram.md#p-10).)
- **Perplexity**: formalmente definita come **2 elevato a questa cross-entropy**.
- **L'inversa**: $2^{-\frac1N\log_2 P(w_1\dots w_N)} = P(w_1\dots w_N)^{-1/N}$, cioè la probabilità inversa del test set normalizzata per la lunghezza: la definizione della [L4, scheda 30](L04-modelli-linguistici-n-gram.md#p-30). Il segno meno dell'entropia diventa l'inverso.
- **Bit per parola**: una cross-entropy di $H$ bit per parola corrisponde a una perplexity di $2^H$: il modello è incerto come una **scelta uniforme tra $2^H$ parole**.

Ecco risolto il mistero della L4: la perplexity è una probabilità inversa perché è l'esponenziale di una cross-entropy. **Cross-entropy più bassa, perplexity più bassa: modello migliore.** La base non conta: $e^{H_{\text{nat}}} = 2^{H_{\text{bit}}}$, la perplexity è la stessa.

> **Da saper fare: Passare tra perplexity e bit**
>
> $H = \log_2\text{PP}$, $\text{PP} = 2^H$. Esempi: PP 8 ↔ 3 bit; PP 1024 ↔ 10 bit; ogni bit in meno **dimezza** la perplexity. In pratica: $H = -\frac1N\sum_i\log_2 P(w_i\mid\text{contesto})$, la media della sorpresa per token; con log naturali è la loss media di training, e $\text{PP} = e^{\text{loss}}$.

<a id="p-40"></a>

### Slide 40 · Perplexity in bit: red, blue, green

$T = $ *red red red red blue*, dalla [L4, scheda 33](L04-modelli-linguistici-n-gram.md#p-33) ($N = 5$).

- **Modello A**, $P = 1/3$ per ogni colore: $H(T) = -\frac15\times5\times\log_2\frac13 = 1{,}58$ bit per parola; perplexity $2^{1{,}58} = 3$ (esatto: $\log_2 3 = 1{,}585$, e $2^{\log_2 3} = 3$).
- **Modello B**, $P(\text{red}) = 0{,}8$, $P(\text{blue}) = 0{,}1$ (e green 0,1): $H(T) = -\frac15(4\log_2 0{,}8 + \log_2 0{,}1) = -\frac15(4\cdot(-0{,}322) + (-3{,}322)) = 0{,}92$ bit per parola; perplexity $2^{0{,}92} = 1{,}89$. Sono gli stessi 3 e 1,89 della [L4, scheda 35](L04-modelli-linguistici-n-gram.md#p-35).
- **Wall Street Journal**: le perplexity unigram, bigram e trigram 962, 170 e 109 ([L4, scheda 32](L04-modelli-linguistici-n-gram.md#p-32)) sono 9,9, 7,4 e 6,8 bit per parola ($\log_2 962 = 9{,}91$, $\log_2 170 = 7{,}41$, $\log_2 109 = 6{,}77$).

Lo stesso confronto tra modelli, misurato in bit per parola. Nota la scala: passare da unigram a bigram fa risparmiare 2,5 bit per parola, da bigram a trigram solo 0,6. Valori verificati in Python (le potenze della slide usano esponenti arrotondati: $2^{1{,}58} = 2{,}99$, $2^{0{,}9219} = 1{,}895$).

> **Da saper fare: Cross-entropy di un modello unigram su una sequenza**
>
> $H(T) = -\frac1N\sum_w c_w\log_2 p_w$. Per il modello C della L4 ($P(\text{red}) = 0{,}5$, blue e green 0,25): $H = -\frac15(4\cdot(-1) + (-2)) = 1{,}2$ bit, $\text{PP} = 2^{1{,}2} = 2{,}30$, come nella L4. Utile ricordare $\log_2 0{,}8 = -0{,}322$, $\log_2 0{,}1 = -3{,}322$, $\log_2 3 = 1{,}585$.

## Verso i modelli neurali

<a id="p-41"></a>

### Slide 41 · Che cosa passa ai large language model

- **Next-token prediction**: come gli n-gram, gli LLM sono addestrati a **predire il token successivo** ([L1, scheda 5](L01-introduzione-al-corso.md#p-5)); le probabilità vengono da una rete neurale invece che da conteggi.
- **Training e test set**: la stessa disciplina: si addestra, si regola sui dati held-out, si testa una volta sola ([L4, scheda 27](L04-modelli-linguistici-n-gram.md#p-27)). Con dati di training presi dal web, la **data contamination** (test set finito nel training) è un rischio reale ([L4, scheda 28](L04-modelli-linguistici-n-gram.md#p-28)).
- **Cross-entropy**: è la **loss** minimizzata per addestrare i modelli linguistici neurali ([L1, scheda 57](L01-introduzione-al-corso.md#p-57)); la perplexity resta la loro metrica, $2^H$, **confrontabile solo a parità di tokenizer** (con token diversi cambiano sia $N$ sia che cosa si predice).
- **Campionamento**: il testo si genera campionando il token successivo, come si campionava dagli n-gram ([L4, scheda 37](L04-modelli-linguistici-n-gram.md#p-37)).
- **N-gram oggi**: **infini-gram**, conteggi di n-gram di lunghezza arbitraria su trilioni di token ([infini-gram.io](https://infini-gram.io)); **KenLM** per modelli n-gram grandi; l'add-one per la classificazione di testi.

Quasi tutto il vocabolario della L4 e della L5 (training/test, perplexity, cross-entropy, smoothing come regolarizzazione, campionamento) resta valido per gli LLM; cambia il modo di stimare $P(w\mid\text{contesto})$.

> **Approfondimento: Perplexity e tokenizer**
>
> (Facoltativo.) Due modelli con tokenizer diversi dividono lo stesso testo in un numero diverso di token: la perplexity per token non è confrontabile. Si confronta allora la probabilità totale del testo normalizzata per una unità comune, per esempio i **bit per byte** o per carattere: $-\log_2 P(\text{testo})/\#\text{byte}$. La probabilità del testo intero non dipende da come lo si tokenizza, il numero di token sì.

<a id="p-42"></a>

### Slide 42 · Dagli n-gram ai modelli linguistici neurali

I due grandi problemi degli n-gram (note storiche del capitolo 3), nei due riquadri:

- **Troppi parametri** (riquadro blu): il numero di parametri cresce **esponenzialmente** con l'ordine dell'n-gram, $V^N$ possibili n-gram. Shakespeare ($V = 29.066$): $V^2 = 844$ milioni di bigram possibili (verificato: $29066^2 = 844.832.356$), e $V^4 \approx 7\times10^{17}$ 4-gram ([L4, scheda 43](L04-modelli-linguistici-n-gram.md#p-43)).
- **Nessuna generalizzazione** (riquadro rosso): non c'è modo di generalizzare dagli esempi di training a quelli di test se non usano **parole identiche**. Ciò che il modello impara su una parola non dice nulla su una parola simile: aver visto *eat lunch* non aiuta con *eat dinner*.

La risposta: i modelli linguistici neurali **proiettano le parole in uno spazio continuo** (embedding), in cui parole con contesti simili hanno rappresentazioni simili; così ciò che si impara su *lunch* si trasferisce a *dinner*. I parametri non crescono più con $V^N$. I modelli **feedforward** (cap. 6), **ricorrenti** (cap. 14) e basati su **transformer** (cap. 7) costruiscono su questa idea.

<a id="p-43"></a>

### Slide 43 · Riepilogo e prossima lezione

**Riepilogo**:

- zeri: gli n-gram mai visti rendono impossibile il test set;
- lo smoothing sposta massa di probabilità dagli eventi visti a quelli non visti;
- Laplace e add-k: un conteggio aggiunto a ogni n-gram, troppa massa agli zeri;
- interpolazione: tutti gli ordini mescolati, $\lambda$ fissati su dati held-out;
- stupid backoff: ordini bassi con peso fisso, uno score e non una probabilità;
- entropia e cross-entropy in bit; perplexity $= 2^H$;
- n-gram: troppi parametri, nessuna generalizzazione tra parole.

**Prossima lezione**: **regressione logistica**, machine learning e classificazione (capitolo 4). Il legame, dall'inizio del capitolo 4: anche il language modeling è una classificazione, con una classe per ogni parola successiva possibile.

## Notebook

Commento al notebook del corso `HLT-L05-smoothing-and-entropy.ipynb` (il notebook è del docente e non è incluso).

Notebook di accompagnamento della lezione: riprende il corpus *I am Sam* e il problema degli zeri, implementa Laplace e add-k, i conteggi aggiustati del Berkeley Restaurant Project, poi passa al corpus delle docstring della libreria standard della L4 diviso questa volta in **training, development e test**: sceglie $k$ e i pesi dell'interpolazione sul development set (ricerca a griglia ed **EM**), valuta una volta sola sul test, prova lo **stupid backoff** e chiude con entropia, codici, cross-entropy e una catena di Markov che illustra il teorema di Shannon-McMillan-Breiman. Serve solo la libreria standard più `matplotlib`. Controlla gli esercizi 2, 3, 5, 6, 7, 8, 9, 10, 11 della scheda.

Ho eseguito il notebook con Python 3.13 (nbconvert): le celle sul corpus giocattolo, su entropia e catena di Markov danno gli stessi output salvati; quelle sulle docstring differiscono di poco perché il corpus dipende dalla versione di Python (2616 frasi di training invece di 2574, perplexity di test del trigram interpolato 288,2 invece di 284,9; $k$ migliore e pesi della griglia identici). Riporto gli output della mia esecuzione. Due problemi reali, verificati e corretti nei riquadri: (1) la contaminazione da docstring ereditate già trovata nella L4 c'è ancora e tocca anche il development set; corretta, il bigram add-k smette di battere l'unigram sul test; (2) l'interpolazione non è una distribuzione di probabilità nei contesti mai visti, il che penalizza il trigram e falsa i pesi trovati da EM. EM, stupid backoff, add-k, entropie e catena di Markov sono implementati correttamente.

### Notebook 1 · Il problema degli zeri

```python
SAM = ["I am Sam", "Sam I am", "I do not like green eggs and ham"]

def sentences_to_tokens(sentences, n):
    return [["<s>"] * (n - 1) + s.split() + ["</s>"] for s in sentences]

def train(sentences, n):
    counts = defaultdict(Counter)
    for toks in sentences_to_tokens(sentences, n):
        for i in range(n - 1, len(toks)):
            counts[tuple(toks[i - n + 1:i])][toks[i]] += 1
    return counts

def mle(counts, context, word):
    c = counts.get(tuple(context))
    if not c or word not in c:
        return Fraction(0)
    return Fraction(c[word], sum(c.values()))

uni, bi, tri = train(SAM, 1), train(SAM, 2), train(SAM, 3)
VOCAB = sorted(uni[()])          # ten words and </s>
N = sum(uni[()].values())
```

Output:

```text
N = 17  V = 11   ['</s>', 'I', 'Sam', 'am', 'and', 'do', 'eggs', 'green', 'ham', 'like', 'not']
P(I     | <s>  ) = 2/3
P(like  | I    ) = 0
P(green | like ) = 1
P(eggs  | green) = 1
P(and   | eggs ) = 1
P(ham   | and  ) = 1
P(</s>  | ham  ) = 1
```

Le stesse funzioni del notebook della L4 (`mle` è la vecchia `prob`): conteggi in un `Counter` per contesto, $n-1$ simboli <s> e un solo </s>. Il modello unigram (`train(SAM, 1)`) non ha <s> e conta </s>: per questo $N = 17$ e il vocabolario dei token che possono seguire una parola ha $V = 11$ elementi, come nella [scheda 5](L05-smoothing-ed-entropia.md#p-5).

La frase di test *I like green eggs and ham* usa sei bigram visti e uno solo mai visto, *I like*: $P(\text{like}\mid\text{I}) = 0/3 = 0$, quindi la probabilità della frase è 0 e la perplexity non si può calcolare (divisione per zero). È il problema degli **zeri** della [scheda 46 della L4](L04-modelli-linguistici-n-gram.md#p-46) e della [scheda 7](L05-smoothing-ed-entropia.md#p-7), in miniatura: basta un n-gram assente per azzerare un intero test set.

### Notebook 2 · Laplace: la riga di am

```python
def addk(counts, context, word, k, V):
    """Add-k estimate of P(word | context); k = 1 is Laplace (add-one) smoothing."""
    c = counts.get(tuple(context), Counter())
    return (c[word] + k) / (sum(c.values()) + k * V)

V = len(VOCAB)
for w in VOCAB:
    print(w, mle(bi, ['am'], w), addk(bi, ['am'], w, 1, V))
```

Output:

```text
after am      MLE    add-one
  </s>      1/2    0.154
  I         0      0.077
  Sam       1/2    0.154
  am        0      0.077
  ...        (the other 7 tokens: 0 and 0.077)
sum of the add-one row: 1.0
P(like | I): MLE 0, add-one 0.0714 = 1/14
```

`addk` è l'equazione 3.28 del libro, $P_{\text{add-}k}(w_n\mid w_{n-1}) = \dfrac{C(w_{n-1}w_n)+k}{C(w_{n-1})+kV}$; con $k = 1$ è Laplace (eq. 3.26, [scheda 14](L05-smoothing-ed-entropia.md#p-14)). Il denominatore è la **somma della riga** `sum(c.values())`: coincide con $C(w_{n-1})$ perché, grazie a </s>, ogni occorrenza di una parola è seguita da qualcosa. Un contesto mai visto ha riga vuota (`Counter()`) e riceve la distribuzione uniforme $k/(kV) = 1/V$.

Riga di *am* ($C(\text{am}) = 2$): $\text{Sam}$ e </s> passano da $1/2$ a $2/13 = 0{,}154$, gli altri nove token da 0 a $1/13 = 0{,}077$; somma $13/13 = 1$. È la tabella della [scheda 20](L05-smoothing-ed-entropia.md#p-20). Nove tredicesimi della massa ($9/13 = 69\%$) finiscono a token mai visti dopo *am*: con un contesto raro rispetto a $V$ add-one ridistribuisce quasi tutto. $P(\text{like}\mid\text{I}) = (0+1)/(3+11) = 1/14$.

### Notebook 3 · La frase di test con add-one

```python
def sentence_prob(p, sentence, n=2):
    toks = sentences_to_tokens([sentence], n)[0]
    return math.prod(p(toks[i - n + 1:i], toks[i]) for i in range(n - 1, len(toks)))

P = sentence_prob(lambda ctx, w: addk(bi, ctx, w, 1, V), TEST)
print(P, P ** (-1 / 7))
```

Output:

```text
add-one: P(I like green eggs and ham) = 1.97e-06, perplexity = 6.53
```

È il conto lasciato come esercizio nella [scheda 20](L05-smoothing-ed-entropia.md#p-20) (esercizio aggiuntivo A). I sette fattori add-one: $P(\text{I}\mid\text{&lt;s&gt;}) = 3/14$, $P(\text{like}\mid\text{I}) = 1/14$ e cinque fattori $2/12 = 1/6$ (*like green, green eggs, eggs and, and ham, ham </s>*: conteggio 1, contesto visto una volta). Prodotto $\frac{3}{14}\cdot\frac{1}{14}\cdot\left(\frac{1}{6}\right)^5 = \frac{1}{508032} = 1{,}97\times10^{-6}$; perplexity $(508032)^{1/7} = 6{,}53$ su $N = 7$ token (sei parole e </s>, non <s>).

Si vede il difetto di add-one: i cinque bigram che con MLE avevano probabilità 1 scendono a $1/6$, perché il loro contesto è visto una sola volta e il $+V = 11$ al denominatore pesa più del conteggio vero.

### Notebook 4 · Add-k: come k sposta la massa

```python
for k in (100, 10, 1, 0.5, 0.1, 0.01, 0):
    print(k, addk(bi, ['am'], 'Sam', k, V), addk(bi, ['am'], 'I', k, V))
print("1/V =", round(1 / V, 3))
```

Output:

```text
   k       P(Sam | am)   P(I | am)
  100      0.092         0.0907
  10       0.098         0.0893
  1        0.154         0.0769
  0.5      0.200         0.0667
  0.1      0.355         0.0323
  0.01     0.479         0.0047
  0        0.500         0.0000
1/V = 0.091
```

Con $C(\text{am Sam}) = 1$, $C(\text{am}) = 2$, $V = 11$: $P(\text{Sam}\mid\text{am}) = \frac{1+k}{2+11k}$ e $P(\text{I}\mid\text{am}) = \frac{k}{2+11k}$. Le righe $k = 1, 0{,}5, 0{,}1, 0{,}01, 0$ sono la tabella della [scheda 21](L05-smoothing-ed-entropia.md#p-21). I due estremi: per $k \to 0$ si torna alla MLE ($1/2$ e $0$); per $k \to \infty$ i conteggi veri diventano trascurabili e ogni token tende a $1/V = 0{,}091$, qualunque siano i dati (con $k = 100$ siamo già a 0,092 e 0,091). $k$ regola quanta massa passa dagli eventi visti a quelli mai visti: è un **iperparametro** da scegliere su dati separati (blocco «Scegliere k»). Esercizio 6 della scheda.

### Notebook 5 · Conteggi aggiustati del Berkeley Restaurant Project

```python
BRP_V = 1446
for bigram, c, c_prev in [("want to", 608, 927), ("chinese food", 82, 158), ("chinese to", 0, 158)]:
    c_star = (c + 1) * c_prev / (c_prev + BRP_V)
    d = f"{c_star / c:.2f}" if c else "-"
    print(bigram, c, c_star, d, (c + 1) / (c_prev + BRP_V))
```

Output:

```text
want to       C = 608   C* = 237.903   d = 0.39   P_Laplace = 0.2566
chinese food  C =  82   C* =   8.176   d = 0.10   P_Laplace = 0.0517
chinese to    C =   0   C* =   0.099   d = -   P_Laplace = 0.0006
```

Il **conteggio aggiustato** $C^* = (C+1)\,\frac{C(w_{n-1})}{C(w_{n-1})+V}$ è il conteggio che, diviso per il denominatore non smussato $C(w_{n-1})$, dà la probabilità di Laplace ([scheda 17](L05-smoothing-ed-entropia.md#p-17)); lo **sconto** è $d = C^*/C$. Riproduce le [schede 18](L05-smoothing-ed-entropia.md#p-18) e [19](L05-smoothing-ed-entropia.md#p-19): *want to* passa da 608 a 238 ($d = 0{,}39$), *chinese food* da 82 a 8,2 ($d = 0{,}10$), e un bigram mai visto dopo *chinese* riceve 0,099. Il fattore $C(w_{n-1})/(C(w_{n-1})+V)$ spiega tutto: $927/2373 = 0{,}39$ contro $158/1604 = 0{,}099$; più la prima parola è rara rispetto a $V$, più forte lo sconto. Esercizio 5 della scheda.

### Notebook 6 · Corpus delle docstring: training, development e test

```python
def module_text(name):
    """The docstring of a module and of its public functions and classes."""
    mod = importlib.import_module(name)          # (inside try/except)
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
test_modules = sorted(texts)[::10]        # the held-out modules of the last notebook
dev_modules = sorted(texts)[5::10]        # a second held-out set, for development
train_sents = [s for m, ss in texts.items() if m not in test_modules and m not in dev_modules for s in ss]
dev_sents = [s for m in dev_modules for s in texts[m]]
test_sents = [s for m in test_modules for s in texts[m]]
vocab = sorted(set(w for s in train_sents + dev_sents + test_sents for w in s.split()) | {"</s>"})
```

Output:

```text
training: 2616 sentences, 46595 tokens; development: 6744 tokens; test: 11520 tokens
V = 4505 types, of which 756 never occur in training
```

Lo stesso corpus del notebook della L4 (docstring di circa 140 moduli, in minuscolo, punteggiatura come parole; 133 moduli producono frasi), ma con **due insiemi tenuti da parte**, sempre per documento: i moduli in posizione 0, 10, 20... dell'ordine alfabetico sono il **test set** (gli stessi 14 della L4: *abc, calendar, configparser, doctest, ...*), quelli in posizione 5, 15, 25... il **development set** (13 moduli: *atexit, codeop, dataclasses, fileinput, gzip, ipaddress, mmap, pickletools, re, site, sys, traceback, wave*). Il development serve a scegliere $k$ e i $\lambda$, il test si usa una volta alla fine: la disciplina della [scheda 27 della L4](L04-modelli-linguistici-n-gram.md#p-27) e della [scheda 25](L05-smoothing-ed-entropia.md#p-25).

Il vocabolario è **chiuso per costruzione**: tutti i tipi dei tre insiemi più </s> ($V = 4505$), di cui 756 mai visti in training. È l'ipotesi dichiarata nel markdown; nella pratica si userebbe <UNK> o un tokenizzatore subword ([scheda 9](L05-smoothing-ed-entropia.md#p-9)). Quei 756 tipi ricevono probabilità solo grazie allo smoothing. I numeri della mia esecuzione (Python 3.13) differiscono di poco da quelli salvati (2574 frasi, 46.019 token, $V = 4458$), come avverte il notebook.

> **Attenzione (errore nelle slide): Bug: le docstring ereditate contaminano ancora development e test**
>
> `module_text` è identica a quella della L4, e lo è anche il bug: `inspect.getdoc(obj)`, per una classe senza docstring propria, restituisce quella della classe madre (tipicamente `Exception`), aggirando il filtro su `__module__`. Verificato eseguendo il notebook con Jupyter (Python 3.13): nei moduli di development e di test ci sono **37 classi con docstring ereditata** (per esempio `dataclasses.FrozenInstanceError`, `wave.Error`, `calendar.IllegalMonthError`, `doctest.DocTestCase`), e quindi:
>
> - **21 delle 615 frasi di test (3,4%, 252 token su 11.520) compaiono anche nel training**; sono 5 frasi distinte, e una sola, *common base class for all non-exit exceptions .*, vale 17 copie;
> - nel **development set** 3 frasi su 340 (38 token) sono nel training, tra cui la stessa frase;
> - il training ha 233 frasi duplicate (quella frase 24 volte, *base class for arithmetic errors .* 10 volte).
>
> Correzione (la stessa della L4): usare solo la docstring propria dell'oggetto.
>
> ```
>     parts = [inspect.cleandoc(mod.__doc__ or "")]
>     ...
>         d = obj.__doc__ if isinstance(getattr(obj, "__doc__", None), str) else None   # own docstring only
>         d = inspect.cleandoc(d) if d else None
> ```
>
> Verifica, rieseguendo tutto il notebook corretto in un kernel nuovo: 2526 frasi di training (45.152 token), development 6712 token, test 10.035 token, $V = 4476$; **nessuna frase di test nel training**; nel development restano 2 frasi che sono docstring proprie ripetute identiche in moduli diversi (*return a new object replacing specified fields with new values .* e una frase sugli argomenti *encoding, errors and newline*): testo davvero duplicato, che una deduplicazione esplicita toglierebbe. Le scelte fatte sul development non cambiano: $k$ migliore 0,02, griglia (0,5, 0,4, 0,1), pesi EM (0,516, 0,428, 0,055). Cambia la valutazione finale sul test:
>
> | modello | originale | corretto |
> | --- | --- | --- |
> | unigram, add-one | 519,1 | 517,0 |
> | bigram, add-k ($k = 0{,}02$) | 489,8 | 519,2 |
> | trigram interpolato, EM | 288,2 | 308,0 |
>
> La contaminazione rendeva il test più facile proprio per i modelli con contesto (le 17 copie di una frase vista 24 volte in training sono quasi gratuite per bigram e trigram): senza di essa **il bigram add-k non batte più l'unigram add-one sul test** (519,2 contro 517,0), anche se sul development lo batte nettamente (372 contro 438). Il trigram interpolato resta di gran lunga il migliore.

### Notebook 7 · Scegliere k sul development set

```python
models = {n: train(train_sents, n) for n in (1, 2, 3)}
totals = {n: {ctx: sum(c.values()) for ctx, c in models[n].items()} for n in (1, 2, 3)}

def p_addk(n, context, word, k):
    c = models[n].get(context)
    return ((c[word] if c else 0) + k) / (totals[n].get(context, 0) + k * V)

def evaluate(p, sentences, n):
    """Cross-entropy (bits per token) and perplexity of an estimator p(context, word)."""
    logp, N = 0.0, 0
    for toks in sentences_to_tokens(sentences, n):
        for i in range(n - 1, len(toks)):
            logp += math.log2(p(tuple(toks[i - n + 1:i]), toks[i]))
            N += 1
    H = -logp / N
    return H, 2 ** H

KS = [1, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001]
dev_ppl = {n: [evaluate(lambda ctx, w: p_addk(n, ctx, w, k), dev_sents, n)[1] for k in KS] for n in (1, 2, 3)}
best_k = KS[min(range(len(KS)), key=lambda i: dev_ppl[2][i])]
```

Output:

```text
   k       unigram   bigram   trigram   (perplexity on the development set)
  1          440.5    944.3    2846.4
  0.5        449.6    731.0    2520.8
  0.2        470.0    543.2    2131.2
  0.1        488.8    456.0    1883.2
  0.05       509.4    403.1    1681.1
  0.02       538.8    372.2    1486.7
  0.01       562.4    373.0    1394.7
  0.005      587.1    393.1    1350.6
  0.002      621.6    451.7    1370.1
  0.001      649.1    524.9    1451.4
best k for the bigram model: 0.02
```

`evaluate` calcola la **cross-entropy** in bit per token, $H = -\frac{1}{N}\sum_i \log_2 P(w_i\mid\text{contesto})$, e la perplexity $2^H$ ([scheda 39](L05-smoothing-ed-entropia.md#p-39)); $N$ conta </s> e non <s>, e per ogni $n$ è lo stesso (il ciclo parte da $n-1$), quindi i tre modelli sono confrontabili. Senza smoothing la perplexity sarebbe infinita: 2803 dei 6744 token di development (41,6%) hanno un bigram mai visto in training (verificato).

Lettura della tabella e del grafico (assi logaritmici, $k$ da 0,001 a 1): il **bigram** ha un minimo netto a $k = 0{,}02$ (372,2; quasi uguale a 0,01) e con $k = 1$ è peggiore dell'unigram (944 contro 440), perché add-one regala troppa massa ai circa $V^2 \approx 2\times10^7$ bigram mai visti. Il **trigram** ha il minimo a $k = 0{,}005$ ma resta sopra 1350 per ogni $k$: i suoi contesti sono quasi tutti rari, e $kV$ al denominatore domina il conteggio vero. L'**unigram** migliora al crescere di $k$ fino al bordo della griglia: il suo $k$ ottimo potrebbe essere sopra 1, ma la griglia si ferma lì. Conclusione del markdown, confermata: add-k non è un buon modo di smussare un modello linguistico ([scheda 21](L05-smoothing-ed-entropia.md#p-21), libro §3.6.2).

### Notebook 8 · Interpolazione lineare: ricerca a griglia

```python
def p_ml(n, context, word):
    c = models[n].get(context)
    return c[word] / totals[n][context] if c and word in c else 0.0

def components(context, word):
    """unigram (add-one), bigram (MLE) and trigram (MLE) estimates of P(word | context)"""
    return (p_addk(1, (), word, 1), p_ml(2, context[-1:], word), p_ml(3, context[-2:], word))

def interpolated(lambdas):
    return lambda ctx, w: sum(l * p for l, p in zip(lambdas, components(ctx, w)))

grid = [(a / 10, b / 10, round(1 - a / 10 - b / 10, 1)) for a in range(1, 11) for b in range(0, 11 - a)]
scores = [(evaluate(interpolated(l), dev_sents, 3)[1], l) for l in grid]
best_ppl, best_l = min(scores)
```

Output:

```text
55 weight vectors tried; best (unigram, bigram, trigram) = (0.5, 0.4, 0.1), development perplexity 214.6
```

L'equazione 3.29, $\hat P(w_n\mid w_{n-2}w_{n-1}) = \lambda_1 P(w_n) + \lambda_2 P(w_n\mid w_{n-1}) + \lambda_3 P(w_n\mid w_{n-2}w_{n-1})$ ([scheda 24](L05-smoothing-ed-entropia.md#p-24)), con bigram e trigram MLE e unigram add-one, perché l'unigram deve dare qualcosa anche ai 756 tipi mai visti in training. La griglia ha passo 0,1 con $\lambda_1 \ge 0{,}1$ (altrimenti tornerebbero gli zeri): $10 + 9 + \dots + 1 = 55$ vettori. Il migliore, $(0{,}5;\ 0{,}4;\ 0{,}1)$, porta la perplexity di development a **214,6**, contro 372 del miglior bigram add-k: mescolare gli ordini funziona molto meglio che aggiungere pseudo-conteggi. Scegliere i $\lambda$ sul development e non sul training è essenziale: sul training la MLE trigram vince sempre e si sceglierebbe $\lambda_3 \approx 1$ ([scheda 25](L05-smoothing-ed-entropia.md#p-25)).

> **Attenzione (errore nelle slide): Bug: l'interpolazione non è una distribuzione nei contesti mai visti**
>
> `p_ml` restituisce 0 quando il contesto non è mai stato visto in training (la MLE lì è $0/0$, indefinita). Allora la miscela non somma a 1: se manca il contesto trigram, $\sum_w \hat P(w) = \lambda_1 + \lambda_2$; se manca anche quello bigram, solo $\lambda_1$. Verificato sommando sui 4505 token del vocabolario con i pesi EM: contesto *of the* 1,000; contesto con prima parola mai vista e *the* 0,945; due parole mai viste 0,515. Non è un caso raro: nel development il contesto trigram manca nel **41,5% dei token** e quello bigram nel 6,2%. La [scheda 24](L05-smoothing-ed-entropia.md#p-24) dice giustamente che la miscela è una distribuzione, ma solo se ogni componente lo è in ogni contesto.
>
> Effetti: la perplexity è pessimistica (si butta via massa), e soprattutto la ricerca dei pesi è falsata, perché il termine trigram è spesso 0 e l'unigram è l'unico sempre definito: EM spinge $\lambda_1$ verso 0,5 e $\lambda_3$ a 0,055. Correzione: quando il contesto di un ordine non è stato visto, quel componente usa l'ordine inferiore.
>
> ```
> def components(context, word):
>     p1 = p_addk(1, (), word, 1)
>     p2 = p_ml(2, context[-1:], word) if context[-1:] in models[2] else p1
>     p3 = p_ml(3, context[-2:], word) if context[-2:] in models[3] else p2
>     return (p1, p2, p3)
> ```
>
> Verifica (stesso kernel): la somma vale 1 in ogni contesto; EM converge a $\lambda = (0{,}472;\ 0{,}352;\ 0{,}176)$, con il trigram pesato tre volte di più; perplexity di development 197,6 invece di 213,5 e di **test 263,9 invece di 288,2** (con anche la correzione delle docstring: 283,2 invece di 308,0). Le conclusioni qualitative non cambiano (l'interpolazione batte nettamente add-k), ma i numeri sì.

### Notebook 9 · EM per i pesi dell'interpolazione

```python
dev_tokens = [(tuple(t[i - 2:i]), t[i]) for t in sentences_to_tokens(dev_sents, 3) for i in range(2, len(t))]
comps = [components(ctx, w) for ctx, w in dev_tokens]
lambdas = [1 / 3, 1 / 3, 1 / 3]
for it in range(1, 21):
    shares = [0.0, 0.0, 0.0]
    for ps in comps:
        z = sum(l * p for l, p in zip(lambdas, ps))
        for j in range(3):
            shares[j] += lambdas[j] * ps[j] / z      # E step: responsibility of component j
    lambdas = [s / len(comps) for s in shares]       # M step: average responsibility
```

Output:

```text
iteration  1: lambdas = [0.491, 0.356, 0.153], development perplexity 218.0
iteration  2: lambdas = [0.516, 0.378, 0.106], development perplexity 214.9
iteration  3: lambdas = [0.519, 0.396, 0.085], development perplexity 214.1
iteration  5: lambdas = [0.517, 0.416, 0.067], development perplexity 213.6
iteration 10: lambdas = [0.515, 0.428, 0.057], development perplexity 213.5
iteration 20: lambdas = [0.515, 0.43, 0.055], development perplexity 213.5
```

L'algoritmo **EM** citato dal libro (Jelinek e Mercer 1980, [scheda 25](L05-smoothing-ed-entropia.md#p-25)) applicato ai pesi di una miscela: le probabilità dei componenti restano fisse (conteggi del training), si stimano solo i $\lambda$. **Passo E**: per ogni token del development, la quota del componente $j$ nella probabilità interpolata, $r_{ij} = \lambda_j p_j(w_i)/\sum_l \lambda_l p_l(w_i)$ (le quote di un token sommano a 1). **Passo M**: il nuovo $\lambda_j$ è la media delle quote. L'implementazione è corretta; $z$ non è mai 0 perché il termine unigram add-one è sempre positivo.

La perplexity scende a ogni iterazione (218,0 → 213,5), come garantisce EM, che converge a un ottimo locale; per i pesi di una miscela la log-verosimiglianza è concava nei $\lambda$, quindi l'ottimo è anche globale. EM trova 213,5, poco meglio della griglia (214,6) perché non è vincolato al passo 0,1. Il peso del trigram, 0,055, è basso anche per il bug del riquadro precedente; senza di esso sale a 0,176. Un'iterazione a mano: esercizio aggiuntivo B.

> **Da saper fare: Un passo di EM a mano**
>
> Due componenti con $\lambda = 0{,}5$ e tre token con $(p_\text{bi}, p_\text{uni})$ = $(0{,}6;\ 0{,}2)$, $(0;\ 0{,}1)$, $(0{,}9;\ 0{,}3)$. Quote del bigram: $0{,}3/0{,}4 = 0{,}75$; $0$; $0{,}45/0{,}6 = 0{,}75$. Nuovo $\lambda_\text{bi} = (0{,}75+0+0{,}75)/3 = 0{,}5$, $\lambda_\text{uni} = 0{,}5$. Il token con bigram nullo assegna tutta la sua quota all'unigram: è così che i token «difficili» spostano peso verso gli ordini bassi.

### Notebook 10 · Valutazione finale sul test set

```python
for name, p, n in [("unigram, add-one", lambda c, w: p_addk(1, c, w, 1), 1),
                   (f"bigram, add-k (k = {best_k})", lambda c, w: p_addk(2, c, w, best_k), 2),
                   ("trigram interpolated, EM weights", interpolated(lambdas), 3)]:
    H, pp = evaluate(p, test_sents, n)
```

Output:

```text
unigram, add-one                   cross-entropy  9.02 bits per token   perplexity  519.1   (2^9.02 = 519.1)
bigram, add-k (k = 0.02)           cross-entropy  8.94 bits per token   perplexity  489.8   (2^8.94 = 489.8)
trigram interpolated, EM weights   cross-entropy  8.17 bits per token   perplexity  288.2   (2^8.17 = 288.2)
```

Solo ora, con $k$ e $\lambda$ fissati sul development, si usa il test, **una volta**. Ogni riga dà la stessa informazione in due unità: cross-entropy in bit per token e perplexity $= 2^H$ ([scheda 39](L05-smoothing-ed-entropia.md#p-39)); per esempio $2^{8{,}17} = 288$. Un bit in meno di cross-entropy dimezza la perplexity: il trigram interpolato risparmia 0,85 bit per token rispetto all'unigram.

Le perplexity di test sono più alte di quelle di development (288 contro 213 per il trigram): i moduli di test sono documenti diversi, e il test non è stato usato per scegliere nulla, quindi è la stima onesta. Attenzione all'interpretazione del confronto bigram/unigram: con la correzione della contaminazione (riquadro del blocco sul corpus) il bigram add-k sale a 519,2 e non batte più l'unigram (517,0); con anche la correzione dell'interpolazione il trigram interpolato scende a 283,2. Un modello con 0,02 pseudo-conteggi per cella su 4505 colonne generalizza male a documenti nuovi.

### Notebook 11 · Stupid backoff

```python
def stupid_backoff(counts_by_n, N_tokens, context, word, lam=0.4):
    n = len(context) + 1
    if n == 1:
        return counts_by_n[1][()][word] / N_tokens
    c = counts_by_n[n].get(tuple(context))
    if c and c[word] > 0:
        return c[word] / sum(c.values())
    return lam * stupid_backoff(counts_by_n, N_tokens, context[1:], word, lam)

sam_counts = {1: uni, 2: bi, 3: tri}
for w in ("am", "do", "Sam"):
    print(w, stupid_backoff(sam_counts, N, ('Sam', 'I'), w))
```

Output:

```text
S(am | Sam I) = 1.000
S(do | Sam I) = 0.133
S(Sam | Sam I) = 0.019
sum over the 11 next tokens: 1.265

context of the    : scores sum to 1.341
context return the: scores sum to 1.428
context if the    : scores sum to 1.402
```

Equazione 3.31 in forma ricorsiva: frequenza relativa dell'n-gram più lungo visto, altrimenti $\lambda = 0{,}4$ volte lo score con un contesto più corto, fino all'unigram $\text{count}(w)/N$. L'implementazione è corretta (verificata con un'implementazione indipendente). Riproduce la [scheda 28](L05-smoothing-ed-entropia.md#p-28): $S(\text{am}\mid\text{Sam I}) = 1$, $S(\text{do}\mid\text{Sam I}) = 0{,}4\cdot1/3 = 0{,}133$, $S(\text{Sam}\mid\text{Sam I}) = 0{,}16\cdot2/17 = 0{,}019$. La somma sugli 11 token è $1 + 0{,}4/3 + 0{,}16\cdot14/17 = 1{,}265$ (la slide arrotonda a 1,27): **non è una distribuzione**, perché la massa dei livelli alti non è scontata ([scheda 27](L05-smoothing-ed-entropia.md#p-27)). Sul corpus delle docstring le somme vanno da 1,34 a 1,43. Va bene per ordinare candidati (Brants et al. 2007, su enormi corpora), non per calcolare una perplexity. L'esercizio 9 della scheda usa il contesto *I am*: somma $473/425 = 1{,}113$.

### Notebook 12 · Entropia e codici

```python
def entropy(probs):
    return -sum(p * math.log2(p) for p in probs if p > 0)

def average_length(probs, code):
    return sum(p * len(c) for p, c in zip(probs, code))

horses = [1/2, 1/4, 1/8, 1/16, 1/64, 1/64, 1/64, 1/64]
entropy(horses), average_length(horses, ["0", "10", "110", "1110", "111100", "111101", "111110", "111111"])
```

Output:

```text
horse race: 2.0 bits; code 0, 10, 110, ...: 2.0 bits
eight equally likely horses: 3.0 bits
four horses 1/2, 1/4, 1/8, 1/8: 1.75 bits; code 0, 10, 110, 111: 1.75
a fair die: 2.585 bits; code 00, 01, 100, 101, 110, 111: 2.667 bits
```

Entropia $H(X) = -\sum_x p(x)\log_2 p(x)$ (eq. 3.32, [scheda 31](L05-smoothing-ed-entropia.md#p-31)); il `if p > 0` applica la convenzione $0\log 0 = 0$. La corsa di cavalli delle [schede 33](L05-smoothing-ed-entropia.md#p-33)-[34](L05-smoothing-ed-entropia.md#p-34): 2 bit, raggiunti dal codice a lunghezza variabile; otto cavalli equiprobabili: 3 bit ([scheda 35](L05-smoothing-ed-entropia.md#p-35)). Quando le probabilità sono potenze di $1/2$ esiste un codice con lunghezze esattamente $-\log_2 p(x)$, e la lunghezza media è uguale all'entropia (1,75 bit per i quattro cavalli dell'esercizio 10).

Il dado: $\log_2 6 = 2{,}585$ bit, ma il miglior codice per un singolo lancio (lunghezze 2, 2, 3, 3, 3, 3, prefix-free, quello di Huffman) ha media $16/6 = 2{,}667$: le lunghezze devono essere intere. Codificando blocchi di lanci ci si avvicina all'entropia: $6^5 = 7776 \le 2^{13}$, quindi 13 bit per 5 lanci, 2,6 bit a lancio.

### Notebook 13 · Cross-entropy e perplexity: i colori

```python
def cross_entropy(p, m):
    return -sum(px * math.log2(m[x]) for x, px in p.items())

p = {"red": 0.5, "blue": 0.25, "green": 0.25}
A = {"red": 1/3, "blue": 1/3, "green": 1/3}
B = {"red": 0.8, "blue": 0.1, "green": 0.1}
```

Output:

```text
H(p) = 1.500 bits
H(p, p itself) = 1.500 bits   perplexity 2.83
H(p, model A ) = 1.585 bits   perplexity 3.00
H(p, model B ) = 1.822 bits   perplexity 3.54
```

Per simboli indipendenti la cross-entropy per token è $H(p,m) = -\sum_x p(x)\log_2 m(x)$: si pesa con la distribuzione vera $p$, si misura con il modello $m$ ([scheda 38](L05-smoothing-ed-entropia.md#p-38)). $H(p) = 1{,}5$ bit; $H(p,A) = \log_2 3 = 1{,}585$; $H(p,B) = 0{,}5\cdot0{,}322 + 0{,}5\cdot3{,}322 = 1{,}822$. Entrambi sopra $H(p)$, come vuole la disuguaglianza $H(p) \le H(p,m)$ (eq. 3.41), con uguaglianza solo per $m = p$. Qui **A è migliore di B**: B è troppo sicuro del rosso e paga 3,32 bit per ogni blu o verde.

Nella [scheda 40](L05-smoothing-ed-entropia.md#p-40) (e nella [scheda 35 della L4](L04-modelli-linguistici-n-gram.md#p-35)) B vinceva su *red red red red blue* (0,92 bit contro 1,58): quella sequenza ha l'80% di rosso, non è un campione tipico di questa $p$. La cross-entropy misurata su un test set dipende da quanto il test rappresenta la distribuzione vera. Esercizio 11 della scheda.

### Notebook 14 · Una sola sequenza lunga: Shannon-McMillan-Breiman

```python
T = {"red":   {"red": 0.8, "blue": 0.1, "green": 0.1},     # P(next color | current color)
     "blue":  {"red": 0.3, "blue": 0.4, "green": 0.3},
     "green": {"red": 0.5, "blue": 0.25, "green": 0.25}}
pi = {c: 1 / 3 for c in COLORS}                  # stationary distribution, by power iteration
for _ in range(200):
    pi = {c: sum(pi[a] * T[a][c] for a in COLORS) for c in COLORS}
rate = sum(pi[a] * entropy(T[a].values()) for a in COLORS)
# sample 100000 colors from the chain (first one from pi), then -1/n log2 P under three models
est_chain = per_token(lambda i, x: math.log2(pi[x] if i == 0 else T[seq[i - 1]][x]))
est_uniform = per_token(lambda i, x: math.log2(1 / 3))
est_unigram = per_token(lambda i, x: math.log2(pi[x]))
```

Output:

```text
stationary distribution: {'red': 0.664, 'blue': 0.177, 'green': 0.159}
entropy rate of the chain: 1.1289 bits per color; entropy of the stationary unigram: 1.2568
n =     10   chain 0.7904   unigram 0.7820   uniform 1.5850
n =    100   chain 1.1329   unigram 1.3418   uniform 1.5850
n =   1000   chain 1.0679   unigram 1.2354   uniform 1.5850
n =  10000   chain 1.1002   unigram 1.2322   uniform 1.5850
n = 100000   chain 1.1225   unigram 1.2529   uniform 1.5850
```

Una catena di Markov sui tre colori è un processo **stazionario ed ergodico** (se parte dalla distribuzione stazionaria, come qui), quindi vale il teorema di Shannon-McMillan-Breiman: $-\frac{1}{n}\log_2 P(w_{1:n})$ su una sola sequenza lunga converge all'entropy rate (eq. 3.38 e 3.40, [scheda 37](L05-smoothing-ed-entropia.md#p-37)). Distribuzione stazionaria esatta $\pi = (75, 20, 18)/113 = (0{,}664;\ 0{,}177;\ 0{,}159)$; entropy rate $\sum_a \pi_a H(T_a) = 0{,}664\cdot0{,}922 + 0{,}177\cdot1{,}571 + 0{,}159\cdot1{,}5 = 1{,}1289$ bit per colore (verificato con numpy). Il calcolo nel notebook è corretto.

Il grafico (asse $n$ logaritmico) mostra tre curve: la catena stessa converge lentamente alla linea tratteggiata dell'entropy rate (1,1225 a $n = 10^5$); il modello unigram con le frequenze $\pi$ converge alla sua cross-entropy, che è $H(\pi) = 1{,}2568$; il modello uniforme dà sempre $\log_2 3 = 1{,}585$. I modelli più semplici hanno cross-entropy più alta: il modello vero ha la più bassa ([scheda 38](L05-smoothing-ed-entropia.md#p-38)). Una precisazione al markdown («the two simpler models stay above the entropy rate»): vale nel limite, non per ogni campione; a $n = 10$ tutte le stime sono sotto l'entropy rate e l'unigram (0,782) è perfino sotto la catena (0,790). Su sequenze corte un modello sbagliato può sembrare migliore: per questo servono test set lunghi. L'ultima cella del notebook propone esercizi: cambiare moduli di development e test, aggiungere un termine 4-gram, sostituire l'unigram add-one con add-k.

> **Approfondimento: Perché l'unigram converge a H(π)**
>
> Facoltativo. Il modello unigram assegna a ogni colore $\pi(x)$, indipendentemente dal precedente. Su una sequenza lunga generata dalla catena ogni colore compare con frequenza $\pi(x)$ (ergodicità), quindi $-\frac{1}{n}\sum_i \log_2\pi(x_i) \to -\sum_x \pi(x)\log_2\pi(x) = H(\pi)$. La differenza $H(\pi) - H_\text{rate} = 1{,}2568 - 1{,}1289 = 0{,}128$ bit è l'informazione che il colore precedente dà sul successivo (l'informazione mutua tra colori consecutivi): è quanto guadagna un bigram rispetto a un unigram su questo processo.

## Studio ed esercizi

### Guida allo studio (circa 4 h 00 min)

**Zeri, Laplace e add-k** (60 min)

Schede 4-21. Saper spiegare perché un solo zero rende impossibile il test set e la perplexity indefinita (schede 4-5, 7); vocabolario aperto e chiuso, <UNK> e perché con BPE non ci sono token sconosciuti (scheda 9). Laplace per unigram e bigram con il $+V$ al denominatore e il perché (schede 10, 14); rifare a mano le righe di *want* e *lunch* (schede 12-16) e i conteggi aggiustati con lo sconto $d$ (schede 17-19); tabella di *am* su I am Sam (scheda 20) e add-k con i due limiti (scheda 21). Esercizi 1-6 e aggiuntivo A; controllare con le celle 2-10 del notebook. Libro §3.6 fino a §3.6.2.

**Interpolazione e backoff** (45 min)

Schede 22-28. Differenza tra interpolazione (tutti gli ordini, sempre) e backoff (l'ordine più alto con conteggi); formula 3.29, perché i $\lambda$ devono sommare a 1, pesi condizionati dal contesto (3.30), held-out set ed EM come iperparametri (schede 24-25); conto della scheda 26; stupid backoff, perché è uno score e non una probabilità, $\lambda = 0{,}4$ (schede 27-28). Esercizi 7, 8, 9 e aggiuntivo B; celle 17-24 del notebook, compresi i due riquadri sui bug. Libro §3.6.3-3.6.4.

**Entropia, cross-entropy, perplexity** (55 min)

Schede 30-40. Definizione di entropia in bit e lettura come limite inferiore della lunghezza media di un codice: rifare le tre corse di cavalli (schede 32-35). Entropia di sequenze, entropy rate, entropia di un linguaggio come limite (scheda 36); Shannon-McMillan-Breiman, stazionarietà ed ergodicità, perché la lingua non è stazionaria (scheda 37); cross-entropy e disuguaglianza $H(p) \le H(p,m)$ (scheda 38); perplexity $= 2^{H}$ e conversioni bit/perplexity, WSJ 962/170/109 (schede 39-40). Esercizi 10, 11 e aggiuntivo C; celle 25-32 del notebook. Libro §3.7.

**Dagli n-gram agli LLM** (15 min)

Schede 41-43. Che cosa resta negli LLM (next-token prediction, train/dev/test, cross-entropy come loss, perplexity confrontabile solo a parità di tokenizzatore, campionamento) e i due limiti degli n-gram: parametri esponenziali nell'ordine e nessuna generalizzazione tra parole simili. Esercizio 12. Libro §3.8 e note storiche del capitolo 3 (Laplace, Jelinek, Kneser-Ney, KenLM).

**Notebook: protocollo sperimentale** (35 min)

Eseguire le celle 11-22: capire perché $k$ e $\lambda$ si scelgono sul development e il test si usa una volta; leggere `evaluate` riga per riga e l'iterazione di EM (passo E e passo M). Applicare le due correzioni dei riquadri (docstring proprie; componenti che ricadono sull'ordine inferiore) e rivedere come cambiano $\lambda$ e perplexity di test. Provare un'altra divisione dei moduli.

**Ripasso orale** (30 min)

Rispondere ad alta voce alle domande della sezione orale senza guardare la traccia. Punti che cadono spesso: perché $+V$ e non $+1$ al denominatore, che cosa misura lo sconto $d$ e perché è forte per parole rare, perché i $\lambda$ si scelgono su held-out, perché lo stupid backoff non è una distribuzione, entropia come lunghezza minima media di un codice, perché la cross-entropy è un limite superiore, perplexity $= 2^H$.

### Esercizi

#### Esercizio 1 (scheda L05, libro 3.5): il simbolo di fine

Supponiamo di non usare il simbolo di fine </s>. Addestra un modello bigram non smussato su questo corpus di training, senza </s>:

```
<s> a b
<s> b b
<s> b a
<s> a a
```

(a) Calcola tutte le probabilità bigram del modello. (b) Mostra che le probabilità delle quattro possibili frasi di 2 parole sull'alfabeto {a, b} sommano a 1, e che anche le probabilità delle otto possibili frasi di 3 parole sommano a 1. (c) Perché è un problema per un modello linguistico, e come lo risolve </s>?

<details><summary>Soluzione</summary>

(a) Bigram: *<s> a* 2, *<s> b* 2, *a b* 1, *a a* 1, *b b* 1, *b a* 1. Senza </s> l'ultima parola di ogni frase non è seguita da nulla, quindi si normalizza per il numero di bigram che *iniziano* con la parola (la somma della riga): *a* compare 4 volte ma solo 2 volte è seguita da qualcosa. (Dividendo per il conteggio unigram 4 le righe di *a* e *b* sommerebbero a 1/2: altro sintomo del problema.)

$$P(\text{a}\mid\text{&lt;s&gt;}) = P(\text{b}\mid\text{&lt;s&gt;}) = \tfrac12,\quad P(\text{a}\mid\text{a}) = P(\text{b}\mid\text{a}) = P(\text{a}\mid\text{b}) = P(\text{b}\mid\text{b}) = \tfrac12$$

(b) Ogni frase di 2 parole ha probabilità $\frac12\cdot\frac12 = \frac14$: le quattro (aa, ab, ba, bb) sommano a 1. Ogni frase di 3 parole ha $\left(\frac12\right)^3 = \frac18$: le otto sommano a 1. In generale per ogni lunghezza $n$ la somma è $\sum_{w_{1:n}} P(w_1\mid\text{&lt;s&gt;})\prod P(w_i\mid w_{i-1}) = 1$, perché si somma una riga alla volta da destra.

(c) Il modello definisce una distribuzione **separata per ogni lunghezza**, non una sola distribuzione su tutte le frasi: la massa totale è $1+1+1+\dots = \infty$, e una frase di 2 parole non è confrontabile con una di 3. Con </s> la fine diventa un token da predire: nel corpus con </s> si ha $P(\text{&lt;/s&gt;}\mid\text{a}) = P(\text{&lt;/s&gt;}\mid\text{b}) = \frac12$ e $\frac14$ per ciascuna continuazione. Una frase di lunghezza $n$ ha probabilità $\frac12\left(\frac14\right)^{n-1}\frac12$, le $2^n$ frasi di quella lunghezza sommano a $\left(\frac12\right)^n$ e il totale è $\sum_{n\ge1}\left(\frac12\right)^n = 1$: una sola distribuzione su frasi di qualunque lunghezza ([scheda 14 della L4](L04-modelli-linguistici-n-gram.md#p-14)). Verificato in Python con frazioni esatte.

</details>

#### Esercizio 2 (scheda L05): smoothing di Laplace degli unigram

Usa il corpus della lezione:

```
<s> I am Sam </s>
<s> Sam I am </s>
<s> I do not like green eggs and ham </s>
```

Conta $N = 17$ token, le parole e </s> ma non <s>. Supponi che il vocabolario contenga anche la parola *you*, che non compare mai nel corpus, così che $V = 12$ (le dieci parole del corpus, </s> e *you*). (a) Calcola le probabilità a massima verosimiglianza e di Laplace (add-one) di *Sam*, *I* e *you*. (b) Se aggiungessimo uno a ogni conteggio ma tenessimo $N$ come denominatore, a quanto sommerebbero le probabilità delle $V$ parole? (c) Il conteggio aggiustato $c^* = (c+1)N/(N+V)$ è il conteggio che, diviso per $N$, dà la probabilità di Laplace. Calcola $c^*$ per *Sam* e *you*, e lo sconto $d = c^*/c$ per *Sam*.

<details><summary>Soluzione</summary>

Conteggi: I 3, </s> 3, am 2, Sam 2, e una volta do, not, like, green, eggs, and, ham: totale 17.

(a) MLE $c/N$: $P(\text{Sam}) = 2/17 = 0{,}118$, $P(\text{I}) = 3/17 = 0{,}176$, $P(\text{you}) = 0$. Laplace $(c+1)/(N+V)$ con $N+V = 29$: $P(\text{Sam}) = 3/29 = 0{,}103$, $P(\text{I}) = 4/29 = 0{,}138$, $P(\text{you}) = 1/29 = 0{,}034$. Le parole viste perdono un po' di probabilità, *you* ne guadagna.

(b) $\sum_w (c_w+1)/N = (N+V)/N = 29/17 = 1{,}71$: più di 1, non sarebbe una distribuzione. Per questo al denominatore si aggiunge $V$, il numero di «osservazioni in più» ([scheda 10](L05-smoothing-ed-entropia.md#p-10)).

(c) $c^*(\text{Sam}) = 3\cdot17/29 = 51/29 = 1{,}76$; $c^*(\text{you}) = 17/29 = 0{,}59$; $d(\text{Sam}) = 1{,}76/2 = 0{,}88$. Sam cede il 12% del suo conteggio; la somma dei $c^*$ resta 17. Verificato in Python.

</details>

#### Esercizio 3 (scheda L05, libro 3.4): bigram add-one

È dato il corpus seguente, modificato da quello della lezione:

```
<s> I am Sam </s>
<s> Sam I am </s>
<s> I am Sam </s>
<s> I do not like green eggs and Sam </s>
```

(a) Con un modello bigram con smoothing add-one, quanto vale $P(\text{Sam}\mid\text{am})$? Includi <s> e </s> nei conteggi come ogni altro token. (b) Confrontala con la $P(\text{Sam}\mid\text{am})$ non smussata e calcola la $P(\text{I}\mid\text{am})$ add-one.

<details><summary>Soluzione</summary>

Come chiede il testo, <s> e </s> sono token come gli altri. Vocabolario: <s>, </s>, I, am, Sam, do, not, like, green, eggs, and: $V = 11$ (*ham* non c'è più). $C(\text{am}) = 3$ (frasi 1, 2, 3); *am* è seguito da Sam due volte (frasi 1 e 3) e da </s> una volta: $C(\text{am Sam}) = 2$.

(a) $P_\text{Laplace}(\text{Sam}\mid\text{am}) = \dfrac{C(\text{am Sam})+1}{C(\text{am})+V} = \dfrac{2+1}{3+11} = \dfrac{3}{14} = 0{,}214$.

(b) Non smussata: $2/3 = 0{,}667$; add-one la riduce a meno di un terzo, perché $C(\text{am}) = 3$ è piccolo rispetto a $V = 11$. $P_\text{Laplace}(\text{I}\mid\text{am}) = (0+1)/14 = 1/14 = 0{,}071$. Controllo della riga: Sam 3/14, </s> 2/14, gli altri 9 token 1/14 ciascuno, totale 14/14. Con la convenzione del testo anche <s> riceve 1/14 dopo *am*, un evento impossibile: è il prezzo di contare <s> come un token qualsiasi (escludendolo, $V = 10$ e il risultato sarebbe $3/13$). Verificato in Python.

</details>

#### Esercizio 4 (scheda L05, libro 3.2 e 3.3): probabilità smussate e non smussate

Probabilità bigram add-one per otto parole del Berkeley Restaurant Project ($V = 1446$), dal libro (righe: prima parola; colonne: parola successiva):

|  | i | want | to | eat | chinese | food | lunch | spend |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| i | 0.0015 | 0.21 | 0.00025 | 0.0025 | 0.00025 | 0.00025 | 0.00025 | 0.00075 |
| want | 0.0013 | 0.00042 | 0.26 | 0.00084 | 0.0029 | 0.0029 | 0.0025 | 0.00084 |
| to | 0.00078 | 0.00026 | 0.0013 | 0.18 | 0.00078 | 0.00026 | 0.0018 | 0.055 |
| eat | 0.00046 | 0.00046 | 0.0014 | 0.00046 | 0.0078 | 0.0014 | 0.02 | 0.00046 |
| chinese | 0.0012 | 0.00062 | 0.00062 | 0.00062 | 0.00062 | 0.052 | 0.0012 | 0.00062 |
| food | 0.0063 | 0.00039 | 0.0063 | 0.00039 | 0.00079 | 0.002 | 0.00039 | 0.00039 |
| lunch | 0.0017 | 0.00056 | 0.00056 | 0.00056 | 0.00056 | 0.0011 | 0.00056 | 0.00056 |
| spend | 0.0012 | 0.00058 | 0.0012 | 0.00058 | 0.00058 | 0.00058 | 0.00058 | 0.00058 |

Assumi anche le probabilità add-one $P(\text{i}\mid\text{&lt;s&gt;}) = 0{,}19$ e $P(\text{&lt;/s&gt;}\mid\text{food}) = 0{,}40$. Le probabilità non smussate della lezione precedente davano $P(\text{&lt;s&gt; i want chinese food &lt;/s&gt;}) \approx 0{,}00019$ e $P(\text{&lt;s&gt; i want to eat chinese food &lt;/s&gt;}) \approx 0{,}00011$. (a) Calcola $P(\text{&lt;s&gt; i want chinese food &lt;/s&gt;})$ con le probabilità add-one. (b) Quale delle due probabilità di questa frase è più alta, non smussata o smussata? Spiega perché. (c) Calcola la $P(\text{&lt;s&gt; i want to eat chinese food &lt;/s&gt;})$ smussata. Il rapporto con il valore non smussato è più grande o più piccolo che in (a), e perché?

<details><summary>Soluzione</summary>

(a) $0{,}19 \times 0{,}21 \times 0{,}0029 \times 0{,}052 \times 0{,}40 = 2{,}41\times10^{-6}$ (fattori: i|<s>, want|i, chinese|want, food|chinese, </s>|food).

(b) La non smussata, $0{,}25\times0{,}33\times0{,}0065\times0{,}52\times0{,}68 = 1{,}90\times10^{-4}$, è circa **79 volte** più alta. Tutti i bigram della frase sono stati visti, e add-one toglie massa proprio ai bigram visti per darla ai circa 1446 mai visti di ogni riga: $P(\text{food}\mid\text{chinese})$ passa da 0,52 a 0,052, $P(\text{chinese}\mid\text{want})$ da 0,0065 a 0,0029. Per una frase fatta di bigram frequenti lo smoothing può solo abbassare la probabilità; in cambio le frasi con un bigram mai visto non hanno più probabilità 0.

(c) $0{,}19 \times 0{,}21 \times 0{,}26 \times 0{,}18 \times 0{,}0078 \times 0{,}052 \times 0{,}40 = 3{,}03\times10^{-7}$. Non smussata: $0{,}25\times0{,}33\times0{,}66\times0{,}28\times0{,}021\times0{,}52\times0{,}68 = 1{,}13\times10^{-4}$. Rapporto $\approx 374$, **più grande** di 79: la frase ha sette fattori invece di cinque e ognuno è scontato (to|want da 0,66 a 0,26, eat|to da 0,28 a 0,18, chinese|eat da 0,021 a 0,0078); i rapporti dei singoli fattori si moltiplicano, quindi le frasi più lunghe perdono di più.

**Sui dati della scheda**: i due valori dichiarati $\approx 0{,}00019$ e $\approx 0{,}00011$ sono corretti (ricalcolati dalla tabella della [scheda 19 della L4](L04-modelli-linguistici-n-gram.md#p-19)), e la tabella add-one coincide con $(C+1)/(C(w_{n-1})+1446)$ calcolato dai conteggi del libro in tutte le 64 celle. Invece i due valori «da assumere», presi dal libro, non sono coerenti con i conteggi BeRP: con 9332 frasi (quindi $C(\text{&lt;s&gt;}) = 9332$) e $P_\text{MLE}(\text{i}\mid\text{&lt;s&gt;}) = 0{,}25$ si ha $C(\text{&lt;s&gt; i}) \approx 2333$ e add-one $2334/10778 = 0{,}217$, non 0,19; con $C(\text{food}) = 1093$ e $P_\text{MLE}(\text{&lt;/s&gt;}\mid\text{food}) = 0{,}68$, add-one dà $744/2539 = 0{,}293$, e per ottenere 0,40 servirebbe $C(\text{food &lt;/s&gt;}) = 1015$, cioè una MLE di 0,93. Vanno presi come dati dell'esercizio; con i valori coerenti (a) diventerebbe $2{,}01\times10^{-6}$ e le conclusioni non cambiano. Tutti i conti verificati in Python.

</details>

#### Esercizio 5 (scheda L05): conteggi aggiustati e sconti

Nel corpus del Berkeley Restaurant Project $C(\text{want}) = 927$, $C(\text{want to}) = 608$, $C(\text{chinese}) = 158$, $C(\text{chinese food}) = 82$ e $V = 1446$. Con add-one il conteggio aggiustato è $C^*(w_{n-1}w_n) = [C(w_{n-1}w_n)+1]\times C(w_{n-1})/(C(w_{n-1})+V)$ e lo sconto è $d = C^*/C$. (a) Calcola $C^*$ e $d$ per *want to* e per *chinese food*. (b) Calcola il conteggio aggiustato di un bigram mai visto dopo *chinese*, come *chinese to*. (c) Perché *chinese food* è scontato tanto più di *want to*? Che cosa succederebbe con un vocabolario più grande?

<details><summary>Soluzione</summary>

(a) *want to*: $C^* = 609\times927/2373 = 237{,}9$, $d = 237{,}9/608 = 0{,}39$. *chinese food*: $C^* = 83\times158/1604 = 8{,}18$, $d = 8{,}18/82 = 0{,}10$. Sono i valori delle [schede 18](L05-smoothing-ed-entropia.md#p-18) e [19](L05-smoothing-ed-entropia.md#p-19).

(b) $C^*(\text{chinese to}) = 1\times158/1604 = 0{,}099$ (probabilità $1/1604 = 0{,}00062$, la cella grigia della tabella).

(c) $d = \frac{C+1}{C}\cdot\frac{C(w_{n-1})}{C(w_{n-1})+V}$: per conteggi grandi il primo fattore è circa 1 e conta il secondo, $927/2373 = 0{,}39$ contro $158/1604 = 0{,}099$. *chinese* è raro e il $+V$ al denominatore schiaccia la sua riga: delle $158+1446$ «osservazioni» della riga, 1446 sono finte e vanno ai bigram mai visti (circa il 90% della massa). Con un vocabolario più grande lo sconto cresce ancora: con $V = 10.000$, $d(\text{chinese food}) = 0{,}016$ e $d(\text{want to}) = 0{,}085$. È il motivo per cui add-one non funziona per i modelli linguistici. Verificato in Python (stessi numeri della cella 10 del notebook).

</details>

#### Esercizio 6 (scheda L05, libro 3.6): trigram add-one e add-k

(a) Supponi di addestrare un modello trigram con smoothing add-one su un corpus con $V$ tipi di parola. Scrivi una formula per $P(w_3\mid w_1,w_2)$, dove $w_3$ segue il bigram $(w_1,w_2)$, in funzione dei conteggi $c(w_1,w_2,w_3)$, $c(w_1,w_2)$ e di $V$. (b) Sul corpus della lezione (esercizio 2), con $V = 11$ possibili token successivi, calcola le probabilità add-one $P(\text{Sam}\mid\text{I am})$ e $P(\text{do}\mid\text{I am})$. (c) Calcola le stesse due probabilità con add-k e $k = 0{,}1$. A che cosa tendono per $k \to 0$ e per $k$ molto grande?

<details><summary>Soluzione</summary>

(a) $$P_\text{Laplace}(w_3\mid w_1,w_2) = \frac{c(w_1,w_2,w_3)+1}{c(w_1,w_2)+V}$$ Il denominatore è la somma della riga, $\sum_w [c(w_1,w_2,w)+1] = c(w_1,w_2) + V$; coincide con $c(w_1,w_2)$ perché, grazie a </s>, ogni occorrenza del bigram è seguita da un token (altrimenti si userebbe $\sum_w c(w_1,w_2,w)$). Con add-k: $(c(w_1,w_2,w_3)+k)/(c(w_1,w_2)+kV)$.

(b) *I am* compare 2 volte (frasi 1 e 2), seguito da Sam e da </s>: $c(\text{I am Sam}) = 1$, $c(\text{I am do}) = 0$. $P(\text{Sam}\mid\text{I am}) = 2/13 = 0{,}154$, $P(\text{do}\mid\text{I am}) = 1/13 = 0{,}077$.

(c) $k = 0{,}1$: $P(\text{Sam}\mid\text{I am}) = 1{,}1/3{,}1 = 11/31 = 0{,}355$, $P(\text{do}\mid\text{I am}) = 0{,}1/3{,}1 = 1/31 = 0{,}032$. Per $k \to 0$ si torna alla MLE: $1/2$ e $0$. Per $k \to \infty$ i conteggi diventano trascurabili e tutti gli 11 token tendono a $1/V = 1/11 = 0{,}091$. Sono gli stessi numeri della riga di *am* nella [scheda 21](L05-smoothing-ed-entropia.md#p-21): nel corpus *am* è sempre preceduto da *I*, quindi il contesto trigram *I am* ha esattamente i conteggi del contesto bigram *am*. Verificato in Python (cella 8 del notebook).

</details>

#### Esercizio 7 (scheda L05, libro 3.7): interpolazione lineare

Usa il corpus modificato dell'esercizio 3:

```
<s> I am Sam </s>
<s> Sam I am </s>
<s> I am Sam </s>
<s> I do not like green eggs and Sam </s>
```

(a) Se usiamo l'interpolazione lineare tra un modello bigram a massima verosimiglianza e un modello unigram a massima verosimiglianza con $\lambda_1 = \lambda_2 = 1/2$, quanto vale $P(\text{Sam}\mid\text{am})$? Includi <s> e </s> nei conteggi come ogni altro token. (b) Calcola la $P(\text{I}\mid\text{am})$ interpolata. Perché non è zero? (c) Spiega perché le probabilità interpolate di tutti i token dopo *am* sommano a 1.

<details><summary>Soluzione</summary>

Contando <s> e </s> come token: $N = 5+5+5+10 = 25$; $C(\text{Sam}) = 4$, $C(\text{I}) = 4$, $C(\text{&lt;s&gt;}) = C(\text{&lt;/s&gt;}) = 4$, $C(\text{am}) = 3$, e 1 per do, not, like, green, eggs, and. Bigram: $C(\text{am Sam}) = 2$, $C(\text{am &lt;/s&gt;}) = 1$.

(a) $$P(\text{Sam}\mid\text{am}) = \tfrac12\cdot\tfrac{2}{3} + \tfrac12\cdot\tfrac{4}{25} = \tfrac13 + \tfrac{2}{25} = \tfrac{31}{75} = 0{,}413$$

(b) $P(\text{I}\mid\text{am}) = \frac12\cdot0 + \frac12\cdot\frac{4}{25} = \frac{2}{25} = 0{,}08$. Il bigram *am I* non è mai stato visto, ma il termine unigram è positivo perché *I* è frequente: la miscela ricade sul contesto più corto ([scheda 26](L05-smoothing-ed-entropia.md#p-26)).

(c) Entrambi i componenti sono distribuzioni sullo stesso vocabolario: $\sum_w P_\text{MLE}(w\mid\text{am}) = 1$ e $\sum_w P_\text{MLE}(w) = 1$, quindi $\sum_w \hat P(w\mid\text{am}) = \lambda_1\cdot1 + \lambda_2\cdot1 = 1$ perché i pesi sommano a 1. Una precisazione dovuta alla convenzione del testo: poiché <s> è contato fra gli unigram, $P(\text{&lt;s&gt;}) = 4/25$ e la miscela dà $2/25$ all'evento impossibile «<s> dopo am»; sui 10 token che possono davvero seguire si somma a $23/25$. Con la convenzione della lezione (unigram su $N = 17$ senza <s>, scheda 26) il problema non c'è. Verificato in Python con frazioni esatte.

</details>

#### Esercizio 8 (scheda L05): scegliere λ su dati held-out

Addestra sul corpus della lezione (esercizio 2) un modello bigram interpolato $P(w_n\mid w_{n-1}) = \lambda P_\text{MLE}(w_n\mid w_{n-1}) + (1-\lambda)P_\text{MLE}(w_n)$, con conteggi unigram su $N = 17$ token (le parole e </s>). L'insieme held-out è la frase <s> I like green eggs and ham </s>. (a) Calcola la probabilità della frase held-out per $\lambda = 0{,}5$ e per $\lambda = 0{,}9$. (b) Quale dei due valori sceglieremmo? Che cosa succede con $\lambda = 1$? (c) Calcola la perplexity della frase held-out per entrambi i valori ($N = 7$ token).

<details><summary>Soluzione</summary>

Fattori: bigram MLE $P(\text{I}\mid\text{&lt;s&gt;}) = 2/3$, $P(\text{like}\mid\text{I}) = 0$, poi cinque bigram con probabilità 1 (like green, green eggs, eggs and, and ham, ham </s>). Unigram: I $3/17$, like, green, eggs, and, ham $1/17$, </s> $3/17$.

(a) $\lambda = 0{,}5$: $\frac{43}{102}\cdot\frac{1}{34}\cdot\left(\frac{9}{17}\right)^4\cdot\frac{10}{17}$ ($0{,}4216\cdot0{,}0294\cdot0{,}5294^4\cdot0{,}5882$) $= 5{,}73\times10^{-4}$. $\lambda = 0{,}9$: $\frac{21}{34}\cdot\frac{1}{170}\cdot\left(\frac{77}{85}\right)^4\cdot\frac{78}{85}$ ($0{,}6176\cdot0{,}0059\cdot0{,}9059^4\cdot0{,}9176$) $= 2{,}25\times10^{-3}$.

(b) $\lambda = 0{,}9$, che dà all'held-out probabilità circa 4 volte più alta: i $\lambda$ si scelgono massimizzando la verosimiglianza dei dati held-out ([scheda 25](L05-smoothing-ed-entropia.md#p-25)). Con $\lambda = 1$ resta il bigram MLE, $P(\text{like}\mid\text{I}) = 0$, la frase ha probabilità 0 e perplexity infinita: un po' di peso all'unigram serve proprio per i bigram mai visti. L'ottimo è intermedio, $\lambda \approx 0{,}84$ (probabilità $2{,}50\times10^{-3}$), trovato con una griglia fine e con EM (esercizio aggiuntivo B).

(c) $PP = P^{-1/7}$: $\lambda = 0{,}5$: $(5{,}73\times10^{-4})^{-1/7} = 2{,}90$; $\lambda = 0{,}9$: $(2{,}25\times10^{-3})^{-1/7} = 2{,}39$. Verificato in Python con frazioni esatte.

</details>

#### Esercizio 9 (scheda L05): stupid backoff

Usa un modello trigram con stupid backoff, $\lambda = 0{,}4$, sul corpus della lezione (esercizio 2); lo score unigram è $\text{count}(w)/N$ con $N = 17$. (a) Calcola $S(\text{Sam}\mid\text{I am})$, $S(\text{&lt;/s&gt;}\mid\text{I am})$, $S(\text{I}\mid\text{I am})$ e $S(\text{do}\mid\text{I am})$. (b) Calcola la somma di $S(w\mid\text{I am})$ sugli 11 possibili token successivi. Che cosa mostra? (c) Che cosa dovrebbe fare un modello di backoff per dare una vera distribuzione di probabilità?

<details><summary>Soluzione</summary>

Il contesto *I am* compare 2 volte, seguito da Sam e da </s>; il bigram *am* è seguito solo da Sam e </s>.

(a) $S(\text{Sam}\mid\text{I am}) = C(\text{I am Sam})/C(\text{I am}) = 1/2$; $S(\text{&lt;/s&gt;}\mid\text{I am}) = 1/2$. Per *I*: trigram *I am I* assente, bigram *am I* assente, si scende all'unigram: $S = 0{,}4\cdot0{,}4\cdot3/17 = 0{,}48/17 = 12/425 = 0{,}028$. Per *do*: stesso percorso, $S = 0{,}16\cdot1/17 = 4/425 = 0{,}0094$.

(b) Sam e </s> danno 1; gli altri nove token (I 3, am 2, e 1 ciascuno do, not, like, green, eggs, and, ham: conteggio totale 12) danno $0{,}16\cdot12/17$. Somma $1 + 1{,}92/17 = 473/425 = 1{,}113 &gt; 1$: lo stupid backoff produce **score, non probabilità**. La massa dei trigram visti non è scontata (sommano già a 1) e quella data ai livelli bassi si aggiunge sopra ([scheda 27](L05-smoothing-ed-entropia.md#p-27); per il contesto *Sam I* della [scheda 28](L05-smoothing-ed-entropia.md#p-28) la somma è 1,265).

(c) **Scontare** gli n-gram di ordine alto (per esempio togliere una quantità fissa a ogni conteggio visto, o usare Good-Turing) per risparmiare massa, e distribuire esattamente quella massa sull'ordine inferiore con un peso $\alpha(\text{contesto})$ dipendente dal contesto e normalizzato sulle sole parole mai viste in quel contesto (backoff di Katz). In alternativa si usa l'interpolazione, che è una distribuzione per costruzione. Verificato in Python con un'implementazione indipendente e con la funzione `stupid_backoff` del notebook.

</details>

#### Esercizio 10 (scheda L05): entropia e codici

(a) Quattro cavalli vincono con probabilità 1/2, 1/4, 1/8 e 1/8. Calcola l'entropia del vincitore, trova un codice binario la cui lunghezza media sia uguale all'entropia e confrontalo con il codice a lunghezza fissa di 2 bit. (b) Qual è l'entropia se i quattro cavalli sono equiprobabili? E se vince sempre lo stesso cavallo? (c) Qual è l'entropia di un dado equo? Trova un codice binario per un singolo lancio e la sua lunghezza media. Può raggiungere l'entropia?

<details><summary>Soluzione</summary>

(a) $H = \frac12\cdot1 + \frac14\cdot2 + 2\cdot\frac18\cdot3 = 1{,}75$ bit. Codice 0, 10, 110, 111 (prefix-free: nessuna parola è prefisso di un'altra, quindi si decodifica senza separatori): lunghezza media $\frac12\cdot1+\frac14\cdot2+\frac18\cdot3+\frac18\cdot3 = 1{,}75$. Uguale all'entropia perché le probabilità sono potenze di 1/2 e ogni lunghezza vale $-\log_2 p$. Il codice fisso costa 2 bit: si risparmia 0,25 bit per corsa.

(b) Equiprobabili: $H = \log_2 4 = 2$ bit, il massimo per quattro esiti, e il codice fisso è già ottimo (come gli 8 cavalli della [scheda 35](L05-smoothing-ed-entropia.md#p-35)). Se vince sempre lo stesso: $H = -1\cdot\log_2 1 = 0$ bit, nessuna incertezza, non serve mandare nulla.

(c) $H = \log_2 6 = 2{,}585$ bit. Codice 00, 01, 100, 101, 110, 111 (prefix-free, è quello di Huffman): lunghezza media $(2\cdot2+4\cdot3)/6 = 8/3 = 2{,}667$ bit. Un codice per un singolo lancio non può raggiungere l'entropia: le lunghezze sono intere, e $-\log_2(1/6) = 2{,}585$ non lo è. Ci si avvicina codificando blocchi: 5 lanci hanno $6^5 = 7776 \le 2^{13} = 8192$ esiti, quindi 13 bit per 5 lanci, 2,6 bit a lancio; con blocchi sempre più lunghi si tende a 2,585 (teorema della codifica di sorgente). Verificato in Python (cella 26 del notebook).

</details>

#### Esercizio 11 (scheda L05): cross-entropy e perplexity

I colori sono generati indipendentemente da una distribuzione vera $p$: $P(\text{red}) = 0{,}5$, $P(\text{blue}) = 0{,}25$, $P(\text{green}) = 0{,}25$. Il modello A dà 1/3 a ogni colore; il modello B dà $P(\text{red}) = 0{,}8$, $P(\text{blue}) = 0{,}1$, $P(\text{green}) = 0{,}1$. Per colori indipendenti la cross-entropy per parola di un modello $m$ è $H(p,m) = -\sum_x p(x)\log_2 m(x)$. (a) Calcola l'entropia $H(p)$. (b) Calcola $H(p,A)$ e $H(p,B)$. Verifica che entrambe siano almeno $H(p)$. Quale modello è migliore? (c) Calcola le perplexity $2^H$ di $p$, A e B. (d) Il modello trigram del Wall Street Journal ha perplexity 109. Quanti bit per parola sono? Qual è la perplexity di un modello con cross-entropy di 7 bit per parola?

<details><summary>Soluzione</summary>

(a) $H(p) = 0{,}5\cdot1 + 0{,}25\cdot2 + 0{,}25\cdot2 = 1{,}5$ bit.

(b) $H(p,A) = -\log_2\frac13 = \log_2 3 = 1{,}585$ bit. $H(p,B) = -(0{,}5\log_2 0{,}8 + 0{,}25\log_2 0{,}1 + 0{,}25\log_2 0{,}1) = 0{,}5\cdot0{,}322 + 0{,}5\cdot3{,}322 = 1{,}822$ bit. Entrambe $\ge 1{,}5$ (eq. 3.41). **A è migliore** (cross-entropy più bassa): B è troppo sicuro del rosso e paga 3,32 bit su metà dei colori.

(c) $2^{1{,}5} = 2{,}83$; $2^{1{,}585} = 3$; $2^{1{,}822} = 3{,}54$. Il modello vero ha la perplexity minima: in media è incerto come una scelta uniforme fra 2,83 colori.

(d) $\log_2 109 = 6{,}77$ bit per parola (la [scheda 40](L05-smoothing-ed-entropia.md#p-40) arrotonda a 6,8). Cross-entropy di 7 bit: perplexity $2^7 = 128$. Nota: sulla sequenza *red red red red blue* della [scheda 40](L05-smoothing-ed-entropia.md#p-40) vinceva B (0,92 bit): quella sequenza non è un campione tipico di $p$. Verificato in Python (cella 28 del notebook).

</details>

#### Esercizio 12 (scheda L05): perché i modelli linguistici neurali

(a) Con un vocabolario di $V = 50.000$ token, quanti bigram, trigram e 5-gram possibili ci sono? (b) Un corpus ha mille miliardi ($10^{12}$) di token. Al massimo quanti 5-gram distinti può contenere, e che frazione dei 5-gram possibili è? (c) Un corpus di training contiene molte volte *the cat sat on the mat*, e *dog* in altri contesti, ma mai *dog sat*. Che cosa sa un modello trigram interpolato di $P(\text{sat}\mid\text{the dog})$? Che cosa gli sfugge?

<details><summary>Soluzione</summary>

(a) $V^2 = 2{,}5\times10^9$ bigram, $V^3 = 1{,}25\times10^{14}$ trigram, $V^5 = 3{,}125\times10^{23}$ 5-gram: i parametri crescono esponenzialmente con l'ordine ([scheda 42](L05-smoothing-ed-entropia.md#p-42)).

(b) Al massimo un 5-gram distinto per posizione, quindi circa $10^{12}$ (un po' meno, 4 posizioni in meno per ogni documento, e in pratica molti meno perché i 5-gram si ripetono). Frazione $\le 10^{12}/3{,}125\times10^{23} = 3{,}2\times10^{-12}$: anche un corpus enorme vede una parte infinitesima dei 5-gram possibili, e quasi tutti i 5-gram di un test sono mai visti o visti poche volte.

(c) $\hat P(\text{sat}\mid\text{the dog}) = \lambda_3\cdot0 + \lambda_2\cdot0 + \lambda_1 P(\text{sat})$: trigram e bigram non sono mai stati visti, resta solo la frequenza unigram di *sat*, la stessa che darebbe dopo qualunque contesto mai visto. Il modello non sa che *dog* e *cat* sono simili (entrambi animali, soggetti di verbi come *sat*, *ate*, *ran*): le parole sono simboli atomici e ciò che impara su *cat* non dice nulla su *dog*. Un modello neurale rappresenta le parole come vettori (embedding) in uno spazio continuo, dove parole con contesti simili sono vicine, e quindi generalizza da *the cat sat* a *the dog sat*.

</details>

#### Esercizio aggiuntivo A: la frase di test con add-one

È l'esercizio proposto nella [scheda 20](L05-smoothing-ed-entropia.md#p-20). Sul corpus *I am Sam* con add-one e $V = 11$, calcola la probabilità della frase <s> I like green eggs and ham </s> e la sua perplexity su $N = 7$ token. Confronta i fattori dei bigram visti con le loro probabilità MLE.

<details><summary>Soluzione</summary>

Conteggi dei contesti: $C(\text{&lt;s&gt;}) = 3$, $C(\text{I}) = 3$, e 1 per like, green, eggs, and, ham. Fattori $(C+1)/(C(w_{n-1})+11)$:

- $P(\text{I}\mid\text{&lt;s&gt;}) = (2+1)/(3+11) = 3/14$ (MLE 2/3)
- $P(\text{like}\mid\text{I}) = (0+1)/(3+11) = 1/14$ (MLE 0)
- like green, green eggs, eggs and, and ham, ham </s>: $(1+1)/(1+11) = 1/6$ ciascuno (MLE 1)

$P = \frac{3}{14}\cdot\frac{1}{14}\cdot\left(\frac16\right)^5 = \frac{3}{196\cdot7776} = \frac{1}{508032} = 1{,}97\times10^{-6}$; perplexity $P^{-1/7} = 508032^{1/7} = 6{,}53$, i valori della slide. I cinque bigram che con MLE erano certi scendono a 1/6: per contesti visti una volta, il $+11$ al denominatore domina. Verificato in Python e con la cella 6 del notebook.

</details>

#### Esercizio aggiuntivo B: un'iterazione di EM a mano

Riprendi l'esercizio 8 (bigram MLE e unigram MLE interpolati, held-out *<s> I like green eggs and ham </s>*). Partendo da $\lambda = 0{,}5$, esegui un'iterazione di EM: per ogni token calcola la quota del bigram $r_i = \lambda p_\text{bi}/(\lambda p_\text{bi} + (1-\lambda)p_\text{uni})$, poi il nuovo $\lambda$ come media delle quote. Verso che valore converge?

<details><summary>Soluzione</summary>

Quote del bigram con $\lambda = 0{,}5$ (il fattore 0,5 si semplifica): I|<s>: $\frac{2/3}{2/3+3/17} = \frac{34}{43} = 0{,}791$; like|I: $0$ (bigram nullo, tutta la quota all'unigram); like green, green eggs, eggs and, and ham: $\frac{1}{1+1/17} = \frac{17}{18} = 0{,}944$ ciascuno; ham </s>: $\frac{1}{1+3/17} = \frac{17}{20} = 0{,}85$.

Nuovo $\lambda = (0{,}791 + 0 + 4\cdot0{,}944 + 0{,}85)/7 = 0{,}774$. La probabilità dell'held-out sale da $5{,}73\times10^{-4}$ a $2{,}31\times10^{-3}$. Iterando: 0,830, 0,838, ... converge a $\lambda = 0{,}839$, con probabilità $2{,}502\times10^{-3}$: lo stesso ottimo trovato con una griglia fine. Il token *like|I*, con quota 0, impedisce a $\lambda$ di arrivare a 1. È ciò che fa la cella 20 del notebook con tre componenti. Verificato in Python.

</details>

#### Esercizio aggiuntivo C: entropy rate di una catena di Markov

Una sorgente emette colori secondo una catena di Markov: $P(\text{red}\mid\text{red}) = 0{,}9$, $P(\text{blue}\mid\text{red}) = 0{,}1$, $P(\text{red}\mid\text{blue}) = P(\text{blue}\mid\text{blue}) = 0{,}5$. (a) Trova la distribuzione stazionaria $\pi$. (b) Calcola l'entropy rate $\sum_a \pi_a H(\cdot\mid a)$. (c) Calcola la cross-entropy, su una sequenza lunga della catena, di un modello unigram con probabilità $\pi$ e di un modello uniforme, e le tre perplexity.

<details><summary>Soluzione</summary>

(a) Stazionarietà: $\pi_r = 0{,}9\pi_r + 0{,}5\pi_b$, cioè $0{,}1\pi_r = 0{,}5\pi_b$; con $\pi_r+\pi_b = 1$: $\pi_r = 5/6$, $\pi_b = 1/6$.

(b) $H(\cdot\mid\text{red}) = H(0{,}9;\,0{,}1) = 0{,}469$ bit, $H(\cdot\mid\text{blue}) = 1$ bit. Entropy rate $= \frac56\cdot0{,}469 + \frac16\cdot1 = 0{,}557$ bit per colore.

(c) Unigram con $\pi$: per Shannon-McMillan-Breiman la stima su una sequenza lunga converge a $H(\pi) = H(5/6;\,1/6) = 0{,}650$ bit; uniforme: 1 bit. Tutte e due sopra l'entropy rate, come vuole $H(p) \le H(p,m)$. Perplexity: $2^{0{,}557} = 1{,}47$ (la catena stessa), $2^{0{,}650} = 1{,}57$, $2^1 = 2$. Il guadagno $0{,}650 - 0{,}557 = 0{,}093$ bit è l'informazione portata dal colore precedente. È la versione a due stati delle celle 30-31 del notebook. Verificato in Python.

</details>

### Domande tipo orale

<details><summary>Che cos'è il problema degli zeri e perché va risolto?</summary>

Traccia: (1) **zeri**: n-gram mai visti nel training ma presenti nel test (*ruby slippers*); con BPE i token non sono mai sconosciuti, le sequenze sì; (2) due danni: si sottostima la probabilità di sequenze possibili, e un solo zero rende 0 la probabilità del test set, quindi la perplexity (inversa) è indefinita; (3) esempio: *I like* nel corpus I am Sam, $P(\text{like}\mid\text{I}) = 0/3$; (4) soluzione: **smoothing** o discounting, togliere un po' di massa agli eventi frequenti per darla a quelli mai visti (*denied the*: 7 conteggi, 2 spostati sulle altre parole); (5) algoritmi: Laplace, add-k, interpolazione, stupid backoff.

</details>

<details><summary>Che cosa sono vocabolario aperto e chiuso? Come si gestiscono le parole sconosciute?</summary>

Traccia: (1) vocabolario chiuso: tutte le parole note in anticipo, $V$ fisso; aperto: nel test compaiono parole **OOV**; (2) <UNK>: si fissa $V$ (per esempio parole viste almeno due volte), le altre parole del training diventano <UNK> e se ne stimano le probabilità come per ogni altra parola; (3) al test ogni parola fuori da $V$ diventa <UNK>: *I like green tomatoes* → *I like green <UNK>*; (4) con tokenizzazione subword (BPE) il vocabolario è l'insieme dei token e ogni parola è una sequenza di token noti fino alle lettere: nessun token sconosciuto; (5) restano gli n-gram mai visti, quindi lo smoothing serve comunque; (6) la perplexity dipende dalla scelta di $V$ e di <UNK>.

</details>

<details><summary>Descrivi lo smoothing di Laplace per unigram e bigram. Perché si aggiunge V al denominatore?</summary>

Traccia: (1) MLE unigram $c_i/N$; Laplace $(c_i+1)/(N+V)$; (2) ogni conteggio aumenta di 1 e ci sono $V$ parole: $V$ osservazioni in più, altrimenti la somma sarebbe $(N+V)/N &gt; 1$; (3) bigram: $(C(w_{n-1}w_n)+1)/(C(w_{n-1})+V)$, perché il denominatore è la somma della riga, sui $V$ bigram che iniziano con $w_{n-1}$; (4) BeRP: $P(\text{to}\mid\text{want}) = 609/2373 = 0{,}26$ contro 0,66; (5) I am Sam: riga di *am* 2/13 per i visti, 1/13 per i nove mai visti; (6) usi: baseline, introduce i concetti degli altri metodi, buono per la classificazione di testi, non per i modelli linguistici moderni.

</details>

<details><summary>Che cosa sono i conteggi aggiustati e lo sconto? Che cosa mostrano su add-one?</summary>

Traccia: (1) $C^* = (C+1)\,C(w_{n-1})/(C(w_{n-1})+V)$: il conteggio che, diviso per il denominatore non smussato, dà la probabilità di Laplace; confrontabile con i conteggi originali; (2) **sconto** $d = C^*/C$; (3) BeRP: *want to* 608 → 238, $d = 0{,}39$; *chinese food* 82 → 8,2, $d = 0{,}10$, un fattore 10; (4) il motivo: il fattore $C(w_{n-1})/(C(w_{n-1})+V)$, piccolo per parole rare rispetto a $V = 1446$: troppa massa va agli zeri; (5) con $V$ più grande peggiora; (6) conclusione: add-one cambia troppo i conteggi, i bigram visti perdono gran parte della probabilità.

</details>

<details><summary>Che cos'è add-k? Come si sceglie k e quali sono i limiti?</summary>

Traccia: (1) $(C(w_{n-1}w_n)+k)/(C(w_{n-1})+kV)$ con $k$ frazionario (0,5; 0,01); (2) $k = 1$ è Laplace, $k = 0$ la MLE, $k \to \infty$ la distribuzione uniforme $1/V$; (3) meno massa spostata dagli eventi visti a quelli mai visti; I am Sam: $P(\text{Sam}\mid\text{am})$ da 0,15 ($k = 1$) a 0,48 ($k = 0{,}01$); (4) $k$ è un iperparametro: si sceglie ottimizzando su un devset, mai sul test; (5) nel notebook il minimo del bigram è a $k = 0{,}02$; (6) limite: per il language modeling funziona ancora male, sconti inappropriati e varianze scarse (Gale e Church 1994); utile per la classificazione.

</details>

<details><summary>Che cos'è l'interpolazione lineare? Perché il risultato è ancora una distribuzione di probabilità?</summary>

Traccia: (1) idea: usare meno contesto quando il contesto lungo non ha conteggi; (2) $\hat P(w_n\mid w_{n-2}w_{n-1}) = \lambda_1 P(w_n) + \lambda_2 P(w_n\mid w_{n-1}) + \lambda_3 P(w_n\mid w_{n-2}w_{n-1})$; (3) $\sum\lambda_i = 1$, $\lambda_i \ge 0$: media pesata di distribuzioni, quindi somma $\sum_i \lambda_i\cdot1 = 1$ (purché ogni componente sia una distribuzione in quel contesto); (4) un trigram mai visto non dà più zero: bigram e unigram riempiono; (5) esempio I am Sam con $\lambda = 1/2$: *am Sam* $21/68 = 0{,}31$, *am I* $3/34$, *I like* $1/34$; (6) rispetto ad add-one i bigram visti conservano più probabilità e gli zeri ricevono una quota proporzionale alla frequenza della parola.

</details>

<details><summary>Come si scelgono i pesi λ dell'interpolazione?</summary>

Traccia: (1) su un **held-out corpus**, tenuto fuori dal training: si fissano le probabilità n-gram del training e si cercano i $\lambda$ che massimizzano la probabilità dell'held-out; (2) sul training si sceglierebbe sempre l'ordine più alto (overfitting); (3) metodi: ricerca a griglia o **EM** (Jelinek e Mercer 1980), iterativo, converge a valori localmente ottimi; passo E: quota di ogni componente per ogni token; passo M: media delle quote; (4) versione raffinata: $\lambda$ funzione del contesto $w_{n-2:n-1}$, più peso al trigram se i conteggi del bigram sono affidabili; (5) i $\lambda$ sono **iperparametri**, come $k$; (6) il test set si usa una volta alla fine.

</details>

<details><summary>Differenza tra interpolazione e backoff. Che cos'è lo stupid backoff e perché non è una distribuzione?</summary>

Traccia: (1) interpolazione: mescola sempre tutti gli ordini; backoff: usa l'ordine più alto con conteggi, altrimenti scende; (2) un backoff corretto deve **scontare** gli ordini alti per lasciare massa a quelli bassi (Katz); (3) **stupid backoff** (Brants et al. 2007): nessuno sconto, frequenza relativa se l'n-gram c'è, altrimenti $\lambda\,S(w\mid\text{contesto più corto})$ con $\lambda = 0{,}4$ fisso, fino a $S(w) = \text{count}(w)/N$; (4) esempio *Sam I*: am 1, do 0,13, Sam 0,019; somma 1,27 > 1; (5) è uno **score**: va bene per scegliere tra candidati su corpora enormi, non per la perplexity.

</details>

<details><summary>Che cos'è l'entropia? Spiega l'esempio della corsa di cavalli.</summary>

Traccia: (1) $H(X) = -\sum_{x\in\chi} p(x)\log_2 p(x)$, misura di informazione; in base 2 si misura in bit; (2) limite inferiore della lunghezza media di un codice ottimo per comunicare l'esito; (3) 8 cavalli con codice binario del numero: 3 bit per corsa; (4) con probabilità 1/2, 1/4, 1/8, 1/16 e 4 volte 1/64: $H = 2$ bit, raggiunti da un codice a lunghezza variabile (0, 10, 110, 1110, 111100, ...) con parole corte per i cavalli probabili; (5) equiprobabili: $H = 3$ bit, il codice fisso è già ottimo; (6) l'entropia è massima per la distribuzione uniforme ($\log_2|\chi|$) e 0 se l'esito è certo.

</details>

<details><summary>Come si definisce l'entropia di una sequenza e di un linguaggio?</summary>

Traccia: (1) variabile che varia su tutte le sequenze di $n$ parole: $H(w_{1:n}) = -\sum p(w_{1:n})\log p(w_{1:n})$; (2) **entropy rate** (entropia per parola): $\frac1n H(w_{1:n})$; (3) un linguaggio come processo stocastico $L$: $H(L) = \lim_{n\to\infty}\frac1n H(w_{1:n})$, servono sequenze infinite; (4) per una catena di Markov l'entropy rate è $\sum_a \pi_a H(\cdot\mid a)$ (notebook: 1,129 bit per colore); (5) non si può sommare su tutte le sequenze: per questo serve il teorema di Shannon-McMillan-Breiman.

</details>

<details><summary>Che cosa dice il teorema di Shannon-McMillan-Breiman? Che cosa vuol dire stazionario, e la lingua lo è?</summary>

Traccia: (1) se il processo è **stazionario ed ergodico**, $H(L) = \lim_{n\to\infty} -\frac1n\log p(w_{1:n})$: basta una sola sequenza abbastanza lunga invece della somma su tutte; (2) intuizione: una sequenza lunga contiene molte sequenze più corte, ognuna ripetuta secondo la sua probabilità; (3) stazionario: le probabilità sono invarianti per traslazione nel tempo; i modelli di Markov, e quindi gli n-gram, lo sono; (4) la lingua naturale no: le parole future possono dipendere da eventi arbitrariamente lontani e dal tempo; (5) quindi i modelli danno solo un'approssimazione, ma in pratica si stima l'entropia dalla log probabilità media di un campione molto lungo; (6) vale anche per la cross-entropy.

</details>

<details><summary>Che cos'è la cross-entropy e perché è un limite superiore dell'entropia?</summary>

Traccia: (1) non conosciamo la distribuzione vera $p$; $m$ è un modello di $p$; (2) $H(p,m) = \lim -\frac1n\sum p(w_{1:n})\log m(w_{1:n})$: sequenze estratte secondo $p$, log probabilità secondo $m$; per un processo stazionario ergodico basta una sequenza lunga, $-\frac1n\log m(w_{1:n})$; (3) $H(p) \le H(p,m)$ per ogni $m$, uguaglianza solo se $m = p$ (disuguaglianza di Gibbs); (4) quindi un modello non può sbagliare sottostimando l'entropia vera; (5) di due modelli il più accurato ha cross-entropy più bassa; (6) esempio colori: $H(p) = 1{,}5$, uniforme 1,585, B 1,822 bit.

</details>

<details><summary>Che relazione c'è fra perplexity e cross-entropy?</summary>

Traccia: (1) la cross-entropy è un limite; la si approssima su una sequenza abbastanza lunga di lunghezza fissa $N$: $H(W) = -\frac1N\log_2 P(w_1\dots w_N)$; (2) perplexity $= 2^{H(W)} = P(w_1\dots w_N)^{-1/N}$, l'inversa della probabilità del test set normalizzata per la lunghezza: spiega la definizione della L4; (3) una cross-entropy di $H$ bit per parola equivale all'incertezza di una scelta uniforme fra $2^H$ parole; (4) colori: A 1,58 bit, perplexity 3; B 0,92 bit, 1,89; (5) WSJ: 962, 170, 109 sono 9,9, 7,4, 6,8 bit per parola; (6) meno cross-entropy, meno perplexity, modello migliore; un bit in meno dimezza la perplexity.

</details>

<details><summary>Che cosa degli n-gram si ritrova nei large language model?</summary>

Traccia: (1) stesso compito, **next-token prediction**, ma probabilità da una rete neurale invece che da conteggi; (2) stessa disciplina sperimentale: training, tuning su held-out, test una volta; con dati dal web la **data contamination** è un rischio reale; (3) la cross-entropy è la loss minimizzata nel training; la perplexity resta la metrica, confrontabile solo a parità di tokenizzatore; (4) la generazione è campionamento del token successivo; (5) gli n-gram oggi: infini-gram (conteggi di n-gram di qualunque lunghezza su trilioni di token), KenLM, add-one per la classificazione.

</details>

<details><summary>Quali sono i due limiti fondamentali degli n-gram che i modelli neurali superano?</summary>

Traccia: (1) **troppi parametri**: il numero di n-gram possibili cresce come $V^n$; Shakespeare ha $V^2 \approx 844$ milioni di bigram possibili; con $V = 50.000$ i 5-gram sono $3\times10^{23}$, nessun corpus li copre; (2) **nessuna generalizzazione**: un n-gram non sa nulla di un contesto che non usa parole identiche; ciò che impara su *cat* non vale per *dog*; smoothing e interpolazione ricadono solo su contesti più corti; (3) i modelli neurali proiettano le parole in uno spazio continuo dove parole con contesti simili hanno rappresentazioni simili; (4) feedforward, ricorrenti e transformer costruiscono su questa idea (capitoli 6, 7, 14).

</details>

<details><summary>Come si confrontano onestamente diversi metodi di smoothing su un corpus reale?</summary>

Traccia: (1) tre insiemi disgiunti, divisi per documento: training per i conteggi, development per gli iperparametri ($k$, $\lambda$), test usato una volta; (2) stesso vocabolario e stesso conteggio di $N$ (</s> sì, <s> no) per tutti i modelli; (3) controllare che test e development non contengano testo del training (contaminazione): nel notebook le docstring ereditate mettevano 21 frasi del training nel test, e correggendo il bigram add-k smette di battere l'unigram; (4) il modello interpolato deve essere una distribuzione in ogni contesto; (5) risultati tipici: add-k con $k$ piccolo meglio di add-one, interpolazione molto meglio di add-k (nel notebook 288 contro 490 di perplexity).

</details>
