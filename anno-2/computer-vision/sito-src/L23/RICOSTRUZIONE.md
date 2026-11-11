# Sorgenti L23 ricostruiti (11/11/2026)

L'esecuzione del 10/11 ha integrato e pubblicato la L23 sul sito, ma il Mac si è disconnesso prima del ritorno dei sorgenti.
L'esecuzione dell'11/11 li ha ricostruiti invertendo build.py sul file pubblicato lessons/L23.json:
- meta.py, slides.py (25 schede), dispensa.html, extra.html, copione.json: testo identico al pubblicato (verificato ricostruendo con build.py e make_voce.py: html uguale a meno della codifica delle immagini, voce_L23.json identico byte per byte);
- immagini in img/: estratte dal sito; quelle che erano in WebP sono state riconvertite in PNG (qualità del WebP pubblicato, non l'originale).
Mancano solo le note di lavoro (NOTE_LIBRO.md) e gli script di verifica dei notebook di quella esecuzione. Numeri misurati: SimSiam 1 epoca su CPU, loss −0,364, 1540 s; probe test 37,99%, k-NN 37,40%; ResNet-18 casuale 32,98% / 32,87%.
