# Computer Vision, Lezione 4 (laboratorio)

Signal processing con audio, classificazione spettrale, convoluzione 2D.
Materiale: 3 notebook in `lab/` (file datati 21/09/2026).

## Indice

1. [Panoramica](#1-panoramica)
2. [demo.ipynb: audio, FFT, filtri, convoluzione 1D](#2-demoipynb-audio-fft-filtri-convoluzione-1d)
3. [classification.ipynb: cifre parlate con feature spettrali](#3-classificationipynb-cifre-parlate-con-feature-spettrali)
4. [15lif.ipynb: convoluzione, cross-correlazione, template matching](#4-15lifipynb-convoluzione-cross-correlazione-template-matching)
5. [Errori e imprecisioni nei notebook](#5-errori-e-imprecisioni-nei-notebook)
6. [Domande tipo esame](#6-domande-tipo-esame)
7. [Stato della verifica e come rieseguire](#7-stato-della-verifica-e-come-rieseguire)

## 1. Panoramica

| Notebook | Tema | Ordine |
|---|---|---|
| `demo.ipynb` | audio, FFT, filtri in frequenza, convoluzione 1D | 1 |
| `classification.ipynb` | feature spettrali + k-NN sulle cifre parlate | 2 |
| `15lif.ipynb` | convoluzione e cross-correlazione a mano, template matching (cap. 15 del visionbook) | 3 |

Collegamenti con le altre lezioni (file in `../../Appunti/`):

- `CV_L3_Signal_Processing_appunti.txt`: convoluzione (slide 14-31), cross-correlazione vs convoluzione (28), bordi (27), teorema di convoluzione (63-66).
- `CV_L6_Aliasing_Scale_Invariance_appunti.txt`: limite di Nyquist e aliasing.

Nei notebook sono state aggiunte celle markdown che iniziano con **[Appunti L4]** (celle originali non modificate).

Convenzioni: `*` = convoluzione, SR = frequenza di campionamento, H(f) = risposta in frequenza di un kernel, f in cicli/campione salvo dove scritto Hz.

## 2. `demo.ipynb`: audio, FFT, filtri, convoluzione 1D

### 2.1 Segnale di partenza

- Accordo di La minore: sinusoidi a 220 (A3), 261.63 (C4), 329.63 (E4) Hz più rumore a banda larga.
- SR = 22050 Hz, durata 2 s, 44100 campioni.

### 2.2 FFT con `np.fft.rfft`

| Cosa | Valore / formula |
|---|---|
| Uscita di `rfft` su N campioni reali | N/2 + 1 valori (qui 22051) |
| Asse in Hz | `np.fft.rfftfreq(n, d=1/SR)` |
| Risoluzione in frequenza | SR/N = 1/durata = 0.5 Hz per bin |
| Ultimo bin | SR/2 = 11025 Hz (Nyquist) |

- Per distinguere frequenze vicine serve più durata, non più SR.
- Scala log: mostra il rumore di fondo e picchi di ordini di grandezza diversi. Per le immagini si userà quasi sempre.

### 2.3 Filtro in frequenza (`freq_filter`)

Tre passi: `rfft`, moltiplicazione per una maschera 0/1, `irfft`.

| Filtro | Parametri | Cosa resta |
|---|---|---|
| Passa-basso | taglio 240 Hz | solo A3 (220 Hz) |
| Passa-alto | taglio 300 Hz | E4 (329.63) più rumore |
| Passa-banda | 245-280 Hz | solo C4 (261.63) |

- Una maschera 0/1 è un filtro ideale a taglio netto. Nel tempo corrisponde a una sinc che oscilla (ringing).
- Nell'audio reale non si fa fft, filtro, ifft, per vincoli di tempo reale (dal testo del notebook).

### 2.4 Separare due segnali

- Accordo (sotto 400 Hz) più melodia (D5 587.33, E5 659.25 Hz, sopra 500 Hz).
- Passa-basso a 400 e passa-alto a 500 li separano perché le bande non si sovrappongono.
- Il rumore dell'accordo è a banda larga: una parte finisce anche nella melodia recuperata.
- Con strumenti veri (armoniche sovrapposte) la separazione è imperfetta.

### 2.5 Convoluzione 1D con `np.convolve`

Lunghezze con segnale 60 e kernel 7 (output stampato):

| `mode` | Lunghezza | Formula |
|---|---|---|
| `full` | 66 | N + K - 1 |
| `same` | 60 | N |
| `valid` | 54 | N - K + 1 |

Tre kernel fondamentali:

| Kernel | Nel tempo | In frequenza |
|---|---|---|
| Box (media su 7 campioni) | sfoca | passa-basso con lobi laterali (ringing) |
| Gaussiana (15 campioni, std 2.5) | sfocatura morbida | passa-basso pulito |
| Derivata `[-1, 0, 1]/2` | evidenzia i bordi, amplifica il rumore | vedi 5.2 |

Teorema di convoluzione: `F{x * h} = F{x} . F{h}`. La FFT del kernel è la sua risposta in frequenza: dice quali frequenze passano.

Valore di |H| a Nyquist (0.5), normalizzato a DC = 1 (calcolato):

| Kernel | \|H(0.5)\| |
|---|---|
| Box | 0.143 |
| Gaussiana | 0.0015 |
| Derivata | 0.0000 |

## 3. `classification.ipynb`: cifre parlate con feature spettrali

Idea: parole diverse hanno vocali e consonanti diverse, separabili in frequenza. Anche una rete convoluzionale per audio fa analisi in frequenza (teorema di convoluzione).

### 3.1 Dati

- Free Spoken Digit Dataset: 3000 WAV, 10 cifre x 6 parlanti x 50 ripetizioni, 8 kHz.
- Da scaricare da GitHub (`Jakobovski/free-spoken-digit-dataset`) in `Lessons/L4/data/free-spoken-digit-dataset-master/recordings`. **Non è presente** nella cartella del corso.
- Ogni clip è portata a 8000 campioni (1 s): zeri aggiunti o taglio. FFT di 8000 campioni = 4001 bin.

### 3.2 Feature spettrali

| Feature | Definizione |
|---|---|
| Centroide | media delle frequenze pesata con la magnitudo |
| Rolloff (85%) | frequenza sotto cui sta l'85% della somma cumulata (vedi 5.3) |
| ZCR | frazione di coppie di campioni consecutivi che cambiano segno |

Intervalli osservati: centroide 572-2218 Hz, rolloff 717-3669 Hz, ZCR 0.014-0.425.

### 3.3 k-NN (k = 5) con split casuale 80/20

Feature normalizzate (media 0, deviazione 1) perché la distanza è euclidea.

| Feature | Train | Test |
|---|---|---|
| 3 feature | 63.8% | 49.8% |
| 3 feature + log-spettro | 92.9% | 88.0% |

Caso = 10%. Numeri dagli output salvati.

- Log-spettro = `np.log(|FFT| + 1)`: il +1 evita -inf dove la magnitudo è circa 0.
- Le 3 feature sono 3 colonne su 4004: dopo la normalizzazione pesano come ogni altra colonna.
- Difetto lieve: normalizzazione calcolata su tutto il dataset prima dello split (vedi 5.4).

### 3.4 Parlante escluso (leave-one-speaker-out)

È il punto principale del notebook. Accuratezza media dagli output salvati:

| Feature | Split casuale | Parlante escluso |
|---|---|---|
| 3 feature | 49.7% | 28.7% |
| 3 feature + log-spettro | 88.2% | 32.2% |

- Lo split casuale è ingannevole: per ogni clip di test ci sono decine di clip della stessa persona e stessa cifra nel train.
- Spiegazione suggerita dal notebook (non verificata da me): lo spettro di tutta la clip contiene anche voce, volume, microfono e stanza. Il k-NN li sfrutta finché il parlante è nel train.
- I valori per singolo parlante sono solo nel grafico, non stampati.

### 3.5 Esercizio: generalizzare a parlanti nuovi

Obiettivo dichiarato: circa 60% sul parlante escluso usando solo NumPy. Hint del notebook, in ordine:

1. Togliere il volume: un guadagno moltiplica lo spettro, dopo il log diventa una costante additiva. Si sottrae la media del log-spettro.
2. Poche decine di bande larghe, più fitte alle basse frequenze, al posto dei 4001 bin (media della potenza per banda).
3. Tagliare il silenzio, dividere la parte parlata in pochi pezzi consecutivi e calcolare le bande per ogni pezzo (conserva l'ordine dei suoni).

Gli MFCC sono la versione standard di queste idee. Non implementato né provato (dataset assente).

## 4. `15lif.ipynb`: convoluzione, cross-correlazione, template matching

### 4.1 Convoluzione e cross-correlazione 1D

Esempio: `l = [1,2,3,4]`, `h = [-1,-2,-3]`.

| Operazione | Formula | Uscita | Risultato |
|---|---|---|---|
| Convoluzione | `out[n] = sum_k l[k] * h[n-k]` | len(l) + len(h) - 1 = 6 | `[-1 -4 -10 -16 -17 -12]` |
| Cross-correlazione | `out[n] = sum_k h[k] * l[n+k]` | len(l) = 4 | `[-14 -20 -11 -4]` |

- La convoluzione coincide con `np.convolve` (verificato).
- I primi due valori della cross-correlazione coincidono con `np.correlate(l, h, 'valid')` = `[-14 -20]` (verificato). Gli ultimi due sono i bordi con zero padding.
- Nella cross-correlazione il kernel non è ribaltato ed è agganciato al suo primo elemento (nel codice: `TODO: boundary`).
- Convoluzione = cross-correlazione con kernel ribaltato.

### 4.2 Versioni 2D

- Convoluzione: uscita (H+h-1) x (W+w-1).
- Cross-correlazione: uscita H x W, kernel agganciato all'angolo in alto a sinistra.
- Quattro cicli annidati: leggibili ma lente.

### 4.3 Risposta a un impulso (verificato eseguendo le funzioni)

Impulso in (10,10):

- convoluzione: copia del kernel, non ribaltato, con angolo in alto a sinistra in (10,10);
- cross-correlazione: kernel ribaltato di 180 gradi, righe 8-10, colonne 6-10.

### 4.4 Template matching

Pattern: triangolo 3x5. Immagine con due triangoli giusti in (10,10) e (15,20) e uno capovolto in (5,20).

| Metodo | (10,10) | (15,20) | capovolto (5,20) | rettangolo pieno (23,5) |
|---|---|---|---|---|
| Cross-correlazione semplice | 9 | 9 | 5 | 9 |
| `template_matching` (normalizzato) | 15.00 | 15.00 | -1.67 | 0.00 |

- Il picco sta sull'angolo in alto a sinistra del pattern perché il kernel è agganciato lì.
- Convoluzione: massimo 9 in (7,24), cioè sul triangolo capovolto, con indice spostato di (2,4) = dimensioni del kernel meno 1. Trova il pattern ribaltato, quindi per cercare un pattern serve la cross-correlazione.
- Problema della cross-correlazione semplice: non è normalizzata, un rettangolo luminoso dà lo stesso 9 del pattern vero (falso positivo).
- `template_matching` corregge con due passi:
  1. kernel con media 0 e deviazione 1, quindi una zona uniforme dà 0 qualunque sia la luminosità;
  2. risposta divisa per la deviazione standard del pezzo di immagine sotto il kernel (contrasto).
- Limiti (dal notebook): niente scala, rotazione, illuminazione non uniforme, variazioni tra istanze. Ai bordi il pezzo è troncato (`TODO: boundary?`).

### 4.5 Esercizi proposti

- Padding e condizioni al contorno diverse (es. circolare con `np.pad(..., mode='wrap')`).
- Riconoscere caratteri in un'immagine di testo con il template di un singolo carattere; provare font e grassetto diversi.
- Trovare gli uccelli in Fig 15.5 del visionbook con un template ritagliato a mano; ridurre la risoluzione (`scipy.ndimage.zoom`) se il rilevatore è rumoroso.

## 5. Errori e imprecisioni nei notebook

Trovati eseguendo il codice o leggendolo.

### 5.1 Segno della derivata (`demo`)

`np.convolve` ribalta il kernel. Con `[-1,0,1]/2` il picco sul fronte di salita è **-0.5** e sul fronte di discesa +0.5. `np.correlate` dà +0.5 sulla salita. Verificato su un impulso senza rumore.

### 5.2 Risposta in frequenza della derivata (`demo`)

Il testo dice "cresce verso Nyquist (passa-alto)". In realtà |H(f)| = |sin(2 pi f)|: 0 in DC, massimo 1 a f = 0.25, di nuovo 0 a Nyquist (0.5). È passa-alto solo per f < 0.25, nel complesso è un passa-banda.

### 5.3 Rolloff (`classification`)

Il testo parla di "energia" ma il codice usa `np.cumsum(mag)`, cioè la magnitudo, non il suo quadrato. Su un segnale sintetico di prova la differenza è piccola (3380 Hz contro 3362 Hz).

### 5.4 Normalizzazione prima dello split (`classification`)

Media e deviazione sono calcolate su tutto il dataset prima di `train_test_split`: piccola fuga di informazione dal test. La cella finale usa una pipeline e la evita.

### 5.5 Piccoli refusi (`demo`)

- Il commento dice "band-pass" ma i filtri sono un passa-basso e un passa-alto.
- Titolo "Band-pass filte" (manca la "r").

## 6. Domande tipo esame

1. **Da cosa dipende la risoluzione in frequenza di una FFT?** Vale SR/N = 1/durata: dipende dalla durata del segnale.
2. **Perché un filtro a taglio netto in frequenza dà ringing?** Nel tempo è una sinc, che oscilla e non decade subito.
3. **Differenza tra convoluzione e cross-correlazione?** Nella convoluzione il kernel è ribaltato. Per cercare un pattern serve la cross-correlazione.
4. **Perché la cross-correlazione semplice sbaglia nel template matching?** Il punteggio dipende dalla luminosità, non dalla somiglianza. Si corregge con kernel a media 0 e divisione per il contrasto locale.
5. **Perché lo split casuale sovrastima l'accuratezza nelle cifre parlate?** Le clip della stessa persona finiscono sia nel train sia nel test. Con parlante escluso l'accuratezza scende (88.2% a 32.2% con il log-spettro).
6. **Che filtro è `[-1, 0, 1]/2` in frequenza?** |H(f)| = |sin(2 pi f)|: zero in DC e a Nyquist, massimo a f = 0.25.

## 7. Stato della verifica e come rieseguire

**Verificato eseguendo codice:** convoluzione e cross-correlazione 1D e 2D, risposta all'impulso, template matching, risposte in frequenza dei tre kernel, segno della derivata, lunghezze di `np.convolve`.

**Non verificato:**

- I numeri di `classification.ipynb` vengono dagli output salvati, non rieseguiti (dataset assente).
- Audio non ascoltato, grafici non guardati.
- I notebook non sono stati rieseguiti per intero.

**Ambiente usato per le verifiche:** numpy 2.2.6, scipy 1.16.1, matplotlib 3.10.5, scikit-learn 1.7.1.

Per rieseguire: `demo` e `15lif` servono numpy, scipy, matplotlib. `classification` richiede in più scikit-learn e il dataset come da 3.1.
