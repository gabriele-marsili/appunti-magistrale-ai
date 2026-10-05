#!/usr/bin/env python3
"""Esporta il sito in una cartella statica per GitHub Pages (CV/docs).
Uso: python3 common/make_gh.py <cartella_uscita> [<cartella_hd>]
- copia index.html (con doctype/charset/viewport), lessons/*.json, .nojekyll;
- le slide HD: nel sito Claude sono asset (/_blob/<id>), qui diventano file hd/<L>.json.
  <cartella_hd> contiene i pacchetti HD come <L>.json (quelli già presenti in uscita/hd restano)."""
import json, os, shutil, sys, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')
out = sys.argv[1]; hdsrc = sys.argv[2] if len(sys.argv) > 2 else None
os.makedirs(os.path.join(out, 'lessons'), exist_ok=True); os.makedirs(os.path.join(out, 'hd'), exist_ok=True)
html = open(os.path.join(SITE, 'index.html'), encoding='utf-8').read()
hd = json.load(open(os.path.join(SITE, 'hd.json')))
for L, url in hd.items():
    html = html.replace(url, 'hd/%s.json' % L)
    if hdsrc and os.path.exists(os.path.join(hdsrc, L + '.json')):
        shutil.copyfile(os.path.join(hdsrc, L + '.json'), os.path.join(out, 'hd', L + '.json'))
    if not os.path.exists(os.path.join(out, 'hd', L + '.json')):
        print('ATTENZIONE: manca hd/%s.json (slide HD di %s non disponibili su GitHub)' % (L, L))
if not html.lstrip().lower().startswith('<!doctype'):
    html = ('<!doctype html>\n<html lang="it">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n') + html + '\n</html>\n'
open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(html)
for f in glob.glob(os.path.join(SITE, 'lessons', '*.json')):
    shutil.copyfile(f, os.path.join(out, 'lessons', os.path.basename(f)))
open(os.path.join(out, '.nojekyll'), 'w').close()
print('ok docs:', len(glob.glob(os.path.join(out, 'lessons', '*.json'))), 'file lezione,', len(glob.glob(os.path.join(out, 'hd', '*.json'))), 'pacchetti HD')
