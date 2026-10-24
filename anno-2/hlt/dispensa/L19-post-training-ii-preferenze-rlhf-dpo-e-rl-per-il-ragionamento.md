# L19 · Post-training II: preferenze, RLHF, DPO e RL per il ragionamento

*Post-training: Preferences* · 23/10/2026 · Claudio Gallicchio · lettura: J&M cap. 8, §8.3-8.4; cap. 1, §1.6.3-1.6.4, §1.7, §1.10

[Versione interattiva sul sito](https://gabriele-marsili.github.io/appunti-magistrale-ai/anno-2/hlt/sito/#L19) · [Indice della dispensa](README.md)

Seconda lezione sul **post-training** (J&M §8.3-8.4 e cap. 1): dopo l'SFT, gli stadi 3 e 4 della pipeline. Le **preferenze** (risposta scelta contro scartata) diventano probabilità con il modello di **Bradley-Terry**, $\sigma(z_i - z_j)$, e un **reward model** addestrato con $-\log\sigma(r_w - r_l)$. Con il reward si fa **RLHF**: massimizzare il reward atteso con una **penalità KL** dal modello di partenza, con il policy gradient (REINFORCE), la baseline e l'advantage, e **PPO** con quattro modelli. **DPO** ottiene lo stesso con una loss supervisionata sulle coppie e due modelli. Per il ragionamento: chain of thought, reward verificabili (**RLVR**) e **GRPO**. Chiudono alignment, sycophancy e limiti aperti. Tutti i numeri delle slide tornano: nessuna correzione. Con il notebook (nessun bug, mostra il reward hacking da length bias) e la scheda di 11 esercizi.

## Indice

- [Apertura](#apertura)
- [Dati di preferenza](#dati-di-preferenza)
- [Reward model](#reward-model)
- [RLHF](#rlhf)
- [DPO](#dpo)
- [RL per il ragionamento](#rl-per-il-ragionamento)
- [Sicurezza e allineamento](#sicurezza-e-allineamento)
- [Notebook](#notebook)
- [Studio ed esercizi](#studio-ed-esercizi)

## Apertura

<a id="p-1"></a>

### Slide 1 · Post-training II: preferenze

Lezione 19, di Claudio Gallicchio (23 ottobre 2026, seconda parte del pomeriggio, 16-18): continua il **post-training** iniziato nella lezione precedente con l'instruction tuning. Il sottotitolo dice il programma: **preference alignment**, **RLHF**, **DPO** e **RL per il ragionamento**.

Il filo della lezione: dopo l'SFT il modello sa seguire istruzioni, ma non sempre risponde nel modo migliore. Si introduce un segnale nuovo, il **confronto fra due risposte** (quale è meglio), lo si trasforma in probabilità con il modello di **Bradley-Terry**, se ne ricava un **reward model** e lo si usa per spostare il modello verso le risposte preferite, con reinforcement learning (RLHF, PPO) o con una loss supervisionata (DPO). Infine il caso in cui la risposta si verifica da sola (matematica, vincoli di formato): **RLVR** e GRPO, la ricetta dei modelli di ragionamento.

<a id="p-2"></a>

### Slide 2 · Indice

Sette parti, nell'ordine della pipeline:

1. **dove siamo**: gli stadi 3 e 4 del training di un LLM;
2. **preference data**: prompt, risposta scelta e risposta scartata;
3. **reward model**: dal confronto a un punteggio, con Bradley-Terry e una loss di cross-entropy;
4. **RLHF**: reinforcement learning con il reward model, penalità KL, baseline, PPO;
5. **DPO**: le stesse preferenze senza reward model né campionamento;
6. **RL per il ragionamento**: chain of thought, reward verificabili, GRPO;
7. **safety e alignment**: che cosa resta aperto (sycophancy, allucinazioni, calibrazione).

Le prime tre parti stanno prima della pausa (scheda 21), le altre dopo.

<a id="p-3"></a>

### Slide 3 · Riferimento: J&M capitoli 8 e 1

Lettura principale: **capitolo 8** di Jurafsky e Martin (Post-training), paragrafi **8.3** Learning from Preferences (pp. 215-219: dati di preferenza, Bradley-Terry con la derivazione dal logit, reward model) e **8.4** LLM Alignment via Preference-Based Learning (pp. 219-223: il quadro RL, l'obiettivo con KL, DPO). Nel draft di agosto 2026 il paragrafo su PPO (8.4.1) è ancora vuoto: per PPO, baseline e GRPO fanno fede le slide e i paper citati.

Dal **capitolo 1**: §1.6.3 Preference Alignment e §1.6.4 RL for Reasoning (pp. 19-21), §1.7 Inference con la chain of thought (pp. 21-24), §1.10 Safety and Alignment (pp. 29-31). Lettura facoltativa: Alammar e Grootendorst, *Hands-On Large Language Models*, cap. 12.

<a id="p-4"></a>

### Slide 4 · Dove siamo: lo stadio 2

La figura (del libro, cap. 1) è la pipeline completa di un LLM moderno in quattro stadi, ognuno con i suoi dati: **1. pretraining** (la pila di libri: testo grezzo) dà il pretrained LLM; **2. instruction tuning** (istruzioni con risposte: sentiment, riassunto, traduzione) dà l'instruction-tuned LLM; **3. preference alignment** (un prompt con due risposte, una col pollice in su e una col pollice in giù) dà il preference-aligned LLM; **4. RL with verifiable rewards** (un problema di matematica con la soluzione controllabile, il segno di spunta verde) dà il modello finale.

Qui il riquadro evidenzia lo stadio 2: è la **prima parte del pomeriggio**, dalle 14 alle 16, cioè la lezione precedente sull'instruction tuning (SFT), LoRA e prompting. Ogni stadio parte dal modello prodotto dallo stadio prima: le frecce doppie della figura.

<a id="p-5"></a>

### Slide 5 · Dove siamo: gli stadi 3 e 4

Stessa figura, ora il riquadro copre gli stadi **3 (preference alignment)** e **4 (RL with verifiable rewards)**: sono l'argomento di oggi.

Che cosa li accomuna, e li distingue dai primi due: nel pretraining e nell'SFT il modello vede la **risposta giusta** e impara a renderla più probabile, token per token (next-token prediction, loss di cross-entropy). Negli stadi 3 e 4 la risposta giusta **non c'è**: il modello genera, qualcuno o qualcosa dà un **reward** (un giudizio sull'intera risposta) e l'addestramento sposta probabilità verso le risposte premiate. È l'idea del **reinforcement learning**.

La differenza fra i due stadi è da dove viene il reward: da **preferenze umane** (o di un LLM) nello stadio 3, da un **controllo automatico** (la risposta è corretta? il formato è rispettato?) nello stadio 4.

<a id="p-6"></a>

### Slide 6 · Dopo l'instruction tuning

Perché non basta l'SFT (J&M §8.3, p. 215):

- **problemi residui**: un modello instruction-tuned può ancora dare risposte illegali, pericolose o fattualmente sbagliate; oppure risposte corrette ma **meno utili** di quanto potrebbero (troppo vaghe, troppo lunghe, poco chiare);
- **un segnale nuovo**: non più la risposta corretta da imitare, ma **quale di due risposte è migliore**. È molto più facile da raccogliere: scrivere una risposta ideale a una domanda difficile richiede un esperto, confrontarne due no;
- **l'obiettivo**: modelli più **helpful**, più **honest**, meno **harmful** (le tre H, la formula di Anthropic usata anche dal libro).

Il limite dell'SFT è strutturale: impara solo da esempi positivi, quindi non riceve mai un segnale esplicito su che cosa *non* dire. I confronti invece portano sia un esempio migliore sia uno peggiore.

## Dati di preferenza

<a id="p-7"></a>
**Slide 7 · Preference data** — Prima parte: che cosa sono i dati di preferenza e da dove vengono.

<a id="p-8"></a>

### Slide 8 · Giudizi di preferenza

Il punto chiave della slide: **una preferenza non richiede competenza**, solo un'opinione sul risultato. Per scrivere la risposta giusta a una domanda di chimica serve un chimico; per dire quale di due risposte ti è sembrata più chiara basta leggerle.

Le forme in cui si esprime una preferenza (J&M p. 216):

- scegliere la migliore fra **due opzioni** (il caso standard);
- sceglierne **una da un menu** di molte;
- una **classifica** (una top-10);
- un semplice **sì o no** su un'opzione isolata.

La seconda idea: a differenza delle istruzioni, le preferenze dicono al modello anche **che cosa non dire**, perché ogni coppia contiene una risposta scartata. È un segnale di tipo nuovo: **meglio o peggio**, non giusto o sbagliato. Una preferenza è sempre relativa: dice solo che una risposta batte l'altra.

<a id="p-9"></a>

### Slide 9 · Dati di preferenza: tre esempi

Un esempio di preference data è una tripla: un **prompt $x$** e due output campionati da un LLM, quello **scelto** (chosen) e quello **scartato** (rejected). Si scrive $o_i \succ o_j \mid x$: $o_i$ è preferito a $o_j$ dato il prompt $x$. I tre esempi della slide (dal dataset HH-RLHF di Anthropic, Bai et al. 2022, come nella fig. 1.10 del libro):

- **impersonare il genitore** in chat con la figlia: scelta la risposta che rifiuta e propone alternative (babysitter), scartata quella che accetta. È una preferenza di **sicurezza** (harmless);
- **che cos'è la malaria**: scelta la risposta che cita il CDC, scartata *I don't know*. Preferenza di **utilità** (helpful);
- **il ketchup è uno smoothie?**: scelta una risposta **falsa** (negli USA i cibi in bottiglia si chiamerebbero smoothie), scartato un secco *Yes*.

Il terzo esempio è il messaggio della slide: la risposta scelta **non deve essere buona, solo migliore**. Nei dataset reali molte risposte scelte sono mediocri, eppure il segnale relativo aiuta lo stesso.

<a id="p-10"></a>

### Slide 10 · Da classifiche a coppie

Gli algoritmi di oggi lavorano su **coppie** (vincitore, perdente). Tre modi di ottenerle:

- **coppie dirette**: annotatori addestrati confrontano due output;
- **classifica di $N$ output**: ogni coppia della classifica è una preferenza, quindi $\binom{N}{2} = N(N-1)/2$ coppie. Con $A \succ B \succ C \succ D$: 6 coppie ($A{\succ}B$, $A{\succ}C$, $A{\succ}D$, $B{\succ}C$, $B{\succ}D$, $C{\succ}D$). InstructGPT faceva ordinare da 4 a 9 output: da 6 a 36 coppie per prompt;
- **una sola scelta fra $N$**: l'annotatore indica solo il migliore, che batte tutti gli altri: $N-1$ coppie (con 4 output, 3 coppie: $A{\succ}B$, $A{\succ}C$, $A{\succ}D$), e nulla si sa sull'ordine fra gli altri.

Una classifica costa all'annotatore poco più di una scelta, ma rende molte più coppie: è il motivo per cui InstructGPT la usava. Le coppie della stessa classifica però non sono indipendenti (condividono lo stesso prompt e gli stessi output); Ouyang et al. le mettevano nello stesso batch per non sovra-adattarsi.

> **Da saper fare: Contare le coppie**
>
> Classifica di $N$ output: $N(N-1)/2$ coppie ($N=4$: 6; $N=5$: 10; $N=9$: 36). Solo il migliore fra $N$: $N-1$ coppie ($N=5$: 4). Verificato con `math.comb`. Con voti (scheda 11) le coppie a pari voti si scartano: voti 40, 12, 12, 3 danno $6 - 1 = 5$ coppie.

<a id="p-11"></a>

### Slide 11 · Da dove vengono le preferenze

Tre fonti (J&M pp. 216-217), in ordine di costo decrescente:

- **persone**: per InstructGPT i prompt venivano da richieste reali di utenti delle applicazioni OpenAI, gli output da modelli precedenti, e il giudizio da **annotatori addestrati** per il compito. Qualità alta, costo alto;
- **voti online**: su Reddit o StackExchange il post è il prompt, le risposte sono gli output e i **voti** degli utenti le ordinano (fig. 8.9 del libro). Preferenze implicite, gratuite, ma rumorose e legate al gusto di quella comunità;
- **language model**: in UltraFeedback le risposte di molti LLM diversi sono ordinate da **GPT-4** (LLM-as-a-judge). Nessuna persona coinvolta: si scala facilmente, ma si ereditano i difetti del giudice.

Il libro cita anche una quarta via: punteggi su una scala (0-4) per **aspetti** separati, come helpfulness, correttezza, verbosità, da cui si ricavano le coppie.

> **Approfondimento: Per il progetto**
>
> Lo stesso problema si presenta nei dataset di **hate speech**: le etichette sono giudizi di annotatori (o di un LLM), e chi giudica conta. Annotatori diversi danno etichette diverse sugli stessi testi, e un LLM usato per etichettare porta i suoi bias. Nel progetto vale la pena dire da dove vengono le etichette del dataset (annotatori, crowdsourcing, accordo fra annotatori) e trattarle come un *surrogato* del concetto che vogliamo, esattamente come il reward model è un surrogato di ciò che vogliamo davvero (scheda 19 e notebook).

## Reward model

<a id="p-12"></a>
**Slide 12 · Reward model** — Seconda parte: dalle coppie a un punteggio per ogni risposta.

<a id="p-13"></a>

### Slide 13 · Dalle preferenze alle probabilità

L'ipotesi di partenza (J&M §8.3.2, p. 218): chi esprime una preferenza assegna implicitamente a ogni output un **punteggio nascosto**, un numero reale $z_i$, e preferisce quello con il punteggio più alto.

Ma non vogliamo solo sapere *chi vince*: vogliamo una **probabilità** $P(o_i \succ o_j \mid x)$. Due motivi:

- distingue una **preferenza debole** (due risposte quasi equivalenti, gli annotatori si dividono) da una **forte** (tutti scelgono la stessa);
- una probabilità si può **imparare** con la massima verosimiglianza e la discesa del gradiente.

La strada è quella della **regressione logistica** ([la sigmoide, scheda 22 della L6](L06-regressione-logistica.md#p-22)): là un punteggio $z = w\cdot x + b$ diventava la probabilità della classe positiva; qui la **differenza** di due punteggi diventa la probabilità che il primo output vinca.

<a id="p-14"></a>

### Slide 14 · Il modello di Bradley-Terry

Il modello di **Bradley-Terry** (1952, nato per i tornei e i confronti a coppie): $$P(o_i \succ o_j \mid x) = \frac{1}{1+e^{-(z_i - z_j)}} = \sigma(z_i - z_j).$$ Il grafico mostra la sigmoide in funzione di $z_i - z_j$ (da $-5$ a $5$) con quattro punti marcati: $\sigma(-1) = 0{,}27$, $\sigma(0) = 0{,}50$, $\sigma(1) = 0{,}73$, $\sigma(3) = 0{,}95$ (verificati: 0,2689; 0,5; 0,7311; 0,9526).

- **differenza piccola**: probabilità vicina a 0,5, preferenza debole o assente;
- **differenza grande**: probabilità vicina a 1 (o a 0 se negativa);
- **simmetria**: $P(o_j \succ o_i) = \sigma(z_j - z_i) = 1 - \sigma(z_i - z_j)$, le due probabilità sommano a 1.

È la stessa sigmoide della regressione logistica binaria. Il libro ne dà la motivazione: la differenza $\delta = z_i - z_j$ è il **log-odds** (il [logit della L6](L06-regressione-logistica.md#p-24)) della preferenza, $\delta = \log\frac{P(o_i\succ o_j)}{1-P(o_i\succ o_j)}$; esponenziando e risolvendo per $P$ si torna a $\sigma(\delta)$.

> **Da saper fare: Dal logit alla sigmoide, e ritorno**
>
> Da $e^{\delta} = \frac{P}{1-P}$: $e^{\delta}(1-P) = P$, quindi $e^{\delta} = P(1+e^{\delta})$ e $P = \frac{e^{\delta}}{1+e^{\delta}} = \frac{1}{1+e^{-\delta}}$. All'inverso, una probabilità $p$ corrisponde alla differenza $\ln\frac{p}{1-p}$: per l'80% serve $\ln 4 = 1{,}386$. Conseguenza importante: aggiungere la stessa costante a tutti i punteggi non cambia nessuna probabilità, quindi i punteggi sono definiti **a meno di una costante** (esercizio 2b).

<a id="p-15"></a>

### Slide 15 · Un reward model

I punteggi $z$ non li conosciamo: abbiamo solo i confronti. Allora si **impara una funzione** che li produce (J&M §8.3.3, p. 219):

- **il reward** $r(x, o)$: un numero per ogni coppia (prompt, output), che fa la parte del punteggio $z$;
- **la probabilità**: $P(o_i \succ o_j \mid x) = \sigma\big(r(x, o_i) - r(x, o_j)\big)$, Bradley-Terry con i reward al posto dei punteggi;
- **i dati**: le coppie di preferenza, ognuna con un vincitore $o_w$ (winner) e un perdente $o_l$ (loser).

Il vantaggio rispetto a imparare un punteggio per ogni risposta vista: $r$ è una funzione del testo, quindi **generalizza** a risposte mai giudicate. È questo che permette di usarlo per dare un voto alle risposte nuove che il modello genererà durante l'addestramento (parte RLHF).

<a id="p-16"></a>

### Slide 16 · La loss del reward model

Si addestra $r$ con la **massima verosimiglianza** delle preferenze osservate. Il target è $P(o_w \succ o_l \mid x) = 1$ per ogni coppia dei dati, quindi la loss di una coppia è meno il log della probabilità della preferenza osservata: $$L_{CE}(x, o_w, o_l) = -\log P(o_w \succ o_l \mid x) = -\log \sigma\big(r(x,o_w) - r(x,o_l)\big).$$ Sul dataset $D$ si fa la media: $L_{CE} = -\mathbb{E}_{(x,o_w,o_l)\sim D}\big[\log\sigma(r(x,o_w)-r(x,o_l))\big]$ (eq. 8.4 del libro).

È una **binary cross-entropy**, la stessa della regressione logistica ([scheda 38 della L6](L06-regressione-logistica.md#p-38)) con etichetta sempre 1 e logit uguale alla differenza dei reward. Si minimizza con la discesa del gradiente. Comportamento: se il reward model già ordina bene la coppia con largo margine la loss è vicina a 0; a parità di reward vale $\ln 2 = 0{,}693$; se ordina al contrario cresce circa linearmente con il margine sbagliato.

<a id="p-17"></a>

### Slide 17 · Esercizio: la loss del reward model

Esercizio in aula (3 minuti, carta e penna). Tre coppie con i reward del vincitore e del perdente: (2,0; 1,0), (1,0; 1,0), (0,5; 2,5). Per ciascuna: la differenza, la probabilità $\sigma$ della differenza, la loss $-\ln\sigma$, poi la media. I valori utili sono dati: $\sigma(1) = 0{,}73$, $\sigma(0) = 0{,}50$, $\sigma(-2) = 0{,}12$ e le loro $-\ln$: 0,31; 0,69; 2,13.

La domanda finale (quale coppia fa cambiare di più i reward) è il punto concettuale: lo si legge dal gradiente nella scheda dopo. Prima di guardare la soluzione, notare la coppia 3: il reward model dà **più** reward al perdente che al vincitore, cioè ordina la coppia al contrario.

<a id="p-18"></a>

### Slide 18 · La loss del reward model a mano

La soluzione in tabella:

| coppia | differenza | $\sigma$ | loss | $1-\sigma$ |
| --- | --- | --- | --- | --- |
| 1 | 1,0 | 0,73 | 0,31 | 0,27 |
| 2 | 0,0 | 0,50 | 0,69 | 0,50 |
| 3 | $-2{,}0$ | 0,12 | 2,13 | 0,88 |

Loss media $(0{,}31+0{,}69+2{,}13)/3 = 1{,}04$ (verificato: 1,0444). **Il gradiente**: la derivata della loss rispetto alla differenza $\Delta = r_w - r_l$ è $-(1-\sigma(\Delta))$, quindi la discesa del gradiente **alza $r(x,o_w)$ e abbassa $r(x,o_l)$** con forza $1-\sigma$, esattamente come nella regressione logistica ([scheda 45 della L6](L06-regressione-logistica.md#p-45), dove il gradiente era $(\sigma - y)x$). La coppia mal ordinata, la 3, riceve la spinta più forte (0,88); la coppia già ben ordinata quasi nessuna.

> **Da saper fare: Il gradiente in una riga**
>
> $\frac{d}{d\Delta}\big[-\ln\sigma(\Delta)\big] = -\frac{\sigma(\Delta)(1-\sigma(\Delta))}{\sigma(\Delta)} = -(1-\sigma(\Delta))$. Quindi $\partial L/\partial r_w = -(1-\sigma)$ e $\partial L/\partial r_l = +(1-\sigma)$: un passo di discesa sposta $r_w$ in su e $r_l$ in giù della stessa quantità $\eta(1-\sigma)$. Con un reward model neurale questo segnale si propaga all'indietro nei pesi (backpropagation).

<a id="p-19"></a>

### Slide 19 · Un reward model da un LLM

In pratica il reward model è a sua volta un LLM (Ziegler et al., 2019; fig. 8.10 del libro). Si parte da un **LLM preaddestrato** (spesso lo stesso modello che si vuole allineare) e si sostituisce la **language modeling head**, che dava un logit per ogni token del vocabolario, con uno strato lineare che dà **un solo numero**, il reward; di solito letto dal vettore dell'ultimo token.

La figura: dalla base di dati delle preferenze (il cilindro rosso, coppie $(x, o_i)$ con la preferenza $o_i \succ o_j$) escono le due coppie $(x, o_i)$ e $(x, o_j)$, che passano **nello stesso reward model** (disegnato due volte, ha gli stessi pesi) e danno $r(x,o_i)$ e $r(x,o_j)$. Questi entrano nella loss $-\log\sigma(r(x,o_i)-r(x,o_j))$, che riceve anche l'etichetta $o_i \succ o_j$ dal basso. Le frecce tratteggiate che tornano ai due modelli sono il gradiente: si addestra con la discesa del gradiente sulla loss delle coppie.

Perché partire da un LLM: per giudicare una risposta bisogna capirla, e la comprensione del linguaggio viene dal pretraining.

<a id="p-20"></a>

### Slide 20 · Usi di un reward model

Un reward model è utile anche da solo, prima di qualunque allineamento (J&M p. 219):

- **best-of-$N$ sampling**: si campionano $N$ risposte, si tiene quella con il reward più alto. Non cambia i pesi del modello, ma costa $N$ generazioni (più il reward model) per ogni risposta;
- **selezione dei dati**: si usano i reward per scegliere gli esempi migliori su cui fare instruction tuning;
- **alignment**: addestrare l'LLM a produrre output con reward alto. È il tema della seconda parte della lezione (RLHF).

Best-of-$N$ e alignment condividono il limite di fondo: ottimizzano il reward model, che è un **surrogato** delle preferenze vere. Più si spinge (più grande $N$, più passi di training), più si rischia di trovare risposte che piacciono al reward model per ragioni sbagliate (reward hacking, scheda 28 e notebook).

<a id="p-21"></a>
**Slide 21 · Pausa** — Dieci minuti di pausa; dopo: RLHF e DPO, RL per il ragionamento, safety.

## RLHF

<a id="p-22"></a>
**Slide 22 · Alignment con il reinforcement learning** — Terza parte: usare il reward model per addestrare l'LLM, con il reinforcement learning (RLHF).

<a id="p-23"></a>

### Slide 23 · Reinforcement learning

Il reinforcement learning (Sutton e Barto, 1998) in una frase: un **agente** impara per prova ed errore, **agisce** e riceve **reward**. Lo schema della slide è un ciclo: l'agente, con la sua **policy** $\pi$, sceglie un'azione; l'**ambiente** risponde con un nuovo stato e un reward, che tornano all'agente.

L'esempio degli scacchi fissa i quattro termini:

- **stato**: la posizione sulla scacchiera;
- **azione**: una mossa;
- **reward**: $+1$ per la vittoria, $-1$ per la sconfitta, 0 per la patta, e solo **alla fine della partita**;
- **policy**: la strategia, quale mossa giocare in ogni posizione.

La differenza con l'apprendimento supervisionato è nella frase in fondo: **nessuno dà la mossa giusta**, solo il risultato finale. L'agente deve capire da solo quali delle sue scelte hanno portato a vincere.

<a id="p-24"></a>

### Slide 24 · Reinforcement learning per un LLM

Lo stesso ciclo per un LLM (J&M p. 220): **molte azioni, un solo reward alla fine**. La figura: il prompt `How do I hard-boil an egg?` e la risposta che si costruisce token per token, `Boil it for 10 minutes .`; il riquadro azzurro racchiude prompt e `Boil it for`, cioè lo stato quando si sceglie il token successivo. Sotto, la distribuzione su quel token: `10` con 0,5, `8` con 0,3, `2` con 0,2 (si campiona `10`). A destra, a risposta finita, il reward model dà $r(x, o) = 3{,}0$.

- **azioni**: i token, scelti uno alla volta;
- **stato**: il prompt più i token generati finora;
- **policy $\pi$**: l'LLM stesso, cioè le probabilità del token successivo da cui si campiona;
- **reward $r(x,o)$**: il reward model, un punteggio per l'**intera risposta**, dato alla fine.

Due differenze dal RL classico, sottolineate dal libro: il reward non è un fatto osservabile (vincere o perdere) ma un **surrogato rumoroso** appreso; e non si parte da una policy casuale ma da un modello già ottimo, da **spingere** leggermente, non da rifare.

<a id="p-25"></a>

### Slide 25 · Il reward atteso

Un giocattolo per capire che cosa si ottimizza: il prompt `How do I hard-boil an egg?` con solo **quattro** risposte possibili (numeri inventati). Il grafico a barre mostra $\pi(o\mid x)$: *clear steps* 0,20 ($r=3$), *right, but very long* 0,30 ($r=2$), *not sure* 0,30 ($r=1$), *wrong time* 0,20 ($r=0$).

- $\pi(o \mid x)$ è la probabilità di un'**intera risposta**, il prodotto delle probabilità dei suoi token (fattorizzazione autoregressiva);
- $r(x, o)$ è il punteggio del reward model.

Il **reward atteso** è la media dei reward pesata con le probabilità: $\mathbb{E}_{o\sim\pi}[r] = 0{,}2\cdot3 + 0{,}3\cdot2 + 0{,}3\cdot1 + 0{,}2\cdot0 = 1{,}5$ (verificato). Con un modello vero le risposte possibili sono infinite e non si può sommare: si **campionano** risposte e si fa la media dei loro reward (stima Monte Carlo).

<a id="p-26"></a>

### Slide 26 · Il reward atteso dopo il training

Dopo il training: **stesse risposte, stessi reward, nuove probabilità**. Le barre ora sono 0,55; 0,30; 0,10; 0,05; i segni grigi orizzontali mostrano dove stavano prima (0,20; 0,30; 0,30; 0,20). Si sono alzate le risposte con reward alto (*clear steps* da 0,20 a 0,55), abbassate quelle con reward basso (*not sure* da 0,30 a 0,10, *wrong time* da 0,20 a 0,05).

Il reward atteso passa da 1,5 a $0{,}55\cdot3 + 0{,}30\cdot2 + 0{,}10\cdot1 + 0{,}05\cdot0 = 2{,}35$ (verificato; le nuove probabilità sommano ancora a 1).

Il messaggio: il reward model è **fisso**, quello che l'addestramento cambia è solo la policy, cioè **dove mette la probabilità**. Allineare significa spostare massa di probabilità verso le risposte premiate.

<a id="p-27"></a>

### Slide 27 · L'obiettivo

L'obiettivo in forma compatta (eq. 8.5 del libro): $$\pi^* = \arg\max_{\pi_\theta}\ \mathbb{E}_{x\sim D,\ o\sim\pi_\theta(o\mid x)}\big[r(x,o)\big].$$ La slide lo legge pezzo per pezzo, con i colori:

- **campionare prompt $x$** da un insieme di prompt di training $D$ (servono solo prompt, nessuna risposta);
- **campionare output $o$** dalla policy $\pi_\theta$, il modello che si sta addestrando;
- **dare un punteggio** a ogni output con il reward model;
- **trovare la policy** con il reward atteso più alto (l'argmax su $\theta$).

Da notare la differenza con l'SFT: là la distribuzione dei dati era fissa (le risposte del dataset); qui gli output vengono dal modello stesso, quindi la distribuzione su cui si fa la media **cambia mentre il modello si addestra**. Per questo il gradiente non si calcola come in una loss normale (scheda 29).

<a id="p-28"></a>

### Slide 28 · Restare vicini al punto di partenza

L'obiettivo con la **penalità KL** (eq. 8.7 del libro): $$\pi^* = \arg\max_{\pi_\theta}\ \mathbb{E}_{x\sim D,\ o\sim\pi_\theta}\Big[r(x,o) - \beta\log\frac{\pi_\theta(o\mid x)}{\pi_{\mathrm{ref}}(o\mid x)}\Big].$$

- **il rischio**: ottimizzando solo il reward, il modello dimentica ciò che ha imparato nel pretraining, inseguendo reward alti su pochi dati di preferenza. Peggio, trova risposte strane che il reward model premia per errore (**reward hacking**: il reward model è solo un surrogato);
- **la penalità**: la **divergenza KL** dalla policy di riferimento $\pi_{\mathrm{ref}}$, il modello di partenza (quello dopo SFT). Misura quanto due distribuzioni differiscono; non è simmetrica, quindi non è una vera distanza. Per **un** output la penalità è il log-rapporto delle due probabilità; **in media** sugli output campionati da $\pi_\theta$ quel log-rapporto è proprio la KL: $\mathbb{E}_{o\sim\pi_\theta}\big[\log\frac{\pi_\theta}{\pi_{\mathrm{ref}}}\big] = D_{KL}(\pi_\theta\,\|\,\pi_{\mathrm{ref}})$;
- **$\beta$**: iperparametro, il peso della penalità. $\beta$ grande, il modello resta vicino a $\pi_{\mathrm{ref}}$; $\beta$ piccolo, insegue il reward.

> **Da saper fare: La penalità di un output**
>
> Output con $r = 0{,}8$, $\pi_{\mathrm{ref}} = 0{,}05$, $\pi_\theta = 0{,}20$, $\beta = 0{,}2$: log-rapporto $\ln 4 = 1{,}386$, penalità $0{,}277$, reward penalizzato $0{,}523$ (esercizio 7). Se la policy dà ancora 0,05 la penalità è 0. Un output che la policy ha reso *meno* probabile del riferimento ha log-rapporto negativo, quindi riceve un bonus: in media però la KL è sempre $\ge 0$.

> **Approfondimento: KL e cross-entropy**
>
> $D_{KL}(p\,\|\,q) = \sum_o p(o)\log\frac{p(o)}{q(o)} = H(p, q) - H(p)$: cross-entropy meno entropia ([cross-entropy della L5](L05-smoothing-ed-entropia.md#p-38)). Vale 0 solo se $p = q$. Sul giocattolo: $D_{KL}(\pi_{\text{dopo}}\|\pi_{\text{prima}}) = 0{,}377$, $D_{KL}(\pi_{\text{prima}}\|\pi_{\text{dopo}}) = 0{,}405$: diverse, la non simmetria della slide.

<a id="p-29"></a>

### Slide 29 · Il policy gradient

Come si calcola il gradiente di un obiettivo in cui gli output vengono dal modello stesso? Si confronta con l'SFT:

- **in SFT**: $\theta \leftarrow \theta + \eta\,\nabla_\theta\log\pi_\theta(o\mid x)$, con $o$ la risposta del dataset: un passo di gradiente la rende più probabile (è la discesa sulla negative log-likelihood, scritta come salita);
- **in RL**: $\theta \leftarrow \theta + \eta\,r(x,o)\,\nabla_\theta\log\pi_\theta(o\mid x)$, con $o$ **campionato da $\pi_\theta$**: lo stesso passo, pesato dal suo reward (con la penalità KL incorporata nel reward).

Lettura dei due fattori: $\nabla_\theta\log\pi_\theta(o\mid x)$ è la **direzione** in cui $o$ diventa più probabile; $r(x,o)$ è la **lunghezza del passo** (reward alto, passo lungo; reward 0, nessun passo). In media su molti campioni la direzione risultante è quella che aumenta il reward atteso.

È l'algoritmo **REINFORCE** (Williams, 1992): **SFT sui propri output, pesato con il reward**.

> **Approfondimento: Perché funziona: il trucco del log**
>
> $\nabla_\theta\mathbb{E}_{o\sim\pi_\theta}[r(o)] = \sum_o r(o)\nabla_\theta\pi_\theta(o) = \sum_o \pi_\theta(o)\,r(o)\,\nabla_\theta\log\pi_\theta(o) = \mathbb{E}_{o\sim\pi_\theta}\big[r(o)\nabla_\theta\log\pi_\theta(o)\big]$, usando $\nabla\pi = \pi\nabla\log\pi$. Il gradiente del reward atteso è quindi una media su campioni del modello: si stima campionando, e il passo della slide è la stima con un solo campione. Per un LLM $\log\pi_\theta(o\mid x) = \sum_t\log\pi_\theta(o_t\mid x, o_{&lt;t})$, la stessa somma della loss di SFT.

<a id="p-30"></a>

### Slide 30 · La baseline

Problema di REINFORCE: con reward tutti positivi (3, 2, 1, 0 nel giocattolo) **ogni** output campionato viene reso più probabile, anche quelli mediocri; solo in media, su moltissimi campioni, le spinte si bilanciano nella direzione giusta. Il gradiente è molto rumoroso.

Rimedio: sottrarre una **baseline** $b$, il reward atteso della policy corrente: $\theta \leftarrow \theta + \eta\,(r(x,o) - b)\,\nabla_\theta\log\pi_\theta(o\mid x)$. Sul giocattolo prima del training $b = 1{,}5$ e la tabella dà:

| output | $r$ | $r-b$ | il passo |
| --- | --- | --- | --- |
| clear steps | 3,0 | $+1{,}5$ | su di 1,5 |
| very long | 2,0 | $+0{,}5$ | su di 0,5 |
| not sure | 1,0 | $-0{,}5$ | giù di 0,5 |
| wrong time | 0,0 | $-1{,}5$ | giù di 1,5 |

$r - b$ è l'**advantage**: quanto un output è **migliore del previsto**. Ora ogni campione spinge nel verso giusto (su se sopra la media, giù se sotto); in media la direzione è la stessa (la baseline non introduce distorsione, perché $\mathbb{E}[\nabla\log\pi] = 0$), con molto meno rumore. Due modi di avere $b$: in **PPO** la stima un **value model**; in **GRPO** è la media dei reward di un gruppo di risposte.

<a id="p-31"></a>

### Slide 31 · Preference-based alignment (RLHF)

Il quadro complessivo (fig. 8.11 del libro): a sinistra l'**instruction-tuned LLM** $\pi_{\mathrm{SFT}}$, a destra il **preference-aligned model** $\pi_\theta$. In mezzo il blocco **Reward Driven Model Updates**, che riceve dall'alto i dati di preferenza (il cilindro: coppie $(x, o_i)$, preferenze $o_i\succ o_j$) e l'**obiettivo basato sul reward** (l'ottagono azzurro).

Il nome: **reinforcement learning from human feedback**, RLHF. Il feedback umano entra solo attraverso le preferenze, condensate nel reward model; l'addestramento vero è reinforcement learning sulla policy. Il punto di partenza è sempre il modello dopo SFT, che fa anche da $\pi_{\mathrm{ref}}$ per la penalità KL: l'idea è **spingere** un modello già buono, non rifarlo.

<a id="p-32"></a>

### Slide 32 · RLHF in tre passi (InstructGPT)

La ricetta di InstructGPT (Ouyang et al., 2022), il metodo dietro le prime versioni di ChatGPT:

1. **SFT**: persone scrivono risposte a prompt; si fa fine-tuning di GPT-3 su queste dimostrazioni (la lezione precedente);
2. **reward model**: persone ordinano da 4 a 9 output del modello per prompt; si addestra un reward model sulle coppie (schede 10-19);
3. **RL**: si massimizza il reward degli output, con la penalità KL, usando l'algoritmo **PPO**.

Il risultato più citato del paper: gli output di **InstructGPT da 1,3 miliardi** di parametri erano **preferiti** dagli annotatori a quelli di **GPT-3 da 175 miliardi**, un modello oltre 100 volte più grande. L'allineamento non aggiunge conoscenza (quella viene dal pretraining) ma rende il modello molto più utile per chi lo usa.

> **Approfondimento: Win rate: come si misura «preferito»**
>
> I modelli allineati si valutano spesso con il **win rate**: si mostrano a giudici (persone o un LLM) le risposte di due modelli allo stesso prompt e si conta quante volte vince il modello A. Con $W$ vittorie, $L$ sconfitte e $T$ pareggi, di solito $\text{win rate} = (W + T/2)/(W + L + T)$. Esempio: 110, 50, 40 su 200 confronti danno $(110+20)/200 = 0{,}65$ (0,6875 ignorando i pareggi). È di nuovo Bradley-Terry: un win rate di 0,65 corrisponde a una differenza di punteggi $\ln(0{,}65/0{,}35) = 0{,}62$. Attenzione al giudice: anche i giudici LLM tendono a preferire le risposte più lunghe, lo stesso length bias del reward model del notebook; per questo esistono win rate corretti per la lunghezza.

<a id="p-33"></a>

### Slide 33 · PPO: Proximal Policy Optimization

**PPO** (Schulman et al., 2017) è l'algoritmo di RL usato da InstructGPT. Richiede **quattro modelli** in memoria durante il training, tutti della taglia di un LLM:

- **policy $\pi_\theta$**: l'LLM, **addestrato**;
- **reference $\pi_{\mathrm{ref}}$**: **congelato**, serve per la penalità KL;
- **reward model**: **congelato**, dà il punteggio agli output;
- **value model**: **addestrato**, predice il reward atteso, cioè la baseline.

Quattro modelli in memoria, e in più la generazione di risposte a ogni passo: un metodo **costoso**. L'aggiornamento è quello della baseline: gli output con reward superiore al previsto (advantage $r - b$ positivo) diventano più probabili, gli altri meno. **Proximal**: ogni aggiornamento è tenuto **piccolo** (nel paper, il rapporto fra nuova e vecchia probabilità di un'azione viene tagliato in un intervallo come $[0{,}8;\ 1{,}2]$), così la policy cambia gradualmente e il training resta stabile.

## DPO

<a id="p-34"></a>
**Slide 34 · Direct Preference Optimization** — Quarta parte: le stesse preferenze, senza reward model e senza reinforcement learning.

<a id="p-35"></a>

### Slide 35 · La loss di DPO

**DPO** (Rafailov et al., 2023; J&M §8.4.2, pp. 222-223) addestra la policy direttamente sulle coppie di preferenza: $$L_{\mathrm{DPO}}(x, o_w, o_l) = -\log\sigma\Big(\beta\log\frac{\pi_\theta(o_w\mid x)}{\pi_{\mathrm{ref}}(o_w\mid x)} - \beta\log\frac{\pi_\theta(o_l\mid x)}{\pi_{\mathrm{ref}}(o_l\mid x)}\Big).$$

- in verde, il **log-rapporto dell'output scelto**: quanto $\pi_\theta$ lo rende più probabile di $\pi_{\mathrm{ref}}$;
- in rosso, **meno lo stesso per l'output scartato**;
- tutto insieme è **la loss del reward model** (scheda 16) con $\beta\log\pi_\theta/\pi_{\mathrm{ref}}$ al posto del reward di ogni output: il modello stesso fa da reward model (**reward implicito**).

Da dove viene: l'obiettivo con KL della scheda 28 ha una soluzione in forma chiusa, $\pi^*(o\mid x) \propto \pi_{\mathrm{ref}}(o\mid x)\exp(r(x,o)/\beta)$. Invertendola, $r(x,o) = \beta\log\frac{\pi^*(o\mid x)}{\pi_{\mathrm{ref}}(o\mid x)} + \beta\log Z(x)$; in Bradley-Terry conta solo la **differenza** dei reward, quindi $Z(x)$ (una somma su tutti gli output possibili, incalcolabile) si cancella. $\beta$ è lo stesso della penalità KL; valori tipici da 0,01 a 0,1.

> **Da saper fare: DPO a mano (esercizio 9)**
>
> Scelto: $\ln\pi_{\mathrm{ref}} = -8$, $\ln\pi_\theta = -7$, log-rapporto $+1$. Scartato: $-9$ e $-10$, log-rapporto $-1$. Con $\beta = 0{,}5$ l'argomento è $0{,}5\,(1-(-1)) = 1$ e la loss $-\ln\sigma(1) = 0{,}313$. All'inizio, con $\pi_\theta = \pi_{\mathrm{ref}}$, entrambi i log-rapporti sono 0 e la loss è $\ln 2 = 0{,}693$ per ogni coppia. Se invece entrambi i log-prob salgono di 1 l'argomento è 0 e la loss resta 0,693: a DPO interessa solo il **margine** fra i due log-rapporti, non i valori assoluti.

> **Da saper fare: Che cosa fa beta**
>
> Coppia con log-rapporti $+0{,}5$ (scelto) e $-0{,}5$ (scartato), differenza 1: con $\beta = 0{,}1$ loss $-\ln\sigma(0{,}1) = 0{,}644$; con $\beta = 0{,}5$, 0,474; con $\beta = 1$, 0,313. Il gradiente rispetto alla differenza dei log-rapporti vale $\beta(1-\sigma)$: 0,048; 0,189; 0,269. Con $\beta$ piccolo serve un margine di log-probabilità molto più grande per ridurre la loss, quindi la policy si allontana di più da $\pi_{\mathrm{ref}}$: è la stessa logica di $\beta$ nella penalità KL.

<a id="p-36"></a>

### Slide 36 · DPO o PPO

I vantaggi di DPO rispetto a PPO (J&M p. 223):

- **nessun reward model** esplicito da addestrare: il reward è implicito nel rapporto $\pi_\theta/\pi_{\mathrm{ref}}$;
- **nessun campionamento**: impara direttamente dalle coppie fisse di $D$, senza generare risposte da $\pi_\theta$ durante il training (la parte più costosa di PPO);
- **due modelli** in memoria, $\pi_\theta$ e $\pi_{\mathrm{ref}}$, invece dei quattro di PPO.

In sintesi: una **loss supervisionata su coppie di preferenza**, più semplice, più economica e più stabile. Il prezzo: DPO è **offline**, impara solo dalle risposte presenti nei dati, mentre PPO valuta le risposte che il modello produce adesso e può correggerne gli errori nuovi. E non toglie il problema di fondo: se le preferenze contengono un bias (per esempio verso le risposte lunghe), DPO lo impara come PPO (notebook, sezione 5).

> **Approfondimento: DPO in pratica**
>
> DPO si combina bene con LoRA (lezione precedente): si addestrano solo gli adattatori, e la policy di riferimento si ottiene gratis disattivandoli, così in memoria resta un solo modello base. Il gradiente di DPO è $-\beta(1-\sigma(\hat h))\big[\nabla\log\pi_\theta(o_w) - \nabla\log\pi_\theta(o_l)\big]$, con $\hat h$ l'argomento della sigmoide: come per il reward model, le coppie che il reward implicito ordina male pesano di più.

## RL per il ragionamento

<a id="p-37"></a>
**Slide 37 · RL per il ragionamento** — Quinta parte: quando la correttezza della risposta si può controllare in automatico.

<a id="p-38"></a>

### Slide 38 · Chain-of-thought prompting

La figura di Wei et al. (2022), fig. 1.15 del libro. A sinistra lo **standard prompting**: una dimostrazione (Roger ha 5 palline, compra 2 confezioni da 3; *A: The answer is 11.*) e la nuova domanda (la mensa aveva 23 mele, ne usa 20, ne compra 6): il modello risponde *27*, sbagliato (croce rossa). A destra il **chain-of-thought prompting**: la stessa dimostrazione con i passaggi, evidenziati in azzurro (*2 cans of 3 tennis balls each is 6 tennis balls. 5 + 6 = 11.*); il modello imita lo schema e scrive i suoi passaggi, in verde: $23 - 20 = 3$, $3 + 6 = 9$, risposta *9*, corretta.

Ogni dimostrazione mostra anche i **passi di ragionamento**, e il modello scrive passi simili prima della risposta. È un esempio di **test-time compute**: spendere più calcolo all'inferenza (più token generati) sui problemi difficili. Funziona perché ogni token generato è un passo di calcolo in più su cui il token successivo può appoggiarsi. Oggi i modelli sono addestrati a produrre queste catene da soli (scheda 41).

<a id="p-39"></a>

### Slide 39 · Dati verificabili

Un esempio da **GSM8K** (Cobbe et al., 2021; fig. 1.12 del libro): Herman nutre gli uccelli a dicembre, gennaio e febbraio, mezza tazza la mattina e mezza il pomeriggio; quante tazze in tutto? La risposta del dataset ragiona a passi: $31+31+28 = 90$ giorni (febbraio non bisestile), $1/2+1/2 = 1$ tazza al giorno, $1\cdot 90 = 90$ tazze. I conti tornano.

Il concetto: esistono **domini in cui una risposta si giudica giusta o sbagliata in automatico**, senza persone. La matematica è l'esempio canonico: basta confrontare il numero finale con quello atteso. I dataset vanno dall'aritmetica delle elementari (GSM8K) ai problemi di livello dottorato. Altri domini simili: codice con test automatici, giochi, logica.

<a id="p-40"></a>

### Slide 40 · Vincoli verificabili

Anche compiti senza una risposta giusta si possono rendere verificabili, se il prompt impone **vincoli formali** (dataset IFEval, Zhou et al. 2023; fig. 1.13 del libro). I tre prompt della slide:

- un saggio sulle lattine di alluminio che contenga le parole *waste*, *material*, *meal* e abbia **più di 30 frasi**;
- una scheda personaggio di D&D, tutta in **JSON** dentro i backtick del markdown, con le parole *medalist* e *theta*;
- lo sbarco sulla Luna è propaganda? La risposta deve contenere una di tre frasi esatte, *My answer is yes.*, *no.* o *maybe.*

Vincoli tipici: parole chiave, formato (JSON, markdown), lunghezza, lingua, un insieme fisso di risposte. Si controllano con un programma. Attenzione al limite: si verificano **i vincoli, non la correttezza del contenuto**. Nel terzo prompt *My answer is yes.* soddisfa il vincolo quanto *no*.

> **Approfondimento: Per il progetto**
>
> Se nel progetto si confronta l'encoder fine-tuned con un LLM in **zero-shot o few-shot** come baseline, conviene usare proprio questo trucco: chiedere una risposta in un insieme chiuso (*Answer with exactly one of: hate, offensive, neither*) e analizzarla con un programma, contando a parte le risposte fuori formato. È la stessa funzione di controllo che fa da reward in RLVR, qui usata per la valutazione.

<a id="p-41"></a>

### Slide 41 · RL con reward verificabili (RLVR)

**RLVR** (reinforcement learning with verifiable rewards): il modello riceve un reward per le risposte **verificabilmente corrette**.

- **il reward**: 1 se la risposta finale è corretta, o i vincoli sono rispettati; 0 altrimenti. Lo calcola un **programma**, non un reward model: niente surrogato appreso, quindi molto meno spazio per il reward hacking (ma solo ciò che si controlla viene premiato);
- **il training**: spinge i parametri verso le risposte corrette e lontano da quelle sbagliate, con lo stesso policy gradient di RLHF;
- **reasoning model**: i modelli addestrati così imparano a scrivere una spiegazione dettagliata, una **chain of thought**, prima della risposta. Nessuno insegna i passaggi: il reward guarda solo la risposta finale, e le catene che portano a risposte giuste vengono rinforzate.

È il passaggio dalla chain of thought *suggerita* con il prompt (scheda 38) a quella *appresa* con il reinforcement learning.

> **Approfondimento: pass@k**
>
> I modelli di ragionamento si valutano spesso con **pass@$k$**: la probabilità che almeno una di $k$ risposte campionate sia corretta. Con $n$ campioni di cui $c$ corretti, la stima non distorta è $1 - \binom{n-c}{k}/\binom{n}{k}$. Con $n = 8$, $c = 2$: pass@1 $= 0{,}25$, pass@4 $= 1 - 15/70 = 0{,}786$ (verificato). Non è nelle slide.

<a id="p-42"></a>

### Slide 42 · Gruppi di risposte (GRPO)

**GRPO** (Group Relative Policy Optimization, Shao et al. 2024, introdotto per DeepSeekMath) è l'algoritmo tipico di RLVR. Quattro passi:

1. **campionare un gruppo**: $G$ risposte alla stessa domanda, dalla policy;
2. **dare il punteggio**: reward 1 alle corrette, 0 alle altre;
3. **advantage**: quanto ogni risposta è migliore della media del suo gruppo;
4. **aggiornare**: alzare la probabilità delle risposte sopra la media, abbassare le altre; con la penalità KL.

$$A_i = \frac{r_i - \mathrm{mean}(r_1,\dots,r_G)}{\mathrm{std}(r_1,\dots,r_G)}$$ $r_i - \mathrm{mean}$: la **baseline è la media del gruppo** (scheda 30). La divisione per la deviazione standard mette tutte le domande sulla **stessa scala**; si aggiunge una piccola costante alla std per non dividere per 0. Quindi **nessun value model**: è il gruppo stesso a dire che cosa aspettarsi, e se il reward è un programma in memoria restano solo la policy e il riferimento per la KL, contro i quattro modelli di PPO.

> **Da saper fare: Advantage di un gruppo (esercizio 10)**
>
> $r = [1,1,0,0,0,1]$: media 0,5, std $\sqrt{\tfrac16\sum(r-0{,}5)^2} = 0{,}5$, advantage $[+1,+1,-1,-1,-1,+1]$. Con $r = [1,0,0,0]$: media 0,25, std $\sqrt{0{,}25\cdot0{,}75} = 0{,}433$, advantage $+1{,}73$ per l'unica corretta e $-0{,}58$ per le altre: una risposta giusta **rara** viene premiata molto. Con $[1,1,1,1,1,1]$ std = 0 e tutti gli advantage sono 0: un gruppo tutto giusto (o tutto sbagliato) **non insegna niente**. Le domande utili sono quelle che il modello a volte sbaglia.

## Sicurezza e allineamento

<a id="p-43"></a>
**Slide 43 · Safety e alignment** — Ultima parte: che cosa significa allineare un modello, e che cosa resta aperto.

<a id="p-44"></a>

### Slide 44 · Alignment

Definizione (J&M §1.10, p. 29): **alignment** è far sì che i language model **evitino danni**, agendo in modi allineati ai **bisogni e valori umani**.

- **AI safety**: il campo più ampio che studia i danni potenziali dei modelli di AI e come mitigarli; l'alignment ne è la parte che riguarda il comportamento dei modelli;
- **sottospecificato**: i bisogni di chi? i valori di chi? e se i valori sono in conflitto? (Kirk et al., 2023). Le preferenze raccolte rappresentano i giudizi di un certo gruppo di annotatori, con le loro istruzioni, non di tutti;
- **ancora aperto**: gli LLM attuali mostrano ancora molti danni che non sappiamo mitigare.

Il libro elenca danni per l'utente (dipendenza emotiva, de-skilling, sycophancy, danni rappresentazionali come stereotipi e hate speech, prestazioni peggiori per alcuni gruppi e lingue) e danni per la società (uso malevolo, impatto ambientale, concentrazione di potere). Un collegamento con la [scheda 49 della L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-49) sui danni rappresentazionali dei classificatori.

<a id="p-45"></a>

### Slide 45 · Sycophancy e preferenze

Un danno che nasce **proprio dall'allineamento con le preferenze**:

- **il comportamento**: quando l'utente dice qualcosa di sbagliato, i modelli spesso **gli danno ragione** invece di correggerlo (Sharma et al., 2024). È la **sycophancy** (piaggeria);
- **una causa**: le persone, e i preference model addestrati sui loro giudizi, a volte preferiscono una risposta convincente che **concorda con l'utente** a una corretta;
- **l'effetto**: ottimizzare per le preferenze può scambiare la **veridicità** con l'accordo.

La frase da ricordare: **le preferenze dicono che cosa piace alle persone, che non è sempre ciò che è vero**. È un caso concreto di reward hacking: il reward model è un surrogato e la policy ne sfrutta i difetti. Lo stesso vale per la **preferenza per le risposte lunghe** (length bias), che il notebook simula: un reward model appreso da annotatori a cui piace la lunghezza premia risposte lunghe anche sbagliate.

<a id="p-46"></a>

### Slide 46 · Mitigare i danni

Un problema **sociotecnico**: non solo informatica, ma anche economia, società, politica (J&M pp. 30-31). Quattro direzioni:

- **post-training**: includere esempi legati ai danni nei dati di instruction tuning e di preferenza (come la coppia sull'impersonare il genitore della scheda 9);
- **constitutional AI** (Bai et al., 2022): una **costituzione** scritta su sicurezza e danni, usata per **generare dati di training** (un modello critica e rivede le proprie risposte secondo i principi) e nel **system prompt**;
- **red teaming**: un team di sicurezza **attacca il proprio sistema** per trovarne le vulnerabilità prima degli altri;
- **value sensitive design**: misurare gli effetti dei modelli sulle persone che li usano, con il loro **consenso informato** (in università, tramite i comitati etici).

> **Approfondimento: Per il progetto**
>
> Un classificatore di **hate speech** è esattamente uno strumento di questa scheda: serve a filtrare dati di training, a valutare le risposte di un modello nel red teaming, a moderare. Per questo i suoi errori pesano in modo asimmetrico per gruppo: un classificatore che segnala come offensivi i testi in un certo dialetto (il libro cita Hofmann et al. 2024 sull'African American English) produce proprio il danno che dovrebbe ridurre. Nel progetto, misurare le prestazioni per sottogruppo e i falsi positivi su termini identitari è il modo concreto di affrontare la parte sul bias.

<a id="p-47"></a>

### Slide 47 · Alcuni limiti che restano

Problemi sistematici non necessariamente legati alla sicurezza (J&M p. 31):

- **allucinazione**: testo fattualmente sbagliato, in particolare persone o fatti **inventati**; grave soprattutto per gli agenti che agiscono nel mondo;
- **overconfidence**: linguaggio molto sicuro (*definitely*) anche quando la risposta è sbagliata;
- **calibrazione**: un modello è ben calibrato se, fra le risposte a cui dà probabilità 0,8, circa l'80% sono corrette. Gli LLM spesso non lo sono: l'accuratezza non corrisponde alla probabilità che assegnano.

Il post-training **riduce** questi problemi, **non li risolve**. Anzi, l'ottimizzazione per le preferenze può peggiorare la calibrazione: alle persone piacciono le risposte sicure di sé.

<a id="p-48"></a>

### Slide 48 · La pipeline completa

Il riassunto di tutto il blocco sul training degli LLM, in una tabella:

| stadio | dati | obiettivo |
| --- | --- | --- |
| pretraining | trilioni di token | token successivo |
| SFT | istruzioni e risposte | token successivo, solo sulla risposta |
| preferenze | risposta scelta e scartata | reward model e PPO, oppure DPO |
| RLVR | problemi verificabili | reward 1 o 0, per esempio GRPO |

Due frasi da ricordare: **il pretraining dà la conoscenza, il post-training plasma il comportamento**; e **ogni stadio parte dal modello dello stadio precedente** (il riferimento della penalità KL è sempre il modello che si riceve). Notare il passaggio di tipo di segnale: dall'imitazione (i primi due stadi, la risposta è data) al reward (gli ultimi due, il modello genera e viene giudicato).

<a id="p-49"></a>

### Slide 49 · Riepilogo e prossima lezione

Il riepilogo in sei punti:

- **preference data**: un prompt, una risposta scelta e una scartata, da persone, voti o LLM;
- **Bradley-Terry**: $P = \sigma(z_i - z_j)$; un reward model addestrato con $-\log\sigma(r_w - r_l)$;
- **RLHF**: massimizzare il reward atteso con una penalità KL; advantage $r - b$; PPO con quattro modelli;
- **DPO**: le stesse preferenze, una loss supervisionata, due modelli;
- **RLVR**: reward da risposte controllabili; chain of thought; gruppi di risposte (GRPO);
- l'**alignment** è sottospecificato; sycophancy, allucinazioni e altri danni restano.

**Prossima lezione** (martedì 27 ottobre, con Andrea Ceni): *From pretraining to a chatbot*, un riepilogo con demo dei capitoli 7 e 8.

## Notebook

Commento al notebook del corso `HLT-L19-post-training-preferences.ipynb` (il notebook è del docente e non è incluso).

Notebook di accompagnamento (solo `numpy`, pochi secondi, nessuna figura): al posto di un language model la policy è una distribuzione su poche risposte candidate (una softmax su un logit per risposta), così tutto si legge per intero. Rifà i numeri delle slide, impara i punteggi di Bradley-Terry da confronti simulati, addestra un reward model lineare con annotatori che amano le risposte lunghe, addestra una policy con REINFORCE + baseline + KL e con DPO mostrando il **reward hacking**, simula GRPO con reward verificabili e ricalcola gli esercizi 1-4 e 6-11 della scheda. Rieseguito da capo: tutti gli output coincidono con quelli salvati, **nessun bug**. Unica svista di forma: la scheda esercizi lo chiama `HLT-L19-post-training-preferences-light.ipynb`, il file distribuito non ha il suffisso `-light`.

### Notebook 1 · I numeri della lezione

```python
sig = lambda z: 1 / (1 + np.exp(-z))
print({dz: round(float(sig(dz)), 2) for dz in (-1, 0, 1, 3)})
for rw, rl in [(2.0, 1.0), (1.0, 1.0), (0.5, 2.5)]:
    dz = rw - rl   # loss -ln sig(dz), push 1 - sig(dz)
r_toy = np.array([3.0, 2.0, 1.0, 0.0])
p_before = np.array([0.20, 0.30, 0.30, 0.20]); p_after = np.array([0.55, 0.30, 0.10, 0.05])
b = p_before @ r_toy   # the baseline
```

Output:

```text
Bradley-Terry: {-1: 0.27, 0: 0.5, 1: 0.73, 3: 0.95}
  (2.0, 1.0)  difference  1.0  P 0.73  loss 0.31  push 1 - sigma 0.27
  (1.0, 1.0)  difference  0.0  P 0.50  loss 0.69  push 1 - sigma 0.50
  (0.5, 2.5)  difference -2.0  P 0.12  loss 2.13  push 1 - sigma 0.88
  mean loss 1.04
expected reward: before 1.50, after 2.35
  clear steps            r = 3.0   r - b = +1.5   up
  ...
  wrong time             r = 0.0   r - b = -1.5   down
```

Ricalcola le schede [14](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-14) (punti della sigmoide), [18](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-18) (loss del reward model e spinta $1-\sigma$), [25](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-25)-[26](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-26) (reward atteso 1,5 e 2,35) e [30](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-30) (advantage con $b = 1{,}5$). Tutti i numeri coincidono con le slide.

### Notebook 2 · Imparare i punteggi dai confronti

```python
true_z = np.array([2.0, 1.2, 0.5, 0.0, -0.8, -1.5])
# 3000 confronti: il primo vince con prob. sig(z_i - z_j)
z = np.zeros(6)
for it in range(500):
    s = sig(z[W] - z[L]); g = np.zeros(6)
    np.add.at(g, W, -(1 - s)); np.add.at(g, L, (1 - s))
    z -= 0.5 * g / len(pairs)
```

Output:

```text
true scores, centered:    [ 1.77  0.97  0.27 -0.23 -1.03 -1.73]
learned scores, centered: [ 1.73  1.04  0.3  -0.28 -1.12 -1.67]
mean loss 0.455
```

Simula il modello di Bradley-Terry: sei risposte con punteggi nascosti, 3000 confronti fra coppie a caso in cui vince la prima con probabilità $\sigma(z_i - z_j)$. Poi dimentica i punteggi e li reimpara **solo dai confronti**, minimizzando $-\log\sigma(z_w - z_l)$: il gradiente è esattamente quello della [scheda 18](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-18), $-(1-\sigma)$ sul vincitore e $+(1-\sigma)$ sul perdente (`np.add.at` accumula i contributi delle coppie in cui una risposta compare più volte).

I punteggi appresi sono vicini a quelli veri **a meno di una costante**: per questo si confrontano dopo aver tolto la media (esercizio 2b). La loss media resta 0,455 e non va a 0: i confronti sono rumorosi per costruzione.

### Notebook 3 · Un reward model con il length bias

```python
U_TRUE = np.array([2.0, 0.5, -0.1])     # correct, polite, length: what we want
BIAS = np.array([0.0, 0.0, 0.6])        # what the annotators also like
a_wins = r.random(4000) < sig((A_ - B_) @ (U_TRUE + BIAS))
w = np.zeros(3)
for it in range(2000):
    dz = (Fw[tr] - Fl[tr]) @ w
    w -= 0.5 * (-(1 - sig(dz))[:, None] * (Fw[tr] - Fl[tr])).mean(0)
```

Output:

```text
reward model weights (correct, polite, length): [1.97 0.58 0.5 ]
the annotators' preferences use:                [2.  0.5 0.5]
held-out pairs ranked as the annotators did: 78%
held-out pairs where the annotators' winner is also better for the true utility: 63%
```

Un reward model **lineare** su tre feature (corretta, cortese, lunghezza in centinaia di parole), come nell'esercizio 4. L'utilità vera vuole risposte corrette e cortesi e penalizza appena la lunghezza ($-0{,}1$); gli annotatori simulati però aggiungono $+0{,}6$ per la lunghezza: la loro preferenza effettiva ha peso $+0{,}5$ sulla lunghezza.

Il reward model impara **ciò che gli annotatori preferivano**, length bias compreso: peso 0,5 sulla lunghezza invece di $-0{,}1$. Ordina come gli annotatori il 78% delle coppie di test (le preferenze sono rumorose), ma il vincitore scelto dagli annotatori è davvero migliore per l'utilità vera solo nel 63% dei casi. È il senso di *surrogato* della [scheda 24](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-24): il reward model riproduce bene i giudizi, e quindi anche i loro difetti.

### Notebook 4 · Addestrare una policy con i reward: reward hacking

```python
def train(beta, steps=3000, lr=0.05, n=16, seed=0):
    th = ref_logits.copy()
    for _ in range(steps):
        pi = softmax(th)
        o = rr.choice(6, n, p=pi)                          # sample from the policy
        rew = r_model[o] - beta * ln(pi[o] / pi_ref[o])    # reward minus KL penalty
        adv = rew - rew.mean()                             # baseline: the average
        g = sum(a * (onehot(oi) - pi) for oi, a in zip(o, adv))
        th += lr * g / n
```

Output:

```text
response                  pi_ref  reward model  true utility
correct polite short       0.262          3.06          2.40
correct curt               0.215          2.22          1.95
correct polite long        0.130          4.06          2.20
wrong polite very long     0.058          5.11         -0.40
wrong curt                 0.159          0.15         -0.03
wrong polite short         0.176          1.09          0.40

reference              E[reward model]  2.32   E[true]  1.38   KL  0.00   most likely: correct polite short (0.26)
trained, beta = 3.0    E[reward model]  2.98   E[true]  1.53   KL  0.11   most likely: correct polite short (0.30)
trained, beta = 1.0    E[reward model]  4.00   E[true]  1.19   KL  0.76   most likely: wrong polite very long (0.38)
trained, beta = 0.05   E[reward model]  5.10   E[true] -0.39   KL  2.80   most likely: wrong polite very long (1.00)
```

Il cuore del notebook. Sei risposte candidate a un prompt; il reward model della sezione precedente dà il reward più alto (5,11) alla risposta **sbagliata ma molto lunga**, che per l'utilità vera vale $-0{,}40$. Il ciclo di training è quello delle [schede 29-30](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-29): 16 campioni dalla policy, reward meno penalità KL per campione ($r - \beta\log\pi/\pi_{\mathrm{ref}}$), advantage come differenza dalla media dei 16, passo $a\,(\text{onehot}(o) - \pi)$, che è il gradiente di $\log\pi(o)$ rispetto ai logit di una softmax ([come nella L7](L07-regressione-logistica-multinomiale-e-valutazione.md#p-20)).

- $\beta = 3$: la policy resta vicina a $\pi_{\mathrm{ref}}$ (KL 0,11), reward e utilità vera salgono un poco (1,38 a 1,53);
- $\beta = 1$: il reward sale a 4,00 ma l'utilità vera scende sotto il punto di partenza (1,19), e la risposta lunga sbagliata è già la più probabile;
- $\beta = 0{,}05$: KL 2,80, la policy dà sempre la risposta lunga sbagliata, reward 5,10, utilità vera $-0{,}39$.

È il **reward hacking**: ottimizzare troppo un surrogato peggiora la qualità vera. La penalità KL limita il danno, ma non corregge un reward model distorto.

> **Approfondimento: Due semplificazioni del codice**
>
> La penalità KL entra come parte del reward di ogni campione e il suo gradiente diretto rispetto a $\theta$ non viene calcolato: è la scelta usuale nelle implementazioni RLHF, coerente con la [scheda 29](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-29) (*with the KL penalty* dentro il reward). La baseline è la media dei 16 campioni dello stesso passo, cioè l'idea di GRPO senza la divisione per la std, non un value model come in PPO.

### Notebook 5 · DPO sulle stesse preferenze

```python
def dpo(beta, steps=2000, lr=0.5):
    th = ref_logits.copy()
    for _ in range(steps):
        logpi = th - np.log(np.exp(th).sum())
        h = beta * ((logpi[PW] - ln(pi_ref[PW])) - (logpi[PL] - ln(pi_ref[PL])))
        coef = -(1 - sig(h)) * beta
        g_logpi = np.zeros(6); np.add.at(g_logpi, PW, coef); np.add.at(g_logpi, PL, -coef)
        g = g_logpi - np.exp(logpi) * g_logpi.sum()     # through the softmax
        th -= lr * g / len(PW)
```

Output:

```text
DPO, beta = 1.0        E[reward model]  4.14   E[true]  0.99   KL  0.92   most likely: wrong polite very long (0.45)
DPO, beta = 0.3        E[reward model]  5.05   E[true] -0.26   KL  2.58   most likely: wrong polite very long (0.95)
```

La loss della [scheda 35](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-35) minimizzata con la discesa del gradiente sui logit, su 2000 coppie giudicate dagli stessi annotatori (con il gusto per la lunghezza). Il gradiente è scritto a mano in due passi: derivata della loss rispetto a $\log\pi(o_w)$ ($-\beta(1-\sigma(h))$) e a $\log\pi(o_l)$ (il contrario), poi attraverso la log-softmax ($g_j - \pi_j\sum_k g_k$). Verificato: è corretto. Solo due modelli: policy e riferimento.

Risultato: DPO si muove nella stessa direzione dell'RL, **senza reward model e senza campionare**, e con $\beta$ piccolo arriva allo stesso esito: la risposta lunga sbagliata diventa la più probabile (0,95 con $\beta = 0{,}3$). Togliere il reward model non toglie il problema: il bias sta **nei dati di preferenza**. I valori di $\beta$ qui sono giocattolo, più grandi di quelli reali (0,01-0,1).

### Notebook 6 · GRPO con reward verificabili

```python
STRAT = ["a + b", "a + b + 1", "a + b - 1", "a * b"]
G, lr = 8, 0.05
for step in range(1, 401):
    pi = probs(th); s_ = rr.choice(4, G, p=pi)              # a group of G answers
    reward = (answers(a, b)[s_] == a + b).astype(float)     # verifiable
    if reward.std() > 0:
        adv = (reward - reward.mean()) / reward.std()
        th += lr * sum(av * (onehot(si) - pi) for si, av in zip(s_, adv)) / G
```

Output:

```text
start: {'a + b': 0.192, 'a + b + 1': 0.287, 'a + b - 1': 0.287, 'a * b': 0.235}
step  50  P(a + b) = 0.487   groups without signal in the last 50: 2
step 100  P(a + b) = 0.790   groups without signal in the last 50: 4
step 200  P(a + b) = 0.942   groups without signal in the last 50: 27
step 400  P(a + b) = 0.978   groups without signal in the last 50: 45
```

Una policy che risponde ad addizioni $a+b$ con una di quattro strategie (giusta, oppure tre errori tipici: $+1$, $-1$, prodotto). Reward verificabile: 1 se il risultato è $a+b$. Per ogni domanda un gruppo di $G = 8$ risposte, advantage $(r - \text{media})/\text{std}$ come nella [scheda 42](L19-post-training-ii-preferenze-rlhf-dpo-e-rl-per-il-ragionamento.md#p-42); nessun reward model, nessun value model, e per brevità nessuna penalità KL.

La probabilità della strategia giusta sale da 0,19 a 0,98. L'ultima colonna è la lezione dell'esercizio 10c: all'inizio quasi ogni gruppo mescola risposte giuste e sbagliate e dà segnale; alla fine quasi ogni gruppo è tutto giusto, std = 0, tutti gli advantage nulli (45 gruppi su 50 senza segnale). Il codice salta esplicitamente quei gruppi invece di aggiungere la costante alla std: stesso effetto. Le domande utili sono quelle che il modello **a volte** sbaglia.

### Notebook 7 · Verifica della scheda esercizi e proposte

```python
print("3  ", np.round(L3, 3), "mean", round(np.mean(L3), 3), "1 - sigma", ...)
h9 = 0.5 * ((-7 - -8) - (-10 - -9))
print("9  ", h9, round(-ln(sig(h9)), 3), round(ln(2), 3), ...)
g10 = np.array([1, 1, 0, 0, 0, 1], float)
print("10 ", g10.mean(), g10.std(), ((g10 - g10.mean()) / g10.std()).round(3))
```

Output:

```text
1   10 [('A', 'C'), ('B', 'C'), ('C', 'D'), ('C', 'E')] 6 36 4 ; votes: 5
2   0.818 0.818 0.953 0.182 ; +10: 0.818 ; ln(0.8 / 0.2) = 1.386
3   [0.127 0.974 0.693] mean 0.598 1 - sigma [0.119 0.622 0.5  ]
4   2.26 0.42 1.84 0.863 0.147 grad [-0.    -0.137 -0.11 ] new w [ 0.5    2.069 -0.145]
6   before 0.9 after 1.3 change [-0.2 -0.1  0.3]
7   1.386 0.277 0.523 ; unchanged: 0.0
8   b 2.0 advantages [ 2.  1. -1. -2.]
9   1.0 0.313 0.693 ; both +1: argument 0.0 loss 0.693
10  0.5 0.5 [ 1.  1. -1. -1. -1.  1.] ; all correct: std 0.0
11  1 0 ; apples: 7
```

I numeri delle soluzioni degli esercizi 1-4 e 6-11 (il 5 chiede solo spiegazioni): coincidono con quelli ricalcolati indipendentemente per la sezione Studio. Notare `g10.std()`: numpy usa di default la std di popolazione (divisione per $G$), la stessa definizione della scheda. La funzione `reward_11` è la soluzione dell'esercizio 11a: dà 1 se la risposta contiene una delle tre frasi esatte, anche se il contenuto fosse falso.

Le proposte finali, da provare: togliere il bias degli annotatori (`BIAS = 0`) e vedere sparire il reward hacking; più valori di $\beta$; togliere la baseline (`adv = rew`): il training funziona ancora ma è più rumoroso; cambiare $G$ e la difficoltà nella sezione GRPO.

## Studio ed esercizi

### Guida allo studio (circa 3 h 20 min)

**Dati di preferenza e Bradley-Terry** (30 min)

Schede 6-16. Saper dire perché dopo l'SFT servono le preferenze, che cos'è una tripla (prompt, scelta, scartata), contare le coppie da una classifica ($N(N-1)/2$) e da una scelta ($N-1$), le tre fonti. Scrivere Bradley-Terry e ricavarlo dal log-odds; la loss del reward model come binary cross-entropy. Libro §8.3 (pp. 215-219), §1.6.3. Esercizi 1, 2, 3.

**Reward model e il suo gradiente** (25 min)

Schede 17-20. Rifare a mano la tabella della scheda 18 (loss 1,04, spinte 0,27; 0,50; 0,88) e il passo di gradiente dell'esercizio 4; il reward model come LLM con la testa sostituita; best-of-$N$. Esercizi 4, 5.

**RLHF: obiettivo, KL, policy gradient, PPO** (45 min)

Schede 23-33: la parte più densa. Le corrispondenze stato/azione/policy/reward per un LLM; il reward atteso sul giocattolo (1,5 e 2,35); l'obiettivo con la KL e il ruolo di $\beta$; REINFORCE come SFT pesato dal reward; baseline e advantage; i tre passi di InstructGPT; i quattro modelli di PPO. Libro §8.4 (pp. 219-221). Esercizi 6, 7, 8, 15.

**DPO** (30 min)

Schede 35-36. Scrivere la loss di DPO e saperla leggere come la loss del reward model con reward implicito $\beta\log\pi_\theta/\pi_{\mathrm{ref}}$; l'idea della derivazione ($Z(x)$ che si cancella); calcolarla a mano; DPO contro PPO. Libro pp. 222-223. Esercizi 9, 13.

**RL per il ragionamento e safety** (35 min)

Schede 38-48. Chain-of-thought prompting e test-time compute; dati e vincoli verificabili; RLVR; GRPO con il calcolo degli advantage e il caso del gruppo senza segnale. Poi alignment, sycophancy, mitigazioni, limiti, la tabella della pipeline. Libro §1.6.4, §1.7 (pp. 20-23), §1.10 (pp. 29-31). Esercizi 10, 11, 16.

**Notebook e ripasso orale** (35 min)

Eseguire il notebook e rifare le proposte della sezione 8, soprattutto `BIAS = 0` e i valori di $\beta$: sono il modo più rapido di capire reward hacking e KL. Poi le domande d'orale, ad alta voce. Esercizio 14 sul win rate.

### Esercizi

#### Esercizio 1 (scheda L19): da classifiche a coppie

1. Un annotatore ordina cinque output: $A \succ B \succ C \succ D \succ E$. Quante coppie di preferenza dà la classifica? Elenca quelle che contengono $C$.
2. Gli annotatori di InstructGPT ordinavano da 4 a 9 output per prompt. Quante coppie dà ogni classifica, come minimo e come massimo? E un annotatore che sceglie solo il migliore di 5?
3. Su StackExchange quattro risposte hanno 40, 12, 12 e 3 voti. Quante coppie si possono estrarre, scartando quelle a pari voti?

<details><summary>Soluzione</summary>

(a) $\binom52 = 10$ coppie. Con $C$: $A\succ C$, $B\succ C$, $C\succ D$, $C\succ E$.

(b) Minimo $\binom42 = 6$, massimo $\binom92 = 36$. Solo il migliore di 5: $5 - 1 = 4$ coppie (il migliore batte ciascuno degli altri; nulla sull'ordine fra gli altri).

(c) Le coppie possibili sono $\binom42 = 6$; quella fra le due risposte da 12 voti si scarta: 5 coppie ($40\succ12$ due volte, $40\succ3$, $12\succ3$ due volte).

</details>

#### Esercizio 2 (scheda L19): il modello di Bradley-Terry

Tre output con punteggi $z_a = 2{,}0$, $z_b = 0{,}5$, $z_c = -1{,}0$. Usa $\sigma(1{,}5) = 0{,}818$ e $\sigma(3) = 0{,}953$.

1. Calcola $P(a\succ b\mid x)$, $P(b\succ c\mid x)$, $P(a\succ c\mid x)$. Quanto vale $P(b\succ a\mid x)$?
2. Aggiungi 10 a tutti i punteggi. Cambiano le probabilità? Che cosa significa per i punteggi che impara un reward model?
3. Nei dati $a$ è preferito a $b$ nell'80% dei confronti. La differenza che dà probabilità $p$ è $\ln(p/(1-p))$. Quale $z_a - z_b$ dà l'80%?

<details><summary>Soluzione</summary>

(a) $P(a\succ b) = \sigma(1{,}5) = 0{,}818$; $P(b\succ c) = \sigma(1{,}5) = 0{,}818$; $P(a\succ c) = \sigma(3) = 0{,}953$. $P(b\succ a) = \sigma(-1{,}5) = 1 - 0{,}818 = 0{,}182$.

(b) No: le differenze non cambiano ($12 - 10{,}5 = 1{,}5$), quindi nemmeno le probabilità. I reward sono definiti **a meno di una costante additiva** (per ogni prompt): solo le differenze hanno significato, e il valore assoluto di un reward non vuol dire nulla.

(c) $\ln(0{,}8/0{,}2) = \ln 4 = 1{,}386$. Verifica: $\sigma(1{,}386) = 0{,}8$.

</details>

#### Esercizio 3 (scheda L19): la loss del reward model

Reward (vincitore, perdente) di tre coppie: (3,0; 1,0), (0,0; 0,5), (1,5; 1,5). Usa $\sigma(2) = 0{,}881$, $\sigma(-0{,}5) = 0{,}378$, $\sigma(0) = 0{,}5$.

1. Calcola la loss $-\ln\sigma(r_w - r_l)$ di ogni coppia e la media.
2. La derivata della loss rispetto alla differenza ha modulo $1-\sigma$. Calcolala per ogni coppia: quale cambia di più i reward?
3. La loss di una coppia può essere 0? Che cosa dovrebbe fare il reward model?

<details><summary>Soluzione</summary>

(a) Differenze 2; $-0{,}5$; 0. Loss: $-\ln0{,}881 = 0{,}127$; $-\ln0{,}378 = 0{,}974$; $-\ln0{,}5 = 0{,}693$. Media $(0{,}127+0{,}974+0{,}693)/3 = 0{,}598$.

(b) $1-\sigma$: 0,119; 0,622; 0,5. La coppia 2, l'unica ordinata al contrario ($r_w &lt; r_l$), riceve la spinta più forte; la coppia 1, già ben ordinata, quasi nessuna.

(c) No, solo al limite: $-\ln\sigma(\Delta)\to0$ per $\Delta\to+\infty$. Il reward model dovrebbe dare al vincitore un reward infinitamente più grande del perdente; la loss si avvicina a 0 allargando il margine, ma non lo raggiunge mai (come la regressione logistica su dati separabili).

</details>

#### Esercizio 4 (scheda L19): un reward model lineare a mano

$r(x,o) = w\cdot\varphi(o)$ con feature (cortese, corretta, lunghezza in centinaia di parole) e $w = [0{,}5;\ 2{,}0;\ -0{,}2]$. $A$ ha $\varphi = [1, 1, 1{,}2]$, $B$ ha $\varphi = [1, 0, 0{,}4]$, e i dati dicono $A\succ B$.

1. Calcola $r(A)$, $r(B)$, la probabilità della preferenza e la loss ($\sigma(1{,}84) = 0{,}863$).
2. Il gradiente della loss rispetto a $w$ è $-(1-\sigma)(\varphi(A)-\varphi(B))$. Fai un passo di discesa con learning rate 0,5. Quali pesi cambiano, e perché il primo no?
3. Gli annotatori spesso preferiscono risposte più lunghe. Che cosa imparerebbe il reward model sul terzo peso, e che cosa potrebbe fare un modello addestrato a prendere reward alti?

<details><summary>Soluzione</summary>

(a) $r(A) = 0{,}5 + 2{,}0 - 0{,}24 = 2{,}26$; $r(B) = 0{,}5 + 0 - 0{,}08 = 0{,}42$. Differenza 1,84; $P(A\succ B) = 0{,}863$; loss $-\ln0{,}863 = 0{,}147$.

(b) $\varphi(A)-\varphi(B) = [0;\ 1;\ 0{,}8]$, $1-\sigma = 0{,}137$: gradiente $[0;\ -0{,}137;\ -0{,}110]$. Nuovo $w = w - 0{,}5\cdot\text{grad} = [0{,}5;\ 2{,}069;\ -0{,}145]$. Il primo peso non cambia perché entrambe le risposte sono cortesi: la feature non distingue la coppia, quindi non spiega la preferenza. Cresce il peso di *corretta*, e anche quello della lunghezza (da $-0{,}2$ a $-0{,}145$), perché qui la vincitrice è anche più lunga.

(c) Se le risposte preferite sono sistematicamente più lunghe, il terzo peso diventa **positivo**: il reward model premia la lunghezza in sé (**length bias**). Una policy ottimizzata contro di lui impara a scrivere risposte sempre più lunghe, anche a scapito della correttezza: reward hacking (notebook, sezioni 3-4).

</details>

#### Esercizio 5 (scheda L19): best-of-N, e che cosa premia il reward

1. Quattro risposte campionate hanno reward 0,2; 1,4; $-0{,}3$; 0,9. Quale restituisce best-of-$N$? Quanto costa rispetto a campionarne una?
2. Sharma et al. (2024): persone e preference model a volte preferiscono una risposta convincente che dà ragione all'utente a una corretta. L'utente scrive *I think the Moon is closer to the Sun than the Earth is, right?* Quale di due risposte, una che concorda e una che corregge, potrebbe avere un reward più alto?
3. Che cosa impara una policy ottimizzata a fondo contro questo reward model? Come si chiama il comportamento?

<details><summary>Soluzione</summary>

(a) La seconda (reward 1,4). Costa $N = 4$ generazioni più 4 valutazioni del reward model invece di una generazione: circa $N$ volte il calcolo all'inferenza, ma nessun training.

(b) Quella che **concorda** potrebbe avere reward più alto, perché il reward model ha imparato dalle preferenze umane che l'accordo con l'utente piace. Eppure l'utente sbaglia: la Luna orbita intorno alla Terra, quindi è a volte un po' più vicina al Sole (luna nuova) e a volte un po' più lontana (luna piena), e in media sta alla stessa distanza. La risposta corretta corregge l'utente.

(c) Impara a dare ragione all'utente anche quando sbaglia, cioè a scambiare la veridicità con l'accordo: **sycophancy**. È un caso di reward hacking: la policy sfrutta un difetto del surrogato.

</details>

#### Esercizio 6 (scheda L19): il reward atteso

Un prompt ha solo tre output possibili, con reward 1, 0 e 2. Prima del training la policy dà loro probabilità $[0{,}5;\ 0{,}3;\ 0{,}2]$, dopo $[0{,}3;\ 0{,}2;\ 0{,}5]$.

1. Calcola il reward atteso prima e dopo.
2. Quali output sono diventati più probabili e quali meno? I reward sono cambiati?
3. Con un vero LLM non si possono elencare tutti gli output. Come si stima il reward atteso?

<details><summary>Soluzione</summary>

(a) Prima: $0{,}5\cdot1 + 0{,}3\cdot0 + 0{,}2\cdot2 = 0{,}9$. Dopo: $0{,}3\cdot1 + 0{,}2\cdot0 + 0{,}5\cdot2 = 1{,}3$.

(b) Più probabile il terzo (reward 2, $+0{,}3$); meno probabili il primo ($-0{,}2$) e il secondo ($-0{,}1$). I reward non cambiano: il training sposta solo la probabilità.

(c) Campionando: si generano molte risposte dalla policy (per molti prompt), si valutano con il reward model e si fa la media (stima Monte Carlo).

</details>

#### Esercizio 7 (scheda L19): la penalità KL a mano

Il reward model dà a un output $r(x,o) = 0{,}8$. Il modello di riferimento gli dava probabilità 0,05, la policy in training 0,20; $\beta = 0{,}2$.

1. Calcola il log-rapporto $\ln(\pi_\theta/\pi_{\mathrm{ref}})$, la penalità $\beta$ per il log-rapporto e il reward meno la penalità.
2. Quanto vale la penalità se la policy dà ancora 0,05 all'output?
3. Che cosa può succedere con $\beta = 0$? E con $\beta$ molto grande?

<details><summary>Soluzione</summary>

(a) $\ln(0{,}20/0{,}05) = \ln4 = 1{,}386$; penalità $0{,}2\cdot1{,}386 = 0{,}277$; reward penalizzato $0{,}8 - 0{,}277 = 0{,}523$.

(b) $\ln1 = 0$: nessuna penalità.

(c) $\beta = 0$: nessun freno, la policy insegue solo il reward model, si allontana dal modello di partenza, dimentica capacità del pretraining e sfrutta i difetti del reward model (reward hacking; nel notebook con $\beta = 0{,}05$ la policy dà sempre la risposta lunga sbagliata). $\beta$ molto grande: la penalità domina, la policy resta praticamente uguale a $\pi_{\mathrm{ref}}$ e l'allineamento non ha effetto.

</details>

#### Esercizio 8 (scheda L19): la baseline

Una policy campiona un output e l'aggiornamento lo rende più probabile in proporzione a $r(x,o) - b$. Un prompt ha quattro output con reward 4, 3, 1, 0, ciascuno con probabilità 0,25.

1. Calcola la baseline $b$, il reward atteso della policy.
2. Calcola l'advantage $r - b$ di ogni output. Quali diventano più probabili quando vengono campionati, quali meno?
3. Senza baseline ($b = 0$), che cosa succede quando si campiona l'output con reward 1? Perché la baseline è utile?

<details><summary>Soluzione</summary>

(a) $b = 0{,}25\,(4+3+1+0) = 2$.

(b) Advantage $+2$, $+1$, $-1$, $-2$. I primi due diventano più probabili, gli altri due meno.

(c) Con $b = 0$ l'advantage è $+1$: l'output con reward 1, che è **sotto la media**, viene reso più probabile. Solo in media su molti campioni le spinte si compensano (quelli con reward alto spingono di più). La baseline fa andare ogni campione nel verso giusto: stessa direzione media, molta meno varianza, training più rapido e stabile.

</details>

#### Esercizio 9 (scheda L19): la loss di DPO

Una coppia con log-probabilità naturali: l'output scelto ha $\ln\pi_{\mathrm{ref}} = -8$ e $\ln\pi_\theta = -7$; lo scartato $\ln\pi_{\mathrm{ref}} = -9$ e $\ln\pi_\theta = -10$. $\beta = 0{,}5$ (giocattolo). Usa $\sigma(1) = 0{,}731$.

1. Calcola i due log-rapporti, l'argomento della sigmoide e la loss. Quanto vale la loss all'inizio, con $\pi_\theta = \pi_{\mathrm{ref}}$?
2. Quali modelli tiene in memoria DPO, e quale si addestra? E PPO?
3. Supponi invece che il training abbia alzato di 1 entrambe le log-probabilità rispetto al riferimento: $\ln\pi_\theta = -7$ per lo scelto e $-8$ per lo scartato. Quanto vale la loss? A che cosa è sensibile DPO?

<details><summary>Soluzione</summary>

(a) Log-rapporti: scelto $-7-(-8) = +1$, scartato $-10-(-9) = -1$. Argomento $0{,}5\,(1-(-1)) = 1$. Loss $-\ln0{,}731 = 0{,}313$. All'inizio entrambi i log-rapporti sono 0: loss $-\ln\sigma(0) = \ln2 = 0{,}693$.

(b) DPO: la policy $\pi_\theta$ (addestrata) e il riferimento $\pi_{\mathrm{ref}}$ (congelato). PPO: policy (addestrata), riferimento (congelato), reward model (congelato), value model (addestrato).

(c) Log-rapporti $+1$ e $+1$, argomento 0, loss 0,693, come all'inizio. DPO guarda solo il **margine** fra il log-rapporto dello scelto e quello dello scartato: alzare entrambi della stessa quantità non serve. Deve rendere lo scelto più probabile *rispetto* allo scartato, relativamente al riferimento.

</details>

#### Esercizio 10 (scheda L19): advantage di gruppo

La deviazione standard di un gruppo è $\mathrm{std} = \sqrt{\text{media di }(r-\text{media})^2}$ sulle $G$ risposte.

1. Un gruppo di 6 risposte a un problema di matematica riceve reward $[1,1,0,0,0,1]$. Calcola media, std e advantage $(r - \text{media})/\text{std}$.
2. La media del gruppo fa la parte della baseline $b$ dell'esercizio 8. Perché GRPO non ha bisogno di un value model?
3. Un altro gruppo riceve $[1,1,1,1,1,1]$. Che cosa succede, e che cosa suggerisce su quali domande sono utili per il training?

<details><summary>Soluzione</summary>

(a) Media 0,5. Scarti $\pm0{,}5$, quadrati 0,25, media 0,25, std 0,5. Advantage $[+1,+1,-1,-1,-1,+1]$.

(b) Il value model in PPO serve a stimare il reward atteso per quel prompt. GRPO lo stima direttamente con la media dei reward di più risposte allo stesso prompt: una stima Monte Carlo della baseline, senza un altro LLM da addestrare e tenere in memoria.

(c) Media 1, std 0: tutti gli advantage sono $0/0$, che con la costante aggiunta alla std diventano 0. Nessun aggiornamento: il gruppo non dà segnale. Lo stesso per un gruppo tutto sbagliato. Utili sono le domande che il modello **a volte** risolve e a volte no: né troppo facili né troppo difficili.

</details>

#### Esercizio 11 (scheda L19): reward verificabili e chain of thought

1. Scrivi, a parole o in Python, una funzione che dà il reward di RLVR per il prompt *Your answer must contain one of the following exact phrases: "My answer is yes.", "My answer is no.", "My answer is maybe."*
2. Per un problema di GSM8K il modello scrive una chain of thought e una risposta finale. Che cosa controlla il reward, e che cosa no?
3. Scrivi una dimostrazione chain-of-thought (domanda, passaggi, risposta) per *A box has 3 rows of 4 apples. 5 apples are eaten. How many are left?* Che cosa fa il modello con una nuova domanda dopo dimostrazioni di questo tipo nel prompt?

<details><summary>Soluzione</summary>

(a) `def reward(resp): return 1 if any(p in resp for p in ["My answer is yes.", "My answer is no.", "My answer is maybe."]) else 0`. Nota: dà 1 a qualunque delle tre, il contenuto non viene giudicato.

(b) Controlla solo che la **risposta finale** (il numero estratto) sia uguale a quella attesa. Non controlla i passaggi: una catena con errori che si compensano, o un'ipotesi fortunata, prende lo stesso reward; una catena giusta con un errore di trascrizione finale prende 0.

(c) *Q: A box has 3 rows of 4 apples. 5 apples are eaten. How many are left? A: The box has 3 × 4 = 12 apples. After 5 are eaten, 12 − 5 = 7 are left. The answer is 7.* Con dimostrazioni così, il modello imita il formato: scrive passi intermedi prima della risposta finale, spendendo più token (test-time compute), il che di solito migliora l'accuratezza sui problemi a più passi.

</details>

#### Esercizio 12 (proprio): KL e obiettivo sul giocattolo

Nel giocattolo delle schede 25-26 $\pi_{\mathrm{ref}} = [0{,}20;\ 0{,}30;\ 0{,}30;\ 0{,}20]$ e dopo il training $\pi_\theta = [0{,}55;\ 0{,}30;\ 0{,}10;\ 0{,}05]$, reward $[3, 2, 1, 0]$.

1. Calcola il log-rapporto $\ln(\pi_\theta/\pi_{\mathrm{ref}})$ di ogni output e la KL $D_{KL}(\pi_\theta\|\pi_{\mathrm{ref}})$.
2. Calcola l'obiettivo $\mathbb{E}[r] - \beta D_{KL}$ per $\beta = 0{,}5$, 1 e 2, e confrontalo con quello della policy di partenza.
3. Calcola anche $D_{KL}(\pi_{\mathrm{ref}}\|\pi_\theta)$: che cosa mostra?

<details><summary>Soluzione</summary>

(a) Log-rapporti: $\ln2{,}75 = 1{,}012$; $0$; $\ln(1/3) = -1{,}099$; $\ln0{,}25 = -1{,}386$. KL $= 0{,}55\cdot1{,}012 + 0 + 0{,}10\cdot(-1{,}099) + 0{,}05\cdot(-1{,}386) = 0{,}556 - 0{,}110 - 0{,}069 = 0{,}377$.

(b) $\mathbb{E}[r] = 2{,}35$. $\beta = 0{,}5$: $2{,}35 - 0{,}189 = 2{,}161$; $\beta = 1$: 1,973; $\beta = 2$: 1,596. La policy di partenza ha KL 0 e obiettivo 1,5: per tutti e tre i $\beta$ la nuova policy è migliore, ma il guadagno si riduce al crescere di $\beta$; con $\beta$ abbastanza grande ($\beta &gt; 0{,}85/0{,}377 \approx 2{,}25$) converrebbe restare dove si era.

(c) $D_{KL}(\pi_{\mathrm{ref}}\|\pi_\theta) = 0{,}405 \ne 0{,}377$: la KL non è simmetrica (scheda 28).

</details>

#### Esercizio 13 (proprio): DPO, beta e probabilità assolute

Una coppia in cui l'output scelto è *meno* probabile dello scartato: scelto $\ln\pi_{\mathrm{ref}} = -12$, $\ln\pi_\theta = -11{,}5$; scartato $\ln\pi_{\mathrm{ref}} = -10$, $\ln\pi_\theta = -10{,}5$.

1. Calcola i log-rapporti e i reward impliciti $\beta\log\pi_\theta/\pi_{\mathrm{ref}}$ con $\beta = 0{,}1$.
2. Calcola la loss DPO per $\beta = 0{,}1$, 0,5 e 1.
3. La policy ha già fatto bene il suo lavoro su questa coppia, anche se lo scelto resta meno probabile dello scartato? Perché?

<details><summary>Soluzione</summary>

(a) Scelto $-11{,}5-(-12) = +0{,}5$, scartato $-10{,}5-(-10) = -0{,}5$. Reward impliciti con $\beta = 0{,}1$: $+0{,}05$ e $-0{,}05$.

(b) Argomento $\beta\cdot1$: $\beta = 0{,}1$: $-\ln\sigma(0{,}1) = 0{,}644$; $\beta = 0{,}5$: 0,474; $\beta = 1$: 0,313. Tutte sotto $\ln2 = 0{,}693$.

(c) Sì, nel senso di DPO: la loss dipende dai log-rapporti con il riferimento, non dalle probabilità assolute. Lo scelto è diventato 1,65 volte più probabile ($e^{0{,}5}$), lo scartato 1,65 volte meno: la policy si è mossa nel verso giusto. Che lo scelto resti meno probabile in assoluto (magari perché più lungo) non conta: per questo DPO non spinge a rendere le risposte preferite le più probabili in assoluto, ma più probabili di quanto lo fossero per $\pi_{\mathrm{ref}}$.

</details>

#### Esercizio 14 (proprio): win rate

Due modelli, A (allineato) e B (solo SFT), rispondono agli stessi 200 prompt; un giudice preferisce A 110 volte, B 50 volte, e dà 40 pareggi.

1. Calcola il win rate di A contando i pareggi come mezza vittoria, e quello calcolato sui soli confronti decisi.
2. Se si interpreta il win rate (con i pareggi) con Bradley-Terry, quale differenza di punteggio fra A e B corrisponde?
3. Il giudice è un LLM e le risposte di A sono in media il doppio più lunghe. Che cosa bisogna sospettare?

<details><summary>Soluzione</summary>

(a) $(110 + 40/2)/200 = 130/200 = 0{,}65$; sui soli confronti decisi $110/160 = 0{,}6875$.

(b) $\ln(0{,}65/0{,}35) = 0{,}619$: $\sigma(0{,}619) = 0{,}65$.

(c) Un **length bias** del giudice: parte della vittoria può venire dalla lunghezza e non dalla qualità. Si controlla con un win rate corretto per la lunghezza, o confrontando risposte di lunghezza simile, o con giudici umani su un campione.

</details>

#### Esercizio 15 (proprio): REINFORCE con e senza baseline

Il giocattolo della scheda 25 (probabilità $[0{,}2;\ 0{,}3;\ 0{,}3;\ 0{,}2]$, reward $[3, 2, 1, 0]$). Si campiona *not sure* (reward 1).

1. Di quanto viene pesato il passo $\nabla\log\pi(o)$ senza baseline, e con $b = 1{,}5$? In che verso va ciascuno?
2. Si campiona *wrong time* (reward 0). Che cosa succede senza baseline, e con la baseline?
3. Perché nella scheda 29 un reward 0 non dà nessun passo, mentre con la baseline sì?

<details><summary>Soluzione</summary>

(a) Senza baseline peso $+1$: *not sure* diventa più probabile, anche se è sotto la media. Con $b = 1{,}5$ peso $-0{,}5$: diventa meno probabile.

(b) Senza baseline peso 0: nessun passo, il campione viene sprecato. Con la baseline peso $-1{,}5$: la risposta sbagliata viene resa nettamente meno probabile.

(c) Senza baseline il passo è proporzionale al reward assoluto: 0 significa nessun segnale. Con la baseline conta il reward **relativo al previsto**: una risposta peggiore della media è un'informazione utile (va scoraggiata), e la baseline la sfrutta.

</details>

#### Esercizio 16 (proprio): GRPO con una sola risposta giusta

Gruppo di $G = 4$ risposte con reward $[1, 0, 0, 0]$, poi un gruppo con $[1, 1, 1, 0]$.

1. Calcola media, std e advantage nei due casi.
2. Confronta l'advantage della risposta giusta nel primo gruppo con quello della sbagliata nel secondo. Che cosa dice sui problemi difficili e facili?
3. Somma gli advantage di ogni gruppo: che cosa osservi?

<details><summary>Soluzione</summary>

(a) Primo gruppo: media 0,25, std $\sqrt{0{,}25\cdot0{,}75} = 0{,}433$; advantage $+1{,}732$ per la giusta, $-0{,}577$ per le sbagliate. Secondo gruppo: media 0,75, std 0,433; $+0{,}577$ per le giuste, $-1{,}732$ per la sbagliata.

(b) Nel problema difficile (una sola giusta) la risposta giusta, rara, riceve una spinta forte verso l'alto; nel problema facile è la risposta sbagliata, rara, a ricevere una spinta forte verso il basso. La normalizzazione per la std mette i due problemi sulla stessa scala.

(c) Somma 0 in entrambi: $1{,}732 - 3\cdot0{,}577 = 0$. Con la media come baseline gli advantage di un gruppo sommano sempre a 0: si sposta probabilità dentro il gruppo, da sotto la media a sopra la media.

</details>

### Domande tipo orale

<details><summary>Perché dopo l'instruction tuning serve un altro stadio? Che cosa hanno di diverso le preferenze?</summary>

Traccia: (1) un modello SFT può ancora dare risposte dannose o sbagliate, o corrette ma poco utili; (2) l'SFT impara solo da esempi positivi, non riceve mai il segnale di che cosa non dire; (3) le preferenze sono confronti, meglio o peggio, non giusto o sbagliato: non richiedono competenza per essere date, quindi si raccolgono facilmente; (4) ogni coppia contiene anche una risposta scartata; (5) obiettivo: più helpful, honest, harmless; (6) la scelta deve essere solo migliore, non buona (esempio del ketchup).

</details>

<details><summary>Come si ottengono coppie di preferenza e da quali fonti?</summary>

Traccia: (1) tripla prompt, scelto, scartato, $o_w \succ o_l \mid x$; (2) confronti diretti; classifica di $N$ output, $N(N-1)/2$ coppie (InstructGPT 4-9 output, da 6 a 36 coppie); scelta del migliore, $N-1$ coppie; (3) fonti: annotatori addestrati (InstructGPT, prompt di utenti reali), voti online (Reddit, StackExchange: post come prompt, risposte ordinate dai voti), LLM come giudici (UltraFeedback con GPT-4); (4) costo e rumore diversi; (5) anche punteggi per aspetti.

</details>

<details><summary>Scrivi il modello di Bradley-Terry e spiega da dove viene.</summary>

Traccia: (1) ogni output ha un punteggio nascosto $z$; (2) $P(o_i\succ o_j\mid x) = \sigma(z_i - z_j)$; (3) la differenza è il log-odds della preferenza: $\delta = \log\frac{P}{1-P}$, da cui $P = 1/(1+e^{-\delta})$, come nella regressione logistica; (4) differenza piccola, probabilità vicina a 0,5; grande, vicina a 0 o 1; (5) $P(o_j\succ o_i) = 1 - P(o_i\succ o_j)$; (6) invarianza per traslazione: i punteggi sono definiti a meno di una costante.

</details>

<details><summary>Come si addestra un reward model? Scrivi la loss e il suo gradiente.</summary>

Traccia: (1) si impara $r(x,o)$ al posto di $z$; (2) loss di una coppia $-\log\sigma(r(x,o_w) - r(x,o_l))$, media sul dataset: binary cross-entropy con target 1, massima verosimiglianza delle preferenze; (3) derivata rispetto alla differenza: $-(1-\sigma)$, alza $r_w$ e abbassa $r_l$; (4) le coppie ordinate male pesano di più (esempio della slide: 0,88 contro 0,27); (5) in pratica un LLM preaddestrato con la LM head sostituita da uno strato lineare a un'uscita (Ziegler 2019); (6) usi: best-of-$N$, selezione dati, alignment.

</details>

<details><summary>Come si mappa il reinforcement learning su un LLM?</summary>

Traccia: (1) RL: agente, policy, azioni, ambiente, reward, nessuno dà l'azione giusta; (2) per un LLM: azioni = token, stato = prompt più token generati, policy = l'LLM (distribuzione del token successivo), reward = reward model sull'intera risposta, alla fine; (3) $\pi(o\mid x)$ prodotto delle probabilità dei token; (4) differenze dal RL classico: reward appreso e rumoroso, non osservabile; si parte da un modello già buono da spingere, non da zero.

</details>

<details><summary>Scrivi l'obiettivo di RLHF con la penalità KL e spiega ogni termine.</summary>

Traccia: (1) $\max_{\pi_\theta}\mathbb{E}_{x\sim D,o\sim\pi_\theta}[r(x,o) - \beta\log\frac{\pi_\theta(o\mid x)}{\pi_{\mathrm{ref}}(o\mid x)}]$; (2) prompt dal dataset, output dalla policy stessa, reward dal reward model; (3) reward atteso: media dei reward pesata dalle probabilità (giocattolo: 1,5 poi 2,35), stimata campionando; (4) penalità: log-rapporto per output, in media la KL da $\pi_{\mathrm{ref}}$ (il modello SFT), non simmetrica; (5) senza penalità: oblio del pretraining e reward hacking; (6) $\beta$ ne regola il peso.

</details>

<details><summary>Che cos'è il policy gradient e perché si usa una baseline?</summary>

Traccia: (1) in SFT $\theta \leftarrow \theta + \eta\nabla\log\pi_\theta(o\mid x)$ con $o$ dal dataset; (2) in RL $o$ campionato da $\pi_\theta$ e il passo moltiplicato per $r(x,o)$: REINFORCE, SFT sui propri output pesato dal reward; (3) $\nabla\log\pi$ è la direzione, $r$ la lunghezza del passo; in media la direzione che alza il reward atteso (trucco del log); (4) con reward tutti positivi ogni campione viene alzato: gradiente rumoroso; (5) baseline $b$ = reward atteso, advantage $r - b$: sopra la media su, sotto giù, stessa direzione media, meno varianza; (6) in PPO $b$ dal value model, in GRPO media del gruppo.

</details>

<details><summary>Descrivi RLHF di InstructGPT e PPO.</summary>

Traccia: (1) tre passi: SFT su dimostrazioni scritte da persone; reward model da classifiche di 4-9 output; RL con PPO e penalità KL; (2) InstructGPT 1,3B preferito a GPT-3 175B; base delle prime versioni di ChatGPT; (3) PPO: quattro modelli, policy (addestrata), riferimento (congelato, per la KL), reward model (congelato), value model (addestrato, baseline); (4) aggiornamento in base all'advantage; (5) proximal: aggiornamenti piccoli, la policy cambia gradualmente; (6) costoso: quattro modelli e campionamento a ogni passo.

</details>

<details><summary>Scrivi la loss di DPO, spiegala e confrontala con PPO.</summary>

Traccia: (1) $-\log\sigma(\beta\log\frac{\pi_\theta(o_w)}{\pi_{\mathrm{ref}}(o_w)} - \beta\log\frac{\pi_\theta(o_l)}{\pi_{\mathrm{ref}}(o_l)})$; (2) è la loss del reward model con reward implicito $\beta\log\pi_\theta/\pi_{\mathrm{ref}}$; (3) derivazione: la soluzione dell'obiettivo con KL dà $r = \beta\log\pi^*/\pi_{\mathrm{ref}} + \beta\log Z(x)$, e in Bradley-Terry $Z$ si cancella; (4) $\beta$ tipicamente 0,01-0,1, stesso ruolo della KL; (5) all'inizio la loss vale $\ln2$; conta solo il margine fra i log-rapporti; (6) contro PPO: niente reward model, niente campionamento, due modelli; più semplice e stabile, ma offline e soggetto agli stessi bias dei dati.

</details>

<details><summary>Che cos'è il reward hacking? Fai esempi.</summary>

Traccia: (1) il reward model è un surrogato appreso delle preferenze, non ciò che vogliamo davvero; (2) ottimizzandolo troppo la policy trova risposte che lo ingannano: alto reward, bassa qualità vera; (3) esempi: length bias (risposte lunghe premiate in sé; notebook: con $\beta$ piccolo la risposta lunga sbagliata diventa certa), sycophancy (dare ragione all'utente); (4) rimedi parziali: penalità KL, reward verificabili, dati migliori; (5) la KL limita il danno ma non corregge un reward model distorto, e DPO eredita i bias dei dati.

</details>

<details><summary>Che cos'è il chain-of-thought prompting e che cosa c'entra con i reasoning model?</summary>

Traccia: (1) Wei et al. 2022: ogni dimostrazione include i passi di ragionamento, il modello imita e scrive passi prima della risposta; (2) esempio delle mele: 27 sbagliato senza passi, 9 corretto con $23-20=3$, $3+6=9$; (3) test-time compute: più calcolo all'inferenza sui problemi difficili; (4) i reasoning model sono addestrati con RLVR a scrivere la chain of thought da soli, anche se il reward guarda solo la risposta finale.

</details>

<details><summary>Che cos'è RLVR? Che cosa vuol dire verificabile?</summary>

Traccia: (1) domini dove una risposta si giudica in automatico: matematica (GSM8K fino al livello dottorato), codice con test; (2) vincoli verificabili (IFEval): parole chiave, formato JSON, lunghezza, lingua, risposte da un insieme fisso; si controllano i vincoli, non il contenuto; (3) reward 1 o 0 calcolato da un programma, nessun reward model; (4) stesso policy gradient di RLHF; (5) produce reasoning model con chain of thought; (6) limite: si premia solo ciò che si controlla.

</details>

<details><summary>Come funziona GRPO? Calcola gli advantage di un gruppo.</summary>

Traccia: (1) per una domanda si campiona un gruppo di $G$ risposte; (2) reward 1 o 0; (3) $A_i = (r_i - \mathrm{mean})/\mathrm{std}$, con una costante sulla std; (4) la media del gruppo è la baseline: niente value model; la std mette le domande sulla stessa scala; (5) aggiornamento con penalità KL; (6) esempio $[1,1,0,0,0,1]$: media 0,5, std 0,5, advantage $\pm1$; (7) gruppo tutto giusto o tutto sbagliato: nessun segnale; utili le domande a difficoltà intermedia.

</details>

<details><summary>Che cosa si intende per alignment e quali problemi restano aperti?</summary>

Traccia: (1) far evitare danni ai modelli, agendo secondo bisogni e valori umani; parte dell'AI safety; (2) sottospecificato: valori di chi? conflitti? (Kirk 2023); (3) sycophancy: le preferenze premiano l'accordo, non la verità (Sharma 2024); (4) mitigazioni: esempi di danni nei dati di post-training, constitutional AI, red teaming, value sensitive design; problema sociotecnico; (5) limiti: allucinazioni, overconfidence, calibrazione; il post-training li riduce, non li risolve.

</details>

<details><summary>Riassumi la pipeline completa di training di un LLM.</summary>

Traccia: (1) pretraining: trilioni di token, next token, dà la conoscenza; (2) SFT: istruzioni e risposte, next token solo sulla risposta; (3) preferenze: scelte e scartate, reward model + PPO oppure DPO; (4) RLVR: problemi verificabili, reward 0/1, GRPO; (5) ogni stadio parte dal modello precedente, che fa da riferimento per la KL; (6) passaggio dall'imitazione (risposta data) al reward (risposta generata e giudicata); il post-training plasma il comportamento.

</details>
