# Brief: appunti web per una lezione di Computer Vision (Unipi, magistrale AI, prof. Antonio Carta)

Stai producendo i dati di UNA lezione per una pagina web di studio. Lo studente incolla le slide su OneNote (una pagina per slide) e ci aggiunge sotto gli appunti: ogni "scheda" della pagina corrisponde a una slide, ha la miniatura della slide e un pulsante Copia che copia gli appunti formattati.

NON pubblicare nulla e non usare il tool Artifact: produci solo i file e verifica che la build funzioni. Chi ti ha incaricato assembla e pubblica.

## Riferimento obbligatorio
Leggi per intero `/tmp/cv/L6/slides.py`, `/tmp/cv/L6/extra.html`, `/tmp/cv/L6/meta.py`: sono la lezione 6 già fatta ed è lo standard di qualità, tono e formato da replicare. Guarda anche `/tmp/cv/common/build.py` e `/tmp/cv/common/style.css` per capire le classi disponibili.

## File da produrre nella tua cartella /tmp/cv/L<n>/
1. `meta.py` con: ID ('L<n>'), NUM, SHORT (2-4 parole, italiano, per il menu), DATE (es. '17 set'), H1 (titolo originale della lezione), EYEBROW ('Lezione n · Antonio Carta · <data estesa>'), INTRO (1-2 frasi: argomenti + "Una scheda per ogni slide del PDF (N pagine), poi guida allo studio..."), PDF (path del PDF o None), PRINTED_TOTAL (il totale stampato nel footer "x / T" delle slide).
2. `slides.py`: una chiamata `s(n, titolo, body_html, kind=None|'div', sec=None|(id, nome, 'slide a–b'), img=None, printed=None)` per OGNI pagina del PDF, nell'ordine, n = numero di pagina del PDF (1..N, nessuna mancante).
   - `sec=` sulla scheda che apre una sezione (di solito la slide divisoria), con id univoco prefissato dalla lezione (es. 'l5-gradienti').
   - `kind='div'` per slide divisorie/di sezione: body di una riga.
   - Numero stampato: la build mostra "pag. n-1/PRINTED_TOTAL" (copertina non numerata, divisorie senza numero). CONTROLLA sul PDF che la numerazione sia davvero così; se per quella lezione è diversa, passa `printed=' <em>· pag. X/T</em>'` o `printed=''` dove serve.
3. `extra.html`: sezioni finali in HTML come in L6: `<div class="sec" id="l<n>-guida"><h2>Guida allo studio</h2><span>…</span></div>` + `<div class="guide">` con card (blocchi di studio con tempi, domande tipo orale in `<details>` con traccia di risposta), ed eventuale sezione notebook. Immagini con `{{IMG:nomefile.png}}` (file nella tua cartella). NON chiudere div extra, NON mettere script.

## Ogni lezione ha anche una dispensa
Oltre alle schede, ogni lezione deve avere /tmp/cv/L<n>/dispensa.html: la spiegazione da zero della lezione con i video da guardare. Istruzioni complete in /tmp/cv/DISPENSA.md (in CV/_sito/DISPENSA.md). Octech non segue le lezioni: la dispensa è la parte più importante. Per i video di Shree Nayar gli ID verificati sono sulla pagina https://fpcv.cs.columbia.edu/ (leggila con WebFetch); YouTube spesso risponde 429, quindi verifica gli altri video con WebSearch.

## Il libro è la fonte principale
Le slide da sole non bastano per studiare: leggi e segui /tmp/cv/LIBRO.md (in CV/_sito/LIBRO.md). Per ogni lezione leggi i capitoli del libro corrispondenti PRIMA di scrivere, costruisci le spiegazioni sul libro e usa le slide come indice di cosa copre la lezione. Riquadri `box b` "Dal libro" nelle schede e sezione "Studia dal libro" in extra.html come descritto lì.

## Contenuto: regole
- Italiano corretto CON accenti (è, più, perché). Nessuna emoji. Formule in Unicode leggibile (σ, ∇, ∑, √, ≈, ×, ∗ per convoluzione) con `<sub>`/`<sup>`; formule importanti in `<span class="f">…</span>` su riga propria.
- Ogni scheda: cosa dice la slide, spiegato (non tradotto parola per parola), in elenchi brevi e grassetti sui termini chiave. Slide di sole figure: descrivi cosa mostra la figura e il punto che dimostra — per farlo GUARDA le slide (renderizza le pagine a immagine con pdftoppm e usa il tool Read sulle immagini, magari in montage 2x3 con `montage` per risparmiare letture). Non inventare il contenuto delle figure.
- Riquadri: `<div class="box k"><b>Da saper fare</b>…</div>` (conti, derivazioni, cose da orale), `<div class="box x"><b>Approfondimento</b>…</div>` (oltre le slide, facoltativo), `<div class="box w"><b>Attenzione: …</b>…</div>` SOLO per errori reali o imprecisioni nelle slide, con la versione corretta. Verifica le formule delle slide: in L6 c'erano errori veri (σ che si sommano invece delle varianze, PDE scritta male). Sii rigoroso ma non inventare errori: segnala solo ciò di cui sei sicuro.
- Collegamenti fra lezioni quando utili (L2 formazione immagine, L3 Fourier e convoluzione, L4 lab FFT, L5 filtri e gradienti, L6 aliasing e piramidi, L7 feature/SIFT).
- HTML valido: chiudi i tag, escape di `<`, `>` e `&` nel testo (&lt; &gt; &amp;). Dentro le stringhe Python triple-quoted evita `"""` e backslash non voluti.

## Build e controllo
`cd /tmp/cv && python3 common/build.py L<n>` deve stampare "ok L<n> N schede …" con N = numero di pagine del PDF. Poi controlla l'HTML generato con un parser (es. `python3 -c` con html.parser o lxml) per tag non chiusi nei body. Non fare screenshot della pagina.

## Risposta finale
Breve: numero di schede, errori delle slide segnalati (slide + problema in una riga ciascuno), eventuali bug nei notebook, qualunque dubbio.
