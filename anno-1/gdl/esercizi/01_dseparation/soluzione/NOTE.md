# Note sulla soluzione

## Perche' due algoritmi invece di uno

La soluzione implementa la d-separazione due volte, di proposito.

`active_paths` e' la trascrizione letterale della definizione di slide: enumera
tutti i cammini semplici non orientati fra `x` e `y` con una DFS sullo
scheletro del DAG, e per ciascuno guarda i nodi interni uno alla volta. Per
ogni tripla `(prev, mid, nxt)` il tipo di sottostruttura si legge da due soli
test booleani: `prev in dag[mid]` dice se la freccia entra in `mid` da
sinistra, `nxt in dag[mid]` se entra da destra. Se entrambi sono veri e' un
collider, altrimenti e' una catena o un fork — e la distinzione fra catena e
fork non serve, perche' la regola di blocco e' identica (`mid ∈ Z` blocca).
Questo e' il primo punto che sorprende chi studia le tre sottostrutture come
tre casi separati: ai fini del blocco i casi sono due, non tre.

`is_dseparated` usa invece **Bayes-Ball** (l'algoritmo `Reachable` di Koller &
Friedman, 3.1). Enumerare i cammini e' corretto ma esponenziale; Bayes-Ball e'
lineare nel numero di archi perche' visita stati `(nodo, direzione)` invece che
cammini. La direzione e' l'unica cosa che serve ricordare del passato: `"up"`
significa che siamo arrivati nel nodo da un suo figlio, `"down"` che ci siamo
arrivati da un suo genitore. Le regole di espansione sono la traduzione
meccanica delle tre sottostrutture, e vale la pena rileggerle guardando quale
sottostruttura codifica ciascuna:

- `("up", y)` con `y ∉ Z`: si sale ai genitori (catena `pa -> y -> ch`) e si
  scende agli altri figli (fork `ch <- y -> ch'`). Entrambe attive perche' `y`
  non e' osservato.
- `("down", y)` con `y ∉ Z`: si scende ai figli (catena `pa -> y -> ch`).
- `("down", y)` con `y ∈ An(Z)`: si risale ai genitori. Questo e' il collider,
  ed e' l'unica regola con una condizione **positiva** su `Z`.

Che le due implementazioni concordino su tutte le coppie e tutti i
condizionamenti dei tre grafi e' verificato da `test_active_paths`. E' il modo
piu' economico per accorgersi di aver sbagliato un caso.

## Il trucco `An(Z)`

La condizione del collider e' "ne' `Yc` ne' alcun suo discendente appartiene a
`Z`". Scritta cosi' invita a calcolare i discendenti di `Yc` e intersecarli con
`Z`, per ogni collider incontrato. E' inutilmente costoso. La stessa condizione
si scrive come `Yc ∈ An(Z)`, dove `An(Z)` include `Z` stesso: "`Yc` ha un
discendente in `Z`" e' letteralmente "`Yc` e' antenato di qualcosa in `Z`".
`An(Z)` si calcola **una volta sola** all'inizio, e questo e' anche il motivo
per cui la specifica di `ancestors` chiede di includere i nodi di partenza —
senza quell'inclusione il caso `Yc ∈ Z` andrebbe trattato a parte.

## Errori tipici

Il piu' comune e' dimenticare i **discendenti** del collider: si scrive
`if mid not in Z: return False` e la funzione risponde correttamente su
`X ⊥ Y | Z` e sbagliato su `X ⊥ Y | W`. E' esattamente il caso che le slide
sottolineano con "if any Y2 descendants is observed it unlocks the path", ed e'
la cosa che viene chiesta all'orale.

Il secondo e' invertire la logica del collider, cioe' trattarlo come catena e
fork: cosi' `D` e `I` risultano dipendenti a priori e indipendenti dato `G`,
ossia il contrario della verita'. Se il test `test_dsep_collider` fallisce su
tutte e tre le asserzioni contemporaneamente, e' quasi certamente questo.

Il terzo riguarda il **Markov blanket**: si scrive `pa(v) ∪ ch(v)` e ci si
ferma. I co-genitori servono proprio perche' il figlio e' un collider fra `v` e
gli altri suoi genitori: condizionare su `ch(v)` apre il cammino `v -> c <- u`,
e per richiuderlo bisogna osservare anche `u`. `test_markov_blanket` controlla
`Mb(D) = {G, I}`: `I` non e' ne' genitore ne' figlio di `D`, e' li' solo perche'
`G` e' un collider. `test_markov_blanket_scherma_ed_e_minimale` verifica anche
la minimalita' — togliendo un qualsiasi elemento dal blanket la schermatura si
rompe — e questa e' la ragione per cui il blanket e' *quello* e non un
soprainsieme qualunque.

Il quarto e' sull'**ordine dei genitori** in `factorization`. La specifica dice
"nell'ordine in cui compaiono in `dag[node]`": chi ordina alfabeticamente per
sicurezza qui passa comunque, perche' le costanti hanno gia' i genitori in
ordine alfabetico, ma su un DAG scritto a mano con `{"G": ["I","D"]}` il
risultato cambierebbe. La convenzione conta perche' e' la stessa che indicizza
gli assi delle CPT in `random_cpts`, e `test_factorization_ricostruisce_la_congiunta`
usa proprio la stringa prodotta come ricetta per rimoltiplicare le CPT.

## L'oracolo numerico e la faithfulness

`test_oracolo_numerico_dsep_implica_indipendenza` non guarda il grafo: prende
la tabella congiunta costruita da `enumerate_joint` e misura, per forza bruta
su tutte le celle, la massima violazione di `P(x,y,z) P(z) = P(x,z) P(y,z)`.
Quella forma prodotto e' la definizione di indipendenza condizionale senza
divisioni, quindi non c'e' bisogno di trattare a parte i casi `P(z) = 0`.

Le due direzioni testate non hanno lo stesso statuto logico ed e' bene averlo
chiaro all'orale. `d-separazione ⇒ indipendenza` e' la **Global Markov
property**: e' un teorema, vale per ogni parametrizzazione, e infatti la
violazione misurata e' dell'ordine di `1e-16`, cioe' puro errore macchina.
`non d-separazione ⇒ dipendenza` e' invece la **faithfulness**: non e' un
teorema, e' una proprieta' che vale per quasi ogni scelta dei parametri ma che
si puo' rompere con cancellazioni esatte fra cammini. Con CPT casuali e seed
fissato la violazione minima misurata e' circa `9e-5`, quasi due ordini di
grandezza sopra la soglia `1e-6` usata nel test, quindi il test e' stabile e non
flaky; il `+0.1` in `random_cpts` serve a tenersi lontani da CPT quasi
deterministiche, che avvicinerebbero pericolosamente i due regimi.

Vale la pena notare cosa succederebbe se la faithfulness fallisse: il grafo
direbbe "dipendenti" e i numeri direbbero "indipendenti". Non sarebbe un bug
del codice — sarebbe il grafo che rappresenta *meno* indipendenze di quante ne
esistano nella distribuzione, che e' esattamente il caso che rende impossibile
il recupero della struttura nei metodi constraint-based (PC, FCI) della lezione
sullo structure learning.

## Collegamento alle slide

- `GDL4 bayesian networks II.pdf`, slide "Blocked Path" e "d-Separation": la
  definizione trascritta in `_path_is_active`.
- `GDL4`, slide "Global Markov Property" e "Faithfulness Property": le due
  direzioni dell'oracolo numerico.
- `GDL4`, slide "Markov Blanket": genitori, figli e *children's parents*.
- `GDL3 bayesian networks I.pdf`, slide "Head-to-Head Connections": la riga
  "If any Y2 descendants is observed it unlocks the path", che e' tutto
  l'esercizio in una frase.
- `GDL3`, slide "Joint Probability Factorization": ordine topologico + chain
  rule + local Markov property, cioe' `factorization`.
