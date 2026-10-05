# Computer Vision

Laurea magistrale in Informatica, percorso AI, Università di Pisa. Secondo anno. Docente: Antonio Carta.

Sito di studio con schede slide per slide, dispensa riscritta da zero per ogni lezione, videolezioni e appunti delle lezioni e dei laboratori.

## Link

- [Sito di studio](https://gabriele-marsili.github.io/appunti-magistrale-ai/anno-2/computer-vision/sito/): schede, presentazione, dispense e videolezioni
- [Dispensa in Markdown](dispensa/), leggibile direttamente su GitHub
- [Notebook OneNote](https://unipiit-my.sharepoint.com/:o:/g/personal/g_marsili9_studenti_unipi_it/IgDWol7jc4l5RIA-8VteYMszAfTN1MWETf97Qt0gV5EWWfs)

## Sito

Sito statico con le lezioni 1-9 (7 di teoria e 2 laboratori):

- **Schede:** ogni slide ha la sua scheda, nello stesso ordine del PDF, con riquadri "Dal libro" (Torralba, Isola, Freeman, *Foundations of Computer Vision*) e riquadri "Attenzione" sugli errori verificati nelle slide.
- **Presentazione:** slide in HD con gli appunti accanto, penna, evidenziatore e sottolineatura.
- **Dispensa per lezione:** spiega da zero, sezione per sezione: problema, idea, figura, matematica, esempio svolto. Ha circa 20 figure per lezione, evidenziature a colori (giallo concetti chiave, rosa problemi e trappole, verde proprietà, blu definizioni), video consigliati e domande di verifica con risposta. C'è anche la Dispensa completa, impaginata a schermo intero e annotabile.
- **Videolezioni:** la sintesi vocale del dispositivo legge un copione parlato che spiega la dispensa pagina per pagina, con sottotitoli. Si può scegliere la velocità da 0,5x a 2x, usare capitoli e barra di avanzamento, e partire da qualunque punto. Durano circa 40 minuti per lezione a 1x.

Le annotazioni restano salvate nel browser.

## Contenuto della cartella

- `sito/`: il sito pubblicato con GitHub Pages (`index.html`; lezioni, dispense e copioni in `lessons/`; slide HD in `hd/`)
- `sito-src/`: sorgenti del sito. Per ogni lezione: schede (`L<n>/slides.py`), dispensa (`L<n>/dispensa.html`), copione della videolezione (`L<n>/copione.json`) e figure. In `common/` ci sono gli script di build e le istruzioni
- `dispensa/`: la dispensa in Markdown, con le figure prese da `sito-src/`
- `Appunti/`: appunti delle lezioni 1-7
- `Lessons/`: appunti dei laboratori 4 e 7, con sorgenti LaTeX

Appunti personali: possono contenere errori. Il sito include le slide del corso (© Antonio Carta, Università di Pisa) per lo studio; i libri non sono inclusi.
