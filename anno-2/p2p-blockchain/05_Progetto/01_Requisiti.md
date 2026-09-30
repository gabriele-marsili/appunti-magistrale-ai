# Checklist requisiti (dalla specifica v1.1)

Spunta `[x]` solo quando il requisito è **implementato e coperto da almeno un test**. Il riferimento tra parentesi è alla sezione della specifica.

## Attori (1.1)
- [ ] Un utente può essere contributor e applicant contemporaneamente
- [ ] Contributor = chiunque abbia un saldo non nullo nel funding pool (valore bloccato incluso)
- [ ] Applicant = chiunque abbia una proposta attiva, un prestito attivo o un prestito concesso/negato

## Pool (1.2)
- [ ] Funding pool: depositi dei contributor, in parte bloccati nei prestiti
- [ ] Compensation pool: alimentato da una parte degli interessi, usato per i prestiti falliti

## Operazioni dei contributor (1.3)
- [ ] Deposito, rifiutato se sotto il minimo (100 000 wei)
- [ ] Prelievo, limitato al *disposable value* (non bloccato)
- [ ] Voto booleano solo su proposte attive; chi non vota conta come "reject"
- [ ] Richiesta di compensazione solo per prestiti falliti (scaduti e non interamente rimborsati)
- [ ] La compensazione copre solo il valore bloccato non ancora rimborsato (esclusi gli interessi già pagati); si può ricevere meno se il pool non basta
- [ ] La compensazione si può richiedere più volte per lo stesso prestito
- [ ] La compensazione fa perdere in proporzione i rimborsi successivi dell'applicant
- [ ] Un prestito è marcato fallito una sola volta e non può tornare "successful"; la marcatura aggiorna la percentuale di collaterale

## Operazioni degli applicant (1.3)
- [ ] Richiesta all'oracle di aggiornare il saldo di un indirizzo Bitcoin
- [ ] Proposta di prestito: importo, tasso di interesse (intero 1-100), durata, indirizzo Bitcoin
- [ ] Richiesta di risoluzione: solo l'applicant originale e solo dopo il periodo di voto (12 blocchi)
- [ ] Rifiuto se il disposable value totale è minore dell'importo
- [ ] Rifiuto se il controllo di liquidità Bitcoin fallisce
- [ ] Voto pesato sul disposable value corrente; il pareggio conta come rifiuto
- [ ] Una proposta chiusa non riceve più voti né richieste di risoluzione
- [ ] In caso di approvazione: blocco proporzionale al disposable value di ciascuno (esempio 10/20/30 → 2/4/6 su 12)
- [ ] L'arrotondamento viene sottratto dall'importo prestato, che riflette il valore effettivo
- [ ] Nuovo contratto dedicato per ogni prestito attivo, con la percentuale di collaterale corrente
- [ ] Rimborso parziale solo dall'applicant originale, anche per prestiti falliti, anche oltre l'importo dovuto
- [ ] Ripartizione del rimborso in quota capitale e quota interessi
- [ ] Capitale: rimborso in ordine di valore bloccato iniziale decrescente, pareggi per indirizzo; l'eccedenza va al compensation pool
- [ ] Interessi: divisi in guadagno e collaterale secondo la percentuale del prestito
- [ ] Guadagno accreditato direttamente ai contributor (non al pool); gli arrotondamenti vanno al compensation pool
- [ ] Collaterale interamente al compensation pool
- [ ] Rimborso completo → prestito "successful", aggiornamento del collaterale, chiusura

## Costanti e note (1.3)
- [ ] Tempo misurato in differenza di block height
- [ ] Periodo di voto = 12
- [ ] Deposito minimo = 100 000 wei
- [ ] Collaterale iniziale 50, tra 1 e 100, +5 per ogni fallimento e -5 per ogni successo
- [ ] Indirizzo del contratto oracle configurato
- [ ] Fee minima dell'oracle = gas dell'update × 0,1 gwei (calcolata sulla tua implementazione)
- [ ] Cambio fisso 1 BTC = 30 ETH

## Oracle (1.4)
- [ ] Contratto on-chain: saldo in BTC per un insieme di indirizzi
- [ ] Funzione di richiesta a pagamento (fee ≥ minima), che aggiunge o aggiorna un indirizzo
- [ ] Componente off-chain che serve tutte le richieste: saldo disponibile = somma degli UTXO dell'indirizzo
- [ ] Controllo di liquidità in risoluzione: saldo × 30 ≥ importo → superato
- [ ] Off-chain progettato per elaborare un blocco alla volta, eseguito sui primi 131 000 blocchi

## Implementazione (1.5)
- [ ] Eventi emessi dove servono (es. nuova proposta)
- [ ] Un contratto dedicato per ogni prestito attivo
- [ ] Gestione della "terminazione" dei contratti
- [ ] Upgradability del contratto principale
- [ ] Test Hardhat su diversi scenari e comportamenti degli utenti
- [ ] Chain privata locale dal genesis fornito; account prefinanziati usati solo per trasferimenti
- [ ] Script Python di setup iniziale (creazione account inclusa)
- [ ] Script Python di demo con stampa dei saldi e dello stato dopo ogni cambiamento significativo
- [ ] Script Python del contributor automatico che vota sempre "approve" e si accorge delle nuove proposte
- [ ] Test o script che misurano il costo in gas di ogni operazione
- [ ] Variante vulnerabile a reentrancy + test di attacco (con eventuale contratto malevolo)
- [ ] Discussione di una strategia malevola di un contributor (senza reentrancy)

## Consegna (2)
- [ ] Sorgenti Solidity di tutti i contratti
- [ ] Tutti gli script di test e deploy
- [ ] Zip della cartella Hardhat
- [ ] Report PDF di massimo 5 pagine: scelte implementative, gas, reentrancy, strategia malevola, breve manuale utente
- [ ] Tutto in un unico zip, con struttura di cartelle leggibile
