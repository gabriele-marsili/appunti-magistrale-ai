# 06 — RBM e contrastive divergence

## Lezione di riferimento

`Lessons/GDL14 MRF.txt` — *Undirected Graphical Models*. Markov Random Fields,
CRF lineari con inferenza esatta a sum-product, e infine i modelli non orientati
con inferenza **approssimata**: Boltzmann Machines, Restricted Boltzmann
Machines, apprendimento per Gibbs sampling (contrastive divergence). Questo
esercizio sta interamente nell'ultima parte del deck.

## Il problema

In un modello non orientato la distribuzione e' definita da un'energia:

    p(v, h) = exp(-E(v, h)) / Z,     Z = Σ_{v,h} exp(-E(v, h))

Per una RBM binaria con `v ∈ {0,1}^D`, `h ∈ {0,1}^H`:

    E(v, h) = -vᵀb - hᵀc - vᵀW h

`Z` e' una somma su `2^(D+H)` termini: intrattabile. Tutto il resto
dell'esercizio e' una conseguenza di questo fatto. Le due domande sono:

1. che cosa **e'** calcolabile esattamente, malgrado `Z`;
2. che cosa si fa quando non lo e'.

**Cosa e' calcolabile.** La marginalizzazione sulle nascoste, cioe' l'*energia
libera*

    F(v) = -log Σ_h exp(-E(v, h)) = -vᵀb - Σ_j softplus(c_j + vᵀW[:, j])

dove `softplus(z) = log(1 + e^z)`. La somma su `2^H` termini collassa in `H`
somme da due termini. Devi saper dire **perche'**: fissato `v`, l'energia e'
affine in `h`, quindi l'esponenziale si fattorizza su `j`, e questo accade solo
perche' **non ci sono archi h–h** (grafo bipartito). Con archi h–h ci sarebbe un
termine `hᵀJh` e non si fattorizzerebbe niente.

Sempre per bipartizione, le condizionali complete sono fattorizzate:

    p(h | v) = Π_j p(h_j | v),   p(h_j = 1 | v) = σ(c_j + vᵀW[:, j])
    p(v | h) = Π_i p(v_i | h),   p(v_i = 1 | h) = σ(b_i + hᵀW[i, :]ᵀ)

Questo permette il campionamento di **Gibbs a blocchi**: tutte le `h` insieme,
poi tutte le `v` insieme. In una Boltzmann machine non ristretta si dovrebbe
aggiornare un'unita' alla volta.

**Cosa non e' calcolabile.** Il gradiente della log-likelihood:

    ∂/∂W  mean_n log p(v_n) = ⟨v hᵀ⟩_dati − ⟨v hᵀ⟩_modello
    ∂/∂b  ...               = ⟨v⟩_dati    − ⟨v⟩_modello
    ∂/∂c  ...               = ⟨h⟩_dati    − ⟨h⟩_modello

La *fase positiva* e' esatta e costa niente (basta `p(h|v)`). La *fase negativa*
e' un'aspettazione sotto il modello, e richiederebbe una catena di Gibbs fatta
girare fino a convergenza. **CD-k** la tronca a `k` passi e la fa partire dai
dati invece che da uno stato casuale. Non e' uno stimatore non distorto: e'
un'approssimazione **biased**, e per `k` finito l'algoritmo non massimizza la
log-likelihood.

## Cosa devi implementare

| funzione | cosa fa |
| --- | --- |
| `sigmoid(x)` | sigmoide logistica, stabile per `|x|` grande |
| `energy(v, h, W, b, c)` | `E(v,h) = -v@b - h@c - v@W@h`, vettorizzata con broadcasting |
| `free_energy(v, W, b, c)` | `F(v)`, con la marginalizzazione analitica sulle `h` |
| `p_h_given_v(v, W, c)` | `P(h_j = 1 | v)`, probabilita' non campioni, shape `(N,H)` |
| `p_v_given_h(h, W, b)` | `P(v_i = 1 | h)`, shape `(N,D)` |
| `sample_bernoulli(p, rng)` | campioni binari elemento per elemento |
| `gibbs_step(v, W, b, c, rng)` | un passo di Gibbs a blocchi, ritorna `(v_new, h_sample, h_prob)` |
| `cd_k(v_data, W, b, c, k, rng)` | gradienti CD-k **di ascesa**, piu' lo stato finale della catena |
| `train_rbm(X, H, epochs, lr, k, batch_size, seed)` | SGD a minibatch, con history delle diagnostiche |

Sono **gia' forniti** e non vanno toccati: `make_bars_and_stripes`,
`log_partition_exact`, `exact_log_likelihood`, `_all_binary`, `_logsumexp`.
Gli ultimi due gruppi sono gli **oracoli**: enumerano tutti i `2^(D+H)` stati e
calcolano `Z` e la log-likelihood esatta. Su un modello reale non li avresti;
qui servono a misurare quanto CD si allontana dalla verita'.

## Specifica operativa

**Segno.** `cd_k` restituisce gradienti **da salire**: l'aggiornamento e'
`W += lr * grad_W`. Il gradiente e' `fase positiva − fase negativa`.

**Statistiche.** Nelle statistiche del gradiente si usano le **probabilita'**
`p(h=1|v)`, non i bit campionati, sia nella fase positiva sia su `v_model`. E'
un'aspettazione condizionale esatta: stessa media, varianza minore
(Rao-Blackwellizzazione). Il valore campionato serve invece *dentro* la catena
di Gibbs, dove propagare una probabilita' al posto di un bit sarebbe sbagliato.

**Catena.** La fase negativa parte da `v_data`, non da rumore.

**Diagnostiche di `train_rbm`**, una per epoca:
- errore di ricostruzione = MSE fra `X` e `p(v | p(h | X))`, deterministico;
- free energy gap = `mean F(X) − mean F(X_rumore)`, con `X_rumore` un array
  binario casuale generato una volta sola all'inizializzazione.

L'inizializzazione e l'ordine di consumo di `rng` sono fissati nella docstring
di `train_rbm`: rispettali, altrimenti i risultati non sono riproducibili.

**Dataset.** `make_bars_and_stripes(seed)` genera Bars-and-Stripes 3x3: 14
pattern binari da 9 bit. E' il benchmark standard delle RBM perche' con `D = 9`
si puo' enumerare `Z` e quindi misurare la log-likelihood **vera**.

## Perché questo esercizio

Scopre tre confusioni.

1. **Che l'energia libera e la log-likelihood siano la stessa cosa.** Non lo
   sono: `F(v)` e' trattabile, `log p(v) = -F(v) - log Z` no. Chi non ha capito
   la differenza pensa che minimizzare `F` sui dati basti; invece serve anche
   *alzare* `F` altrove, ed e' esattamente cio' che fa la fase negativa.
2. **Che contrastive divergence sia "il" gradiente.** Non lo e'. Il test
   `test_cd_k_bias_k1_molto_peggio_di_k50` confronta CD-1 e CD-50 con il
   gradiente esatto calcolato per differenze finite sulla log-likelihood
   enumerata, su un batch replicato 1000 volte in modo che la varianza Monte
   Carlo sia trascurabile. Quello che resta e' **bias**: CD-1 sbaglia di circa
   il 40% della norma del gradiente, CD-50 di un ordine di grandezza meno.
   Aumentare il numero di dati non toglie il bias; aumentare `k` si'.
3. **Che l'errore di ricostruzione misuri la qualita' del modello.** Non la
   misura. E' un proxy comodo perche' e' calcolabile sempre; sui dati veri puo'
   scendere mentre la log-likelihood peggiora. Qui, grazie all'enumerazione, si
   possono guardare entrambi.

E poi c'e' la "R" di RBM: la fattorizzazione delle condizionali non e' un
comodo dettaglio implementativo, e' *tutto*. Un test la verifica e ne mostra la
controprova: se si aggiunge un accoppiamento h–h all'energia, `p(h|v)` smette di
essere il prodotto delle marginali e il campionamento a blocchi non e' piu'
lecito.

## Vincoli

Solo `numpy` e la standard library. Niente `torch`, `scipy`, `sklearn`,
`matplotlib`. Ogni sorgente di casualita' passa dal `rng`
(`numpy.random.Generator`) che ricevi come argomento: mai `np.random.seed`, mai
il modulo `random`, mai `time`.

`sigmoid` non deve produrre overflow, `inf` o `NaN` per input di modulo 1000. Il
test lo verifica con `np.errstate(over="raise", invalid="raise")`; nota che
`np.where` valuta entrambi i rami prima di scegliere.

Non toccare `make_bars_and_stripes`, `log_partition_exact`,
`exact_log_likelihood`, `_all_binary`, `_logsumexp`.

## Come autovalutarti

```bash
cd /home/claude/gdl/esercizi/06_rbm_cd
python3 -m pytest test_rbm_cd.py -v
```

Tutti i test devono passare. Ogni asserzione ha un messaggio che indica quale
errore concettuale l'ha fatta fallire; leggilo prima di correggere a caso.
L'intera suite gira in circa un secondo.

## Tempo stimato

100 minuti. Le prime sei funzioni sono una o due righe l'una una volta che hai
scritto la formula giusta su carta — la parte lenta e' derivare l'energia libera
e convincersi del segno del gradiente. `cd_k` e `train_rbm` sono meccaniche, ma
un segno sbagliato li fa divergere senza errori evidenti.

## Domande d'orale collegate

1. Perche' in una RBM la marginalizzazione sulle unita' nascoste e' analitica,
   mentre la costante di partizione resta intrattabile?
2. Che cosa cambia fra una Boltzmann machine generale e una *restricted*? Che
   cosa si guadagna, in termini di inferenza, imponendo la bipartizione?
3. Scrivi il gradiente della log-likelihood di una RBM. Perche' compare una
   differenza fra due aspettazioni, e da dove viene la seconda?
4. Che approssimazione fa contrastive divergence, ed e' uno stimatore non
   distorto del gradiente? Che cosa succede al crescere di `k`?
5. Perche' l'errore di ricostruzione non e' una misura affidabile della qualita'
   di una RBM, e che cosa useresti al suo posto?
