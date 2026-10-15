# rechenzenter-erkenntnisse
Website zu Rechenzentren in der Schweiz. Sie fasst die Erkenntnisse aus dem Projekt «Zukunft Arbeitsplatzgebiete – Versorgungsfunktionen ressourcen-effizient und konfliktfrei integrieren» zusammen. Erarbeitet von KEEAS für den Verein Metropolitanraum Zürich. Themen: Akteure, Typen, Standortfaktoren, Vergleich Europa und Welt, Trends und künftiger Bedarf.

## Aufbau

| Ordner / Datei | Inhalt |
|---|---|
| `inhalte/` | Ein Text pro Kapitel (Markdown). Die Reihenfolge folgt dem Dateinamen (`01_…`, `02_…`). |
| `daten/` | Zahlen als CSV, Trennzeichen Semikolon (z. B. `kennzahlen.csv`). |
| `bilder/` | Logo als `logo.svg` oder `logo.png`. |
| `vorlage/` | Gerüst (`seite.html`), Gestaltung (`stil.css`) und Skript (`seite.js`). |
| `einstellungen.txt` | Titel, Untertitel, Herausgeber, Entwurf ja/nein. |
| `bauen.py` | Baut `index.html` aus allem oben. |
| `index.html` | Die fertige Seite. Wird erzeugt, nicht von Hand ändern. |

## Texte schreiben

- Jede Datei beginnt mit einem Kopf zwischen `---` und `---`: `titel`, `kurztitel` (Menü), `anker` (Sprungmarke), `status` (`leer`, `entwurf` oder `fertig`). Optional `aufgeklappt: ja`, dann ist das Kapitel beim Öffnen der Seite aufgeklappt.
- `## Überschrift` für Unterkapitel.
- Besondere Boxen, je als eigener Absatz mit `>`:
  - `> Grafik: Beschreibung` zeigt einen Platzhalter für eine Grafik.
  - `> Offen: Aufgabe` zeigt eine Notiz. Sie erscheint nur im Entwurf.
  - `> Kennzahlen` zeigt die Kacheln aus `daten/kennzahlen.csv`.
  - `> Kennzahlen: Hyperscale` zeigt nur die Zeilen mit dieser `gruppe` in `daten/kennzahlen.csv`.
  - `> Grössenvergleich: Hyperscale, Kollokation, Edge` zeigt Quadrate nach IT-Leistung (erste Zeile mit Einheit MW je genannter `gruppe`). Ein Klick öffnet den passenden Reiter.
  - `> Reiter: Anfang` … `> Reiter: Ende`: Jeder Abschnitt `## Name` dazwischen wird ein Reiter.
  - `> Akteurslandkarte` zeigt die Ringkarte mit den Porträts aus `daten/akteure.md`.
  - `> Standortfaktoren` zeigt die Symbolleiste aus `daten/standortfaktoren.md`. Beim Darüberfahren wird ein Symbol gross, darunter erscheinen Text, Bild und Kennzahlen (Gruppe = Name des Faktors in `daten/kennzahlen.csv`). Symbole liegen in `vorlage/symbole/` (Lucide, Lizenz ISC).
- Bild mit Legende: `![Beschreibung](bilder/datei.jpg "Legende")`. Grosse Bilder verkleinert in `bilder/web/` ablegen.
- Quelle am Ende eines Absatzes: `(Quelle: …)`. Sie erscheint als kleine Zeile darunter.

## Seite bauen

```
python3 bauen.py
```

Einmalig vorher: `pip3 install markdown`. Danach `index.html` im Browser öffnen.

## Veröffentlichen

1. In `einstellungen.txt` auf `entwurf: nein` stellen und neu bauen.
2. In GitHub Desktop: «Commit to main», dann «Push origin».
3. Erst nach Freigabe der MKZ: Repo auf Public stellen, unter Settings → Pages den Branch `main` und den Ordner `/ (root)` wählen.
