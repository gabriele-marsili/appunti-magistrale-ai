"""Uso: python3 build.py <cartella_lezione>
La cartella contiene:
  meta.py    -> TITLE (titolo pagina <title>), H1, EYEBROW, INTRO (html), PDF (path o None), OUT (path html)
  slides.py  -> chiamate s(n, titolo, body_html, kind=None|'div', sec=None|(id, nome, 'slide a-b'), img=None, printed=None)
  extra.html -> html libero dopo le slide (guida allo studio ecc.), con {{IMG:file.png}} per immagini nella cartella
"""
import base64, os, re, sys, subprocess, html as H
D = sys.argv[1]; C = os.path.dirname(os.path.abspath(__file__))
M = {}; exec(open(f'{D}/meta.py').read(), M)
S = []
def s(n, t, body, kind=None, sec=None, img=None, printed=None):
    S.append(dict(n=n, t=t, body=body, kind=kind, sec=sec, img=img, printed=printed))
exec(open(f'{D}/slides.py').read(), {'s': s})
def uri(p):
    raw = open(p, 'rb').read()
    if p.endswith('.png') and len(raw) > 60000:
        # immagini grandi: webp, molto più leggero (stessa resa a schermo)
        import io
        from PIL import Image
        im = Image.open(io.BytesIO(raw)); im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
        if im.width > 1400: im = im.resize((1400, round(im.height * 1400 / im.width)), Image.LANCZOS)
        b = io.BytesIO(); im.save(b, 'WEBP', quality=86, method=4)
        if b.tell() < len(raw): return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
    mime = 'image/png' if p.endswith('.png') else 'image/jpeg'
    return f'data:{mime};base64,' + base64.b64encode(raw).decode()
th = None
if M.get('PDF'):
    th = f'{D}/_thumbs'
    if not os.path.isdir(th):
        os.makedirs(th)
        subprocess.run(['pdftoppm', '-jpeg', '-jpegopt', 'quality=72', '-scale-to', '640', M['PDF'], f'{th}/s'], check=True)
    files = sorted(os.listdir(th)); w = len(re.search(r's-(\d+)', files[0]).group(1))
out = []; nav = []
for d in S:
    n = d['n']
    if d['sec']:
        sid, name, rng = d['sec']
        nav.append((sid, name))
        out.append(f'<div class="sec" id="{sid}"><h2>{name}</h2><span>{rng}</span></div>')
    img = d['img'] and os.path.join(D, d['img'])
    if img is None and th and d['kind'] != 'nothumb':
        img = f'{th}/s-{n:0{w}d}.jpg'
    cls = 'slide' + (' div' if d['kind'] == 'div' else '') + ('' if img else ' nothumb')
    if M.get('PDF'):
        pr = d['printed'] if d['printed'] is not None else ('' if (n == 1 or d['kind'] == 'div') else f' <em>· pag. {n-1}/{M["PRINTED_TOTAL"]}</em>')
        label = f'SLIDE {n}{pr}' + (' <em>· divisoria</em>' if d['kind'] == 'div' else '')
    else:
        label = d['printed'] or f'SCHEDA {n}'
    thumb = f'<div class="thumb"><img src="{uri(img)}" alt="Slide {n}: {H.escape(d["t"])}" loading="lazy"></div>' if img else ''
    out.append(f'''<article class="{cls}" id="s{n}" data-n="{n}">{thumb}
<div class="notes"><div class="head"><div><div class="num">{label}</div><h3>{d['t']}</h3></div><button class="copy" type="button" aria-label="Copia gli appunti della scheda {n}">Copia</button></div>
<div class="body" data-hl="{M['ID']}-s{n}">{d['body'].strip()}</div></div></article>''')
extra = open(f'{D}/extra.html').read() if os.path.exists(f'{D}/extra.html') else ''
for m in set(re.findall(r'\{\{IMG:([^}]+)\}\}', extra)):
    extra = extra.replace('{{IMG:%s}}' % m, uri(os.path.join(D, m)))
for sid, name in re.findall(r'<div class="sec" id="([^"]+)"><h2>([^<]+)</h2>', extra):
    nav.append((sid, name))
howto = open(f'{C}/howto.html').read() if M.get('PDF') else M.get('HOWTO', '')
# dispensa: spiegazione da zero della lezione, prima delle schede
disp = open(f'{D}/dispensa.html').read() if os.path.exists(f'{D}/dispensa.html') else ''
for m in set(re.findall(r'\{\{IMG:([^}]+)\}\}', disp)):
    disp = disp.replace('{{IMG:%s}}' % m, uri(os.path.join(D, m)))
disp = disp.replace('<div class="disp">', f'<div class="disp" data-hl="{M["ID"]}-disp">', 1)
dnav = re.findall(r'<div class="sec" id="([^"]+)"><h2>([^<]+)</h2>', disp)
nav[:0] = dnav
body = f"""<header class="hero"><div class="eyebrow">{M['EYEBROW']}</div><h1>{M['H1']}</h1><p>{M['INTRO']}</p></header>
{disp}
{howto}
{chr(10).join(out)}
{extra}"""
import json
os.makedirs('/tmp/cv/site/lessons', exist_ok=True)
frag = dict(id=M['ID'], num=M['NUM'], short=M['SHORT'], h1=M['H1'], date=M.get('DATE',''), nav=nav, html=body)
json.dump(frag, open(f"/tmp/cv/site/lessons/{M['ID']}.json", 'w'), ensure_ascii=False)
print('ok', M['ID'], len(S), 'schede', round(len(body) / 1e6, 2), 'MB')
