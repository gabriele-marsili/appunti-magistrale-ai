# 04 — Variational Inference: CAVI su una mixture di gaussiane

## Lezione di riferimento

`Lessons/GDL11 variational.txt` — Variational Inference: modelli a variabili latenti
intrattabili, lower bound della massima verosimiglianza (ELBO), approssimazione
variazionale come forma generalizzata di EM.

Il modello e' quello canonico del tutorial di Blei, Kucukelbir e McAuliffe
("Variational Inference: A Review for Statisticians", sezione 3): mixture di
gaussiane univariate con varianza nota.

## Il modello

Generativo:

```
mu_k         ~ N(0, sigma0^2)          k = 1..K
c_i          ~ Cat(1/K, ..., 1/K)      i = 1..N
x_i | c_i=k  ~ N(mu_k, 1)
```

Le medie `mu` e le assegnazioni `c` sono latenti. La marginale
`p(x) = sum_c int p(mu) p(c) p(x | c, mu) dmu` richiede `K^N` termini: intrattabile.

Famiglia variazionale mean-field:

```
q(mu, c) = prod_k N(mu_k; m_k, s2_k) * prod_i Cat(c_i; phi_i)
```

I parametri variazionali sono `m` (K,), `s2` (K,), `phi` (N, K).

Vale la decomposizione esatta

```
log p(x) = ELBO(q) + KL( q(mu, c) || p(mu, c | x) )
```

con

```
ELBO(q) = E_q[log p(mu)] + E_q[log p(c)] + E_q[log p(x | c, mu)] + H[q(mu)] + H[q(c)]
```

Poiche' la KL e' non negativa, l'ELBO e' un **lower bound** di `log p(x)` per
qualunque `q`, e massimizzarlo equivale a minimizzare la KL dalla posterior vera.

CAVI (Coordinate Ascent Variational Inference) itera l'aggiornamento della regola
generica del mean-field

```
log q*(z_j)  =  E_{q(z_-j)}[ log p(x, z) ] + const
```

una coordinata alla volta. Ogni aggiornamento e' il massimo esatto dell'ELBO in
quel blocco, quindi l'ELBO non puo' mai scendere.

## Cosa devi implementare

In `cavi.py`, le funzioni marcate `# TODO`:

- `log_norm_pdf(x, mu, var)` — log-densita' gaussiana univariata, vettorizzata.
- `elbo(x, phi, m, s2, sigma0_sq)` — ELBO in **forma chiusa**, valido per qualunque `q` mean-field, non solo all'ottimo.
- `update_phi(x, m, s2)` — aggiornamento coordinato di `q(c)`, shape `(N, K)`, righe normalizzate.
- `update_mu(x, phi, sigma0_sq)` — aggiornamento coordinato di `q(mu)`, ritorna `(m, s2)` entrambi shape `(K,)`.
- `cavi(x, K, sigma0_sq=10.0, n_iter=200, tol=1e-8, seed=0)` — il ciclo completo; ritorna un dict con `"m"`, `"s2"`, `"phi"`, `"elbo_history"`, `"n_iter"`. L'inizializzazione e' fissata nella docstring: rispettala, i test ci contano.
- `kl_gaussians(m1, v1, m2, v2)` — KL fra due gaussiane univariate, forma chiusa.
- `log_marginal_bound_gap(x, phi, m, s2, sigma0_sq, log_evidence)` — ritorna `log_evidence - elbo`, cioe' `KL(q || posterior)`.

Sono gia' forniti e non vanno toccati: `make_mixture_data` (generatore di dati) e
`elbo_monte_carlo` (stima Monte Carlo dell'ELBO, usata come oracolo indipendente
per verificare che la tua formula analitica calcoli davvero la stessa quantita').

## Perche' questo esercizio

Scopre tre confusioni tipiche. La prima: credere che l'ELBO sia
un'*approssimazione* della log-evidenza, quando e' un *bound inferiore* — la
disuguaglianza vale per ogni `q`, anche pessimo, e il test con `N=4, K=2` la
verifica contro la log-evidenza calcolata esattamente per enumerazione. La
seconda: nell'aggiornamento di `q(c)` entra `E[mu_k^2] = m_k^2 + s2_k`, non
`E[mu_k]^2 = m_k^2`; usare il momento sbagliato lascia l'ELBO ancora monotono, ma
gli update smettono di essere massimi condizionati — la monotonia da sola non
basta a dirti che il codice e' giusto. La terza: dimenticare i termini di entropia
di `q`, che e' la differenza fra ottimizzare l'ELBO e ottimizzare una semplice
log-verosimiglianza attesa.

## Vincoli

Solo `numpy` e la stdlib. Niente `torch`, `scipy`, `sklearn`, `matplotlib`.
Determinismo: usa `np.random.default_rng(seed)`, mai `np.random.seed` o `random`.
`elbo` deve essere analitica: non e' ammessa una stima Monte Carlo.

## Come autovalutarti

```bash
cd /home/claude/gdl/esercizi/04_variational_cavi
python3 -m pytest test_cavi.py -v
```

Sullo skeleton falliscono tutti i test. Quando passano tutti e 12, hai finito.
Per confrontarti con la soluzione di riferimento:

```bash
GDL_SOL=1 python3 -m pytest test_cavi.py -v
```

## Tempo stimato

Fra 90 e 120 minuti. La parte lunga e' derivare a mano l'ELBO termine per termine
e i due update coordinati; il codice, una volta scritte le formule, sono venti
righe.

## Domande d'orale collegate

1. Da dove viene la disuguaglianza `log p(x) >= ELBO(q)` e cosa misura esattamente
   il gap? Cosa serve perche' sia zero?
2. Perche' CAVI converge, e a cosa converge? Che garanzia hai sull'ottimo trovato?
3. Ricava l'aggiornamento coordinato `q*(z_j) propto exp(E_{q(-j)}[log p(x, z)])`.
   Nel modello mixture, quali momenti di `q(mu)` compaiono nell'update di `q(c)` e perche'?
4. In che senso la variational inference generalizza l'EM? Cosa diventa l'E-step e
   cosa il M-step, e cosa succede quando la posterior esatta e' nella famiglia
   variazionale?
