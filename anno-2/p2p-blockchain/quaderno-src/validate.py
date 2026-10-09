#!/usr/bin/env python3
"""Valida un file lessons/<ID>.json. Uso: validate.py file.json [--pages N]"""
import json, re, sys

ALLOWED_TAGS = {"p", "strong", "em", "ul", "ol", "li", "code", "pre", "table", "thead", "tbody", "tr", "th", "td",
                "h4", "br", "sup", "sub", "blockquote", "b", "i", "span", "div", "hr"}
BOX_TYPES = {"sapere", "attenzione", "approfondimento"}
BAD_ACCENTS = re.compile(r"\b(perche|poiche|cosi|piu|puo|gia|pero|citta|verra|sara|e')\b(?![\w])", re.I)
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐✅]")


def html_issues(s, where, errs):
    if not isinstance(s, str):
        errs.append(f"{where}: non è una stringa")
        return
    for t in re.findall(r"</?\s*([a-zA-Z0-9]+)", s):
        if t.lower() not in ALLOWED_TAGS:
            errs.append(f"{where}: tag non ammesso <{t}>")
    if "style=" in s or "<script" in s.lower():
        errs.append(f"{where}: style/script non ammessi")
    if EMOJI.search(s):
        errs.append(f"{where}: contiene emoji")
    text = re.sub(r"<[^>]+>", " ", s)
    text = re.sub(r"\$[^$]*\$", " ", text)
    m = BAD_ACCENTS.search(text)
    if m:
        errs.append(f"{where}: possibile accento mancante '{m.group(0)}'")


def validate(d, pages=None):
    errs = []
    for k in ["id", "kind", "num", "date", "title", "pdf", "pages", "summary", "sections", "slides", "study",
              "exercises", "codeExercises", "oral", "formulas", "corrections", "links"]:
        if k not in d:
            errs.append(f"manca il campo {k}")
    if errs:
        return errs
    if not re.fullmatch(r"(L|LAB)\d{2}", d["id"]):
        errs.append("id non valido")
    if d["kind"] not in ("teoria", "seminario", "lab"):
        errs.append("kind non valido")
    n = d["pages"]
    if pages and n != pages:
        errs.append(f"pages={n} ma il PDF ha {pages} pagine")
    ps = [s.get("p") for s in d["slides"]]
    if ps != list(range(1, n + 1)):
        errs.append(f"le schede devono essere p=1..{n} in ordine (trovate {len(ps)})")
    html_issues(d["summary"], "summary", errs)
    for s in d["slides"]:
        w = f"slide p{s.get('p')}"
        if s.get("kind") not in ("title", "normal", "divider"):
            errs.append(f"{w}: kind non valido")
        if not s.get("title"):
            errs.append(f"{w}: titolo vuoto")
        html_issues(s.get("html", ""), w, errs)
        if s.get("kind") == "normal" and len(re.sub(r"<[^>]+>", "", s.get("html", ""))) < 120:
            errs.append(f"{w}: appunti troppo brevi per una slide di contenuto")
        for b in s.get("boxes", []):
            if b.get("type") not in BOX_TYPES:
                errs.append(f"{w}: box type non valido {b.get('type')}")
            html_issues(b.get("html", ""), w + " box", errs)
    cov = set()
    for sec in d["sections"]:
        cov.update(range(sec["from"], sec["to"] + 1))
    if cov != set(range(1, n + 1)):
        errs.append("le sections non coprono esattamente tutte le pagine")
    att = sum(1 for s in d["slides"] for b in s.get("boxes", []) if b.get("type") == "attenzione")
    att += sum(1 for c in d.get("code", []) for bl in c.get("blocks", []) for b in bl.get("boxes", []) if b.get("type") == "attenzione")
    if att != len(d["corrections"]):
        errs.append(f"box attenzione ({att}) e corrections ({len(d['corrections'])}) non coincidono")
    for i, e in enumerate(d["codeExercises"]):
        for k in ["title", "level", "lang", "q", "starter", "solution", "output", "explain"]:
            if k not in e:
                errs.append(f"codeExercise {i}: manca {k}")
    for i, o in enumerate(d["oral"]):
        html_issues(o.get("a", ""), f"oral {i}", errs)
    if len(d["oral"]) < 5:
        errs.append("servono almeno 5 domande d'orale")
    if d["kind"] != "lab" and len(d["exercises"]) < 2:
        errs.append("servono almeno 2 esercizi a mano")
    if len(d["codeExercises"]) < 2:
        errs.append("servono almeno 2 esercizi di codice")
    G = d.get("guided")
    if d["kind"] == "lab" and G is not None:
        if not G.get("intro"):
            errs.append("guided: manca intro")
        html_issues(G.get("intro", ""), "guided intro", errs)
        html_issues(G.get("prereq", ""), "guided prereq", errs)
        steps = G.get("steps", [])
        if len(steps) < 4:
            errs.append("guided: servono almeno 4 passi")
        for i, st in enumerate(steps):
            w = f"guided passo {i+1}"
            if not st.get("title"):
                errs.append(f"{w}: titolo vuoto")
            if not (st.get("code") or st.get("run")):
                errs.append(f"{w}: serve code o run")
            html_issues(st.get("html", ""), w, errs)
            html_issues(st.get("check", ""), w + " check", errs)
            for p in st.get("slides", []):
                if not (isinstance(p, int) and 1 <= p <= d["pages"]):
                    errs.append(f"{w}: slide {p} fuori range")
    for l in d["links"]:
        if not re.fullmatch(r"(L|LAB)\d{2}", l.get("to", "")):
            errs.append(f"link non valido {l}")
    return errs


if __name__ == "__main__":
    f = sys.argv[1]
    pages = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[2] == "--pages" else None
    d = json.load(open(f, encoding="utf-8"))
    e = validate(d, pages)
    if e:
        print("ERRORI:\n" + "\n".join(e[:80]))
        sys.exit(1)
    print(f"OK {d['id']}: {len(d['slides'])} schede, {len(d['corrections'])} correzioni")
