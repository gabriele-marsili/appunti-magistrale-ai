#!/usr/bin/env python3
"""Elenca i blocchi della dispensa di una lezione come li vede il lettore (figli diretti di .disp).
Uso: python3 common/blocks.py L5   (dopo build.py L5)
Colonne: indice | tag | ancora (40 caratteri, da copiare in "a") | resto del testo"""
import json, sys, re, bs4, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def blocks(L):
    d = json.load(open(os.path.join(ROOT, 'site/lessons/%s.json' % L)))
    s = bs4.BeautifulSoup(d['html'], 'html.parser')
    disp = s.select_one('div.disp[data-hl]')
    src = open(os.path.join(ROOT, L, 'dispensa.html')).read()
    figs = [m.group(1) for m in re.finditer(r'<figure>.*?\{\{IMG:([^}]+)\}\}', src, re.S)]
    out = []; k = 0
    for c in disp.children:
        if not isinstance(c, bs4.Tag): continue
        if c.name == 'figure':
            cap = c.find('figcaption'); img = c.find('img')
            txt = (cap.get_text(' ') if cap else (img.get('alt','') if img else ''))
            fn = figs[k] if k < len(figs) else '?'; k += 1
            out.append(('figure', txt, fn)); continue
        else:
            txt = c.get_text(' ')
        txt = re.sub(r'\s+', ' ', txt).strip()
        out.append((c.name + ('.' + '.'.join(c.get('class')) if c.get('class') else ''), txt, ''))
    return out
def anchor(t): return t[:40]
if __name__ == '__main__':
    for i, (tag, txt, fn) in enumerate(blocks(sys.argv[1])):
        extra = ('  [immagine: /tmp/cv/%s/%s]' % (sys.argv[1], fn)) if fn else ''
        print('%3d | %-10s | %s | %s%s' % (i, tag, anchor(txt), txt[40:160], extra))
