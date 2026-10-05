
(function(){
  function cleanClone(slide){
    var src = slide.querySelector('.notes .body');
    var title = slide.querySelector('h3').textContent;
    var num = slide.getAttribute('data-n');
    var c = src.cloneNode(true);
    c.querySelectorAll('.f').forEach(function(f){
      var p = document.createElement('p');
      p.style.fontFamily = 'Consolas, monospace';
      p.innerHTML = f.innerHTML; f.replaceWith(p);
    });
    c.querySelectorAll('.box').forEach(function(b){
      var d = document.createElement('div');
      var lab = b.querySelector(':scope > b');
      var p = document.createElement('p');
      p.innerHTML = '<b>' + (lab ? lab.textContent : '') + '</b>';
      d.appendChild(p);
      if (lab) lab.remove();
      while (b.firstChild) d.appendChild(b.firstChild);
      b.replaceWith(d);
    });
    var html = '<h3>Slide ' + num + ' · ' + title + '</h3>' + c.innerHTML;
    return {html: html, text: 'Slide ' + num + ' - ' + title + '\n\n' + c.innerText};
  }
  function flash(btn, msg){
    var old = btn.textContent; btn.textContent = msg; btn.classList.add('ok');
    setTimeout(function(){ btn.textContent = old; btn.classList.remove('ok'); }, 1400);
  }
  function fallback(slide, btn){
    var body = slide.querySelector('.notes .body');
    var r = document.createRange(); r.selectNodeContents(body);
    var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
    var ok = false; try { ok = document.execCommand('copy'); } catch(e) {}
    flash(btn, ok ? 'Copiato' : 'Selezionato: premi Cmd+C');
  }
  document.addEventListener('click', function(e){
    var btn = e.target.closest('.copy'); if (!btn) return;
    var slide = btn.closest('.slide');
    var d = cleanClone(slide);
    try {
      if (window.ClipboardItem && navigator.clipboard && navigator.clipboard.write) {
        navigator.clipboard.write([new ClipboardItem({
          'text/html': new Blob([d.html], {type:'text/html'}),
          'text/plain': new Blob([d.text], {type:'text/plain'})
        })]).then(function(){ flash(btn, 'Copiato'); }, function(){ fallback(slide, btn); });
      } else { fallback(slide, btn); }
    } catch(err) { fallback(slide, btn); }
  });
})();
