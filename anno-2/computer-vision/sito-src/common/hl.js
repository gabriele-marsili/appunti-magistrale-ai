(function(){
  "use strict";
  /* Evidenziatore di testo per dispense e schede: seleziona del testo, scegli un colore.
     Ogni zona evidenziabile ha data-hl="<lezione>-<parte>" (es. L3-disp, L3-s12).
     Ancoraggio: offset di carattere nel testo della zona + testo esatto (fallback: ricerca del testo). */
  var COLORS = [['y','Giallo'],['g','Verde'],['p','Rosa'],['b','Blu'],['u','Sottolinea']];
  var store = {db:null, uid:null}, data = {}, loadedLessons = {}, chains = {}, timers = {};
  var bar, curSel = null, curMark = null;

  function lsGet(k){ try { var v = localStorage.getItem('cvhl:'+k); return v ? JSON.parse(v) : null; } catch(e){ return null; } }
  function lsSet(k,v){ try { if (v && v.items.length) localStorage.setItem('cvhl:'+k, JSON.stringify(v)); else localStorage.removeItem('cvhl:'+k); } catch(e){} }
  function col(){ return store.db.collection('data/users/' + store.uid); }

  (function init(){
    if (!window.claude || !window.claude.use) return;
    Promise.all([window.claude.use('db'), window.claude.use('user')]).then(function(r){
      if (!r[0] || !r[1]) return;
      return r[1].id().then(function(id){ if (!id) return; store.db = r[0]; store.uid = id; Object.keys(loadedLessons).forEach(loadCloud); });
    }).catch(function(){});
  })();

  function zonesIn(root){ return Array.prototype.slice.call((root||document).querySelectorAll('[data-hl]')); }
  function lessonOf(key){ return key.split('-')[0]; }

  function loadLocal(keys){
    keys.forEach(function(k){ if (!data[k]) data[k] = lsGet(k) || {items:[], updated:0}; });
  }
  function loadCloud(L){
    if (!store.db) return;
    col().where('lesson','==',L).get().then(function(snap){
      snap.docs.forEach(function(d){
        var b = d.data(); if (!b || b.kind !== 'hl') return;
        var loc = data[b.zone];
        if (!loc || (b.updated||0) >= (loc.updated||0)) { data[b.zone] = {items: b.items||[], updated: b.updated||0}; lsSet(b.zone, data[b.zone]); }
      });
      Object.keys(data).forEach(function(k){
        if (lessonOf(k) !== L) return;
        var inCloud = snap.docs.some(function(d){ var b = d.data(); return b && b.kind === 'hl' && b.zone === k && (b.updated||0) >= (data[k].updated||0); });
        if (!inCloud && data[k].items.length) save(k, true);
      });
      renderAll();
    }).catch(function(){});
  }
  function save(k, now){
    data[k].updated = data[k].updated || Date.now(); lsSet(k, data[k]);
    if (!store.db) return;
    clearTimeout(timers[k]);
    timers[k] = setTimeout(function(){
      var body = {kind:'hl', lesson: lessonOf(k), zone: k, items: data[k].items, updated: data[k].updated};
      chains[k] = (chains[k] || Promise.resolve()).then(function(){
        var ref = col().doc('hl-' + k);
        return body.items.length ? ref.set(body) : ref.delete();
      }).catch(function(){});
    }, now ? 0 : 600);
  }

  /* ---- testo della zona ---- */
  function textNodes(zone){
    var out = [], w = document.createTreeWalker(zone, NodeFilter.SHOW_TEXT, {acceptNode: function(n){
      return n.parentNode.closest('button, script, style, .hl-bar') ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT; }});
    while (w.nextNode()) out.push(w.currentNode);
    return out;
  }
  function offsetsOf(zone, range){
    var nodes = textNodes(zone), pos = 0, s = -1, e = -1;
    for (var i = 0; i < nodes.length; i++){
      var n = nodes[i], len = n.nodeValue.length;
      if (n === range.startContainer) s = pos + range.startOffset;
      if (n === range.endContainer) e = pos + range.endOffset;
      pos += len;
    }
    if (s < 0 && range.startContainer.nodeType === 1) s = pos0(zone, range.startContainer, range.startOffset, nodes);
    if (e < 0 && range.endContainer.nodeType === 1) e = pos0(zone, range.endContainer, range.endOffset, nodes);
    return [s, e];
  }
  function pos0(zone, el, off, nodes){
    var target = el.childNodes[off] || null, pos = 0;
    for (var i = 0; i < nodes.length; i++){
      if (target && (target === nodes[i] || (target.compareDocumentPosition(nodes[i]) & Node.DOCUMENT_POSITION_FOLLOWING) || target.contains(nodes[i]))) return pos;
      pos += nodes[i].nodeValue.length;
    }
    return pos;
  }
  function unwrapAll(zone){
    zone.querySelectorAll('mark.hl').forEach(function(m){
      var p = m.parentNode; while (m.firstChild) p.insertBefore(m.firstChild, m); p.removeChild(m);
    });
    zone.normalize();
  }
  function wrapRange(zone, s, e, item){
    var nodes = textNodes(zone), pos = 0;
    nodes.forEach(function(n){
      var len = n.nodeValue.length, a = Math.max(s, pos), b = Math.min(e, pos + len);
      if (b > a && n.nodeValue.slice(a - pos, b - pos).trim().length) {
        var r = document.createRange(); r.setStart(n, a - pos); r.setEnd(n, b - pos);
        var m = document.createElement('mark'); m.className = 'hl hl-' + item.c; m.setAttribute('data-hid', item.id);
        try { r.surroundContents(m); } catch(err) {}
      }
      pos += len;
    });
  }
  function render(zone){
    var k = zone.getAttribute('data-hl'), d = data[k];
    unwrapAll(zone);
    if (!d || !d.items.length) return;
    var full = textNodes(zone).map(function(n){ return n.nodeValue; }).join('');
    d.items.slice().sort(function(a,b){ return b.s - a.s; }).forEach(function(it){
      var s = it.s, e = it.e;
      if (full.slice(s, e) !== it.t) { var j = full.indexOf(it.t); if (j < 0) return; s = j; e = j + it.t.length; }
      wrapRange(zone, s, e, it);
    });
  }
  function renderKey(k){ document.querySelectorAll('[data-hl="' + k + '"]').forEach(render); }
  function renderAll(){ zonesIn().forEach(render); }

  /* ---- barra ---- */
  function buildBar(){
    bar = document.createElement('div'); bar.className = 'hl-bar'; bar.hidden = true;
    bar.setAttribute('role','toolbar'); bar.setAttribute('aria-label','Evidenzia il testo selezionato');
    bar.innerHTML = COLORS.map(function(c){ return '<button type="button" class="hl-sw hl-sw-' + c[0] + '" data-c="' + c[0] + '" title="' + c[1] + '" aria-label="' + c[1] + '">' + (c[0]==='u' ? 'U' : '') + '</button>'; }).join('') +
      '<button type="button" class="hl-del" data-del="1" title="Togli evidenziazione">Togli</button>';
    document.body.appendChild(bar);
    bar.addEventListener('mousedown', function(e){ e.preventDefault(); });
    bar.addEventListener('click', function(e){
      var b = e.target.closest('button'); if (!b) return;
      if (b.dataset.del) removeMark(); else apply(b.dataset.c);
      hide();
    });
  }
  function hide(){ if (bar) bar.hidden = true; curSel = null; curMark = null; }
  function place(rect, delOnly){
    if (!bar) buildBar();
    bar.querySelectorAll('.hl-sw').forEach(function(x){ x.hidden = !!delOnly; });
    bar.querySelector('.hl-del').hidden = !delOnly;
    bar.hidden = false;
    var bw = bar.offsetWidth, bh = bar.offsetHeight, vw = document.documentElement.clientWidth;
    var x = Math.min(Math.max(8, rect.left + rect.width/2 - bw/2), vw - bw - 8);
    var y = rect.top - bh - 8; if (y < 8) y = rect.bottom + 8;
    bar.style.left = x + 'px'; bar.style.top = y + 'px';
  }
  function onSelect(){
    var sel = window.getSelection();
    if (!sel || sel.isCollapsed || !sel.rangeCount) { if (!curMark) hide(); return; }
    var r = sel.getRangeAt(0), zone = (r.commonAncestorContainer.nodeType === 1 ? r.commonAncestorContainer : r.commonAncestorContainer.parentNode).closest('[data-hl]');
    if (!zone || !sel.toString().trim()) { hide(); return; }
    curSel = {zone: zone, range: r.cloneRange()}; curMark = null;
    place(r.getBoundingClientRect(), false);
  }
  function apply(c){
    if (!curSel) return;
    var zone = curSel.zone, k = zone.getAttribute('data-hl'), o = offsetsOf(zone, curSel.range);
    if (o[0] < 0 || o[1] <= o[0]) return;
    var full = textNodes(zone).map(function(n){ return n.nodeValue; }).join('');
    loadLocal([k]);
    data[k].items.push({id: Date.now().toString(36) + Math.random().toString(36).slice(2,6), s:o[0], e:o[1], t: full.slice(o[0], o[1]), c:c});
    data[k].updated = Date.now();
    window.getSelection().removeAllRanges();
    renderKey(k); save(k);
  }
  function removeMark(){
    if (!curMark) return;
    var zone = curMark.closest('[data-hl]'), k = zone.getAttribute('data-hl'), id = curMark.getAttribute('data-hid');
    data[k].items = data[k].items.filter(function(it){ return it.id !== id; }); data[k].updated = Date.now();
    renderKey(k); save(k);
  }
  document.addEventListener('mouseup', function(e){ if (bar && bar.contains(e.target)) return; setTimeout(onSelect, 10); });
  document.addEventListener('touchend', function(e){ if (bar && bar.contains(e.target)) return; setTimeout(onSelect, 250); });
  document.addEventListener('keyup', function(e){ if (e.shiftKey) setTimeout(onSelect, 10); });
  document.addEventListener('click', function(e){
    var m = e.target.closest('mark.hl');
    if (m && window.getSelection().isCollapsed) { curMark = m; curSel = null; place(m.getBoundingClientRect(), true); return; }
    if (bar && !bar.contains(e.target) && window.getSelection().isCollapsed) hide();
  });
  window.addEventListener('scroll', function(){
    if (!bar || bar.hidden) return;
    if (curSel) place(curSel.range.getBoundingClientRect(), false);
    else if (curMark && document.contains(curMark)) place(curMark.getBoundingClientRect(), true);
    else hide();
  }, {passive:true});

  window.HL = {
    shown: function(){
      var zs = zonesIn(); if (!zs.length) return;
      var keys = zs.map(function(z){ return z.getAttribute('data-hl'); });
      loadLocal(keys);
      keys.map(lessonOf).filter(function(v,i,a){ return a.indexOf(v) === i; }).forEach(function(L){
        if (!loadedLessons[L]) { loadedLessons[L] = true; loadCloud(L); }
      });
      renderAll();
    },
    refresh: renderAll
  };
})();
