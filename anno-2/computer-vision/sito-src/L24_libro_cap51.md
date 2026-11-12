# Visionbook cap. 51 "Vision and Language" — report di lettura (https://visionbook.mit.edu/VLMs.html)

Struttura: 51.1 Introduction · 51.2 Background: Representing Text as Tokens · 51.3 Learning Visual Representations from Language Supervision · 51.4 Translating between Images and Text (51.4.1 Text-to-Image, 51.4.2 Image-to-Text) · 51.5 Text as a Visual Representation · 51.6 Visual Question Answering · 51.7 Concluding Remarks. Figure 51.1–51.13.

## 51.1
Visione e linguaggio costruiscono entrambi modelli del mondo; il linguaggio come rappresentazione del pensiero (Fodor 1975). Il linguaggio può migliorare la visione e viceversa.

## 51.2 Token
Stessa ricetta della visione moderna: tokenizzare, poi transformer (cap. 26).
Tre opzioni: one-hot per parola (vocabolario K enorme: >100.000 parole in inglese, identificatori aperti); one-hot per carattere (poche decine di codici ma una parola diventa una sequenza); **BPE** (Gage 1994): codici per sottostringhe frequenti come "th", "ing"; usato da GPT e CLIP.
Token = W_tokenize · x, x one-hot in R^K, W_tokenize di dimensioni d × K: in pratica una lookup table. Fig. 51.1: stringa → one-hot → vettori token (a livello di parola per semplicità).
Uscita: modello autoregressivo che predice il prossimo elemento con una softmax sui K elementi del vocabolario.

## 51.3 Rappresentazioni visive dalla supervisione del linguaggio
Il linguaggio come pretext task (cap. 30). La classificazione è già una forma debole di supervisione linguistica (un nome fra K). Lavori precedenti: aggettivi e verbi (Isola et al. 2015), relazioni (Visual Genome), domande-risposte (VQA). Con dati e calcolo sufficienti conviene usare tutto il linguaggio libero: CLIP (Radford et al. 2021).
CLIP è un metodo contrastivo (cap. 30 § 30.10) le cui due "viste" sono un'immagine e la sua didascalia. Precursore per il captioning: Im2Text (Ordóñez et al. 2011).
Notazione: ℓ immagine, t testo; f_ℓ encoder immagine (input pixel [3×N×M]), f_t encoder testo; z_ℓ = f_ℓ(ℓ), z_t = f_t(t), normalizzati a norma 1; d_z dimensione dell'embedding; S^{d_z} insieme dei vettori unitari.
Obiettivo: versione SIMMETRICA della InfoNCE dell'eq. 30.4 (la formula nel libro è un'immagine; nel libro non compare la temperatura). La normalizzazione impedisce di abbassare la loss spingendo i negativi infinitamente lontano.
Fig. 51.2: batch di N = 6 coppie, matrice 6×6 di punteggi: 6 positivi sulla diagonale (verdi) da aumentare, 30 negativi fuori diagonale (rossi) da diminuire.
Fig. 51.3: t-SNE (cap. 13, fig. 13.9) degli embedding dei due rami, separato per encoder ma congiunto fra gli strati; immagini come icone con colore e forma. Per le immagini gli strati iniziali raggruppano per COLORE e i finali più per FORMA; per il testo il contrario. Spiegazione: nei pixel il colore è superficiale, la forma richiede elaborazione; nel testo parole di colore e di forma sono ugualmente semplici. È un'osservazione qualitativa.
Fig. 51.4: spazio congiunto. Dopo la normalizzazione tutti gli embedding stanno su un'ipersfera (disegnata come cerchio); ogni descrizione cade vicino alle icone che descrive (non perfettamente). Embedding CLIP a 768 dimensioni proiettati in 2D con kernel PCA con kernel coseno; tolta la prima componente principale, che codifica uno scostamento globale fra embedding di immagini e di testi (il "modality gap").
Classificatori zero-shot su misura: per ogni classe una frase t^a, t^b...; z_t^a = f_t(t^a), z_t^b = f_t(t^b); immagine z_ℓ^q = f_ℓ(ℓ^q); si sceglie la classe con prodotto scalare massimo: ŷ = argmax_c z_ℓ^q · z_t^c. Fig. 51.5: "striped red circles" contro "polka dotted green square", CLIP congelato. Fig. 51.6: (a) embedding delle immagini, (b) classificatore triangolo/cerchio (forma), (c) viola/verde acqua (colore), (d) punta di freccia/palla (oggetto): stesse immagini, partizioni diverse dello spazio secondo i testi scelti; più classi = più vettori testo. Paragone con un astrolabio.

## 51.4 Tradurre fra immagini e testo
Estende la traduzione fra domini del cap. 34 a modalità diverse (X2Y). Ricetta modulare: encoder f: X → Z, decoder g: Z → Y, traduttore g∘f. Problema: l'uscita dell'encoder può non essere un ingresso adatto al decoder. Soluzioni: (1) fine-tuning di g∘f su coppie; (2) f e g congelati e un traduttore h: Z → Z nello spazio latente (g∘h∘f), cfr. latent diffusion (Rombach et al. 2022).
51.4.1 Text-to-image: modello generativo condizionato (cap. 34) con il testo come condizione. (a) cVAE (§ 34.4.2), che il libro attribuisce a DALL-E 1: in addestramento encoder immagine + decoder condizionato sul testo (fig. 51.8), in campionamento rumore gaussiano + testo nel decoder (fig. 51.9). (b) diffusione condizionata (DALL-E 2, latent diffusion): embedding testuali inseriti in più strati della U-Net di denoising (fig. 51.10). La VAE genera in un passo, la diffusione con una catena di passi di denoising. Fig. 51.7: text-to-image come mappa dallo spazio dei testi a quello delle immagini.
51.4.2 Image-to-text (captioning): encoder immagine (transformer → token) + decoder testuale autoregressivo che legge i token visivi con cross-attention (fig. 51.11; esempio BLIP-2). Varianti: ogni strato del decoder fa cross-attention ai token immagine, oppure l'encoder comprime i token in un unico token riassuntivo.
Cross-attention: Q_t = T_t W_{t,q}ᵀ (query dai token testo), K_ℓ = T_ℓ W_{ℓ,k}ᵀ, V_ℓ = T_ℓ W_{ℓ,v}ᵀ (chiavi e valori dai token immagine), A_cross = softmax(Q_t K_ℓᵀ / √m), T_out,cross = A_cross V_ℓ (m = dimensione delle chiavi, mai definita nel capitolo). Combinazione con la self-attention: T = w_cross T_out,cross + w_self T_out,self (pesi eventualmente appresi).
Decoder autoregressivo (§ 32.7) con attenzione causale (§ 26.10). In addestramento riceve i token delle parole precedenti della didascalia vera (teacher forcing, termine non usato nel libro); in campionamento si genera parola per parola riappendendo l'output. Token BPE o a parola.

## 51.5 Il testo come rappresentazione visiva
Un modello image-to-text è un altro encoder visivo la cui uscita è testo. Altre rappresentazioni: frequenze di Fourier, semantica e geometria della scena, embedding (DINO, CLIP). Fig. 51.12: una stessa immagine in più rappresentazioni (pixel, profondità con MiDaS, caption di BLIP-2, ...). Il testo si collega ai modelli di linguaggio, che possono ragionare sul contenuto; ma non conserva tutto.

## 51.6 VQA
Obiettivo: un sistema che risponde a qualunque domanda su un'immagine ("test di Turing per la visione"). VQA (Antol et al. 2015): immagine + domanda → risposta testuale. Ricetta: encoder testo per la domanda, encoder immagine, decoder testo per la risposta; dati come tuple {[domanda, immagine], risposta}; riferimento BLIP-2. Esercizio: modificare il transformer della fig. 51.11 per il VQA. Fig. 51.13: esempio di sistema VQA.

## 51.7
Il linguaggio come rappresentazione percettiva: dice "cosa c'è dove" (Marr 1982) in forma compatta e astratta collegata ad altra conoscenza.

## Refusi notati
z_t^b = f_t(t^a) (va t^b); "prodotto scalare fra vettori unitari proporzionale all'angolo" (è il coseno); S^{d_z} vs ipersfera (d_z−1)-dimensionale; "text encoder" invece di "text decoder" nel testo di 51.4.2 e nella didascalia della fig. 51.11; m non definito; refusi tipografici minori ("principle component", "the the", "cricle").
