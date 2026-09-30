# Note alla soluzione

## Gli assi di P, e perche' sbagliarli non costa niente

La convenzione `P[s, a, s'] = P(S_{t+1} = s' | S_t = s, A_t = a)` fissa che il
primo asse sia la partenza e l'ultimo l'arrivo. Ne segue che la somma su `s'`
del backup contrae l'ultimo asse, cioe' `P @ V` (numpy contrae per default
l'ultimo asse del primo operando con l'unico asse del secondo) e restituisce
shape `(S, A)`. Il guaio e' che anche `np.einsum("tas,t->sa", P, V)`
restituisce shape `(S, A)`: le shape combaciano, la Q che ne esce ha valori
plausibili, e value iteration converge tranquillamente a un punto fisso, solo
che e' il punto fisso di un altro MDP. Per questo il gridworld dei test e'
asimmetrico — goal in `(0,3)`, trappola in `(1,3)`, e sono l'unica sorgente di
premio non uniforme — e per questo `test_q_from_v_oracolo_definizione` riscrive
il backup con tre cicli espliciti invece che con l'algebra vettoriale: e' un
oracolo che non condivide una riga con l'implementazione. La mutazione fa
cadere 9 test su 12; con un ambiente simmetrico non ne farebbe cadere nessuno.

## `max_a` contro `sum_a pi(a|s)`: il posto dove si sbaglia in silenzio

Bellman atteso e Bellman ottimo differiscono per un solo operatore nella stessa
posizione sintattica. Mettere `max_a` dentro `policy_evaluation` non solleva
niente: si ottiene una funzione che ignora l'argomento `pi` e restituisce `V*`
sempre. E `V*` e' una funzione di valore perfettamente sensata — e' persino il
punto fisso di *un'* equazione di Bellman — quindi tutti i controlli di
plausibilita' passano.

L'unico modo per accorgersene e' un oracolo che calcoli `V^pi` senza usare
nessun operatore di Bellman. La scelta e' il sistema lineare: il punto fisso di
`V <- R_pi + gamma P_pi V` e' l'unica soluzione di `(I - gamma P_pi) V = R_pi`,
e per `gamma < 1` la matrice `I - gamma P_pi` e' invertibile perche' `P_pi` e'
stocastica e quindi il suo raggio spettrale e' 1. `np.linalg.solve` fa
eliminazione di Gauss in un colpo solo: nessuna iterazione, nessun operatore di
Bellman, nessun criterio d'arresto. Se i due numeri coincidono a `1e-8` su
quattro policy diverse (uniforme, deterministica, eps-greedy, stocastica
casuale) e tre valori di `gamma`, l'implementazione e' quella giusta. Il test
costruisce anche `P_pi` e `R_pi` con cicli espliciti, per non riciclare la
stessa `einsum` che sta nell'implementazione.

L'errore di troncamento e' controllato: uscendo con
`||V_{k+1} - V_k||_inf < tol` l'errore residuo rispetto al punto fisso e'
limitato da `tol * gamma / (1 - gamma)`, cioe' `1.9e-11` per `tol = 1e-12` e
`gamma = 0.95`. La tolleranza del confronto, `atol = 1e-8`, ha tre ordini di
grandezza di margine.

## Contrazione: perche' e' un test e non un commento

`||T*V1 - T*V2||_inf <= gamma ||V1 - V2||_inf` e' l'intera dimostrazione di
convergenza di value iteration, compressa in una riga, e si verifica
numericamente in modo diretto: 120 coppie di `V` casuali (con scale diverse,
`0.1`, `1`, `20`, perche' un bug moltiplicativo si vede solo se le scale
variano) per quattro valori di `gamma`, su due MDP. Dimenticare `gamma` sul
termine di bootstrap porta il rapporto a `~1` e il test cade su tutti i
`gamma < 1`.

C'e' pero' un modo stupido di soddisfare la disuguaglianza: restituire una
`T*V` che non dipende da `V`. Il test aggiunge quindi il controllo opposto, che
il rapporto massimo osservato sia almeno `0.5 * gamma`: la contrazione dev'essere
stretta perche' `gamma` e' il vero modulo, non perche' l'operatore e' costante.
Un vincolo verificato per il motivo sbagliato non e' un vincolo.

## Perche' policy iteration vince (e di quanto)

I numeri della suite, con `tol = 1e-12`:

| MDP | gamma | backup di VI | round di PI |
|---|---|---|---|
| gridworld 4x4, slip 0.2 | 0.90 | 44 | 3 |
| MDP casuale 12 stati, 4 azioni | 0.95 | 535 | 3 |

La differenza non e' un dettaglio implementativo, e' strutturale. Value
iteration si avvicina a `V*` solo geometricamente: dopo `k` backup l'errore e'
`O(gamma^k)`, quindi per arrivare a `1e-12` con `gamma = 0.95` servono
`log(1e-12)/log(0.95) ~ 540` passi, ed e' esattamente il numero misurato.
Policy iteration invece **risolve esattamente** `V^pi` a ogni round e poi
migliora; le policy deterministiche sono `A^S`, la sequenza dei loro valori e'
strettamente crescente, quindi il numero di round e' finito e in pratica
piccolissimo. Il prezzo e' che ogni round costa una valutazione completa.

Vale la pena notare perche' sul gridworld il vantaggio e' meno spettacolare
(44 contro 3 invece di 535 contro 3): li' gli stati terminali sono assorbenti e
l'agente ci finisce presto, quindi il residuo di value iteration decade come
`gamma^k` moltiplicato per la probabilita' di non essere ancora assorbiti, che
e' molto piu' rapido di `gamma^k`. Per questo il test usa anche un MDP casuale
senza stati terminali: e' li' che il tasso di convergenza e' davvero `gamma`.

Il confronto delle due policy con `np.array_equal` e' lecito solo perche' nel
gridworld con `slip = 0.2` l'azione ottima e' *strettamente* migliore della
seconda in ogni stato non terminale — il margine minimo fra la prima e la
seconda azione e' `0.0096`, contro un errore numerico di `1e-11`. Con
`slip = 0` ci sono pareggi veri (due percorsi equivalenti verso il goal) e due
implementazioni corrette possono restituire due policy ottime diverse: per
quello la variante deterministica del gridworld non compare in quel test. Negli
stati terminali tutte le `Q` sono esattamente `0.0` e `np.argmax` sceglie
deterministicamente l'indice 0 in entrambi gli algoritmi, quindi nemmeno li'
c'e' ambiguita'.

## Q-learning: perche' l'ambiente dei test e' deterministico

`q_learning` gira su `slip = 0`, e non e' pigrizia. Con transizioni e premi
deterministici il target `r + gamma max_a' Q(s',a')` e' una funzione
deterministica di `Q`, quindi l'aggiornamento a passo costante e' una
contrazione deterministica: per ogni coppia aggiornata,

```
|Q_new(s,a) - Q*(s,a)| <= (1 - alpha + alpha*gamma) ||Q - Q*||_inf
```

cioe' modulo `1 - alpha(1 - gamma) = 0.95` con `alpha = 0.5` e `gamma = 0.9`.
Con gli exploring starts ogni coppia riceve migliaia di aggiornamenti in 4000
episodi e l'errore finisce sotto la precisione macchina — misurato,
`2.2e-16`. La soglia del test e' `1e-3`: tre ordini di grandezza di margine,
nessuna dipendenza dal seed, nessun rischio di flakiness. Con `slip > 0` il
target sarebbe stocastico e `alpha` costante lascerebbe un rumore residuo
`O(alpha)`: si potrebbe rimediare con un `alpha` decrescente, ma questo
significherebbe cambiare la firma richiesta e introdurre una scelta di
scheduling che non e' nelle slide.

Gli **exploring starts** sono parte del contratto, non un dettaglio: sono la
versione praticabile della condizione "ogni coppia `(s,a)` visitata infinite
volte" che serve alla convergenza di Q-learning. Senza, con `eps` piccolo, le
coppie mai visitate restano a zero e il test se ne accorge. Le transizioni
terminali usano `target = r` invece di `r + gamma max Q(s')`: qui e'
irrilevante ai fini del punto fisso, perche' gli stati terminali sono
assorbenti a premio nullo e `Q(terminale, ·)` converge comunque a zero — ma e'
la scrittura corretta in generale ed e' quella richiesta.

## Il punto: off-policy

E' il motivo per cui l'esercizio esiste. Il target di Q-learning contiene
`max_{a'} Q(s',a')`, che e' il valore dell'azione **greedy** in `s'`, mentre
l'azione effettivamente eseguita al passo successivo verra' scelta dalla
eps-greedy e sara' spesso un'altra. Sostituire `max_{a'} Q(s',a')` con
`Q(s', a')` per l'azione `a'` campionata da' SARSA: un algoritmo on-policy, che
converge al valore **della policy che sta eseguendo**, esplorazione compresa.

Il gridworld e' costruito perche' le due cose siano lontane: la trappola `-1`
sta immediatamente sotto il goal `+1`, quindi una policy che il 90% delle volte
si muove a caso ci cade spesso, e il suo valore e' molto peggiore di quello
della policy ottima. Misurato sul gridworld deterministico con `gamma = 0.9`:

| eps | `\|\|Q* - Q^{pi_eps}\|\|_inf` |
|---|---|
| 0.3 | 0.36 |
| 0.5 | 0.63 |
| 0.9 | 1.09 |

Il test `test_q_learning_e_off_policy` gira con `eps = 0.9` e verifica **due
cose**, non una: che `Q` disti da `Q*` meno di `1e-3`, e che disti da
`Q^{pi_eps}` piu' di `0.5 * 1.09`. La seconda meta' e' quella che rende il test
non falsificabile a caso: un'implementazione SARSA sbaglia il primo controllo
*e* passa clamorosamente dall'altra parte nel secondo, e il messaggio d'errore
lo dice esplicitamente. `Q^{pi_eps}` viene calcolata valutando esattamente la
policy eps-greedy rispetto a `Q*`, che e' proprio il punto fisso a cui SARSA
converge. Il test include anche l'assert che il divario costruito sia davvero
`> 0.5`, cosi' se un domani si cambiano i premi del gridworld il test si
lamenta di se stesso invece di diventare vacuo.

## eps-greedy: la formula delle slide, non quella che viene in mente

La slide scrive

```
pi'(a|s) = eps/m + (1 - eps)   se a = argmax Q(s,a)
         = eps/m               altrimenti
```

cioe': con probabilita' `eps` si estrae uniformemente fra **tutte** le `m`
azioni. La versione che viene in mente per prima — "con probabilita' `eps`
prendi un'azione *diversa* dalla greedy" — da' `pi'(a*|s) = 1 - eps`, che e'
una policy diversa, e con `eps = 1` non sceglie mai la greedy. Il test lo vede
in due modi: con `eps = 1` la distribuzione empirica deve essere uniforme
(`0.25` su quattro azioni; la versione sbagliata darebbe `0` sulla greedy e
`0.333` sulle altre), e con `eps = 0.5` deve valere `0.625` sulla greedy contro
il `0.5` della versione sbagliata.

La tolleranza e' `0.02` su `20000` estrazioni per stato: la deviazione standard
di una frequenza binomiale con `p ~ 0.25` e `N = 20000` e' `0.0031`, quindi la
soglia sta a oltre sei deviazioni standard e il test passa qualunque sia il
modo in cui l'implementazione consuma il generatore — cosa che conta, perche'
campionare direttamente da `rng.choice(A, p=...)` e' altrettanto corretto ma
produce una sequenza completamente diversa. Il regime `eps = 0` si controlla
invece in modo esatto, non statistico: dev'essere deterministicamente
l'argmax, sempre.

## Il caso limite `gamma = 0`

Con `gamma = 0` il termine di bootstrap sparisce e restano solo i premi
immediati: `V*(s) = max_a R[s,a]` **esattamente**, `Q = R` identicamente, e la
policy ottima e' miope, `argmax_a R[s,a]`. E' un caso in cui la risposta si
scrive a mano, quindi non serve nessun oracolo. Serve anche a fissare due cose
che altrimenti si potrebbero sbagliare senza accorgersene: che `gamma`
moltiplichi il termine giusto (se moltiplicasse `R`, con `gamma = 0` verrebbe
tutto zero), e che il criterio d'arresto guardi l'incremento e non il valore
(con `gamma = 0` il punto fisso si raggiunge al primo backup e il secondo lo
conferma: `n_iter` dev'essere 2).

Gli stati terminali sono la seconda meta' del test, e per ogni `gamma`: essendo
assorbenti a premio nullo valgono `0` sia sotto `V*` sia sotto qualunque `V^pi`.
Un valore diverso da zero li' significa in genere che si sta incassando il
premio d'ingresso una seconda volta — cioe' che si e' modellato il premio come
funzione dello stato di arrivo invece che della coppia `(s, a)`.

## Collegamento alle slide

`policy_evaluation` e' la slide "Model Based - Iterative Policy Evaluation",
`policy_iteration` e' "Model Based - Policy Iteration" con il suo ciclo
valutazione/miglioramento greedy, `value_iteration` e' "Model Based - Value
Iteration" ("using Bellman optimality in place of Bellman expectation" — la
frase e' letteralmente la specifica di `bellman_backup`). `q_from_v` e'
l'identita' `q_pi(s,a) = R^a_s + gamma sum_{s'} P^a_{ss'} v_pi(s')` della slide
"Action-Value Function", e `greedy_policy` e' la "Finding an Optimal Policy".
`q_learning` e `epsilon_greedy` sono la slide "Q-Learning – Off-policy RL", da
cui sono presi sia l'aggiornamento sia la formula esatta della policy
comportamentale. Tutto quello che viene dopo nel deck — approssimazione di
funzione, DQN, policy gradient, actor-critic — sostituisce la lookup table con
una rete: questo esercizio e' la lookup table, cioe' la cosa che quelle reti
approssimano.
