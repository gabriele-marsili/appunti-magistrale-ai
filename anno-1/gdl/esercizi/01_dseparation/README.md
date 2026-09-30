# 01 — d-separazione, Markov blanket, fattorizzazione

## Lezione di riferimento

`Lessons/GDL4 bayesian networks II.pdf` — *d-separation, Markov Property and
Faithfulness, Markov Blanket*. Prerequisito immediato:
`Lessons/GDL3 bayesian networks I.pdf` — *Local Markov Property, Joint
Probability Factorization*, e soprattutto le tre sottostrutture fondamentali
(tail-to-tail / head-to-tail / head-to-head).

## Rappresentazione

Un DAG e' un `dict[str, list[str]]` che mappa **ogni** nodo alla lista dei suoi
**genitori**. Ogni nodo compare come chiave, anche se la sua lista e' vuota:

```python
CHAIN = {"A": [], "B": ["A"], "C": ["B"]}          # A -> B -> C
COLLIDER = {"X": [], "Y": [], "Z": ["X","Y"], "W": ["Z"]}   # X -> Z <- Y, Z -> W
STUDENT = {"D": [], "I": [], "G": ["D","I"], "S": ["I"], "L": ["G"]}
```

I figli non sono memorizzati da nessuna parte: vanno ricavati.

## Specifica matematica

**Cammino bloccato.** Sia `r = (Y1 ... Y2)` un cammino *non orientato* fra `Y1`
e `Y2`. Il cammino e' bloccato da `Z` se esiste almeno un nodo interno `Yc` per
cui vale una di queste condizioni:

- `r` contiene una catena (head-to-tail) `Yi -> Yc -> Yj` con `Yc ∈ Z`;
- `r` contiene un fork (tail-to-tail) `Yi <- Yc -> Yj` con `Yc ∈ Z`;
- `r` contiene un collider (head-to-head) `Yi -> Yc <- Yj` con **ne' `Yc` ne'
  alcun suo discendente** in `Z`.

**d-separazione.** `X` e' d-separato da `Y` dato `Z`, scritto `Dsep_G(X,Y|Z)`,
se e solo se *tutti* i cammini non orientati fra un nodo di `X` e un nodo di
`Y` sono bloccati da `Z`.

**Global Markov property.** Se `Dsep_G(X,Y|Z)` allora `X ⊥ Y | Z` in ogni
distribuzione che fattorizza secondo `G`. Il viceversa (`X ⊥ Y | Z` implica
`Dsep_G(X,Y|Z)`) e' la condizione di **faithfulness**, che e' un'ipotesi
aggiuntiva, non un teorema.

**Fattorizzazione.** Catena delle probabilita' + local Markov property:

```
P(V) = prod_{v ∈ V} P(v | pa(v))
```

**Markov blanket.** `Mb(v) = pa(v) ∪ ch(v) ∪ pa(ch(v)) \ {v}`. E' l'insieme
minimale tale che `v ⊥ V \ ({v} ∪ Mb(v)) | Mb(v)`.

## Cosa devi implementare

In `dseparation.py`, le funzioni marcate `# TODO`:

- `parents(dag, node) -> list[str]` — copia della lista di genitori memorizzata.
- `children(dag, node) -> list[str]` — figli, in ordine alfabetico.
- `ancestors(dag, nodes) -> set[str]` — chiusura ancestrale di un insieme, che
  **include** i nodi di partenza.
- `markov_blanket(dag, node) -> set[str]` — genitori, figli e co-genitori dei figli.
- `is_dseparated(dag, X, Y, Z) -> bool` — X, Y, Z insiemi di nodi. Scegli tu
  l'algoritmo (Bayes-Ball oppure grafo morale ancestrale) ma **documenta quale**.
- `active_paths(dag, x, y, Z) -> list[list[str]]` — tutti i cammini attivi fra
  due nodi singoli, ognuno come lista di nodi da `x` a `y`. E' la spiegazione
  costruttiva di ogni non-separazione.
- `factorization(dag) -> str` — es. `"P(A)P(B)P(C|A,B)"`, nodi in ordine
  topologico, senza spazi.
- `implies_independence(dag, X, Y, Z) -> bool` — stesso verdetto di
  `is_dseparated`, ma solleva `ValueError` se un nodo non esiste nel DAG o se
  X, Y, Z non sono a due a due disgiunti.

Sono gia' forniti e **non** vanno reimplementati: le tre costanti `CHAIN`,
`COLLIDER`, `STUDENT` con le rispettive cardinalita', `topological_order`,
`random_cpts` ed `enumerate_joint` (che costruisce la tabella congiunta
completa dalle CPT: serve all'oracolo dei test).

## Perche' questo esercizio

Perche' il collider si comporta all'incontrario di tutto il resto: condizionare
su un nodo di solito *blocca* l'informazione, ma su un collider — o su un suo
qualsiasi discendente — la *sblocca*. Chi implementa la d-separazione
"a intuito" scrive un semplice controllo di raggiungibilita' e ottiene la
risposta giusta su catene e fork e sbagliata su ogni v-structure; chi ricorda
il collider ma dimentica i discendenti sbaglia su `X ⊥ Y | W` in
`X -> Z <- Y, Z -> W`. Il test numerico non lascia scampo: costruisce la
congiunta vera e misura l'indipendenza per marginalizzazione.

## Vincoli

Solo `numpy` e libreria standard. Niente `networkx`, `pgmpy`, `torch`,
`scipy`, `sklearn`, `matplotlib`. Nessuna casualita' non seminata.

## Come autovalutarti

```bash
cd /home/claude/gdl/esercizi/01_dseparation
python3 -m pytest test_dseparation.py -v
```

Sono 14 test. Sullo skeleton falliscono tutti. Se vuoi vedere la suite verde di
riferimento: `GDL_SOL=1 python3 -m pytest test_dseparation.py -q`.

Consiglio sull'ordine: prima `parents`/`children`/`ancestors`, poi
`factorization` e `markov_blanket` (che si appoggiano ai primi), poi
`active_paths` (piu' facile da scrivere e da debuggare, perche' e' la
definizione letterale), infine `is_dseparated` — che deve dare esattamente lo
stesso verdetto di `active_paths` ma senza enumerare i cammini.

## Tempo stimato

90-120 minuti se e' la prima volta che implementi la d-separazione; 45 se hai
gia' presente Bayes-Ball. La parte che porta via piu' tempo non e' il codice,
e' convincersi del caso collider-con-discendente.

## Domande d'orale collegate

1. Enuncia la definizione di cammino bloccato e spiega perche' il collider ha
   la condizione invertita rispetto a catena e fork.
2. Nella rete Student, `D` e `I` sono marginalmente indipendenti ma diventano
   dipendenti osservando `G`. Come si chiama questo fenomeno e come lo spieghi
   a parole? Cosa succede se invece di `G` osservi solo `L`?
3. Che differenza c'e' fra Global Markov property e faithfulness? Quale delle
   due e' un teorema e quale un'assunzione, e a cosa serve quest'ultima nello
   structure learning?
4. Cos'e' il Markov blanket di un nodo e perche' contiene anche i co-genitori
   dei figli? Cosa succede se ne togli uno?
