# Guida al Midterm 1 - GMM con EM Algorithm

## Panoramica del compito

Devi implementare un **Gaussian Mixture Model (GMM)** addestrato tramite l'algoritmo **Expectation-Maximization (EM)**, con selezione del modello tramite **BIC**. Nello specifico:

1. `log_likelihood(samples)` - calcola log P(X|theta)
2. `fit(samples)` - addestra i parametri con EM
3. `bic(samples)` - calcola il Bayesian Information Criterion
4. Selezionare il miglior k tra {1, ..., 6} massimizzando il BIC

**Vincolo importante:** la matrice di covarianza e' **diagonale**, quindi per ogni Gaussiana k memorizzi solo un vettore di varianze `sigma_k` di dimensione d (non una matrice d x d).

---

## 1. Cos'e' un GMM

Un GMM modella i dati come provenienti da una **miscela di K distribuzioni Gaussiane**. Ogni dato x viene generato da:
1. Scegliere una componente k con probabilita' pi_k (variabile latente z)
2. Campionare x dalla Gaussiana N(mu_k, Sigma_k)

La densita' di probabilita' per un singolo punto x e':

```
P(x | theta) = sum_{k=1}^{K} pi_k * N(x | mu_k, Sigma_k)
```

dove:
- **pi_k**: peso della k-esima componente (mixing coefficient), con sum_k pi_k = 1
- **mu_k**: vettore media della k-esima Gaussiana (dimensione d)
- **Sigma_k**: matrice di covarianza (nel nostro caso diagonale, quindi un vettore di d varianze)

### Gaussiana multivariata con covarianza diagonale

Dato che Sigma_k e' diagonale, la Gaussiana si semplifica. Se sigma_k = (sigma_{k,1}^2, ..., sigma_{k,d}^2) sono le varianze lungo ogni dimensione:

```
N(x | mu_k, sigma_k) = prod_{l=1}^{d} (1 / sqrt(2 * pi * sigma_{k,l}^2)) * exp(-(x_l - mu_{k,l})^2 / (2 * sigma_{k,l}^2))
```

In log-space (molto piu' stabile numericamente):

```
log N(x | mu_k, sigma_k) = -d/2 * log(2*pi) - 1/2 * sum_{l=1}^{d} log(sigma_{k,l}^2) - 1/2 * sum_{l=1}^{d} (x_l - mu_{k,l})^2 / sigma_{k,l}^2
```

Dove `sigma_{k,l}^2` e' la varianza (il quadrato della deviazione standard) della componente k sulla dimensione l. Nel notebook `_sigma` ha shape `(n_categories, n_features)` e rappresenta le **varianze** (o le deviazioni standard -- decidi tu, ma sii coerente).

---

## 2. Log-Likelihood

La **log-likelihood** dell'intero dataset X = {x_1, ..., x_N} e':

```
log P(X | theta) = sum_{j=1}^{N} log P(x_j | theta)
                  = sum_{j=1}^{N} log [ sum_{k=1}^{K} pi_k * N(x_j | mu_k, sigma_k) ]
```

### Trucco log-sum-exp per stabilita' numerica

Il calcolo `log(sum_k exp(a_k))` e' numericamente instabile. Si usa il trucco:

```
log(sum_k exp(a_k)) = max(a) + log(sum_k exp(a_k - max(a)))
```

Applicato al nostro caso, per ogni campione j:

```
a_{j,k} = log(pi_k) + log N(x_j | mu_k, sigma_k)

log P(x_j | theta) = logsumexp_k(a_{j,k})
```

Poi sommi su tutti i campioni j per ottenere la log-likelihood totale (uno scalare).

---

## 3. Algoritmo EM

L'EM e' un algoritmo iterativo a due passi che massimizza la log-likelihood quando ci sono variabili latenti (nel nostro caso z, l'assegnamento ai cluster).

### Inizializzazione dei parametri

L'inizializzazione e' **fondamentale** perche' EM converge solo a minimi locali. Strategie possibili:
- **Random**: pesi uniformi, medie casuali, varianze unitarie
- **Campionamento**: scegli K punti dal dataset come medie iniziali
- **K-means++**: seleziona le medie iniziali in modo che siano ben distanziate tra loro (consigliata)

Suggerimento pratico:
- `pi`: inizializza a 1/K per tutti (uniforme)
- `mu`: scegli K punti a caso dal dataset (o usa k-means++)
- `sigma`: inizializza a varianze unitarie o alla varianza globale dei dati

### E-Step (Expectation)

Calcola le **responsabilita'** (posterior) gamma_{j,k} = P(z_j = k | x_j, theta^(t)):

```
gamma_{j,k} = P(z_j = k | x_j, theta^(t))
             = (pi_k * N(x_j | mu_k, sigma_k)) / (sum_{k'=1}^{K} pi_{k'} * N(x_j | mu_{k'}, sigma_{k'}))
```

In pratica, per stabilita' numerica, lavora in log-space:
1. Calcola `log_num_{j,k} = log(pi_k) + log N(x_j | mu_k, sigma_k)`
2. Calcola `log_denom_j = logsumexp_k(log_num_{j,k})`
3. `gamma_{j,k} = exp(log_num_{j,k} - log_denom_j)`

Il risultato e' una matrice (N, K) dove ogni riga somma a 1.

### M-Step (Maximization)

Aggiorna i parametri usando le responsabilita':

Definisci prima la "conta effettiva" per ogni componente k:
```
N_k = sum_{j=1}^{N} gamma_{j,k}
```

Poi aggiorna:

**Pesi:**
```
pi_k^(new) = N_k / N
```

**Medie:**
```
mu_k^(new) = (1 / N_k) * sum_{j=1}^{N} gamma_{j,k} * x_j
```

**Varianze (diagonale):**
```
sigma_{k,l}^2 (new) = (1 / N_k) * sum_{j=1}^{N} gamma_{j,k} * (x_{j,l} - mu_{k,l}^(new))^2
```

Nota: usa le medie **appena aggiornate** per calcolare le nuove varianze.

### Criterio di convergenza

Ripeti E-step e M-step fino a quando:
```
|log_likelihood^(t+1) - log_likelihood^(t)| < epsilon
```
oppure raggiungi un numero massimo di iterazioni (es. 100-300).

**Proprieta' fondamentale di EM:** la log-likelihood e' garantita essere **monotonicamente non-decrescente** ad ogni iterazione (Teorema di Dempster, Laird e Rubin, 1977). Se la tua implementazione mostra log-likelihood che scende, c'e' un bug.

---

## 4. BIC (Bayesian Information Criterion)

Il BIC bilancia la bonta' di adattamento (log-likelihood) con la complessita' del modello (numero di parametri):

```
BIC = log P(X | theta) - (|theta| / 2) * log(n)
```

dove:
- `log P(X | theta)` e' la log-likelihood (calcolata sopra)
- `n` e' il numero di campioni nel training set
- `|theta|` e' il **numero totale di parametri** del modello

### Conteggio dei parametri |theta|

Con K componenti e dati d-dimensionali, e covarianza diagonale:

| Parametri | Quanti | Spiegazione |
|-----------|--------|-------------|
| pi (pesi) | K - 1 | K pesi ma con vincolo sum = 1, quindi K-1 liberi |
| mu (medie) | K * d | K vettori di dimensione d |
| sigma (varianze diag.) | K * d | K vettori di d varianze |

**Totale:**
```
|theta| = (K - 1) + K * d + K * d = (K - 1) + 2 * K * d
```

Si vuole **massimizzare** il BIC: il modello col BIC piu' alto e' quello migliore. Il BIC penalizza modelli troppo complessi (K alto), evitando l'overfitting.

---

## 5. Riepilogo operativo: cosa fare nel codice

### `__init__(self, n_categories, n_features)`
- Inizializza `_pi` shape (K,), `_mu` shape (K, d), `_sigma` shape (K, d)
- Scegli una strategia di inizializzazione (vedi sopra)

### `log_likelihood(self, samples) -> scalare`
1. Per ogni campione j e componente k, calcola `log(pi_k) + log N(x_j | mu_k, sigma_k)`
2. Per ogni campione j, applica logsumexp sulle K componenti
3. Somma su tutti i campioni N
4. Restituisci lo scalare

### `fit(self, samples)`
1. Inizializza i parametri (nel `__init__` o qui)
2. Ripeti:
   a. **E-step**: calcola gamma (N, K) -- le responsabilita'
   b. **M-step**: aggiorna pi, mu, sigma usando le formule sopra
   c. Calcola log-likelihood
   d. Controlla convergenza
3. Salva i parametri finali in `_pi`, `_mu`, `_sigma`

### `bic(self, samples) -> scalare`
1. Calcola log-likelihood
2. Conta |theta| = (K-1) + 2*K*d
3. Restituisci `log_likelihood - (|theta|/2) * log(n)`

---

## 6. Insidie comuni e consigli

- **Stabilita' numerica**: lavora SEMPRE in log-space. Non calcolare mai `exp(...)` senza prima aver sottratto il massimo (log-sum-exp trick).
- **Varianze che collassano**: se una Gaussiana "cattura" un solo punto, la varianza puo' andare a zero causando divisione per zero. Aggiungi un floor minimo alle varianze (es. 1e-6).
- **Log di zero**: `log(pi_k)` puo' essere problematico se pi_k -> 0. Anche qui, floor minimo.
- **Inizializzazione**: prova diverse inizializzazioni e/o usa k-means++. Una cattiva inizializzazione puo' portare EM in un pessimo minimo locale.
- **Ordine delle operazioni nel M-step**: aggiorna PRIMA mu, POI sigma (usando il mu appena aggiornato).
- **Il metodo `log_likelihood` deve restituire uno scalare** (la somma su tutti i campioni), come si vede dal codice di training che fa `print(f"logP(X|theta)={ll:.4f}")`.

---

## 7. Collegamento con le lezioni (GDL7 e GDL8)

- **GDL7 (Learning with fully observed variables)**: introduce il Maximum Likelihood Estimation nel caso in cui tutte le variabili sono osservate. Con dati completi, i parametri ML si ottengono in forma chiusa (es. media campionaria, varianza campionaria).

- **GDL8 (Learning with hidden variables)**: affronta il caso in cui esistono **variabili latenti** (come z nel GMM). La log-likelihood non si puo' massimizzare direttamente, quindi si usa l'algoritmo EM:
  - Si introduce la **complete likelihood** L_c(theta | X, Z)
  - L'E-step calcola l'**aspettativa** della complete log-likelihood rispetto alla distribuzione posteriore delle variabili latenti
  - L'M-step **massimizza** questa aspettativa rispetto ai parametri
  - Il teorema di Dempster-Laird-Rubin garantisce convergenza monotona della log-likelihood
