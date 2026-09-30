# GDL — esercizi di codice

Quindici esercizi in numpy puro, uno per blocco tematico del corso. Ogni esercizio è
uno scheletro da riempire, una suite di test che ti dice se l'hai riempito bene, e una
soluzione di riferimento **da guardare solo dopo**.

Non coprono tutte e 29 le lezioni, e non devono. Coprono i punti in cui scrivere il
codice cambia davvero quello che hai capito: dove la formula sulle slide sembra chiara
finché non devi decidere un asse, un segno o un ordine di aggiornamento. Su d-separazione,
EM, Viterbi, CAVI, MCMC, contrastive divergence, convoluzione, BPTT, gating, attention,
ELBO, discriminatore ottimo, cambio di variabile, message passing e Bellman ci sono
esercizi. Su LDA, causalità, structure learning, diffusion e causal representation
learning no: lì il ritorno di un'implementazione giocattolo è basso rispetto al tempo,
e per un orale conviene spenderlo sulla teoria.

## Prima di iniziare

Serve `numpy` e `pytest`. Il venv che usi per i midterm (`../midterms/.venv`) ha già
numpy 2.4.4 e torch, ma **non** pytest, quindi o lo aggiungi lì:

```bash
source ../midterms/.venv/bin/activate
pip install pytest
```

oppure te ne fai uno dedicato, che è più pulito visto che qui torch non serve:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Come si usa

Dalla cartella di un esercizio:

```bash
cd 03_hmm
python3 -m pytest test_hmm.py -v      # tutto rosso: devi ancora scrivere il codice
$EDITOR hmm.py                        # implementa le funzioni marcate # TODO
python3 -m pytest test_hmm.py -v      # verde = hai finito
```

I test sono il tuo parametro di autovalutazione: ogni fallimento ha un messaggio che
spiega *cosa* è sbagliato, non solo che qualcosa lo è. Almeno un test per esercizio è un
oracolo indipendente — lo stesso risultato calcolato per forza bruta o dalla definizione —
quindi non puoi passarlo per caso con un'implementazione che "sembra" giusta.

Solo quando sei verde (o quando sei bloccato da più di venti minuti su un singolo test),
apri `soluzione/`. Dentro c'è l'implementazione commentata e un `NOTE.md` con il
ragionamento, gli errori tipici e il collegamento alla slide.

Per controllare che la soluzione di riferimento sia effettivamente corretta:

```bash
GDL_SOL=1 python3 -m pytest test_hmm.py -q
```

Questo fa girare gli stessi test contro la soluzione invece che contro il tuo file.
Serve anche a distinguere "il mio codice è sbagliato" da "il test è sbagliato".

`./run_tests.sh` esegue tutto in sequenza; `./run_tests.sh --sol` lo fa sulle soluzioni.

## Mappa

| # | Cartella | Lezione | Argomento | Blocco nel piano | Tempo |
|---|---|---|---|---|---|
| 01 | `01_dseparation` | GDL3-4 | d-separazione, Bayes-Ball, Markov blanket, fattorizzazione | Parte I | 1.5-2h |
| 02 | `02_em_gmm_bic` | GDL8 | EM per GMM in spazio log, BIC e model selection | Parte II | 2-3h |
| 03 | `03_hmm` | GDL9-10 | forward-backward con scaling, Viterbi, Baum-Welch | Parte II | 2.5-4h |
| 04 | `04_variational_cavi` | GDL11 | ELBO, CAVI su mixture di gaussiane | Parte II | 1.5-2h |
| 05 | `05_sampling` | GDL13 | rejection, importance, Metropolis-Hastings, Gibbs | Parte II | 1.5h |
| 06 | `06_rbm_cd` | GDL14 | RBM, energia libera, contrastive divergence | 28/07 | 1.5h |
| 07 | `07_conv_forward` | GDL15-16 | im2col, conv2d, pooling, campo recettivo | 29/07 | 2h |
| 08 | `08_rnn_evgp` | GDL17 | RNN, BPTT, exploding/vanishing gradient | 30/07 | 2h |
| 09 | `09_lstm_gru_esn` | GDL18 | gate LSTM/GRU, constant error carousel, echo state | 31/07 | 1.5h |
| 10 | `10_attention` | GDL19-20 | attention additiva, scaled dot-product, multi-head | 01/08 | 2h |
| 11 | `11_vae_elbo` | GDL24 | ELBO, reparameterization vs score function | 04/08 | 1.5h |
| 12 | `12_gan_optimal_d` | GDL25 | D\*, `-log 4 + 2·JSD`, saturazione del gradiente | 05/08 | 1.5h |
| 13 | `13_flow` | GDL27-28 | coupling, log-det dello Jacobiano, cambio di variabile | 06/08 | 1.5h |
| 14 | `14_gnn` | GDL32-33 | message passing, GCN, GAT, oversmoothing | 10/08 | 2.5h |
| 15 | `15_rl` | GDL34 | value/policy iteration, Q-learning off-policy | 11/08 | 2-4h |

Totale onesto: **28-35 ore**. È tanto. Se il tempo stringe, questo è l'ordine di priorità
per un orale: 03, 02, 04, 11, 12 sono quelli che ti fanno rispondere meglio a domande di
derivazione; 01, 08, 14 sono quelli che scoprono più confusioni; 05, 06, 09, 13, 15 sono
consolidamento; 07 e 10 li hai già in parte fatti con i midterm.

Le date nella colonna "blocco" corrispondono ai task GDL nel progetto Todoist
*📚 Studio esami*, e la sezione *🎥 GDL — video per lezione* ha un video per ciascuna
di quelle lezioni. Esercizio, video e slot di studio parlano della stessa lezione.

## Cosa scopre ciascun esercizio

Non sono esercizi di sintassi. Ognuno è costruito attorno a una confusione precisa:

**01** — che la d-separazione non sia "seguire le frecce": il collider si comporta al
contrario, e condizionare su un suo discendente riapre il cammino.
**02** — che l'E-step vada fatto in spazio log e che la log-likelihood di EM debba
crescere monotonamente; se scende, hai un bug, non un caso sfortunato.
**03** — che `argmax` delle marginali non sia la sequenza di Viterbi. Il test contiene un
controesempio in cui il cammino ottenuto dalle marginali ha probabilità esattamente zero.
**04** — che l'ELBO sia un *lower bound*: verificato su 300 `q` casuali, con il gap che si
chiude solo all'ottimo.
**05** — che Gibbs sia Metropolis-Hastings con rapporto di accettazione esattamente 1.
**06** — che CD-1 sia uno stimatore *distorto* del gradiente: errore ≈0.55 contro ≈0.02
di CD-50, su un gradiente di norma ≈1.41.
**07** — equivarianza alla traslazione e campo recettivo misurati, non affermati.
**08** — che il gradiente decada come il raggio spettrale (0.4988 misurato contro 0.5
teorico) e che anche a ρ=1 esatto con `W_hh` ortogonale si perdano 4 ordini di grandezza
in 20 passi.
**09** — la echo state property vista come convergenza degli stati a ρ=0.9 contro
divergenza a ρ=1.5.
**10** — lo scaling per `sqrt(d_head)` e non `sqrt(d_model)`: differenza invisibile con
una sola testa.
**11** — che pathwise e REINFORCE stimino *lo stesso* gradiente e differiscano solo per
varianza (rapporto ~5800× a campioni appaiati), e che la KL dentro l'ELBO
(`q‖prior`) non sia quella che misura quanto il bound è lasco (`q‖posterior`).
**12** — che con D ottimo il generatore stia minimizzando `-log 4 + 2·JSD`, e che la
saturazione dipenda dal regime, non dalla loss: gradiente `1.4e-05` contro `1.6e+01` con
distribuzioni quasi disgiunte, rapporto 1.7 quando si sovrappongono.
**13** — che il log-det vada valutato sull'ingresso di *ogni* layer: sbagliando questo si
ottiene un flusso ancora perfettamente invertibile la cui densità però non integra a 1.
**14** — che l'oversmoothing sia un fatto spettrale e non un incidente di training:
energia di Dirichlet 2.21 → 0.110 → 1.7e-05 a 1, 5, 20 layer, con rapporto asintotico
pari a λ₂².
**15** — che `max_a` e `Σ_a π(a|s)` occupino lo stesso posto nella formula ma siano due
equazioni diverse: un `max` dentro `policy_evaluation` restituisce silenziosamente `V*`.
E che il target di Q-learning usi `max_{a'} Q(s',a')` e non la Q dell'azione eseguita —
con ε=0.9, Q-learning converge a `Q*` mentre SARSA si ferma a distanza 1.09.

## Vincoli

Solo `numpy` e stdlib. Niente torch, scipy, sklearn, matplotlib. Non è una limitazione
dell'ambiente: è il punto. Se `torch.nn.MultiheadAttention` fa il lavoro al posto tuo,
l'esercizio non serve a niente. Vale anche per il resto — niente `np.convolve`,
niente `scipy.stats`, niente `sklearn.mixture`.

Tutto è deterministico: `np.random.default_rng(seed)` con seed espliciti, mai
`np.random.seed`, mai `random`, mai `time`. Se un test passa una volta e fallisce la
successiva, è un bug tuo, non rumore.

## Nota sul vincolo dei midterm

Il testo del Midterm 3 vieta l'uso di codice generato da LLM. Questi esercizi sono
materiale di studio, non consegne: `02_em_gmm_bic` e `07_conv_forward` battono lo stesso
terreno dei midterm 1 e 2 (già consegnati) ma con API e struttura diverse, e non c'è
nessun esercizio sull'adversarial autoencoder del midterm 3. Se dovessi tornare su un
midterm, il codice va scritto di tua mano.

## Struttura

```
esercizi/
  _SPEC.md              contratto con cui sono stati scritti (utile se ne vuoi altri)
  run_tests.sh          esegue tutto
  requirements.txt      numpy, pytest
  NN_slug/
    README.md           la consegna
    slug.py             lo scheletro da riempire
    test_slug.py        la suite
    soluzione/
      slug_sol.py       la soluzione — apri dopo
      NOTE.md           ragionamento ed errori tipici
```

189 test in totale. Tutti verdi sulle soluzioni, tutti rossi sugli scheletri.
