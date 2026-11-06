# Verifica: i picchi di attenzione [CLS] del blocco 12 di ViT-B/16 sono token ad alta norma ("register-like", Darcet et al. 2024)?
import torch, math, torchvision, numpy as np
from torchvision import transforms
from torchvision.models import vit_b_16, ViT_B_16_Weights
from torch.utils.data import Subset, DataLoader
torch.set_num_threads(1)
mean=(0.485,0.456,0.406); std=(0.229,0.224,0.225)
eval_tf=transforms.Compose([transforms.Resize(256),transforms.CenterCrop(224),transforms.ToTensor(),transforms.Normalize(mean,std)])
val_full=torchvision.datasets.Imagenette('/tmp/cv/L18/work/data',split='val',size='320px',download=False,transform=eval_tf)
perm=torch.randperm(len(val_full),generator=torch.Generator().manual_seed(42)).tolist()
test=Subset(val_full,perm[len(perm)//2:])
x,_=next(iter(DataLoader(test,batch_size=32)))
vit=vit_b_16(weights=ViT_B_16_Weights.IMAGENET1K_V1).eval()
def run(batch):
    B=batch.size(0); t=vit._process_input(batch); t=torch.cat([vit.class_token.expand(B,-1,-1),t],1)+vit.encoder.pos_embedding
    norms=[];atts=[]
    with torch.no_grad():
        for blk in vit.encoder.layers:
            h=blk.ln_1(t); a,w=blk.self_attention(h,h,h,need_weights=True,average_attn_weights=False)
            atts.append(w.mean(1)); t=t+a; t=t+blk.mlp(blk.ln_2(t)); norms.append(t.norm(dim=-1))
    return norms,atts
norms,atts=run(x[:32])
for L in [5,9,10,11]:
    n=norms[L][:,1:]; print(f'blocco {L+1}: norma token patch mediana {n.median():.1f}, max {n.max():.1f}, rapporto max/mediana per img (prime 4):',[round((n[i].max()/n[i].median()).item(),1) for i in range(4)])
# per ogni immagine: top-5 patch per attenzione CLS nel blocco 12 e la loro norma in uscita al blocco 11 (ingresso al 12)
for i in range(4):
    a=atts[11][i,0,1:]; top=a.topk(5).indices; nin=norms[10][i,1:]
    rank=(nin.argsort(descending=True).argsort())
    print(f'img {i}: top5 attn CLS b12 -> quota attn {a[top].sum():.2f}; norma(ingresso b12) {[round(v,0) for v in nin[top].tolist()]} rank norma {rank[top].tolist()} | mediana {nin.median():.0f}')
# quota dell'attenzione CLS del blocco 12 sui token con norma > 3x mediana, su 32 immagini
q=[];cnt=[]
for i in range(32):
    nin=norms[10][i,1:]; hi=nin>3*nin.median(); q.append(atts[11][i,0,1:][hi].sum().item()); cnt.append(hi.sum().item())
print('32 img: n token alta norma medio',np.mean(cnt),'quota media attn CLS b12 su di essi',round(np.mean(q),2), 'min',round(min(q),2))
