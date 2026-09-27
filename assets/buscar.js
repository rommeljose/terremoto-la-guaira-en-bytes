/* Buscador del sitio — JavaScript puro, sin dependencias ni servidor.
   Lee assets/buscar.json (lo genera herramientas/generar_indice.py) la primera
   vez que se abre. Se abre con el botón «buscar», con Ctrl/⌘+K o con la tecla /.
   Insensible a mayúsculas y a tildes. © 2026 Rommel Contreras, CC BY-NC-SA 4.0 */
(function () {
  'use strict';
  var script = document.currentScript, base = (script && script.dataset.base) || '.';
  var indice = null, cargando = null, sel = -1, resultados = [];

  var CSS = '' +
  '.bq-btn{display:inline-block;font-family:"IBM Plex Sans",system-ui,sans-serif;font-size:.82rem;' +
  'font-weight:600;color:var(--blue,#1f5fa8);background:var(--paper,#f6f8fb);border:1px solid var(--line,#dde3ec);' +
  'border-radius:20px;padding:5px 12px;cursor:pointer;margin:0 0 18px 8px;vertical-align:top}' +
  '.bq-btn:hover{border-color:var(--blue,#1f5fa8)}' +
  '.bq-btn kbd{font-family:"IBM Plex Mono",monospace;font-size:.72rem;opacity:.65;margin-left:6px;border:0;background:none}' +
  '.bq-capa{position:fixed;inset:0;z-index:9000;display:none;background:rgba(10,16,26,.55);' +
  'padding:8vh 16px 16px;overflow-y:auto}' +
  '.bq-capa[open]{display:block}' +
  '.bq-caja{max-width:720px;margin:0 auto;background:var(--card,var(--panel,#fff));color:var(--ink,#182231);' +
  'border:1px solid var(--line,#dde3ec);border-radius:14px;box-shadow:0 18px 50px rgba(8,14,24,.35);overflow:hidden}' +
  '.bq-caja input{width:100%;box-sizing:border-box;border:0;border-bottom:1px solid var(--line,#dde3ec);' +
  'background:transparent;color:var(--strong,#0c1420);font-family:"Source Serif 4",Georgia,serif;' +
  'font-size:1.12rem;padding:16px 18px;outline:none}' +
  '.bq-caja input::placeholder{color:var(--muted,#5a6675);opacity:.8}' +
  '.bq-meta{font-family:"IBM Plex Sans",system-ui,sans-serif;font-size:.74rem;color:var(--muted,#5a6675);' +
  'padding:8px 18px;border-bottom:1px solid var(--line,#dde3ec);display:flex;justify-content:space-between;gap:12px}' +
  '.bq-lista{list-style:none;margin:0;padding:0;max-height:58vh;overflow-y:auto}' +
  '.bq-lista li{border-bottom:1px solid var(--line,#dde3ec)}' +
  '.bq-lista li:last-child{border-bottom:0}' +
  '.bq-lista a{display:block;padding:12px 18px;text-decoration:none;color:inherit}' +
  '.bq-lista li[aria-selected="true"] a,.bq-lista a:hover{background:var(--blue-soft,rgba(31,95,168,.10))}' +
  '.bq-h{font-family:"IBM Plex Sans",system-ui,sans-serif;font-weight:700;font-size:.94rem;color:var(--strong,#0c1420)}' +
  '.bq-p{font-family:"IBM Plex Mono",monospace;font-size:.7rem;color:var(--muted,#5a6675);' +
  'text-transform:uppercase;letter-spacing:.08em;margin-bottom:3px}' +
  '.bq-t{font-size:.88rem;line-height:1.5;color:var(--ink,#182231);margin-top:4px}' +
  '.bq-t mark,.bq-h mark{background:rgba(227,154,43,.22);color:inherit;padding:0 2px;' +
  'border-radius:2px;box-shadow:inset 0 -2px 0 rgba(227,154,43,.75)}' +
  '.bq-vacio{padding:22px 18px;font-size:.9rem;color:var(--muted,#5a6675)}' +
  '@media (max-width:560px){.bq-capa{padding:4vh 10px 10px}.bq-lista{max-height:66vh}}';

  function norm(s) {
    return s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  }
  function esc(s) {
    return s.replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function marcar(txt, terminos) {
    var n = norm(txt), trozos = [], i = 0, cortes = [];
    terminos.forEach(function (t) {
      var d = 0;
      while ((d = n.indexOf(t, d)) !== -1) { cortes.push([d, d + t.length]); d += t.length; }
    });
    cortes.sort(function (a, b) { return a[0] - b[0]; });
    cortes.forEach(function (c) {
      if (c[0] < i) return;
      trozos.push(esc(txt.slice(i, c[0])), '<mark>', esc(txt.slice(c[0], c[1])), '</mark>');
      i = c[1];
    });
    trozos.push(esc(txt.slice(i)));
    return trozos.join('');
  }
  function extracto(txt, terminos) {
    var n = norm(txt), p = -1;
    terminos.forEach(function (t) { var d = n.indexOf(t); if (d !== -1 && (p === -1 || d < p)) p = d; });
    if (p === -1) return txt.slice(0, 190) + (txt.length > 190 ? '…' : '');
    var a = Math.max(0, p - 80), b = Math.min(txt.length, p + 150);
    if (a > 0) { var e = txt.indexOf(' ', a); if (e !== -1 && e < p) a = e + 1; }
    return (a > 0 ? '…' : '') + txt.slice(a, b).trim() + (b < txt.length ? '…' : '');
  }

  function buscar(q) {
    var terminos = norm(q).split(/[^a-z0-9ñ]+/).filter(function (t) { return t.length > 1; });
    if (!terminos.length || !indice) return [];
    return indice.map(function (r) {
      var h = norm(r.h), t = norm(r.t), punt = 0, todos = true;
      terminos.forEach(function (term) {
        var enH = h.indexOf(term) !== -1, enT = t.indexOf(term) !== -1;
        if (!enH && !enT) { todos = false; return; }
        if (enH) punt += 12;
        if (enT) punt += Math.min(6, (t.split(term).length - 1));
      });
      if (!todos) return null;
      if (h.indexOf(norm(q)) !== -1) punt += 18;          // frase entera en el encabezado
      if (t.indexOf(norm(q)) !== -1) punt += 6;           // frase entera en el cuerpo
      punt += r.n === 1 ? 0 : (r.n === 2 ? 3 : 1);        // una sección pesa más que un apartado
      return { r: r, punt: punt };
    }).filter(Boolean).sort(function (a, b) { return b.punt - a.punt; }).slice(0, 30)
      .map(function (x) { return x.r; });
  }

  // --- interfaz ------------------------------------------------------------
  var capa, campo, lista, meta;
  function construir() {
    var est = document.createElement('style'); est.textContent = CSS;
    document.head.appendChild(est);
    capa = document.createElement('div');
    capa.className = 'bq-capa';
    capa.innerHTML =
      '<div class="bq-caja" role="dialog" aria-modal="true" aria-label="Buscar en el sitio">' +
      '<input type="search" autocomplete="off" spellcheck="false" ' +
      'placeholder="Buscar en el sitio: retroproyección, Okada, banda prohibida…" aria-label="Términos de búsqueda">' +
      '<div class="bq-meta"><span class="bq-n">Escribe para buscar</span>' +
      '<span>↑↓ moverse · ⏎ abrir · Esc cerrar</span></div>' +
      '<ul class="bq-lista" role="listbox" aria-label="Resultados"></ul></div>';
    document.body.appendChild(capa);
    campo = capa.querySelector('input');
    lista = capa.querySelector('.bq-lista');
    meta = capa.querySelector('.bq-n');
    capa.addEventListener('click', function (e) { if (e.target === capa) cerrar(); });
    campo.addEventListener('input', pintar);
    document.addEventListener('keydown', teclas);
  }

  function pintar() {
    var q = campo.value.trim();
    resultados = buscar(q); sel = -1;
    if (!q) { lista.innerHTML = ''; meta.textContent = 'Escribe para buscar'; return; }
    var terminos = norm(q).split(/[^a-z0-9ñ]+/).filter(function (t) { return t.length > 1; });
    meta.textContent = resultados.length
      ? resultados.length + (resultados.length === 1 ? ' resultado' : ' resultados')
      : 'Sin resultados';
    if (!resultados.length) {
      lista.innerHTML = '<li class="bq-vacio">Nada coincide con <b>' + esc(q) +
        '</b>. Prueba con menos palabras, o con un término del método: <i>Green</i>, <i>Okada</i>, <i>jackknife</i>, <i>directividad</i>.</li>';
      return;
    }
    lista.innerHTML = resultados.map(function (r) {
      return '<li role="option"><a href="' + base + '/' + r.u + '">' +
        '<div class="bq-p">' + esc(r.p) + '</div>' +
        '<div class="bq-h">' + marcar(r.h, terminos) + '</div>' +
        '<div class="bq-t">' + marcar(extracto(r.t, terminos), terminos) + '</div></a></li>';
    }).join('');
  }

  function mover(d) {
    if (!resultados.length) return;
    var lis = lista.querySelectorAll('li');
    if (sel >= 0 && lis[sel]) lis[sel].removeAttribute('aria-selected');
    sel = (sel + d + lis.length) % lis.length;
    lis[sel].setAttribute('aria-selected', 'true');
    lis[sel].scrollIntoView({ block: 'nearest' });
  }
  function teclas(e) {
    if (!capa.hasAttribute('open')) {
      var dentro = /^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName) || e.target.isContentEditable;
      if ((e.key === 'k' || e.key === 'K') && (e.ctrlKey || e.metaKey)) { e.preventDefault(); abrir(); }
      else if (e.key === '/' && !dentro && !e.ctrlKey && !e.metaKey && !e.altKey) { e.preventDefault(); abrir(); }
      return;
    }
    if (e.key === 'Escape') { e.preventDefault(); cerrar(); }
    else if (e.key === 'ArrowDown') { e.preventDefault(); mover(1); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); mover(-1); }
    else if (e.key === 'Enter') {
      var lis = lista.querySelectorAll('li a');
      if (lis.length) { e.preventDefault(); (lis[sel >= 0 ? sel : 0]).click(); }
    }
  }

  function cargar() {
    if (indice) return Promise.resolve();
    if (!cargando) {
      cargando = fetch(base + '/assets/buscar.json')
        .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
        .then(function (d) { indice = d; })
        .catch(function () {
          meta.textContent = 'No se pudo cargar el índice';
          lista.innerHTML = '<li class="bq-vacio">El índice de búsqueda no está disponible ahora mismo.</li>';
        });
    }
    return cargando;
  }
  function abrir() {
    capa.setAttribute('open', '');
    document.documentElement.style.overflow = 'hidden';
    campo.focus(); campo.select();
    cargar().then(function () { if (campo.value.trim()) pintar(); });
  }
  function cerrar() {
    capa.removeAttribute('open');
    document.documentElement.style.overflow = '';
  }

  function boton() {
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'bq-btn';
    b.innerHTML = 'buscar <kbd>Ctrl K</kbd>';
    b.setAttribute('aria-label', 'Buscar en el sitio');
    b.addEventListener('click', abrir);
    var back = document.querySelector('.sheet > .back');
    if (back) { back.insertAdjacentElement('afterend', b); return; }
    var head = document.querySelector('.sheet > header');
    if (head) { b.style.margin = '0 0 4px'; head.insertAdjacentElement('afterend', b); return; }
    document.body.insertBefore(b, document.body.firstChild);
  }

  function iniciar() { construir(); boton(); if (location.hash === '#buscar') abrir(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();
