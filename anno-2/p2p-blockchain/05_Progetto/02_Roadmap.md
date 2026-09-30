# Roadmap a step

Questa roadmap **non contiene soluzioni**. Per ogni step trovi:
- **Obiettivo**: cosa ottieni alla fine.
- **Prima studia**: le lezioni e i lab da vedere prima.
- **Domande guida**: rispondi per iscritto in `03_Decisioni.md` prima di scrivere codice.
- **Fatto quando**: il criterio per passare allo step successivo.

Se ti blocchi su uno step, chiedimi un **suggerimento mirato** su quel punto, non la soluzione. Imparerai di più, e all'orale discuterai codice che hai scritto tu.

Prerequisiti di teoria prima di partire: L14 (account, transazioni, gas), L15 (token, per vedere contratti reali), L08 (UTXO, che ti serve per l'oracle). Di laboratorio: da LAB06 a LAB11.

---

## Step 0 - Capire il sistema su carta (1-2 giorni)

**Obiettivo:** un modello del sistema che sai spiegare senza guardare la specifica.

**Prima studia:** la specifica v1.1, tutta.

**Domande guida**
- Disegna gli stati di una proposta e di un prestito (proposta attiva, rifiutata, approvata; prestito attivo, successful, failed). Quali transizioni esistono e chi le innesca?
- Quali dati servono per ogni contributor, ogni proposta e ogni prestito? Dove vivono (contratto principale o contratto del prestito)?
- Rifai a mano l'esempio del blocco 10/20/30 → 2/4/6. Poi inventane uno con arrotondamento (es. importo 10 su 3 contributor uguali): dove finisce il resto?
- Simula a mano un rimborso parziale di un prestito con 3 contributor: quanto va a ciascuno come capitale, quanto come guadagno e quanto al compensation pool?
- Elenca gli eventi che emetteresti e chi li ascolterà (script del votante automatico, oracle).

**Fatto quando:** hai un diagramma a stati e 2-3 esempi numerici svolti a mano. Diventeranno i tuoi primi casi di test.

---

## Step 1 - Chain privata funzionante

**Obiettivo:** un nodo geth avviato dal genesis del docente, un account nuovo finanziato dall'account prefinanziato, una transazione verificata da Python.

**Prima studia:** LAB09 (setup geth, Clique, web3.py), LAB01 (opzioni di rete di geth). Il materiale è in `02_Lab/LAB09 - 2026-04-27/materiale/`.

**Domande guida**
- Perché serve proprio geth 1.13.15? Cosa cambia nelle versioni successive?
- Nel genesis, cosa significano `clique.period`, `extradata` e `alloc`? Perché l'indirizzo compare in `extradata`?
- Come fai a trasferire valore dall'account prefinanziato a un account nuovo senza usare il prefinanziato per altro?

**Fatto quando:** da uno script Python stampi il saldo del nuovo account dopo averlo finanziato. I comandi di avvio sono salvati in `ambiente/`.

---

## Step 2 - Hardhat e un contratto giocattolo

**Obiettivo:** un progetto Hardhat in `hardhat/` con un contratto minimo (solo deposito e prelievo) e i suoi test.

**Prima studia:** LAB06-LAB07 (Solidity), LAB10 (Hardhat 3, test in Solidity), LAB11 (test in TypeScript, misura del gas).

**Domande guida**
- Test in Solidity o in TypeScript: quali scenari sono più comodi nell'uno e quali nell'altro?
- Come simuli più utenti e il passare dei blocchi (serve per il periodo di voto e la scadenza)?
- Come verifichi in un test che una chiamata debba fallire (revert)?

**Fatto quando:** `npx hardhat test` passa con test di deposito, deposito sotto il minimo (revert) e prelievo oltre il disponibile (revert).

---

## Step 3 - Il contratto principale: pool, proposte, voto

**Obiettivo:** deposito, prelievo, proposta, voto e risoluzione, con il blocco proporzionale dei fondi. Per ora il controllo di liquidità è un mock che risponde sempre "ok".

**Prima studia:** LAB08 (pattern e vulnerabilità), L14 (costi dello storage).

**Domande guida**
- Il voto è pesato sul disposable value **al momento della risoluzione**, non del voto. Quali conseguenze ha sul modo in cui salvi i voti?
- Iterare su tutti i contributor costa gas in proporzione al loro numero. È accettabile? Che limiti imponi o documenti?
- Come eviti che il totale bloccato superi il disposable value, tenendo conto degli arrotondamenti?

**Fatto quando:** i test coprono approvazione, rifiuto, pareggio, fondi insufficienti e risoluzione chiesta troppo presto o da un altro utente. Gli esempi numerici dello step 0 passano come test.

---

## Step 4 - Il contratto del prestito: rimborsi, fallimento, compensazione

**Obiettivo:** un contratto deployato per ogni prestito, con rimborso parziale, marcatura di fallimento e compensazione dal compensation pool. In più, aggiornamento della percentuale di collaterale.

**Prima studia:** L20 (lending e applicazioni reali), LAB08 (contratti che creano contratti, `Creator.sol` nel materiale).

**Domande guida**
- Come comunicano il contratto principale e quello del prestito? Chi custodisce il valore bloccato?
- L'ordine di rimborso (dal lock più alto al più basso, pareggi per indirizzo): lo calcoli una volta alla creazione o a ogni rimborso? Quanto costa?
- La compensazione "fa perdere in proporzione i rimborsi successivi". Formalizza questa regola con un esempio numerico prima di scriverla in codice.
- Cosa significa "terminare" un contratto di prestito concluso, visto lo stato attuale di `selfdestruct`?

**Fatto quando:** i test coprono rimborso completo in una volta, rimborso in più rate, rimborso eccedente, prestito scaduto, compensazione ripetuta e rimborso dopo una compensazione.

---

## Step 5 - Oracle Bitcoin

**Obiettivo:** contratto oracle on-chain e un processo Python che legge i blocchi Bitcoin (i primi 131.000), tiene gli UTXO per indirizzo e risponde alle richieste scrivendo i saldi sul contratto.

**Prima studia:** L08 (transazioni e UTXO), LAB04-LAB05 (parsing della blockchain, dati "ChaindataFolder" su Moodle), LAB09 (web3.py ed eventi).

**Domande guida**
- Il componente off-chain deve elaborare "un blocco alla volta, come se arrivassero in tempo reale". Come strutturi il loop?
- Quali tipi di output hanno gli indirizzi nei primi 131.000 blocchi (P2PK, P2PKH)? Come ricavi l'indirizzo da un output P2PK?
- Come ti accorgi delle richieste: filtro sugli eventi o polling?
- Come calcoli la fee minima (gas dell'update × 0,1 gwei)? Il gas dell'update è sempre lo stesso?
- Bitcoin ha 8 decimali, Solidity non ha i float: in che unità salvi i saldi e come applichi il cambio 1 BTC = 30 ETH senza perdere precisione?

**Fatto quando:** chiedi il saldo di un indirizzo noto (es. di un blocco dei primi) e, dopo l'elaborazione, il contratto riporta il valore giusto. Controllalo a mano su un block explorer. Una risoluzione con liquidità insufficiente viene rifiutata.

---

## Step 6 - Upgradability ed eventi

**Obiettivo:** il contratto principale è aggiornabile e tutti gli eventi utili vengono emessi.

**Prima studia:** LAB08 (migrazione, separazione logica/dati: `CreatedMigration.sol`, `CreatedSeparation.sol`).

**Domande guida**
- Migrazione dello stato, separazione dati/logica o proxy: pro e contro di ciascuno per questo progetto?
- Cosa succede ai contratti di prestito già deployati quando aggiorni il principale?

**Fatto quando:** un test mostra un aggiornamento che conserva lo stato (depositi e prestiti attivi).

---

## Step 7 - Script Python, gas e sicurezza

**Obiettivo:** tutti i deliverable della sezione 1.5.

**Prima studia:** LAB09 (web3.py), LAB11 (misura del gas), LAB08 (reentrancy: `Victim.sol`, `Attacker.sol`).

**Da produrre**
- `scripts/setup`: crea gli account, li finanzia dal prefinanziato, deploya oracle e servizio.
- `scripts/demo`: uno scenario completo con stampa dei saldi e dello stato dopo ogni passo significativo.
- `scripts/auto_voter`: un contributor che vota sempre "approve" appena nota una proposta.
- Una tabella con il gas di ogni operazione.
- Una copia modificata e vulnerabile a reentrancy, un contratto attaccante e un test che mostra l'attacco.

**Domande guida**
- Quale punto del tuo codice, modificato, diventerebbe vulnerabile? Perché la versione originale non lo è?
- Strategia malevola di un contributor senza reentrancy: ragiona su tempi di deposito e prelievo rispetto a voto e risoluzione, e sull'ordine di rimborso. Chi ci guadagna e chi ci perde?

**Fatto quando:** eseguendo di fila setup e demo sulla chain privata ottieni un output leggibile senza errori.

---

## Step 8 - Report e preparazione all'orale

**Obiettivo:** un report PDF di massimo 5 pagine e uno zip di consegna ordinato.

**Struttura suggerita del report:** scelte implementative (1,5 pagine), gas (0,5), reentrancy (0,5), strategia malevola (1), manuale utente (1).

**Fatto quando:**
- Tutte le voci di `01_Requisiti.md` sono spuntate.
- Sai fare la demo in 5 minuti.
- Sai rispondere alle domande sul progetto in `04_Esame/Esame orale - guida e domande.md`.
