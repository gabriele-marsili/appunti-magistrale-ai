# Aggiornamento automatico del sito di Computer Vision

Sito: https://claude.ai/artifact/8MHVhWfaz6Qc348RsB4vTk (index.html + lessons/L<n>.json come file pubblicati; slide HD per lezione come asset JSON, URL in site/hd.json). Capabilities del sito: db, user, assets (non passare `capabilities` quando ripubblichi, così restano).
Cartella del corso sul Mac: ~/Desktop/Everything/pisa/corsi/magistrale/secondo_anno/CV (in device_bash: $HOME/mnt/CV). Questa cartella: CV/_sito.

## Passi
0. Lavoro rimasto in sospeso: se esiste _sito/_da_pubblicare/LEGGIMI.md (non "LEGGIMI_pubblicato_*"), una esecuzione precedente ha preparato tutto ma non è riuscita a pubblicare. Per prima cosa completa quella pubblicazione seguendo il LEGGIMI (passi 7 e 8 con i file di quella cartella), poi rinomina LEGGIMI.md in LEGGIMI_pubblicato_<data>.md e prosegui col resto.
1. Controllo (sul Mac): `python3 $HOME/mnt/CV/_sito/common/check_new.py`. Lavoro da fare = file "nuovi" o "modificati" (ignora la chiave "altro") PIÙ le lezioni in "da_arricchire_col_libro" (lezioni già nel sito scritte solo dalle slide, da rifare integrando il libro: al massimo 2 per esecuzione, in ordine, dopo il materiale nuovo). Se non c'è nulla, fermati e rispondi in una riga.
   Prima di scrivere qualunque lezione leggi LIBRO.md: il libro è la fonte principale degli appunti.
2. Porta i sorgenti in cloud: sul Mac `cd $HOME/mnt/CV && tar czf _sito/_bundle.tgz --exclude _sito/_bundle.tgz _sito`, poi device_stage_files su quel file, estrai in /tmp/cv-pkg e crea la struttura di lavoro:
   /tmp/cv/common, /tmp/cv/L<n>, /tmp/cv/BRIEF.md, /tmp/cv/LIBRO.md, /tmp/cv/site/{lessons,hd.json} (build.py e shell.py usano questi percorsi fissi).
   Nota: build.py rigenera le miniature (_thumbs) dal PDF di quella lezione, quindi per ricostruire una lezione vecchia serve anche il suo PDF.
3. Stage in cloud dei file nuovi della lezione (PDF, notebook, eventuali appunti .md/.pdf già scritti da me). File di dati pesanti (cartelle data/, .npy, .gz) solo se servono per eseguire i notebook.
4. Scrivi la lezione in /tmp/cv/L<n>/ seguendo BRIEF.md, con lo stesso standard delle lezioni esistenti (leggi per esempio L6/slides.py). Lezione con PDF: una scheda per pagina. Lab senza slide: come L4 (una sezione per notebook, schede per blocco logico, figure di output come img, notebook eseguiti per cercare bug). Se nella cartella della lezione ci sono miei appunti già scritti (es. Appunti_L7_Lab.md), usali come fonte ma verifica tutto.
   Se un file è di una lezione già nel sito (modificato o aggiunto dopo), aggiorna quella lezione invece di crearne una nuova.
   Arricchimento di una lezione esistente: parti dai suoi slides.py/extra.html, rileggi il PDF e i capitoli del libro, aggiungi riquadri "Dal libro" e la sezione "Studia dal libro", correggi ciò che il libro smentisce. Non perdere il contenuto buono già presente.
5. `cd /tmp/cv && python3 common/build.py L<n>` (poi `python3 common/make_dispensa.py`, che rigenera site/lessons/dispensa.json con la Dispensa completa: va ripubblicato insieme alle lezioni) (per ogni lezione toccata; lo stile è cambiato, quindi ricostruisci pure tutte le lezioni che ripubblichi) e poi `python3 common/shell.py`.
6. Se la lezione ha un PDF: genera il pacchetto HD con la stessa logica di common/make_hd.py (pdftoppm 1800 px -> webp q78 -> JSON {id, slides:[data URI]}), caricalo come asset: Artifact publish con url del sito, asset:true, file_path del JSON (file sotto la working directory). Aggiungi "/_blob/<id>" a site/hd.json e rilancia shell.py.
7. Ripubblica. Octech ha autorizzato esplicitamente questa pubblicazione: il sito è un suo artifact privato e aggiornarlo è lo scopo del task.
   a. PRIMA di qualunque publish o upload di asset fai `Artifact action="read"` con l'url del sito: un publish verso un artifact che la sessione non ha letto viene rifiutato.
   b. Copia index.html e i lessons/L<n>.json nuovi o cambiati sotto la working directory (/home/claude/...: i file da pubblicare devono stare lì, non in /tmp) e chiama Artifact publish con url del sito, file_path = index.html, files = {"lessons/L<n>.json": ...} solo per le lezioni nuove o cambiate (i file non passati restano). Non passare capabilities.
   c. Se il publish viene rifiutato o bloccato: riprova una sola volta dopo aver rifatto la read. Se fallisce ancora, NON perdere il lavoro: salva sul Mac in _sito/_da_pubblicare index.html, hd.json, lessons/ cambiati e un LEGGIMI.md con l'elenco esatto dei passi mancanti (publish, copia in site/, comandi --segna e --arricchito), salva comunque i sorgenti delle lezioni (passo 8 senza --segna) e chiudi con un messaggio che inizia con "DA PUBBLICARE:" seguito dal motivo del rifiuto, così Octech può farlo pubblicare a mano o la prossima esecuzione lo riprende dal passo 0.
8. Salva indietro sul Mac: aggiorna _sito (dati lezione, site/lessons, site/hd.json, index.html) con un tar da cloud -> device_commit_files in CV/_sito/_ritorno.tgz -> estrai sul Mac sopra _sito. Poi `python3 $HOME/mnt/CV/_sito/common/check_new.py --segna L<n> ...` per le lezioni integrate e `--arricchito L<n> ...` per quelle rifatte col libro. Anche le lezioni nuove scritte già col libro vanno segnate --arricchito se erano nella lista.
9. Risposta finale breve: lezioni integrate, errori trovati nelle slide/notebook, cosa non è stato possibile fare.

## File temporanei
- Nella cartella di Octech usa sempre e solo questi nomi, sovrascrivendoli: _sito/_bundle.tgz (sorgenti verso il cloud), _sito/_lessons.tgz (PDF e notebook verso il cloud, se servono in blocco), _sito/_ritorno.tgz (dal cloud verso il Mac). Non creare altri archivi.
- Per device_commit_files dai al file in /mnt/user-data/outputs/ un nome NUOVO a ogni esecuzione (es. ritorno_<data-ora>.tgz): riusare un nome già committato può far arrivare sul Mac una versione vecchia. Il devicePath resta _sito/_ritorno.tgz (con force: true). Dopo il commit controlla sul Mac che la dimensione coincida prima di estrarre.
- Sul Mac `tar x` NON può sovrascrivere file esistenti (la cancellazione è disattivata): estrai gli archivi di ritorno con Python, aprendo ogni file in scrittura ('wb') sopra quello vecchio. Il commit accetta file fino a 20 MB: se serve, dividi in due archivi (_ritorno.tgz sorgenti, _ritorno2.tgz cartella site).
- Ogni lezione nuova ha anche la dispensa (dispensa.html, istruzioni in DISPENSA.md): è la parte più importante per Octech.
- Dopo la dispensa (e dopo build.py della lezione) scrivi anche il copione della videolezione: istruzioni in COPIONE.md, file L<n>/copione.json, controllo `python3 common/make_voce.py L<n>` che genera site/lessons/voce_L<n>.json. Ripubblica lessons/voce_L<n>.json insieme alla lezione (stesso publish, nei files). Se modifichi una dispensa esistente, rilancia make_voce.py su quella lezione: se un'ancora non si trova più, aggiorna il campo "a" del segmento con l'ancora nuova stampata da common/blocks.py.

## Regole
- Non ricreare mai un nuovo artifact: sempre update con url.
- Italiano con accenti, niente emoji.
- Se qualcosa manca (PDF illeggibile, computer non raggiungibile), non inventare contenuti: fermati e riportalo.

## Repo GitHub (gabriele-marsili/appunti-magistrale-ai)
Il materiale di CV va nel repo degli appunti della magistrale, in anno-2/computer-vision. Octech non tiene copie locali del repo: si pubblica con `magistrale/pubblica.py`, che legge CV/pubblica.json, clona il repo in una cartella temporanea, copia, committa, pusha e cancella la copia. Cosa finisce dove:
- Appunti/ -> Appunti/
- Lessons/ -> Lessons/ (solo Appunti_* e appunti_src/, niente PDF delle slide)
- _sito/ -> sito-src/ (sorgenti)
- _pubblica/sito/ -> sito/ (sito statico per GitHub Pages)
- _pubblica/dispensa/ -> dispensa/ (Markdown)
- _pubblica/README.md -> README.md
Dopo aver pubblicato l'artifact (passo 7), tieni aggiornata CV/_pubblica:
1. Nel cloud: `python3 common/make_gh.py /tmp/cv/gh_docs <cartella con i pacchetti HD nuovi, rinominati <L>.json>`, poi porta in CV/_pubblica/sito/ (con archivi da massimo 20 MB estratti con Python) index.html, i lessons/*.json cambiati e gli hd/<L>.json nuovi.
2. Rigenera la dispensa Markdown sul Mac, dalla cartella CV: `python3 _sito/common/make_md.py _sito _pubblica/dispensa` (servono pandoc e bs4; se mancano, salta il passo e scrivilo nel messaggio finale).
3. Pubblica su GitHub. Se $HOME/mnt/magistrale/pubblica.py esiste, cioè la cartella magistrale è collegata all'esecuzione, e accanto c'è il file .github-token, lancia `cd /tmp && python3 $HOME/mnt/magistrale/pubblica.py CV -m "CV: <cosa è cambiato, es. L10 Image Features>"`.
   - Lo script clona il repo in una cartella temporanea, copia secondo CV/pubblica.json, committa, pusha e cancella la copia. Non leggere, stampare o copiare il token: lo usa solo lo script.
   - Se stampa "Pubblicato: <commit>", nel messaggio finale scrivi "GitHub aggiornato (<commit>)".
   - Se il token manca, la cartella non è collegata o il push fallisce, NON riprovare in altri modi. Scrivi nel messaggio finale: "Da pubblicare su GitHub: python3 ~/Desktop/Everything/pisa/corsi/magistrale/pubblica.py CV", con il motivo.
   - Pubblica su GitHub solo dopo che l'artifact è stato pubblicato con successo, e solo se le dispense o i sorgenti sono cambiati.
