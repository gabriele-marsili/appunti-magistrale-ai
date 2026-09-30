# Note alla soluzione — RBM e contrastive divergence

## Il collegamento con la lezione

Il deck `GDL14 MRF` fa un percorso preciso: parte dai Markov Random Field
generali, dove la distribuzione e' definita da potenziali su clique e la
costante di partizione e' globale; passa per i CRF lineari, dove la struttura a
catena rende l'inferenza esatta con sum-product; e arriva ai modelli non
orientati con inferenza *approssimata*, cioe' le Boltzmann machine. La RBM sta
esattamente nel punto in cui si rinuncia a calcolare `Z` e si accetta di
stimarne il gradiente per campionamento. Contrastive divergence e' il prezzo di
quella rinuncia.

La cosa da tenere presente attraversando l'esercizio: in un modello *orientato*
la likelihood si fattorizza sui nodi e ogni fattore e' gia' normalizzato, quindi
il massimo di verosimiglianza per dati completi si scrive in forma chiusa
(GDL7). In un modello *non orientato* i potenziali non sono normalizzati, la
normalizzazione e' una sola e globale, e la sua derivata rispetto ai parametri
e' un'aspettazione sotto il modello. E' da li' che nasce la fase negativa, e da
li' nasce tutta la difficolta'.

## Perche' l'energia libera e' calcolabile

Fissato `v`, l'energia della RBM e'

    E(v, h) = -vᵀb - Σ_j h_j (c_j + vᵀW[:, j])

cioe' e' **affine in h**, con i coefficienti delle `h_j` che non si mescolano
fra loro. Quindi

    Σ_h exp(-E(v,h)) = e^{vᵀb} Σ_h Π_j e^{h_j a_j}
                     = e^{vᵀb} Π_j Σ_{h_j ∈ {0,1}} e^{h_j a_j}
                     = e^{vᵀb} Π_j (1 + e^{a_j}),      a_j = c_j + vᵀW[:, j]

e la somma su `2^H` termini diventa un prodotto di `H` somme da due termini. Lo
scambio somma/prodotto e' lecito solo perche' nell'esponente non compaiono
termini `h_j h_k`: e' la bipartizione del grafo, non un trucco algebrico. La
stessa proprieta' e' quella che rende `p(h|v)` un prodotto di Bernoulli
indipendenti, e quindi che rende lecito il Gibbs *a blocchi*. In una Boltzmann
machine generale, con un termine `hᵀJh`, nulla di tutto questo funziona: si
torna al campionamento unita' per unita' e la marginalizzazione diventa un'altra
somma intrattabile.

Il test `test_p_h_given_v_fattorizza_solo_perche_il_grafo_e_bipartito` verifica
esattamente questo, e include la controprova: aggiunge un `hᵀJh` all'energia
enumerata e mostra che il prodotto delle marginali per unita' smette di
coincidere con la congiunta condizionale. Non e' un test di implementazione, e'
un test di comprensione.

Nota su cosa `F` *non* e': `p(v) = e^{-F(v)}/Z`, quindi `log p(v) = -F(v) - log
Z`. `F` e' trattabile, `log Z` no. La differenza di due energie libere e'
significativa (il rapporto di probabilita' fra due configurazioni), il valore
assoluto di una sola non lo e'. Da qui l'idea del *free energy gap* come
diagnostica: si guarda `F(dati) - F(rumore)`, dove `log Z` si cancella.

## Il gradiente e il suo segno

Derivando `log p(v) = -F(v) - log Z` rispetto a `W_ij` si ottengono due
contributi. Il primo, da `-F`, e' `v_i · p(h_j = 1 | v)`: e' un'aspettazione
sotto la posteriore delle nascoste dato *quel* dato, ed e' esatta. Il secondo,
da `-log Z`, e' `-⟨v_i h_j⟩_{p(v,h)}`: e' un'aspettazione sotto il modello,
senza condizionamento, e richiede di campionare dalla congiunta.

Il risultato e' `⟨v hᵀ⟩_dati - ⟨v hᵀ⟩_modello`: una *differenza di correlazioni*.
Il modello viene spinto ad abbassare l'energia dove ci sono i dati e ad alzarla
dove il modello mette massa da solo. Se le due aspettazioni coincidono, il
gradiente e' nullo: e' la condizione di *moment matching* tipica delle famiglie
esponenziali.

L'errore piu' facile e' il segno. La funzione restituisce un gradiente di
**ascesa**, quindi `W += lr * grad_W`. Chi ha in mente "loss e discesa" scrive
`W -= lr * grad_W` e ottiene un modello che peggiora monotonamente senza
sollevare nessuna eccezione: l'errore di ricostruzione sale lentamente e sembra
un problema di learning rate. Il test
`test_cd_k_e_una_direzione_di_ascesa` lo intercetta direttamente, verificando
che un passo di `+η·grad` aumenti la log-likelihood esatta.

## Perche' probabilita' e non campioni nelle statistiche

Nelle statistiche del gradiente si usa `p(h=1|v)` invece del bit campionato.
Questo e' Rao-Blackwell: `E[h_j | v] = p(h_j = 1|v)`, quindi la media non cambia
e la varianza scende. Il bit campionato serve *dentro* la catena di Gibbs, dove
propagare una probabilita' al posto di un bit sarebbe un errore concettuale (si
starebbe facendo mean-field, non campionamento, e la catena non avrebbe piu'
`p` come distribuzione invariante).

Un'implementazione che campiona anche nelle statistiche non e' *sbagliata*, ma
su Bars-and-Stripes converge molto peggio; se in piu' si sbaglia
l'accoppiamento (le `h` prese da un passo diverso rispetto a `v_model`) il
training si blocca del tutto. I due test su `train_rbm` falliscono in quel caso,
e i loro messaggi lo dicono.

## Il punto: CD e' biased

`test_cd_k_bias_k1_molto_peggio_di_k50` e' la ragione d'essere dell'esercizio.
Su un modello con `D=5`, `H=3` e pesi grandi (`W ~ 3·N(0,1)`, quindi catena che
mescola lentamente) si calcola il gradiente esatto per differenze finite
centrali su `exact_log_likelihood` — che a sua volta enumera tutti i `2^8`
stati. Poi si confrontano CD-1 e CD-50 sullo stesso batch, replicato 1000 volte:
4000 catene parallele, varianza Monte Carlo dell'ordine di `10⁻²` per
componente.

I numeri, con il seed dei test: `‖grad vero‖ ≈ 1.41`, errore di CD-1 `≈ 0.55`
(circa il 40%), errore di CD-50 `≈ 0.02`. La differenza non e' rumore, e' bias:
non sparisce mediando su piu' dati, sparisce solo allungando la catena. La
morale che va detta all'orale: CD-k massimizza qualcosa che *non e'* la
log-likelihood (Hinton lo introduce proprio come approssimazione di una
differenza di divergenze KL), e funziona in pratica perche' il bias e' piccolo
nella direzione che conta, non perche' sia trascurabile.

C'e' un dettaglio da non sbagliare nel test: il batch va **replicato**, non
ingrandito con dati diversi, altrimenti si confronterebbe il gradiente CD di un
dataset con il gradiente vero di un altro. E le differenze finite vanno centrali
con `eps ≈ 1e-5`: in avanti soltanto l'errore di troncamento `O(eps)` sarebbe
dello stesso ordine dell'errore di CD-50 e il test perderebbe senso.

## Trappole tecniche minori

`sigmoid` con `np.where` produce i valori giusti ma emette overflow: `np.where`
valuta entrambi i rami prima di scegliere. Servono maschere booleane con
indicizzazione, cosi' che `exp` non venga mai chiamata sul ramo sbagliato. Il
test usa `np.errstate(over="raise", invalid="raise")` per renderlo un errore
duro. L'underflow di `exp(-1000)` a zero, invece, e' innocuo e va lasciato
passare.

`softplus` si scrive `np.logaddexp(0.0, z)`, che e' gia' stabile; scriverlo come
`np.log(1 + np.exp(z))` esplode per `z` grande e restituisce `inf` per l'energia
libera dei pattern piu' probabili — cioe' proprio dove serve precisione.

`p_h_given_v` usa `W`, `p_v_given_h` usa `W.T`. Con `D ≠ H` uno sbaglio qui da'
un errore di shape e si scopre subito; con `D = H` passa silenziosamente. I test
usano apposta dimensioni diverse.

`sample_bernoulli` deve usare `rng.random(...) < p` e non `<=`: `rng.random()`
sta in `[0, 1)`, quindi il confronto stretto da' esattamente `0` per `p = 0` e
esattamente `1` per `p = 1`. Con `<=` il caso `p = 0` produrrebbe un `1` con
probabilita' non nulla.

In `gibbs_step` l'ordine dei consumi di `rng` (prima `h`, poi `v`) e' fissato
nella docstring. Non e' matematicamente rilevante — la catena e' corretta in
entrambi i casi — ma tenere l'ordine documentato rende gli esperimenti
riproducibili, ed e' un'abitudine che vale la pena avere.

`train_rbm` usa un unico `Generator` creato dal `seed`, consumato sempre nello
stesso ordine. Ne segue una proprieta' comoda usata dal test sulla
log-likelihood: una corsa da 1200 epoche contiene come prefisso esatto una corsa
da 400 epoche con lo stesso seed, quindi si possono ottenere checkpoint
confrontabili semplicemente rilanciando il training con `epochs` crescente,
senza sporcare l'API con callback.
