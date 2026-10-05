# Copione della videolezione di una lezione

## Cos'è
Sul sito, la dispensa di ogni lezione si può "guardare" come una videolezione. Le pagine della dispensa scorrono da sole. Una voce sintetica italiana (quella del dispositivo di Octech: Alice, Federica o Luca su Mac e iPhone) legge un copione parlato, con i sottotitoli e il blocco di cui si sta parlando evidenziato. Octech la guarda a 0.5x, 1x, 1.5x o 2x.

Octech (magistrale AI a Pisa) non segue le lezioni e dalle slide non ha capito quasi nulla. La videolezione deve spiegargli la lezione come farebbe un buon tutor seduto accanto a lui con la dispensa aperta. NON deve rileggere la dispensa: deve spiegarla.

## Materiale
- Dispensa: /tmp/cv/L<n>/dispensa.html. È la fonte principale ed è già verificata su slide e libro.
- Blocchi della dispensa come li vede il lettore: `cd /tmp/cv && python3 common/blocks.py L<n>`. Colonne: indice, tag, ancora (i primi 40 caratteri del blocco), resto del testo e, per le figure, il percorso del PNG.
- Slide e schede: /tmp/cv/L<n>/slides.py (contengono le correzioni agli errori delle slide). Libro: /tmp/cv/LIBRO.md. Usali solo per spiegare meglio, mai per aggiungere argomenti che la dispensa non tratta.

## Cosa produrre
`/tmp/cv/L<n>/copione.json`, in UTF-8:
```json
{"L": "L5", "segs": [
  {"a": "<ancora del blocco, copiata ESATTA dalla colonna 3 di blocks.py>", "t": "Testo parlato…"},
  …
]}
```
- Ogni segmento è legato al blocco di cui parla: mentre la voce lo legge, il lettore mostra la pagina con quel blocco e lo evidenzia. `a` va copiata carattere per carattere dall'output di blocks.py, spazi compresi. Le ancore sono uniche, ma se due blocchi avessero la stessa ancora aggiungi `"b": <indice>`.
- I segmenti seguono l'ordine dei blocchi; puoi tornare su un blocco precedente solo per un richiamo breve. Non serve un segmento per ogni blocco: i titoli h3 si coprono con il primo segmento della sezione (ancorato all'h3, che annuncia di cosa si parla e perché).
- Ogni segmento ha 1-5 frasi (circa 20-90 parole). Più segmenti sullo stesso blocco vanno bene, ad esempio per una figura importante.
- Lunghezza totale: 4000-6000 parole (circa 30-40 minuti a 1x).

## Come deve suonare
- È una lezione parlata in seconda persona, con un tono da tutor sveglio: "Partiamo da un problema concreto…", "Ora guarda la figura: la curva rossa…", "Qui c'è la trappola in cui cascano tutti…".
- Spiega il perché e collega i passaggi. Dove la dispensa è densa, rallenta e usa un'analogia o un esempio a voce. Dove la dispensa è già chiara, riassumi. Non ripetere frasi della dispensa parola per parola.
- **Figure:** guarda OGNI figura con Read prima di parlarne e dì cosa guardare: quale pannello, quale colore, cosa succede da sinistra a destra, quale numero leggere. Tutto deve essere vero rispetto all'immagine.
- **Formule:** dì cosa significano e leggile in parole. Se la formula è sullo schermo, puoi dire "nella formula che vedi" e poi spiegarla.
- Ogni sezione finisce con una frase "da portare a casa" collegata al riquadro Il punto.
- **"Guarda prima questi video":** basta un segmento che dica che i video sono un complemento, utili da vedere prima o dopo.
- **"Verifica di aver capito":** per ogni domanda, leggi la domanda, poi di' "metti in pausa e prova a rispondere", poi spiega la risposta.
- **"Come proseguire":** un segmento breve.
- Inizia con 2-3 frasi di aggancio: un problema reale e cosa saprai fare alla fine. Chiudi con un riassunto parlato di 4-6 frasi.

## Regole per la sintesi vocale (importante: il testo viene letto da una voce automatica e mostrato come sottotitolo)
- Niente simboli matematici o di codice nel testo. Scrivi in parole: "sigma al quadrato", "f di x", "x con pedice i", "la somma su k", "omega uguale a zero", "derivata parziale di I rispetto a x", "pi greco". Le lettere greche vanno scritte per esteso.
- Numeri semplici in cifre ("3 pixel", "1200 punti"). Frazioni e decimali in parole ("un quarto", "zero virgola cinque"). Niente "1/4", "x2", "≈", "→", "%" (scrivi "per cento").
- Niente parentesi, barre, virgolette tipografiche strane, elenchi puntati, markdown o HTML. Le frasi sono brevi, una virgola in più è meglio di una frase lunga.
- Niente abbreviazioni come "es.", "ecc." o "cfr.": scrivi "per esempio", "e così via".
- Termini inglesi tecnici: usali quando servono per l'esame (feature, kernel, matching, keypoint, aliasing, blur), ma introducili una volta con il corrispettivo italiano. Sigle come SIFT, RANSAC, CNN, DoG: alla prima occorrenza dì cosa significano ("DoG, cioè differenza di gaussiane").
- Non scrivere "slide N": Octech non vede le slide durante la videolezione. Puoi dire "come nelle slide del prof" quando serve, e segnalare a voce gli errori delle slide ("attenzione: nelle slide qui c'è un errore, il segno giusto è…").

## Correttezza
Tutto ciò che dici deve essere coerente con la dispensa. Se noti un errore nella dispensa, non correggerlo da solo: segnalalo nella risposta finale.

## Controllo
`cd /tmp/cv && python3 common/make_voce.py L<n>` deve stampare "ok L<n> …". Lo script risolve le ancore e controlla simboli vietati e lunghezze; correggi finché non dà ok. Non pubblicare nulla e non usare il tool Artifact. Non modificare dispensa.html, slides.py o i file in common/.

## Risposta finale (breve)
Numero di segmenti, numero di parole, durata stimata a 1x (parole / 150), figure commentate, eventuali errori trovati nella dispensa.
