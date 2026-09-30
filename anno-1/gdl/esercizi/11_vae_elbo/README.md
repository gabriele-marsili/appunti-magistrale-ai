# 11 — VAE: ELBO e reparameterization trick

## Lezione di riferimento

`Lessons/GDL24 VAE.pdf` — *Variational Autoencoders*. In particolare le slide
sull'approssimazione variazionale (ELBO), sul reparameterization trick e sulla
loss del VAE: slide 21 (`log P(x|θ) ≥ E_Q[log P(x,z)] − E_Q[log Q(z)]`), 22
(il trick), 25–26 (la loss e la sua differenziabilità), 27 (lettura
informazionale dei due termini).

## Il problema

Un VAE è un modello a variabili latenti continue:

    P_θ(x) = ∫ P_θ(x|z) P_θ(z) dz

L'integrale è intrattabile appena il decoder è una rete non banale. La lezione
lo aggira due volte, e le due mosse sono indipendenti:

1. **Il bound.** Si introduce una `Q(z|x, φ)` e si massimizza l'ELBO invece
   della log-verosimiglianza.
2. **La differenziabilità.** L'ELBO contiene un'attesa rispetto a `Q`, che
   dipende dai parametri `φ` che stiamo derivando. Campionare da `Q` è
   un'operazione non differenziabile; il reparameterization trick sposta la
   casualità in una variabile che *non* dipende da `φ`.

Questo esercizio implementa entrambe, e poi mette a confronto il trick con
l'alternativa che *non* richiede differenziabilità (lo stimatore score
function, alias REINFORCE), per misurare cosa si guadagna.

## Cosa devi implementare

| funzione | cosa fa |
| --- | --- |
| `gaussian_log_prob(x, mean, log_var)` | `log N(x; mean, diag(exp(log_var)))`, sommata sulle dimensioni |
| `kl_diag_gaussian_standard(mean, log_var)` | `KL(Q(z\|x) ‖ N(0, I))` in forma chiusa, una per esempio |
| `reparameterize(mean, log_var, rng)` | `z = mean + exp(0.5·log_var) · ε`, `ε ~ N(0, I)` |
| `elbo(x, mean, log_var, decoder_fn, rng, n_samples)` | stima Monte Carlo dell'ELBO per esempio |
| `reparam_grad_estimator(grad_f, mean, log_var, rng, n_samples)` | gradiente di `E_q[f(z)]` col trick (pathwise) |
| `score_function_grad_estimator(f, mean, log_var, rng, n_samples, baseline)` | gradiente di `E_q[f(z)]` con REINFORCE, con e senza baseline |

Il decoder arriva come `callable`: l'esercizio resta numpy puro, non c'è nessuna
rete da addestrare. Sono già forniti `toy_decoder`, `toy_log_evidence`
(quadratura), `toy_posterior` e le costanti `TOY_A / TOY_B / TOY_X_LOG_VAR`:
sono il modello giocattolo su cui i test misurano l'ELBO, e non vanno toccati.

## Specifica matematica

**Convenzione.** `log_var` è il logaritmo della **varianza**. La deviazione
standard è `exp(0.5·log_var)`. Nella slide la stessa quantità è scritta
`σ(x)` con il campionamento `z = μ(x) + σ^{1/2}(x)·ε`: l'esponente `1/2` è
esattamente il fattore `0.5` che compare qui.

**Log-densità gaussiana diagonale.**

    log N(x; m, diag(exp(lv))) = −0.5 · Σ_d [ log(2π) + lv_d + (x_d − m_d)² / exp(lv_d) ]

Il termine `log(2π)` compare una volta **per dimensione**.

**KL in forma chiusa** fra `N(m, diag(exp(lv)))` e il prior `N(0, I)`:

    KL = 0.5 · Σ_d ( exp(lv_d) + m_d² − 1 − lv_d )

Non serve campionare: è il termine "regularization" della slide 25.

**ELBO.** Con la decomposizione della slide 21,

    L(x, θ, φ) = E_Q[ log P(x|z) ] − KL( Q(z|x, φ) ‖ P(z) )

Solo il primo termine si stima per campionamento:

    L ≈ (1/S) Σ_s log P(x | z_s) − KL,        z_s = m + exp(0.5·lv) · ε_s

**L'identità che spiega il bound.** Per ogni `q`,

    log P(x) − L(q) = KL( q(z) ‖ P(z|x) )

Il difetto dell'ELBO rispetto alla log-evidenza è la KL fra `q` e la
**posterior vera**, non fra `q` e il prior. Da qui seguono due cose: l'ELBO è
sempre `≤ log P(x)`, e il bound è stretto se e solo se `q = P(z|x)`.

**Due stimatori dello stesso gradiente.** Sia `q = N(m, diag(exp(lv)))`.

*Pathwise* (reparameterization trick): scrivendo `z = m + std·ε` con
`std = exp(0.5·lv)` e `ε ~ N(0, I)`, l'attesa è rispetto a una distribuzione che
non dipende dai parametri, quindi il gradiente entra dentro l'attesa:

    ∂/∂m   E_q[f(z)] = E_ε[ f'(z) ]
    ∂/∂lv  E_q[f(z)] = E_ε[ f'(z) · 0.5 · std · ε ]

*Score function* (REINFORCE): dall'identità `∂q/∂φ = q · ∂ log q/∂φ`,

    ∂/∂φ E_q[f(z)] = E_q[ f(z) · ∂ log q(z)/∂φ ]

con, per la gaussiana diagonale,

    ∂ log q/∂m  = (z − m) / exp(lv)
    ∂ log q/∂lv = 0.5 · ( (z − m)² / exp(lv) − 1 )

Poiché `E_q[∂ log q/∂φ] = 0`, si può sottrarre a `f(z)` una costante
(*baseline*) senza introdurre distorsione: cambia solo la varianza.

Nota la differenza fra le due firme: il pathwise riceve `grad_f` e non `f`, lo
score function riceve `f` e non `grad_f`. Non è un dettaglio di comodo, è la
proprietà che li distingue.

## Perché questo esercizio

Scopre quattro confusioni.

1. **Che il reparameterization trick non serva a campionare, ma a derivare.**
   `rng.normal(mean, std)` e `mean + std * rng.standard_normal()` producono la
   stessa distribuzione; solo la seconda scrittura ha un `ε` che non dipende dai
   parametri, ed è per questo che si può propagare il gradiente. Il test `(e)`
   verifica proprio che, a parità di seed, `(z − mean)/exp(0.5·log_var)` non
   cambi al variare di `mean` e `log_var`.
2. **Da quale KL è fatto il gap dell'ELBO.** La KL che compare *dentro*
   l'ELBO è `KL(q ‖ prior)`; la KL che misura *quanto il bound è lasco* è
   `KL(q ‖ posterior)`. Sono due oggetti diversi e vengono scambiati di
   continuo.
3. **Che pathwise e score function stimino lo stesso gradiente.** Non sono due
   gradienti diversi né due approssimazioni di cose diverse: hanno la stessa
   media esatta. Cambia solo la varianza — di ordini di grandezza. È l'unica
   ragione per cui il VAE si addestra col trick.
4. **Che `log_var` sia il log della varianza.** Metà degli errori numerici di
   un VAE scritto a mano vive nel fattore `0.5`.

## Vincoli

Solo `numpy` e la standard library. Niente `torch`, `scipy`, `sklearn`,
`matplotlib`. Ogni sorgente di casualità passa dal `rng`
(`numpy.random.Generator`) che ricevi come argomento: mai `np.random.seed`, mai
il modulo `random`, mai `time`.

Il rumore va estratto in un'unica chiamata a `rng.standard_normal(...)` con la
shape indicata nelle docstring: alcuni test confrontano stimatori diversi a
parità di seed e si aspettano che vedano gli **stessi** campioni.

Non toccare `toy_decoder`, `toy_log_evidence`, `toy_posterior` e le costanti
`TOY_A / TOY_B / TOY_X_LOG_VAR`: sono già forniti e i test li usano come
oracolo.

## Come autovalutarti

```bash
cd /home/claude/gdl/esercizi/11_vae_elbo
python3 -m pytest test_vae_elbo.py -v
```

Tutti i test devono passare. Ogni asserzione ha un messaggio che indica quale
errore concettuale l'ha fatta fallire; leggilo prima di correggere a caso. Le
tolleranze dei test stocastici sono calibrate sull'errore standard della stima:
se sei fuori di molto è un errore di formula, non rumore.

## Tempo stimato

100 minuti. Le prime tre funzioni sono poche righe l'una e si scrivono in venti
minuti. L'ELBO richiede attenzione alle shape `(S, B, D)`. I due stimatori del
gradiente sono la parte lunga: derivare a mano `∂ log q/∂ log_var` e
`∂z/∂ log_var` è l'esercizio vero.

## Domande d'orale collegate

1. Perché l'ELBO è un limite inferiore di `log P(x)`, e quanto vale esattamente
   la differenza fra i due?
2. Che cosa rende non differenziabile l'ELBO scritto come `E_{z~Q}[·]`, e in che
   modo esatto il reparameterization trick risolve il problema?
3. I due termini dell'ELBO — ricostruzione e KL — perché uno si stima per
   campionamento e l'altro no?
4. Esiste un modo di stimare `∇_φ E_{q_φ}[f(z)]` senza reparameterizzare. Qual è,
   perché non lo si usa nel VAE, e in quali casi invece è l'unica opzione?
5. Che cosa succede all'ELBO se la `Q` collassa sul prior? E se collassa su una
   delta?
