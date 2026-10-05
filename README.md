# rechenzenter-erkenntnisse
Website zu Rechenzentren. Sie fasst die wichtigsten Erkenntnisse aus der Studie «Versorgungsfunktionen» zusammen. Erarbeitet von KEEAS für den Verein Metropolitanraum Zürich. Themen: Akteure, Typen, Standortfaktoren, Vergleich Europa und Welt, Trends und künftiger Bedarf.

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
