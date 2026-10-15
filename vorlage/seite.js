// Kapitel auf- und zuklappen, Verzeichnis markieren, Hell/Dunkel umschalten.
(function () {
  var kapitel = Array.prototype.slice.call(document.querySelectorAll('details.kapitel'));
  var links = Array.prototype.slice.call(document.querySelectorAll('.kapitelnav a[data-anker]'));
  var alle = document.getElementById('alle');

  function oeffne(id) {
    var ziel = id && document.getElementById(id);
    if (ziel && ziel.tagName === 'DETAILS') ziel.open = true;
  }
  function beschrifteAlle() {
    if (!alle) return;
    var offen = kapitel.every(function (k) { return k.open; });
    alle.textContent = offen ? 'Alle zuklappen' : 'Alle aufklappen';
  }

  // Klick im Verzeichnis öffnet das Kapitel, danach springt der Browser hin
  links.forEach(function (a) {
    a.addEventListener('click', function () { oeffne(a.getAttribute('data-anker')); });
  });
  // Direktlink mit #kapitel öffnet das Kapitel
  oeffne(decodeURIComponent(location.hash.slice(1)));
  window.addEventListener('hashchange', function () { oeffne(decodeURIComponent(location.hash.slice(1))); });

  if (alle) {
    alle.addEventListener('click', function () {
      var oeffnen = !kapitel.every(function (k) { return k.open; });
      kapitel.forEach(function (k) { k.open = oeffnen; });
      beschrifteAlle();
    });
  }
  kapitel.forEach(function (k) { k.addEventListener('toggle', beschrifteAlle); });
  beschrifteAlle();

  // Verzeichnis: Kapitel markieren, das gerade im Blick ist
  if (!links.length || !('IntersectionObserver' in window)) return;
  var sichtbar = {};
  function markiere(anker) {
    links.forEach(function (a) {
      var aktiv = a.getAttribute('data-anker') === anker;
      a.classList.toggle('aktiv', aktiv);
      if (aktiv) a.setAttribute('aria-current', 'location'); else a.removeAttribute('aria-current');
    });
  }
  var beobachter = new IntersectionObserver(function (eintraege) {
    eintraege.forEach(function (e) { sichtbar[e.target.id] = e.isIntersecting; });
    for (var i = 0; i < links.length; i++) {
      var id = links[i].getAttribute('data-anker');
      if (sichtbar[id]) { markiere(id); return; }
    }
  }, { rootMargin: '-10% 0px -60% 0px' });
  kapitel.forEach(function (k) { beobachter.observe(k); });
})();

// Schalter Hell/Dunkel. Ohne Wahl gilt die Einstellung des Geräts.
(function () {
  var knopf = document.getElementById('thema');
  if (!knopf) return;
  var wurzel = document.documentElement;
  function dunkelAktiv() {
    var t = wurzel.getAttribute('data-theme');
    if (t) return t === 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  }
  function beschrifte() {
    var dunkel = dunkelAktiv();
    knopf.textContent = dunkel ? 'Hell' : 'Dunkel';
    knopf.setAttribute('aria-label', dunkel ? 'Helles Layout zeigen' : 'Dunkles Layout zeigen');
  }
  try {
    var gespeichert = localStorage.getItem('thema');
    if (gespeichert === 'dark' || gespeichert === 'light') wurzel.setAttribute('data-theme', gespeichert);
  } catch (e) {}
  beschrifte();
  knopf.addEventListener('click', function () {
    var neu = dunkelAktiv() ? 'light' : 'dark';
    wurzel.setAttribute('data-theme', neu);
    try { localStorage.setItem('thema', neu); } catch (e) {}
    beschrifte();
  });
})();

// Akteurslandkarte: Porträt beim Darüberfahren, Fokussieren oder Antippen zeigen.
(function () {
  Array.prototype.forEach.call(document.querySelectorAll('.landkarte'), function (karte) {
    var ringe = Array.prototype.slice.call(karte.querySelectorAll('.ring'));
    var hinweis = karte.querySelector('.landkarte-hinweis');
    if (!ringe.length) return;
    karte.classList.add('interaktiv');
    var aktiv = null;
    function zeige(ring) {
      if (aktiv === ring) return;
      ringe.forEach(function (r) {
        var an = r === ring;
        r.classList.toggle('aktiv', an);
        r.setAttribute('aria-expanded', an ? 'true' : 'false');
        var portrait = document.getElementById(r.getAttribute('data-portrait'));
        if (portrait) portrait.classList.toggle('sichtbar', an);
      });
      if (hinweis) hinweis.hidden = !!ring;
      aktiv = ring;
    }
    ringe.forEach(function (r) {
      r.addEventListener('pointerenter', function () { zeige(r); });
      r.addEventListener('focus', function () { zeige(r); });
      r.addEventListener('click', function () { zeige(r); });
      r.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); zeige(r); }
      });
    });
    // Maus verlässt die Karte: wieder Hinweis zeigen. Auf dem Handy bleibt das Porträt stehen.
    karte.addEventListener('pointerleave', function (e) { if (e.pointerType === 'mouse') zeige(null); });
    karte.addEventListener('focusout', function (e) { if (!karte.contains(e.relatedTarget)) zeige(null); });
  });
})();

// Reiter: immer nur ein Abschnitt sichtbar. Der Grössenvergleich springt in den passenden Reiter.
(function () {
  var boxen = Array.prototype.slice.call(document.querySelectorAll('[data-reiter]'));
  var vergleich = Array.prototype.slice.call(document.querySelectorAll('[data-reiter-ziel]'));

  function markiereVergleich(id) {
    vergleich.forEach(function (a) { a.classList.toggle('aktiv', a.getAttribute('data-reiter-ziel') === id); });
  }

  boxen.forEach(function (box) {
    var knoepfe = Array.prototype.slice.call(box.querySelectorAll('[role="tab"]'));
    if (!knoepfe.length) return;
    box.classList.add('interaktiv');

    function waehle(id, fokus) {
      knoepfe.forEach(function (k) {
        var an = k.getAttribute('aria-controls') === id;
        k.setAttribute('aria-selected', an ? 'true' : 'false');
        k.tabIndex = an ? 0 : -1;
        var feld = document.getElementById(k.getAttribute('aria-controls'));
        if (feld) feld.classList.toggle('aktiv', an);
        if (an && fokus) k.focus();
      });
      markiereVergleich(id);
    }

    knoepfe.forEach(function (k, i) {
      k.addEventListener('click', function () { waehle(k.getAttribute('aria-controls')); });
      k.addEventListener('keydown', function (e) {
        var neu = null;
        if (e.key === 'ArrowRight') neu = knoepfe[(i + 1) % knoepfe.length];
        if (e.key === 'ArrowLeft') neu = knoepfe[(i - 1 + knoepfe.length) % knoepfe.length];
        if (e.key === 'Home') neu = knoepfe[0];
        if (e.key === 'End') neu = knoepfe[knoepfe.length - 1];
        if (neu) { e.preventDefault(); waehle(neu.getAttribute('aria-controls'), true); }
      });
    });
    box.addEventListener('reiter-waehlen', function (e) { waehle(e.detail); });

    // Start: Reiter aus dem Link (#reiter-…) oder der erste
    var start = knoepfe[0].getAttribute('aria-controls');
    var hash = decodeURIComponent(location.hash.slice(1));
    knoepfe.forEach(function (k) {
      if (k.getAttribute('aria-controls') === hash) {
        start = hash;
        var kapitel = box.closest('details');
        if (kapitel) kapitel.open = true;
      }
    });
    waehle(start);
    if (start === hash) setTimeout(function () { box.scrollIntoView({ block: 'start' }); }, 0);
  });

  vergleich.forEach(function (a) {
    a.addEventListener('click', function (e) {
      var id = a.getAttribute('data-reiter-ziel');
      var feld = document.getElementById(id);
      var box = feld && feld.closest('[data-reiter]');
      if (!box || !box.classList.contains('interaktiv')) return;
      e.preventDefault();
      var kapitel = box.closest('details');
      if (kapitel) kapitel.open = true;
      box.dispatchEvent(new CustomEvent('reiter-waehlen', { detail: id }));
      box.scrollIntoView({ block: 'start' });
    });
  });
})();

// Standortfaktoren: Symbol beim Darüberfahren gross, die anderen verblassen. Das Feld darunter wechselt.
// Das zuletzt gewählte Feld bleibt stehen, damit man in Ruhe lesen kann.
(function () {
  Array.prototype.forEach.call(document.querySelectorAll('[data-faktoren]'), function (box) {
    var leiste = box.querySelector('.faktoren-leiste');
    var knoepfe = Array.prototype.slice.call(box.querySelectorAll('.faktor'));
    if (!leiste || !knoepfe.length) return;
    box.classList.add('interaktiv');

    function waehle(knopf, fokus) {
      knoepfe.forEach(function (k) {
        var an = k === knopf;
        k.setAttribute('aria-selected', an ? 'true' : 'false');
        k.tabIndex = an ? 0 : -1;
        var feld = document.getElementById(k.getAttribute('aria-controls'));
        if (feld) feld.classList.toggle('aktiv', an);
      });
      if (fokus) knopf.focus();
    }
    function tastatur(k) {
      try { return k.matches(':focus-visible'); } catch (e) { return true; }
    }

    knoepfe.forEach(function (k, i) {
      k.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') waehle(k); });
      k.addEventListener('click', function () { waehle(k); box.classList.add('fokus'); });
      k.addEventListener('focus', function () { if (tastatur(k)) { waehle(k); box.classList.add('fokus'); } });
      k.addEventListener('keydown', function (e) {
        var neu = null;
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') neu = knoepfe[(i + 1) % knoepfe.length];
        if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') neu = knoepfe[(i - 1 + knoepfe.length) % knoepfe.length];
        if (e.key === 'Home') neu = knoepfe[0];
        if (e.key === 'End') neu = knoepfe[knoepfe.length - 1];
        if (e.key === 'Escape') { box.classList.remove('fokus'); return; }
        if (neu) { e.preventDefault(); waehle(neu, true); }
      });
    });
    // Gross und verblasst nur, solange die Maus über den Symbolen ist oder die Tastatur dort steht.
    leiste.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') box.classList.add('fokus'); });
    leiste.addEventListener('pointerleave', function (e) { if (e.pointerType === 'mouse') box.classList.remove('fokus'); });
    leiste.addEventListener('focusout', function (e) { if (!leiste.contains(e.relatedTarget)) box.classList.remove('fokus'); });
    // Auf dem Handy: Antippen ausserhalb der Symbole hebt die Hervorhebung auf.
    document.addEventListener('pointerdown', function (e) { if (!leiste.contains(e.target)) box.classList.remove('fokus'); });
  });
})();
