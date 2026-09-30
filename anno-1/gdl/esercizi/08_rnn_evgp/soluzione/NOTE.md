# Note sulla soluzione

## Il filo conduttore

Tutto l'esercizio esiste per rendere misurabile una singola formula, quella che
GDL17 mette al centro:

    dh_t / dh_{t-k} = ∏_{j=0}^{k-1} diag(tanh'(a_{t-j})) · W_hh

Un prodotto di `k` matrici, e nient'altro. Il vanishing e l'exploding non sono
patologie misteriose delle reti profonde: sono ciò che succede a un prodotto di
`k` fattori quando `k` cresce. Se uno studente scrive il BPTT e poi guarda la
curva di `‖dL/dh_t‖`, quella formula smette di essere una slide.

La scelta che rende l'esercizio leggibile è `make_recurrent_matrix` con
`orthogonal=True`: `W_hh = ρ · Q` con `Q` ortogonale. Tutti gli autovalori
hanno modulo `ρ`, e per di più `‖W_hh v‖ = ρ ‖v‖` per *ogni* `v`, non solo
asintoticamente. Niente transiente dovuto alla non normalità della matrice: il
decadimento è geometrico dal primo passo, e i test possono confrontare il tasso
misurato col raggio spettrale a `rtol=0.02` senza barare. Con una gaussiana
riscalata (`orthogonal=False`) il raggio spettrale sarebbe lo stesso ma la
norma potrebbe crescere per parecchi passi prima di decadere — istruttivo, ma
inadatto a un'asserzione secca.

## Le convenzioni, che sono metà del lavoro

`H` ha `T+1` righe, `X`, `A`, `Y` ne hanno `T`. La regola è: `X[i]`, `A[i]`,
`Y[i]` parlano dello stesso timestep, `H[i]` è lo stato *prima* di quel
timestep e `H[i+1]` quello *dopo*. Da qui discendono le due asserzioni che nel
backward si sbagliano più spesso:

- `dWhh += outer(dA[i], H[i])` — con `H[i]`, lo stato **precedente**. Usare
  `H[i+1]` è l'errore classico e il gradient check lo prende subito.
- `dh_per_step[i+1] += Why^T dY[i]` — lo stato `h_{i+1}` influenza anche
  l'output del proprio timestep, non solo il futuro. Chi dimentica questo
  termine ottiene una curva del vanishing sfasata di uno, che decade lo stesso
  e quindi *sembra* giusta: solo il confronto numerico contro `dL/dh_t`
  (test 4) la smaschera.

La convenzione di `tanh_prime` è deliberatamente esplicitata perché
`tanh'(a) = 1 - tanh(a)² = 1 - h²`: le due espressioni sono la stessa cosa, ma
la funzione accetta il **pre-attivato**. Passarle `h` dà `1 - tanh(h)²`, che è
sbagliato ovunque tranne che in zero — e in zero il gradient check non se ne
accorge, perché lì i due valori coincidono. Il test include la controprova
esplicita (`assert max|got - sbagliata| > 0.1`) proprio per non lasciare
scampo.

## `rnn_backward` non assume `h_0 = 0`

È una scelta che sembra un dettaglio e invece è quella che rende
`bptt_truncated` tre righe invece di trenta. `rnn_backward` legge lo stato
iniziale da `cache["H"][0]` e non lo assume nullo. Di conseguenza una
**finestra** della cache

    {"X": X[lo:hi], "H": H[lo:hi+1], "A": A[lo:hi]}

è, per `rnn_backward`, una sequenza a sé stante che parte dallo stato
`H[lo]`. Il gradiente non scende sotto `lo`: questo *è* il troncamento, non una
sua approssimazione. Non serve un secondo backward con un parametro `depth`.

L'altra cosa da capire in `bptt_truncated` è perché con `k2 ≥ T` il risultato
coincide *esattamente* (a meno dell'ordine delle somme in virgola mobile: nei
test la differenza è `2e-15`) con il BPTT completo. La ragione è che la loss è
una somma sui timestep e il gradiente è un operatore lineare: spezzare la somma
in blocchi e sommare i gradienti dei blocchi dà lo stesso risultato, purché
ogni termine di loss sia contato una volta sola e nessun cammino venga tagliato.
I due modi di sbagliare questo test sono simmetrici: blocchi che non coprono
tutti i timestep (tipicamente l'ultimo blocco parziale quando `k1` non divide
`T` — per questo il test prova `k1 = 5` con `T = 12`), oppure blocchi che si
sovrappongono e contano due volte gli stessi errori.

Il forward, invece, non si tronca mai: lo stato viene portato avanti su tutta
la sequenza. Chi resetta anche lo stato non sta facendo BPTT troncato, sta
facendo addestramento su sottosequenze indipendenti, che è un'altra cosa e
peggiore.

## I tre regimi, e perché le scale degli input sono quelle

I test scelgono con cura la scala degli input, e la scelta è a sua volta il
contenuto didattico.

**ρ = 0.5, input di scala 0.05.** Lo stato resta vicino all'origine, dove
`tanh' ≈ 1` e la ricorrenza è di fatto lineare. Il rapporto fra norme
consecutive è costante entro `0.02` e il tasso stimato è `0.4988` contro un
raggio spettrale di `0.5`. Il vanishing è puro effetto di `W_hh`.

**ρ = 1.0, input di scala 0.8.** Qui `W_hh` è ortogonale: il test verifica
esplicitamente `‖W_hh^T v‖ = ‖v‖` a `rtol=1e-10`. La parte lineare **non
attenua nulla**, punto per punto. Eppure il gradiente perde più di quattro
ordini di grandezza in venti passi, e le norme sono monotone: con `W_hh` ortogonale
`‖dh_{t-1}‖ = ‖tanh'(a_t) ⊙ dh_t‖ < ‖dh_t‖` a ogni singolo passo, non solo in
media. L'unico colpevole possibile è `diag(tanh')`. Questo è il test che
distingue chi ha capito la lezione da chi ha imparato la regola "raggio
spettrale minore di uno": la condizione spettrale è **necessaria e non
sufficiente**, e con una saturante non è mai soddisfatta davvero. È anche la
ragione per cui le soluzioni al vanishing (gating in LSTM/GRU, skip connection,
ReLU al posto di tanh) attaccano il fattore `diag(tanh')` e non `W_hh`: le
inizializzazioni ortogonali da sole non bastano.

**ρ = 2.0, input di scala 1e-6.** Gli input microscopici tengono lo stato nel
regime lineare per tutti i quindici passi, dove il tasso di crescita è
esattamente `2` (misurato: `1.9991`). Se si usassero input di scala normale
`tanh` saturerebbe dopo cinque o sei passi e `diag(tanh')` frenerebbe
l'esplosione. Non è un trucco per far passare il test, è il fenomeno: la
saturazione della non linearità è precisamente ciò che *limita* l'exploding
nelle RNN reali, ed è il motivo per cui l'exploding si manifesta come picchi
sporadici (quando la traiettoria attraversa una regione non satura) invece che
come divergenza sistematica.

## Clipping

Il punto concettuale è che il riscalamento usa **un solo scalare**, comune a
tutti i parametri. Da qui la proprietà testata col coseno: la direzione
nell'intero spazio dei parametri è invariata, cambia solo la lunghezza del
passo. Il clipping per-componente (`np.clip` su ogni entrata) è un'altra cosa e
storce la direzione, il che è esattamente l'errore che il test col coseno
prende.

Due dettagli implementativi: `total_norm` è la norma **prima** del clipping (è
la diagnostica utile — dice quanto stava esplodendo — e non deve dipendere da
`max_norm`, cosa che il test verifica chiamando la funzione due volte con
soglie diverse); e il dizionario in ingresso non va modificato in place, perché
il chiamante tipicamente vuole tenersi il gradiente originale per il logging.
La divisione per zero sul gradiente nullo si evita con la struttura
`if total > max_norm: scale = ... else: scale = 1.0`, non con un `max(eps, ...)`
al denominatore.

Infine, la ragione per cui `clip_gradients` prende un dizionario generico e non
i cinque gradienti: perché ci si può infilare per sbaglio anche
`dh_per_step`, e allora la norma calcolata non è più quella
dell'aggiornamento. Il docstring lo dice; nei test si passa sempre e solo il
sottoinsieme dei parametri.

## Il caso T = 1

`dWhh` è **esattamente** zero, non "piccolo": con una sola ricorrenza l'unico
prodotto `W_hh h` è con `h_0 = 0`, quindi `W_hh` non entra nella funzione di
loss e il suo gradiente è identicamente nullo. È un controllo severo perché
un'implementazione che usasse `H[i+1]` al posto di `H[i]` nell'accumulo di
`dWhh` qui darebbe un valore diverso da zero, e fallirebbe rumorosamente su un
caso in cui il gradient check da solo potrebbe non essere abbastanza sensibile.

## Collegamento alla slide

GDL17 elenca, dopo la dissezione delle cause, le direzioni per attaccare
l'EVGP. Lette attraverso il prodotto di jacobiane diventano una tassonomia:
clipping agisce a valle sul modulo del gradiente e riguarda solo l'exploding;
le inizializzazioni ortogonali agiscono su `W_hh` e da sole non bastano (test
6); il gating di LSTM/GRU sostituisce `diag(tanh')` con qualcosa che può valere
1, cioè crea un cammino di gradiente non attenuato; le skip connection
aggiungono un termine identità al prodotto; l'attenzione, che arriva più avanti
nel corso, elimina proprio il cammino ricorrente sostituendolo con un accesso
diretto, e il prodotto di jacobiane lungo `k` passi sparisce. Sono tutte
risposte alla stessa formula.
