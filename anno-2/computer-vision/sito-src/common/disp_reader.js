(function(){
  "use strict";
  /* schermo intero vero (Fullscreen API); se il browser non lo permette resta a tutta finestra */
  function fsToggle(el, btn){
    var d = document, cur = d.fullscreenElement || d.webkitFullscreenElement;
    try {
      if (cur) { (d.exitFullscreen || d.webkitExitFullscreen).call(d); return; }
      var req = el.requestFullscreen || el.webkitRequestFullscreen;
      if (!req) { btn.textContent = 'Schermo intero non disponibile'; btn.disabled = true; return; }
      var r = req.call(el); if (r && r.catch) r.catch(function(){ btn.title = 'Il browser non ha permesso lo schermo intero'; });
    } catch(e) {}
  }
  function fsSync(btn){
    var on = !!(document.fullscreenElement || document.webkitFullscreenElement);
    btn.textContent = on ? 'Esci da schermo intero' : 'Schermo intero'; btn.setAttribute('aria-pressed', on ? 'true' : 'false');
  }

  /* Presentazione della dispensa: una sezione per pagina, a tutto schermo, con penna/evidenziatore/sottolinea
     a mano libera e selezione del testo (evidenziatore di HL). La pagina ha larghezza fissa (PAPER px) e viene
     scalata allo schermo: così i segni restano allineati al testo su qualunque dispositivo. */
  /* pagine tutte uguali: formato fisso (orizzontale 16:10 o verticale), riempite col contenuto e scalate allo schermo */
  var FORMATS = {w:{W:1000,H:625}, t:{W:440,H:740}}, FMT = 'w', PW = 1000, PH = 625, PAD = 44, ZSTEPS = [0.85, 1, 1.15, 1.3], zi = 1;
  var PEN = [['#1F2A33','Nero'],['#C62828','Rosso'],['#1565C0','Blu']];
  var HLC = [['#FFE34D','Giallo'],['#7CE38B','Verde'],['#FF9CC6','Rosa'],['#8EC5FF','Blu']];
  var W = {pen:2.2, line:2.6, hl:16};
  var store = {db:null, uid:null}, ann = {}, loaded = {}, timers = {}, chains = {};
  var st = {open:false, pages:[], i:0, tool:'none', pen:'#C62828', hl:'#FFE34D', notes:true, undo:{}, cur:null};
  var root, stage, paper, content, canvas, ctx, countEl, range, titleEl;

  (function init(){
    if (!window.claude || !window.claude.use) return;
    Promise.all([window.claude.use('db'), window.claude.use('user')]).then(function(r){
      if (!r[0] || !r[1]) return;
      return r[1].id().then(function(id){ if (!id) return; store.db = r[0]; store.uid = id; setStatus(); Object.keys(loaded).forEach(loadCloud); });
    }).catch(function(){});
  })();
  function col(){ return store.db.collection('data/users/' + store.uid); }
  function key(p){ return p.L + '-p' + p.k + '-' + FMT + zi + '-v2'; }  // v2: dispensa riscritta il 4/10 (i segni v1 restano nel db)
  function lsGet(k){ try { var v = localStorage.getItem('cvdpen:' + k); return v ? JSON.parse(v) : null; } catch(e){ return null; } }
  function lsSet(k, v){ try { if (v && v.strokes.length) localStorage.setItem('cvdpen:' + k, JSON.stringify(v)); else localStorage.removeItem('cvdpen:' + k); } catch(e){} }
  function setStatus(msg){ var el = document.getElementById('dr-status'); if (el) el.textContent = msg || (store.db ? 'Segni salvati nel tuo account' : 'Segni salvati solo in questo browser'); }
  function strokes(p){ var k = key(p); if (!ann[k]) ann[k] = lsGet(k) || {strokes:[], updated:0}; return ann[k].strokes; }
  function loadCloud(L){
    if (!store.db) return;
    col().where('lesson','==',L).get().then(function(snap){
      snap.docs.forEach(function(d){
        var b = d.data(); if (!b || b.kind !== 'dpen') return;
        var loc = ann[b.zone];
        if (!loc || (b.updated||0) >= (loc.updated||0)) { ann[b.zone] = {strokes: b.strokes||[], updated: b.updated||0}; lsSet(b.zone, ann[b.zone]); }
      });
      if (st.open) redraw();
    }).catch(function(){});
  }
  function changed(p){
    var k = key(p), v = ann[k]; v.updated = Date.now(); lsSet(k, v);
    if (!store.db) return;
    clearTimeout(timers[k]);
    timers[k] = setTimeout(function(){
      var body = {kind:'dpen', lesson:p.L, zone:k, strokes:v.strokes, updated:v.updated};
      if (JSON.stringify(body).length > 240000) { setStatus('Troppi segni su questa pagina: salvati solo in questo browser'); return; }
      setStatus('Salvataggio…');
      chains[k] = (chains[k] || Promise.resolve()).then(function(){
        var ref = col().doc(k); return v.strokes.length ? ref.set(body) : ref.delete();
      }).then(function(){ setStatus(); }, function(){ setStatus('Salvataggio nel tuo account non riuscito: segni salvati in questo browser'); });
    }, 700);
  }

  /* ---- sorgenti: blocchi della dispensa raggruppati per lezione e sezione ---- */
  function sources(){
    var out = [];
    document.querySelectorAll('#main .disp[data-hl]').forEach(function(disp){
      var L = disp.getAttribute('data-hl').split('-')[0];
      var info = (window.LESSONS||[]).filter(function(x){ return x.id === L; })[0];
      var lesson = info ? 'L' + info.num + ' · ' + info.h1 : L, sec = null;
      Array.prototype.forEach.call(disp.children, function(el, bi){
        el.setAttribute('data-bi', bi);
        if (el.tagName === 'H3' || !sec) { sec = {L:L, lesson:lesson, title: el.tagName === 'H3' ? el.textContent : 'Introduzione', els:[]}; out.push(sec); }
        sec.els.push(el);
      });
    });
    return out;
  }
  /* impagina: ogni sezione inizia una pagina nuova; i blocchi riempiono la pagina finché c'è spazio;
     elenchi lunghi vengono spezzati per voci; un blocco più alto di una pagina viene rimpicciolito in show() */
  function paginate(secs){
    var meas = document.createElement('div');
    meas.className = 'dr-content disp dr-measure';
    meas.style.cssText = 'position:absolute;left:-99999px;top:0;visibility:hidden;width:' + PW + 'px;padding:' + PAD + 'px;font-size:' + (17 * ZSTEPS[zi] * (FMT === 't' ? 0.94 : 1)) + 'px';
    meas.style.setProperty('--imgmax', Math.round((PH - 2 * PAD) * 0.62) + 'px');
    paper.appendChild(meas);
    var pages = [], perL = {};
    function newPage(sec){ var k = perL[sec.L] || 0; perL[sec.L] = k + 1; var pg = {L:sec.L, k:k, lesson:sec.lesson, title:sec.title, nodes:[]}; pages.push(pg); return pg; }
    function reset(sec){ meas.innerHTML = ''; var kk = document.createElement('div'); kk.className = 'dr-kicker'; kk.textContent = sec.lesson + ' · ' + sec.title; meas.appendChild(kk); }
    function fits(){ return meas.scrollHeight <= PH; }
    secs.forEach(function(sec){
      var pg = newPage(sec); reset(sec);
      var queue = sec.els.map(function(e){ return e.cloneNode(true); });
      while (queue.length) {
        var n = queue.shift();
        meas.appendChild(n);
        if (fits()) { pg.nodes.push(n); continue; }
        meas.removeChild(n);
        if (splittable(n)) {
          var head = n.cloneNode(false), items = Array.prototype.slice.call(n.children), moved = 0, total = items.length, start0 = parseInt(n.getAttribute('start') || '1', 10);
          meas.appendChild(head);
          while (items.length) { head.appendChild(items[0]); if (!fits()) { head.removeChild(items[0]); break; } items.shift(); moved++; }
          if (!moved && !pg.nodes.length) { head.appendChild(items.shift()); moved = 1; }
          if (moved) pg.nodes.push(head); else meas.removeChild(head);
          if (items.length) {
            var rest = n.cloneNode(false); items.forEach(function(x){ rest.appendChild(x); });
            if (rest.tagName === 'OL') rest.setAttribute('start', start0 + total - items.length);
            queue.unshift(rest); pg = newPage(sec); reset(sec);
          }
          continue;
        }
        if (!pg.nodes.length) { pg.nodes.push(n); if (queue.length) { pg = newPage(sec); reset(sec); } continue; }
        // niente titoletti orfani in fondo alla pagina: il titolo va con il suo contenuto
        var carry = [];
        while (pg.nodes.length > 1 && /^H[3-6]$/.test(pg.nodes[pg.nodes.length - 1].tagName)) carry.unshift(pg.nodes.pop());
        pg = newPage(sec); reset(sec); queue.unshift(n); for (var ci = carry.length - 1; ci >= 0; ci--) queue.unshift(carry[ci]);
      }
    });
    paper.removeChild(meas);
    return pages.filter(function(p){ return p.nodes.length; });
  }
  function splittable(n){ return (n.tagName === 'UL' || n.tagName === 'OL' || (n.classList && n.classList.contains('watch'))) && n.children.length > 1; }
  function pickFormat(){
    var w = stage ? stage.clientWidth : window.innerWidth, h = stage ? stage.clientHeight : window.innerHeight;
    var f = (w / Math.max(1, h)) >= 1.05 ? 'w' : 't';
    FMT = f; PW = FORMATS[f].W; PH = FORMATS[f].H; PAD = f === 'w' ? 44 : 28;
  }
  function repaginate(keepPage){
    pickFormat();
    st.pages = paginate(st.secs);
    var i = 0;
    if (keepPage) for (var j = 0; j < st.pages.length; j++) if (st.pages[j].L === keepPage.L && st.pages[j].title === keepPage.title) { i = j; break; }
    st.i = i; range.max = st.pages.length; show();
  }

  function sw(c, n, kind){ return '<button type="button" class="sw" data-' + kind + '="' + c + '" style="background:' + c + '" aria-label="' + n + '" title="' + n + '"></button>'; }
  function build(){
    root = document.createElement('div'); root.className = 'pv dr'; root.hidden = true;
    root.setAttribute('role','dialog'); root.setAttribute('aria-label','Presentazione della dispensa');
    root.innerHTML =
      '<div class="pv-bar">' +
        '<span class="pv-title" id="dr-title"></span>' +
        '<div class="pv-group"><button type="button" data-act="prev" aria-label="Pagina precedente">&#8592;</button><span class="pv-count" id="dr-count"></span><button type="button" data-act="next" aria-label="Pagina successiva">&#8594;</button></div>' +
        '<div class="pv-group"><button type="button" data-tool="none" title="Puntatore: puoi anche selezionare il testo per evidenziarlo (V)">Puntatore</button><button type="button" data-tool="pen" title="Penna (P)">Penna</button>' + PEN.map(function(c){ return sw(c[0], 'Penna ' + c[1].toLowerCase(), 'pen'); }).join('') + '</div>' +
        '<div class="pv-group"><button type="button" data-tool="hl" title="Evidenziatore a mano libera (H)">Evidenzia</button>' + HLC.map(function(c){ return sw(c[0], 'Evidenziatore ' + c[1].toLowerCase(), 'hl'); }).join('') + '<button type="button" data-tool="line" title="Sottolinea con una riga dritta (U)">Sottolinea</button></div>' +
        '<div class="pv-group"><button type="button" data-tool="eraser" title="Gomma (E)">Gomma</button><button type="button" data-act="undo" title="Annulla (Cmd/Ctrl+Z)">Annulla</button><button type="button" data-act="clear" title="Cancella i segni di questa pagina">Pulisci pagina</button></div>' +
        '<div class="pv-group"><button type="button" data-act="zoomout" aria-label="Testo più piccolo" title="Testo più piccolo">A−</button><button type="button" data-act="zoomin" aria-label="Testo più grande" title="Testo più grande">A+</button></div>' +
 '<div class="pv-group"><button type="button" class="dr-vbtn" data-act="video" title="Videolezione: una voce spiega la dispensa pagina per pagina (barra spaziatrice)">Videolezione</button></div>' +
        '<span class="pv-spacer"></span>' +
        '<button type="button" data-act="fs" title="Schermo intero (F)">Schermo intero</button>' +
        '<button type="button" data-act="close" title="Chiudi (Esc)">Chiudi</button>' +
      '</div>' +
      '<div class="dr-stage" id="dr-stage"><div class="dr-paper" id="dr-paper"><div class="dr-content disp" id="dr-content"></div><canvas id="dr-canvas"></canvas></div></div>' +
      '<div class="dr-vbar" id="dr-vbar" hidden>' +
        '<div class="dr-vctl"><button type="button" data-v="prev" aria-label="Segmento precedente" title="Segmento precedente">&#9198;</button><button type="button" data-v="play" class="dr-vplay" aria-label="Riproduci o pausa" title="Riproduci / pausa (barra spaziatrice)">&#9654;</button><button type="button" data-v="next" aria-label="Segmento successivo" title="Segmento successivo">&#9197;</button>' +
        '<span class="dr-vrates">' + [0.5, 1, 1.5, 2].map(function(r){ return '<button type="button" data-rate="' + r + '">' + String(r).replace('.', ',') + 'x</button>'; }).join('') + '</span>' +
        '<select id="dr-voice" aria-label="Voce"></select><span class="dr-vpos" id="dr-vpos"></span><button type="button" data-v="stop" title="Chiudi la videolezione">Chiudi video</button></div>' +
        '<div class="dr-vtl"><select id="dr-vles" aria-label="Lezione"></select><select id="dr-vchap" aria-label="Capitolo"></select><input type="range" id="dr-vseek" min="0" max="0" value="0" aria-label="Posizione nella videolezione"><span class="dr-vtime" id="dr-vtime"></span><button type="button" id="dr-vres" hidden></button></div>' +
        '<div class="dr-cap" id="dr-cap" aria-live="polite"></div>' +
      '</div>' +
      '<div class="pv-foot"><span class="pv-status" id="dr-status"></span><input type="range" id="dr-range" min="1" max="1" value="1" aria-label="Vai alla pagina"><span class="keys">&#8592; &#8594; pagina · P penna · H evidenzia · U sottolinea · E gomma · V puntatore · F schermo intero · Esc chiudi</span></div>';
    document.body.appendChild(root);
    stage = root.querySelector('#dr-stage'); paper = root.querySelector('#dr-paper'); content = root.querySelector('#dr-content');
    canvas = root.querySelector('#dr-canvas'); ctx = canvas.getContext('2d');
    countEl = root.querySelector('#dr-count'); range = root.querySelector('#dr-range'); titleEl = root.querySelector('#dr-title');
    root.addEventListener('click', function(e){
      var b = e.target.closest('button'); if (!b || !root.querySelector('.pv-bar').contains(b)) return;
      var a = b.dataset.act;
      if (a === 'prev') go(st.i - 1); else if (a === 'next') go(st.i + 1);
      else if (a === 'close') close(); else if (a === 'fs') fsToggle(root, b); else if (a === 'undo') undo(); else if (a === 'clear') clearPage();
      else if (a === 'video') V.toggleBar();
      else if (a === 'zoomin') zoom(1); else if (a === 'zoomout') zoom(-1);
      else if (b.dataset.tool) setTool(b.dataset.tool);
      else if (b.dataset.pen) { st.pen = b.dataset.pen; setTool(st.tool === 'line' ? 'line' : 'pen'); }
      else if (b.dataset.hl) { st.hl = b.dataset.hl; setTool('hl'); }
    });
    range.addEventListener('input', function(){ if (V.playing) V.pause(); go(+range.value - 1); });
    V.bind();
    window.addEventListener('resize', function(){ if (!st.open) return; var old = FMT; pickFormat(); if (FMT !== old) repaginate(st.pages[st.i]); else layout(); });
    bindDraw();
    document.addEventListener('keydown', onKey);
    var fb = root.querySelector('[data-act="fs"]'); ['fullscreenchange','webkitfullscreenchange'].forEach(function(ev){ document.addEventListener(ev, function(){ fsSync(fb); if (st.open) setTimeout(function(){ var old = FMT; pickFormat(); if (FMT !== old) repaginate(st.pages[st.i]); else layout(); }, 80); }); });
    setStatus();
  }
  try { var z = parseInt(localStorage.getItem('cvdr:zi'), 10); if (z >= 0 && z < ZSTEPS.length) zi = z; } catch(e){}
  function zoom(d){
    var nz = Math.max(0, Math.min(ZSTEPS.length - 1, zi + d)); if (nz === zi) return;
    var cur = st.pages[st.i]; zi = nz; try { localStorage.setItem('cvdr:zi', zi); } catch(e){}
    repaginate(cur);
  }
  function setTool(t){
    st.tool = t;
    root.querySelectorAll('[data-tool]').forEach(function(b){ b.setAttribute('aria-pressed', b.dataset.tool === t ? 'true' : 'false'); });
    root.querySelectorAll('[data-pen]').forEach(function(b){ b.setAttribute('aria-pressed', (t === 'pen' || t === 'line') && b.dataset.pen === st.pen ? 'true' : 'false'); });
    root.querySelectorAll('[data-hl]').forEach(function(b){ b.setAttribute('aria-pressed', t === 'hl' && b.dataset.hl === st.hl ? 'true' : 'false'); });
    paper.classList.toggle('drawing', t === 'pen' || t === 'hl' || t === 'line');
    paper.classList.toggle('erasing', t === 'eraser');
  }

  function open(startL, startBi){
    if (!root) build();
    st.secs = sources(); if (!st.secs.length) return;
    st.secs.forEach(function(sc){ if (!loaded[sc.L]) { loaded[sc.L] = true; loadCloud(sc.L); } });
    st.open = true; root.hidden = false; document.documentElement.style.overflow = 'hidden';
    setTool('none');
    pickFormat();
    st.pages = paginate(st.secs); range.max = st.pages.length;
    st.i = 0;
    if (startL) for (var j = 0; j < st.pages.length; j++) if (st.pages[j].L === startL) { st.i = j; break; }
    if (startL && startBi != null) for (var j2 = 0; j2 < st.pages.length; j2++) { var pp = st.pages[j2]; if (pp.L !== startL) continue; if (pp.nodes.some(function(n){ return +n.getAttribute('data-bi') >= startBi; })) { st.i = j2; break; } }
    show();
  }
  function close(){
    if (!st.open) return; if (document.fullscreenElement || document.webkitFullscreenElement) { try { (document.exitFullscreen || document.webkitExitFullscreen).call(document); } catch(e){} }
    V.stop(true);
    st.open = false; root.hidden = true; document.documentElement.style.overflow = '';
    setTimeout(floatSync, 50);

    if (window.HL) HL.refresh();
  }
  function go(i){ i = Math.max(0, Math.min(st.pages.length - 1, i)); if (i === st.i && content.childNodes.length) return; st.i = i; show(); }
  function show(){
    var p = st.pages[st.i]; if (!p) return;
    titleEl.textContent = p.lesson;
    countEl.textContent = (st.i + 1) + ' / ' + st.pages.length; range.value = st.i + 1;
    content.innerHTML = '';
    content.style.fontSize = (17 * ZSTEPS[zi] * (FMT === 't' ? 0.94 : 1)) + 'px';
    content.style.setProperty('--imgmax', Math.round((PH - 2 * PAD) * 0.62) + 'px');
    content.style.padding = PAD + 'px';
    var kk = document.createElement('div'); kk.className = 'dr-kicker'; kk.textContent = p.lesson + ' · ' + p.title; content.appendChild(kk);
    p.nodes.forEach(function(n){ content.appendChild(n.cloneNode(true)); });
    content.setAttribute('data-hl', key(p));
    content.querySelectorAll('mark.hl').forEach(function(m){ var par = m.parentNode; while (m.firstChild) par.insertBefore(m.firstChild, m); par.removeChild(m); });
    content.normalize();
    if (window.HL) HL.shown();
    V.mark();
    content.querySelectorAll('img').forEach(function(im){ if (!im.complete) im.addEventListener('load', fitContent, {once:true}); });
    layout();
  }
  function fitContent(){
    // un blocco troppo alto per la pagina viene rimpicciolito, la pagina resta della stessa misura
    content.style.transform = ''; content.style.width = PW + 'px';
    var h = content.scrollHeight;
    if (h > PH) { var f = PH / h; content.style.transformOrigin = '0 0'; content.style.transform = 'scale(' + f + ')'; content.style.width = (PW / f) + 'px'; }
  }
  function layout(){
    if (!st.open) return;
    var sw_ = stage.clientWidth - 24, sh_ = stage.clientHeight - 24;
    var s = Math.min(sw_ / PW, sh_ / PH);
    paper.style.width = PW + 'px'; paper.style.height = PH + 'px';
    paper.style.transform = 'scale(' + s + ')';
    paper.style.left = Math.round((stage.clientWidth - PW * s) / 2) + 'px';
    paper.style.top = Math.round((stage.clientHeight - PH * s) / 2) + 'px';
    var sizer = root.querySelector('.dr-sizer'); if (sizer) sizer.remove();
    st.scale = s;
    fitContent();
    var dpr = window.devicePixelRatio || 1, q = Math.min(3, dpr * s);
    canvas.width = Math.round(PW * q); canvas.height = Math.round(PH * q);
    canvas.style.width = PW + 'px'; canvas.style.height = PH + 'px';
    st.q = q; redraw();
  }
  function drawStroke(s){
    var p = s.p, q = st.q; if (!p || p.length < 2) return;
    ctx.save(); ctx.lineCap = s.t === 'hl' ? 'butt' : 'round'; ctx.lineJoin = 'round';
    ctx.strokeStyle = s.c; ctx.globalAlpha = s.t === 'hl' ? 0.45 : 1; ctx.lineWidth = s.w * q;
    ctx.beginPath(); ctx.moveTo(p[0]*q, p[1]*q);
    if (p.length === 2) ctx.lineTo(p[0]*q + 0.1, p[1]*q);
    for (var k = 2; k < p.length - 2; k += 2) { var mx = (p[k] + p[k+2]) / 2, my = (p[k+1] + p[k+3]) / 2; ctx.quadraticCurveTo(p[k]*q, p[k+1]*q, mx*q, my*q); }
    if (p.length >= 4) ctx.lineTo(p[p.length-2]*q, p[p.length-1]*q);
    ctx.stroke(); ctx.restore();
  }
  function redraw(){
    if (!ctx || !st.open) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    strokes(st.pages[st.i]).forEach(drawStroke); if (st.cur) drawStroke(st.cur);
  }
  function pos(e){ var r = canvas.getBoundingClientRect(), s = st.scale; return [Math.round((e.clientX - r.left) / s * 10) / 10, Math.round((e.clientY - r.top) / s * 10) / 10]; }
  function pushUndo(op){ var k = key(st.pages[st.i]); (st.undo[k] = st.undo[k] || []).push(op); }
  function eraseAt(q){
    var list = strokes(st.pages[st.i]), rad = 12;
    for (var i = list.length - 1; i >= 0; i--) {
      var p = list[i].p, hit = false;
      for (var k = 0; k < p.length; k += 2) { var dx = p[k] - q[0], dy = p[k+1] - q[1]; if (dx*dx + dy*dy < rad*rad) { hit = true; break; } }
      if (!hit && list[i].t === 'line' && p.length === 4) {
        var vx = p[2]-p[0], vy = p[3]-p[1], L2 = vx*vx + vy*vy || 1e-9, t = Math.max(0, Math.min(1, ((q[0]-p[0])*vx + (q[1]-p[1])*vy) / L2));
        var ex = p[0] + t*vx - q[0], ey = p[1] + t*vy - q[1]; hit = ex*ex + ey*ey < rad*rad;
      }
      if (hit) { pushUndo({t:'erase', s:list.splice(i,1)[0], i:i}); changed(st.pages[st.i]); redraw(); return; }
    }
  }
  function bindDraw(){
    var down = false;
    canvas.addEventListener('pointerdown', function(e){
      if (st.tool === 'none') return;
      e.preventDefault(); canvas.setPointerCapture(e.pointerId); down = true;
      var q = pos(e);
      if (st.tool === 'eraser') { eraseAt(q); return; }
      st.cur = {t:st.tool, c: st.tool === 'hl' ? st.hl : st.pen, w: W[st.tool], p:[q[0], q[1]]};
      if (st.tool === 'line') st.cur.p.push(q[0], q[1]);
      redraw();
    });
    canvas.addEventListener('pointermove', function(e){
      if (!down) return;
      if (st.tool === 'eraser') { eraseAt(pos(e)); return; }
      if (!st.cur) return;
      if (st.cur.t === 'line') { var q = pos(e), p = st.cur.p; if (Math.abs(q[1]-p[1]) < Math.abs(q[0]-p[0]) * 0.12) q[1] = p[1]; p[2] = q[0]; p[3] = q[1]; }
      else (e.getCoalescedEvents ? e.getCoalescedEvents() : [e]).forEach(function(ev){
        var q = pos(ev), p = st.cur.p; if (Math.abs(q[0]-p[p.length-2]) + Math.abs(q[1]-p[p.length-1]) > 1.2) p.push(q[0], q[1]);
      });
      requestAnimationFrame(redraw);
    });
    function end(){
      if (!down) return; down = false;
      if (st.cur) { var s = st.cur; st.cur = null;
        if (s.t !== 'line' || Math.abs(s.p[2]-s.p[0]) + Math.abs(s.p[3]-s.p[1]) > 4) { strokes(st.pages[st.i]).push(s); pushUndo({t:'add'}); changed(st.pages[st.i]); }
        redraw(); }
    }
    canvas.addEventListener('pointerup', end); canvas.addEventListener('pointercancel', end);
  }
  function undo(){
    var p = st.pages[st.i], u = st.undo[key(p)], list = strokes(p); if (!u || !u.length) return;
    var op = u.pop();
    if (op.t === 'add') list.pop(); else if (op.t === 'erase') list.splice(op.i, 0, op.s); else if (op.t === 'clear') Array.prototype.push.apply(list, op.s);
    changed(p); redraw();
  }
  function clearPage(){ var p = st.pages[st.i], list = strokes(p); if (!list.length) return; pushUndo({t:'clear', s:list.splice(0, list.length)}); changed(p); redraw(); }
  function onKey(e){
    if (!st.open) return;
    var tag = (e.target.tagName || '').toLowerCase();
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'z') { e.preventDefault(); undo(); return; }
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    if (tag === 'input') return;
    var k = e.key;
    if (k === ' ' && V.on) { e.preventDefault(); V.playPause(); return; }
    if (V.on && V.playing && /^(ArrowRight|ArrowLeft|PageDown|PageUp)$/.test(k)) V.pause();
    if (k === 'ArrowRight' || k === 'PageDown') { e.preventDefault(); go(st.i + 1); }
    else if (k === 'ArrowLeft' || k === 'PageUp') { e.preventDefault(); go(st.i - 1); }
    else if (k === 'Escape') { if (st.tool !== 'none') setTool('none'); else close(); }
    else if (k === 'f' || k === 'F') fsToggle(root, root.querySelector('[data-act="fs"]'));
    else if (k === 'p' || k === 'P') setTool('pen'); else if (k === 'h' || k === 'H') setTool('hl');
    else if (k === 'u' || k === 'U') setTool('line'); else if (k === 'e' || k === 'E') setTool('eraser'); else if (k === 'v' || k === 'V') setTool('none');
  }


  /* ---- Videolezione: copione parlato (lessons/voce_L<n>.json) letto con la sintesi vocale del dispositivo,
     sincronizzato con le pagine; ogni segmento è legato a un blocco della dispensa (data-bi) ---- */
  var V = (function(){
    var SS = window.speechSynthesis, cache = {}, tok = 0;
    var me = {on:false, playing:false, L:null, segs:null, si:0, k:0, sents:[], rate:1, voice:null};
    var LEX = [[/\bfeatures\b/gi,'fìciurs'],[/\bfeature\b/gi,'fìciur'],[/\bmatching\b/gi,'mècing'],[/\bmatch\b/gi,'mècc'],
      [/\bkeypoints?\b/gi,'kìpoint'],[/\bblur\b/gi,'blèr'],[/\baliasing\b/gi,'èliasing'],[/\bframes?\b/gi,'frèim'],
      [/\blayers?\b/gi,'lèier'],[/\bwarping\b/gi,'uòrping'],[/\bblending\b/gi,'blènding'],[/\bpooling\b/gi,'pùling'],
      [/\bringing\b/gi,'rìnghing'],[/\btemplate\b/gi,'tèmplit'],[/\bedges?\b/gi,'ègg'],[/\bdeep learning\b/gi,'dip lèrning'],[/\bnotebook\b/gi,'nòtbuc']];
    try { var r0 = parseFloat(localStorage.getItem('cvv:rate')); if ([0.5, 1, 1.5, 2].indexOf(r0) >= 0) me.rate = r0; } catch(e){}
    function $(id){ return root && root.querySelector('#' + id); }
    function itVoices(){ return SS ? SS.getVoices().filter(function(v){ return /^it/i.test(v.lang); }) : []; }
    function score(v){ var n = v.name; return (/premium|enhanced|avanzat|migliorat|neural|natural|online/i.test(n) ? 4 : 0) + (/google/i.test(n) ? 2 : 0) + (/alice|federica|luca|elsa|isabella|diego|emma|giuseppe/i.test(n) ? 1 : 0) + (v.localService ? 0 : 1); }
    function fillVoices(){
      var sel = $('dr-voice'); if (!sel) return;
      var vs = itVoices().sort(function(a, b){ return score(b) - score(a); }), saved = null;
      try { saved = localStorage.getItem('cvv:voice'); } catch(e){}
      if (!vs.length) { sel.innerHTML = '<option>Nessuna voce italiana</option>'; sel.disabled = true; me.voice = null; return; }
      sel.disabled = false;
      sel.innerHTML = vs.map(function(v, i){ return '<option value="' + i + '">' + v.name.replace(/</g, '') + '</option>'; }).join('');
      var idx = 0; vs.forEach(function(v, i){ if (v.name === saved) idx = i; });
      sel.value = String(idx); me.voice = vs[idx]; me._vs = vs;
    }
    function setRate(r){
      me.rate = r; try { localStorage.setItem('cvv:rate', r); } catch(e){}
      root.querySelectorAll('[data-rate]').forEach(function(b){ b.setAttribute('aria-pressed', +b.dataset.rate === r ? 'true' : 'false'); });
      if (me.playing) { speak(); }
    }
    function load(L){
      if (cache[L]) return Promise.resolve(cache[L]);
      return fetch('lessons/voce_' + L + '.json').then(function(r){ if (!r.ok) throw 0; return r.json(); }).then(function(d){ cache[L] = d; return d; });
    }
    function split(t){ return (t.match(/[^.!?…]+[.!?…]+[»"')]*\s*|[^.!?…]+$/g) || [t]).map(function(x){ return x.trim(); }).filter(Boolean); }
    function pageOf(L, b){
      for (var j = 0; j < st.pages.length; j++) { var p = st.pages[j]; if (p.L !== L) continue; for (var q = 0; q < p.nodes.length; q++) if (+p.nodes[q].getAttribute('data-bi') === b) return j; }
      return -1;
    }
    function firstOnPage(i){
      var p = st.pages[i]; if (!p || !me.segs) return 0;
      var bis = p.nodes.map(function(n){ return +n.getAttribute('data-bi'); });
      for (var s = 0; s < me.segs.length; s++) if (bis.indexOf(me.segs[s].b) >= 0) return s;
      var mx = Math.max.apply(null, bis);
      for (s = 0; s < me.segs.length; s++) if (me.segs[s].b > mx) return s;
      return 0;
    }
    function caption(){
      var cap = $('dr-cap'); if (!cap) return;
      cap.innerHTML = me.sents.map(function(x, i){ var e = x.replace(/&/g, '&amp;').replace(/</g, '&lt;'); return i === me.k ? '<b>' + e + '</b>' : '<span>' + e + '</span>'; }).join(' ');
      var pos = $('dr-vpos'); if (pos && me.segs) pos.textContent = (me.si + 1) + ' / ' + me.segs.length;
      if (me.segs && me.cum) {
        var sk = $('dr-vseek'); sk.max = me.segs.length - 1; if (!me._seeking) sk.value = me.si;
        $('dr-vtime').textContent = mmss(me.cum[me.si] / me.rate) + ' / ' + mmss(me.cum[me.segs.length] / me.rate);
        var ch = $('dr-vchap'), cv = 0; (me.chaps || []).forEach(function(c, ci){ if (c.s <= me.si) cv = ci; }); if (ch.options.length) ch.value = String(cv);
        var ls = $('dr-vles'); if (ls.querySelector('option[value="' + me.L + '"]')) ls.value = me.L;
        var rb = $('dr-vres'), sv = me.saved || 0;
        if (sv > me.si + 2 && sv < me.segs.length) { rb.hidden = false; rb.textContent = 'Riprendi da ' + mmss(me.cum[sv] / me.rate); } else rb.hidden = true;
      }
      var pb = root.querySelector('.dr-vplay'); if (pb) { pb.innerHTML = me.playing ? '&#10073;&#10073;' : '&#9654;'; pb.setAttribute('aria-pressed', me.playing ? 'true' : 'false'); }
    }
    me.mark = function(){
      if (!content) return;
      content.querySelectorAll('.dr-now').forEach(function(n){ n.classList.remove('dr-now'); });
      if (!me.on || !me.segs || !me.segs[me.si]) return;
      var p = st.pages[st.i]; if (!p || p.L !== me.L) return;
      content.querySelectorAll('[data-bi="' + me.segs[me.si].b + '"]').forEach(function(n){ n.classList.add('dr-now'); });
    };
    function seg(i, autoplay){
      if (!me.segs) return;
      if (i >= me.segs.length) {
        var nx = nextLesson(me.L);
        if (nx && autoplay) { useLesson(nx, 0, true); return; }
        me.pause(); me.si = me.segs.length - 1; me.sents = ['Fine della videolezione.']; me.k = 0; caption(); return;
      }
      me.si = Math.max(0, i); me.k = 0; me.sents = split(me.segs[me.si].t);
      try { localStorage.setItem('cvv:pos:' + me.L, me.si); } catch(e){}
      var j = pageOf(me.L, me.segs[me.si].b);
      if (j >= 0 && j !== st.i) go(j); else me.mark();
      caption();
      if (autoplay) speak();
    }
    function say(t){ var x = t; LEX.forEach(function(l){ x = x.replace(l[0], l[1]); }); return x; }
    function speak(){
      if (!SS) return;
      var my = ++tok; SS.cancel();
      me.playing = true; caption();
      var u = new SpeechSynthesisUtterance(say(me.sents[me.k] || ''));
      u.lang = 'it-IT'; if (me.voice) u.voice = me.voice; u.rate = me.rate;
      u.onend = function(){
        if (my !== tok || !me.playing) return;
        if (me.k + 1 < me.sents.length) { me.k++; caption(); speak(); }
        else setTimeout(function(){ if (my === tok && me.playing) seg(me.si + 1, true); }, 350 / me.rate);
      };
      u.onerror = function(e){ if (my !== tok) return; if (e && (e.error === 'interrupted' || e.error === 'canceled')) return; me.playing = false; caption(); };
      // Chrome si blocca dopo ~15 s di parlato continuo: un resume periodico lo tiene sveglio
      SS.speak(u);
      clearInterval(me._ka); me._ka = setInterval(function(){ if (!me.playing) { clearInterval(me._ka); return; } if (SS.paused) SS.resume(); }, 5000);
    }
    me.pause = function(){ me.playing = false; tok++; if (SS) SS.cancel(); caption(); };
    me.playPause = function(){
      if (me.playing) { me.pause(); return; }
      var p = st.pages[st.i];
      if (p && (p.L !== me.L || pageOf(me.L, me.segs[me.si].b) !== st.i)) { start(); return; }
      speak();
    };
    me.unlock = function(){ try { if (SS) { var u = new SpeechSynthesisUtterance(' '); u.volume = 0; SS.speak(u); } } catch(e){} };
    function mmss(sec){ sec = Math.round(sec); return Math.floor(sec / 60) + ':' + ('0' + (sec % 60)).slice(-2); }
    var WPS = 150 / 60; // parole al secondo a 1x (stima)
    function lessonsInReader(){ var out = []; st.pages.forEach(function(p){ if (out.indexOf(p.L) < 0) out.push(p.L); }); return out; }
    function nextLesson(L){ var ls = lessonsInReader(), k = ls.indexOf(L); return k >= 0 && k + 1 < ls.length ? ls[k + 1] : null; }
    function lessonName(L){ var info = (window.LESSONS || []).filter(function(x){ return x.id === L; })[0]; return info ? 'L' + info.num + ' · ' + info.h1 : L; }
    function fillLessons(){
      var sel = $('dr-vles'), ls = lessonsInReader();
      sel.innerHTML = ls.map(function(L){ return '<option value="' + L + '">' + lessonName(L).replace(/</g, '') + '</option>'; }).join('');
      sel.hidden = ls.length < 2;
    }
    function prepare(L, segs){
      try { me.saved = parseInt(localStorage.getItem('cvv:pos:' + L), 10) || 0; } catch(e){ me.saved = 0; }
      me.L = L; me.segs = segs; me.cum = [0];
      segs.forEach(function(x, i){ me.cum.push(me.cum[i] + x.t.split(/\s+/).length / WPS + 0.35); });
      me.chaps = []; var last = null;
      segs.forEach(function(x, i){ var j = pageOf(L, x.b), t = j >= 0 ? st.pages[j].title : ''; if (t && t !== last) { me.chaps.push({s:i, t:t}); last = t; } });
      $('dr-vchap').innerHTML = me.chaps.map(function(c, ci){ return '<option value="' + ci + '">' + c.t.replace(/</g, '') + '</option>'; }).join('');
      fillLessons();
    }
    function useLesson(L, i, play, fromBi){
      $('dr-cap').textContent = 'Carico il copione…';
      return load(L).then(function(segs){
        prepare(L, segs);
        if (fromBi != null) { i = segs.length - 1; for (var s2 = 0; s2 < segs.length; s2++) if (segs[s2].b >= fromBi) { i = s2; break; } }
        seg(i == null ? 0 : i, play);
      }, function(){ me.playing = false; $('dr-cap').textContent = 'La videolezione di ' + lessonName(L) + ' non è ancora pronta.'; });
    }
    /* parte dal punto in cui sei: dal blocco indicato, altrimenti dalla pagina aperta */
    function start(fromBi){
      if (!SS) { showBar(); $('dr-cap').textContent = 'Questo browser non ha la sintesi vocale. Prova con Safari o Chrome.'; return; }
      var p = st.pages[st.i]; if (!p) return;
      showBar(); fillVoices();
      var L = p.L;
      if (fromBi != null) { useLesson(L, null, true, fromBi); return; }
      load(L).then(function(segs){
        prepare(L, segs);
        seg(firstOnPage(st.i), true);
      }, function(){ me.playing = false; $('dr-cap').textContent = 'La videolezione di ' + lessonName(L) + ' non è ancora pronta.'; });
    }
    me.start = start;
    function showBar(){ if (me.on) return; me.on = true; $('dr-vbar').hidden = false; root.classList.add('dr-video'); root.querySelector('.dr-vbtn').setAttribute('aria-pressed', 'true'); setRate(me.rate); layout(); }
    me.stop = function(silent){
      if (!root) return; me.pause(); me.on = false; var vb = $('dr-vbar'); if (vb) vb.hidden = true;
      root.classList.remove('dr-video'); var vbtn = root.querySelector('.dr-vbtn'); if (vbtn) vbtn.setAttribute('aria-pressed', 'false');
      if (!silent) { me.mark(); layout(); }
    };
    me.toggleBar = function(){ if (me.on) me.stop(); else { me.unlock(); start(); } };
    me.bind = function(){
      if (SS && SS.addEventListener) SS.addEventListener('voiceschanged', fillVoices);
      $('dr-vbar').addEventListener('click', function(e){
        var b = e.target.closest('button'); if (!b) return;
        if (b.dataset.rate) { setRate(+b.dataset.rate); return; }
        var a = b.dataset.v;
        if (a === 'play') me.playPause();
        else if (a === 'prev') seg(me.si - 1, me.playing);
        else if (a === 'next') seg(me.si + 1, me.playing);
        else if (a === 'stop') me.stop();
      });
      $('dr-vres').addEventListener('click', function(){ var sv = me.saved; me.saved = 0; seg(sv, true); });
      var sk = $('dr-vseek');
      sk.addEventListener('input', function(){ me._seeking = true; if (me.segs && me.cum) $('dr-vtime').textContent = mmss(me.cum[+sk.value] / me.rate) + ' / ' + mmss(me.cum[me.segs.length] / me.rate); });
      sk.addEventListener('change', function(){ me._seeking = false; var was = me.playing || me._wasPlaying; seg(+sk.value, was); });
      sk.addEventListener('pointerdown', function(){ me._wasPlaying = me.playing; });
      $('dr-vchap').addEventListener('change', function(e){ var c = me.chaps && me.chaps[+e.target.value]; if (c) seg(c.s, me.playing); });
      $('dr-vles').addEventListener('change', function(e){ var L = e.target.value; if (L && L !== me.L) useLesson(L, 0, me.playing || true); });
      $('dr-voice').addEventListener('change', function(e){
        var v = me._vs && me._vs[+e.target.value]; if (!v) return; me.voice = v;
        try { localStorage.setItem('cvv:voice', v.name); } catch(err){}
        if (me.playing) speak();
      });
      // un clic su un paragrafo durante la videolezione fa ripartire la voce da lì
      content.addEventListener('dblclick', function(e){
        if (!me.on || !me.segs) return; var n = e.target.closest('[data-bi]'); if (!n) return;
        var b = +n.getAttribute('data-bi'); for (var s = 0; s < me.segs.length; s++) if (me.segs[s].b >= b) { seg(s, true); return; }
      });
    };
    return me;
  })();

  document.addEventListener('click', function(e){
    var b = e.target.closest('#main [data-present-disp]'); if (!b) return;
    if (b.hasAttribute('data-video')) V.unlock();
    open(b.getAttribute('data-present-disp') || null);
    if (b.hasAttribute('data-fs') && root) fsToggle(root, root.querySelector('[data-act="fs"]'));
    if (b.hasAttribute('data-video')) V.start(b.hasAttribute('data-bi') ? +b.getAttribute('data-bi') : null);
  });
  /* pulsante flottante: avvia la videolezione dal punto della dispensa che stai leggendo */
  var flt = null;
  function visibleBlock(){
    var best = null;
    document.querySelectorAll('#main .disp[data-hl]').forEach(function(d){
      if (best) return;
      var r = d.getBoundingClientRect(); if (r.bottom < 120 || r.top > window.innerHeight - 80) return;
      var kids = d.children;
      for (var i = 0; i < kids.length; i++) { var kr = kids[i].getBoundingClientRect(); if (kr.bottom > 110) { best = {L: d.getAttribute('data-hl').split('-')[0], bi: i}; break; } }
    });
    return best;
  }
  function floatSync(){
    if (!flt) return;
    var v = visibleBlock(); flt.hidden = !v || (root && !root.hidden);
  }
  function floatInit(){
    if (flt) { floatSync(); return; }
    flt = document.createElement('button'); flt.type = 'button'; flt.className = 'dr-float'; flt.hidden = true;
    flt.innerHTML = '&#9654; Videolezione da qui'; flt.title = 'Avvia la videolezione dal paragrafo che stai leggendo';
    document.body.appendChild(flt);
    flt.addEventListener('click', function(){
      var v = visibleBlock(); if (!v) return;
      V.unlock(); open(v.L, v.bi); V.start(v.bi); floatSync();
    });
    var tmo = null; window.addEventListener('scroll', function(){ if (tmo) return; tmo = setTimeout(function(){ tmo = null; floatSync(); }, 150); }, {passive:true});
    floatSync();
  }
  window.DR = {
    decorate: function(){
      floatInit();
      // pulsante "Presenta la dispensa" accanto al titolo di ogni dispensa e nella barra della lezione
      document.querySelectorAll('#main .disp[data-hl]').forEach(function(d){
        var L = d.getAttribute('data-hl').split('-')[0], sec = d.previousElementSibling;
        while (sec && !sec.classList.contains('sec')) sec = sec.previousElementSibling;
        if (sec && !sec.querySelector('[data-present-disp]')) {
          var b = document.createElement('button'); b.type = 'button'; b.className = 'btn-primary btn-sm'; b.setAttribute('data-present-disp', L); b.textContent = 'Presenta la dispensa';
          sec.appendChild(b);
          var bv = document.createElement('button'); bv.type = 'button'; bv.className = 'btn-primary btn-sm btn-ghost'; bv.setAttribute('data-present-disp', L); bv.setAttribute('data-video', '1'); bv.textContent = 'Guarda la videolezione';
          sec.appendChild(bv);
        }
      });
      var tools = document.querySelector('#main .lesson-tools');
      if (tools && !tools.querySelector('[data-present-disp]') && document.querySelector('#main .disp[data-hl]')) {
        var b2 = document.createElement('button'); b2.type = 'button'; b2.className = 'btn-primary'; b2.setAttribute('data-present-disp', '');
        b2.textContent = 'Presenta la dispensa'; tools.insertBefore(b2, tools.children[1] || null);
        var b3 = document.createElement('button'); b3.type = 'button'; b3.className = 'btn-primary btn-ghost'; b3.setAttribute('data-present-disp', ''); b3.setAttribute('data-fs', '1');
        b3.textContent = 'Dispensa a schermo intero'; tools.insertBefore(b3, b2.nextSibling);
        var b4 = document.createElement('button'); b4.type = 'button'; b4.className = 'btn-primary btn-ghost'; b4.setAttribute('data-present-disp', ''); b4.setAttribute('data-video', '1');
        b4.textContent = 'Videolezione'; tools.insertBefore(b4, b3.nextSibling);
      }
      var hero = document.querySelector('#main header.hero');
      if (hero && location.hash === '#dispensa' && !hero.querySelector('[data-present-disp]')) {
        var d3 = document.createElement('div'); d3.className = 'lesson-tools';
        d3.innerHTML = '<button type="button" class="btn-primary" data-present-disp="">Presenta la dispensa</button><button type="button" class="btn-primary btn-ghost" data-present-disp="" data-fs="1">Schermo intero</button><button type="button" class="btn-primary btn-ghost" data-present-disp="" data-video="1">Videolezione</button><span>Una sezione per pagina, a tutto schermo, con penna, evidenziatore e sottolineatura. Puoi anche selezionare il testo per evidenziarlo.</span>';
        hero.appendChild(d3);
        var ch = document.createElement('div'); ch.className = 'lesson-tools dr-vchips';
        var Ls = []; document.querySelectorAll('#main .disp[data-hl]').forEach(function(d){ Ls.push(d.getAttribute('data-hl').split('-')[0]); });
        ch.innerHTML = '<span>Videolezione di:</span>' + Ls.map(function(L){ var info = (window.LESSONS||[]).filter(function(x){ return x.id === L; })[0]; return '<button type="button" class="btn-primary btn-sm btn-ghost" data-present-disp="' + L + '" data-video="1" title="' + (info ? info.h1.replace(/"/g, '') : L) + '">' + (info ? 'L' + info.num : L) + '</button>'; }).join('');
        hero.appendChild(ch);
      }
    },
    close: close
  };
})();
