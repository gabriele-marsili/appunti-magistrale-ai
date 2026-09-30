# 02 — EM per Gaussian Mixture Models e model selection con BIC

## Lezione di riferimento

`Lessons/GDL8 learning hidden.pdf` — *Learning with hidden variables*: modelli a variabili
latenti, maximum likelihood con variabili non osservate, algoritmo Expectation-Maximization,
exact maximum likelihood learning in mixture models. Per la gaussiana multivariata e la
regola di Bayes usata nell'E-step: `Lessons/GDL2 prob refresh.pdf`.

L'esercizio ricalca il **Midterm 1** del corso (GMM + EM + BIC, solo numpy).

## Il modello

Una mistura di K gaussiane su $\mathbb{R}^D$ con variabile latente discreta $z_n \in \{1,\dots,K\}$:

$$p(z_n = k) = \pi_k, \qquad p(x_n \mid z_n = k) = \mathcal{N}(x_n \mid \mu_k, \Sigma_k)$$

$$p(x_n \mid \theta) = \sum_{k=1}^{K} \pi_k \, \mathcal{N}(x_n \mid \mu_k, \Sigma_k),
\qquad \sum_k \pi_k = 1, \; \pi_k \ge 0$$

La log-likelihood dei dati osservati contiene un logaritmo di somma e non si annulla in forma
chiusa: è esattamente il motivo per cui serve EM.

$$\ell(\theta) = \sum_{n=1}^{N} \log \sum_{k=1}^{K} \pi_k \, \mathcal{N}(x_n \mid \mu_k, \Sigma_k)$$

**E-step** — posterior sulla variabile latente ai parametri correnti (responsabilità):

$$\gamma_{nk} = p(z_n = k \mid x_n, \theta^{(t)})
= \frac{\pi_k \, \mathcal{N}(x_n \mid \mu_k, \Sigma_k)}{\sum_{j} \pi_j \, \mathcal{N}(x_n \mid \mu_j, \Sigma_j)}$$

**M-step** — massimizzazione in forma chiusa di $Q(\theta \mid \theta^{(t)}) = \mathbb{E}_{z \mid x, \theta^{(t)}}[\log p(x, z \mid \theta)]$, con $N_k = \sum_n \gamma_{nk}$:

$$\pi_k = \frac{N_k}{N}, \qquad
\mu_k = \frac{1}{N_k}\sum_n \gamma_{nk} x_n, \qquad
\Sigma_k = \frac{1}{N_k}\sum_n \gamma_{nk} (x_n - \mu_k)(x_n - \mu_k)^\top$$

**Densità gaussiana multivariata:**

$$\log \mathcal{N}(x \mid \mu, \Sigma) = -\tfrac{1}{2}\Big( D \log 2\pi + \log|\Sigma| + (x-\mu)^\top \Sigma^{-1} (x-\mu) \Big)$$

**Model selection.** Il numero di componenti K non si può scegliere massimizzando la
likelihood (cresce sempre con K). Si penalizza la complessità:

$$\text{BIC} = -2\,\ell(\hat\theta) + p \log N, \qquad
\text{AIC} = -2\,\ell(\hat\theta) + 2p$$

con `p` numero di parametri liberi; **in questa convenzione si sceglie il valore più basso**.
Per una GMM a covarianze piene:

$$p = \underbrace{(K-1)}_{\text{pesi}} + \underbrace{KD}_{\text{medie}} + \underbrace{K\,\tfrac{D(D+1)}{2}}_{\text{covarianze simmetriche}}$$

## Cosa devi implementare

Nel file `em_gmm_bic.py`, tutte le funzioni marcate `# TODO`:

- `logsumexp(A, axis=-1)` — riduzione log-sum-exp. **Non è fornita apposta: scriverla in modo
  numericamente stabile è parte dell'esercizio.** La versione ingenua
  `np.log(np.sum(np.exp(A), axis))` va in overflow o restituisce `-inf`/`NaN` appena gli
  esponenti si allontanano da zero; serve lo shift per il massimo, e serve gestire il caso in
  cui tutti gli elementi lungo l'asse valgano `-inf`.
- `log_gaussian_pdf(X, mu, Sigma) -> (N,)` — log-densità gaussiana multivariata via Cholesky.
- `gaussian_pdf(X, mu, Sigma) -> (N,)` — densità, calcolata esponenziando la log-densità.
- `init_params(X, K, rng) -> (pis, mus, Sigmas)` — k-means++ sulle medie, implementato a mano;
  pesi uniformi; covarianze inizializzate alla covarianza empirica del dataset.
- `e_step(X, pis, mus, Sigmas) -> (resp, loglik)` — responsabilità `(N,K)` normalizzate per
  riga e log-likelihood totale, tutto in spazio log.
- `m_step(X, resp, reg=1e-6) -> (pis, mus, Sigmas)` — aggiornamenti in forma chiusa, con `reg`
  sulla diagonale delle covarianze.
- `fit_gmm(X, K, n_iter=200, tol=1e-6, seed=0, reg=1e-6) -> dict` — ciclo EM completo, con
  `"loglik_history"`, `"n_iter"` e `"resp"` coerenti con i parametri finali.
- `n_params_gmm(K, D) -> int` — parametri liberi con covarianze piene.
- `bic(loglik, n_params, N) -> float` e `aic(loglik, n_params) -> float`.
- `select_k(X, k_values, seed=0, **kw) -> dict` — scelta di K per BIC minimo.
- `predict(X, model) -> (N,)` — hard assignment via argmax delle responsabilità.

`make_blobs_like(n_per_cluster, means, covs, seed)` è già fornito e non va toccato.

## Perché questo esercizio

Perché smaschera tre confusioni in un colpo solo: che la log-likelihood da monitorare sia
quella dei dati *completi* $\log p(x,z)$ e non quella marginale $\log p(x)$ (nel primo caso la
curva non è monotona e il criterio di stop non ha senso); che le responsabilità si possano
calcolare come rapporto di densità in spazio lineare (con punti lontani dalle componenti
diventa `0/0`); e che il BIC si "massimizzi" — dipende dalla convenzione di segno, e sceglierla
male fa selezionare sistematicamente il K più grande.

## Vincoli

Solo `numpy` e la standard library. Niente `scipy` (quindi niente `scipy.special.logsumexp`,
`scipy.stats.multivariate_normal`, `scipy.linalg.solve_triangular`), niente `sklearn`,
niente `torch`, niente `matplotlib`. Nessuna sorgente di casualità oltre a
`np.random.default_rng(seed)`: mai `np.random.seed`, mai il modulo `random`, mai `time`.

## Come autovalutarti

```bash
cd /home/claude/gdl/esercizi/02_em_gmm_bic
python3 -m pytest test_em_gmm_bic.py -v
```

I test coprono: monotonia della log-likelihood su 30 combinazioni (dataset, K, seed),
normalizzazione delle responsabilità, oracolo in forma chiusa per K=1, recupero di K=3 via
BIC su tre gaussiane separate, stabilità numerica su punti lontanissimi, caso limite K=N,
e conteggio dei parametri.

Per confrontarti con la soluzione di riferimento:

```bash
GDL_SOL=1 python3 -m pytest test_em_gmm_bic.py -v
```

## Tempo stimato

2-3 ore se hai già presente la derivazione di EM; 4-5 se è la prima volta che scrivi un
E-step in spazio log. La parte che ruba più tempo non è la matematica, è far tornare gli assi
delle responsabilità e capire perché la log-likelihood scende.

## Domande d'orale collegate

1. Perché la log-likelihood di una mistura non si massimizza in forma chiusa, mentre quella di
   una singola gaussiana sì? Cosa cambia esattamente quando la variabile latente è osservata?
2. Dimostra (o argomenta) che EM non può far decrescere la log-likelihood dei dati osservati.
   Da dove viene il lower bound, e quando è stretto?
3. Perché la likelihood di una mistura gaussiana a covarianze piene è illimitata superiormente,
   e cosa si fa in pratica per evitare il collasso di una componente?
4. Perché non si sceglie K massimizzando la likelihood? Cosa penalizza il BIC rispetto all'AIC,
   e in che senso il BIC è "consistente" e l'AIC no?
