# Note sulla soluzione — 03 core, least core, nucleolo

## L'idea in una frase

Core, strong ε-core e nucleolo sono lo stesso poliedro guardato tre volte:
`C_ε = {x preimputazione : e(S,x) ≤ ε ∀S proprio}`. Il core è `C_0`; il least
core è `C_{ε*}` con `ε*` minimo per cui `C_ε ≠ ∅`; il nucleolo è ciò che resta
quando si continua a stringere anche il *secondo* excess più grande, poi il terzo,
e così via. Il codice è letteralmente questa frase.

## Perché serve il passo "attive in ogni soluzione ottima"

Dopo aver trovato `ε*`, il least core `C_{ε*}` in generale **non è un punto**:
è un poliedro. Le coalizioni il cui excess vale `ε*` in *tutto* `C_{ε*}` non
possono più migliorare, quindi vanno congelate come uguaglianze. Le altre —
quelle che raggiungono `ε*` solo in *qualche* punto di `C_{ε*}` — restano libere
e verranno trattate al giro successivo.

Congelare invece le coalizioni attive nel vertice restituito dall'LP è
l'errore classico: quel vertice è uno dei tanti ottimi, e la scelta dipende
dall'ordine di enumerazione. Il risultato diventa non deterministico e sbagliato.

Il test per distinguere i due casi è un LP in più per coalizione:
`max x(S)` con `ε` fissato a `ε*`. Se il massimo è ancora `v(S) − ε*`, `S` non
può essere allentata da nessuna parte → è attiva ovunque.

## Perché l'oracolo random funziona

Il nucleolo è l'unico minimo lessicografico di `θ` sull'insieme (convesso, chiuso)
delle preimputazioni, e `θ` è continua. Quindi confrontare `θ(x*)` con `θ(y)` per
migliaia di `y` casuali è un test debole ma **non vacuo**: qualunque errore
sistematico (coalizione dimenticata, segno dell'excess invertito, ordinamento
crescente invece che decrescente) produce un `x*` che perde contro moltissimi `y`.
Il confronto coi vertici del core e coi loro punti medi aggiunge i punti
"strutturati", che sono quelli su cui un'implementazione quasi-giusta sbaglia.

Nota che non è una dimostrazione di correttezza: è un oracolo. Se serve certezza
su un gioco specifico, il caso `n = 3` si fa a mano in dieci minuti.

## Costo e limiti

- `lp_min` enumera `C(m, d)` combinazioni. Per `n = 3`: `m = 7`, `d = 4` → 35.
  Per `n = 4`: `m = 15`, `d = 5` → 3003. Per `n = 5` diventerebbe `C(31,6) ≈ 736k`,
  oltre il tetto `MAX_COMBINAZIONI`: da qui il vincolo `n ≤ 4`.
- Un vero solutore userebbe il simplesso (`O(m)` iterazioni tipiche). Qui il punto
  non è l'efficienza ma non avere dipendenze e restare esatti.
- `nucleolus` fa `O(2^n)` LP per giro e al più `n` giri.

## Trappole

1. **Segno dell'excess.** `e(S,x) = v(S) − x(S)`: è l'*insoddisfazione*. Excess
   positivo = la coalizione prende meno di quanto potrebbe da sola. Chi lo
   definisce col segno opposto ordina tutto al contrario e il nucleolo diventa il
   punto peggiore invece del migliore.
2. **Includere N e la coalizione vuota in θ.** Entrambe hanno excess costante
   (`0` e `v(N) − x(N) = 0` su una preimputazione): includerle non cambia il
   minimo lessicografico ma cambia la lunghezza del vettore e fa fallire i test.
   La definizione usa solo le coalizioni proprie.
3. **Confrontare float con `==`.** Tutto lo schema vive di uguaglianze attive:
   senza tolleranza (`1e-7`) le coalizioni tight non vengono mai riconosciute e
   il ciclo non termina mai o termina subito.
4. **`np.linalg.solve` in batch.** `solve(M, rhs)` con `M` di forma `(K,d,d)` e
   `rhs` di forma `(K,d)` viene interpretato come sistema matriciale, non come
   `K` sistemi vettoriali: serve `rhs[..., None]` e poi `[..., 0]`. (È il bug che
   ho preso io scrivendo `lp.py`.)

## Fatti da ricordare all'orale

- Il core può essere vuoto (gioco di maggioranza a 3 giocatori: `ε* = 1/3 > 0`),
  il **nucleolo mai**: esiste ed è unico per ogni gioco TU. È l'argomento
  principale a favore del nucleolo come concetto di soluzione.
- Se il core è non vuoto, il nucleolo ci sta dentro (ed è nel least core).
- Il nucleolo è nel core ⇏ è il valore di Shapley: sono concetti diversi con
  assiomatizzazioni diverse. Sul gioco additivo coincidono, in generale no.
