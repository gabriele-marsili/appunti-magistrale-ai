# Note sulla soluzione — 01 minimax / alfa-beta

## L'invariante che rende corretta la potatura

Durante la visita, `alpha` è il *miglior valore già garantito a MAX* lungo il
cammino dalla radice, `beta` il *miglior valore già garantito a MIN*. La chiamata
`alphabeta(node, alpha, beta, ...)` non promette di restituire il valore minimax
esatto di `node`: promette il valore esatto **solo se questo cade dentro
`(alpha, beta)`**. Se cade fuori, restituisce un valore che è comunque abbastanza
buono da far scartare il nodo al livello superiore (fail-soft/fail-hard).

Da qui la correttezza: alla radice la finestra è `(-inf, +inf)`, quindi il valore
restituito è esatto. È l'argomento da esporre all'orale, non il codice.

## Trappole in cui è facile cadere

1. **Aggiornare la variabile sbagliata.** In un nodo di MAX si aggiorna solo
   `alpha`, in un nodo di MIN solo `beta`. Chi aggiorna entrambi ottiene tagli
   scorretti e il test dell'oracolo cade.
2. **`>` invece di `>=` nel cut-off.** Con `alpha > beta` si tagliano meno rami
   (risultato ancora corretto, ma il test sul risparmio medio può fallire); con
   una condizione sbagliata nel verso opposto si tagliano rami buoni e cambia il
   valore. Il taglio corretto è `if alpha >= beta: break`.
3. **Contare i nodi potati.** Se si incrementa il contatore prima del `break` su
   tutti i figli, il risparmio sparisce e il conteggio non dice più niente.
4. **`order_children` che modifica l'albero in place.** I `namedtuple` sono
   immutabili, ma la lista `children` no: `node.children.sort()` muterebbe
   l'albero originale e il confronto "stesso valore prima e dopo" diventerebbe
   vacuo. La soluzione costruisce nuovi `Node`.

## Complessità

- `minimax`: `Θ(b^d)` nodi, sempre.
- `alphabeta`: `Ω(b^⌈d/2⌉ + b^⌊d/2⌋ − 1)` foglie nel caso migliore (Knuth-Moore
  1975), `O(b^d)` nel caso peggiore. Nel caso migliore la profondità
  effettivamente esplorabile a parità di budget **raddoppia**: è l'unico enunciato
  quantitativo che vale la pena ricordare a memoria.
- `order_children` è ovviamente barare (calcola il minimax completo per
  ordinare); serve solo a esibire il caso migliore. Nella pratica si usano
  euristiche di ordinamento, che è esattamente il "deep guessing" delle slide L12:
  valutare solo i prossimi `m` ply con una funzione di valutazione euristica.

## Perché il risparmio medio è "solo" ~30-40%

Su alberi con foglie i.i.d. l'ordine dei figli è casuale, quindi si è lontani dal
caso migliore. Il numero atteso di foglie valutate cresce come `b^(0.75 d)`
circa (Knuth-Moore, branching factor efficace `b^0.75`), non come `b^(d/2)`.
È esattamente il senso della frase nelle slide: senza un buon ordinamento
l'alfa-beta aiuta, ma non salva dall'esplosione combinatoria.
