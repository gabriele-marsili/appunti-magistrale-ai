# L12 · Laboratorio: word embedding

*Word Embeddings: when words become coordinates* · 13/10/2026 · Andrea Ceni · lettura: J&M cap. 5 (§5.2-5.4 ipotesi distribuzionale, matrice parola-contesto, coseno; §5.5 word2vec, in particolare §5.5.1-5.5.2 con Eq. 5.19-5.27 e §5.5.3 GloVe e fasttext; §5.6 visualizzazione; §5.7 analogie; §5.8 bias; §5.9 valutazione con WordSim-353 e SimLex-999); cap. 11, §11.1.1-11.1.2 (tf-idf); Appendice J (PPMI)

[Versione interattiva sul sito](https://gabriele-marsili.github.io/appunti-magistrale-ai/anno-2/hlt/sito/#L12) · [Indice della dispensa](README.md)

Laboratorio (solo notebook, nessuna slide) che mette in pratica la **semantica vettoriale** della L10 e **word2vec** della L11. Si parte da un corpus giocattolo: matrice parola-contesto, **coseno**, **PPMI** che spegne la colonna di *the*. Poi word2vec (skip-gram con negative sampling) addestrato con gensim su *Pinocchio*, e i vettori pre-addestrati **GloVe** 100d: vicini, odd-one-out, **analogie** (e perché le parole di input vanno escluse), PCA, bias di genere, il vettore unico di *bank*. Infine una gara di classificazione del sentiment: **media degli embedding** (0,7325) contro **TF-IDF** (0,8725). Gli esercizi: Spearman su WordSim-353 e SimLex-999, la loss e i gradienti di SGNS scritti a mano e usati per addestrare word2vec da zero, battere la baseline densa, il debiasing per proiezione e il test *lipstick on a pig*.

Tutto rieseguito (gensim 4.4, scikit-learn 1.9, NLTK 3.10.3, GloVe scaricato da gensim-data): tutti i numeri si riproducono tranne i vicini di gensim, non deterministici con più thread, e la TF-IDF, il cui output salvato (0,865) non corrisponde al codice. Errori trovati: la check cell dell'esercizio 1 con il controllo "non implementato" disattivato e l'output TF-IDF non aggiornato.

## Indice

- [Notebook](#notebook)
- [Studio ed esercizi](#studio-ed-esercizi)

## Notebook

Commento al notebook del corso `HLT-2026-27-L12-Word-embeddings.ipynb` (il notebook è del docente e non è incluso).

Prima parte guidata (celle 0-31). Sezione 1: un corpus giocattolo di otto frasi su gatti, cani, pizza e pasta, con cui si costruiscono a mano gli **embedding da conteggi** della L10: matrice parola-contesto, coseno, PPMI. Sezione 2: si passa ai vettori **densi** addestrando word2vec (skip-gram con negative sampling) con gensim sul testo di *Pinocchio*, lo stesso libro del laboratorio L9.

Ho rieseguito tutte le celle (Python 3.13, gensim 4.4.0, NLTK 3.10.3). La parte sul corpus giocattolo è deterministica e coincide con gli output salvati. Attenzione alla versione di NLTK: gli output salvati di questo notebook vengono da **NLTK 3.10.3** (3.124 frasi, 42.696 token di Pinocchio); con NLTK 3.9.2 la segmentazione in frasi dà 2.209 frasi e 42.525 token (l'opposto del laboratorio L9, che era stato eseguito con la 3.9). I vicini prodotti da gensim cambiano un po' a ogni esecuzione (vedi il blocco sui vicini di Pinocchio).

### Notebook 1 · Obiettivi, letture e setup

```python
!pip -q install gensim
import math, re, random
from collections import Counter
import numpy as np, pandas as pd, matplotlib.pyplot as plt, nltk
from sklearn.decomposition import PCA
SEED = 42; random.seed(SEED); np.random.seed(SEED)
for _pkg in ["punkt", "punkt_tab", "movie_reviews"]:
    nltk.download(_pkg, quiet=True)
# helper per le check cell degli esercizi: _ok, _fail, _todo, _err, _close, _np_cos
```

Output:

```text
Ready. No words were harmed during vectorization.
```

Gli obiettivi dichiarati: spiegare l'**ipotesi distribuzionale**; costruire un embedding da conteggi, pesarlo con la **PPMI** e confrontare parole con il **coseno**; spiegare che cosa impara **word2vec** (skip-gram con negative sampling, SGNS); usare embedding statici pre-addestrati per similarità, odd-one-out, analogie, visualizzazione; riconoscerne i limiti (dipendenza dal corpus, cecità al contesto, bias); confrontare la **media degli embedding** con la baseline sparsa **TF-IDF** in un compito di classificazione.

Letture indicate dal notebook: L10 (J&M §5.1-5.4, §11.1.1-11.1.2 per tf-idf, Appendice J per la PPMI) e L11 (J&M §5.5-5.10). La cella di setup installa gensim, importa le librerie e definisce i piccoli helper usati dalle *check cell* degli esercizi (`_close` confronta due float con tolleranza relativa, `_np_cos` è un coseno già pronto per l'esercizio 4).

Nel file salvato l'output della cella mostra un errore di compilazione di gensim (pip tenta di costruirlo per Python 3.14), ma poi la cella stampa *Ready*: gensim era già installato nell'ambiente, l'errore non ha conseguenze.

### Notebook 2 · Il corpus giocattolo

```python
toy_sentences = [
    "cats chase mice", "dogs chase balls", "cats like milk", "dogs like bones",
    "pizza tastes good", "pasta tastes good", "pizza uses cheese", "pasta uses cheese",
]
toy_tokens = [s.split() for s in toy_sentences]
toy_word_counts = Counter([w for s in toy_sentences for w in s.split()])
```

Output:

```text
Counter({'cats': 2, 'chase': 2, 'dogs': 2, 'like': 2, 'pizza': 2, 'tastes': 2, 'good': 2,
         'pasta': 2, 'uses': 2, 'cheese': 2, 'mice': 1, 'balls': 1, 'milk': 1, 'bones': 1})
Total token words: 24
Dimensions (= vocabulary size): 14
```

L'**ipotesi distribuzionale** ([scheda 9 della L10](L10-semantica-vettoriale.md#p-9)): parole che compaiono in contesti simili tendono ad avere significati simili, *you shall know a word by the company it keeps* (Firth, 1957). Per vederla all'opera basta un universo minuscolo: otto frasi di tre parole, 24 token, 14 tipi. Il corpus è costruito apposta: *cats* e *dogs* compaiono esattamente negli stessi contesti (*chase*, *like*), e così *pizza* e *pasta* (*tastes*, *uses*), mentre i due gruppi non condividono nessun vicino.

Il numero di tipi (14) è anche la **dimensione** dei vettori che costruiremo: un embedding da conteggi ha una dimensione per ogni parola del vocabolario.

### Notebook 3 · La matrice di co-occorrenza

```python
def build_cooccurrence(sentences, window=1):
    vocab = sorted({w for sent in sentences for w in sent})
    word_to_i = {w: i for i, w in enumerate(vocab)}
    matrix = np.zeros((len(vocab), len(vocab)), dtype=int)
    for sent in sentences:
        for i, target in enumerate(sent):
            left, right = max(0, i - window), min(len(sent), i + window + 1)
            for j in range(left, right):
                if i != j:
                    matrix[word_to_i[target], word_to_i[sent[j]]] += 1
    return vocab, word_to_i, matrix

vocab, word_to_i, cooc = build_cooccurrence(toy_tokens, window=1)
```

Output:

```text
        balls bones cats chase cheese dogs good like mice milk ...
cats        0     0    0     1      0    0    0    1    0    0
chase       1     0    1     0      0    1    0    0    1    0
dogs        0     0    0     1      0    0    0    1    0    0
like        0     1    1     0      0    1    0    0    0    1
...
```

La **matrice parola-contesto** della [scheda 18 della L10](L10-semantica-vettoriale.md#p-18): si scorre il corpus, la parola corrente è il **target** $w$, le parole nella **finestra** intorno sono i **contesti** $c$, e ogni coppia (target, contesto) aggiunge 1 alla cella $C(w,c)$ di una matrice $|V|\times|V|$. La figura del notebook mostra le due cose: (A) una finestra $\pm 2$ intorno a *puppet* genera 4 coppie; (B) con finestra $\pm 1$ in una frase di tre parole la parola centrale genera 2 coppie e quelle ai bordi 1 sola. Ogni frase dà quindi 4 coppie, le 8 frasi $N = 32$ coppie da 24 token: dettaglio che tornerà nella PPMI.

Ogni **riga** è il vettore di una parola: *cats* ha un 1 sotto *chase* e uno sotto *like*, esattamente come *dogs*. Sono embedding **sparsi** (quasi tutti zeri) e **interpretabili** (la dimensione *chase* vuol dire "quante volte accanto a *chase*"), con tante dimensioni quante le parole del vocabolario ([scheda 15 della L10](L10-semantica-vettoriale.md#p-15)). Con una finestra simmetrica la matrice è simmetrica: la riga di $w$ coincide con la sua colonna, perché ogni coppia $(w,c)$ viene contata anche come $(c,w)$ quando il target è $c$.

### Notebook 4 · Il coseno

```python
def cos(a, b):
    a = np.asarray(a).reshape(1, -1); b = np.asarray(b).reshape(1, -1)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(cosine_similarity(a, b)[0, 0])

def toy_similarity(w1, w2):
    return cos(cooc[word_to_i[w1]], cooc[word_to_i[w2]])
```

Output:

```text
('cats', 'dogs') 1.0
('pizza', 'pasta') 1.0
('cats', 'pizza') 0.0
```

La **similarità coseno** ([scheda 27 della L10](L10-semantica-vettoriale.md#p-27)):
$$\cos(\mathbf u,\mathbf v)=\frac{\mathbf u\cdot\mathbf v}{\|\mathbf u\|\,\|\mathbf v\|}=\frac{\sum_i u_iv_i}{\sqrt{\sum_i u_i^2}\sqrt{\sum_i v_i^2}}$$
Con conteggi (mai negativi) sta fra 0 e 1; con gli embedding densi può essere negativa. Il notebook ricorda perché non si usa il prodotto scalare puro: cresce con la lunghezza dei vettori, e le parole frequenti hanno vettori lunghi, quindi sembrerebbero simili a tutto ([scheda 25 della L10](L10-semantica-vettoriale.md#p-25)).

Risultati: *cats*-*dogs* e *pizza*-*pasta* valgono 1 (righe identiche), *cats*-*pizza* vale 0 (nessun contesto in comune, prodotto scalare nullo). La funzione `cos` restituisce 0 se uno dei vettori è nullo, per evitare la divisione per zero: lo useremo per tutto il notebook, anche sui vettori GloVe.

### Notebook 5 · Checkpoint: giocare con il corpus

```python
def nearest_in_toy(word, topn=5):
    scores = [(other, round(toy_similarity(word, other), 3)) for other in vocab if other != word]
    return sorted(scores, key=lambda x: x[1], reverse=True)[:topn]

nearest_in_toy("pizza")
```

Output:

```text
[('pasta', 1.0), ('cheese', 0.707), ('good', 0.707), ('balls', 0.0), ('bones', 0.0)]
```

Il vicino più prossimo di *pizza* è *pasta* (1,0), poi *cheese* e *good* a 0,707. Conto: la riga di *pizza* ha 1 sotto *tastes* e 1 sotto *uses* (norma $\sqrt2$); quella di *cheese* ha solo 1 sotto *uses* (norma 1); prodotto scalare 1, coseno $1/\sqrt2 = 0{,}707$. *Cheese* e *pizza* non sono "simili" come cibo: condividono un contesto, *uses*, perché entrambi gli stanno accanto. È una similarità **del secondo ordine**, basata sui vicini comuni.

Le quattro domande del checkpoint, con le risposte verificate ricalcolando la matrice (esercizio 5 per i conti):

1. *Gigi hates Gianni* non cambia nulla per *cats* e *dogs*: le loro righe non toccano le parole nuove, il coseno resta 1.
2. *Gigi hates pizza* sì: la riga di *pizza* guadagna la dimensione *hates*, e il coseno con *pasta* scende a $2/(\sqrt3\sqrt2) = 0{,}816$.
3. Per tornare a 1 basta dare a *pasta* lo stesso contesto: *Gigi hates pasta*.
4. Per avvicinare *cats* e *pizza* serve un contesto in comune, per esempio *pizza chase mice* o *cats tastes good*: il coseno passa da 0 a $1/(\sqrt3\sqrt2) = 0{,}408$ (la seconda abbassa anche *cats*-*dogs* a 0,816).

Morale: il "significato" di un embedding da conteggi è tutto e solo nei contesti osservati; una frase in più cambia la geometria.

### Notebook 6 · Troppo sale: PMI e PPMI

```python
def ppmi(counts):
    counts = [[float(c) for c in row] for row in counts]
    N = sum(sum(row) for row in counts)
    row_sums = [sum(row) for row in counts]
    col_sums = [sum(col) for col in zip(*counts)]
    result = []
    for i, row in enumerate(counts):
        new_row = []
        for j, c in enumerate(row):
            if c == 0:
                new_row.append(0.0)
            else:
                pmi = math.log2(c * N / (row_sums[i] * col_sums[j]))
                new_row.append(max(pmi, 0.0))
        result.append(new_row)
    return result
```

Nei corpora veri parole come *the*, *of*, *and* stanno accanto a quasi tutto: con i conteggi grezzi tutte le parole condividono questi contesti e sembrano simili. Il rimedio è la **pointwise mutual information** ([scheda 48 della L10](L10-semantica-vettoriale.md#p-48)): $w$ e $c$ compaiono insieme più spesso di quanto ci si aspetterebbe se fossero indipendenti?
$$\text{PMI}(w,c)=\log_2\frac{P(w,c)}{P(w)\,P(c)}\qquad \text{PPMI}(w,c)=\max\big(\text{PMI}(w,c),\,0\big)$$
I valori negativi ("si evitano") sono inaffidabili senza corpora enormi e vengono portati a 0 ([scheda 50 della L10](L10-semantica-vettoriale.md#p-50)).

Il punto delicato è **quali probabilità**. L'evento elementare è una **coppia** (target, contesto), e tutte e tre le probabilità si calcolano sulle stesse $N = \sum_{w,c} C(w,c)$ coppie, come nella [scheda 52 della L10](L10-semantica-vettoriale.md#p-52):
$$P(w,c)=\frac{C(w,c)}{N}\qquad P(w)=\frac{\sum_c C(w,c)}{N}\ (\text{riga})\qquad P(c)=\frac{\sum_w C(w,c)}{N}\ (\text{colonna})$$
Perché la somma di riga e non la frequenza della parola? Nel corpus giocattolo *cats* e *chase* compaiono entrambe 2 volte, ma *cats* è sempre al bordo (2 coppie) e *chase* sempre al centro (4 coppie): $P(\textit{chase}) = 4/32$, $P(\textit{cats}) = 2/32$. Contando coppie, la PMI vale esattamente 0 quando $w$ e $c$ sono indipendenti. Per esempio $\text{PPMI}(\textit{cats},\textit{chase}) = \log_2\frac{1\cdot 32}{2\cdot 4} = 2$.

Due note del notebook: la PMI dei bigrammi del laboratorio L9 è la stessa cosa con la finestra più stretta possibile, una parola a sinistra (lì $N$ era il numero di token, che è circa il numero di coppie); e la $N$ della PMI (coppie) non è la $N$ del tf-idf (documenti). La funzione `ppmi` calcola $\log_2\frac{C(w,c)\,N}{\text{riga}_w\cdot\text{colonna}_c}$, che è la stessa formula con le $N$ semplificate, e lascia a 0 le celle vuote (dove la PMI sarebbe $-\infty$).

### Notebook 7 · Il mondo del "the": conteggi grezzi contro PPMI

```python
the_sentences = [
    "the cats chase the mice", "the dogs chase the balls",
    "the cats like the milk", "the dogs like the bones",
    "the pizza tastes good", "the pasta tastes good",
    "the pizza uses the cheese", "the pasta uses the cheese",
]
the_vocab, the_ix, the_counts = build_cooccurrence([s.split() for s in the_sentences], window=1)
the_ppmi = np.asarray(ppmi(the_counts), dtype=float)
```

Output:

```text
            pair  cosine on raw counts  cosine on PPMI
0    cats - dogs                 1.000           1.000
1  pizza - pasta                 1.000           1.000
2   cats - pizza                 0.667           0.045
3  dogs - cheese                 0.816           0.212
4    mice - milk                 1.000           1.000
PPMI of the column 'the': {'cats': 0.58, 'pizza': 0.58, 'mice': 1.58, 'cheese': 1.58}
```

Stesse frasi con *the* davanti a ogni nome. Ora *cats* e *pizza* condividono il contesto *the* (2 volte ciascuno) e sui conteggi grezzi il coseno sale da 0 a 0,667: righe $(\textit{chase}{:}1,\ \textit{like}{:}1,\ \textit{the}{:}2)$ e $(\textit{tastes}{:}1,\ \textit{uses}{:}1,\ \textit{the}{:}2)$, prodotto scalare 4, norme $\sqrt6$, coseno $4/6$. Con la PPMI crolla a 0,045.

La figura (due heatmap affiancate, righe = target, colonne = contesti, colonna *the* nel riquadro arancione) mostra perché. Nei conteggi grezzi la colonna *the* è la più scura (valori 2 per quasi tutti i nomi). Nella PPMI scende a 0,6 per i nomi che hanno anche altri contesti: $N = 60$ coppie, la colonna *the* somma 20, quindi $\text{PPMI}(\textit{cats},\textit{the}) = \log_2\frac{2\cdot 60}{4\cdot 20} = \log_2 1{,}5 = 0{,}58$, mentre le coppie informative salgono a 1,9 (*cats*-*chase*: $\log_2\frac{1\cdot 60}{4\cdot 4} = 1{,}91$) e la più forte è *good*-*tastes* con 3,9 ($\log_2\frac{2\cdot60}{2\cdot4} = \log_2 15$).

Le risposte alle domande *Discuss*:

- *cats*-*pizza* crolla perché l'unico contesto comune, *the*, ora pesa poco (0,58) rispetto ai contesti distintivi (1,91): il prodotto scalare è $0{,}58^2 = 0{,}34$ su norme di circa 2,8. *cats*-*dogs* resta a 1 perché le due righe sono identiche: la PPMI cambia i pesi, non l'uguaglianza.
- *mice* e *milk* hanno similarità 1 anche con la PPMI: entrambe compaiono solo dopo *the*, quindi le righe hanno un solo valore non nullo (1,58, più alto perché per queste parole *the* è l'unica evidenza). Non è un difetto della PPMI ma **mancanza di dati**: con un solo contesto osservato, tutte le parole viste solo accanto a *the* sono indistinguibili.

Il riquadro della cella 21 ricorda la variante della [scheda 57 della L10](L10-semantica-vettoriale.md#p-57): la PMI favorisce i contesti rari, e si corregge con $P_\alpha(c) = \text{count}(c)^\alpha/\sum_{c'}\text{count}(c')^\alpha$, $\alpha = 0{,}75$, che alza un po' la probabilità dei contesti rari e quindi abbassa la loro PMI. La funzione del notebook usa la PPMI semplice. Lo stesso $\alpha$ torna in word2vec per estrarre le parole negative.

### Notebook 8 · Che cosa insegna il modello giocattolo

Il riepilogo della sezione 1, in quattro punti: una parola si rappresenta con la sua **distribuzione sui contesti**; distribuzioni simili danno vettori simili; i conteggi grezzi sono dominati dalle parole frequenti, quindi la **pesatura** (PPMI per le parole, tf-idf per i documenti) è essenziale; il difetto dei vettori da conteggi è che sono **sparsi** e crescono con il vocabolario (decine o centinaia di migliaia di dimensioni). Gli embedding densi come word2vec imparano invece una rappresentazione compatta di 50-300 dimensioni, senza memorizzare la matrice dei conteggi ([scheda 5 della L11](L11-embedding-word2vec.md#p-5)).

### Notebook 9 · Word2vec: che cosa impara SGNS e dove sono gli embedding

Word2vec impara i vettori risolvendo un compito di predizione: in **skip-gram** la parola centrale predice i contesti, in **CBOW** il contesto predice la parola centrale ([schede 36-37 della L11](L11-embedding-word2vec.md#p-36)). I vettori sono un sottoprodotto: si inventa un compito la cui soluzione costringe a costruire la rappresentazione voluta (self-supervision).

**Skip-gram con negative sampling** addestra una piccola **regressione logistica** (quella della L6) che distingue coppie vere da coppie finte:
$$P(+\mid w,c)=\sigma(\mathbf c\cdot\mathbf w)=\frac{1}{1+e^{-\mathbf c\cdot\mathbf w}}$$
Esempi positivi: le coppie $(w, c_{pos})$ che compaiono davvero nella finestra; negativi: per ogni positivo, $k$ coppie $(w, c_{neg})$ con $c_{neg}$ estratto dal vocabolario con probabilità $\propto \text{count}^{0{,}75}$ ([scheda 22 della L11](L11-embedding-word2vec.md#p-22)). Ogni parola ha **due** vettori, $\mathbf w$ come target e $\mathbf c$ come contesto ([scheda 17 della L11](L11-embedding-word2vec.md#p-17)); il training alza $\mathbf c_{pos}\cdot\mathbf w$ e abbassa $\mathbf c_{neg}\cdot\mathbf w$. Due parole con gli stessi contesti vengono spinte verso gli stessi vettori di contesto e finiscono vicine: l'ipotesi distribuzionale, ora imparata invece che contata.

La figura mostra le due matrici: $W$ (vettori target, arancione) e $C$ (vettori di contesto, blu), entrambe $|V|$ righe per $d$ colonne ($d$ = `vector_size` = 80). Durante il training la coppia vera (*pinocchio*, *nose*) spinge in su $\mathbf c\cdot\mathbf w$, una coppia con una parola casuale lo spinge in giù. Dopo il training l'embedding di una parola è la sua **riga di $W$**: `pinocchio_w2v.wv["pinocchio"]` restituisce 80 numeri. È comune buttare $C$ o usare $W + C$ ([scheda 32 della L11](L11-embedding-word2vec.md#p-32)); gensim tiene $W$ in `wv` e conserva $C$ in `syn1neg`. Differenza con la riga della matrice dei conteggi: le $d$ colonne **non hanno un nome**, contano solo distanze e direzioni.

### Notebook 10 · Pinocchio: dal testo alle frasi, poi il training

```python
text = requests.get("https://www.gutenberg.org/files/500/500-0.txt", timeout=30).content.decode("utf-8", errors="ignore")
sentences = []
for sent in nltk.sent_tokenize(text):
    toks = [w.lower() for w in nltk.word_tokenize(sent) if w.isalpha()]
    if len(toks) >= 3:
        sentences.append(toks)

pinocchio_w2v = Word2Vec(sentences=sentences, vector_size=80, window=10,
                         min_count=2, sg=1, epochs=20, seed=SEED)
```

Output:

```text
Downloaded 239,501 characters of wooden-puppet drama.
sentences: 3124   tokens: 42696
example: ['geppetto', 'do', 'not', 'insult', 'me', 'or', 'i', 'shall', 'call', 'you', 'polendina']
Vocabulary size: 2182
Vector size: 80
```

Il corpus è *Pinocchio* da Project Gutenberg (239.501 caratteri, licenza compresa). Il preprocessing: segmentazione in frasi e tokenizzazione Penn Treebank di NLTK, minuscole, solo token alfabetici (via punteggiatura e numeri), frasi di almeno 3 parole. Risultato: 3.124 frasi, 42.696 token. Con NLTK 3.9.2 lo stesso codice dà 2.209 frasi e 42.525 token: cambia la segmentazione in frasi (come già visto nel laboratorio L9), non il resto.

Gli iperparametri di `Word2Vec`, da saper leggere: `vector_size=80` = dimensione $d$; `window=10` = distanza massima target-contesto; `min_count=2` = le parole viste una sola volta escono dal vocabolario (restano 2.182 tipi); `sg=1` = skip-gram (0 = CBOW); `epochs=20` passate sul corpus. Non indicati, quindi ai default di gensim: `negative=5` ($k$), `ns_exponent=0.75` ($\alpha$), `sample=1e-3` (subsampling delle parole frequenti), `workers=3`.

Il notebook lo dice subito: 42 mila token sono pochissimi (GloVe ne ha visti 6 miliardi), e il risultato serve proprio a vedere che aspetto ha la **scarsità di dati**.

### Notebook 11 · I vicini nel modello di Pinocchio e gli iperparametri

```python
for word in ["pinocchio", "father", "fox", "school", "hands"]:
    print(word, pinocchio_w2v.wv.most_similar(word, topn=5))
```

Output:

```text
pinocchio: bravo 0.635, insulted 0.632, breaking 0.622, jumping 0.615, anxiously 0.614
father:    comfort 0.741, son 0.733, spare 0.723, milk 0.718, saved 0.672
fox:       cat 0.916, blind 0.776, innkeeper 0.767, repeated 0.764, met 0.745
school:    succeed 0.868, study 0.845, sing 0.803, pipes 0.784, ahead 0.776
hands:     clapped 0.821, shook 0.793, swore 0.793, wig 0.777, together 0.759
```

I vicini riflettono la **storia**, non il significato generale: *fox* ha come primo vicino *cat* (0,92), perché il Gatto e la Volpe compaiono sempre insieme; *school* sta con *study* e *succeed* (le promesse di Pinocchio); *father* con *son*. Molti vicini sono rumore (*milk* per *father*, *pipes* per *school*): con poche occorrenze per parola le stime sono instabili.

Instabili anche in senso letterale: rieseguendo la cella i numeri cambiano. Nelle mie due esecuzioni *pinocchio* ha avuto come vicini *marionette, setting, bless* e poi *bravo, sneezing, he*, con NLTK identico. Il motivo: gensim usa 3 thread (`workers=3`) e l'ordine con cui i thread aggiornano i vettori non è deterministico; il `seed` fissa solo l'inizializzazione. Per risultati riproducibili servono `workers=1` e un `PYTHONHASHSEED` fisso. È la **variabilità intrinseca** di cui parla J&M §5.9.

Il mini-esperimento chiede di cambiare un iperparametro alla volta. Le due domande, verificate addestrando con `workers=1`:

- **Finestra** ([scheda 45 della L11](L11-embedding-word2vec.md#p-45)): con `window=2` i vicini di *hands* sono parti del corpo (*arms, teeth, legs, body, shoulders*): parole che occupano lo stesso posto nella frase (*his hands*, *his legs*), similarità più sintattica e di tipo. Con `window=10` diventano parole della scena (*clapped, shook, swore, crossed, together*): ciò che succede intorno alle mani, similarità più tematica.
- **Velocità**: CBOW è più veloce (0,7-0,8 s contro 1,1 s con finestra 2 e 3,0 s con finestra 10, nelle mie prove). Skip-gram fa un passo di classificazione per **ogni coppia** (target, contesto), circa $2L$ per token con finestra $L$; CBOW ne fa **uno per token**, con la media dei vettori di contesto come input. Per questo il costo di skip-gram cresce con la finestra e quello di CBOW quasi no.

Commento al notebook del corso `HLT-2026-27-L12-Word-embeddings.ipynb` (il notebook è del docente e non è incluso).

Seconda parte guidata (celle 32-85). Si caricano i vettori **GloVe** 100d pre-addestrati (400.000 parole) e li si interroga: vicini più prossimi, il gioco dell'intruso, le **analogie** con il metodo del parallelogramma scritto a mano, una proiezione PCA, i **bias** di genere, il vettore unico di *bank*. Poi dalle parole ai documenti: la **media degli embedding** come rappresentazione di una frase, e una gara di classificazione del sentiment sulle recensioni di film del laboratorio L9, media degli embedding contro **TF-IDF**.

Ho rieseguito tutto (il download di GloVe da gensim-data funziona, 128 MB): tutte le celle danno output identici a quelli salvati, tranne la TF-IDF (cella 78 e seguenti), dove il codice dà 0,8725 e non lo 0,865 salvato (riquadro nel blocco della TF-IDF).

### Notebook 1 · GloVe: un embedding pre-addestrato

```python
import gensim.downloader as api
USE_LARGE_GOOGLE_NEWS = False
model_name = "word2vec-google-news-300" if USE_LARGE_GOOGLE_NEWS else "glove-wiki-gigaword-100"
emb = api.load(model_name)
```

Output:

```text
Loading: glove-wiki-gigaword-100
Loaded 400000 vectors of dimension 100
The vector of 'pizza' starts with [ 0.228  0.045 -0.555 -0.003 -0.037  0.463  0.998 -0.508] ...
```

Addestrare su un libro è istruttivo ma limitato; si prendono in prestito vettori addestrati da altri su miliardi di parole. Il default è **GloVe 100d** (*Global Vectors*, Stanford): Wikipedia + Gigaword, 6 miliardi di token, 400.000 parole tutte minuscole, 128 MB. In alternativa (flag `USE_LARGE_GOOGLE_NEWS`) i vettori **word2vec** di Google News: 300 dimensioni, circa 100 miliardi di parole, 1,6 GB.

**GloVe non è word2vec** ([scheda 40 della L11](L11-embedding-word2vec.md#p-40)), ma sta a metà strada: come i modelli a conteggi costruisce prima una matrice di co-occorrenza parola-contesto $X$ su tutto il corpus; come word2vec poi *impara* vettori densi, chiedendo che il prodotto scalare fra vettore della parola e vettore del contesto approssimi il logaritmo del conteggio, $\mathbf w\cdot\mathbf c\approx\log X_{wc}$ (più due termini di bias, omessi nel notebook). Stessa materia prima, le statistiche di co-occorrenza: per questo i vettori GloVe si comportano come quelli di word2vec.

Sono embedding **statici**: un solo vettore per voce del vocabolario. Il riquadro su **fasttext** ([scheda 38 della L11](L11-embedding-word2vec.md#p-38)): skip-gram sulla parola e sui suoi n-grammi di caratteri (da 3 a 6), quindi sa costruire un vettore anche per una parola mai vista; GloVe e word2vec no, `emb["pinocchiesque"]` dà `KeyError`. In gensim si addestra con `gensim.models.FastText`, con la stessa interfaccia di `Word2Vec`.

### Notebook 2 · Vicini più prossimi: GloVe contro Pinocchio

```python
for word in ["car", "computer", "pizza", "language"]:
    print(word, emb.most_similar(word, topn=5))
for word in ["pinocchio", "father", "fox", "school", "hands"]:
    print(word, emb.most_similar(word, topn=5))
```

Output:

```text
CAR       vehicle 0.863, truck 0.86, cars 0.837, driver 0.819, driving 0.781
COMPUTER  computers 0.875, software 0.837, technology 0.764, pc 0.737, hardware 0.729
PIZZA     sandwich 0.749, sandwiches 0.722, bread 0.701, pizzas 0.7, burger 0.698
LANGUAGE  languages 0.826, word 0.746, spoken 0.738, arabic 0.732, english 0.721

PINOCCHIO geppetto 0.666, bambi 0.577, rapunzel 0.577, snowman 0.553, collodi 0.55
FATHER    son 0.924, brother 0.922, grandfather 0.883, mother 0.866, uncle 0.865
FOX       abc 0.796, nbc 0.778, cbs 0.756, television 0.736, tv 0.709
SCHOOL    college 0.885, schools 0.836, elementary 0.816, students 0.803, student 0.781
HANDS     hand 0.834, face 0.701, fingers 0.7, away 0.698, down 0.695
```

`most_similar` restituisce le parole con il **coseno** più alto (gensim normalizza i vettori e fa un prodotto matrice-vettore su tutto il vocabolario). Il modello non ha definizioni: solo geometria appresa dalle statistiche del corpus. Nei vicini si vedono tutti i tipi di relazione mescolati: sinonimi o quasi (*car*-*vehicle*), co-iponimi (*pizza*-*sandwich*, *father*-*brother*), forme flesse (*cars*, *computers*, *pizzas*), parole solo correlate (*car*-*driver*, *language*-*spoken*). Il coseno di un modello distribuzionale misura la **relatedness** più che la similarità stretta ([scheda 6 della L10](L10-semantica-vettoriale.md#p-6)): tornerà nell'esercizio 1.

Le stesse cinque parole del modello di Pinocchio ora hanno vicini da "senso comune": *father* con i nomi di parentela, *school* con *college*, *hands* con *hand, fingers*. *Pinocchio* è un personaggio fra altri personaggi di fiabe (*bambi, rapunzel*) e il suo autore (*collodi*): in Wikipedia di Pinocchio si parla **dall'esterno**, nel libro dall'interno. Il corpus decide.

### Notebook 3 · Fox: il corpus decide quale senso

Nel modello di Pinocchio *fox* è il personaggio, vicino a *cat*; in GloVe è la rete televisiva, vicina ad *abc, nbc, cbs*. Un embedding statico ha un solo vettore per parola, e quel vettore cattura il senso **dominante nel corpus** di addestramento: nelle notizie e in Wikipedia Fox è soprattutto un network. Gli embedding catturano ciò che il corpus enfatizza, non un "vero significato" universale; il corpus conta non solo per l'affidabilità ma per **quale senso** viene appreso.

> **Approfondimento: Polisemia od omonimia?**
>
> Il notebook chiama il caso di *fox* **polisemia**. A rigore la linguistica distingue la **polisemia** (sensi diversi ma collegati: *bank* la banca e il palazzo della banca) dall'**omonimia** (stessa forma, significati senza relazione: *bank* la banca e la riva). La rete Fox prende il nome dalla Fox Film Corporation di William Fox, non dall'animale: è più un caso di omonimia (per di più fra un nome comune e un nome proprio). Per l'embedding la differenza non conta: in entrambi i casi un'unica forma riceve un unico vettore, mescolanza dei sensi pesata per frequenza (blocco su *bank* più avanti). J&M §5.1 usa il termine generico *polysemous* e rimanda all'Appendice I per i sensi.

### Notebook 4 · Il gioco dell'intruso

```python
def odd_one_out(words):
    vectors = [emb[w] for w in words]
    center = np.mean(vectors, axis=0)
    sims = [cos(v, center) for v in vectors]
    return words[sims.index(min(sims))]

fool_sets = [["fox", "cat", "dog", "whale"]]
```

Output:

```text
['fox', 'cat', 'dog', 'whale'] -> fox
```

Strategia per trovare l'intruso: il **centroide** del gruppo (media dei vettori) e la parola con il coseno minimo rispetto al centroide. L'esempio del notebook è già una trappola: fra *fox, cat, dog, whale* ci si aspetterebbe *whale* (unico animale marino), ma il modello sceglie *fox*, perché in GloVe *fox* è soprattutto la rete televisiva e il suo vettore si allontana dagli animali. È il blocco precedente visto da un'altra parte.

La consegna invita a costruire insiemi che **ingannano** il modello: gli errori dicono che cosa ha davvero catturato lo spazio più dei successi. Due limiti del metodo da ricordare: l'intruso partecipa al centroide (con pochi elementi lo sposta verso di sé), e una parola rara o ambigua ha un vettore "medio" che può risultare lontano da tutto.

### Notebook 5 · Analogie con gensim

```python
def gensim_analogy(model, a, b, c, topn=5):
    # a : b :: c : d  ->  b - a = d - c  ->  d = b - a + c
    return [(w, round(s, 3)) for w, s in model.most_similar(positive=[b, c], negative=[a], topn=topn)]

gensim_analogy(emb, "man", "king", "woman")
gensim_analogy(emb, "germany", "hitler", "italy")
```

Output:

```text
man : king :: woman : ?
[('queen', 0.77), ('monarch', 0.684), ('throne', 0.676), ('daughter', 0.659), ('princess', 0.652)]
germany : hitler :: italy : ?
[('mussolini', 0.827), ('fascist', 0.685), ('stalin', 0.667), ('adolf', 0.626), ('napoleon', 0.582)]
```

Il **metodo del parallelogramma** ([scheda 48 della L11](L11-embedding-word2vec.md#p-48)): per $a : b :: c : ?$ si cerca la parola più vicina a $\mathbf b - \mathbf a + \mathbf c$. Funziona quando la relazione è codificata, almeno approssimativamente, come una **direzione**: lo spostamento $\mathbf{king}-\mathbf{man}$ è vicino a $\mathbf{queen}-\mathbf{woman}$. Nella notazione di gensim si passano $b$ e $c$ come `positive` e $a$ come `negative`.

Il riquadro della cella 45: la L11 scrive il metodo come l'argmin di una distanza, "per esempio euclidea"; gensim ordina invece per **coseno**. Per vettori di norma 1 le due classifiche coincidono: $\|\mathbf t - \mathbf x\|^2 = \|\mathbf t\|^2 + 1 - 2\,\mathbf t\cdot\mathbf x$, e con $\mathbf t$ fisso minimizzare la distanza equivale a massimizzare $\mathbf t\cdot\mathbf x$, cioè il coseno.

Gli esempi riescono (*queen* 0,77; *mussolini* 0,83), ma il notebook avverte: non trasformare un'analogia riuscita in una religione, i risultati cambiano con modello, corpus, vocabolario e tipo di relazione ([scheda 50 della L11](L11-embedding-word2vec.md#p-50)).

### Notebook 6 · Analogie a mano: perché si escludono le parole di input

```python
VOCAB_50K = emb.index_to_key[:50000]       # GloVe ordina le parole per frequenza
_M50 = np.vstack([emb[w] for w in VOCAB_50K])
_M50 = _M50 / np.linalg.norm(_M50, axis=1, keepdims=True)

def similarities_to(vec):
    vec = np.asarray(vec, dtype=float)
    return _M50 @ (vec / np.linalg.norm(vec))

def analogy(a, b, c, topn=5, exclude_inputs=True):
    target = emb[b] - emb[a] + emb[c]
    scores = similarities_to(target)
    result = []
    for i in np.argsort(-scores):
        word = VOCAB_50K[i]
        if exclude_inputs and word in (a, b, c):
            continue
        result.append((word, float(scores[i])))
        if len(result) == topn:
            break
    return result
```

Output:

```text
  a : b :: c : ?             inputs excluded              inputs allowed             gensim most_similar
man : king :: woman        queen, monarch, throne       king, queen, monarch       queen, monarch, throne
france : paris :: italy    rome, milan, naples          rome, milan, italy         rome, milan, naples
good : better :: bad       worse, too, getting          bad, worse, better         worse, too, even
mouse : mice :: child      children, pregnant, infants  child, children, pregnant  children, pregnant, infants
walk : walked :: swim      swam, swimming, drowned      swim, swam, swimming       swam, swimming, drowned
big : bigger :: small      larger, smaller, large       ...                        ...

gensim_analogy(emb, "good", "best", "bad")
[('worst', 0.698), ('movie', 0.667), ('big', 0.665), ('ever', 0.657), ('film', 0.638)]
```

Si riscrive l'analogia aprendo la scatola: `similarities_to` calcola in un colpo il coseno fra un vettore e le prime 50.000 parole (righe normalizzate, un prodotto matrice-vettore), `analogy` ordina per coseno con $\mathbf b-\mathbf a+\mathbf c$ e, se `exclude_inputs=True`, salta $a$, $b$, $c$.

La tabella risponde alla scommessa e alle domande *Discuss*:

- **Senza esclusione vince quasi sempre un input**, di solito $b$ o $c$: *king* per *man : king :: woman*, *bad* per *good : better :: bad*, *child*, *swim*. Geometricamente è inevitabile quando lo spostamento $\mathbf b-\mathbf a$ è piccolo rispetto ai vettori: $\mathbf b - \mathbf a + \mathbf c$ resta a distanza $\|\mathbf b-\mathbf a\|$ da $\mathbf c$, e quasi nessun'altra parola è così vicina. Per questo la regola di esclusione ([scheda 50 della L11](L11-embedding-word2vec.md#p-50)) fa una parte consistente del lavoro nei risultati famosi: la risposta "giusta" spesso è solo il **secondo** vicino.
- gensim esclude anch'esso gli input e in più **normalizza** i tre vettori prima di combinarli: per questo su *good : better :: bad* le terze risposte differiscono (*getting* contro *even*).
- *big : bigger :: small* dà *larger* prima di *smaller*: fallimento dell'embedding o della valutazione? Un po' tutti e due: *larger* è un comparativo plausibile semanticamente vicino, ma la relazione richiesta era "comparativo di *small*". Con una valutazione a corrispondenza esatta conta come errore, anche se il modello ha catturato la parte "comparativo".

Il laboratorio delle analogie (cella 53) mostra un fallimento istruttivo: *good : best :: bad* dà *worst*, ma subito dopo *movie, big, ever, film*: i superlativi in Wikipedia e nelle notizie compaiono in frasi come *the worst movie ever*, e il vettore somma porta con sé quel contesto.

### Notebook 7 · Visualizzare lo spazio con la PCA

```python
def plot_words(model, words):
    words = [w for w in words if w in model]
    vectors = np.vstack([model[w] for w in words])
    xy = PCA(n_components=2).fit_transform(vectors)
    plt.scatter(xy[:, 0], xy[:, 1]) ...

plot_words(emb, ["king", "queen", "prince", "princess", "dog", "cat", "horse", "tiger",
                 "rome", "paris", "london", "berlin", "pizza", "pasta", "bread", "cheese"])
```

Cento dimensioni non stanno su un proiettore: la **PCA** proietta i 16 vettori sulle due direzioni di massima varianza ([scheda 44 della L11](L11-embedding-word2vec.md#p-44)). Nella figura si vedono quattro gruppi ben separati: cibo a destra (*pizza, pasta, bread, cheese*, PC1 fra 3 e 5), animali in alto al centro (*tiger, horse, cat, dog*), reali a sinistra in alto (*king, queen, princess, prince*, con *king* e *queen* quasi sovrapposti), città in basso a sinistra (*rome* e *berlin* sovrapposte, *paris*, *london*). PC1 separa il cibo da tutto il resto, PC2 gli animali e i reali dalle città.

Avvertenza del notebook: è un'**ombra** 2D, non la geometria vera. Due punti vicini nel piano non sono per forza vicini in 100 dimensioni (qui *king* e *queen* sembrano coincidere, ma il loro coseno è 0,75; *rome* e *berlin*, sovrapposte, hanno coseno 0,63). Il riquadro sulla **t-SNE**: la proiezione più usata per gli embedding (J&M Fig. 5.10) è non lineare, preserva meglio i vicinati locali, ma le distanze fra gruppi lontani non hanno significato e la figura cambia con il seme casuale; la PCA è lineare, veloce e deterministica.

### Notebook 8 · Gli embedding hanno un bagaglio: i bias

```python
professions = ["engineer", "nurse", "teacher", "scientist", "programmer", "doctor", "receptionist", "manager"]
for p in professions:
    sim_w, sim_m = cos(emb[p], emb["woman"]), cos(emb[p], emb["man"])
    rows.append({"profession": p, "sim_woman": sim_w, "sim_man": sim_m, "woman_minus_man": sim_w - sim_m})
```

Output:

```text
  profession  sim_woman  sim_man  woman_minus_man
       nurse      0.614    0.456            0.158
receptionist      0.336    0.190            0.147
     teacher      0.579    0.526            0.054
      doctor      0.633    0.609            0.024
   scientist      0.384    0.437           -0.053
  programmer      0.201    0.265           -0.063
    engineer      0.334    0.430           -0.096
     manager      0.242    0.456           -0.214
```

Gli embedding statici imparano da testi prodotti da persone, quindi codificano anche **stereotipi** e associazioni indesiderate (J&M §5.8, [scheda 53 della L11](L11-embedding-word2vec.md#p-53)). La misura del notebook è la differenza di coseni $\cos(\mathbf p,\mathbf{woman}) - \cos(\mathbf p,\mathbf{man})$ per otto professioni: *nurse* (+0,158) e *receptionist* (+0,147) pendono verso *woman*, *manager* (−0,214) ed *engineer* (−0,096) verso *man*. Da leggere come evidenza sulle **associazioni nei dati** di addestramento, non come verità sulle professioni.

L'esempio classico di Bolukbasi et al. (2016): *man : computer programmer :: woman : homemaker*, con word2vec addestrato sulle notizie. Le domande *Discuss*: un classificatore o un sistema di ranking costruito sopra questi vettori (per esempio lo screening dei CV) eredita le associazioni e può penalizzare un gruppo, un **danno allocativo** ([scheda 55 della L11](L11-embedding-word2vec.md#p-55)); cancellare qualche parola non basta, perché l'associazione è distribuita su moltissime parole e dimensioni (l'esercizio 4 lo misura). L'abitudine da prendere: valutare una rappresentazione non solo sull'accuratezza ma anche sui comportamenti che **non** si vogliono.

### Notebook 9 · Un vettore per bank: gli embedding statici non leggono il contesto

```python
print("bank ->", [w for w, _ in emb.most_similar("bank", topn=10)])
for w in ["loan", "money", "shore", "river"]:
    print(f"cos(bank, {w}) = {cos(emb['bank'], emb[w]):.3f}")
emb.most_similar(positive=["bank", "river"], negative=["money"], topn=6)
```

Output:

```text
bank -> ['banks', 'banking', 'credit', 'investment', 'financial', 'securities', 'lending', 'funds', 'ubs', 'finance']
cos(bank, loan) = 0.551
cos(bank, money) = 0.572
cos(bank, shore) = 0.511
cos(bank, river) = 0.334
bank - money + river -> ['danube', 'estuary', 'rivers', 'rhine', 'tigris', 'meuse']
```

Un embedding statico ha **un vettore per voce**: *bank* è lo stesso in *I deposited money at the bank* e in *We sat on the river bank*. Quel vettore è grosso modo una **miscela dei sensi pesata per frequenza**, e in notizie e Wikipedia vince di gran lunga il senso finanziario: nessuna parola fluviale fra i 10 vicini (risposta alla scommessa), tutti termini bancari.

Il senso fluviale però c'è, nascosto: $\cos(\textit{bank},\textit{shore}) = 0{,}511$, quasi quanto *loan* (0,551). Sottraendo *money* e aggiungendo *river* si arriva in zona fiumi (*danube, estuary, rhine*); il notebook nota che togliere solo *money* non basta. (La cella 66 ristampa gli stessi quattro coseni della cella 64: non cambiano, perché il vettore di *bank* non è stato modificato.)

Il punto è che il modello **non sa scegliere** un vettore diverso in base alla frase. È il ponte verso gli **embedding contestuali**: nei transformer la rappresentazione di un token viene aggiornata dai blocchi di attention usando i token circostanti, quindi *bank* avrà vettori diversi nelle due frasi. Gli stessi limiti valgono per i dataset di valutazione senza contesto ([scheda 57 della L11](L11-embedding-word2vec.md#p-57)).

### Notebook 10 · Dalle parole alle frasi: la media

```python
TOKEN_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
def tokenize_simple(text):
    return TOKEN_RE.findall(text.lower())

def mean_embedding(model, text):
    words = [w for w in tokenize_simple(text) if w in model]
    if not words:
        return np.zeros(model.vector_size, dtype=float)
    return np.mean([model[w] for w in words], axis=0)

def sentence_similarity(model, s1, s2):
    return cos(mean_embedding(model, s1), mean_embedding(model, s2))
```

Output:

```text
0.906 | A dog is running in the park <-> A puppy runs outside
0.904 | I love this movie <-> This film is fantastic
0.441 | I love this movie <-> Quantum mechanics studies physical systems
0.991 | The movie is good <-> The movie is not good
```

La rappresentazione di documento più semplice: la **media dei vettori** delle parole note,
$$\mathbf x_d=\frac{1}{|d|}\sum_{w\in d}\mathbf e_w$$
(le parole fuori vocabolario si saltano, un testo senza parole note diventa il vettore nullo). Perde ordine, sintassi, struttura della negazione, sfumature; eppure è una baseline sorprendentemente utile. Le prime tre coppie vanno come ci si aspetta: frasi con lo stesso significato ma parole diverse (*dog/puppy, running/runs*) hanno coseno 0,906, argomenti diversi 0,441. È il vantaggio dei vettori densi sul bag of words: *puppy* e *dog* sono vicini anche senza essere la stessa parola.

La quarta coppia è il punto debole: *The movie is good* e *The movie is not good* hanno coseno **0,991** nonostante il sentiment opposto. Le due medie condividono *the, movie, is, good*; l'unica differenza è *not*, un vettore in più diluito in una media di cinque. La media non può rappresentare la **composizione** (*not* che si applica a *good*): ordine e struttura contano.

### Notebook 11 · La gara di sentiment: il dataset

```python
from nltk.corpus import movie_reviews
docs, labels = [], []
for label in movie_reviews.categories():
    for fileid in movie_reviews.fileids(label):
        docs.append(" ".join(movie_reviews.words(fileid)))
        labels.append(1 if label == "pos" else 0)
train_idx, test_idx = train_test_split(np.arange(len(docs)), test_size=0.2,
                                       random_state=SEED, stratify=labels)
```

Output:

```text
1600 train reviews, 400 test reviews
```

Si torna alle recensioni di film del laboratorio L9 (`movie_reviews`, 1.000 positive e 1.000 negative), con la stessa divisione stratificata 80/20 (1.600 training, 400 test) e lo stesso seme. Due concorrenti, entrambi con una **regressione logistica** sopra: (A) la media degli embedding GloVe, un vettore denso di 100 numeri; (B) la **TF-IDF**, un vettore sparso di 12.000 numeri.

Regola metodologica sottolineata dal notebook: la TF-IDF si stima **solo sul training**. Se il vocabolario e le idf si calcolassero su tutti i documenti prima della divisione, il test lascerebbe trapelare informazione nel modello (*data leakage*, la stessa logica di train/dev/test della [scheda 27 della L4](L04-modelli-linguistici-n-gram.md#p-27)).

### Notebook 12 · Concorrente A: la media degli embedding

```python
def embed_documents(model, texts):
    return np.vstack([mean_embedding(model, t) for t in tqdm(texts)])

X_train_emb = embed_documents(emb, train_texts)
X_test_emb = embed_documents(emb, test_texts)
clf_emb = LogisticRegression(max_iter=2000, random_state=SEED).fit(X_train_emb, y_train)
acc_emb = accuracy_score(y_test, clf_emb.predict(X_test_emb))
```

Output:

```text
Mean-embedding accuracy: 0.7325
```

Ogni recensione diventa la media dei vettori GloVe delle sue parole (in media circa 790 token: la media di tante parole tende ad assomigliarsi da una recensione all'altra). Accuracy sul test: **0,7325**, cioè 293 recensioni su 400. Non male per un modello con 100 feature e nessuna conoscenza del compito, ma vedremo che è molto sotto la baseline sparsa, e che una parte della differenza non dipende dagli embedding ma da come la regressione logistica è **regolarizzata** (esercizio 3).

### Notebook 13 · Concorrente B: TF-IDF

```python
tfidf = TfidfVectorizer(
    ngram_range=(1, 2),  # unigrammi e bigrammi: "not good" diventa una feature
    min_df=2,            # via gli n-grammi presenti in meno di 2 documenti
    max_features=12000,  # dei rimanenti, i 12k piu' frequenti
    sublinear_tf=True,   # 1 + ln(count) invece del conteggio
)
X_train_tfidf = tfidf.fit_transform(train_texts)
X_test_tfidf = tfidf.transform(test_texts)
clf_tfidf = LogisticRegression(max_iter=2000, random_state=SEED).fit(X_train_tfidf, y_train)
```

Output:

```text
TF-IDF accuracy: 0.8725          (output salvato nel file: 0.865, vedi riquadro)
```

Come una recensione diventa un vettore TF-IDF ([scheda 43 della L10](L10-semantica-vettoriale.md#p-43)):

1. **Feature**: dalle recensioni di training si raccolgono unigrammi e bigrammi, si tolgono quelli presenti in meno di 2 recensioni, si tengono i 12.000 più frequenti.
2. **Term frequency**, quanto conta $t$ in questa recensione ([scheda 39 della L10](L10-semantica-vettoriale.md#p-39)): $\text{tf}_{t,d} = 1+\log_{10}\text{count}(t,d)$ se il conteggio è positivo, 0 altrimenti. Il logaritmo smorza le ripetizioni: 10 occorrenze pesano 2, 100 pesano 3.
3. **Inverse document frequency**, quanto è raro $t$ nella collezione ([scheda 41 della L10](L10-semantica-vettoriale.md#p-41)): $\text{idf}_t = \log_{10}(N/\text{df}_t)$ con $N$ = 1.600 recensioni di training; un termine presente ovunque ha idf 0.
4. **TF-IDF** $= \text{tf}_{t,d}\cdot\text{idf}_t$: alto per i termini frequenti qui e rari altrove.

Il confronto della cella 76: la media degli embedding ha 100 dimensioni condivise da tutte le parole e dà a ogni token lo stesso peso; la TF-IDF ha una dimensione per feature e pesa ciascuna per quanto è informativa.

Il riquadro della cella 77: scikit-learn usa formule un po' diverse. Con `sublinear_tf=True`, $\text{tf} = 1+\ln\text{count}$ (logaritmo naturale); l'idf è **smussata**, $\text{idf}_t = \ln\frac{1+N}{1+\text{df}_t}+1$ (un termine in tutti i documenti ha idf 1, non 0); infine ogni vettore documento è diviso per la sua norma L2. E la cella 79: nella matrice termine-documento della L10 un documento è una **colonna**, scikit-learn tiene la trasposta, una riga per recensione (1.600 × 12.000), come vogliono i classificatori.

> **Attenzione (errore nelle slide): L'output salvato della TF-IDF (0,865) non viene da questo codice**
>
> Nel file salvato le celle 78, 80 e 84 mostrano accuracy **0,865** (precision e recall 0,8614/0,8700 sui negativi). Rieseguendo il codice com'è scritto ottengo **0,8725**, identico con scikit-learn 1.6.1, 1.7.2, 1.8.0 e 1.9.1 (TF-IDF e regressione logistica lbfgs sono deterministiche, la divisione usa lo stesso seme, la media degli embedding dà 0,7325 come nell'output salvato). Lo 0,8725 è anche il numero citato dal markdown dell'esercizio 3 (cella 100), che quindi è giusto: è l'output salvato a essere rimasto da una versione precedente della cella. Con `max_features=20000` invece di 12.000 si ottiene esattamente 0,865, verosimilmente la configurazione di allora. Report corretto, rieseguito: negativi P 0,8706, R 0,8750; positivi P 0,8744, R 0,8700; accuracy 0,8725. Il resto del ragionamento (TF-IDF batte la media di circa 14 punti) non cambia.

### Notebook 14 · Il tabellone e perché vince la TF-IDF

```python
print(classification_report(y_test, pred_tfidf, target_names=["negative", "positive"], digits=4))
ConfusionMatrixDisplay.from_predictions(y_test, pred_tfidf, display_labels=["negative", "positive"])
```

Output:

```text
          representation  dimensions  test_accuracy
        TF-IDF 1-2 grams       12000         0.8725
  Mean static embeddings         100         0.7325

              precision    recall  f1-score   support
    negative     0.8706    0.8750    0.8728       200
    positive     0.8744    0.8700    0.8722       200
    accuracy                         0.8725       400
(rieseguito; matrice di confusione: 175 negativi giusti, 25 negativi dati positivi,
 26 positivi dati negativi, 174 positivi giusti)
```

TF-IDF 0,8725 contro media 0,7325: 14 punti, 56 recensioni su 400. Nel laboratorio L9 il bag of words con regressione logistica arrivava a 0,868, praticamente lo stesso: su questo compito le feature lessicali sono difficili da battere. Le ragioni proposte dal notebook:

- il sentiment dipende spesso da **indizi lessicali specifici** (*excellent, awful, waste*), che la TF-IDF tiene come feature separate;
- la media cancella ordine e interazioni locali; i bigrammi della TF-IDF ne recuperano una parte (*not good* è una feature);
- gli embedding statici non sono addestrati per il sentiment: *good* e *bad* compaiono in contesti simili e hanno vettori vicini;
- la TF-IDF conserva i termini **rari ma molto predittivi**, che nella media di 800 parole pesano 1/800.

Perché tenere comunque gli embedding: trasferiscono informazione semantica fra parole collegate (una parola mai vista nel training ma vicina a una nota contribuisce lo stesso), sono compatti e densi, e diventano molto più potenti se contestuali o adattati al compito.

Il riquadro della cella 83 risolve l'apparente contraddizione con la L11 ([scheda 6](L11-embedding-word2vec.md#p-6): i vettori densi funzionano meglio degli sparsi). Il colpevole non è la densità ma la **media**: una compressione densa a 100 dimensioni della stessa TF-IDF (SVD troncata, cioè LSA) arriva a 0,855 nella mia verifica (0,8725 se standardizzata), mentre la media perde le poche parole fortemente polari di una recensione. Anche un word2vec addestrato proprio su queste recensioni, mediato, resta basso: io ottengo 0,75-0,76 (il notebook dice "circa 0,74").

### Notebook 15 · La mappa da portarsi via

Il riepilogo finale del notebook, in otto righe da saper ripetere: **vettori da conteggi** (significato dalla co-occorrenza, sparsi e interpretabili, la PPMI doma le parole frequenti); **word2vec e GloVe** (vettori densi statici, la similarità diventa geometria; SGNS = regressione logistica su coppie vere contro finte); il **coseno** come strumento di confronto delle direzioni; le **analogie** (alcune relazioni sono direzioni, ma non è universale, e gli input vanno esclusi); la **media** per i documenti (economica e utile, ma ordine e contesto spariscono); i **bias** ereditati dai dati; il **limite statico** (un tipo, un vettore, qualunque sia il contesto); la **TF-IDF**, baseline formidabile.

Commento al notebook del corso `HLT-2026-27-L12-Word-embeddings.ipynb` (il notebook è del docente e non è incluso).

Quattro esercizi non valutati (celle 86-110), indipendenti fra loro. Ognuno ha una cella *YOUR CODE HERE* e, tranne il 3, una *check cell* che stampa se la funzione è giusta e poi la usa su dati veri: (1) la correlazione di Spearman per valutare gli embedding su WordSim-353 e SimLex-999; (2) la loss e i gradienti di SGNS, poi usati per addestrare word2vec da zero su Pinocchio; (3) battere la media degli embedding nella gara di sentiment; (4) la direzione di genere, il *neutralize* e il test *lipstick on a pig*.

Nel file salvato le celle *YOUR CODE HERE* sono già compilate da chi ha eseguito il notebook, e qui sono **corrette** (passano tutte le check cell, e le ho verificate in modo indipendente). Le soluzioni commentate, con le risposte alle domande *Discuss*, sono nella sezione *Studio ed esercizi* (esercizi 1-4). Rieseguendo, gli output coincidono con quelli salvati salvo dove intervengono gensim (non deterministico) o la TF-IDF.

### Notebook 1 · Come funzionano gli esercizi

Schema fisso: un riquadro con nome della funzione, **input**, **output**, un suggerimento e un esempio svolto con il risultato atteso; la cella `# YOUR CODE HERE` dove sostituire `return None`; la **check cell** che stampa "corretto", "qualcosa non va" (con l'input sbagliato, il valore ottenuto e quello atteso) oppure "non ancora implementato" se la funzione restituisce ancora `None`. Gli esercizi richiedono le celle precedenti (fino alla sezione 8 per l'esercizio 3). Che cosa insegnano: (1) la valutazione **intrinseca** degli embedding e la differenza fra similarità e relatedness; (2) la loss di SGNS e i suoi gradienti; (3) feature engineering su vettori densi e una sorpresa sulla regolarizzazione; (4) il debiasing per proiezione e i suoi limiti.

### Notebook 2 · Esercizio 1: la correlazione di Spearman

```python
def spearman(x, y):
    def rank(v):
        # valori minori di e, piu' la posizione media dei valori uguali a e
        return [sum(u < e for u in v) + (sum(u == e for u in v) + 1) / 2 for e in v]
    a, b = np.array(rank(x), dtype=float), np.array(rank(y), dtype=float)
    a, b = a - a.mean(), b - b.mean()
    return float((a @ b) / np.sqrt((a @ a) * (b @ b)))
```

Output:

```text
spearman agrees with scipy, ties included.
```

Come si valuta un embedding senza un compito a valle? Si fanno valutare coppie di parole a delle persone e si controlla se i coseni ordinano le coppie nello stesso modo ([schede 56-57 della L11](L11-embedding-word2vec.md#p-56), J&M §5.9). Due dataset che gensim include: **WordSim-353** (353 coppie, punteggi 0-10; agli annotatori si chiedeva la similarità, ma di fatto hanno valutato la **relatedness**: *coffee-cup* prende un voto alto) e **SimLex-999** (999 coppie, solo **similarità**: coppie correlate ma non simili, come *coffee-cup* o gli antonimi *happy-sad*, prendono voti bassi).

La metrica è la **correlazione di rango di Spearman** $\rho$: la correlazione di Pearson calcolata sui **ranghi**, con i valori pari che ricevono la media dei ranghi che occupano (`[10, 20, 20, 30]` → `[1, 2.5, 2.5, 4]`). Si usano i ranghi perché interessa solo l'**ordine**: coseni e voti umani sono su scale diverse e non c'è motivo che il legame sia lineare. La funzione del file calcola il rango di ogni valore come "quanti valori sono minori" più la posizione media del blocco dei pari, poi la Pearson sui ranghi centrati: è corretta (spiegazione e verifica nell'esercizio 1 della sezione Studio).

> **Attenzione (errore nelle slide): La check cell dell'esercizio 1 non riconosce una funzione non implementata**
>
> Nella cella 89 del file il controllo iniziale è disattivato: `if False:#spearman([1, 2, 3], [1, 2, 3]) is None:`. Con la consegna intatta (`return None`) la check cell non stampa "non ancora implementato" ma *your code raised TypeError: float() argument must be a string or a real number, not 'NoneType'*, perché `_close` prova a convertire `None` in float. Verificato eseguendo la cella con una `spearman` che restituisce `None`. Correzione: ripristinare `if spearman([1, 2, 3], [1, 2, 3]) is None:`, come nelle check cell degli esercizi 2 e 4. Con una funzione implementata la cella funziona correttamente.

### Notebook 3 · Esercizio 1: GloVe e Pinocchio contro i giudizi umani

```python
DATASETS = {"WordSim-353": read_pairs("wordsim353.tsv"), "SimLex-999": read_pairs("simlex999.txt")}
MODELS = {"GloVe 100d": emb, "Pinocchio Word2Vec": pinocchio_w2v.wv}

def evaluate_similarity(model, pairs):
    human, machine = [], []
    for w1, w2, score in pairs:
        if w1 in model and w2 in model:      # coppie con parole ignote saltate
            human.append(score); machine.append(float(model.similarity(w1, w2)))
    return spearman(human, machine), len(human)
```

Output:

```text
             model      dataset  Spearman rho  pairs covered
        GloVe 100d  WordSim-353         0.533      353 / 353
        GloVe 100d   SimLex-999         0.298      999 / 999
Pinocchio Word2Vec  WordSim-353         0.108       25 / 353
Pinocchio Word2Vec   SimLex-999         0.211      197 / 999

GloVe finds them similar, humans do not:
   accept - reject   human 0.8/10  cosine 0.82
     easy - difficult human 0.6/10 cosine 0.76
   shrink - grow     human 0.2/10  cosine 0.71
    short - long     human 1.2/10  cosine 0.82   ...
Humans find them similar, GloVe does not:
  creator - maker    human 9.6/10  cosine 0.24
    begin - originate human 8.2/10 cosine 0.23
     crib - cradle   human 8.6/10  cosine 0.27
  alcohol - gin      human 8.7/10  cosine 0.29   ...
```

GloVe: $\rho = 0{,}533$ su WordSim-353 ma solo 0,298 su SimLex-999. Le coppie su cui GloVe e gli annotatori di SimLex litigano di più spiegano perché: GloVe dà coseni alti agli **antonimi** (*accept-reject* 0,82, *short-long* 0,82, *easy-difficult* 0,76), che SimLex valuta quasi 0. Gli antonimi compaiono negli stessi contesti (*the task was easy/difficult*), quindi per un modello distribuzionale sono vicinissimi. Il coseno premia la **relatedness**, che è ciò che WordSim misura davvero. Dall'altra parte, sinonimi rari o di registro diverso (*creator-maker*, *crib-cradle*, *alcohol-gin*) hanno coseni bassi: compaiono in testi diversi, anche se significano quasi la stessa cosa.

Il modello di Pinocchio copre solo 25 coppie di WordSim e 197 di SimLex: i suoi $\rho$ **non sono confrontabili** con quelli di GloVe (coppie diverse, e su 25 coppie la stima è instabile: nelle mie esecuzioni 0,108, 0,045 e 0,065, a seconda dell'addestramento). Per avvicinarsi a SimLex: finestre più **strette** (o contesti sintattici), che premiano la similarità di tipo invece del tema (blocco sui vicini di Pinocchio); più dati; oppure correggere i vettori con risorse lessicali che marcano sinonimi e antonimi.

### Notebook 4 · Esercizio 2: la loss e i gradienti di SGNS

```python
def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))

def sgns_loss_and_gradients(w, c_pos, c_negs):
    s_pos = c_pos @ w                   # punteggio della coppia vera
    s_negs = c_negs @ w                 # k punteggi delle coppie negative
    sig_pos, sig_negs = sigmoid(s_pos), sigmoid(s_negs)
    loss = np.logaddexp(0.0, -s_pos) + np.sum(np.logaddexp(0.0, s_negs))
    grad_w = (sig_pos - 1.0) * c_pos + sig_negs @ c_negs
    grad_c_pos = (sig_pos - 1.0) * w
    grad_c_negs = sig_negs[:, None] * w[None, :]
    return loss, grad_w, grad_c_pos, grad_c_negs
```

Output:

```text
loss and gradients are right (they match the numerical derivatives).
```

La loss di una coppia positiva con le sue $k$ negative (J&M Eq. 5.21, [scheda 24 della L11](L11-embedding-word2vec.md#p-24)):
$$L = -\log\sigma(\mathbf c_{pos}\cdot\mathbf w) - \sum_{i=1}^{k}\log\sigma(-\mathbf c_{neg_i}\cdot\mathbf w)$$
Il primo termine vuole $P(+\mid w,c_{pos})$ vicina a 1, la somma vuole $P(-\mid w,c_{neg_i}) = 1-\sigma(\mathbf c_{neg_i}\cdot\mathbf w) = \sigma(-\mathbf c_{neg_i}\cdot\mathbf w)$ vicina a 1. I gradienti sono quelli delle Eq. 5.22-5.24 ([schede 27-28 della L11](L11-embedding-word2vec.md#p-27)): $[\sigma(\mathbf c_{pos}\cdot\mathbf w)-1]\,\mathbf w$, $\sigma(\mathbf c_{neg_i}\cdot\mathbf w)\,\mathbf w$ e la loro combinazione per $\mathbf w$.

La soluzione del file è vettorizzata: `c_negs @ w` calcola i $k$ prodotti scalari in un colpo; `sig_negs @ c_negs` è $\sum_i\sigma_i\,\mathbf c_{neg_i}$; `sig_negs[:, None] * w[None, :]` costruisce la matrice $k\times d$ con riga $i$ uguale a $\sigma_i\mathbf w$. Per la loss usa `np.logaddexp(0, -s)`, cioè $\log(1+e^{-s}) = -\log\sigma(s)$, numericamente stabile anche per punteggi molto negativi (dove `log(sigmoid(s))` darebbe `log(0)`). Esempio svolto: $\mathbf w = \mathbf c_{pos} = [1,0]$, $\mathbf c_{neg} = [0,1]$: $L = -\log\sigma(1)-\log\sigma(0) = 0{,}313+0{,}693 = 1{,}006$, $\nabla_{\mathbf w} = [-0{,}269;\ 0{,}5]$, $\nabla_{\mathbf c_{pos}} = [-0{,}269;\ 0]$, $\nabla_{\mathbf c_{neg}} = [0{,}5;\ 0]$.

La check cell confronta prima con l'esempio svolto (e segnala un probabile errore di segno), poi i gradienti con le **derivate numeriche** della loss stessa (differenze centrali con $\varepsilon = 10^{-6}$, vettori casuali con $d = 6$, $k = 3$): un controllo che non dipende dalla derivazione e che è buona pratica ogni volta che si scrivono gradienti a mano.

### Notebook 5 · Esercizio 2: addestrare word2vec da zero

```python
def train_sgns(sentences, dim=50, window=2, k=5, epochs=5, lr0=0.05, min_count=3, t_sub=1e-3, seed=0):
    ...
    p_neg = freq ** 0.75 / np.sum(freq ** 0.75)                      # distribuzione dei negativi
    keep = np.minimum(1.0, np.sqrt(t_sub / (freq / freq.sum())) + t_sub / (freq / freq.sum()))  # subsampling
    W = (rng.random((len(vocab), dim)) - 0.5) / dim                 # target: piccoli casuali
    Cm = np.zeros((len(vocab), dim))                                # contesti: zeri
    for epoch in range(epochs):
        lr = lr0 * (1 - epoch / epochs)
        for sent in data:
            sent = [i for i in sent if rng.random() < keep[i]]
            for pos, wi in enumerate(sent):
                for j in finestra(pos):
                    negs = prossimi k negativi
                    loss, g_w, g_pos, g_negs = sgns_loss_and_gradients(W[wi], Cm[sent[j]], Cm[negs])
                    W[wi] -= lr * g_w
                    Cm[sent[j]] -= lr * g_pos
                    np.subtract.at(Cm, negs, lr * np.asarray(g_negs))
```

Output:

```text
epoch 1/5: mean loss 3.151 on 91,784 pairs
epoch 2/5: mean loss 2.644 on 91,828 pairs
epoch 3/5: mean loss 2.589 on 91,624 pairs
epoch 4/5: mean loss 2.555 on 91,874 pairs
epoch 5/5: mean loss 2.530 on 91,658 pairs
pinocchio  yours: ['geppetto', 'marionette', 'himself', 'her', 'him', 'neck']
father     yours: ['dear', 'my', 'oh', 'friend', 'own', 'old']
fox        yours: ['cat', 'farmer', 'repeated', 'shoulders', 'turning', 'house']
school     yours: ['go', 'get', 'wanted', 'listen', 'study', 'eat']
said       yours: ['friend', 'then', 'him', 'asked', 'back', 'angrily']
cried      yours: ['lifted', 'close', 'turning', 'stood', 'tears', 'seeing']
```

Il ciclo fa, in NumPy puro, quello che gensim fa internamente: per ogni target e ogni contesto nella finestra estrae $k$ negativi, chiama la funzione dell'esercizio e fa un passo di discesa del gradiente sui tre vettori coinvolti (gli aggiornamenti delle Eq. 5.25-5.27, [scheda 29 della L11](L11-embedding-word2vec.md#p-29)). Dettagli da saper leggere: negativi estratti con $P_\alpha$, $\alpha = 0{,}75$; **subsampling** delle parole frequenti, tenute con probabilità $\min\big(1, \sqrt{t/f}+t/f\big)$ con $f$ la frequenza relativa e $t = 10^{-3}$ (la formula del codice C di word2vec: *the* e *and* vengono spesso scartate, così la finestra arriva più lontano); learning rate che decresce linearmente; `np.subtract.at` per aggiornare correttamente anche quando lo stesso negativo è estratto due volte. Questa parte è deterministica (seme fisso, un solo thread): rieseguendo ottengo esattamente gli stessi numeri e vicini.

Le domande *Discuss*:

- **Loss iniziale**: i vettori di contesto partono da zero, quindi tutti i prodotti scalari valgono 0 e $\sigma(0) = 0{,}5$: ogni coppia ha $L = (k+1)\ln 2 = 6\cdot 0{,}693 = 4{,}16$ con $k = 5$ (logaritmo naturale). La media della prima epoca è 3,15 perché la loss scende già durante l'epoca.
- **Perché poi scende poco** (2,64 → 2,53): la loss ha un pavimento alto. I negativi sono estratti a caso e a volte sono contesti veri; e soprattutto lo stesso target compare con tantissimi contesti diversi, quindi il classificatore non può dare probabilità 1 a tutti i veri e 0 a tutti i finti con vettori di 50 dimensioni. Conta che le parole si dispongano bene, non che la loss vada a zero.
- **Perché due matrici**: con $\mathbf c = \mathbf w$ il punteggio della coppia $(w,w)$ sarebbe $\mathbf w\cdot\mathbf w = \|\mathbf w\|^2 \ge 0$, sempre alto. Ma una parola compare raramente accanto a sé stessa, e quando viene estratta come negativo di sé stessa il modello dovrebbe abbassare $\|\mathbf w\|^2$, cioè accorciare il vettore: conflitto con il resto del training. Con due vettori distinti il problema sparisce.
- Con `window=5` e `k=15` (provato): le coppie raddoppiano (188 mila per epoca invece di 92 mila) e ognuna aggiorna 16 vettori di contesto invece di 6; il tempo passa da 14 a 40 secondi. I vicini diventano più tematici: *father* → *son, milk, comfort, family*; *school* → *study, succeed, promise*; *cried* → *laughing, crying, sobbing*. La loss media sale a circa 3,4, ma non è confrontabile: con $k = 15$ contiene 15 termini negativi invece di 5.

Confronto con gensim: i vicini "fatti in casa" (finestra 2) sono più sintattici (*father*: *dear, my, oh*, da *my dear father*); quelli di gensim (finestra 10) più tematici. Entrambi trovano *fox*-*cat*.

### Notebook 6 · Esercizio 3: battere la baseline

```python
IDF = {w: math.log10(len(train_tokens) / c) for w, c in _df.items()}   # idf sul solo training

def evaluate_doc_vectors(doc_vector, name, standardize=False, C=1.0):
    X_tr = np.vstack([doc_vector(t) for t in train_tokens]); X_te = ...
    if standardize:
        scaler = StandardScaler().fit(X_tr); X_tr, X_te = scaler.transform(X_tr), scaler.transform(X_te)
    clf = LogisticRegression(max_iter=5000, C=C, random_state=SEED).fit(X_tr, y_train)

# tentativo salvato nel file
STANDARDIZE = True
C = 0.1
def my_doc_vector(tokens):
    vectors = [emb[w] for w in tokens if w in emb and w not in STOPWORDS]
    if not vectors:
        return np.zeros(emb.vector_size)
    return np.mean(vectors, axis=0)
```

Output:

```text
attempt 2: mean without stopwords, standardized, C=0.1: 100 features, accuracy 0.7650

TF-IDF (Section 8)                                   0.8725   (file: 0.8650)
attempt 2: mean without stopwords, standardized...   0.7650
mean embedding (Section 8)                           0.7325
```

Obiettivo: superare 0,7325 con una rappresentazione **densa** costruita dagli embedding, scrivendo `my_doc_vector(tokens)` (un vettore di lunghezza fissa per recensione) e scegliendo se standardizzare le feature e quanto regolarizzare (`C` = inverso della forza di regolarizzazione). Non c'è check cell: l'arbitro è un tabellone. Le idee suggerite: pesare le parole per IDF (calcolata solo sul training), togliere le stopword, aggiungere statistiche oltre alla media (massimo e minimo per dimensione, concatenati), e "guardare la grandezza dei numeri" ricordando che la regressione logistica è regolarizzata.

Il tentativo salvato (media senza stopword, standardizzata, $C = 0{,}1$) arriva a 0,765. Nelle mie prove, una modifica alla volta, la sorpresa è che il guadagno viene quasi tutto da un'idea sola, la **standardizzazione**: la media semplice standardizzata dà **0,7725**, e togliere le stopword in realtà peggiora un po' (0,7675). Il perché, la tabella completa e la significatività sono nell'esercizio 3 della sezione Studio. Ultima domanda *Discuss*: una media di 100-300 numeri non può distinguere *not good* da *good* (blocco sulla media delle frasi), un vettore denso costruito da un modello che legge la frase in ordine sì: è lo scopo degli embedding contestuali.

### Notebook 7 · Esercizio 4: la direzione di genere e il neutralize

```python
GENDER_PAIRS = [("she", "he"), ("her", "his"), ("woman", "man"), ("mother", "father"),
                ("daughter", "son"), ("girl", "boy"), ("female", "male"), ("herself", "himself")]

def bias_direction(pairs):
    diffs = [emb[f] / np.linalg.norm(emb[f]) - emb[m] / np.linalg.norm(emb[m]) for f, m in pairs]
    d = np.mean(diffs, axis=0)
    return d / np.linalg.norm(d)

def neutralize(v, d):
    return v - (v @ d) * d
```

Output:

```text
cosine(bias direction, she - he) = 0.891
```

Il debiasing di Bolukbasi et al. (2016), versione minima (J&M §5.8): (1) trovare la **direzione di genere** come media delle differenze $\hat{\mathbf f}-\hat{\mathbf m}$ su otto coppie definitorie (*she/he, her/his, woman/man, ...*), con $\hat{\mathbf x} = \mathbf x/\|\mathbf x\|$ (si normalizza ogni parola prima, così le parole frequenti, con vettori più lunghi, non dominano), e normalizzarla; (2) **neutralizzare** le parole che dovrebbero essere neutre togliendo la componente lungo quella direzione:
$$\mathbf v_\perp = \mathbf v - (\mathbf v\cdot\mathbf d)\,\mathbf d,\qquad \mathbf v_\perp\cdot\mathbf d = \mathbf v\cdot\mathbf d - (\mathbf v\cdot\mathbf d)\|\mathbf d\|^2 = 0\ \text{ se } \|\mathbf d\| = 1.$$
È la proiezione ortogonale sull'iperpiano perpendicolare a $\mathbf d$; serve che $\mathbf d$ sia unitario, altrimenti si toglie la quantità sbagliata. Esempio svolto: `neutralize([3, 4], [1, 0])` = `[0, 4]`. La direzione trovata ha coseno 0,891 con $\mathbf{she}-\mathbf{he}$: le otto coppie concordano in buona parte.

La check cell verifica l'esempio, l'ortogonalità su un vettore casuale di dimensione 20, che sia tolta *solo* la componente lungo $\mathbf d$, la norma 1 e il verso (femminile meno maschile); accetta con un avviso una direzione calcolata senza normalizzare le parole (coseno almeno 0,99 con quella attesa).

> **Approfondimento: "Length 1" nella consegna vuol dire norma 1**
>
> La cella 104 descrive l'output di `bias_direction` come *a NumPy array of length 1 (a unit vector)*. La parola è ambigua: in algebra lineare la lunghezza di un vettore è la sua norma ([scheda 25 della L10](L10-semantica-vettoriale.md#p-25)), ma in NumPy è il numero di elementi (`len`): un array di lunghezza 1 avrebbe un solo numero. Quello richiesto è un array di **100** componenti (la dimensione di GloVe) con **norma** 1, $\|\mathbf d\| = 1$, come chiarisce la parentesi e come controlla la check cell (`np.linalg.norm(b_)` deve valere 1). Formulazione più chiara: *a NumPy array of the same length as the word vectors (100), with norm 1*.

### Notebook 8 · Esercizio 4: il test "lipstick on a pig"

```python
proj = similarities_to(g_dir)          # coseno di ogni parola di VOCAB_50K con la direzione di genere
order = np.argsort(proj)
male_words = [VOCAB_50K[i] for i in order[:500]]
female_words = [VOCAB_50K[i] for i in order[-500:]]
X_before = np.vstack([emb[w] for w in words])
X_after = np.vstack([neutralize(emb[w], g_dir) for w in words])
cross_val_score(KNeighborsClassifier(n_neighbors=10, metric="cosine"), X, y_bias, cv=5).mean()
```

Output:

```text
    profession  projection before (+ = female)  after neutralize
     homemaker                           0.363               0.0
          maid                           0.330               0.0
  receptionist                           0.305               0.0
         nurse                           0.304               0.0
     librarian                           0.136               0.0
       teacher                           0.055               0.0
        doctor                           0.017               0.0
     scientist                          -0.114               0.0
      engineer                          -0.219               0.0
     architect                          -0.223               0.0
       captain                          -0.288               0.0
       manager                          -0.320               0.0
          boss                          -0.341               0.0

most male-leaning:   ['caliph', 'yawar', 'arsene', 'chiefs', 'gundy', 'harun', ...]
most female-leaning: ['irina', 'rhoda', 'louisa', 'uterus', 'kristina', 'kournikova', ...]
largest |projection on the gender direction| after neutralizing: 5.1e-07
10-NN recovers the original male/female leaning before neutralizing: 100.0%  (chance: 50%)
10-NN recovers the original male/female leaning after neutralizing: 93.1%  (chance: 50%)
```

Prima del neutralize le professioni si dispongono lungo la direzione di genere come nello stereotipo: *homemaker* (+0,363), *maid*, *receptionist*, *nurse* dalla parte femminile, *engineer* (−0,219), *architect*, *captain*, *manager* fino a *boss* (−0,341) da quella maschile. Dopo, la componente è esattamente 0 (a meno degli arrotondamenti float32, $5\cdot10^{-7}$).

Il test di Gonen e Goldberg (2019), *Lipstick on a pig*: si prendono le 500 parole più "maschili" e le 500 più "femminili" del vocabolario secondo la proiezione (nomi propri, sport e califfati da una parte, nomi femminili e parole del corpo e della gravidanza dall'altra), si neutralizzano **tutte**, e si chiede a un classificatore 10-NN con distanza coseno (validazione incrociata a 5 fold) di ritrovare da che parte stava ciascuna. Prima: 100%. Dopo: **93,1%**, contro il 50% del caso.

Le risposte *Discuss*: la proiezione è zero, ma il genere non sta solo in quella direzione; è **distribuito** su molte altre dimensioni correlate, e soprattutto nella struttura dei **vicinati**: le parole "femminili" restano vicine fra loro (*irina* vicino a *kristina*, *pregnant* a *breastfeeding*), quindi un k-NN le raggruppa ancora. Il bias è una proprietà della geometria intera, non una direzione che si toglie (J&M §5.8: il debiasing riduce il bias ma non lo elimina). Per un sistema di screening dei CV gli embedding neutralizzati non sono una garanzia: un classificatore a valle può ricostruire l'informazione rimossa da altri indizi, e servono valutazioni dirette del comportamento sui gruppi (danno allocativo, [scheda 55 della L11](L11-embedding-word2vec.md#p-55)).

## Studio ed esercizi

### Guida allo studio (circa 5 h 00 min)

**Dai conteggi alla PPMI** (45 min)

Notebook parte 1, celle 3-22. Saper costruire a mano la matrice parola-contesto con finestra $\pm1$ (perché $N$ = 32 coppie da 24 token), calcolare coseni su righe di conteggi, rispondere alle quattro domande del checkpoint, calcolare PPMI di singole celle e spiegare perché *cats*-*pizza* passa da 0,667 a 0,045. Esercizi 5 e 6. Ripasso: L10 schede 18, 25-28, 48-57. Libro §5.3-5.4 e Appendice J.

**Word2vec su Pinocchio** (30 min)

Celle 23-31. Che cosa impara SGNS, le due matrici $W$ e $C$ e quale si tiene, gli iperparametri di `Word2Vec` (anche quelli di default: `negative`, `ns_exponent`, `sample`, `workers`), perché i vicini cambiano a ogni esecuzione, l'effetto della finestra (*hands* con finestra 2 e 10), perché CBOW è più veloce. Ripasso L11 schede 7, 17, 32-33, 36-37, 45. Libro §5.5.

**Embedding pre-addestrati: vicini, analogie, bias, bank** (50 min)

Celle 32-67. GloVe contro word2vec contro fasttext; vicini e corpus (*fox*); odd-one-out; il parallelogramma, l'equivalenza fra coseno e distanza euclidea per vettori unitari, perché senza esclusione vince un input (esercizio 8); leggere una PCA e i suoi limiti, t-SNE; la differenza di coseni per il bias di genere; il vettore unico di *bank* e il ponte verso gli embedding contestuali. Libro §5.5.3, §5.6-5.8; L11 schede 38-40, 44, 47-55.

**Dalla parola al documento: media contro TF-IDF** (35 min)

Celle 68-85. Perché la media dà 0,991 fra *good* e *not good*; il protocollo della gara (split stratificato, TF-IDF stimata solo sul training); le formule tf-idf del libro e di scikit-learn (esercizio 9); i numeri 0,7325 e 0,8725 (non lo 0,865 salvato); le quattro ragioni per cui vince la TF-IDF e perché non è un argomento contro la densità (LSA 0,855). Ripasso L10 schede 39-43, laboratorio L9 (bag of words 0,868).

**Esercizi 1 e 2: valutazione e SGNS da zero** (60 min)

Scrivere da soli `spearman` (con i pari) e `sgns_loss_and_gradients`, derivando i gradienti su carta, poi confrontare con le soluzioni. Saper spiegare 0,533 contro 0,298 (relatedness contro similarità, antonimi), la loss iniziale $6\ln2$, il controllo con le derivate numeriche, il ciclo di training (subsampling, $P_\alpha$, learning rate decrescente). Esercizio 7 a mano. Libro §5.5.2 (Eq. 5.21-5.27) e §5.9; L11 schede 24-31, 56-57.

**Esercizi 3 e 4: regolarizzazione e debiasing** (50 min)

Provare almeno tre varianti di `my_doc_vector` e capire perché la standardizzazione da sola porta a 0,7725 (deviazione standard 0,038 delle feature, penalità L2), con il paired bootstrap ($p \approx 0{,}028$). Scrivere `bias_direction` e `neutralize`, verificare l'ortogonalità, interpretare il 93,1% del test di Gonen e Goldberg. Ripasso L6 scheda 31, L7 schede 47 e 56, L11 schede 53-55; libro §5.8.

**Ripasso orale** (30 min)

Rispondere ad alta voce alle domande della sezione orale senza guardare la traccia, citando almeno un numero del laboratorio per risposta (0,707 di *pizza-cheese*, 0,045, $6\ln2 = 4{,}16$, 0,533/0,298, 0,991, 0,7325/0,7725/0,8725, 93,1%).

### Esercizi

#### Esercizio 1 (notebook L12): Spearman, embedding contro giudizi umani

Scrivi `spearman(x, y)` senza `scipy`: due liste di numeri della stessa lunghezza $n \ge 2$; sostituisci ogni valore con il suo **rango** (1 = il più piccolo, i valori pari ricevono la media dei ranghi che occupano: `[10, 20, 20, 30]` → `[1, 2.5, 2.5, 4]`) e restituisci la correlazione di Pearson dei due vettori di ranghi. Controlli: `spearman([1,2,3,4],[10,20,30,40])` = 1, con `[40,30,20,10]` = −1, `spearman([1,2,3,4,5],[5,6,7,8,7])` = 0,8208. Poi rispondi: perché GloVe concorda di più con WordSim-353 che con SimLex-999? Il $\rho$ del modello di Pinocchio è confrontabile con quello di GloVe? Come cambieresti l'addestramento per avvicinarti a SimLex?

<details><summary>Soluzione</summary>

```
def spearman(x, y):
    # Input: two lists of numbers of the same length.
    # Output: Spearman's rank correlation (a float). Ties get the average of their ranks.
    def rank(v):
        # values smaller than e, plus the average position of the values equal to e
        return [sum(u < e for u in v) + (sum(u == e for u in v) + 1) / 2 for e in v]
    a, b = np.array(rank(x), dtype=float), np.array(rank(y), dtype=float)
    a, b = a - a.mean(), b - b.mean()
    return float((a @ b) / np.sqrt((a @ a) * (b @ b)))
```

È la soluzione presente nel file, ed è corretta (passa la check cell, che la confronta anche con `scipy.stats.spearmanr` su dati casuali pieni di pari). Il rango: se $m$ valori sono minori di $e$ e $q$ sono uguali (lui compreso), il blocco dei pari occupa le posizioni $m+1,\dots,m+q$, la cui media è $m + (q+1)/2$. Poi Pearson sui ranghi centrati. Costo $O(n^2)$, irrilevante per 999 coppie.

Verifica a mano dell'esempio: ranghi $a = [1,2,3,4,5]$, $b = [1,2,3{,}5,5,3{,}5]$ (i due 7 occupano le posizioni 3 e 4). Centrati (medie 3 e 3): $[-2,-1,0,1,2]$ e $[-2,-1,0{,}5,2,0{,}5]$. $\sum a_ib_i = 4+1+0+2+1 = 8$, $\sum a_i^2 = 10$, $\sum b_i^2 = 9{,}5$: $\rho = 8/\sqrt{95} = 0{,}8208$. Nota: la formula scorciatoia $1-\frac{6\sum d_i^2}{n(n^2-1)}$ vale solo **senza pari**: qui $d = [0,0,-0{,}5,-1,1{,}5]$, $\sum d^2 = 3{,}5$, dà $1-21/120 = 0{,}825$, sbagliato. Il Pearson sui valori (0,832) è un altro errore tipico, che la check cell riconosce.

Risultati: GloVe 0,533 su WordSim-353, 0,298 su SimLex-999; Pinocchio 0,108 (25 coppie) e 0,211 (197 coppie). Risposte:

- Il coseno di un modello distribuzionale misura la **relatedness**: antonimi e parole dello stesso tema compaiono negli stessi contesti (*accept-reject* 0,82, *short-long* 0,82, che SimLex valuta circa 1/10). WordSim, pur chiedendo la similarità, ha raccolto giudizi di relatedness; SimLex no. Per lo stesso motivo sinonimi di registro diverso (*creator-maker* 0,24) restano lontani.
- No: Pinocchio copre poche coppie, diverse da quelle di GloVe e probabilmente più facili (parole frequenti); su 25 coppie $\rho$ oscilla molto fra un addestramento e l'altro (0,045-0,108 nelle mie esecuzioni). Il confronto corretto si fa sulle stesse coppie.
- Finestre strette o contesti sintattici (similarità di tipo più che di tema), più dati, oppure correggere i vettori con un lessico di sinonimi e antonimi.

</details>

#### Esercizio 2 (notebook L12): la loss e i gradienti di SGNS da zero

Scrivi `sgns_loss_and_gradients(w, c_pos, c_negs)`: `w` e `c_pos` di forma `(d,)`, `c_negs` di forma `(k, d)`; restituisci `(loss, grad_w, grad_c_pos, grad_c_negs)` con
$$L = -\log\sigma(\mathbf c_{pos}\cdot\mathbf w) - \sum_{i=1}^{k}\log\sigma(-\mathbf c_{neg_i}\cdot\mathbf w)$$
e i gradienti delle stesse forme degli input. Ricava i gradienti su carta usando $\frac{d}{dz}\log\sigma(z) = 1-\sigma(z)$. Esempio: `w = [1, 0]`, `c_pos = [1, 0]`, `c_negs = [[0, 1]]` → loss 1,006, `grad_w = [-0.269, 0.5]`, `grad_c_pos = [-0.269, 0]`, `grad_c_negs = [[0.5, 0]]`. Scommessa: con tutti i vettori di contesto a zero, quanto vale la loss di ogni coppia con $k = 5$?

<details><summary>Soluzione</summary>

**Derivazione.** Chiamo $s_+ = \mathbf c_{pos}\cdot\mathbf w$ e $s_i = \mathbf c_{neg_i}\cdot\mathbf w$. Primo termine: $\frac{\partial}{\partial s_+}[-\log\sigma(s_+)] = -(1-\sigma(s_+)) = \sigma(s_+)-1$. Termini negativi: $\frac{\partial}{\partial s_i}[-\log\sigma(-s_i)] = -(1-\sigma(-s_i))\cdot(-1) = 1-\sigma(-s_i) = \sigma(s_i)$. Regola della catena con $\partial s_+/\partial\mathbf c_{pos} = \mathbf w$, $\partial s_+/\partial\mathbf w = \mathbf c_{pos}$ e lo stesso per i negativi:
$$\frac{\partial L}{\partial\mathbf c_{pos}} = [\sigma(s_+)-1]\,\mathbf w\qquad \frac{\partial L}{\partial\mathbf c_{neg_i}} = \sigma(s_i)\,\mathbf w\qquad \frac{\partial L}{\partial\mathbf w} = [\sigma(s_+)-1]\,\mathbf c_{pos}+\sum_i\sigma(s_i)\,\mathbf c_{neg_i}$$
cioè J&M Eq. 5.22-5.24: (previsto − vero) × input, come nella regressione logistica della L6.

```
def sgns_loss_and_gradients(w, c_pos, c_negs):
    s_pos = c_pos @ w                       # score of the true pair
    s_negs = c_negs @ w                     # k scores, shape (k,)
    sig_pos, sig_negs = sigmoid(s_pos), sigmoid(s_negs)
    # -log sigma(s) = log(1 + exp(-s)) and -log sigma(-s) = log(1 + exp(s)), stable via logaddexp
    loss = np.logaddexp(0.0, -s_pos) + np.sum(np.logaddexp(0.0, s_negs))
    grad_w = (sig_pos - 1.0) * c_pos + sig_negs @ c_negs
    grad_c_pos = (sig_pos - 1.0) * w
    grad_c_negs = sig_negs[:, None] * w[None, :]   # row i = sigma(s_i) * w
    return loss, grad_w, grad_c_pos, grad_c_negs
```

Esempio svolto: $s_+ = 1$, $s_1 = 0$. $L = \ln(1+e^{-1}) + \ln 2 = 0{,}3133+0{,}6931 = 1{,}0064$. $\sigma(1)-1 = -0{,}2689$, $\sigma(0) = 0{,}5$: $\nabla_{\mathbf w} = -0{,}2689\,[1,0] + 0{,}5\,[0,1] = [-0{,}269;\ 0{,}5]$; $\nabla_{\mathbf c_{pos}} = -0{,}2689\,[1,0]$; $\nabla_{\mathbf c_{neg}} = 0{,}5\,[1,0]$. La check cell passa, gradienti uguali alle derivate numeriche.

**Scommessa**: con $\mathbf c = \mathbf 0$ tutti i punteggi sono 0 e $L = (k+1)\ln 2 = 6 \cdot 0{,}693 = 4{,}159$. Nel training da zero la media della prima epoca è 3,151 e poi la loss si ferma intorno a 2,53: pavimento alto perché lo stesso target ha moltissimi contesti diversi e i negativi casuali a volte sono contesti veri. Perché due matrici: con $\mathbf c = \mathbf w$ la coppia $(w,w)$ avrebbe punteggio $\|\mathbf w\|^2 \ge 0$, ma una parola quasi mai compare accanto a sé stessa, quindi il training dovrebbe accorciare il vettore, in conflitto con tutto il resto.

</details>

#### Esercizio 3 (notebook L12): battere la media degli embedding

Nella gara di sentiment la media dei vettori GloVe ottiene 0,7325 (TF-IDF 0,8725). Scrivi `my_doc_vector(tokens)` (input: le parole minuscole di una recensione; output: un vettore NumPy di lunghezza fissa) e scegli `STANDARDIZE` e `C` per superare 0,7325 con una rappresentazione **densa**. Prova un'idea alla volta: pesi IDF, togliere le stopword, media + massimo + minimo concatenati, standardizzazione, regolarizzazione. Poi: quale cambiamento aiuta di più e perché (guarda `np.abs(X_train_emb).mean()`)? Il miglioramento è significativo su 400 recensioni?

<details><summary>Soluzione</summary>

Una soluzione semplice, che è anche la migliore che ho trovato:

```
STANDARDIZE = True
C = 1.0
def my_doc_vector(tokens):
    vectors = [emb[w] for w in tokens if w in emb]
    if not vectors:
        return np.zeros(emb.vector_size)
    return np.mean(vectors, axis=0)
# mean, standardized, C=1: 100 features, accuracy 0.7725
```

Cioè: la **stessa media** della sezione 8, con le feature standardizzate. Le prove, una modifica alla volta (tutte rieseguite, regressione logistica deterministica):

| rappresentazione | standardizzata | C | feature | accuracy |
| --- | --- | --- | --- | --- |
| media (sezione 8) | no | 1 | 100 | 0,7325 |
| media | sì | 1 | 100 | **0,7725** |
| media | sì | 0,1 | 100 | 0,7725 |
| media | no | 100 | 100 | 0,7700 |
| media senza stopword | no | 1 | 100 | 0,7250 |
| media senza stopword | sì | 1 | 100 | 0,7675 |
| media senza stopword (tentativo del file) | sì | 0,1 | 100 | 0,7650 |
| media pesata per IDF | no | 1 | 100 | 0,7350 |
| media pesata per IDF | sì | 1 | 100 | 0,7450 |
| media + max + min, senza stopword | sì | 0,1 | 300 | 0,7625 |

**Perché la standardizzazione** (la "sorpresa sulla regolarizzazione"): la media di circa 800 vettori è molto simile da una recensione all'altra. Il valore assoluto medio delle feature è 0,22, ma la loro **deviazione standard** fra recensioni è in media solo 0,038. Per sfruttare differenze così piccole la regressione logistica ha bisogno di pesi grandi (dell'ordine di $1/0{,}038 \approx 26$ volte quelli che servirebbero su feature di varianza 1), e la penalità L2 di default ($C = 1$, [scheda 56 della L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-56)) li schiaccia: il modello è troppo regolarizzato. Due rimedi equivalenti: standardizzare (z-score, [scheda 31 della L6](L06-regressione-logistica.md#p-31)), così ogni feature ha varianza 1, oppure alzare $C$ (con $C = 100$ senza standardizzare: 0,770). Le stopword e l'IDF, invece, aiutano poco o niente: i pesi IDF rendono la media più rumorosa (domina qualche parola rara), e le stopword contengono indizi utili (*not*, *no*, *but*, *too* sono nella lista di NLTK).

**Significatività**: fra la media (0,7325) e la media standardizzata (0,7725) ci sono 64 recensioni su cui i due modelli discordano: 40 giuste solo per la seconda, 24 solo per la prima. Il paired bootstrap del laboratorio L9 ([scheda 47 della L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-47); $10^4$ campioni, conto dei campioni con $\delta(x^{(i)}) \ge 2\delta(x)$, $\delta = 0{,}04$) dà $p \approx 0{,}028$: significativo al 5%, anche se non di molto. Una recensione vale 0,25 punti, quindi differenze di uno o due punti fra le varianti della tabella non sono distinguibili dal caso. Il divario con la TF-IDF (10 punti) resta: una media non vede *not good*, una feature bigramma sì.

</details>

#### Esercizio 4 (notebook L12): la direzione di genere e il neutralize

Scrivi `bias_direction(pairs)`: dalle coppie `(parola_femminile, parola_maschile)` di `GENDER_PAIRS` restituisci il vettore unitario $\mathbf d$ = media delle differenze $\hat{\mathbf f}-\hat{\mathbf m}$ dei vettori GloVe **normalizzati**, divisa per la sua norma. Scrivi `neutralize(v, d)`: $\mathbf v - (\mathbf v\cdot\mathbf d)\,\mathbf d$. Controlli: `neutralize([3, 4], [1, 0])` = `[0, 4]`; $\mathbf d$ ha norma 1 e coseno circa 0,89 con $\mathbf{she}-\mathbf{he}$. Poi interpreta il test *lipstick on a pig*: perché un 10-NN ritrova ancora l'orientamento di genere delle parole dopo il neutralize?

<details><summary>Soluzione</summary>

```
def bias_direction(pairs):
    diffs = [emb[f] / np.linalg.norm(emb[f]) - emb[m] / np.linalg.norm(emb[m]) for f, m in pairs]
    d = np.mean(diffs, axis=0)
    return d / np.linalg.norm(d)

def neutralize(v, d):
    return v - (v @ d) * d
```

(La soluzione del file, corretta.) $\mathbf v\cdot\mathbf d$ è la componente di $\mathbf v$ lungo $\mathbf d$ (perché $\|\mathbf d\| = 1$); togliendo $(\mathbf v\cdot\mathbf d)\,\mathbf d$ resta la proiezione sull'iperpiano ortogonale: $(\mathbf v - (\mathbf v\cdot\mathbf d)\mathbf d)\cdot\mathbf d = \mathbf v\cdot\mathbf d - \mathbf v\cdot\mathbf d = 0$. Esempio: $[3,4]\cdot[1,0] = 3$, $[3,4]-3\,[1,0] = [0,4]$. Normalizzare le parole prima della differenza evita che le coppie con vettori lunghi (parole frequenti come *he*, *his*) pesino di più. Risultato: coseno 0,891 con $\mathbf{she}-\mathbf{he}$; le professioni vanno da +0,363 (*homemaker*) a −0,341 (*boss*) e dopo il neutralize hanno tutte componente 0.

Il test: 500 parole più maschili e 500 più femminili di VOCAB\_50K, tutte neutralizzate; un 10-NN con coseno (5 fold) ritrova l'etichetta nel 100% dei casi prima e nel **93,1%** dopo (caso: 50%). Spiegazione: il neutralize toglie **una** direzione, ma l'informazione di genere è distribuita su molte dimensioni correlate e soprattutto nei **vicinati**: le parole che erano femminili restano vicine fra loro (nomi femminili fra nomi femminili, parole della gravidanza fra loro), e un k-NN usa proprio i vicinati. Il bias è una proprietà della geometria intera, non una direzione (Gonen e Goldberg, 2019; J&M §5.8: il debiasing riduce, non elimina). Per uno screening dei CV non basta: va valutato il comportamento del sistema finale sui gruppi.

</details>

#### Esercizio 5: il checkpoint del corpus giocattolo

Corpus delle otto frasi (*cats chase mice, dogs chase balls, cats like milk, dogs like bones, pizza tastes good, pasta tastes good, pizza uses cheese, pasta uses cheese*), finestra $\pm 1$, conteggi grezzi. (a) Scrivi le righe di *cats*, *pizza*, *cheese* e calcola $\cos(\textit{pizza},\textit{cheese})$. (b) Aggiungi *Gigi hates pizza*: quanto vale $\cos(\textit{pizza},\textit{pasta})$? (c) Quale frase lo riporta a 1? (d) Aggiungi invece al corpus originale *cats tastes good*: quanto valgono $\cos(\textit{cats},\textit{pizza})$ e $\cos(\textit{cats},\textit{dogs})$?

<details><summary>Soluzione</summary>

(a) Ogni nome sta al bordo della frase, quindi vede solo la parola centrale. *cats* = {*chase*: 1, *like*: 1}; *pizza* = {*tastes*: 1, *uses*: 1}; *cheese* = {*uses*: 2} (compare in *pizza uses cheese* e *pasta uses cheese*, e in entrambe il suo unico vicino è *uses*). $\cos(\textit{pizza},\textit{cheese}) = \frac{1\cdot 2}{\sqrt2\cdot 2} = \frac{1}{\sqrt2} = 0{,}707$, come nell'output del notebook: il coseno non dipende dalla lunghezza, il 2 si semplifica.

(b) *pizza* diventa {*tastes*: 1, *uses*: 1, *hates*: 1}, *pasta* resta {*tastes*: 1, *uses*: 1}. $\cos = \frac{2}{\sqrt3\sqrt2} = 0{,}816$.

(c) *Gigi hates pasta*: le due righe tornano identiche, coseno 1. (Qualunque frase che dia a *pasta* gli stessi contesti aggiunti a *pizza*.)

(d) *cats* = {*chase*: 1, *like*: 1, *tastes*: 1}. Con *pizza*: prodotto scalare 1, $\cos = \frac{1}{\sqrt3\sqrt2} = 0{,}408$. Con *dogs* = {*chase*: 1, *like*: 1}: $\frac{2}{\sqrt3\sqrt2} = 0{,}816$. Una frase sola avvicina *cats* a *pizza* e lo allontana da *dogs*. Verificato in Python ricostruendo la matrice con `build_cooccurrence`.

</details>

#### Esercizio 6: PPMI a mano nel mondo del "the"

Nel corpus con *the* (*the cats chase the mice, the dogs chase the balls, the cats like the milk, the dogs like the bones, the pizza tastes good, the pasta tastes good, the pizza uses the cheese, the pasta uses the cheese*), finestra $\pm 1$, si sa che: $N = 60$ coppie; la riga di *cats* è {*chase*: 1, *like*: 1, *the*: 2} (somma 4); la colonna *the* somma 20; le colonne *chase* e *like* sommano 4; la riga *mice* è {*the*: 1}; la riga *good* è {*tastes*: 2}, la colonna *tastes* somma 4. (a) Calcola PPMI(*cats*, *the*), PPMI(*cats*, *chase*), PPMI(*mice*, *the*), PPMI(*good*, *tastes*). (b) La riga PPMI di *pizza* ha gli stessi valori di quella di *cats* su *tastes*, *uses*, *the*. Calcola $\cos(\textit{cats},\textit{pizza})$ sui conteggi grezzi e sulla PPMI.

<details><summary>Soluzione</summary>

(a) Con $\text{PMI} = \log_2\frac{C(w,c)\,N}{\text{riga}_w\,\text{colonna}_c}$:

- (*cats*, *the*): $\log_2\frac{2\cdot60}{4\cdot20} = \log_2 1{,}5 = 0{,}585$;
- (*cats*, *chase*): $\log_2\frac{1\cdot60}{4\cdot4} = \log_2 3{,}75 = 1{,}907$;
- (*mice*, *the*): $\log_2\frac{1\cdot60}{1\cdot20} = \log_2 3 = 1{,}585$;
- (*good*, *tastes*): $\log_2\frac{2\cdot60}{2\cdot4} = \log_2 15 = 3{,}907$.

Tutte positive, quindi PPMI = PMI. Sono i valori della heatmap (0,6; 1,9; 1,6; 3,9). *the* pesa poco per *cats* perché *the* sta accanto a tutto (colonna 20 su 60); pesa di più per *mice* perché *mice* ha una sola coppia.

(b) Grezzi: *cats* = (chase 1, like 1, the 2), *pizza* = (tastes 1, uses 1, the 2); prodotto scalare $2\cdot2 = 4$, norme $\sqrt{1+1+4} = \sqrt6$: $\cos = 4/6 = 0{,}667$. PPMI: *cats* = (1,907; 1,907; 0,585), *pizza* = (1,907; 1,907; 0,585) su dimensioni diverse tranne *the*; prodotto scalare $0{,}585^2 = 0{,}342$, norma al quadrato $2\cdot1{,}907^2+0{,}585^2 = 7{,}616$: $\cos = 0{,}342/7{,}616 = 0{,}045$. Coincide con la tabella del notebook (0,667 e 0,045). La PPMI ha ridotto il peso del contesto comune e poco informativo.

</details>

#### Esercizio 7: un passo di SGD per SGNS

Riprendi l'esempio dell'esercizio 2: $\mathbf w = [1,0]$, $\mathbf c_{pos} = [1,0]$, un solo negativo $\mathbf c_{neg} = [0,1]$, quindi loss 1,006 e gradienti $\nabla_{\mathbf w} = [-0{,}269;\ 0{,}5]$, $\nabla_{\mathbf c_{pos}} = [-0{,}269;\ 0]$, $\nabla_{\mathbf c_{neg}} = [0{,}5;\ 0]$. Fai un passo di discesa del gradiente con $\eta = 1$, aggiornando i tre vettori **con i gradienti calcolati sui valori vecchi** (come il ciclo del notebook e le Eq. 5.25-5.27). Calcola i nuovi prodotti scalari $\mathbf c_{pos}\cdot\mathbf w$ e $\mathbf c_{neg}\cdot\mathbf w$ e la nuova loss. Che cosa è successo geometricamente?

<details><summary>Soluzione</summary>

- $\mathbf w' = [1,0] - [-0{,}269;\ 0{,}5] = [1{,}269;\ -0{,}5]$
- $\mathbf c_{pos}' = [1,0] - [-0{,}269;\ 0] = [1{,}269;\ 0]$
- $\mathbf c_{neg}' = [0,1] - [0{,}5;\ 0] = [-0{,}5;\ 1]$

Nuovi punteggi: $\mathbf c_{pos}'\cdot\mathbf w' = 1{,}269^2 = 1{,}610$ (era 1); $\mathbf c_{neg}'\cdot\mathbf w' = -0{,}5\cdot1{,}269 + 1\cdot(-0{,}5) = -1{,}134$ (era 0). Nuova loss: $-\log\sigma(1{,}610) - \log\sigma(1{,}134) = 0{,}182 + 0{,}279 = 0{,}461$, da 1,006.

Geometricamente: $\mathbf w$ si è allungato verso $\mathbf c_{pos}$ e ha preso una componente negativa lungo la direzione di $\mathbf c_{neg}$; $\mathbf c_{pos}$ si è allungato verso $\mathbf w$; $\mathbf c_{neg}$ si è spostato in direzione opposta a $\mathbf w$. Il positivo si avvicina, il negativo si allontana: la Fig. 5.7 del libro. Con $\eta = 0{,}5$ la loss scende a 0,705. Verificato in NumPy con la funzione dell'esercizio 2.

</details>

#### Esercizio 8: il parallelogramma e la regola di esclusione

Vettori giocattolo in 2D: $\mathbf{man} = (3,0)$, $\mathbf{king} = (3,1)$, $\mathbf{woman} = (1,3)$, $\mathbf{queen} = (2;\ 4{,}5)$. Risolvi *man : king :: woman : ?* con il metodo del parallelogramma. (a) Calcola il vettore obiettivo. (b) Calcola distanza euclidea e coseno di ciascuna delle quattro parole dall'obiettivo. (c) Chi vince senza escludere gli input, e chi escludendoli? (d) Perché senza esclusione vince quella parola, in generale?

<details><summary>Soluzione</summary>

(a) $\mathbf t = \mathbf{king}-\mathbf{man}+\mathbf{woman} = (3,1)-(3,0)+(1,3) = (1,4)$, norma $\sqrt{17} = 4{,}123$.

(b)

| parola | distanza da $\mathbf t$ | coseno con $\mathbf t$ |
| --- | --- | --- |
| man (3, 0) | $\sqrt{4+16} = 4{,}472$ | $3/(3\cdot4{,}123) = 0{,}243$ |
| king (3, 1) | $\sqrt{4+9} = 3{,}606$ | $7/(3{,}162\cdot4{,}123) = 0{,}537$ |
| woman (1, 3) | $\sqrt{0+1} = 1{,}000$ | $13/(3{,}162\cdot4{,}123) = 0{,}997$ |
| queen (2; 4,5) | $\sqrt{1+0{,}25} = 1{,}118$ | $20/(4{,}924\cdot4{,}123) = 0{,}985$ |

(c) Senza esclusione vince *woman* con entrambe le misure; escludendo $a$, $b$, $c$ vince *queen*.

(d) La distanza di $\mathbf t$ da $\mathbf c$ è esattamente $\|\mathbf b-\mathbf a\|$ (qui 1): se lo spostamento della relazione è piccolo rispetto alle distanze fra parole diverse, l'input $c$ è quasi sempre il punto più vicino. Nel notebook succede con GloVe: senza esclusione escono *king*, *bad*, *child*, *swim*. Per questo la regola di esclusione (J&M §5.7, [scheda 50 della L11](L11-embedding-word2vec.md#p-50)) è parte integrante del metodo e va dichiarata quando si riportano i risultati.

</details>

#### Esercizio 9: tf-idf del libro e di scikit-learn

Training di $N = 1600$ recensioni. Un termine $t$ compare 10 volte nella recensione $d$ e in 16 recensioni in tutto. (a) Calcola il tf-idf con le formule del libro (L10: $\text{tf} = 1+\log_{10}\text{count}$, $\text{idf} = \log_{10}(N/\text{df})$). (b) Calcola il valore che `TfidfVectorizer(sublinear_tf=True)` assegna prima della normalizzazione L2 ($\text{tf} = 1+\ln\text{count}$, $\text{idf} = \ln\frac{1+N}{1+\text{df}}+1$). (c) Quanto vale l'idf di un termine presente in tutte le 1.600 recensioni con le due formule? (d) Perché la differenza di scala fra (a) e (b) non conta per il classificatore?

<details><summary>Soluzione</summary>

(a) $\text{tf} = 1+\log_{10}10 = 2$; $\text{idf} = \log_{10}(1600/16) = \log_{10}100 = 2$; tf-idf $= 4$.

(b) $\text{tf} = 1+\ln 10 = 3{,}303$; $\text{idf} = \ln\frac{1601}{17}+1 = \ln 94{,}18 + 1 = 4{,}545+1 = 5{,}545$; prodotto $18{,}31$.

(c) Libro: $\log_{10}(1600/1600) = 0$, il termine sparisce. scikit-learn: $\ln\frac{1601}{1601}+1 = 1$, il termine resta con peso minimo (il "+1" evita di azzerarlo del tutto; lo smoothing "+1" su numeratore e denominatore è come aggiungere un documento che contiene tutti i termini, ed evita divisioni per zero).

(d) Cambiare base del logaritmo moltiplica tutti gli idf (e i tf meno 1) per costanti; inoltre scikit-learn divide ogni vettore documento per la sua norma L2, quindi conta solo la **direzione** del vettore, come nel coseno. Le differenze reali sono lo smoothing e il "+1", che cambiano i pesi relativi dei termini comunissimi, non la scala globale. Verificato in Python.

</details>

### Domande tipo orale

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
