# Esecuzione ridotta del notebook vit_trained.ipynb: training su un sottoinsieme, figure salvate in out/
import json, os, sys, time, re
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
W='/tmp/cv/L18/work'; os.chdir(W)
EP=int(os.environ.get('EP','1')); NTR=int(os.environ.get('NTR','0'))
nb=json.load(open('/tmp/cv/L18/vit_trained.ipynb'))
cur={'cell':0,'k':0}
def show(*a,**k):
    cur['k']+=1; plt.savefig(f"{W}/out/c{cur['cell']:02d}_{cur['k']}.png",dpi=90,bbox_inches='tight'); plt.close('all')
plt.show=show
import torch; torch.set_num_threads(2)
g={'__name__':'__main__'}
log=open(f'{W}/out/log_EP{EP}_N{NTR}.txt','w')
class Tee:
    def write(self,s): sys.__stdout__.write(s); log.write(s); log.flush()
    def flush(self): pass
sys.stdout=Tee()
for i,c in enumerate(nb['cells'],1):
    if c['cell_type']!='code': continue
    src=''.join(c['source'])
    src=src.replace('download=True','download=False')
    src=re.sub(r'EPOCHS = 40.*', f'EPOCHS = {EP}', src)
    if i==5 and NTR:
        src+=f"\ntrain_set = Subset(train_set, torch.randperm(len(train_set), generator=torch.Generator().manual_seed(0))[:{NTR}].tolist())\ntrain_loader = DataLoader(train_set, batch_size=BATCH_SIZE, shuffle=True, num_workers=2)\nprint('SUBSET train', len(train_set))\n"
    cur['cell']=i; cur['k']=0
    print(f'\n##### CELLA {i}'); t=time.time()
    exec(compile(src,f'cella{i}','exec'),g)
    print(f'##### fine cella {i} ({time.time()-t:.1f}s)')
import pickle
torch.save(g['model'].state_dict(), f'{W}/out/model_EP{EP}_N{NTR}.pt')
