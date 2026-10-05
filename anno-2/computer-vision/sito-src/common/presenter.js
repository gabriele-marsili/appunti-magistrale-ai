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

  var HD = window.HD_URLS || {};          // lezione -> url del pacchetto slide ad alta risoluzione
  var hdCache = {}, hdLoading = {};
  var ann = {};                            // ann[L][n] = {strokes:[], updated:ms}
  var annLoaded = {};
  var store = {db:null, uid:null};
  var saveTimers = {}, saveChains = {};
  var st = {open:false, L:null, n:1, list:[], tool:'none', pen:'#C62828', hl:'#FFE34D', undo:{}, cur:null, notes:true};

  var PEN = [['#1F2A33','Nero'],['#C62828','Rosso'],['#1565C0','Blu']];
  var HL  = [['#FFE34D','Giallo'],['#7CE38B','Verde'],['#FF9CC6','Rosa']];
  var WIDTH = {pen:0.0024, line:0.0026, hl:0.02};

  /* ---------- archivio annotazioni ---------- */
  function lsKey(L,n){ return 'cvann:'+L+':'+n; }
  function lsGet(L,n){ try { var v = localStorage.getItem(lsKey(L,n)); return v ? JSON.parse(v) : null; } catch(e){ return null; } }
  function lsSet(L,n,v){ try { if (v && v.strokes.length) localStorage.setItem(lsKey(L,n), JSON.stringify(v)); else localStorage.removeItem(lsKey(L,n)); } catch(e){} }
  function col(){ return store.db.collection('data/users/' + store.uid); }

  function setStatus(msg){
    var el = document.getElementById('pv-status'); if (!el) return;
    el.textContent = msg || (store.db ? 'Annotazioni salvate nel tuo account' : 'Annotazioni salvate solo in questo browser');
  }

  function loadLocal(L){
    if (annLoaded[L]) return; annLoaded[L] = true; ann[L] = ann[L] || {};
    st.listFor = null;
    document.querySelectorAll('#main article.slide').forEach(function(a){
      var n = +a.getAttribute('data-n'); var v = lsGet(L,n); if (v) ann[L][n] = v;
    });
    if (store.db) loadCloud(L);
  }
  function loadCloud(L){
    col().where('lesson','==',L).get().then(function(snap){
      snap.docs.forEach(function(d){
        var b = d.data(); if (!b || b.kind) return;
        var loc = ann[L][b.n];
        if (!loc || (b.updated||0) >= (loc.updated||0)) { ann[L][b.n] = {strokes: b.strokes||[], updated: b.updated||0}; lsSet(L,b.n,ann[L][b.n]); }
      });
      // annotazioni fatte offline più recenti del cloud: le carico su
      Object.keys(ann[L]).forEach(function(n){
        var inCloud = snap.docs.some(function(d){ return d.data() && !d.data().kind && d.data().n == n && (d.data().updated||0) >= (ann[L][n].updated||0); });
        if (!inCloud && ann[L][n].strokes.length) queueCloud(L, +n);
      });
      markCards(L); if (st.open && st.L === L) redraw();
    }).catch(function(){ setStatus('Non riesco a leggere le annotazioni dal tuo account: uso quelle di questo browser'); });
  }
  function queueCloud(L,n){
    if (!store.db) return;
    var id = L + '-s' + n, key = id;
    var v = ann[L][n] || {strokes:[], updated:Date.now()};
    var body = {lesson:L, n:n, strokes:v.strokes, updated:v.updated};
    if (JSON.stringify(body).length > 240000) { setStatus('Troppe annotazioni su questa slide: salvate solo in questo browser'); return; }
    setStatus('Salvataggio…');
    saveChains[key] = (saveChains[key] || Promise.resolve()).then(function(){
      var ref = col().doc(id);
      return v.strokes.length ? ref.set(body) : ref.delete();
    }).then(function(){ setStatus(); }, function(e){
      setStatus(e && e.code === 'quota_exceeded' ? 'Spazio annotazioni esaurito: salvate solo in questo browser' : 'Salvataggio nel tuo account non riuscito: salvate in questo browser');
    });
  }
  function changed(L,n){
    var v = ann[L][n]; v.updated = Date.now(); lsSet(L,n,v); markCard(L,n);
    var k = L+':'+n; clearTimeout(saveTimers[k]);
    saveTimers[k] = setTimeout(function(){ queueCloud(L,n); }, 700);
  }
  function strokesOf(L,n){ ann[L] = ann[L] || {}; if (!ann[L][n]) ann[L][n] = {strokes:[], updated:0}; return ann[L][n].strokes; }

  (function initStore(){
    if (!window.claude || !window.claude.use) return;
    Promise.all([window.claude.use('db'), window.claude.use('user')]).then(function(r){
      var db = r[0], user = r[1]; if (!db || !user) return;
      return user.id().then(function(id){
        if (!id) return; store.db = db; store.uid = id; setStatus();
        Object.keys(annLoaded).forEach(loadCloud);
      });
    }).catch(function(){});
  })();

  /* ---------- segni sulle schede ---------- */
  function markCard(L,n){
    if (currentLesson() !== L) return;
    var a = document.getElementById('s'+n); if (!a) return;
    var num = a.querySelector('.num'); if (!num) return;
    var has = ann[L][n] && ann[L][n].strokes.length;
    var dot = num.querySelector('.ann-dot');
    if (has && !dot) { dot = document.createElement('span'); dot.className = 'ann-dot'; dot.textContent = 'ANNOTATA'; num.appendChild(dot); }
    if (!has && dot) dot.remove();
  }
  function markCards(L){ Object.keys(ann[L]||{}).forEach(function(n){ markCard(L,+n); }); }
  function currentLesson(){ var h = location.hash.replace('#',''); return h; }

  /* ---------- interfaccia ---------- */
  var root, frame, img, canvas, ctx, notesEl, countEl, range, titleEl;
  function sw(color, name, kind){ return '<button type="button" class="sw" data-'+kind+'="'+color+'" style="background:'+color+'" aria-label="'+name+'" title="'+name+'"></button>'; }
  function build(){
    root = document.createElement('div'); root.className = 'pv'; root.hidden = true;
    root.setAttribute('role','dialog'); root.setAttribute('aria-label','Presentazione slide');
    root.innerHTML =
      '<div class="pv-bar">' +
        '<span class="pv-title" id="pv-title"></span>' +
        '<div class="pv-group"><button type="button" data-act="prev" aria-label="Slide precedente">&#8592;</button><span class="pv-count" id="pv-count"></span><button type="button" data-act="next" aria-label="Slide successiva">&#8594;</button></div>' +
        '<div class="pv-group"><button type="button" data-tool="none" title="Puntatore: niente segni, clic e swipe cambiano slide (V)">Puntatore</button><button type="button" data-tool="pen" title="Penna (P)">Penna</button>' + PEN.map(function(c){return sw(c[0],'Penna '+c[1].toLowerCase(),'pen');}).join('') + '</div>' +
        '<div class="pv-group"><button type="button" data-tool="hl" title="Evidenziatore (H)">Evidenzia</button>' + HL.map(function(c){return sw(c[0],'Evidenziatore '+c[1].toLowerCase(),'hl');}).join('') + '<button type="button" data-tool="line" title="Sottolinea con una riga dritta (U)">Sottolinea</button></div>' +
        '<div class="pv-group"><button type="button" data-tool="eraser" title="Gomma: tocca un tratto per cancellarlo (E)">Gomma</button><button type="button" data-act="undo" title="Annulla (Cmd/Ctrl+Z)">Annulla</button><button type="button" data-act="clear" title="Cancella tutti i segni di questa slide">Pulisci slide</button></div>' +
        '<span class="pv-spacer"></span>' +
                '<button type="button" data-act="notes" aria-pressed="true" title="Mostra o nascondi gli appunti (N)">Appunti</button>' +
        '<button type="button" data-act="fs" title="Schermo intero (F)">Schermo intero</button>' +
        '<button type="button" data-act="close" title="Chiudi (Esc)">Chiudi</button>' +
      '</div>' +
      '<div class="pv-main">' +
        '<div class="pv-stage" id="pv-stage"><div class="pv-frame" id="pv-frame"><img id="pv-img" alt=""><canvas id="pv-canvas"></canvas></div>' +
          '<button type="button" class="pv-nav prev" data-act="prev" aria-label="Slide precedente">&#8249;</button><button type="button" class="pv-nav next" data-act="next" aria-label="Slide successiva">&#8250;</button></div>' +
        '<aside class="pv-notes" id="pv-notes" aria-label="Appunti della slide"></aside>' +
      '</div>' +
      '<div class="pv-foot"><span class="pv-status" id="pv-status"></span><input type="range" id="pv-range" min="1" max="1" value="1" aria-label="Vai alla slide"><span class="keys">&#8592; &#8594; slide · P penna · H evidenzia · U sottolinea · E gomma · V puntatore · N appunti · F schermo intero · Esc chiudi</span></div>';
    document.body.appendChild(root);
    frame = root.querySelector('#pv-frame'); img = root.querySelector('#pv-img'); canvas = root.querySelector('#pv-canvas');
    ctx = canvas.getContext('2d'); notesEl = root.querySelector('#pv-notes'); countEl = root.querySelector('#pv-count');
    range = root.querySelector('#pv-range'); titleEl = root.querySelector('#pv-title');

    root.addEventListener('click', function(e){
      var b = e.target.closest('button'); if (!b || !root.contains(b)) return;
      if (b.dataset.act === 'prev') go(st.n - 1, -1);
      else if (b.dataset.act === 'next') go(st.n + 1, 1);
      else if (b.dataset.act === 'close') close();
      else if (b.dataset.act === 'fs') fsToggle(root, b);
      else if (b.dataset.act === 'undo') undo();
      else if (b.dataset.act === 'clear') clearSlide();
      else if (b.dataset.act === 'notes') toggleNotes();
      else if (b.dataset.tool) setTool(b.dataset.tool);
      else if (b.dataset.pen) { st.pen = b.dataset.pen; setTool(st.tool === 'line' ? 'line' : 'pen'); }
      else if (b.dataset.hl) { st.hl = b.dataset.hl; setTool('hl'); }
    });
    range.addEventListener('input', function(){ goIndex(+range.value - 1); });
    img.addEventListener('load', layout);
    window.addEventListener('resize', function(){ if (st.open) layout(); });
    bindDraw(); bindSwipe();
    document.addEventListener('keydown', onKey);
    var fb = root.querySelector('[data-act="fs"]'); ['fullscreenchange','webkitfullscreenchange'].forEach(function(ev){ document.addEventListener(ev, function(){ fsSync(fb); if (st.open) setTimeout(layout, 60); }); });
    setStatus();
  }
  function syncToolbar(){
    root.querySelectorAll('[data-tool]').forEach(function(b){ b.setAttribute('aria-pressed', b.dataset.tool === st.tool ? 'true':'false'); });
    root.querySelectorAll('[data-pen]').forEach(function(b){ b.setAttribute('aria-pressed', (st.tool==='pen'||st.tool==='line') && b.dataset.pen === st.pen ? 'true':'false'); });
    root.querySelectorAll('[data-hl]').forEach(function(b){ b.setAttribute('aria-pressed', st.tool==='hl' && b.dataset.hl === st.hl ? 'true':'false'); });
    frame.classList.toggle('drawing', st.tool === 'pen' || st.tool === 'hl' || st.tool === 'line');
    frame.classList.toggle('erasing', st.tool === 'eraser');
  }
  function setTool(t){ st.tool = t; syncToolbar(); }
  function toggleNotes(){
    st.notes = !st.notes; root.classList.toggle('nonotes', !st.notes);
    root.querySelector('[data-act="notes"]').setAttribute('aria-pressed', st.notes ? 'true':'false');
    try { localStorage.setItem('cvpv:notes', st.notes ? '1':'0'); } catch(e){}
    layout();
  }

  /* ---------- apertura e navigazione ---------- */
  function open(L, n){
    if (!root) build();
    st.L = L; st.open = true;
    st.list = Array.prototype.map.call(document.querySelectorAll('#main article.slide'), function(a){ return +a.getAttribute('data-n'); });
    if (!st.list.length) return;
    try { st.notes = localStorage.getItem('cvpv:notes') !== '0'; } catch(e){}
    root.classList.toggle('nonotes', !st.notes);
    root.querySelector('[data-act="notes"]').setAttribute('aria-pressed', st.notes ? 'true':'false');
    var info = (window.LESSONS||[]).filter(function(x){return x.id===L;})[0];
    titleEl.textContent = info ? 'L' + info.num + ' · ' + info.h1 : L;
    range.max = st.list.length;
    loadLocal(L);
    if (HD[L] && !hdCache[L] && !hdLoading[L]) {
      hdLoading[L] = fetch(HD[L]).then(function(r){ if (!r.ok) throw 0; return r.json(); })
        .then(function(d){ hdCache[L] = d.slides; if (st.open && st.L === L) show(); })
        .catch(function(){ hdLoading[L] = null; });
    }
    root.hidden = false; document.documentElement.style.overflow = 'hidden';
    syncToolbar();
    st.n = st.list.indexOf(n) >= 0 ? n : st.list[0];
    show();
    root.querySelector('[data-act="next"]').focus({preventScroll:true});
  }
  function close(){
    if (!st.open) return;
    if (document.fullscreenElement || document.webkitFullscreenElement) { try { (document.exitFullscreen || document.webkitExitFullscreen).call(document); } catch(e){} }
    st.open = false; root.hidden = true; document.documentElement.style.overflow = '';
    var a = document.getElementById('s' + st.n); if (a) a.scrollIntoView({block:'start'});
  }
  function goIndex(i){ i = Math.max(0, Math.min(st.list.length - 1, i)); st.n = st.list[i]; show(); }
  function go(n){ var i = st.list.indexOf(st.n); var d = n - st.n; goIndex(i + (d > 0 ? 1 : -1)); }

  function show(){
    var i = st.list.indexOf(st.n), a = document.getElementById('s' + st.n);
    countEl.textContent = (i + 1) + ' / ' + st.list.length; range.value = i + 1;
    var src = null;
    if (hdCache[st.L] && hdCache[st.L][st.n - 1]) src = hdCache[st.L][st.n - 1];
    else if (a) { var t = a.querySelector('.thumb img'); if (t) src = t.src; }
    var stage = root.querySelector('#pv-stage'), empty = stage.querySelector('.pv-empty');
    if (src) { if (empty) empty.remove(); frame.hidden = false; if (img.src !== src) img.src = src; else layout(); }
    else {
      frame.hidden = true;
      if (!empty) { empty = document.createElement('div'); empty.className = 'pv-empty'; stage.insertBefore(empty, stage.firstChild); }
      empty.textContent = 'Nessuna immagine per questa scheda: gli appunti sono nel pannello.';
    }
    notesEl.innerHTML = '';
    if (a) {
      var c = a.cloneNode(true); c.removeAttribute('id');
      var th = c.querySelector('.thumb'); if (th) th.remove();
      c.className = 'slide'; notesEl.appendChild(c);
    }
    notesEl.scrollTop = 0;
    // precarico la successiva
    if (hdCache[st.L] && st.list[i+1]) { var p = new Image(); p.src = hdCache[st.L][st.list[i+1]-1] || ''; }
    redraw();
  }

  /* ---------- disegno ---------- */
  function layout(){
    if (!st.open || frame.hidden) return;
    var stage = root.querySelector('#pv-stage');
    var W = stage.clientWidth - 28, H = stage.clientHeight - 28;
    var ar = (img.naturalWidth && img.naturalHeight) ? img.naturalWidth / img.naturalHeight : 1.6;
    var w = Math.min(W, H * ar), h = w / ar;
    frame.style.width = Math.max(50, Math.floor(w)) + 'px'; frame.style.height = Math.max(30, Math.floor(h)) + 'px';
    var dpr = window.devicePixelRatio || 1;
    canvas.width = Math.round(frame.clientWidth * dpr); canvas.height = Math.round(frame.clientHeight * dpr);
    redraw();
  }
  function drawStroke(s){
    var W = canvas.width, H = canvas.height, p = s.p; if (!p || p.length < 2) return;
    ctx.save();
    ctx.lineCap = s.t === 'hl' ? 'butt' : 'round'; ctx.lineJoin = 'round';
    ctx.strokeStyle = s.c; ctx.globalAlpha = s.t === 'hl' ? 0.5 : 1;
    ctx.lineWidth = Math.max(1, s.w * W);
    ctx.beginPath(); ctx.moveTo(p[0]*W, p[1]*H);
    if (p.length === 2) ctx.lineTo(p[0]*W + 0.1, p[1]*H);
    for (var k = 2; k < p.length - 2; k += 2) {
      var mx = (p[k] + p[k+2]) / 2, my = (p[k+1] + p[k+3]) / 2;
      ctx.quadraticCurveTo(p[k]*W, p[k+1]*H, mx*W, my*H);
    }
    if (p.length >= 4) ctx.lineTo(p[p.length-2]*W, p[p.length-1]*H);
    ctx.stroke(); ctx.restore();
  }
  function redraw(){
    if (!ctx || !st.open) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    strokesOf(st.L, st.n).forEach(drawStroke);
    if (st.cur) drawStroke(st.cur);
  }
  function pos(e){
    var r = canvas.getBoundingClientRect();
    return [Math.min(1, Math.max(0, (e.clientX - r.left) / r.width)), Math.min(1, Math.max(0, (e.clientY - r.top) / r.height))];
  }
  function r4(v){ return Math.round(v * 10000) / 10000; }
  function pushUndo(op){ var k = st.L + ':' + st.n; (st.undo[k] = st.undo[k] || []).push(op); }
  function eraseAt(q){
    var list = strokesOf(st.L, st.n), ar = canvas.width / canvas.height, rad = 0.012;
    for (var i = list.length - 1; i >= 0; i--) {
      var p = list[i].p, hit = false;
      for (var k = 0; k < p.length; k += 2) { var dx = (p[k] - q[0]) * ar, dy = p[k+1] - q[1]; if (dx*dx + dy*dy < rad*rad) { hit = true; break; } }
      if (!hit && list[i].t === 'line' && p.length === 4) { // segmento
        var ax=p[0]*ar, ay=p[1], bx=p[2]*ar, by=p[3], qx=q[0]*ar, qy=q[1], vx=bx-ax, vy=by-ay, L2=vx*vx+vy*vy||1e-9;
        var t=Math.max(0,Math.min(1,((qx-ax)*vx+(qy-ay)*vy)/L2)), ex=ax+t*vx-qx, ey=ay+t*vy-qy; hit = ex*ex+ey*ey < rad*rad;
      }
      if (hit) { var s = list.splice(i, 1)[0]; pushUndo({t:'erase', s:s, i:i}); changed(st.L, st.n); redraw(); return; }
    }
  }
  function bindDraw(){
    var down = false;
    canvas.addEventListener('pointerdown', function(e){
      if (st.tool === 'none') return;
      e.preventDefault(); canvas.setPointerCapture(e.pointerId); down = true;
      var q = pos(e);
      if (st.tool === 'eraser') { eraseAt(q); return; }
      var t = st.tool;
      st.cur = {t:t, c: t === 'hl' ? st.hl : st.pen, w: WIDTH[t], p:[r4(q[0]), r4(q[1])]};
      if (t === 'line') st.cur.p.push(r4(q[0]), r4(q[1]));
      redraw();
    });
    canvas.addEventListener('pointermove', function(e){
      if (!down) return;
      if (st.tool === 'eraser') { eraseAt(pos(e)); return; }
      if (!st.cur) return;
      var evs = e.getCoalescedEvents ? e.getCoalescedEvents() : [e]; if (!evs.length) evs = [e];
      if (st.cur.t === 'line') {
        var q = pos(e), p = st.cur.p, ar = canvas.width / canvas.height;
        var dy = q[1] - p[1], dx = (q[0] - p[0]) * ar;
        if (Math.abs(dy) < Math.abs(dx) * 0.12) q[1] = p[1];   // quasi orizzontale: raddrizza
        p[2] = r4(q[0]); p[3] = r4(q[1]);
      } else {
        evs.forEach(function(ev){
          var q = pos(ev), p = st.cur.p, lx = p[p.length-2], ly = p[p.length-1];
          if (Math.abs(q[0]-lx) + Math.abs(q[1]-ly) > 0.0015) p.push(r4(q[0]), r4(q[1]));
        });
      }
      requestAnimationFrame(redraw);
    });
    function end(){
      if (!down) return; down = false;
      if (st.cur) {
        var s = st.cur; st.cur = null;
        var ok = s.t !== 'line' || Math.abs(s.p[2]-s.p[0]) + Math.abs(s.p[3]-s.p[1]) > 0.004;
        if (ok) { strokesOf(st.L, st.n).push(s); pushUndo({t:'add'}); changed(st.L, st.n); }
        redraw();
      }
    }
    canvas.addEventListener('pointerup', end); canvas.addEventListener('pointercancel', end);
  }
  function undo(){
    var k = st.L + ':' + st.n, u = st.undo[k], list = strokesOf(st.L, st.n);
    if (!u || !u.length) return;
    var op = u.pop();
    if (op.t === 'add') list.pop();
    else if (op.t === 'erase') list.splice(op.i, 0, op.s);
    else if (op.t === 'clear') Array.prototype.push.apply(list, op.s);
    changed(st.L, st.n); redraw();
  }
  function clearSlide(){
    var list = strokesOf(st.L, st.n); if (!list.length) return;
    pushUndo({t:'clear', s:list.splice(0, list.length)}); changed(st.L, st.n); redraw();
  }
  function bindSwipe(){
    var stage = root.querySelector('#pv-stage'), sx = null, sy = 0;
    stage.addEventListener('pointerdown', function(e){ if (st.tool !== 'none' || e.target.closest('button')) return; sx = e.clientX; sy = e.clientY; });
    stage.addEventListener('pointerup', function(e){
      if (sx === null) return; var dx = e.clientX - sx, dy = e.clientY - sy; sx = null;
      if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 1.5) goIndex(st.list.indexOf(st.n) + (dx < 0 ? 1 : -1));
    });
  }
  function onKey(e){
    if (!st.open) return;
    var tag = (e.target.tagName || '').toLowerCase();
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'z') { e.preventDefault(); undo(); return; }
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    if (tag === 'input' && e.target.type === 'range' && (e.key === 'ArrowLeft' || e.key === 'ArrowRight')) return;
    var k = e.key;
    if (k === 'ArrowRight' || k === 'PageDown' || (k === ' ' && tag !== 'button')) { e.preventDefault(); goIndex(st.list.indexOf(st.n) + 1); }
    else if (k === 'ArrowLeft' || k === 'PageUp') { e.preventDefault(); goIndex(st.list.indexOf(st.n) - 1); }
    else if (k === 'Home') goIndex(0);
    else if (k === 'End') goIndex(st.list.length - 1);
    else if (k === 'Escape') { if (st.tool !== 'none') setTool('none'); else close(); }
    else if (k === 'f' || k === 'F') fsToggle(root, root.querySelector('[data-act="fs"]'));
    else if (k === 'n' || k === 'N') toggleNotes();
    else if (k === 'p' || k === 'P') setTool('pen');
    else if (k === 'h' || k === 'H') setTool('hl');
    else if (k === 'u' || k === 'U') setTool('line');
    else if (k === 'e' || k === 'E') setTool('eraser');
    else if (k === 'v' || k === 'V') setTool('none');
  }

  /* ---------- aggancio alla vista a schede ---------- */
  document.addEventListener('click', function(e){
    var t = e.target.closest('#main .slide .thumb img');
    if (t) { var a = t.closest('article.slide'); open(currentLesson(), +a.getAttribute('data-n')); return; }
    var b = e.target.closest('#main [data-present]');
    if (b) open(currentLesson(), +(b.getAttribute('data-present')) || null);
  });
  window.PV = {
    lessonShown: function(L){
      var hero = document.querySelector('#main header.hero');
      if (hero && !document.querySelector('#main .lesson-tools')) {
        var d = document.createElement('div'); d.className = 'lesson-tools';
        d.innerHTML = '<button type="button" class="btn-primary" data-present="1">Presentazione</button><span>Slide a tutto schermo con appunti a lato, penna ed evidenziatore. Oppure clicca una miniatura per aprirla lì. Nella dispensa e negli appunti seleziona del testo per evidenziarlo o sottolinearlo.</span>';
        hero.appendChild(d);
      }
      loadLocal(L); markCards(L);
    },
    close: close
  };
})();
