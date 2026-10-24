# L9 · Laboratorio: NLTK e spaCy

*NLTK and spaCy: from raw text to tags, entities and sentiment* · 07/10/2026 · Andrea Ceni · lettura: J&M cap. 2 (§2.5 corpora, §2.8 tokenizzazione a regole e segmentazione in frasi); cap. 4 (§4.3.1 e Fig. 4.2, §4.9-4.11, Fig. 4.11 ed Eq. 4.48, §4.13); cap. 18 (§18.1-18.3, Fig. 18.4, §18.6); facoltativi: cap. 19-20 (parsing), cap. 23 (lessici per il sentiment)

[Versione interattiva sul sito](https://gabriele-marsili.github.io/appunti-magistrale-ai/anno-2/hlt/sito/#L9) · [Indice della dispensa](README.md)

Laboratorio (solo notebook, nessuna slide) sulle due librerie Python classiche per l'NLP. Con **NLTK**, su *Pinocchio* scaricato da Project Gutenberg: segmentazione e tokenizzazione Penn Treebank, frequenze, concordanze, stopword, **collocazioni con la PMI**, PoS tagging, stemming e lemmatizzazione, **bag of words** e n-grammi. Poi il sentiment con **VADER** (lessico + regole) e con un transformer pre-addestrato, e la pipeline di **spaCy** (lemmi, PoS, dipendenze, noun chunk, NER). Gli esercizi riprendono L6-L8 su dati veri: ambiguità dei tag e baseline most-frequent-tag sul Penn Treebank, valutazione della NER sugli span, Dante fuori dominio, quattro classificatori di sentiment confrontati con precision, recall, F1 e paired bootstrap.

Tutto rieseguito (gli output si riproducono con NLTK 3.9.x). Errori trovati: le percentuali di VADER e la "probabilità" $(\text{compound}+1)/2$ interpretate male nel markdown, una check cell (A2) che accetta una funzione sbagliata con output salvato sbagliato, Dante attribuito al 56% di accuratezza.

## Indice

- [Notebook](#notebook)
- [Studio ed esercizi](#studio-ed-esercizi)

## Notebook

Commento al notebook del corso `HLT-2026-27-L09-NLTK_and_SpaCy.ipynb` (il notebook è del docente e non è incluso).

Prima parte guidata del laboratorio (celle 0-89): con **NLTK** si parte da un libro vero, *Le avventure di Pinocchio* in inglese scaricato da Project Gutenberg, e si ripassano in pratica gli strumenti delle lezioni L2-L4 e L8: segmentazione in frasi e tokenizzazione Penn Treebank, frequenze (`FreqDist`), concordanze, stopword, **collocazioni con la PMI**, dispersion plot, PoS tagging, stemming e lemmatizzazione, **bag of words**, n-grammi di parole e di caratteri.

Ho rieseguito tutte le celle (Python 3.13). Gli output salvati si riproducono **esattamente con NLTK 3.9.x** (3.9.1 e 3.9.2 provati); con NLTK 3.10.3, l'ultima versione, la segmentazione in frasi cambia e quindi cambiano molti conteggi (vedi il blocco sulla tokenizzazione). Le figure sono quelle degli output salvati.

### Notebook 1 · Un libro vero da Project Gutenberg

```python
import requests
url_pinocchio = "https://www.gutenberg.org/files/500/500-0.txt"
text = requests.get(url_pinocchio).content.decode()
text[:500]          # a single huge string: only the beginning
print(text)
```

Output:

```text
'\ufeffThe Project Gutenberg EBook of The Adventures of Pinocchio, by\r\nC. Collodi--Pseudonym of Carlo Lorenzini\r\n\r\nThis eBook is for the use of anyone anywhere at no cost and with\r\nalmost no restrictions whatsoever. ...'
```

Il corpus è **una sola stringa** di 239.501 caratteri: il testo di Pinocchio (traduzione di Carol Della Chiesa) *più* l'intestazione e, in fondo, la lunga licenza di Project Gutenberg. Tre dettagli che torneranno: il file inizia con il **BOM** `﻿` (il carattere U+FEFF che alcuni editor mettono in testa ai file UTF-8, [scheda 22 della L2](L02-parole-e-token.md#p-22)), le righe finiscono con `\r\n` (convenzione Windows), e i dialoghi usano le virgolette tipografiche “ ” e l'apostrofo ’, non i caratteri ASCII.

Nessuna pulizia viene fatta: il testo fra `*** START OF THIS PROJECT GUTENBERG EBOOK` e `*** END` è il libro, il resto (circa 3.400 token su 53.332) è licenza in inglese legale. È esattamente il problema del **datasheet** di un corpus ([scheda 46](L02-parole-e-token.md#p-46) e [scheda 48 della L2](L02-parole-e-token.md#p-48)): sapere che cosa c'è davvero dentro prima di contare. Le collocazioni più avanti lo mostrano in modo spettacolare.

### Notebook 2 · Frasi e parole: sent_tokenize e word_tokenize

```python
import nltk
nltk.download('punkt_tab')
sentences = nltk.sent_tokenize(text)          # Punkt
sentences[42]

tokenized_text = nltk.word_tokenize(text)     # Penn Treebank conventions
tokenized_text[1000:1010]

tokenized_sentences = [nltk.word_tokenize(s) for s in nltk.sent_tokenize(text)]
tokenized_sentences[42]
```

Output:

```text
'Oh, stop it!'
['the', 'piece', 'of', 'wood', 'to', 'his', 'friend', 'Geppetto', ',', 'who']
['Oh', ',', 'stop', 'it', '!']
```

**Punkt** è il segmentatore in frasi di NLTK: un modello *non supervisionato* (Kiss e Strunk, 2006) che impara da testo grezzo quali parole seguite da punto sono abbreviazioni (*Mr.*, *Dr.*), sigle o iniziali, e quindi dove un punto chiude davvero una frase. È il problema della [scheda 32 della L3](L03-elaborazione-del-testo.md#p-32): il punto è ambiguo fra fine frase e abbreviazione.

`word_tokenize` prima divide in frasi con Punkt e poi applica a ogni frase il tokenizzatore a regex con le convenzioni **Penn Treebank** ([scheda 30](L03-elaborazione-del-testo.md#p-30) e [scheda 31 della L3](L03-elaborazione-del-testo.md#p-31)): la punteggiatura diventa un token, i clitici si staccano (`I``’ll`, `don``’``t` con l'apostrofo tipografico, che le regex PTB non riconoscono come apostrofo inglese). Il risultato è una lista di 53.332 token.

Il punto chiave per tutto il notebook: **quasi ogni funzione NLTK lavora su liste di token**, non su stringhe. Per questo si tokenizza sempre per primo.

> **Approfondimento: Stesso codice, conteggi diversi: NLTK 3.9 contro 3.10**
>
> Ho rieseguito la cella con l'ultima versione (NLTK 3.10.3) e con la 3.9.2: solo la seconda riproduce gli output salvati.
>
> |  | NLTK 3.9.2 (output del notebook) | NLTK 3.10.3 |
> | --- | --- | --- |
> | frasi | 2.298 | 3.410 |
> | token | 53.332 | 53.814 |
> | token `.` | 1.840 | 2.322 |
> | `sentences[42]` | Oh, stop it! | He listened for the tiny voice to moan and cry. |
>
> Il motivo: con la 3.9 Punkt **non spezza** dopo `!”` seguito da un a capo, e unisce paragrafi diversi in una sola "frase" (*I’ll fix him!”\r\n\r\nWith these words, ...*). Poiché il tokenizzatore PTB stacca solo il punto **finale** della frase, i punti rimasti in mezzo restano attaccati alla parola: nell'output della 3.9 ci sono 443 token come `it.`, `you.`, `me.`. Per questo `Pinocchio` conta 451 con la 3.9 e 457 con la 3.10. Morale (già nella L3): tokenizzazione e segmentazione sono scelte che cambiano tutti i numeri a valle; per riprodurre un risultato bisogna fissare anche la versione della libreria.

### Notebook 3 · Contare con FreqDist

```python
freq_dist = nltk.FreqDist(tokenized_text)
freq_dist.most_common(20)
plt.figure(figsize=(15, 5))
freq_dist.plot(50, marker='o')
tokenized_text.count('Pinocchio')
```

Output:

```text
[(',', 3345), ('the', 2100), ('.', 1840), ('and', 1357), ('“', 1316), ('”', 1313),
 ('to', 1298), ('a', 1085), ('of', 860), ('I', 794), ('he', 728), ('you', 688),
 ('!', 616), ('his', 555), ('?', 485), ('in', 472), ('’', 458), ('Pinocchio', 451), ...]
451
```

`FreqDist` è un `Counter` con metodi in più: `N()` = numero di **istanze** (53.332 token), `B()` = numero di **tipi** (4.718), la distinzione della [scheda 8 della L2](L02-parole-e-token.md#p-8). In cima ci sono punteggiatura e parole funzionali: la virgola da sola è il 6,3% del testo, i primi 20 tipi coprono il 39% dei token. Il grafico mostra la tipica coda lunga (legge di Zipf): pochi tipi frequentissimi, migliaia di tipi rari.

Due cose da notare nella lista: le virgolette di apertura “ (1.316) e chiusura ” (1.313) sono tipi diversi, e quasi pareggiano (tre virgolette restano spaiate); l'apostrofo tipografico ’ (458) è un token a sé, perché il tokenizzatore PTB riconosce solo l'apostrofo ASCII. *Pinocchio* è il primo nome proprio, al 18° posto.

### Notebook 4 · Concordanze con nltk.Text

```python
nltk_text = nltk.Text(tokenized_text)
nltk_text.concordance('Pinocchio')
nltk_text.concordance('Pinocchio', width=100, lines=10)
```

Output:

```text
Displaying 25 of 457 matches:
tenberg EBook of The Adventures of Pinocchio , by C. Collodi -- Pseudonym of Ca
berg.org Title : The Adventures of Pinocchio Author : C. Collodi -- Pseudonym o
 GUTENBERG EBOOK THE ADVENTURES OF PINOCCHIO * * * Produced by Charles Keller (
...
```

Una **concordanza** (KWIC, *key word in context*) mostra ogni occorrenza della parola con una finestra di contesto: lo strumento classico dei lessicografi per capire come si usa una parola. `nltk.Text` avvolge la lista di token e aggiunge metodi di esplorazione (concordanze, collocazioni, dispersion plot).

Perché 457 occorrenze se `count('Pinocchio')` dava 451? La concordanza **ignora maiuscole e minuscole**: conta anche le 6 occorrenze di *PINOCCHIO* (titoli e intestazione, terza riga dell'output). È il *case folding* della [scheda 33 della L3](L03-elaborazione-del-testo.md#p-33) applicato di nascosto: due funzioni della stessa libreria danno numeri diversi per la "stessa" domanda. Le prime righe vengono dall'intestazione Gutenberg, non dal romanzo.

### Notebook 5 · Togliere le stopword

```python
from nltk.corpus import stopwords
stop_set = set(stopwords.words('english'))   # a set: fast membership tests
filtered_freq_dist = nltk.FreqDist({k: v for (k, v) in freq_dist.items()
                                    if k.lower() not in stop_set and k.isalnum()})
filtered_freq_dist.most_common(20)
```

Output:

```text
[('Pinocchio', 451), ('said', 225), ('Marionette', 204), ('little', 158), ('one', 144),
 ('like', 105), ('two', 104), ('poor', 93), ('Fairy', 91), ('good', 89), ('want', 85),
 ('Project', 83), ('cried', 79), ('go', 79), ('answered', 78), ('Geppetto', 74), ...]
```

Le **stopword** sono parole funzionali molto frequenti e poco informative sul contenuto (articoli, preposizioni, pronomi, ausiliari): la lista inglese di NLTK ne ha 198. Il filtro toglie anche ogni token non alfanumerico (`isalnum`: punteggiatura, ma anche *A-B-C* o *twenty-one*). Il confronto si fa su `k.lower()` perché la lista è in minuscolo.

Dopo il filtro la classifica parla del libro: *Pinocchio, Marionette, Fairy, Geppetto*, i verbi del dialogo (*said, cried, answered, asked*). Ma al 12° posto c'è ***Project* (83)**: viene quasi tutto dalla licenza Gutenberg. Il filtro funziona bene per vedere *di che cosa parla* un testo; vedremo con VADER che è pericoloso quando conta il *come*: la lista contiene *not, no, nor, but, very, too*.

### Notebook 6 · Collocazioni e PMI

```python
from nltk.collocations import BigramCollocationFinder, BigramAssocMeasures
bigram_measures = BigramAssocMeasures()

def is_noise(word):
    """True for stopwords and tokens shorter than 3 characters."""
    return len(word) < 3 or word.lower() in stop_set

finder = BigramCollocationFinder.from_words(tokenized_text)   # counts C(w1), C(w2), C(w1 w2)
finder.apply_word_filter(is_noise)                            # drop bigrams with a noisy word
finder.apply_freq_filter(5)                                   # drop bigrams seen < 5 times
finder.nbest(bigram_measures.pmi, 20)
```

Output:

```text
[('Lovely', 'Maiden'), ('Red', 'Lobster'), ('Azure', 'Hair'), ('United', 'States'),
 ('giant', 'oak'), ('public', 'domain'), ('Literary', 'Archive'), ('Little', 'Man'),
 ('oak', 'tree'), ('Fire', 'Eater'), ('Farmer', 'John'), ('Mastro', 'Antonio'),
 ('Mastro', 'Cherry'), ('A-B-C', 'book'), ('Archive', 'Foundation'),
 ('Gutenberg', 'Literary'), ('Terrible', 'Shark'), ('set', 'forth'),
 ('Talking', 'Cricket'), ('next', 'morning')]
```

Una **collocazione** è una combinazione di parole che compaiono insieme più spesso del caso (*strong tea* sì, *powerful tea* no). Per misurarlo si confronta la probabilità del bigramma con quella che avrebbe se le due parole fossero indipendenti: la **pointwise mutual information**
$$\text{PMI}(w_1,w_2) = \log_2\frac{P(w_1w_2)}{P(w_1)P(w_2)} = \log_2\frac{P(w_2\mid w_1)}{P(w_2)} = \log_2\frac{C(w_1w_2)\cdot N}{C(w_1)\,C(w_2)}.$$
La seconda forma usa la probabilità bigram MLE della [scheda 13 della L4](L04-modelli-linguistici-n-gram.md#p-13): di quanto cresce la probabilità di $w_2$ sapendo che la parola precedente è $w_1$. PMI = 0 se indipendenti, positiva se si attraggono.

Verifica a mano su *Talking Cricket*: $C(w_1w_2) = 18$, $C(\textit{Talking}) = 19$, $C(\textit{Cricket}) = 34$, $N = 53.332$: $\log_2(18\cdot 53332/(19\cdot 34)) = \log_2 1486{,}0 = 10{,}54$, identico a `bigram_measures.pmi`. In cima, *Lovely Maiden* (5, 5, 5) ha PMI 13,38: le due parole compaiono **solo** insieme.

La risposta alla domanda del notebook (*che cosa dice la lista del testo scaricato?*): *United States, public domain, Literary Archive, Archive Foundation, Gutenberg Literary* vengono dalla licenza, non da Collodi. Trigrammi e 4-grammi (celle 41-42) lo confermano: *Gutenberg Literary Archive Foundation* è il primo 4-gramma. Con i 4-grammi emergono anche i pezzi della tokenizzazione: *don ’ t want*, *I ’ ll give*.

Nota della cella 35: `nltk_text.collocations()` usa un'altra misura (il *log-likelihood ratio*) e dà infatti una lista diversa (*Project Gutenberg-tm, gold pieces, Project Gutenberg, Fire Eater, Talking Cricket*, ...).

### Notebook 7 · Perché serve il filtro di frequenza

```python
finder_all = BigramCollocationFinder.from_words(tokenized_text)   # no filters at all
for bigram in finder_all.nbest(bigram_measures.pmi, 10):
    print(bigram, "  C(w1 w2) =", finder_all.ngram_fd[bigram],
          " C(w1) =", finder_all.word_fd[bigram[0]], " C(w2) =", finder_all.word_fd[bigram[1]])

b = BigramCollocationFinder.from_documents(sentences)   # sentences are strings!
b.apply_freq_filter(5)
b.nbest(bigram_measures.pmi, 10)
```

Output:

```text
('#', '500')   C(w1 w2) = 1  C(w1) = 1  C(w2) = 1
('1500', 'West')   C(w1 w2) = 1  C(w1) = 1  C(w2) = 1
('4557', 'Melan')   C(w1 w2) = 1  C(w1) = 1  C(w2) = 1
...
[('*', '*'), ('/', '/'), ('5', '0'), ('0', '0'), ('2', '0'), (':', '/'), ('E', 'R'), ('V', 'E'), ('z', 'z'), ('O', 'U')]
```

Senza filtri, in cima ci sono bigrammi visti **una volta**, fatti di parole viste una volta: $C(w_1w_2) = C(w_1) = C(w_2) = 1$ dà $\text{PMI} = \log_2 N = \log_2 53332 = 15{,}70$, il massimo possibile: poiché $C(w_1w_2)\le\min(C(w_1),C(w_2))$, la PMI è al più $\log_2\big(N/\max(C(w_1),C(w_2))\big)$, e il valore $\log_2 N$ si raggiunge solo con tutti e tre i conteggi uguali a 1. Ho contato: **130 bigrammi** sono a pari merito a 15,70, e quasi tutti vengono dalla licenza (indirizzi, numeri, *AGREEMENT WILL*). La PMI è **sbilanciata verso gli eventi rari**: con conteggi minuscoli la stima MLE è inaffidabile, lo stesso problema degli zeri e dei conteggi piccoli negli n-gram ([scheda 46 della L4](L04-modelli-linguistici-n-gram.md#p-46)). La cura minima è una soglia di frequenza; la lezione sugli embedding tornerà su questo bias.

La cella 40 risponde a *che cosa succede usando `sentences`*: `from_documents` si aspetta una lista di documenti, ognuno una **lista di token**; una stringa invece viene iterata **carattere per carattere**, e si ottengono collocazioni di caratteri (`('*', '*')`, `('5', '0')`). Python non dà errore perché anche una stringa è iterabile: è il bug più comune con NLTK, lo stesso di `pos_tag` su una stringa (cella 55).

### Notebook 8 · Dispersion plot

```python
nltk_text.dispersion_plot(["Pinocchio", "Fox", "Cat", "Geppetto"])
len(tokenized_text)
```

Output:

```text
53332
```

Ogni trattino è un'occorrenza della parola, in ascissa la posizione nel testo (offset in token). Si legge la trama senza leggere il libro: *Pinocchio* è dappertutto; *Fox* e *Cat* compaiono sempre **insieme** (prima occorrenza ai token 9.683 e 9.686) in pochi episodi; *Geppetto* sta all'inizio (i primi capitoli, dal token 1.007) e alla fine (il ritrovamento nel pesce-cane, fino al token 49.930), quasi assente in mezzo. Il libro finisce al token 50.023 (`*** END`): gli ultimi 3.300 token sono licenza e nessun personaggio vi compare. È un modo semplice per vedere che la distribuzione delle parole non è stazionaria lungo un testo.

### Notebook 9 · PoS tagging con NLTK

```python
nltk.download('averaged_perceptron_tagger_eng')   # a pretrained linear classifier
nltk.pos_tag(nltk.word_tokenize('I saw a bird.'))
nltk.pos_tag(nltk.word_tokenize('Can you lend me a saw?'))
#nltk.pos_tag(sentences[42])   # it doesn't run on strings...
nltk.pos_tag(tokenized_sentences[42])
nltk.pos_tag(nltk.word_tokenize('My name is Andrea'))
nltk.pos_tag(nltk.word_tokenize('Mi chiamo Andrea'))
```

Output:

```text
[('I', 'PRP'), ('saw', 'VBD'), ('a', 'DT'), ('bird', 'NN'), ('.', '.')]
[('Can', 'MD'), ('you', 'PRP'), ('lend', 'VB'), ('me', 'PRP'), ('a', 'DT'), ('saw', 'NN'), ('?', '.')]
[('Oh', 'UH'), (',', ','), ('stop', 'VB'), ('it', 'PRP'), ('!', '.')]
[('My', 'PRP$'), ('name', 'NN'), ('is', 'VBZ'), ('Andrea', 'NNP')]
[('Mi', 'NNP'), ('chiamo', 'NN'), ('Andrea', 'NNP')]
```

`nltk.pos_tag` usa un **averaged perceptron**: un classificatore lineare che sceglie il tag di ogni parola guardando feature della parola e del contesto (parole vicine, suffissi, i tag già assegnati a sinistra), addestrato sul WSJ del Penn Treebank. Restituisce i tag **Penn Treebank** della [scheda 12 della L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-12).

- *saw* diventa VBD in *I saw a bird* e NN in *lend me a saw*: il tagging è disambiguazione con il contesto ([scheda 13 della L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-13)).
- *Oh* è UH (interiezione), *My* è PRP\$ (pronome possessivo), *is* è VBZ (presente, 3a singolare).
- Su una stringa la funzione non va (cella 55, commentata): itererebbe sui caratteri.
- Sull'italiano il tagger inglese sbaglia tutto: *Mi* NNP, *chiamo* NN. Non sa che lingua sta leggendo: assegna a parole mai viste i tag più plausibili *per l'inglese* (maiuscola → nome proprio, altrimenti nome). È il caso estremo del problema del dominio ([scheda 21 della L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-21)).

### Notebook 10 · PoS tagging dell'italiano con spaCy

```python
# !python -m spacy download it_core_news_sm
import spacy
nlp = spacy.load("it_core_news_sm")      # pretrained Italian pipeline
doc = nlp("Mi chiamo Andrea")
for token in doc:
    print(f"{token.text}: {token.pos_}")
```

Output:

```text
Mi: PRON
chiamo: VERB
Andrea: PROPN
```

Con un modello addestrato sull'italiano i tag sono giusti: *Mi* pronome (clitico), *chiamo* verbo, *Andrea* nome proprio. spaCy usa il tagset **Universal Dependencies** (`pos_`: PRON, VERB, PROPN, [scheda 10 della L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-10)), lo stesso per tutte le lingue; il tag fine specifico del treebank sta in `tag_`. Nota tecnica: nell'output salvato la cella 60 (`!python -m spacy download`) ha fallito sulla macchina di chi l'ha eseguita (*No module named spacy* in un altro interprete Python); la cella 61 ha funzionato perché il modello era già installato nel kernel del notebook.

### Notebook 11 · Stemming e lemmatizzazione

```python
from nltk.stem.porter import PorterStemmer
stemmer = PorterStemmer()
stemmer.stem('cars'), stemmer.stem('was')

from nltk.stem import WordNetLemmatizer
wnl = WordNetLemmatizer()
wnl.lemmatize('dogs')
wnl.lemmatize('was')                 # by default it assumes a noun
wnl.lemmatize('was', pos='v')
wnl.lemmatize('better'), wnl.lemmatize('better', pos='a'), wnl.lemmatize('better', pos='r')
```

Output:

```text
('car', 'wa')
'dog'
'wa'
'be'
('better', 'good', 'well')
```

Ripasso della [scheda 33](L03-elaborazione-del-testo.md#p-33) e della [scheda 34 della L3](L03-elaborazione-del-testo.md#p-34). Lo **stemmer di Porter** applica regole di riscrittura dei suffissi senza dizionario: *cars → car* va bene, ma *was → wa* (la regola *-s → ∅* non sa che *was* è un verbo irregolare). Ho provato altre parole: *policy → polici*, *studies → studi*, e sia *university* sia *universal* diventano *univers*: lo stemming confonde parole di significato diverso.

Il **lemmatizzatore WordNet** cerca il lemma nel dizionario WordNet, ma deve sapere la **parte del discorso**: senza `pos` assume un nome, e allora *was* diventa *wa* anche qui (WordNet ha davvero il nome *WA*, la sigla dello stato di Washington). Con `pos='v'` dà *be*; *better* è *good* come aggettivo e *well* come avverbio. Quindi la lemmatizzazione corretta richiede prima il PoS tagging: è quello che fa spaCy nella sua pipeline (parte 2), dove `token.lemma_` arriva dopo il tagger.

### Notebook 12 · Bag of words: l'ordine si perde

```python
t1 = nltk.word_tokenize('I won, and thus you lose.')
t2 = nltk.word_tokenize('I lose, and thus you won.')
t1 == t2
b1, b2 = set(t1), set(t2)     # binary bag of words of one document
b1 == b2
```

Output:

```text
False
True
```

Per classificare un documento serve un vettore $\mathbf x$ di **lunghezza fissa** ([scheda 8 della L6](L06-regressione-logistica.md#p-8)), ma i documenti hanno lunghezze diverse. Il **bag of words** fissa un vocabolario $V$ e rappresenta un documento $d$ con un vettore in $\mathbb R^{|V|}$: $x_j = 1$ se $w_j$ compare in $d$ (versione **binaria**) oppure $x_j = C_d(w_j)$ (versione a **conteggi**). Una feature per parola del vocabolario: decine di migliaia di feature, quasi tutte 0 in un dato documento (vettore *sparso*), e nessun lessico scelto a mano: è il classificatore a imparare quali parole contano (la differenza con le sei feature della [scheda 26 della L6](L06-regressione-logistica.md#p-26), che si vedrà nell'esercizio B2).

Il prezzo: l'**ordine** sparisce. *I won, and thus you lose* e *I lose, and thus you won* hanno la stessa bag (stesso insieme di 8 token) e significato opposto; anche *good movie, not bad* e *bad movie, not good*. In Python la bag binaria di un documento è semplicemente il `set` dei suoi token.

### Notebook 13 · N-grammi di parole e di caratteri

```python
b1 = set(nltk.ngrams(nltk.word_tokenize('I won, and thus, you lose.'), 2))
b2 = set(nltk.ngrams(nltk.word_tokenize('I lose, and thus, you won.'), 2))
b1 == b2

b1 = set(nltk.ngrams('rainbow', 3))      # a string is a sequence of characters
b2 = set(nltk.ngrams('rainbaw', 3))
b1.intersection(b2)
```

Output:

```text
False
{('a', 'i', 'n'), ('i', 'n', 'b'), ('r', 'a', 'i')}
```

Una **bag of bigrams** conserva un po' di ordine locale: ora *(I, won)* e *(you, lose)* stanno in un documento, *(I, lose)* e *(you, won)* nell'altro, e i due insiemi differiscono (4 bigrammi su 8 in comune). Sono gli n-gram della [scheda 7 della L4](L04-modelli-linguistici-n-gram.md#p-7), usati qui come feature invece che per stimare probabilità. Il costo è un vocabolario molto più grande e più sparso.

`nltk.ngrams` funziona su qualunque sequenza, anche su una stringa: si ottengono gli **n-grammi di caratteri**. *rainbow* e il refuso *rainbaw* hanno 5 trigrammi ciascuno, 3 in comune: la somiglianza di Jaccard è $|A\cap B|/|A\cup B| = 3/7 = 0{,}43$, mentre come parole intere sarebbero semplicemente diverse. Gli n-grammi di caratteri rendono la rappresentazione robusta a refusi, varianti morfologiche e parole mai viste: la stessa idea, più raffinata, della tokenizzazione subword della [scheda 28 della L2](L02-parole-e-token.md#p-28).

Commento al notebook del corso `HLT-2026-27-L09-NLTK_and_SpaCy.ipynb` (il notebook è del docente e non è incluso).

Seconda parte guidata (celle 90-151). Prima il **sentiment** in due modi opposti: **VADER**, un analizzatore a regole con un lessico fatto a mano, e un **transformer** pre-addestrato (DistilBERT su SST-2) usato come scatola nera tramite la `pipeline` di Hugging Face. Poi **spaCy**: una pipeline che da una stringa produce un oggetto `Doc` con frasi, lemmi, PoS, dipendenze sintattiche, noun chunk ed entità; infine la stessa NER con NLTK (`ne_chunk`) per confronto.

Ho rieseguito tutto (NLTK 3.9.2, spaCy 3.8 con `en_core_web_sm` 3.8.0, transformers con PyTorch su CPU): output identici a quelli salvati. Ho trovato **due affermazioni sbagliate** sull'interpretazione dei punteggi di VADER (riquadri nel secondo blocco).

### Notebook 1 · VADER: un lessico e qualche regola

```python
from nltk.sentiment import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()
vader_lexicon = sia.lexicon          # dict: token -> valence in [-4, +4]
type(vader_lexicon), len(vader_lexicon)
```

Output:

```text
(dict, 7502)
[('$:', -1.5), ('%)', -0.4), ('%-)', -1.5), ('&-:', -0.4), ...]
```

**VADER** (Hutto e Gilbert, 2014) è un analizzatore di sentiment **a regole**, pensato per testi brevi dei social: nessun parametro appreso da dati etichettati. Due ingredienti:

1. **Lessico**: 7.502 voci (parole, ma anche emoticon e slang), ognuna con una **valenza** in $[-4, +4]$, media dei voti di 10 annotatori. Valori controllati: *great* 3,1, *good* 1,9, *nice* 1,8, *fantastic* 2,6, *sucked* −2,0, *disappointed* −2,1, *bad* −2,5; *predictable* e *gripping* non ci sono (valenza 0).
2. **Regole** che correggono la valenza col contesto (costanti verificate nel sorgente di NLTK): una **negazione** nelle 3 parole precedenti moltiplica per $-0{,}74$; un **intensificatore** (*very, absolutely*) aggiunge $0{,}293$ in modulo, un attenuatore (*kind of, slightly*) lo toglie; una parola in **MAIUSCOLO** in un testo misto aggiunge $0{,}733$; ogni **!** aggiunge $0{,}292$ (al massimo 4); con **but** le parole prima pesano $0{,}5$ e quelle dopo $1{,}5$.

Le valenze corrette si sommano in $s$, che viene schiacciato in $(-1, 1)$: $\text{compound} = s/\sqrt{s^2+15}$. Per esempio *good* da solo: $1{,}9/\sqrt{1{,}9^2+15} = 0{,}4404$; *not good*: $s = -0{,}74\cdot 1{,}9 = -1{,}406$, compound $-0{,}3412$. È lo stesso schema della [scheda 26 della L6](L06-regressione-logistica.md#p-26) (contare parole positive e negative di un lessico), ma con pesi fissati a mano invece che appresi.

La cella 95 disegna le 20 voci più positive e più negative del lessico (figura non riportata: molte voci negative sono insulti e parole di violenza).

### Notebook 2 · VADER su una recensione: i quattro punteggi

```python
text = ("The new movie, called Pinocchio, was absolutely fantastic! The plot was gripping, "
        "and the actors gave an outstanding performance. However, the ending was a bit too "
        "predictable, which left me very disappointed.")
sentiment_score = sia.polarity_scores(text)
prob_positive = (sentiment_score['compound'] + 1) / 2     # compound varies in (-1, 1)
```

Output:

```text
NLTK Sentiment Analysis Result: {'neg': 0.086, 'neu': 0.707, 'pos': 0.207, 'compound': 0.6996}
Overall probability of positive sentiment: 0.8498
```

Il conto si rifà a mano. VADER divide il testo su spazi e toglie la punteggiatura: 31 parole, di cui solo tre nel lessico.

| parola | valenza | regola | valenza finale |
| --- | --- | --- | --- |
| fantastic | 2,6 | preceduta da *absolutely*: +0,293 | 2,893 |
| outstanding | 3,0 |  | 3,0 |
| disappointed | −2,1 | preceduta da *very*: −0,293 | −2,393 |

Somma 3,5, più 0,292 per il punto esclamativo: $s = 3{,}792$, $\text{compound} = 3{,}792/\sqrt{3{,}792^2+15} = 0{,}6996$. *However* non è trattato come *but* (la regola riconosce solo *but*), quindi la delusione finale non pesa di più.

> **Attenzione (errore nelle slide): neg, neu e pos non sono percentuali del testo**
>
> Il markdown (celle 90 e 99) dice che *8.6% of text is negative, 70.7% neutral, 20.7% positive*. Non è così. Nel testo c'è **una** parola negativa su 31 (3,2%) e due positive (6,5%). VADER calcola i tre punteggi su una somma pesata in cui ogni parola neutra vale 1 e ogni parola con sentiment vale $1 + |v|$ ($v$ = valenza dopo le regole; la spinta dei punti esclamativi va al lato più forte):
>
> $$\text{pos} = \frac{(2{,}893+1)+(3{,}0+1)+0{,}292}{39{,}578} = 0{,}207,\quad \text{neg} = \frac{2{,}393+1}{39{,}578} = 0{,}086,\quad \text{neu} = \frac{28}{39{,}578} = 0{,}707$$
>
> con $39{,}578 = 8{,}185 + 3{,}393 + 28$. Sono quindi quote di **intensità** di sentiment, non quote di testo: *disappointed*, una parola, pesa come 3,4 parole neutre. Verificato ricostruendo le valenze parola per parola con le funzioni interne di `SentimentIntensityAnalyzer` e confrontando con `polarity_scores`.

> **Attenzione (errore nelle slide): (compound + 1)/2 non è una probabilità**
>
> La cella 100 (e poi la 101 e la 108) stampa *Overall probability of positive sentiment*. Il compound è una somma di valenze schiacciata da $s/\sqrt{s^2+15}$: nessun modello probabilistico, nessun addestramento che lo calibri. Riscalarlo in $[0,1]$ non lo rende una probabilità. Prova: dipende da quante parole positive ci sono, non da quanto è certo il giudizio. *good* dà 0,72, *good good good* 0,91, *good* ripetuto sei volte 0,97, e *It was good.* ripetuto cinque volte 0,96. Sulla stessa recensione DistilBERT dice NEGATIVE con 0,94 (blocco più sotto), VADER "0,85 di probabilità di positivo". Una vera $P(+\mid x)$ è quella della regressione logistica ([scheda 28 della L6](L06-regressione-logistica.md#p-28)), stimata con la cross-entropy sui dati. Meglio chiamare $(\text{compound}+1)/2$ un **punteggio** in $[0,1]$.

### Notebook 3 · Un nome proprio con parole negative

```python
text2 = "The new movie, called The Hell of Rapists, was absolutely fantastic!"
sentiment_score2 = sia.polarity_scores(text2)
```

Output:

```text
{'neg': 0.436, 'neu': 0.379, 'pos': 0.185, 'compound': -0.743}
```

Un titolo di film inventato contiene due parole con valenza fortemente negativa (*hell* −3,6, *rapists* −3,3): la recensione è entusiasta ma il compound è −0,74. Un lessico non sa che quelle parole fanno parte di un **nome proprio** (un'entità, nel senso della NER della [scheda 59 della L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-59)) e che quindi non esprimono il giudizio di chi scrive. Un sistema basato su parole isolate non ha modo di distinguere *uso* e *menzione*: servirebbe almeno riconoscere le entità prima di contare il sentiment.

### Notebook 4 · Togliere le stopword cambia il sentiment?

```python
stop_words = set(stopwords.words('english'))
tokens = nltk.word_tokenize(text)
filtered_tokens = [word for word in tokens if word.lower() not in stop_words]
filtered_text = ' '.join(filtered_tokens)
filtered_sent_score = sia.polarity_scores(filtered_text)
```

Output:

```text
'new movie , called Pinocchio , absolutely fantastic ! plot gripping , actors gave outstanding performance . However , ending bit predictable , left disappointed .'
NLTK Sentiment Analysis Result: {'neg': 0.118, 'neu': 0.571, 'pos': 0.311, 'compound': 0.7257}
```

Sì, e il motivo è preciso. *very* è nella lista delle stopword di NLTK: togliendolo, *disappointed* perde l'intensificatore e torna a −2,1. Nuova somma $2{,}893 + 3{,}0 - 2{,}1 + 0{,}292 = 4{,}085$, compound $4{,}085/\sqrt{4{,}085^2+15} = 0{,}7257$: la recensione sembra **più** positiva. *absolutely* invece non è una stopword e resta. neu scende (da 28 a 15 parole neutre, su 18 parole invece di 31) e quindi pos e neg salgono: un'altra prova che non sono quote di testo.

Il caso peggiore è la negazione: *not, no, nor, but* sono stopword. *The movie was not good* ha compound −0,34; filtrato diventa *movie good*, compound +0,44: polarità **invertita**. La rimozione delle stopword è una scelta che dipende dal compito: utile per vedere di che cosa parla un testo (le frequenze del blocco sulle stopword), dannosa per il sentiment, dove le parole funzionali portano negazione, intensità e contrasto (il trucco NOT\_ della L6 serve proprio a conservarle).

### Notebook 5 · Un modello pre-addestrato: la pipeline di Hugging Face

```python
from transformers import pipeline
sentiment_pipeline = pipeline('sentiment-analysis',
    model='distilbert/distilbert-base-uncased-finetuned-sst-2-english')
sentiment_result = sentiment_pipeline(text)
```

Output:

```text
[{'label': 'NEGATIVE', 'score': 0.9432029128074646}]
```

`pipeline` nasconde tutto: scarica il modello, lo tokenizza (con il suo tokenizzatore subword, [scheda 28 della L2](L02-parole-e-token.md#p-28)), lo esegue e trasforma le uscite in un'etichetta con un punteggio (la softmax delle due classi, [scheda 7 della L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-7)). Il modello è **DistilBERT**, un transformer piccolo, prima pre-addestrato su testo generico e poi addestrato (*fine-tuned*) su **SST-2**, frasi di recensioni etichettate positivo/negativo: a differenza di VADER, il sentiment l'ha **imparato** dai dati. I transformer avranno più lezioni nel seguito del corso; qui è una scatola nera.

Sulla stessa recensione il verdetto è opposto a VADER: **NEGATIVE con 0,943**. Ho provato a togliere l'ultima frase (*However, the ending ... very disappointed.*): diventa POSITIVE con 0,9999. Il modello dà molto peso alla conclusione delusa, che VADER tratta come una parola negativa fra tante. Altre prove: *not good* NEGATIVE 0,9998, *The movie was not bad at all* POSITIVE 0,997: la negazione è gestita dal contesto, senza regole scritte a mano. Quale dei due ha ragione su questa recensione è discutibile; il confronto quantitativo sta nell'esercizio B2.

### Notebook 6 · spaCy: una pipeline, un oggetto Doc

```python
import spacy
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

doc = nlp(text)                 # text: three paragraphs about Game of Thrones
len(doc), doc[2], doc[42]
for i, sentence in enumerate(doc.sents):
    print(i, sentence.text)
```

Output:

```text
(412, Thrones, Martin)
0 Game of Thrones is an American fantasy drama television series created by David Benioff and D. B. Weiss for HBO.
1 It is an adaptation of A Song of Ice and Fire, a series of fantasy novels by George R. R. Martin, the first of which is A Game of Thrones.
...
```

Due filosofie: NLTK è una **cassetta degli attrezzi** (funzioni separate su liste di token, le combini tu), spaCy è una **pipeline**: carichi un modello una volta, gli passi la stringa grezza e ottieni un `Doc` con tutte le analisi già fatte. Per `en_core_web_sm` i componenti sono `tok2vec, tagger, parser, attribute_ruler, lemmatizer, ner` (verificato con `nlp.pipe_names`): una piccola rete neurale (`tok2vec`) calcola una rappresentazione di ogni token, condivisa dai componenti successivi. `_sm` = *small*; esistono `_md`, `_lg` e `_trf` (basato su un transformer).

Il `Doc` si comporta come una sequenza di token: `len(doc)` = 412 token (spazi e a capo compresi), `doc[2]` = *Thrones*. `doc.sents` dà le frasi, segmentate usando l'albero a dipendenze del parser invece di regole sul punto: *D. B. Weiss* e *George R. R. Martin* non spezzano la frase, il problema delle abbreviazioni della [scheda 32 della L3](L03-elaborazione-del-testo.md#p-32) risolto dal modello.

### Notebook 7 · Attributi dei token: lemma, PoS, dipendenza, forma

```python
for token in doc:
    row = [token.text,
           token.lemma_,   # lemmatization
           token.pos_,     # coarse PoS (Universal Dependencies)
           token.tag_,     # fine-grained PoS (Penn Treebank)
           token.dep_,     # syntactic dependency relation
           token.shape_,   # orthographic word shape
           token.is_alpha, token.is_stop]
    print(row)
df = pd.DataFrame(tokens)   # one row per token
```

Output:

```text
['Game', 'Game', 'PROPN', 'NNP', 'nsubj', 'Xxxx', True, False]
['of', 'of', 'ADP', 'IN', 'prep', 'xx', True, True]
['Thrones', 'Thrones', 'PROPN', 'NNP', 'pobj', 'Xxxxx', True, False]
['is', 'be', 'AUX', 'VBZ', 'ROOT', 'xx', True, True]
...
['created', 'create', 'VERB', 'VBN', 'acl', 'xxxx', True, False]
['D.', 'D.', 'PROPN', 'NNP', 'compound', 'X.', False, False]
```

Ogni token porta tutte le analisi: `lemma_` (*is → be*, *created → create*, senza dover passare la PoS a mano come con WordNet), **due tagset** insieme, `pos_` Universal Dependencies (PROPN, AUX, ADP) e `tag_` Penn Treebank (NNP, VBZ, IN), come nelle [schede 10](L08-sequence-labelling-pos-tagging-e-ner.md#p-10) e [12 della L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-12); `dep_`, la relazione sintattica con la testa; `shape_`, la **word shape** (maiuscole → X, minuscole → x, cifre → d, sequenze lunghe accorciate a 4: *Thrones → Xxxxx*), proprio la feature dei CRF per le parole sconosciute ([scheda 77 della L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-77)); `is_stop`, la lista di stopword di spaCy.

Il DataFrame (cella 131) mette tutto in tabella, 412 righe: comodo per filtrare e contare. L'ultima riga è il token `\n` con PoS SPACE: spaCy conserva gli spazi come token per poter ricostruire il testo esatto.

### Notebook 8 · L'albero a dipendenze

```python
from spacy import displacy
pinocchio_doc = nlp("Pinocchio sold his book to buy a ticket.")
for token in pinocchio_doc:
    print(f"{token.text:10s} --{token.dep_:>6s}-->  {token.head.text}")
display(HTML(displacy.render(pinocchio_doc, style="dep")))
```

Output:

```text
Pinocchio  -- nsubj-->  sold
sold       --  ROOT-->  sold
his        --  poss-->  book
book       --  dobj-->  sold
to         --   aux-->  buy
buy        -- advcl-->  sold
a          --   det-->  ticket
ticket     --  dobj-->  buy
.          -- punct-->  sold
```

Un **dependency parse** collega ogni parola alla sua **testa** con un arco etichettato dalla relazione grammaticale; il verbo principale è la **ROOT** (in spaCy la sua testa è sé stesso, come si vede nell'output), e gli archi formano un albero ([scheda 44 della L1](L01-introduzione-al-corso.md#p-44)). Qui: *Pinocchio* soggetto (`nsubj`) di *sold*, *book* oggetto diretto (`dobj`), *his* possessivo di *book*, *buy* subordinata avverbiale (`advcl`: il perché della vendita) con il suo oggetto *ticket*. Chi fa che cosa a chi, leggibile dagli archi.

Le etichette sono quelle di ClearNLP usate da spaCy (`dobj`, `poss`, `prep`, `pobj`), non quelle Universal Dependencies (che userebbero `obj`, `nmod:poss`). L'altra rappresentazione classica è l'albero a costituenti, che raggruppa le parole in sintagmi annidati; il parsing è nei capitoli 19-20 del libro, facoltativi per questo laboratorio.

### Notebook 9 · Noun chunk e verbi

```python
print("Noun phrases:", [chunk.text for chunk in doc.noun_chunks])
print("Verbs:", [token.lemma_ for token in doc if token.pos_ == "VERB"])
```

Output:

```text
Noun phrases: ['Game', 'Thrones', 'an American fantasy drama television series', 'David Benioff', 'D. B. Weiss', 'HBO', 'It', 'an adaptation', 'A Song', 'Ice', 'Fire', ...]
Verbs: ['create', 'shoot', 'premier', 'conclude', 'broadcast', 'Set', 'have', 'follow', ..., 'praise', 'act', ...]
```

I **noun chunk** sono sintagmi nominali *di base*: un nome con determinanti, aggettivi e nomi modificatori che dipendono da lui (*an American fantasy drama television series*), ricavati dall'albero a dipendenze. Sono piatti, senza annidamenti: *Game of Thrones* esce come due chunk, *Game* e *Thrones*, perché *of Thrones* è un sintagma preposizionale attaccato a *Game*. Utili per estrarre le "cose" di cui parla un testo.

Il filtro sui verbi usa `pos_` e `lemma_` insieme. Si vedono errori del modello piccolo: *premiered → premier* (il lemma giusto è *premiere*), *Set* lasciato maiuscolo, *act* da *its acting*, che lì è un nome. Un tagger al 97% sbaglia comunque una parola su 30.

### Notebook 10 · NER con spaCy

```python
text = """Apple Inc. was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne
in April 1976 in Cupertino, California. The company is known for its iPhones,
iPads, and Mac computers. In 2023, Apple became the first company to reach a
market capitalization of $3 trillion."""
doc = nlp(text)
for ent in doc.ents:                       # entities found by the pipeline
    print(f"{ent.text:<20} {ent.label_:<10} {spacy.explain(ent.label_)}")
html = displacy.render(doc, style="ent")
```

Output:

```text
Apple Inc.           ORG        Companies, agencies, institutions, etc.
Steve Jobs           PERSON     People, including fictional
Steve Wozniak        PERSON     People, including fictional
Ronald Wayne         PERSON     People, including fictional
April 1976           DATE       Absolute or relative dates or periods
Cupertino            GPE        Countries, cities, states
California           GPE        Countries, cities, states
iPhones              ORG        Companies, agencies, institutions, etc.
Mac                  ORG        Companies, agencies, institutions, etc.
2023                 DATE       Absolute or relative dates or periods
Apple                ORG        Companies, agencies, institutions, etc.
first                ORDINAL    "first", "second", etc.
$3 trillion          MONEY      Monetary values, including unit
```

Le entità sono già in `doc.ents`: ogni entità è uno **span** (inizio, fine, tipo), l'output di un named entity recognizer della [scheda 61 della L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-61). Il modello è addestrato su OntoNotes, con 18 tipi: oltre a PERSON, ORG e GPE (entità geopolitiche: stati, città), anche tipi "numerici" come DATE, MONEY, ORDINAL, CARDINAL. Internamente il riconoscimento si fa con tag in stile BIO sui token ([scheda 64 della L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-64)): `token.ent_iob_` e `token.ent_type_`, usati nell'esercizio A4.

Quasi tutto giusto, con errori istruttivi: *iPhones* e *Mac* sono prodotti, non organizzazioni (OntoNotes ha il tipo PRODUCT), *iPads* è mancato del tutto. È l'**ambiguità di tipo** della [scheda 63 della L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-63): lo stesso nome (*Apple*, *Mac*) può essere azienda o prodotto. Sul testo di Game of Thrones si vede di più: *Thrones* ORG, *Westeros* ORG, *the Iron Throne* PERSON. *\$3 trillion* è un'unica entità MONEY, simbolo di valuta compreso.

### Notebook 11 · La stessa NER con NLTK

```python
nltk.download('words')                   # word list: the chunker checks if a word is Basic English
nltk.download('maxent_ne_chunker_tab')   # maximum-entropy classifier (= multinomial logistic regression)
from nltk.chunk import ne_chunk
named_entities = ne_chunk(pos_tag(word_tokenize(text)))   # PoS tags are required

def extract_entities(tree):
    entities = []
    for subtree in tree:
        if isinstance(subtree, nltk.Tree):   # a named entity
            entities.append((" ".join(w for w, t in subtree.leaves()), subtree.label()))
    return entities
```

Output:

```text
Apple                PERSON
Inc.                 ORGANIZATION
Steve Jobs           PERSON
Steve Wozniak        PERSON
Ronald Wayne         PERSON
Cupertino            GPE
California           GPE
iPhones              ORGANIZATION
iPads                ORGANIZATION
Mac                  ORGANIZATION
Apple                PERSON
```

NLTK vuole i passi espliciti: tokenizzare, fare il PoS tagging, poi `ne_chunk`, che restituisce un albero (`nltk.Tree`) in cui le entità sono sottoalberi etichettati (`(PERSON Steve/NNP Jobs/NNP)`). Il chunker è un classificatore a **massima entropia**, cioè una **regressione logistica multinomiale** ([L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-5)), su feature scritte a mano: la parola, il suo PoS, la forma (maiuscole, cifre), prefisso e suffisso di 3 lettere, parole e PoS vicini, il tag già assegnato alla parola precedente e, verificato nel sorgente, se la parola appartiene alle 850 parole del *Basic English* (`words.words('en-basic')`). Sono le feature locali di un CRF ([scheda 75 della L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-75)), ma la decisione si prende un token alla volta, da sinistra a destra, senza la decodifica globale di Viterbi.

Risultato peggiore di spaCy: *Apple* è PERSON due volte e *Inc.* un'organizzazione separata (span sbagliato), e mancano date e importi perché i tipi di NLTK sono solo PERSON, ORGANIZATION, GPE, LOCATION, FACILITY (più il raro GSP). L'esercizio A4 misura la differenza con precision e recall sugli span.

### Notebook 12 · NLTK o spaCy?

|  | NLTK | spaCy |
| --- | --- | --- |
| input | liste di token | testo grezzo |
| stile | funzioni indipendenti da combinare | una pipeline, una chiamata |
| modelli | algoritmi classici: perceptron, massima entropia, regole (Porter, VADER) | reti neurali pre-addestrate per molte lingue |
| output | liste, insiemi, alberi | `Doc` con attributi per token e span |
| punti di forza | corpora e risorse lessicali (WordNet, treebank, movie\_reviews), didattica, controllo di ogni passo | velocità, NER e parsing migliori, uso in produzione |

La sintesi del notebook: NLTK per esplorare e studiare (e per i corpora, usati anche negli esercizi), spaCy per applicazioni veloci e robuste. Entrambi usano **modelli statistici** addestrati su corpora annotati; cambia il tipo di modello (classificatori lineari su feature scritte a mano contro piccole reti neurali su rappresentazioni apprese). Il nodo comune con le lezioni: i numeri dipendono dal corpus di addestramento e dal dominio.

Commento al notebook del corso `HLT-2026-27-L09-NLTK_and_SpaCy.ipynb` (il notebook è del docente e non è incluso).

Gli esercizi del laboratorio (celle 152-198), non valutati: per ognuno una cella *YOUR CODE HERE* e una *check cell* che stampa se la funzione è giusta e poi la usa su dati veri. **Parte A** (J&M cap. 18, L8): ambiguità dei tag, baseline most-frequent-tag, valutazione della NER sugli span, cambio di dominio. **Parte B** (J&M cap. 4, L6-L7): le sei feature della Fig. 4.2 con il lessico di VADER, precision/recall/F1 di quattro classificatori di sentiment, paired bootstrap test.

Attenzione al file salvato: le celle *YOUR CODE HERE* sono già compilate da chi ha eseguito il notebook, in parte con **tentativi sbagliati** (A1, A2, A3, il bonus) e con output di versioni precedenti (A4). Non sono soluzioni del docente. Le soluzioni complete, scritte e verificate a parte facendo passare tutte le check cell, sono nella sezione *Studio ed esercizi* (esercizi A1-A5, B1-B3); gli output qui sotto sono quelli ottenuti con quelle soluzioni (NLTK 3.9.2, spaCy 3.8, `en_core_web_sm` e `it_core_news_sm` 3.8.0, scikit-learn, DistilBERT su CPU).

### Notebook 1 · Setup della parte A: un campione del Penn Treebank

```python
from nltk.corpus import treebank
from spacy.tokens import Doc
nlp_en = spacy.load("en_core_web_sm")

tb_sents = [[(w, t) for (w, t) in s if t != "-NONE-"] for s in treebank.tagged_sents()]
_cut = int(0.8 * len(tb_sents))
tb_train, tb_test = tb_sents[:_cut], tb_sents[_cut:]
```

Output:

```text
3131 training and 783 test sentences; 94084 tokens
[('Pierre', 'NNP'), ('Vinken', 'NNP'), (',', ','), ('61', 'CD'), ('years', 'NNS'), ('old', 'JJ'), (',', ','), ('will', 'MD'), ('join', 'VB'), ('the', 'DT'), ('board', 'NN'), ...]
```

NLTK contiene un campione del 10% del **Penn Treebank** WSJ: 3.914 frasi con i tag gold. Si tolgono i token `-NONE-`, elementi vuoti dell'annotazione sintattica (tracce, soggetti sottintesi), che non sono parole del testo: restano 94.084 token. Divisione 80/20 **per frasi** e nell'ordine del corpus (le prime 3.131 per il training, le ultime 783 per il test), quindi i documenti di test sono diversi da quelli di training. Le check cell usano `Doc(nlp_en.vocab, words=...)` per dare a spaCy gli **stessi token** di NLTK: altrimenti i due tagger non sarebbero confrontabili token per token.

### Notebook 2 · A1. Sei parti del discorso per back

```python
BACK = [("earnings growth took a back seat", "JJ"), ("a small building in the back", "NN"),
        ("a clear majority of senators back the bill", "VBP"), ("Dave began to back toward the door", "VB"),
        ("enable the country to buy back debt", "RP"), ("I was twenty-one back then", "RB")]

def two_taggers(sentence):
    words = nltk.word_tokenize(sentence)
    return (words, [t for _, t in nltk.pos_tag(words)],
            [tok.tag_ for tok in nlp_en(Doc(nlp_en.vocab, words=words))])
```

Output:

```text
gold  NLTK  spaCy  sentence
JJ    JJ    JJ     earnings growth took a back seat
NN    NN    NN     a small building in the back
VBP   VBP   VBP    a clear majority of senators back the bill
VB    VB    VB     Dave began to back toward the door
RP    RP    RB     enable the country to buy back debt
RB    RB    RB     I was twenty-one back then
```

Le sei frasi della [scheda 18 della L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-18): NLTK le azzecca tutte, spaCy sbaglia solo la particella di *buy back* (RB invece di RP), un errore classico perché particella e avverbio hanno la stessa forma e si distinguono solo per il legame col verbo. Attenzione però: queste frasi vengono dal WSJ o dal libro, e il tagger di NLTK è addestrato sul WSJ; frasi "facili" per costruzione.

Il compito è trovare almeno tre frasi su cui i due tagger **non sono d'accordo**, e decidere chi ha ragione con il tagset Penn. Il tentativo salvato nella cella 159 usa frasi informali (*yuppy, that's one incredible sentence*): passa il controllo, ma i disaccordi sono su interiezioni e minuscole, poco interessanti. Una soluzione con frasi ambigue vere è nell'esercizio A1 della sezione studio.

### Notebook 3 · A2. Quanto è ambiguo l'inglese?

```python
# check A2 (excerpt)
_toy = [("the", "DT"), ("back", "NN"), ("back", "RB"), ("the", "DT"), ("dog", "NN")]
ft, fk = ambiguity_stats(_toy)          # must be (1/3, 0.4)
...
ft, fk = ambiguity_stats([p for s in tb_sents for p in s])
```

Output:

```text
with a correct ambiguity_stats:
OK treebank sample: 9.9% of the types are ambiguous, covering 36.5% of the tokens  (book, full WSJ: 14% / 55%)
   the most ambiguous words, with their tag counts:
   set    {'VBN': 12, 'VBD': 6, 'VB': 6, 'NN': 3, 'VBP': 2}
   back   {'RB': 15, 'RP': 6, 'NN': 2, 'VB': 1, 'JJ': 1}
   hit    {'VBN': 3, 'VBD': 3, 'VB': 2, 'NN': 1, 'VBP': 1}
   the    {'DT': 4038, 'JJ': 5, 'NNP': 1, 'CD': 1}
   a      {'DT': 1874, 'JJ': 2, 'IN': 1, 'LS': 1}
```

La Fig. 18.4 del libro ([scheda 17 della L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-17)): sul WSJ completo il 14% dei **tipi** è ambiguo (compare con 2 o più tag) ma copre il 55% dei **token**. Sul campione: **9,9% dei tipi, 36,5% dei token**. La forbice è la stessa: pochi tipi ambigui, ma sono le parole **frequenti** (*the* con 4.038 DT ha anche 5 JJ, 1 NNP e 1 CD; *a*, *set*, *back*).

Perché meno del libro (domanda *Discuss*): un tipo risulta ambiguo solo se nel corpus lo **vediamo** con due tag diversi. Con il 10% dei dati molti tipi compaiono poche volte, spesso una sola, e non hanno occasione di mostrare il secondo tag; tutte le parole rare sembrano non ambigue. Più dati, più ambiguità osservata: la stessa logica di Heaps ([scheda 12 della L2](L02-parole-e-token.md#p-12)) applicata alle coppie (parola, tag). Notare anche i tag "anomali" di *the* (JJ, CD): in parte errori di annotazione, che su un corpus grande gonfiano ulteriormente il conteggio dei tipi ambigui.

> **Attenzione (errore nelle slide): La check cell di A2 accetta una funzione sbagliata (e l'output salvato è sbagliato)**
>
> La cella 163 controlla `ambiguity_stats` solo sull'esempio giocattolo, dove ogni parola ambigua ha **due** tag e compare **due** volte. La funzione salvata nella cella 162 conta, per i tipi, il numero di tag "nuovi" diviso per il numero di tipi, e per i token il numero totale di tag delle parole ambigue diviso per $N$: sull'esempio giocattolo dà per caso $(1/3,\ 0{,}4)$, quindi la check cell stampa il segno di corretto, ma sul treebank dà **11,5% e 2,7%**, i numeri dell'output salvato. Quelli giusti sono **9,9% e 36,5%**: verificato rieseguendo la check cell con la funzione della cella 162 (ottengo esattamente 11,5% / 2,7%) e con la soluzione corretta dell'esercizio A2, e ricontando a mano con un `Counter`. Il 2,7% avrebbe dovuto insospettire: la Fig. 18.4 dice che le parole ambigue sono le più frequenti, quindi la quota sui token deve essere molto **più alta** di quella sui tipi. Un test che distingue le due funzioni: `[(\"a\",\"X\"),(\"a\",\"Y\"),(\"a\",\"X\"),(\"b\",\"Z\")]` deve dare $(0{,}5;\ 0{,}75)$.

### Notebook 4 · A3. La baseline most-frequent-tag

```python
# check A3 (excerpt)
mft = dict(train_mft(tb_train))
test_words = [[w for w, _ in s] for s in tb_test]
results = {"most frequent tag": [list(tag_mft(mft, ws)) for ws in test_words],
           "NLTK pos_tag": [[t for _, t in nltk.pos_tag(ws)] for ws in test_words],
           "spaCy en_core_web_sm": [[tok.tag_ for tok in d]
                for d in nlp_en.pipe(Doc(nlp_en.vocab, words=ws) for ws in test_words)]}
```

Output:

```text
   10.0% of the test tokens never occur in training

   tagger                               all   known  unknown
   most frequent tag                  87.0%   94.5%    19.0%
   NLTK pos_tag                       96.3%   97.1%    89.1%
   spaCy en_core_web_sm               95.4%   96.0%    90.3%

(bonus, with the rules of exercise A3)
   most frequent tag + NN             87.0%   94.5%    19.0%
   most frequent tag + your rules     92.8%   94.5%    77.1%

   the gold tags of the unknown words: {'NNP': 547, 'NN': 355, 'CD': 265, 'JJ': 219, 'NNS': 168, 'VBN': 73, 'VB': 56, 'VBG': 54}
```

La baseline della [scheda 20 della L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-20): a ogni parola il tag più frequente nel training, NN alle parole mai viste. Il libro dice circa 92%; qui **87,0%**. Risposte alle domande *Discuss*:

- **Dove perde?** Sulle parole **sconosciute**: 94,5% sulle note, 19,0% sulle ignote, che sono il 10% dei token di test (con un training di 75.385 token; il 92% del libro usa il WSJ completo, con molte meno parole ignote). Le ignote sono soprattutto NNP, CD, JJ, NNS: NN è il tag giusto solo per 355 su 1.867.
- **Quanto credere a 96,3% e 95,4%?** Il perceptron di NLTK è addestrato sul WSJ del Penn Treebank, spaCy su OntoNotes, che contiene anche testo WSJ: le nostre frasi di test sono quasi certamente nei loro dati di training. È contaminazione del test set ([scheda 27 della L4](L04-modelli-linguistici-n-gram.md#p-27)): i loro numeri sono ottimistici, la baseline invece è valutata onestamente su frasi mai viste. Per un confronto equo andrebbero tutti riaddestrati sullo stesso training.

Bonus: qualche regola su suffissi, maiuscole e cifre (le feature delle parole sconosciute della [scheda 77 della L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-77)) porta le ignote dal 19% al **77%** e il totale al **92,8%**, sopra il 92% del libro. È esattamente ciò che un CRF può usare e un HMM no.

### Notebook 5 · A4. Valutare la NER sugli span: spaCy contro NLTK

```python
SPACY_MAP = {"PERSON": "PER", "ORG": "ORG", "GPE": "LOC", "LOC": "LOC", "FAC": "LOC"}
NLTK_MAP = {"PERSON": "PER", "ORGANIZATION": "ORG", "GPE": "LOC", "LOCATION": "LOC", "GSP": "LOC", "FACILITY": "LOC"}

def bio_spacy(tokens):
    doc = nlp_en(Doc(nlp_en.vocab, words=tokens))
    return [f"{t.ent_iob_}-{SPACY_MAP[t.ent_type_]}" if t.ent_type_ in SPACY_MAP else "O" for t in doc]

def bio_nltk(tokens):
    triples = nltk.chunk.tree2conlltags(nltk.ne_chunk(nltk.pos_tag(tokens)))
    return [f"{b[0]}-{NLTK_MAP[b[2:]]}" if b != "O" and b[2:] in NLTK_MAP else "O" for _, _, b in triples]
```

Output:

```text
OK span extraction and span-level metrics work
   70% of the gold tokens are O (outside any entity)

spaCy  span P 0.65  R 0.72  F1 0.68   |   token-level BIO accuracy 89.5%
       false positives: iPhones/ORG, iPads/ORG, Mac/ORG, Pisa/ORG, the University of Padua/ORG, the University of Colorado/ORG, the Leaning Tower/LOC
       false negatives: Pisa/LOC, University of Padua/ORG, University of Colorado/ORG, Leaning Tower/LOC, Pisa/LOC
NLTK   span P 0.54  R 0.72  F1 0.62   |   token-level BIO accuracy 88.6%
       false positives: Apple/PER, Inc./ORG, iPhones/ORG, iPads/ORG, Mac/ORG, Apple/PER, University/ORG, Padua/LOC, University/ORG, Colorado/LOC, Leaning Tower/ORG
       false negatives: Apple Inc./ORG, Apple/ORG, University of Padua/ORG, University of Colorado/ORG, Leaning Tower/LOC
```

Il testo della NER di prima più qualche frase su Pisa, Galileo e il libro, con 18 entità gold PER/ORG/LOC; i due sistemi ricevono gli stessi token e le loro etichette sono mappate sui tre tipi (GPE e FAC diventano LOC; DATE, MONEY, PRODUCT sono ignorati). L'unità di valutazione è lo **span** (§18.6, [scheda 81 della L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-81)): uno span predetto è giusto solo se inizio, fine e tipo coincidono.

Il *Bet*: accuracy sui token 89,5% e 88,6%, ma F1 sugli span **0,68 e 0,62**. Perché l'accuracy per token inganna: il **70% dei token è O**, quindi un sistema che non trova nessuna entità ha già il 70%; e un errore di confine su uno span lungo lascia giusti quasi tutti i suoi token. È il problema delle classi sbilanciate della [scheda 24 della L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-24).

*the University of Padua* contro il gold *University of Padua*: un solo token di differenza costa **un falso positivo e un falso negativo**, cioè sia precision sia recall (lo stesso caso di *Jane* contro *Jane Villanueva* del libro). È giusto? La valutazione esatta è severa: l'entità è stata trovata e il tipo è giusto, e l'articolo è una convenzione di annotazione. Per questo si usano anche metriche "parziali" (sovrapposizione degli span), ma lo standard CoNLL resta il match esatto. Notare anche *Pisa*: spaCy la etichetta ORG in *was born in Pisa* e non la trova affatto in *the Leaning Tower in Pisa*. NLTK sbaglia di più sui confini (*Apple* / *Inc.* separati, *University* / *Padua* spezzati).

Nel file salvato l'output della check cell (stampe di debug, *got [(0, 3, 'PER'), (3, 1, 'LOC')]*) viene da una versione precedente della funzione, non dal codice presente nella cella 173: va ignorato.

### Notebook 6 · A5. Fuori dal dominio: spaCy legge Dante

```python
nlp_it = spacy.load("it_core_news_sm")
for text_ in [DANTE, MODERN]:
    print(text_)
    for tok in nlp_it(text_):
        print(f"   {tok.text:12s} {tok.pos_:6s} {tok.lemma_:12s} {tok.morph}")
```

Output:

```text
Nel mezzo del cammin di nostra vita mi ritrovai per una selva oscura, ché la diritta via era smarrita.
   cammin       NOUN   cammin       Gender=Masc
   ritrovai     VERB   ritrovaire   Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin
   ché          SCONJ  ché
   diritta      NOUN   diritta      Gender=Fem|Number=Sing
   via          ADV    via
   smarrita     VERB   smarrire     Gender=Fem|Number=Sing|Tense=Past|VerbForm=Part
   (other tokens correct)
```

Il terzetto iniziale della *Commedia* con il modello piccolo italiano, addestrato su italiano contemporaneo. Errori trovati (domanda 1):

- *ritrovai*: lemma inventato *ritrovaire* e morfologia *3a persona plurale, presente*; è la 1a singolare del passato remoto di *ritrovare*;
- *diritta via*: *diritta* NOUN e *via* ADV; sono aggettivo + nome;
- *cammin*: lemma *cammin* (forma tronca di *cammino*) e numero mancante.

Domanda 3, da dove vengono: ho riscritto solo l'ordine e le forme antiche (*cammino*, *perché*, *la via diritta*) lasciando *mi ritrovai*: *via* torna NOUN e *diritta* ADJ con lemma *diritto*, quindi l'errore su *diritta via* veniva dall'**ordine delle parole** (aggettivo prima del nome); *cammin* era una **forma antica**. *ritrovai* invece resta sbagliato anche in prosa moderna (e così *trovai → trovaire*): il passato remoto di 1a persona è raro nei dati di training (giornalistici) e il modello piccolo non lo sa analizzare. Non tutti gli errori su Dante sono "colpa di Dante". Domanda 2: una parafrasi con il passato prossimo (*mi sono ritrovato*) è etichettata tutta correttamente (soluzione A5 nella sezione studio); ma una parafrasi con *un bosco buio* dà *bosco* e *buio* PROPN: anche l'italiano moderno ha i suoi errori.

> **Attenzione (errore nelle slide): Dante non scende al 56%**
>
> Il markdown della cella 176 dice *tagging accuracy drops by 15-40 points ... (Dante: down to ~56-75%)*. Nel grafico della [scheda 21 della L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-21) Dante è al **75,0%** (da 97,0 sulle news, 22 punti in meno); il 56,2% è il **Middle English** (inglese medievale, da 97,3 sul WSJ, 41 punti in meno). La forbice 56-75% è quella di tutti i domini lontani del grafico, non di Dante.

### Notebook 7 · B1. Le feature della Fig. 4.2 con un lessico vero

```python
FIG42_DOC = ("It's hokey. There are virtually no surprises, and the writing is second-rate. "
             "So why was it so enjoyable? For one thing, the cast is great. Another nice touch "
             "is the music. I was overcome with the urge to get off the couch and start dancing. "
             "It sucked me in, and it'll do the same to you.")
VADER_LEXICON = SentimentIntensityAnalyzer().lexicon
PRONOUNS_12 = {"i", "me", "my", "mine", "myself", "we", "us", "our", "ours", "ourselves",
               "you", "your", "yours", "yourself", "yourselves"}
W_BOOK, B_BOOK = np.array([2.5, -5.0, -1.2, 0.5, 2.0, 0.7]), 0.1
X_BOOK = np.array([3, 2, 1, 3, 0, 4.19])
```

Output:

```text
OK your x = [4, 2, 1, 3, 0, 4.22]   book's x = [3, 2, 1, 3, 0, 4.19]
   positive for VADER: ['surprises', 'enjoyable', 'great', 'nice']
   negative for VADER: ['no', 'sucked']
   P(+|x) with the book's weights: book's x -> 0.70,   your x -> 0.97
```

La recensione della Fig. 4.2 (§4.3.1), già vista nella [scheda 26](L06-regressione-logistica.md#p-26) e nella [scheda 27 della L6](L06-regressione-logistica.md#p-27), ora con un estrattore di feature vero: `word_tokenize`, minuscole, lessico VADER. Il vettore cambia da $[3, 2, 1, 3, 0, 4{,}19]$ a $[4, 2, 1, 3, 0, 4{,}22]$ e, con gli stessi pesi del libro, $P(+\mid x)$ sale da $\sigma(0{,}833) = 0{,}70$ a $\sigma(3{,}354) = 0{,}97$ (un'unità in più su $x_1$ vale $+2{,}5$ nel logit). Risposte alle domande *Discuss*:

- **Lessico**: VADER conta come positive *surprises* (0,9), *enjoyable, great, nice*; come negative *no* (−1,2) e *sucked*. Non conosce *hokey* e *second-rate*, le due negative del libro. *surprises* qui è negativo (*virtually no surprises*), e *sucked* è positivo (*It sucked me in*, mi ha coinvolto): un lessico non vede il contesto.
- **68 token invece di 66**: `word_tokenize` separa i clitici, *It's* → `It``'s` e *it'll* → `it``'ll`, due token in più (convenzione Penn Treebank, [scheda 30 della L3](L03-elaborazione-del-testo.md#p-30)); $\ln 68 = 4{,}22$.
- **Pesi ed estrattore vanno insieme**: i pesi sono stati stimati per *quelle* feature calcolate in *quel* modo. Cambiare tokenizzatore o lessico dopo il training sposta la distribuzione delle feature e il classificatore non è più calibrato, senza alcun errore visibile: le predizioni cambiano in silenzio. Il modello va riaddestrato con il nuovo estrattore (è quello che fa B2).

### Notebook 8 · B2. Precision, recall, F1 e quattro classificatori di sentiment

```python
mr_ids = movie_reviews.fileids()                                # 1000 pos + 1000 neg
mr_raw = [movie_reviews.raw(f) for f in mr_ids]
mr_tok = [list(movie_reviews.words(f)) for f in mr_ids]          # tokenized, lowercased
mr_y = np.array([1 if f.startswith("pos") else 0 for f in mr_ids])
idx_train, idx_test = train_test_split(np.arange(len(mr_ids)), test_size=0.2,
                                       random_state=0, stratify=mr_y)

def bow_classifier(docs_tokens):
    vec = CountVectorizer(analyzer=lambda toks: toks, binary=True)   # binary bag of words
    X = vec.fit_transform(docs_tokens)
    clf = LogisticRegression(max_iter=2000).fit(X[idx_train], y_train)
    return clf, vec, clf.predict(X[idx_test])

predictions = {"VADER (rules)": np.array([int(sia.polarity_scores(mr_raw[i])["compound"] >= 0) for i in idx_test])}
X6 = np.array([extract_features(t) for t in mr_raw])
clf6 = LogisticRegression(max_iter=1000).fit(X6[idx_train], y_train)
```

Output:

```text
OK metrics agree with sklearn.  Spam example (textbook ex. 4.2): precision 0.800, recall 0.600, f1 0.686, accuracy 0.978;  a classifier that never says spam: accuracy 0.960, F1 0.000

1600 training and 400 test reviews, 792 tokens per review on average
bag of words: 39,768 features

system                        P      R     F1    acc   predicted positive
VADER (rules)             0.615  0.855  0.715  0.660    69.5%
LR 6 features (B1)        0.709  0.720  0.715  0.713    50.7%
LR bag of words           0.848  0.895  0.871  0.868    52.8%
DistilBERT SST-2          0.917  0.775  0.840  0.853    42.2%

pushes towards POSITIVE: fun, memorable, others, both, hilarious, true, very, sometimes, performances, well, terrific, overall, wonderfully, perfectly, many
pushes towards NEGATIVE: worst, bad, supposed, nothing, waste, script, maybe, awful, plot, unfortunately, mess, lame, ridiculous, poor, wasted

weights of the 6-feature model: {'x1 pos': 0.057, 'x2 neg': -0.053, 'x3 no': -0.388, 'x4 pron': -0.026, 'x5 !': -0.38, 'x6 ln len': 0.402}
```

Il corpus **movie\_reviews** (Pang e Lee): 2.000 recensioni lunghe (792 token in media), bilanciate; 1.600 per il training e 400 per il test, divisione stratificata. Quattro sistemi valutati con la propria `prf` (§4.9, [scheda 25](L07-regressione-logistica-multinomiale-e-valutazione.md#p-25) e [scheda 27 della L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-27)). La check cell usa anche l'esercizio 4.2 del libro (spam): accuracy 0,978 ma F1 0,686, e un classificatore che non dice mai spam ha accuracy 0,96 e F1 0. DistilBERT (bonus, cella 193) ha richiesto circa 100 secondi su CPU.

Risposte alle domande *Discuss*:

- **VADER dice "positivo" al 69,5%** delle recensioni (metà sono positive): recall alta (0,855), **precision** bassa (0,615), ed è la precision (con l'accuracy 0,66) a rivelarlo; la recall da sola lo nasconde. Su testi lunghi le parole positive tendono a prevalere anche nelle stroncature, e la soglia è compound $\ge 0$.
- **Peso piccolo di $x_1$** (0,057): $x_1$ e $x_2$ sono **conteggi**, quindi crescono con la lunghezza della recensione: sul corpus la correlazione con $x_6$ è 0,80 per $x_1$ e 0,72 per $x_2$, e 0,55 fra loro. Una recensione lunga ha molte parole positive *e* molte negative; l'informazione utile è nella loro differenza (pesi quasi opposti, +0,057 e −0,053), che a parità di lunghezza è piccola rispetto alle variazioni dovute alla lunghezza stessa. La regressione logistica di scikit-learn è anche regolarizzata L2 per default ($C = 1$, [scheda 56 della L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-56)), che schiaccia pesi ridondanti. Con feature non normalizzate per la lunghezza (meglio sarebbero le proporzioni) le sei feature arrivano solo a 0,713.
- **Bag of words vince** (F1 0,871): ha 39.768 feature, una per parola, e impara dai dati quali contano, anche parole che nessun lessico di sentiment contiene. Non tutte riguardano il sentiment: *both, others, many, sometimes* da una parte, *supposed, script, plot, maybe* dall'altra sono indizi di **stile** delle recensioni positive e negative di questo corpus (chi stronca un film parla della trama e di cosa *avrebbe dovuto* essere). Funzionano qui, ma potrebbero non generalizzare: è la lettura dei pesi della §4.13 ([scheda 52 della L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-52)).
- **DistilBERT** (mai visto queste recensioni) arriva a F1 0,840, vicino al bag of words, con un profilo opposto a VADER: precision alta, recall bassa (predice positivo solo il 42,2%). Legge solo i primi 512 token: in recensioni lunghe il giudizio finale spesso viene tagliato.

### Notebook 9 · B3. La differenza è significativa?

```python
# given cell 197 (excerpt)
correct = {name: [int(p == t) for p, t in zip(pred, y_test)] for name, pred in predictions.items()}
for a, b_ in pairs:
    if acc[a] < acc[b_]:
        a, b_ = b_, a                      # A is the classifier with the higher accuracy
    d, p = paired_bootstrap(correct[a], correct[b_], b=10000, seed=0)
```

Output:

```text
OK example of the book (10 documents): delta = 0.20, p = 0.269, not significant;  exercise 11 of L07 (5 documents): delta = 0.40, p = 0.215

A                      B                       acc A  acc B   delta  reviews  p-value   significant at .05?
LR bag of words        VADER (rules)           0.868  0.660   0.207       83   0.0000   yes
LR bag of words        LR 6 features (B1)      0.868  0.713   0.155       62   0.0000   yes
LR bag of words        DistilBERT SST-2        0.868  0.853   0.015        6   0.2698   no
LR 6 features (B1)     VADER (rules)           0.713  0.660   0.052       21   0.0265   yes
```

Il **paired bootstrap** della §4.11 ([scheda 44](L07-regressione-logistica-multinomiale-e-valutazione.md#p-44) e [scheda 47 della L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-47)), sull'accuracy. Due dettagli della consegna che contano: il campionamento è **appaiato** (si estraggono recensioni, ognuna porta il risultato di A e di B), e il confronto $\delta(x^{(i)}) \ge 2\delta(x)$ va fatto con **maggiore o uguale** e su **conteggi interi**. Con il maggiore stretto, sull'esempio del libro si ottiene $p \approx 0{,}145$ invece di 0,27 (verificato): i pareggi esatti sono frequenti con 10 documenti. La check cell riconosce proprio questo errore.

Risposte alle domande *Discuss*:

- Significative a 0,05: bag of words contro VADER (83 recensioni di differenza) e contro le sei feature (62), e anche sei feature contro VADER (21 recensioni, $p = 0{,}027$). **Non** significativa bag of words contro DistilBERT: 6 recensioni su 400, $p = 0{,}27$.
- Un $p &gt; 0{,}05$ **non dimostra** che i due classificatori siano ugualmente buoni: dice solo che con 400 recensioni non possiamo escludere che la differenza sia dovuta al caso ([scheda 43 della L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-43)). Per decidere servono più dati di test, o la cross-validation sull'intero corpus ([scheda 34](L07-regressione-logistica-multinomiale-e-valutazione.md#p-34)), che usa tutte le 2.000 recensioni come test a turno.
- Su recensioni di un altro sito mi aspetto che **DistilBERT** regga meglio: il bag of words ha imparato anche lo stile di *questo* corpus (*script, supposed, both*), mentre DistilBERT è stato addestrato su un altro dataset ed è già "fuori dominio" qui, eppure è quasi alla pari. È di nuovo il problema del dominio della parte A.

## Studio ed esercizi

### Guida allo studio (circa 4 h 40 min)

**Parte NLTK: dal testo ai conteggi** (50 min)

Notebook parte 1 (celle 1-89). Saper spiegare: perché il testo Gutenberg contiene una licenza e che effetto ha; Punkt e `word_tokenize` (convenzioni PTB, clitici, apostrofo tipografico) e il confronto 3.9/3.10; `FreqDist`, tipi e istanze; concordanza case-insensitive (457 contro 451); stopword; **PMI** con il conto a mano di *Talking Cricket* e il limite $\log_2 N$; bag of words, bigrammi, n-grammi di caratteri. Esercizi 9, 10, 11. Ripasso collegato: L2 (corpora, tipi e istanze), L3 (schede 30-34), L4 (MLE, scheda 13). Libro §2.5 e §2.8.

**Sentiment: VADER e un transformer** (35 min)

Notebook parte 2, celle 90-114. Rifare a mano il compound della recensione d'esempio (0,6996) e i tre punteggi neg/neu/pos, capire perché non sono percentuali di testo e perché $(\text{compound}+1)/2$ non è una probabilità; l'effetto delle stopword (*very*, *not*); che cosa fa la `pipeline` di Hugging Face e perché DistilBERT dà NEGATIVE sulla stessa recensione. Esercizio 12. Collegamenti: L6 (schede 26-28, feature di sentiment e $P(+\mid x)$). Facoltativo: J&M cap. 23 (lessici per il sentiment).

**spaCy: pipeline, dipendenze, NER** (35 min)

Notebook parte 2, celle 115-151. Componenti della pipeline `en_core_web_sm`; attributi dei token (`lemma_`, `pos_` UD e `tag_` Penn, `dep_`, `shape_`); leggere un albero a dipendenze (nsubj, dobj, advcl, ROOT); noun chunk; NER con spaCy e con `ne_chunk` di NLTK, errori tipici (prodotti come ORG, span spezzati). Collegamenti: L8 (schede 10, 12, 59-64, 75-77), L1 (scheda 44).

**Esercizi parte A: PoS tagging e NER** (70 min)

Notebook parte 3, esercizi A1-A5: scrivere da soli `ambiguity_stats`, `train_mft`/`tag_mft`/`tag_accuracy`, `guess_unknown`, `bio_to_spans`, `span_prf` e farli passare le check cell; poi confrontare con le soluzioni. Attenzione alla check cell di A2 (troppo debole). Esercizio 13 a mano. Libro §18.1-18.3 (Fig. 18.4, baseline 92%) e §18.6. Ripasso L8 schede 17-21 e 81.

**Esercizi parte B: classificazione e significatività** (60 min)

Esercizi B1-B3: `extract_features`, `confusion`/`prf`, `paired_bootstrap`; leggere la tabella dei quattro classificatori e i test di significatività, saper rispondere alle domande *Discuss*. Rifare a mano $z = 3{,}354$ della Fig. 4.2 con il lessico VADER e le metriche dell'esercizio 4.2 del libro. Libro §4.3.1, §4.9-4.11, §4.13. Ripasso L7 schede 25-27 e 44-47.

**Ripasso orale** (30 min)

Rispondere ad alta voce alle domande della sezione orale senza guardare la traccia, con almeno un numero del laboratorio per risposta (PMI 10,5 bit, 87% della baseline, F1 0,68 contro accuracy 89,5%, $p = 0{,}27$). Rieseguire il notebook con NLTK 3.9 per ritrovare gli stessi numeri.

### Esercizi

#### Esercizio A1 (notebook L09): far litigare i due tagger

Scrivi una lista `my_sentences` di almeno tre frasi inglesi su cui il tagger di NLTK (`nltk.pos_tag`) e quello di spaCy (`en_core_web_sm`, sugli stessi token) assegnano tag Penn Treebank diversi ad almeno una parola. Per ogni disaccordo decidi chi ha ragione (a volte nessuno dei due). Idee: *that, down, put, set*; *I saw her duck*; frasi garden-path; titoli di giornale.

<details><summary>Soluzione</summary>

```
my_sentences = [
    "I saw her duck.",
    "The old man the boat.",
    "Police help dog bite victim.",
    "Put that down and set the table.",
    "Time flies like an arrow; fruit flies like a banana.",
]
```

La check cell stampa 4 frasi su 5 in disaccordo. Analisi, con i tag completi dei due sistemi:

- *I saw her duck.* Entrambi: *duck* NN. NLTK: *her* PRP, spaCy: PRP\$. La frase ha due letture: *her* PRP\$ + *duck* NN (ho visto la sua anatra) oppure *her* PRP + *duck* VB (l'ho vista abbassarsi). spaCy è coerente con la prima; NLTK mescola le due (PRP seguito da un nome), quindi sbaglia.
- *The old man the boat.* Nessun disaccordo, ma entrambi sbagliano: la lettura grammaticale è *the old* (gli anziani, soggetto) *man* VBP (manovrano) *the boat*. È una garden-path: il contesto locale spinge verso *man* NN.
- *Police help dog bite victim.* *Police*: NLTK NNP (per la maiuscola), spaCy NNS: giusto NNS (nome plurale). *help*: NLTK NN, spaCy VBP: giusto VBP nella lettura sensata (la polizia aiuta la vittima del morso). Ragione a spaCy.
- *Put that down and set the table.* *down*: NLTK NN, spaCy RP. È la particella del phrasal verb *put down*: RP, ragione a spaCy (come *buy back* nella tabella di *back*).
- *Time flies like an arrow; fruit flies like a banana.* *Time*: NNP (NLTK) contro NN (spaCy): NN. Primo *flies*: NNS contro VBZ: VBZ. *fruit*: NLTK CC (assurdo, una congiunzione), spaCy NN. Nella seconda metà entrambi danno *flies* NNS e *like* IN, ma la lettura giusta è *fruit flies* (moscerini) soggetto e *like* VBP (amano): sbagliano tutti e due.

Morale: i disaccordi cadono sulle parole ambigue fra classi aperte e sulle frasi dove la lettura giusta richiede di capire il senso, non solo il contesto locale ([scheda 19 della L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-19)).

</details>

#### Esercizio A2 (notebook L09): quanto è ambiguo l'inglese

Scrivi `ambiguity_stats(tagged_words)`: riceve una lista di coppie `(parola, tag)`, una per token, e restituisce `(frac_ambiguous_types, frac_ambiguous_tokens)`. Un tipo è ambiguo se compare con almeno 2 tag diversi; la prima frazione è tipi ambigui / tipi, la seconda è token il cui tipo è ambiguo / token. Maiuscole e minuscole distinte. Esempio: `[("the","DT"),("back","NN"),("back","RB"),("the","DT"),("dog","NN")]` → $(0{,}333;\ 0{,}4)$. Poi spiega perché sul campione del treebank le percentuali sono più basse di quelle del libro (14% e 55%).

<details><summary>Soluzione</summary>

```
def ambiguity_stats(tagged_words):
    """Input: a list of (word, tag) pairs. Output: (frac_ambiguous_types, frac_ambiguous_tokens)."""
    tags_of = {}                                  # word -> set of the tags it appears with
    for word, tag in tagged_words:
        tags_of.setdefault(word, set()).add(tag)
    ambiguous = {w for w, tags in tags_of.items() if len(tags) >= 2}
    frac_types = len(ambiguous) / len(tags_of)
    frac_tokens = sum(1 for word, _ in tagged_words if word in ambiguous) / len(tagged_words)
    return frac_types, frac_tokens
```

Due passate: la prima costruisce per ogni parola l'**insieme** dei suoi tag (un insieme, così un tag ripetuto non conta due volte), la seconda conta i token il cui tipo ha almeno due tag. Esempio: tipi *the* {DT}, *back* {NN, RB}, *dog* {NN}: 1 ambiguo su 3; token di *back*: 2 su 5.

Sul campione (94.084 token): **9,9% dei tipi, 36,5% dei token** (libro, WSJ completo: 14% e 55%). Le parole ambigue sono le frequenti (*the, a, set, back, hit*), per questo la quota sui token è molto più alta di quella sui tipi. Il campione dà numeri più bassi perché l'ambiguità si **osserva** solo se una parola compare abbastanza volte da mostrare i suoi diversi tag: con il 10% del corpus molte parole compaiono una volta sola e sembrano non ambigue. Nota: la funzione salvata nel notebook (cella 162) passa la check cell ma dà 11,5% e 2,7%, numeri sbagliati (riquadro nel blocco A2 del notebook).

</details>

#### Esercizio A3 (notebook L09): la baseline most-frequent-tag (con bonus)

Scrivi `train_mft(tagged_sents)` (dizionario parola → tag più frequente nel training), `tag_mft(model, words, unk_tag="NN")` (un tag per parola, `unk_tag` per le parole sconosciute) e `tag_accuracy(gold_sents, pred_tags)` (frazione di **token** corretti). Bonus: `guess_unknown(word)`, regole per le parole mai viste. Rispondi: dove perde la baseline? Che cosa significa che NLTK e spaCy sono addestrati su testo WSJ?

<details><summary>Soluzione</summary>

```
def train_mft(tagged_sents):
    """Input: a list of sentences, each a list of (word, tag). Output: a dict {word: most frequent tag}."""
    counts = {}                                   # word -> {tag: count}
    for sent in tagged_sents:
        for word, tag in sent:
            counts.setdefault(word, {})
            counts[word][tag] = counts[word].get(tag, 0) + 1
    return {word: max(tc, key=tc.get) for word, tc in counts.items()}

def tag_mft(model, words, unk_tag="NN"):
    """Input: the dict of train_mft, a list of words. Output: a list of tags, one per word."""
    return [model.get(w, unk_tag) for w in words]

def tag_accuracy(gold_sents, pred_tags):
    """Fraction of tokens whose predicted tag equals the gold tag."""
    right = total = 0
    for sent, preds in zip(gold_sents, pred_tags):
        for (_, gold), pred in zip(sent, preds):
            right += (gold == pred)
            total += 1
    return right / total if total else 0.0
```

`max(tc, key=tc.get)` sceglie il tag con il conteggio massimo; `model.get(w, unk_tag)` gestisce le parole ignote senza `KeyError`; l'accuracy si accumula sui token di tutte le frasi (non si fa la media delle accuracy per frase, che darebbe lo stesso peso a frasi corte e lunghe). Sull'esempio della consegna: *book* ha NN due volte e VBP una, quindi NN; `tag_accuracy` dà 2/3.

Bonus:

```
def guess_unknown(word):
    """Input: a word never seen in training. Output: a Penn Treebank tag."""
    w = word.replace(",", "").replace(".", "", 1)
    if w.isdigit() or (w[:1].isdigit() and "-" not in word):
        return "CD"                               # 1987, 3.5, 1,200
    if word[0].isupper():
        return "NNP"                              # Rossi, Vinken
    if "-" in word:
        return "JJ"                               # once-in-a-lifetime, well-known
    if word.endswith("ing"):
        return "VBG"
    if word.endswith("ed"):
        return "VBN"
    if word.endswith("ly"):
        return "RB"
    if word.endswith(("ous", "ive", "able", "ible", "al", "ful", "ic", "less")):
        return "JJ"
    if word.endswith("s") and not word.endswith("ss"):
        return "NNS"
    return "NN"
```

Risultati sul test (783 frasi, 18.699 token, il 10% mai visto nel training):

| tagger | tutti | noti | ignoti |
| --- | --- | --- | --- |
| most frequent tag + NN | 87,0% | 94,5% | 19,0% |
| most frequent tag + regole | 92,8% | 94,5% | 77,1% |
| NLTK pos\_tag | 96,3% | 97,1% | 89,1% |
| spaCy en\_core\_web\_sm | 95,4% | 96,0% | 90,3% |

La baseline perde soprattutto sulle parole **ignote** (19%: NN è giusto solo per 355 delle 1.867 ignote, che sono in maggioranza NNP, CD, JJ, NNS). Le regole su maiuscola, cifre, trattino e suffissi la portano al 92,8%, oltre il 92% del libro: sono le feature di forma e suffisso che un CRF può usare e un HMM no ([scheda 77 della L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-77)). I tagger di NLTK e spaCy sono addestrati su dati che contengono il WSJ, quindi probabilmente anche le nostre frasi di test: i loro numeri sono gonfiati dalla **contaminazione** ([scheda 27 della L4](L04-modelli-linguistici-n-gram.md#p-27)), mentre la baseline è valutata su frasi davvero nuove. Il confronto non è alla pari.

</details>

#### Esercizio A4 (notebook L09): dal BIO agli span, precision e recall sugli span

Scrivi `bio_to_spans(tags)`, che da una lista di tag BIO restituisce l'insieme degli span `(start, end, type)` con `end` escluso (come lo slicing Python); un `I-X` che non continua uno span di tipo X ne apre uno nuovo (convenzione `conlleval`). Poi `span_prf(gold_spans, pred_spans)` → `(precision, recall, f1)` con match esatto, 0 se un denominatore è 0. Esempio: gold {(0,2,PER), (3,4,LOC)}, pred {(0,2,PER), (3,5,LOC), (6,7,ORG)} → (0,333; 0,5; 0,4). Rispondi: perché l'accuracy sui token inganna? Quanto costa *the University of Padua* contro *University of Padua*?

<details><summary>Soluzione</summary>

```
def bio_to_spans(tags):
    """Input: a list of BIO tags. Output: a set of (start, end, type), end exclusive."""
    spans = set()
    start, typ = None, None                       # the span that is currently open
    for i, tag in enumerate(tags):
        prefix, _, label = tag.partition("-")
        continues = prefix == "I" and start is not None and label == typ
        if start is not None and not continues:   # the open span ends before token i
            spans.add((start, i, typ))
            start, typ = None, None
        if prefix == "B" or (prefix == "I" and not continues):
            start, typ = i, label                 # B-X, or a stray I-X (conlleval), opens a span
    if start is not None:                         # span still open at the end
        spans.add((start, len(tags), typ))
    return spans

def span_prf(gold_spans, pred_spans):
    """Input: two sets of spans. Output: (precision, recall, f1)."""
    tp = len(set(gold_spans) & set(pred_spans))
    p = tp / len(pred_spans) if pred_spans else 0.0
    r = tp / len(gold_spans) if gold_spans else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f
```

Il ciclo tiene aperto al più uno span (`start`, `typ`). A ogni tag: se c'è uno span aperto e il tag non è un `I-` dello stesso tipo, lo span si chiude **prima** del token corrente (`end = i`); poi un `B-X`, o un `I-X` che non continua nulla, apre un nuovo span. Alla fine si chiude lo span ancora aperto (`end = len(tags)`): è il caso `["O", "B-ORG"]` → {(1, 2, ORG)} che la check cell verifica. Due `B-PER` consecutivi danno due span distinti. La sequenza malformata `["O","I-PER","I-PER","B-LOC","I-ORG"]` dà {(1,3,PER), (3,4,LOC), (4,5,ORG)}.

Esempio della consegna: $tp = 1$ (solo (0,2,PER)), $P = 1/3$, $R = 1/2$, $F_1 = 2\cdot\frac13\cdot\frac12/(\frac13+\frac12) = 0{,}4$. La check cell passa con tutti i casi, compreso quello senza span gold (nessuna divisione per zero).

Sul testo dell'esercizio: spaCy $P = 0{,}65$, $R = 0{,}72$, $F_1 = 0{,}68$; NLTK $0{,}54$, $0{,}72$, $0{,}62$; accuracy sui token 89,5% e 88,6%. L'accuracy per token inganna perché il 70% dei token è O (un sistema che non trova nulla ha già il 70%) e un errore di confine sbaglia uno o due token ma tutto lo span. *the University of Padua* contro *University of Padua*: un falso positivo (lo span predetto non esiste nel gold) e un falso negativo (lo span gold non è trovato), quindi peggiorano sia $P$ sia $R$. È severo (entità e tipo sono giusti, l'articolo è una scelta di annotazione), ma è lo standard del match esatto ([scheda 81 della L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-81)).

</details>

#### Esercizio A5 (notebook L09): spaCy legge Dante

Esegui `it_core_news_sm` sul terzetto *Nel mezzo del cammin di nostra vita / mi ritrovai per una selva oscura, / ché la diritta via era smarrita* e (1) trova almeno tre errori di PoS, lemma o morfologia; (2) riscrivi il terzetto in prosa moderna nella stringa `MODERN` e rietichettalo: gli errori spariscono? (3) Quali errori vengono da forme antiche e quali dall'ordine delle parole?

<details><summary>Soluzione</summary>

```
DANTE = ("Nel mezzo del cammin di nostra vita mi ritrovai per una selva oscura, "
         "ché la diritta via era smarrita.")
MODERN = ("A metà della nostra vita mi sono ritrovato in una selva oscura, "
          "perché la strada giusta era perduta.")
```

(1) Errori su Dante: *ritrovai* con lemma inesistente *ritrovaire* e morfologia *Person=3, Number=Plur, Tense=Pres* (è 1a singolare del passato remoto di *ritrovare*); *diritta* NOUN e *via* ADV (sono ADJ + NOUN); *cammin* con lemma *cammin* (forma tronca di *cammino*) e senza numero.

(2) La versione moderna qui sopra è etichettata tutta correttamente: *sono* AUX, *ritrovato* VERB con lemma *ritrovare*, *strada* NOUN, *giusta* ADJ lemma *giusto*, *perduta* VERB lemma *perdere*. Ma non è merito solo della modernità: con *mi trovai in un bosco buio* il modello dà *trovai → trovaire* e *bosco*, *buio* PROPN.

(3) Esperimento di controllo: cambiando solo *cammin → cammino*, *ché → perché*, *la diritta via → la via diritta* e lasciando *mi ritrovai*, *via* diventa NOUN e *diritta* ADJ (lemma *diritto*): l'errore su *diritta via* dipendeva dall'**ordine delle parole** (aggettivo anteposto); quello su *cammin* dalla **forma antica**. L'errore su *ritrovai* resta: dipende dal **passato remoto**, raro nel testo giornalistico di training, non da Dante. Collegamento: il calo di accuratezza fuori dominio della [scheda 21 della L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-21) (Dante al 75%) è una somma di cause diverse.

</details>

#### Esercizio B1 (notebook L09): le sei feature della Fig. 4.2 con il lessico VADER

Scrivi `extract_features(text)` → `[x1, ..., x6]`: tokenizza con `nltk.word_tokenize` e metti in minuscolo; $x_1$/$x_2$ = numero di token con valenza VADER positiva/negativa (`VADER_LEXICON.get(t, 0)`); $x_3$ = 1 se c'è *no*; $x_4$ = numero di pronomi di 1a e 2a persona (`PRONOUNS_12`); $x_5$ = 1 se c'è *!*; $x_6$ = logaritmo naturale del numero di token. Esempio: *No! You and I loved it, my friend.* → $[2, 1, 1, 3, 1, 2{,}398]$. Confronta con il vettore del libro $[3, 2, 1, 3, 0, 4{,}19]$ e con $P(+\mid x)$.

<details><summary>Soluzione</summary>

```
def extract_features(text):
    """Input: text, a string. Output: the list [x1, x2, x3, x4, x5, x6]."""
    toks = [t.lower() for t in nltk.word_tokenize(text)]
    x1 = sum(1 for t in toks if VADER_LEXICON.get(t, 0) > 0)    # positive lexicon tokens
    x2 = sum(1 for t in toks if VADER_LEXICON.get(t, 0) < 0)    # negative lexicon tokens
    x3 = 1 if "no" in toks else 0
    x4 = sum(1 for t in toks if t in PRONOUNS_12)
    x5 = 1 if "!" in toks else 0
    x6 = math.log(len(toks))
    return [x1, x2, x3, x4, x5, x6]
```

Esempio della consegna: 11 token `['no','!','you','and','i','loved','it',',','my','friend','.']`; positivi *loved* (2,9) e *friend* (2,2), negativo *no* (−1,2); *no* presente, pronomi *you, i, my*, *!* presente, $\ln 11 = 2{,}398$. Sul documento della Fig. 4.2: $[4, 2, 1, 3, 0, \ln 68 = 4{,}22]$ (VADER conta anche *surprises* come positiva, *no* e *sucked* come negative, e ignora *hokey* e *second-rate*; i clitici *'s* e *'ll* sono token separati: 68 invece di 66).

Con i pesi del libro: $z = 2{,}5\cdot 4 - 5\cdot 2 - 1{,}2\cdot 1 + 0{,}5\cdot 3 + 2\cdot 0 + 0{,}7\cdot 4{,}22 + 0{,}1 = 3{,}354$, $\sigma(3{,}354) = 0{,}97$ contro $\sigma(0{,}833) = 0{,}70$ del libro. Stessi pesi, estrattore diverso, probabilità molto diversa: i pesi hanno senso solo con l'estrattore con cui sono stati addestrati.

</details>

#### Esercizio B2 (notebook L09): confusione, precision, recall, F1

Scrivi, senza `sklearn.metrics`, `confusion(y_true, y_pred)` → `(tp, fp, fn, tn)` per etichette 0/1, e `prf(y_true, y_pred)` → dizionario con `precision`, `recall`, `f1`, `accuracy`, con 0 quando un denominatore è 0. Esempio: `y_true = [1,1,0,0,1]`, `y_pred = [1,0,1,0,1]` → (2,1,1,1) e $P = R = F_1 = 0{,}667$, accuracy 0,6. Poi interpreta la tabella dei quattro classificatori.

<details><summary>Soluzione</summary>

```
def confusion(y_true, y_pred):
    """(tp, fp, fn, tn) for labels 0/1."""
    tp = fp = fn = tn = 0
    for t, p in zip(y_true, y_pred):
        if p == 1:
            if t == 1: tp += 1
            else:      fp += 1
        else:
            if t == 1: fn += 1
            else:      tn += 1
    return tp, fp, fn, tn

def prf(y_true, y_pred):
    tp, fp, fn, tn = confusion(y_true, y_pred)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (tp + tn) / (tp + fp + fn + tn) if tp + fp + fn + tn else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, "accuracy": accuracy}
```

Esempio: posizioni (1,1) tp, (1,0) fn, (0,1) fp, (0,0) tn, (1,1) tp: $(2, 1, 1, 1)$; $P = 2/3$, $R = 2/3$, $F_1 = 2/3$, accuracy $3/5$. Esercizio 4.2 del libro (1.000 email, 40 spam, 30 etichettate spam di cui 24 vere): $tp = 24$, $fp = 6$, $fn = 16$, $tn = 954$; $P = 0{,}8$, $R = 0{,}6$, $F_1 = 0{,}686$, accuracy 0,978. Un classificatore che non dice mai spam ha accuracy 0,96 e $F_1 = 0$ ([scheda 26 della L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-26)). La check cell confronta anche con scikit-learn su 5 vettori casuali: coincide.

| sistema | P | R | F1 | acc | % positivi predetti |
| --- | --- | --- | --- | --- | --- |
| VADER (regole) | 0,615 | 0,855 | 0,715 | 0,660 | 69,5% |
| LR, 6 feature | 0,709 | 0,720 | 0,715 | 0,713 | 50,7% |
| LR, bag of words | 0,848 | 0,895 | 0,871 | 0,868 | 52,8% |
| DistilBERT SST-2 | 0,917 | 0,775 | 0,840 | 0,853 | 42,2% |

VADER sbilanciato verso "positivo" (precision bassa, recall alta); le sei feature limitate (conteggi correlati con la lunghezza, pesi quasi nulli su $x_1$ e $x_2$); il bag of words vince perché impara 39.768 pesi dai dati, compresi indizi di stile non di sentiment (*script, supposed, both*); DistilBERT, mai addestrato su questo corpus, è vicino al bag of words con precision alta e recall bassa.

</details>

#### Esercizio B3 (notebook L09): paired bootstrap test

Scrivi `paired_bootstrap(correct_a, correct_b, b=10000, seed=0)` → `(delta, p_value)`: `correct_a` e `correct_b` sono liste 0/1 (1 = il classificatore ha indovinato quella recensione), `delta` = accuracy di A meno accuracy di B, il p-value è la frazione di $b$ test set virtuali (estratti con reinserimento, appaiati) con $\delta(x^{(i)}) \ge 2\delta(x)$. Sull'esempio del libro (Fig. 4.11, A giusto 7 volte su 10, B 5) deve dare $\delta = 0{,}2$ e $p \approx 0{,}27$. Interpreta i test fra i quattro classificatori.

<details><summary>Soluzione</summary>

```
def paired_bootstrap(correct_a, correct_b, b=10000, seed=0):
    """(delta, p_value) of the paired bootstrap test, A minus B."""
    rng = random.Random(seed)
    n = len(correct_a)
    delta_count = sum(correct_a) - sum(correct_b)     # n * delta(x), an integer
    hits = 0
    for _ in range(b):
        idx = [rng.randrange(n) for _ in range(n)]    # n reviews, with replacement
        d_i = sum(correct_a[j] - correct_b[j] for j in idx)   # same reviews for A and B
        if d_i >= 2 * delta_count:
            hits += 1
    return delta_count / n, hits / b
```

Punti chiave: (1) **appaiato**: si estrae un indice di recensione e si prendono i risultati di A e B su quella stessa recensione; (2) **con reinserimento**, $n$ estrazioni; (3) il confronto è fatto su **conteggi interi** (`delta_count` = $n\,\delta(x)$), così $\delta(x^{(i)}) \ge 2\delta(x)$ non soffre di arrotondamenti in virgola mobile; (4) **maggiore o uguale**: con il maggiore stretto il p-value dell'esempio scende a circa 0,145, perché i pareggi esatti sono frequenti. Risultati: esempio del libro $\delta = 0{,}2$, $p = 0{,}269$ (seed 1); esercizio 11 della L7 (5 documenti) $\delta = 0{,}4$, $p = 0{,}215$; due classificatori identici $\delta = 0$, $p = 1$; 90% contro 50% su 100 documenti $p &lt; 0{,}01$.

Sui 400 test: bag of words meglio di VADER (+83 recensioni) e delle sei feature (+62) con $p &lt; 0{,}0001$; sei feature meglio di VADER (+21, $p = 0{,}027$); bag of words contro DistilBERT +6 recensioni, $p = 0{,}27$, **non significativo**. Questo non prova che siano equivalenti: con 400 esempi non si riesce a distinguerli. Servirebbero più dati di test o la cross-validation ([scheda 34 della L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-34)).

</details>

#### Esercizio 9: PMI di collocazioni dai conteggi

In Pinocchio tokenizzato ($N = 53.332$ token) valgono questi conteggi:

| bigramma | $C(w_1w_2)$ | $C(w_1)$ | $C(w_2)$ |
| --- | --- | --- | --- |
| Talking Cricket | 18 | 19 | 34 |
| of the | 183 | 860 | 2.100 |
| said Pinocchio | 27 | 225 | 451 |
| Pinocchio said | 2 | 451 | 225 |

(a) Calcola la PMI (in bit) di ciascun bigramma. (b) *of the* è il bigramma più frequente dei quattro: perché ha PMI bassa? (c) Perché *said Pinocchio* e *Pinocchio said* hanno PMI così diverse? (d) Qual è la PMI di un bigramma visto una volta, formato da due parole viste una volta? Che cosa insegna?

<details><summary>Soluzione</summary>

Formula: $\text{PMI} = \log_2\dfrac{C(w_1w_2)\,N}{C(w_1)\,C(w_2)}$.

(a) *Talking Cricket*: $\frac{18\cdot 53332}{19\cdot 34} = \frac{959.976}{646} = 1.486{,}0$, $\log_2 = 10{,}54$. *of the*: $\frac{183\cdot 53332}{860\cdot 2100} = \frac{9.759.756}{1.806.000} = 5{,}404$, $\log_2 = 2{,}43$. *said Pinocchio*: $\frac{27\cdot 53332}{225\cdot 451} = \frac{1.439.964}{101.475} = 14{,}19$, $\log_2 = 3{,}83$. *Pinocchio said*: $\frac{2\cdot 53332}{101.475} = 1{,}051$, $\log_2 = 0{,}07$.

(b) La PMI confronta la frequenza osservata con quella attesa sotto indipendenza, $C(w_1)C(w_2)/N = 860\cdot 2100/53332 = 33{,}9$: *of the* compare 183 volte, 5,4 volte più dell'atteso, ma *of* e *the* sono così frequenti che si incontrano spesso anche per caso. *Talking Cricket* è atteso 0,012 volte e compare 18 volte: 1.486 volte l'atteso.

(c) La PMI di bigramma è **asimmetrica** nell'ordine: conta $C(w_1w_2)$ nell'ordine dato. Nel dialogo inglese si scrive *“...,” said Pinocchio* (inversione dopo la battuta) molto più di *Pinocchio said*: il secondo ha PMI quasi 0, cioè la frequenza attesa per caso.

(d) $\log_2(1\cdot N/(1\cdot 1)) = \log_2 53332 = 15{,}70$, il massimo possibile: più di *Talking Cricket*. La PMI premia gli eventi rari e le stime da conteggi minuscoli sono inaffidabili: serve una soglia di frequenza (nel notebook 130 bigrammi sono a pari merito a 15,70 senza filtro). Tutti i valori verificati con `BigramAssocMeasures.pmi` di NLTK sul testo vero.

</details>

#### Esercizio 10: bag of words contro bag of bigrams

Documenti: $d_1$ = *good movie , not bad*, $d_2$ = *bad movie , not good* (già tokenizzati, 5 token). Vocabolario $V$ = (*,*, *bad*, *good*, *movie*, *not*). (a) Scrivi i vettori bag of words binari. (b) Elenca gli insiemi di bigrammi e calcola la similarità di Jaccard fra $d_1$ e $d_2$ con le parole e con i bigrammi. (c) Un classificatore lineare sul bag of words binario può dare a $d_1$ e $d_2$ probabilità diverse? E sul bag of bigrams? (d) Quale bigramma porta l'informazione sulla negazione, e che cosa fa invece il trucco NOT\_ visto nel notebook della L6?

<details><summary>Soluzione</summary>

(a) Entrambi $\mathbf x = [1, 1, 1, 1, 1]$: stessi cinque token, ordine perso.

(b) $d_1$: {(good, movie), (movie, ,), (, , not), (not, bad)}; $d_2$: {(bad, movie), (movie, ,), (, , not), (not, good)}. Jaccard sulle parole: $5/5 = 1$. Sui bigrammi: intersezione {(movie, ,), (, , not)} = 2, unione 6: $2/6 = 0{,}33$.

(c) Sul bag of words binario no: $\mathbf x$ è identico, quindi $\mathbf w\cdot\mathbf x + b$ è identico per qualunque peso. Sul bag of bigrams sì: le feature (not, bad) e (not, good) sono diverse e possono ricevere pesi di segno opposto (positivo per *not bad*, negativo per *not good*).

(d) (not, bad) e (not, good). Il trucco NOT\_ del notebook della L6 aggiunge il prefisso NOT\_ a tutte le parole dopo una negazione fino alla punteggiatura: *not bad* → NOT\_bad, una feature unigram diversa da *bad*; i bigrammi lo ottengono senza regole ma solo per la parola immediatamente successiva (*not very bad* darebbe (not, very) e (very, bad)). Verificato con `nltk.ngrams`.

</details>

#### Esercizio 11: n-grammi di caratteri e Jaccard

(a) Elenca i trigrammi di caratteri di *rainbow* e del refuso *rainbaw* e calcola la similarità di Jaccard. (b) Ripeti per *rainbow* e *rainbows*. (c) Quanti trigrammi ha una parola di $L$ caratteri (senza padding)? (d) Perché gli n-grammi di caratteri aiutano con parole mai viste nel training, e che cosa hanno in comune con BPE?

<details><summary>Soluzione</summary>

(a) *rainbow*: `rai` `ain` `inb` `nbo` `bow`; *rainbaw*: `rai` `ain` `inb` `nba` `baw`. Intersezione 3, unione 7: $J = 3/7 = 0{,}43$. Una lettera cambiata altera tutti i trigrammi che la contengono, al più tre; la *o* è la sesta lettera su sette, quindi sta solo in `nbo` e `bow`: due trigrammi diversi per parola, tre condivisi.

(b) *rainbows* ha i 5 trigrammi di *rainbow* più `ows`: $J = 5/6 = 0{,}83$. La flessione aggiunge un trigramma, non cambia gli altri.

(c) $L - 2$ (in generale $L - n + 1$ per gli $n$-grammi); con padding (es. `#rainbow#`) $L$, e si marcano inizio e fine parola.

(d) Una parola mai vista condivide molti n-grammi con parole viste (radici, suffissi come `ing`, `ed#`): la rappresentazione non è un vettore tutto nuovo. È la stessa idea dei **subword** ([scheda 28 della L2](L02-parole-e-token.md#p-28)): BPE impara dai dati quali pezzi tenere, gli n-grammi di caratteri li prendono tutti. Verificato con `set(nltk.ngrams(w, 3))`.

</details>

#### Esercizio 12: il compound di VADER a mano

Valenze del lessico: *good* 1,9, *bad* −2,5, *great* 3,1, *nice* 1,8. Regole: intensificatore (*very*) $\pm 0{,}293$ in modulo; negazione nelle 3 parole precedenti $\times(-0{,}74)$; parola in maiuscolo in un testo misto $\pm 0{,}733$ in modulo; con *but* le parole prima $\times 0{,}5$ e quelle dopo $\times 1{,}5$. $\text{compound} = s/\sqrt{s^2+15}$. Calcola il compound di: (a) *The acting was not great*; (b) *The film is GREAT and the cast is nice*; (c) *The plot was good but the ending was very bad*. (d) Per (c) calcola anche neg, neu e pos (10 parole; ogni parola neutra conta 1, ogni parola con sentiment $1 + |v|$).

<details><summary>Soluzione</summary>

(a) $s = -0{,}74 \cdot 3{,}1 = -2{,}294$; compound $= -2{,}294/\sqrt{5{,}262+15} = -2{,}294/4{,}501 = -0{,}510$.

(b) *GREAT* in maiuscolo: $3{,}1 + 0{,}733 = 3{,}833$; *nice* 1,8; $s = 5{,}633$; compound $= 5{,}633/\sqrt{31{,}73+15} = 5{,}633/6{,}836 = 0{,}824$.

(c) *good* prima di *but*: $1{,}9\cdot 0{,}5 = 0{,}95$. *very bad*: $-2{,}5 - 0{,}293 = -2{,}793$, dopo *but*: $\times 1{,}5 = -4{,}190$. $s = -3{,}240$; compound $= -3{,}240/\sqrt{10{,}49+15} = -3{,}240/5{,}049 = -0{,}642$. Una frase che inizia bene e finisce male è giudicata negativa.

(d) pos: $0{,}95+1 = 1{,}95$; neg: $4{,}190+1 = 5{,}190$; neu: 8 parole (anche *very* e *but* contano come neutre). Totale $15{,}14$: neg $= 0{,}343$, neu $= 0{,}528$, pos $= 0{,}129$. Nota: due parole su dieci hanno sentiment, ma neg + pos vale 47%: sono quote di intensità, non di testo. Tutti i valori coincidono con `polarity_scores` di NLTK (−0,5096; 0,824; −0,6416 e 0,343/0,528/0,129).

</details>

#### Esercizio 13: precision, recall e F1 sugli span BIO

Frase: *Galileo Galilei taught at the University of Padua in Italy* (10 token, indici 0-9).

gold: `B-PER I-PER O O O B-ORG I-ORG I-ORG O B-LOC`  
sistema: `B-PER O O O B-ORG I-ORG I-ORG I-ORG O B-LOC`

(a) Scrivi gli span gold e predetti come `(start, end, type)` con end escluso. (b) Calcola precision, recall e F1 sugli span. (c) Calcola l'accuracy sui tag BIO token per token. (d) Commenta la differenza.

<details><summary>Soluzione</summary>

(a) gold: (0, 2, PER), (5, 8, ORG), (9, 10, LOC). Sistema: (0, 1, PER), (4, 8, ORG), (9, 10, LOC).

(b) Solo (9, 10, LOC) coincide: $tp = 1$. $P = 1/3$, $R = 1/3$, $F_1 = 1/3 = 0{,}33$. Due errori di confine (*Galileo* senza *Galilei*; *the* incluso nell'organizzazione) costano ciascuno un falso positivo e un falso negativo.

(c) Token per token: posizioni 0 (B-PER) giusta, 1 (I-PER contro O) sbagliata, 2-3 giuste, 4 (O contro B-ORG) sbagliata, 5 (B-ORG contro I-ORG) sbagliata, 6-9 giuste: 7/10 = 70%.

(d) 70% di token giusti ma un'entità su tre trovata: l'accuracy sui token premia gli O facili e non vede che uno span con un confine sbagliato è inutilizzabile (chi estrae *Galileo* non ha estratto la persona *Galileo Galilei*). Per questo la NER si valuta sugli span (§18.6, [scheda 81 della L8](L08-sequence-labelling-pos-tagging-e-ner.md#p-81)). Verificato con le funzioni `bio_to_spans` e `span_prf` dell'esercizio A4.

</details>

### Domande tipo orale

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
