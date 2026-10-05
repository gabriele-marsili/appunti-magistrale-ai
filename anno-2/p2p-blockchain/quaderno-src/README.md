# Sorgenti del Quaderno

Script e template che generano il sito in `../quaderno/`.

| File | A cosa serve |
|---|---|
| `template.html` | la pagina: indice, lezioni, presentazione con annotazioni, Ripasso esame |
| `build.py` | genera il sito dalle lezioni; `--public` produce la versione senza PDF delle slide |
| `validate.py` | controlla il JSON di una lezione (una scheda per pagina, accenti, riquadri, correzioni) |
| `SCHEMA.md` | formato del JSON di una lezione e regole di scrittura |
| `compress.sh` | ricomprime i PDF delle slide (solo per la versione privata) |
| `meta.json` | data, titolo, docente e numero di pagine di ogni lezione |

Le lezioni sono in `../quaderno/lessons/` (JSON compatto, una per file). Per rigenerare il sito: mettile in `sito/lessons/` accanto a questi file e lancia `python3 sito/build.py --public`. La versione pubblica non usa i PDF, ma `build.py` legge il rapporto d'aspetto delle pagine dai PDF in `pdf/`; senza PDF basta lasciare il campo `ratio` già presente nei JSON.

Librerie incluse in `../quaderno/vendor/`: pdf.js 3.11.174 (Apache-2.0), MathJax 3.2.2 (Apache-2.0), highlight.js 11.9.0 (BSD-3-Clause).
