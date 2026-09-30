# Note alla soluzione

## Come si ricava tutto

Il punto di partenza e' la sola identita' che serve davvero:

```
log p(x) = ELBO(q) + KL( q || p(mu, c | x) )
```

Da qui, siccome la KL e' non negativa, l'ELBO e' un bound inferiore per ogni `q`,
e massimizzarlo in `q` equivale a minimizzare la KL dalla posterior. Tutto il
resto e' contabilita'.

L'ELBO si scrive come `E_q[log p(x, c, mu)] - E_q[log q(mu, c)]` e, grazie alla
fattorizzazione mean-field, ogni pezzo si spezza in somme indipendenti. L'unico
punto in cui bisogna stare attenti e' che nel termine di verosimiglianza compare
`E_q[(x_i - mu_k)^2] = x_i^2 - 2 x_i m_k + (m_k^2 + s2_k)`: il secondo momento di
`q(mu_k)` non e' `m_k^2`, e' `m_k^2 + s2_k`. Questa e' la trappola principale
dell'esercizio, e ritorna identica nell'update di `phi`.

Gli update coordinati escono dalla regola generica
`log q*(z_j) = E_{q(z_-j)}[log p(x, z)] + const`:

- per `c_i`, tutti i termini che non dipendono da `k` (il `log(1/K)`, il
  `-0.5 log 2pi`, il `-0.5 x_i^2`) finiscono nella costante di normalizzazione,
  e resta `phi_ik propto exp(m_k x_i - 0.5 (m_k^2 + s2_k))`;
- per `mu_k`, il prior gaussiano e la verosimiglianza gaussiana si coniugano, e le
  precisioni si sommano: `1/s2_k = 1/sigma0^2 + sum_i phi_ik`, con media
  `m_k = (sum_i phi_ik x_i) * s2_k`. Le responsabilita' `phi_ik` giocano il ruolo
  di conteggi frazionari, esattamente come nell'M-step di EM.

## Trappole

**`E[mu^2]` contro `E[mu]^2`.** Se in `update_phi` si usa `m_k^2` invece di
`m_k^2 + s2_k`, l'ELBO calcolato resta comunque monotono lungo le iterazioni
(verificato: il salto minimo e' `-3e-14`, cioe' zero numerico). Il test di
monotonia da solo non lo scopre. Lo scopre solo il test di *ottimalita'*
condizionata: si perturba `phi` intorno al valore restituito da `update_phi` e si
controlla che l'ELBO non salga mai. Con il momento sbagliato il deficit e' circa
`0.42` nat, ben sopra la tolleranza. Morale, che vale anche all'orale: la
monotonia dell'ELBO e' necessaria ma non sufficiente per dire che gli update sono
giusti.

**Entropie dimenticate.** Se si omette `H[q(mu)]` o `H[q(c)]` si sta massimizzando
la log-verosimiglianza attesa, non l'ELBO: si ottiene una specie di EM hard che
collassa `s2` verso zero. Il confronto con `elbo_monte_carlo` lo becca subito,
perche' lo stimatore MC include per costruzione il `- log q`.

**Normalizzazione sull'asse sbagliato.** `phi` va normalizzato per riga
(`axis=1`, sulle componenti), non per colonna. Normalizzare per colonna produce
un oggetto che somma a 1 sui dati: e' una quantita' senza senso e infatti fa
saltare sei test su dodici.

**Overflow.** `update_phi` deve sottrarre il massimo per riga prima
dell'esponenziale. Senza, basta un `x_i` dell'ordine di qualche centinaio per
ottenere `inf/inf = nan`.

**Ordine della KL.** `kl_gaussians(m1, v1, m2, v2)` e' `E_{p1}[log p1 - log p2]`.
Scambiare gli argomenti da' un numero comunque positivo e comunque plausibile, per
cui l'errore passa inosservato finche' non lo si confronta con una stima Monte
Carlo (che campiona esplicitamente da `p1`).

**Label switching.** Le componenti sono scambiabili: `cavi` puo' restituire le
medie in qualunque ordine, e con seed diversi le restituisce in ordini diversi.
Nel test si ordina `m` e si ordinano le medie vere prima di confrontarle; per
l'accuratezza del clustering si rimappano le colonne di `phi` tramite il rango
delle medie stimate.

## Il test che conta

`test_elbo_e_lower_bound_della_log_evidenza` e' il cuore dell'esercizio. Con
`N=4, K=2` si enumerano tutte le 16 assegnazioni e per ciascuna si integra `mu`
in forma chiusa:

```
int N(mu; 0, s0^2) prod_{i in k} N(x_i; mu, 1) dmu
  = exp( -0.5 n_k log(2pi) - 0.5 log(s0^2) - 0.5 log(A) + B^2/(2A) - S/2 )
```

con `A = n_k + 1/s0^2`, `B = sum x_i`, `S = sum x_i^2` sul cluster `k` (per
`n_k = 0` l'espressione vale esattamente 1, come deve, perche' e' l'integrale del
solo prior). Poi `log p(x) = -N log K + logsumexp_c sum_k log I_k(c)`.

Questo e' un oracolo genuinamente indipendente: non usa il mean-field, non usa
nessuna delle funzioni dello studente, e ha un costo `K^N` che lo rende
impraticabile appena `N` cresce — che e' precisamente il motivo per cui esiste la
variational inference. La formula analitica e' stata verificata anche contro una
quadratura numerica bidimensionale su griglia `4001 x 4001` in `[-25, 25]^2`: i
due valori coincidono a `1.1e-13`, quindi l'enumerazione esatta e' stata tenuta e
non si e' fatto ricorso alla quadratura nel test (piu' lenta e piu' pesante in
memoria).

La verifica non si limita al punto fisso di CAVI: si estrae 300 volte un `q`
casuale e si controlla che l'ELBO resti sotto la log-evidenza. E' il punto che
distingue un bound da un'approssimazione. Al punto fisso il gap misurato vale
circa `1.11` nat: e' esattamente `KL(q || posterior)`, ed e' strettamente positivo
perche' il mean-field spezza la dipendenza fra `c` e `mu` che nella posterior vera
c'e' eccome.

## Perche' `K = 1` e' un caso limite interessante

Con una sola componente, `q(c_i)` e' degenere e `q(mu_1)` risulta essere
*esattamente* la posterior `p(mu | x)` (prior gaussiano coniugato con
verosimiglianza gaussiana). Non c'e' nessuna dipendenza da spezzare, la
fattorizzazione mean-field non costa nulla, quindi `KL(q || posterior) = 0` e
l'ELBO uguaglia la log-evidenza a meno dell'arrotondamento (`~3e-15` misurato).
E' l'unico caso in cui il bound e' stretto, e serve a rendere concreto che il gap
non e' un difetto dell'algoritmo ma il prezzo della fattorizzazione scelta.

## Collegamento alla lezione

`GDL11 variational` inquadra il problema come massimizzazione della verosimiglianza
in modelli a variabili latenti dove `log int prod_i P(x_i | z) P(z) dz` non ha
forma chiusa. La mixture di gaussiane e' il caso minimo in cui l'integrale e'
davvero intrattabile (somma su `K^N` configurazioni) ma il bound resta calcolabile
a mano, e per `N` piccolo si puo' confrontare con la verita'. La stessa struttura
— ELBO, aggiornamenti coordinati, entropia di `q` — ritorna identica nelle lezioni
su LDA (`GDL12`) e sui VAE (`GDL24`), dove l'unica differenza e' che l'update
coordinato in forma chiusa viene sostituito da una salita del gradiente
riparametrizzata.
