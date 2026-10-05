# Aggiungere immagini a una dispensa

La dispensa /tmp/cv/L<n>/dispensa.html ha solo 3 figure su ~5000 parole: troppo poche per uno studente che non ha seguito la lezione. Il tuo compito è aggiungerne altre dove un'immagine fa capire meglio del testo, SENZA riscrivere il testo (al massimo ritocchi una frase per richiamare la figura: "come si vede nella figura qui sotto").

## Cosa fare
1. Leggi tutta la dispensa e individua i punti in cui manca un'immagine che servirebbe davvero: un concetto geometrico, un grafico di una funzione o di uno spettro, un confronto prima/dopo, uno schema di una pipeline, un esempio numerico che si capisce meglio disegnato. Obiettivo: 4-6 figure nuove (totale 7-9), circa una per sezione importante, nessuna decorativa.
2. Due tipi di figure ammessi:
   - generate da te con matplotlib/numpy (diagrammi, grafici, esempi sintetici, schemi);
   - ritagli di figure dalle slide della lezione (PDF in meta.py, variabile PDF; renderizza con `pdftoppm -r 150 -f N -l N -png`, ritaglia con PIL solo la parte utile, didascalia "Dalla slide N"). Usali quando la slide ha già il disegno giusto (es. una foto di esempio, un risultato).
3. Stile delle figure generate: sfondo bianco, testo leggibile anche su telefono (font ≥ 12 pt con figsize tipo (8, 4.5) e dpi 150, non più larghe di 1400 px), colori distinguibili (es. #1565C0 blu, #C62828 rosso, #2E7D32 verde, #EF6C00 arancio, grigi per il contesto), assi e titoli in italiano, niente titoli ridondanti con la didascalia. Una figura con più pannelli va bene se ognuno resta leggibile a 360 px di larghezza: preferisci al massimo 2-3 pannelli affiancati.
4. Salva in /tmp/cv/L<n>/disp_<nome>.png (non sovrascrivere file esistenti) e inserisci nel punto giusto:
   `<figure><img src="{{IMG:disp_<nome>.png}}" alt="descrizione di cosa mostra"><figcaption>Cosa guardare nella figura, in una o due frasi.</figcaption></figure>`
5. GUARDA ogni figura (tool Read sull'immagine) prima di inserirla e correggila se è illeggibile, sbagliata o confusa. Controlla i numeri con il testo: la figura deve dire la stessa cosa della dispensa.
6. Lavora in una tua cartella di appoggio /tmp/cv/figwork/L<n>/ (script ecc.), mai nello scratchpad condiviso.
7. Build: `cd /tmp/cv && python3 common/build.py L<n>` deve dare "ok". Controlla l'HTML con html.parser.

Non pubblicare nulla, non usare il tool Artifact.

Risposta finale breve: figure aggiunte (nome, sezione, cosa mostrano), dubbi.
