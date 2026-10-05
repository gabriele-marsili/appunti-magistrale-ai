# Riscrittura della dispensa di una lezione (versione 2)

## Il problema
Octech (magistrale AI a Pisa, triennale in informatica) sta leggendo le dispense del sito ma "per buona parte dei concetti non ci capisce niente" e "mancano molte immagini". Non segue le lezioni. La dispensa deve permettergli di LEGGERE E BASTA e capire: chiara, concisa, interessante, fedele a slide e libro. È la cosa più importante del sito.

## Cosa hai a disposizione
- Dispensa attuale: /tmp/cv/L<n>/dispensa.html (versione 1, backup in /tmp/cv/backup_v1/L<n>/). Ha già contenuto corretto e verificato, video e figure (/tmp/cv/L<n>/disp_*.png): riusa tutto ciò che è buono.
- Slide: PDF indicato in /tmp/cv/L<n>/meta.py (PDF=...; None per i lab, che hanno i notebook). Schede slide per slide: /tmp/cv/L<n>/slides.py (contengono anche le correzioni agli errori delle slide).
- Libro: /tmp/cv/LIBRO.md dice quali capitoli del visionbook (https://visionbook.mit.edu/) usare. Leggili con WebFetch.
- Evidenziature fatte da Octech su questa lezione (solo L1-L6): /tmp/cv/user_hl/L<n>.json, lista di {page, c, text}. c: y giallo, p rosa, g verde, b blu. I testi sono frammenti presi dalla versione 1 (possono essere tagliati a metà parola).

## Cosa produrre
Riscrivi /tmp/cv/L<n>/dispensa.html (stesso schema di base: `<div class="sec" id="l<n>-dispensa"><h2>Dispensa</h2><span>parti da qui · circa NN minuti</span></div>` seguito da UN `<div class="disp">…</div>` che contiene tutto; niente script, niente stili inline).

### Come scrivere perché si capisca
- Prima di scrivere, rileggi le slide e i capitoli del libro e fai l'elenco dei concetti della lezione: devono esserci TUTTI, nell'ordine che rende più facile capire.
- Ogni sezione (`<h3>`) segue questo schema: **il problema** (perché ci serve, con un esempio concreto o una domanda), **l'idea** (intuizione in parole semplici, un'analogia se aiuta), **la figura** che la mostra, **la matematica** (solo quella necessaria; ogni simbolo spiegato la prima volta; cosa "dice" la formula a parole), **un esempio svolto piccolo** con numeri veri, e in fondo un riquadro `<div class="box k"><b>Il punto</b><p>…</p></div>` di 1-3 frasi.
- Frasi brevi, un'idea per paragrafo, niente gergo non spiegato, niente giri di parole. Se un concetto dipende da una lezione precedente, richiamalo in una frase con link (`<a href="#L3">L3</a>`).
- Concisa non vuol dire povera: taglia ripetizioni e digressioni, non le spiegazioni. Obiettivo 3500-5500 parole.
- Rendila interessante: parti da esempi reali (foto, telefono, panorami, auto a guida autonoma, Instagram), mostra cosa va storto se non si fa nel modo giusto.
- Mantieni (aggiornandoli se serve): "In una frase", "Prima di iniziare", "Guarda prima questi video" (gli stessi video già verificati, non aggiungerne di non verificati), "Il riassunto in 10 righe", "Verifica di aver capito" con risposte in `<details>`, "Come proseguire". Mantieni i rimandi alle correzioni delle slide (riquadri Attenzione delle schede).

### Immagini: molte di più
- Obiettivo: una figura per ogni concetto che si capisce meglio vedendolo, in pratica 12-20 figure. Riusa le disp_*.png esistenti che vanno bene e creane di nuove in /tmp/cv/L<n>/disp2_<nome>.png (mai sovrascrivere file esistenti).
- Tipi: grafici e schemi con matplotlib/numpy (sfondo bianco, testo grande e leggibile anche da telefono, max 1400 px di larghezza, assi e titoli in italiano, colori #1565C0 #C62828 #2E7D32 #EF6C00), ritagli delle slide quando la slide ha già il disegno giusto (pdftoppm -r 150, ritaglio con PIL, didascalia "Dalla slide N"), passo-passo (sequenze di pannelli che mostrano un algoritmo che procede).
- Formato: `<figure><img src="{{IMG:disp2_nome.png}}" alt="…"><figcaption>Cosa guardare, 1-2 frasi.</figcaption></figure>`.
- GUARDA ogni figura con Read prima di inserirla; numeri coerenti col testo.
- Lavora in /tmp/cv/figwork2/L<n>/ (mai nello scratchpad condiviso).

### Evidenziature automatiche nello stile di Octech
Evidenzia tu il testo con `<mark class="sh sh-X">…</mark>`, dove X è:
- `y` giallo: concetti chiave e frasi da ricordare in generale;
- `p` rosa: cose "cattive": problemi, limiti, errori tipici, trappole, cosa va storto (aliasing, rumore amplificato, ringing…);
- `g` verde: cose "buone": proprietà, vantaggi, garanzie, cosa funziona (separabile, invertibile, lineare…);
- `b` blu: definizioni e cose particolarmente importanti (il termine definito e la sua definizione, la formula centrale della lezione).
Densità: circa il 10-15% del testo, mai paragrafi interi, mai dentro `<pre>`, titoli o didascalie. Le formule centrali in `<span class="f">` possono avere il blu sull'intera formula (`<mark class="sh sh-b">` intorno al contenuto della span).

### Conservare le evidenziature di Octech
Il file /tmp/cv/user_hl/L<n>.json dice cosa Octech ha già evidenziato e con che colore: è sia il suo stile da imitare sia il suo lavoro da conservare.
- Ogni concetto che ha evidenziato deve restare nella nuova dispensa, con una frase che lo esprime (se possibile la stessa, ripulita) evidenziata con lo STESSO colore che ha usato lui.
- Le sue scelte di colore prevalgono sulle tue regole se diverse.
- Alla fine controlla la copertura: per ogni sua evidenziatura (scarta i frammenti di 1-2 parole senza senso) verifica che nella nuova dispensa ci sia un `<mark class="sh sh-<stesso colore>">` con quel contenuto o equivalente. Riporta la percentuale coperta nella risposta.

## Build e controllo
`cd /tmp/cv && python3 common/build.py L<n>` deve dare "ok". Controlla l'HTML con html.parser (tag bilanciati, nessun `{{IMG` rimasto nel JSON in /tmp/cv/site/lessons/L<n>.json). Non pubblicare, non usare il tool Artifact.

## Risposta finale (breve)
Parole, sezioni, figure nuove (nome + cosa mostra), numero di evidenziature per colore, copertura delle evidenziature di Octech (%), dubbi.
