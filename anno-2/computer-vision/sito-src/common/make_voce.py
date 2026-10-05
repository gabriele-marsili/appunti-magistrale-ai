#!/usr/bin/env python3
"""Controlla i copioni delle videolezioni e scrive site/lessons/voce_L<n>.json.
Uso: python3 common/make_voce.py [L5 ...]   (senza argomenti: tutte le lezioni con copione.json)
Le ancore "a" vengono risolte sull'indice del blocco nella dispensa costruita (site/lessons/L<n>.json)."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blocks import blocks, anchor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BAD = re.compile(r'[=+−∑∗≈→←↔/%()\[\]{}<>_^|*#~\\∫∂√∞≤≥×·αβγδεζηθικλμνξπρστυφχψωΑΒΓΔΘΛΞΠΣΦΨΩ“”]')

def check(L):
    p = os.path.join(ROOT, L, 'copione.json')
    d = json.load(open(p, encoding='utf-8'))
    bl = blocks(L)
    anchors = [anchor(t) for _, t, _ in bl]
    errs, out, words = [], [], 0
    last = -1
    for i, s in enumerate(d['segs']):
        a, t = s.get('a', ''), s.get('t', '').strip()
        idx = [j for j, x in enumerate(anchors) if x == a]
        if 'b' in s and s['b'] in idx: b = s['b']
        elif len(idx) == 1: b = idx[0]
        elif not idx:
            # tolleranza: confronto senza spazi
            na = re.sub(r'\s+', '', a); idx = [j for j, x in enumerate(anchors) if re.sub(r'\s+', '', x) == na]
            if len(idx) == 1: b = idx[0]
            else: errs.append('seg %d: ancora non trovata: %r' % (i, a)); continue
        else: errs.append('seg %d: ancora ambigua %r, aggiungi "b" fra %s' % (i, a, idx)); continue
        m = BAD.findall(t)
        if m: errs.append('seg %d: simboli da scrivere in parole: %s  in: %s' % (i, ''.join(sorted(set(m))), t[:90]))
        if re.search(r'\b(es|ecc|cfr)\.', t): errs.append('seg %d: abbreviazione' % i)
        if re.search(r'\bslide \d', t, re.I): errs.append('seg %d: non citare "slide N"' % i)
        n = len(t.split()); words += n
        if n > 130: errs.append('seg %d: troppo lungo (%d parole), dividilo' % (i, n))
        if b < last - 12: errs.append('seg %d: torna molto indietro (blocco %d dopo %d)' % (i, b, last))
        last = max(last, b)
        out.append({'b': b, 't': t})
    return out, words, errs

def main(args):
    ls = args or sorted([x for x in os.listdir(ROOT) if re.fullmatch(r'L\d+', x) and os.path.exists(os.path.join(ROOT, x, 'copione.json'))], key=lambda x: int(x[1:]))
    bad = False
    for L in ls:
        segs, words, errs = check(L)
        if errs:
            bad = True
            print('ERRORI %s (%d):' % (L, len(errs))); [print('  ' + e) for e in errs[:60]]
            continue
        json.dump(segs, open(os.path.join(ROOT, 'site/lessons/voce_%s.json' % L), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        print('ok %s: %d segmenti, %d parole, circa %d minuti a 1x' % (L, len(segs), words, round(words / 150)))
    sys.exit(1 if bad else 0)

if __name__ == '__main__':
    main(sys.argv[1:])
