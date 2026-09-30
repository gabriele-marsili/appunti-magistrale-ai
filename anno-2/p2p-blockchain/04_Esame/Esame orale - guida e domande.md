---
tags:
  - università/p2p-blockchain
  - esame
corso: "P2P & Blockchain 25-26 (9 CFU)"
docenti: "Laura Ricci, Damiano Di Francesco Maesa"
---

# Esame orale - guida e domande

Fonti: regole d'esame pubblicate su Moodle 25-26, chat Telegram del corso (luglio 2024 - settembre 2026), file `domandep2p.md` condiviso in chat l'8/07/2025 (resoconti di più orali). Dove un'informazione viene da un singolo studente è indicato: sono testimonianze, non regole ufficiali.

## Come funziona l'esame

### Regole ufficiali (Moodle 25-26)

L'esame è **progetto finale + orale**. La consegna avviene su Moodle (attività "Lab Project 25/26 - Decentralised Lending Service", aperta fino al 1/05/2027) come unico zip. **La deadline di consegna coincide con la data dell'appello su Valutami**: le date di Valutami sono date di consegna, non di orale. L'orale si tiene di solito **1-2 settimane dopo** la deadline; la data esatta viene comunicata dopo la consegna (via mail e/o su e-learning con i turni).

L'orale comprende la **discussione del progetto** e una **discussione di argomenti del corso non coperti dal progetto**. Il progetto si discute all'orale del primo appello a cui ci si iscrive. Si può usare il proprio laptop durante la discussione. Il progetto si può fare in gruppo di massimo 2, ma ognuno deve saperlo discutere da solo.

### Com'è in pratica (testimonianze)

- **Durata** circa 50 minuti (Giacomo, 21/08/2026).
- **Prima parte, circa 20 minuti: progetto.** Chiede di mostrare che funziona (demo), commenta la qualità del codice e le scelte implementative, chiede perché una cosa è stata fatta in un certo modo.
- **Seconda parte: teoria**, di solito 3-4 domande.
- **Stile delle domande**: ampie, su argomenti grossi. Ti lascia fare un discorso (perché serve un sistema, quali caratteristiche ha) e ti guida con domande successive verso ciò che vuole sentire. Non si fissa sui dettagli minuti, ma alcune definizioni "a elenco" le vuole complete (esempio ricorrente: le **tre proprietà dell'hash crittografico**).
- **Clima**: descritta come calma e gentile.
- **Chi ha fatto il progetto Ethereum** in genere non riceve domande su Ethereum/Solidity. Però una volta risultava che potesse chiedere argomenti Ethereum non emersi nella discussione del progetto (es. Proof of Stake). Fabio Piscitelli, 26/06/2026: "Potrebbe chiedertelo se proprio non ne avete parlato durante la discussione del progetto".
- **Argomenti grossi** secondo chi ha dato l'esame: Bitcoin, Ethereum, strutture dati, metodi crittografici, attacchi. Sulle applicazioni (token, NFT, applicazioni reali) domanda meno, ma senza garanzie.

> [!warning] Nota sulla versione del corso
>
> Dal 25-26 il corso è da **9 CFU** e il progetto è il "Decentralised Lending Service" su Ethereum. La vecchia modalità "presentazione su Bitcoin" e la versione da 6 CFU riguardano chi ha il piano di studi degli anni precedenti (per la versione da 6 CFU la prof ha indicato di attenersi a slide e progetto dell'e-learning dell'anno prima). Se hai dubbi su quale versione ti spetti, scrivi a laura.ricci@unipi.it prima di iniziare il progetto.

> [!tip] Cosa ne segue per te
>
> Col progetto su Ethereum, la parte di teoria all'orale tende a pescare da overlay/DHT, crittografia e strutture dati, Bitcoin e attacchi. Questi sono i blocchi da preparare meglio. Ethereum lo porti "gratis" solo se lo discuti bene nel progetto: preparati a collegare il tuo codice a gas, account model, PoS, trie.

## Domande reali degli orali passati

Riportate come raccontate dagli studenti (2024-2025, prof. Ricci). Tra parentesi la lezione della dispensa dove studiarle.

### Resoconti per esame

**Esame A** (progetto Ethereum)
1. Cosa sono gli UTXO? (L07, L08)
2. Cos'è la Lightning Network, perché è stata introdotta e come funziona? Risposta attesa: nasce per i limiti di scalabilità di Bitcoin. (L12)
3. Overlay non strutturati: se vuoi mandare informazioni su una rete non strutturata, che meccanismi usi? Flooding: qual è il problema (banda), cos'è il TTL? Expanding ring: progressione del TTL e algoritmo. (L02)

**Esame B** (progetto Ethereum)
1. Quali sono gli attacchi a Bitcoin? Come faresti un double spending? (L10)
2. DHT: differenza tra hash crittografico e consistent hashing. Le tre proprietà dell'hash crittografico. (L03, L05)
3. Come funziona Chord? (L03)

**Esame C**
1. Caratteristiche di un hash crittografico (one-way, collision resistance, ...). (L05)
2. Cos'è il malleability attack? (L10, L13)
3. Regola con cui Kademlia mappa oggetti e nodi; com'è fatta la routing table di Kademlia. (L04)

**Esame D**
1. Bitcoin: cos'è un escrow? (L11)
2. Cos'è il consistent hashing? (L03)
3. Cos'è un Merkle tree? Quando si usano Merkle root e Merkle proof in Bitcoin? (Voleva arrivare ai nodi SPV / light client.) (L06, L11)

**Esame E** (8/07/2025, progetto Ethereum, niente domande su Ethereum)
1. Consistent hashing. (L03)
2. Bitcoin: proof of work, tempo tra i blocchi, script. (L08, L09)
3. Distanze in Kademlia (XOR). (L04)

**Esame F** (8/07/2025, presentazione Bitcoin)
1. Differenza principale tra Ethereum e Bitcoin. (L14)
2. Blockchain trilemma. (L01, L22)
3. Come si risolve la scalabilità in Bitcoin ed Ethereum? (Lightning, dimensione blocco, intervallo tra blocchi.) Cos'è un rollup? (L12, L22)
4. Come sono organizzati i dati in Ethereum? Struttura del Merkle Patricia Trie. (L06, L18)

**Altre testimonianze sparse**
- Ottobre 2024: domande su DHT e Merkle tree (Ruggiero Dibenedetto).
- Esame da 6 CFU con presentazione Bitcoin: domande sul programma Bitcoin (UTXO, proof of work, script). Se la presentazione è dettagliata, fa meno domande. Se nomini qualcosa (es. malleability) ti chiede di approfondirlo.

### Frequenza per argomento

| Argomento | Volte chiesto | Lezioni |
|---|---|---|
| Consistent hashing / hash crittografico vs consistent | 4 | L03, L05 |
| Proprietà dell'hash crittografico | 3 | L05 |
| Kademlia (distanza XOR, routing table, mapping) | 2 | L04 |
| Merkle tree, Merkle proof, SPV | 2 (+1 DHT/Merkle) | L06, L11 |
| Attacchi Bitcoin (double spending, malleability) | 2 | L10, L13 |
| Scalabilità (Lightning, rollup, trilemma) | 2 | L12, L22, L01 |
| UTXO | 1 | L07, L08 |
| Chord | 1 | L03 |
| Overlay non strutturati (flooding, TTL, expanding ring) | 1 | L02 |
| Escrow | 1 | L11 |
| PoW, tempo di blocco, script | 1 | L08, L09 |
| Ethereum vs Bitcoin, Merkle Patricia Trie | 1 | L14, L18 |

Il campione è piccolo (una decina di orali), ma lo schema è chiaro. Ogni orale pesca quasi sempre **una domanda P2P/DHT**, **una di crittografia o strutture dati** e **una su Bitcoin** (meccanismi o attacchi).

## Domande di teoria da allenare (inventate, sul programma 25-26)

Sono formulate nello stile della prof: domande ampie, da sviluppare come discorso. Le risposte non ci sono apposta. Prova a rispondere ad alta voce in 3-5 minuti ciascuna, poi controlla sulla dispensa.

### P2P, overlay e DHT
1. Cosa distingue un sistema P2P da un sistema client-server? Quali proprietà (scalabilità, churn, fault tolerance) motivano il P2P? (L01)
2. Confronta overlay non strutturati e strutturati: pro, contro e quando useresti l'uno o l'altro. (L02, L03)
3. Gnutella: come avviene la ricerca, che problemi ha il flooding e come li mitigano super-peer, expanding ring, random walk? (L02)
4. Perché il semplice hashing modulo N non funziona in un sistema P2P e come lo risolve il consistent hashing? Cosa succede al join e al leave di un nodo? (L03)
5. Chord: finger table, lookup in $O(\log N)$, gestione di join e stabilizzazione. (L03)
6. Kademlia: perché la metrica XOR, com'è fatta una k-bucket, come avviene un lookup iterativo e parallelo, perché preferisce i nodi vecchi? (L04)
7. Dove si usa Kademlia nella pratica (BitTorrent, Ethereum discovery, IPFS)? (L04, L16, LAB01)

### Crittografia e strutture dati
8. Proprietà dell'hash crittografico, cosa garantisce ciascuna e dove serve nella blockchain. (L05)
9. Firme digitali e crittografia a chiave pubblica: come si usano in Bitcoin per autorizzare una spesa? (L05, L08)
10. Hash pointer e blockchain come lista tamper-evident: perché modificare un blocco invalida tutti i successivi? (L06, L07)
11. Merkle tree: costruzione, Merkle proof, costo di verifica, uso nei nodi SPV. (L06, L11)
12. Bloom filter: a cosa servono, falsi positivi, come li usano i client SPV e che problema di privacy hanno. (L06, L11)
13. Merkle Patricia Trie: perché Ethereum ne ha bisogno e quali trie ci sono nel blocco. (L06, L18)

### Blockchain e Bitcoin
14. Quale problema risolve la blockchain? Double spending, consenso, Byzantine generals. (L07)
15. Modello UTXO vs modello ad account: vantaggi e svantaggi. (L07, L08, L14)
16. Come è fatta una transazione Bitcoin e come la valida lo Script (P2PKH passo passo)? (L08)
17. Proof of Work: difficoltà, target, aggiustamento ogni 2016 blocchi, perché 10 minuti. (L09)
18. Longest chain rule, fork temporanei, perché si aspettano 6 conferme. (L09, L10)
19. Mining pool: perché esistono, come si distribuiscono le ricompense, che rischi portano alla decentralizzazione. (L10)
20. Attacchi: double spending, 51%, Sybil, eclipse, selfish mining, malleability. Come funzionano e quali contromisure ci sono? (L10, L13)
21. Multisig, P2SH, timelock ed escrow: come si costruisce uno scambio con arbitro? (L11)
22. Hard fork vs soft fork, con esempi (SegWit, Bitcoin Cash, Taproot). (L13)
23. Scalabilità di Bitcoin: perché è limitata e quali soluzioni esistono (on-chain vs off-chain)? (L12, L13)
24. Lightning Network: canali di pagamento, commitment transaction, HTLC, routing multi-hop, cosa succede se una parte bara. (L12)

### Ethereum e oltre (se non emersi nella discussione del progetto)
25. Ethereum vs Bitcoin: account model, stato, smart contract, gas. (L14)
26. Il gas: perché esiste, come si calcola la fee, cosa cambia con EIP-1559. (L14, L18)
27. Proof of Stake in Ethereum: validatori, slot ed epoche, finalità (Casper FFG), slashing. (L17)
28. Trilemma della blockchain e soluzioni di scaling Layer 2: rollup optimistic vs ZK. (L22)
29. IPFS: content addressing, CID, ruolo della DHT, perché serve per gli NFT. (L16, L15)
30. Token ERC-20 ed ERC-721: interfaccia, differenze, allowance. (L15)

## Domande sul progetto da aspettarsi (inventate)

Nella prima parte dell'orale si discute il tuo codice. Queste domande servono a verificare che tu abbia capito le scelte, non solo che il codice funzioni. Usale anche come checklist mentre sviluppi.

**Architettura**
1. Com'è organizzato il bundle di contratti? Perché ogni prestito attivo è un contratto separato e quali costi e vantaggi ha questa scelta?
2. Come hai reso aggiornabile (upgradable) il contratto principale? Che pattern hai usato e che rischi introduce?
3. Come gestisci la "terminazione" dei contratti? Perché non basta `selfdestruct`?

**Logica di business**
4. Come calcoli il valore disponibile (disposable value) di ogni contributor e il peso del suo voto? Cosa succede se cambia tra il voto e la risoluzione?
5. Come hai gestito l'aritmetica a precisione finita (arrotondamenti nel blocco dei fondi e nella ripartizione degli interessi)? Dove finisce la differenza?
6. Come ordini i contributor nel rimborso (dal lock più alto al più basso, pareggi per indirizzo)? Quanto costa in gas questo ordinamento e come lo hai reso sostenibile?
7. Come evolve la percentuale di collaterale globale? Quando un prestito è "fallito" e perché può essere marcato solo una volta?
8. Come misuri il tempo? Perché in block height e non in timestamp?

**Oracle**
9. Com'è fatto l'oracle: parte on-chain e parte off-chain. Come nota le richieste (eventi)? Come calcola il saldo di un indirizzo (somma degli UTXO)?
10. Perché elabori un blocco alla volta? Come gestiresti una riorganizzazione della catena Bitcoin?
11. Come hai calcolato la fee minima dell'oracle (gas dell'update × 0,1 gwei)?
12. Quali sono i limiti di sicurezza dell'oracle centralizzato e della prova di liquidità senza firma? Come li risolveresti in un sistema reale?

**Sicurezza e costi**
13. Mostra la variante vulnerabile a reentrancy e l'attacco. Perché funziona e quali difese esistono (checks-effects-interactions, reentrancy guard, pull payment)?
14. Quali operazioni costano di più in gas e perché? Come le hai misurate?
15. Esiste una strategia per cui un contributor guadagna ingiustamente a spese degli altri (es. sfruttando la regola del voto a maggioranza o l'ordine di rimborso)? Descrivila e proponi una contromisura.
16. Lo script del contributor che vota sempre sì: come si accorge delle nuove proposte? Polling o filtri di eventi?

**Ambiente**
17. Perché gli account prefinanziati del genesis si possono usare solo per trasferire valore? Come hai creato e finanziato gli altri account?
18. Che consenso usa la tua chain privata (Clique, PoA) e come si confronta con PoW e PoS visti a lezione?
