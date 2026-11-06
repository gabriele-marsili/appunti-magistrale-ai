# Verifiche per le soluzioni: (a) senza posizioni il [CLS] e' invariante alle permutazioni delle patch;
# (b) test di occlusione (cella 48) sul ViT-B/16 preaddestrato; (c) costi in MAC.
import json, re, math, torch, torch.nn as nn, torch.nn.functional as F, torchvision
from torchvision import transforms
from torch.utils.data import Subset, DataLoader
torch.set_num_threads(1)
nb = json.load(open('/tmp/cv/L18/vit_trained.ipynb'))
g = {}
src = lambda i: ''.join(nb['cells'][i - 1]['source'])
exec("import math, torch, torch.nn as nn, torch.nn.functional as F\n" + src(11).split('patch_embed = PatchEmbed')[0], g)
exec(src(33), g)
exec(src(35).split('model = ViT')[0], g)
ViT = g['ViT']
m = ViT(); m.load_state_dict(torch.load('/tmp/cv/L18/work/out/model_EP1_N0.pt')); m.eval()
mean = (0.485, 0.456, 0.406); std = (0.229, 0.224, 0.225)
tf = transforms.Compose([transforms.Resize(256), transforms.CenterCrop(224), transforms.ToTensor(), transforms.Normalize(mean, std)])
val = torchvision.datasets.Imagenette('/tmp/cv/L18/work/data', split='val', size='320px', download=False, transform=tf)
perm = torch.randperm(len(val), generator=torch.Generator().manual_seed(42)).tolist()
test = Subset(val, perm[len(perm) // 2:])
x, y = next(iter(DataLoader(test, batch_size=8)))

def logits_shuffled(model, imgs, p):
    t = model.patch_embed(imgs)[:, p]
    t = torch.cat([model.cls_token.expand(len(imgs), -1, -1), t], 1) + model.pos_embed
    for b in model.blocks: t = b(t)
    return model.head(model.norm(t)[:, 0])

torch.manual_seed(0); p = torch.randperm(196)
with torch.no_grad():
    a = logits_shuffled(m, x, torch.arange(196)); b = logits_shuffled(m, x, p)
    print('(a) con posizioni: max |diff logit| dopo permutazione', (a - b).abs().max().item(),
          '| predizioni uguali', (a.argmax(1) == b.argmax(1)).float().mean().item())
    m.pos_embed.zero_()
    a = logits_shuffled(m, x, torch.arange(196)); b = logits_shuffled(m, x, p)
    print('(a) pos_embed = 0: max |diff logit| dopo permutazione', (a - b).abs().max().item())

from torchvision.models import vit_b_16, ViT_B_16_Weights
vit = vit_b_16(weights=ViT_B_16_Weights.IMAGENET1K_V1).eval()
img = x[0:1].clone()   # chain saw
with torch.no_grad():
    pr = vit(img).softmax(-1)[0]
    print('(b) ViT-B/16 immagine 0: p(chain saw)=%.3f top1=%s' % (pr[491], ViT_B_16_Weights.IMAGENET1K_V1.meta['categories'][pr.argmax()]))
    # occlusione a griglia di patch 2x2 (32x32 pixel) con il valore medio (0 dopo la normalizzazione)
    res = []
    for r in range(0, 14, 2):
        for c in range(0, 14, 2):
            o = img.clone(); o[..., r*16:(r+2)*16, c*16:(c+2)*16] = 0
            res.append((vit(o).softmax(-1)[0, 491].item(), r, c))
    res.sort()
    print('(b) occlusioni 32x32 che abbassano di piu p(chain saw):', [(round(v, 3), r, c) for v, r, c in res[:5]])
    print('(b) p(chain saw) occludendo le righe di patch 0-1, colonne 6-9 (zona delle cuffie):', end=' ')
    o = img.clone(); o[..., 0:32, 96:160] = 0; print(round(vit(o).softmax(-1)[0, 491].item(), 3))

# (c) costi in moltiplicazioni-somme per immagine
for P in (16, 8):
    N = (224 // P) ** 2; T = N + 1; D = 96
    lin = 12 * T * D * D; att = 2 * T * T * D; pe = N * P * P * 3 * D
    print(f'(c) P={P}: T={T}, per blocco lineare {lin/1e6:.1f}M, attenzione {att/1e6:.1f}M; totale 2 blocchi + patch {(2*(lin+att)+pe)/1e6:.1f}M; memoria A (32,4,T,T) float32 {32*4*T*T*4/1e6:.1f} MB')
