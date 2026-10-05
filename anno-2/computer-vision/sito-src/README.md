# Sito appunti Computer Vision - come aggiornarlo

Pagina pubblicata: https://claude.ai/artifact/8MHVhWfaz6Qc348RsB4vTk (artifact multi-file: index.html + lessons/L<n>.json)

Struttura sorgenti (in questo progetto, cartella sito/):
- common/: build.py (lezione -> lessons/L<n>.json), shell.py (index.html con indice e menu), style.css, copy.js, howto.html, BRIEF.md (istruzioni per scrivere una lezione)
- L<n>/: meta.py, slides.py, extra.html per ogni lezione. Le immagini (L4/img, L6/blend.png, L6/lap.png) non sono qui: si recuperano dall'artifact pubblicato o si rigenerano.

Per aggiungere una lezione nuova:
1. ricreare /tmp/cv/common e /tmp/cv/L<k> dai file del progetto; recuperare i lessons/*.json esistenti leggendo l'artifact (Artifact read con path lessons/L<k>.json) in /tmp/cv/site/lessons/
2. scrivere /tmp/cv/L<n>/ seguendo BRIEF.md (PDF della lezione nella cartella CV/Lessons del Mac)
3. python3 common/build.py L<n>; python3 common/shell.py
4. ripubblicare index.html sullo stesso URL passando url + files con tutti i lessons/*.json

## Presentazione e annotazioni (dal 25 settembre)
- Capabilities dell'artifact: db, user, assets. Le annotazioni (penna, evidenziatore, sottolinea) sono salvate per utente nel db, collezione data/users/<id>, documento "<L>-s<n>" con {lesson, n, strokes, updated}; copia anche in localStorage.
- Slide ad alta risoluzione: un JSON per lezione ({id, slides:[data URI webp 1800px]}) generato da common/make_hd.py e caricato come ASSET dell'artifact (Artifact publish con url + asset:true + file_path, una chiamata per file). Gli URL /_blob/<id> vanno in sito/hd.json, che shell.py incorpora nella pagina.
- Nuova lezione: build.py -> shell.py -> ripubblica index.html con files lessons/*.json (tutti) -> make_hd per il PDF nuovo -> carica l'asset -> aggiorna hd.json -> shell.py -> ripubblica.
