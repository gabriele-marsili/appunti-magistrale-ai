# Esercizio 03 — Hidden Markov Model: forward-backward, Viterbi, Baum-Welch

## Lezione di riferimento

`Lessons/GDL9-10 hmm` — Hidden Markov Models. Inferenza esatta su una catena
con variabili osservate e non osservate: sum-product message passing (algoritmo
forward-backward), max-product message passing (Viterbi), e l'algoritmo EM per
gli HMM (Baum-Welch).

## Convenzioni (non sono un dettaglio, sono meta' dell'esercizio)

HMM discreto con `K` stati latenti e `M` simboli osservabili.

| oggetto | shape | significato | normalizzazione |
|---|---|---|---|
| `pi` | `(K,)` | `pi[k] = P(z_1 = k)` | `pi.sum() == 1` |
| `A` | `(K, K)` | `A[i, j] = P(z_t = j \| z_{t-1} = i)` | `A.sum(axis=1) == 1` |
| `B` | `(K, M)` | `B[k, o] = P(x_t = o \| z_t = k)` | `B.sum(axis=1) == 1` |
| `obs` | `(T,)` int | una sequenza, valori in `{0..M-1}` | — |

In `A` **la riga e' lo stato di partenza e la colonna e' lo stato di arrivo**.
Quindi una distribuzione riga `p` si propaga in avanti con `p @ A`, mentre un
messaggio `v` si propaga all'indietro con `A @ v`. Scambiare i due usi e'
l'errore piu' frequente in assoluto: il codice gira lo stesso, non solleva
nessuna eccezione, e restituisce numeri perfettamente plausibili e sbagliati.
Le matrici usate nei test sono deliberatamente asimmetriche proprio per
smascherare questo.

## Formule

Forward-backward **scalato** (versione di Rabiner, l'unica che sopravvive a
`T` grande senza underflow):

```
alpha[t, k] = P(z_t = k | obs[0..t])                        ogni riga somma a 1
scaling[t]  = P(obs[t] | obs[0..t-1]),   scaling[0] = P(obs[0])
beta[t, k]  = P(obs[t+1..T-1] | z_t = k) / prod_{s>t} scaling[s],  beta[T-1]=1
```

Ricorsioni:

```
alpha[0] ∝ pi * B[:, obs[0]]
alpha[t] ∝ (alpha[t-1] @ A) * B[:, obs[t]]         scaling[t] = costante di norm.
beta[t]  = (A @ (B[:, obs[t+1]] * beta[t+1])) / scaling[t+1]
```

Da cui:

```
log P(obs)  = sum_t log(scaling[t])
gamma[t, k] = P(z_t = k | obs) = alpha[t, k] * beta[t, k]
xi[t, i, j] = P(z_t = i, z_{t+1} = j | obs)
            = alpha[t, i] * A[i, j] * B[j, obs[t+1]] * beta[t+1, j] / scaling[t+1]
```

Viterbi (max-product), **in spazio logaritmico**:

```
delta[0, k] = log pi[k] + log B[k, obs[0]]
delta[t, j] = max_i ( delta[t-1, i] + log A[i, j] ) + log B[j, obs[t]]
psi[t, j]   = argmax_i ( delta[t-1, i] + log A[i, j] )
```

con backtracking dei `psi` per ricostruire il path. Le probabilita' nulle
danno `-inf`: e' il valore corretto, non va sostituito con un epsilon.

Baum-Welch (EM), M-step:

```
pi_new     = gamma[0]
A_new[i,j] = sum_{t=0}^{T-2} xi[t,i,j] / sum_{t=0}^{T-2} gamma[t,i]
B_new[k,o] = sum_{t: obs[t]=o} gamma[t,k] / sum_{t=0}^{T-1} gamma[t,k]
```

## Cosa devi implementare

In `hmm.py`, le funzioni marcate `# TODO`:

- `forward(obs, pi, A, B) -> (alpha, scaling)` — forward scalato, `alpha` (T,K) con righe a somma 1, `scaling` (T,).
- `backward(obs, pi, A, B, scaling) -> beta` — backward scalato con **gli stessi** fattori.
- `log_likelihood(obs, pi, A, B) -> float` — `sum(log(scaling))`.
- `posterior_marginals(obs, pi, A, B) -> gamma` — (T,K), `P(z_t = k | obs)`.
- `xi(obs, pi, A, B) -> ndarray (T-1, K, K)` — `P(z_t = i, z_{t+1} = j | obs)`.
- `viterbi(obs, pi, A, B) -> (path, logprob)` — MAP congiunto, in log.
- `baum_welch(obs, K, M, n_iter=100, tol=1e-6, seed=0) -> dict` — con chiavi `"pi"`, `"A"`, `"B"`, `"loglik_history"`, `"n_iter"`.

`sample_hmm`, `random_hmm` e `forward_naive` sono gia' scritte: generano i dati
e fanno da oracolo brute-force (enumerazione delle `K^T` traiettorie). Non
toccarle.

## Perche' questo esercizio

Perche' costringe a separare due cose che a lezione sembrano la stessa e non lo
sono: **i marginali posteriori `gamma[t]` e la sequenza MAP di Viterbi**. La
sequenza degli argmax di `gamma` puo' essere una traiettoria a probabilita'
zero, e i test contengono un HMM costruito apposta in cui questo succede.
Secondariamente, obbliga a fare i conti con lo scaling del forward-backward e
con l'orientamento di `A`, che sono i due punti dove si sbaglia in silenzio.

## Vincoli

Solo `numpy` e la stdlib. Niente torch, scipy, sklearn, matplotlib. Niente loop
su tutte le traiettorie negli algoritmi veri: il costo deve essere `O(T K^2)`,
non `O(K^T)`. Determinismo assoluto: `np.random.default_rng(seed)`, mai
`np.random.seed` e mai il modulo `random`.

## Come autovalutarti

```bash
cd /home/claude/gdl/esercizi/03_hmm
python3 -m pytest test_hmm.py -v
```

Se vuoi vedere la suite passare sulla soluzione di riferimento:

```bash
GDL_SOL=1 python3 -m pytest test_hmm.py -v
```

## Tempo stimato

2 ore e mezza se hai gia' visto il forward-backward e ti serve solo rimetterlo
in piedi. 4-5 ore partendo dalle sole slide, di cui buona parte spesa a
debuggare lo scaling di `beta` e l'orientamento di `A`.

## Domande d'orale collegate

1. Perche' la sequenza degli stati piu' probabili istante per istante non
   coincide in generale con la sequenza di stati piu' probabile? Sai fare un
   esempio in cui la prima ha probabilita' zero?
2. Che cosa sono esattamente i fattori di scaling del forward, e perche'
   permettono di calcolare `log P(x)` senza mai rappresentare `P(x)`?
3. Nel forward-backward, quali messaggi sono sum-product e quali max-product?
   Che cosa cambia nell'algoritmo quando si passa dagli uni agli altri?
4. Nell'M-step di Baum-Welch, perche' il denominatore della stima di `A` somma
   `gamma` fino a `T-2` e quello di `B` fino a `T-1`? Perche' la
   log-likelihood non puo' scendere?
