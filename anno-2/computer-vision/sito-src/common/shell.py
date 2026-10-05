import json, glob, re, os, html as H
dnav = json.load(open('/tmp/cv/site/lessons/dispensa.json'))['nav'] if os.path.exists('/tmp/cv/site/lessons/dispensa.json') else []
L = sorted((json.load(open(f)) for f in [f for f in glob.glob('/tmp/cv/site/lessons/L*.json')]), key=lambda d: d['num'])
man = [dict(id=d['id'], num=d['num'], short=d['short'], h1=d['h1'], date=d['date'], nav=d['nav'],
            n=len(re.findall(r'<article class="slide', d['html'])), w=len(re.findall(r'class="box w"', d['html'][d['html'].find('<article'):])),
            lab=('NOTEBOOK' in d['html'] and 'SLIDE 1' not in d['html'])) for d in L]
style = open('/tmp/cv/common/style.css').read()
style = style.replace('.slide .thumb{position:sticky;top:70px', '.slide .thumb{position:sticky;top:118px').replace('scroll-margin-top:64px', 'scroll-margin-top:120px').replace('scroll-margin-top:70px', 'scroll-margin-top:120px')
style += '''
.top{padding-block:8px 0}
.top .row1{display:flex;gap:14px;align-items:center;flex-wrap:wrap}
.lessons{display:flex;gap:4px;flex-wrap:wrap}
.lessons a{color:#C9D3DA;text-decoration:none;font-size:13.5px;padding:4px 10px;border-radius:6px;font-variant-numeric:tabular-nums}
.lessons a[aria-current="page"]{background:#E9EEF1;color:#1C2630;font-weight:600}
.lessons a:hover:not([aria-current]),.lessons a:focus-visible{background:#35464E;color:#fff;outline:none}
.secnav{display:flex;gap:2px;overflow-x:auto;margin-top:6px;padding-bottom:8px;scrollbar-width:thin}
.secnav a{white-space:nowrap;color:#9FB0BB;text-decoration:none;font-size:13px;padding:3px 9px;border-radius:5px}
.secnav a:hover,.secnav a:focus-visible{background:#35464E;color:#fff;outline:none}
.secnav:empty{display:none}
.top nav.secnav{flex-wrap:nowrap}
.home-grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));margin-top:22px}
.lcard{display:grid;gap:6px;align-content:start;text-decoration:none;color:var(--ink);background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:16px 18px}
.lcard:hover,.lcard:focus-visible{border-color:var(--accent);outline:none}
.lcard .n{font-family:"IBM Plex Mono",monospace;font-size:12.5px;color:var(--accent)}
.lcard h3{font-size:19px}
.lcard p{margin:0;color:var(--muted);font-size:14px}
.lcard .meta{display:flex;gap:8px;flex-wrap:wrap;margin-top:4px}
.loading{padding:60px 0;color:var(--muted)}
'''
js = open('/tmp/cv/common/copy.js').read()
pjs = open('/tmp/cv/common/presenter.js').read() + '\n' + open('/tmp/cv/common/hl.js').read() + '\n' + open('/tmp/cv/common/disp_reader.js').read()
style += open('/tmp/cv/common/presenter.css').read()
import os
hd = json.load(open('/tmp/cv/site/hd.json')) if os.path.exists('/tmp/cv/site/hd.json') else {}
page = f'''<title>Computer Vision · Appunti</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&family=IBM+Plex+Mono:wght@400;500&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&display=swap">
<style>{style}</style>
<div class="top"><div class="wrap">
  <div class="row1"><strong>Computer Vision</strong><nav class="lessons" id="lessons" aria-label="Lezioni"></nav></div>
  <nav class="secnav" id="secnav" aria-label="Sezioni della lezione"></nav>
</div></div>
<div class="wrap"><main id="main"></main></div>
<script>
var LESSONS = {json.dumps(man, ensure_ascii=False)};
var HD_URLS = {json.dumps(hd)};
var DISP_NAV = {json.dumps(dnav, ensure_ascii=False)};
var cache = {{}};
function esc(s){{return String(s).replace(/[&<>"]/g,function(c){{return {{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c];}});}}
function renderNav(cur){{
  var h = '<a href="#home"' + (cur==='home'?' aria-current="page"':'') + '>Indice</a><a href="#dispensa"' + (cur==='dispensa'?' aria-current="page"':'') + '>Dispensa completa</a>';
  LESSONS.forEach(function(l){{ h += '<a href="#'+l.id+'"'+(cur===l.id?' aria-current="page"':'')+' title="'+esc(l.h1)+'">L'+l.num+' · '+esc(l.short)+'</a>'; }});
  document.getElementById('lessons').innerHTML = h;
  var l = LESSONS.filter(function(x){{return x.id===cur;}})[0];
  var navl = l ? l.nav : (cur==='dispensa' ? DISP_NAV : null);
  document.getElementById('secnav').innerHTML = navl ? navl.map(function(s){{return '<a href="#'+cur+'" data-sec="'+s[0]+'">'+esc(s[1])+'</a>';}}).join('') : '';
}}
function home(){{
  var h = '<header class="hero"><div class="eyebrow">Laurea magistrale in AI · Università di Pisa · Antonio Carta · 2026/27</div><h1>Appunti di Computer Vision</h1><p>Ogni lezione si apre con una dispensa che la spiega da zero, con i video da guardare prima e i capitoli del libro. Sotto ci sono le schede slide per slide (con le correzioni agli errori delle slide), la modalità presentazione e la guida allo studio con le domande tipo orale.</p><p style="margin-top:16px"><a class="btn-primary" style="display:inline-block;text-decoration:none" href="#dispensa">Leggi la dispensa completa</a></p></header><div class="home-grid">';
  LESSONS.slice().reverse().forEach(function(l){{
    h += '<a class="lcard" href="#'+l.id+'"><span class="n">LEZIONE '+l.num+(l.date?' · '+esc(l.date):'')+(l.lab?' · LAB':'')+'</span><h3>'+esc(l.h1)+'</h3><p>'+esc(l.short)+'</p><span class="meta"><span class="tag k">'+l.n+' schede</span>'+(l.w?'<span class="tag w">'+l.w+' correzioni</span>':'')+'</span></a>';
  }});
  document.getElementById('main').innerHTML = h + '</div>';
}}
function show(id){{
  var main = document.getElementById('main');
  renderNav(id);
  if (id==='home'){{ main.className=''; home(); window.scrollTo(0,0); return; }}
  var isL = id !== 'dispensa';
  main.className = isL ? '' : 'dview';
  if (cache[id]){{ main.innerHTML = cache[id]; window.scrollTo(0,0); isL && window.PV && PV.lessonShown(id); window.HL && HL.shown(); window.DR && DR.decorate(); return; }}
  main.innerHTML = '<p class="loading">Carico la lezione…</p>';
  fetch('lessons/'+id+'.json').then(function(r){{ if(!r.ok) throw new Error(r.status); return r.json(); }}).then(function(d){{
    cache[id] = d.html; if (current()===id){{ main.innerHTML = d.html; window.scrollTo(0,0); isL && window.PV && PV.lessonShown(id); window.HL && HL.shown(); window.DR && DR.decorate(); }}
  }}).catch(function(){{ main.innerHTML = '<p class="loading">Non riesco a caricare la lezione. Ricarica la pagina per riprovare.</p>'; }});
}}
function current(){{
  var h = location.hash.replace('#','');
  if (h==='dispensa') return h;
  return LESSONS.some(function(l){{return l.id===h;}}) ? h : 'home';
}}
document.getElementById('secnav').addEventListener('click', function(e){{
  var a = e.target.closest('a[data-sec]'); if(!a) return;
  e.preventDefault(); var t = document.getElementById(a.getAttribute('data-sec')); if(t) t.scrollIntoView({{behavior:'smooth'}});
}});
window.addEventListener('hashchange', function(){{ window.PV && PV.close(); window.DR && DR.close(); show(current()); }});
show(current());
</script>
<script>{js}</script>
<script>{pjs}</script>'''
open('/tmp/cv/site/index.html','w').write(page)
print('shell', len(page), [ (m['id'], m['n'], m['w']) for m in man])
