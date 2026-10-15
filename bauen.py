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


def kennzahlen(entwurf, gruppe=""):
    """Kacheln aus daten/kennzahlen.csv. Spalte «gruppe» leer = Einleitung, sonst z. B. «Hyperscale»."""
    pfad = DATEN / "kennzahlen.csv"
    if not pfad.exists():
        warnungen.append("daten/kennzahlen.csv fehlt, Kacheln bleiben leer.")
        return ""
    with pfad.open(encoding="utf-8-sig", newline="") as f:
        zeilen = list(csv.DictReader(f, delimiter=";"))
    kacheln = []
    for z in zeilen:
        z = {k.strip().lower(): (v or "").strip() for k, v in z.items() if k}
        if z.get("gruppe", "").lower() != gruppe.strip().lower():
            continue
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
        link = z.get("link", "")
        quelle_text = html.escape(quelle)
        if link:
            quelle_text = f'<a href="{html.escape(link)}" target="_blank" rel="noopener">{quelle_text}</a>'
        quelle_html = f'<p class="kachel-quelle">Quelle: {quelle_text}</p>' if quelle and quelle.lower() != "offen" else ""
        kacheln.append(
            f'<div class="{klasse}">{marke}'
            f'<p class="kachel-wert">{html.escape(z.get("wert", ""))}{einheit}</p>'
            f'<p class="kachel-text">{html.escape(z.get("text", ""))}</p>'
            f'{quelle_html}</div>'
        )
    return '<div class="kacheln">' + "".join(kacheln) + "</div>" if kacheln else ""


def md_zu_html(text, entwurf, bausteine):
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
            if a in bausteine:
                teile.append(bausteine[a])
                continue
            if a in ("Reiter: Anfang", "Reiter: Ende"):
                teile.append("<!--REITER-ANFANG-->" if a.endswith("Anfang") else "<!--REITER-ENDE-->")
                continue
            g = re.match(r"Grössenvergleich\s*:\s*(.+)\Z", a, re.S)
            if g:
                teile.append(groessenvergleich([s.strip() for s in g.group(1).split(",")]))
                continue
            g = re.match(r"Kennzahlen\s*:\s*(.+)\Z", a, re.S)
            if g:
                teile.append(kennzahlen(entwurf, g.group(1)))
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
    roh = BILD.sub(bild, roh)
    roh = roh.replace("<table>", '<div class="tabelle"><table>').replace("</table>", "</table></div>")
    roh = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', roh)
    return REITER.sub(reiter, roh)


REITER = re.compile(r"<!--REITER-ANFANG-->(.*?)<!--REITER-ENDE-->", re.S)


def kennung(text):
    text = re.sub(r"<[^>]+>", "", text).lower()
    for alt, neu in (("ä", "ae"), ("ö", "oe"), ("ü", "ue")):
        text = text.replace(alt, neu)
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def reiter(m):
    """Abschnitte «## Name» zwischen «> Reiter: Anfang» und «> Reiter: Ende» als Reiter."""
    teile = re.split(r"(?=<h3>)", m.group(1).strip())
    vorspann = "" if teile[0].startswith("<h3>") else teile[0]
    knoepfe, felder = [], []
    for n, teil in enumerate(t for t in teile if t.startswith("<h3>")):
        titel = re.match(r"<h3>(.*?)</h3>", teil, re.S).group(1)
        ziel = "reiter-" + kennung(titel)
        inhalt = teil[teil.index("</h3>") + 5:]
        knoepfe.append(f'<button type="button" role="tab" id="{ziel}-knopf" aria-controls="{ziel}" '
                       f'aria-selected="{"true" if n == 0 else "false"}" tabindex="{0 if n == 0 else -1}">{titel}</button>')
        felder.append(f'<section class="reiter-feld{" aktiv" if n == 0 else ""}" id="{ziel}" role="tabpanel" '
                      f'aria-labelledby="{ziel}-knopf"><h3 class="reiter-titel">{titel}</h3>{inhalt}</section>')
    return (vorspann + '<div class="reiter" data-reiter><div class="reiter-leiste" role="tablist">'
            + "".join(knoepfe) + "</div>" + "".join(felder) + "</div>")


def zahl(text):
    try:
        return float(text.replace("'", "").replace("’", "").replace(",", "."))
    except ValueError:
        return None


def groessenvergleich(gruppen=None):
    """Quadrate, deren Fläche der IT-Leistung (MW) je Gruppe in daten/kennzahlen.csv entspricht.
    Mit «> Grössenvergleich: A, B, C» nur diese Gruppen."""
    pfad = DATEN / "kennzahlen.csv"
    if not pfad.exists():
        return ""
    with pfad.open(encoding="utf-8-sig", newline="") as f:
        zeilen = [{k.strip().lower(): (v or "").strip() for k, v in z.items() if k} for z in csv.DictReader(f, delimiter=";")]
    werte = []
    for z in zeilen:
        gruppe = z.get("gruppe", "")
        if gruppen and gruppe.lower() not in [g.lower() for g in gruppen]:
            continue
        if gruppe and z.get("einheit", "").upper() == "MW" and zahl(z.get("wert", "")) and gruppe not in [g for g, _, _ in werte]:
            werte.append((gruppe, zahl(z["wert"]), z["wert"]))
    if not werte:
        return ""
    groesste = max(w for _, w, _ in werte)
    elemente = []
    for gruppe, wert, anzeige in werte:
        ziel = "reiter-" + kennung(gruppe)
        elemente.append(
            f'<li><a class="vergleich-element" href="#{ziel}" data-reiter-ziel="{ziel}" style="--anteil: {(wert / groesste) ** 0.5:.3f}">'
            f'<span class="vergleich-flaeche" aria-hidden="true"></span>'
            f'<span class="vergleich-name">{html.escape(gruppe)}</span>'
            f'<span class="vergleich-wert">{html.escape(anzeige)} MW</span></a></li>')
    return '<ul class="vergleich" aria-label="Grössenvergleich nach IT-Leistung">' + "".join(elemente) + "</ul>"


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


BILD = re.compile(r"<p>\s*<img ([^>]*?)\s*/?>\s*</p>")
BILDTYP = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".svg": "image/svg+xml", ".webp": "image/webp"}


def bild(m):
    """Bild aus dem Markdown: in die Seite einbetten, Titel als Bildlegende."""
    attr = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
    src, alt, legende = attr.get("src", ""), attr.get("alt", ""), attr.get("title", "")
    pfad = ORDNER / html.unescape(src)
    if src.startswith("bilder/") and pfad.exists() and pfad.suffix.lower() in BILDTYP:
        daten = base64.b64encode(pfad.read_bytes()).decode("ascii")
        src = f"data:{BILDTYP[pfad.suffix.lower()]};base64,{daten}"
    elif src.startswith("bilder/"):
        # Bild fehlt noch: Platzhalter statt eines kaputten Bildes zeigen.
        warnungen.append(f"Bild {src} fehlt.")
        unterschrift = f"<figcaption>{legende}</figcaption>" if legende else ""
        return (f'<figure class="bild"><div class="grafik-platzhalter"><span class="marke">Bild folgt</span>'
                f'<p>{alt}</p></div>{unterschrift}</figure>')
    unterschrift = f"<figcaption>{legende}</figcaption>" if legende else ""
    return f'<figure class="bild"><img src="{src}" alt="{alt}" loading="lazy">{unterschrift}</figure>'


def akteurslandkarte():
    """Interaktive Karte aus daten/akteure.md: ein Ring pro Gruppe, innen beginnend, mit Porträt."""
    pfad = DATEN / "akteure.md"
    if not pfad.exists():
        return ""
    text = re.sub(r"<!--.*?-->", "", pfad.read_text(encoding="utf-8-sig"), flags=re.S)
    gruppen = re.findall(r"^## +(.+?)\s*\n(.*?)(?=^## |\Z)", text, flags=re.S | re.M)
    if not gruppen:
        warnungen.append("daten/akteure.md: keine Gruppen (## Name) gefunden.")
        return ""
    innen, schritt, rand = 58, 46, 8
    radien = [innen + i * schritt for i in range(len(gruppen))]
    mitte = radien[-1] + rand
    groesse = 2 * mitte
    ringe, portraits = [], []
    for i in range(len(gruppen) - 1, -1, -1):
        name, inhalt = gruppen[i][0].strip(), gruppen[i][1]
        kennung = "portrait-" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        y = mitte + 5 if i == 0 else mitte - (radien[i - 1] + radien[i]) / 2 + 5
        ringe.append(
            f'<g class="ring ring-{i}" tabindex="0" role="button" aria-controls="{kennung}" aria-expanded="false" '
            f'aria-label="{html.escape(name)}: Porträt zeigen" data-portrait="{kennung}">'
            f'<circle cx="{mitte}" cy="{mitte}" r="{radien[i]}"/>'
            f'<text x="{mitte}" y="{y:.0f}" text-anchor="middle">{html.escape(name)}</text></g>')
        portraits.insert(0,
            f'<article class="portrait" id="{kennung}"><h4>{html.escape(name)}</h4>'
            f'{md_einfach(inhalt)}</article>')
    return (
        '<figure class="landkarte">'
        f'<svg class="landkarte-grafik" viewBox="0 0 {groesse} {groesse}" role="group" '
        f'aria-label="Akteurslandkarte: {len(gruppen)} Ringe, innen beginnend">' + "".join(ringe) + "</svg>"
        '<div class="portraits"><p class="landkarte-hinweis">Für ein Porträt mit der Maus über einen Ring fahren '
        'oder ihn antippen.</p>' + "".join(portraits) + "</div></figure>")


def symbol(name):
    """Symbol aus vorlage/symbole/<name>.svg, ohne feste Grösse, Farbe folgt dem Text."""
    pfad = VORLAGE / "symbole" / f"{name}.svg"
    if not name or not pfad.exists():
        warnungen.append(f"Symbol «{name}» fehlt in vorlage/symbole/.")
        return ""
    svg = re.sub(r"<!--.*?-->", "", pfad.read_text(encoding="utf-8"), flags=re.S).strip()
    kopf_ende = svg.index(">")
    kopf = re.sub(r'\s(width|height|class)="[^"]*"', "", svg[:kopf_ende])
    return re.sub(r"\s+", " ", kopf + ' aria-hidden="true" focusable="false"' + svg[kopf_ende:])


def standortfaktoren(entwurf):
    """Symbolleiste aus daten/standortfaktoren.md: beim Darüberfahren wird ein Symbol gross,
    die anderen verblassen, darunter erscheint das Feld mit Text, Bild und Kennzahlen."""
    pfad = DATEN / "standortfaktoren.md"
    if not pfad.exists():
        return ""
    text = re.sub(r"<!--.*?-->", "", pfad.read_text(encoding="utf-8-sig"), flags=re.S)
    gruppen = re.findall(r"^## +(.+?)\s*\n(.*?)(?=^## |\Z)", text, flags=re.S | re.M)
    if not gruppen:
        warnungen.append("daten/standortfaktoren.md: keine Faktoren (## Name) gefunden.")
        return ""
    knoepfe, felder = [], []
    for n, (name, inhalt) in enumerate(gruppen):
        name = name.strip()
        angaben, zeilen = {}, inhalt.strip().splitlines()
        while zeilen and (not zeilen[0].strip() or re.match(r"(symbol|zentral|tool)\s*:", zeilen[0].strip(), re.I)):
            zeile = zeilen.pop(0).strip()
            if zeile:
                k, v = zeile.split(":", 1)
                angaben[k.strip().lower()] = v.strip()
        roh = md_einfach("\n".join(zeilen))
        figuren = [bild(m) for m in BILD.finditer(roh)]
        roh = BILD.sub("", roh).strip()
        ziel = "faktor-" + kennung(name)
        zentral = ja(angaben.get("zentral", ""))
        erster = n == 0
        li = '<li class="ist-zentral">' if zentral else "<li>"
        knoepfe.append(
            f'{li}<button type="button" role="tab" '
            f'class="faktor{" zentral" if zentral else ""}" id="{ziel}-knopf" '
            f'aria-controls="{ziel}" aria-selected="{"true" if erster else "false"}" tabindex="{0 if erster else -1}">'
            f'<span class="faktor-symbol">{symbol(angaben.get("symbol", ""))}</span>'
            f'<span class="faktor-name">{html.escape(name)}</span></button></li>')
        marke = '<span class="marke-zentral">zentral</span>' if zentral else ""
        tool = (f'<p class="faktor-tool"><span>Im Tool</span> {html.escape(angaben["tool"])}</p>'
                if angaben.get("tool") else "")
        klasse = "faktor-feld" + (" aktiv" if erster else "") + ("" if figuren else " ohne-bild")
        felder.append(
            f'<section class="{klasse}" id="{ziel}" role="tabpanel" aria-labelledby="{ziel}-knopf">'
            f'<div class="faktor-text"><h4>{html.escape(name)}{marke}</h4>{roh}{tool}</div>'
            + "".join(figuren) + kennzahlen(entwurf, name) + "</section>")
    return ('<div class="faktoren" data-faktoren>'
            '<ul class="faktoren-leiste" role="tablist" aria-label="Standortfaktoren">' + "".join(knoepfe) + "</ul>"
            '<p class="faktoren-legende"><span class="eintrag"><span class="punkt voll" aria-hidden="true"></span>'
            'zentral laut den Gesprächen</span><span class="eintrag"><span class="punkt" aria-hidden="true"></span>'
            'weitere Faktoren</span>'
            '<span class="faktoren-hinweis">Mit der Maus über ein Symbol fahren oder es antippen.</span></p>'
            '<div class="faktoren-felder">' + "".join(felder) + "</div></div>")


def md_einfach(text):
    """Markdown ohne Boxen: für Porträts und andere kurze Texte."""
    roh = markdown.markdown(text, extensions=["sane_lists"], output_format="html")
    roh = re.sub(r"\s*\(Quelle:\s*([^()]*)\)", r'<span class="quelle">Quelle: \1</span>', roh)
    return re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener">', roh)


def bilddatei(name):
    """Sucht zuerst die verkleinerte Kopie in bilder/web/, sonst in bilder/."""
    for pfad in (BILDER / "web" / name, BILDER / name):
        if pfad.exists():
            return pfad
    return None


def datei_uri(pfad):
    typ = BILDTYP.get(pfad.suffix.lower(), "application/octet-stream")
    return f"data:{typ};base64," + base64.b64encode(pfad.read_bytes()).decode("ascii")


def logo(alt):
    """logo_pos.png (hell) und logo_neg.png (dunkel), sonst logo.svg/png/jpg."""
    alt = html.escape(alt)
    hell, dunkel = bilddatei("logo_pos.png"), bilddatei("logo_neg.png")
    if hell and dunkel:
        return (f'<img class="logo logo-hell" src="{datei_uri(hell)}" alt="{alt}">'
                f'<img class="logo logo-dunkel" src="{datei_uri(dunkel)}" alt="{alt}">')
    for name in ("logo.svg", "logo.png", "logo.jpg"):
        pfad = bilddatei(name)
        if pfad:
            return f'<img class="logo" src="{datei_uri(pfad)}" alt="{alt}">'
    return ""


def favicon():
    """favicon_pos.png für helle, favicon_neg.png für dunkle Browser-Leisten."""
    hell, dunkel = bilddatei("favicon_pos.png"), bilddatei("favicon_neg.png")
    teile = []
    if hell:
        media = ' media="(prefers-color-scheme: light)"' if dunkel else ""
        teile.append('<link rel="icon" type="image/png" href="' + datei_uri(hell) + '"' + media + ">")
    if dunkel:
        teile.append('<link rel="icon" type="image/png" href="' + datei_uri(dunkel) + '" media="(prefers-color-scheme: dark)">')
    return "\n".join(teile)


def baue(variante=None):
    einstellungen = lies_schluessel_werte((ORDNER / "einstellungen.txt").read_text(encoding="utf-8-sig"))
    entwurf = ja(einstellungen.get("entwurf", "ja"))
    stand = heute()
    bausteine = {"Kennzahlen": kennzahlen(entwurf), "Akteurslandkarte": akteurslandkarte(),
                 "Grössenvergleich": groessenvergleich(), "Standortfaktoren": standortfaktoren(entwurf)}

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
            f'      <div class="kapitel-inhalt">\n{md_zu_html(text, entwurf, bausteine)}\n      </div>\n'
            f'    </details>'
        )

    ersatz = {
        "titel": html.escape(einstellungen.get("titel", "Rechenzentren")),
        "untertitel": html.escape(einstellungen.get("untertitel", "")),
        "ueberzeile": html.escape(einstellungen.get("ueberzeile", "")),
        "herausgeber": html.escape(einstellungen.get("herausgeber", "")),
        "projekt_zeile": (f'<p class="projekt">Projekt «{html.escape(einstellungen["projekt"])}»</p>'
                          if einstellungen.get("projekt") else ""),
        "beschreibung": html.escape(einstellungen.get("beschreibung", "")),
        "stand": stand,
        "robots": '<meta name="robots" content="noindex">' if entwurf else "",
        "entwurf_band": ('<div class="entwurf-band">Entwurf, nicht zur Weitergabe. '
                         'Notizen «Offen» sind nur im Entwurf sichtbar.</div>') if entwurf else "",
        "logo": logo("KEEAS"),
        "favicon": favicon(),
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
