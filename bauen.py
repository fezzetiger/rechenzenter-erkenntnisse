#!/usr/bin/env python3
"""Baut index.html aus den Texten in inhalte/ und den Zahlen in daten/.

Aufruf:   python3 bauen.py                    baut index.html
          python3 bauen.py --variante raster  baut entwuerfe/raster.html aus entwuerfe/raster/
          python3 bauen.py --alle             baut alle Entwürfe in entwuerfe/
Braucht:  Python 3.8 oder neuer und das Paket «markdown» (einmalig: pip3 install markdown)

Die fertige Seite ist eine einzige Datei (index.html). Gestaltung, Skript und Logo
stecken darin. So läuft sie auf GitHub Pages, auf einem Webhosting oder verschlüsselt.
"""
import argparse
import base64
import csv
import datetime
import html
import re
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    sys.exit("Das Paket «markdown» fehlt. Einmalig installieren mit:  pip3 install markdown")

ORDNER = Path(__file__).resolve().parent
INHALTE = ORDNER / "inhalte"
DATEN = ORDNER / "daten"
VORLAGE = ORDNER / "vorlage"
BILDER = ORDNER / "bilder"
ZIEL = ORDNER / "index.html"
ENTWUERFE = ORDNER / "entwuerfe"
SCHRIFT = re.compile(r"\Ainter(-display)?-(\d{3})(-italic)?\Z")

STATUS = {"leer": "leer", "entwurf": "Entwurf", "fertig": "fertig"}
MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
          "August", "September", "Oktober", "November", "Dezember"]

ZITAT = re.compile(r"<blockquote>\s*(.*?)\s*</blockquote>", re.S)
ABSATZ = re.compile(r"<p>(.*?)</p>", re.S)
BOX = re.compile(r"\A(Grafik|Offen)\s*:\s*(.*)\Z", re.S)
KOPF = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.S)

warnungen = []


def lies_schluessel_werte(text):
    """Liest Zeilen der Form «name: wert». Leere Zeilen und # werden übersprungen."""
    werte = {}
    for zeile in text.splitlines():
        zeile = zeile.strip()
        if not zeile or zeile.startswith("#") or ":" not in zeile:
            continue
        name, wert = zeile.split(":", 1)
        werte[name.strip().lower()] = wert.strip()
    return werte


def ja(wert):
    return str(wert).strip().lower() in ("ja", "yes", "true", "1")


def heute():
    d = datetime.date.today()
    return f"{d.day}. {MONATE[d.month - 1]} {d.year}"


def kennzahlen(entwurf):
    pfad = DATEN / "kennzahlen.csv"
    if not pfad.exists():
        warnungen.append("daten/kennzahlen.csv fehlt, Kacheln bleiben leer.")
        return ""
    with pfad.open(encoding="utf-8-sig", newline="") as f:
        zeilen = list(csv.DictReader(f, delimiter=";"))
    kacheln = []
    for z in zeilen:
        z = {k.strip().lower(): (v or "").strip() for k, v in z.items() if k}
        status = z.get("status", "").lower()
        if status == "offen" and not entwurf:
            continue
        einheit = f'<span class="kachel-einheit">{html.escape(z.get("einheit", ""))}</span>' if z.get("einheit") else ""
        marke = ""
        if entwurf and status in ("offen", "entwurf"):
            art = "leer" if status == "offen" else "entwurf"
            marke = f'<span class="status status-{art}">{"offen" if status == "offen" else "Entwurf"}</span>'
        klasse = "kachel ist-offen" if status == "offen" else "kachel"
        quelle = z.get("quelle", "")
        quelle_html = f'<p class="kachel-quelle">Quelle: {html.escape(quelle)}</p>' if quelle and quelle.lower() != "offen" else ""
        kacheln.append(
            f'<div class="{klasse}">{marke}'
            f'<p class="kachel-wert">{html.escape(z.get("wert", ""))}{einheit}</p>'
            f'<p class="kachel-text">{html.escape(z.get("text", ""))}</p>'
            f'{quelle_html}</div>'
        )
    return '<div class="kacheln">' + "".join(kacheln) + "</div>" if kacheln else ""


def md_zu_html(text, entwurf, kacheln_html):
    roh = markdown.markdown(text, extensions=["tables", "sane_lists", "attr_list"], output_format="html")
    # Überschriften eine Stufe tiefer: «##» im Text wird <h3>, weil <h2> der Kapiteltitel ist
    for n in range(5, 0, -1):
        roh = re.sub(rf"<(/?)h{n}\b", rf"<\1h{n + 1}", roh)

    def box(art, inhalt):
        if art == "Offen":
            return f'<aside class="offen"><span class="marke">Offen</span><p>{inhalt}</p></aside>' if entwurf else ""
        return f'<figure class="grafik-platzhalter"><span class="marke">Grafik folgt</span><p>{inhalt}</p></figure>'

    def zitat(m):
        # Markdown fasst aufeinanderfolgende «>»-Absätze zu einem Zitat zusammen.
        # Darum jeden Absatz einzeln prüfen. Nur wenn alle eine Box sind, wird ersetzt.
        innen = m.group(1)
        absaetze = [a.strip() for a in ABSATZ.findall(innen)]
        if not absaetze or ABSATZ.sub("", innen).strip():
            return m.group(0)
        teile = []
        for a in absaetze:
            if a == "Kennzahlen":
                teile.append(kacheln_html)
                continue
            b = BOX.match(a)
            if not b:
                return m.group(0)
            teile.append(box(b.group(1), b.group(2).strip()))
        return "\n".join(teile)

    roh = ZITAT.sub(zitat, roh)
    # «(Quelle: …)» am Ende eines Absatzes als eigene, kleine Zeile darstellen
    roh = re.sub(r"\s*\(Quelle:\s*([^()]*)\)", r'<span class="quelle">Quelle: \1</span>', roh)
    # Tabellen seitlich scrollbar machen, Links nach aussen in neuem Tab öffnen
    roh = roh.replace("<table>", '<div class="tabelle"><table>').replace("</table>", "</table></div>")
    roh = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', roh)
    return roh


def schriften():
    """Bettet die Schriften aus vorlage/schriften/ (inter-400.woff2, inter-display-800.woff2 …) ein."""
    regeln = []
    for pfad in sorted((VORLAGE / "schriften").glob("*.woff2")):
        m = SCHRIFT.match(pfad.stem)
        if not m:
            warnungen.append(f"Schrift {pfad.name}: Name nicht erkannt, übersprungen.")
            continue
        familie = "Inter Display" if m.group(1) else "Inter"
        stil = "italic" if m.group(3) else "normal"
        daten = base64.b64encode(pfad.read_bytes()).decode("ascii")
        regeln.append(f'@font-face {{ font-family: "{familie}"; font-style: {stil}; font-weight: {m.group(2)}; '
                      f'font-display: swap; src: url(data:font/woff2;base64,{daten}) format("woff2"); }}')
    return "\n".join(regeln)


def vorlagedatei(name, variante):
    """Nimmt die Datei aus entwuerfe/<variante>/, sonst aus vorlage/."""
    if variante:
        pfad = ENTWUERFE / variante / name
        if pfad.exists():
            return pfad
    return VORLAGE / name


def logo(alt):
    for name, typ in (("logo.svg", "image/svg+xml"), ("logo.png", "image/png"), ("logo.jpg", "image/jpeg")):
        pfad = BILDER / name
        if pfad.exists():
            daten = base64.b64encode(pfad.read_bytes()).decode("ascii")
            return f'<img class="logo" src="data:{typ};base64,{daten}" alt="{html.escape(alt)}">'
    return ""


def baue(variante=None):
    einstellungen = lies_schluessel_werte((ORDNER / "einstellungen.txt").read_text(encoding="utf-8-sig"))
    entwurf = ja(einstellungen.get("entwurf", "ja"))
    stand = heute()
    kacheln_html = kennzahlen(entwurf)

    nav, kapitel, zaehler = [], [], {}
    for datei in sorted(INHALTE.glob("*.md")):
        if datei.name.startswith("_"):
            continue
        m = KOPF.match(datei.read_text(encoding="utf-8-sig"))
        if not m:
            warnungen.append(f"{datei.name}: Kopf (zwischen --- und ---) fehlt, Datei übersprungen.")
            continue
        kopf, text = lies_schluessel_werte(m.group(1)), m.group(2)
        titel = kopf.get("titel") or datei.stem
        kurz = kopf.get("kurztitel") or titel
        anker = re.sub(r"[^a-z0-9-]", "", (kopf.get("anker") or datei.stem.split("_", 1)[-1]).lower())
        status = kopf.get("status", "leer").lower()
        if status not in STATUS:
            warnungen.append(f"{datei.name}: Status «{status}» unbekannt (erlaubt: leer, entwurf, fertig).")
            status = "leer"
        zaehler[status] = zaehler.get(status, 0) + 1

        nr = f"{len(kapitel) + 1:02d}"
        marke = f'<span class="status status-{status}">{STATUS[status]}</span>' if entwurf else ""
        nav.append(f'      <li><a href="#{anker}" data-anker="{anker}"><span class="nr">{nr}</span>'
                   f'<span class="name">{html.escape(kurz)}</span>{marke}</a></li>')
        offen = " open" if ja(kopf.get("aufgeklappt", "nein")) else ""
        kapitel.append(
            f'    <details class="kapitel" id="{anker}"{offen}>\n'
            f'      <summary class="kapitel-kopf"><span class="nr" aria-hidden="true">{nr}</span>'
            f'<h2 id="{anker}-titel">{html.escape(titel)}</h2>{marke}<span class="zeichen" aria-hidden="true"></span></summary>\n'
            f'      <div class="kapitel-inhalt">\n{md_zu_html(text, entwurf, kacheln_html)}\n      </div>\n'
            f'    </details>'
        )

    ersatz = {
        "titel": html.escape(einstellungen.get("titel", "Rechenzentren")),
        "untertitel": html.escape(einstellungen.get("untertitel", "")),
        "ueberzeile": html.escape(einstellungen.get("ueberzeile", "")),
        "herausgeber": html.escape(einstellungen.get("herausgeber", "")),
        "beschreibung": html.escape(einstellungen.get("beschreibung", "")),
        "stand": stand,
        "robots": '<meta name="robots" content="noindex">' if entwurf else "",
        "entwurf_band": ('<div class="entwurf-band">Entwurf, nicht zur Weitergabe. '
                         'Notizen «Offen» sind nur im Entwurf sichtbar.</div>') if entwurf else "",
        "logo": logo(einstellungen.get("herausgeber", "Logo")),
        "nav": "\n".join(nav),
        "kapitel": "\n".join(kapitel),
        "stil": schriften() + "\n" + vorlagedatei("stil.css", variante).read_text(encoding="utf-8"),
        "skript": vorlagedatei("seite.js", variante).read_text(encoding="utf-8"),
    }
    grafik = ENTWUERFE / variante / "grafik.js" if variante else VORLAGE / "grafik.js"
    if grafik.exists():
        ersatz["skript"] += "\n" + grafik.read_text(encoding="utf-8")
    seite = vorlagedatei("seite.html", variante).read_text(encoding="utf-8")
    for name, wert in ersatz.items():
        seite = seite.replace("{{" + name + "}}", wert)
    ziel = ENTWUERFE / f"{variante}.html" if variante else ZIEL
    ziel.write_text(seite, encoding="utf-8")

    uebersicht = ", ".join(f"{STATUS[s]} {n}" for s, n in sorted(zaehler.items()))
    print(f"{ziel.relative_to(ORDNER)} gebaut: {len(kapitel)} Kapitel ({uebersicht}), "
          f"{'Entwurf' if entwurf else 'Veröffentlichung'}, {ziel.stat().st_size // 1024} KB")
    for w in warnungen:
        print("Hinweis:", w)
    warnungen.clear()


def main():
    teile = argparse.ArgumentParser(description="Baut die Website aus inhalte/ und daten/.")
    teile.add_argument("--variante", help="Entwurf aus entwuerfe/<name>/ bauen")
    teile.add_argument("--alle", action="store_true", help="alle Entwürfe in entwuerfe/ bauen")
    args = teile.parse_args()
    if args.alle:
        for ordner in sorted(p for p in ENTWUERFE.iterdir() if p.is_dir()):
            baue(ordner.name)
    elif args.variante:
        if not (ENTWUERFE / args.variante).is_dir():
            sys.exit(f"Entwurf «{args.variante}» fehlt: Ordner entwuerfe/{args.variante}/ anlegen.")
        baue(args.variante)
    else:
        baue()


if __name__ == "__main__":
    main()
