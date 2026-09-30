# 08 — RNN vanilla, BPTT e il problema exploding/vanishing gradient

## Lezione di riferimento

`Lessons/GDL17 propagation.txt` — *Information Propagation in Deep Networks*.
Dati sequenziali, refresher sulle RNN vanilla, l'exploding/vanishing gradient
problem (EVGP), dissezione delle cause del vanishing e prime direzioni per
risolverlo. È la lezione che motiva tutto quello che viene dopo: gating
(LSTM/GRU), inizializzazioni ortogonali, skip connection, e infine
l'attenzione, che il cammino ricorrente lo elimina del tutto.

## Il problema

Una RNN vanilla è definita da

    a_t = W_hh h_{t-1} + W_xh x_t + b_h
    h_t = tanh(a_t)
    y_t = W_hy h_t + b_y

con `h_0 = 0`. Il gradiente della loss rispetto ai parametri ricorrenti si
ottiene per backpropagation through time, cioè srotolando la rete nel tempo e
applicando la catena. Il cuore della catena è la jacobiana di un passo di
ricorrenza:

    dh_t / dh_{t-1} = diag(tanh'(a_t)) · W_hh

e quindi, per risalire da `t` a `t - k`,

    dh_t / dh_{t-k} = ∏_{j=0}^{k-1} diag(tanh'(a_{t-j})) · W_hh

Un prodotto di `k` matrici. Se il fattore tipico ha modulo `< 1` il prodotto
collassa esponenzialmente (*vanishing*): la rete smette di ricevere segnale di
apprendimento dalle dipendenze lontane, e non perché siano irrilevanti, ma
perché il gradiente non ci arriva. Se ha modulo `> 1` il prodotto diverge
(*exploding*): un singolo passo di gradiente scaraventa i pesi fuori dalla
regione utile.

Il criterio di prima approssimazione è il raggio spettrale `ρ(W_hh)`, ma è
**condizione necessaria e non sufficiente**: la jacobiana vera contiene anche
`diag(tanh'(a_t))`, che ha entrate in `(0, 1]` e può solo attenuare. Con `tanh`
il gradiente vanisce anche esattamente a `ρ(W_hh) = 1`. Questo esercizio ti fa
misurare la cosa invece che ripeterla.

## Cosa devi implementare

| funzione | cosa fa |
| --- | --- |
| `tanh_prime(a)` | derivata di tanh sul **pre-attivato** `a` |
| `rnn_forward(X, Wxh, Whh, bh, Why, by)` | forward, ritorna `(H, Y, cache)` con i pre-attivati in cache |
| `rnn_backward(dY, cache, Wxh, Whh, Why)` | BPTT completo; oltre ai gradienti dei parametri restituisce `dh_per_step` |
| `bptt_truncated(X, targets, params, k1, k2)` | BPTT(k1, k2): aggiorna ogni `k1` passi, propaga indietro `k2` |
| `gradient_norms_over_time(X, targets, params)` | `‖dL/dh_t‖` per ogni `t`, con loss solo sull'ultimo timestep |
| `jacobian_product_spectral_radius(Whh, H, cache)` | raggio spettrale del prodotto cumulativo delle jacobiane, all'indietro |
| `spectral_radius(M)` | massimo modulo degli autovalori (`np.linalg.eigvals`) |
| `clip_gradients(grads, max_norm)` | clipping globale sulla norma L2 di tutti i gradienti concatenati |

## Specifica

**Convenzioni di shape e di indice.** Sono metà del lavoro; sono ripetute nel
docstring di modulo di `rnn_evgp.py`.

    X (T, D)        X[i]   = input al timestep i,  i = 0..T-1
    H (T+1, Hdim)   H[i]   = stato DOPO i timestep;  H[0] = 0
    A (T, Hdim)     A[i]   = Whh @ H[i] + Wxh @ X[i] + bh,   H[i+1] = tanh(A[i])
    Y (T, O)        Y[i]   = Why @ H[i+1] + by

`X[i]`, `A[i]`, `Y[i]` parlano dello stesso timestep; `H[i]` è lo stato *prima*
e `H[i+1]` lo stato *dopo*. Lo sfasamento di uno è la prima fonte di bug.

**Backward.** Con `dY[i] = dL/dY[i]`, per `i` da `T-1` a `0`:

    dH[i+1] += Why^T dY[i]
    dA[i]    = dH[i+1] ⊙ tanh'(A[i])
    dWxh    += dA[i] ⊗ X[i]      dWhh += dA[i] ⊗ H[i]      dbh += dA[i]
    dH[i]    = Whh^T dA[i]

`dh_per_step[t] = dL/dH[t]` per `t = 0..T`, e `dh_per_step[0] == dh0`. Nota che
`h_t` influenza sia l'output `y_{t-1}` sia tutto il futuro: se dimentichi il
primo contributo, l'intera curva del vanishing è sfasata di uno.

**BPTT troncato.** Schema BPTT(k1, k2) di Williams & Peng, con `k2 ≥ k1`. La
sequenza si spezza in blocchi consecutivi di `k1` timestep (l'ultimo può essere
più corto); per il blocco che termina in `hi` si iniettano soltanto gli errori
dei suoi timestep e si propaga indietro fino a `max(0, hi - k2)`, poi si
tronca. I contributi si sommano. Il forward resta sull'intera sequenza: si
tronca il backward, non lo stato.

Poiché la loss è una somma sui timestep e il gradiente è lineare nella loss, con
`k2 ≥ T` la partizione in blocchi è esatta e il risultato coincide con il BPTT
completo, qualunque sia `k1`. Con `k2` piccolo l'errore è **bias**, non rumore:
i cammini lunghi vengono eliminati sistematicamente.

**Curva del vanishing.** `gradient_norms_over_time` inietta un errore solo in
`y_{T-1}` (loss `0.5 ‖y_{T-1} - target_{T-1}‖²`) e restituisce
`‖dL/dh_t‖` per `t = 0..T`. Con decadimento geometrico, il rapporto fra norme a
distanza fissa `d` è costante e vale circa `ρ^d`; il tasso per passo si stima
come `(‖dL/dh_0‖ / ‖dL/dh_T‖)^(1/T)`.

**Clipping globale.**

    total = sqrt( Σ_k ‖grads[k]‖_F² )
    se total > max_norm:  grads ← grads · (max_norm / total)

È un unico scalare comune a tutte le componenti: la direzione nello spazio dei
parametri non cambia, cambia solo la lunghezza del passo. `total_norm`
restituito è quello **prima** del clipping — è la diagnostica che dice quanto
stava esplodendo.

## Perché questo esercizio

Perché "il gradiente svanisce" è una frase che si può ripetere senza aver
capito niente, e qui invece è un numero che devi far uscire. Le confusioni che
l'esercizio scopre, in ordine di gravità:

1. **Che `ρ(W_hh) < 1` sia la causa del vanishing.** È una causa. Con `tanh` il
   gradiente svanisce anche a `ρ(W_hh) = 1` esatto, perché la jacobiana vera è
   `diag(tanh'(a_t)) W_hh` e `tanh' ≤ 1`. Il test
   `test_raggio_spettrale_unitario_ma_gradiente_vanisce_lo_stesso` usa una
   `W_hh` ortogonale, che conserva la norma *esattamente*, e mostra che il
   gradiente collassa lo stesso di più di quattro ordini di grandezza. Il
   raggio spettrale è condizione necessaria, non sufficiente.
2. **Che il troncamento del BPTT sia un'approssimazione "rumorosa".** Non lo è:
   è un bias sistematico che cancella esattamente le dipendenze a lungo
   termine, cioè proprio quelle che vorresti imparare.
3. **Che il gradient clipping curi il vanishing.** Cura l'exploding, e solo
   quello: è un tappo sulla lunghezza del passo, la direzione resta identica. Se
   il gradiente è già a `1e-9`, clippare non lo risveglia.

C'è poi la trappola della convenzione di `tanh'`: pre-attivato o post-attivato.
`tanh'(a) = 1 - tanh(a)²` e anche `= 1 - h²`, ma se passi `h` a una funzione che
si aspetta `a` ottieni `1 - tanh(h)²`, che è sbagliato ovunque tranne che in
zero — e in zero il gradient check non se ne accorge.

## Vincoli

Solo `numpy` e la standard library. Niente `torch`, `scipy`, `sklearn`,
`matplotlib`. Nessun autodiff: il BPTT si scrive a mano, è il punto.
Ogni sorgente di casualità passa da `np.random.default_rng(seed)` con seed
esplicito: mai `np.random.seed`, mai il modulo `random`, mai `time`.

Non toccare `numerical_gradient`, `make_copy_task`, `make_recurrent_matrix`,
`init_params`, `pack_params`, `unpack_params`, `mse_loss_and_grad`,
`format_decay_profile` e `PARAM_KEYS`: sono già forniti e i test li usano.

## Come autovalutarti

```bash
cd /home/claude/gdl/esercizi/08_rnn_evgp
python3 -m pytest test_rnn_evgp.py -v
```

Il test che conta più di tutti è `test_gradient_check_bptt_completo`: confronta
ogni gradiente con `numerical_gradient` (differenze finite centrali) a
`rtol=1e-5`. Se quello non passa, tutto il resto misura la cosa sbagliata —
sistemalo prima di guardare gli altri. Ogni asserzione ha un messaggio che
indica quale errore concettuale l'ha fatta fallire.

Una volta implementato tutto, `python3 rnn_evgp.py` stampa il profilo di
`‖dL/dh_t‖` in scala logaritmica nei tre regimi `ρ = 0.5`, `ρ = 1.0`, `ρ = 2.0`.
Guardalo: è l'esercizio in una figura.

## Tempo stimato

2 ore. Forward e `tanh_prime` sono dieci minuti; il backward richiede di essere
scrupolosi sugli indici e di far passare il gradient check (aspettati di
litigarci); `bptt_truncated` è breve se ti accorgi che una finestra della cache
si può dare in pasto a `rnn_backward` come se fosse una sequenza a sé. I test
sul vanishing non richiedono altro codice: girano su quello che hai già
scritto.

## Domande d'orale collegate

1. Scrivi la jacobiana `dh_t/dh_{t-1}` di una RNN vanilla e spiega da dove
   nasce l'exploding/vanishing gradient problem.
2. Se inizializzo `W_hh` ortogonale, quindi con raggio spettrale 1, il problema
   del vanishing è risolto? Perché no?
3. Che differenza c'è fra gradient clipping e le soluzioni al vanishing? Su
   quale dei due problemi agisce, e perché non sull'altro?
4. Che cosa perdo con il BPTT troncato, e in che senso l'errore che introduco è
   un bias e non del rumore?
5. Quali direzioni ha il corso indicato per attaccare l'EVGP, e per ciascuna
   quale fattore del prodotto di jacobiane sta modificando?
