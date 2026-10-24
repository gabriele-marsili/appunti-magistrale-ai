# L16 · Laboratorio: dagli n-gram a GPT

*Lab: Language Models from counting characters to GPT* · 16/10/2026 · Andrea Ceni · lettura: J&M cap. 3 (§3.1 n-gram, Markov e MLE; §3.2-3.3 training/test set e perplexity; §3.4 campionamento; §3.5 overfitting; §3.6.1-3.6.2 Laplace e add-k; §3.7 entropia e cross-entropy); cap. 6, §6.6 (training con backpropagation); cap. 7 (§7.1 attenzione; §7.2 transformer block; §7.3 forma matriciale, Eq. 7.39-7.40; §7.4 embedding di token e posizione; §7.5 language modeling head; §7.6 decodifica, temperatura e top-k; §7.7 pretraining, Eq. 7.55, teacher forcing, §7.7.1 perplexity in nats; §7.8 KV cache)

[Versione interattiva sul sito](https://gabriele-marsili.github.io/appunti-magistrale-ai/anno-2/hlt/sito/#L16) · [Indice della dispensa](README.md)

Laboratorio (solo notebook, nessuna slide) che gioca un unico gioco con due modelli opposti: **dati i caratteri visti finora, prevedere il prossimo**, sulla *Divina Commedia* (il corpus scelto negli output salvati; in alternativa Tiny Shakespeare). Prima gli **n-gram di caratteri** della L4-L5: tabella bigram per conteggio, generazione greedy e campionata, ordini fino a 9, **cross-entropy e perplexity** su validazione con e senza add-$\alpha$, e il **muro degli n-gram** ($V^h$ contesti). Poi un **tiny GPT** stile nanoGPT costruito classe per classe sulla figura del transformer della L14 (testa causale, multi-head, feedforward, blocco prenorm, embedding di posizione, LM head), addestrato con AdamW e confrontato con il 5-gram sulla stessa metrica: dopo 500 passi su CPU il 5-gram vince ancora (1,77 contro 2,23 nats). Gli esercizi guardano dentro le teste di attenzione, tolgono i componenti uno alla volta (ablazioni) e rendono il modello veloce: attenzione vettorizzata, SDPA/FlashAttention, **KV cache**.

## Indice

- [Notebook](#notebook)
- [Studio ed esercizi](#studio-ed-esercizi)

## Notebook

Commento al notebook del corso `HLT-2026-27-L16-Language_Models_from_counting_characters_to_GPT.ipynb` (il notebook è del docente e non è incluso).

Prima parte guidata (celle 0-35): un unico gioco, *dati i caratteri visti finora, scommetti sul prossimo*, giocato prima con i modelli a conteggio della [L4](L04-modelli-linguistici-n-gram.md#p-7) e della [L5](L05-smoothing-ed-entropia.md#p-7). Il token è il **carattere** (vocabolario piccolissimo e trasparente), il corpus a scelta fra *Tiny Shakespeare* e la *Divina Commedia*. Si costruiscono la tabella bigram per conteggio (MLE), la si guarda come mappa, la si usa per generare (greedy contro campionamento), si allunga il contesto fino al 9-gram, si misurano **cross-entropy** e **perplexity** su testo held-out con e senza add-$\alpha$, e si arriva al **muro degli n-gram**: $V^h$ contesti possibili.

**Il corpus degli output salvati è Dante**, non Shakespeare: nella cella 6 è attivo `DATASET = "Dante"` (535.473 caratteri, 77 simboli). Tutti i numeri qui sotto sono quindi sulla *Commedia*. Ho installato PyTorch 2.14 (CPU) e rieseguito tutto il notebook sullo stesso testo, con le mie soluzioni degli esercizi: tutta la parte n-gram (vocabolario, split, conteggi, tabelle, perplexity, campioni generati con seed fissati, autopsia) coincide **esattamente** con gli output salvati; anche la parte neurale guidata (inizializzazione, loss iniziale, curva di training fino al passo 500, campioni generati, confronto finale) si riproduce identica, grazie al seed fisso e al training su CPU; cambiano solo i tempi dei benchmark, che dipendono dalla macchina. Una curiosità del file: la cella di setup (4) mostra come output salvato un `ModuleNotFoundError: No module named 'torch'`, residuo di un'esecuzione di quella sola cella in un ambiente senza PyTorch; tutte le altre celle hanno output regolari.

### Notebook 1 · Il gioco, le regole della casa e il setup

```python
SEED = 1337
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)
device = "cuda" if torch.cuda.is_available() else "cpu"
```

La tabella iniziale del notebook mette in colonna i due modelli che si confronteranno: **n-gram di caratteri** e **tiny GPT**. Restano identici l'unità (il carattere), l'obiettivo (predire il carattere successivo), il dataset, lo split, la metrica e il modo di generare (campionare dalle probabilità del prossimo carattere). Cambiano solo il **contesto** (gli ultimi $n-1$ caratteri esatti contro una rappresentazione appresa di fino a `block_size` caratteri), il modo di imparare (contare contro discesa del gradiente) e i parametri (tabelle di conteggi contro pesi).

La regola della casa è la **regola della catena** della [scheda 11 della L4](L04-modelli-linguistici-n-gram.md#p-11):

$$P(x_1,\ldots,x_T)=\prod_{t=1}^{T}P(x_t\mid x_{&lt;t})$$

e tutto il notebook risponde a una domanda: come stimare $P(x_t\mid x_{&lt;t})$. L'n-gram risponde con conteggi su un contesto esatto e corto (assunzione di Markov), GPT con una rappresentazione neurale appresa di un contesto lungo. Due differenze di notazione rispetto alle slide: i token sono caratteri, scritti $x_t$ invece di $w_t$, e non si usano `<s>` e `</s>`: il corpus è un unico flusso di caratteri e l'a capo `\n` è un carattere come gli altri.

Il setup importa PyTorch, NumPy, pandas e matplotlib e fissa i seed: rende ripetibili i campioni degli n-gram, mentre per la parte neurale la ripetibilità vale solo a parità di hardware e versione.

### Notebook 2 · Il corpus: la Divina Commedia

```python
DATASET = "Dante"
#DATASET = "Shakespeare"
text = download_corpus(DATASET)   # prova le URL in ordine; Gutenberg come riserva
print(f"Characters: {len(text):,}")
```

Output:

```text
Downloaded Divina Commedia (Dante Alighieri) from https://raw.githubusercontent.com/DanieleVeri/deep_comedy/master/divina_commedia.txt
Characters: 535,473
CANTO PRIMO

  Nel mezzo del cammin di nostra vita
mi ritrovai per una selva oscura
ché la diritta via era smarrita.
  Ah quanto a dir qual era è cosa dura
...
```

Due corpora possibili: *Tiny Shakespeare* (circa 1,1 milioni di caratteri, battute di dialogo `SPEAKER:`) e la *Commedia* (circa 0,54 milioni, terzine di endecasillabi in rima incatenata). Si sceglie una volta e si tiene per tutto il notebook, perché vocabolario, split e modelli dipendono dal corpus. Negli output salvati la scelta è **Dante**: 535.473 caratteri, scaricati dal repository *deep\_comedy* (con Project Gutenberg come riserva, ripulito di intestazione e licenza da `strip_gutenberg`).

Il testo ha una struttura molto regolare che i modelli dovranno imparare: un'intestazione `CANTO ...` per canto, ogni terzina che comincia con **due spazi** di rientro, ogni verso chiuso da un a capo. Le vocali accentate sono scritte all'antica con l'acuto (*piú*, *sí*, *Cosí*), e la dieresi segna le dieresi metriche (*orïoli*): tutto questo finisce nel vocabolario.

### Notebook 3 · PLACE YOUR BETS #1 e il tokenizer in quattro righe

```python
chars = sorted(set(text))                  # il vocabolario V
vocab_size = len(chars)
stoi = {ch: i for i, ch in enumerate(chars)}
itos = {i: ch for ch, i in stoi.items()}
def encode(s): return [stoi[c] for c in s]
def decode(ids): return "".join(itos[i] for i in ids)
```

Output:

```text
Vocabulary size: 77
Vocabulary:
"\n !'(),-.:;?ABCDEFGHIJLMNOPQRSTUVZ[]abcdefghijlmnopqrstuvxyz«»ÀÈÏàèéëìíïòúüý…"
encode('amor') = [36, 47, 49, 52]  decode(...) = 'amor'
```

Il "tokenizer" del laboratorio: il vocabolario è l'insieme ordinato dei caratteri distinti, `stoi` assegna a ciascuno un id (l'ordine è quello dei code point Unicode: prima `\n` e spazio, poi la punteggiatura, le maiuscole, le minuscole, infine le lettere accentate), `itos` torna indietro, `encode` e `decode` convertono stringhe e liste di id. I modelli vedono solo gli id. È la tokenizzazione più semplice possibile, uno dei tre candidati della [scheda 29 della L2](L02-parole-e-token.md#p-29) (parole, caratteri, sottoparole), senza BPE: i moderni LLM usano sottoparole, ma l'obiettivo di language modeling è identico.

Le risposte alle scommesse #1 (Dante), verificate sul testo:

- **Quanti caratteri distinti?** 77 (Shakespeare ne ha 65).
- **`A` e `a` sono lo stesso token?** No: nessun *case folding*, sono due id diversi (12 e 36). Il modello deve imparare da solo che si comportano in modo simile.
- **Dopo `t`?** La `o` (18,9%), di poco davanti a `e` (18,1%) e `a` (17,2%): lo si vede nel blocco del modello bigram.
- **Lettere inglesi assenti:** `k` e `w` (e le maiuscole `K`, `W`, `X`, `Y`). Ci sono invece `x` (3 volte, tutte in latino: *Vexilla*, *exitu*, *excelsis*), `y` (una volta, *Aegypto*) e `j` (2 volte, nel provenzale di Arnaut Daniel: *jausen*, *joi*). Accentate: `à è é ì í ò ú`, le dieresi `ï ë ü`, poi rarità come `ý`, `À È Ï` e i puntini `…` (1 volta). Le più frequenti sono `í` (1.529) e `è` (926).

### Notebook 4 · Lo split train/validation: niente sbirciate

```python
data = encode(text)
cut = int(0.90 * len(data))
train_ids = data[:cut]     # primo 90%: conteggi (n-gram) e discesa del gradiente (GPT)
val_ids = data[cut:]       # ultimo 10%: solo valutazione
```

Output:

```text
Train characters:      481925
Validation characters:  53548
Validation starts with:
"e vien quel ch'ei pensa».\n  Cosí Beatrice; e quelle anime liete\nsi fero spere sopra fissi poli,\n..."
```

Lo split si fa **una volta** e vale per tutti i modelli: primo 90% per l'addestramento (481.925 caratteri), ultimo 10% per la validazione (53.548). Il fit sul training dice quanto bene un modello spiega dati già visti; il fit sulla validazione quanto bene predice testo nuovo. Il set di validazione fa la parte del **development set** della [scheda 27 della L4](L04-modelli-linguistici-n-gram.md#p-27): si usa per confrontare modelli e scegliere iperparametri (l'ordine $n$, $\alpha$). Un esperimento rigoroso terrebbe anche un test set da usare una sola volta; il notebook lo salta, quindi i numeri di validazione sono un po' ottimisti.

Lo split non è casuale ma **contiguo**: la validazione è la fine del *Paradiso* (comincia a metà del canto XXIV, "Cosí Beatrice; e quelle anime liete"). È la scelta giusta per il testo (uno split casuale di caratteri metterebbe in validazione pezzi di parole già viste a cavallo del taglio), ma introduce uno spostamento di dominio: lessico teologico e astronomico del *Paradiso* contro un training dominato da *Inferno* e *Purgatorio*. È la questione di genere e dominio della [scheda 44 della L4](L04-modelli-linguistici-n-gram.md#p-44), in piccolo.

### Notebook 5 · Il modello bigram: contare e normalizzare

```python
def build_ngram_table(ids, order=2):
    history = order - 1
    table = defaultdict(Counter)          # table[context][next] = C(context next)
    ...
    for i in range(history, len(ids)):
        ctx = tuple(ids[i-history:i])     # gli n-1 token precedenti esatti
        table[ctx][ids[i]] += 1
    return table

bigram_table = build_ngram_table(train_ids, order=2)
show_next_chars("t", bigram_table)
```

Output:

```text
   next_char  count  MLE_probability
0        'o'   3800         0.189130
1        'e'   3638         0.181067
2        'a'   3462         0.172307
3        'r'   2815         0.140106
4        'i'   2322         0.115568
5        't'   2139         0.106460
6        'u'   1394         0.069381
7        "'"    185         0.009208
8        'à'    115         0.005724
...
```

Il **modello bigram di caratteri** assume che il prossimo carattere dipenda solo dal precedente (assunzione di Markov, [scheda 12 della L4](L04-modelli-linguistici-n-gram.md#p-12)): $P(x_t\mid x_{&lt;t})\approx P(x_t\mid x_{t-1})$. La stima **MLE** è un rapporto di conteggi, $P(b\mid a)=C(ab)/C(a)$ ([scheda 13 della L4](L04-modelli-linguistici-n-gram.md#p-13)). Niente rete, niente optimizer, niente gradiente: solo contare.

`build_ngram_table` scorre gli id di training e per ogni posizione registra quale token ha seguito il contesto dei suoi $n-1$ predecessori. Il risultato è un dizionario *contesto → Counter dei successori*: la tabella dei conteggi delle slide, memorizzata in forma **sparsa** (solo le coppie che compaiono). Con `order=1` il contesto è la tupla vuota e si ottiene l'unigram.

La riga di `t`: dopo `t` vengono quasi sempre vocali (`o e a i u`, insieme il 72,7%), poi `r` (*tr*: *trattar*, *entrai*) e `t` (le doppie: *diritta*, *tutto*). L'apostrofo (0,9%) è *t'* come in *Tant'è*. Il denominatore $C(t)$ vale $3800/0{,}18913 \approx 20.092$: tutte le volte che `t` è seguito da qualcosa nel training.

### Notebook 6 · La mappa bigram e il controllo di normalizzazione

```python
top = [tok for tok, _ in Counter(train_ids).most_common(30)]
for i, a in enumerate(top):
    counts = bigram_table[(a,)]; total = sum(counts.values())
    for j, b in enumerate(top):
        P[i, j] = counts[b] / total       # MLE: C(a b) / C(a)
plt.imshow(P, cmap="Blues")
```

Output:

```text
Context: 't'
Probability sum: 1.0000000000000002
```

Il modello bigram è una matrice $|V|\times|V|$: la riga $a$ è la distribuzione $P(\cdot\mid a)$. La figura mostra le 30 righe e colonne dei caratteri più frequenti (spazio `␣`, poi `e a i o n r l t s c d \n u m p , v ' g h f . q b z ; í : »`), con scala di blu da 0 (bianco) a 1 (blu scuro). Ogni riga completa somma a 1 su tutto il vocabolario; qui se ne vede solo una parte, quindi le righe visibili possono sommare a meno di 1. Che cosa si legge:

- la **colonna dello spazio** (prima a sinistra) è azzurra per le vocali `e a i o`: in italiano le parole finiscono quasi sempre in vocale; è scura per `í` (*sí*, *piú*: dopo `í` viene lo spazio nel 78% dei casi) e per `,` e `:`;
- le **celle quasi nere** sono i successori quasi deterministici: `.` → `\n` (il punto chiude quasi sempre il verso), `q` → `u` (2.661 su 2.661 nel training: probabilità 1), `;` → `\n`; più chiare `h` → `e` (55%: *che*), `c` → `h`, `»` → `.`;
- consonanti seguite da vocali (righe `t s c d m p v b z` con le colonne `e a i o` azzurre) e la riga `\n` con lo spazio: dopo un a capo viene il rientro di due spazi della terzina successiva.

Il **sanity check** (celle 16-17) somma la riga di `t`: 1,0000000000000002, cioè 1 a meno dell'errore di arrotondamento in virgola mobile. È la proprietà $\sum_b P(b\mid a)=1$ che la MLE garantisce per costruzione per ogni contesto visto.

### Notebook 7 · Generare: greedy contro campionamento

```python
def sample_from_counter(counter, rng):
    return rng.choices(list(counter.keys()), weights=list(counter.values()), k=1)[0]

def generate_ngram(table, order=2, max_new_tokens=400, seed=42, greedy=False, start=None):
    ...
        ctx = tuple(output[-history:])          # gli ultimi n-1 caratteri generati
        counts = table.get(ctx)
        if not counts: break                    # contesto mai visto: il modello non sa che dire
        nxt = counts.most_common(1)[0][0] if greedy else sample_from_counter(counts, rng)
```

Output:

```text
GREEDY BIGRAM:
Co che che che che che che che che che ... che ch

SAMPLED BIGRAM:
Co el'a sto migi luituni de TOrtto NTE ntosuo oncesvirer  e.
pre lli
co quò,
...
```

Il modello definisce probabilità; la **politica di decodifica** decide come usarle. Due politiche: **greedy** (sempre il carattere più probabile, `most_common(1)`) e **campionamento** (estrarre a caso secondo la distribuzione, [scheda 37 della L4](L04-modelli-linguistici-n-gram.md#p-37); i conteggi fanno da pesi perché sono proporzionali alle probabilità MLE). La generazione parte dai primi $n-1$ caratteri del training (`C` di *CANTO*), guarda la riga del contesto, sceglie, aggiunge, sposta il contesto di uno e ripete.

**Perché il greedy si blocca su "che che che"?** Perché con un contesto di un carattere la scelta greedy è una funzione deterministica del carattere corrente, e una funzione su un insieme finito prima o poi entra in un ciclo. Qui: `C` → `o` (34%) → spazio (29%) → `c` (10,5%, la lettera più frequente a inizio parola) → `h` (32%) → `e` (55%) → spazio (35%) → `c`... Il ciclo *␣che* si ripete per sempre. Il campionamento invece produce testo vario: parole spezzate, ma frequenze di lettere, spazi, a capo e apostrofi plausibili.

**Mini-esperimento (cella 21): il seed cambia la distribuzione?** No: la tabella è fissata dal training; il seed cambia solo la **traiettoria** campionata. Tre seed danno tre testi diversi dallo stesso modello.

### Notebook 8 · PLACE YOUR BETS #2: trigram, 5-gram, 9-gram

```python
orders = [1, 2, 3, 5, 9]
ngram_tables = {n: build_ngram_table(train_ids, order=n) for n in orders}
for n in [2, 3, 5, 9]:
    print(generate_ngram(ngram_tables[n], order=n, max_new_tokens=260, seed=8))
```

Output:

```text
3-GRAM SAMPLE
CANTO Sacetto ar carti pe
che lo i la guai qualmestesche no da non so
...
5-GRAM SAMPLE
CANTO SECONDO
  Questa atto tre piango triema lago viver lo noi lor pastoro
...
9-GRAM SAMPLE
CANTO PRIMO

  Nel mezzo del carcere, e io li tenne, invaghito
che questa grande ardore;
...
```

Un modello di ordine $n$ usa i $n-1$ caratteri precedenti: $P(x_t\mid x_{&lt;t})\approx P(x_t\mid x_{t-n+1},\ldots,x_{t-1})$. Più contesto rende le previsioni molto più specifiche, ma i contesti si **frammentano**: stringhe esatte più lunghe ricorrono meno spesso. È la versione a caratteri delle slide *Shakespeare, dagli unigram ai 4-gram* ([scheda 38 della L4](L04-modelli-linguistici-n-gram.md#p-38)).

I campioni lo mostrano bene: il 2-gram fa sillabe; il 3-gram parole brevi vere (*che*, *la*, *non*) e l'intestazione *CANTO*; il 5-gram parole quasi tutte vere, il rientro delle terzine e un *CANTO SECONDO* corretto; il 9-gram comincia con *Nel mezzo del* e poi devia (*carcere*), con versi che sono collage di pezzi del poema: sta **copiando** il training, come i 4-gram di Shakespeare della [scheda 43 della L4](L04-modelli-linguistici-n-gram.md#p-43).

**Risposte alle scommesse #2** (verificate nel blocco successivo): (1) la **training cross-entropy** più bassa la ha il 9-gram, se non si fa smoothing (MLE: 0,303 nats contro 2,358 del bigram); con add-0,1 il quadro si complica, perché lo smoothing pesa molto sui contesti visti una volta sola (1,873 contro 1,525 del 5-gram). (2) La migliore in **validazione** non è né il bigram né il 9-gram ma il 5-gram (1,767). (3) I **contesti mai visti** li incontra più spesso il 9-gram: il 52,7% delle posizioni di validazione ha un contesto di 8 caratteri mai comparso nel training.

### Notebook 9 · Cross-entropy e perplexity su testo held-out

```python
class CountCharNGramLM:
    def prob(self, tok, ctx):
        ctx = tuple(ctx[-history:]) if history else tuple()
        c = self.table[ctx][tok]; total = self.context_totals[ctx]
        if self.alpha == 0:
            return c / total if total else 0.0                  # MLE
        return (c + self.alpha) / (total + self.alpha * self.V)  # add-k
    def evaluate(self, ids):
        ...  logp += math.log(p) ...
        ce = -logp / N
        return ce, math.exp(ce), coverage, 0
```

Output:

```text
   order  alpha  contexts  train_CE    val_CE    val_PPL  val_context_coverage  zero_prob_events
0      1    0.0         1  3.058706  3.050435  21.124531   1.000000      0
1      1    0.1         1  3.058706  3.050438  21.124589   1.000000      0
2      2    0.0        77  2.357717       inf        inf   1.000000     12
3      2    0.1        77  2.358542  2.348047  10.465109   1.000000      0
4      3    0.0      1159  1.904110       inf        inf   0.999776    176
5      3    0.1      1159  1.915891  1.921970   6.834406   0.999776      0
6      5    0.0     32248  1.276109       inf        inf   0.979494   4087
7      5    0.1     32248  1.524782  1.767016   5.853362   0.979494      0
8      9    0.0    349208  0.302986       inf        inf   0.473198  36018
9      9    0.1    349208  1.872804  3.503442  33.229632   0.473198      0
```

La **cross-entropy** di un modello su un testo di $N$ token predetti è la media del log-probabilità negativo dei token effettivamente comparsi, e la **perplexity** ne è l'esponenziale:

$$H=-\frac1N\sum_{i=1}^{N}\ln P(x_i\mid\text{context}_i),\qquad \text{PPL}=e^{H}$$

Più bassa è meglio. La L5 usa $\log_2$ (bit, $\text{PPL}=2^H$, [scheda 39 della L5](L05-smoothing-ed-entropia.md#p-39)); qui, come in PyTorch e in J&M §7.7.1, si usa il logaritmo naturale: **nats**. La perplexity è lo stesso numero in entrambi i casi, cambia solo l'unità di $H$: $H_\text{bit}=H_\text{nat}/\ln 2$.

Il problema dei modelli non lisciati: un evento mai visto ha probabilità 0 e $-\ln 0=\infty$ (gli *zeri* della [scheda 46 della L4](L04-modelli-linguistici-n-gram.md#p-46)). Per questo la classe `CountCharNGramLM` calcola anche la **coverage** (frazione di posizioni il cui contesto esatto compare nel training) e una versione con **add-$\alpha$**, che è l'add-$k$ della [scheda 21 della L5](L05-smoothing-ed-entropia.md#p-21): $P(b\mid a)=\dfrac{C(ab)+\alpha}{C(a)+\alpha V}$; $\alpha=1$ è Laplace, $\alpha=0$ la MLE, e un contesto mai visto riceve la distribuzione uniforme $1/V$.

Lettura della tabella:

- con $\alpha=0$ basta un evento impossibile per avere perplexity infinita: già il bigram ne ha 12 in validazione (coppie mai viste come `sú`, `ít`, `[n`), il 9-gram 36.018;
- la **training CE MLE** scende monotonamente (3,06 → 2,36 → 1,90 → 1,28 → 0,30): più contesto esatto, più memoria;
- la **validation CE lisciata** scende fino al 5-gram (PPL 5,85) e poi risale bruscamente con il 9-gram (PPL 33,2, peggio dell'unigram!);
- la **coverage** crolla al 47% per il 9-gram;
- l'unigram ha quasi la stessa CE su train e validazione (3,059 e 3,050): non può andare in overfitting perché non guarda il contesto.

> **Attenzione (errore nelle slide): La colonna contexts conta anche i contesti della validazione**
>
> La colonna `contexts` viene calcolata come `len(lm.table)` *dopo* aver chiamato `evaluate` sul training e sulla validazione. Ma `prob` legge `self.table[ctx][tok]`, e `table` è un `defaultdict(Counter)`: leggere un contesto mai visto lo **inserisce** nella tabella con un Counter vuoto. Così ogni contesto nuovo incontrato in validazione gonfia il conteggio. I contesti distinti davvero presenti nel training sono **1.149** (trigram), **31.239** (5-gram) e **321.762** (9-gram), non 1.159, 32.248 e 349.208: le differenze (10, 1.009 e 27.446) sono esattamente i contesti di validazione assenti dal training. Verificato contando con un `set` le tuple di contesto di training e di validazione. Le probabilità, le CE e la coverage non sono toccate (`context_totals` è un `Counter`, che in lettura non inserisce nulla). Correzione: leggere con `self.table.get(ctx, {}).get(tok, 0)`, oppure calcolare `contexts` prima di valutare.

### Notebook 10 · Che cosa è successo: fit, overfitting e coverage

```python
plot_df = results_df[results_df["alpha"] == 0.1]
axes[0].plot(plot_df["order"], plot_df["train_CE"], marker="o", label="train")
axes[0].plot(plot_df["order"], plot_df["val_CE"], marker="o", label="validation")
axes[1].plot(plot_df["order"], plot_df["val_context_coverage"], marker="o")
```

Due grafici sui modelli lisciati ($\alpha=0{,}1$), con l'ordine $n$ in ascissa (1, 2, 3, 5, 9). **A sinistra** la cross-entropy in nats per carattere: le curve di training (blu) e validazione (arancio) sono sovrapposte per $n=1,2,3$ (3,06; 2,35; 1,92), si separano al 5-gram (1,52 contro 1,77, minimo della validazione) e divergono al 9-gram (1,87 contro 3,50). **A destra** la coverage: 1 fino al trigram, 0,98 al 5-gram, 0,47 al 9-gram.

Tre effetti: (1) il **fit di training** migliora con il contesto (nella versione MLE in modo monotono); (2) la **coverage cala** perché molti contesti lunghi di validazione non sono mai stati visti esattamente; (3) senza smoothing un solo evento impossibile rende la perplexity infinita. Il divario fra le curve è **overfitting**: il 9-gram ricorda il training ma non generalizza ([scheda 43 della L4](L04-modelli-linguistici-n-gram.md#p-43)).

Perché anche la training CE lisciata del 9-gram risale (1,87 > 1,52)? Perché la maggior parte dei contesti di 8 caratteri è stata vista una o due volte: per un contesto visto una volta, add-0,1 dà al successore osservato $(1+0{,}1)/(1+0{,}1\cdot 77)=1{,}1/8{,}7=0{,}126$ invece di 1, cioè $-\ln 0{,}126=2{,}07$ nats. Con $V=77$ la massa $\alpha V=7{,}7$ è enorme rispetto ai conteggi: è lo stesso problema di Laplace della [scheda 19 della L5](L05-smoothing-ed-entropia.md#p-19) (troppa massa agli zeri). Un $\alpha$ diverso per ogni ordine, o l'interpolazione/backoff della [L5](L05-smoothing-ed-entropia.md#p-24), farebbe molto meglio.

> **Approfondimento: Il 9-gram con backoff batterebbe il 5-gram?**
>
> L'add-$\alpha$ tratta un contesto mai visto con la distribuzione uniforme: per il 9-gram, metà delle posizioni di validazione riceve $1/77$ per qualunque carattere, cioè $\ln 77=4{,}34$ nats, peggio dell'unigram. Una **interpolazione** ([scheda 24 della L5](L05-smoothing-ed-entropia.md#p-24)) o uno **stupid backoff** ([scheda 27](L05-smoothing-ed-entropia.md#p-27)) ripiegherebbero sull'8-gram, il 7-gram e così via, fino a un contesto visto: è proprio il motivo per cui nei sistemi n-gram veri (KenLM, Kneser-Ney modificato) ordini alti non fanno danni. Il notebook usa solo add-$\alpha$ per tenere il codice minimo, quindi "il 5-gram è il migliore" vale *per questo smoothing*, non per gli n-gram in generale.

### Notebook 11 · Autopsia delle probabilità: dove sbaglia il 5-gram

```python
def surprisal_table(lm, ids, start=0, length=120):
    ...
        p = lm.prob(tok, ctx)
        rows.append({"context": repr(decode(ctx)), "observed_next": repr(itos[tok]),
                     "probability": p, "surprisal_bits": -math.log2(p),
                     "context_seen": tuple(ctx) in lm.context_totals})
autopsy = surprisal_table(models[(5, 0.1)], val_ids, start=50, length=120)
autopsy.sort_values("surprisal_bits", ascending=False).head(15)
```

Output:

```text
    context observed_next  probability  surprisal_bits  context_seen
79   'come'           't'     0.000189       12.370960          True
115  'orïo'           'l'     0.004608        7.761551          True
53   'mman'           'd'     0.006803        7.199672          True
114  "'orï"           'o'     0.007874        6.988685          True
57   'do, '           'v'     0.008166        6.936103          True
80   'omet'           'e'     0.008547        6.870365          True
117  'ïoli'          '\n'     0.012987        6.266787         False
116  'rïol'           'i'     0.012987        6.266787         False
81   'mete'           '.'     0.012987        6.266787         False
...
```

Una media può nascondere dove un modello fallisce: `surprisal_table` guarda le singole previsioni. La **surprisal** $-\log_2 p$ misura la sorpresa in bit: 0 bit = certezza, 1 bit = moneta fra due caratteri, $\log_2 77=6{,}27$ bit = tiro a caso fra tutti i caratteri. La media delle surprisal su un testo è esattamente la cross-entropy in bit.

Le 15 previsioni peggiori del 5-gram lisciato su 120 posizioni di validazione (il passo "a guisa di comete. / E come cerchi in tempra d'orïoli"):

- `'come'` → `t` (12,4 bit, $p=0{,}00019$): il contesto è visto migliaia di volte, ma quasi sempre come parola *come* seguita da spazio; *comete* è un caso raro. Contesto **visto ma ambiguo**: aumentare $n$ non aiuta, serve sapere che si sta leggendo una similitudine astronomica;
- `'ïoli'`, `'rïol'`, `'mete'` (6,27 bit, `context_seen=False`): contesto **mai visto**, quindi distribuzione uniforme, $p=1/77=0{,}012987$, $\log_2 77=6{,}27$ bit: il valore esatto del tiro a caso;
- `'orïo'` → `l`, `'mman'` → `d` (da *fiammando*): contesti visti poche volte con successori diversi.

**Risposte al Discuss:** (1) alcuni contesti difficili sono mai visti (rïol, ïoli), altri visti ma ambigui (come); (2) aumentare $n$ non risolve necessariamente: allunga il contesto, ma aumenta i contesti mai visti; (3) vorremmo una generalizzazione per **somiglianza**: sapere che *orïoli* somiglia a *orïente*, che dopo *come* in una similitudine possono venire molte parole, che contesti diversi possono predire la stessa cosa. È esattamente ciò che danno gli embedding appresi.

### Notebook 12 · Il muro degli n-gram e PLACE YOUR BETS #3

```python
for h in [1, 2, 4, 8, 16, 32, 64]:
    log10_contexts = h * math.log10(vocab_size)    # log10(V^h) = h log10 V
    print(f"history={h:2d}  possible contexts ≈ 10^{log10_contexts:.1f}")
```

Output:

```text
history= 1  possible contexts ≈ 10^1.9
history= 2  possible contexts ≈ 10^3.8
history= 4  possible contexts ≈ 10^7.5
history= 8  possible contexts ≈ 10^15.1
history=16  possible contexts ≈ 10^30.2
history=32  possible contexts ≈ 10^60.4
history=64  possible contexts ≈ 10^120.7
```

Con $V$ simboli, una tabella a contesto esatto con storia $h$ ha fino a $V^h$ contesti possibili: $\log_{10}V^h=h\log_{10}77=1{,}886\,h$. Con $h=8$ (9-gram) sono $10^{15{,}1}$, con $h=64$ $10^{120{,}7}$, più degli atomi dell'universo osservabile (circa $10^{80}$). Il training ha solo 481.925 posizioni, quindi può contenere al più circa $4{,}8\cdot10^5$ contesti distinti: per $h=8$ ne compaiono 321.762, una frazione infinitesima ($3\cdot 10^{-10}$) di quelli possibili.

La L5 chiude con lo stesso argomento per le parole: con il $V=29.066$ di Shakespeare ci sono $V^2\approx 845$ milioni di bigram possibili ([scheda 42 della L5](L05-smoothing-ed-entropia.md#p-42)). **Troppi parametri e nessuna generalizzazione**: ciò che un n-gram impara su un contesto non dice nulla su un contesto simile.

**Scommessa #3: perché non un 65-gram?** Una tabella indicizzata da ogni storia esatta di 64 caratteri non è solo enorme: quasi ogni contesto di validazione sarebbe nuovo (già con 8 caratteri lo è il 53%), quindi la tabella darebbe la distribuzione uniforme quasi ovunque. La domanda giusta è un'altra: un modello può imparare che contesti diversi sono **statisticamente collegati**, invece di trattare ogni stringa diversa come un oggetto a sé? È il ponte verso le rappresentazioni apprese della [scheda 43 della L13](L13-reti-neurali.md#p-43) (forza statistica condivisa).

Commento al notebook del corso `HLT-2026-27-L16-Language_Models_from_counting_characters_to_GPT.ipynb` (il notebook è del docente e non è incluso).

Seconda parte guidata (celle 36-73): stesso casinò, rappresentazioni apprese. Si costruisce pezzo per pezzo un **piccolo GPT** nello stile di nanoGPT (Karpathy), con ogni classe messa in corrispondenza con la figura del transformer della [L14](L14-transformer-l-attenzione.md#p-7) (J&M Fig. 7.16): una testa di attenzione causale, la multi-head attention, il feedforward, il blocco prenorm con la residual stream, il modello completo con embedding di token e di posizione, layer norm finale e testa di language modeling. Poi lo si addestra con AdamW sullo stesso obiettivo (cross-entropy sul carattere successivo), lo si confronta con gli n-gram sulla stessa validazione e si gioca con la temperatura.

Iperparametri: $d=96$, $A=4$ teste da $d_k=24$, $L=2$ blocchi, contesto $N=64$ caratteri, batch di 24 finestre, dropout 0,1: **244.301 parametri**. Gli output salvati vengono da un'esecuzione su **CPU**, quindi con il budget ridotto di **500 passi** (su GPU il notebook ne fa 5.000): il GPT arriva a 2,23 nats in validazione e **perde** contro il 5-gram (1,77), come il notebook stesso avverte. Nella mia riesecuzione (PyTorch 2.14 su CPU, stesso seed, stessi 500 passi) tutti i numeri e i testi generati di questa parte coincidono con quelli salvati.

### Notebook 1 · Lo stesso obiettivo: finestre e target spostati di uno

```python
batch_size = 24      # B: finestre per minibatch
block_size = 64      # T: la finestra di contesto (N nelle slide)
def get_batch(split_name):
    source = train_tensor if split_name == "train" else val_tensor
    ix = torch.randint(len(source) - block_size - 1, (batch_size,))
    x = torch.stack([source[i:i+block_size] for i in ix])        # [B, T]
    y = torch.stack([source[i+1:i+block_size+1] for i in ix])    # [B, T] spostati di uno
    return x.to(device), y.to(device)
```

Output:

```text
Input shape: torch.Size([24, 64])
Target shape: torch.Size([24, 64])

input : 'ngo la grotta assiso».\n  Allora piú che prima li occhi apersi;\ng'
target: 'go la grotta assiso».\n  Allora piú che prima li occhi apersi;\ngu'
```

Per GPT le coppie input/target si ottengono spostando il testo di un carattere: `input H E L L`, `target E L L O`. Il modello stima ancora $P(x_t\mid x_{&lt;t})$: cambia solo come il contesto è rappresentato e come le probabilità sono apprese.

Una finestra di `block_size` caratteri dà **64 esempi di training insieme**: in ogni posizione $t$ il modello vede $x_{\le t}$ e deve predire $x_{t+1}$, cioè `y[b, t]` è il target del prefisso `x[b, :t+1]`. È la figura *Tutta la finestra di contesto* della [scheda 9 della L14](L14-transformer-l-attenzione.md#p-9) e il **teacher forcing** di J&M §7.7: in training il modello riceve sempre la storia vera, mai le proprie previsioni. Nell'esempio stampato si vede bene: la riga `target` è la riga `input` senza la prima lettera e con una lettera in più in fondo (`gu`, inizio di *guardai*).

`get_batch` pesca 24 posizioni di partenza casuali e impila le finestre: tensori di forma `[B, T] = [24, 64]` di id interi (`torch.long`). Il limite `len(source) - block_size - 1` garantisce che anche il target, che arriva un carattere più in là, stia dentro il testo (è prudente di uno: l'ultima finestra possibile non viene mai estratta, cosa del tutto irrilevante).

### Notebook 2 · Una baseline onesta: il caso uniforme

```python
uniform_ce = math.log(vocab_size)       # -log(1/V)
print(f"Uniform-random cross-entropy: {uniform_ce:.3f} nats/character")
print(f"Uniform-random perplexity:    {math.exp(uniform_ce):.1f}")
```

Output:

```text
Uniform-random cross-entropy: 4.344 nats/character
Uniform-random perplexity:    77.0
```

Un modello che dà la stessa probabilità $1/V$ a ogni carattere ha cross-entropy $-\ln(1/V)=\ln V=\ln 77=4{,}344$ nats e perplexity esattamente $V=77$: la perplexity come **fattore di ramificazione** della [scheda 34 della L4](L04-modelli-linguistici-n-gram.md#p-34) (con scelte equiprobabili la perplexity è il numero di scelte). È il punto di riferimento comune: una rete non addestrata deve partire lì vicino, e ogni modello utile deve stare sotto. Per confronto, l'unigram sta a 3,05 (PPL 21,1) e il 5-gram lisciato a 1,77 (PPL 5,85): dopo aver visto 4 caratteri, l'incertezza sul successivo equivale a scegliere fra circa 6 caratteri equiprobabili.

### Notebook 3 · La configurazione e la mappa figura-codice

```python
@dataclass
class GPTConfig:
    vocab_size: int          # |V|
    block_size: int = 64     # N: lunghezza massima del contesto
    n_embd: int = 96         # d: dimensione del modello (larghezza della residual stream)
    n_head: int = 4          # A: teste per strato
    n_layer: int = 2         # L: blocchi
    dropout: float = 0.1
```

Output:

```text
GPTConfig(vocab_size=77, block_size=64, n_embd=96, n_head=4, n_layer=2, dropout=0.1)
```

La pipeline: **id dei token → embedding di token + embedding di posizione → $L$ transformer block → logit sullo stesso vocabolario di caratteri**, cioè la figura *Un token attraverso il transformer* della [L14 (schede 6-8)](L14-transformer-l-attenzione.md#p-6), J&M Fig. 7.16. Il notebook la riproduce e affianca una tabella che conviene tenere a mente per l'orale:

| Figura | Codice | Forma |
| --- | --- | --- |
| token in input | `idx` | `[B, T]` |
| embedding $E$ | `token_embedding` | `[B, T, d]` |
| posizioni $E_{pos}$ | `position_embedding` | `[T, d]` |
| ingresso nella residual stream | `x = tok + pos` | `[B, T, d]` |
| blocco ripetuto $L$ volte | `blocks` |  |
| layer norm, MHA, somma | `x = x + attn(ln1(x))` | `[B, T, d]` |
| layer norm, FFN, somma | `x = x + ffwd(ln2(x))` | `[B, T, d]` |
| layer norm finale | `ln_f` |  |
| unembedding $U$ | `lm_head` | `[B, T, V]` |
| softmax | `F.softmax` in `generate`, dentro `F.cross_entropy` nel training | `[B, T, V]` |

Nomi: $d$ = `n_embd` = 96, $A$ = `n_head` = 4, $d_k=d_v=d/A$ = 24, $L$ = `n_layer` = 2, $N$ = `block_size` = 64. PyTorch aggiunge davanti a tutto la dimensione del **batch** $B$: la matrice $X$ $[N\times d]$ di J&M §7.3 diventa un tensore `[B, T, d]`, una $X$ per finestra. A differenza di una tabella n-gram, il modello non ha una riga per ogni stringa esatta di 64 caratteri: impara rappresentazioni numeriche riutilizzabili.

### Notebook 4 · Una testa di attenzione causale

```python
class Head(nn.Module):
    def __init__(self, head_size, config):
        self.key   = nn.Linear(config.n_embd, head_size, bias=False)   # W^K
        self.query = nn.Linear(config.n_embd, head_size, bias=False)   # W^Q
        self.value = nn.Linear(config.n_embd, head_size, bias=False)   # W^V
        self.register_buffer("tril", torch.tril(torch.ones(config.block_size, config.block_size)))
    def forward(self, x):
        B, T, C = x.shape
        k = self.key(x); q = self.query(x)                                 # [B, T, d_k]
        weights = q @ k.transpose(-2, -1) * (k.size(-1) ** -0.5)           # [B, T, T]
        weights = weights.masked_fill(self.tril[:T, :T] == 0, float("-inf"))
        weights = F.softmax(weights, dim=-1)
        weights = self.dropout(weights)
        v = self.value(x)
        return weights @ v                                                  # [B, T, d_v]
```

`Head` è la testa di attenzione della L14 calcolata per **tutti i token insieme**, nella forma matriciale di J&M §7.3 ([scheda 59 della L14](L14-transformer-l-attenzione.md#p-59)):

$$Q=XW^Q,\quad K=XW^K,\quad V=XW^V,\qquad \text{head}=\operatorname{softmax}\!\Big(\operatorname{mask}\Big(\frac{QK^\top}{\sqrt{d_k}}\Big)\Big)V$$

I passi numerati nei commenti del codice sono quelli di *Calcolare $a_3$ passo per passo* ([schede 26-28 della L14](L14-transformer-l-attenzione.md#p-26)): (1) query, key e value per proiezione; (2) un solo prodotto matriciale `q @ k.transpose(-2, -1)` dà tutti i confronti query-key, una matrice `[T, T]` per finestra ([scheda 55](L14-transformer-l-attenzione.md#p-55)); (3) divisione per $\sqrt{d_k}=\sqrt{24}$; maschera; (4) softmax per riga, i pesi $\alpha_{ij}$; (5)-(6) somma pesata dei value.

La **maschera** è la matrice triangolare inferiore `tril` (1 sulla diagonale e sotto): `masked_fill(tril == 0, -inf)` mette $-\infty$ sui confronti con token futuri, così la softmax dà loro peso $e^{-\infty}=0$: è esattamente $QK^\top+M$ della [scheda 56 della L14](L14-transformer-l-attenzione.md#p-56). `self.tril[:T, :T]` ritaglia la maschera quando la finestra è più corta di 64 (in generazione, all'inizio).

Due dettagli di PyTorch: `nn.Linear(d, d_k, bias=False)` calcola $xW^\top$ e memorizza un peso di forma `[d_k, d]`, quindi la $W^Q$ $[d\times d_k]$ delle slide è `self.query.weight.T` (stessa funzione, memoria trasposta); `register_buffer` salva `tril` dentro il modulo (si sposta sulla GPU con lui) senza farne un parametro addestrabile. Il dropout sui pesi di attenzione azzera a caso alcune connessioni durante il training.

### Notebook 5 · Multi-head attention: teste in parallelo, concatenazione, W^O

```python
class MultiHeadAttention(nn.Module):
    def __init__(self, config):
        head_size = config.n_embd // config.n_head                         # d_k = d_v = d / A
        self.heads = nn.ModuleList([Head(head_size, config) for _ in range(config.n_head)])
        self.proj = nn.Linear(config.n_embd, config.n_embd)                 # W^O
    def forward(self, x):
        x = torch.cat([head(x) for head in self.heads], dim=-1)             # [B, T, A*d_v]
        return self.dropout(self.proj(x))                                   # [B, T, d]
```

$A=4$ teste in parallelo, ognuna con le sue $W^Q,W^K,W^V$; le uscite, $[1\times d_v]$ ciascuna, sono **concatenate** in $[1\times Ad_v]$ e riproiettate in $[1\times d]$ da $W^O$ ([schede 37-39 della L14](L14-transformer-l-attenzione.md#p-37)). Con $d_v=d/A=24$, $Ad_v=96=d$ e $W^O$ è quadrata $d\times d$. Nel codice: `self.heads` sono i quattro trapezi della figura, `torch.cat(..., dim=-1)` è *Concatenate Outputs*, `self.proj` è $W^O$ (qui con bias). Il ciclo Python sulle teste è leggibile ma lento: l'esercizio 3 lo sostituirà con un unico prodotto matriciale.

### Notebook 6 · Il feedforward position-wise

```python
class FeedForward(nn.Module):
    def __init__(self, config):
        self.net = nn.Sequential(
            nn.Linear(config.n_embd, 4 * config.n_embd),   # W1, b1: d -> 4d
            nn.GELU(),
            nn.Linear(4 * config.n_embd, config.n_embd),   # W2, b2: 4d -> d
            nn.Dropout(config.dropout))
```

Una rete con uno strato nascosto di dimensione $d_{ff}=4d=384$, applicata a **ogni posizione indipendentemente** (*position-wise*: non mescola mai i token, lo fa solo l'attenzione; [scheda 46 della L14](L14-transformer-l-attenzione.md#p-46)). Contiene la maggior parte dei parametri del blocco: qui 74.208 su 111.552. La L14 la scrive con ReLU; i GPT usano **GELU**, una versione liscia della ReLU ([scheda 15 della L13](L13-reti-neurali.md#p-15)); gli LLM moderni la variante con gate SwiGLU ([scheda 47 della L14](L14-transformer-l-attenzione.md#p-47)).

### Notebook 7 · Il blocco prenorm e la residual stream

```python
class Block(nn.Module):
    def __init__(self, config):
        self.ln1 = nn.LayerNorm(config.n_embd); self.attn = MultiHeadAttention(config)
        self.ln2 = nn.LayerNorm(config.n_embd); self.ffwd = FeedForward(config)
    def forward(self, x):
        x = x + self.attn(self.ln1(x))     # O = X + MHA(LN(X))   (mescola i token)
        x = x + self.ffwd(self.ln2(x))     # H = O + FFN(LN(O))   (per posizione)
        return x
```

Il blocco **prenorm** della L14 ([scheda 50](L14-transformer-l-attenzione.md#p-50)), J&M Eq. 7.39-7.40:

$$O=X+\text{MultiHeadAttention}(\text{LayerNorm}(X)),\qquad H=O+\text{FFN}(\text{LayerNorm}(O))$$

Le due righe di `forward` sono le due equazioni: ogni componente **legge** dalla residual stream `x` (dopo averla normalizzata) e **aggiunge** il suo risultato ([scheda 43](L14-transformer-l-attenzione.md#p-43)). Ingresso e uscita hanno la stessa forma `[B, T, d]`, quindi i blocchi si impilano ([scheda 52](L14-transformer-l-attenzione.md#p-52)). `nn.LayerNorm` ha guadagno $\gamma$ e offset $\beta$ appresi ([scheda 49](L14-transformer-l-attenzione.md#p-49)). Le connessioni residue sono quelle della [scheda 67 della L13](L13-reti-neurali.md#p-67): il gradiente passa dalla somma senza attenuarsi.

### Notebook 8 · Esercizio veloce: la maschera causale

```python
torch.tril(torch.ones(8, 8, dtype=torch.int))          # 1 = consentito
torch.tril(torch.ones(8, 8, dtype=torch.int)) == 0     # True = futuro, da mascherare
scores = torch.rand(8, 8)
masked_scores = scores.masked_fill(torch.tril(torch.ones(8, 8, dtype=torch.int)) == 0, float("-inf"))
weights = F.softmax(masked_scores, dim=-1)
```

Output:

```text
tensor([[1.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
        [0.4817, 0.5183, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
        [0.3702, 0.4107, 0.2190, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000],
        [0.3209, 0.2785, 0.2637, 0.1370, 0.0000, 0.0000, 0.0000, 0.0000],
        [0.1490, 0.2601, 0.1449, 0.2430, 0.2030, 0.0000, 0.0000, 0.0000],
        ...
        [0.1851, 0.1236, 0.1130, 0.1020, 0.1493, 0.1288, 0.1198, 0.0784]])
```

La matrice `tril` per $T=8$: 1 sulla diagonale e sotto. `tril == 0` è la maschera booleana dei posti da riempire con $-\infty$ (il triangolo superiore). Poi si applica a punteggi casuali e si fa la softmax per riga: ogni riga somma a 1 e ha zeri sopra la diagonale. La prima riga è $[1,0,\ldots,0]$: la posizione 0 può guardare solo se stessa. Ho ricalcolato le softmax con NumPy dai punteggi stampati: coincidono (ad esempio riga 1: $1/(1+e^{0{,}3677-0{,}2944})=0{,}4817$).

**Risposte.** (1) *Riga 4*: contando da 0, come stampa PyTorch, la riga 4 è `[1, 1, 1, 1, 1, 0, 0, 0]`, quindi sono visibili le posizioni 0, 1, 2, 3, 4 (la posizione stessa e le quattro precedenti); le posizioni 5, 6, 7 sono future. (2) *Senza maschera il training non ha senso*: il target di posizione $t$ è `y[t] = x[t+1]`, cioè il carattere che sta **dentro l'input** alla posizione successiva. Senza maschera la posizione $t$ può guardare $x_{t+1}$ e copiarlo: la loss crolla verso 0 senza che il modello impari a predire nulla, e in generazione, dove il futuro non esiste, il modello è inutile. L'ablazione *no causal mask (cheating!)* dell'esercizio 2 lo mostra con i numeri.

### Notebook 9 · TinyGPT: il modello completo e la loss iniziale

```python
class TinyGPT(nn.Module):
    def __init__(self, config):
        self.token_embedding = nn.Embedding(config.vocab_size, config.n_embd)      # E
        self.position_embedding = nn.Embedding(config.block_size, config.n_embd)   # E_pos
        self.blocks = nn.Sequential(*[Block(config) for _ in range(config.n_layer)])
        self.ln_f = nn.LayerNorm(config.n_embd)
        self.lm_head = nn.Linear(config.n_embd, config.vocab_size)                 # U
        self.apply(self._init_weights)     # N(0, 0.02), bias a zero
    def forward(self, idx, targets=None):
        x = self.token_embedding(idx) + self.position_embedding(torch.arange(T))
        x = self.ln_f(self.blocks(x)); logits = self.lm_head(x)                    # [B, T, |V|]
        loss = F.cross_entropy(logits.reshape(B*T, V), targets.reshape(B*T))
    @torch.no_grad()
    def generate(self, idx, max_new_tokens, temperature=1.0, top_k=None):
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -self.config.block_size:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :] / max(float(temperature), 1e-5)
            ... top-k ...
            nxt = torch.multinomial(F.softmax(logits, dim=-1), 1)
            idx = torch.cat([idx, nxt], dim=1)
```

Output:

```text
Parameters: 244,301
Initial minibatch loss: 4.377
Uniform baseline:       4.344
```

`TinyGPT` monta i pezzi dal basso in alto: (1) **input encoding**, embedding del token più embedding della posizione (J&M §7.4), con posizioni **assolute e apprese**, $E_{pos}$ $[N\times d]$, come nel GPT originale (i modelli moderni preferiscono RoPE); (2) i $L$ blocchi; (3) un layer norm finale; (4) la **testa di language modeling** (J&M §7.5, [scheda 8 della L14](L14-transformer-l-attenzione.md#p-8)): l'unembedding `lm_head` porta ogni vettore da $d$ a $|V|$ logit. Qui $U$ è una matrice separata con bias, non il *weight tying* $U=E^\top$ del libro.

`forward` calcola anche la loss: la cross-entropy in ogni posizione, mediata sulle $B\times T=1536$ posizioni del batch (J&M Eq. 7.55). `F.cross_entropy` riceve i logit grezzi e applica la softmax (in forma log-softmax, numericamente stabile) al suo interno. `generate` è la **decodifica autoregressiva** (J&M §7.6): taglia il contesto agli ultimi 64 token, ricalcola tutta la finestra, prende i logit dell'**ultima** posizione, li divide per la temperatura, applica l'eventuale top-$k$, campiona con `torch.multinomial`, accoda e ripete.

**Discuss: perché la loss iniziale è così vicina alla baseline uniforme?** `_init_weights` inizializza tutti i pesi con $\mathcal N(0;0{,}02^2)$ e i bias a zero: i logit in uscita sono tutti vicinissimi a 0, la softmax è quasi uniforme e la loss vale circa $\ln 77=4{,}344$ (osservato 4,377). Un'inizializzazione più grande darebbe logit sbilanciati a caso e una loss iniziale più alta, cioè passi di training sprecati a "disimparare" la sicurezza ingiustificata.

**Dove stanno i 244.301 parametri?** (conto completo negli esercizi) Per blocco: attenzione $3\cdot 96\cdot 96$ ($W^Q,W^K,W^V$ delle 4 teste, senza bias) $+\,96\cdot96+96$ ($W^O$) $=36.960\approx 4d^2=36.864$; feedforward $96\cdot384+384+384\cdot96+96=74.208\approx 8d^2=73.728$; due layer norm $4\cdot96=384$. Totale per blocco 111.552, due blocchi 223.104 (91%). Poi $E$ $77\cdot96=7.392$, $E_{pos}$ $64\cdot96=6.144$, `ln_f` 192, `lm_head` $96\cdot77+77=7.469$. I conti del notebook ($4d^2$ e $8d^2$, [scheda 40 della L14](L14-transformer-l-attenzione.md#p-40)) sono giusti a meno dei bias.

### Notebook 10 · Generare prima del training

```python
start_id = stoi.get("\n", 0)
start = torch.tensor([[start_id]], dtype=torch.long, device=device)   # prompt: un solo a capo, [1, 1]
print(decode(model.generate(start, max_new_tokens=300, temperature=1.0)[0].tolist()))
```

Output:

```text
O]u]uëò'c[n'ý
B .Rtbé!CtNDò ;ixòt.túdíFraN-V-edBml CMüné(;igJcoò]ébaBëúJA»hVdOPcUòcýeju)CR»Hi(x?M llOVf(z- ÈoloF':UhýíýAüÈqMi
...
```

L'equivalente neurale di un casinò senza informazione: con pesi casuali la distribuzione è quasi uniforme e il testo è una zuppa di tutti i 77 simboli, con caratteri rarissimi nel corpus (`ý`, `[`, `Ï`, `J`) frequenti quanto le vocali. Il prompt è un tensore `[1, 1]` con il solo a capo; `[0].tolist()` estrae la prima (e unica) sequenza del batch e la converte in lista di id da decodificare.

### Notebook 11 · Il ciclo di training

```python
optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)
max_steps = 500 if device == "cpu" else 5000
for step in range(max_steps + 1):
    if step % eval_every == 0 or step == max_steps:
        losses = estimate_gpt_loss()               # media su 10 batch, in eval mode
    ...
    xb, yb = get_batch("train")                    # 1. un minibatch casuale
    _, loss = model(xb, yb)                        # 2. forward + cross-entropy
    optimizer.zero_grad(set_to_none=True)          # 3. azzera i gradienti
    loss.backward()                                # 4. backpropagation
    optimizer.step()                               # 5. aggiornamento AdamW
```

Output:

```text
step    0 | train 4.369 | val 4.364
step   50 | train 2.973 | val 2.958
step  100 | train 2.648 | val 2.641
...
step  300 | train 2.365 | val 2.371
step  400 | train 2.312 | val 2.292
step  500 | train 2.255 | val 2.225
```

Si sostituisce la stima per conteggio con l'apprendimento per gradiente. Ogni passo è la ricetta della [scheda 52 della L13](L13-reti-neurali.md#p-52): (1) un minibatch casuale; (2) forward pass e loss; (3) `zero_grad`, perché PyTorch **accumula** i gradienti e quelli del passo precedente vanno dimenticati; (4) `loss.backward()`, la **backpropagation**, regola della catena sul grafo computazionale ([scheda 56 della L13](L13-reti-neurali.md#p-56)), che calcola il gradiente rispetto a tutti i 244.301 parametri, embedding compresi; (5) `optimizer.step()`, l'aggiornamento. L'optimizer è **AdamW**, Adam con weight decay disaccoppiato, lo standard per i modelli linguistici ([schede 61 e 64 della L13](L13-reti-neurali.md#p-61)), con learning rate $3\cdot10^{-4}$.

Ogni 50 passi `estimate_gpt_loss` media la loss su 10 batch casuali di training e di validazione in modalità `eval` (dropout spento, `no_grad`), poi rimette `model.train()`; ai passi 100, 1100, 2100... stampa un campione. Su CPU: 500 passi, cioè $500\cdot 24\cdot 64\approx 768.000$ posizioni viste, circa 1,6 passate sul training. La loss scende da 4,37 a 2,26/2,23 (train/val); il campione al passo 100 ha già spazi, a capo, il rientro e sillabe italiane.

Nella mia riesecuzione su CPU la curva è identica fino al terzo decimale, campione al passo 100 compreso: con seed fisso, training su CPU e stessa sequenza di estrazioni casuali il risultato è deterministico (su GPU non lo sarebbe in generale).

### Notebook 12 · La curva di apprendimento

```python
plt.plot(steps, train_losses, marker="o", label="GPT train")
plt.plot(steps, val_losses, marker="o", label="GPT validation")
plt.axhline(uniform_ce, linestyle="--", label="uniform baseline")
```

Cross-entropy in nats per carattere contro il passo di training, con la baseline uniforme $\ln 77=4{,}34$ tratteggiata. Le due curve partono sulla baseline (passo 0: 4,37 e 4,36), crollano nei primi 50 passi (2,97: il modello impara le frequenze dei caratteri, l'unigram vale 3,05) e poi scendono lentamente fino a 2,26/2,23 al passo 500, ancora in discesa: il modello è lontano dalla convergenza. Train e validazione restano **sovrapposte** (la validazione è addirittura un filo sotto a fine corsa, rumore di stima su 10 batch e dropout acceso solo in training): nessun overfitting, il contrario del 9-gram. Con 244.301 parametri e meno di due passate sui dati, il problema del modello è l'*underfitting*.

### Notebook 13 · Generare dopo il training

```python
sample = model.generate(start, max_new_tokens=800, temperature=0.8, top_k=30)
print(decode(sample[0].tolist()))
```

Output:

```text
  cunosirra que si cagallla va sí olorten iú pusero, gl di tolertre.
  Or me quepi dinol somomo cn fbelue cutodi
ssenno an di scala sí sespono vulla
si condaele pa titosto  perunota,
ch'a calali lli finta sto saltgi,
...
```

Il notebook invita a cercare strati di struttura appresa, non a chiedersi solo "sembra Dante?": frequenze dei caratteri (giuste), spazi e punteggiatura (virgole e punti a fine verso), maiuscole (rare, a inizio verso: *Or*), **a capo** con versi di lunghezza plausibile, il **rientro di due spazi** a inizio terzina, frammenti di parole e parole vere brevi (*che*, *di*, *sí*, *ch'a*, *scala*), le caporali *«*. Manca la grammatica locale: dopo 500 passi il GPT è ancora poco più di un buon trigram. Con 5.000 passi su GPU il testo migliora molto.

### Notebook 14 · Stesso compito, modello diverso: il confronto

```python
best_row = ngram_cmp.loc[ngram_cmp["val_CE"].idxmin()]     # miglior n-gram lisciato
final_gpt = estimate_gpt_loss()                             # GPT: stima su 10 batch casuali
comparison = pd.DataFrame([...])
```

Output:

```text
                      model                  context  validation_CE  validation_PPL
0            Uniform random                     none       4.343805       77.000000
1  Best tested n-gram (n=5)   exact previous 4 chars       1.767016        5.853362
2                  Tiny GPT  learned, up to 64 chars       2.226370        9.266168
```

Confronto alla pari: stessa tokenizzazione, stesso testo di validazione, stessa metrica (nats per carattere). Il miglior n-gram (scelto sulla validazione, cosa lecita per un dev set) è il 5-gram con add-0,1: CE 1,767, PPL 5,85. Il tiny GPT dopo 500 passi: CE 2,226, PPL 9,27, tra il bigram (2,35) e il trigram (1,92). **Vince il 5-gram**, come il notebook stesso prevede (*Important scientific caution*). La CE dell'n-gram è esatta su tutta la validazione; quella del GPT è stimata su 10 batch casuali (15.360 posizioni), con un po' di rumore.

La conclusione utile è **strutturale**, non la classifica: gli n-gram rappresentano il contesto per **identità esatta**, GPT impara **rappresentazioni riutilizzabili** del contesto. Con più training (5.000 passi su GPU, o un modello più largo) un GPT di questa taglia scende sotto il 5-gram (i GPT a caratteri su Tiny Shakespeare, nella versione di nanoGPT con 6 strati e $d=384$, arrivano a circa 1,47 nats in validazione); un n-gram invece non migliora più allungando il contesto, perché sbatte contro il muro.

Lo **showdown finale** (cella 69) genera 350 caratteri da ogni modello: il 9-gram produce versi quasi interamente presi dal poema (*Ma dimmi, e come a sparvier grifagno*), il 5-gram parole vere in sequenze strane, il GPT a 500 passi la struttura del verso con parole per lo più inventate. Attenzione a non confondere qualità apparente e generalizzazione: il 9-gram "scrive meglio" ma ha la perplexity di validazione peggiore di tutti (33,2) perché sa solo copiare.

### Notebook 15 · La temperatura: campionare non è addestrare

```python
for temp in [0.4, 0.8, 1.2]:
    out = model.generate(start, max_new_tokens=260, temperature=temp, top_k=30)
```

Output:

```text
TEMPERATURE = 0.4
  con ch'a sia stono pun se din mara,
che  di di col pora di lallo che che che di cella che e l'ante cena quel coll comon illla
...
TEMPERATURE = 1.2
etre 'à cha guo guta ch'ur ora ciontravi
ins'a van nditielta i aorlte,.
...
```

La **temperatura** $\tau$ divide i logit prima della softmax, $p_i\propto e^{z_i/\tau}$ (J&M §7.6.3): $\tau&lt;1$ rende la distribuzione più appuntita (verso il greedy), $\tau&gt;1$ la appiattisce (verso l'uniforme), e i pesi del modello **non cambiano**. È la versione neurale della distinzione vista con i bigram fra modello di probabilità e politica di generazione. A $\tau=0{,}4$ il testo ricade nelle ripetizioni (*che che che di*), come il greedy bigram; a $\tau=1{,}2$ compaiono combinazioni improbabili (*,.*, *tz*).

`top_k=30` tiene solo i 30 caratteri più probabili prima di campionare (*top-k sampling*, J&M §7.6.4); `top_k=1` è il greedy. Il notebook suggerisce di aggiungere il **top-p** (nucleus): tenere il più piccolo insieme di token la cui probabilità cumulata raggiunge $p$. Una realizzazione in poche righe: ordinare i logit, calcolare la cumulata delle softmax, mascherare i token oltre la soglia (tenendo sempre il primo), rinormalizzare.

**Domanda 9 del notebook** (perché la qualità cambia con la temperatura se la loss di validazione no?): la loss di validazione valuta le probabilità del modello sul testo vero, con teacher forcing, ed è indipendente dalla decodifica; la temperatura cambia solo come si *usano* quelle probabilità per generare, quindi cambia il testo prodotto senza toccare la loss.

### Notebook 16 · La mappa da portarsi via e le domande di discussione

L'invariante del notebook: **predire il token successivo dai token precedenti**. Ciò che cambia è il modello del contesto:

- **n-gram**: suffisso esatto → lookup dei conteggi → normalizzazione (MLE + smoothing) → probabilità del prossimo carattere. Trasparente e veloce, ma i contesti esatti si frammentano (il muro).
- **GPT**: id → embedding + posizioni → $L\times$(attenzione causale multi-head + feedforward) sulla residual stream → rappresentazione contestuale appresa → unembedding → logit → softmax. L'attenzione costruisce la rappresentazione di ogni posizione dalle precedenti, la maschera tiene onesto il training, tutte le posizioni si addestrano in parallelo.
- Stesso obiettivo e stessa metrica (cross-entropy e perplexity sulla stessa validazione); la decodifica (greedy, temperatura, top-$k$) è una scelta separata dal modello.

Il transformer non risolve un problema diverso: è una risposta molto più flessibile allo stesso problema di probabilità condizionata. Le dieci domande di discussione della cella 73 sono riprese, con tracce di risposta, nelle domande d'orale della sezione Studio.

Commento al notebook del corso `HLT-2026-27-L16-Language_Models_from_counting_characters_to_GPT.ipynb` (il notebook è del docente e non è incluso).

Tre esercizi non valutati (celle 74-107), che usano il modello addestrato e le celle precedenti: (1) **guardare dentro le teste di attenzione**; (2) **ablazioni**, togliere un componente alla volta e riaddestrare; (3) **rendere veloce** il tiny GPT in cinque parti: attenzione vettorizzata, SDPA (FlashAttention), lo spreco della generazione, la **KV cache**, la cache preallocata. Ogni esercizio ha celle *YOUR CODE HERE* da completare e celle *Given* che usano il codice per disegnare grafici e confrontare con l'originale.

Nel file salvato le celle da completare sono **vuote** (sollevano `NotImplementedError`) e le celle *Given* stampano solo il messaggio di attesa, tranne i grafici che non dipendono dagli esercizi. Ho scritto le soluzioni, le ho inserite nel notebook e l'ho rieseguito tutto su CPU: le figure di questa parte marcate come "mia esecuzione" vengono da lì. Tutti i controlli di correttezza passano (differenza dall'originale 0 per l'attenzione vettorizzata, $1{,}2\cdot10^{-7}$ per SDPA, testo greedy identico con la KV cache e con la cache preallocata). I **tempi** invece sono poco affidabili: la macchina su cui ho eseguito è una CPU condivisa a 2 core, con picchi casuali (lo stesso calcolo misurato due volte può differire di 3-4 volte). Riporto i tempi come indicazione qualitativa; le soluzioni complete e le risposte alle domande sono nella sezione *Studio ed esercizi*.

### Notebook 1 · Esercizio 1: le matrici di attenzione di una finestra

```python
def get_attention(m, text):            # (n_layer, n_head, T, T)
    # un forward hook su head.dropout: inputs[0] sono i pesi dopo la softmax
    hooks.append(head.dropout.register_forward_hook(fn))
    m(idx); ... rimuovere gli hook ...
maps = get_attention(model, window)    # window: 48 caratteri di validazione da inizio verso
```

Output:

```text
'  fede è sustanza di cose sperate,\ned argomento '
```

Il modello addestrato ha $L\times A=2\times4=8$ teste. Su una finestra di $T$ caratteri ogni testa produce una matrice $T\times T$ di pesi $\alpha_{tj}$: la riga $t$ dice **dove guarda** la posizione $t$. Il notebook distingue bene due oggetti diversi: la **mappa bigram** è una proprietà dell'*output* ($P(\text{next}\mid\text{current})$, una tabella fissa), mentre una matrice di attenzione dice quali *posizioni* vengono lette e cambia a ogni finestra.

Il modo più semplice di catturare i pesi senza toccare `Head.forward` è un **forward hook** sul dropout dei pesi: l'input del dropout è proprio la matrice dopo la softmax (in `eval` il dropout è l'identità). La figura (mia esecuzione, modello a 500 passi) mostra le 8 matrici sulla finestra *"␣␣fede è sustanza di cose sperate,\ned argomento"* (Par. XXIV, 64-65): righe = query, colonne = key, triangolo superiore nullo per la maschera, il pixel in alto a sinistra giallo perché la posizione 0 può guardare solo se stessa (peso 1). Si vedono: **layer 0, head 2** e **head 0** con una colonna luminosa sotto il `\n`: dopo l'a capo tutte le posizioni del nuovo verso guardano l'a capo; **layer 0, head 1** con una diagonale appena sotto la principale (il carattere precedente); **layer 0, head 3** quasi uniforme sul passato recente; le teste del layer 1 più diffuse, con trame a strisce che seguono gli spazi.

### Notebook 2 · Esercizio 1: dove guardano le teste in media

```python
def attention_by_distance(maps, max_dist=12):
    out = torch.zeros(*maps.shape[:2], max_dist + 1)
    for k in range(min(max_dist, T - 1) + 1):
        out[..., k] = torch.diagonal(maps, offset=-k, dim1=-2, dim2=-1).mean(-1)
    return out
```

Output:

```text
   layer  head  k=0 (itself)  k=1 (previous)  lift on '\n'  lift on space
0      0     0          0.12            0.11          2.32           1.45
1      0     1          0.12            0.14          1.29           0.97
2      0     2          0.10            0.12          2.79           1.02
3      0     3          0.10            0.09          0.95           0.97
4      1     0          0.09            0.07          1.03           1.23
5      1     1          0.10            0.06          0.99           1.54
6      1     2          0.09            0.07          1.14           1.29
7      1     3          0.12            0.05          1.23           1.81
```

Una finestra può ingannare: la cella media su 200 finestre casuali di validazione. `attention_by_distance` prende la $k$-esima diagonale sotto la principale (`torch.diagonal(..., offset=-k)`, gli $\alpha_{t,t-k}$ per tutti i $t\ge k$) e ne fa la media: quanto, in media, una testa guarda $k$ caratteri indietro. La misura non dipende da dove comincia la finestra. Il **lift** divide la massa di attenzione su `\n` o sullo spazio per la loro frequenza fra le key visibili: 1 = nessuna preferenza.

Lettura (mia esecuzione, modello a 500 passi). **Grafico di sinistra (layer 0)**: tutte le curve decrescono con la distanza (attenzione al passato recente), ma **head 1** ha il picco a $k=1$ (0,137 contro 0,12 a $k=0$) e **head 2** pure (0,117 contro 0,100), con un crollo a $k=2$: sono le candidate **teste del carattere precedente**. **Grafico di destra (layer 1)**: picco a $k=0$ (0,09-0,115), poi una discesa più piatta; head 3 ha un minimo a $k=1$ e un piccolo rialzo a $k=2$-$3$. Nella tabella, **head 2 e head 0 del layer 0 guardano gli a capo** 2,8 e 2,3 volte più del caso; head 3 del layer 1 guarda gli spazi 1,8 volte più del caso.

Come avverte il notebook, a 500 passi le teste sono ancora poco specializzate (pesi massimi medi intorno a 0,14): la specializzazione emerge con il budget GPU da 5.000 passi. Le domande di discussione (a che cosa serve una testa del carattere precedente, una testa degli a capo, che cosa può fare il layer 1 in più) sono risolte nella sezione Studio.

### Notebook 3 · Dove si nasconde la mappa bigram

```python
one_char = torch.arange(vocab_size).unsqueeze(1)                     # V finestre di lunghezza 1
P_gpt = F.softmax(model(one_char)[0][:, 0, :], dim=-1)             # (V, V): riga c = P(next | c)
P_counts[a] = [(c[b] + 0.1) / (tot + 0.1 * vocab_size) for b in range(vocab_size)]
kl = np.sum(freq * np.sum(P_counts * np.log(P_counts / P_gpt), axis=1))
```

Output:

```text
average KL(counts || GPT) = 0.141 nats
```

La mappa bigram non sta nei pesi di attenzione ma nell'**output della posizione 0**. In ogni finestra di training la posizione 0 vede un solo carattere e deve predire il successivo: a quella posizione il GPT è stato addestrato a essere un **bigram**. Dando in input ciascuno dei 77 caratteri da solo (77 finestre di lunghezza 1), la softmax dà la stima del GPT di $P(\text{next}\mid c)$. La cella la mette accanto alla mappa contata (con add-0,1, così il logaritmo non incontra zeri) e calcola la $D_{KL}(P_\text{counts}\,\|\,P_\text{GPT})$ media, pesata con la frequenza dei caratteri: **0,141 nats** (identica nella mia esecuzione).

Le due mappe (figura salvata) sono molto simili: colonna dello spazio, `q` → `u`, `.` → `\n`, `;` → `\n`, `í` → spazio, consonanti → vocali. Le differenze principali: le celle quasi deterministiche sono **meno scure** nel GPT (`q` → `u`, `.` → `\n` e soprattutto `»` → `.`, molto più chiara), mentre la riga `\n` → spazio è più scura nel GPT che nei conteggi. Il motivo: la posizione 0 riceve solo 24 esempi per passo (uno per finestra), cioè $500\cdot24=12.000$ esempi in tutto il training contro i 481.924 bigram contati; i caratteri rari sono visti pochissime volte in posizione 0, e una softmax poco addestrata non arriva alle probabilità estreme. Con 5.000 passi ci si aspetta una KL più piccola (non l'ho verificato: richiede il training lungo).

### Notebook 4 · Esercizio 2: ablazioni

```python
def make_variant(name):
    torch.manual_seed(SEED); m = TinyGPT(config)
    if name == "no position embeddings":
        m.position_embedding.weight.data.zero_(); m.position_embedding.weight.requires_grad_(False)
    elif name == "no residual connections":
        m.blocks = nn.Sequential(*[BlockNoResidual(config) for _ in range(config.n_layer)]); m.apply(m._init_weights)
    elif name == "no layer norm":   # ln1, ln2, ln_f -> nn.Identity()
    elif name == "no attention":    # blk.attn = ZeroOut()  (x + 0 = x)
    elif name == "no feedforward":  # blk.ffwd = ZeroOut()
    elif name == "no causal mask (cheating!)":   # head.tril.fill_(1.0)
    return m.to(device)
```

Output:

```text
baseline                     val loss 2.361
no position embeddings       val loss 2.356
no residual connections      val loss 3.062
no layer norm                val loss 2.900
no attention                 val loss 2.444
no feedforward               val loss 2.420
no causal mask (cheating!)   val loss 0.512
```

Un'**ablazione** toglie un componente e riaddestra, per misurare a che cosa serve: è il modo standard di giustificare un'architettura in un articolo. `make_variant` costruisce un `TinyGPT` nuovo e lo modifica; `train_variant` lo addestra con AdamW come nella sezione 8, con lo stesso seed (stessi batch per tutte le varianti). Output e figura sono della mia esecuzione su CPU: 300 passi per variante, valutazione ogni 30.

La figura sovrappone validazione (linee piene) e training (tratteggiate), con la baseline uniforme (4,34), il miglior n-gram (5-gram, 1,77), il 2-gram (2,35) e il 3-gram (1,92) come riferimenti orizzontali. Si vedono tre gruppi: (1) baseline, senza posizioni, senza feedforward e senza attenzione scendono insieme fino a 2,36-2,44, appena sopra la retta del bigram; (2) **senza residue** (verde) e **senza layer norm** (rosso) si fermano intorno a 3,0, il livello dell'unigram (3,05): senza residue la curva è piatta da 60 passi in poi; (3) **senza maschera** (rosa) segue la baseline fino al passo 240 e poi precipita (1,76 al passo 270, 0,51 al 300): in quel momento il modello scopre il trucco di copiare il carattere successivo.

I campioni generati confermano: baseline e senza posizioni producono testo quasi identico (stessa inizializzazione, e a 300 passi le posizioni non contano ancora); senza residue e senza layer norm escono lettere a caso con la giusta frequenza; il modello che bara genera quasi solo a capo e simboli rari (`»`, `ý`, `Ï`, `…`), perché in generazione il futuro da copiare non c'è.

### Notebook 5 · Esercizio 3, parti 1-2: attenzione vettorizzata e SDPA

```python
q, k, v = self.qkv(x).chunk(3, dim=-1)                       # ognuno [B, T, d]
q = q.view(B, T, self.n_head, hd).transpose(1, 2)            # [B, A, T, d_k]
att = (q @ k.transpose(-2, -1)) * hd ** -0.5                 # [B, A, T, T]: una matrice per testa
att = att.masked_fill(mask == 0, float("-inf")).softmax(-1)
y = (att @ v).transpose(1, 2).contiguous().view(B, T, C)     # concatenazione delle teste
# Parte 2:
y = F.scaled_dot_product_attention(q, k, v, dropout_p=p, is_causal=True)
```

Output:

```text
vectorised (Part 1)          max |difference| from the original: 0.0e+00
SDPA (Part 2)                max |difference| from the original: 1.2e-07
     original (loop over heads)  vectorised (Part 1)  SDPA (Part 2)
T
64                        102.9                 24.3           11.6
128                       115.8                 74.5           72.3
256                       216.8                387.3          107.4
512                       955.3               1024.0          386.7
```

Il `Head` della parte 2 è leggibile ma lancia molte operazioni piccole in un ciclo Python. **Parte 1**: un solo `nn.Linear(d, 3d)` calcola query, key e value di tutte le teste (le righe del peso sono, nell'ordine, le $W^Q$ delle 4 teste, poi le $W^K$, poi le $W^V$: è così che `copy_mha_into_csa` copia i pesi); `view` e `transpose` fanno delle teste una **dimensione di batch**, `(B, A, T, d_k)`, e un solo prodotto dà un tensore `(B, A, T, T)` di punteggi. Poi si riuniscono le teste con `transpose(1, 2).contiguous().view(B, T, C)`, che è proprio la concatenazione. **Parte 2**: `F.scaled_dot_product_attention` fa scala, maschera, softmax e somma pesata in un kernel **fuso**; le implementazioni FlashAttention non materializzano la matrice $T\times T$ ma la calcolano a blocchi tenendo il massimo e la somma correnti della softmax.

La correttezza è esatta: differenza 0 per la versione vettorizzata (stesse operazioni), $1{,}2\cdot10^{-7}$ per SDPA (altro ordine delle somme in virgola mobile). Tempi (forward + backward di uno strato, batch 16, mia esecuzione su CPU, prima figura): SDPA è la più veloce a ogni $T$ (da 2,5 a 9 volte l'originale); la versione vettorizzata vince nettamente a $T=64$ ma a $T=256$-$512$ è più lenta del ciclo. Su CPU il ciclo sulle teste crea tensori `(B, T, T)` più piccoli, che stanno meglio nella cache, mentre la versione vettorizzata alloca in un colpo `(B, A, T, T)`: il notebook lo dice, *measure, do not assume*. In una seconda misura indipendente SDPA è stata di nuovo la più veloce e la vettorizzata di nuovo più lenta del ciclo a $T=512$, ma con valori assoluti diversi: considerali indicativi.

La seconda figura (salvata; su CPU la memoria non si misura) è la memoria teorica della versione esplicita, punteggi più pesi in float32: $2\cdot B\cdot A\cdot T^2\cdot4$ byte $=2$, 8, 32, 128 MB per $T=64,\ldots,512$. Raddoppiare $T$ quadruplica la memoria: il costo quadratico della [scheda 60 della L14](L14-transformer-l-attenzione.md#p-60).

### Notebook 6 · Esercizio 3, parte 3: lo spreco nella generazione

```python
for _ in range(n_new):
    logits, _ = m(idx[:, -m.config.block_size:])        # tutto il contesto, di nuovo
    nxt = logits[:, -1, :].argmax(dim=-1, keepdim=True)
    idx = torch.cat([idx, nxt], dim=1)
```

Output:

```text
total time for 511 tokens: 14.81 s
```

La `generate` della parte 2 rifà il forward su **tutto** il contesto a ogni token: dopo *Nel mezzo del cammin di nostra* genera *␣vita*, e per il carattere successivo ricalcola le key e i value di *Nel mezzo del cammin di nostra* in ogni strato, anche se erano già stati calcolati al passo prima. Con un prompt di $T$ token, il passo successivo ripete per i $T$ token vecchi le proiezioni $Q,K,V$, il feedforward e i $T^2$ confronti dell'attenzione, ma usa solo l'ultima riga dei logit. Il costo del passo cresce con la lunghezza, quindi il lavoro totale per $n$ token cresce in modo quadratico (proiezioni e feedforward, $\sum_t t$) o addirittura cubico (attenzione, $\sum_t t^2$).

La figura salvata (modello di benchmark con 4 strati, $d=128$, contesto 512, pesi casuali, greedy) mostra il tempo di ogni passo: cresce in modo circa **lineare** da circa 5 ms a circa 55 ms, con un picco isolato di 400 ms intorno al token 450 (rumore della macchina), per un totale di 14,8 s. Nella mia esecuzione, su una macchina più lenta e rumorosa, il totale è stato 97,6 s.

### Notebook 7 · Esercizio 3, parti 4-5: la KV cache

```python
if past_kv is not None:
    k = torch.cat([past_k, k], dim=2); v = torch.cat([past_v, v], dim=2)
mask = self.tril[T_total - T:T_total, :T_total]                    # le ultime T righe
y = F.scaled_dot_product_attention(q, k, v, attn_mask=mask.bool())  # non is_causal con T_q != T_k
# FastGPT.forward: positions = torch.arange(pos_offset, pos_offset + T)
# generate_cached: il prompt una volta, poi UN token per passo con le cache
```

Output:

```text
Greedy text identical to model.generate: True
'e vien quel che con che che l che che se l che che che che l che'
Same text as generate_cached: True
```

La **KV cache** di J&M §7.8: si salvano key e value dei token precedenti e per un token nuovo si calcolano solo $q,k,v$ suoi (Fig. 7.23 del libro: in nero i vettori presi dalla cache, nuovi solo $q_4,k_4,v_4$). Ogni strato ha la sua cache di forma `(B, A, T_cached, d_k)`. Le query non si salvano: le uscite dei token vecchi sono già calcolate e non cambiano, perché con la maschera causale un token non vede quelli successivi.

Tre dettagli da non sbagliare, tutti suggeriti dal notebook: le **posizioni** del token nuovo partono da `pos_offset`, non da 0; la **maschera** per $T$ query nuove su $T_\text{total}$ key è formata dalle ultime $T$ righe della triangolare (per un solo token, una riga di uni); con SDPA non si può usare `is_causal=True` quando $T_q\ne T_k$, perché PyTorch allinea la maschera all'angolo in alto a sinistra, quindi la si passa come `attn_mask`. Niente finestra scorrevole: prompt più token generati devono stare in `block_size`.

Risultati della mia esecuzione: il `FastGPT` con i pesi addestrati genera **esattamente** lo stesso testo greedy di `model.generate` (54 caratteri dopo un prompt di 10: *e vien quel* e poi un ciclo *che che*, il greedy degenera anche nel GPT). Nella figura, sul modello di benchmark, il tempo per passo senza cache cresce con la posizione, con la cache resta piatto: 97,6 s contro 5,8 s, **×16,8**. La cache **preallocata** (parte 5) dà lo stesso testo; i suoi tempi nella mia macchina sono stati incoerenti fra una misura e l'altra (batch 8: 7,8 s contro 12,5 s di `torch.cat`, cioè ×1,6, in linea con il ×1,8 dichiarato dal notebook; batch 1: risultati opposti in due misure consecutive), quindi non li uso per conclusioni.

## Studio ed esercizi

### Guida allo studio (circa 4 h 35 min)

**N-gram di caratteri: contare, generare, valutare** (45 min)

Blocchi 1-12 della parte 1 del notebook. Obiettivo: saper costruire a mano una tabella bigram e le sue probabilità MLE, spiegare perché il greedy va in loop e il campionamento no, leggere la tabella dei risultati (training CE, validation CE, coverage, zeri) e la figura con le due curve. Ripassa in parallelo le [schede 11-13](L04-modelli-linguistici-n-gram.md#p-11), [30-34](L04-modelli-linguistici-n-gram.md#p-30) e [36-46 della L4](L04-modelli-linguistici-n-gram.md#p-36), le [schede 21](L05-smoothing-ed-entropia.md#p-21) e [38-39 della L5](L05-smoothing-ed-entropia.md#p-38). Libro: J&M §3.1-3.5, §3.6.1-3.6.2, §3.7.

**Il muro degli n-gram e l'idea delle rappresentazioni apprese** (20 min)

Blocchi 11-12 (autopsia, $V^h$) e il blocco sulla baseline uniforme. Devi saper dire con numeri perché un 65-gram non ha senso e che cosa si guadagna con gli embedding: [scheda 42 della L5](L05-smoothing-ed-entropia.md#p-42), [schede 43](L13-reti-neurali.md#p-43) e [47-48 della L13](L13-reti-neurali.md#p-47).

**Il tiny GPT riga per riga** (60 min)

Blocchi della parte 2 fino a TinyGPT. Con la figura del transformer della [L14 (schede 6-9)](L14-transformer-l-attenzione.md#p-6) accanto, ricostruisci per ogni classe le forme dei tensori (`[B,T]` → `[B,T,d]` → `[B,T,T]` → `[B,T,d_v]` → `[B,T,V]`), la maschera causale e il conteggio dei parametri. Libro: J&M §7.1-7.5 (Eq. 7.39-7.40 per il blocco prenorm). Esercizi D ed E della lista qui sotto.

**Training, confronto, decodifica** (30 min)

Ciclo di training in cinque passi ([L13](L13-reti-neurali.md#p-52)), curva di apprendimento, confronto con il 5-gram e la sua interpretazione, temperatura e top-$k$. Libro: J&M §7.6 (decodifica) e §7.7 (Eq. 7.55, teacher forcing, §7.7.1 perplexity in nats).

**Esercizi del notebook: attenzione, ablazioni, velocità** (90 min)

Prova a scrivere da solo `get_attention`, `attention_by_distance`, `make_variant`, `CausalSelfAttention` e la KV cache, poi confronta con le soluzioni qui sotto (tutte verificate eseguendo il notebook su CPU). Più importanti per l'esame dei dettagli di PyTorch: le risposte alle domande (cosa fa una testa, cosa succede senza ciascun componente, perché il costo è quadratico, perché si cachano $K$ e $V$, quanta memoria serve). Libro: J&M §7.3 (costo quadratico) e §7.8 (KV cache).

**Ripasso orale** (30 min)

Rispondi a voce alle domande qui sotto in 1-2 minuti l'una, con i numeri del laboratorio (77 caratteri, 5-gram a PPL 5,85, GPT a 2,23 nats dopo 500 passi, 244.301 parametri, $V^{64}\approx10^{120{,}7}$).

### Esercizi

#### Notebook L16: le scommesse PLACE YOUR BETS e la maschera causale

Rispondi alle tre *PLACE YOUR BETS* del notebook e all'esercizio veloce sulla maschera. #1: quanti caratteri distinti ha la Commedia? `A` e `a` sono lo stesso token? Quale carattere segue più spesso `t`? Quali lettere dell'alfabeto inglese mancano e quali accentate compaiono? #2: chi ha la training cross-entropy più bassa fra bigram e 9-gram? Chi va meglio in validazione? Chi incontra più contesti mai visti? #3: perché non costruire una tabella su tutte le storie esatte di 64 caratteri? Maschera: per la riga 4 di `tril` con $T=8$, quali posizioni sono visibili, e perché senza maschera il training non ha senso?

<details><summary>Soluzione</summary>

**#1** (verificato sul testo): 77 caratteri; `A` (id 12) e `a` (id 36) sono token diversi, nessun case folding; dopo `t` viene `o` con 0,189 (poi `e` 0,181 e `a` 0,172). Mancano `k` e `w` (e le maiuscole `K W X Y`); `x`, `y`, `j` compaiono solo in parole latine o provenzali (*Vexilla*, *Aegypto*, *jausen*). Accentate: `à è é ì í ò ú`, dieresi `ï ë ü`, rarità `ý À È Ï`; la più frequente è `í` (1.529 volte, per la grafia *sí*, *piú*).

**#2**: senza smoothing la training CE più bassa è del 9-gram (0,303 contro 2,358 nats); con add-0,1 il 9-gram risale a 1,873 (contesti visti una volta penalizzati), sopra il 5-gram (1,525) ma ancora sotto il bigram (2,359). In validazione vince il 5-gram (1,767; il 9-gram fa 3,503, peggio dell'unigram 3,050). I contesti mai visti li incontra il 9-gram: coverage 47,3% contro il 100% del bigram.

**#3**: $77^{64}\approx10^{120{,}7}$ contesti possibili contro meno di mezzo milione di posizioni di training: quasi ogni contesto di validazione sarebbe nuovo e riceverebbe l'uniforme. Il punto non è solo la dimensione: una tabella tratta ogni stringa come un oggetto isolato, mentre serve un modello che impari che contesti diversi sono statisticamente collegati.

**Maschera**: contando da 0, la riga 4 è `[1,1,1,1,1,0,0,0]`: visibili le posizioni 0-4. Il target `y[t]` è `x[t+1]`, che sta nell'input: senza maschera la posizione $t$ lo legge e lo copia. Lo conferma l'ablazione: senza maschera la loss di validazione scende a 0,51 in 300 passi e il testo generato è spazzatura.

</details>

#### Esercizio 1 del notebook L16: guardare dentro le teste di attenzione

Scrivi `get_attention(m, text)`, che restituisce un tensore `(n_layer, n_head, T, T)` con i pesi di attenzione (dopo la softmax) di ogni testa per il testo dato, e `attention_by_distance(maps, max_dist=12)`, che restituisce `(L, A, max_dist+1)` con, in posizione $k$, la media di $\alpha_{t,t-k}$ sulle posizioni $t\ge k$. Poi rispondi: a che cosa serve una testa che guarda il carattere precedente, se la residual stream contiene già il carattere corrente? E una che guarda l'ultimo a capo? Che cosa può fare una testa del layer 1 che nessuna del layer 0 può fare? Un peso di attenzione alto può essere inutile?

<details><summary>Soluzione</summary>

```
@torch.no_grad()
def get_attention(m, text):
    """Input: a TinyGPT and a string of at most block_size characters.
    Output: a tensor (n_layer, n_head, T, T) with the attention weights (after the softmax) of every head."""
    m.eval()
    idx = torch.tensor([encode(text)], dtype=torch.long, device=next(m.parameters()).device)
    L, A = len(m.blocks), len(m.blocks[0].attn.heads)
    maps = [[None] * A for _ in range(L)]
    hooks = []
    for l, blk in enumerate(m.blocks):
        for a, head in enumerate(blk.attn.heads):
            def fn(module, inputs, output, l=l, a=a):
                maps[l][a] = inputs[0][0].detach().cpu()      # (T, T): the weights after the softmax
            hooks.append(head.dropout.register_forward_hook(fn))
    try:
        m(idx)
    finally:
        for h in hooks:
            h.remove()
    return torch.stack([torch.stack(row) for row in maps])  # (L, A, T, T)

def attention_by_distance(maps, max_dist=12):
    """Input: the output of get_attention, shape (L, A, T, T).
    Output: a tensor (L, A, max_dist + 1); entry k = mean of alpha[t, t-k] over the positions t >= k."""
    T = maps.shape[-1]
    out = torch.zeros(*maps.shape[:2], max_dist + 1)
    for k in range(min(max_dist, T - 1) + 1):
        out[..., k] = torch.diagonal(maps, offset=-k, dim1=-2, dim2=-1).mean(-1)
    return out
```

Verificata nella mia esecuzione: forma `(2, 4, 48, 48)` sulla finestra di prova, righe che sommano a 1, triangolo superiore nullo; i grafici del notebook si generano senza errori. Un'alternativa senza hook è ricalcolare i pesi a mano (embedding, blocchi precedenti, `ln1`, query e key), più lunga e più fragile.

- **Testa del carattere precedente** (nel modello a 500 passi: layer 0, head 1 e head 2, picco a $k=1$): la residual stream della posizione $t$ contiene solo $x_t$ (più la posizione); per usare anche $x_{t-1}$ qualcuno deve copiarlo lì, ed è il lavoro di quella testa. Con lei il modello imita un **trigram** ($x_{t-1},x_t\to x_{t+1}$); più teste così, a distanze diverse, danno n-gram più lunghi, ma con rappresentazioni condivise invece che tabelle.
- **Testa degli a capo** (layer 0, head 2 e head 0, lift 2,8 e 2,3): il peso su un a capo che sta a distanza $k$ dipende da $k$ tramite gli embedding di posizione, quindi la testa può stimare *quanti caratteri fa* è cominciato il verso. Serve a predire quando il verso (un endecasillabo, circa 30-40 caratteri) sta per finire e quando arriva il rientro di due spazi della terzina.
- **Layer 1**: le sue teste leggono una residual stream già mescolata dal layer 0, quindi possono confrontare *contesti* invece che caratteri (per esempio cercare la posizione che seguiva una precedente occorrenza dello stesso carattere: è il meccanismo delle *induction head*, che richiede almeno due strati). Una testa del layer 0 vede solo embedding di token e posizione.
- **Peso alto ma inutile**: sì. Il peso dice *dove* la testa legge, non *che cosa* scrive: se il value di quella posizione è piccolo, o se $W^O$ e gli strati successivi lo ignorano, il contributo alla previsione è nullo. Esempio tipico: teste che "parcheggiano" il peso sulla prima posizione o sullo spazio quando non hanno niente da fare. L'attenzione non è una spiegazione.

Sulla mappa bigram (cella 82): le due mappe differiscono soprattutto nelle celle quasi deterministiche (`q` → `u`, `.` → `\n`, `»` → `.`), meno nette nel GPT, perché la posizione 0 riceve un solo esempio per finestra; la KL (0,141 nats a 500 passi) dovrebbe scendere con 5.000 passi.

</details>

#### Esercizio 2 del notebook L16: ablazioni

Scrivi `make_variant(name)` che, per ciascuno dei sette nomi di `VARIANTS` (baseline, senza position embedding, senza connessioni residue, senza layer norm, senza attenzione, senza feedforward, senza maschera causale), restituisce un `TinyGPT` nuovo e non addestrato con quel componente tolto. Prima di eseguire, scommetti: ordina le varianti per loss di validazione finale; quale sarà la loss del modello che bara? Che tipo di modello è il transformer senza attenzione, e quale loss della sezione 4 raggiungerà? Poi rispondi alle domande della cella 89.

<details><summary>Soluzione</summary>

```
class ZeroOut(nn.Module):
    def forward(self, x):
        return torch.zeros_like(x)

class BlockNoResidual(Block):
    def forward(self, x):
        x = self.attn(self.ln1(x))
        x = self.ffwd(self.ln2(x))
        return x

def make_variant(name):
    """Input: one of the names in VARIANTS.
    Output: a fresh, untrained TinyGPT (built with config) on device, with the component removed."""
    torch.manual_seed(SEED)
    m = TinyGPT(config)
    if name == "baseline":
        pass
    elif name == "no position embeddings":
        m.position_embedding.weight.data.zero_()
        m.position_embedding.weight.requires_grad_(False)
    elif name == "no residual connections":
        m.blocks = nn.Sequential(*[BlockNoResidual(config) for _ in range(config.n_layer)])
        m.apply(m._init_weights)
    elif name == "no layer norm":
        for blk in m.blocks:
            blk.ln1 = nn.Identity()
            blk.ln2 = nn.Identity()
        m.ln_f = nn.Identity()
    elif name == "no attention":
        for blk in m.blocks:
            blk.attn = ZeroOut()
    elif name == "no feedforward":
        for blk in m.blocks:
            blk.ffwd = ZeroOut()
    elif name == "no causal mask (cheating!)":
        for blk in m.blocks:
            for head in blk.attn.heads:
                head.tril.fill_(1.0)
    else:
        raise ValueError(name)
    return m.to(device)
```

Note: la posizione si azzera e si congela (`requires_grad_(False)`; `train_variant` passa all'optimizer solo i parametri con gradiente, così AdamW non la tocca); per togliere attenzione o feedforward senza riscrivere `Block.forward` si sostituisce il modulo con uno che restituisce zeri, così `x + 0 = x`; per le residue serve una sottoclasse con un altro `forward`, reinizializzata con `_init_weights`; la maschera si toglie riempiendo di uni il buffer `tril`.

**Risultati** (mia esecuzione, CPU, 300 passi per variante, loss di validazione finale): cheating 0,512 < senza posizioni 2,356 ≈ baseline 2,361 < senza feedforward 2,420 < senza attenzione 2,444 < senza layer norm 2,900 < senza residue 3,062.

- **Senza attenzione** i token non si mescolano mai: la posizione $t$ vede solo $x_t$ e il suo embedding di posizione, che non dice nulla sul contenuto. È un **bigram** neurale, e il suo limite è la loss del bigram della sezione 4 (2,348); a 300 passi è a 2,444 e ci si avvicina dall'alto.
- **Senza maschera** la loss è spettacolare perché le posizioni 0-62 possono copiare il target, che è nell'input; solo la posizione 63 deve davvero predire. Il limite è circa $\text{CE}_{63}/64\approx 2{,}3/64\approx0{,}04$ nats; a 300 passi è 0,51 e sta crollando (il trucco si scopre bruscamente fra il passo 240 e il 300). Il testo generato è fatto di a capo e simboli rari: in generazione l'ultimo token non ha un futuro da copiare.
- **Senza position embedding** a questo budget non c'è differenza (2,356 contro 2,361). L'informazione d'ordine non sparisce del tutto: con la maschera causale la posizione $t$ fa una media su $t+1$ token, quindi la prima posizione vede solo se stessa e la decima una media di dieci, e la rete può dedurre quanto è lunga la storia. Quello che si perde è il "chi è il precedente": a parità di contenuto, un carattere un passo indietro e uno dieci passi indietro sono indistinguibili. Il notebook prevede un distacco con il budget GPU (1.500 passi), che non ho verificato.
- **Senza residue** il modello resta inchiodato a 3,06, cioè all'**unigram** (3,05): senza la scorciatoia della somma, l'identità del carattere corrente deve attraversare attenzione e feedforward appena inizializzati (pesi con deviazione 0,02) e si perde, così la rete impara solo le frequenze. **Senza layer norm** (2,90) il training è molto più lento. Entrambi gli effetti crescono con la profondità: con `n_layer = 6` il segnale e il gradiente devono attraversare tre volte più strati, e senza residue e normalizzazione svaniscono o esplodono (L13, connessioni residue e normalizzazione).

</details>

#### Esercizio 3 del notebook L16, parti 1-2: attenzione vettorizzata e SDPA

Scrivi `CausalSelfAttention(config, use_sdpa=False)` con una sola proiezione `qkv`, le teste come dimensione di batch e `forward(x, past_kv=None)` che restituisce `(y, (k, v))`; nel ramo `use_sdpa` usa `F.scaled_dot_product_attention`. Domande: perché un grande prodotto matriciale è preferibile a un ciclo su molti piccoli? Quanti elementi ha la matrice di attenzione di una testa per una sequenza di $T$ token, che cosa succede raddoppiando $T$, e quanti GB servirebbero per uno strato con $T=100.000$ e 32 teste in float32? Scommessa: quanto sarà più veloce la versione vettorizzata con contesto 64 e 512?

<details><summary>Soluzione</summary>

```
class CausalSelfAttention(nn.Module):
    def __init__(self, config, use_sdpa=False):
        super().__init__()
        assert config.n_embd % config.n_head == 0
        self.n_head = config.n_head
        self.use_sdpa = use_sdpa
        self.qkv = nn.Linear(config.n_embd, 3 * config.n_embd, bias=False)   # W^Q, W^K, W^V of all the heads
        self.proj = nn.Linear(config.n_embd, config.n_embd)                  # W^O
        self.dropout_p = config.dropout
        self.attn_dropout = nn.Dropout(config.dropout)
        self.resid_dropout = nn.Dropout(config.dropout)
        self.register_buffer("tril", torch.tril(torch.ones(config.block_size, config.block_size)))

    def forward(self, x, past_kv=None):
        B, T, C = x.shape
        hd = C // self.n_head
        q, k, v = self.qkv(x).chunk(3, dim=-1)
        q = q.view(B, T, self.n_head, hd).transpose(1, 2)
        k = k.view(B, T, self.n_head, hd).transpose(1, 2)
        v = v.view(B, T, self.n_head, hd).transpose(1, 2)
        if past_kv is not None:
            past_k, past_v = past_kv
            k = torch.cat([past_k, k], dim=2)
            v = torch.cat([past_v, v], dim=2)
        T_total = k.size(2)
        mask = self.tril[T_total - T:T_total, :T_total]
        if self.use_sdpa:
            p = self.dropout_p if self.training else 0.0
            if past_kv is None:
                y = F.scaled_dot_product_attention(q, k, v, dropout_p=p, is_causal=True)
            else:
                y = F.scaled_dot_product_attention(q, k, v, attn_mask=mask.bool(), dropout_p=p)
        else:
            att = (q @ k.transpose(-2, -1)) * hd ** -0.5
            att = att.masked_fill(mask == 0, float("-inf"))
            att = F.softmax(att, dim=-1)
            att = self.attn_dropout(att)
            y = att @ v
        y = y.transpose(1, 2).contiguous().view(B, T, C)
        y = self.resid_dropout(self.proj(y))
        return y, (k, v)
```

Il ramo `past_kv` e la maschera "ultime $T$ righe" servono alla parte 4; senza cache $T_\text{total}=T$ e la maschera è la solita triangolare. Verificata: differenza massima dall'originale 0 (vettorizzata) e $1{,}2\cdot10^{-7}$ (SDPA).

- **Perché un prodotto grande**: ogni operazione PyTorch ha un costo fisso (interprete Python, dispatch, su GPU il lancio del kernel); con $A$ teste il ciclo paga $A$ volte questo costo per ogni passo. Un prodotto grande ammortizza l'overhead e dà alla libreria di algebra lineare (o alla GPU) abbastanza lavoro da usare tutti i core in parallelo.
- **Memoria**: $T^2$ elementi per testa; raddoppiando $T$ si quadruplica. Con $T=10^5$ e 32 teste: $32\cdot10^{10}\cdot4$ byte $=1{,}28\cdot10^{12}$ byte, circa **1.280 GB** per strato e per sequenza, solo i punteggi. Per questo FlashAttention calcola l'attenzione a blocchi senza mai scrivere la matrice intera.
- **Scommessa** (mia CPU, batch 16, forward + backward): a $T=64$ la vettorizzata è circa 4 volte più veloce (24 contro 103 ms), a $T=512$ no (1.024 contro 955 ms); SDPA è la più veloce ovunque (387 ms a $T=512$, ×2,5). Su GPU ci si aspetta un vantaggio netto della vettorizzata a ogni $T$. Morale del notebook: *measure, do not assume*.

</details>

#### Esercizio 3 del notebook L16, parti 3-5: lo spreco della generazione e la KV cache

Parte 3: se il prompt ha $T$ token, quali calcoli si ripetono per generare il successivo? Come cresce il lavoro totale con il numero di token generati? Parte 4: scrivi `FastBlock` e `FastGPT` (con `forward(idx, targets=None, past_kvs=None, pos_offset=0)` e `generate_cached`), verifica che il testo greedy sia identico a `model.generate`; perché si cachano $K$ e $V$ ma non $Q$? Quanta memoria serve la cache di un modello con $L$ strati, dimensione $d$ e contesto $N$? Parte 5 (facoltativa): `generate_preallocated` con buffer allocati una volta. Discussione finale: quale parte dà il guadagno maggiore nel training e quale in generazione? Stima la cache di Llama 3.1 8B ($L=32$, $d=4096$, 128k token, float16) senza GQA. Perché non si può scartare la entry più vecchia della cache e continuare?

<details><summary>Soluzione</summary>

```
class FastBlock(nn.Module):
    def __init__(self, config, use_sdpa=False):
        super().__init__()
        self.ln1 = nn.LayerNorm(config.n_embd)
        self.attn = CausalSelfAttention(config, use_sdpa)
        self.ln2 = nn.LayerNorm(config.n_embd)
        self.ffwd = FeedForward(config)

    def forward(self, x, past_kv=None):
        a, new_kv = self.attn(self.ln1(x), past_kv)
        x = x + a
        x = x + self.ffwd(self.ln2(x))
        return x, new_kv

class FastGPT(nn.Module):
    def __init__(self, config, use_sdpa=False):
        super().__init__()
        self.config = config
        self.token_embedding = nn.Embedding(config.vocab_size, config.n_embd)
        self.position_embedding = nn.Embedding(config.block_size, config.n_embd)
        self.blocks = nn.ModuleList([FastBlock(config, use_sdpa) for _ in range(config.n_layer)])
        self.ln_f = nn.LayerNorm(config.n_embd)
        self.lm_head = nn.Linear(config.n_embd, config.vocab_size)

    def forward(self, idx, targets=None, past_kvs=None, pos_offset=0):
        B, T = idx.shape
        positions = torch.arange(pos_offset, pos_offset + T, device=idx.device)
        x = self.token_embedding(idx) + self.position_embedding(positions)
        new_kvs = []
        for i, blk in enumerate(self.blocks):
            x, kv = blk(x, None if past_kvs is None else past_kvs[i])
            new_kvs.append(kv)
        logits = self.lm_head(self.ln_f(x))
        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits.reshape(B * T, -1), targets.reshape(B * T))
        return logits, loss, new_kvs

    @torch.no_grad()
    def generate_cached(self, idx, max_new_tokens, temperature=1.0, top_k=None):
        self.eval()
        assert idx.size(1) + max_new_tokens - 1 <= self.config.block_size, "no sliding window with a cache"
        logits, _, kvs = self(idx)                                   # the prompt, once
        for i in range(max_new_tokens):
            l = logits[:, -1, :] / max(float(temperature), 1e-5)
            if top_k is not None:
                k = min(top_k, l.size(-1))
                threshold = torch.topk(l, k).values[:, [-1]]
                l = l.masked_fill(l < threshold, float("-inf"))
            nxt = torch.multinomial(F.softmax(l, dim=-1), 1)
            idx = torch.cat([idx, nxt], dim=1)
            if i == max_new_tokens - 1:
                break
            logits, _, kvs = self(nxt, past_kvs=kvs, pos_offset=idx.size(1) - 1)   # ONE token per step
        return idx
```

```
@torch.no_grad()
def generate_preallocated(self, idx, max_new_tokens, temperature=1.0, top_k=None):
    self.eval()
    cfg = self.config
    B, A = idx.size(0), cfg.n_head
    hd = cfg.n_embd // A
    caches = [(torch.empty(B, A, cfg.block_size, hd, device=idx.device),
               torch.empty(B, A, cfg.block_size, hd, device=idx.device)) for _ in self.blocks]

    def run(tokens, pos):
        T = tokens.size(1)
        x = self.token_embedding(tokens) + self.position_embedding(torch.arange(pos, pos + T, device=tokens.device))
        for blk, (kc, vc) in zip(self.blocks, caches):
            att = blk.attn
            q, k, v = att.qkv(blk.ln1(x)).chunk(3, dim=-1)
            q, k, v = [t.view(B, T, A, hd).transpose(1, 2) for t in (q, k, v)]
            kc[:, :, pos:pos + T] = k                                 # write in place, no copy of the past
            vc[:, :, pos:pos + T] = v
            mask = att.tril[pos:pos + T, :pos + T].bool()
            y = F.scaled_dot_product_attention(q, kc[:, :, :pos + T], vc[:, :, :pos + T], attn_mask=mask)
            x = x + att.proj(y.transpose(1, 2).contiguous().view(B, T, cfg.n_embd))
            x = x + blk.ffwd(blk.ln2(x))
        return self.lm_head(self.ln_f(x))

    logits = run(idx, 0)
    for i in range(max_new_tokens):
        l = logits[:, -1, :] / max(float(temperature), 1e-5)
        if top_k is not None:
            k = min(top_k, l.size(-1))
            threshold = torch.topk(l, k).values[:, [-1]]
            l = l.masked_fill(l < threshold, float("-inf"))
        nxt = torch.multinomial(F.softmax(l, dim=-1), 1)
        idx = torch.cat([idx, nxt], dim=1)
        if i == max_new_tokens - 1:
            break
        logits = run(nxt, idx.size(1) - 1)
    return idx

FastGPT.generate_preallocated = generate_preallocated      # attach the method to the class
```

Verificate: `Greedy text identical to model.generate: True` con i pesi addestrati, e `Same text as generate_cached: True` per la versione preallocata (anche con batch 8).

- **Parte 3**: per il token $T+1$ si ricalcolano, in ogni strato, le proiezioni $Q,K,V$ e il feedforward di tutti i $T$ token vecchi e gli $O(T^2)$ confronti dell'attenzione, ma serve solo l'ultima riga. Il passo $t$ costa circa $O(t\,d^2+t^2d)$, quindi generare $n$ token costa $O(n^2d^2+n^3d)$: il tempo per passo cresce linearmente (figura della parte 3), il totale in modo quadratico. Con la cache il passo $t$ costa $O(d^2+t\,d)$ e il totale $O(n\,d^2+n^2d)$.
- **Perché $K$ e $V$ ma non $Q$**: il token nuovo deve confrontare la sua query con le key di tutti i token e sommarne i value: key e value dei vecchi servono a ogni passo e, con la maschera causale, non cambiano più. Le query dei vecchi servirebbero solo a ricalcolare le loro uscite, che sono già note e immutabili.
- **Memoria**: $2\cdot L\cdot N\cdot d$ numeri per sequenza (key e value, tutte le teste). Llama 3.1 8B: $2\cdot32\cdot131.072\cdot4.096\cdot2$ byte $=68{,}7$ GB $=64$ GiB per una sequenza; con GQA (8 teste di key/value su 32) 16 GiB.
- **Training contro generazione**: nel training tutte le posizioni si calcolano in parallelo e non c'è lavoro ripetuto, quindi contano le parti 1-2 (SDPA: nella mia misura ×2,5 a $T=512$; su GPU anche la memoria); in generazione il collo di bottiglia è il ricalcolo sequenziale, quindi vince la KV cache (×16,8 nella mia esecuzione). La preallocazione (parte 5) è un raffinamento: ×1,6 nella mia misura con batch 8, rumorosa con batch 1, in linea con l'1,1-1,8 dichiarato dal notebook.
- **Niente finestra scorrevole con la cache**: le key salvate contengono già l'embedding della loro posizione assoluta (sommato all'ingresso) e, dal secondo strato, il contesto che vedevano, compreso il token che si vorrebbe scartare. Dopo uno scorrimento ogni token dovrebbe avere la posizione diminuita di uno e un contesto diverso: tutte le key e i value andrebbero ricalcolati. `generate` invece ritaglia gli ultimi `block_size` token e ricalcola tutto da capo, quindi può scorrere.

</details>

#### Esercizio A: un bigram di caratteri a mano

Corpus di training (un solo flusso di caratteri, lo spazio è un carattere): `casa cara casa`. (a) Scrivi la tabella dei conteggi bigram $C(ab)$ e le probabilità MLE $P(b\mid a)$. (b) Calcola la probabilità delle continuazioni di `casa` e di `sara` (cioè il prodotto delle probabilità dei 3 caratteri dopo il primo), la cross-entropy in nats per carattere e la perplexity. (c) Che cosa succede alla stringa `rs`? (d) Rifai (b) e (c) con add-1 (Laplace) su $V=5$.

<details><summary>Soluzione</summary>

(a) Il vocabolario è $\{␣, a, c, r, s\}$, $V=5$. Coppie consecutive: `ca as sa a␣ ␣c ca ar ra a␣ ␣c ca as sa`. Conteggi: $C(ca)=3$; $C(as)=2$, $C(a␣)=2$, $C(ar)=1$ (quindi $C(a)=5$ come contesto: l'ultima `a` non ha successore); $C(sa)=2$; $C(␣c)=2$; $C(ra)=1$. MLE: $P(a\mid c)=1$, $P(s\mid a)=0{,}4$, $P(␣\mid a)=0{,}4$, $P(r\mid a)=0{,}2$, $P(a\mid s)=1$, $P(c\mid ␣)=1$, $P(a\mid r)=1$.

(b) `casa`: $1\cdot0{,}4\cdot1=0{,}4$; $H=-\ln(0{,}4)/3=0{,}305$ nats; PPL $=0{,}4^{-1/3}=1{,}357$. `sara`: $P(a\mid s)P(r\mid a)P(a\mid r)=1\cdot0{,}2\cdot1=0{,}2$; $H=-\ln(0{,}2)/3=0{,}536$; PPL $=1{,}710$. (c) $P(s\mid r)=0/1=0$: probabilità zero, $H=\infty$, perplexity infinita (gli zeri della L4). (d) Add-1: $P(b\mid a)=\frac{C(ab)+1}{C(a)+5}$. `casa`: $\frac{4}{8}\cdot\frac{3}{10}\cdot\frac{3}{7}=0{,}0643$, $H=0{,}915$, PPL $=2{,}50$. `sara`: $\frac37\cdot\frac2{10}\cdot\frac26=0{,}0286$, $H=1{,}185$, PPL $=3{,}27$. `rs`: $\frac{0+1}{1+5}=\frac16$, $H=\ln 6=1{,}792$, PPL $=6$. Lo smoothing elimina l'infinito ma toglie molta massa ai bigram visti (da 1 a 0,5 per `ca`): con un vocabolario e conteggi così piccoli, Laplace è brutale (verificato in Python).

</details>

#### Esercizio B: perché la training CE lisciata del 9-gram risale

Nel notebook, con add-$\alpha$ e $\alpha=0{,}1$, $V=77$, la training cross-entropy è 1,525 nats per il 5-gram e 1,873 per il 9-gram, mentre con la MLE il 9-gram ha 0,303. Spiega il fenomeno calcolando la probabilità che add-0,1 dà al successore osservato quando il contesto è stato visto (i) 1 volta, (ii) 2 volte con lo stesso successore, (iii) 10 volte con lo stesso successore, e il contributo in nats. Quanto vale la probabilità di ciascuno degli altri 76 caratteri nel caso (i)? E per un contesto mai visto?

<details><summary>Soluzione</summary>

Add-$\alpha$: $P=\frac{C(\text{ctx}\,b)+\alpha}{C(\text{ctx})+\alpha V}$ con $\alpha V=7{,}7$. (i) $\frac{1{,}1}{8{,}7}=0{,}126$, $-\ln=2{,}07$ nats; gli altri 76 caratteri hanno $\frac{0{,}1}{8{,}7}=0{,}0115$ ciascuno, in tutto l'87% della massa va a caratteri mai visti dopo quel contesto. (ii) $\frac{2{,}1}{9{,}7}=0{,}216$, $1{,}53$ nats. (iii) $\frac{10{,}1}{17{,}7}=0{,}571$, $0{,}56$ nats. Contesto mai visto: $\frac{0{,}1}{0{,}1\cdot77}=1/77$, $\ln 77=4{,}34$ nats per qualunque carattere.

La MLE darebbe probabilità 1 (0 nats) in tutti e tre i casi. Nel 9-gram la gran parte dei 321.762 contesti di training è vista pochissime volte, quindi lo smoothing "ruba" quasi tutta la massa proprio dove il modello era sicuro: anche sul training la CE sale. Nel 5-gram i contesti sono più frequenti e la stessa costante $\alpha V=7{,}7$ pesa meno. È il problema di Laplace della L5 (troppa massa agli zeri): $\alpha$ andrebbe scelto per ogni ordine sulla validazione, o meglio si dovrebbe interpolare con gli ordini inferiori.

</details>

#### Esercizio C: nats, bit e perplexity

(a) Converti in bit per carattere e in perplexity: la baseline uniforme ($\ln 77$ nats), il 5-gram lisciato (1,767 nats) e il tiny GPT (2,226 nats). (b) Un modello ha perplexity 5,85: in che senso "esita fra circa 6 caratteri"? (c) Un collega riporta per un modello a sottoparole (BPE) una perplexity di 20 sulla stessa Commedia e conclude che è peggiore del 5-gram di caratteri. Ha ragione?

<details><summary>Soluzione</summary>

(a) $H_\text{bit}=H_\text{nat}/\ln 2$, PPL $=e^{H_\text{nat}}=2^{H_\text{bit}}$. Uniforme: $4{,}344$ nats $=6{,}267$ bit, PPL 77. 5-gram: $1{,}767$ nats $=2{,}549$ bit, PPL $e^{1{,}767}=5{,}853$. GPT: $2{,}226$ nats $=3{,}212$ bit, PPL $9{,}266$. (b) La perplexity è il fattore di ramificazione medio pesato: un modello che a ogni passo scegliesse uniformemente fra 5,85 caratteri avrebbe la stessa cross-entropy (L4, schede 33-35). (c) No: la perplexity si confronta solo **a parità di tokenizzazione**, perché è una media per token e i token sono diversi. Un token BPE vale in media diversi caratteri; per confrontare bisogna riportare tutto a una stessa unità, per esempio bit per carattere: $\text{bpc}=\frac{N_\text{tok}\log_2 \text{PPL}_\text{tok}}{N_\text{char}}$. Con 4 caratteri per token, $\log_2 20/4=1{,}08$ bit per carattere, molto meglio dei 2,55 del 5-gram.

</details>

#### Esercizio D: contare i parametri del tiny GPT

Con $|V|=77$, $N=64$, $d=96$, $A=4$, $L=2$, $d_{ff}=4d$: conta i parametri di ogni componente di `TinyGPT` (le $W^Q,W^K,W^V$ di `Head` sono senza bias; `proj`, i due `nn.Linear` del feedforward e `lm_head` hanno il bias; ogni `LayerNorm` ha $\gamma$ e $\beta$). Verifica il totale stampato dal notebook, 244.301. Che frazione sta nei blocchi? Come cambia il totale con weight tying ($U=E^\top$, bias di `lm_head` mantenuto)?

<details><summary>Soluzione</summary>

- Attenzione di un blocco: $3\cdot A\cdot d\cdot d_k=3\cdot96\cdot96=27.648$, più $W^O$: $96\cdot96+96=9.312$; totale $36.960$ ($\approx4d^2=36.864$).
- Feedforward: $96\cdot384+384+384\cdot96+96=74.208$ ($\approx8d^2=73.728$).
- Due layer norm: $2\cdot2\cdot96=384$. Blocco: $111.552$; due blocchi: $223.104$.
- $E$: $77\cdot96=7.392$; $E_{pos}$: $64\cdot96=6.144$; `ln_f`: $192$; `lm_head`: $96\cdot77+77=7.469$.

Totale $223.104+7.392+6.144+192+7.469=244.301$, come nel notebook (verificato anche con `sum(p.numel() ...)` nella mia esecuzione). I blocchi sono il 91,3%. Con weight tying si risparmiano i $96\cdot77=7.392$ pesi di `lm_head`: $236.909$. In un LLM vero il rapporto si inverte rispetto al vocabolario: con $|V|$ di decine di migliaia, embedding e unembedding pesano molto, ed è per questo che il tying è diffuso.

</details>

#### Esercizio E: una testa causale a mano

Tre posizioni. I punteggi già scalati $QK^\top/\sqrt{d_k}$ sono

$$S=\begin{pmatrix}2&5&-1\\1&3&4\\0&1&1\end{pmatrix}$$

e i value sono $v_0=(1,0)$, $v_1=(0,1)$, $v_2=(1,1)$. (a) Applica la maschera causale e la softmax per riga. (b) Calcola le uscite $a_0,a_1,a_2$. (c) Quali elementi di $S$ non hanno avuto alcun effetto? (d) Nel training, a quale carattere di `y` corrisponde l'uscita di posizione 1, e perché senza maschera il problema diventa banale?

<details><summary>Soluzione</summary>

(a) Maschera: $S_{01},S_{02},S_{12}\to-\infty$. Riga 0: $(1,0,0)$. Riga 1: softmax$(1,3)=(0{,}119;\;0{,}881)$, cioè $(0{,}119;\,0{,}881;\,0)$. Riga 2: softmax$(0,1,1)=(1,e,e)/(1+2e)=(0{,}155;\,0{,}422;\,0{,}422)$.

(b) $a_0=v_0=(1,0)$. $a_1=0{,}119\,(1,0)+0{,}881\,(0,1)=(0{,}119;\,0{,}881)$. $a_2=0{,}155\,(1,0)+0{,}422\,(0,1)+0{,}422\,(1,1)=(0{,}578;\,0{,}845)$.

(c) $5$, $-1$ e $4$ (il triangolo superiore): sono i confronti con il futuro, cancellati dalla maschera; il 5 sarebbe stato il punteggio più alto della riga 0. (d) L'uscita di posizione 1 serve a predire `y[1] = x[2]`. Senza maschera la posizione 1 potrebbe dare peso a $v_2$, che contiene (nel primo strato, direttamente) l'embedding di $x_2$, cioè la risposta: il modello imparerebbe a copiare invece che a predire (verificato in NumPy).

</details>

#### Esercizio F: memoria dell'attenzione e della KV cache

(a) Quanti elementi ha la matrice di attenzione di una testa per una sequenza di $T$ token? Che cosa succede raddoppiando $T$? Con $T=100.000$ e 32 teste, quanti GB servono per uno strato in float32? (b) Quanto occupa la KV cache, per sequenza, di un modello con $L$ strati, dimensione $d$ e contesto $N$, in float16? Applicala a Llama 3.1 8B ($L=32$, $d=4096$, $N=128\text{k}=131.072$) senza e con grouped-query attention (cache ridotta di 4 volte), e al tiny GPT del laboratorio in float32.

<details><summary>Soluzione</summary>

(a) $T^2$ elementi; raddoppiando $T$ si quadruplicano. $T=10^5$: $10^{10}$ elementi per testa, $\times32$ teste $\times4$ byte $=1{,}28\cdot10^{12}$ byte $=1.280$ GB per strato e per sequenza, solo per i punteggi (il doppio se si tengono anche i pesi dopo la softmax per il backward). È il motivo per cui FlashAttention non materializza mai la matrice.

(b) Per ogni strato e ogni token si salvano una key e un value di dimensione $d$ (tutte le teste insieme): $2\cdot L\cdot N\cdot d$ numeri. Llama 3.1 8B in float16: $2\cdot32\cdot131.072\cdot4.096\cdot2$ byte $=68{,}7\cdot10^9$ byte $=64$ GiB per una sola sequenza; con GQA (8 teste di key/value su 32 di query) 16 GiB. Tiny GPT ($L=2$, $N=64$, $d=96$, float32): $2\cdot2\cdot64\cdot96\cdot4=98.304$ byte $=96$ KiB; il modello di benchmark ($L=4$, $N=512$, $d=128$): 2 MiB (verificato in Python).

</details>

### Domande tipo orale

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
