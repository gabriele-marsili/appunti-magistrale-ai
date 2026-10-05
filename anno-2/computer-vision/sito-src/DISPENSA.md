**Standard attuale (dal 4 ottobre): segui /tmp/cv/RISCRITTURA.md (in CV/_sito/RISCRITTURA.md) per struttura per sezione, 12-20 figure ed evidenziature automatiche `<mark class="sh sh-y|p|g|b">` (giallo concetti chiave, rosa problemi, verde proprietà, blu definizioni). Le regole qui sotto valgono dove non contraddicono RISCRITTURA.md.**

# Dispensa di una lezione: istruzioni

## Per chi è
Octech, studente della magistrale in AI a Pisa (triennale in informatica: conosce algebra lineare, analisi di base, probabilità, Python/numpy). Non segue le lezioni e dalle slide non ha capito praticamente nulla: le slide riprendono il libro in modo frammentario e con errori. La dispensa deve permettergli di capire la lezione DA ZERO senza aver visto la lezione, e poi usare le schede slide per slide (già sul sito, sotto la dispensa) come ripasso.

## Cosa produrre
File `/tmp/cv/L<n>/dispensa.html` (frammento HTML, niente script, niente stili inline salvo eccezioni) e, se servono, figure `/tmp/cv/L<n>/disp_*.png` generate da te con matplotlib/numpy (richiamate con `{{IMG:disp_nome.png}}`).
Struttura obbligatoria:

```html
<div class="sec" id="l<n>-dispensa"><h2>Dispensa</h2><span>parti da qui · circa NN minuti</span></div>
<div class="disp">
  <p><b>In una frase:</b> …</p>
  <h3>Prima di iniziare</h3>   <!-- prerequisiti, con link alle lezioni precedenti: <a href="#L3">L3</a> -->
  <h3>Guarda prima questi video</h3>
  <div class="watch">
    <a href="URL"><span class="k">Video · 14 min</span><b>Titolo esatto</b><span class="d">Autore. Cosa guardare e perché.</span></a>
    …
  </div>
  <h3>…sezioni della spiegazione…</h3>
  …
  <h3>Il riassunto in 10 righe</h3>
  <h3>Verifica di aver capito</h3>   <!-- 4-6 domande, risposta in <details><summary>…</summary><p>…</p></details> -->
  <h3>Come proseguire</h3>   <!-- capitoli del libro con link, poi "ora ripassa con le schede qui sotto" -->
</div>
```

## La spiegazione
- Costruita sul libro (vedi /tmp/cv/LIBRO.md): leggi davvero i capitoli con WebFetch. Le slide (PDF della lezione) servono a sapere quali argomenti coprire: copri tutto ciò che c'è nelle slide, nell'ordine più chiaro per capire (che può essere diverso da quello delle slide).
- Parti dal problema concreto (perché ci serve questa cosa), poi l'intuizione, poi la matematica, poi un esempio numerico svolto passo passo, poi cosa succede in pratica (codice numpy breve quando aiuta, in `<pre>`).
- Ogni formula introdotta va spiegata simbolo per simbolo la prima volta. Formule importanti in `<span class="f">…</span>`; Unicode con <sub>/<sup>.
- 1-3 figure generate da te dove un'immagine vale più del testo (es. spettro di un segnale, aliasing di una sinusoide, una piramide, una proiezione prospettica, un'omografia applicata a un quadrato). Controllale guardandole prima di includerle.
- Rimanda alle schede con il numero di slide ("vedi slide 23 qui sotto") e alle correzioni già segnalate nelle schede quando la slide sbaglia.
- Lunghezza: 2500-4500 parole. Italiano corretto con accenti, tono da buon tutor: chiaro, diretto, niente frasi riempitive, niente emoji.
- Copyright: spiegazioni tue, mai paragrafi del libro copiati; citazioni solo di una frase, virgolettate.

## I video
- 2-4 video per lezione, i più chiari per QUESTI argomenti, in ordine di visione. Priorità: Shree Nayar "First Principles of Computer Vision" (YouTube, Columbia), 3Blue1Brown (convoluzione, Fourier), Cyrill Stachniss (camera, omografie, RANSAC, feature), Steve Brunton (Fourier), Computerphile, lezioni universitarie (MIT, Stanford CS231n, Michigan EECS 498) per la parte deep.
- SOLO link verificati: trova ogni video con WebSearch e usa l'URL esatto restituito (youtube.com/watch?v=… specifico, non playlist generiche se non necessario). Se possibile apri la pagina con WebFetch per confermare titolo e durata; se la durata non è verificabile scrivi solo "Video". Mai inventare un URL o un ID.
- Nel testo `d` scrivi cosa guardare (tutto, o i minuti utili) e cosa ti serve capire.

## Build e controllo
`cd /tmp/cv && python3 common/build.py L<n>` deve stampare "ok L<n> …". Controlla con html.parser che il frammento non abbia tag non chiusi. Non pubblicare nulla, non usare il tool Artifact.

## Risposta finale
Breve: parole circa, sezioni, video inclusi (titolo + URL), figure create, eventuali dubbi.
