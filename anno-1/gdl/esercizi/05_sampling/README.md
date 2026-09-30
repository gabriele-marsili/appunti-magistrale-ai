# 05 — Campionamento: rejection, importance, MCMC

## Lezione di riferimento

`Lessons/GDL13 sampling.txt` — *Sampling methods and approximations*. Proprietà dei
sampler, campionamento da distribuzioni univariate (trasformazione inversa,
rejection), campionamento multivariato (ancestor sampling, Gibbs), elementi di
Markov Chain Monte Carlo. È la lezione che sta sotto all'inferenza approssimata
di LDA e, più avanti, a tutto ciò che nel corso si campiona invece di
integrare.

## Il problema

Nella quasi totalità dei casi la distribuzione da cui vogliamo campionare è nota
solo a meno della costante di normalizzazione:

    p(x) = p~(x) / Z,     Z = ∫ p~(x) dx   incalcolabile

Tutti i metodi di questo esercizio lavorano con `p~` e mai con `Z`. Il file
`sampling.py` fornisce già una target bimodale non normalizzata `TARGET_BIMODAL`
e le costanti `Z_TRUE`, `MU_TRUE`, `VAR_TRUE` calcolate per quadratura: sono
l'oracolo esatto contro cui misurare gli stimatori Monte Carlo.

## Cosa devi implementare

| funzione | cosa fa |
| --- | --- |
| `inverse_transform_sample(inv_cdf, n, rng)` | campiona applicando `F^{-1}` a uniformi |
| `rejection_sample(target_unnorm, proposal_sample, proposal_pdf, M, n, rng)` | rejection sampling; restituisce `n` campioni accettati e l'acceptance rate |
| `importance_weights(samples, target_unnorm, proposal_pdf)` | pesi di importanza **non normalizzati** |
| `self_normalized_importance_estimate(f, samples, target_unnorm, proposal_pdf)` | stima di `E_p[f]` senza conoscere `Z` |
| `effective_sample_size(weights)` | `(Σ w)² / Σ w²` |
| `metropolis_hastings(log_target, x0, n, proposal_std, rng)` | MH con random walk gaussiano simmetrico, **in spazio log** |
| `gibbs_bivariate_normal(rho, n, x0, rng)` | Gibbs esatto per la normale bivariata standard con correlazione `rho` |
| `autocorrelation(chain, max_lag)` | autocorrelazione empirica della catena, lag `0..max_lag` |
| `mcmc_effective_sample_size(chain, max_lag=50)` | `N / (1 + 2 Σ ρ_k)` |

## Specifica matematica

**Trasformazione inversa.** Se `U ~ Uniform(0,1)` e `F` è la CDF di `X`, allora
`F^{-1}(U) ~ X`.

**Rejection.** Data `q` normalizzata e `M` con `M q(x) ≥ p~(x)` per ogni `x`:
si estrae `x ~ q` e `u ~ U(0,1)`, si accetta se

    u · M · q(x) ≤ p~(x)

I campioni accettati sono distribuiti esattamente come `p~/Z`. Se anche `p~` è
normalizzata, la probabilità di accettazione vale esattamente `1/M`, perché

    P(accetto) = ∫ [p(x) / (M q(x))] q(x) dx = (1/M) ∫ p(x) dx = 1/M

**Importance sampling.** Con `w_i = p~(x_i)/q(x_i)` e `x_i ~ q`, lo stimatore
*self-normalized*

    E_p[f] ≈ Σ_i w_i f(x_i) / Σ_i w_i

non richiede `Z`, perché il denominatore lo stima implicitamente
(`(1/n) Σ w_i → Z`). Come conseguenza la stima è invariante se moltiplichi `p~`
per una costante qualsiasi. Diagnostica: `ESS = (Σ w)² / Σ w²`, che vale `n` con
pesi uniformi e `1` quando un solo campione porta tutta la massa.

**Metropolis-Hastings.** Proposta `y = x + σ z`, `z ~ N(0,1)`. La proposal è
simmetrica (`q(y|x) = q(x|y)`), quindi i suoi termini si cancellano e

    α = min(1, p~(y) / p~(x))     →     accetta se   log u < log p~(y) − log p~(x)

Se la proposta viene rifiutata, lo stato corrente viene **ripetuto** nella
catena. La costante di normalizzazione sparisce nel rapporto: è tutto il punto.
Il calcolo va fatto in spazio log, non in spazio densità.

**Gibbs per la normale bivariata standard.** Con matrice di covarianza
`[[1, ρ], [ρ, 1]]` le condizionali complete sono

    x1 | x2 ~ N(ρ x2, 1 − ρ²)
    x2 | x1 ~ N(ρ x1, 1 − ρ²)

Uno *sweep* aggiorna `x1` a partire dal valore corrente di `x2`, poi `x2` a
partire dal valore **appena aggiornato** di `x1`.

**Diagnostica MCMC.** Con `x̄` media della catena e denominatore `N` a ogni lag:

    c_k = (1/N) Σ_{t=0}^{N−k−1} (x_t − x̄)(x_{t+k} − x̄),     ρ_k = c_k / c_0

    τ = 1 + 2 Σ_{k=1}^{K} ρ_k     (somma troncata al primo ρ_k ≤ 0)
    ESS = N / τ

## Perché questo esercizio

Scopre tre confusioni, in ordine di gravità.

1. **Che cosa sia davvero la costante di normalizzazione.** Chi non l'ha capito
   scrive `Σ w_i f(x_i) / n` invece di `Σ w_i f(x_i) / Σ w_i`, e ottiene una
   stima sbagliata di un fattore `Z`.
2. **Che l'acceptance rate della rejection non sia un dettaglio implementativo**
   ma esattamente `1/M`: dice quanto lavoro butti via, e spiega perché la
   rejection diventa inutilizzabile in alta dimensione.
3. **Che Gibbs non sia un metodo alternativo a Metropolis-Hastings, ma un caso
   particolare.** Se prendi come proposal la condizionale completa
   `q(x' | x) = p(x'_i | x_{−i})`, il rapporto di accettazione di MH vale
   *identicamente* 1 e la catena non rifiuta mai. Il test
   `test_gibbs_e_metropolis_hastings_con_ratio_uno` lo verifica numericamente
   punto per punto, e verifica anche la controprova: cambiando proposal, il
   rapporto smette di valere 1.

C'è poi la differenza fra i due `effective_sample_size`: quello dei pesi di
importanza misura la degenerazione dei pesi, quello MCMC misura la
correlazione temporale della catena. Sono nozioni diverse con lo stesso nome.

## Vincoli

Solo `numpy` e la standard library. Niente `torch`, `scipy`, `sklearn`,
`matplotlib`. Ogni sorgente di casualità passa dal `rng`
(`numpy.random.Generator`) che ricevi come argomento: mai `np.random.seed`, mai
il modulo `random`, mai `time`.

Non toccare `normal_pdf`, `normal_logpdf`, `TARGET_BIMODAL`,
`_quadrature_reference` e le costanti `Z_TRUE / MU_TRUE / VAR_TRUE`: sono già
fornite e i test le usano.

## Come autovalutarti

```bash
cd /home/claude/gdl/esercizi/05_sampling
python3 -m pytest test_sampling.py -v
```

Tutti i test devono passare. Ogni asserzione ha un messaggio che indica quale
errore concettuale l'ha fatta fallire; leggilo prima di correggere a caso.

## Tempo stimato

90 minuti. Le prime cinque funzioni sono poche righe l'una; Metropolis-Hastings
e Gibbs richiedono attenzione a *quale* valore è quello corrente e a *quando* si
ripete uno stato. La parte lunga è capire perché il test sul rapporto uguale a 1
funziona.

## Domande d'orale collegate

1. Nel rejection sampling, che cosa determina l'acceptance rate e perché il
   metodo degrada in alta dimensione?
2. Perché l'importance sampling self-normalized funziona anche se non conosciamo
   la costante di normalizzazione, e a che prezzo (bias, varianza)?
3. Perché il rapporto di accettazione di Metropolis-Hastings non richiede la
   costante di normalizzazione della target?
4. In che senso Gibbs sampling è un caso particolare di Metropolis-Hastings?
   Quanto vale il suo rapporto di accettazione e perché?
5. Che cosa significa che una catena MCMC ha `p` come distribuzione invariante,
   e come lo distingueresti empiricamente da una catena che converge a
   qualcos'altro?
