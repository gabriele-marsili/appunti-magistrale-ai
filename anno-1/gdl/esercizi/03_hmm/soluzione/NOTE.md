# Note alla soluzione

## L'orientamento di A, e perche' e' la meta' del lavoro

La convenzione `A[i, j] = P(z_t = j | z_{t-1} = i)` fissa che la riga sia lo
stato di partenza. Da qui discendono, senza margine di scelta, due espressioni
che sembrano intercambiabili e non lo sono. Nel forward si propaga in avanti
una *distribuzione*: `alpha[t-1]` e' un vettore riga di probabilita' e la
predittiva a un passo e' `sum_i alpha[t-1, i] A[i, j]`, cioe' `alpha[t-1] @ A`.
Nel backward si propaga all'indietro un *messaggio*, non una distribuzione:
`beta[t, i] = sum_j A[i, j] (B[j, obs[t+1]] beta[t+1, j])`, cioe' `A @ v`. In
un caso si somma sull'indice di riga, nell'altro su quello di colonna, e
l'unico modo di non sbagliare e' guardare su quale variabile si sta sommando
invece di andare a memoria.

Questo errore non solleva eccezioni: le shape combaciano sempre, `alpha`
continua a sommare a 1 riga per riga e la log-likelihood resta un numero
negativo dall'aria innocua. Per questo tutte le matrici della suite di test
sono asimmetriche e c'e' un oracolo `forward_naive` che enumera esplicitamente
le `K^T` traiettorie: e' l'unico controllo che non condivide alcun pezzo di
codice con l'implementazione da verificare. La mutazione `A @ alpha[t-1]` fa
cadere otto test su tredici; con matrici simmetriche non ne farebbe cadere
nessuno.

## Lo scaling: quale convenzione, e perche' gamma non va normalizzato

Ho usato lo scaling di Rabiner nella sua forma piu' stretta: `alpha[t]` e'
esattamente la distribuzione filtrata `P(z_t | obs[0..t])`, quindi somma a 1
per costruzione, e `scaling[t]` e' la predittiva a un passo
`P(obs[t] | obs[0..t-1])`. La regola della catena da' subito
`P(obs) = prod_t scaling[t]`, cioe' `log P(obs) = sum_t log scaling[t]`: la
likelihood non viene mai rappresentata, solo il suo logaritmo, ed e' per questo
che l'algoritmo regge sequenze lunghe migliaia di passi.

Il punto meno ovvio e' che `beta` deve usare **gli stessi** fattori, divisi con
lo sfasamento giusto: `beta[t] = (A @ v) / scaling[t+1]`, non `/ scaling[t]`.
Con questa scelta `beta[t, k]` vale
`P(obs[t+1..T-1] | z_t = k) / prod_{s>t} scaling[s]`, e nel prodotto
`alpha[t] * beta[t]` i due gruppi di fattori si ricompongono esattamente in
`prod_s scaling[s] = P(obs)`, che e' proprio il denominatore che servirebbe.
Risultato: `gamma = alpha * beta` e basta, senza normalizzare. Il corollario
diagnostico e' comodo: **se hai dovuto normalizzare gamma a mano perche' non
sommava a 1, il bug e' nello scaling di beta**, non in gamma. Lo stesso
sfasamento ricompare in `xi`, dove il divisore e' ancora `scaling[t+1]`;
usare `scaling[t]` produce una `xi` che sbaglia di un fattore costante per
ogni `t` e che quindi non marginalizza piu' a `gamma` (sei test cadono).

## Il controesempio Viterbi contro argmax(gamma)

E' il motivo per cui l'esercizio esiste. Le due quantita' rispondono a due
domande diverse: `gamma[t]` risponde "dove sono al tempo `t`, mediando su tutto
quello che potrei fare negli altri istanti", Viterbi risponde "qual e' la
storia complessivamente piu' probabile". Incollare gli argmax dei marginali
non produce in generale la storia piu' probabile, e nel caso peggiore non
produce nemmeno una storia possibile.

L'HMM costruito nella suite (`PI_CE`, `A_CE`, `B_CE`, `OBS_CE`) rende la cosa
estrema. Tre stati, prior uniforme. La transizione `1 -> 2` e' vietata:
`A[1, 2] = 0`. Gli stati 0 e 2 finiscono invece nello stato 2 con probabilita'
alta (0.90 e 0.60). Il simbolo 0 e' informativo, lo stato 1 lo emette piu'
spesso degli altri (0.36 contro 0.24 e 0.20); il simbolo 2 e' emesso con
probabilita' 0.2 da tutti e tre gli stati, quindi non sposta nulla. Osservando
`obs = [0, 2, 2]` si ottiene

```
gamma = [[0.3000, 0.4500, 0.2500],
         [0.2900, 0.2900, 0.4200],
         [0.2435, 0.2435, 0.5130]]
```

L'argmax riga per riga da' `[1, 2, 2]`, che ha probabilita' **esattamente
zero**: al primo passo userebbe la transizione vietata. Viterbi restituisce
`[1, 0, 2]`, con `log P(path, obs) = -6.1376`, e l'enumerazione delle 27
traiettorie conferma che quello e' davvero il massimo. Il meccanismo e'
trasparente: al tempo 1 lo stato 2 e' il piu' probabile marginalmente perche'
ci si arriva da 0 e da 2, che insieme raccolgono il 55% della massa iniziale;
ma nessuna di quelle due strade parte dallo stato 1, che e' il piu' probabile
al tempo 0. Il marginale somma su strade incompatibili fra loro, il MAP deve
sceglierne una.

La costruzione e' stata fatta a ritroso, e vale la pena raccontarla perche' e'
riutilizzabile. Si sceglie la tabella congiunta desiderata `f(i, j)` su due
istanti, imponendo che il massimo di cella cada in una posizione diversa dalla
coppia (argmax dei totali di riga, argmax dei totali di colonna). Poi si nota
che un HMM realizza `f(i, j) = pi_i B[i, obs_0] A[i, j] B[j, obs_1]`: se si fa
in modo che `B[:, obs_1]` sia costante rispetto allo stato (il simbolo non
informativo), allora `A[i, :]` e' semplicemente la riga `f(i, :)` normalizzata
e `pi_i B[i, obs_0]` e' proporzionale al totale di riga. Da qui si leggono i
parametri. L'osservazione in piu' al tempo 2 non serve alla logica, serve solo
a rendere il controesempio meno degenere di una sequenza di lunghezza 2.

Il test verifica tre cose distinte, e le verifica tutte: che i due path
differiscano, che il path marginale abbia log-probabilita' `-inf` (cioe' che
sia il controesempio che credo, non un caso fortunato di due path entrambi
leciti), e che Viterbi coincida con il MAP trovato per enumerazione. Un
controesempio non verificato e' un aneddoto.

## Viterbi in log, e gli zeri

La ricorsione va fatta in log fin dall'inizio: in spazio lineare
`delta[T-1]` va in underflow con la stessa velocita' di `alpha`, e non si puo'
rimediare normalizzando perche' normalizzare cambierebbe il valore restituito
di `logprob`, che per contratto e' la log-probabilita' **congiunta**
`log P(path, obs)` e non quella condizionata. Gli zeri di `A` diventano `-inf`,
e cosi' devono restare: sostituirli con un epsilon renderebbe percorribile una
transizione vietata e in questo esercizio distruggerebbe proprio il fenomeno
che si vuole osservare. Si silenzia il warning con
`np.errstate(divide="ignore")`, non si tocca il valore. L'aritmetica IEEE fa il
resto: `-inf + x = -inf`, e `np.argmax` su una riga di soli `-inf` restituisce
0 senza esplodere, che e' innocuo perche' quel ramo non vincera' mai a meno che
tutto sia impossibile.

Nel backtracking, `psi[t, j]` e' l'argmax sullo stato **precedente**, quindi si
massimizza lungo `axis=0` di `delta[t-1][:, None] + log_A`. Con `[None, :]` al
posto di `[:, None]` si ottiene ancora una matrice `(K, K)` e ancora un path
lecito: se ne accorge solo il test sull'HMM quasi deterministico, dove il path
vero e' noto, e il confronto con l'enumerazione.

## Baum-Welch: i due dettagli che rompono la monotonia

Il primo e' banale ma frequente: `gamma` e `xi` dell'E-step devono essere
calcolate **entrambe** con i parametri correnti, prima di toccare qualunque
cosa. Se si aggiorna `pi` e poi si ricalcola `xi`, si sta mescolando E-step e
M-step e la garanzia di EM salta.

Il secondo e' la somma nel denominatore di `A`. Il numeratore e'
`sum_{t=0}^{T-2} xi[t, i, j]`: ci sono `T-1` transizioni, non `T`. Il
denominatore deve essere il conteggio atteso di *uscite* dallo stato `i`, cioe'
`sum_{t=0}^{T-2} gamma[t, i]`, che non e' `sum_{t=0}^{T-1} gamma[t, i]` perche'
dall'ultimo istante non parte nessuna transizione. Con la somma completa le
righe di `A` non sommano piu' a 1 e la log-likelihood puo' scendere; e' una
delle mutazioni testate. Per `B`, invece, la somma corre su tutti i `T`
istanti, perche' ogni istante ha un'emissione.

Restano i denominatori nulli. Con `T = 1` non ci sono transizioni e
`sum_{t<=T-2} gamma[t, i]` e' una somma vuota: la scelta e' lasciare `A`
invariata, cosi' resta una matrice stocastica valida invece di riempirsi di
`NaN`. Piu' in generale si aggiorna solo dove il denominatore e' positivo. Non
serve invece nessuna protezione contro il collasso di una colonna di `B` su un
simbolo osservato: se il simbolo `o` compare al tempo `t`, `gamma[t]` somma a 1
e quindi almeno uno stato gli assegna massa positiva.

Per `loglik_history` ho scelto la convenzione piu' verificabile: l'elemento 0
e' la log-likelihood dei parametri iniziali, l'elemento `i` quella dopo
l'`i`-esimo aggiornamento, e `n_iter = len(history) - 1`. Cosi' la monotonia si
controlla con un solo `np.diff(...) >= 0` e non c'e' ambiguita' su quale
parametro corrisponda a quale valore. La tolleranza nel test e' `-1e-9` e non
`0` perche' la somma dei logaritmi dei fattori di scaling ha rumore di
arrotondamento dell'ordine di `1e-15` per passo.

## Collegamento alle slide

Il forward-backward e' l'istanza su catena del sum-product message passing
(GDL9-10, "Exact inference on a chain with observed and unobserved variables"):
`alpha` e' il messaggio che viaggia dalla radice temporale in avanti, `beta`
quello che torna indietro, e `gamma` la loro combinazione nel nodo. Viterbi e'
la stessa struttura di messaggi con il semianello (max, +) al posto di
(sum, ×): stesso grafo, stessa complessita' `O(T K^2)`, semantica diversa. E'
esattamente la coppia "sum-product message passing example" / "max-product
message passing example" delle slide, e la ragione per cui vengono presentate
di seguito e' proprio che si somigliano troppo. Baum-Welch e' EM applicato a
questa catena: l'E-step e' un forward-backward, l'M-step sono conteggi attesi
normalizzati, cioe' le stesse formule di massima verosimiglianza che si
userebbero se gli stati fossero osservati, con `gamma` e `xi` al posto dei
conteggi veri.
