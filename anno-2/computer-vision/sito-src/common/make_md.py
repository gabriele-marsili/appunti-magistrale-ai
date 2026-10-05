# Genera dispensa/*.md dalla dispensa HTML.
# Uso: dalla cartella anno-2/computer-vision del repo appunti-magistrale-ai: python3 sito-src/common/make_md.py
import re, subprocess, os, bs4, unicodedata
SITE='https://gabriele-marsili.github.io/appunti-magistrale-ai/anno-2/computer-vision/sito/'
def slug(s):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+','-',s).strip('-')[:50]
idx=[]
for n in range(1,10):
    L='L%d'%n; meta={}
    exec(open('sito-src/%s/meta.py'%L).read(), meta)
    html=open('sito-src/%s/dispensa.html'%L, encoding='utf-8').read()
    html=re.sub(r'\{\{IMG:([^}]+)\}\}', lambda m: '../sito-src/%s/%s'%(L,m.group(1)), html)
    s=bs4.BeautifulSoup(html,'html.parser')
    for sec in s.select('div.sec'): sec.decompose()
    for m in s.select('mark.sh'):
        if m.find_parent(['b','strong']) or m.find(['b','strong']): m.unwrap(); continue
        b=s.new_tag('strong'); b.extend(list(m.contents)); m.replace_with(b)
    for f in s.select('span.f'):
        c=s.new_tag('code'); c.string=f.get_text(); f.replace_with(c)
    for box in s.select('div.box'):
        bq=s.new_tag('blockquote'); bq.extend(list(box.contents)); box.replace_with(bq)
    for d in s.select('details'):
        sm=d.find('summary')
        if sm: 
            p=s.new_tag('p'); st=s.new_tag('strong'); st.string=sm.get_text(); p.append(st); sm.replace_with(p)
        d.unwrap()
    for w in s.select('div.watch'):
        ul=s.new_tag('ul')
        for a in w.find_all('a'):
            li=s.new_tag('li'); na=s.new_tag('a', href=a['href']); b=a.find('b'); na.string=b.get_text(' ',strip=True) if b else a['href']
            k=a.find('span',class_='k'); d=a.find('span',class_='d')
            li.append(na); li.append(' (%s). %s'%(k.get_text(' ',strip=True) if k else 'Video', d.get_text(' ',strip=True) if d else ''))
            ul.append(li)
        w.replace_with(ul)
    for dv in s.find_all('div'): dv.unwrap()
    for a in s.find_all('a', href=True):
        if re.fullmatch(r'#L\d+', a['href']): a['href']='%s-%s.md'%(a['href'][1:].replace('L','L0'), '') if False else SITE+a['href']
    md=subprocess.run(['pandoc','-f','html','-t','gfm','--wrap=none'],input=str(s),capture_output=True,text=True).stdout
    md=re.sub(r'\n{3,}','\n\n',md)
    title=meta['H1']; name='L%02d-%s.md'%(n,slug(meta.get('SHORT',title)))
    head='# L%d · %s\n\n*%s*\n\n[Versione interattiva sul sito, con videolezione](%s#%s) · [Indice della dispensa](README.md)\n\n'%(n,meta.get('SHORT',title),meta.get('EYEBROW',''),SITE,L)
    open('dispensa/'+name,'w',encoding='utf-8').write(head+md)
    idx.append((n,name,meta.get('SHORT',title),title,len(md.split())))
r='# Dispensa di Computer Vision\n\nUna dispensa per lezione, scritta da zero integrando slide e libro (Torralba, Isola, Freeman, *Foundations of Computer Vision*). Il **grassetto** corrisponde alle evidenziature del sito. La versione interattiva, con evidenziature colorate, presentazione annotabile e videolezione, è sul [sito](%s#dispensa).\n\n| Lezione | Argomento | Parole |\n|---|---|---|\n'%SITE
for n,name,sh,t,w in idx: r+='| [L%d · %s](%s) | %s | %d |\n'%(n,sh,name,t,w)
open('dispensa/README.md','w',encoding='utf-8').write(r)
print(r)
