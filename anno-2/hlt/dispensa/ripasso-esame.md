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

**Regola della catena (caratteri)** ([L16](L16-laboratorio-dagli-n-gram-a-gpt.md))

$$
P(x_1,\ldots,x_T)=\prod_{t=1}^{T}P(x_t\mid x_{<t})
$$

Vale per ogni modello del laboratorio; i modelli differiscono solo nel modo di stimare $P(x_t\mid x_{&lt;t})$.

**N-gram di caratteri (Markov)** ([L16](L16-laboratorio-dagli-n-gram-a-gpt.md))

$$
P(x_t\mid x_{<t})\approx P(x_t\mid x_{t-n+1},\ldots,x_{t-1})
$$

Ordine $n$ = storia di $n-1$ caratteri; $n=2$ bigram: $P(x_t\mid x_{t-1})$.

**Stima MLE bigram** ([L16](L16-laboratorio-dagli-n-gram-a-gpt.md))

$$
P(b\mid a)=\frac{C(a\,b)}{C(a)}
$$

$C(a)$ = numero di bigram che cominciano con $a$. Nel lab: $P(o\mid t)=3800/20092=0{,}189$; $P(u\mid q)=1$.

**Contesti possibili di un n-gram** ([L16](L16-laboratorio-dagli-n-gram-a-gpt.md))

$$
\#\text{contesti}\le V^{h},\qquad \log_{10}V^h=h\log_{10}V
$$

$h=n-1$. Con $V=77$: $h=8$ dà $10^{15{,}1}$, $h=64$ dà $10^{120{,}7}$. Il muro degli n-gram.

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

**Accuracy del tagging** ([L8, slide 81](L08-sequence-labelling-pos-tagging-e-ner.md#p-81))

$$
\text{accuracy} = \frac{\#\text{token con tag corretto}}{\#\text{token}}
$$

Misura standard per il PoS tagging.

**Precision, recall, F1 sulle entità** ([L8, slide 81](L08-sequence-labelling-pos-tagging-e-ner.md#p-81))

$$
P = \frac{\#\text{span corretti}}{\#\text{span predetti}},\quad R = \frac{\#\text{span corretti}}{\#\text{span gold}},\quad F_1 = \frac{2PR}{P + R}
$$

Uno span è corretto solo con confini e tipo identici al gold; un errore di confine vale un FP e un FN.

**Precision, recall e F1 sugli span (NER)** ([L9](L09-laboratorio-nltk-e-spacy.md))

$$
P = \frac{|G\cap S|}{|S|},\quad R = \frac{|G\cap S|}{|G|},\quad F_1 = \frac{2PR}{P+R}
$$

$G$ = insieme degli span gold $(\text{start}, \text{end}, \text{tipo})$, $S$ = span predetti; match esatto di confini e tipo. Un errore di confine costa un falso positivo e un falso negativo. 0 per convenzione se un denominatore è nullo.

**Correlazione di rango di Spearman** ([L11, slide 56](L11-embedding-word2vec.md#p-56))

$$
\rho = 1 - \frac{6\sum_i d_i^2}{n(n^2-1)}
$$

$d_i$ = differenza fra il rango umano e il rango del modello della coppia $i$, $n$ coppie (senza pareggi). Esercizio 12: $\rho = 1 - 48/120 = 0{,}60$.

**Correlazione di Spearman (con i pari)** ([L12](L12-laboratorio-word-embedding.md))

$$
\rho=\frac{\sum_i(a_i-\bar a)(b_i-\bar b)}{\sqrt{\sum_i(a_i-\bar a)^2}\sqrt{\sum_i(b_i-\bar b)^2}},\qquad a_i=\text{rango}(x_i),\ b_i=\text{rango}(y_i)
$$

Pearson sui ranghi; i valori pari ricevono la media dei ranghi occupati. La scorciatoia $1-\frac{6\sum d_i^2}{n(n^2-1)}$ vale solo senza pari. Esempio: $[1..5]$ contro $[5,6,7,8,7]$ → 0,8208.

**Cross-entropy held-out (nats)** ([L16](L16-laboratorio-dagli-n-gram-a-gpt.md))

$$
H=-\frac{1}{N}\sum_{i=1}^{N}\ln P(x_i\mid \text{context}_i)
$$

Media del log-probabilità negativo dei caratteri veri. 5-gram lisciato: 1,767 nats; tiny GPT a 500 passi: 2,226.

**Perplexity e conversione bit/nats** ([L16](L16-laboratorio-dagli-n-gram-a-gpt.md))

$$
\text{PPL}=e^{H_\text{nat}}=2^{H_\text{bit}},\qquad H_\text{bit}=\frac{H_\text{nat}}{\ln 2}
$$

Stesso numero in qualunque base. 5-gram: PPL 5,85 (2,55 bit/carattere).

**Surprisal** ([L16](L16-laboratorio-dagli-n-gram-a-gpt.md))

$$
s(x)=-\log_2 P(x\mid\text{context})
$$

In bit: 0 = certo, 1 = moneta, $\log_2 77=6{,}27$ = uniforme sui 77 caratteri. La media delle surprisal è la CE in bit.

**Baseline uniforme** ([L16](L16-laboratorio-dagli-n-gram-a-gpt.md))

$$
H_\text{unif}=-\ln\frac1V=\ln V,\qquad \text{PPL}_\text{unif}=V
$$

$\ln 77=4{,}344$ nats, PPL 77: la loss iniziale di una rete inizializzata con pesi piccoli (4,377 osservata).

**Likelihood di un testo** ([L17, slide 54](L17-pretraining-dei-modelli-linguistici.md#p-54))

$$
\text{likelihood}(w_{1:T}) = \prod_{i=1}^{T}P(w_i\mid w_{<i})
$$

Prodotto delle probabilità dei token; decresce con la lunghezza (Eq. 7.56).

**Perplexity** ([L17, slide 54](L17-pretraining-dei-modelli-linguistici.md#p-54))

$$
\mathrm{PP}(w_{1:T}) = P(w_{1:T})^{-1/T} = \left(\prod_{t=1}^{T}P(w_t\mid w_{<t})^{-1}\right)^{1/T}
$$

Inverso della probabilità normalizzato per la lunghezza (Eq. 7.57). Più bassa è meglio. Dipende dal tokenizzatore.

**Perplexity e cross-entropy** ([L17, slide 55](L17-pretraining-dei-modelli-linguistici.md#p-55))

$$
\mathrm{PP} = \exp\left(\frac1T\sum_{t=1}^{T}-\ln P(w_t\mid w_{<t})\right) = 2^{H_{bit}}
$$

Esponenziale della loss media in nat (Eq. 7.58); stesso valore con log in base 2. Esempio: loss 0,853, perplexity 2,35.

**Accuratezza sul sottoinsieme pulito** ([L17, slide 60](L17-pretraining-dei-modelli-linguistici.md#p-60))

$$
\text{acc}_{pulito} = \frac{\text{corrette} - \text{corrette contaminate}}{\text{totale} - \text{contaminate}}
$$

Esempio della lezione: $(90-30)/(100-30) = 85{,}7\%$ contro il 90% complessivo.

**Win rate** ([L19, slide 32](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-32))

$$
\text{win rate} = \frac{W + T/2}{W + L + T}
$$

Vittorie, sconfitte, pareggi nei confronti a coppie fra due modelli. Non nelle slide. 110, 50, 40: 0,65.

**pass@k** ([L19, slide 41](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-41))

$$
\text{pass@}k = 1 - \binom{n-c}{k}\Big/\binom{n}{k}
$$

Probabilità che almeno una di $k$ risposte sia corretta, stimata da $n$ campioni con $c$ corretti. Non nelle slide. $n = 8$, $c = 2$, $k = 4$: 0,786.

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

**Add-α (add-k)** ([L16](L16-laboratorio-dagli-n-gram-a-gpt.md))

$$
P(b\mid \text{ctx})=\frac{C(\text{ctx}\,b)+\alpha}{C(\text{ctx})+\alpha V}
$$

$\alpha=1$ Laplace, $\alpha=0$ MLE; contesto mai visto: $1/V$. Nel lab $\alpha=0{,}1$, $V=77$, quindi $\alpha V=7{,}7$.

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

### Sequence labelling

**Baseline most-frequent-tag** ([L8, slide 20](L08-sequence-labelling-pos-tagging-e-ner.md#p-20))

$$
\hat t(w) = \operatorname*{argmax}_{t} C(w, t)
$$

Ogni parola riceve il tag con cui compare più spesso nel training (NN se sconosciuta). Circa 92% sul WSJ, contro ~97% dei tagger supervisionati.

**Numero di tag degli schemi BIO** ([L8, slide 66](L08-sequence-labelling-pos-tagging-e-ner.md#p-66))

$$
|\text{IO}| = n + 1,\qquad |\text{BIO}| = 2n + 1,\qquad |\text{BIOES}| = 4n + 1
$$

$n$ = tipi di entità. Con PER, LOC, ORG, GPE: 5, 9, 17.

### Hidden Markov model

**Assunzione di Markov** ([L8, slide 24](L08-sequence-labelling-pos-tagging-e-ner.md#p-24))

$$
P(q_i = a\mid q_1\dots q_{i-1}) = P(q_i = a\mid q_{i-1})
$$

Per predire lo stato successivo conta solo lo stato corrente. Sui tag: modello bigram dei tag.

**Matrice di transizione** ([L8, slide 27](L08-sequence-labelling-pos-tagging-e-ner.md#p-27))

$$
a_{ij} = P(q_t = j\mid q_{t-1} = i),\qquad \sum_{j=1}^{N} a_{ij} = 1\ \ \forall i
$$

Riga = stato precedente, colonna = stato successivo; ogni riga è una distribuzione.

**Distribuzione iniziale** ([L8, slide 28](L08-sequence-labelling-pos-tagging-e-ner.md#p-28))

$$
\pi_i = P(q_1 = i),\qquad \sum_{i=1}^{N}\pi_i = 1
$$

Nei tagger coincide con la riga <s> di $A$: $\pi_j = P(t_1 = j\mid\langle s\rangle)$.

**Probabilità di una sequenza in una catena di Markov** ([L8, slide 29](L08-sequence-labelling-pos-tagging-e-ner.md#p-29))

$$
P(q_1\dots q_T) = \pi_{q_1}\prod_{t=2}^{T} a_{q_{t-1}q_t}
$$

Esempio: $P(\text{hot hot hot hot}) = 0{,}1\cdot0{,}6^3 = 0{,}0216$.

**Indipendenza delle osservazioni** ([L8, slide 33](L08-sequence-labelling-pos-tagging-e-ner.md#p-33))

$$
P(o_i\mid q_1,\dots,q_T,\ o_1,\dots,o_T) = P(o_i\mid q_i)
$$

Un'osservazione dipende solo dallo stato che l'ha generata. Emissione: $b_i(o_t) = P(o_t\mid q_i)$, $\sum_{w\in V} b_i(w) = 1$.

**Probabilità congiunta HMM** ([L8, slide 34](L08-sequence-labelling-pos-tagging-e-ner.md#p-34))

$$
P(w_{1:n}, t_{1:n}) = \prod_{i=1}^{n} P(t_i\mid t_{i-1})\,P(w_i\mid t_i),\quad t_0 = \langle s\rangle
$$

Conseguenza delle due assunzioni: prodotto di transizioni ed emissioni.

**MLE delle transizioni** ([L8, slide 35](L08-sequence-labelling-pos-tagging-e-ner.md#p-35))

$$
P(t_i\mid t_{i-1}) = \frac{C(t_{i-1}, t_i)}{C(t_{i-1})}
$$

Esempio WSJ: $P(\text{VB}\mid\text{MD}) = 10471/13124 = 0{,}80$.

**MLE delle emissioni** ([L8, slide 35](L08-sequence-labelling-pos-tagging-e-ner.md#p-35))

$$
P(w_i\mid t_i) = \frac{C(t_i, w_i)}{C(t_i)}
$$

Esempio: $P(\textit{will}\mid\text{MD}) = 4046/13124 = 0{,}31$. Non va confusa con la posterior $P(\text{MD}\mid\textit{will})$.

**Obiettivo della decodifica** ([L8, slide 38](L08-sequence-labelling-pos-tagging-e-ner.md#p-38))

$$
\hat t_{1:n} = \operatorname*{argmax}_{t_1\dots t_n} P(t_1\dots t_n\mid w_1\dots w_n)
$$

La sequenza di tag più probabile date le parole (Eq. 18.12).

**Decodifica con Bayes** ([L8, slide 39](L08-sequence-labelling-pos-tagging-e-ner.md#p-39))

$$
\hat t_{1:n} = \operatorname*{argmax}_{t_{1:n}} P(w_{1:n}\mid t_{1:n})\,P(t_{1:n})
$$

Bayes più eliminazione del denominatore $P(w_{1:n})$, costante rispetto ai tag.

**Tagger HMM bigram** ([L8, slide 42](L08-sequence-labelling-pos-tagging-e-ner.md#p-42))

$$
\hat t_{1:n} \approx \operatorname*{argmax}_{t_1\dots t_n}\prod_{i=1}^{n} P(w_i\mid t_i)\,P(t_i\mid t_{i-1})
$$

Emissione $B$ per transizione $A$ (Eq. 18.17), dopo le approssimazioni di indipendenza delle osservazioni e bigram.

### Viterbi

**Cella di Viterbi** ([L8, slide 46](L08-sequence-labelling-pos-tagging-e-ner.md#p-46))

$$
v_t(j) = \max_{q_1,\dots,q_{t-1}} P(q_1\dots q_{t-1},\ o_1\dots o_t,\ q_t = j\mid\lambda)
$$

Probabilità del miglior cammino che finisce nello stato $j$ dopo $t$ osservazioni.

**Ricorsione di Viterbi** ([L8, slide 46](L08-sequence-labelling-pos-tagging-e-ner.md#p-46))

$$
v_t(j) = \max_{i=1}^{N} v_{t-1}(i)\,a_{ij}\,b_j(o_t),\qquad bt_t(j) = \operatorname*{argmax}_{i} v_{t-1}(i)\,a_{ij}
$$

Cammino precedente × transizione × emissione; il backpointer registra il predecessore migliore.

**Inizializzazione e terminazione** ([L8, slide 47](L08-sequence-labelling-pos-tagging-e-ner.md#p-47))

$$
v_1(j) = \pi_j\,b_j(o_1);\qquad P^* = \max_{j} v_T(j),\quad q_T^* = \operatorname*{argmax}_j v_T(j)
$$

Poi il backtrace: $q_{t-1}^* = bt_t(q_t^*)$.

**Viterbi in log-spazio** ([L8, slide 47](L08-sequence-labelling-pos-tagging-e-ner.md#p-47))

$$
\log v_t(j) = \max_i\big[\log v_{t-1}(i) + \log a_{ij}\big] + \log b_j(o_t)
$$

Evita l'underflow; il max non cambia perché il log è monotono.

**Complessità** ([L8, slide 53](L08-sequence-labelling-pos-tagging-e-ner.md#p-53))

$$
\text{forza bruta: } O(N^T)\qquad \text{Viterbi: } O(T\,N^2)\ \text{tempo},\ O(T\,N)\ \text{memoria}
$$

$N$ = tag, $T$ (o $L$) = lunghezza. 45 tag, 20 parole: $20\cdot45^2 = 40.500$ contro $45^{20}\approx1{,}2\cdot10^{33}$.

### Conditional random field

**CRF** ([L8, slide 72](L08-sequence-labelling-pos-tagging-e-ner.md#p-72))

$$
P(Y\mid X) = \frac{1}{Z(X)}\exp\Big(\sum_{k=1}^{K} w_k F_k(X, Y)\Big)
$$

Modello log-lineare su sequenze intere: una softmax sulle sequenze di tag.

**Normalizzatore del CRF** ([L8, slide 72](L08-sequence-labelling-pos-tagging-e-ner.md#p-72))

$$
Z(X) = \sum_{Y'\in\mathcal Y}\exp\Big(\sum_{k=1}^{K} w_k F_k(X, Y')\Big)
$$

Somma su tutte le $N^n$ sequenze; si calcola con forward-backward, non per enumerazione.

**Feature globali come somma di locali** ([L8, slide 73](L08-sequence-labelling-pos-tagging-e-ner.md#p-73))

$$
F_k(X, Y) = \sum_{i=1}^{n} f_k(y_{i-1}, y_i, X, i)
$$

Nel CRF lineare la feature locale vede solo $y_i$, $y_{i-1}$, tutto $X$ e la posizione $i$. $F_k$ conta quante volte scatta $f_k$.

**Decodifica CRF** ([L8, slide 79](L08-sequence-labelling-pos-tagging-e-ner.md#p-79))

$$
\hat Y = \operatorname*{argmax}_{Y\in\mathcal Y}\sum_{i=1}^{n}\sum_{k=1}^{K} w_k\,f_k(y_{i-1}, y_i, X, i)
$$

Exp e $Z(X)$ spariscono dall'argmax.

**Viterbi per il CRF** ([L8, slide 80](L08-sequence-labelling-pos-tagging-e-ner.md#p-80))

$$
v_t(j) = \max_{i=1}^{N}\Big[v_{t-1}(i) + \sum_{k=1}^{K} w_k\,f_k(y_{t-1} = i, y_t = j, X, t)\Big]
$$

Come per l'HMM, ma con somme di pesi al posto di prodotti di probabilità (log-spazio).

### Collocazioni

**Pointwise mutual information di un bigramma** ([L9](L09-laboratorio-nltk-e-spacy.md))

$$
\text{PMI}(w_1,w_2) = \log_2\frac{P(w_1w_2)}{P(w_1)\,P(w_2)} = \log_2\frac{P(w_2\mid w_1)}{P(w_2)}
$$

Quanto più spesso del caso le due parole compaiono in sequenza: 0 se indipendenti, positiva se si attraggono, negativa se si evitano. In bit (logaritmo in base 2).

**PMI dai conteggi (stime MLE)** ([L9](L09-laboratorio-nltk-e-spacy.md))

$$
\text{PMI}(w_1,w_2) = \log_2\frac{C(w_1w_2)\cdot N}{C(w_1)\,C(w_2)}
$$

Con $P(w_2\mid w_1) = C(w_1w_2)/C(w_1)$ e $P(w_2) = C(w_2)/N$, $N$ = numero di token. Esempio: *Talking Cricket* (18, 19, 34, $N = 53.332$) = 10,54 bit; *of the* = 2,43 bit.

**PMI massima con conteggi unitari** ([L9](L09-laboratorio-nltk-e-spacy.md))

$$
C(w_1w_2) = C(w_1) = C(w_2) = 1 \;\Rightarrow\; \text{PMI} = \log_2 N
$$

Il valore più alto possibile: per questo la PMI va usata con una soglia di frequenza. Su Pinocchio $\log_2 53332 = 15{,}70$, raggiunto da 130 bigrammi senza filtri.

### Rappresentazione del testo

**Bag of words binario e a conteggi** ([L9](L09-laboratorio-nltk-e-spacy.md))

$$
x_j = \mathbb 1[w_j \in d] \quad\text{oppure}\quad x_j = C_d(w_j),\qquad \mathbf x\in\mathbb R^{|V|}
$$

Una feature per parola del vocabolario $V$; vettore di lunghezza fissa e sparso; l'ordine delle parole si perde.

**Similarità di Jaccard fra insiemi di n-grammi** ([L9](L09-laboratorio-nltk-e-spacy.md))

$$
J(A,B) = \frac{|A\cap B|}{|A\cup B|}
$$

Con gli insiemi di trigrammi di caratteri: $J(\textit{rainbow}, \textit{rainbaw}) = 3/7 = 0{,}43$, $J(\textit{rainbow}, \textit{rainbows}) = 5/6$. Una parola di $L$ caratteri ha $L-n+1$ n-grammi (senza padding).

**Media degli embedding di un documento** ([L12](L12-laboratorio-word-embedding.md))

$$
\mathbf x_d=\frac{1}{|d|}\sum_{w\in d}\mathbf e_w
$$

Solo parole nel vocabolario dell'embedding; vettore nullo se nessuna. Perde ordine e negazione: *The movie is good* e *The movie is not good* hanno coseno 0,991.

**tf-idf del libro** ([L12](L12-laboratorio-word-embedding.md))

$$
\text{tf}_{t,d}=\begin{cases}1+\log_{10}\text{count}(t,d)&\text{count}>0\\0&\text{altrimenti}\end{cases}\qquad \text{idf}_t=\log_{10}\frac{N}{\text{df}_t}\qquad \text{tf-idf}=\text{tf}_{t,d}\cdot\text{idf}_t
$$

$N$ = numero di documenti (qui 1.600 recensioni di training). 10 occorrenze → tf 2; un termine presente in tutti i documenti → idf 0.

**tf-idf di scikit-learn (sublinear_tf=True)** ([L12](L12-laboratorio-word-embedding.md))

$$
\text{tf}=1+\ln\text{count}(t,d)\qquad \text{idf}_t=\ln\frac{1+N}{1+\text{df}_t}+1\qquad \mathbf x_d\leftarrow\frac{\mathbf x_d}{\|\mathbf x_d\|_2}
$$

Logaritmo naturale, idf smussata (un termine ovunque ha idf 1), normalizzazione L2 di ogni documento.

### Sentiment

**Compound di VADER** ([L9](L09-laboratorio-nltk-e-spacy.md))

$$
\text{compound} = \frac{s}{\sqrt{s^2+\alpha}},\qquad \alpha = 15
$$

$s$ = somma delle valenze corrette dalle regole (più 0,292 per ogni !, al massimo 4). Valori in $(-1, 1)$; soglia convenzionale $\pm 0{,}05$. Esempio: *good* $1{,}9/\sqrt{18{,}61} = 0{,}4404$. Non è una probabilità.

**Regole di VADER (costanti)** ([L9](L09-laboratorio-nltk-e-spacy.md))

$$
v_{\text{neg}} = -0{,}74\,v,\quad v_{\text{very}} = v \pm 0{,}293,\quad v_{\text{CAPS}} = v \pm 0{,}733,\quad v_{\text{prima di but}} = 0{,}5\,v,\quad v_{\text{dopo but}} = 1{,}5\,v
$$

Negazione nelle 3 parole precedenti; intensificatore e maiuscole aumentano il modulo (attenuatori come *kind of* lo diminuiscono); *but* sposta il peso verso la parte finale.

**Punteggi neg, neu, pos di VADER** ([L9](L09-laboratorio-nltk-e-spacy.md))

$$
\text{pos} = \frac{\sum_{v_i>0}(v_i+1)}{T},\quad \text{neg} = \frac{\sum_{v_i<0}(|v_i|+1)}{T},\quad \text{neu} = \frac{\#\{v_i=0\}}{T}
$$

$T$ = somma dei tre numeratori; la spinta dei punti esclamativi si aggiunge al lato più forte. Ogni parola neutra pesa 1, ogni parola con sentiment $1+|v_i|$: sono quote di intensità, non percentuali di testo.

### PoS tagging

**Ambiguità dei tag su tipi e token** ([L9](L09-laboratorio-nltk-e-spacy.md))

$$
\text{amb}_{\text{tipi}} = \frac{|\{w : |T(w)|\ge 2\}|}{|V|},\qquad \text{amb}_{\text{token}} = \frac{\sum_{w: |T(w)|\ge 2} C(w)}{N}
$$

$T(w)$ = insieme dei tag con cui compare $w$. WSJ completo: 14% e 55% (Fig. 18.4); campione NLTK: 9,9% e 36,5%.

**Baseline most-frequent-tag** ([L9](L09-laboratorio-nltk-e-spacy.md))

$$
\hat t(w) = \begin{cases}\arg\max_t C(w, t) & w \text{ visto nel training}\\ \text{NN} & \text{altrimenti}\end{cases}
$$

Accuratezza circa 92% sul WSJ completo (libro); 87,0% sul campione NLTK (19% sulle parole ignote), 92,8% con regole su suffissi e maiuscole per le ignote.

### Semantica vettoriale

**Prodotto scalare** ([L10, slide 24](L10-semantica-vettoriale.md#p-24))

$$
\mathbf v\cdot\mathbf w = \sum_{i=1}^{N} v_iw_i
$$

Alto se i due vettori hanno valori grandi nelle stesse dimensioni, 0 se ortogonali. Non invariante alla scala: $\text{dot}(c\mathbf v,\mathbf w) = c\,\text{dot}(\mathbf v,\mathbf w)$. Esempio $[1, 3]\cdot[3;\ 1{,}6] = 7{,}8$.

**Lunghezza (norma) di un vettore** ([L10, slide 25](L10-semantica-vettoriale.md#p-25))

$$
|\mathbf v| = \sqrt{\sum_{i=1}^{N} v_i^2}
$$

Per i vettori di conteggi cresce con la frequenza della parola (bias della frequenza). Vettore unitario: $\mathbf v/|\mathbf v|$.

**Coseno come prodotto scalare normalizzato** ([L10, slide 26](L10-semantica-vettoriale.md#p-26))

$$
\mathbf a\cdot\mathbf b = |\mathbf a||\mathbf b|\cos\theta
$$

Da cui $\cos\theta = \mathbf a\cdot\mathbf b/(|\mathbf a||\mathbf b|)$; per vettori unitari il prodotto scalare è il coseno.

**Similarità coseno** ([L10, slide 27](L10-semantica-vettoriale.md#p-27))

$$
\text{cosine}(\mathbf v,\mathbf w) = \frac{\mathbf v\cdot\mathbf w}{|\mathbf v||\mathbf w|} = \frac{\sum_i v_iw_i}{\sqrt{\sum_i v_i^2}\sqrt{\sum_i w_i^2}}
$$

Intervallo $[-1, 1]$; $[0, 1]$ per conteggi non negativi. Invariante alla scala: $\cos(c\mathbf v,\mathbf w) = \cos(\mathbf v,\mathbf w)$ per $c&gt;0$. Esempi: cos(digital, information) = 0,996, cos(cherry, information) = 0,018.

**Distanza euclidea** ([L10, slide 7](L10-semantica-vettoriale.md#p-7))

$$
d(\mathbf v,\mathbf w) = |\mathbf v-\mathbf w| = \sqrt{\sum_i (v_i-w_i)^2}
$$

Misura alternativa (esercizio 2): adatta a punti su scale con un punto neutro, come valence/arousal/dominance di Osgood; dipende dalla lunghezza, quindi non adatta ai conteggi grezzi.

**Similarità coseno** ([L12](L12-laboratorio-word-embedding.md))

$$
\cos(\mathbf u,\mathbf v)=\frac{\mathbf u\cdot\mathbf v}{\|\mathbf u\|\,\|\mathbf v\|}=\frac{\sum_i u_iv_i}{\sqrt{\sum_i u_i^2}\sqrt{\sum_i v_i^2}}
$$

Fra 0 e 1 per vettori di conteggi, fra −1 e 1 per embedding densi. Nel lab: *pizza*-*cheese* $= 1/\sqrt2 = 0{,}707$ sul corpus giocattolo.

**Coppie della matrice parola-contesto** ([L12](L12-laboratorio-word-embedding.md))

$$
N=\sum_{w}\sum_{c}C(w,c)
$$

Numero di coppie (target, contesto) osservate. Con finestra $\pm1$ una frase di 3 parole dà 4 coppie: le 8 frasi del corpus giocattolo danno $N = 32$ da 24 token.

### Information retrieval

**Term frequency** ([L10, slide 39](L10-semantica-vettoriale.md#p-39))

$$
\text{tf}_{t,d} = \begin{cases}1+\log_{10}\text{count}(t,d) & \text{count}(t,d)>0\\ 0 & \text{altrimenti}\end{cases}
$$

Ogni fattore 10 aggiunge 1: count 1, 10, 100, 1000 → tf 1, 2, 3, 4. Variante delle edizioni precedenti: $\log_{10}(\text{count}+1)$.

**Inverse document frequency** ([L10, slide 41](L10-semantica-vettoriale.md#p-41))

$$
\text{idf}_t = \log_{10}\frac{N}{\text{df}_t}
$$

$N$ = documenti della collezione, $\text{df}_t$ = documenti che contengono $t$. 0 per un termine presente ovunque. Shakespeare ($N = 37$): Romeo 1,57, battle 0,246, fool 0,012, good 0.

**tf-idf** ([L10, slide 43](L10-semantica-vettoriale.md#p-43))

$$
\text{tf-idf}(t,d) = w_{t,d} = \text{tf}_{t,d}\cdot\text{idf}_t
$$

Alto per i termini frequenti nel documento e rari nella collezione. battle in Julius Caesar: $(1+\log_{10}7)\cdot0{,}246 = 0{,}454$.

**Punteggio di un documento (tf-idf cosine)** ([L10, slide 46](L10-semantica-vettoriale.md#p-46))

$$
\text{score}(q,d) = \cos(\mathbf q,\mathbf d) = \frac{\mathbf q}{|\mathbf q|}\cdot\frac{\mathbf d}{|\mathbf d|} = \sum_{t\in q}\frac{\text{tf-idf}(t,q)}{|\mathbf q|}\cdot\frac{\text{tf-idf}(t,d)}{|\mathbf d|}
$$

La query è pesata come un documento. Esempio del libro: query *sweet love*, Doc 1 0,747, Doc 2 0,078.

**BM25 (approfondimento)** ([L10, slide 38](L10-semantica-vettoriale.md#p-38))

$$
\sum_{t\in q}\log\frac{N}{\text{df}_t}\cdot\frac{\text{tf}_{t,d}}{k\left(1-b+b\frac{|d|}{|d_{avg}|}\right)+\text{tf}_{t,d}}
$$

Variante di tf-idf citata nella slide 38 (libro §11.1.3): $k$ controlla la saturazione della frequenza ($k = 0$: solo presenza), $b$ la normalizzazione per la lunghezza. Tipici $k\in[1{,}2;\ 2]$, $b = 0{,}75$.

### Associazione (PMI)

**Pointwise mutual information** ([L10, slide 48](L10-semantica-vettoriale.md#p-48))

$$
\text{PMI}(w,c) = \log_2\frac{P(w,c)}{P(w)P(c)}
$$

Osservato contro atteso sotto indipendenza, in bit. 0 = come il caso, positiva = più del caso, negativa = meno. cherry-pie 4,38; information-data 0,094; cherry-computer −6,70.

**Positive PMI** ([L10, slide 50](L10-semantica-vettoriale.md#p-50))

$$
\text{PPMI}(w,c) = \max\left(\log_2\frac{P(w,c)}{P(w)P(c)},\ 0\right)
$$

I valori negativi (inaffidabili) e i $-\infty$ delle coppie mai viste diventano 0 (Niwa e Nitta, 1994).

**Probabilità da una matrice di conteggi** ([L10, slide 52](L10-semantica-vettoriale.md#p-52))

$$
p_{ij} = \frac{f_{ij}}{\sum_{i'}\sum_{j'}f_{i'j'}},\quad p_{i*} = \frac{\sum_j f_{ij}}{\sum_{i'}\sum_{j'}f_{i'j'}},\quad p_{*j} = \frac{\sum_i f_{ij}}{\sum_{i'}\sum_{j'}f_{i'j'}}
$$

Congiunta e marginali di parola (riga) e contesto (colonna), stime di massima verosimiglianza. Nell'esempio $N = 11.716$.

**PPMI di una cella** ([L10, slide 53](L10-semantica-vettoriale.md#p-53))

$$
\text{PPMI}_{ij} = \max\left(\log_2\frac{p_{ij}}{p_{i*}p_{*j}},\ 0\right) = \max\left(\log_2\frac{f_{ij}\,N}{f_{i*}\,f_{*j}},\ 0\right)
$$

La seconda forma (conteggio osservato su conteggio atteso $f_{i*}f_{*j}/N$) è la più comoda a mano ed evita gli errori di arrotondamento.

**PPMI con α (contesti)** ([L10, slide 57](L10-semantica-vettoriale.md#p-57))

$$
\text{PPMI}_\alpha(w,c) = \max\left(\log_2\frac{P(w,c)}{P(w)P_\alpha(c)},\ 0\right),\qquad P_\alpha(c) = \frac{\text{count}(c)^\alpha}{\sum_{c'}\text{count}(c')^\alpha}
$$

Levy et al. (2015), α = 0,75: i contesti rari ricevono più probabilità e quindi PMI più bassa. $P = 0{,}99/0{,}01$ diventa $0{,}97/0{,}03$.

**Mutual information (approfondimento)** ([L10, slide 48](L10-semantica-vettoriale.md#p-48))

$$
I(X;Y) = \sum_{x,y}P(x,y)\log_2\frac{P(x,y)}{P(x)P(y)}
$$

Media della PMI su tutte le coppie; sempre $\ge 0$, nulla solo per variabili indipendenti. La formula fra due eventi della slide 48 è la versione puntuale.

**Probabilità dalla matrice di co-occorrenza** ([L12](L12-laboratorio-word-embedding.md))

$$
P(w,c)=\frac{C(w,c)}{N}\qquad P(w)=\frac{\sum_c C(w,c)}{N}\qquad P(c)=\frac{\sum_w C(w,c)}{N}
$$

Tutte sulle stesse $N$ coppie: $P(w)$ è la somma di riga, $P(c)$ quella di colonna (non la frequenza della parola).

**PPMI di una cella dai conteggi** ([L12](L12-laboratorio-word-embedding.md))

$$
\text{PPMI}(w,c)=\max\left(\log_2\frac{C(w,c)\,N}{\sum_{c'}C(w,c')\,\sum_{w'}C(w',c)},\ 0\right)
$$

La forma calcolata da `ppmi` nel notebook; celle vuote a 0. Esempio: PPMI(*cats*, *the*) $= \log_2\frac{2\cdot60}{4\cdot20} = 0{,}585$.

### Word2vec

**Probabilità che c sia un contesto di w** ([L11, slide 15](L11-embedding-word2vec.md#p-15))

$$
P(+\mid w,c) = \sigma(\mathbf c\cdot\mathbf w) = \frac{1}{1+\exp(-\mathbf c\cdot\mathbf w)}
$$

Eq. 5.15. $\mathbf w$ dalla matrice dei target $W$, $\mathbf c$ da quella dei contesti $C$. Esempio: apricot·jam = 1, $\sigma(1) = 0{,}73$.

**Probabilità che c non sia un contesto** ([L11, slide 16](L11-embedding-word2vec.md#p-16))

$$
P(-\mid w,c) = 1-P(+\mid w,c) = \sigma(-\mathbf c\cdot\mathbf w) = \frac{1}{1+\exp(\mathbf c\cdot\mathbf w)}
$$

Eq. 5.12 e 5.16. Le due probabilità sommano a 1; si usa $1-\sigma(x) = \sigma(-x)$.

**Sigmoide e sua derivata** ([L11, slide 15](L11-embedding-word2vec.md#p-15))

$$
\sigma(x) = \frac{1}{1+e^{-x}}\qquad \sigma'(x) = \sigma(x)(1-\sigma(x))\qquad \frac{d}{dx}\log\sigma(x) = 1-\sigma(x)
$$

Valori utili: $\sigma(0) = 0{,}5$, $\sigma(1) = 0{,}73$, $\sigma(2) = 0{,}88$, $\sigma(3) = 0{,}95$. La terza identità è quella che serve per i gradienti.

**Similarità come prodotto scalare** ([L11, slide 14](L11-embedding-word2vec.md#p-14))

$$
\text{Similarity}(w,c)\approx\mathbf c\cdot\mathbf w
$$

Eq. 5.13: un contesto è probabile se il suo embedding ha prodotto scalare alto con quello del target.

**Probabilità di una finestra (indipendenza)** ([L11, slide 16](L11-embedding-word2vec.md#p-16))

$$
P(+\mid w,c_{1:L}) = \prod_{i=1}^{L}\sigma(\mathbf c_i\cdot\mathbf w)\qquad \log P(+\mid w,c_{1:L}) = \sum_{i=1}^{L}\log\sigma(\mathbf c_i\cdot\mathbf w)
$$

Eq. 5.17-5.18. I contesti sono assunti indipendenti dato il target.

**Parametri di skip-gram** ([L11, slide 17](L11-embedding-word2vec.md#p-17))

$$
\theta = \begin{bmatrix}W\\ C\end{bmatrix}\in\mathbb R^{2|V|\times d}
$$

Un target embedding e un context embedding per parola: $2|V|d$ numeri, 30 milioni con $|V| = 50.000$ e $d = 300$.

**Distribuzione delle parole di rumore** ([L11, slide 22](L11-embedding-word2vec.md#p-22))

$$
P_\alpha(w) = \frac{\text{count}(w)^\alpha}{\sum_{w'}\text{count}(w')^\alpha}\qquad \alpha = 0{,}75
$$

Eq. 5.19. Le parole rare guadagnano probabilità: con due eventi 0,99/0,01 si passa a 0,97/0,03 (Eq. 5.20). $\alpha = 1$: $P$ originale; $\alpha = 0$: uniforme.

**Loss di skip-gram con negative sampling** ([L11, slide 24](L11-embedding-word2vec.md#p-24))

$$
L(w,c_{pos},c_{neg*}) = -\Big[\log\sigma(\mathbf c_{pos}\cdot\mathbf w) + \sum_{i=1}^{k}\log\sigma(-\mathbf c_{neg_i}\cdot\mathbf w)\Big]
$$

Eq. 5.21, per una coppia positiva e $k$ parole di rumore. Vale $(k+1)\ln2$ con tutti i prodotti a 0, tende a 0 per un classificatore perfetto. Esempio della scheda 30: 1,14.

**Gradienti rispetto ai contesti** ([L11, slide 27](L11-embedding-word2vec.md#p-27))

$$
\frac{\partial L}{\partial\mathbf c_{pos}} = [\sigma(\mathbf c_{pos}\cdot\mathbf w)-1]\,\mathbf w\qquad \frac{\partial L}{\partial\mathbf c_{neg_i}} = \sigma(\mathbf c_{neg_i}\cdot\mathbf w)\,\mathbf w
$$

Eq. 5.22-5.23: probabilità prevista meno etichetta (1 o 0), per $\mathbf w$.

**Gradiente rispetto al target** ([L11, slide 28](L11-embedding-word2vec.md#p-28))

$$
\frac{\partial L}{\partial\mathbf w} = [\sigma(\mathbf c_{pos}\cdot\mathbf w)-1]\,\mathbf c_{pos} + \sum_{i=1}^{k}\sigma(\mathbf c_{neg_i}\cdot\mathbf w)\,\mathbf c_{neg_i}
$$

Eq. 5.24: gli errori delle $k+1$ coppie, ciascuno per il suo vettore di contesto.

**Aggiornamenti della SGD** ([L11, slide 29](L11-embedding-word2vec.md#p-29))

$$
\mathbf c_{pos}^{t+1} = \mathbf c_{pos}^{t} - \eta\,\frac{\partial L}{\partial\mathbf c_{pos}}\Big|_t\quad \mathbf c_{neg_i}^{t+1} = \mathbf c_{neg_i}^{t} - \eta\,\frac{\partial L}{\partial\mathbf c_{neg_i}}\Big|_t\quad \mathbf w^{t+1} = \mathbf w^{t} - \eta\,\frac{\partial L}{\partial\mathbf w}\Big|_t
$$

Eq. 5.25-5.27: tutti i gradienti valutati con i valori al tempo $t$. $\eta$ = learning rate (0,5 nell'esempio della slide, 0,025 nel notebook).

**Embedding finale di una parola** ([L11, slide 32](L11-embedding-word2vec.md#p-32))

$$
\mathbf e_i = \mathbf w_i + \mathbf c_i\quad\text{oppure}\quad \mathbf e_i = \mathbf w_i
$$

Si sommano i due embedding o si butta via $C$.

**Fasttext: parola come somma di n-grammi** ([L11, slide 39](L11-embedding-word2vec.md#p-39))

$$
\mathbf v_{where} = \mathbf z_{\langle where\rangle} + \sum_{g\in G(where)}\mathbf z_g
$$

$G$ = n-grammi di caratteri (3-6) della parola con i confini < >; per una parola sconosciuta si sommano solo gli n-grammi. Una parola di $m$ lettere ha $4m-6$ n-grammi di lunghezza 3-6 ($m\ge4$).

**SGNS come fattorizzazione della PMI (approfondimento)** ([L11, slide 40](L11-embedding-word2vec.md#p-40))

$$
\mathbf w\cdot\mathbf c = \text{PMI}(w,c) - \log k
$$

Levy e Goldberg (2014), non nel libro: all'ottimo SGNS fattorizza una matrice PMI spostata di $\log k$ (con $P_\alpha$ al denominatore se il rumore viene da $P_\alpha$).

**Distribuzione dei negativi (e del contesto per la PPMI con α)** ([L12](L12-laboratorio-word-embedding.md))

$$
P_\alpha(w)=\frac{\text{count}(w)^{\alpha}}{\sum_{w'}\text{count}(w')^{\alpha}},\qquad \alpha=0{,}75
$$

Alza la probabilità delle parole rare. In gensim è `ns_exponent=0.75`; nel training fatto a mano `p_neg = freq ** 0.75 / np.sum(freq ** 0.75)`.

**Probabilità di una coppia vera** ([L12](L12-laboratorio-word-embedding.md))

$$
P(+\mid w,c)=\sigma(\mathbf c\cdot\mathbf w)=\frac{1}{1+e^{-\mathbf c\cdot\mathbf w}}
$$

$\mathbf w$ riga di $W$ (target), $\mathbf c$ riga di $C$ (contesto). $P(-\mid w,c) = \sigma(-\mathbf c\cdot\mathbf w)$.

**Loss di SGNS per una coppia** ([L12](L12-laboratorio-word-embedding.md))

$$
L=-\log\sigma(\mathbf c_{pos}\cdot\mathbf w)-\sum_{i=1}^{k}\log\sigma(-\mathbf c_{neg_i}\cdot\mathbf w)
$$

J&M Eq. 5.21. Con tutti i vettori di contesto nulli vale $(k+1)\ln 2$ ($= 4{,}16$ con $k = 5$). Implementazione stabile: `np.logaddexp(0, -s)` $= -\log\sigma(s)$.

**Gradienti di SGNS** ([L12](L12-laboratorio-word-embedding.md))

$$
\frac{\partial L}{\partial\mathbf c_{pos}}=[\sigma(\mathbf c_{pos}\cdot\mathbf w)-1]\,\mathbf w,\quad \frac{\partial L}{\partial\mathbf c_{neg_i}}=\sigma(\mathbf c_{neg_i}\cdot\mathbf w)\,\mathbf w,\quad \frac{\partial L}{\partial\mathbf w}=[\sigma(\mathbf c_{pos}\cdot\mathbf w)-1]\,\mathbf c_{pos}+\sum_{i}\sigma(\mathbf c_{neg_i}\cdot\mathbf w)\,\mathbf c_{neg_i}
$$

J&M Eq. 5.22-5.24, da $\frac{d}{dz}\log\sigma(z) = 1-\sigma(z)$. Esempio: $\mathbf w = \mathbf c_{pos} = [1,0]$, $\mathbf c_{neg} = [0,1]$ → $\nabla_{\mathbf w} = [-0{,}269;\ 0{,}5]$.

**Probabilità di tenere una parola (subsampling)** ([L12](L12-laboratorio-word-embedding.md))

$$
P_{\text{keep}}(w)=\min\left(1,\ \sqrt{\frac{t}{f(w)}}+\frac{t}{f(w)}\right),\qquad t=10^{-3}
$$

$f(w)$ = frequenza relativa nel corpus. Le parole frequentissime vengono scartate spesso, così la finestra raggiunge parole più lontane. È la formula del codice di word2vec usata in `train_sgns` (in gensim: `sample=1e-3`).

### Proprietà degli embedding

**Metodo del parallelogramma** ([L11, slide 48](L11-embedding-word2vec.md#p-48))

$$
\hat{\mathbf b}^* = \underset{\mathbf x}{\operatorname{argmin}}\ \text{distance}(\mathbf x,\ \mathbf b-\mathbf a+\mathbf a^*)
$$

Eq. 5.28, per $a : b :: a^* : b^*$, escludendo le parole di input. Distanza euclidea nel libro, spesso coseno in pratica.

**Differenza di coseni come misura di bias** ([L11, slide 54](L11-embedding-word2vec.md#p-54))

$$
\text{bias}(x) = \cos(\mathbf x,\mathbf{she}) - \cos(\mathbf x,\mathbf{he})
$$

Esercizio 11: positivo se la parola pende verso *she*. Nell'esempio nurse +0,759, engineer −0,632, teacher 0.

**Analogia con il parallelogramma (coseno)** ([L12](L12-laboratorio-word-embedding.md))

$$
\hat d=\underset{x\notin\{a,b,c\}}{\operatorname{argmax}}\ \cos\big(\mathbf x,\ \mathbf b-\mathbf a+\mathbf c\big)
$$

$a : b :: c : d$. Per vettori unitari equivale a minimizzare la distanza euclidea, perché $\|\mathbf t-\mathbf x\|^2 = \|\mathbf t\|^2+1-2\,\mathbf t\cdot\mathbf x$. L'esclusione degli input è essenziale.

**Odd-one-out con il centroide** ([L12](L12-laboratorio-word-embedding.md))

$$
\text{intruso}=\underset{w\in S}{\operatorname{argmin}}\ \cos\Big(\mathbf w,\ \tfrac{1}{|S|}\textstyle\sum_{v\in S}\mathbf v\Big)
$$

La parola meno simile al centro di massa del gruppo $S$.

### Bias

**Direzione di genere** ([L12](L12-laboratorio-word-embedding.md))

$$
\mathbf d=\frac{\bar{\boldsymbol\delta}}{\|\bar{\boldsymbol\delta}\|},\qquad \bar{\boldsymbol\delta}=\frac{1}{P}\sum_{p=1}^{P}\left(\frac{\mathbf f_p}{\|\mathbf f_p\|}-\frac{\mathbf m_p}{\|\mathbf m_p\|}\right)
$$

Media delle differenze femminile − maschile dei vettori normalizzati su $P$ coppie definitorie, poi normalizzata. In GloVe con 8 coppie: coseno 0,891 con $\mathbf{she}-\mathbf{he}$.

**Neutralize (proiezione ortogonale)** ([L12](L12-laboratorio-word-embedding.md))

$$
\mathbf v_\perp=\mathbf v-(\mathbf v\cdot\mathbf d)\,\mathbf d,\qquad \mathbf v_\perp\cdot\mathbf d=0\ \ (\|\mathbf d\|=1)
$$

Toglie la componente lungo $\mathbf d$. Esempio: $[3,4]$ con $\mathbf d = [1,0]$ → $[0,4]$. Non toglie l'informazione distribuita nelle altre dimensioni (10-NN al 93,1% dopo il neutralize).

**Bias di una parola come differenza di coseni** ([L12](L12-laboratorio-word-embedding.md))

$$
\text{bias}(p)=\cos(\mathbf p,\mathbf{woman})-\cos(\mathbf p,\mathbf{man})
$$

Positivo = più vicino a *woman*. In GloVe: *nurse* +0,158, *manager* −0,214.

### Reti neurali

**Unità neurale** ([L13, slide 10](L13-reti-neurali.md#p-10))

$$
z = b + \sum_i w_i x_i = \mathbf w\cdot\mathbf x + b,\qquad a = f(z)
$$

Eq. 6.1-6.4. $z$ pre-attivazione, $f$ attivazione non lineare. Esempio del libro: $\mathbf w = [0{,}2;0{,}3;0{,}9]$, $b = 0{,}5$, $\mathbf x = [0{,}5;0{,}6;0{,}1]$: $z = 0{,}87$, $\sigma(z) = 0{,}70$.

**Sigmoide, tanh, ReLU** ([L13, slide 14](L13-reti-neurali.md#p-14))

$$
\sigma(z) = \frac{1}{1+e^{-z}}\quad \tanh(z) = \frac{e^z - e^{-z}}{e^z + e^{-z}}\quad \mathrm{ReLU}(z) = \max(z,0)
$$

Eq. 6.3, 6.5, 6.6. Codomini $(0,1)$, $(-1,1)$, $[0,\infty)$. GELU $= z\,\Phi(z)$, liscia, minimo circa −0,17.

**Derivate delle attivazioni** ([L13, slide 16](L13-reti-neurali.md#p-16))

$$
\sigma'(z) = \sigma(z)(1-\sigma(z)) \le \tfrac14\qquad \tanh'(z) = 1-\tanh^2(z)\qquad \mathrm{ReLU}'(z) = \begin{cases}0 & z<0\\ 1 & z\ge0\end{cases}
$$

Eq. 6.38-6.40 (in $z = 0$ la derivata della ReLU per convenzione vale 1). Il limite 1/4 spiega il vanishing gradient: dieci sigmoidi in catena danno al più $(1/4)^{10}\approx10^{-6}$.

**Perceptron e frontiera lineare** ([L13, slide 18](L13-reti-neurali.md#p-18))

$$
y = \begin{cases}0 & \mathbf w\cdot\mathbf x + b\le 0\\ 1 & \mathbf w\cdot\mathbf x + b > 0\end{cases}\qquad x_2 = -\frac{w_1}{w_2}x_1 - \frac{b}{w_2}
$$

Eq. 6.7. La frontiera di un'unità è una retta (iperpiano in $d$ dimensioni): XOR non è linearmente separabile.

**Rete XOR** ([L13, slide 21](L13-reti-neurali.md#p-21))

$$
\mathbf h = \mathrm{ReLU}\Big(\begin{bmatrix}1&1\\1&1\end{bmatrix}\mathbf x + \begin{bmatrix}0\\-1\end{bmatrix}\Big),\qquad y = \mathrm{ReLU}(h_1 - 2h_2)
$$

Fig. 6.6. $\mathbf h$ = [0,0], [1,0], [1,0], [2,1] per i quattro input; $y$ = 0, 1, 1, 0.

**Collasso di strati lineari** ([L13, slide 26](L13-reti-neurali.md#p-26))

$$
W^{[2]}(W^{[1]}\mathbf x + \mathbf b^{[1]}) + \mathbf b^{[2]} = W'\mathbf x + \mathbf b',\quad W' = W^{[2]}W^{[1]},\ \mathbf b' = W^{[2]}\mathbf b^{[1]} + \mathbf b^{[2]}
$$

Eq. 6.14. Senza non linearità la profondità non aggiunge espressività.

**Approssimazione universale** ([L13, slide 27](L13-reti-neurali.md#p-27))

$$
\sup_{\mathbf x\in K}\Big|f(\mathbf x) - \sum_{j=1}^N u_j\,\sigma(\mathbf w_j\cdot\mathbf x + b_j)\Big| < \varepsilon
$$

Hornik et al. 1989: per ogni $f$ continua su un compatto $K$ e ogni $\varepsilon>0$ esiste un $N$ (che può essere esponenziale in $d$). Interpolazione di $x^2$ con ReLU a passo $h$: errore massimo $h^2/4$.

**Rete feedforward a due strati** ([L13, slide 31](L13-reti-neurali.md#p-31))

$$
\mathbf h = g(W\mathbf x + \mathbf b),\quad \mathbf z = U\mathbf h,\quad \mathbf y = \mathrm{softmax}(\mathbf z)
$$

Eq. 6.12. Forme: $W$ $d_h\times d$, $\mathbf b$ e $\mathbf h$ $d_h$, $U$ $K\times d_h$, $\mathbf z$ e $\mathbf y$ $K$. Parametri: $d_hd + d_h + Kd_h$ (+$K$ con bias di output).

**Forward pass su un batch** ([L13, slide 33](L13-reti-neurali.md#p-33))

$$
H = g(XW^\top + \mathbf b),\quad Z = HU^\top,\quad \hat Y = \mathrm{softmax}(Z)
$$

Eq. 6.20. $X$ $m\times d$, $H$ $m\times d_h$, $Z$ $m\times K$; softmax riga per riga. Il libro in Eq. 6.22 usa $\mathbf xW$ con $W$ di forma $d\times d_h$.

**Notazione per strati** ([L13, slide 34](L13-reti-neurali.md#p-34))

$$
\mathbf z^{[\ell]} = W^{[\ell]}\mathbf a^{[\ell-1]} + \mathbf b^{[\ell]},\qquad \mathbf a^{[\ell]} = g^{[\ell]}(\mathbf z^{[\ell]}),\qquad \mathbf a^{[0]} = \mathbf x,\ \hat{\mathbf y} = \mathbf a^{[n]}
$$

Eq. 6.13. $\mathbf z^{[n]}$ sono i logit.

**Softmax e sua invarianza** ([L13, slide 36](L13-reti-neurali.md#p-36))

$$
\mathrm{softmax}(\mathbf z)_i = \frac{e^{z_i}}{\sum_{j=1}^K e^{z_j}} = \frac{e^{z_i - c}}{\sum_j e^{z_j - c}}
$$

Eq. 6.9. Contano solo le differenze: $p_i/p_j = e^{z_i - z_j}$ (scarto 2 → rapporto 7,4). Calcolo stabile con $c = \max\mathbf z$.

**Cross-entropy (negative log likelihood)** ([L13, slide 38](L13-reti-neurali.md#p-38))

$$
L_{CE}(\mathbf p,\mathbf y) = -\sum_{k=1}^K y_k\log p_k = -\log p_c = -z_c + \log\sum_j e^{z_j}
$$

Eq. 6.26-6.28. $p_c$ = 0,1 / 0,5 / 0,9 → $L$ = 2,30 / 0,69 / 0,11. Uniforme su $K$ classi: $\log K$. Caso binario: $-[y\log\hat y + (1-y)\log(1-\hat y)]$ (Eq. 6.25).

**Gradiente rispetto ai logit** ([L13, slide 57](L13-reti-neurali.md#p-57))

$$
\frac{\partial L}{\partial z} = a - y\ \text{(sigmoide + BCE)},\qquad \frac{\partial L}{\partial\mathbf z} = \mathbf p - \mathbf y\ \text{(softmax + CE)},\qquad \frac{\partial L}{\partial w_j} = (a-y)\,x_j
$$

Eq. 6.29, 6.42-6.43. L'errore di previsione per l'input.

### Embedding e pooling

**Lookup nella matrice di embedding** ([L13, slide 42](L13-reti-neurali.md#p-42))

$$
\mathbf e(w) = \mathbf x_w E,\qquad E\in\mathbb R^{|V|\times d},\ \mathbf x_w\ \text{one-hot } 1\times|V|
$$

Fig. 6.11. Il prodotto con un one-hot seleziona la riga di $w$; in pratica è un'indicizzazione.

**Mean e max pooling** ([L13, slide 44](L13-reti-neurali.md#p-44))

$$
\mathbf x_{\text{mean}} = \frac1n\sum_{i=1}^n\mathbf e(w_i),\qquad (\mathbf x_{\max})_j = \max_i\ \mathbf e(w_i)_j
$$

Eq. 6.21. Con maschera di padding: $\sum_i m_i\mathbf e_i/\sum_i m_i$. Invarianti all'ordine.

**Language model neurale feedforward** ([L13, slide 47](L13-reti-neurali.md#p-47))

$$
\mathbf e = [E\mathbf x_{t-3}; E\mathbf x_{t-2}; E\mathbf x_{t-1}],\ \mathbf h = g(W\mathbf e + \mathbf b),\ \mathbf z = U\mathbf h,\ \hat{\mathbf y} = \mathrm{softmax}(\mathbf z)
$$

Eq. 6.23-6.24, Bengio et al. 2003. Approssima $P(w_t\mid w_{1:t-1})\approx P(w_t\mid w_{t-N+1:t-1})$. $\mathbf e$ ha dimensione $Nd$, $U$ è $|V|\times d_h$.

### Addestramento reti neurali

**Discesa del gradiente** ([L13, slide 53](L13-reti-neurali.md#p-53))

$$
\theta^{t+1} = \theta^t - \eta\,\frac{\partial L}{\partial\theta}
$$

Loss non convessa per le reti: si cerca un buon minimo. $\eta$ learning rate.

**Regola della catena su un grafo** ([L13, slide 55](L13-reti-neurali.md#p-55))

$$
\frac{\partial L}{\partial x} = \frac{\partial L}{\partial y}\cdot\frac{\partial y}{\partial x}\qquad(\text{downstream} = \text{upstream}\times\text{locale})
$$

Eq. 6.31-6.34. Esempio $L = c(a+2b)$ con $a = 3$, $b = 1$, $c = -2$: $\partial L/\partial a = -2$, $\partial L/\partial b = -4$, $\partial L/\partial c = 5$. I contributi di più rami si sommano.

**SGD con momentum** ([L13, slide 61](L13-reti-neurali.md#p-61))

$$
\mathbf v\leftarrow\beta\mathbf v + \mathbf g,\qquad \theta\leftarrow\theta - \eta\,\mathbf v
$$

Con gradiente costante $v\to1/(1-\beta) = 10$ per $\beta = 0{,}9$; con gradiente alternato le oscillazioni si smorzano.

**Adam** ([L13, slide 61](L13-reti-neurali.md#p-61))

$$
\mathbf m\leftarrow\beta_1\mathbf m + (1-\beta_1)\mathbf g,\ \ \mathbf s\leftarrow\beta_2\mathbf s + (1-\beta_2)\mathbf g^2,\ \ \hat{\mathbf m} = \frac{\mathbf m}{1-\beta_1^t},\ \hat{\mathbf s} = \frac{\mathbf s}{1-\beta_2^t},\ \ \theta\leftarrow\theta - \eta\frac{\hat{\mathbf m}}{\sqrt{\hat{\mathbf s}} + \epsilon}
$$

$\beta_1 = 0{,}9$, $\beta_2\approx0{,}999$. Primo passo: $\eta\,\mathrm{sign}(g)$. AdamW: weight decay disaccoppiato.

**Cosine annealing** ([L13, slide 62](L13-reti-neurali.md#p-62))

$$
\eta_t = \frac{\eta_{\max}}{2}\Big(1 + \cos\frac{\pi t}{T}\Big)
$$

Da $\eta_{\max}$ a 0 in $T$ passi; $\eta_{T/2} = \eta_{\max}/2$. Spesso preceduto da un warm-up lineare.

**L2 e weight decay** ([L13, slide 64](L13-reti-neurali.md#p-64))

$$
L_{\text{reg}} = L + \frac\lambda2\|\theta\|^2,\qquad \theta\leftarrow(1-\eta\lambda)\,\theta - \eta\,\nabla_\theta L
$$

Ogni passo restringe i pesi di $(1-\eta\lambda)$: con $\eta\lambda = 0{,}001$, dopo 1000 passi resta $e^{-1}\approx0{,}37$.

**Dropout invertito** ([L13, slide 65](L13-reti-neurali.md#p-65))

$$
\tilde{\mathbf h} = \frac{\mathbf m\odot\mathbf h}{1-p},\quad m_j\sim\mathrm{Bernoulli}(1-p),\quad E[\tilde h_j] = h_j
$$

Nuova maschera a ogni mini-batch; al test nessun dropout. $p\approx0{,}1$ nei transformer, fino a 0,5 negli MLP.

**Inizializzazione Xavier e He** ([L13, slide 66](L13-reti-neurali.md#p-66))

$$
\mathrm{Var}(W_{ij}) = \frac{1}{n_{\text{in}}}\ (\text{Xavier}),\qquad \frac{2}{n_{\text{in}}}\ (\text{He, ReLU})
$$

Per $n_{\text{in}} = 300$: deviazioni standard 0,058 e 0,082. Pesi tutti uguali: simmetria mai rotta.

**LayerNorm** ([L13, slide 66](L13-reti-neurali.md#p-66))

$$
\hat{\mathbf h} = \boldsymbol\gamma\odot\frac{\mathbf h - \mu}{\sigma} + \boldsymbol\beta
$$

$\mu$ e $\sigma$ sulle feature di un esempio (LayerNorm) o su un batch per ogni feature (BatchNorm); $\boldsymbol\gamma$, $\boldsymbol\beta$ appresi.

**Connessione residua** ([L13, slide 67](L13-reti-neurali.md#p-67))

$$
\mathbf h^{[\ell+1]} = \mathbf h^{[\ell]} + F(\mathbf h^{[\ell]}),\qquad \frac{\partial\mathbf h^{[\ell+1]}}{\partial\mathbf h^{[\ell]}} = I + \frac{\partial F}{\partial\mathbf h^{[\ell]}}
$$

Il termine $I$ dà ai gradienti un percorso diretto; il blocco impara una correzione.

### Transformer

**Attenzione semplificata** ([L14, slide 18](L14-transformer-l-attenzione.md#p-18))

$$
a_i = \sum_{j\le i}\alpha_{ij}\,x_j,\qquad \alpha_{ij} = \mathrm{softmax}_j(x_i\cdot x_j)
$$

Somma pesata degli input fino a $i$ con pesi dalla softmax dei prodotti scalari. Nessun parametro. Esempio chicken/road/it: pesi 0,24; 0,09; 0,67.

**Softmax sui token del contesto** ([L14, slide 18](L14-transformer-l-attenzione.md#p-18))

$$
\alpha_{ij} = \frac{\exp(\mathrm{score}(x_i,x_j))}{\sum_{k\le i}\exp(\mathrm{score}(x_i,x_k))}
$$

Normalizzazione solo sulle posizioni $k\le i$ (causale); pesi in $[0,1]$ che sommano a 1.

**Proiezioni query, key, value** ([L14, slide 23](L14-transformer-l-attenzione.md#p-23))

$$
q_i = x_iW^Q,\quad k_j = x_jW^K,\quad v_j = x_jW^V
$$

$W^Q, W^K$: $[d\times d_k]$; $W^V$: $[d\times d_v]$. Stesse matrici a ogni posizione, diverse per testa e per strato.

**Scaled dot product** ([L14, slide 24](L14-transformer-l-attenzione.md#p-24))

$$
\mathrm{score}(x_i,x_j) = \frac{q_i\cdot k_j}{\sqrt{d_k}}
$$

Il prodotto scalare ha deviazione standard circa $\sqrt{d_k}$; dividendo si evita una softmax satura e gradienti minuscoli.

**Output di una testa** ([L14, slide 25](L14-transformer-l-attenzione.md#p-25))

$$
\mathrm{head}_i = \sum_{j\le i}\alpha_{ij}v_j,\qquad a_i = \mathrm{head}_i\,W^O
$$

$\mathrm{head}_i$: $[1\times d_v]$; $W^O$: $[d_v\times d]$; $a_i$: $[1\times d]$ come l'input. Esempio della lezione: $a_3 = [0{,}93;\ 1{,}31;\ 1{,}31]$.

**Multi-head attention** ([L14, slide 39](L14-transformer-l-attenzione.md#p-39))

$$
a_i = (\mathrm{head}_i^1\oplus\mathrm{head}_i^2\oplus\dots\oplus\mathrm{head}_i^A)\,W^O
$$

$A$ teste con matrici proprie; concatenazione $[1\times Ad_v]$; $W^O$: $[Ad_v\times d]$. Di solito $d_k = d_v = d/A$.

**Pesi dell'attenzione di uno strato** ([L14, slide 40](L14-transformer-l-attenzione.md#p-40))

$$
3A\,d\,d_k + A\,d_v\,d = 4d^2\quad (d_k = d_v = d/A)
$$

Senza bias. Originale ($d = 512$, $A = 8$): 1.048.576. Uguale a una testa sola di dimensione piena.

**Feedforward position-wise** ([L14, slide 46](L14-transformer-l-attenzione.md#p-46))

$$
\mathrm{FFN}(x) = \mathrm{ReLU}(xW_1+b_1)W_2+b_2,\qquad d_{ff} = 4d
$$

Stessi pesi a ogni posizione. $2d\,d_{ff} = 8d^2$ pesi: con $d = 512$, 2.097.152, il doppio dell'attenzione.

**SwiGLU** ([L14, slide 47](L14-transformer-l-attenzione.md#p-47))

$$
\mathrm{FFN}_{\mathrm{SwiGLU}}(x) = \big(\mathrm{Swish}_\beta(xW_1+b_1)\otimes(xW_2+b_2)\big)W_3+b_3,\quad \mathrm{Swish}_\beta(x) = x\,\sigma(\beta x)
$$

Feedforward con gate degli LLM moderni (Shazeer, 2020); $\otimes$ prodotto componente per componente; $d_{ff}$ un po' meno di $4d$.

**Layer norm** ([L14, slide 49](L14-transformer-l-attenzione.md#p-49))

$$
\mathrm{LayerNorm}(x) = \gamma\,\frac{x-\mu}{\sigma}+\beta,\quad \mu = \tfrac1d\sum_j x[j],\ \sigma = \sqrt{\tfrac1d\sum_j (x[j]-\mu)^2}
$$

Sul vettore di un token. $\gamma$ gain, $\beta$ offset imparabili ($2d$ parametri). $[2,4,6,8]\to[-1{,}34;\ -0{,}45;\ 0{,}45;\ 1{,}34]$.

**RMSNorm** ([L14, slide 49](L14-transformer-l-attenzione.md#p-49))

$$
\mathrm{RMSNorm}(x) = \frac{x}{\sqrt{\frac1d\sum_j x[j]^2}}
$$

Senza sottrarre la media (di solito con un gain imparabile). Usata da molte reti moderne.

**Transformer block (prenorm)** ([L14, slide 50](L14-transformer-l-attenzione.md#p-50))

$$
t^1 = \mathrm{LN}(x_i),\ t^2 = \mathrm{MHA}(t^1_i,[t^1_1..t^1_{i-1}]),\ t^3 = t^2+x_i,\ t^4 = \mathrm{LN}(t^3),\ t^5 = \mathrm{FFN}(t^4),\ h_i = t^5+t^3
$$

Quindi $h_i = x_i + t_i^2 + t_i^5$: la residual stream.

**Attenzione in forma matriciale** ([L14, slide 59](L14-transformer-l-attenzione.md#p-59))

$$
\mathrm{head} = \mathrm{softmax}\Big(\mathrm{mask}\Big(\frac{QK^\top}{\sqrt{d_k}}\Big)\Big)V,\qquad Q = XW^Q,\ K = XW^K,\ V = XW^V
$$

$X$: $[N\times d]$; $QK^\top$: $[N\times N]$; head: $[N\times d_v]$; $A = \mathrm{head}\,W^O$: $[N\times d]$.

**Maschera causale** ([L14, slide 56](L14-transformer-l-attenzione.md#p-56))

$$
M_{ij} = \begin{cases}0 & j\le i\\ -\infty & j>i\end{cases},\qquad \mathrm{mask}(QK^\top) = QK^\top + M
$$

Dopo la softmax i pesi sul futuro sono 0 ($e^{-\infty} = 0$).

**Blocco in forma matriciale** ([L14, slide 62](L14-transformer-l-attenzione.md#p-62))

$$
O = X + \mathrm{MultiHeadAttention}(\mathrm{LayerNorm}(X)),\qquad H = O + \mathrm{FFN}(\mathrm{LayerNorm}(O))
$$

Eq. 7.39-7.40 del libro. $X$ e $H$: $[N\times d]$, quindi i blocchi si impilano.

**Costo dell'attenzione** ([L14, slide 60](L14-transformer-l-attenzione.md#p-60))

$$
N^2\ \text{punteggi per testa e strato};\quad N(N+1)/2\ \text{non mascherati}
$$

Quadratico nella lunghezza del contesto: $N = 1000\to10^6$, $N = 10^5\to10^{10}$.

**Parametri per blocco** ([L14, slide 46](L14-transformer-l-attenzione.md#p-46))

$$
4d^2\ (\text{attenzione}) + 8d^2\ (\text{FFN},\ d_{ff}=4d) \approx 12d^2
$$

GPT-3 175B: $96\cdot12\cdot12288^2\approx1{,}74\cdot10^{11}$.

**Embedding come prodotto con un one-hot** ([L15, slide 11](L15-transformer-embedding-lm-head-e-decoding.md#p-11))

$$
x\,E = E_{k,:},\qquad x\in\{0,1\}^{1\times|V|},\ x_k = 1
$$

Selezionare la riga $k$ di $E$ $[|V|\times d]$ equivale a moltiplicare il one-hot del token $k$ per $E$. Per la sequenza: one-hot $[N\times|V|]$ per $E$ = $[N\times d]$.

**Pesi della matrice di embedding** ([L15, slide 13](L15-transformer-embedding-lm-head-e-decoding.md#p-13))

$$
\#E = |V|\cdot d
$$

Esempi: $50.000\cdot512 = 25{,}6$ milioni; $50.000\cdot768 = 38{,}4$ milioni.

**Input con posizioni assolute** ([L15, slide 16](L15-transformer-embedding-lm-head-e-decoding.md#p-16))

$$
X_i = E[\mathrm{id}(i)] + E_{pos}[i],\qquad X\in\mathbb{R}^{N\times d}
$$

Somma (non concatenazione) dell'embedding del token e di quello della posizione, entrambi $[1\times d]$. $E_{pos}$ appresa $[N\times d]$, oppure sostituita da una funzione fissa.

**Embedding di posizione sinusoidali** ([L15, slide 19](L15-transformer-embedding-lm-head-e-decoding.md#p-19))

$$
PE(p,2i) = \sin\frac{p}{10000^{2i/d}},\qquad PE(p,2i+1) = \cos\frac{p}{10000^{2i/d}}
$$

$p$ posizione, $d$ dimensione del modello, $i = 0,\dots,d/2-1$. Frequenze $\omega_i = 10000^{-2i/d}$, da 1 (un radiante per posizione) a circa $10^{-4}$. Con $d = 4$: $PE(p) = [\sin p, \cos p, \sin(p/100), \cos(p/100)]$.

**Prodotto scalare fra posizioni sinusoidali** ([L15, slide 21](L15-transformer-embedding-lm-head-e-decoding.md#p-21))

$$
PE(p)\cdot PE(q) = \sum_{i=0}^{d/2-1}\cos\big(\omega_i\,(p-q)\big)
$$

Dipende solo dalla distanza; vale $d/2$ per $p = q$. Con $d = 64$: $PE(4)\cdot PE(5) = 30{,}9$, $PE(4)\cdot PE(17) = 21{,}0$.

**RoPE (una coppia di dimensioni)** ([L15, slide 23](L15-transformer-embedding-lm-head-e-decoding.md#p-23))

$$
(R(m\theta)\,q)\cdot(R(n\theta)\,k) = q^\top R\big((n-m)\theta\big)\,k,\qquad R(\alpha) = \begin{pmatrix}\cos\alpha & -\sin\alpha\\ \sin\alpha & \cos\alpha\end{pmatrix}
$$

Query in posizione $m$ ruotata di $m\theta$, key in posizione $n$ di $n\theta$: il punteggio dipende dal contenuto e da $m-n$. Una velocità $\theta_i = 10000^{-2i/d}$ per coppia; si applica a query e key in ogni strato.

**Language modeling head (con weight tying)** ([L15, slide 28](L15-transformer-embedding-lm-head-e-decoding.md#p-28))

$$
u = h^L_N\,E^\top,\qquad y = \mathrm{softmax}(u)
$$

$h^L_N$ $[1\times d]$, $E^\top$ $[d\times|V|]$, logit $u$ e probabilità $y$ $[1\times|V|]$. Il logit del token $k$ è $h\cdot E_k$. Senza tying $E^\top$ è sostituita da una matrice $U$ appresa (altri $|V|d$ pesi).

**Input encoding** ([L16](L16-laboratorio-dagli-n-gram-a-gpt.md))

$$
X=E[\text{idx}]+E_{pos}[0{:}T],\qquad X\in\mathbb R^{B\times T\times d}
$$

Embedding del token più embedding appreso della posizione assoluta (J&M §7.4).

**Testa di attenzione causale (forma matriciale)** ([L16](L16-laboratorio-dagli-n-gram-a-gpt.md))

$$
\text{head}=\operatorname{softmax}\!\Big(\frac{QK^\top}{\sqrt{d_k}}+M\Big)V,\quad Q=XW^Q,\;K=XW^K,\;V=XW^V
$$

$M_{ij}=0$ se $j\le i$, $-\infty$ se $j&gt;i$ (in PyTorch: `masked_fill(tril == 0, -inf)`). Forme: $[T\times d_k]$, punteggi $[T\times T]$.

**Multi-head attention** ([L16](L16-laboratorio-dagli-n-gram-a-gpt.md))

$$
\text{MHA}(X)=(\text{head}_1\oplus\cdots\oplus\text{head}_A)\,W^O,\qquad d_k=d_v=d/A
$$

Nel lab $A=4$, $d=96$, $d_k=24$; $W^O$ quadrata $96\times96$ (con bias).

**Blocco prenorm** ([L16](L16-laboratorio-dagli-n-gram-a-gpt.md))

$$
O=X+\text{MHA}(\text{LN}(X)),\qquad H=O+\text{FFN}(\text{LN}(O))
$$

J&M Eq. 7.39-7.40. FFN: $d\to4d\to d$ con GELU.

**Loss di language modeling** ([L16](L16-laboratorio-dagli-n-gram-a-gpt.md))

$$
\mathcal L=-\frac{1}{BT}\sum_{b=1}^{B}\sum_{t=1}^{T}\ln \operatorname{softmax}(\mathbf z_{b,t})[y_{b,t}]
$$

Media sulle $B\times T$ posizioni del batch (J&M Eq. 7.55); $y_{b,t}=x_{b,t+1}$. `F.cross_entropy` riceve i logit.

**Parametri di un blocco** ([L16](L16-laboratorio-dagli-n-gram-a-gpt.md))

$$
\underbrace{4d^2}_{\text{attenzione}}+\underbrace{2\,d\,d_{ff}}_{\text{FFN}}=12d^2\quad(d_{ff}=4d)
$$

A meno di bias e layer norm. Con $d=96$: $110.592$ contro i $111.552$ esatti; il tiny GPT ha 244.301 parametri.

**Memoria della KV cache** ([L16](L16-laboratorio-dagli-n-gram-a-gpt.md))

$$
M_{KV}=2\cdot L\cdot N\cdot d\cdot b\ \text{byte per sequenza}
$$

$b$ byte per numero (2 in float16). Llama 3.1 8B a 128k token: 64 GiB senza GQA, 16 GiB con GQA.

**Memoria della matrice di attenzione** ([L16](L16-laboratorio-dagli-n-gram-a-gpt.md))

$$
B\cdot A\cdot T^2\ \text{elementi per strato}
$$

Quadratica in $T$: raddoppiare il contesto quadruplica la memoria. $T=10^5$, $A=32$, float32: 1.280 GB per strato e per sequenza.

**Parametri di un transformer (conto semplice)** ([L17, slide 43](L17-pretraining-dei-modelli-linguistici.md#p-43))

$$
N \approx 12\,L\,d^2 + |V|\,d
$$

$4d^2$ attenzione + $8d^2$ feedforward ($d_{ff} = 4d$) per strato, più l'embedding $E$ (weight tying, niente bias e layer norm). GPT-3: 174,6B; GPT-2 XL: 1,55B.

**Memoria della KV cache** ([L17, slide 47](L17-pretraining-dei-modelli-linguistici.md#p-47))

$$
M_{KV} = 2\cdot L\cdot d_{kv}\cdot b\cdot T
$$

Key e value ($d_{kv}$ numeri ciascuno, $= d$ senza GQA) per strato, $b$ byte per numero, $T$ token. GPT-3 a 16 bit: 4,7 MB per token, 9,7 GB per 2.048 token.

**Calcoli di key e value in generazione** ([L17, slide 45](L17-pretraining-dei-modelli-linguistici.md#p-45))

$$
\text{senza cache: } \sum_{i=1}^{n} i = \frac{n(n+1)}{2},\qquad \text{con cache: } n
$$

Per strato, generando $n$ token. Per $n = 1000$: 500.500 contro 1.000.

### Decoding

**Greedy decoding** ([L15, slide 38](L15-transformer-embedding-lm-head-e-decoding.md#p-38))

$$
\hat w_t = \operatorname{argmax}_{w\in V} P(w\mid w_{\lt t})
$$

Sempre il token più probabile; deterministico. Coincide con l'argmax dei logit.

**Probabilità di una sequenza generata** ([L15, slide 40](L15-transformer-embedding-lm-head-e-decoding.md#p-40))

$$
P(w_1,\dots,w_T) = \prod_{t=1}^{T} P(w_t\mid w_{\lt t})
$$

Base del confronto fra greedy e beam search: yes yes EOS $0{,}5\cdot0{,}4\cdot1 = 0{,}20$, ok ok EOS $0{,}4\cdot0{,}7\cdot1 = 0{,}28$.

**Random sampling** ([L15, slide 42](L15-transformer-embedding-lm-head-e-decoding.md#p-42))

$$
w_t\sim P(w\mid w_{\lt t}),\qquad w_t = \min\{k : \textstyle\sum_{j\le k} y_j \gt r\},\ r\sim U[0,1)
$$

Si estrae il token secondo la sua probabilità, fino a EOS; in pratica con le cumulate e un numero casuale $r$.

**Temperature sampling** ([L15, slide 47](L15-transformer-embedding-lm-head-e-decoding.md#p-47))

$$
y = \mathrm{softmax}(u/\tau)
$$

$\tau\lt1$ più appuntita ($\tau\to0$: greedy), $\tau\gt1$ più piatta ($\tau\to\infty$: uniforme), $\tau = 1$ softmax normale. Conserva l'ordine. Esempio: logit 1,2; 0,9; 0,1; -0,5 con $\tau = 0{,}5$: 0,59; 0,32; 0,07; 0,02.

**Top-k (rinormalizzazione)** ([L15, slide 51](L15-transformer-embedding-lm-head-e-decoding.md#p-51))

$$
\tilde P(w) = \frac{P(w)}{\sum_{w'\in V^{(k)}} P(w')}\ \ \text{per } w\in V^{(k)},\ \ 0 \text{ altrimenti}
$$

$V^{(k)}$ = i $k$ token più probabili. $k = 1$ greedy, $k = |V|$ random sampling. Esempio $k = 2$: 0,44/0,77 = 0,57 e 0,33/0,77 = 0,43.

**Top-p (nucleus)** ([L15, slide 54](L15-transformer-embedding-lm-head-e-decoding.md#p-54))

$$
V^{(p)} = \text{il più piccolo insieme tale che } \sum_{w\in V^{(p)}} P(w\mid w_{\lt t}) \ge p
$$

Token presi in ordine di probabilità decrescente fino a superare (o raggiungere) $p$, poi rinormalizzati. Esempio $p = 0{,}9$ sulle cumulate 0,44; 0,77; 0,92: tre token, 0,48; 0,36; 0,16.

### Decodifica

**Softmax con temperatura** ([L16](L16-laboratorio-dagli-n-gram-a-gpt.md))

$$
p_i=\frac{e^{z_i/\tau}}{\sum_j e^{z_j/\tau}}
$$

$\tau&lt;1$ più appuntita (verso il greedy), $\tau&gt;1$ più piatta; i pesi non cambiano. Top-$k$: si tengono i $k$ logit maggiori.

### Pretraining

**Cross-entropy loss su una posizione** ([L17, slide 17](L17-pretraining-dei-modelli-linguistici.md#p-17))

$$
L_{CE}(\hat y_t, y_t) = -\sum_{w\in V} y_t[w]\log\hat y_t[w]
$$

Distanza fra distribuzione predetta $\hat y_t$ e corretta $y_t$ sul vocabolario (Eq. 7.53).

**Loss con target one-hot** ([L17, slide 17](L17-pretraining-dei-modelli-linguistici.md#p-17))

$$
L_{CE}(\hat y_t, y_t) = -\log\hat y_t[w_{t+1}]
$$

Con $y_t$ one-hot resta meno il log della probabilità del vero token successivo (Eq. 7.54). Esempio: 0,44 dà 0,82 nat.

**Loss media di una sequenza** ([L17, slide 21](L17-pretraining-dei-modelli-linguistici.md#p-21))

$$
L_{CE}(\text{batch di lunghezza }T) = \frac1T\sum_{t=1}^{T}-\log\hat y_t[w_{t+1}]
$$

Media sulle $T$ posizioni (Eq. 7.55); esempio della lezione 4,26/5 = 0,85.

**Loss di un modello uniforme** ([L17, slide 18](L17-pretraining-dei-modelli-linguistici.md#p-18))

$$
L_{CE} = \ln|V|,\qquad \mathrm{PP} = |V|
$$

Probabilità $1/|V|$ a ogni token: loss di partenza tipica. $\ln 50.000 = 10{,}82$, $\ln1.500 = 7{,}31$.

**Finestre per batch** ([L17, slide 23](L17-pretraining-dei-modelli-linguistici.md#p-23))

$$
\#\text{finestre} = \frac{\text{token per batch}}{N},\qquad \#\text{passi per epoca} = \frac{D}{\text{token per batch}}
$$

GPT-3: $3{,}2\cdot10^6/2048\approx1.560$ finestre; 300B token in 93.750 passi.

### Scaling

**Scaling law di Kaplan** ([L17, slide 50](L17-pretraining-dei-modelli-linguistici.md#p-50))

$$
L(N) = \left(\frac{N}{8{,}8\cdot10^{13}}\right)^{-0{,}076},\quad L(D) = \left(\frac{D}{5{,}4\cdot10^{13}}\right)^{-0{,}095},\quad L(C_{min}) = \left(\frac{C_{min}}{2{,}3\cdot10^{8}}\right)^{-0{,}050}
$$

Test loss in nat; $N$ parametri senza embedding, $D$ token, $C$ in PF-giorni. Rette in log-log. $L(10^9) = 2{,}38$.

**Costo di training** ([L17, slide 51](L17-pretraining-dei-modelli-linguistici.md#p-51))

$$
C \approx 6\,N\,D
$$

FLOP: 2 per parametro per token nel forward, 4 nel backward. Chinchilla $5{,}88\cdot10^{23}$, GPT-3 $3{,}15\cdot10^{23}$, Llama 3.1 8B $7{,}2\cdot10^{23}$.

**Allocazione compute-optimal (Hoffmann et al., 2022)** ([L17, slide 51](L17-pretraining-dei-modelli-linguistici.md#p-51))

$$
N_{opt}\propto C^{1/2},\qquad D_{opt}\propto C^{1/2},\qquad D\approx20N\ \Rightarrow\ N_{opt} = \sqrt{C/120}
$$

Modello e dati crescono insieme; con 4 volte il calcolo raddoppiano entrambi. Chinchilla: 70B e 1,4T.

### Post-training

**Loss dell'instruction tuning (solo risposta)** ([L18, slide 18](L18-post-training-i-instruction-tuning-lora-e-prompting.md#p-18))

$$
L = -\frac{1}{|R|}\sum_{t\in R}\log P(w_t\mid w_{<t}) = \frac{\sum_t m_t\,\ell_t}{\sum_t m_t},\quad \ell_t = -\log P(w_t\mid w_{<t})
$$

Cross-entropy media sul token successivo, ma solo sulle posizioni $R$ della risposta (maschera $m_t = 1$; 0 per istruzione e marcatori). Esempio *buona notte*: 0,415 (0,42 nella slide) contro 1,06 su tutti i token.

**Memoria del fine-tuning completo (Adam, mixed precision)** ([L18, slide 31](L18-post-training-i-instruction-tuning-lora-e-prompting.md#p-31))

$$
\text{byte per parametro} = \underbrace{2}_{\text{pesi 16 bit}} + \underbrace{2}_{\text{gradienti}} + \underbrace{4+4+4}_{\text{copia 32 bit, } m,\ v} = 16
$$

Senza attivazioni (Rajbhandari et al., 2020). Modello da $N$ parametri: $16N$ byte; 7B: 112 GB.

**Forward pass di LoRA** ([L18, slide 35](L18-post-training-i-instruction-tuning-lora-e-prompting.md#p-35))

$$
h = xW + xAB,\qquad W\in\mathbb R^{k\times d},\ A\in\mathbb R^{k\times r},\ B\in\mathbb R^{r\times d},\ r\ll\min(k,d)
$$

$W$ congelata; si addestrano solo $A$ e $B$. $\Delta W = AB$ ha rango al più $r$. Si calcola come $(xA)B$.

**Parametri addestrati da LoRA** ([L18, slide 38](L18-post-training-i-instruction-tuning-lora-e-prompting.md#p-38))

$$
\#\text{LoRA} = r(k+d),\qquad \frac{r(k+d)}{kd} = \frac{r}{d}+\frac{r}{k}
$$

Contro $kd$ del fine-tuning completo. $k = d = 4096$, $r = 8$: 65 536 contro 16 777 216, lo 0,39%. Pareggio per $r = kd/(k+d)$ (2048 per $k = d = 4096$).

**Inizializzazione e gradienti di LoRA** ([L18, slide 35](L18-post-training-i-instruction-tuning-lora-e-prompting.md#p-35))

$$
A\sim\text{casuale},\ B = 0;\qquad \frac{\partial L}{\partial A} = G B^\top,\quad \frac{\partial L}{\partial B} = A^\top G,\quad G = \frac{\partial L}{\partial (W+AB)}
$$

All'inizio $AB = 0$: il modello è quello preaddestrato. Se anche $A = 0$ entrambi i gradienti sono nulli e l'addestramento non parte.

**Fusione dei pesi LoRA (merge)** ([L18, slide 39](L18-post-training-i-instruction-tuning-lora-e-prompting.md#p-39))

$$
x(W + AB) = xW + (xA)B \;\Rightarrow\; W' = W + AB
$$

Dopo l'addestramento si sostituisce $W$ con $W'$: nessun costo in più all'inferenza. Per cambiare modulo: $W + A_1B_1 - A_1B_1 + A_2B_2$.

**Costo del prodotto con LoRA** ([L18, slide 37](L18-post-training-i-instruction-tuning-lora-e-prompting.md#p-37))

$$
(xA)B:\ r(k+d)\ \text{moltiplicazioni}\qquad x(AB):\ krd + kd
$$

Esempio $k = d = 3$, $r = 1$: 6 contro 18. Nell'addestramento non si costruisce mai $AB$.

**Fattore di scala di LoRA (implementazioni)** ([L18, slide 35](L18-post-training-i-instruction-tuning-lora-e-prompting.md#p-35))

$$
h = xW + \frac{\alpha}{r}\,xAB
$$

Non nelle slide (equivale ad $\alpha = r$); nell'articolo di Hu et al. e nelle librerie. Esempio $r = 8$, $\alpha = 16$: scala 2.

**Livelli di quantizzazione e bit effettivi** ([L18, slide 40](L18-post-training-i-instruction-tuning-lora-e-prompting.md#p-40))

$$
\#\text{livelli} = 2^b,\qquad \text{bit/peso} = b + \frac{32}{\text{blocco}}
$$

$b = 16$: 65 536 valori; $b = 4$: 16 livelli. Con scala a 32 bit ogni 64 pesi: 4,5 bit per peso, 7B in circa 3,9 GB.

**Memoria di LoRA e QLoRA (pesi congelati)** ([L18, slide 41](L18-post-training-i-instruction-tuning-lora-e-prompting.md#p-41))

$$
M_{\text{full}} \approx 16N,\quad M_{\text{LoRA}} \approx 2N,\quad M_{\text{QLoRA}} \approx 0{,}5N\ \text{byte}
$$

Trascurando le matrici LoRA e le attivazioni. 7B: 112 / 14 / 3,5 GB; 65B in QLoRA: 32,5 GB (una GPU da 48 GB).

### Preferenze

**Coppie da una classifica** ([L19, slide 10](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-10))

$$
N \succ \dots:\quad \binom{N}{2} = \frac{N(N-1)}{2}\ \text{coppie};\qquad \text{solo il migliore: } N-1
$$

Classifica di $N$ output: tutte le coppie. $N = 4$: 6; InstructGPT da 4 a 9 output: da 6 a 36. Scelta del solo migliore: $N-1$ coppie.

**Modello di Bradley-Terry** ([L19, slide 14](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-14))

$$
P(o_i \succ o_j \mid x) = \frac{1}{1+e^{-(z_i - z_j)}} = \sigma(z_i - z_j)
$$

Sigmoide della differenza dei punteggi nascosti. $\sigma(-1) = 0{,}27$, $\sigma(0) = 0{,}5$, $\sigma(1) = 0{,}73$, $\sigma(3) = 0{,}95$. Invariante se si aggiunge una costante a tutti i punteggi.

**Differenza come log-odds** ([L19, slide 14](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-14))

$$
z_i - z_j = \log\frac{P(o_i\succ o_j\mid x)}{1 - P(o_i\succ o_j\mid x)}
$$

La differenza dei punteggi è il logit della preferenza; risolvendo per $P$ si ottiene Bradley-Terry. Per $P = 0{,}8$: $\ln 4 = 1{,}386$.

### Reward model

**Probabilità con il reward model** ([L19, slide 15](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-15))

$$
P(o_i \succ o_j \mid x) = \sigma\big(r(x,o_i) - r(x,o_j)\big)
$$

Il reward appreso $r(x,o)$ prende il posto del punteggio $z$.

**Loss del reward model** ([L19, slide 16](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-16))

$$
L_{CE} = -\mathbb{E}_{(x,o_w,o_l)\sim D}\big[\log\sigma\big(r(x,o_w) - r(x,o_l)\big)\big]
$$

Binary cross-entropy (negative log-likelihood) delle preferenze osservate, target $P(o_w\succ o_l) = 1$. Coppia a pari reward: $\ln 2 = 0{,}693$. Esempio della slide: media 1,04.

**Gradiente rispetto alla differenza** ([L19, slide 18](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-18))

$$
\frac{\partial L}{\partial r_w} = -(1-\sigma(r_w - r_l)),\qquad \frac{\partial L}{\partial r_l} = 1-\sigma(r_w - r_l)
$$

La discesa alza $r_w$ e abbassa $r_l$ con forza $1-\sigma$: massima per le coppie ordinate male.

### RLHF

**Reward atteso** ([L19, slide 25](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-25))

$$
\mathbb{E}_{o\sim\pi(\cdot\mid x)}[r(x,o)] = \sum_o \pi(o\mid x)\,r(x,o)
$$

Media dei reward pesata con le probabilità, $\pi(o\mid x)$ prodotto delle probabilità dei token. Giocattolo: 1,5 prima, 2,35 dopo. Con un LLM si stima campionando.

**Obiettivo di RL** ([L19, slide 27](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-27))

$$
\pi^* = \arg\max_{\pi_\theta}\ \mathbb{E}_{x\sim D,\ o\sim\pi_\theta(o\mid x)}\big[r(x,o)\big]
$$

Prompt dal dataset, output dalla policy in training, punteggio dal reward model.

**Obiettivo con penalità KL** ([L19, slide 28](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-28))

$$
\pi^* = \arg\max_{\pi_\theta}\ \mathbb{E}_{x\sim D,\ o\sim\pi_\theta}\Big[r(x,o) - \beta\log\frac{\pi_\theta(o\mid x)}{\pi_{\mathrm{ref}}(o\mid x)}\Big]
$$

$\pi_{\mathrm{ref}}$ è il modello di partenza (SFT), $\beta$ il peso della penalità. Esempio: $r = 0{,}8$, rapporto 4, $\beta = 0{,}2$: $0{,}8 - 0{,}277 = 0{,}523$.

**Divergenza KL** ([L19, slide 28](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-28))

$$
D_{KL}(\pi_\theta\,\|\,\pi_{\mathrm{ref}}) = \mathbb{E}_{o\sim\pi_\theta}\Big[\log\frac{\pi_\theta(o\mid x)}{\pi_{\mathrm{ref}}(o\mid x)}\Big] \ge 0
$$

Media del log-rapporto sugli output della policy; 0 solo se le distribuzioni coincidono; non simmetrica.

**Passo di SFT** ([L19, slide 29](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-29))

$$
\theta \leftarrow \theta + \eta\,\nabla_\theta\log\pi_\theta(o\mid x)
$$

$o$ è la risposta del dataset: la si rende più probabile.

**REINFORCE (policy gradient)** ([L19, slide 29](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-29))

$$
\theta \leftarrow \theta + \eta\,r(x,o)\,\nabla_\theta\log\pi_\theta(o\mid x),\quad o\sim\pi_\theta
$$

SFT sui propri campioni pesato dal reward (Williams, 1992). Viene da $\nabla\mathbb{E}[r] = \mathbb{E}[r\,\nabla\log\pi]$.

**Policy gradient con baseline (advantage)** ([L19, slide 30](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-30))

$$
\theta \leftarrow \theta + \eta\,\big(r(x,o) - b\big)\,\nabla_\theta\log\pi_\theta(o\mid x)
$$

$b$ = reward atteso della policy; $r - b$ è l'advantage. Giocattolo con $b = 1{,}5$: $+1{,}5$, $+0{,}5$, $-0{,}5$, $-1{,}5$.

### DPO

**Loss di DPO** ([L19, slide 35](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-35))

$$
L_{\mathrm{DPO}} = -\log\sigma\Big(\beta\log\frac{\pi_\theta(o_w\mid x)}{\pi_{\mathrm{ref}}(o_w\mid x)} - \beta\log\frac{\pi_\theta(o_l\mid x)}{\pi_{\mathrm{ref}}(o_l\mid x)}\Big)
$$

Loss del reward model con reward implicito $\beta\log\pi_\theta/\pi_{\mathrm{ref}}$. $\beta$ tipico 0,01-0,1. Vale $\ln2$ all'inizio ($\pi_\theta = \pi_{\mathrm{ref}}$). Esempio: log-rapporti $+1$ e $-1$, $\beta = 0{,}5$: 0,313.

**Reward in funzione della policy ottima** ([L19, slide 35](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-35))

$$
r(x,o) = \beta\log\frac{\pi^*(o\mid x)}{\pi_{\mathrm{ref}}(o\mid x)} + \beta\log Z(x),\qquad Z(x) = \sum_o \pi_{\mathrm{ref}}(o\mid x)\,e^{r(x,o)/\beta}
$$

Inversione della soluzione in forma chiusa dell'obiettivo con KL (eq. 8.10-8.11 del libro); in Bradley-Terry $Z(x)$ si cancella. Non nelle slide, nel libro.

### RL per il ragionamento

**Reward verificabile** ([L19, slide 41](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-41))

$$
r(x,o) = \begin{cases}1 & \text{risposta corretta o vincoli rispettati}\\ 0 & \text{altrimenti}\end{cases}
$$

Calcolato da un programma, senza reward model.

**Advantage di GRPO** ([L19, slide 42](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-42))

$$
A_i = \frac{r_i - \mathrm{mean}(r_1,\dots,r_G)}{\mathrm{std}(r_1,\dots,r_G) + \varepsilon}
$$

Baseline = media del gruppo di $G$ risposte, std per la scala ($\varepsilon$ piccolo, la costante della slide). $[1,1,0,0,0,1]$: advantage $\pm1$. Gli advantage di un gruppo sommano a 0.

## Correzioni alle slide

- **L2, slide 35** (Training su un corpus piccolo: inizio): n e non è «più frequente di ogni altra coppia»: è un pareggio. [Dettagli](L02-parole-e-token.md#p-35)
- **L3, slide 6** (Disgiunzione di caratteri: le parentesi quadre): r"a^b" non trova mai «a^b» in Python. [Dettagli](L03-elaborazione-del-testo.md#p-6)
- **L3, slide 31** (Un tokenizer a espressioni regolari (NLTK)): Il pattern non produce «82%» come dice il commento. [Dettagli](L03-elaborazione-del-testo.md#p-31)
- **L3, slide 34** (Lo stemmer di Porter): «doing → doe» e «policy → polic» non sono output di Porter. [Dettagli](L03-elaborazione-del-testo.md#p-34)
- **L4, slide 18** (Conteggi bigram: sparsità): Gli zeri sono la metà delle celle, non la maggioranza. [Dettagli](L04-modelli-linguistici-n-gram.md#p-18)
- **L4, slide 19** (Probabilità bigram): Cella food → chinese: 0,00091, non 0,00092. [Dettagli](L04-modelli-linguistici-n-gram.md#p-19)
- **L7, slide 9** (Softmax di un vettore: un esempio): La somma degli esponenziali è 33,23, non 33,24. [Dettagli](L07-regressione-logistica-multinomiale-e-valutazione.md#p-9)
- **L8, slide 5** (Il compito di tagging): Janet è PROPN, non NOUN. [Dettagli](L08-sequence-labelling-pos-tagging-e-ner.md#p-5)
- **L8, slide 12** (Il tagset Penn Treebank): La tabella mostra 33 tag, non 36: manca l'ultima riga. [Dettagli](L08-sequence-labelling-pos-tagging-e-ner.md#p-12)
- **L8, slide 57** (Il backtrace di Viterbi): Due valori della figura sono sbagliati. [Dettagli](L08-sequence-labelling-pos-tagging-e-ner.md#p-57)
- **L8, slide 65** (BIO tagging: un esempio): La tabella non è il BIO della frase sopra. [Dettagli](L08-sequence-labelling-pos-tagging-e-ner.md#p-65)
- **L10, slide 42** (L'idf in Shakespeare): idf di Falstaff: 0,966, non 0,967. [Dettagli](L10-semantica-vettoriale.md#p-42)
- **L10, slide 54** (PPMI: un esempio svolto): pmi(cherry, computer) = −6,70, non −6,47. [Dettagli](L10-semantica-vettoriale.md#p-54)
- **L11, slide 50** (Analogie: le cautele): potato, non «potatoe». [Dettagli](L11-embedding-word2vec.md#p-50)

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
- **L9** · VADER su una recensione: i quattro punteggi: neg, neu e pos non sono percentuali del testo
- **L9** · VADER su una recensione: i quattro punteggi: (compound + 1)/2 non è una probabilità
- **L9** · A2. Quanto è ambiguo l'inglese?: La check cell di A2 accetta una funzione sbagliata (e l'output salvato è sbagliato)
- **L9** · A5. Fuori dal dominio: spaCy legge Dante: Dante non scende al 56%
- **L12** · Concorrente B: TF-IDF: L'output salvato della TF-IDF (0,865) non viene da questo codice
- **L12** · Esercizio 1: la correlazione di Spearman: La check cell dell'esercizio 1 non riconosce una funzione non implementata
- **L16** · Cross-entropy e perplexity su testo held-out: La colonna contexts conta anche i contesti della validazione
- **L17** · Scaling in miniatura: Il commento della cella 23 non è robusto
- **L18** · Che cosa ha imparato: formato e quando fermarsi: Fragilità: molte istruzioni non dicono quale funzione

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

### L8 · Sequence labelling: PoS tagging e NER

<details><summary>Che cos'è il sequence labelling? Confronta PoS tagging e NER.</summary>

Traccia: (1) data $x_1\dots x_n$, produrre $y_1\dots y_n$ della stessa lunghezza, un'etichetta per parola; le etichette non sono indipendenti; (2) PoS tagging: ogni parola ha esattamente un tag, è un problema di disambiguazione (*book* nome/verbo); (3) NER: l'unità è uno span di lunghezza ignota, quindi c'è anche segmentazione, oltre all'ambiguità di tipo (*Washington*); (4) il BIO riduce la NER a etichettatura per parola, così gli stessi modelli (HMM, CRF, neurali) servono per entrambi; (5) valutazione: accuracy per il PoS, P/R/F1 sulle entità per la NER.

</details>

<details><summary>Come si definiscono le parti del discorso? Classi aperte e chiuse, UD e Penn Treebank.</summary>

Traccia: (1) per comportamento grammaticale, non per significato: distribuzione (*very young* sì, *very cat* no) e morfologia (*happy → happiness*); il significato è solo una tendenza; (2) classi chiuse: function word corte, frequenti, ambigue (ADP, AUX, DET, PRON...); aperte: nomi, verbi, aggettivi, avverbi, interiezioni, nuovi membri di continuo (parole sconosciute); (3) UD: 17 tag (6 aperti, 8 chiusi, 3 altri), universali per 100+ lingue, distinzioni fini come feature morfologiche; (4) Penn: 36 tag di parola (45 con la punteggiatura), specifici dell'inglese, es. VB/VBD/VBG/VBN/VBP/VBZ contro un solo VERB.

</details>

<details><summary>Quanto è difficile il PoS tagging? Ambiguità, baseline e stato dell'arte.</summary>

Traccia: (1) l'85-86% dei tipi ha un solo tag, ma il 14-15% ambiguo copre il 55-67% dei token, perché sono le parole frequenti (*back* ha sei tag); (2) baseline most-frequent-tag: ogni parola col suo tag più frequente, NN per le sconosciute: circa 92% sul WSJ; (3) tagger supervisionati (HMM, CRF, BERT) circa 97%, pari all'accordo umano; (4) quindi solo 5 punti fra baseline e tetto: confrontare sempre con la baseline; (5) i numeri valgono nel dominio: su testi storici o social si perdono 15-40 punti.

</details>

<details><summary>Definisci un hidden Markov model e le sue due assunzioni.</summary>

Traccia: (1) catena di Markov: stati $Q$, matrice $A$ con righe che sommano a 1, iniziale $\pi$; ipotesi di Markov $P(q_i\mid q_{1:i-1}) = P(q_i\mid q_{i-1})$; un bigram LM è una catena sulle parole; (2) HMM: gli stati (tag) sono nascosti, si osservano le parole; si aggiungono le emissioni $B$, $b_i(o_t) = P(o_t\mid q_i)$; (3) assunzione 1: Markov sugli stati; assunzione 2: indipendenza delle osservazioni, $o_i$ dipende solo da $q_i$; (4) conseguenza: $P(w, t) = \prod_i P(t_i\mid t_{i-1})P(w_i\mid t_i)$, due famiglie di parametri, transizioni ed emissioni.

</details>

<details><summary>Come si stimano le matrici A e B di un tagger HMM? Che differenza c'è fra P(will|MD) e P(MD|will)?</summary>

Traccia: (1) per massima verosimiglianza, contando su un corpus annotato: $P(t_i\mid t_{i-1}) = C(t_{i-1},t_i)/C(t_{i-1})$, $P(w_i\mid t_i) = C(t_i,w_i)/C(t_i)$; (2) esempio WSJ: $P(\text{VB}\mid\text{MD}) = 10471/13124 = 0{,}80$, $P(\textit{will}\mid\text{MD}) = 4046/13124 = 0{,}31$; (3) $P(\textit{will}\mid\text{MD})$ è un'emissione: "se genero un modale, quanto spesso è *will*"; $P(\text{MD}\mid\textit{will})$ è la posterior, "quanto spesso *will* è un modale" (quella che userebbe la baseline); (4) senza smoothing coppie mai viste hanno probabilità zero: servono smoothing e gestione delle parole sconosciute.

</details>

<details><summary>Deriva la formula di decodifica di un tagger HMM bigram.</summary>

Traccia: (1) obiettivo $\hat t = \operatorname{argmax}_t P(t_{1:n}\mid w_{1:n})$; (2) Bayes: $P(w\mid t)P(t)/P(w)$; (3) $P(w)$ è costante rispetto ai tag, si elimina; (4) indipendenza delle osservazioni: $P(w_{1:n}\mid t_{1:n})\approx\prod P(w_i\mid t_i)$; (5) Markov/bigram: $P(t_{1:n})\approx\prod P(t_i\mid t_{i-1})$; (6) risultato $\operatorname{argmax}\prod_i P(w_i\mid t_i)P(t_i\mid t_{i-1})$: emissioni $B$ per transizioni $A$; (7) è la stessa struttura di Naive Bayes (verosimiglianza per prior) con una sequenza come classe; il max su $N^n$ sequenze si fa con Viterbi.

</details>

<details><summary>Descrivi l'algoritmo di Viterbi e la sua complessità.</summary>

Traccia: (1) reticolo $N\times T$; $v_t(j)$ = probabilità del miglior cammino che finisce nello stato $j$ al tempo $t$; (2) inizializzazione $v_1(j) = \pi_j b_j(o_1)$; ricorsione $v_t(j) = \max_i v_{t-1}(i)a_{ij}b_j(o_t)$ con backpointer = argmax; terminazione $\max_j v_T(j)$; backtrace; (3) correttezza: due cammini che arrivano nello stesso stato hanno lo stesso futuro (Markov), quindi basta tenere il migliore (principio di ottimalità); (4) costo $O(N^2T)$ contro $O(N^T)$ della forza bruta: 45 tag e 20 parole, 40.500 operazioni contro $10^{33}$ cammini; memoria $O(NT)$; (5) in pratica in log-spazio contro l'underflow.

</details>

<details><summary>In che senso Viterbi somiglia alla distanza di edit minima?</summary>

Traccia: (1) entrambi sono programmazione dinamica su una tabella 2D riempita colonna per colonna (o cella per cella) da sottoproblemi già risolti; (2) distanza di edit: $D[i,j] = \min$ su tre predecessori (cancellazione, inserimento, sostituzione) di costo precedente + costo dell'operazione; Viterbi: $v_t(j) = \max$ su $N$ predecessori di probabilità precedente × transizione × emissione (in log: somma); (3) entrambi salvano backpointer e ricostruiscono la soluzione col backtrace (allineamento contro sequenza di tag); (4) entrambi evitano l'enumerazione esponenziale (allineamenti o sequenze) grazie alla sottostruttura ottima.

</details>

<details><summary>Perché non basta scegliere per ogni parola il tag con l'emissione più alta? Usa l'esempio The fans watch the race.</summary>

Traccia: (1) solo $B$ dà DT VB NN DT VB: tre errori su cinque; (2) $b_j(w) = P(w\mid j)$ non tiene conto del contesto (e non è nemmeno la posterior); (3) le transizioni penalizzano VB dopo DT ($0{,}1$ contro $0{,}9$) e vietano DT dopo NN ($0$); (4) nel reticolo a *watch* la cella migliore è NN (0,0027) ma ogni cammino da lì muore perché NN→DT = 0: vince VB (0,00135); (5) risultato DT NN VB DT NN con probabilità $1{,}215\cdot10^{-5}$; (6) morale: un tagger greedy sbaglia, Viterbi tiene il miglior cammino per ogni stato e decide solo alla fine.

</details>

<details><summary>Che cos'è il BIO tagging? Quanti tag servono e quali sono le varianti?</summary>

Traccia: (1) B = primo token di uno span, I = token interni, O = fuori; tag tipizzati (B-PER, I-ORG); (2) stessa informazione della notazione a parentesi, ma un'etichetta per parola: la NER diventa sequence labelling; (3) con $n$ tipi: $2n+1$ tag (9 per PER, LOC, ORG, GPE); (4) IO: $n+1$ tag, perde i confini fra entità adiacenti dello stesso tipo; BIOES: $4n+1$, aggiunge E (fine) e S (span di una parola); (5) vincolo: I-X solo dopo B-X o I-X; (6) più tag aumentano il costo di Viterbi in modo quadratico.

</details>

<details><summary>Perché un HMM non basta per la NER? Quali feature usa un CRF?</summary>

Traccia: (1) nella NER dominano le parole sconosciute, per cui $P(w\mid t)$ non è stimata; (2) gli indizi utili sono maiuscole, forma, affissi, parole vicine (*Mr.*, *Inc.*), presenza in un gazetteer: l'HMM può usare solo $P(t\mid t)$ e $P(w\mid t)$ e vede i vicini solo tramite il loro tag; aggiungere indizi a un modello generativo richiede condizionamenti sempre più complessi; (3) il CRF accetta feature arbitrarie: identità della parola e dei vicini, PoS, word shape e short shape (DC10-30 → XXdd-dd, Xd-d), prefissi e suffissi fino a 4, gazetteer, embedding; (4) le feature si generano da template, con cutoff sotto 5 occorrenze.

</details>

<details><summary>Definisci il CRF a catena lineare. Che relazione ha con la regressione logistica multinomiale?</summary>

Traccia: (1) $P(Y\mid X) = \exp(\sum_k w_k F_k(X,Y))/Z(X)$, $Z(X) = \sum_{Y'}\exp(\sum_k w_k F_k(X,Y'))$; (2) le feature globali sono somme di locali: $F_k = \sum_i f_k(y_{i-1}, y_i, X, i)$, quindi $K$ pesi fissi per frasi di ogni lunghezza; (3) lineare: ogni feature locale vede solo $y_i$ e $y_{i-1}$ (ma tutto $X$), il che rende possibili Viterbi e forward-backward; un CRF generale può usare tag lontani, con inferenza più cara; (4) è una regressione logistica multinomiale in cui le classi sono tutte le sequenze di tag: punteggio lineare nelle feature, softmax su $\mathcal Y$; per $n = 1$ coincide con essa.

</details>

<details><summary>Confronta HMM e CRF: generativo contro discriminativo.</summary>

Traccia: (1) HMM: modella la congiunta $P(X,Y) = P(X\mid Y)P(Y)$ e passa da Bayes; parametri = probabilità contate (MLE), trasparente ed economico; (2) CRF: modella direttamente $P(Y\mid X)$, normalizzazione globale sulla sequenza, pesi appresi per gradiente; (3) l'HMM fa assunzioni forti sull'input (ogni parola dipende solo dal suo tag), il CRF non fa assunzioni su $X$ e accetta feature sovrapposte; (4) parallelo esatto con Naive Bayes contro regressione logistica (L6); (5) un HMM equivale a un CRF lineare con template $\langle y_{i-1},y_i\rangle$ e $\langle y_i, x_i\rangle$ e pesi $\log a$, $\log b$; (6) entrambi si decodificano con Viterbi (prodotti per l'HMM, somme di pesi per il CRF); entrambi ~97% sul PoS inglese.

</details>

<details><summary>Come si addestra un CRF e come si trova la sequenza migliore?</summary>

Traccia: (1) training supervisionato come la regressione logistica: massimizzare la log-verosimiglianza condizionata $\sum\log P(Y\mid X)$ con SGD; le attese delle feature sotto il modello si calcolano con forward-backward; regolarizzazione L1/L2 importante (milioni di feature); (2) inferenza: nell'argmax si eliminano exp (monotono) e $Z(X)$ (costante per $X$): resta $\operatorname{argmax}_Y\sum_i\sum_k w_k f_k(y_{i-1},y_i,X,i)$; (3) Viterbi con somme: $v_t(j) = \max_i[v_{t-1}(i) + \sum_k w_k f_k(i, j, X, t)]$, matrice $N\times T$ con backpointer; funziona perché ogni passo dipende da un solo tag precedente.

</details>

<details><summary>Come si valuta un sistema di NER e perché non si usa l'accuracy sui token?</summary>

Traccia: (1) il PoS si valuta con l'accuracy perché ogni token ha un tag; (2) nella NER l'unità è l'entità: uno span predetto è corretto solo se confini e tipo coincidono col gold; precision = corrette/predette, recall = corrette/gold, $F_1$ media armonica; (3) un errore di confine (*Jane* invece di *Jane Villanueva*) costa un FP e un FN; (4) l'accuracy per token è gonfiata dai tanti O (classi sbilanciate) e pesa poco gli errori di confine; (5) disallineamento: si addestra per token, si valuta per entità; (6) per confrontare due sistemi: paired bootstrap sulle $F_1$.

</details>

### L9 · Laboratorio: NLTK e spaCy

<details><summary>Che differenza c'è fra NLTK e spaCy, come filosofia e come modelli?</summary>

Traccia: (1) NLTK cassetta degli attrezzi: funzioni indipendenti su liste di token, le combini tu (tokenizza, poi `pos_tag`, poi `ne_chunk`); (2) spaCy pipeline: `nlp(testo)` restituisce un `Doc` con frasi, lemmi, PoS UD e Penn, dipendenze, entità già calcolati; (3) modelli: NLTK classici (averaged perceptron per il PoS, massima entropia = regressione logistica multinomiale per la NER, regole per Porter e VADER), spaCy piccole reti neurali con un `tok2vec` condiviso; (4) NLTK ricco di corpora e risorse (treebank, WordNet, movie\_reviews), spaCy più veloce e accurato su NER e parsing; (5) entrambi statistici, addestrati su corpora annotati: il dominio conta.

</details>

<details><summary>Come funzionano sent_tokenize e word_tokenize di NLTK, e perché lo stesso codice dà conteggi diversi con versioni diverse?</summary>

Traccia: (1) Punkt: segmentatore non supervisionato che impara abbreviazioni e iniziali per decidere se un punto chiude la frase ([scheda 32 della L3](L03-elaborazione-del-testo.md#p-32)); (2) `word_tokenize` = Punkt + tokenizzatore a regex con convenzioni Penn Treebank: punteggiatura separata, clitici staccati (*it'll* → *it* + *'ll*); (3) il punto viene staccato solo a fine frase, quindi un errore di segmentazione lascia token come *it.*; (4) su Pinocchio NLTK 3.9 dà 2.298 frasi e 53.332 token, la 3.10 3.410 frasi e 53.814 token; (5) conseguenza: tokenizzazione e versione della libreria vanno documentate, perché cambiano tutti i numeri a valle.

</details>

<details><summary>Che cos'è la PMI e come si usa per trovare collocazioni? Quali sono i suoi limiti?</summary>

Traccia: (1) collocazione = parole che co-occorrono più del caso; (2) $\text{PMI} = \log_2 P(w_1w_2)/(P(w_1)P(w_2)) = \log_2 P(w_2\mid w_1)/P(w_2)$, con stime MLE $\log_2 C(w_1w_2)N/(C(w_1)C(w_2))$; (3) 0 se indipendenti, positiva se si attraggono; esempio *Talking Cricket* 10,5 bit, *of the* 2,4; (4) limite: bias verso gli eventi rari, conteggi 1-1-1 danno il massimo $\log_2 N$ (130 bigrammi a pari merito su Pinocchio), quindi filtro di frequenza e filtro sulle stopword; (5) il risultato rivela il corpus: in cima uscivano bigrammi della licenza Gutenberg (datasheet, [scheda 48 della L2](L02-parole-e-token.md#p-48)); (6) la PMI tornerà negli embedding.

</details>

<details><summary>Stemming e lemmatizzazione: differenze, e perché il lemmatizzatore ha bisogno della parte del discorso?</summary>

Traccia: (1) entrambi riducono forme diverse a una forma canonica ([scheda 33 della L3](L03-elaborazione-del-testo.md#p-33)); (2) stemming (Porter): regole sui suffissi, niente dizionario, veloce, il risultato può non essere una parola (*policy → polici*, *was → wa*) e confonde parole diverse (*university, universal → univers*); (3) lemmatizzazione: cerca il lemma in un dizionario (WordNet), restituisce una parola vera; (4) serve la PoS perché il lemma dipende dalla categoria: *better* → *good* (aggettivo) o *well* (avverbio), *was* → *be* solo come verbo, come nome WordNet dà *wa*; (5) spaCy fa il tagging prima e lemmatizza dopo, NLTK richiede di passare `pos` a mano.

</details>

<details><summary>Che cos'è il bag of words? Che cosa perde, e come si recupera un po' di informazione?</summary>

Traccia: (1) un classificatore vuole un vettore di lunghezza fissa; (2) vocabolario $V$, documento → $\mathbf x \in \mathbb R^{|V|}$ binario ($x_j = 1$ se $w_j \in d$) o a conteggi; (3) una feature per parola, decine di migliaia, vettore sparso, nessun lessico scelto a mano: i pesi si imparano ([scheda 30 della L6](L06-regressione-logistica.md#p-30)); (4) perde l'ordine: *I won, you lose* e *I lose, you won* hanno la stessa bag, così *good movie, not bad* e *bad movie, not good*; (5) bigrammi di parole recuperano l'ordine locale (e la negazione: *not bad*), al costo di più feature; n-grammi di caratteri danno robustezza a refusi e parole nuove (Jaccard *rainbow/rainbaw* 3/7).

</details>

<details><summary>Come funziona VADER? Che cosa significano neg, neu, pos e compound?</summary>

Traccia: (1) analizzatore a regole, niente training: lessico di circa 7.500 voci con valenza in $[-4, 4]$ (media di 10 annotatori); (2) regole: negazione $\times(-0{,}74)$, intensificatori $\pm 0{,}293$, maiuscole $+0{,}733$, punti esclamativi $+0{,}292$, *but* (0,5 prima, 1,5 dopo); (3) compound $= s/\sqrt{s^2+15}$ in $(-1, 1)$, soglia convenzionale $\pm 0{,}05$; (4) neg/neu/pos sono quote di una somma in cui le parole neutre valgono 1 e quelle con sentiment $1+|v|$: quote di intensità, **non** percentuali di testo (sulla recensione d'esempio 1 parola negativa su 31 dà neg 8,6%); (5) $(\text{compound}+1)/2$ non è una probabilità; (6) limiti: niente contesto (*sucked me in*), nomi propri con parole negative, *however* non trattato come *but*.

</details>

<details><summary>Togliere le stopword è sempre una buona idea?</summary>

Traccia: (1) le stopword sono parole funzionali frequenti (198 nella lista inglese di NLTK); (2) toglierle aiuta quando interessa *di che cosa* parla un testo: le frequenze di Pinocchio passano da virgole e articoli a *Pinocchio, Marionette, Fairy, Geppetto*; (3) fa danni quando interessa il *come*: la lista contiene *not, no, nor, but, very, too*; (4) esempi: la recensione d'esempio sembra più positiva perché sparisce *very* davanti a *disappointed* (compound da 0,700 a 0,726); *The movie was not good* (−0,34) diventa *movie good* (+0,44); (5) quindi è una scelta che dipende dal compito, da validare sul dev set, non un passo di default.

</details>

<details><summary>Sentiment a regole, con feature fatte a mano, con bag of words, con un transformer: che cosa mostra il confronto sul corpus movie_reviews?</summary>

Traccia: (1) VADER F1 0,715 ma accuracy 0,66: dice positivo al 69,5%, precision 0,615 e recall 0,855; (2) regressione logistica sulle 6 feature della Fig. 4.2: accuracy 0,713, feature povere e correlate con la lunghezza; (3) regressione logistica su bag of words binario: F1 0,871, accuracy 0,868, 39.768 pesi imparati dai dati; tra le parole più pesanti anche indizi di stile del corpus (*script, supposed, both*); (4) DistilBERT su SST-2, mai visto questo corpus: F1 0,840, precision alta e recall bassa; (5) paired bootstrap: bag of words significativamente meglio di VADER e delle 6 feature, non distinguibile da DistilBERT ($p = 0{,}27$); (6) lezione: imparare dai dati del dominio batte le regole, ma il vantaggio può non trasferirsi ad altri domini.

</details>

<details><summary>Quanto è ambiguo il PoS tagging dell'inglese? Che cosa misura la Fig. 18.4 e che cosa si ottiene sul campione di NLTK?</summary>

Traccia: (1) un tipo è ambiguo se compare con 2+ tag; si misura la quota sui tipi e quella sui token; (2) WSJ completo: 14% dei tipi, 55% dei token ([scheda 17 della L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-17)); (3) la differenza: i tipi ambigui sono le parole frequenti (*the, a, back, set, that*); (4) campione del 10%: 9,9% e 36,5%, più bassi perché l'ambiguità si osserva solo se una parola compare abbastanza volte con tag diversi; (5) attenzione al test della funzione: la versione salvata nel notebook dava 11,5% e 2,7% e la check cell non se ne accorgeva (2,7% sui token è incompatibile con l'idea che le parole ambigue siano le frequenti).

</details>

<details><summary>La baseline most-frequent-tag: come funziona, quanto fa nel laboratorio, e perché il confronto con NLTK e spaCy non è alla pari?</summary>

Traccia: (1) ogni parola riceve il tag più frequente nel training, le ignote NN ([scheda 20 della L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-20)); (2) libro 92%; nel laboratorio 87,0% (94,5% sulle note, 19,0% sulle ignote, che sono il 10% del test perché il training è piccolo, 75.000 token); (3) poche regole su forma e suffissi (maiuscola → NNP, cifre → CD, *-ing*, *-ed*, *-ly*, *-s*) portano le ignote al 77% e il totale al 92,8%: le feature che un CRF sa usare; (4) NLTK (96,3%) e spaCy (95,4%) sono addestrati su dati che includono il WSJ, quindi probabilmente anche le frasi di test: contaminazione, numeri ottimistici; (5) un confronto equo richiede lo stesso training e un test mai visto da nessuno.

</details>

<details><summary>Perché la NER si valuta sugli span e non sui token? Fai un esempio numerico.</summary>

Traccia: (1) l'unità di risposta è l'entità: uno span predetto è corretto solo se inizio, fine e tipo coincidono (§18.6, [scheda 81 della L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-81)); (2) $P$ = span corretti / span predetti, $R$ = span corretti / span gold, $F_1$ media armonica; (3) i token O sono la maggioranza (70% nell'esercizio A4), quindi l'accuracy per token è alta anche per sistemi scarsi: spaCy 89,5% sui token ma $F_1 = 0{,}68$ sugli span, NLTK 88,6% e 0,62; (4) un errore di confine (*the University of Padua* contro *University of Padua*) costa un falso positivo e un falso negativo; (5) per passare dai tag BIO agli span serve una funzione come `bio_to_spans`, con la convenzione conlleval per gli I- isolati.

</details>

<details><summary>Che cosa succede a un tagger fuori dal suo dominio? Discuti l'esempio di Dante.</summary>

Traccia: (1) il 97% vale sul dominio di training; su testi lontani l'accuratezza crolla (Dante 75%, Middle English 56%, Twitter 74%: [scheda 21 della L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-21)); (2) cause: parole sconosciute e forme antiche (*cammin*), ordine delle parole diverso (*diritta via* → NOUN + ADV), costruzioni rare nei dati (passato remoto: *ritrovai → ritrovaire*, 3a plurale); (3) esperimento: normalizzando solo forme e ordine, *diritta via* torna giusto ma *ritrovai* resta sbagliato, quindi le cause si separano; (4) anche l'italiano moderno ha errori (*bosco buio* PROPN); (5) caso estremo: il tagger inglese di NLTK sull'italiano (*Mi chiamo Andrea* → NNP NN NNP).

</details>

<details><summary>Come si implementa il paired bootstrap test e come si leggono i risultati del laboratorio?</summary>

Traccia: (1) $\delta(x)$ = accuracy di A meno quella di B sul test set; (2) $b$ test set virtuali di $n$ esempi estratti **con reinserimento** e **appaiati** (stesso esempio per A e B); (3) $p$ = frazione con $\delta(x^{(i)}) \ge 2\delta(x)$ (Eq. 4.48; equivale a centrare la distribuzione in 0); (4) dettagli: conteggi interi invece di accuracy (niente errori di virgola mobile), maggiore o uguale (con il maggiore stretto l'esempio del libro dà 0,145 invece di 0,27); (5) risultati: bag of words contro VADER e contro 6 feature $p &lt; 10^{-4}$, contro DistilBERT $p = 0{,}27$; (6) $p &gt; 0{,}05$ non prova l'equivalenza: servono più dati o cross-validation ([scheda 43 della L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-43)).

</details>

<details><summary>Perché i pesi di un classificatore vanno sempre insieme al suo estrattore di feature? Usa l'esempio della Fig. 4.2.</summary>

Traccia: (1) Fig. 4.2: sei feature, pesi $[2{,}5, -5, -1{,}2, 0{,}5, 2, 0{,}7]$, $b = 0{,}1$, $P(+\mid x) = \sigma(0{,}833) = 0{,}70$ ([scheda 28 della L6](L06-regressione-logistica.md#p-28)); (2) con `word_tokenize` e il lessico VADER il vettore diventa $[4, 2, 1, 3, 0, 4{,}22]$: lessico diverso (*surprises* positiva, *hokey* e *second-rate* assenti) e clitici separati (68 token); (3) stessi pesi, $P(+\mid x) = 0{,}97$; (4) i pesi sono stimati per una precisa distribuzione delle feature: cambiare tokenizzatore o lessico dopo il training cambia le predizioni in silenzio; (5) la cura è riaddestrare con l'estrattore nuovo, e documentare l'intera pipeline (model card, [scheda 51 della L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-51)).

</details>

### L10 · Semantica vettoriale

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

### L11 · Embedding word2vec

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

### L12 · Laboratorio: word embedding

<details><summary>Come si costruisce un embedding da conteggi e perché serve la PPMI?</summary>

Traccia: (1) ipotesi distribuzionale; (2) matrice parola-contesto: finestra $\pm L$, ogni coppia (target, contesto) aggiunge 1 a $C(w,c)$, la riga è il vettore della parola, sparso e interpretabile, $|V|$ dimensioni; (3) similarità con il coseno, non con il prodotto scalare (bias della lunghezza); (4) problema: le parole frequenti (*the*) sono contesto di tutto e rendono simile tutto (nel lab *cats*-*pizza* 0,667 solo per *the*); (5) PPMI: $\max(\log_2\frac{P(w,c)}{P(w)P(c)},0)$ con probabilità sulle coppie (somme di riga e colonna), pesa poco i contesti presenti ovunque, porta *cats*-*pizza* a 0,045; (6) valori negativi tagliati perché inaffidabili; variante $\alpha = 0{,}75$ contro il bias verso i contesti rari.

</details>

<details><summary>Nella PMI di una matrice parola-contesto, perché P(w) è la somma della riga e non la frequenza della parola?</summary>

Traccia: (1) l'evento elementare è una coppia (target, contesto), le $N$ sono le coppie (somma di tutte le celle); (2) una parola al bordo di una frase genera meno coppie di una al centro: nel corpus giocattolo *cats* e *chase* compaiono 2 volte ma generano 2 e 4 coppie; (3) usando somme di riga e colonna le tre probabilità sono stimate sullo stesso spazio di eventi e la PMI vale esattamente 0 in caso di indipendenza; (4) esempio: PPMI(*cats*, *chase*) $= \log_2\frac{1\cdot32}{2\cdot4} = 2$; (5) attenzione a non confondere questa $N$ con quella del tf-idf (documenti).

</details>

<details><summary>Che cosa impara skip-gram con negative sampling? Scrivi la loss e i gradienti.</summary>

Traccia: (1) classificatore binario coppia vera/finta, $P(+\mid w,c) = \sigma(\mathbf c\cdot\mathbf w)$: una regressione logistica in cui i parametri sono gli embedding; (2) positivi dalla finestra, $k$ negativi per positivo estratti con $P_\alpha$, $\alpha = 0{,}75$; (3) loss $-\log\sigma(\mathbf c_{pos}\cdot\mathbf w)-\sum_i\log\sigma(-\mathbf c_{neg_i}\cdot\mathbf w)$; (4) gradienti $[\sigma-1]\mathbf w$, $\sigma_i\mathbf w$, $[\sigma-1]\mathbf c_{pos}+\sum\sigma_i\mathbf c_{neg_i}$, forma (previsto − vero) × input; (5) SGD: il positivo si avvicina, i negativi si allontanano; (6) due matrici $W$ e $C$, si tiene $W$ (gensim) o $W+C$; (7) nel lab la loss iniziale vale $(k+1)\ln2 = 4{,}16$ e il controllo con le derivate numeriche verifica i gradienti.

</details>

<details><summary>Perché word2vec usa due vettori per parola?</summary>

Traccia: (1) $\mathbf w$ come target, $\mathbf c$ come contesto, matrici $W$ e $C$ di $|V|\times d$; (2) con un solo vettore il punteggio di $(w,w)$ sarebbe $\|\mathbf w\|^2\ge0$, sempre alto, mentre una parola quasi mai compare accanto a sé stessa: il training dovrebbe accorciare i vettori, in conflitto con il resto; (3) i due ruoli sono diversi: parole con gli stessi contesti hanno $\mathbf w$ simili perché vengono spinte verso gli stessi $\mathbf c$; (4) dopo il training si tiene $W$ o si usa $W+C$; in gensim $W$ è `wv`, $C$ è `syn1neg`.

</details>

<details><summary>Che effetto ha la dimensione della finestra? E skip-gram contro CBOW?</summary>

Traccia: (1) finestra stretta: vicini che occupano lo stesso ruolo sintattico, similarità di tipo (nel lab, con finestra 2 *hands* ha come vicini *arms, teeth, legs*); (2) finestra larga: vicini tematici, ciò che accade nella stessa scena (*clapped, shook, swore* con finestra 10); (3) per avvicinarsi alla similarità di SimLex conviene una finestra stretta; (4) skip-gram fa un passo per ogni coppia target-contesto (circa $2L$ per token), CBOW uno per token con la media del contesto: CBOW è più veloce (0,8 s contro 3,0 s con finestra 10) e il suo costo cresce poco con la finestra; skip-gram di solito è migliore sulle parole rare.

</details>

<details><summary>Che differenza c'è fra word2vec, GloVe e fasttext?</summary>

Traccia: (1) word2vec: predizione locale, scorre le finestre una alla volta (SGNS o CBOW); (2) GloVe: parte dalla matrice di co-occorrenza globale e impara vettori tali che $\mathbf w\cdot\mathbf c\approx\log X_{wc}$ (più bias): a metà fra conteggi e predizione, stessa materia prima; (3) fasttext: skip-gram su parola e n-grammi di caratteri (3-6), la parola è la somma dei suoi n-grammi, quindi costruisce vettori anche per parole mai viste (`pinocchiesque`) ed è utile per lingue morfologicamente ricche; (4) tutti statici: un vettore per tipo; (5) word2vec e PPMI sono legati: SGNS fattorizza implicitamente una matrice PMI spostata (Levy e Goldberg).

</details>

<details><summary>Come funziona il metodo del parallelogramma e quali cautele richiede?</summary>

Traccia: (1) $a : b :: c : ?$, si cerca la parola più vicina a $\mathbf b-\mathbf a+\mathbf c$; funziona se la relazione è una direzione ($\mathbf{king}-\mathbf{man}\approx\mathbf{queen}-\mathbf{woman}$); (2) distanza euclidea o coseno: per vettori unitari danno la stessa classifica ($\|\mathbf t-\mathbf x\|^2 = \|\mathbf t\|^2+1-2\mathbf t\cdot\mathbf x$); (3) le parole di input vanno escluse: $\mathbf t$ dista da $\mathbf c$ solo $\|\mathbf b-\mathbf a\|$, e nel lab senza esclusione vincono *king, bad, child, swim*; (4) funziona bene per alcune relazioni (capitali, flessione) e male per altre; i risultati dipendono da modello e corpus (*good : best :: bad* → *worst, movie*); (5) la valutazione a corrispondenza esatta può punire risposte plausibili (*larger*).

</details>

<details><summary>Perché un embedding statico non basta per bank? Che cosa contiene il suo vettore?</summary>

Traccia: (1) un vettore per tipo, lo stesso in tutte le frasi; (2) il vettore è una miscela dei sensi pesata per frequenza: in GloVe i 10 vicini di *bank* sono tutti finanziari; (3) il senso minoritario è nascosto ma presente ($\cos(\textit{bank},\textit{shore}) = 0{,}51$, e $\mathbf{bank}-\mathbf{money}+\mathbf{river}$ porta a *danube, estuary*); (4) il senso dominante dipende dal corpus (*fox*: personaggio in Pinocchio, rete TV in GloVe); (5) soluzione: embedding contestuali, in cui la rappresentazione del token è ricalcolata dall'attention in base alla frase; (6) anche i dataset di valutazione senza contesto (WordSim, SimLex) hanno lo stesso limite.

</details>

<details><summary>Come si valutano intrinsecamente gli embedding? Commenta i risultati di GloVe su WordSim-353 e SimLex-999.</summary>

Traccia: (1) valutazione intrinseca: correlazione fra i coseni e i giudizi umani su coppie di parole, con la $\rho$ di Spearman (Pearson sui ranghi, pari con rango medio): conta l'ordine, non la scala; (2) WordSim-353 di fatto misura la relatedness, SimLex-999 la similarità; (3) GloVe: 0,533 contro 0,298; (4) il coseno distribuzionale premia la relatedness: antonimi come *accept-reject* (0,82) o *short-long* hanno contesti uguali; sinonimi di registro diverso (*creator-maker* 0,24) no; (5) $\rho$ calcolate su coppie diverse non si confrontano (Pinocchio: 25 coppie); (6) altre valutazioni: TOEFL, analogie, ed estrinseca su compiti a valle.

</details>

<details><summary>Perché la media degli embedding perde contro la TF-IDF nella classificazione del sentiment?</summary>

Traccia: (1) numeri: media GloVe 0,7325, TF-IDF 1-2 grammi 0,8725 (bag of words del lab L9: 0,868); (2) il sentiment dipende da indizi lessicali specifici, che la TF-IDF tiene come feature separate e pesate per informatività; (3) la media di circa 800 parole diluisce le poche parole polari e cancella ordine e negazione (*good* e *not good* hanno coseno 0,991); (4) i bigrammi recuperano una parte della composizione; (5) gli embedding statici non sono addestrati sul compito (*good* e *bad* sono vicini); (6) non è la densità il problema: una SVD a 100 dimensioni della TF-IDF arriva a 0,855; (7) metà del divario è regolarizzazione: con le feature standardizzate la media arriva a 0,7725.

</details>

<details><summary>Nell'esercizio 3 la standardizzazione da sola migliora la media degli embedding di 4 punti. Perché?</summary>

Traccia: (1) la media di centinaia di vettori varia poco da una recensione all'altra: deviazione standard media 0,038 per feature; (2) per usare differenze così piccole servono pesi grandi; (3) la regressione logistica di scikit-learn ha una penalità L2 di default ($C = 1$) che schiaccia i pesi grandi: modello troppo regolarizzato; (4) standardizzare (z-score sul training) porta ogni feature a varianza 1, e la stessa penalità diventa ragionevole: 0,7325 → 0,7725; in alternativa alzare $C$ ($C = 100$: 0,770); (5) l'effetto è significativo ma di poco (paired bootstrap, $p\approx0{,}028$; 40 contro 24 recensioni discordi); (6) stopword e IDF non aiutano.

</details>

<details><summary>Come si misura e come si prova a rimuovere il bias di genere negli embedding? Funziona?</summary>

Traccia: (1) misura: differenza di coseni con *woman* e *man* (nel lab *nurse* +0,158, *manager* −0,214), o proiezione su una direzione di genere; analogia di Bolukbasi *man : programmer :: woman : homemaker*; (2) direzione: media delle differenze normalizzate su coppie definitorie (*she/he*, ...), coseno 0,89 con $\mathbf{she}-\mathbf{he}$; (3) neutralize: $\mathbf v-(\mathbf v\cdot\mathbf d)\mathbf d$, componente nulla; (4) Gonen e Goldberg: dopo il neutralize un 10-NN ritrova l'orientamento nel 93,1% dei casi: il bias è distribuito nella geometria e nei vicinati; (5) conseguenze: danno allocativo e rappresentazionale, il debiasing riduce ma non elimina, va valutato il comportamento del sistema finale.

</details>

<details><summary>Che cosa mostra (e che cosa non mostra) una proiezione PCA di embedding? Differenza con t-SNE.</summary>

Traccia: (1) PCA: proiezione lineare sulle direzioni di massima varianza, deterministica e veloce; (2) nel lab 16 parole formano quattro gruppi (cibo, animali, reali, città), PC1 separa il cibo; (3) è un'ombra: punti vicini nel piano possono non esserlo in 100 dimensioni (*king* e *queen* sovrapposti ma coseno 0,75), e viceversa; (4) t-SNE: non lineare, preserva meglio i vicinati locali, ma distanze fra gruppi e dimensioni dei gruppi non hanno significato, e la figura cambia con il seme; (5) le conclusioni vanno verificate sui coseni veri.

</details>

<details><summary>Perché due addestramenti di word2vec sullo stesso corpus danno vicini diversi? Che cosa implica?</summary>

Traccia: (1) fonti di casualità: inizializzazione, estrazione dei negativi, subsampling, e in gensim l'ordine degli aggiornamenti fra thread (`workers=3`), che il seme non controlla; (2) nel lab i vicini di *pinocchio* cambiano fra esecuzioni, la $\rho$ di Pinocchio su WordSim va da 0,045 a 0,108; (3) su corpora piccoli la variabilità è grande; (4) per riprodurre: `workers=1` e seme fisso (il word2vec fatto a mano del lab è deterministico); (5) per studiare associazioni in un corpus: addestrare più modelli (bootstrap sui documenti) e mediare (J&M §5.9).

</details>

### L13 · Reti neurali

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

### L14 · Transformer: l'attenzione

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

### L15 · Transformer: embedding, LM head e decoding

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

### L16 · Laboratorio: dagli n-gram a GPT

<details><summary>Che cosa resta identico e che cosa cambia fra il modello n-gram e il tiny GPT del laboratorio?</summary>

Traccia: (1) identici: unità (carattere), vocabolario di 77 simboli, obiettivo (predire il prossimo carattere, regola della catena), dati, split 90/10, metrica (cross-entropy in nats e perplexity sulla stessa validazione), generazione per campionamento; (2) cambiano la rappresentazione del contesto (ultimi $n-1$ caratteri esatti contro rappresentazione appresa di fino a 64 caratteri), l'apprendimento (contare e normalizzare contro discesa del gradiente con backprop e AdamW), i parametri (tabelle sparse di conteggi contro 244.301 pesi); (3) la decodifica (greedy, temperatura, top-$k$) è indipendente dal modello in entrambi i casi.

</details>

<details><summary>Come si stima un modello bigram di caratteri e perché il greedy produce "che che che"?</summary>

Traccia: (1) assunzione di Markov $P(x_t\mid x_{&lt;t})\approx P(x_t\mid x_{t-1})$; (2) MLE $P(b\mid a)=C(ab)/C(a)$, una matrice $|V|\times|V|$ le cui righe sommano a 1; esempio: dopo `t` la `o` con 0,189, dopo `q` la `u` con probabilità 1; (3) generazione: si guarda la riga del carattere corrente e si sceglie; (4) greedy = funzione deterministica del carattere corrente, quindi prima o poi un ciclo: C→o→␣→c→h→e→␣→c...; (5) il campionamento segue la distribuzione e produce testo vario; il seed cambia la traiettoria, non il modello.

</details>

<details><summary>Perché aumentando n la cross-entropy di training scende quasi sempre, mentre quella di validazione no?</summary>

Traccia: (1) con un contesto più lungo il modello MLE è più specifico e, al limite, memorizza il training: training CE MLE da 3,06 (unigram) a 0,30 (9-gram); (2) in validazione i contesti lunghi sono spesso mai visti (coverage 47% con 8 caratteri) e i conteggi per contesto sono pochi, quindi stime rumorose; (3) senza smoothing un solo zero dà perplexity infinita; con add-0,1 la validation CE ha un minimo al 5-gram (1,77, PPL 5,85) e risale al 9-gram (3,50, PPL 33); (4) è overfitting; il dev set serve a scegliere $n$; (5) "quasi sempre": con lo smoothing la training CE del 9-gram risale perché i contesti visti una volta perdono quasi tutta la massa.

</details>

<details><summary>Che cosa ripara l'add-α e che cosa non ripara?</summary>

Traccia: (1) formula $\frac{C(\text{ctx}\,b)+\alpha}{C(\text{ctx})+\alpha V}$; $\alpha=1$ Laplace, $\alpha=0$ MLE; (2) ripara gli **zeri**: ogni carattere ha probabilità positiva, quindi la perplexity è finita; un contesto mai visto riceve l'uniforme $1/V$; (3) non ripara la **sparsità**: un contesto mai visto non riceve informazione dai contesti simili, solo l'uniforme (6,27 bit); (4) toglie troppa massa ai contesti visti poche volte (con $V=77$, $\alpha V=7{,}7$); (5) non generalizza: servono backoff/interpolazione o, meglio, rappresentazioni apprese.

</details>

<details><summary>Cross-entropy e perplexity: definizioni, unità, legame con la loss di training.</summary>

Traccia: (1) $H=-\frac1N\sum_i\ln P(x_i\mid\text{context}_i)$ su testo held-out; (2) PPL $=e^H$ (nats) $=2^{H_\text{bit}}$ (bit), stesso numero; $H_\text{bit}=H_\text{nat}/\ln2$; (3) la loss di training del GPT è la stessa quantità sul batch (J&M Eq. 7.55), quindi PPL $=e^{\text{loss}}$; (4) baseline uniforme: $\ln V=4{,}344$, PPL 77; (5) media delle surprisal $-\log_2 p$ = CE in bit; (6) confrontabile solo a parità di tokenizzazione e di testo di valutazione.

</details>

<details><summary>Che cos'è il muro degli n-gram e perché una tabella a 64 caratteri è diversa da un transformer con contesto di 64 caratteri?</summary>

Traccia: (1) contesti possibili $V^h$: con $V=77$, $h=8$ già $10^{15}$, $h=64$ circa $10^{120{,}7}$; il training ne contiene al più mezzo milione; (2) quasi ogni contesto lungo di validazione è nuovo, la tabella risponderebbe con l'uniforme; (3) un n-gram tratta stringhe diverse come oggetti non collegati: nessuna condivisione statistica; (4) il transformer ha parametri fissi (244k) indipendenti da $V^h$, rappresenta i caratteri con embedding e combina le posizioni con l'attenzione, quindi contesti diversi ma simili producono rappresentazioni simili e previsioni simili; (5) il contesto lungo è usabile perché non serve averlo visto identico.

</details>

<details><summary>In che senso gli embedding permettono la condivisione statistica fra contesti diversi?</summary>

Traccia: (1) nell'n-gram ogni contesto ha i suoi conteggi, separati; (2) con gli embedding ogni carattere (e, dopo l'attenzione, ogni contesto) è un vettore denso appreso; (3) caratteri che si comportano in modo simile (vocali, `A` e `a`) finiscono vicini, e i pesi che li elaborano sono condivisi; (4) ciò che il gradiente impara su un contesto sposta parametri usati da tutti i contesti simili; (5) analogia con *eat lunch* / *eat dinner* della L5 e con la forza statistica condivisa della L13; (6) nel lab: il GPT alla posizione 0 impara una mappa bigram vicina a quella contata (KL 0,141 nats) senza tabella.

</details>

<details><summary>Descrivi una testa di attenzione causale del tiny GPT, con le forme dei tensori.</summary>

Traccia: (1) ingresso $X$ `[B, T, d]` = `[24, 64, 96]`; (2) $Q=XW^Q$, $K=XW^K$, $V=XW^V$, ognuno `[B, T, 24]` (`nn.Linear` senza bias, peso memorizzato trasposto); (3) punteggi $QK^\top/\sqrt{d_k}$ `[B, T, T]`; (4) maschera: `tril` e `masked_fill(-inf)` sopra la diagonale; (5) softmax per riga, dropout; (6) uscita pesi @ $V$ `[B, T, 24]`; (7) multi-head: 4 teste concatenate in `[B, T, 96]` e $W^O$; (8) costo $O(T^2)$ in tempo e memoria.

</details>

<details><summary>Perché la maschera causale è essenziale nel training di GPT? Che cosa succede se la si toglie?</summary>

Traccia: (1) il target in posizione $t$ è `y[t] = x[t+1]`, che sta dentro l'input; (2) la maschera impedisce alla posizione $t$ di leggere le posizioni $&gt;t$: $QK^\top+M$ con $-\infty$ sopra la diagonale, peso 0 dopo la softmax; (3) senza maschera il modello copia il carattere successivo: nell'ablazione la loss crolla molto sotto ogni modello onesto; (4) ma in generazione il futuro non c'è, il modello non ha imparato a predire e produce spazzatura; (5) la maschera permette anche di addestrare tutte le $T$ posizioni in parallelo con un solo forward (teacher forcing).

</details>

<details><summary>Descrivi il blocco transformer prenorm del laboratorio e il ruolo di residual stream, layer norm e feedforward.</summary>

Traccia: (1) $O=X+\text{MHA}(\text{LN}(X))$, $H=O+\text{FFN}(\text{LN}(O))$ (J&M Eq. 7.39-7.40); (2) residual stream: ogni componente legge e aggiunge, ingresso e uscita `[B, T, d]`, blocchi impilabili; il gradiente passa dalle somme; (3) layer norm prima di ogni sotto-blocco (prenorm) con $\gamma,\beta$ appresi, più `ln_f` finale; (4) attenzione = mescola i token, feedforward $d\to4d\to d$ con GELU = elabora ogni posizione da sola, contiene circa due terzi dei parametri del blocco; (5) nelle ablazioni: senza attenzione il modello degenera in un bigram.

</details>

<details><summary>Descrivi il ciclo di training del tiny GPT. Che cosa è cambiato rispetto agli n-gram?</summary>

Traccia: (1) minibatch di 24 finestre casuali da 64 caratteri, target spostati di uno; (2) forward e loss (cross-entropy media sulle $24\cdot64$ posizioni); (3) `zero_grad` (i gradienti si accumulano); (4) `backward`: backprop sul grafo computazionale, gradienti per tutti i parametri, embedding compresi; (5) `step` di AdamW, lr $3\cdot10^{-4}$; (6) valutazione periodica in `eval` (dropout spento) su train e val; (7) rispetto agli n-gram: niente conteggi esatti, una stima iterativa e approssimata; l'esito dipende da budget, iperparametri, inizializzazione (loss iniziale $\approx\ln 77$); dopo 500 passi il GPT (2,23) perde contro il 5-gram (1,77).

</details>

<details><summary>Perché la qualità del testo generato cambia con la temperatura, mentre la loss di validazione no?</summary>

Traccia: (1) temperatura: logit divisi per $\tau$ prima della softmax; $\tau&lt;1$ appuntisce, $\tau&gt;1$ appiattisce, $\tau\to0$ greedy; (2) la loss di validazione misura le probabilità che il modello assegna al testo vero, con teacher forcing, senza mai campionare: non dipende da $\tau$; (3) la temperatura è una scelta di decodifica, come top-$k$ e top-$p$; (4) nel lab: $\tau=0{,}4$ ripetizioni (*che che che*), $\tau=1{,}2$ combinazioni improbabili; (5) stessa distinzione dei bigram: modello di probabilità contro politica di generazione.

</details>

<details><summary>Che cosa mostrano le ablazioni dell'esercizio 2?</summary>

Traccia: (1) ablazione = togliere un componente e riaddestrare a parità di dati, batch e budget; (2) nella mia esecuzione su CPU (300 passi per variante): baseline 2,361, senza posizioni 2,356, senza feedforward 2,420, senza attenzione 2,444, senza layer norm 2,900, senza residue 3,062, senza maschera 0,512; (3) senza attenzione le posizioni non si parlano: il modello è un bigram e tende alla sua loss (2,35); (4) senza maschera causale la loss crolla perché il modello copia il carattere successivo, ma il testo generato è spazzatura; (5) senza residue il modello resta inchiodato all'unigram (3,06 contro 3,05): l'identità del carattere corrente non attraversa i blocchi; senza layer norm il training è molto più lento; l'effetto cresce con la profondità; (6) senza position embedding, a questo budget, nessuna differenza: un po' di informazione d'ordine passa dalla maschera causale (la posizione $t$ vede $t+1$ token).

</details>

<details><summary>Che cos'è la KV cache e perché si cachano K e V ma non Q?</summary>

Traccia: (1) la `generate` ingenua ricalcola tutto il contesto a ogni passo: il tempo per passo cresce con la lunghezza, il totale in modo quadratico; (2) i $K$ e $V$ dei token passati non cambiano (attenzione causale: un token non vede quelli successivi), quindi si salvano per ogni strato, forma `(B, A, T, d_k)`; (3) a ogni passo si calcolano solo $q,k,v$ del nuovo token, si accodano $k,v$ e si fa un'attenzione di una riga; (4) $Q$ dei token passati non serve più: le loro uscite sono già calcolate; (5) memoria $2LNd$ numeri per sequenza (64 GiB per Llama 3.1 8B a 128k in fp16 senza GQA); (6) con la cache niente finestra scorrevole: le posizioni assolute delle key salvate non si possono spostare.

</details>

<details><summary>Perché un'attenzione vettorizzata e una SDPA fusa sono più veloci, e che cosa non cambiano?</summary>

Traccia: (1) il ciclo sulle teste lancia molte operazioni piccole; una proiezione `qkv` unica e la dimensione delle teste come dimensione di batch fanno un solo grande prodotto, che sfrutta meglio CPU e GPU (meno overhead, meno lanci di kernel); (2) `F.scaled_dot_product_attention` usa kernel fusi (FlashAttention) che non materializzano la matrice $T\times T$: calcolano a blocchi con massimo e somma correnti della softmax, risparmiando memoria e trasferimenti; (3) la funzione matematica è la stessa: uscite uguali a meno di $10^{-6}$; (4) il costo resta $O(T^2)$ in operazioni: cambia la costante e la memoria, non l'ordine.

</details>

<details><summary>Se gli LLM usano sottoparole e non caratteri, che cosa del laboratorio resta valido?</summary>

Traccia: (1) l'obiettivo (prossimo token, regola della catena) e la loss (cross-entropy); (2) la valutazione con perplexity su held-out, ma confrontabile solo a parità di tokenizer; (3) l'architettura identica, con $|V|$ di decine di migliaia invece di 77 (embedding e unembedding più grandi); (4) maschera causale, teacher forcing, training in parallelo, decodifica con temperatura, top-$k$, top-$p$, KV cache; (5) il muro degli n-gram è ancora peggiore: $V^h$ con $V$ grande; (6) cambia la granularità: con sottoparole un contesto di $N$ token copre molto più testo.

</details>

### L17 · Pretraining dei modelli linguistici

<details><summary>Che cos'è il pretraining e perché si dice self-supervised?</summary>

Traccia: (1) primo dei quattro stadi di training, su trilioni di token, produce un base model; (2) obiettivo: predire il token successivo a ogni posizione (Shannon game con correzione); (3) self-supervised: i target sono nel testo, nessuna annotazione; formalmente MLE condizionata, ogni token è un esempio; (4) si aggiornano tutti i pesi con backpropagation e un ottimizzatore come Adam, compresi gli embedding; (5) il modello impara lingua e conoscenza come effetto collaterale; (6) limite: continua testo, non segue istruzioni.

</details>

<details><summary>Scrivi la cross-entropy loss del language modeling e spiega perché si riduce a meno il log di una probabilità.</summary>

Traccia: (1) $L_{CE} = -\sum_w y_t[w]\log\hat y_t[w]$ fra distribuzione predetta e corretta su $V$; (2) $y_t$ one-hot sul vero token $w_{t+1}$, tutti gli altri termini si annullano; (3) resta $-\log\hat y_t[w_{t+1}]$; (4) probabilità 1 dà loss 0, probabilità vicina a 0 loss enorme; esempio 0,44 dà 0,82; (5) sulla sequenza si fa la media sulle $T$ posizioni; (6) stessa loss della regressione logistica con $|V|$ classi; minimizzarla = massimizzare la verosimiglianza; log naturale, nat.

</details>

<details><summary>Che cos'è il teacher forcing? Quali vantaggi ha e che differenza crea con l'inferenza?</summary>

Traccia: (1) in training a ogni posizione il contesto è il testo vero, non la previsione del modello; (2) esempio: il modello scommette *the*, il vero è *all*, si prosegue con *all*; (3) la previsione serve solo per la loss; (4) vantaggi: errori che non si propagano, contesti noti in anticipo quindi tutte le posizioni in parallelo; (5) in inferenza il modello si nutre delle proprie uscite: situazione mai vista in training (exposure bias).

</details>

<details><summary>Perché il pretraining di un transformer si può fare in parallelo su tutte le posizioni, e come si riempie la finestra?</summary>

Traccia: (1) target noti: il token successivo di ogni posizione è nel testo; (2) maschera causale: nessuna posizione vede il proprio target, l'output di ciascuna non dipende dal futuro; (3) un forward con la forma matriciale dà $N$ distribuzioni e $N$ loss; (4) senza maschera il modello copierebbe il successivo; (5) packing: documenti corti concatenati con `eot` per riempire la finestra, niente padding sprecato; (6) batch grandi: GPT-3 3,2M token, circa 1.560 finestre da 2.048.

</details>

<details><summary>Come può un modello addestrato solo a predire il token successivo fare sentiment analysis o rispondere a domande?</summary>

Traccia: (1) generazione condizionata: il task scritto nel prompt, il modello lo continua; (2) sentiment: prompt *The sentiment of ... is:* e confronto di $P(\textit{positive})$ e $P(\textit{negative})$, 0,42 contro 0,03; (3) QA: *Q: ... A:*, poi *Charles*, poi *Darwin*, un token alla volta; (4) riassunto con `tl;dr`; (5) funziona perché il web è pieno di task svolti; (6) limite: un base model non segue istruzioni in modo affidabile, serve instruction tuning.

</details>

<details><summary>Da dove vengono i dati di pretraining e come si filtrano? Quali problemi pongono i filtri?</summary>

Traccia: (1) soprattutto Common Crawl (istantanee del web, miliardi di pagine), più dati curati (Wikipedia, libri); The Pile come esempio di mix di 22 fonti; (2) scala: Llama 3.1 15T token, circa 71.000 anni di lettura; (3) filtri di qualità: deduplicazione, boilerplate, contenuti per adulti, spesso classificatori con punteggio; (4) filtri di sicurezza: classificatori di tossicità; (5) problemi: falsi allarmi su dialetti minoritari come l'AAE, modelli meno tossici ma peggiori a riconoscere la tossicità; filtrare meglio è un problema aperto.

</details>

<details><summary>Quali questioni etiche e legali pongono i dati di pretraining?</summary>

Traccia: (1) copyright: libri e articoli protetti; fair use negli USA incerto, compenso non risolto; (2) casi: Bartz v. Anthropic (training fair use, ma non i libri piratati: 1,5 miliardi), NYT v. OpenAI aperto, GEMA v. OpenAI (testi memorizzati nei pesi = copia); (3) privacy: telefoni, email; (4) consenso dei siti; (5) skew verso autori di USA e paesi sviluppati; (6) data-centric AI: chiedersi provenienza, autori, compenso, liceità.

</details>

<details><summary>Conta i parametri di un transformer come GPT-3 e verifica i 175B.</summary>

Traccia: (1) attenzione $W^Q,W^K,W^V,W^O$: $4d^2$; (2) feedforward $d\times4d$ e $4d\times d$: $8d^2$; (3) strato $12d^2$, modello $12Ld^2 + |V|d$; (4) ipotesi: niente bias e layer norm, weight tying; (5) GPT-3: $12\cdot96\cdot12288^2 = 174{,}0$B più $50\text{K}\cdot12288 = 0{,}6$B, 174,6B; GPT-2 XL 1,55B; (6) i modelli moderni (GQA, SwiGLU, embedding non legati) si discostano: Llama 3.1 8B 6,97B dalla formula contro 8,03B.

</details>

<details><summary>Che cos'è la KV cache, perché funziona e quanto costa in memoria?</summary>

Traccia: (1) in training tutti i token insieme; in inferenza un token nuovo alla volta; (2) key e value dei token precedenti non cambiano (causalità), ricalcolarli è uno spreco; (3) si salvano key e value, si calcola solo $q_i, k_i, v_i$ del nuovo token; le query e i punteggi no; (4) calcoli di key/value: $n(n+1)/2$ senza cache contro $n$; (5) memoria $2Ld$ numeri per token: GPT-3 $2\cdot96\cdot12288 = 2{,}36$M, 4,7 MB a 16 bit, 9,7 GB per 2.048 token; (6) cresce con contesto e sequenze; GQA la riduce condividendo key e value fra teste.

</details>

<details><summary>Che cosa dicono le scaling law di Kaplan et al. (2020)?</summary>

Traccia: (1) tre fattori: parametri $N$, token $D$, calcolo $C$; (2) la test loss scende come legge di potenza di ciascuno, $L = (X/X_c)^{-\alpha}$, retta in log-log; (3) esponenti: 0,076 per $N$, 0,095 per $D$, 0,050 per $C$; (4) ogni legge vale se gli altri fattori non limitano; (5) esempio: $L(10^9) = 2{,}38$ nat, perplexity 10,8; per dimezzare la loss serve un modello circa 9.000 volte più grande; (6) conseguenza: più grande è meglio, in modo prevedibile, quindi modelli sempre più grandi, con costi di energia e acqua.

</details>

<details><summary>Come si spende in modo ottimale un budget di calcolo? Spiega Chinchilla e il 6ND.</summary>

Traccia: (1) $C\approx6ND$: 2 FLOP per parametro per token nel forward, 4 nel backward; (2) a $C$ fisso, più parametri vuol dire meno token; (3) Hoffmann et al.: $N_{opt}\propto C^{1/2}$, $D_{opt}\propto C^{1/2}$; (4) circa 20 token per parametro, quindi $C = 120N^2$; (5) Chinchilla 70B e 1,4T batte Gopher 280B e 300B con budget simile ($5{,}9$ contro $5{,}0\cdot10^{23}$ con 6ND); (6) GPT-3 con 1,7 token per parametro era troppo grande per i suoi dati.

</details>

<details><summary>Perché Llama 3.1 8B è stato addestrato con quasi 1.900 token per parametro, ben oltre Chinchilla?</summary>

Traccia: (1) Chinchilla minimizza la loss a parità di calcolo di training; (2) ma l'inferenza costa a ogni prompt, circa proporzionale a $N$; (3) un modello piccolo addestrato più a lungo è più economico da servire; (4) la loss continua a scendere oltre i 20 token per parametro, solo più lentamente; (5) numeri: 15T/8B = 1.875; calcolo $7{,}2\cdot10^{23}$, simile a Chinchilla con un modello 9 volte più piccolo; (6) Llama 3.1 405B invece 37 token per parametro.

</details>

<details><summary>Definisci la perplexity e dimostra che è l'esponenziale della cross-entropy media.</summary>

Traccia: (1) likelihood = prodotto delle probabilità dei token, decresce con la lunghezza; (2) perplexity $= P(w_{1:T})^{-1/T}$, inverso normalizzato per la lunghezza, misura per token; (3) $\ln\mathrm{PP} = \frac1T\sum -\ln P(w_t\mid w_{&lt;t}) = L_{CE}$; (4) quindi $\mathrm{PP} = e^{L_{CE}}$, con loss in nat; in bit $2^{H}$, stesso numero; (5) esempio: prodotto 0,01408, $0{,}01408^{-1/5} = 2{,}35 = e^{0{,}853}$; (6) interpretazione: scelta fra circa 2,35 token equiprobabili; più bassa è meglio.

</details>

<details><summary>Perché non si possono confrontare le perplexity di modelli con tokenizzatori diversi?</summary>

Traccia: (1) la perplexity normalizza per il numero di token $T$; (2) stesso testo, stessa probabilità 0,001: con 4 token 5,6, con 6 token 3,2; (3) la qualità del modello sul testo è identica, cambia solo la divisione; (4) un tokenizzatore che spezza di più fa sembrare il modello migliore; (5) regola: stessa tokenizzazione, oppure normalizzare per un'unità comune (parole, caratteri, byte).

</details>

<details><summary>Come si valutano gli LLM oltre la perplexity? Che cos'è la data contamination?</summary>

Traccia: (1) accuratezza su test set etichettati e mai visti; (2) benchmark da esami umani: MMLU (15.908 domande in 57 aree), BigBench Hard, GSM8k, AIME24; proxy di conoscenza e ragionamento; (3) contaminazione: il test finisce nel training perché entrambi sono sul web; la metrica sovrastima; (4) esempio: 90% complessivo, ma 86% sulle 70 domande pulite; (5) rimedio: pubblicare i dati o la sovrapposizione con i test, modelli completamente open.

</details>

<details><summary>Come si valutano i task con molte risposte corrette? Che cosa sono le metriche proxy e la legge di Goodhart?</summary>

Traccia: (1) task soggettivi: conversazione, traduzione, sycophancy; (2) giudici umani con rubrica (fedeltà, fluenza), scelti per competenza o varietà di provenienza; (3) LLM-as-a-judge: più economico e meno dannoso per le persone, prompt curato e verificato su un campione umano, singolo o a coppie; (4) metriche proxy: sovrapposizione di token (chrF, BLEU, ROUGE), WER; esempio 5/6 contro 2/7; comode ma imperfette, verificare la significatività; (5) Goodhart: ottimizzando la metrica si ottimizzano proprietà casuali e la metrica peggiora come proxy.

</details>

<details><summary>Oltre all'accuratezza, quali altri fattori conta valutare in un modello?</summary>

Traccia: (1) efficienza: dimensione, tempo di training e inferenza, memoria GPU, prestazione a budget fisso; (2) energia: kWh, kg di CO$_2$, green AI; (3) sicurezza e bias: linguaggio tossico e stereotipi, con StereoSet, RealToxicityPrompts, BBQ; (4) equità: prestazioni buone per tutti i gruppi, criterio del gruppo più svantaggiato invece della media; (5) collegamento con i dati: skew e filtri influenzano bias ed equità.

</details>

### L18 · Post-training I: instruction tuning, LoRA e prompting

<details><summary>Perché un base model non segue le istruzioni?</summary>

Traccia: (1) è addestrato a predire il token successivo nel testo del web: continua il prompt in modo plausibile; (2) esempi di Ouyang et al.: *Explain the moon landing to a six year old* diventa un'altra consegna, *Translate to French: The small dog* diventa *The small dog crossed the road*; (3) due problemi: poco utile (non segue istruzioni, debole nel ragionamento lungo) e dannoso (risposte pericolose, false, offensive; esempio del furto al supermercato); (4) causa: obiettivo del pretraining disallineato con ciò che serve alle persone; (5) rimedio: post-training.

</details>

<details><summary>Quali sono le fasi del post-training e che dati usa ciascuna?</summary>

Traccia: (1) base model = dopo il pretraining, prima del post-training; (2) instruction tuning (SFT): coppie istruzione-risposta, cross-entropy sulla risposta; (3) preference alignment (RLHF, DPO): coppie di risposte con la preferita; (4) RLVR: problemi con risposta verificabile (matematica, codice), ricompensa se corretta; (5) ognuna parte dal modello precedente (figura delle quattro fasi); (6) costo molto minore del pretraining.

</details>

<details><summary>Che cos'è l'instruction tuning e perché si chiama supervised fine-tuning?</summary>

Traccia: (1) fine-tuning di un base model su istruzioni di molti compiti con le loro risposte; (2) stesso obiettivo del pretraining, cross-entropy sul token successivo, ma solo sui token della risposta; (3) supervised perché ogni istruzione ha una risposta corretta, come un'etichetta, mentre nel pretraining il target è solo il testo che segue (self-supervised); (4) fine-tuning = ulteriori passate di addestramento su dati nuovi a partire da un modello preaddestrato; (5) risultato: impara i compiti e a seguire istruzioni in generale (meta-learning); (6) dati: al più milioni di esempi, poche epoche.

</details>

<details><summary>Perché nell'instruction tuning la loss si calcola solo sulla risposta? Fai un esempio numerico.</summary>

Traccia: (1) l'istruzione è il contesto: passa nella rete ma non entra nella loss (maschera $m_t = 0$); (2) l'istruzione è sempre data dall'utente, il modello non deve imparare a scriverla; (3) esempio *Translate to Italian: good night* / *buona notte*: media sulla risposta $(0{,}92 + 0{,}22 + 0{,}11)/3 \approx 0{,}42$, su tutti i token $8{,}49/8 \approx 1{,}06$, dominata da *good* ($-\ln 0{,}05 = 3{,}00$), imprevedibile per natura; (4) il `</s>` della risposta invece è addestrato: insegna a fermarsi; (5) nel notebook la loss sulla risposta dà una loss di test sulle risposte un po' migliore (3,71 contro 3,79).

</details>

<details><summary>Che cos'è un chat template? Che cosa si addestra e come si usa all'inferenza?</summary>

Traccia: (1) converte una conversazione in una sequenza di token con marcatori di ruolo (`<|system|>`, `<|user|>`, `<|assistant|>`) e un terminatore di turno `</s>` (TinyLlama); (2) loss solo sui turni dell'assistente e i loro `</s>`; (3) all'inferenza il programma scrive la conversazione e termina con `<|assistant|>`; il modello genera la risposta e si ferma a `</s>`; (4) ogni famiglia di modelli ha il suo template, va usato lo stesso dell'addestramento.

</details>

<details><summary>Da dove vengono i dati per l'instruction tuning?</summary>

Traccia: (1) scritti da persone: alta qualità, costosi (parte di Aya, volontari in 65 lingue); (2) convertiti da dataset NLP annotati: campi in coppie chiave/valore, inseriti in template (*Suppose {{premise}} Can we infer that {{hypothesis}}? Yes, no, or maybe?*), l'etichetta diventa la risposta; template parafrasati da LLM per varietà; (3) generati da LLM: es. dati di sicurezza di Bianchi et al. (domande dannose parafrasate, risposte sicure controllate da persone; 500 bastano a ridurre la dannosità); (4) dimensioni: Aya 513M, Super-NaturalInstructions 5M/1600 compiti, Flan 2022 15M/1836, OPT-IML 18M/2000.

</details>

<details><summary>Come si valuta un modello instruction-tuned?</summary>

Traccia: (1) l'obiettivo è seguire istruzioni per compiti nuovi, quindi il test va su compiti esclusi dall'addestramento; (2) leave-one-out: instruction tuning su molti compiti, test su quello escluso; (3) compiti simili (25 dataset di entailment in Super-NaturalInstructions) renderebbero il test troppo facile: si raggruppano in cluster e si esclude un cluster intero; (4) un modello per ogni cluster da valutare; (5) esempio della figura: training su NLI, QA, traduzione, riassunto, test sul sentiment.

</details>

<details><summary>Quanta memoria serve per fare fine-tuning completo di un modello da 7B e perché?</summary>

Traccia: (1) Adam in mixed precision: pesi 16 bit (2 byte), gradienti 16 bit (2), copia dei pesi a 32 bit e due momenti a 32 bit (12): 16 byte per parametro; (2) $7\cdot10^9\cdot16 = 112$ GB senza attivazioni; (3) una A100/H100 ha 80 GB: non basta; un 70B richiede 1120 GB, almeno 14 GPU; (4) da qui il bisogno di PEFT: con LoRA restano i 2 byte dei pesi congelati (14 GB), con QLoRA 0,5 byte (3,5 GB).

</details>

<details><summary>Spiega LoRA: forme delle matrici, forward pass e numero di parametri.</summary>

Traccia: (1) le matrici dense ($W^Q, W^K, W^V, W^O$, feedforward) restano congelate; (2) l'aggiornamento $\Delta W$ ($k\times d$) è scritto come $AB$, $A$ $k\times r$, $B$ $r\times d$, $r \ll \min(k,d)$; (3) forward $h = xW + xAB$, calcolato come $(xA)B$; (4) parametri $r(k+d)$ invece di $kd$: per $k = d = 4096$, $r = 8$, 65 536 contro 16 777 216, lo 0,39%; (5) perché funziona: l'aggiornamento necessario ha bassa dimensione intrinseca (Aghajanyan et al.); (6) $r$ tipico 4-64, compromesso costo/capacità; (7) esempio a mano: $h = [5,4,1]$.

</details>

<details><summary>Come si inizializzano A e B in LoRA, e perché non entrambe a zero?</summary>

Traccia: (1) $A$ casuale, $B = 0$: $AB = 0$ e il modello parte esattamente dal preaddestrato; (2) gradienti: con $G = \partial L/\partial W$, $\partial L/\partial A = GB^\top$, $\partial L/\partial B = A^\top G$; (3) se $A = B = 0$ entrambi i gradienti sono nulli e l'addestramento non parte; (4) con $A$ casuale $B$ riceve subito gradiente non nullo; (5) eventuale fattore $\alpha/r$ delle implementazioni.

</details>

<details><summary>Quali sono i vantaggi pratici di LoRA?</summary>

Traccia: (1) memoria: niente gradienti né stato di Adam per i pesi congelati; (2) nessun costo all'inferenza: $x(W + AB) = xW + xAB$, si fonde $AB$ in $W$ una volta; (3) moduli intercambiabili: un LoRA per dominio o compito, si somma o si sottrae da $W$; checkpoint piccoli (GPT-3, $r = 4$ su $W^Q$, $W^V$: circa 18,9 milioni di parametri, 37,7 MB); (4) originariamente solo sulle matrici dell'attenzione, oggi molte varianti; (5) limite: rango basso, meno espressivo di un $\Delta W$ completo.

</details>

<details><summary>Che cos'è la quantizzazione e come la usa QLoRA?</summary>

Traccia: (1) memorizzare i pesi con meno bit: 16 bit = 65 536 valori, 4 bit = 16 livelli; (2) ogni peso diventa l'indice del livello più vicino, a blocchi con una scala propria; (3) livelli non uniformi, più fitti dove i pesi (circa normali) sono densi: 4-bit NormalFloat; (4) memoria circa 4 volte minore (4,5 bit effettivi con una scala a 32 bit ogni 64 pesi), piccola perdita di precisione; (5) QLoRA: modello base congelato a 4 bit, LoRA a 16 bit; 65B su una GPU da 48 GB; un 7B in 3,5 GB invece di 14 o 112.

</details>

<details><summary>Che differenza c'è fra prompting zero-shot e few-shot? Che cosa insegnano le dimostrazioni?</summary>

Traccia: (1) zero-shot: solo l'istruzione; few-shot: istruzione più alcune dimostrazioni, esempi etichettati nel prompt; (2) esempio one-shot di MMLU: una domanda con risposta C, poi la domanda vera, risposta (B), `"aab"`; (3) il compito è mostrato, non solo descritto; le dimostrazioni insegnano soprattutto formato e spazio delle risposte; anche etichette sbagliate possono aiutare (Min et al.); (4) poche: rendimenti decrescenti e rischio di adattarsi agli esempi; (5) chain-of-thought: dimostrazioni con i passi di ragionamento.

</details>

<details><summary>Che cos'è il system prompt?</summary>

Traccia: (1) prima istruzione al modello, anteposta in silenzio a qualunque testo dell'utente; (2) definisce compito o ruolo, tono, contesto (*You are a helpful and knowledgeable assistant...*); (3) può essere lungo migliaia di token grazie ai contesti lunghi (quello di Claude); (4) nel chat template ha un marcatore proprio ed è contesto senza loss; (5) costo: va elaborato a ogni conversazione; la KV cache lo evita all'interno di una conversazione.

</details>

<details><summary>Che cos'è l'in-context learning e come si confronta con il fine-tuning?</summary>

Traccia: (1) apprendimento durante il prompting senza aggiornare i pesi; (2) cambiano solo il contesto e le attivazioni; le dimostrazioni aiutano a eseguire un compito nuovo; (3) finita la conversazione si perde tutto; (4) il fine-tuning cambia i pesi, ciò che si impara resta; (5) due modi di adattare un modello: cambiare il prompt (immediato, nessun dato di training, costa token a ogni chiamata) o cambiare i pesi (dati e addestramento, reso economico da LoRA/QLoRA, effetto permanente).

</details>

<details><summary>Riassumi il percorso da base model ad assistente visto in questa lezione.</summary>

Traccia: (1) il base model continua il testo; (2) SFT con lo stesso obiettivo del pretraining, su dati diversi, loss sulla risposta, chat template; (3) dati da persone, dataset NLP con template, LLM; valutazione su cluster esclusi; (4) per farlo a basso costo LoRA ($h = xW + xAB$, frazione minima dei parametri) e QLoRA (base a 4 bit); (5) all'uso, prompting zero-shot, few-shot e system prompt, con in-context learning senza modificare i pesi; (6) prossimi passi: preferenze e RLVR.

</details>

### L19 · Post-training II: preferenze, RLHF, DPO e RL per il ragionamento

<details><summary>Perché dopo l'instruction tuning serve un altro stadio? Che cosa hanno di diverso le preferenze?</summary>

Traccia: (1) un modello SFT può ancora dare risposte dannose o sbagliate, o corrette ma poco utili; (2) l'SFT impara solo da esempi positivi, non riceve mai il segnale di che cosa non dire; (3) le preferenze sono confronti, meglio o peggio, non giusto o sbagliato: non richiedono competenza per essere date, quindi si raccolgono facilmente; (4) ogni coppia contiene anche una risposta scartata; (5) obiettivo: più helpful, honest, harmless; (6) la scelta deve essere solo migliore, non buona (esempio del ketchup).

</details>

<details><summary>Come si ottengono coppie di preferenza e da quali fonti?</summary>

Traccia: (1) tripla prompt, scelto, scartato, $o_w \succ o_l \mid x$; (2) confronti diretti; classifica di $N$ output, $N(N-1)/2$ coppie (InstructGPT 4-9 output, da 6 a 36 coppie); scelta del migliore, $N-1$ coppie; (3) fonti: annotatori addestrati (InstructGPT, prompt di utenti reali), voti online (Reddit, StackExchange: post come prompt, risposte ordinate dai voti), LLM come giudici (UltraFeedback con GPT-4); (4) costo e rumore diversi; (5) anche punteggi per aspetti.

</details>

<details><summary>Scrivi il modello di Bradley-Terry e spiega da dove viene.</summary>

Traccia: (1) ogni output ha un punteggio nascosto $z$; (2) $P(o_i\succ o_j\mid x) = \sigma(z_i - z_j)$; (3) la differenza è il log-odds della preferenza: $\delta = \log\frac{P}{1-P}$, da cui $P = 1/(1+e^{-\delta})$, come nella regressione logistica; (4) differenza piccola, probabilità vicina a 0,5; grande, vicina a 0 o 1; (5) $P(o_j\succ o_i) = 1 - P(o_i\succ o_j)$; (6) invarianza per traslazione: i punteggi sono definiti a meno di una costante.

</details>

<details><summary>Come si addestra un reward model? Scrivi la loss e il suo gradiente.</summary>

Traccia: (1) si impara $r(x,o)$ al posto di $z$; (2) loss di una coppia $-\log\sigma(r(x,o_w) - r(x,o_l))$, media sul dataset: binary cross-entropy con target 1, massima verosimiglianza delle preferenze; (3) derivata rispetto alla differenza: $-(1-\sigma)$, alza $r_w$ e abbassa $r_l$; (4) le coppie ordinate male pesano di più (esempio della slide: 0,88 contro 0,27); (5) in pratica un LLM preaddestrato con la LM head sostituita da uno strato lineare a un'uscita (Ziegler 2019); (6) usi: best-of-$N$, selezione dati, alignment.

</details>

<details><summary>Come si mappa il reinforcement learning su un LLM?</summary>

Traccia: (1) RL: agente, policy, azioni, ambiente, reward, nessuno dà l'azione giusta; (2) per un LLM: azioni = token, stato = prompt più token generati, policy = l'LLM (distribuzione del token successivo), reward = reward model sull'intera risposta, alla fine; (3) $\pi(o\mid x)$ prodotto delle probabilità dei token; (4) differenze dal RL classico: reward appreso e rumoroso, non osservabile; si parte da un modello già buono da spingere, non da zero.

</details>

<details><summary>Scrivi l'obiettivo di RLHF con la penalità KL e spiega ogni termine.</summary>

Traccia: (1) $\max_{\pi_\theta}\mathbb{E}_{x\sim D,o\sim\pi_\theta}[r(x,o) - \beta\log\frac{\pi_\theta(o\mid x)}{\pi_{\mathrm{ref}}(o\mid x)}]$; (2) prompt dal dataset, output dalla policy stessa, reward dal reward model; (3) reward atteso: media dei reward pesata dalle probabilità (giocattolo: 1,5 poi 2,35), stimata campionando; (4) penalità: log-rapporto per output, in media la KL da $\pi_{\mathrm{ref}}$ (il modello SFT), non simmetrica; (5) senza penalità: oblio del pretraining e reward hacking; (6) $\beta$ ne regola il peso.

</details>

<details><summary>Che cos'è il policy gradient e perché si usa una baseline?</summary>

Traccia: (1) in SFT $\theta \leftarrow \theta + \eta\nabla\log\pi_\theta(o\mid x)$ con $o$ dal dataset; (2) in RL $o$ campionato da $\pi_\theta$ e il passo moltiplicato per $r(x,o)$: REINFORCE, SFT sui propri output pesato dal reward; (3) $\nabla\log\pi$ è la direzione, $r$ la lunghezza del passo; in media la direzione che alza il reward atteso (trucco del log); (4) con reward tutti positivi ogni campione viene alzato: gradiente rumoroso; (5) baseline $b$ = reward atteso, advantage $r - b$: sopra la media su, sotto giù, stessa direzione media, meno varianza; (6) in PPO $b$ dal value model, in GRPO media del gruppo.

</details>

<details><summary>Descrivi RLHF di InstructGPT e PPO.</summary>

Traccia: (1) tre passi: SFT su dimostrazioni scritte da persone; reward model da classifiche di 4-9 output; RL con PPO e penalità KL; (2) InstructGPT 1,3B preferito a GPT-3 175B; base delle prime versioni di ChatGPT; (3) PPO: quattro modelli, policy (addestrata), riferimento (congelato, per la KL), reward model (congelato), value model (addestrato, baseline); (4) aggiornamento in base all'advantage; (5) proximal: aggiornamenti piccoli, la policy cambia gradualmente; (6) costoso: quattro modelli e campionamento a ogni passo.

</details>

<details><summary>Scrivi la loss di DPO, spiegala e confrontala con PPO.</summary>

Traccia: (1) $-\log\sigma(\beta\log\frac{\pi_\theta(o_w)}{\pi_{\mathrm{ref}}(o_w)} - \beta\log\frac{\pi_\theta(o_l)}{\pi_{\mathrm{ref}}(o_l)})$; (2) è la loss del reward model con reward implicito $\beta\log\pi_\theta/\pi_{\mathrm{ref}}$; (3) derivazione: la soluzione dell'obiettivo con KL dà $r = \beta\log\pi^*/\pi_{\mathrm{ref}} + \beta\log Z(x)$, e in Bradley-Terry $Z$ si cancella; (4) $\beta$ tipicamente 0,01-0,1, stesso ruolo della KL; (5) all'inizio la loss vale $\ln2$; conta solo il margine fra i log-rapporti; (6) contro PPO: niente reward model, niente campionamento, due modelli; più semplice e stabile, ma offline e soggetto agli stessi bias dei dati.

</details>

<details><summary>Che cos'è il reward hacking? Fai esempi.</summary>

Traccia: (1) il reward model è un surrogato appreso delle preferenze, non ciò che vogliamo davvero; (2) ottimizzandolo troppo la policy trova risposte che lo ingannano: alto reward, bassa qualità vera; (3) esempi: length bias (risposte lunghe premiate in sé; notebook: con $\beta$ piccolo la risposta lunga sbagliata diventa certa), sycophancy (dare ragione all'utente); (4) rimedi parziali: penalità KL, reward verificabili, dati migliori; (5) la KL limita il danno ma non corregge un reward model distorto, e DPO eredita i bias dei dati.

</details>

<details><summary>Che cos'è il chain-of-thought prompting e che cosa c'entra con i reasoning model?</summary>

Traccia: (1) Wei et al. 2022: ogni dimostrazione include i passi di ragionamento, il modello imita e scrive passi prima della risposta; (2) esempio delle mele: 27 sbagliato senza passi, 9 corretto con $23-20=3$, $3+6=9$; (3) test-time compute: più calcolo all'inferenza sui problemi difficili; (4) i reasoning model sono addestrati con RLVR a scrivere la chain of thought da soli, anche se il reward guarda solo la risposta finale.

</details>

<details><summary>Che cos'è RLVR? Che cosa vuol dire verificabile?</summary>

Traccia: (1) domini dove una risposta si giudica in automatico: matematica (GSM8K fino al livello dottorato), codice con test; (2) vincoli verificabili (IFEval): parole chiave, formato JSON, lunghezza, lingua, risposte da un insieme fisso; si controllano i vincoli, non il contenuto; (3) reward 1 o 0 calcolato da un programma, nessun reward model; (4) stesso policy gradient di RLHF; (5) produce reasoning model con chain of thought; (6) limite: si premia solo ciò che si controlla.

</details>

<details><summary>Come funziona GRPO? Calcola gli advantage di un gruppo.</summary>

Traccia: (1) per una domanda si campiona un gruppo di $G$ risposte; (2) reward 1 o 0; (3) $A_i = (r_i - \mathrm{mean})/\mathrm{std}$, con una costante sulla std; (4) la media del gruppo è la baseline: niente value model; la std mette le domande sulla stessa scala; (5) aggiornamento con penalità KL; (6) esempio $[1,1,0,0,0,1]$: media 0,5, std 0,5, advantage $\pm1$; (7) gruppo tutto giusto o tutto sbagliato: nessun segnale; utili le domande a difficoltà intermedia.

</details>

<details><summary>Che cosa si intende per alignment e quali problemi restano aperti?</summary>

Traccia: (1) far evitare danni ai modelli, agendo secondo bisogni e valori umani; parte dell'AI safety; (2) sottospecificato: valori di chi? conflitti? (Kirk 2023); (3) sycophancy: le preferenze premiano l'accordo, non la verità (Sharma 2024); (4) mitigazioni: esempi di danni nei dati di post-training, constitutional AI, red teaming, value sensitive design; problema sociotecnico; (5) limiti: allucinazioni, overconfidence, calibrazione; il post-training li riduce, non li risolve.

</details>

<details><summary>Riassumi la pipeline completa di training di un LLM.</summary>

Traccia: (1) pretraining: trilioni di token, next token, dà la conoscenza; (2) SFT: istruzioni e risposte, next token solo sulla risposta; (3) preferenze: scelte e scartate, reward model + PPO oppure DPO; (4) RLVR: problemi verificabili, reward 0/1, GRPO; (5) ogni stadio parte dal modello precedente, che fa da riferimento per la KL; (6) passaggio dall'imitazione (risposta data) al reward (risposta generata e giudicata); il post-training plasma il comportamento.

</details>
