import subprocess, glob, base64, io, json, sys, os
from PIL import Image
pdfs={'L2':'/mnt/user-data/uploads/CV/Lessons/L2.pdf','L3':'/mnt/user-data/uploads/CV/Lessons/L3.pdf','L5':'/mnt/user-data/uploads/CV/Lessons/L5.pdf','L6':'/mnt/user-data/uploads/CV/Lessons/L6/L6.pdf'}
for L,p in pdfs.items():
    d=f'/tmp/cv/hd/{L}'; os.makedirs(d,exist_ok=True)
    if not glob.glob(d+'/p-*.png'):
        subprocess.run(['pdftoppm','-png','-scale-to','1800',p,d+'/p'],check=True)
    out=[]
    for f in sorted(glob.glob(d+'/p-*.png')):
        b=io.BytesIO(); Image.open(f).convert('RGB').save(b,'WEBP',quality=78,method=5)
        out.append('data:image/webp;base64,'+base64.b64encode(b.getvalue()).decode())
    json.dump({'id':L,'slides':out},open(f'/home/claude/cv-hd/{L}-hd.json','w'))
    print(L,len(out),os.path.getsize(f'/home/claude/cv-hd/{L}-hd.json')//1024//1024,'MB')
