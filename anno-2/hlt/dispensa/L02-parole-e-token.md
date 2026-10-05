# L2 · Parole e token

*Words and Tokens* · 24/09/2026 · Claudio Gallicchio · lettura: J&M cap. 2, §2.1-2.5

[Versione interattiva sul sito](https://gabriele-marsili.github.io/appunti-magistrale-ai/anno-2/hlt/sito/#L2) · [Indice della dispensa](README.md)

Come si rappresenta il testo per un modello linguistico. Le parole sono un'unità ambigua (convenzioni, lingue senza spazi) e infinita (**legge di Heaps**, parole sconosciute); i **morfemi** sono difficili da segmentare tra lingue; i **caratteri** Unicode, codificati in byte **UTF-8**, sono ben definiti ma troppo piccoli. La soluzione pratica è la **tokenizzazione subword** con **BPE**: si imparano i merge da un corpus e li si applica in ordine al testo nuovo; i tokenizer reali lavorano sui byte, con pretokenizzazione, e penalizzano le lingue diverse dall'inglese. Chiude il tema dei **corpora** e dei datasheet. È la base di tutto ciò che un LLM legge e predice.

## Indice

- [Apertura](#apertura)
- [Parole](#parole)
- [Morfemi](#morfemi)
- [Unicode](#unicode)
- [Tokenizzazione subword: BPE](#tokenizzazione-subword-bpe)
- [Corpora](#corpora)
- [Notebook](#notebook)
- [Studio ed esercizi](#studio-ed-esercizi)

## Apertura

<a id="p-1"></a>
**Slide 1 · Parole e token** — Lezione 2 (Gallicchio, 24 settembre 2026): come si trasforma il testo nelle unità che un modello linguistico legge, dalle parole ai token subword.

<a id="p-2"></a>

### Slide 2 · Indice della lezione

Cinque parti, che seguono un filo logico preciso: si cercano le **unità** con cui rappresentare il testo e si scartano una dopo l'altra quelle naturali.

- **Parole**: che cosa conta come parola, tipi e istanze, legge di Heaps. Problema: le parole sono troppe e in molte lingue non sono nemmeno segnate dagli spazi.
- **Morfemi**: le parti delle parole; unità sensate ma difficili da definire in modo uniforme tra le lingue.
- **Unicode**: caratteri, code point e byte UTF-8; unità ben definite ma troppo piccole.
- **Tokenizzazione subword**: la soluzione pratica, BPE, che impara i token dai dati.
- **Corpora**: da dove vengono i testi su cui tutto questo si addestra, e come documentarli.

<a id="p-3"></a>

### Slide 3 · Riferimento: J&M capitolo 2

Lettura principale: Jurafsky e Martin, *Speech and Language Processing*, 3a ed. (draft del 19 agosto 2026), **capitolo 2, sezioni 2.1-2.5**: parole (2.1), morfemi (2.2), Unicode (2.3), tokenizzazione subword con BPE (2.4), corpora (2.5). Le sezioni 2.6-2.9 (espressioni regolari, regole di tokenizzazione, edit distance) sono della lezione successiva.

Il QR code porta al sito del libro, [web.stanford.edu/~jurafsky/slp3/](https://web.stanford.edu/~jurafsky/slp3/), da cui si scaricano i capitoli in PDF. Gli esempi delle slide (la frase del picnic, il corpus *set new new renew reset renew*, le frasi in inglese e spagnolo) sono tutti presi dal capitolo: leggerlo dopo la lezione è il modo più rapido per fissarli.

## Parole

<a id="p-4"></a>
**Slide 4 · Parole** — Si parte dall'unità più intuitiva, la parola, e si scopre perché non basta: contarle è ambiguo e sono troppe.

<a id="p-5"></a>

### Slide 5 · Da dove viene la tokenizzazione: ELIZA

La slide riporta il celebre dialogo di **ELIZA** (Weizenbaum, 1966), il programma che imitava uno psicoterapeuta rogersiano. ELIZA non capisce nulla: riconosce **pattern sulle parole** e li riscrive.

- *I need some help* attiva il pattern «I need X» e produce «WHAT WOULD IT MEAN TO YOU IF YOU GOT X», con X = *some help*.
- *My mother takes care of me* diventa «WHO ELSE IN YOUR FAMILY TAKES CARE OF YOU»: oltre al pattern c'è la sostituzione dei pronomi (*me* diventa *you*).

Per fare questo bisogna prima spezzare l'input in parole: è già una forma di **tokenizzazione**. I chatbot moderni funzionano in modo del tutto diverso (modelli neurali che predicono il token successivo, vedi L1), ma il primo passo di ogni sistema NLP resta lo stesso: segmentare il testo in unità. Il libro apre il capitolo 2 proprio con questo dialogo.

<a id="p-6"></a>

### Slide 6 · Quante parole? La domanda

La frase di esempio del libro: *They picnicked by the pool, then lay back on the grass and looked at the stars.* La domanda sembra banale, ma la risposta dipende da due convenzioni che la slide successiva rende esplicite: la punteggiatura conta come parola? *The* e *the* sono la stessa parola? Prima di guardare la risposta conviene contare a mano.

<a id="p-7"></a>

### Slide 7 · Quante parole? Tre risposte

La stessa frase dà numeri diversi a seconda della convenzione:

- **16 parole** se si spezza sugli spazi e si ignora la punteggiatura.
- **18 parole** se la virgola e il punto contano come parole a sé. I modelli linguistici di solito trattano la punteggiatura come unità separate.
- **14 tipi** (*word types*): *the* compare tre volte, tutte le altre forme una volta sola, quindi 16 - 2 = 14 forme distinte.

Verifica (notebook, cella 2): senza punteggiatura N = 16, |V| = 14; con punteggiatura N = 18, |V| = 16, perché si aggiungono i due tipi `,` e `.`.

> **Da saper fare: Contare istanze e tipi a mano**
>
> 1. Fissa le convenzioni: punteggiatura sì o no, maiuscole distinte o no.
> 2. Conta le occorrenze: è N.
> 3. Conta le forme distinte (le ripetute valgono una volta): è |V|.
> 4. Controllo: |V| ≤ N sempre; N - |V| è il numero di ripetizioni.
>
> All'esame capita la frase dell'esercizio 1 della scheda: vedi la sezione Studio.

<a id="p-8"></a>

### Slide 8 · Tipi e istanze di parola

Tre termini da tenere distinti:

- **Word type**: una forma distinta. L'insieme dei tipi è il **vocabolario** $V$, la sua dimensione $|V|$. Nella frase: 14.
- **Word instance**: un'occorrenza nel testo corrente. $N$ è il numero di istanze: 16.
- **Token**: d'ora in poi, l'output di un tokenizer. Testi più vecchi chiamano *word tokens* le istanze; il libro riserva «token» alle unità della tokenizzazione subword (BPE, più avanti).

*They* e *they*: stesso tipo o due? Dipende dal compito. Per il recupero di informazioni conviene unirli; per il riconoscimento di entità (L1) la maiuscola è un indizio prezioso. Per questo alcuni sistemi mantengono due versioni del modello, *cased* e *uncased* (per esempio BERT ne ha entrambe).

Collegamento: nella L1 le convenzioni di tokenizzazione (*New York-based*, *l'acqua*) erano già un problema; vedi [scheda 40 della L1](L01-introduzione-al-corso.md#p-40).

<a id="p-9"></a>

### Slide 9 · Che cosa è una parola dipende dal compito

- **Punteggiatura**: segna confini (virgole, punti, due punti) e significato (il punto interrogativo cambia il tipo di frase, le virgolette segnalano una citazione). Si tiene o si scarta a seconda del compito.
- **Parlato**: *I do uh main- mainly business data processing* contiene un **frammento** (*main-*, parola interrotta) e una **pausa piena** (*uh*). In una trascrizione pulita si tolgono; nel riconoscimento del parlato si tengono, perché *uh* e *um* aiutano a predire cosa viene dopo (segnalano esitazione, spesso prima di una parola rara o di una riformulazione).
- **Contrazioni**: *I'm* è una parola ortografica ma due parole grammaticali, il pronome *I* e il verbo *'m* (am). In italiano lo stesso vale per *dell'*, *c'è*, *dammelo*.
- **Maiuscole**: *They* e *they*, uno o due tipi.

Il messaggio: non esiste una definizione di «parola» valida per tutti i compiti, e questa è la prima ragione per cercare un'unità diversa.

<a id="p-10"></a>

### Slide 10 · Lingue senza parole ortografiche

La frase cinese 姚明进入总决赛 (*yáo míng jìn rù zǒng jué sài*, «Yao Ming raggiunge la finale») è mostrata con tre segmentazioni, ognuna con la sua glossa inglese:

- **3 parole** (standard Chinese Treebank): 姚明 / 进入 / 总决赛, «YaoMing reaches finals»: il nome proprio è una parola sola.
- **5 parole** (standard Peking University): 姚 / 明 / 进入 / 总 / 决赛, «Yao Ming reaches overall finals»: cognome e nome separati, e l'aggettivo 总 «complessivo» staccato.
- **7 caratteri**: 姚 明 进 入 总 决 赛, glossati «Yao Ming enter enter overall decision game»: nessuna parola, solo caratteri.

Cinese, giapponese e thai non separano le parole con spazi. In cinese una parola è lunga in media 1,5-1,9 caratteri e ogni carattere (*hanzi*) è più o meno un morfema e una sillaba; quale segmentazione sia «giusta» è una convenzione. Per il cinese i caratteri sono un'unità ragionevole, per giapponese e thai sono troppo piccoli.

Seconda ragione per non usare le parole: in molte lingue non esistono come unità ortografiche.

<a id="p-11"></a>

### Slide 11 · Quante parole ci sono in una lingua?

La tabella (Figura 2.1 del libro) riporta tipi e istanze di alcuni corpora inglesi:

| Corpus | Tipi |V| | Istanze N | |V|/N |
| --- | --- | --- | --- |
| Shakespeare | 29 mila | 884 mila | 3,3% |
| Brown corpus | 38 mila | 1 milione | 3,8% |
| Switchboard (telefonate) | 20 mila | 2,4 milioni | 0,83% |
| COCA | 2 milioni | 440 milioni | 0,45% |
| Google n-grams | 13 milioni | 1000 miliardi | 0,0013% |

(L'ultima colonna è calcolata qui.) Più grande è il corpus, più tipi si trovano: non esiste un numero fisso di parole in una lingua. Il rapporto tipi/istanze scende, ma |V| continua a salire. Switchboard, pur più grande del Brown, ha meno tipi: il parlato spontaneo usa un vocabolario più ristretto dello scritto. Il dato di Google conta solo i tipi con almeno 40 occorrenze, quindi il numero vero è molto più alto.

<a id="p-12"></a>

### Slide 12 · Crescita del vocabolario: legge di Heaps

**Legge di Herdan-Heaps**: $|V| = kN^{\beta}$, con $k, \beta &gt; 0$ e $0 &lt; \beta &lt; 1$. Valori riportati tra 0,44 e 0,56 (il libro aggiunge «o anche più alti», a seconda di genere e dimensione del corpus): il vocabolario cresce un po' più in fretta della radice quadrata della lunghezza del testo.

**Il grafico** (Tria et al. 2018, corpus di libri di Project Gutenberg) è in scala log-log: in ascissa il numero totale di parole lette $w$ (da $10^0$ a $10^9$), in ordinata la dimensione del dizionario $D$ (da $10^0$ a $10^6$). La curva blu spessa parte da (1, 1) e arriva a circa $5\cdot 10^5$ tipi dopo circa $3\cdot10^8$ parole. Due rette di riferimento: una **verde con pendenza 1** ($\beta = 1$), parallela alla curva nel tratto iniziale fino a circa $10^3$ parole; una **arancione con pendenza 0,44**, parallela alla curva da circa $10^5$ in poi. Tra le due la curva si piega.

In log-log una legge di potenza è una retta: $\log|V| = \log k + \beta\log N$, con pendenza $\beta$. I **due regimi**: all'inizio compaiono parole funzionali e comuni e quasi ogni parola è nuova (crescita lineare); poi le **parole funzionali** (a, of) sono esaurite, sono un insieme chiuso, e arrivano solo **parole di contenuto**, nomi propri e termini tecnici, che non finiscono mai.

Conseguenza: qualunque vocabolario fissato incontrerà di continuo **parole sconosciute**.

> **Da saper fare: Usare la legge di Heaps**
>
> Se $N$ diventa $mN$, il vocabolario diventa $k(mN)^{\beta} = m^{\beta}\,|V|$: il fattore non dipende da $k$. Con $\beta = 0{,}5$ e $m = 4$: $4^{0{,}5} = 2$, il vocabolario raddoppia. Con $\beta = 0{,}44$ e $m = 10$: $10^{0{,}44} \approx 2{,}75$. Per stimare $\beta$ da due punti: $\beta = \dfrac{\log(|V_2|/|V_1|)}{\log(N_2/N_1)}$.

> **Approfondimento: Heaps e Zipf**
>
> (Facoltativo, oltre le slide.) La legge di Heaps è legata alla **legge di Zipf**: se la frequenza della parola di rango $r$ decresce come $r^{-\alpha}$ con $\alpha &gt; 1$, il vocabolario cresce circa come $N^{1/\alpha}$. Un $\beta$ vicino a 0,5 corrisponde a una coda di Zipf ripida. Zipf verrà ripreso quando si parlerà di modelli n-gram e di parole rare.

<a id="p-13"></a>

### Slide 13 · Il problema delle parole sconosciute

Nessun vocabolario cattura tutte le parole possibili. Esempio del libro: il corpus di addestramento contiene *low*, *new*, *newer*; nel corpus di test compare *lower*. Un sistema basato su parole non sa che cosa farne: è una parola **fuori vocabolario** (OOV, *out of vocabulary*), e di solito finisce in un simbolo generico <UNK> che butta via tutta l'informazione.

Due problemi, quindi, per le parole come unità: molte lingue non hanno parole ortografiche (scheda 10) e il numero di parole cresce senza limite (scheda 12).

Soluzione: i modelli linguistici **non usano parole** ma unità più piccole, i **subword**, che si ricombinano per rappresentare parole mai viste: *lower* = `low``er`. Notare che *-er* è stato visto in *newer*. Per capire quali unità più piccole usare, la lezione guarda prima a due candidati: morfemi e caratteri.

## Morfemi

<a id="p-14"></a>
**Slide 14 · Morfemi** — Seconda candidata come unità: le parti delle parole dotate di significato.

<a id="p-15"></a>

### Slide 15 · Morfemi

Un **morfema** è la più piccola unità dotata di significato di una lingua; la **morfologia** li studia.

Esempio segmentato: *Doc work-ed care-ful-ly wash-ing the glass-es*.

- **Radice** (*root*): il morfema centrale, che porta il significato principale: *work, care, wash, glass*.
- **Affisso** (*affix*): aggiunge un significato ulteriore: *-ed* (passato), *-ful*, *-ly*, *-ing*, *-es* (plurale).
- **Uno o molti**: *fox* è un morfema; *cats* due, *cat* + *-s* plurale. In cinese ogni carattere è per lo più un morfema.

Conto: la frase ha 6 parole e 11 morfemi (1 + 2 + 3 + 2 + 1 + 2), cioè circa 1,8 morfemi per parola, vicino alla stima di 1,7 per l'inglese della scheda 17. In italiano: *gatt-i*, *ri-scriv-eva*, *gentil-mente*.

<a id="p-16"></a>

### Slide 16 · Flessione, derivazione, clitici

- **Morfemi flessivi** (*inflectional*): grammaticali, con ruolo sintattico (accordo, tempo). Produttivi, spesso obbligatori, significato prevedibile. Esempi: *-s* del plurale, *-ed* del passato; in italiano *gatt-o/gatt-i*, *parl-o/parl-ava*. Non cambiano la categoria della parola.
- **Morfemi derivazionali**: più idiosincratici per applicazione e significato; di solito si applicano solo a una sottoclasse di parole e **cambiano la categoria grammaticale**: *care* (nome) + *-ful* = *careful* (aggettivo) + *-ly* = *carefully* (avverbio). In italiano *gentile* → *gentilmente*, *leggere* → *leggibile*.
- **Clitici**: si comportano sintatticamente come parole ma sono ridotti e attaccati a un'altra parola: *'ve* in *I've* vale *have* ma non può stare da solo; *'s* in *the teacher's book*; *l'* in *l'opéra*. In italiano: *l'acqua*, *dammelo* (da-mme-lo), *c'è*.

Flessione e derivazione sono due **poli di un continuum**, non classi nette. Per la tokenizzazione i clitici sono importanti: i pretokenizzatori dei modelli reali li staccano con regole apposite (scheda 41), e il tokenizer di GPT-4o separa *'s* in *Jane's* (scheda 42).

<a id="p-17"></a>

### Slide 17 · Tipologia morfologica

**La figura** (Greenberg 1960, Figura 2.3 del libro) è un asse orizzontale «Morphemes per Word» con una freccia verso sinistra etichettata **Analytic**, il centro **Synthetic** e la destra **Polysynthetic**. Le lingue sono punti sull'asse: Vietnamese 1,1; Farsi 1,5; English 1,7; Old English 2,1; Yakut 2,2; Swahili 2,5; Sanskrit 2,6; Greenlandic (Inuit) 3,7.

Due dimensioni della **tipologia morfologica**:

1. **Morfemi per parola**. Le lingue **isolanti** o analitiche (vietnamita, cantonese) hanno circa un morfema per parola; le **polisintetiche** (il koryak, parlato in Kamchatka) mettono in una parola un'intera frase inglese: *t-ə-nk'e-mejŋ-ə-jetemə-nni-k* «ho cucito molte coperture di yurta nel mezzo della notte».
2. **Segmentabilità**. Nelle lingue **agglutinanti** (turco) i morfemi hanno confini netti, uno per significato; nelle **fusive** un affisso fonde più significati: l'inglese *-s* di *she reads* vuol dire insieme terza persona, singolare e presente. L'italiano è fusivo: *-o* di *parlo* è prima persona, singolare, presente indicativo.

Il libro precisa che sono tendenze più che proprietà rigide delle lingue. Conseguenza: i morfemi sono difficili da definire e da segmentare in modo uniforme, quindi non sono un buon standard di tokenizzazione tra lingue.

## Unicode

<a id="p-18"></a>
**Slide 18 · Unicode** — Terza candidata come unità: il carattere, e come i caratteri diventano numeri e byte.

<a id="p-19"></a>

### Slide 19 · Da ASCII a Unicode: ASCII

Storicamente le lettere latine dell'inglese si codificavano con **ASCII** (anni '60): un byte per carattere, ma solo 128 codici (il bit più alto è sempre 0), di cui 95 stampabili; gli altri sono codici di controllo pensati per le telescriventi.

La tabella mostra alcuni codici in esadecimale e decimale: `<` 3C = 60, `=` 3D = 61, `>` 3E = 62, `?` 3F = 63; `@` 40 = 64, `A` 41 = 65, `B` 42 = 66, `C` 43 = 67; `\` 5C = 92, `]` 5D = 93, `^` 5E = 94, `_` 5F = 95; `` ` `` 60 = 96, `a` 61 = 97, `b` 62 = 98, `c` 63 = 99.

Curiosità utile: minuscola = maiuscola + 0x20 (A = 0x41, a = 0x61). Per l'inglese ASCII basta.

<a id="p-20"></a>

### Slide 20 · Da ASCII a Unicode: perché non basta

La slide aggiunge due esempi: lo spagnolo *Señor —respondió Sancho—* (due caratteri non ASCII, ñ e ó, più le lineette) e un passo in devanagari (articolo 1 della Dichiarazione universale dei diritti umani in hindi).

- ASCII non basta nemmeno per lingue in alfabeto latino come lo spagnolo o l'italiano (è, à).
- Il **devanagari** si usa per circa 120 lingue (hindi, marathi, nepali, sanscrito...).
- I caratteri cinesi in Unicode sono circa 100.000 (varianti CJKV comprese).

**Unicode 16.0** copre più di 150.000 caratteri e 168 sistemi di scrittura (*scripts*), dal cuneiforme alle emoji: lingue vive, lingue antiche, simboli matematici, valute.

<a id="p-21"></a>

### Slide 21 · Code point

Unicode assegna a ogni carattere un numero unico, il **code point**, scritto in esadecimale col prefisso `U+`, da U+0000 a U+10FFFF (= 1.114.111 in decimale, quindi 1.114.112 valori possibili).

- U+0061 *a* LATIN SMALL LETTER A (= 97)
- U+00F1 *ñ* LATIN SMALL LETTER N WITH TILDE (= 241)
- U+8FDB 进 (ideogramma CJK, = 36.827)
- U+1F600 emoji GRINNING FACE (= 128.512)

Più di un milione di code point: c'è spazio per caratteri nuovi. I primi 128 coincidono con ASCII (compatibilità all'indietro).

**Code point ≠ glifo**: il glifo è la forma visiva, che dipende dal font. La *a* in Times, in Courier, in grassetto o in corsivo sono glifi diversi dello stesso code point U+0061. Il testo che un modello legge è fatto di code point (anzi, di byte, come si vedrà), non di glifi.

<a id="p-22"></a>

### Slide 22 · Dai code point ai byte

La parola *hello* è la sequenza di 5 code point U+0068 U+0065 U+006C U+006C U+006F. Per salvarla in un file serve una **codifica** (*encoding*).

- **UTF-32** (UTF = Unicode Transformation Format): i code point arrivano a 1.114.111, servono 21 bit ($2^{20} &lt; 1.114.112 \le 2^{21}$), e si arrotonda a 4 byte per carattere: `00 00 00 68 00 00 00 65 ...`. File 4 volte più lunghi che in ASCII e pieni di byte zero, che i vecchi programmi in stile C leggono come fine stringa: niente compatibilità.
- **UTF-8**: i 128 code point ASCII occupano un byte ciascuno, `68 65 6C 6C 6F`. Ogni file ASCII è già un file UTF-8 valido.

UTF-8 è a **lunghezza variabile**: i code point da 128 in su usano 2, 3 o 4 byte, tutti con valore tra 128 e 255 (bit alto a 1), quindi non si confondono mai con ASCII. Quasi tutto il web è in UTF-8.

<a id="p-23"></a>

### Slide 23 · UTF-8: la tabella

La tabella (dalla specifica Unicode 16.0, Figura 2.5 del libro) dice, per ogni intervallo di code point, come i bit del code point riempiono i byte:

| Code point | Bit utili | Byte UTF-8 |
| --- | --- | --- |
| U+0000-U+007F | 7 | `0xxxxxxx` |
| U+0080-U+07FF | 11 | `110yyyyy 10xxxxxx` |
| U+0800-U+FFFF | 16 | `1110zzzz 10yyyyyy 10xxxxxx` |
| U+10000-U+10FFFF | 21 | `11110uuu 10uuzzzz 10yyyyyy 10xxxxxx` |

- I **bit iniziali del primo byte** dicono quanti byte occupa il carattere: `0` uno, `110` due, `1110` tre, `11110` quattro.
- I **byte di continuazione** iniziano sempre con `10`.

In pratica: ASCII in 1 byte; la maggior parte delle scritture europee, mediorientali e africane in 2; la maggior parte di cinese, giapponese e coreano in 3; CJKV rari, emoji e alcuni simboli in 4. Poiché un byte di continuazione non può essere scambiato per un inizio, UTF-8 è **autosincronizzante**: da un punto qualsiasi basta spostarsi al massimo di 3 byte per ritrovare l'inizio di un carattere.

> **Da saper fare: Contare i caratteri da una sequenza di byte**
>
> Guarda solo i byte che non iniziano con `10`: ognuno apre un carattere. In esadecimale: 00-7F carattere ASCII; 80-BF continuazione; C2-DF inizio di 2 byte; E0-EF inizio di 3; F0-F4 inizio di 4. Esempio: `F0 9F 98 80 21` ha due inizi (F0 e 21), quindi 2 caratteri (l'emoji U+1F600 e !). Esercizio 6 della scheda.

<a id="p-24"></a>

### Slide 24 · UTF-8: l'esempio di ñ

La slide evidenzia con un riquadro la seconda riga della tabella (U+0080-U+07FF), quella in cui cade **ñ = U+00F1**.

1. Bit di U+00F1 su 16 bit: `00000000 11110001`. La riga 2 usa gli 11 bit bassi: `00011 110001`, cioè yyyyy = `00011`, xxxxxx = `110001`.
2. Si riempiono gli stampi: `110`+`00011` = `11000011` = C3; `10`+`110001` = `10110001` = B1.
3. Risultato: **C3 B1**, due byte.

La stessa ricetta dà tre byte per 进 (U+8FDB → `11101000 10111111 10011011` = E8 BF 9B) e quattro per un'emoji (U+1F600 → F0 9F 98 80). Verificato con `str.encode('utf-8')` e con la funzione `utf8_by_hand` del notebook.

> **Da saper fare: Codificare in UTF-8 a mano**
>
> 1. Converti il code point in binario.
> 2. Scegli la riga dall'intervallo (≤ 7F, ≤ 7FF, ≤ FFFF, oltre).
> 3. Scrivi il numero su 7, 11, 16 o 21 bit con zeri a sinistra.
> 4. Riempi da sinistra le x/y/z/u dello stampo.
> 5. Converti ogni byte in esadecimale e controlla: il primo byte inizia con 110/1110/11110, gli altri con 10.
>
> Esercizio 5 della scheda (é e 进), svolto nella sezione Studio.

<a id="p-25"></a>

### Slide 25 · Unicode in Python

Il codice della slide, con l'annotazione che in UTF-8 *é* corrisponde a 2 byte, C3 A9:

```
s = "café"
len(s)                  # 4 code point
b = s.encode("utf-8")   # b'caf\xc3\xa9'
len(b)                  # 5 byte
b.decode("utf-8") == s  # True
open("text.txt", encoding="utf-8")
```

- Da Python 3 una `str` è una sequenza di **code point**: `len()`, indici ed espressioni regolari lavorano sui caratteri, non sui byte.
- Un file invece è una sequenza di **byte** (`bytes`). **Non esiste un file di testo senza codifica**: oggi UTF-8, in dati vecchi ASCII o Latin-1. La codifica si specifica all'apertura del file.

Se si sbaglia codifica la decodifica spesso non fallisce ma produce *mojibake*: i byte C3 A9 letti come Latin-1 diventano *Ã©* (notebook, cella 19).

<a id="p-26"></a>

### Slide 26 · Stesso aspetto, code point diversi

```
a = "caf\u00e9"     # é come un code point
b = "cafe\u0301"    # e + accento acuto combinante
a == b              # False
len(a), len(b)      # (4, 5)
unicodedata.normalize("NFC", b) == a   # True
```

Le due stringhe si vedono identiche ma sono sequenze diverse: per un contatore sono due **tipi** diversi, per un tokenizer due input diversi, con token diversi. La **normalizzazione Unicode** le rende uguali: **NFC** compone (e + ◌́ → é), **NFD** scompone (é → e + ◌́).

Regola pratica: un tokenizer preaddestrato si aspetta esattamente la preelaborazione con cui è stato addestrato. Si applica la sua normalizzazione documentata, non una inventata.

> **Approfondimento: NFKC e casi reali**
>
> (Facoltativo.) Esistono anche le forme di compatibilità **NFKC/NFKD**, che oltre a comporre sostituiscono varianti «di presentazione»: la legatura ﬁ diventa *fi*, l'esponente ² diventa 2. Sono più aggressive e perdono informazione. Il problema non è teorico: testo copiato da PDF o nomi di file creati su sistemi diversi possono arrivare in forma decomposta, e due parole «uguali» finiscono in due tipi distinti.

## Tokenizzazione subword: BPE

<a id="p-27"></a>
**Slide 27 · Pausa** — Pausa di 10 minuti; dopo la pausa: imparare un vocabolario dai dati.

<a id="p-28"></a>
**Slide 28 · Tokenizzazione subword** — Byte-pair encoding: come si impara il vocabolario (training) e come lo si applica a testo nuovo (encoding).

<a id="p-29"></a>

### Slide 29 · Tre candidati per il token

- **Parole**: il livello giusto quanto a significato (significati abbastanza stabili), ma difficili da definire tra lingue, e ce ne sono sempre di nuove (Heaps).
- **Morfemi**: anche loro al livello giusto di significato, ma difficili da definire e da segmentare, soprattutto nelle lingue fusive.
- **Caratteri**: ben definiti grazie a Unicode, ma unità troppo piccole: poco significato ciascuno e sequenze lunghissime (un modello con contesto fisso vedrebbe molto meno testo).

In pratica si usa un approccio **guidato dai dati** che *impara* i token da un corpus: per lo più della grandezza di parole o morfemi, all'occorrenza piccoli come un carattere. Definizione: la **tokenizzazione** è il processo di segmentazione del testo in ingresso in token.

<a id="p-30"></a>

### Slide 30 · Perché tokenizzare, e come

- **Un insieme fisso di unità**: sistemi diversi concordano su domande semplici, come «quanto è lungo questo testo?», o se *don't* e *New York* sono uno o due token. Serve alla **replicabilità**: molte misure, tra cui la **perplexity**, presuppongono una tokenizzazione fissa (la perplexity è normalizzata per token: due modelli con tokenizer diversi non si confrontano direttamente; vedi la valutazione nella [scheda 70 della L1](L01-introduzione-al-corso.md#p-70)).
- **Niente parole sconosciute**: con token più piccoli delle parole, ogni parola mai vista è una sequenza di unità note: *lower* = `low``er`; nel caso peggiore un acronimo come *GRPO* si scrive lettera per lettera.
- **Algoritmi**: **byte-pair encoding** (BPE; Sennrich et al. 2016, derivato da un algoritmo di compressione di Gage 1994) e **unigram language modeling** (Kudo 2018), entrambi nella libreria SentencePiece. Qui si studia BPE.
- **Due fasi**: *training*, che da un corpus grezzo, già diviso grossolanamente in parole, induce un vocabolario di token; *encoding*, che segmenta una frase nuova nei token di quel vocabolario.

<a id="p-31"></a>

### Slide 31 · Training BPE: l'idea (inizio)

Corpus giocattolo di 10 caratteri su un alfabeto di 5 simboli: `A B D C A B E C A B`. Il vocabolario iniziale è l'insieme dei caratteri, {A, B, C, D, E}; la lunghezza del corpus è 10 simboli. Le slide successive aggiungono una riga alla volta.

<a id="p-32"></a>

### Slide 32 · Training BPE: primo merge A B → AB

Si contano le **coppie adiacenti**: A B 3 volte, C A 2, B D, D C, B E, E C una volta ciascuna. La più frequente è A B (3, più di ogni altra: qui è vero). Si crea il token `AB`, lo si aggiunge al vocabolario e si sostituisce ovunque: `AB D C AB E C AB`.

Il corpus passa da 10 a 7 simboli: ogni occorrenza sostituita accorcia la sequenza di 1, quindi 10 - 3 = 7.

<a id="p-33"></a>

### Slide 33 · Training BPE: secondo merge C AB → CAB

Ricontando sul nuovo corpus `AB D C AB E C AB`: C AB compare 2 volte, tutte le altre coppie (AB D, D C, AB E, E C) una volta. Si fonde in `CAB`: `AB D CAB E CAB`, lunghezza 7 - 2 = 5.

L'algoritmo in una frase: si parte dai caratteri, si fonde la coppia adiacente più frequente in un nuovo token, lo si aggiunge al vocabolario, si sostituiscono tutte le occorrenze; si ripete **k volte**. Alla fine il vocabolario contiene i caratteri più **k token nuovi**: k è l'iperparametro che fissa la dimensione del vocabolario.

<a id="p-34"></a>

### Slide 34 · L'algoritmo di training BPE

Lo pseudocodice (Figura 2.6 del libro, da Bostrom e Durrett 2020):

```
function BYTE-PAIR ENCODING(stringhe C, numero di merge k) returns vocab V
  V ← tutti i caratteri distinti in C
  for i = 1 to k do
    tL, tR ← coppia di token adiacenti più frequente in C
    tNEW ← tL + tR          # concatenazione
    V ← V + tNEW            # aggiorna il vocabolario
    sostituisci ogni occorrenza di tL, tR in C con tNEW
  return V
```

**La complicazione pratica**: i merge sono ammessi solo **dentro le parole**. Il corpus viene prima spezzato su spazi e punteggiatura, lo spazio viene attaccato all'**inizio** di ogni parola (scritto \_), e ogni parola porta il suo conteggio. I conteggi vengono dal corpus, i merge restano dentro le stringhe. Così si lavora su un dizionario {parola: frequenza}, molto più piccolo del corpus, e i token non attraversano mai i confini di parola.

> **Da saper fare: Lo pseudocodice all'orale**
>
> Saperlo riscrivere e commentare: input (corpus pre-diviso in parole con conteggi, k), inizializzazione (caratteri), ciclo (conta coppie pesate per frequenza, argmax, merge, aggiorna), output (vocabolario = caratteri + k token, *e la lista ordinata dei merge*, che serve all'encoder). Il libro dice «returns V», ma per codificare testo nuovo serve l'**ordine** dei merge.

<a id="p-35"></a>

### Slide 35 · Training su un corpus piccolo: inizio

Corpus *set new new renew reset renew*, diviso in parole con lo spazio iniziale (\_) e i conteggi:

| conteggio | parola |
| --- | --- |
| 2 | `_ n e w` |
| 2 | `_ r e n e w` |
| 1 | `s e t` |
| 1 | `_ r e s e t` |

Vocabolario iniziale: 7 simboli, {\_, e, n, r, s, t, w}. *set* non ha lo spazio iniziale perché è la prima parola del corpus: non c'è nessuno spazio prima.

I conteggi delle coppie includono le frequenze delle parole: n e compare 2 volte in *new* (che ha conteggio 2) e 2 in *renew*, 4 in totale. Tabella completa: n e 4, **e w 4**, \_ r 3, r e 3, \_ n 2, e n 2, s e 2, e t 2, e s 1.

> **Attenzione (errore nelle slide): n e non è «più frequente di ogni altra coppia»: è un pareggio**
>
> La slide dice che n e (4) è più frequente di ogni altra coppia. Falso: anche **e w vale 4** (2 in *new* + 2 in *renew*). Primo merge: pareggio tra n e ed e w, risolto dall'ordine di scansione (n e compare prima in `_ n e w`; il notebook sceglie la prima coppia incontrata).
>
> Versione corretta: «n e ed e w valgono entrambe 4, più di ogni altra coppia; a parità si prende la prima». Il risultato finale non cambia: scegliendo e w, il merge 2 sarebbe n ew → new (sempre 4) e gli 8 merge darebbero lo stesso vocabolario con `ew` al posto di `ne`. Verificato eseguendo il training con entrambe le scelte.

<a id="p-36"></a>

### Slide 36 · Merge 1: n e → ne

`ne` entra nel vocabolario (8 simboli) e sostituisce n e in ogni parola: `_ ne w` (2), `_ r e ne w` (2), `s e t`, `_ r e s e t`.

Si ricontano le coppie: ne w 4 (2 + 2), \_ r 3, r e 3, \_ ne 2, e ne 2, s e 2, e t 2, e s 1. Ora ne w è davvero il massimo, da solo. Notare che la coppia e w è sparita: la sua *e* è stata assorbita in `ne`. Merge che si sovrappongono si «rubano» caratteri, per questo i conteggi vanno rifatti a ogni passo.

<a id="p-37"></a>

### Slide 37 · Merge 2: ne w → new

Conteggio 4. Tutta la parola *new* è ora un unico token, anche dentro *renew*: `_ new` (2), `_ r e new` (2). Il token `new` non ha lo spazio iniziale, quindi è un pezzo **interno** di parola, utile anche per parole mai viste come *anew*.

Conteggi dopo il merge: \_ r 3, r e 3 (pareggio, stavolta la slide non dice nulla di sbagliato), poi \_ new 2, e new 2, s e 2, e t 2, e s 1.

<a id="p-38"></a>

### Slide 38 · Merge 3 e 4: _r, poi _re

Merge 3: \_ r → `_r` (conteggio 3: 2 da *renew*, 1 da *reset*). Merge 4: \_r e → `_re` (conteggio 3). Corpus: `_ new` (2), `_re new` (2), `s e t` (1), `_re s e t` (1); vocabolario {\_, e, n, r, s, t, w, ne, new, \_r, \_re}.

Al merge 3 \_ r e r e valgono entrambe 3: anche questo è un pareggio. Se si scegliesse r e, il merge 4 sarebbe \_ re → \_re: stesso risultato.

Il punto della slide: il sistema ha indotto un **prefisso iniziale re-** senza sapere nulla di morfologia, solo dalle frequenze. BPE trova spesso morfemi, ma solo quando coincidono con sequenze frequenti.

<a id="p-39"></a>

### Slide 39 · I merge successivi

La tabella «merge / current vocabulary» continua:

- (\_, new) → `_new`
- (\_re, new) → `_renew`
- (s, e) → `se`
- (se, t) → `set`

Dopo 8 merge il vocabolario ha **15 elementi**: 7 caratteri + 8 token (ne, new, \_r, \_re, \_new, \_renew, se, set). Tutti questi merge hanno conteggio 2 e dopo il merge 4 ci sono quattro coppie a pari merito (\_ new, \_re new, s e, e t): l'ordine riportato è quello del libro e del notebook, che a parità prendono la prima coppia incontrata.

Il merge finale produce `set` senza spazio iniziale, perché nel corpus *set* è la prima parola. Un *set* in mezzo a una frase (`_set`) verrebbe codificato come `_``set`. I sistemi reali fanno decine di migliaia di merge.

<a id="p-40"></a>

### Slide 40 · L'encoder BPE

L'**encoding** applica i merge imparati al testo nuovo, **nell'ordine in cui sono stati imparati** (per rango), in modo greedy. Le frequenze nel testo di test non contano nulla.

Esempio della slide, *\_newer*:

- `_ n e w e r`
- rango 1, n e → ne: `_ ne w e r`
- rango 2, ne w → new: `_ new e r`
- ranghi 3 e 4 non si applicano (non c'è r); rango 5, \_ new → \_new: `_new e r`
- nessun altro merge si applica: `_new``e``r`

Molti merge ricreano parole del training, altri catturano morfemi (`_re`). Altri esempi (verificati col notebook): *\_renewest* → `_renew``e``s``t`; *\_reset* → `_re``set`.

> **Da saper fare: Codificare con una lista di merge**
>
> 1. Spezza la parola in caratteri (con \_ iniziale se c'era uno spazio).
> 2. Scorri la lista dei merge dal rango 1 in giù; per ognuno sostituisci tutte le occorrenze, da sinistra a destra.
> 3. Quando la lista è finita, i simboli rimasti sono i token.
>
> Errore tipico: cercare il token più lungo del vocabolario (*longest match*). BPE non fa così: conta l'ordine dei merge. Esercizio 8 della scheda.

<a id="p-41"></a>

### Slide 41 · BPE in pratica

- **Scala**: decine di migliaia di merge su corpora enormi, vocabolari di 50.000, 100.000 o 200.000 token. La maggior parte delle parole diventa un solo token; le parole rare e sconosciute ne prendono diversi.
- **Byte, non caratteri**: BPE gira sui **byte UTF-8** del testo: 256 simboli di base, quindi non esiste mai un token sconosciuto (qualunque testo è una sequenza di byte). All'inizio l'algoritmo riscopre le sequenze di 2 e 3 byte di UTF-8 (per esempio C3 A9 = é); le sequenze illegali (merge a cavallo di caratteri) sono rare e si filtrano.
- **Pretokenizzazione**: prima del BPE, espressioni regolari dividono l'input su spazi e punteggiatura, staccano i clitici, spezzano i numeri in gruppi di cifre. I merge restano dentro questi pezzi (*chunk*).
- **Tokenizer multilingue**: addestrati su molte lingue, ma con dati dominati dall'inglese; quindi la maggior parte dei token va all'inglese e le altre lingue vengono spezzate in pezzi più corti.

> **Approfondimento: Ordini di grandezza reali**
>
> (Facoltativo.) GPT-2 usa un BPE a livello di byte con 50.257 token; il tokenizer di GPT-4 (`cl100k_base`) circa 100.000; quello di GPT-4o (`o200k_base`) circa 200.000. Un vocabolario più grande accorcia le sequenze (meno token per testo) ma ingrandisce la matrice di embedding e lo strato di output, e i token rari vengono visti poco in addestramento.

<a id="p-42"></a>

### Slide 42 · Un tokenizer reale: GPT-4o

Lo screenshot di [Tiktokenizer](https://tiktokenizer.vercel.app) mostra la frase *Anyhow, she's seen Jane's 224123 flowers anyhow!* con un colore di sfondo per token; il punto · indica uno spazio. I blocchi colorati sono 13:

`Any``how``,``·she's``·seen``·Jane``'s``·``224``123``·flowers``·anyhow``!`

- La maggior parte delle parole è **un token, spazio iniziale compreso**.
- *Jane's* è diviso (il clitico *'s* viene staccato su un nome proprio), mentre il frequente *she's* resta intero.
- *224123* diventa `224``123`: la pretokenizzazione spezza i numeri in gruppi di (al massimo) 3 cifre. Lo spazio prima del numero resta da solo, come token a sé (id 220).
- *Anyhow* maiuscolo a inizio frase è due token, `Any``how`; `·anyhow` dopo uno spazio, minuscolo, è uno.

L'output vero del tokenizer è una sequenza di **id** interi: 11865, 8923, 11, ... (il libro li elenca tutti e 13: 11865, 8923, 11, 31211, 6177, 23919, 885, 220, 19427, 7633, 18887, 147065, 0). Sono questi id che il modello riceve e predice (*next-token prediction*, L1).

<a id="p-43"></a>

### Slide 43 · Tokenizzazione tra lingue: inglese

Una frase di una ricetta, *In a deep bowl, mix the orange juice with the sugar, ginger, and nutmeg.*, con lo stesso tokenizer di GPT-4o: **19 token**. Le parole sono 14, e 13 sono token singoli (con lo spazio iniziale); solo *nutmeg* è diviso, in `·nut``meg`. Poi 3 virgole e il punto finale: 13 + 2 + 4 = 19.

(Nello screenshot *·g* e *inger* sono sulla fine di una riga e l'inizio della successiva ma hanno lo stesso colore: è un solo token, *·ginger*, spezzato dall'a capo.)

<a id="p-44"></a>

### Slide 44 · Tokenizzazione tra lingue: spagnolo

La stessa frase in spagnolo, *En un recipiente hondo, mezclar el jugo de naranja con el azúcar, jengibre, y nuez moscada.*: 16 parole, **33 token**, contro i 19 dell'inglese (1,7 volte tanti). Parole di base vengono frammentate: *hondo* «profondo» → `·h``ondo`, e così *jugo* «succo», *nuez* «noce», *jengibre* «zenzero». Nello screenshot si vede un mosaico di colori molto più fitto dentro le parole spagnole.

Lo spagnolo **non** è una lingua a basse risorse, eppure le sue parole si frammentano. La **sovrasegmentazione** costa: rappresentazioni del significato peggiori (il modello deve ricostruire la parola dai pezzi), contesti più lunghi a parità di testo (meno testo nella finestra di contesto), costi più alti di addestramento e di uso (le API si pagano a token). Nelle lingue a basse risorse si scende fino ai singoli caratteri o byte.

Verifica dal notebook dello studente: *Il comitato ha rinviato la decisione alla settimana successiva.* fa 16 token, la traduzione inglese 10.

<a id="p-45"></a>

### Slide 45 · Token che attraversano le parole: SuperBPE

**La figura** (Liu et al. 2025) confronta due segmentazioni della frase *By the way, I am a fan of the Milky Way.*, con un riquadro per token:

- BPE (blu), 13 token: `By``·the``·way``,``·I``·am``·a``·fan``·of``·the``·Milky``·Way``.`
- SuperBPE (rosa), 7 token: `By·the·way``,·I·am``·a``·fan``·of·the``·Milky·Way``.`

Idea: rilassare la pretokenizzazione. Un primo stadio di BPE impara i soliti subword dentro le parole; un secondo stadio ammette merge attraverso spazi e punteggiatura. Espressioni frequenti come *By the way* e *I am* diventano token singoli (nella figura il secondo token comprende anche la virgola davanti, *, I am*) e lo stesso testo richiede meno token. Idea simile: BoundlessBPE (Schmidt et al. 2025).

## Corpora

<a id="p-46"></a>
**Slide 46 · Corpora** — Chi ha prodotto il testo, dove, quando e perché: i dati non sono neutri.

<a id="p-47"></a>

### Slide 47 · La lingua è situata

- **Lingua**: nel mondo ci sono 7.097 lingue, ma gli algoritmi si sviluppano e si testano soprattutto sull'inglese o sulle lingue ufficiali di grandi nazioni industrializzate. Le schede 43-44 mostrano un effetto concreto di questo squilibrio.
- **Varietà**: l'African American English scrive *iont* per *I don't* e *talmbout* per *talking about*, forme che cambiano la segmentazione in parole. Gli strumenti devono funzionare con le varietà che le persone usano davvero (in Italia: dialetti, italiano regionale, scrittura dei social).
- **Code switching**: *Por primera vez veo a @username actually being hateful! it was beautiful:)*, spagnolo e inglese nello stesso enunciato. È molto comune nel mondo.
- **Genere, autore, tempo**: notizie, narrativa, Wikipedia, telefonate, note cliniche, atti parlamentari; età, genere e classe sociale di chi scrive; la lingua cambia nel tempo.

Conseguenza: un corpus è sempre un campione di una lingua in una situazione. Un modello addestrato su quel campione eredita le sue coperture e le sue lacune.

<a id="p-48"></a>

### Slide 48 · Documentare un corpus: il datasheet

Un **datasheet** (Gebru et al. 2020, *Datasheets for datasets*) o *data statement* (Bender et al. 2021) documenta un corpus con queste voci:

- **Motivazione**: perché è stato raccolto, da chi, chi l'ha finanziato.
- **Situazione**: quando e dove il testo è stato scritto o detto; compito, testo curato, social media, monologo o dialogo.
- **Varietà linguistica**: quale lingua, dialetto, regione.
- **Demografia dei parlanti**: età, genere e altre caratteristiche degli autori.
- **Processo di raccolta**: dimensione, campionamento, consenso, preelaborazione, metadati.
- **Processo di annotazione**: quali annotazioni, chi sono gli annotatori, come sono stati formati.
- **Distribuzione**: copyright e altri vincoli di proprietà intellettuale.

Serve a chi usa i dati per capire a che cosa generalizzeranno i risultati. L'esercizio 10 della scheda chiede di assegnare fatti alle voci.

> **Da saper fare: Le sette voci a memoria**
>
> Motivazione, Situazione, Varietà, Demografia, Raccolta, Annotazione, Distribuzione: nell'ordine, «perché, in che contesto, quale lingua, chi scrive, come raccolto, come etichettato, chi può usarlo». Attenzione a non confondere Situazione (contesto di produzione del testo) con Raccolta (come il corpus è stato costruito).

<a id="p-49"></a>

### Slide 49 · Riepilogo e prossima lezione

**Riepilogo**:

- parole: tipi e istanze, nessun numero fisso (Heaps);
- morfemi: radici, affissi, clitici, tipologia;
- Unicode: code point, byte UTF-8, `str` e `bytes`;
- BPE: i merge si imparano una volta e si applicano in modo greedy, nell'ordine;
- tokenizer reali, anche tra lingue diverse;
- corpora: lingua situata, datasheet.

**Prossima lezione**: *Text processing*: espressioni regolari, regole di tokenizzazione (la pretokenizzazione della scheda 41 è fatta proprio con regex), edit distance. Capitolo 2, sezioni 2.6-2.9.

## Notebook

Commento al notebook del corso `HLT-L02-words-and-tokens.ipynb` (il notebook è del docente e non è incluso).

Notebook di accompagnamento della lezione: conta parole e tipi, misura la legge di Heaps, codifica UTF-8 a mano, addestra e applica BPE passo per passo, e (opzionale) usa il vero tokenizer di GPT-4o con `tiktoken`. Serve solo la libreria standard più `matplotlib`; le celle opzionali (Alice da Gutenberg, tiktoken) richiedono la rete. Permette di controllare gli esercizi 1, 4, 5, 6, 7, 8 della scheda. Trovati tre bug reali (in `words()` con punteggiatura iniziale, nella punteggiatura tipografica di Alice, nella codifica della frase di test su Gettysburg): sono segnalati nei blocchi con la correzione verificata.

### Notebook 1 · Parole e tipi: la funzione words()

```python
def words(text, keep_punctuation=False, case_sensitive=True):
    out = []
    for chunk in text.split():
        if not case_sensitive:
            chunk = chunk.lower()
        core = chunk.strip(".,;:!?\"'()")
        trailing = chunk[len(core):] if chunk.endswith(tuple(".,;:!?\"')")) else ""
        if core:
            out.append(core)
        if keep_punctuation and trailing:
            out.extend(trailing)
    return out
```

Output:

```text
punctuation dropped: N = 16 instances, |V| = 14 types
punctuation kept: N = 18 instances, |V| = 16 types
case sensitive = True : N = 13, |V| = 7
case sensitive = False: N = 13, |V| = 6
```

Tokenizzatore minimale: divide sugli spazi (`str.split`), toglie la punteggiatura ASCII ai bordi di ogni pezzo e, se richiesto, la rimette come istanze separate (un carattere ciascuna, grazie a `extend` su una stringa). Riproduce i numeri delle slide 7-8: 16 istanze e 14 tipi senza punteggiatura, 18 e 16 con. Sulla frase dell'esercizio 1: N = 13, |V| = 7 distinguendo maiuscole, 6 senza.

> **Attenzione (errore nelle slide): Bug: punteggiatura iniziale con keep_punctuation=True**
>
> `trailing = chunk[len(core):]` assume che `core` inizi alla posizione 0 del pezzo. Se c'è punteggiatura *iniziale* l'offset è sbagliato: esce un token spurio e la punteggiatura iniziale si perde.
>
> ```
> words('"Hello," she said.', keep_punctuation=True)
> # ['Hello', 'o', ',', '"', 'she', 'said', '.']   <- 'o' spurio, manca il '"' iniziale
> words('(word) ok', keep_punctuation=True)
> # ['word', 'd', ')', 'ok']
> ```
>
> Correzione: trovare la posizione del core nel pezzo e separare punteggiatura iniziale e finale.
>
> ```
> PUNCT = ".,;:!?\"'()"
> def words(text, keep_punctuation=False, case_sensitive=True):
>     out = []
>     for chunk in text.split():
>         if not case_sensitive:
>             chunk = chunk.lower()
>         core = chunk.strip(PUNCT)
>         if not core:                      # pezzo di sola punteggiatura
>             if keep_punctuation: out.extend(chunk)
>             continue
>         start = chunk.find(core)
>         leading, trailing = chunk[:start], chunk[start + len(core):]
>         if keep_punctuation: out.extend(leading)
>         out.append(core)
>         if keep_punctuation: out.extend(trailing)
>     return out
> ```
>
> Verifica: ora dà `['"', 'Hello', ',', '"', 'she', 'said', '.']` e `['(', 'word', ')', 'ok']`, e sulla frase del picnic restituisce esattamente le stesse liste dell'originale (16/14 e 18/16). Sulle frasi usate nel notebook il bug non si manifesta, perché non hanno punteggiatura iniziale.

### Notebook 2 · Un corpus piccolo: il discorso di Gettysburg

```python
tokens = [w for w in words(GETTYSBURG, case_sensitive=False) if w != "-"]
counts = Counter(tokens)
print(f"N = {len(tokens)} instances, |V| = {len(counts)} types, type/token ratio = {len(counts)/len(tokens):.2f}")
```

Output:

```text
N = 271 instances, |V| = 138 types, type/token ratio = 0.51
 13  that
 11  the
 10  we
  8  to
  8  here
```

Il discorso di Lincoln (1863), con le lineette scritte come trattini isolati e poi scartate. Risultato: **N = 271, |V| = 138**, rapporto tipi/istanze 0,51. Le parole più frequenti sono parole funzionali: *that* 13, *the* 11, *we* 10, *to* e *here* 8, *a* 7. Unica parola con punteggiatura interna rimasta: *battle-field*, che resta un tipo solo (il trattino non è tra i caratteri tolti).

### Notebook 3 · Legge di Heaps sul discorso di Gettysburg

```python
def vocabulary_growth(tokens):
    seen, growth = set(), []
    for w in tokens:
        seen.add(w); growth.append(len(seen))
    return growth

def fit_beta(growth):
    """least-squares slope of log|V| against log N"""
    xs = [math.log(n) for n in range(1, len(growth) + 1)]
    ys = [math.log(v) for v in growth]
    ...
```

Output:

```text
fitted slope beta = 0.80
```

Si legge il testo parola per parola e si registra quanti tipi distinti si sono visti dopo N istanze; poi si stima $\beta$ come pendenza della retta dei minimi quadrati di $\log|V|$ contro $\log N$. La figura ha due pannelli: a sinistra |V| contro N in scala lineare (curva quasi rettilinea da 0 a 138 tipi su 271 istanze, con piccoli gradini piatti quando si ripetono parole); a destra la stessa curva in log-log, quasi una retta, con pendenza stimata **$\beta = 0{,}80$**.

Con 271 parole siamo nel primo regime della figura di Heaps (scheda 12): quasi ogni parola è nuova e $\beta$ è vicino a 1. Le prime 19 istanze sono tutte parole nuove (la prima ripetizione è *and*, alla ventesima), quindi all'inizio la curva coincide con la diagonale $|V| = N$.

### Notebook 4 · Alice nel paese delle meraviglie (opzionale)

```python
URL = "https://www.gutenberg.org/files/11/11-0.txt"
raw = urllib.request.urlopen(URL, timeout=30).read().decode("utf-8")
body = raw.split("*** START OF")[1].split("*** END OF")[0]
book_tokens = words(body, case_sensitive=False)
beta_book = plot_growth(book_tokens, "Alice's Adventures in Wonderland")
```

Output:

```text
N = 26531, |V| = 3793
fitted slope beta = 0.69
most frequent: [('the', 1617), ('and', 788), ('to', 710), ('a', 620), ('she', 531), ...]
```

Scarica il libro da Project Gutenberg (serve la rete; qui gli output sono quelli salvati dallo studente). Risultato: **N = 26.531, |V| = 3.793**, $\beta$ stimato **0,69**. Le parole più frequenti: *the* 1617, *and* 788, *to* 710, *a* 620, *she* 531, *of* 494, *said* 456, *it* 445, *alice* 383, *in* 354. La figura: a sinistra |V| cresce in modo concavo fino a circa 3800 (rapida all'inizio, poi sempre più lenta); a destra, in log-log, la curva è quasi una retta da (1, 1) a circa (2,7·104, 3,8·103).

Il markdown della cella 7 dice che su un libro intero $\beta$ scende a circa 0,5-0,6, ma il notebook ottiene 0,69. Perché:

1. **Il libro è corto**. 26.531 parole stanno ancora nella zona di transizione del grafico di Heaps (scheda 12), dove la curva si piega tra $10^3$ e $10^5$: il regime con $\beta \approx 0{,}44$ inizia verso $10^5$ parole. I valori 0,44-0,56 si osservano su corpora molto più grandi.
2. **Il vocabolario è gonfiato** dal bug della punteggiatura Unicode (riquadro sotto): varianti come *‘well!’* contano come tipi nuovi e aggiungono tipi rari lungo tutto il testo, alzando |V| e un po' la pendenza.
3. **Il fit sull'intera curva** incide poco, contro l'intuizione: la regressione usa un punto per ogni N, quindi il 96% dei punti ha N > 1000 e la stima è dominata dalla coda. Su corpora sintetici (Zipf) il fit su tutti gli N e quello solo su N > 1000 differiscono di meno di 0,01.

> **Attenzione (errore nelle slide): Bug: la punteggiatura tipografica non viene tolta**
>
> `words()` toglie solo la punteggiatura ASCII `.,;:!?"'()`, ma il file Gutenberg `11-0.txt` usa virgolette tipografiche ‘ ’ “ ” e la lineetta —. Queste restano attaccate alle parole:
>
> ```
> words('‘Well!’ thought Alice. “I’ve got it—”', case_sensitive=False)
> # ['‘well!’', 'thought', 'alice', '“i’ve', 'got', 'it—”']
> ```
>
> Così *well*, *‘well!’*, *well,* ecc. diventano tipi diversi: **|V| = 3793 è sovrastimato** e $\beta = 0{,}69$ ne risente. Correzione, con un'espressione regolare che tiene le lettere e l'apostrofo interno (anche tipografico), più la normalizzazione NFC:
>
> ```
> import re, unicodedata
> def book_words(text):
>     text = unicodedata.normalize("NFC", text).lower()
>     return re.findall(r"\w+(?:[’']\w+)*", text)
>
> book_words('‘Well!’ thought Alice. “I’ve got it—”')
> # ['well', 'thought', 'alice', 'i’ve', 'got', 'it']
> ```
>
> Alternativa: togliere ai bordi tutti i caratteri con categoria Unicode che inizia per P (`unicodedata.category(c).startswith('P')`: ‘ “ sono Pi, — è Pd), che dà lo stesso risultato sull'esempio ma non separa *it—and* se la lineetta è in mezzo; la regex sì. Per stimare il secondo regime conviene anche fittare solo la coda (per esempio N > 1000) o usare punti equispaziati in log N. Il valore corretto per Alice non si può calcolare qui (serve scaricare il libro): su un corpus sintetico con il 12% di parole «sporcate» da virgolette, |V| cresce del 25-40% e $\beta$ di circa 0,02.
>
> Difetto minore: `split("*** START OF")[1]` lascia nel testo il resto della riga di intestazione (*THE PROJECT GUTENBERG EBOOK ...*), una manciata di token spuri.

### Notebook 5 · Code point e byte

```python
for ch in "aé进😀":
    print(f"{ch!r:6} U+{ord(ch):04X}  {unicodedata.name(ch)}")
for s in ["café", "日本", "😀", "naïve"]:
    b = s.encode("utf-8")
    print(f"{s!r:10} {len(s)} code points, {len(b)} bytes: {b.hex(' ').upper()}")
```

Output:

```text
'a'    U+0061  LATIN SMALL LETTER A
'é'    U+00E9  LATIN SMALL LETTER E WITH ACUTE
'进'    U+8FDB  CJK UNIFIED IDEOGRAPH-8FDB
'😀'    U+1F600  GRINNING FACE
'café'     4 code points, 5 bytes: 63 61 66 C3 A9
'日本'       2 code points, 6 bytes: E6 97 A5 E6 9C AC
'😀'        1 code points, 4 bytes: F0 9F 98 80
'naïve'    5 code points, 6 bytes: 6E 61 C3 AF 76 65
```

`ord` dà il code point, `unicodedata.name` il nome ufficiale, `encode('utf-8')` i byte. Risultati: *café* 4 code point e 5 byte (é = C3 A9); *日本* 2 code point e 6 byte (3 ciascuno); l'emoji U+1F600, 1 code point e 4 byte; *naïve* 5 e 6. Sono le risposte dell'esercizio 4a.

### Notebook 6 · UTF-8 a mano

```python
ROWS = [(0x7F, "0xxxxxxx"), (0x7FF, "110xxxxx 10xxxxxx"),
        (0xFFFF, "1110xxxx 10xxxxxx 10xxxxxx"),
        (0x10FFFF, "11110xxx 10xxxxxx 10xxxxxx 10xxxxxx")]

def utf8_by_hand(ch):
    cp = ord(ch)
    template = next(t for last, t in ROWS if cp <= last)
    n_bits = template.count("x")
    bits = format(cp, f"0{n_bits}b")
    it = iter(bits)
    encoded = "".join(next(it) if c == "x" else c for c in template)
```

Output:

```text
é  U+00E9  = 11101001 in binary
  row:      110xxxxx 10xxxxxx
  payload:  00011101001  (11 bits, zero-padded on the left)
  bytes:    11000011 10101001
  hex:      C3 A9   Python agrees: C3 A9

进  U+8FDB  = 1000111111011011 in binary
  row:      1110xxxx 10xxxxxx 10xxxxxx
  payload:  1000111111011011  (16 bits, zero-padded on the left)
  bytes:    11101000 10111111 10011011
  hex:      E8 BF 9B   Python agrees: E8 BF 9B
```

Implementa la tabella della scheda 23: sceglie la riga dal code point, scrive il numero sul numero di bit disponibili (7, 11, 16, 21) con zeri a sinistra e riempie le x dello stampo in ordine. Confronta col risultato di Python. Copre ñ (C3 B1, esempio del libro), é (C3 A9) e 进 (E8 BF 9B), cioè l'esercizio 5, e l'emoji U+1F600 (F0 9F 98 80).

### Notebook 7 · Leggere i byte

```python
def byte_role(b):
    if b < 0x80:  return "1-byte character (ASCII)"
    if b < 0xC0:  return "continuation byte (10......)"
    if b < 0xE0:  return "start of a 2-byte character (110.....)"
    if b < 0xF0:  return "start of a 3-byte character (1110....)"
    return "start of a 4-byte character (11110...)"
```

Output:

```text
E2 82 AC -> '€' (1 characters)
C3 B1 6F 6C 61 -> 'ñola' (4 characters)
68 65 6C 6C 6F -> 'hello' (5 characters)
F0 9F 98 80 21 -> '😀!' (2 characters)
```

La direzione inversa: dai primi bit di ogni byte si capisce dove iniziano i caratteri e quanto sono lunghi, senza decodificare (autosincronizzazione). Sulle sequenze dell'esercizio 6: `E2 82 AC` = € (1 carattere), `C3 B1 6F 6C 61` = *ñola* (4), `68 65 6C 6C 6F` = *hello* (5), `F0 9F 98 80 21` = emoji U+1F600 + ! (2).

Nota: la funzione è didattica e non segnala i byte che in UTF-8 non possono mai comparire (C0, C1, F5-FF): li classifica come inizi di carattere. Per le sequenze dell'esercizio non importa.

### Notebook 8 · Nessun file di testo senza codifica: mojibake

```python
data = "café".encode("utf-8")
print("as utf-8: ", data.decode("utf-8"))
print("as latin-1:", data.decode("latin-1"))
with open("demo.txt", "w", encoding="utf-8") as f:
    f.write("Señor, respondió")
```

Output:

```text
as utf-8:  café
as latin-1: cafÃ©
on disk:   53 65 C3 B1 6F 72 2C 20 72 65 73 70 6F 6E 64 69 C3 B3
read back: Señor, respondió
```

Decodificare con la codifica sbagliata non dà errore: produce **mojibake**. I due byte C3 A9 di é letti come Latin-1 sono due caratteri, Ã e ©: *cafÃ©*. La seconda parte scrive *Señor, respondió* in UTF-8 e rilegge i byte: ñ = C3 B1, ó = C3 B3. Morale: specificare sempre `encoding=` in `open`.

### Notebook 9 · Normalizzazione Unicode

```python
a = "café"
b = "café"      # contiene e + U+0301 (combinante), invisibile nel sorgente
print(a == b, len(a), len(b))
print(unicodedata.normalize("NFC", a) == unicodedata.normalize("NFC", b))
```

Output:

```text
café café | equal: False | code points: 4 5 | bytes: 5 6
NFC: True | NFD: True
['U+0063', 'U+0061', 'U+0066', 'U+0065', 'U+0301']
```

Le due stringhe si vedono uguali ma *a* ha é come U+00E9 (4 code point, 5 byte) e *b* ha e + U+0301 (5 code point, 6 byte): `a == b` è False; dopo NFC (o NFD) sono uguali. La NFD di *a* è U+0063 U+0061 U+0066 U+0065 U+0301.

> **Da saper fare: Consiglio: rendere visibile l'accento combinante**
>
> Non è un bug, ma la cella è fragile: la stringa `b` contiene un U+0301 letterale, invisibile nel sorgente. Un editor o un copia-incolla che normalizza in NFC la trasforma silenziosamente in *café* composto, e la cella stamperebbe `equal: True` senza che si capisca perché. Meglio scrivere il carattere con l'escape, come nella slide: `b = "cafe\u0301"`.

### Notebook 10 · Training BPE sul corpus del libro

```python
def pair_counts(corpus):
    counts = Counter()
    for toks, n in corpus.items():
        for a, b in zip(toks, toks[1:]):
            counts[(a, b)] += n
    return counts
...
(a, b), n = counts.most_common(1)[0]   # ties: the first pair found in the corpus
BOOK_CORPUS = {"_new": 2, "_renew": 2, "set": 1, "_reset": 1}
vocab, merges = train_bpe(BOOK_CORPUS, k=8)
```

Output:

```text
merge 1: n e -> ne  (count 4; next: ew 4, _r 3, re 3)
merge 2: ne w -> new  (count 4; next: _r 3, re 3, _ne 2)
merge 3: _ r -> _r  (count 3; next: re 3, _new 2, enew 2)
merge 4: _r e -> _re  (count 3; next: _new 2, enew 2, se 2)
merge 5: _ new -> _new  (count 2; next: _renew 2, se 2, et 2)
merge 6: _re new -> _renew  (count 2; next: se 2, et 2, _res 1)
merge 7: s e -> se  (count 2; next: et 2, _res 1)
merge 8: se t -> set  (count 2; next: _rese 1)
vocabulary after 8 merges: ['_', 'e', 'n', 'r', 's', 't', 'w', 'ne', 'new', '_r', '_re', '_new', '_renew', 'se', 'set'] (15 tokens)
```

Implementazione diretta dello pseudocodice (scheda 34): il corpus è un dizionario {tupla di token: frequenza}, le coppie sono pesate con la frequenza della parola, a ogni passo si fonde la più frequente. A parità, `Counter.most_common` conserva l'ordine di inserimento, quindi vince la prima coppia incontrata. Stampa il corpus dopo ogni merge e le tre coppie seguenti.

L'output conferma le slide 35-39 e mostra i pareggi: al merge 1 «next: ew 4» (e w vale 4 come n e, vedi il riquadro della [scheda 35](L02-parole-e-token.md#p-35)); al merge 3 «next: re 3»; ai merge 5-7 ci sono più coppie a 2. Vocabolario finale: 15 token, con `set` senza spazio iniziale.

### Notebook 11 · L'encoder

```python
def encode(word, merges):
    toks = list(word)
    for pair in merges:
        toks = merge(toks, pair)
    return toks
```

Output:

```text
_newer       -> ['_new', 'e', 'r']
_renewest    -> ['_renew', 'e', 's', 't']
_lower       -> ['_', 'l', 'o', 'w', 'e', 'r']
_reset       -> ['_re', 'set']
_new         -> ['_new']
new          -> ['new']
```

Applica i merge nell'ordine appreso a una parola spezzata in caratteri (scheda 40). Risultati: `_new``e``r` per *\_newer*; `_renew``e``s``t` per *\_renewest*; *\_lower* resta in caratteri, `_``l``o``w``e``r`; `_re``set` per *\_reset*; *\_new* e *new* diventano un token ciascuno (`_new` e `new`, token diversi).

Attenzione a *\_lower*: *l* e *o* non sono nei 7 caratteri del corpus di training. Con un BPE su caratteri sarebbero simboli sconosciuti; è il BPE su byte (256 simboli di base, scheda 41) che elimina davvero il problema. Il codice Python non se ne accorge perché non controlla l'appartenenza al vocabolario.

### Notebook 12 · Il corpus dell'esercizio 7

```python
EXERCISE_7 = {"_hug": 10, "_pug": 5, "_pun": 12, "_bun": 4, "_hugs": 5}
vocab7, merges7 = train_bpe(EXERCISE_7, k=3)
```

Output:

```text
merge 1: u g -> ug  (count 20; next: _p 17, pu 17, un 16)
merge 2: _ p -> _p  (count 17; next: un 16, _h 15, hug 15)
merge 3: u n -> un  (count 16; next: _h 15, hug 15, _pu 12)
vocabulary size: 11
_bug     -> ['_', 'b', 'ug']
_pun     -> ['_p', 'un']
```

Controllo dell'esercizio 7: vocabolario iniziale di 8 simboli, merge u g (20), \_ p (17), u n (16), vocabolario finale 11. *\_bug* → `_``b``ug`, *\_pun* → `_p``un`. Svolgimento completo nella sezione Studio. (Le «next» stampate al merge 1 vengono dai conteggi *prima* del merge: pu 17 scende a 12 dopo il merge 2.)

### Notebook 13 · BPE sul discorso di Gettysburg

```python
def word_counts(text):
    return Counter("_" + w for w in words(text, case_sensitive=False) if w != "-")

vocab_g, merges_g = train_bpe(word_counts(GETTYSBURG), k=60, verbose=False)
test = "the nation dedicated to freedom and to the people"
print([tok for w in word_counts(test) for tok in encode(w, merges_g)])
```

Output:

```text
last learned tokens: ['me', 'se', '_and', '_ded', '_dedic', '_dedicat', 'ing', '_ca', '_not', '_de', 'her', '_con', '_nat', '_nation', 'iv', '_in', 'op', '_can', 'le', '_o']
['_the', '_nation', '_dedicat', 'ed', '_to', '_f', 're', 'ed', 'o', 'm', '_and', '_p', 'e', 'op', 'le']
```

60 merge su un testo vero. I primi merge sono coppie frequentissime (\_ t, a t, \_t h, r e, \_ a, \_ w, e d...); tra gli ultimi compaiono parole intere (`_and`, `_not`, `_nation`, `_can`) e pezzi di parole ripetute (`_dedic`, `_dedicat`, `ing`). La frase di test: parole frequenti nel discorso diventano un token, *freedom* (presente una volta sola) si spezza in `_f``re``ed``o``m`, *people* in `_p``e``op``le`.

> **Attenzione (errore nelle slide): Bug: la frase di test perde le parole ripetute**
>
> La codifica itera su `word_counts(test)`, che è un `Counter`: le chiavi sono i tipi, non le istanze. Le parole ripetute compaiono una sola volta: la frase ha 9 parole ma ne vengono codificate 7 (manca il secondo *to* e il secondo *the*), quindi l'output **non è la tokenizzazione della frase**. Correzione: iterare sulle istanze, nell'ordine.
>
> ```
> print([tok for w in words(test, case_sensitive=False) for tok in encode("_" + w, merges_g)])
> # ['_the', '_nation', '_dedicat', 'ed', '_to', '_f', 're', 'ed', 'o', 'm',
> #  '_and', '_to', '_the', '_p', 'e', 'op', 'le']   (17 token)
> ```
>
> Verificato eseguendo la cella corretta: 17 token invece di 15. Per il training invece `word_counts` è giusto, perché lì servono proprio le frequenze dei tipi.

### Notebook 14 · Un tokenizer reale: tiktoken (opzionale)

```python
import tiktoken
enc = tiktoken.get_encoding("o200k_base")   # GPT-4o
def show_tokens(text):
    ids = enc.encode(text)
    pieces = [enc.decode([i]) for i in ids]
    ...
```

Output:

```text
16 tokens / 10 tokens / 16 tokens / 28 tokens
[7633, 19354, 29338, 19267, 18, 326, 5918, ...]   # ids dell'ultima frase
```

Stesso tokenizer di GPT-4o (`o200k_base`, circa 200.000 token) che si vede su Tiktokenizer. Serve la rete la prima volta; gli output qui sono quelli salvati dallo studente (il punto · indica lo spazio):

- *Anyhow, Jane's dog said she's 224123 years old, anyhow.*, **16 token**: `Any``how``,``·Jane``'s``·dog``·said``·she's``·``224``123``·years``·old``,``·anyhow``.`. Stessi fenomeni della slide 42: *Anyhow* in due pezzi, *'s* staccato da *Jane* ma non da *she*, numero in gruppi di 3 cifre con lo spazio isolato.
- Inglese, *The committee postponed the decision until the following week.*, **10 token**: 9 parole e il punto, una parola = un token.
- Italiano, *Il comitato ha rinviato la decisione alla settimana successiva.*, **16 token**: `Il``·com``it``ato``·ha``·rin``vi``ato``·la``·decision``e``·alla``·settimana``·success``iva``.`. Stesse 9 parole, 1,6 volte i token; *decisione* e *successiva* riusano token inglesi (`·decision`, `·success`).
- *1234567890123 and https://web.stanford.edu/~jurafsky/slp3/ and C6H12O6*, **28 token**: `123``456``789``012``3``·and``·https``://``web``.st``an``ford``.edu``/~``jur``af``sky``/sl``p``3``/``·and``·C``6``H``12``O``6`.

Il numero è tagliato in gruppi di 3 cifre *da sinistra*, che non corrispondono alle posizioni decimali: un indizio del perché i modelli linguistici sbagliano l'aritmetica (esercizio 11).

> **Approfondimento: Limite di show_tokens**
>
> (Nota facoltativa.) `enc.decode([i])` decodifica ogni token da solo. Con un BPE su byte un token può contenere solo una parte dei byte di un carattere (per esempio in emoji o in testo cinese): decodificato da solo produce il carattere di sostituzione (U+FFFD, un rombo con il punto interrogativo). Per visualizzare token qualsiasi conviene `enc.decode_single_token_bytes(i)`, che restituisce i byte grezzi. Sulle quattro frasi del notebook, tutte ASCII, il problema non si presenta.

## Studio ed esercizi

### Guida allo studio (circa 3 h 50 min)

**Parole, tipi, Heaps** (35 min)

Schede 5-13. Saper contare N e |V| con convenzioni diverse (frase del picnic, esercizio 1), definire type/instance/token, spiegare perché «parola» dipende dal compito e dalla lingua (cinese, scheda 10). Legge di Heaps: formula, significato di k e β, i due regimi del grafico di Gutenberg, conto $m^{\beta}$. Libro §2.1 (pp. 33-37 del capitolo).

**Morfemi e tipologia** (25 min)

Schede 15-17. Radice/affisso, flessione/derivazione/clitici con esempi inglesi e italiani, le due dimensioni della tipologia (morfemi per parola; agglutinante vs fusivo) e la figura di Greenberg. Fare l'esercizio 3. Libro §2.2.

**Unicode e UTF-8** (45 min)

Schede 19-26. Code point vs glifo vs byte; perché UTF-32 no e UTF-8 sì; la tabella UTF-8 a memoria; codificare a mano (ñ, é, 进) e leggere sequenze di byte; `str` vs `bytes`; NFC/NFD. Esercizi 4, 5, 6; eseguire le celle 11-21 del notebook. Libro §2.3.

**BPE: training ed encoding** (60 min)

Schede 29-40. Rifare a mano il corpus *set new new renew reset renew* con tutti i conteggi (attenzione ai pareggi, [scheda 35](L02-parole-e-token.md#p-35)), poi l'encoder su *\_newer*, *\_renewest*, *\_lower*. Esercizi 7 e 8, controllati con le celle 23-27 del notebook. Saper scrivere lo pseudocodice. Libro §2.4.1-2.4.2.

**BPE reale, lingue, corpora** (35 min)

Schede 41-48. Byte-level BPE, pretokenizzazione, esempi di GPT-4o (Anyhow, Jane's, 224123), inglese 19 vs spagnolo 33 token e conseguenze, SuperBPE; lingua situata e datasheet. Esercizi 9, 10, 11 (provare Tiktokenizer). Libro §2.4.3 e §2.5.

**Ripasso orale** (30 min)

Rispondere ad alta voce alle domande della sezione orale senza guardare la traccia, poi confrontare. Punti che cadono spesso: differenza tipo/istanza/token, perché BPE non ha parole sconosciute (e perché servono i byte), perché l'ordine dei merge conta nell'encoder, costi della sovrasegmentazione.

### Esercizi

#### Esercizio 1 (scheda L02): contare le parole

Frase: *The cat saw the other cat, and the other cat saw the dog.* (a) Quante istanze, senza e con punteggiatura? (b) Quanti tipi, se *The* e *the* sono lo stesso tipo? E se sono diversi? (c) Quale numero è N e quale |V|?

<details><summary>Soluzione</summary>

(a) Parole separate da spazi, tolta la punteggiatura: The, cat, saw, the, other, cat, and, the, other, cat, saw, the, dog = **13 istanze**. Con virgola e punto come parole: **15**.

(b) Frequenze: the/The 4 (1 maiuscolo + 3), cat 3, saw 2, other 2, and 1, dog 1. Unendo maiuscole e minuscole: {the, cat, saw, other, and, dog} = **6 tipi**. Distinguendo: si aggiunge *The*, **7 tipi**. Con la punteggiatura come tipi, rispettivamente 8 e 9.

(c) Il numero di istanze è **N** (13 o 15), il numero di tipi è **|V|** (6 o 7). Verificato con la funzione `words` del notebook (N = 13, |V| = 7 e 6).

</details>

#### Esercizio 2 (scheda L02): legge di Heaps

$|V| = kN^{\beta}$ con $\beta = 0{,}5$. (a) Il corpus passa da N a 4N istanze: di che fattore cresce il vocabolario? (b) Che cosa significherebbe $\beta = 1$? In quale parte di un corpus la crescita ha quell'aspetto? (c) Perché nessun vocabolario può contenere tutte le parole che un modello incontrerà?

<details><summary>Soluzione</summary>

(a) $|V'| = k(4N)^{0{,}5} = 4^{0{,}5}\,kN^{0{,}5} = 2|V|$: il vocabolario **raddoppia**; $k$ si semplifica. In generale il fattore è $m^{\beta}$.

(b) $\beta = 1$ (con $k = 1$) vuol dire $|V| = N$: ogni parola letta è nuova, il vocabolario cresce linearmente. Succede all'**inizio** di un corpus, quando compaiono per la prima volta parole funzionali e comuni: è il primo regime del grafico di Gutenberg (retta verde, fino a circa $10^3$ parole). Nel notebook, il discorso di Gettysburg (271 parole) dà $\beta \approx 0{,}80$ e le prime 19 parole sono tutte nuove.

(c) Perché $|V|$ cresce senza limite con $N$ (per $\beta &gt; 0$ non c'è asintoto): le parole funzionali sono un insieme chiuso, ma le parole di contenuto (nomi propri, termini tecnici, neologismi, prestiti, errori di battitura, forme flesse rare) continuano ad arrivare. Qualunque vocabolario finito incontrerà parole sconosciute: da qui i token subword.

</details>

#### Esercizio 3 (scheda L02): morfemi

Segmenta in morfemi e classifica ogni affisso (flessivo, derivazionale, clitico); indica la radice: *unhappiness, cats, carefully, I've, l'opéra*.

<details><summary>Soluzione</summary>

- **un-happi-ness**: radice *happy* (scritta *happi* davanti al suffisso); *un-* derivazionale (negazione; non cambia categoria, resta aggettivo, ma crea una parola nuova con significato diverso); *-ness* derivazionale (aggettivo → nome).
- **cat-s**: radice *cat*; *-s* flessivo (plurale).
- **care-ful-ly**: radice *care*; *-ful* derivazionale (nome → aggettivo); *-ly* derivazionale (aggettivo → avverbio).
- **I-'ve**: *I* pronome (radice); *'ve* clitico (forma ridotta di *have*, non può stare da solo).
- **l'-opéra**: radice *opéra*; *l'* clitico (articolo determinativo francese ridotto).

Totale: 11 morfemi in 5 parole. Distinzione chiave: la flessione esprime categorie grammaticali senza creare una parola nuova, la derivazione crea una parola nuova (spesso di un'altra categoria), il clitico è una parola sintattica appoggiata a un'altra.

</details>

#### Esercizio 4 (scheda L02): code point, glifi e byte

(a) Quanti code point e quanti byte UTF-8 in *café*, in *日本* e nell'emoji U+1F600 (GRINNING FACE)? (b) La *a* in Times New Roman e in Courier: stesso code point? Stesso glifo? (c) *café* con é = U+00E9 oppure e + U+0301: sono uguali in Python? Quanti code point? Che cosa li rende uguali?

<details><summary>Soluzione</summary>

(a) *café*: 4 code point; c, a, f un byte ciascuno, é (U+00E9, riga 2) due byte C3 A9: **5 byte** (63 61 66 C3 A9). *日本*: 2 code point (U+65E5, U+672C), entrambi nella riga 3: **6 byte** (E6 97 A5 E6 9C AC). L'emoji: 1 code point (U+1F600 > U+FFFF), riga 4: **4 byte** (F0 9F 98 80).

(b) Stesso code point, U+0061; glifi diversi (il glifo è la forma disegnata dal font).

(c) No: `"caf\u00e9" == "cafe\u0301"` è False. La prima ha 4 code point, la seconda 5 (e 6 byte invece di 5). Diventano uguali con la **normalizzazione Unicode**: `unicodedata.normalize("NFC", ...)` (compone) o NFD (scompone) applicata a entrambe. Verificato in Python.

</details>

#### Esercizio 5 (scheda L02, libro 2.3): UTF-8 a mano

Codifica in UTF-8 mostrando i bit: (a) é, U+00E9; (b) 进, U+8FDB. Quanti byte ciascuno?

<details><summary>Soluzione</summary>

**(a) é = U+00E9.** 0x00E9 = 233, tra U+0080 e U+07FF: riga 2, stampo `110yyyyy 10xxxxxx`, 11 bit utili.

- 0xE9 in binario: `1110 1001`; su 11 bit: `00011101001`.
- yyyyy = `00011`, xxxxxx = `101001`.
- Byte 1: `110`+`00011` = `11000011` = **C3**; byte 2: `10`+`101001` = `10101001` = **A9**.

Risultato: **C3 A9, 2 byte**.

**(b) 进 = U+8FDB.** Tra U+0800 e U+FFFF: riga 3, stampo `1110zzzz 10yyyyyy 10xxxxxx`, 16 bit utili.

- 0x8FDB in binario (una cifra esadecimale = 4 bit): 8 = `1000`, F = `1111`, D = `1101`, B = `1011`: `1000 1111 1101 1011`.
- zzzz = `1000`, yyyyyy = `111111`, xxxxxx = `011011`.
- Byte 1: `1110`+`1000` = `11101000` = **E8**; byte 2: `10`+`111111` = `10111111` = **BF**; byte 3: `10`+`011011` = `10011011` = **9B**.

Risultato: **E8 BF 9B, 3 byte**. Entrambi verificati con `.encode('utf-8')` e con `utf8_by_hand` del notebook.

</details>

#### Esercizio 6 (scheda L02): leggere byte UTF-8

Quanti caratteri codifica ciascuna sequenza? Spiega come si capisce dai primi bit, senza decodificare: `E2 82 AC` · `C3 B1 6F 6C 61` · `68 65 6C 6C 6F` · `F0 9F 98 80 21`.

<details><summary>Soluzione</summary>

Regola: un byte `0xxxxxxx` (00-7F) è un carattere ASCII; `10xxxxxx` (80-BF) è una continuazione; `110` (C0-DF) apre un carattere di 2 byte, `1110` (E0-EF) di 3, `11110` (F0-F7) di 4. Si contano i byte che non sono continuazioni.

- `E2 82 AC`: E2 = `11100010` apre 3 byte, 82 e AC sono `10......`: **1 carattere** (€, U+20AC).
- `C3 B1 6F 6C 61`: C3 = `11000011` apre 2 byte, B1 continuazione; 6F, 6C, 61 ASCII: **4 caratteri** (*ñola*).
- `68 65 6C 6C 6F`: tutti sotto 80, ASCII: **5 caratteri** (*hello*).
- `F0 9F 98 80 21`: F0 = `11110000` apre 4 byte (9F, 98, 80 continuazioni), 21 ASCII: **2 caratteri** (l'emoji U+1F600 e !).

Verificato con `byte_role` e `bytes.fromhex(...).decode('utf-8')`.

</details>

#### Esercizio 7 (scheda L02): training BPE a mano

Corpus (parole con spazio iniziale \_ e conteggi): \_hug 10, \_pug 5, \_pun 12, \_bun 4, \_hugs 5. (a) Vocabolario iniziale e dimensione. (b) I primi tre merge, con i conteggi delle coppie che li giustificano. (c) Dimensione del vocabolario dopo tre merge. (d) Come l'encoder tokenizza \_bug e \_pun con questi tre merge?

<details><summary>Soluzione</summary>

(a) Caratteri distinti: {\_, b, g, h, n, p, s, u}, **8 simboli**.

(b) **Passo 1**, coppie pesate: u g = 10 (hug) + 5 (pug) + 5 (hugs) = **20**; \_ p = 5 + 12 = 17; p u = 17; u n = 12 + 4 = 16; \_ h = 10 + 5 = 15; h u = 15; g s = 5; \_ b = 4; b u = 4. Merge **u g → ug** (20). Corpus: \_ h ug (10), \_ p ug (5), \_ p u n (12), \_ b u n (4), \_ h ug s (5).

**Passo 2**: \_ p 17; u n 16; \_ h 15; h ug 15; p u 12 (la u di *pug* è finita in ug); p ug 5; ug s 5; \_ b 4; b u 4. Merge **\_ p → \_p** (17). Corpus: \_ h ug, \_p ug, \_p u n, \_ b u n, \_ h ug s.

**Passo 3**: u n 16; \_ h 15; h ug 15; \_p u 12; \_p ug 5; ug s 5; \_ b 4; b u 4. Merge **u n → un** (16). Nessun pareggio in testa in nessuno dei tre passi (al passo 1 \_ p e p u sono pari a 17, ma sotto u g).

(c) 8 + 3 = **11**: {\_, b, g, h, n, p, s, u, ug, \_p, un}.

(d) *\_bug*: `_ b u g` → rango 1 (u g) → `_ b ug`; ranghi 2 e 3 non si applicano: `_``b``ug` (3 token). *\_pun*: `_ p u n` → rango 1 nulla → rango 2 → `_p u n` → rango 3 → `_p``un` (2 token). *\_bug* non era nel corpus ma è codificato con token noti. Verificato con `train_bpe` ed `encode` del notebook.

</details>

#### Esercizio 8 (scheda L02): l'encoder con i merge del libro

Merge, in ordine: n e → ne, ne w → new, \_ r → \_r, \_r e → \_re, \_ new → \_new, \_re new → \_renew, s e → se, se t → set. Tokenizza \_renewest, \_lower e \_reset. Quale mostra perché BPE non ha il problema delle parole sconosciute?

<details><summary>Soluzione</summary>

**\_renewest**: `_ r e n e w e s t` → (1) n e: `_ r e ne w e s t` → (2) ne w: `_ r e new e s t` → (3) \_ r: `_r e new e s t` → (4) \_r e: `_re new e s t` → (5) nessun «\_ new» → (6) \_re new: `_renew e s t` → (7) s e: nessuna s seguita da e (la s è seguita da t) → (8) nulla. Risultato: `_renew``e``s``t`.

**\_lower**: nessun merge si applica (non c'è n e, né \_ r, né s e): `_``l``o``w``e``r`.

**\_reset**: `_ r e s e t` → (3) `_r e s e t` → (4) `_re s e t` → (7) `_re se t` → (8) `_re``set`.

Quale mostra l'assenza di parole sconosciute: **\_renewest**, parola mai vista resa con token noti (una parte del vocabolario più caratteri). *\_lower* mostra il caso peggiore, lo spelling carattere per carattere; ma attenzione, *l* e *o* non sono nell'alfabeto del corpus di training: con BPE su caratteri sarebbero simboli sconosciuti. La garanzia completa arriva solo col BPE su byte, dove i 256 byte sono tutti nel vocabolario di base. Verificato con `encode` del notebook.

</details>

#### Esercizio 9 (scheda L02): tokenizer in pratica

Con il tokenizer di GPT-4o: (a) perché *anyhow* dopo uno spazio è un token e *Anyhow* a inizio frase due, *Any* e *how*? (b) Perché *224123* diventa *224* e *123*? (c) Una frase spagnola ha 33 token, la traduzione inglese 19: perché, e due conseguenze per un modello che lavora in spagnolo?

<details><summary>Soluzione</summary>

(a) I merge si imparano dalle frequenze del corpus e i token includono lo spazio iniziale. La stringa *·anyhow* (spazio + minuscolo) compare spesso in mezzo alle frasi ed è diventata un token; *Anyhow* maiuscolo senza spazio (inizio di testo) è molto più raro, quindi non ha un token proprio e viene composto da pezzi frequenti, *Any* + *how*. Per BPE *·anyhow*, *anyhow* e *Anyhow* sono stringhe diverse.

(b) Per la **pretokenizzazione**: prima del BPE un'espressione regolare spezza i numeri in gruppi di al massimo 3 cifre, da sinistra, e i merge non attraversano questi pezzi. Quindi 224123 → 224 | 123 (e lo spazio che precede resta da solo).

(c) Il tokenizer è multilingue ma addestrato su dati dominati dall'inglese: la maggior parte dei merge (e dei 200.000 token) serve a stringhe inglesi, quindi le parole spagnole si spezzano più spesso (*hondo* → h + ondo). Conseguenze: (1) sequenze più lunghe, quindi meno testo nella finestra di contesto e più costo di calcolo in addestramento e in inferenza (e più spesa se si paga a token); (2) rappresentazioni peggiori del significato, perché il modello deve ricostruire parole da frammenti poco informativi. Nelle lingue a basse risorse si arriva a caratteri o byte singoli.

</details>

#### Esercizio 10 (scheda L02): il datasheet

Corpus di tweet italiani sui vaccini. Assegna ogni fatto a una voce del datasheet (Motivazione, Situazione, Varietà linguistica, Demografia dei parlanti, Processo di raccolta, Processo di annotazione, Distribuzione): (a) raccolti nel 2021 tramite l'API pubblica campionando l'1% del flusso; (b) la maggior parte degli autori ha 18-30 anni; (c) non ridistribuibile per i termini della piattaforma e il copyright; (d) tre annotatori hanno etichettato la posizione (stance) di ogni tweet dopo due ore di formazione; (e) testi in italiano, con alcuni tweet in napoletano; (f) costruito per studiare l'esitazione vaccinale, con un finanziamento pubblico di ricerca; (g) post spontanei sui social, non curati.

<details><summary>Soluzione</summary>

- (a) **Processo di raccolta** (come e quanto si è campionato).
- (b) **Demografia dei parlanti**.
- (c) **Distribuzione**.
- (d) **Processo di annotazione** (chi annota, cosa, con quale formazione).
- (e) **Varietà linguistica**.
- (f) **Motivazione** (perché e chi finanzia).
- (g) **Situazione** (contesto di produzione del testo: social media, spontaneo).

Il 2021 in (a) è una data della raccolta; se l'enunciato parlasse di quando i testi sono stati *scritti*, starebbe anche in Situazione.

</details>

#### Esercizio 11 (scheda L02, libro 2.1-2.2): provare un tokenizer

Su tiktokenizer.vercel.app con GPT-4o: (a) una frase di circa 15 parole in italiano e la traduzione inglese: confronta il numero di token e quali parole si spezzano. (b) Tokenizza un numero lungo (1234567890123), un URL (https://web.stanford.edu/~jurafsky/slp3/) e una formula chimica (C6H12O6): come si spezzano? Perché un LLM può essere scarso in aritmetica? (c) La stessa parola con e senza spazio iniziale, e maiuscola: cambia il numero di token?

<details><summary>Soluzione</summary>

Dati reali salvati dallo studente con `tiktoken` (`o200k_base`).

(a) *The committee postponed the decision until the following week.* = **10 token** (ogni parola un token, più il punto). *Il comitato ha rinviato la decisione alla settimana successiva.* = **16 token**: `Il``·com``it``ato``·ha``·rin``vi``ato``·la``·decision``e``·alla``·settimana``·success``iva``.`. Stesso numero di parole (9), 1,6 volte i token. Spezzate: *comitato* (3), *rinviato* (3), *decisione* (2), *successiva* (2); le ultime due riusano token inglesi. Con una frase di 15 parole ci si deve aspettare lo stesso schema: quasi tutte le parole inglesi intere, le italiane meno comuni spezzate, e un numero di token sensibilmente più alto per l'italiano.

(b) 28 token in tutto. Numero: `123``456``789``012``3`, gruppi di 3 cifre da sinistra. URL: `·https``://``web``.st``an``ford``.edu``/~``jur``af``sky``/sl``p``3``/` (15 pezzi, tagli arbitrari come *.st|an|ford*). Formula: `·C``6``H``12``O``6`. Aritmetica: i gruppi partono da sinistra e non sono allineati alle posizioni decimali (in 1234 il token 123 contiene le migliaia, in 123 le centinaia), quindi la stessa cifra finisce in token diversi a seconda della lunghezza del numero; il riporto attraversa i confini di token; e il modello vede *id* di token, non valori numerici.

(c) Dalla frase di prova: `·anyhow` (con spazio, minuscolo) è 1 token, *Anyhow* maiuscolo a inizio testo è 2, `Any``how`. In generale il numero di token può cambiare con lo spazio iniziale e con la maiuscola, perché sono stringhe diverse per BPE: parole comuni tendono a restare 1 token in tutte le forme, parole meno comuni si spezzano soprattutto nelle forme senza spazio o maiuscole. Il caso *anyhow* senza spazio e minuscolo non è nei dati salvati: va provato sul sito.

</details>

#### Esercizio aggiuntivo A: stimare β da due corpora

Dalla tabella della scheda 11: Brown corpus ha 38 mila tipi su 1 milione di istanze, COCA 2 milioni di tipi su 440 milioni. Supponendo che seguano la stessa legge di Heaps, stima $\beta$. Il risultato è nell'intervallo 0,44-0,56? Commenta.

<details><summary>Soluzione</summary>

$\beta = \dfrac{\ln(2\,000\,000/38\,000)}{\ln(440\,000\,000/1\,000\,000)} = \dfrac{\ln 52{,}6}{\ln 440} = \dfrac{3{,}96}{6{,}09} \approx 0{,}65$.

È più alto di 0,44-0,56. Motivi: i due corpora non sono lo stesso testo che cresce (genere e composizione diversi; COCA contiene molti più nomi propri, termini tecnici e testo del web), e i conteggi dei tipi dipendono dalla tokenizzazione adottata. Il libro stesso dice «0,44-0,56 o anche più alti»: $\beta$ dipende da corpus e genere. Calcolo verificato in Python.

</details>

#### Esercizio aggiuntivo B: pareggi nel training BPE

Nel corpus *set new new renew reset renew* (scheda 35) scrivi tutti i conteggi delle coppie al primo passo. C'è un pareggio? Rifai i primi due merge scegliendo l'altra coppia: il vocabolario dopo 8 merge cambia?

<details><summary>Soluzione</summary>

Conteggi: n e 4, e w 4, \_ r 3, r e 3, \_ n 2, e n 2, s e 2, e t 2, e s 1. **Pareggio** tra n e ed e w a 4.

Scegliendo e w: corpus `_ n ew` (2), `_ r e n ew` (2), `s e t`, `_ r e s e t`; al passo 2 la coppia massima è n ew = 4, merge → `new`. Da lì il corpus è identico a quello del libro, e i merge 3-8 sono gli stessi (\_r, \_re, \_new, \_renew, se, set). Vocabolario finale: 15 elementi, uguale a quello del libro tranne `ew` al posto di `ne`. Anche al merge 3 c'è un pareggio (\_ r e r e, 3) e ai merge 5-7 più coppie a 2: le implementazioni reali fissano una regola deterministica (per esempio la prima coppia incontrata, o l'ordine lessicografico). Verificato rieseguendo il training con entrambe le scelte.

</details>

### Domande tipo orale

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
