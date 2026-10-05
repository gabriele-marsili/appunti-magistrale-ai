# Ripasso esame · Human Language Technologies

[Indice della dispensa](README.md) · [Versione interattiva](https://gabriele-marsili.github.io/appunti-magistrale-ai/anno-2/hlt/sito/#ripasso)

## Formulario

### Modelli linguistici

**Normalizzazione della distribuzione sul token successivo** ([L1, slide 5](L01-introduzione-al-corso.md#p-5))

$$
\sum_{w\in V} P(w\mid w_{<t}) = 1,\quad P(w\mid w_{<t})\ge 0
$$

Un language model restituisce una distribuzione sul vocabolario $V$. Esempio della slide: $0.42+0.31+0.09+0.03+0.15=1$.

**Softmax (anticipazione)** ([L1, slide 5](L01-introduzione-al-corso.md#p-5))

$$
P(w\mid w_{<t}) = \frac{e^{z_w}}{\sum_{v\in V} e^{z_v}}
$$

Trasforma i logit $z_w$ prodotti dalla rete in probabilità positive che sommano a 1. Logit $(2,1,0)\to(0.665, 0.245, 0.090)$. Visto in dettaglio nei capp. 4 e 7.

**Regola della catena (fattorizzazione autoregressiva)** ([L1, slide 6](L01-introduzione-al-corso.md#p-6))

$$
P(w_1,\dots,w_n)=\prod_{i=1}^{n}P(w_i\mid w_1,\dots,w_{i-1})
$$

Identità esatta: la probabilità di una sequenza è il prodotto delle probabilità condizionate di ogni token dati i precedenti. È ciò che un modello autoregressivo calcola.

**Decoding greedy** ([L1, slide 6](L01-introduzione-al-corso.md#p-6))

$$
\hat w_t = \arg\max_{w\in V} P(w\mid w_{<t})
$$

Sceglie sempre il token più probabile (water nella slide 5). L'alternativa è campionare $w_t\sim P(\cdot\mid w_{&lt;t})$.

**Loss di pretraining (cross-entropy, anticipazione)** ([L1, slide 57](L01-introduzione-al-corso.md#p-57))

$$
L = -\frac{1}{N}\sum_{t=1}^{N}\log P_\theta(w_t\mid w_{<t})
$$

Media delle log-probabilità negative dei token veri; il pretraining la minimizza. Nell'instruction tuning la somma è solo sui token della risposta. Capp. 4, 6, 7.

**Scaling laws (Hoffmann et al. 2022, J&M §1.1)** ([L1, slide 7](L01-introduzione-al-corso.md#p-7))

$$
N_{opt}\propto C^{1/2},\qquad D_{opt}\propto C^{1/2}
$$

A budget di calcolo $C$ fissato, parametri $N$ e token di training $D$ ottimali crescono entrambi circa come la radice di $C$. Dal libro, non dalle slide.

**Frequenza relativa di una parola data la storia** ([L4, slide 9](L04-modelli-linguistici-n-gram.md#p-9))

$$
P(w\mid h) = \frac{C(h\,w)}{C(h)}
$$

Stima diretta: tra le volte in cui si è vista la storia $h$, quante era seguita da $w$. Inutilizzabile per storie lunghe (conteggi 0).

**Distribuzione sulla parola successiva** ([L4, slide 5](L04-modelli-linguistici-n-gram.md#p-5))

$$
\sum_{w\in V} P(w\mid h) = 1,\quad P(w\mid h)\ge 0
$$

Un LM dà una probabilità per ogni parola del vocabolario (più </s>), e le probabilità di ogni contesto sommano a 1.

**Regola della catena** ([L4, slide 11](L04-modelli-linguistici-n-gram.md#p-11))

$$
P(w_{1:n}) = P(w_1)P(w_2\mid w_1)\cdots P(w_n\mid w_{1:n-1}) = \prod_{k=1}^{n}P(w_k\mid w_{1:k-1})
$$

Identità esatta: probabilità congiunta come prodotto di condizionate. Lega probabilità di sequenze e predizione della parola successiva.

### Estrazione di informazione

**Miscela di topic** ([L1, slide 49](L01-introduzione-al-corso.md#p-49))

$$
P(w\mid d)=\sum_{k=1}^{K}\theta_{d,k}\,\phi_k(w),\qquad \sum_k \theta_{d,k}=1
$$

$\theta_d$: miscela di topic del documento (es. 0.10, 0.25, 0.65); $\phi_k$: distribuzione sulle parole del topic $k$.

### Valutazione

**Accuracy** ([L1, slide 70](L01-introduzione-al-corso.md#p-70))

$$
\mathrm{Acc}=\frac{\#\,\text{risposte corrette}}{\#\,\text{esempi nel test set}}
$$

Su un test set etichettato e mai usato per il training (attenzione alla data contamination). MMLU: 15.908 domande in 57 aree.

**Perplexity** ([L1, slide 70](L01-introduzione-al-corso.md#p-70))

$$
\mathrm{PP}(W)=P(w_1,\dots,w_N)^{-1/N}=2^{-\frac{1}{N}\sum_{i}\log_2 P(w_i\mid w_{<i})}
$$

Più bassa è meglio; normalizzata per la lunghezza. Esempio: probabilità 0.5, 0.25, 0.125, 0.5 → $\mathrm{PP}=2^{1.75}\approx3.36$. Modello perfetto: 1; uniforme su $|V|$: $|V|$. Cap. 3.

**Precisione** ([L3, slide 12](L03-elaborazione-del-testo.md#p-12))

$$
P = \frac{TP}{TP + FP}
$$

Frazione delle corrispondenze trovate che sono giuste; si alza riducendo i falsi positivi. Definizione formale nel capitolo 4 del libro.

**Recall** ([L3, slide 12](L03-elaborazione-del-testo.md#p-12))

$$
R = \frac{TP}{TP + FN}
$$

Frazione dei casi giusti che vengono trovati; si alza riducendo i falsi negativi.

**Word error rate** ([L3, slide 52](L03-elaborazione-del-testo.md#p-52))

$$
\text{WER} = \frac{S + D + I}{N}
$$

S, D, I dall'allineamento di distanza minima (costi 1) fra ipotesi e riferimento, calcolato su parole; N = parole del riferimento. Può superare il 100%.

**Perplexity** ([L4, slide 30](L04-modelli-linguistici-n-gram.md#p-30))

$$
\mathrm{PP}(W) = P(w_1w_2\dots w_N)^{-\frac{1}{N}} = \sqrt[N]{\frac{1}{P(w_1w_2\dots w_N)}}
$$

Probabilità inversa del test set, normalizzata per il numero di token $N$ (</s> contato, <s> no). Più bassa è meglio; $\mathrm{PP}\ge1$.

**Perplexity con la regola della catena** ([L4, slide 31](L04-modelli-linguistici-n-gram.md#p-31))

$$
\mathrm{PP}(W) = \sqrt[N]{\prod_{i=1}^{N}\frac{1}{P(w_i\mid w_1\dots w_{i-1})}}
$$

Media geometrica delle probabilità condizionate inverse su tutto il test set.

**Perplexity unigram e bigram** ([L4, slide 31](L04-modelli-linguistici-n-gram.md#p-31))

$$
\mathrm{PP}_{\text{uni}}(W) = \sqrt[N]{\prod_{i=1}^{N}\frac{1}{P(w_i)}},\qquad \mathrm{PP}_{\text{bi}}(W) = \sqrt[N]{\prod_{i=1}^{N}\frac{1}{P(w_i\mid w_{i-1})}}
$$

Esempio bigram: <s> I am Sam </s> con il modello I am Sam, $\sqrt[4]{9} = 1{,}73$. WSJ: 962 (unigram), 170 (bigram), 109 (trigram).

**Perplexity in log** ([L4, slide 30](L04-modelli-linguistici-n-gram.md#p-30))

$$
\mathrm{PP}(W) = \exp\!\Big(-\frac{1}{N}\sum_{i=1}^{N}\ln P(w_i\mid w_{<i})\Big)
$$

Forma usata nel codice: esponenziale della log-verosimiglianza media negativa per token. Se un termine ha probabilità 0 la perplexity è infinita.

**Perplexity di un modello uniforme** ([L4, slide 34](L04-modelli-linguistici-n-gram.md#p-34))

$$
P(w) = \tfrac{1}{k}\ \forall w \;\Rightarrow\; \mathrm{PP} = \big((\tfrac1k)^N\big)^{-1/N} = k
$$

Coincide con il fattore di ramificazione. Colori: A = 3; B ($0{,}8; 0{,}1; 0{,}1$) su red red red red blue: $0{,}04096^{-1/5} = 1{,}89$.

**Cross-entropy su un test set** ([L5, slide 39](L05-smoothing-ed-entropia.md#p-39))

$$
H(W) = -\frac1N\log_2 P(w_1w_2\dots w_N)
$$

Approssimazione a lunghezza fissa $N$; bit per parola (o per token).

**Perplexity come 2 alla cross-entropy** ([L5, slide 39](L05-smoothing-ed-entropia.md#p-39))

$$
\text{Perplexity}(W) = 2^{H(W)} = P(w_1\dots w_N)^{-\frac1N} = \sqrt[N]{\frac{1}{P(w_1\dots w_N)}}
$$

$H$ bit per parola equivalgono a una scelta uniforme tra $2^H$ parole. Colori: A 1,58 bit → 3; B 0,92 bit → 1,89. WSJ: 962, 170, 109 = 9,9, 7,4, 6,8 bit.

**Precision** ([L7, slide 25](L07-regressione-logistica-multinomiale-e-valutazione.md#p-25))

$$
P = \frac{tp}{tp + fp}
$$

Frazione dei casi etichettati positivi dal sistema che lo sono davvero (riga della matrice di confusione).

**Recall** ([L7, slide 25](L07-regressione-logistica-multinomiale-e-valutazione.md#p-25))

$$
R = \frac{tp}{tp + fn}
$$

Frazione dei positivi veri che il sistema trova (colonna della matrice di confusione).

**Accuracy** ([L7, slide 24](L07-regressione-logistica-multinomiale-e-valutazione.md#p-24))

$$
\text{accuracy} = \frac{tp + tn}{tp + fp + tn + fn}
$$

Frazione di decisioni corrette. Ingannevole con classi sbilanciate: tutto negativo su 100 positivi in un milione dà 0,9999.

**F-measure** ([L7, slide 27](L07-regressione-logistica-multinomiale-e-valutazione.md#p-27))

$$
F_\beta = \frac{(\beta^2+1)\,P R}{\beta^2 P + R}
$$

$\beta &gt; 1$ favorisce la recall, $\beta &lt; 1$ la precision. Media armonica pesata: $F = 1/(\alpha/P + (1-\alpha)/R)$ con $\beta^2 = (1-\alpha)/\alpha$.

**F1** ([L7, slide 27](L07-regressione-logistica-multinomiale-e-valutazione.md#p-27))

$$
F_1 = \frac{2PR}{P+R} = \frac{2\,tp}{2\,tp + fp + fn}
$$

Media armonica di P e R. $P = 0{,}9$, $R = 0{,}1$: $F_1 = 0{,}18$.

**Media armonica** ([L7, slide 28](L07-regressione-logistica-multinomiale-e-valutazione.md#p-28))

$$
\text{HM}(a_1,\dots,a_n) = \frac{n}{\frac{1}{a_1} + \dots + \frac{1}{a_n}}
$$

Reciproco della media dei reciproci; sta fra il minimo e la media aritmetica, vicina al minimo.

**Macroaverage** ([L7, slide 31](L07-regressione-logistica-multinomiale-e-valutazione.md#p-31))

$$
P_{\text{macro}} = \frac1K\sum_{k=1}^{K}\frac{tp_k}{tp_k + fp_k}
$$

Media delle misure per classe; ogni classe pesa uguale. Esempio urgent/normal/spam: 0,60.

**Microaverage** ([L7, slide 31](L07-regressione-logistica-multinomiale-e-valutazione.md#p-31))

$$
P_{\text{micro}} = \frac{\sum_k tp_k}{\sum_k tp_k + \sum_k fp_k} = R_{\text{micro}} = \text{accuracy}
$$

Misura sulla matrice sommata; ogni documento pesa uguale. Con una sola etichetta per documento $\sum fp = \sum fn$, quindi micro P = micro R = accuracy. Esempio: 268/367 = 0,73.

### Parole e vocabolario

**Istanze e tipi** ([L2, slide 8](L02-parole-e-token.md#p-8))

$$
N = \#\text{occorrenze},\quad |V| = \#\text{forme distinte},\quad |V| \le N
$$

N conta le istanze nel testo corrente, |V| la dimensione del vocabolario (tipi). Frase del picnic: N = 16, |V| = 14 (18 e 16 con la punteggiatura).

**Rapporto tipi/istanze** ([L2, slide 11](L02-parole-e-token.md#p-11))

$$
\text{TTR} = \frac{|V|}{N}
$$

Diminuisce al crescere del corpus (Gettysburg 138/271 = 0,51; Brown 3,8%; COCA 0,45%) anche se |V| continua a crescere.

**Legge di Herdan-Heaps** ([L2, slide 12](L02-parole-e-token.md#p-12))

$$
|V| = k N^{\beta},\qquad k>0,\ 0<\beta<1
$$

$|V|$ tipi, $N$ istanze, $k$ e $\beta$ costanti positive dipendenti dal corpus. Valori riportati $\beta \approx 0{,}44$-$0{,}56$ (o più alti): poco più della radice quadrata. Nel tratto iniziale di un corpus $\beta \approx 1$.

**Heaps in scala log-log** ([L2, slide 12](L02-parole-e-token.md#p-12))

$$
\log |V| = \log k + \beta \log N
$$

Una legge di potenza è una retta in log-log con pendenza $\beta$; il notebook stima $\beta$ con i minimi quadrati su questi punti (Gettysburg 0,80, Alice 0,69).

**Crescita del vocabolario per un fattore m** ([L2, slide 12](L02-parole-e-token.md#p-12))

$$
\frac{|V(mN)|}{|V(N)|} = m^{\beta},\qquad \beta = \frac{\log(|V_2|/|V_1|)}{\log(N_2/N_1)}
$$

Il fattore non dipende da $k$. Con $\beta = 0{,}5$, $m = 4$: fattore 2 (esercizio 2). La seconda forma stima $\beta$ da due punti.

### Unicode

**Spazio dei code point** ([L2, slide 21](L02-parole-e-token.md#p-21))

$$
\text{U+0000} \ldots \text{U+10FFFF}:\ 0x10FFFF = 1\,114\,111,\quad 1\,114\,112 \text{ valori} \le 2^{21}
$$

Servono 21 bit ($2^{20} = 1\,048\,576 &lt; 1\,114\,112 \le 2^{21}$), quindi UTF-32 usa 4 byte per carattere. I primi 128 code point coincidono con ASCII (128 codici, 95 stampabili).

**Lunghezza in UTF-32 e UTF-8** ([L2, slide 22](L02-parole-e-token.md#p-22))

$$
\text{UTF-32: } 4n \text{ byte};\qquad \text{UTF-8: } \sum_{i=1}^{n} \ell(c_i),\ \ell(c) = \begin{cases}1 & c \le \text{7F}\\ 2 & c \le \text{7FF}\\ 3 & c \le \text{FFFF}\\ 4 & \text{altrimenti}\end{cases}
$$

$n$ code point, $c_i$ i loro valori. Esempi: café 5 byte, 日本 6, emoji U+1F600 4, hello 5 (UTF-32: 20).

**Stampi UTF-8** ([L2, slide 23](L02-parole-e-token.md#p-23))

$$
\texttt{0xxxxxxx}\ |\ \texttt{110yyyyy 10xxxxxx}\ |\ \texttt{1110zzzz 10yyyyyy 10xxxxxx}\ |\ \texttt{11110uuu 10uuzzzz 10yyyyyy 10xxxxxx}
$$

7, 11, 16, 21 bit utili. Il primo byte indica la lunghezza, le continuazioni iniziano con 10. ñ = U+00F1 → C3 B1; é → C3 A9; 进 = U+8FDB → E8 BF 9B; emoji U+1F600 → F0 9F 98 80.

### Tokenizzazione

**Conteggio pesato delle coppie in BPE** ([L2, slide 35](L02-parole-e-token.md#p-35))

$$
c(a,b) = \sum_{w} f(w)\cdot \#_{w}(a\,b)
$$

$f(w)$ frequenza della parola $w$ nel corpus, $\#_w(a\,b)$ quante volte i token $a, b$ sono adiacenti nella segmentazione corrente di $w$. Si fonde $\arg\max_{(a,b)} c(a,b)$ (a parità, una regola fissa). Esempio: $c(n,e) = 2\cdot1 + 2\cdot1 = 4$.

**Dimensione del vocabolario BPE** ([L2, slide 33](L02-parole-e-token.md#p-33))

$$
|V_{\text{BPE}}| = |\Sigma| + k
$$

$\Sigma$ alfabeto iniziale (caratteri del corpus, oppure i 256 byte nel BPE su byte), $k$ numero di merge. Libro: 7 + 8 = 15; esercizio 7: 8 + 3 = 11.

**Accorciamento del corpus a ogni merge** ([L2, slide 32](L02-parole-e-token.md#p-32))

$$
L' = L - c(a,b)
$$

Ogni occorrenza fusa riduce la lunghezza di un simbolo. Corpus ABDCABECAB: 10 → 7 (A B, 3 volte) → 5 (C AB, 2 volte). Vale per coppie di simboli diversi; con coppie uguali sovrapposte (a a a) il conteggio va fatto sulle occorrenze non sovrapposte.

**Rapporto di frammentazione tra lingue** ([L2, slide 44](L02-parole-e-token.md#p-44))

$$
\text{fertility} = \frac{\#\text{token}}{\#\text{parole}}
$$

Token per parola (nome usato in letteratura, non nelle slide). GPT-4o: ricetta inglese 19 token (14 parole più 4 segni), spagnola 33 (16 parole); nel notebook inglese 10 e italiano 16 token per le stesse 9 parole.

### Espressioni regolari

**Contatori** ([L3, slide 8](L03-elaborazione-del-testo.md#p-8))

$$
x^{*}:\ \ge 0 \quad x^{+} = x\,x^{*}:\ \ge 1 \quad x? = (x\,|\,\varepsilon) \quad x\{n\}:\ \text{esattamente } n
$$

Si applicano al carattere o gruppo immediatamente precedente. `{n,m}` da n a m occorrenze. `*?` e `+?` sono le versioni non greedy.

**Precedenza degli operatori** ([L3, slide 10](L03-elaborazione-del-testo.md#p-10))

$$
(\ ) \;>\; *\ +\ ?\ \{\} \;>\; \text{sequenze e ancore} \;>\; |
$$

Dalla più alta alla più bassa. `the*` = th + e\*; `the|any` = the oppure any.

### Distanza di edit

**Casi base** ([L3, slide 40](L03-elaborazione-del-testo.md#p-40))

$$
D[i,0] = \sum_{k=1}^{i} \text{del-cost}(X[k]),\quad D[0,j] = \sum_{k=1}^{j} \text{ins-cost}(Y[k])
$$

Con costi unitari $D[i,0] = i$ e $D[0,j] = j$: distanza dalla stringa vuota.

**Ricorrenza generale** ([L3, slide 40](L03-elaborazione-del-testo.md#p-40))

$$
D[i,j] = \min\{D[i-1,j] + \text{del}(X[i]),\ D[i,j-1] + \text{ins}(Y[j]),\ D[i-1,j-1] + \text{sub}(X[i],Y[j])\}
$$

$D[i,j]$ = distanza fra i primi $i$ caratteri di $X$ e i primi $j$ di $Y$; risposta $D[n,m]$; $\text{sub}(x,x) = 0$.

**Levenshtein con sostituzione a 2** ([L3, slide 40](L03-elaborazione-del-testo.md#p-40))

$$
D[i,j] = \min\{D[i-1,j]+1,\ D[i,j-1]+1,\ D[i-1,j-1] + 2\cdot[X[i] \ne Y[j]]\}
$$

Equivale a vietare le sostituzioni (una sostituzione = cancellazione + inserimento). intention → execution: 8.

**Levenshtein (costi 1)** ([L3, slide 36](L03-elaborazione-del-testo.md#p-36))

$$
D[i,j] = \min\{D[i-1,j]+1,\ D[i,j-1]+1,\ D[i-1,j-1] + [X[i] \ne Y[j]]\}
$$

Distanza di Levenshtein classica. intention → execution: 5. Limiti: $|n-m| \le d \le \max(n,m)$.

**Complessità** ([L3, slide 41](L03-elaborazione-del-testo.md#p-41))

$$
O(nm)\ \text{tempo},\quad O(nm)\ \text{memoria con backtrace},\ O(m)\ \text{solo distanza}
$$

Tabella di $(n+1)(m+1)$ celle, ognuna in tempo costante.

**Distanza con sostituzione a 2 e LCS** ([L3, slide 49](L03-elaborazione-del-testo.md#p-49))

$$
d_{1,1,2}(X,Y) = n + m - 2\,\mathrm{LCS}(X,Y)
$$

Con inserimento e cancellazione a 1 e sostituzione a 2 (o più) conviene sempre allineare solo lettere uguali: la distanza è il numero di caratteri fuori dalla più lunga sottosequenza comune. Esempi: intention/execution $9+9-2\cdot5 = 8$; sunday/saturday $6+8-2\cdot5 = 4$; drive/brief $5+5-2\cdot3 = 4$. Verificata contro la DP su 3000 coppie casuali. Utile per controllare una tabella fatta a mano.

**Limiti della distanza di Levenshtein (costi 1)** ([L3, slide 36](L03-elaborazione-del-testo.md#p-36))

$$
|n-m| \le d(X,Y) \le \max(n,m)
$$

Servono almeno $|n-m|$ inserimenti o cancellazioni per pareggiare le lunghezze; al massimo si sostituiscono i $\min(n,m)$ caratteri allineati e si inseriscono o cancellano gli altri. Esempio: leda/deal, $0 \le 3 \le 4$. Con sostituzione a 2 il limite superiore diventa $n+m$.

### N-gram

**Assunzione di Markov (bigram)** ([L4, slide 12](L04-modelli-linguistici-n-gram.md#p-12))

$$
P(w_n\mid w_{1:n-1}) \approx P(w_n\mid w_{n-1})
$$

La parola dipende solo dalla precedente: $P(\text{blue}\mid\text{The water ... beautifully}) \approx P(\text{blue}\mid\text{beautifully})$.

**Assunzione di Markov (n-gram)** ([L4, slide 12](L04-modelli-linguistici-n-gram.md#p-12))

$$
P(w_n\mid w_{1:n-1}) \approx P(w_n\mid w_{n-N+1:n-1})
$$

Si guardano $N-1$ parole indietro: $N = 2$ bigram, $N = 3$ trigram.

**Probabilità di una sequenza con un bigram** ([L4, slide 20](L04-modelli-linguistici-n-gram.md#p-20))

$$
P(w_{1:n}) \approx \prod_{k=1}^{n}P(w_k\mid w_{k-1})
$$

Con $w_0 = $ <s> e un fattore finale $P(\text{&lt;/s&gt;}\mid w_n)$. Esempio: $P(\text{&lt;s&gt; i want english food &lt;/s&gt;}) = 0{,}25\times0{,}33\times0{,}0011\times0{,}5\times0{,}68 = 0{,}000031$.

**MLE bigram** ([L4, slide 13](L04-modelli-linguistici-n-gram.md#p-13))

$$
P(w_n\mid w_{n-1}) = \frac{C(w_{n-1}w_n)}{\sum_w C(w_{n-1}w)} = \frac{C(w_{n-1}w_n)}{C(w_{n-1})}
$$

Frequenza relativa; la somma dei bigram che iniziano con $w_{n-1}$ è il suo conteggio unigram. Esempi: $P(\text{am}\mid\text{I}) = 2/3$; $P(\text{want}\mid\text{i}) = 827/2533 = 0{,}33$.

**MLE n-gram** ([L4, slide 13](L04-modelli-linguistici-n-gram.md#p-13))

$$
P(w_n\mid w_{n-N+1:n-1}) = \frac{C(w_{n-N+1:n-1}\,w_n)}{C(w_{n-N+1:n-1})}
$$

Stessa idea per contesti di $N-1$ parole; per il trigram all'inizio della frase si usano due <s>.

**MLE unigram** ([L4, slide 13](L04-modelli-linguistici-n-gram.md#p-13))

$$
P(w) = \frac{C(w)}{N_{\text{tot}}}
$$

Conteggio diviso il numero totale di token. Esempio: Chinese 400 volte su un milione, $P = 0{,}0004$: il valore che rende più probabili 400 occorrenze.

**Log probabilità** ([L4, slide 22](L04-modelli-linguistici-n-gram.md#p-22))

$$
p_1 p_2 p_3 p_4 = \exp(\log p_1+\log p_2+\log p_3+\log p_4)
$$

Si sommano i log (naturali) invece di moltiplicare, per evitare l'underflow; si torna con exp solo alla fine.

**Sparsità: n-gram possibili** ([L4, slide 43](L04-modelli-linguistici-n-gram.md#p-43))

$$
\#\text{n-gram possibili} = V^n,\qquad \#\text{bigram distinti osservati} \le N-1
$$

Shakespeare: $V = 29.066$, $V^2 \approx 8{,}45\cdot10^8$, $V^4 \approx 7\cdot10^{17}$, contro $N = 884.647$ token: al più lo 0,105% dei bigram compare.

### Smoothing

**Laplace (add-one) sugli unigram** ([L5, slide 10](L05-smoothing-ed-entropia.md#p-10))

$$
P_{\text{Laplace}}(w_i) = \frac{c_i+1}{N+V}
$$

$c_i$ conteggio della parola, $N$ token totali, $V$ dimensione del vocabolario: $V$ osservazioni fittizie in più al denominatore.

**Somma senza correzione del denominatore** ([L5, slide 10](L05-smoothing-ed-entropia.md#p-10))

$$
\sum_i \frac{c_i+1}{N} = \frac{N+V}{N} > 1
$$

Perché nell'add-one il denominatore deve crescere di $V$.

**Laplace (add-one) sui bigram** ([L5, slide 14](L05-smoothing-ed-entropia.md#p-14))

$$
P_{\text{Laplace}}(w_n\mid w_{n-1}) = \frac{C(w_{n-1}w_n)+1}{\sum_w (C(w_{n-1}w)+1)} = \frac{C(w_{n-1}w_n)+1}{C(w_{n-1})+V}
$$

Ogni riga riceve $V$ conteggi in più. BeRP: $P(\text{to}\mid\text{want}) = 609/2373 = 0{,}26$ (MLE 0,66).

**Conteggio ricostruito (adjusted count)** ([L5, slide 17](L05-smoothing-ed-entropia.md#p-17))

$$
C^*(w_{n-1}w_n) = \frac{[C(w_{n-1}w_n)+1]\times C(w_{n-1})}{C(w_{n-1})+V}
$$

Il conteggio che, diviso per il denominatore non smoothed $C(w_{n-1})$, dà la probabilità add-one. $C^*(\text{want to}) = 238$.

**Sconto** ([L5, slide 18](L05-smoothing-ed-entropia.md#p-18))

$$
d = \frac{C^*}{C}
$$

Rapporto tra conteggio nuovo e vecchio: $d(\text{want to}) = 0{,}39$, $d(\text{chinese food}) = 0{,}10$.

**Add-k** ([L5, slide 21](L05-smoothing-ed-entropia.md#p-21))

$$
P^*_{\text{Add-}k}(w_n\mid w_{n-1}) = \frac{C(w_{n-1}w_n)+k}{C(w_{n-1})+kV}
$$

$k=1$ Laplace, $k=0$ MLE; $k$ si sceglie sul devset.

**Interpolazione lineare** ([L5, slide 24](L05-smoothing-ed-entropia.md#p-24))

$$
\hat P(w_n\mid w_{n-2}w_{n-1}) = \lambda_1P(w_n) + \lambda_2P(w_n\mid w_{n-1}) + \lambda_3P(w_n\mid w_{n-2}w_{n-1}),\quad \sum_i\lambda_i = 1
$$

Media pesata delle stime unigram, bigram e trigram; i $\lambda$ si fissano su un corpus held-out (EM).

**Interpolazione con pesi condizionati dal contesto** ([L5, slide 25](L05-smoothing-ed-entropia.md#p-25))

$$
\hat P(w_n\mid w_{n-2}w_{n-1}) = \lambda_1(w_{n-2:n-1})P(w_n) + \lambda_2(w_{n-2:n-1})P(w_n\mid w_{n-1}) + \lambda_3(w_{n-2:n-1})P(w_n\mid w_{n-2}w_{n-1})
$$

Ogni $\lambda$ dipende dalle due parole precedenti: più peso al trigram se il contesto è frequente.

**Stupid backoff** ([L5, slide 27](L05-smoothing-ed-entropia.md#p-27))

$$
S(w_i\mid w_{i-N+1:i-1}) = \begin{cases}\frac{\text{count}(w_{i-N+1:i})}{\text{count}(w_{i-N+1:i-1})} & \text{se count}(w_{i-N+1:i})>0\\ \lambda S(w_i\mid w_{i-N+2:i-1}) & \text{altrimenti}\end{cases}
$$

Niente discounting, $\lambda = 0{,}4$ (Brants et al. 2007): uno score, non una probabilità.

**Stupid backoff: caso base unigram** ([L5, slide 27](L05-smoothing-ed-entropia.md#p-27))

$$
S(w) = \frac{\text{count}(w)}{N}
$$

Il backoff termina nell'unigram.

### Teoria dell'informazione

**Entropia** ([L5, slide 31](L05-smoothing-ed-entropia.md#p-31))

$$
H(X) = -\sum_{x\in\chi}p(x)\log_2 p(x)
$$

In bit con log in base 2; limite inferiore ai bit medi di un codice ottimale. Uniforme su $k$ valori: $\log_2 k$.

**Entropia della corsa di cavalli** ([L5, slide 33](L05-smoothing-ed-entropia.md#p-33))

$$
H = \tfrac12\cdot1+\tfrac14\cdot2+\tfrac18\cdot3+\tfrac1{16}\cdot4+4\cdot\tfrac1{64}\cdot6 = 2\text{ bit}
$$

Con probabilità 1/2, 1/4, 1/8, 1/16, 4 × 1/64; equiprobabili: 3 bit.

**Lunghezza media di un codice** ([L5, slide 34](L05-smoothing-ed-entropia.md#p-34))

$$
\bar L = \sum_x p(x)\,\ell(x) \ge H(X)
$$

Il codice 0, 10, 110, 1110, 1111xx ha $\bar L = 2$ bit $= H$, perché $\ell(x) = -\log_2 p(x)$.

**Entropia di sequenze di n parole** ([L5, slide 36](L05-smoothing-ed-entropia.md#p-36))

$$
H(w_1,\dots,w_n) = -\sum_{w_{1:n}\in L}p(w_{1:n})\log p(w_{1:n})
$$

Variabile aleatoria che varia su tutte le sequenze di lunghezza $n$.

**Entropy rate (per parola)** ([L5, slide 36](L05-smoothing-ed-entropia.md#p-36))

$$
\frac1n H(w_{1:n}) = -\frac1n\sum_{w_{1:n}\in L}p(w_{1:n})\log p(w_{1:n})
$$

Entropia della sequenza divisa per il numero di parole.

**Entropia di un linguaggio** ([L5, slide 36](L05-smoothing-ed-entropia.md#p-36))

$$
H(L) = \lim_{n\to\infty}\frac1n H(w_{1:n})
$$

Il linguaggio come processo stocastico; servono sequenze infinitamente lunghe.

**Teorema di Shannon-McMillan-Breiman** ([L5, slide 37](L05-smoothing-ed-entropia.md#p-37))

$$
H(L) = \lim_{n\to\infty}-\frac1n\log p(w_{1:n})
$$

Per processi stazionari ed ergodici basta una sola sequenza lunga.

**Cross-entropy** ([L5, slide 38](L05-smoothing-ed-entropia.md#p-38))

$$
H(p,m) = \lim_{n\to\infty}-\frac1n\sum_{W\in L}p(w_1,\dots,w_n)\log m(w_1,\dots,w_n)
$$

Sequenze estratte da $p$, log probabilità secondo il modello $m$.

**Cross-entropy su una sequenza lunga** ([L5, slide 38](L05-smoothing-ed-entropia.md#p-38))

$$
H(p,m) = \lim_{n\to\infty}-\frac1n\log m(w_1\dots w_n)
$$

Non serve conoscere $p$: basta un campione lungo (il test set).

**Limite superiore** ([L5, slide 38](L05-smoothing-ed-entropia.md#p-38))

$$
H(p)\le H(p,m)
$$

Per ogni modello $m$; il modello più accurato ha cross-entropy più bassa.

### Classificazione

**Training set etichettato** ([L6, slide 10](L06-regressione-logistica.md#p-10))

$$
\{(x^{(1)},y^{(1)}),(x^{(2)},y^{(2)}),\dots,(x^{(m)},y^{(m)})\}
$$

$m$ coppie osservazione-etichetta; l'apice $(i)$ indica l'esempio, il pedice $j$ la feature: $x^{(i)}_j$.

### Naive Bayes

**Classe più probabile (Bayes)** ([L6, slide 14](L06-regressione-logistica.md#p-14))

$$
\hat c = \operatorname*{argmax}_{c\in C} P(c\mid d) = \operatorname*{argmax}_{c\in C} P(d\mid c)\,P(c)
$$

$P(d\mid c)$ likelihood, $P(c)$ prior; $P(d)$ si elimina perché uguale per tutte le classi.

**Classificatore Naive Bayes** ([L6, slide 15](L06-regressione-logistica.md#p-15))

$$
c_{NB} = \operatorname*{argmax}_{c\in C} P(c)\prod_{i\in\text{positions}} P(w_i\mid c)
$$

Bag of words + indipendenza delle parole data la classe; il prodotto è sulle posizioni del documento di test.

**Naive Bayes in spazio log** ([L6, slide 15](L06-regressione-logistica.md#p-15))

$$
c_{NB} = \operatorname*{argmax}_{c\in C} \log P(c) + \sum_{i\in\text{positions}}\log P(w_i\mid c)
$$

Somma di log probabilità, contro l'underflow; funzione lineare dei conteggi delle parole.

**Prior** ([L6, slide 16](L06-regressione-logistica.md#p-16))

$$
\hat P(c) = \frac{N_c}{N_{doc}}
$$

Frazione dei documenti di training nella classe $c$.

**Likelihood (MLE)** ([L6, slide 16](L06-regressione-logistica.md#p-16))

$$
\hat P(w_i\mid c) = \frac{\text{count}(w_i,c)}{\sum_{w\in V}\text{count}(w,c)}
$$

Frequenza di $w_i$ nel testo concatenato della classe $c$; $V$ vocabolario di tutte le classi.

**Likelihood con add-one** ([L6, slide 17](L06-regressione-logistica.md#p-17))

$$
\hat P(w_i\mid c) = \frac{\text{count}(w_i,c)+1}{\left(\sum_{w\in V}\text{count}(w,c)\right)+|V|}
$$

Laplace: nessuna parola del vocabolario ha probabilità 0 in una classe. Le parole di test mai viste in training si eliminano.

### Regressione logistica

**Somma pesata (logit)** ([L6, slide 20](L06-regressione-logistica.md#p-20))

$$
z = \left(\sum_{i=1}^n w_ix_i\right)+b = \mathbf{w}\cdot\mathbf{x}+b
$$

$w_i$ pesi, $b$ bias (intercept); $z\in(-\infty,+\infty)$.

**Sigmoide** ([L6, slide 22](L06-regressione-logistica.md#p-22))

$$
\sigma(z) = \frac{1}{1+e^{-z}} = \frac{1}{1+\exp(-z)}
$$

Funzione logistica: manda $\mathbb{R}$ in $(0,1)$; $\sigma(0) = 0{,}5$, $\sigma(2) = 0{,}881$.

**Derivata della sigmoide** ([L6, slide 22](L06-regressione-logistica.md#p-22))

$$
\sigma'(z) = \sigma(z)\,(1-\sigma(z))
$$

Massimo $1/4$ in $z = 0$; serve per derivare il gradiente della loss.

**Probabilità delle due classi** ([L6, slide 23](L06-regressione-logistica.md#p-23))

$$
P(y=1) = \sigma(\mathbf{w}\cdot\mathbf{x}+b),\quad P(y=0) = 1-\sigma(\mathbf{w}\cdot\mathbf{x}+b) = \sigma(-(\mathbf{w}\cdot\mathbf{x}+b))
$$

Le due probabilità sommano a 1.

**Simmetria della sigmoide** ([L6, slide 23](L06-regressione-logistica.md#p-23))

$$
1-\sigma(x) = \sigma(-x)
$$

Per questo $P(y=0) = \sigma(-z)$.

**Logit** ([L6, slide 24](L06-regressione-logistica.md#p-24))

$$
\text{logit}(p) = \sigma^{-1}(p) = \ln\frac{p}{1-p}
$$

Log degli odds; $z$ si legge come log odds della classe positiva. $\text{logit}(0{,}8) = \ln 4 = 1{,}39$.

**Soglia di decisione** ([L6, slide 25](L06-regressione-logistica.md#p-25))

$$
\text{decision}(x) = \begin{cases}1 & \text{se } P(y=1\mid x) > 0.5\\ 0 & \text{altrimenti}\end{cases}
$$

Equivale a $\mathbf{w}\cdot\mathbf{x}+b &gt; 0$: confine lineare (iperpiano). $\hat y = \sigma(z) = P(y=1\mid x)$.

**Standardizzazione (z-score)** ([L6, slide 31](L06-regressione-logistica.md#p-31))

$$
\mu_i = \frac1m\sum_{j=1}^m x_i^{(j)},\quad \sigma_i = \sqrt{\frac1m\sum_{j=1}^m\left(x_i^{(j)}-\mu_i\right)^2},\quad x_i' = \frac{x_i-\mu_i}{\sigma_i}
$$

Media 0 e deviazione standard 1 per ogni feature; $\sigma_i$ non è la sigmoide. Statistiche dal training set.

**Normalizzazione min-max** ([L6, slide 32](L06-regressione-logistica.md#p-32))

$$
x_i' = \frac{x_i-\min(x_i)}{\max(x_i)-\min(x_i)}
$$

Porta la feature in $[0,1]$.

**Forma matriciale** ([L6, slide 33](L06-regressione-logistica.md#p-33))

$$
\hat{\mathbf{y}} = \sigma(\mathbf{X}\mathbf{w}+\mathbf{b})
$$

$\mathbf{X}$: $m\times f$ (un esempio per riga), $\mathbf{w}$: $f\times 1$, $\mathbf{b}$ e $\hat{\mathbf{y}}$: $m\times 1$; $\sigma$ elemento per elemento.

**Softmax** ([L7, slide 7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-7))

$$
\text{softmax}(z_i) = \frac{\exp(z_i)}{\sum_{j=1}^{K}\exp(z_j)},\quad 1\le i\le K
$$

$K$ logit in $K$ probabilità che sommano a 1. Invariante per traslazione: $\text{softmax}(\mathbf z + c) = \text{softmax}(\mathbf z)$; in pratica si sottrae $\max_j z_j$.

**Softmax per due classi** ([L7, slide 7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-7))

$$
\frac{e^{z_1}}{e^{z_1}+e^{z_2}} = \sigma(z_1 - z_2)
$$

Con $K = 2$ la softmax è la sigmoide della differenza: regressione binaria con $\mathbf w = \mathbf w_1 - \mathbf w_2$, $b = b_1 - b_2$ (esercizio 2).

**Probabilità della classe k** ([L7, slide 10](L07-regressione-logistica-multinomiale-e-valutazione.md#p-10))

$$
P(y_k = 1\mid\mathbf x) = \frac{\exp(\mathbf w_k\cdot\mathbf x + b_k)}{\sum_{j=1}^{K}\exp(\mathbf w_j\cdot\mathbf x + b_j)}
$$

Un vettore di pesi $\mathbf w_k$ e un bias $b_k$ per classe; $z_k = \mathbf w_k\cdot\mathbf x + b_k$ è il logit della classe.

**Forma matriciale** ([L7, slide 11](L07-regressione-logistica-multinomiale-e-valutazione.md#p-11))

$$
\hat{\mathbf y} = \text{softmax}(W\mathbf x + \mathbf b),\quad W\in\mathbb R^{K\times f},\ \mathbf b\in\mathbb R^{K}
$$

Righe di $W$ = vettori di pesi (prototipi) delle classi. Per un batch $X$ ($m\times f$): $\hat Y = \text{softmax}(XW^{\top} + \mathbf b)$ riga per riga.

**Cross-entropy per K classi** ([L7, slide 16](L07-regressione-logistica-multinomiale-e-valutazione.md#p-16))

$$
L_{CE}(\hat{\mathbf y},\mathbf y) = -\sum_{k=1}^{K} y_k\log\hat y_k
$$

$\mathbf y$ one-hot, $\hat{\mathbf y}$ uscita della softmax, log naturale. Per $K = 2$ ritrova la cross-entropy binaria $-[y\log\hat y + (1-y)\log(1-\hat y)]$.

**Negative log likelihood** ([L7, slide 17](L07-regressione-logistica-multinomiale-e-valutazione.md#p-17))

$$
L_{CE} = -\log\hat y_c = -z_c + \log\sum_{j=1}^{K} e^{z_j}
$$

$c$ classe corretta. Esempio: $\hat y_c = 0{,}7$ dà 0,36. La seconda forma (log-sum-exp) serve per derivare il gradiente.

**Gradiente per K classi** ([L7, slide 20](L07-regressione-logistica-multinomiale-e-valutazione.md#p-20))

$$
\frac{\partial L_{CE}}{\partial w_{k,i}} = (\hat y_k - y_k)\,x_i,\qquad \frac{\partial L_{CE}}{\partial b_k} = \hat y_k - y_k
$$

Errore sulla classe $k$ per la feature $i$. In forma matriciale $\nabla_W L = (\hat{\mathbf y} - \mathbf y)\,\mathbf x^{\top}$ ($K\times f$); per un batch $(1/m)(\hat Y - Y)^{\top}X$.

### Loss

**Bernoulli** ([L6, slide 37](L06-regressione-logistica.md#p-37))

$$
p(y\mid x) = \hat y^{\,y}(1-\hat y)^{1-y}
$$

Vale $\hat y$ se $y = 1$, $1-\hat y$ se $y = 0$.

**Cross-entropy loss** ([L6, slide 37](L06-regressione-logistica.md#p-37))

$$
L_{CE}(\hat y, y) = -\log p(y\mid x) = -\left[y\log\hat y + (1-y)\log(1-\hat y)\right]
$$

Negative log likelihood dell'etichetta vera; log naturale. Da 0 a $+\infty$; $\ln 2 = 0{,}69$ con $\hat y = 0{,}5$.

**Cross-entropy loss con la sigmoide** ([L6, slide 38](L06-regressione-logistica.md#p-38))

$$
L_{CE} = -\left[y\log\sigma(\mathbf{w}\cdot\mathbf{x}+b)+(1-y)\log\left(1-\sigma(\mathbf{w}\cdot\mathbf{x}+b)\right)\right]
$$

Sulla recensione di esempio: 0,36 se $y = 1$, 1,2 se $y = 0$.

### Ottimizzazione

**Obiettivo: loss media minima** ([L6, slide 41](L06-regressione-logistica.md#p-41))

$$
\hat\theta = \operatorname*{argmin}_\theta \frac1m\sum_{i=1}^m L_{CE}\left(f(x^{(i)};\theta), y^{(i)}\right)
$$

$\theta = \{\mathbf{w}, b\}$, $\hat y^{(i)} = f(x^{(i)};\theta)$.

**Discesa del gradiente in una dimensione** ([L6, slide 43](L06-regressione-logistica.md#p-43))

$$
w^{t+1} = w^t - \eta\,\frac{d}{dw}L(f(x;w),y)
$$

Pendenza negativa → $w$ aumenta; $\eta$ learning rate.

**Aggiornamento con il gradiente** ([L6, slide 44](L06-regressione-logistica.md#p-44))

$$
\theta^{t+1} = \theta^t - \eta\,\nabla L(f(x;\theta),y)
$$

$\nabla L$ = vettore delle derivate parziali rispetto a ogni peso e al bias.

**Gradiente della regressione logistica** ([L6, slide 45](L06-regressione-logistica.md#p-45))

$$
\frac{\partial L_{CE}}{\partial w_j} = (\hat y - y)\,x_j,\qquad \frac{\partial L_{CE}}{\partial b} = \hat y - y
$$

Errore della previsione per l'input; per un solo esempio.

**Costo di un mini-batch** ([L6, slide 52](L06-regressione-logistica.md#p-52))

$$
\text{Cost}(\hat y, y) = \frac1m\sum_{i=1}^m L_{CE}(\hat y^{(i)}, y^{(i)})
$$

Media delle loss degli $m$ esempi (assunti indipendenti).

**Gradiente del mini-batch** ([L6, slide 52](L06-regressione-logistica.md#p-52))

$$
\frac{\partial\,\text{Cost}}{\partial w_j} = \frac1m\sum_{i=1}^m\left[\sigma(\mathbf{w}\cdot\mathbf{x}^{(i)}+b)-y^{(i)}\right]x_j^{(i)}
$$

Media dei gradienti individuali; per il bias la media degli errori $\hat y^{(i)}-y^{(i)}$.

**Gradiente in forma matriciale** ([L6, slide 52](L06-regressione-logistica.md#p-52))

$$
\frac{\partial\,\text{Cost}}{\partial\mathbf{w}} = \frac1m(\hat{\mathbf{y}}-\mathbf{y})^\top\mathbf{X} = \frac1m\left(\sigma(\mathbf{X}\mathbf{w}+\mathbf{b})-\mathbf{y}\right)^\top\mathbf{X}
$$

$\mathbf{X}$: $m\times f$, $\mathbf{y}$: $m\times 1$.

### Significatività statistica

**Effect size** ([L7, slide 38](L07-regressione-logistica-multinomiale-e-valutazione.md#p-38))

$$
\delta(x) = M(A, x) - M(B, x)
$$

Differenza della metrica $M$ (F1, accuracy) fra A e B sul test set $x$.

**Ipotesi e p-value** ([L7, slide 42](L07-regressione-logistica-multinomiale-e-valutazione.md#p-42))

$$
H_0: \delta(x)\le 0,\quad H_1: \delta(x) \gt 0,\qquad p = P\big(\delta(X)\ge\delta(x)\mid H_0\big)
$$

Probabilità, se A non è migliore di B, di un $\delta$ almeno grande quanto l'osservato; si rifiuta $H_0$ se $p$ è sotto una soglia fissata prima (0,05 o 0,01). Moneta: 9+ teste su 10, $p = 11/1024$.

**p-value del paired bootstrap** ([L7, slide 47](L07-regressione-logistica-multinomiale-e-valutazione.md#p-47))

$$
p\text{-value}(x) = \frac1b\sum_{i=1}^{b}\mathbb 1\big(\delta(x^{(i)}) \ge 2\delta(x)\big)
$$

$b$ test set virtuali $x^{(i)}$ estratti da $x$ con reinserimento, appaiati. $2\delta(x)$ perché la distribuzione bootstrap è centrata su $\delta(x)$ e va spostata in 0 (Eq. 4.48). Esempio a 10 documenti: 0,27.

### Regolarizzazione

**Obiettivo regolarizzato** ([L7, slide 55](L07-regressione-logistica-multinomiale-e-valutazione.md#p-55))

$$
\hat\theta = \arg\max_\theta \sum_{i=1}^{m}\log P(y^{(i)}\mid x^{(i)}) - \alpha R(\theta)
$$

$\alpha$ forza della regolarizzazione (iperparametro); il bias non è incluso in $R$.

**L2 (ridge)** ([L7, slide 56](L07-regressione-logistica-multinomiale-e-valutazione.md#p-56))

$$
R(\theta) = \lVert\theta\rVert_2^2 = \sum_{j=1}^{n}\theta_j^2
$$

Tanti pesi piccoli; derivata $2\theta_j$; corrisponde a un prior gaussiano con $\alpha = 1/(2\sigma^2)$.

**L1 (lasso)** ([L7, slide 56](L07-regressione-logistica-multinomiale-e-valutazione.md#p-56))

$$
R(\theta) = \lVert\theta\rVert_1 = \sum_{i=1}^{n}|\theta_i|
$$

Pesi sparsi, molti esattamente 0; non differenziabile in 0; corrisponde a un prior di Laplace.

**Weight decay (passo con L2)** ([L7, slide 56](L07-regressione-logistica-multinomiale-e-valutazione.md#p-56))

$$
\theta_j \leftarrow (1 - 2\eta\alpha)\,\theta_j - \eta\,\frac{\partial L}{\partial\theta_j}
$$

Discesa del gradiente su $L + \alpha\sum\theta^2$: a ogni passo il peso si riduce di un fattore costante ($\eta = 0{,}1$, $\alpha = 0{,}5$: 0,9). Esercizio 12.

**Prior gaussiano e L2** ([L7, slide 57](L07-regressione-logistica-multinomiale-e-valutazione.md#p-57))

$$
\log\prod_{j}\frac{1}{\sqrt{2\pi\sigma^2}}e^{-\theta_j^2/(2\sigma^2)} = -\frac{1}{2\sigma^2}\sum_j\theta_j^2 + \text{cost.}
$$

Massimizzare log verosimiglianza + log prior gaussiano a media 0 equivale alla regolarizzazione L2 con $\alpha = 1/(2\sigma^2)$ (Eq. 4.54-4.56).

## Correzioni alle slide

- **L2, slide 35** (Training su un corpus piccolo: inizio): n e non è «più frequente di ogni altra coppia»: è un pareggio. [Dettagli](L02-parole-e-token.md#p-35)
- **L3, slide 6** (Disgiunzione di caratteri: le parentesi quadre): r"a^b" non trova mai «a^b» in Python. [Dettagli](L03-elaborazione-del-testo.md#p-6)
- **L3, slide 31** (Un tokenizer a espressioni regolari (NLTK)): Il pattern non produce «82%» come dice il commento. [Dettagli](L03-elaborazione-del-testo.md#p-31)
- **L3, slide 34** (Lo stemmer di Porter): «doing → doe» e «policy → polic» non sono output di Porter. [Dettagli](L03-elaborazione-del-testo.md#p-34)
- **L4, slide 18** (Conteggi bigram: sparsità): Gli zeri sono la metà delle celle, non la maggioranza. [Dettagli](L04-modelli-linguistici-n-gram.md#p-18)
- **L4, slide 19** (Probabilità bigram): Cella food → chinese: 0,00091, non 0,00092. [Dettagli](L04-modelli-linguistici-n-gram.md#p-19)
- **L7, slide 9** (Softmax di un vettore: un esempio): La somma degli esponenziali è 33,23, non 33,24. [Dettagli](L07-regressione-logistica-multinomiale-e-valutazione.md#p-9)

## Bug trovati nei notebook del corso

- **L2** · Parole e tipi: la funzione words(): Bug: punteggiatura iniziale con keep_punctuation=True
- **L2** · Alice nel paese delle meraviglie (opzionale): Bug: la punteggiatura tipografica non viene tolta
- **L2** · BPE sul discorso di Gettysburg: Bug: la frase di test perde le parole ripetute
- **L3** · ELIZA, una cascata di sostituzioni: Bug: le regole .* X .* non scattano se la parola chiave è a inizio frase
- **L3** · Il pretokenizer di GPT-2 con re (esercizio 7): Imprecisione: le classi di re non sono esattamente \p{L} e \p{N}
- **L3** · Contare le parole alla Unix, in Python: Bug minore: il corpus contiene docstring ereditate e importate
- **L4** · Un corpus più grande: le docstring della libreria standard: Bug: getdoc eredita le docstring, e il test set contiene frasi del training
- **L5** · Corpus delle docstring: training, development e test: Bug: le docstring ereditate contaminano ancora development e test
- **L5** · Interpolazione lineare: ricerca a griglia: Bug: l'interpolazione non è una distribuzione nei contesti mai visti

## Domande d'orale, per lezione

### L1 · Introduzione al corso

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

### L2 · Parole e token

<details><summary>Che differenza c'è tra word type, word instance e token?</summary>

Traccia: (1) type = forma distinta, l'insieme è il vocabolario V, dimensione |V|; (2) instance = occorrenza nel testo, conteggio N; esempio della frase del picnic: 16 istanze, 14 tipi (*the* ×3); (3) token = output del tokenizer; nella letteratura vecchia «word token» = istanza, il libro riserva «token» ai subword; (4) i numeri dipendono dalle convenzioni (punteggiatura: 18 istanze; maiuscole: They/they) e le convenzioni dipendono dal compito.

</details>

<details><summary>Perché la definizione di parola dipende dal compito e dalla lingua?</summary>

Traccia: (1) punteggiatura: si tiene o no; (2) parlato: frammenti e pause piene, utili nel riconoscimento del parlato; (3) contrazioni e clitici: *I'm* una parola ortografica, due grammaticali; (4) maiuscole; (5) lingue senza spazi: cinese 姚明进入总决赛 in 3, 5 o 7 unità a seconda dello standard (Chinese Treebank, Peking University, caratteri); (6) conclusione: la parola non è un'unità affidabile tra compiti e lingue.

</details>

<details><summary>Enuncia la legge di Heaps e interpreta il grafico di Gutenberg.</summary>

Traccia: (1) $|V| = kN^{\beta}$, $0 &lt; \beta &lt; 1$, valori tipici 0,44-0,56: poco più della radice quadrata; (2) in log-log è una retta di pendenza β; (3) grafico: curva da 1 a circa $10^9$ parole, retta verde β = 1 all'inizio, arancione β = 0,44 da circa $10^5$; (4) due regimi: prima quasi ogni parola è nuova (parole funzionali e comuni), poi arrivano solo parole di contenuto, nomi, termini tecnici; (5) conseguenza: nessun vocabolario è completo, parole sconosciute; (6) conto: N ×4 con β = 0,5 → |V| ×2.

</details>

<details><summary>Che cos'è il problema delle parole sconosciute e come lo risolvono i subword?</summary>

Traccia: (1) un modello addestrato su low, new, newer non sa gestire lower al test (OOV, <UNK>); (2) per Heaps capita sempre; (3) i subword sono unità più piccole ricombinabili: lower = low + er; (4) con BPE ogni parola è una sequenza di token noti, nel caso peggiore caratteri (GRPO lettera per lettera); (5) garanzia completa col BPE su byte: 256 simboli di base coprono qualsiasi testo.

</details>

<details><summary>Che cosa sono morfemi flessivi, derivazionali e clitici? Esempi.</summary>

Traccia: (1) morfema = minima unità con significato, radice + affissi (*care-ful-ly*); (2) flessivi: grammaticali, produttivi, obbligatori, prevedibili, non cambiano categoria (-s plurale, -ed passato; gatt-i); (3) derivazionali: idiosincratici, sottoclasse di parole, cambiano categoria (care → careful → carefully; gentile → gentilmente); (4) clitici: sintatticamente parole, ridotti e attaccati (I've, teacher's, l'opéra, dammelo); (5) flessione e derivazione sono poli di un continuum.

</details>

<details><summary>Descrivi le due dimensioni della tipologia morfologica.</summary>

Traccia: (1) morfemi per parola: isolanti/analitiche (vietnamita 1,1, cantonese) → sintetiche → polisintetiche (koryak, groenlandese 3,7); inglese 1,7 nella stima di Greenberg 1960; (2) segmentabilità: agglutinanti (turco, confini netti) vs fusive (russo -om; inglese -s di she reads = 3a persona + singolare + presente; italiano -o di parlo); (3) sono tendenze; (4) conseguenza: i morfemi sono difficili da usare come unità standard tra lingue.

</details>

<details><summary>Che differenza c'è tra carattere, code point, glifo e byte?</summary>

Traccia: (1) Unicode assegna a ogni carattere un code point, U+0000-U+10FFFF (1.114.112 valori), primi 128 = ASCII; (2) glifo = forma visiva del font; a in Times e Courier stesso U+0061; (3) i byte vengono da una codifica: UTF-8 usa 1-4 byte; (4) in Python `str` = code point, `bytes` = byte; café: 4 code point, 5 byte; (5) non esiste file di testo senza codifica.

</details>

<details><summary>Perché si usa UTF-8 e non UTF-32? Come funziona UTF-8?</summary>

Traccia: (1) UTF-32: 4 byte fissi (21 bit necessari), file 4 volte più grandi, pieni di zeri che rompono i sistemi in stile C; (2) UTF-8 a lunghezza variabile: ASCII 1 byte (compatibile), poi 2, 3, 4 byte con valori 128-255; (3) primo byte 0/110/1110/11110 indica la lunghezza, continuazioni 10; (4) esempio ñ U+00F1 → 11000011 10110001 = C3 B1; (5) autosincronizzante; (6) quasi tutto il web è UTF-8.

</details>

<details><summary>Che cos'è la normalizzazione Unicode e perché importa per la tokenizzazione?</summary>

Traccia: (1) lo stesso testo visibile può avere code point diversi: é = U+00E9 oppure e + U+0301; (2) stringhe diverse per Python (4 vs 5 code point), tipi diversi per un contatore, token diversi per un tokenizer; (3) NFC compone, NFD scompone; (4) un tokenizer preaddestrato va usato con la sua normalizzazione documentata; (5) cenno a NFKC (compatibilità, più aggressiva).

</details>

<details><summary>Perché non usare come token parole, morfemi o caratteri? Che cosa si fa in pratica?</summary>

Traccia: (1) parole: livello giusto ma mal definite tra lingue e infinite (Heaps); (2) morfemi: significativi ma difficili da segmentare, soprattutto nelle fusive; (3) caratteri: ben definiti ma poco significato e sequenze lunghe; (4) soluzione: token appresi dai dati (BPE, unigram LM), per lo più della taglia di parole e morfemi, a volte caratteri; (5) motivi per tokenizzare: unità fisse per replicabilità (perplexity), niente parole sconosciute.

</details>

<details><summary>Descrivi l'algoritmo di training BPE e applicalo al corpus del libro.</summary>

Traccia: (1) corpus pre-diviso in parole con spazio iniziale e conteggi; (2) vocabolario iniziale = caratteri (7); (3) ciclo k volte: coppia adiacente più frequente (pesata per frequenza), nuovo token, sostituzione; (4) corpus set new new renew reset renew: n e 4 (pari con e w), ne w 4, \_ r 3, \_r e 3, poi \_new, \_renew, se, set a 2; (5) 15 elementi dopo 8 merge; (6) induce il prefisso \_re senza morfologia; (7) output: vocabolario e lista ordinata dei merge.

</details>

<details><summary>Come funziona l'encoder BPE? Perché conta l'ordine dei merge?</summary>

Traccia: (1) la parola nuova si spezza in caratteri; (2) si applicano i merge nell'ordine appreso (rango), greedy, ognuno a tutte le occorrenze; (3) le frequenze del test non contano; (4) esempio \_newer → \_ ne w e r → \_ new e r → \_new e r; (5) l'ordine conta perché un merge presuppone i token creati dai precedenti e merge alternativi si contendono gli stessi caratteri; non è longest match; (6) \_renewest → \_renew e s t mostra parole nuove da token noti.

</details>

<details><summary>Che cosa cambia nel BPE reale: byte, pretokenizzazione, dimensioni?</summary>

Traccia: (1) scala: decine di migliaia di merge, vocabolari 50k-200k, parole comuni = 1 token; (2) BPE su byte UTF-8: 256 simboli base, mai token sconosciuti, riscopre le sequenze di 2-3 byte, sequenze illegali filtrate; (3) pretokenizzazione con regex: spazi, punteggiatura, clitici, numeri in gruppi di cifre; merge dentro i chunk; (4) esempi GPT-4o: 224123 → 224 | 123, Jane | 's ma she's intero, Any | how vs ·anyhow; (5) SuperBPE rilassa la pretokenizzazione.

</details>

<details><summary>Perché i tokenizer multilingue penalizzano le lingue diverse dall'inglese? Quali conseguenze?</summary>

Traccia: (1) dati di training dominati dall'inglese, quindi la maggior parte dei merge serve all'inglese; (2) esempio: ricetta inglese 19 token (14 parole, solo nutmeg diviso), spagnola 33 (16 parole, hondo → h + ondo, jugo, nuez, jengibre); italiano 16 vs inglese 10 dal notebook; (3) conseguenze: rappresentazioni peggiori, contesti più lunghi, costi maggiori di addestramento e d'uso; (4) lingue a basse risorse fino a caratteri singoli; (5) collegamento ai corpora: la lingua è situata.

</details>

<details><summary>Che cos'è SuperBPE?</summary>

Traccia: (1) BPE standard non attraversa i confini di parola per via della pretokenizzazione; (2) SuperBPE (Liu et al. 2025), e BoundlessBPE: primo stadio BPE normale, secondo stadio con merge attraverso spazi e punteggiatura; (3) esempio: By the way, I am a fan of the Milky Way. 13 token con BPE, 7 con SuperBPE (By the way, , I am, of the, Milky Way diventano token singoli); (4) vantaggio: meno token per lo stesso testo.

</details>

<details><summary>In che senso la lingua è situata? Che cos'è un datasheet?</summary>

Traccia: (1) 7.097 lingue, strumenti centrati sull'inglese; (2) varietà (African American English: iont, talmbout), code switching (spagnolo-inglese), genere, autore, epoca; (3) un corpus è un campione situato e il modello ne eredita i limiti; (4) datasheet (Gebru et al. 2020) / data statement (Bender et al. 2021): motivazione, situazione, varietà, demografia, raccolta, annotazione, distribuzione; (5) esempio: tweet italiani sui vaccini (esercizio 10).

</details>

### L3 · Elaborazione del testo

<details><summary>Che cos'è un'espressione regolare e a che cosa serve nell'elaborazione del testo?</summary>

Traccia: (1) notazione algebrica che descrive un insieme di stringhe (Kleene); (2) usi: ricerca (grep, editor, `re.search`), sostituzione (`re.sub`, ELIZA), tokenizzazione a regole e pretokenizzazione per BPE; (3) mattoni: quadre (un carattere da un insieme), contatori, ancore, disgiunzione con pipe, gruppi; (4) raw string in Python; (5) le regex si compilano in automi a stati finiti, quindi sono veloci: per questo si usano nella tokenizzazione, che gira su tutto il testo.

</details>

<details><summary>Spiega la differenza fra [catdog], cat|dog, gupp(y|ies) e guppy|ies, e la precedenza degli operatori.</summary>

Traccia: (1) quadre = un solo carattere fra c, a, t, d, o, g; (2) pipe = disgiunzione fra stringhe; (3) precedenza dalla più alta: parentesi, contatori, sequenze e ancore, disgiunzione; (4) quindi `guppy|ies` = guppy oppure ies, servono le parentesi per limitare la pipe al suffisso; (5) analogamente `the*` ripete solo la e e `the|any` non trova thany; (6) le parentesi servono anche per applicare un contatore a una sequenza: `(Column [0-9]+ +)*`.

</details>

<details><summary>Che cosa significa che le regex sono greedy? Come si ottiene il comportamento opposto?</summary>

Traccia: (1) fra le corrispondenze che partono nella stessa posizione si prende la più lunga: `[a-z]*` su once upon a time dà once, non il vuoto; (2) la ricerca parte comunque dalla posizione più a sinistra possibile; (3) operatori lazy `*?` e `+?`: consumano il meno possibile, secondo significato di `?`; (4) esempio pratico: estrarre il contenuto fra parentesi o tag, `\((.*)\)` contro `\((.*?)\)`; (5) un pattern che accetta il vuoto corrisponde sempre.

</details>

<details><summary>Che cosa sono falsi positivi e falsi negativi, precisione e recall? Usa l'esempio dell'articolo the.</summary>

Traccia: (1) `the` perde The a inizio frase: falso negativo; (2) `[tT]he` trova the dentro other e there: falsi positivi; (3) `\b[tT]he\b` con confini di parola; (4) precisione = ridurre i falsi positivi, $TP/(TP+FP)$; recall = ridurre i falsi negativi, $TP/(TP+FN)$; (5) sono antagonisti: allargare il pattern alza il recall e abbassa la precisione; (6) l'idea ritorna in ogni valutazione di sistemi NLP (capitolo 4).

</details>

<details><summary>Che cosa sono i gruppi di cattura, le backreference e i gruppi non catturanti?</summary>

Traccia: (1) le parentesi memorizzano la sottostringa trovata in registri numerati da sinistra a destra; (2) nel rimpiazzo `\1`, `\2`: date americane in europee con `\2-\1-\3`; (3) nel pattern stesso (backreference): `\b([A-Za-z]+)\s+\1\b` trova parole ripetute; (4) `(?:...)` raggruppa senza memorizzare, utile con i contatori: le 15 date, solo l'ultima nel gruppo 1; (5) collegamento con ELIZA, che riusa `\1` per rimandare le parole dell'utente.

</details>

<details><summary>Che cos'è un'asserzione lookahead? Spiega ^(?![tT])(\w+)\b.</summary>

Traccia: (1) controlla se un pattern compare dopo, senza consumare testo (larghezza zero, come ancore e `\b`); (2) `(?=...)` positivo, `(?!...)` negativo; (3) nell'esempio: inizio riga, controlla che il carattere non sia t/T, poi cattura la prima parola dallo stesso punto; (4) uso tipico: escludere un caso speciale; (5) nel pretokenizer di GPT-2 `\s+(?!\S)` lascia l'ultimo spazio alla parola successiva.

</details>

<details><summary>Come funziona ELIZA?</summary>

Traccia: (1) Weizenbaum 1966, simula uno psicoterapeuta rogersiano; (2) cascata di sostituzioni regex: input in maiuscolo, poi scambio dei pronomi (MY → YOUR, I'M → YOU ARE), poi regole che trasformano tutta la riga in risposta; (3) esempio `.* YOU ARE (DEPRESSED|SAD) .*` → I AM SORRY TO HEAR YOU ARE \1, e `.* ALWAYS .*` → CAN YOU THINK OF A SPECIFIC EXAMPLE; (4) nessuna comprensione, solo pattern; (5) l'ordine delle regole decide quale scatta.

</details>

<details><summary>Descrivi la regex di pretokenizzazione di GPT-2 e il suo output su We're 350 dogs! Um, lunch?</summary>

Traccia: (1) prima di BPE si divide il testo in chunk e i merge non attraversano i chunk; (2) libreria `regex` per `\p{L}` e `\p{N}` (proprietà Unicode); (3) cinque alternative in ordine: contrazioni, lettere, cifre, altra punteggiatura (ognuna con spazio iniziale opzionale), spazi con il lookahead; (4) output: We, 're, ·350, ·dogs, !, ·Um, ,, ·lunch, ?; (5) effetti: clitici staccati, punteggiatura separata, spazio incorporato all'inizio dei chunk; (6) stessi effetti del tokenizer GPT-4o (che in più spezza i numeri in gruppi di 3 cifre).

</details>

<details><summary>Come si contano le parole di un corpus con gli strumenti Unix? Che limiti ha questa tokenizzazione?</summary>

Traccia: (1) `tr -sc 'A-Za-z' '\n'`: complemento delle lettere in a capo, squeeze delle ripetizioni, una parola per riga; (2) `sort | uniq -c`: uniq conta solo righe adiacenti, quindi serve ordinare; (3) `tr A-Z a-z` per il case folding (72 AARON + 25 Aaron = 97 aaron); (4) `sort -n -r` per frequenza: in cima parole funzionali (the, and, i, to, of, a, you); (5) limiti: apostrofi (cat's → cat, s), trattini, numeri persi, lettere non ASCII, nessuna gestione dei clitici.

</details>

<details><summary>Quando servono token che siano parole? Quali sono i desiderata di una tokenizzazione a regole per l'inglese?</summary>

Traccia: (1) parsing (vuole parole grammaticali), linguistica e scienze sociali (token definito a priori); (2) metodo: standard + regole regex compilate in automi, perché deve essere veloce; (3) punteggiatura staccata ma interna tenuta (m.p.h., Ph.D., AT&T); (4) numeri e simboli interi (prezzi, date, 555,500.50; convenzioni diverse per lingua); URL, hashtag, email; (5) clitici espansi o separati; (6) multiparola (New York) con dizionari, legame con NER.

</details>

<details><summary>Che cos'è lo standard Penn Treebank? Tokenizza un esempio.</summary>

Traccia: (1) standard dei treebank del Linguistic Data Consortium; (2) clitici separati: doesn't → does + n't; (3) parole con trattino unite (Francisco-based); (4) tutta la punteggiatura separata, virgolette e dollaro compresi (\$ 10); (5) esempio della slide con le virgolette; (6) si implementa con regex in ordine, come il tokenizer NLTK `regexp_tokenize` (e l'ordine delle alternative conta: 82% viene spezzato perché `\w+` viene prima).

</details>

<details><summary>Perché la segmentazione in frasi non è banale in inglese?</summary>

Traccia: (1) indizi: . ? !; ? e ! quasi non ambigui; (2) il punto è ambiguo fra abbreviazione (Dr.) e fine frase, e può essere entrambe (Inc. a fine frase); (3) quindi si decide insieme alla tokenizzazione in parole; (4) dizionari di abbreviazioni fatti a mano o appresi (Kiss e Strunk 2006); (5) CoreNLP: la frase finisce su un . ! ? non già inglobato in un token, più eventuali virgolette o parentesi di chiusura.

</details>

<details><summary>Confronta case folding, lemmatizzazione e stemming.</summary>

Traccia: (1) tutti normalizzano le forme e riducono |V|; (2) case folding: tutto minuscolo, utile per IR e parlato, perde US/us, Fed/fed, dannoso per sentiment, MT, IE; (3) lemmatizzazione: forma di dizionario (am, are, is → be; voglio → volere) con analisi morfologica, dizionario e regole; gestisce gli irregolari; (4) stemming: taglia suffissi con regole, senza dizionario; Porter 1980, regole in cascata con condizioni (ATIONAL → ATE, ING → ε se c'è vocale, SSES → SS); veloce, stem non parole; (5) errori: over-stemming (organization/organ, university/universe) e under-stemming (European/Europe).

</details>

<details><summary>Definisci la distanza di edit minima e l'allineamento. Quanto vale fra intention ed execution?</summary>

Traccia: (1) minimo numero (costo) di inserimenti, cancellazioni, sostituzioni per trasformare una stringa nell'altra; (2) allineamento: corrispondenza fra simboli e stringa vuota, con lista d/s/i; (3) intention/execution: d i, s n→e, s t→x, i c, s n→u; (4) Levenshtein costi 1: 5; con sostituzione a 2 (equivale a vietare le sostituzioni): 8; (5) usi: correzione ortografica, WER nel parlato, allineamento di frasi in MT.

</details>

<details><summary>Perché si usa la programmazione dinamica per la distanza di edit? Scrivi la ricorrenza.</summary>

Traccia: (1) ricerca del cammino più breve fra stringhe: spazio enorme ma molti cammini arrivano alla stessa stringa; (2) principio di ottimalità: se exention è sul cammino ottimo, il tratto fino a exention è ottimo; (3) sottoproblemi = coppie di prefissi, $D[i,j]$; (4) casi base $D[i,0]=i$, $D[0,j]=j$; (5) ricorrenza: minimo fra sopra + del, sinistra + ins, diagonale + sub (0 se le lettere coincidono); (6) riempimento per righe, risposta $D[n,m]$, costo $O(nm)$; Bellman 1957, Wagner-Fischer 1974.

</details>

<details><summary>Come si ottiene un allineamento dalla tabella? Che cos'è il backtrace?</summary>

Traccia: (1) durante il riempimento si salvano i backpointer: ↑ cancellazione, ← inserimento, ↖ sostituzione o corrispondenza; in caso di pareggio più frecce; (2) backtrace dall'ultima cella a (0,0); (3) ogni cammino completo è un allineamento ottimo (per intention/execution 134 con sostituzione a 2, 7 con costi 1); (4) due celle del cammino nella stessa riga = inserimento, nella stessa colonna = cancellazione; (5) il cammino evidenziato ricostruisce l'allineamento d s s = i s = = = =.

</details>

<details><summary>Che cos'è il word error rate e che relazione ha con la distanza di edit? E Viterbi?</summary>

Traccia: (1) WER = (S + D + I) / N, con N parole del riferimento; (2) S, D, I si ottengono dall'allineamento di distanza minima fra le sequenze di parole (simboli = parole); (3) può superare il 100% per via degli inserimenti; (4) si usa per valutare il riconoscimento del parlato; (5) Viterbi: stessa struttura di programmazione dinamica, ma cerca l'allineamento di probabilità massima invece della distanza minima.

</details>

<details><summary>Perché the* non trova thethe, e che cosa trovano gupp(y|ies) e guppy|ies su guppies?</summary>

Traccia: (1) precedenza: parentesi, poi contatori, poi sequenza, poi disgiunzione; (2) il contatore si attacca al solo elemento precedente: `the*` = th + e\*, quindi la prima corrispondenza su *thethe* è *the*; per ripetere la parola serve `(the)*`; (3) la pipe separa sequenze intere: `guppy|ies` = guppy oppure ies, su *guppies* trova solo *ies*; con `gupp(y|ies)` la disgiunzione è ristretta al suffisso e trova tutta la parola; (4) metodo di lettura: parentesi, contatori, sequenze, pipe per ultima.

</details>

<details><summary>Il pretokenizer di GPT-2 su I'm 42 years old!! Don't ask.: quali chunk dà e perché !! resta insieme mentre Don't si spezza?</summary>

Traccia: (1) alternative provate in ordine in ogni posizione, ogni alternativa greedy; (2) chunk: I, 'm, ␣42, ␣years, ␣old, !!, ␣Don, 't, ␣ask, .; (3) lo spazio va con la parola o il numero che segue; (4) *!!*: la classe della punteggiatura ha il `+`, prende tutta la sequenza; (5) *Don't*: le lettere si fermano all'apostrofo, poi la contrazione `'t` vince perché è la prima alternativa; il taglio è Don + 't, diverso dal do + n't del Treebank; (6) con l'apostrofo tipografico le contrazioni non scattano.

</details>

<details><summary>Come si decide se un punto chiude una frase? Applica la regola a Dr. Rossi arrived at 9 a.m. He works for Acme Inc. The meeting lasted 2.5 hours.</summary>

Traccia: (1) ? e ! sono quasi sempre confini, il punto è ambiguo (abbreviazioni, decimali); (2) prima si decide se il punto appartiene al token (dizionario di abbreviazioni, scritto a mano o appreso, Punkt di Kiss e Strunk); (3) poi un token che finisce con il punto chiude la frase se la parola dopo ha la maiuscola e il token non è un titolo; (4) nell'esempio: Dr. solo token, a.m. e Inc. token e confine insieme, 2.5 solo token, l'ultimo punto solo confine: 3 frasi; (5) limite: *U.S. Army* viene spezzato per errore; CoreNLP deriva la segmentazione dalla tokenizzazione.

</details>

<details><summary>La scelta dei costi può cambiare la parola più vicina? Mostralo con drive, brief, divers.</summary>

Traccia: (1) due sistemi: Levenshtein a costi 1 e la variante con sostituzione a 2 (= cancellazione + inserimento); (2) a costi 1: drive-brief 3 (tre sostituzioni o sostituzione + cancellazione + inserimento), drive-divers 3 (cancella r, inserisci r e s): pareggio; (3) a sostituzione 2: brief sale a 4, divers resta 3 perché il suo allineamento non usa sostituzioni; (4) con sostituzione a 2 la distanza è $n + m - 2\,\text{LCS}$: 5+5-6 = 4, 5+6-8 = 3; (5) conclusione: la distanza dipende dal modello dei costi, e in pratica i pesi si scelgono in base agli errori reali (tastiera, fonetica).

</details>

### L4 · Modelli linguistici n-gram

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

### L5 · Smoothing ed entropia

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

### L6 · Regressione logistica

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

### L7 · Regressione logistica multinomiale e valutazione

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
