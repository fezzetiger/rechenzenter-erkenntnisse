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
