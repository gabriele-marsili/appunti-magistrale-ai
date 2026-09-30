# 12 — GAN: il discriminatore ottimo e cosa minimizza davvero il generatore

## Lezione di riferimento

`Lessons/GDL25 GAN.pdf` — *Generative Adversarial Networks*. Slide 9-11:
l'ottimizzazione alternata del gioco min-max, la separazione fra ascesa del
discriminatore e discesa del generatore, e la nota «Optimizing this doesn't
really work» sulla loss minimax con la sua sostituzione non-saturating. Sullo
sfondo, le slide 17-18 (mode collapse: «the gradient available to the generator
becomes tiny») e la slide 21 sull'effetto della loss di Wasserstein: entrambe
parlano dello stesso fenomeno che qui si misura.

## Il problema

Il deck scrive il gioco così:

    C = min_{θ_G} max_{θ_D}  E_x[log D_{θ_D}(x)] + E_z[log(1 − D_{θ_D}(G_{θ_G}(z)))]

e poi lo spezza in due passi alternati: ascesa su `θ_D`, discesa su `θ_G`. Le
domande che il deck lascia aperte sono due, e sono quelle a cui rispondi qui.

1. Fissato `G`, chi è il discriminatore che massimizza `C`? E che cosa vale `C`
   in quel punto?
2. Perché la discesa `min_{θ_G} E_z[log(1 − D(G(z)))]` «non funziona» mentre la
   variante `max_{θ_G} E_z[log D(G(z))]` sì?

Per rispondere senza addestrare nulla, l'ambientazione è 1D e discretizzata.
Sia `p_data` sia `p_g` sono densità già valutate sui punti di una griglia
(`GRID`, 1601 punti su [-8, 8]), e ogni valore atteso diventa una quadratura:

    E_{x~p}[f(x)] = ∫ p(x) f(x) dx ≈ integrate(p * f, grid)

Il rumore `z` non compare mai esplicitamente: `p_g` è già il push-forward di
`z ~ N(0,1)` attraverso `G_θ(z) = θ_0 + exp(θ_1)·z`, cioè `N(θ_0, exp(θ_1)²)`.
Il generatore ha due soli parametri e il suo gradiente si calcola per
differenze finite. Niente torch, e ogni numero è esatto a meno dell'epsilon
macchina.

## Cosa devi implementare

| funzione | cosa fa |
| --- | --- |
| `optimal_discriminator(p_data, p_g)` | `D*(x) = p_data/(p_data + p_g)`, con `0/0 → 0.5` |
| `discriminator_loss(D, p_data, p_g, grid)` | il valore del gioco `C(D, G)`, per quadratura |
| `generator_loss_minimax(D, p_g, grid)` | `E_{p_g}[log(1 − D)]`, da minimizzare |
| `generator_loss_nonsaturating(D, p_g, grid)` | `− E_{p_g}[log D]`, da minimizzare |
| `kl_divergence(p, q, grid)` | `KL(p‖q)` con la convenzione `0 log 0 = 0` |
| `jsd(p, q, grid)` | divergenza di Jensen-Shannon, in nat |
| `value_at_optimum(p_data, p_g, grid)` | `−log 4 + 2·JSD(p_data‖p_g)`, in forma chiusa |
| `generator_gradient(theta, p_data, grid, variant, h)` | gradiente della loss di `G` **a `D` congelato** |
| `train_generator(theta0, p_data, grid, variant, lr, n_steps, h)` | discesa giocattolo su `θ_G` |

## Specifica matematica

**Il valore del gioco.** Con `p_g` densità indotta da `G`,

    C(D, G) = ∫ p_data(x) log D(x) dx + ∫ p_g(x) log(1 − D(x)) dx

**Discriminatore ottimo.** L'integrando è *separabile in x*: il valore
`D(x) = d` in un punto non vincola i valori negli altri punti. Quindi il
massimo si trova punto per punto, derivando `p_data·log d + p_g·log(1 − d)`
rispetto a `d`:

    p_data/d − p_g/(1 − d) = 0    ⟹    D*(x) = p_data(x) / (p_data(x) + p_g(x))

La derivata seconda è `−p_data/d² − p_g/(1−d)² ≤ 0`: è un massimo. Dove
`p_data(x) + p_g(x) = 0` l'integrando è identicamente nullo e `d` è
indeterminato; per convenzione, in questo esercizio, `D*(x) = 0.5`.

**Valore all'ottimo.** Sostituendo `D*` e ponendo `m = (p_data + p_g)/2`,

    p_data log(p_data/(p_data+p_g)) + p_g log(p_g/(p_data+p_g))
        = p_data log(p_data/m) + p_g log(p_g/m) − (p_data + p_g) log 2

e integrando, usando `∫p_data = ∫p_g = 1`,

    C(D*, G) = −log 4 + 2·JSD(p_data ‖ p_g)

con

    JSD(p‖q) = ½ KL(p‖m) + ½ KL(q‖m),    m = (p+q)/2,    0 ≤ JSD ≤ log 2

Il minimo su `G` vale `−log 4 ≈ −1.3863` e si raggiunge **solo** per
`p_g = p_data`. Il massimo, `C(D*,G) = 0`, corrisponde a supporti disgiunti.

**Le due loss del generatore.** Il deck le scrive come

    minimax:          C_G = min_{θ_G} E_z[log(1 − D(G(z)))]
    non-saturating:   C_G = max_{θ_G} E_z[log D(G(z))]

Qui **entrambe** vanno restituite come quantità da minimizzare, cioè la seconda
col segno cambiato (`−E[log D]`), altrimenti confrontare i due gradienti non ha
senso.

**Perché la minimax satura.** Fissato `D`, la sensibilità delle due loss al
punto in cui il generatore mette massa è governata da

    ∂_x log(1 − D) = − D'/(1 − D)        ∂_x log D = D'/D

da cui l'identità

    ∂_x log(1 − D)  =  − [ D / (1 − D) ] · ∂_x log D

Dove il discriminatore è quasi perfetto sui campioni falsi si ha `D ≈ 0`, e il
fattore `D/(1−D) ≈ D` schiaccia il segnale della minimax di un fattore pari a
`D` stesso — che può valere `1e-7` o meno. La non-saturating, che deriva
`log D`, non subisce quel fattore: `log D` resta ripido anche quando `D` è
minuscolo. Questa è, quantitativamente, la «flat gradient when sample is plainly
fake» della slide 11.

**Convenzioni numeriche.** `safe_log` (fornita) pavimenta l'argomento del
logaritmo a `1e-300`: serve a realizzare `0 · log 0 = 0` senza `nan` e a
mantenere finiti i casi degeneri. Usa sempre `integrate` (fornita) per gli
integrali: le tolleranze dei test sono tarate su quella quadratura.

**Il vincolo che rende l'esercizio non banale.** In `generator_gradient` il
discriminatore va calcolato **una volta sola**, sul `p_g` corrente, e poi
**congelato** mentre le differenze finite perturbano `θ`. È il passo 2 della
slide 10: il discriminatore ha già fatto la sua ascesa e sta fermo. Se lo
ricalcolassi a ogni `θ` perturbato staresti differenziando `−log 4 + 2·JSD`,
cioè il valore *all'ottimo*, che è un'altra funzione e non satura.

## Perché questo esercizio

Scopre tre confusioni.

1. **Che il generatore stia minimizzando «una loss adversarial», qualunque cosa
   voglia dire.** Non è così: una volta che il discriminatore è al suo massimo,
   quello che il generatore minimizza è `−log 4 + 2·JSD(p_data‖p_g)`, cioè una
   divergenza fra distribuzioni. Il gioco min-max è una *procedura* per
   minimizzare una quantità che ha un nome preciso.
2. **Che minimax e non-saturating siano «la stessa cosa scritta in due modi».**
   Hanno lo stesso punto stazionario ideale e gradienti che differiscono, nel
   regime che conta, di sei ordini di grandezza. Il test lo misura.
3. **Che la saturazione dipenda dalla loss e non dal regime.** Con `p_g` e
   `p_data` ben sovrapposte i due gradienti sono confrontabili (rapporto ≈ 1.7):
   la minimax si spegne solo quando il discriminatore è quasi perfetto — che è
   esattamente ciò che succede a inizio addestramento e in mode collapse.

C'è poi un quarto punto, non evidente finché non lo si vede: `JSD ≤ log 2`
significa che a supporti disgiunti il valore all'ottimo è *costante* (vale 0) e
quindi il gradiente rispetto a `θ_G` è nullo comunque si scriva la loss del
discriminatore. È l'argomento che motiva la distanza di Wasserstein della
slide 20.

## Vincoli

Solo `numpy` e la standard library. Niente `torch`, `scipy`, `sklearn`,
`matplotlib`. Ogni sorgente di casualità passa dal `rng`
(`numpy.random.Generator`) ricevuto come argomento: mai `np.random.seed`, mai il
modulo `random`, mai `time`.

Non toccare `integrate`, `safe_log`, `make_grid`, `GRID`,
`gaussian_mixture_density`, `uniform_density`, `generator_density`,
`sample_from_grid_density`, `P_DATA`, `THETA_OVERLAP`, `THETA_FAR`: sono già
forniti e i test li usano.

`value_at_optimum` va implementata dalla forma chiusa (via `jsd`), **non**
chiamando `optimal_discriminator` + `discriminator_loss`: il test confronta i
due percorsi e se sono lo stesso codice non verifica nulla.

## Come autovalutarti

```bash
cd /home/claude/gdl/esercizi/12_gan_optimal_d
python3 -m pytest test_gan.py -v
```

Tutti i test devono passare. Ogni asserzione ha un messaggio che indica quale
errore concettuale l'ha fatta fallire; leggilo prima di correggere a caso.

## Tempo stimato

75 minuti. Le prime sette funzioni sono poche righe l'una e il grosso del tempo
se ne va sulle convenzioni (`0 log 0`, il caso `0/0`, il segno della
non-saturating). `generator_gradient` è breve ma va pensata: se il test sulla
saturazione dà un rapporto di 2 invece che di `1e6`, il problema è quasi sempre
che il discriminatore non è congelato.

## Domande d'orale collegate

1. Per `G` fisso, qual è il discriminatore ottimo e come lo si ricava? Perché la
   derivazione si può fare punto per punto invece che nello spazio delle
   funzioni?
2. Che cosa vale il gioco quando il discriminatore è ottimo, e che cosa dice
   questo su ciò che il generatore sta effettivamente minimizzando? Quanto vale
   il minimo e quando si raggiunge?
3. Perché la loss minimax del generatore satura, e perché la variante
   non-saturating no? La differenza è nell'ottimo o nel gradiente?
4. Che problema pone il fatto che la Jensen-Shannon sia limitata da `log 2`
   quando i supporti di `p_data` e `p_g` sono disgiunti, e in che modo la
   distanza di Wasserstein lo evita?
