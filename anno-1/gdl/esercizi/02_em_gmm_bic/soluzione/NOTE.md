# Note sulla soluzione

## Perché tutto è in spazio log

La scelta strutturale della soluzione è che nessuna densità viene mai materializzata in spazio
lineare, tranne in `gaussian_pdf` che è solo un `exp` della log-densità e serve per i test di
normalizzazione. Il motivo è concreto: in `log_gaussian_pdf` il termine di Mahalanobis
$(x-\mu)^\top \Sigma^{-1} (x-\mu)$ cresce come il quadrato della distanza e diviso per la
varianza. Con un punto a distanza $10^5$ da una componente con varianza $10^{-4}$ vale $10^{14}$.
La densità corrispondente è `exp(-5e13)`, cioè `0.0` in doppia precisione — e non uno zero
innocuo: nell'E-step diventa `0/0` quando si normalizza, cioè `NaN` che poi si propaga a tutti
i parametri. Con `logsumexp` invece si sottrae il massimo prima di esponenziare, l'argomento
massimo di `exp` è `0`, e le responsabilità restano perfettamente definite anche quando in
spazio lineare non esisterebbero più. È il test `test_stabilita_numerica_punti_lontanissimi`.

Il dettaglio che quasi tutti sbagliano nel `logsumexp` è il caso in cui il massimo lungo l'asse
sia `-inf` (succede se qualche $\pi_k$ è finito esattamente a zero): `-inf - (-inf)` è `NaN`, e
il `NaN` sopravvive anche se poi si esponenzia. La soluzione sostituisce lo shift con `0.0`
quando il massimo non è finito, il che restituisce correttamente `-inf` senza passare da `NaN`.

## Cholesky invece di inv + det

`log_gaussian_pdf` fattorizza $\Sigma = LL^\top$ e ricava le due quantità che servono dalla
sola `L`: $\log|\Sigma| = 2\sum_i \log L_{ii}$ e $(x-\mu)^\top \Sigma^{-1}(x-\mu) = \|z\|^2$ con
$Lz = x-\mu$. Passare da `np.linalg.inv` e `np.linalg.det` funziona su matrici ben condizionate
ma degrada in fretta: il determinante di una $\Sigma$ mal condizionata underflowa a `0.0` in
dimensione anche solo 10-15, e `log(0)` manda tutto a `-inf`. Con Cholesky il log-determinante
è una somma di logaritmi e non underflowa mai. Nella soluzione la Cholesky ha anche un fallback
con jitter crescente: non è didattico, è solo una rete contro covarianze che il round-off rende
non-definite-positive per un pelo.

## L'ordine dentro il M-step

Nella formula della covarianza aggiornata compare $\mu_k$ **nuova**, non quella dell'iterazione
precedente:

$$\Sigma_k^{(t+1)} = \frac{1}{N_k}\sum_n \gamma_{nk}\,(x_n - \mu_k^{(t+1)})(x_n - \mu_k^{(t+1)})^\top$$

Usare $\mu_k^{(t)}$ è l'errore più comune, e il sintomo è esattamente quello che il test
principale cerca: la log-likelihood smette di essere monotona. Non esplode, non produce `NaN`,
semplicemente ogni tanto scende di un pelo — ed è per questo che è un bug che sopravvive a
lungo se non lo si cerca apposta. Stesso discorso per l'asse di normalizzazione delle
responsabilità: `resp.sum(axis=0)` invece di `axis=1` produce numeri plausibili, cluster
plausibili, e una history non monotona.

## Perché la monotonia è IL test

Il teorema di EM dice che $\log p(X \mid \theta^{(t+1)}) \ge \log p(X \mid \theta^{(t)})$ perché
ogni iterazione massimizza un lower bound che tocca la log-likelihood nel punto corrente. È una
garanzia, non una tendenza: un singolo decremento oltre il round-off è la prova che
l'implementazione non sta facendo EM. Per questo il test gira su 30 combinazioni di
(dataset, K, seed) e usa una tolleranza di $10^{-10}$ relativa alla magnitudine della
log-likelihood, cioè poco più del round-off di doppia precisione accumulato sulla somma di
qualche centinaio di termini.

Una precisazione onesta: con `reg > 0` il M-step non è più l'esatto massimizzatore della Q
function (il ridge si comporta come un prior debole sulle covarianze), quindi la monotonia
formalmente non è garantita al 100%. In pratica con `reg = 1e-6` su dati non degeneri i
decrementi sono esattamente zero, come verificato. Diventano visibili — dell'ordine di $10^{-5}$
— solo quando si chiede un K molto maggiore del numero vero di componenti e qualche componente
inizia a collassare: per questo le configurazioni del test si fermano a K = numero vero + 1.

## Lo schema init → E → (M → E)*

`fit_gmm` calcola una E-step subito dopo l'inizializzazione, poi alterna M ed E registrando la
log-likelihood dopo ogni E. Questo garantisce due cose che si perdono con l'ordine più naturale
"per ogni iterazione: E, poi M":

1. `loglik_history` è la sequenza dei valori di $\ell$ valutati su parametri successivi, quindi
   è la sequenza su cui il teorema di monotonia parla direttamente;
2. i parametri restituiti, `resp` e `loglik_history[-1]` si riferiscono **agli stessi**
   parametri. Con l'altro ordine, quando si esce dal ciclo dopo un M-step, `resp` è quello
   calcolato sui parametri *precedenti* — e `predict` sui dati di training restituirebbe
   assegnamenti leggermente incoerenti con `model["Sigmas"]`.

Da qui la convenzione `n_iter == len(loglik_history) - 1`, verificata dal test.

## Il caso K = 1 come oracolo

Con una sola componente la variabile latente sparisce: $\gamma_{n1} = 1$ per costruzione, il
lower bound coincide con la log-likelihood, e il M-step riproduce esattamente lo stimatore di
massima verosimiglianza di una singola gaussiana. Il test lo verifica contro
`np.cov(X, rowvar=False, bias=True)`, cioè con denominatore $N$: lo stimatore ML della
covarianza è biased, quello con $N-1$ è la correzione di Bessel e **non** è ciò che il M-step
produce. Confondere i due è un errore che passa inosservato su dataset grandi e si vede solo
sui piccoli. Il fit dell'oracolo gira con `reg=0.0` perché altrimenti il ridge sposterebbe la
covarianza di `1e-6` sulla diagonale e il confronto esatto fallirebbe.

## Il ridge e la degenerazione della likelihood

La likelihood di una mistura gaussiana a covarianze piene è **illimitata superiormente**: basta
centrare una componente su un singolo punto e far tendere la sua covarianza a zero perché la
densità in quel punto diverga. Non è un problema numerico, è una patologia del modello — la ML
non ha un massimo globale ben definito, si cercano massimi locali "buoni". Il termine
`reg * I` mette un pavimento agli autovalori e rende il problema numericamente trattabile. Il
test `test_caso_limite_k_uguale_n` è esattamente questa situazione portata all'estremo (una
componente per campione): senza ridge la log-likelihood divergerebbe; con `reg = 1e-3` resta
finita e tutte le $\Sigma_k$ restano definite positive (il test lo verifica chiamando
`np.linalg.cholesky`, che solleva se non lo sono).

Collegato: la protezione `np.maximum(Nk, 10 * eps)` nel M-step. Se una componente muore
(nessun punto le assegna responsabilità apprezzabile) $N_k \to 0$ e la divisione produce
`NaN`. Il floor la lascia dov'è invece di distruggere il fit.

## BIC: la convenzione di segno

`bic` implementa $-2\ell + p\log N$, da **minimizzare**. La convenzione opposta
($\ell - \tfrac{1}{2}p\log N$, da massimizzare) descrive la stessa quantità cambiata di segno e
riscalata di 2, ma se all'orale si dice "si prende il BIC più alto" senza dichiarare quale
convenzione si sta usando, si ha ragione metà delle volte. Il messaggio di errore del test su
`select_k` lo dice esplicitamente: se il modello selezionato è sempre il K massimo, quasi certo
che si stia massimizzando invece di minimizzare.

Il conteggio dei parametri (`n_params_gmm`) ha due punti in cui si sbaglia: i pesi di mixing
sono $K-1$ e non $K$, perché il vincolo $\sum_k \pi_k = 1$ toglie un grado di libertà; e le
covarianze piene hanno $D(D+1)/2$ parametri liberi ciascuna e non $D^2$, perché sono
simmetriche. Con $K=3, D=2$ la differenza fra il conteggio giusto (17) e quello sbagliato
($3 + 6 + 12 = 21$) vale $4\log N$ sul BIC, abbastanza da cambiare la selezione. Il test lo
verifica sia con numeri calcolati a mano sia per enumerazione esplicita delle entrate del
triangolo superiore.

Sul confronto BIC/AIC: la penalità del BIC supera quella dell'AIC per $N > e^2 \approx 7.4$,
quindi su qualsiasi dataset realistico il BIC preferisce modelli più semplici. La ragione
teorica è che il BIC approssima la marginal likelihood bayesiana (ed è consistente: con
$N \to \infty$ seleziona il modello vero se è nella famiglia), mentre l'AIC stima la
divergenza KL predittiva e tende a sovrastimare la complessità.

## k-means++ e il ruolo dell'inizializzazione

EM converge a un massimo locale, quindi l'inizializzazione decide quale. Inizializzare le medie
uniformemente a caso significa, con probabilità non trascurabile, farle cadere tutte dentro lo
stesso blob: EM ci mette moltissime iterazioni a separarle, o non ci riesce. k-means++ estrae
il primo centro uniformemente e ogni successivo con probabilità proporzionale a $D(x)^2$
(distanza al quadrato dal centro già scelto più vicino), che è un modo economico di spargere i
centri. Il caso limite da gestire è la somma delle $D(x)^2$ uguale a zero — succede quando ogni
punto coincide con un centro già scelto — perché `rng.choice` con un vettore `p` non
normalizzabile solleva. La soluzione ricade su una scelta uniforme.

Le covarianze iniziali sono tutte uguali alla covarianza empirica dell'intero dataset: è una
scelta deliberatamente sovradispersa, così ogni componente "vede" all'inizio tutti i punti e le
responsabilità partono morbide. Partire da covarianze piccole significa partire già quasi in
hard assignment, il che è un ottimo modo per bloccarsi in un massimo locale al primo giro.

## Collegamento alle slide

`GDL8 learning hidden.pdf` colloca EM nella tabella "structure × data": struttura fissa e dati
incompleti (variabili latenti) → EM per la ML, MCMC/VBEM per l'approccio bayesiano. La GMM è
il caso in cui i passi E ed M sono entrambi in forma chiusa, e per questo è il punto di
partenza di tutta la linea "latent variable EM" del corso: da qui si va a Baum-Welch per gli
HMM (`GDL9-10`), dove l'E-step diventa forward-backward invece di una normalizzazione per riga,
e poi al variational inference e all'ELBO (`GDL11`, `GDL24`), dove l'E-step esatto non è più
calcolabile e si sostituisce con una $q$ approssimata. La responsabilità $\gamma_{nk}$ di
questo esercizio *è* la $q(z)$ dell'ELBO, nel caso fortunato in cui coincide esattamente con la
posterior vera.
