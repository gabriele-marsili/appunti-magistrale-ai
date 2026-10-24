# L16 Lab: CNNs for Image Classification – note di lavoro (24/10/2026)

Materiale: un solo notebook, /tmp/cv/L16/cnn_image_classification.ipynb (29 celle, numerate da 1 con le markdown; l'ultima è vuota). Eseguito dal docente su Windows, CPU. Nessuna slide, data e docente non noti.
Lavoro in /tmp/cv/L16/work (script in work/scripts: run_nb.py esecuzione ridotta, exp.py mini esperimenti, check_model.py parametri/forme/campo recettivo, macs.py, plot_lr.py; uscite in work/out; figure originali estratte in work/orig/cNN_KK.png).

## Mappa celle -> schede
1–3 setup (s1) · 4–5 dataset (s2), augmentation (s3), Normalize (s4) · 6–8 visualizzazione (s5) · 9–10 DataLoader (s6) · 11–12 modello: intro/slim (s7), BasicBlock (s8), shortcut (s9), BatchNorm (s10, celle 12–13), BottleNeck (s11), ResNet/_make_layer (s12) · 13 stampa, forme, parametri, RF (s13) · 14–15 setup training (s14), ciclo (s15), uscite salvate (s16) · 16–17 valutazione (s17) · 18–20 ultimo batch (s18) · 21 visualize_pca (s19) · 22–23 hook (s20) · 24 PCA conv4_x (s21) · 25 e 27 griglie 8×8 (s22) · 26–27 conv1 (s23) · 28 esercizi (s24).

## Uscite salvate del docente
- Cella 6: (3, 32, 32), label 6 (frog). Cella 7: avviso Clipping, range [−2.4290657, 2.5574567] (identico nella nostra esecuzione). Cella 10: batch [100, 3, 32, 32].
- Cella 15: epoca 1 1563/1563 in 36:23 (1.40 s/it), "Loss: 1.1877" (ultimo batch, 16 immagini); epoca 2 interrotta a 261/1563 dopo 10:03 (2.31 s/it), KeyboardInterrupt. Modello valutato ≈ 1824 aggiornamenti.
- Cella 17: ACC 0.6323, 313 batch, 2:29.
- Cella 19: x [16, 3, 32, 32]; cella 20 clipping range [−2.0025976, 2.3590088]. Cella 23: [16, 256, 8, 8].
- Le 16 immagini (ultime del test, non mescolato): horse (cavallo con cavaliere), dog, ship, airplane, ship, bird, horse, airplane, cat, dog, cat, ship, cat, dog, automobile, horse.

## Bug e imprecisioni verificati eseguendo
1. Cella 7: `train_data[0][0].transpose(0,2)` -> (W, H, C): immagine trasposta sulla diagonale (verificato: uguale a permute(1,2,0).transpose(0,1)); in più tensore normalizzato -> clipping. Corretto: permute(1,2,0) + denormalizzazione. Cella 8 usa i dati grezzi uint8 HWC, per questo è giusta (frog, label 6). Cella 20 usa numpy transpose(1,2,0): assi giusti, colori falsati dalla normalizzazione. Nota: cella 7 chiama train_data[0] due volte -> due augmentation diverse.
2. Cella 15: `resnet18(num_classes=100)` su CIFAR-10 (cella 13 usa 10). Funziona (etichette < 100). Misurato con 300 batch: loss primo batch 4.35 (ln100 = 4.61), logit medio classi 0–9 = 6.83, classi 10–99 = −0.79, nessuna predizione ≥ 10; 46 170 parametri in più (11 220 132 vs 11 173 962).
3. Cella 5: Normalize std (0.2023, 0.1994, 0.2010) non è la std per canale del training (misurata 0.2470, 0.2435, 0.2616) ma la media delle std per immagine (misurata 0.2022, 0.1993, 0.2009). Media giusta (0.4914, 0.4822, 0.4465). Effetto: std degli ingressi ≈ 1.22, 1.22, 1.30. Innocuo in pratica (BN dopo la prima conv).
4. Celle 11 e 28: "slim ResNet18" / "our resnet18 is slightly different from theirs (slim version, less units)": FALSO. diff con https://raw.githubusercontent.com/weiaicunzai/pytorch-cifar100/master/models/resnet.py: BasicBlock, BottleNeck, ResNet identici (solo docstring/righe vuote); unica differenza resnet18(num_classes=100) con parametro. README del repo: resnet18 11.2M = 11 220 132 misurati. Rispetto a torchvision resnet18 (ImageNet) con 10 classi: 11 181 642 vs 11 173 962, differenza solo stem 7×7 (9408) vs 3×3 (1728). MACs su 32×32: 555.4 M (CIFAR) vs 37.0 M (stem ImageNet, arriva a 8×8 dopo lo stem e 1×1 a layer4).
Non bug ma da notare: DataLoader ricreato a ogni epoca (ok); nessun momentum/weight decay/scheduler (SGD defaults verificati: momentum 0, wd 0); loss in barra = singolo batch; no validation set; torch.max(pred.data, 1) legacy (-> argmax); model(x) per gli hook fuori da no_grad; grafici solo 64/256 canali con scala colore per riquadro; PCA per immagine (colori non confrontabili); nn.ReLU(inplace=True)(...) creato a ogni forward (funziona); BN momentum=0.1 nella stampa = tasso medie mobili.

## Numeri misurati (PyTorch 2.14.1+cpu, torchvision 0.29.1, 2 thread, seme 0)
- Forme: conv1 64×32×32, conv2_x 64×32×32, conv3_x 128×16×16, conv4_x 256×8×8, conv5_x 512×4×4, avg_pool 512×1×1.
- Parametri per stadio (10 classi): conv1 1 856; conv2_x 147 968; conv3_x 525 568; conv4_x 2 099 712; conv5_x 8 393 728; fc 5 130; totale 11 173 962. 20 Conv2d (17 + 3 shortcut 1×1), 20 BatchNorm2d. ResNet-50 CIFAR (BottleNeck [3,4,6,3], 100 classi) 23 705 252.
- Campo recettivo teorico (verificato col supporto del gradiente su input 224×224 casuale): 3, 11, 25, 53, 109.
- Esecuzione ridotta (num_classes=100 come notebook, lr 0.04, 300 batch da 32): 169.9 s; loss media primi 50 = 2.74, ultimi 50 = 1.72; acc test (10 000) = 0.4111; eval 47 s; 313 batch, ultimo 16.
- PCA 3 componenti, varianza spiegata media (6 immagini): conv1 0.687, conv2_x 0.606, conv3_x 0.541, conv4_x 0.556, conv5_x 0.574. Frazione di zeri dopo ReLU: 0.499, 0.342, 0.390, 0.379, 0.368.
- Mini esperimento lr (num_classes=10, aug sì, 300 batch, acc su prime 2000 immagini di test): lr 0.04: loss primi 25 = 2.64, ultimi 25 = 1.73, acc 0.322; lr 0.4: 5.71 -> 1.96, acc 0.2835; lr 4.0: 8.65 -> 2.16, acc 0.171; nessun NaN.
- Mini esperimento augmentation (num_classes=10, 5000 immagini di training casuali, 10 epoche = 1570 batch da 32, lr 0.04, acc in eval su 5000 train senza aug e prime 2000 test; ~19 min per run): con aug train 0.584, test 0.5515, loss 1.03; senza aug train 0.977, test 0.539, loss 0.099. Curve per epoca irregolari in eval (es. senza aug ep 5 train 0.277): BN running stats con lr fisso e senza momentum. Figure: img/es_aug.png, img/es_lr.png.

## Repository weiaicunzai/pytorch-cifar100 (letto 24/10)
train.py: SGD(lr=args.lr (default 0.1), momentum=0.9, weight_decay=5e-4), MultiStepLR(milestones=[60,120,160], gamma=0.2), WarmUpLR lineare per args.warm=1 epoca (lr = base_lr·m/total_iters), batch default 128, transform train RandomCrop(32,4) + flip + RandomRotation(15) + Normalize(CIFAR100 mean/std = (0.5071, 0.4865, 0.4409), (0.2673, 0.2564, 0.2762)). EPOCH 200. README: il testo dice "Nesterov momentum 0.9" ma train.py non attiva nesterov. resnet18: 11.2M, top-1 err 24.39, top-5 6.95.

## Paragrafi del libro letti (testi locali in /tmp/cv/libri)
- visionbook 10.3 (GD, algoritmo 10.1), 10.4 (schedule; lineare dipende da K; cosine; decay su plateau), 10.5 (momentum, fig. 10.2: un po' aiuta, troppo oltrepassa; Nesterov e Adam solo nominati), 10.6.2 (clipping), 10.7 (SGD, batch, regolarizzazione implicita: soluzione a norma minima nei problemi lineari). Formule MathJax mancanti nel txt: usato il resoconto di NOTE_L16_L17.md.
- visionbook 12.7.3 (batchnorm: statistiche del batch in training, aggregate a test; statistiche del test utili per lo shift; layernorm "trasposta").
- visionbook 14.4 (forward poi backward, alg. 14.1), 14.5 (batch: media dei gradienti, eq. 14.3).
- visionbook 24.4 (CNN semplice: un solo conv layer nonostante il testo dica due; gap "somma" ma è media: refusi già noti), 24.6 (feature map, fig. 24.23–24.25, PCA rosso/verde/blu = componenti 1/2/3, ResNet18 tra le reti), 24.7 (RF, downsampling, gap), 24.11.3 (ResNet, W x_in, identità facile, "la rete impara quanto essere profonda").
- visionbook 36.2 (augmentation, invarianza, OCR b/d, chiralità, equivarianza per segmentazione, domain randomization, fig. 36.2 Caltech256 vs CIFAR100 con PCA di CLIP).
- Prince 6.1 (GD, line search), 6.2.1 (eq. 6.10 con SOMMA sul batch; epoca; senza reinserimento), 6.2.2 (proprietà SGD, schedule a gradini), 6.3 (momentum m ← βm + (1−β)g), 6.3.1 Nesterov, 6.4 (Adam; difficile scegliere un lr stabile in tutte le direzioni, fig. 6.9), 9.3.8 (augmentation), 11.4 (BN eq. 11.7–11.9, per canale su batch e posizioni, statistiche congelate a test), 11.4.1 (benefici: propagazione stabile, lr più alti, regolarizzazione), 11.5.1 (ResNet nell'ordine BN-ReLU-conv = pre-attivazione; bottleneck 1×1-3×3-1×1; ResNet-200).
- Nota per la dispensa: il Prince 11.5.1 descrive il blocco in ordine pre-attivazione, il notebook usa l'ordine originale post-attivazione (conv-BN-ReLU, ReLU dopo la somma).

## Dubbi
- La fig. 36.2 e le figure 24.24–24.25 non sono state guardate (solo didascalie nel txt).
- I risultati dei mini esperimenti sono a seme singolo e pochi batch: indicativi.
