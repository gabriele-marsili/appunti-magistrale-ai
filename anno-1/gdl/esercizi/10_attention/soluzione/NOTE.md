# Note sulla soluzione

## Il filo conduttore

Tutto l'esercizio serve a rendere verificabile una frase che nelle slide di
GDL20 compare come domanda retorica: *"what are we losing when we gain global
dependencies and full parallelism?"*. La risposta è l'ordine. La self-attention
è una funzione **equivariante alle permutazioni** delle posizioni, e lo è in
modo esatto per qualsiasi valore dei pesi: non è un'approssimazione, non
dipende dall'inizializzazione, è una proprietà strutturale. Da qui discende
tutto il resto — il positional encoding esiste per rompere quella simmetria, e
la maschera causale esiste per rompere l'altra simmetria (passato/futuro) che
l'attenzione da sola non conosce.

Il salto GDL19 → GDL20 è nella stessa direzione. In GDL19 l'attenzione è un
ponte fra due sequenze diverse: le query vengono dal decoder, chiavi e valori
dall'encoder. In GDL20 si osserva che nulla obbliga le due sorgenti a essere
diverse, e che facendole coincidere si ottiene un meccanismo che sostituisce la
ricorrenza invece di affiancarla. Per questo `multi_head_attention` è una sola
funzione con due argomenti `X_q` e `X_kv`, e nel corpo non c'è alcun `if`:
qualunque implementazione che distingua i due casi con un ramo di codice ha
mancato il punto della lezione.

## Scaled dot-product: due dettagli che decidono tutto

Il primo è `np.swapaxes(K, -1, -2)` e non `K.T`. Con `K` di shape
`(N, H, L, d)` la trasposta di numpy inverte **tutti** gli assi e produce
`(d, L, H, N)`: il calcolo o esplode o, peggio, funziona per caso su un input
2D e si rompe appena arriva il batch. Chi prototipa su matrici e poi aggiunge le
teste inciampa qui sistematicamente.

Il secondo è che il mascheramento va fatto **prima** del softmax. La tentazione
è di calcolare il softmax e poi azzerare le entrate mascherate. Il risultato ha
la shape giusta e i pesi giusti a meno di una costante, ma le righe non sommano
più a 1 e l'output non è più una combinazione convessa dei valori: diventa una
combinazione con massa mancante, che si accorcia proprio dove la maschera è più
aggressiva. Il test `(a)` lo prende, e lo prende anche il test `(b)`, perché la
mancata rinormalizzazione fa comparire nell'output di ogni posizione una
dipendenza dalla *quantità* di futuro mascherato.

Lo `-inf` è deliberato e ha una conseguenza che va conosciuta: se una riga è
interamente mascherata, `softmax` produce NaN. È il comportamento corretto —
una distribuzione su un insieme vuoto non esiste — e non capita mai con
`causal_mask`, che lascia sempre visibile la diagonale. Può capitare con
`padding_mask` su una sequenza di lunghezza 0. La docstring lo dice.

## Le maschere e il verso

`causal_mask(L)` è `np.triu(ones, k=1)`: `True` sopra la diagonale, cioè `j > i`.
Le tre varianti sbagliate sono `k=0` (che maschera anche la diagonale e rende
la prima riga completamente vuota), `np.tril(..., k=-1)` (che maschera il
passato invece del futuro) e la negazione booleana. Nessuna delle tre si vede
guardando le shape o controllando che i pesi sommino a 1: tutte e tre passano
quei controlli.

Il test `(b)` è costruito per questo. Non guarda la maschera, guarda il
comportamento: perturba di `+5` tutti gli input strettamente dopo `t` e
verifica che l'output alle posizioni `0..t` non si muova (`atol=1e-12`,
perché la differenza dovrebbe essere esattamente zero in aritmetica floating
point — gli stessi numeri entrano negli stessi prodotti). Il test include
anche la controprova: l'output alle posizioni `> t` **deve** cambiare, altrimenti
il test sarebbe superato anche da una funzione costante. Senza quella seconda
asserzione un test di invarianza è quasi sempre vacuo.

`padding_mask` restituisce `(N, L)` e non una maschera già broadcastabile a
quattro assi. È una scelta: la stessa maschera serve in contesti con numero di
assi diverso, e chi la usa deve sapere dove va inserita. La docstring dà la
formula, `mask[:, None, None, :]`.

## split_heads e merge_heads

`reshape(N, L, n_heads, d_head).transpose(0, 2, 1, 3)`, in quest'ordine.
L'errore tipico è `reshape(N, n_heads, L, d_head)` diretto, che ha la shape
giusta ma contenuto sbagliato: mescola posizioni e teste, perché il reshape
legge la memoria in ordine C e i dati sono disposti con `L` che varia più
lentamente di `d_model`. La shape corretta non garantisce il contenuto
corretto, e questo è esattamente il tipo di bug che sopravvive a un training
completo producendo solo un modello un po' peggiore.

Il test `(d)` verifica il round-trip nei due versi, ma anche una cosa in più:
che la testa `h` corrisponda alle colonne `[h·d_head, (h+1)·d_head)`. Il
round-trip da solo non basterebbe — anche un'implementazione con interleaving
è invertibile.

## Lo scaling, quantificato

Il test `(f)` non si limita a dire "senza scaling è peggio": lo misura.
Con `d_k = 64`, `L_k = 64` e componenti standard normali, l'entropia media dei
pesi vale circa `3.80` nat con lo scaling (contro un massimo di
`log 64 = 4.16`) e circa `0.67` senza. Il peso massimo passa da `0.15` a
`0.999`. L'asserzione è `H_non_scalata < 0.25 · H_scalata`, con un margine
ampio rispetto al valore osservato (`0.67` contro una soglia di `0.95`), quindi
non è flaky.

C'è anche una controprova algebrica che non dipende dalle costanti scelte:
moltiplicando `Q` per `sqrt(d_k)` prima di chiamare la funzione si deve
riottenere **esattamente** il softmax non scalato. Se il denominatore fosse
`d_k` o `sqrt(d_model)` questa identità non varrebbe.

## Il positional encoding e la rotazione

La proprietà `PE[pos+k] = M_k PE[pos]` viene dalle formule di somma:

    sin(ω(p+k)) = sin(ωp) cos(ωk) + cos(ωp) sin(ωk)
    cos(ω(p+k)) = cos(ωp) cos(ωk) − sin(ωp) sin(ωk)

quindi ogni coppia di colonne `(2i, 2i+1)` subisce la rotazione di angolo
`ω_i k`, e `M_k` è block-diagonale con blocchi `[[cos, sin], [−sin, cos]]`.
Il punto è che `M_k` **non dipende da `pos`**: un modello lineare può imparare a
riconoscere "distanza `k`" con un unico insieme di pesi, valido a ogni
posizione. È il motivo per cui questo encoding, che sembra arbitrario, non lo è.

Nel test la matrice è costruita a mano dalle identità trigonometriche, non
riusando `positional_encoding`: è un oracolo indipendente. C'è poi un secondo
oracolo che non assume nemmeno la struttura a blocchi: si cerca ai minimi
quadrati una qualunque matrice che porti `PE[:-k]` in `PE[k:]` e si verifica
che il residuo sia dell'ordine di `1e-14`. Attenzione a un dettaglio: quella
soluzione ai minimi quadrati **non** coincide con `M_k` e **non** è ortogonale,
perché per `d_model = 16` e `L = 64` le colonne a bassissima frequenza sono
quasi collineari (`sin(ωp) ≈ ωp`, `cos(ωp) ≈ 1`) e il sistema è
mal condizionato: la mappa lineare esiste ma non è unica. Verificare
l'ortogonalità della matrice ricavata da `lstsq` sarebbe un test sbagliato, e
infatti nel test si verifica l'ortogonalità solo di `M_k` analitica. Il test
include anche la controprova su un encoding casuale, per cui il residuo ai
minimi quadrati sale a circa `3.5`.

## Equivarianza alle permutazioni

Perché vale: i pesi `alpha_ij` dipendono solo dalla coppia `(x_i, x_j)`, e
l'output alla posizione `i` è `Σ_j alpha_ij (x_j Wv)`. Permutando le righe di
`X` con `P`, la matrice dei punteggi diventa `P S Pᵀ`, il softmax per righe
commuta con questa trasformazione, e l'output diventa `P` volte l'output
originale. Nel test lo scarto misurato è `1.1e-16`, cioè zero macchina: non è
una proprietà approssimata.

Per la rottura serve attenzione a come si imposta il confronto. Non basta
mostrare che `attention(X + PE) ≠ attention(X)`: quello è ovvio e non dice
niente. Bisogna confrontare `attention(perm(X) + PE)` con
`perm(attention(X + PE))`, cioè permutare i **token** lasciando il PE inchiodato
alle posizioni. Se l'equivarianza reggesse ancora, il PE non starebbe
codificando nulla di posizionale. Lo scarto relativo osservato è circa `0.63`
contro una soglia di `0.05`, quindi ampiamente sopra soglia; il test controlla
anche che la permutazione estratta non sia l'identità, perché con `L = 6` non è
impossibile.

## LayerNorm contro BatchNorm

Le asserzioni su media e varianza usano `atol=1e-4` e non `1e-9`, e la ragione è
`eps`: la varianza dell'output non è esattamente 1 ma `σ²/(σ² + eps)`, che per
`σ² ≈ 1` e `eps = 1e-5` sbaglia di circa `1e-5`. Stringere la tolleranza
significherebbe pretendere `eps = 0`, che è numericamente sbagliato. Per lo
stesso motivo l'invarianza a shift e scala vale a meno di `eps`: riscalando
l'input di `a` la varianza diventa `a²σ²` e il termine `eps` pesa diversamente.

Il confronto con BatchNorm è nel test `(h)` ed è la parte che vale la pena
guardare. Si applica `layer_norm` a un batch, poi la si applica a ogni riga da
sola, e si verifica che i due risultati coincidano esattamente. Poi si cambiano
tutti gli elementi del batch tranne il primo e si verifica che l'output del
primo non si muova. Una BatchNorm di riferimento, scritta nel test come
contrasto, si sposta invece di oltre `1.0`. È questa proprietà — statistiche
locali all'esempio — che rende LayerNorm adatta a sequenze paddate di lunghezza
variabile, dove le statistiche di batch sarebbero calcolate anche sul padding.

## Il blocco encoder e il post-LN

La convenzione post-LN ha una conseguenza direttamente testabile: essendo la
LayerNorm l'ultima operazione, con `gamma2 = 1` e `beta2 = 0` l'output ha media
0 e varianza 1 sull'ultimo asse. Con pre-LN questa asserzione è falsa, ed è per
quello che il test la usa: è il modo più economico per verificare che
l'ordinamento delle operazioni sia quello dichiarato.

C'è poi un test più sottile: azzerando `Wo` e `W2` entrambi i sottomoduli
diventano nulli e deve restare solo il cammino residuo, cioè
`LayerNorm(LayerNorm(X))`. Il confronto è con `layer_norm(X, gamma1, beta1)`,
sfruttando che la LayerNorm è idempotente a meno di `eps` (da cui `atol=1e-4`).
Chi ha dimenticato il residuo, o lo ha sommato dopo la normalizzazione invece
che prima, ottiene zero e il test fallisce.

Il test verifica infine che la causalità sopravviva al blocco intero. Non è
scontato a priori ma lo diventa una volta capito che la feed-forward è
*position-wise*: applica gli stessi pesi a ogni posizione separatamente, senza
mai mescolarle. Tutto il mescolamento è nell'attenzione, quindi mascherare lì
basta. Se qualcuno implementasse la FFN con una convoluzione o con un flatten
sulle posizioni, questa asserzione lo prenderebbe.

## Il costo

`attention_complexity` non pretende di essere un conteggio esatto — nessuno lo
è, dipende da come si contano fused multiply-add e da cosa si tiene in memoria.
La convenzione è documentata nella docstring e il test la verifica una volta su
un caso piccolo, ma le asserzioni che contano sono asintotiche: raddoppiando
`L` con `d` fisso il costo deve tendere a quadruplicare (a `L = 1e5`, `d = 64`
il rapporto misurato è `3.997`), mentre raddoppiando `d` deve solo circa
raddoppiare. È il contrasto fra i due comportamenti a dire che il collo di
bottiglia è la lunghezza e non la dimensione, e a motivare tutta la letteratura
sull'attenzione efficiente.
