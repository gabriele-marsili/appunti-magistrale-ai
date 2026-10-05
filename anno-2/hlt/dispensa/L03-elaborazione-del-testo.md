# L3 · Elaborazione del testo

*Text Processing* · 29/09/2026 · Claudio Gallicchio · lettura: J&M cap. 2, §2.6-2.9

[Versione interattiva sul sito](https://gabriele-marsili.github.io/appunti-magistrale-ai/anno-2/hlt/sito/#L3) · [Indice della dispensa](README.md)

Gli strumenti classici, deterministici, per lavorare sul testo. Le **espressioni regolari** descrivono insiemi di stringhe (quadre, contatori, ancore, disgiunzione, gruppi, lookahead) e servono per cercare, sostituire (ELIZA) e **pretokenizzare** prima di BPE (la regex di GPT-2). Con `tr`, `sort` e `uniq` si contano le parole di un corpus in una riga. Quando i token devono essere parole si usa una **tokenizzazione a regole** (standard Penn Treebank, tokenizer a regex di NLTK, segmentazione in frasi) con eventuale normalizzazione (case folding, lemmatizzazione, stemmer di Porter). Infine la **distanza di edit minima**, calcolata con la programmazione dinamica, misura quanto sono simili due stringhe e con il backtrace dà l'allineamento, base del word error rate.

## Indice

- [Apertura](#apertura)
- [Espressioni regolari](#espressioni-regolari)
- [Strumenti Unix](#strumenti-unix)
- [Tokenizzazione a regole](#tokenizzazione-a-regole)
- [Distanza di edit minima](#distanza-di-edit-minima)
- [Notebook](#notebook)
- [Studio ed esercizi](#studio-ed-esercizi)

## Apertura

<a id="p-1"></a>
**Slide 1 · Elaborazione del testo** — Lezione 3 (Gallicchio, 29 settembre 2026): gli strumenti classici per lavorare sul testo, cioè espressioni regolari, tokenizzazione a regole e distanza di edit.

<a id="p-2"></a>

### Slide 2 · Indice della lezione

Quattro parti, tutte dalla seconda metà del capitolo 2 del libro. Dopo la tokenizzazione appresa dai dati (BPE, [L2](L02-parole-e-token.md#p-28)) si torna agli strumenti **deterministici**, scritti a mano, che restano ovunque nella pipeline:

- **Espressioni regolari**: il linguaggio per descrivere insiemi di stringhe; servono per cercare, sostituire e anche per la **pretokenizzazione** che precede BPE.
- **Strumenti Unix** (`tr`, `sort`, `uniq`): contare le parole di un corpus in una riga di comando.
- **Tokenizzazione a regole**: quando i token devono essere parole (parsing, linguistica), lo standard Penn Treebank, la segmentazione in frasi, la normalizzazione (case folding, lemmatizzazione, stemming).
- **Distanza di edit minima**: quanto sono simili due stringhe, calcolata con la **programmazione dinamica**, e l'allineamento che se ne ricava.

Il filo comune: sono tutti algoritmi senza apprendimento, veloci e trasparenti, che si usano prima o intorno ai modelli neurali.

<a id="p-3"></a>

### Slide 3 · Riferimento: J&M capitolo 2, §2.6-2.9

Lettura principale: Jurafsky e Martin, *Speech and Language Processing*, 3a ed. (draft del 19 agosto 2026), **capitolo 2, sezioni 2.6-2.9**: espressioni regolari (2.6), strumenti Unix (2.7), tokenizzazione a regole (2.8), distanza di edit minima (2.9); più il riassunto dell'intero capitolo (2.10). Il QR code porta al sito del libro, web.stanford.edu/~jurafsky/slp3/.

Nota per lo studio: la parte sulla **normalizzazione** (case folding, lemmatizzazione, stemmer di Porter, schede 33-34) non è nel draft 2026 del capitolo 2; veniva dalle edizioni precedenti del libro. Per quella parte le schede sono la fonte principale.

Gli esercizi di fine capitolo 2.4-2.10 riguardano proprio questa lezione (regex, ELIZA, edit distance): alcuni sono svolti nella sezione Studio.

## Espressioni regolari

<a id="p-4"></a>
**Slide 4 · Espressioni regolari** — Un linguaggio algebrico per specificare insiemi di stringhe: la base di ricerca, sostituzione e pretokenizzazione.

<a id="p-5"></a>

### Slide 5 · Che cos'è un'espressione regolare

Una **espressione regolare** (*regex*) è una notazione algebrica che caratterizza un **insieme di stringhe**: il pattern `r"Buttercup"` descrive l'insieme che contiene la sola stringa *Buttercup*. `re.search(pattern, s)` scandisce `s` da sinistra e restituisce la **prima** corrispondenza (qui *Buttercup* dentro *I'm called little Buttercup*), oppure `None`.

Tre usi nel corso:

- **Ricerca**: trovare un pattern in una riga o in un testo lungo (`grep`, editor come vim ed Emacs, ogni linguaggio di programmazione).
- **Sostituzione**: dire come cambiare la stringa trovata (`re.sub`); ricerca e sostituzione sono il cuore della tokenizzazione a regole.
- **Pretokenizzazione**: il passo che, prima di BPE, spezza il corpus grosso modo sugli spazi è una regex (schede 18-20; [L2 scheda 41](L02-parole-e-token.md#p-41)).

**Raw string**: in Python si scrive `r"..."`, così il backslash resta un carattere e arriva intatto al motore regex. Senza `r`, `"\b"` sarebbe il carattere *backspace* e non il confine di parola. Le varianti (Python `re`, libreria `regex`, grep, POSIX) differiscono nei dettagli: conviene provare il pattern in un tester online.

<a id="p-6"></a>

### Slide 6 · Disgiunzione di caratteri: le parentesi quadre

Le **parentesi quadre** indicano **un solo carattere** scelto in un insieme. Le regex sono *case sensitive*: `r"[mM]ary"` trova sia *Mary* sia *mary*.

| Pattern | Significato | Esempio (prima corrispondenza) |
| --- | --- | --- |
| `[mM]ary` | Mary o mary | *Mary* Ann stopped by Mona's |
| `[abc]` | a, b oppure c | In uomini, in sold**a**ti |
| `[1234567890]` | una cifra qualunque | plenty of **7** to 5 |
| `[A-Z]`, `[a-z]`, `[0-9]` | **intervallo** (*range*): una maiuscola, una minuscola, una cifra | we should call it '**D**renched Blossoms'; **m**y beans...; Chapter **1**: Down the Rabbit Hole |
| `[^A-Z]` | **negazione**: non una maiuscola | O**y**fn pripetchik |
| `[^Ss]` | né S né s | **I** have no exquisite reason for't |
| `[^.]` | non un punto (dentro le quadre il punto è letterale) | **o**ur resident Djinn |
| `[e^]` | e oppure ^ (il caret non è in prima posizione: è letterale) | look up **^** now |
| `a^b` | secondo la slide, la stringa a^b | look up a^b now (vedi riquadro) |

Il caret nega **solo se è il primo simbolo dopo `[`**. Gli intervalli seguono l'ordine dei code point: `[b-g]` è uno fra b, c, d, e, f, g; `[2-5]` uno fra 2, 3, 4, 5. Tutti gli esempi sono stati verificati con `re.search` (l'ultimo no, vedi sotto).

> **Attenzione (errore nelle slide): r"a^b" non trova mai «a^b» in Python**
>
> La tabella (presa dal libro, Fig. 2.10) dice che `r"a^b"` corrisponde alla stringa *a^b* in «look up a^b now», e il libro aggiunge che fuori dalle quadre il caret «di solito» sta per un caret. In Python non è così: fuori dalle parentesi quadre `^` è **sempre un'ancora** (inizio stringa, o inizio riga con `re.M`), anche in mezzo al pattern. Quindi `r"a^b"` chiede «a, poi inizio riga, poi b», che non può mai succedere.
>
> Verifica: `re.search(r"a^b", "look up a^b now")` restituisce `None`, e lo stesso con la libreria `regex`. Versione corretta: **`r"a\^b"`** (caret con escape), che trova *a^b* in posizione 8. Il caret letterale non in prima posizione dentro le quadre (`[e^]`) invece funziona. Il comportamento del libro vale per le regex POSIX di base (`grep` senza `-E`), dove `^` fuori dall'inizio è letterale.

<a id="p-7"></a>

### Slide 7 · Ripetizione: il linguaggio delle pecore

Obiettivo: descrivere *baa!*, *baaa!*, *baaaa!*, ..., cioè b, almeno due a, punto esclamativo.

- `r"ba*!"` è **sbagliato**: la **stella di Kleene** `*` vuol dire «zero o più occorrenze del carattere precedente», quindi accetta anche *b!* e *ba!*.
- `r"baaa*!"`: b, poi aa obbligatorie, poi zero o più a. È il linguaggio giusto.
- `r"baa+!"`: lo stesso linguaggio con il **più di Kleene** `+`, «una o più occorrenze».

Verificato con `re.fullmatch`: *b!* e *ba!* passano solo con il primo pattern; *baa!*, *baaa!*, *baaaaa!* passano con tutti e tre.

La ripetizione si applica al **carattere o all'espressione immediatamente precedente**: `r"[ab]*"` è una sequenza di zero o più caratteri, ciascuno a o b (*aaaa*, *ababab*, *bbbb* e anche la stringa vuota). Il modo standard di scrivere «un numero intero» è `r"[0-9]+"`. Relazione utile: `x+` equivale a `xx*`.

> **Da saper fare: Stella che accetta il vuoto**
>
> Errore tipico all'esame: usare `*` quando serve almeno un'occorrenza. Poiché `*` accetta zero occorrenze, `re.search(r"[0-9]*", "abc")` ha successo e restituisce la stringa **vuota** in posizione 0: un pattern che può corrispondere al vuoto corrisponde sempre, da qualche parte. Per «almeno una cifra» serve `[0-9]+`.

<a id="p-8"></a>

### Slide 8 · Contatori e jolly

La tabella degli operatori di ripetizione (**contatori**):

| Regex | Corrisponde a |
| --- | --- |
| `*` | zero o più occorrenze del carattere o espressione precedente |
| `+` | una o più occorrenze |
| `?` | zero o una occorrenza (elemento opzionale) |
| `{n}` | esattamente n occorrenze |
| `.` | un carattere qualsiasi (tranne il newline) |
| `.*` | una stringa qualsiasi di zero o più caratteri |

- `r"colou?r"`: la u è opzionale, quindi *color* e *colour* (non *colouur*); `r"koalas?"` trova *koala* e *koalas*.
- `r"ax{10}z"`: a, esattamente dieci x, z. Con nove x non corrisponde; con undici neppure, perché dopo la decima x serve la z.
- `r"rose.*rose"`: il **jolly** `.` con la stella è «qualunque cosa»: trova una riga in cui *rose* compare due volte. Non attraversa le righe: su *rose\nrose* non trova nulla.

Il libro elenca anche le forme `{n,m}` (da n a m), `{n,}` (almeno n), `{,m}` (al massimo m). Tutti gli esempi sono stati eseguiti in Python.

<a id="p-9"></a>

### Slide 9 · Ancore e confini di parola

| Regex | Corrisponde a |
| --- | --- |
| `^` | inizio riga |
| `$` | fine riga |
| `\b` | confine di parola |
| `\B` | non confine di parola |

- `r"^The"`: *The* solo a inizio riga. Il caret ha tre usi: ancora di inizio riga, negazione come primo simbolo dentro le quadre, caret letterale (in Python quest'ultimo richiede `\^` o una posizione non iniziale dentro le quadre, vedi [scheda 6](L03-elaborazione-del-testo.md#p-6)).
- `r"^The dog\.$"`: una riga che contiene **esattamente** *The dog.* Il backslash rende il punto letterale; senza, `r"^The dog.$"` accetta anche *The dog!* e *The dogo* (verificato). Con uno spazio finale (*The dog.* ) nessuno dei due corrisponde.
- `r"\bthe\b"`: la parola *the* ma non dentro *other*. Per `\b` una «parola» è una sequenza di lettere, cifre e underscore (i caratteri di `\w`): `r"\b99\b"` trova 99 in *There are 99 bottles* e in *\$99* (il dollaro non è un carattere di parola), non in *299 bottles* (fra 2 e 9 non c'è confine) né in *99\_bottles*.

**Larghezza zero**: ancore e confini corrispondono alla stringa vuota fra due caratteri, non consumano nulla. In `r"the\b the"` il `\b` verifica il confine fra e e spazio, e lo spazio resta disponibile per il resto del pattern: il pattern trova *the the*.

<a id="p-10"></a>

### Slide 10 · Disgiunzione, raggruppamento e precedenza

- `r"cat|dog"`: la **barra verticale** (*pipe*) è la disgiunzione fra stringhe. Le quadre non bastano: `r"[catdog]"` è **un** carattere fra c, a, t, d, o, g.
- `r"gupp(y|ies)"`: le **parentesi** fanno comportare un pezzo di pattern come un singolo carattere per gli operatori intorno. Senza, `r"guppy|ies"` significa *guppy* oppure *ies*: la sequenza lega più forte della pipe (su *guppy guppies* trova *guppy* e *ies*).
- `r"(Column [0-9]+ +)*"`: la stella si applica di default a un solo carattere; con le parentesi ripete l'intera sequenza *Column*, numero, spazi. `r"Column [0-9]+ *"` invece troverebbe una sola *Column* seguita da spazi.

**Precedenza** degli operatori, dalla più alta alla più bassa (tabella della slide):

| Livello | Operatori |
| --- | --- |
| Parentesi | `( )` |
| Contatori | `* + ? {}` |
| Sequenze e ancore | `the ^my end$` |
| Disgiunzione | `|` |

Conseguenze: `r"the*"` è *th* seguito da zero o più e, quindi trova *theeeee* ma non *thethe* (per quello serve `(the)*`); `r"the|any"` è *the* oppure *any*, non *thany* o *theny* (per quello serve `th(e|a)ny`).

> **Da saper fare: Leggere una regex con la precedenza**
>
> Metodo: (1) individua le parentesi; (2) attacca ogni contatore al solo elemento che lo precede; (3) leggi le sequenze; (4) solo alla fine spezza sulle pipe. Esempio: `^ab+|cd*$` si legge `(^a(b+))|(c(d*)$)`: «a inizio riga seguita da una o più b» oppure «c seguita da zero o più d a fine riga».

<a id="p-11"></a>

### Slide 11 · Matching greedy e non greedy

I pattern sono **greedy** (avidi): fra le corrispondenze possibili che partono nella stessa posizione prendono la **più lunga**. `re.search(r"[a-z]*", "once upon a time")` potrebbe corrispondere alla stringa vuota, a *o*, *on*, *onc* o *once*: restituisce *once* (verificato).

Per ottenere la corrispondenza più corta si usano gli operatori **non greedy** (*lazy*):

- `*?`: stella di Kleene che consuma il meno possibile (`[a-z]*?` sulla stessa frase restituisce la stringa vuota);
- `+?`: più di Kleene che consuma il meno possibile (`[a-z]+?` restituisce *o*).

È il **secondo significato del punto interrogativo**: dopo un carattere significa «opzionale», dopo un contatore significa «il più corto possibile».

Quando conta: estrarre il contenuto fra delimitatori. Su `<b>uno</b> e <b>due</b>`, il pattern `<b>.*</b>` prende tutto dal primo tag di apertura all'ultimo tag di chiusura; `<b>.*?</b>` si ferma al primo `</b>` e trova i due elementi separatamente.

Nota: greedy riguarda la lunghezza a partire da una posizione. La regex trova comunque la corrispondenza che **inizia più a sinistra**: su *Once upon* (O maiuscola) `[a-z]*` restituisce la stringa vuota in posizione 0, perché a posizione 0 una corrispondenza vuota esiste già.

<a id="p-12"></a>

### Slide 12 · Esempio: trovare l'articolo the; precisione e recall

Raffinamenti successivi di un pattern per l'articolo inglese *the*:

- `r"the"` perde *The* a inizio frase: un **falso negativo** (una stringa giusta che non troviamo).
- `r"[tT]he"` trova *the* anche dentro o*the*r e *the*re (evidenziati in azzurro nella slide): **falsi positivi** (stringhe trovate per errore).
- `r"\b[tT]he\b"`: confine di parola su entrambi i lati, elimina quei falsi positivi.

Correggere un sistema significa lavorare su due fronti antagonisti:

- **Precisione** (*precision*): ridurre i falsi positivi.
- **Recall** (*richiamo*): ridurre i falsi negativi.

Allargare il pattern alza il recall ma tende ad abbassare la precisione, e viceversa. Il libro darà definizioni numeriche nel capitolo 4; in anticipo: $P = \frac{TP}{TP+FP}$, $R = \frac{TP}{TP+FN}$. Esempio su *The other one there, the blithe one. The end, then.* (3 articoli): `the` trova 5 stringhe di cui 1 giusta ($P = 1/5$, $R = 1/3$); `[tT]he` ne trova 7, 3 giuste ($P = 3/7$, $R = 1$); `\b[tT]he\b` ne trova 3, tutte giuste ($P = R = 1$). Verificato con `re.finditer`. Il pattern finale sbaglierebbe ancora con *THE* maiuscolo o con *the\_*.

<a id="p-13"></a>

### Slide 13 · Alias ed escape

**Alias**: abbreviazioni per insiemi comuni; la maiuscola è la **negazione** della minuscola.

| Regex | Espansione | Significato | Prima corrispondenza |
| --- | --- | --- | --- |
| `\d` | `[0-9]` | una cifra | Party of **5** |
| `\D` | `[^0-9]` | una non cifra | **B**lue moon |
| `\w` | `[a-zA-Z0-9_]` | alfanumerico o underscore | **D**aiyu |
| `\W` | `[^\w]` | non alfanumerico | **!**!!! |
| `\s` | `[ \r\t\n\f]` | spazio bianco (spazio, tab, a capo...) | inConcord (lo spazio) |
| `\S` | `[^\s]` | non spazio bianco | **i**n Concord |

**Escape**: il backslash dà il significato letterale a un carattere speciale.

| Regex | Corrisponde a | Esempio |
| --- | --- | --- |
| `\*` | un asterisco | K**\***A\*P\*L\*A\*N |
| `\.` | un punto | Dr**.** Livingstone, I presume |
| `\?` | un punto interrogativo | Why don't they come and lend a hand**?** |
| `\n` | un a capo |  |
| `\t` | un tab |  |

Tutte le prime corrispondenze verificate con Python.

> **Approfondimento: Alias in Python 3 e Unicode**
>
> (Facoltativo.) Le espansioni della tabella valgono per l'ASCII. In Python 3, sui pattern `str`, `\d` e `\w` sono **Unicode**: `\w` accetta anche *è*, *ß*, ideogrammi cinesi; `\d` anche le cifre arabo-indiane. Per il comportamento solo ASCII si usa il flag `re.ASCII`. Anche `\s` include più caratteri della tabella (per esempio `\v` e gli spazi Unicode). Collegamento con [L2 scheda 26](L02-parole-e-token.md#p-26): due stringhe uguali a vista possono avere code point diversi, e una regex lavora sui code point.

<a id="p-14"></a>

### Slide 14 · Sostituzioni

`re.sub(pattern, repl, string)` prende un pattern da cercare, una stringa di rimpiazzo e la stringa su cui lavorare, e sostituisce **tutte** le occorrenze non sovrapposte, da sinistra a destra. `re.sub(r"cherry", r"apricot", s)` cambia ogni *cherry* in *apricot*.

Il secondo esempio converte le date dal **formato americano** (mese/giorno/anno) al **formato europeo** (giorno-mese-anno):

```
re.sub(r"(\d{2})/(\d{2})/(\d{4})", r"\2-\1-\3", s)
The date is 10/15/2011  ->  The date is 15-10-2011
```

Il pattern cerca due cifre, barra, due cifre, barra, quattro cifre; le tre coppie di parentesi memorizzano mese, giorno e anno, e il rimpiazzo le rimette in ordine 2, 1, 3 separate da trattini. Verificato: l'output è esattamente *The date is 15-10-2011*. Il meccanismo delle parentesi è spiegato nella scheda successiva.

Limite: il pattern non controlla che il mese sia fra 01 e 12, né i confini di parola; su *110/15/20111* sostituirebbe comunque un pezzo. In pratica si aggiungerebbe `\b` ai bordi.

<a id="p-15"></a>

### Slide 15 · Sostituzioni e gruppi di cattura

**Gruppo di cattura**: ogni coppia di parentesi memorizza la sottostringa che ha trovato in un registro numerato, contando le parentesi aperte **da sinistra a destra**. Nel pattern delle date il mese è il gruppo 1, il giorno il 2, l'anno il 3; nel rimpiazzo `\1`, `\2`, `\3` li richiamano (in Python si leggono anche con `m.group(1)`).

**Trovare ripetizioni**: i gruppi servono anche senza sostituzione, perché `\1` può comparire *nel pattern stesso* (*backreference*). `r"\b([A-Za-z]+)\s+\1\b"` cattura una parola e chiede che la stessa parola ricompaia dopo degli spazi: trova *the the* in *Paris in the the spring*, non trova nulla in *the theory* grazie al `\b` finale. È l'esercizio 2.5.1 del libro (*Humbert Humbert*).

**Gruppo non catturante**: `(?: pattern )` raggruppa (per un contatore o una disgiunzione) senza occupare un registro. Nel pattern

```
(?:\d\d/\d\d/\d\d\d\d\s+){14}(\d\d/\d\d/\d\d\d\d)
```

le prime 14 date, ciascuna seguita da spazi, sono ripetute senza memorizzarle, e solo la quindicesima finisce nel gruppo 1. Verificato su 15 date separate da spazi: `m.group(1)` è la quindicesima e `len(m.groups())` vale 1. Con parentesi normali il `{14}` avrebbe comunque un solo registro, che conterrebbe l'ultima delle 14 ripetizioni: il gruppo non catturante evita la confusione sulla numerazione.

<a id="p-16"></a>

### Slide 16 · Asserzioni lookahead

Un **lookahead** guarda avanti nel testo per controllare se un pattern corrisponde, **senza spostare il puntatore** di matching. Come ancore e confini è a **larghezza zero**.

- `(?= pattern)`: vero se *pattern* compare subito dopo (lookahead positivo).
- `(?! pattern)`: vero se *pattern* **non** compare subito dopo (lookahead negativo). Serve a escludere un caso speciale mentre si analizza qualcosa di complesso.

Esempio della slide: `r"^(?![tT])(\w+)\b"` = la prima parola della riga, a meno che cominci con t o T. Passo per passo: `^` inizio riga; `(?![tT])` controlla che il prossimo carattere non sia t o T, senza consumarlo; `(\w+)` cattura la parola partendo dallo stesso punto; `\b` la chiude.

Verifica: *Once upon* → *Once*; *42 is it* → *42* (`\w` include le cifre); *Tomorrow we go* e *the end* → nessuna corrispondenza; anche una riga che inizia con spazi non corrisponde, perché dopo `^` serve subito un carattere di parola.

Esempio positivo: `r"\b\w+(?=ing\b)"` su *walking and singing things* restituisce *walk* e *sing*: la radice viene presa, il suffisso *ing* viene solo controllato.

<a id="p-17"></a>

### Slide 17 · ELIZA: una cascata di sostituzioni

Il dialogo nella figura (dal libro):

- User: *They're always bugging us about something or other.* → ELIZA: CAN YOU THINK OF A SPECIFIC EXAMPLE
- User: *Well, my boyfriend made me come here.* → ELIZA: YOUR BOYFRIEND MADE YOU COME HERE
- User: *He says I'm depressed much of the time.* → ELIZA: I AM SORRY TO HEAR YOU ARE DEPRESSED

Come funziona **ELIZA** (Weizenbaum 1966, il sistema che apriva la [lezione 2](L02-parole-e-token.md#p-5)): una **cascata di sostituzioni regex**. Primo stadio: l'input viene messo in maiuscolo e i pronomi vengono ribaltati (MY → YOUR, I'M → YOU ARE, ME → YOU), così quando ELIZA ripete un pezzo della frase sembra riferirsi correttamente all'utente. Secondo stadio: altre regole riconoscono pattern e trasformano tutto l'input in una risposta:

```
re.sub(r".* YOU ARE (DEPRESSED|SAD) .*",
       r"I AM SORRY TO HEAR YOU ARE \1", input)
re.sub(r".* ALWAYS .*",
       r"CAN YOU THINK OF A SPECIFIC EXAMPLE", input)
```

Il gruppo di cattura `(DEPRESSED|SAD)` riporta nella risposta l'aggettivo usato dall'utente; `.*` ai due lati fa corrispondere tutta la riga, che viene così sostituita per intero. Verificato con una mini implementazione: le tre risposte del dialogo escono identiche (la terza dopo il passaggio I'M → YOU ARE; la seconda richiede solo il ribaltamento dei pronomi).

Nel notebook: [implementazione di ELIZA](L03-elaborazione-del-testo.md), con il bug degli spazi descritto nel riquadro qui sotto e la correzione con `\b`.

> **Da saper fare: Dettagli dei pattern di ELIZA**
>
> Gli spazi nel pattern contano: `.* YOU ARE (DEPRESSED|SAD) .*` richiede uno spazio prima di YOU e uno dopo l'aggettivo. Quindi *I'm sad* (che diventa YOU ARE SAD, all'inizio e senza nulla dopo) **non** corrisponde, e ELIZA risponderebbe con un'altra regola. L'ordine delle regole nella cascata decide quale scatta quando più pattern corrispondono: è la stessa logica dello stemmer di Porter ([scheda 34](L03-elaborazione-del-testo.md#p-34)).

<a id="p-18"></a>

### Slide 18 · Regex per la pretokenizzazione BPE: il pretokenizer di GPT-2

Prima di BPE il corpus viene diviso in **chunk** su spazi e punteggiatura; i merge non attraversano mai i confini dei chunk ([L2 scheda 41](L02-parole-e-token.md#p-41)). GPT-2 (Radford et al. 2019) lo fa con **una sola regex**, trascritta dalla slide:

```
import regex as re
pat = re.compile(
  # Contractions: 't and 'm are tokens
  r"'s|'t|'re|'ve|'m|'ll|'d|"
  # Words: sequence of Unicode letters (after optional space)
  r" ?\p{L}+|"
  # Number: sequence of digits (after optional space)
  r" ?\p{N}+|"
  # Punctuation: sequence of non-alphanumeric/non-space (after optional space)
  r" ?[^\s\p{L}\p{N}]+|"
  # whitespace
  r"\s+(?!\S)|\s+"
)
text = "We're 350 dogs! Um, lunch?"
print(pat.findall(text))
['We', "'re", ' 350', ' dogs', '!', ' Um', ',', ' lunch', '?']
```

Serve la libreria esterna **`regex`** (non il modulo standard `re`) perché supporta le **proprietà Unicode**: `\p{L}` qualunque lettera di qualunque alfabeto, `\p{N}` qualunque numero; `\P{L}` e `\P{N}` le negazioni. Così il pretokenizer funziona anche su *caffè*, *perché*, cirillico o cinese, dove `[A-Za-z]` fallirebbe. Le parti della regex sono commentate nella scheda successiva.

<a id="p-19"></a>

### Slide 19 · Le cinque alternative del pretokenizer

Il riquadro evidenzia le cinque alternative, provate **in ordine** in ogni posizione:

1. **Contrazioni** `'s|'t|'re|'ve|'m|'ll|'d`: i clitici inglesi diventano chunk a sé ([L2 scheda 16](L02-parole-e-token.md#p-16)). Sono in testa, così vincono sull'apostrofo come punteggiatura.
2. **Parole**  `?\p{L}+`: una sequenza di lettere, con uno spazio iniziale opzionale.
3. **Numeri**  `?\p{N}+`: una sequenza di cifre, con spazio opzionale.
4. **Punteggiatura**  `?[^\s\p{L}\p{N}]+`: una sequenza di simboli che non sono spazi, lettere o cifre (per esempio *!!* o *?!*), con spazio opzionale.
5. **Spazi** `\s+(?!\S)|\s+`: una sequenza di spazi bianchi che non è seguita da un non spazio (lookahead negativo, [scheda 16](L03-elaborazione-del-testo.md#p-16)), altrimenti qualunque sequenza di spazi.

Il lookahead serve a lasciare **l'ultimo spazio** alla parola successiva. Su *Hello   world* (tre spazi) l'output verificato è `['Hello', ' ', ' world']`: `\s+(?!\S)` prende due spazi (fermandosi prima dello spazio seguito da w), il terzo spazio si attacca a *world*. Così *world* ha la stessa forma, `' world'`, con uno o più spazi prima, e BPE vede un solo tipo.

> **Approfondimento: Limiti noti della regex di GPT-2**
>
> (Facoltativo, verificato con la libreria `regex`.) Le contrazioni sono solo minuscole: *She'S* dà `['She', "'", 'S']`. `'t` separa *don't* in `[' don', "'t"]`, non nel *do* + *n't* del Penn Treebank ([scheda 30](L03-elaborazione-del-testo.md#p-30)). Le regex dei tokenizer successivi (GPT-4, GPT-4o) rendono le contrazioni insensibili alle maiuscole e spezzano i numeri in gruppi di al massimo 3 cifre ([L2 scheda 42](L02-parole-e-token.md#p-42)).

<a id="p-20"></a>

### Slide 20 · L'output del pretokenizer

Su *We're 350 dogs! Um, lunch?* l'output è:

`We``'re``·350``·dogs``!``·Um``,``·lunch``?` (· = spazio)

Rieseguito con la libreria `regex`: identico alla slide, sia con l'apostrofo dritto sia con quello tipografico (purché pattern e testo usino lo stesso carattere: con pattern `'` e testo *We’re* l'apostrofo tipografico finisce da solo come punteggiatura).

- *We're* → *We* + *'re*: vince l'alternativa delle contrazioni.
- La punteggiatura si stacca da *dogs* e *lunch*: *!* e *?* sono chunk a sé.
- Alcuni chunk iniziano con uno spazio ( *350*,  *dogs*,  *Um*,  *lunch*), altri no: *We* perché è a inizio testo, *!* e *,* perché attaccati alla parola precedente.

Sono gli stessi effetti visti nel tokenizer di GPT-4o nella [lezione precedente](L02-parole-e-token.md#p-42): parole con lo spazio iniziale incorporato, clitici staccati, punteggiatura separata. Una differenza: GPT-2 tiene `' 350'` con lo spazio e tutte le cifre insieme, mentre GPT-4o lascia lo spazio da solo e divide i numeri lunghi in gruppi di 3 cifre.

Nel notebook: [lo stesso pretokenizer scritto con il modulo `re`](L03-elaborazione-del-testo.md) e l'esercizio 7 della scheda.

<a id="p-21"></a>
**Slide 21 · Pausa** — Pausa di 10 minuti; dopo la pausa: contare le parole con Unix, tokenizzazione a regole, distanza di edit.

## Strumenti Unix

<a id="p-22"></a>
**Slide 22 · Strumenti Unix semplici** — Tokenizzazione e conteggio delle parole in una sola riga di comando, con tr, sort e uniq.

<a id="p-23"></a>

### Slide 23 · Una parola per riga: tr -sc

```
tr -sc 'A-Za-z' '\n' < sh.txt
```

`tr` (*translate*) sostituisce caratteri con altri caratteri. `'A-Za-z'` è l'insieme delle lettere; l'opzione `-c` ne prende il **complemento**, quindi seleziona ogni carattere non alfabetico e lo cambia in un a capo `'\n'`. L'opzione `-s` (*squeeze*) comprime una serie di sostituzioni consecutive in una sola: una sequenza di spazi, virgole e punti produce un solo a capo, non righe vuote.

Risultato: **una parola per riga**. L'output sui sonetti di Shakespeare (`sh.txt`) comincia con THE, SONNETS, by, William, Shakespeare, From, fairest, creatures... È una tokenizzazione ingenua: una «parola» è una sequenza massimale di lettere ASCII, cioè l'analogo di `re.findall(r"[A-Za-z]+", testo)`.

Conseguenze da saper dire (verificate su un testo di prova): *cat's* diventa due righe, *cat* e *s*; *state-of-the-art* diventa quattro parole; i numeri spariscono; le lettere accentate (*perché*) spezzano la parola perché non sono in `A-Za-z`. Se il file inizia con un carattere non alfabetico, la prima riga è vuota.

<a id="p-24"></a>

### Slide 24 · Contare: sort | uniq -c

```
tr -sc 'A-Za-z' '\n' < sh.txt | sort | uniq -c
```

`uniq -c` collassa le righe identiche **adiacenti** e antepone il numero di ripetizioni. Adiacenti è la parola chiave: per contare tutte le occorrenze di una parola bisogna prima **ordinare** con `sort`, che mette vicine le righe uguali. Senza `sort`, *the ... the* in punti diversi del testo darebbe due righe con conteggio 1.

Output mostrato: 1945 A, 72 AARON, 19 ABBESS, 25 Aaron, 6 Abate, 1 Abates... Maiuscole e minuscole sono ancora **parole diverse**: A, AARON e Aaron sono contati separatamente (AARON in maiuscolo è il nome del personaggio nelle battute delle opere).

L'ordine della lista è quello per **byte** (locale C): tutte le maiuscole vengono prima delle minuscole, per questo ABBESS (B = 66) precede Aaron (a = 97). Con un locale linguistico (per esempio `en_US.UTF-8`) `sort` ordinerebbe in modo diverso e mescolerebbe maiuscole e minuscole; per risultati riproducibili si usa `LC_ALL=C sort`.

<a id="p-25"></a>

### Slide 25 · Unire maiuscole e minuscole: tr A-Z a-z

```
tr -sc 'A-Za-z' '\n' < sh.txt | tr A-Z a-z | sort | uniq -c
```

Un secondo `tr` mappa ogni maiuscola nella minuscola corrispondente **prima** dell'ordinamento: è il **case folding** ([scheda 33](L03-elaborazione-del-testo.md#p-33)). Output: 14725 a, 97 aaron, 1 abaissiez, 10 abandon, 2 abandoned, 2 abase, 1 abash, 14 abate...

Coerenza dei numeri: **aaron = 97 = 72 AARON + 25 Aaron** (quindi nel testo non compare *aaron* tutto minuscolo). Per *a*: 14725 = 1945 *A* + 12780 occorrenze di *a* minuscolo (il 12780 si ricava per differenza, la slide non lo mostra). Similmente *abate* 14 comprende i 6 *Abate* del passo precedente più 8 occorrenze scritte in altro modo (abate, ABATE).

Il numero di tipi diminuisce (le forme che differiscono solo per le maiuscole si fondono) e i conteggi crescono: è una scelta di **normalizzazione**, che perde distinzioni come *US* e *us*. Collegamento con [L2 scheda 8](L02-parole-e-token.md#p-8): tipi e istanze dipendono dalle convenzioni.

<a id="p-26"></a>

### Slide 26 · Le parole più frequenti: sort -n -r

```
tr -sc 'A-Za-z' '\n' < sh.txt | tr A-Z a-z | sort | uniq -c | sort -n -r
```

L'ultimo `sort` ordina le righe in modo **numerico** (`-n`: 100 dopo 99, non prima come nell'ordine alfabetico) e **inverso** (`-r`: dal più grande). Risultato, le parole più frequenti di Shakespeare:

| Conteggio | Parola |
| --- | --- |
| 27378 | the |
| 26084 | and |
| 22538 | i |
| 19771 | to |
| 17481 | of |
| 14725 | a |
| 13826 | you |

In cima ci sono, come in ogni corpus, le **parole funzionali** brevi: articoli, pronomi, preposizioni, congiunzioni ([L2 scheda 12](L02-parole-e-token.md#p-12): sono un insieme chiuso che si esaurisce presto). Il valore di *a*, 14725, è coerente con la scheda precedente.

Pipeline utile per statistiche veloci su un corpus inglese. Per qualunque cosa più complessa (clitici, numeri, lingue con accenti o senza spazi) si passa agli algoritmi di tokenizzazione veri, come BPE.

Nel notebook: [la stessa pipeline in Python](L03-elaborazione-del-testo.md) su un corpus di docstring.

> **Da saper fare: Scrivere e leggere la pipeline**
>
> Saper dire cosa fa ogni stadio e cosa succede togliendolo: senza il primo `sort` `uniq -c` conta solo le ripetizioni consecutive; senza `-s` compaiono righe vuote contate come «parola» vuota; senza `-n` l'ordinamento è alfabetico sui numeri (1000 prima di 99). Varianti: `head -20` in coda per le prime 20; `wc -l` dopo `uniq` per il numero di tipi $|V|$, dopo il primo `tr` per il numero di istanze $N$. Esercizio svolto nella sezione Studio.

## Tokenizzazione a regole

<a id="p-27"></a>
**Slide 27 · Tokenizzazione a regole** — Quando i token devono essere parole, e dove finiscono le frasi.

<a id="p-28"></a>

### Slide 28 · Quando i token devono essere parole

BPE è il modo standard di tokenizzare per i modelli linguistici, ma ci sono casi in cui i token devono essere **parole** e non subword:

- **Parsing**: un parser per l'inglese vuole in ingresso parole grammaticali ([L1 scheda 43](L01-introduzione-al-corso.md#p-43)), non pezzi come *\_new* + *er*.
- **Studio linguistico**: applicazioni con una definizione a priori del token da studiare; scienze sociali, dove le parole ortografiche sono l'oggetto di studio (contare quante volte compare una parola in un corpus di giornali).

**Il metodo**: si definisce prima uno **standard** (che cos'è un token in ogni caso difficile), poi lo si implementa con **regole**: algoritmi deterministici basati su espressioni regolari compilate in **automi a stati finiti** efficienti. La tokenizzazione gira prima di ogni altra elaborazione, su tutto il testo, quindi deve essere molto veloce.

**Nomi**: trattare espressioni multiparola come *New York* o *rock 'n' roll* come un solo token richiede un **dizionario**; per questo la tokenizzazione a regole è strettamente legata al **riconoscimento di entità** (NER, [L1 scheda 47](L01-introduzione-al-corso.md#p-47)).

**Normalizzazione**: le pipeline a regole spesso normalizzano anche le forme: **case folding** (*Fed* e *fed*), **lemmatizzazione** (*am, are, is* → *be*), **stemming** (taglio degli affissi). Dettagli nelle schede 33-34.

<a id="p-29"></a>

### Slide 29 · Desiderata per l'inglese

Uno standard deve decidere che cos'è un token in ciascuno di questi casi (i tre riquadri della slide):

- **Punteggiatura**: staccare virgole e punti come token separati, perché le virgole sono utili ai parser e i punti segnalano i confini di frase. Ma tenere la punteggiatura **interna** alle parole: *m.p.h.*, *Ph.D.*, *AT&T*, *cap'n*.
- **Numeri e simboli**: prezzi (`$45.55`) e date (*01/02/06*) restano interi; il prezzo non va spezzato in 45 e 55. In inglese le virgole compaiono dentro i numeri ogni tre cifre (*555,500.50*), mentre spagnolo, francese e tedesco usano la virgola decimale e lo spazio (o il punto) per le migliaia: *555 500,50*. Anche URL, hashtag (*#nlproc*) e indirizzi email vanno tenuti interi.
- **Clitici**: espandere le contrazioni segnate da apostrofo, *we're* → *we are*, *what're* → *what are*. Un **clitico** non può stare da solo e compare solo attaccato a un'altra parola ([L2 scheda 16](L02-parole-e-token.md#p-16)); succede anche in francese con i pronomi (*j'ai*) e gli articoli (*l'homme*), e in italiano (*l'acqua*, *c'è*).

La tokenizzazione **dipende dalla lingua**: la stessa regola su virgole e punti nei numeri è giusta per l'inglese e sbagliata per l'italiano. È la stessa idea delle convenzioni di [L1 scheda 40](L01-introduzione-al-corso.md#p-40) (*New York-based*).

<a id="p-30"></a>

### Slide 30 · Lo standard Penn Treebank

La **tokenizzazione Penn Treebank** è lo standard dei corpora annotati sintatticamente (*treebank*) distribuiti dal Linguistic Data Consortium (LDC). Esempio della slide (il simbolo ␣ separa i token):

```
Input:  "The San Francisco-based restaurant," they said,
        "doesn't charge $10".
Output: " The San Francisco-based restaurant , " they said ,
        " does n't charge $ 10 " .
```

- **Clitici** separati: *doesn't* → *does* + *n't*. Il taglio è prima di *n't*, non all'apostrofo: così *does* resta un verbo intero e *n't* è la negazione.
- **Trattini**: le parole con trattino restano unite (*San Francisco-based* dà *San* e *Francisco-based*).
- **Punteggiatura**: tutta separata, virgolette e simbolo del dollaro compresi: `$ 10` sono due token.

Verifica con `nltk.tokenize.TreebankWordTokenizer` sulla frase della slide: stessi token; in più NLTK scrive le virgolette di apertura come ``` `` ``` e di chiusura come `''`, la convenzione originale del Treebank per distinguerle. Altri casi: *can't* → *ca* + *n't*; *they'll* → *they* + *'ll*; *kids'* → *kids* + *'*.

<a id="p-31"></a>

### Slide 31 · Un tokenizer a espressioni regolari (NLTK)

Codice della slide (libro Fig. 2.16, da Bird et al. 2009):

```
text = 'That U.S.A. poster-print costs $12.40...'
pattern = r'''(?x)       # set flag to allow verbose regexps
    (?:[A-Z]\.)+          # abbreviations, e.g. U.S.A.
  | \w+(?:-\w+)*          # words with optional internal hyphens
  | \$?\d+(?:\.\d+)?%?    # currency, percentages, e.g. $12.40, 82%
  | \.\.\.                # ellipsis
  | [][.,;"'?():_`-]      # these are separate tokens; includes ], [
'''
nltk.regexp_tokenize(text, pattern)
['That', 'U.S.A.', 'poster-print', 'costs', '$12.40', '...']
```

`(?x)` è il flag **verbose**: spazi e commenti nel pattern vengono ignorati, così la regex si può scrivere su più righe commentate. `nltk.regexp_tokenize` restituisce tutte le corrispondenze da sinistra a destra (come `re.findall`; i gruppi sono tutti non catturanti apposta, altrimenti `findall` restituirebbe i gruppi). Le alternative sono provate **in ordine**: abbreviazioni, parole con trattini interni, valute e percentuali, puntini di sospensione, singoli segni di punteggiatura (la classe `[][...]` comincia con `]` subito dopo `[`, dove è letterale). I caratteri che non corrispondono a nessuna alternativa (spazi, `&`, `/`, `!`) vengono scartati. Output rieseguito con NLTK 3.10: identico alla slide.

La slide aggiunge che le ambiguità si risolvono con l'ordine delle regole e le classi: l'apostrofo è genitivo in *the book's cover*, virgolette in *'The other class', she said*, clitico in *they're*. Il libro dice che algoritmi deterministici *progettati con cura* possono farlo; questo pattern non lo fa: su quella frase stacca l'apostrofo sempre allo stesso modo (*book*, *'*, *s*; *they*, *'*, *re*).

Nel notebook: [il pattern eseguito](L03-elaborazione-del-testo.md) e [un Penn Treebank semplificato](L03-elaborazione-del-testo.md).

> **Attenzione (errore nelle slide): Il pattern non produce «82%» come dice il commento**
>
> Il commento della terza alternativa promette *82%* come token, ma l'alternativa `\w+(?:-\w+)*` viene prima e corrisponde già a *82* (le cifre sono in `\w`); il segno `%` non è in nessuna alternativa e viene scartato. Verifica: `nltk.regexp_tokenize('82% of it', pattern)` dà `['82', 'of', 'it']`. Per lo stesso motivo *12.40* senza dollaro diventa `['12', '.', '40']`: la valuta funziona solo perché `$` non è in `\w`. Correzione: mettere l'alternativa numerica **prima** di quella delle parole (allora *82%* e *12.40* restano interi, verificato; effetto collaterale: *3rd* diventa *3* + *rd*). Il difetto è già nella figura del libro e nel libro NLTK; la regola generale della slide, «l'ordine delle alternative conta», è proprio ciò che lo spiega.

> **Da saper fare: Eseguire il tokenizer a mano**
>
> In ogni posizione: prova le alternative nell'ordine; la prima che corrisponde vince (anche se una successiva darebbe un token più lungo); consuma il testo trovato; se nessuna corrisponde, salta un carattere. Esempio verificato: *Ph.D. students at AT&T* → `['Ph', '.', 'D.', 'students', 'at', 'AT', 'T']`: *Ph* non è un'abbreviazione nel senso di `(?:[A-Z]\.)+` perché h è minuscola, e `&` viene perso.

<a id="p-32"></a>

### Slide 32 · Segmentazione in frasi

La **segmentazione in frasi** è un passo opzionale dell'elaborazione del testo, importante per i compiti che cercano **struttura**, come il parsing (che lavora frase per frase).

- **Indizi**: la punteggiatura, cioè punti, punti interrogativi, punti esclamativi. *?* e *!* sono indicatori relativamente non ambigui di fine frase: bastano regole semplici.
- **Il punto** è ambiguo: può segnare un'abbreviazione (*Dr.*) o un confine di frase; il punto di *Inc.* a fine frase è **entrambe le cose insieme**. Per questo tokenizzazione in parole e in frasi si affrontano **insieme**: decidere se il punto fa parte della parola è una decisione di tokenizzazione.
- **In pratica**: prima si decide se un punto appartiene alla parola, con un dizionario di abbreviazioni costruito a mano o appreso dai dati (Kiss e Strunk 2006, il metodo del *Punkt* tokenizer di NLTK). Nel toolkit **Stanford CoreNLP** la segmentazione è una conseguenza deterministica della tokenizzazione: una frase finisce a un `.`, `!` o `?` che **non è già stato raggruppato** con altri caratteri in un token (un'abbreviazione o un numero come *12.40*), eventualmente seguito da virgolette o parentesi di chiusura.

Esempio: *Mr. Smith paid \$12.40 to Acme Inc. He left.* Il punto di *Mr.* e quello di *12.40* sono dentro token; quello di *Inc.* è dentro il token ma la frase finisce lì comunque (serve un'euristica in più: la parola seguente ha la maiuscola); l'ultimo punto è isolato e chiude la frase.

Nel notebook: [due regole di segmentazione a confronto](L03-elaborazione-del-testo.md) (esercizio 9 della scheda).

<a id="p-33"></a>

### Slide 33 · Normalizzazione delle parole

La **normalizzazione** mette parole o token in un formato standard: *U.S.A.* o *USA*, *uh-huh* o *uhhuh*, *am/is/are* o *be*. Tre tecniche, dalla più semplice:

- **Case folding**: tutto in minuscolo (il `tr A-Z a-z` della [scheda 25](L03-elaborazione-del-testo.md#p-25)). Aiuta il **recupero dell'informazione** e il riconoscimento del parlato, dove gli utenti scrivono o dicono le cose in minuscolo. Ma perde distinzioni: *US* e *us*, *Fed* e *fed*, *SAIL* e *sail*. Quindi danneggia analisi del sentiment, traduzione automatica ed estrazione di informazione, dove le maiuscole sono un indizio utile (per un nome proprio, o per il tono: *GREAT*).
- **Lemmatizzazione**: ricondurre una parola al suo **lemma**, la forma di dizionario: *am, are, is* → *be*; *car, cars, car's, cars'* → *car*; in italiano *voglio, vuoi* → *volere*. *He is reading detective stories* → *He be read detective story*. Si fa con il **parsing morfologico**: separare radici e affissi ([L2 schede 15-16](L02-parole-e-token.md#p-15)) con un dizionario e regole. Serve a gestire le forme irregolari (*am* → *be*) che nessuna regola di suffisso tratta.
- **Stemming**: versione grezza della lemmatizzazione: taglia gli affissi finali con regole di riscrittura, **senza dizionario**. Il classico è lo **stemmer di Porter** (1980), semplice e veloce, ancora comune nel recupero dell'informazione.

Tutte e tre riducono il numero di tipi $|V|$ fondendo forme diverse: utile quando i dati sono pochi o quando si cerca per significato, dannoso quando la differenza fra le forme conta. I modelli neurali con BPE di solito non normalizzano: le varianti restano distinte e il modello impara da solo le somiglianze.

<a id="p-34"></a>

### Slide 34 · Lo stemmer di Porter

La slide mostra un paragrafo di *L'isola del tesoro* e il suo output dopo lo stemmer (a sinistra l'originale, a destra gli stem):

| Testo | Output |
| --- | --- |
| This was not the map we found in Billy Bones's chest, but an accurate copy, | Thi wa not the map we found in Billi Bone s chest but an accur copi |
| complete in all things-names and heights and soundings-with the single exception of | complet in all thing name and height and sound with the singl except of |
| the red crosses and the written notes. | the red cross and the written note |

Verifica: tokenizzando con `[A-Za-z]+` e applicando `PorterStemmer` di NLTK (modalità di default) l'output coincide parola per parola con la slide. In modalità `ORIGINAL_ALGORITHM` l'unica differenza è la *s* isolata di *Bones's*, che l'algoritmo originale riduce alla stringa vuota. Gli stem **non sono parole** (*accur*, *copi*, *singl*); conta solo che parole con la stessa radice ricevano lo stesso stem.

**Regole di riscrittura** applicate in serie, a cascata come ELIZA: `ATIONAL → ATE` (*relational* → *relate*); `ING → ε` se lo stem contiene una vocale (*motoring* → *motor*, mentre *sing* resta *sing*); `SSES → SS` (*grasses* → *grass*). Nota: la regola ATIONAL → ATE produce *relate*, ma un passo successivo toglie la e finale e l'output completo è *relat*.

**Errori**: **over-stemming** (fonde parole diverse: *organization* → *organ*, verificato) e **under-stemming** (non fonde parole collegate: *European* → *european* ma *Europe* → *europ*, restano separate, verificato). Abbastanza buono per la ricerca, non per l'analisi linguistica.

> **Attenzione (errore nelle slide): «doing → doe» e «policy → polic» non sono output di Porter**
>
> Porter dà ***doing* → *do*** e ***policy* → *polici***. Verifica con NLTK in tutte e tre le modalità (inclusa `ORIGINAL_ALGORITHM`, fedele all'articolo del 1980) e a mano: per *doing* il passo 1b toglie *ing* perché *do* contiene una vocale, e non aggiunge la e perché *do* ha misura $m = 0$; per *policy* il passo 1c trasforma la y finale in i (lo stem contiene una vocale) e nessun passo successivo ha una regola per *-ici*. La lista classica (Krovetz 1993, riportata nelle edizioni precedenti del libro) elenca **coppie** di parole diverse che uno stemmer fonde per errore: *organization/organ*, *doing/doe*, *policy/police*, non output. Versione corretta: «over-stemming: *organization* e *organ* ricevono lo stesso stem *organ*». Con NLTK la coppia *policy/police* non viene nemmeno fusa (*polici* contro *polic*).

> **Da saper fare: Applicare le regole citate**
>
> All'orale si chiede tipicamente di applicare una regola e dire perché la condizione conta: `ING → ε` solo se lo stem contiene una vocale, altrimenti *sing* → *s*. Esempi verificati con NLTK: *caresses* → *caress*, *ponies* → *poni*, *hopping* → *hop*, *running* → *run*, *happiness* → *happi*, *national* → *nation*, *university*, *universe*, *universal* → tutte *univers* (over-stemming), *computer*, *computation*, *computing* → *comput*.

## Distanza di edit minima

<a id="p-35"></a>
**Slide 35 · Distanza di edit minima** — Quanto sono simili due stringhe? Distanza di edit, allineamento e programmazione dinamica.

<a id="p-36"></a>

### Slide 36 · Distanza di edit

La **distanza di edit minima** fra due stringhe è il **numero minimo di operazioni di editing** (inserimento, cancellazione, sostituzione) necessarie per trasformare una stringa nell'altra.

Esempio: *intention* → *execution*, distanza **5**. Le cinque operazioni: cancellare i, sostituire n con e, sostituire t con x, inserire c, sostituire n con u (nell'inglese della slide «substitute e for n» significa «metti e al posto di n»).

**A cosa serve**: confrontare una parola scritta male con le correzioni candidate; confrontare le parole prodotte da un riconoscitore del parlato o da un traduttore automatico con una sequenza di riferimento. Qui è definita su parole (i simboli sono lettere), ma l'algoritmo vale per qualunque sequenza, anche di parole intere.

**Levenshtein** (1966): il peso più semplice, ogni operazione costa 1 e sostituire una lettera con se stessa costa 0; *intention* → *execution* vale 5. **Versione alternativa**: inserimenti e cancellazioni costano 1 e le sostituzioni non sono permesse; equivale a sostituzioni di costo 2, perché ogni sostituzione si può simulare con una cancellazione più un inserimento. Con questi costi la distanza diventa **8**: le stesse cinque operazioni costano 1 + 2 + 2 + 1 + 2 = 8. Entrambi i valori sono verificati con la programmazione dinamica (schede 45-49).

> **Da saper fare: Distanza come metrica**
>
> Con costi simmetrici (inserimento = cancellazione) la distanza è una **metrica**: $d(x,y) \ge 0$, $d(x,y)=0$ solo se $x=y$, $d(x,y)=d(y,x)$ (un inserimento letto al contrario è una cancellazione), disuguaglianza triangolare. Limiti utili per controllare un conto: $|n-m| \le d \le \max(n,m)$ con costi 1; con sostituzione a 2, $d \le n+m$ (cancellare tutto e reinserire tutto).

<a id="p-37"></a>

### Slide 37 · Allineamento

```
I N T E * N T I O N
| | | | | | | | | |
* E X E C U T I O N
d s s   i s
```

Un **allineamento** è una corrispondenza fra sottostringhe delle due sequenze: I è allineata con la stringa vuota (*\**), N con E, T con X, E con E, la stringa vuota con C, e così via. È la visualizzazione più utile di una distanza fra stringhe.

Sotto, in rosso, la **lista delle operazioni** che trasforma la stringa in alto in quella in basso: **d** cancellazione (I contro \*), **s** sostituzione (N→E, T→X, N→U), **i** inserimento (\* contro C). Le colonne senza lettera sono corrispondenze esatte (E=E, T, I, O, N): costo 0.

Costo dell'allineamento: con Levenshtein a costi 1, $1 + 3 + 1 = 5$; con sostituzione a 2, $1 + 3\cdot 2 + 1 = 8$. Regola di lettura: un asterisco in alto è un inserimento, un asterisco in basso è una cancellazione, due lettere diverse sono una sostituzione. La distanza è il costo minimo su **tutti** gli allineamenti possibili, e in generale ci sono più allineamenti ottimi (scheda 51).

<a id="p-38"></a>

### Slide 38 · La distanza di edit come problema di ricerca

La figura mostra *intention* alla radice e tre archi, uno per tipo di operazione, verso tre stringhe figlie: **del** → *ntention* (cancellata la i iniziale), **ins** → *intecntion* (inserita una c dopo *inte*), **subst** → *inxention* (t sostituita da x).

Trovare la distanza è cercare il **cammino più breve** da una stringa all'altra, un'operazione per passo. Lo spazio di tutte le sequenze di operazioni è enorme (ogni stringa ha decine di figli, e la profondità cresce con la lunghezza), quindi una ricerca ingenua è impraticabile. Però **molti cammini diversi arrivano alla stessa stringa**: cancellare prima la i e poi sostituire la t, o viceversa, porta allo stesso punto.

Idea: ricordare il cammino più breve verso ogni stringa la prima volta che la si raggiunge, invece di ricalcolarlo. È la **programmazione dinamica** (Bellman 1957): un metodo basato su una **tabella** che combina le soluzioni di sottoproblemi. Nel NLP la stessa idea regge l'algoritmo di Viterbi e il parsing CKY.

<a id="p-39"></a>

### Slide 39 · Il cammino da intention a execution

La figura mostra un cammino ottimo, dall'alto in basso: *intention* → (cancella i) *ntention* → (sostituisci n con e) *etention* → (sostituisci t con x) *exention* → (inserisci u) *exenution* → (sostituisci n con c) *execution*. Costo con sostituzioni a 2: $1+2+2+1+2 = 8$. La stringa *exention* è evidenziata.

Nota: questo cammino inserisce u e sostituisce n con c, mentre l'allineamento della [scheda 37](L03-elaborazione-del-testo.md#p-37) inserisce c e sostituisce n con u. Non è una contraddizione: sono due allineamenti ottimi diversi, con lo stesso costo 8 (e anche 5 con costi 1). Entrambi risultano fra quelli ricostruiti con il backtrace.

**Il principio di ottimalità**: se *exention* sta sul cammino ottimo da *intention* a *execution*, allora anche il pezzo da *intention* a *exention* deve essere ottimo. Altrimenti, sostituendo quel pezzo con uno più corto, si otterrebbe un cammino complessivo più corto, e quello di partenza non sarebbe ottimo: contraddizione.

Quindi la distanza verso una stringa si costruisce dalle distanze verso i suoi **prefissi**: questi sono i **sottoproblemi**. Nella tabella della programmazione dinamica ogni cella è la distanza fra un prefisso della sorgente e un prefisso della destinazione.

<a id="p-40"></a>

### Slide 40 · La ricorrenza

$D[i,j]$ è la distanza di edit fra i primi $i$ caratteri della sorgente $X$ (lunghezza $n$) e i primi $j$ caratteri della destinazione $Y$ (lunghezza $m$). La risposta è $D[n,m]$.

**Casi base**: $D[i,0] = i$ (da $i$ caratteri alla stringa vuota servono $i$ cancellazioni); $D[0,j] = j$ (dalla stringa vuota a $j$ caratteri servono $j$ inserimenti).

**Ricorrenza** (Levenshtein con inserimento e cancellazione 1, sostituzione 2):

$$D[i,j] = \min \begin{cases} D[i-1,j] + 1 \\ D[i,j-1] + 1 \\ D[i-1,j-1] + \begin{cases} 2 & \text{se } X[i] \ne Y[j] \\ 0 & \text{se } X[i] = Y[j] \end{cases} \end{cases}$$

È il minimo sui tre modi di arrivare nella cella $(i,j)$:

- **dall'alto**, $(i-1,j)$: si è già trasformato $X[1..i-1]$ in $Y[1..j]$ e si **cancella** $X[i]$;
- **da sinistra**, $(i,j-1)$: si è già ottenuto $Y[1..j-1]$ da $X[1..i]$ e si **inserisce** $Y[j]$;
- **dalla diagonale**, $(i-1,j-1)$: si allinea $X[i]$ con $Y[j]$, con una **sostituzione** (costo 2) o una **corrispondenza** (costo 0).

La forma generale ha costi arbitrari: $D[i-1,j] + \text{del-cost}(X[i])$, $D[i,j-1] + \text{ins-cost}(Y[j])$, $D[i-1,j-1] + \text{sub-cost}(X[i],Y[j])$. Con sostituzione a 1 si ottiene la distanza di Levenshtein classica.

<a id="p-41"></a>

### Slide 41 · L'algoritmo MIN-EDIT-DISTANCE

Pseudocodice della slide (libro Fig. 2.21):

```
function MIN-EDIT-DISTANCE(source, target) returns min-distance
  n <- LENGTH(source)
  m <- LENGTH(target)
  Create a distance matrix D[n+1, m+1]
  # Initialization: the zeroth row and column is the distance from the empty string
  D[0,0] = 0
  for each row i from 1 to n do
      D[i,0] <- D[i-1,0] + del-cost(source[i])
  for each column j from 1 to m do
      D[0,j] <- D[0,j-1] + ins-cost(target[j])
  # Recurrence relation:
  for each row i from 1 to n do
      for each column j from 1 to m do
          D[i,j] <- MIN( D[i-1,j]   + del-cost(source[i]),
                         D[i-1,j-1] + sub-cost(source[i], target[j]),
                         D[i,j-1]   + ins-cost(target[j]) )
  # Termination
  return D[n,m]
```

L'algoritmo ha preso il nome da Wagner e Fischer (1974), ma è stato scoperto indipendentemente da molti. È **programmazione dinamica bottom-up**: una tabella $D$ con $n+1$ righe e $m+1$ colonne (la riga e la colonna 0 rappresentano la stringa vuota), in cui ogni cella è calcolata da celle già riempite.

**Complessità**: $(n+1)(m+1)$ celle, ognuna in tempo costante, quindi tempo e memoria $O(nm)$. Per *intention*/*execution* sono 100 celle, contro un numero di sequenze di edit che cresce in modo esponenziale. Se serve solo la distanza (non l'allineamento) basta tenere due righe alla volta: memoria $O(m)$.

> **Approfondimento: L'algoritmo in Python**
>
> (Facoltativo.) Implementazione usata per verificare tutte le tabelle di queste schede:
>
> ```
> def edit_distance(s, t, sub=2, ins=1, dele=1):
>     n, m = len(s), len(t)
>     D = [[0]*(m+1) for _ in range(n+1)]
>     for i in range(1, n+1): D[i][0] = D[i-1][0] + dele
>     for j in range(1, m+1): D[0][j] = D[0][j-1] + ins
>     for i in range(1, n+1):
>         for j in range(1, m+1):
>             c = 0 if s[i-1] == t[j-1] else sub
>             D[i][j] = min(D[i-1][j] + dele,
>                           D[i-1][j-1] + c,
>                           D[i][j-1] + ins)
>     return D[n][m]
>
> edit_distance("intention", "execution")        # 8
> edit_distance("intention", "execution", sub=1) # 5
> ```
>
> Attenzione agli indici: nello pseudocodice le stringhe partono da 1, in Python da 0, quindi $X[i]$ è `s[i-1]`.

<a id="p-42"></a>

### Slide 42 · Inizializzazione: riga 0 e colonna 0

Il riquadro evidenzia la parte di **inizializzazione**: $D[0,0] = 0$, poi la prima colonna $D[i,0] = D[i-1,0] + \text{del-cost}(X[i])$ e la prima riga $D[0,j] = D[0,j-1] + \text{ins-cost}(Y[j])$.

Sono le distanze dalla stringa vuota: nella prima colonna $i$ cancellazioni, nella prima riga $j$ inserimenti. Con costi unitari $D[i,0] = i$ e $D[0,j] = j$; con costi specifici per lettera la prima colonna è la somma cumulata dei costi di cancellazione delle lettere della sorgente.

<a id="p-43"></a>

### Slide 43 · Ricorrenza: righe, poi colonne

Il riquadro evidenzia il doppio ciclo: per ogni riga $i$ da 1 a $n$, per ogni colonna $j$ da 1 a $m$, la cella è il minimo fra la cella **sopra** più il costo di cancellazione, la cella in **diagonale** più il costo di sostituzione (0 se le lettere coincidono) e la cella a **sinistra** più il costo di inserimento.

Perché l'ordine funziona: procedendo riga per riga, da sinistra a destra, le tre celle da cui dipende $(i,j)$, cioè $(i-1,j)$, $(i-1,j-1)$ e $(i,j-1)$, sono già state riempite. Andrebbe bene anche colonna per colonna, o per antidiagonali: basta rispettare le dipendenze.

<a id="p-44"></a>

### Slide 44 · Terminazione e costi

Il riquadro evidenzia l'ultima riga: si restituisce $D[n,m]$, la distanza fra le stringhe complete.

I costi possono essere **fissi** (per esempio ogni inserimento costa 1) oppure **specifici per lettera**, per rappresentare il fatto che alcune lettere vengono inserite (o confuse) più spesso di altre; sostituire una lettera con se stessa costa sempre 0. Esempio: in un correttore ortografico, sostituire a con s (vicine sulla tastiera) può costare meno che sostituire a con p (scheda 52). Con costi specifici l'algoritmo non cambia: cambiano solo i numeri sommati nelle tre alternative.

<a id="p-45"></a>

### Slide 45 · Riempire la tabella: intention → execution

Tabella completa della slide (libro Fig. 2.20): righe = sorgente *intention*, colonne = destinazione *execution*, # = stringa vuota, inserimenti e cancellazioni 1, sostituzioni 2. $D[i,j]$ è la distanza fra i prefissi.

| src\tar | # | e | x | e | c | u | t | i | o | n |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| # | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| i | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 6 | 7 | 8 |
| n | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 7 | 8 | 7 |
| t | 3 | 4 | 5 | 6 | 7 | 8 | 7 | 8 | 9 | 8 |
| e | 4 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 9 |
| n | 5 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 10 |
| t | 6 | 5 | 6 | 7 | 8 | 9 | 8 | 9 | 10 | 11 |
| i | 7 | 6 | 7 | 8 | 9 | 10 | 9 | 8 | 9 | 10 |
| o | 8 | 7 | 8 | 9 | 10 | 11 | 10 | 9 | 8 | 9 |
| n | 9 | 8 | 9 | 10 | 11 | 12 | 11 | 10 | 9 | 8 |

**Verifica**: ho ricalcolato la tabella con la programmazione dinamica e l'ho confrontata cella per cella con l'immagine della slide: tutte le 100 celle coincidono.

Come leggerla: $D[4,3] = 5$ è la distanza fra *inte* ed *exe*; la riga di *e* ha 3 nella colonna di *e* ($D[4,1]$, *inte* contro *e*: tre cancellazioni) perché le due e si allineano gratis. Si nota anche la «diagonale bassa» in fondo a destra: dopo *...t* i suffissi *tion* coincidono e i valori restano 8 lungo la diagonale.

> **Da saper fare: Riempire una tabella DP a mano**
>
> 1. Scrivi la sorgente sulle righe e la destinazione sulle colonne, con # in testa a entrambe.
> 2. Prima riga $0,1,2,\dots,m$; prima colonna $0,1,\dots,n$.
> 3. Per ogni cella: sopra + 1, sinistra + 1, diagonale + (0 se le lettere di riga e colonna coincidono, altrimenti 2 oppure 1 secondo i costi richiesti). Scrivi il minimo e, se serve l'allineamento, le frecce di tutte le alternative che raggiungono il minimo.
> 4. Controlli: celle adiacenti in orizzontale o verticale differiscono al massimo di 1 (con costi unitari di ins/del); lungo una diagonale di corrispondenze il valore non cambia.
>
> Esercizi con tabelle complete nella sezione Studio (leda/deal, drive/brief, drive/divers).

<a id="p-46"></a>

### Slide 46 · Inizializzazione: D[i,0] = i, D[0,j] = j

La slide evidenzia la riga 0 (0, 1, ..., 9) e la colonna 0 (0, 1, ..., 9) della tabella. Dalla stringa vuota ai primi $j$ caratteri di *execution* servono $j$ inserimenti; dai primi $i$ caratteri di *intention* alla stringa vuota servono $i$ cancellazioni. Per esempio $D[0,4] = 4$: per scrivere *exec* da zero servono quattro inserimenti.

<a id="p-47"></a>

### Slide 47 · D[1,1] = 2: i contro e

Prima cella interna, *i* contro *e*:

- dall'alto: $D[0,1] + 1 = 1 + 1 = 2$ (cancellazione di i);
- da sinistra: $D[1,0] + 1 = 1 + 1 = 2$ (inserimento di e);
- dalla diagonale: $D[0,0] + 2 = 2$ (sostituzione, perché $i \ne e$).

Il minimo è 2, raggiunto **in tre modi**: la cella avrà tre frecce ↖ ← ↑ nella tabella dei backpointer ([scheda 50](L03-elaborazione-del-testo.md#p-50)). Con sostituzione a costo 1 la stessa cella varrebbe 1, solo dalla diagonale.

<a id="p-48"></a>

### Slide 48 · D[4,1] = 3: e contro e, una corrispondenza

Cella riga *e* (quarta lettera di *intention*), colonna *e* (prima lettera di *execution*). La diagonale non costa nulla quando le lettere coincidono:

- dalla diagonale: $D[3,0] + 0 = 3$;
- dall'alto: $D[3,1] + 1 = 4 + 1 = 5$;
- da sinistra: $D[4,0] + 1 = 4 + 1 = 5$.

Il minimo è 3, solo dalla diagonale. Significato: per trasformare *inte* in *e* conviene cancellare *i*, *n*, *t* (costo 3) e tenere la *e*. Numeri verificati con la tabella ricalcolata.

<a id="p-49"></a>

### Slide 49 · D[9,9] = 8: la distanza minima

L'ultima cella contiene la risposta: $D[9,9] = 8$. Coincide con le cinque operazioni contate a mano nella [scheda 36](L03-elaborazione-del-testo.md#p-36): una cancellazione, un inserimento e tre sostituzioni a costo 2, $1 + 1 + 3\cdot 2 = 8$.

Con Levenshtein a costi tutti 1 la stessa procedura dà $D[9,9] = 5$ (verificato): le tre sostituzioni costano 1 invece di 2. Nella versione a costo 2 una sostituzione vale quanto una cancellazione più un inserimento, quindi l'algoritmo è indifferente fra le due scelte: è per questo che gli allineamenti ottimi sono molti di più (scheda 51).

<a id="p-50"></a>

### Slide 50 · Backtrace: i backpointer

Per ottenere l'**allineamento** e non solo la distanza, mentre si riempie la tabella si memorizza in ogni cella una freccia (**backpointer**) verso la cella da cui si è arrivati: **↑** dall'alto per una cancellazione, **←** da sinistra per un inserimento, **↖** dalla diagonale per una sostituzione o una corrispondenza. In caso di parità si tengono **più frecce**. Tabella della slide (libro Fig. 2.22, grafica da Gusfield 1997), in grassetto le celle del cammino evidenziato:

| src\tar | # | e | x | e | c | u | t | i | o | n |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| # | **0** | ← 1 | ← 2 | ← 3 | ← 4 | ← 5 | ← 6 | ← 7 | ← 8 | ← 9 |
| i | **↑ 1** | ↖←↑ 2 | ↖←↑ 3 | ↖←↑ 4 | ↖←↑ 5 | ↖←↑ 6 | ↖←↑ 7 | ↖ 6 | ← 7 | ← 8 |
| n | ↑ 2 | **↖←↑ 3** | ↖←↑ 4 | ↖←↑ 5 | ↖←↑ 6 | ↖←↑ 7 | ↖←↑ 8 | ↑ 7 | ↖←↑ 8 | ↖ 7 |
| t | ↑ 3 | ↖←↑ 4 | **↖←↑ 5** | ↖←↑ 6 | ↖←↑ 7 | ↖←↑ 8 | ↖ 7 | ←↑ 8 | ↖←↑ 9 | ↑ 8 |
| e | ↑ 4 | ↖ 3 | ← 4 | **↖← 5** | **← 6** | ← 7 | ←↑ 8 | ↖←↑ 9 | ↖←↑ 10 | ↑ 9 |
| n | ↑ 5 | ↑ 4 | ↖←↑ 5 | ↖←↑ 6 | ↖←↑ 7 | **↖←↑ 8** | ↖←↑ 9 | ↖←↑ 10 | ↖←↑ 11 | ↖↑ 10 |
| t | ↑ 6 | ↑ 5 | ↖←↑ 6 | ↖←↑ 7 | ↖←↑ 8 | ↖←↑ 9 | **↖ 8** | ← 9 | ← 10 | ←↑ 11 |
| i | ↑ 7 | ↑ 6 | ↖←↑ 7 | ↖←↑ 8 | ↖←↑ 9 | ↖←↑ 10 | ↑ 9 | **↖ 8** | ← 9 | ← 10 |
| o | ↑ 8 | ↑ 7 | ↖←↑ 8 | ↖←↑ 9 | ↖←↑ 10 | ↖←↑ 11 | ↑ 10 | ↑ 9 | **↖ 8** | ← 9 |
| n | ↑ 9 | ↑ 8 | ↖←↑ 9 | ↖←↑ 10 | ↖←↑ 11 | ↖←↑ 12 | ↑ 11 | ↑ 10 | ↑ 9 | **↖ 8** |

Verifica: ho ricalcolato i backpointer (tutte le alternative che raggiungono il minimo) e li ho confrontati con l'immagine: coincidono in tutte le 99 celle. Le celle con tre frecce sono quelle in cui cancellare, inserire o sostituire costa lo stesso, tipiche della zona in alto a destra dove nessuna lettera coincide.

<a id="p-51"></a>

### Slide 51 · Backtrace: dalla distanza all'allineamento

Il **backtrace** parte dall'8 nell'angolo in basso a destra e segue le frecce fino alla cella in alto a sinistra. **Ogni cammino completo** è un allineamento di costo minimo; le celle in grassetto ne mostrano uno:

1. $(9,9) \to (8,8)$ ↖: n = n; poi $(7,7)$ e $(6,6)$ ↖: o = o, i = i; poi $(5,5)$ ↖: t = t (valori sempre 8, corrispondenze gratuite).
2. $(5,5) \to (4,4)$ ↖: n contro u, sostituzione ($8 = 6 + 2$).
3. $(4,4) \to (4,3)$ ←: inserimento di c ($6 = 5 + 1$).
4. $(4,3) \to (3,2)$ ↖: e = e ($5 = 5 + 0$).
5. $(3,2) \to (2,1)$ ↖: t contro x, sostituzione ($5 = 3 + 2$).
6. $(2,1) \to (1,0)$ ↖: n contro e, sostituzione ($3 = 1 + 2$).
7. $(1,0) \to (0,0)$ ↑: cancellazione di i ($1 = 0 + 1$).

Letto dal basso verso l'alto è esattamente l'allineamento della [scheda 37](L03-elaborazione-del-testo.md#p-37): d, s, s, =, i, s, =, =, =, =. **Due celle in grassetto nella stessa riga** ($D[4,3]$ e $D[4,4]$) indicano un inserimento; **due nella stessa colonna** ($D[0,0]$ e $D[1,0]$) una cancellazione; un passo diagonale è una sostituzione o una corrispondenza.

Quanti allineamenti ottimi? Contando tutti i cammini delle frecce: **134** con sostituzione a 2 (molti scambiano una sostituzione con una coppia cancellazione + inserimento, stesso costo), **7** con Levenshtein a costi 1. Fra i 134 c'è anche quello della [scheda 39](L03-elaborazione-del-testo.md#p-39) (n → c, poi inserimento di u).

Nel notebook: [backtrace ed enumerazione di tutti gli allineamenti ottimi](L03-elaborazione-del-testo.md).

> **Da saper fare: Backtrace a mano**
>
> (1) Parti da $(n,m)$. (2) Scegli una freccia della cella: ↖ allinea $X[i]$ con $Y[j]$ (= se uguali, s se diversi), ↑ allinea $X[i]$ con \* (d), ← allinea \* con $Y[j]$ (i). (3) Ripeti fino a $(0,0)$. (4) Rovescia la lista. Controllo: la somma dei costi delle operazioni deve dare $D[n,m]$. Se nella tabella non hai segnato le frecce, puoi ricostruirle all'indietro: da $(i,j)$ vai in una cella vicina il cui valore più il costo del passo dà esattamente $D[i,j]$.

<a id="p-52"></a>

### Slide 52 · Dove si usa la distanza di edit

- **Correzione ortografica**: ordinare le correzioni candidate di una parola sbagliata per distanza. I pesi possono riflettere la tastiera: le sostituzioni fra tasti vicini sono più probabili, quindi costano meno.
- **Riconoscimento del parlato**: il **word error rate** (WER) si calcola da un allineamento di edit distance minima fra le parole prodotte dal riconoscitore e la trascrizione di riferimento. Qui i simboli sono parole intere: $\text{WER} = \frac{S + D + I}{N}$, con $S$, $D$, $I$ sostituzioni, cancellazioni e inserimenti dell'allineamento a costi 1 e $N$ numero di parole del riferimento. Esempio verificato: riferimento *the cat sat on the mat*, ipotesi *the cat sit on mat*: una sostituzione (sat/sit) e una cancellazione (the), WER = 2/6 ≈ 0,33. Collegamento con la valutazione in [L1 scheda 70](L01-introduzione-al-corso.md#p-70).
- **Traduzione automatica**: allineare le frasi di un **corpus parallelo** (lo stesso testo in due lingue).
- **Viterbi**: un'estensione probabilistica della distanza di edit minima: invece della distanza minima calcola l'allineamento di **probabilità massima** fra una stringa e un'altra. Stessa tabella, stessa ricorrenza, con probabilità moltiplicate (o log-probabilità sommate) e massimo al posto del minimo.

> **Da saper fare: WER oltre il 100%**
>
> Il WER non è limitato a 1: il denominatore è la lunghezza del riferimento, mentre gli inserimenti possono essere quanti si vuole. Riferimento di 2 parole, ipotesi di 5 parole tutte sbagliate: almeno 2 sostituzioni + 3 inserimenti, WER = 5/2 = 250%.

<a id="p-53"></a>

### Slide 53 · Riepilogo e prossima lezione

**Riepilogo**:

- espressioni regolari: parentesi quadre, contatori, ancore, gruppi, sostituzioni;
- una sola regex pretokenizza il testo per BPE;
- `tr`, `sort` e `uniq` contano le parole in una riga di comando;
- tokenizzazione a regole: uno standard (Penn Treebank), un tokenizer a regex, i confini di frase;
- distanza di edit minima: allineamento, programmazione dinamica, backtrace.

**Prossima lezione**: **modelli linguistici n-gram** (capitolo 3): probabilità delle sequenze di parole e come si valuta un modello linguistico. Riprende la predizione della parola successiva della [lezione 1](L01-introduzione-al-corso.md#p-3) e la perplessità ([L1 scheda 70](L01-introduzione-al-corso.md#p-70)); i conteggi di parole di questa lezione (e le scelte di tokenizzazione e normalizzazione) sono la materia prima degli n-gram.

## Notebook

Commento al notebook del corso `HLT-L03-text-processing.ipynb` (il notebook è del docente e non è incluso).

Notebook di accompagnamento della lezione (Python, solo libreria standard; le celle facoltative usano il modulo `regex`, la rete o una shell Unix). Due funzioni di servizio, `show` (evidenzia tutte le corrispondenze) e `check` (prova un pattern su stringhe da accettare e da rifiutare), accompagnano tutta la parte sulle regex: esempi delle figure 2.8-2.16 del libro, i **primi tentativi sbagliati** da correggere per gli esercizi 2 e 3 della scheda, sostituzioni e gruppi, ELIZA, il pretokenizer di GPT-2 riscritto con `re`, il conteggio delle parole alla Unix su un corpus di docstring di Python, il tokenizer NLTK, un Penn Treebank semplificato, la segmentazione in frasi e infine distanza di edit, backtrace ed enumerazione di tutti gli allineamenti ottimi, con le tabelle degli esercizi 10-12.

L'ho rieseguito da capo (Python 3.11, nbconvert): tutti gli output coincidono con quelli salvati, conteggi delle docstring compresi; la cella facoltativa con `regex` gira qui (stessi chunk di `re` sulle tre frasi), quella con la shell anche (stessi 12 conteggi), quella che scarica Shakespeare no (niente rete). Il notebook non produce figure (solo evidenziazioni HTML, riportate qui fra parentesi quadre). Trovati **un bug reale** (ELIZA: i pattern `.* X .*` non scattano quando la parola chiave è a inizio frase, perché lo spazio viene aggiunto solo in fondo), **un bug minore** (il corpus delle docstring contiene doppioni ereditati e importati) e **un'affermazione imprecisa** (le classi di `re` non sono esattamente `\p{L}` e `\p{N}`), ciascuno con correzione verificata. Numeri di cella: posizione nel file `.ipynb` contando da 0 anche le celle di testo (non il contatore `In [n]`). I pattern delle celle 21-23, 25-27 e 38 sono sbagliati apposta (esercizi), non bug.

### Notebook 1 · Il tester: show e check

```python
def show(pattern, *texts, flags=0):          # evidenzia ogni match di re.finditer
    for t in texts:
        display(Matches(pattern, t, flags))

def check(pattern, accept=(), reject=(), how="fullmatch", flags=0):
    find = {"fullmatch": re.fullmatch, "search": re.search}[how]
    ...   # per ogni stringa: ok / WRONG, poi "k of n correct"

show(r"Buttercup", "I'm called little Buttercup")
check(r"colou?r", accept=["color", "colour"], reject=["colouur", "colr"])
```

Output:

```text
r"Buttercup"   I'm called little [Buttercup]   (1 matches)
r"colou?r"   (fullmatch)
  ok     should match      'color'
  ok     should match      'colour'
  ok     should not match  'colouur'
  ok     should not match  'colr'
  4 of 4 correct: all good
```

Due strumenti per tutto il notebook. `show` usa `re.finditer`: tutte le corrispondenze non sovrapposte, da sinistra a destra, comprese quelle di **lunghezza zero** (ancore, `\b`, lookahead, stelle che accettano il vuoto), che nella versione HTML sono una barretta rossa e in quella testuale `[]`. `check` distingue i due modi di usare un pattern: `re.fullmatch` (tutta la stringa deve corrispondere, come nelle domande «il linguaggio delle stringhe tali che...») e `re.search` (basta un pezzo, come in grep). È la distinzione che la scheda esercizi fissa per ogni domanda: «the whole string must match» contro «a search».

Il primo esempio è quello di [scheda 5](L03-elaborazione-del-testo.md#p-5); `colou?r` è quello di [scheda 8](L03-elaborazione-del-testo.md#p-8). Il conteggio testuale scrive sempre «matches» anche per 1 (solo estetica).

### Notebook 2 · Parentesi quadre e il caret

```python
show(r"[wW]oodchuck", "Woodchuck or woodchuck?")
show(r"[0-9]", "plenty of 7 to 5")
show(r"[A-Z]", "we should call it 'Drenched Blossoms'")
show(r"[^A-Z]", "Oyfn pripetchik")
show(r"[^Ss]", "I have no exquisite reason for't")
show(r"[e^]", "look up ^ now")
show(r"a^b", "look up a^b now")       # in Python a caret outside brackets is always the start-of-line anchor
show(r"a\^b", "look up a^b now")      # so a literal caret must be escaped
```

Output:

```text
r"[wW]oodchuck"   [Woodchuck] or [woodchuck]?   (2 matches)
r"[0-9]"   plenty of [7] to [5]   (2 matches)
r"[A-Z]"   we should call it '[D]renched [B]lossoms'   (2 matches)
r"[^A-Z]"   O[y][f][n][ ][p][r][i][p][e][t][c][h][i][k]   (14 matches)
r"[^Ss]"   [I][ ][h][a][v][e][ ][n][o][ ][e][x][q][u][i]s[i][t][e][ ][r][e][a]s[o][n][ ][f][o][r]['][t]   (30 matches)
r"[e^]"   look up [^] now   (1 matches)
r"a^b"   look up a^b now   (0 matches)
r"a\^b"   look up [a^b] now   (1 matches)
```

Gli esempi delle figure 2.8-2.10 del libro ([scheda 6](L03-elaborazione-del-testo.md#p-6)). Da notare: `[^A-Z]` e `[^Ss]` trovano **un carattere per volta** (14 e 30 corrispondenze), spazi e apostrofi compresi; `[e^]` trova il caret perché non è in prima posizione dentro le quadre.

Le ultime due righe riproducono il riquadro di correzione della [scheda 6](L03-elaborazione-del-testo.md#p-6): in Python `a^b` non trova mai *a^b* (il caret fuori dalle quadre è sempre un'ancora), serve `a\^b`. Il notebook lo dice esplicitamente nel testo della cella 3: conferma quanto già scritto nella scheda.

### Notebook 3 · Ripetizione, contatori e jolly

```python
SHEEP = ["baa!", "baaa!", "baaaaaa!"]
NOT_SHEEP = ["ba!", "b!", "baa", "baab!"]
check(r"ba*!",  SHEEP, NOT_SHEEP)     # wrong: the star allows zero a
check(r"baa*!", SHEEP, NOT_SHEEP)
check(r"baa+!", SHEEP, NOT_SHEEP)

show(r"beg.n", "begin, beg'n, begun, began, beg\nn")
show(r"[0-9]+", "Room 101 costs $1250 a night")
show(r"\d{3}", "Room 101 costs $1250 a night")
show(r"[ab]*", "aaaa ababab bbbb")
```

Output:

```text
r"ba*!"   (fullmatch)
  ok     should match      'baa!'
  ok     should match      'baaa!'
  ok     should match      'baaaaaa!'
  WRONG  should not match  'ba!'
  WRONG  should not match  'b!'
  ok     should not match  'baa'
  ok     should not match  'baab!'
  5 of 7 correct
...
r"baa+!"   (fullmatch)  7 of 7 correct: all good

r"beg.n"   [begin], [beg'n], [begun], [began], beg
n   (4 matches)
r"[0-9]+"   Room [101] costs $[1250] a night   (2 matches)
r"\d{3}"   Room [101] costs $[125]0 a night   (2 matches)
r"[ab]*"   [aaaa][] [ababab][] [bbbb][]   (6 matches)
```

Il linguaggio delle pecore ([scheda 7](L03-elaborazione-del-testo.md#p-7)): `ba*!` accetta anche *ba!* e *b!*; `baa*!`, nella versione del notebook, sbaglia ancora *ba!*, perché ha una sola a obbligatoria. La versione giusta con la stella è `baaa*!` (quella della slide), oppure `baa+!`.

La seconda cella mostra il jolly (`beg.n` non attraversa il newline), `[0-9]+` contro `\d{3}` (su *1250* il contatore esatto prende *125* e lascia lo 0) e `[ab]*`, che produce anche **corrispondenze vuote**: dopo *aaaa*, nella posizione dello spazio, la stella accetta zero caratteri ([scheda 8](L03-elaborazione-del-testo.md#p-8), riquadro della [scheda 7](L03-elaborazione-del-testo.md#p-7)).

### Notebook 4 · Esercizio 1 della scheda: leggere pattern

```python
for s in ["color", "colour", "colouur"]:
    print(f"colou?r  {s!r:10}", "match" if re.fullmatch(r"colou?r", s) else "no match")
for s in ["ba!", "baa!", "baaaa!", "baaa"]:
    print(f"baa+!    {s!r:10}", "match" if re.fullmatch(r"baa+!", s) else "no match")
show(r"\b[tT]he\b", "The other cat sat there, then the dog left.")
```

Output:

```text
colou?r  'color'    match
colou?r  'colour'   match
colou?r  'colouur'  no match
baa+!    'ba!'      no match
baa+!    'baa!'     match
baa+!    'baaaa!'   match
baa+!    'baaa'     no match
r"\b[tT]he\b"   [The] other cat sat there, then [the] dog left.   (2 matches)
```

Controllo diretto dell'esercizio 1: `colou?r` accetta *color* e *colour*, non *colouur* (il `?` ammette al massimo una u); `baa+!` rifiuta *ba!* (servono almeno due a) e *baaa* (manca il punto esclamativo); `\b[tT]he\b` trova solo *The* e *the*, non *other*, *there*, *then*, perché in ciascuno manca un confine di parola a uno dei due lati. Soluzione completa nella sezione Studio.

### Notebook 5 · Ancore, confini di parola, alias ed escape

```python
show(r"^The", "The dog saw The Cat.")
check(r"^The dog\.$", accept=["The dog."], reject=["The dog!", "The dogo", "The dog. Yes."])
check(r"^The dog.$",  accept=["The dog."], reject=["The dog!", "The dogo", "The dog. Yes."])   # the period is a wildcard
show(r"\b99\b", "There are 99 bottles", "It costs $99", "There are 299 bottles")
show(r"\b", "the cat")

show(r"\d+", "Party of 5, table 12")
show(r"\w+", "l'opéra, café_2 and naïve")
show(r"\s+", "tabs\tand   spaces\nand newlines")
show(r"\.", "K.A.P.L.A.N")
show(r"\?", "Would you light my candle?")
```

Output:

```text
r"^The"   [The] dog saw The Cat.   (1 matches)
r"^The dog\.$"   (fullmatch)
  4 of 4 correct: all good
r"^The dog.$"   (fullmatch)
  ok     should match      'The dog.'
  WRONG  should not match  'The dog!'
  WRONG  should not match  'The dogo'
  ok     should not match  'The dog. Yes.'
  2 of 4 correct
r"\b99\b"   There are [99] bottles   (1 matches)
r"\b99\b"   It costs $[99]   (1 matches)
r"\b99\b"   There are 299 bottles   (0 matches)
r"\b"   []the[] []cat[]   (4 matches)
r"\d+"   Party of [5], table [12]   (2 matches)
r"\w+"   [l]'[opéra], [café_2] [and] [naïve]   (5 matches)
r"\s+"   tabs[	]and[   ]spaces[
]and[ ]newlines   (4 matches)
r"\."   K[.]A[.]P[.]L[.]A[.]N   (5 matches)
r"\?"   Would you light my candle[?]   (1 matches)
```

Riproduce la [scheda 9](L03-elaborazione-del-testo.md#p-9) e la [scheda 13](L03-elaborazione-del-testo.md#p-13): senza backslash il punto di `^The dog.$` è un jolly e accetta *The dog!* e *The dogo*; `\b99\b` trova 99 dopo il dollaro (che non è un carattere di parola) ma non in 299; `\b` da solo su *the cat* dà 4 corrispondenze vuote, una per ogni confine.

Due precisazioni. (1) Il testo dice che `^` e `$` ancorano all'inizio e alla fine della *riga*: in Python senza il flag `re.M` ancorano all'inizio e alla fine della **stringa** (con `re.M` di ogni riga). Negli esempi, tutti di una riga, non cambia nulla. (2) `\w+` su *l'opéra, café\_2 and naïve* tiene insieme le lettere accentate e l'underscore: in Python 3 `\w` è Unicode (riquadro della [scheda 13](L03-elaborazione-del-testo.md#p-13)), a differenza di `[A-Za-z]` e di `tr`.

### Notebook 6 · Disgiunzione, precedenza, greedy

```python
show(r"cat|dog", "raining cats and dogs")
show(r"gupp(y|ies)", "one guppy, two guppies")
show(r"guppy|ies", "one guppy, two guppies")
show(r"Column [0-9]+ *", "Column 1 Column 2 Column 3")
show(r"(Column [0-9]+ *)*", "Column 1 Column 2 Column 3")

show(r"[a-z]*", "once upon a time")
show(r"<.*>", "<a> x <b>")
show(r"<.*?>", "<a> x <b>")
```

Output:

```text
r"cat|dog"   raining [cat]s and [dog]s   (2 matches)
r"gupp(y|ies)"   one [guppy], two [guppies]   (2 matches)
r"guppy|ies"   one [guppy], two gupp[ies]   (2 matches)
r"Column [0-9]+ *"   [Column 1 ][Column 2 ][Column 3]   (3 matches)
r"(Column [0-9]+ *)*"   [Column 1 Column 2 Column 3][]   (2 matches)
r"[a-z]*"   [once][] [upon][] [a][] [time][]   (8 matches)
r"<.*>"   [<a> x <b>]   (1 matches)
r"<.*?>"   [<a>] x [<b>]   (2 matches)
```

Gli esempi delle [schede 10](L03-elaborazione-del-testo.md#p-10) e [11](L03-elaborazione-del-testo.md#p-11). `guppy|ies` trova *guppy* e poi solo *ies* dentro *guppies*: la sequenza lega più forte della pipe. Con `Column [0-9]+ *` ogni *Column n* è una corrispondenza separata; con le parentesi e la stella tutta la riga è una sola corrispondenza (seguita da una corrispondenza vuota in fondo).

Il notebook scrive `(Column [0-9]+ *)*`, la slide e il libro `(Column [0-9]+ +)*`: non è un errore, sono due varianti. Con `+` ogni colonna deve essere seguita da almeno uno spazio, quindi sulla stessa riga la corrispondenza si ferma a *Column 1 Column 2*  e l'ultima colonna resta fuori (verificato). Greedy contro lazy: `<.*>` prende tutto da *<a>* a *<b>*, `<.*?>` i due tag separati (esercizio 6c della scheda).

### Notebook 7 · Trovare l'articolo the: falsi positivi e falsi negativi

```python
TEXT = "The other one there, the blithe one. Then the end: the"
show(r"the", TEXT)                                          # misses The: false negative
show(r"[tT]he", TEXT)                                       # other, there, blithe, Then: false positives
show(r"\b[tT]he\b", TEXT)                                   # a word boundary on both sides
show(r"[^a-zA-Z][tT]he[^a-zA-Z]", TEXT)                     # without \b: misses The at the start and the at the end
show(r"(^|[^a-zA-Z])[tT]he([^a-zA-Z]|$)", TEXT)             # the book's final version
```

Output:

```text
r"the"   The o[the]r one [the]re, [the] bli[the] one. Then [the] end: [the]   (6 matches)
r"[tT]he"   [The] o[the]r one [the]re, [the] bli[the] one. [The]n [the] end: [the]   (8 matches)
r"\b[tT]he\b"   [The] other one there, [the] blithe one. Then [the] end: [the]   (4 matches)
r"[^a-zA-Z][tT]he[^a-zA-Z]"   The other one there,[ the ]blithe one. Then[ the ]end: the   (2 matches)
r"(^|[^a-zA-Z])[tT]he([^a-zA-Z]|$)"   [The ]other one there,[ the ]blithe one. Then[ the ]end:[ the]   (4 matches)
```

La sequenza di raffinamenti del libro ([scheda 12](L03-elaborazione-del-testo.md#p-12)) su una frase costruita apposta, con 4 articoli: *The*, *the*, *the*, *the* finale. `the`: 6 corrispondenze, 3 giuste (perde *The*, prende *other*, *there*, *blithe*), $P = 3/6$, $R = 3/4$. `[tT]he`: 8 corrispondenze, 4 giuste, $P = 1/2$, $R = 1$. `\b[tT]he\b`: 4 su 4, $P = R = 1$.

La versione senza `\b`, `[^a-zA-Z][tT]he[^a-zA-Z]`, perde il *The* iniziale e il *the* finale perché chiede un carattere prima e dopo; la versione finale del libro, `(^|[^a-zA-Z])[tT]he([^a-zA-Z]|$)`, li recupera con le ancore, ma le sue corrispondenze includono lo spazio o la punteggiatura intorno (*[The ]*, *[ the ]*): per estrarre solo la parola si usa il gruppo o `\b`.

### Notebook 8 · Esercizi 2 e 3 della scheda: correggere i primi tentativi

```python
check(r"^[a-z]+$",   accept=["hello", "Hello", "HLT", "b"], ...)        # 2a
check(r"^[a-z]+b$",  accept=["b", "bob", "climb", "ab"], ...)          # 2b
check(r"^(b|bab)*$", accept=["b", "bab", "bbabb", "babab", "bbb"], ...) # 2c
check(r"(\w+) \1", how="search", reject=[..., "in the theatre", "this is"])       # 3a
check(r"^\d+.*[A-Za-z]+$", how="search", reject=[..., "42nd street", ...])        # 3b
check(r"grotto.*raven", how="search", accept=["the raven flew into the grotto", ...])  # 3c
```

Output:

```text
r"^[a-z]+$"        5 of 7   WRONG: 'Hello', 'HLT'
r"^[a-z]+b$"       7 of 8   WRONG: 'b'
r"^(b|bab)*$"      9 of 10  WRONG: 'babab'
r"(\w+) \1"        5 of 7   WRONG: 'in the theatre', 'this is'
r"^\d+.*[A-Za-z]+$" 6 of 7  WRONG: '42nd street'
r"grotto.*raven"   3 of 6   WRONG: 'the raven flew into the grotto', 'grottos and ravens', 'grottoraven'

# con le correzioni (mia esecuzione):
r"[A-Za-z]+"  r"[a-z]*b"  r"(b+(ab+)*)?"  r"\b([A-Za-z]+)\s+\1\b"
r"^\d+\b.*\b[A-Za-z]+$"  r"\bgrotto\b.*\braven\b|\braven\b.*\bgrotto\b"   -> all good
```

Qui i pattern sono **volutamente sbagliati**: lo studente deve capire perché e correggerli. Le cause: (2a) manca la classe maiuscola; (2b) `[a-z]+` vuole almeno una lettera prima della b finale, quindi rifiuta *b*: serve `[a-z]*b`; (2c) i blocchi *bab* non possono condividere la b centrale, quindi *babab* (= bab + ab) resta fuori: la forma giusta è `(b+(ab+)*)?`; (3a) senza `\b` il gruppo cattura pezzi di parola: *is is* dentro *this is*, *the the* dentro *the theatre*; (3b) `\d+` seguito da `.*` accetta *42nd*: serve `\b` dopo l'intero; (3c) l'ordine delle due parole non è fisso e mancano i confini (*grottos*, *grottoraven*).

Ho verificato che le correzioni passano tutti i test del notebook e, per 2c, che coincidono con la definizione su tutte le stringhe di a e b fino a lunghezza 10. Soluzioni ragionate negli esercizi 2 e 3 della sezione Studio.

### Notebook 9 · Esercizi 5 e 6 della scheda

```python
SENT = "The theory of the other them: the end."
show(r"[tT]he", SENT)
show(r"\b[tT]he\b", SENT)
show(r"\bthe\b", SENT)

show(r"the*", "thethe theee")
show(r"gupp(y|ies)", "guppies")
show(r"guppy|ies", "guppies")
show(r"<.*>", "<a> x <b>")
show(r"<.*?>", "<a> x <b>")
```

Output:

```text
r"[tT]he"   [The] [the]ory of [the] o[the]r [the]m: [the] end.   (6 matches)
r"\b[tT]he\b"   [The] theory of [the] other them: [the] end.   (3 matches)
r"\bthe\b"   The theory of [the] other them: [the] end.   (2 matches)
r"the*"   [the][the] [theee]   (3 matches)
r"gupp(y|ies)"   [guppies]   (1 matches)
r"guppy|ies"   gupp[ies]   (1 matches)
r"<.*>"   [<a> x <b>]   (1 matches)
r"<.*?>"   [<a>] x [<b>]   (2 matches)
```

Esercizio 5: `[tT]he` trova 6 stringhe, di cui 3 falsi positivi (*theory*, *other*, *them*): $P = 3/6$, $R = 3/3$. `\b[tT]he\b` li elimina ($P = R = 1$); `\bthe\b` non ha falsi positivi ma perde *The* iniziale, un falso negativo che abbassa il recall a $2/3$.

Esercizio 6: la prima corrispondenza di `the*` è *the* (la stella si applica solo alla e, [scheda 10](L03-elaborazione-del-testo.md#p-10)), poi *the* e *theee*; `gupp(y|ies)` trova tutta la parola, `guppy|ies` solo *ies*; greedy e lazy come nel blocco precedente.

### Notebook 10 · Sostituzioni, gruppi di cattura, lookahead (esercizio 4)

```python
print(re.sub(r"cherry", r"apricot", "I like cherry pie and cherry tart"))
print(re.sub(r"janet", r"Janet", "janet and janet's cat"))
print(re.sub(r"(\d{2})/(\d{2})/(\d{4})", r"\2-\1-\3", "The date is 10/15/2011"))
show(r"\b([A-Za-z]+)\s+\1\b", "Paris in the the spring, and and so on")

dates = " ".join(f"{d:02d}/01/2026" for d in range(1, 21))
m = re.search(r"(?:\d\d/\d\d/\d{4}\s+){14}(\d\d/\d\d/\d{4})", dates)
print(m.group(1))

for line in ["The cat sleeps", "Cats sleep", "tomorrow, maybe", "Maybe tomorrow"]:
    m = re.search(r"^(?![tT])(\w+)\b", line)
    print(f"{line!r:20}", m.group(1) if m else None)

print(re.sub(r"(\d{2})/(\d{2})/(\d{4})", r"\2-\1-\3", "Due 03/09/2026 and 12/25/2025"))
print(re.sub(r"(\d)", r"<\1>", "the 35 boxes weigh 120 kg"))      # first attempt for (b): fix it
```

Output:

```text
I like apricot pie and apricot tart
Janet and Janet's cat
The date is 15-10-2011
r"\b([A-Za-z]+)\s+\1\b"   Paris in [the the] spring, [and and] so on   (2 matches)
15/01/2026
'The cat sleeps'     None
'Cats sleep'         Cats
'tomorrow, maybe'    None
'Maybe tomorrow'     Maybe
Due 09-03-2026 and 25-12-2025
the <3><5> boxes weigh <1><2><0> kg
```

Gli esempi delle [schede 14-16](L03-elaborazione-del-testo.md#p-14): sostituzione semplice, date americane in europee con tre gruppi, parole ripetute con la backreference `\1`, il gruppo non catturante che salta 14 date e cattura la quindicesima, il lookahead negativo `^(?![tT])(\w+)\b` (prima parola della riga se non comincia per t). In più un lookahead positivo: `\d+(?=kg)` prende 5 e 7 ma non 12, e il *kg* non entra nella corrispondenza.

Esercizio 4a: sulle date della scheda il pattern scambia i primi due campi, *Due 09-03-2026 and 25-12-2025*. Il primo tentativo per 4b è volutamente sbagliato: `(\d)` prende una cifra per volta e dà *<3><5>*; con `(\d+)` (greedy) si ottiene *the <35> boxes weigh <120> kg* (verificato).

### Notebook 11 · ELIZA, una cascata di sostituzioni

```python
POINT_OF_VIEW = [(r"\bMY\b", "YOUR"), (r"\bI['’]M\b", "YOU ARE"),
                 (r"\bME\b", "YOU"), (r"\bMYSELF\b", "YOURSELF")]
RESPONSES = [(r".* YOU ARE (DEPRESSED|SAD) .*", r"I AM SORRY TO HEAR YOU ARE \1"),
             (r".* ALWAYS .*", r"CAN YOU THINK OF A SPECIFIC EXAMPLE")]

def eliza(utterance, verbose=False):
    s = utterance.upper()
    for pattern, repl in POINT_OF_VIEW:
        s = re.sub(pattern, repl, s)
    s = re.sub(r"^(WELL|OH|SO),?\s+", "", s)          # drop an initial interjection
    s = re.sub(r"[.!?]+$", "", s).strip()               # and the final punctuation
    for pattern, repl in RESPONSES:
        if re.match(pattern, s + " "):                  # a space at the end, so that ' .*' can match at the end
            return re.sub(pattern, repl, s + " ").strip()
    return s

# cella 42: due regole in più
RESPONSES.append((r"^YOU ARE (.*)", r"HOW LONG HAVE YOU BEEN \1"))
RESPONSES.append((r".* YOUR (MOTHER|FATHER) .*", r"TELL ME MORE ABOUT YOUR FAMILY"))
```

Output:

```text
User:  They're always bugging us about something or other.
   after the first set: THEY'RE ALWAYS BUGGING US ABOUT SOMETHING OR OTHER
ELIZA: CAN YOU THINK OF A SPECIFIC EXAMPLE
User:  Well, my boyfriend made me come here.
   after the first set: YOUR BOYFRIEND MADE YOU COME HERE
ELIZA: YOUR BOYFRIEND MADE YOU COME HERE
User:  He says I'm depressed much of the time.
   after the first set: HE SAYS YOU ARE DEPRESSED MUCH OF THE TIME
ELIZA: I AM SORRY TO HEAR YOU ARE DEPRESSED

I'm tired of this course.                        -> HOW LONG HAVE YOU BEEN TIRED OF THIS COURSE
I think my mother likes regular expressions.     -> TELL ME MORE ABOUT YOUR FAMILY
The weather is nice.                             -> THE WEATHER IS NICE
```

Implementazione giocattolo della [scheda 17](L03-elaborazione-del-testo.md#p-17): primo stadio (ribaltamento dei pronomi, dopo il maiuscolo), pulizia di interiezione iniziale e punteggiatura finale, secondo stadio (la prima regola che corrisponde trasforma tutto l'input in risposta, altrimenti eco). Le tre risposte del dialogo del libro escono identiche. L'ordine degli stadi conta: la regola *YOU ARE (DEPRESSED|SAD)* può scattare solo perché *I'M* è già diventato *YOU ARE*. La cella 42 è il punto di partenza dell'esercizio 2.6 del libro.

L'eco quando nessuna regola scatta (*THE WEATHER IS NICE*) e la mancata inversione di *YOU* in *I* sono semplificazioni dichiarate, non bug.

> **Attenzione (errore nelle slide): Bug: le regole .* X .* non scattano se la parola chiave è a inizio frase**
>
> I pattern del libro chiedono uno spazio **prima** della parola chiave (`.* YOU ARE`, `.* ALWAYS`, `.* YOUR`). Il codice aggiunge uno spazio solo in fondo (`s + " "`, per far funzionare  `.*` finale), non all'inizio. Quindi quando la parola chiave apre la frase la regola non scatta mai. Verificato eseguendo la funzione del notebook:
>
> - *I'm sad.* → `YOU ARE SAD` (eco) invece di `I AM SORRY TO HEAR YOU ARE SAD`; con le regole della cella 42 diventa `HOW LONG HAVE YOU BEEN SAD`, perché risponde la regola sbagliata;
> - *Always the same.* → `ALWAYS THE SAME` invece di `CAN YOU THINK OF A SPECIFIC EXAMPLE`;
> - *My mother hates me.* → `YOUR MOTHER HATES YOU`: la regola della famiglia della cella 42 non scatta.
>
> Correzione (verificata sugli stessi input e sui tre del dialogo, che restano identici): usare i confini di parola invece degli spazi e `fullmatch` senza padding.
>
> ```
> RESPONSES = [(r".*\bYOU ARE (DEPRESSED|SAD)\b.*", r"I AM SORRY TO HEAR YOU ARE \1"),
>              (r".*\bALWAYS\b.*", r"CAN YOU THINK OF A SPECIFIC EXAMPLE")]
> ...
>     for pattern, repl in RESPONSES:
>         if re.fullmatch(pattern, s):
>             return re.sub(pattern, repl, s, count=1)
> # cella 42
> RESPONSES.append((r"YOU ARE (.*)", r"HOW LONG HAVE YOU BEEN \1"))
> RESPONSES.append((r".*\bYOUR (MOTHER|FATHER)\b.*", r"TELL ME MORE ABOUT YOUR FAMILY"))
> ```
>
> Risultati: *I'm sad.* → `I AM SORRY TO HEAR YOU ARE SAD`; *Always the same.* → `CAN YOU THINK OF A SPECIFIC EXAMPLE`; *My mother hates me.* → `TELL ME MORE ABOUT YOUR FAMILY`; *I'm tired of this course.* → `HOW LONG HAVE YOU BEEN TIRED OF THIS COURSE`. Aggiungere uno spazio anche in testa (`" " + s + " "`) ripara le regole del libro ma rompe la regola `^YOU ARE` della cella 42 (verificato), per questo conviene `\b`. Il limite è già annunciato nel riquadro della [scheda 17](L03-elaborazione-del-testo.md#p-17).

### Notebook 12 · Il pretokenizer di GPT-2 con re (esercizio 7)

```python
GPT2_RE = r"""'s|'t|'re|'ve|'m|'ll|'d| ?[^\W\d_]+| ?\d+| ?(?:[^\s\w]|_)+|\s+(?!\S)|\s+"""

def pretokenize(text):
    return re.findall(GPT2_RE, text)

print(pretokenize("We're 350 dogs! Um, lunch?"))

print(pretokenize("I'm 42 years old!! Don't ask."))
print(pretokenize("Don’t ask."))      # with a typographic apostrophe the contraction rule does not fire
```

Output:

```text
['We', "'re", ' 350', ' dogs', '!', ' Um', ',', ' lunch', '?']
['I', "'m", ' 42', ' years', ' old', '!!', ' Don', "'t", ' ask', '.']
['Don', '’', 't', ' ask', '.']

# cella 48 (facoltativa, modulo regex), mia esecuzione:
... same as re: True   (tutte e tre le frasi)
```

Il pattern della [scheda 18](L03-elaborazione-del-testo.md#p-18) riscritto per il modulo standard `re`, che non ha `\p{L}` e `\p{N}`: una lettera è `[^\W\d_]` (carattere di parola che non è cifra né underscore), un numero `\d`, la punteggiatura `(?:[^\s\w]|_)`. Su *We're 350 dogs! Um, lunch?* dà esattamente l'output della [scheda 20](L03-elaborazione-del-testo.md#p-20).

Esercizio 7: *I'm 42 years old!! Don't ask.* → `I` `'m` `␣42` `␣years` `␣old` `!!` `␣Don` `'t` `␣ask` `.` (10 chunk). Con l'apostrofo tipografico (*Don’t*) le contrazioni, scritte con l'apostrofo dritto, non scattano: `Don` `’` `t`, come osservato nella [scheda 20](L03-elaborazione-del-testo.md#p-20).

> **Attenzione (errore nelle slide): Imprecisione: le classi di re non sono esattamente \p{L} e \p{N}**
>
> Il testo dice che con `re` «possiamo scrivere le stesse classi». Quasi: in Python `\w` contiene tutti i caratteri alfanumerici, compresi i numeri che non sono cifre decimali (categorie Unicode **No** e **Nl**: ², ³, ½, ¼, numeri romani Ⅻ, ...), mentre `\d` contiene solo le cifre decimali (Nd). Quindi `[^\W\d_]` tratta ² o ½ come **lettere**, mentre `\p{L}` no. Verifica con il modulo `regex`: *E = mc²* dà `␣mc²` con `re` e `␣mc` `²` con il pattern originale; su tutti i caratteri assegnati di Unicode le due versioni divergono esattamente sui 1131 caratteri No e Nl. Sulle frasi del notebook e della scheda il risultato è identico, quindi gli esercizi non cambiano.
>
> Correzione verificata (0 differenze su tutti i caratteri assegnati): togliere i numeri No/Nl dalle lettere e aggiungerli ai numeri.
>
> ```
> import unicodedata
> NUM = "".join(re.escape(chr(c)) for c in range(0x110000)
>               if not 0xD800 <= c <= 0xDFFF and unicodedata.category(chr(c)) in ("Nl", "No"))
> LET, DIG = rf"[^\W\d_{NUM}]", rf"(?:\d|[{NUM}])"
> GPT2_RE = rf"""'s|'t|'re|'ve|'m|'ll|'d| ?{LET}+| ?{DIG}+| ?(?:[^\s\w]|_)+|\s+(?!\S)|\s+"""
> ```
>
> In pratica si usa direttamente il modulo `regex`, come la [scheda 18](L03-elaborazione-del-testo.md#p-18). Differenza residua inevitabile: `re` e `regex` possono avere tabelle Unicode di versioni diverse (i caratteri non assegnati in una versione e assegnati nell'altra).

### Notebook 13 · Contare le parole alla Unix, in Python

```python
def module_text(name):
    """the docstring of a module and of its public functions and classes"""
    mod = importlib.import_module(name)
    parts = [inspect.getdoc(mod) or ""]
    for member, obj in inspect.getmembers(mod):
        if not member.startswith("_") and (inspect.isfunction(obj) or inspect.isclass(obj)):
            parts.append(inspect.getdoc(obj) or "")
    return "\n".join(parts)

def unix_word_counts(text):
    words = re.sub(r"[^A-Za-z]+", "\n", text).split("\n")    # tr -sc 'A-Za-z' '\n'
    words = [w.lower() for w in words if w]                   # tr A-Z a-z
    return Counter(words).most_common()                        # sort | uniq -c | sort -n -r
```

Output:

```text
47998 words, 3710 distinct
  2818 the
  1578 a
  1095 is
  1001 to
   983 of
   749 and
   657 for
   530 in
   530 be
   526 if
   392 object
   387 or
```

La pipeline della [scheda 26](L03-elaborazione-del-testo.md#p-26) tradotta riga per riga: `re.sub` con la classe negata e `+` è `tr -sc` (una sequenza di non lettere diventa un solo a capo), `lower()` è `tr A-Z a-z`, `Counter.most_common()` fa `sort | uniq -c | sort -n -r` senza bisogno di ordinare prima (il contatore non richiede righe adiacenti). Il corpus sono le docstring di 61 moduli della libreria standard: 47.998 parole, 3.710 tipi; in testa le parole funzionali (*the*, *a*, *is*, *to*, *of*) come in Shakespeare, più parole del dominio (*object*, *if*).

La cella facoltativa con la vera shell (eseguita qui) dà gli stessi 12 conteggi: su testo ASCII le due pipeline coincidono. Il messaggio *sort: write failed: Broken pipe* che compare eseguendola è innocuo: `head` chiude la pipe dopo 12 righe. La cella che scarica Shakespeare non gira senza rete; il notebook stesso avverte che i conteggi saranno solo dello stesso ordine di quelli del libro (edizione diversa).

> **Attenzione (errore nelle slide): Bug minore: il corpus contiene docstring ereditate e importate**
>
> La docstring di `module_text` promette «la docstring del modulo e delle sue funzioni e classi pubbliche», ma (1) `inspect.getdoc` su una classe senza docstring propria **eredita** quella della classe madre: per esempio *Common base class for all non-exit exceptions.* entra 26 volte, una per ogni eccezione che non ha una docstring sua; (2) `inspect.getmembers` elenca anche i nomi **importati** da altri moduli, che vengono così contati più volte. Misurato: 59 docstring ereditate e 160 membri importati, circa 6.300 parole su 47.998 (il 13%) sono doppioni.
>
> Correzione verificata: tenere solo ciò che il modulo definisce e solo la docstring propria.
>
> ```
> for member, obj in inspect.getmembers(mod):
>     if (not member.startswith("_") and (inspect.isfunction(obj) or inspect.isclass(obj))
>             and obj.__module__ == mod.__name__):          # solo ciò che il modulo definisce
>         parts.append(inspect.cleandoc(obj.__doc__ or "")) # docstring propria, non ereditata
> ```
>
> Risultato: 41.656 parole e 3.580 tipi; la classifica delle parole funzionali resta la stessa (*the* 2.496, *a* 1.343, *is* 972, ...), mentre *object* scende da 392 a 308 ed esce dalle prime 12. Il messaggio didattico della cella non cambia; cambiano i numeri. È lo stesso difetto di `getdoc` segnalato nel notebook della L4, dove però causava contaminazione fra training e test.

### Notebook 14 · Il tokenizer a regex di NLTK

```python
NLTK_PATTERN = r"""(?x)        # set flag to allow verbose regexps
      (?:[A-Z]\.)+             # abbreviations, e.g. U.S.A.
    | \w+(?:-\w+)*             # words with optional internal hyphens
    | \$?\d+(?:\.\d+)?%?       # currency, percentages, e.g. $12.40, 82%
    | \.\.\.                   # ellipsis
    | [][.,;"'?():_`-]         # these are separate tokens; includes ], [
"""
print(re.findall(NLTK_PATTERN, "That U.S.A. poster-print costs $12.40..."))
print(re.findall(NLTK_PATTERN, "It costs 12.40 euros, 82% of $15."))
```

Output:

```text
['That', 'U.S.A.', 'poster-print', 'costs', '$12.40', '...']
['It', 'costs', '12', '.', '40', 'euros', ',', '82', 'of', '$15', '.']
```

Il pattern della [scheda 31](L03-elaborazione-del-testo.md#p-31) (libro Fig. 2.16) usato con `re.findall`, che per un pattern senza gruppi catturanti restituisce le corrispondenze come `nltk.regexp_tokenize`. La prima frase riproduce l'output della slide. La seconda mostra il difetto già corretto nel riquadro della [scheda 31](L03-elaborazione-del-testo.md#p-31): senza dollaro `\w+` vince sull'alternativa numerica, *12.40* diventa `12` `.` `40` e il *%* di *82%* sparisce. Il notebook lo spiega nello stesso modo e propone la stessa correzione (alternativa numerica prima di quella delle parole): verificata, dà `12.40` e `82%`, con l'effetto collaterale *3rd* → `3` `rd`. Notebook e scheda concordano.

### Notebook 15 · Penn Treebank semplificato (esercizio 8)

```python
def ptb_tokenize(sentence):
    s = sentence
    s = re.sub(r'"', ' " ', s)                               # quotes
    s = re.sub(r"([;:?!()\[\]])", r" \1 ", s)                # punctuation that is always a token
    s = re.sub(r",(?!\d)|(?<!\d),", " , ", s)                # commas, but not inside numbers like 555,500
    s = re.sub(r"\$", " $ ", s)                              # the dollar sign
    s = re.sub(r"\.(?=[\s\"')\]]*$)", " . ", s)              # the final period only
    s = re.sub(r"(?i)n't\b", " n't", s)                      # clitics: n't first
    s = re.sub(r"(?i)'(s|re|ve|ll|d|m)\b", r" '\1", s)       # then 's 're 've 'll 'd 'm
    return s.split()

book = ptb_tokenize('"The San Francisco-based restaurant," they said, "doesn\'t charge $10".')
print(" ".join(book))

tokens = ptb_tokenize('"They don\'t know," she said, "it\'s $12.50 per hour-long lesson."')
print(" ".join(tokens))
print(len(tokens), "tokens")
```

Output:

```text
" The San Francisco-based restaurant , " they said , " does n't charge $ 10 " .
" They do n't know , " she said , " it 's $ 12.50 per hour-long lesson . "
20 tokens
```

Una cascata di sostituzioni, come ELIZA: virgolette, punteggiatura sempre separata, virgole tranne quelle fra cifre (lookahead e lookbehind negativi), dollaro, solo il punto **finale** (eventualmente seguito da virgolette o parentesi), poi i clitici con *n't* prima degli altri. Sulla frase della [scheda 30](L03-elaborazione-del-testo.md#p-30) dà l'output della slide.

Esercizio 8: 20 token. È anche il conteggio di `TreebankWordTokenizer` di NLTK (verificato), che però scrive le virgolette come ``` `` ``` e `''`. Semplificazioni dichiarate, non bug: una frase per riga (un punto interno come in *Ph.D.* non viene toccato, ma nemmeno un punto di fine frase interno), virgolette non distinte fra apertura e chiusura, apostrofi di citazione e genitivi plurali (*kids'*) non separati.

### Notebook 16 · Segmentazione in frasi (esercizio 9)

```python
TEXT9 = "Dr. Rossi arrived at 9 a.m. He works for Acme Inc. The meeting lasted 2.5 hours."
for s in re.split(r"(?<=[.!?])\s+", TEXT9):
    print("|", s)

TITLES = {"Dr.", "Mr.", "Mrs.", "Ms.", "Prof.", "St."}

def segment(text):
    tokens = text.split()
    sentences, current = [], []
    for k, tok in enumerate(tokens):
        current.append(tok)
        nxt = tokens[k + 1] if k + 1 < len(tokens) else None
        if tok[-1] in "!?" or (tok.endswith(".") and tok not in TITLES and (nxt is None or nxt[0].isupper())):
            sentences.append(" ".join(current))
            current = []
    if current:
        sentences.append(" ".join(current))
    return sentences
```

Output:

```text
| Dr.
| Rossi arrived at 9 a.m.
| He works for Acme Inc.
| The meeting lasted 2.5 hours.

| Dr. Rossi arrived at 9 a.m.
| He works for Acme Inc.
| The meeting lasted 2.5 hours.

| She moved to the U.S.
| Army base.
| It was 9 p.m. when she arrived.
```

La regola ingenua «spezza dopo ogni `.!?` seguito da spazio» (lookbehind `(?<=[.!?])`) taglia dopo *Dr.*. La regola migliore della cella 64 decide token per token, come la [scheda 32](L03-elaborazione-del-testo.md#p-32): un token che finisce con il punto chiude la frase se non è un titolo e la parola dopo ha la maiuscola (o se è l'ultimo). Sull'esercizio 9 dà 3 frasi: il punto finale di *a.m.* e quello di *Inc.* sono insieme parte del token e confine; *2.5* non finisce con un punto.

Il secondo testo mostra il limite, dichiarato: *U.S.* seguito da *Army* maiuscolo viene preso per fine frase. Servirebbe sapere che *U.S.* è un'abbreviazione che di solito non chiude la frase: è ciò che il Punkt tokenizer (Kiss e Strunk 2006) impara dai dati. Altro limite non citato: *"Really?" she asked* non viene riconosciuto perché il token finisce con la virgoletta, non con `?`.

### Notebook 17 · Distanza di edit minima: la tabella

```python
def min_edit_distance(source, target, ins_cost=1, del_cost=1, sub_cost=2):
    """The algorithm of Figure 2.21. Returns the whole table D."""
    n, m = len(source), len(target)
    D = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):                    # zeroth column: deletions only
        D[i][0] = D[i - 1][0] + del_cost
    for j in range(1, m + 1):                    # zeroth row: insertions only
        D[0][j] = D[0][j - 1] + ins_cost
    for i in range(1, n + 1):                    # recurrence, row by row
        for j in range(1, m + 1):
            sub = 0 if source[i - 1] == target[j - 1] else sub_cost
            D[i][j] = min(D[i - 1][j] + del_cost,          # from above: delete source[i]
                          D[i - 1][j - 1] + sub,           # from the diagonal: substitute, or match at cost 0
                          D[i][j - 1] + ins_cost)          # from the left: insert target[j]
    return D


D = min_edit_distance("intention", "execution")
```

Output:

```text
       #    e    x    e    c    u    t    i    o    n
  #    0    1    2    3    4    5    6    7    8    9
  i    1    2    3    4    5    6    7    6    7    8
  n    2    3    4    5    6    7    8    7    8    7
  t    3    4    5    6    7    8    7    8    9    8
  e    4    3    4    5    6    7    8    9   10    9
  n    5    4    5    6    7    8    9   10   11   10
  t    6    5    6    7    8    9    8    9   10   11
  i    7    6    7    8    9   10    9    8    9   10
  o    8    7    8    9   10   11   10    9    8    9
  n    9    8    9   10   11   12   11   10    9    8

distance, substitutions at 2: 8
distance, substitutions at 1: 5
```

Traduzione diretta dello pseudocodice della [scheda 41](L03-elaborazione-del-testo.md#p-41) (libro Fig. 2.21), con costi di default 1, 1, 2 (inserimento, cancellazione, sostituzione). Gli indici del libro partono da 1, quelli di Python da 0: per questo si confrontano `source[i - 1]` e `target[j - 1]`. La tabella stampata coincide cella per cella con quella della [scheda 45](L03-elaborazione-del-testo.md#p-45); la distanza è 8 con sostituzione a 2 e 5 con costi 1 ([scheda 36](L03-elaborazione-del-testo.md#p-36), [scheda 49](L03-elaborazione-del-testo.md#p-49)). La funzione accetta anche liste di parole invece di stringhe, perché usa solo `len`, indici e `==`: è ciò che serve per il WER (ultimo blocco).

### Notebook 18 · Backtrace e tutti gli allineamenti ottimi

```python
def backtrace(source, target, ins_cost=1, del_cost=1, sub_cost=2):
    D = min_edit_distance(source, target, ins_cost, del_cost, sub_cost)
    i, j = len(source), len(target)
    while i > 0 or j > 0:
        sub = sub_cost if i > 0 and j > 0 and source[i - 1] != target[j - 1] else 0
        if i > 0 and j > 0 and D[i][j] == D[i - 1][j - 1] + sub:   # diagonale
            ...; i, j = i - 1, j - 1
        elif i > 0 and D[i][j] == D[i - 1][j] + del_cost:          # dall'alto: cancellazione
            ...; i -= 1
        else:                                                       # da sinistra: inserimento
            ...; j -= 1

def all_alignments(source, target, ..., limit=30):   # segue TUTTI i puntatori (ricorsione)
```

Output:

```text
       #    e    x    e    c    u    t    i    o    n
...
distance 8
   i n t e * n t i o n
   * e x e c u t i o n
   d s s   i s

134 minimum-cost alignments of intention and execution
3 minimum-cost alignments of cat and cut:

   c a t
   c u t
     s  
   ...
```

Il backtrace non memorizza i puntatori: li **ricostruisce** all'indietro, scegliendo una cella vicina il cui valore più il costo del passo dà esattamente $D[i,j]$ (è il metodo del riquadro della [scheda 51](L03-elaborazione-del-testo.md#p-51)). In caso di parità preferisce la diagonale, poi l'alto, poi la sinistra: con questa scelta esce proprio l'allineamento della [scheda 37](L03-elaborazione-del-testo.md#p-37), e il cammino in parentesi quadre coincide con quello in grassetto della [scheda 50](L03-elaborazione-del-testo.md#p-50).

`all_alignments` segue tutti i puntatori: 134 allineamenti ottimi per intention/execution con sostituzione a 2, come scritto nella [scheda 51](L03-elaborazione-del-testo.md#p-51) (e 7 con costi 1, verificato con la stessa funzione). *cat*/*cut* mostra perché con sostituzione a 2 gli allineamenti si moltiplicano: una sostituzione (2) costa quanto una cancellazione più un inserimento (1 + 1), in due ordini diversi.

### Notebook 19 · Esercizi 10, 11 e 12 della scheda

```python
show_alignment("leda", "deal", sub_cost=1)             # exercise 10
print_all_alignments("leda", "deal", sub_cost=1)

for sub in (1, 2):                                      # exercise 11 (textbook 2.8)
    d_brief = min_edit_distance("drive", "brief", sub_cost=sub)[-1][-1]
    d_divers = min_edit_distance("drive", "divers", sub_cost=sub)[-1][-1]
    print(f"substitution cost {sub}: drive-brief {d_brief}, drive-divers {d_divers}")
print()
show_alignment("drive", "brief", sub_cost=2)
show_alignment("drive", "divers", sub_cost=2)

show_alignment("sunday", "saturday")                   # exercise 12, substitutions at 2
print_all_alignments("sunday", "saturday")
```

Output:

```text
       #    d    e    a    l
  #  [0]    1    2    3    4
  l    1  [1]    2    3    3
  e    2    2  [1]    2    3
  d    3    2    2  [2]    3
  a    4    3    3    2  [3]

distance 3
   l e d a
   d e a l
   s   s s

substitution cost 1: drive-brief 3, drive-divers 3
substitution cost 2: drive-brief 4, drive-divers 3

       #    s    a    t    u    r    d    a    y
  #  [0]    1    2    3    4    5    6    7    8
  s    1  [0]  [1]  [2]    3    4    5    6    7
  u    2    1    2    3  [2]    3    4    5    6
  n    3    2    3    4    3  [4]    5    6    7
  d    4    3    4    5    4    5  [4]    5    6
  a    5    4    3    4    5    6    5  [4]    5
  y    6    5    4    5    6    7    6    5  [4]

distance 4
   s * * u n d a y
   s a t u r d a y
     i i   s      

3 minimum-cost alignments of sunday and saturday
```

Le tabelle degli esercizi. (10) *leda* → *deal* a costi 1: distanza 3, due allineamenti ottimi (tre sostituzioni, oppure sostituzione + cancellazione di d + inserimento di l). (11) Con costi 1 *drive* dista 3 sia da *brief* sia da *divers* (pareggio); con sostituzione a 2 *brief* sale a 4 e *divers* resta 3, perché il suo allineamento ottimo non usa sostituzioni: la risposta dipende dai costi. (12) *sunday* → *saturday* con sostituzione a 2: distanza 4, tre allineamenti ottimi; il backtrace dà inserisci a, inserisci t, sostituisci n con r.

Tabelle complete con i backpointer nelle soluzioni della sezione Studio, generate con la stessa DP e controllate contro l'output del notebook.

### Notebook 20 · Dove si usa: correzione ortografica, WER, entità

```python
typed = "graffe"
for cand in ["giraffe", "grail", "graf", "gaffe", "graph"]:
    print(f"{typed} -> {cand:8} {min_edit_distance(typed, cand, sub_cost=1)[-1][-1]}")
print()
reference = "the cat sat on the mat".split()
recognized = "the cat sat on mat today".split()
d = min_edit_distance(reference, recognized, sub_cost=1)[-1][-1]
print(f"word error rate = {d} / {len(reference)} = {d / len(reference):.2f}")
print()
show_alignment("Stanford President Marc Tessier-Lavigne".split(),
               "Stanford University President Marc Tessier-Lavigne".split(), table=False)
```

Output:

```text
graffe -> giraffe  1
graffe -> grail    3
graffe -> graf     2
graffe -> gaffe    1
graffe -> graph    3

word error rate = 2 / 6 = 0.33


distance 1
   Stanford *          President Marc Tessier-Lavigne
   Stanford University President Marc Tessier-Lavigne
            i
```

Le applicazioni della [scheda 52](L03-elaborazione-del-testo.md#p-52). Correzione: con costi 1 *giraffe* e *gaffe* sono entrambe a distanza 1 da *graffe* (un inserimento, una cancellazione): la distanza da sola non sceglie, servono pesi o probabilità (canale rumoroso). WER: sulle **liste di parole**, *the cat sat on the mat* contro *the cat sat on mat today* ha distanza 2 (cancellazione di *the*, inserimento di *today*), WER = 2/6 ≈ 0,33 (verificato). Ultimo esempio: due menzioni della stessa entità differiscono per un solo inserimento di parola.

Nota: il WER va calcolato con costi tutti 1, come fa la cella (`sub_cost=1`); con il default a 2 una parola sbagliata varrebbe due errori.

## Studio ed esercizi

### Guida allo studio (circa 5 h 30 min)

**Espressioni regolari: sintassi** (45 min)

Schede 5-13. Imparare la tabella di quadre, intervalli e negazione, i contatori (`* + ? {n}`, `.`), ancore e `\b`, alias ed escape, la tabella di precedenza. Saper leggere un pattern con la precedenza e scriverne uno con casi di test. Attenzione al caret letterale in Python (riquadro della scheda 6). Esercizi 1, 2, 6 della scheda ufficiale e aggiuntivo A. Libro §2.6.1-2.6.6. Consiglio pratico: provare ogni esempio in Python, è il modo più rapido di fissarli.

**Gruppi, sostituzioni, lookahead, ELIZA, GPT-2** (35 min)

Schede 14-20. Gruppi di cattura e numerazione, backreference (parole ripetute), gruppi non catturanti, greedy contro lazy, lookahead, ELIZA come cascata di sostituzioni, le cinque alternative del pretokenizer di GPT-2 e il suo output. Esercizi 3, 4, 5, 7 della scheda; aggiuntivi B, C, E. Libro §2.6.7-2.6.9; ripassare [L2 schede 41-42](L02-parole-e-token.md#p-41).

**Unix e tokenizzazione a regole** (30 min)

Schede 23-32. Saper scrivere la pipeline `tr | sort | uniq -c | sort -n -r` e spiegare ogni opzione; desiderata per l'inglese, Penn Treebank, il tokenizer NLTK (ordine delle alternative, riquadro sull'82%), segmentazione in frasi. Esercizi 8 e 9 della scheda; aggiuntivi D e F. Libro §2.7-2.8.

**Normalizzazione e Porter** (20 min)

Schede 33-34 (materiale non presente nel draft 2026 del libro: le schede sono la fonte). Differenze fra case folding, lemmatizzazione e stemming, con pro e contro; le tre regole di Porter citate e i due tipi di errore (attenzione agli esempi corretti nel riquadro). Esercizio aggiuntivo G.

**Distanza di edit** (45 min)

Schede 36-52: definizione, allineamento, principio di ottimalità, ricorrenza, pseudocodice, tabella intention/execution (rifarla a mano almeno una volta, confrontando con la scheda 45), backpointer e backtrace, WER. Libro §2.9. Le tabelle degli esercizi 10-12 della scheda sono il tipo di esercizio più probabile allo scritto; aggiuntivo H per il WER.

**Scheda esercizi ufficiale (L03)** (80 min)

I 12 esercizi della scheda, a mano, prima di guardare il notebook e le soluzioni: circa 30 minuti per le regex (1-6), 15 per la tokenizzazione (7-9), 35 per le tre griglie di distanza di edit (10-12, con le frecce e il backtrace). Poi controllare ogni risposta con la cella corrispondente del notebook e con le soluzioni qui sotto. Punti delicati: la stringa vuota in 2c, i `\b` in 3a e 3b, il perché di *thethe* in 6a, il doppio ruolo del punto in 9, il pareggio a costi unitari in 11.

**Notebook** (45 min)

Eseguire il notebook dall'inizio (solo libreria standard). Correggere i primi tentativi sbagliati delle celle 21-27 e 38 finché `check` dice *all good*; leggere `min_edit_distance`, `backtrace` e `all_alignments` finché si sa spiegare ogni riga. Provare le correzioni dei tre riquadri: ELIZA con `\b` (e *I'm sad.*), il pretokenizer su *E = mc²*, `module_text` senza doppioni. Poi cambiare gli input: nuove regole ELIZA, altre coppie di parole per la distanza.

**Ripasso orale** (30 min)

Rispondere ad alta voce alle domande della sezione orale senza guardare la traccia, poi confrontare. Punti che cadono spesso: precedenza degli operatori, greedy, gruppi e `\1`, perché `uniq` vuole l'input ordinato, clitici nel Treebank, ricorrenza della distanza di edit con i due sistemi di costi (5 contro 8), come si legge un allineamento dal backtrace.

### Esercizi

#### Esercizio 1 (scheda L03): leggere pattern

Di' che cosa corrisponde a ciascun pattern (raw string Python). In (a) e (b) deve corrispondere tutta la stringa, in (c) è una ricerca.

(a) `r"colou?r"` su *color*, *colour*, *colouur*. (b) `r"baa+!"` su *ba!*, *baa!*, *baaaa!*, *baaa*. (c) Sottolinea le occorrenze trovate da `r"\b[tT]he\b"` in: *The other cat sat there, then the dog left.*

<details><summary>Soluzione</summary>

(a) `?` rende opzionale il solo carattere precedente, la u: *color* sì, *colour* sì, *colouur* **no** (al massimo una u).

(b) `baa+!` = b, una a, poi una o più a, poi !, cioè almeno due a: *ba!* no (una sola a), *baa!* sì, *baaaa!* sì, *baaa* no (manca il punto esclamativo, e con `fullmatch` serve tutta la stringa).

(c) Due occorrenze: **The** other cat sat there, then **the** dog left. *other* contiene *the* ma prima della t c'è la o (nessun confine); in *there* e *then* dopo la e c'è un'altra lettera (nessun confine). La maiuscola di *The* è coperta da `[tT]`. Verificato con `re.finditer` (cella 9 del notebook).

</details>

#### Esercizio 2 (scheda L03, libro 2.4): scrivere pattern per linguaggi

Scrivi una regex per ciascun insieme (deve corrispondere tutta la stringa): (a) tutte le stringhe alfabetiche; (b) tutte le stringhe alfabetiche minuscole che finiscono con una b; (c) tutte le stringhe sull'alfabeto {a, b} in cui ogni a è immediatamente preceduta e immediatamente seguita da una b.

<details><summary>Soluzione</summary>

(a) `[A-Za-z]+` (con `re.fullmatch`; con `re.search` servono le ancore: `^[A-Za-z]+$`). Il `+` esclude la stringa vuota. *Hello*, *HLT* sì; *abc1*, *hello world*, *don't* no. Errore tipico (primo tentativo del notebook): `[a-z]+` rifiuta le maiuscole.

(b) `[a-z]*b`: zero o più minuscole, poi b. *b*, *bob*, *climb* sì; *Bob*, *bobs*, *climB* no. Errore tipico: `[a-z]+b` rifiuta la stringa *b*.

(c) `(b+(ab+)*)?`. Ragionamento: una stringa non vuota deve iniziare con b (una a iniziale non ha la b prima); dopo ogni a serve almeno una b, quindi il resto è una sequenza di blocchi *a* + una o più b; due a consecutive sono impossibili; la stringa non può finire con a. La stringa vuota non contiene a, quindi soddisfa la condizione: il tutto è opzionale (se si vuole escluderla, togliere il `?`). *b*, *bab*, *bbabb*, *babab* sì; *a*, *ab*, *ba*, *baab*, *abab* no.

Il primo tentativo del notebook, `(b|bab)*`, sbaglia *babab*: i blocchi *bab* non possono condividere la b centrale. Anche `b*(bab*)*`, che sembra naturale, è sbagliata (accetta *ba*). Verifica: ho confrontato `(b+(ab+)*)?` con la definizione su tutte le stringhe di a e b fino a lunghezza 10, nessuna discrepanza; `(b|bab)*` sbaglia 7 stringhe fino a lunghezza 7.

</details>

#### Esercizio 3 (scheda L03, libro 2.5): pattern per testo

Per *parola* si intende una stringa alfabetica separata dalle altre da spazi, punteggiatura o a capo. Scrivi un pattern (ricerca) per: (a) stringhe con due parole consecutive ripetute (*Humbert Humbert*, *the the*, ma non *the bug* né *the big bug*); (b) righe che iniziano con un intero e finiscono con una parola; (c) stringhe che contengono sia la parola *grotto* sia la parola *raven* (non *grottos*).

<details><summary>Soluzione</summary>

(a) `\b([A-Za-z]+)\s+\1\b`. Il gruppo cattura una parola, `\1` chiede la stessa sequenza dopo uno o più spazi. I due `\b` sono essenziali: il primo tentativo del notebook, `(\w+) \1`, trova *is is* dentro *this is* e *the the* dentro *in the theatre*. Per non distinguere maiuscole (*The the*) si aggiunge `re.I`; se anche la punteggiatura può separare le due parole si usa `[^A-Za-z]+` al posto di `\s+`.

(b) `^\d+\b.*\b[A-Za-z]+$`. Il `\b` dopo l'intero esclude *42nd street*, che il primo tentativo `^\d+.*[A-Za-z]+$` accetta; il `\b` prima della parola finale fa sì che sia una parola intera. *42 is the answer*, *7 samurai* sì; *The 42 answers*, *42 is the answer.* (finisce con il punto), *42 44* no. Su un testo di più righe si usa `re.M`.

(c) Le due parole possono comparire in qualunque ordine, quindi due alternative: `\bgrotto\b.*\braven\b|\braven\b.*\bgrotto\b`; oppure due lookahead: `^(?=.*\bgrotto\b)(?=.*\braven\b)`. Il primo tentativo `grotto.*raven` sbaglia tre casi: ordine inverso (*the raven flew into the grotto*), *grottos and ravens* e *grottoraven* (niente confini). Tutte le correzioni passano tutti i test delle celle 25-27 del notebook (verificato).

</details>

#### Esercizio 4 (scheda L03): sostituzioni e gruppi di cattura

(a) Qual è l'output di `re.sub(r"(\d{2})/(\d{2})/(\d{4})", r"\2-\1-\3", "Due 03/09/2026 and 12/25/2025")`? (b) Scrivi una sostituzione che metta parentesi angolari intorno a ogni intero: *the 35 boxes weigh 120 kg* diventa *the <35> boxes weigh <120> kg*.

<details><summary>Soluzione</summary>

(a) Gruppo 1 = primo campo, gruppo 2 = secondo, gruppo 3 = anno; il rimpiazzo li rimette nell'ordine 2, 1, 3 con i trattini: **Due 09-03-2026 and 25-12-2025**. Nota: la regex non sa se *03/09* è il 9 marzo (formato americano) o il 3 settembre; scambia i campi in ogni caso. È l'esempio della [scheda 14](L03-elaborazione-del-testo.md#p-14).

(b) `re.sub(r"(\d+)", r"<\1>", s)`, oppure senza gruppo `re.sub(r"\d+", r"<\g<0>>", s)` (`\g<0>` è tutta la corrispondenza). Il `+` greedy prende l'intero numero; il primo tentativo del notebook, `(\d)`, prende una cifra per volta e dà *<3><5>* e *<1><2><0>*. Per non toccare cifre dentro parole (*H2O*) si usa `\b\d+\b`. Verificato: output *the <35> boxes weigh <120> kg*.

</details>

#### Esercizio 5 (scheda L03): falsi positivi e falsi negativi

Il pattern `r"[tT]he"` viene applicato, cercando tutte le corrispondenze, a *The theory of the other them: the end.* (a) Quante corrispondenze ci sono e quali sono falsi positivi, se cerchiamo l'articolo *the*? (b) Quale pattern li elimina? I falsi positivi abbassano la precisione o il recall? (c) Che tipo di errore farebbe `r"\bthe\b"` su questa stringa?

<details><summary>Soluzione</summary>

(a) **6 corrispondenze**: *The* (posizione 0), *the* dentro *theory*, *the*, *the* dentro *other*, *the* dentro *them*, *the* prima di *end*. Gli articoli veri sono 3; i **falsi positivi** sono 3: *theory*, *other*, *them*. Precisione $3/6 = 0{,}5$, recall $3/3 = 1$.

(b) `r"\b[tT]he\b"`: 3 corrispondenze, tutte giuste, $P = R = 1$. I falsi positivi abbassano la **precisione** ($P = TP/(TP+FP)$); i falsi negativi il recall.

(c) `\bthe\b` non ha falsi positivi ma perde *The* maiuscolo a inizio frase: un **falso negativo**, che abbassa il recall a $2/3$ (precisione 1). Verificato con la cella 29 del notebook ([scheda 12](L03-elaborazione-del-testo.md#p-12)).

</details>

#### Esercizio 6 (scheda L03): precedenza e greediness

(a) Qual è la prima corrispondenza di `r"the*"` in *thethe theee*? Perché non è *thethe*? (b) Sulla stringa *guppies*, che cosa trovano `r"gupp(y|ies)"` e `r"guppy|ies"`? (c) Qual è la prima corrispondenza di `r"<.*>"` e di `r"<.*?>"` in *<a> x <b>*?

<details><summary>Soluzione</summary>

(a) **the** (posizioni 0-3). I contatori hanno precedenza più alta della sequenza: `the*` è *th* seguito da zero o più *e*, e la stella si applica solo alla e. Dopo la prima e viene una t, quindi la stella si ferma a una e. Per ripetere *the* serve `(the)*`, che trova *thethe*. Le corrispondenze successive sono *the* e *theee* (qui la stella greedy prende tutte e tre le e).

(b) `gupp(y|ies)`: le parentesi limitano la disgiunzione a *y|ies*, quindi trova **guppies**. `guppy|ies`: la sequenza lega più della pipe, quindi è *guppy* oppure *ies*; *guppy* non c'è (dopo gupp viene i), e la ricerca trova solo **ies** (posizioni 4-7).

(c) `<.*>` è greedy: `.*` si allunga il più possibile e poi arretra fino all'ultimo *>*: **<a> x <b>**. `<.*?>` è lazy: si ferma al primo *>*: **<a>** (poi, cercando ancora, *<b>*). Verificato con la cella 30 del notebook ([schede 10](L03-elaborazione-del-testo.md#p-10) e [11](L03-elaborazione-del-testo.md#p-11)).

</details>

#### Esercizio 7 (scheda L03): pretokenizzazione per BPE

Il pretokenizer di GPT-2 è `'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+`. Quali chunk produce per *I'm 42 years old!! Don't ask.*? Spiega perché *!!* è un solo chunk e perché *Don't* viene spezzato.

<details><summary>Soluzione</summary>

In ogni posizione si provano le alternative in ordine; vince la prima che corrisponde, e ogni alternativa è greedy. Risultato (10 chunk, ␣ = spazio):

`I` `'m` `␣42` `␣years` `␣old` `!!` `␣Don` `'t` `␣ask` `.`

- *I*: lettere, si ferma all'apostrofo; *'m*: la prima alternativa (contrazioni) vince sull'apostrofo come punteggiatura.
- *␣42*: lo spazio va con il numero che segue ( `?\p{N}+`); lo stesso per *␣years*, *␣old*.
- *!!*: l'alternativa della punteggiatura  `?[^\s\p{L}\p{N}]+` ha il `+`, quindi prende tutta la sequenza di simboli consecutivi; non c'è spazio prima (i punti esclamativi sono attaccati a *old*).
- *Don't*: in posizione dello spazio prima di D nessuna contrazione corrisponde;  `?\p{L}+` prende *␣Don* e si ferma all'apostrofo, che non è una lettera. Nella posizione dell'apostrofo l'alternativa `'t` viene provata per prima e vince. Il taglio è quindi *Don* + *'t*, non il *do* + *n't* del Penn Treebank ([scheda 19](L03-elaborazione-del-testo.md#p-19)).
- *.*: punteggiatura, attaccata ad *ask*, senza spazio.

Verificato sia con il pattern originale (modulo `regex`) sia con la versione `re` della cella 46 del notebook. Con l'apostrofo tipografico (*Don’t*) le contrazioni non scattano e si ottiene *Don*, *’*, *t*.

</details>

#### Esercizio 8 (scheda L03): tokenizzazione Penn Treebank

Tokenizza secondo le convenzioni Penn Treebank (clitici separati, tutta la punteggiatura separata, parole con trattino unite) e conta i token: *"They don't know," she said, "it's \$12.50 per hour-long lesson."*

<details><summary>Soluzione</summary>

`"` `They` `do` `n't` `know` `,` `"` `she` `said` `,` `"` `it` `'s` `$` `12.50` `per` `hour-long` `lesson` `.` `"`

**20 token**. Punti da giustificare: *don't* → *do* + *n't* (taglio prima di n't, [scheda 30](L03-elaborazione-del-testo.md#p-30)); *it's* → *it* + *'s*; il dollaro è un token a sé e *12.50* resta intero (il punto decimale non è punteggiatura); *hour-long* resta unito; la virgola dentro le virgolette dopo *know* e il punto dopo *lesson* sono token separati, e le virgolette di chiusura vengono dopo. Verificato con la funzione `ptb_tokenize` del notebook (20 token) e con `TreebankWordTokenizer` di NLTK (20 token, con le virgolette scritte ``` `` ``` in apertura e `''` in chiusura, la convenzione originale).

</details>

#### Esercizio 9 (scheda L03): segmentazione in frasi

Per ogni punto del testo seguente di' se fa parte di un token, se è un confine di frase o entrambe le cose. Quante frasi ci sono? *Dr. Rossi arrived at 9 a.m. He works for Acme Inc. The meeting lasted 2.5 hours.*

<details><summary>Soluzione</summary>

| Punto | Parte di un token | Confine di frase |
| --- | --- | --- |
| *Dr.* | sì (abbreviazione) | no |
| i primi due punti di *a.m.* | sì | no |
| l'ultimo punto di *a.m.* | sì | **sì** (segue *He*) |
| *Inc.* | sì | **sì** (segue *The*) |
| *2.5* | sì (numero decimale) | no |
| dopo *hours* | no (token a sé) | **sì** |

**3 frasi**: *Dr. Rossi arrived at 9 a.m.* / *He works for Acme Inc.* / *The meeting lasted 2.5 hours.* Il testo mostra perché la segmentazione va fatta insieme alla tokenizzazione ([scheda 32](L03-elaborazione-del-testo.md#p-32)): il punto di un'abbreviazione a fine frase svolge due ruoli insieme, e il criterio «segue una maiuscola» non basta da solo (dopo *Dr.* viene *Rossi*, maiuscolo, ma la frase continua: serve la lista dei titoli). La regola ingenua «spezza dopo ogni punto seguito da spazio» dà 4 frasi (taglia dopo *Dr.*); la funzione `segment` del notebook dà le 3 giuste (verificato).

</details>

#### Esercizio 10 (scheda L03, libro 2.7): la griglia leda → deal

Calcola la distanza di edit minima da *leda* a *deal* con inserimento, cancellazione e sostituzione tutti di costo 1. Riempi la griglia, dai la distanza e un allineamento.

<details><summary>Soluzione</summary>

Righe *leda* (sorgente), colonne *deal*; in ogni cella le frecce di tutte le alternative che danno il minimo (↖ diagonale, ← inserimento, ↑ cancellazione); in grassetto il cammino del backtrace del notebook (preferenza diagonale, poi alto, poi sinistra).

| src\tar | # | d | e | a | l |
| --- | --- | --- | --- | --- | --- |
| # | **0** | ← 1 | ← 2 | ← 3 | ← 4 |
| l | ↑ 1 | **↖ 1** | ↖← 2 | ↖← 3 | ↖ 3 |
| e | ↑ 2 | ↖↑ 2 | **↖ 1** | ← 2 | ← 3 |
| d | ↑ 3 | ↖ 2 | ↑ 2 | **↖ 2** | ↖← 3 |
| a | ↑ 4 | ↑ 3 | ↖↑ 3 | ↖ 2 | **↖← 3** |

Esempi di celle: $D[1,1]$ (*l*/*d*) $= D[0,0] + 1 = 1$; $D[2,2]$ (*le*/*de*) $= D[1,1] + 0 = 1$ perché e = e; $D[3,3]$ (*led*/*dea*) $= \min(D[2,3]+1, D[2,2]+1, D[3,2]+1) = 2$; $D[4,3]$ (*leda*/*dea*) $= D[3,2] + 0 = 2$ perché a = a; $D[4,4] = \min(D[3,4]+1,\ D[3,3]+1,\ D[4,3]+1) = 3$.

Distanza **3**. Due allineamenti ottimi: (1) tutta diagonale: l→d (s), e = e, d→a (s), a→l (s), costo 3; (2) l→d (s), e = e, d cancellata (d), a = a, l inserita (i), costo 1 + 1 + 1 = 3:

```
l e d a *
d e * a l
s   d   i
```

Verificato con la cella 72 del notebook, che trova esattamente questi due. Con sostituzione a 2 la distanza sarebbe 4 (il secondo allineamento resta ottimo), con 4 allineamenti ottimi.

</details>

#### Esercizio 11 (scheda L03, libro 2.8): i costi contano

La parola *drive* è più vicina a *brief* o a *divers*? Rispondi con costi unitari, poi con i costi della lezione (inserimento e cancellazione 1, sostituzione 2).

<details><summary>Soluzione</summary>

**Costi unitari.** *drive* → *brief*:

| src\tar | # | b | r | i | e | f |
| --- | --- | --- | --- | --- | --- | --- |
| # | **0** | ← 1 | ← 2 | ← 3 | ← 4 | ← 5 |
| d | ↑ 1 | **↖ 1** | ↖← 2 | ↖← 3 | ↖← 4 | ↖← 5 |
| r | ↑ 2 | ↖↑ 2 | **↖ 1** | ← 2 | ← 3 | ← 4 |
| i | ↑ 3 | ↖↑ 3 | ↑ 2 | **↖ 1** | ← 2 | ← 3 |
| v | ↑ 4 | ↖↑ 4 | ↑ 3 | ↑ 2 | **↖ 2** | ↖← 3 |
| e | ↑ 5 | ↖↑ 5 | ↑ 4 | ↑ 3 | ↖ 2 | **↖← 3** |

Distanza **3**: d→b (s), r = r, i = i, v→e (s), e→f (s); oppure d→b (s), r, i, v cancellata (d), e = e, f inserita (i).

*drive* → *divers*:

| src\tar | # | d | i | v | e | r | s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| # | **0** | ← 1 | ← 2 | ← 3 | ← 4 | ← 5 | ← 6 |
| d | ↑ 1 | **↖ 0** | ← 1 | ← 2 | ← 3 | ← 4 | ← 5 |
| r | ↑ 2 | **↑ 1** | ↖ 1 | ↖← 2 | ↖← 3 | ↖ 3 | ← 4 |
| i | ↑ 3 | ↑ 2 | **↖ 1** | ↖← 2 | ↖← 3 | ↖←↑ 4 | ↖ 4 |
| v | ↑ 4 | ↑ 3 | ↑ 2 | **↖ 1** | ← 2 | ← 3 | ← 4 |
| e | ↑ 5 | ↑ 4 | ↑ 3 | ↑ 2 | **↖ 1** | **← 2** | **← 3** |

Distanza **3**, un solo allineamento ottimo: d = d, r cancellata, i, v, e uguali, r e s inserite. Con costi unitari è un **pareggio** (3 e 3).

**Sostituzione a 2.** *drive* → *brief*:

| src\tar | # | b | r | i | e | f |
| --- | --- | --- | --- | --- | --- | --- |
| # | **0** | ← 1 | ← 2 | ← 3 | ← 4 | ← 5 |
| d | ↑ 1 | **↖←↑ 2** | ↖←↑ 3 | ↖←↑ 4 | ↖←↑ 5 | ↖←↑ 6 |
| r | ↑ 2 | ↖←↑ 3 | **↖ 2** | ← 3 | ← 4 | ← 5 |
| i | ↑ 3 | ↖←↑ 4 | ↑ 3 | **↖ 2** | ← 3 | ← 4 |
| v | ↑ 4 | ↖←↑ 5 | ↑ 4 | **↑ 3** | ↖←↑ 4 | ↖←↑ 5 |
| e | ↑ 5 | ↖←↑ 6 | ↑ 5 | ↑ 4 | **↖ 3** | **← 4** |

Distanza **4**: d→b sostituzione (2), r, i uguali, v cancellata (1), e = e, f inserita (1). Gli allineamenti ottimi sono 3 (gli altri due sostituiscono la sostituzione d→b con cancellazione + inserimento).

*drive* → *divers*:

| src\tar | # | d | i | v | e | r | s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| # | **0** | ← 1 | ← 2 | ← 3 | ← 4 | ← 5 | ← 6 |
| d | ↑ 1 | **↖ 0** | ← 1 | ← 2 | ← 3 | ← 4 | ← 5 |
| r | ↑ 2 | **↑ 1** | ↖←↑ 2 | ↖←↑ 3 | ↖←↑ 4 | ↖ 3 | ← 4 |
| i | ↑ 3 | ↑ 2 | **↖ 1** | ← 2 | ← 3 | ←↑ 4 | ↖←↑ 5 |
| v | ↑ 4 | ↑ 3 | ↑ 2 | **↖ 1** | ← 2 | ← 3 | ← 4 |
| e | ↑ 5 | ↑ 4 | ↑ 3 | ↑ 2 | **↖ 1** | **← 2** | **← 3** |

Distanza ancora **3**: l'allineamento ottimo non usa sostituzioni, quindi il loro costo non conta.

**Risposta**: con costi unitari *drive* è equidistante (3 e 3); con sostituzione a 2 è più vicina a *divers* (3 contro 4). Controllo rapido con la formula della LCS (sostituzione a 2): $5 + 5 - 2\cdot 3 = 4$ per *brief* (LCS *rie*), $5 + 6 - 2\cdot 4 = 3$ per *divers* (LCS *dive*). Verificato con la cella 73 del notebook.

</details>

#### Esercizio 12 (scheda L03): backtrace sunday → saturday

Calcola la distanza di edit minima da *sunday* a *saturday* con inserimento e cancellazione a 1 e sostituzione a 2. Poi ricava un allineamento con il backtrace dall'ultima cella e scrivi la lista delle operazioni.

<details><summary>Soluzione</summary>

Righe *sunday*, colonne *saturday*; frecce di tutte le alternative minime, in grassetto il cammino del backtrace.

| src\tar | # | s | a | t | u | r | d | a | y |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| # | **0** | ← 1 | ← 2 | ← 3 | ← 4 | ← 5 | ← 6 | ← 7 | ← 8 |
| s | ↑ 1 | **↖ 0** | **← 1** | **← 2** | ← 3 | ← 4 | ← 5 | ← 6 | ← 7 |
| u | ↑ 2 | ↑ 1 | ↖←↑ 2 | ↖←↑ 3 | **↖ 2** | ← 3 | ← 4 | ← 5 | ← 6 |
| n | ↑ 3 | ↑ 2 | ↖←↑ 3 | ↖←↑ 4 | ↑ 3 | **↖←↑ 4** | ↖←↑ 5 | ↖←↑ 6 | ↖←↑ 7 |
| d | ↑ 4 | ↑ 3 | ↖←↑ 4 | ↖←↑ 5 | ↑ 4 | ↖←↑ 5 | **↖ 4** | ← 5 | ← 6 |
| a | ↑ 5 | ↑ 4 | ↖ 3 | ← 4 | ←↑ 5 | ↖←↑ 6 | ↑ 5 | **↖ 4** | ← 5 |
| y | ↑ 6 | ↑ 5 | ↑ 4 | ↖←↑ 5 | ↖←↑ 6 | ↖←↑ 7 | ↑ 6 | ↑ 5 | **↖ 4** |

Distanza **4**. Backtrace da $(6,8)$: ↖ y = y, ↖ a = a, ↖ d = d fino a $(3,5)$, sempre valore 4 (corrispondenze gratuite); $(3,5) \to (2,4)$ ↖: n contro r, sostituzione ($4 = 2 + 2$); $(2,4) \to (1,3)$ ↖: u = u ($2 = 2 + 0$); $(1,3) \to (1,2) \to (1,1)$ ← ←: inserimenti di t e di a ($2 = 1 + 1$, $1 = 0 + 1$); $(1,1) \to (0,0)$ ↖: s = s.

```
s * * u n d a y
s a t u r d a y
  i i   s
```

Lista delle operazioni (da sinistra): tieni s, **inserisci a**, **inserisci t**, tieni u, **sostituisci n con r**, tieni d, a, y. Costo $1 + 1 + 2 = 4$. Gli allineamenti ottimi sono 3: negli altri due la sostituzione n→r è sostituita da cancellazione di n + inserimento di r, in un ordine o nell'altro (stesso costo 2). Controllo: LCS = *suday* (5), $6 + 8 - 2\cdot 5 = 4$. Con costi unitari la distanza sarebbe 3 (l'esempio classico). Verificato con la cella 74 del notebook.

</details>

#### Esercizio aggiuntivo A: leggere regex e precedenza

Per ogni pattern (usato con `re.search`) di' quali stringhe corrispondono. (a) `^(the)*$` su: vuota, *the*, *thethe*, *thee*. (b) `^ab*|c$` su: *a*, *abbb*, *xc*, *ac?*. (c) `^[^aeiou]+$` su: *rhythm*, *sky*, *tree*. (d) `^x{2,3}y?$` su: *xx*, *xxxy*, *x*, *xxxxy*.

<details><summary>Soluzione</summary>

(a) Sì, sì, sì, no: la stella ripete l'intero gruppo; *thee* non è una concatenazione di *the*.

(b) La pipe ha la precedenza più bassa: il pattern è `(^ab*)|(c$)`, «a a inizio stringa seguita da b» **oppure** «c a fine stringa». Quindi *a* sì, *abbb* sì, *xc* sì (seconda alternativa), *ac?* sì (prima alternativa: la a iniziale basta, `search` non chiede di coprire tutta la stringa). Errore tipico: leggerlo come `^(ab*|c)$`, che rifiuterebbe *xc* e *ac?*.

(c) Solo consonanti: *rhythm* e *sky* sì, *tree* no.

(d) Due o tre x e una y opzionale: *xx* sì, *xxxy* sì, *x* no, *xxxxy* no (quattro x; `^` e `$` impediscono di trovarne tre dentro). Verificato.

</details>

#### Esercizio aggiuntivo B: sostituzioni con gruppi (e una trappola greedy)

(a) Converti le date ISO *2027-01-15* nel formato *15/01/2027*. (b) Trasforma *Rossi, Mario; Bianchi, Anna* in *Mario Rossi; Anna Bianchi*. (c) Che cosa produce `re.sub(r"\((.*)\)", r"[\1]", "f(a) + g(b)")`? Come lo correggi?

<details><summary>Soluzione</summary>

(a) `re.sub(r"(\d{4})-(\d{2})-(\d{2})", r"\3/\2/\1", s)`: gruppo 1 anno, 2 mese, 3 giorno, ricomposti al contrario. Su *Esame il 2027-01-15, orale 2027-02-03.* dà *Esame il 15/01/2027, orale 03/02/2027.*

(b) `re.sub(r"\b([A-Z][a-z]+), ([A-Z][a-z]+)\b", r"\2 \1", s)` → *Mario Rossi; Anna Bianchi*.

(c) `.*` è greedy: va dalla prima `(` all'**ultima** `)`, quindi l'output è *f[a) + g(b]*. Con la versione lazy `\((.*?)\)` si ottiene *f[a] + g[b]*; in alternativa `\(([^)]*)\)`, che non può attraversare una parentesi chiusa. Tutti e tre verificati.

</details>

#### Esercizio aggiuntivo C: precisione e recall di un pattern

Testo: *Nel 1999 pagammo 2500 euro; nel 2021 i visitatori furono 120345, nel '98 pochi. Dal 2020 al 2023 poi.* Obiettivo: trovare gli anni scritti con quattro cifre. Calcola precisione e recall di `\d{4}` e di `\b(?:19|20)\d{2}\b`.

<details><summary>Soluzione</summary>

Anni a quattro cifre nel testo: 1999, 2021, 2020, 2023, quindi 4 positivi veri.

`\d{4}` trova 6 stringhe: 1999, 2500, 2021, **1203** (le prime quattro cifre di 120345), 2020, 2023. $TP = 4$, $FP = 2$ (2500 e 1203), $FN = 0$: $P = 4/6 \approx 0{,}67$, $R = 4/4 = 1$.

`\b(?:19|20)\d{2}\b` trova 1999, 2021, 2020, 2023: $P = R = 1$. I `\b` escludono 1203 dentro 120345, il prefisso 19/20 esclude 2500. Se il compito includesse anche gli anni abbreviati (*'98*), il recall scenderebbe a 4/5 = 0,8: allargare il pattern per prenderlo (per esempio `'\d{2}`) rischia nuovi falsi positivi. Verificato con `re.finditer`.

</details>

#### Esercizio aggiuntivo D: pipeline Unix a mano

Il file `ex.txt` contiene *The cat saw the dog. The dog saw THE cat's toy!* Scrivi l'output di (a) `tr -sc 'A-Za-z' '\n' &lt; ex.txt | sort | uniq -c` (ordinamento per byte) e (b) `tr -sc 'A-Za-z' '\n' &lt; ex.txt | tr A-Z a-z | sort | uniq -c | sort -n -r`. (c) Quante istanze e quanti tipi, prima e dopo il case folding? (d) Che cosa cambia togliendo il primo `sort` in (b)?

<details><summary>Soluzione</summary>

Il primo `tr` produce 12 righe: The, cat, saw, the, dog, The, dog, saw, THE, cat, s, toy (l'apostrofo di *cat's* spezza la parola; il punto esclamativo finale diventa l'a capo conclusivo).

(a) Maiuscole prima delle minuscole: `1 THE`, `2 The`, `2 cat`, `2 dog`, `1 s`, `2 saw`, `1 the`, `1 toy`.

(b) `4 the`, `2 saw`, `2 dog`, `2 cat`, `1 toy`, `1 s` (a parità di conteggio, `sort -r` ordina all'indietro anche il resto della riga).

(c) Istanze $N = 12$ in entrambi i casi; tipi $|V| = 8$ prima (THE, The, the distinti) e $|V| = 6$ dopo il case folding.

(d) Senza ordinamento `uniq -c` collassa solo le righe uguali *adiacenti*: in questo testo nessuna parola si ripete di seguito, quindi tutte le 12 righe avrebbero conteggio 1. Verificato eseguendo la pipeline con `LC_ALL=C`.

</details>

#### Esercizio aggiuntivo E: il pretokenizer di GPT-2

Applica a mano la regex di GPT-2 (schede 18-19) a: (a) *I don't know,  it's 2026!!* (due spazi dopo la virgola); (b) *Città di Pisa: 3,5 km.*

<details><summary>Soluzione</summary>

(a) `I``·don``'t``·know``,``·``·it``'s``·2026``!!` (· = spazio). *don't* diventa *don* + *'t* (contrazione della regex, diversa dal *do* + *n't* del Treebank); dei due spazi il primo resta da solo (`\s+(?!\S)`) e il secondo si attacca a *it*; *!!* è un'unica sequenza di punteggiatura.

(b) `Città``·di``·Pisa``:``·3``,``5``·km``.`: `\p{L}` accetta la à; il numero decimale all'italiana si spezza in tre chunk (3, virgola, 5). Entrambi verificati con la libreria `regex`.

</details>

#### Esercizio aggiuntivo F: tokenizzazione Penn Treebank

Tokenizza secondo lo standard Penn Treebank: *She said, "I can't pay \$45.55 for the state-of-the-art Ph.D. books."*

<details><summary>Soluzione</summary>

*She* | *said* | *,* | *"* | *I* | *ca* | *n't* | *pay* | *\$* | *45.55* | *for* | *the* | *state-of-the-art* | *Ph.D.* | *books* | *.* | *"*: 17 token.

Punti chiave: *can't* si divide in *ca* + *n't* (il clitico è *n't*); il dollaro si stacca dal numero, ma *45.55* resta intero; le parole con trattino restano unite; *Ph.D.* tiene i punti interni e finale perché è un'abbreviazione; virgolette e punto finale sono token. Verificato con `TreebankWordTokenizer` di NLTK, che scrive le virgolette di apertura come ``` `` ``` e quelle di chiusura come `''`.

</details>

#### Esercizio aggiuntivo G: stemmer di Porter e normalizzazione

(a) Applica Porter a: *caresses, ponies, relational, motoring, sing, hopping, generalization, computer, computation*. (b) Per la frase *He is reading detective stories* scrivi il risultato di case folding, lemmatizzazione e stemming.

<details><summary>Soluzione</summary>

(a) *caress* (SSES → SS), *poni* (IES → I), *relat* (ATIONAL → ATE dà *relate*, poi il passo 5 toglie la e), *motor*, *sing* (lo stem *s* non contiene vocali, ING resta), *hop* (tolto ING, poi la doppia consonante si riduce), *gener* (*generalization* → *generalize* → *general* → *gener*, un caso di over-stemming), *comput*, *comput*. Verificato con NLTK.

(b) Case folding: *he is reading detective stories*. Lemmatizzazione: *He be read detective story* (scheda 33). Stemming Porter (NLTK, token per token): *he is read detect stori*; con l'algoritmo originale *is* diventa *i* (NLTK lo protegge con una lista di eccezioni). Lo stemmer non sa che *is* è una forma di *be* e produce stem che non sono parole.

</details>

#### Esercizio aggiuntivo H: word error rate

Riferimento: *i want to book a flight to pisa*. Ipotesi del riconoscitore: *i want book the flight to pisa please*. Allinea le due sequenze di parole con costi 1 e calcola il WER.

<details><summary>Soluzione</summary>

Allineamento ottimo: i = i, want = want, **to** cancellata (D), book = book, **a → the** (S), flight, to, pisa uguali, **please** inserita (I). $S = 1$, $D = 1$, $I = 1$, $N = 8$ parole nel riferimento: $\text{WER} = 3/8 = 37{,}5\%$. Verificato con la DP sulle liste di parole (distanza 3). Nota: la distanza si calcola fra **parole**, non fra caratteri: *a* → *the* è una sola sostituzione.

</details>

### Domande tipo orale

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
