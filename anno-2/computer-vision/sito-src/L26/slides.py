VB = 'https://visionbook.mit.edu/'
def L(slug, txt): return f'<a href="{VB}{slug}" target="_blank">{txt}</a>'
LK = {
 '{C51}': L('VLMs.html', 'cap. 51'),
 '{C30}': L('representation_learning.html', 'cap. 30'),
 '{C37}': L('transfer_learning.html', 'cap. 37'),
 '{C13}': L('neural_nets_as_distribution_transformers.html', 'cap. 13'),
 '{C35}': L('bias_and_shift.html', 'cap. 35'),
}
def R(t):
    for k, v in LK.items(): t = t.replace(k, v)
    return t
def C(a, b=None): return 'NOTEBOOK lab_vlm_peft.ipynb · ' + (f'celle {a}–{b}' if b else f'cella {a}')

# ===================== PARTE 1 · SETUP E DATI =====================

s(1, "Obiettivi e struttura del lab", R("""
<p>Un solo notebook in otto parti, che mette insieme le ultime due lezioni: i modelli visione-linguaggio della <a href="#L24">L24</a> e il fine-tuning efficiente della <a href="#L25">L25</a>.</p>
<ol>
<li><b>Setup</b> e dataset <b>Oxford Flowers102</b> (102 specie di fiori, split ufficiali), con un sottoinsieme fisso di <b>16 specie</b> «difficili».</li>
<li><b>CLIP</b>: encoder, proiezioni nello spazio comune, matrice di similarità coseno.</li>
<li>Lo <b>spazio degli embedding</b>: PCA di immagini e testi, retrieval.</li>
<li><b>Zero-shot</b> e <b>few-shot</b>: classificazione con i prompt, prompt ensembling, linear probe, tutte le 102 classi, probe strato per strato.</li>
<li><b>Qwen2.5-VL</b>: captioning e VQA con un VLM generativo (facoltativo, serve una GPU).</li>
<li><b>PEFT</b> con la libreria <code>peft</code> di Hugging Face sull'encoder visivo di CLIP: BitFit, LoRA, QLoRA, DoRA, AdaLoRA, VeRA.</li>
<li><b>SemLA</b> in piccolo: un LoRA per dominio (nebbia, notte, pioggia) e fusione al test.</li>
<li><b>Confronto finale</b> di zero-shot, probe e PEFT sulle stesse immagini.</li>
</ol>
<p>Il notebook dice che serve una GPU per LoRA e Qwen. Noi l'abbiamo eseguito tutto su <b>CPU</b> (2 core) forzando la parte LoRA: le dieci sessioni di addestramento richiedono circa 3 minuti l'una. Qwen2.5-VL e QLoRA, che richiedono CUDA, sono spiegati ma non eseguiti.</p>
"""), sec=('l26-p1', 'Parte 1 · Setup e Flowers102', 'schede 1–3'), printed=C(1))

s(2, "Setup e configurazione", R("""
<pre>CLASS_IDS = [4, 11, 15, 17, 29, 30, 31, 40, 47, 48, 49, 50, 51, 52, 53, 63]
SHOTS_PER_CLASS = 10; VAL_PER_CLASS = 10; TEST_PER_CLASS = 20; BATCH_SIZE = 16
RUN_LORA = torch.cuda.is_available()   # parte PEFT
RUN_QWEN = False; RUN_PEFT_EXTENSIONS = True; RUN_SEMLA = True
LORA_RANK = 4; LORA_ALPHA = 8
EPOCHS = 20; MAX_STEPS_PER_EPOCH = 6</pre>
<ul>
<li>16 classi fisse, 10 immagini di training e 10 di validazione per classe (sono gli split ufficiali di Flowers102), 20 di test per classe estratte dallo split di test: 160 + 160 + 320 immagini.</li>
<li>LoRA con <b>r = 4</b> e <b>α = 8</b>, quindi il fattore di scala α/r vale 2.</li>
<li>Addestramento: 20 epoche ma al massimo 6 passi per epoca, con batch 16: <b>120 passi</b> in tutto, e 6 × 16 = 96 immagini per epoca su 160 (non tutte le immagini di training vengono viste in ogni epoca).</li>
<li>Le celle 3–4 installano i pacchetti (<code>transformers 4.51.3</code>, <code>peft</code>, <code>bitsandbytes</code>) e disinstallano <code>torchao</code>, che in Colab va in conflitto con <code>peft</code>.</li>
</ul>
<div class="box w"><b>Attenzione: senza GPU la parte PEFT salta, e poi una cella va in errore</b><p><code>RUN_LORA = torch.cuda.is_available()</code>: su CPU tutte le parti 6–8 vengono saltate in silenzio. Ma la cella 80 (l'esercizio sui conti di BitFit e LoRA) legge <code>peft_results["BitFit"]</code> senza controllare, e su CPU va in <code>KeyError</code>. Su CPU LoRA è lento ma fattibile: per eseguire tutto basta scrivere <code>RUN_LORA = True</code>. QLoRA resta saltata comunque, perché richiede bitsandbytes con CUDA.</p></div>
"""), printed=C(2, 6))

s(3, "Oxford Flowers102 e gli split ufficiali", R("""
<ul>
<li><b>102 specie</b> di fiori comuni nel Regno Unito, foto ad alta risoluzione. Gli split ufficiali hanno <b>10 immagini di training e 10 di validazione per classe</b>; il resto (6149 immagini) è il test.</li>
<li>Il notebook usa la lista dei nomi delle classi del repository di CLIP (<code>FLOWER_NAMES</code>, 102 nomi in ordine di etichetta).</li>
<li><code>choose_indices</code> sceglie a caso, con un generatore fissato (seed 42), un certo numero di indici per classe; <code>raw_subset</code> carica le immagini e rimappa le etichette da 0–101 a 0–15.</li>
<li>Le 16 classi: english marigold, colt's foot, globe-flower, peruvian lily, sweet william, carnation, garden phlox, barbeton daisy, buttercup, oxeye daisy, common dandelion, petunia, wild pansy, primula, sunflower, silverbush. Sono scelte apposta con <b>coppie che si somigliano</b>: margherite (oxeye e barbeton daisy), gialli tondi (globe-flower e buttercup), gialli a raggi (colt's foot e dandelion), garofani (carnation e sweet william).</li>
</ul>
<p>La figura mostra due foto di training per ogni classe.</p>
<div class="box w"><b>Attenzione: commento contraddittorio</b><p>Il commento in <code>choose_indices</code> dice di accedere agli elementi pubblici del dataset «per non dipendere dal layout non documentato di <code>_labels</code>», e la riga dopo usa proprio <code>ds._labels</code>. Funziona (con torchvision 0.29), ma è un attributo privato e potrebbe cambiare nome.</p></div>
"""), img='img/n08_fiori.png', printed=C(7, 8))

# ===================== PARTE 2 · CLIP =====================

s(4, "CLIP: encoder, proiezioni e matrice di similarità", R("""
<p>CLIP (<a href="#L24">L24</a>) ha due encoder. Per un'immagine x<sub>i</sub> e una descrizione s<sub>j</sub> produce h<sup>v</sup><sub>i</sub> ∈ ℝ<sup>D<sub>v</sub></sup> e h<sup>t</sup><sub>j</sub> ∈ ℝ<sup>D<sub>t</sub></sup>, li proietta nello spazio comune e li normalizza:</p>
<span class="f">v<sub>i</sub> = W<sub>v</sub>h<sup>v</sup><sub>i</sub> / ‖W<sub>v</sub>h<sup>v</sup><sub>i</sub>‖,  t<sub>j</sub> = W<sub>t</sub>h<sup>t</sup><sub>j</sub> / ‖W<sub>t</sub>h<sup>t</sup><sub>j</sub>‖,  S<sub>ij</sub> = v<sub>i</sub><sup>T</sup>t<sub>j</sub></span>
<ul>
<li><b>ViT-B/32</b>: immagini 224×224, patch 32×32, quindi 7 × 7 = <b>49 token di patch più il [CLS]</b>; D<sub>v</sub> = 768, proiettato a <b>d<sub>z</sub> = 512</b>.</li>
<li>Testo: BPE, transformer causale, feature del token di fine testo, D<sub>t</sub> = 512 proiettato a 512.</li>
<li>Nel codice: <code>clip.text_model(...).pooler_output</code> → <code>clip.text_projection</code> → <code>F.normalize</code>; per le immagini <code>vision_model(...).pooler_output</code> (il [CLS] dopo la LayerNorm finale) → <code>visual_projection</code> → normalizza.</li>
</ul>
<p><b>Nostra esecuzione</b>: 16 prompt «a photo of a {nome} flower.» diventano token di lunghezza 11 (con padding); <code>logit_scale.exp()</code> = <b>100,0</b>, cioè temperatura τ = 0,01, il massimo consentito in CLIP. La heatmap confronta un'immagine di test per classe con i 16 prompt: la diagonale è più rossa, ma i valori stanno quasi tutti fra 0,15 e 0,35.</p>
<div class="box x"><b>Approfondimento: perché i coseni sono così bassi</b><p>Immagini e testi non occupano la stessa zona dell'ipersfera (il <i>modality gap</i>, scheda 8): anche la coppia giusta ha coseno intorno a 0,3. Conta la differenza fra i valori, non il valore assoluto. Per questo la scala della figura (da −0,1 a 0,5) appiattisce i colori: con <code>vmin=0.1, vmax=0.4</code> la diagonale si vedrebbe molto meglio.</p></div>
"""), img='img/n12_similarita.png', sec=('l26-p2', 'Parte 2 · CLIP e similarità', 'schede 4–7'), printed=C(9, 12))

s(5, "La loss contrastiva simmetrica", R("""
<p>Con N coppie immagine-testo e logit ℓ<sub>ij</sub> = S<sub>ij</sub>/τ la loss di CLIP è</p>
<span class="f">ℒ<sub>CLIP</sub> = ½ [ (1/N) ∑<sub>i</sub> CE(ℓ<sub>i,:</sub>, i) + (1/N) ∑<sub>j</sub> CE(ℓ<sub>:,j</sub>, j) ]</span>
<p>Prima parte: per ogni immagine, una softmax <b>sulla riga</b> (quale testo le corrisponde). Seconda: per ogni testo, una softmax <b>sulla colonna</b>. Sulla diagonale le coppie giuste, fuori i negativi del batch.</p>
<pre>logits = clip.logit_scale.exp() * S
loss_i2t = F.cross_entropy(logits, pair_indices)
loss_t2i = F.cross_entropy(logits.T, pair_indices)</pre>
<p><b>Nostra esecuzione</b> sulle 16 coppie (un'immagine per classe con il suo prompt): immagine→testo <b>0,626</b>, testo→immagine <b>1,163</b>, simmetrica 0,895.</p>
<div class="box k"><b>Da saper fare: la domanda della cella 13</b><p>Perché le due loss differiscono se la matrice è la stessa? Perché normalizzano in direzioni diverse. Un'immagine «facile» con un coseno alto sulla sua didascalia vince la sua riga; ma la colonna di quel testo può contenere un'altra immagine che gli somiglia quasi altrettanto (per esempio la buttercup per il prompt di globe-flower, o la colt's foot per quello di dandelion): la softmax di colonna è più incerta. Le righe e le colonne contengono numeri diversi, quindi le cross-entropy sono diverse; la matrice è simmetrica solo nel nome, non nei valori.</p></div>
<div class="box b"><b>Dal libro · {C51}, § 51.3 e {C30}, § 30.10</b><p>Il libro presenta CLIP come un metodo contrastivo in cui le due viste sono un'immagine e la sua didascalia, con la InfoNCE dell'eq. 30.4 applicata nei due sensi; la temperatura non compare nella formula del libro, mentre CLIP la impara (qui il fattore 100).</p></div>
"""), img='img/n14_loss.png', printed=C(13, 14))

s(6, "Temperatura: similarità e softmax", R("""
<p>La probabilità di una descrizione j per l'immagine i è p(j | x<sub>i</sub>) = exp(S<sub>ij</sub>/τ) / ∑<sub>m</sub> exp(S<sub>im</sub>/τ). Il notebook varia la scala 1/τ e disegna la softmax per la prima immagine (english marigold).</p>
<ul>
<li><b>Scala 1</b>: tutte le barre intorno a 1/16 ≈ 0,06. I coseni differiscono di qualche centesimo, e senza amplificazione la softmax è quasi uniforme.</li>
<li><b>Scala 14</b>: la classe giusta prende circa 0,14 e barbeton daisy circa 0,12: ancora molto piatta.</li>
<li><b>Scala 100</b> (quella appresa da CLIP): english marigold circa <b>0,82</b>, barbeton daisy circa 0,15, il resto quasi zero.</li>
</ul>
<p>Il <b>ranking non cambia mai</b>: dividere tutti i coseni per lo stesso τ non cambia quale è il più grande. Cambia solo quanto la distribuzione è concentrata.</p>
<div class="box k"><b>Da saper fare: la domanda della cella 15</b><p>Abbassare τ (alzare la scala) rende la softmax più appuntita. Ma una probabilità alta non significa una predizione più affidabile: è solo la stessa differenza fra coseni moltiplicata per un numero più grande. La confidenza di una softmax dipende da τ, che è una scelta (o un parametro appreso per la loss di training), non una misura di affidabilità. Per giudicare la fiducia ha più senso guardare il margine fra i primi due coseni (scheda 13) o calibrare τ su un insieme di validazione.</p></div>
"""), img='img/n16_temperatura.png', printed=C(15, 16))

s(7, "Esercizio: la matrice di similarità", R("""
<p>Soluzione (il notebook lascia la cella vuota):</p>
<pre>S = features_5 @ text_features.detach().cpu().T
print(S.shape)                      # torch.Size([16, 16])
print([CLASS_NAMES[i] for i in S.argmax(dim=1).tolist()])</pre>
<ul>
<li><b>Forma</b>: (numero di immagini) × (numero di descrizioni), qui 16 × 16. Con quattro descrizioni in più diventa 16 × 20: una colonna per ogni testo.</li>
<li><b>Risultato</b>: 14 immagini su 16 hanno come descrizione più simile la propria. Gli errori: <b>colt's foot → common dandelion</b> e <b>globe-flower → buttercup</b>, proprio due delle coppie «gemelle» del sottoinsieme.</li>
<li>Il nome <code>features_5</code> è un residuo di una versione con 5 immagini: qui sono 16.</li>
</ul>
"""), printed=C(17, 18))

# ===================== PARTE 3 · SPAZIO DEGLI EMBEDDING =====================

s(8, "PCA degli embedding e modality gap", R("""
<p>Due PCA a 2 componenti sugli embedding a 512 dimensioni di 256 immagini di test (16 per classe):</p>
<ul>
<li><b>Solo immagini</b>: le prime due componenti spiegano il <b>26,5%</b> della varianza. Si vedono gruppi per specie (sunflower, colt's foot e dandelion a destra, i garofani a sinistra), parzialmente sovrapposti.</li>
<li><b>Immagini e testi insieme</b> (32,9%): la prima componente separa le due <b>modalità</b>. Tutte le immagini stanno vicino a PC1 ≈ 0, tutti i 16 testi (stelle) intorno a PC1 ≈ 0,9–1. È il <b>modality gap</b>: CLIP è addestrato a rendere alti i coseni delle coppie giuste <i>relativamente</i> alle altre, non a sovrapporre le due nuvole.</li>
<li>Lungo PC2 l'ordine delle stelle ricorda quello delle immagini (in alto dandelion e colt's foot, in basso garden phlox e petunia): l'allineamento c'è, ma solo in parte nelle direzioni di massima varianza.</li>
</ul>
<div class="box k"><b>Da saper fare: la domanda della cella 21</b><p>La stella più vicina nella figura non è sempre la classe predetta da CLIP. La PCA tiene solo 2 delle 512 dimensioni (un terzo della varianza) e conserva le direzioni di massima varianza, non i coseni; in più la direzione più «varia» è proprio quella che separa immagini e testi, che non serve a distinguere le classi. Retrieval e classificazione si calcolano nello spazio originale.</p></div>
<div class="box b"><b>Dal libro · {C51}, fig. 51.4 e § 30.10.1</b><p>Il libro disegna lo spazio congiunto come un'ipersfera su cui immagini e testi corrispondenti finiscono vicini; la loss contrastiva spinge verso <i>allineamento</i> (positivi vicini) e <i>uniformità</i> (punti sparsi sulla sfera). Il modality gap mostra che nella pratica le due modalità restano in due «calotte» diverse.</p></div>
"""), img='img/n20_pca_congiunta.png', sec=('l26-p3', 'Parte 3 · Spazio degli embedding e retrieval', 'schede 8–10'), printed=C(19, 22))

s(9, "Retrieval: testo → immagine e immagine → immagine", R("""
<p>Retrieval con il coseno nello spazio a 512 dimensioni: sim(s, x<sub>i</sub>) = t(s)<sup>T</sup>v(x<sub>i</sub>) per testo → immagine, sim(x, x<sub>i</sub>) = v(x)<sup>T</sup>v(x<sub>i</sub>) per immagine → immagine (escludendo la query stessa).</p>
<ul>
<li>«a close-up of a common dandelion»: 5 tarassachi su 5 (coseni 0,330–0,351).</li>
<li>«<b>a photo of a barbeton daisy</b>»: le prime 5 sono tutte <b>margherite bianche</b>, cioè oxeye daisy (coseni 0,335–0,358). La barbeton daisy (gerbera) è di solito rossa, arancione o rosa: CLIP associa la parola «daisy» alla margherita comune. È lo stesso errore che vedrai nella matrice di confusione.</li>
<li>Immagine → immagine (query = una colt's foot): i 5 vicini sono fiori gialli a raggi, con coseni 0,91–0,94, molto più alti dei coseni immagine-testo (stessa modalità, niente gap).</li>
</ul>
<div class="box k"><b>Da saper fare: retrieval contro zero-shot (cella 23)</b><p>Il retrieval fissa un testo e ordina molte immagini (si confrontano i valori di una <b>colonna</b> di S); lo zero-shot fissa un'immagine e sceglie fra poche descrizioni (una <b>riga</b>). Nel retrieval conta che le prime k siano giuste, nello zero-shot conta solo l'argmax, e l'insieme delle classi candidate cambia il risultato.</p></div>
"""), img='img/n24_retrieval_barbeton.png', printed=C(23, 28))

s(10, "Esercizio: le tue query", R("""
<p>Le nostre quattro query (la cella 30 lascia dei puntini da completare):</p>
<ul>
<li>«a photo of a sunflower»: 5 girasoli su 5 (coseni 0,325–0,340).</li>
<li>«a field of bright yellow flowers»: fiori gialli di specie diverse (buttercup, marigold, dandelion, globe-flower), coseni più bassi (0,27–0,28): la query descrive un colore, non una specie, e nessuna immagine è davvero «un campo».</li>
<li>«a purple flower with a dark center»: petunie e viole del pensiero (wild pansy), più un phlox: la descrizione per attributi funziona.</li>
<li>«a flower drawn by a child»: quattro margherite bianche e una globe-flower. Nessun disegno nel dataset: CLIP sceglie le foto più vicine al fiore «stilizzato» (petali bianchi a raggiera, centro giallo).</li>
</ul>
<p>La lezione: il testo libero permette query per attributi e per stile, ma il risultato dipende dalle parole scelte; prompt diversi per la stessa classe danno classifiche diverse (scheda 14).</p>
"""), img='img/n30_bambino.png', printed=C(29, 30))

# ===================== PARTE 4 · ZERO-SHOT E FEW-SHOT =====================

s(11, "Zero-shot: la galleria delle predizioni", R("""
<span class="f">ŷ(x) = argmax<sub>j</sub> v(x)<sup>T</sup>t<sub>j</sub></span>
<p>Nessun addestramento: la classe è il prompt più simile. La galleria mostra sei immagini di test (una ogni tre classi circa) con i 16 coseni in barre orizzontali: english marigold, peruvian lily, garden phlox, oxeye daisy, wild pansy, silverbush, <b>tutte corrette</b>.</p>
<p>Nota quanto sono vicine le barre: per la english marigold il coseno giusto è circa 0,34 e il secondo (barbeton daisy) circa 0,33. Una differenza di un centesimo decide la classe.</p>
"""), img='img/n32_galleria.png', sec=('l26-p4', 'Parte 4 · Zero-shot, linear probe e profondità', 'schede 11–17'), printed=C(31, 32))

s(12, "Zero-shot contro linear probe", R("""
<p>Stesso encoder congelato, due classificatori:</p>
<ul>
<li><b>Zero-shot</b>: argmax dei coseni con i 16 prompt.</li>
<li><b>Linear probe</b>: regressione logistica p(y | x) = softmax(Wv(x) + b) addestrata sulle 160 immagini di training (10 per classe) sugli embedding normalizzati a 512 dimensioni.</li>
</ul>
<p><b>Nostra esecuzione</b> sulle 320 immagini di test: zero-shot <b>81,2%</b>, linear probe <b>88,7%</b>.</p>
<p>Le matrici di confusione mostrano dove sbaglia lo zero-shot: <b>globe-flower → buttercup 18 volte su 20</b> (il prompt «globe-flower flower» è poco informativo per CLIP), <b>oxeye daisy → barbeton daisy 11 su 20</b> (lo scambio inverso del retrieval della scheda 9), english marigold → barbeton daisy 5. Il probe corregge quasi tutti questi errori (globe-flower 18/20 giuste) perché impara dalle immagini il confine fra le classi, invece di affidarsi al nome. Resta qualche confusione su petunia (14 su 20 nello zero-shot, 7 nel probe: qui il probe peggiora, scambiandola con sweet william e garden phlox).</p>
<div class="box b"><b>Dal libro · {C37}, § 37.3.2</b><p>Il linear probe è il modo più leggero di adattare un modello: un modulo lineare sulle feature congelate, ottimizzabile come un problema convesso. Nel libro serve anche per «sondare» cosa sa uno strato: se una feature separa linearmente le classi, lo strato «conosce» quella distinzione (scheda 17).</p></div>
"""), img='img/n33_confusione.png', printed=C(33))

s(13, "Gli errori e il margine", R("""
<p>Il notebook mostra 4 immagini corrette e 4 sbagliate, con il coseno della classe predetta e quello della seconda (<i>runner-up</i>). In tutto <b>260 corrette e 60 errori</b>.</p>
<ul>
<li>Le prime quattro corrette e le prime quattro sbagliate sono tutte english marigold (il test set è ordinato per classe): quelle sbagliate diventano barbeton daisy, con coseni 0,32–0,33 contro 0,30–0,32. I margini sono di uno o due centesimi sia per le giuste sia per le sbagliate.</li>
<li>Le calendule sbagliate sono quelle più «a margherita» (petali a raggiera ben aperti, centro scuro): proprio i tratti che CLIP associa alla barbeton daisy.</li>
</ul>
<div class="box k"><b>Da saper fare: la domanda della cella 34</b><p>Gli errori nascono da specie visivamente simili (forma e colore), da nomi poco noti o ambigui («daisy» compare in due classi), da sfondi e inquadrature. Un margine piccolo fra primo e secondo coseno segnala una predizione incerta; un margine grande non garantisce che sia giusta, ma in media gli errori hanno margini più piccoli.</p></div>
<div class="box x"><b>Approfondimento</b><p>Per una galleria più varia conviene scegliere gli esempi a caso fra tutte le classi (<code>rng.choice</code>), invece dei primi indici di un test set ordinato.</p></div>
"""), img='img/n35_errori.png', printed=C(34, 35))

s(14, "Prompt ensembling e sensibilità ai template", R("""
<p>Per ogni classe si codificano più template, si fa la media degli embedding normalizzati e si rinormalizza:</p>
<span class="f">t̄<sub>c</sub> = normalize( (1/K) ∑<sub>k</sub> t<sub>c,k</sub> )</span>
<p>La cella 37 lascia i template con dei puntini da completare. Noi abbiamo usato: «a photo of a {} flower.», «a close-up photo of a {} flower.», «a beautiful {} flower.», «a photo of a {}, a type of flower.» (quest'ultimo è uno dei template dell'articolo di CLIP per Flowers102).</p>
<p><b>Nostra esecuzione</b>: prompt singolo <b>81,2%</b>, ensemble di 4 <b>82,8%</b>. Template da soli: «a beautiful {} flower.» circa 84%, «a photo of a {} flower.» 81%, «a photo of a {}, a type of flower.» 81%, «a close-up photo of a {} flower.» circa 79%.</p>
<div class="box k"><b>Da saper fare: le domande delle celle 36 e 43</b><p>L'ensemble aiuta un po' (+1,6 punti) ma non batte il template migliore da solo: la media dei vettori sta «in mezzo» e un template cattivo la sposta nella direzione sbagliata. Media degli embedding e testo concatenato sono cose diverse: la media combina K punti dello spazio (un centroide), mentre concatenare i prompt in un'unica frase produce un solo testo lungo e strano, che l'encoder (con 77 token al massimo) codifica come una frase sola, senza nessuna garanzia di stare vicino al centroide.</p></div>
"""), img='img/n38_template.png', printed=C(36, 38))

s(15, "Zero-shot su tutte le 102 specie", R("""
<p>Stessa procedura con i 102 nomi e 8 immagini di test per specie (816 immagini): accuratezza top-1 <b>65,3%</b>.</p>
<p>Le confusioni più frequenti: geranium → pelargonium (8), marigold → english marigold (8), cape flower → gaura (7), ball moss → bromelia, prince of wales feathers → red ginger, moon orchid → hard-leaved pocket orchid, windflower → japanese anemone (6 ciascuna). Sono quasi tutte coppie che <b>anche il nome</b> rende vicine (stesso genere botanico o sinonimi), e alcune sono davvero indistinguibili per un non botanico.</p>
<p>La figura mostra le 10 immagini con il margine più negativo (coseno della classe giusta meno il miglior coseno sbagliato): pincushion protea scambiata per mexican aster e garden phlox, cape flower per gaura, ball moss per bromelia.</p>
<div class="box k"><b>Da saper fare: la domanda della cella 39</b><p>Da 16 a 102 classi l'accuratezza scende (81% → 65%), ma i numeri non sono confrontabili: con più candidati ci sono più occasioni di sbagliare, le 16 classi sono un sottoinsieme scelto apposta (con coppie difficili ma anche classi facili), e le immagini di test sono diverse (8 per classe su 102 contro 20 su 16). Il caso a caso sarebbe 1/16 ≈ 6% contro 1/102 ≈ 1%.</p></div>
"""), img='img/n40_difficili.png', printed=C(39, 40))

s(16, "Similarità fra le classi nello spazio del testo", R("""
<p>Matrice 102 × 102 dei coseni fra i prototipi di testo «a photo of a {nome} flower.» (diagonale esclusa). I valori sono quasi tutti fra 0,5 e 0,9: i prompt condividono gran parte delle parole.</p>
<p>Le coppie più simili: english marigold ↔ marigold (0,974), petunia ↔ mexican petunia (0,960), king protea ↔ pincushion protea (0,925), tree mallow ↔ mallow, fire lily ↔ sword lily, corn poppy ↔ tree poppy, pelargonium ↔ geranium (0,895), water lily ↔ lotus, windflower ↔ rose, globe-flower ↔ windflower.</p>
<div class="box k"><b>Da saper fare: la domanda della cella 41</b><p>In parte sì: marigold/english marigold e pelargonium/geranium sono fra le confusioni più frequenti della scheda 15. Ma non sempre: petunia ↔ mexican petunia ha coseno 0,96 e non è fra gli errori principali, perché i fiori sono diversi; cape flower → gaura è un errore frequente pur non essendo fra le coppie di testo più simili. La similarità fra testi misura quanto si somigliano i nomi, la difficoltà visiva quanto si somigliano le foto; lo zero-shot sbaglia soprattutto quando le due cose coincidono.</p></div>
"""), img='img/n42_prototipi.png', printed=C(41, 43))

s(17, "Le feature lungo la profondità del ViT", R("""
<p>Si estrae il token [CLS] dopo ogni blocco (13 «istantanee»: gli embedding iniziali più 12 blocchi), lo si normalizza e si addestra un linear probe separato su ciascuno.</p>
<p><b>Nostra esecuzione</b> (accuratezza di test, valori letti dal grafico): blocco 0 circa 6% (il caso), poi una salita lenta fino a circa 53% al blocco 6, una discesa intorno al 44% ai blocchi 8–9, e una risalita rapida: circa 61% al blocco 10, 72% all'11 e <b>circa 91% al 12</b>, sopra la linea tratteggiata del probe sugli embedding proiettati (88,7%).</p>
<ul>
<li>L'informazione che separa le specie emerge soprattutto negli <b>ultimi strati</b>: i primi codificano colori e texture locali, gli ultimi concetti.</li>
<li>Il [CLS] dei primi blocchi non ha ancora «raccolto» l'informazione delle patch: nei ViT il [CLS] diventa un riassunto dell'immagine solo dopo vari strati di attenzione.</li>
<li>L'ultimo blocco batte di poco la proiezione finale: la proiezione a 512 dimensioni è addestrata per allinearsi al testo, non per separare queste 16 specie, e perde un po' di informazione.</li>
</ul>
<div class="box b"><b>Dal libro · {C13}, fig. 13.9 e {C51}, fig. 51.3</b><p>Il libro mostra, strato per strato, come una rete trasforma la distribuzione dei dati fino a renderla separabile linearmente, e la fig. 51.3 fa la stessa analisi su CLIP: solo negli ultimi strati le classi si separano.</p></div>
"""), img='img/n45_profondita.png', printed=C(44, 46))

# ===================== PARTE 5 · QWEN2.5-VL =====================

s(18, "Qwen2.5-VL: un VLM generativo", R("""
<p>CLIP confronta embedding, non genera testo. <b>Qwen2.5-VL-3B-Instruct</b> è un VLM generativo (<a href="#L24">L24</a>): un encoder visivo produce token dell'immagine che condizionano un modello di linguaggio autoregressivo insieme all'istruzione:</p>
<span class="f">p<sub>θ</sub>(a | x, q) = ∏<sub>t=1</sub><sup>T</sup> p<sub>θ</sub>(a<sub>t</sub> | a<sub>&lt;t</sub>, x, q)</span>
<p>x l'immagine, q la domanda o istruzione, a = (a<sub>1</sub>, …, a<sub>T</sub>) la risposta generata un token alla volta.</p>
<ul>
<li>Caricamento in <b>4 bit NF4</b> con <code>BitsAndBytesConfig</code> (la stessa quantizzazione di QLoRA, <a href="#L25">L25</a>), calcolo in FP16; <code>min_pixels</code> e <code>max_pixels</code> limitano il numero di patch da 28×28 (da 256 a 768 token visivi).</li>
<li><code>ask_qwen</code> costruisce il messaggio in formato chat (immagine + testo), genera in modo greedy (<code>do_sample=False</code>) e decodifica solo la continuazione, tagliando i token d'ingresso.</li>
</ul>
<p>Disattivato di default (<code>RUN_QWEN = False</code>) e non eseguito da noi: richiede una GPU CUDA.</p>
"""), sec=('l26-p5', 'Parte 5 · Qwen2.5-VL (facoltativa)', 'schede 18–19'), printed=C(47, 50))

s(19, "Captioning, VQA, sensibilità al prompt, CLIP contro Qwen", R("""
<ul>
<li><b>Captioning</b> (cella 52): «Describe this image in one sentence.» su tre immagini di test.</li>
<li><b>VQA</b> (cella 54): due domande per immagine (oggetto principale, colore dei petali, quanti fiori, forma dei petali, colore dominante, sfondo). Le risposte sono testo libero di lunghezza variabile.</li>
<li><b>Esercizio</b> (cella 56): tre domande su un'immagine, una di presenza, una di conteggio, una di relazioni spaziali. Dalla <a href="#L24">L24</a> sai cosa aspettarti: i VLM sono bravi sulla presenza, peggiori su <b>conteggio</b> e <b>relazioni spaziali</b>.</li>
<li><b>Sensibilità al prompt</b> (cella 58): la stessa immagine con tre istruzioni diverse produce descrizioni diverse; il modello può inventare dettagli plausibili ma falsi (<i>allucinazioni</i>).</li>
<li><b>CLIP contro Qwen</b> (cella 63): CLIP sceglie fra 16 nomi fissi, Qwen risponde liberamente e può dare nomi fuori dalle 16 classi. Per un confronto di accuratezza bisogna vincolare entrambi agli stessi candidati (per esempio chiedendo a Qwen di scegliere da una lista).</li>
</ul>
<div class="box x"><b>Approfondimento</b><p>La cella 61 usa <code>google.colab.files.upload()</code>: fuori da Colab va sostituita con <code>Image.open('percorso.jpg')</code>.</p></div>
"""), printed=C(51, 63))

# ===================== PARTE 6 · PEFT =====================

s(20, "Gli strumenti comuni per il PEFT", R("""
<pre>def peft_logits(vision, proj, pixels, scale=10.0):
    pooled = vision(pixel_values=pixels).pooler_output
    image = F.normalize(proj(pooled), dim=-1)
    return scale * (image @ text_features.detach().T)

def train_peft(...):   # AdamW, lr 2e-4, EPOCHS x MAX_STEPS_PER_EPOCH passi, cross-entropy
def fresh_clip_encoder():   # una copia nuova e congelata di vision_model e visual_projection</pre>
<ul>
<li>Il classificatore resta quello <b>zero-shot</b>: i 16 embedding di testo fanno da pesi fissi, e si adatta solo l'encoder visivo. Il text encoder resta congelato.</li>
<li>Ogni metodo parte da <code>fresh_clip_encoder()</code>, cioè dagli stessi pesi preaddestrati: il confronto è equo.</li>
<li>Stesso budget per tutti: 120 passi da 16 immagini, AdamW con lr 2·10<sup>−4</sup>.</li>
</ul>
<div class="box w"><b>Attenzione: la scala dei logit è 10, non 100</b><p>Per l'addestramento <code>peft_logits</code> usa una scala fissa 10 (temperatura 0,1), mentre lo zero-shot di CLIP usa la scala appresa 100. Per l'argmax non cambia nulla, ma per la loss sì: con scala 10 la softmax è molto più piatta (scheda 6), la cross-entropy iniziale è alta (circa 2,15, vicina a ln 16 ≈ 2,77) e i gradienti spingono a cambiare molto gli embedding. È una scelta legittima, ma va saputa: è uno dei motivi per cui gli embedding si spostano tanto dopo LoRA (scheda 31).</p></div>
"""), sec=('l26-p6', 'Parte 6 · PEFT con la libreria peft', 'schede 20–26'), printed=C(64, 65))

s(21, "BitFit sull'encoder di CLIP", R("""
<pre>for n, p in vision.named_parameters():
    p.requires_grad_(n.endswith('bias'))</pre>
<p>Si sbloccano solo i bias: quelli di Q, K, V, O, dei due strati dell'MLP e delle LayerNorm in ogni blocco, più le due LayerNorm fuori dai blocchi. Nessun modulo aggiunto.</p>
<p><b>Nostra esecuzione</b>: <b>102 912</b> parametri addestrabili su 87 456 000 (0,118%); accuratezza di test <b>87,8%</b>, da 81,2% dello zero-shot.</p>
<div class="box k"><b>Da saper fare: il conto (cella 80)</b><p>Per blocco: attenzione 4d = 3072, MLP 3072 + 768 = 3840, due LayerNorm 2d = 1536: totale 8448 = 11d. Dodici blocchi: 101 376; più le due LayerNorm esterne (<code>pre_layrnorm</code> e <code>post_layernorm</code>) 1536: <b>102 912</b>, esattamente il valore misurato. La convoluzione delle patch in CLIP non ha bias.</p></div>
"""), printed=C(66, 67))

s(22, "LoRA su q_proj e v_proj", R("""
<pre>LoraConfig(r=4, lora_alpha=8, lora_dropout=0.05, bias='none',
           target_modules=['q_proj', 'v_proj'])
vision = inject_adapter_in_model(build_lora(), vision)</pre>
<ul>
<li><code>inject_adapter_in_model</code> sostituisce ogni <code>q_proj</code> e <code>v_proj</code> (24 matrici 768×768) con uno strato LoRA che contiene il Linear originale congelato più <code>lora_A</code> (4×768) e <code>lora_B</code> (768×4).</li>
<li><code>lora_dropout=0.05</code> applica dropout all'ingresso del ramo LoRA durante il training.</li>
</ul>
<p><b>Nostra esecuzione</b>: <b>147 456</b> parametri addestrabili (0,168%), cioè 24 × 4 × (768 + 768).</p>
<ul>
<li><b>Controllo dell'inizializzazione</b>: prima del training le predizioni sulle prime 8 immagini sono identiche a quelle zero-shot ([0, 0, 7, 0, 0, 0, 7, 0] in entrambi i casi). È B = 0 della <a href="#L25">L25</a>: ΔW = 0.</li>
<li><b>Dopo il training</b>: zero-shot 81,2% → <b>LoRA 92,8%</b>. La loss di training scende da 2,15 a 0,70 in 20 epoche, senza appiattirsi: con più passi migliorerebbe ancora.</li>
</ul>
<div class="box k"><b>Da saper fare: come cambia con r (celle 68 e 72)</b><p>Ogni proiezione aggiunge r(d<sub>in</sub> + d<sub>out</sub>) = 1536r parametri, 24 proiezioni: 36 864r. Con r = 2, 4, 8: 73 728, 147 456, 294 912. Raddoppiare il rango raddoppia i parametri ma, come nella <a href="#L25">L25</a>, non garantisce un'accuratezza migliore: con 160 immagini di training un rango più alto rischia più overfitting.</p></div>
"""), img='img/n69_loss_lora.png', printed=C(68, 69))

s(23, "La ΔW appresa e i suoi valori singolari", R("""
<p>Per la prima matrice adattata (<code>encoder.layers.0.self_attn.v_proj</code>) si calcola ΔW = (α/r)BA, con A 4×768, B 768×4, ΔW 768×768, e i suoi valori singolari.</p>
<ul>
<li>La mappa del blocco 64×64 in alto a sinistra è <b>piena</b>: quasi tutte le entrate sono diverse da zero (ordine di 10<sup>−3</sup>), con un evidente motivo a strisce verticali e orizzontali, tipico di un prodotto di poche colonne per poche righe.</li>
<li>I valori singolari: <b>4 diversi da zero</b> (circa 0,44, 0,31, 0,21, 0,12), tutti gli altri esattamente zero.</li>
</ul>
<div class="box k"><b>Da saper fare: la domanda della cella 70</b><p>Il numero di valori singolari non nulli è al massimo r = 4, ed è esattamente 4 qui. Un aggiornamento a basso rango <b>non</b> modifica pochi pesi: modifica tutti i 589 824 pesi, ma lungo sole 4 direzioni. Il motivo a strisce è proprio questo: ogni riga di ΔW è una combinazione delle stesse 4 righe di A.</p></div>
"""), img='img/n71_deltaw.png', printed=C(70, 72))

s(24, "QLoRA (non eseguita)", R("""
<span class="f">h = dequant(W<sub>NF4</sub>) x + (α/r) BAx</span>
<ul>
<li>CLIP viene ricaricato con <code>BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.float32)</code>: pesi in NF4 con double quantization, calcolo in FP32.</li>
<li><code>prepare_model_for_kbit_training</code> congela tutto e porta in FP32 i parametri piccoli che conviene tenere precisi (LayerNorm).</li>
<li>Prima del LoRA si misura lo zero-shot del modello <b>quantizzato</b> (può essere un po' diverso da quello in FP32), poi si inietta LoRA sull'encoder visivo quantizzato e si controlla che l'inizializzazione non cambi le predizioni.</li>
<li>Il ciclo ha controlli contro valori non finiti e il <i>gradient clipping</i> a norma 1: con pesi quantizzati l'addestramento è più fragile.</li>
<li>Il blocco <code>finally</code> ripristina <code>text_features</code>, che durante l'esperimento è sostituito da quello del modello quantizzato.</li>
</ul>
<p>Richiede bitsandbytes con CUDA: su CPU stampa «Skipping QLoRA».</p>
"""), printed=C(73, 74))

s(25, "DoRA, AdaLoRA e VeRA", R("""
<pre>build_dora():    LoraConfig(..., use_dora=True)
build_adalora(): AdaLoraConfig(target_r=4, init_r=8, total_step=120, tinit=0, tfinal=0, deltaT=1)
build_vera():    VeraConfig(r=64, projection_prng_key=42)   # con get_peft_model</pre>
<p><b>Nostra esecuzione</b> (stesso budget, stesse immagini):</p>
<table>
<tr><th>metodo</th><th>parametri addestrabili</th><th>accuratezza</th></tr>
<tr><td>DoRA</td><td>165 888</td><td><b>93,1%</b></td></tr>
<tr><td>AdaLoRA</td><td>295 104</td><td>82,5%</td></tr>
<tr><td>VeRA (r = 64)</td><td>19 968</td><td>81,6%</td></tr>
</table>
<ul>
<li><b>DoRA</b>: i parametri di LoRA più un vettore di moduli m da 768 per ognuna delle 24 matrici (147 456 + 18 432 = 165 888). Risultato appena sopra LoRA.</li>
<li><b>AdaLoRA</b>: parte da init_r = 8, quindi per matrice P (8×768), Q (768×8) e Λ (8): 12 296 × 24 = 295 104.</li>
<li><b>VeRA</b>: per matrice un vettore d da 64 e uno b da 768, cioè 832 × 24 = 19 968; le matrici casuali sono buffer condivisi, non parametri.</li>
</ul>
<div class="box w"><b>Attenzione: AdaLoRA e VeRA non sono confrontati in modo equo</b><p>Il notebook avverte che AdaLoRA è incompleto: <code>train_peft</code> non chiama mai <code>update_and_allocate</code>, quindi la potatura dei ranghi non avviene, e iniettando con <code>inject_adapter_in_model</code> manca anche la penalità di ortogonalità. In più P e Q partono con valori molto piccoli e Λ da zero, così con lr 2·10<sup>−4</sup> e 120 passi si muovono poco. VeRA ha lo stesso problema in forma più forte: il vettore b parte da zero e VeRA, per costruzione, ha bisogno di learning rate molto più alti (l'articolo usa valori dell'ordine di 10<sup>−2</sup>); con lo stesso lr di LoRA resta praticamente allo zero-shot (81,6% contro 81,2%). I risultati di AdaLoRA e VeRA qui dicono «con questo budget non si muovono», non che i metodi siano peggiori.</p></div>
"""), printed=C(75, 76))

s(26, "Confronto dei metodi PEFT e conti dei parametri", R("""
<p>Il grafico della cella 78 mette a confronto accuratezza e parametri (scala logaritmica). Con l'esercizio della cella 81 abbiamo aggiunto LoRA anche su <code>out_proj</code>:</p>
<table>
<tr><th>metodo</th><th>parametri</th><th>accuratezza</th></tr>
<tr><td>BitFit</td><td>102 912</td><td>87,8%</td></tr>
<tr><td>LoRA q, v</td><td>147 456</td><td>92,8%</td></tr>
<tr><td>DoRA q, v</td><td>165 888</td><td>93,1%</td></tr>
<tr><td><b>LoRA q, v, o</b></td><td>221 184</td><td><b>94,4%</b></td></tr>
<tr><td>AdaLoRA</td><td>295 104</td><td>82,5%</td></tr>
<tr><td>VeRA</td><td>19 968</td><td>81,6%</td></tr>
</table>
<div class="box k"><b>Da saper fare: le domande delle celle 79 e 82</b><p>BitFit e LoRA hanno un numero di parametri simile perché 11d per blocco (bias) e 4 × 1536 × 2 = 12 288 per blocco (LoRA con r = 4 su due matrici) sono dello stesso ordine; con r = 2 LoRA ne ha meno di BitFit. Più parametri non vuol dire più accuratezza (AdaLoRA ne ha di più e va peggio). LoRA si fonde in W<sub>0</sub> senza costo in inferenza perché è lineare; QLoRA richiede la dequantizzazione a ogni moltiplicazione perché i pesi sono salvati in 4 bit (e se si fonde BA in pesi a 4 bit, bisogna riquantizzare). VeRA può usare un rango più alto perché il rango tocca solo il vettore d (r numeri), mentre le matrici A e B sono casuali e condivise fra tutti gli strati; in LoRA invece A e B sono propri di ogni matrice.</p></div>
<div class="box x"><b>Approfondimento: quanto pesa un checkpoint</b><p>Con <code>peft</code> si salva solo l'adapter: 147 456 parametri in FP32 sono circa 0,6 MB, contro circa 600 MB dell'intero CLIP ViT-B/32 (151 milioni di parametri) in FP32.</p></div>
"""), img='img/n78_confronto_peft.png', printed=C(77, 82))

# ===================== PARTE 7 · SEMLA =====================

s(27, "SemLA in piccolo: i domini sintetici", R("""
<p>Il notebook riproduce il meccanismo di SemLA (<a href="#L25">L25</a>) su classificazione, simulando il domain shift con tre corruzioni delle stesse immagini:</p>
<ul>
<li><b>fog</b>: sfocatura gaussiana (raggio 1,2) e fusione al 48% con un velo grigio chiaro (230, 235, 240): meno contrasto.</li>
<li><b>night</b>: i canali R, G, B moltiplicati per 0,28, 0,36, 0,55 più un piccolo offset blu: immagine scura e fredda.</li>
<li><b>rain</b>: luminosità al 75% e strisce chiare semitrasparenti disegnate in diagonale.</li>
<li><b>clean</b>: le immagini originali.</li>
</ul>
<p>La figura mostra sei fiori di training nei quattro domini.</p>
<div class="box x"><b>Approfondimento: la pioggia è sempre la stessa</b><p>Il generatore delle strisce è reinizializzato con seed 42 per ogni immagine: tutte le immagini della stessa dimensione hanno <b>esattamente le stesse strisce</b> nelle stesse posizioni. Per una pioggia più realistica il generatore andrebbe creato una volta fuori dal ciclo.</p></div>
"""), img='img/n86_domini.png', sec=('l26-p7', 'Parte 7 · SemLA: recupero e fusione di LoRA', 'schede 27–30'), printed=C(83, 85))

s(28, "Un LoRA per ogni dominio", R("""
<p>Per ogni dominio: un CLIP nuovo, LoRA su q e v, training sulle immagini di training corrotte, test sulle immagini di test corrotte allo stesso modo. Si salvano le matrici (A, B, scala) di ogni strato e il <b>centroide</b> normalizzato degli embedding CLIP (del modello congelato) delle immagini di training del dominio.</p>
<p><b>Nostra esecuzione</b>, accuratezza nel proprio dominio: clean <b>93,1%</b>, fog <b>91,9%</b>, night <b>92,5%</b>, rain <b>89,1%</b>.</p>
<p>Il LoRA «clean» ha la stessa configurazione di quello della parte 6 ma dà 93,1% invece di 92,8%: l'ordine dei batch e il dropout dipendono dallo stato del generatore casuale, che a questo punto del notebook è diverso. Su 320 immagini un'immagine vale 0,3 punti: differenze di questo ordine sono rumore.</p>
"""), printed=C(86, 87))

s(29, "Recupero e fusione al test", R("""
<p>Per un'immagine di test: embedding CLIP congelato, coseno con i centroidi, i k = 2 domini più vicini, pesi con una softmax a temperatura (scala 10 sulle similarità), e l'aggiornamento</p>
<span class="f">ΔW(x) = ∑<sub>i=1</sub><sup>k</sup> w<sub>i</sub>(x) (α/r) B<sub>i</sub>A<sub>i</sub></span>
<p>sommato temporaneamente ai pesi di un CLIP congelato, usato per la predizione e poi sottratto. Quattro condizioni su 64 immagini per dominio (4 per classe): zero-shot, adapter del dominio sbagliato (il successivo nella lista), fusione dei due recuperati, oracolo (l'adapter del dominio vero).</p>
<p><b>Nostra esecuzione</b> (valori letti dal grafico, ogni immagine vale circa 1,6 punti):</p>
<ul>
<li><b>Zero-shot</b>: circa 83% clean, 80% fog, <b>70% night</b>, 77% rain. La notte è il dominio più dannoso.</li>
<li><b>Qualunque adapter</b> aiuta molto, anche quello del dominio sbagliato (86–92%): gran parte del guadagno viene dall'aver adattato CLIP al compito delle 16 specie, non al dominio.</li>
<li><b>Fusione</b>: 92–94% in tutti i domini, al livello dell'oracolo (e su fog e rain perfino sopra di una o due immagini, cosa possibile con 64 immagini).</li>
</ul>
<div class="box k"><b>Da saper fare: la domanda della cella 94</b><p>Non servono gradienti perché si combinano soltanto matrici già addestrate, pesate con similarità calcolate in un passo in avanti di CLIP. Un adapter di un altro dominio migliora comunque lo zero-shot perché ha imparato le 16 classi; la fusione aiuta di più quando il dominio di test è un misto, o quando il recupero sbaglia di poco. Può peggiorare rispetto all'oracolo se recupera domini sbagliati con peso alto.</p></div>
<div class="box w"><b>Attenzione: «exactly undo the patch» non è esatto</b><p><code>_apply_delta</code> somma w·ΔW ai pesi e poi lo sottrae. In virgola mobile (W + Δ) − Δ non è sempre uguale a W: restano errori di arrotondamento dell'ordine di 10<sup>−8</sup> che si accumulano sulle oltre mille predizioni. Qui sono trascurabili, ma per un ripristino esatto conviene salvare una copia dei pesi e ricopiarla. In più <code>dict(vision.named_modules())</code> viene ricostruito per ogni strato a ogni chiamata, il che rende il ciclo lento senza motivo.</p></div>
"""), img='img/n91_fusione.png', printed=C(88, 90))

s(30, "Esercizio: un dominio nuovo, «sepia»", R("""
<pre>def corrupt_sepia(images):
    tf = T.ColorJitter(saturation=(0.1, 0.1), hue=(0.08, 0.08))
    return [tf(img) for img in images]</pre>
<p>Si addestra un quinto LoRA sul dominio nuovo, se ne calcola il centroide e lo si aggiunge alla libreria. <b>Nostra esecuzione</b>: per un'immagine di test «sepia» il recupero sceglie <b>sepia (peso 0,60) e night (0,40)</b>, quindi il nuovo dominio viene riconosciuto; il secondo è la notte, l'altro dominio con colori spenti.</p>
<div class="box w"><b>Attenzione: non è un seppia</b><p>Con <code>saturation=(0.1, 0.1)</code> la saturazione scende al 10% e lo spostamento di tinta (0,08) agisce su colori ormai quasi grigi: il risultato è un'immagine <b>quasi in bianco e nero</b>, come si vede nella figura, non il tono marrone di una vecchia foto. Un vero seppia si ottiene con la matrice di colore classica (per esempio R′ = 0,393R + 0,769G + 0,189B e simili per G′ e B′) o convertendo in grigi e poi colorando in marrone. Inoltre la cella fa <code>DOMAINS.append('sepia')</code>: rieseguirla aggiunge «sepia» una seconda volta, e il recupero lo vede due volte.</p></div>
"""), img='img/n94_sepia.png', printed=C(91, 93))

# ===================== PARTE 8 · CONFRONTO =====================

s(31, "Quanto si sposta la rappresentazione dopo LoRA", R("""
<p>Per ogni immagine di test la distanza coseno fra embedding prima e dopo LoRA: Δ<sub>i</sub> = 1 − (v<sub>i</sub><sup>base</sup>)<sup>T</sup>v<sub>i</sub><sup>LoRA</sup>. Si usano gli embedding LoRA salvati subito dopo il training della parte 6 (la parte 7 riusa le variabili <code>vision</code> e <code>proj</code>).</p>
<p><b>Nostra esecuzione</b>: distanza media <b>0,65</b> (istogramma fra 0,4 e 0,85), quasi uguale per tutte le classi (da circa 0,59 per sunflower a 0,77 per english marigold). LoRA <b>corregge 49</b> immagini sbagliate dallo zero-shot e ne <b>peggiora 12</b>.</p>
<ul>
<li>0,65 è uno spostamento enorme: in media l'embedding ruota di circa 70 gradi. Con 147 mila parametri LoRA cambia profondamente la geometria dello spazio, non la ritocca.</li>
<li>Corrette: soprattutto english marigold che lo zero-shot chiamava barbeton daisy. Peggiorate: soprattutto <b>barbeton daisy</b> (gerbere rosse e arancioni) che ora diventano sunflower o oxeye daisy.</li>
<li>Nella PCA (base calcolata sugli embedding congelati) le nuvole di LoRA sono più compatte per classe e spostate, ma la PCA spiega solo il 26% della varianza.</li>
</ul>
<div class="box k"><b>Da saper fare: le domande della cella 95</b><p>Uno spostamento più grande non vuol dire una classificazione migliore: le distanze sono simili per tutte le classi, e quello che conta è la direzione dello spostamento rispetto ai prototipi di testo, non quanto ci si sposta. Lo spostamento è così grande anche perché l'addestramento usa scala 10 (scheda 20): con una softmax piatta la cross-entropy spinge forte a ruotare gli embedding verso il prototipo giusto, e niente frena l'allontanamento dallo spazio originale di CLIP.</p></div>
<div class="box x"><b>Approfondimento</b><p>La prima figura della cella ha una legenda posizionata con <code>bbox_to_anchor=(2.24, 1)</code> rispetto al primo grafico: finisce in mezzo fra i due pannelli e li stringe. Basta <code>fig.legend(..., loc='center right')</code>.</p></div>
"""), img='img/n97_corretti.png', sec=('l26-p8', 'Parte 8 · Confronto finale', 'schede 31–32'), printed=C(95, 96))

s(32, "Il confronto finale sulle stesse immagini", R("""
<table>
<tr><th>metodo</th><th>accuratezza sul test pulito (320 immagini)</th></tr>
<tr><td>CLIP zero-shot</td><td>81,2%</td></tr>
<tr><td>CLIP linear probe (10 esempi per classe)</td><td>88,8%</td></tr>
<tr><td>BitFit</td><td>87,8%</td></tr>
<tr><td>LoRA q, v</td><td>92,8%</td></tr>
<tr><td>VeRA</td><td>81,6%</td></tr>
<tr><td>DoRA</td><td>93,1%</td></tr>
<tr><td>AdaLoRA</td><td>82,5%</td></tr>
<tr><td>LoRA q, v, o (nostra aggiunta)</td><td>94,4%</td></tr>
</table>
<p>Le idee da portare a casa:</p>
<ul>
<li>Lo zero-shot è un ottimo punto di partenza senza nessuna etichetta, ma sbaglia sulle coppie con nomi o aspetto simili.</li>
<li>Il linear probe usa le stesse feature e guadagna 7–8 punti con 10 esempi per classe.</li>
<li>Adattare l'<b>encoder</b> con LoRA o DoRA guadagna altri 4–6 punti con lo 0,2% dei parametri; BitFit si ferma al livello del probe.</li>
<li>AdaLoRA e VeRA, con questo budget e questo learning rate, non si muovono (scheda 25).</li>
</ul>
<p>Le domande finali della cella 99 hanno le risposte nella sezione <a href="#l26-soluzioni">Soluzioni</a>.</p>
"""), img='img/n99_riepilogo.png', printed=C(97, 99))
