# Formato dati di una lezione (lessons/<ID>.json) e regole di scrittura

Questo file è il brief per chi scrive una lezione (subagente o nuova conversazione).
ID validi: `L01`..`L99` (teoria e seminari), `LAB01`..`LAB99` (laboratorio).

## Regole di contenuto (obbligatorie)

- Italiano corretto con accenti veri (è, à, perché, così, più, può). Niente emoji. Niente "e'" al posto di "è".
- **Guarda davvero ogni slide**: apri l'immagine PNG della pagina (non basarti solo sul testo estratto). Le figure vanno descritte per quello che mostrano davvero (assi, frecce, nodi, colori, numeri). Non inventare contenuti che la slide non ha.
- **Spiega, non tradurre**: per ogni slide di contenuto scrivi cosa dice, perché (motivazione, intuizione), e i collegamenti con lezioni precedenti (es. "come visto in L03 per Chord..."). Se la slide dà per scontato un passaggio, esplicitalo.
- Lunghezza indicativa: 80-220 parole per slide di contenuto; slide molto dense o tecniche anche di più; slide banali (titolo, sommario, "domande?") brevi. Le **slide divisorie** (solo titolo di sezione) hanno `kind: "divider"` e al massimo una riga.
- Le schede seguono **una per pagina del PDF, nello stesso ordine**, senza saltarne nessuna (`p` da 1 a N).
- `printed`: il numero stampato sulla slide se esiste ed è diverso da `p`, altrimenti `null`.
- Formule: usa LaTeX tra `$...$` (inline) o `$$...$$` (display) dentro le stringhe HTML. Per cose semplici (O(log N), 2^160) va bene anche HTML con `<sup>`.
- **Controlla formule e numeri con calcoli** (Python/numpy, script in /home/claude/p2p/work/<ID>/). Un riquadro "Attenzione" si mette **solo per errori certi** nella slide (formula sbagliata, numero sbagliato, affermazione tecnicamente falsa), con la versione corretta e il perché. Se hai solo un dubbio, NON mettere Attenzione: scrivilo nel report finale come dubbio. Refusi ortografici irrilevanti non contano.
- Riquadri (`boxes` in una scheda):
  - `attenzione` (rosso): solo errori reali nella slide, con correzione. Ogni box attenzione deve avere anche una voce in `corrections`.
  - `sapere` ("Da saper fare", arancione): conti, derivazioni, dimostrazioni, definizioni da dire all'orale (es. le tre proprietà dell'hash).
  - `approfondimento` (azzurro): materiale facoltativo oltre le slide (contesto storico, dettagli reali del protocollo, numeri attuali). Breve e corretto.
- In fondo alla lezione: guida allo studio a blocchi con minuti stimati; esercizi a mano con soluzione; esercizi di codice (vedi sotto); domande tipo orale con traccia di risposta.
- Domande d'orale: usa anche `/home/claude/p2p/src/testi/04_Esame/` (domande reali degli appelli passati). Se una domanda è stata davvero chiesta, metti `"real": true`.
- La dispensa esistente in `/home/claude/p2p/src/testi/03_Dispensa/` è materiale di confronto utile, ma la fonte sono le slide. Non copiarla: riscrivi scheda per scheda.

## Esercizi di codice (codeExercises)

Piccoli esercizi progressivi che fanno capire "facendo" i concetti della lezione (Python 3 standard library o numpy per la teoria; Solidity o Python per i lab/Ethereum). Da 3 a 6 per lezione, livelli `base`, `medio`, `avanzato`. Esempi: calcolare distanze XOR e bucket Kademlia, costruire una Merkle tree e verificarne una proof, simulare un hash puzzle con difficoltà, interprete a stack per uno script P2PKH, simulazione double spend, calcolo base fee EIP-1559. Ogni esercizio ha: consegna chiara, codice di partenza con TODO, 1-3 suggerimenti, soluzione completa **eseguita e testata da te**, output atteso (copiato dall'esecuzione vera), spiegazione. Per Solidity: compila la soluzione con solc (npm `solc`) prima di inserirla.

## Laboratori (ID LABxx)

Oltre alle schede delle slide, per ogni file di codice in `materiale/` (o gruppo di file correlati) crea una sezione in `code`: una scheda per blocco logico del codice (contratto, funzione, test) con il codice e la spiegazione. Esegui/compila ciò che si può (solc per Solidity, python per gli script, pandas per i CSV): cerca bug reali (overflow, reentrancy, controlli mancanti, unità wei/ether, segni, tipi, off-by-one) e mostra la correzione in un box `attenzione` (e in `corrections` con `p: null` e `where` che indica file e riga). Se produci figure di output (es. grafici dai CSV), salvale come PNG piccoli (max 700px di lato) e mettile in `figs` come data URI base64.

## Struttura JSON

```json
{
  "id": "L04",
  "kind": "teoria | seminario | lab",
  "num": 4,
  "date": "2026-02-23",
  "title": "Kademlia DHT",
  "teacher": "Laura Ricci",
  "pdf": "pdf/L04.pdf",
  "pages": 73,
  "summary": "<p>2-4 frasi: di cosa parla la lezione e perché conta.</p>",
  "sections": [ {"title": "Richiamo a Chord", "from": 1, "to": 9} ],
  "slides": [
    {
      "p": 1, "printed": null, "kind": "title | normal | divider",
      "title": "Titolo breve della scheda",
      "html": "<p>Appunti ...</p><ul><li>...</li></ul>",
      "boxes": [ {"type": "sapere | attenzione | approfondimento", "title": "...", "html": "<p>...</p>"} ]
    }
  ],
  "code": [
    {"title": "Creator.sol", "intro": "<p>...</p>",
     "blocks": [ {"title": "...", "lang": "solidity | python | typescript | java | text", "code": "...", "html": "<p>spiegazione</p>", "boxes": [], "figs": ["data:image/png;base64,..."]} ] }
  ],
  "study": [ {"title": "Blocco 1 - XOR e k-bucket (slide 10-30)", "minutes": 40, "html": "<p>cosa fare, come verificare di aver capito</p>"} ],
  "exercises": [ {"q": "<p>...</p>", "a": "<p>soluzione passo passo</p>"} ],
  "codeExercises": [
    {"title": "...", "level": "base | medio | avanzato", "lang": "python | solidity", "q": "<p>consegna</p>",
     "starter": "codice con TODO", "hints": ["..."], "solution": "codice completo", "output": "output atteso", "explain": "<p>...</p>"}
  ],
  "oral": [ {"q": "Domanda", "a": "<p>traccia di risposta: punti da toccare in ordine</p>", "real": false} ],
  "formulas": [ {"topic": "DHT e Kademlia", "name": "Distanza XOR", "tex": "d(x,y) = x \\oplus y", "note": "interpretata come intero; simmetrica, triangolare", "p": 14} ],
  "corrections": [ {"p": 23, "where": "slide 21", "wrong": "cosa dice la slide", "right": "versione corretta", "why": "motivazione e verifica (es. calcolo)"} ],
  "links": [ {"to": "L03", "why": "Kademlia riprende le DHT di L03 cambiando la metrica"} ]
}
```

Note:
- `sections`: 3-10 macro-sezioni che coprono tutte le pagine (from/to inclusi), usate per il menu della lezione.
- `formulas.topic`: usa uno di questi argomenti se possibile: "Overlay e DHT", "Crittografia", "Strutture dati", "Bitcoin: transazioni e script", "Bitcoin: mining e consenso", "Bitcoin: attacchi", "Lightning e canali", "Ethereum: gas e fee", "Ethereum: PoS", "Token", "IPFS", "Layer 2", "Accumulatori", "Identità", "Interoperabilità", "Solidity".
- `links`: collegamenti verso altre lezioni (L01..L23, LAB01..LAB12), sia precedenti sia successive quando ovvio dal programma.
- HTML ammesso: p, strong, em, ul, ol, li, code, pre, table/tr/th/td, h4, br, sup, sub, blockquote. Niente style inline, niente script, niente immagini esterne.
- Scrivi il JSON con `json.dump(obj, f, ensure_ascii=False, indent=1)` da Python: mai a mano.
- Valida con `python3 /home/claude/p2p/sito/validate.py <file.json>` finché non passa.

## Lab guidati ("guided", solo per i LAB)

Sezione "Rifallo tu": il lab rifatto da zero sul Mac dello studente (macOS, Apple Silicon), passo per passo, così si segue anche senza la registrazione.

```json
"guided": {
  "minutes": 120,
  "intro": "<p>Cosa costruisci, cosa impari, come si collega alle slide e al progetto.</p>",
  "prereq": "<p>Strumenti da installare (con comandi brew/npm/pip esatti e versioni) e file da scaricare.</p>",
  "steps": [
    {"title": "Crea il progetto Maven", "slides": [3, 4],
     "html": "<p>Perché questo passo, cosa fa ogni parte del codice.</p>",
     "file": "pom.xml", "lang": "xml", "code": "...contenuto completo del file...",
     "run": "mvn -q compile", "expected": "output reale copiato dall'esecuzione",
     "check": "<p>Come capisci che funziona / cosa provare a cambiare.</p>"}
  ]
}
```
- 6-15 passi; ogni passo ha `code` (file completo o pezzo da aggiungere, dicendo dove) e/o `run` (comandi da terminale).
- `slides`: le pagine del PDF a cui il passo si riferisce (il sito mette un pulsante "Codice" su quelle schede).
- Tutto va eseguito davvero prima di scriverlo; `expected` è l'output vero. Se un passo richiede rete Bitcoin o servizi non raggiungibili, dillo e dai un'alternativa locale.
- `lang`: java, solidity, python, typescript, javascript, json, xml, bash, text.
