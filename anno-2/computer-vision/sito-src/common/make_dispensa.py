"""Unisce le dispense di tutte le lezioni in site/lessons/dispensa.json (vista "Dispensa completa")."""
import os, re, json, base64, glob
R = '/tmp/cv'
def uri(p):
    raw = open(p, 'rb').read()
    if p.endswith('.png') and len(raw) > 60000:
        # immagini grandi: webp, molto più leggero (stessa resa a schermo)
        import io
        from PIL import Image
        im = Image.open(io.BytesIO(raw)); im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
        if im.width > 1200: im = im.resize((1200, round(im.height * 1200 / im.width)), Image.LANCZOS)
        b = io.BytesIO(); im.save(b, 'WEBP', quality=80, method=4)
        if b.tell() < len(raw): return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
    mime = 'image/png' if p.endswith('.png') else 'image/jpeg'
    return f'data:{mime};base64,' + base64.b64encode(raw).decode()
parts = []; nav = []
for d in sorted(glob.glob(f'{R}/L*'), key=lambda x: int(re.sub(r'\D', '', os.path.basename(x)) or 0)):
    L = os.path.basename(d); p = f'{d}/dispensa.html'
    if not re.fullmatch(r'L\d+', L) or not os.path.exists(p): continue
    M = {}; exec(open(f'{d}/meta.py').read(), M)
    h = open(p).read()
    for m in set(re.findall(r'\{\{IMG:([^}]+)\}\}', h)): h = h.replace('{{IMG:%s}}' % m, uri(os.path.join(d, m)))
    mt = re.search(r'<div class="sec" id="[^"]+"><h2>[^<]*</h2>(?:<span>([^<]*)</span>)?</div>', h)
    tempo = mt.group(1) if mt and mt.group(1) else ''
    if mt: h = h[:mt.start()] + h[mt.end():]
    h = h.replace('<div class="disp">', f'<div class="disp" data-hl="{L}-disp">', 1)
    sid = f'd-{L}'
    nav.append((sid, f'L{M["NUM"]} · {M["SHORT"]}'))
    parts.append(f'<div class="sec" id="{sid}"><h2>L{M["NUM"]} · {M["H1"]}</h2><span>{tempo} · <a href="#{L}">apri le schede della lezione</a></span></div>\n{h}')
intro = ('<header class="hero"><div class="eyebrow">Computer Vision · dispensa del corso</div><h1>Dispensa completa</h1>'
         '<p>Tutte le dispense delle lezioni in sequenza, da leggere come un libro. Ogni capitolo parte dai video da guardare prima e finisce con le domande di verifica; il link accanto al titolo porta alle schede slide per slide della lezione. Seleziona del testo per evidenziarlo (giallo, verde, rosa) o sottolinearlo: i segni restano salvati e compaiono anche nella pagina della lezione.</p>'
         '<p class="legend-hl"><span><mark class="sh sh-y">giallo</mark> concetti chiave</span><span><mark class="sh sh-p">rosa</mark> problemi, limiti, trappole</span><span><mark class="sh sh-g">verde</mark> proprietà e vantaggi</span><span><mark class="sh sh-b">blu</mark> definizioni e formule centrali</span></p></header>')
html = intro + '\n'.join(parts)
json.dump({'id': 'dispensa', 'nav': nav, 'html': html}, open(f'{R}/site/lessons/dispensa.json', 'w'), ensure_ascii=False)
print('dispensa', len(parts), 'lezioni', round(len(html) / 1e6, 2), 'MB')
