<!--
Standortfaktoren für die Übersicht im Kapitel «Standortfaktoren».
Reihenfolge = Reihenfolge der Symbole. Jeder Faktor beginnt mit «## Name».
Direkt unter dem Namen stehen drei Angaben:
  symbol:  Dateiname eines Symbols in vorlage/symbole/ (ohne .svg)
  zentral: ja, wenn der Faktor laut den Gesprächen zu den wichtigsten gehört
  tool:    wie das Tool den Faktor misst (kurz)
Danach der Text mit Quelle am Schluss und optional ein Bild:
  ![Beschreibung](bilder/datei.jpg "Legende mit Bildnachweis")
Fehlt die Bilddatei noch, erscheint ein Platzhalter mit der Beschreibung.
Kennzahlen kommen aus daten/kennzahlen.csv (Spalte «gruppe» = Name des Faktors).
-->

## Strom

symbol: zap
zentral: ja
tool: Distanz zum nächsten Unterwerk ab 50 kV

Rechenzentren brauchen sehr viel Strom. Das Übertragungsnetz der Schweiz ist sehr gut ausgebaut. Seine Reserven liegen aber nicht unbedingt dort, wo Rechenzentren gebaut werden können. Auf den tieferen Netzebenen fehlen oft Leitungen und Unterwerke. Entscheidend ist deshalb die Lage der Unterwerke und ihr Platz zum Wachsen. (Quelle: Gespräche mit Betreibern, 2026)

![Unterwerk mit Transformatoren und Hochspannungsleitungen](bilder/standort_strom.jpg)

## Glasfaser

symbol: network
zentral: ja
tool: Anteil der Gebäude mit Glasfaser und Anzahl Anbieter

Rechenzentren brauchen schnelle und sichere Datenleitungen. Entscheidend ist die Nähe zu den Hauptglasfaserleitungen und zu den Internetknoten. Die Hauptleitungen verlaufen meist entlang von Autobahn und Bahn. Grosse Rechenzentren sind aus mehreren Richtungen ans Netz angeschlossen. (Quelle: Gespräche mit Betreibern, 2026)

![Glasfaseranschlüsse in einem Rechenzentrum](bilder/standort_glasfaser.jpg)

## Kundennähe

symbol: building-2
zentral: ja
tool: Beschäftigte in IT, Finanz, Pharma und Verwaltung im Umkreis

Rechenzentren entstehen dort, wo ihre Kunden sind. Diese kommen etwa aus IT, Pharma und Finanzindustrie sowie von NGOs. Die Nähe zählt wegen der Latenz, also der Verzögerung bei der Datenübertragung. Bei Zahlungen in Echtzeit, etwa mit Twint, sind die Anforderungen besonders hoch. Wichtig ist auch das Ökosystem: Wer dazugehört, will dort sein, wo auch die anderen sind. (Quelle: Gespräche mit Betreibern, 2026)

## Abwärme

symbol: heater
zentral: ja
tool: Distanz zu Wärmenetzen, die Abwärme aufnehmen können (in Arbeit)

Fast die ganze Energie eines Rechenzentrums wird zu Wärme. Am schwierigsten ist ihre Abnahme. Die Abwärme ist eher kühl und eignet sich vor allem für Netze mit tiefer Temperatur. Wärmeverbünde lohnen sich nur mit genügend Abnehmern in dichten Siedlungen. Gerade dort fehlt aber oft der Platz für ein Rechenzentrum. Abnehmer müssen deshalb früh gesichert werden. (Quelle: Gespräche mit Betreibern und Energiedienstleister, 2026)

![Rückkühler auf dem Dach eines Rechenzentrums oder Wärmezentrale eines Wärmeverbunds](bilder/standort_abwaerme.jpg)

## Erreichbarkeit

symbol: route
tool: Distanz zum Autobahnanschluss und ÖV-Güteklasse

Rechenzentren müssen gut erreichbar sein. Kunden kommen für den Unterhalt ihrer Server vor Ort, besonders bei Kollokation. Sie sollen nicht allzu weit fahren müssen. Auch für den Bau braucht es gute Zufahrten. (Quelle: Gespräche mit Betreibern, 2026)

![Zufahrt und Anlieferung eines Rechenzentrums](bilder/standort_erreichbarkeit.jpg)

## Naturgefahren

symbol: shield-alert
tool: Gefahrenstufe aus den kantonalen Gefahrenkarten, erhebliche Gefahr schliesst aus

Rechenzentren sind kritische Infrastruktur. Der Standort sollte eine geringe Erdbebengefahr haben und ausserhalb von Überflutungszonen liegen. In der Nähe dürfen keine Gefahrenquellen sein, etwa eine Flugpiste, ein Tanklager, Güterzüge oder Chemiebetriebe. (Quelle: Gespräche mit Betreibern, 2026)

![Ausschnitt einer Gefahrenkarte mit Arbeitszonen](bilder/standort_naturgefahren.jpg)

## Grundstück

symbol: land-plot
tool: Hangneigung; nur Flächen in Arbeitszonen ab 0.8 ha

Das Grundstück sollte möglichst flach sein. Rechenzentren bauen flach und breit, denn fehlende Fläche lässt sich nicht durch Höhe ausgleichen. Pro Geschoss braucht es 5 bis 6 m Raumhöhe. Mehr als zwei Geschosse sind statisch unwirtschaftlich. Rückkühler auf dem Dach vergrössern die nötige Grundfläche zusätzlich. (Quelle: Gespräche mit Betreibern, 2026)

![Flacher, breiter Baukörper eines Rechenzentrums auf einem grossen Grundstück](bilder/standort_grundstueck.jpg)
