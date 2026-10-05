"""Elenca i file del corso non ancora integrati nel sito.
Uso (sul Mac, da device_bash):  python3 $HOME/mnt/CV/_sito/common/check_new.py
Stampa JSON: {"nuovi": {"L7": [...]}, "modificati": {...}, "lezioni_nel_sito": [...]}
Con  --segna L7 L8  registra come integrati i file attuali di quelle lezioni in _sito/stato.json.
"""
import os, sys, json, re

ROOT = os.path.join(os.environ['HOME'], 'mnt', 'CV')
STATO = os.path.join(ROOT, '_sito', 'stato.json')
IGNORA_DIR = {'data', '__pycache__', '.ipynb_checkpoints', 'fig'}


def lezione(rel):
    m = re.match(r'Lessons/(L\d+)', rel)
    return m.group(1) if m else 'altro'


def scan():
    out = {}
    base = os.path.join(ROOT, 'Lessons')
    for d, dirs, files in os.walk(base):
        dirs[:] = [x for x in dirs if x not in IGNORA_DIR and not x.startswith('.')]
        for f in files:
            if f.startswith('.'):
                continue
            p = os.path.join(d, f)
            rel = os.path.relpath(p, ROOT)
            st = os.stat(p)
            out[rel] = [st.st_size, int(st.st_mtime)]
    return out


stato = json.load(open(STATO)) if os.path.exists(STATO) else {'file': {}, 'lezioni': []}
cur = scan()

if len(sys.argv) > 2 and sys.argv[1] == '--arricchito':
    stato['da_arricchire'] = [x for x in stato.get('da_arricchire', []) if x not in sys.argv[2:]]
    json.dump(stato, open(STATO, 'w'), indent=1)
    print('arricchite col libro', sys.argv[2:])
    sys.exit()

if len(sys.argv) > 2 and sys.argv[1] == '--segna':
    for rel, v in cur.items():
        if lezione(rel) in sys.argv[2:]:
            stato['file'][rel] = v
    stato['lezioni'] = sorted(set(stato['lezioni']) | set(sys.argv[2:]), key=lambda s: int(s[1:]))
    json.dump(stato, open(STATO, 'w'), indent=1)
    print('segnate', sys.argv[2:])
    sys.exit()

nuovi, mod = {}, {}
for rel, v in cur.items():
    old = stato['file'].get(rel)
    if old is None:
        nuovi.setdefault(lezione(rel), []).append(rel)
    elif old != v:
        mod.setdefault(lezione(rel), []).append(rel)
print(json.dumps({'nuovi': nuovi, 'modificati': mod, 'lezioni_nel_sito': stato['lezioni'], 'da_arricchire_col_libro': stato.get('da_arricchire', [])}, indent=1, ensure_ascii=False))
