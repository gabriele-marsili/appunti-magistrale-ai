# Note sulla soluzione

## Il filo conduttore

Il deck GDL25 presenta il GAN come una procedura: ascesa sul discriminatore,
discesa sul generatore, e una nota laconica («Optimizing this doesn't really
work») sul fatto che la seconda va riscritta. Questo esercizio riempie i due
buchi che la procedura lascia: chi è il discriminatore che vince l'ascesa, e
che cosa sta minimizzando il generatore quando quello ha già vinto. La risposta
alla prima domanda è una riga di calcolo differenziale; la risposta alla seconda
è che il generatore minimizza `−log 4 + 2·JSD(p_data‖p_g)`, cioè una divergenza
fra distribuzioni. Tutto il resto — saturazione, mode collapse, Wasserstein —
segue da lì.

L'ambientazione 1D su griglia serve a rendere queste due frasi *numeri*. Non
c'è nessuna approssimazione: `p_data` e `p_g` sono densità esatte valutate su
1601 punti, gli integrali sono trapezi con passo 0.01, e le identità teoriche
si verificano a `1e-12`.

## Il discriminatore ottimo, e perché la derivazione punto per punto è lecita

L'obiezione naturale è che stiamo massimizzando su uno spazio di *funzioni*,
non su un numero. Il punto che sblocca tutto è che l'integrando

    p_data(x) log d + p_g(x) log(1 − d)

non accoppia punti diversi: il valore che `D` assume in `x` non vincola quello
che assume in `x'`. Massimizzare l'integrale equivale a massimizzare
l'integrando in ogni `x` separatamente, e quello è un problema in una variabile
reale. Derivando: `p_data/d − p_g/(1−d) = 0` ⟹ `d = p_data/(p_data + p_g)`;
derivata seconda `−p_data/d² − p_g/(1−d)²`, sempre ≤ 0, quindi massimo.

Il test `test_optimal_discriminator_oracolo_massimizzazione_puntuale` fa
esattamente questo a forza bruta, su una griglia di 20001 valori di `d`, senza
mai usare la formula chiusa. È il modo più diretto di convincersi che la
derivazione è quella e non un'altra.

Il caso `0/0` non è un dettaglio implementativo mascherato: dove
`p_data = p_g = 0` l'integrando è identicamente nullo per *qualsiasi* `d`, e il
problema di massimo non seleziona niente. Qualunque valore in (0,1) sarebbe
legittimo; la convenzione `0.5` è la più leggibile («il classificatore non ha
informazione») e non cambia nessun integrale. La trappola è scrivere
`p_data / (p_data + p_g)` e lasciare che numpy produca `nan`: nel test sui
supporti disgiunti quel `nan` si propaga a `C(D*,G)` e a tutto il resto. La
soluzione usa `np.where(s > 0, p_data/np.where(s > 0, s, 1.0), 0.5)`: il
denominatore fittizio serve perché `np.where` valuta *entrambi* i rami e senza
di esso la divisione per zero avviene comunque (warning + `nan` scartato).

## La convenzione `0 log 0 = 0`

È la seconda fonte di `nan`. Compare in tre posti: `p_data · log D` dove
`p_data = 0` e `D = 0`; `p_g · log(1−D)` dove `p_g = 0` e `D = 1`; `p · log(p/m)`
dove `p = 0` e `m = 0`. Invece di scrivere tre `np.where`, la soluzione usa
`safe_log`, che pavimenta l'argomento a `1e-300`: `log(0)` diventa `−690.78`,
un numero finito, e moltiplicato per una densità nulla dà esattamente `0`.
Il pavimento è fornito nello skeleton apposta, perché non è la parte didattica
dell'esercizio ed è la classica cosa su cui si perde mezz'ora.

Con questa convenzione `KL(p‖q)` fra supporti disgiunti non è `+inf` ma
`≈ 690.09`: matematicamente sbagliato, numericamente utile, e il test lo
asserisce esplicitamente (`> 100`, finito) per non lasciare ambiguità.
Nella `JSD` il problema non si pone mai, perché `m = (p+q)/2` è nulla solo dove
lo sono entrambe.

## L'identità `C(D*,G) = −log 4 + 2·JSD`

Il conto è tre righe e vale la pena rifarlo a mano perché il `2` e il `log 4`
sono i due punti in cui si sbaglia. Con `m = (p_d + p_g)/2`:

    p_d log(p_d/(p_d+p_g)) = p_d log(p_d/m) − p_d log 2
    p_g log(p_g/(p_d+p_g)) = p_g log(p_g/m) − p_g log 2

Integrando, i due `log 2` danno `−2 log 2 = −log 4` perché *entrambe* le densità
integrano a 1, e i due termini di KL danno `KL(p_d‖m) + KL(p_g‖m) = 2·JSD`
perché la JSD ha i coefficienti `½` davanti. Se ottieni `−log 2 + JSD` hai
dimenticato che i termini sono due; se ottieni `−log 4 + JSD` hai lasciato i
`½`.

`test_value_at_optimum_coincide_col_percorso_numerico` confronta i due lati
dell'identità su cinque scenari. Perché il confronto sia esatto e non
approssimato serve che `∫p_data = ∫p_g = 1` *sotto la stessa quadratura*: per
questo `gaussian_mixture_density` e `uniform_density` rinormalizzano dividendo
per `integrate(p, grid)` invece di fidarsi delle costanti analitiche. Senza
quella rinormalizzazione l'identità sarebbe vera solo a `1e-4` e la tolleranza
`rtol=1e-6` fallirebbe — e uno studente passerebbe un'ora a cercare l'errore
nella formula giusta.

Da qui i due casi limite. `p_g = p_data`: `D* ≡ 0.5`, `JSD = 0`,
`C(D*,G) = 2 log(1/2) = −log 4` esatto — il generatore ha vinto e il
discriminatore è ridotto a tirare una moneta. Supporti disgiunti: `D*` vale 1
sui dati, 0 sui falsi, `JSD = log 2` (il suo massimo), e
`C(D*,G) = −log 4 + 2 log 2 = 0` — anche qui *esatto*, e non per caso: sui dati
`log D* = log 1 = 0` e sui falsi `log(1−D*) = log 1 = 0`.

## La saturazione: i numeri

Questa è la parte per cui l'esercizio esiste. Scenario `THETA_FAR`, cioè
`p_g = N(5.5, 0.3²)` contro `p_data = ½N(−1.5, 0.5²) + ½N(1.5, 0.5²)`. Il
discriminatore ottimo è praticamente perfetto sui campioni falsi:
`E_{p_g}[D*] = 2.84e−07`. Con `h = 1e−4`, `D` congelato:

| | minimax | non-saturating |
| --- | --- | --- |
| loss | `−4.395e−07` | `32.884` |
| `∂/∂θ_0` (media) | `+7.555e−06` | `+16.000` |
| `∂/∂θ_1` (log-sigma) | `−1.133e−05` | `−0.640` |
| ‖∇‖ | `1.362e−05` | `1.601e+01` |

Rapporto: **1.18e+06**, sei ordini di grandezza. Controprova sullo scenario
`THETA_OVERLAP` (`p_g = N(0, 1.2²)`, buona copertura dei dati): ‖∇‖ vale
`0.349` per la minimax e `0.591` per la non-saturating, rapporto `1.70`. La
saturazione non è una proprietà della loss minimax, è una proprietà del
*regime* — e il regime «discriminatore quasi perfetto» è esattamente quello in
cui si parte e quello in cui si finisce col mode collapse (slide 18: «the
gradient available to the generator becomes tiny»).

Il meccanismo, in una riga: `∂_x log(1−D) = −[D/(1−D)]·∂_x log D`. La minimax
vede la stessa pendenza della non-saturating, moltiplicata per `D`. Con
`D ~ 2.8e−7` il fattore di soppressione previsto è `~3.5e+06`, dello stesso ordine
del `1.18e+06` misurato. Non coincidono esattamente perché il gradiente residuo
della minimax non viene dalla regione dove `p_g` ha massa, ma dalla coda
sinistra di `p_g` che sfiora la moda destra dei dati: è l'unico posto in cui la
minimax riceve ancora segnale, ed è una frazione infinitesima dei campioni
generati.

La discesa giocattolo (`lr = 0.01`, 60 passi, da `θ = (5.5, log 0.3)`) rende la
cosa visibile:

| | minimax | non-saturating |
| --- | --- | --- |
| media `θ_0` | `5.5 → 5.4999955` | `5.5 → 1.974` |
| sigma | `0.300 → 0.300002` | `0.300 → 0.369` |
| loss | `−4.3953e−07 → −4.3958e−07` | `32.884 → 1.537` |
| ‖∇‖ primo → ultimo | `1.3616e−05 → 1.3617e−05` | `16.01 → 1.32` |

La minimax non si muove: dopo 60 passi la media si è spostata di `4.5e−06`, e
la norma del gradiente è la stessa del primo passo, perché non è andata da
nessuna parte. La non-saturating arriva a `1.974`, cioè addosso alla moda destra
dei dati (`+1.5`), e **ignora completamente quella sinistra**: mode collapse in
piena regola, ottenuto senza addestrare nulla, semplicemente perché il
generatore giocattolo è unimodale e la discesa è locale.

## L'errore che il test `test_generator_gradient_congela_il_discriminatore` prende

È l'errore concettuale più costoso dell'esercizio. Nel ciclo del GAN il
discriminatore viene aggiornato e poi *sta fermo* mentre il generatore fa il suo
passo. Se nelle differenze finite si ricalcola `D*` per ogni `θ` perturbato, si
sta derivando `C(D*_θ, G_θ)`, cioè `−log 4 + 2·JSD(p_data‖p_g(θ))`: una funzione
diversa, che **non satura** (la JSD ha gradiente ragionevole anche a supporti
quasi disgiunti, finché non diventano esattamente disgiunti). Il test misura
entrambe le versioni sullo scenario sovrapposto e le confronta: per la minimax
vengono `−0.3486` (D congelato, corretta) e `−0.1623` (D mobile, sbagliata),
un fattore 2.15. Su `THETA_FAR` la differenza è meno vistosa in valore assoluto
(`1.362e−05` contro `5.337e−06`) ma il rapporto è ancora 2.55.

Detto altrimenti: la saturazione è un fenomeno del *gradiente a D fisso*.
Se ti concedi di muovere anche il discriminatore, il min-max sembra funzionare
benissimo — e questo è precisamente il motivo per cui il problema non si vede
finché non si scrive il codice.

## Trappole minori

Il segno della non-saturating. La slide 11 la scrive come **massimizzazione** di
`E[log D]`; qui è richiesta come `−E[log D]`, da minimizzare, altrimenti i due
gradienti non sono confrontabili (uno punterebbe in salita e l'altro in discesa)
e la discesa `θ ← θ − lr·∇` andrebbe nella direzione sbagliata. Il test
asserisce `mm ≤ 0 < ns` con `D` costante, che prende l'errore subito.

`value_at_optimum` implementata come
`discriminator_loss(optimal_discriminator(...), ...)`. Funziona, passa quasi
tutti i test, ma svuota `test_value_at_optimum_coincide_col_percorso_numerico`,
che diventa una tautologia. Lo skeleton lo vieta esplicitamente nella docstring;
è il tipo di scorciatoia che un test non può impedire, solo scoraggiare.

La quadratura. Usare `np.sum(p * f) * dx` invece di `np.trapezoid` sposta i
risultati di qualche `1e-3` sui bordi della griglia e fa fallire le tolleranze
strette. Per questo `integrate` è fornita: non è la parte interessante e non
deve diventare una fonte di rumore.

Infine, `train_generator` deve restituire `n_steps + 1` valori di loss e
`n_steps` norme di gradiente: la loss va registrata *prima* di ogni passo e una
volta ancora alla fine. Registrarla dopo il passo perde lo stato iniziale ed è
il motivo per cui il test controlla `thetas[0] == theta0` con tolleranza zero.
