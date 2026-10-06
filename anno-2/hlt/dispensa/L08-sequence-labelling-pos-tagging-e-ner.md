# L8 · Sequence labelling: PoS tagging e NER

*Sequence Labelling* · 06/10/2026 · Andrea Ceni · lettura: J&M cap. 18, §18.1-18.7

[Versione interattiva sul sito](https://gabriele-marsili.github.io/appunti-magistrale-ai/anno-2/hlt/sito/#L8) · [Indice della dispensa](README.md)

Lezione sul **sequence labelling** (J&M cap. 18): assegnare un'etichetta a ogni parola. Prima le **parti del discorso**: classi aperte e chiuse, tagset UD (17 tag) e Penn Treebank, quanta ambiguità c'è davvero (55-67% dei token), baseline al 92% contro 97%. Poi l'**HMM**: catena di Markov sui tag con emissioni delle parole, matrici $A$ e $B$ stimate contando, decodifica con Bayes e due assunzioni, e l'**algoritmo di Viterbi** (programmazione dinamica in $O(N^2T)$, come la distanza di edit) con due esempi numerici ricalcolati cella per cella. Poi la **NER**, ridotta a etichettatura per parola con **BIO** ($2n+1$ tag), e il **CRF** a catena lineare: una regressione logistica multinomiale su sequenze intere, con feature arbitrarie (word shape, affissi, gazetteer) e decodifica ancora con Viterbi. Chiude la valutazione per entità (precision, recall, F1). Errori corretti nelle slide: tabella Penn incompleta (p. 12), due valori della Fig. 18.14 (p. 57), tabella BIO non coerente con la frase (p. 65), Janet NOUN invece di PROPN (p. 5).

## Indice

- [Apertura](#apertura)
- [Part-of-speech tagging](#part-of-speech-tagging)
- [Hidden Markov model](#hidden-markov-model)
- [Algoritmo di Viterbi](#algoritmo-di-viterbi)
- [Named entity recognition](#named-entity-recognition)
- [Conditional random field](#conditional-random-field)
- [Studio ed esercizi](#studio-ed-esercizi)

## Apertura

<a id="p-1"></a>

### Slide 1 · Sequence labelling: PoS tagging e NER

Ottava lezione, prima di Andrea Ceni, sul capitolo 18 di J&M. Finora abbiamo classificato **un oggetto alla volta** (un documento: Naive Bayes, regressione logistica, L6-L7). Qui l'uscita è una **sequenza di etichette**, una per parola: è il **sequence labelling**.

- **Part-of-speech tagging**: a ogni parola la sua classe grammaticale (NOUN, VERB, DET...).
- **Named entity recognition** (NER): trovare e classificare gli span che sono nomi propri (persone, organizzazioni, luoghi), ridotto a etichettatura parola per parola con lo schema **BIO**.

Due modelli classici: l'**HMM** (generativo, parente stretto dei modelli n-gram della L4 e di Naive Bayes) e il **CRF** (discriminativo, una regressione logistica multinomiale "su sequenze"). Per entrambi la decodifica si fa con l'**algoritmo di Viterbi**, programmazione dinamica come la distanza di edit della L3.

<a id="p-2"></a>

### Slide 2 · Indice della lezione

Cinque blocchi, separati da slide divisorie:

1. **Part-of-speech tagging**: classi di parole, tagset (UD, Penn Treebank), ambiguità, baseline (§18.1-18.2).
2. **Hidden Markov model**: catene di Markov, matrici $A$ e $B$, decodifica (§18.4.1-18.4.4).
3. **Algoritmo di Viterbi**: reticolo, ricorsione, backtrace, esempi numerici (§18.4.5-18.4.6).
4. **Named entity recognition**: tipi di entità, BIO/IO/BIOES (§18.3).
5. **Conditional random field**: modello log-lineare su sequenze, feature, inferenza; poi valutazione della NER (§18.5-18.7).

La pausa cade fra la parte HMM e Viterbi.

<a id="p-3"></a>

### Slide 3 · Riferimento: J&M capitolo 18

Lettura: **Jurafsky & Martin**, *Speech and Language Processing*, 3a ed. draft, capitolo 18 (*Sequence Labeling for Parts of Speech and Named Entities*):

- 18.1 classi di parole (in gran parte dell'inglese); 18.2 PoS tagging;
- 18.3 named entity e NER (con BIO);
- 18.4 HMM per il PoS tagging (Markov chain, HMM, componenti, decodifica, Viterbi, esempio svolto);
- 18.5 CRF; 18.6 valutazione della NER; 18.7 dettagli (dati, metodi a regole, lingue morfologicamente ricche).

Le slide seguono il libro abbastanza fedelmente; gli esempi marcati *instructor example* (frase *The fans watch the race*, grafico sui domini, pesi del CRF) sono del docente. Il QR code porta al sito del libro.

## Part-of-speech tagging

<a id="p-4"></a>
**Slide 4 · Part-of-speech tagging** — Prima parte: classi di parole e il compito di tagging.

<a id="p-5"></a>

### Slide 5 · Il compito di tagging

Un **tagger** mappa la sequenza di parole $x_1,\dots,x_n$ nella sequenza di tag $y_1,\dots,y_n$: **stessa lunghezza**, ogni $y_i$ corrisponde esattamente a $x_i$. Questa è la definizione di **sequence labelling**.

La figura (Fig. 18.3 del libro): le cinque parole *Janet will back the bill* entrano dal basso in una scatola arancione "Part of Speech Tagger", che emette verso l'alto cinque etichette in ovali azzurri: NOUN, AUX, VERB, DET, NOUN.

Differenza con la classificazione delle L6-L7: lì un'etichetta per tutto il documento; qui $n$ etichette **non indipendenti** (dopo un DET è probabile un NOUN o un ADJ, quasi mai un VERB). Tutta la lezione parla di come sfruttare queste dipendenze fra etichette vicine.

Sulla stessa frase tornano l'HMM con Viterbi ([scheda 54](L08-sequence-labelling-pos-tagging-e-ner.md#p-54)) e le feature del CRF ([scheda 75](L08-sequence-labelling-pos-tagging-e-ner.md#p-75)), con i tag Penn: *Janet/NNP will/MD back/VB the/DT bill/NN*.

> **Attenzione (errore nelle slide): Janet è PROPN, non NOUN**
>
> Nella figura *Janet* riceve NOUN. In Universal Dependencies un nome proprio di persona è **PROPN** (la [scheda 10](L08-sequence-labelling-pos-tagging-e-ner.md#p-10) mette proprio *Regina* fra gli esempi di PROPN), e la stessa lezione dice "Janet is always NNP" ([scheda 17](L08-sequence-labelling-pos-tagging-e-ner.md#p-17)), che in UD corrisponde a PROPN. Sequenza UD corretta: **PROPN AUX VERB DET NOUN**. L'errore viene dalla Fig. 18.3 del libro, riprodotta tale e quale.

<a id="p-6"></a>

### Slide 6 · Le parti del discorso: storia (background)

**Slide di background, non nel capitolo 18** (il libro cita solo Dionisio Trace e Aristotele nell'introduzione). Una linea del tempo con tre tappe:

- **Yāska e Pāṇini** (India, grammatica del sanscrito, V-IV sec. a.C. circa): Yāska distingue **quattro classi**: nomi, verbi, preverbi, particelle.
- **Aristotele** (Grecia, IV sec. a.C.): separa il nome (*onoma*) dal verbo (*rhēma*), con i connettivi come terzo tipo.
- **Dionisio Trace** (Alessandria, I sec. a.C. circa; attribuzione incerta): **otto parti del discorso**: nome, verbo, participio, articolo, pronome, preposizione, avverbio, congiunzione.

Messaggio: le otto classi di Trace sono riconoscibili nei tagset di oggi (il libro: base delle grammatiche europee per 2000 anni). L'NLP ha **ereditato** le categorie dalla grammatica tradizionale, non le ha inventate. Da sapere come contesto, non come contenuto d'esame.

<a id="p-7"></a>

### Slide 7 · Si definiscono dal comportamento grammaticale

**Part of speech = word class = PoS tag**: tre nomi per la stessa cosa, il libro li usa in modo intercambiabile.

Il punto centrale: le classi si definiscono dal **comportamento grammaticale**, non dal significato.

- **Il significato è solo una tendenza**: i nomi spesso indicano persone e cose (*cat, mango, Pisa*), ma *beauty, arrival, idea* sono nomi e non sono cose. Gli aggettivi spesso indicano proprietà (*red, young*).
- **La grammatica è la definizione**: (1) **distribuzione**, cioè con cosa si combina la parola: *very young* va bene, *very cat* no, quindi dopo *very* ci sta un aggettivo; (2) **morfologia**: i suffissi cambiano la classe, *happy* (ADJ) → *happiness* (NOUN), *home* (NOUN) → *homeless* (ADJ).

Queste due fonti di evidenza (parole vicine e affissi) sono esattamente le feature che useranno i tagger: contesto per l'HMM, suffissi e forma della parola per il CRF ([scheda 77](L08-sequence-labelling-pos-tagging-e-ner.md#p-77)). I tagset in uso hanno fra **40 e 200 tag**, e tutto questo vale per l'inglese.

<a id="p-8"></a>

### Slide 8 · Classi chiuse e classi aperte

- **Classe chiusa** (*the, she, on, and*): insieme di parole relativamente fisso (nuove preposizioni non nascono quasi mai). Sono **function word**: corte, frequentissime, con funzione grammaticale. In UD: adposizioni, ausiliari, congiunzioni, determinanti, numerali, particelle, pronomi.
- **Classe aperta** (*dog, run, beautiful, clearly, doomscrolling, COVID*): **content word**: nomi, verbi, aggettivi, avverbi, più la piccola classe aperta delle interiezioni. Nuovi membri continuamente.

Perché conta per il tagging, con due difficoltà opposte:

- le parole chiuse sono poche ma **frequenti e spesso ambigue** (*that, to, up*): pesano molto sull'accuratezza;
- le parole aperte crescono sempre, quindi nel test arrivano **parole sconosciute**, per cui l'HMM non ha conteggi (lo stesso problema delle parole fuori vocabolario, [scheda 9 della L5](L05-smoothing-ed-entropia.md#p-9)).

<a id="p-9"></a>

### Slide 9 · L'inventario delle classi

Le classi UD in due riquadri, con esempi:

| Classe aperta | Esempi | Classe chiusa | Esempi |
| --- | --- | --- | --- |
| NOUN | algorithm, cat | ADP | in, on, by |
| PROPN | Regina, IBM | AUX | can, may, are |
| VERB | draw, provide | CCONJ | and, or, but |
| ADJ | red, young | DET | a, an, the |
| ADV | very, slowly | NUM | one, two, 2026 |
| INTJ | oh, um, yes | PART | 's, not, to |
|  |  | PRON | she, who, I |
|  |  | SCONJ | whether, because |

6 aperte + 8 chiuse = 14; con le 3 "altre" (PUNCT, SYM, X) si arriva ai 17 tag UD della scheda successiva. Da notare: **AUX** separato da VERB (*are* in *are reading* è AUX); **PART** contiene il *to* dell'infinito e il genitivo *'s*; **SCONJ** contiene i complementatori (*that* in *I thought that...*).

<a id="p-10"></a>

### Slide 10 · Il tagset Universal Dependencies

La tabella è la Fig. 18.1 del libro: i **17 tag UPOS** di Universal Dependencies (de Marneffe et al., 2021) in tre gruppi.

- **Open class (6)**: ADJ, ADV, NOUN, VERB, PROPN, INTJ.
- **Closed class (8)**: ADP (adposizione: preposizione o posposizione), AUX, CCONJ, DET, NUM, PART, PRON, SCONJ.
- **Other (3)**: PUNCT, SYM (simboli come \$ o emoji), X (altro: *asdf*).

Pensato per essere **universale**: lo stesso inventario per oltre cento lingue; le distinzioni più fini (numero, caso, tempo...) si aggiungono come *feature* morfologiche separate, non come tag diversi. È il tagset già visto nell'esempio della [scheda 42 della L1](L01-introduzione-al-corso.md#p-42) e quello che usa spaCy (`token.pos_`), da riprendere nel laboratorio.

<a id="p-11"></a>

### Slide 11 · Classi di parole (in gran parte) inglesi

Tutto quanto visto descrive l'**inglese**; le lingue ritagliano le classi in modo diverso. Quattro esempi:

- **Gli aggettivi non sono universali**: in coreano le parole che corrispondono agli aggettivi inglesi si comportano come una sottoclasse di verbi (*beautiful* ≈ "essere bello").
- **Nome e verbo sono contesi**: secondo alcuni il riau indonesiano e il tongano non distinguono affatto nome e verbo (Broschart 1997; Evans 2000; Gil 2000).
- **Adposizioni, non preposizioni**: l'inglese le mette prima del nome (*in Tokyo*), giapponese e hindi dopo (*Tōkyō de*, *Tokyo mẽ*): perciò UD usa ADP e non PREP.
- **La morfologia fa esplodere il tagset**: per ceco, ungherese, turco un tag diventa una sequenza di feature morfologiche e i tagset sono **4-10 volte più grandi** (§18.7.2).

Conseguenza: UD definisce un solo inventario astratto per tutte le lingue; il tag è ADP, non PREP.

<a id="p-12"></a>

### Slide 12 · Il tagset Penn Treebank

Il **Penn Treebank tagset** (Marcus et al., 1993; Fig. 18.2): **36 tag** specifici dell'inglese, più fini di UD. Esempio: dove UD ha un solo VERB, Penn ha **VB** (base, *eat*), **VBD** (passato, *ate*), **VBG** (gerundio, *eating*), **VBN** (participio passato, *eaten*), **VBP** (presente non 3a sing., *eat*), **VBZ** (presente 3a sing., *eats*). Altre distinzioni: **NN/NNS/NNP/NNPS** (comune/proprio × singolare/plurale), JJ/JJR/JJS (grado dell'aggettivo), **MD** (modale: *can, will*), **EX** (*there* esistenziale), **POS** (*'s*), **TO**, **DT**, **IN** (preposizione e congiunzione subordinante insieme).

Va conosciuto perché etichetta i corpora Penn Treebank (WSJ) e tutti gli esempi numerici di questa lezione ([schede 55-56](L08-sequence-labelling-pos-tagging-e-ner.md#p-55)). Ai 36 tag di parola si aggiungono 9 tag di punteggiatura e simboli: è il tagset **a 45 tag** citato nella [scheda 17](L08-sequence-labelling-pos-tagging-e-ner.md#p-17). Lo stesso progetto ha fissato lo standard di tokenizzazione visto nella [scheda 30 della L3](L03-elaborazione-del-testo.md#p-30).

> **Attenzione (errore nelle slide): La tabella mostra 33 tag, non 36: manca l'ultima riga**
>
> La tabella della slide si ferma alla riga MD / RP / WP\$: contando, sono 11 righe × 3 = **33 tag**. Manca l'ultima riga della Fig. 18.2 del libro, con tre tag:
>
> - **NN**: nome comune singolare o di massa (*llama*), proprio il tag più usato negli esempi della lezione;
> - **SYM**: simbolo (*+, %, &*);
> - **WRB**: wh-avverbio (*how, where*).
>
> Con questi tre si arriva ai 36 dichiarati (verificato contando i tag della Fig. 18.2 nel libro, pagina 403).

<a id="p-13"></a>

### Slide 13 · Il tagging è un compito di disambiguazione

- **Compito**: assegnare una parte del discorso a ogni parola del testo.
- **Input**: sequenza di parole già tokenizzate e un tagset.
- **Output**: un tag per parola, stessa lunghezza.

La difficoltà è l'**ambiguità** (la stessa che apriva il corso, [scheda 34 della L1](L01-introduzione-al-corso.md#p-34)): la stessa forma ha classi diverse a seconda del contesto.

- *Book that flight.*: **book** è verbo (imperativo, "prenota").
- *Hand me that book.*: **book** è nome.
- *that*: determinante in *Does that flight serve dinner*, complementatore (SCONJ) in *I thought that your flight was earlier*.

La forma della parola è identica, cambia solo il contesto: per questo un tagger deve guardare le parole e i tag vicini, non solo la parola.

<a id="p-14"></a>

### Slide 14 · Frasi inglesi annotate

L'annotazione rende esplicito il tag di ogni token, nel formato `parola/TAG` (tag UD):

`There/PRON were/VERB 70/NUM children/NOUN there/ADV ./PUNCT`

`Preliminary/ADJ findings/NOUN were/AUX reported/VERB in/ADP today/NOUN 's/PART New/PROPN England/PROPN Journal/PROPN of/ADP Medicine/PROPN`

Cose da notare:

- **there/PRON** (esistenziale: *there were*) contro **there/ADV** (luogo: "là"): stessa forma, classe diversa. In Penn il primo sarebbe EX, il secondo RB.
- *were* è VERB nella prima frase (verbo principale esistenziale) e AUX nella seconda (ausiliare del passivo *were reported*).
- Tutte le parole del nome della rivista sono PROPN, anche *Journal* e *Medicine* che altrove sarebbero NOUN: fanno parte di un nome proprio.
- *'s* è un token separato (PART), come prevede la tokenizzazione Penn.

Il libro (18.1-18.2) ha frasi quasi uguali (*are* al posto di *were*, *London* al posto di *New England*) con anche i tag Penn.

<a id="p-15"></a>

### Slide 15 · A che cosa serve il PoS tagging

Due usi:

- **NLP a valle: una feature economica e riutilizzabile**. Nel **parsing** i tag restringono la ricerca sintattica ([scheda 43 della L1](L01-introduzione-al-corso.md#p-43)); nella **traduzione automatica** l'ordine aggettivo-nome cambia fra lingue (scheda seguente); nel **text-to-speech** la pronuncia dipende dal tag: *contrast* nome (accento sulla prima sillaba) e verbo (sulla seconda).
- **Analisi linguistica: una variabile da controllare**. Studi di cambiamento lessicale (parole nuove, significati che si spostano: *text* da NN a VB, "mandare un SMS"); misure di similarità di significato calcolate dentro una stessa classe; statistiche di corpus riportate per parte del discorso.

Oggi i grandi modelli neurali non hanno bisogno dei tag come input, ma il tagging resta un passo standard delle pipeline (spaCy, NLTK) e un banco di prova classico per i modelli di sequenza.

<a id="p-16"></a>

### Slide 16 · I tag nella traduzione automatica

Due esempi del docente, inglese → italiano:

- **Scelta della parola**: *book* si traduce *prenota* o *libro*? Dipende dal tag. *Book/VERB that flight* → *Prenota quel volo*; *Hand me that book/NOUN* → *Passami quel libro*.
- **Ordine delle parole**: *the red car* (DET ADJ NOUN) → *la macchina rossa*. Nella figura *the* va dritto su *la*, mentre le frecce di *red* e *car* si incrociano: in italiano l'aggettivo segue il nome.

Il tag dice al sistema **quale parola scegliere** e **dove metterla**. Nei sistemi statistici classici le regole di riordino erano scritte proprio in termini di PoS; nei sistemi neurali questa informazione è appresa implicitamente.

<a id="p-17"></a>

### Slide 17 · Quanto è ambiguo l'inglese?

Fig. 18.4: ambiguità dei tag nei corpora WSJ e Brown (Treebank-3, tagset a 45 tag).

|  | WSJ | Brown |
| --- | --- | --- |
| Tipi non ambigui (1 tag) | 44.432 (86%) | 45.799 (85%) |
| Tipi ambigui (2+ tag) | 7.025 (14%) | 8.050 (15%) |
| Token non ambigui | 577.421 (45%) | 384.349 (33%) |
| Token ambigui | 711.780 (55%) | 786.646 (67%) |

Distinguere **tipi** (parole distinte del vocabolario) e **token** (occorrenze nel testo), come nella L2. La maggior parte dei tipi ha un solo tag (*Janet* sempre NNP, *hesitantly* sempre RB), ma il 14-15% di tipi ambigui sono le parole **frequenti** (*that, back, to, up*), quindi coprono il **55-67% dei token**. Più di metà delle parole di un testo va davvero disambiguata.

Percentuali ricalcolate: WSJ tipi 44.432/51.457 = 86,3%; Brown 45.799/53.849 = 85,1%; token WSJ 577.421/1.289.201 = 44,8%; Brown 384.349/1.170.995 = 32,8%. Tutte coerenti con la tabella.

<a id="p-18"></a>

### Slide 18 · Sei parti del discorso per una parola: back

La parola *back* con sei tag Penn diversi:

| Tag | Contesto | Perché |
| --- | --- | --- |
| JJ | earnings growth took a *back* seat | modifica il nome *seat* |
| NN | a small building in the *back* | dopo DT, testa del sintagma |
| VBP | a clear majority of senators *back* the bill | verbo finito, presente non 3a sing. |
| VB | Dave began to *back* toward the door | forma base dopo *to* |
| RP | enable the country to buy *back* debt | particella del phrasal verb *buy back* |
| RB | I was twenty-one *back* then | avverbio di tempo |

In ogni riga è il **contesto** a decidere. Altre parole comuni molto ambigue: *that, down, put, set*. *back* torna nell'esempio *Janet will back the bill* (VB dopo il modale *will*), dove la matrice $B$ le dà quattro tag possibili ([scheda 56](L08-sequence-labelling-pos-tagging-e-ner.md#p-56)).

<a id="p-19"></a>

### Slide 19 · Che cosa disambigua un tag?

Le fonti di evidenza, sull'esempio *Janet will back the bill*:

- **Probabilità a priori parola/tag**: *will* è di solito un modale (MD), raramente un nome ("testamento").
- **Identità delle parole vicine**: dopo *the* la parola successiva difficilmente è un verbo.
- **Prefissi**: *unable*: *un-* → aggettivo.
- **Suffissi**: *importantly*: *-ly* → avverbio; *reported*: *-ed* → VBD o VBN.
- **Maiuscole e forma della parola**: *Janet* con l'iniziale maiuscola → nome proprio.

La riga in fondo anticipa l'arco della lezione: l'**HMM** sfrutta solo le prime due (emissioni $P(w\mid t)$ e transizioni fra tag); per aggiungere le altre serve un modello in cui si possano mettere **feature arbitrarie**, cioè il **CRF** ([scheda 69](L08-sequence-labelling-pos-tagging-e-ner.md#p-69)).

<a id="p-20"></a>

### Slide 20 · Lo stato dell'arte e la baseline

- **Baseline most-frequent-tag: circa 92%**. A ogni token si dà il tag con cui la parola è comparsa più spesso nel training; una parola mai vista prende **NN**, il tag aperto più frequente. Misurata sul WSJ, training sulle sezioni 0-18, test sulle sezioni 22-24 (il libro dà 92,3%, da Abney et al., 1999).
- **Tagger supervisionati: circa 97%**. Oltre il 97% su 15 lingue UD (Wu e Dredze, 2019); su inglese HMM, CRF e BERT si equivalgono; l'accordo fra annotatori umani è circa lo stesso (Manning, 2011).

Due lezioni: (1) **confrontare sempre** un tagger con una baseline almeno così buona (regola generale del libro); (2) fra baseline e stato dell'arte ci sono **solo 5 punti**, e lo stato dell'arte coincide col tetto umano. Un 95% non è un buon risultato: è più vicino alla baseline che al tetto.

Un modo utile di leggere i numeri: in termini di errore, passare da 92% a 97% significa ridurre gli errori da 8 a 3 ogni 100 parole, cioè di oltre il 60%.

> **Da saper fare: Calcolare la baseline**
>
> Training: si conta, per ogni parola, quante volte compare con ciascun tag; si salva il tag più frequente. Test: si assegna quel tag (NN per le parole sconosciute) e si misura l'**accuracy** = tag corretti / token. Su un corpus ambiguo la baseline sbaglia sistematicamente i casi minoritari: se *book* è NN 2 volte su 3, *book the flight* diventa NN DT NN (esercizio 2).

<a id="p-21"></a>

### Slide 21 · L'effetto del dominio

Grafico a barre del docente (non nel libro): cinque coppie, barra blu = dominio "standard", barra rossa = dominio lontano.

| Lingua | Standard | Lontano | Calo |
| --- | --- | --- | --- |
| Inglese | WSJ 97,3 | Shakespeare 81,9 | 15,4 |
| Tedesco | moderno 97,0 | Early Modern 69,6 | 27,4 |
| Inglese | WSJ 97,3 | Middle English 56,2 | 41,1 |
| Italiano | News 97,0 | Dante 75,0 | 22,0 |
| Inglese | WSJ 97,3 | Twitter 73,7 | 23,6 |

Il 97% vale **sul dominio di training**. Testi storici, letterari o social hanno ortografia, lessico e sintassi diversi: molte parole sconosciute, distribuzioni di tag diverse. L'accuratezza va sempre riportata insieme al dominio. La didascalia dice "15-40 punti": a rigore il calo va da 15,4 a 41,1 (Middle English), quindi "circa 15-41".

È lo stesso fenomeno di *genre* e dialetto visto per i modelli n-gram (L4): un modello è buono quanto la somiglianza fra training e test.

<a id="p-22"></a>

### Slide 22 · Algoritmi per il sequence labelling

- **Generativi: HMM**. Modellano come sono stati **generati** i dati, cioè la congiunta $P(\text{parole}, \text{tag})$; le probabilità si stimano contando su un corpus annotato; trasparenti, economici, facili da ispezionare.
- **Discriminativi: CRF (e MEMM)**. Modellano direttamente $P(\text{tag}\mid\text{parole})$; sono **log-lineari**, quindi si può aggiungere qualunque feature. I modelli neurali di sequenza (RNN, transformer) arrivano più avanti nel corso.

È la stessa distinzione generativo/discriminativo della [scheda 13 della L6](L06-regressione-logistica.md#p-13): HMM sta a CRF come **Naive Bayes** sta alla **regressione logistica**. Entrambi richiedono un training set annotato a mano ed entrambi arrivano a circa 97% sull'inglese.

Il MEMM (*maximum entropy Markov model*, Ratnaparkhi 1996) è una versione più semplice del CRF che normalizza localmente a ogni posizione; il libro lo cita solo nelle note storiche.

## Hidden Markov model

<a id="p-23"></a>
**Slide 23 · Hidden Markov model** — Seconda parte: un modello generativo per sequenze di tag.

<a id="p-24"></a>

### Slide 24 · Catene di Markov

Una **catena di Markov** assegna probabilità a sequenze di stati, con un'ipotesi fortissima: per predire il futuro conta **solo il presente**.

$$P(q_i = a\mid q_1\dots q_{i-1}) = P(q_i = a\mid q_{i-1})$$

È l'**assunzione di Markov** già vista per i bigrammi ([scheda 12 della L4](L04-modelli-linguistici-n-gram.md#p-12)): gli stati precedenti influenzano il futuro solo attraverso lo stato corrente. Come predire il meteo di domani guardando oggi ma non ieri.

- Gli stati possono essere parole, tag, o altro (il meteo).
- I valori degli archi uscenti da ogni stato sommano a 1.

A destra il grafo del meteo che la scheda successiva spiega nel dettaglio.

<a id="p-25"></a>

### Slide 25 · Una catena di Markov per il meteo

Fig. 18.8a: tre stati HOT1, COLD2, WARM3, ognuno colorato con i suoi archi uscenti. Leggendo i colori:

| da \ a | HOT | COLD | WARM | somma |
| --- | --- | --- | --- | --- |
| HOT | 0,6 | 0,1 | 0,3 | 1 |
| COLD | 0,1 | 0,8 | 0,1 | 1 |
| WARM | 0,3 | 0,1 | 0,6 | 1 |

Distribuzione iniziale $\pi = [0{,}1;\ 0{,}7;\ 0{,}2]$ (HOT, COLD, WARM). $a_{ij}$ è la probabilità di passare dallo stato $i$ allo stato $j$; ogni **riga** è una distribuzione. La tabella è proprio la **matrice di transizione** $A$.

Le probabilità sulla diagonale sono alte (0,6; 0,8; 0,6): il tempo tende a restare com'è. COLD è il più "persistente".

<a id="p-26"></a>

### Slide 26 · Una catena di Markov per le parole

Fig. 18.8b: stessa macchina, ma gli stati sono parole: *are*, *uniformly*, *charming*.

| da \ a | uniformly | are | charming | somma |
| --- | --- | --- | --- | --- |
| uniformly | 0,1 | 0,4 | 0,5 | 1 |
| are | 0,5 | 0 | 0,5 | 1 |
| charming | 0,6 | 0,2 | 0,2 | 1 |

(*are* non ha anello su se stesso.) Questo è esattamente un **modello linguistico bigram** (L4): ogni arco è $P(w_i\mid w_{i-1})$, la probabilità della parola successiva data la precedente. Per esempio $P(\textit{charming}\mid\textit{are}) = 0{,}5$.

Il collegamento è importante: un modello bigram **è** una catena di Markov sulle parole. Nell'HMM la catena di Markov sarà sui **tag**, e le parole verranno "emesse" dai tag.

<a id="p-27"></a>

### Slide 27 · Catena di Markov: definizione formale

Una catena di Markov è specificata da tre componenti:

- $Q = q_1 q_2\dots q_N$: gli $N$ **stati** (uno per tag, o per condizione meteo);
- $A$: la **matrice delle probabilità di transizione**, $N\times N$,
  $$a_{ij} = P(q_t = j\mid q_{t-1} = i),\qquad \sum_{j=1}^{N} a_{ij} = 1\quad \forall i$$
  ogni riga è una distribuzione;
- $\pi$: la distribuzione sugli stati iniziali (scheda seguente); alcuni stati possono avere $\pi_j = 0$, cioè non possono essere iniziali.

Attenzione alla convenzione: **riga = stato di partenza, colonna = stato di arrivo**. È la stessa di tutte le tabelle $A$ della lezione ([scheda 48](L08-sequence-labelling-pos-tagging-e-ner.md#p-48), [scheda 55](L08-sequence-labelling-pos-tagging-e-ner.md#p-55)).

<a id="p-28"></a>

### Slide 28 · Il vettore delle probabilità iniziali

$\pi$ è una distribuzione sullo stato in cui parte la catena:

$$\pi_i = P(q_1 = i),\quad 1\le i\le N,\qquad \sum_{i=1}^{N}\pi_i = 1$$

Per il meteo $\pi = [0{,}1;\ 0{,}7;\ 0{,}2]$: probabilità 0,7 di partire da COLD.

Nei tagger, invece di un vettore separato, si usa spesso un tag fittizio di inizio frase **<s>**: $\pi_j = P(t_1 = j\mid \langle s\rangle)$ diventa semplicemente la prima riga di $A$ (così nelle [schede 48](L08-sequence-labelling-pos-tagging-e-ner.md#p-48) e [55](L08-sequence-labelling-pos-tagging-e-ner.md#p-55)). È lo stesso trucco dei simboli di inizio frase nei bigrammi della L4.

<a id="p-29"></a>

### Slide 29 · Esercizio: probabilità di due sequenze

L'esercizio del libro (18.4-18.5): con $\pi = [0{,}1;\ 0{,}7;\ 0{,}2]$ e la catena della [scheda 25](L08-sequence-labelling-pos-tagging-e-ner.md#p-25), calcolare la probabilità di *cold hot cold hot* e *hot hot hot hot*. La probabilità di una sequenza è lo stato iniziale per il prodotto delle transizioni:

$$P(q_1\dots q_T) = \pi_{q_1}\prod_{t=2}^{T} a_{q_{t-1}q_t}$$

- $P(\text{hot hot hot hot}) = 0{,}1\cdot 0{,}6\cdot 0{,}6\cdot 0{,}6 = 0{,}0216$
- $P(\text{cold hot cold hot}) = 0{,}7\cdot 0{,}1\cdot 0{,}1\cdot 0{,}1 = 0{,}0007$

La prima è circa **31 volte** più probabile, nonostante parta da HOT ($\pi = 0{,}1$) invece che da COLD (0,7). Il fatto del mondo codificato: il tempo è **persistente**, alternare caldo e freddo ogni giorno è molto improbabile (le transizioni HOT↔COLD valgono 0,1, le permanenze 0,6-0,8). Verificato con numpy.

> **Da saper fare: Probabilità di una sequenza in una catena di Markov**
>
> Scrivi la sequenza, prendi $\pi$ del primo stato, poi moltiplica una transizione per ogni coppia consecutiva leggendo **riga = stato precedente**. Con $T$ stati ci sono 1 fattore iniziale e $T-1$ transizioni. Esempio extra: $P(\text{cold cold cold cold}) = 0{,}7\cdot 0{,}8^3 = 0{,}3584$.

<a id="p-30"></a>

### Slide 30 · Dalla catena di Markov all'HMM

- **Catena di Markov: gli eventi sono osservati**. Utile quando serve la probabilità di una sequenza di eventi visibili: gli stati sono esattamente ciò che vediamo (le parole in un modello bigram).
- **Hidden Markov model: gli eventi sono nascosti**. Nel tagging vediamo le parole ma **non i tag**; i tag sono i "fattori causali" che dobbiamo inferire dalle parole. L'HMM permette di parlare insieme di eventi osservati (parole) ed eventi nascosti (tag).

Gli stati si chiamano **hidden** proprio perché non sono osservati. L'idea generativa: il testo è prodotto da un processo che prima sceglie un tag (seguendo la catena di Markov sui tag), poi da quel tag "emette" una parola. Decodificare significa risalire dalle parole alla sequenza di tag che più probabilmente le ha prodotte.

<a id="p-31"></a>

### Slide 31 · HMM: definizione

Un HMM è specificato da (tabella della slide, con le righe nuove rispetto alla catena di Markov segnate in verde):

| Simbolo | Componente |  |
| --- | --- | --- |
| $Q = q_1\dots q_N$ | $N$ stati | come nella catena |
| $A = a_{11}\dots a_{NN}$ | matrice di transizione, righe che sommano a 1 | come nella catena |
| $O = o_1\dots o_T$ | sequenza di $T$ osservazioni dal vocabolario $V$ | **nuovo** |
| $B = b_i(o_t)$ | **emission probabilities** (observation likelihood): probabilità che lo stato $i$ generi $o_t$ | **nuovo** |
| $\pi = \pi_1\dots\pi_N$ | distribuzione iniziale | come nella catena |

Le componenti del modello sono quattro: $Q$, $A$, $B$, $\pi$; la sequenza $O$ è l'**input**. Per il tagging: stati = tag, osservazioni = parole, $b_i(o_t) = P(w\mid t)$. Ogni riga di $B$ è una distribuzione sull'intero vocabolario: $\sum_{w\in V} b_i(w) = 1$.

<a id="p-32"></a>

### Slide 32 · Assunzione 1: l'assunzione di Markov

La figura mostra la catena degli stati nascosti $\dots, q_{i-1}, q_i$ con le frecce fra stati consecutivi; un arco lungo da uno stato più lontano a $q_i$ è barrato con una X rossa.

$$P(q_i\mid q_1,\dots,q_{i-1}) = P(q_i\mid q_{i-1})$$

La probabilità di uno stato dipende **solo dallo stato precedente**: gli archi più lunghi sono esclusi. È un HMM **del primo ordine** (bigram sui tag). Un HMM del secondo ordine (trigram, come il tagger TnT di Brants 2000) condizionerebbe sui due tag precedenti, al costo di più parametri e di una decodifica più cara.

<a id="p-33"></a>

### Slide 33 · Assunzione 2: indipendenza delle osservazioni

La figura aggiunge la riga delle osservazioni con frecce verticali verdi stato → osservazione; due archi verso $o_i$, uno da un'altra osservazione e uno da uno stato diverso da $q_i$, sono barrati.

$$P(o_i\mid q_1,\dots,q_i,\dots,q_T,\ o_1,\dots,o_i,\dots,o_T) = P(o_i\mid q_i)$$

Un'osservazione dipende **solo dallo stato che l'ha prodotta**, non da altri stati né da altre osservazioni. Nel tagging: la probabilità della parola dipende solo dal suo tag. È l'analogo dell'ipotesi "naive" di Naive Bayes ([scheda 15 della L6](L06-regressione-logistica.md#p-15)), dove le feature erano indipendenti data la classe.

È anche il limite principale dell'HMM: la parola precedente o successiva (*Mr.* prima di un nome di persona) non può influire direttamente sulla parola corrente ([scheda 69](L08-sequence-labelling-pos-tagging-e-ner.md#p-69)).

<a id="p-34"></a>

### Slide 34 · Transizioni ed emissioni

La figura riassume la struttura: frecce orizzontali azzurre lungo la catena nascosta (**transitions**) e frecce verticali verdi verso le osservazioni (**emissions**).

Due assunzioni, due famiglie di parametri:

- dall'assunzione di Markov → le **transizioni** $A$, $P(t_i\mid t_{i-1})$;
- dall'indipendenza delle osservazioni → le **emissioni** $B$, $P(w_i\mid t_i)$.

Con queste due ipotesi la probabilità congiunta di parole e tag si fattorizza in un prodotto di fattori locali:

$$P(w_{1:n}, t_{1:n}) = \prod_{i=1}^{n} P(t_i\mid t_{i-1})\,P(w_i\mid t_i)\qquad (t_0 = \langle s\rangle)$$

È questa fattorizzazione locale che renderà possibile Viterbi.

<a id="p-35"></a>

### Slide 35 · Le due componenti di un tagger HMM

Entrambe si stimano per **massima verosimiglianza** (MLE) contando su un corpus annotato, esattamente come i bigrammi della [scheda 13 della L4](L04-modelli-linguistici-n-gram.md#p-13):

$$P(t_i\mid t_{i-1}) = \frac{C(t_{i-1}, t_i)}{C(t_{i-1})}\qquad\qquad P(w_i\mid t_i) = \frac{C(t_i, w_i)}{C(t_i)}$$

- **A (transizioni)**: nel WSJ MD compare 13.124 volte ed è seguito da VB 10.471 volte: $P(\text{VB}\mid\text{MD}) = 10471/13124 = 0{,}80$ (esatto 0,7979).
- **B (emissioni)**: dei 13.124 MD, 4.046 sono la parola *will*: $P(\textit{will}\mid\text{MD}) = 4046/13124 = 0{,}31$ (esatto 0,3083).

Attenzione al verso: $P(\textit{will}\mid\text{MD})$ **non** è "qual è il tag più probabile per *will*" (quella sarebbe la posterior $P(\text{MD}\mid\textit{will})$, alta); è "se genero un modale, quanto è probabile che sia *will*". Un tag con molte parole possibili (NN) ha emissioni piccole per ciascuna parola.

Come per gli n-gram, i conteggi zero sono un problema (coppie mai viste): in pratica servono smoothing e trattamento delle parole sconosciute (L5); il libro mostra le tabelle senza smoothing.

> **Da saper fare: Stima MLE da un corpus annotato**
>
> Per $A$: aggiungi <s> (e se vuoi </s>) a ogni frase, conta le coppie di tag consecutivi e dividi per il numero di volte che il primo tag compare **come precedente**. Per $B$: conta le coppie (tag, parola) e dividi per il conteggio del tag. Controllo: ogni riga deve sommare a 1. Esercizio 2.

<a id="p-36"></a>

### Slide 36 · Un HMM per il PoS tagging

Fig. 18.9: tre stati, VB1, MD2, NN3, collegati da tutti gli archi di transizione $a_{11}, a_{12}, \dots, a_{33}$ (inclusi gli anelli su se stessi). Da ogni stato una freccia tratteggiata porta a un riquadro azzurro $B_1$, $B_2$, $B_3$ con la sua distribuzione di emissione sull'intero vocabolario: $P(\textit{aardvark}\mid\text{MD}), \dots, P(\textit{will}\mid\text{MD}), \dots, P(\textit{the}\mid\text{MD}), \dots, P(\textit{back}\mid\text{MD}), \dots, P(\textit{zebra}\mid\text{MD})$, e così per VB e NN.

Il tagger completo ha **uno stato per tag** (45 per Penn, 17 per UD), ognuno con la propria distribuzione su $|V|$ parole. Numero di parametri: $N^2$ transizioni (più $N$ iniziali) e $N\cdot|V|$ emissioni, la parte grossa. Con $N = 45$ e $|V| = 50.000$: circa 2.000 transizioni contro 2,25 milioni di emissioni, quasi tutte zero o rarissime.

<a id="p-37"></a>

### Slide 37 · Il tagging HMM come decodifica

Per un modello con variabili nascoste, la **decodifica** (*decoding*) è trovare la sequenza di stati nascosti che corrisponde alla sequenza di osservazioni:

**dato** l'HMM $\lambda = (A, B)$ e le osservazioni $O = o_1\dots o_T$, **trovare** la sequenza di stati più probabile $Q = q_1\dots q_T$.

- $A$ fornisce la probabilità **a priori** di una sequenza di tag;
- $B$ fornisce la **verosimiglianza** di ogni parola osservata sotto un tag;
- per il tagging, osservazioni = parole, stati = tag.

($\pi$ non compare in $\lambda$ perché è incorporata in $A$ come riga <s>.) Le prossime schede scrivono l'obiettivo in termini di quantità che sappiamo contare.

<a id="p-38"></a>

### Slide 38 · L'obiettivo della decodifica

Si sceglie la sequenza di tag più probabile date le parole (Eq. 18.12):

$$\hat t_{1:n} = \operatorname*{argmax}_{t_1\dots t_n} P(t_1\dots t_n\mid w_1\dots w_n)$$

Nella slide le parentesi graffe indicano $\hat t_{1:n}$ come "most probable tag sequence" e $w_1\dots w_n$ come "the observed words". L'argmax è su **tutte** le sequenze di tag: con $N$ tag e $n$ parole sono $N^n$ candidate, troppe da elencare ([scheda 51](L08-sequence-labelling-pos-tagging-e-ner.md#p-51)).

Il problema: non abbiamo un modo diretto per stimare $P(t_{1:n}\mid w_{1:n})$ per frasi intere (ogni frase è quasi unica). Le tre schede seguenti lo riscrivono con Bayes e due approssimazioni.

<a id="p-39"></a>

### Slide 39 · Decodifica: regola di Bayes

Tre righe (Eq. 18.13-18.14):

$$\hat t_{1:n} = \operatorname*{argmax}_{t_{1:n}} P(t_{1:n}\mid w_{1:n}) = \operatorname*{argmax}_{t_{1:n}} \frac{P(w_{1:n}\mid t_{1:n})\,P(t_{1:n})}{P(w_{1:n})} = \operatorname*{argmax}_{t_{1:n}} P(w_{1:n}\mid t_{1:n})\,P(t_{1:n})$$

Prima la **regola di Bayes** (nel riquadro "reminder": $P(x\mid y) = P(y\mid x)P(x)/P(y)$), poi si **elimina il denominatore** (in rosso nella slide): $P(w_{1:n})$ è lo stesso per ogni sequenza di tag candidata, quindi non cambia l'argmax.

È identico al passaggio di Naive Bayes ([scheda 14 della L6](L06-regressione-logistica.md#p-14)): $\hat c = \operatorname{argmax}_c P(d\mid c)P(c)$. Qui la "classe" è un'intera sequenza di tag: verosimiglianza per prior.

<a id="p-40"></a>

### Slide 40 · Decodifica: la probabilità delle parole

Il primo fattore, la verosimiglianza $P(w_1\dots w_n\mid t_1\dots t_n)$ (incorniciato nella slide), si semplifica con l'**indipendenza delle osservazioni**: la probabilità di una parola dipende solo dal suo tag (Eq. 18.15):

$$P(w_1\dots w_n\mid t_1\dots t_n) \approx \prod_{i=1}^{n} P(w_i\mid t_i)$$

Un prodotto di **emissioni**, una per parola. Il simbolo $\approx$ ricorda che è un'approssimazione: nella realtà la parola dipende anche dalle parole vicine (*New* rende più probabile *York*), ma l'HMM lo ignora.

<a id="p-41"></a>

### Slide 41 · Decodifica: la probabilità dei tag

Il secondo fattore, la prior $P(t_1\dots t_n)$, si semplifica con l'**assunzione bigram**: la probabilità di un tag dipende solo dal tag precedente (Eq. 18.16):

$$P(t_1\dots t_n) \approx \prod_{i=1}^{n} P(t_i\mid t_{i-1})$$

È la **regola della catena** ([scheda 11 della L4](L04-modelli-linguistici-n-gram.md#p-11)) troncata dall'assunzione di Markov: esattamente un modello linguistico bigram, ma sui tag invece che sulle parole. Per $i = 1$ il tag precedente è <s>, quindi $P(t_1\mid\langle s\rangle) = \pi_{t_1}$.

<a id="p-42"></a>

### Slide 42 · Probabilità di emissione e di transizione

Mettendo insieme le tre schede (Eq. 18.17), in tre passi: l'obiettivo, Bayes senza denominatore, le due assunzioni:

$$\hat t_{1:n} \approx \operatorname*{argmax}_{t_1\dots t_n}\prod_{i=1}^{n}\underbrace{P(w_i\mid t_i)}_{\text{emissione } B}\ \underbrace{P(t_i\mid t_{i-1})}_{\text{transizione } A}$$

Le due parti corrispondono esattamente a $B$ e $A$. Domanda in fondo alla slide: come si trova la sequenza $t_1,\dots,t_n$ che massimizza questo prodotto senza provarle tutte? Risposta: l'**algoritmo di Viterbi**.

Precisazione sulla didascalia ("maximising the probability of observing the sequence of words"): il prodotto è la probabilità **congiunta** $P(w_{1:n}, t_{1:n})$, non la probabilità delle sole parole; massimizzarla sui tag equivale a massimizzare la posterior $P(t_{1:n}\mid w_{1:n})$.

> **Da saper fare: Derivazione da saper ripetere all'orale**
>
> (1) obiettivo $\operatorname{argmax} P(t\mid w)$; (2) Bayes; (3) via il denominatore, costante rispetto ai tag; (4) indipendenza delle osservazioni: $\prod P(w_i\mid t_i)$; (5) Markov: $\prod P(t_i\mid t_{i-1})$; (6) stima per conteggio di $A$ e $B$. Dire sempre *quale* assunzione giustifica ogni passo.

<a id="p-43"></a>
**Slide 43 · Pausa** — Pausa di 10 minuti; dopo la pausa l'algoritmo di Viterbi (prima della pausa: §18.1-18.4.4).

## Algoritmo di Viterbi

<a id="p-44"></a>
**Slide 44 · Algoritmo di Viterbi** — Terza parte: la decodifica con la programmazione dinamica.

<a id="p-45"></a>

### Slide 45 · L'algoritmo di Viterbi

**Viterbi** restituisce il cammino di stati dell'HMM che assegna **massima probabilità** alla sequenza di osservazioni. È un'istanza di **programmazione dinamica**:

- si costruisce una **matrice di probabilità**, il **reticolo** (*lattice*, *trellis*): una riga per stato, una colonna per istante;
- ogni cella si riempie **ricorsivamente** dalla colonna precedente;
- somiglia all'algoritmo della **distanza di edit minima** (capitolo 2, [scheda 41 della L3](L03-elaborazione-del-testo.md#p-41)).

Il parallelo con la distanza di edit è stretto: là una tabella $D[i,j]$ riempita cella per cella con un **min** su tre predecessori, qui una tabella $v_t(j)$ con un **max** su $N$ predecessori; in entrambi i casi si salvano i **backpointer** e la soluzione si ricostruisce alla fine con il **backtrace** ([scheda 50 della L3](L03-elaborazione-del-testo.md#p-50)). Il sottoproblema "miglior cammino che arriva in questa cella" ha **sottostruttura ottima**: il miglior cammino globale passa per migliori cammini parziali.

<a id="p-46"></a>

### Slide 46 · La ricorsione di Viterbi

Ogni cella del reticolo è (Eq. 18.18):

$$v_t(j) = \max_{q_1,\dots,q_{t-1}} P(q_1\dots q_{t-1},\ o_1\dots o_t,\ q_t = j\mid\lambda)$$

la probabilità che l'HMM sia nello stato $j$ dopo le prime $t$ osservazioni, avendo percorso la sequenza di stati **più probabile** $q_1\dots q_{t-1}$. Si calcola dalla colonna precedente (Eq. 18.19):

$$v_t(j) = \max_{i=1}^{N}\ \underbrace{v_{t-1}(i)}_{\text{cammino precedente}}\ \underbrace{a_{ij}}_{\text{transizione } i\to j}\ \underbrace{b_j(o_t)}_{\text{emissione di } o_t \text{ da } j}$$

- per ogni istante $t$ c'è una cella $v_t(j)$ per ogni tag $j$;
- ogni cella prende la più probabile fra le estensioni dei cammini che vi arrivano;
- un **backpointer** registra quale predecessore $i$ ha dato il massimo.

Nota: $b_j(o_t)$ non dipende da $i$, quindi si può portare fuori dal max: $v_t(j) = b_j(o_t)\max_i v_{t-1}(i)\,a_{ij}$. Rispetto al prodotto completo della [scheda 42](L08-sequence-labelling-pos-tagging-e-ner.md#p-42) (richiamato in piccolo in alto a destra) l'unica differenza è che il max viene fatto passo per passo invece che sull'intera sequenza.

<a id="p-47"></a>

### Slide 47 · Viterbi in pseudocodice

Fig. 18.10 del libro, quattro fasi:

1. **Inizializzazione** ($t = 1$): per ogni stato $s$, $\text{viterbi}[s,1] = \pi_s\cdot b_s(o_1)$, backpointer 0.
2. **Ricorsione** ($t = 2\dots T$): per ogni stato $s$, $\text{viterbi}[s,t] = \max_{s'} \text{viterbi}[s',t-1]\cdot a_{s',s}\cdot b_s(o_t)$ e $\text{backpointer}[s,t] = \operatorname{argmax}_{s'}$ della stessa quantità.
3. **Terminazione**: $\text{bestpathprob} = \max_s \text{viterbi}[s,T]$, $\text{bestpathpointer} = \operatorname{argmax}_s \text{viterbi}[s,T]$.
4. **Backtrace**: dallo stato finale migliore si seguono i backpointer all'indietro nel tempo; si restituiscono il cammino e la sua probabilità.

Due matrici $N\times T$ (probabilità e backpointer). Due cicli annidati su $t$ e $s$, più il max interno su $s'$: da qui il costo $O(N^2T)$ ([scheda 53](L08-sequence-labelling-pos-tagging-e-ner.md#p-53)).

> **Approfondimento: In pratica si lavora in log-spazio**
>
> Moltiplicare molte probabilità piccole porta all'**underflow** (nell'esempio Janet si arriva a $10^{-15}$ in sole 5 parole). Come per i modelli n-gram ([scheda 22 della L4](L04-modelli-linguistici-n-gram.md#p-22)) si usano i logaritmi: $\log v_t(j) = \max_i[\log v_{t-1}(i) + \log a_{ij}] + \log b_j(o_t)$. Il max non cambia perché il log è monotono; i prodotti diventano somme. È esattamente la forma che assumerà Viterbi per il CRF ([scheda 80](L08-sequence-labelling-pos-tagging-e-ner.md#p-80)). Sostituendo il max con una somma si ottiene invece l'algoritmo **forward**, che calcola $P(O\mid\lambda)$ (appendice A del libro, non in programma qui).

<a id="p-48"></a>

### Slide 48 · Un esempio numerico: The fans watch the race

Esempio del docente, tre tag (DT, NN, VB), frase *The fans watch the race*.

| A | DT | NN | VB |
| --- | --- | --- | --- |
| <s> | 1,0 | 0 | 0 |
| DT | 0 | 0,9 | 0,1 |
| NN | 0 | 0,5 | 0,5 |
| VB | 0,5 | 0,5 | 0 |

| B | the | fans | watch | race |
| --- | --- | --- | --- | --- |
| DT | 0,2 | 0 | 0 | 0 |
| NN | 0 | 0,1 | 0,3 | 0,1 |
| VB | 0 | 0,2 | 0,15 | 0,3 |

- Righe di $A$: riga = tag precedente, colonna = tag successivo; tutte sommano a 1 (verificato). La riga <s> fa da $\pi$: ogni frase comincia con DT.
- Le righe di $B$ **non** sommano a 1 perché sono mostrate solo 4 parole del vocabolario (DT emette anche *a, this*...).
- Gli zeri contano: NN→DT = 0 e VB→VB = 0 escluderanno interi cammini.

Si tratta di numeri inventati per l'esempio, "come se" stimati contando su un corpus.

<a id="p-49"></a>

### Slide 49 · Le emissioni da sole non bastano

Primo tentativo: scegliere per ogni parola il tag con l'emissione più alta, una parola alla volta, usando solo $B$ (i massimi di colonna sono riquadrati in rosso).

|  | the | fans | watch | the | race |
| --- | --- | --- | --- | --- | --- |
| migliore per B | DT | VB (0,2) | NN (0,3) | DT | VB (0,3) |
| corretto | DT | NN | VB | DT | NN |

Tre errori su cinque. Il problema è che $b_j(w) = P(w\mid j)$ non è nemmeno la quantità giusta per scegliere il tag di una parola isolata (servirebbe $P(j\mid w)$), e soprattutto ignora il contesto: dopo un DT un verbo è improbabile.

Sono le **transizioni** a correggere: $P(\text{VB}\mid\text{DT}) = 0{,}1$ contro $P(\text{NN}\mid\text{DT}) = 0{,}9$. Precisazione sulla didascalia: le transizioni non *escludono* un verbo dopo un determinante (la probabilità è 0,1, non 0), lo **penalizzano** abbastanza da farlo perdere: a *fans* il cammino DT→VB vale 0,004 contro 0,018 di DT→NN (scheda seguente).

<a id="p-50"></a>

### Slide 50 · Decodifica con Viterbi passo per passo

Il reticolo completo: colonne = parole, righe = NN, DT, VB; celle grigie = 0 perché $B$ dà probabilità zero a quel tag per quella parola. Sopra/sotto ogni cella il conto $v_{t-1}(i)\times(a_{ij}\,b_j(o_t))$. Ricalcolato cella per cella con numpy: **tutti i valori della slide sono corretti**.

|  | the | fans | watch | the | race |
| --- | --- | --- | --- | --- | --- |
| NN | 0 | 0,018 (DT) | 0,0027 (NN) | 0 | $1{,}215\cdot10^{-5}$ (DT) |
| DT | 0,2 | 0 | 0 | 0,000135 (VB) | 0 |
| VB | 0 | 0,004 (DT) | 0,00135 (NN) | 0 | $4{,}05\cdot10^{-6}$ (DT) |

(fra parentesi il backpointer). I passaggi:

- *the*: $v_1(\text{DT}) = 1{,}0\times 0{,}2 = 0{,}2$.
- *fans*: NN $= 0{,}2\times(0{,}9\times0{,}1) = 0{,}018$; VB $= 0{,}2\times(0{,}1\times0{,}2) = 0{,}004$.
- *watch*: NN = max(da NN $0{,}018\times0{,}5\times0{,}3 = 0{,}0027$; da VB $0{,}004\times0{,}15 = 0{,}0006$) = 0,0027; VB = max(da NN $0{,}018\times0{,}5\times0{,}15 = 0{,}00135$; da VB $0{,}004\times 0 = 0$) = 0,00135.
- *the*: DT = max(da NN $0{,}0027\times 0 = 0$; da VB $0{,}00135\times0{,}5\times0{,}2 = 0{,}000135$). NN era la cella migliore a *watch*, ma NN→DT = 0: ogni cammino che passa di lì muore (nota in rosso).
- *race*: NN $= 0{,}000135\times(0{,}9\times0{,}1) = 1{,}215\cdot10^{-5}$; VB $= 0{,}000135\times(0{,}1\times0{,}3) = 4{,}05\cdot10^{-6}$.

Fine: NN batte VB; **backtrace** NN ← DT ← VB ← NN ← DT, cioè **DT NN VB DT NN** (frecce verdi spesse). Controllo per forza bruta sulle $3^5 = 243$ sequenze: stessa risposta.

> **Da saper fare: La lezione dell'esempio**
>
> La sequenza si decide **solo alla fine**: a *watch* la cella migliore era NN, ma il cammino ottimo passa per VB, perché la parola successiva (*the*) richiede una transizione verso DT che solo VB permette. Un tagger **greedy** (sceglie il tag migliore a ogni passo e prosegue) avrebbe preso NN a *watch* e poi si sarebbe trovato con probabilità 0. Viterbi conserva il miglior cammino **per ogni stato**, non solo il migliore in assoluto. Da saper rifare a mano: esercizi 3 e 4.

<a id="p-51"></a>

### Slide 51 · Forza bruta

Figura: un reticolo con 5 stati nascosti per 3 istanti, ogni nodo collegato a tutti i nodi della colonna successiva (fascio di linee grigie).

Elencare ogni cammino uno per uno: ogni stato si ramifica in $N$ successori a ogni passo, quindi i cammini sono $N^L$ (qui $L$ = lunghezza della frase, il $T$ del libro). Il costo è **esponenziale** nella lunghezza: $O(N^L)$ (a rigore $O(L\cdot N^L)$, perché ogni cammino richiede $L$ moltiplicazioni).

Esempio: 45 tag e una frase di 20 parole danno $45^{20}\approx 1{,}16\cdot 10^{33}$ cammini.

<a id="p-52"></a>

### Slide 52 · Viterbi

Stesso reticolo, ma ora per ogni nodo sopravvive **una sola** freccia entrante (verde): quella del miglior predecessore. Le altre, grigio chiaro, vengono scartate.

Conteggio: per ogni nodo si confrontano $N$ modi di entrarvi, ci sono $N$ nodi per colonna, e la colonna si ripete $L$ volte: $O(L\cdot N^2)$. Il lavoro **per passo** non cresce con la lunghezza della frase.

Perché si può scartare: due cammini che arrivano nello stesso stato $j$ al tempo $t$ hanno lo stesso futuro (per l'assunzione di Markov il seguito dipende solo da $j$). Quello con probabilità minore resterà minore qualunque cosa accada dopo, quindi non potrà mai diventare ottimo.

<a id="p-53"></a>

### Slide 53 · Perché vince la programmazione dinamica

|  | Forza bruta | Viterbi |
| --- | --- | --- |
| Costo | $O(N^L)$ | $O(L\cdot N^2)$ |
| Crescita | esponenziale nella lunghezza | lineare nella lunghezza, quadratica nel numero di tag |
| 45 tag, 20 parole | $45^{20}\approx 1{,}2\cdot10^{33}$: senza speranza | $20\cdot 45^2 = 40.500$, "circa 40.000" |

Il rapporto fra i due è circa $3\cdot10^{28}$. Tutto il risparmio poggia su un'osservazione: un cammino che non è ottimo per arrivare in una cella non può diventare ottimo più avanti (**principio di ottimalità**, conseguenza dell'assunzione di Markov). Memoria: $O(N\cdot L)$ per le due matrici.

> **Da saper fare: Contare operazioni e cammini**
>
> Con $N$ tag e $L$ parole: cammini $N^L$; celle $N\cdot L$; ogni cella fa $N$ prodotti e un max, quindi circa $L\cdot N^2$ operazioni (la prima colonna costa solo $N$). Per UPOS ($N = 17$) e $L = 10$: $17^{10}\approx 2{,}0\cdot10^{12}$ cammini contro $10\cdot 289 = 2.890$ operazioni. Esercizio 5.

<a id="p-54"></a>

### Slide 54 · L'esempio del libro: Janet will back the bill

Fig. 18.11: il reticolo per *Janet will back the bill* con 7 tag per colonna (DT, RB, NN, JJ, VB, MD, NNP). Gli stati in grigio hanno emissione zero per quella parola e sono esclusi; restano attivi:

- *Janet*: solo NNP;
- *will*: NN, VB, MD;
- *back*: RB, NN, JJ, VB (quattro tag, cfr. [scheda 18](L08-sequence-labelling-pos-tagging-e-ner.md#p-18));
- *the*: DT e NNP (in titoli come *Somewhere Over the Rainbow* tutte le parole sono NNP);
- *bill*: NN, VB.

Le frecce sottili collegano i nodi attivi di colonne vicine; quelle spesse tracciano il cammino corretto **NNP MD VB DT NN**. Il numero di cammini possibili non nulli è solo $1\cdot3\cdot4\cdot2\cdot2 = 48$: gli zeri di $B$ potano molto, ma su frasi vere e con 45 tag serve comunque Viterbi.

<a id="p-55"></a>

### Slide 55 · Probabilità di transizione (matrice A)

Fig. 18.12: $P(t_i\mid t_{i-1})$ stimate sul WSJ **senza smoothing**. Righe = tag condizionante (precedente), colonne = tag successivo; la riga <s> è la distribuzione iniziale.

|  | NNP | MD | VB | JJ | NN | RB | DT |
| --- | --- | --- | --- | --- | --- | --- | --- |
| <s> | 0,2767 | 0,0006 | 0,0031 | 0,0453 | 0,0449 | 0,0510 | 0,2026 |
| NNP | 0,3777 | 0,0110 | 0,0009 | 0,0084 | 0,0584 | 0,0090 | 0,0025 |
| MD | 0,0008 | 0,0002 | 0,7968 | 0,0005 | 0,0008 | 0,1698 | 0,0041 |
| VB | 0,0322 | 0,0005 | 0,0050 | 0,0837 | 0,0615 | 0,0514 | 0,2231 |
| JJ | 0,0366 | 0,0004 | 0,0001 | 0,0733 | 0,4509 | 0,0036 | 0,0036 |
| NN | 0,0096 | 0,0176 | 0,0014 | 0,0086 | 0,1216 | 0,0177 | 0,0068 |
| RB | 0,0068 | 0,0102 | 0,1011 | 0,1012 | 0,0120 | 0,0728 | 0,0479 |
| DT | 0,1147 | 0,0021 | 0,0002 | 0,2157 | 0,4744 | 0,0102 | 0,0017 |

Lettura: $P(\text{MD}\mid\text{NNP}) = 0{,}0110$; $P(\text{VB}\mid\text{MD}) = 0{,}7968$ (il 0,80 della [scheda 35](L08-sequence-labelling-pos-tagging-e-ner.md#p-35)); dopo DT vengono soprattutto NN (0,47) e JJ (0,22), quasi mai VB (0,0002). Le righe **non sommano a 1** (da 0,18 per RB a 0,97 per MD) perché sono mostrate solo 7 colonne dei 45 tag: il resto della massa va ai tag non mostrati.

<a id="p-56"></a>

### Slide 56 · Verosimiglianze delle osservazioni (matrice B)

Fig. 18.13: $P(w\mid t)$ dal WSJ, senza smoothing e "leggermente semplificate" (dice il libro).

|  | Janet | will | back | the | bill |
| --- | --- | --- | --- | --- | --- |
| NNP | 0,000032 | 0 | 0 | 0,000048 | 0 |
| MD | 0 | 0,308431 | 0 | 0 | 0 |
| VB | 0 | 0,000028 | 0,000672 | 0 | 0,000028 |
| JJ | 0 | 0 | 0,000340 | 0 | 0 |
| NN | 0 | 0,000200 | 0,000223 | 0 | 0,002337 |
| RB | 0 | 0 | 0,010446 | 0 | 0 |
| DT | 0 | 0 | 0 | 0,506099 | 0 |

Lettura per riga: $P(\textit{will}\mid\text{MD}) = 0{,}308431$ (circa il 4046/13124 = 0,3083 della [scheda 35](L08-sequence-labelling-pos-tagging-e-ner.md#p-35); la piccola differenza viene dalla semplificazione). $P(\textit{the}\mid\text{DT}) = 0{,}51$: metà dei determinanti sono *the*. Le emissioni dei tag aperti sono minuscole (NN ha decine di migliaia di parole). Gli zeri sono coppie parola-tag mai viste nel training: senza smoothing una parola nuova o un uso nuovo sarebbero impossibili.

<a id="p-57"></a>

### Slide 57 · Il backtrace di Viterbi

Fig. 18.14 del libro: le colonne *Janet* e *will* compilate, la terza solo impostata (max × emissione), le altre vuote. In basso a sinistra il nodo $\pi$ da cui partono le probabilità iniziali; le frecce tratteggiate blu sono il backtrace.

- Colonna 1: $v_1(\text{NNP}) = 0{,}28\times0{,}000032 \approx 0{,}000009$; per MD, VB, JJ la probabilità iniziale moltiplica un'emissione nulla, quindi 0.
- Colonna 2: l'unico predecessore non nullo è NNP. $v_2(\text{MD}) = \max\times 0{,}308 = 2{,}772\cdot10^{-8}$, $v_2(\text{NN}) = \max\times0{,}0002 \approx 10^{-10}$, $v_2(\text{VB}) = \max\times0{,}000028$.
- Colonna 3 (*back*): VB, JJ, NN, RB moltiplicano il max per 0,00067, 0,00034, 0,000223, 0,0104.

Completando il reticolo il backtrace restituisce **NNP MD VB DT NN**, la sequenza corretta (il libro lo lascia come esercizio: è l'esercizio 4 qui sotto, risolto con numpy).

> **Attenzione (errore nelle slide): Due valori della figura sono sbagliati**
>
> (1) Sulla freccia NNP→MD c'è scritto **$.000009 \times .01 = .9\text{e-}8$**: $9\cdot10^{-6}\times 0{,}01 = 9\cdot10^{-8}$, non $0{,}9\cdot10^{-8}$. Il valore successivo $9\cdot10^{-8}\times0{,}308 = 2{,}772\cdot10^{-8}$ conferma che si intendeva $9\cdot10^{-8}$.
>
> (2) **$v_2(\text{VB}) = 2{,}5\text{e-}13$** è sbagliato: l'unico predecessore è NNP, quindi $v_2(\text{VB}) = 0{,}000009\times P(\text{VB}\mid\text{NNP})\times 0{,}000028 = 9\cdot10^{-6}\times0{,}0009\times0{,}000028 = 2{,}27\cdot10^{-13}\approx 2{,}2\cdot10^{-13}$ (con i valori esatti delle tabelle $2{,}23\cdot10^{-13}$).
>
> Inoltre la figura arrotonda $P(\text{MD}\mid\text{NNP}) = 0{,}0110$ a 0,01 e $\pi_{\text{NNP}} = 0{,}2767$ a 0,28: con i valori delle tabelle $v_2(\text{MD}) = 8{,}854\cdot10^{-6}\times0{,}0110\times0{,}308431 = 3{,}00\cdot10^{-8}$, non 2,772e-8 (arrotondamento, non errore). Nessuno di questi cambia il cammino finale. Errori ereditati dalla Fig. 18.14 del libro; verificati con numpy.

## Named entity recognition

<a id="p-58"></a>
**Slide 58 · Named entity recognition** — Quarta parte: trovare e classificare span di testo.

<a id="p-59"></a>

### Slide 59 · Named entity

Una **named entity** è, grosso modo, qualunque cosa a cui ci si possa riferire con un **nome proprio**. I quattro tipi più comuni (Fig. 18.5):

| Tipo | Tag | Categorie | Esempio |
| --- | --- | --- | --- |
| Persone | PER | persone, personaggi | *Turing* is a giant of computer science. |
| Organizzazioni | ORG | aziende, squadre | *The IPCC* warned about the cyclone. |
| Luoghi | LOC | regioni, montagne, mari | *Mt. Sanitas* is in *Sunshine Canyon*. |
| Entità geopolitiche | GPE | paesi, stati | *Palo Alto* is raising the fees for parking. |

**GPE** e LOC si distinguono perché un'entità geopolitica ha un governo e può "agire" (*Palo Alto* alza le tariffe), un luogo fisico no. Il termine si estende per comodità a **date, orari, prezzi**, che non sono entità; molte applicazioni aggiungono tipi specifici (proteine, geni, prodotti, opere). Il compito era già stato presentato nella [scheda 47 della L1](L01-introduzione-al-corso.md#p-47).

<a id="p-60"></a>

### Slide 60 · Riconoscimento e classificazione

La NER sono due problemi intrecciati:

- **Riconoscimento: trovare lo span**. Le entità sono spesso frasi di più parole (*United States of America*); nel PoS tagging ogni parola ha esattamente un tag, nella NER l'unità è uno **span di lunghezza ignota**; nulla nell'input segna i confini; la maggior parte delle parole non è un'entità.
- **Classificazione: assegnare il tipo** (PER, LOC, ORG, GPE, o nessuno). La stessa stringa può avere tipi diversi: *JFK* è una persona, un aeroporto, e un numero qualsiasi di scuole, ponti, strade. I **gazetteer** (liste di nomi) aiutano ma non risolvono: decide il contesto.

Le decisioni su confini e tipo interagiscono. A differenza del PoS tagging c'è un **problema di segmentazione**: decidere che cos'è un'entità e dove comincia e finisce. La soluzione standard per ridurlo a etichettatura parola per parola è il BIO ([scheda 64](L08-sequence-labelling-pos-tagging-e-ner.md#p-64)).

<a id="p-61"></a>

### Slide 61 · L'output di un named entity recognizer

Un paragrafo di notizie con le entità tra parentesi quadre etichettate:

*Citing high fuel prices, [ORG United Airlines] said [TIME Friday] it has increased fares by [MONEY \$6] per round trip on flights to some cities also served by lower-cost carriers. [ORG American Airlines], a unit of [ORG AMR Corp.], immediately matched the move, spokesman [PER Tim Wagner] said. [ORG United], a unit of [ORG UAL Corp.], said the increase took effect [TIME Thursday] and applies to most routes where it competes against discount carriers, such as [LOC Chicago] to [LOC Dallas] and [LOC Denver] to [LOC San Francisco].*

Conteggio (il libro: 13 menzioni): **5 ORG** (United Airlines, American Airlines, AMR Corp., United, UAL Corp.), **4 LOC**, **2 TIME**, **1 PER**, **1 MONEY**. TIME e MONEY sono l'estensione a cose che non sono entità. Da notare che *United* e *United Airlines* sono due menzioni della stessa azienda: collegarle è un compito diverso (coreferenza, entity linking).

<a id="p-62"></a>

### Slide 62 · A che cosa serve la NER

Le entità sono un primo passo utile in moltissimi compiti:

| Compito | Che cosa danno le entità |
| --- | --- |
| Sentiment analysis | il sentiment di un consumatore verso una **particolare** entità (aspect-based) |
| Question answering | le risposte candidate a *who, where, when* |
| Entity linking | un ponte fra la menzione e Wikipedia o un'altra base di conoscenza |
| Rappresentazione semantica | eventi e relazioni fra i partecipanti |

L'ultima riga è il ponte verso la **relation extraction** ([scheda 48 della L1](L01-introduzione-al-corso.md#p-48)): prima si trovano le entità, poi le relazioni fra loro (chi lavora per chi, cosa si trova dove).

<a id="p-63"></a>

### Slide 63 · Ambiguità di tipo

Fig. 18.6: quattro frasi, la stessa stringa *Washington*, quattro tipi:

- [PER Washington] was born into slavery on the farm of James Burroughs. (Booker T. Washington, persona)
- [ORG Washington] went up 2 games to 1 in the four-game series. (una squadra)
- Blair arrived in [LOC Washington] for what may well be his last state visit. (la città come luogo)
- In June, [GPE Washington] passed a primary seatbelt law. (lo stato come entità politica)

Nessuna conoscenza lessicale risolve questo caso: un dizionario direbbe solo che *Washington* è un nome proprio. Decide il **contesto**: *was born* → persona; *went up 2 games to 1* → squadra; *arrived in* → luogo; *passed a law* → entità politica. Per questo servono modelli che guardino le parole vicine (feature del CRF, o contesto bidirezionale nei modelli neurali).

<a id="p-64"></a>

### Slide 64 · BIO tagging

Il **BIO tagging** (Ramshaw e Marcus, 1995) trasforma il riconoscimento di span in etichettatura **parola per parola**:

- **B** (*begin*): il token che **apre** uno span;
- **I** (*inside*): token all'interno di uno span (dopo il primo);
- **O** (*outside*): token fuori da ogni span.

I tag catturano sia il **confine** sia il **tipo** (B-PER, I-ORG...). Contiene esattamente la stessa informazione della notazione con parentesi, e permette di assegnare una sola etichetta $y_i$ a ogni parola $x_i$, come nel PoS tagging: qualunque sequence labeller (HMM, CRF, RNN, transformer) si può usare per la NER senza modifiche.

Vincolo implicito: **I-X può seguire solo B-X o I-X**; la sequenza O I-PER è malformata. Un CRF impara questo vincolo dalle feature di transizione $\langle y_{i-1}, y_i\rangle$ (peso molto negativo per O→I-PER).

<a id="p-65"></a>

### Slide 65 · BIO tagging: un esempio

La frase *[PER Jane Villanueva] of [ORG United], a unit of [ORG United Airlines Holding], discussed the [LOC Chicago] route.* e la tabella sotto:

| Jane | Villanueva | of | United | Airlines | Holding | discussed | the | Chicago | route | . |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B-PER | I-PER | O | B-ORG | I-ORG | I-ORG | O | O | B-LOC | O | O |

11 token, 11 etichette; dalla tabella si rileggono tre span: PER *Jane Villanueva*, ORG *United Airlines Holding*, LOC *Chicago*. Ogni B apre uno span nuovo, gli I lo allungano, il primo O (o un nuovo B) lo chiude.

> **Attenzione (errore nelle slide): La tabella non è il BIO della frase sopra**
>
> La tabella salta i token *, a unit of United*: legge "of United Airlines Holding", mentre la frase ha due ORG distinti. Il BIO corretto della frase completa (17 token, **quattro** span) è:
>
> Jane/B-PER Villanueva/I-PER of/O United/B-ORG ,/O a/O unit/O of/O United/B-ORG Airlines/I-ORG Holding/I-ORG ,/O discussed/O the/O Chicago/B-LOC route/O ./O
>
> La tabella a 11 token è coerente con sé stessa (tre span), ma è un estratto accorciato, ereditato dalla Fig. 18.7 del libro. Verificato convertendo gli span in BIO con uno script.

<a id="p-66"></a>

### Slide 66 · Quanti tag servono al BIO?

Con $n$ tipi di entità: **un solo** tag O, più un B e un I per ogni tipo:

$$\#\text{tag BIO} = 2n + 1$$

Esempio della slide: $n = 4$ (PER, LOC, ORG, GPE) → $2\cdot4+1 = 9$ etichette: O, B-PER, I-PER, B-LOC, I-LOC, B-ORG, I-ORG, B-GPE, I-GPE.

Per confronto (stesso ragionamento): **IO** usa $n + 1$ tag (5 per $n = 4$), **BIOES** ne usa $4n + 1$ (17 per $n = 4$; B, I, E, S per tipo più O). Per OntoNotes, con 18 tipi, il BIO ha 37 etichette. Il numero di tag conta perché Viterbi costa $O(N^2T)$: passare da BIO a BIOES moltiplica il costo per circa $(17/9)^2\approx 3{,}6$.

<a id="p-67"></a>

### Slide 67 · Varianti del BIO: IO e BIOES

Fig. 18.7 del libro: la stessa frase in tre schemi.

| Parola | IO | BIO | BIOES |
| --- | --- | --- | --- |
| Jane | I-PER | B-PER | B-PER |
| Villanueva | I-PER | I-PER | E-PER |
| of | O | O | O |
| United | I-ORG | B-ORG | B-ORG |
| Airlines | I-ORG | I-ORG | I-ORG |
| Holding | I-ORG | I-ORG | E-ORG |
| discussed / the | O | O | O |
| Chicago | I-LOC | B-LOC | S-LOC |
| route / . | O | O | O |

- **IO** elimina B e **perde informazione**: due entità dello stesso tipo adiacenti (*the Juventus Inter match*: I-ORG I-ORG) diventano indistinguibili da un'unica entità di due parole.
- **BIOES** aggiunge **E** (*end*, ultimo token di uno span lungo) e **S** (*single*, span di una sola parola). Più tag, ma confini più espliciti, spesso utile ai modelli.

(La frase in alto nella slide è la versione del libro, *said the fare applies to the Chicago route*, diversa dalla tabella, che come nella [scheda 65](L08-sequence-labelling-pos-tagging-e-ner.md#p-65) salta *, a unit of United*.)

<a id="p-68"></a>

### Slide 68 · Algoritmi standard per la NER

Un sequence labeller si addestra su testo annotato in BIO. Quattro famiglie, che differiscono per **come nascono le feature**:

| Famiglia | Membri | Feature |
| --- | --- | --- |
| Modello di sequenza generativo | HMM | progettate a mano, molto vincolate (solo tag precedente e parola) |
| Modello di sequenza discriminativo | CRF, MEMM | progettate a mano, senza vincoli |
| Modello di sequenza neurale | RNN, transformer | apprese dai dati |
| Language model preaddestrato | BERT con fine-tuning | apprese, poi trasferite |

La tabella è una storia della NER in quattro righe: dagli HMM (Bikel et al., 1997) ai CRF (McCallum e Li, 2003), poi CRF sopra reti convoluzionali (Collobert et al., 2011) e BiLSTM-CRF, poi transformer. Spesso uno strato CRF resta sopra la rete neurale per imporre la coerenza delle transizioni BIO.

<a id="p-69"></a>

### Slide 69 · Perché un HMM non basta

Gli indizi che identificano le entità sono proprio quelli che un HMM **non può esprimere**:

- **Parole sconosciute**: nella NER dominano (nomi nuovi di continuo), e per loro $P(\text{parola}\mid\text{tag})$ non è mai stata contata: l'HMM non ha evidenza sulla parola, solo le transizioni dai tag vicini.
- **Maiuscole e morfologia** aiuterebbero: una parola con l'iniziale maiuscola è probabilmente un nome proprio.
- Anche le **parole vicine**: dopo *Mr.* viene una persona, prima di *Inc.* un'organizzazione; ma l'HMM vede il vicino solo attraverso il suo tag, ed entrambi sono NNP.
- In un modello generativo ogni indizio va codificato dentro $P(\text{tag}\mid\text{tag})$ o $P(\text{parola}\mid\text{tag})$, e diventa più difficile a ogni feature aggiunta (il libro, nota 2: servirebbero condizionamenti sempre più complicati).

Stesso problema di Naive Bayes rispetto alla regressione logistica (L6): con un modello generativo è difficile aggiungere feature correlate fra loro; con un modello log-lineare discriminativo basta aggiungere un peso.

## Conditional random field

<a id="p-70"></a>
**Slide 70 · Conditional random field** — Quinta parte: un modello discriminativo per sequenze.

<a id="p-71"></a>

### Slide 71 · HMM e CRF a confronto

Due grafi: a sinistra (HMM) la catena di $Y$ con frecce orizzontali e frecce verticali $Y\to X$; a destra (CRF) i nodi $Y$ collegati fra loro da archi senza verso, e ogni $Y$ collegato a **tutte** le $X$ (fascio verde).

- **HMM (generativo)**: per massimizzare $P(Y\mid X)$ passa da Bayes e dalla verosimiglianza $P(X\mid Y)$:
  $$\hat Y = \operatorname*{argmax}_Y p(X\mid Y)\,p(Y) = \operatorname*{argmax}_Y \prod_i p(x_i\mid y_i)\prod_i p(y_i\mid y_{i-1})$$
- **CRF (discriminativo)**: calcola direttamente la posterior, $\hat Y = \operatorname{argmax}_{Y} P(Y\mid X)$, su sequenze intere; molte meno assunzioni, quindi le feature possono essere qualunque cosa (anche guardare tutta $X$).

Un CRF **non** calcola una probabilità per ogni tag a ogni posizione: calcola punteggi locali, li somma, e normalizza **una volta sola** sull'intera sequenza (normalizzazione globale). È la differenza con il MEMM, che normalizza a ogni passo.

<a id="p-72"></a>

### Slide 72 · Il modello CRF

Un CRF è un modello **log-lineare** che assegna una probabilità a un'intera sequenza di uscita $Y$, fra tutte le sequenze possibili $\mathcal Y$, data l'intera sequenza di ingresso $X$:

$$P(Y\mid X) = \frac{1}{Z(X)}\exp\Big(\sum_{k=1}^{K} w_k F_k(X, Y)\Big)\qquad Z(X) = \sum_{Y'\in\mathcal Y}\exp\Big(\sum_{k=1}^{K} w_k F_k(X, Y')\Big)$$

$w_k$ sono i pesi appresi, $F_k$ le $K$ **feature globali**; $Z(X)$ è il **normalizzatore** (funzione di partizione), una somma su tutte le $N^n$ sequenze di tag.

Il paragone del libro: una "gigantesca versione sequenziale della **regressione logistica multinomiale**". Confronta con la softmax della [scheda 10 della L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-10): là $P(y_k\mid x) = \exp(\mathbf w_k\cdot\mathbf x)/\sum_j\exp(\mathbf w_j\cdot\mathbf x)$ su $K$ classi; qui le "classi" sono tutte le possibili sequenze di tag, il punteggio di ciascuna è $\sum_k w_k F_k(X,Y)$, e la softmax è fatta su $\mathcal Y$.

<a id="p-73"></a>

### Slide 73 · Feature globali e locali

Le $K$ funzioni $F_k$ sono **globali**: ciascuna è una proprietà dell'intero input $X$ e dell'intero output $Y$. Ognuna si scompone in una **somma di feature locali** $f_k$ su tutte le posizioni $i$ (Eq. 18.26):

$$F_k(X, Y) = \sum_{i=1}^{n} f_k(y_{i-1}, y_i, X, i)$$

Una feature locale può usare $y_i$, $y_{i-1}$, tutto l'input $X$ e la posizione $i$. In pratica $F_k$ **conta quante volte** la feature $f_k$ scatta nella frase: se $f_k$ = "$y_i$ = DT e $x_i$ = *the*" e la frase ha due *the* taggati DT, $F_k = 2$.

Perché è importante: sommando sulle posizioni c'è **un insieme fisso di $K$ pesi** che funziona per frasi di qualunque lunghezza (il peso $w_k$ è condiviso da tutte le posizioni). Si apprende un peso per ogni feature globale $F_k$, non per ogni occorrenza locale.

<a id="p-74"></a>

### Slide 74 · Il CRF a catena lineare

Limitare ogni feature locale a $y_i$ e $y_{i-1}$ (oltre a $X$ e $i$) è ciò che rende la catena **lineare**. Nella figura i nodi $Y$ sono collegati solo a quelli adiacenti (azzurro), mentre ogni $Y$ resta collegato a tutte le $X$ (verde): sull'input nessun vincolo.

- È la versione usata quasi ovunque nell'elaborazione del linguaggio.
- È anche ciò che mantiene utilizzabili **Viterbi** (decodifica) e **forward-backward** (calcolo di $Z(X)$ e dei gradienti in training).
- Un CRF generale può condizionare su tag lontani come $y_{i-4}$, e richiede un'inferenza più complessa.

La dipendenza fra le uscite è la stessa dell'HMM bigram (solo il tag precedente), ma la dipendenza dall'input è libera: ecco perché il CRF "corrisponde" all'HMM ma è più espressivo.

<a id="p-75"></a>

### Slide 75 · Template di feature

Il progettista sceglie i **template**; le feature vere e proprie sono generate **automaticamente** da ogni istanza del training. Feature lecite (valori 0/1, $\mathbb 1\{\cdot\}$ vale 1 se la condizione è vera):

- $\mathbb 1\{x_i = \textit{the},\ y_i = \text{DET}\}$
- $\mathbb 1\{y_i = \text{PROPN},\ x_{i+1} = \textit{Street},\ y_{i-1} = \text{NUM}\}$
- $\mathbb 1\{y_i = \text{VERB},\ y_{i-1} = \text{AUX}\}$

Template: $\langle y_i, x_i\rangle$, $\langle y_i, y_{i-1}\rangle$, $\langle y_i, x_{i-1}, x_{i+2}\rangle$. Su *Janet/NNP will/MD back/VB the/DT bill/NN*, quando $x_i$ = *back* generano (numeri arbitrari):

- `f3743`: $y_i$ = VB e $x_i$ = *back* (template parola-tag, l'equivalente di un'emissione);
- `f156`: $y_i$ = VB e $y_{i-1}$ = MD (template tag-tag, l'equivalente di una transizione);
- `f99732`: $y_i$ = VB e $x_{i-1}$ = *will* e $x_{i+2}$ = *bill* (impossibile in un HMM: guarda parole diverse da $x_i$).

È la stessa logica delle feature della regressione logistica multinomiale, che dipendono dalla coppia (input, classe) ([scheda 15 della L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-15)).

<a id="p-76"></a>

### Slide 76 · Come scatta una feature

Esempio del docente: una feature vale 1 o 0 in una posizione, per **una** tagging candidata. Due candidate per *Janet will back the bill*: $Y$ = NNP MD **VB** DT NN e $Y'$ = NNP MD **NN** DT NN; differiscono solo in $i = 3$ (*back*).

| Feature in $i = 3$ | Template | Peso | $Y$ | $Y'$ |
| --- | --- | --- | --- | --- |
| $y_i$ = VB, $x_i$ = back | $\langle y_i, x_i\rangle$ | +2,1 | 1 | 0 |
| $y_i$ = NN, $x_i$ = back | $\langle y_i, x_i\rangle$ | −0,4 | 0 | 1 |
| $y_i$ = VB, $y_{i-1}$ = MD | $\langle y_i, y_{i-1}\rangle$ | +1,5 | 1 | 0 |
| $y_i$ = NN, $y_{i-1}$ = MD | $\langle y_i, y_{i-1}\rangle$ | −1,2 | 0 | 1 |
| $y_i$ = VB, $x_{i-1}$ = will, $x_{i+2}$ = bill | $\langle y_i, x_{i-1}, x_{i+2}\rangle$ | +0,8 | 1 | 0 |

Punteggio in $i = 3$ = somma dei pesi delle feature che scattano: $Y$: $2{,}1 + 1{,}5 + 0{,}8 = 4{,}4$; $Y'$: $-0{,}4 - 1{,}2 = -1{,}6$ (verificato). Pesi illustrativi. Poi si sommano i punteggi di tutte le posizioni, si esponenzia e si normalizza su tutte le taggature: questo è $P(Y\mid X)$. Le due candidate coincidono ovunque tranne in $i = 3$, quindi nel rapporto $P(Y\mid X)/P(Y'\mid X)$ si semplificano $Z(X)$ e tutte le feature uguali; resta la differenza dei punteggi in $i = 3$ e in $i = 4$ (dove la feature di transizione vede DT dopo VB in un caso e DT dopo NN nell'altro, con pesi non mostrati). Limitandosi alla posizione 3: $e^{4{,}4-(-1{,}6)} = e^{6}\approx 403$ a favore di $Y$.

> **Da saper fare: Punteggio e probabilità di una sequenza in un CRF**
>
> (1) Per ogni posizione elenca le feature che scattano con la tagging candidata; (2) somma i loro pesi, poi somma su tutte le posizioni: è $s(Y) = \sum_k w_k F_k(X,Y)$; (3) $P(Y\mid X) = e^{s(Y)}/\sum_{Y'} e^{s(Y')}$. Il rapporto fra due candidate non richiede $Z$: $P(Y)/P(Y') = e^{s(Y) - s(Y')}$. Esercizio 9.

<a id="p-77"></a>

### Slide 77 · Feature per le parole sconosciute

La **word shape** mappa le minuscole in `x`, le maiuscole in `X`, le cifre in `d`, e conserva la punteggiatura. La **short word shape** fonde le ripetizioni consecutive dello stesso tipo di carattere.

| Parola | Word shape | Short word shape |
| --- | --- | --- |
| I.M.F. | X.X.X. | X.X.X. |
| DC10-30 | XXdd-dd | Xd-d |
| well-dressed | xxxx-xxxxxxx | x-x |
| L'Occitane | X'Xxxxxxxx | X'Xx |

Tutte verificate con una funzione Python. Si usano anche **prefissi e suffissi** (di lunghezza fino a 2 per il PoS, fino a 4 per la NER): per *well-dressed* i prefissi *w, we* e i suffissi *ed, d*. Le feature che compaiono meno di **5 volte** nel training di solito si scartano (feature cutoff).

Perché aiutano: una parola mai vista come *Zelenskyj* ha comunque shape `Xxxxxxxxx` (short `Xx`), che il modello ha visto migliaia di volte associata a NNP o B-PER. È ciò che l'HMM non può fare ([scheda 69](L08-sequence-labelling-pos-tagging-e-ner.md#p-69)).

<a id="p-78"></a>

### Slide 78 · Le stesse feature su una frase

Un'altra feature importante per la NER: la presenza di $w_i$ in un **gazetteer**, una lista di nomi di luoghi (spesso con milioni di voci, es. GeoNames). Fig. 18.16, sulla frase di Jane Villanueva:

| Parola | POS | Short shape | Gazetteer | BIO |
| --- | --- | --- | --- | --- |
| Jane | NNP | Xx | 0 | B-PER |
| Villanueva | NNP | Xx | 1 | I-PER |
| of | IN | x | 0 | O |
| United / Airlines / Holding | NNP | Xx | 0 | B-ORG / I-ORG / I-ORG |
| discussed | VBD | x | 0 | O |
| the | DT | x | 0 | O |
| Chicago | NNP | Xx | 1 | B-LOC |
| route | NN | x | 0 | O |
| . | . | . | 0 | O |

Si assume che *Chicago* e *Villanueva* siano nel gazetteer (Villanueva è anche un toponimo). Le feature valgono 0 o 1 (la colonna POS diventa feature come $\mathbb 1\{\text{POS} = \text{NNP}\}$). Il caso di *Villanueva* mostra che il gazetteer è un **indizio**, non una regola: qui è parte di un nome di persona, e il peso della feature va bilanciato da altre (B-PER sul token precedente, transizione B-PER→I-PER). Il PoS stesso diventa un input per la NER: le due attività si combinano.

<a id="p-79"></a>

### Slide 79 · Training e inferenza nei CRF

- **Training: stimare i pesi $w$**. Gli stessi algoritmi supervisionati della regressione logistica: **discesa del gradiente stocastica** che massimizza la log-verosimiglianza condizionata del training ($\sum \log P(Y\mid X)$). La regolarizzazione **L1 o L2** conta molto, perché le feature generate dai template sono milioni ([scheda 56 della L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-56)). I gradienti richiedono le attese delle feature sotto il modello, calcolate con la versione CRF di forward-backward.
- **Inferenza: trovare la sequenza migliore**. Nell'argmax spariscono sia l'esponenziale (monotono) sia $Z(X)$ (costante per una data $X$):
  $$\hat Y = \operatorname*{argmax}_{Y}\sum_{i=1}^{n}\sum_{k=1}^{K} w_k\,f_k(y_{i-1}, y_i, X, i)$$
  resta una somma di feature locali pesate sulle posizioni; si riempie una matrice $N\times T$ con backpointer: **di nuovo Viterbi**.

Il CRF a catena lineare dipende a ogni passo da un solo tag precedente: è esattamente ciò che rende applicabile Viterbi.

<a id="p-80"></a>

### Slide 80 · Viterbi per l'HMM e per il CRF

Le due ricorsioni a confronto (Eq. 18.31 e 18.33), per $1\le j\le N$, $1 &lt; t\le T$:

$$\text{HMM:}\quad v_t(j) = \max_{i=1}^{N}\ v_{t-1}(i)\,a_{ij}\,b_j(o_t)$$
$$\text{CRF:}\quad v_t(j) = \max_{i=1}^{N}\Big[v_{t-1}(i) + \sum_{k=1}^{K} w_k\,f_k(y_{t-1} = i,\ y_t = j,\ X,\ t)\Big]$$

Le probabilità di prior (transizione) e verosimiglianza (emissione) sono sostituite da una **somma di feature pesate**; somma e non prodotto perché il CRF lavora in **log-spazio** (il punteggio è l'esponente). In piccolo a sinistra di ogni formula, l'obiettivo globale: $\prod_i P(w_i\mid t_i)P(t_i\mid t_{i-1})$ per l'HMM, $\sum_i\sum_k w_k f_k(y_{i-1}, y_i, X, i)$ per il CRF.

> **Approfondimento: Un HMM è un CRF particolare**
>
> Prendendo il log della ricorsione HMM: $\log v_t(j) = \max_i[\log v_{t-1}(i) + \log a_{ij} + \log b_j(o_t)]$. È la ricorsione CRF con due soli template, $\langle y_{i-1}, y_i\rangle$ con peso $\log a_{ij}$ e $\langle y_i, x_i\rangle$ con peso $\log b_j(x_i)$. Quindi ogni HMM corrisponde a un CRF lineare con pesi vincolati a essere log-probabilità; il CRF libera i pesi (stimati discriminativamente) e permette altre feature. È la stessa relazione che c'è fra Naive Bayes e regressione logistica (L6).

<a id="p-81"></a>

### Slide 81 · Valutazione della NER

- **PoS tagging: accuracy**. Ogni token ha esattamente un tag; la baseline most-frequent-tag è al 92% ([scheda 20](L08-sequence-labelling-pos-tagging-e-ner.md#p-20)).
- **NER: recall, precision, F1** (le misure della [scheda 25 della L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-25)): l'**unità di risposta è l'entità**, non la parola. Un'entità predetta è corretta solo se **confini e tipo** coincidono esattamente con quelli gold.

$$P = \frac{\#\text{entità corrette}}{\#\text{entità predette}}\qquad R = \frac{\#\text{entità corrette}}{\#\text{entità gold}}\qquad F_1 = \frac{2PR}{P+R}$$

- Etichettare *Jane* invece di *Jane Villanueva* costa **due errori**: un falso positivo (lo span [PER Jane], che non esiste nel gold) e un falso negativo ([PER Jane Villanueva], mancato).
- **Disallineamento train-test**: si valuta su entità, ma si addestra su parole (una loss per token).

Perché non l'accuracy sui token: quasi tutti i token sono O, quindi un sistema che non trova nulla ha accuracy altissima (lo stesso problema delle classi sbilanciate, [scheda 24 della L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-24)). Per confrontare due sistemi NER si usa il paired bootstrap ([scheda 44 della L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-44)).

> **Da saper fare: Valutazione a livello di span**
>
> (1) Converti gold e predizione da BIO a insiemi di span (tipo, inizio, fine); (2) TP = span presenti in entrambi, identici; (3) $P$ = TP / span predetti, $R$ = TP / span gold, $F_1$ media armonica. Un errore di confine o di tipo vale **un FP e un FN**. Esercizio 8: con 4 entità gold, 5 predette e 3 corrette, $P = 0{,}6$, $R = 0{,}75$, $F_1 = 0{,}667$, mentre l'accuracy sui token è 13/14 = 92,9%.

<a id="p-82"></a>

### Slide 82 · Ulteriori dettagli

- **Dati**: gli algoritmi sono supervisionati, quindi servono etichette. **Universal Dependencies**: corpora annotati PoS in oltre cento lingue; **Penn Treebank** per inglese, cinese, arabo; **OntoNotes** per le named entity (inglese, cinese, arabo); corpora di dominio per testi biomedici e letterari.
- **In pratica le regole sono ancora comuni**: la NER commerciale combina spesso liste e regole con un po' di apprendimento supervisionato (es. IBM System T). Approccio a passate successive: prima regole ad **alta precisione** (bassa recall) per le menzioni non ambigue, poi ricerca di sottostringhe dei nomi trovati, poi liste di dominio, infine un sequence labeller che usa come feature i risultati delle passate precedenti.
- **Lingue morfologicamente ricche**: tagset fatti di sequenze di tag morfologici (es. turco *iz+Noun+A3sg+Pnon+Gen*), da 4 a 10 volte più grandi.

Un corpus turco di 10 milioni di token ha **quattro volte** i tipi di un corpus inglese della stessa dimensione: più tipi significa più parole sconosciute e più bisogno di analisi morfologica.

<a id="p-83"></a>

### Slide 83 · Riassunto

**Un compito, due etichettature, un algoritmo di decodifica.**

- Le parole di **classe chiusa** sono frequenti, ambigue, funzionali; quelle di **classe aperta** sono nomi, verbi, aggettivi, avverbi.
- Il **PoS tagging** assegna un'etichetta a ogni parola; la **NER** etichetta span, che il **BIO** riduce a un'etichetta per parola.
- L'**HMM** è generativo: $A$ e $B$ stimate per massima verosimiglianza su un corpus annotato, decodifica con **Viterbi**.
- Il **CRF** è discriminativo: un modello log-lineare sull'intera sequenza, con feature che dipendono da $y_i$, $y_{i-1}$, $X$ e $i$.
- I tagger si valutano con l'**accuracy**; i riconoscitori di entità con **recall, precision, F1** sulle entità.

Il filo comune: "un compito" perché entrambi sono sequence labelling; "un algoritmo" perché Viterbi decodifica sia l'HMM sia il CRF lineare.

<a id="p-84"></a>

### Slide 84 · Riepilogo e prossima lezione

**Recap**:

- parti del discorso definite dal comportamento grammaticale; classi aperte e chiuse; tagset UD e Penn Treebank;
- PoS tagging e NER come sequence labelling; BIO trasforma gli span in un'etichetta per parola;
- HMM: transizioni $A$ ed emissioni $B$, contate su un corpus annotato (MLE);
- Viterbi: programmazione dinamica in $O(L\cdot N^2)$; la sequenza si sceglie solo alla fine, col backtrace;
- CRF: log-lineare sull'intera sequenza; i template generano le feature, i pesi si apprendono;
- valutazione: accuracy per il PoS; precision, recall, F1 sulle entità per la NER.

**Prossima lezione (laboratorio)**: NLTK e spaCy in pratica: tokenizzazione, frequenze e collocazioni, PoS tagging e lemmatizzazione, NER con spaCy e NLTK, sentiment con VADER e con un transformer. **Dopo**: lezione sui **word embedding**.

## Studio ed esercizi

### Guida allo studio (circa 4 h 45 min)

**Classi di parole, tagset, ambiguità** (40 min)

Schede 5-22. Saper dire perché le PoS si definiscono per distribuzione e morfologia e non per significato; classi aperte e chiuse con esempi; i 17 tag UPOS in tre gruppi (6+8+3) e le distinzioni principali del Penn Treebank (VB\*, NN\*, MD, DT, IN); leggere la tabella di ambiguità (tipi contro token, 14-15% contro 55-67%); baseline 92% contro 97%. Esercizio 2 (seconda parte). Libro §18.1-18.2.

**Catene di Markov e HMM** (50 min)

Schede 24-42. Definizioni formali ($Q$, $A$, $B$, $\pi$, righe che sommano a 1); probabilità di una sequenza in una catena (esercizio 1); le due assunzioni e cosa barrano le figure; stima MLE di $A$ e $B$ e la differenza fra $P(\textit{will}\mid\text{MD})$ e $P(\text{MD}\mid\textit{will})$; la derivazione in sei passi della [scheda 42](L08-sequence-labelling-pos-tagging-e-ner.md#p-42). Esercizio 2. Libro §18.4.1-18.4.4.

**Viterbi a mano** (75 min)

Schede 45-57. Ricorsione, inizializzazione, terminazione, backtrace; rifare da soli il reticolo *The fans watch the race* ([scheda 50](L08-sequence-labelling-pos-tagging-e-ner.md#p-50)) senza guardare; capire perché a *watch* la cella migliore non sta sul cammino ottimo; complessità $O(N^2T)$ contro $N^T$; parallelo con la distanza di edit della L3. Esercizi 3, 4, 5 (il 4 completa l'esempio Janet del libro e mostra i due errori della [scheda 57](L08-sequence-labelling-pos-tagging-e-ner.md#p-57)). Libro §18.4.5-18.4.6.

**NER e schemi BIO** (35 min)

Schede 59-69. Tipi di entità (PER, ORG, LOC, GPE e le estensioni), segmentazione e ambiguità di tipo (*Washington*); BIO, IO, BIOES con il numero di tag ($2n+1$, $n+1$, $4n+1$) e cosa perde IO; la correzione della [scheda 65](L08-sequence-labelling-pos-tagging-e-ner.md#p-65); perché un HMM non basta. Esercizio 6. Libro §18.3.

**CRF e valutazione** (55 min)

Schede 71-82. Formula del CRF con $Z(X)$; feature globali come somme di feature locali; catena lineare; template e feature generate; il conto della [scheda 76](L08-sequence-labelling-pos-tagging-e-ner.md#p-76); word shape e gazetteer; training (SGD, regolarizzazione) e inferenza (Viterbi in log-spazio). Valutazione a livello di entità con l'esempio di *Jane*. Esercizi 7, 8, 9, 10. Libro §18.5-18.7.

**Ripasso orale** (30 min)

Rispondere ad alta voce alle domande della sezione orale senza guardare la traccia, con particolare cura per: derivazione della decodifica HMM, Viterbi e complessità, HMM contro CRF (generativo/discriminativo, Naive Bayes/regressione logistica), BIO e valutazione a livello di span. Il laboratorio successivo (NLTK, spaCy) farà vedere gli stessi compiti con strumenti reali.

### Esercizi

#### Esercizio 1 (schede 25-29): probabilità in una catena di Markov

Con la catena del meteo della [scheda 25](L08-sequence-labelling-pos-tagging-e-ner.md#p-25) (HOT→HOT 0,6, HOT→COLD 0,1, HOT→WARM 0,3; COLD→COLD 0,8, COLD→HOT 0,1, COLD→WARM 0,1; WARM→WARM 0,6, WARM→HOT 0,3, WARM→COLD 0,1) e $\pi = [0{,}1;\ 0{,}7;\ 0{,}2]$ (HOT, COLD, WARM), calcola: (a) $P(\text{hot hot hot hot})$; (b) $P(\text{cold hot cold hot})$; (c) $P(\text{cold cold cold cold})$; (d) $P(\text{warm warm hot hot})$. (e) Che cosa dice il confronto fra (a) e (b)?

<details><summary>Soluzione</summary>

Formula: $P(q_{1:T}) = \pi_{q_1}\prod_{t=2}^{T} a_{q_{t-1}q_t}$.

- (a) $0{,}1\cdot0{,}6\cdot0{,}6\cdot0{,}6 = 0{,}0216$.
- (b) $0{,}7\cdot0{,}1\cdot0{,}1\cdot0{,}1 = 0{,}0007$.
- (c) $0{,}7\cdot0{,}8^3 = 0{,}3584$.
- (d) $0{,}2\cdot0{,}6\cdot0{,}3\cdot0{,}6 = 0{,}0216$ (coincide con (a) per caso).

(e) (a) è circa 31 volte più probabile di (b) anche se HOT ha probabilità iniziale molto più bassa di COLD: le permanenze (0,6-0,8) dominano sulle alternanze (0,1). Il modello codifica che il tempo è persistente. Verificato con numpy.

</details>

#### Esercizio 2 (schede 20, 35): stima MLE di A e B e baseline

Corpus annotato di quattro frasi:

`book/VB the/DT flight/NN`  
`the/DT book/NN sells/VB`  
`the/DT flight/NN leaves/VB`  
`the/DT book/NN leaves/VB`

(a) Aggiungendo <s> all'inizio e </s> alla fine di ogni frase, stima per MLE la matrice $A$ (righe <s>, DT, NN, VB; colonne DT, NN, VB, </s>) e la matrice $B$. Controlla che le righe sommino a 1. (b) Calcola $P(\textit{book}\mid\text{VB})$ e $P(\text{VB}\mid\textit{book})$: perché sono diverse? (c) Tagga *book the flight* con la baseline most-frequent-tag e con l'HMM (Viterbi, includendo la transizione finale verso </s>). Quale accuracy ottiene ciascuno?

<details><summary>Soluzione</summary>

(a) Conteggi dei tag: DT 4, NN 4, VB 4; ogni tag compare 4 volte anche come "precedente" (contando <s> 4 volte). Transizioni: <s>→DT 3, <s>→VB 1; DT→NN 4; NN→VB 3, NN→</s> 1; VB→DT 1, VB→</s> 3.

| A | DT | NN | VB | </s> |
| --- | --- | --- | --- | --- |
| <s> | 0,75 | 0 | 0,25 | 0 |
| DT | 0 | 1 | 0 | 0 |
| NN | 0 | 0 | 0,75 | 0,25 |
| VB | 0,25 | 0 | 0 | 0,75 |

$B$: DT: *the* 4/4 = 1. NN: *book* 2/4 = 0,5, *flight* 2/4 = 0,5. VB: *book* 1/4 = 0,25, *sells* 1/4 = 0,25, *leaves* 2/4 = 0,5. Tutte le righe sommano a 1.

(b) $P(\textit{book}\mid\text{VB}) = 1/4 = 0{,}25$ (fra i 4 verbi, uno è *book*); $P(\text{VB}\mid\textit{book}) = 1/3$ (fra le 3 occorrenze di *book*, una è verbo). Sono condizionate su eventi diversi: la prima è l'emissione dell'HMM, la seconda la posterior che userebbe la baseline.

(c) **Baseline**: *book* è NN 2 volte e VB 1, quindi NN; *the* → DT; *flight* → NN. Risultato NN DT NN: 2/3 corretti. **HMM**: $v_1(\text{VB}) = 0{,}25\cdot0{,}25 = 0{,}0625$, $v_1(\text{NN}) = 0$ perché $P(\text{NN}\mid\langle s\rangle) = 0$ (nessuna frase comincia con un nome), $v_1(\text{DT}) = 0$ (DT non emette *book*). $v_2(\text{DT}) = 0{,}0625\cdot0{,}25\cdot1 = 0{,}015625$ (da VB). $v_3(\text{NN}) = 0{,}015625\cdot1\cdot0{,}5 = 0{,}0078125$ (da DT); con </s>: $\times0{,}25 = 0{,}00195$. Risultato **VB DT NN**: 3/3. Il contesto (inizio frase, poi DT) corregge la scelta lessicale. Verificato con uno script.

</details>

#### Esercizio 3 (schede 46-50): Viterbi completo a mano

Con l'HMM della [scheda 48](L08-sequence-labelling-pos-tagging-e-ner.md#p-48) (tag DT, NN, VB; stesse tabelle $A$ e $B$), decodifica la frase *the watch fans race* ("i fan degli orologi corrono"). (a) Riempi il reticolo $v_t(j)$ con i backpointer. (b) Fai il backtrace. (c) Confronta con la scelta parola per parola basata solo su $B$. (d) Quale cella è la migliore della colonna *fans*? Sta sul cammino ottimo?

<details><summary>Soluzione</summary>

(a) Emissioni utili: *the*: DT 0,2; *watch*: NN 0,3, VB 0,15; *fans*: NN 0,1, VB 0,2; *race*: NN 0,1, VB 0,3.

- *the*: $v_1(\text{DT}) = 1\cdot0{,}2 = 0{,}2$.
- *watch*: NN $= 0{,}2\cdot0{,}9\cdot0{,}3 = 0{,}054$ (DT); VB $= 0{,}2\cdot0{,}1\cdot0{,}15 = 0{,}003$ (DT).
- *fans*: NN = max(da NN $0{,}054\cdot0{,}5\cdot0{,}1 = 0{,}0027$; da VB $0{,}003\cdot0{,}5\cdot0{,}1 = 0{,}00015$) = **0,0027** (NN); VB = max(da NN $0{,}054\cdot0{,}5\cdot0{,}2 = 0{,}0054$; da VB $0{,}003\cdot0\cdot0{,}2 = 0$) = **0,0054** (NN).
- *race*: NN = max(da NN $0{,}0027\cdot0{,}5\cdot0{,}1 = 0{,}000135$; da VB $0{,}0054\cdot0{,}5\cdot0{,}1 = 0{,}00027$) = **0,00027** (VB); VB = max(da NN $0{,}0027\cdot0{,}5\cdot0{,}3 = 0{,}000405$; da VB $0{,}0054\cdot0 = 0$) = **0,000405** (NN).

|  | the | watch | fans | race |
| --- | --- | --- | --- | --- |
| DT | 0,2 | 0 | 0 | 0 |
| NN | 0 | 0,054 (DT) | 0,0027 (NN) | 0,00027 (VB) |
| VB | 0 | 0,003 (DT) | 0,0054 (NN) | 0,000405 (NN) |

(b) Massimo finale: VB 0,000405. Backtrace: VB@race ← NN@fans ← NN@watch ← DT@the. Risultato **DT NN NN VB**, probabilità 0,000405.

(c) Solo $B$: DT, NN (0,3), VB (0,2), VB (0,3): DT NN VB VB, sbagliato su *fans* (e impossibile: VB→VB = 0).

(d) La cella migliore di *fans* è VB (0,0054), ma il cammino ottimo passa per NN@fans: VB non può essere seguito da VB, e *race* come VB è più probabile che come NN. Ancora una volta la decisione si prende solo alla fine. Verificato con numpy e per forza bruta.

</details>

#### Esercizio 4 (schede 54-57): completare il reticolo di Janet will back the bill

Il libro lascia "come esercizio per il lettore" il completamento della Fig. 18.14. Con le tabelle delle [schede 55-56](L08-sequence-labelling-pos-tagging-e-ner.md#p-55) (valori esatti, senza arrotondare): (a) calcola le colonne *Janet* e *will* e confrontale con la figura della [scheda 57](L08-sequence-labelling-pos-tagging-e-ner.md#p-57); (b) completa *back*, *the*, *bill* (bastano gli stati con emissione non nulla); (c) fai il backtrace. (d) Alla colonna *back* qual è la cella migliore? Perché non viene scelta?

<details><summary>Soluzione</summary>

(a) *Janet*: solo NNP, $v_1 = 0{,}2767\cdot0{,}000032 = 8{,}854\cdot10^{-6}$. *will* (unico predecessore NNP): MD $= 8{,}854\cdot10^{-6}\cdot0{,}0110\cdot0{,}308431 = 3{,}004\cdot10^{-8}$; NN $= \dots\cdot0{,}0584\cdot0{,}0002 = 1{,}034\cdot10^{-10}$; VB $= \dots\cdot0{,}0009\cdot0{,}000028 = 2{,}231\cdot10^{-13}$. La figura dà 2,772e-8 (arrotondando 0,0110 a 0,01), $10^{-10}$, e 2,5e-13: quest'ultimo è sbagliato (con gli arrotondamenti della figura si ottiene 2,27e-13).

(b) *back* (candidati $v_2(i)\,a_{ij}$, vince sempre MD):

- VB: da MD $3{,}004\cdot10^{-8}\cdot0{,}7968 = 2{,}394\cdot10^{-8}$ (da NN $1{,}4\cdot10^{-13}$) → $\times0{,}000672 = 1{,}609\cdot10^{-11}$;
- RB: da MD $\cdot0{,}1698 = 5{,}101\cdot10^{-9}$ → $\times0{,}010446 = 5{,}328\cdot10^{-11}$;
- NN: da MD $2{,}403\cdot10^{-11}$ (da NN $1{,}258\cdot10^{-11}$) → $\times0{,}000223 = 5{,}359\cdot10^{-15}$;
- JJ: da MD $1{,}502\cdot10^{-11}$ → $\times0{,}00034 = 5{,}107\cdot10^{-15}$.

*the*: DT: da VB $1{,}609\cdot10^{-11}\cdot0{,}2231 = 3{,}589\cdot10^{-12}$, da RB $5{,}328\cdot10^{-11}\cdot0{,}0479 = 2{,}552\cdot10^{-12}$ → VB, $\times0{,}506099 = 1{,}816\cdot10^{-12}$. NNP: da VB $5{,}18\cdot10^{-13}$ (da RB $3{,}62\cdot10^{-13}$) → $\times0{,}000048 = 2{,}486\cdot10^{-17}$.

*bill*: NN: da DT $1{,}816\cdot10^{-12}\cdot0{,}4744 = 8{,}616\cdot10^{-13}$ → $\times0{,}002337 = 2{,}014\cdot10^{-15}$. VB: da DT $\cdot0{,}0002\cdot0{,}000028 = 1{,}017\cdot10^{-20}$.

(c) Massimo finale NN ($2{,}01\cdot10^{-15}$). Backtrace: NN ← DT ← VB ← MD ← NNP: **NNP MD VB DT NN**, la sequenza gold.

(d) A *back* la cella migliore è **RB** ($5{,}3\cdot10^{-11}$, più di tre volte VB), perché $b_{\text{RB}}(\textit{back}) = 0{,}0104$ è molto più alta di $b_{\text{VB}}(\textit{back})$. Ma la parola successiva è *the*: $P(\text{DT}\mid\text{VB}) = 0{,}2231$ contro $P(\text{DT}\mid\text{RB}) = 0{,}0479$, e il cammino via VB vince ($3{,}59$ contro $2{,}55\cdot10^{-12}$). Un tagger greedy avrebbe scelto RB. Tutti i valori calcolati con numpy.

</details>

#### Esercizio 5 (schede 51-53, 66): complessità

(a) Con il tagset UPOS ($N = 17$) e una frase di $T = 10$ parole, quante sequenze di tag andrebbero valutate per forza bruta? Quante operazioni (prodotti) fa circa Viterbi? Quanta memoria serve per le matrici? (b) Verifica il "circa 40.000" della [scheda 53](L08-sequence-labelling-pos-tagging-e-ner.md#p-53) ($N = 45$, $T = 20$). (c) Per una NER con 4 tipi di entità e frasi di 30 parole, di quanto aumenta il costo di Viterbi passando da BIO a BIOES?

<details><summary>Soluzione</summary>

(a) Forza bruta: $17^{10} = 2.015.993.900.449\approx 2{,}0\cdot10^{12}$ sequenze (ciascuna con ~$2T$ moltiplicazioni). Viterbi: $T\cdot N^2 = 10\cdot289 = 2.890$ prodotti circa (esattamente $N + (T-1)N^2 = 17 + 9\cdot289 = 2.618$ celle-candidato). Memoria: due matrici $N\times T$, cioè $2\cdot170 = 340$ valori.

(b) $20\cdot45^2 = 40.500$: corretto. Forza bruta: $45^{20}\approx1{,}16\cdot10^{33}$.

(c) BIO: $2\cdot4+1 = 9$ tag, costo $30\cdot81 = 2.430$; BIOES: $4\cdot4+1 = 17$ tag, costo $30\cdot289 = 8.670$. Fattore $289/81\approx3{,}6$: il costo cresce col **quadrato** del numero di tag, non con la lunghezza.

</details>

#### Esercizio 6 (schede 64-67): BIO, IO, BIOES

Frase: *Mario Rossi of Banca Intesa flew from Pisa to New York on Monday .* con entità [PER Mario Rossi], [ORG Banca Intesa], [GPE Pisa], [GPE New York] (tipi usati: PER, ORG, LOC, GPE; le date non si annotano). (a) Scrivi le etichette IO, BIO e BIOES. (b) Quante etichette diverse ha ciascuno schema con questi 4 tipi? (c) Ricostruisci gli span dalla sequenza BIO `B-PER I-PER O B-LOC B-LOC O` su *Anna Bianchi visited Pisa Livorno yesterday*. Che cosa succederebbe in IO? (d) Che cosa c'è di sbagliato in `O I-ORG I-ORG O`?

<details><summary>Soluzione</summary>

(a)

| Token | IO | BIO | BIOES |
| --- | --- | --- | --- |
| Mario | I-PER | B-PER | B-PER |
| Rossi | I-PER | I-PER | E-PER |
| of | O | O | O |
| Banca | I-ORG | B-ORG | B-ORG |
| Intesa | I-ORG | I-ORG | E-ORG |
| flew, from | O | O | O |
| Pisa | I-GPE | B-GPE | S-GPE |
| to | O | O | O |
| New | I-GPE | B-GPE | B-GPE |
| York | I-GPE | I-GPE | E-GPE |
| on, Monday, . | O | O | O |

(b) IO $n+1 = 5$; BIO $2n+1 = 9$; BIOES $4n+1 = 17$.

(c) Span: [PER Anna Bianchi], [LOC Pisa], [LOC Livorno]: il secondo B-LOC apre un nuovo span anche senza un O in mezzo. In IO la sequenza diventerebbe I-PER I-PER O I-LOC I-LOC O e si leggerebbe un solo span [LOC Pisa Livorno]: è l'informazione che IO perde.

(d) Un I-ORG dopo O è malformato (uno span non può cominciare con I). Convenzione comune di riparazione: trattare il primo I-ORG come B-ORG, quindi span [ORG token2 token3]. Un CRF con feature di transizione impara pesi molto negativi per O→I-X e non produce quasi mai questi casi. Conversioni verificate con uno script.

</details>

#### Esercizio 7 (schede 77-78): word shape e feature per parole sconosciute

(a) Calcola word shape e short word shape di *COVID-19*, *iPhone15*, *3.14*, *U.S.A.*, *Pisa*. (b) Elenca le feature prefisso/suffisso (lunghezza ≤ 2) di *Pisa*. (c) Perché queste feature aiutano su una parola mai vista, mentre l'HMM non può usarle?

<details><summary>Soluzione</summary>

(a) Regola: maiuscola → X, minuscola → x, cifra → d, punteggiatura invariata; short shape: si fondono le ripetizioni consecutive.

| Parola | Shape | Short shape |
| --- | --- | --- |
| COVID-19 | XXXXX-dd | X-d |
| iPhone15 | xXxxxxdd | xXxd |
| 3.14 | d.dd | d.d |
| U.S.A. | X.X.X. | X.X.X. |
| Pisa | Xxxx | Xx |

(b) prefix = P, prefix = Pi, suffix = a, suffix = sa (più shape = Xxxx e short shape = Xx).

(c) Una parola nuova non ha conteggi propri, ma la sua shape e i suoi affissi sono condivisi con migliaia di parole viste nel training (Xx con NNP/B-PER, -ed con VBD/VBN, d.d con CD/NUM): il CRF ha pesi per queste feature. L'HMM vede la parola solo tramite $P(w\mid t)$, che per una parola nuova è zero (o una costante di smoothing uguale per tutte). Shape calcolate con una funzione Python.

</details>

#### Esercizio 8 (scheda 81): valutazione NER a livello di span

Frase (14 token): *Jane Villanueva of United Airlines Holding discussed the Chicago route with Tim Wagner .*

Gold: [PER Jane Villanueva], [ORG United Airlines Holding], [LOC Chicago], [PER Tim Wagner].

Sistema (in BIO): Jane/B-PER Villanueva/B-LOC of/O United/B-ORG Airlines/I-ORG Holding/I-ORG discussed/O the/O Chicago/B-LOC route/O with/O Tim/B-PER Wagner/I-PER ./O

(a) Elenca gli span predetti. (b) Calcola precision, recall e F1 a livello di entità. (c) Calcola l'accuracy dei tag BIO a livello di token. (d) Commenta la differenza. Perché il sistema potrebbe aver taggato *Villanueva* come LOC?

<details><summary>Soluzione</summary>

(a) Predetti: [PER Jane], [LOC Villanueva], [ORG United Airlines Holding], [LOC Chicago], [PER Tim Wagner]: 5 span.

(b) Corretti (stessi confini e stesso tipo): ORG United Airlines Holding, LOC Chicago, PER Tim Wagner: TP = 3. $P = 3/5 = 0{,}60$; $R = 3/4 = 0{,}75$; $F_1 = 2\cdot0{,}6\cdot0{,}75/(0{,}6+0{,}75) = 0{,}9/1{,}35 = 0{,}667$. L'errore su *Jane Villanueva* produce **due falsi positivi** ([PER Jane], [LOC Villanueva]) e **un falso negativo** ([PER Jane Villanueva]).

(c) Solo *Villanueva* ha il tag sbagliato (gold I-PER, predetto B-LOC): 13/14 = 92,9%.

(d) L'accuracy per token è gonfiata dai tanti O facili e "conta" un errore di confine come un solo token sbagliato; la valutazione per entità riflette che una persona è stata spezzata in due entità sbagliate. Probabile causa: *Villanueva* è nel **gazetteer** come luogo ([scheda 78](L08-sequence-labelling-pos-tagging-e-ner.md#p-78)), e il peso di quella feature ha battuto la transizione B-PER→I-PER. Verificato con uno script (span da BIO, intersezione di insiemi).

</details>

#### Esercizio 9 (schede 72-80): un CRF giocattolo

Frase $X$ = *time flies*, tag possibili NN e VB. Il CRF lineare ha sei feature locali (valgono 1 se la condizione è vera) con pesi:

- $f_1$: $y_i$ = NN e $x_i$ = *time*, $w_1 = 1{,}0$
- $f_2$: $y_i$ = VB e $x_i$ = *flies*, $w_2 = 1{,}5$
- $f_3$: $y_i$ = NN e $x_i$ = *flies*, $w_3 = 0{,}5$
- $f_4$: $y_i$ = VB e $y_{i-1}$ = NN, $w_4 = 0{,}8$
- $f_5$: $y_i$ = NN e $y_{i-1}$ = NN, $w_5 = 0{,}2$
- $f_6$: $y_i$ = VB e $i = 1$, $w_6 = -1{,}0$

(a) Per ciascuna delle 4 sequenze di tag elenca le feature che scattano e calcola il punteggio $s(Y) = \sum_k w_k F_k(X,Y)$. (b) Calcola $Z(X)$ e $P(Y\mid X)$ per tutte e quattro. (c) Ritrova la sequenza migliore con Viterbi in log-spazio. (d) Quanto vale $P(y_2 = \text{VB}\mid X)$? (e) Quale template corrisponde a $f_6$, ed è lecito in un CRF lineare?

<details><summary>Soluzione</summary>

(a)

| $Y$ | feature | $s(Y)$ | $e^{s}$ | $P(Y\mid X)$ |
| --- | --- | --- | --- | --- |
| NN NN | $f_1, f_3, f_5$ | 1,7 | 5,474 | 0,157 |
| NN VB | $f_1, f_2, f_4$ | 3,3 | 27,113 | 0,778 |
| VB NN | $f_6, f_3$ | −0,5 | 0,607 | 0,017 |
| VB VB | $f_6, f_2$ | 0,5 | 1,649 | 0,047 |

(b) $Z(X) = 5{,}474 + 27{,}113 + 0{,}607 + 1{,}649 = 34{,}842$; le probabilità sono in tabella (sommano a 1). È una softmax sulle 4 sequenze: la regressione logistica multinomiale con le sequenze come classi.

(c) $v_1(\text{NN}) = w_1 = 1{,}0$; $v_1(\text{VB}) = w_6 = -1{,}0$. $v_2(\text{NN}) = \max(1{,}0 + 0{,}5 + 0{,}2;\ -1{,}0 + 0{,}5) = 1{,}7$ (da NN); $v_2(\text{VB}) = \max(1{,}0 + 1{,}5 + 0{,}8;\ -1{,}0 + 1{,}5) = 3{,}3$ (da NN). Massimo 3,3 → **NN VB**, come l'argmax esaustivo; $Z$ ed exp non servono.

(d) $P(\text{NN VB}) + P(\text{VB VB}) = 0{,}778 + 0{,}047 = 0{,}825$.

(e) $f_6$ usa $y_i$ e la posizione $i$: template $\langle y_i, i\rangle$, lecito perché una feature locale può dipendere da $(y_{i-1}, y_i, X, i)$. Verificato enumerando le sequenze in Python.

</details>

#### Esercizio 10 (schede 75-76): feature generate dai template

Frase annotata *the/DT fans/NN watch/VB the/DT race/NN*. Template: $\langle y_i, x_i\rangle$, $\langle y_i, y_{i-1}\rangle$ (con $y_0$ = <s>). (a) Elenca le feature locali che scattano in ogni posizione. (b) Calcola i valori delle feature globali $F_k$ diverse da zero. (c) Quanti pesi servono per questa frase? E se la frase fosse lunga il doppio con le stesse coppie?

<details><summary>Soluzione</summary>

(a) Posizione 1: ($y$=DT, $x$=the), ($y$=DT, $y_{-1}$=<s>). Posizione 2: (NN, fans), (NN dopo DT). Posizione 3: (VB, watch), (VB dopo NN). Posizione 4: (DT, the), (DT dopo VB). Posizione 5: (NN, race), (NN dopo DT).

(b) Sommando sulle posizioni: $F$(DT, the) = 2; $F$(NN dopo DT) = 2; $F$(DT dopo <s>) = 1; $F$(NN, fans) = 1; $F$(VB, watch) = 1; $F$(VB dopo NN) = 1; $F$(DT dopo VB) = 1; $F$(NN, race) = 1. Otto feature globali non nulle, 10 attivazioni locali.

(c) Otto pesi (uno per feature globale), non dieci: le feature ripetute condividono il peso. Raddoppiando la frase con le stesse coppie i valori $F_k$ raddoppiano ma i pesi restano otto: è il motivo per cui un insieme fisso di $K$ pesi funziona per frasi di qualsiasi lunghezza ([scheda 73](L08-sequence-labelling-pos-tagging-e-ner.md#p-73)). Notare che con soli questi due template il CRF ha le stesse "feature" di un HMM (emissioni e transizioni), ma con pesi liberi.

</details>

### Domande tipo orale

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
