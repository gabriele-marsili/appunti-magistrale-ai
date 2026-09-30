# Note sulla soluzione

## Il filo conduttore

La lezione GDL24 fa due mosse separate e le presenta di seguito, il che le fa
sembrare una sola. La prima è il bound: `log P(x) ≥ E_Q[log P(x,z)] − E_Q[log
Q(z)]`, che si ottiene con Jensen (o, equivalentemente, sottraendo una KL non
negativa) e vale per *qualunque* `Q`. La seconda è il reparameterization trick,
che non ha niente a che vedere con il bound: serve a rendere derivabile una
quantità che il bound ha già prodotto. Si può avere il primo senza il secondo
(si stima il gradiente con REINFORCE) e il secondo senza il primo (il trick si
usa ovunque compaia un'attesa rispetto a una distribuzione parametrizzata).
Tutto l'esercizio è costruito per tenere separate le due cose.

## log_var è il log della varianza

È la fonte numero uno di errori numerici in un VAE scritto a mano. La slide 25
scrive `z = μ(x) + σ^{1/2}(x) * ε`: quell'esponente `1/2` dice che `σ(x)` è la
**varianza**, non la deviazione standard. Nella soluzione la deviazione standard
è quindi `exp(0.5 * log_var)`, e nella log-densità il termine di
normalizzazione porta `log_var` (che è `2 log std`) e non `2 * log_var`.

Chi confonde i due termini ottiene una densità che integra a `1/std` invece che
a 1 — invisibile a occhio, ma il test `(a)` la prende per quadratura, sia in 1D
sia in 2D. La versione 2D serve a prendere l'altro errore classico, cioè
sommare `log(2π)` una volta sola per tutto il vettore invece che una volta per
dimensione: in 1D i due errori coincidono, in 2D no.

Nota implementativa minore: la soluzione scrive `(x - mean)**2 * np.exp(-log_var)`
e non `... / np.exp(log_var)`. In aritmetica esatta sono la stessa cosa, ma la
seconda passa da un `exp` che va in underflow a 0 quando `log_var` è molto
negativo — e con un encoder che sta collassando `log_var` diventa molto negativo
per davvero.

## La KL in forma chiusa

`KL = 0.5 Σ_d (exp(lv) + m² − 1 − lv)`. I due errori tipici sono dimenticare il
`−1` e sbagliare il segno di `lv`. Entrambi lasciano una funzione che *sembra*
una KL (non negativa, minima vicino al prior) ma che non lo è. Il test `(c)`
non ricopia la formula: campiona `z ~ q` e stima `E_q[log q(z) − log p(z)]`
dalla definizione, con densità scritte dentro il test. È l'oracolo indipendente
della suite.

Il test `(d)` chiede che `mean = 0, log_var = 0` dia esattamente `0.0`, con
`atol=0.0`. Non è pedanteria: `exp(0) + 0 − 1 − 0` fa `0.0` in virgola mobile
senza residui, quindi qualunque valore diverso da zero segnala un termine
mancante o di troppo, non un errore di arrotondamento.

Vale la pena tenere a mente la lettura della slide 27: questo termine è "il
numero di bit necessari a convertire un campione non informativo da `P(z)` in un
campione da `Q(z|x)`". Cioè quanto l'encoder si è dovuto allontanare dal prior
per codificare `x`.

## Il trick, e perché il test guarda `(z − mean)/std`

L'implementazione è una riga. Il punto è quale riga.

    z = mean + np.exp(0.5 * log_var) * rng.standard_normal(mean.shape)

contro

    z = rng.normal(mean, np.exp(0.5 * log_var))

Le due producono la stessa distribuzione, e su numpy producono perfino gli
stessi numeri (internamente `Generator.normal` fa `loc + scale * z`). Ma nel
grafo di calcolo di un framework autodiff la seconda è una foglia: `mean` e
`log_var` entrano nel campionatore e non ne escono più derivabili. La prima
invece è una funzione elementare di `mean`, `log_var` ed `ε`, ed `ε` è una
costante rispetto ai parametri. È la figura della slide 22: il rombo "Sample" si
sposta fuori dal percorso `μ, σ → z`.

Il test `(e)` verifica la proprietà giusta — che a parità di seed `ε` non
dipenda dai parametri — anche se, per la ragione appena detta, non riesce a
distinguere le due scritture su numpy. Serve comunque a prendere chi estrae il
rumore con una shape sbagliata, chi lo riestrae più volte, o chi fa dipendere il
numero di estrazioni dai parametri. La distinzione concettuale la deve fare lo
studente, ed è l'oggetto della domanda d'orale numero 2.

Il test `(f)` prende invece l'errore aritmetico: scala `exp(log_var)` invece di
`exp(0.5*log_var)`, cioè varianza empirica `exp(2*log_var)`.

## ELBO: shape e un solo blocco di rumore

`elbo` è la funzione dove si perde tempo, e il tempo si perde sulle shape. La
soluzione replica `mean` e `log_var` a `(S, B, D)` con `np.broadcast_to` e
chiama `reparameterize` **una volta sola**: così il rumore è `(S, B, D)`, si
consuma una sola estrazione dal `rng` e il codice resta vettoriale. Fare un
ciclo Python su `s` funziona ma consuma il `rng` in un ordine diverso, il che
non rompe nessun test qui ma rende irriproducibili i confronti fra esecuzioni.
`np.broadcast_to` restituisce una vista in sola lettura: va bene, perché
`reparameterize` usa `mean.shape` e non scrive dentro.

L'altro punto è che `n_samples` **media**, non somma, e la KL si sottrae una
volta sola fuori dalla media. Un ELBO con la KL dentro la media per `S` campioni
è ancora giusto per caso (la KL non dipende da `s`), ma uno con `rec.sum(axis=0)`
no: il test `(g)` confronta la media di 4000 stime a `S = 1` con una singola
stima a `S = 200000` e lo scarta.

## L'ELBO come bound, e di quale KL è fatto il gap

Il modello giocattolo è lineare-gaussiano di proposito: `P(x|z) = N(a z + b, s²)`
con prior `N(0,1)`. È l'unico caso in cui si ha tutto in forma chiusa —
marginale `N(b, a² + s²)` e posterior `N(a(x−b)/(s²+a²), s²/(s²+a²))` — e quindi
si può misurare l'ELBO contro un oracolo esatto. `toy_log_evidence` la calcola
comunque per **quadratura** sul latente, per non ricopiare la forma chiusa
dentro l'oracolo; il test `(h)` verifica che le due coincidano a `1e-10` e poi
usa la quadratura.

Il test `(i)` è quello che vale la pena aver capito:

    log P(x) − ELBO(q) = KL( q(z) ‖ P(z|x) )

Con `q` gaussiana e posterior gaussiana entrambi i membri si scrivono in forma
chiusa, quindi il test non verifica solo la disuguaglianza ma il valore esatto
del difetto. Ne segue tutto il resto: che l'ELBO sia `≤ log P(x)`, che il bound
sia stretto se e solo se `q` è la posterior, e che massimizzare l'ELBO rispetto
a `φ` significhi contemporaneamente stringere il bound e alzare la
verosimiglianza. La confusione da evitare è credere che il gap sia
`KL(q ‖ prior)`: quello è un *addendo* dell'ELBO, e nel caso `q = P(z|x)` è in
generale diverso da zero mentre il gap è zero.

Un dettaglio sulla tolleranza: nel caso `q = posterior` la stima Monte Carlo
può risultare *sopra* `log P(x)` di qualche millesimo. Non è un errore: l'ELBO è
`≤ log P(x)` in valore atteso, la sua stima con `S` finito no. Per questo il
test usa `atol` esplicite calibrate sull'errore standard, e per questo il caso
"bound stretto" è separato dai casi "bound lasco" (dove il margine è di ordine
1 e la disuguaglianza è robusta).

## I due stimatori: perché hanno firme diverse

    reparam_grad_estimator(grad_f, ...)          # riceve f', non f
    score_function_grad_estimator(f, ...)        # riceve f, non f'

L'asimmetria delle firme è il contenuto dell'esercizio. Il pathwise deriva
*attraverso* `f`, quindi ha bisogno di `f'`; in cambio il rumore che gli resta è
solo quello di `ε`. Lo score function non tocca mai `f` se non valutandola,
quindi funziona su `f` non differenziabile, discreta, o su un simulatore
opaco — e paga tutto il rumore della distribuzione.

Le derivate da ricavare a mano sono quattro. Per il pathwise, con
`std = exp(0.5·lv)`:

    ∂z/∂m  = 1
    ∂z/∂lv = 0.5 · exp(0.5·lv) · ε = 0.5 · std · ε

quel `0.5` è ciò che si dimentica. Per lo score function, da
`log q = −0.5 Σ [log 2π + lv + (z−m)²/exp(lv)]`:

    ∂ log q/∂m  = (z − m)/exp(lv) = ε/std
    ∂ log q/∂lv = 0.5 · ((z−m)²/exp(lv) − 1) = 0.5 · (ε² − 1)

il `−1` è ciò che si dimentica qui. Senza il `−1` lo stimatore è distorto di
`0.5 · E_q[f]`, che su una loss di ricostruzione è un numero enorme.

Nota che nella soluzione anche lo score function campiona `z` come
`m + std·ε`. Non è un'incoerenza: quella è solo la maniera di estrarre da `q`, e
lo stimatore non usa mai la derivabilità del percorso. Ma serve al test chiave,
perché con lo stesso seed i due stimatori vedono gli **stessi** `z` e il
confronto fra varianze diventa appaiato: la differenza misurata è tutta
attribuibile alla formula, non alla fortuna del campionamento.

## Il test chiave: stessa media, varianze incomparabili

Con `f(z) = Σ_d z_d²` sotto `q = N(m, diag(exp(lv)))` si ha
`E_q[f] = Σ_d (m_d² + exp(lv_d))`, quindi

    ∂/∂m_d  E_q[f] = 2 m_d
    ∂/∂lv_d E_q[f] = exp(lv_d)

esattamente. È l'oracolo analitico: nessuna delle due formule viene ricopiata
nel test. Il test `(l)` verifica che *entrambi* gli stimatori convergano lì.

Il test `(m)` misura poi la varianza su 8000 ripetizioni con `S = 32` campioni
ciascuna, con `m = (1, 2, −1.5)` e `lv = −3` (deviazione standard ≈ 0.22). Il
rapporto fra le varianze su `∂/∂m` esce intorno a **5800**, quello su `∂/∂lv`
fra 150 e 550. Non è un artefatto della scelta dei parametri: per `D = 1` la
varianza per campione dello score function su `∂/∂m` vale

    m⁴/σ² + 14 m² + 15 σ²

contro `4σ²` del pathwise. Il termine `m⁴/σ²` esplode quando `q` è stretta —
cioè esattamente nel regime in cui un encoder ben addestrato lavora. E in
dimensione `D` si aggiungono i termini incrociati `E[z_j⁴]/σ_d²` per ogni `j ≠ d`:
la varianza dello score function cresce con la dimensione del latente, quella
del pathwise no. Questo è il motivo per cui nel VAE si usa il trick, e la
risposta alla domanda d'orale numero 4.

La tolleranza larga sull'assenza di distorsione dello score function nel test
`(m)` (`atol = 0.30` contro `0.02` per il pathwise) non è lassismo: è
precisamente la quantità che il test sta misurando. Con `R·S = 256 000` campioni
l'errore standard è ≈ 0.07, quindi `0.30` sono quattro deviazioni standard.

## La baseline

`E_q[∂ log q/∂φ] = 0` per qualunque `q` normalizzata (è l'integrale di
`∂q/∂φ`, e `∫q = 1` non dipende da `φ`). Quindi sottrarre una costante `b` a
`f(z)` lascia la media inalterata e cambia solo la varianza. Con `b = E_q[f]` il
test `(n)` misura una riduzione di 25–35 volte su `∂/∂m`. Resta comunque due
ordini di grandezza peggiore del pathwise: la baseline è una pezza, non una
soluzione.

Attenzione a *dove* si sottrae: `b` va tolta a `f(z)`, non al gradiente. Chi
scrive `(f(z) · ∂log q) − b` introduce una distorsione pari a `b`, e il test lo
prende con l'asserzione sulla media.

Va detto che una baseline *costante* è esattamente non distorta, mentre la
tentazione naturale — usare la media campionaria di `f` sugli stessi `S`
campioni — introduce una piccola distorsione, perché la baseline diventa
correlata con lo score. Si risolve con una baseline leave-one-out; qui la firma
accetta solo `None` o un `float` proprio per non nascondere il problema dentro
l'implementazione.

## Quando serve ancora lo score function

Il test `(o)` usa `f(z) = 1[z > 0]`, il cui gradiente è nullo quasi ovunque: il
pathwise costruito su `f'` restituisce zero, mentre il gradiente vero non lo è,
perché `E_q[f] = Φ(m/σ)` e `∂/∂m = φ(m/σ)/σ ≈ 0.333`. Lo score function lo
recupera correttamente. È il caso che spiega perché REINFORCE non è un
sottoprodotto storico: latenti discreti, ricompense di reinforcement learning,
metriche non differenziabili. Il VAE gaussiano è il caso fortunato in cui il
trick è disponibile, non il caso generale.

## Collegamento alle slide

Slide 21 introduce l'ELBO e annota "It is not differentiable!" accanto al
termine di ricostruzione: quella nota è il problema che le slide 22 e 26
risolvono, e che questo esercizio misura. Slide 25 dà la loss con la KL in forma
chiusa "when both Q(z) and P(z) are Gaussians" — la formula di
`kl_diag_gaussian_standard`. Slide 26 enuncia il criterio in una riga: "No
expectation is w.r.t. distributions that depend on model parameters ⇒ we can
move gradients into them", che è letteralmente la giustificazione dello
stimatore pathwise.

Una nota terminologica che vale la pena tenere ferma, perché il deck usa la
stessa parola per due cose diverse. Nelle slide 8–9 sul DAE, "score function" è
`∇_x log p(x)`: il gradiente rispetto all'**input**, quello che tornerà nei
modelli di diffusione. Nello "score function estimator" di questo esercizio il
gradiente è `∇_φ log q(z|φ)`, rispetto ai **parametri**. Stesso nome, oggetti
diversi; all'orale conviene disambiguare prima di rispondere.
