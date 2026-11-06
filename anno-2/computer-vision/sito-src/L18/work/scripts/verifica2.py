import json, torch, torchvision
from torchvision.models import vit_b_16, ViT_B_16_Weights
torch.set_num_threads(1)
vit = vit_b_16(weights=ViT_B_16_Weights.IMAGENET1K_V1).eval()
print('dropout encoder p =', vit.encoder.dropout.p, '| block dropout p =', vit.encoder.layers[0].dropout.p, '| attn dropout', vit.encoder.layers[0].self_attention.dropout)
nb = json.load(open('/tmp/cv/L18/vit_trained.ipynb')); g = {'device': 'cpu'}
src = ''.join(nb['cells'][55]['source']).split('# Display 4 images')[0]
exec("import torch\n" + src, g)
from torchvision import transforms
from torch.utils.data import Subset, DataLoader
mean=(0.485,0.456,0.406); std=(0.229,0.224,0.225)
tf=transforms.Compose([transforms.Resize(256),transforms.CenterCrop(224),transforms.ToTensor(),transforms.Normalize(mean,std)])
val=torchvision.datasets.Imagenette('/tmp/cv/L18/work/data',split='val',size='320px',download=False,transform=tf)
perm=torch.randperm(len(val),generator=torch.Generator().manual_seed(42)).tolist()
x,_=next(iter(DataLoader(Subset(val,perm[len(perm)//2:]),batch_size=4)))
with torch.no_grad():
    _,_,_,lg = g['pretrained_rollout'](vit, x); ref = vit(x)
print('max |logit rollout - logit torchvision| =', (lg-ref).abs().max().item())
