#!/usr/bin/env python3
"""Build del Quaderno P2P & Blockchain.

Legge:  sito/lessons/*.json   (una lezione per file, formato in SCHEMA.md)
        sito/template.html    (pagina)
        sito/vendor/          (pdf.js, worker, MathJax, highlight.js)
        pdf/<ID>.pdf          (PDF ricompressi, vedi README)
Scrive: dist/ pronto da pubblicare (index.html, lessons/, pdf/, vendor/, ripasso.json)

Uso: python3 sito/build.py [--root /home/claude/p2p] [--public]
  --public: versione per GitHub (dist_public/): niente PDF delle slide (diritto d'autore),
            index.html completo di <head>, il lettore puo' caricare il proprio PDF nel browser.
"""
import json, os, re, shutil, subprocess, sys

ROOT = sys.argv[sys.argv.index("--root") + 1] if "--root" in sys.argv else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITO = os.path.join(ROOT, "sito")
PUBLIC = "--public" in sys.argv
DIST = os.path.join(ROOT, "dist_public" if PUBLIC else "dist")
sys.path.insert(0, SITO)
from validate import validate  # noqa: E402

GROUPS = [
    {"name": "P2P e DHT", "short": "P2P e DHT", "ids": ["L01", "L02", "L03", "L04"]},
    {"name": "Crittografia e strutture dati", "short": "Crypto e strutture", "ids": ["L05", "L06"]},
    {"name": "Bitcoin", "short": "Bitcoin", "ids": ["L07", "L08", "L09", "L10", "L11", "L12", "L13"]},
    {"name": "Ethereum, token e IPFS", "short": "Ethereum", "ids": ["L14", "L15", "L16", "L17", "L18", "L20", "L22"]},
    {"name": "Seminari", "short": "Seminari", "ids": ["L19", "L21", "L23"]},
    {"name": "Laboratorio", "short": "Laboratorio", "ids": [f"LAB{i:02d}" for i in range(1, 13)]},
]
TOPIC_ORDER = ["Overlay e DHT", "Crittografia", "Strutture dati", "Bitcoin: transazioni e script", "Bitcoin: mining e consenso",
               "Bitcoin: attacchi", "Lightning e canali", "Ethereum: gas e fee", "Ethereum: PoS", "Token", "IPFS", "Layer 2",
               "Accumulatori", "Identità", "Interoperabilità", "Solidity"]


def page_ratio(pdf):
    out = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    m = re.search(r"Page size:\s+([\d.]+) x ([\d.]+)", out)
    pages = int(re.search(r"Pages:\s+(\d+)", out).group(1))
    return (round(float(m.group(1)) / float(m.group(2)), 4) if m else 4 / 3), pages


def odd_dollars(s):
    s = re.sub(r"<(pre|code)>[\s\S]*?</\1>", "", s)
    s = re.sub(r"\$\$[\s\S]*?\$\$", "", s)
    s = s.replace("\\$", "")
    return s.count("$") % 2 == 1


def main():
    ldir = os.path.join(SITO, "lessons")
    files = sorted(f for f in os.listdir(ldir) if re.fullmatch(r"(L|LAB)\d{2}\.json", f))
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    for d in (["lessons", "vendor"] if PUBLIC else ["lessons", "pdf", "vendor"]):
        os.makedirs(os.path.join(DIST, d))
    manifest, formulas, oral, corrections, links = [], [], [], [], []
    problems = 0
    for f in files:
        L = json.load(open(os.path.join(ldir, f), encoding="utf-8"))
        lid = L["id"]
        pdf = os.path.join(ROOT, "pdf", f"{lid}.pdf")
        ratio, pages = page_ratio(pdf)
        errs = validate(L, pages)
        for s in L["slides"]:
            for txt in [s.get("html", "")] + [b.get("html", "") for b in s.get("boxes", [])]:
                if odd_dollars(txt):
                    errs.append(f"p{s['p']}: numero dispari di $ (usa \\$ per il simbolo del dollaro)")
        if errs:
            problems += 1
            print(f"[{lid}] ATTENZIONE:\n  " + "\n  ".join(errs[:15]))
        L["ratio"] = ratio
        L["pdf"] = f"pdf/{lid}.pdf"
        json.dump(L, open(os.path.join(DIST, "lessons", f), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        if not PUBLIC:
            shutil.copy(pdf, os.path.join(DIST, "pdf", f"{lid}.pdf"))
        manifest.append({"id": lid, "kind": L["kind"], "num": L["num"], "date": L["date"], "title": L["title"],
                         "teacher": L.get("teacher", ""), "pdf": L["pdf"], "pages": L["pages"],
                         "cards": len(L["slides"]), "corrections": len(L["corrections"])})
        for x in L["formulas"]:
            formulas.append({**x, "lesson": lid})
        for x in L["oral"]:
            oral.append({**x, "lesson": lid})
        for x in L["corrections"]:
            corrections.append({**x, "lesson": lid})
        for x in L["links"]:
            links.append({"from": lid, "to": x["to"], "why": x.get("why", "")})
    manifest.sort(key=lambda l: (l["date"] or "9999", l["id"]))
    order = {l["id"]: i for i, l in enumerate(manifest)}
    corrections.sort(key=lambda c: (order.get(c["lesson"], 999), c.get("p") or 0))
    oral.sort(key=lambda o: order.get(o["lesson"], 999))
    json.dump({"formulas": formulas, "oral": oral, "corrections": corrections, "links": links, "topicOrder": TOPIC_ORDER},
              open(os.path.join(DIST, "ripasso.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    tpl = open(os.path.join(SITO, "template.html"), encoding="utf-8").read()
    tpl = tpl.replace("/*MANIFEST*/null/*END*/", "/*MANIFEST*/" + json.dumps(manifest, ensure_ascii=False) + "/*END*/")
    tpl = tpl.replace("/*GROUPS*/null/*END*/", "/*GROUPS*/" + json.dumps(GROUPS, ensure_ascii=False) + "/*END*/")
    if not PUBLIC and os.path.exists(os.path.join(SITO, "recordings.json")):
        # link alle registrazioni (pagine Moodle, servono le credenziali Unipi): solo versione privata
        rec = json.load(open(os.path.join(SITO, "recordings.json"), encoding="utf-8"))
        tpl = tpl.replace("/*RECORDINGS*/null/*END*/", "/*RECORDINGS*/" + json.dumps(rec, ensure_ascii=False) + "/*END*/")
    if PUBLIC:
        tpl = tpl.replace("/*PUBLIC*/false/*END*/", "/*PUBLIC*/true/*END*/")
        tpl = ('<!doctype html>\n<html lang="it">\n<head>\n<meta charset="utf-8">\n'
               '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
               '<style>[hidden]{display:none!important}body{margin:0}img{max-width:100%}</style>\n'
               + tpl.replace("<header class=\"appbar\">", "</head>\n<body>\n<header class=\"appbar\">", 1)
               + "\n</body>\n</html>\n")
    open(os.path.join(DIST, "index.html"), "w", encoding="utf-8").write(tpl)
    for v in os.listdir(os.path.join(SITO, "vendor")):
        shutil.copy(os.path.join(SITO, "vendor", v), os.path.join(DIST, "vendor", v))
    total = sum(os.path.getsize(os.path.join(dp, fn)) for dp, _, fns in os.walk(DIST) for fn in fns)
    nfiles = sum(len(fns) for _, _, fns in os.walk(DIST))
    print(f"Build: {len(manifest)} lezioni, {sum(l['cards'] for l in manifest)} schede, {len(corrections)} correzioni, "
          f"{len(oral)} domande, {len(formulas)} formule. dist = {total/1e6:.1f} MB in {nfiles} file. Lezioni con avvisi: {problems}")
    if total > 62e6 or nfiles > 250:
        print("ATTENZIONE: vicino ai limiti dell'artifact (64 MB, 255 file per versione)")


if __name__ == "__main__":
    main()
