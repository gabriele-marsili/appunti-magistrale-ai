NB = 'NOTEBOOK panorama.ipynb · '
HOM = '<a href="https://visionbook.mit.edu/homography.html" target="_blank">visionbook.mit.edu/homography.html</a>'
HC = '<a href="https://visionbook.mit.edu/homogeneous_coordinates.html" target="_blank">visionbook.mit.edu/homogeneous_coordinates.html</a>'

# ---------------------------------------------------------------- dalle immagini ai match

s(1, "Panorama a basso livello: obiettivo, setup, immagini", """
<p>Il notebook rifà <b>a mano</b> la pipeline della L9 (slide 48): keypoint → descrittori → match → omografia robusta → warping → composizione, su due foto della serie "boat" di OpenCV (lungofiume di San Pietroburgo, 3888 × 2592 pixel ciascuna). Poi confronta il risultato con lo <code>Stitcher</code> di OpenCV, che fa tutto in una chiamata.</p>
<pre>import cv2, numpy as np, matplotlib.pyplot as plt
cv2.__version__                          # '4.13.0'

def to_rgb(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

img1 = cv2.imread("data/boat1.jpg")      # array uint8 (2592, 3888, 3), canali B, G, R
img2 = cv2.imread("data/boat2.jpg")</pre>
<p><b>Figura:</b> le due foto. La seconda è scattata ruotando la camera verso destra: il campanile dorato, a destra nella prima, è quasi al centro nella seconda; a destra compaiono un ponte e la riva lontana.</p>
<ul>
<li><code>cv2.imread</code> restituisce un array NumPy <b>(altezza, larghezza, canali)</b> in ordine <b>BGR</b>, non RGB. Matplotlib si aspetta RGB: senza <code>to_rgb</code> cielo e acqua diventerebbero arancioni. Se il file non esiste, <code>imread</code> non solleva eccezioni ma restituisce <code>None</code>.</li>
<li><code>show</code> è un piccolo aiuto: figura, <code>imshow</code> (in grigio se l'immagine ha 2 dimensioni), assi spenti.</li>
<li>Le immagini vanno bene per un'<b>omografia</b> perché la scena è lontana e la camera ruota quasi sul posto: è il caso "rotazione pura" della L9 (slide 22–23), in cui H = KRK<sup>−1</sup> vale per tutti i punti, a qualunque profondità.</li>
</ul>
""", sec=("l10-match", "Dalle immagini ai match: SIFT e ratio test", 'schede 1–6'), img='img/l10_input.jpg', printed=NB + 'celle 1–5')

s(2, "Keypoint e descrittori SIFT con detectAndCompute", """
<pre>gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
sift = cv2.SIFT_create()                             # parametri di default
kps1, desc1 = sift.detectAndCompute(gray1, None)    # None = nessuna maschera
kps2, desc2 = sift.detectAndCompute(gray2, None)</pre>
<ul>
<li><code>detectAndCompute</code> fa in una chiamata le due metà della SIFT della L8: <b>rilevamento</b> (estremi della piramide DoG, raffinamento sub-pixel, scarto dei punti a basso contrasto e sui bordi, orientazione dominante) e <b>descrizione</b> (istogrammi di gradiente 4 × 4 celle × 8 orientazioni = <b>128</b> valori).</li>
<li>Uscite: <code>kps</code>, una lista di oggetti <code>cv2.KeyPoint</code> (posizione, scala, angolo, risposta: scheda 4), e <code>desc</code>, una matrice <b>N × 128</b> di <code>float32</code>, una riga per keypoint, nello stesso ordine.</li>
<li>Numeri verificati: <b>19096</b> keypoint nella prima foto, <b>12804</b> nella seconda (la prima ha più texture: il veliero, l'edificio a sinistra, il ghiaccio). Tempo: circa 5.6 s per le due immagini su 2 core.</li>
<li>Il secondo argomento è una <b>maschera</b> opzionale: un'immagine uint8 che limita la ricerca ai pixel non nulli (per esempio solo la zona di sovrapposizione).</li>
</ul>
<div class="box w"><b>Attenzione: la conversione in grigio non è obbligatoria</b><p>Il commento dice che SIFT di OpenCV "uses a single channel, so we convert". È vero che SIFT lavora sulla luminanza, ma <code>detectAndCompute</code> accetta anche un'immagine BGR e la converte da sola: passando <code>img1</code> a colori si ottengono gli stessi 19096 keypoint e descrittori identici (verificato). Convertire esplicitamente resta una buona abitudine (chiaro e uguale per tutti i detector). L'osservazione sul colore invece è giusta: lo stesso punto può avere colori diversi fra due scatti per luce e ombre, mentre la struttura dei gradienti è più stabile.</p></div>
<div class="box b"><b>Dal libro · Szeliski cap. 7, § 7.1.1–7.1.2, e L8</b><p>Il visionbook non ha un capitolo sui keypoint: la fonte è Szeliski cap. 7 (detector e descrittori) e l'articolo di Lowe 2004, già riassunti nella L8. Da ricordare per questo lab: il keypoint SIFT è <b>covariante</b> a traslazione, scala e rotazione (porta con sé posizione, scala e angolo), il descrittore è calcolato nella finestra normalizzata e quindi è <b>invariante</b> a queste trasformazioni e, grazie alla normalizzazione, ai cambi affini di luminosità.</p></div>
""", printed=NB + 'celle 6–7')

s(3, "knnMatch e ratio test di Lowe", """
<pre>bf = cv2.BFMatcher(cv2.NORM_L2)               # forza bruta, distanza euclidea
knn = bf.knnMatch(desc1, desc2, k=2)          # per ogni desc1: i 2 più vicini in desc2
matches = []
for m, n in knn:                              # m = 1° vicino, n = 2° vicino
    if m.distance &lt; ratio * n.distance:       # ratio = 0.75
        matches.append(m)
pts1 = np.float64([kps1[m.queryIdx].pt for m in matches])
pts2 = np.float64([kps2[m.trainIdx].pt for m in matches])</pre>
<ul>
<li><b>BFMatcher</b> confronta ogni descrittore della prima immagine (<b>query</b>) con <b>tutti</b> quelli della seconda (<b>train</b>): 19096 × 12804 ≈ 2.4·10<sup>8</sup> distanze in 128 dimensioni, circa 4 s. È il nearest neighbour esaustivo della L9 (slide 11); per insiemi più grandi si usa FLANN (ricerca approssimata).</li>
<li><code>NORM_L2</code> è la distanza giusta per descrittori reali come SIFT (L9, slide 12).</li>
<li><code>knnMatch(..., k=2)</code> restituisce per ogni query una lista dei 2 match migliori in ordine di distanza: servono entrambi per il <b>ratio test</b> (L9, slide 14–15): si tiene il match solo se d<sub>1</sub> &lt; 0.75 · d<sub>2</sub>, cioè se il primo vicino è nettamente migliore del secondo.</li>
<li>Risultato: dei 19096 candidati ne restano <b>3839</b> (20%). Le coordinate dei match finiscono in due array N × 2 <b>allineati</b>: <code>pts1[i]</code> e <code>pts2[i]</code> sono la stessa coppia.</li>
</ul>
<p><b>Quanti match al variare della soglia</b> (verificato sulle stesse due immagini):</p>
<pre>ratio   0.6    0.7    0.75   0.8    0.9    1.0
match   2854   3490   3839   4268   6593   19095</pre>
<div class="box k"><b>Da saper spiegare: perché il rapporto e non una soglia sulla distanza</b><p>La distanza assoluta di un match giusto varia molto da un punto all'altro (dipende da texture, rumore, contrasto), quindi una soglia fissa o taglia match buoni o lascia passare match cattivi. Il secondo vicino invece stima "quanto è vicino un descrittore sbagliato qualsiasi" proprio in quella zona dello spazio dei descrittori: se il primo è molto più vicino, il match è distintivo. Sulle strutture ripetute (finestre, onde) d<sub>1</sub> ≈ d<sub>2</sub> e il test scarta il match, che è proprio il caso ambiguo della L9 (slide 8 e 13).</p></div>
<div class="box b"><b>Dalla fonte · Lowe 2004, § 7.1, e Szeliski § 7.1.3</b><p>Lowe usa la soglia <b>0.8</b> e riporta che elimina circa il 90% dei match sbagliati perdendo meno del 5% di quelli giusti; il notebook è più severo (0.75): meno match, più puliti. In Szeliski (cap. 7, § 7.1.3 Feature matching) lo stesso criterio si chiama <b>NNDR</b>, nearest neighbor distance ratio. Con soglia 1.0 il test non scarta nulla: l'unico match che manca alla colonna "1.0" (19095 su 19096) è un caso di parità esatta d<sub>1</sub> = d<sub>2</sub>.</p></div>
""", printed=NB + 'cella 7')

s(4, "Dentro gli oggetti: KeyPoint e DMatch", """
<pre>pts1[0]          # array([  28.37, 2301.59])
kps1[0].angle, kps1[0].pt, kps1[0].response, kps1[0].size
                 # (22.69, (2.35, 478.26), 0.0195, 1.97)
matches[0].distance, matches[0].queryIdx, matches[0].trainIdx
                 # (163.10, 79, 5091)</pre>
<ul>
<li><b>KeyPoint</b>: <code>pt</code> = posizione (x, y) in pixel, sub-pixel, con x = colonna e y = riga; <code>size</code> = <b>diametro</b> della regione significativa, proporzionale alla scala σ a cui è stato trovato; <code>angle</code> = orientazione dominante in gradi (0–360); <code>response</code> = forza della risposta DoG, utile per tenere i più forti; <code>octave</code> = ottava e livello della piramide, impacchettati in un intero.</li>
<li><b>DMatch</b>: <code>queryIdx</code> = indice in <code>kps1</code>/<code>desc1</code>, <code>trainIdx</code> = indice in <code>kps2</code>/<code>desc2</code>, <code>distance</code> = distanza L2 fra i due descrittori.</li>
<li>Le tre celle non parlano dello stesso punto: <code>pts1[0]</code> è il keypoint del <b>primo match</b>, cioè <code>kps1[79]</code> (queryIdx = 79), non <code>kps1[0]</code>. <code>kps1[0]</code> è un keypoint minuscolo (diametro 2 pixel) sul bordo sinistro, che non ha passato il ratio test (d<sub>1</sub> = 322, d<sub>2</sub> = 330: rapporto 0.97, verificato).</li>
<li>La distanza 163 ha senso solo in relazione alle altre: OpenCV scala i descrittori SIFT normalizzati di un fattore 512 (qui i valori vanno da 0 a 214), quindi le distanze sono dell'ordine delle centinaia.</li>
</ul>
<div class="box x"><b>Approfondimento: le scale dei keypoint</b><p>Il diametro <code>size</code> va da 1.8 a 656 pixel; la mediana è 2.6 e il 90% è sotto 7: la maggior parte dei keypoint SIFT è a scala fine, trovata nelle prime ottave (OpenCV raddoppia l'immagine prima della prima ottava, come suggerisce Lowe). I pochi keypoint grandi descrivono strutture ampie, come le nuvole.</p></div>
""", printed=NB + 'celle 8–10')

s(5, "Disegnare i keypoint", """
<pre>def draw_large_keypoints(img, keypoints, radius_scale=0.5, thickness=2, max_points=None):
    out = img.copy()
    if max_points is not None:     # i più forti per response
        keypoints = sorted(keypoints, key=lambda k: -k.response)[:max_points]
    for kp in keypoints:
        x, y = map(int, kp.pt)
        r = max(3, int(kp.size * radius_scale))
        cv2.circle(out, (x, y), r, (0, 255, 0), thickness, lineType=cv2.LINE_AA)
    return out</pre>
<p><b>Figura:</b> i 5000 keypoint più forti di ciascuna foto, cerchi verdi con raggio proporzionale alla scala. Si concentrano sulla linea dell'orizzonte (edifici, alberi, fortezza), sul sartiame del veliero, sul campanile e sul suo riflesso, sui pezzi di ghiaccio; quasi nessuno sul cielo uniforme e sull'acqua liscia. Qualche cerchio grande sulle nuvole e attorno alla fortezza.</p>
<ul>
<li>È il comportamento atteso di un detector di blob/angoli (L8): servono variazioni di intensità in più direzioni; le zone piatte non hanno keypoint.</li>
<li><code>cv2.drawKeypoints</code> esiste (con il flag <code>DRAW_RICH_KEYPOINTS</code> disegna anche scala e orientazione), ma su foto da 10 megapixel cerchi sottili da 1 pixel sono invisibili una volta ridotta l'immagine: per questo la funzione su misura con spessore 3.</li>
<li>I colori sono in BGR: <code>(0, 255, 0)</code> è verde in entrambi gli ordini, per questo qui non si nota.</li>
</ul>
<div class="box x"><b>Approfondimento: raggio e diametro</b><p><code>kp.size</code> è un diametro, quindi il raggio "vero" della regione è <code>size/2</code>; con <code>radius_scale=0.7</code> i cerchi sono 1.4 volte più grandi della regione. È solo una scelta grafica, ma va tenuto presente se si vuole leggere la scala dalla figura.</p></div>
""", img='img/l10_kps.jpg', printed=NB + 'celle 11–12')

s(6, "Disegnare i match migliori", """
<pre>canvas = np.zeros((max(h1, h2), w1 + w2, 3), dtype=np.uint8)
canvas[:h1, :w1] = img1; canvas[:h2, w1:w1+w2] = img2       # affiancate
matches = sorted(matches, key=lambda m: m.distance)[:max_matches]
for m in matches:
    p1 = tuple(map(int, kps1[m.queryIdx].pt))
    p2 = tuple(map(int, kps2[m.trainIdx].pt))
    p2 = (p2[0] + w1, p2[1])                               # sposta nella metà destra
    cv2.line(canvas, p1, p2, color, line_thickness, lineType=cv2.LINE_AA)</pre>
<p><b>Figura:</b> le due foto affiancate e i 10 match con distanza più piccola. Tutte le linee sono quasi orizzontali e parallele e partono dalla fortezza e dagli alberi sotto il campanile: nella seconda foto gli stessi punti stanno circa 1200 pixel più a sinistra.</p>
<ul>
<li>Le coordinate del punto nella seconda foto vanno <b>traslate di w1</b> perché sulla tela affiancata la seconda immagine comincia alla colonna w1.</li>
<li>Linee parallele e della stessa lunghezza sono il segno visivo di match coerenti con un unico movimento (qui quasi una traslazione orizzontale, la camera che ruota). Un match sbagliato si riconosce come una linea storta o di lunghezza diversa.</li>
<li><code>rng = np.random.default_rng(0)</code> dà un colore casuale ma riproducibile per ogni match.</li>
</ul>
<div class="box w"><b>Attenzione: "distanza piccola" non vuol dire "match più affidabile"</b><p>Il commento dice "the smaller the distance, the better the match". Per scegliere quali disegnare va bene, ma l'affidabilità la misura il <b>rapporto</b> d<sub>1</sub>/d<sub>2</sub>, non d<sub>1</sub> (scheda 3): una distanza piccola può capitare anche su una struttura ripetuta, dove il secondo vicino è altrettanto vicino. Qui i 10 migliori sono tutti giusti perché hanno già passato il ratio test.</p></div>
""", img='img/l10_match10.jpg', printed=NB + 'celle 13–14')

# ---------------------------------------------------------------- RANSAC

s(7, "Normalizzazione dei punti e DLT", """
<p>Il testo del notebook dice che la DLT non è ancora stata spiegata e che interessa solo RANSAC. Nella L9 la DLT c'è (slide 28–29, con la derivazione del libro): qui si vede come diventa codice.</p>
<pre>def normalize_points(pts):
    mean = pts.mean(axis=0)
    std = pts.std(axis=0).mean()           # media delle due deviazioni standard
    s = np.sqrt(2) / std
    T = np.array([[s, 0, -s*mean[0]],
                  [0, s, -s*mean[1]],
                  [0, 0, 1]])              # trasla nel baricentro, poi scala
    ...
def dlt_homography(src_pts, dst_pts):      # H tale che dst ~ H @ src
    src_n, T_src = normalize_points(src_pts)
    dst_n, T_dst = normalize_points(dst_pts)
    A = []
    for (x, y), (u, v) in zip(src_n, dst_n):
        A.append([-x, -y, -1,  0,  0,  0, u*x, u*y, u])
        A.append([ 0,  0,  0, -x, -y, -1, v*x, v*y, v])
    _, _, Vt = np.linalg.svd(np.asarray(A))
    H_n = Vt[-1].reshape(3, 3)             # ultimo vettore singolare destro
    H = np.linalg.inv(T_dst) @ H_n @ T_src # torna alle coordinate in pixel
    return H / H[2, 2]</pre>
<ul>
<li><b>Le righe di A</b> sono quelle della L9 (slide 29) cambiate di segno: da u = (h<sub>1</sub>·p)/(h<sub>3</sub>·p) si moltiplica per il denominatore e si porta tutto da una parte. Il segno non cambia il nucleo di A. Con N coppie, A è <b>2N × 9</b>.</li>
<li><b>Soluzione</b>: il vettore h di norma 1 che minimizza ‖Ah‖ è l'ultima riga di V<sup>T</sup> nella SVD (autovettore di A<sup>T</sup>A con autovalore minimo). Con 4 coppie in posizione generale la soluzione è esatta.</li>
<li><b>Normalizzazione</b>: T sposta il baricentro nell'origine e scala le coordinate a valori dell'ordine di 1; si stima H<sub>n</sub> fra punti normalizzati e si torna indietro con <b>H = T<sub>dst</sub><sup>−1</sup> H<sub>n</sub> T<sub>src</sub></b> (se p<sub>n</sub> = T<sub>src</sub>p e q<sub>n</sub> = H<sub>n</sub>p<sub>n</sub>, allora q = T<sub>dst</sub><sup>−1</sup>H<sub>n</sub>T<sub>src</sub>p).</li>
<li><code>H /= H[2, 2]</code> fissa la scala arbitraria in modo che h<sub>33</sub> = 1 (comodo da leggere; fallisce solo nel caso raro h<sub>33</sub> ≈ 0).</li>
</ul>
<div class="box k"><b>Da saper spiegare: a cosa serve la normalizzazione (numeri verificati)</b><p>In pixel le colonne di A mescolano 1 e termini come u·x ≈ 10<sup>6</sup>–10<sup>7</sup>. Sugli inlier di questo lab il rapporto fra il primo e il penultimo valore singolare di A è <b>1.2·10<sup>8</sup></b> senza normalizzare e <b>22</b> dopo: il sistema diventa ben condizionato. In questo caso, in doppia precisione, la H finale cambia poco (errore medio sugli inlier 0.526 px in entrambi i casi), ma con pochi punti o in precisione singola la differenza si vede: è la ragione per cui Hartley e Zisserman la considerano obbligatoria.</p></div>
<div class="box x"><b>Approfondimento: non è esattamente la normalizzazione di Hartley</b><p>Hartley e Zisserman (cap. 4, "normalized DLT") scalano in modo che la <b>distanza media</b> dall'origine sia √2. Il notebook rende invece √2 la <b>media delle due deviazioni standard</b>. Sugli inlier, che sono sparsi soprattutto in orizzontale (deviazioni standard normalizzate 2.43 in x e 0.40 in y), la distanza media risulta 2.18 invece di 1.41. Non è un errore: lo scopo (coordinate di ordine 1, centrate) è raggiunto e il risultato non cambia.</p></div>
<div class="box b"><b>Dal libro · cap. 41, § 41.3.1 Direct Linear Transform Algorithm</b><p>Il libro scrive il sistema A h = 0 con A di dimensione 2N × 9, prende come soluzione l'autovettore di A<sup>T</sup>A con autovalore minimo e conclude che servono almeno <b>quattro corrispondenze</b> (8 gradi di libertà, 2 equazioni per coppia). Aggiunge che per risultati accurati conviene poi minimizzare l'errore di riproiezione partendo dalla DLT; il notebook si ferma alla DLT. La normalizzazione non è nel libro: è in Hartley e Zisserman, cap. 4. {HOM}</p></div>
""".replace('{HOM}', HOM), sec=("l10-ransac", "Omografia robusta: DLT e RANSAC", 'schede 7–10'), printed=NB + 'celle 15–16')

s(8, "Errore di riproiezione e ciclo RANSAC", """
<pre>def reprojection_errors(H, src_pts, dst_pts):
    src_h = np.column_stack([src_pts, np.ones(len(src_pts))])  # coordinate omogenee
    pred_h = (H @ src_h.T).T
    pred = pred_h[:, :2] / pred_h[:, 2:3]                       # divisione prospettica
    return np.linalg.norm(pred - dst_pts, axis=1)               # distanza in pixel

def ransac_homography(src_pts, dst_pts, num_iters=3000, threshold=4.0):
    for _ in range(num_iters):
        idx = np.random.choice(n, 4, replace=False)    # campione minimo
        try:
            H = dlt_homography(src_pts[idx], dst_pts[idx])
        except np.linalg.LinAlgError:
            continue
        inliers = reprojection_errors(H, src_pts, dst_pts) &lt; threshold
        if inliers.sum() &gt; best_count:                 # tieni il consenso più grande
            best_count, best_inliers, best_H = inliers.sum(), inliers, H
    return dlt_homography(src_pts[best_inliers], dst_pts[best_inliers]), best_inliers

H, inliers = ransac_homography(pts2, pts1)   # H porta i punti di img2 in img1</pre>
<ul>
<li>È esattamente l'algoritmo della L9 (slide 38): <b>campiona</b> 4 coppie (il minimo per 8 gradi di libertà), <b>stima</b> H con la DLT, <b>conta</b> gli inlier, <b>ripeti</b>, poi <b>ristima</b> H con tutti gli inlier del modello migliore.</li>
<li><b>Errore di riproiezione</b>: si porta ogni punto di src con H (coordinate omogenee, prodotto, divisione per la terza componente) e si misura la distanza euclidea in pixel dal punto corrispondente in dst. È l'errore "in un verso" d(q, Hp) della L9 (slide 39), non quello simmetrico.</li>
<li><b>Soglia</b> 4 pixel su foto da 3888 pixel: circa lo 0.1% della larghezza. Gli inlier finali hanno errore medio <b>0.53 px</b> (mediana 0.39).</li>
<li><code>replace=False</code>: le 4 coppie devono essere distinte, come raccomanda anche il libro, altrimenti il campione è degenere.</li>
<li><b>Verso di H</b>: si passa <code>(pts2, pts1)</code>, quindi H va da img2 a img1. È la scelta comoda per lo stitching: img1 resta ferma e si deforma solo img2.</li>
</ul>
<div class="box w"><b>Attenzione: il try/except non intercetta i campioni collineari</b><p>Il commento dice che se i 4 punti sono collineari la DLT "will fail" e il <code>try</code> salta l'iterazione. Verificato: con 4 punti su una retta <code>np.linalg.svd</code> non solleva nessuna eccezione e restituisce una H degenere (rango 1, entrate dell'ordine di 10<sup>16</sup>). L'eccezione arriva solo nel caso estremo di 4 punti <b>identici</b> (deviazione standard 0, divisione per zero, NaN, "SVD did not converge"); su 3000 campioni reali non è mai scattata. Il codice funziona lo stesso perché una H degenere ottiene pochissimi inlier e non vince mai; un controllo esplicito di degenerazione (per esempio sull'area del quadrilatero o sul rango) è la soluzione pulita.</p></div>
<div class="box b"><b>Dal libro · cap. 41, § 41.3.2 Robust Model Fitting</b><p>I passi del libro: scegli a caso un insieme minimo di punti, stima il modello, calcola gli inlier, ripeti N volte, stima il modello finale dagli inlier del consenso più grande. Il libro ricava k = log(1 − p)/log(1 − w<sup>n</sup>) e raccomanda il campionamento <b>senza reinserimento</b> per evitare fit degeneri. {HOM}</p></div>
""".replace('{HOM}', HOM), printed=NB + 'cella 16')

s(9, "Il risultato: H stimata e inlier", """
<pre>print(f"inliers: {inliers.sum()} / {len(inliers)}")   # inliers: 3258 / 3839
inlier_matches = [m for m, keep in zip(matches, inliers) if keep]</pre>
<p><b>Figura:</b> 80 match inlier (i più vicini nello spazio dei descrittori): tutte linee orizzontali e parallele, dalla fortezza, dagli alberi e dal ponte, più una sulle nuvole.</p>
<p><b>H stimata</b> (riesecuzione con <code>np.random.seed(0)</code>, 3259 inlier):</p>
<pre>H = [[ 0.8065   -0.0003   1220.8 ]
     [-0.0629    0.9362     62.3 ]
     [-5.1e-05   2.0e-06     1    ]]</pre>
<ul>
<li><b>3258 inlier su 3839</b> negli output salvati, cioè w ≈ <b>0.85</b>; 581 match del ratio test erano sbagliati. Rieseguendo si ottiene fra 3259 e 3263: RANSAC è casuale e il notebook non fissa il seme.</li>
<li>Lettura di H: la traslazione di <b>1221 pixel</b> in x dice che un punto all'angolo sinistro di img2 cade a 1221 pixel dal bordo sinistro di img1; la sovrapposizione è quindi circa il 69% della larghezza. I termini h<sub>31</sub>, h<sub>32</sub> ≠ 0 sono la parte <b>proiettiva</b>: la camera ha ruotato, e l'immagine 2 si deforma a trapezio (scheda 11).</li>
<li><b>Confronto con OpenCV</b>: <code>cv2.findHomography(pts2, pts1, cv2.RANSAC, 4.0)</code> trova 3241 inlier e una H quasi uguale: sugli inlier le due H differiscono al massimo di 8 pixel, ai quattro angoli di img2 (estrapolando) al massimo di 19.</li>
</ul>
<div class="box k"><b>Da saper fare: quante iterazioni servivano?</b><p>Con w = 0.85, n = 4, p = 0.99: k = log(0.01)/log(1 − 0.85<sup>4</sup>) = −4.61/−0.74 ≈ 6.3, quindi <b>7 iterazioni</b>; il notebook ne fa 3000. Ma 7 è un minimo teorico, non una garanzia di qualità: ripetendo RANSAC con 7 iterazioni su 50 semi la mediana è 2717 inlier e il caso peggiore 770; con 50 iterazioni la mediana sale a 3247. Il motivo: la formula garantisce un campione di soli inlier, ma 4 inlier vicini fra loro e con un po' di rumore danno una H imprecisa lontano dal campione. Per questo in pratica si fanno più iterazioni, o si rifinisce il modello ad ogni miglioramento (LO-RANSAC).</p></div>
<div class="box x"><b>Approfondimento: costo</b><p>3000 iterazioni costano circa 2.8 s, quasi tutti nel ciclo Python della DLT e nel calcolo degli errori su 3839 punti. <code>cv2.findHomography</code> fa lo stesso in millisecondi, adatta il numero di iterazioni alla frazione di inlier trovata e rifinisce H con Levenberg-Marquardt sull'errore in pixel. Con <code>cv2.USAC_MAGSAC</code> trova 3255 inlier.</p></div>
""", img='img/l10_inliers.jpg', printed=NB + 'celle 16–17')

s(10, "Cosa scarta RANSAC: gli outlier", """
<p>Figura aggiunta (non è nel notebook): 40 dei 581 match <b>scartati</b> da RANSAC, scelti a caso, in rosso.</p>
<p><b>Figura:</b> le linee rosse non sono parallele e lunghe uguali come quelle degli inlier: alcune sono oblique (una parte dall'albero del veliero), molte sono quasi orizzontali ma di lunghezza sbagliata, cioè collegano un punto a un dettaglio simile più in là lungo la riva o nei riflessi. La maggior parte parte dall'acqua, sotto la riva.</p>
<ul>
<li>Dove stanno (verificato): <b>484</b> outlier su 581 sono sotto l'orizzonte, nell'acqua; 37 nel cielo. Nell'acqua ci sono riflessi increspati e lastre di ghiaccio molto simili fra loro, che per di più possono spostarsi fra uno scatto e l'altro: descrittori simili in posti diversi, cioè le strutture ripetute della L9 (slide 8).</li>
<li>Quanto sono sbagliati: errore di riproiezione mediano 71 px, il 10% oltre 1800 px; solo 55 sono "quasi giusti" (fra 4 e 20 px), cioè punti che si sono mossi davvero (acqua, nuvole) o localizzati male.</li>
<li>Il 15% di outlier sopravvissuti al ratio test basterebbe a rovinare una stima ai minimi quadrati (L9, slide 33–34): anche un solo match con errore di 1800 px domina la somma dei quadrati. RANSAC non li corregge, li <b>ignora</b>.</li>
</ul>
""", img='img/l10_outliers.jpg', printed=NB + 'figura aggiunta, dati della cella 16')

# ---------------------------------------------------------------- warping e composizione

s(11, "La tela del panorama: dove finiscono gli angoli di img2", """
<pre>corners_img2 = np.float64([[0, 0], [w2, 0], [w2, h2], [0, h2]])
corners_img2_h = np.column_stack([corners_img2, np.ones(4)])
warped = (H @ corners_img2_h.T).T
warped_corners_img2 = warped[:, :2] / warped[:, 2:3]          # angoli di img2 in img1
all_corners = np.vstack([corners_img1, warped_corners_img2])
xmin, ymin = np.floor(all_corners.min(axis=0)).astype(int)
xmax, ymax = np.ceil(all_corners.max(axis=0)).astype(int)
tx, ty = -xmin, -ymin
T = np.array([[1, 0, tx], [0, 1, ty], [0, 0, 1]])            # traslazione
pano_w, pano_h = xmax - xmin, ymax - ymin</pre>
<p><b>Figura</b> (prima figura della cella 20): il contorno di img2 proiettato con H su img1, in verde: il lato sinistro è una retta quasi verticale a x ≈ 1220, il resto esce dall'immagine a destra.</p>
<ul>
<li>Per sapere quanto deve essere grande la tela si proiettano i <b>4 angoli</b> di img2: basta perché un'omografia manda rette in rette, quindi il contorno di img2 diventa un quadrilatero con vertici negli angoli proiettati.</li>
<li>Angoli proiettati (verificati): (1221, 62), (5438, −227), (5402, 2784), (1214, 2476). Il quadrilatero è un <b>trapezio</b>, più alto a destra: è l'effetto dei termini proiettivi di H.</li>
<li>La bounding box di tutti gli angoli (img1 e img2 proiettata) va da (0, −228) a (5438, 2784): tela di <b>5438 × 3012</b> pixel.</li>
<li>Il punto più in alto ha y = −228, fuori dalla tela: la traslazione <b>T</b> con t<sub>y</sub> = 228 sposta tutto in coordinate positive. Comporre T e H (<b>T @ H</b>) dà la mappa da img2 alla tela: le trasformazioni in coordinate omogenee si concatenano con il prodotto di matrici (cap. 38).</li>
</ul>
<div class="box x"><b>Approfondimento: la cella 20 rifà la 19</b><p>La cella 20 ripete gli stessi passi con le funzioni di OpenCV: <code>cv2.perspectiveTransform(corners, H)</code> fa prodotto e divisione prospettica al posto delle tre righe NumPy (vuole un array <code>float32</code> di forma (N, 1, 2)), e <code>cv2.polylines</code> disegna il contorno. Stesso risultato, stessa tela.</p></div>
""", sec=("l10-warp", "Warping e composizione", 'schede 11–14'), img='img/l10_footprint.jpg', printed=NB + 'celle 18–20')

s(12, "warpPerspective: warping inverso sulla tela", """
<pre>warped_img2 = cv2.warpPerspective(img2, T @ H, (pano_w, pano_h))   # dsize = (larghezza, altezza)</pre>
<p><b>Figura:</b> img2 deformata sulla tela da 5438 × 3012: occupa la parte destra; il bordo superiore sale verso destra e quello inferiore scende verso destra, quindi il lato destro è più alto del sinistro. Il resto della tela è nero.</p>
<ul>
<li><code>warpPerspective(src, M, dsize)</code> riempie un'immagine di dimensione <code>dsize</code> = <b>(larghezza, altezza)</b>, attenzione all'ordine opposto a <code>shape</code>.</li>
<li>Internamente fa <b>warping inverso</b> (L9, slide 49): per ogni pixel (x′, y′) della tela calcola M<sup>−1</sup>(x′, y′), il punto di img2 da cui viene, e lo campiona con interpolazione <b>bilineare</b> (default <code>INTER_LINEAR</code>). Per questo non restano buchi. Si passa M "in avanti" (da img2 alla tela) e OpenCV la inverte; con il flag <code>WARP_INVERSE_MAP</code> si passa direttamente l'inversa.</li>
<li>I pixel della tela il cui punto di origine cade fuori da img2 restano a 0 (nero): <code>borderMode=BORDER_CONSTANT</code> di default.</li>
</ul>
<div class="box b"><b>Dal libro · cap. 38, § 38.5 Image Warping</b><p>Il libro confronta forward mapping (si sposta ogni pixel di input: buchi e aliasing) e <b>backward mapping</b>, che considera il metodo migliore: si scorre ogni pixel dell'immagine di destinazione, si applica la trasformazione inversa e si interpola l'input (bilineare, bicubica o Lanczos). È ciò che fa <code>warpPerspective</code>. Nel § 38.3 la gerarchia delle trasformazioni: traslazione 2 gradi di libertà, euclidea 3, similitudine 4, affine 6, proiettiva 8. {HC}</p></div>
""".replace('{HC}', HC), img='img/l10_warped.jpg', printed=NB + 'celle 19–20')

s(13, "Composizione: incollare img1 sulla tela", """
<pre>panorama = warped_img2.copy()
panorama[ty:ty + h1, tx:tx + w1] = img1     # img1 sopra, senza fusione</pre>
<p><b>Figura:</b> il panorama di due foto. A sinistra img1 intera, a destra la parte di img2 che sporge; bande nere triangolari sopra e sotto, dove la tela non è coperta da nessuna delle due. Si vede una <b>linea verticale</b> netta dove finisce img1: a destra il cielo è più scuro e grigio.</p>
<ul>
<li>img1 è il riferimento: in coordinate della tela è solo traslata di (t<sub>x</sub>, t<sub>y</sub>) = (0, 228), quindi basta copiarla con uno slicing. Nella zona di sovrapposizione (6.8 milioni di pixel) img1 <b>sovrascrive</b> img2.</li>
<li>La geometria è giusta: alberi, fortezza e linea dell'orizzonte continuano senza salti attraverso la giunzione. Quello che non torna è la <b>luminosità</b> (scheda 14).</li>
<li>La cella 18 lo dice: come comporre bene "non è stato discusso". È lo step "compose" della L9 (slide 49), qui nella versione più semplice possibile.</li>
</ul>
<div class="box w"><b>Attenzione: il panorama di due immagini viene più alto del necessario e con molto nero</b><p>La tela è la bounding box di tutti gli angoli, quindi contiene anche i triangoli neri dovuti alla prospettiva di img2: circa il <b>10%</b> della tela da 16.4 megapixel non contiene immagine (verificato). Non è un errore, ma per un risultato presentabile si ritaglia il più grande rettangolo interamente coperto. E più immagini si aggiungono con lo stesso riferimento, più le ultime si allungano: per questo il libro (§ 41.3.3) sceglie come riferimento l'immagine <b>centrale</b>, e lo Stitcher proietta su una sfera (scheda 16).</p></div>
""", img='img/l10_pano2.jpg', printed=NB + 'celle 19–20')

s(14, "Perché si vede la giunzione", """
<p>Figura aggiunta: ingrandimento del panorama della scheda 13 attorno al bordo destro di img1 (ritaglio di 1200 × 1200 pixel).</p>
<p><b>Figura:</b> a sinistra della linea il cielo è chiaro e caldo (img1), a destra più scuro e grigio (img2); gli alberi e la riva attraversano la linea senza sdoppiarsi.</p>
<ul>
<li>Le due foto hanno <b>luminosità</b> diversa: nella zona comune img1 ha media 114.5 e img2 98.2 su 255 (in grigio, verificato), cioè img2 è circa il 15% più scura; nel cielo 137 contro 120. Cause tipiche: esposizione automatica diversa fra gli scatti e <b>vignettatura</b>, che scurisce i bordi di ogni foto.</li>
<li>La differenza media in valore assoluto nella sovrapposizione è <b>16.8 livelli</b>, quasi uguale alla differenza delle medie (16.3): è in gran parte uno scarto di luminosità globale, non un errore di allineamento (gli inlier hanno errore sotto il pixel).</li>
<li>Rimedi, dal più semplice (L9, slide 49 e approfondimento): <b>compensazione del guadagno</b> (scalare img2 perché abbia la stessa media di img1 nella sovrapposizione); <b>feathering</b>, media pesata con pesi che scendono verso il bordo di ciascuna immagine; <b>blending multi-banda</b> con le piramidi laplaciane della L6; scelta di una <b>cucitura</b> ottima. Lo Stitcher di OpenCV usa tre di queste (scheda 16).</li>
<li>Provato (Esercizi risolti, n. 4): con il guadagno 1.16 la differenza media nella sovrapposizione scende da 16.4 a 7.4 livelli, e aggiungendo il feathering la linea sparisce.</li>
</ul>
<div class="box b"><b>Dal libro · Szeliski cap. 8, § 8.4 Compositing</b><p>Il visionbook (§ 41.3.3) mostra il panorama finale ma non parla di fusione. Szeliski dedica al compositing un paragrafo: scelta della superficie di proiezione, selezione dei pixel e delle cuciture, pesi di fusione (feathering), blending multi-banda e nel dominio del gradiente, compensazione dell'esposizione. I sottoparagrafi non sono stati verificati online.</p></div>
""", img='img/l10_seam.jpg', printed=NB + 'cella 20, dettaglio')

# ---------------------------------------------------------------- tutto insieme e API ad alto livello

s(15, "Tutto insieme: stitch_two_images", """
<pre>def stitch_two_images(img1, img2):
    pts1, pts2, kps1, kps2, matches = detect_and_match(img1, img2)
    H, inliers = ransac_homography(pts2, pts1)          # img2 -&gt; img1
    ...                                                  # angoli, tela, T
    warped_img2 = cv2.warpPerspective(img2, T @ H, (pano_w, pano_h))
    panorama = warped_img2.copy()
    panorama[ty:ty + h1, tx:tx + w1] = img1
    return panorama, H, inliers, matches, kps1, kps2
# matches: 3839
# inliers: 3260 / 3839</pre>
<ul>
<li>La cella 22 ripete tutte le funzioni (detect_and_match, normalize_points, dlt_homography, reprojection_errors, ransac_homography) e le chiude in una funzione unica: è la versione da tenere come riferimento per gli esercizi.</li>
<li>Stessi match (3839: SIFT e il matcher a forza bruta sono deterministici), inlier diversi di poco (3260 contro 3258): è solo il seme casuale di RANSAC. Per risultati riproducibili si chiama <code>np.random.seed(0)</code> prima, o meglio si passa un <code>np.random.default_rng(seed)</code> alla funzione.</li>
<li>Il panorama è lo stesso della scheda 13.</li>
</ul>
<div class="box k"><b>Da saper fare: la pipeline in 6 righe</b><p>1) keypoint e descrittori (SIFT); 2) per ogni descrittore i 2 vicini più prossimi; 3) ratio test (e volendo mutual NN); 4) RANSAC con DLT su 4 coppie e soglia in pixel, ristima sugli inlier; 5) proiezione degli angoli, tela e traslazione T; 6) warping inverso con T·H e composizione. Ogni passo corrisponde a una parte della L8 o della L9: saper dire quale.</p></div>
""", sec=("l10-api", "Tutto insieme e Stitcher di OpenCV", 'schede 15–17'), printed=NB + 'celle 21–22')

s(16, "Lo Stitcher di OpenCV su sei foto", """
<pre>stitcher = cv2.Stitcher_create(cv2.Stitcher_PANORAMA)   # o cv2.Stitcher_SCANS
status, pano = stitcher.stitch(imgs)                   # lista di 6 immagini BGR
if status != cv2.Stitcher_OK: ...                       # codice di errore</pre>
<p><b>Figura:</b> il panorama delle 6 foto, 10722 × 2663 pixel (11.6 s): tutto il fiume, dal veliero a sinistra ai palazzi della riva opposta e alla punta dell'isola a destra. Bordi curvi (proiezione sferica), orizzonte dritto, nessuna giunzione visibile nel cielo.</p>
<ul>
<li><b>Cosa fa dentro</b> in modalità PANORAMA (codice sorgente di OpenCV 4.x): keypoint e descrittori <b>ORB</b> (non SIFT), matching "best of 2 nearest" con ratio test, stima delle camere da omografie, <b>bundle adjustment</b> che rifinisce insieme rotazioni e focali di tutte le camere, <b>wave correction</b> (raddrizza l'orizzonte), proiezione <b>sferica</b>, compensazione dell'esposizione a blocchi, ricerca della cucitura con <b>graph cut</b>, <b>blending multi-banda</b>. Per velocità registra le immagini a 0.6 megapixel e cerca le cuciture a 0.1, poi compone a risoluzione piena.</li>
<li>Rispetto al lavoro a mano: stessa idea (feature, match, modello robusto, warping), ma con un modello di <b>camera</b> (K e R per ogni foto) invece di una H per coppia, ottimizzazione globale e composizione vera.</li>
<li><code>d3=True</code> nel notebook taglia ogni foto in tre fette sovrapposte: più immagini piccole, più facile trovare match quando le foto sono poche. <code>mode="scans"</code> attiva il modello affine (scheda 17).</li>
<li>Con due foto (boat1, boat2) lo Stitcher dà 4800 × 2543; con boat1 e boat6, che non si sovrappongono, restituisce status 1 = <code>ERR_NEED_MORE_IMGS</code>.</li>
</ul>
<div class="box w"><b>Attenzione: se lo stitching fallisce, la cella va in errore</b><p><code>main</code> in caso di errore stampa il messaggio e fa <code>return 1</code>; la riga dopo chiama <code>cv2.cvtColor(pano, ...)</code> con <code>pano = 1</code> e OpenCV solleva un'eccezione poco leggibile. Verificato passando due foto senza sovrapposizione. Meglio restituire <code>None</code> e controllare prima di disegnare, oppure sollevare un'eccezione con il codice di stato. Inoltre <code>plt.imshow</code> senza <code>plt.figure(figsize=...)</code> mostra un panorama da 10722 pixel in una figura 6.4 × 4.8 pollici: si vede piccolissimo, con gli assi in pixel.</p></div>
<div class="box b"><b>Dal libro · cap. 41, § 41.3.3 Image Stitching, e Szeliski cap. 8</b><p>Il libro allinea tutte le immagini a un'immagine di riferimento (quella centrale) con le omografie stimate a coppie e le deforma in un'unica vista (fig. 41.9). Lo Stitcher fa un passo in più, descritto da Szeliski nel cap. 8 (§ 8.2 Image stitching e § 8.3 Global alignment): modello di rotazione per ogni camera, bundle adjustment, proiezioni cilindriche o sferiche, compositing. {HOM}</p></div>
""".replace('{HOM}', HOM), img='img/l10_stitch_panorama.jpg', printed=NB + 'celle 23–24')

s(17, "Esercizi del notebook", """
<p>La cella 25 propone quattro attività. Soluzioni con codice e numeri nella sezione "Esercizi risolti" in fondo alla pagina; qui i risultati in breve.</p>
<ul>
<li><b>Documentazione</b> di SIFT e della classe Stitcher: in particolare i parametri di <code>SIFT_create</code> (<code>nfeatures</code>, <code>contrastThreshold</code>, <code>edgeThreshold</code>, <code>sigma</code>) e i "setter" dello Stitcher (<code>setRegistrationResol</code>, <code>setPanoConfidenceThresh</code>, <code>setWaveCorrection</code>).</li>
<li><b>Mutual nearest neighbours</b> dopo il ratio test: da 3839 a <b>3738</b> match; RANSAC (<code>findHomography</code>) trova 3222 inlier invece di 3241, la frazione di inlier sale dall'84.4% all'<b>86.2%</b>. Toglie soprattutto outlier.</li>
<li><b>Stitcher affine</b> (<code>Stitcher_SCANS</code>, in figura): 10970 × 2856 in 4.2 s. Nessuna proiezione sferica e nessuna compensazione dell'esposizione: bordi a gradini, bande di luminosità diversa nel cielo e nell'acqua, giunzioni visibili. Il modello affine è adatto a scansioni di documenti piatti, non a una camera che ruota.</li>
<li><b>ORB</b> con <code>NORM_HAMMING</code>: con 5000 keypoint 811 match dopo il ratio test, 746 inlier, H entro 11 pixel da quella di SIFT agli angoli; 25 volte più veloce di SIFT nell'estrazione.</li>
</ul>
<div class="box w"><b>Attenzione: per ORB la norma giusta è NORM_HAMMING, non NORM_HAMMING2</b><p>Il notebook dice che ORB "requires Hamming distance NORM_HAMMING2". La documentazione di OpenCV dice che <code>NORM_HAMMING</code> va usata con ORB, BRISK e BRIEF, e <code>NORM_HAMMING2</code> solo con ORB creato con <code>WTA_K</code> = 3 o 4 (ogni elemento del descrittore occupa 2 bit). Con il default <code>WTA_K = 2</code> la norma corretta è <code>NORM_HAMMING</code>. Verificato: HAMMING2 funziona lo stesso perché conta coppie di bit diverse (742 match, 694 inlier), ma è una distanza diversa da quella per cui il descrittore è progettato. Inoltre SURF non è in <code>opencv-python</code>: è brevettato e sta nei moduli "nonfree" di <code>opencv-contrib</code>, da compilare a parte. E i due link "C++ tutorial" e "OpenCV extra samples" puntano alla stessa pagina (i dati di test), non a un tutorial.</p></div>
""", img='img/l10_stitch_scans.jpg', printed=NB + 'cella 25')
