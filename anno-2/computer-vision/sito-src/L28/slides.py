VB = 'https://visionbook.mit.edu/'
def L(slug, txt): return f'<a href="{VB}{slug}" target="_blank">{txt}</a>'
LK = {
 '{C37}': L('transfer_learning.html', 'cap. 37'),
 '{C34}': L('conditional_generative_models.html', 'cap. 34'),
 '{C51}': L('VLMs.html', 'cap. 51'),
 '{C32}': L('generative_models.html', 'cap. 32'),
 '{C31}': L('perceptual_organization.html', 'cap. 31'),
 '{C14}': L('backpropagation.html', 'cap. 14'),
 '{C26}': L('transformers.html', 'cap. 26'),
}
def P(n): return f' <em>· pag. {n}/62</em>'
def R(t):
    for k, v in LK.items(): t = t.replace(k, v)
    return t

# ===================== INTRODUZIONE =====================

s(1, "Personalized Diffusion Models: copertina", R("""
<p>Lezione del 19 novembre 2026, ancora di <b>Donald Shenaj</b>, il seguito diretto della <a href="#L27">L27</a> (modelli di diffusione) e della <a href="#L25">L25</a> (PEFT e LoRA). Tema: <b>personalizzare</b> un modello di diffusione testo-immagine, cioè fargli generare <i>quel</i> soggetto preciso (il tuo cane, una persona, un oggetto, uno stile) in scene nuove, partendo da poche foto.</p>
<p>Il PDF ha 62 pagine e il footer stampa «n / 62» con n = pagina del PDF, copertina compresa. Le divisorie (3, 21, 27, 39, 50, 53) non hanno footer. La pag. 62 è la panoramica delle miniature.</p>
<div class="box k"><b>Il filo della lezione in una frase</b><p>Per insegnare un soggetto nuovo si può ottimizzare qualcosa per ogni soggetto (un vettore di testo, tutti i pesi, o solo un LoRA), oppure addestrare una volta sola un modulo che legge direttamente una foto di riferimento; il problema di fondo è sempre lo stesso: <b>fedeltà al soggetto</b> contro <b>libertà del prompt</b>, senza rovinare ciò che il modello sapeva già.</p></div>
"""), sec=("l28-intro", "Introduzione", "slide 1–2"), printed=P(1))

s(2, "Lecture Outline", R("""
<p>Sei parti:</p>
<ol>
<li><b>Optimization-Based Personalization</b>: Textual Inversion, DreamBooth, LoRA, HyperDreamBooth. Slide 3–20.</li>
<li><b>Personalization Without Per-Subject Fine-Tuning</b>: Cross-Image Attention, IP-Adapter. Slide 21–26.</li>
<li><b>Evaluation and Compositionality</b>: metriche, fusione di LoRA (ZipLoRA, B-LoRA), metriche che si possono ingannare, giudici multimodali. Slide 27–38.</li>
<li><b>Extensions: Controlled and Video Generation</b>: ControlNet, OminiControl, AnimateDiff, MotionLoRA. Slide 39–49.</li>
<li><b>Limitations and Open Problems</b>. Slide 50–52.</li>
<li><b>Other Ways to Adapt Generation</b>: ottimizzare il rumore iniziale, Noise Hypernetworks. Slide 53–62.</li>
</ol>
"""), printed=P(2))

# ===================== PARTE 1 =====================

s(3, "Optimization-Based Personalization", R("""<p>Divisoria della prima parte: metodi che ottimizzano qualcosa per ogni nuovo soggetto.</p>"""),
  kind='div', sec=("l28-ottim", "Parte 1 · Personalizzazione con ottimizzazione per soggetto", "slide 3–20"), printed='')

s(4, "Personalized Image Generation", R("""
<p><b>Il problema</b>: dato un piccolo insieme di <b>foto di riferimento</b> (3–10) di un soggetto specifico (persona, oggetto, stile), generare immagini nuove di <i>proprio quel</i> soggetto in contesti, pose e stili nuovi, guidate dal testo.</p>
<p>Perché è difficile:</p>
<ul>
<li>il modello preaddestrato non ha mai visto <i>il tuo</i> cane;</li>
<li>le parole del prompt («dog») indicano una <b>classe</b>, non un <b>individuo</b>: «un corgi» genera un corgi qualunque;</li>
<li>bisogna <b>iniettare</b> l'identità nuova senza distruggere la conoscenza generale del modello.</li>
</ul>
<p>La figura (Ruiz et al., DreamBooth): a sinistra quattro foto di un corgi su sfondo arancione; a destra lo stesso cane sull'Acropoli, che nuota, che dorme, in una cuccia, in un secchio, dal parrucchiere.</p>
"""), sec=None, printed=P(4))

s(5, "Personalization: The Generalization Problem", R("""
<ul>
<li>Poche foto <b>non coprono</b> punti di vista, sfondi e stili nuovi: il modello deve inventare ciò che non ha visto.</li>
<li>Aggiornare il denoiser può <b>cambiare il significato</b> della parola di classe («dog» comincia a voler dire «quel cane»).</li>
<li>Adattarsi troppo alle foto riduce l'<b>editabilità</b>: il modello continua a riprodurre la posa e lo sfondo delle foto invece di seguire il prompt.</li>
</ul>
<span class="f">fedeltà al soggetto  contro  editabilità del prompt</span>
<p>Per questo i metodi si valutano con <b>prompt assenti dal training</b>: è il test di generalizzazione, come il test set in classificazione.</p>
<p>La figura: in alto la sveglia gialla di riferimento e un metodo guidato dall'immagine (DALL-E 2) che cambia il contesto ma perde la sveglia (croce rossa sulla fedeltà); in basso un metodo guidato dal testo (Imagen) che sbaglia i dettagli, e DreamBooth che tiene entrambi (spunte verdi).</p>
<div class="box b"><b>Dal libro · {C37}, § 37.3.1</b><p>Il libro dà la motivazione generale: quando si adatta un modello preaddestrato, a volte si congelano parti della rete proprio per <b>non dimenticare</b> ciò che sapeva prima. È il problema che qui prende il nome di language drift e che DreamBooth combatte con la prior preservation.</p></div>
"""), printed=P(5))

s(6, "Textual Inversion", R("""
<p><b>Idea</b> (Gal et al., 2022): imparare un <b>nuovo vettore di embedding</b> v* per un token nuovo S* che rappresenta il soggetto, senza toccare il modello di diffusione.</p>
<p>Addestramento:</p>
<ol>
<li>si aggiunge al vocabolario un token S* con embedding v* (una riga nuova nella tabella degli embedding dell'encoder di testo);</li>
<li>si congelano U-Net ed encoder di testo;</li>
<li>si ottimizza solo v* con la loss di diffusione, usando prompt come «A photo of S*»:</li>
</ol>
<span class="f">v* = arg min<sub>v</sub> 𝔼<sub>x<sub>0</sub>, t, ε</sub> ‖ε − ε<sub>θ<sub>0</sub></sub>(z<sub>t</sub>, t, c(v))‖<sub>2</sub><sup>2</sup></span>
<p>c(v) è l'uscita dell'encoder di testo quando il prompt contiene S* con embedding v; θ<sub>0</sub> sono i pesi congelati. È la loss della <a href="#L27">L27</a>, ma il gradiente scorre attraverso U-Net ed encoder fino a un solo vettore.</p>
<p>Dopo il training si usa S* in un prompt qualunque: «a photo of S* on the beach».</p>
<ul>
<li>Pro: si addestra un solo vettore (768 numeri in Stable Diffusion v1), facile da salvare e condividere.</li>
<li>Contro: <b>capacità limitata</b> (il modello deve saper già disegnare qualcosa di simile) e un'ottimizzazione per ogni nuovo concetto.</li>
</ul>
<p>La figura: il prompt passa dal tokenizer; il token S* (indice 508 nella figura) ha un embedding v* da imparare; tutto il resto (encoder di testo, generatore) è col lucchetto.</p>
<div class="box b"><b>Dal libro · {C37}, § 37.5 Prompting</b><p>Il libro definisce il prompting come modificare l'<b>ingresso</b> invece del modello, e mostra prompt fatti di pixel ottimizzati. Textual Inversion è proprio questo, nello spazio degli embedding del testo: un prompt ottimizzato con il gradiente, con il modello fermo. Lo stesso spirito del prompt tuning della <a href="#L25">L25</a>.</p></div>
"""), printed=P(6))

s(7, "DreamBooth", R("""
<p><b>Idea</b> (Ruiz et al., 2023): fare il <b>fine-tuning dell'intero modello</b> di diffusione (o della sola U-Net) su 3–5 foto del soggetto, legandolo a un <b>identificatore raro</b> [V], un token che il modello usa pochissimo e che quindi non ha un significato forte da sovrascrivere.</p>
<p>Due loss:</p>
<ol>
<li><b>ricostruzione</b> sulle foto del soggetto con il prompt «a [V] dog»: impara il soggetto;</li>
<li><b>prior preservation</b>: immagini della classe («a dog»), generate dal modello stesso prima del fine-tuning, incluse nel training per evitare il <b>language drift</b> (la parola «dog» cambia significato) e la dimenticanza catastrofica.</li>
</ol>
<span class="f">ℒ = ℒ<sub>subject</sub> + λ ℒ<sub>prior</sub></span>
<p>Proprietà: alta fedeltà al soggetto, prompt componibili liberamente; ma il fine-tuning completo produce un <b>file grande</b> (una copia del modello per soggetto).</p>
<p>La figura: in alto la loss di ricostruzione sulle foto con «A [V] dog»; in basso la loss di classe su immagini generate dal modello congelato (in rosso) con «A dog»; i due modelli gialli condividono i pesi.</p>
"""), printed=P(7))

s(8, "DreamBooth: Prior-Preservation Objective", R("""
<p>La loss di <b>istanza</b> ricostruisce il soggetto:</p>
<span class="f">ℒ<sub>inst</sub> = 𝔼<sub>x∈𝒟<sub>s</sub>, t, ε</sub> ‖ε − ε<sub>θ</sub>(z<sub>t</sub>, t, c<sub>inst</sub>)‖<sub>2</sub><sup>2</sup></span>
<p>La loss di <b>classe</b> conserva la distribuzione preaddestrata della classe:</p>
<span class="f">ℒ<sub>prior</sub> = 𝔼<sub>x̃∼p<sub>θ<sub>0</sub></sub>(·|c<sub>class</sub>), t, ε</sub> ‖ε − ε<sub>θ</sub>(z̃<sub>t</sub>, t, c<sub>class</sub>)‖<sub>2</sub><sup>2</sup></span>
<span class="f">ℒ<sub>DB</sub> = ℒ<sub>inst</sub> + λ ℒ<sub>prior</sub></span>
<ul>
<li>𝒟<sub>s</sub> sono le foto del soggetto; x̃ sono immagini <b>generate dal modello originale</b> θ<sub>0</sub> con il prompt di classe, z̃<sub>t</sub> la loro versione rumorosa.</li>
<li>λ regola la forza della regolarizzazione.</li>
<li>Senza il termine di classe, il fine-tuning può far diventare «dog» sinonimo del cane di riferimento.</li>
</ul>
<div class="box k"><b>Da saper fare: perché funziona</b><p>Il modello impara a fare due cose insieme: con «a [V] dog» riprodurre il soggetto, con «a dog» continuare a fare ciò che faceva prima. Le immagini di classe sono un'«autodistillazione»: il modello imita sé stesso com'era, così i pesi condivisi non possono scivolare tutti verso il soggetto. È una regolarizzazione verso il modello di partenza, come la distillazione del <a href="#L22">L22</a>, ma fatta sulle uscite generate.</p></div>
"""), printed=P(8))

s(9, "DreamBooth: Instance and Class Prompts", R("""
<ul>
<li>Prompt di istanza: «a [V] dog»; prompt di classe: «a dog».</li>
<li>Si fa il fine-tuning del denoiser sulle foto del soggetto.</li>
<li>Un modello <b>congelato</b> genera gli esempi di classe per la prior preservation.</li>
</ul>
<span class="f">𝒟<sub>inst</sub> = {(x<sub>i</sub>, c<sub>inst</sub>)},   𝒟<sub>class</sub> = {(x̃<sub>j</sub>, c<sub>class</sub>)}</span>
<p>Si allena su due insiemi di coppie (immagine, prompt): poche foto vere col prompt di istanza, e tante immagini generate col prompt di classe. In pratica le immagini di classe si generano di solito <b>una volta sola prima</b> del fine-tuning (qualche centinaio), non a ogni passo.</p>
<p>Nota sul nome [V]: si sceglie un token raro del tokenizer (in pratica sequenze come «sks»), perché una parola comune porterebbe con sé un significato che il modello dovrebbe prima disimparare.</p>
"""), printed=P(9))

s(10, "DreamBooth: Prior Preservation Ablation", R("""
<p>L'esperimento decisivo. Tre righe di immagini generate con il prompt «A dog»:</p>
<ul>
<li><b>modello originale</b>: razze diverse (border collie, husky, golden, pastore);</li>
<li><b>fine-tuning senza ℒ<sub>prior</sub></b>: la classe <b>collassa</b> sul soggetto, ogni «dog» è il corgi di riferimento;</li>
<li><b>con la prior preservation</b>: «a dog» torna vario, mentre «a [V] dog» riproduce ancora il soggetto.</li>
</ul>
<p>Questo è il <b>language drift</b> reso visibile: senza regolarizzazione il fine-tuning non insegna solo «[V] = questo cane», insegna anche «dog = questo cane», perché i pesi che producono la classe sono gli stessi.</p>
"""), printed=P(10))

s(11, "DreamBooth: Qualitative Results", R("""
<p>Da 3–5 foto casuali DreamBooth permette:</p>
<ul>
<li><b>viste nuove</b> (il gatto visto dall'alto, dal basso, da dietro: viste mai fotografate);</li>
<li><b>rifacimenti artistici</b> (il cane alla Van Gogh, in marmo alla Michelangelo, alla Vermeer);</li>
<li><b>modifiche di proprietà</b> (il chow chow trasformato in panda, leone, ippopotamo, tenendo i tratti del viso).</li>
</ul>
<p>L'identità del soggetto resta riconoscibile anche con cambi forti di contesto e stile. Le viste nuove sono la prova che il modello non sta copiando le foto: usa ciò che sa della classe «gatto» per completare.</p>
"""), printed=P(11))

s(12, "DreamBooth: More Qualitative Results", R("""
<ul>
<li><b>Accessorization</b> (sinistra): il chow chow con vestiti e accessori nuovi (cuoco, strega, supereroe, angelo), mentre il prompt decide la scena.</li>
<li><b>Recontextualization</b> (destra): lo zaino rosa e la teiera in luoghi, luci e condizioni nuove (Grand Canyon, cielo notturno, Versailles, in acqua; la teiera che galleggia nel mare o nel latte, che versa il tè).</li>
</ul>
<p>Identità coerente, contesto flessibile: è esattamente il compromesso della slide 5 risolto bene.</p>
"""), printed=P(12))

s(13, "Example: Generating a Comic with a Consistent Character", R("""
<p>Un'applicazione: da quattro disegni di un mostriciattolo rosso (a sinistra) si genera un fumetto (a destra) in cui il personaggio resta <b>lo stesso</b> in ogni vignetta: mangia, guarda la TV, corre, scrive «Oh no!». L'ultima vignetta («Not like this...») lo mostra blu, cioè con una proprietà cambiata dal prompt.</p>
<p>La coerenza del personaggio fra immagini diverse è ciò che un modello testo-immagine normale non sa fare: con lo stesso prompt genera ogni volta un mostro diverso.</p>
"""), printed=P(13))

s(14, "Textual Inversion vs. DreamBooth: Qualitative Comparison", R("""
<p>Stesso vaso rosso di riferimento, stessi prompt (neve, spiaggia, foresta, Torre Eiffel), tre metodi:</p>
<ul>
<li><b>DreamBooth</b> (con Imagen e con Stable Diffusion) tiene la forma e il colore esatti del vaso;</li>
<li><b>Textual Inversion</b> (Stable Diffusion) prende lo stile generale (rosso, ramoscelli) ma perde i dettagli: escono vasi diversi, più arancioni.</li>
</ul>
<p>Spiegazione: un solo vettore di embedding ha <b>capacità limitata</b>. Può solo indicare un punto dello spazio dei testi che il modello conosce già; se quel vaso preciso non è esprimibile come «parola» per il modello congelato, nessun vettore lo rappresenta. DreamBooth invece cambia i pesi, quindi può imparare davvero qualcosa di nuovo.</p>
"""), printed=P(14))

s(15, "DreamBooth: Failure Modes", R("""
<ul>
<li><b>Sintesi sbagliata del contesto</b>: prompt rari o difficili («on the moon», «in the ISS») escono male, perché anche il modello originale li genera male (il limite è il prior, non la personalizzazione).</li>
<li><b>Intreccio contesto-aspetto</b>: colore o texture del soggetto cambiano con il contesto (lo zaino diventa marrone nel deserto di sale, blu sul tessuto blu).</li>
<li><b>Overfitting</b>: se il contesto richiesto somiglia agli sfondi delle foto (la foresta), il modello riproduce la posa e la scena originali.</li>
</ul>
<p>Questi difetti motivano i metodi più leggeri, veloci e controllabili delle slide successive.</p>
"""), printed=P(15))

s(16, "LoRA for Personalized Image Generation", R("""
<p>LoRA (<a href="#L25">L25</a>) applicato alla U-Net o al DiT:</p>
<ul>
<li>si congela W<sub>0</sub> e si aggiunge un ramo a basso rango ΔW = BA, con r ≪ d;</li>
<li>si applica alle proiezioni dell'attenzione W<sub>Q</sub>, W<sub>K</sub>, W<sub>V</sub>, W<sub>O</sub>;</li>
<li>in inferenza W = W<sub>0</sub> + (α/r) BA.</li>
</ul>
<p>Perché è ideale per la personalizzazione:</p>
<ul>
<li><b>molto più piccolo</b> di un fine-tuning completo (MB invece di GB);</li>
<li><b>componibile</b>: più LoRA si possono sommare o fondere (soggetto + stile, slide 30);</li>
<li>supportato ovunque (diffusers, AUTOMATIC1111, ComfyUI).</li>
</ul>
<p><b>La ricetta standard</b>: <b>DreamBooth + LoRA</b>, cioè lo stesso addestramento di DreamBooth (stesse loss, stesso [V]) ma ottimizzando solo i parametri LoRA. Risultato: un adattatore piccolo e condivisibile per soggetto.</p>
<p>La figura è quella di LoRA: pesi preaddestrati in blu, A inizializzata gaussiana 𝒩(0, σ<sup>2</sup>), B = 0, quindi all'inizio il modello è esattamente quello originale.</p>
"""), printed=P(16))

s(17, "Textual Inversion vs. DreamBooth", R("""
<p>θ<sub>0</sub> è il denoiser preaddestrato. I tre problemi di ottimizzazione:</p>
<ul>
<li>Textual Inversion: min<sub>v*</sub> ℒ<sub>diff</sub>(θ<sub>0</sub>, v*);</li>
<li>DreamBooth: min<sub>θ</sub> ℒ<sub>inst</sub>(θ) + λ ℒ<sub>prior</sub>(θ);</li>
<li>DreamBooth + LoRA: min<sub>A,B</sub> ℒ<sub>inst</sub>(θ<sub>0</sub>, BA) + λ ℒ<sub>prior</sub>(θ<sub>0</sub>, BA).</li>
</ul>
<table>
<tr><th></th><th>Textual Inversion</th><th>DreamBooth</th><th>DreamBooth + LoRA</th></tr>
<tr><td>Parametri addestrati</td><td>v*</td><td>θ</td><td>A, B</td></tr>
<tr><td>Spazio per soggetto</td><td>bassissimo</td><td>alto</td><td>basso</td></tr>
<tr><td>Fedeltà al soggetto</td><td>moderata</td><td>alta</td><td>alta</td></tr>
<tr><td>Training per soggetto</td><td>sì</td><td>sì</td><td>sì</td></tr>
</table>
<p>Tutti e tre ottimizzano parametri per ogni soggetto nuovo. LoRA riduce i parametri addestrabili mantenendo l'obiettivo di DreamBooth.</p>
<div class="box k"><b>Da saper fare</b><p>Collocare ogni metodo su due assi: <b>dove</b> si interviene (ingresso di testo, pesi, ramo a basso rango) e <b>quanto</b> costa salvarlo. Textual Inversion: 768 numeri. LoRA rango 1 su SD: 386 mila numeri, 1,6 MB (slide 19). DreamBooth su SD 1.5: la U-Net intera, 860 milioni di parametri, circa 1,7 GB in FP16.</p></div>
"""), printed=P(17))

s(18, "HyperDreamBooth: Fast Face Personalization", R("""
<p>Obiettivo (Ruiz et al., 2024): personalizzare da <b>una sola foto di un viso</b>, in fretta.</p>
<ul>
<li><b>Offline</b> (fase 1, su larga scala): per molte identità di training si ottimizza un piccolo adattatore; poi si addestra un'<b>iperrete</b> (hypernetwork) che, data una foto, <b>prevede i pesi</b> dell'adattatore.</li>
<li><b>Identità nuova</b> (fase 2): l'iperrete prevede i pesi in un solo passaggio in avanti; facoltativamente li si rifinisce con un breve fine-tuning per una fedeltà maggiore.</li>
<li>Il backbone di diffusione resta congelato.</li>
</ul>
<p>Il cambio di prospettiva: invece di risolvere un problema di ottimizzazione per ogni persona, si <b>impara a risolverlo</b> una volta per tutte (si «ammortizza» l'ottimizzazione).</p>
<div class="box b"><b>Dal libro · {C14}, § 14.6.5</b><p>Il libro usa il termine <b>hypernetwork</b> per una rete le cui uscite fanno da parametri di un'altra rete (lo nota a proposito della rete «all'indietro» della backpropagation). HyperDreamBooth ne è un esempio: l'uscita dell'iperrete sono i pesi LoRA del denoiser.</p></div>
"""), printed=P(18))

s(19, "HyperDreamBooth: Lightweight DreamBooth", R("""
<p>Un LoRA normale è un aggiornamento a basso rango. <b>LiDB</b> (Lightweight DreamBooth) parte dal rango uno:</p>
<span class="f">ΔW = b a<sup>⊤</sup></span>
<p>e comprime ancora usando <b>basi casuali fisse</b>:</p>
<span class="f">b = U b̃,   a = V ã,   ΔW = U b̃ ã<sup>⊤</sup> V<sup>⊤</sup></span>
<ul>
<li>U, V: basi fisse ortogonalizzate (casuali, mai addestrate, uguali per tutti i soggetti);</li>
<li>b̃, ã: coefficienti specifici del soggetto, molto corti;</li>
<li>l'iperrete prevede questi pochi coefficienti, non tutto il denoiser.</li>
</ul>
<p>La figura confronta: LoRA DreamBooth con r = 1 ha 386 mila variabili (1,6 MB); LiDB con a = 100 e b = 50 ha 28 mila variabili (120 KB). Le matrici «Aux» col lucchetto sono U e V, quelle «Train» i coefficienti.</p>
<div class="box k"><b>Da saper fare</b><p>Per una matrice d<sub>out</sub> × d<sub>in</sub>: LoRA di rango 1 addestra d<sub>out</sub> + d<sub>in</sub> numeri; LiDB ne addestra a + b, indipendentemente dalle dimensioni della matrice. Il rango resta 1, ma la direzione dell'aggiornamento è vincolata al sottospazio generato da U e V. È la stessa idea di VeRA (<a href="#L25">L25</a>): matrici casuali condivise e pochi coefficienti propri.</p></div>
"""), printed=P(19))

s(20, "HyperDreamBooth: Training and Inference", R("""
<p><b>Offline: addestrare l'iperrete.</b></p>
<ul>
<li>Si precalcolano i pesi LiDB ottimizzati ϕ<sub>i</sub>* per molte identità.</li>
<li>Si prevedono i pesi da una foto del viso: ϕ̂<sub>i</sub> = H<sub>ψ</sub>(E<sub>face</sub>(x<sub>i</sub>)), con E<sub>face</sub> un encoder di visi e H<sub>ψ</sub> l'iperrete (un transformer decoder che produce i pesi strato per strato).</li>
<li>Si ottimizzano i parametri ψ con</li>
</ul>
<span class="f">ℒ<sub>hyper</sub> = ℒ<sub>recon</sub> + λ ‖ϕ̂<sub>i</sub> − ϕ<sub>i</sub>*‖<sub>2</sub><sup>2</sup></span>
<p>cioè: i pesi previsti devono far ricostruire bene la foto (ℒ<sub>recon</sub>, la loss di diffusione) ed essere vicini a quelli trovati ottimizzando (regolarizzazione sui pesi).</p>
<p><b>Test: identità nuova.</b></p>
<ul>
<li>Si prevede l'adattatore senza ottimizzazione: ϕ<sup>(0)</sup> = H<sub>ψ</sub>(E<sub>face</sub>(x<sub>new</sub>)).</li>
<li>Facoltativo: lo si rifinisce con la loss di diffusione per circa 40 passi.</li>
</ul>
<p>La predizione dà un ottimo punto di partenza, il breve fine-tuning recupera i dettagli dell'identità.</p>
"""), printed=P(20))

# ===================== PARTE 2 =====================

s(21, "Personalization Without Per-Subject Fine-Tuning", R("""<p>Divisoria della seconda parte: personalizzare senza ottimizzare nulla per il singolo soggetto.</p>"""),
  kind='div', sec=("l28-senza", "Parte 2 · Senza fine-tuning per soggetto", "slide 21–26"), printed='')

s(22, "Semantic Correspondence in Attention Features", R("""
<ul>
<li>I metodi visti finora richiedono un'ottimizzazione per ogni soggetto (embedding, pesi, LoRA).</li>
<li>Le feature di attenzione dei modelli di diffusione codificano <b>corrispondenze semantiche</b> fra immagini diverse.</li>
<li>Oggetti simili condividono feature di attenzione anche se hanno aspetto diverso.</li>
<li>Queste corrispondenze permettono un <b>trasferimento di aspetto senza addestramento</b>.</li>
</ul>
<p>La figura: linee rosse collegano parti corrispondenti di una giraffa e di una zebra (testa con testa, zampe con zampe). Sono le stesse corrispondenze che si cercavano a mano con SIFT nella <a href="#L8">L8</a>–<a href="#L9">L9</a>, ma fra oggetti diversi: è corrispondenza <i>semantica</i>, non geometrica.</p>
<div class="box b"><b>Dal libro · {C31}, § 31.3.2</b><p>Il libro mostra che le feature dense di un modello autosupervisionato (DINO) raggruppano parti con lo stesso significato anche in immagini diverse. È lo stesso fenomeno: le reti grandi imparano rappresentazioni in cui «testa di animale» è vicina a «testa di animale», qualunque sia la pelliccia.</p></div>
"""), printed=P(22))

s(23, "Cross-Image Attention: Training-Free Appearance Transfer", R("""
<p>Si usano due immagini: una per la <b>struttura</b>, una per l'<b>aspetto</b>. Nella self-attention del denoiser si sostituiscono chiavi e valori con quelli dell'immagine di aspetto:</p>
<span class="f">softmax(Q<sup>str</sup> (K<sup>app</sup>)<sup>⊤</sup> / √d) V<sup>app</sup></span>
<ul>
<li>Q<sup>str</sup> conserva struttura e disposizione (ogni posizione della giraffa resta dov'è);</li>
<li>K<sup>app</sup>, V<sup>app</sup> trasferiscono l'informazione di aspetto (ogni posizione va a «prendere» il materiale nella parte corrispondente della zebra);</li>
<li>si applica durante tutto il denoising, <b>senza fine-tuning</b>.</li>
</ul>
<p>È la cross-attention della <a href="#L27">L27</a> usata in modo nuovo: lì le chiavi venivano dal testo, qui da un'altra immagine. Il motivo per cui funziona è la slide 22: la query di «testa di giraffa» è simile alla chiave di «testa di zebra».</p>
"""), printed=P(23))

s(24, "Cross-Image Attention: Example Generations", R("""
<p>Figura 1 dell'articolo (Alaluf et al., 2024). In ciascun pannello la riga in alto contiene le immagini di <b>aspetto</b>, la cella in basso a sinistra l'immagine di <b>struttura</b>; le altre celle in basso sono i risultati: stessa posa e disposizione della struttura, texture e materiale dell'aspetto sopra.</p>
<ul>
<li>A sinistra: il Duomo di Milano con l'aspetto del Taj Mahal, di una chiesa in mattoni, della Sagrada Família.</li>
<li>A destra: la giraffa con l'aspetto di un canguro, di una tigre, di una zebra.</li>
</ul>
<p>Funziona attraverso categorie, forme e punti di vista diversi, senza ottimizzazione per coppia.</p>
"""), printed=P(24))

s(25, "IP-Adapter: Image Prompts via Decoupled Cross-Attention", R("""
<p><b>IP-Adapter</b> (Ye et al., 2023) condiziona la generazione su un'<b>immagine di riferimento</b>, oltre che sul testo.</p>
<ul>
<li>U-Net ed encoder di testo congelati.</li>
<li>Si addestra un ramo di <b>cross-attention per l'immagine</b>, in parallelo a quella per il testo:</li>
</ul>
<span class="f">Z = Attn(Q, K<sub>t</sub>, V<sub>t</sub>) + λ Attn(Q, K<sub>i</sub>, V<sub>i</sub>)</span>
<ul>
<li>Q dalle feature della U-Net (come sempre); K<sub>t</sub>, V<sub>t</sub> dal testo; K<sub>i</sub>, V<sub>i</sub> dalle feature dell'immagine di riferimento (encoder di immagini di CLIP più una piccola proiezione che ne fa 4 token).</li>
<li>Testo e immagine sono trattati <b>separatamente</b> («decoupled»): due attenzioni distinte, sommate; λ regola il peso dell'immagine.</li>
<li>Si addestrano solo <b>22 milioni</b> di parametri.</li>
</ul>
<div class="box k"><b>Da saper fare: perché separare</b><p>L'alternativa ingenua è concatenare i token dell'immagine a quelli del testo nella stessa cross-attention. Ma lì il softmax mette in competizione parole e token d'immagine, e le matrici W<sub>K</sub>, W<sub>V</sub> del testo, addestrate solo su testo, non sanno leggere feature d'immagine. Con due attenzioni separate il ramo del testo resta identico al modello originale e il nuovo ramo impara da zero le sue proiezioni.</p></div>
"""), printed=P(25))

s(26, "IP-Adapter: Reusable Across Fine-Tuned Checkpoints", R("""
<ul>
<li>Si addestra l'IP-Adapter <b>una volta</b> su un modello base.</li>
<li>Lo si riusa con checkpoint derivati (fine-tuning di comunità) che hanno la stessa architettura: Realistic Vision, Anything v4, ReV Animated, SD 1.4 nella figura.</li>
<li>L'immagine di riferimento fornisce l'aspetto, il checkpoint decide lo stile.</li>
<li>Nessun fine-tuning per soggetto: basta dare una nuova immagine come prompt.</li>
</ul>
<p>La figura: sette immagini di riferimento in alto (una ragazza, un paesaggio, un cane, la Ragazza con l'orecchino di perla, un guerriero, un busto, un lago) e, sotto, le generazioni con diversi checkpoint: stesso contenuto, stili diversi (fotorealistico, anime, illustrazione).</p>
<p>Funziona perché il ramo dell'IP-Adapter è separato: il checkpoint cambia i pesi della U-Net ma la «presa» sulle feature resta compatibile.</p>
"""), printed=P(26))

# ===================== PARTE 3 =====================

s(27, "Evaluation and Compositionality", R("""<p>Divisoria della terza parte: come si valuta la personalizzazione e come si combinano più concetti.</p>"""),
  kind='div', sec=("l28-valut", "Parte 3 · Valutazione e composizione", "slide 27–38"), printed='')

s(28, "Evaluation Metrics for Personalized Generation", R("""
<p><b>Fedeltà al soggetto</b>:</p>
<ul>
<li><b>DINO</b>: similarità coseno fra le feature di un ViT addestrato con DINO dell'immagine generata e di quella di riferimento, DINO = cos(f<sub>DINO</sub>(x<sub>gen</sub>), f<sub>DINO</sub>(x<sub>ref</sub>)). Misura la conservazione dell'identità.</li>
<li><b>CLIP-I</b>: la stessa cosa con l'encoder di immagini di CLIP, CLIP-I = cos(E<sub>img</sub>(x<sub>gen</sub>), E<sub>img</sub>(x<sub>ref</sub>)).</li>
</ul>
<p><b>Aderenza al testo</b>:</p>
<ul>
<li><b>CLIP-T</b>: similarità fra l'immagine generata e il prompt, CLIP-T = cos(E<sub>img</sub>(x<sub>gen</sub>), E<sub>text</sub>(y)).</li>
</ul>
<p><b>Qualità dell'immagine</b>: FID (<a href="#L27">L27</a>), IS (Inception Score), valutazione umana (coerenza del soggetto, fedeltà al prompt, qualità visiva).</p>
<p><b>Il compromesso</b>: più fine-tuning ⇒ più fedeltà (DINO e CLIP-I salgono) ma potenzialmente meno editabilità (CLIP-T scende). I buoni metodi migliorano il <b>fronte di Pareto</b>, non una sola metrica.</p>
<div class="box x"><b>Approfondimento: perché DINO oltre a CLIP-I</b><p>CLIP è addestrato ad allineare immagini e didascalie, quindi due cani diversi della stessa razza hanno embedding CLIP molto simili: CLIP-I misura soprattutto la <i>classe</i>. DINO è addestrato senza testo a distinguere ogni immagine dalle altre (instance discrimination, <a href="#L21">L21</a>–<a href="#L22">L22</a>), quindi è più sensibile ai dettagli dell'<i>individuo</i>. Per questo DreamBooth lo propone come metrica principale di fedeltà.</p></div>
<div class="box b"><b>Dal libro · {C51}, § 51.3</b><p>CLIP-I e CLIP-T usano lo spazio congiunto di CLIP: lo stesso prodotto scalare fra vettori normalizzati che il libro usa per la classificazione zero-shot.</p></div>
"""), printed=P(28))

s(29, "DreamBooth vs. Textual Inversion: Quantitative Results", R("""
<table>
<tr><th>Metodo</th><th>DINO ↑</th><th>CLIP-I ↑</th><th>CLIP-T ↑</th></tr>
<tr><td>Immagini reali</td><td>0,774</td><td>0,885</td><td>–</td></tr>
<tr><td>DreamBooth (Imagen)</td><td>0,696</td><td>0,812</td><td>0,306</td></tr>
<tr><td>DreamBooth (Stable Diffusion)</td><td>0,668</td><td>0,803</td><td>0,305</td></tr>
<tr><td>Textual Inversion (Stable Diffusion)</td><td>0,569</td><td>0,780</td><td>0,255</td></tr>
</table>
<ul>
<li>DINO e CLIP-I (fedeltà): DreamBooth conserva meglio l'identità.</li>
<li>CLIP-T (testo): DreamBooth segue anche meglio i prompt.</li>
<li>Fare il fine-tuning del denoiser dà più capacità che ottimizzare un solo embedding.</li>
</ul>
<p>La riga «immagini reali» è il tetto: è la similarità media fra due foto vere diverse dello stesso soggetto. DreamBooth (Imagen) a 0,696 contro 0,774 vuol dire che ha recuperato buona parte della distanza fra Textual Inversion e il tetto. Numeri verificati sulla Tabella 1 dell'articolo.</p>
<div class="box k"><b>Da saper fare</b><p>Leggere la tabella come un grafico a due assi: DreamBooth sta in alto a destra (più fedele e più aderente), Textual Inversion in basso a sinistra. Qui non c'è compromesso fra i metodi perché DreamBooth domina su entrambe le metriche; il compromesso compare <i>dentro</i> un metodo, variando quanto si addestra.</p></div>
"""), printed=P(29))

s(30, "Combining Two LoRA Concepts", R("""
<p>Un adattatore ha imparato un soggetto, un altro uno stile:</p>
<span class="f">ΔW<sub>subject</sub> = B<sub>s</sub>A<sub>s</sub>,   ΔW<sub>style</sub> = B<sub>c</sub>A<sub>c</sub></span>
<p>Fusione pesata:</p>
<span class="f">W′ = W<sub>0</sub> + λ<sub>s</sub> B<sub>s</sub>A<sub>s</sub> + λ<sub>c</sub> B<sub>c</sub>A<sub>c</sub></span>
<ul>
<li>I due adattatori si attivano insieme senza cambiare il backbone condiviso.</li>
<li>L'aggiornamento fuso ha rango al più r<sub>s</sub> + r<sub>c</sub>, non necessariamente r<sub>s</sub>.</li>
<li>Sommare i parametri <b>non garantisce</b> che soggetto e stile restino separati nel significato.</li>
</ul>
<p>Attenzione alla notazione della slide: il pedice c qui sta per lo <b>stile</b> (come in LoRA.rar), mentre nella slide 31 di ZipLoRA c sta per il <b>contenuto</b>. Il problema della somma ingenua: le due correzioni toccano le stesse colonne delle stesse matrici e possono interferire (lo stile «trascina» il contenuto della sua foto, slide 37).</p>
"""), printed=P(30))

s(31, "ZipLoRA: Learning How to Merge", R("""
<p>La fusione ingenua usa pesi scalari fissi w<sub>c</sub>, w<sub>s</sub>: ΔW<sub>m</sub> = w<sub>c</sub>ΔW<sub>c</sub> + w<sub>s</sub>ΔW<sub>s</sub>. ZipLoRA (Shah et al., 2023) impara invece un coefficiente <b>per colonna</b>, per il contenuto e per lo stile:</p>
<span class="f">ΔW<sub>m</sub> = m<sub>c</sub> ⊗ ΔW<sub>c</sub> + m<sub>s</sub> ⊗ ΔW<sub>s</sub>,   ΔW<sub>c</sub> = B<sub>c</sub>A<sub>c</sub>, ΔW<sub>s</sub> = B<sub>s</sub>A<sub>s</sub></span>
<p>⊗ è la scala per colonna: (ΔW<sub>m</sub>)<sub>:,j</sub> = m<sub>c</sub><sup>(j)</sup>(ΔW<sub>c</sub>)<sub>:,j</sub> + m<sub>s</sub><sup>(j)</sup>(ΔW<sub>s</sub>)<sub>:,j</sub>, con m<sub>c</sub>, m<sub>s</sub> ∈ ℝ<sup>d<sub>in</sub></sup> per ΔW ∈ ℝ<sup>d<sub>out</sub>×d<sub>in</sub></sup>.</p>
<ul>
<li>Si ottimizzano <b>solo</b> m<sub>c</sub> e m<sub>s</sub>: i LoRA restano fermi.</li>
</ul>
<p>La figura: un LoRA di contenuto (il chow chow) e uno di stile («Flowers in [S] style») entrano nella fusione ZipLoRA, che genera il cane nello stile dei fiori in quattro situazioni.</p>
<div class="box k"><b>Da saper fare: perché per colonna</b><p>La colonna j di ΔW dice come l'aggiornamento risponde alla componente j dell'ingresso. Pesare per colonna permette di dire «per questa direzione d'ingresso uso il contenuto, per quest'altra lo stile», invece di un unico miscuglio. Numero di parametri da ottimizzare: 2d<sub>in</sub> per matrice, pochissimi.</p></div>
"""), printed=P(31))

s(32, "ZipLoRA: Fidelity and Orthogonality Losses", R("""
<p>Tre termini. Con D il modello base, D ⊕ L il modello con un LoRA L, L<sub>m</sub> la fusione, (x<sub>c</sub>, p<sub>c</sub>) e (x<sub>s</sub>, p<sub>s</sub>) immagini e prompt di contenuto e di stile:</p>
<span class="f">ℒ<sub>content</sub> = ‖(D ⊕ L<sub>m</sub>)(x<sub>c</sub>, p<sub>c</sub>) − (D ⊕ L<sub>c</sub>)(x<sub>c</sub>, p<sub>c</sub>)‖<sub>2</sub></span>
<span class="f">ℒ<sub>style</sub> = ‖(D ⊕ L<sub>m</sub>)(x<sub>s</sub>, p<sub>s</sub>) − (D ⊕ L<sub>s</sub>)(x<sub>s</sub>, p<sub>s</sub>)‖<sub>2</sub></span>
<span class="f">ℒ<sub>ortho</sub> = ∑<sub>i</sub> |m<sub>c</sub><sup>(i)</sup> m<sub>s</sub><sup>(i)</sup>|,   ℒ<sub>merge</sub> = ℒ<sub>content</sub> + ℒ<sub>style</sub> + λ ℒ<sub>ortho</sub></span>
<ul>
<li>I primi due chiedono che il modello fuso, col prompt di contenuto, si comporti come il LoRA di contenuto da solo, e col prompt di stile come il LoRA di stile da solo.</li>
<li>Il terzo spinge a non usare la stessa colonna per entrambi: se m<sub>c</sub><sup>(i)</sup> è grande, m<sub>s</sub><sup>(i)</sup> deve essere piccolo, e viceversa.</li>
</ul>
<p>La figura: il modello con L<sub>c+s</sub> (fuso) viene confrontato con D + L<sub>c</sub> sul «A [V] dog» e con D + L<sub>s</sub> su «Flowers in [S] style»; le differenze tornano indietro come gradiente solo sui coefficienti m.</p>
"""), printed=P(32))

s(33, "ZipLoRA: Qualitative Comparison", R("""
<p>Tabella di immagini: tre soggetti (un corgi, una teiera, un peluche) in quattro stili ciascuno (pastello a cera, render 3D, disegno al tratto, adesivo, acquerello, cartone piatto...). Righe: <b>fusione aritmetica diretta</b>, training congiunto, StyleDrop + DreamBooth, Custom Diffusion, Mix-of-Show, e in fondo <b>ZipLoRA</b>.</p>
<p>Cosa guardare: nelle righe in alto spesso il soggetto si perde (il cane non è più lui) o lo stile non arriva; ZipLoRA conserva entrambi in quasi tutte le colonne. È un confronto qualitativo scelto dagli autori: va preso come illustrazione, non come misura.</p>
"""), printed=P(33))

s(34, "B-LoRA: Content and Style Separation", R("""
<ul>
<li>B-LoRA (Frenkel et al., 2024) adatta solo <b>due blocchi transformer</b> scelti di SDXL, uno associato al contenuto e uno allo stile (nella figura W<sup>4</sup> e W<sup>5</sup>).</li>
<li>Si addestrano i LoRA da <b>una sola immagine</b> di riferimento: ΔW<sub>ℓ</sub> = B<sub>ℓ</sub>A<sub>ℓ</sub> con ℓ ∈ {ℓ<sub>content</sub>, ℓ<sub>style</sub>}.</li>
<li>Loss di ricostruzione di diffusione standard: <b>nessuna loss esplicita</b> di separazione fra contenuto e stile.</li>
<li>Poi si combinano i pesi «di contenuto» di un soggetto con quelli «di stile» di un altro.</li>
</ul>
<p>La separazione è <b>implicita</b>: gli autori hanno trovato con esperimenti che in SDXL quei due blocchi controllano rispettivamente cosa c'è e come è disegnato, quindi un LoRA allenato su entrambi i blocchi con una sola foto si divide da solo in due pezzi riusabili.</p>
<p>La figura: (1) stilizzazione da un'immagine di stile; si usa il ΔW<sup>4</sup> del contenuto «A [c]» e il ΔW<sup>5</sup> dello stile «A [s]» per ottenere «A [c] in [s] style».</p>
"""), printed=P(34))

s(35, "B-LoRA: Example Generations", R("""
<p>Figura 2 dell'articolo. Da una sola immagine di contenuto (un cagnolino bianco, a sinistra) quattro risultati: tre usano un'immagine di stile come riferimento (schizzo a matita, disegno a colori, una foto di un cane su sfondo urbano) e l'ultimo, a destra, solo il prompt di testo «made of glass».</p>
<p>Una sola immagine basta per addestrare entrambi i B-LoRA: non serve un dataset di stile a parte.</p>
"""), printed=P(35))

s(36, "Personalization: Identity vs. Editability", R("""
<ul>
<li><b>Identità del soggetto</b>: conservare i tratti distintivi.</li>
<li><b>Editabilità del prompt</b>: cambiare posa, sfondo, vestiti, stile.</li>
<li>Adattarsi molto al soggetto può ridurre l'editabilità sui prompt nuovi.</li>
<li>Le due proprietà vanno <b>valutate separatamente</b>.</li>
</ul>
<p>La figura riprende lo zaino e la teiera di DreamBooth in contesti nuovi (Grand Canyon, bagnato, Boston, cielo notturno; la teiera nel latte, trasparente con il latte dentro, che versa il tè, nel mare). Un'immagine come «teiera trasparente» è un buon test: l'identità (forma) deve restare, una proprietà (materiale) deve cambiare.</p>
"""), printed=P(36))

s(37, "Automatic Metrics Can Be Gamed", R("""
<p>Esempio dall'articolo LoRA.rar (Shenaj et al., 2025): fusione ingenua di un LoRA di soggetto e uno di stile.</p>
<ul>
<li><b>Riga in alto</b>: il contenuto dell'immagine di stile <b>«filtra»</b> nell'immagine generata (esce un personaggio diverso dal gatto). Eppure CLIP-I dà 0,817, un valore alto, perché l'immagine somiglia comunque al riferimento. DINO invece è 0,180.</li>
<li><b>Riga in basso</b>: il soggetto (il peluche) è conservato, ma lo stile non è stato trasferito. DINO dà 0,801, alto, perché misura solo l'identità. CLIP-I è 0,445.</li>
</ul>
<p>Conclusione: <b>una sola metrica di similarità non cattura tutti i fallimenti</b>. Ogni metrica guarda una cosa sola, e un'immagine sbagliata in un modo diverso può prendere un punteggio alto.</p>
<div class="box k"><b>Da saper fare</b><p>Per ogni metrica, dire che tipo di errore <i>non</i> vede: DINO non vede se lo stile manca; CLIP-I premia somiglianze di classe o di stile anche se il soggetto è sbagliato; CLIP-T non sa nulla dell'identità. Per questo si riportano sempre più metriche insieme, più una valutazione umana o con un giudice multimodale.</p></div>
"""), printed=P(37))

s(38, "LLaVA-Critic: Evaluating Generated Images", R("""
<ul>
<li>Si usa un <b>LLM multimodale</b> (un VLM come LLaVA, <a href="#L24">L24</a>) per giudicare le immagini generate, guardando immagine e testo insieme.</li>
<li>Lo si addestra su dati di istruzioni per il giudizio, per due compiti: <b>pointwise</b> (dare un voto a un'immagine) e <b>pairwise</b> (confrontare due immagini e scegliere la migliore).</li>
<li>Il modello produce sia un giudizio sia una <b>spiegazione</b> testuale.</li>
<li>I criteri possono includere fedeltà al soggetto, aderenza al prompt e qualità visiva.</li>
<li>I giudizi di un MLLM <b>completano</b> DINO, CLIP-I e CLIP-T, non li sostituiscono.</li>
</ul>
<p>I grafici (Xiong et al., 2024) confrontano le distribuzioni dei punteggi e la correlazione con i giudizi di riferimento su vari benchmark (MM-Vet, WildVision-Bench, LLaVA-in-the-Wild, MMHal-Bench) per diversi modelli: il critico addestrato si avvicina di più ai giudizi di riferimento.</p>
"""), printed=P(38))

# ===================== PARTE 4 =====================

s(39, "Extensions: Controlled and Video Generation", R("""<p>Divisoria della quarta parte: controllo spaziale e generazione video.</p>"""),
  kind='div', sec=("l28-controllo", "Parte 4 · Controllo spaziale e video", "slide 39–49"), printed='')

s(40, "ControlNet: Spatial Conditioning", R("""
<ul>
<li>Condizionare la generazione su <b>informazione spaziale</b>: bordi, mappe di profondità, pose, maschere di segmentazione.</li>
<li>La condizione spaziale fissa la <b>struttura</b> dell'immagine; il prompt decide il resto.</li>
<li>ControlNet (Zhang et al., 2023) aggiunge un ramo addestrabile a un modello di diffusione preaddestrato, che resta congelato.</li>
<li>Si può combinare con modelli personalizzati, per controllare posa e disposizione del soggetto.</li>
</ul>
<p>La figura: in alto i bordi di Canny di un cervo e quattro generazioni che li rispettano («fiaba, cervo gigante con corna d'oro», «città galica»...); in basso uno scheletro di posa e generazioni con la stessa posa («chef in cucina», «statua di Lincoln»).</p>
<div class="box b"><b>Dal libro · {C34}, § 34.6 Image-to-Image Translation e § 34.4.4</b><p>Il libro presenta la traduzione immagine-immagine (pix2pix: da una mappa di layout di una facciata a una foto) come generazione condizionata su un'immagine, e nel § 34.4.4 dice che un modello di diffusione si condiziona semplicemente dando la condizione in ingresso al denoiser. ControlNet è la versione moderna: la «mappa» è un bordo, una posa o una profondità, e il generatore è un modello di diffusione preaddestrato. Prince, nelle note del cap. 18, cita proprio il «control network» per condizionare su bordi, pose, segmentazioni e profondità.</p></div>
"""), printed=P(40))

s(41, "ControlNet: Zero Convolutions", R("""
<ul>
<li>Si <b>copiano</b> i blocchi della U-Net preaddestrata per formare un ramo addestrabile.</li>
<li>La U-Net originale resta <b>congelata</b> («locked»).</li>
<li>Ramo addestrabile e ramo congelato sono collegati da <b>zero convolution</b>.</li>
<li>Una zero convolution è una convoluzione 1 × 1 inizializzata con pesi e bias nulli: y = W<sub>zero</sub> ∗ x + b<sub>zero</sub>, W<sub>zero</sub> = 0, b<sub>zero</sub> = 0.</li>
<li>All'inizio il ramo aggiunto produce residui <b>nulli</b>: il modello è esattamente quello originale.</li>
</ul>
<p>La figura: (a) prima, un blocco qualunque x → y; (b) dopo, il blocco è bloccato e accanto c'è la sua copia addestrabile, che riceve x più la condizione c passata da una zero convolution, e la cui uscita passa da un'altra zero convolution prima di essere sommata a y.</p>
<div class="box w"><b>Precisazione: perché i pesi a zero non bloccano l'addestramento</b><p>Viene da pensare che con tutto a zero il gradiente sia nullo, come per LoRA con A e B entrambe a zero (<a href="#L25">L25</a>). Non è così: per y = Wx + b il gradiente rispetto a W è (∂ℒ/∂y) x<sup>⊤</sup>, e x (l'uscita della copia addestrabile, che parte dai pesi preaddestrati) <b>non è zero</b>. Quindi al primo passo W<sub>zero</sub> diventa diverso da zero, e dal secondo passo anche il gradiente arriva alla copia. È lo stesso meccanismo di LoRA con B = 0 e A gaussiana: un solo fattore a zero.</p></div>
"""), printed=P(41))

s(42, "ControlNet: Stable Diffusion Architecture", R("""
<ul>
<li><b>Ramo bloccato</b>: la U-Net preaddestrata di Stable Diffusion, con parametri fissi θ<sub>0</sub>.</li>
<li><b>Ramo addestrabile</b>: copia dei blocchi encoder e del blocco centrale della U-Net, con parametri ϕ.</li>
<li>La condizione spaziale c<sub>f</sub> entra nel ramo addestrabile.</li>
<li>Le sue feature si sommano alla U-Net congelata tramite zero convolution, a <b>più risoluzioni</b> (64 × 64, 32 × 32, 16 × 16, 8 × 8), sulle skip connection del decoder e sul blocco centrale.</li>
</ul>
<p>La figura: a sinistra la U-Net di SD (encoder A–D, centrale, decoder D–A) con i lucchetti; a destra la copia addestrabile di encoder e centrale; le linee con «zero convolution» portano le feature della copia dentro il decoder congelato.</p>
<p>Il decoder <b>non</b> viene copiato: la copia dell'encoder «legge» la condizione e dice al decoder originale come correggere le sue skip connection. Il costo è circa metà U-Net in più per passo.</p>
"""), printed=P(42))

s(43, "Controllable Image Generation", R("""
<table>
<tr><th></th><th>LoRA</th><th>ControlNet</th><th>IP-Adapter</th></tr>
<tr><td>Condizione</td><td>soggetto / stile</td><td>mappa spaziale</td><td>immagine di riferimento</td></tr>
<tr><td>Meccanismo</td><td>adattamento dei pesi</td><td>ramo aggiuntivo della U-Net</td><td>cross-attention per l'immagine</td></tr>
<tr><td>Si addestra</td><td>i fattori A, B</td><td>i parametri ϕ di ControlNet</td><td>il ramo di attenzione per l'immagine</td></tr>
<tr><td>Soggetto nuovo</td><td>fine-tuning del LoRA</td><td>si fornisce una mappa</td><td>si fornisce un'immagine</td></tr>
</table>
<ul>
<li>LoRA adatta i pesi a un soggetto o a uno stile.</li>
<li>ControlNet vincola la struttura spaziale; IP-Adapter condiziona sull'aspetto di riferimento.</li>
<li>I metodi si possono <b>combinare</b> nello stesso modello compatibile (per esempio: LoRA del tuo cane + ControlNet di posa + prompt).</li>
</ul>
<div class="box k"><b>Da saper fare</b><p>Per una richiesta concreta, scegliere il metodo: «il mio cane in questa posa» = LoRA (DreamBooth) + ControlNet di posa; «una scena con l'aspetto di questa foto, senza addestrare nulla» = IP-Adapter; «questa scena, con questi bordi, dipinta» = ControlNet di Canny + prompt.</p></div>
"""), printed=P(43))

s(44, "ControlNet: Training Objective", R("""
<p>Dati un'immagine x<sub>0</sub>, un prompt c<sub>text</sub> e una condizione spaziale c<sub>spatial</sub>:</p>
<span class="f">z<sub>t</sub> = √ᾱ<sub>t</sub> z<sub>0</sub> + √(1 − ᾱ<sub>t</sub>) ε,   ε ∼ 𝒩(0, I)</span>
<span class="f">ℒ<sub>ControlNet</sub>(ϕ) = 𝔼<sub>z<sub>0</sub>, t, ε, c</sub> ‖ε − ε<sub>θ<sub>0</sub>, ϕ</sub>(z<sub>t</sub>, t, c<sub>text</sub>, c<sub>spatial</sub>)‖<sub>2</sub><sup>2</sup></span>
<ul>
<li>θ<sub>0</sub>: parametri congelati della U-Net preaddestrata; ϕ: il ramo ControlNet addestrabile, zero convolution comprese.</li>
<li>c<sub>spatial</sub> si <b>ricava dall'immagine stessa</b> (un rilevatore di bordi di Canny, un estimatore di profondità come MiDaS della <a href="#L17">L17</a>, un estimatore di pose): le coppie di training si costruiscono automaticamente da qualunque collezione di immagini.</li>
<li>Si ottimizza solo ϕ con la solita loss di previsione del rumore.</li>
</ul>
<p>È la loss della <a href="#L27">L27</a> con un ingresso in più. Nell'articolo il prompt viene anche sostituito a caso da una stringa vuota (circa metà delle volte), così il ramo impara a leggere la struttura dalla mappa e non a appoggiarsi al testo.</p>
"""), printed=P(44))

s(45, "OminiControl: Architecture and Training", R("""
<ul>
<li>Si congela il backbone preaddestrato di <b>FLUX</b> (<a href="#L27">L27</a>).</li>
<li>L'immagine di condizione si codifica con il VAE preaddestrato, come l'immagine da generare.</li>
<li>Si <b>concatenano</b> in un'unica sequenza i token dell'immagine rumorosa, del testo e della condizione: S = [X<sub>t</sub>; C<sub>T</sub>; C<sub>I</sub>].</li>
<li>Si addestra un LoRA separato per ogni tipo di condizione (Canny, profondità, generazione guidata da un soggetto).</li>
<li>Loss: quella standard di flow matching di FLUX, ℒ<sub>FM</sub> = 𝔼 ‖v<sub>θ<sub>0</sub>,ϕ</sub>(x<sub>t</sub>, t, c) − (ε − x<sub>0</sub>)‖<sup>2</sup>, con ε il rumore (convenzione t = 0 dati della <a href="#L27">L27</a>).</li>
<li>Si aggiornano solo i parametri LoRA ϕ.</li>
</ul>
<p>La figura: sommare direttamente le feature della condizione alle feature dell'immagine («Direct Adding») allinea male la sagoma del cammello («Poor match»); metterle nella sequenza unificata dà un allineamento perfetto.</p>
<p>È l'idea di ControlNet riscritta per un DiT con attenzione congiunta: invece di un ramo copiato, la condizione diventa semplicemente <b>altri token</b> nella stessa attenzione.</p>
"""), printed=P(45))

s(46, "OminiControl: Spatial Alignment", R("""
<p>Esempio della figura: C<sub>img</sub> è un pinguino di peluche di riferimento, C<sub>text</sub> il prompt «In a bright room. It is placed on a table.»</p>
<ul>
<li>I token d'immagine hanno indici spaziali (h, w) usati dalla codifica posizionale (RoPE in FLUX).</li>
<li>Per i token di riferimento:</li>
</ul>
<span class="f">p<sub>ref</sub> = (h, w) <i>condivisa</i>,  oppure  (h + Δ<sub>h</sub>, w + Δ<sub>w</sub>) <i>spostata</i></span>
<ul>
<li><b>Condivisa</b>: incoraggia l'allineamento pixel per pixel con l'immagine generata (giusto per bordi e profondità).</li>
<li><b>Spostata</b>: lascia il soggetto libero di comparire in posizioni nuove (giusto per la generazione guidata dal soggetto).</li>
</ul>
<p>Nella figura con «Shared Pos.» il pinguino resta nella stessa posizione del riferimento, con «Shifting Pos.» compare sul tavolo in un punto diverso.</p>
"""), printed=P(46))

s(47, "OminiControl: Qualitative Results", R("""
<ul>
<li><b>Controllo spaziale</b> (a sinistra): rispetta bordi e profondità (camera da letto, bagno), confrontato con T2I-Adapter e ControlNet.</li>
<li><b>Generazione guidata dal soggetto</b> (a destra): porta una lattina e una scarpa di riferimento in scene nuove («sullo specchio», «in spiaggia»), confrontato con IP-Adapter su FLUX e su SD e con SSR-Encoder.</li>
<li>La stessa architettura gestisce entrambi i tipi di condizione: cambia solo il LoRA e la scelta delle posizioni.</li>
</ul>
"""), printed=P(47))

s(48, "AnimateDiff: Architecture and Training", R("""
<p>La figura mostra tre fasi:</p>
<ol>
<li><b>Ridurre gli effetti negativi</b>: un <i>domain adapter</i> (un LoRA nei layer d'immagine, Q = W<sup>Q</sup>z + Adapter(z)) assorbe la differenza di qualità fra le immagini del dataset video (fotogrammi sfocati, con watermark) e le immagini normali, così il modulo di moto non la impara.</li>
<li><b>Imparare i priori di moto</b>: si inserisce un <b>modulo di moto</b> (un transformer temporale con proiezione d'uscita inizializzata a zero) e lo si addestra su video.</li>
<li>Facoltativo: <b>adattarsi a pattern nuovi</b> con MotionLoRA su 20–50 video di riferimento (slide 49).</li>
</ol>
<p>Formalmente: si inseriscono moduli temporali ϕ in un denoiser d'immagine preaddestrato ε<sub>θ<sub>0</sub></sub>, si congela θ<sub>0</sub> e si addestra ϕ su clip video:</p>
<span class="f">ℒ<sub>motion</sub>(ϕ) = 𝔼<sub>z<sub>0</sub>, ε, t, c</sub> ‖ε − ε<sub>θ<sub>0</sub>, ϕ</sub>(z<sub>t</sub>, t, c)‖<sub>2</sub><sup>2</sup></span>
<p>z<sub>t</sub> è un latente video rumoroso, c il testo. Il modulo imparato si riusa con <b>modelli d'immagine personalizzati compatibili</b>: un DreamBooth o un LoRA del tuo personaggio diventa animabile senza riaddestrarlo. Sono gli strati temporali della <a href="#L27">L27</a> (slide 46–48), ma inseribili in qualunque derivato dello stesso modello.</p>
"""), printed=P(48))

s(49, "MotionLoRA: Adapting Motion Patterns", R("""
<ul>
<li>Si adatta un modulo di moto di AnimateDiff a un <b>movimento specifico</b>, per esempio zoom o panoramica della camera.</li>
<li>Aggiornamenti a basso rango delle proiezioni dell'attenzione temporale:</li>
</ul>
<span class="f">W′<sub>motion</sub> = W<sub>motion</sub> + (α/r) B<sub>m</sub>A<sub>m</sub>,   B<sub>m</sub> ∈ ℝ<sup>d<sub>out</sub>×r</sup>, A<sub>m</sub> ∈ ℝ<sup>r×d<sub>in</sub></sup></span>
<ul>
<li>Si congelano il modello d'immagine θ e il modulo di moto preaddestrato ϕ.</li>
<li>Si addestrano solo A<sub>m</sub>, B<sub>m</sub> su video che mostrano il movimento voluto, con lo stesso obiettivo di previsione del rumore: min<sub>A<sub>m</sub>,B<sub>m</sub></sub> 𝔼 ‖ε − ε<sub>θ,ϕ,A<sub>m</sub>,B<sub>m</sub></sub>(z<sub>t</sub>, t, c)‖<sup>2</sup>.</li>
<li>LoRA di soggetto e MotionLoRA si combinano per controllare <b>aspetto e movimento indipendentemente</b>.</li>
</ul>
<p>La separazione funziona perché agiscono su strati diversi: il LoRA di soggetto sugli strati spaziali, il MotionLoRA solo su quelli temporali.</p>
"""), printed=P(49))

# ===================== PARTE 5 =====================

s(50, "Limitations and Open Problems", R("""<p>Divisoria della quinta parte: limiti e problemi aperti.</p>"""),
  kind='div', sec=("l28-limiti", "Parte 5 · Riepilogo e problemi aperti", "slide 50–52"), printed='')

s(51, "Summary of Personalization Methods", R("""
<table>
<tr><th>Metodo</th><th>Cosa si addestra</th><th>Soggetto nuovo</th><th>Limite principale</th></tr>
<tr><td>Textual Inversion</td><td>embedding v*</td><td>ottimizzare v*</td><td>capacità limitata</td></tr>
<tr><td>DreamBooth</td><td>denoiser θ</td><td>fine-tuning di θ</td><td>calcolo e spazio</td></tr>
<tr><td>DreamBooth + LoRA</td><td>fattori A, B</td><td>ottimizzare A, B</td><td>rango dell'adattatore limitato</td></tr>
<tr><td>HyperDreamBooth</td><td>iperrete e adattatore</td><td>prevedere e rifinire</td><td>pensato per i visi</td></tr>
<tr><td>IP-Adapter</td><td>ramo di attenzione per l'immagine</td><td>un passaggio in avanti</td><td>fedeltà all'identità</td></tr>
</table>
<ul>
<li>I metodi basati su ottimizzazione imparano parametri per ogni soggetto.</li>
<li>HyperDreamBooth prevede un'inizializzazione e la rifinisce per un soggetto nuovo.</li>
<li>IP-Adapter usa direttamente un'immagine di riferimento, senza ottimizzazione per soggetto.</li>
</ul>
<p>La riga da ricordare: più ci si allontana dall'ottimizzazione per soggetto, più si guadagna in velocità e meno in fedeltà fine. IP-Adapter è istantaneo ma conserva l'identità meno bene di DreamBooth.</p>
"""), printed=P(51))

s(52, "Open Problems and Research Directions", R("""
<ol>
<li><b>Personalizzazione few-shot</b>: un soggetto da una sola foto, con poco o nessun fine-tuning.</li>
<li><b>Valutazione</b>: le similarità di CLIP e DINO non catturano tutti gli aspetti di fedeltà e aderenza; le metriche con MLLM sono più costose e vanno ancora validate.</li>
<li><b>Personalizzazione del moto</b>: imparare movimenti specifici del soggetto mantenendo l'identità coerente fra i frame.</li>
<li><b>Composizione di più concetti</b>: mettere più soggetti personalizzati nella stessa scena senza che si mescolino.</li>
<li><b>Personalizzazione con i DiT</b>: adattare i metodi ad architetture come FLUX e SD3, tenendo conto dell'attenzione congiunta testo-immagine.</li>
</ol>
<p>Il punto 5 si capisce con la <a href="#L27">L27</a>: molti metodi (IP-Adapter, Cross-Image Attention) sono nati per la cross-attention della U-Net, dove testo e immagine sono separati. Nel MM-DiT testo e immagine stanno nella stessa attenzione, quindi bisogna ripensare dove inserire il soggetto (OminiControl, slide 45, è un esempio).</p>
"""), printed=P(52))

# ===================== PARTE 6 =====================

s(53, "Other Ways to Adapt Generation", R("""<p>Divisoria della sesta parte: adattare la generazione senza toccare il modello, agendo sul rumore iniziale.</p>"""),
  kind='div', sec=("l28-rumore", "Parte 6 · Adattare il rumore iniziale", "slide 53–62"), printed='')

s(54, "Noise Optimization: Test-Time Compute", R("""
<p>G<sub>θ</sub>(z, c) è un generatore congelato <b>a pochi passi</b> (distillato, <a href="#L27">L27</a> slide 27), con z ∼ 𝒩(0, I). Data una <b>ricompensa</b> R(x, c) ∈ ℝ (estetica, aderenza al prompt...), si genera x = G<sub>θ</sub>(z, c).</p>
<p>L'<b>ottimizzazione del rumore al test</b> aggiorna ripetutamente il rumore di partenza con la salita del gradiente:</p>
<span class="f">z<sup>(k+1)</sup> = z<sup>(k)</sup> + η ∇<sub>z</sub> R(G<sub>θ</sub>(z<sup>(k)</sup>, c), c)</span>
<ul>
<li>Richiede i gradienti <b>attraverso il generatore</b> in inferenza (è per questo che serve un generatore a pochi passi: derivare attraverso 50 passi costerebbe troppo).</li>
<li>Più passi di ottimizzazione = più calcolo e latenza.</li>
<li>L'obiettivo è una ricompensa, <b>non</b> l'identità di un soggetto.</li>
</ul>
<p>È il «test-time compute» applicato alle immagini: si spende calcolo al momento della generazione invece che nel training. Ricorda gli esempi avversari della <a href="#L14">L14</a>: anche lì si fa salita del gradiente sull'ingresso, solo che lì l'ingresso è l'immagine e lo scopo è ingannare un classificatore.</p>
"""), printed=P(54))

s(55, "Noise Hypernetworks: Modify Initial Noise", R("""
<p>Invece di ottimizzare z per ogni prompt, si <b>impara una mappa</b> (Eyring et al., 2025):</p>
<span class="f">z ∼ 𝒩(0, I),   z̃ = z + H<sub>ϕ</sub>(z, c),   x = G<sub>θ<sub>0</sub></sub>(z̃, c)</span>
<ul>
<li>G<sub>θ<sub>0</sub></sub> resta congelato.</li>
<li>H<sub>ϕ</sub> si addestra <b>una volta</b> per produrre un rumore iniziale migliore (nella figura è un LoRA sullo stesso modello base, usato come rete del rumore).</li>
<li>In inferenza basta <b>una valutazione</b> dell'iperrete.</li>
</ul>
<p>È lo stesso salto concettuale di HyperDreamBooth (slide 18): un'ottimizzazione per istanza viene <b>ammortizzata</b> in una rete che ne prevede il risultato. La figura: a sinistra il training (il rumore passa dalla rete, poi dal generatore, una ricompensa e una regolarizzazione KL tornano come gradiente), a destra l'inferenza (rumore iniziale → rumore ottimizzato → generatore).</p>
"""), printed=P(55))

s(56, "Noise Hypernetworks: Training Objective", R("""
<p>Si definisce una distribuzione obiettivo sul rumore «inclinata» verso la ricompensa:</p>
<span class="f">p*(z | c) ∝ p<sub>0</sub>(z) exp(R(G<sub>θ<sub>0</sub></sub>(z, c), c)/τ)</span>
<p>(p<sub>0</sub> è la gaussiana standard, τ una temperatura: rumori che danno immagini con ricompensa alta diventano più probabili, ma senza allontanarsi troppo dal prior). Si adatta H<sub>ϕ</sub> perché z̃ = z + H<sub>ϕ</sub>(z, c) si comporti come un campione di p*:</p>
<span class="f">ℒ(ϕ) = 𝔼<sub>z,c</sub> [ (λ/2) ‖H<sub>ϕ</sub>(z, c)‖<sub>2</sub><sup>2</sup> − R(G<sub>θ<sub>0</sub></sub>(z + H<sub>ϕ</sub>(z, c), c), c) ]</span>
<ul>
<li>Il termine quadratico tiene z̃ vicino al prior gaussiano: è un sostituto calcolabile del termine KL che porta la distribuzione imparata verso p*.</li>
<li>Il termine di ricompensa spinge le generazioni verso ricompense più alte.</li>
<li>Il generatore resta congelato; si addestra solo H<sub>ϕ</sub>.</li>
</ul>
<div class="box k"><b>Da saper fare: perché serve il termine quadratico</b><p>Senza, la soluzione ottima manderebbe ogni z nello stesso punto di ricompensa massima: tutte le immagini uguali (<b>reward hacking</b>, e collasso della diversità come nella CFG troppo alta). La penalità sullo spostamento ‖H‖<sup>2</sup> fa sì che ogni rumore si muova solo un po', quindi immagini diverse restano diverse. La dispensa ha un esempio numerico.</p></div>
"""), printed=P(56))

s(57, "Noise Hypernetworks: Qualitative Results", R("""
<p>Quattro righe: SANA-Sprint, SANA-Sprint + HyperNoise, FLUX-Schnell, FLUX-Schnell + HyperNoise (due generatori a pochi passi, <a href="#L27">L27</a>). Quattro prompt complessi: uno squalo gigante con un'auto rossa e montagne; un ponte blu con muschio verde, lanterne rosse e riflessi; una fetta di pizza sorridente che fa yoga in cima a una montagna; una barca a vela, un faro rosso e l'aurora.</p>
<p>Cosa guardare: con HyperNoise compaiono più spesso tutti gli elementi chiesti (l'auto rossa, le lanterne, la pizza che fa davvero yoga), cioè migliora l'aderenza a prompt composizionali, con lo stesso generatore e un solo passaggio in più.</p>
"""), printed=P(57))

s(58, "Noise Hypernetworks: Optimizing Desired Rewards", R("""
<p>Esperimento con una ricompensa volutamente semplice: <b>quanto è rossa</b> l'immagine. Da sinistra a destra aumentano i passi di training.</p>
<ul>
<li><b>In alto, HyperNoise</b>: le immagini diventano più rosse ma restano pappagallo, delfino, treno, auto riconoscibili.</li>
<li><b>In basso, fine-tuning LoRA</b> del generatore sulla stessa ricompensa: alla fine le immagini diventano macchie rosse senza contenuto.</li>
</ul>
<p>Il messaggio: modificare il <b>rumore</b> con una penalità di vicinanza al prior è molto più conservativo che modificare i <b>pesi</b> del generatore, che sfruttano la ricompensa fino a distruggere le immagini (reward hacking).</p>
"""), printed=P(58))

s(59, "Hands-On: DreamBooth + LoRA", R("""
<p><b>Flusso di addestramento</b>:</p>
<ol>
<li>raccogliere 3–5 foto del soggetto;</li>
<li>scegliere il prompt identificatore, per esempio «a [V] dog»;</li>
<li>caricare un modello di diffusione preaddestrato;</li>
<li>congelare il backbone e addestrare i parametri LoRA A, B;</li>
<li>salvare l'adattatore del soggetto.</li>
</ol>
<span class="f">W′ = W<sub>0</sub> + (α/r) BA</span>
<p><b>Inferenza</b>: si carica l'adattatore e si generano immagini con prompt che contengono l'identificatore.</p>
<pre>
# pipeline preaddestrata gia' caricata
pipe.load_lora_weights("my_subject_lora", adapter_name="subject")
image = pipe("a [V] dog on the beach").images[0]
</pre>
<ul>
<li>I pesi LoRA sono salvati <b>a parte</b> dal modello base.</li>
<li>Adattatori diversi si caricano per soggetti diversi, sullo stesso modello.</li>
</ul>
<p>Nota pratica: nel codice reale «[V]» va sostituito dal token effettivamente usato nel training (spesso «sks»); il prompt di inferenza deve contenerlo identico.</p>
"""), printed=P(59))

s(60, "Summary", R("""
<ul>
<li><b>Textual Inversion</b>: un nuovo embedding di token, modello congelato.</li>
<li><b>DreamBooth / LoRA</b>: fine-tuning del denoiser, o solo di parametri a basso rango, per imparare un soggetto.</li>
<li><b>HyperDreamBooth</b>: prevedere i pesi personalizzati da un'immagine, poi un breve fine-tuning.</li>
<li><b>ZipLoRA / B-LoRA</b>: combinare soggetto e stile attraverso adattatori LoRA.</li>
<li><b>IP-Adapter</b>: un'immagine di riferimento come condizione, senza fine-tuning per soggetto.</li>
<li><b>ControlNet / AnimateDiff</b>: controllo della struttura spaziale e della coerenza temporale.</li>
<li><b>Noise Hypernetworks</b>: prevedere il rumore iniziale per migliorare la generazione senza aggiornare il modello.</li>
</ul>
<p>Manca nel riassunto un concetto che all'orale conta: la <b>prior preservation</b> di DreamBooth e il language drift che previene (slide 8–10). E il filo comune a ControlNet, AnimateDiff, LoRA: partire da un ramo che vale <b>zero</b>, così all'inizio il modello è identico a quello preaddestrato.</p>
"""), sec=("l28-fine", "Chiusura", "slide 60–62"), printed=P(60))

s(61, "References", R("""
<p>Bibliografia. Gli articoli da conoscere per nome: Gal et al. 2022 (Textual Inversion), Ruiz et al. 2023 (DreamBooth), Hu et al. 2022 (LoRA), Ruiz et al. 2024 (HyperDreamBooth), Alaluf et al. 2024 (Cross-Image Attention), Ye et al. 2023 (IP-Adapter), Shah et al. 2023 (ZipLoRA), Frenkel et al. 2024 (B-LoRA), Shenaj et al. 2025 (LoRA.rar), Zhang et al. 2023 (ControlNet), Tan et al. 2025 (OminiControl), Guo et al. 2024 (AnimateDiff), Eyring et al. 2025 (Noise Hypernetworks). Citati ma non trattati nelle slide: InstantID (Wang et al., 2024) e «Not All Layers Are Created Equal» (Shenaj et al., 2026) sui ranghi LoRA adattivi.</p>
"""), printed=P(61))

s(62, "Panoramica delle slide", R("""
<p>Non è una slide: è la pagina di panoramica con le miniature delle 61 pagine, generata automaticamente da Beamer.</p>
"""), printed=P(62))
