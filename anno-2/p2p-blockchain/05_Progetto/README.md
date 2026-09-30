# Progetto finale 25/26 - Decentralised Lending Service

Specifica ufficiale: `00_Consegna/v011_ProjectP2PBC_LAB2526.pdf` (versione 1.1 dell'11/05/2026). La v1.0 differisce solo in una parola: nella regola sulla compensazione "applicant" è corretto in "contributor". Leggi la v1.1 per intero, due volte, prima di scrivere qualsiasi riga di codice.

Consegna: un unico zip su Moodle (attività "Lab Project 25/26"). La deadline coincide con la data dell'appello su Valutami. Gruppi di massimo 2 persone.

## Cosa c'è in questa cartella

| Cartella / file | Contenuto | Chi lo riempie |
|---|---|---|
| `00_Consegna/` | Specifica PDF (v1.0, v1.1) e zip del docente con genesis file e account prefinanziato (keystore + password) | Docente, non modificare |
| `01_Requisiti.md` | Checklist di tutti i requisiti estratti dalla specifica, da spuntare | Tu, man mano |
| `02_Roadmap.md` | Percorso a step: per ogni step obiettivo, cosa studiare prima, domande a cui rispondere, criterio di "fatto" | Guida: leggila, non contiene soluzioni |
| `03_Decisioni.md` | Diario delle scelte progettuali (servirà per il report e per l'orale) | Tu |
| `ambiente/` | Chain privata geth (datadir, script di avvio) | Tu, allo step 1 |
| `hardhat/` | Progetto Hardhat: contratti, test, misure del gas | Tu, dagli step 2-3 (`npx hardhat --init` qui dentro) |
| `oracle/` | Oracle off-chain in Python che legge la blockchain Bitcoin | Tu, allo step 5 |
| `scripts/` | Script Python: setup, demo, strategia "vota sempre sì" | Tu, allo step 6 |
| `report/` | Report PDF di massimo 5 pagine | Tu, allo step 8 |

## Ambiente previsto dal laboratorio

Questi sono gli strumenti e le versioni indicati nelle slide di laboratorio: controlla lì i dettagli.

- **geth v1.13.15**: l'ultima versione che supporta Clique/PoA. Le versioni recenti non avviano la chain del genesis fornito (LAB09). Su Mac con chip Apple verifica tu quale build è disponibile per la tua architettura: fa parte dell'esercizio di setup.
- **Hardhat 3** (LAB10 usa 3.4.3) con template `node-test-runner-viem`, **Node 22** (via `nvm`). Test in Solidity (`.t.sol`, anche con forge-std) e in TypeScript (LAB10, LAB11).
- **web3.py** per gli script Python (LAB09, `02_Lab/LAB09.../materiale/example1-3.py`).
- **Remix** e MetaMask sono opzionali, per esplorare (LAB06, LAB07, LAB09).
- **Dati Bitcoin**: il link "ChaindataFolder" su Moodle (sezione del 17 marzo) e il parsing visto in LAB04/LAB05. L'oracle va eseguito solo sui primi 131.000 blocchi della mainnet.

> Genesis fornito: `chainId` 202526, Clique con `period` 10, account prefinanziato `0xd278…b523`. La specifica dice che gli account prefinanziati possono **solo trasferire valore**: non usarli per deployare o chiamare contratti.

## Regola d'oro

Committa spesso (git) e scrivi in `03_Decisioni.md` il **perché** di ogni scelta mentre la fai. All'orale ti chiederanno proprio quello, e a fine progetto non lo ricorderai.
