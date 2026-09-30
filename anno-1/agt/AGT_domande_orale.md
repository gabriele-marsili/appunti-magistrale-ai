# AGT — Domande d'orale e informazioni sull'esame

Orale (colloquio da non frequentante) — venerdì 11 settembre 2026.
Fonti: chat Telegram del gruppo `[AGT] Algorithmic Game Theory` (feb 2025 – set 2026), pagina esami del prof (`pages.di.unipi.it/bigi/dida/agt/exams.html`), slide L1–L24, dispensa 2024/25.

---

## 1. Cosa dice il gruppo Telegram sull'orale

Nessuno nel gruppo ha mai postato una lista di domande specifiche fatte agli appelli: le informazioni sono tutte sul *formato* dell'orale. Testimonianze dirette di chi l'ha sostenuto (citazioni letterali):

| Data | Chi | Cosa dice |
|---|---|---|
| 18.10.2025 | Riccardo | «Le dimostrazioni le fa solo nel corso a matematica, qui **al massimo ti fa uno sketch**» |
| 29.10.2025 | Nicola Pitzalis | «lui è molto tranquillo come prof» · «ci sono comunque **un bel po' di cose da sapere, da ricordare più che altro**» |
| 06.02.2026 | Nicola Pitzalis (orale fatto) | «ti chiede di **parlare di un argomento in maniera generica** e poi in base a ciò che esponi propone domande» · «super chill» · «ti lascia seguire la direzione che preferisci» · «io ho impostato ogni domanda in: **definizioni principali – esempio di riferimento – digressione su un sotto-argomento**; lui poi ti veicola un po' verso ciò che gli interessa» · «cerca di integrarsi a come lo esponi, senza essere invadente» · «**non mi ha fatto fare nessun esercizio preciso, mi ha chiesto di costruire esempi ad hoc**, al massimo» |
| 31.03.2026 | sara (orale "tradizionale" da non frequentante) | «non ti chiede i dettagli anzi **ti chiede un argomento molto ampio (ad esempio, i giochi sequenziali oppure il two sided matching)** e poi ti lascia parlare di quello che vuoi e **ti lascia scrivere alla lavagna se vuoi** (cioè non è lui che ti chiede formule matematiche), in generale è anche **abbastanza alto con i voti**» |
| 24.06.2026 | elia zanchetta | risposta alla mail per la data dopo ~7 giorni (era in viaggio): se non risponde, rimandare la mail |
| 08.09.2026 | WhoIsMars | ha l'orale venerdì 11 e non sa se l'orario è quello su Valutami: **scrivere al prof per confermare l'orario** |

Dalla pagina esami del prof: colloquio di **circa 45 minuti**, solo in presenza, unica data concordata con tutti i candidati; compilare il **questionario di valutazione su esami.unipi.it prima dell'esame**.

### Cosa ne segue per la preparazione

1. Le domande d'apertura sono **macro-argomenti** ("mi parli dei giochi sequenziali", "il two-sided matching", "i giochi cooperativi", "il bargaining"). Bisogna avere pronta, per ognuno dei ~10 macro-argomenti sotto, un'esposizione di 5–8 minuti a struttura fissa: **definizioni → esempio di riferimento → risultato principale (enunciato + sketch) → sotto-argomento in cui portare la conversazione**.
2. Le domande di approfondimento nascono da ciò che dici: **non aprire porte che non sai chiudere** (non citare un teorema di cui non sai lo sketch).
3. Dimostrazioni: sketch, non dettagli. Ma gli sketch dei teoremi centrali (Nash/Nikaido–Isoda, minimax, potential games, Zermelo/backward induction, Nash bargaining, Gale–Shapley, Bondareva–Shapley, unicità del nucleolo, assiomi di Shapley) vanno saputi.
4. Esempi ad hoc: saper **costruire al volo** un gioco 2×2 con 0/1/2 NE puri, un gioco con core vuoto, un'istanza di matching con due matching stabili, un problema di bargaining in cui Nash ≠ Kalai–Smorodinsky.
5. Molto è "da ricordare": nomi, date, formule (Rubinstein, Shapley, SSPI/BPI), assiomi.

---

## 2. I macro-argomenti d'apertura (elenco da cui il prof pesca)

| # | Macro-argomento | Lezioni | Esempio di riferimento da portare | Sotto-argomento verso cui virare |
|---|---|---|---|---|
| A | Giochi in forma normale e Nash equilibrium | L1–L3 | Dilemma del prigioniero, BoS, RPS | esistenza (Nikaido–Isoda), NE misti |
| B | Dominanza, IESDS, razionalizzabilità, sicurezza | L4–L5 | Hotelling, gioco con IESDS che isola l'NE | maximin vs NE nei giochi zero-sum |
| C | Strategie miste, esistenza, minimax | L6 | RPS, matching pennies | von Neumann e LP |
| D | Best response dynamics e potential games | L7–L8 | esempio delle slide con ciclo di Jacobi, dilemma del prigioniero | convergenza Gauss-Seidel, caratterizzazione con cicli |
| E | Learning: fictitious play, regret matching | L9 | RPS con fictitious play | convergenza a correlated eq. |
| F | Giochi sequenziali: SPE, backward induction, Stackelberg | L10–L13 | Sequential BoS, centipede, chain store, Stackelberg duopoly | alfa-beta, Stackelberg–Nash ottimistico/pessimistico |
| G | Bargaining assiomatico | L14–L15 | divide-the-euro, bankruptcy | Kalai–Smorodinsky vs Nash (IIA vs monotonicity) |
| H | Nash program e bargaining sequenziale | L15–L16 | ultimatum, two-stage, Rubinstein | limite → generalized Nash bargaining solution |
| I | Exchange economies, one-sided matching, TTC | L17 | house allocation, ciclo TTC | core e strategy-proofness |
| J | Two-sided matching, Gale–Shapley | L18 | istanza 3×3 con due matching stabili | proponent-optimality, manipolabilità, Gibbard–Satterthwaite |
| K | Giochi cooperativi TU: core | L19–L22 | max-flow game, gloves game, gioco ρ a 3 giocatori | Bondareva–Shapley, market games, strutture coalizionali |
| L | Nucleolo e least core | L23 | bankruptcy game | schema di Maschler (LP successivi) |
| M | Valore di Shapley e indici di potere | L24 | gloves, ONU | assiomi e unicità, SSPI vs BPI |

Le tre famiglie di solution concepts da tenere come spina dorsale: (1) non-cooperative (NE, SPE, correlated, Stackelberg); (2) bargaining (Nash, KS, Rubinstein, Baron–Ferejohn); (3) cooperative TU (core, nucleolo, Shapley, indici di potere). Il **Nash program** è il ponte tra (1) e (2).

---

## 3. Domande — L1–L13 (parte non cooperativa)

Formato: **domanda** → traccia in 2–4 righe. Le tracce rimandano alla dispensa (`dispensa_AGT.pdf`, cap. 1–13).

### L1–L2 — Introduzione, forma normale ed estesa

**1. Che cos'è un gioco in forma normale? E in forma estesa? Quando si usa l'una o l'altra?**
Forma normale: $(N,(S_i),(u_i))$, giocatori, insiemi di strategie, utilità sui profili; mosse simultanee. Forma estesa: albero con nodi decisionali, information set, payoff alle foglie; mosse sequenziali. Ogni gioco in forma estesa ha una forma normale (strategie = piani completi), ma si perde la struttura temporale. Esempi: sequential allocation, Cournot con bene indivisibile.

**2. Enunci il teorema di Zermelo.**
In un gioco finito a informazione perfetta a due giocatori, a somma zero, senza pareggi: uno dei due ha una strategia vincente (con pareggi: o uno vince o entrambi possono forzare il pareggio). Sketch: induzione sull'altezza dell'albero (backward induction). Esempio Chomp con l'argomento di strategy stealing. Collega ai giochi sequenziali (L11) e a minimax/alfa-beta (L12).

**3. Classifichi i giochi (cooperativi/non, simultanei/sequenziali, zero-sum, informazione perfetta/imperfetta, completa/incompleta).**
Elencare gli assi e collocare gli esempi del corso: RPS (zero-sum simultaneo), sequential BoS (sequenziale, informazione perfetta), TU games (cooperativi).

**4. Descriva il dilemma del prigioniero, BoS, Hawk–Dove, RPS: quali sono gli NE puri?**
PD: unico NE (D,D), dominante, non Pareto-efficiente. BoS: due NE puri + uno misto. Hawk–Dove: due NE puri asimmetrici + misto. RPS: nessun NE puro, unico misto uniforme.

**5. Duopolio di Cournot con bene indivisibile / sequential allocation: come si modella e cosa si trova?**
Quantità come strategie, prezzo inverso della domanda, best response di ciascuno, NE all'intersezione. Confronto poi con Stackelberg (L10) e oligopolio con leader (L12).

### L3 — Utilità attesa e Nash equilibrium

**6. Definisca l'equilibrio di Nash (puro). Interpretazione con le best response.**
$s^*$ è NE se $u_i(s^*)\ge u_i(s_i,s^*_{-i})$ per ogni $i$, $s_i$; equivalentemente $s^*_i\in BR_i(s^*_{-i})$ per ogni $i$: punto fisso della corrispondenza di best response. Esempio: BoS.

**7. Perché l'utilità attesa (von Neumann–Morgenstern) è necessaria per parlare di strategie miste?**
Le strategie miste sono lotterie sui profili; serve una funzione di utilità lineare nelle probabilità per confrontarle. Le utilità sono definite a meno di trasformazioni affini positive (collegamento con l'assioma di invarianza nel bargaining, L14).

**8. Giochi zero-sum simmetrici: cosa si può dire del valore?**
Nel gioco simmetrico a somma zero il valore è 0; se esiste un NE puro è un punto di sella. RPS come esempio.

### L4–L5 — Dominanza, IESDS, razionalizzabilità, sicurezza

**9. Strategia strettamente/debolmente dominata; relazione con gli NE.**
Una strategia strettamente dominata non è mai usata in un NE (nemmeno misto); una debolmente dominata può esserlo. Esempio 2×2 in cui l'eliminazione di strategie debolmente dominate fa perdere un NE.

**10. IESDS: l'ordine di eliminazione conta? E per le debolmente dominate?**
Per le strettamente dominate no (risultato finale unico); per le debolmente dominate sì. Se IESDS lascia un solo profilo, quello è l'unico NE (gioco dominance-solvable).

**11. Che cos'è la razionalizzabilità / IENBR?**
Eliminazione iterata delle strategie che non sono mai best response. In 2 giocatori coincide con IESDS (con dominanza da strategie miste). Gli NE sono profili di strategie razionalizzabili.

**12. Strategie di sicurezza (maximin): definizione e rapporto con NE.**
$\max_{s_i}\min_{s_{-i}}u_i$; garantisce un livello a prescindere dagli altri. In generale il valore maximin ≤ payoff di NE; nei giochi zero-sum a strategie miste maximin = NE (minimax, L6).

**13. Gioco di Hotelling: modello e NE.**
Due candidati scelgono una posizione in $[0,100]$, gli elettori (uniformi) votano il più vicino; l'unico NE è $x_1=x_2=50$. Si ottiene per IESDS: al primo passo si eliminano le posizioni $<25$ e $>75$, poi iterativamente fino a $\{50\}$.

### L6 — Strategie miste, esistenza, minimax

**14. Come si calcola un NE misto in un gioco 2×2? Principio di indifferenza.**
Ogni strategia nel supporto deve dare la stessa utilità attesa; risolvere il sistema. Esempio BoS: $(2/3,1/3)$ ecc. Osservazione: la mia probabilità serve a rendere indifferente *l'avversario*.

**15. Enunci il teorema di Nash e il teorema di Nikaido–Isoda; sketch.**
Nikaido–Isoda: $S_i$ convessi compatti, $u_i$ continue e quasi-concave in $s_i$ ⇒ esiste NE. Nash: ogni gioco finito ha un NE misto (i simplessi sono convessi compatti e l'utilità attesa è lineare in $\sigma_i$). Sketch: le ipotesi di Nikaido–Isoda valgono per il gioco misto esteso (simplessi compatti e convessi, utilità attese multilineari, quindi continue e quasi-concave).

**16. Teorema minimax di von Neumann: enunciato, sketch e significato.**
In un gioco zero-sum finito $\max_x\min_y x^TAy=\min_y\max_x x^TAy$ = valore del gioco; gli NE sono le coppie di strategie maximin/minimax, sono intercambiabili e danno lo stesso payoff. Calcolo via LP.

### L7–L8 — Best response dynamics e potential games

**17. Descriva la best response dynamics (Jacobi vs Gauss-Seidel).**
Jacobi: tutti aggiornano simultaneamente; Gauss-Seidel: uno alla volta. Punti fissi = NE puri. Jacobi può ciclare anche quando esiste un NE (esempio di coordinamento); Gauss-Seidel converge nei potential games.

**18. Definisca i potential games (exact/ordinal). Perché hanno sempre un NE puro?**
Esiste $P$ tale che $u_i(s_i,s_{-i})-u_i(s'_i,s_{-i})=P(s_i,s_{-i})-P(s'_i,s_{-i})$ (exact) o stesso segno (ordinal). Il massimo di $P$ (gioco finito) è un NE puro. BRD asincrona aumenta strettamente $P$ ⇒ termina in un NE (finite improvement property).

**19. Caratterizzazione dei potential games tramite cicli.**
Un gioco finito è un exact potential game sse per ogni ciclo chiuso di lunghezza 4 (cambio di due giocatori) la somma alternata delle variazioni di utilità è nulla. Saper fare la verifica su un 2×2.

**20. Esempi di potential games del corso.**
Giochi di coordinamento, dilemma del prigioniero, gli esempi numerici delle slide L7–L8; saper esibire la funzione potenziale e verificarla sui cicli.

### L9 — Learning: fictitious play e regret matching

**21. Che cos'è il fictitious play? Quando converge?**
Ogni giocatore gioca best response alla frequenza empirica delle mosse passate degli altri. Le frequenze empiriche convergono all'insieme degli NE in: zero-sum a 2 giocatori (Robinson, tasso $O(1/\sqrt{k})$), $2\times2$ con diagonal property (Miyasawa), $2\times n$ non degeneri (Berger), giochi risolvibili per IESDS (Milgrom–Roberts), potential games ordinali (Monderer–Shapley). Non converge in generale: "gentle RPS". Convergono le frequenze, non le azioni.

**22. Regret matching: definizione di regret, regola di aggiornamento, risultato di convergenza.**
Regret cumulato $R_t(a)=\sum_\tau[u(a,s_{-i}^\tau)-u(s_i^\tau,s_{-i}^\tau)]$; si gioca $a$ con probabilità proporzionale a $\max(R_t(a),0)$. Il regret medio va a 0 come $O(1/\sqrt{T})$ e la distribuzione empirica dei profili converge all'insieme degli **equilibri correlati** (non necessariamente NE).

**23. Definisca l'equilibrio correlato e lo confronti con NE.**
Distribuzione $\mu$ sui profili tale che, ricevuta la raccomandazione, nessuno vuole deviare. Ogni NE (prodotto) è correlato; l'insieme dei correlati è un politopo (LP). Esempio: semaforo / BoS con moneta pubblica.

### L10–L13 — Giochi sequenziali, SPE, Stackelberg

**24. Gioco di Stackelberg: definizione e differenza da Cournot.**
Leader sceglie per primo anticipando la best response del follower; risolto per backward induction. Nel duopolio il leader ottiene di più che in Cournot (first-mover advantage); confronto quantità/prezzi nella tabella degli oligopoli (L12).

**25. Definisca sottogioco e SPE. Perché l'NE non basta nei giochi sequenziali?**
SPE: NE in ogni sottogioco. Elimina le minacce non credibili (chain store paradox). Esempio: sequential BoS ha più NE ma un solo SPE; veto driven choice.

**26. Backward induction: procedura, risultato e limiti.**
In un gioco finito a informazione perfetta la backward induction produce un SPE in strategie pure (costo $O(|V|)$, albero esponenziale nel numero di mosse). Limiti: centipede game (esito controintuitivo), informazione imperfetta (serve il concetto di information set), forward induction.

**27. Alfa-beta pruning: cosa fa e perché è corretto; ruolo dell'ordinamento.**
Minimax con potatura dei rami che non possono cambiare il valore (bound $\alpha,\beta$); stesso valore di minimax; l'ordinamento dei figli (best-first) determina quanto si pota. Deep guessing / funzioni di valutazione quando l'albero è troppo profondo (scacchi, Deep Blue).

**28. Giochi multi-stage e oligopolio con un leader e molti follower.**
Follower giocano Cournot dato il leader; leader massimizza anticipando l'NE dei follower. Tabella comparativa: monopolio, Cournot, Stackelberg, oligopolio con leader.

**29. Stackelberg–Nash games: definizione, working assumption, equilibri ottimistici e pessimistici.**
Un leader, $n$ follower che giocano un gioco di Nash $G(x_1)$. Se $NE(x_1)$ non è singleton: OSN ($\max$ sul migliore NE) e PSN ($\max\min$). Esistenza: finiti ⇒ entrambi esistono se $NE(x_1)\neq\emptyset$; continui ⇒ Nikaido–Isoda + Weierstrass per l'ottimistico.

**30. Esempio di pool mining nelle blockchain.**
Piattaforma (leader) fissa la ricompensa $r$; miner (follower) scelgono la potenza $p_i$ in un Cournot con domanda inversa $r/t$. Saper impostare le utilità e dire com'è l'equilibrio nel caso omogeneo.

---

## 4. Domande "trasversali" (collegamenti che il prof apprezza)

**31. Che cosa hanno in comune NE, core e Nash bargaining solution?** Tutti sono definiti come "nessuno (individuo / coalizione) ha incentivo a deviare" o come punto fisso/argmax; differiscono su chi può deviare e con quali vincoli (accordi vincolanti o no).

**32. Che cos'è il Nash program?** Fondare le soluzioni cooperative/assiomatiche (Nash bargaining) come esiti di equilibrio (SPE) di giochi non cooperativi: demand game e Rubinstein → NBS generalizzata.

**33. Perché il core può essere vuoto e cosa si fa in quel caso?** Bondareva–Shapley; least core, nucleolo (sempre non vuoto e unico), Shapley (sempre definito, non necessariamente nel core).

**34. Quando core, nucleolo e Shapley coincidono / differiscono?** Esempi: gloves game (core = nucleolo = (0,0,1), Shapley (1/6,1/6,2/3)); gioco simmetrico.

**35. In quali punti del corso compare la programmazione lineare?** Minimax (L6), equilibri correlati (L9), core e Bondareva–Shapley (L21), least core e nucleolo (L22–23).

**36. Quali risultati di impossibilità/manipolabilità ha visto?** Gibbard–Satterthwaite (social choice), manipolabilità di Gale–Shapley per il lato ricevente (Roth), strategy-proofness di TTC e del lato proponente in DA.

# Domande d'orale — L14, L15, L16 (Bargaining)

Corso: Algorithmic Game Theory (prof. Bigi, Unipi, LM Informatica 2025/26).
Per ogni domanda: traccia di risposta in 2–4 righe (definizione chiave · esempio · collegamento).

---

## L14 — Bargaining assiomatico: soluzione di Nash, Kalai–Smorodinsky, egalitaria

**1. Che cos'è un problema di bargaining? Quali sono gli assiomi di Nash sul dato?**
Una coppia $(U,u^*)$: $U \subseteq \mathbb{R}^n$ insieme degli outcome fattibili (vettori di pay-off), $u^*$ il *disagreement point*, cioè l'esito se non si raggiunge un accordo. Assiomi: (i) $U$ convesso e compatto; (ii) esiste $u \in U$ con $u > u^*$ componente per componente. La convessità corrisponde alla possibilità di fare lotterie fra accordi; (ii) garantisce che cooperare conviene strettamente a tutti.
*Collegamento*: è un solution concept **assiomatico** — non si modellano le mosse, come nei giochi TU (core, nucleolo, Shapley).

**2. Che cos'è una bargaining function? Perché si chiama solution concept?**
Detta $\mathcal{B}$ la famiglia dei bargaining games che soddisfano (i)–(ii), una bargaining function è una qualunque $\psi:\mathcal{B}\to\mathbb{R}^n$. È un meccanismo/arbitrato che a ogni problema associa un esito, esattamente come il valore di Shapley associa a ogni gioco TU un'allocazione.
*Collegamento*: la logica "lista di assiomi ⇒ soluzione unica" è la stessa della caratterizzazione di Shapley.

**3. Da dove nascono i problemi di bargaining? Fai due esempi.**
(a) *Cooperazione in giochi non cooperativi*: se i giocatori possono accordarsi sulle strategie miste, $U$ è l'inviluppo convesso dei vettori di pay-off — es. $U=\mathrm{conv}\{(2,2),(3,0),(4,1),(1,0),(1,1),(3,1)\}$, convesso e compatto per costruzione.
(b) *Bankruptcy*: attivo $a$, debiti $d_i$ con $\sum_i d_i > a$; $U=\{u\ge 0: \sum_k u_k \le a,\ u_i\le d_i\}$, $u^*=0$.
*Collegamento*: il bankruptcy problem è anche un gioco TU, e lì si confronta con nucleolo e Shapley.

**4. Elenca le sei proprietà desiderabili per una bargaining function.**
Feasibility ($\psi\in U$); rationality ($\psi\ge u^*$); Pareto optimality ($u\in U, u\ge\psi \Rightarrow u=\psi$); IIA (se $\widehat U\subseteq U$ e $\psi(U,u^*)\in\widehat U$ allora $\psi(\widehat U,u^*)=\psi(U,u^*)$); covarianza per trasformazioni affini positive; symmetry (se $U$ è $ij$-simmetrico e $u^*_i=u^*_j$ allora $\psi_i=\psi_j$).
*Nota*: la covarianza affine dice che la soluzione non deve dipendere dalla scala e dall'origine con cui ciascun giocatore misura la propria utilità.

**5. Enuncia il teorema di Nash (1950) e spiega perché il massimo esiste ed è unico.**
Esiste un'unica $\psi$ che soddisfa tutti e sei gli assiomi: $\psi^{na}(U,u^*)=\arg\max\{\prod_k(x_k-u^*_k): x\in U, x\ge u^*\}$. Esistenza per Weierstrass ($g$ continua su compatto); unicità perché l'argmax coincide con quello di $\sum_k \log(x_k-u^*_k)$, strettamente concava su un convesso.
*Collegamento*: la trasformazione logaritmica riappare nella versione generalizzata (L15) con i pesi $\alpha_k$.

**6. Perché $\psi^{na}$ soddisfa gli assiomi? (verifica)**
Feasibility e rationality sono per costruzione; Pareto optimality perché $g$ è strettamente crescente in ogni coordinata su $\{x>u^*\}$; IIA perché il massimizzatore su $U$ che sta in $\widehat U$ è massimizzatore anche su $\widehat U$; covarianza affine perché $g$ cambia solo per la costante positiva $\prod_k\alpha_k$ e l'argmax non si muove; simmetria dalla simmetria di $g$ più l'unicità del massimo.
*Nota*: l'unicità della bargaining function (parte non banale del teorema) è data per acquisita nel corso.

**7. Perché la Pareto optimality è essenziale? Che cosa succede senza?**
Se $u^*\in U$, la funzione costante $\psi\equiv u^*$ soddisfa tutte le altre cinque proprietà. Anzi, $\psi^{na}$ e $\psi\equiv u^*$ (con tutte le loro combinazioni convesse) sono le uniche a soddisfare i cinque assiomi restanti.
*Collegamento*: senza efficienza il pacchetto assiomatico non ha mordente — stesso ruolo dell'efficienza nella caratterizzazione del valore di Shapley.

**8. Significato geometrico della soluzione di Nash e caratterizzazione di Moulin.**
Per $n=2$, $g(x)=(x_1-u^*_1)(x_2-u^*_2)$ è l'area del rettangolo di vertici opposti $u^*$ e $x$: Nash massimizza quell'area. Moulin (1983): $\psi^{na}$ è anche l'unica bargaining function che soddisfa feasibility, **midpoint domination** ($\psi\ge \sum_i d^i/n$, con $d^i$ il massimo per $i$ lasciando gli altri a $u^*$) e IIA.
*Collegamento*: la midpoint domination implica la rationality ed è un benchmark di equità esplicito.

**9. Che cos'è la comprehensiveness e perché serve?**
$U$ è $u^*$-comprehensive se $x\in U$, $u^*\le y\le x$ implica $y\in U$ (equivalentemente $(U-\mathbb{R}^n_+)\cap(u^*+\mathbb{R}^n_+)=U$): si può sempre "buttar via" utilità restando sopra il disaccordo. Vale sempre $\psi^{na}(U,u^*)=\psi^{na}((U-\mathbb{R}^n_+)\cap(u^*+\mathbb{R}^n_+),u^*)$.
*Collegamento*: è ipotesi necessaria nel teorema di Kalai (1977) sulla soluzione egalitaria.

**10. La critica di Luce–Raiffa all'IIA: spiegala con l'esempio numerico.**
$U=\{x\ge 0: x_1/10+x_2/4\le1\}$, $u^*=(0,0)$: massimizzando $x_1x_2$ si trova $\psi^{na}=(5,2)$. Su $\widehat U = U\cap\{x_1\le 5\}$ la soluzione resta $(5,2)$ per IIA. Ma in $U$ le aspettative massime sono $(10,4)$ e ciascuno prende metà (sembra equo), mentre in $\widehat U$ sono $(5,4)$: il giocatore 1 prende **tutto** il suo massimo e il 2 solo metà.
*Collegamento*: è la motivazione diretta della soluzione di Kalai–Smorodinsky.

**11. Punto utopia, weak monotonicity e soluzione di Kalai–Smorodinsky.**
$m(U)_i=\max\{x_i:(x_i,x_{-i})\in U\}$. Weak monotonicity: $\widehat U\subseteq U$ e $m(\widehat U)=m(U)$ implicano $\psi(\widehat U,u^*)\le\psi(U,u^*)$. Per $n=2$, $\psi^{ks}$ è l'intersezione del segmento $u^*\!-\!m(U)$ con la frontiera di $U$: i guadagni sono proporzionali ai massimi possibili. È l'unica $\psi$ con feasibility, rationality, Pareto optimality, symmetry e weak monotonicity.
*Esempio*: su $U$ sopra, $\psi^{ks}=(5,2)=\psi^{na}$; su $\widehat U$, $\psi^{ks}=(10/3, 8/3)\ne(5,2)$.

**12. Il risultato di impossibilità di Roth (1979): enunciato e controesempio.**
Per $n\ge3$ non esiste alcuna $\psi$ con feasibility, rationality, Pareto optimality, symmetry e weak monotonicity. Controesempio: $u^*=0$, $S=\mathrm{conv}\{(0,0,0),(1,0,1),(0,1,1)\}\subseteq T=\{u\ge0: u_i\le1, \sum u_i\le 2\}$, con $m(S)=m(T)=(1,1,1)$. Su $T$ (simmetrico) Pareto+simmetria danno $(2/3,2/3,2/3)$; su $S$ la Pareto optimality forza $[\psi(S,u^*)]_3=1 > 2/3$: contraddizione.
*Collegamento*: tipico "impossibility theorem", come Arrow e Gibbard–Satterthwaite.

**13. Strong monotonicity, soluzione egalitaria e teorema di Kalai (1977).**
Strong monotonicity: $\widehat U\subseteq U \Rightarrow \psi(\widehat U,u^*)\le\psi(U,u^*)$ (senza vincolo sul punto utopia). La soluzione egalitaria è $u^*+\tau(1,\dots,1)$ con $\tau=\min_i\max\{x_i-u^*_i:x\in U\}$: guadagni uguali. Kalai: è l'unica $\psi$ con feasibility, rationality, **weak** Pareto optimality, symmetry e strong monotonicity, se $U$ è $u^*$-comprehensive.
*Collegamento*: si indebolisce la Pareto optimality a quella debole e si rafforza la monotonicità da debole a forte; sostituendo $(1,\dots,1)$ con $p>0$ si ha la soluzione proporzionale — strong monotonicity ≈ proporzionalità.

---

## L15 — Nash generalizzato, Nash program, demand game, ultimatum

**1. Che cos'è la soluzione di Nash generalizzata? Enunciato.**
Se $\psi$ soddisfa feasibility, rationality, **weak** Pareto optimality, affine positive covariance e IIA (ma **non** la simmetria), allora esistono *bargaining powers* $\alpha_k\ge0$ tali che $\psi(U,u^*)=\arg\max\{\prod_k(x_k-u^*_k)^{\alpha_k}: x\in U, x\ge u^*\}$.
*Collegamento*: con $\alpha_k$ tutti uguali si ritrova la soluzione di Nash: la simmetria è esattamente ciò che impone pesi uguali.

**2. Divide the euro con bargaining powers: svolgi il conto.**
$n=2$, $U=\{x\ge0: x_1+x_2\le1\}$, $u^*=(0,0)$. Massimizzo $\alpha_1\log x_1+\alpha_2\log(1-x_1)$: da $\alpha_1/x_1=\alpha_2/(1-x_1)$ segue $\psi=(\alpha_1/(\alpha_1+\alpha_2),\ \alpha_2/(\alpha_1+\alpha_2))$.
*Collegamento*: l'euro si divide in proporzione al potere contrattuale; con $\alpha_1=\alpha_2$ si ha $(1/2,1/2)$.

**3. Che cos'è il Nash program?**
È il progetto di **giustificare** i solution concept cooperativi come equilibri (tipicamente SPE) di giochi non cooperativi espliciti: si costruisce una procedura di contrattazione le cui soluzioni strategiche coincidono con la soluzione assiomatica.
*Collegamento*: è il **ponte** fra bargaining assiomatico (L14) e giochi in forma estesa / SPE; il compimento è il teorema di Rubinstein al limite $\delta\to1$.

**4. Quali sono i modelli non cooperativi di bargaining visti nel corso?**
Nash demand game (richieste simultanee); bargaining sequenziale a due giocatori: ultimatum (offerta take-it-or-leave-it), two stage (un round di offerta a testa), infinite horizon (offerte alternate fino all'accordo, Rubinstein); e il modello legislativo di Baron–Ferejohn ($n$ giocatori, proponente estratto a sorte, maggioranza qualificata).

**5. Definisci il Nash demand game (strategie e pay-off).**
Dato $(U,u^*)$: $S_i=[u^*_i, m_i]$ con $m_i=\max\{x_i:(x_i,x_{-i})\in U\}$, cioè $S=[u^*,m]$ con $m$ il punto utopia. Pay-off: $u_i(x)=x_i$ se $(x_i,x_{-i})\in U$, altrimenti $u^*_i$. Ognuno dichiara simultaneamente ciò che pretende; se le richieste non sono congiuntamente fattibili, tutti prendono il disaccordo.
*Collegamento*: il punto utopia $m(U)$ è lo stesso oggetto della soluzione di Kalai–Smorodinsky.

**6. Quali sono gli equilibri di Nash del demand game? Perché è un problema?**
Ogni $x\in U$ Pareto ottimale con $x\ge u^*$ è un NE (chiedere di più rende infeasible → $u^*_i$; chiedere di meno dà meno), e anche il profilo delle richieste massime incompatibili lo è. C'è quindi un **continuo** di equilibri: tutta la frontiera di Pareto. Il gioco da solo non seleziona nulla.
*Esempio*: divide the euro, ogni $(t,1-t)$ con $t\in[0,1]$ è NE.

**7. Definisci l'ultimatum game: strategie e pay-off.**
Divide the euro in un'unica fase: I propone $x\in[0,1]$ (la sua frazione), II accetta o rifiuta; se rifiuta entrambi prendono 0. $S_1=[0,1]$, $S_2=\{\sigma:[0,1]\to\{\text{yes,no}\}\}$; $u_1=x$ e $u_2=1-x$ se $\sigma(x)=$ yes, altrimenti $(0,0)$. Con yes$\mapsto1$, no$\mapsto0$: $u_1=x\sigma(x)$, $u_2=(1-x)\sigma(x)$.
*Nota*: $S_2$ è l'insieme di **tutte** le regole di accettazione, scelte prima di vedere l'offerta (forma strategica di un gioco estensivo).

**8. Equilibri di Nash vs SPE nell'ultimatum game.**
Per ogni $t\in[0,1]$ la coppia ($x=t$, $\sigma_t(x)=$yes iff $x\le t$) è NE con pay-off $(t,1-t)$: continuo di equilibri sostenuti da minacce **non sequenzialmente razionali**. Nell'unico esito SPE II accetta ogni offerta che gli lasci $\ge0$ e I si tiene tutto → pay-off $(1,0)$.
*Collegamento*: stesso meccanismo "molti NE → un solo SPE" dei giochi di Stackelberg.

**9. Sketch dell'induzione a ritroso nell'ultimatum game.**
Nel sottogioco che segue l'offerta $x$, II confronta $1-x$ con $0$: la razionalità sequenziale impone $\sigma^*(x)=$ yes per ogni $x$ con $1-x\ge0$. Anticipando $\sigma^*$, il giocatore I risolve $\max_{x\in[0,1]} x$ e propone $x=1$.
*Collegamento*: è il blocco base dell'induzione a ritroso nei giochi a più stadi (L16).

**10. Perché il Nash demand game "da solo" non basta e serve la teoria sequenziale?**
Perché ha un continuo di equilibri e non c'è struttura temporale che discrimini fra loro. Introducendo tempo, sconto e razionalità sequenziale (SPE) l'esito diventa unico: è la strada dei modelli ultimatum → two stage → Rubinstein.

---

## L16 — Bargaining sequenziale: two stage, Rubinstein, Baron–Ferejohn

**1. Descrivi il gioco a due stadi (regole, strategie, sconti).**
I propone $x\in[0,1]$; II accetta oppure rifiuta e fa una **controproposta finale**; I accetta o rifiuta (in tal caso $(0,0)$). Sconti $\delta_i\in\,]0,1[$: un pay-off $z$ al secondo stadio vale $\delta_i z$. Strategie: $S_1=[0,1]\times\{\sigma_1:[0,1]\to\{\text{yes,no}\}\}$, $S_2=\{\sigma_2:[0,1]\to\{\text{yes}\}\cup[0,1]\}$.

**2. Calcola l'SPE del gioco a due stadi.**
Induzione a ritroso. Ultimo stadio: I accetta qualsiasi controproposta, quindi II si prende tutto e ottiene $\delta_2$. Primo stadio: il valore di continuazione di II è $\delta_2$, quindi accetta sse $1-x\ge\delta_2$, cioè $x\le 1-\delta_2$. I offre $x^*=1-\delta_2$: pay-off $(1-\delta_2,\ \delta_2)$.
*Collegamento*: per $\delta_2\to0$ si ritrova l'esito dell'ultimatum, $(1,0)$; $\delta_1$ non compare perché l'ultimo a proporre è II.

**3. Quali sono le assunzioni preliminari del gioco a orizzonte infinito?**
Il tempo è discreto, con passi temporali unitari $t\in\mathbb{N}$; i fattori di sconto non cambiano nel tempo; se il gioco prosegue all'infinito entrambi i giocatori ottengono 0. Le utilità sono $u_i(x,t)=\delta_i^t x$.
*Contesto*: è la situazione più complessa, in cui entrambi possono sempre fare una controproposta finché non si raggiunge un accordo.

**4. Quali proprietà devono valere per le utilità $u_i(x,t)=\delta_i^t x$?**
(a) $u_i(x,t)>u_i(z,t)\iff x>z$; (b) $u_i(x,t)>u_i(x,s)\iff t<s$; (c) $u_i(x,t)>u_i(z,t+1)\iff u_i(x,0)>u_i(z,1)$.
*Nelle slide*: "pie is desirable", "time matters", "stationarity over time", più la "increasing loss to delay".

**5. Perché si considerano solo strategie stazionarie e perché non si può fare induzione a ritroso?**
Data la complessità del gioco si considerano solo strategie stazionarie: entrambi i giocatori giocano continuamente la stessa strategia nel tempo. L'induzione a ritroso esplicita non è applicabile perché l'albero del gioco ha **altezza infinita**.
*Collegamento*: al suo posto si usa la condizione di indifferenza del rispondente.

**6. Qual è la condizione che caratterizza l'SPE a orizzonte infinito?**
Il proponente corrente deve rendere il rispondente **indifferente** fra accettare e rifiutare: il pay-off ottenuto accettando l'offerta corrente deve eguagliare il pay-off atteso che il rispondente otterrebbe rifiutando e formulando una controproposta.

**7. Scrivi e risolvi le due equazioni di indifferenza.**
Per il giocatore 2: $\delta_2^t(1-x)=\delta_2^{t+1}y \iff 1-x=\delta_2 y$. Per il giocatore 1: $\delta_1^t(1-y)=\delta_1^{t+1}x \iff 1-y=\delta_1 x$. Risolvendo il sistema: $x^*=\dfrac{1-\delta_2}{1-\delta_1\delta_2}$ e $y^*=\dfrac{1-\delta_1}{1-\delta_1\delta_2}$.

**8. Scrivi le funzioni di accettazione e l'SPE (teorema di Rubinstein).**
$\sigma_1^*(y)=$ yes se $y\le 1-y^*$, altrimenti $x^*$; $\sigma_2^*(x)=$ yes se $x\le 1-x^*$, altrimenti $y^*$ (cioè: si accetta se l'offerta è accettabile, altrimenti si rilancia con la propria offerta stazionaria). L'unico SPE è il profilo $((x^*,\sigma_1^*),(y^*,\sigma_2^*))$.

**9. Quali sono i pay-off di equilibrio?**
Se entrambi agiscono razionalmente il gioco finisce dopo la prima offerta, con pay-off $\dfrac{1-\delta_2}{1-\delta_1\delta_2}$ e $1-\dfrac{1-\delta_2}{1-\delta_1\delta_2}=\dfrac{\delta_2(1-\delta_1)}{1-\delta_1\delta_2}$. Se l'offerta viene accettata al tempo $t$, i pay-off sono $((x^*)^t,\ 1-(x^*)^t)$.

**10. Qual è il collegamento con il Nash program (limite dei pay-off)?**
Al tendere di $t\to0$ i pay-off convergono a $\left(\dfrac{\rho_1}{\rho_1+\rho_2},\dfrac{\rho_2}{\rho_1+\rho_2}\right)$, che corrisponde alla **generalized Nash bargaining solution** con bargaining powers $\rho_i=\log\frac{1}{\delta_i}$, detti *instantaneous rates of interest*.
*Collegamento*: chiude il Nash program aperto in L15 — una procedura non cooperativa (SPE) restituisce la soluzione assiomatica generalizzata.

**11. Descrivi il modello di Baron–Ferejohn.**
Differisce dai precedenti perché coinvolge $n$ giocatori. A ogni round un proponente è scelto casualmente e deve ottenere l'approvazione di una maggioranza fissata di $k$ giocatori con offerte opportune. Tutti condividono lo stesso $\delta$; se un'offerta è rifiutata si estrae un nuovo proponente e il tempo avanza. Si analizza con **strategie stazionarie**.

**12. Scrivi e spiega la condizione di indifferenza di Baron–Ferejohn.**
Il proponente offre una quota $s\le1$ a ciascuno dei $k$ rispondenti, rendendoli indifferenti fra accettare e rifiutare:
$$ s=\delta\left[\frac{1}{n}(1-ks)+\frac{k}{n}s\right]=\frac{\delta}{n}. $$
Nel round successivo il giocatore è proponente con probabilità $1/n$ (e prende $1-ks$) oppure uno dei $k$ rispondenti con probabilità $k/n$ (e prende $s$); la media pesata è il valore di continuazione atteso, moltiplicato per $\delta$ per il tempo trascorso.

**13. Che cos'è la reservation share?**
È il valore $s^*=\dfrac{\delta}{n}$ che risolve la condizione di indifferenza (nell'espressione fra parentesi i termini in $ks$ si cancellano e resta $1/n$). È la quota minima che un rispondente accetta; il proponente si tiene $1-ks^*$.

**14. Riassumi la catena logica ultimatum → two stage → orizzonte infinito.**
Ultimatum: un solo stadio, esito SPE $(1,0)$. Two stage: il proponente deve compensare il valore di continuazione dell'avversario, esito $(1-\delta_2,\delta_2)$. Orizzonte infinito: strategie stazionarie e condizione di indifferenza rendono il valore di continuazione endogeno, e si ottiene $x^*=(1-\delta_2)/(1-\delta_1\delta_2)$, che al limite dà la generalized Nash bargaining solution.
*Collegamento*: è il completamento del Nash program iniziato in L15; Baron–Ferejohn estende lo schema da 2 a $n$ giocatori con maggioranza qualificata.
# Domande d'orale — L17, L18, L19 (Exchange markets, matching, giochi TU)

Corso: Algorithmic Game Theory (prof. Bigi, Unipi, LM Informatica 2025/26).
Per ogni domanda: traccia di risposta in 2–4 righe (definizione chiave · esempio · collegamento).

---

## L17 — Exchange economies, house allocation, Top Trading Cycle

**1. Che cos'è un'exchange economy e in che senso il matching ne è un caso particolare?**
Ogni agente ha una dotazione iniziale di beni, che vengono scambiati **senza pagamenti monetari**; le valutazioni sono preferenze ordinali, non utilità cardinali. Se ogni bene è unico e indivisibile e ogni dotazione è unitaria (un bene per agente), l'economia degenera in un problema di matching one-to-one.
*Collegamento*: senza denaro non si può usare il machinery dei giochi TU; il "prezzo" è la sola posizione nelle liste di preferenza.

**2. Differenza fra one-sided e two-sided matching. Che cos'è un mechanism?**
Nel one-sided solo un lato (gli agenti) ha preferenze, l'altro è fatto di oggetti passivi (case, posti, organi); nel two-sided entrambi i lati hanno preferenze (L18). Un mechanism è una procedura/algoritmo che, date le preferenze dichiarate, produce un matching.
*Collegamento*: la distinzione è decisiva per la strategy-proofness: possibile nel one-sided (TTC), impossibile nel two-sided (Roth 1982).

**3. Formalizza il problema di house allocation (Shapley–Scarf 1974).**
Dati $N$ e $H$ con $|N|=|H|=n$; ogni $i$ dichiara preferenze **strette** $\succ_i$ su $H$: complete, irriflessive, transitive (l'asimmetria segue). Un matching è una funzione iniettiva $f:N\to H$, cioè $P=\{(i,f(i)):i\in N\}$. Nell'economia di scambio si aggiunge il matching iniziale $f_0$ = dotazioni.
*Collegamento*: la strettezza delle preferenze garantisce che $h_S(i)$ sia ben definita; con indifferenze serve un tie-breaking.

**4. Definisci $h_S(i)$ e il digrafo $A_f(S)$. Perché esiste sempre un ciclo?**
$h_S(i)\in S$ è l'agente che, in $f|_S$, detiene l'oggetto preferito da $i$: $j=h_S(i)\iff f(j)\succ_i f(k)\ \forall k\in S,k\ne j$ (può essere $h_S(i)=i$). $A_f(S)=\{(i,h_S(i)):i\in S\}$. Ogni nodo ha out-degree esattamente 1 (preferenze strette) e il grafo è finito: seguendo gli archi si ritorna necessariamente su un nodo già visitato, quindi esiste un ciclo orientato.
*Collegamento*: ciclo orientato ≡ permutazione mutuamente vantaggiosa; cappio ≡ l'agente ha già il meglio disponibile.

**5. Scrivi l'algoritmo TTC e discutine terminazione e complessità.**
$S_0=N$, $k=0$; se $S_k=\emptyset$ stop; costruisci $G_k=(S_k,A_{f_0}(S_k))$; trova un ciclo $C_k$; poni $f(i)=f_0(h_{S_k}(i))$ per $i\in C_k$; $S_{k+1}=S_k\setminus C_k$. Termina in al più $n$ iterazioni (ogni iterazione elimina almeno un agente). I cicli di un digrafo con out-degree 1 sono disgiunti, quindi si possono estrarre **tutti** in un colpo solo.
*Collegamento*: la ricerca dei cicli è l'unico lavoro computazionale richiesto, ed è ciò che rende TTC un vero *mechanism* eseguibile.

**6. Esegui TTC su un'istanza (esempio a 4 agenti).**
$f_0(i)=i$; preferenze $1:3\,4\,1\,2$; $2:1\,3\,4\,2$; $3:1\,2\,4\,3$; $4:2\,1\,3\,4$. Iter. 0: $1\to3,\,2\to1,\,3\to1,\,4\to2$; unico ciclo $\{1,3\}$ ⇒ $f(1)=3$, $f(3)=1$. Iter. 1 su $\{2,4\}$: $2\to4$, $4\to2$, ciclo ⇒ $f(2)=4$, $f(4)=2$. Tutti stanno debolmente meglio che in $f_0$.
*Collegamento*: mostra concretamente la individual rationality e la dipendenza da $f_0$.

**7. Enuncia il teorema di Roth–Postlewaite (1977).**
Il matching di TTC è **individually rational** ($f(i)\succ_i f_0(i)$ o $f(i)=f_0(i)$) e **stabile**: non esistono $S\subseteq N$ e permutazione $\pi:S\to S$ con $\pi(i)\ne i$ e $f(\pi(i))\succ_i f(i)$ per ogni $i\in S$. Inoltre TTC è l'**unico** meccanismo individually rational e stabile.
*Collegamento*: sono le due proprietà che le slide indicano come caratterizzanti — nessun altro meccanismo le soddisfa entrambe.

**8. Sketch della dimostrazione di stabilità di TTC.**
Induzione sull'ordine di rimozione dei cicli: gli agenti di $C_0$ ricevono la prima scelta **assoluta**, quindi non possono migliorare e non possono stare in una coalizione bloccante (che deve migliorare *tutti* i membri). Rimossi loro e i loro oggetti, gli agenti di $C_1$ ricevono la prima scelta fra i rimanenti, ecc. Quindi la coalizione bloccante è vuota.
*Collegamento*: la individual rationality si prova osservando che la propria dotazione è sempre fra i candidati, perché l'agente appartiene ancora a $S_k$.

**9. Che cosa significa esattamente che un gruppo di agenti "blocca" un matching?**
Serve un $S\subseteq N$ e una permutazione $\pi:S\to S$ con $\pi(i)\ne i$ e $f(\pi(i))\succ_i f(i)$ per **ogni** $i\in S$: la coalizione si riorganizza usando **solo** gli oggetti già assegnati ai suoi membri e migliora tutti. La stabilità è l'assenza di un tale $S$.
*Collegamento*: è la stessa logica di blocco coalizionale con cui in L19 una coalizione valuta se staccarsi dalla grande coalizione.

**10. Enuncia la strategy-proofness di TTC (Roth 1982).**
Per ogni $i$, se $f$ è il TTC sotto $(\succ_i,\succ_{-i})$ e $f'$ sotto $(\succ_i',\succ_{-i})$, allora $f'(i)\ne h$ per ogni $h\succ_i f(i)$: nessun agente può ottenere un'allocazione migliore falsificando le proprie preferenze. (Le slide danno il solo enunciato.)
*Collegamento*: risultato positivo raro — contrasta con l'impossibilità di Roth 1982 sul two-sided e con Gibbard–Satterthwaite.

**11. Perché l'esito di TTC dipende da $f_0$? Cosa si fa se $f_0$ non c'è?**
Perché i cicli sono costruiti sui **proprietari**: cambiando le dotazioni cambiano gli archi e quindi i cicli. Se non c'è dotazione iniziale, si genera $f_0$ a caso (random endowment) oppure si usa la **serial dictatorship** quando gli agenti hanno priorità (il primo prende il preferito, il secondo il preferito fra i rimanenti, ...).
*Collegamento*: la serial dictatorship è anch'essa strategy-proof, ma non usa alcuna nozione di proprietà.

**12. Quali estensioni del modello sono state citate?**
Dotazione iniziale solo per alcuni agenti (varianti di TTC); preferenze non strette (tie-breaking o gestione interna); preferenze mancanti/alternative inaccettabili; $|N|\ne|H|$ (gestire l'assenza di match); many-to-one e many-to-many.
*Collegamento*: le stesse estensioni ricompaiono nel two-sided (college admission, stable roommates).

---

## L18 — Two-sided matching, Gale–Shapley, social choice

**1. Formalizza il marriage problem.**
$M,W$ con $|M|=|W|=n$; preferenze strette $\succ_m$ su $W$ per ogni uomo e $\succ_w$ su $M$ per ogni donna. Un matching è una funzione iniettiva $f:W\to M$, con inversa $f^{-1}:M\to W$; $P=\{(w,f(w))\}=\{(f^{-1}(m),m)\}$.
*Collegamento*: rispetto a L17 entrambi i lati hanno preferenze, quindi il criterio non è più la sola convenienza degli agenti ma la stabilità della coppia.

**2. Definisci obiezione e matching stabile; dai le formulazioni equivalenti.**
$(w,m)$ obietta a $f$ se $m\succ_w f(w)$ e $w\succ_m f^{-1}(m)$ (si preferiscono reciprocamente ai partner assegnati). $f$ è stabile se nessuna coppia obietta; equivalentemente $m\succ_w f(w)\Rightarrow f^{-1}(m)\succ_m w$, o $w\succ_m f^{-1}(m)\Rightarrow f(w)\succ_w m$.
*Collegamento*: è la condizione di non-bloccaggio limitata alle coppie donna-uomo.

**3. Definisci la dominanza fra matching e il legame con la stabilità.**
$f$ è dominato da $\hat f$ se esiste $S\subseteq M\cup W$, $S\ne\emptyset$, con (i) $\hat f(S\cap W)=S\cap M=f(S\cap W)$ (ridistribuzione **interna** a $S$), (ii) $\hat f(w)\succ_w f(w)$ per $w\in S\cap W$, (iii) $\hat f^{-1}(m)\succ_m f^{-1}(m)$ per $m\in S\cap M$. Allora: $f$ stabile $\iff$ $f$ non dominato.
*Collegamento*: le blocking pair sono il caso $|S|=2$; la stabilità è quindi non-dominanza (definizione degli appunti a mano).

**4. Enuncia il teorema di esistenza (Gale–Shapley 1962) e di' come si dimostra.**
Esiste sempre almeno un matching stabile per il marriage problem. La prova è **costruttiva**: il deferred acceptance (men's o women's courtship) termina e restituisce un matching stabile.
*Collegamento*: contrasto con lo **stable roommates** (pool unico), dove i matching stabili possono non esistere.

**5. Descrivi il men's courtship algorithm.**
Ogni uomo propone alla sua top-available (la più preferita che non lo ha ancora rifiutato); ogni donna trattiene il migliore fra i proponenti (incluso l'eventuale match corrente) e rifiuta gli altri; i rifiutati scendono di una posizione. Formalmente: $r_m=1$; $L_k(w)=\{m:p_m(r_m)=w\}$; stop se $|L_k(w)|=1$ per ogni $w$; altrimenti $\bar m=\max_w L_k(w)$, $f(w)=\bar m$, $r_m{+}{+}$ per i rifiutati.
*Collegamento*: "deferred" perché nessuna accettazione è definitiva fino allo stop.

**6. Perché l'algoritmo termina, e in quante iterazioni?**
Al più $n(n-1)+1$ iterazioni: ogni iterazione non terminale produce almeno un rifiuto e ogni uomo può essere rifiutato al più $n-1$ volte. Gli uomini **scendono** lungo le liste, le donne **salgono** (il match provvisorio migliora monotonamente).
*Collegamento*: questa monotonia opposta è la radice della men-optimality/women-disappointment.

**7. Esegui Gale–Shapley su un'istanza $3\times3$ (uomini e poi donne proponenti).**
$m_1:w_1w_2w_3$, $m_2:w_1w_3w_2$, $m_3:w_2w_1w_3$; $w_1:m_3m_1m_2$, $w_2:m_1m_3m_2$, $w_3:m_2m_1m_3$. Men's: $k=1$: $m_1,m_2\to w_1$ (tiene $m_1$, rifiuta $m_2$), $m_3\to w_2$; $k=2$: $m_2\to w_3$; stop: $f_M=\{(w_1,m_1),(w_2,m_3),(w_3,m_2)\}$. Women's: tutte propongono al top e i tre uomini sono distinti ⇒ $f_W=\{(w_1,m_3),(w_2,m_1),(w_3,m_2)\}$.
*Collegamento*: due matching stabili distinti ⇒ istanza adatta a illustrare Knuth e Gale–Sotomayor.

**8. Enuncia la proponent optimality e dai lo sketch.**
Il men's courtship è **men-optimal** ($\hat f^{-1}(m)\preceq_m f^{-1}(m)$ per ogni altro stabile $\hat f$) e **women-disappointing** ($\hat f(w)\not\prec_w f(w)$); quindi è weak Pareto optimal per gli uomini. Sketch (le slide danno il solo enunciato): poiché gli uomini scendono e le donne salgono lungo le liste, nessun uomo viene mai rifiutato da una donna con cui potrebbe essere accoppiato in un matching stabile, altrimenti quel matching avrebbe una coppia con obiezione.
*Collegamento*: discende dal fatto che gli uomini scendono e le donne salgono lungo le liste durante l'esecuzione.

**9. Enuncia il teorema di Knuth (1976) e interpretalo.**
Se $f,\hat f$ sono stabili, allora $\hat f^{-1}(m)\preceq_m f^{-1}(m)$ per ogni $m$ **se e solo se** $\hat f(w)\not\prec_w f(w)$ per ogni $w$: gli interessi dei due lati sono esattamente opposti sull'insieme dei matching stabili. Sketch: se una donna peggiorasse mentre tutti gli uomini peggiorano, la coppia $(w,f(w))$ obietterebbe a $\hat f$.
*Collegamento*: il matching del men's courtship è quindi il migliore per gli uomini e il peggiore per le donne fra tutti gli stabili.

**10. Che cosa dice l'impossibilità di Roth (1982) e come si concilia con Dubins–Freedman?**
Nessun meccanismo che produca sempre matching stabili è strategy-proof (per **tutti** i giocatori). Però (Dubins–Freedman 1981) il men's courtship è **coalitionally strategy-proof per gli uomini**: nessun $S\subseteq M$ può ottenere $(f')^{-1}(m)\succ_m f^{-1}(m)$ per tutti i suoi membri.
*Collegamento*: la manipolabilità si scarica interamente sul lato non proponente.

**11. Enuncia Gale–Sotomayor (1985) e mostra una manipolazione.**
Se esistono almeno due matching stabili, può esistere una donna che, dichiarando $\succ_w'$ falsa, ottiene $f'(w)\succ_w f(w)$. Nell'istanza sopra, $w_1$ ottiene $m_1$ ma preferisce $m_3$: dichiarando $m_3\succ' m_2\succ' m_1$ rifiuta $m_1$ al primo round; $m_1$ scalza $m_3$ da $w_2$, $m_3$ propone a $w_1$ che lo trattiene ⇒ esce $f_W$ e $w_1$ ottiene $m_3$.
*Collegamento*: la manipolazione porta all'esito del women's courtship, cioè quello favorevole al lato non proponente.

**12. Quanti matching stabili ci possono essere? Altri contesti citati.**
Irving–Leather (1986): per ogni $\ell$ esiste un'istanza con $n=2^\ell$ e almeno $2^{n-1}$ matching stabili. Contesti: indifferenze, numero diverso di uomini e donne, alternative inaccettabili (si resta single), many-to-one/many-to-many (college admission), stable roommates (esistenza non garantita), fairness nella scelta fra i matching stabili.
*Collegamento*: l'esplosione esponenziale motiva la ricerca di criteri di selezione (equità) oltre a men/women-optimal.

**13. Che cos'è una social choice function? Quando è dittatoriale?**
$G:P^N\to H$ aggrega un profilo di preferenze strette in un'unica commodity ($|P|=|H|!$): maggioranza relativa, metodi di Borda/Condorcet, sempre con tie-breaking. È dittatoriale se esiste $i$ con $G(p_1,\dots,p_n)=\max_{p_i}H$ per ogni profilo.
*Collegamento*: è il caso limite del matching in cui c'è un solo "posto" da assegnare a tutti.

**14. Definisci unanimità e monotonicità; enuncia i due teoremi di impossibilità.**
Unanimità: se $h$ è il top di tutti allora $G=h$. Monotonicità: se $\bar h\succ_{p_i}h'\Rightarrow\bar h\succ_{q_i}h'$ per ogni $i,h'$, allora $G(p)=\bar h\Rightarrow G(q)=\bar h$. (a) Se $|H|\ge3$, unanimità + monotonicità ⇒ dittatoriale. (b) Gibbard–Satterthwaite: non manipolabilità + unanimità ⇒ dittatoriale ($|H|\ge3$), poiché non manipolabilità + unanimità ⇒ monotonicità.
*Collegamento*: con $|H|=2$ la maggioranza semplice è unanime, monotona e non dittatoriale; anche randomizzando (Gibbard 1977) la manipolabilità resta.

---

## L19 — Cooperative maximum flow e giochi coalizionali TU

**1. Descrivi il gioco del massimo flusso cooperativo.**
Carrier con rotte $s$–$t$ esclusive su un grafo capacitato; il worth di una coalizione $S$ è il **massimo flusso $s$–$t$ sul sottografo indotto dagli archi posseduti da $S$**. Esempio delle slide: $v(1)=1,v(2)=2,v(3)=3$, $v(12)=8$, $v(13)=9$, $v(23)=22$, $v(N)=29$.
*Collegamento*: enorme sinergia (unendo gli archi si formano cammini $s$–$t$ nuovi) ed è superadditivo; è l'esempio-guida con cui le slide introducono i giochi TU.

**2. Definisci un gioco coalizionale TU e le ipotesi implicite del modello.**
$(N,v)$ con $v:\mathcal{P}(N)\to\mathbb{R}$, $v(\emptyset)=0$; $v(S)$ è il worth di $S$. Ipotesi: ogni giocatore aderisce a **una sola** coalizione; il worth di una coalizione non dipende dalle altre; l'utilità è **arbitrariamente divisibile** fra i membri (trasferibile).
*Collegamento*: le due domande poste dalle slide sono "quali coalizioni si formeranno?" e "come dividere il worth fra i membri?".

**3. Che cos'è un gioco semplice? Fai i due esempi visti.**
$(N,v)$ è semplice se $v(S)\in\{0,1\}$; $S$ è vincente se $v(S)=1$. (a) Maggioranza pesata: $v_{q,w}(S)=1$ se $\sum_{i\in S}w_i\ge q$; procedura bicamerale $v=\min\{v_{q,w},v_{q',w'}\}$. (b) Consiglio di sicurezza ONU: $n=15$, $P$ permanenti con $|P|=5$, $v(S)=1$ sse $P\subseteq S$ e $|S|\ge9$.
*Collegamento*: i membri permanenti sono giocatori con **veto**: nessuna coalizione che ne escluda uno è vincente.

**4. Che cos'è un cost game? Come si tratta rispetto a un gioco di valori?**
Esempio MST: città da collegare a una centrale $r$, costo di $S$ = minimum spanning tree sul sottografo indotto da $S\cup\{r\}$ ($v(1)=40$, $v(2)=5$, $v(12)=25$, ...). Trattandosi di costi si **cambiano i segni** nell'analisi teorica (le disuguaglianze si invertono, superadditività ↔ subadditività).
*Collegamento*: dal cost game si passa al **savings game** (fondi meno costo del MST), che è a valori e superadditivo.

**5. Descrivi il savings game dei fondi statali.**
Ogni città riceve 40 M€ e vuole risparmiare: $v(S)$ = fondi complessivi di $S$ meno il costo del MST su $S\cup\{r\}$. Tabella: $v(1)=0,v(2)=35,v(3)=35,v(4)=30$; $v(12)=55,v(13)=45,v(14)=30,v(23)=70,v(24)=65,v(34)=65$; $v(123)=90,v(124)=85,v(134)=75,v(234)=100$; $v(N)=120$.
*Collegamento*: superadditivo (es. $v(12)+v(34)=120=v(N)$); le domande delle slide sono quali città cooperano e come riallocare i fondi risparmiati.

**6. Definisci i market games e dai la struttura generale (Shapley–Shubik 1969).**
$N=W\cup B$ (vino/bottiglie): $v(S)=\min\{\sum_{i\in S\cap W}\ell_i,\ \sum_{i\in S\cap B}b_i\}$; con $\ell=(6,5,4)$ e $b=(5,7)$: $v(14)=5$, $v(125)=7$, $v(12345)=\min\{15,12\}=12$, e $v(S)=0$ se $S$ sta tutta da un lato. In generale: $n$ trader con panieri di beni, ciascun paniere dà utilità, lo scambio è ammesso dentro la coalizione, e $v(S)$ = massimo valore della somma delle utilità riallocando i beni.
*Collegamento*: è l'analogo **cardinale e trasferibile** dell'economia di scambio di L17 (là solo preferenze ordinali, qui utilità ripartibile).

**7. Come si ricava un gioco TU da un gioco non cooperativo?**
Dato $(N,(\Delta_i),(u_i))$, si pone $\Delta_S=\prod_{i\in S}\Delta_i$ e si assegna a $S$ il suo **valore di sicurezza**: $v(S)=\max_{x_S\in\Delta_S}\min_{x_{S^c}\in\Delta_{S^c}}\sum_{i\in S}u_i(x_S,x_{S^c})$, con $S^c=N\setminus S$.
*Collegamento*: è la lettura maximin (à la von Neumann) della cooperazione; il gioco così ottenuto è sempre superadditivo.

**8. Perché il valore di sicurezza è superadditivo?**
Se $S\cap T=\emptyset$ e $x_S,x_T$ sono strategie di sicurezza, la coalizione $S\cup T$ può giocare $(x_S,x_T)$ e garantirsi almeno $v(S)+v(T)$: gli avversari residui $(S\cup T)^c$ hanno **meno** possibilità di quante ne avessero $S^c$ e $T^c$ separatamente (i membri di $T$ non giocano più contro $S$ e viceversa).
*Collegamento*: giustifica formalmente la formazione della grande coalizione.

**9. Definisci superadditività e monotonia; che relazione c'è?**
Superadditivo: $S\cap T=\emptyset\Rightarrow v(S)+v(T)\le v(S\cup T)$. Monotono: $S\subseteq T\Rightarrow v(S)\le v(T)$. Se $v\ge0$, superadditività ⇒ monotonia: $v(T)\ge v(S)+v(T\setminus S)\ge v(S)$.
*Collegamento*: la superadditività **impedisce le coalizioni "segrete"** e giustifica lo studio della sola ripartizione di $v(N)$.

**10. Enuncia e dimostra la proposizione sulle famiglie disgiunte.**
Se $(N,v)$ è superadditivo e $\{S_i\}_{i\in I}$ sono a due a due disgiunte, allora $\sum_i v(S_i)\le v(\bigcup_i S_i)$. Prova per induzione su $|I|$: base = definizione; passo: $\sum_{i\le k+1}v(S_i)\le v(U)+v(S_{k+1})\le v(U\cup S_{k+1})$ con $U=\bigcup_{i\le k}S_i$. In particolare $\sum_{i\in S}v(i)\le v(S)$ e $v(1)+\dots+v(n)\le v(N)$.
*Collegamento*: la disuguaglianza $\sum_i v(i)\le v(N)$ è anche il criterio che, nel teorema di classificazione, distingue le tre normalizzazioni.

**11. Definisci la superadditive cover e le sue tre proprietà.**
$v^*(S)=\max_{\mathcal{P}\in\mathbb{P}(S)}\sum_{T\in\mathcal{P}}v(T)$ sull'insieme $\mathbb{P}(S)$ delle partizioni di $S$. Allora (i) $v^*\ge v$ (partizione banale); (ii) $(N,v^*)$ è superadditivo (unione di partizioni ottime di insiemi disgiunti); (iii) se $w$ è superadditivo e $w\ge v$ allora $w\ge v^*$ — cioè $v^*$ è il **minimo** gioco superadditivo che domina $v$.
*Collegamento*: serve quando la superadditività fallisce, tipicamente per costi di coordinamento.

**12. Esempio di gioco non superadditivo e calcolo di $v^*$.**
Market game con costo d'accordo: $v(S)=\min\{\sum\ell_i,\sum b_i\}-c\,|S\cap W|\,|S\cap B|$. Con $c=1$: $v(14)=4$, $v(25)=4$ ma $v(1245)=7<8$ (si pagano 4 accordi invece di 2), quindi non superadditivo. La copertura dà $v^*(1245)=v(15)+v(24)=5+4=9$ e $v^*(12345)=9$.
*Collegamento*: mostra che con costi di coordinamento conviene spezzarsi in sottocoalizioni, ed è proprio ciò che $v^*$ misura.

**13. Definisci l'equivalenza strategica e di' che cosa preserva.**
$(N,w)$ è strategicamente equivalente a $(N,v)$ se esistono $a>0$ e $b\in\mathbb{R}^n$ con $w(S)=a\,v(S)+b(S)$, $b(S)=\sum_{i\in S}b_i$ (cambio di unità + valore costante per giocatore). È una relazione di equivalenza; preserva la **superadditività** (perché $b$ è additivo), non la monotonia: $v(S)=|S|$ è monotono, ma con $b_i=-2$ si ha $w(S)=-|S|$.
*Collegamento*: è la relazione che permette di ricondurre ogni gioco a una delle tre forme normalizzate del teorema seguente.

**14. Enuncia e dimostra il teorema di classificazione (normalizzazioni 0-1, 0-0, 0-(-1)).**
$(N,v)$ è equivalente a un gioco 0-1 (risp. 0-0, 0-(-1)) normalizzato sse $\sum_i v(i)<v(N)$ (risp. $=$, $>$). Prova: si pone $b_i=-a\,v(i)$ così $w(i)=0$ e $w(N)=a(v(N)-\sum_i v(i))$; si sceglie $a=|v(N)-\sum_i v(i)|^{-1}$ nei casi stretti, un $a>0$ qualsiasi nel caso di uguaglianza. Il segno di $v(N)-\sum_i v(i)$ è invariante, quindi le classi sono esclusive ed esaustive.
*Collegamento*: il caso $\sum_i v(i)<v(N)$ è quello in cui la cooperazione crea valore, e la forma 0-1 ne è il rappresentante canonico.
# Domande d'orale — AGT L20–L24 (giochi coalizionali TU)

Prof. Bigi — Unipi, LM Informatica 2025/26.
Per ogni domanda: traccia di risposta in 2–4 righe. All'orale il prof chiede
tipicamente enunciato preciso + sketch di dimostrazione + esempio.

---

## L20 — Giochi coalizionali TU: imputazioni, stable sets, core

**1. Che cos'è un gioco coalizionale con utilità trasferibile?**
Una coppia $(N,v)$ con $N=\{1,\dots,n\}$ e $v:\mathcal{P}(N)\to\mathbb{R}$, $v(\emptyset)=0$; $v(S)$ è il worth che la coalizione $S$ si garantisce da sola. "Utilità trasferibile" significa che $v(S)$ è liberamente divisibile fra i membri (denaro), quindi non servono le preferenze individuali. La domanda centrale è come dividere $v(N)$ fra i giocatori.

**2. Perché si parla di accordi vincolanti e cosa cambia rispetto ai giochi non cooperativi?**
Nei giochi non cooperativi ogni giocatore sceglie una strategia e il coordinamento è solo autoimposto (NE). Qui i giocatori possono firmare accordi che vengono fatti rispettare: l'oggetto di studio non è più il profilo di strategie ma la ripartizione del valore. Le "deviazioni" diventano deviazioni di gruppo (coalizioni), non individuali.

**3. Faccia un esempio di gioco coalizionale nato da un problema di ottimizzazione.**
Cooperative maximum flow: ogni vettore possiede alcuni archi di una rete, $v(S)$ = massimo flusso $s$–$t$ nel sottografo indotto dagli archi di $S$ (es. $v(1)=1,v(2)=2,v(3)=3$, $v(12)=8$, $v(23)=22$, $v(N)=29$). Altro esempio: risparmi aggregati, $v(S)=40|S|$ meno il costo del MST su $S\cup\{r\}$.

**4. Che cos'è un'imputazione?**
$x\in\mathbb{R}^n$ tale che (i) $x(N)=v(N)$ (razionalità sociale / efficienza) e (ii) $x_i\ge v(i)$ per ogni $i$ (razionalità individuale). L'insieme è $X(N,v)$, che può essere vuoto (se $\sum_i v(i)>v(N)$). Rilassando (ii) si ottengono le preimputazioni $X^0(N,v)$, che sono un iperpiano e non sono mai vuote.

**5. Definisca la dominanza fra imputazioni.**
$y$ domina $x$ attraverso $S$ se $y_i>x_i$ per ogni $i\in S$ (tutti in $S$ migliorano) e $y(S)\le v(S)$ ($S$ può realizzare $y$ da sola). È l'analogo cooperativo della deviazione profittevole: una coalizione ha motivo di rompere l'accordo. $x$ è non dominata se nessuna coppia $(y,S)$ la domina.

**6. Che cos'è uno stable set di von Neumann–Morgenstern?**
$G\subseteq X(N,v)$ internamente stabile (nessun $x\in G$ dominato da un $y\in G$) ed esternamente stabile (ogni imputazione fuori da $G$ è dominata da qualche $y\in G$). Nel gloves game ce ne sono almeno tre: $G_1=\{(t,t,1-2t)\}$, $G_2=\{(t,0,1-t)\}$, $G_3=\{(0,t,1-t)\}$. Aumann: non c'è teoria generale né algoritmi, da qui il passaggio al core.

**7. Definisca il core e ne elenchi le proprietà.**
$C(N,v)=\{x: x(N)=v(N),\ x(S)\ge v(S)\ \forall S\}$ (Gillies 1959): allocazioni razionali per ogni coalizione. È un poliedro compatto e convesso sull'iperpiano $x(N)=v(N)$, è contenuto in $X(N,v)$ (prendendo $S$ singoletto) ed è fatto di imputazioni non dominate. Può essere vuoto.

**8. Perché ogni elemento del core è non dominato?**
Se $y$ dominasse $x\in C(N,v)$ attraverso $S$, avremmo $v(S)\ge y(S)>x(S)\ge v(S)$, assurdo. Quindi il core è internamente stabile; se il gioco è superadditivo vale anche il viceversa, cioè il core coincide con l'insieme delle imputazioni non dominate.

**9. Calcoli il core del gloves game.**
$v(13)=v(23)=v(N)=1$, resto $0$. Da $x_1+x_3\ge1$, $x_2+x_3\ge1$, $x(N)=1$, $x\ge0$ segue $x_1=x_2=0$: $C(N,v)=\{(0,0,1)\}$. Nessuna coalizione vincente esiste senza il giocatore 3, e la competizione fra 1 e 2 azzera il loro potere contrattuale.

**10. Discuta il gioco a 3 giocatori con $v(S)=\rho$ per $|S|=2$ e $v(N)=3$.**
Le condizioni di core sono $x_k\le 3-\rho$; sommando, $3\le 3(3-\rho)$, cioè $\rho\le2$. Quindi $C\ne\emptyset\iff\rho\le2$; $C=\{(1,1,1)\}$ per $\rho=2$; $C$ ha cardinalità del continuo per $\rho<2$. Il gioco è superadditivo per $0\le\rho\le3$: **superadditivo non implica core non vuoto**.

**11. Che ruolo ha la superadditività?**
$S\cap T=\emptyset\Rightarrow v(S)+v(T)\le v(S\cup T)$: cooperare non fa mai danno. Implica che il core coincide con le imputazioni non dominate, e che ogni partizione soddisfa la condizione necessaria $\sum_j v(S_j)\le v(N)$. Non basta però a garantire $C\ne\emptyset$ (vedi gioco $\rho$ con $2<\rho\le3$).

**12. Che cos'è l'equivalenza strategica e perché è utile?**
$w=av+b$ con $a>0$, $b\in\mathbb{R}^n$ (cioè $w(S)=av(S)+b(S)$). Allora $C(N,w)=aC(N,v)+b$, e lo stesso vale per nucleolo e valore di Shapley (covarianza). Serve a normalizzare i giochi (forma 0-1, 0-0) senza cambiare la struttura delle soluzioni: è il trucco usato per la bancarotta a 2 creditori.

---

## L21 — Bondareva–Shapley, giochi bilanciati, market games

**1. Enunci una condizione necessaria per la non vuotezza del core.**
Se $C(N,v)\ne\emptyset$, allora per ogni partizione $\{S_1,\dots,S_k\}$ di $N$ vale $\sum_j v(S_j)\le v(N)$. Dimostrazione: si sommano $x(S_j)\ge v(S_j)$ e si usa $\sum_j x(S_j)=x(N)=v(N)$. Corollario: i giochi (strategicamente equivalenti a) 0-(-1) normalizzati hanno core vuoto.

**2. Dia la caratterizzazione LP della non vuotezza del core.**
$C(N,v)\ne\emptyset \iff v_P\le v(N)$, dove $v_P$ è l'ottimo di $(P)\ \min\{x(N): x(S)\ge v(S),\ S\subsetneq N\}$. Se $v_P\le v(N)$ si prende l'ottimo e si aggiunge lo scarto a una componente (le disuguaglianze restano valide); viceversa ogni punto del core è ammissibile con $x(N)=v(N)$.

**3. Che cos'è un vettore di pesi bilancianti?**
Con $\mathcal{C}=\mathcal{P}(N)\setminus\{\emptyset,N\}$: $\lambda_S\ge0$ tali che $\sum_{S\ni i}\lambda_S=1$ per ogni giocatore $i$. Interpretazione: $\lambda_S$ è la frazione di tempo dedicata alla coalizione $S$, e ogni giocatore è occupato al 100%. Le partizioni sono il caso particolare $\lambda_S\in\{0,1\}$.

**4. Quando un gioco è bilanciato?**
Se per **ogni** vettore di pesi bilancianti vale $\sum_S \lambda_S v(S)\le v(N)$: nessuna organizzazione "a tempo parziale" batte la grande coalizione. La bilanciatezza è invariante per equivalenza strategica (usando $\sum_{S\ni i}\lambda_S=1$ il termine $b$ si semplifica).

**5. Enunci e dimostri (sketch) il teorema di Bondareva–Shapley.**
$C(N,v)\ne\emptyset\iff (N,v)$ è bilanciato. Sketch: core non vuoto $\iff v_P\le v(N)$; bilanciato $\iff v_D\le v(N)$ dove $(D)\ \max\{\sum_S\lambda_S v(S):\lambda$ pesi bilancianti$\}$; $(D)$ è il duale di $(P)$ (la colonna di $x_i$ dà il vincolo $\sum_{S\ni i}\lambda_S=1$); per dualità forte $v_P=v_D$.

**6. Che dimensione ha l'LP che decide la non vuotezza del core?**
$(P)$ ha $n$ variabili ma $2^n-2$ vincoli (uno per ogni coalizione propria non vuota): il numero di vincoli è esponenziale in $n$. Lo stesso vale per il duale $(D)$, che ha una variabile $\lambda_S$ per coalizione e $n$ vincoli.

**7. Che cos'è il balanced cover?**
$v^\star(S)=v(S)$ per $S\ne N$ e $v^\star(N)=\max\{\max_\lambda\sum_S\lambda_S v(S),\ v(N)\}$: si alza $v(N)$ del minimo necessario. Proprietà: $v^\star\ge v$; $(N,v^\star)$ è bilanciato; $v$ è bilanciato $\iff v^\star=v$; se $w\ge v$ è bilanciato allora $w\ge v^\star$ (minimalità).

**8. Definisca un market game.**
$n$ agenti, $p$ merci, dotazioni $w^i\in\mathbb{R}^p_+$, utilità **concave** $u_i$; $v(S)=\max\{\sum_{i\in S}u_i(z^i): \sum_{i\in S}z^i=\sum_{i\in S}w^i,\ z^i\ge0\}$ (Shapley–Shubik 1969). Vale $v(i)=u_i(w^i)$. Esempio: vino/bottiglie con $u_i(z)=\min\{z_1,z_2\}$ dà $v(S)=\min\{\sum_{S\cap P}\ell_i,\sum_{S\cap B}b_i\}$.

**9. Che relazione c'è fra market games e bilanciatezza?**
Teorema: ogni market game è bilanciato, quindi (per Bondareva–Shapley) ha core non vuoto. La classe è inoltre chiusa per equivalenza strategica: se $w=av+b$ con $a>0$, $(N,w)$ è il market game con utilità $au_i+b_i$.

**10. Che cos'è un sottogioco e che cos'è un gioco totalmente bilanciato?**
$(S,w)$ con $w=v|_{\mathcal{P}(S)}$ è un sottogioco. $(N,v)$ è totalmente bilanciato se tutti i suoi sottogiochi sono bilanciati. Ogni sottogioco di un market game è ancora un market game (si restringe la lista degli agenti), dunque i market games sono totalmente bilanciati.

**11. Enunci il teorema di caratterizzazione dei giochi totalmente bilanciati.**
$(N,v)$ totalmente bilanciato $\iff$ è un market game $\iff$ è un maximum flow game. Conseguenza pratica: i due esempi motivanti del corso (flusso cooperativo, vino/bottiglie) hanno sempre core non vuoto; l'aggiunta dei costi di accordo distrugge la proprietà e il core diventa vuoto.

**12. Calcoli il core del gioco dei risparmi aggregati.**
Da $x_3\ge35$ e $x_{123}\ge90$ segue $x_4\le30$, quindi $x_4=30$; da $x_{124}\ge85$ segue $x_3=35$; da $x_{12}\ge55$ e $x_{34}=65$ segue $x_1+x_2=55$; $x_{13}\ge45$ dà $x_1\ge10$ e $x_{234}\ge100$ dà $x_1\le20$. Quindi $C=\{(t,55-t,35,30):10\le t\le20\}$: un segmento.

---

## L22 — Strutture coalizionali, quasi core, least core

**1. Che cos'è il core rispetto a una struttura coalizionale?**
Data una partizione $\mathcal{P}$ di $N$: $C(N,v,\mathcal{P})=\{x: x(S)=v(S)\ \forall S\in\mathcal{P},\ x(S)\ge v(S)\ \forall S\subseteq N\}$. L'efficienza è **per blocco** (niente trasferimenti fra coalizioni diverse), ma la razionalità coalizionale vale per tutte le $S$, anche quelle che attraversano i blocchi. Per $\mathcal{P}=\{N\}$ si ritrova $C(N,v)$.

**2. Definisca il superadditive cover.**
$v^*(S)=\max_{\mathcal{T}\text{ partizione di }S}\sum_{T\in\mathcal{T}}v(T)$: il meglio che $S$ ottiene organizzandosi liberamente in sottocoalizioni. $(N,v^*)$ è superadditivo, $v^*\ge v$, e $v^*=v$ sse $v$ è superadditivo.

**3. Enunci e dimostri (sketch) il teorema $C(N,v,\mathcal{P})=C(N,v^*)\cap X(\mathcal{P},v)$.**
Il punto chiave: $x(S)\ge v(S)\ \forall S \iff x(S)\ge v^*(S)\ \forall S$; infatti $x(S)=\sum_{T\in\mathcal{T}}x(T)\ge\sum_T v(T)$ per ogni partizione $\mathcal{T}$ di $S$, e si prende il max. Il resto è riscrivere le condizioni: $x(N)=v^*(N)$ + razionalità dà $C(N,v^*)$, le uguaglianze sui blocchi danno $X(\mathcal{P},v)$.

**4. Quali strutture coalizionali "sopravvivono"?**
Solo quelle ottime. Se $v^*(N)=\sum_{T\in\mathcal{P}}v(T)$ allora $C(N,v,\mathcal{P})=C(N,v^*)$; se $v^*(N)>\sum_{T\in\mathcal{P}}v(T)$ allora $C(N,v,\mathcal{P})=\emptyset$ (perché $x(N)$ sarebbe $<v^*(N)$, mentre deve essere $\ge$). Quindi la superadditività "guida" la formazione delle coalizioni.

**5. Illustri il market game con costi di accordo.**
$v(S)=\min\{\sum_{S\cap P}\ell_i,\sum_{S\cap B}b_i\}-c|S\cap P||S\cap B|$: ogni coppia produttore/imbottigliatore costa $c$. Con $c=1$ e i dati del corso: $C(N,v)=\emptyset$, $v^*(N)=9>6=v(N)$, $C(N,v^*)=\{(t,t,0,4-t,5-t):0\le t\le1\}$; le sole partizioni ottime sono $\{135\},\{24\}$ e $\{235\},\{14\}$.

**6. Che cos'è una preimputazione e perché serve?**
$x$ con $x(N)=v(N)$ soltanto: $X^0(N,v)$ è un iperpiano, dunque **mai vuoto**, a differenza di $X(N,v)$ e di $C(N,v)$. Serve come dominio "sempre disponibile" su cui definire quasi core, least core e prenucleolo quando il core è vuoto.

**7. Definisca strong e weak $\varepsilon$-core.**
$C_\varepsilon(N,v)=\{x\in X^0: x(S)\ge v(S)-\varepsilon\ \forall S\subsetneq N\}$ (penale fissa) e $\widetilde C_\varepsilon(N,v)=\{x\in X^0: x(S)\ge v(S)-|S|\varepsilon\}$ (penale pro capite). Per $\varepsilon\ge0$: $C_\varepsilon\subseteq\widetilde C_\varepsilon\subseteq C_{n\varepsilon}$ (perché $1\le|S|\le n$), con inclusioni invertite per $\varepsilon\le0$.

**8. Proprietà del quasi core?**
$C_0=C$; monotonia in $\varepsilon$; per $\varepsilon_2<0<\varepsilon_1$ vale $C_{\varepsilon_2}\subseteq C\subseteq C_{\varepsilon_1}$; $C_\varepsilon\ne\emptyset$ per $\varepsilon$ grande (basta prendere una preimputazione e $\varepsilon\ge\max_S e(S,\bar x)$); $C_\varepsilon=\emptyset$ per $\varepsilon$ molto negativo (sommando i vincoli su una partizione).

**9. Definisca il least core.**
$I(N,v)=\{\varepsilon: C_\varepsilon\ne\emptyset\}=[\bar\varepsilon,+\infty)$ e $LC(N,v)=\bigcap_{\varepsilon\in I}C_\varepsilon=C_{\bar\varepsilon}$ (Maschler–Peleg–Shapley 1979). È sempre non vuoto; se $C\ne\emptyset$ allora $\bar\varepsilon\le0$ e $LC\subseteq C$.

**10. Caratterizzazione variazionale del least core.**
$LC(N,v)=\arg\min\{\max_{S\subsetneq N}(v(S)-x(S)) : x\in X^0(N,v)\}$: minimizza la massima insoddisfazione. Si ottiene risolvendo l'LP $\min \delta$ s.t. $x(S)+\delta\ge v(S)$, $x(N)=v(N)$: ammissibile e limitato, quindi ottimo esistente; la funzione obiettivo è convessa (max di affini).

**11. Che cos'è l'eccesso e come si reinterpretano i core?**
$e(S,x)=v(S)-x(S)$: $\le0$ coalizione soddisfatta, $>0$ misura di insoddisfazione. Allora $C_\varepsilon=\{x\in X^0: e(S,x)\le\varepsilon\ \forall S\subsetneq N\}$ e il least core dà la minima massima insoddisfazione. Il core è il caso $\varepsilon=0$.

**12. Vettore ordinato di insoddisfazione e ordine lessicografico.**
$\theta(x)=(e(S_1,x),\dots,e(S_{2^n},x))$ con eccessi in ordine non crescente. $a\ge_{lex}b$ se $a=b$ oppure esiste $k$ con $a_i=b_i$ per $i<k$ e $a_k>b_k$: è un ordine totale ma **non continuo** (es. $a^h=(1/h,-1)\to(0,-1)$ con $a^h>_{lex}(0,0)$ ma il limite no). Minimizzare $\theta$ lessicograficamente porta al nucleolo.

---

## L23 — Nucleolo e prenucleolo

**1. Definisca il nucleolo relativo a un insieme $K$.**
$\mathcal{N}(N,v,K)=\{x\in K:\theta(x)\le_{lex}\theta(y)\ \forall y\in K\}$ (Schmeidler 1969): i minimi lessicografici del vettore ordinato degli eccessi su $K$. Si abbassa prima la massima insoddisfazione, poi la seconda a parità della prima, e così via.

**2. Che differenza c'è fra nucleolo e prenucleolo?**
$\mathcal{N}(N,v)$ è il nucleolo relativo alle **imputazioni** $X(N,v)$; $\mathcal{PN}(N,v)$ è il prenucleolo, relativo alle **preimputazioni** $X^0(N,v)$. Il prenucleolo esiste sempre (l'iperpiano non è mai vuoto), il nucleolo solo se $X(N,v)\ne\emptyset$. Se il prenucleolo è individualmente razionale, coincide col nucleolo.

**3. Mostri un caso in cui prenucleolo e nucleolo differiscono.**
$n=3$, $v(\{1,2\})=1$ e tutto il resto (incluso $v(N)$) $=0$. Allora $X(N,v)=\{(0,0,0)\}=\mathcal{N}$, mentre sulle preimputazioni: $\theta_1\ge\max\{s,1-s\}\ge1/2$ con $s=x_1+x_2=1/2$, poi si minimizza $\max\{|x_1|,|x_2|\}$: $\mathcal{PN}=(1/4,1/4,-1/2)$, che non è un'imputazione.

**4. Enunci il teorema di esistenza e unicità.**
Se $X(N,v)\ne\emptyset$ allora $|\mathcal{N}(N,v)|=1$; e $|\mathcal{PN}(N,v)|=1$ sempre. Sono quindi concetti di soluzione **single-valued**: esattamente ciò che serve a un arbitro che debba scegliere una sola ripartizione.

**5. Quali proprietà generali hanno i nucleoli relativi a $K$?**
$K_2\subseteq K_1\Rightarrow \mathcal{N}(N,v,K_1)\cap K_2\subseteq\mathcal{N}(N,v,K_2)$; se inoltre $\emptyset\ne\mathcal{N}(N,v,K_1)\subseteq K_2$ i due nucleoli coincidono; covarianza $\mathcal{N}(N,av+b,aK+b)=a\mathcal{N}(N,v,K)+b$. Da queste discendono i legami fra nucleolo e prenucleolo.

**6. Che relazione c'è fra prenucleolo, least core e core?**
Sempre: $\mathcal{PN}(N,v)\in LC(N,v)$ e $LC(N,v)=C_{\bar\varepsilon}(N,v)$ con $\bar\varepsilon=\theta_1(\mathcal{PN})$. Se $C(N,v)\ne\emptyset$: $\mathcal{N}=\mathcal{PN}\in C(N,v)$, perché $LC\subseteq C\subseteq X$ e quindi il prenucleolo è individualmente razionale.

**7. Quali proprietà soddisfa il prenucleolo?**
Null player, simmetria e covarianza per equivalenza strategica ($\mathcal{N}(av+b,aK+b)=a\mathcal{N}(v,K)+b$, perché $e_w(S,ax+b)=a\,e_v(S,x)$). **Non** è additivo: $\mathcal{PN}(v+w)\ne\mathcal{PN}(v)+\mathcal{PN}(w)$ in generale — la differenza chiave rispetto al valore di Shapley.

**8. Il nucleolo è additivo?**
No: né $\mathcal{N}$ né $\mathcal{PN}$ sono additivi, cioè in generale $[\mathcal{P}]\mathcal{N}(N,v+w)\ne[\mathcal{P}]\mathcal{N}(N,v)+[\mathcal{P}]\mathcal{N}(N,w)$. È la proprietà che distingue il nucleolo dal valore di Shapley, il quale è additivo per costruzione ma può cadere fuori dal core.

**9. Descriva lo schema di Maschler.**
Successione di LP: al passo $k$, $\min\delta$ s.t. $\delta\ge e(S,x)$ per $S\in\mathcal{F}_k$, $x\in K_k$; si pone $K_{k+1}$ = insieme delle soluzioni ottime, si rimuovono da $\mathcal{F}_k$ le coalizioni il cui eccesso è ormai **fissato** a $\delta_k$, e si itera. Al primo passo $\delta_1=\bar\varepsilon$ e $K_2=LC$; termina in $\le n$ passi con il prenucleolo.

**10. Qual è il problema computazionale del calcolo del nucleolo?**
Ogni LP dello schema ha $O(2^n)$ vincoli (uno per coalizione), quindi il calcolo diretto è esponenziale nel numero di giocatori. Il numero di iterazioni è invece piccolo ($\le n$), perché la dimensione dell'insieme ammissibile cala di almeno 1 a ogni passo.

**11. Risolva il caso della bancarotta con 2 creditori.**
$v(\{i\})=\max\{p-d_{-i},0\}$, $v(N)=p$, con $d_1+d_2>p$. Traslando con $b=(v(1),v(2))$ i due creditori diventano simmetrici, quindi il prenucleolo di $w$ è $(w(N)/2,w(N)/2)$; per covarianza $\mathcal{N}(v)=\big(\frac{v(N)+v(1)-v(2)}{2},\frac{v(N)+v(2)-v(1)}{2}\big)\in C(N,v)$. In pratica: parte non contesa + metà del resto.

**12. Calcoli il nucleolo del gioco dei risparmi aggregati.**
Lungo il core $x_t=(t,55-t,35,30)$ molti eccessi sono identicamente $0$, quindi $\bar\varepsilon=0$ e $LC=C=\{x_t:10\le t\le20\}$. Al secondo LP si minimizza $\max\{-t,\ t-20,\ 10-t\}$ su $[10,20]$: minimo $-5$ in $t=15$. Quindi $\mathcal{N}=(15,40,35,30)$, il punto medio del segmento-core.

**13. E per il market game con costi di accordo?**
Primo LP: $\bar\varepsilon=1.5$, $LC=\{(t,t,0,2.5-t,3.5-t):0\le t\le1\}$. Secondo LP: fissate le coalizioni con eccesso costante $1.5$, restano $e(34)=t+0.5$, $e(125)=1.5-t$, $e(1345)=t$; si minimizza il loro max su $[0,1]$: $t=0.5$. Quindi $\mathcal{N}=\mathcal{PN}=(0.5,0.5,0,2,3)$, benché $C(N,v)=\emptyset$.

---

## L24 — Assiomatica, valore di Shapley, indici di potere

**1. Che cosa distingue un concetto di soluzione set-valued da uno single-valued?**
$\Phi:\mathcal{G}\rightrightarrows\mathbb{R}^N$ restituisce un insieme (core, least core, stable sets); $\varphi:\mathcal{G}\to\mathbb{R}^N$ restituisce un punto (prenucleolo, valore di Shapley). Il secondo serve quando è richiesta una scelta unica (arbitrato); il primo descrive l'insieme degli accordi stabili.

**2. Elenchi le proprietà desiderabili per $\varphi$.**
Efficienza $\sum_i\varphi_i(v)=v(N)$; simmetria (giocatori con gli stessi contributi ricevono lo stesso); null player ($\varphi_i=0$ se $i$ non contribuisce mai); additività $\varphi(v+w)=\varphi(v)+\varphi(w)$; covarianza $\varphi(av+b)=a\varphi(v)+b$.

**3. Perché i tentativi ingenui falliscono?**
$\varphi_i(v)=v(i)$: manca l'efficienza. $\varphi_i(v)=\max_S\{v(S\cup i)-v(S)\}$: mancano efficienza e additività (il max di una somma non è la somma dei max). $\varphi_i(v)=v(\{1..i\})-v(\{1..i-1\})$: efficiente (somma telescopica), additivo, null player, ma **non simmetrico** perché fissa un ordine arbitrario.

**4. Enunci il teorema di Shapley.**
Esiste un unico concetto single-valued che soddisfa efficienza, simmetria, null player e additività, ed è $\Sh_i(v)=\frac{1}{n!}\sum_{\pi\in\Pi_N}[v(P_i(\pi)\cup\{i\})-v(P_i(\pi))]$, con $P_i(\pi)$ = predecessori di $i$ in $\pi$. È il contributo marginale medio su tutti gli ordini d'arrivo.

**5. Dia la formulazione alternativa e la giustifichi.**
$\Sh_i(v)=\frac{1}{n!}\sum_{S\subseteq N\setminus\{i\}}|S|!(n-|S|-1)![v(S\cup i)-v(S)]$, perché $|\{\pi: P_i(\pi)=S\}|=|S|!(n-|S|-1)!$ (si ordinano liberamente i predecessori e i successori). È la formula da usare nei conti a mano.

**6. Come si interpreta la formula di Shapley?**
I giocatori entrano in una stanza in ordine casuale uniforme e ciascuno riceve il valore che aggiunge al gruppo già presente: $\Sh_i(v)$ è il contributo marginale atteso di $i$. La dimostrazione dell'unicità non è stata svolta a lezione: basta sapere che i quattro assiomi determinano $\varphi$ e che $\Sh$ li soddisfa (ed è anche covariante).

**7. Che cosa sono monotonicità e marginalità?**
Marginalità: se i contributi marginali di $i$ coincidono in $v$ e $w$, allora $\varphi_i(v)=\varphi_i(w)$ (il compenso dipende solo dai contributi marginali). Monotonicità: contributi marginali maggiori $\Rightarrow$ compenso maggiore. Monotonicità $\Rightarrow$ marginalità; il valore di Shapley soddisfa entrambe.

**8. Enunci la caratterizzazione di Young.**
Il valore di Shapley è l'unico concetto single-valued che soddisfa efficienza, simmetria e marginalità (Young 1985). Vale inoltre la proposizione: efficienza + simmetria + marginalità $\Rightarrow$ null player, quindi questa caratterizzazione sostituisce due assiomi (null player e additività) con la sola marginalità.

**9. Il valore di Shapley sta nel core?**
Non necessariamente, neppure quando il core è non vuoto. Gloves game: $\Sh=(1/6,1/6,2/3)$ mentre $C=\{(0,0,1)\}$. Risparmi aggregati: $\Sh=(11.\overline6,41.\overline6,36.\overline6,30)\notin C$ (il core impone $x_3=35$). Shapley misura il contributo, il core la stabilità.

**10. Quando conviene il core, quando il nucleolo, quando Shapley?**
Core: "quali accordi sono stabili?" — insieme, spesso vuoto o troppo grande. Least core/nucleolo: "come arbitrare minimizzando l'insoddisfazione?" — sempre definiti, unici, e nel core quando questo è non vuoto. Shapley: "quanto ha contribuito ciascuno?" — sempre definito, additivo, ma non necessariamente stabile.

**11. Che cos'è un gioco semplice monotono?**
$v(S)\in\{0,1\}$ (semplice) e $v(S)=1\Rightarrow v(T)=1$ per $T\supseteq S$ (monotono); $S$ è vincente se $v(S)=1$, perdente altrimenti. Modella le procedure di voto; la ripartizione diventa la misura del **potere** dei votanti.

**12. Definisca Shapley–Shubik e Banzhaf.**
Con $W(i)=\{S$ perdente $: S\cup\{i\}$ vincente$\}$ (gli *swing* di $i$): $\mathrm{SSPI}_i=\sum_{S\in W(i)}|S|!(n-|S|-1)!/n!$ (= valore di Shapley del gioco semplice, probabilità di essere pivotale in un ordine casuale) e $\mathrm{BPI}_i=|W(i)|/2^{n-1}$ (frazione di coalizioni in cui $i$ è pivotale, non efficiente: si normalizza).

**13. Unanimità e dittatura.**
Unanimità $v_u(S)=1$ sse $S=N$: $W(i)=\{N\setminus i\}$, quindi $\mathrm{SSPI}_i=1/n$ e $\mathrm{BPI}_i=1/2^{n-1}$ (stessa quota relativa per tutti). Dittatura $v_d(S)=1$ sse $k\in S$: entrambi gli indici danno 1 a $k$ e 0 agli altri.

**14. Calcoli gli indici per il Consiglio di Sicurezza ONU.**
$n=15$, $v(S)=1$ sse $P\subseteq S$ ($|P|=5$) e $|S|\ge9$. Per $i\notin P$ gli swing sono $S\supseteq P$ con $|S|=8$: $\binom93=84$, quindi $\mathrm{SSPI}_i=84\cdot 8!6!/15!\approx0.00186$ e, per efficienza, $\mathrm{SSPI}_p=(1-10\cdot0.00186)/5\approx0.19628$. Banzhaf (slide): $\approx0.00513$ e $\approx0.01282$, cioè circa $4.5\%$ e $11\%$ normalizzati.

**15. Che differenza c'è fra Shapley–Shubik e Banzhaf?**
Entrambi contano gli swing $W(i)$, ma il SSPI li pesa con $|S|!(n-|S|-1)!/n!$ (conta gli *ordini*, ed è efficiente: la somma fa 1), mentre il BPI li conta tutti allo stesso modo dividendo per $2^{n-1}$ (conta le *coalizioni*, e non è efficiente: va normalizzato per confrontare i giocatori). Il BPI soddisfa comunque la proprietà di null player.

**16. Che cosa il corso non copre?**
Giochi bayesiani, aste, mechanism design (e quindi VCG), giochi dinamici/differenziali, evolutivi, mean-field, combinatori, razionalità limitata, cake cutting, raffinamenti del NE, giochi coalizionali NTU e con esternalità, giochi ripetuti e di segnalazione.
