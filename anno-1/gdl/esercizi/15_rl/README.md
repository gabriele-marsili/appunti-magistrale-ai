# Esercizio 15 — MDP tabellari: value iteration, policy iteration, Q-learning

## Lezione di riferimento

`Lessons/GDL34 RL` — (Deep) Reinforcement Learning, Fundamentals. La parte
model based (iterative policy evaluation, policy iteration, value iteration) e
la prima parte model free (Q-learning off-policy con esplorazione eps-greedy).
Niente approssimazione di funzione: qui `V` e `Q` sono lookup table, come nella
slide "Value Function Approximation" prima che diventino reti.

## Convenzioni (non sono un dettaglio, sono meta' dell'esercizio)

MDP tabellare `(S, A, P, R, gamma)`, stati `{0..S-1}`, azioni `{0..A-1}`.

| oggetto | shape | significato | normalizzazione |
|---|---|---|---|
| `P` | `(S, A, S)` | `P[s, a, s'] = P(S_{t+1} = s' \| S_t = s, A_t = a)` | `P.sum(axis=2) == 1` |
| `R` | `(S, A)` | `R[s, a] = E[R_{t+1} \| S_t = s, A_t = a]` | — |
| `V` | `(S,)` | valore dello stato | — |
| `Q` | `(S, A)` | valore della coppia stato-azione | — |
| `pi` | `(S, A)` | `pi[s, a] = pi(a \| s)` | `pi.sum(axis=1) == 1` |

In `P` **il primo asse e' lo stato di partenza e l'ultimo e' lo stato di
arrivo**. L'unica contrazione lecita con `V` e' sull'ultimo asse, e produce
shape `(S, A)`:

```
P @ V        equivalente a    np.einsum("sat,t->sa", P, V)
```

Contrarre il primo asse (`np.einsum("tas,t->sa", P, V)`) produce anch'esso
shape `(S, A)`: nessuna eccezione, nessun warning, solo numeri sbagliati. Il
gridworld usato nei test e' asimmetrico apposta (goal in alto a destra,
trappola subito sotto) e quella mutazione fa cadere 9 test su 12.

`R[s, a]` e' gia' un valore **atteso** sul prossimo stato: non c'e' nessuna
somma su `s'` da fare sopra. Il premio si incassa **uscendo** da `s`, non
entrando.

Le policy sono sempre matrici `(S, A)` con righe che sommano a 1. Una policy
deterministica si rappresenta **one-hot**. Serve perche' `policy_evaluation`
abbia un solo tipo di input da gestire e perche' due policy ottime si possano
confrontare con `np.array_equal`.

Gli stati terminali sono **assorbenti a premio nullo**: `P[s, a, s] = 1` e
`R[s, a] = 0` per ogni `a`. Ne segue `V*(s) = 0` esattamente, per ogni `gamma`.

## Formule

Le tre equazioni, in notazione delle slide.

Bellman **atteso** (valuta una policy data):

```
V^pi(s) = sum_a pi(a|s) [ R[s,a] + gamma sum_{s'} P[s,a,s'] V^pi(s') ]
```

Bellman **ottimo** (valuta la policy migliore):

```
V*(s) = max_a [ R[s,a] + gamma sum_{s'} P[s,a,s'] V*(s') ]
Q*(s,a) = R[s,a] + gamma sum_{s'} P[s,a,s'] V*(s')
pi*(s) = argmax_a Q*(s,a)
```

La differenza fra i due backup e' una parola: `sum_a pi(a|s)` contro `max_a`.

Iterative policy evaluation, in forma matriciale, con

```
P_pi[s, s'] = sum_a pi[s,a] P[s,a,s']        (S, S)
R_pi[s]     = sum_a pi[s,a] R[s,a]           (S,)
```

itera `V <- R_pi + gamma * (P_pi @ V)`; il suo punto fisso e' l'unica soluzione
del sistema lineare `(I - gamma P_pi) V = R_pi`.

Value iteration itera `V_{k+1} = T* V_k`. L'operatore `T*` e' una contrazione
di modulo `gamma` in norma infinito,

```
|| T*V1 - T*V2 ||_inf <= gamma || V1 - V2 ||_inf
```

ed e' questo, e nient'altro, a garantire la convergenza.

Q-learning (model free, off-policy):

```
Q(s,a) <- Q(s,a) + alpha [ r + gamma max_{a'} Q(s',a') - Q(s,a) ]
```

con azione comportamentale campionata dalla eps-greedy delle slide

```
pi'(a|s) = eps/m + (1 - eps)   se a = argmax_{a'} Q(s,a')
         = eps/m               altrimenti                  (m = numero azioni)
```

Nota bene la formula: con probabilita' `eps` si estrae **uniformemente fra
tutte le m azioni, greedy compresa**. Non e' "con probabilita' eps prendi
un'azione non greedy": quella darebbe `pi'(a*|s) = 1 - eps` e con `eps = 1` non
sceglierebbe mai l'azione greedy.

## Cosa devi implementare

In `rl.py`, le funzioni marcate `# TODO`:

- `q_from_v(V, P, R, gamma) -> Q` — `(S, A)`, la `q_pi` indotta da una `V`.
- `greedy_policy(Q) -> pi` — `(S, A)` one-hot sull'argmax, pareggi all'indice minore.
- `bellman_backup(V, P, R, gamma) -> (V_new, pi)` — un passo di backup di ottimalita' piu' la policy greedy.
- `value_iteration(P, R, gamma, tol, max_iter) -> (V, pi, n_iter)`.
- `policy_evaluation(pi, P, R, gamma, tol, max_iter) -> V` — `V^pi` iterativa.
- `policy_iteration(P, R, gamma, tol, max_iter) -> (V, pi, n_iter)` — policy iniziale obbligatoria: azione 0 ovunque.
- `epsilon_greedy(Q, s, eps, rng) -> a` — un'azione campionata, intero.
- `q_learning(env_step, S, A, gamma, alpha, eps, n_episodes, rng, max_steps) -> Q` — model free, exploring starts.

`make_gridworld`, `make_env_step`, `make_random_mdp` e `render_policy` sono
gia' scritte: sono l'ambiente e gli strumenti di debug, non l'esercizio. Non
toccarle. In particolare `env_step(s, a, rng) -> (s_next, reward, done)` e'
l'**unico** accesso all'ambiente consentito dentro `q_learning`: se li' dentro
compaiono `P` o `R`, non e' model free.

## Perche' questo esercizio

Perche' costringe a separare due coppie di cose che a lezione sembrano la
stessa e non lo sono. La prima e' **Bellman atteso contro Bellman ottimo**: la
media pesata `sum_a pi(a|s)` e il massimo `max_a` occupano lo stesso posto
nella formula, girano entrambi senza errori, e mettere il `max` dentro
`policy_evaluation` produce silenziosamente `V*` al posto di `V^pi`. La
seconda, ed e' il cuore, e' **on-policy contro off-policy**: nel target di
Q-learning c'e' `max_{a'} Q(s',a')`, non la `Q` dell'azione che la policy
comportamentale eseguira' davvero. Scrivere la seconda da' SARSA, che converge
al valore della policy esplorativa — nel gridworld dei test, con la trappola
accanto al goal, una cosa lontana `1.1` in norma infinito da `Q*`. La suite
misura esattamente quella distanza.

## Vincoli

Solo `numpy` e la stdlib. Niente torch, niente gym, niente scipy, niente
sklearn, niente matplotlib. Nessuna soluzione in forma chiusa dentro
`policy_evaluation`: deve essere iterativa (il sistema lineare risolto con
`np.linalg.solve` e' l'oracolo del test, non l'implementazione). Determinismo
assoluto: si usa il `rng` passato come argomento, mai `np.random.seed`, mai il
modulo `random`, mai `time`.

## Come autovalutarti

```bash
cd /home/claude/gdl/esercizi/15_rl
python3 -m pytest test_rl.py -v
```

Se vuoi vedere la suite passare sulla soluzione di riferimento:

```bash
GDL_SOL=1 python3 -m pytest test_rl.py -v
```

`render_policy(pi, 4, 4, terminal)` stampa la policy come griglia di frecce:
serve piu' di quanto sembri, una policy sbagliata si riconosce a occhio.

## Tempo stimato

2 ore se hai gia' presente la differenza fra le due equazioni di Bellman e devi
solo scrivere il codice. 3-4 ore partendo dalle sole slide, di cui la maggior
parte spesa su `q_learning` e sull'orientamento degli assi di `P`.

## Domande d'orale collegate

1. In che senso Q-learning e' *off-policy*? Che cosa impara se la policy
   comportamentale e' completamente casuale, e perche' e' diverso da quello che
   imparerebbe SARSA nella stessa situazione?
2. Policy iteration converge in pochissimi round e value iteration in
   centinaia di backup. Da dove viene la differenza, visto che risolvono lo
   stesso problema? Che cosa costa un round di policy iteration?
3. Perche' value iteration converge? Che ruolo ha esattamente `gamma` nella
   dimostrazione, e che cosa succede quando `gamma -> 1`?
4. Scrivi l'equazione di Bellman attesa e quella ottima. Dove sta la
   differenza, e che cosa calcoli se metti un `max` dentro la valutazione di
   una policy?
